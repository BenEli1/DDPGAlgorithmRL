"""Stable paths relative to the repository root."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"


def ensure_result_directories() -> None:
    """Create the result directories used by command-line runs."""
    for path in (
        RESULTS_DIR / "checkpoints",
        RESULTS_DIR / "metrics",
        RESULTS_DIR / "plots",
        RESULTS_DIR / "reports",
        RESULTS_DIR / "screenshots",
        RESULTS_DIR / "trajectories",
    ):
        path.mkdir(parents=True, exist_ok=True)
