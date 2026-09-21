"""Build the mdr command-line binary on the current operating system."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = ROOT_DIR / "app"
IS_WINDOWS = sys.platform == "win32"
BINARY_NAME = "mdr.exe" if IS_WINDOWS else "mdr"
DATA_SEPARATOR = ";" if IS_WINDOWS else ":"


def run(*command: str) -> None:
    subprocess.check_call(command, cwd=ROOT_DIR)


def main() -> None:
    run(sys.executable, "-m", "pip", "install", "-r", "requirements-build.txt")
    run(
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        "mdr",
        "--console",
        "--clean",
        "--paths",
        str(APP_DIR),
        "--add-data",
        f"{APP_DIR / 'config.json'}{DATA_SEPARATOR}.",
        str(APP_DIR / "index.py"),
    )
    print(f"\nBuilt binary: {ROOT_DIR / 'dist' / BINARY_NAME}")


if __name__ == "__main__":
    main()
