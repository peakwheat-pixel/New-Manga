# DSH r2 findings disposition — M2-PACKAGED-AC1-ICU-ISOLATION-FIX

- DSH decision: `APPROVED` (0 P0/P1), reviewed code head `4499217d7b2249da16d5dbf27a3219a43876aac7`.
- Owner evidence commit: `2c79645939635beef4a391f4bd9071ffeacd300b`.
- DSH report: `doc/reviews/M2-PACKAGED-AC1-ICU-ISOLATION-FIX-4499217d-dsh-r2.md`.
- DSH did not run product tests. Existing Gate results remain the Owner's fresh runs at `4499217d`; this disposition does not claim a rerun.

| Finding | Disposition | Evidence / rationale |
|---|---|---|
| R2-001 (P2) | CLOSED | Codex ran and archived the exact base-to-code `git diff --name-only`, forbidden path classification, and `git diff --check` in `r2-codex-scope-validation.log`; no `src/`, `apps/`, `tests/`, dependency, schema, or migration paths occur. |
| R2-002 (P3) | ACCEPTED WITH LIMITATION | The delivered fresh build had zero ICU candidates for the spec classifier, so candidate classification branches have static-review evidence only. Unknown external sources fail closed and the final recursive bundle gate passed. No production guard/logging change was made after the approved fresh build. |
| R2-003 (P3) | ACCEPTED WITH LIMITATION | The one-time raw scan records 313 PE files and its five entry hashes match `build-fingerprint.json`; it lacks its own timestamp/interpreter/head fields and has a hard-coded summary count. Treat the raw scan as evidence for this fixed bundle only; improve metadata before reusing the scanner for another bundle. |
| R2-004 (P3) | CLOSED | `REPORT.md` now says 542 is the System32 ICU export total and identifies the 20 Qt6Core-required `ucnv_*` symbols separately. |
| R2-005 (P3) | CLOSED | Task and Handoff specify that CS-Z3 asserts four sidecar process counts are zero; `python.exe: 6` is a recorded observation, not a zero-residue assertion. |
| R2-006 (P3) | CLOSED | The original r1 report is retained at `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/review-dsh-r1.md` on the current mainline; r2 report is recorded under `doc/reviews/`; Task, Handoff, and `REPORT.md` identify the exact Owner evidence commit. |

No production code changed after `4499217d`. The two accepted limitations are non-blocking and remain explicit; they do not convert unknown runtime behavior into a PASS.