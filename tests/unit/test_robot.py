"""Robot movement and swept-collision tests."""

import numpy as np

from robot_vacuum_ddpg.simulator.geometry import Pose, Rectangle
from robot_vacuum_ddpg.simulator.map_loader import FloorMap
from robot_vacuum_ddpg.simulator.robot import Robot, RobotConfig


def test_robot_moves_continuously() -> None:
    floor_map = FloorMap("empty", Rectangle(0.0, 0.0, 10.0, 10.0), Pose(1.0, 1.0, 0.0), ())
    robot = Robot(
        floor_map.start_pose,
        RobotConfig(radius=0.2, time_step=0.5, max_linear_speed=2.0, max_angular_speed=1.0),
    )

    result = robot.move(np.asarray([0.5, 0.0], dtype=np.float32), floor_map)

    assert result.collision is False
    assert robot.pose.x == 1.5
    assert robot.pose.y == 1.0
    assert robot.linear_velocity == 1.0


def test_swept_collision_rejects_entire_pose() -> None:
    floor_map = FloorMap(
        "thin_obstacle",
        Rectangle(0.0, 0.0, 10.0, 10.0),
        Pose(1.0, 5.0, 0.0),
        (Rectangle(2.0, 4.0, 2.1, 6.0),),
    )
    robot = Robot(
        floor_map.start_pose,
        RobotConfig(radius=0.2, time_step=1.0, max_linear_speed=3.0, max_angular_speed=1.0),
    )

    result = robot.move(np.asarray([1.0, 0.0], dtype=np.float32), floor_map)

    assert result.collision is True
    assert robot.pose == floor_map.start_pose
    assert robot.linear_velocity == 0.0
    assert robot.angular_velocity == 0.0
