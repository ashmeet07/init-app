import subprocess
import sys
import importlib.util


def main():
    print("\n📦 Building py-create package...\n")

    try:
        subprocess.check_call([sys.executable, "scripts/build_compiler.py"])
        if importlib.util.find_spec("build") is not None:
            subprocess.check_call([sys.executable, "-m", "build"])
        else:
            subprocess.check_call([sys.executable, "setup.py", "sdist"])

        print("\n✔ Build complete 😌🔥\n")

    except Exception:
        print("\n❌ Build failed\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
