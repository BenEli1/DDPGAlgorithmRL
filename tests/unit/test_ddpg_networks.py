"""Shape and range tests for the DDPG function approximators."""

import torch

from robot_vacuum_ddpg.ddpg import Actor, Critic


def test_actor_output_shape_and_range() -> None:
    actor = Actor(state_dim=13, action_dim=2, hidden_sizes=(32, 16))
    actions = actor(torch.randn(5, 13) * 100.0)

    assert actions.shape == (5, 2)
    assert torch.all(actions >= -1.0)
    assert torch.all(actions <= 1.0)


def test_critic_output_shape() -> None:
    critic = Critic(state_dim=13, action_dim=2, hidden_sizes=(32, 16))
    values = critic(torch.randn(5, 13), torch.randn(5, 2))

    assert values.shape == (5, 1)
