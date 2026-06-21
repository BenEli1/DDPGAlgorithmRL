"""Tkinter canvas rendering for immutable SDK demo snapshots."""

import tkinter as tk

from robot_vacuum_ddpg.gui.view_model import heading_endpoint, world_to_canvas
from robot_vacuum_ddpg.sdk import DemoSnapshot


def draw_snapshot(
    canvas: tk.Canvas,
    snapshot: DemoSnapshot,
    canvas_size: tuple[int, int],
) -> None:
    """Render map geometry and robot evidence without simulator logic."""
    canvas.delete("all")

    def convert(point: tuple[float, float]) -> tuple[float, float]:
        return world_to_canvas(point, snapshot.bounds, canvas_size)

    min_x, min_y = convert((snapshot.bounds[0], snapshot.bounds[1]))
    max_x, max_y = convert((snapshot.bounds[2], snapshot.bounds[3]))
    canvas.create_rectangle(min_x, max_y, max_x, min_y, width=3)
    for obstacle in snapshot.obstacles:
        first = convert((obstacle[0], obstacle[1]))
        second = convert((obstacle[2], obstacle[3]))
        canvas.create_rectangle(first[0], second[1], second[0], first[1], fill="dimgray")
    for point in snapshot.cleaned_cells:
        x_value, y_value = convert(point)
        canvas.create_oval(
            x_value - 2,
            y_value - 2,
            x_value + 2,
            y_value + 2,
            fill="gold",
            outline="",
        )
    if len(snapshot.trajectory) > 1:
        points = [coordinate for point in snapshot.trajectory for coordinate in convert(point)]
        canvas.create_line(*points, fill="royalblue", width=2)
    for point in snapshot.collision_points:
        x_value, y_value = convert(point)
        canvas.create_line(
            x_value - 5, y_value - 5, x_value + 5, y_value + 5, fill="red", width=2
        )
        canvas.create_line(
            x_value - 5, y_value + 5, x_value + 5, y_value - 5, fill="red", width=2
        )
    robot_x, robot_y = convert(snapshot.robot_position)
    canvas.create_oval(
        robot_x - 9, robot_y - 9, robot_x + 9, robot_y + 9, fill="seagreen"
    )
    heading = convert(heading_endpoint(snapshot.robot_position, snapshot.robot_heading))
    canvas.create_line(
        robot_x, robot_y, heading[0], heading[1], fill="black", width=3, arrow="last"
    )
