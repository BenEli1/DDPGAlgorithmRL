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

- [ ] Initialize Git if the workspace remains uninitialized; preserve any existing history if repository context changes.
- [ ] Create `pyproject.toml` with Python and dependency metadata.
- [ ] Configure Ruff, pytest, and coverage.
- [ ] Create and commit `uv.lock`.
- [ ] Add `.gitignore` and `.env-example`.
- [ ] Create package, test, config, data, assets, and results directories.
- [ ] Add version `1.00` and configuration schema versions.
- [ ] Add `config/smoke_training.json` with two episodes, 20 steps, batch size 16, warm-up 16, and seed 42.
- [ ] Add CLI entry point and SDK facade skeleton.
- [ ] Verify package import and CLI help through `uv run`.

## Simulator

- [ ] Define map and geometry models.
- [ ] Add `MapLoader` protocol and native JSON loader.
- [ ] Add and validate `data/sample_maps/simple_room.json`.
- [ ] Implement circle/segment and circle/rectangle collision checks.
- [ ] Reject the full proposed pose on collision and verify pose remains unchanged.
- [ ] Test swept-path collision so a fast step cannot tunnel through an obstacle.
- [ ] Implement ray distance intersections.
- [ ] Implement robot pose and continuous kinematics.
- [ ] Clip normalized actions to `[-1, 1]`.
- [ ] Implement seven normalized distance sensors.
- [ ] Implement the documented 13-value default state.
- [ ] Implement free-space coverage grid and cleaning disk.
- [ ] Implement decomposed reward terms.
- [ ] Implement reset, step, done, and info contracts.
- [ ] Document the exact HouseExpo extension boundary.

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
- [ ] Keep hyperparameters in versioned configuration.

## Training, SDK, and CLI

- [ ] Implement deterministic seed utility.
- [ ] Implement metrics collector and JSON schema.
- [ ] Implement warm-up and episode training loop.
- [ ] Implement noise-free evaluation rollout.
- [ ] Expose training, evaluation, and plotting only through `VacuumSDK`.
- [ ] Add `train`, `evaluate`, and `plot` CLI commands.
- [ ] Add clear validation and missing-file errors.

## Visualization and results

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
- [ ] Test environment action clipping.
- [ ] Test reward for new versus revisited cells.
- [ ] Test boundary and obstacle collisions.
- [ ] Test valid and invalid map loading.
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
- [ ] Run `uv sync --extra dev` from the locked environment.
- [ ] Run `uv run pytest` successfully.
- [ ] Run `uv run ruff check .` successfully.
- [ ] Confirm no forbidden environment framework appears in dependencies/imports.
- [ ] Confirm `requirements.txt` is absent and `uv.lock` is committed.
- [ ] Confirm meaningful Git history exists for the submitted repository.
- [ ] Confirm docs, code, configuration, and metrics agree.
- [ ] Confirm no secrets or generated caches are committed.
- [ ] Mark release `1.00` complete only after every mandatory audit item passes.
