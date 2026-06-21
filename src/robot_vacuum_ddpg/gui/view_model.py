"""GUI-independent coordinate and status conversion helpers."""

from math import cos, sin

from robot_vacuum_ddpg.sdk import DemoSnapshot


def world_to_canvas(
    point: tuple[float, float],
    bounds: tuple[float, float, float, float],
    canvas_size: tuple[int, int],
    padding: float = 24.0,
) -> tuple[float, float]:
    """Map world coordinates into a padded canvas with an inverted y-axis."""
    min_x, min_y, max_x, max_y = bounds
    width, height = canvas_size
    scale = min(
        (width - 2.0 * padding) / (max_x - min_x),
        (height - 2.0 * padding) / (max_y - min_y),
    )
    x_value = padding + (point[0] - min_x) * scale
    y_value = height - padding - (point[1] - min_y) * scale
    return x_value, y_value


def heading_endpoint(
    position: tuple[float, float],
    heading: float,
    length: float = 0.45,
) -> tuple[float, float]:
    """Return a world-coordinate endpoint for a robot heading indicator."""
    return position[0] + length * cos(heading), position[1] + length * sin(heading)


def status_values(snapshot: DemoSnapshot, artifact_path: str = "-") -> dict[str, str]:
    """Format an SDK snapshot for the GUI status panel."""
    return {
        "step": str(snapshot.step),
        "reward": f"{snapshot.total_reward:.3f}",
        "collisions": str(snapshot.collisions),
        "coverage": f"{snapshot.coverage_percent:.2f}%",
        "action": f"[{snapshot.current_action[0]:.3f}, {snapshot.current_action[1]:.3f}]",
        "state_length": str(snapshot.state_vector_length),
        "artifact": artifact_path,
    }
