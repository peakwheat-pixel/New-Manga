---
task: M2-SFX-MISROUTE-UI-IMPL-1
owner: ZCode（编排接管：子 agent 配额耗尽后同身份续做）
base_commit: ecbfe9cb
delivery_head: 见 git log 分支头（本 Handoff 随 docs commit 落，hash 以分支 tip 为准）
status: in_review（停写）
date: 2026-10-06
---

# Handoff: M2-SFX-MISROUTE-UI-IMPL-1 — UI-MITIGATION 产品实现

## 1. 交付一句话

UI-MITIGATION 设计契约（FROZEN）的产品实现切片：不对称状态机四分支的 UI 决策面（纯函数 `relabelMachine.ts`）+ E1-E4 视觉层（RegionOverlay SVG 警示外圈/E2E3 pill/ViewerPanel 反馈条）+ 双改标入口（RegionOverlay 右键菜单 + RegionInspector 按钮组）+ 反向改标确认框；vitest 77→**102**（+25 先红后绿）、build EXIT=0、pytest 1847+1sk+1 failed 等量。

## 2. commit 链（base `ecbfe9cb`，分支 `agent/zcode/M2-SFX-MISROUTE-UI-IMPL-1`）

- claim（frontmatter in_progress+base 对账 3a65150b→ecbfe9cb）
- impl（relabelMachine+确认框+右键菜单+RegionOverlay/ViewerPanel/RegionInspector/WorkbenchPage 扩展）
- test（relabelMachine.test 20+WorkbenchPage.test overlay mitigation 5+前置断言 1 处按 IMPL-1 口径更新）
- verify（raw 证据 8 log）
- docs（Task 回填+本 Handoff+设计尾注）

## 3. AC 判定与关键裁量

| AC | 判定 | 一句话 |
|---|---|---|
| AC1 | **PARTIAL** | 四分支中 undo 执行面=禁用态+原因（Core 无 restore runtime；A6 禁止反向改标模拟撤销）；其余三分支+守卫①②+expected_revision 并发保护全落地 |
| AC2 | PASS | E1-E4 全落地；**RC-1 裁定=不含**：设计 R1 原文「警示置位不写 revision、初始唯一来源是人工」→suspect=纯前端 UI 态，RC-1 契约修订留给持久化/heuristic 需求（OPEN-2） |
| AC3 | PASS | 偏差 9 条逐条登记（Task 回填）；A2/A3/A5/A8/A9/A12 可测面落 vitest |
| AC4 | PASS | vitest 102=77+25/build EXIT=0/pytest 1847 等量（failed=test_catalog 既有） |
| AC5 | PASS | Task 回填+Handoff+设计尾注（原文零回改） |

## 4. Review 转发指令（可直接转发）

> 对 M2-SFX-MISROUTE-UI-IMPL-1 做非作者 r1 Review：worktree `G:/CODEX/New Manga.worktrees/M2-SFX-MISROUTE-UI-IMPL-1-zcode`，分支 `agent/zcode/M2-SFX-MISROUTE-UI-IMPL-1`，base `ecbfe9cb`。合同=`doc/tasks/M2-SFX-MISROUTE-UI-IMPL-1.md`；交付回填=Task 文档「交付回填」节；Handoff=本文。重点核：①RC-1 裁定（不含）是否成立——对照设计 R1/OPEN-2 原文；②AC1 PARTIAL 判定（undo 禁用）是否合规——A6 红线 vs 设计 R5；③偏差 9 条是否有漏/错登记；④A1-A12 断言逐条（零源文件写路径/空 OCR 可警示/警示不自动动作/前端零决策/A12 禁用+原因/三重编码）；⑤禁改面（设计 §4.1 状态机语义、qml、GATE runner、WORKBENCH 已交付读取面行为）；⑥vitest 102 构成与 raw log。结论=approved/approved_with_conditions/changes_requested。

## 5. 已知限制与后续候选

- undo/rerender/revision 历史三个动作按钮=禁用态（restore/rerender/ListRegionRevisions runtime 均在后续命令面 Task；建议与 RC-4 域一并释放）。
- SFX_ARB 不可达+⧉ 字形未渲染（label 前缀不在读取面，RC-4）。
- A13(a) E3 对比度首取证据 deferred 至 token 真值链落地（fallback 值非真值）。
- EV-5 全局不一致提示行 deferred。
- Qoder 非 author UI/UX 复审可选（派发通道可用时）——视觉层（E1/E2/E3 pill 几何、反馈条形态）是其复审主对象。
