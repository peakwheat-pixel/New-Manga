---
task_id: P02PRE-R1H-H2-COLLECTOR
reviewer: Codex /root
author: Antigravity
base_commit: 90b9972fd621c37c6926b8a52416e2947965ff6c
reviewed_head: b4936c35067680fb7309c37405a4afed2b6c0c44
reviewed_docs_head: 6a59d82c6de3a525e3c1ebd49b5879cc1318e6cc
decision: changes_requested
---

# P02PRE-R1H-H2-COLLECTOR — R5 Review adjudication

## 裁决

**`CHANGES_REQUESTED`；R5 code head `b4936c35067680fb7309c37405a4afed2b6c0c44` 暂不集成。** DSH 对 R4 要求的 R5 修复给出 `APPROVED_STATIC_CONTENT`；Codex 确认 R4 P2-1、P3-1..5 的已裁决范围及 R2-01..04、P4、R3-CX-02/03 closures 通过。Codex 将 DSH 另报的三个 P3 提升为 R6 集成前必修项，原因是 collector 的新时点 meta 仍误述修复轮次、Owner Task 内部 Handoff SHA 失配、以及固定路径链 FAIL 的 exit/disposition 与 Task 已冻结约定不一致。

DSH 报告：[dsh-source-review-r5.md](dsh-source-review-r5.md)，session `session-1c32ed5d-b920-45b6-9198-335bc8a3636e`，CLI exit 0，stderr 0 bytes。DSH 在其环境无法启动 PowerShell/Git，按要求未绕过；Codex 独立对 manifest 的 14 项输入做 pre/post SHA-256 与 byte count 核验，14/14 匹配，并确认两份代码在 reviewed commit、worktree blob 一致、Owner worktree clean。核验记录：[source-review-r5-input-verification.json](source-review-r5-input-verification.json)。报告绑定 code `b4936c35067680fb7309c37405a4afed2b6c0c44`、docs/worktree HEAD `6a59d82c6de3a525e3c1ebd49b5879cc1318e6cc`；root HEAD/index 仍为 `343895fb5f0329c0c07a7104ec321b698f967607` / `C5CA88842173A8FE4B9C6B6B675528347EECBDC73F85600ABA06F11E3A692B68`。

## Finding 裁决与 R6 要求

1. **R5-CX-01（原 DSH P3-1，提升为 P2）：meta 修复说明陈旧。** `tools/p02/h1-raw-pre-run.ps1:1209` 仍把本轮称为 R4 且引用 R3 adjudication。R6 更新 `revisionNote`，准确描述 R5 对应的 R4 裁决修复；selftest 增加静态断言，防止继续输出旧轮次说明。新输出不能把 R5 描述为 R4。
2. **R5-CX-02（原 DSH P3-2，提升为 P2）：Owner Task 的 Handoff pin 过期。** Owner Task R5 canonical row `h2-r5-handoff` 记录 `bc907f62…`，但 manifest 与实际 Handoff pin 为 `bee4e019a3e0c4437c0c38ed5df5772d7d376d2b7a8b357fb7a2875d87e4622b`、10,193 bytes。R6 在最终 Handoff 固定后修正 Owner Task row，并在最终文档提交中复算。root Task 的独立 R5 Handoff pin 已为实际值，不改写旧 manifest 或本报告。
3. **R5-CX-03（原 DSH P3-3，提升为 P2）：固定路径链 FAIL 的状态映射不符 Task。** `tools/p02/h1-raw-pre-run.ps1:1331` 的 `Require` 在此前已记录 `CHECK_FAIL:path-chain-fixed-paths` 后抛错，catch 默认产出 `BLOCKED_EXCEPTION_FAIL_CLOSED` / exit 5；Owner Task `:119` 规定任一 FAIL check 应是 `BLOCKED_BY_FAILED_CHECKS` / exit 4。R6 应保留 observation 后立即硬停，在 fail-closed catch 中准确映射此特定 path-chain check 为既定失败 disposition/exit，并增加不执行 live collector 的判别力自测。不得吞掉原失败原因、延后 snapshot/launcher，或把 blocked 记录为 PASS。
4. **原 DSH P3-4（null/null 分类输入）：接受为非阻塞限制。** 生产调用在 `Get-PathProbeObservation` 中始终传入属性值或捕获的异常；若共享函数意外收到两者皆 null，当前会异常并由 collector 外层 fail-closed 捕获，不会伪装为 absence/PASS。此非生产输入不阻止 R6/Task 完成。
5. **原 DSH P3-5（链 helper 的 LinkTarget 异常未记录）：接受为非阻塞限制。** reparse leaf 在读取 LinkTarget 前已加入 `reparseComponents`；即便读取异常，ordinary-chain gate 仍失败并在使用任何 launcher/snapshot 前停止。它缺少可选 LinkTarget 错误细节，但不会解引用链接或放行。保持这一限制可见，后续不得把空 LinkTarget 解释为目标不存在。

R6 仅修复上述前三项及对应 Owner Task/Handoff/selftest 文档，遵循既有 allowlist。完成后固定新 code/docs head，PS 7.6.6 Parser 与纯 selftest 通过，再由 DSH 对新 exact head 做非作者复审；R5 verdict 不转移。无 live collector/getter/executor、registry/WER/ACL/profile/AppContainer 查询、Build/Cargo、AC1–AC7 或 Sandbox。

## 状态与运行边界

当前 Task 回到 `in_progress`，由 Antigravity 在现有 worktree/branch 执行 R6。R5 DSH 报告与 14/14 post-pins 保留为历史交付审查，不能作为新 head 的最终批准。H2-RUN 仍为独立 `proposed` Task，没有运行授权。Technical Gate `NOT_SATISFIED`、`private_registry_absence=UNPROVABLE`、Build Gate `BLOCKED`、Hard Build Barrier `EFFECTIVE`、Build/Cargo 与 AC1–AC7 `NOT_RUN`，H1 v2 P2-1 `OPEN` 均不变。
