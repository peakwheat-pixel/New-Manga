# P02 Antigravity formal implementation task r1

This is the formal P02 implementation start message following your explicit `ACCEPT` in conversation `054911c9-b133-4514-b471-143b80249fce`. Codex has integrated the P02 `in_progress / ACTIVE` status and fast-forwarded your clean Owner branch to the current `main` checkpoint. Read the actual Live Git state before editing: report `git rev-parse HEAD`, `git rev-parse HEAD^{tree}`, branch and clean status.

## Task and fixed contract

- Task: `doc/tasks/P02.md`, real Workbench Tauri/WebView2 behavior verification harness.
- Owner: Antigravity. Non-author implementation Reviewer: DeepSeek Harness. Integrator: Codex.
- Worktree: `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`
- Branch: `agent/antigravity/P02-real-webview-harness`
- Behavior base: `241ff3b70b6fc0490ea238efd486cc707f849031`
- Frozen scope contract SHA-256: `27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`; scope r1–r4 remains frozen. Do not revise AC, broaden Owner paths, alter dependencies or make product decisions.

## Implement the released AC1–AC7

Build a reproducible, synthetic-data-only harness for verifying this source tree's actual Tauri/WebView2 Workbench. Cover executable identity, navigation and input, the 300ms quiet period/page invalidation, post-write refresh for retype/undo/restore, Workbench keyboard/focus, and computed colors/token mapping/contrast. Persist per-case result (`PASS`/`FAIL`/`BLOCKED`/`NOT_RUN`), real/mock layer, command, environment, source/binary hashes, exit, timing/color data, screenshots/logs and skip reason. Record product gaps as findings; do not repair product UI, styling, tokens, debounce, focus behavior or performance.

Only use the frozen Task allowlist: `apps/desktop/frontend/e2e/**`, `verification/P02/**`, task-produced rebuildable local outputs in `apps/desktop/frontend/dist/**` and `verification/P02/cargo-target/**` after checking their pre-existing contents, `doc/handoffs/P02-*.md`, and actual execution records in `doc/tasks/P02.md`. Do not modify `apps/desktop/frontend/src/**`, dependency manifests, `apps/desktop/src-tauri/**` source, Python Core, SQLite schema/migrations, shared IPC/Schema, dependencies, packaged EXE, P03 runner, design tokens/contracts, or any user data, Locks, current/pinned Revision or credentials. No new dependency without a Codex-frozen minimal scope delta.

## Stage A: safe foundation first

1. Read the Task and inspect the real source, available WebView2/runtime/driver tools, and the existence/content of `apps/desktop/frontend/dist` and `verification/P02/cargo-target`; do not overwrite unknown files.
2. Implement the smallest useful synthetic fixture plus read-only environment/source identity probe in allowed paths. Static inspection and safe front-end control checks are allowed; record exact commands and results.
3. Continue all build-independent harness work that can be safely completed. Keep changes on this Owner branch, checkpoint commits, and report the exact files/AC mapping, tests, unresolved blockers and next step.

## Hard build barrier

The preflight found that `tauri_build::try_build`/Tauri build machinery writes generated files into the source tree and that no trusted sidecar input is present in the fixed baseline. **Do not run Cargo, Tauri or sidecar builds in this Owner worktree.** Wait for Codex to register an exact scratch worktree/output allowlist, synthetic or trusted sidecar source, and commands, followed by independent DeepSeek Harness review. A normal browser, Vite, JSDOM, SSR, mock IPC, old executable or fake timers cannot be presented as real WebView2/Core evidence. AC4 may use IPC/Core mocks only when explicitly labeled `REAL_WEBVIEW_MOCK_IPC`; it does not prove SQLite/Core persistence.

Do not stop after a plan alone: complete all safe no-build work within the released scope, retain recoverable checkpoints and provide a real Handoff tied to commits. Do not mark the Task `done`; formal Review and Codex integration gates remain required.
