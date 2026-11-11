# FEA-15-PIN-BASIS-ENFORCE-1 evidence

## AC1 baseline checkpoint — transition accepted; AC1c A stopped pending adjudication

This remains a partial baseline result. ZCode release Addendum 4 accepts the exact historical delta below as a one-time transition and lifts the procedural STOP for AC1c A-side gates. This does not authorize implementation: AC1d independent baseline confirmation must pass first. No implementation was started.

- Fixed A clone HEAD: `2df8db7a4d19b591e919ecc6e8f8651167800ef0`.
- Runtime: Git `2.52.0.windows.1`; PowerShell `7.6.9`; Python `3.14.6`; `core.autocrlf=true`; clone-local `core.longpaths=true`.
- Before measurement, the corrected clone was detached at the exact base and `git status --porcelain` was empty. The first checkout emitted Windows `Filename too long` errors; after setting only this clone's `core.longpaths=true`, forced checkout returned `EXIT=0`, restored the sample files, and reported a clean tree. The first checkout's subcommand exit was not captured separately; it is not represented as a pass.
- Frozen-script reproduction anchor: `EXIT=0`; output SHA-256 exactly matched both the historical output and Addendum 2's pin `27ab6ac6f3e1c2213d6bfcd6acec11d16c94f1025a1e02abb0465bb90c523323`; `5,350 → 5,376`, added 26, removed 0, changed 0.
- Formal inventory: `EXIT=0`; `5,438` rows (`5,420` Task evidence rows + `18` frozen pins), measured at the fixed base. Inventory SHA-256: `3c6e39a269437873e2bb9b40c4b3c9461bcafaa1d171f240dfed322565bc1ce2`.
- Formal delta against the registered `e9f7bb1b48c885cb329848d2d3591e145ff3d229` inventory: `5,376 → 5,438`; `ADDED=62`, `REMOVED=0`, **`CHANGED=2`**. Added rows are attributed to `FEA-15-PIN-POLICY-1` (31), `GOV-CHECKER-NOTASK-1` (18), and `GOV-REFINCIDENT-1` (13). Delta SHA-256: `d737fcc75efcf10ab24ef55be75d5b6538c9acea1939450a5516867a652a95ea`.
- The two changed rows are both existing `FEA-15-PIN-POLICY-1` rows. Their identities and `pin_sha256` values are unchanged; the `class` values changed from empty to `CANONICAL` after the table header was simplified, and `release-gates.ac_gate` changed from `AC3 release baseline` to `AC3 release gates`. ZCode Addendum 4 attributes both to `d26c43c76576b0f514530874fc9cb04f016674e6` and accepts this exact `CHANGED=2` as a one-time transition. It must remain `CHANGED=2`, never be rewritten as zero. See `history-transition-ledger.md` and [Addendum 4](../../doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-zcode-release-adjudication-addendum4-2026-11-12.md).
- AC1c A-side run at main HEAD `8d1d75ca246ef0daf7f3c116974cf16cfa21d410`, A HEAD `2df8db7a4d19b591e919ecc6e8f8651167800ef0`: default and all four Addendum 4 historical TaskPaths returned `EXIT=1`; `verify_pins.ps1` returned `EXIT=1` with 16/18 mismatches; API returned `EXIT=0` (`1/79/6=86`); fixed boundary matrix returned `EXIT=0`, SHA-256 `e8c48163d5c552b337a478326d7e7e8d7c637c2304741c66b579f48ce6a70246`. Full command output is in `ac1c-a-gates-8d1d75ca.log`. FAIL is not PASS.
- The A clone had `core.autocrlf=true`, `core.longpaths=true`; raw porcelain showed only the Task-local untracked output directory (inventory, delta, reproduction, and matrix JSON), with no tracked changes. Its `REBASELINE_PLAN.md` Git blob is 6,992 bytes while the checked-out file is 7,056 bytes / 64 lines. Default, `AGPL-RELEASE-1`, and `AD002-FOLLOWUPS-1` failed the Plan budget; `FEA-06-PREREQ-1` also reported historical evidence hash/path/resource/closeout failures; `CHAPTER-SELECTOR-1` also reported missing resource-manifest and AC status markers. `verify_pins.ps1` mismatched C01b, C02, C03, C05, C06, C07, C08, C09, C10, C11, C12, C13, C14, C15, C16, and FEA01; C04b/C17 passed.
- Addendum 4 stop condition is active pending ZCode adjudication of these exact results. No A clone config, checker, historical file, or frozen pin was changed. B TaskPath remains **NOT_RUN** and is not PASS.

## Versioned artifacts

| File | Purpose | SHA-256 / result |
|---|---|---|
| `capture_pin_basis_baseline.py` | Runtime rebinding wrapper; only the released path/input/output constants are rebound; original generator parsing/hash logic and `ROOT` are unchanged | `e4300b7bdbca9870e3b50354e011d955dfd56236d45a2d95b90fedf52073a03a` |
| `pin-inventory-2df8db7.json` | Formal base inventory | `3c6e39a269437873e2bb9b40c4b3c9461bcafaa1d171f240dfed322565bc1ce2` |
| `pin-inventory-delta-repro-e9f7bb1.json` | Frozen default delta reproduction anchor | `27ab6ac6f3e1c2213d6bfcd6acec11d16c94f1025a1e02abb0465bb90c523323`; exact match |
| `pin-inventory-delta-e9f7bb1-to-2df8db7.json` | Formal current-universe delta; contains the two changed rows awaiting adjudication | `d737fcc75efcf10ab24ef55be75d5b6538c9acea1939450a5516867a652a95ea` |
| `pin-r194-matrix-2df8db7.json` | Fixed four-sample boundary matrix; byte-for-byte copy from retained A clone | `e8c48163d5c552b337a478326d7e7e8d7c637c2304741c66b579f48ce6a70246`; `EXIT=0` |
| `ac1c-a-gates-8d1d75ca.log` | A-side default, four historical TaskPath, pins, API, and matrix commands with times and EXIT | default/TaskPaths/pins `EXIT=1`; API/matrix `EXIT=0` |
| `ac1a-delta-repro-e9f7bb1.log` | Reproduction command, UTC start, HEAD, mapping, source/input/output hashes, EXIT | `EXIT=0` |
| `ac1a-inventory-2df8db7.log` | Formal inventory command, UTC start, HEAD, environment, source/output hashes, EXIT | `EXIT=0` |
| `ac1a-delta-e9f7bb1-to-2df8db7.log` | Formal delta command, UTC start, HEAD, mapping, source/input/output hashes, EXIT | `EXIT=0`, stop condition recorded |

All three generators were loaded from the base clone using `importlib`; `sys.dont_write_bytecode=True`. The inventory script rebound only `OUT`. The delta reproduction rebound only `OUTPUT`; the formal delta rebound only the Addendum 2-approved `BASELINE`, `EXPECTED_BASELINE_HEAD`, `CURRENT`, and `OUTPUT`. The fixed matrix generator ran through the released wrapper and wrote `pin-r194-matrix-2df8db7.json` to the retained A clone; SHA-256 `e8c48163d5c552b337a478326d7e7e8d7c637c2304741c66b579f48ce6a70246`. Historical output paths were not overwritten.

## External resource

The fixed A clone is retained at `G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/baseline-2df8db7` with `PRESERVE_REFERENCED`. Its checkout was verified clean before measurement; current porcelain contains only its Task-local untracked JSON outputs. The matrix JSON copy in this repository matches the clone output byte-for-byte. No cleanup, prune, GC, or repack was performed.
