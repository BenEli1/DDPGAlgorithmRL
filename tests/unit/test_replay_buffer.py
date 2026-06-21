"""Replay-buffer shape and defensive-storage tests."""

import numpy as np

from robot_vacuum_ddpg.ddpg import ReplayBuffer


def test_replay_buffer_sample_shapes_and_copies() -> None:
    buffer = ReplayBuffer(capacity=4, state_dim=3, action_dim=2, seed=7)
    state = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    action = np.array([0.2, -0.4], dtype=np.float32)
    for index in range(4):
        buffer.add(state + index, action, float(index), state + index + 1, index == 3)
    state[:] = 99.0

    batch = buffer.sample(3)

    assert batch.states.shape == (3, 3)
    assert batch.actions.shape == (3, 2)
    assert batch.rewards.shape == (3, 1)
    assert batch.next_states.shape == (3, 3)
    assert batch.dones.shape == (3, 1)
    assert not np.any(batch.states == 99.0)
