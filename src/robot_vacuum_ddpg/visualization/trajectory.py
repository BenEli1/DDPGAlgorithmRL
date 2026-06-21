"""Trajectory visualization for custom floor maps."""

import os
from collections.abc import Sequence
from math import cos, sin
from pathlib import Path

import numpy as np

from robot_vacuum_ddpg.shared.paths import PROJECT_ROOT

os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".matplotlib-cache"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle as RectanglePatch  # noqa: E402

from robot_vacuum_ddpg.simulator.geometry import Pose
from robot_vacuum_ddpg.simulator.map_loader import FloorMap


def save_trajectory_plot(
    floor_map: FloorMap,
    trajectory: list[Pose],
    output_path: Path,
    collision_points: Sequence[Pose] = (),
    cleaned_cells: np.ndarray | None = None,
    title: str | None = None,
) -> Path:
    """Save map geometry and an ordered continuous trajectory as a PNG."""
    if not trajectory:
        raise ValueError("trajectory must contain at least one pose")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(figsize=(8, 6))
    bounds = floor_map.bounds
    axes.set_xlim(bounds.min_x, bounds.max_x)
    axes.set_ylim(bounds.min_y, bounds.max_y)
    axes.set_aspect("equal", adjustable="box")
    axes.set_title(title or f"Random-policy trajectory: {floor_map.name}")
    axes.set_xlabel("x position")
    axes.set_ylabel("y position")
    axes.add_patch(
        RectanglePatch(
            (bounds.min_x, bounds.min_y),
            bounds.max_x - bounds.min_x,
            bounds.max_y - bounds.min_y,
            fill=False,
            edgecolor="black",
            linewidth=2.0,
            label="Map boundary",
        )
    )
    for index, obstacle in enumerate(floor_map.obstacles):
        axes.add_patch(
            RectanglePatch(
                (obstacle.min_x, obstacle.min_y),
                obstacle.max_x - obstacle.min_x,
                obstacle.max_y - obstacle.min_y,
                facecolor="dimgray",
                edgecolor="black",
                label="Obstacle" if index == 0 else None,
            )
        )
    if cleaned_cells is not None and cleaned_cells.size:
        axes.scatter(
            cleaned_cells[:, 0],
            cleaned_cells[:, 1],
            color="gold",
            alpha=0.35,
            s=12,
            label="Cleaned cells",
            zorder=1,
        )
    x_values = [pose.x for pose in trajectory]
    y_values = [pose.y for pose in trajectory]
    axes.plot(x_values, y_values, color="tab:blue", linewidth=1.5, label="Robot path")
    axes.scatter(x_values[0], y_values[0], color="tab:green", s=70, label="Start", zorder=3)
    axes.scatter(x_values[-1], y_values[-1], color="tab:red", s=70, label="Final", zorder=3)
    final_pose = trajectory[-1]
    axes.quiver(
        final_pose.x,
        final_pose.y,
        0.45 * cos(final_pose.theta),
        0.45 * sin(final_pose.theta),
        angles="xy",
        scale_units="xy",
        scale=1.0,
        color="black",
        width=0.006,
        label="Final heading",
        zorder=4,
    )
    if collision_points:
        axes.scatter(
            [pose.x for pose in collision_points],
            [pose.y for pose in collision_points],
            marker="x",
            color="crimson",
            s=55,
            linewidths=1.8,
            label="Collision attempt",
            zorder=4,
        )
    axes.legend(loc="best")
    axes.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)
    return output_path
