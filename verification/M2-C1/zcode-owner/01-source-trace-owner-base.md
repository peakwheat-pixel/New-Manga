# M2-C1 ZCode Owner Verification — 01 Source Trace at Owner Base

Owner: ZCode. Fixed base: `7478f72fe6f9872cae29f4fa12888b5e1f2380f1`.
Adopted draft source head: `ac38dede84ff22290c9b9d579c1372c8184a7bd5`.

The Codex draft Contract anchors every **AS-IS** claim to baseline
`eec1aa49d07119f0aa66ff461ebbb55e4595e624` (the master HEAD at draft Task
registration) with a full trace table in the draft tree
(`ac38dede:verification/M2-C1/source-trace.md`). The Owner base `7478f72…` is a
later commit. This document records, per AC-1, the Owner's re-validation that
**every evidence reference used by the Contract resolves identically at
`7478f72…`**, so the draft trace remains valid without modifying the Contract.

## A. Blob identity of all Contract-cited evidence files

`git rev-parse <base>:$f` compared between `eec1aa4…` and `7478f72…`:

| File | blob OID (identical at both baselines) | Result |
|---|---|---|
| `src/application/tasks/projection.py` | `49f11ac8312ff5dbc9831a0da368f20dae44ac04` | SAME |
| `src/application/editing/region_canvas.py` | `806b2874fa130f73d0a2872c5e4f641eb1b5eb39` | SAME |
| `src/application/tasks/service.py` | `42306d9a31e04f3ca91cd612b194bdc70dc97088` | SAME |
| `src/domain/tasks/models.py` | `473b2f9ca1f93065830de1cf7ac8ae98584edaf7` | SAME |
| `src/application/editing/ports.py` | `fa84fa7d0c8731143364bc01ff51670887e60975` | SAME |
| `src/application/editing/service.py` | `741d33fafb9a53ebc32d64406f6b06f2416306d7` | SAME |
| `src/bootstrap/core_assembly.py` | `8d4a04d9665b7ee9a5529e190dee3477c391583f` | SAME |
| `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md` | `8ca8c9c68d5bed0f56e22fd76ebd537728a3526a` | SAME |
| `doc/design/M2-UI1_REACT_FEATURE_PARITY_VISUAL_CONTRACT.md` | `0fb126d0f2a23ce07a2aa3469cd95c0a19d5c0e7` | SAME |

Additionally `git diff --name-status eec1aa4… 7478f72… -- src/application src/domain src/ui`
produced **empty output, exit 0**: no application/domain/UI source change at all
between the draft AS-IS baseline and the Owner base.

## B. Owner spot checks at `7478f72…` (independent of draft/R3 runs)

Each check below was executed by ZCode directly against the Owner base and
compared against the corresponding Contract claim:

| Contract claim (section) | Check at `7478f72…` | Result |
|---|---|---|
| §7.1 Run state values | `src/domain/tasks/models.py:91-99`: `PipelineRunStatus` = pending, running, paused, blocked, completed, completed_with_failures, failed, cancelled, interrupted — 9 values, verbatim equal to Contract §7.1 | PASS |
| §9 half-up conversion | `src/application/editing/region_canvas.py:40-41`: `_to_pixels = min(size, max(0, math.floor(axis * size + 0.5)))` — pixel-space half-up then clamp to `[0,size]`, exactly as Contract §9/§3.1 state | PASS |
| §9 typed geometry errors | `normalized_to_page_geometry` validates positive page size and ≥2 points; typed `RegionCanvasError` with stable `.code` (R3 evidence `06` covered the full code set: `PAGE_SIZE_UNAVAILABLE`, `TOO_FEW_POINTS`, `DEGENERATE_GEOMETRY`) | PASS |
| §5 / R-008 attribution | `src/application/editing/ports.py:30`: `def list_revisions(self, region_id: str) -> list[RegionRevision]` on `RegionRepository` port; editing service defines `restore_revision` / `set_revision_pinned` (R3 evidence `05` counted service `list_revisions` definitions = 0) | PASS |
| §6.1 projection fields | `src/application/tasks/projection.py:82-92`: `PageProjectionRow` = page_id, page_order, filename, status, is_locked, is_pipeline_current, error_code (7 row fields, equal to Contract §6.1 rows mapping); `:96-119` `TaskProjection` dataclass field lines counted by ZCode = **23**, equal to R3's count and to the Contract §6.1 mapping table (6+1+1+7+1+6+1) | PASS |
| §6.1/§7.1 lifecycle authority | `src/application/tasks/service.py:829`: `def control_run(self, run_id: str, action: str) -> ControlResult`; `:832` pause gate `status not in {PENDING, RUNNING}`; `:886`: `def recover_running_runs`; `:903`: `def retry_failed_targets` with `raise PipelineError("TARGET_NOT_FOUND", …)` on no failed pages | PASS |
| §10 large-media prohibition | `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md:33` reads `4. **Large binary boundary.** Large comic images, Webtoon assets and model weights must not traverse ordinary JSON IPC or Base64 IPC…` verbatim | PASS |
| §10 data-protection invariants | `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md:35` reads `6. **SQLite authority.** Python Core alone owns persistent state writes. IPC contracts must preserve source-file safety, Managed Copy, human edits, Lock, current/pinned Revision and recoverable task state.` verbatim | PASS |
| §5 Settings row honesty | `git grep -c 'CredentialRef' 7478f72… -- src/` → **exit 1 (zero hits)**; Contract correctly marks credential DTO/exchange `UNKNOWN / DEFERRED` instead of inventing a type | PASS |
| §2 Qt-free seam | `src/application` / `src/domain` / `src/ui` blob-identical between both baselines (section A); R3 evidence `07` verified no PySide6/`src.ui` imports in `projection.py` / `region_canvas.py` on the identical blob content | PASS |

## C. Coverage of the dispatch-mandated topics

Mapping of the mandated topic list to Contract sections and their evidence class
(all resolve at `7478f72…` per sections A/B above):

| Topic | Contract section | Evidence class |
|---|---|---|
| Python Core = business & persistence authority; SQLite single writer | §1, §2, §10 | TO-BE (AD-001:17-36, :35) + PROPOSAL boundary restatement |
| Command / query / event / projection & resource boundaries | §4, §5, §5.1, §5.2, §6 | PROPOSAL (wire) over AS-IS service existence |
| Types, version & capability negotiation | §3, §3.1, §3.2 | PROPOSAL; handshake itself AS-IS NOT_IMPLEMENTED / UNKNOWN |
| Errors (typed envelope, source code preservation) | §8 | PROPOSAL over AS-IS observed codes (`INVALID_RUN_TRANSITION`, `RUN_NOT_INTERRUPTED`, `TARGET_NOT_FOUND`, `RegionCanvasError.code`) |
| Task lifecycle / progress / cancel / recovery | §7.1, §7.2 | AS-IS state machine (`control_run`, `recover_running_runs`) + PROPOSAL transport lifecycle, startup handshake UNVERIFIED |
| Resource lifecycle & safety boundary | §10 | TO-BE invariants (AD-001) |
| Source file / Managed Copy / human edits / Lock / current & pinned Revision / recoverability protection | §10 | TO-BE invariants; specific wire conflict token UNKNOWN |
| Page-level `blocked` vs Run status domains | §7.1, §11 | AS-IS two distinct status domains; UI mapping DEFERRED / USER_DECISION_REQUIRED |
| Large-media channel | §10, §11 | Prohibition TO-BE; selection DEFERRED to independent Spike |

## D. Draft trace equivalence statement

The draft `source-trace.md` remains the historical Owner-of-record trace for the
draft head; it is not copied into this Owner delivery because the allowed Owner
paths are limited to `verification/M2-C1/zcode-owner/**`. Its evidence column
remains valid at `7478f72…` because every `src/**` and cited `doc/**` file it
references is blob-identical between the two baselines (section A), and because
the only divergent file (`src/bootstrap/app.py`, see `05-drift-and-links.md`)
is cited by it only for the role statement "`src/bootstrap/app.py` remains Qt
entry", which remains true at `7478f72…` (the change adds PyInstaller frozen
resource-root resolution only; the module is still the Qt/QML application entry).

Product pytest / GUI / IPC runtime checks: **NOT_RUN** (document-only Task; no
product test was added or executed by ZCode).
