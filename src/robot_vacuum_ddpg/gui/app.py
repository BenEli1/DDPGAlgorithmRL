"""Thin Tkinter GUI that renders and controls an SDK demo session."""

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from robot_vacuum_ddpg.gui.canvas_renderer import draw_snapshot
from robot_vacuum_ddpg.gui.view_model import status_values
from robot_vacuum_ddpg.sdk import DemoSession, DemoSnapshot, VacuumSDK
from robot_vacuum_ddpg.shared.paths import CONFIG_DIR, DATA_DIR, RESULTS_DIR


class VacuumGUI:
    """Interactive canvas and controls backed exclusively by VacuumSDK."""

    CANVAS_SIZE = (760, 560)

    def __init__(self, root: tk.Tk, sdk: VacuumSDK | None = None) -> None:
        self.root = root
        self.sdk = sdk or VacuumSDK()
        self.session: DemoSession | None = None
        self.running = False
        self.root.title("Robot Vacuum Simulator Demo")
        self._build_layout()
        self.reset()

    def _build_layout(self) -> None:
        controls = ttk.Frame(self.root, padding=8)
        controls.pack(fill="x")
        self.seed = tk.StringVar(value="42")
        self.max_steps = tk.StringVar(value="150")
        self.map_path = tk.StringVar(value=str(DATA_DIR / "sample_maps" / "simple_house.json"))
        self.delay_ms = tk.IntVar(value=40)
        for column, (label, variable, width) in enumerate(
            (("Seed", self.seed, 8), ("Max steps", self.max_steps, 8), ("Map file", self.map_path, 48))
        ):
            ttk.Label(controls, text=label).grid(row=0, column=column * 2, padx=3)
            ttk.Entry(controls, textvariable=variable, width=width).grid(
                row=0, column=column * 2 + 1, padx=3
            )
        ttk.Label(controls, text="Delay (ms)").grid(row=1, column=0, padx=3)
        ttk.Scale(controls, from_=0, to=500, variable=self.delay_ms).grid(
            row=1, column=1, sticky="ew", padx=3
        )
        buttons = (
            ("Reset", self.reset),
            ("Step random action", self.step_random),
            ("Run episode", self.run_episode),
            ("Pause / stop", self.pause),
            ("Save screenshot", self.save_screenshot),
            ("Generate report", self.generate_report),
        )
        for index, (label, callback) in enumerate(buttons):
            ttk.Button(controls, text=label, command=callback).grid(
                row=2, column=index, padx=3, pady=6, sticky="ew"
            )
        body = ttk.Frame(self.root, padding=(8, 0, 8, 8))
        body.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(
            body, width=self.CANVAS_SIZE[0], height=self.CANVAS_SIZE[1], background="white"
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        self.status_vars = {name: tk.StringVar(value="-") for name in status_values_names()}
        status = ttk.LabelFrame(body, text="Status", padding=8)
        status.pack(side="right", fill="y", padx=(8, 0))
        for row, (name, label) in enumerate(status_labels().items()):
            ttk.Label(status, text=f"{label}:").grid(row=row, column=0, sticky="nw", pady=3)
            ttk.Label(status, textvariable=self.status_vars[name], wraplength=210).grid(
                row=row, column=1, sticky="nw", pady=3
            )

    def reset(self) -> None:
        """Create a fresh SDK session from the current GUI inputs."""
        self.running = False
        try:
            self.session = self.sdk.create_demo_session(
                CONFIG_DIR / "default_simulator.json",
                seed=int(self.seed.get()),
                max_steps=int(self.max_steps.get()),
                map_path=Path(self.map_path.get()),
            )
            self._refresh(self.session.snapshot())
        except (OSError, ValueError, RuntimeError) as error:
            messagebox.showerror("Reset failed", str(error))

    def step_random(self) -> None:
        """Advance the current SDK session once."""
        if self.session is not None:
            self._refresh(self.session.step_random())

    def run_episode(self) -> None:
        """Start a non-blocking random-policy rollout."""
        if self.session is None or self.session.done:
            self.reset()
        self.running = self.session is not None
        self._run_next()

    def _run_next(self) -> None:
        if not self.running or self.session is None:
            return
        snapshot = self.session.step_random()
        self._refresh(snapshot)
        if snapshot.done:
            self.running = False
            return
        self.root.after(max(1, self.delay_ms.get()), self._run_next)

    def pause(self) -> None:
        """Pause an active scheduled rollout."""
        self.running = False

    def save_screenshot(self) -> None:
        """Save a portable rendering of the controls, map, and status."""
        if self.session is None:
            return
        path = RESULTS_DIR / "screenshots" / "gui_demo.png"
        try:
            self.sdk.save_gui_preview(self.session, path, Path(self.map_path.get()))
            self._refresh(self.session.snapshot(), str(path))
        except OSError as error:
            messagebox.showerror("Screenshot failed", str(error))

    def generate_report(self) -> None:
        """Generate the standard report bundle for the current session."""
        if self.session is None:
            return
        try:
            result = self.sdk.save_demo_artifacts(
                self.session,
                command="uv run robot-vacuum gui (Generate report button)",
            )
            self._refresh(self.session.snapshot(), str(result.report_path))
        except OSError as error:
            messagebox.showerror("Report failed", str(error))

    def _refresh(self, snapshot: DemoSnapshot, artifact_path: str = "-") -> None:
        self._draw(snapshot)
        for name, value in status_values(snapshot, artifact_path).items():
            self.status_vars[name].set(value)

    def _draw(self, snapshot: DemoSnapshot) -> None:
        draw_snapshot(self.canvas, snapshot, self.CANVAS_SIZE)


def status_labels() -> dict[str, str]:
    """Return stable user-facing status labels."""
    return {
        "step": "Current step",
        "reward": "Total reward",
        "collisions": "Collisions",
        "coverage": "Coverage",
        "action": "Current action",
        "state_length": "State vector length",
        "artifact": "Last artifact",
    }


def status_values_names() -> tuple[str, ...]:
    """Return status keys without requiring a simulator snapshot."""
    return tuple(status_labels())


def launch_gui() -> None:
    """Create the Tk root window and start the local event loop."""
    root = tk.Tk()
    VacuumGUI(root)
    root.mainloop()
