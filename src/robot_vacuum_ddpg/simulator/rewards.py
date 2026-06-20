"""Transparent reward components for cleaning and safe movement."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class RewardConfig:
    """Configurable weights for the simulator reward."""

    clean_weight: float
    completion_bonus: float
    collision_penalty: float
    step_penalty: float
    control_penalty: float

    def __post_init__(self) -> None:
        """Require nonnegative reward magnitudes."""
        if min(
            self.clean_weight,
            self.completion_bonus,
            self.collision_penalty,
            self.step_penalty,
            self.control_penalty,
        ) < 0.0:
            raise ValueError("Reward magnitudes must be nonnegative")


@dataclass(frozen=True, slots=True)
class RewardBreakdown:
    """Named reward terms for metrics and tests."""

    cleaning: float
    completion: float
    collision: float
    step: float
    control: float

    @property
    def total(self) -> float:
        """Return the sum of all signed components."""
        return self.cleaning + self.completion + self.collision + self.step + self.control

    def as_dict(self) -> dict[str, float]:
        """Return JSON-compatible named components."""
        return {
            "cleaning": self.cleaning,
            "completion": self.completion,
            "collision": self.collision,
            "step": self.step,
            "control": self.control,
        }


def calculate_reward(
    newly_cleaned_cells: int,
    collision: bool,
    reached_target: bool,
    action: np.ndarray,
    config: RewardConfig,
) -> RewardBreakdown:
    """Calculate a reward without hidden environment state."""
    return RewardBreakdown(
        cleaning=config.clean_weight * newly_cleaned_cells,
        completion=config.completion_bonus if reached_target else 0.0,
        collision=-config.collision_penalty if collision else 0.0,
        step=-config.step_penalty,
        control=-config.control_penalty * float(np.mean(np.square(action))),
    )
