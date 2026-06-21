"""SDK-owned state for interactive random-policy simulator sessions."""

from dataclasses import dataclass

import numpy as np

from robot_vacuum_ddpg.simulator.environment import VacuumEnvironment
from robot_vacuum_ddpg.simulator.geometry import Pose
from robot_vacuum_ddpg.simulator.map_loader import FloorMap


@dataclass(frozen=True, slots=True)
class DemoSnapshot:
    """GUI-safe immutable view of one interactive simulator state."""

    step: int
    total_reward: float
    collisions: int
    coverage_percent: float
    current_action: tuple[float, float]
    state_vector_length: int
    map_name: str
    bounds: tuple[float, float, float, float]
    obstacles: tuple[tuple[float, float, float, float], ...]
    robot_position: tuple[float, float]
    robot_heading: float
    trajectory: tuple[tuple[float, float], ...]
    collision_points: tuple[tuple[float, float], ...]
    cleaned_cells: tuple[tuple[float, float], ...]
    done: bool


class DemoSession:
    """Incremental random-policy session exposed only through the SDK layer."""

    def __init__(
        self,
        floor_map: FloorMap,
        environment: VacuumEnvironment,
        seed: int,
        max_steps: int,
    ) -> None:
        if max_steps <= 0:
            raise ValueError("max_steps must be positive")
        self.floor_map = floor_map
        self.environment = environment
        self.seed = seed
        self.max_steps = min(max_steps, environment.config.max_steps)
        self.total_reward = 0.0
        self.collisions = 0
        self.current_action = np.zeros(2, dtype=np.float32)
        self.collision_poses: list[Pose] = []
        self.environment.reset(seed=seed)

    @property
    def done(self) -> bool:
        """Return whether the environment or requested demo limit is complete."""
        return self.environment.done or self.environment.step_count >= self.max_steps

    def reset(self) -> DemoSnapshot:
        """Reset accumulated metrics and return the initial snapshot."""
        self.environment.reset(seed=self.seed)
        self.total_reward = 0.0
        self.collisions = 0
        self.current_action = np.zeros(2, dtype=np.float32)
        self.collision_poses.clear()
        return self.snapshot()

    def step_random(self) -> DemoSnapshot:
        """Advance once with a seeded random action and return a snapshot."""
        if self.done:
            return self.snapshot()
        self.current_action = self.environment.sample_random_action()
        _, reward, _, info = self.environment.step(self.current_action)
        self.total_reward += reward
        if info["collision"]:
            self.collisions += 1
            self.collision_poses.append(info["attempted_pose"])
        return self.snapshot()

    def snapshot(self) -> DemoSnapshot:
        """Convert internal domain objects into immutable GUI display values."""
        bounds = self.floor_map.bounds
        pose = self.environment.robot.pose
        return DemoSnapshot(
            step=self.environment.step_count,
            total_reward=self.total_reward,
            collisions=self.collisions,
            coverage_percent=self.environment.coverage_ratio * 100.0,
            current_action=(float(self.current_action[0]), float(self.current_action[1])),
            state_vector_length=self.environment.state_dim,
            map_name=self.floor_map.name,
            bounds=(bounds.min_x, bounds.min_y, bounds.max_x, bounds.max_y),
            obstacles=tuple(
                (item.min_x, item.min_y, item.max_x, item.max_y)
                for item in self.floor_map.obstacles
            ),
            robot_position=(pose.x, pose.y),
            robot_heading=pose.theta,
            trajectory=tuple((item.x, item.y) for item in self.environment.trajectory),
            collision_points=tuple((item.x, item.y) for item in self.collision_poses),
            cleaned_cells=tuple(map(tuple, self.environment.cleaned_cells.tolist())),
            done=self.done,
        )
