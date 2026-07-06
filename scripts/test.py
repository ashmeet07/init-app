import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run_pytest() -> bool:
    if importlib.util.find_spec("pytest") is None:
        return False

    subprocess.check_call([sys.executable, "-m", "pytest"], cwd=ROOT)
    return True


def smoke_call(message: str, fn, *args):
    fn(*args)
    print(f"ok - {message}")


def run_smoke_tests() -> None:
    from tests.test_branding_templates import (
        test_branded_starter_templates_render,
        test_supported_starter_apps_render_valid_python,
        test_starter_app_uses_project_relative_ui_paths,
    )
    from tests.test_dependency_resolution import (
        test_mysql_uses_portable_driver,
        test_other_project_types_include_domain_dependencies,
        test_postgres_uses_modern_binary_package,
        test_supported_web_frameworks_include_runtime_dependency,
        test_sqlite_does_not_pull_native_database_drivers,
    )
    from tests.test_django_generation import (
        test_django_generated_app_accepts_localhost_requests,
        test_django_drf_generation_adds_rest_framework_settings,
        test_django_generation_creates_working_project_surface,
    )
    from tests.test_file_support import (
        test_generated_paths_preserve_supported_file_locations,
        test_missing_templates_generate_useful_supported_files,
    )
    from tests.test_output_paths import (
        test_default_output_base_prefers_documents,
        test_output_dir_manifest_controls_project_root,
        test_project_metadata_tracks_paths,
    )
    from tests.test_packaging_metadata import (
        test_init_app_installs_django_for_generation_commands,
        test_package_version_is_stable_major_release,
    )

    smoke_call("default output path", test_default_output_base_prefers_documents)
    smoke_call("portable mysql dependency", test_mysql_uses_portable_driver)
    smoke_call("sqlite dependency set", test_sqlite_does_not_pull_native_database_drivers)
    smoke_call("postgres dependency set", test_postgres_uses_modern_binary_package)
    smoke_call("web framework dependencies", test_supported_web_frameworks_include_runtime_dependency)
    smoke_call("other project dependencies", test_other_project_types_include_domain_dependencies)
    smoke_call("packaging includes django", test_init_app_installs_django_for_generation_commands)
    smoke_call("package version", test_package_version_is_stable_major_release)
    smoke_call("support file path mapping", test_generated_paths_preserve_supported_file_locations)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        smoke_call("output dir controls root", test_output_dir_manifest_controls_project_root, tmp_path)
        smoke_call("project metadata", test_project_metadata_tracks_paths, tmp_path)
        smoke_call("branding templates", test_branded_starter_templates_render, tmp_path)
        smoke_call("project-relative starter paths", test_starter_app_uses_project_relative_ui_paths, tmp_path)
        smoke_call("starter app syntax matrix", test_supported_starter_apps_render_valid_python, tmp_path)
        smoke_call("support file fallbacks", test_missing_templates_generate_useful_supported_files, tmp_path)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        smoke_call("django standard generation", test_django_generation_creates_working_project_surface, tmp_path)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        smoke_call("django drf generation", test_django_drf_generation_adds_rest_framework_settings, tmp_path)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        smoke_call("django localhost requests", test_django_generated_app_accepts_localhost_requests, tmp_path)

    run_load_tests()


def run_load_tests(iterations: int = 25) -> None:
    from create_app.framework.bundler import Bundler
    from create_app.initializer.generator import Generator

    frameworks = ("fastapi", "flask", "django", "bottle", "falcon", "pyramid")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for index in range(iterations):
            framework = frameworks[index % len(frameworks)]
            ctx = {
                "project_name": f"load_{index}",
                "framework": framework,
                "fw_name": framework,
                "build_strategy": "production" if index % 2 else "standard",
                "database": ("sqlite", "mysql", "postgresql")[index % 3],
                "venv_enabled": False,
            }
            bundler = Bundler(root / f"bundle_{index}", ctx)
            assert bundler.ctx["dependencies"]
            generator = Generator(root / f"render_{index}", bundler.ctx)
            generator._render_and_write("common/entry.py.tpl", "app.py")
            assert (root / f"render_{index}" / "app.py").exists()
    print(f"ok - load generation loop ({iterations} iterations)")


def main() -> int:
    os.environ.setdefault("PYTHONPYCACHEPREFIX", "/private/tmp/init-app-pycache")
    try:
        if not run_pytest():
            print("pytest not installed; running built-in smoke tests.")
            run_smoke_tests()
        return 0
    except Exception as exc:
        print(f"tests failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
