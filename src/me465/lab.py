"""`uv run lab <name>` — open a lab's notebook in JupyterLab, working on your own copy.

The notebooks under `labs/` are templates the course updates; you never edit
them. The first time you open a lab, its notebook is copied to `work/`, which
git ignores, and JupyterLab opens that copy. Later runs open your copy again.

When the course has updated a lab since you copied it, `lab` says so.
`uv run lab <name> --fresh` sets your copy aside (as `work/<name>-previous.ipynb`)
and starts again from the new template.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LABS = ROOT / "labs"
WORK = ROOT / "work"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stamp(name: str) -> Path:
    return WORK / f".{name}.template"


def template_changed(name: str) -> bool:
    """True if labs/<name>/<name>.ipynb differs from the template the work copy was made from."""
    template = LABS / name / f"{name}.ipynb"
    stamp = _stamp(name)
    if not (WORK / f"{name}.ipynb").exists():
        return False
    # a copy made before stamps existed: no record of its origin, so say so
    return not stamp.exists() or stamp.read_text().strip() != _digest(template)


def copy_template(name: str, *, fresh: bool = False) -> Path:
    """Make (or refresh, with fresh=True) the work copy of a lab; returns its path."""
    template = LABS / name / f"{name}.ipynb"
    WORK.mkdir(exist_ok=True)
    copy = WORK / f"{name}.ipynb"
    if copy.exists() and fresh:
        previous = WORK / f"{name}-previous.ipynb"
        k = 2
        while previous.exists():
            previous = WORK / f"{name}-previous-{k}.ipynb"
            k += 1
        shutil.move(copy, previous)
        print(f"set your old copy aside as {previous.relative_to(ROOT)}")
    if not copy.exists():
        shutil.copy(template, copy)
        _stamp(name).write_text(_digest(template))
        print(f"copied {template.relative_to(ROOT)} to {copy.relative_to(ROOT)}: work there")
    else:
        print(f"opening your copy, {copy.relative_to(ROOT)}")
        if template_changed(name):
            print(f"NOTE: the course has updated labs/{name}/{name}.ipynb since you copied it.")
            print(f"      To start from the new version: uv run lab {name} --fresh  (your copy is kept)")
    for asset in (LABS / name).iterdir():  # figures the notebook shows, alongside the copy
        if asset.suffix.lower() in (".png", ".jpg", ".svg", ".pdf"):
            target = WORK / asset.name
            if not target.exists() or _digest(target) != _digest(asset):
                shutil.copy(asset, target)
    return copy


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    launch = "--no-launch" not in args
    fresh = "--fresh" in args
    names = [a for a in args if not a.startswith("--")]
    available = sorted(p.name for p in LABS.iterdir() if (p / f"{p.name}.ipynb").exists())
    if len(names) != 1 or names[0] not in available:
        print("usage: uv run lab <name> [--fresh]    (one of: " + ", ".join(available) + ")")
        return 2
    copy = copy_template(names[0], fresh=fresh)
    if not launch:
        return 0
    return subprocess.call([sys.executable, "-m", "jupyterlab", str(copy)], cwd=ROOT)
