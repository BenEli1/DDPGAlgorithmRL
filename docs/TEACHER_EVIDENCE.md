# Teacher Evidence Pack

This page is the fastest review path through the submission. The images below are committed snapshots produced by the repository's own commands. Runtime outputs remain reproducible under `results/`; curated copies live under `assets/evidence/` so they render on GitHub.

## 1. Demo evidence

### Random-policy simulator demonstration

Command: `uv run robot-vacuum demo --max-steps 150 --seed 42`

![Random-policy trajectory](../assets/evidence/random_policy_trajectory.png)

The plot shows the map boundary, obstacles, cleaned cells, ordered robot path, start/final pose, final heading, and collision attempts. This is simulator evidence, not DDPG evidence.

### GUI map-view export

Command: `uv run robot-vacuum gui`, then select **Save screenshot**.

![GUI map view](../assets/evidence/gui_map_view.png)

This is the GUI's application-generated map view. It intentionally excludes desktop/window chrome so the evidence is portable and cannot capture unrelated screen content. The GUI controls, status fields, and workflow are documented in [GUI_GUIDE.md](GUI_GUIDE.md).

### DDPG smoke evidence

Command: `uv run robot-vacuum train --config config/smoke_training.json`

![Smoke learning curve](../assets/evidence/smoke_learning_curve.png)

![Smoke critic loss](../assets/evidence/smoke_critic_loss.png)

Evaluation command: `uv run robot-vacuum evaluate --checkpoint results/checkpoints/best_actor.pt`

![Smoke evaluation trajectory](../assets/evidence/smoke_evaluation_trajectory.png)

The two-episode run produced 25 optimizer updates. Evaluation reached only 0.89% coverage in 500 steps, so it proves integration but does not support a convergence claim. The exact recorded arrays and resolved configuration are in [`smoke_training_metrics.json`](../assets/evidence/smoke_training_metrics.json).

## 2. Assessment-area traceability

| Assessment area | Repository evidence |
|---|---|
| Project planning | [PRD](PRD.md), [implementation plan](PLAN.md), [TODO](TODO.md), simulator and DDPG PRDs |
| Code documentation | Typed modules, design-focused docstrings, [README](../README.md), demo/GUI/results guides |
| Testing and quality | 19 tests, 88.08% coverage, Ruff, and [automated GitHub workflow](../.github/workflows/quality.yml) |
| UI and user experience | SDK-backed Tkinter GUI, committed map-view image, [GUI guide](GUI_GUIDE.md) |
| Configuration and security | `pyproject.toml`, locked `uv.lock`, versioned JSON configuration, `.env-example`, and the [privacy/security policy](PRIVACY_SECURITY.md) |
| Research and analysis | [Experiment log](EXPERIMENTS.md) with hypotheses, observations, conclusions, and next experiments |
| Version and AI workflow | Meaningful Git commits plus [AI prompt and decision log](PROMPT_LOG.md) |
| Cost awareness | [Resource and cost analysis](RESOURCE_AND_COST.md) with memory/runtime scaling equations |
| Extensibility | SDK facade, map-loader protocol, isolated simulator/DDPG/GUI packages, [extension points](#3-extensibility) |
| Quality standards | Locked dependencies, CI, coverage threshold, Ruff rules, tests, artifact schema, and [quality policy](QUALITY_STANDARDS.md) |

## 3. Extensibility

The main extension seams are explicit:

- Add map formats by implementing `MapLoader`; simulation logic does not change.
- Add obstacle geometry behind geometry/map abstractions.
- Change neural-network sizes and learning hyperparameters through JSON configuration.
- Add agents or evaluation strategies against the environment's stable 13-state/two-action contract.
- Add GUI views over immutable `DemoSnapshot` values without moving reward, collision, or dynamics logic into Tkinter.
- Add new output formats from recorded metric documents without recomputing episode outcomes.

## 4. Honest submission boundary

- Full DDPG mechanics are implemented and smoke tested.
- The recorded smoke run is not convergence evidence.
- The 200-episode configuration has not been presented as a completed experiment.
- Full HouseExpo polygon parsing is an extension point, not a current claim.
- Curated evidence is committed; canonical runtime results remain locally regenerated and ignored.
