import os
import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = ROOT / ".venv"


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def run(cmd: list[str]) -> None:
    subprocess.check_call(cmd, cwd=ROOT)


def run_capture(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=ROOT, text=True).strip()


def manual_editable_install(python: Path) -> None:
    purelib = Path(
        run_capture([
            str(python),
            "-c",
            "import sysconfig; print(sysconfig.get_paths()['purelib'])",
        ])
    )
    scripts_dir = Path(
        run_capture([
            str(python),
            "-c",
            "import sysconfig; print(sysconfig.get_path('scripts'))",
        ])
    )

    purelib.mkdir(parents=True, exist_ok=True)
    scripts_dir.mkdir(parents=True, exist_ok=True)
    (purelib / "init_app_editable.pth").write_text(str(ROOT) + "\n", encoding="utf-8")

    if os.name == "nt":
        launcher = scripts_dir / "init-app.cmd"
        launcher.write_text(
            f'@echo off\r\n"{python}" -m create_app.engine.cli %*\r\n',
            encoding="utf-8",
        )
    else:
        launcher = scripts_dir / "init-app"
        launcher.write_text(
            f'#!{python}\nfrom create_app.engine.cli import main\nmain()\n',
            encoding="utf-8",
        )
        launcher.chmod(0o755)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install init-app for local development.")
    parser.add_argument(
        "--offline-source",
        action="store_true",
        help="Install only the editable source package without downloading dependencies.",
    )
    parser.add_argument(
        "--skip-compiler",
        action="store_true",
        help="Skip the native compiler build.",
    )
    args = parser.parse_args()

    if not VENV_DIR.exists():
        print(f"Creating virtual environment at {VENV_DIR}")
        run([sys.executable, "-m", "venv", str(VENV_DIR)])

    python = venv_python()
    print("Installing init-app in editable mode")

    if args.offline_source:
        manual_editable_install(python)
    else:
        try:
            run([str(python), "-m", "pip", "install", "-e", "."])
        except subprocess.CalledProcessError:
            print("Standard editable install failed; linking source manually.")
            manual_editable_install(python)

    if not args.skip_compiler:
        print("Building native compiler")
        run([str(python), "scripts/build_compiler.py"])

    print("\nDev install complete.")
    if os.name == "nt":
        print(r"Activate with: .\.venv\Scripts\Activate.ps1")
    else:
        print("Activate with: source .venv/bin/activate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
