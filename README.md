# DDPG Robotic Vacuum Simulator

A small, inspectable Python project for Bar-Ilan University Vibe Coding Workshop Exercise 05. The current milestone provides a custom 2D robotic-vacuum simulator; a from-scratch PyTorch DDPG agent is the next planned milestone.

> Milestone status: project scaffold, simulator, random-policy CLI demo, trajectory plotting, and simulator tests are implemented. DDPG networks, replay, exploration, training, learning curves, critic-loss graphs, checkpoints, and trained-policy results remain pending.

## Safe assignment scope

The first release will demonstrate the complete DDPG learning pipeline without trying to reproduce a physics engine:

- A custom, headless 2D simulator; no Gymnasium, Gazebo, Stable-Baselines, RLlib, or external environment.
- A circular robot with pose `(x, y, theta)` and differential-drive-like control.
- A two-value continuous action `[linear_command, angular_command]`, with both values clipped to `[-1, 1]` and scaled by configured speed limits.
- JSON floor plans containing a bounded free area and rectangular obstacles.
- A map-loader interface designed for later HouseExpo adaptation, plus one small project-native sample map. Full HouseExpo compatibility is not claimed for the first release.
- Normalized ray distance sensors, robot motion and heading, collision contact, and cleaning coverage in the state vector.
- Reward for newly cleaned cells and completion; penalties for collisions, time, and excessive actuation.
- A future DDPG actor, critic, target networks, replay buffer, Gaussian exploration noise, and soft target updates implemented directly in PyTorch.
- A working Matplotlib trajectory output now; reward and critic-loss plots after DDPG training exists.
- Deterministic simulator tests and a random-policy CLI demo suitable for automated checking.

## Source priority

Requirements are interpreted in this order:

1. `EX05-DDPG-Robot-Simulator (1).pdf`
2. `gemini-L09-Deep-Deterministic-Policy-Gradient-DDPG-and-EX05t.pdf`
3. `DDPG_Autonomous_Blueprint.pdf`
4. `software_submission_guidelines-V3.pdf`

If this README conflicts with a higher-priority source, the source wins and the documentation must be corrected before implementation.

## Current and planned repository structure

```text
.
|-- README.md
|-- pyproject.toml
|-- uv.lock
|-- .gitignore
|-- .env-example
|-- assets/
|-- config/
|   |-- default_simulator.json
|   |-- default_training.json
|   `-- smoke_training.json
|-- data/
|   `-- sample_maps/
|       `-- simple_house.json
|-- docs/
|   |-- PRD.md
|   |-- PLAN.md
|   |-- TODO.md
|   |-- PRD_ddpg_algorithm.md
|   |-- PRD_simulator.md
|   |-- SUMMARY_REPORT.md
|   `-- PROMPT_LOG.md
|-- results/
|   |-- checkpoints/
|   |-- metrics/
|   |-- plots/
|   `-- trajectories/
|-- src/
|   `-- robot_vacuum_ddpg/
|       |-- __init__.py
|       |-- main.py
|       |-- sdk/
|       |   |-- __init__.py
|       |   `-- sdk.py
|       |-- simulator/
|       |   |-- __init__.py
|       |   |-- environment.py
|       |   |-- geometry.py
|       |   |-- map_loader.py
|       |   |-- rewards.py
|       |   |-- robot.py
|       |   `-- sensors.py
|       |-- ddpg/
|       |   |-- __init__.py
|       |   |-- actor.py
|       |   |-- agent.py
|       |   |-- critic.py
|       |   |-- noise.py
|       |   |-- replay_buffer.py
|       |   `-- soft_update.py
|       |-- training/
|       |   |-- __init__.py
|       |   |-- metrics.py
|       |   `-- trainer.py
|       |-- visualization/
|       |   |-- __init__.py
|       |   |-- plots.py
|       |   `-- trajectory.py
|       `-- shared/
|           |-- __init__.py
|           |-- config.py
|           |-- paths.py
|           |-- random_seed.py
|           `-- version.py
`-- tests/
    |-- unit/
    `-- integration/
```

The scaffold, simulator, SDK, shared utilities, sample map, visualization, and tests now exist. Files shown under `ddpg/` and most files under `training/` remain future work; their package directories contain no DDPG or training logic yet.

## Architecture

The CLI delegates the implemented random-policy use case to a single SDK facade. The SDK coordinates the simulator and trajectory visualization. Future DDPG and trainer modules will join through the documented state/action contract; no DDPG logic exists in the current milestone.

```text
CLI
 |
 v
VacuumSDK  ---> training orchestration ---> metrics and plots
 |                    |                         |
 +--> simulator <-----+---- transitions ----> DDPG agent
       ^                                         |
       `------------ state/action contract ------'
```

See [docs/PRD.md](docs/PRD.md), [docs/PRD_simulator.md](docs/PRD_simulator.md), and [docs/PRD_ddpg_algorithm.md](docs/PRD_ddpg_algorithm.md) for the formal contracts.

## Installation and current commands

Python 3.11 or newer and `uv` are required:

```bash
uv sync --extra dev
uv run robot-vacuum --max-steps 100 --seed 42
uv run pytest
uv run ruff check .
```

The CLI runs one continuous random-policy episode and writes `results/trajectories/random_policy.png`. The following commands remain planned and intentionally unavailable until DDPG is implemented:

```bash
uv run robot-vacuum train --config config/default_training.json
uv run robot-vacuum evaluate --checkpoint results/checkpoints/best_actor.pt
uv run robot-vacuum train --config config/smoke_training.json
```

The smoke configuration will use two episodes, 20 steps per episode, batch size 16, warm-up 16, and seed 42. It verifies integration and artifact generation only; it is not evidence of convergence.

## Planned result artifacts

| Artifact | Path | Status |
|---|---|---|
| Random-policy trajectory | `results/trajectories/random_policy.png` | Generated by current CLI; ignored by Git |
| Cumulative reward curve | `results/plots/learning_curve.png` | Pending DDPG training |
| Critic loss curve | `results/plots/critic_loss.png` | Pending DDPG training |
| Evaluation trajectory | `results/trajectories/evaluation_trajectory.png` | Pending trained-policy evaluation |
| Machine-readable metrics | `results/metrics/training_metrics.json` | Pending DDPG training |

No generated result is claimed until the files exist and the final audit records the command used to create them.

## Exercise 05 compliance at a glance

| Exercise requirement | Planned evidence |
|---|---|
| DDPG rather than DQN, PPO, or a Q-table | Project-owned PyTorch actor-critic implementation and tests |
| Continuous action in `[-1, 1]` | Two-value linear/angular actor output with final `tanh` and defensive clipping |
| Continuous state | Normalized ray distances, velocity, heading, coverage, and contact flag |
| No ready-made simulator | Custom geometry, kinematics, sensing, collision, coverage, and reward modules |
| Actor and critic | Separate, directly inspectable network modules |
| Target networks and soft updates | Target actor/critic plus exact `tau` interpolation test |
| Replay and exploration | Fixed-capacity replay buffer and training-only Gaussian noise |
| Required graphs | Reward, critic-loss, and map trajectory PNG files under `results/` |
| HouseExpo intent | Loader abstraction and honest release-1 sample-map limitation |
| Professional submission | uv lockfile, SDK facade, configs, type hints, docstrings, pytest, Ruff, and prompt log |

The canonical DDPG configuration names are reserved in `config/default_training.json`; their use by an agent remains pending.

| Configuration key | Planned default |
|---|---:|
| `actor_lr` | `0.0001` |
| `critic_lr` | `0.001` |
| `gamma` | `0.99` |
| `tau` | `0.005` |
| `noise_sigma` | `0.20` |
| `batch_size` | `64` |
| `replay_buffer_size` | `100000` |

## Quality gates

- `uv.lock` exists and must be committed with this milestone; `pyproject.toml` is the dependency source of truth.
- No `requirements.txt` is used as a second dependency source.
- `uv run pytest` passes with at least 85% coverage for `src/` where practical for this exercise.
- `uv run ruff check .` reports zero violations.
- Environment actions are clipped to `[-1, 1]`; future actor outputs must meet the same bound.
- The simulator is project-owned and imports no forbidden environment framework.
- A seeded random-policy run creates a trajectory; DDPG smoke training and its required plots remain pending.
- The summary report links exact code locations and records actual hyperparameters and limitations.

## Documentation

- [Product requirements](docs/PRD.md)
- [Implementation plan](docs/PLAN.md)
- [Tracked work](docs/TODO.md)
- [DDPG specification](docs/PRD_ddpg_algorithm.md)
- [Simulator specification](docs/PRD_simulator.md)
- [Summary report](docs/SUMMARY_REPORT.md)
- [AI prompt log](docs/PROMPT_LOG.md)

## Academic honesty and limitations

The documentation and later implementation are AI-assisted; material prompts and decisions are recorded in `docs/PROMPT_LOG.md`. The planned sample-map loader is an extension point toward HouseExpo, not a claim of full HouseExpo support. Training quality can vary by seed and compute budget, so functional correctness and saved evidence are separated from any claim of convergence.
