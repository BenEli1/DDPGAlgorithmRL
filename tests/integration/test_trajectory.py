"""Integration test for trajectory artifact generation."""

import json
from pathlib import Path

from robot_vacuum_ddpg.sdk import VacuumSDK
from robot_vacuum_ddpg.shared.paths import CONFIG_DIR


def test_random_episode_creates_trajectory_png(tmp_path: Path) -> None:
    output = tmp_path / "trajectory.png"
    metrics_output = tmp_path / "metrics.json"
    report_output = tmp_path / "report.md"

    result = VacuumSDK().run_random_episode(
        CONFIG_DIR / "default_simulator.json",
        output_path=output,
        metrics_path=metrics_output,
        report_path=report_output,
        seed=7,
        max_steps=5,
    )

    assert result.steps == 5
    assert result.trajectory_path == output
    assert output.exists()
    assert output.stat().st_size > 0
    assert result.metrics_path == metrics_output
    assert result.report_path == report_output

    metrics = json.loads(metrics_output.read_text(encoding="utf-8"))
    required_fields = {
        "seed",
        "max_steps",
        "steps_executed",
        "total_reward",
        "collisions",
        "coverage_percent",
        "final_position",
        "final_heading",
        "map_name",
        "generated_artifacts",
    }
    assert required_fields <= metrics.keys()
    assert metrics["seed"] == 7
    assert metrics["max_steps"] == 5
    assert metrics["steps_executed"] == 5
    assert set(metrics["final_position"]) == {"x", "y"}
    assert set(metrics["generated_artifacts"]) == {"trajectory", "metrics", "report"}
    assert metrics["map_name"] == "simple_house"
    assert 0.0 <= metrics["coverage_percent"] <= 100.0

    report = report_output.read_text(encoding="utf-8")
    assert "# Random-Policy Simulator Demo Report" in report
    assert "not a trained DDPG policy" in report
    assert metrics["command"] in report


def test_record_random_episode_creates_gif(tmp_path: Path) -> None:
    output = tmp_path / "demo.gif"

    result = VacuumSDK().record_random_episode(
        CONFIG_DIR / "default_simulator.json",
        output,
        seed=7,
        max_steps=4,
        frame_stride=1,
    )

    assert result == output
    assert output.read_bytes().startswith(b"GIF89a")


def test_sdk_creates_portable_gui_preview(tmp_path: Path) -> None:
    output = tmp_path / "gui_preview.png"
    sdk = VacuumSDK()
    session = sdk.create_demo_session(
        CONFIG_DIR / "default_simulator.json",
        seed=7,
        max_steps=4,
    )
    session.step_random()

    result = sdk.save_gui_preview(session, output)

    assert result == output
    assert output.read_bytes().startswith(b"\x89PNG")
