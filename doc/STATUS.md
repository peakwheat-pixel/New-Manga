# Current Development Status

Planning source of truth: [Project Rebaseline Plan](REBASELINE_PLAN.md)

Execution checkpoint: 2026-09-22 (Asia/Shanghai)

| Field | Current value |
|---|---|
| Latest product integration | `f56f441c1ce981ff83a3af98c5862917e35711f1` (T1.1.1 product merge) |
| Branch | `master` |
| Mainline HEAD at this checkpoint | `ef8d0e02a21f2834420130a2553e90fdf9443368` (later documentation commits; no `src/**`, `tests/**` or `requirements.txt` change since `f56f441`) |
| Current milestone | **M1 — Alpha Core Loop Closure** |
| Stage | **Stage B — Controlled Execution** |
| Current product checkpoint | `T1.2.1 — Settings UI & ViewModel = REVIEW_BLOCKED / NOT INTEGRATED`; T1.1.1 and T1.1.2 are `VERIFIED_COMPLETE`. |
| Current owner/reviewer | T1.2.1 implementation: ZCode; non-author reviewer/integrator: Codex. Blocking findings: B-001/B-002. |
| Current branch/worktree | Author: `agent/zcode/T1.2.1-settings-ui-viewmodel` / `G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`; isolated Codex candidate: `agent/codex/T1.2.1-integration` / `C:\Users\49745\.codex\worktrees\t121-codex-integration\New Manga` (not merged). |
| Current review base/head | base `d11d927`; delivery `c54f360`; author handoff `ace633a`; isolated partial repair `0b4e434`. |
| Latest integrated product test status | T1.1.1 integration: Python 3.12 implementation venv, `1077 collected = 1070 passed + 6 skipped + 1 known environment failure`, exit 1. The failure is the model-runtime readiness assertion; six skips are OpenSSL-unavailable TLS cases. T1.2.1 candidate results are recorded in its review, not claimed as mainline verification. |
| Smoke status | `python -m bootstrap.app --smoke-test --data-root <temp>` exit 0; SQLite and managed directory created. |
| Compile status | `python -m compileall -q src tests` exit 0. |
| Current blockers | No T1.1.1 integration blockers. T1.2.1 review found unresolved production provider-registry binding and network/proxy transport wiring blockers; no formal `doc/tasks/T1.2.1.md` release record is committed. Deferred outside these tasks: the expected model-runtime readiness assertion in the implementation venv and the previously observed export signal race; neither is in the detector diff. Graphite F is not applied to production QML; reading/export history remain JSON-backed; product packaging and clean-machine gate are absent. |
| Pre-reconciliation dirty main-worktree files | Preserve `experiments/TASK-017/README.md` (tracked modification) and untracked `.codewiki/`, `.qoder-credits/`, `docs/`, `material/`, `wiki/codewiki/temp/`. Recheck `git status` before any edit; current documentation edits are separate. |
| Worktrees | Existing inventory is a 2026-09-20 conservative snapshot. Old `TASK-013-qoder` is clean but based on pre-Stage-A history and contains prior Qoder work; preserved, not selected. T1.1.2 worktree is clean at `5b91745`. No deletion or prune is authorized. |
| Evidence | [T1.1.1 integration](../verification/T1.1.1/integration-f56f441.md); [T1.2.1 non-author review](../verification/T1.2.1/review-c54f360.md); [T1.2.1 isolated candidate](../verification/T1.2.1/integration-0b4e434.md) |

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

1. T1.2.1: close B-001 provider-registry resolution and B-002 network/proxy
   transport wiring; incorporate/review the isolated B-003 mirror repair.
2. T2.1.1: apply the selected Graphite Atelier token layer to production QML.
3. T3.1.1: migrate reading progress and export history from JSON to SQLite.
4. T3.2.1: build and verify a product Windows onedir package on a clean machine.

## Stage B execution gate

T1.1.2 and T1.1.1 are integrated and verified. T1.2.1 has been delivered but
its review is blocked; do not integrate it or release T2.1.1 until B-001/B-002
are resolved, the missing formal Task scope is recorded, and a fresh non-author review and Codex
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
