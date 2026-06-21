# Experiment and Analysis Log

## Purpose

The experimental goal is to separate software-integration evidence from reinforcement-learning performance evidence. A run is interpreted from saved metrics and plots; screenshots alone are never treated as proof of learning.

## Experiment E0: seeded random policy

**Question:** Does the custom simulator produce deterministic, inspectable transitions and artifacts without a learning algorithm?

**Method:** Run `uv run robot-vacuum demo --max-steps 150 --seed 42` on `simple_house.json`.

**Observed evidence:** The trajectory includes continuous motion, collision attempts, first-visit cleaned cells, start/final markers, and heading. JSON and Markdown reports agree because both consume the same SDK snapshot.

**Conclusion:** Simulator, SDK, visualization, and reporting are integrated. The run says nothing about DDPG learning because its actions are random.

## Experiment E1: DDPG smoke integration

**Question:** Can transitions move through replay into real actor/critic updates, a checkpoint, metrics, and plots?

**Hypothesis:** With 2 episodes × 20 steps, the run should exercise all software paths after the 16-transition warm-up, but the budget is too small to establish convergence.

**Method:** Run `uv run robot-vacuum train --config config/smoke_training.json` with seed 42, batch size 16, Gaussian sigma 0.2, gamma 0.99, and tau 0.005.

**Observations:**

- Episode rewards: `4.7400`, `1.7959`.
- Coverage: `0.4983%`, `0.3322%`.
- Optimizer updates: `25`.
- Critic MSE values were finite; they ranged approximately from `0.0246` to `0.4592`.
- Reward decreased across the two episodes. Two samples cannot define a learning trend.

**Conclusion:** The full DDPG data/update/artifact pipeline executes correctly. The observations do not support convergence, monotonic improvement, or stability claims.

## Experiment E2: deterministic smoke-checkpoint evaluation

**Question:** Can the saved actor be loaded and evaluated without exploration noise?

**Method:** Run `uv run robot-vacuum evaluate --checkpoint results/checkpoints/best_actor.pt` for the simulator's 500-step limit.

**Observations:** Reward `-3.003`, coverage `0.89%`, two collisions. The trajectory stays near the start area.

**Conclusion:** Checkpoint serialization and deterministic evaluation work. Policy quality is poor, which is expected from the smoke budget.

## Next experiment matrix

| Experiment | Variables | Minimum evidence | Decision enabled |
|---|---|---|---|
| Multi-seed baseline | Seeds 1, 7, 21, 42, 84 | Reward/coverage mean and spread | Whether improvement is repeatable |
| Training-budget sweep | 50, 100, 200 episodes | Learning curves and evaluation coverage | Whether more experience helps |
| Noise sensitivity | Sigma 0.1, 0.2, 0.3 | Coverage and collision distributions | Exploration/exploitation trade-off |
| Reward sensitivity | Collision and cleaning weights | Reward components plus coverage | Whether reward aligns with task success |
| Map generalization | Multiple held-out maps | Deterministic evaluation per map | Whether behavior transfers |

No future experiment should be labeled converged without multiple seeds, a stated success threshold, and evaluation independent of exploration noise.
