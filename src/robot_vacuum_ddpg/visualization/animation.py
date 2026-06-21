"""Application-only GIF rendering from immutable simulator snapshots."""

import os
from dataclasses import dataclass
from math import cos, sin
from pathlib import Path

import numpy as np

from robot_vacuum_ddpg.shared.paths import PROJECT_ROOT

os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".matplotlib-cache"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402
from matplotlib.patches import Rectangle as RectanglePatch  # noqa: E402

from robot_vacuum_ddpg.simulator.map_loader import FloorMap


@dataclass(frozen=True, slots=True)
class AnimationFrame:
    """Primitive values needed to render one safe, application-only frame."""

    step: int
    total_reward: float
    coverage_percent: float
    robot_position: tuple[float, float]
    robot_heading: float
    trajectory: tuple[tuple[float, float], ...]
    collision_points: tuple[tuple[float, float], ...]
    cleaned_cells: tuple[tuple[float, float], ...]


def save_trajectory_animation(
    floor_map: FloorMap,
    frames: list[AnimationFrame],
    output_path: Path,
    frame_duration_ms: int = 120,
) -> Path:
    """Render evolving SDK state without accessing or capturing the desktop."""
    if not frames or frame_duration_ms <= 0:
        raise ValueError("Animation requires frames and a positive frame duration")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(figsize=(8, 6))
    bounds = floor_map.bounds
    axes.set(xlim=(bounds.min_x, bounds.max_x), ylim=(bounds.min_y, bounds.max_y))
    axes.set_aspect("equal", adjustable="box")
    axes.set_title(f"Live random-policy simulator: {floor_map.name}")
    axes.set_xlabel("x position")
    axes.set_ylabel("y position")
    axes.grid(alpha=0.2)
    axes.add_patch(
        RectanglePatch(
            (bounds.min_x, bounds.min_y),
            bounds.max_x - bounds.min_x,
            bounds.max_y - bounds.min_y,
            fill=False,
            edgecolor="black",
            linewidth=2.0,
        )
    )
    for obstacle in floor_map.obstacles:
        axes.add_patch(
            RectanglePatch(
                (obstacle.min_x, obstacle.min_y),
                obstacle.max_x - obstacle.min_x,
                obstacle.max_y - obstacle.min_y,
                facecolor="dimgray",
                edgecolor="black",
            )
        )
    path_line, = axes.plot([], [], color="tab:blue", linewidth=2.0)
    cleaned = axes.scatter([], [], color="gold", alpha=0.4, s=18)
    collisions = axes.scatter([], [], marker="x", color="crimson", s=60)
    robot = axes.scatter([], [], color="seagreen", s=100, zorder=4)
    heading, = axes.plot([], [], color="black", linewidth=2.5, zorder=5)
    status = axes.text(
        0.02,
        0.98,
        "",
        transform=axes.transAxes,
        va="top",
        bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "lightgray"},
    )

    def update(frame: AnimationFrame):
        trajectory = np.asarray(frame.trajectory, dtype=float)
        path_line.set_data(trajectory[:, 0], trajectory[:, 1])
        cleaned.set_offsets(_points(frame.cleaned_cells))
        collisions.set_offsets(_points(frame.collision_points))
        robot.set_offsets(np.asarray([frame.robot_position]))
        x_value, y_value = frame.robot_position
        heading.set_data(
            (x_value, x_value + 0.4 * cos(frame.robot_heading)),
            (y_value, y_value + 0.4 * sin(frame.robot_heading)),
        )
        status.set_text(
            f"step {frame.step}  |  reward {frame.total_reward:.2f}  |  "
            f"coverage {frame.coverage_percent:.2f}%"
        )
        return path_line, cleaned, collisions, robot, heading, status

    animation = FuncAnimation(figure, update, frames=frames, interval=frame_duration_ms)
    animation.save(
        output_path,
        writer=PillowWriter(fps=max(1, round(1000 / frame_duration_ms))),
        dpi=90,
    )
    plt.close(figure)
    return output_path


def _points(values: tuple[tuple[float, float], ...]) -> np.ndarray:
    return np.asarray(values, dtype=float).reshape((-1, 2))
