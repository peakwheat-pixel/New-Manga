# T2.1.1 Release Gate — base `7f34135`

Date: 2026-09-22 (Asia/Shanghai)

## Decision

**PASS TO START — `T2.1.1 = READY`, implementation not started.**

This is a release decision only. No production QML, tests, Schema, bootstrap,
provider/runtime, or dependency code was changed by this gate.

## Recovery point

| Item | Verified value |
|---|---|
| Repository | `G:/CODEX/New Manga` |
| Main branch | `master` |
| Base HEAD | `7f341355968f69fc3db7b6824d73ec7d56c182be` |
| Owner branch | `agent/qoder/T2.1.1-design-f-qml` |
| Owner worktree | `G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml` |
| Owner worktree HEAD | `7f341355968f69fc3db7b6824d73ec7d56c182be` |
| Reviewer/integrator | Codex, non-author |
| Main worktree dirty state | Pre-existing files preserved; no cleanup or overwrite performed |

## Gate checks

- **Roadmap order:** PASS. T2.1.1 is order 4 and follows T1.1.2 and T1.2.1.
- **Dependencies:** PASS. T1.1.2 and T1.2.1 are recorded as
  `VERIFIED_COMPLETE` in the current Rebaseline Plan and STATUS.
- **Design input:** PASS. F is the user-selected Graphite Atelier combination:
  A color modes/visual language, B geometry, A information architecture.
- **Token source:** PASS. `tokens-cand-f.json` records F/A color equality,
  F/B geometry equality, and `card-w = 158px`; the contract requires F's
  24-pair contrast surface and the selected-row/direct-skip extensions.
- **Token mechanism:** PASS. This Task freezes mechanism (a), one QML
  `pragma Singleton` delivered through `qmldir`.
- **Current gap:** CONFIRMED. Production QML has no existing `qmldir` or
  theme singleton and still contains pre-F hard-coded colors. This is the
  released implementation scope, not evidence of completion.
- **UI/test seam:** PASS. The existing AppShell QML harness loads all four
  page roots; `tests/ui_shell/test_qml_shell.py`,
  `tests/workbench/test_qml_workbench.py`, and the bootstrap smoke test are
  the available starting points for fresh implementation evidence.
- **Write-set boundary:** PASS. `src/bootstrap/app.py`, ports, Schema,
  provider/runtime, Settings, Roadmap content, user data, and other dirty
  files are excluded from Owner changes.

## Commands and observed results

| Check | Result |
|---|---|
| `git status --short --branch` | `master`; only pre-existing dirty/untracked files; preserved |
| `git rev-parse HEAD` | `7f341355968f69fc3db7b6824d73ec7d56c182be` |
| `git worktree add -b agent/qoder/T2.1.1-design-f-qml ... 7f34135` | PASS; new worktree clean at base |
| Implementation focused tests | NOT_RUN — no implementation exists at gate time |
| Full suite | NOT_RUN — not a completion claim |
| Compileall | NOT_RUN — no implementation change to validate |
| Bootstrap smoke | NOT_RUN — reserved for implementation/integration evidence |
| Diff check | NOT_RUN before governance edits; must be run by Codex after this record is committed and by the implementation review |

## Gate boundary

Qoder may implement only the allowed paths in
[`doc/tasks/T2.1.1.md`](../../doc/tasks/T2.1.1.md). Qoder must stop and ask
Codex before any scope expansion. A fixed delivery HEAD and Handoff are
required before non-author review. `READY` is not `VERIFIED_COMPLETE` and does
not release T2.2.1 or any later Roadmap Task.
