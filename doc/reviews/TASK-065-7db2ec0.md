---
task_id: TASK-065
reviewer: Codex independent review agent (non-author)
author: Codex implementation agent
base_commit: 772d63c2c921a08606d742438a146cb310159b02
reviewed_head: 7db2ec0c8b8f60f81e37d4c07f981e0c04ebd735
delivery_head: 367eeae92a6a680019e3d1737aab477b180e3f7a
decision: approved
---

# Review: TASK-065 re-review

## Scope and basis

Reviewed fixed range `772d63c2c921a08606d742438a146cb310159b02...7db2ec0c8b8f60f81e37d4c07f981e0c04ebd735`, with implementation/evidence-tested delivery `367eeae92a6a680019e3d1737aab477b180e3f7a`. Sources: `REBASELINE_PLAN.md` T1.3.2, TASK-065 AC1-AC5, TASK-058 Review F-002/F-003/F-005/F-006, first Review `TASK-065-c5f8217.md`, the new Handoff, the complete diff, affected shutdown call chain, and committed verification artefacts.

## Standards (executed)

No documented-standard violation or Fowler smell was found. Every changed path is allowed by TASK-065. Production changes are limited to the authorized `AppServices.conn` annotation and adjacent docstring; no product behavior, Schema, dependency, QML, storage, cleanup, or unrelated Task changed. Task state, Handoff, and evidence now agree.

## Spec (executed)

AC1-AC4 are satisfied. The injected executor callback cannot return until shutdown sets `run.cancel_requested` (or the bounded five-second guard fails the test), so `_shutdown_services` necessarily begins while the worker is executing. Existing postconditions remain: controller drained, cancellation observed, run terminal, and the SQLite facade closed. AC5 has the required 951 collected tests, no added skip/xfail, a Handoff, and this independent approval; its checkbox correctly remains pending for integrator bookkeeping.

`AppServices.conn: ThreadRoutedConnection` and the per-thread close wording match the actual facade. Removing `assert sys.stderr is not None` and its unused import does not weaken the retained stderr-content assertion.

## First-review finding disposition

| Finding | Disposition | Evidence |
|---|---|---|
| R-001 active-worker proof | **closed** | `wait_for_shutdown` waits for `run.cancel_requested`; pre/post cancellation and drain assertions are explicit. Fresh fixed-head shutdown suites pass. |
| R-002 commit-bound PASS evidence | **closed** | targeted/integration/full logs record `HEAD=367eeae...` with empty `SOURCE_TREE_STATE`. |
| R-003 missing RED artefact | **closed** | `verification/TASK-065/discrimination-red.log` records environment, collection, modified fixture state, the expected active-worker assertion failure, and `EXIT=1`. |
| R-004 stale Task ledger | **closed** | TASK-065 is `in_review`, AC1-AC4/results are updated, Handoff and first Review are linked, and AC5 remains pending until approval bookkeeping. |

## Findings

Within the recorded scope, no new finding remains open.

## Verification

| Scenario | Command/check | Environment/commit | Result | Evidence |
|---|---|---|---|---|
| Active-worker/related shutdown suite | `python -m pytest tests/core/test_shutdown_drain.py tests/workbench/test_drain_shutdown.py -q -p no:cacheprovider -rs` | PowerShell; TASK-012-py312; `PYTHONPATH=src`; `PYTHONDONTWRITEBYTECODE=1`; `QT_QPA_PLATFORM` unset; `7db2ec0` | **PASS: 7 passed / 0 skipped / EXIT=0** | Fresh reviewer run |
| Full regression | `python -m pytest tests -q -p no:cacheprovider -rs` | same environment; `7db2ec0` | **PASS: 945 passed / 6 skipped / EXIT=0**; all six skips are the listed `openssl unavailable` network cases | Fresh reviewer run; delivery evidence in `verification/TASK-065/full-suite.log` records 951 collected at clean `367eeae` |
| Discrimination RED | old fast fixture plus active-worker assertion | recorded `c5f8217` worktree state | **Expected FAIL: 1 failed / EXIT=1** | `verification/TASK-065/discrimination-red.log` |
| Added skip/xfail scan | scan added test lines in fixed diff | `772d63c...7db2ec0` | **PASS: 0 added** | Review command output |
| Path whitelist | compare all changed paths with TASK-065 allowed paths | fixed diff | **PASS: 0 out of scope** | Review command output |
| Diff whitespace | `git diff --check 772d63c...7db2ec0` | fixed diff | **PASS / EXIT=0** | Review command output |

**Architecture:** PASS. The implementation changes no runtime architecture or dependency direction and accurately documents the existing connection facade.

**Verification:** PASS. The regression test now deterministically exercises a live worker at shutdown; RED and clean delivery-head GREEN evidence are reproducible and complete.

## Decision and integration note

**Approved.** Fixed reviewed head `7db2ec0c8b8f60f81e37d4c07f981e0c04ebd735` may proceed to Codex integration. Integration must still update TASK-065/STATUS, record the integration commit, run post-integration regression, and apply the Closure Gate. This approval does not authorize other planned tasks or worktree cleanup.
