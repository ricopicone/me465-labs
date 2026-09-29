"""`uv run lab <name>` — open a lab's notebook in JupyterLab, working on your own copy.

The notebooks under `labs/` are templates the course updates; you never edit
them. The first time you open a lab, its notebook is copied to `work/`, which
git ignores, and JupyterLab opens that copy. Later runs open your copy again.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LABS = ROOT / "labs"
WORK = ROOT / "work"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    launch = "--no-launch" not in args
    names = [a for a in args if not a.startswith("--")]
    available = sorted(p.name for p in LABS.iterdir() if (p / f"{p.name}.ipynb").exists())
    if len(names) != 1 or names[0] not in available:
        print("usage: uv run lab <name>    (one of: " + ", ".join(available) + ")")
        return 2
    name = names[0]
    template = LABS / name / f"{name}.ipynb"
    WORK.mkdir(exist_ok=True)
    copy = WORK / f"{name}.ipynb"
    if copy.exists():
        print(f"opening your copy, {copy.relative_to(ROOT)}")
    else:
        shutil.copy(template, copy)
        print(f"copied {template.relative_to(ROOT)} to {copy.relative_to(ROOT)}: work there")
    if not launch:
        return 0
    return subprocess.call([sys.executable, "-m", "jupyterlab", str(copy)], cwd=ROOT)
