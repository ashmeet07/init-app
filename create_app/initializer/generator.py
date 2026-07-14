import os
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from create_app.logger import logger

class Generator:
    """
    Filesystem writer for generated projects.

    Generator knows how to create folders, render templates, and place static
    assets in the framework-specific location expected by the starter app.
    """
    def __init__(self, root: Path, ctx: dict):
        self.root = root
        self.ctx = ctx
        self.fw = str(ctx.get("framework", "fastapi")).lower()
        self.is_drf = ctx.get("is_drf", False)
        self.app_name = ctx.get("app_name", "core_app")
        
        # Base directory points to the installed/source create_app package.
        self.base_dir = Path(__file__).parent.parent.resolve()
        
        # Jinja checks package templates first, then shared HTML/static folders.
        search_paths = [
            str(self.base_dir),
            str(self.base_dir / "common" / "template"),
            str(self.base_dir / "framework" / "templates")
        ]
        
        valid_paths = [p for p in search_paths if Path(p).exists()]
        
        logger.info(f"⚙️ Generator Engine Linked: Root={self.root}")
        
        self.env = Environment(
            loader=FileSystemLoader(valid_paths),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def _render_and_write(self, tpl_path: str, output_rel_path: str):
        """Renders a Jinja2 template and writes it to the target path."""
        tpl_path = tpl_path.replace("\\", "/")
        target_path = self.root / output_rel_path
        
        # Guard for Django UI assets: Skip generic "ui/" if framework is Django
        # (Django uses app-specific folders handled in _handle_static_assets)
        if self.fw == "django" and (output_rel_path.startswith("ui/") or output_rel_path == "ui"):
            return

        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            template = self.env.get_template(tpl_path)
            rendered_content = template.render(**self.ctx)
            
            if not rendered_content.strip():
                logger.warning(f"⚠️ Template {tpl_path} rendered as empty. Check context variables.")

            target_path.write_text(rendered_content, encoding="utf-8")
            logger.debug(f"📝 Rendered: {output_rel_path}")

        except TemplateNotFound:
            fallback = self._fallback_content(output_rel_path)
            target_path.write_text(fallback, encoding="utf-8")
            logger.debug(f"📝 Generated fallback: {output_rel_path}")
        except Exception as e:
            logger.error(f"❌ Template Error [{tpl_path}]: {str(e)}")
            if not target_path.exists():
                fallback = self._fallback_content(output_rel_path)
                target_path.write_text(fallback, encoding="utf-8")
                logger.warning(f"⚠️ Created fallback file: {output_rel_path}")

    def _fallback_content(self, output_rel_path: str) -> str:
        """Create useful starter content for supported files that lack templates."""
        path = output_rel_path.replace("\\", "/")
        name = Path(path).name
        suffix = Path(path).suffix.lower()
        project = self.ctx.get("project_name", "app")
        framework = self.ctx.get("fw_name", self.fw)
        dependencies = self.ctx.get("dependencies", "")

        if name == "Dockerfile":
            return (
                "FROM python:3.11-slim\n\n"
                "ENV PYTHONDONTWRITEBYTECODE=1\n"
                "ENV PYTHONUNBUFFERED=1\n\n"
                "WORKDIR /app\n"
                "COPY requirements.txt .\n"
                "RUN python -m pip install --upgrade pip setuptools wheel\n"
                "RUN pip install --no-cache-dir -r requirements.txt\n"
                "COPY . .\n"
                "CMD [\"python\", \"app.py\"]\n"
            )

        if name in {"docker-compose.yml", "docker-compose.prod.yml"}:
            return (
                "services:\n"
                "  app:\n"
                "    build: ..\n"
                "    ports:\n"
                "      - \"8000:8000\"\n"
                "    env_file:\n"
                "      - ../.env\n"
            )

        if name == ".dockerignore":
            return ".git\n.venv\nvenv\n__pycache__\n*.pyc\n.env\nbuild\ndist\n"

        if path.startswith(".github/workflows/") and suffix in {".yml", ".yaml"}:
            return (
                "name: CI\n\n"
                "on:\n"
                "  push:\n"
                "  pull_request:\n\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-python@v5\n"
                "        with:\n"
                "          python-version: '3.11'\n"
                "      - run: python -m pip install --upgrade pip\n"
                "      - run: python -m pip install --upgrade setuptools wheel\n"
                "      - run: python -m pip install -r requirements.txt\n"
                "      - run: python -m compileall .\n"
            )

        if path.startswith(".github/ISSUE_TEMPLATE/") and suffix == ".md":
            title = name.replace("_", " ").replace(".md", "").title()
            return f"# {title}\n\n## Summary\n\n## Steps to Reproduce\n\n## Expected Behavior\n\n"

        if name == "PULL_REQUEST_TEMPLATE.md":
            return "## Summary\n\n## Checklist\n\n- [ ] Tests or validation completed\n"

        if name == "Jenkinsfile":
            return (
                "pipeline {\n"
                "  agent any\n"
                "  stages {\n"
                "    stage('Test') {\n"
                "      steps { sh 'python -m compileall .' }\n"
                "    }\n"
                "  }\n"
                "}\n"
            )

        if suffix == ".groovy":
            return "def call() {\n  echo 'Pipeline step placeholder'\n}\n"

        if suffix == ".sh":
            return "#!/usr/bin/env sh\nset -eu\n\necho \"Running project script\"\n"

        if path.startswith("k8s/") and suffix in {".yml", ".yaml"}:
            if name == "deployment.yml":
                return (
                    "apiVersion: apps/v1\n"
                    "kind: Deployment\n"
                    "metadata:\n"
                    f"  name: {project}\n"
                    "spec:\n"
                    "  replicas: 1\n"
                    "  selector:\n"
                    "    matchLabels:\n"
                    f"      app: {project}\n"
                    "  template:\n"
                    "    metadata:\n"
                    "      labels:\n"
                    f"        app: {project}\n"
                    "    spec:\n"
                    "      containers:\n"
                    f"        - name: {project}\n"
                    f"          image: {project}:latest\n"
                    "          ports:\n"
                    "            - containerPort: 8000\n"
                )
            if name == "service.yml":
                return (
                    "apiVersion: v1\n"
                    "kind: Service\n"
                    "metadata:\n"
                    f"  name: {project}\n"
                    "spec:\n"
                    "  selector:\n"
                    f"    app: {project}\n"
                    "  ports:\n"
                    "    - port: 80\n"
                    "      targetPort: 8000\n"
                )
            if name == "ingress.yml":
                return (
                    "apiVersion: networking.k8s.io/v1\n"
                    "kind: Ingress\n"
                    "metadata:\n"
                    f"  name: {project}\n"
                    "spec:\n"
                    "  rules:\n"
                    "    - http:\n"
                    "        paths:\n"
                    "          - path: /\n"
                    "            pathType: Prefix\n"
                    "            backend:\n"
                    "              service:\n"
                    f"                name: {project}\n"
                    "                port:\n"
                    "                  number: 80\n"
                )
            if name == "hpa.yml":
                return (
                    "apiVersion: autoscaling/v2\n"
                    "kind: HorizontalPodAutoscaler\n"
                    "metadata:\n"
                    f"  name: {project}\n"
                    "spec:\n"
                    "  minReplicas: 1\n"
                    "  maxReplicas: 3\n"
                    "  scaleTargetRef:\n"
                    "    apiVersion: apps/v1\n"
                    "    kind: Deployment\n"
                    f"    name: {project}\n"
                )
            if name == "pvc.yml":
                return (
                    "apiVersion: v1\n"
                    "kind: PersistentVolumeClaim\n"
                    "metadata:\n"
                    f"  name: {project}\n"
                    "spec:\n"
                    "  accessModes:\n"
                    "    - ReadWriteOnce\n"
                    "  resources:\n"
                    "    requests:\n"
                    "      storage: 1Gi\n"
                )
            if name == "secret.yml":
                return (
                    "apiVersion: v1\n"
                    "kind: Secret\n"
                    "metadata:\n"
                    f"  name: {project}\n"
                    "type: Opaque\n"
                    "stringData:\n"
                    "  APP_ENV: production\n"
                )
            return (
                "apiVersion: v1\n"
                "kind: ConfigMap\n"
                "metadata:\n"
                f"  name: {project}\n"
                "data:\n"
                f"  FRAMEWORK: {framework}\n"
            )

        if name == "pyproject.toml":
            package_name = str(project).replace("_", "-")
            return (
                "[build-system]\n"
                "requires = [\"setuptools>=61\", \"wheel\"]\n"
                "build-backend = \"setuptools.build_meta\"\n\n"
                "[project]\n"
                f"name = \"{package_name}\"\n"
                "version = \"0.1.0\"\n"
                "requires-python = \">=3.9\"\n"
            )

        if name == "setup.cfg":
            package_name = str(project).replace("_", "-")
            return (
                "[metadata]\n"
                f"name = {package_name}\n"
                "version = 0.1.0\n"
                "description = Generated Python application\n\n"
                "[options]\n"
                "packages = find:\n"
                "python_requires = >=3.9\n"
                "install_requires =\n"
                f"{self._indent_requirements(dependencies)}"
            )

        if name == "setup.py":
            return "from setuptools import setup\n\nsetup()\n"

        if name == "MANIFEST.in":
            return "include README.md\nrecursive-include . *.py *.md *.txt *.yml *.yaml\n"

        if name == "package.json":
            return f'{{\n  "name": "{project}",\n  "version": "0.1.0",\n  "private": true\n}}\n'

        if name == "requirements.txt":
            return f"{dependencies}\n" if dependencies else "\n"

        if name == ".editorconfig":
            return "root = true\n\n[*]\ncharset = utf-8\nindent_style = space\nindent_size = 4\n"

        if name == "alembic.ini":
            return "[alembic]\nscript_location = db/migrations\nsqlalchemy.url = sqlite:///app.db\n"

        if suffix == ".md":
            title = name.replace("_", " ").replace(".md", "").title()
            return f"# {title}\n\nGenerated for {project} ({framework}).\n"

        if suffix in {".yml", ".yaml"}:
            return f"name: {project}\n"

        if suffix == ".json":
            return "{}\n"

        if suffix == ".ini":
            return f"[{project}]\nframework = {framework}\n"

        return f"# {name}\n\nGenerated for {project}.\n"

    @staticmethod
    def _indent_requirements(dependencies: str) -> str:
        lines = [line.strip() for line in str(dependencies).splitlines() if line.strip()]
        if not lines:
            return ""
        return "".join(f"    {line}\n" for line in lines)

    def run(self, blueprint: dict, manifest_rules: list):
        """Executes the physical build sequence."""
        if not blueprint: 
            blueprint = {}
            
        self.root.mkdir(parents=True, exist_ok=True)
        logger.info("🛠️ Building project filesystem...")

        # Create directories first so rendered files always have a parent path.
        folders_to_create = (blueprint.get("folders", []) + blueprint.get("packages", []))
        for folder in folders_to_create:
            if not folder or folder == "none" or (folder.lower() == "ui" and self.fw == "django"):
                continue
            
            target = self.root / folder
            target.mkdir(parents=True, exist_ok=True)
            
            if folder in blueprint.get("packages", []):
                (target / "__init__.py").touch()

        if manifest_rules:
            logger.info(f"📄 Rendering {len(manifest_rules)} files from manifest...")
            for rule in manifest_rules:
                self._render_and_write(rule["source"], rule["target"])

        self._handle_static_assets()
        
        logger.info("🏁 Physical generation phase complete.")
        return True

    def _handle_static_assets(self):
        """Place shared HTML/CSS/JS assets in the correct framework folder."""
        
        # HTML templates live under app/templates for Django and ui/ otherwise.
        src_tpl_dir = self.base_dir / "common" / "template"
        if src_tpl_dir.exists():
            for tpl_file in src_tpl_dir.glob("*.tpl"):
                clean_name = tpl_file.name.replace(".tpl", "")
                
                if self.fw == "django":
                    target_path = f"{self.app_name}/templates/{clean_name}"
                else:
                    target_path = f"ui/{clean_name}"
                
                tpl_lookup = f"common/template/{tpl_file.name}"
                self._render_and_write(tpl_lookup, target_path)

        src_static_dir = self.base_dir / "common" / "static"
        if not src_static_dir.exists():
            return

        if self.fw == "django":
            target_static_root = self.root / self.app_name / "static"
        else:
            ui_folder = self.ctx.get("ui_folder", "ui")
            target_static_root = self.root / ui_folder / "static"

        for root_path, _, files in os.walk(src_static_dir):
            for file in files:
                source_file = Path(root_path) / file
                rel_path = source_file.relative_to(src_static_dir)
                
                if file.endswith(".tpl"):
                    clean_name = str(rel_path).replace(".tpl", "")
                    
                    if clean_name.startswith("scripts"):
                        clean_name = clean_name.replace("scripts", "js", 1)
                    
                    tpl_lookup = f"common/static/{rel_path}".replace("\\", "/")
                    
                    final_abs_path = target_static_root / clean_name
                    rel_to_root = str(final_abs_path.relative_to(self.root))
                    
                    self._render_and_write(tpl_lookup, rel_to_root)
                else:
                    dest_file = target_static_root / rel_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, dest_file)
