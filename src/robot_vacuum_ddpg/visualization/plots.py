"""Headless learning diagnostics generated only from recorded metrics."""

import os
from pathlib import Path

from robot_vacuum_ddpg.shared.paths import PROJECT_ROOT

os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".matplotlib-cache"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def save_learning_curve(rewards: list[float], output_path: Path) -> Path:
    """Plot cumulative episode reward without implying convergence."""
    if not rewards:
        raise ValueError("At least one episode reward is required")
    return _save_series(
        list(range(1, len(rewards) + 1)),
        rewards,
        output_path,
        "DDPG training reward (integration evidence)",
        "Episode",
        "Cumulative reward",
    )


def save_critic_loss(losses: list[float], output_path: Path) -> Path:
    """Plot each observed critic MSE optimizer update."""
    if not losses:
        raise ValueError("At least one critic loss is required")
    return _save_series(
        list(range(1, len(losses) + 1)),
        losses,
        output_path,
        "DDPG critic loss (integration evidence)",
        "Optimizer update",
        "Critic MSE loss",
    )


def _save_series(
    x_values: list[int],
    y_values: list[float],
    output_path: Path,
    title: str,
    x_label: str,
    y_label: str,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(figsize=(8, 5))
    axes.plot(x_values, y_values, color="tab:blue", linewidth=1.5)
    axes.set_title(title)
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)
    axes.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)
    return output_path
