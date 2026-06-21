"""Machine-readable metrics produced directly from the training loop."""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class TrainingMetrics:
    """Accumulate outcomes once so reports and plots never recompute learning."""

    episode_rewards: list[float] = field(default_factory=list)
    episode_steps: list[int] = field(default_factory=list)
    coverage_percent: list[float] = field(default_factory=list)
    actor_losses: list[float] = field(default_factory=list)
    critic_losses: list[float] = field(default_factory=list)

    def as_document(
        self,
        config: dict[str, Any],
        state_dim: int,
        action_dim: int,
        duration_seconds: float,
        artifacts: dict[str, str],
    ) -> dict[str, Any]:
        """Return the stable JSON schema used by submission evidence."""
        return {
            "schema_version": "1.00",
            "run_type": "ddpg_training",
            "claim": "integration_only_not_convergence",
            "state_dim": state_dim,
            "action_dim": action_dim,
            "duration_seconds": duration_seconds,
            "config": config,
            "episodes": asdict(self),
            "generated_artifacts": artifacts,
        }


def write_training_metrics(document: dict[str, Any], path: Path) -> Path:
    """Write indented JSON atomically enough for a single-process CLI run."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return path
