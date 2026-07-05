import os
from pathlib import Path
import create_app.constants as const 

# 🟢 Centralized Logger Import
from create_app.logger import logger

from create_app.rules.global_rules import get_global_manifest
from create_app.rules.standard_rules import STANDARD_BLUEPRINT
from create_app.rules.production_rules import PROD_WEB_RULES
from create_app.rules.django_rules import DJANGO_PATCH_RULES
from create_app.rules.others_rules import OTHERS_RULES

class Bundler:
    """
    SILENT LOGIC BUNDLER (v3.5.3)
    Resolves architecture, INJECTS constants, and POPULATES dependencies.
    FEATURE: Precise Django requirement resolution.
    FEATURE: Added Rich Libraries (WTForms, Flask-Mail, Mappers, and Schema tools).
    """
    def __init__(self, root: Path, ctx: dict):
        self.root = root  
        self.ctx = ctx
        
        # 1. Normalize Context keys
        self.fw_name = ctx.get('fw_name', ctx.get('framework', 'fastapi')).lower()
        self.strategy = ctx.get('build_strategy', 'standard').lower()
        self.is_drf = ctx.get('is_drf', False)
        self.db_engine = str(ctx.get('database', 'sqlite')).lower()
        
        logger.info(f"🏗️ Bundler Init: FW={self.fw_name}, Strategy={self.strategy}, DRF={self.is_drf}")
        
        # ⚡ 2. Inject Raw Constants
        constants_dict = {k: v for k, v in const.__dict__.items() if not k.startswith("__")}
        self.ctx.update(constants_dict)
        
        # ⚡ 3. Intelligent Context & Dependencies
        self._inject_dynamic_defaults()
        self._resolve_dependencies()

    def _resolve_dependencies(self):
        """Comprehensive Dependency Resolver - Injects Rich Professional Libraries."""
        logger.debug(f"🔍 Deep Scanning dependencies for {self.fw_name}...")
        
        # 1. Global Core Requirements: pure-Python/portable by default for CI and dev containers.
        deps = [
            "python-dotenv", 
            "jinja2", 
            "pyyaml", 
            "loguru", 
            "alembic",     
            "sqlalchemy",  
            "cryptography",
            "pydantic"      # Added as global for Mappers/Schemas across all frameworks
        ]

        # 2. Framework-Specific Logic with Rich Add-ons
        if self.fw_name == "fastapi":
            deps += [
                "fastapi", "uvicorn[standard]", "pydantic[email]", 
                "pydantic-settings", "httpx", "python-multipart" # Multipart for file handling
            ]
            if self.strategy in ["production", "auto_config"]:
                deps += ["slowapi", "fastapi-pagination", "python-jose[cryptography]", "passlib[bcrypt]", "gunicorn"]
        
        elif self.fw_name == "flask":
            # RICH FLASK STACK: Forms, Mail, Mappers, and Auth
            deps += [
                "flask", "flask-cors", "flask-sqlalchemy", "gunicorn",
                "flask-wtf", "wtforms",          # Form Handling
                "flask-mail",                    # Email Integration
                "flask-marshmallow",             # Object Serialization/Mappers
                "marshmallow-sqlalchemy"         # DB to Schema Mapping
            ]
            if self.strategy in ["production", "auto_config"]:
                deps += ["flask-jwt-extended", "flask-migrate", "flask-smorest"]
        
        elif self.fw_name == "django":
            # RICH DJANGO STACK
            deps += [
                "django", "django-environ", "django-cors-headers", 
                "django-extensions", "django-crispy-forms" # Beautiful forms
            ]
            
            # DRF + JSON API Requirements
            if self.is_drf:
                deps += [
                    "djangorestframework", 
                    "django-filter", 
                    "drf-spectacular", 
                    "djangorestframework-simplejwt",
                    "djangorestframework-jsonapi"
                ]
            
            if self.strategy in ["production", "auto_config"]:
                deps += ["django-redis", "django-health-check", "whitenoise", "gunicorn"]

        elif self.fw_name in ["bottle", "falcon", "pyramid"]:
            # Basic mapper for micro-frameworks
            deps += [self.fw_name, "waitress", "marshmallow"]

        # 3. Database Adapters (Extra resolution)
        if "mysql" in self.db_engine:
            deps += ["PyMySQL"]
        elif "postgres" in self.db_engine:
            deps += ["psycopg[binary]"]
        elif "mongodb" in self.db_engine:
            deps += ["pymongo", "motor", "beanie" if self.fw_name == "fastapi" else "mongoengine"]

        # 4. Domain Specific (AI & Data Science)
        if self.fw_name == "rag_ai":
            deps += ["openai", "langchain", "langchain-community", "chromadb", "qdrant-client", "tiktoken", "pypdf"]
        elif self.fw_name == "mlops_core":
            deps += ["scikit-learn", "mlflow", "joblib", "bentoml", "optuna"]

        # Final Clean up: Deduplicate and sort
        unique_deps = sorted(list(set(deps)))
        self.ctx["dependencies"] = "\n".join(unique_deps)
        logger.info(f"📦 Successfully resolved {len(unique_deps)} libraries for {self.fw_name}.")

    def _inject_dynamic_defaults(self):
        """Retrieves framework-specific values from constants.py."""
        default_port = const.DEFAULT_PORTS.get(self.fw_name, "8000")
        servers = const.FRAMEWORK_SERVER_MAPPING.get(self.fw_name, ["uvicorn"])
        default_server = servers[0] if servers else "uvicorn"

        self.ctx.update({
            "version": const.__version__,
            "app_name": self.ctx.get("app_name", const.APP_NAME),
            "port": self.ctx.get("port", default_port),
            "host": self.ctx.get("host", "0.0.0.0"),
            "debug": "True" if self.strategy == "standard" else "False",
            "server_type": self.ctx.get("server_type", default_server),
            "server": self.ctx.get("server", self.ctx.get("server_type", default_server)),
            "fw_name": self.fw_name
        })

    def _get_architectural_blueprint(self):
        """Resolves folder structure."""
        if "django" in self.fw_name:
            mode = "drf" if self.is_drf else "standard"
            return DJANGO_PATCH_RULES.get(mode, DJANGO_PATCH_RULES["standard"])
        elif self.fw_name in OTHERS_RULES:
            return OTHERS_RULES.get(self.fw_name)
        else:
            lookup_map = {"fastapi": "FastAPI", "flask": "Flask", "bottle": "Bottle"}
            lookup = lookup_map.get(self.fw_name, self.fw_name.capitalize())
            source_dict = PROD_WEB_RULES if self.strategy in ["production", "auto_config"] else STANDARD_BLUEPRINT
            return source_dict.get(lookup, source_dict.get("FastAPI"))

    def execute(self):
        """Finalizes build data and forces correct template injection."""
        logger.info("🚀 Bundler Execution Started.")
        blueprint = self._get_architectural_blueprint()
        manifest = get_global_manifest(self.ctx)
        
        # UI Folder Setup
        ui_map = {"fastapi": "ui", "flask": "templates", "bottle": "templates"}
        ui_folder = ui_map.get(self.fw_name, "ui")
        self.ctx["ui_folder"] = ui_folder

        if self.fw_name in ["fastapi", "flask", "bottle"]:
            if "folders" not in blueprint: blueprint["folders"] = []
            if ui_folder not in blueprint["folders"]:
                blueprint["folders"].append(ui_folder)

        # Entry point normalization
        entry_found = False
        for rule in manifest:
            if any(x in rule["target"] for x in ["app.py", "main.py", "entry.py"]):
                rule["target"] = "app.py"
                if "django" not in self.fw_name:
                    rule["source"] = "common/entry.py.tpl"
                    entry_found = True
            
            if not rule["source"].startswith("common/") and not rule["source"].startswith("framework/"):
                rule["source"] = f"common/{rule['source']}"

        if not entry_found and "django" not in self.fw_name:
            manifest.append({"source": "common/entry.py.tpl", "target": "app.py"})

        # UI Inject
        if self.fw_name in ["fastapi", "flask", "bottle"]:
            ui_rules = [
                {"source": "common/template/index.html.tpl", "target": f"{ui_folder}/index.html"},
                {"source": "common/static/css/style.css.tpl", "target": f"{ui_folder}/static/css/style.css"},
                {"source": "common/static/scripts/script.js.tpl", "target": f"{ui_folder}/static/js/script.js"}
            ]
            existing = [r["target"] for r in manifest]
            for rule in ui_rules:
                if rule["target"] not in existing: manifest.append(rule)

        # Requirements
        manifest.append({"source": "common/requirements.txt.tpl", "target": "requirements.txt"})

        return {"blueprint": blueprint, "manifest": manifest, "ctx": self.ctx}
