"""Continuous robot kinematics and collision-safe pose updates."""

from dataclasses import dataclass
from math import cos, sin

import numpy as np

from robot_vacuum_ddpg.simulator.geometry import (
    EPSILON,
    Pose,
    Rectangle,
    segment_intersects_rectangle,
    wrap_angle,
)
from robot_vacuum_ddpg.simulator.map_loader import FloorMap


@dataclass(frozen=True, slots=True)
class RobotConfig:
    """Physical parameters for the simplified circular robot."""

    radius: float
    time_step: float
    max_linear_speed: float
    max_angular_speed: float

    def __post_init__(self) -> None:
        """Validate positive physical parameters."""
        if min(
            self.radius,
            self.time_step,
            self.max_linear_speed,
            self.max_angular_speed,
        ) <= 0.0:
            raise ValueError("Robot physical parameters must be positive")


@dataclass(frozen=True, slots=True)
class MovementResult:
    """Outcome of one attempted robot movement."""

    action: np.ndarray
    collision: bool
    attempted_pose: Pose


class Robot:
    """Circular robot with differential-drive-like unicycle kinematics."""

    def __init__(self, start_pose: Pose, config: RobotConfig) -> None:
        self.config = config
        self.pose = start_pose
        self.linear_velocity = 0.0
        self.angular_velocity = 0.0

    def reset(self, pose: Pose) -> None:
        """Reset pose and resulting velocities."""
        self.pose = pose
        self.linear_velocity = 0.0
        self.angular_velocity = 0.0

    @staticmethod
    def clip_action(action: np.ndarray) -> np.ndarray:
        """Validate and clip a two-value continuous action."""
        array = np.asarray(action, dtype=np.float32)
        if array.shape != (2,):
            raise ValueError(f"action must have shape (2,), got {array.shape}")
        if not np.isfinite(array).all():
            raise ValueError("action values must be finite")
        return np.clip(array, -1.0, 1.0).astype(np.float32)

    def move(self, action: np.ndarray, floor_map: FloorMap) -> MovementResult:
        """Attempt one movement and reject the full pose on collision."""
        clipped = self.clip_action(action)
        linear_velocity = float(clipped[0]) * self.config.max_linear_speed
        angular_velocity = float(clipped[1]) * self.config.max_angular_speed
        next_theta = wrap_angle(
            self.pose.theta + angular_velocity * self.config.time_step
        )
        attempted = Pose(
            self.pose.x + linear_velocity * cos(next_theta) * self.config.time_step,
            self.pose.y + linear_velocity * sin(next_theta) * self.config.time_step,
            next_theta,
        )
        collision = self._path_collides(attempted, floor_map)
        if collision:
            self.linear_velocity = 0.0
            self.angular_velocity = 0.0
        else:
            self.pose = attempted
            self.linear_velocity = linear_velocity
            self.angular_velocity = angular_velocity
        return MovementResult(clipped, collision, attempted)

    def _path_collides(self, attempted: Pose, floor_map: FloorMap) -> bool:
        radius = self.config.radius
        safe_bounds = Rectangle(
            floor_map.bounds.min_x + radius,
            floor_map.bounds.min_y + radius,
            floor_map.bounds.max_x - radius,
            floor_map.bounds.max_y - radius,
        )
        if not (
            safe_bounds.min_x + EPSILON < attempted.x < safe_bounds.max_x - EPSILON
            and safe_bounds.min_y + EPSILON < attempted.y < safe_bounds.max_y - EPSILON
        ):
            return True
        return any(
            segment_intersects_rectangle(
                self.pose.x,
                self.pose.y,
                attempted.x,
                attempted.y,
                obstacle.expanded(radius),
            )
            for obstacle in floor_map.obstacles
        )
