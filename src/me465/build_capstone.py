"""Build the capstone scene from the course scene. Instructors only.

Like `build_scene`, the scene is generated, never drawn by hand. Run it against a running
CoppeliaSim (ME465_PORT picks another instance):

    uv run python -m me465.build_capstone

It loads `scenes/ur5.ttt` (the UR5 on its stand, exactly as in Sim 1), and adds:

- a suction cup on the flange: a stalk and a cup, visual only (static, not respondable),
  parented to `tip`, with a dummy `tool` at the cup's face, TOOL_LENGTH along the flange's z;
- a table in front of the arm whose top is level with the top of the pedestal, so the table
  is the plane z = 0 of {s};
- a cube `cube` (dynamic, respondable, 5 cm, 0.1 kg) on the table at CUBE_START;
- a target `target`: a dummy on the table surface at TARGET, carrying a thin green pad
  (static, not respondable) a little larger than the cube.

and saves `scenes/pick_place.ttt`.
"""

from __future__ import annotations

import numpy as np
from screws.coppelia import connect

from me465 import PEDESTAL, SCENE, default_port
from me465.capstone import CAPSTONE_SCENE, CUBE_SIZE

#: Cup face from the flange, along the flange's z, meters.
TOOL_LENGTH = 0.10

#: Where the cube starts and where it goes: (x, y) in {s} and a yaw in degrees.
CUBE_START = (0.45, -0.20, 15.0)
TARGET = (0.40, 0.30, -30.0)

#: Table footprint in the world frame (x from, x to, y from, y to); its top is at PEDESTAL.
TABLE = (0.20, 0.80, -0.55, 0.55)

CUBE_MASS = 0.1
PAD_SIZE = 0.07


def _shape(sim, h, *, static: bool, respondable: bool) -> None:
    sim.setObjectInt32Param(h, sim.shapeintparam_static, 1 if static else 0)
    sim.setObjectInt32Param(h, sim.shapeintparam_respondable, 1 if respondable else 0)


def _color(sim, h, rgb) -> None:
    sim.setShapeColor(h, None, sim.colorcomponent_ambient_diffuse, list(rgb))


def _place(sim, h, x, y, z, yaw_deg=0.0) -> None:
    sim.setObjectPosition(h, [x, y, z], sim.handle_world)
    sim.setObjectOrientation(h, [0.0, 0.0, float(np.radians(yaw_deg))], sim.handle_world)


def build(port: int | None = None) -> None:
    sim = connect(port=default_port(port))
    if sim.getSimulationState() != sim.simulation_stopped:
        sim.stopSimulation()
        while sim.getSimulationState() != sim.simulation_stopped:
            pass
    sim.loadScene(str(SCENE))

    # The suction cup. The arm is at its zero position in the saved scene, and the cup is
    # built along the flange's z there; parented to `tip`, it goes wherever the flange goes.
    tip = sim.getObject("/UR5/tip")
    stalk = sim.createPrimitiveShape(sim.primitiveshape_cylinder, [0.03, 0.03, 0.07], 0)
    cup = sim.createPrimitiveShape(sim.primitiveshape_cylinder, [0.05, 0.05, 0.03], 0)
    tool = sim.createDummy(0.02)
    for h, alias, z in ((stalk, "tool_stalk", 0.035), (cup, "tool_cup", 0.085), (tool, "tool", TOOL_LENGTH)):
        sim.setObjectAlias(h, alias)
        sim.setObjectParent(h, tip, False)
        sim.setObjectMatrix(h, [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, z], tip)
    for h in (stalk, cup):
        _shape(sim, h, static=True, respondable=False)
    _color(sim, stalk, (0.6, 0.6, 0.62))
    _color(sim, cup, (0.12, 0.12, 0.14))

    # The table: a solid block from the floor to the top of the pedestal.
    x0, x1, y0, y1 = TABLE
    table = sim.createPrimitiveShape(sim.primitiveshape_cuboid, [x1 - x0, y1 - y0, PEDESTAL], 0)
    sim.setObjectAlias(table, "table")
    _shape(sim, table, static=True, respondable=True)
    _place(sim, table, (x0 + x1) / 2, (y0 + y1) / 2, PEDESTAL / 2)
    _color(sim, table, (0.78, 0.70, 0.55))

    # The cube, resting on the table.
    cube = sim.createPrimitiveShape(sim.primitiveshape_cuboid, [CUBE_SIZE] * 3, 0)
    sim.setObjectAlias(cube, "cube")
    _shape(sim, cube, static=False, respondable=True)
    sim.computeMassAndInertia(cube, CUBE_MASS / CUBE_SIZE**3)
    cx, cy, cyaw = CUBE_START
    _place(sim, cube, cx, cy, PEDESTAL + CUBE_SIZE / 2, cyaw)
    _color(sim, cube, (0.73, 0.05, 0.18))

    # The target: a frame on the table surface, and a pad to show it.
    target = sim.createDummy(0.02)
    sim.setObjectAlias(target, "target")
    tx, ty, tyaw = TARGET
    _place(sim, target, tx, ty, PEDESTAL, tyaw)
    pad = sim.createPrimitiveShape(sim.primitiveshape_cuboid, [PAD_SIZE, PAD_SIZE, 0.002], 0)
    sim.setObjectAlias(pad, "target_pad")
    _shape(sim, pad, static=True, respondable=False)
    sim.setObjectParent(pad, target, False)
    sim.setObjectMatrix(pad, [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0.001], target)
    _color(sim, pad, (0.20, 0.65, 0.30))

    CAPSTONE_SCENE.parent.mkdir(parents=True, exist_ok=True)
    sim.saveScene(str(CAPSTONE_SCENE))
    print(f"saved {CAPSTONE_SCENE}")


if __name__ == "__main__":
    build()
