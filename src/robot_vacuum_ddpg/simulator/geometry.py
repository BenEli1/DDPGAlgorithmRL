"""Pure geometry primitives and intersection helpers for the simulator."""

from dataclasses import dataclass
from math import pi

EPSILON = 1e-9


@dataclass(frozen=True, slots=True)
class Pose:
    """Continuous planar robot pose."""

    x: float
    y: float
    theta: float


@dataclass(frozen=True, slots=True)
class Rectangle:
    """Axis-aligned rectangle."""

    min_x: float
    min_y: float
    max_x: float
    max_y: float

    def __post_init__(self) -> None:
        """Reject empty or inverted rectangles."""
        if self.min_x >= self.max_x or self.min_y >= self.max_y:
            raise ValueError("Rectangle minimums must be smaller than maximums")

    def expanded(self, margin: float) -> "Rectangle":
        """Return a rectangle expanded in every direction by margin."""
        return Rectangle(
            self.min_x - margin,
            self.min_y - margin,
            self.max_x + margin,
            self.max_y + margin,
        )


def wrap_angle(angle: float) -> float:
    """Wrap an angle to the half-open interval [-pi, pi)."""
    return (angle + pi) % (2.0 * pi) - pi


def point_in_rectangle(x: float, y: float, rectangle: Rectangle) -> bool:
    """Return whether a point is inside or on a rectangle."""
    return (
        rectangle.min_x - EPSILON <= x <= rectangle.max_x + EPSILON
        and rectangle.min_y - EPSILON <= y <= rectangle.max_y + EPSILON
    )


def circle_intersects_rectangle(
    x: float,
    y: float,
    radius: float,
    rectangle: Rectangle,
) -> bool:
    """Return whether a circle touches or overlaps a rectangle."""
    closest_x = min(max(x, rectangle.min_x), rectangle.max_x)
    closest_y = min(max(y, rectangle.min_y), rectangle.max_y)
    distance_squared = (x - closest_x) ** 2 + (y - closest_y) ** 2
    return distance_squared <= radius**2 + EPSILON


def segment_intersects_rectangle(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    rectangle: Rectangle,
) -> bool:
    """Test a line segment against a rectangle with the slab algorithm."""
    direction_x = end_x - start_x
    direction_y = end_y - start_y
    lower = 0.0
    upper = 1.0
    for origin, direction, minimum, maximum in (
        (start_x, direction_x, rectangle.min_x, rectangle.max_x),
        (start_y, direction_y, rectangle.min_y, rectangle.max_y),
    ):
        if abs(direction) <= EPSILON:
            if origin < minimum - EPSILON or origin > maximum + EPSILON:
                return False
            continue
        first = (minimum - origin) / direction
        second = (maximum - origin) / direction
        near, far = sorted((first, second))
        lower = max(lower, near)
        upper = min(upper, far)
        if lower > upper + EPSILON:
            return False
    return True


def ray_rectangle_distances(
    origin_x: float,
    origin_y: float,
    direction_x: float,
    direction_y: float,
    rectangle: Rectangle,
) -> list[float]:
    """Return nonnegative distances from a ray to rectangle edges."""
    distances: list[float] = []
    if abs(direction_x) > EPSILON:
        for edge_x in (rectangle.min_x, rectangle.max_x):
            distance = (edge_x - origin_x) / direction_x
            hit_y = origin_y + distance * direction_y
            if distance >= 0.0 and rectangle.min_y - EPSILON <= hit_y <= rectangle.max_y + EPSILON:
                distances.append(distance)
    if abs(direction_y) > EPSILON:
        for edge_y in (rectangle.min_y, rectangle.max_y):
            distance = (edge_y - origin_y) / direction_y
            hit_x = origin_x + distance * direction_x
            if distance >= 0.0 and rectangle.min_x - EPSILON <= hit_x <= rectangle.max_x + EPSILON:
                distances.append(distance)
    return distances
