import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ROOT / "compiler" / "main.c",
    ROOT / "compiler" / "core" / "engine.c",
    ROOT / "compiler" / "platform" / "actions.c",
]


def output_path(name: Optional[str] = None) -> Path:
    suffix = ".exe" if platform.system() == "Windows" else ""
    return ROOT / "bin" / (name or f"init-app-compiler{suffix}")


def find_compiler() -> tuple[str, list[str]]:
    system = platform.system()

    if system == "Windows":
        cl = shutil.which("cl")
        if cl:
            return cl, ["msvc"]

        for candidate in ("clang", "gcc", "cc"):
            path = shutil.which(candidate)
            if path:
                return path, ["gnu"]

    for candidate in ("cc", "clang", "gcc"):
        path = shutil.which(candidate)
        if path:
            return path, ["gnu"]

    raise RuntimeError(
        "No C compiler found. Install Xcode Command Line Tools on macOS, "
        "build-essential on Debian/Ubuntu, or MSVC/MinGW on Windows."
    )


def build(output: Path) -> None:
    compiler, family = find_compiler()
    output.parent.mkdir(parents=True, exist_ok=True)

    if family == ["msvc"]:
        cmd = [
            compiler,
            "/nologo",
            "/W4",
            "/O2",
            *[str(src) for src in SOURCES],
            f"/Fe:{output}",
        ]
    else:
        cmd = [
            compiler,
            "-std=c99",
            "-Wall",
            "-Wextra",
            "-O2",
            *[str(src) for src in SOURCES],
            "-o",
            str(output),
        ]

    subprocess.check_call(cmd, cwd=ROOT)
    print(f"Built {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the init-app native C engine.")
    parser.add_argument("-o", "--output", type=Path, help="Output executable path")
    args = parser.parse_args()

    try:
        build(args.output or output_path())
    except Exception as exc:
        print(f"Compiler build failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
