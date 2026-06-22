# Coding Style Report

**Date:** 2026-06-21  
**Scope:** Python source, tests, packaging, configuration, generated evidence, CLI/GUI boundaries, and documentation consistency.

## Outcome

The implemented simulator/demo scope passes the repository's Ruff, pytest, and coverage gates. The style pass made two structural extractions instead of suppressing the size issue:

- `simulator/coverage.py` now owns coverage-cell construction and first-visit bookkeeping.
- `simulator/observation.py` now owns normalized state-vector assembly.

This leaves `VacuumEnvironment` focused on episode lifecycle and composition. DDPG configuration, evaluation, metrics, and training are also split by responsibility; the largest implementation file is the 175-line SDK facade.

## Packaging and dependency discipline

- `pyproject.toml` is the only dependency and tool-configuration source.
- `uv.lock` is present and tracked.
- No `requirements.txt`, Pipfile, Poetry lock, or alternate dependency manifest exists.
- Runtime dependencies remain NumPy and Matplotlib; dev tools remain pytest, pytest-cov, and Ruff.
- Tkinter comes from the Python standard library/OS Python distribution and is not falsely declared as a PyPI dependency.
- No forbidden environment framework is imported or declared.

## Configuration and hardcoded values

Simulator time step, radii, speed limits, sensor range/angles, coverage resolution, termination, and reward weights live in `config/default_simulator.json`. DDPG consumes validated hyperparameters from the versioned smoke/default training JSON files.

Remaining literals fall into these legitimate categories:

- mathematical/domain invariants such as action dimension 2, clipping bounds, angle wrapping, and float tolerances;
- serialization schema version;
- CLI exit codes and formatting precision;
- GUI layout dimensions, colors, padding, marker sizes, and default presentation delay;
- documented demo defaults such as seed 42 and requested step count.

No second hardcoded copy of sensor-angle defaults remains in Python.

## Naming, typing, and documentation

- Domain objects use descriptive names such as `CoverageGrid`, `DemoSession`, `DemoSnapshot`, `MovementResult`, and `RewardBreakdown`.
- Public functions and methods use return and parameter type hints.
- Frozen/slotted dataclasses protect immutable value contracts where appropriate.
- Docstrings explain boundaries and rationale, including why coverage is discretized separately, why snapshots are immutable, why reports share a metrics record, and why screenshot rendering uses a portable fallback.
- Comments are sparse and reserved for exceptional import-order/backend constraints rather than narrating obvious code.

## Duplication and dependency direction

| Concern | Owner | Consumers |
|---|---|---|
| Geometry/collision/kinematics | `simulator/` | Environment only |
| Coverage bookkeeping | `CoverageGrid` | Environment |
| Observation normalization | `build_observation` | Environment |
| Random demo lifecycle | `DemoSession` | SDK batch demo and GUI |
| Artifact metrics | SDK metrics dictionary | JSON and Markdown writers |
| Trajectory/map image | Visualization module | SDK demo and screenshot fallback |
| User interaction | CLI/Tkinter GUI | SDK only |

The report writer does not recalculate rewards, collisions, coverage, or positions. It formats the exact dictionary written to JSON.

## Test policy

Verified:

```text
21 tests passed
89.17% aggregate coverage
0 Ruff violations
```

The coverage configuration excludes `main.py` and Tkinter/canvas wrappers because they contain parsing or display wiring rather than domain logic. GUI-independent coordinate/status conversion is tested, SDK/report integration is tested, and Tk window initialization was manually smoke checked.

## Generated-file policy

- Caches, virtual environments, coverage files, builds, and all result categories are ignored.
- `.gitkeep` files preserve the intended result directory structure.
- Runtime artifacts are generated locally and listed with commands in `ARTIFACT_INDEX.md`.
- Documentation never labels random-policy evidence as trained-policy or convergence evidence.

## Items intentionally not "fixed"

- DDPG packages now contain the verified actor, critic, replay, noise, targets, updates, training, evaluation, and artifact pipeline.
- Smoke results remain integration evidence only; no unsupported convergence claim is made.
- The GUI preview reproduces application controls, map, and status from SDK data without
  pretending to capture cross-platform window chrome.
- Full HouseExpo support remains out of scope until a real adapter and polygon tests exist.
