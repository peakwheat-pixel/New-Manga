# FEA-15-PIN-BASIS-ENFORCE-1 evidence

## AC1 baseline checkpoint — A/B/AC1d adjudicated; AC2/AC3 released

ZCode release Addendum 4 accepts the exact historical delta below as a one-time transition. The AC1c A-side outcomes were adjudicated `ACCEPT_CONTINUE`; every observed A-side FAIL remains FAIL and every PASS remains as observed. B's permitted R0 assertions and TaskPath passed. A separate fresh, read-only ZCode session returned `AC1D_PASS` for the baseline confirmation. That decision releases only AC2/AC3 implementation from R0; AC4/AC5 remain NOT_RUN and are not released by this baseline decision. See the [AC1c A adjudication](../../doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac1c-a-release-adjudication-2026-11-12.md) and [AC1d confirmation](../../doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac1d-baseline-confirmation-2026-11-12.md).

- Fixed A clone HEAD: `2df8db7a4d19b591e919ecc6e8f8651167800ef0`.
- Runtime: Git `2.52.0.windows.1`; PowerShell `7.6.9`; Python `3.14.6`; `core.autocrlf=true`; clone-local `core.longpaths=true`.
- Before measurement, the corrected clone was detached at the exact base and `git status --porcelain` was empty. The first checkout emitted Windows `Filename too long` errors; after setting only this clone's `core.longpaths=true`, forced checkout returned `EXIT=0`, restored the sample files, and reported a clean tree. The first checkout's subcommand exit was not captured separately; it is not represented as a pass.
- Frozen-script reproduction anchor: `EXIT=0`; output SHA-256 exactly matched both the historical output and Addendum 2's pin `27ab6ac6f3e1c2213d6bfcd6acec11d16c94f1025a1e02abb0465bb90c523323`; `5,350 → 5,376`, added 26, removed 0, changed 0.
- Formal inventory: `EXIT=0`; `5,438` rows (`5,420` Task evidence rows + `18` frozen pins), measured at the fixed base. Inventory SHA-256: `3c6e39a269437873e2bb9b40c4b3c9461bcafaa1d171f240dfed322565bc1ce2`.
- Formal delta against the registered `e9f7bb1b48c885cb329848d2d3591e145ff3d229` inventory: `5,376 → 5,438`; `ADDED=62`, `REMOVED=0`, **`CHANGED=2`**. Added rows are attributed to `FEA-15-PIN-POLICY-1` (31), `GOV-CHECKER-NOTASK-1` (18), and `GOV-REFINCIDENT-1` (13). Delta SHA-256: `d737fcc75efcf10ab24ef55be75d5b6538c9acea1939450a5516867a652a95ea`.
- The two changed rows are both existing `FEA-15-PIN-POLICY-1` rows. Their identities and `pin_sha256` values are unchanged; the `class` values changed from empty to `CANONICAL` after the table header was simplified, and `release-gates.ac_gate` changed from `AC3 release baseline` to `AC3 release gates`. ZCode Addendum 4 attributes both to `d26c43c76576b0f514530874fc9cb04f016674e6` and accepts this exact `CHANGED=2` as a one-time transition. It must remain `CHANGED=2`, never be rewritten as zero. See `history-transition-ledger.md` and [Addendum 4](../../doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-zcode-release-adjudication-addendum4-2026-11-12.md).
- AC1c A-side run at main HEAD `8d1d75ca246ef0daf7f3c116974cf16cfa21d410`, A HEAD `2df8db7a4d19b591e919ecc6e8f8651167800ef0`: default and all four Addendum 4 historical TaskPaths returned `EXIT=1`; `verify_pins.ps1` returned `EXIT=1` with 16/18 mismatches; API returned `EXIT=0` (`1/79/6=86`); fixed boundary matrix returned `EXIT=0`, SHA-256 `e8c48163d5c552b337a478326d7e7e8d7c637c2304741c66b579f48ce6a70246`. Full command output is in `ac1c-a-gates-8d1d75ca.log`. FAIL is not PASS.
- The matrix file's A output/worktree SHA-256 is `e8c48163d5c552b337a478326d7e7e8d7c637c2304741c66b579f48ce6a70246` (4438 bytes). The Canonical Evidence pin uses the `6086a5b1f7c1f95ea91a313798dbd391f5132648` Git blob SHA-256 `68ec4b50c3bbfc450218bc35fdc7da8f43454cf23eaedae8cbd4c872d879ec41` (4316 bytes); both were independently verified and differ because checkout EOL conversion changes the bytes.
- The A clone had `core.autocrlf=true`, `core.longpaths=true`; raw porcelain showed only the Task-local untracked output directory (inventory, delta, reproduction, and matrix JSON), with no tracked changes. Its `REBASELINE_PLAN.md` Git blob is 6,992 bytes while the checked-out file is 7,056 bytes / 64 lines. Default, `AGPL-RELEASE-1`, and `AD002-FOLLOWUPS-1` failed the Plan budget; `FEA-06-PREREQ-1` also reported historical evidence hash/path/resource/closeout failures; `CHAPTER-SELECTOR-1` also reported missing resource-manifest and AC status markers. `verify_pins.ps1` mismatched C01b, C02, C03, C05, C06, C07, C08, C09, C10, C11, C12, C13, C14, C15, C16, and FEA01; C04b/C17 passed.
- ZCode adjudicated AC1c A as `ACCEPT_CONTINUE`: the 7056/6992 Plan byte difference is deterministic EOL expansion; the 16/18 pin mismatches are working-tree byte effects; historical TaskPath findings are static frozen baseline facts. These results remain recorded as FAIL and are not PASS. No A clone config, checker, historical file, or frozen pin was changed. At adjudication time B was **NOT_RUN**; B has since run at R0 as recorded below.

## AC1c B R0 verification

- R0: `bfae0b9bd6a9b85a9a546d2adda0b684783ddb24`; comparison base: `2df8db7a4d19b591e919ecc6e8f8651167800ef0`. The B clone is retained at `G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/r0-baseline`.
- The clone was created with `git clone --no-checkout` (`EXIT=0`). Clone-local `core.autocrlf=false` and `core.longpaths=true` were written and verified before the first checkout; `.git/config` last-write time was `2026-11-11T18:26:32Z`, before the checkout reflog time `2026-11-11T18:26:49Z`. Checkout detached at R0 with `EXIT=0`.
- Environment: Windows; Git `2.52.0.windows.1`; PowerShell `7.6.9`; Python `3.14.6`; clone-local `core.autocrlf=false`, `core.longpaths=true`. B clone was clean before and after its TaskPath command.
- Task, STATUS, and Plan file presence assertions: all `PASS`. `git diff --no-renames --name-status 2df8db7… bfae0b9…`: `EXIT=0`, 25 paths, all within the released Task scope. Per-file Git blob comparison across `tools/governance/**` and `doc/templates/**`: `PASS`, all 24 files identical.
- Only B gate run: `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md`, `2026-11-11T18:30:33.972Z`–`2026-11-11T18:30:36.832Z`, `EXIT=0` (3 warnings). B default, pins, API, inventory/delta/reproduction, historical TaskPaths, and sample matrix were **NOT_RUN** by design; they are not PASS.
- At clean main R0 HEAD, the separate recorded default check, current TaskPath, 18-pin audit, and API inventory all returned `EXIT=0` (3 warnings on each governance check; API `1/79/6=86`). Full outputs are in `r0-main-gates-bfae0b9.log` and `ac1c-b-r0-assertions-taskpath-bfae0b9.log`.

## AC1d independent baseline confirmation

- ZCode fresh session `sess_fd863071-c665-4b61-89be-2156ace80595`, decision turn `turn_133dc2f6-c7f1-467c-a8a5-2c342f12c65a`, returned `AC1D_PASS` after read-only review of main HEAD `0851085cbeeaaea95d1fd94b55a435a3e2eef102`; frozen implementation baseline is R0 `bfae0b9bd6a9b85a9a546d2adda0b684783ddb24`. The report records the original long-run CLI EXIT as not captured; the same-session receipt returned `EXIT=0` but only repeated the existing decision. The decision is recorded as reported, without claiming the uncaptured run EXIT.
- The report explicitly unblocks only AC2 and AC3. AC4/AC5 and other unrun gates remain NOT_RUN. A-side failures and all other baseline results retain their original statuses.
- The report described 15 Canonical Evidence rows at its reviewed HEAD. A separate logged check at `cdd5d258690471c8069d47f461f04a1ef9a306bd` enumerated the then-current 19 rows; all 19 commits contained the pinned path and all Git blob SHA-256 values matched. The audit log records `PIN_AUDIT=PASS failures=0`, `EXIT=0`, and clean status before/after; it does not cover later evidence rows.
- Inventory, delta, and reproduction pins use Git blob bytes, while the A-clone artifact table records autocrlf=true worktree bytes. The pairs were independently compared after CRLF-to-LF normalization: inventory blob `2aca6413774798056323f152f5a3ffc8a0fd82461bb6bdeef5f0c65fbf1d87c4` / A output `3c6e39a269437873e2bb9b40c4b3c9461bcafaa1d171f240dfed322565bc1ce2` (146,220 CRLF pairs); delta blob `f88f99052ee1580a8b859c5468b5621005df5e77e1bd179045d0c279fce97f21` / A output `d737fcc75efcf10ab24ef55be75d5b6538c9acea1939450a5516867a652a95ea` (941 pairs); reproduction blob `c27247db93960076ff27566e642be5b3d273588be47a8fa378eb81866bb3701e` / A output `27ab6ac6f3e1c2213d6bfcd6acec11d16c94f1025a1e02abb0465bb90c523323` (414 pairs). Each normalized worktree file exactly equals its pinned Git blob; pins are unchanged.
- `.gitattributes` has no EOL rule for this verification directory. The resulting worktree/blob byte distinction remains a documented limitation; this Task does not change `.gitattributes` or perform renormalization.

## AC1d post-pinbackfill gates

- At clean main HEAD `d362d2286a6fa23e4f3c6ec3a12fdf7d0e66c352`, the default check and this TaskPath each returned `EXIT=0` with 3 warnings; `verify_pins.ps1` returned `EXIT=0` with 18/18 pins; API inventory returned `EXIT=0` with `1/79/6=86`. All commands are recorded with timestamps, generated HEAD, and EXIT in `post-ac1d-pinbackfill-gates-d362d228.log`; the worktree was clean before and after.

## AC2/AC3 implementation and verification

- Implementation is limited to the released AC2/AC3 scope. The R0 implementation branch is `codex/fea-15-pin-basis-enforce-1`: checker/template/test implementation `fd84360219fddf1e0b7611c1da1a088d5635593c`, STATUS-budget-safe fixture adjustment `5e216dc53102ff93db39124b97ab85d88f18643b`, and R-001 negative tests `ee0b25ac07dd6d9d756e98c3f10adaf4ffadce57` (current implementation HEAD; clean).
- A separate validation clone overlays the implementation on main baseline `dd6372420a459cdc9a4c39377f663f1b5d0d8646`. Initial candidate `a2a3401…` was followed by the test-only R-001 commit; final validation HEAD is `bf377705783da10eebcf6585316178984ef663d8`. Clone-local `core.autocrlf=false`, `core.longpaths=true`; clean before and after. The final candidate contains the same four implementation/test file blobs as the corresponding implementation branch commits.
- At implementation HEAD `5e216dc…`, with `core.autocrlf=true`, `python -m pytest tools/governance/tests/test_canonical_evidence_basis.py -q` returned `13 passed, 2 subtests passed`, `EXIT=0`. This run exercises the legacy blob alternative where the working-tree bytes differ from the Git blob.
- At validation HEAD `a2a3401…`, with `core.autocrlf=false`, the same focused command returned `11 passed, 2 skipped, 2 subtests passed`, `EXIT=0`; the two skips are cases that require different blob/worktree bytes, which are identical in this checkout. `test_architecture_assertions.py -q` returned `31 passed, 43 subtests passed`, `EXIT=0`.
- The requested full suite `python -m pytest tools/governance/tests -q` at validation HEAD returned `56 passed, 2 skipped, 3 failed, 55 subtests passed`, `EXIT=1`. All three failures are in `test_residual_runtime_identity.py`; the scanner reports 169 `TABLE_DELIMITER` errors, first at `doc/tasks/CHAPTER-SELECTOR-1.md`. The same three tests fail at unmodified main baseline `dd637242…` under the same `core.autocrlf=false` configuration (`3 failed, 9 passed`, `EXIT=1`, same 169 errors). `clean_workspace.py` and historical Task files are unchanged by this implementation; the baseline failure is recorded as a limitation and was not edited in this Task.
- At validation HEAD `a2a3401…`, default and this TaskPath governance checks each returned `EXIT=0` with 3 warnings; API inventory returned `EXIT=0` with `1/79/6=86`. `verify_pins.ps1` returned `EXIT=1` in the `core.autocrlf=false` clone with C04b/C17 EOL mismatches; the same two mismatches reproduce at unmodified baseline `dd637242…`. On the existing main checkout (`core.autocrlf=true`) at that baseline, `verify_pins.ps1` returned `EXIT=0`, all 18 pins. No pin, contract, `.gitattributes`, or historical Task bytes were changed.
- At the original AC2/AC3 validation checkpoint, AC4's cross-checkout matrix and AC5's four historical TaskPaths, post-integration gate bundle, independent review, and final adjudication were **NOT_RUN**. Those earlier logs remain limited to their recorded checkpoint; current AC4 evidence is below.

## AC2/AC3 independent Review

- Fresh, read-only ZCode CLI `0.17.1` session `sess_6b151e7e-8133-4b6a-ae6f-3c47296e5b7a` reviewed base `bfae0b9bd6a9b85a9a546d2adda0b684783ddb24` through implementation HEAD `5e216dc53102ff93db39124b97ab85d88f18643b`; initial review turn `turn_f7833d05-4c82-435e-bf53-7107ffc59c82`. It returned `APPROVED_WITH_LIMITATIONS`, no P0/P1 code findings, and AC2/AC3 `PASS` within the released scope.
- Review finding R-001 (P2) recommends extra negative tests for malformed row arity, invalid SHA/commit, and repository-boundary direction cases. The reviewer judged this non-blocking for the literal AC3 list and deferred disposition to an independent ZCode adjudication. Six P3 observations are informational; README implementation hash typo was corrected in main `06432c1fb94b7fe8a81c575a27076868a448a074`.
- The same fresh Review session, follow-up turn `turn_ade3c4aa-3c7f-426a-85ac-060dcf566544`, explicitly retracted P3-6. Microsoft Learn documents that PowerShell 7.4+ preserves native stdout bytes when redirecting to a file; the task's logs record PowerShell 7.6.9. The old and new implementations therefore use the same byte basis on this project's runtime; the new implementation removes temporary-file I/O and reduces runtime-version dependence. The correction and source link are preserved in the Review report.
- The reviewer could not directly run `git status` on the implementation worktree; Codex separately verified it clean at the reviewed head. The Review is not AC5 final adjudication, does not authorize AC4/AC5, and does not approve Task integration or closure. The complete report is [`FEA-15-PIN-BASIS-ENFORCE-1-ac2-ac3-zcode-review-2026-11-12.md`](../../doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac2-ac3-zcode-review-2026-11-12.md).
- At main HEAD `3e05096b3ea256c5136abccc8b735464462cb351`, post-Review default and this TaskPath checks each returned `EXIT=0` with 3 warnings, `verify_pins.ps1` returned `EXIT=0` with 18/18 pins, and API inventory returned `EXIT=0` with `1/79/6=86`; full command output is `ac2ac3-post-review-gates.log`.

## Versioned artifacts

| File | Purpose | SHA-256 / result |
|---|---|---|
| `capture_pin_basis_baseline.py` | Runtime rebinding wrapper; only the released path/input/output constants are rebound; original generator parsing/hash logic and `ROOT` are unchanged | `e4300b7bdbca9870e3b50354e011d955dfd56236d45a2d95b90fedf52073a03a` |
| `pin-inventory-2df8db7.json` | Formal base inventory | `3c6e39a269437873e2bb9b40c4b3c9461bcafaa1d171f240dfed322565bc1ce2` |
| `pin-inventory-delta-repro-e9f7bb1.json` | Frozen default delta reproduction anchor | `27ab6ac6f3e1c2213d6bfcd6acec11d16c94f1025a1e02abb0465bb90c523323`; exact match |
| `pin-inventory-delta-e9f7bb1-to-2df8db7.json` | Formal current-universe delta; its two changed rows are accepted by Addendum 4 as a one-time transition | `d737fcc75efcf10ab24ef55be75d5b6538c9acea1939450a5516867a652a95ea` |
| `pin-r194-matrix-2df8db7.json` | Fixed four-sample boundary matrix; byte-for-byte copy from retained A clone | `e8c48163d5c552b337a478326d7e7e8d7c637c2304741c66b579f48ce6a70246`; `EXIT=0` |
| `ac1c-a-gates-8d1d75ca.log` | A-side default, four historical TaskPath, pins, API, and matrix commands with times and EXIT | default/TaskPaths/pins `EXIT=1`; API/matrix `EXIT=0` |
| `r0-main-gates-bfae0b9.log` | Clean main R0 default/TaskPath/pins/API gates with generated HEAD, timestamps, and EXIT | all four `EXIT=0` |
| `ac1c-b-r0-assertions-taskpath-bfae0b9.log` | B R0 file presence, allowed diff scope, 24 blob comparisons, environment, and only permitted TaskPath | assertions `PASS`; TaskPath `EXIT=0` |
| `ac1d-canonical-evidence-blob-audit-0851085.log` | AC1d pre-implementation audit of the 19 Canonical Evidence rows at generated HEAD `cdd5d258690471c8069d47f461f04a1ef9a306bd` | 19/19 commit:path and Git blob SHA checks `PASS`; `EXIT=0`; clean before/after |
| `FEA-15-PIN-BASIS-ENFORCE-1-ac1d-baseline-confirmation-2026-11-12.md` | Fresh ZCode AC1d baseline decision and adjudication boundaries | `AC1D_PASS`; only AC2/AC3 released |
| `post-ac1d-pinbackfill-gates-d362d228.log` | Clean main default, current TaskPath, pins, and API gates after AC1d Task pinbackfill | all four `EXIT=0`; 3 warnings on each governance check; pins 18/18; API 1/79/6=86 |
| `ac2ac3-basis-focused-autocrlf-true.log` | Focused basis tests on implementation branch at generated HEAD `5e216dc53102ff93db39124b97ab85d88f18643b` | `13 passed`, `EXIT=0`; blob/worktree EOL-different legacy case exercised |
| `ac2ac3-basis-focused-final.log` | Focused basis tests on final candidate at generated HEAD `a2a3401eb703c3ae7899375755c981eabbf47572` (`core.autocrlf=false`) | `11 passed, 2 skipped`, `EXIT=0`; skips require EOL-different bytes |
| `ac2ac3-architecture-tests.log` | Architecture checker fixture suite at generated HEAD `a2a3401eb703c3ae7899375755c981eabbf47572` | `31 passed, 43 subtests passed`, `EXIT=0` |
| `ac2ac3-full-pytest-final.log` | Full governance suite at generated HEAD `a2a3401eb703c3ae7899375755c981eabbf47572` | `56 passed, 2 skipped, 3 failed, 55 subtests passed`, `EXIT=1`; three baseline failures retained |
| `ac2ac3-candidate-gates.log` | Candidate default/TaskPath/pins/API at generated HEAD `a2a3401eb703c3ae7899375755c981eabbf47572` | default/TaskPath `EXIT=0`; false-checkout pins `EXIT=1` (C04b/C17); API `EXIT=0`, 1/79/6=86 |
| `ac2ac3-baseline-controls.log` | Unmodified main baseline control at `dd6372420a459cdc9a4c39377f663f1b5d0d8646` | same three residual suite failures and same two false-checkout pin mismatches; true-checkout pins `EXIT=0`, 18/18 |
| `ac2ac3-source-overlay-audit.log` | Four implementation/test Git blobs compared between implementation HEAD `5e216dc53102ff93db39124b97ab85d88f18643b` and validation HEAD `a2a3401eb703c3ae7899375755c981eabbf47572` | 4/4 identical, `EXIT=0` |
| `ac2ac3-post-review-gates.log` | Main default/TaskPath/pins/API checks after AC2/AC3 Review report commit | `EXIT=0`; 3 warnings on each governance check; pins 18/18; API 1/79/6=86 |
| `doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac2-ac3-zcode-review-2026-11-12.md` | Fresh ZCode AC2/AC3 Review and same-session P3-6 correction | `APPROVED_WITH_LIMITATIONS`; AC2/AC3 PASS; R-001 P2 disposition awaits fresh adjudication |
| `ac2ac3-r001-negative-tests-retry2.log` | R-001 negative tests at implementation HEAD `ee0b25ac07dd6d9d756e98c3f10adaf4ffadce57` | `17 passed, 9 subtests passed`; `EXIT=0`; clean before run |
| `ac2ac3-r001-negative-tests-attempt1-metadata-gap.log` | First R-001 test run | Tests `17 passed, 9 subtests passed`, `EXIT=0`; `CORE_AUTOCRLF` capture is blank, so retry2 is the environment-qualified record |
| `ac4-clone-t-gates-actual.log` / `ac4-clone-f-gates-actual.log` | T/F default, TaskPath, 18 pins, API, focused suite at candidate `bf377705783da10eebcf6585316178984ef663d8` | T checks FAIL (Plan budget), pins 16 mismatch, API PASS; F checks PASS, pins 2 mismatch, API PASS; focused tests `EXIT=0` both |
| `ac4-clone-creation-audit.log` | T/F fresh clone settings and checkout-order audit | Final T/F config values are recorded, but their last-write timestamps follow the checkout reflog time; this audit does not prove settings preceded checkout. T/F output shape is consistent with intended modes; `EXIT=0` |
| `ac4-clone-t-pin-eol-normalization-retry2.log` | T-side pin mismatch normalization | 16/16 equal frozen pin and candidate blob after CRLF→LF; `EXIT=0` |
| `ac4-generator-integrity-t-retry2.log` / `ac4-generator-integrity-f-retry2.log` | Frozen inventory generator identities in T/F | 2/2 sources match HEAD/base blob and pin in each clone; `EXIT=0` each |
| `ac4-clone-t-pin-eol-normalization.log` / `ac4-generator-integrity-f.log` / `ac4-inventory-audit.log` and `.json` | Superseded preflight attempts | `EXIT=1`; helper assumptions/parsing were corrected; see current status note and retry2 logs; no product/source file changed |
| `ac4-inventory-r0.json` | R0 inventory at `bfae0b9bd6a9b85a9a546d2adda0b684783ddb24` | SHA-256 `425692adcaddf8a9ab6d86ef3aff885d6056cddd84fa17f3dbc108c7913de8b3`; 5455 rows |
| `ac4-clone-t-inventory.json` / `ac4-clone-f-inventory.json` | T/F candidate inventories at `bf377705783da10eebcf6585316178984ef663d8` | T SHA-256 `d4e9ec69117fd747398397d8ef3b879efe2fa53dbbbf8f7ea24d2f91933ec709`; F SHA-256 `4c81ff65ba345e10c00d5e0bc90f89c02f31b167ba467fbd7fd8b28756d64a62`; 5462 rows each |
| `ac4-inventory-delta-r0-to-bf377705783da10eebcf6585316178984ef663d8-t.json` / `...-f.json` | Frozen generator deltas R0→candidate | Both `+8/-1/~0`; T SHA-256 `80dfa9175e9317f3f461bad7b32208298616c05cfa4451d4c078533a3996daa1`; F SHA-256 `7137ee43077a1ce4f7bbc21c209144bc99838849fa683b92fc85cdc82e16b1b1` |
| `ac4-inventory-audit-retry2.json` / `.log` | Exact paths, row identities and historical target bytes audit | 11/11 changed paths allowed; 4737 unchanged historical paths, 0 failures; `EXIT=0`; JSON SHA-256 `a9e8d1795900b1a6adcec1e9860b8d8a4654392c21cd2a2a039e7cc2c76c18dd` |
| `ac1a-delta-repro-e9f7bb1.log` | Reproduction command, UTC start, HEAD, mapping, source/input/output hashes, EXIT | `EXIT=0` |
| `ac1a-inventory-2df8db7.log` | Formal inventory command, UTC start, HEAD, environment, source/output hashes, EXIT | `EXIT=0` |
| `ac1a-delta-e9f7bb1-to-2df8db7.log` | Formal delta command, UTC start, HEAD, mapping, source/input/output hashes, EXIT | `EXIT=0`, stop condition recorded |

All three generators were loaded from the base clone using `importlib`; `sys.dont_write_bytecode=True`. The inventory script rebound only `OUT`. The delta reproduction rebound only `OUTPUT`; the formal delta rebound only the Addendum 2-approved `BASELINE`, `EXPECTED_BASELINE_HEAD`, `CURRENT`, and `OUTPUT`. The fixed matrix generator ran through the released wrapper and wrote `pin-r194-matrix-2df8db7.json` to the retained A clone; SHA-256 `e8c48163d5c552b337a478326d7e7e8d7c637c2304741c66b579f48ce6a70246`. Historical output paths were not overwritten.

## External resource

The fixed A clone and R0 clone remain retained; R0 contains its Task-local inventory output. Implementation worktree G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/implementation is on codex/fea-15-pin-basis-enforce-1 at 7eefb54dc5ca74ddf9cc5459eb40fb10769a44e1, clean. Validation clone G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/validation-ac2ac3 is at candidate 4ed7f32b3ce9104ecee11aad593bde222055a0df, core.autocrlf=false, core.longpaths=true, clean. T/F clones are at the same candidate and retain the intended final config values; the v2 audit timestamps do not prove those values were written before checkout (P2-2). Each has only Task-local inventory/delta JSONs untracked. All clones and worktrees are preserved; no cleanup, prune, GC, or repack was performed.

## 当前执行状态（2026-11-12；以下优先于此前的历史状态）

- AC1 已由 Addendum 4、AC1c A 裁决与 AC1d 确认收口；AC2/AC3 实现分支最新提交为 7eefb54dc5ca74ddf9cc5459eb40fb10769a44e1，候选验证 HEAD 4ed7f32b3ce9104ecee11aad593bde222055a0df。该提交增加 R0 与候选在修改后 PNG 工作树字节下的 legacy blob fallback 对照测试，并让正向夹具要求完整治理检查 EXIT=0 和 Governance check: PASS。在实现 worktree clean HEAD 上专项测试为 18 passed, 9 subtests passed，EXIT=0。
- 新鲜 ZCode AC2/AC3 Review session sess_fb32a1da-f389-4e0a-b1dc-226bfd412284 / turn turn_219eedb3-126b-44eb-b3ea-1e2cd2bcd144 审查 HEAD bf377705783da10eebcf6585316178984ef663d8，结论 APPROVED_WITH_LIMITATIONS。P1-1 要求核验旧六列表 PNG blob fallback 字节语义；P1-3 要求正向测试验证整个 checker 成功；P1-2 指出其当时未见 AC2/AC3 artifacts 与 card pinbackfill。P1-1/P1-3 后续修复在实现 HEAD 7eefb54dc5ca74ddf9cc5459eb40fb10769a44e1 与候选 4ed7f32b3ce9104ecee11aad593bde222055a0df 得到 fresh Review 确认；Review、receipt、证据提交与 Task pinbackfill 均已完成。四个历史 TaskPath 在 AC5 实跑前保持 NOT_RUN。
- AC4 v2 对照在 Windows fresh clones 使用相同候选 HEAD 4ed7f32b3ce9104ecee11aad593bde222055a0df：T=core.autocrlf true、F=false，两侧 core.longpaths true，最终配置值与输出 EOL 形态相符；但 clone audit 时间戳不证明设置先于 checkout（P2-2）。首次两组 gate 调用实际子进程 CWD 错落在主仓库；四份 wrong-CWD 日志明确作废不用于结果。采用工具级 native CWD=克隆目录重跑的记录为 ac4-v2-t-gates-nativecwd.log 与 ac4-v2-f-gates-nativecwd.log。
- AC4 T：default 与本 TaskPath 均因 Plan 工作树 7035/7000 bytes 超限 EXIT=1（各 2 warnings）；verify_pins.ps1 因 16 个 EOL 工作树字节 mismatch EXIT=1；API EXIT=0；专项测试 18 passed, 9 subtests passed、EXIT=0。AC4 F：default 与本 TaskPath PASS、各 3 warnings、EXIT=0；pins 仅 C04b/C17 mismatch、EXIT=1；API EXIT=0；专项测试 16 passed, 2 skipped, 9 subtests passed、EXIT=0。两个 skip 是 F checkout 下不可区分的 EOL 分支，不计作覆盖通过。
- C1：T 的 16 个 mismatch 文件逐项 CRLF→LF 后与冻结 pin 及候选 HEAD blob 一致，16/16、EXIT=0，见 ac4-v2-t-pin-eol-normalization.log。C2：T/F 两侧冻结 inventory generators 均 2/2 与 R0/source/HEAD blobs 及 SHA 一致，分别 EXIT=0，见 ac4-v2-generator-integrity-t.log 与 ac4-v2-generator-integrity-f.log。
- AC4 v2 inventories：R0 5455 行；T/F 各 5462 行。T/F row identity/SHA 集一致，均 ADDED=8 / REMOVED=1 / CHANGED=0；8 条新增来自本 Task，唯一移除行由同 ID 的更新 README pin 替代。其余 4737 个历史 evidence paths 中，1032 raw-equal、3705 在 T 侧仅 CRLF→LF 后一致，0 failures。v2 inventory、delta 和 audit 文件 SHA 见对应日志及 Canonical Evidence；审计 FILE_DIFF=PASS、ALLOWED_PATH_EOL=11/11、EXIT=0，audit JSON SHA-256 acd19f03d677eb410dfa88274fd0c348e2c13d74f65403fa43512cc3f8906486。
- AC4 v2 fresh ZCode Review session sess_426becfe-44b9-4e2e-9f16-9eaccdddbd05 / turn turn_80b3a6dd-0d90-4edf-b60f-c95ab3fd9f94 returned APPROVED_WITH_LIMITATIONS（P0/P1=0）。Fresh AC4 adjudication session sess_b3fbf940-0ae4-446e-9eb0-e3d29e347451 / turn turn_718a6417-c6ea-407e-8b4c-63ccd198ed4b decided AC4 ACCEPT_WITH_LIMITATIONS; P2-1/P2-2 ACCEPT_AS_LIMITATION; AC5 RELEASED conditionally under the exact scope in the adjudication report. R-001 and Review-R-001 remain open; Linux and four historical TaskPaths remain NOT_RUN.
- 主仓库 post-pinbackfill gates 在 HEAD da3336391674d4a1cff6983849b570cf1e9e4d88：default / 本 TaskPath PASS、各 3 warnings、EXIT=0；18 pins EXIT=0；API EXIT=0，日志 main-post-pinbackfill-gates-da3336391.log。完整 suite 与 post-pinbackfill gate 日志均已入库于 32f229f26；此前 a9ca17988 post-evidence gates 也全 EXIT=0。外部实现、验证、R0、AC4 T/F 克隆均保留，不执行清理、prune、GC 或 repack。该处 main gate 记录为历史 checkpoint；后续 fresh ZCode AC4 adjudication 已条件释放 AC5，当前状态以本 README 末尾裁决摘要和 Task 卡最新 rolling checkpoint 为准。

## AC2/AC3/AC4 v2 fresh independent Review and evidence-quality findings (2026-11-12)

- ZCode CLI fresh read-only session sess_426becfe-44b9-4e2e-9f16-9eaccdddbd05 / turn turn_80b3a6dd-0d90-4edf-b60f-c95ab3fd9f94 reviewed main HEAD 7f1e7173e7638c79e024985ad91b18a073df727c, implementation HEAD 7eefb54dc5ca74ddf9cc5459eb40fb10769a44e1, and AC4 candidate 4ed7f32b3ce9104ecee11aad593bde222055a0df. Verdict: APPROVED_WITH_LIMITATIONS, P0=0/P1=0. Report: doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac2-ac3-ac4-v2-zcode-review-2026-11-12.md; raw CLI receipt: ac2-ac4-current-review-zcode-cli-20261112.jsonl.
- AC2/AC3 P1-1 and P1-3 remediations are sufficient per the fresh Review. The subsequent fresh AC4 adjudication accepted AC4 with limitations and conditionally released AC5; this is not final Task acceptance.

### P2-1: distinguish generation-time worktree SHA from Canonical Evidence Git-blob SHA

The six generation logs report generation-time output hashes, which match the current main worktree bytes for these six JSON artifacts. Canonical Evidence pins the committed Git-blob bytes; in the current Windows checkout these differ because the worktree contains CRLF. All six current worktree files become byte-identical to their pinned Git blobs after removing CR bytes. The values below were independently recalculated from current worktree bytes and git show HEAD:<path>:

| Generated artifact | Worktree SHA-256 recorded by generation log | Git-blob SHA-256 / Canonical pin |
|---|---|---|
| ac4-v2-inventory-audit.json | acd19f03d677eb410dfa88274fd0c348e2c13d74f65403fa43512cc3f8906486 | ac321500f01b342516dbec4d7f48083cea5a44bc3479b05c0c2476ff5e472c92 |
| ac4-inventory-r0.json | 425692adcaddf8a9ab6d86ef3aff885d6056cddd84fa17f3dbc108c7913de8b3 | 578b9e30933c5d8807da8a2687c8adc903bbcce58c1653adca61a3d8437af0e9 |
| ac4-v2-clone-t-inventory.json | fd1916eb1cb4b16f6fa7a0da316e21f684111f6cef5c9251dcc759e4f09c6bc0 | 6d29d0fd54141f74c22b9ff4b283d7f74d514b37b92191c8d4aed0d6a9e5b5aa |
| ac4-v2-clone-f-inventory.json | 1e680f71fdd8cebb70607b5458f8ee8b1cffe9dc03e803b7846b63a40388450c | 5206e4c5d3ab2a86b2bb1d35154d8ad3edc0f4f5d93602d49dd08212dec780f0 |
| ac4-inventory-delta-r0-to-4ed7f32b3ce9104ecee11aad593bde222055a0df-t.json | bbc48c6f7249f503a591a2f40a08a73cc55968c24ec669895290219f1d7953ef | 9daceedc583621725bff1691b7fd2ca815fce90fabab304c4cbdbf128a64e623 |
| ac4-inventory-delta-r0-to-4ed7f32b3ce9104ecee11aad593bde222055a0df-f.json | f055bb1ad4a12c70343b4675837bf77c7c3d76f5798f2a6b064681477fa4caea | ae697e5c58c669bf7ae9c649f49fc6248e50d424925071f0e58e4972cf926eb3 |

For example, the audit JSON is 28,227 worktree bytes with 577 CR bytes; removing CR yields the exact 27,650-byte Git blob. The logged generation hashes are valid for their stated worktree outputs; they must not be described as the Canonical Git-blob pin. This is an evidence-labeling limitation, not evidence of content alteration. Keep the historical logs and pins unchanged.

### P2-2: clone-creation audit does not prove configuration preceded checkout

ac4-v2-clone-creation-audit.log records CHECKOUT_REFLOG_UTC=2026-11-12T06:20:42+08:00 (22:20:42Z), while CONFIG_LAST_WRITE_UTC is 22:21:20.9076373Z for T and 22:21:29.4210567Z for F. These recorded config timestamps are 38.9 and 47.4 seconds later than the checkout reflog timestamp; the audit started at 22:21:18Z. Therefore this log does not prove that the recorded settings were written before checkout, despite the prior summary wording. The resulting T/F settings and EOL output behavior are consistent with the intended modes, but the sequence remains unproven. Per AC4 adjudication session sess_b3fbf940-0ae4-446e-9eb0-e3d29e347451, accept this as an evidence-quality limitation. Keep the historical log; no current or future document may claim the order was proven. Do not infer a proven ordering. The original sampler/clone-creation script and raw config/reflog source were not preserved with this log; the field names alone do not establish whether the audit rewrote config or which exact reflog event was sampled. The AC5 Handoff must record this evidence limitation and avoid asserting provenance beyond the recorded timestamps.

### P3-1: implementation-to-candidate commit mapping

Implementation HEAD 7eefb54dc5ca74ddf9cc5459eb40fb10769a44e1 is not an ancestor of validation candidate 4ed7f32b3ce9104ecee11aad593bde222055a0df; the candidate is a cherry-pick replay based on main dd6372420. The four checked implementation/test file blobs match. Record this mapping when planning integration so the exact candidate shape is explicit.

- AC4 current state: ACCEPT_WITH_LIMITATIONS; P2-1/P2-2 ACCEPT_AS_LIMITATION. AC5 conditionally RELEASED but integration and AC5 gates have not run. T Plan budget and pin mismatches remain FAIL; full suite 3 failed / EXIT=1 remains FAIL; Linux and four historical TaskPaths are NOT_RUN until executed under AC5. R-001 and Review-R-001 remain open.
- ZCode CLI raw Review receipt：外部原件 G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/zcode-ac2-ac4-current-review-20261112.jsonl，SHA-256 F61710BFF588A4C94FD9056E3A7E8D19E530BEFCD06E9FA37CA68FFBD4B0F3A6，CLI EXIT=0；仓库证据副本为 verification/FEA-15-PIN-BASIS-ENFORCE-1/ac2-ac4-current-review-zcode-cli-20261112.jsonl。外部原件保留。

## Post-review main gates at b199cf383

Generated at main HEAD b199cf38329651cbe0d6fc15d7d2934fe6d3c6b5, process CWD G:/CODEX/New Manga:

- pwsh -NoProfile -File tools/governance/check.ps1: PASS, 3 warnings, EXIT=0.
- pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md: PASS, 3 warnings, EXIT=0.
- pwsh -NoProfile -File tools/governance/verify_pins.ps1: 18/18 pins, EXIT=0.
- python tools/generate_api_inventory.py --check: IReaderProgressSink 1 / IHostController 79 / IRunController 6 / total 86, EXIT=0.

The complete timestamped command/output record is verification/FEA-15-PIN-BASIS-ENFORCE-1/main-review-pinbackfill-gates-b199cf383.log and was committed at c20fe22a1. A later final Task-pinbackfill gate run at main HEAD 139ae06223d0458a97e8f37c5ef5b7480f3410b2 also returned EXIT=0 for all four commands. ZCode then adjudicated AC4 ACCEPT_WITH_LIMITATIONS and conditionally released AC5; the task remains in progress.

## AC4 adjudication and conditional AC5 release (2026-11-12)

- ZCode independent adjudication session sess_b3fbf940-0ae4-446e-9eb0-e3d29e347451 / turn turn_718a6417-c6ea-407e-8b4c-63ccd198ed4b reviewed main HEAD 139ae06223d0458a97e8f37c5ef5b7480f3410b2. Decision: AC4 ACCEPT_WITH_LIMITATIONS; P2-1/P2-2 ACCEPT_AS_LIMITATION; AC5 RELEASED conditionally. Formal report: doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac4-adjudication-2026-11-12.md. Raw CLI receipt: ac4-adjudication-zcode-cli-20261112.jsonl.
- P2-1 is accepted as a byte-basis labeling limitation. Keep the six SHA pairs above and state that generation-log hashes represent generation-time output bytes while Canonical Evidence pins Git-blob bytes. Preserve the historical logs and pins.
- P2-2 is accepted as an evidence-quality limitation. The clone audit does not prove configuration preceded checkout; no document may claim that ordering. AC5 documentation must clarify both timestamp fields and either add ordering evidence or retain the limitation. No T/F gate rerun is required by the adjudication.
- AC5 is released only for the bounded integration and post-integration gates in the adjudication report. Integrate the four commits from implementation branch fd84360219fddf1e0b7611c1da1a088d5635593c through 7eefb54dc5ca74ddf9cc5459eb40fb10769a44e1 into current main by cherry-pick/equivalent content. Do not merge candidate 4ed7f32b3ce9104ecee11aad593bde222055a0df; it is not reachable in main. Verify the four file blobs and record the 7eef ↔ 4ed ↔ integrated-head map.
- Required AC5 gates after integration: default check, this TaskPath, AGPL-RELEASE-1, AD002-FOLLOWUPS-1, FEA-06-PREREQ-1, CHAPTER-SELECTOR-1, 18 pins, and API inventory. The three full-suite failures remain FAIL/EXIT=1 if the suite is run; the adjudication does not require it.
- R-001 and Review-R-001 remain open for final Integrator disposition; Linux remains NOT_RUN; four historical TaskPaths remain NOT_RUN until AC5 execution. AC5 integration Review, final adjudication, and Task completion are not done.

- ZCode CLI raw AC4 adjudication receipt: external original G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/zcode-ac4-adjudication-20261112.jsonl, SHA-256 7F6C73B24A59AFA5D912196F9E16832DBEE90F03057B973FA322CF4F661AD1A9, CLI EXIT=0; repository copy verification/FEA-15-PIN-BASIS-ENFORCE-1/ac4-adjudication-zcode-cli-20261112.jsonl. External original retained.

## Post-AC4 adjudication Task-card gates at 211987767

Generated at main HEAD 211987767278dd730769bb592db990488e59a46c, process CWD G:/CODEX/New Manga, after updating AC4/AC5 status and Task pointers:

- pwsh -NoProfile -File tools/governance/check.ps1: PASS, 3 warnings, EXIT=0.
- pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md: PASS, 3 warnings, EXIT=0.
- pwsh -NoProfile -File tools/governance/verify_pins.ps1: 18/18 pins, EXIT=0.
- python tools/generate_api_inventory.py --check: IReaderProgressSink 1 / IHostController 79 / IRunController 6 / total 86, EXIT=0.

The full timestamped record is verification/FEA-15-PIN-BASIS-ENFORCE-1/main-post-ac4-release-card-gates-211987767.log. These governance gates validate the updated Task/STATUS/Plan; AC5 implementation and integration gates remain NOT_RUN. Next: cherry-pick the four authorized implementation commits and verify the four file blobs before running AC5 gates.

## Post-AC4 Task pinbackfill gates at 6c5d0015 (preliminary working-tree run)

Generated at `HEAD=6c5d0015f0dde91eb2b1418ee313aa760d6d30a0`. At execution time, the Task card Canonical Evidence pinbackfill was present as an uncommitted working-tree change; therefore this is retained as a preliminary run, not a clean committed-state gate record. The TaskPath check read the updated card and passed; a clean committed-state run is still required before integration.

- Default governance check: PASS, 3 warnings, `EXIT=0`.
- FEA-15 TaskPath check: PASS, 3 warnings, `EXIT=0`.
- Frozen pins: 18/18, `EXIT=0`.
- API inventory: 1/79/6 = 86, `EXIT=0`.

Timestamped command/output log: `verification/FEA-15-PIN-BASIS-ENFORCE-1/main-post-ac4-card-pinbackfill-gates-6c5d0015.log`. Its generated HEAD and process output are preserved as observed; the working-tree qualification above is based on the contemporaneous Git status.

## Clean committed-state post-AC4 card gates at c16d3fff

Generated at main HEAD `c16d3fff945100d23648eee77c5c602a62552555` with an empty `git status --porcelain`, after the Task Canonical Evidence pinbackfill was committed:

- Default governance check: PASS, 3 warnings, `EXIT=0`.
- FEA-15 TaskPath check: PASS, 3 warnings, `EXIT=0`.
- Frozen pins: 18/18, `EXIT=0`.
- API inventory: IReaderProgressSink 1 / IHostController 79 / IRunController 6 = 86, `EXIT=0`.

Timestamped command/output log: `verification/FEA-15-PIN-BASIS-ENFORCE-1/main-clean-post-ac4-card-gates-c16d3fff.log`. This is a clean committed-state pre-integration run; AC5 integration gates remain pending.

## AC5 integration and required gate results (2026-11-12)

The four authorized implementation commits were cherry-picked onto main in order. The resulting implementation head is `e69fc2dc7a5f6ec68c9a881c1e25599cfe634da3`; candidate commit `4ed7f32b3ce9104ecee11aad593bde222055a0df` was not merged, and that commit object is absent from the main repository. T/F validation clones were read only for the candidate blob comparison.

| Source path | Implementation / candidate / integrated SHA-256 | Git blob in integrated head | Result |
|---|---|---|---|
| `tools/governance/check.ps1` | `1a6f7ab38e1b3fad80c9c282880c74e77bbbb81e6300653af3678d0694a6cff2` | `a320c034494c31b7ba8c9fd8e7f685cb917692e4` | Match in implementation `7eefb54`, candidate 4ed T/F, integrated `e69fc2dc` |
| `doc/templates/TASK.md` | `89371702736ae5756ceacf96c9e3e93ff10b2517aa38a1f253095f69361afc7c` | `574b82d7414f9f700858a3acbc296b6da6c60fc8` | Match in implementation `7eefb54`, candidate 4ed T/F, integrated `e69fc2dc` |
| `tools/governance/tests/test_canonical_evidence_basis.py` | `2b82fb2d0eacc0f664a6464ffe4e34ffed2a8022bf938295e8195ea32569fd0f` | `aabe8e14b9c649d5f53ab053b19822817ab1a75b` | Match in implementation `7eefb54`, candidate 4ed T/F, integrated `e69fc2dc` |
| `tools/governance/tests/test_architecture_assertions.py` | `26f79e8a2d6b2d26e2e2e2320800c787b8535698de1a852b1ed63b24a9169e57` | `e9b0bbc7c598ea39dc9eba1a1cc8605a8a741635` | Match in implementation `7eefb54`, candidate 4ed T/F, integrated `e69fc2dc` |

Commit mapping: `fd84360219fddf1e0b7611c1da1a088d5635593c` → `d363b13dca5a517734c90f56daf2593f9e4c22bc`; `5e216dc53102ff93db39124b97ab85d88f18643b` → `6e2db2e904f35d2e5c54c6fb643e323b6222c071`; `ee0b25ac07dd6d9d756e98c3f10adaf4ffadce57` → `3ec23cc4688174a8597862ce07603c1ae38f573a`; `7eefb54dc5ca74ddf9cc5459eb40fb10769a44e1` → `e69fc2dc7a5f6ec68c9a881c1e25599cfe634da3`.

The blob map is recorded in `verification/FEA-15-PIN-BASIS-ENFORCE-1/ac5-integration-blob-map-e69fc2dc7.log`; it was generated at the clean integration HEAD and includes SHA-256 and Git blob IDs for implementation, both candidate clones, and integration.

The required AC5 gates were run at clean main HEAD `e69fc2dc7a5f6ec68c9a881c1e25599cfe634da3`. The complete timestamped command/output record is `verification/FEA-15-PIN-BASIS-ENFORCE-1/ac5-integrated-gates-e69fc2dc7.log`.

| Gate | Result |
|---|---|
| Default `check.ps1` | PASS, 3 warnings, `EXIT=0` |
| FEA-15 TaskPath | PASS, 3 warnings, `EXIT=0` |
| `AGPL-RELEASE-1` TaskPath | PASS, 3 warnings, `EXIT=0` |
| `AD002-FOLLOWUPS-1` TaskPath | PASS, 3 warnings, `EXIT=0` |
| `FEA-06-PREREQ-1` TaskPath | FAIL, 13 errors / 3 warnings, `EXIT=1` |
| `CHAPTER-SELECTOR-1` TaskPath | FAIL, 6 errors / 3 warnings, `EXIT=1` |
| Frozen pins | 18/18, `EXIT=0` |
| API inventory | IReaderProgressSink 1 / IHostController 79 / IRunController 6 = 86, `EXIT=0` |

The FEA-06 TaskPath reports historical canonical evidence SHA mismatches, a missing `AppearanceCoordinator.cs` path, unregistered evidence-directory files, and historical DONE/resource/AC-state violations. The CHAPTER-SELECTOR TaskPath reports a missing Resource Manifest and missing v3 AC status markers for AC1–AC5. These are observed failures in the historical Task cards. No historical Task or evidence file was edited, and no gate failure is reclassified as PASS. The AC5 adjudication requires stopping on these failures for Integrator disposition.

The full governance pytest suite was not rerun because it is not an AC5 required gate; its earlier `61 passed / 2 skipped / 3 failed / EXIT=1` record remains FAIL. Linux remains `NOT_RUN`. R-001 and Review-R-001 remain open. AC5 Handoff, fresh independent Review, and separate final adjudication are pending; the Task remains `in_progress` and is not accepted or closed.

Preserved limitations for the pending Handoff: P2-1 keeps the six worktree-SHA/Git-blob-SHA pairs and the distinction “generation-log SHA = generation-time worktree bytes; Canonical pin = Git blob bytes.” P2-2 remains an evidence-quality limitation: the audit records T/F config last-write times after the checkout reflog time, the original sampler/script is unavailable, and the audit does not prove config-before-checkout. Do not assert that ordering.

## Fresh AC5 ZCode Review (2026-11-12)

- Independent read-only Review: fresh ZCode session `sess_3e7c8eaa-c247-4cb2-beeb-8fa8be8975c2`, turn `turn_cc3cd65c-0cf2-4995-87cb-036883a20fb2`, CLI `EXIT=0`. Reviewed main HEAD `fea5c742afe4ecdb1e3e6a8116bc0c18f1cabeb1`, implementation integration `e69fc2dc7a5f6ec68c9a881c1e25599cfe634da3`, and four authorized files. Verdict `APPROVED_WITH_LIMITATIONS` (P0=0 / P1=0 / P2=1 / P3=3); report: `doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac5-zcode-review-2026-11-12.md`; raw receipt: `verification/FEA-15-PIN-BASIS-ENFORCE-1/zcode-ac5-integration-review-20261112.jsonl`.
- The Review's P2-A found the stale clone-audit summary row that said settings preceded checkout. This row is corrected above under the already released AC4 P2-2 documentation condition; the underlying historical audit log is unchanged. No document now claims the ordering was proven.
- The Review's P3-C said post-pinbackfill gates had not been rerun. A clean four-gate run had in fact been executed at HEAD `fea5c742afe4ecdb1e3e6a8116bc0c18f1cabeb1` after the Task pinbackfill and before the Review: default, this TaskPath, 18 pins and API all `EXIT=0`. At Review time its log was only in the task workspace and was not among the Review inputs. The log is now copied to `verification/FEA-15-PIN-BASIS-ENFORCE-1/main-post-ac5-card-pinbackfill-gates-fea5c742a.log`; the Task will pin it. This corrects the assertion that the gates were not run; the separate evidence-pinning gap is closed by this follow-up.
- P3-B (redundant validation branch in the legacy SHA checker) and P3-D (whole-worktree clean status for external clones not independently proven) remain for the final Integrator disposition; no source fix or clone cleanup was performed. The Review does not adjudicate the two historical TaskPath failures, close R-001 / Review-R-001, or mark this Task done.
- External raw receipt retained at `G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/zcode-ac5-integration-review-20261112.jsonl`, SHA-256 `3164B313C7D00A2FED668BE0D885231398614A791630560C1724F93B779F8776`, CLI `EXIT=0`. The post-pinbackfill gate log's SHA-256 is `E51609034637F085549B75EAEC37D54B5AFA85FB9302AC78258FFC49C84DAC0E`.

## Post-Review card-check checkpoint and Plan budget correction

- At clean committed HEAD `6dad54fe6f131ff0c9ed88ff6feed6e4a04c8ffa`, default and FEA-15 TaskPath checks returned `FAIL/EXIT=1` because the updated `doc/REBASELINE_PLAN.md` measured 7013 bytes, over its 7000-byte limit. Pins remained 18/18 `EXIT=0`; API inventory remained 1/79/6=86 `EXIT=0`. The complete failed run is retained in `main-post-ac5-review-card-pinbackfill-gates-6dad54fe6.log` and is not reclassified.
- The FEA-15 plan row was shortened within the authorized current-pointer scope; Plan is now 6999 bytes. At clean HEAD `88a97d46d97485d1f3003d04ab0598a845c423b7`, the default check, FEA-15 TaskPath, 18 pins and API inventory all returned `EXIT=0` (checks each had 3 warnings). Full record: `main-post-plan-budget-fix-gates-88a97d46d.log`.
- These corrective gates only verify the Task/status pointer update. The two historical TaskPath failures from the required AC5 run at integration HEAD `e69fc2dc` remain `FAIL/EXIT=1` pending final ZCode Integrator adjudication.

## Final AC5 ZCode Integrator adjudication (2026-11-12)

- Fresh ZCode session `sess_1bff86d4-2618-42f8-841c-8a701eed4933`, decision turn `turn_1f3df43f-3f02-4b8a-be7a-b19c86539dfa`, report turn `turn_d9624924-6c57-4f00-9abe-de49278ece70`; reviewed clean main HEAD `7661a63fafc638ea09ea340b346e999ab6923bb2`. Decision: AC5 `MET_WITH_LIMITATIONS`; Task terminal status `closed_with_limitations` after closeout; report: `doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac5-final-adjudication-2026-11-12.md` (SHA-256 `8041AAB063B9633F4974D876D3EDAD9534A27406B2F36E31077316AB0BA4FD3A`); raw receipt: `zcode-ac5-final-adjudication-20261112.jsonl` (SHA-256 `002323A55C0566D9F32F26F91A064950201465F3B5089D2CB9A8196CD8A30A67`, CLI `EXIT=0`).
- The two historical TaskPath failures remain `FAIL/EXIT=1`: `FEA-06-PREREQ-1` (13 errors) and `CHAPTER-SELECTOR-1` (6 errors). ZCode accepts them as documented historical limitations based on an indirect evidence chain, not same-environment A/B proof. No historical Task/evidence bytes are changed or reclassified.
- `Review-R-001` is closed. `R-001` remains conditional until a full-row Canonical Evidence Git-blob audit returns `EXIT=0`; do not close it before that audit. P2-1/P2-2 remain accepted limitations; P2-A resolved; P3-B accepted as non-blocking, P3-C resolved by evidence, P3-D accepted as a limitation.
- Supplementary clean post-pinbackfill gates at HEAD `7661a63fafc638ea09ea340b346e999ab6923bb2`: default and TaskPath each PASS with 3 warnings / `EXIT=0`; frozen pins 18/18 / `EXIT=0`; API inventory 1/79/6=86 / `EXIT=0`. The original timestamped log is copied to `main-post-ac5-final-card-pinbackfill-gates-7661a63fa.log` and remains separately pinned in the closeout Task card.
- Full governance suite remains `61 passed / 2 skipped / 3 failed / EXIT=1`; Linux `NOT_RUN`. Neither is rewritten as PASS. No push or resource cleanup is authorized.

## Post-adjudication card-pinbackfill gates (2026-11-12)

- Generated at clean main HEAD `e5f115ff2392f6a6be4d8158a76769c68f9b81b2`, `PROCESS_CWD=G:\CODEX\New Manga`, empty `GIT_STATUS_PORCELAIN`; default check and this TaskPath each PASS with 3 warnings / `EXIT=0`; `verify_pins.ps1` 18/18 / `EXIT=0`; API inventory 1/79/6=86 / `EXIT=0`.
- Timestamped command/output log: `main-post-final-adjudication-card-pinbackfill-gates-e5f115ff2.log`. External original SHA-256 `6D971A9827F59BA745CA7DDF4609CB60AC46B887A1302A9337F6D8177A20BE35`; copied into this evidence directory. This run verifies the Task card pinbackfill at e5f115ff; it does not replace the required final clean-head gates after terminal closeout.

## R-001 full-row blob audit and latest card-pinbackfill gates (2026-11-12)

- Full Canonical Evidence audit generated at clean `main` HEAD `fbfc7de07ef51e1cf0372cfafb526bf81aaf71c6`: all 53 rows had an existing `commit:path` blob and matching SHA-256; `PASS_ROWS=53`, `FAIL_ROWS=0`, `EXIT=0`. The timestamped row-by-row log is `canonical-evidence-blob-audit-fbfc7de07.log`; external original SHA-256 `0A6503D5B2FFF463E31DBF5C514BC29C58EA3B9EB06735FE84B75DC58B0F1968`. This satisfies ZCode's R-001 audit condition; the Task Closeout Record will record `R-001=CLOSED` after the audit log is committed and pinned.
- At the same clean HEAD, default and this TaskPath checks each PASS with 3 warnings / `EXIT=0`; frozen pins 18/18 / `EXIT=0`; API inventory 1/79/6=86 / `EXIT=0`. Raw command log: `main-post-final-adjudication-card-pinbackfill-gates-fbfc7de07.log`; external original SHA-256 `67BAF710C6FA51A199F7A14DBE3D09B1251BB76ED44446636BA9CEFCEBA0D052`.
- Both logs were copied into this evidence directory; their external originals remain preserved. No historical Task/evidence bytes changed. The final clean-head gate run after terminal closeout remains pending.

## R-001 full-section audit correction (2026-11-12; supersedes earlier 53-row claim)

The earlier `53/53 PASS` records (`canonical-evidence-blob-audit-fbfc7de07.log` and the corresponding interim attempt) covered only the first Canonical Evidence table. The parser stopped at explanatory prose and did not include the continuation tables, so those runs do **not** satisfy R-001's full-card audit condition. Their raw bytes and historical commits remain unchanged; the earlier statement above that the audit satisfied R-001 is superseded by this correction.

A full-section audit at clean main HEAD `d4c4d9ffbbd3a59f79f4cd242dac19ffa23af1eb` scanned the entire Canonical Evidence section through `## Resource Manifest`: `PARSED_ROWS=88`, `PASS_ROWS=76`, `FAIL_ROWS=12`, `EXIT=1`. The row-by-row log is `canonical-evidence-blob-audit-full-section-d4c4d9ffb.log`, SHA-256 `20BE3B23212E55D007C52BDF3D9716BDFDA193CEF70887BD0E6359E8B3E0696C`. It is preserved unchanged. The independent ZCode review confirmed the scope/counts and all 12 mismatch values; 1 row has an incorrect commit reference, 10 rows have evidenced worktree/original-versus-Git-blob EOL basis differences, and 1 row has a truncated SHA pin.

ZCode's follow-up adjudication (session `sess_14d54cdc-c657-466a-9678-23eb966f8ea1`, turn `turn_4707ecd4-9c3c-4132-a3c3-f8cd8af535c9`) authorizes the bounded active-card corrections in its report. At this correction point, R-001 remains **OPEN** and the Task remains `in_progress`; the final full-section audit must return `EXIT=0` before R-001 can close. See [the full-audit adjudication](../../doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-r001-full-audit-adjudication-2026-11-12.md), [the remediation adjudication](../../doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-r001-remediation-adjudication-2026-11-12.md), and [the README scope clarification](../../doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-r001-readme-scope-clarification-2026-11-12.md).

The 18 frozen pins, historical Task/Review/Handoff/checkpoint/evidence bytes, raw logs, and external workspace originals remain unchanged. The historical Handoff's `53/53` text is retained as historical content and is superseded by the new adjudication; no historical file is rewritten. No prior audit `FAIL` is reclassified as `PASS`.

## Corrected full-section audit before final pinbackfill (2026-11-12)

At clean main HEAD `3832e459cb867c4ea2e953673e81151d00c53ed8`, the corrected active Task card contained 98 Canonical Evidence data rows. The full-section Git-blob audit returned `PARSED_ROWS=98`, `PASS_ROWS=98`, `FAIL_ROWS=0`, `EXIT=0`. The log is `canonical-evidence-full-section-audit-3832e459.log`; it records the generated HEAD, empty `git status --porcelain`, section range, command and per-row result. The clean-head default governance check, FEA-15 TaskPath, 18 frozen pins, and API inventory at the same HEAD all returned `EXIT=0` (the two check commands each emitted the 3 existing warnings). Gate log: `main-post-r001-card-correction-gates-3832e459.log`.

These results validate the authorized 12-row correction and the 98 rows then present. R-001 remains **OPEN** and the Task remains `in_progress` because these two logs and the independent final Review evidence still need their Canonical Evidence pins, followed by a full-section audit of the post-pinbackfill card. The 98/98 result is not the terminal closeout audit. No historical FAIL was changed, and no frozen pin or source evidence was modified.

## R-001 101-row audit and post-evidence gate run (2026-11-12)

At clean main HEAD `daaed8112d0c79a7b5e827442847071180a2e577`, the full-section Git-blob audit parsed and passed all 101 then-pinned Canonical Evidence rows (`101/101`, `EXIT=0`). Its log is `canonical-evidence-full-section-audit-daaed811.log`; SHA-256 `C6C96129EAE22BCEFC8F02B8D0D33D3A32EBD459794823C29384F9F128CDAF16`.

After that audit and log were committed, clean main HEAD `4fa651d803c29783e6db9a2eaf85ea6baa30464e` was verified: default and FEA-15 TaskPath governance checks each PASS with 3 warnings / `EXIT=0`; frozen pins 18/18 / `EXIT=0`; API inventory 1/79/6=86 / `EXIT=0`. The complete command/output record is `main-post-r001-review-pinbackfill-gates-daaed811.log`, SHA-256 `61E3622AB89C5CA60F06E93C1B73FD97F676E7C47DAF7598BCDD40792F6B2688`.

Both logs are retained in the verification directory and their workspace originals remain preserved. These gates preceded the active-card pinbackfill for the two logs. R-001 remains **OPEN**, the Task remains `in_progress`, and the independent Review plus a full-section audit after card pinbackfill are pending. Earlier audit failures and limitations remain unchanged.

## Superseding correction: gate-log byte sources and run identity (2026-11-12)

The preceding 101-row section conflated two different gate runs and attributed the wrong byte digest to the external source. The repository file `main-post-r001-review-pinbackfill-gates-daaed811.log` is the run generated at clean HEAD `daaed8112d0c79a7b5e827442847071180a2e577` (`GENERATED_UTC=2026-11-12T02:35:31Z`), even though it was committed in `4fa651d803c29783e6db9a2eaf85ea6baa30464e`. Its Git blob SHA-256 is `e95abcebc0f44f5781225668c84673ae65b105bb7370dfc8f561408766614a68`. The previous `61e3622a…` value was measured from the main worktree file, which contained one CR byte; removing that byte yields the pure-LF Git blob.

The external workspace file `post-evidence-commit-gates-4fa651d.log` is a separate run generated at HEAD `4fa651d803c29783e6db9a2eaf85ea6baa30464e` (`GENERATED_AT=2026-11-12T10:37:29+08:00`). Its actual SHA-256 is `cab7acda91859e48a7fd68a9f225e42277fa4c6a7bd3f1456227fcb320c9aba9`; it contains 160 CR bytes, and removing them yields `ac0f5d6b251c1a89deff456509960c85de3d5d65e8a9f68177feb4f0bfc3afd9`, not the repository blob. Both runs independently record default check, TaskPath, pins, and API `EXIT=0`. The prior Resource Manifest entry's `61E…` association with this external source is inaccurate; its bytes remain unchanged under the ZCode adjudication boundary, and this correction records the discrepancy.

At clean HEAD `fe6e447ad85741c4364f3be678cd3676c41f0f10`, the full-section audit returned `PARSED_ROWS=103`, `PASS_ROWS=102`, `FAIL_ROWS=1`, `EXIT=1`. The preserved failure log is `canonical-evidence-full-section-audit-fe6e447ad.log` (SHA-256 `ABF4CD9C0A0C19D5F20105715D36563F0CC452AB17BE9CDDB2DF7FC8C13918E2`); ZCode's separate adjudication authorized the single Canonical SHA field correction and is recorded in the pinned Task report. This failed run is not reclassified. R-001 remains **OPEN** pending fresh independent Review and a later full-section audit.

## R-001 corrected-card independent Review (2026-11-12)

Fresh ZCode CLI session `sess_1037261b-dc28-4248-a059-71e96d63556e` / turn `turn_339865a0-4018-4a6c-aec9-40aab84c8a6a` performed a read-only Review of clean main HEAD `674e01cc9ef59e5df384e4964cd625a17ede4c1f`. Verdict: `APPROVED` (`P0=0 / P1=0 / P2=0`), with no finding against the authorized correction. The report is `doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-r001-correction-review-2026-11-12.md`; the raw CLI receipt is `zcode-r001-correction-review-20261112.jsonl`.

Two non-blocking P3 observations remain for closeout: P3-O1 asks that the report-metadata correction commit (`98f8d17aa`) be noted in Closeout/Handoff; P3-O2 records a duplicated word in the preserved ZCode adjudication heading. Neither changes the SHA result or scope. R-001 remains **OPEN** and the Task remains `in_progress` until the post-Review full-section audit and terminal gates complete. Earlier FAIL and NOT_RUN results remain unchanged.

## R-001 terminal closeout failure and ZCode adjudication (2026-11-12)

- The terminal-state candidate at HEAD `e59469986553a63876a2685ad4388f1d65df58a6` produced `FAIL (43 errors, 4 warnings) / EXIT=1`. The unchanged original log is `preliminary-closeout-gates-e59469986-fail.log` (workspace-original SHA-256 `B08A7C4E537E9416D2711A71B6ED797E32CB01DB8EC76E849099BCEF42F0F752`); its classification remains FAIL.
- After restoring the active Task and STATUS to `in_progress` / R-001 OPEN, the recovery run at the same HEAD returned default check, TaskPath, frozen pins, and API inventory `EXIT=0`; both check runs had three warnings. The original log is `post-failure-recovery-gates-e59469986-r2.log` (workspace-original SHA-256 `E2BE6C7EFD64F68044B9E3D4466A216DD36011DA0BC0AB575F658D0A72FBD067`).
- The existing post-pinbackfill complete-section Git-blob audit at clean HEAD `e59469986553a63876a2685ad4388f1d65df58a6` remains `120/120 PASS / EXIT=0`; log `canonical-evidence-full-section-audit-e59469986-post-pinbackfill.log` (workspace-original SHA-256 `F51D7FF82A028FEB7885A21FFE9AA14C8CD27C795FDCECCE78F7837A5222D4D1`). It predates the new adjudication pins and does not replace a later audit.
- ZCode's fresh read-only ruling (`AUTHORIZE_BOUNDED_CLOSEOUT_NORMALIZATION`, session `sess_2a379865-1182-4371-9b7c-63e47ef8b603`, turn `turn_27b225f9-9f41-4f6b-b2fb-a9dec02ba719`, CLI `EXIT=0`) authorizes pinning the failure/recovery/audit evidence, normalizing unprotected Resource Manifest rows, and exactly one change to protected row 61E: delete only the literal `SHA-256 ` prefix after rechecking the referenced worktree file still hashes to `61E3622AB89C5CA60F06E93C1B73FD97F676E7C47DAF7598BCDD40792F6B2688`. Any drift or missing workspace resource is a stop condition. Full report: `../../doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-r001-terminal-closeout-adjudication-2026-11-12.md`; raw receipt: `zcode-r001-closeout-manifest-adjudication-20261112.jsonl` (workspace-original SHA-256 `E5F28AB4E95C17E9C7CA24DDA97D01D3BB74F155E0AF6BB9A9D5240851DD04C7`).
- R-001 remains OPEN and the Task remains `in_progress` until the authorized normalization, a fresh independent Review, terminal-state gates, and the final full-section audit all pass. No FAIL or NOT_RUN classification is changed.
## R-001 STATUS budget gate failure and ZCode adjudication (2026-11-12)

- At clean main HEAD `661211b548a5d17a7368457e04b37c3dd192a948`, the first post-normalization gate (`pwsh -NoProfile -File tools/governance/check.ps1`) returned `FAIL (1 error, 2 warnings) / EXIT=1`: `doc/STATUS.md` measured 3298 bytes against the 3200-byte limit; 31/45 lines. TaskPath, pins, API, and full-section audit were not run due the stop rule. Original log: `r001-post-normalization-gates-661211b54-budget-fail.log`; workspace-original SHA-256 `B3C7F66A60AD04DAFC513C821DFDA22E4DCBF6F5A54D7C13AE08FCDC713B0407`. This remains FAIL and is superseded only by a later clean retry.
- Fresh ZCode adjudication `AUTHORIZE_BOUNDED_STATUS_COMPRESSION_AND_RETRY`, session `sess_3b0755a2-981e-4f83-ab5f-b2584a0da0dd`, decision turn `turn_fb3b11b8-6b36-45dc-85d1-466fe7452ba3`, CLI `EXIT=0`, authorizes changing only the current Task summary on STATUS line 7. It must retain the Task link/id, `in_progress`, AC1–4 complete and AC4 limitation, the 43-error `EXIT=1` FAIL, the ZCode-authorized manifest normalization, R-001 OPEN, and pending independent Review/terminal gates/final full-section audit. Target STATUS size is ≤3190 bytes; all other STATUS lines stay byte-identical. Full ruling: `../../doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-r001-status-budget-adjudication-2026-11-12.md`; raw receipt: `zcode-r001-status-budget-adjudication-followup-20261112.jsonl`.
- After the failure log and ruling are pinned and the bounded STATUS edit is committed, rerun clean-head gates in order: default check, this TaskPath, `verify_pins.ps1` (18/18), API inventory (1/79/6=86), then full-section audit. Any nonzero exit stops work; preserve the result and keep Task `in_progress` / R-001 OPEN.
## R-001 clean-head retry after STATUS compression (2026-11-12)

At clean `main` HEAD `df6b5d7d418c5d9321c3089a085ab840e25fa628`, the bounded STATUS line-7 compression produced 3188 bytes; the other 30 lines match the adjudicated baseline byte-for-byte. Task remains `in_progress`, R-001 remains `OPEN`, and the prior terminal-candidate `43 errors / EXIT=1` remains FAIL.

- Default governance check: `EXIT=0`, 3 warnings.
- FEA-15 TaskPath check: `EXIT=0`, 3 warnings.
- Frozen pins: `18/18`, `EXIT=0`.
- API inventory: `IReaderProgressSink=1 / IHostController=79 / IRunController=6`, total 86, `EXIT=0`.
- Full-section Canonical Evidence Git-blob audit: `130/130 PASS`, `FAIL_ROWS=0`, `EXIT=0`.

Each raw log below records its generated HEAD and command-level exit status; the full audit also records branch and clean porcelain. These are the first clean retry results before their Task pinbackfill. External workspace originals remain preserved.

- `r001-post-status-compression-default-df6b5d7d41.log` — 643 bytes; workspace-original SHA-256 `b2e7eaf30241100b87804ed9107c19700e080a7bc7159a7f43cd93c948e2c276`.
- `r001-post-status-compression-gates-df6b5d7d41.log` — 7177 bytes; workspace-original SHA-256 `77f4c8e8d80bebcd3df4cde1a2654cb00055118af06be7b732c59660d4145905`.
- `r001-post-status-compression-full-section-audit-df6b5d7d41.log` — 39039 bytes; workspace-original SHA-256 `b78835304e6aa4e3f1823fe53accb468f59fbb8aaad7cd4eda28104411551273`.

R-001 remains **OPEN** pending a fresh independent Review, terminal-state gates, and the final full-section audit. No earlier FAIL or NOT_RUN result is reclassified.

## R-001 post-pinbackfill gates and 134-row audit (2026-11-12)

After the first clean retry logs and their four Canonical Evidence pins were committed, the Task pinbackfill HEAD `8f383aa60f9835843d0f0b3b51e4afb0e241f591` was rechecked from a clean `main` worktree.

- Default governance check: `EXIT=0`, 3 warnings.
- FEA-15 TaskPath check: `EXIT=0`, 3 warnings.
- Frozen pins: `18/18`, `EXIT=0`.
- API inventory: `1/79/6=86`, `EXIT=0`.
- Full-section Git-blob audit: `134/134 PASS`, `FAIL_ROWS=0`, `EXIT=0`; `GIT_STATUS_PORCELAIN` was empty.

These results cover the 134 Canonical Evidence rows present at `8f383aa60f`, including the first retry evidence pins. The two raw logs below contain generated HEAD and command-level EXIT values; their workspace originals remain preserved.

- `r001-post-pinbackfill-gates-8f383aa60f.log` — 7675 bytes; workspace-original SHA-256 `6ed5dd23e15db8a1e4940c58318414ba7c7f65353da12df571ee63ba89fffae1`.
- `r001-post-pinbackfill-full-section-audit-8f383aa60f.log` — 40285 bytes; workspace-original SHA-256 `00f94b9777fe7804d5cdea6fc53dc0fda2da6a0a0bc3bcdfd378d9cc796be4aa`.

Task remains `in_progress`, R-001 remains **OPEN**, and terminal-state gates plus the fresh independent Review are pending. Earlier FAIL and NOT_RUN classifications remain unchanged.

## R-001 review-ready clean-head gates and 137-row audit (2026-11-12)

At clean `main` HEAD `70423741c1c6499d57082ded5b7cdd691e58842b`, after pinning the 134-row post-pinbackfill evidence, default governance, this TaskPath, the 18 frozen pins, and API inventory each returned `EXIT=0`; default and TaskPath each emitted 3 warnings. API counts were `1/79/6=86`. The complete Canonical Evidence section audit passed `137/137`, `FAIL_ROWS=0`, `EXIT=0`, with empty `GIT_STATUS_PORCELAIN`.

These are review-ready clean-head results; the Task remains `in_progress` and R-001 `OPEN`. Logs:

- `r001-review-ready-gates-70423741c1.log` — 7675 bytes; workspace-original SHA-256 `c924e62cc24af7e73bb646ca8b3b85a18e9ebc87f29598bf652e702f47f5dfc5`.
- `r001-review-ready-audit-70423741c1.log` — 41199 bytes; workspace-original SHA-256 `885801a9e7b8ec30b55a2c94e76d2413478cf61fc94eee1426e86c1e972ba6f6`.

No historical FAIL or NOT_RUN classification changed.
