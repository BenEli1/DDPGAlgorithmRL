"""Deterministic ray distance sensors for local wall perception."""

from math import cos, sin

import numpy as np

from robot_vacuum_ddpg.simulator.geometry import Pose, ray_rectangle_distances
from robot_vacuum_ddpg.simulator.map_loader import FloorMap


class DistanceSensorArray:
    """Cast configurable rays against map bounds and obstacles."""

    def __init__(self, relative_angles: tuple[float, ...], max_range: float) -> None:
        if not relative_angles:
            raise ValueError("At least one sensor angle is required")
        if max_range <= 0.0:
            raise ValueError("Sensor max_range must be positive")
        self.relative_angles = relative_angles
        self.max_range = max_range

    def read(self, pose: Pose, floor_map: FloorMap) -> np.ndarray:
        """Return nearest normalized distance for every configured ray."""
        readings = [self._read_one(pose, angle, floor_map) for angle in self.relative_angles]
        return np.asarray(readings, dtype=np.float32)

    def _read_one(self, pose: Pose, relative_angle: float, floor_map: FloorMap) -> float:
        angle = pose.theta + relative_angle
        direction_x = cos(angle)
        direction_y = sin(angle)
        distances = ray_rectangle_distances(
            pose.x,
            pose.y,
            direction_x,
            direction_y,
            floor_map.bounds,
        )
        for obstacle in floor_map.obstacles:
            distances.extend(
                ray_rectangle_distances(
                    pose.x,
                    pose.y,
                    direction_x,
                    direction_y,
                    obstacle,
                )
            )
        nearest = min((value for value in distances if value >= 0.0), default=self.max_range)
        return min(nearest, self.max_range) / self.max_range
