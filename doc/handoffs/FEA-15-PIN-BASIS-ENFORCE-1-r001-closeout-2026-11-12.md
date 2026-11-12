---
task_id: FEA-15-PIN-BASIS-ENFORCE-1
author: Codex
recipient: ZCode
base_commit: d8b9b20869ac0957e152eddb9b5de88c8c2f9326
delivery_head: e69fc2dc7a5f6ec68c9a881c1e25599cfe634da3
status: delivered
---

# Handoff：FEA-15-PIN-BASIS-ENFORCE-1 R-001 closeout

## 交付结果

AC5 的 ZCode 最终裁决为 `MET_WITH_LIMITATIONS`，Task 终态为 `closed_with_limitations`。本 Handoff 记录集成结果、明确保留的失败与限制，以及 R-001 条件关闭规则。生成本文件时 Task 仍为 `in_progress`、R-001 为 `OPEN`；最终状态、最终全行 blob audit 和终态门禁以 Task 卡 Closeout Record 及其 Canonical Evidence 为准。

集成 base 为 `7f101e8e`，四个获准实现提交及 main 集成提交如下：

| Implementation source | Main integration commit |
|---|---|
| `fd84360219fddf1e0b7611c1da1a088d5635593c` | `d363b13dca5a517734c90f56daf2593f9e4c22bc` |
| `5e216dc53102ff93db39124b97ab85d88f18643b` | `6e2db2e904f35d2e5c54c6fb643e323b6222c071` |
| `ee0b25ac07dd6d9d756e98c3f10adaf4ffadce57` | `3ec23cc4688174a8597862ce07603c1ae38f573a` |
| `7eefb54dc5ca74ddf9cc5459eb40fb10769a44e1` | `e69fc2dc7a5f6ec68c9a881c1e25599cfe634da3` |

四个实现文件的 implementation、T/F candidate 与 integration Git blob 对照已通过。Candidate `4ed7f32b3ce9104ecee11aad593bde222055a0df` 仅用于 blob 对照，未集成且主仓库不可达。不得将其合入 main。

| AC | 结果 | 交付与限制 |
|---|---|---|
| AC1 | MET | 固定基线、inventory/delta 重算与 `ADDED=62 / REMOVED=0 / CHANGED=2` 一次性转接均有证据；A-side FAIL/PASS 原样保留。 |
| AC2 | MET | 新七列表 basis 校验与旧六列表兼容逻辑已集成。 |
| AC3 | MET | 新旧格式、basis、来源和负例测试已覆盖；focused suite 结果见 Task 卡证据。 |
| AC4 | MET_WITH_LIMITATIONS | ZCode 接受 P2-1/P2-2 为限制；Linux 为 `NOT_RUN`。 |
| AC5 | MET_WITH_LIMITATIONS | 两条历史 TaskPath FAIL 按 ZCode 裁决接纳为 documented historical limitation；不得改写历史卡、日志或 FAIL。 |

## 验证证据与状态

截至本 Handoff 生成时，最近已固定的活跃卡全节审计为 clean HEAD `e3e6a2e0e31cf257112ad57fe99cc1b4a0f6f239` 上 `152/152 PASS`、`FAIL_ROWS=0`、`EXIT=0`；对应 default、TaskPath、18 pins、API 四门均 `EXIT=0`。这不是终态卡最终审计。另有 clean HEAD `7661a63fafc638ea09ea340b346e999ab6923bb2` 的 post-pinbackfill 四门日志，结果均 `EXIT=0`，生成时工作树 clean；该日志的仓外原件保留，仓内副本及 SHA 见 Task 卡 Canonical Evidence。

| 检查项 | 结果 | 说明 |
|---|---|---|
| Final AC5 adjudication | `MET_WITH_LIMITATIONS` | ZCode fresh session `sess_1bff86d4-2618-42f8-841c-8a701eed4933`；decision turn `turn_1f3df43f-3f02-4b8a-be7a-b19c86539dfa`；报告及回执已在仓库证据中。 |
| Historical `FEA-06-PREREQ-1` TaskPath | `FAIL`, 13 errors, `EXIT=1` | ZCode 接纳为 documented historical limitation；不修改历史卡或证据。 |
| Historical `CHAPTER-SELECTOR-1` TaskPath | `FAIL`, 6 errors, `EXIT=1` | ZCode 接纳为 documented historical limitation；不修改历史卡或证据。 |
| Attribution | 间接证据链 | 高置信推论，不是同环境 A/B 重放证明；不得表述为绝对因果已证明。 |
| Full governance suite | `FAIL`, 61 passed / 2 skipped / 3 failed, `EXIT=1` | 三项同名失败在基线复现；原分类保持 FAIL。 |
| Linux | `NOT_RUN` | 无真实 Linux 运行证据，不推断为 PASS。 |
| R-001 | `CLOSE_CONDITIONAL_ON_FINAL_BLOB_AUDIT` | 对终态卡 Canonical Evidence 全部行验证 `commit:path` 存在且 Git blob SHA-256 等于 pin；audit `EXIT=0` 后在 Task Closeout Record 关闭。若失败则保持 OPEN、停止收口且不得修改 pin 凑绿。 |
| Review-R-001 | `CLOSE` | 四类负例覆盖与独立 Review 前置已满足；不等同于 R-001。 |

### P2-1：生成日志 worktree SHA 与 Canonical Git blob SHA

生成日志记录生成时工作树字节；Canonical pin 记录对应 commit 的 Git blob 字节。六对历史 SHA 如下，两个口径各自保留：

| Artifact | Generation log / worktree SHA-256 | Git blob SHA-256 / Canonical pin |
|---|---|---|
| `ac4-v2-inventory-audit.json` | `acd19f03d677eb410dfa88274fd0c348e2c13d74f65403fa43512cc3f8906486` | `ac321500f01b342516dbec4d7f48083cea5a44bc3479b05c0c2476ff5e472c92` |
| `ac4-inventory-r0.json` | `425692adcaddf8a9ab6d86ef3aff885d6056cddd84fa17f3dbc108c7913de8b3` | `578b9e30933c5d8807da8a2687c8adc903bbcce58c1653adca61a3d8437af0e9` |
| `ac4-v2-clone-t-inventory.json` | `fd1916eb1cb4b16f6fa7a0da316e21f684111f6cef5c9251dcc759e4f09c6bc0` | `6d29d0fd54141f74c22b9ff4b283d7f74d514b37b92191c8d4aed0d6a9e5b5aa` |
| `ac4-v2-clone-f-inventory.json` | `1e680f71fdd8cebb70607b5458f8ee8b1cffe9dc03e803b7846b63a40388450c` | `5206e4c5d3ab2a86b2bb1d35154d8ad3edc0f4f5d93602d49dd08212dec780f0` |
| T inventory delta | `bbc48c6f7249f503a591a2f40a08a73cc55968c24ec669895290219f1d7953ef` | `9daceedc583621725bff1691b7fd2ca815fce90fabab304c4cbdbf128a64e623` |
| F inventory delta | `f055bb1ad4a12c70343b4675837bf77c7c3d76f5798f2a6b064681477fa4caea` | `ae697e5c58c669bf7ae9c649f49fc6248e50d424925071f0e58e4972cf926eb3` |

### P2-2：checkout 设置时序未证明

T/F 配置最后写入时间与 checkout reflog 时间一致；原始 sampler/script 和 config/reflog 来源未留存，现有证据**不能证明配置先于 checkout**。这是永久 evidence-quality limitation。不得声称设置顺序已证明，也不要求重跑 T/F gates。

## Review findings 与限制

- Review P2-A（README 的旧时序口径）：`RESOLVED`，已修正为“不能证明设置先于 checkout”；历史 audit log 保持原样。
- Review P3-B（legacy SHA 分支冗余/重复报错）：`ACCEPT_AS_NON_BLOCKING`，本 Task 不改；若要改工具，须另行释放范围。
- Review P3-C（pinbackfill 后未重跑四门）：`RESOLVED_BY_EVIDENCE`；对应既有日志和后续预算失败/修正日志均如实保留。
- Review P3-D（外部 clone 全树 clean 未独立验证）：`ACCEPT_AS_LIMITATION`；受审路径由等价 blob 证据覆盖。
- 独立 corrected-card Review 的 P3-O1 要求记录报告元数据更正 commit `98f8d17aa`，已记录；P3-O2 的历史标题拼写保持原字节。
- Full suite、两条历史 TaskPath FAIL、Linux `NOT_RUN`、P2-1/P2-2 与 P3-D 均保留其真实分类。禁止把任何 FAIL/NOT_RUN 改写成 PASS。

## 资源与操作边界

所有外部 clone、worktree、原始日志、receipt 与派生产物均 `PRESERVE_REFERENCED`；不删除、不迁移、不归档、不运行 worktree prune、GC 或 repack。18 frozen pins、冻结契约、历史 Task/Review/Handoff/evidence 字节保持不变。全程不 push。

## 下一任务建议

- Task ID / 标题：无需下一步操作；`NEW-MANGA-V1-FULL-AUDIT` 仍因材料未传播而 blocked，且没有其他已释放 READY Task。
- 推荐 Agent / Reviewer：无需下一步操作。
- 推荐原因与前置依赖：本 Task 按 ZCode 裁决以 `closed_with_limitations` 收口；历史治理修复或新范围须另行释放 Task。
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `main`；实现 delivery head `e69fc2dc7a5f6ec68c9a881c1e25599cfe634da3`；最终 closeout HEAD 以 Task 卡为准。
- 允许修改路径：无需下一步操作。
- 禁止范围与新增授权条件：不得修改历史卡/证据、冻结契约/pins、批量迁移、清理资源或 push；均需单独释放/授权。
- 交付物：无需下一步操作。
- 验证命令、环境与完成 Gate：无需下一步操作。
- 可直接转发给 Agent 的指令：无需下一步操作。

## 风险与遗留

历史 TaskPath 的治理登记缺陷仍在；如需修复，须另开范围，不得在本 Task 中扩展。最终全行 blob audit 与终态四门的实测结果只以 Task 卡后续收口记录为准。
