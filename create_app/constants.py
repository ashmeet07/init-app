"""
UNIFIED ARCHITECTURAL CONSTANTS (v0.6.1)
Project: init-app Engine
Focus: Base, RAG AI, Data Engineering, and Enterprise DevOps.
Standardization: Atomic Base-IDs for High-Performance Routing.
"""

__version__ = "2.2.0b2"

# --- 1. BRANDING & IDENTITY ---
APP_NAME    = "init-app"
APP_TAGLINE = "High-Performance System & Native Extension Generator"

# --- 2. CORE ENGINE BLUEPRINTS (Base Slugs) ---
FRAMEWORKS = [
    "fastapi", "flask", "django", "bottle", 
    "sanic", "falcon", "tornado", "pyramid", "others" 
]

OTHERS_PROJECT_TYPES = [
    "base", 
    "hp_cli", 
    "data_pipeline",
    "dbt_analytics",
    "mlops_core",
    "rag_ai"
]

PROJECT_MODES = ["standard", "production", "auto_config", "custom"]

# --- 3. INTELLIGENT DESCRIPTIONS (Mapping Base to Display) ---
DESCRIPTIONS = {
    # Base Slugs : Display Description
    "fastapi":       "High-performance Async API with OpenAPI support.",
    "flask":         "Flexible and lightweight WSGI micro-framework.",
    "django":        "Feature-rich 'batteries-included' web framework.",
    "bottle":        "Ultra-lightweight single-file WSGI micro-framework.",
    "sanic":         "Next-gen Async Python web server & framework.",
    "falcon":        "Minimalist ASGI/WSGI framework for high-performance APIs.",
    "tornado":       "Asynchronous networking library and web framework.",
    "pyramid":       "Small, fast, down-to-earth Python web framework.",
    "others":        "Specialized Python system and data engineering engines.",
    
    # Specialized Base Engines
    "base":    "Python Base Project",
    "rag_ai":        "LLM-powered Retrieval Augmented Generation engine.",
    "mlops_core":    "Machine Learning lifecycle and model serving core.",
    "hp_cli":        "Optimized Command Line Interface with Click/Typer.",
    "data_pipeline": "Workflow orchestration for complex data task graphs.",
    "dbt_analytics": "Data transformation and documentation for SQL warehouses.",
    
    # Architectural Base Modes
    "standard":      "Clean architecture with basic configuration layers.",
    "production":    "Enterprise-ready setup with Docker, K8s, and Jenkins folders.",
    "auto_config":   "One-click deployment using optimized system defaults.",
    "custom":        "Full manual control over architectural components.",
    
    # Data & Storage
    "postgresql":    "Robust, production-grade relational database.",
    "sqlite":        "Portable, serverless file-based database.",
    "mongodb":       "NoSQL document store for flexible data schemas."
}

# --- 4. DATA NEXUS & ORM SUITE ---
DB_ENGINES = ["postgresql", "mysql", "sqlite", "mongodb", "none"]

DB_STRUCTURE = [
    "db/migrations", "db/seeds", "db/schemas", "db/scripts"
]

ORM_MAPPING = {
    "fastapi": ["sqlalchemy", "tortoise_orm", "beanie"],
    "flask":   ["flask_sqlalchemy", "mongoengine"],
    "django":  ["django_orm"],
    "others":  ["sqlalchemy", "peewee", "na"]
}

# --- 5. RUNTIME & SERVER ORCHESTRATION ---
SERVER_OPTIONS = ["uvicorn", "gunicorn", "waitress", "gevent", "wsgiref", "na"]

FRAMEWORK_SERVER_MAPPING = {
    "fastapi": ["uvicorn", "gunicorn"],
    "flask":   ["gunicorn", "waitress", "gevent", "wsgiref", "na"],
    "django":  ["gunicorn", "waitress", "wsgiref"],
    "bottle":  ["waitress", "gevent", "wsgiref", "na"],
    "sanic":   ["na"],
    "falcon":  ["gunicorn", "waitress", "wsgiref"],
    "tornado": ["na"],
    "pyramid": ["waitress", "gunicorn", "wsgiref"],
    "others":  ["na"]
}

DEFAULT_PORTS = {
    "fastapi": "8000", "flask": "5000", "django": "8000",
    "bottle":  "8080", "sanic": "8000", "falcon": "8000",
    "tornado": "8888", "pyramid": "6543", "others": "na"
}

# --- 6. DEVOPS & CI/CD SUITES ---
JENKINS_SUITE = [
    "jenkins/Jenkinsfile",
    "jenkins/pipelines/build.groovy",
    "jenkins/pipelines/deploy.groovy",
    "jenkins/scripts/notify.sh"
]

DOCKER_SUITE = [
    "docker/Dockerfile",
    "docker/docker-compose.yml",
    "docker/docker-compose.prod.yml",
    "docker/.dockerignore",
    "docker/DOCKER.md"
]

K8S_FILES = [
    "k8s/deployment.yml", "k8s/service.yml", "k8s/ingress.yml",
    "k8s/hpa.yml", "k8s/pvc.yml", "k8s/configmap.yml", "k8s/secret.yml"            
]

GITHUB_SUITE = [
    ".github/workflows/ci.yml", ".github/workflows/security.yml",
    ".github/ISSUE_TEMPLATE/bug_report.md", ".github/ISSUE_TEMPLATE/feature_request.md",
    ".github/PULL_REQUEST_TEMPLATE.md"
]

# --- 7. ARCHITECTURAL LAYERS ---
RAG_LAYERS  = ["vectordb", "embeddings", "knowledge", "prompts", "retrievers", "chains"]
DATA_LAYERS = ["dags", "transformers", "staging", "analysis", "artifacts"]

ALL_CUSTOM_FOLDERS = [
    "config", "routes", "services", "models", "schemas", "middleware", "utils",
    "templates", "static", "assets", "logs", "tests", "docs", "scripts",
    "src", "include", "k8s", ".github", "db", "docker", "jenkins"
] + RAG_LAYERS + DATA_LAYERS

# --- 8. SYSTEM DEFAULTS & ASSETS ---
GLOBAL_DEFAULTS = [
    ".env.example", "Makefile", "README.md", ".gitignore", ".editorconfig", "alembic.ini"               
]

COMMUNITY_CORE = [
    "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md", "CHANGELOG.md"
]

PACKAGE_FILES = [
    "MANIFEST.in", "setup.py", "setup.cfg", "requirements.txt", "package.json"              
]

UI_MAPPING = {
    "bottle": "views", "flask": "templates", "fastapi": "templates",
    "django": "templates", "others": "assets"
}
