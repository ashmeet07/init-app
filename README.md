
<a href="https://pypi.org/project/init-app/"><img width="1024" height="359" alt="init-app-logo(2)" src="https://github.com/user-attachments/assets/c4c929d3-5031-4e26-96a3-7c9129522303" /></a>

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/init-app?period=total&units=NONE&left_color=YELLOW&right_color=ORANGE&left_text=downloads)](https://pepy.tech/projects/init-app)

<div align="center">

[![FastAPI](https://img.shields.io/badge/FastAPI-05998b?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Django](https://img.shields.io/badge/Django-092e20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Bottle](https://img.shields.io/badge/Bottle-000000?style=flat-square&logoColor=white)](https://bottlepy.org/)
[![Falcon](https://img.shields.io/badge/Falcon-3e3e3e?style=flat-square&logoColor=white)](https://falconframework.org/)
[![Pyramid](https://img.shields.io/badge/Pyramid-303030?style=flat-square&logo=pyramid&logoColor=white)](https://trypyramid.com/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-215a81?style=flat-square&logo=uvicorn&logoColor=white)](https://www.uvicorn.org/)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=flat-square&logo=gunicorn&logoColor=white)](https://gunicorn.org/)
[![Hypercorn](https://img.shields.io/badge/Hypercorn-000000?style=flat-square&logoColor=white)](https://github.com/pgjones/hypercorn)
[![Waitress](https://img.shields.io/badge/Waitress-ffcc00?style=flat-square&logoColor=black)](https://docs.pylonsproject.org/projects/waitress/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=flat-square&logo=jenkins&logoColor=white)](https://www.jenkins.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![dbt](https://img.shields.io/badge/dbt-FF694B?style=flat-square&logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)](https://www.linux.org/)
[![Windows](https://img.shields.io/badge/Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python_3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)

</div>


<div align="center" >
<img width="750" height="350" alt="image" src="https://github.com/user-attachments/assets/7b78c8eb-c14d-4f97-aa2c-f3677b845132" />
</div>







**Version:** `2.2.0b2`

**Engineer:** `Ashmeet Singh`

## Cross-Platform Setup

Use a virtual environment so editable installs work the same way on macOS, Linux, and Windows.
Do not run `pip3 install -e .` directly against Apple system Python; older pip versions can fall back to `setup.py develop` and try to write into protected system site-packages.

### One-command dev install

```bash
python3 scripts/install_dev.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Offline or DNS-restricted environment:

```bash
python -m pip install -e .
```

If runtime dependencies are already installed or supplied by your own wheelhouse, install only the source package without network access:

```bash
python scripts/install_dev.py --offline-source
```

The dev installer also builds the native compiler. Use `--skip-compiler` only when a C compiler is not available on that machine.

Build the optional native C engine with:

```bash
python scripts/build_compiler.py
```

The compiler output is written to `bin/init-app-compiler` on macOS/Linux and `bin/init-app-compiler.exe` on Windows.

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

Database adapters are chosen to work cleanly in local, CI, and container environments. MySQL projects use `PyMySQL` by default, so generated installs do not require native `mysqlclient`, `pkg-config`, or system MySQL headers.

### Infrastructure Forge

* `--docker`: `dockerfile`, `docker-compose`, `.dockerignore`.
* `--github`: `main.yml`, `ci.yml`, `cd.yml`.
* `--k8s`: `deployment.yml`, `service.yml`, `ingress.yml`.
* `--jenkins`: `Jenkinsfile`.
* `--community`: `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`.
* `--package-files`: `setup.cfg`, `setup.py`, `MANIFEST.in`.

---

## 🚀 3. Usage Examples

### A. The "Speed Demon" (Auto-Config)

Builds a FastAPI project with SQLite and a VENV instantly.

```bash
init-app quick_api -f fastapi -t auto_config --venv y

```

By default, this creates `~/Documents/quick_api` no matter which folder your terminal is currently in. Use `--here` to keep the old current-folder behavior, or `--output-dir /path/to/apps` for CI and DevOps scripts.

Persist your preferred default:

```bash
init-app --set-default-path-behavior current
init-app --set-default-output-dir ~/Documents/backend-apps
init-app --show-path-config
```

After saving a default, normal commands use it automatically:

```bash
init-app quick_api -f fastapi
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

<img width="400" height="552" alt="image" src="https://github.com/user-attachments/assets/75f44825-f486-40df-9100-015be74d9877" />

<img width="400" height="452" alt="image" src="https://github.com/user-attachments/assets/7dfda372-7ecf-4b3b-9d88-765c4ddc04c7" />


# **Contributors are welcome to this to enhance the optimisation of this repository**
