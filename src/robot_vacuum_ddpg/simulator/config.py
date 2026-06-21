"""Validated simulator configuration assembled from versioned JSON data."""

from dataclasses import dataclass
from math import radians
from typing import Any

from robot_vacuum_ddpg.simulator.rewards import RewardConfig
from robot_vacuum_ddpg.simulator.robot import RobotConfig


@dataclass(frozen=True, slots=True)
class EnvironmentConfig:
    """Keep physical and reward choices outside environment lifecycle code."""

    robot: RobotConfig
    cleaning_radius: float
    sensor_max_range: float
    sensor_angles: tuple[float, ...]
    coverage_cell_size: float
    target_coverage: float
    max_steps: int
    terminate_on_collision: bool
    reward: RewardConfig

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EnvironmentConfig":
        """Convert JSON values once so the domain receives typed parameters."""
        reward_data = data.get("reward")
        if not isinstance(reward_data, dict):
            raise ValueError("reward configuration must be an object")
        angles = data.get("sensor_angles_degrees")
        if not isinstance(angles, list) or not angles:
            raise ValueError("sensor_angles_degrees must be a non-empty list")
        config = cls(
            robot=RobotConfig(
                radius=float(data["robot_radius"]),
                time_step=float(data["time_step"]),
                max_linear_speed=float(data["max_linear_speed"]),
                max_angular_speed=float(data["max_angular_speed"]),
            ),
            cleaning_radius=float(data["cleaning_radius"]),
            sensor_max_range=float(data["sensor_max_range"]),
            sensor_angles=tuple(radians(float(value)) for value in angles),
            coverage_cell_size=float(data["coverage_cell_size"]),
            target_coverage=float(data["target_coverage"]),
            max_steps=int(data["max_steps"]),
            terminate_on_collision=bool(data.get("terminate_on_collision", False)),
            reward=RewardConfig(**reward_data),
        )
        config._validate()
        return config

    def _validate(self) -> None:
        if min(self.cleaning_radius, self.sensor_max_range, self.coverage_cell_size) <= 0.0:
            raise ValueError("Simulator distances and coverage_cell_size must be positive")
        if not 0.0 < self.target_coverage <= 1.0:
            raise ValueError("target_coverage must be in (0, 1]")
        if self.max_steps <= 0:
            raise ValueError("max_steps must be positive")
