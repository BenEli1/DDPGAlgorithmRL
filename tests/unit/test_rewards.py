"""Tests for transparent reward behavior."""

import numpy as np

from robot_vacuum_ddpg.simulator.rewards import RewardConfig, calculate_reward


def test_new_cleaning_is_better_than_revisit() -> None:
    config = RewardConfig(1.0, 25.0, 5.0, 0.01, 0.01)
    action = np.zeros(2, dtype=np.float32)

    cleaning = calculate_reward(1, False, False, action, config)
    revisit = calculate_reward(0, False, False, action, config)

    assert cleaning.total > revisit.total
    assert cleaning.cleaning == 1.0


def test_collision_penalty_is_negative() -> None:
    config = RewardConfig(1.0, 25.0, 5.0, 0.01, 0.01)

    result = calculate_reward(0, True, False, np.zeros(2, dtype=np.float32), config)

    assert result.collision == -5.0
    assert result.total < 0.0
