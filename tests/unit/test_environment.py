"""Environment contract and action-bound tests."""

import numpy as np

from robot_vacuum_ddpg.simulator.environment import VacuumEnvironment


def test_reset_returns_documented_state(environment: VacuumEnvironment) -> None:
    state = environment.reset(seed=42)

    assert state.shape == (13,)
    assert state.dtype == np.float32
    assert np.isfinite(state).all()
    assert environment.step_count == 0
    assert len(environment.trajectory) == 1


def test_step_clips_action(environment: VacuumEnvironment) -> None:
    environment.reset(seed=42)
    start_x = environment.robot.pose.x

    _, _, _, info = environment.step(np.asarray([5.0, 0.0], dtype=np.float32))

    expected_distance = (
        environment.config.robot.max_linear_speed * environment.config.robot.time_step
    )
    assert environment.robot.pose.x == start_x + expected_distance
    assert info["collision"] is False


def test_collision_has_negative_reward_component(environment: VacuumEnvironment) -> None:
    environment.reset(seed=42)
    environment.robot.pose = environment.floor_map.start_pose.__class__(0.21, 1.0, 3.141592653589793)

    _, reward, _, info = environment.step(np.asarray([1.0, 0.0], dtype=np.float32))

    assert info["collision"] is True
    assert info["reward_components"]["collision"] < 0.0
    assert reward < 0.0
