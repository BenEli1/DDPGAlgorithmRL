"""Validated JSON map loading behind a future HouseExpo adapter boundary."""

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from robot_vacuum_ddpg.simulator.geometry import Pose, Rectangle, point_in_rectangle


@dataclass(frozen=True, slots=True)
class FloorMap:
    """Simulator-native floor map independent of any source JSON schema."""

    name: str
    bounds: Rectangle
    start_pose: Pose
    obstacles: tuple[Rectangle, ...]

    def point_is_free(self, x: float, y: float) -> bool:
        """Return whether a point lies in bounds and outside obstacles."""
        return point_in_rectangle(x, y, self.bounds) and not any(
            point_in_rectangle(x, y, obstacle) for obstacle in self.obstacles
        )


class MapLoader(Protocol):
    """Interface implemented by native and future HouseExpo map loaders."""

    def load(self, path: Path) -> FloorMap:
        """Load and validate a map file."""
        ...


class JsonMapLoader:
    """Load the small project-native JSON floor-map format."""

    SUPPORTED_SCHEMA = "1.00"

    def load(self, path: Path) -> FloorMap:
        """Read, validate, and convert a JSON file into a FloorMap."""
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise ValueError(f"Map file does not exist: {path}") from error
        except json.JSONDecodeError as error:
            raise ValueError(f"Map file is not valid JSON: {path}") from error
        if not isinstance(document, dict):
            raise ValueError("Map document must be a JSON object")
        if document.get("schema_version") != self.SUPPORTED_SCHEMA:
            raise ValueError(f"Unsupported map schema_version: {document.get('schema_version')!r}")

        bounds = self._rectangle(document.get("bounds"), "bounds")
        start_pose = self._pose(document.get("start_pose"))
        obstacles_data = document.get("obstacles", [])
        if not isinstance(obstacles_data, list):
            raise ValueError("obstacles must be a list")
        obstacles = tuple(
            self._obstacle(item, index) for index, item in enumerate(obstacles_data)
        )
        floor_map = FloorMap(
            name=str(document.get("name", path.stem)),
            bounds=bounds,
            start_pose=start_pose,
            obstacles=obstacles,
        )
        self._validate_layout(floor_map)
        return floor_map

    @staticmethod
    def _number(mapping: dict[str, Any], key: str, context: str) -> float:
        value = mapping.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{context}.{key} must be a number")
        numeric = float(value)
        if not math.isfinite(numeric):
            raise ValueError(f"{context}.{key} must be finite")
        return numeric

    @classmethod
    def _rectangle(cls, value: Any, context: str) -> Rectangle:
        if not isinstance(value, dict):
            raise ValueError(f"{context} must be an object")
        return Rectangle(
            cls._number(value, "min_x", context),
            cls._number(value, "min_y", context),
            cls._number(value, "max_x", context),
            cls._number(value, "max_y", context),
        )

    @classmethod
    def _pose(cls, value: Any) -> Pose:
        if not isinstance(value, dict):
            raise ValueError("start_pose must be an object")
        return Pose(
            cls._number(value, "x", "start_pose"),
            cls._number(value, "y", "start_pose"),
            cls._number(value, "theta", "start_pose"),
        )

    @classmethod
    def _obstacle(cls, value: Any, index: int) -> Rectangle:
        context = f"obstacles[{index}]"
        if not isinstance(value, dict) or value.get("type") != "rectangle":
            raise ValueError(f"{context}.type must be 'rectangle'")
        return cls._rectangle(value, context)

    @staticmethod
    def _validate_layout(floor_map: FloorMap) -> None:
        bounds = floor_map.bounds
        for index, obstacle in enumerate(floor_map.obstacles):
            if not (
                bounds.min_x <= obstacle.min_x < obstacle.max_x <= bounds.max_x
                and bounds.min_y <= obstacle.min_y < obstacle.max_y <= bounds.max_y
            ):
                raise ValueError(f"obstacles[{index}] must lie inside bounds")
        if not floor_map.point_is_free(floor_map.start_pose.x, floor_map.start_pose.y):
            raise ValueError("start_pose must be inside bounds and outside obstacles")
