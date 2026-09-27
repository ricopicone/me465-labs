"""Build the course scene from CoppeliaSim's own UR5 model. Instructors only.

The scene students load is not drawn by hand: this script makes it, so what is
in it is written down. Run it against a running CoppeliaSim:

    uv run python -m me465.build_scene

It starts from an empty scene (floor and lights), loads the UR5 that ships with
CoppeliaSim, stands it on a 0.4 m pedestal, removes the demo script that would otherwise drive the arm on its
own, marks the flange with a `tip` frame, and saves `scenes/ur5.ttt`.
"""

from screws.coppelia import connect

from me465 import PEDESTAL, SCENE


def build() -> None:
    sim = connect()
    if sim.getSimulationState() != sim.simulation_stopped:
        sim.stopSimulation()
        while sim.getSimulationState() != sim.simulation_stopped:
            pass
    sim.closeScene()  # leaves the default empty scene: floor, lights, camera

    models = sim.getStringParam(sim.stringparam_resourcesdir) + "/models"
    base = sim.loadModel(models + "/robots/non-mobile/UR5.ttm")

    # On a stand, as a real UR5 is mounted. On the floor, MR's home pose (the
    # arm stretched out level with the base) would put the tool into the floor.
    # It also means the world frame and the robot's base frame {s} differ, by
    # a pure lift of PEDESTAL metres, which is the first thing students find.
    stand = sim.createPrimitiveShape(sim.primitiveshape_cuboid, [0.3, 0.3, PEDESTAL])
    sim.setObjectAlias(stand, "pedestal")
    sim.setObjectPosition(stand, [0, 0, PEDESTAL / 2], sim.handle_world)
    sim.setShapeColor(stand, None, sim.colorcomponent_ambient_diffuse, [0.35, 0.35, 0.38])
    p = sim.getObjectPosition(base, sim.handle_world)
    sim.setObjectPosition(base, [p[0], p[1], p[2] + PEDESTAL], sim.handle_world)

    # The model's demo: a threaded script that sweeps the arm through three
    # poses. Students' code is the only thing that moves the robot here.
    sim.removeObjects([sim.getObject("/UR5/Script")])

    # The flange frame is a force sensor called `connection`. A dummy in the
    # same place called `tip` is what screws' Arm takes as the tip, and what
    # `arm.tip_frame()` reads.
    connection = sim.getObject("/UR5/connection")
    tool = sim.createDummy(0.02)
    sim.setObjectAlias(tool, "tip")
    sim.setObjectParent(tool, connection, False)
    sim.setObjectMatrix(tool, [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0], connection)

    SCENE.parent.mkdir(parents=True, exist_ok=True)
    sim.saveScene(str(SCENE))
    print(f"saved {SCENE} (UR5 handle {base})")


if __name__ == "__main__":
    build()
