# M2-SFX-MISROUTE-UI-MITIGATION · AC 自检记录

- 性质：设计交付，无运行验证。本文件 = AC 逐条自检表 + AC4 断言清单自查 + diff 面核对。
- 被检对象：`doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md`（设计文档唯一主体）。
- 环境：base=`fb5d56c6`，claim=`8d844726`，纯文档 diff，无需运行环境。

## 1. AC 逐条自检表

| AC | 要求（Task 合同原文摘要） | 自检结果 | 证据落点（design.md 章节） |
|---|---|---|---|
| AC1 | sfx 疑似警示 + 手动改标入口完整视觉规格（沿 M2-UI1 token 体系），覆盖 Workbench 检测编辑态 + Reader 阅读态两场景 | PASS | §3.1（四元素 E1–E4 + token 引用表）、§3.2（Workbench：叠加规则 + 两幅 ASCII：ViewerPanel/RegionInspector）、§3.3（Reader：页级提示条 + ASCII）、§3.4（机器 vs 人工区分）、§3.5（双主题对比度） |
| AC2 | 改标操作状态机（改标→确认→SfxPolicy 生效语义反馈→撤销）、与 SettingsPanel sfx.policy 联动语义、误改标防护（源文件/Revision 零风险可视传达） | PASS | §4.1（mermaid 状态机 + R1–R6 转换规约）、§4.2（联动表 + 三条硬规则）、§4.3（四条可视传达事实）、§4.4（已渲染损害修复路径） |
| AC3 | region 级字段清单逐项标注 M2-C1 现状承载与否；缺失项登记为契约修订候选、不 widening | PASS | §5 表 D1–D10（已承载 3 / 部分承载 2 / 缺失 5）+ RC-1…RC-5 候选登记 + widening 禁令重申 |
| AC4 | 「违反即红」硬性断言清单（沿 M2-UI1 hard-code guard 先例），每条带理由，供未来实现 Task 直接引用 | PASS | §6 表 A1–A13，每条 = 断言 + 理由（证据锚点：gate.py / detection_sfx.py:202 / M2-C1 §10 / UI 契约 §7.2 / DOMAIN-EXT-DIAG） |
| AC5 | 零产品代码：无 React/Python/Rust 产品实现改动；交付=设计文档+Handoff | PASS（静态原型页诚实省略） | §7.1（零 diff 声明 + 省略理由）、§7.2（EV-1…EV-8 清单）、§7.3（冻结面小结） |

## 2. AC4 断言清单自查（A1–A13 可测性）

| # | 断言主题 | 自查：可测？ | 自查说明 |
|---|---|---|---|
| A1 | 源文件零写路径 | 可测 | 实现 Task 可用 diff 断言（改标路径零文件系统写调用）+ Core 写面审计 |
| A2 | 警示/改标不依赖 OCR 非空或紧贴候选 | 可测 | 空 OCR region 的渲染/交互测试用例可直接构造 |
| A3 | 警示不自动触发领域变更 | 可测 | 警示出现前后 revision 计数/管线状态零变化断言 |
| A4 | 改标后 gate 语义一致 | 可测 | sfx+skip/manual 无自动译文、UI 无「已翻译」态断言（对齐 gate.py 单测语义） |
| A5 | 反向改标显式确认 | 可测 | 交互测试：无确认路径不可达翻译链 |
| A6 | 改标走 revision + 撤销走恢复 | 可测 | revision 计数/origin 断言；撤销后 revision 历史完整性断言 |
| A7 | 机器/人工改标可区分且不互串 | 可测 | `sfx-arb-` 前缀 region 的徽标/来源断言 |
| A8 | 三重编码 | 可测 | 静态断言（字形+文本节点存在）沿 M2-UI1 hard-code guard 先例 |
| A9 | UI 不重算 policy 门 | 可测 | 前端无 decide 等价逻辑的静态检查 + 数据仅来自 Core 快照断言 |
| A10 | Reader 零写操作 | 可测 | Reader 组件无写命令调用静态断言 |
| A11 | SfxPolicy 三值零改动 | 可测 | types.ts/设置页测试零 diff（既有 48 条测试保持绿） |
| A12 | 改标入口限 speech↔sfx | 可测 | 其余四类型入口 disabled + 原因文案断言 |
| A13 | 双主题对比度（r1 R-004 拆分双口径） | 可测 | (a) E2/E3/E4 徽标合成底 ≥4.5:1（E3 新增组合首次取证，R-005）；(b) E1 与 `bg-canvas` 非文字图形 ≥3:1 + 双载体强制——两口径均可测（实现 Task 交付物） |

## 3. diff 面核对

| 检查 | 命令 | 结果 |
|---|---|---|
| 工作区干净 | `git status --porcelain` | 仅本 Task 允许面文件（见 Handoff 提交清单） |
| 尾随空白 | `git diff --check` | EXIT=0（收尾 commit 后复核，见 Handoff 验证表） |
| 禁改面 | `git diff --name-only` 核对 | `apps/desktop/frontend/src/**`、`src/**`、`src-tauri/**`、`doc/contracts/**`、`doc/STATUS.md`、token 真值文件零命中 |

## 4. DSH r1 闭合复核（2026-10-04，verdict=`approved_with_conditions`，0×P0/P1；4×P2+6×P3+7×P4 全文档级）

r1 返修后受影响自检行复核结果（处置对照全表见 Handoff「DSH r1 修订段」）：

| 自检行 | r1 变更 | 复核结果 |
|---|---|---|
| §1 AC2 行 | 状态机三处转换缺陷修复（R-002）：反向取消按来源守卫回退、SFX_ARB_RELABEL 补 undo/反向出边、撤销回触发态（警示保留守卫①） | PASS——mermaid 与 R5/R6 规约一致，无死态、无来源丢失 |
| §1 AC2 行 | 联动表键改 region 快照值（R-001），translate 行加 RC-2/EV-8 前置 | PASS——对 core_assembly 非 SFX 强制 SKIP 事实的两种 EV-8 分支均不再产生错误断言 |
| §1 AC3 行 | D2 source 收缩 `human\|heuristic`（R-003）、D3 响应含 revision_no+undo 来源注记（R-009）、D7 origin 四值口径（R-013）、D8「DTO 结构未定义」口径（R-014） | PASS——零 widening 边界不变 |
| §1 AC4 行 | A13 拆双口径 (a)/(b)（R-004）、E3 首次取证义务（R-005）、A9 映射/决策分界（R-006）、A2 理由 BJ15 ref1 限定（R-012） | PASS——13 条编号稳定，无豁免口 |
| §1 AC1 行 | 警示范围收窄 speech（R-015）、E3/八态/toolbar 同位优先级（R-008）、hex 改对照参考（R-011）、几何字面量登记义务（R-016）、Reader 数据来源 D6→D8/RC-5 更正（R-007）、mermaid 标点（R-017）、依据链表述（R-018） | PASS——三重编码/叠加不合并/虚线保留三规则不受影响 |
| §3 diff 面 | r1 返修零产品代码复核 | PASS——改动面仍仅 design/verification/handoffs/Task 四处 |
