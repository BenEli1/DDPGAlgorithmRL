"""Shared fixtures for simulator tests."""

import json
from pathlib import Path

import pytest

from robot_vacuum_ddpg.shared.paths import CONFIG_DIR, DATA_DIR
from robot_vacuum_ddpg.simulator.environment import EnvironmentConfig, VacuumEnvironment
from robot_vacuum_ddpg.simulator.map_loader import JsonMapLoader


@pytest.fixture
def sample_map_path() -> Path:
    """Return the committed native sample-map path."""
    return DATA_DIR / "sample_maps" / "simple_house.json"


@pytest.fixture
def environment(sample_map_path: Path) -> VacuumEnvironment:
    """Return a fresh environment using committed default configuration."""
    config_data = json.loads((CONFIG_DIR / "default_simulator.json").read_text(encoding="utf-8"))
    floor_map = JsonMapLoader().load(sample_map_path)
    return VacuumEnvironment(floor_map, EnvironmentConfig.from_dict(config_data))
