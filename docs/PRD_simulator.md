# Custom 2D Simulator Requirements

## 1. Purpose and boundary

Define the small custom simulator in which DDPG learns vacuum navigation. The simulator owns deterministic geometry, robot motion, sensing, cleaning coverage, reward, episode state, and map validation. It is not a Gym-compatible wrapper and has no dependency on PyTorch.

Implementation status: this simulator contract is implemented under `src/robot_vacuum_ddpg/simulator/` and verified by simulator-focused tests. DDPG and training are implemented in separate packages and consume the simulator only through its existing state/action contract.

## 2. Release 1 map scope

Release 1 supports a project-native JSON schema with:

- rectangular map bounds;
- axis-aligned rectangular obstacles;
- a valid start pose;
- metric-like floating-point coordinates.

A `MapLoader` protocol shall isolate file format conversion from simulation. A future `HouseExpoMapLoader` may convert HouseExpo polygons into the same internal `FloorMap`, but it is outside release 1. The project shall include a small sample JSON and shall not label it as a genuine HouseExpo file.

### Proposed native JSON

```json
{
  "schema_version": "1.00",
  "name": "simple_room",
  "bounds": {"min_x": 0.0, "min_y": 0.0, "max_x": 10.0, "max_y": 8.0},
  "start_pose": {"x": 1.0, "y": 1.0, "theta": 0.0},
  "obstacles": [
    {"type": "rectangle", "min_x": 4.0, "min_y": 2.5, "max_x": 5.5, "max_y": 5.5}
  ]
}
```

Validation shall reject unknown schema versions, non-finite coordinates, inverted rectangles, obstacles outside bounds, overlapping start pose, and maps with no cleanable cells.

## 3. Robot model

The robot is a circle of configured radius with pose `(x, y, theta)`. It stores current normalized/physical linear and angular velocity only as needed to form the next state.

The normalized action is:

```text
a = [a_linear, a_angular], each in [-1, 1]
v = a_linear * max_linear_speed
omega = a_angular * max_angular_speed
```

With fixed time step `dt`, differential-drive-like unicycle kinematics are:

```text
theta_next = wrap(theta + omega * dt)
x_next = x + v * cos(theta_next) * dt
y_next = y + v * sin(theta_next) * dt
```

Using the updated heading is a documented semi-implicit choice that remains stable and simple. A single geometry function shall own this convention so tests and documentation cannot drift.

Actions are clipped before scaling. A proposed pose is collision-checked before commit. On collision, release 1 rejects the full proposed pose: position and heading remain at the last valid pose, linear and angular velocities are recorded as zero, and the contact flag is set. This single policy is mandatory and directly tested.

## 4. Collision model

Collision occurs when the robot circle overlaps or touches:

- the outer map boundary; or
- any obstacle rectangle.

Contact counts as collision using a small configured numerical tolerance. Collision checks shall use the robot radius, not only its center. The implementation shall validate the swept motion from current pose to proposed pose against expanded boundaries and obstacles so a step cannot tunnel through geometry. A small time step remains useful but is not the sole safety mechanism.

The environment shall never commit a penetrating pose. The `info` dictionary records collision and the attempted pose.

## 5. Distance sensors

The default sensor uses seven rays relative to heading at angles:

```text
[-90, -60, -30, 0, 30, 60, 90] degrees
```

Each ray returns the nearest distance to boundary or obstacle, capped at `sensor_max_range`, divided by that range, and clipped to `[0, 1]`. `0` means immediate contact; `1` means no hit within range. Ray calculations shall be deterministic and independent of plotting.

Sensor count and angles are configurable. State dimension shall be derived from the loaded simulator configuration.

## 6. Cleaning coverage

The map is discretized only for tracking cleaned area, not for robot motion or action selection. A configured square grid marks cells whose centers lie in free space. On reset, all cleanable cells are dirty. After every valid pose, any free cell center within the circular cleaning radius becomes clean.

```text
coverage_ratio = cleaned_free_cells / total_free_cells
```

A cell earns new-cleaning reward exactly once per episode. Revisiting it does not earn that term. This prevents stationary or circular reward farming.

## 7. State vector

With seven default rays, observations have 13 continuous values in this stable order:

| Indices | Feature | Normalization |
|---|---|---|
| `0..6` | nearest ray distances | distance / max range in `[0,1]` |
| `7` | current linear velocity | divided by max absolute linear speed, `[-1,1]` |
| `8` | current angular velocity | divided by max absolute angular speed, `[-1,1]` |
| `9` | heading sine | `sin(theta)`, `[-1,1]` |
| `10` | heading cosine | `cos(theta)`, `[-1,1]` |
| `11` | cleaning coverage | ratio in `[0,1]` |
| `12` | most recent collision/contact | `0.0` or `1.0` |

The state is returned as a finite NumPy `float32` array. Absolute `(x,y)` is intentionally omitted so the baseline policy learns from local sensing and coverage; adding normalized position is an extension requiring a schema/state-dimension update.

## 8. Reward function

Reward shall be decomposed and expose each contribution in `info`:

```text
reward =
    clean_weight * newly_cleaned_cells
  + completion_bonus * reached_target_coverage
  - collision_penalty * collision
  - step_penalty
  - control_penalty * mean(action^2)
```

Proposed baseline values:

| Term | Planned value | Intent |
|---|---:|---|
| `clean_weight` | `1.0` per cell | Dominant useful progress signal |
| `completion_bonus` | `25.0` | Reward finishing the coverage target |
| `collision_penalty` | `5.0` | Make contact clearly undesirable |
| `step_penalty` | `0.01` | Discourage aimless long episodes |
| `control_penalty` | `0.01` | Mild efficiency/smoothness pressure |

The exact scale will be validated against cell size so one normal cleaning step is positive. Configuration owns all weights. No reward is based directly on hidden future information.

## 9. Episode lifecycle

### Reset

1. Validate or accept the already validated map.
2. Seed the environment RNG if a seed is supplied.
3. Place the robot at a configured valid start pose.
4. Clear coverage, trajectory, step count, collision flag, and velocities.
5. Clean cells under the initial cleaning disk without awarding transition reward.
6. Return the initial state.

### Step

1. Validate action shape and finite values.
2. Clip action to `[-1, 1]`.
3. Propose the next pose through kinematics.
4. Detect collision and commit only a valid pose.
5. On collision, reject the full pose and record zero resulting velocity plus contact; otherwise update the committed pose and velocities.
6. Append the committed pose to the trajectory.
7. Mark newly cleaned cells.
8. Calculate decomposed reward.
9. Increment step count and calculate termination.
10. Return `(next_state, reward, done, info)`.

### Termination

An episode ends when target coverage is reached or `max_steps` is exhausted. Collision is non-terminal by default so the policy can learn recovery; `terminate_on_collision` is configurable and defaults to false. The `info` result shall distinguish `terminated_reason` values such as `coverage` and `max_steps`.

## 10. Default simulator configuration

| Parameter | Planned default |
|---|---:|
| Time step | `0.10` |
| Robot radius | `0.20` |
| Cleaning radius | `0.25` |
| Max linear speed | `1.00` |
| Max angular speed | `2.00` |
| Sensor max range | `3.00` |
| Sensor angles | seven angles listed above |
| Coverage cell size | `0.20` |
| Target coverage | `0.90` |
| Max steps | `500` |
| Terminate on collision | `false` |

All physical and reward values reside in `config/default_simulator.json`, are range-validated, and are copied into saved run metrics.

## 11. Class responsibilities

| Module | Responsibility |
|---|---|
| `config.py` | Convert versioned JSON values into validated typed simulator configuration |
| `coverage.py` | Build free-space cells and track first-time cleaning independently of motion |
| `geometry.py` | Pure intersection, collision, angle, and kinematics helpers/data |
| `map_loader.py` | Loader protocol, native JSON parsing, validation into `FloorMap` |
| `observation.py` | Assemble, normalize, and validate the stable state-vector contract |
| `robot.py` | Robot pose, action scaling, proposal/commit state |
| `sensors.py` | Ray definitions and nearest normalized distances |
| `rewards.py` | Reward configuration and pure component calculation |
| `environment.py` | Episode lifecycle, coverage, composition, public contract |

Rendering is excluded from simulator modules and lives in `visualization/`.

## 12. Acceptance tests

- Reset returns the documented 13-value default state with finite normalized values.
- Same map, seed, and action sequence produce identical state/reward trajectories.
- Continuous fractional actions cause fractional pose changes.
- Out-of-range actions behave exactly like their clipped equivalents.
- Robot cannot cross boundary or obstacle geometry.
- A swept-path test proves the robot cannot tunnel through a thin obstacle.
- A collision leaves position and heading unchanged and sets resulting velocities to zero.
- Sensor distance decreases predictably when moving toward a wall.
- New coverage increases the ratio and reward; revisiting does neither.
- Completion and maximum-step termination report distinct reasons.
- Malformed maps fail with field-specific messages.
- Simulator package imports neither PyTorch nor forbidden environment frameworks.

## 13. Trajectory evidence contract

The environment shall record the committed pose after reset and after every step as an ordered sequence of `(x, y, theta)` values. Rejected collision proposals are not inserted as physical positions; the unchanged committed pose may be repeated so the plotted time sequence remains aligned with steps. Evaluation shall pass this trajectory and the loaded `FloorMap` to the visualization layer.

The simulator does not render figures. `visualization/trajectory.py` shall use the recorded sequence to draw map boundaries, obstacles, a continuous path line, and distinct start/final markers under `results/trajectories/`. This separation keeps geometry and episode state independent from Matplotlib.

## 14. HouseExpo extension plan

A future adapter may:

1. Read a HouseExpo JSON record.
2. Extract or convert the floor boundary and obstacle/wall polygons.
3. Normalize coordinates into the internal `FloorMap` geometry.
4. Choose or validate a free start pose.
5. Rasterize free cells only for coverage tracking.

Polygon obstacles would require general circle-polygon collision and ray-polygon intersection. Until that adapter and tests exist, README and report language must say `HouseExpo-ready loader abstraction`, never `HouseExpo supported`.
