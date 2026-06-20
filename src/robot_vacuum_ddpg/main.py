"""Command-line entry point for the simulator-only project phase."""

import argparse
from pathlib import Path

from robot_vacuum_ddpg.sdk import VacuumSDK
from robot_vacuum_ddpg.shared.paths import CONFIG_DIR, RESULTS_DIR


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(description="Custom 2D robotic vacuum simulator")
    parser.add_argument(
        "--config",
        type=Path,
        default=CONFIG_DIR / "default_simulator.json",
        help="Simulator JSON configuration",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS_DIR / "trajectories" / "random_policy.png",
        help="Trajectory PNG destination",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-steps", type=int, default=100)
    return parser


def main() -> int:
    """Run one random-policy episode through the SDK facade."""
    args = build_parser().parse_args()
    try:
        result = VacuumSDK().run_random_episode(
            simulator_config_path=args.config,
            output_path=args.output,
            seed=args.seed,
            max_steps=args.max_steps,
        )
    except (ValueError, RuntimeError) as error:
        print(f"error: {error}")
        return 2
    print(
        f"steps={result.steps} reward={result.cumulative_reward:.3f} "
        f"coverage={result.coverage_ratio:.3f} collisions={result.collisions}"
    )
    print(f"trajectory={result.trajectory_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
