# Current Development Status

Planning source of truth: [Project Rebaseline Plan](REBASELINE_PLAN.md)

Audit checkpoint: 2026-09-21 (Asia/Shanghai)

| Field | Current value |
|---|---|
| Code baseline HEAD | `ce21ff9ea5738970bbda9a86079b673918c76048` |
| Branch | `master` |
| Integrated code HEAD | `5b917459deeb72de575d0985e1315889444cef4b` |
| Current milestone | **M1 — Alpha Core Loop Closure** |
| Stage | **Stage B — Controlled Execution** |
| Active product task | `T1.1.1 — Production Text Detector = INTEGRATION_BLOCKED / SCOPE CLARIFICATION`; `T1.1.2 — Region Canvas & Creator = VERIFIED_COMPLETE`. |
| Product task owner/reviewer | Implementation: ZCode; non-author review/integration: Codex; T1.1.1 blocking findings: 0; IMPORTANT deferred findings: 2. |
| Execution branch/worktree | `agent/zcode/T1.1.1-production-text-detector` / `G:\CODEX\New Manga.worktrees\T1.1.1-production-text-detector` |
| Execution base/head | review base `4a1ed6ca`; delivery head `2f116a2`; R2 docs head `4a631355` |
| Verified test status | Fresh Python 3.12 venv: `1031 collected = 1025 passed + 6 skipped`, exit 0. All six skips are OpenSSL-unavailable TLS cases; one existing MOBI deprecation warning. |
| Smoke status | `python -m bootstrap.app --smoke-test --data-root <temp>` exit 0; SQLite and managed directory created. |
| Compile status | `python -m compileall -q src tests` exit 0. |
| Current blockers | T1.1.1 R2 review has 0 code blockers, but Integration Gate is blocked: the latest gate scope excludes the formal Task's required `src/bootstrap/app.py` detector seam and supporting `tests/**`; see `verification/T1.1.1/integration-scope-blocker-d7119a2.md`. Master still uses the prior T1.1.2 product state. Deferred: author full-suite pass/skip count correction and existing export signal race. Settings page is a placeholder with no Settings VM; Graphite F is not applied to production QML; reading/export history remain JSON-backed; product packaging and clean-machine gate are absent. |
| Dirty main-worktree files | Preserve: `experiments/TASK-017/README.md` (tracked modification); `.qoder-credits/` (19 untracked files); `.codewiki/`, `wiki/`, `.repowikiignore`, `doc/AI_COORDINATION.md` (untracked parallel/generated material). |
| Worktrees | Existing inventory is a 2026-09-20 conservative snapshot. Old `TASK-013-qoder` is clean but based on pre-Stage-A history and contains prior Qoder work; preserved, not selected. T1.1.2 worktree is clean at `5b91745`. No deletion or prune is authorized. |
| Last product integration | `5b91745` T1.1.2 Region Canvas & Creator; prior product integration was `38d6eaa` TASK-057. |
| Evidence | [Codex T1.1.2 final verification](../verification/TASK-013/t112-codex-final-integration.log) |

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

1. T1.1.1: choose and wire one real text detector; MangaOCR is recognition,
   not detection.
2. T1.2.1: expose provider, credential, endpoint and proxy settings safely.
3. T2.1.1: apply the selected Graphite Atelier token layer to production QML.
4. T3.1.1: migrate reading progress and export history from JSON to SQLite.
5. T3.2.1: build and verify a product Windows onedir package on a clean machine.

## Stage B execution gate

T1.1.2 is integrated and verified. T1.1.1 R2 has a fixed implementation
delivery head and an approved non-author review, but its Integration Gate is
blocked by a scope conflict; it is not integrated or verified. Do not start any
later roadmap unit.
Preserve all dirty files and worktrees. `TASK-013` remains the historical task;
T1.1.2 is closed and T1.1.1 is approved but remains outside the integrated
product state until the Codex integration gate completes.

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

The requested Integration Gate was blocked before product acceptance. The actual
master had advanced from declared `94ab0d3` to `d7119a2` with CodeWiki-only
documentation changes. An isolated candidate merge at `f56f441` preserved the
ZCode history, but its diff necessarily includes the formal Task's required
`src/bootstrap/app.py` detector injection and supporting `tests/**` files.

The latest Integration Gate list did not authorize those paths, although
`doc/tasks/T1.1.1.md` does. The candidate is therefore not merged to master and
no integration verification was recorded as PASS. Evidence:
[integration scope blocker](../verification/T1.1.1/integration-scope-blocker-d7119a2.md).

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
