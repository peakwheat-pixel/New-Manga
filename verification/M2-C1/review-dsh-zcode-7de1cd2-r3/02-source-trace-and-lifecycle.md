# M2-C1 ZCode Owner Delivery — DSH independent Review r3: source-trace and lifecycle re-verification

Reviewer: DeepSeek Harness (non-author). All facts below were re-derived by this Review
from the fixed objects; none is copied from the Owner or from Qoder conclusions.

Environment: PowerShell 7 (`pwsh`), Python 3.14.6, git 2.52.0.windows.1.
Probe scripts and their verbatim output are committed next to this file:
`probe-source-trace-recount.py` / `02-source-trace-recount.log`,
`probe-lifecycle-lines.py` / `03-lifecycle-lines.log`.

## 1. Blob identity of all nine Contract-cited evidence files

`git rev-parse <base>:<path>` compared across three revisions
(`eec1aa4…` = draft AS-IS baseline, `7478f72…` = Owner base, `7de1cd2…` = Owner Delivery):

| File | eec1aa4 | 7478f72 | 7de1cd2 | SAME (all three) |
|---|---|---|---|---|
| `src/application/tasks/projection.py` | `49f11ac8` | `49f11ac8` | `49f11ac8` | YES |
| `src/application/editing/region_canvas.py` | `806b2874` | `806b2874` | `806b2874` | YES |
| `src/application/tasks/service.py` | `42306d9a` | `42306d9a` | `42306d9a` | YES |
| `src/domain/tasks/models.py` | `473b2f9c` | `473b2f9c` | `473b2f9c` | YES |
| `src/application/editing/ports.py` | `fa84fa7d` | `fa84fa7d` | `fa84fa7d` | YES |
| `src/application/editing/service.py` | `741d33fa` | `741d33fa` | `741d33fa` | YES |
| `src/bootstrap/core_assembly.py` | `8d4a04d9` | `8d4a04d9` | `8d4a04d9` | YES |
| `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md` | `8ca8c9c6` | `8ca8c9c6` | `8ca8c9c6` | YES |
| `doc/design/M2-UI1_REACT_FEATURE_PARITY_VISUAL_CONTRACT.md` | `0fb126d0` | `0fb126d0` | `0fb126d0` | YES |

The Owner's `01-source-trace-owner-base.md` §A table is independently reproduced
(exact 40-hex OIDs match its abbreviated values).

## 2. TaskProjection field count (§6.1 claim = 23)

`src/application/tasks/projection.py` at the fixed base:

```text
class TaskProjection at line 96
field count = 23
   97: run_id                      104: rows                    111: processing_page_count
   98: run_status                  105: total_page_count       112: blocked_reasons
   99: run_title                   106: completed_page_count   113: can_pause
  100: overall_progress            107: failed_page_count      114: can_stop
  101: current_page_id             108: skipped_page_count     115: can_continue
  102: current_step_type           109: blocked_page_count     116: can_restart
  103: step_flow                   110: waiting_page_count     117: can_abandon
                                                              118: can_retry_failed
                                                              119: extra
```

23 fields, each one accounted for by the Contract §6.1 mapping table
(6 named scalars + 1 step_flow + 1 rows + 7 counts + 1 blocked_reasons + 6 controls + 1 extra
= 23). The Owner/R3 count is independently confirmed.

## 3. Run lifecycle §7.1 line-by-line

`src/application/tasks/service.py` at the fixed base:

| Contract §7.1 claim | Independently observed | Verdict |
|---|---|---|
| `pause` only from `pending`/`running`; sets and persists `pause_requested=True`; pending -> `paused` synchronously | `:829 def control_run`; `:832` guard `status not in {PENDING, RUNNING}` -> `INVALID_RUN_TRANSITION`; `:834 run.pause_requested = True`; `:835-836` PENDING -> PAUSED; `:837 self._persist(run)` | PASS |
| `stop` rejects terminal runs; pending/paused cancel immediately | `:841` rejects COMPLETED / COMPLETED_WITH_FAILURES / FAILED / CANCELLED; `:843 run.cancel_requested = True`; `:844-846` PENDING/PAUSED -> CANCELLED via `_cancel_pending_tasks` | PASS |
| `continue`: paused -> pending; interrupted re-plans; else `INVALID_RUN_TRANSITION` | `:851-855` PAUSED -> PENDING with `pause_requested=False`; `:856-860` INTERRUPTED -> `plan_run(run_id, mode="continue")`; `:861` otherwise raises `INVALID_RUN_TRANSITION` | PASS |
| `restart` only from interrupted, creates a new run with `source_run_id` and `retry_reason`, marks the old run | `:864-865` non-INTERRUPTED -> `RUN_NOT_INTERRUPTED`; `:866-871 create_run(..., source_run_id=run.run_id, retry_reason="restart_after_interruption")`; `:872 run.interruption_disposition = "restarted"` | PASS |
| `abandon` only from interrupted; old run -> `cancelled` with `termination_reason="abandoned_after_interruption"`; does **not** set `interruption_disposition` | `:877-878` non-INTERRUPTED -> `RUN_NOT_INTERRUPTED`; `:879 status = CANCELLED`; `:880 termination_reason = "abandoned_after_interruption"`; no `interruption_disposition` assignment in that branch | PASS |
| `retry_failed_targets` creates a linked new run; no failed page -> `TARGET_NOT_FOUND` | `:903 def retry_failed_targets`; `:905-911` collects FAILED PAGE targets; `:912-913 if not failed_pages: raise PipelineError("TARGET_NOT_FOUND", "run has no failed page targets")`; `:914-916 create_run(..., PAGE_SELECTION, selected_ids=failed_pages)` | PASS |
| `recover_running_runs` turns persisted RUNNING runs/tasks/steps into `interrupted` and saves | `:886 def recover_running_runs`; `:890-892` RUNNING -> INTERRUPTED; `:893-895` RUNNING tasks -> INTERRUPTED; `:896-898` RUNNING steps -> INTERRUPTED; `:899 self._persist(run)` | PASS |
| `PipelineRunStatus` has the nine cited values, verbatim | `src/domain/tasks/models.py:90-99` = pending, running, paused, blocked, completed, completed_with_failures, failed, cancelled, interrupted | PASS |

Run-level `blocked` and the separate Task/Page status domain are therefore genuinely two
different value domains, as §7.1 and §11 assert.

## 4. Region geometry §9 half-up + clamp

`src/application/editing/region_canvas.py:40-41` at the fixed base:

```python
def _to_pixels(axis: float, size: int) -> int:
    return min(size, max(0, math.floor(axis * size + 0.5)))
```

Pixel-space half-up rounding followed by a clamp to `[0, size]`, exactly as Contract
§3.1/§9 state; no pre-clamp of the normalised input to `[0,1]`. PASS.

## 5. Port attribution §5 / R-008

| Claim | Observed at fixed base | Verdict |
|---|---|---|
| `list_revisions` belongs to the `RegionRepository` port | `src/application/editing/ports.py:30 def list_revisions(self, region_id: str) -> list[RegionRevision]` | PASS |
| the editing *service* does not define `list_revisions` | `git show <base>:src/application/editing/service.py` -> `def list_revisions` matches = **0** | PASS |
| the service exposes `restore_revision` / `set_revision_pinned` | `:550 def restore_revision`, `:574 def set_revision_pinned` | PASS |
| the service delegates to the port | `:131 (rev.revision_no for rev in self._repo.list_revisions(region.region_id))` | PASS |

## 6. Credential honesty §5

```text
$ git grep -c CredentialRef 7478f72fe6f9872cae29f4fa12888b5e1f2380f1 -- src/
exit 1  (zero hits)
```

The Contract marks the credential DTO/exchange `UNKNOWN / DEFERRED` instead of inventing
a type. PASS.

## 7. Command catalogue §5.1

`CommandType` member enumeration at the fixed base = 18 values; the Contract §5.1 wire
enum list = 18 values; set difference in both directions = empty. The wire enum is
therefore a faithful restatement of the existing Core enum, not an invented one. PASS.

## 8. AD-001 citations §2 / §10

At the fixed base:

```text
AD-001:15  ## TARGET_INTENT and decision
AD-001:19  | Boundary | Authority and responsibility | Exclusions |
AD-001:21  | React + TypeScript | ... No direct SQLite access, OCR execution or domain logic. |
AD-001:22  | Tauri / Rust | ... Rust carries no domain business logic and is not a DB writer. |
AD-001:23  | Python Core | ... SQLite persistence, ... task, revision and lock authority. |
AD-001:24  | SQLite | ... React and Rust cannot become independent DB writers. |
AD-001:33  4. **Large binary boundary.** Large comic images, Webtoon assets and model
           weights must not traverse ordinary JSON IPC or Base64 IPC...
AD-001:35  6. **SQLite authority.** Python Core alone owns persistent state writes. IPC
           contracts must preserve source-file safety, Managed Copy, human edits, Lock,
           current/pinned Revision and recoverable task state.
```

Contract §10's "AD-001 large-binary boundary" and "SQLite authority" statements reproduce
the source lines verbatim; the §2 "TARGET_INTENT and decision" table citation and the
"Migration constraints item 6 (line 35)" citation are both exact. PASS.

## 9. Qt-signal and Qt-coupling citations

```text
$ git grep -nE "runStatusChanged|runFinished|taskProgressChanged" b237728 -- src/
src/ui/viewmodels/workbench/run_controller.py:56   runFinished = Signal(str, str)
src/ui/viewmodels/workbench/viewmodel.py:70        taskProgressChanged = Signal()
src/ui/viewmodels/workbench/viewmodel.py:71        runStatusChanged = Signal()
src/ui/viewmodels/workbench/viewmodel.py:78        runFinished = Signal(str, str)

$ git cat-file -e HEAD:src/application/export/pdf_qt.py    -> exit 0
```

The four §6.2 event rows describe real existing Qt signals, the Contract labels the IPC
events as un-implemented, and the admitted `pdf_qt` Qt-coupling exception named in §2
exists at the reviewed head. PASS.

## 10. Product tests

No product test was added or executed by this Review:
pytest / GUI / IPC runtime / serialisation / large-media capacity = **NOT_RUN**
(document-only Task; see 07-notrun-register.log).
