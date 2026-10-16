---
task_id: HOST-ISSUER-1-C1
author: Codex
recipient: DeepSeek Harness (non-author Review), Coordinator DSH
base_commit: 6a5051dcafa549f200730a4f9824d83d187f07a2
delivery_head: af6fa705de54489ce32811cdc8dd3be51a1fd999
status: ready_for_review
---

# Handoff：HOST-ISSUER-1-C1

## 交付结果

固定交付 head：`af6fa705de54489ce32811cdc8dd3be51a1fd999`，分支 `codex/HOST-ISSUER-1-C1-grant-registration-contract`，worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1-C1`。

该 head 冻结 M2-C1 rev 2.3 / protocol `2.3` 的 §5.7 HostControl：通过 Tauri host 直接持有的 `StdioLibraryChannel` 子进程 stdio，以独立 envelope 注册/撤销 live Core 内存 grant；明确 host session credential、Core process session 绑定、关闭/重启/轮换失效、稳定拒绝码和零副作用。两种 ref 字段、签名对象及 `REF_*` 语义未改。§12 只授权 `src/bootstrap/core_service.py` 与 `tests/core/**` 的后续最小 Core 实现；没有 runtime 代码变更。

该 head 修改/新增：

- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`
- `doc/tasks/HOST-ISSUER-1-C1.md`
- `verification/HOST-ISSUER-1-C1/coverage-matrix.md`
- `verification/HOST-ISSUER-1-C1/compatibility-impact.md`

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1–AC5 契约 wire / session / ref / errors / allowlist | 静态比对 contract §§3、5.6、5.7、10.3、10.4、11、12 与 P09-FU2/P16 seam | 只读；`af6fa705de54489ce32811cdc8dd3be51a1fd999` | PASS（文档定义与既有面静态对照）；runtime `NOT_RUN` | `verification/HOST-ISSUER-1-C1/compatibility-impact.md` |
| AC6 对照完整性 | 逐条映射 HOST-ISSUER-1 AC1–AC7、§10.3、§10.4、§5.6 | 只读；`af6fa705de54489ce32811cdc8dd3be51a1fd999` | PASS（静态覆盖）；host implementation `NOT_RUN` | `verification/HOST-ISSUER-1-C1/coverage-matrix.md` |
| 修改范围 | `git diff --cached --check`；核对 `base..head` 修改路径 | PowerShell / Git；`6a5051d..af6fa705` | PASS；仅契约、Task 与本 Task 验证文件 | 本 Task Canonical Evidence 与最终 Git 记录 |
| Core/Tauri/WebView runtime、构建、测试 | 未运行；本 Task 只授权并修订契约，没有实现代码 | 不适用 | `NOT_RUN` | 本 Task AC 状态表 |
| 非作者 Review / Coordinator integration | 未执行 | 不适用 | `NOT_RUN`；AC8 未完成 | 待 Reviewer / Coordinator 记录 |

未运行测试或构建；本次验证是契约与既有 source/seam 的静态对照，不构成 runtime 安全通过证明。

## 接收方式

- 分支：`codex/HOST-ISSUER-1-C1-grant-registration-contract`
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1-C1`
- 复核范围：固定 `base_commit=6a5051dcafa549f200730a4f9824d83d187f07a2` → `delivery_head=af6fa705de54489ce32811cdc8dd3be51a1fd999`；reviewer 可从共同 Git history 读取该 head。
- 当前 Task 只允许修改本 Task 的契约、Task、Handoff 与 `verification/HOST-ISSUER-1-C1/**`。Review 只读；若发现需改契约，先记录 finding 并交 Owner 处理。
- 未新增依赖、Schema/migration、Tauri command、capability 或 runtime。

## 下一任务建议（必填）

- Task ID / 标题：`HOST-ISSUER-1-C1` 非作者 Review 与 Coordinator 集成 Gate
- 推荐 Agent / Reviewer：DeepSeek Harness（独立 Review）；Coordinator DSH 负责集成裁决。
- 推荐原因与前置依赖：当前 Owner 为 Codex；AC8 要求固定 head 的非作者 Review 和 Coordinator integration。Review 通过并集成后，再从新集成基线恢复已阻塞的 HOST-ISSUER-1。
- Recovery point：唯一仓库 `G:/CODEX/New Manga`；branch/worktree 如上；base `6a5051dcafa549f200730a4f9824d83d187f07a2`；fixed head `af6fa705de54489ce32811cdc8dd3be51a1fd999`。
- 允许修改路径：Review 只读；Review 产物写入 `verification/HOST-ISSUER-1-C1/**`。集成由 Coordinator 在经授权的主线工作流执行。
- 禁止范围与新增授权条件：不得自审、不得暴露 WebView callable registration、不改 ref 字段/既有 `REF_*`，不实现 host/Core runtime；任何修复需由 Owner 在当前 Task 的允许范围单独处理。不得 push。
- 交付物：固定 head 的独立 Review 报告；Review 通过后由 Coordinator 记录集成 commit 和 Task Gate。
- 验证命令、环境与完成 Gate：静态审查 `git diff 6a5051dcafa549f200730a4f9824d83d187f07a2..af6fa705de54489ce32811cdc8dd3be51a1fd999`，逐条覆盖 AC1–AC8、§10.3/§10.4、§5.6、§12；完成 Gate 为 Review approved、Coordinator integration verified，未跑项继续 `NOT_RUN`。
- 可直接转发给 Agent 的指令：

  > 请作为非作者 Reviewer，只读审查 `codex/HOST-ISSUER-1-C1-grant-registration-contract` 的固定 head `af6fa705de54489ce32811cdc8dd3be51a1fd999`（base `6a5051dcafa549f200730a4f9824d83d187f07a2`）。逐条核对 HOST-ISSUER-1-C1 AC1–AC8、HOST-ISSUER-1 AC1–AC7、M2-C1 §5.6/§10.3/§10.4/§12；重点检查 HostControl 是否只能经 host-owned `StdioLibraryChannel` live-Core 通道、WebView/普通 JSON-RPC 拒绝机制、Core/host session 失效、注册拒绝零副作用、ref 字段与 `REF_*` 不变、allowlist 是否最小。不要改契约或代码；将 findings、未覆盖风险、reviewed base/head 与结论写入 `verification/HOST-ISSUER-1-C1/**`。之后由 Coordinator 决定集成，并在通过后恢复 HOST-ISSUER-1。

## 风险与遗留

- HostControl 与 host issuer runtime、Core handler、WebView 负向测试均尚未实现；HOST-ISSUER-1 尚未解阻。
- host session 轮换要求结束当前 session 并重启 Core；本契约不定义 grant 数量上限或多来源 UI 选择策略。
- blocker assessment 在 HOST-ISSUER-1 来源 worktree；source pin 与 SHA 见本 Task Canonical Evidence。来源 worktree、主仓均只读。
- 主仓未修改；未 push、未 merge。Task 保持 `in_progress`，AC8 Review/集成仍为 `NOT_RUN`。
