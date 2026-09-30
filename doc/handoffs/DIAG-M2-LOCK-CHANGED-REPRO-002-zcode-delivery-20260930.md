---
task_id: DIAG-M2-LOCK-CHANGED-REPRO-002
author: ZCode (Owner)
recipient: DeepSeek Harness (non-author Review) → Codex proxy (Integrator)
base_commit: b9fc977017f101a9731d4cb4bf5d270cc6f65d62
delivery_head: 18975a7a (experiment+evidence) — 本 Handoff 以文档提交追加，引用该 head
status: delivered_awaiting_review
---

# Handoff：DIAG-M2-LOCK-CHANGED-REPRO-002 — regionless LOCK_CHANGED 缺口 mock detect 两段式复现核实

## 交付结果（结论先行）

**AC4 结论（四选一 → ③「已由 M2-P1 修复」变体，登记有误不成立）**：

1. **登记缺口真实存在过**：S2（修复前锚点 `d268a170`，M2-P1 merge `a174fb9c` 的 main 侧 parent）上，mock detect（`assemble_core_services(mock_local_providers=True)` 注册路径）两段式 Run1（`TRANSLATE_ALL` regionless 自动前插 detect）复现 `ocr FAILED error_code=LOCK_CHANGED`，且 [DIAG-M2-REGIONLESS-LOCK-CHANGED-001](../research/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md) 诊断三特征逐项齐备：`target_id == page_id`、`input_refs` 无 `"region"` 键、`error_detail` 含 `expected None`。**M2-AC1 handoff §风险与遗留的登记在写作时点（2026-09-28 11:06，缺陷未修）属实。**
2. **非 mock-detect 特有**：S1（HEAD `6cbeafe0`）与 S2 的唯一代码差异 = M2-P1 修复（`_backfill_detected_regions` 同时重绑 `target_id`+`region_id`）；同一 harness、同一场景，修复前红/修复后绿——判别点在 planner backfill 代码，与 detect provider 实现（mock vs 真 docTR）无关。真 docTR 在修复前是否同样触发属**推断**（未实测，无当时运行证据），如实标注；但不影响「已修复」结论。
3. **已由 M2-P1 修复**：S1 在 HEAD 上 Run1 全链 9 步（detect→ocr→color→term_extract→translate→segment→mask_refine→inpaint→render）一段式 `COMPLETED`；ocr StepRun 取证 `target_id == region_id`、`input_refs_keys == ["region"]`——`PlanUnit.target_id ≡ 写目标` 不变式生效，`LOCK_CHANGED` 未复现。
4. **M2-TA3-A「未复现」的根因**：其 5 case 运行于修复后的 main（M2-P1 `a174fb9c` 先于 M2-TA3-A base），非「mock-detect 特有」、非「登记有误」。
5. **时序条件性维度（S3）**：两轮（S1/S2）Run2（`RETRANSLATE_REGION_FULL` region 级链）均 `COMPLETED`——S2 轮尤其实证「首 run 失败后重规划自愈」（DIAG-001 §4 断言独立复核，即用户症状「首跑失败重试成功」的机理）；Run3（同 DB 二次 `TRANSLATE_ALL`）`COMPLETED` 零新 step_runs（既有完成态幂等重规划语义）。该缺口从来是**单 run 内 detect→backfill→ocr 首链**条件性，跨 run 重规划路径无缺口。

**处置建议**：

- [M2-TA3-A](../../doc/tasks/M2-TA3-A.md) **L-1**：闭为「已核实——缺口真实、已由 M2-P1 修复（`a174fb9c`）、非 mock-detect 特有」，不再保留缺陷候选。
- [M2-AC1 handoff §风险与遗留](../../doc/handoffs/M2-AC1-zcode-delivery-20260928.md)：历史 handoff 原文**不改写**（当时事实的忠实记录）；闭环指针以本 Task/Handoff + STATUS 记录为准。
- `src/bootstrap/acceptance_bridge.py:338-340` docstring 仍写「the region-less detect→backfill chain has a known production planner gap」——现存**过时注释**（生产代码，本 Task 禁改 `src/**`），登记为 cosmetic 遗留候选：建议随未来触碰该文件的 Task 顺手更新，或以最小 docs 修正 Task 处置；不阻塞。
- **无需新修复 Task**（缺陷已修）。

## 提交链（branch `agent/zcode/DIAG-M2-LOCK-CHANGED-REPRO-002`，worktree `G:/CODEX/New Manga.worktrees/DIAG-LOCK-CHANGED-REPRO-002-zcode`）

| commit | 内容 |
|---|---|
| `6cbeafe0` | claim：Task `ready → in_progress`（Owner 认领） |
| `18975a7a` | 实验脚本 + S1/S2 运行证据（5 文件） |

变更路径（`d69a3e1c..18975a7a`，6 路径全落允许清单；`src/**`、`apps/**`、`tests/**`、`doc/contracts/**` 零命中）：

- `experiments/DIAG-M2-LOCK-CHANGED-REPRO-002/repro_two_phase.py`（新增，唯一实验资产）
- `verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s{1,2}-*-{run.log,verdict.json}`（4 个证据文件）
- `doc/tasks/DIAG-M2-LOCK-CHANGED-REPRO-002.md`（claim 翻转+本次回填）

## AC 对照

| AC | 结果 | 证据 |
|---|---|---|
| AC1 主判定 S1 | **满足**：verdict=`NOT_REPRODUCED`，EXIT=0；Run1 全链 COMPLETED；ocr 取证 `target_id==region_id`、`input_refs_keys=["region"]` | [s1-head-run.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s1-head-run.log)、[s1-head-verdict.json](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s1-head-verdict.json) |
| AC2 先红反证 S2 | **满足**：verdict=`REPRODUCED`，EXIT=0；诊断三特征齐备（`target_id_is_page_id=True`、`region_key_in_input_refs=False`、`error_detail_has_expected_none=True`） | [s2-prefix-run.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s2-prefix-run.log)、[s2-prefix-verdict.json](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s2-prefix-verdict.json) |
| AC3 时序自愈 S3 | **满足**：S2 轮 run1 失败后 Run2 region 级链 COMPLETED（自愈实证）；S1/S2 两轮 Run3 幂等零新步骤（语义如实记录） | 同上两份 run.log（run2/run3 行） |
| AC4 结论登记 | **满足**：四选一落定 + 处置建议（本 Handoff §交付结果 + Task §交付与运行记录） | 本文件 |
| AC5 范围与证据纪律 | **满足**：`git diff --check d69a3e1c..HEAD` EXIT=0；6 路径全允许；全部日志带 shell 头+EXIT 尾 | 本文件 + raw 日志头部/尾部 |

## 实际测试命令与结果

环境：Git Bash (win32)；解释器 `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 + PySide6 6.11.2，QT offscreen）。

| 轮次 | 命令 | 结果 | EXIT |
|---|---|---|---|
| S1 终版（v3 脚本） | `repro_two_phase.py --label s1-head --expect not-reproduced --out …/s1-head-verdict.json` | `NOT_REPRODUCED`；run1 COMPLETED（9 步）、run2 COMPLETED、run3 COMPLETED(0 步) | 0 |
| S2 终版（v3 脚本，临时 worktree @`d268a170`） | 同上 `--label s2-prefix-d268a170 --expect reproduced` | `REPRODUCED`；run1 COMPLETED_WITH_FAILURES（ocr failed LOCK_CHANGED）、run2 COMPLETED（自愈）、run3 COMPLETED(0 步) | 0 |
| 范围自查 | `git diff --check d69a3e1c..HEAD`；`git diff --name-status d69a3e1c..HEAD` | 空 / 6 路径 | 0 |

**迭代披露（v1/v2 已被 v3 覆盖，无原始日志留存）**：

- v1：harness 未设 provider binding → run1 ocr `PROVIDER_NOT_CONFIGURED` fail-closed。发现 binding 是 harness 侧装配步骤（`acceptance_bridge.method_run_pipeline` 与 M2-TA3-A `MOCK_BINDINGS` 两个先例均显式绑定），补齐。该轮顺带实证：registry 注册不足以解析 provider，持久化 binding 缺失时 fail-closed 正确。
- v2：verdict 判定大小写 bug（DB 存小写 `"failed"`，判定比较 `"FAILED"`）→ S2 首轮 verdict JSON 误标 `NOT_REPRODUCED`/EXIT=1（当轮日志已捕获 `ocr failed LOCK_CHANGED`）；修正为大小写规范化 + 补 AC2 三特征取证字段（`target_id_is_page_id` 等）。
- v3（终版，入库）：S1/S2 均一次通过。

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
