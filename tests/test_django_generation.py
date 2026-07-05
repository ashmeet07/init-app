import json
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


def build_django_project(tmp_path, drf=False):
    manifest = {
        "project name": "django_demo",
        "app_name": "web",
        "core blueprint": "django",
        "build strategy": "standard",
        "framework": "django",
        "is_drf": drf,
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
    assert "'web'," in settings
    assert "SECRET_KEY = os.environ.get" in settings

    readme = (project / "README.md").read_text()
    assert "python manage.py runserver" in readme
    assert "python app.py" not in readme

    metadata = json.loads((project / ".init-app.json").read_text())
    assert metadata["framework"] == "django"
    assert metadata["project_path"] == str(project.resolve())


def test_django_drf_generation_adds_rest_framework_settings(tmp_path):
    project = build_django_project(tmp_path, drf=True)

    settings = (project / "django_demo" / "settings.py").read_text()
    assert "'rest_framework'," in settings
    assert "'web'," in settings
    assert "REST_FRAMEWORK =" in settings
