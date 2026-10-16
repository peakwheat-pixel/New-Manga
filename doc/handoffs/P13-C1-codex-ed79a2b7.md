---
task_id: P13-C1
author: Codex
recipient: Codex / Coordinator
base_commit: c33033dc02c4373d3a3a35333a2c7aeac03c7ce6
delivery_head: ed79a2b778e13e8aa892014eb16a38be4e27fdf7
status: approved_pending_integration
---

# Handoff：P13-C1 Runtime IPC 契约修订

## 交付结果

契约修订固定在 `ed79a2b778e13e8aa892014eb16a38be4e27fdf7`，分支 `codex/P13-C1-runtime-ipc-contract`。交付提交：

- `d2a0e839033aba415865755a93756b39e158a3e8` — `docs(P13-C1): freeze runtime IPC wire v2`
- `ed79a2b778e13e8aa892014eb16a38be4e27fdf7` — `docs(P13-C1): close restart and projection wire gaps`

变更路径为 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`、`verification/P13-C1/p11-d08-coverage.md`、`verification/P13-C1/compatibility-impact.md`。后续 Task/Handoff/Review 归档为文档提交；不改变上述 `delivery_head`。

契约现冻结 StartRun/Retry/Restart 幂等键与 fingerprint、ControlRun 完整转换/拒绝矩阵、Run snapshot、TaskProjection 的错误/重试/可得执行详情，以及四类重要 Run 事件；§12 明确授权 P13 在既有 allowlist 内实现 Python IPC Runtime。协议目标 major 为 2.0；现有 Core 代码仍是 1.6，运行时未实现。

| AC | 结果 | 证据 |
|---|---|---|
| AC1 幂等键 | PASS | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §4、§5.5；[Review](../../verification/P13-C1/review-ed79a2b7.md) |
| AC2 控制转换 | PASS | 同文件 §5.5 全状态合法/拒绝表与错误类别；Review |
| AC3 查询与投影 | PASS | 同文件 §5、§5.5、§6.1；P11/D08 对照表 |
| AC4 状态事件 | PASS | 同文件 §3、§6.2；Review |
| AC5 授权与兼容 | PASS | 同文件 §3.2、§12；[兼容说明](../../verification/P13-C1/compatibility-impact.md) |
| AC6 逐条覆盖 | PASS | [P11 / D08 覆盖表](../../verification/P13-C1/p11-d08-coverage.md)：P11 逻辑面及 D08 五组 18 条 AC 均有 wire carrier 或明确责任边界 |
| AC7 范围 | PASS | 固定交付 head 的 diff 仅含上述允许的契约和 verification 文件；无 runtime、Schema、产品代码或依赖改动 |
| AC8 固定 head / Review / Handoff / commit | PARTIAL | head 已固定、非作者 Review 已批准、Handoff 与提交已归档；Coordinator 集成 `NOT_RUN`（当前任务明确禁止 merge/push），故 Task 状态为 `approved`，等待集成而非 `done` |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 契约与范围静态核对 | 独立 Reviewer 对照 P11 §2–§7、D08 五组 18 条 AC、P13 allowlist；`git diff --check c33033dc02c4373d3a3a35333a2c7aeac03c7ce6..ed79a2b778e13e8aa892014eb16a38be4e27fdf7` | 当前 Task worktree，固定 head `ed79a2b7…` | PASS；Review finding 0 | `verification/P13-C1/review-ed79a2b7.md` |
| Runtime / SQLite reopen / crash recovery / UI timing / end-to-end | 未运行（本 Task 只授权文档契约工作；运行验收属于后续 P13/P14） | 未运行 | NOT_RUN | 后续 P13/P14 验收 |

## 接收方式

- 分支：`codex/P13-C1-runtime-ipc-contract`
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/P13-C1-RUNTIME-IPC`
- 固定契约 head：`ed79a2b778e13e8aa892014eb16a38be4e27fdf7`
- 下一 Task 不应从旧 P13 基线直接实现。只读核对发现现有 P13 worktree `G:/CODEX/New Manga.workspace/worktrees/P13-RUN-RUNTIME` 的 branch 为 `codex/P13-run-runtime-control-recovery`、HEAD=`0e56c84f83872372cc116ad8dc82b374802cdae5`；而 `doc/tasks/P13.md` 声明 base=`f87d312c367a961a742816f9d87b609e9045845c`。该 worktree 当时无 `git status --porcelain` 输出。Coordinator 必须先处理 C1 正式集成及此 base/head 漂移，再决定如何恢复 P13；本 Task 未写入该 worktree。
- `doc/tasks/P13-C1.md` 初始 `base_commit` 为 `0e56c84f83872372cc116ad8dc82b374802cdae5`，但本 Task 获准坐标、worktree `HEAD` 与实际分支起点均为 `c33033dc02c4373d3a3a35333a2c7aeac03c7ce6`。已按获准坐标记载并保留漂移说明。
- Task 所列只读输入 `verification/P13/blockers.md` 与 `verification/P13/p11-implementation-matrix.md` 在本 worktree 不存在；因此没有为它们建立 `SOURCE_PIN`。本交付使用 Task 中记录的阻塞事实、P11/D08/P13 文档及只读实现文件。

## 下一任务建议（必填）

- **Task ID / 标题：** `P13` — 后台恢复（Run 接线 → 控制 → 恢复）。当前 Task 仍为 `blocked`；建议启动条件是 C1 契约先由 Coordinator 集成，并将 P13 的 `base_commit`、现有 worktree HEAD 与释放状态重新核对一致。
- **推荐 Agent / Reviewer：** 由 Codex / Coordinator 先完成集成和恢复门；依赖解除后推荐 ZCode 承担该独立长任务，DeepSeek Harness 做非作者 Review。Owner / Reviewer 不得相同；以重新释放的 Task 为准。
- **推荐原因与前置依赖：** P13 依赖冻结的 P11 生命周期契约及本次 P13-C1 wire/授权；目前 P13 Task 和现存 worktree 的 base 不一致，不能直接从现状继续运行时实现。
- **Recovery point：** 仓库 `G:/CODEX/New Manga`；当前 P13 worktree `G:/CODEX/New Manga.workspace/worktrees/P13-RUN-RUNTIME`；branch `codex/P13-run-runtime-control-recovery`；实测 HEAD `0e56c84f83872372cc116ad8dc82b374802cdae5`；P13 Task 声明 base `f87d312c367a961a742816f9d87b609e9045845c`；本 Task 固定契约 head `ed79a2b778e13e8aa892014eb16a38be4e27fdf7`。Coordinator 先协调差异，不覆盖当前 worktree。
- **允许修改路径：** 只按重新释放的 `doc/tasks/P13.md` allowlist；其当前记录包含 `src/application/tasks/**`、`src/bootstrap/core_service.py`、`src/bootstrap/core_assembly.py`、`src/infrastructure/sqlite/pipeline.py`（含确需 migration）、provider retry/runtime seams 与 `tests/core/**`。路径变化需由 Coordinator 在 Task 更新。
- **禁止范围与新增授权条件：** 不改 P11 或本次冻结契约；不改 React/Tauri/Rust/QML、额外产品行为或依赖；不得创建第二 scheduler/store；不得未经授权扩大 Schema/migration 路径。P13 依赖、base、Owner、Reviewer 和 allowlist 必须先被 Coordinator 重新确认。
- **交付物：** P13 Task 所需 runtime、判别测试、固定实现 head、独立 Review、verification、Handoff；对 D08 与 P11 的每项验收提供可重现结果。
- **验证命令、环境与完成 Gate：** 按重新释放的 P13 Task 执行对应 `tests/core/**`、SQLite 跨重启恢复、scheduler ownership、故障恢复与事件/投影检查；记录每条命令、环境、退出码与 skip 原因。独立 Review、测试、Codex 集成验证全部通过后才可标 `done`。
- **可直接转发给 Agent 的指令：** “先不要修改或继续现有 P13 worktree。请由 Codex/Coordinator 将 P13-C1 固定契约 head `ed79a2b778e13e8aa892014eb16a38be4e27fdf7` 正式集成，并核对 `doc/tasks/P13.md` 声明的 base `f87d312c367a961a742816f9d87b609e9045845c` 与现有 P13 worktree `G:/CODEX/New Manga.workspace/worktrees/P13-RUN-RUNTIME` 的 branch `codex/P13-run-runtime-control-recovery` / HEAD `0e56c84f83872372cc116ad8dc82b374802cdae5`；在 Task base、worktree head、Owner、Reviewer 和 allowlist 被更新并重新释放之前，不得启动 P13 实现。释放后按 `doc/tasks/P13.md` 与已集成 P13-C1 契约实现、测试并提交固定 head、verification 和 Handoff。”

## 风险与遗留

- 契约 major 2.0 是有意破坏性变更：旧 major 1 消费端必须升级；stdio 输出改为 Response/Event 混流。当前实现仍是 major 1/minor 6，不能把本契约称为已实现。
- 未运行 Runtime、数据库、crash、UI 或产品端到端验收；交付只批准契约设计。
- `verification/P13/` 中 Task 指定的两个 blocker 输入文件缺失于本 worktree；需 Coordinator 补齐其权威证据路径或在 Task 中重新说明事实来源。
- P13 现有 Task base 与 worktree HEAD 漂移，必须在恢复 P13 前协调。
- 未 merge、未 push；主仓及既有 P13 worktree 未写入。
