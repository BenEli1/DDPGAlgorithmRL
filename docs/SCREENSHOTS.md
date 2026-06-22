# Screenshot and Visual Evidence Guide

Curated, reviewed evidence is committed under `assets/evidence/`; reproducible runtime
outputs are generated under the Git-ignored `results/` tree.

## Committed GUI evidence

- `assets/evidence/gui_map_view.png` isolates the simulator map, trajectory, pose, heading,
  obstacles, and cleaned cells.
- `assets/evidence/gui_full_window.png` shows the complete application layout: inputs, six
  controls, map, and status panel. The committed version is application-rendered from an
  immutable SDK snapshot, not an operating-system screenshot.

Automatic Windows screen capture was attempted during the final audit but the desktop
session returned `OSError: screen grab failed`. The portable artifact avoids a fragile or
privacy-sensitive dependency while still proving the GUI layout.

## Manual full-window replacement workflow

1. Run `uv run robot-vacuum gui`.
2. Select **Step random action** a few times or run a full episode.
3. Select **Save screenshot** to regenerate `results/screenshots/gui_demo.png`.
4. Use the operating system's screenshot tool to capture only the Tkinter window, including
   its controls and status panel. Exclude the desktop, taskbar, notifications, usernames,
   and unrelated windows.
5. Save the reviewed crop as `assets/evidence/gui_full_window.png`, replacing the portable
   version.
6. Open the image, verify that all text is legible and no personal content is visible, then
   commit it.

## Runtime artifact regeneration

```bash
uv run robot-vacuum demo --max-steps 150 --seed 42
uv run robot-vacuum record-demo --max-steps 150 --seed 42 --frame-stride 3
uv run robot-vacuum gui
uv run robot-vacuum train --config config/smoke_training.json
uv run robot-vacuum evaluate --checkpoint results/checkpoints/best_actor.pt
```

The random-policy trajectory and animation prove simulator integration. The GUI images prove
map rendering plus controls/status layout. The learning/loss plots, metrics, checkpoint, and
evaluation trajectory prove that the DDPG software path executes. A two-episode smoke run is
not evidence of convergence or useful learned performance.
