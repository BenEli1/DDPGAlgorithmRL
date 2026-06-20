"""Reproducible random-number helpers for simulator-only runs."""

import random

import numpy as np


def seed_everything(seed: int) -> np.random.Generator:
    """Seed Python and NumPy and return a dedicated NumPy generator."""
    random.seed(seed)
    np.random.seed(seed)
    return np.random.default_rng(seed)
