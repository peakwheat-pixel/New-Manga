verdict: unacceptable

---
task_id: UIUX-V2-RUNTIME-REALCORE-2
reviewer: Codex
author: DSH
base_commit: 3070050a8db6b9423eff0deb6cbb71d5a5bfa29d
reviewed_head: 0718482e5535cc3d0f923aa6681f79288b9b5f50
decision: changes_requested
scope: 仅复审 apps/desktop/frontend/e2e/uiux-v2/run.mjs 的指定 diff；不修改源码、不重跑 E2E。
---

# Review：UIUX-V2-RUNTIME-REALCORE-2 — DSH closeout r2

## 范围与依据

固定审查 `3070050a8..0718482e5`，文件仅 `apps/desktop/frontend/e2e/uiux-v2/run.mjs`。对照上一轮 `review-codex-dsh-closeout.md`、S8 断言与 `record()` 逻辑，并读取 `run-i35/report.json`。工作区在审查前无未提交变更；未修改源码或运行验收。

## 必答问题

1. **三个问题未全部解决。** 原先无差别降级已改成标签白名单，统计口径与结论范围也已修正；但降级没有受“CDP 注入路径确实不可用”这一条件约束，见下方 R-CLOSEOUT-R2-1。故第 1 项部分解决，整体仍不可接受。
2. **四个白名单字符串与 S8 的 `checks.push` 标签逐字一致。** 对照 `run.mjs:666`、`:677`、`:728`、`:737`、`:739`、`:743-745` 与白名单 `:771-776`，包括空格、大小写及 `input[type=file]` 写法均一致。当前 run-i35 实际记录也包含相同标签（`run-i35/report.json:498-523`）。
3. **“S6 创建的作品仍来自真实书架”不会被降级。** 它在 S8 的 push 位于 `run.mjs:626`，不在四项白名单内；降级循环只处理 `CDP_INJECTION_LABELS.includes(item.label)` 为真的项（`:777-780`）。同一标签未来即使在 S8 失败也保持 `FAIL`。但错误码断言的回归仍有被吞风险，见 R-CLOSEOUT-R2-1。
4. **HUMAN_VERIFY 仍在明细中可见，没有被 passRate 隐藏。** `record()` 明确累计 `humanVerify` 并将其和 `total` 写入 `checkSummary`（`run.mjs:57-76`）；终端逐项打印状态和标签（`:78-80`）。run-i35 的 S8 为 `humanVerify=5`、`total=9`、`failed=0`（`run-i35/report.json:533-541`），四条降级项和 G1 项仍分别列明（`:498-530`）。`passRateScope` 也明确写出 `KNOWN_DEFECT` 与 `HUMAN_VERIFY` 不计分母（`run.mjs:76`）。因此明细可见；S8 顶层仍显示 `ok=true`/PASS，是当前显式“未验证项单列”口径的结果，不代表这些项目已验证通过。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-CLOSEOUT-R2-1 | P1 | `apps/desktop/frontend/e2e/uiux-v2/run.mjs:737-739, 771-783` | 降级条件只有 `item.status === "FAIL"` 与标签白名单匹配，没有核实 CDP 注入是否不可用。若未来 `setImportFileInput` 成功交付不支持格式文件，但应用未显示错误码，`导入失败明确显示错误码` 的 FAIL 仍会被改成 HUMAN_VERIFY，导致真实产品回归不再阻断验收。相同问题也适用于白名单中在输入控件/注入能力恢复后出现的断言失败。 | `:737` 在 `injectedInvalid.delivered` 为真后直接检查错误码；`:778` 不论该交付结果为何都按 label 降级。run-i35 当前没有覆盖这条路径：`report.json:519-523` 是因无输入控件而产生的人工项。 | 只在实际检测到 CDP 注入前置不可用时降级那些由该前置阻断的断言；输入交付已成功后的错误码校验失败应保留 FAIL。 | open |

## 修订项判定

- **无差别循环：部分修复。** 四项白名单保护了 S6 真实书架和其它非白名单断言（`:768-780`），但白名单标签仍被无条件降级；尚未满足“仅 CDP 注入不可用时才降级”。
- **passRateScope：已修复。** 分母为 PASS + FAIL（`:67-76`），声明同时排除 `KNOWN_DEFECT` 与 `HUMAN_VERIFY`；明细计数仍可见。
- **自动化能力表述：已收窄。** 注释明确说本结论只证明 CDP 注入不可用，UI Automation/键盘路径本轮未验证（`:761-766`）；没有据此断言其它路径不可能。
- **场景标题：已修复。** 明确写出 CDP 注入不可用、转人工验证及其它断言继续门禁（`:787`）。

## 验证

| 场景 | 方法 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 指定 diff 与 S8 标签 | 静态对照 `git diff 3070050a8 0718482e5 -- apps/desktop/frontend/e2e/uiux-v2/run.mjs` 及每处 `checks.push` | base `3070050a8` / head `0718482e5` | PASS（只读审查） | `run.mjs:666-745, 771-783` |
| HUMAN_VERIFY 汇总与呈现 | 检查 `record()`、终端输出及 canonical report | head `0718482e5` | PASS（静态检查） | `run.mjs:57-80`; `run-i35/report.json:465-541` |
| run-i35 总体结果 | 读取 canonical report | head `0718482e5` | PASS（report 记载 10 个场景均 `ok=true`，S8 有 5 项 HUMAN_VERIFY） | `run-i35/report.json`；脚本按 `report.ok` 决定进程 exit（`run.mjs:968, 993-1005`）。本复审未重跑；未发现独立保存的 run-i35 进程 exit-code 记录。 |
| CDP 可用时错误码回归能否被门禁捕获 | 静态追踪实际注入成功分支和降级条件 | head `0718482e5` | FAIL（门禁缺陷） | `run.mjs:733-739, 777-783` |
| UIA/键盘驱动原生选择器 | 未执行 | head `0718482e5` | NOT_RUN | 本次范围只审指定脚本 diff；源码注释亦说明本轮未验证 `run.mjs:764-766`。 |

## 结论与复审

`0718482e5` 修正了原先全量降级、统计口径说明及 CDP 结论措辞，但白名单成员按标签无条件降级，仍可吞掉 CDP 已成功交付后的错误码回归。R-CLOSEOUT-R2-1 为 P1，修复该门禁后需再审新 head；当前结论 `unacceptable`。

本次仅新增本复审报告；未改验收脚本、未运行测试、未提交 commit。