"""A thin bridge from Python to a running CoppeliaSim, through its ZMQ remote API.

This is deliberately small: connect, load the course scene, step the physics,
read and command the joints, and read where frames are. Everything is in
stepping mode, so the simulation advances only when you call `step` — your
code decides when time moves, the way a real controller samples a real plant.

    from me465.sim import Sim

    s = Sim.connect()
    s.load_scene()
    s.start()
    s.set_joint_targets([0, 0, 0, 0, 0, 0])
    s.settle()
    print(s.joint_positions())
    print(s.tool_pose())
    s.stop()
"""

from __future__ import annotations

import socket
import time
from pathlib import Path

import numpy as np

HOST = "localhost"
PORT = 23000

#: The course scene, built by `me465.build_scene` from CoppeliaSim's own UR5.
SCENE = Path(__file__).resolve().parent / "scenes" / "ur5.ttt"


class NotRunning(RuntimeError):
    """CoppeliaSim is not running, or its remote API server is not listening."""


def port_open(host: str = HOST, port: int = PORT, timeout: float = 2.0) -> bool:
    """Whether something is listening on the remote API port.

    The ZMQ client waits forever for a server that is not there, so we knock
    on the port first and fail with a message instead of a hang.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _matrix(flat) -> np.ndarray:
    """CoppeliaSim's 12-number pose (a 3x4, row by row) as a 4x4 transform."""
    T = np.eye(4)
    T[:3, :] = np.reshape(flat, (3, 4))
    return T


class Sim:
    """One connection to CoppeliaSim, with the UR5 of the course scene."""

    def __init__(self, client, sim):
        self.client = client
        self.sim = sim
        self.joints: list[int] = []
        self.base = None
        self.tool = None

    # --- connecting and loading ----------------------------------------------

    @classmethod
    def connect(cls, host: str = HOST, port: int = PORT) -> "Sim":
        if not port_open(host, port):
            raise NotRunning(
                f"Nothing is listening on {host}:{port}. Start CoppeliaSim first "
                "(just open it; the remote API server starts by itself)."
            )
        from coppeliasim_zmqremoteapi_client import RemoteAPIClient

        client = RemoteAPIClient(host, port)
        return cls(client, client.require("sim"))

    def version(self) -> str:
        v = self.sim.getInt32Param(self.sim.intparam_program_full_version)
        return f"{v // 1000000}.{v // 10000 % 100}.{v // 100 % 100}"

    def load_scene(self, path: str | Path = SCENE) -> None:
        """Stop anything running, open the scene, and find the UR5 in it."""
        self.stop()
        self.sim.loadScene(str(Path(path).resolve()))
        self._find_robot()

    def _find_robot(self) -> None:
        sim = self.sim
        self.base = sim.getObject("/UR5")
        self.joints = [sim.getObject("/UR5/joint", {"index": i}) for i in range(6)]
        self.tool = sim.getObject("/UR5/tool")

    # --- time ----------------------------------------------------------------

    def start(self) -> None:
        """Start the simulation in stepping mode: it waits for `step`."""
        self.sim.setStepping(True)
        self.sim.startSimulation()

    def stop(self) -> None:
        sim = self.sim
        if sim.getSimulationState() != sim.simulation_stopped:
            sim.stopSimulation()
            while sim.getSimulationState() != sim.simulation_stopped:
                time.sleep(0.01)

    def step(self, n: int = 1) -> None:
        for _ in range(n):
            self.sim.step()

    @property
    def dt(self) -> float:
        return self.sim.getSimulationTimeStep()

    @property
    def time(self) -> float:
        return self.sim.getSimulationTime()

    # --- the joints ----------------------------------------------------------

    def joint_positions(self) -> np.ndarray:
        """The six joint angles the simulator measures right now, in radians."""
        return np.array([self.sim.getJointPosition(j) for j in self.joints])

    def set_joint_targets(self, theta) -> None:
        """Command the six joints' position controllers (radians)."""
        for j, q in zip(self.joints, theta, strict=True):
            self.sim.setJointTargetPosition(j, float(q))

    def settle(self, seconds: float = 3.0, tol: float = 1e-5) -> np.ndarray:
        """Step until the joints stop moving (or `seconds` pass); return where they stopped."""
        previous = self.joint_positions()
        for _ in range(max(1, int(seconds / self.dt))):
            self.step()
            now = self.joint_positions()
            if np.max(np.abs(now - previous)) < tol:
                return now
            previous = now
        return previous

    # --- frames --------------------------------------------------------------

    def pose(self, handle: int, relative_to: int | None = None) -> np.ndarray:
        """A frame's 4x4 transform, in the world frame unless `relative_to` is given."""
        ref = self.sim.handle_world if relative_to is None else relative_to
        return _matrix(self.sim.getObjectMatrix(handle, ref))

    def tool_pose(self) -> np.ndarray:
        """The tool (flange) frame in the world frame: the simulator's ground truth."""
        return self.pose(self.tool)

    def joint_frames(self) -> list[np.ndarray]:
        """Each joint's frame in the world frame. A joint turns about its frame's z-axis."""
        return [self.pose(j) for j in self.joints]
