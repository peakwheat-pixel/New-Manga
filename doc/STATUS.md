# Current Development Status

Planning source of truth: [Project Rebaseline Plan](REBASELINE_PLAN.md)

Execution checkpoint: 2026-09-25 (Asia/Shanghai)

| Field | Current value |
|---|---|
| Latest child-slice integration | REPAIR-13 task delta integrated at `6fe7455d0927ae0b4328b77f117893d373797d92`; post-integration verification: 162 passed, exit 0. Parent T3.2.1 Release Gate remains OPEN. |
| T3.1.1 Release Gate base | `e771179`; delivery `899bd3c`; independent Review `4e1eb3a` approved |
| Branch | `master` |
| Mainline base checked before this audit/control baseline | `ade58140ac37d972385be416b4cc3ee7d81073b3`; T1.2.1 integrated at `9a14310`, evidence at `e92c414`. |
| Current milestone | **M1 — Alpha Core Loop Closure** |
| Stage | **Stage B — Controlled Execution** |
| Current product checkpoint | T1.1.1, T1.1.2, T1.2.1, T2.1.1, T2.2.1, and T3.1.1 are VERIFIED_COMPLETE. T3.2.1 remains unintegrated as a release and its Full Gate remains OPEN; REPAIR-13 child slice is done at integration `6fe7455`. REPAIR-9 findings and remaining parent Gate evidence are still open. Parent AC3 remains BLOCKED. |
| Current Active Task | [T3.2.1](tasks/T3.2.1.md) full Release Gate closeout (Codex). Child [REPAIR-13](tasks/T3.2.1-REPAIR-13.md) is `done`, integration=`6fe7455d0927ae0b4328b77f117893d373797d92`; child [REPAIR-14](tasks/T3.2.1-REPAIR-14.md) delivery `56bd33a` received independent `changes_requested` Review=`4301939` and is awaiting evidence revision; parent Gate remains OPEN. |
| Parallel research Task | [M2-D1 Headless & Qt Coupling Audit](tasks/M2-D1.md) is `done`: DeepSeek Harness Delivery=`0a27a54`, Handoff=`6f2cbb3`; Codex non-author [Review](reviews/M2-D1-0a27a54.md) `41f0571` `approved`; integration merge=`100abfb`. [Research report](research/M2-D1_HEADLESS_QT_COUPLING_AUDIT.md) has 26 evidence-classified items; Qt platform/headless runtime remains `UNVERIFIED`, product tests `NOT_RUN`. M2 implementation remains `PLANNED / NOT_RELEASED`; no successor implementation Task is released. |
| Current owner/reviewer | Full Gate Owner=Codex; final full-scope Reviewer=DeepSeek Harness (independent non-author). REPAIR-13 Owner=ZCode; REPAIR-14 Owner=Antigravity, Reviewer=DeepSeek Harness (independent non-author). |
| Current branch/worktree | Main branch=`master`; REPAIR-13 task delta integrated at `6fe7455d0927ae0b4328b77f117893d373797d92` from fixed evidence head `13ae23f65e963cf1d5aea19634572627e5e709db`. REPAIR-14 branch=`agent/antigravity/T3.2.1-repair-14`, worktree=`G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-14`, fixed base=`4ab6f58c06cb0691413e2630cb48a145c18c383a` (clean at creation). ZCode author worktree/branch remain preserved at `13ae23f` with three untracked DSH artifacts. All unrelated dirty paths remain preserved. |
| Latest reviewed base/head | REPAIR-8 Review `2585efd69009cd7620c6b020e67df90c7d49b0f1` approved delivery `3cdfdee126e8aab6b7930e49460a753abc69dad0` / tip `37d5488ebf8e33f897e802b4147cbd5fb1ad8e04` for documentation only. REPAIR-9 Review `85f8c59d0a012c1edc4e466187b5b42515297d74` returned `changes_requested` for `d2bf6a8` / `eeb095e`. REPAIR-10 Review `ddc21a2f3cf5521675e95d6e2a8f8f50b1c065fb` approved `be5200e` / `d7edea5` for packaging-test path independence only. REPAIR-11 Review `4f2f8a07e5b8119834cdc4cfd0fd0aa5c62ac4cc` returned `changes_requested`; REPAIR-12 base `962239521afbfec72025ab01941f89e08116ffc4`, Delivery `a2f6695bb289518db656f4d266910dccaa171207`, Handoff `8738c41d7215920935e6fa067d3740e69280cdc6`, Review `a6564862649b00fd91fa4e4ea8a2f64205eb71b7` `approved` for its evidence slice only. No full T3.2.1 Review is approved. |
| Latest integrated product test status | REPAIR-13 post-integration `tests/ui_shell tests/reading_export/test_qml_contract.py`: 162 passed, 0 skipped, exit 0; this is a focused child-slice suite, not the full T3.2.1 Gate. |
| Smoke status | The original clean Sandbox package failed QtCore import. REPAIR-9 smoke passed after its ICU packaging repair; neither fact satisfies the full Gate. REPAIR-13 final fixed package `aed0094` was run locally with an isolated `--data-root` and real GUI interaction through two-page ZIP export; DeepSeek Harness accepts child AC1–AC5 under the user-approved local verification route. The old Sandbox attempts remain historical evidence; the parent clean-Windows/Sandbox Gate is unchanged. |
| Compile status | No fresh T3.2.1 final-head compile/build is claimed by this closeout. |
| Current blockers | Parent T3.2.1 Gate remains OPEN; parent AC3=BLOCKED; AC5=NOT_RUN; AC6/AC7=PARTIAL / NOT_RUN; AC8/AC9=NOT_RUN; R-014–R-016=OPEN. REPAIR-13 child slice is done; its C2 supplement has a count-only discrepancy (12 claimed vs 13 independently counted), while post-C2 full diff-check is exit 0. Parent AC3 and child AC4 remain separate scopes. |
| Full Gate closure audit | [Codex closeout](../verification/T3.2.1/release-gate-closeout-b800d11.md) and [verification log](../verification/T3.2.1/release-gate-closeout-verification.log) record source checkpoint `35e55f1`, isolated candidate `188d72a`, REPAIR-12 Review, and O-12-2 disposition. Earlier [closure assessment](../verification/T3.2.1/closure-assessment-253af07.md), [Sandbox attempt](../verification/T3.2.1/clean-sandbox-ac3-20260924.md), and the new [manual AC3 observation](../verification/T3.2.1/ac3-interactive-20260925/manual-observations.md) are evidence. |
| Clean Windows environment route | Windows Sandbox is available (`C:\Windows\System32\WindowsSandbox.exe`). Prior status records Windows 11 Enterprise x64 build 26100; the latest manual baseline raw log reports `OS=Windows 10 Enterprise`, `OS_BUILD=26100`. Reconcile this label discrepancy before claiming edition-specific coverage. Build 3's exact hash and real-GUI attempt are recorded in [manual AC3 observations](../verification/T3.2.1/ac3-interactive-20260925/manual-observations.md); smoke evidence is not the full AC3 workflow. |
| F-003 disposition | REPAIR-11 Delivery `9622395` corrected the four wording instances; Review `4f2f8a0` independently marked R11-AC4 PASS. The REPAIR-11 slice overall remains `changes_requested` for F-11-1/F-11-2; no historical Review/log is to be rewritten. |
| G7-002 source ruling | Codex fixed the REPAIR-7 count source to `verification/T3.2.1/repair-5/reference-check.log` blob `fdddfc19225c66ca32a85a3ebe5b5e1cc3fe1dfe` at revision `297c3dd7d0c977eb22eedefd0ba1ae03d29b64cd` (identical at REPAIR-7 base `14f587c`). The `e54a7b6` blob `09b5f2d20a592694031ff40e3c02d7dc8e48d6aa` is historical 40/39 evidence, not the 41/40/27/19 derivation source. Both stay read-only. |
| REPAIR-8 allowed paths | Antigravity may change only `doc/tasks/T3.2.1-REPAIR-5.md`, `doc/tasks/T3.2.1-REPAIR-6.md`, `doc/handoffs/T3.2.1-REPAIR-6-f6dc383.md`, its new REPAIR-8 Handoff, and `verification/T3.2.1/repair-8/**`. Codex alone maintains this STATUS and the REPAIR-8 Task. Product code, tests, dependencies, Schema, original reference log, REPAIR-7 Handoffs and Reviewer reports are excluded. |
| REPAIR-9 allowed paths | `packaging/**`, `tests/packaging/**`, `verification/T3.2.1/repair-9/**`, and one new REPAIR-9 Handoff. Codex alone maintains this STATUS and the Task file. `src/**`, dependencies, Schema, REPAIR-7/8 artifacts and existing Review reports are excluded unless Codex separately expands scope. |
| REPAIR-10 allowed paths | Antigravity may change only `tests/packaging/**` for F-3(b), add evidence under `verification/T3.2.1/repair-9/**`, and add one new REPAIR-10 Handoff. Task/STATUS/Plan/index registration is Codex-owned; `src/**`, `packaging/**`, dependencies, Schema, REPAIR-7/8 artifacts, any Review report and the original `repair-5/reference-check.log` are prohibited. Base=`eeb095ea94cdf0d477bcb09ab7c761883b06f833`. |
| REPAIR-11 allowed paths | Antigravity may change `verification/T3.2.1/repair-11/**`, only the four F-003 wording instances in `doc/tasks/T3.2.1-REPAIR-6.md` / `doc/handoffs/T3.2.1-REPAIR-6-f6dc383.md`, and one new REPAIR-11 Handoff. Codex alone owns Task/STATUS/Plan/index registration. Base=`188d72a9d144b8cab16f77757abc46318ac8e5e6`; O-1 is already present and REPAIR-10 F-3(b) is approved. Product code, tests, packaging, dependencies, Schema, old evidence and all Review reports are excluded. |
| REPAIR-12 outcome | Base=`962239521afbfec72025ab01941f89e08116ffc4`; Delivery=`a2f6695bb289518db656f4d266910dccaa171207`; Handoff/tip=`8738c41d7215920935e6fa067d3740e69280cdc6`; independent Review=`a6564862649b00fd91fa4e4ea8a2f64205eb71b7` `approved` for the evidence slice only. O-12-2 is handled in the Codex closeout record; no Owner branch is merged. |
| REPAIR-13 registration | ZCode / DeepSeek Harness; `done`; fixed base=`8738c41d7215920935e6fa067d3740e69280cdc6`, product delivery=`aed009405fd523c52fa45e604afe40f01cef3d45`, final Handoff/evidence head=`13ae23f65e963cf1d5aea19634572627e5e709db`, independent Review report=`ccd26a4b4ef19a33ad91841602535614705213bd` (`APPROVE_WITH_CONDITIONS`, C1/C2 satisfied); integration=`6fe7455d0927ae0b4328b77f117893d373797d92`. Parent Gate status unchanged. |
| REPAIR-14 review/revision | [T3.2.1-REPAIR-14](tasks/T3.2.1-REPAIR-14.md); Owner=Antigravity; status=`changes_requested`; delivery=`56bd33a`, Handoff/evidence head=`9cff94f`, DeepSeek Harness Review=`4301939` (`changes_requested`). Base=`4ab6f58c06cb0691413e2630cb48a145c18c383a`; same branch/worktree remain assigned. Fix evidence/metadata findings and complete applicable fixed-package GUI AC4 before re-review. No integration. Parent Gate OPEN / AC3 BLOCKED unchanged. |
| Pre-reconciliation dirty main-worktree files | Preserve `experiments/TASK-017/README.md`, the uncommitted `.codewiki/`, `.codex/`, `.dsh/`, `.gemini/`, `.qoder-credits/`, `.qoder/`, `.tmp.driveupload/`, `.workbuddy/`, `.zcode/`, `docs/superpowers/plans/`, `material/`, `wiki/codewiki/temp/`, and all other pre-existing dirty paths. No cleanup or overwrite was performed. |
| Worktrees | All prior worktrees remain preserved. REPAIR-13 ZCode worktree remains at `13ae23f`; its three untracked DSH prompt/run/report files were preserved. The author branch was not merged wholesale; the fixed REPAIR-13 task delta was applied to `master`. No worktree was deleted or pruned. |
| Evidence | [REPAIR-13 Task](tasks/T3.2.1-REPAIR-13.md); [independent Review](../verification/T3.2.1/repair-13/review-report-dsh.md); [C2 diff-check supplement](../verification/T3.2.1/repair-13/diff-check-full-post-c2.md); [Codex integration record](../verification/T3.2.1/repair-13/integration-6fe7455.md); parent [T3.2.1 Release Gate](../verification/T3.2.1/release-gate-c2fcb1c.md). |

## Parallel architecture governance registration

`GOV-001` is `done`: Codex integrated the documentation registration at merge `969f7a5e535b6d98b163bab9fb6ac2f6e8512088` from fixed base `1e8cb1157c987945316351728f725073b8b109f9`; DeepSeek Harness independently [approved](reviews/GOV-001-2e8f4bf.md) it at `bbf24e73b0d5b40f23f90ce851e47c7cf681ab2a`. The approved author branch `codex/architecture-decision-registration` remains preserved. [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md) records the user-accepted React + TypeScript + Tauri + Python Core target as `ACCEPTED_TARGET_ARCHITECTURE / IMPLEMENTATION_NOT_RELEASED`. [REBASELINE_PLAN](REBASELINE_PLAN.md) registers future M2 `PLANNED / NOT_RELEASED`. The sole released Discovery successor, [M2-D1](tasks/M2-D1.md), is now `done` after Codex independent [Review](reviews/M2-D1-0a27a54.md) and integration merge `100abfb`; no migration implementation is released. This does not change the Current Active Task row above: T3.2.1 Full Gate stays OPEN and AC3 stays BLOCKED. REPAIR-13 is done at integration `6fe7455`; REPAIR-14 was released after its dependency closed and is now awaiting revision after independent Review `4301939`. Neither child slice closes the parent Gate. User decisions remain open for T3.2.1 Legacy Closure scope and future React UI ownership. The main-worktree dirty/untracked set observed before GOV-001 is `PRE_EXISTING_WORKTREE_CHANGE`; it was not edited by this registration or audit integration.

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

1. T3.2.1: full Release Gate remains open. The `c2fcb1c` decision was PASS TO START; AC3 interactive Windows workflow is `BLOCKED` after the fixed-package import failure and blocks release.

## Stage B execution gate

T1.1.2, T1.1.1, T1.2.1 and T2.1.1 are integrated and verified. Preserve all
dirty files and worktrees. `TASK-013` remains the historical task; completed
T1.1.2 and the completed T2.1.1 state belong to the Current Roadmap.

## T2.1.1 Release Gate checkpoint

Codex created the formal [T2.1.1 Task](tasks/T2.1.1.md) and the isolated
Qoder worktree `G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml` from
`7f341355968f69fc3db7b6824d73ec7d56c182be`. The selected token delivery was
fixed to `pragma Singleton` + `qmldir`. Qoder delivered, Codex completed
non-author review, repaired the one blocking status-badge defect, and
integrated the task at product code commit `5da1cf6`.

## T2.1.1 Non-author Review / Integration checkpoint

Codex reviewed Qoder delivery `bc49ef9` with evidence/Handoff head `ddb2044`.
The authorized QML/test/verification scope was respected; `Main.qml` palette
binding, `AppShell.qml` rail token, and presentation-only `SettingsView.qml`
changes were accepted as in-scope. The light-mode dark-canvas consequence was
handled with the F `.vfloat`-style `CanvasCaption`; the webtoon canvas ground
remains an IMPORTANT deferred finding.

One BLOCKING finding was found in `NavBadge.qml`: `st-run` was used as a solid
background with `on-accent` text (2.54:1 in dark mode), violating the F status
badge contract. A focused test was first red, the minimum fix was committed
as `5da1cf6`, and the test became green. Qoder history is preserved in merge
commit `e34e19c`.

Fresh integration evidence: focused QML/workbench/reader-export `382 passed`,
full suite `1178 passed, 11 skipped, 0 failed, 1 warning`, compileall exit 0,
bootstrap smoke exit 0, and diff-check clean. Environment skips are documented
in [integration evidence](../verification/T2.1.1/integration-5da1cf6.md).
Review: [review-bc49ef9](../verification/T2.1.1/review-bc49ef9.md).
Result: **T2.1.1 = VERIFIED_COMPLETE**. Its successor now has its own
Release Gate.

## T2.2.1 Release Gate / completion checkpoint

Codex created the formal [T2.2.1 Task](tasks/T2.2.1.md), implementation plan,
and [Release Gate](../verification/T2.2.1/release-gate-ef1a9b8.md) at base
`16810c5`. ZCode delivered the functional seam at `df637df`; Qoder delivered
the QML/UI head `0846573` in
`G:/CODEX/New Manga.worktrees/T2.2.1-qoder`. Codex approved the non-author
review and integrated the serial chain at product code head `fe9fca0`.

The frozen scope is: Reader chapter picker, Workbench empty-state picker,
dismissible command-error presentation, and webtoon `Tokens.bgCanvas`
consistency. Region six-state rendering, command palette, storage, bootstrap,
Schema, provider/runtime, and dependency changes are excluded.

Focused integration verification is `278 passed`, exit 0. Compile and smoke
are exit 0. Full-suite verification is `1209 passed`, six explicit OpenSSL
skips, one known torch-environment failure, exit 1; this limitation is
recorded in [integration evidence](../verification/T2.2.1/integration-aad510b.md)
and is not hidden as PASS. Result: **T2.2.1 = VERIFIED_COMPLETE**.

## T3.1.1 independent Release Gate and integration checkpoint

Codex created the formal [T3.1.1 Task](tasks/T3.1.1.md), implementation plan,
and [independent Release Gate](../verification/T3.1.1/release-gate-e771179.md)
at governance base `e771179`. Antigravity delivered `899bd3c`; DeepSeek Harness
independently reviewed it in a separate worktree and approved it at `4e1eb3a`.
Codex then integrated the product delivery at `0c70e44`, merged the Review and
Handoff evidence, and reran the focused/core/compileall/smoke gates.

Integration evidence is [integration-899bd3c](../verification/T3.1.1/integration-899bd3c.md):
focused `220 passed`, core `49 passed`, compileall exit 0, smoke exit 0, and
`git diff --check` exit 0. R-001/R-003 wording is corrected by explicit Task
disposition; R-002 remains a documented non-blocking P2 defer.

Result: **T3.1.1 = VERIFIED_COMPLETE**. T3.2.1 now has its own Release Gate;
implementation has not started.

## T3.2.1 Windows Packaging Release Gate / delivery Review checkpoint

Codex established the formal [T3.2.1 Task](tasks/T3.2.1.md) and
[Release Gate](../verification/T3.2.1/release-gate-c2fcb1c.md) from the verified
T3.1.1 baseline `c2fcb1c`. REPAIR-2 delivered product head
`7d687f51567d4f947fee9b3f6eff4bc95e2b6413` and evidence/Handoff head
`ffff7c688df07165c6e801c0c9572e9c4910cb9e`. DeepSeek Harness independently
reviewed it at commit `4613338815406be0fdf2240cb1e5715a619f61f7` and returned
`CHANGES_REQUESTED`: R-008 still passes after its production branch is removed,
and AC7's Handoff `PASS` conflicts with the Task's `PARTIAL / NOT_RUN`. The
delivery remains isolated; `master` has no T3.2.1 product integration.

### T3.2.1-REPAIR-3 review result

[T3.2.1-REPAIR-3](tasks/T3.2.1-REPAIR-3.md) delivered product head
`d79d7dd251cd5f10434ea40c54e15e8bae42d374` and evidence/Handoff head
`c04497e157bb76dabdc70aedabd07ba3496d45e4`. DeepSeek Harness reviewed the
fixed delivery and returned `CHANGES_REQUESTED` at
`54f2627196969309d5c3942caf19ccec6c6ab7b5` for R-017–R-021. R-008's test
discrimination passed independent mutation; AC3 remains `NOT_RUN`, AC6/AC7
remain `PARTIAL / NOT_RUN`, and R-014–R-016 remain open.

### T3.2.1-REPAIR-4 release record

[T3.2.1-REPAIR-4](tasks/T3.2.1-REPAIR-4.md) is `ready` and released to
Antigravity. Delivery head is `f39ddc0fcaeb8c8271d73376f82b3ec9f15c0fd9`;
Handoff commit is `f2581a44d1198639ad00fd386e1fbe1dc61c1f7a`. DeepSeek Harness
reviewed it at `dc199f607c407adce40d303cb182b28f9a76a1db` and returned
`CHANGES_REQUESTED` for F-001: `doc/tasks/T3.2.1.md:153` points to a nonexistent
REPAIR-4 Handoff filename.

REPAIR-4 remains `changes_requested`; its review report and the author delivery
stay on their isolated branches. REPAIR-5 is `ready` on branch
`agent/antigravity/T3.2.1-repair-5`, worktree
`G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-5`, based on the valid
REPAIR-4 author tip `0e0905f8041743175239183d9c4ab7eabb78cb90`. Its scope is
F-001 plus relative-link and commit-object reachability self-checks for
`doc/tasks/T3.2.1*.md`. AC3 and AC5 remain `NOT_RUN`; AC6 and AC7 remain
`PARTIAL / NOT_RUN`; R-014–R-016 remain open. No source, test, packaging,
dependency, Schema or product behavior changes are authorized. The new fixed
head requires fresh independent DeepSeek Harness review; Codex must still
complete the full T3.2.1 Release Gate before any product integration.

The hard final boundary is D07/D08: a real Windows x64 machine without Python,
venv, source checkout or developer PATH must complete the package workflow,
restart with data intact, preserve source/data safety, and leave no residual
process. TASK-004's minimal onedir experiment remains supporting evidence only;
its clean-machine E12 is `BLOCKED` and cannot satisfy T3.2.1.

The frozen boundary is: additive v4 migration, SQLite adapters for the existing
progress/history ports, one-time non-destructive legacy JSON import, bootstrap
injection, and migration/data-loss evidence. TASK-028 Library/Page/Region work,
v1–v3 migration edits, backup UI, Pipeline/Provider/QML and packaging remain out
of T3.1.1 scope. T3.2.1 packaging is released only within its own Gate.

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
  Codex. B-003 follow-up delivery `e5716ac` / Handoff `e025c9a` is now
  independently approved; product integration and final verification are the
  current Codex-only next step.

## T1.2.1 R5 non-author review checkpoint (historical; superseded by integration)

Codex reviewed ZCode R5 implementation `e5716ac` against `39dbbf7` and Handoff
`e025c9a` in `G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`.
The author worktree is clean at `e025c9a`.

- Result: **REVIEW APPROVED — B-003 CLOSED; READY FOR INTEGRATION VERIFICATION**.
- R5 implementation scope is limited to `src/bootstrap/app.py` and
  `tests/core/test_transport_credential_assembly.py`; Handoff and redacted
  probe are the only accompanying evidence paths.
- `_credential_store()` catches construction/import failures and returns
  `None`; production `assemble_services` constructs one store and shares it
  with transport, provider resolver and SettingsViewModel. The Handoff
  §10.2③ cleanup is confirmed in scope because it removes a duplicate vault
  construction inside the same authorized assembly file.
- Fresh Git Bash full: `1139 passed, 1 known torch environment failure, 0
  skipped, 1 warning`, exit 1. Fresh PowerShell full: `1133 passed, 6
  OpenSSL skips, 1 known failure, 1 warning`, exit 1. Assembly/fail-closed
  focused: `5 passed`, exit 0; broader R5 focused set: `90 passed`, exit 0.
- Compileall exit 0; six bootstrap smoke runs passed; diff-check exit 0.
  Fresh production probe passed: two real assemblies, SQLite binding,
  registry resolution, provider client request, exact proxy Basic header,
  zero auth failures, secret absent from output, and vault cleanup true.
- Evidence: [R5 review](../verification/T1.2.1/review-e5716ac.md).
- Status: `T1.2.1 = READY_FOR_INTEGRATION_VERIFICATION`; Codex may now
  integrate serially. Do not start T2.1.1 before final integration evidence.

## T1.2.1 R4 non-author review checkpoint (historical)

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
| TaskStatus | T1.2.1, T2.1.1, T2.2.1 and T3.1.1 VERIFIED_COMPLETE; T3.2.1 in_progress / release_gate_open; REPAIR-8/10/12 approved (scope-limited); REPAIR-9 remains changes_requested; REPAIR-13 done at integration `6fe7455`, AC1–AC6 satisfied; REPAIR-14 changes_requested after Review `4301939`. |
| ExecutionState | REPAIR-14 REVISION_REQUIRED; product delivery is preserved at `56bd33a`; evidence revision and applicable AC4 package GUI verification are pending. Codex continues the parent T3.2.1 Gate closeout; parent AC3 remains BLOCKED. |
| `Current Executor` | Antigravity owns the bounded revision in the existing worktree; DeepSeek Harness will independently re-review a new fixed head; Codex owns task metadata and later integration. |
| YOU ARE HERE | T3.1.1 verified → T3.2.1 full Gate OPEN → REPAIR-13 done → REPAIR-14 `changes_requested` at Review `4301939`; evidence revision and fixed-package GUI AC4 remain before approval → parent Gate closeout remains separate |
| `Dependency Blocking Chain` | T3.1.1 `VERIFIED_COMPLETE` → close remaining REPAIR-9 findings and R-014–R-016 → final Windows AC3/AC5/AC6–AC9 evidence → full independent Review → Codex parent Gate integration verification |
| `Safe Parallel` | RepoWiki/derived knowledge refresh; isolated research-only work |
| Conditional | No REPAIR-13 evidence follow-up remains. The C2 record's pre-cleanup count differs from Codex's fixed-range recount (12 vs 13); all reported whitespace is removed and post-C2 full diff-check is exit 0. |
| `Do Not Start Yet` | Do not integrate REPAIR-14 until required revisions pass independent re-review. Do not work outside its frozen allowed paths, merge candidate branches, claim parent release readiness, or publish a release before all parent Gate criteria/final Review. |
| Safe To Resume | Antigravity may continue the REPAIR-14 revision on its existing branch/worktree at base `4ab6f58`; complete evidence corrections and applicable AC4 verification. Codex may continue the separate parent T3.2.1 closeout; parent Gate remains OPEN and AC3 remains BLOCKED. |
| `Latest audit checkpoint` | `verification/T3.2.1/release-gate-closeout-b800d11.md`; closeout start `master`=`b800d11`; product Gate baseline `c2fcb1c` |

### Current position map

```text
T1.1.2 VERIFIED_COMPLETE
        ↓
T1.1.1 VERIFIED_COMPLETE @ f56f441
        ↓
T1.2.1 VERIFIED_COMPLETE @ 9a14310 / e92c414
        ↓
T2.1.1 VERIFIED_COMPLETE @ 5da1cf6
        ↓
T2.2.1 VERIFIED_COMPLETE @ fe9fca0
        ↓
T3.1.1 VERIFIED_COMPLETE @ 0c70e44
        ↓
T3.2.1 implementation authorization (PASS TO START) @ c2fcb1c
        ↓
T3.2.1 isolated repairs; full Release Gate OPEN (parent AC3 BLOCKED; REPAIR-13 done at integration `6fe7455`)
        ↓
REPAIR-13 task delta integrated at `6fe7455` (C1/C2 conditions satisfied; parent Gate still open)
        ↓
REPAIR-14 F-13-3 implementation delivery `56bd33a`; review `4301939` requested evidence revision, no integration
```

### Parallel execution matrix

| Work item | Readiness | Class | Conflict |
|---|---|---|---|
| T1.2.1 | complete | closed | provider runtime, VM, Settings QML, bootstrap integrated |
| T2.1.1 | complete | `CLOSED` | four-page QML/theme; F token contract; T1.2.1 UI contracts |
| T3.1.1 | complete | closed | SQLite v4 progress/export persistence integrated and independently approved |
| T3.2.1-REPAIR-8 | approved | documentation slice only | DSH report `2585efd`; no product/Gate approval |
| T3.2.1-REPAIR-9 | changes_requested | review findings open | DSH report `85f8c59`; Codex O-1 whitespace correction is isolated at `188d72a`; F-2/F-4/O-3 remain |
| T3.2.1-REPAIR-10 | approved | packaging tests only | DSH report `ddc21a2`; 12 passed without external `PYTHONPATH`; full Gate remains open |
| T3.2.1-REPAIR-13 | done | QML import/readability, dialog contrast, F-13-2 + F-13-4 and local two-page export | ZCode owner; DeepSeek Harness independent reviewer; delivery `aed0094`, evidence head `13ae23f`, Review conditions satisfied; Codex integration=`6fe7455`; parent Gate remains open |
| T3.2.1-REPAIR-14 | changes_requested | F-13-3: restore persisted bookshelf entries after process restart | Antigravity; delivery=`56bd33a`; Review=`4301939`; evidence revision and applicable AC4 package GUI verification pending; no integration |
| T3.2.1 full Release Gate | in_progress | Codex closeout | Parent AC3 remains `BLOCKED`; remaining parent evidence and final Review are required before release readiness |
| RepoWiki | ready | safe parallel derived write | `wiki/repowiki/**` only |
| CodeWiki | conditional | derived write, freshness caveat | `wiki/codewiki/**`; not Task truth |

## T1.2.1 integration completion checkpoint

Codex fast-forwarded master to integration evidence commit `e92c414`, whose
code integration merge is `9a14310`. The author chain from `c54f360` through
`e025c9a` is preserved as the merge's second parent. The final integration
tree is clean; the pre-existing main-worktree dirty files remain untouched.

- R5 Review: [review-e5716ac](../verification/T1.2.1/review-e5716ac.md),
  BLOCKING findings = 0.
- Final integration evidence: [integration-9a14310](../verification/T1.2.1/integration-9a14310.md).
- Final product probe: two production assemblies, persisted SQLite binding,
  registry/provider resolution, exact authenticated proxy header, zero auth
  failures, no secret exposure, and vault cleanup all passed.
- Final focused suite: 122 passed, exit 0. Full suite: Git Bash 1139 passed,
  1 known torch environment failure, 0 skipped; PowerShell 1133 passed, 6
  OpenSSL skips, 1 known failure; both exit 1 only for the documented
  environment assertion. Compileall, six smoke runs, and diff-check passed.
- Result: `T1.2.1 = VERIFIED_COMPLETE`. T2.1.1 subsequently passed its own
  Release Gate and is recorded in the completion checkpoint above.

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
