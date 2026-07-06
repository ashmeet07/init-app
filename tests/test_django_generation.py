import json
import ast
import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import patch

from create_app.initializer.controller import Controller


def fake_django_run(cmd, cwd=None, check=False, capture_output=False):
    root = Path(cwd)

    if "startproject" in cmd:
        project_name = cmd[cmd.index("startproject") + 1]
        package = root / project_name
        package.mkdir(parents=True, exist_ok=True)
        (root / "manage.py").write_text("#!/usr/bin/env python\n", encoding="utf-8")
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "urls.py").write_text("urlpatterns = []\n", encoding="utf-8")
        (package / "settings.py").write_text(
            """from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'unsafe-dev-key'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
""",
            encoding="utf-8",
        )

    if "startapp" in cmd:
        app_name = cmd[cmd.index("startapp") + 1]
        app = root / app_name
        app.mkdir(parents=True, exist_ok=True)
        (app / "__init__.py").write_text("", encoding="utf-8")
        (app / "views.py").write_text("", encoding="utf-8")

    class Result:
        returncode = 0

    return Result()


def build_django_project(tmp_path, drf=False, database="sqlite"):
    manifest = {
        "project name": "django_demo",
        "app_name": "web",
        "core blueprint": "django",
        "build strategy": "standard",
        "framework": "django",
        "is_drf": drf,
        "database": database,
        "venv_enabled": False,
        "output_dir": str(tmp_path),
        "init_strategy": {},
    }

    controller = Controller(manifest, ["docs"])

    with patch("docs.prerequisite.Prerequisite.check_system") as prereq:
        with patch("create_app.initializer.controller.subprocess.run", side_effect=fake_django_run):
            prereq.return_value = {"status": True, "errors": []}
            controller.run_mission()

    return tmp_path / "django_demo"


def test_django_generation_creates_working_project_surface(tmp_path):
    project = build_django_project(tmp_path)

    assert (project / "manage.py").exists()
    assert not (project / "app.py").exists()
    assert (project / "web" / "templates" / "index.html").exists()
    assert (project / "web" / "static" / "css" / "style.css").exists()

    manage_py = (project / "manage.py").read_text()
    assert "LOCAL_VENV_PYTHON" in manage_py
    assert "INIT_APP_VENV_REEXEC" in manage_py

    urls = (project / "django_demo" / "urls.py").read_text()
    assert 'path("", views.home, name="home")' in urls
    assert 'path("health", views.health, name="health")' in urls
    assert 'path("api/about", views.about, name="about")' in urls

    views = (project / "web" / "views.py").read_text()
    assert "def home" in views
    assert "def health" in views
    assert "JsonResponse" in views

    settings = (project / "django_demo" / "settings.py").read_text()
    assert "import os" in settings
    assert 'load_dotenv(BASE_DIR / ".env")' in settings
    assert "'web'," in settings
    assert ",," not in settings
    assert "SECRET_KEY = os.environ.get" in settings
    assert "django-insecure-init-app-local-dev-key-change-me" in settings
    assert "localhost 127.0.0.1 [::1]" in settings

    readme = (project / "README.md").read_text()
    assert "python manage.py runserver" in readme
    assert "python app.py" not in readme

    metadata = json.loads((project / ".init-app.json").read_text())
    assert metadata["framework"] == "django"
    assert metadata["project_path"] == str(project.resolve())


def test_django_drf_generation_adds_rest_framework_settings(tmp_path):
    project = build_django_project(tmp_path, drf=True)

    settings_path = project / "django_demo" / "settings.py"
    settings = settings_path.read_text()
    assert "'rest_framework'," in settings
    assert "'web'," in settings
    assert "'django_extensions'," not in settings
    assert ",," not in settings
    assert "REST_FRAMEWORK =" in settings
    ast.parse(settings, filename=str(settings_path))


def test_django_env_defaults_support_localhost(tmp_path):
    project = build_django_project(tmp_path, database="mysql")

    env_file = (project / ".env").read_text()
    assert "SECRET_KEY=django-insecure-init-app-local-dev-key-change-me" in env_file
    assert "DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]" in env_file
    assert "DB_ENGINE=mysql" in env_file
    assert "DB_HOST=localhost" in env_file


def test_django_generated_app_accepts_localhost_requests(tmp_path):
    if importlib.util.find_spec("django") is None:
        return

    project = build_django_project(tmp_path)
    sys.path.insert(0, str(project))
    old_settings = os.environ.get("DJANGO_SETTINGS_MODULE")
    os.environ["DJANGO_SETTINGS_MODULE"] = "django_demo.settings"

    try:
        import django
        from django.test import Client

        django.setup()
        client = Client(HTTP_HOST="127.0.0.1")

        home = client.get("/")
        health = client.get("/health")

        assert home.status_code == 200
        assert health.status_code == 200
        assert health.json() == {"status": "online", "framework": "django"}
    finally:
        if old_settings is None:
            os.environ.pop("DJANGO_SETTINGS_MODULE", None)
        else:
            os.environ["DJANGO_SETTINGS_MODULE"] = old_settings
        if str(project) in sys.path:
            sys.path.remove(str(project))


def test_django_mysql_settings_match_selected_database(tmp_path):
    project = build_django_project(tmp_path, database="mysql")

    settings = (project / "django_demo" / "settings.py").read_text()
    assert "pymysql.install_as_MySQLdb()" in settings
    assert '"ENGINE": "django.db.backends.mysql"' in settings
    assert '"PORT": os.environ.get("DB_PORT", "3306")' in settings
    assert '"OPTIONS": {"charset": "utf8mb4"}' in settings


def test_django_postgres_settings_match_selected_database(tmp_path):
    project = build_django_project(tmp_path, database="postgresql")

    settings = (project / "django_demo" / "settings.py").read_text()
    assert '"ENGINE": "django.db.backends.postgresql"' in settings
    assert '"PORT": os.environ.get("DB_PORT", "5432")' in settings
