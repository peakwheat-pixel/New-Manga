# T3.1.1 Release Gate — Storage Convergence

Date: 2026-09-22 (Asia/Shanghai)
Decision: **PASS TO START**
Task: [T3.1.1](../../doc/tasks/T3.1.1.md)
Owner: Codex
Independent reviewer: DeepSeek Harness
Base: `e771179` (`master`)
Implementation branch: `agent/codex/T3.1.1-storage-sqlite` (to be created)
Implementation worktree: `G:/CODEX/New Manga.worktrees/T3.1.1-codex-storage-sqlite` (not created at gate time)

## Gate conclusion

The task is independently scoped and ready to start. The gate releases only the
implementation work described below. It does not claim that the migration,
adapters, tests, Review, or integration already exist.

## Preconditions checked

- At Gate creation, `e771179` was the current mainline governance head; product
  code remains at the already integrated T2.2.1 head `fe9fca0`.
- T2.2.1 is `VERIFIED_COMPLETE` with focused integration evidence; the known full
  suite torch environment failure remains an environment limitation and is not a
  T3.1.1 blocker.
- TASK-057 is integrated and its backup/recovery evidence is present. T3.1.1
  reuses existing migration backup/restore semantics and does not wire backup UI.
- Current SQLite schema is v3. `ReadingService` is constructed with
  `JsonProgressDocumentStore(data_root / "reading_progress.json")`; `ExportService`
  is constructed with `JsonHistoryDocumentStore(data_root / "export_history.json")`.
- Existing main-worktree changes and untracked paths are preserved and excluded
  from this Task; no cleanup, reset, or overwrite is authorized.

## Frozen scope

In scope:

- one additive SQLite migration after v3 for ReadingProgress and ExportHistory;
- SQLite adapters behind the existing application store ports;
- one-time import of valid legacy JSON with durable import markers;
- strict/non-destructive handling of malformed legacy input;
- production bootstrap injection and focused regression/failure evidence;
- Handoff, DeepSeek Harness independent Review, and Codex integration records.

Out of scope:

- TASK-028 Library/Page/Region implementation;
- edits to v1/v2/v3 migration SQL;
- Pipeline graph/handlers, Provider/credential, QML/UI, packaging, backup UI;
- user source files, Managed Copy, Lock/current/pinned Revision semantics;
- new dependencies or deletion/replacement of legacy JSON files.

## Required invariants

1. Existing `ReadingProgress` and `ExportRecord` fields round-trip without changing
   service behavior. Original and Translated remain independent; Webtoon offsets and
   duration survive restart.
2. `(book_id, chapter_id, mode)` is unique for progress. Export history preserves
   all terminal statuses, snapshots needed by repeat, and newest-first history.
3. Valid legacy documents import once. Missing files represent an empty legacy
   store. A present malformed document is preserved and produces a typed,
   diagnosable migration failure; it is never silently discarded or marked imported.
4. After successful import, SQLite is the only production write truth. Legacy JSON
   remains untouched recovery material; no write path uses `os.replace` on those two
   files.
5. Database writes and imports have explicit short transaction boundaries. Failure
   leaves no partial rows and never modifies the legacy files or user source data.
6. Migration remains additive, checksum-protected, backup-compatible, and rejects
   databases newer than the known schema.

## Required evidence before integration

- migration tests from empty/v3 databases, including failure rollback and newer-schema
  rejection;
- progress/history adapter round-trip, restart, uniqueness/order, and failure tests;
- valid/missing/malformed/duplicate-prevention legacy import tests with file hash/mtime
  assertions;
- real production assembly probe proving both services use SQLite and no longer write
  the legacy JSON paths;
- focused suite, full suite, compileall, bootstrap smoke, `git diff --check`, and
  exact shell/venv/test-result headers;
- Codex Handoff bound to the delivery head;
- DeepSeek Harness independent Review bound to the same base/head and reporting
  Architecture, Verification, data-loss and allowed-path findings;
- Codex integration evidence after an `approved` Review.

## Gate audit trail

Read-only audit commands used before this Gate:

```text
PowerShell, repo: G:\CODEX\New Manga
git rev-parse --short HEAD                         => e771179
git branch --show-current                          => master
git status --short                                 => existing dirty/untracked paths only; preserved
rg JsonProgressDocumentStore src tests             => JSON progress store and current bootstrap call site
rg JsonHistoryDocumentStore src tests              => JSON history store and current bootstrap call site
rg SCHEMA_VERSION_V3 default_migrations src       => SQLite highest known schema is v3
```

Observed source facts are recorded here as As-Is evidence, not as an acceptance
result. All implementation test rows remain `NOT_RUN` until a delivery head exists.

## Gate ownership

Codex may now create the isolated worktree and implement T3.1.1. DeepSeek Harness
must remain independent and cannot review an implementation it authored. No
downstream T3.2.1 release is permitted until this Task reaches
`VERIFIED_COMPLETE`.

## Reassignment addendum — 2026-09-22

Per the user's explicit reassignment, implementation ownership is now
**Antigravity**. Codex remains Lead / Architect / Integrator and DeepSeek Harness
remains the independent non-author Reviewer. The original Gate base and frozen
scope are unchanged.

The released implementation worktree was created from `e771179` with:

```text
branch: agent/antigravity/T3.1.1-storage-sqlite
worktree: G:/CODEX/New Manga.worktrees/T3.1.1-antigravity-storage-sqlite
HEAD: e771179
status: clean
```

The prior Codex worktree is preserved but is no longer the active implementation
workspace. No product code or database was changed by this reassignment.
