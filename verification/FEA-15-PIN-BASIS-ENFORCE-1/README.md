# FEA-15-PIN-BASIS-ENFORCE-1 evidence

## AC1 baseline checkpoint — transition accepted; A-side resume pending

This remains a partial baseline result. ZCode release Addendum 4 accepts the exact historical delta below as a one-time transition and lifts the procedural STOP for AC1c A-side gates. This does not authorize implementation: AC1d independent baseline confirmation must pass first. No implementation was started.

- Fixed A clone HEAD: `2df8db7a4d19b591e919ecc6e8f8651167800ef0`.
- Runtime: Git `2.52.0.windows.1`; PowerShell `7.6.9`; Python `3.14.6`; `core.autocrlf=true`; clone-local `core.longpaths=true`.
- Before measurement, the corrected clone was detached at the exact base and `git status --porcelain` was empty. The first checkout emitted Windows `Filename too long` errors; after setting only this clone's `core.longpaths=true`, forced checkout returned `EXIT=0`, restored the sample files, and reported a clean tree. The first checkout's subcommand exit was not captured separately; it is not represented as a pass.
- Frozen-script reproduction anchor: `EXIT=0`; output SHA-256 exactly matched both the historical output and Addendum 2's pin `27ab6ac6f3e1c2213d6bfcd6acec11d16c94f1025a1e02abb0465bb90c523323`; `5,350 → 5,376`, added 26, removed 0, changed 0.
- Formal inventory: `EXIT=0`; `5,438` rows (`5,420` Task evidence rows + `18` frozen pins), measured at the fixed base. Inventory SHA-256: `3c6e39a269437873e2bb9b40c4b3c9461bcafaa1d171f240dfed322565bc1ce2`.
- Formal delta against the registered `e9f7bb1b48c885cb329848d2d3591e145ff3d229` inventory: `5,376 → 5,438`; `ADDED=62`, `REMOVED=0`, **`CHANGED=2`**. Added rows are attributed to `FEA-15-PIN-POLICY-1` (31), `GOV-CHECKER-NOTASK-1` (18), and `GOV-REFINCIDENT-1` (13). Delta SHA-256: `d737fcc75efcf10ab24ef55be75d5b6538c9acea1939450a5516867a652a95ea`.
- The two changed rows are both existing `FEA-15-PIN-POLICY-1` rows. Their identities and `pin_sha256` values are unchanged; the `class` values changed from empty to `CANONICAL` after the table header was simplified, and `release-gates.ac_gate` changed from `AC3 release baseline` to `AC3 release gates`. ZCode Addendum 4 attributes both to `d26c43c76576b0f514530874fc9cb04f016674e6` and accepts this exact `CHANGED=2` as a one-time transition. It must remain `CHANGED=2`, never be rewritten as zero. See `history-transition-ledger.md` and [Addendum 4](../../doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-zcode-release-adjudication-addendum4-2026-11-12.md).
- Default checker, the four historical `-TaskPath` checks, 18 pins, API, sample matrix, and current-TaskPath B clone remain **NOT_RUN** at this checkpoint. AC1c now permits the A-side checks to resume. B remains after the A evidence commit and pinbackfill; neither NOT_RUN state is PASS.
- Addendum 4 excludes `basis` / `basis_counts` from cross-environment invariance claims because fresh-checkout EOL differences reclassify observations. It also permits clone-local `core.longpaths=true`. The first checkout subcommand EXIT was not captured; that attempt is not PASS. On resumption, record A clone `git status --porcelain` and `core.longpaths` before running gates.

## Versioned artifacts

| File | Purpose | SHA-256 / result |
|---|---|---|
| `capture_pin_basis_baseline.py` | Runtime rebinding wrapper; only the released path/input/output constants are rebound; original generator parsing/hash logic and `ROOT` are unchanged | `e4300b7bdbca9870e3b50354e011d955dfd56236d45a2d95b90fedf52073a03a` |
| `pin-inventory-2df8db7.json` | Formal base inventory | `3c6e39a269437873e2bb9b40c4b3c9461bcafaa1d171f240dfed322565bc1ce2` |
| `pin-inventory-delta-repro-e9f7bb1.json` | Frozen default delta reproduction anchor | `27ab6ac6f3e1c2213d6bfcd6acec11d16c94f1025a1e02abb0465bb90c523323`; exact match |
| `pin-inventory-delta-e9f7bb1-to-2df8db7.json` | Formal current-universe delta; contains the two changed rows awaiting adjudication | `d737fcc75efcf10ab24ef55be75d5b6538c9acea1939450a5516867a652a95ea` |
| `ac1a-delta-repro-e9f7bb1.log` | Reproduction command, UTC start, HEAD, mapping, source/input/output hashes, EXIT | `EXIT=0` |
| `ac1a-inventory-2df8db7.log` | Formal inventory command, UTC start, HEAD, environment, source/output hashes, EXIT | `EXIT=0` |
| `ac1a-delta-e9f7bb1-to-2df8db7.log` | Formal delta command, UTC start, HEAD, mapping, source/input/output hashes, EXIT | `EXIT=0`, stop condition recorded |

All three generators were loaded from the base clone using `importlib`; `sys.dont_write_bytecode=True`. The inventory script rebound only `OUT`. The delta reproduction rebound only `OUTPUT`; the formal delta rebound only the Addendum 2-approved `BASELINE`, `EXPECTED_BASELINE_HEAD`, `CURRENT`, and `OUTPUT`. The matrix generator has not been run. Historical output paths were not overwritten.

## External resource

The fixed A clone is retained at `G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/baseline-2df8db7` with `PRESERVE_REFERENCED`. Its checkout was verified clean before measurement; measurement outputs are untracked inside that clone. No cleanup, prune, GC, or repack was performed.
