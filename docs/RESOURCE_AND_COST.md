# Resource and Cost Awareness

## Current operating model

The project is local and offline. It calls no paid API, cloud model, database, or hosted simulator, so the direct per-run service cost is **$0**. The real costs are developer time, CPU time, memory, storage, electricity, and CI minutes.

## Measured submission artifacts

- Smoke training loop: approximately `0.10 s` on the audited Windows CPU environment, excluding interpreter startup and plot rendering.
- Smoke checkpoint: `186,229` bytes.
- Curated teacher evidence bundle: approximately `248 KB`.
- PyTorch was the largest dependency download during setup (approximately `117 MB` in this environment).

These measurements are environment-specific and are recorded as order-of-magnitude evidence, not universal benchmarks.

## Scaling behavior

Training work grows approximately with:

```text
episodes × steps_per_episode × updates_per_step × batch_size × network_compute
```

The default `200 × 500` configuration permits up to 100,000 environment transitions, compared with 40 in smoke training. Its upper-bound step count is therefore 2,500 times larger before considering larger `[256, 256]` networks and batch size 64.

Replay storage uses float32 arrays. With state dimension 13 and action dimension 2, raw bytes per transition are approximately:

```text
(state + action + reward + next_state + done) × 4
=(13 + 2 + 1 + 13 + 1) × 4
=120 bytes
```

At capacity 100,000, raw replay arrays require about 12 MB, excluding Python/allocator overhead. Model, optimizer, plots, and checkpoints add comparatively modest storage for the current architecture.

## Cost controls

- Use `smoke_training.json` for code checks and CI; never run the default experiment merely to verify imports.
- Keep CPU as the portable default and make acceleration an explicit future option.
- Save only the best observed checkpoint rather than every episode.
- Keep generated runtime artifacts ignored; commit only small curated evidence.
- Use uv's locked dependency cache in CI.
- Compare experiments through metrics before increasing training budget.

## If scaled beyond the course project

A professional deployment would record wall time, hardware, energy estimate, checkpoint retention, and CI usage per experiment. GPU or cloud execution should be justified by measured throughput improvement and a budget cap, not enabled by default.
