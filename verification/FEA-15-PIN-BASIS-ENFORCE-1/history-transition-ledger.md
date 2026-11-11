# FEA-15-PIN-BASIS-ENFORCE-1 history transition ledger

依据 [ZCode release Addendum 4](../../doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-zcode-release-adjudication-addendum4-2026-11-12.md)，记录一次性历史衔接。`e9f7bb1b48c885cb329848d2d3591e145ff3d229` 的 5,376 行快照保持不可改写；固定 `2df8db7a4d19b591e919ecc6e8f8651167800ef0` 的 5,438 行 inventory（SHA-256 `3c6e39a269437873e2bb9b40c4b3c9461bcafaa1d171f240dfed322565bc1ce2`）是本 Task 唯一后续历史不变性基线。

正式 delta 文件 SHA-256：`d737fcc75efcf10ab24ef55be75d5b6538c9acea1939450a5516867a652a95ea`。转接数字必须原样保留：`ADDED=62 / REMOVED=0 / CHANGED=2`。新增行按来源为 `FEA-15-PIN-POLICY-1` 31、`GOV-CHECKER-NOTASK-1` 18、`GOV-REFINCIDENT-1` 13。

| identity (`source_file / evidence_id / path / commit`) | before → after | unchanged `pin_sha256` | attribution |
|---|---|---|---|
| `doc/tasks/FEA-15-PIN-POLICY-1.md` / `release-adjudication` / `doc/reviews/FEA-15-PIN-POLICY-1-zcode-release-adjudication-2026-11-11.md` / `0730335f835306a19d283f06dbc0164134a9e04e` | `class`: `""` → `CANONICAL` | `3912a32cdd434d7d6df8a61be3d758600adc92d27f0e6c00cd4c4791a57b2092` | `d26c43c76576b0f514530874fc9cb04f016674e6` simplified the header so the frozen parser reads the class |
| `doc/tasks/FEA-15-PIN-POLICY-1.md` / `release-gates` / `verification/FEA-15-PIN-POLICY-1/release-gates-0730335.log` / `be4efb395a5dcf5fb03f51e48813b7c046f0d469` | `class`: `""` → `CANONICAL`; `ac_gate`: `AC3 release baseline` → `AC3 release gates` | `18258a64e59ed4387b85c07c5598ebf681f429a0e1edb5dc39f18afbe0e2682e` | `d26c43c76576b0f514530874fc9cb04f016674e6`; header parsing plus wording update in the same closeout commit |

The two rows retain their identity and `pin_sha256`; both are attributed to a prior registered closeout commit. This is an accepted one-time transition, not a repair or a zero-change result. Subsequent comparison of the frozen 5,438-row history against post-implementation inventory must preserve each historical identity and `pin_sha256`, with `deleted=0` and `changed=0` under the delta tool's four-field semantics. Task self-evidence rows are a separate increment layer. Any later `deleted>0`, `changed>0`, or unattributed addition stops work for ZCode adjudication.

## Environment observations and limits

- The recorded `basis_count_delta` is `BLOB +422`, `INCONSISTENT +81`, `MIXED -382`, `UNRESOLVED_COMMIT +271`, `WORKTREE -330` (all other categories 0). Addendum 4 attributes the reclassification to fresh-checkout EOL differences. `basis` / `basis_counts` are observations and are excluded from cross-environment invariance claims.
- The fixed A clone is detached at `2df8db7…`; clone-local `core.longpaths=true` is permitted. A forced checkout after setting it returned `EXIT=0`, clean status, and restored sample files. The initial checkout subcommand EXIT was not captured and is not represented as PASS. On AC1c resumption, record `git status --porcelain` and `git config --get core.longpaths` before gates; preserve the clone and its outputs.
- The Addendum 2 reproduction anchor was `EXIT=0`, exact SHA match `27ab6ac6f3e1c2213d6bfcd6acec11d16c94f1025a1e02abb0465bb90c523323`. No base checker, historical TaskPath, pins, API, sample matrix, or B TaskPath result is asserted by this ledger.
