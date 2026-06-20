# AI Prompt and Decision Log

This log records material AI-assisted development prompts and the decisions produced from them. It is intentionally concise rather than a transcript of every tool command. Dates use the local project date.

## Entry 001 - Documentation-first project definition

**Date:** 2026-06-20  
**Role requested:** Senior software architect and implementation agent  
**Phase:** Requirements and architecture only

### Prompt summary

Create a small professional Python project for Exercise 05: a custom robotic-vacuum simulator trained with DDPG. Treat four attached course PDFs in a strict priority order. Before coding, provide safe scope, repository structure, and complete drafts of the README, PRD, plan, TODO, DDPG PRD, simulator PRD, summary report, and prompt log. Do not implement code.

### Source files reviewed

1. `EX05-DDPG-Robot-Simulator (1).pdf`
2. `gemini-L09-Deep-Deterministic-Policy-Gradient-DDPG-and-EX05t.pdf`
3. `DDPG_Autonomous_Blueprint.pdf`
4. `software_submission_guidelines-V3.pdf`

### Decisions

- Use a custom project-owned simulator with no Gymnasium/Gazebo dependency.
- Use normalized action `[linear_command, angular_command]` in `[-1,1]^2` and scale it inside the simulator.
- Use seven rays plus velocity, heading, coverage, and collision for a 13-value default state.
- Use a native JSON map with rectangular obstacles and a loader protocol; do not claim full HouseExpo support.
- Use first-time coverage reward with collision, step, and control penalties.
- Implement DDPG directly in PyTorch with final actor `tanh`, critic state/action concatenation, target networks, replay, Gaussian noise, terminal-masked Bellman target, negative-Q actor loss, and soft updates.
- Use one SDK facade so CLI code does not duplicate business logic.
- Separate checker-friendly smoke correctness from longer-run convergence claims.
- Mark summary-report results and code-line locations as pending rather than inventing evidence.

### Strict grader review findings and improvements

| Initial risk or vague point | Improvement made |
|---|---|
| "Continuous movement" had no formal command meaning | Defined two normalized controls and scaling semantics. |
| State description lacked stable order/dimension | Defined a 13-value ordered baseline with normalization. |
| Collision response was underspecified | Required full-pose rejection, unchanged heading/position, zero resulting velocity, and a contact flag. |
| Coverage reward could be farmed | Reward only newly cleaned free-space cells once per episode. |
| DDPG description could omit terminal masking | Added `(1-done)` explicitly to the Bellman target and tests. |
| Exploration rationale was conceptual only | Specified zero-mean Gaussian noise, sigma, training-only use, clipping, and failure mode without it. |
| Soft updates lacked a testable statement | Added exact interpolation equation and known-tensor test. |
| HouseExpo language risked overclaiming | Repeatedly labeled release 1 as native sample format plus future adapter boundary. |
| Plot requirements lacked file contracts | Fixed paths for reward, critic loss, trajectory, and metrics JSON. |
| "Training works" was not measurable | Added a two-episode smoke criterion requiring an update and non-empty artifacts. |
| Final report could claim future work as done | Added visible documentation-phase status and TBD evidence table. |
| Software requirements were diffuse | Added uv/Ruff/pytest/coverage/SDK/configuration quality gates. |

### Output

- `README.md`
- `docs/PRD.md`
- `docs/PLAN.md`
- `docs/TODO.md`
- `docs/PRD_ddpg_algorithm.md`
- `docs/PRD_simulator.md`
- `docs/SUMMARY_REPORT.md`
- `docs/PROMPT_LOG.md`

### Implementation status

No implementation code, package scaffold, configuration, test, training artifact, or generated result was created in this entry. Temporary PDF-inspection files were removed after source review.

## Entry 002 - Strict AI-grader documentation review

**Date:** 2026-06-20  
**Phase:** Documentation quality gate

### Prompt summary

Review all eight generated documents as a strict grader for Exercise 05, DDPG completeness, continuous control, forbidden platforms, required graphs, professional software practice, realistic scope, and honest limitations; then improve the documents directly without implementation.

### Findings

- All mandatory Exercise 05 and DDPG components were already present.
- Collision response and anti-tunneling behavior still used choice-oriented wording and were not implementation-ready.
- Plot paths existed, but exact assignment axis semantics needed stronger acceptance language.
- The plan mentioned tests but did not consistently order work as red-green-refactor.
- The README needed a compact compliance index and the planned checkpoint directory.
- Submission evidence needed explicit checks for an absent `requirements.txt`, committed `uv.lock`, and CLI-to-SDK delegation.
- The workspace is not currently a Git repository, so professional version-history compliance remains a visible scaffold task.
- The original two-episode smoke command conflicted with the 1,000-transition default warm-up and could not perform the update its acceptance criterion required.
- Two quotation marks in this log were corrupted by terminal encoding, and the temporary-file note was stale.

### Improvements

- Chose one collision contract: reject the full proposed pose and set resulting velocity to zero.
- Made swept-path collision validation mandatory.
- Added graph semantics, plot acceptance criteria, and requirement traceability.
- Reordered simulator and DDPG plan items around test-first development.
- Added a README Exercise 05 compliance matrix.
- Added uv lockfile, no-`requirements.txt`, and SDK delegation audit criteria.
- Added Git initialization/history checks without performing repository setup during the documentation-only phase.
- Added a dedicated smoke configuration with batch size and warm-up 16 so a 40-step run can perform updates without weakening production defaults.
- Added an explicit documentation-grade table to the summary report.
- Repaired encoding and status text in this prompt log.

### Verification

Documentation-only search audit; no implementation code or result artifact was created.

## Template for future entries

```text
## Entry NNN - Short title

Date:
Phase:
Prompt summary:
Files/source material consulted:
Decisions and trade-offs:
Files changed:
Verification performed:
Open risks or follow-up:
```

Future entries should record prompts that materially affect architecture, algorithms, reward design, public interfaces, dependencies, experiments, or final conclusions. Routine formatting and typo corrections do not need separate entries.
