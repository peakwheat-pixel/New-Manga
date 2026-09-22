# T2.2.1 Release Gate — base `ef1a9b8`

Date: 2026-09-22 (Asia/Shanghai)

## Decision

**CONDITIONAL PASS TO PREPARE — scope frozen; implementation not started.**

Codex has created the formal Task and implementation plan from the current
integrated baseline. The owner worktrees and branches still need to be created
before the Task can move from `proposed` to `ready`; no production code or
tests were changed by this gate.

## Recovery point

| Item | Verified value |
|---|---|
| Repository | `G:/CODEX/New Manga` |
| Main branch | `master` |
| Base HEAD | `ef1a9b893d1da54fbc2b6e65dad285c54bae7ec5` |
| Primary owner | ZCode |
| QML/UI/UX owner | Qoder |
| Non-author reviewer/integrator | Codex |
| Primary branch/worktree | pending Codex creation |
| QML branch/worktree | pending Codex creation |
| Main worktree dirty state | Existing `experiments/TASK-017/README.md`, agent caches, plans, material, and wiki temp paths preserved; no cleanup or overwrite authorized |

## Gate checks

- **Roadmap order:** PASS. T2.2.1 is order 5 after verified T2.1.1.
- **Dependencies:** PASS. T1.1.2, T1.2.1, and T2.1.1 are recorded as
  verified complete in the current Plan and STATUS.
- **Current seam:** PASS. Production bootstrap publishes
  `bookshelfViewModel` and `navigationViewModel`; existing bookshelf models
  and navigation slots cover the planned picker handoff.
- **Reader gap:** PASS as released scope. `readerPickChapter` is present but
  disabled; the webtoon Flickable lacks the paged viewer's explicit
  `Tokens.bgCanvas` ground.
- **Workbench gap:** PASS as released scope. `workbenchPickContext` is
  present but disabled without context; the command-error surface exists but
  remains provisional and must be polished without changing error generation.
- **Architecture boundary:** PASS. No QML database/file access, new page,
  storage change, bootstrap seam, Schema, provider/runtime, or dependency
  change is included.
- **Write-set separation:** PASS in principle. ZCode owns functional seam/test
  work; Qoder owns QML/UI/UX paths. Codex must create separate worktrees and
  serialize any overlapping test edits.

## Commands and observed results

| Check | Result |
|---|---|
| `git status --short --branch` | PASS — pre-existing dirty/untracked paths preserved |
| `git rev-parse HEAD` | PASS — `ef1a9b893d1da54fbc2b6e65dad285c54bae7ec5` |
| T1.1.2/T1.2.1/T2.1.1 dependency evidence | PASS — current Plan/STATUS and linked integration records |
| Implementation focused tests | NOT_RUN — implementation has not started |
| Full suite | NOT_RUN — this is a preparation gate, not a completion claim |
| Compileall | NOT_RUN — no implementation change to validate |
| Bootstrap smoke | NOT_RUN — reserved for implementation/integration evidence |
| Diff check | PASS — governance files will be checked before commit |

## Gate boundary

ZCode and Qoder may begin only after Codex records the actual base, branch, and
worktree for each owner and changes the Task to `ready`. Qoder may implement
only the declared QML/UI/UX paths; ZCode may not invent a Python seam or modify
shared contracts without a Codex scope decision. Both agents must deliver
fixed heads, tests, evidence, and Handoff material. Neither author worktree may
merge `master` or declare `VERIFIED_COMPLETE`.
