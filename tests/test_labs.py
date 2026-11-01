"""Every lab notebook is a valid notebook whose code cells compile (no simulator needed)."""

from pathlib import Path

import nbformat
import pytest

LABS = sorted((Path(__file__).resolve().parent.parent / "labs").glob("*/*.ipynb"))


@pytest.mark.parametrize("path", LABS, ids=lambda p: p.parent.name)
def test_notebook_is_valid_and_compiles(path):
    nb = nbformat.read(path, as_version=4)
    nbformat.validate(nb)
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        source = "\n".join(line for line in cell.source.splitlines() if not line.startswith("%"))
        compile(source, f"{path.name}[{i}]", "exec")
