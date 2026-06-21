"""Slow target-network interpolation for stable Bellman targets."""

from torch import nn


def soft_update(target: nn.Module, online: nn.Module, tau: float) -> None:
    """Apply target = tau * online + (1 - tau) * target in place."""
    if not 0.0 < tau <= 1.0:
        raise ValueError("tau must be in (0, 1]")
    for target_parameter, online_parameter in zip(
        target.parameters(), online.parameters(), strict=True
    ):
        target_parameter.data.mul_(1.0 - tau).add_(online_parameter.data, alpha=tau)
