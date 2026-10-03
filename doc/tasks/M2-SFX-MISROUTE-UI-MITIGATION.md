---
id: M2-SFX-MISROUTE-UI-MITIGATION
title: "SFX 误路由缓解 UI 设计切片：region 手动改标 sfx + speech 疑似警示（裁决①授权；设计交付，产品实现 blocked_on Workbench React 页）"
kind: design
status: done
integration_commit: 4d77a778
approval: user_ruling_2026-10-04_按推荐_裁决1_维持现状+UI缓解
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者；集成核验=编排会话代行 Codex）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-SFX-DETECT-DOMAIN-EXT-DIAG, M2-REGION-OVERLAP-ARBITRATION]
base_commit: fb5d56c6
branch: agent/zcode/M2-SFX-MISROUTE-UI-MITIGATION
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-MISROUTE-UI-MITIGATION-zcode
owner_claim: 2026-10-03T22:26:03Z
delivery_head: c92eaddd
rework_head: 42be3c11
integration_commit: null
---

# M2-SFX-MISROUTE-UI-MITIGATION：SFX 误路由缓解 UI 设计切片

> **改派记录（2026-10-04，用户指令）**：原分配 Owner=Qoder（UI/UX 设计责任方默认）；用户裁决改派 Owner=**ZCode**（AGENTS.md「除非 Task 另行明确分配」条款+M2-S3/M2-C2 改派先例）。交付形态不变（设计文档，零产品代码）；非作者 Reviewer=DeepSeek Harness 不变。原 Qoder 分配 branch/worktree 命名作废，未创建过现场。

## 来源与目标

- 来源：[M2-SFX-DETECT-DOMAIN-EXT-DIAG](M2-SFX-DETECT-DOMAIN-EXT-DIAG.md) report §5 方案⑤（用户裁决① 2026-10-04「按推荐」采纳=维持现状+产品侧缓解）。BJ 域误路由损害形态实证：SFX 被判 speech/text → 对话链乱译进渲染成品（BJ13 region#1/#3）；仲裁 Task（[M2-REGION-OVERLAP-ARBITRATION](M2-REGION-OVERLAP-ARBITRATION.md)，裁决③并行释放）闭合检测侧，本 Task 闭合用户侧兜底。
- 现状侦察（2026-10-04）：React 前端现有面=Library/Settings/resourceChannel/ac1 driver 四块，**尚无 Workbench/Reader 页面与 region 数据通道**。故本 Task 为**设计交付形态**（沿 M2-UI1 先例：Design, verification and Handoff only; no product implementation），产品实现 blocked_on Workbench React 页面与 region/译文 IPC 通道存在（另行释放）。
- 目标：sfx 疑似警示 + region 手动改标的**视觉/交互契约**，使未来 Workbench React 实现有冻结标准；同时把仲裁 Task 需要预留的数据接口注记（region 级 sfx 疑似信号）反馈给其 AC1 提案。

## Acceptance Criteria

- [ ] AC1 视觉契约：sfx 疑似警示（region 角标/边框/徽标形态）与手动改标入口（speech→sfx / sfx→speech 双向）的完整视觉规格（沿 M2-UI1 token 体系），覆盖检测后 Workbench 与 Reader 阅读态两场景。
- [ ] AC2 交互契约：改标操作状态机（改标→确认→SfxPolicy 生效语义反馈→撤销）、与 SFX 策略设置页（既有 SettingsPanel sfx.policy）的联动语义、误改标的防护（源文件/Revision 零风险约束的可视传达）。
- [ ] AC3 数据需求注记：本 UI 所需 region 级字段清单（sfx 疑似信号、当前 region_type、policy 生效态），逐项标注现有契约是否承载（M2-C1 rev 现状）——缺失项登记为未来契约修订候选，不擅自 widening。
- [ ] AC4 判别力验证：契约文档含「违反即红」的硬性断言清单（沿 M2-UI1 hard-code guard 先例），供未来实现 Task 直接引用。
- [ ] AC5 零产品代码：无 React/Python/Rust 产品实现改动；交付=设计文档+（可选）静态原型验证页（历史 .qoder-credits canvas 先例）+Handoff。

## 允许修改范围

- `doc/design/M2-SFX-MISROUTE-UI-MITIGATION/**`（新增设计文档）、`doc/tasks/M2-SFX-MISROUTE-UI-MITIGATION.md`、`doc/handoffs/M2-SFX-MISROUTE-UI-MITIGATION-*.md`、`verification/M2-SFX-MISROUTE-UI-MITIGATION/**`；
- 可选：仓库既有设计 token 文档的引用性补充章节（只增不改既有定义）。

## 禁止范围

- `apps/desktop/frontend/src/**`、`src/**`、`src-tauri/**`、`doc/contracts/**`、`doc/STATUS.md`；
- 产品实现、IPC 通道扩展、SfxPolicy 语义变更（设置页已 done 的三值策略零改动）；
- 检测/仲裁行为（属 M2-REGION-OVERLAP-ARBITRATION）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1-AC4 | planned：设计评审（DSH 非作者静态 review）+AC4 断言清单逐条自检 | 无需运行环境 | owner 自检 PASS（2026-10-03）；DSH r1=approved_with_conditions（0×P0/P1，4×P2+6×P3+7×P4→18 条全闭合 @42be3c11）；DSH r2=approved_with_conditions（18/18 闭合，N-1..N-4 集成方闭合） | `verification/M2-SFX-MISROUTE-UI-MITIGATION/ac-self-check.md` |
| AC5 零产品代码 | `git diff fb5d56c6..HEAD --name-only` 面核对 + `git diff --check` | `c92eaddd` | PASS（改动面仅 design/verification/handoffs/Task 四处；EXIT=0） | Handoff 验证表 |

## 依赖、风险与阻塞

- depends_on：M2-SFX-DETECT-DOMAIN-EXT-DIAG（done，损害形态证据）、M2-REGION-OVERLAP-ARBITRATION（ready，仲裁语义影响「疑似」信号定义——设计按双形态兼容：改标前疑似警示/改标后确定态；仲裁 Task AC1 定案不回改本 Task 视觉规格，仅数据注记）。
- 风险：Workbench React 页尚未释放，契约可能随页面实现演进——以 AC4 断言清单锚定不可变语义，其余标注 EVOLVING。
- 产品实现 Task 的释放条件：Workbench React 页面 + region/译文 IPC 通道 Task 存在且集成；届时本设计为其 UI 验收输入。

## 交付与运行记录

- Handoff：[M2-SFX-MISROUTE-UI-MITIGATION-c92eaddd](../handoffs/M2-SFX-MISROUTE-UI-MITIGATION-c92eaddd.md)（含 DSH r1 修订段）。
- Review：DSH r1（2026-10-04，非作者）=`approved_with_conditions`（0×P0/P1；4×P2+6×P3+7×P4，全文档级）——设计核心语义全部核对成立（损害链、改标语义、SfxPolicy 门、零 widening、token 真实性、13 断言思路）；18 条条件已于 r1 返修（rework=`42be3c11`）逐条闭合，处置对照见 Handoff「DSH r1 修订段」。r2 闭合复核：待编排方派发。
- 集成：尚无。

### DSH r1 返修记录（Owner=ZCode；2026-10-04，rework=`42be3c11`，零产品代码）

- **P2 四条全闭合**：R-001 联动表键改 region 快照值（translate 行加 RC-2/EV-8 前置；core_assembly 非 SFX 强制 SKIP 事实落入——speech 快照恒 skip，按全局值断言在 EV-8 沿用分支下不再错误）；R-002 状态机三处（反向取消来源守卫保 SFX_ARB 态、SFX_ARB_RELABEL 补撤销/反向出边、撤销回触发态警示保留）；R-003 疑似信号 source 收缩 `human|heuristic`（仲裁=确定态改标，以 `sfx-arb-` 前缀+origin=machine 追溯）；R-004 A13 拆双口径（徽标 4.5:1 合成底 / E1 边框 3:1 非文字图形对 `bg-canvas`+双载体强制）。
- **P3/P4 十四条全闭合**：修订 17+登记 1（R-015 采纳收窄、非 speech 出口登记 EV-1；其余为精确化——E3 首次取证义务、A9 映射/决策分界、Reader 来源 D8/RC-5 更正、同位优先级与五层计数、RC-2 响应 revision_no、hex 对照口径、BJ15 ref1 限定、origin 四值、D8 DTO 口径、几何字面量登记、mermaid 标点、依据链表述、R-010 status 流转 in_review）。逐条对照表见 Handoff「DSH r1 修订段」；自检复核见 ac-self-check.md §4。
- status 按 R-010 口径流转 `in_progress→in_review`（r1 已出 verdict，待 r2 闭合复核后由集成方流转）。

### 交付记录（Owner=ZCode；设计交付 2026-10-03，base=`fb5d56c6`，claim=`8d844726`，delivery=`c92eaddd`）

- **交付物**：主设计契约 `doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md`（新增目录；§0 速览/§1 损害与改标语义/§2 领域事实六条/§3 AC1/§4 AC2/§5 AC3/§6 AC4/§7 AC5/§8 边界自证）+ 自检 `verification/M2-SFX-MISROUTE-UI-MITIGATION/ac-self-check.md`。**零产品代码**：`apps/desktop/frontend/src/**`、`src/**`、`src-tauri/**`、`doc/contracts/**`、`doc/STATUS.md`、token 真值文件零 diff；静态原型验证页诚实省略（Workbench React 页不存在，原型页无两场景数据流可验证）。
- **AC1 视觉契约（PASS）**：警示=叠加层 E1（warn 色 2px **实线**边框，虚线保留给「需校对」）+ E2 徽标 pill（`♪?` + warn-soft/st-warn-t + 文本，三重编码）；改标成功态 E3 类型徽标（skip 色 `♪`，文案按 **region policy 快照**分档）；反馈条 E4。Workbench 双入口（RegionOverlay 右键菜单——与草稿多边形右键闭合按草稿态互斥——+ RegionInspector 按钮组）；Reader=页级提示条+跳转（诚实于 `GetReaderProjection` 无 region 面）；机器改标（`sfx-arb-`）加 `⧉` 字形区分。token 全部引用 Graphite Atelier（`tokens-cand-f.json`），零复制零新增定义。
- **AC2 交互契约（PASS）**：不对称状态机（mermaid + R1–R6 规约）——speech→sfx 即时执行+undo 窗（默认 skip 下只减害）；sfx→speech 显式确认框（反向=重新进入对白翻译链，须明示乱译回归风险）；撤销=`restore_revision`（禁止反向改标模拟）；与设置页联动三硬规则（只读不写、region 快照显示优先、三值零改动）；已渲染损害闭环=反馈条 `[重渲染本页]`（`rerender_single` 语义，改标不抹除已贴译文、不得静默清空历史译文）。
- **AC3 数据需求（PASS，登记不改约）**：D1–D10 逐项对照 M2-C1 rev 1.3——已承载 D1/D9/D10，部分承载 D6/D7，缺失 D2（疑似信号字段）/D3（改标命令；Core `RegionEditingService` 现无 `set_region_type`）/D4/D5（region 读取面；`RegionSummary` 结构未定义）/D8（Reader 疑似计数）→ **RC-1…RC-5 契约修订候选登记，零 widening**。仲裁 Task 交付记录的「UI-MITIGATION 对齐注记」（疑似字段无产出、属未来契约修订候选）由本表承接闭环。
- **AC4 硬性断言（PASS）**：A1–A13 十三条红线，每条带理由与证据锚点（`gate.py:32-42`、`detection_sfx.py:202`、M2-C1 §10、UI 契约 §7.2、DOMAIN-EXT-DIAG BJ15 深盲 0 候选等）；可测性自查 13/13。
- **AC5 零产品代码（PASS）**：见交付物行；EV-1…EV-8 演进项 + 冻结面小结（§7.3：断言/改标语义表/领域事实/状态机拓扑/三条视觉规则不可演进）。
- **遗留（预期内）**：EV-8 改标后 policy 快照语义（OPEN，归 RC-2 裁决，UI 两侧兼容）；警示信号初始仅人工来源（检测器 BJ 零响应，方案⑤「可发现/可修正」非「自动发现」边界）。
- 证据：[design.md](../design/M2-SFX-MISROUTE-UI-MITIGATION/design.md) + [ac-self-check.md](../../verification/M2-SFX-MISROUTE-UI-MITIGATION/ac-self-check.md) + [Handoff](../handoffs/M2-SFX-MISROUTE-UI-MITIGATION-c92eaddd.md)。（status 流转记录见上方「DSH r1 返修记录」：交付时 in_progress，r1 返修后按 R-010 流转 in_review。）
