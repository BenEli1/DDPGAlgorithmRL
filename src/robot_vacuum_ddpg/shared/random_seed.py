"""Reproducible random-number helpers shared by simulation and learning."""

import random

import numpy as np
import torch


def seed_everything(seed: int) -> np.random.Generator:
    """Seed each local stochastic backend and return an isolated NumPy generator."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    return np.random.default_rng(seed)
