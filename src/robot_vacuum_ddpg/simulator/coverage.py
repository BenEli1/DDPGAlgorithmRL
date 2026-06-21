"""Grid bookkeeping that keeps cleaning evidence separate from robot motion."""

from dataclasses import dataclass

import numpy as np

from robot_vacuum_ddpg.simulator.map_loader import FloorMap


@dataclass(slots=True)
class CoverageGrid:
    """Track first-time cleaning without discretizing simulator movement."""

    cells: np.ndarray
    cleaning_radius: float
    cleaned: np.ndarray

    @classmethod
    def from_map(
        cls,
        floor_map: FloorMap,
        cell_size: float,
        cleaning_radius: float,
    ) -> "CoverageGrid":
        """Build free-space cell centers once so every step stays inexpensive."""
        bounds = floor_map.bounds
        x_values = np.arange(bounds.min_x + cell_size / 2.0, bounds.max_x, cell_size)
        y_values = np.arange(bounds.min_y + cell_size / 2.0, bounds.max_y, cell_size)
        cells = np.asarray(
            [
                (x_value, y_value)
                for x_value in x_values
                for y_value in y_values
                if floor_map.point_is_free(float(x_value), float(y_value))
            ],
            dtype=np.float32,
        )
        if len(cells) == 0:
            raise ValueError("Map contains no cleanable coverage cells")
        return cls(cells, cleaning_radius, np.zeros(len(cells), dtype=np.bool_))

    @property
    def ratio(self) -> float:
        """Expose coverage as a normalized value for rewards and observations."""
        return float(np.mean(self.cleaned))

    @property
    def cleaned_cells(self) -> np.ndarray:
        """Return a copy so presentation code cannot mutate simulator state."""
        return self.cells[self.cleaned].copy()

    def reset(self, robot_position: tuple[float, float]) -> None:
        """Clear prior episode state and mark the initial cleaning footprint."""
        self.cleaned.fill(False)
        self.mark(robot_position)

    def mark(self, robot_position: tuple[float, float]) -> int:
        """Mark first visits and return the count used by the reward function."""
        delta = self.cells - np.asarray(robot_position, dtype=np.float32)
        in_radius = np.sum(np.square(delta), axis=1) <= self.cleaning_radius**2
        newly_cleaned = in_radius & ~self.cleaned
        self.cleaned |= in_radius
        return int(np.count_nonzero(newly_cleaned))
