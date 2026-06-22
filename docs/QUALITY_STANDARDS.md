# Quality Standards

## Enforced gates

Every proposed change should pass:

```bash
uv sync --extra dev --locked
uv run ruff check .
uv run pytest --cov=robot_vacuum_ddpg --cov-report=term-missing
```

`pyproject.toml` enforces an 85% branch-aware coverage threshold and the selected Ruff error, naming, import, modernization, bugbear, comprehension, and simplification rule families. `uv.lock` makes dependency resolution reproducible.

The GitHub Actions workflow runs the same locked installation, Ruff check, test suite, and coverage gate on pushes and pull requests. It has read-only repository permissions.

Final audit result (2026-06-23): 21 tests passed, branch-aware coverage was 89.17%, and Ruff reported zero violations.

## Design standards

- The simulator owns geometry, reward, state, collision, and dynamics.
- The SDK is the high-level use-case boundary for CLI and GUI consumers.
- The GUI renders immutable snapshots and does not duplicate simulator rules.
- Training configuration is validated before expensive work begins.
- Metrics are recorded once and reused by plots/reports.
- Generated results are either ignored and reproducible or deliberately copied into curated evidence.
- No result is described as convergence without supporting experiments.

## Review checklist

- Add or update a test for behavioral changes.
- Keep configuration outside domain code.
- Preserve state/action and checkpoint schema compatibility or version the change.
- Update commands, evidence paths, and limitations together.
- Inspect generated plots visually; do not test Matplotlib pixels.
- Never commit secrets, `.env`, caches, arbitrary desktop captures, or unreviewed personal files.
