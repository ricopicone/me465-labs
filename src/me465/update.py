"""`uv run update` — get the course's latest labs and packages.

With a git clone this pulls the course repository (fast-forward only: your
work lives in `work/`, which the course never touches) and then syncs the
Python packages. From a ZIP download there is nothing to pull: download the
ZIP again and unzip it over this folder; `work/` is left alone.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(*cmd: str) -> int:
    print("$", " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


def main() -> int:
    if (ROOT / ".git").exists():
        status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, capture_output=True, text=True)
        if status.stdout.strip():
            print("You have edited files the course tracks:\n" + status.stdout)
            print("Move your changes into work/ (uv run lab <name> makes the copy), then run this again.")
            return 1
        if run("git", "pull", "--ff-only") != 0:
            print("The pull did not go through. Bring this output to office hours.")
            return 1
    else:
        print("This folder is not a git clone (you used Download ZIP). To update: download the ZIP")
        print("again from GitHub and unzip it over this folder. Your work/ folder is not in the ZIP,")
        print("so it stays as it is. Then run this command again to sync the packages.")
    if run("uv", "sync") != 0:
        print("Package sync failed. Bring this output to office hours.")
        return 1
    print("up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
