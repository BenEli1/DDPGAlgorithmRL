# Final Submission Audit

**Audit date:** 2026-06-21  
**Baseline revision:** `bc88d59` (`origin/main`) plus current working-tree demo, GUI, reporting, and style changes  
**Verdict:** The custom simulator, SDK, local GUI, from-scratch DDPG pipeline, smoke evidence, documentation, packaging, and quality gates are implemented. Smoke training proves integration only; convergence remains unestablished.

## Verified commands

```bash
uv sync --extra dev
uv run robot-vacuum demo --max-steps 150 --seed 42
uv run robot-vacuum train --config config/smoke_training.json
uv run robot-vacuum evaluate --checkpoint results/checkpoints/best_actor.pt
uv run pytest
uv run pytest --cov=robot_vacuum_ddpg --cov-report=term-missing
uv run ruff check .
```

Observed results:

- uv resolved 50 packages and installed the locked PyTorch runtime successfully.
- Ruff passed with zero violations.
- Pytest passed all 20 tests.
- Coverage passed the configured 85% gate at 88.48%.
- The seeded demo generated a PNG, JSON metrics, and Markdown report.
- A Tkinter create/update/destroy smoke check initialized the GUI successfully.
- The GUI screenshot fallback generated a readable PNG with map, path, cleaned cells, robot position, and heading.
- Smoke training generated metrics, reward/loss plots, and a loadable checkpoint; deterministic evaluation generated a trajectory.

On systems with an institutional certificate chain, use `--system-certs` for `uv sync` or set `UV_SYSTEM_CERTS=true` before `uv run` if an editable rebuild needs registry access.

## Submission checklist

| Check | Result | Evidence |
|---|---|---|
| `pyproject.toml` is authoritative | Pass | Build, runtime/dev dependencies, scripts, tests, coverage, and Ruff live in one file |
| `uv.lock` exists and is tracked | Pass | Lock format revision 3; no second dependency source |
| No `requirements.txt`/Pipenv/Poetry source | Pass | Repository scan returned none |
| No forbidden simulator framework | Pass | No Gymnasium, Gazebo, Stable-Baselines, or RLlib dependency/import |
| No secrets | Pass | No credential pattern found; `.env-example` says none are required |
| Configuration separated from code | Pass | Simulator/reward and training hyperparameters are versioned in separate JSON files |
| Generated artifacts controlled | Pass | Runtime outputs are under `results/`, ignored by category, and documented in `ARTIFACT_INDEX.md` |
| Reasonable module sizes | Pass | Learning/domain modules are focused; largest SDK facade is 175 nonblank, non-comment lines |
| Clear names and type hints | Pass | Public contracts use domain names and typed dataclasses/snapshots |
| Useful docstrings | Pass | Boundary modules explain design intent: discretization only for coverage, immutable GUI snapshots, shared metrics source, and SDK isolation |
| Duplicate business logic removed | Pass | CLI batch demos and GUI sessions share `DemoSession` and SDK artifact methods |
| CLI/GUI use SDK | Pass | CLI calls `VacuumSDK`; GUI uses `VacuumSDK`, `DemoSession`, and immutable `DemoSnapshot` |
| Simulator independent of GUI | Pass | `simulator/` has no Tkinter, GUI, SDK, reporting, or Matplotlib dependency |
| Reports preserve outcomes | Pass | JSON and Markdown writers consume the same SDK metrics record; the report only formats values |
| README commands valid | Pass | `demo`, `make-demo`, `gui`, `train`, and `evaluate` match parser choices |
| Documentation matches code | Pass | DDPG implementation and smoke-only evidence are distinguished from convergence |

## Architecture result

```text
CLI ---------+
             v
GUI -----> VacuumSDK -----> DemoSession -----> custom simulator
             |                                  |
             +----> reports/plots <-------------+
```

- `CoverageGrid` owns discretized cleaning bookkeeping.
- `build_observation` owns state normalization and validation.
- `VacuumEnvironment` owns episode lifecycle and composition.
- `DemoSession` owns incremental random-policy run state.
- The GUI renders immutable snapshots and forwards actions; it cannot mutate simulator internals.

## Artifact result

Generated locally and visually inspected:

- `results/trajectories/random_policy.png`
- `results/metrics/random_policy_metrics.json`
- `results/reports/random_policy_report.md`
- `results/screenshots/gui_demo.png`
- `results/plots/learning_curve.png`
- `results/plots/critic_loss.png`
- `results/metrics/training_metrics.json`
- `results/checkpoints/best_actor.pt`
- `results/trajectories/evaluation_trajectory.png`

These are intentionally ignored, not committed evidence. A clean clone regenerates them with the commands in `ARTIFACT_INDEX.md`.

## Exercise 05 status

| Requirement | Status |
|---|---|
| Custom project-owned simulator | Implemented |
| Continuous two-value action clipped to `[-1, 1]` | Implemented |
| Documented 13-value default state | Implemented |
| Random-policy trajectory/report evidence | Implemented |
| Local Python GUI | Implemented |
| Actor, critic, target networks, replay, noise, soft updates | Implemented |
| DDPG training/evaluation | Implemented; smoke verified |
| Learning curve and critic-loss graph | Implemented; smoke evidence only |
| Checkpoint evaluation trajectory | Implemented; no convergence claim |
| Full HouseExpo adapter | Pending; only the native sample format and loader boundary exist |

## Remaining honest limitations

- Random-policy artifacts prove simulator integration only.
- The DDPG record is a two-episode smoke run; its 0.89% evaluation coverage does not support convergence or useful-policy claims.
- The simulator uses simplified deterministic kinematics, perfect sensors, rectangular obstacles, and grid-approximated coverage.
- The native JSON map is not a HouseExpo record; full HouseExpo polygon support is not claimed.
- The GUI screenshot is a portable Matplotlib rendering of the current map view, not a capture of Tkinter window chrome.
- GUI wrapper/rendering files are excluded from aggregate coverage; GUI-independent conversions are unit tested and window initialization is smoke checked manually.
- Current working-tree changes still require an intentional review/commit before submission.
- Personal submission files and source course documents remain local and are excluded by generic PDF and office-document ignore rules.

## Final sign-off commands

```bash
uv sync --extra dev
uv run robot-vacuum demo --max-steps 150 --seed 42
uv run robot-vacuum gui
uv run robot-vacuum train --config config/smoke_training.json
uv run robot-vacuum evaluate --checkpoint results/checkpoints/best_actor.pt
uv run pytest
uv run pytest --cov=robot_vacuum_ddpg --cov-report=term-missing
uv run ruff check .
```
