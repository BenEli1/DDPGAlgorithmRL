"""Noise-free checkpoint evaluation and trajectory evidence."""

from dataclasses import dataclass
from pathlib import Path

from robot_vacuum_ddpg.ddpg import DDPGAgent
from robot_vacuum_ddpg.simulator.environment import VacuumEnvironment
from robot_vacuum_ddpg.simulator.geometry import Pose
from robot_vacuum_ddpg.visualization import save_trajectory_plot


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    """Deterministic evaluation summary that makes no performance claim."""

    trajectory_path: Path
    steps: int
    total_reward: float
    coverage_percent: float
    collisions: int


def evaluate_checkpoint(
    environment: VacuumEnvironment,
    checkpoint_path: Path,
    output_path: Path,
    seed: int,
) -> EvaluationResult:
    """Evaluate without exploration noise and render the simulator-owned trajectory."""
    agent = DDPGAgent.load_checkpoint(checkpoint_path)
    if (agent.state_dim, agent.action_dim) != (environment.state_dim, environment.action_dim):
        raise ValueError("Checkpoint dimensions do not match the configured simulator")
    state = environment.reset(seed=seed)
    reward_total = 0.0
    collisions: list[Pose] = []
    while not environment.done:
        state, reward, _, info = environment.step(agent.select_action(state, explore=False))
        reward_total += reward
        if info["collision"]:
            collisions.append(info["attempted_pose"])
    save_trajectory_plot(
        environment.floor_map,
        environment.trajectory,
        output_path,
        collision_points=collisions,
        cleaned_cells=environment.cleaned_cells,
        title=f"DDPG checkpoint evaluation: {environment.floor_map.name}",
    )
    return EvaluationResult(
        output_path,
        environment.step_count,
        reward_total,
        environment.coverage_ratio * 100.0,
        len(collisions),
    )
