# P14 Owner Checkpoint — 2026-10-16

- Agent / Task: Codex / P14
- TaskStatus / ExecutionState: `in_progress` / `ACTIVE`
- Branch / Worktree: `codex/P14` / `G:/CODEX/New Manga.workspace/worktrees/P14`
- Base / current HEAD: `536962909963eaeeff7e94ff511f76f927652cd6` / `536962909963eaeeff7e94ff511f76f927652cd6`
- Reviewer: `dsh`
- Scope: implementation under `apps/desktop/frontend/src/**`; task/evidence under `doc/tasks/P14.md` and `verification/P14/**`.

## Working tree

- Modified implementation/tests: `apps/desktop/frontend/src/bookshelf/error.ts`, `error.test.ts`, `region/RegionOverlay.tsx`, `shell/AppShell.tsx`, and Workbench components/tests in `apps/desktop/frontend/src/workbench/**`.
- Modified task record: `doc/tasks/P14.md` (owner/reviewer/release metadata and verified prerequisites).
- New Workbench files: `DisabledFeature.tsx`, `ExportDialog.tsx`, `client.ts`, `client.test.ts`.
- Evidence captured under `verification/P14/**`.
- `verification/P04/diagnostic_p22_21316_1792156787974.jsonl` is untracked; preserve and never stage it.
- User-listed 19 protected dirty paths are not modified. No staged changes. Tauri files currently clean after `git diff` confirmed Cargo generated line-ending-only noise and only those generated paths were restored.

## Completed

- Read P14 scope, AD-001 Workbench §3/§7, collaboration rules, and DSH dispatch instructions.
- Implemented Workbench layout, navigation, existing Run/export flows, projection refresh after events, safe error/display projections, keyboard behavior, and visible disabled entries for every listed §7 gap.
- Frontend test: 18 files / 190 tests passed, exit 0 (`frontend-tests.log`, metadata alongside).
- Frontend build passed, exit 0 (`frontend-build.log`, metadata alongside).
- Python Core: 407 passed, exit 0 (`core-tests.log`).
- Rust source suite: 95 passed, exit 0 (`rust-source-tests.log`).
- Rust packaged sidecar suite: 12 passed, exit 0 (`rust-packaged-tests.log`).
- GUI e2e not run; this headless Windows environment lacks a WebView2 window handle (`0x80070578`).
- Governance checker not run; it is unavailable in this worktree.

## Open question / blocker to release

The user hard boundary forbids opaque references entering WebView, while the frozen page-image flow (§3 and contract §10.2) requires its short-lived random `m2res` mapping URL/ID to cross into WebView. The UI does not render the stable resource key, filesystem paths, export/import grants, or credentials. Asked user whether the `m2res` mapping is an explicit channel exception; no answer yet. Do not commit or dispatch review until this is resolved.

## Exact next steps

1. Incorporate the user's boundary decision.
2. Re-run frontend tests/build if any code changes; preserve Core/Rust evidence (frontend-only follow-up does not alter those suites).
3. Review final diff and permitted paths; create implementation commit only after the boundary is resolved.
4. Dispatch read-only DSH review on the fixed commit, capture session ID/result, then finish the Task test table, Handoff, and SHA256 evidence. Keep Task `in_review`; do not claim acceptance.
