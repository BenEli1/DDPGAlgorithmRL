# Demo Guide

This guide describes only functionality that exists at revision `bc88d59`. The current demo runs the custom simulator with a seeded random continuous policy. It is not DDPG training and is not evidence of convergence.

## Setup

From the repository root:

```bash
uv sync --extra dev
```

Python 3.11 or newer and `uv` are required. No environment variables or secrets are needed.

## Run the simulator demo

```bash
uv run robot-vacuum demo --max-steps 150 --seed 42
```

The CLI prints:

- executed step count;
- cumulative episode reward;
- final cleaning coverage ratio;
- collision count;
- trajectory, metrics, and report output paths.

The default outputs are:

```text
results/trajectories/random_policy.png
results/metrics/random_policy_metrics.json
results/reports/random_policy_report.md
```

The command delegates to `VacuumSDK.run_random_episode`. The SDK loads configuration and map data, runs the environment, and invokes the visualization module; the CLI does not duplicate simulator logic.

## Useful options

```bash
uv run robot-vacuum --help
uv run robot-vacuum make-demo --max-steps 150 --seed 42
uv run robot-vacuum demo --config config/default_simulator.json --seed 7 --max-steps 250
```

`--max-steps` is capped by the `max_steps` value in the simulator configuration. `--output` may point elsewhere, but submission demos should stay under `results/trajectories/`.

## What the trajectory proves

The PNG shows:

- sample-map bounds and rectangular obstacles;
- the continuous sequence of committed robot positions;
- distinct start and final markers;
- successful headless Matplotlib output.

It proves simulator and visualization integration. Because actions are random, short runs may move very little or collide repeatedly. It does not prove that a policy learned to clean or navigate.

## Current limitations

- The trajectory PNG is generated locally and ignored by Git, so a clean clone must run the command to create it.
- The GUI screenshot is a portable Matplotlib map-view fallback, not a capture of window chrome.
- No `train`, `evaluate`, or `plot` subcommand exists.
- No DDPG checkpoint or trained-policy result exists.

## Current artifact flow

The implemented demo flow is:

1. Run `uv run robot-vacuum demo --max-steps 150 --seed 42` or the equivalent `make-demo` alias.
2. Inspect the trajectory PNG, JSON metrics, and Markdown report under `results/`.
3. After a GUI exists, capture it at `results/screenshots/gui_demo.png`.
4. After DDPG exists, run smoke training for integration evidence and a separately documented evaluation for learned-policy evidence.

The planned GUI must call the SDK and display `DemoResult`; it must not reproduce kinematics, collision, coverage, reward, or plotting logic.

## Verification commands

```bash
uv run ruff check .
uv run pytest
uv run pytest --cov=robot_vacuum_ddpg --cov-report=term-missing
```

At the DDPG smoke audit these pass with 19 tests and 88.08% coverage under the documented coverage policy.

## Troubleshooting

- `Configuration file does not exist`: run from the repository root or pass a valid `--config` path.
- Invalid map/configuration error: restore the committed JSON files or validate edited numeric fields and schema version.
- No PNG appears: read the printed `trajectory=` path and verify its parent directory is writable.
- Episode already done: SDK users must call `reset` before stepping a completed environment; normal CLI use handles this lifecycle.
