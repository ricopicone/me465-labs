"""open_lab and settle must leave CoppeliaSim released between cells: idle in stepping mode,
its window locks up and offers an 'abort execution' banner that, clicked, strands the
notebook (Sim 1, October 2026). A fake scene stands in for the simulator."""

import numpy as np
import pytest

import me465


class FakeArm:
    n = 6

    def __init__(self, scene):
        self.scene, self.target, self.q = scene, np.zeros(6), np.zeros(6)

    def mode(self, _):
        pass

    def command_positions(self, theta):
        self.target = np.asarray(theta, float)

    def theta(self):
        return self.q.copy()


class FakeScene:
    dt = 0.05

    def __init__(self, *a, **k):
        self.released, self.steps, self.fail_at = False, 0, None
        self.sim = self
        self.simulation_stopped = 0
        self.loaded = None
        self.arm_ = FakeArm(self)

    # the sim calls open_lab makes
    def getSimulationState(self):
        return 0

    def loadScene(self, path):
        self.loaded = path

    def arm(self, path):
        return self.arm_

    def start(self):
        pass

    def stop(self):
        pass

    def step(self):
        if self.fail_at is not None and self.steps == self.fail_at:
            raise ConnectionError("simulator went away")
        self.released = False  # as screws.coppelia.Scene.step takes the clock back
        self.steps += 1
        a = self.arm_
        a.q = a.q + 0.5 * (a.target - a.q)  # a motor that converges

    def release(self):
        self.released = True


@pytest.fixture
def fake(monkeypatch):
    import screws.coppelia

    made = {}

    def make(*a, **k):
        made["scene"] = FakeScene()
        return made["scene"]

    monkeypatch.setattr(screws.coppelia, "Scene", make)
    return made


def test_open_lab_returns_released(fake):
    scene, arm = me465.open_lab()
    assert scene.loaded and scene.released


def test_settle_steps_then_releases():
    scene = FakeScene()
    scene.arm_.command_positions([0.3, 0, 0, 0, 0, 0])
    q = me465.settle(scene, scene.arm_)
    assert scene.steps > 1 and scene.released
    assert np.allclose(q, [0.3, 0, 0, 0, 0, 0], atol=1e-4)


def test_settle_releases_even_when_stepping_fails():
    scene = FakeScene()
    scene.arm_.command_positions([0.3, 0, 0, 0, 0, 0])
    scene.fail_at = 3
    with pytest.raises(ConnectionError):
        me465.settle(scene, scene.arm_)
    assert scene.released
