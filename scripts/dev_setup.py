import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main():
    print("\n🚀 Setting up py-create dev environment...\n")

    try:
        subprocess.check_call([sys.executable, "scripts/install_dev.py"], cwd=ROOT)

        print("\n✔ Dev environment ready 😌🔥\n")

    except Exception:
        print("\n❌ Dev setup failed\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
