---
task_id: M2-REGION-RETYPE-CONTRACT
author: ZCode（subagent，契约冻结 Owner）
recipient: Codex（integrator，编排会话代行，用户全权授权）；Review：DeepSeek Harness（非作者）
base_commit: 4c12e8af
delivery_head: a108996b
status: delivered_pending_review
---

# Handoff：M2-REGION-RETYPE-CONTRACT（T5a · 契约冻结）

## 交付结果

M2-C1 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev `1.3` → `1.4` **草案**（delivery_head=`a108996b`，1 file，+59/−3），**零代码零 runtime**。提交链：claim `8d41d8ef` → 契约修订 `a108996b` → 本文档 commit（Handoff/Task 回填/verification）。

与 AC 逐项对照（自检证据全文：[verification/M2-REGION-RETYPE-CONTRACT/contract-freeze-report.md](../../verification/M2-REGION-RETYPE-CONTRACT/contract-freeze-report.md)）：

| AC | 交付 | 结论 |
|---|---|---|
| AC1 | §5 表 `SetRegionType` 行 + §5.4 条目 1–3：请求 `{region_id, new_region_type, expected_revision?}` → 响应含 `revision_no`+改标后生效态（沿 SaveManualTranslation/§5.3 一次往返先例）；`new_region_type` 复用 `REGION_TYPE_VALUES` 六值；错误码零新码（映射表：非法 payload→`INVALID_REQUEST`/乐观冲突→`INPUT_REVISION_CHANGED`/目标缺失→`TARGET_NOT_FOUND`/未分类→`UNKNOWN`）；改标=经既有 commit seam 新 revision，**origin 恒 `user`**（RegionOrigin 四值零新增）；撤销=既有 `RestoreRegionRevision` 引用不重定义，明文禁止反向改标模拟 | PASS |
| AC2 | §5 表 `ListRegions` 行 + §5.4 条目 5：`RegionSummary` 最小五字段 DTO（region_id/region_type/sfx_policy/origin/revision_no），读取面不含几何/文本/标注状态；**取舍定案=新命令**（三条理由：既有命令面无 region 读取通道且扩容=major 变更、改标数据需求与画布几何通道解耦、详情按 id 过滤避免命令面冗余）；来源字段语义注记：`sfx-arb-` label 不持久化（`entities.py:267-288` snapshot 无 label 字段），机器/人工可区分权威=`origin` | PASS |
| AC3 | §5.4 条目 6/7：并发与人工覆盖 C1–C7（人工优先写通道不互斥、AI 侧 Revision/Lock 双守卫 fail-closed 存候选、乐观期望显式拒绝、改标后决策生效、机器笔上人工叠加、目标缺失）+持久性 P1–P4（重开持久、重检测幂等复用不回滚人工改标、撤销完整恢复+历史保留、撤销后再改标规则幂等）；全部两行式（触发+期望），域守卫事实链见报告 §2 | PASS |
| AC4 | §5.4 条目 8（RULED）：「忽略」=处理动作（gate `SKIP_POLICY` 派生）或过滤状态（UI-local），**不是** RegionType 值；六值闭集零新增；对「持久化忽略状态」方向预拒绝；设计稿 R-015 不回改，差异登记落 verification §3.2 | PASS |
| AC5 | §5.4 条目 4（EV-8 裁决，RULED）：**「按改标时全局配置重快照」**（改标为 sfx）；对称条款=改标为非 sfx 时强制 `skip`（「policy can never leak onto non-SFX regions」跨写路径不变量）。理由：①gate 消费 region 快照不读全局（`gate.py:32-42`）+speech 快照恒 skip（`core_assembly.py:1036-1045`）→继承分支使全局 translate 对改标 region 永久不可达、静默失效无自愈；②与新建语义一致（改标=重新类型化）；③与设计稿 §4.2 translate 行前置一致，UI 零返工。设计稿 EV-8 由此闭合（转 CLOSED 属集成方动作） | PASS |
| AC6 | 头部+Revision history `1.4` 段+§5.4 末条：三处明示「runtime 未实现，本修订不授权 runtime 实现」（实现=T5b 另行释放）；§1–§4/§6–§10 保护语义零放松（diff 核对：仅头部/Revision history/§5/§5.4/§11 变更，§12 原文未动）；协议 minor 目标 `2`→`3` 登记（bump 归实现 Task） | PASS |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1–AC6 逐条自检 | 静态核对：Task 合同 AC 文本 × 契约修订条款 × `src/**` 源码行号证据 | worktree `G:/CODEX/New Manga.worktrees/M2-REGION-RETYPE-CONTRACT-zcode` @`a108996b` | PASS | [contract-freeze-report.md §1](../../verification/M2-REGION-RETYPE-CONTRACT/contract-freeze-report.md) |
| AC3 断言可测性 | 每条断言转录核对：C1–C7/P1–P4 各=单一触发条件+单一可观察期望，验证锚点为 Core 行为 | 同上 | PASS | 报告 §2（契约 §5.4 全文转录） |
| 一致性（交叉引用） | UI 设计稿 RC-1..RC-5/§4.2/EV-8/R-015/A1–A13 × 契约条款；仲裁 Task sfx-arb- 语义 × §5.4 条目 2 | 同上 | PASS | 报告 §3（核对表+差异登记 3 项） |
| 修订纪律（diff 面） | `git diff --stat`（1 file, +59/−3）；`git diff --check`（EXIT=0）；`src/**`/`tests/**`/`apps/**`/`packaging/**`/`doc/STATUS.md`/既有设计稿零 diff 核对 | 同上 | PASS | 报告 §4 |
| runtime 行为 | 未运行——契约冻结 Task 无 runtime 交付；rev 1.4 明示不授权 runtime 实现；C1–C7/P1–P4 测试执行归 T5b | N/A | NOT_RUN（by design） | 报告 §5 |

## 接收方式

- 分支：`agent/zcode/M2-REGION-RETYPE-CONTRACT`；worktree：`G:/CODEX/New Manga.worktrees/M2-REGION-RETYPE-CONTRACT-zcode`；base=`4c12e8af`，delivery_head=`a108996b`。
- 复核入口：读 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 头部/Revision history `1.4`/§5 表两行/§5.4 全文/§11 两行，对照 [verification 报告](../../verification/M2-REGION-RETYPE-CONTRACT/contract-freeze-report.md) 与 Task 合同 AC1–AC6。
- 接收者具体检查建议：①EV-8 理由链的技术事实三锚点（`gate.py:32-42`/`core_assembly.py:1036-1045`/`service.py:521-529`）逐行复核；②错误码映射表「零新码」逐码核对既有字面量出处；③确认 §1–§4/§6–§10/§12 无语义漂移（diff 仅 5 处落点）。

## 下一任务建议（必填）

- Task ID / 标题：**M2-REGION-RETYPE-CONTRACT Review**（本 Task 的独立 Review 环节，reviewer=DeepSeek Harness 非作者）；Review 通过后由集成方执行集成与本 Task done 收口。
- 推荐 Agent / Reviewer：DSH（独立 Review）；集成=编排会话代行 Codex。
- 推荐原因与前置依赖：Task 合同指定 reviewer=DeepSeek Harness（非作者）；前置=本 Handoff 与 delivery_head `a108996b` 已就绪。
- Recovery point：仓库 `G:/CODEX/New Manga`；branch/worktree `agent/zcode/M2-REGION-RETYPE-CONTRACT`（worktree 已存在：`G:/CODEX/New Manga.worktrees/M2-REGION-RETYPE-CONTRACT-zcode`）；base `4c12e8af` / head `a108996b`（+文档 commit）。
- 允许修改路径：Review 报告 `verification/M2-REGION-RETYPE-CONTRACT/**`（新增）；集成阶段允许 STATUS/PLAN 收口与本 Task frontmatter done。
- 禁止范围与新增授权条件：`src/**`、`tests/**`、`apps/**`、`packaging/**`（rev 1.4 不授权 runtime）；M2-C1 既有 §1–§4/§6–§10/§12 保护语义；设计稿/仲裁 Task 产物只读。若 Review 要求契约条款修改，回到本 Task 分支修订并在 Revision history 注记，不得静默改文。
- 交付物：Review 报告（沿 doc/templates/REVIEW.md）；集成后：设计稿 EV-8 转 CLOSED 注记（Task 合同已裁决此分工）。
- 验证命令、环境与完成 Gate：静态复核（无 runtime 命令）；Gate=AC1–AC6 逐条 Review PASS+diff 面符合允许范围+零新码核对通过。
- 可直接转发给 Agent 的指令：「以 DSH 身份 Review M2-REGION-RETYPE-CONTRACT @branch `agent/zcode/M2-REGION-RETYPE-CONTRACT` head `a108996b`（非作者 Review）。读 doc/tasks/M2-REGION-RETYPE-CONTRACT.md AC1–AC6、doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md rev 1.4 草案（头部/Revision history 1.4/§5 表 SetRegionType+ListRegions 两行/§5.4 全文/§11 两行）、verification/M2-REGION-RETYPE-CONTRACT/contract-freeze-report.md。重点：①EV-8 裁决理由链技术事实复核（gate.py:32-42/core_assembly.py:1036-1045）；②错误码零新码逐码核对；③C1–C7/P1–P4 可测性；④§1–§4/§6–§10 零放松。产出 Review 报告至 verification/M2-REGION-RETYPE-CONTRACT/，不改契约正文；发现契约缺陷回 owner 分支修订。」

## 风险与遗留

- **runtime 未实现（by design）**：rev 1.4 为草案；`SetRegionType`/`ListRegions` 的 Python handler、Tauri 面、前端 pin、协议 minor bump（`2`→`3`）全部归 T5b。T5b 未释放前任何实现都无授权。
- **EV-8 裁决的 UI 联动**：裁决=重快照，设计稿 §4.2 translate 行由此可达；「设计稿 EV-8 转 CLOSED」为集成方动作（Task 合同明示），本 Task 未回改设计稿。
- **设计稿差异 1（label 前缀承载）**：读取面以 `origin` 承载机器/人工区分；若未来 UI 需要「仲裁改标 vs 普通检测 sfx」细分来源，属 RC-4（RevisionSummary 结构）候选，须新授权修订（已登记 verification §3.2）。
- **几何读取缺口**：`ListRegions` 最小集不含几何（设计稿 D5/RC-3 剩余部分）；Workbench overlay 若需几何通道，须后续授权修订或归 T5b 一并冻结——集成裁决时留意。
- **TARGET_NOT_FOUND 复用边界**：region 不存在复用该既有码（§8 行「may need richer subcode」注记原样适用）；T5b 若判定需 region 专属 subcode 走新修订，本修订未发明新码。
- 关联 Task：T5b（实现，待释放）、M2-SFX-MISROUTE-UI-MITIGATION（设计稿，EV-8 闭合方）、M2-REGION-OVERLAP-ARBITRATION（sfx-arb- 上游，done）。

## 实验附录（仅实验任务）

不适用（契约冻结 Task，无实验）。
