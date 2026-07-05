This is the "Source of Truth" document for your engine. I’ve designed this `COMMANDLINE.md` to look professional, high-tech, and crystal clear, exposing every feature from the **Architect** logic to the **Infrastructure Forge**.

---

### 📄 `COMMANDLINE.md`

# 🌌 Advanced Project Engine - CLI Manual

**Version:** `4.6.0`

**Engineer:** `Ashmeet Singh`

This document outlines the full capabilities of the Project Engine. The engine supports two primary flows: **Interactive UI** (Menu-driven) and **Headless CLI** (Flag-driven).

---

## 🕹️ 1. Build Strategies

The engine behaves differently based on the `-t` (type) flag:

| Strategy | Behavior |
| --- | --- |
| `auto_config` | **Zero-Config.** Uses smart defaults for the chosen framework. Best for rapid prototyping. |
| `standard` | **The Balanced Build.** Generates common folder structures (routes, models, schemas). |
| `production` | **Enterprise Ready.** Includes full infrastructure suites (Docker, K8s) and strict folder separation. |
| `custom` | **Total Control.** Enables manual folder selection and individual `__init__.py` configuration. |

---

## 🛠️ 2. CLI Flag Reference

Use these flags to bypass menus and automate your workflow.

### Core Identity

* `name`: The name of your project folder.
* `-f, --framework`: `fastapi`, `flask`, `django`, `others`.
* `-s, --server`: Specify the runner (e.g., `uvicorn`, `gunicorn`, `hypercorn`).
* `-t, --type`: The build strategy (`auto_config`, `standard`, `production`, `custom`).
* `--output-dir`: Directory where the project folder is created. Defaults to `~/Documents`.
* `--here`: Create the project in the current working directory.
* `--path-behavior`: One-off path behavior for this project: `documents`, `current`, or `custom`.
* `--set-default-path-behavior`: Save the default path behavior for future runs.
* `--set-default-output-dir`: Save a custom default output directory for future runs.
* `--show-path-config`: Show saved path behavior.
* `--reset-path-config`: Reset saved path behavior.

### Architecture & Packages (Custom Mode)

* `--folders`: Manually define every directory to be created.
* `--packages`: Define which of those folders should be Python packages (adds `__init__.py`).

### Data & Environment

* `--db`: Set the database engine (`sqlite`, `postgres`, `mysql`, `mongodb`).
* `--venv`: Enable virtual environment creation (`y` or `n`).

### Infrastructure Forge

* `--docker`: `dockerfile`, `docker-compose`, `.dockerignore`.
* `--github`: `main.yml`, `ci.yml`, `cd.yml`.
* `--k8s`: `deployment.yml`, `service.yml`, `ingress.yml`.
* `--jenkins`: `Jenkinsfile`.

---

## 🚀 3. Usage Examples

### A. The "Speed Demon" (Auto-Config)

Builds a FastAPI project with SQLite and a VENV instantly.

```bash
init-app quick_api -f fastapi -t auto_config --venv y

```

### B. The "Full Stack Pro" (Production)

Builds a Django + Postgres app with Docker and GitHub Actions.

```bash
init-app pro_backend -f django -t production --db postgres --docker dockerfile docker-compose --github main.yml

```

### C. The "Architect" (Deep Customization)

The most powerful command. Manually define folders and only make `src` and `app` Python packages.

```bash
init-app bespoke_engine -f fastapi -t custom \
  --folders src app docs tests logs \
  --packages src app \
  --db mongodb --venv y

```

---

## 🧠 4. Internal Logic & Features

### 🐍 Selective Package Initialization

Unlike standard generators that put `__init__.py` everywhere, this engine uses an `init_strategy` map. It only converts a folder into a Python package if explicitly told to or if the framework requires it.

### 💉 Snippet Injection (Django)

When building Django, the engine performs "surgical" regex injections:

* **Settings Patching**: Automatically adds your App to `INSTALLED_APPS`.
* **Security Injection**: Moves `SECRET_KEY` to environment variable logic.
* **DRF Integration**: If DRF is detected, it injects the `REST_FRAMEWORK` configuration block automatically.

### 🛡️ UI Folder Guard

The engine contains a security layer that prevents any template rendering from writing into the `ui/` directory, protecting the engine's core interface assets during a project build.

---

## 🏗️ 5. Directory Structure Example (Production)

```text
my_project/
├── .github/workflows/    # Generated via --github
├── docker/               # Generated via --docker
├── venv/                 # Generated via --venv
├── app/                  # Package (init_strategy: True)
│   ├── __init__.py
│   ├── routes/
│   ├── models/
│   └── schemas/
├── requirements.txt      # Auto-generated
└── app.py                # Main Entrypoint

```

---

**Mission Control is ready. What would you like to build next?**
