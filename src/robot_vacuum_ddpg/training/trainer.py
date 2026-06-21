"""Episode orchestration that joins the SDK-created simulator to DDPG."""

import time
from dataclasses import asdict, dataclass
from pathlib import Path

from robot_vacuum_ddpg.ddpg import DDPGAgent
from robot_vacuum_ddpg.shared.paths import PROJECT_ROOT, RESULTS_DIR
from robot_vacuum_ddpg.shared.random_seed import seed_everything
from robot_vacuum_ddpg.simulator.environment import VacuumEnvironment
from robot_vacuum_ddpg.training.config import TrainingConfig
from robot_vacuum_ddpg.training.metrics import TrainingMetrics, write_training_metrics
from robot_vacuum_ddpg.visualization import save_critic_loss, save_learning_curve


@dataclass(frozen=True, slots=True)
class TrainingResult:
    """Paths and counts printed by the CLI after a completed training run."""

    metrics_path: Path
    learning_curve_path: Path
    critic_loss_path: Path
    checkpoint_path: Path
    episodes: int
    updates: int


def train_ddpg(
    environment: VacuumEnvironment,
    config: TrainingConfig,
    output_dir: Path = RESULTS_DIR,
) -> TrainingResult:
    """Train, checkpoint the best observed episode, and save recorded evidence."""
    seed_everything(config.seed)
    agent = DDPGAgent(
        environment.state_dim,
        environment.action_dim,
        config.agent_config(),
        config.seed,
    )
    metrics = TrainingMetrics()
    checkpoint_path = output_dir / "checkpoints" / "best_actor.pt"
    total_steps = 0
    best_reward = float("-inf")
    started = time.perf_counter()
    for episode in range(config.episodes):
        state = environment.reset(seed=config.seed + episode)
        reward_total = 0.0
        for step in range(config.max_steps_per_episode):
            action = (
                environment.sample_random_action()
                if total_steps < config.warmup_transitions
                else agent.select_action(state, explore=True)
            )
            next_state, reward, environment_done, _ = environment.step(action)
            episode_done = environment_done or step + 1 == config.max_steps_per_episode
            agent.replay.add(state, action, reward, next_state, episode_done)
            state = next_state
            reward_total += reward
            total_steps += 1
            if total_steps >= config.warmup_transitions:
                for _ in range(config.updates_per_step):
                    update = agent.update()
                    if update is not None:
                        metrics.actor_losses.append(update.actor_loss)
                        metrics.critic_losses.append(update.critic_loss)
            if episode_done:
                break
        metrics.episode_rewards.append(reward_total)
        metrics.episode_steps.append(step + 1)
        metrics.coverage_percent.append(environment.coverage_ratio * 100.0)
        if reward_total > best_reward:
            best_reward = reward_total
            agent.save_checkpoint(checkpoint_path, config.seed, total_steps)
    duration = time.perf_counter() - started
    learning_path = save_learning_curve(
        metrics.episode_rewards, output_dir / "plots" / "learning_curve.png"
    )
    critic_path = save_critic_loss(
        metrics.critic_losses, output_dir / "plots" / "critic_loss.png"
    )
    metrics_path = output_dir / "metrics" / "training_metrics.json"
    artifacts = {
        "learning_curve": _display_path(learning_path),
        "critic_loss": _display_path(critic_path),
        "checkpoint": _display_path(checkpoint_path),
        "metrics": _display_path(metrics_path),
    }
    document = metrics.as_document(
        asdict(config), environment.state_dim, environment.action_dim, duration, artifacts
    )
    write_training_metrics(document, metrics_path)
    return TrainingResult(
        metrics_path,
        learning_path,
        critic_path,
        checkpoint_path,
        config.episodes,
        len(metrics.critic_losses),
    )
def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()
