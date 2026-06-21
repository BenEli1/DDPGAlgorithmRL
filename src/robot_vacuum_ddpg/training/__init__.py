"""DDPG training, evaluation, and evidence generation."""

from robot_vacuum_ddpg.training.config import TrainingConfig
from robot_vacuum_ddpg.training.evaluation import EvaluationResult, evaluate_checkpoint
from robot_vacuum_ddpg.training.metrics import TrainingMetrics, write_training_metrics
from robot_vacuum_ddpg.training.trainer import (
    TrainingResult,
    train_ddpg,
)

__all__ = [
    "EvaluationResult",
    "TrainingConfig",
    "TrainingMetrics",
    "TrainingResult",
    "evaluate_checkpoint",
    "train_ddpg",
    "write_training_metrics",
]
