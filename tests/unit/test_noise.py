"""Exploration-noise tests at the normalized action boundary."""

import numpy as np

from robot_vacuum_ddpg.ddpg import add_gaussian_noise


def test_gaussian_noise_flow_clips_actions() -> None:
    action = np.array([0.95, -0.95], dtype=np.float32)
    noisy = add_gaussian_noise(action, sigma=10.0, rng=np.random.default_rng(42))

    assert noisy.shape == (2,)
    assert noisy.dtype == np.float32
    assert np.all(noisy >= -1.0)
    assert np.all(noisy <= 1.0)
    assert not np.array_equal(noisy, action)


def test_zero_sigma_preserves_action() -> None:
    action = np.array([0.25, -0.5], dtype=np.float32)

    assert np.array_equal(
        add_gaussian_noise(action, sigma=0.0, rng=np.random.default_rng(42)), action
    )
