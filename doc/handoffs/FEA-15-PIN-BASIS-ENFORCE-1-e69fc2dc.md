---
task_id: FEA-15-PIN-BASIS-ENFORCE-1
author: Codex
recipient: ZCode
base_commit: d8b9b20869ac0957e152eddb9b5de88c8c2f9326
delivery_head: e69fc2dc7a5f6ec68c9a881c1e25599cfe634da3
status: delivered
---

# Handoff：FEA-15-PIN-BASIS-ENFORCE-1

## 交付结果

AC5 已由 fresh ZCode Integrator adjudication 判为 `MET_WITH_LIMITATIONS`。目标 Task 终态是 `closed_with_limitations`；Task 卡和权威状态指针的最终 closeout 仍待本 Handoff pin 回填、最终全行审计和终态门禁。

四个获准实现提交按 cherry-pick 集成到 main；集成前 base 为 `7f101e8e`，delivery head 为 `e69fc2dc7a5f6ec68c9a881c1e25599cfe634da3`：

| Implementation source | Main integration commit |
|---|---|
| `fd84360219fddf1e0b7611c1da1a088d5635593c` | `d363b13dca5a517734c90f56daf2593f9e4c22bc` |
| `5e216dc53102ff93db39124b97ab85d88f18643b` | `6e2db2e904f35d2e5c54c6fb643e323b6222c071` |
| `ee0b25ac07dd6d9d756e98c3f10adaf4ffadce57` | `3ec23cc4688174a8597862ce07603c1ae38f573a` |
| `7eefb54dc5ca74ddf9cc5459eb40fb10769a44e1` | `e69fc2dc7a5f6ec68c9a881c1e25599cfe634da3` |

Changed paths are `tools/governance/check.ps1`, `doc/templates/TASK.md`, `tools/governance/tests/test_canonical_evidence_basis.py`, and `tools/governance/tests/test_architecture_assertions.py`. The validation candidate `4ed7f32b3ce9104ecee11aad593bde222055a0df` was used only for blob comparison; it is not integrated into main and is unreachable from the main repository.

## AC 对照

| AC | 结果 | 交付与限制 |
|---|---|---|
| AC1 | MET | 固定基线、inventory/delta 重算、`ADDED=62 / REMOVED=0 / CHANGED=2` 一次性转接均保留；ZCode 接受的 A-side FAIL/PASS 均原样记录。 |
| AC2 | MET | 新七列表 basis 校验与旧六列表兼容逻辑已集成。 |
| AC3 | MET | 负例覆盖含四项 Review-R-001 用例；实现分支专项测试 `18 passed, 9 subtests, EXIT=0`，候选 T/F 专项测试也分别有 `EXIT=0` 记录。 |
| AC4 | MET_WITH_LIMITATIONS | ZCode `ACCEPT_WITH_LIMITATIONS`；P2-1/P2-2 保留。T/F checkout 的历史 EOL 结果不重分类；Linux `NOT_RUN`。 |
| AC5 | MET_WITH_LIMITATIONS | 八项集成门禁均实跑；两条历史 TaskPath FAIL 由 ZCode 接纳为 documented historical limitation，详见下表和最终 adjudication。 |

## 验证证据

| AC/场景 | 实际命令或步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC5 集成门禁 | `pwsh -NoProfile -File tools/governance/check.ps1`；本 Task、`AGPL-RELEASE-1`、`AD002-FOLLOWUPS-1`、`FEA-06-PREREQ-1`、`CHAPTER-SELECTOR-1` TaskPath；`verify_pins.ps1`；`python tools/generate_api_inventory.py --check` | Windows main，clean `e69fc2dc7a5f6ec68c9a881c1e25599cfe634da3` | default、本 Task、AGPL、AD002、18 pins、API 均 `EXIT=0`；`FEA-06-PREREQ-1` FAIL（13 errors / `EXIT=1`）；`CHAPTER-SELECTOR-1` FAIL（6 errors / `EXIT=1`）。两条 FAIL 保持 FAIL。 | `verification/FEA-15-PIN-BASIS-ENFORCE-1/ac5-integrated-gates-e69fc2dc7.log` |
| 实现 blob 对照 | 7eef implementation、4ed candidate T/F、e69 integration 四路径 Git blob/SHA-256 对照 | implementation 7eef、candidate T/F 4ed、main e69 | 四文件全部一致，`EXIT=0`；4ed 不进入 main。 | `verification/FEA-15-PIN-BASIS-ENFORCE-1/ac5-integration-blob-map-e69fc2dc7.log` |
| AC5 独立 Review | fresh ZCode read-only Review | main `fea5c742afe4ecdb1e3e6a8116bc0c18f1cabeb1` / integration e69 | `APPROVED_WITH_LIMITATIONS`；P0/P1=0。P2-A 已修正；P3-B non-blocking；P3-C 经证据解决；P3-D limitation。 | [Review 报告](../reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac5-zcode-review-2026-11-12.md)、仓内 raw receipt |
| 最终 ZCode adjudication | fresh session `sess_1bff86d4-2618-42f8-841c-8a701eed4933`；decision turn `turn_1f3df43f-3f02-4b8a-be7a-b19c86539dfa` | reviewed clean HEAD `7661a63fafc638ea09ea340b346e999ab6923bb2` | AC5 `MET_WITH_LIMITATIONS`；历史 TaskPath FAIL 接纳为限制；Review-R-001 CLOSE；R-001 条件关闭于全行 blob audit `EXIT=0`。 | [最终裁决报告](../reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac5-final-adjudication-2026-11-12.md)、`verification/FEA-15-PIN-BASIS-ENFORCE-1/zcode-ac5-final-adjudication-20261112.jsonl` |
| Task card pinbackfill 门禁 | 四门命令同 Task 卡提交后运行 | clean main `fbfc7de07ef51e1cf0372cfafb526bf81aaf71c6` | default、TaskPath 各 3 warnings / `EXIT=0`；pins 18/18 / `EXIT=0`；API 1/79/6=86 / `EXIT=0`。 | `verification/FEA-15-PIN-BASIS-ENFORCE-1/main-post-final-adjudication-card-pinbackfill-gates-fbfc7de07.log` |
| Canonical Evidence blob audit | 对当时 Task 卡全部 53 行逐行执行 `git cat-file blob <commit>:<path>` 并核 SHA-256 | clean main `fbfc7de07ef51e1cf0372cfafb526bf81aaf71c6` | 53/53 PASS，0 failures，`EXIT=0`。Task closeout 前会在包含 Handoff 与最终 pin 的 Task 卡上再执行一次全行审计。 | `verification/FEA-15-PIN-BASIS-ENFORCE-1/canonical-evidence-blob-audit-fbfc7de07.log` |

## 必须保留的 limitation

**两条历史门禁失败。** `FEA-06-PREREQ-1` 为 13 errors / `EXIT=1`；`CHAPTER-SELECTOR-1` 为 6 errors / `EXIT=1`。ZCode 接纳它们作为 documented historical limitation。归因是高置信间接证据链，未做同环境 A/B 重放；不得声称绝对因果已经证明，不得修改两张历史卡或其 `verification/**` 字节，也不得将 FAIL 改成 PASS。

**P2-1：worktree SHA 与 Git blob SHA 的口径。** generation log 中 SHA 是生成时工作树字节；Canonical Evidence pin 是对应 commit 中 Git blob 字节。六对历史数据如下：

| Artifact | Generation log / worktree SHA-256 | Git blob SHA-256 / Canonical pin |
|---|---|---|
| `ac4-v2-inventory-audit.json` | `acd19f03d677eb410dfa88274fd0c348e2c13d74f65403fa43512cc3f8906486` | `ac321500f01b342516dbec4d7f48083cea5a44bc3479b05c0c2476ff5e472c92` |
| `ac4-inventory-r0.json` | `425692adcaddf8a9ab6d86ef3aff885d6056cddd84fa17f3dbc108c7913de8b3` | `578b9e30933c5d8807da8a2687c8adc903bbcce58c1653adca61a3d8437af0e9` |
| `ac4-v2-clone-t-inventory.json` | `fd1916eb1cb4b16f6fa7a0da316e21f684111f6cef5c9251dcc759e4f09c6bc0` | `6d29d0fd54141f74c22b9ff4b283d7f74d514b37b92191c8d4aed0d6a9e5b5aa` |
| `ac4-v2-clone-f-inventory.json` | `1e680f71fdd8cebb70607b5458f8ee8b1cffe9dc03e803b7846b63a40388450c` | `5206e4c5d3ab2a86b2bb1d35154d8ad3edc0f4f5d93602d49dd08212dec780f0` |
| T inventory delta | `bbc48c6f7249f503a591a2f40a08a73cc55968c24ec669895290219f1d7953ef` | `9daceedc583621725bff1691b7fd2ca815fce90fabab304c4cbdbf128a64e623` |
| F inventory delta | `f055bb1ad4a12c70343b4675837bf77c7c3d76f5798f2a6b064681477fa4caea` | `ae697e5c58c669bf7ae9c649f49fc6248e50d424925071f0e58e4972cf926eb3` |

**P2-2：clone 设置时序未证明。** T/F config last-write timestamps follow the checkout reflog timestamp; the original sampler/script and raw config/reflog source were not retained. The evidence does not prove configuration preceded checkout. This is a permanent evidence-quality limitation; no document should claim otherwise.

**其他限制。** Full governance suite 的历史结果为 `61 passed / 2 skipped / 3 failed / EXIT=1`，同名失败在基线也出现；保持 FAIL。Linux `NOT_RUN`。Review P3-B 的冗余 legacy SHA checker branch 不在本 Task 修改；P3-D（external clone 全树 clean 未独立证明）作为 limitation 保留。所有仓外 clone、worktree、过程日志及原始 receipt 均 `PRESERVE_REFERENCED`；未清理、未 prune、未运行 GC/repack。

## 接收方式与下一任务建议

实现已集成于 main；复核/恢复使用 Task 卡 `doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md`、本 Handoff、最终 ZCode adjudication 和该卡 Canonical Evidence。候选 `4ed7f32b3ce9104ecee11aad593bde222055a0df` 只用于历史 blob 对照，禁止集成。

- Task ID / 标题：无需下一步操作；当前 Plan 无 READY 节点，且 ZCode 未释放历史卡修复或其他新范围。
- 推荐 Agent / Reviewer：无需下一步操作；若以后释放历史治理登记修复，按新 Task 任命 Owner 与上下文独立 Reviewer。
- 推荐原因与前置依赖：本 Task 以 `closed_with_limitations` 收口；任何历史卡修复须另行释放 Task。
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `main`；Task base `d8b9b20869ac0957e152eddb9b5de88c8c2f9326`；实现 delivery head `e69fc2dc7a5f6ec68c9a881c1e25599cfe634da3`；final closeout HEAD 由 Task 卡记录。
- 允许修改路径：无需下一步操作；后续治理范围须在新 Task 中冻结。
- 禁止范围与新增授权条件：不得修改历史卡/证据、冻结契约/pins、批量迁移、清理资源或 push；均需另行授权。
- 交付物：无需下一步操作；本 Task 的代码、测试、Handoff、Review、adjudication 和 verification 已记录。
- 验证命令、环境与完成 Gate：未来新 Task 需重新定义；本 Task final closeout 仍按其卡运行四门并记录 EXIT。
- 可直接转发给 Agent 的指令：无需下一步操作；没有安全且已授权的后续 Task。

## 风险与遗留

本 Handoff 不授权修复历史 TaskPath FAIL、迁移 pin、修改契约或清理外部资源。R-001 将在 Handoff pin 回填后的最终 Task 卡上再次运行全行 blob audit；全部 PASS 且终态卡四门通过后，Task 方可按 ZCode 裁决关闭。
