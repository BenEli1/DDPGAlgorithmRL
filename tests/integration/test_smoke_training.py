"""Small end-to-end DDPG training proof without a convergence assertion."""

import json
from pathlib import Path

from robot_vacuum_ddpg.shared.paths import CONFIG_DIR
from robot_vacuum_ddpg.simulator.environment import VacuumEnvironment
from robot_vacuum_ddpg.training import TrainingConfig, evaluate_checkpoint, train_ddpg


def test_smoke_training_creates_metrics(
    environment: VacuumEnvironment,
    tmp_path: Path,
) -> None:
    config = TrainingConfig.from_json(CONFIG_DIR / "smoke_training.json")

    result = train_ddpg(environment, config, output_dir=tmp_path)
    metrics = json.loads(result.metrics_path.read_text(encoding="utf-8"))

    assert result.metrics_path.exists()
    assert result.learning_curve_path.exists()
    assert result.critic_loss_path.exists()
    assert result.checkpoint_path.exists()
    assert metrics["claim"] == "integration_only_not_convergence"
    assert len(metrics["episodes"]["episode_rewards"]) == 2
    assert metrics["episodes"]["critic_losses"]

    evaluation = evaluate_checkpoint(
        environment,
        result.checkpoint_path,
        tmp_path / "trajectories" / "evaluation_trajectory.png",
        seed=42,
    )
    assert evaluation.trajectory_path.exists()
    assert evaluation.steps > 0
