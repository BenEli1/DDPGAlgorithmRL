"""Observation assembly that keeps the state contract explicit and testable."""

import numpy as np


def build_observation(
    sensor_values: np.ndarray,
    linear_velocity: float,
    angular_velocity: float,
    max_linear_speed: float,
    max_angular_speed: float,
    heading: float,
    coverage_ratio: float,
    collision: bool,
) -> np.ndarray:
    """Normalize domain values once so agents and interfaces cannot drift."""
    state = np.concatenate(
        (
            np.clip(sensor_values, 0.0, 1.0),
            np.asarray(
                [
                    np.clip(linear_velocity / max_linear_speed, -1.0, 1.0),
                    np.clip(angular_velocity / max_angular_speed, -1.0, 1.0),
                    np.sin(heading),
                    np.cos(heading),
                    np.clip(coverage_ratio, 0.0, 1.0),
                    float(collision),
                ],
                dtype=np.float32,
            ),
        )
    ).astype(np.float32)
    if not np.isfinite(state).all():
        raise RuntimeError("Simulator produced an invalid observation")
    return state
