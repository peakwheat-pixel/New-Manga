# AC4 — P02 AC3 分支的 25 条 pin：只读状态记录（已更正）

**Task**: GOV-DEBT-CLEANUP-2 · **AC**: AC4 · **性质**: 只读，不合并、不重钉

| 项 | 值 |
|---|---|
| 分支 | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` |
| 固定 head | `0af8980884e9d027042ef145cd966577d86b5bc5` |
| head 是否为当前 HEAD 祖先 | **no** |
| 分支上的证据文件 | 72 |
| 其中已在主分支入库 | 0 |
| Task pin 总数 | 25 |
| 在分支上存在 | 21 |
| 在分支上也不存在 | 4 |

## 状态结论（全部 25 条）

- **21 条在分支上存在**：状态 `ON_FIXED_BRANCH_NOT_MAINLINE`。
  只确认「该固定 head 有此路径」，**不视为主线 Canonical Evidence，不视为已集成，不重钉。**
- **4 条在分支上也不存在**：状态 `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED`。
  保留原引用与原 pin，不静默移除。

## 对本文件早期数字的更正（DSH 实测）

本文件最初记「23 条 / 18 存在 / 5 缺失」，并把
`doc/handoffs/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION-R1.md` 列为缺失。

**实测不符。** 用 `git cat-file -e 0af8980884e9d027042ef145cd966577d86b5bc5:<path>` 逐条核对，
该文件在固定 head 上**存在**；Task 的 Canonical Evidence 表实为 **25 行**（不是 23）。

| 项 | 早期记录 | 实测 |
|---|---:|---:|
| pin 总数 | 23 | **25** |
| 在固定 head 存在 | 18 | **21** |
| 在固定 head 不存在 | 5 | **4** |

错误原因：早期记录按目录名与印象汇总，未逐条对固定 head 求值。这类「汇总数字未经实测」
正是本 Task 要清理的债务类型，因此这里保留原数字并显式更正，而不是静默覆盖。

**4 条缺失项**（保留原引用，不删除、不重钉）：

```
verification/P02-NEW-TIME-BASELINE/codex-parent-integration-r1.md
verification/P02-NEW-TIME-BASELINE/codex-parent-integration-r1.json
verification/P02-NEW-TIME-BASELINE/codex-post-resolution-selftest-r1.meta.json
verification/P02-NEW-TIME-BASELINE/codex-post-resolution-selftest-r1.fixture-inventory.json
```

## 事实与方法

固定 head `0af8980884e9d027042ef145cd966577d86b5bc5` **不是**当前 HEAD 的祖先；
该分支上 72 个证据文件、0 个在主分支入库。所有 21 条「存在」仅为
`ON_FIXED_BRANCH_NOT_MAINLINE`，不构成主线证据、不视为已集成。

## 全部 25 条逐项记录（AC4 要求）

固定 head：`0af8980884e9d027042ef145cd966577d86b5bc5`。存在性用 `git cat-file -e <head>:<path>` 实测，blob 与大小同样实测。
**「存在」仅表示该固定 head 有此路径——不视为主线 Canonical Evidence，不视为已集成，不重钉。**

| evidence_id | path | pinned commit | 在固定 head 上 | blob | 大小 | 状态 |
|---|---|---|---|---|---|---|
| `P02-AC3-RESOLUTION-ZCODE-PREFLIGHT-R1` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/zcode-owner-preflight-r1.json` | `7f04eb3c3d6b3641ddd2eca24f2dcce44a7d2bd2` | 存在 | `e55d6fca1fe2` | 2820 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-ZCODE-PREFLIGHT-R2` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/zcode-owner-preflight-r2.json` | `671b8d0260e2d475bc26ad1307973e7f809d6d0d` | 存在 | `f04e7b40b4d7` | 2820 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-ZCODE-PREFLIGHT-R3` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/zcode-owner-preflight-r3.json` | `d12aafa5e3de8b06522ffe213f6b100ea8c8f2e9` | 存在 | `47b829666c46` | 2919 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-COLLECTOR-R1` | `tools/p02/p02-new-time-baseline.ps1` | `75c5cc4fc7100096aafe7f1e6e514c0eb7072526` | 存在 | `630833290e8e` | 97658 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-SELFTEST-SOURCE-R1` | `tools/p02/p02-new-time-baseline-selftest.ps1` | `75c5cc4fc7100096aafe7f1e6e514c0eb7072526` | 存在 | `519a48c77e9d` | 75441 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-HANDOFF-R1` | `doc/handoffs/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION-R1.md` | `4021c6389814c25ab2ea7bb9e6eb92df935ab2c9` | 存在 | `583e439ae852` | 11384 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-CODEX-SELFTEST-R1` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/codex-selftest-verify-r1.meta.json` | `62b27a7a9e66702125c9a7ca3b4fe71ec5570e77` | 存在 | `3e8aab995239` | 3898 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-FIXTURE-INVENTORY-CODEX-R2` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/selftest-temp-fixture-inventory-codex-r2.json` | `b5dea0e2d52ffd9391692b9a6dee3f3ea001e44d` | 存在 | `d43b0ec195f1` | 2250 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-CODEX-VERIFY-JSON-R1` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/codex-verify-ac3-resolution-r1.json` | `5b0d7c39abdbe51dc8d70aab3bf105c1a1c2bb29` | 存在 | `e2643d8e9137` | 5510 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-CODEX-VERIFY-MD-R1` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/codex-verify-ac3-resolution-r1.md` | `5965f573264032f9e8cb9b64abad8e6d819c39e7` | 存在 | `d0e5acbad2ed` | 1607 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-DSH-REVIEW-MANIFEST-R1` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/p02-ac3-resolution-dsh-review-evidence-manifest-r1.json` | `c5562afd7d3349613313ec090f995703f7f65abc` | 存在 | `30d2fcfaa490` | 7191 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-DSH-PREFLIGHT-R1` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/dsh-review-preflight-r1.json` | `08ac648a330d2d0eb738793c95e0cf06ee4ccb70` | 存在 | `0ac21e1cbcc7` | 2574 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-DSH-PREFLIGHT-R2` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/dsh-review-preflight-r2.json` | `08ac648a330d2d0eb738793c95e0cf06ee4ccb70` | 存在 | `622a93b1841d` | 2674 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-DSH-PREFLIGHT-R3` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/dsh-review-preflight-r3.json` | `e786349fa91e76c7071969958a13a09ce4a37148` | 存在 | `622a93b1841d` | 2674 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-DSH-MANIFEST-R2-CURRENT-VERIFY` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/dsh-evidence-manifest-r2-post-update-verify.stdout.json` | `e786349fa91e76c7071969958a13a09ce4a37148` | 存在 | `3af19f2a43c5` | 607 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-DSH-REVIEW-MANIFEST-R2` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/p02-ac3-resolution-dsh-review-evidence-manifest-r2.json` | `08ac648a330d2d0eb738793c95e0cf06ee4ccb70` | 存在 | `6906ede7e028` | 7854 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-DSH-SOURCE-REVIEW-R1` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/dsh-source-review-r1.md` | `2210b51904cd8b2eefc69ffd0dd94f3304b22bb5` | 存在 | `fc1e31c7f68e` | 12985 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-DSH-REVIEW-METADATA-R1` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/dsh-source-review-r1.meta.json` | `2210b51904cd8b2eefc69ffd0dd94f3304b22bb5` | 存在 | `580134e4ffae` | 4411 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-CODEX-ADJUDICATION-R1` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/codex-dsh-review-adjudication-r1.md` | `2210b51904cd8b2eefc69ffd0dd94f3304b22bb5` | 存在 | `7bcc820ba24e` | 3601 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-CONVERGENCE-R1` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/codex-convergence-ac3-resolution-r1.stdout.json` | `2210b51904cd8b2eefc69ffd0dd94f3304b22bb5` | 存在 | `57817ae057ac` | 1245 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |
| `P02-AC3-RESOLUTION-PARENT-INTEGRATION-R1` | `verification/P02-NEW-TIME-BASELINE/codex-parent-integration-r1.md` | `071ed5d0c9c445c901e2d450c23c15f927bfe6ca` | **不存在** | — | — | `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED` |
| `P02-AC3-RESOLUTION-PARENT-INTEGRATION-JSON-R1` | `verification/P02-NEW-TIME-BASELINE/codex-parent-integration-r1.json` | `071ed5d0c9c445c901e2d450c23c15f927bfe6ca` | **不存在** | — | — | `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED` |
| `P02-AC3-RESOLUTION-PARENT-SELFTEST-R1` | `verification/P02-NEW-TIME-BASELINE/codex-post-resolution-selftest-r1.meta.json` | `071ed5d0c9c445c901e2d450c23c15f927bfe6ca` | **不存在** | — | — | `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED` |
| `P02-AC3-RESOLUTION-PARENT-SELFTEST-FIXTURES-R1` | `verification/P02-NEW-TIME-BASELINE/codex-post-resolution-selftest-r1.fixture-inventory.json` | `071ed5d0c9c445c901e2d450c23c15f927bfe6ca` | **不存在** | — | — | `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED` |
| `P02-AC3-RESOLUTION-RESOURCE-CLOSEOUT-R1` | `verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/resource-closeout-r1.json` | `d77aa934db9e21282af1bbbbbb0263b4deb06a34` | 存在 | `510bb10fc064` | 6208 bytes | `ON_FIXED_BRANCH_NOT_MAINLINE` |

## 早期汇总中的缺失项（已被实测更正，见下）

| `doc/handoffs/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION-R1.md` | `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED` |
| `verification/P02-NEW-TIME-BASELINE/codex-parent-integration-r1.md` | `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED` |
| `verification/P02-NEW-TIME-BASELINE/codex-parent-integration-r1.json` | `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED` |
| `verification/P02-NEW-TIME-BASELINE/codex-post-resolution-selftest-r1.meta.json` | `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED` |
| `verification/P02-NEW-TIME-BASELINE/codex-post-resolution-selftest-r1.fixture-inventory.json` | `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED` |

## 明确未做的事

- 未合并该分支，也未 cherry-pick 任何提交。
- 未把 pin 改指向 worktree 绝对路径。
- 未从 Task 中删除任何引用。
- 未把该分支上的任何文件称为「已集成」。
- 未修改 `P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` 的 `integration_status`。
