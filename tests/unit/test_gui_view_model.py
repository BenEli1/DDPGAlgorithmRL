"""Tests for GUI-independent snapshot conversion helpers."""

from math import pi

import pytest

from robot_vacuum_ddpg.gui.view_model import heading_endpoint, status_values, world_to_canvas
from robot_vacuum_ddpg.sdk import DemoSnapshot


def test_world_to_canvas_preserves_bounds_and_inverts_y() -> None:
    lower_left = world_to_canvas((0.0, 0.0), (0.0, 0.0, 10.0, 8.0), (760, 560))
    upper_right = world_to_canvas((10.0, 8.0), (0.0, 0.0, 10.0, 8.0), (760, 560))

    assert lower_left[0] < upper_right[0]
    assert lower_left[1] > upper_right[1]


def test_heading_and_status_conversion() -> None:
    endpoint = heading_endpoint((2.0, 3.0), pi / 2.0, length=1.0)
    snapshot = DemoSnapshot(
        step=4,
        total_reward=1.25,
        collisions=2,
        coverage_percent=3.5,
        current_action=(0.5, -0.25),
        state_vector_length=13,
        map_name="simple_house",
        bounds=(0.0, 0.0, 10.0, 8.0),
        obstacles=(),
        robot_position=(2.0, 3.0),
        robot_heading=pi / 2.0,
        trajectory=((2.0, 3.0),),
        collision_points=(),
        cleaned_cells=(),
        done=False,
    )

    assert endpoint == pytest.approx((2.0, 4.0))
    assert status_values(snapshot, "result.png") == {
        "step": "4",
        "reward": "1.250",
        "collisions": "2",
        "coverage": "3.50%",
        "action": "[0.500, -0.250]",
        "state_length": "13",
        "artifact": "result.png",
    }
