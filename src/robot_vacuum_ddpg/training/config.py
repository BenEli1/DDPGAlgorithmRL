"""Validated JSON configuration for DDPG training."""

import json
from dataclasses import dataclass
from pathlib import Path

from robot_vacuum_ddpg.ddpg import AgentConfig


@dataclass(frozen=True, slots=True)
class TrainingConfig:
    """Keep experiment choices outside both agent mathematics and orchestration."""

    seed: int
    episodes: int
    max_steps_per_episode: int
    actor_lr: float
    critic_lr: float
    gamma: float
    tau: float
    noise_sigma: float
    batch_size: int
    replay_buffer_size: int
    warmup_transitions: int
    updates_per_step: int
    actor_hidden_sizes: tuple[int, ...]
    critic_hidden_sizes: tuple[int, ...]

    @classmethod
    def from_json(cls, path: Path) -> "TrainingConfig":
        """Load configuration with clear errors before any expensive training work."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"Cannot load training configuration: {path}") from error
        if not isinstance(data, dict) or data.get("schema_version") != "1.00":
            raise ValueError("Training configuration must use schema_version 1.00")
        values = {key: value for key, value in data.items() if key != "schema_version"}
        values["actor_hidden_sizes"] = tuple(values["actor_hidden_sizes"])
        values["critic_hidden_sizes"] = tuple(values["critic_hidden_sizes"])
        config = cls(**values)
        config._validate()
        return config

    def agent_config(self) -> AgentConfig:
        """Expose only mathematical hyperparameters to the agent."""
        return AgentConfig(
            self.actor_lr,
            self.critic_lr,
            self.gamma,
            self.tau,
            self.noise_sigma,
            self.batch_size,
            self.replay_buffer_size,
            self.actor_hidden_sizes,
            self.critic_hidden_sizes,
        )

    def _validate(self) -> None:
        positive = (
            self.episodes,
            self.max_steps_per_episode,
            self.batch_size,
            self.replay_buffer_size,
            self.updates_per_step,
        )
        if min(positive) <= 0 or min(self.actor_lr, self.critic_lr) <= 0.0:
            raise ValueError("Training counts, sizes, and learning rates must be positive")
        if self.replay_buffer_size < self.batch_size or self.warmup_transitions < 0:
            raise ValueError("Replay capacity must cover the batch and warmup must be nonnegative")
        if not 0.0 <= self.gamma <= 1.0 or not 0.0 < self.tau <= 1.0:
            raise ValueError("gamma must be in [0, 1] and tau in (0, 1]")
        if self.noise_sigma < 0.0 or min(self.actor_hidden_sizes + self.critic_hidden_sizes) <= 0:
            raise ValueError("Noise must be nonnegative and hidden sizes must be positive")
