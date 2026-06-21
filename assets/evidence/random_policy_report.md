# Random-Policy Simulator Demo Report

## Demo summary

This run exercised the custom continuous-control vacuum simulator with a seeded random policy. It generated trajectory and coverage visualization plus reproducible run metrics.

## Exact command

```bash
uv run robot-vacuum demo --max-steps 150 --seed 42
```

## Generated artifacts

- Trajectory: `results/trajectories/random_policy.png`
- JSON metrics: `results/metrics/random_policy_metrics.json`
- Markdown report: `results/reports/random_policy_report.md`

## Metrics

| Metric | Value |
|---|---:|
| Seed | 42 |
| Requested maximum steps | 150 |
| Steps executed | 150 |
| Total reward | -6.005049 |
| Collisions | 5 |
| Coverage | 1.384% |
| Final position | (0.523144, 0.915066) |
| Final heading | 0.764693 rad |
| Map | simple_house |

## Limitations

This demo uses random actions. It is simulator integration evidence, not a trained DDPG policy, and it does not demonstrate learning or convergence.

## Next steps for DDPG

Implement and test the actor, critic, target networks, replay buffer, Gaussian exploration noise, soft target updates, and training loop. Only then should real training metrics, learning curves, critic-loss plots, checkpoints, and noise-free evaluation trajectories be generated.
