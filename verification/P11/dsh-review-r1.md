---
task_id: P11
title: 长任务生命周期契约
reviewer: dsh（非作者；Owner=codex，reviewer 由 role_exclusion 机器排除 owner，未参与 implementation/repair）
owner: codex
base_commit: 68fbdde891b05920d689f3521a3d26b7b6a98f5d
declared_delivery_head: b7fb677338af56eaebbfa9c5b642646dd8b5ae90
declared_review_head: d57f8d3d661b5ea80d3cf34fb5b8636fca391195
reviewed_head: c7922ae1c62f4cac8721a2730fc19c7c973c7e83
review_worktree: G:/CODEX/New Manga.workspace/worktrees/P11-LONG-TASK-LIFECYCLE-CONTRACT
base_worktree: G:/CODEX/New Manga（用户 dirty 未被触碰）
date: 2026-10-15
mode: 只读审查 + 独立 Git/blob/SHA-256 复核 + 来源锚点与实现符号实证；未修改被审分支或主仓任何文件
object_binding: VERIFIED
architecture_axis: PASS
verification_axis: PASS（静态；runtime / UI 明确 NOT_RUN 并移交 P13/P14）
decision: approved_with_conditions
decision_scope: 契约静态交付面（AC1–AC4）通过；AC5 的独立 Review 由本文件闭合，Coordinator 集成待执行
---

# P11 长任务生命周期契约 — 独立 Review（R1）

## 0. 审查对象与方法

- 对象：`codex/P11-long-task-lifecycle-contract`，`68fbdde8..c7922ae1`（Owner=codex）。
- Reviewer 实际执行 Git、blob、SHA-256、来源锚点与实现符号复核；**未采信 Owner 自述**。

### 0.1 本轮实际执行的复核

| 项 | 方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only 68fbdde8..HEAD` | **仅 3 条授权路径**：契约、`doc/tasks/P11.md`、Handoff；无越界 |
| worktree 洁净 | `git status --porcelain` | **空（clean）** |
| 主仓零改动 | `git status --porcelain --untracked-files=no` | **19 项，与开工前完全一致**（全部为用户既有 dirty）；无新增/删除 |
| 契约 blob sha256 | 独立 `git cat-file blob HEAD:doc/contracts/...` → SHA-256 | `63a65cc13934fd962514b217f5fedee897075a034769cc2d5d4ca7e9aeb65914`，**与 Task 证据表一致** |
| D04 锚点 | 主仓与 worktree 双侧 grep | §11.1–§11.4 / §12 / §13 / §14 / §22 / §30.1–§30.3 / §31 / §51 **全部命中** |
| D07 锚点 | 同上（标题为 `# N.` 一级） | §6 / §56 / §64 / §65 / §66 **全部命中** |
| D08 锚点 | 同上 | §26–§32 **全部命中**；AC-CMD/PIPE/PAUSE/STOP/CRASH/RETRY/PROGRESS 共 13 个 AC ID **全部存在** |
| TASK-002 锚点 | grep | §6.1 / §6.2 **存在** |
| 实现符号 | grep 真实源码 | `PipelineService`、`create_run`、`control_run`、`recover_running_runs`、`retry_failed_targets`、`PipelineStore`、`InMemoryPipelineStore`、`TaskProjection`、`build_projection` **全部存在** |
| §8 代码断言实证 | 阅读 `service.py:845–906` 等 | 见 §2，**断言逐条为真** |

## 1. AC 逐项结论

| AC | Owner 结论 | Reviewer 判定 | 说明 |
|---|---|---|---|
| AC1 | 完成（静态） | **接受** | §1 需求映射表 26 行，逐条给出 D04/D07/D08/TASK-002 的真实章节锚点；Reviewer 双侧复核全部命中，非"文件存在"式映射 |
| AC2 | 完成（静态） | **接受** | §2 accept 幂等与 durable 判定点；§4.1 状态枚举；§4.2 合法转换 18 行；§4.5 非法转换拒绝清单覆盖 9 个状态；§5 重试；§6 崩溃恢复与重放边界 |
| AC3 | 完成（静态） | **接受** | §8 逐项对照真实符号并区分"现存可复用 / 拟议新增"；所指缺口经 Reviewer 实读源码证实（见 §2）；未修改任何实现文件 |
| AC4 | 完成（静态） | **接受** | §10 明确 PASS 仅限静态来源/一致性/只读实现核对；5 类 runtime/UI 验证明确 `NOT_RUN` 并指名 P13/P14 |
| AC5 | NOT_RUN | **Review 部分由本文件闭合；集成待 Coordinator** | Task 保持 `in_review`，未越权标 done |

## 2. §8 现状对照的独立实证（Reviewer 实读源码）

| 契约断言 | 实证 | 判定 |
|---|---|---|
| `control_run` 允许 `Pending` 直接 pause | `service.py:848` 允许 `PENDING/RUNNING`；`:851–852` 将 `PENDING` 直接置 `PAUSED` | **成立**。与本契约 §4.2/§4.5（`Pending` 必须拒绝 pause）**冲突** → P13 破坏性修正项 |
| `Blocked` 上 Stop 无法完成 `Blocked→Cancelled` | `service.py:856–864`：仅 `PENDING/PAUSED` 置 `CANCELLED`；`BLOCKED` 只写 `cancel_requested` 并保持状态；`execute_run` 对 Blocked 提前返回 | **成立** → 与 §4.2 表冲突，P13 修正项 |
| Restart 未作原子组合 | `service.py:882–889`：`create_run` 与来源 disposition 分两次 `_persist` | **成立** → P13 需原子化 |
| 失败目标重试未校验 Run 状态 | `service.py:919` `retry_failed_targets` 只按失败 Page 判定 | **成立** → P13 需补状态门 |

结论：§8 不是描述性套话，而是**可核验、可传递给 P13 的缺口清单**。

## 3. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| **F1** | **P2（Gate 前置）** | **交付 head 未冻结为单一值**：Task frontmatter `delivery_head=b7fb6773`、Owner 在回答/Handoff 中建议 review head=`d57f8d3d`，而分支实际 `HEAD=c7922ae1`（`d57f8d3d` 之后仍有 `c7922ae1 docs(P11): align handoff with canonical evidence`）。"固定 head 非作者 Review"要求被审对象唯一 | Reviewer 已将本 Review 绑定**实际 HEAD `c7922ae1`**（契约 blob 自 `b7fb6773` 起未变，sha256 一致，故风险低）。集成时 Coordinator 必须把 `delivery_head` 修正为实际交付 head，并在 closeout 记录本不一致 |
| F2 | P3 | §8 揭示的 4 个实现缺口（Pending+pause、Blocked+stop、restart 非原子、retry 缺状态门）与本契约 §4.2/§4.5 目标语义**直接冲突**；契约已标注为"拟议新增/P13 修正"，但未声明其为**破坏性变更** | P13 释放时必须把这 4 项列为破坏性变更清单与回归项，避免按旧行为实现 |
| F3 | P3 | Task 台账"Owner 开工时用户固定坐标"措辞含糊（实际是 Coordinator 释放坐标 `68fbdde8`，用户未参与该坐标决定） | 措辞修正，不影响事实正确性 |
| F4 | P4 | 契约 §1 混用"D07 §6"式引用与 D07 实际 `# 6.` 层级；不影响可检索性 | 不阻塞；后续契约统一引用格式即可 |

## 4. 条件

- **C1**：Coordinator 集成时冻结实际被审 head `c7922ae1c62f4cac8721a2730fc19c7c973c7e83`，并把 Task `delivery_head` 由 `b7fb6773` 修正为该实际值。
- **C2**：P13 释放时引用本 Task 与契约 §8，把 F2 的 4 项列为破坏性变更与回归 Gate。
- **C3**：closeout 登记证据 pin（本 Review、契约 blob/commit）与 Resource Manifest（worktree 保留）。
- 上述条件不要求修改被审分支；契约内容本身无需返修（F1 是元数据冻结问题，F2–F4 已由契约自身记录或属措辞）。

## 5. 能力边界

- 本 Review 仅覆盖契约交付面的静态正确性与范围合规；**不代表** P13 runtime、真实 Pipeline、UI 或 E2E 的任何结论。
- 所有 Git / blob / SHA-256 / 锚点 / 符号结论均由 Reviewer 在 live 环境实际执行。
- Reviewer 未修改被审分支、主仓或任何证据文件；未 push。
