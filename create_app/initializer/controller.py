import os
import sys
import json
import subprocess
import shutil
import re
from pathlib import Path
from typing import Optional
import jinja2

# --- AGGRESSIVE PATH RESOLUTION ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path: 
    sys.path.insert(0, ROOT_DIR)

from create_app.framework.bundler import Bundler
from create_app.engine.ui.ui_config import UIConfig 
from create_app.initializer.generator import Generator
from create_app.path_config import PathConfig
import create_app.constants as const 
from create_app.engine.ui.spinner import Spinner 
from docs.prerequisite import Prerequisite
from create_app.logger import logger

class Controller:
    """
    Build orchestrator.

    The controller receives a normalized manifest from either CLI or interactive
    mode, resolves the output path, asks Bundler for the logical blueprint, and
    asks Generator to write the project files.
    """
    def __init__(self, manifest: dict, folders: list): 
        self.manifest = manifest
        self.p_name = manifest.get("project name", "new_project")
        
        # Normalize user-facing labels into stable slugs used by rules/templates.
        bp_raw = str(manifest.get("core blueprint", "fastapi")).lower()
        self.fw = bp_raw.split(" (")[0].strip().split(" +")[0]
        self.is_drf = "rest framework" in bp_raw or manifest.get("is_drf", False)
        self.strategy = str(manifest.get("build strategy", "standard")).lower()
        
        # Auto-config is intentionally opinionated: it enables the full suite.
        if self.strategy == "auto_config":
            logger.info("⚡ Auto-Config: Forcing Every Production Suite & Folder.")
            folders = list(const.ALL_CUSTOM_FOLDERS)
            self.manifest["infra_files"] = {
                "docker": list(const.DOCKER_SUITE),
                "jenkins": list(const.JENKINS_SUITE),
                "kubernetes": list(const.K8S_FILES),
                "github": list(const.GITHUB_SUITE)
            }
            self.manifest["init_strategy"] = {f: True for f in folders}

        self.invocation_dir = Path.cwd().resolve()
        self.output_base = self._resolve_output_base(manifest)
        self.root = self.output_base / self.p_name
        self.colors = UIConfig.C
        
        # Context shared with templates and build helpers.
        self.ctx = {
            **self.manifest,
            "project_name": self.p_name,
            "app_name": manifest.get("app_name", "core_app"),
            "framework": self.fw,
            "build_strategy": self.strategy,
            "is_drf": self.is_drf,
            "custom_folders": folders,
            "init_strategy": self.manifest.get("init_strategy", {}),
            "invocation_dir": str(self.invocation_dir),
            "output_dir": str(self.output_base),
            "project_path": str(self.root),
        }

        logger.info(f"🚀 Controller linked for mission: {self.p_name}")
        self.executor = Bundler(self.root, self.ctx)
        self.worker = Generator(self.root, self.executor.ctx)
        
        # Terminal instructions are normal templates rendered after generation.
        self.tpl_path = Path(ROOT_DIR) / "create_app" / "common"
        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(self.tpl_path)))

    @staticmethod
    def _default_output_base() -> Path:
        """Default generated apps to the user's Documents folder."""
        return (Path.home() / "Documents").resolve()

    @classmethod
    def _resolve_output_base(cls, manifest: dict) -> Path:
        """Choose where a generated project folder will be created."""
        raw_output = manifest.get("output_dir") or manifest.get("output path")
        if raw_output:
            return Path(str(raw_output)).expanduser().resolve()

        if manifest.get("create_in_current_dir"):
            return Path.cwd().resolve()

        config = PathConfig.load()
        behavior = manifest.get("path_behavior") or config.get("path_behavior", "documents")

        if behavior == "current":
            return Path.cwd().resolve()

        if behavior == "custom":
            configured_output = config.get("output_dir")
            if configured_output:
                return Path(str(configured_output)).expanduser().resolve()

        return cls._default_output_base()

    def _sync_project_paths(self):
        """Keep path context and worker roots aligned if tests override self.root."""
        self.root = Path(self.root).expanduser().resolve()
        self.output_base = self.root.parent
        self.ctx.update({
            "invocation_dir": str(self.invocation_dir),
            "output_dir": str(self.output_base),
            "project_path": str(self.root),
        })
        self.executor.root = self.root
        self.executor.ctx.update(self.ctx)
        self.worker.root = self.root
        self.worker.ctx.update(self.executor.ctx)

    @staticmethod
    def _normalize_generated_path(path: str, suite: Optional[str] = None) -> str:
        """Return the final project path for a requested support file."""
        normalized = str(path).replace("\\", "/").strip()
        if normalized.endswith(".tpl"):
            normalized = normalized[:-4]

        suite_aliases = {"github": ".github", "kubernetes": "k8s", "pkg": ""}
        suite_root = suite_aliases.get(str(suite or "").lower(), str(suite or "").lower())

        if suite_root and suite_root != "community":
            if normalized == suite_root or normalized.startswith(f"{suite_root}/"):
                return normalized
            if suite_root == ".github":
                return f".github/workflows/{normalized}"
            return f"{suite_root}/{normalized}"

        return normalized

    def _source_for_target(self, target: str) -> str:
        """Prefer a real template when one exists; otherwise let Generator synthesize."""
        candidates = [
            self.tpl_path / f"{target}.tpl",
            self.tpl_path / target,
            self.tpl_path / "template" / f"{os.path.basename(target)}.tpl",
        ]
        for candidate in candidates:
            if candidate.exists():
                return f"common/{candidate.relative_to(self.tpl_path)}".replace("\\", "/")
        return f"generated/{target}.tpl"

    def _run_prerequisites(self):
        """Validates system tools before starting the build."""
        with Spinner("Verifying system requirements"):
            check = Prerequisite.check_system()
        
        if not check["status"]:
            logger.error(f"❌ Prerequisites failed: {check.get('errors')}")
            sys.exit(1)

    def _setup_virtual_env(self):
        """Creates a virtual environment only if requested."""
        raw_val = self.manifest.get("venv_enabled", self.manifest.get("venv", True))
        
        if raw_val in [False, "no", "n", "false", "skip"]:
            logger.info("🚫 VENV setup skipped.")
            return

        venv_path = self.root / "venv"
        req_file = self.root / "requirements.txt"

        try:
            with Spinner("Setting up virtual environment"):
                subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True, capture_output=True)
            
            if req_file.exists():
                with Spinner("Installing dependencies (pip)"):
                    pip_exe = venv_path / ("Scripts" if os.name == "nt" else "bin") / "pip"
                    subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], capture_output=True)
                    subprocess.run([str(pip_exe), "install", "-r", str(req_file)], check=True, capture_output=True)
                logger.info("✅ Dependencies installed.")
        except Exception as e:
            logger.error(f"⚠️ VENV warning: {str(e)}")

    def _handle_django_logic(self):
        """Native Django bootstrapping with Dynamic Snippet Injection."""
        app_name = self.ctx.get("app_name", "core_app")
        tpl_dir = self.tpl_path
        
        with Spinner(f"Injected Django architecture"):
            # 1. Standard Bootstrap
            if not self._run_django_command([sys.executable, "-m", "django", "startproject", self.p_name, "."]):
                self._scaffold_django_project(app_name)
            elif not self._run_django_command([sys.executable, "manage.py", "startapp", app_name]):
                self._scaffold_django_app(app_name)

            settings_path = self.root / self.p_name / "settings.py"
            if settings_path.exists():
                content = settings_path.read_text(encoding="utf-8")
                
                # --- A. SECRET KEY & HOSTS ---
                if (tpl_dir / "secret.tpl").exists():
                    secret_patch = (tpl_dir / "secret.tpl").read_text()
                    pattern = r"SECRET_KEY = .*?ALLOWED_HOSTS = \[\]"
                    content = re.sub(pattern, secret_patch, content, flags=re.DOTALL)
                
                # --- B. INSTALLED_APPS INJECTION ---
                if self.is_drf:
                    # Case 1: Django REST Framework selected - Inject from apps.py.tpl
                    apps_tpl = tpl_dir / "apps.py.tpl"
                    if apps_tpl.exists():
                        apps_list_raw = apps_tpl.read_text().replace('{{app_name}}', app_name)
                        content = self._inject_installed_apps(content, apps_list_raw.splitlines())
                else:
                    # Case 2: Normal Django - Just add the app name at the end of the list
                    content = self._inject_installed_apps(content, [f"'{app_name}',"])

                # --- C. REST_FRAMEWORK CONFIG (DRF ONLY) ---
                if self.is_drf:
                    rf_tpl = tpl_dir / "rf.py.tpl"
                    if rf_tpl.exists() and "REST_FRAMEWORK =" not in content:
                        rf_config = rf_tpl.read_text().strip()
                        content += f"\n\n{rf_config}\n"

                # --- D. UTILITY IMPORTS ---
                if "import os" not in content:
                    content = content.replace("from pathlib import Path", "from pathlib import Path\nimport os")

                content = self._patch_django_env_loader(content)
                content = self._patch_django_database_settings(content)
                content = self._ensure_django_runtime_settings(content)
                
                settings_path.write_text(content, encoding="utf-8")
                logger.info(f"✅ Django settings.py patched. Mode: {'DRF' if self.is_drf else 'Standard'}")

            views_path = self.root / app_name / "views.py"
            views_path.write_text(
                f'''from django.http import JsonResponse
from django.shortcuts import render


def home(request):
    return render(request, "index.html")


def health(request):
    return JsonResponse({{"status": "online", "framework": "django"}})


def about(request):
    return JsonResponse({{
        "name": "{self.p_name}",
        "framework": "django",
        "strategy": "{self.strategy}",
        "status": "online",
        "generated_by": "init-app",
    }})
''',
                encoding="utf-8",
            )

            urls_path = self.root / self.p_name / "urls.py"
            if urls_path.exists():
                urls_path.write_text(
                    f'''from django.contrib import admin
from django.urls import path

from {app_name} import views


urlpatterns = [
    path("", views.home, name="home"),
    path("health", views.health, name="health"),
    path("api/about", views.about, name="about"),
    path("admin/", admin.site.urls),
]
''',
                    encoding="utf-8",
                )

            self._patch_django_manage_py()

    def _run_django_command(self, cmd: list) -> bool:
        """Run a Django management command and expose useful failures."""
        try:
            subprocess.run(cmd, cwd=self.root, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or exc.stdout or "").strip()
            if isinstance(stderr, bytes):
                stderr = stderr.decode(errors="replace")
            if stderr:
                logger.warning(f"Django command failed: {stderr}")
            else:
                logger.warning(f"Django command failed: {' '.join(cmd)}")
            return False

    @staticmethod
    def _inject_installed_apps(settings_content: str, app_lines: list) -> str:
        """Insert INSTALLED_APPS entries without duplicate or doubled commas."""
        clean_lines = []
        for raw_line in app_lines:
            value = str(raw_line).strip()
            if not value:
                continue
            value = value.rstrip(",")
            if not (value.startswith("'") or value.startswith('"')):
                value = repr(value)
            clean_lines.append(f"    {value},")

        if not clean_lines:
            return settings_content

        existing = set(re.findall(r"['\"]([^'\"]+)['\"]", settings_content))
        unique_lines = []
        for line in clean_lines:
            app_name_match = re.search(r"['\"]([^'\"]+)['\"]", line)
            app_name = app_name_match.group(1) if app_name_match else ""
            if app_name and app_name in existing:
                continue
            existing.add(app_name)
            unique_lines.append(line)

        if not unique_lines:
            return settings_content

        insertion = "\n".join(unique_lines) + "\n"
        pattern = r"(INSTALLED_APPS\s*=\s*\[.*?)(^\])"
        return re.sub(
            pattern,
            rf"\1{insertion}\2",
            settings_content,
            flags=re.DOTALL | re.MULTILINE,
            count=1,
        )

    def _patch_django_database_settings(self, settings_content: str) -> str:
        """Replace Django's default database block with the selected database."""
        block = self._django_database_settings_block()
        pattern = r"DATABASES\s*=\s*\{\s*['\"]default['\"]\s*:\s*\{.*?\n\s*\}\s*\n\}"
        if re.search(pattern, settings_content, flags=re.DOTALL):
            return re.sub(pattern, block, settings_content, flags=re.DOTALL, count=1)
        return f"{settings_content.rstrip()}\n\n{block}\n"

    def _ensure_django_runtime_settings(self, settings_content: str) -> str:
        """Fill settings that a minimal/fallback Django project needs to boot."""
        additions = []

        if "ROOT_URLCONF" not in settings_content:
            additions.append(f'ROOT_URLCONF = "{self.p_name}.urls"')

        if "WSGI_APPLICATION" not in settings_content:
            additions.append(f'WSGI_APPLICATION = "{self.p_name}.wsgi.application"')

        if "MIDDLEWARE" not in settings_content:
            additions.append('''MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]''')

        if "TEMPLATES" not in settings_content:
            additions.append('''TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]''')

        if "STATIC_URL" not in settings_content:
            additions.append('STATIC_URL = "static/"')

        if "DEFAULT_AUTO_FIELD" not in settings_content:
            additions.append('DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"')

        if not additions:
            return settings_content

        return f"{settings_content.rstrip()}\n\n" + "\n\n".join(additions) + "\n"

    @staticmethod
    def _patch_django_env_loader(settings_content: str) -> str:
        """Add optional python-dotenv loading to generated Django settings."""
        if "load_dotenv(BASE_DIR / \".env\")" in settings_content:
            return settings_content

        loader = '''try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass
'''
        pattern = r"(BASE_DIR\s*=\s*Path\(__file__\)\.resolve\(\)\.parent\.parent\s*\n)"
        if re.search(pattern, settings_content):
            return re.sub(pattern, rf"\1\n{loader}", settings_content, count=1)
        return settings_content

    def _django_database_settings_block(self) -> str:
        """Return a Django DATABASES block for sqlite, MySQL, or PostgreSQL."""
        db = str(self.ctx.get("database", self.manifest.get("database", "sqlite"))).lower()

        if "mysql" in db:
            return '''try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    pass

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME", "app_db"),
        "USER": os.environ.get("DB_USER", "root"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "3306"),
        "OPTIONS": {"charset": "utf8mb4"},
    }
}'''

        if "postgres" in db:
            return '''DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "app_db"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}'''

        return '''DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / os.environ.get("DB_NAME", "db.sqlite3"),
    }
}'''

    def _scaffold_django_project(self, app_name: str):
        """Fallback Django scaffold for environments without django installed."""
        project_pkg = self.root / self.p_name
        project_pkg.mkdir(parents=True, exist_ok=True)
        (project_pkg / "__init__.py").write_text("", encoding="utf-8")
        (project_pkg / "asgi.py").write_text(
            f'''import os

from django.core.asgi import get_asgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{self.p_name}.settings")

application = get_asgi_application()
''',
            encoding="utf-8",
        )
        (project_pkg / "wsgi.py").write_text(
            f'''import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{self.p_name}.settings")

application = get_wsgi_application()
''',
            encoding="utf-8",
        )
        database_block = self._django_database_settings_block()
        (project_pkg / "settings.py").write_text(
            f'''from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-init-app-local-dev-key-change-me",
)
DEBUG = os.environ.get("DEBUG", "1").lower() in {"1", "true", "yes", "on"}
ALLOWED_HOSTS = [
    host
    for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        "localhost 127.0.0.1 [::1]",
    ).replace(",", " ").split()
    if host
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "{self.p_name}.urls"

TEMPLATES = [
    {{
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {{
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        }},
    }},
]

WSGI_APPLICATION = "{self.p_name}.wsgi.application"

{database_block}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
''',
            encoding="utf-8",
        )
        (self.root / "manage.py").write_text(
            self._django_manage_py_content(),
            encoding="utf-8",
        )
        self._scaffold_django_app(app_name)

    def _patch_django_manage_py(self):
        """Ensure manage.py can re-exec through the generated local venv."""
        manage_path = self.root / "manage.py"
        if manage_path.exists():
            manage_path.write_text(self._django_manage_py_content(), encoding="utf-8")

    def _django_manage_py_content(self) -> str:
        """Return the managed Django entry script used in generated projects."""
        return f'''#!/usr/bin/env python
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
LOCAL_VENV_PYTHON = (
    PROJECT_ROOT
    / "venv"
    / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
)


def reexec_with_project_venv():
    if os.environ.get("INIT_APP_VENV_REEXEC") == "1":
        return
    if not LOCAL_VENV_PYTHON.exists():
        return
    current = Path(sys.executable).resolve()
    target = LOCAL_VENV_PYTHON.resolve()
    if current == target:
        return
    os.environ["INIT_APP_VENV_REEXEC"] = "1"
    os.execv(str(target), [str(target), __file__, *sys.argv[1:]])


def main():
    reexec_with_project_venv()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{self.p_name}.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        print("\\nMissing dependency: django")
        print("Install the generated project requirements first:")
        print("  python -m pip install -r requirements.txt\\n")
        raise SystemExit(1)
    try:
        execute_from_command_line(sys.argv)
    except ModuleNotFoundError as exc:
        print(f"\\nMissing dependency: {{exc.name}}")
        print("Install the generated project requirements first:")
        print("  python -m pip install -r requirements.txt\\n")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
'''

    def _scaffold_django_app(self, app_name: str):
        """Create a minimal Django app when startapp cannot run locally."""
        app_dir = self.root / app_name
        app_dir.mkdir(parents=True, exist_ok=True)
        (app_dir / "__init__.py").write_text("", encoding="utf-8")
        (app_dir / "apps.py").write_text(
            f'''from django.apps import AppConfig


class {self._django_config_class_name(app_name)}Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "{app_name}"
''',
            encoding="utf-8",
        )
        (app_dir / "models.py").write_text("# Create your models here.\n", encoding="utf-8")
        (app_dir / "tests.py").write_text("# Create your tests here.\n", encoding="utf-8")
        (app_dir / "views.py").write_text("", encoding="utf-8")

    @staticmethod
    def _django_config_class_name(app_name: str) -> str:
        return "".join(part.capitalize() for part in re.split(r"[_\\W]+", app_name) if part) or "App"

    def _display_tpl(self, tpl_name: str):
        """Renders a specific template directly to terminal output."""
        try:
            template = self.jinja_env.get_template(tpl_name)
            output = template.render(self.executor.ctx)
            print(f"{self.colors['white']}{output}")
        except Exception as e:
            logger.debug(f"Terminal render skipped for {tpl_name}: {e}")

    def _render_instructions(self):
        """Displays final summary by populating templates directly."""
        print("\n" + "—"*50)
        self._display_tpl("venv.txt.tpl")
        self._display_tpl("work.txt.tpl")
        print("—"*50 + "\n")

    def _write_project_metadata(self):
        """Persist traceability data for generated projects."""
        metadata = {
            "project_name": self.p_name,
            "framework": self.fw,
            "build_strategy": self.strategy,
            "project_path": str(self.root),
            "output_dir": str(self.output_base),
            "invocation_dir": str(self.invocation_dir),
            "generated_by": const.APP_NAME,
            "generator_version": const.__version__,
        }
        (self.root / ".init-app.json").write_text(
            json.dumps(metadata, indent=2) + "\n",
            encoding="utf-8",
        )

    def run_mission(self):
        """Master Build Sequence Orchestrator."""
        try:
            self._sync_project_paths()
            self._run_prerequisites()
            self.root.mkdir(parents=True, exist_ok=True)
            
            if self.fw == "django": 
                self._handle_django_logic()
            
            # Resolve rules, render files, then create any requested support files.
            build_data = self.executor.execute()
            self.worker.ctx = build_data.get('ctx', self.ctx) 
            
            with Spinner("Generating project architecture"):
                final_manifest = []
                for rule in build_data.get('manifest', []):
                    if any(x in rule["target"] for x in ["work.txt", "venv.txt"]):
                        continue

                    if any(x in rule["target"] for x in ["_main.py", "run.py", "entry.py"]):
                        rule["target"] = "app.py"
                    
                    if not rule["source"].startswith("common/") and not rule["source"].startswith("framework/"):
                        rule["source"] = f"common/{rule['source']}"
                        
                    final_manifest.append(rule)

                infra_map = self.manifest.get("infra_files", {})
                for suite, files in infra_map.items():
                    if not files: continue
                    for filename in files:
                        target = self._normalize_generated_path(filename, suite)
                        final_manifest.append({
                            "source": self._source_for_target(target),
                            "target": target,
                        })
                
                self.worker.run(blueprint=build_data.get('blueprint'), manifest_rules=final_manifest)
            
            self._setup_virtual_env()
            
            if self.fw == "django":
                ui_dir = self.root / "ui"
                if ui_dir.exists(): 
                    shutil.rmtree(ui_dir)

            self._write_project_metadata()
            
            self._render_instructions()

        except Exception as e:
            logger.error(f"🔥 Controller Failure: {str(e)}", exc_info=True)
            print(f"\n  {self.colors['accent']}✖ {self.colors['white']}failure: {str(e).lower()}")
