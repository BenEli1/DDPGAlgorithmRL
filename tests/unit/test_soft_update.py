"""Exact target interpolation test for the DDPG soft update."""

import torch
from torch import nn

from robot_vacuum_ddpg.ddpg import soft_update


def test_soft_update_exact_math() -> None:
    online = nn.Linear(1, 1)
    target = nn.Linear(1, 1)
    for parameter in online.parameters():
        parameter.data.fill_(4.0)
    for parameter in target.parameters():
        parameter.data.fill_(2.0)

    soft_update(target, online, tau=0.25)

    for parameter in target.parameters():
        assert torch.equal(parameter, torch.full_like(parameter, 2.5))
