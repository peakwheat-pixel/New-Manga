---
task_id: DIAG-M2-LOCK-CHANGED-REPRO-002
author: ZCode (Owner)
recipient: DeepSeek Harness (non-author Review) → Codex proxy (Integrator)
base_commit: b9fc977017f101a9731d4cb4bf5d270cc6f65d62
delivery_head: 2c13530b (Owner branch tip: implementation/evidence 8d2162c1 + 文档轮 145b3ed5/fb36d21f + r2 review import 2c13530b) — 本 Handoff 以文档提交追加，引用实现 head
status: delivered_awaiting_review
---

# Handoff：DIAG-M2-LOCK-CHANGED-REPRO-002 — regionless LOCK_CHANGED 缺口 mock detect 两段式复现核实

## 交付结果（结论先行）

**AC4 结论（四选一 → ③「已由 M2-P1 修复」变体，登记有误不成立）**：

1. **登记缺口真实存在过**：S2（修复前锚点 `d268a170`，M2-P1 merge `a174fb9c` 的 main 侧 parent）上，mock detect（`assemble_core_services(mock_local_providers=True)` 注册路径）两段式 Run1（`TRANSLATE_ALL` regionless 自动前插 detect）复现 `ocr FAILED error_code=LOCK_CHANGED`，且 [DIAG-M2-REGIONLESS-LOCK-CHANGED-001](../research/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md) 诊断三特征逐项齐备：`target_id == page_id`、`input_refs` 无 `"region"` 键、`error_detail` 含 `expected None`。**M2-AC1 handoff §风险与遗留的登记在写作时点（2026-09-28 11:06，缺陷未修）属实。**
2. **机制上非 mock-detect 特有**：S1（HEAD）与 S2（`d268a170`）的判别点由归因 diff 证据锁定（DSH r1 F-001）：`d268a170..57a83485` 区间 `src/` 变更**恰 3 文件**，其中与本链写守卫路径相关的行为变化**唯一**= `src/application/tasks/service.py` 的 M2-P1 重绑（+15/-2，`replace(item, region_id=primary)` → `replace(item, region_id=primary, target_id=primary)` + 不变式 docstring）；另两个文件（`src/application/export/service.py`=M2-AC1 Reader export lineage、`src/bootstrap/core_service.py`=M2-AC1 stub decoder）均不在 detect→backfill→ocr 写守卫路径上，其余区间增量全为 tests/apps/docs/experiments（[f001-attribution-diff.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/f001-attribution-diff.log)）。同一 harness、同一场景，修复前红/修复后绿。真 docTR 在修复前是否同样触发属**推断**（未实测，无当时运行证据），如实标注；但不影响「已修复」结论。
3. **已由 M2-P1 修复**：S1 在 HEAD 上 Run1 全链 9 步（detect→ocr→color→term_extract→translate→segment→mask_refine→inpaint→render）一段式 `COMPLETED`；ocr StepRun 取证 `target_id == region_id`、`input_refs_keys == ["region"]`——`PlanUnit.target_id ≡ 写目标` 不变式生效，`LOCK_CHANGED` 未复现。
4. **M2-TA3-A「未复现」的根因**：其 5 case 运行于修复后的 main（M2-P1 `a174fb9c` 先于 M2-TA3-A base），非「mock-detect 特有」、非「登记有误」。
5. **时序条件性维度（S3，v5 终版）**：S2 轮 run1 失败后，**Run4 `retry_failed_targets` 探针**（v5 起置于 region 级链之前）按 Region fan-out 重规划并**真实执行 region 级链 8 步（ocr→…→render）后 `COMPLETED`**——「首跑失败、重试成功」用户症状机理直接实证（DIAG-001 §4 断言的运行级复核）；Run2（`RETRANSLATE_REGION_FULL`，强制重跑语义）8 步 COMPLETED；两轮 Run3（同命令 `TRANSLATE_ALL` 重规划）`COMPLETED` 零新 step_runs（既有完成态幂等语义）。该缺口从来是**单 run 内 detect→backfill→ocr 首链**条件性，重试/重规划路径无缺口。

**处置建议**：

- [M2-TA3-A](../../doc/tasks/M2-TA3-A.md) **L-1**：闭为「已核实——缺口真实、已由 M2-P1 修复（`a174fb9c`）、非 mock-detect 特有」，不再保留缺陷候选。
- [M2-AC1 handoff §风险与遗留](../../doc/handoffs/M2-AC1-zcode-delivery-20260928.md)：历史 handoff 原文**不改写**（当时事实的忠实记录）；闭环指针以本 Task/Handoff + STATUS 记录为准。
- `src/bootstrap/acceptance_bridge.py:338-340` docstring 仍写「the region-less detect→backfill chain has a known production planner gap」、`experiments/M2-TA3-A/run_smoke.py:273` 注释「ocr hits the known gap」——两处现存**过时注释**（生产代码/既有实验资产，本 Task 禁改），登记为 cosmetic 遗留候选（后者与 M2-TA3-A L-7 同域）：建议随未来触碰相应文件的 Task 顺手更新，或以最小 docs 修正 Task 处置；不阻塞。
- **L-1 闭合落地位置（F-007）**：M2-TA3-A.md 正文修改不在本 Task 范围——L-1 的「已核实闭合」以本 Task/Handoff + STATUS 集成收口行为准（集成时由代行 Codex 在 STATUS与本 Task 集成记录写实「M2-TA3-A L-1 = 已核实关闭，见本 Task」）；源文档 `M2-TA3-A.md:54/:119` 维持旧口径不改写，由本登记覆盖其效力。
- **无需新修复 Task**（缺陷已修）。

## 提交链（branch `agent/zcode/DIAG-M2-LOCK-CHANGED-REPRO-002`，worktree `G:/CODEX/New Manga.worktrees/DIAG-LOCK-CHANGED-REPRO-002-zcode`）

| commit | 内容 |
|---|---|
| `6cbeafe0` | claim：Task `ready → in_progress`（Owner 认领） |
| `18975a7a` | r1 实验 + S1/S2 运行证据（v3 脚本，5 文件） |
| `57a83485` | r1 Task 回填 + 本 Handoff 首版 |
| `8d2162c1` | r2 返修：v5 脚本（F-003/F-004/F-002 探针/F-010）+ v5 重跑证据 + F-001/F-005/F-006 证据 + DSH r1 报告归档（9 文件） |
| `145b3ed5` | r2 Handoff/Task 回填（F-001..F-010 闭合映射） |
| `fb36d21f` | generated diff log whitespace-only 规范化（文件内披露）；Owner 文档/证据终 tip |
| `2c13530b` | DSH r2 报告原字节归档（Owner branch 尾 commit） |

变更路径（`d69a3e1c..2c13530b`，全部落允许清单；`src/**`、`apps/**`、`tests/**`、`doc/contracts/**` 零命中——范围证据：r1 区间 [ac5-scope-proof.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/ac5-scope-proof.log)（覆盖至 57a83485）、集成 tip 全区间 [ac5-scope-proof-r2.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/ac5-scope-proof-r2.log)（DSH r2 N-1 闭合，标注集成方产物）：Task 文件、`experiments/DIAG-M2-LOCK-CHANGED-REPRO-002/repro_two_phase.py`、`verification/DIAG-M2-LOCK-CHANGED-REPRO-002/**`、`doc/handoffs/DIAG-M2-LOCK-CHANGED-REPRO-002-*.md`、`doc/reviews/DIAG-M2-LOCK-CHANGED-REPRO-002-*`（r1 报告归档）。

## AC 对照

| AC | 结果 | 证据 |
|---|---|---|
| AC1 主判定 S1 | **满足**（v5）：verdict=`NOT_REPRODUCED`（正向合取：ocr completed+`target_id==region_id`+refs 含 region+run1 COMPLETED 9 步；缺任一即 `INCONCLUSIVE` EXIT=1，DSH r1 F-003 闭合），EXIT=0 | [s1-head-run.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s1-head-run.log)、[s1-head-verdict.json](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s1-head-verdict.json) |
| AC2 先红反证 S2 | **满足**（v5）：verdict=`REPRODUCED`，EXIT=0；§3 预测四项全对齐——三特征（`target_id_is_page_id=True`、`region_key_in_input_refs=False`、`error_detail_has_expected_none=True`）+ 零写取证（run1 后 `region_revisions_count=1`，DSH r1 F-004 闭合） | [s2-prefix-run.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s2-prefix-run.log)、[s2-prefix-verdict.json](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s2-prefix-verdict.json) |
| AC3 时序自愈 S3 | **满足**（v5）：S2 轮 Run4 `retry_failed_targets` 探针（先于 region 链）重规划后真实执行 region 级链 8 步 COMPLETED（自愈实证，DSH r1 F-002 闭合）；Run3 幂等零新步骤（语义如实） | 同上两份 run.log（run4/run2/run3 行） |
| AC4 结论登记 | **满足**：四选一落定（含推断限定词，F-009 同步）+ 归因 diff 证据（F-001 闭合）+ 处置建议与落地位置（F-007） | 本文件 §交付结果 + [f001-attribution-diff.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/f001-attribution-diff.log) |
| AC5 范围与证据纪律 | **满足**：`git diff --check` 两 range EXIT=0；禁改零命中；provenance 锚定（F-005 闭合：v5 sha256=`d71825ff…`，S1/S2 副本同哈希）；范围原始日志（F-006 闭合） | [ac5-scope-proof.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/ac5-scope-proof.log)、[00-provenance.txt](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/00-provenance.txt) |

## 实际测试命令与结果

环境：Git Bash (win32)；解释器 `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 + PySide6 6.11.2，QT offscreen）。

| 轮次 | 命令 | 结果 | EXIT |
|---|---|---|---|
| S1 终版（v5） | `repro_two_phase.py --label s1-head --expect not-reproduced --out …/s1-head-verdict.json` | `NOT_REPRODUCED`（正向合取）；run1 COMPLETED（9 步）、run2 COMPLETED、run3 COMPLETED(0 步)、run4 SKIPPED | 0 |
| S2 终版（v5，临时 worktree @`d268a170`） | 同上 `--label s2-prefix-d268a170 --expect reproduced` | `REPRODUCED`；run1 COMPLETED_WITH_FAILURES（ocr failed LOCK_CHANGED+零写 revisions=1）、**run4 retry 驱动 region 链 8 步 COMPLETED**、run2 COMPLETED、run3 COMPLETED(0 步) | 0 |
| 归因（F-001） | `git diff --name-status d268a170..57a83485 -- src/` + service.py 专项 diff | src 恰 3 文件、本链相关唯一=重绑 | 0 |
| 范围自查（F-006） | `git diff --check`（两 range）+ name-status + 禁改 grep | 空/全允许/零命中 | 0 |

**迭代披露（v1–v4 无原始留存，如实；全轨迹见 [00-provenance.txt](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/00-provenance.txt)）**：

- v1：harness 未设 provider binding → run1 ocr `PROVIDER_NOT_CONFIGURED` fail-closed。发现 binding 是 harness 侧装配步骤（`acceptance_bridge.method_run_pipeline` 与 M2-TA3-A `MOCK_BINDINGS` 两个先例均显式绑定），补齐。该轮顺带实证：registry 注册不足以解析 provider，持久化 binding 缺失时 fail-closed 正确。
- v2：verdict 判定大小写 bug（DB 存小写 `"failed"`，判定比较 `"FAILED"`）→ S2 首轮 verdict JSON 误标 `NOT_REPRODUCED`/EXIT=1（当轮日志已捕获 `ocr failed LOCK_CHANGED`）；修正为大小写规范化 + 补 AC2 三特征取证字段。
- v3：首个完整入库轮（S1 `NOT_REPRODUCED` / S2 `REPRODUCED`，与终版同判）；其日志/JSON 后被 v5 覆盖。
- v4（DSH r1 条件轮）：+`INCONCLUSIVE` 正向合取（F-003）、+零写取证（F-004）、+Run4 retry 探针——但 Run4 排在 Run2 之后，region 链已被 Run2 完成，retry 只余 0 步幂等；v5 修正。
- v5（终版，sha256=`d71825ff44388aac2a6e05821a633c9c1fa3566dee81f33c57a0ed96d42ecaa9`，S1/S2 副本实测同哈希）：Run4 前置至 region 链之前；S2 轮 retry 真实驱动 region 级链 8 步全执行后 COMPLETED。入库的 S1/S2 日志+verdict JSON 均为 v5 产出。

## Review 轨迹

- **DSH r1**（非作者静态，沙箱无法执行命令）：[approved_with_conditions](../../doc/reviews/DIAG-M2-LOCK-CHANGED-REPRO-002-57a83485-dsh-r1.md)（0×P0/P1、3×P2、4×P3、3×P4；报告原字节 import，SHA256=`8091fb05…9223f7`；被审 head=`57a83485`）。条件 F-001~F-010 已在 v5 返修轮全数闭合（映射见 Task §交付与运行记录 r2 行）。

## 未跑项（如实）

- 真 docTR × 修复前锚点（`d268a170`）组合：未测（当时无 docTR 运行证据；非本 Task 判定必需，见结论 §2）。
- 全仓回归套件（cargo/pytest/vitest）：未跑——本 Task 零产品代码/测试改动（`src/**`、`tests/**` 零命中），无回归面；集成方按惯例做最小复跑即可。
- scratch DB 未入库（Temp 临时目录，无取证价值；verdict JSON 已含全部取证字段）。

## 风险与遗留

- `acceptance_bridge.py:338-340` 过时注释（见处置建议 §3）——遗留候选，不阻塞。
- offscreen 环境 `QFontDatabase` 字体目录警告（与 M2-TA3-A L-5 同源噪音；render 步骤 completed，判定不受影响）。
- S2 锚点 `d268a170` 的 schema 与 HEAD 一致性未单独审计（脚本直查 `step_runs` 通用列成功运行，间接实证兼容）。

## 启动/复现方式

```bash
cd "G:/CODEX/New Manga.worktrees/DIAG-LOCK-CHANGED-REPRO-002-zcode"
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" \
  experiments/DIAG-M2-LOCK-CHANGED-REPRO-002/repro_two_phase.py \
  --label s1-head --expect not-reproduced \
  --out verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s1-head-verdict.json
# EXIT=0 = HEAD 上缺口不复现（修复在位）
# S2 先红反证：git worktree add --detach <tmp> d268a170 后复制脚本同相对路径运行 --expect reproduced
```

## 下一接收者

DeepSeek Harness（非作者静态 Review，固定 base=`b9fc9770`、reviewed head=本分支 tip）→ 代行 Codex 集成（复跑 S1+S2 终版命令 + 范围自查 + L-1/STATUS 回填）。

## 可直接转发给 Reviewer 的指令

```
致 DeepSeek Harness（非作者 Reviewer）：对 DIAG-M2-LOCK-CHANGED-REPRO-002 交付执行独立静态 Review。
仓库 G:/CODEX/New Manga，branch agent/zcode/DIAG-M2-LOCK-CHANGED-REPRO-002，worktree
G:/CODEX/New Manga.worktrees/DIAG-LOCK-CHANGED-REPRO-002-zcode，固定 base=b9fc9770（release d69a3e1c），
被审 head=分支 tip（claim 6cbeafe0 → 实验+证据 18975a7a → 本 Handoff）。
任务文件 doc/tasks/DIAG-M2-LOCK-CHANGED-REPRO-002.md；Owner Handoff
doc/handoffs/DIAG-M2-LOCK-CHANGED-REPRO-002-zcode-delivery-20260930.md；证据
verification/DIAG-M2-LOCK-CHANGED-REPRO-002/**（S1/S2 run.log+verdict.json，shell 头+EXIT 尾）。
重点复核：(1) 结论四选一判定是否被证据支撑——S1 NOT_REPRODUCED/EXIT=0（@head）与 S2 REPRODUCED/EXIT=0
（@d268a170 修复前锚点）的判别矩阵，及 S2 诊断三特征（target_id==page_id / input_refs 无 region 键 /
expected None）与 DIAG-M2-REGIONLESS-LOCK-CHANGED-001 §3 预测逐项一致；(2) verdict JSON 与 run.log
逐字段一致；(3) 范围审计——d69a3e1c..tip 仅 6 允许路径、src/** 零命中；(4) 脚本判定逻辑有无
虚判风险（REPRODUCED 判据=run1 ocr failed+LOCK_CHANGED）；(5) 处置建议（L-1 闭合、handoff 不改写、
acceptance_bridge docstring 过时注释遗留候选）是否恰当。沙箱受限可静态 Review。报告按 REVIEW 模板落
doc/reviews/，结论 approved / changes_requested + 逐条 P0-P4。
```
