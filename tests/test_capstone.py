"""The capstone cell's arithmetic, without a simulator."""

import numpy as np

from me465 import capstone


def test_a_cube_has_24_rotations():
    Rs = capstone._CUBE_SYMMETRIES
    assert len(Rs) == 24
    assert all(np.isclose(np.linalg.det(R), 1.0) for R in Rs)
    assert len({tuple(R.ravel()) for R in Rs}) == 24


def test_frames_are_in_s_on_top_of_the_pedestal():
    assert np.allclose(capstone.T_WS[:3, 3], [0, 0, capstone.PEDESTAL])
    assert np.allclose(capstone.T_SW @ capstone.T_WS, np.eye(4))


def test_a_quarter_turn_is_no_error_for_a_cube():
    Rz = np.array([[0.0, -1, 0], [1, 0, 0], [0, 0, 1]])
    assert min(capstone._angle(Q @ Rz) for Q in capstone._CUBE_SYMMETRIES) < 1e-9
