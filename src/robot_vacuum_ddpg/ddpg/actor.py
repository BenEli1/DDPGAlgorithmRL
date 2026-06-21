"""Deterministic policy network for normalized continuous robot controls."""

from collections.abc import Sequence

import torch
from torch import nn


class Actor(nn.Module):
    """Map state batches to bounded actions the simulator can consume directly."""

    def __init__(self, state_dim: int, action_dim: int, hidden_sizes: Sequence[int]) -> None:
        super().__init__()
        if state_dim <= 0 or action_dim <= 0 or not hidden_sizes or min(hidden_sizes) <= 0:
            raise ValueError("Actor dimensions and hidden sizes must be positive")
        layers: list[nn.Module] = []
        input_dim = state_dim
        for hidden_dim in hidden_sizes:
            layers.extend((nn.Linear(input_dim, hidden_dim), nn.ReLU()))
            input_dim = hidden_dim
        layers.extend((nn.Linear(input_dim, action_dim), nn.Tanh()))
        self.network = nn.Sequential(*layers)

    def forward(self, states: torch.Tensor) -> torch.Tensor:
        """Return actions in [-1, 1] through the explicit final tanh layer."""
        return self.network(states)
