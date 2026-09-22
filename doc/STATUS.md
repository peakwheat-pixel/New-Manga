# Current Development Status

Planning source of truth: [Project Rebaseline Plan](REBASELINE_PLAN.md)

Execution checkpoint: 2026-09-22 (Asia/Shanghai)

| Field | Current value |
|---|---|
| Latest product integration | `f56f441c1ce981ff83a3af98c5862917e35711f1` (T1.1.1 product merge) |
| Branch | `master` |
| Mainline base checked before this audit/control baseline | `4dfe9e7850c370634a293118536672e5f91680f8` (R4 scope release; no T1.2.1 product merge). Read live HEAD with `git rev-parse HEAD`. |
| Current milestone | **M1 — Alpha Core Loop Closure** |
| Stage | **Stage B — Controlled Execution** |
| Current product checkpoint | `T1.2.1 — R4 REVIEWED / INTEGRATION BLOCKED ON B-003 / NOT INTEGRATED`; T1.1.1 and T1.1.2 are `VERIFIED_COMPLETE`. |
| Current Active Task | T1.2.1 B-003 follow-up is pending ZCode delivery; no product implementation or integration is authorized outside the bounded scope in the review. |
| Current owner/reviewer | T1.2.1 R4 candidate: ZCode; non-author reviewer/integrator: Codex. R4-B001/B002/B004/B005 resolved; B-003 remains BLOCKING. |
| Current branch/worktree | Author: `agent/zcode/T1.2.1-settings-ui-viewmodel` / `G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`; isolated Codex candidate: `agent/codex/T1.2.1-integration` / `C:\Users\49745\.codex\worktrees\t121-codex-integration\New Manga` (not merged). |
| Current review base/head | base `d11d927`; R1 `c54f360` / `ace633a`; R3 `d978d6f` / `7376bce`; R4 candidate `39dbbf7` / `a527b85`; isolated Codex candidate `0b4e434` is not integrated. |
| Latest integrated product test status | T1.1.1 integration: Python 3.12 implementation venv, `1077 collected = 1070 passed + 6 skipped + 1 known environment failure`, exit 1. The failure is the model-runtime readiness assertion; six skips are OpenSSL-unavailable TLS cases. T1.2.1 candidate results are recorded in its review, not claimed as mainline verification. |
| Smoke status | `python -m bootstrap.app --smoke-test --data-root <temp>` exit 0; SQLite and managed directory created. |
| Compile status | `python -m compileall -q src tests` exit 0. |
| Current blockers | No T1.1.1 integration blockers. T1.2.1 R4 non-author review resolved four R3 seams, but B-003 production transport credential injection is not implemented; integration and final verification are withheld. The single `SettingsView.qml` filter is explicitly reconciled into R4 scope; other QML remains forbidden. Deferred outside this Task: known model-runtime readiness assertion and export signal race. Graphite F is not applied to production QML; reading/export history remain JSON-backed; packaging and clean-machine gate are absent. |
| Pre-reconciliation dirty main-worktree files | Preserve `experiments/TASK-017/README.md` (tracked modification) and untracked `.codewiki/`, `.qoder-credits/`, `docs/`, `material/`, `wiki/codewiki/temp/`. Recheck `git status` before any edit; current documentation edits are separate. |
| Worktrees | Existing inventory is a 2026-09-20 conservative snapshot. Old `TASK-013-qoder` is clean but based on pre-Stage-A history and contains prior Qoder work; preserved, not selected. T1.1.2 worktree is clean at `5b91745`. No deletion or prune is authorized. |
| Evidence | [Project audit](../verification/PROJECT-AUDIT-2026-09-22.md); [T1.1.1 integration](../verification/T1.1.1/integration-f56f441.md); [T1.2.1 R1 review](../verification/T1.2.1/review-c54f360.md); [R3 review](../verification/T1.2.1/review-d978d6f.md); [R4 review](../verification/T1.2.1/review-39dbbf7.md); [R4 probe](../verification/T1.2.1/r4-probe-39dbbf7.log) |

## Verified completed capability

SQLite v2 core persistence, managed copy, image/PDF/picture-MOBI import,
Webtoon tiled reading, scheduler/executor, rendering/export, connection
ownership, diagnostics wiring, four top-level routes, backup/restore service
tests and restore admission/latch tests are present and covered by the fresh
isolated suite. This is implementation evidence, not a claim of real-provider
quality or release readiness.

T1.1.2 manual rectangle/polygon creation, canonical page-coordinate conversion,
real SQLite persistence, revision creation, deletion, Inspector cleanup,
source-file protection, production bootstrap wiring and fresh integration
verification are now complete.

## Open gaps

1. T1.2.1: review the ZCode R4 candidate `39dbbf7`, close B-003 and resolve
   QML allowed-path drift under the frozen [Task](tasks/T1.2.1.md); then Codex
   re-reviews and verifies integration.
2. T2.1.1: apply the selected Graphite Atelier token layer to production QML.
3. T3.1.1: migrate reading progress and export history from JSON to SQLite.
4. T3.2.1: build and verify a product Windows onedir package on a clean machine.

## Stage B execution gate

T1.1.2 and T1.1.1 are integrated and verified. T1.2.1 has been delivered but
its R3 review is blocked. The formal Task freezes R4 revision scope; there is
no current implementation in progress. Do not integrate R3 or release T2.1.1
until R3-B001–B005 are resolved, a fresh non-author review and Codex
integration gate pass. Preserve all dirty files and worktrees. `TASK-013`
remains the historical task; T1.1.2 and T1.1.1 are closed in the current roadmap
state.

## T1.1.1 preparation Release Gate

Codex reviewed the fixed evaluation `base=1fa5f89` → `head=ed607b7` from
`G:\CODEX\New Manga.worktrees\T1.1.1-detector-evaluation`.

- Result: **CONDITIONAL_PASS — implementation scope may be prepared; production
  implementation is not started.**
- Selection: docTR local detection (`fast_base` default proposal); CTD is
  **NO-GO** under the current GPL-3.0 and unverified weight-license chain.
- Verification: the evaluation harness was independently rerun with the
  recorded Python 3.12 environment: `22/22 checks`, exit `0`; the result was
  written outside the repository. Evaluation evidence remains at
  `verification/T1.1.1/`.
- Formal Task: [T1.1.1 Production Text Detector](tasks/T1.1.1.md).
- Release conditions: adapter and merge-policy tests, pinned local weights with
  typed missing-weight failure, harness promotion plus real-page quality pass,
  license/compliance re-check, and explicit CPU/GPU torch packaging choice.
- Historical checkpoint state: Task was `proposed`; no owner/branch/worktree or
  production implementation had been released at that preparation review.
  The current implementation/review state is recorded below.

## T1.1.1 implementation Review checkpoint

Codex independently reviewed ZCode delivery
`4a1ed6ca2778301da983f9f9159210a2fcca6985` against base
`1fa5f893649ec3c9f13f0823aca838548d863393` in
`G:\CODEX\New Manga.worktrees\T1.1.1-production-text-detector`.

- Owner: ZCode; non-author Reviewer/Integrator: Codex.
- Result: **CHANGES_REQUESTED — NOT APPROVED FOR INTEGRATION**.
- Blocking findings: R-001 horizontal merge tolerance is not used; R-002 block
  padding is not clipped to page bounds; R-003 torch is not pinned and CPU/GPU
  environments use different torch minor versions; R-004 compliance re-check
  is not present as reproducible verification evidence.
- Important follow-ups: default weight-fetch destination does not match the
  production default path; merge-policy tests do not cover the critical
  threshold/boundary mutations.
- Fresh evidence: focused CPU `41 passed` and GPU `41 passed`; compileall,
  bootstrap smoke and diff check exit 0. Full-suite failures reproduce in the
  fixed `1fa5f89` control and are recorded as baseline evidence, not as a
  T1.1.1 regression.
- Review report: [T1.1.1 review 4a1ed6c](../verification/T1.1.1/review-4a1ed6c.md).
- Integration: none; master product code remains at the prior integrated
  T1.1.2 state. ZCode must deliver a new head and wait for re-review.

## T1.1.1 R2 Review checkpoint

Codex reviewed ZCode R2 delivery `2f116a2` against base `4a1ed6ca` in
`G:\CODEX\New Manga.worktrees\T1.1.1-production-text-detector`.

- R2 code commit: `2f116a2`; follow-up evidence/Handoff commit:
  `4a631355316e959e9a9704f1ead2eaed39cbf7a3`.
- Result: **APPROVED FOR CODEX INTEGRATION WINDOW**; all six historical
  blockers are fixed and fresh CPU/GPU focused suites are `46 passed` each.
- Fresh full-suite evidence is recorded in
  [review-2f116a2](../verification/T1.1.1/review-2f116a2.md): implementation
  environment `1069 passed, 6 skipped, 2 failed`; baseline environment
  `1043 passed, 11 skipped, 1 failed`. The only product failure is the
  pre-existing export signal race; the other implementation-environment
  failure is the expected model-runtime readiness assertion.
- IMPORTANT deferred findings: correct the stale author pass/skip split in the
  R2 evidence, and assign the export race to a separate export/reading repair
  window. Neither is a T1.1.1 R2 code blocker.
- Integration: none yet; master remains at the prior T1.1.2 product state.
  ZCode must not merge. Codex owns the next serial integration gate.

## T1.1.1 Integration Gate checkpoint

The scope reconciliation was authorized by the user. The isolated candidate
merge at `f56f441` preserves all ZCode commits and includes the required
`src/bootstrap/app.py` detector injection and supporting `tests/**` files.
Fresh focused CPU tests (`46 passed`), bootstrap detection-to-SQLite probe,
bootstrap smoke, compileall, real-material detection, source protection, and
diff check passed. The full suite recorded `1077 collected = 1070 passed + 6
skipped + 1 known environment failure`, exit 1; the failure is the expected
`test_registry_readiness` assertion because this detector venv contains torch.
The historical export signal race remains a separate deferred issue and was
not part of this diff. Full evidence:
[T1.1.1 Codex integration evidence](../verification/T1.1.1/integration-f56f441.md).

## T1.2.1 Non-author Review / Integration Gate checkpoint

Codex reviewed ZCode delivery `c54f360` against base `d11d927` in
`G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`; the author
handoff is `ace633a`.

- Result: **REVIEW_BLOCKED — NOT APPROVED FOR INTEGRATION**.
- Scope: the implementation diff stays within the authorized settings,
  ViewModel, SettingsView.qml, bootstrap and two test paths. The author
  worktree was clean.
- Blocking findings: the UI-created provider profile ID is not resolvable by
  the production registry, and saved network/proxy settings are not applied
  to the provider transport. A minimal provider-to-pipeline mirror repair was
  tested and committed only in isolated Codex candidate `0b4e434`; it was not
  merged to master.
- Fresh evidence: focused candidate tests `161 passed, 6 skipped`, exit 0;
  compileall, bootstrap smoke, source-protection subset, and diff check exit
  0. Full suite `1094 passed, 6 skipped, 1 failed, 1 warning`, exit 1; the
  only failure is the known torch-installed registry-readiness environment
  assertion.
- Evidence: [T1.2.1 review](../verification/T1.2.1/review-c54f360.md) and
  [Codex integration evidence](../verification/T1.2.1/integration-0b4e434.md).
- Status: `T1.2.1 = REVIEW_BLOCKED / IMPLEMENTED_NOT_VERIFIED`. Do not start
  T2.1.1. ZCode must resolve B-001/B-002 and wait for re-review.

## T1.2.1 R3 Non-author Review checkpoint

Codex reviewed the ZCode R3 implementation `d978d6f` against `ace633a` and
the R3 Handoff `7376bce` in
`G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`.

- Result: **CHANGES_REQUESTED — R3 REVIEW_BLOCKED**.
- Scope: `git diff ace633a..d978d6f --stat` contains exactly the six
  authorized R3 paths; QML, `src/ports/**`, SQLite schema, Roadmap and STATUS
  are untouched by the R3 implementation.
- The single-profile happy path is independently reproduced through the
  migrated SQLite row, `_load_pipeline_settings`/
  `_load_pipeline_defaults`, `build_provider_runtime`, fixed registry-slot
  resolution and a recording transport.
- Remaining blocking findings: one profile id cannot alias multiple capability
  slots; `proxy_policy` semantics and missing-network fail-closed behavior are
  not preserved; production `StdlibTransport` lacks the credential store for
  proxy credentials; disabled fixed-slot profiles still resolve; and binding
  does not validate the profile capability declaration.
- Fresh R3 verification in the stated implementation venv: focused
  `410 collected = 403 passed + 6 skipped + 1 failed`, exit 1; full
  `1124 collected = 1117 passed + 6 skipped + 1 failed`, one warning, exit 1;
  compileall, six smoke runs and diff-check exit 0. The single failure is the
  known torch registry-readiness environment assertion; the six skips are
  OpenSSL-unavailable TLS cases.
- Evidence: [R3 review](../verification/T1.2.1/review-d978d6f.md) and
  [R3 edge probes](../verification/T1.2.1/r3-edge-probes-d978d6f.log).
- Status remains `T1.2.1 = REVIEW_BLOCKED / IMPLEMENTED_NOT_VERIFIED`. No R3
  product commit is integrated; do not start T2.1.1.

## T1.2.1 R4 revision Release Gate

Codex has frozen the [formal Task](tasks/T1.2.1.md) after the
[R3 review](../verification/T1.2.1/review-d978d6f.md). This records the next
authorized revision, not a claim that implementation has resumed or passed.

- **Owner / reviewer**: ZCode / Codex (non-author). Original base
  `d11d927a46c9d2350b0e8e8161abb8ff21acba79`; reviewed R3 implementation
  `d978d6f17f52b5b02ce7c2efa434e491e7cc878c`; current author Handoff HEAD
  `7376bce954e700c43a4fed5dbdc43b71580c3fcf`.
- **Recovery**: `agent/zcode/T1.2.1-settings-ui-viewmodel` at
  `G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`, clean when this
  Gate was recorded. Recheck branch, HEAD, dirty state and Git common dir
  before author work; stop on divergence.
- **Allowed**: only the source, test, Task, Handoff and verification paths in
  [T1.2.1 §允许修改范围](tasks/T1.2.1.md#允许修改范围). The current R4
  reconciliation permits only the single `SettingsView.qml` capability filter;
  other QML remains forbidden. `0b4e434` remains an isolated unmerged
  candidate, not the repair base.
- **Exit**: R4 implementation `39dbbf7` and Handoff `a527b85` were reviewed by
  Codex. B-003 is authorized for one narrow follow-up delivery: inject the
  existing credential store into production `StdlibTransport`, add assembly
  evidence and a redacted authenticated-proxy probe. Product integration and
  final verification remain blocked until that delivery passes non-author
  review.

## T1.2.1 R4 non-author review checkpoint

Codex reviewed ZCode implementation `39dbbf7` against the R3 implementation
baseline `d978d6f` and Handoff `a527b85` against `7376bce` in the author
worktree. The author worktree is clean at `a527b85`.

- Result: **R4 EDGE REVIEW APPROVED; INTEGRATION BLOCKED — B-003**.
- The implementation diff contains exactly six paths: registry, runtime,
  Settings ViewModel, the explicitly reconciled `SettingsView.qml` filter,
  and two focused test files. `src/bootstrap/app.py` is unchanged.
- R4-B001 multi-capability aliasing, B002 network policy/fail-closed behavior,
  B004 disabled-slot behavior, and B005 capability validation were reproduced
  by independent runtime probe. Evidence: [R4 review](../verification/T1.2.1/review-39dbbf7.md)
  and [R4 probe](../verification/T1.2.1/r4-probe-39dbbf7.log).
- B-003 remains BLOCKING: production line 642 still constructs
  `StdlibTransport()` without `credential_store`. The existing authenticated
  proxy adapter subset passes, but that is not production bootstrap evidence.
- B-003 is **authorized for the next delivery only**: use the existing
  credential-store seam with best-effort `None` fallback, add an assembly-level
  test and a local redacted authenticated-proxy probe. No ports, schema,
  dependencies or QML redesign are authorized.
- Fresh author-worktree evidence: Git Bash focused `421 passed + 1 known
  torch readiness failure`, full `1135 passed + 1 known failure`; PowerShell
  focused `415 passed + 6 OpenSSL skips + 1 known failure`, full `1129 passed
  + 6 skips + 1 known failure`; compileall exit 0, six smoke runs 6/6, and
  diff-check exit 0. The known failure and environment skips are not reported
  as all-green.
- Status: `T1.2.1 = REVIEW_BLOCKED_B003_PENDING / NOT INTEGRATED`. Do not
  start T2.1.1. Next executor: ZCode for the bounded repair; Codex remains
  non-author Reviewer/Integrator.

## V2 Project Control Dashboard

Detailed evidence and maps are in [PROJECT-AUDIT-2026-09-22](../verification/PROJECT-AUDIT-2026-09-22.md).

| Field | Current value |
|---|---|
| `TaskStatus` | T1.2.1 `review_blocked_b003_pending`; no product commit integrated |
| `ExecutionState` | `WAITING_FOR_B003` on master; R4 edge review is complete, product integration withheld |
| `Current Executor` | ZCode next for bounded B-003 delivery; Codex non-author Reviewer/Integrator |
| `YOU ARE HERE` | T1.1.1 + T1.1.2 integrated → T1.2.1 R4 edge review → B-003 follow-up → T2.1.1 unreleased |
| `Dependency Blocking Chain` | T1.2.1 B-003/scope/review/integration → T2.1.1 → T2.2.1 → T3.1.1 → T3.2.1 |
| `Safe Parallel` | RepoWiki/derived knowledge refresh; isolated research-only work |
| `Conditional` | T3.1.1 design/research after write-set review |
| `Do Not Start Yet` | T2.1.1, T2.2.1, T3.2.1 and any product change outside a released Task |
| `Safe To Resume` | Yes for the authorized T1.2.1 B-003 follow-up; no integration or T2.1.1 until fresh gates close |
| `Latest audit checkpoint` | `verification/PROJECT-AUDIT-2026-09-22.md`; control baseline `25bff3c`; source baseline `4dfe9e7` |

### Current position map

```text
T1.1.2 VERIFIED_COMPLETE
        ↓
T1.1.1 VERIFIED_COMPLETE @ f56f441
        ↓
T1.2.1 R4 candidate @ 39dbbf7 / a527b85 (not integrated)
        ↓
Codex non-author review + B-003 + scope gate
        ↓
T2.1.1 (not released)
```

### Parallel execution matrix

| Work item | Readiness | Class | Conflict |
|---|---|---|---|
| T1.2.1 R4 | conditional | `DO_NOT_PARALLEL` with T2.1.1 | provider runtime, VM, Settings QML, bootstrap |
| T2.1.1 | not ready | `DO_NOT_START_YET` | four-page QML/theme and T1.2.1 contract |
| T3.1.1 research | conditional | research-only parallel | SQLite/storage write set |
| RepoWiki | ready | safe parallel derived write | `wiki/repowiki/**` only |
| CodeWiki | conditional | derived write, freshness caveat | `wiki/codewiki/**`; not Task truth |

## T1.2.1 R4 candidate reality update

The ZCode worktree is clean at `a527b85` and focused verification reports
`415 passed, 6 skipped, 1 failed`, exit 1. The known torch readiness assertion
and OpenSSL skips are recorded separately. The candidate has not been reviewed
or integrated. It leaves B-003 production `StdlibTransport` credential-store
injection unimplemented and changes `src/ui/qml/settings/SettingsView.qml`,
which is outside the current Task's allowed paths; Codex must resolve both
before approval.

## Recovery instruction

```powershell
Set-Location 'G:\CODEX\New Manga'
git status --short --branch
git rev-parse HEAD
Get-Content doc\STATUS.md
Get-Content doc\REBASELINE_PLAN.md
git log -8 --oneline --decorate
```

If the worktree is dirty, preserve the listed files and identify their owner
before any edit. Resume from the latest committed checkpoint, not chat memory.

Worker recovery check:

```powershell
Set-Location 'G:\CODEX\New Manga.worktrees\T1.1.2-qoder'
git status --short --branch
git rev-parse HEAD
```
