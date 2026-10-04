---
id: M2-REGION-RETYPE-CONTRACT
title: "Region 改标契约冻结：SetRegionType 命令+读取面 DTO+Revision/并发语义+「忽略」定义（T5a；rev 1.3→1.4 草案）"
kind: contract
status: in_progress
approval: user_ruling_2026-10-04_训练质量效率优先_许可降权备案
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-SFX-MISROUTE-UI-MITIGATION, M2-SETTINGS-IPC-CHANNEL]
base_commit: 74fa71e9
branch: agent/zcode/M2-REGION-RETYPE-CONTRACT
worktree: G:/CODEX/New Manga.worktrees/M2-REGION-RETYPE-CONTRACT-zcode
integration_commit: null
---

# M2-REGION-RETYPE-CONTRACT：Region 改标契约冻结（T5a）

## 来源与目标

纠错素材积累链（T5 线）与未来 Workbench 改标 UI 的共同地基。UI 设计稿（M2-SFX-MISROUTE-UI-MITIGATION）已定 RC-1..RC-5 契约修订候选；本 Task 把其核心（RC-1/RC-2）冻结为 M2-C1 契约修订草案（rev 1.3→1.4）。沿 M2-C2 契约修订先例：**只修契约文本，不实现 runtime**（实现=T5b 另行释放）。

## Acceptance Criteria

- [x] AC1 `SetRegionType` 命令冻结（M2-C1 §5 新命令）：请求（region_id/new_region_type/expected_revision）+响应（含 `revision_no`，沿 SaveManualTranslation 先例）；错误码零新码（复用 typed 家族）；改标=新 revision（origin 语义定案：MACHINE/RESTORED 之外的**用户类型决策**标记方案）；撤销=既有 restore 语义引用不重定义。
- [x] AC2 读取面 DTO 冻结（RC-1）：region 列表/详情的最小字段集（id/类型/policy 快照/来源 sfx-arb- 前缀/revision_no/标注状态不含——读取面不含训练语义）；复用既有命令扩容 vs 新命令的取舍定案（给理由）。
- [x] AC3 并发与人工覆盖语义冻结（Codex 第 7 点）：①AI 任务（批量翻译/重检测）运行期间人工改标的冲突规则——人工覆盖优先级、AI 侧 fail-closed 行为、LOCK/Revision 守卫交互；②项目重开/重检测/撤销场景下改标持久性语义。全部写成可测断言（每条给触发条件+期望行为）。
- [x] AC4 「忽略」语义定案（Codex 第 8 点）：`RegionType` 六值枚举**不新增**（设计稿 R-015 已收窄 speech）；「忽略」定为**处理动作/过滤状态**（非领域类型）——落为契约注释+设计稿对齐注记（不回改已集成设计稿，差异登记于本 Task）。
- [x] AC5 SfxPolicy 快照规则定案（EV-8 裁决）：改标后 policy 快照=「按改标时全局配置重快照」vs「继承原快照」二选一冻结+理由（技术事实：core_assembly 强制非 SFX=SKIP，speech→sfx 改标时必须产生新 policy 值——与 UI 设计稿 §4.2 联动表对齐）。
- [x] AC6 修订纪律：契约修订不放松既有保护语义；版本记录 rev 1.4 草案段完整；明确「本修订不授权 runtime 实现」。

## 允许修改范围

`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（rev 1.3→1.4 草案标注）、`doc/tasks/M2-REGION-RETYPE-CONTRACT.md`、`doc/handoffs/M2-REGION-RETYPE-CONTRACT-*.md`、`verification/M2-REGION-RETYPE-CONTRACT/**`。

## 禁止范围

`src/**`、`tests/**`、`apps/**`、`packaging/**`、`doc/STATUS.md`、既有设计稿/Task 产物（只读引用）、M2-C1 既有 §1-§4 保护语义。

## 测试要求

| 场景/AC | 计划步骤 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC3 断言可测性 | 每条语义给触发+期望 | 静态 | PASS（C1–C7/P1–P4 全部落 M2-C1 §5.4，每条=触发条件+期望行为两行式，验证锚点=Core 行为） | [contract-freeze-report.md §2](../../verification/M2-REGION-RETYPE-CONTRACT/contract-freeze-report.md) |
| 一致性 | 与 UI 设计稿/仲裁 Task 交叉引用核对 | 静态 | PASS（核对表：RC-1..RC-5/§4.2/EV-8/R-015/A1–A13/sfx-arb- 语义逐项；差异登记 3 项落报告 §3.2） | [contract-freeze-report.md §3](../../verification/M2-REGION-RETYPE-CONTRACT/contract-freeze-report.md) |
| 修订纪律（diff 面） | 允许面核对+零新码核对 | 静态 | PASS（`git diff --stat`=1 file +59/−3 仅契约；`git diff --check` EXIT=0；错误码映射表逐码复用既有字面量） | [contract-freeze-report.md §4](../../verification/M2-REGION-RETYPE-CONTRACT/contract-freeze-report.md) |

## 依赖、风险与阻塞

depends_on 已 done。风险：EV-8/AC5 裁决影响 UI 联动表——设计稿已按「region 快照优先+EV-8 OPEN」写，本 Task 裁决后登记对齐注记即可（设计稿 EV-8 转 CLOSED 由集成方处理）。

## 交付与运行记录

- **delivery_head（契约修订）：`a108996b`**（M2-C1 rev `1.3`→`1.4` 草案：头部/Revision history 1.4/§5 表 SetRegionType+ListRegions 两行/§5.4 新增/§11 两行；claim=`8d41d8ef`，base=`4c12e8af`）。runtime 未实现，本修订不授权 runtime 实现（T5b 另行释放）。
- AC 自检结论：AC1–AC6 全 PASS（证据与 AC3 断言清单、交叉核对表、差异登记见 [verification 报告](../../verification/M2-REGION-RETYPE-CONTRACT/contract-freeze-report.md)）。
- EV-8 裁决：按改标时全局配置重快照（sfx 方向）；非 sfx 方向强制 skip（M2-C1 §5.4 条目 4，RULED）。
- Handoff：[M2-REGION-RETYPE-CONTRACT-a108996b.md](../handoffs/M2-REGION-RETYPE-CONTRACT-a108996b.md)（下一任务建议=DSH 非作者 Review）。Review：尚无。
- status=in_progress：待 Review+集成后由集成方收口 done（frontmatter integration_commit 由集成方回填）。
