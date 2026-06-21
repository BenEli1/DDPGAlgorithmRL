"""State-action value network used by DDPG."""

from collections.abc import Sequence

import torch
from torch import nn


class Critic(nn.Module):
    """Estimate one unbounded Q-value from each concatenated state-action pair."""

    def __init__(self, state_dim: int, action_dim: int, hidden_sizes: Sequence[int]) -> None:
        super().__init__()
        if state_dim <= 0 or action_dim <= 0 or not hidden_sizes or min(hidden_sizes) <= 0:
            raise ValueError("Critic dimensions and hidden sizes must be positive")
        layers: list[nn.Module] = []
        input_dim = state_dim + action_dim
        for hidden_dim in hidden_sizes:
            layers.extend((nn.Linear(input_dim, hidden_dim), nn.ReLU()))
            input_dim = hidden_dim
        layers.append(nn.Linear(input_dim, 1))
        self.network = nn.Sequential(*layers)

    def forward(self, states: torch.Tensor, actions: torch.Tensor) -> torch.Tensor:
        """Concatenate along the feature dimension and return scalar Q estimates."""
        if states.ndim != 2 or actions.ndim != 2 or states.shape[0] != actions.shape[0]:
            raise ValueError("Critic expects equally sized two-dimensional batches")
        return self.network(torch.cat((states, actions), dim=-1))
