"""`uv run check` — is this machine ready for a lab day?

Runs each step in order and stops at the first failure, with the fix for it.
Paste the whole output into the setup checkpoint on the course site.
"""

from __future__ import annotations

import platform
import sys

# Colour only on a terminal: pasted into the checkpoint, escape codes are noise.
if sys.stdout.isatty():
    GREEN, RED, RESET = "\033[32m", "\033[31m", "\033[0m"
else:
    GREEN = RED = RESET = ""


def ok(msg: str) -> None:
    print(f"  {GREEN}✓{RESET} {msg}")


def fail(msg: str, fix: str) -> None:
    print(f"  {RED}✗ {msg}{RESET}")
    print(f"    Fix: {fix}")
    print(f"\nme465 check FAILED — {platform.system()} {platform.machine()}, Python {platform.python_version()}")
    sys.exit(1)


def main() -> None:
    print("me465 check\n")

    try:
        import numpy  # noqa: F401
        import modern_robotics  # noqa: F401
        import coppeliasim_zmqremoteapi_client  # noqa: F401
    except ImportError as e:
        fail(f"a Python package is missing ({e.name})",
             "run the command from inside the me465-labs folder, as `uv run check`, so uv installs them.")
    ok(f"Python {platform.python_version()} with numpy, modern_robotics and the CoppeliaSim client")

    from me465.sim import PORT, SCENE, NotRunning, Sim

    try:
        s = Sim.connect()
    except NotRunning:
        fail(f"CoppeliaSim is not running (nothing on port {PORT})",
             "open CoppeliaSim, wait for its window, then run this again. "
             "If it is open, check that a firewall is not blocking localhost.")
    version = s.version()
    ok(f"connected to CoppeliaSim {version}")
    major, minor = (int(x) for x in version.split(".")[:2])
    if (major, minor) < (4, 10):
        fail(f"CoppeliaSim {version} is too old", "install the current version (4.10 or newer, the Edu edition) from coppeliarobotics.com.")

    try:
        s.load_scene()
    except Exception as e:  # the remote side reports its own error text
        fail(f"could not load the course scene ({e})",
             f"make sure {SCENE} exists; `git pull` or re-download the course repo.")
    ok("loaded the course scene: a UR5 on its stand")

    import numpy as np

    try:
        s.start()
        s.set_joint_targets([0.3, -0.5, 0.8, 0.0, 0.4, 0.0])
        reached = s.settle()
        tool = s.tool_pose()
    finally:
        s.stop()
    if np.max(np.abs(reached - [0.3, -0.5, 0.8, 0.0, 0.4, 0.0])) > 1e-2:
        fail(f"the arm did not reach the commanded angles (got {np.round(reached, 3)})",
             "reload the scene (File > Open scene) and run again; if it persists, tell your instructor.")
    ok(f"stepped the physics and moved the arm; tool at {np.round(tool[:3, 3], 3)} m")

    print(f"\nme465 check PASSED — CoppeliaSim {version}, {platform.system()} {platform.machine()}, "
          f"Python {platform.python_version()}")


if __name__ == "__main__":
    main()
