"""Tests for the native JSON map loader."""

from pathlib import Path

import pytest

from robot_vacuum_ddpg.simulator.map_loader import JsonMapLoader


def test_loads_sample_map(sample_map_path: Path) -> None:
    floor_map = JsonMapLoader().load(sample_map_path)

    assert floor_map.name == "simple_house"
    assert floor_map.start_pose.x == 1.0
    assert len(floor_map.obstacles) == 2
    assert floor_map.point_is_free(1.0, 1.0)
    assert not floor_map.point_is_free(4.5, 3.0)


def test_rejects_unsupported_schema(tmp_path: Path) -> None:
    path = tmp_path / "bad_map.json"
    path.write_text('{"schema_version": "9.99"}', encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported map schema_version"):
        JsonMapLoader().load(path)
