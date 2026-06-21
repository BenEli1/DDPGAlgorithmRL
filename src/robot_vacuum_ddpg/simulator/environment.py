"""Framework-free 2D robotic vacuum environment."""

from typing import Any

import numpy as np

from robot_vacuum_ddpg.simulator.config import EnvironmentConfig
from robot_vacuum_ddpg.simulator.coverage import CoverageGrid
from robot_vacuum_ddpg.simulator.geometry import Pose
from robot_vacuum_ddpg.simulator.map_loader import FloorMap
from robot_vacuum_ddpg.simulator.observation import build_observation
from robot_vacuum_ddpg.simulator.rewards import calculate_reward
from robot_vacuum_ddpg.simulator.robot import Robot
from robot_vacuum_ddpg.simulator.sensors import DistanceSensorArray


class VacuumEnvironment:
    """Small custom environment exposing reset and continuous-action step methods."""

    def __init__(self, floor_map: FloorMap, config: EnvironmentConfig) -> None:
        self.floor_map = floor_map
        self.config = config
        self.robot = Robot(floor_map.start_pose, config.robot)
        self.sensors = DistanceSensorArray(config.sensor_angles, config.sensor_max_range)
        self.coverage = CoverageGrid.from_map(
            floor_map,
            config.coverage_cell_size,
            config.cleaning_radius,
        )
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
        return self.coverage.ratio

    @property
    def cleaned_cells(self) -> np.ndarray:
        """Return a defensive copy of cleaned coverage-cell centers."""
        return self.coverage.cleaned_cells

    def reset(self, seed: int | None = None) -> np.ndarray:
        """Reset episode state and return the initial continuous observation."""
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        self.robot.reset(self.floor_map.start_pose)
        self.trajectory = [self.robot.pose]
        self.step_count = 0
        self.last_collision = False
        self.done = False
        self.coverage.reset((self.robot.pose.x, self.robot.pose.y))
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
        newly_cleaned = self.coverage.mark((self.robot.pose.x, self.robot.pose.y))
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

    def _state(self) -> np.ndarray:
        sensor_values = self.sensors.read(self.robot.pose, self.floor_map)
        state = build_observation(
            sensor_values,
            self.robot.linear_velocity,
            self.robot.angular_velocity,
            self.config.robot.max_linear_speed,
            self.config.robot.max_angular_speed,
            self.robot.pose.theta,
            self.coverage_ratio,
            self.last_collision,
        )
        if state.shape != (self.state_dim,):
            raise RuntimeError("Simulator produced an invalid observation")
        return state
