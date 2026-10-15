---
task_id: P11
author: Codex
recipient: DeepSeek Harness Review / Codex Coordinator
base_commit: 68fbdde891b05920d689f3521a3d26b7b6a98f5d
delivery_head: b7fb677338af56eaebbfa9c5b642646dd8b5ae90
status: in_review
---

# Handoff：P11

## 交付结果

契约交付 head `b7fb677338af56eaebbfa9c5b642646dd8b5ae90`，branch=`codex/P11-long-task-lifecycle-contract`，worktree=`G:/CODEX/New Manga.workspace/worktrees/P11-LONG-TASK-LIFECYCLE-CONTRACT`，base=`68fbdde891b05920d689f3521a3d26b7b6a98f5d`。Task 证据记录固定于 `d57f8d3d661b5ea80d3cf34fb5b8636fca391195`（以 `git rev-parse HEAD` 实测）；该 commit 含正确的 Canonical Evidence hash。文件名中的短 hash 指契约交付 head。

提交列表：

- `01c20fbc28323664553ab0a2fcc981690ead9881` — `docs(P11): define long task lifecycle contract`
- `470e2264ae689157dd45a0c8d9ec329907d71fc7` — `docs(P11): make child-run retries idempotent`
- `b7fb677338af56eaebbfa9c5b642646dd8b5ae90` — `docs(P11): record lifecycle implementation gaps`
- `e3a8fab32a4b89ad9103fd3c9eb11af3a49d075d` — `docs(P11): record static evidence and review state`（含 `doc/tasks/P11.md` 的 AC 状态与 Canonical Evidence）。
- `d57f8d3d661b5ea80d3cf34fb5b8636fca391195` — `docs(P11): correct canonical evidence hash`（按 Git blob 重新计算并修正证据元数据）。
- 本 Handoff 单独追加；按仓库约定引用先前的契约交付 head。

变更路径仅有本 Task 允许的三项：

- `doc/contracts/P11_LONG_TASK_LIFECYCLE_CONTRACT.md`
- `doc/tasks/P11.md`
- `doc/handoffs/P11-codex-b7fb6773.md`

| AC | 状态 | 证据 |
|---|---|---|
| AC1 | 完成（静态） | `doc/contracts/P11_LONG_TASK_LIFECYCLE_CONTRACT.md` §1：D04 / D07 / D08 逐项来源映射。 |
| AC2 | 完成（静态） | 同文件 §2–§6：幂等 durable acceptance、合法与非法状态转换、失败重试、崩溃恢复和重放边界。 |
| AC3 | 完成（静态） | 同文件 §8–§9：实际符号对照、现存复用 / 拟议新增、P13 / P14 消费边界。 |
| AC4 | 完成（静态计划与来源检查） | 同文件 §10；`doc/tasks/P11.md` 测试表。Runtime、真实 Pipeline 和 UI 均 `NOT_RUN`。 |
| AC5 | `NOT_RUN` | 独立 DSH Review 和 Coordinator 集成未执行；本 Task 保持 `in_review`，不标 `done`。 |

契约 blob 由 `git hash-object --path=...` 定位（blob=`f075d3a06c126fe72f644992a6774f520e38d366`），再通过 `git cat-file blob <blob>` 原始内容流式计算 SHA-256：`63a65cc13934fd962514b217f5fedee897075a034769cc2d5d4ca7e9aeb65914`。Canonical Evidence 已写入 `doc/tasks/P11.md`。

## 验证证据

| AC / 场景 | 实际命令 / 步骤 | 环境与被测 commit | 结果 | 日志 / 产物 |
|---|---|---|---|---|
| 来源锚点 | `rg -n '^## (11\.|12\.|13\.|14\.|22\.|30\.|31\.|51\.)|^# (6\.|56\.|64\.|65\.|66\.)|^# (26\.|27\.|28\.|29\.|30\.|31\.|32\.)|^## AC-(CMD|PIPE|PAUSE|STOP|CRASH|RETRY|PROGRESS)|^## 6\.' doc/04_USER_FLOW.md doc/07_NON_FUNCTIONAL_REQUIREMENTS.md doc/08_ACCEPTANCE_CRITERIA.md doc/contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md` | worktree，只读来源 | PASS：所需章节锚点均命中 | 契约 §1；Task 交付记录 |
| 指定实现符号与方法 | `rg -n 'class PipelineService|def create_run|def control_run|def recover_running_runs|def retry_failed_targets|def _persist|class PipelineStore|class InMemoryPipelineStore|class TaskProjection|def build_projection|class ProductionStepExecutor|SqlitePipelineStore|def execute\(' src/application/tasks/service.py src/application/tasks/store.py src/application/tasks/projection.py src/application/translation/pipeline/executor.py src/infrastructure/pipeline/executor.py src/infrastructure/pipeline/assembly.py`，随后逐项阅读指定文件 | worktree，base `68fbdde…` | PASS：现状与契约差异列入 §8 | 契约 §8 |
| 合法/非法转换与来源一致性 | 手工逐项对照 D04 §30.1/§30.3、D08 AC-PAUSE/STOP/CRASH/RETRY、TASK-002 合同 §6 | 固定契约 head `b7fb6773…` | PASS：静态矩阵；不代表 runtime 行为 | 契约 §4 |
| 格式与 blob SHA-256 | `git show --check --oneline HEAD`；`git hash-object --path=doc/contracts/P11_LONG_TASK_LIFECYCLE_CONTRACT.md doc/contracts/P11_LONG_TASK_LIFECYCLE_CONTRACT.md` + `git cat-file blob <blob>` + SHA-256 stream | linked worktree / shared Git metadata | PASS：无 whitespace error；SHA-256 与 Canonical Evidence 相同 | `doc/tasks/P11.md` Canonical Evidence |
| DB 重开、接受幂等、控制竞态、崩溃恢复 | 未执行（明确留给 P13） | — | `NOT_RUN` | 契约 §10 |
| 真实 OCR / Translation / Inpaint Pipeline | 未执行；deterministic executor 不作为真实能力证明 | — | `NOT_RUN` | 契约 §10 |
| React UI、暂停 ≤200 ms、进度投影刷新与 PageList 同源 | 未执行（明确留给 P14） | — | `NOT_RUN` | 契约 §10 |

未运行产品测试、runtime、真实 Pipeline、UI 或端到端命令；没有将其记为 PASS。

## 接收方式

- 仓库：`G:/CODEX/New Manga` 的 linked worktree；worktree=`G:/CODEX/New Manga.workspace/worktrees/P11-LONG-TASK-LIFECYCLE-CONTRACT`。
- branch=`codex/P11-long-task-lifecycle-contract`；base=`68fbdde891b05920d689f3521a3d26b7b6a98f5d`；契约交付 head=`b7fb677338af56eaebbfa9c5b642646dd8b5ae90`。
- 后续审查须对 P11 当前固定分支 head 只读检查，并对照 P11 AC、D04 / D07 / D08、P08 P11 范围与契约 §8 现状差异。请检查 Blocked Stop、Pending Pause、重试状态门、Restart 原子性、SQLite durable acceptance / Step 提交原子性及 P13/P14 分界。
- Review 阶段不写仓库文件；Review 结果交回 Codex，由 Codex 在本 Task 允许的 Handoff 路径记录。不得修改 `src/**`、`apps/**`、`packaging/**`、`tests/**`、Schema、D04/D07/D08，亦不得 push / merge / rebase / reset / stash 或清理 worktree。

## 下一任务建议（必填）

- Task ID / 标题：P11 AC5 非作者 Review 与集成 Gate（当前 P11 的剩余验收，不创建新 Task）。
- 推荐 Agent / Reviewer：DeepSeek Harness（非作者 Reviewer）；Codex 为 Owner / 后续 Coordinator。
- 推荐原因与前置依赖：AC1–AC4 静态交付完成；AC5 要求固定 head 非作者 Review 与 Coordinator 集成。先 Review，再由 Coordinator 按独立授权决定集成；本次任务禁止 merge。
- Recovery point：worktree `G:/CODEX/New Manga.workspace/worktrees/P11-LONG-TASK-LIFECYCLE-CONTRACT`；branch `codex/P11-long-task-lifecycle-contract`；base `68fbdde891b05920d689f3521a3d26b7b6a98f5d`；固定 Review head `d57f8d3d661b5ea80d3cf34fb5b8636fca391195`；contract delivery head `b7fb677338af56eaebbfa9c5b642646dd8b5ae90`。后续只追加 Handoff，不改契约内容。
- 允许修改路径：Reviewer 只读，不写文件；Codex 仅可在已有 `doc/handoffs/P11-*.md` 中记录 Review 结果。Coordinator 集成须另按授权执行。
- 禁止范围与新增授权条件：不得改实现、Schema 或 D04/D07/D08；不得改变本契约语义；不得 push / merge / rebase / reset / stash / 删除文件或 worktree。任何产品终态取舍须等待用户裁决。
- 交付物：固定 head 的独立 Review findings / 结论；随后在同一 Handoff 记录 Review 路径或 `NOT_RUN`，并由 Coordinator 记录集成决定与 commit。
- 验证命令、环境与完成 Gate：只读检查 `git rev-parse HEAD`、`git status --short --branch`、`git diff --stat 68fbdde891b05920d689f3521a3d26b7b6a98f5d...<reviewed_head>`；逐项核实 AC1–AC5 与契约引用。Review 未批准、P0/P1 finding 未关或未集成时不得将 P11 置为 `done`；未执行命令写 `NOT_RUN`。
- 可直接转发给 Agent 的指令：

  > 请以 DeepSeek Harness 非作者 Reviewer 身份，对 P11 固定 Review head `d57f8d3d661b5ea80d3cf34fb5b8636fca391195` 做只读 Review。仓库 worktree：`G:/CODEX/New Manga.workspace/worktrees/P11-LONG-TASK-LIFECYCLE-CONTRACT`；branch：`codex/P11-long-task-lifecycle-contract`；base：`68fbdde891b05920d689f3521a3d26b7b6a98f5d`；契约交付 head：`b7fb677338af56eaebbfa9c5b642646dd8b5ae90`。检查 `doc/contracts/P11_LONG_TASK_LIFECYCLE_CONTRACT.md`、`doc/tasks/P11.md` 与 P11 来源文档，重点验证来源映射、状态矩阵与拒绝清单、idempotency / durable acceptance、重试退避、恢复重放边界、单 scheduler / store 所有权、§8 实现事实与 P13/P14 消费边界。只读并返回 findings 与 AC 状态，不改文件、不运行 runtime / Pipeline / UI、不 push / merge / 清理 worktree；未验证项明确 `NOT_RUN`。Review 后由 Codex 决定 Coordinator 集成。

## 风险与遗留

- AC5 尚未通过：DSH Review、Coordinator 集成均为 `NOT_RUN`，Task 当前 `in_review`。P13 尚须实现并验证 durable key/事务、single-owner 恢复与 Step/Artifact 一致性；契约 §8 已列现有 Blocked Stop、Pending Pause、Restart 非原子、Retry 状态校验和详情投影差异。
- 本 Task 未检查 `infrastructure.sqlite.pipeline` 内部事务实现；它在指定只读参考范围之外，已明确交 P13 验证。
- Commit 输出显示 Git 自动 repack 因共享 Git 元数据中的既有坏 ref `refs/codex/turn-diffs/checkpoints/2a21a8a61d84cda7b0ed63268dcdbb89/7567e5540e8991fc4af26294b9559d40/1791463160005/ba2cc422-720c-4912-902c-8e760a71313c` 失败；本次 commit 均成功。未执行修复或清理。
- 主仓 `G:/CODEX/New Manga` 零改动声明：本 Task 的文件操作仅落在上述 worktree 的三条授权路径；未对主仓执行写入。主仓开始时已有 dirty 条目，结束时须以最终 `git status --porcelain --untracked-files=no` 核对与开工快照一致。
- 没有未决产品终态语义裁决；若 Review 提出此类需求，按 P11 禁止范围转 `BLOCKED_WAITING_EXTERNAL_DECISION`。
