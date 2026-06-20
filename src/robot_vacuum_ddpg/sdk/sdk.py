"""SDK facade used by the CLI and future external consumers."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from robot_vacuum_ddpg.shared.paths import PROJECT_ROOT, RESULTS_DIR, ensure_result_directories
from robot_vacuum_ddpg.shared.random_seed import seed_everything
from robot_vacuum_ddpg.simulator.environment import EnvironmentConfig, VacuumEnvironment
from robot_vacuum_ddpg.simulator.map_loader import JsonMapLoader
from robot_vacuum_ddpg.visualization.trajectory import save_trajectory_plot


@dataclass(frozen=True, slots=True)
class DemoResult:
    """Summary returned by a random-policy simulator episode."""

    steps: int
    cumulative_reward: float
    coverage_ratio: float
    collisions: int
    trajectory_path: Path


class VacuumSDK:
    """Single high-level entry point for current simulator functionality."""

    def run_random_episode(
        self,
        simulator_config_path: Path,
        output_path: Path | None = None,
        seed: int = 42,
        max_steps: int | None = None,
    ) -> DemoResult:
        """Run one random-policy episode and save its trajectory figure."""
        seed_everything(seed)
        simulator_data = self._load_json(simulator_config_path)
        map_path = self._resolve_project_path(simulator_data["map_path"])
        floor_map = JsonMapLoader().load(map_path)
        environment = VacuumEnvironment(
            floor_map,
            EnvironmentConfig.from_dict(simulator_data),
        )
        environment.reset(seed=seed)
        cumulative_reward = 0.0
        collisions = 0
        step_limit = min(max_steps or environment.config.max_steps, environment.config.max_steps)
        for _ in range(step_limit):
            action = environment.sample_random_action()
            _, reward, done, info = environment.step(action)
            cumulative_reward += reward
            collisions += int(info["collision"])
            if done:
                break
        ensure_result_directories()
        destination = output_path or RESULTS_DIR / "trajectories" / "random_policy.png"
        save_trajectory_plot(floor_map, environment.trajectory, destination)
        return DemoResult(
            steps=environment.step_count,
            cumulative_reward=cumulative_reward,
            coverage_ratio=environment.coverage_ratio,
            collisions=collisions,
            trajectory_path=destination,
        )

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise ValueError(f"Configuration file does not exist: {path}") from error
        except json.JSONDecodeError as error:
            raise ValueError(f"Configuration file is invalid JSON: {path}") from error
        if not isinstance(document, dict):
            raise ValueError("Configuration document must be a JSON object")
        return document

    @staticmethod
    def _resolve_project_path(value: object) -> Path:
        if not isinstance(value, str) or not value:
            raise ValueError("map_path must be a non-empty string")
        path = Path(value)
        return path if path.is_absolute() else PROJECT_ROOT / path
