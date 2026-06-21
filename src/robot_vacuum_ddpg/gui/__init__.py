"""Local Tkinter interface for SDK-backed simulator demos."""

__all__ = ["launch_gui"]


def launch_gui() -> None:
    """Import Tkinter only when the optional desktop interface is launched."""
    from robot_vacuum_ddpg.gui.app import launch_gui as launch

    launch()
