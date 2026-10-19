"""uv run update puts back a scene CoppeliaSim saved over, and still refuses to pull over
any other edited file (Sim 1, October 2026). A throwaway git repository stands in."""

import subprocess

import pytest

from me465 import update

SCENE = update.SCENES[0]


@pytest.fixture
def repo(tmp_path, monkeypatch):
    def git(*a):
        subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (tmp_path / SCENE).parent.mkdir(parents=True)
    (tmp_path / SCENE).write_bytes(b"course scene")
    (tmp_path / "labs").mkdir()
    (tmp_path / "labs" / "sim1.ipynb").write_text("course notebook")
    git("add", ".")
    git("commit", "-qm", "course")
    monkeypatch.setattr(update, "ROOT", tmp_path)
    return tmp_path


def test_a_saved_scene_is_put_back(repo):
    (repo / SCENE).write_bytes(b"saved by CoppeliaSim")
    assert update._restore_scenes(update._edited()) == []
    assert (repo / SCENE).read_bytes() == b"course scene"
    assert update._edited() == []


def test_other_edits_are_left_alone_and_reported(repo):
    (repo / SCENE).write_bytes(b"saved by CoppeliaSim")
    (repo / "labs" / "sim1.ipynb").write_text("student answers")
    assert update._restore_scenes(update._edited()) == ["labs/sim1.ipynb"]
    assert (repo / "labs" / "sim1.ipynb").read_text() == "student answers"
    assert (repo / SCENE).read_bytes() == b"course scene"


def test_main_refuses_to_pull_over_other_edits(repo, capsys):
    (repo / "labs" / "sim1.ipynb").write_text("student answers")
    assert update.main() == 1
    assert "labs/sim1.ipynb" in capsys.readouterr().out
