# T3.1.1 Implementation Plan: Unify Reading Progress and Export History into SQLite

## Gate status

Release Gate **PASSED TO START** on 2026-09-22. This is a planning artifact;
no product code or database has been changed by the gate.

## Objective

Move the two currently JSON-backed document stores used by `ReadingService` and
`ExportService` into the existing SQLite database with one additive migration,
one-time safe legacy import, transactional writes, restart recovery, and no
loss or mutation of user data.

## Execution sequence

1. Create the Antigravity worktree from base `e771179` and record its exact path.
2. Add only the next SQLite migration and the smallest adapters that preserve the
   existing application ports. Reuse `application_metadata` for one-time import
   markers unless a smaller v4 mechanism is required by the implementation.
3. Implement strict, non-destructive legacy import for
   `reading_progress.json` and `export_history.json`. Keep the source files as
   read-only recovery material; never delete or replace them.
4. Switch the production bootstrap to the SQLite adapters and add discriminating
   tests for both isolated adapters and the real production assembly.
5. Run the focused suite, migration/import failure probes, compile and bootstrap
   smoke checks. Write the Handoff with fixed commit and all command headers.
6. Stop for DeepSeek Harness independent Review. Resolve findings on a new head,
   then let Codex integrate only an approved head and record final evidence.

## Non-goals

Do not implement TASK-028 Library/Page/Region work, wire backup UI, change
Pipeline/Provider/QML behavior, alter v1–v3 migrations, add dependencies, or
delete legacy JSON files.

## Definition of done

The formal Task remains `ready` until implementation, independent Review and
Codex integration evidence are complete. T3.2.1 is not released by this plan.
