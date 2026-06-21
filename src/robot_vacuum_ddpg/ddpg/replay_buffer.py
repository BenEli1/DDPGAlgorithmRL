"""Fixed-capacity replay memory with reproducible uniform sampling."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class TransitionBatch:
    """A shape-stable NumPy mini-batch ready for tensor conversion."""

    states: np.ndarray
    actions: np.ndarray
    rewards: np.ndarray
    next_states: np.ndarray
    dones: np.ndarray


class ReplayBuffer:
    """Store defensive transition copies and overwrite the oldest at capacity."""

    def __init__(self, capacity: int, state_dim: int, action_dim: int, seed: int) -> None:
        if min(capacity, state_dim, action_dim) <= 0:
            raise ValueError("Replay dimensions and capacity must be positive")
        self.capacity = capacity
        self._states = np.empty((capacity, state_dim), dtype=np.float32)
        self._actions = np.empty((capacity, action_dim), dtype=np.float32)
        self._rewards = np.empty((capacity, 1), dtype=np.float32)
        self._next_states = np.empty((capacity, state_dim), dtype=np.float32)
        self._dones = np.empty((capacity, 1), dtype=np.float32)
        self._rng = np.random.default_rng(seed)
        self._size = 0
        self._position = 0

    def __len__(self) -> int:
        return self._size

    def add(
        self,
        state: np.ndarray,
        action: np.ndarray,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ) -> None:
        """Copy one transition into ring-buffer storage."""
        self._states[self._position] = state
        self._actions[self._position] = action
        self._rewards[self._position, 0] = reward
        self._next_states[self._position] = next_state
        self._dones[self._position, 0] = float(done)
        self._position = (self._position + 1) % self.capacity
        self._size = min(self._size + 1, self.capacity)

    def sample(self, batch_size: int) -> TransitionBatch:
        """Sample without replacement so one update never repeats a transition."""
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if batch_size > self._size:
            raise ValueError("Cannot sample more transitions than the replay buffer contains")
        indices = self._rng.choice(self._size, size=batch_size, replace=False)
        return TransitionBatch(
            self._states[indices].copy(),
            self._actions[indices].copy(),
            self._rewards[indices].copy(),
            self._next_states[indices].copy(),
            self._dones[indices].copy(),
        )
