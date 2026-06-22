# Implementation Plan

## Planning principles

- Follow the source priority in `PRD.md`.
- Finish and review documentation before implementation.
- Build the smallest vertical slice that exposes every required DDPG mechanism.
- Keep smoke-test correctness independent from claims of learned performance.
- Update `TODO.md`, `PROMPT_LOG.md`, and `SUMMARY_REPORT.md` as evidence is produced.
- For each public behavior, follow a red-green-refactor loop: add the smallest failing test, implement only enough to pass, then improve structure with the suite green.

## Phase 0 - Documentation (complete)

### Deliverables

- Root README.
- Product PRD, implementation plan, task tracker, DDPG PRD, simulator PRD, summary report skeleton, and prompt log.
- Proposed repository structure, formal state/action contracts, default hyperparameters, and measurable acceptance criteria.

### Strict grader review

The first draft is reviewed against the assignment for:

- explicit continuous action range and meaning;
- custom simulator prohibition and HouseExpo limitation;
- state, reward, termination, and collision semantics;
- every DDPG equation and stability mechanism;
- all required visual outputs and paths;
- exact future code-location reporting;
- uv, pytest, Ruff, SDK, configuration, and reproducibility requirements;
- honest separation of planned versus completed work.

### Exit gate

All eight required Markdown files exist, contain no unqualified implementation claims, and jointly cover AC-1 through AC-16.

## Phase 1 - Project scaffold (complete and committed)

### Work

1. Confirm the initialized Git repository, `origin` remote, active branch, and intended documentation-only change scope.
2. Add `pyproject.toml` with runtime and dev dependency groups, CLI entry point, Ruff, pytest, and coverage configuration.
3. Generate and commit `uv.lock` through `uv lock` or `uv sync`.
4. Add `.gitignore`, `.env-example`, package folders, and `__init__.py` files.
5. Add versioned simulator, default-training, and tiny smoke-training JSON configuration.
6. Add path, config validation, seed, and version utilities.
7. Add empty result directories using `.gitkeep` only where needed.

### Verification

```bash
uv sync --extra dev
uv run python -c "import robot_vacuum_ddpg"
uv run ruff check .
```

### Exit gate

The package imports, configuration loads, CLI help runs, and no domain placeholder falsely reports success.

## Phase 2 - Custom simulator (complete)

### Work order

1. Write geometry/model tests, then define immutable pose, segment, rectangle, and map data models.
2. Write valid/invalid map tests, then implement sample JSON validation and `MapLoader` protocol.
3. Write contact, swept-path, and ray-distance tests, then implement collision checks and ray intersections.
4. Write clipping and known-motion tests, then implement robot kinematics.
5. Write sensor shape/range tests, then implement configurable rays and observations.
6. Write new/revisited-cell tests, then implement coverage and first-visit cleaning.
7. Write component-level reward tests, then implement decomposed reward calculation.
8. Write reset/step integration tests, then compose `VacuumEnvironment`.

### Exit gate

Simulator unit and integration tests pass without importing PyTorch or any forbidden environment library. A scripted action sequence yields finite observations, collision evidence, and increasing coverage.

## Phase 2.5 - Demo evidence and local GUI (complete)

### Implemented work

1. Added explicit `demo` and `make-demo` CLI commands that generate trajectory, JSON metrics, and Markdown reports.
2. Added an SDK-owned `DemoSession` and immutable `DemoSnapshot` for incremental consumers.
3. Added a Tkinter GUI with reset, random step, scheduled run, pause, screenshot, and report controls.
4. Added GUI inputs for seed, maximum steps, map path, and display delay.
5. Added canvas rendering for boundaries, obstacles, cleaned cells, collision attempts, trajectory, robot position, and heading.
6. Added a portable Matplotlib full-layout GUI preview at `results/screenshots/gui_demo.png`.
7. Added GUI-independent coordinate/status tests; no display server is required by the test suite.

### Architecture gate

The GUI imports the SDK contract and shared path constants only. Simulator construction, stepping, rewards, collision, coverage, report serialization, and Matplotlib artifact rendering remain behind SDK methods.

## Phase 3 - DDPG core (implemented and smoke verified)

### Work order

1. Write actor bounds tests, then implement the actor MLP with a visibly final `torch.tanh` or `nn.Tanh`.
2. Write critic input/shape tests, then implement the critic MLP over concatenated state and action.
3. Write replay capacity/sample tests, then implement the fixed-capacity replay buffer with injected RNG.
4. Write sigma/clipping tests, then implement Gaussian noise and its action-selection integration.
5. Write exact interpolation tests, then implement the soft-update helper.
6. Write target-copy and optimizer tests, then compose online/target networks and optimizers in `DDPGAgent`.
7. Write terminal-mask and synthetic-update tests, then implement Bellman target, critic MSE, actor negative-Q loss, and target updates.
8. Write a round-trip test, then implement checkpoint save/load with model and optimizer state plus metadata.

### Exit gate

Shape, bounds, replay, noise, equation, gradient, and soft-update tests pass. One synthetic update changes online parameters and leaves target parameters as the exact soft interpolation.

## Phase 4 - Training, SDK, and CLI

### Work order

1. Implement structured metrics collection and JSON serialization.
2. Implement trainer warm-up, episode loop, updates, evaluation, and checkpoint selection.
3. Implement `VacuumSDK.train`, `.evaluate`, and `.plot_results` as the only external business interface.
4. Implement CLI subcommands delegating to the SDK.
5. Add a two-episode deterministic smoke integration test using tiny limits.

### Exit gate

The smoke command uses two episodes, 20 steps per episode, batch size 16, warm-up 16, and seed 42. It completes on CPU, performs at least one learning update, saves metrics, and returns a useful nonzero exit code on invalid input. It is an integration test, not a convergence experiment.

## Phase 5 - Visualization and evidence

### Work

1. Plot per-episode cumulative reward with an optional moving average.
2. Plot critic loss against optimizer update index.
3. Plot map geometry, obstacles, trajectory, start, finish, and optionally cleaned cells.
4. Run a documented baseline training configuration.
5. Save resolved configuration, metrics, plots, and an evaluation trajectory.

### Exit gate

All required files are non-empty, readable in a headless environment, and generated from the metrics file rather than hand-authored data. Axis labels are exactly tied to the assignment semantics: episode versus cumulative reward, and update index versus critic MSE.

## Phase 6 - Tests and quality hardening

### Required tests

- Reset/step contract and deterministic seed.
- Action clipping and actor bounds.
- Kinematics and observation normalization.
- Reward for new versus revisited cells.
- Boundary and obstacle collision.
- Valid and malformed map loading.
- Replay capacity and random batch shapes.
- Actor and critic shapes.
- Gaussian noise and clipping.
- Soft target update arithmetic.
- Critic terminal mask and actor loss direction where practical.
- Training smoke, result serialization, and plot creation.

### Commands

```bash
uv run ruff check .
uv run pytest
uv run pytest --cov=robot_vacuum_ddpg --cov-report=term-missing
```

### Exit gate

Ruff has zero violations, tests pass, coverage meets the configured gate, and no implementation file exceeds the size target without a recorded reason.

## Phase 7 - Final report and audit

1. Replace every `TBD after implementation` marker in `SUMMARY_REPORT.md` with verified evidence or an explicit limitation.
2. Add exact relative paths and line numbers for assignment-critical DDPG mechanisms.
3. Record actual hyperparameters, run command, seed, duration, and result paths.
   The report must use the canonical names `actor_lr`, `critic_lr`, `gamma`, `tau`, `noise_sigma`, `batch_size`, and `replay_buffer_size`.
4. Answer why DDPG fits, what removing Gaussian noise does, and how soft updates stabilize training.
5. Re-run README commands from a clean `uv sync` environment.
6. Search dependencies and imports for forbidden frameworks.
7. Compare configuration defaults, docs, metrics, and implemented state/action dimensions.
8. Update `TODO.md` checkboxes only from test or artifact evidence.

### Final audit checklist

- [ ] README and all required docs are complete.
- [ ] `pyproject.toml` and committed `uv.lock` are authoritative.
- [ ] CLI delegates to SDK; no duplicated training logic.
- [ ] Simulator is custom and continuous.
- [ ] DDPG equations match the lecture specification.
- [ ] All required tests pass.
- [ ] Reward, critic-loss, and trajectory plots exist.
- [ ] Metrics JSON records the actual run.
- [ ] Summary report points to exact code.
- [ ] HouseExpo limitation is stated accurately.
- [ ] No secret or forbidden dependency is present.

## Definition of done

The project is done when the final audit passes from a clean checkout using only documented `uv` commands. A successful smoke test proves integration; any convergence claim additionally requires a longer recorded run and visible supporting plots.
