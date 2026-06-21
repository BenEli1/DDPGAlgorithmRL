"""Gaussian exploration for deterministic policies."""

import numpy as np


def add_gaussian_noise(
    action: np.ndarray,
    sigma: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Perturb collection actions and clip at the simulator's normalized boundary."""
    if sigma < 0.0:
        raise ValueError("sigma must be nonnegative")
    noise = rng.normal(0.0, sigma, size=action.shape)
    return np.clip(action + noise, -1.0, 1.0).astype(np.float32)
