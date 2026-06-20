# Product Requirements Document

## 1. Product statement

Build a compact educational application in which a circular robotic vacuum learns smooth, continuous navigation and cleaning behavior through DDPG. The product must make the simulator, reinforcement-learning algorithm, training evidence, and design decisions easy for a lecturer or automated checker to inspect.

## 2. Problem and users

Discrete actions hide the central control problem of a robot: choosing continuously varying motor and steering commands. The project needs a transparent demonstration that DDPG can learn from continuous state and action vectors in a project-owned environment.

Primary users are the course lecturer and AI checker. A secondary user is a student who wants to reproduce a short run, inspect the algorithm, and extend the map adapter.

## 3. Source hierarchy

1. Exercise 05 assignment PDF.
2. Lecture 09 DDPG notes.
3. DDPG Autonomous Blueprint.
4. General software submission guidelines.

The current PRD was drafted from all four local sources. The exercise explicitly takes precedence.

## 4. Goals

- Demonstrate a correct, from-scratch PyTorch DDPG implementation.
- Demonstrate a custom 2D continuous-control simulator without ready-made environment platforms.
- Reward useful cleaning coverage while discouraging contact and inefficient motion.
- Produce reproducible metrics and the three required visualizations.
- Keep responsibilities modular and expose use cases through one SDK facade.
- Make every assignment-critical mechanism findable in code, tests, and the final report.

## 5. Non-goals

- Photorealistic physics, SLAM, mapping uncertainty, wheel slip, battery simulation, or a live GUI.
- Full HouseExpo dataset ingestion in release 1.
- Comparison experiments against PPO, DQN, or other libraries.
- Production robotics safety or deployment on physical hardware.
- Cloud services, external APIs, network calls, or an API gatekeeper; the release is fully local.
- Guaranteed high-performing convergence in the short checker smoke run.

## 6. Functional requirements

### FR-1 Custom environment

The application shall load a JSON map, reset a robot to a valid pose, advance deterministic 2D kinematics by one time step, detect collision, update coverage, calculate reward, and return a continuous state vector. It shall not derive from or wrap Gymnasium, Gazebo, or another external RL environment.

### FR-2 Continuous control

The environment shall accept exactly two normalized real-valued controls:

```text
action[0] = normalized linear command in [-1, 1]
action[1] = normalized angular command in [-1, 1]
```

Commands shall be clipped defensively and scaled by simulator configuration.

### FR-3 Continuous observations

The default state shall contain normalized distance-ray readings, normalized linear and angular velocity, `sin(theta)`, `cos(theta)`, cleaning coverage ratio, and a collision/contact flag. With seven default rays, the default state dimension is 13. State shape shall be exposed by the environment rather than duplicated in the agent.

### FR-4 Cleaning objective and termination

Newly cleaned free-space grid cells shall earn positive reward. Collision, elapsed time, and unnecessary control effort shall incur penalties. Episodes shall end at maximum steps or configured target coverage; a collision terminates only if the configuration explicitly enables it.

### FR-5 DDPG agent

The agent shall implement an actor `mu(s)`, critic `Q(s,a)`, target actor, target critic, replay buffer, Gaussian training noise, critic Bellman update, actor policy-gradient update, and soft target updates. The actor's final activation shall be `tanh`.

### FR-6 Training and evaluation

Training shall collect transitions `(state, action, reward, next_state, done)`, add them to replay, sample random mini-batches after warm-up, update both networks, soft-update targets, and save metrics. Evaluation shall use the actor without exploration noise.

### FR-7 Visualization and outputs

The product shall save cumulative reward per episode, critic loss over update steps, and an evaluation trajectory over the map with start and final markers. Metrics shall also be machine-readable JSON under `results/metrics/`.

### FR-8 SDK and CLI

The CLI shall contain argument parsing and user-facing error handling only. Training, evaluation, and plotting shall be available through a `VacuumSDK` high-level interface to avoid duplicated business logic.

### FR-9 Configuration and reproducibility

Simulator and training parameters shall be stored in versioned JSON configuration. Seed control shall cover Python, NumPy, PyTorch, environment reset, replay sampling, and Gaussian noise where applicable.

### FR-10 Inspectability

The report shall identify exact code locations for actor, critic, actor `tanh`, replay buffer, Gaussian noise, Bellman target, actor loss, and soft update, and shall include the actual hyperparameter values used for the documented run.

### FR-11 Required graph semantics

The learning curve shall use episode number on the x-axis and cumulative episode reward on the y-axis. The critic-loss graph shall use optimizer update index on the x-axis and mean critic MSE on the y-axis. The trajectory figure shall draw map bounds and obstacles, a continuous path line, and distinct start and final markers. Titles, axes, legends where needed, and non-empty data are mandatory.

## 7. Non-functional requirements

- Python 3.11+, NumPy, PyTorch, Matplotlib, pytest, and Ruff.
- `uv` for locking, syncing, and all documented commands; no `requirements.txt` as a dependency source.
- Type hints and docstrings on public modules, classes, functions, and methods.
- Small modules with a single responsibility; target at most 150 code lines per file, excluding blanks and comments, unless a justified exception is recorded.
- Clear validation errors for malformed maps, invalid configuration, shape mismatch, and missing checkpoints.
- No secrets; `.env-example` is included only to meet submission structure and states that no secret is required.
- Headless plotting for CI and checker environments.
- At least 85% test coverage is a project quality target; critical DDPG equations and environment transitions require direct tests regardless of aggregate coverage.

## 8. Proposed architecture and ownership

| Layer | Ownership | Must not own |
|---|---|---|
| CLI | Parse commands, print results, choose exit codes | Training logic or DDPG math |
| SDK | Stable high-level `train`, `evaluate`, and `plot` use cases | Neural-network internals |
| Training | Episode orchestration and metrics | Geometry or network definitions |
| Simulator | Map, geometry, sensors, robot, coverage, reward | PyTorch or replay memory |
| DDPG | Networks, replay, noise, losses, target updates | Map format or plotting |
| Visualization | Read maps/metrics and write figures | Mutate training state |
| Shared/infrastructure | Config validation, paths, seeds, versions | Domain policy |

## 9. Data and interface contracts

### Environment step

```text
reset(seed?) -> state: float32[state_dim]
step(action: float32[2])
  -> (next_state: float32[state_dim], reward: float, done: bool, info: dict)
```

`info` shall include at least `collision`, `newly_cleaned_cells`, `coverage_ratio`, `pose`, and `step_count`.

### Agent

```text
select_action(state, explore: bool) -> float32[2]
observe(state, action, reward, next_state, done) -> None
update() -> optional update metrics
save(path) / load(path)
```

### Metrics file

The JSON document shall include schema version, seed, resolved configuration, episode rewards, episode coverage, collision counts, critic losses, actor losses, elapsed time, and artifact paths.

## 10. Default hyperparameter baseline

These are design defaults, not claimed optimized values:

| Parameter | Planned default | Rationale |
|---|---:|---|
| Actor learning rate | `1e-4` | Conservative deterministic-policy updates |
| Critic learning rate | `1e-3` | Faster value fitting than policy movement |
| Discount `gamma` | `0.99` | Values long-horizon cleaning |
| Soft update `tau` | `0.005` | Slowly moving target networks |
| Gaussian sigma | `0.20` | Material early exploration in normalized action space |
| Replay capacity | `100000` | Diverse history without excessive memory |
| Batch size | `64` | Stable, checker-friendly update size |
| Hidden layers | `[256, 256]` | Standard compact MLP baseline |
| Warm-up transitions | `1000` | Avoid updates on a tiny correlated sample |
| Episodes | `200` | Modest local training budget |
| Max steps/episode | `500` | Bounded runtime and meaningful coverage horizon |

All values will live in configuration and the final report will state any overrides.

## 11. Acceptance criteria

| ID | Verifiable acceptance criterion |
|---|---|
| AC-1 | A repository search finds no dependency or import of Gymnasium, Gazebo, Stable-Baselines, or RLlib. |
| AC-2 | For at least 100 sampled inputs, actor output shape is `(batch, 2)` and every value is within `[-1, 1]`. |
| AC-3 | Environment reset returns a finite `float32` state of documented shape; step accepts continuous actions and returns the documented tuple. |
| AC-4 | A known action advances the pose according to documented kinematics within numerical tolerance. |
| AC-5 | Collision against a boundary or obstacle prevents penetration and produces a negative collision contribution. |
| AC-6 | Cleaning a new cell produces more reward than revisiting the same cell under otherwise equal conditions. |
| AC-7 | Replay sampling returns randomized tensors/arrays with correct state, action, reward, next-state, and done shapes. |
| AC-8 | Critic output shape is `(batch, 1)` for batched states and actions. |
| AC-9 | With controlled parameters, one soft update equals `tau*online + (1-tau)*target` exactly within tolerance. |
| AC-10 | Gaussian exploration changes at least one selected action under a fixed nonzero sigma, and the final action is clipped to `[-1, 1]`. |
| AC-11 | A dedicated smoke configuration with two episodes, 20 steps per episode, batch size 16, and warm-up 16 performs at least one update and writes a valid metrics JSON plus three non-empty PNG files. |
| AC-12 | `uv run pytest` and `uv run ruff check .` pass; test coverage meets the configured gate or a documented, lecturer-visible exception is present. |
| AC-13 | `docs/SUMMARY_REPORT.md` links exact implemented locations and answers the three conceptual assignment questions. |
| AC-14 | Plot tests or artifact inspection confirm the required axis labels, trajectory map geometry, path line, and start/final markers. |
| AC-15 | `pyproject.toml` and committed `uv.lock` are present, `requirements.txt` is absent, and documented execution uses `uv run`. |
| AC-16 | The CLI delegates train/evaluate/plot operations to the SDK; a code review finds no duplicated domain logic in entrypoints. |

## 12. Requirement traceability

| Exercise 05 requirement | Specification | Planned verification/evidence |
|---|---|---|
| Continuous robotic control | FR-2 and simulator PRD Sections 3 and 7 | action clipping, kinematics, and actor-bound tests |
| Custom simulator | FR-1 and simulator PRD | dependency/import search and simulator integration tests |
| Sensor/coverage state | FR-3 and simulator PRD Section 7 | state ordering, shape, range, and seed tests |
| Positive cleaning and negative contact/inefficiency reward | FR-4 and simulator PRD Section 8 | new/revisit, collision, and reward-component tests |
| DDPG actor-critic | FR-5 and DDPG PRD Sections 4-5 | network shape and gradient-update tests |
| Replay, Gaussian noise, and targets | FR-5 and DDPG PRD Sections 6-9 | replay, noise, mask, and soft-update tests |
| Training loop | FR-6 and DDPG PRD Section 10 | seeded smoke run and metrics JSON |
| Three required visualizations | FR-7 and FR-11 | three inspected PNG artifacts |
| Exact code explanation and hyperparameters | FR-10 | completed summary-report index and run table |
| Professional packaging | non-functional requirements | clean uv sync, pytest/coverage, Ruff, and repository audit |

## 13. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Training is unstable or slow | Seed runs, normalize inputs, separate smoke correctness from long training, save resolved configuration. |
| Reward hacking by spinning or wall hugging | Reward only first-time coverage, penalize collision/time/control, inspect trajectories. |
| Robot tunnels through obstacles | Use bounded time step and segment/circle collision validation before pose commit. |
| HouseExpo schema is more complex than the sample | Define a loader protocol and honest adapter boundary; do not claim full support. |
| Results are not reproducible across hardware | Record seed and package lock; allow minor floating-point variation. |
| Documentation drifts from code | Final audit compares paths, dimensions, defaults, and commands against implementation. |

## 14. Release definition

Release 1 is complete only when all mandatory artifacts exist, acceptance criteria are checked, results were generated by the committed code, and limitations are stated honestly. Documentation completion alone is the gate to begin implementation, not a product release.
