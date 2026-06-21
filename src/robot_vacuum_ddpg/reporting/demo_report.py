"""Generate machine-readable and Markdown random-policy demo reports."""

import json
from pathlib import Path
from typing import Any


def write_demo_metrics(metrics: dict[str, Any], output_path: Path) -> Path:
    """Write one demo run record as stable, readable JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    return output_path


def write_demo_report(metrics: dict[str, Any], output_path: Path) -> Path:
    """Write a human-readable report from the same metrics record."""
    artifacts = metrics["generated_artifacts"]
    final_position = metrics["final_position"]
    rows = (
        ("Seed", metrics["seed"]),
        ("Requested maximum steps", metrics["max_steps"]),
        ("Steps executed", metrics["steps_executed"]),
        ("Total reward", f"{metrics['total_reward']:.6f}"),
        ("Collisions", metrics["collisions"]),
        ("Coverage", f"{metrics['coverage_percent']:.3f}%"),
        ("Final position", f"({final_position['x']:.6f}, {final_position['y']:.6f})"),
        ("Final heading", f"{metrics['final_heading']:.6f} rad"),
        ("Map", metrics["map_name"]),
    )
    table = "\n".join(f"| {name} | {value} |" for name, value in rows)
    report = f"""# Random-Policy Simulator Demo Report

## Demo summary

This run exercised the custom continuous-control vacuum simulator with a seeded random policy. It generated trajectory and coverage visualization plus reproducible run metrics.

## Exact command

```bash
{metrics["command"]}
```

## Generated artifacts

- Trajectory: `{artifacts["trajectory"]}`
- JSON metrics: `{artifacts["metrics"]}`
- Markdown report: `{artifacts["report"]}`

## Metrics

| Metric | Value |
|---|---:|
{table}

## Limitations

This demo uses random actions. It is simulator integration evidence, not a trained DDPG policy, and it does not demonstrate learning or convergence.

## Next steps for DDPG

Implement and test the actor, critic, target networks, replay buffer, Gaussian exploration noise, soft target updates, and training loop. Only then should real training metrics, learning curves, critic-loss plots, checkpoints, and noise-free evaluation trajectories be generated.
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return output_path
