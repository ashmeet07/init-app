import re
from pathlib import Path


VERSION_FILES = [
    Path("create_app/constants.py"),
    Path("setup.cfg"),
    Path("README.md"),
]


def main():
    constants = VERSION_FILES[0].read_text()
    match = re.search(r'__version__ = "([^"]+)"', constants)

    if not match:
        print("❌ Version not found")
        return

    current_version = match.group(1)

    print(f"\nCurrent version → {current_version}")

    new_version = input("New version → ")

    VERSION_FILES[0].write_text(
        constants.replace(
            f'__version__ = "{current_version}"',
            f'__version__ = "{new_version}"',
        ),
        encoding="utf-8",
    )

    setup_cfg = VERSION_FILES[1].read_text(encoding="utf-8")
    VERSION_FILES[1].write_text(
        re.sub(r"^version = .*$", f"version = {new_version}", setup_cfg, flags=re.MULTILINE),
        encoding="utf-8",
    )

    readme = VERSION_FILES[2].read_text(encoding="utf-8")
    VERSION_FILES[2].write_text(
        re.sub(r"\*\*Version:\*\* `[^`]+`", f"**Version:** `{new_version}`", readme),
        encoding="utf-8",
    )

    print(f"\n✔ Version updated → {new_version} 😌🔥\n")


if __name__ == "__main__":
    main()
