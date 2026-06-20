"""Framework-free 2D robotic vacuum environment."""

from dataclasses import dataclass
from math import pi, radians
from typing import Any

import numpy as np

from robot_vacuum_ddpg.simulator.geometry import Pose
from robot_vacuum_ddpg.simulator.map_loader import FloorMap
from robot_vacuum_ddpg.simulator.rewards import RewardConfig, calculate_reward
from robot_vacuum_ddpg.simulator.robot import Robot, RobotConfig
from robot_vacuum_ddpg.simulator.sensors import DistanceSensorArray


@dataclass(frozen=True, slots=True)
class EnvironmentConfig:
    """Validated simulator parameters used by VacuumEnvironment."""

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
        """Build a validated environment configuration from JSON data."""
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


class VacuumEnvironment:
    """Small custom environment exposing reset and continuous-action step methods."""

    def __init__(self, floor_map: FloorMap, config: EnvironmentConfig) -> None:
        self.floor_map = floor_map
        self.config = config
        self.robot = Robot(floor_map.start_pose, config.robot)
        self.sensors = DistanceSensorArray(config.sensor_angles, config.sensor_max_range)
        self._cleanable_cells = self._build_cleanable_cells()
        if len(self._cleanable_cells) == 0:
            raise ValueError("Map contains no cleanable coverage cells")
        self._cleaned = np.zeros(len(self._cleanable_cells), dtype=np.bool_)
        self.trajectory: list[Pose] = []
        self.step_count = 0
        self.last_collision = False
        self.done = False
        self._rng = np.random.default_rng()

    @property
    def state_dim(self) -> int:
        """Return the observation-vector size derived from sensor count."""
        return len(self.config.sensor_angles) + 6

    @property
    def action_dim(self) -> int:
        """Return the fixed continuous action-vector size."""
        return 2

    @property
    def coverage_ratio(self) -> float:
        """Return the fraction of free coverage cells cleaned this episode."""
        return float(np.mean(self._cleaned))

    def reset(self, seed: int | None = None) -> np.ndarray:
        """Reset episode state and return the initial continuous observation."""
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        self.robot.reset(self.floor_map.start_pose)
        self._cleaned.fill(False)
        self.trajectory = [self.robot.pose]
        self.step_count = 0
        self.last_collision = False
        self.done = False
        self._mark_cleaned()
        return self._state()

    def sample_random_action(self) -> np.ndarray:
        """Sample a continuous random action for simulator demos only."""
        return self._rng.uniform(-1.0, 1.0, size=2).astype(np.float32)

    def step(self, action: np.ndarray) -> tuple[np.ndarray, float, bool, dict[str, Any]]:
        """Advance the simulator by one step using a continuous action."""
        if self.done:
            raise RuntimeError("Episode is done; call reset before another step")
        movement = self.robot.move(action, self.floor_map)
        self.last_collision = movement.collision
        self.trajectory.append(self.robot.pose)
        newly_cleaned = self._mark_cleaned()
        self.step_count += 1
        reached_target = self.coverage_ratio >= self.config.target_coverage
        reached_limit = self.step_count >= self.config.max_steps
        collision_end = movement.collision and self.config.terminate_on_collision
        self.done = reached_target or reached_limit or collision_end
        breakdown = calculate_reward(
            newly_cleaned,
            movement.collision,
            reached_target,
            movement.action,
            self.config.reward,
        )
        reason = None
        if reached_target:
            reason = "coverage"
        elif collision_end:
            reason = "collision"
        elif reached_limit:
            reason = "max_steps"
        info: dict[str, Any] = {
            "collision": movement.collision,
            "attempted_pose": movement.attempted_pose,
            "pose": self.robot.pose,
            "newly_cleaned_cells": newly_cleaned,
            "coverage_ratio": self.coverage_ratio,
            "step_count": self.step_count,
            "terminated_reason": reason,
            "reward_components": breakdown.as_dict(),
        }
        return self._state(), breakdown.total, self.done, info

    def _build_cleanable_cells(self) -> np.ndarray:
        bounds = self.floor_map.bounds
        spacing = self.config.coverage_cell_size
        x_values = np.arange(bounds.min_x + spacing / 2.0, bounds.max_x, spacing)
        y_values = np.arange(bounds.min_y + spacing / 2.0, bounds.max_y, spacing)
        return np.asarray(
            [
                (x, y)
                for x in x_values
                for y in y_values
                if self.floor_map.point_is_free(float(x), float(y))
            ],
            dtype=np.float32,
        )

    def _mark_cleaned(self) -> int:
        delta = self._cleanable_cells - np.asarray(
            [self.robot.pose.x, self.robot.pose.y], dtype=np.float32
        )
        in_radius = np.sum(np.square(delta), axis=1) <= self.config.cleaning_radius**2
        newly_cleaned = in_radius & ~self._cleaned
        self._cleaned |= in_radius
        return int(np.count_nonzero(newly_cleaned))

    def _state(self) -> np.ndarray:
        sensor_values = self.sensors.read(self.robot.pose, self.floor_map)
        state = np.concatenate(
            (
                sensor_values,
                np.asarray(
                    [
                        self.robot.linear_velocity / self.config.robot.max_linear_speed,
                        self.robot.angular_velocity / self.config.robot.max_angular_speed,
                        np.sin(self.robot.pose.theta),
                        np.cos(self.robot.pose.theta),
                        self.coverage_ratio,
                        float(self.last_collision),
                    ],
                    dtype=np.float32,
                ),
            )
        )
        if state.shape != (self.state_dim,) or not np.isfinite(state).all():
            raise RuntimeError("Simulator produced an invalid observation")
        state[-6:-4] = np.clip(state[-6:-4], -1.0, 1.0)
        state[:-6] = np.clip(state[:-6], 0.0, 1.0)
        state[-2:] = np.clip(state[-2:], 0.0, 1.0)
        return state.astype(np.float32)


def default_sensor_angles() -> tuple[float, ...]:
    """Return the documented seven-ray default in radians."""
    return tuple(radians(value) for value in (-90, -60, -30, 0, 30, 60, 90))


def heading_is_normalized(pose: Pose) -> bool:
    """Return whether a pose heading follows the simulator angle contract."""
    return -pi <= pose.theta < pi
