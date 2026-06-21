"""DDPG agent that owns policy/value networks and their mathematical updates."""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn

from robot_vacuum_ddpg.ddpg.actor import Actor
from robot_vacuum_ddpg.ddpg.critic import Critic
from robot_vacuum_ddpg.ddpg.noise import add_gaussian_noise
from robot_vacuum_ddpg.ddpg.replay_buffer import ReplayBuffer
from robot_vacuum_ddpg.ddpg.soft_update import soft_update


@dataclass(frozen=True, slots=True)
class AgentConfig:
    """Hyperparameters that affect DDPG network construction and updates."""

    actor_lr: float
    critic_lr: float
    gamma: float
    tau: float
    noise_sigma: float
    batch_size: int
    replay_buffer_size: int
    actor_hidden_sizes: tuple[int, ...]
    critic_hidden_sizes: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class UpdateStats:
    """Scalar learning diagnostics emitted after one mini-batch update."""

    actor_loss: float
    critic_loss: float


class DDPGAgent:
    """Combine DDPG networks, targets, replay, noise, and optimizers."""

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        config: AgentConfig,
        seed: int,
        device: str = "cpu",
    ) -> None:
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.config = config
        self.device = torch.device(device)
        self.actor = Actor(state_dim, action_dim, config.actor_hidden_sizes).to(self.device)
        self.critic = Critic(state_dim, action_dim, config.critic_hidden_sizes).to(self.device)
        self.target_actor = Actor(state_dim, action_dim, config.actor_hidden_sizes).to(self.device)
        self.target_critic = Critic(state_dim, action_dim, config.critic_hidden_sizes).to(self.device)
        self.target_actor.load_state_dict(self.actor.state_dict())
        self.target_critic.load_state_dict(self.critic.state_dict())
        for network in (self.target_actor, self.target_critic):
            network.requires_grad_(False)
            network.eval()
        self.actor_optimizer = torch.optim.Adam(self.actor.parameters(), lr=config.actor_lr)
        self.critic_optimizer = torch.optim.Adam(self.critic.parameters(), lr=config.critic_lr)
        self.replay = ReplayBuffer(config.replay_buffer_size, state_dim, action_dim, seed)
        self._noise_rng = np.random.default_rng(seed)

    def select_action(self, state: np.ndarray, explore: bool = False) -> np.ndarray:
        """Return one deterministic action, optionally perturbed for data collection."""
        if state.shape != (self.state_dim,):
            raise ValueError(f"Expected state shape ({self.state_dim},), got {state.shape}")
        state_tensor = torch.as_tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            action = self.actor(state_tensor).squeeze(0).cpu().numpy()
        if explore:
            return add_gaussian_noise(action, self.config.noise_sigma, self._noise_rng)
        return action.astype(np.float32)

    def update(self) -> UpdateStats | None:
        """Run one terminal-masked critic update, actor update, and target update."""
        if len(self.replay) < self.config.batch_size:
            return None
        batch = self.replay.sample(self.config.batch_size)
        states = self._tensor(batch.states)
        actions = self._tensor(batch.actions)
        rewards = self._tensor(batch.rewards)
        next_states = self._tensor(batch.next_states)
        dones = self._tensor(batch.dones)
        with torch.no_grad():
            next_actions = self.target_actor(next_states)
            targets = rewards + self.config.gamma * (1.0 - dones) * self.target_critic(
                next_states, next_actions
            )
        critic_loss = nn.functional.mse_loss(self.critic(states, actions), targets)
        self.critic_optimizer.zero_grad(set_to_none=True)
        critic_loss.backward()
        self.critic_optimizer.step()

        self.critic.requires_grad_(False)
        actor_loss = -self.critic(states, self.actor(states)).mean()
        self.actor_optimizer.zero_grad(set_to_none=True)
        actor_loss.backward()
        self.actor_optimizer.step()
        self.critic.requires_grad_(True)
        soft_update(self.target_actor, self.actor, self.config.tau)
        soft_update(self.target_critic, self.critic, self.config.tau)
        return UpdateStats(float(actor_loss.item()), float(critic_loss.item()))

    def save_checkpoint(self, path: Path, seed: int, training_step: int) -> Path:
        """Persist enough state for deterministic evaluation and continued training."""
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "schema_version": "1.00",
                "state_dim": self.state_dim,
                "action_dim": self.action_dim,
                "agent_config": asdict(self.config),
                "seed": seed,
                "training_step": training_step,
                "actor": self.actor.state_dict(),
                "critic": self.critic.state_dict(),
                "target_actor": self.target_actor.state_dict(),
                "target_critic": self.target_critic.state_dict(),
                "actor_optimizer": self.actor_optimizer.state_dict(),
                "critic_optimizer": self.critic_optimizer.state_dict(),
            },
            path,
        )
        return path

    @classmethod
    def load_checkpoint(cls, path: Path, device: str = "cpu") -> "DDPGAgent":
        """Reconstruct an agent after validating the checkpoint's public schema."""
        if not path.exists():
            raise ValueError(f"Checkpoint does not exist: {path}")
        payload: dict[str, Any] = torch.load(path, map_location=device, weights_only=True)
        if payload.get("schema_version") != "1.00":
            raise ValueError("Unsupported checkpoint schema")
        config_data = dict(payload["agent_config"])
        config_data["actor_hidden_sizes"] = tuple(config_data["actor_hidden_sizes"])
        config_data["critic_hidden_sizes"] = tuple(config_data["critic_hidden_sizes"])
        agent = cls(
            int(payload["state_dim"]),
            int(payload["action_dim"]),
            AgentConfig(**config_data),
            int(payload["seed"]),
            device,
        )
        agent.actor.load_state_dict(payload["actor"])
        agent.critic.load_state_dict(payload["critic"])
        agent.target_actor.load_state_dict(payload["target_actor"])
        agent.target_critic.load_state_dict(payload["target_critic"])
        agent.actor_optimizer.load_state_dict(payload["actor_optimizer"])
        agent.critic_optimizer.load_state_dict(payload["critic_optimizer"])
        return agent

    def _tensor(self, values: np.ndarray) -> torch.Tensor:
        return torch.as_tensor(values, dtype=torch.float32, device=self.device)
