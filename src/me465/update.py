"""`uv run update` — get the course's latest labs and packages.

With a git clone this pulls the course repository (fast-forward only: your
work lives in `work/`, which the course never touches) and then syncs the
Python packages. A clone of a fork is pointed back at the course repository
first. A ZIP download has no repository to pull from: the command says how
to replace it with a clone.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COURSE_REPO = "ricopicone/me465-labs"
COURSE_URL = f"https://github.com/{COURSE_REPO}.git"
# Files CoppeliaSim writes when a student saves the scene: never anyone's work, so an
# update puts them back instead of refusing to pull (Sim 1, October 2026).
SCENES = ("src/me465/scenes/ur5.ttt",)


def _origin_is_the_course() -> bool | None:
    """True if origin is the course repository, False if it is something else (a fork),
    None if there is no origin."""
    r = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        return None
    url = r.stdout.strip().lower().removesuffix(".git")
    return url.endswith(COURSE_REPO.lower())


def _edited() -> list[str]:
    """Tracked files that differ from the last commit, as repository paths."""
    r = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, capture_output=True, text=True)
    return [line[3:].strip().strip('"') for line in r.stdout.splitlines() if line.strip()]


def _restore_scenes(edited: list[str]) -> list[str]:
    """Put back any scene file CoppeliaSim saved over; return the other edited files."""
    scenes = [f for f in edited if f in SCENES]
    if scenes:
        print("CoppeliaSim saved over the course's scene; putting it back (your work is in work/):")
        for f in scenes:
            print("   ", f)
        subprocess.call(["git", "checkout", "--", *scenes], cwd=ROOT)
        print("When CoppeliaSim asks whether to save the scene, answer No.\n")
    return [f for f in edited if f not in SCENES]


def run(*cmd: str) -> int:
    print("$", " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


def main() -> int:
    if (ROOT / ".git").exists():
        edited = _restore_scenes(_edited())
        if edited:
            print("You have edited files the course tracks:\n" + "\n".join(edited) + "\n")
            print("Move your changes into work/ (uv run lab <name> makes the copy), then run this again.")
            return 1
        origin = _origin_is_the_course()
        if origin is False:
            print(f"This clone points at a fork, which does not receive the course's updates;")
            print(f"pointing it back at {COURSE_URL}.")
            run("git", "remote", "set-url", "origin", COURSE_URL)
        elif origin is None:
            run("git", "remote", "add", "origin", COURSE_URL)
        if run("git", "pull", "--ff-only", "origin", "main") != 0:
            print("The pull did not go through. Bring this output to office hours.")
            return 1
    else:
        print("This folder is not a git clone (it came from Download ZIP), so it cannot be updated.")
        print("Replace it: in a terminal, in your Documents folder, run")
        print("    git clone https://github.com/ricopicone/me465-labs.git")
        print("then move this folder's work/ (if any) into the new me465-labs, delete this folder,")
        print("and run uv run update there. See the README, step 4.")
        return 1
    if run("uv", "sync") != 0:
        print("Package sync failed. If it says a file could not be removed (\"Access is denied\" on")
        print("Windows), JupyterLab is still running: stop it (Ctrl+C in its terminal, or close")
        print("that terminal), then run this again. Otherwise bring this output to office hours.")
        return 1
    print("up to date")
    print("If JupyterLab or CoppeliaSim was open, quit them and start again from uv run lab.")
    from me465.lab import LABS, template_changed

    for lab in sorted(p.name for p in LABS.iterdir() if (p / f"{p.name}.ipynb").exists()):
        if template_changed(lab):
            print(f"NOTE: labs/{lab}/{lab}.ipynb changed. Your copy in work/ is untouched; to start")
            print(f"      from the new version run: uv run lab {lab} --fresh  (your copy is kept)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
