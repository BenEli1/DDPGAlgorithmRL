# GUI Guide

The project includes a local, Python-only Tkinter interface for the implemented random-policy simulator demo. It is a thin consumer of `VacuumSDK`: the GUI does not implement environment transitions, reward, collision, coverage, map loading, report serialization, or Matplotlib artifact logic.

## Launch

From the repository root:

```bash
uv sync --extra dev
uv run robot-vacuum gui
```

Tkinter ships with the standard Windows and macOS Python installers. Minimal Linux installations may require the operating system's `python3-tk` package; this is not a PyPI or uv dependency.

## Inputs

- **Seed:** controls the repeatable random-action sequence.
- **Max steps:** limits the interactive episode and is capped by simulator configuration.
- **Map file:** defaults to `data/sample_maps/simple_house.json` and accepts another valid native map JSON path.
- **Delay:** controls milliseconds between scheduled Run episode steps.

Changing an input takes effect on the next **Reset** or when **Run episode** resets a completed session.

## Controls

- **Reset:** creates a fresh SDK session using current inputs.
- **Step random action:** performs exactly one random continuous action.
- **Run episode:** schedules steps without blocking the Tk event loop.
- **Pause / stop:** stops future scheduled steps; the current session remains visible.
- **Save screenshot:** writes `results/screenshots/gui_demo.png`.
- **Generate report:** writes the standard trajectory, JSON metrics, and Markdown report bundle for the current partial or completed session.

## Display and status

The canvas shows map boundaries, rectangular obstacles, cleaned cells, the trajectory trail, collision attempts, current robot position, and robot heading. The status panel shows current step, total reward, collision count, coverage percentage, current action, state-vector length, and the most recently saved artifact path.

## Screenshot behavior

Tkinter window capture is platform-dependent. The **Save screenshot** control therefore uses the SDK's Matplotlib renderer as a portable fallback and saves the current map view to:

```text
results/screenshots/gui_demo.png
```

This image contains simulator visual evidence but not the surrounding buttons or operating-system window frame. It is generated and ignored by Git.

![GUI map-view screenshot](../results/screenshots/gui_demo.png)

## Architecture

```text
Tkinter controls/canvas
        |
        v
VacuumSDK -> DemoSession -> custom simulator
        |
        +-> report writers
        `-> Matplotlib screenshot/trajectory renderer
```

`DemoSnapshot` is immutable display data. GUI-independent coordinate transforms and status formatting live in `gui/view_model.py` and are covered by unit tests.

## Limitations

- Actions are random; the GUI does not represent a trained DDPG policy.
- The current map schema supports rectangular bounds and obstacles.
- Pause is cooperative between scheduled steps; it does not interrupt a step already executing.
- DDPG training/evaluation is available through the CLI; the GUI intentionally remains a simulator inspection tool rather than a training dashboard.
