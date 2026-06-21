"""Command-line entry point for demos, DDPG training, evaluation, and GUI use."""

import argparse
import subprocess
import sys
from pathlib import Path

from robot_vacuum_ddpg.sdk import VacuumSDK
from robot_vacuum_ddpg.shared.paths import CONFIG_DIR, RESULTS_DIR


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(description="Custom 2D robotic vacuum simulator")
    parser.add_argument(
        "command",
        nargs="?",
        choices=("demo", "make-demo", "record-demo", "gui", "train", "evaluate"),
        default="demo",
        help="Generate evidence, train/evaluate DDPG, or open the local GUI",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=CONFIG_DIR / "default_simulator.json",
        help="Simulator config for demos or training config for train",
    )
    parser.add_argument(
        "--simulator-config",
        type=Path,
        default=CONFIG_DIR / "default_simulator.json",
        help="Simulator JSON configuration for training and evaluation",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS_DIR / "trajectories" / "random_policy.png",
        help="Trajectory PNG destination",
    )
    parser.add_argument(
        "--metrics-output",
        type=Path,
        default=RESULTS_DIR / "metrics" / "random_policy_metrics.json",
        help="Demo metrics JSON destination",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=RESULTS_DIR / "reports" / "random_policy_report.md",
        help="Demo Markdown report destination",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=RESULTS_DIR / "checkpoints" / "best_actor.pt",
        help="DDPG checkpoint used by evaluate",
    )
    parser.add_argument(
        "--animation-output",
        type=Path,
        default=RESULTS_DIR / "animations" / "random_policy_demo.gif",
        help="Animated simulator GIF destination",
    )
    parser.add_argument("--frame-stride", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-steps", type=int, default=100)
    return parser


def main() -> int:
    """Dispatch every public use case through the SDK facade."""
    args = build_parser().parse_args()
    if args.command == "gui":
        from robot_vacuum_ddpg.gui import launch_gui

        launch_gui()
        return 0
    sdk = VacuumSDK()
    try:
        if args.command == "record-demo":
            path = sdk.record_random_episode(
                args.config,
                args.animation_output,
                seed=args.seed,
                max_steps=args.max_steps,
                frame_stride=args.frame_stride,
            )
            print(f"animation={path}")
            return 0
        if args.command == "train":
            result = sdk.train(args.config, args.simulator_config)
            print(f"episodes={result.episodes} updates={result.updates}")
            print(f"metrics={result.metrics_path}")
            print(f"learning_curve={result.learning_curve_path}")
            print(f"critic_loss={result.critic_loss_path}")
            print(f"checkpoint={result.checkpoint_path}")
            return 0
        if args.command == "evaluate":
            result = sdk.evaluate(
                args.checkpoint,
                args.simulator_config,
                output_path=RESULTS_DIR / "trajectories" / "evaluation_trajectory.png",
                seed=args.seed,
            )
            print(
                f"steps={result.steps} reward={result.total_reward:.3f} "
                f"coverage={result.coverage_percent:.2f}% collisions={result.collisions}"
            )
            print(f"trajectory={result.trajectory_path}")
            return 0
        result = sdk.run_random_episode(
            simulator_config_path=args.config,
            output_path=args.output,
            metrics_path=args.metrics_output,
            report_path=args.report_output,
            seed=args.seed,
            max_steps=args.max_steps,
            command="uv run robot-vacuum " + subprocess.list2cmdline(sys.argv[1:]),
        )
    except (KeyError, OSError, TypeError, ValueError, RuntimeError) as error:
        print(f"error: {error}")
        return 2
    print(
        f"steps={result.steps} reward={result.cumulative_reward:.3f} "
        f"coverage={result.coverage_ratio:.3f} collisions={result.collisions}"
    )
    print(f"trajectory={result.trajectory_path}")
    print(f"metrics={result.metrics_path}")
    print(f"report={result.report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
