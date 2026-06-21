# Artifact Index

Generated runtime artifacts live under `results/`. They are intentionally ignored by Git; only `.gitkeep` directory markers are committed. Run the listed commands after a clean checkout.

## Implemented generated artifacts

| Type | Artifact | Exact generation command/action | Repository status |
|---|---|---|---|
| Image | `results/trajectories/random_policy.png` | `uv run robot-vacuum demo --max-steps 150 --seed 42` | Generated locally; ignored |
| Metrics | `results/metrics/random_policy_metrics.json` | `uv run robot-vacuum demo --max-steps 150 --seed 42` | Generated locally; ignored |
| Report | `results/reports/random_policy_report.md` | `uv run robot-vacuum demo --max-steps 150 --seed 42` | Generated locally; ignored |
| Image | `results/screenshots/gui_demo.png` | Run `uv run robot-vacuum gui`, then click **Save screenshot** | Generated locally; ignored |
| Animation | `results/animations/random_policy_demo.gif` | `uv run robot-vacuum record-demo --max-steps 150 --seed 42 --frame-stride 3` | Generated locally; reviewed copy committed under `assets/evidence/` |
| Image | `results/plots/learning_curve.png` | `uv run robot-vacuum train --config config/smoke_training.json` | Generated locally; ignored |
| Image | `results/plots/critic_loss.png` | `uv run robot-vacuum train --config config/smoke_training.json` | Generated locally; ignored |
| Metrics | `results/metrics/training_metrics.json` | `uv run robot-vacuum train --config config/smoke_training.json` | Generated locally; ignored |
| Checkpoint | `results/checkpoints/best_actor.pt` | `uv run robot-vacuum train --config config/smoke_training.json` | Generated locally; ignored |
| Image | `results/trajectories/evaluation_trajectory.png` | `uv run robot-vacuum evaluate --checkpoint results/checkpoints/best_actor.pt` | Generated locally; ignored |

`uv run robot-vacuum make-demo --max-steps 150 --seed 42` is an equivalent convenience alias for the first three artifacts.

## What each artifact proves

- **Random-policy trajectory:** custom simulator, continuous movement, map rendering, cleaned cells, collision attempts, and heading visualization work together.
- **Random-policy metrics:** the SDK records the seed, requested/executed steps, reward, collisions, coverage, final pose, map, and artifact paths.
- **Random-policy report:** human-readable formatting is generated from the same metrics record rather than recomputing outcomes.
- **GUI screenshot:** the GUI's current map state can be saved portably through the SDK Matplotlib fallback. It is not a capture of window controls.

- **DDPG plots/metrics/checkpoint:** the two-episode smoke run exercises replay, updates, serialization, and plotting.
- **Evaluation trajectory:** the saved actor loads and runs without exploration noise.

The random-policy artifacts are not DDPG evidence. The DDPG smoke artifacts prove integration only and must not be presented as convergence evidence. The longer default command overwrites the same canonical paths, so preserve separately named copies when comparing experiments.

## Submission documents

These Markdown files are authored repository documentation, not generated runtime outputs, and are intended to be committed:

- `docs/PRD.md`
- `docs/PLAN.md`
- `docs/TODO.md`
- `docs/PRD_ddpg_algorithm.md`
- `docs/PRD_simulator.md`
- `docs/DEMO_GUIDE.md`
- `docs/GUI_GUIDE.md`
- `docs/RESULTS_GUIDE.md`
- `docs/SUMMARY_REPORT.md`
- `docs/STYLE_REPORT.md`
- `docs/FINAL_AUDIT.md`

Personal submission files and source course documents are intentionally excluded by generic PDF and office-document ignore rules. They are not project artifacts and must not be committed.
