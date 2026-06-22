# Demo Guide

This guide describes the current `main` branch. The demo runs the custom simulator with a seeded random continuous policy. It is not DDPG training and is not evidence of convergence.

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

For an animated README-ready walkthrough generated only from simulator state:

```bash
uv run robot-vacuum record-demo --max-steps 150 --seed 42 --frame-stride 3
```

The GIF is written to `results/animations/random_policy_demo.gif`. It is a random-policy simulator demonstration, not evidence of DDPG convergence.

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
- The GUI screenshot is a portable Matplotlib reproduction of controls, map, and status from
  SDK data, not a capture of the desktop or window chrome.
- DDPG training and deterministic evaluation are separate CLI workflows; the seeded random
  demo must not be presented as learned-policy evidence.
- The committed DDPG record is only a two-episode smoke run and does not prove convergence.

## Current artifact flow

The implemented demo flow is:

1. Run `uv run robot-vacuum demo --max-steps 150 --seed 42` or the equivalent `make-demo` alias.
2. Inspect the trajectory PNG, JSON metrics, and Markdown report under `results/`.
3. Run the GUI and select **Save screenshot** to create `results/screenshots/gui_demo.png`.
4. Run smoke training and deterministic evaluation using the commands in `RESULTS_GUIDE.md`;
   interpret them as integration evidence only.

The implemented GUI calls the SDK and displays immutable `DemoSnapshot` values; it does not
reproduce kinematics, collision, coverage, reward, or reporting logic.

## Verification commands

```bash
uv run ruff check .
uv run pytest
uv run pytest --cov=robot_vacuum_ddpg --cov-report=term-missing
```

At the GUI-preview audit these pass with 21 tests and 89.17% coverage under the documented coverage policy.

## Troubleshooting

- `Configuration file does not exist`: run from the repository root or pass a valid `--config` path.
- Invalid map/configuration error: restore the committed JSON files or validate edited numeric fields and schema version.
- No PNG appears: read the printed `trajectory=` path and verify its parent directory is writable.
- Episode already done: SDK users must call `reset` before stepping a completed environment; normal CLI use handles this lifecycle.
