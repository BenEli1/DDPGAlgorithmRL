"""Integration test for trajectory artifact generation."""

from pathlib import Path

from robot_vacuum_ddpg.sdk import VacuumSDK
from robot_vacuum_ddpg.shared.paths import CONFIG_DIR


def test_random_episode_creates_trajectory_png(tmp_path: Path) -> None:
    output = tmp_path / "trajectory.png"

    result = VacuumSDK().run_random_episode(
        CONFIG_DIR / "default_simulator.json",
        output_path=output,
        seed=7,
        max_steps=5,
    )

    assert result.steps == 5
    assert result.trajectory_path == output
    assert output.exists()
    assert output.stat().st_size > 0
