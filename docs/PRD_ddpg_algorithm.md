# DDPG Algorithm Requirements

## 1. Purpose

Specify an inspectable, from-scratch PyTorch implementation of Deep Deterministic Policy Gradient for a two-dimensional continuous robot action. This document is the contract for the future `ddpg/` package and its tests.

## 2. Why DDPG is appropriate

The vacuum must choose continuously varying linear and angular commands. A Q-table cannot represent the continuous state/action space, and DQN requires a finite discrete action set; discretizing two controls reduces smoothness and grows combinations rapidly. PPO can support continuous actions, but it learns a stochastic policy on-policy and is not the algorithm assigned in Exercise 05. DDPG directly learns a deterministic continuous actor, uses a critic to differentiate action quality, and reuses stored experience off-policy through replay. That combination matches continuous motor control and the course's required architecture.

## 3. Dimensions and tensor conventions

- `state_dim`: read from the environment contract; default `13`.
- `action_dim`: exactly `2`.
- State batch: `float32`, shape `(batch_size, state_dim)`.
- Action batch: `float32`, shape `(batch_size, 2)`, normalized to `[-1, 1]`.
- Reward and done batches: shape `(batch_size, 1)`.
- Critic output: `float32`, shape `(batch_size, 1)`.
- Device: configurable, CPU by default for checker portability.

Shape validation shall fail clearly instead of relying on accidental PyTorch broadcasting.

## 4. Actor network

Planned location: `src/robot_vacuum_ddpg/ddpg/actor.py`.

The actor represents the deterministic policy:

```text
a = mu(s | theta_mu)
```

Baseline architecture:

```text
state -> Linear(256) -> ReLU -> Linear(256) -> ReLU
      -> Linear(action_dim) -> Tanh -> normalized action
```

The final `tanh` is mandatory and shall be directly visible in `forward`. It bounds both action components to `[-1, 1]`. The simulator, not the actor, scales normalized commands to physical speed limits. Tests shall check output shape, finite values, and bounds for random and extreme finite inputs.

## 5. Critic network

Planned location: `src/robot_vacuum_ddpg/ddpg/critic.py`.

The critic represents:

```text
Q(s, a | theta_Q)
```

Baseline architecture:

```text
concatenate(state, action)
  -> Linear(256) -> ReLU -> Linear(256) -> ReLU -> Linear(1)
```

The output has no bounding activation because Q-values may be any real number. Tests shall confirm that both state and action influence the output and that the batch result shape is `(batch, 1)`.

## 6. Target networks

Planned composition location: `src/robot_vacuum_ddpg/ddpg/agent.py`.

The agent owns:

- online actor `mu`;
- online critic `Q`;
- target actor `mu_target`;
- target critic `Q_target`.

At construction, target weights shall be exact copies of online weights. Target parameters shall not receive optimizer gradients.

## 7. Replay buffer

Planned location: `src/robot_vacuum_ddpg/ddpg/replay_buffer.py`.

Each transition contains:

```text
(state, action, reward, next_state, done)
```

Requirements:

- Fixed configurable capacity; oldest transitions are overwritten when full.
- Defensive copies or immutable storage so later environment mutation cannot change history.
- Uniform random sampling without replacement within one mini-batch.
- Injected/seeded NumPy generator for reproducibility.
- Clear error if sampling more items than stored.
- Returned batches have explicit dtypes and column shapes for reward/done.

Replay breaks short-term correlation and allows DDPG's off-policy updates to reuse data, improving sample efficiency and training stability.

## 8. Gaussian exploration noise

Planned location: `src/robot_vacuum_ddpg/ddpg/noise.py`; application in `agent.py` action selection.

During training only:

```text
epsilon ~ Normal(0, sigma^2 I)
action = clip(mu(state) + epsilon, -1, 1)
```

The baseline standard deviation is `sigma = 0.20`. Evaluation uses the unmodified deterministic actor. A future optional schedule may decay sigma, but constant Gaussian noise is sufficient for release 1 and must remain documented if used.

Without noise, a deterministic actor returns the same action for the same state. Early random weights would repeatedly collect a narrow and usually poor slice of experience; the replay buffer would contain little evidence of alternative turns or speeds, leaving the robot likely stuck in a local behavior such as looping or revisiting one region. Noise changes data collection, not the evaluation policy, and permits discovery of routes around obstacles and into uncleaned areas.

## 9. Update equations

### 9.1 Bellman target

With rewards `r`, terminal mask `d` encoded as `0.0` or `1.0`, and no target-network gradients:

```text
next_action = mu_target(next_state)
y = reward + gamma * (1 - done) * Q_target(next_state, next_action)
```

`y` shall be computed inside a no-gradient context or detached. The terminal mask is mandatory so terminal transitions do not bootstrap beyond the episode.

### 9.2 Critic update

```text
current_q = Q(state, action)
critic_loss = mean((current_q - y)^2)
```

The critic optimizer minimizes mean squared error. The baseline critic learning rate is `1e-3`.

### 9.3 Actor update

```text
predicted_action = mu(state)
actor_loss = -mean(Q(state, predicted_action))
```

Minimizing negative Q maximizes the critic's assessment of actor actions. Critic parameters need not be updated by this backward pass; their gradients shall be cleared or temporarily disabled to avoid useless accumulation. The baseline actor learning rate is `1e-4`.

### 9.4 Soft target update

Planned location: `src/robot_vacuum_ddpg/ddpg/soft_update.py`.

After online updates, every corresponding target parameter shall be updated in place:

```text
target_param = tau * online_param + (1 - tau) * target_param
```

The baseline is `tau = 0.005`. A direct unit test with known scalar tensors shall verify the arithmetic for actor and critic targets.

Soft updates stabilize critic learning because the Bellman target depends on separate networks that move slowly. If targets changed immediately with every online critic update, the critic would chase a value generated by the same rapidly changing estimator, creating feedback, oscillation, or divergence. Small `tau` creates a low-pass moving target while still tracking improved online networks.

## 10. Agent update sequence

One update shall follow this order:

1. Stop if replay contains fewer than `batch_size` transitions.
2. Sample one random mini-batch.
3. Compute target actions and terminal-masked Bellman targets without gradients.
4. Update the online critic from MSE.
5. Update the online actor from negative mean critic value.
6. Soft-update target critic and target actor.
7. Return scalar actor loss, critic loss, and optional Q statistics for metrics.

The trainer decides when updates occur; the agent owns the mathematical update.

## 11. Baseline hyperparameters

| Parameter | Default | Canonical configuration key |
|---|---:|---|
| Actor hidden layers | `[256, 256]` | `actor_hidden_sizes` |
| Critic hidden layers | `[256, 256]` | `critic_hidden_sizes` |
| Actor learning rate | `0.0001` | `actor_lr` |
| Critic learning rate | `0.001` | `critic_lr` |
| Discount factor | `0.99` | `gamma` |
| Soft update coefficient | `0.005` | `tau` |
| Gaussian exploration standard deviation | `0.20` | `noise_sigma` |
| Replay-buffer capacity | `100000` | `replay_buffer_size` |
| Batch size | `64` | `batch_size` |
| Warm-up transitions | `1000` | `warmup_transitions` |
| Updates per environment step | `1` | `updates_per_step` |

Configuration validation shall require positive learning rates, capacity at least batch size, `0 <= gamma <= 1`, `0 < tau <= 1`, and nonnegative sigma.

The seven assignment-facing names `actor_lr`, `critic_lr`, `gamma`, `tau`, `noise_sigma`, `batch_size`, and `replay_buffer_size` are stable public configuration keys and must appear unchanged in saved metrics and the final report.

The separate smoke configuration overrides batch size and warm-up to `16` while preserving the DDPG equations. Default training values must never be silently mutated to make a test pass.

## 12. Checkpoints

A checkpoint shall store online/target model states, optimizer states, state/action dimensions, resolved agent configuration, seed, training step, and schema version. Evaluation shall load on CPU by default and reject dimension/configuration incompatibility with a clear error. Checkpoint files will live under `results/checkpoints/`; this extra result directory may be created during implementation.

## 13. Required tests

- Actor shape and bounds.
- Critic scalar shape and concatenated input behavior.
- Target initialization equality.
- Replay capacity, defensive storage, error path, reproducible sample shapes.
- Gaussian noise changes actions when sigma is nonzero, leaves them unchanged at zero, and clips output.
- Bellman target excludes future Q when `done = 1`.
- Critic and actor losses are finite for a synthetic batch.
- One update changes online parameters.
- Soft update matches the exact interpolation and does not alias online tensors.
- Checkpoint round trip reproduces deterministic actor output.

## 14. Traceability table

| Assignment requirement | Planned implementation | Planned verification |
|---|---|---|
| Actor with `tanh` | `ddpg/actor.py` | actor bounds test |
| Critic gets state and action | `ddpg/critic.py` | critic shape/input test |
| Target actor and critic | `ddpg/agent.py` | target initialization test |
| Replay transitions | `ddpg/replay_buffer.py` | buffer tests |
| Gaussian exploration | `ddpg/noise.py`, `agent.py` | noise/clipping tests |
| Critic Bellman update | `ddpg/agent.py` | terminal-mask/update tests |
| Actor negative-Q update | `ddpg/agent.py` | actor update test |
| Soft target equation | `ddpg/soft_update.py` | exact arithmetic test |

Exact line numbers will be added to `SUMMARY_REPORT.md` only after implementation.
