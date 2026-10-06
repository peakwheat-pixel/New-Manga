---
id: M2-SFX-MISROUTE-UI-IMPL-1
title: "SFX 误路由缓解 UI 产品实现：E1-E4 视觉+不对称状态机+改标交互（设计契约 M2-SFX-MISROUTE-UI-MITIGATION 的实现切片）"
kind: feature
status: ready
owner: ZCode
reviewer: DeepSeek Harness（非作者，技术主审）；Qoder（非作者 UI/UX 复审，派发通道可用时补审）
integrator: 编排会话代行 Codex（用户全权授权）
approval: user_2026-10-06「释放：Workbench React 页（依赖已就绪）、UI-MITIGATION 实现（blocked 已解除）、BJ13 召回恢复链」三件之一（候选 B；**blocked_on M2-WORKBENCH-REACT-1 集成，接力派发**）
depends_on: [M2-SFX-MISROUTE-UI-MITIGATION, M2-WORKBENCH-REACT-1]
base_commit: 3a65150b
branch: agent/zcode/M2-SFX-MISROUTE-UI-IMPL-1
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-MISROUTE-UI-IMPL-1-zcode
review_events: []
created: 2026-10-06
---

# Task: M2-SFX-MISROUTE-UI-IMPL-1 — UI-MITIGATION 产品实现

## 背景与授权

用户 2026-10-06 释放三件中的候选 B。设计契约 M2-SFX-MISROUTE-UI-MITIGATION（done @merge `4d77a778`）登记「产品实现 blocked_on Workbench React 页+region 通道」——该前置由 M2-WORKBENCH-REACT-1（候选 A，同批释放）交付：React 页壳（`<WorkbenchPage>` 五区+`<RegionOverlay>` SVG 只读画框+`<RegionInspector>`）+ region client（`listRegions`/`setRegionType`）+ D5 几何读取面。

**派发时序（真依赖，非配额）**：本 Task status=ready 但 **Owner 派发等 M2-WORKBENCH-REACT-1 merge 后接力**——E1-E4 落点组件（`<RegionOverlay>`/`<RegionInspector>`）与数据通道（region client+几何）在前置集成前不存在于集成态。同批释放=合同冻结与授权就位，避免二次请示。

## 验收条件

- **AC1 改标交互全套（不对称状态机，FROZEN §4.1）**：speech→sfx 即时执行无确认（R2）、sfx→speech 显式确认框明示后果（R3，含 §4.2 反馈条文案——EV-8 已 CLOSED：改标按当前配置重快照，translate 行可达须明示「将按拟声词翻译链重新翻译」）、撤销=revision 恢复回触发态（R5，undo=restore 到改标前 revision 非二次改标）、失败即原态+来源守卫（R6）；消费 `setRegionType`（expected_revision 并发保护，INPUT_REVISION_CHANGED 处理沿 §5.4 错误码映射）。
- **AC2 E1-E4 视觉按设计实现**：落点 `<RegionOverlay>`（SVG 层）+`<RegionInspector>`（§3.2）；E4 反馈条于 ViewerPanel 画布底部居中（:119-121）；改标入口示意 :126-142。E1 疑似警示的数据源=`suspect.sfx` 字段（RC-1）——**RC-1 契约修订归本 Task 裁量**：字段未落地前 E1 不渲染、不虚构数据（设计 :150 原文约束）；若 Owner 判定本 Task 含 RC-1 additive 修订（M2-C1 rev 追加+Core runtime+minor 处置），沿 WORKBENCH-REACT-1 AC1 的核实-择一-登记流程；若判定不含，E1 登记为「数据源 NOT_IN_SCOPE 待后续字段 Task」并在交付注记——二择一须在 Task 内显式登记理由。
- **AC3 Design-to-impl 保真核验**：设计文档 §2 状态机、§3 视觉、§4 反馈文案逐条对照实现，偏差逐条登记（设计为 FROZEN 契约，实现偏差=偏差登记非静默改动）；设计 §7 断言（13 条）中 UI 可测面落入 vitest。
- **AC4 测试与回归**：vitest 交互状态机单测（四分支+撤销+失败路径先红后绿）+组件测试；前端基线等量递增；pytest 基线不破坏；若触 Core runtime（RC-1）则受影响套件等量递增+契约修订草案登记。
- **AC5 文档**：Task 回填+Handoff+设计文档尾注（实现完成状态注记，设计原文不回改——沿 EV-8 集成注记先例 :340）。

## 纪律与限制

- 允许路径：`apps/desktop/frontend/**`、`src/bootstrap/core_service.py` 与 Core 应用层（仅 AC2 选含 RC-1 时，逐文件声明）、`apps/desktop/src-tauri/**`（仅 RC-1 需要新命令时，逐文件声明）、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（仅 RC-1 additive 修订）、`doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md`（仅文尾实现注记）、`tests/**`、`verification/M2-SFX-MISROUTE-UI-IMPL-1/**`、`doc/tasks/M2-SFX-MISROUTE-UI-IMPL-1.md`、`doc/handoffs/`。
- 禁改：设计契约 §4.1 状态机语义（FROZEN）、`src/ui/qml/**`、GATE runner 场景集、`doc/STATUS.md`/`doc/REBASELINE_PLAN.md`（集成方收口面）、M2-WORKBENCH-REACT-1 已交付的页壳读取面行为（在其之上叠加）。
- **范围边界**：Reader 页级提示条（§3.3）——Reader React 页不存在，本 Task 不实现、不虚构；RC-4/RC-5 不在范围；detect/翻译链行为零变更（本 Task 纯 UI 层+可能的 RC-1 数据面）。
- Owner 分工注记：同 M2-WORKBENCH-REACT-1（ZCode 实现、Qoder 非 author UI/UX 复审可选）。
