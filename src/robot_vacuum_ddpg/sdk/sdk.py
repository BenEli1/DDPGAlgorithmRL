"""SDK facade used by the CLI and future external consumers."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from robot_vacuum_ddpg.reporting import write_demo_metrics, write_demo_report
from robot_vacuum_ddpg.sdk.session import DemoSession, DemoSnapshot
from robot_vacuum_ddpg.shared.paths import PROJECT_ROOT, RESULTS_DIR, ensure_result_directories
from robot_vacuum_ddpg.shared.random_seed import seed_everything
from robot_vacuum_ddpg.simulator.environment import EnvironmentConfig, VacuumEnvironment
from robot_vacuum_ddpg.simulator.map_loader import JsonMapLoader
from robot_vacuum_ddpg.visualization.animation import AnimationFrame, save_trajectory_animation
from robot_vacuum_ddpg.visualization.trajectory import save_trajectory_plot


@dataclass(frozen=True, slots=True)
class DemoResult:
    """Summary returned by a random-policy simulator episode."""

    steps: int
    cumulative_reward: float
    coverage_ratio: float
    collisions: int
    trajectory_path: Path
    metrics_path: Path
    report_path: Path


class VacuumSDK:
    """Single high-level entry point for current simulator functionality."""

    def run_random_episode(
        self,
        simulator_config_path: Path,
        output_path: Path | None = None,
        metrics_path: Path | None = None,
        report_path: Path | None = None,
        seed: int = 42,
        max_steps: int | None = None,
        command: str | None = None,
    ) -> DemoResult:
        """Run one random-policy episode and save its trajectory figure."""
        session = self.create_demo_session(
            simulator_config_path,
            seed=seed,
            max_steps=max_steps,
        )
        while not session.done:
            session.step_random()
        return self.save_demo_artifacts(
            session,
            output_path=output_path,
            metrics_path=metrics_path,
            report_path=report_path,
            command=command,
        )

    def create_demo_session(
        self,
        simulator_config_path: Path,
        seed: int = 42,
        max_steps: int | None = None,
        map_path: Path | None = None,
    ) -> DemoSession:
        """Create an incremental simulator session for CLI or GUI consumers."""
        environment = self.create_environment(simulator_config_path, seed=seed, map_path=map_path)
        floor_map = environment.floor_map
        requested_steps = max_steps or environment.config.max_steps
        return DemoSession(floor_map, environment, seed, requested_steps)

    def record_random_episode(
        self,
        simulator_config_path: Path,
        output_path: Path,
        seed: int = 42,
        max_steps: int = 150,
        frame_stride: int = 3,
    ) -> Path:
        """Record a seeded episode from SDK snapshots, never from the desktop."""
        if frame_stride <= 0:
            raise ValueError("frame_stride must be positive")
        session = self.create_demo_session(simulator_config_path, seed, max_steps)
        frames = [self._animation_frame(session.snapshot())]
        while not session.done:
            snapshot = session.step_random()
            if snapshot.done or snapshot.step % frame_stride == 0:
                frames.append(self._animation_frame(snapshot))
        return save_trajectory_animation(session.floor_map, frames, output_path)

    def create_environment(
        self,
        simulator_config_path: Path,
        seed: int = 42,
        map_path: Path | None = None,
    ) -> VacuumEnvironment:
        """Build a seeded environment so every caller shares configuration loading."""
        seed_everything(seed)
        simulator_data = self._load_json(simulator_config_path)
        selected_map = map_path or self._resolve_project_path(simulator_data["map_path"])
        floor_map = JsonMapLoader().load(selected_map)
        return VacuumEnvironment(floor_map, EnvironmentConfig.from_dict(simulator_data))

    def train(self, training_config_path: Path, simulator_config_path: Path):
        """Train DDPG through the SDK without coupling learning into the simulator."""
        from robot_vacuum_ddpg.training import TrainingConfig, train_ddpg

        config = TrainingConfig.from_json(training_config_path)
        environment = self.create_environment(simulator_config_path, seed=config.seed)
        return train_ddpg(environment, config)

    def evaluate(
        self,
        checkpoint_path: Path,
        simulator_config_path: Path,
        output_path: Path | None = None,
        seed: int = 42,
    ):
        """Run a deterministic checkpoint evaluation through the shared SDK factory."""
        from robot_vacuum_ddpg.training import evaluate_checkpoint

        environment = self.create_environment(simulator_config_path, seed=seed)
        destination = output_path or RESULTS_DIR / "trajectories" / "evaluation_trajectory.png"
        return evaluate_checkpoint(environment, checkpoint_path, destination, seed)

    def save_session_view(self, session: DemoSession, output_path: Path) -> Path:
        """Save the current map view as a portable screenshot fallback."""
        return save_trajectory_plot(
            session.floor_map,
            session.environment.trajectory,
            output_path,
            collision_points=session.collision_poses,
            cleaned_cells=session.environment.cleaned_cells,
        )

    def save_demo_artifacts(
        self,
        session: DemoSession,
        output_path: Path | None = None,
        metrics_path: Path | None = None,
        report_path: Path | None = None,
        command: str | None = None,
    ) -> DemoResult:
        """Save trajectory, JSON metrics, and Markdown report for a session."""
        ensure_result_directories()
        destination = output_path or RESULTS_DIR / "trajectories" / "random_policy.png"
        metrics_destination = metrics_path or RESULTS_DIR / "metrics" / "random_policy_metrics.json"
        report_destination = report_path or RESULTS_DIR / "reports" / "random_policy_report.md"
        self.save_session_view(session, destination)
        snapshot = session.snapshot()
        artifacts = {
            "trajectory": self._display_path(destination),
            "metrics": self._display_path(metrics_destination),
            "report": self._display_path(report_destination),
        }
        metrics: dict[str, Any] = {
            "schema_version": "1.00",
            "run_type": "random_policy_demo",
            "command": command
            or f"uv run robot-vacuum demo --max-steps {session.max_steps} --seed {session.seed}",
            "seed": session.seed,
            "max_steps": session.max_steps,
            "steps_executed": snapshot.step,
            "total_reward": snapshot.total_reward,
            "collisions": snapshot.collisions,
            "coverage_percent": snapshot.coverage_percent,
            "final_position": {
                "x": snapshot.robot_position[0],
                "y": snapshot.robot_position[1],
            },
            "final_heading": snapshot.robot_heading,
            "map_name": snapshot.map_name,
            "generated_artifacts": artifacts,
        }
        write_demo_metrics(metrics, metrics_destination)
        write_demo_report(metrics, report_destination)
        return DemoResult(
            steps=snapshot.step,
            cumulative_reward=snapshot.total_reward,
            coverage_ratio=snapshot.coverage_percent / 100.0,
            collisions=snapshot.collisions,
            trajectory_path=destination,
            metrics_path=metrics_destination,
            report_path=report_destination,
        )

    @staticmethod
    def _animation_frame(snapshot: DemoSnapshot) -> AnimationFrame:
        return AnimationFrame(
            snapshot.step,
            snapshot.total_reward,
            snapshot.coverage_percent,
            snapshot.robot_position,
            snapshot.robot_heading,
            snapshot.trajectory,
            snapshot.collision_points,
            snapshot.cleaned_cells,
        )

    @staticmethod
    def _display_path(path: Path) -> str:
        """Return a portable project-relative path when possible."""
        resolved = path.resolve()
        try:
            return resolved.relative_to(PROJECT_ROOT.resolve()).as_posix()
        except ValueError:
            return resolved.as_posix()

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
