---
task_id: P13
author: Codex
recipient: DSH
base_commit: 11d14c4d42472e1fd0af4af80d5526f2215325c7
delivery_head: 78b0d439a819f55c8e7a97ad2a09d9e066a08a80
status: in_review
---

# Handoff：P13 Core Run Runtime

## 交付结果

实现提交 `78b0d439a819f55c8e7a97ad2a09d9e066a08a80`，分支 `codex/P13-run-runtime-control-recovery`，worktree `G:/CODEX/New Manga.workspace/worktrees/P13-RUN-RUNTIME`。

- AC1–AC2：StartRun / RetryFailedTargets 使用持久幂等账本和规范 fingerprint；接受事务原子写入 Run、固定顺序目标、执行快照与 key。重复同键返回原 Run 当前状态；异 fingerprint 返回 `IDEMPOTENCY_KEY_REUSED`。重放不会重新解析目标或设置。
- AC3：Core scheduler 只从持久 PipelineStore 领取工作；数据库路径级 OS advisory lease 跨进程排他，lease owner 才恢复和推进；worker 连接按线程路由；非 owner 写入 scheduler 状态被拒绝。
- AC4：`Pending.pause` 拒绝；`Blocked.stop` 到 `Cancelled`；Restart 的父 Run disposition、child 来源及幂等记录在单 SQLite transaction 中写入；RetryFailedTargets 仅接受 `CompletedWithFailures`。非法状态矩阵保留无副作用断言。
- AC5：最多 3 次总请求（原请求 + 2 次重试），延迟 1s / 2s；优先遵守 `Retry-After`；Authentication、InvalidInput、MissingCredential、Lock/人工保护冲突不自动重试。
- AC6：获取 lease 后只将此前 `Running` 标成 `Interrupted`；Continue 沿用原快照并只重放未安全提交步骤；Restart 与 Abandon 分支独立。Page current 指针与成功 Step 状态一起提交。
- AC7：新增只读 TaskProjection tasks/steps 查询，状态、统计、原因、retry、当前 Page/Step 和 controls 来自同一 Run；未冻结的 provider/model/device 输出 null；错误文本安全裁剪。普通投影 250ms 节流，四类重要事件在状态提交后 best-effort 输出。
- AC8：改动限于 P13 allowlist 与直接相关 Core tests；未改 D04/D08 语义、冻结契约或 P14 UI；无新增依赖。
- AC9：固定实现 head、提交、测试日志与本 Handoff 均已创建。Task 保持 `in_review`，等待独立 Review / Coordinator integration Gate。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| P11 §2–§9 对照 | 逐节核对条款、基线缺口、方案、判别验证和实施证据 | 基线 `11d14c4d` → `78b0d439` | PASS | `verification/P13/p11-section-matrix-20261016.md` |
| AC1–AC7 定向测试 | 指定 Python 3.12 执行两份 P13 测试文件 | `78b0d439` | 79 passed，exit 0 | `verification/P13/p13-runtime-tests.log` |
| AC4(a–d) 红绿 | 基线执行四个同名判别用例，再执行相同用例 | 基线 `11d14c4d` → `78b0d439` | before 4 failed / exit 1；after 4 passed / exit 0 | `verification/P13/ac4-before.log`、`verification/P13/ac4-after-green-full.log` |
| AC4(c) 当前基线 / SQLite 原子性 | 当前基线跑 Restart 注入用例；新实现跑真实 SQLite child 写失败回滚 | `11d14c4d` → `78b0d439` | before 1 failed、51 passed / exit 1；after 1 passed / exit 0 | `verification/P13/ac4-current-base.log`、`verification/P13/ac4-c-sqlite-after.log` |
| Core 回归 | `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe -m pytest tests/core -q` | `78b0d439`，指定 Python 3.12 / PySide6 6.11.2 环境 | 340 passed、1 warning，exit 0 | `verification/P13/core-suite-final.log` |
| F3 protocol major | major 1 请求拒绝、major 2/minor 0 接受及 ping 版本断言 | `78b0d439` | PASS | `tests/core/test_core_service.py`、`tests/core/test_p13_run_runtime.py::test_retry_after_is_not_capped_and_runtime_version_is_major_two` |
| F5 SQLite migration | 临时 SQLite 验证 additive ledger 建表、schema version 不变及事务回滚 | `78b0d439` | PASS；真实用户库回退 NOT_RUN | `verification/P13/migration-boundary.md`、P13 runtime log |
| scope / whitespace | `git diff --check` 与固定基线 name-only 审阅 | `78b0d439` | PASS；逐项确认仅含 P13 allowlist 路径 | 最终 name-only 列表在本次交付回报原样输出 |

自动化测试使用 fake transport；真实 Provider 网络调用未运行。真实用户数据库回退未运行。SQLite ledger migration 边界和保留已有幂等数据时的回退要求见 `verification/P13/migration-boundary.md`。

## 接收方式

- 分支：`codex/P13-run-runtime-control-recovery`；worktree：`G:/CODEX/New Manga.workspace/worktrees/P13-RUN-RUNTIME`。
- 固定基线：`11d14c4d42472e1fd0af4af80d5526f2215325c7`；实现提交：`78b0d439a819f55c8e7a97ad2a09d9e066a08a80`。
- 指定测试环境命令：`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe -m pytest tests/core -q`。
- 不需要额外依赖或用户数据。测试数据库全部位于 pytest 临时目录。

## 下一任务建议（必填）

- Task ID / 标题：P13 Independent Review and Integration Gate（当前 Task 的关闭步骤，不新增实现 Task）。
- 推荐 Agent / Reviewer：DSH（任务 frontmatter 已指定 `reviewer=dsh`）。
- 推荐原因与前置依赖：P13 owner 实现和测试已固定；项目要求非作者 Review 与 Coordinator 集成后才关闭 Task。
- Recovery point：仓库 `G:/CODEX/New Manga`；branch/worktree `codex/P13-run-runtime-control-recovery` / `G:/CODEX/New Manga.workspace/worktrees/P13-RUN-RUNTIME`；base `11d14c4d42472e1fd0af4af80d5526f2215325c7`；head `78b0d439a819f55c8e7a97ad2a09d9e066a08a80`。
- 允许修改路径：Review 仅写 `verification/P13/**` Review 记录；任何实现修复需先由 Codex 明确授权并回到 P13 Owner。
- 禁止范围与新增授权条件：不得修改 P11 或 M2-C1 冻结契约、不得扩展 P13 allowlist、不得修改 P14 UI、不得 push/merge；发现契约缺陷时标记 `BLOCKED_WAITING_EXTERNAL_DECISION`。
- 交付物：独立 Review 结论及按项目流程由 Coordinator 完成集成决策。
- 验证命令、环境与完成 Gate：执行指定 py312 `pytest tests/core -q`，审阅 P11 matrix、AC4 红绿证据、SQLite 事务和最终 diff；Gate 为 Review 通过且 Coordinator 集成后更新 Task 状态。
- 可直接转发给 Agent 的指令：`请对固定 head 78b0d439a819f55c8e7a97ad2a09d9e066a08a80 做 P13 独立 Review。只读检查 AC1–AC8 与 P11 matrix、AC4 红绿判别证据、F3/F5 边界、线程/SQLite owner 与最终范围；用指定 py312 环境执行 tests/core。将结论写入 verification/P13/**，不得自行改实现或冻结契约。完成后交 Coordinator 决定集成与关闭。`

## 风险与遗留

- `pipeline_run_idempotency` 是 additive、无 schema version bump 的 SQLite 表；已有 key 账本不能在回退时删除。细节见 `verification/P13/migration-boundary.md`。
- 真正网络 Provider 行为与真实用户数据库回退为 `NOT_RUN`；fake transport 和临时 SQLite 故障注入已覆盖对应控制路径。
- 独立 Review / Coordinator integration 尚未运行，因此 P13 保持 `in_review`。
