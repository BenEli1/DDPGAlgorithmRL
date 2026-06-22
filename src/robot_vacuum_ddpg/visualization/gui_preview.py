"""Portable rendering of the GUI layout from immutable application state."""

import os
from dataclasses import dataclass
from math import cos, sin
from pathlib import Path

from robot_vacuum_ddpg.shared.paths import PROJECT_ROOT

os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".matplotlib-cache"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402


@dataclass(frozen=True, slots=True)
class GuiPreviewData:
    """Values needed to document the GUI without capturing the user's desktop."""

    seed: int
    max_steps: int
    map_path: str
    step: int
    total_reward: float
    collisions: int
    coverage_percent: float
    current_action: tuple[float, float]
    state_vector_length: int
    map_name: str
    bounds: tuple[float, float, float, float]
    obstacles: tuple[tuple[float, float, float, float], ...]
    robot_position: tuple[float, float]
    robot_heading: float
    trajectory: tuple[tuple[float, float], ...]
    collision_points: tuple[tuple[float, float], ...]
    cleaned_cells: tuple[tuple[float, float], ...]
    artifact_path: str


def save_gui_preview(data: GuiPreviewData, output_path: Path) -> Path:
    """Render controls, map, and status from SDK data for portable evidence."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure = plt.figure(figsize=(13, 7.5), facecolor="#eef2f6")
    grid = figure.add_gridspec(
        2,
        2,
        height_ratios=(1.25, 7.0),
        width_ratios=(4.3, 1.45),
        hspace=0.14,
        wspace=0.12,
    )
    controls = figure.add_subplot(grid[0, :])
    map_axes = figure.add_subplot(grid[1, 0])
    status_axes = figure.add_subplot(grid[1, 1])
    _draw_controls(controls, data)
    _draw_map(map_axes, data)
    _draw_status(status_axes, data)
    figure.suptitle(
        "Robot Vacuum Simulator — Local Tkinter GUI",
        fontsize=16,
        fontweight="bold",
        y=0.99,
    )
    figure.text(
        0.5,
        0.012,
        "Portable application-rendered preview • no desktop or personal content captured",
        ha="center",
        fontsize=9,
        color="#52606d",
    )
    figure.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(figure)
    return output_path


def _draw_controls(axes, data: GuiPreviewData) -> None:
    axes.set_axis_off()
    axes.set_xlim(0, 1)
    axes.set_ylim(0, 1)
    fields = (
        ("Seed", str(data.seed), 0.01, 0.10),
        ("Max steps", str(data.max_steps), 0.13, 0.11),
        ("Map file", data.map_path, 0.27, 0.38),
        ("Delay", "40 ms", 0.67, 0.11),
    )
    for label, value, x_position, width in fields:
        axes.text(x_position, 0.78, label, fontsize=8, color="#52606d")
        axes.add_patch(
            Rectangle(
                (x_position, 0.48),
                width,
                0.26,
                facecolor="white",
                edgecolor="#9aa5b1",
                linewidth=0.8,
            )
        )
        axes.text(
            x_position + 0.008,
            0.61,
            value,
            fontsize=8,
            va="center",
            color="#243b53",
            clip_on=True,
        )
    buttons = (
        "Reset",
        "Step random action",
        "Run episode",
        "Pause / stop",
        "Save screenshot",
        "Generate report",
    )
    button_width = 0.145
    for index, label in enumerate(buttons):
        x_position = 0.01 + index * 0.163
        axes.add_patch(
            Rectangle(
                (x_position, 0.05),
                button_width,
                0.28,
                facecolor="#ffffff",
                edgecolor="#627d98",
                linewidth=0.9,
            )
        )
        axes.text(
            x_position + button_width / 2,
            0.19,
            label,
            ha="center",
            va="center",
            fontsize=8,
            color="#102a43",
        )


def _draw_map(axes, data: GuiPreviewData) -> None:
    min_x, min_y, max_x, max_y = data.bounds
    axes.set_xlim(min_x, max_x)
    axes.set_ylim(min_y, max_y)
    axes.set_aspect("equal", adjustable="box")
    axes.set_facecolor("white")
    axes.set_title(f"Map: {data.map_name}", fontsize=11, loc="left")
    axes.set_xlabel("x position")
    axes.set_ylabel("y position")
    axes.add_patch(
        Rectangle(
            (min_x, min_y),
            max_x - min_x,
            max_y - min_y,
            fill=False,
            edgecolor="#102a43",
            linewidth=2.0,
        )
    )
    for obstacle in data.obstacles:
        obstacle_min_x, obstacle_min_y, obstacle_max_x, obstacle_max_y = obstacle
        axes.add_patch(
            Rectangle(
                (obstacle_min_x, obstacle_min_y),
                obstacle_max_x - obstacle_min_x,
                obstacle_max_y - obstacle_min_y,
                facecolor="#627d98",
                edgecolor="#243b53",
            )
        )
    if data.cleaned_cells:
        axes.scatter(
            [point[0] for point in data.cleaned_cells],
            [point[1] for point in data.cleaned_cells],
            color="#f7c948",
            alpha=0.28,
            s=12,
            label="Cleaned cells",
            zorder=1,
        )
    if data.trajectory:
        axes.plot(
            [point[0] for point in data.trajectory],
            [point[1] for point in data.trajectory],
            color="#147d92",
            linewidth=2.0,
            label="Trajectory",
            zorder=3,
        )
        axes.scatter(*data.trajectory[0], color="#27ab83", s=65, label="Start", zorder=4)
    if data.collision_points:
        axes.scatter(
            [point[0] for point in data.collision_points],
            [point[1] for point in data.collision_points],
            marker="x",
            color="#d64545",
            s=55,
            label="Collision",
            zorder=5,
        )
    robot_x, robot_y = data.robot_position
    axes.scatter(robot_x, robot_y, color="#d64545", s=85, label="Robot", zorder=6)
    axes.arrow(
        robot_x,
        robot_y,
        0.48 * cos(data.robot_heading),
        0.48 * sin(data.robot_heading),
        width=0.035,
        head_width=0.18,
        color="#102a43",
        length_includes_head=True,
        zorder=7,
    )
    axes.legend(loc="upper right", fontsize=8)
    axes.grid(alpha=0.2)


def _draw_status(axes, data: GuiPreviewData) -> None:
    axes.set_axis_off()
    axes.set_xlim(0, 1)
    axes.set_ylim(0, 1)
    axes.add_patch(
        Rectangle(
            (0.02, 0.02),
            0.96,
            0.96,
            facecolor="white",
            edgecolor="#9fb3c8",
            linewidth=1.0,
        )
    )
    axes.text(0.08, 0.92, "Status", fontsize=13, fontweight="bold", color="#102a43")
    values = (
        ("Current step", str(data.step)),
        ("Total reward", f"{data.total_reward:.3f}"),
        ("Collisions", str(data.collisions)),
        ("Coverage", f"{data.coverage_percent:.2f}%"),
        ("Current action", f"({data.current_action[0]:.3f}, {data.current_action[1]:.3f})"),
        ("State vector length", str(data.state_vector_length)),
        ("Last artifact", data.artifact_path),
    )
    y_position = 0.82
    for label, value in values:
        axes.text(0.08, y_position, label, fontsize=8, color="#627d98")
        axes.text(0.08, y_position - 0.045, value, fontsize=9, color="#102a43", wrap=True)
        y_position -= 0.115
