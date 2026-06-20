# Project TODO

Legend: `[ ]` pending, `[x]` verified complete. A task is checked only when its artifact or command evidence exists.

## Documentation-first gate

- [x] Read the Exercise 05 assignment PDF.
- [x] Read the Lecture 09 DDPG notes.
- [x] Inspect the DDPG Autonomous Blueprint PDF.
- [x] Read the software submission guidelines PDF.
- [x] Define a safe, non-overengineered release scope.
- [x] Draft `README.md`.
- [x] Draft `docs/PRD.md` with measurable acceptance criteria.
- [x] Draft `docs/PLAN.md` with gated development phases.
- [x] Draft `docs/PRD_ddpg_algorithm.md`.
- [x] Draft `docs/PRD_simulator.md`.
- [x] Draft `docs/SUMMARY_REPORT.md` without invented results.
- [x] Draft `docs/PROMPT_LOG.md`.
- [x] Strictly review the docs against assignment-critical DDPG, simulator, visualization, and software requirements.
- [x] Perform a second strict-grader pass and resolve ambiguous collision, plotting, TDD, and submission evidence.
- [ ] Lecturer/user approval of documentation gate, if requested.

## Scaffold

- [x] Confirm the workspace is an initialized Git repository tracking `origin/main`.
- [x] Create `pyproject.toml` with Python and dependency metadata.
- [x] Configure Ruff, pytest, and coverage.
- [x] Create `uv.lock`.
- [ ] Commit `uv.lock` with the scaffold milestone.
- [x] Add `.gitignore` and `.env-example`.
- [x] Create package, test, config, data, assets, and results directories.
- [x] Add package version `1.0.0` and configuration schema version `1.00`.
- [x] Add `config/smoke_training.json` with two episodes, 20 steps, batch size 16, warm-up 16, and seed 42.
- [x] Add CLI entry point and SDK facade for the random-policy simulator demo.
- [x] Verify package import and CLI execution through `uv run`.

## Simulator

- [x] Define map and geometry models.
- [x] Add `MapLoader` protocol and native JSON loader.
- [x] Add and validate `data/sample_maps/simple_house.json`.
- [x] Implement circle/segment and circle/rectangle collision checks.
- [x] Reject the full proposed pose on collision and verify pose remains unchanged.
- [x] Test swept-path collision so a fast step cannot tunnel through an obstacle.
- [x] Implement ray distance intersections.
- [x] Implement robot pose and continuous kinematics.
- [x] Clip normalized actions to `[-1, 1]`.
- [x] Implement seven normalized distance sensors.
- [x] Implement the documented 13-value default state.
- [x] Implement free-space coverage grid and cleaning disk.
- [x] Implement decomposed reward terms.
- [x] Implement reset, step, done, and info contracts.
- [x] Document the exact HouseExpo extension boundary.

## DDPG

- [ ] Implement actor network with final `tanh`.
- [ ] Implement critic network over concatenated state and action.
- [ ] Create target actor and target critic from online weights.
- [ ] Implement replay buffer and random mini-batches.
- [ ] Implement Gaussian exploration noise and action clipping.
- [ ] Implement terminal-masked Bellman target.
- [ ] Implement critic MSE update.
- [ ] Implement actor `-Q` update.
- [ ] Implement and call soft target update with `tau`.
- [ ] Implement CPU checkpoint save/load.
- [x] Reserve future hyperparameters in versioned configuration without implementing DDPG logic.
- [x] Use the exact configuration names `actor_lr`, `critic_lr`, `gamma`, `tau`, `noise_sigma`, `batch_size`, and `replay_buffer_size`.

## Training, SDK, and CLI

- [x] Implement deterministic seed utility for the simulator and random-policy demo.
- [ ] Implement metrics collector and JSON schema.
- [ ] Implement warm-up and episode training loop.
- [ ] Implement noise-free evaluation rollout.
- [ ] Expose training, evaluation, and plotting only through `VacuumSDK`.
- [ ] Add `train`, `evaluate`, and `plot` CLI commands.
- [x] Add clear simulator configuration, action, map, and missing-file errors.

## Visualization and results

- [x] Generate and test `results/trajectories/random_policy.png` from the simulator CLI.
- [ ] Generate `results/plots/learning_curve.png`.
- [ ] Generate `results/plots/critic_loss.png`.
- [ ] Generate `results/trajectories/evaluation_trajectory.png`.
- [ ] Save `results/metrics/training_metrics.json`.
- [ ] Verify plots show correct labels, map geometry, and trajectory markers.
- [ ] Verify reward axes are episode and cumulative reward.
- [ ] Verify critic-loss axes are optimizer update and critic MSE.
- [ ] Record run command, seed, resolved configuration, and duration.

## Tests

- [ ] Test reset/step and repeatable seed behavior.
- [x] Test environment action clipping.
- [x] Test reward for new versus revisited cells.
- [x] Test boundary and obstacle collisions.
- [x] Test valid and invalid map loading.
- [ ] Test sensor and state ranges.
- [ ] Test replay capacity and sample shapes.
- [ ] Test actor range and output shape.
- [ ] Test critic scalar output shape.
- [ ] Test Gaussian noise and final clipping.
- [ ] Test exact soft target interpolation.
- [ ] Test Bellman terminal masking.
- [ ] Test basic training loop and artifact creation.
- [ ] Reach configured coverage target.

## Final report and audit

- [ ] Replace summary-report placeholders with exact code locations.
- [ ] Replace planned hyperparameters with the resolved run values.
- [ ] Add actual result paths and observations.
- [ ] Answer all three conceptual DDPG questions.
- [x] Run `uv sync --extra dev` from the locked environment.
- [x] Run `uv run pytest` successfully for the scaffold/simulator milestone.
- [x] Run `uv run ruff check .` successfully for the scaffold/simulator milestone.
- [ ] Confirm no forbidden environment framework appears in dependencies/imports.
- [ ] Confirm `requirements.txt` is absent and `uv.lock` is committed.
- [ ] Confirm meaningful Git history exists for the submitted repository.
- [ ] Confirm docs, code, configuration, and metrics agree.
- [ ] Confirm no secrets or generated caches are committed.
- [ ] Mark release `1.00` complete only after every mandatory audit item passes.
