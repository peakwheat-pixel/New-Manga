# Integration record — M2-P1 Regionless Detection Fan-out and Guard Rebinding

- **Merge:** `a174fb9cb5ed221441527165e79d98db7b414a10` (parents `d268a170` + Owner tip `59acb340318359b6c94278c968edcafb125268c1`); strategy `ort`, no conflicts; 5 paths (1 modified product file, 1 new test file, 3 docs/evidence).
- **Fixed base:** `338266417437e3007345aaa8496c5e936745dfd6`; release commit `0a5348b34f0600a224b252c925f497b82d410659`; Owner branch `agent/antigravity/M2-P1-regionless-region-rebinding` preserved at tip; worktree `G:/CODEX/New Manga.worktrees/M2-P1-agy` preserved.
- **Integrator:** Codex role executed by ZCode session acting as Codex (user full authorization 2026-09-28).

## Head ledger (DSH P2 #1 disposition)

| Head | Meaning |
|---|---|
| `33826641` | fixed base (code freeze point) |
| `0a5348b3` | release commit (Task file + governance; code-identical to base) |
| `12961a81` | fix commit: `_backfill_detected_regions` rebinds `target_id`+`region_id` (+15/-2 incl. docstring) |
| `78e9637f` | **code/test head**: + `tests/pipeline/test_regionless_rebinding.py` (729 lines, R0–R5, N1–N7) |
| `59acb340` | **Owner tip (5-path delivery)**: adds only `doc/tasks/M2-P1.md` status advance, `doc/handoffs/M2-P1-78e9637f.md`, `verification/M2-P1/evidence-78e9637f.md` |
| `a174fb9c` | integration merge |

`78e9637f..59acb340` verified to contain exactly the three doc/evidence paths above — zero `src/**`/`tests/**` changes (git `--name-status` recorded 2026-09-28). The `78e9637f` head recorded inside the Owner's Handoff/evidence refers to the code/test head; this record supersedes with the full ledger.

## Verification (independent replays, all `EXIT` per Task AC5)

- Owner (Antigravity, at `59acb340`): pytest trio **21 passed** EXIT=0; `reproduce.py` NOT_REPRODUCED **EXIT=1**; `git diff --check` EXIT=0. Logged in Owner evidence.
- Integrator (at `59acb340` before review): same three commands re-run independently — 21 passed EXIT=0; NOT_REPRODUCED with real process exit code **1**; diff --check EXIT=0.
- Integrator (at integration head `a174fb9c`, this record): pytest trio **21 passed** EXIT=0; `reproduce.py` **EXIT=1** (NOT_REPRODUCED — the AC4 strong discriminator; the positive-shape evidence in the Owner's log rules out a vacuous pass); `git diff --check 33826641..HEAD` EXIT=0.

## Review

- DeepSeek Harness non-author [review](../../../doc/reviews/M2-P1-59acb340-dsh.md): **`approved_with_conditions`** — 0×P0/P1, 1×P2 (head-ledger alignment: disposed above), 8×P3 observations. Four axes judged: fix semantics correct (full rebind, not half-fix), test discrimination strong (R0/R1/N1/N7 spot-checked), scope clean (+13 lines confined to the target function), regression risk closed (`commit_step_result` lands on the Region branch; no consumer parses targets out of `unit_id`).
- P2 #1 (head ledger): **fixed** in this record and in `doc/tasks/M2-P1.md`.
- P3 dispositions (all recorded, none blocking): P3-1 `handle_term_extract` `book_id` mismatch on regionless first run — pre-existing on the has-Region page-scope path, no functional impact today (no tm_store in production assembly), **recorded as input to the future fan-out/scheduling slice**; P3-2 `expected_revisions/expected_lock` remain Page-shaped after rebind (audit-only fields, never guard inputs) — cleanup candidate for the same slice; P3-3..P3-8 (proxy-level R2 assertion, R3 failure-step identity, N1 half-fix counter-case, cold-reload coverage, docstring wording, AC4 wording) accepted as-is per Task AC wording.

## Scope audit

- Owner delta `0a5348b3..59acb340`: 5 paths, all inside the Task allowlist; `src/application/tasks/service.py` net +13 lines entirely inside `_backfill_detected_regions`; zero changes to contracts, schema, dependencies, packaging, Legacy QML; multi-Region fan-out scheduling untouched (primary-only semantics preserved per diagnosis §5.2).
- The defect from [DIAG-M2-REGIONLESS-LOCK-CHANGED-001](../../research/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md) is closed: regionless `detect → backfill → ocr` now commits the OCR revision against the primary Region (2 revisions, `current_revision_id` advances) instead of failing `LOCK_CHANGED`.
