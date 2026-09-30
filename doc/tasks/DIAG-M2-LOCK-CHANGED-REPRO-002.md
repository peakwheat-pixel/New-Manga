---
id: DIAG-M2-LOCK-CHANGED-REPRO-002
title: M2-AC1 登记的 regionless LOCK_CHANGED 缺口——mock detect 两段式复现核实（M2-TA3-A L-1）
kind: diagnosis
status: done
approval: integrated
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness (non-author)
integrator: Codex（2026-09-28 起由 ZCode 代行，用户全权授权）
depends_on: [M2-TA3-A]
base_commit: b9fc977017f101a9731d4cb4bf5d270cc6f65d62
branch: agent/zcode/DIAG-M2-LOCK-CHANGED-REPRO-002
worktree: G:/CODEX/New Manga.worktrees/DIAG-LOCK-CHANGED-REPRO-002-zcode
integration_commit: null
delivery_head: 2c13530b (Owner branch tip, r2 review import; implementation+evidence=8d2162c1)
integration_commit: 1faf6c1b
---

# DIAG-M2-LOCK-CHANGED-REPRO-002：regionless LOCK_CHANGED 缺口 mock detect 两段式复现核实

## 来源与目标

**登记来源（被核实对象）**：

1. [M2-AC1 handoff §风险与遗留](../handoffs/M2-AC1-zcode-delivery-20260928.md)（2026-09-28 11:06，`aaf21a13`）：
   「regionless 页面的 detect→backfill→ocr 链在当前生产 planner 下以 `LOCK_CHANGED` 失败（ocr input_refs 冻结自 page target 快照）。本闭环按 planner 设计改走 region-level 链（seed 时经生产 `RegionEditingService` 预置 Region）……该缺口建议另行登记诊断/修复 Task。」
2. [M2-TA3-A](M2-TA3-A.md) L-1（2026-09-30 集成 `5dc69d16`）：真 docTR detect 下 5 case（Run1 `TRANSLATE_ALL` 页级链 regionless 自动前插 detect）**全部未复现**——「需缺陷 Task 以 mock detect 复现核实（或修正该登记的条件描述）」。

**起草时已核实的仓库事实（Task 起草证据，非运行结论）**：

- 时间线：M2-AC1 handoff 登记（09-28 11:06）时缺陷未修；静态诊断 [DIAG-M2-REGIONLESS-LOCK-CHANGED-001](DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md) 定位根因（`_backfill_detected_regions` 只重绑 `region_id` 未重绑 `target_id` ⇒ ocr `input_refs` 冻结自 Page ⇒ `RegionStepWriter._persist` 以 `None` 比对 Region current revision ⇒ `LockBlocked(LOCK_CHANGED)`）；修复 Task [M2-P1](M2-P1.md) 于 2026-09-28 16:27 集成（merge `a174fb9c`）。
- M2-TA3-A（09-30）运行于**修复后** main——「未复现」的候选解释是修复已落地，而非「mock-detect 特有」；但该解释未经 mock detect 路径实证，L-1 因此保留。
- 生产 planner 前插条件实测（`src/application/tasks/service.py` `_plan_region`）：页面无 Region 且命令链含 `ocr`（如 `TRANSLATE_ALL`）⇒ steps 前插 `detect`，`PlanUnit(target_id=page_id, region_id=None)`。
- mock detect 注册路径（任务指定）：`assemble_core_services(mock_local_providers=True)`（正式消费者=`bootstrap.acceptance_bridge.assemble_acceptance_core`），detector=`MockLocalDetectionProvider`（固定 inset 1/8 几何单候选）；ocr/translate 同 registry 三件套。
- M2-AC1 released 验收 loop **从未执行 detect**（seed 预置 Region，`mock_local.py` docstring DSH r1 F-007 明示）——「mock detect 实际执行 + regionless backfill 链」在当前 HEAD 上没有任何既有运行证据，本 Task 补该空白。

**目标（一个可观察的交付结果）**：以 mock detect 构造与 M2-TA3-A 相同的两段式场景（Run1=`TRANSLATE_ALL` 页级链 regionless 自动前插 detect；Run2=`RETRANSLATE_REGION_FULL` region 级链），在修复前/后两个锚点上判定该登记缺口的归属（mock-detect 特有 / 时序条件性 / 已由 M2-P1 修复登记过时 / 登记有误），产出结论与最小复现（或撤销/修正登记的建议）。**缺陷确认后修复另行释放，本 Task 不改任何生产代码。**

## Acceptance Criteria

- [x] **AC1（主判定 S1）**：实验脚本（`experiments/DIAG-M2-LOCK-CHANGED-REPRO-002/repro_two_phase.py`，零 `src/**` 改动）在当前 HEAD 用 `mock_local_providers=True` 注册路径装配生产栈，regionless fixture 页跑两段式：Run1 `TRANSLATE_ALL`（PAGE_SELECTION）+ Run2 `RETRANSLATE_REGION_FULL`（REGION，逐 Region）。逐字段记录 run 状态、`step_runs`、ocr StepRun 的 `target_id`/`region_id`/`input_refs`，机器可读 verdict 落盘。**结果：verdict=`NOT_REPRODUCED` EXIT=0；Run1 全链 9 步 COMPLETED；ocr `target_id==region_id`、`input_refs_keys=["region"]`。** 证据：[s1-head-run.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s1-head-run.log)、[s1-head-verdict.json](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s1-head-verdict.json)。
- [x] **AC2（先红反证 S2）**：同一脚本在修复前锚点 `d268a170` 上跑，**实际 `REPRODUCED`（预期达成）**：ocr `FAILED` + `error_code=LOCK_CHANGED`，诊断 §3 预测四项中三项特征齐备（`target_id_is_page_id=True`、`region_key_in_input_refs=False`、`error_detail_has_expected_none=True`）且第 4 项零写取证达成（run1 后 `region_revisions_count=1`）。证据：[s2-prefix-run.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s2-prefix-run.log)、[s2-prefix-verdict.json](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s2-prefix-verdict.json)。
- [x] **AC3（时序自愈 S3）**：S2 轮 run1 失败后 **Run4 `retry_failed_targets` 探针**（v5 起，置于 region 级链之前）真实驱动 region 级链 8 步（ocr→…→render）全执行后 `COMPLETED`——「首跑失败、重试成功」用户症状机理直接实证；Run2（RETRANSLATE_REGION_FULL，强制重跑语义）亦 8 步 COMPLETED；两轮 Run3（同命令 TRANSLATE_ALL 重规划）`COMPLETED` 零新 step_runs（既有完成态幂等语义，如实记录）。
- [x] **AC4（结论登记）**：结论=**登记缺口真实存在过、已由 M2-P1 修复（`a174fb9c`）、机制上非 mock-detect 特有（真 docTR 在修复前是否同样触发属推断，未实测）、非「未修」时序条件性**；M2-TA3-A 未复现根因=其运行于修复后 main。归因证据（DSH r1 F-001）：`d268a170..57a83485` 区间 `src/` 变更恰 3 文件，其中与本链写守卫路径相关的行为变化唯一= `service.py` 的 M2-P1 重绑（[f001-attribution-diff.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/f001-attribution-diff.log)）。处置建议：M2-TA3-A L-1 闭为已核实；M2-AC1 handoff 原文不改写（历史忠实记录）；`acceptance_bridge.py:338-340` 过时 docstring 与 `run_smoke.py:273` 过时注释登记遗留候选（维持不改、引用本 Task 结论）；无需新修复 Task。详见 [Handoff §交付结果](../handoffs/DIAG-M2-LOCK-CHANGED-REPRO-002-zcode-delivery-20260930.md)。
- [x] **AC5（范围与证据纪律）**：`git diff --check` 两 range 均 EXIT=0；禁改路径零命中；日志均带 shell 头+EXIT 尾。范围证据：[ac5-scope-proof.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/ac5-scope-proof.log)。**base 口径（F-008）**：`b9fc9770`=释放时 main 锚点（frontmatter base_commit）；`d69a3e1c`=release commit（worktree 检出点，范围 diff 起点）；`d268a170`=仅 S2 使用的修复前锚点。

## 允许修改范围

- `experiments/DIAG-M2-LOCK-CHANGED-REPRO-002/**`（新增实验脚本）
- `verification/DIAG-M2-LOCK-CHANGED-REPRO-002/**`（证据日志、S2 锚点运行记录）
- `doc/tasks/DIAG-M2-LOCK-CHANGED-REPRO-002.md`（本文件）
- `doc/handoffs/DIAG-M2-LOCK-CHANGED-REPRO-002-*.md`
- `doc/reviews/DIAG-M2-LOCK-CHANGED-REPRO-002-*`（Reviewer 报告）
- 元数据导航面（`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/tasks/README.md`）按协议 §3.6 仅状态与链接回填

## 禁止范围

- `src/**`、`apps/**`、`tests/**`、`doc/contracts/**`、`requirements*.txt`——零改动（缺陷确认后修复另行释放）
- `experiments/M2-TA3-A/**` 等既有实验资产——只读引用
- 两处被核实登记（M2-AC1 handoff、M2-TA3-A Task 文件）的**正文修改**不在本 Task 范围——处置建议落本 Task/Handoff，登记修订由 Codex 在集成收口时按协议以最小文档修正落实或另行释放
- 用户真实漫画库、共享 app.db、任何仓库外路径

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| S1 主判定（AC1） | `python experiments/DIAG-M2-LOCK-CHANGED-REPRO-002/repro_two_phase.py --label s1-head --expect not-reproduced --out …/s1-head-verdict.json` | TASK-012-py312 venv（Py3.12.3+PySide6 6.11.2 offscreen）；HEAD worktree | **executed（v5 终版）**：verdict=`NOT_REPRODUCED`（正向合取断言全满足），Run1 全链 COMPLETED、Run2 COMPLETED、Run3 COMPLETED(0 步)、Run4 SKIPPED | [s1-head-run.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s1-head-run.log)、[s1-head-verdict.json](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s1-head-verdict.json) |
| S2 先红反证（AC2） | 临时 worktree @`d268a170` + 同脚本 `--expect reproduced` | 同 venv；修复前锚点 | **executed（v5 终版）**：verdict=`REPRODUCED`，run1 ocr `failed LOCK_CHANGED` 三特征+零写（revisions=1）齐备 | [s2-prefix-run.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s2-prefix-run.log)、[s2-prefix-verdict.json](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/s2-prefix-verdict.json) |
| S3 重规划时序（AC3） | 同脚本内置 Run2/Run3/Run4 | 同 S1/S2 | **executed（v5 终版）**：S2 轮 Run4 retry 探针驱动 region 级链 8 步 COMPLETED（自愈实证）；两轮 Run3 COMPLETED 零新 step_runs（幂等语义） | 同上两份 run.log |
| 归因（F-001） | `git diff --name-status d268a170..57a83485 -- src/` + service.py 专项 diff | — | **executed**：src 变更恰 3 文件、本链相关行为变化唯一=M2-P1 重绑 | [f001-attribution-diff.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/f001-attribution-diff.log) |
| 范围/whitespace（AC5） | `git diff --check`（两 range）+ name-status + 禁改 grep | — | **executed**：全部 EXIT=0/零命中 | [ac5-scope-proof.log](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/ac5-scope-proof.log) |

测试迭代披露：v1（无 provider binding → `PROVIDER_NOT_CONFIGURED`，补 binding）与 v2（verdict 大小写 bug）的原始日志已被覆盖、仅文字披露；v3=首个完整入库轮；v4（DSH r1 条件轮：+INCONCLUSIVE 正向合取/+零写取证/+Run4 探针，Run4 排序在 Run2 后致 retry 只余幂等）；v5（终版）=Run4 前置，S2 轮 retry 真实驱动 region 链 8 步。全轨迹见 [00-provenance.txt](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/raw/00-provenance.txt)（v5 sha256=`d71825ff…`，S1/S2 副本同哈希）。

## 依赖、风险与阻塞

- depends_on：`M2-TA3-A`（done @`5dc69d16`——L-1 登记来源）；`M2-P1`（done @`a174fb9c`——修复本体，S2 锚点选择依据）。
- 风险 1：S2 反证不红（如 `d268a170` 与 HEAD 的装配面漂移导致脚本不可运行）→ 按 AC2 降级路径如实登记，不虚构归因。
- 风险 2：mock detect 三件套的 ocr/translate provider 解析依赖 registry 唯一性/绑定，若 HEAD 装配在 regionless+detect 执行路径上有未接线行为（该路径无既有运行证据），S1 可能出现 `PROVIDER_*` 类 fail-closed——这本身就是有效证据，如实记录并归因（environment/defect）。
- 风险 3：跨 commit DB 复用（S2 失败 DB → HEAD 重规划）存在 schema 漂移风险——**不做**跨 commit DB 复用；S3 在 S1 同 commit 同 DB 内完成。
- 无用户裁决依赖；无外部资源依赖。

## 交付与运行记录

- **2026-09-30 release（代行 Codex）**：`proposed → ready / DIAG_M2_LOCK_CHANGED_REPRO_002_RELEASED`。起草（含登记来源、时间线核实、S1/S2/S3 实验矩阵冻结）与释放同批完成（用户指令授权新建本缺陷核实 Task 并全链交付）。冻结：base=`b9fc977017f101a9731d4cb4bf5d270cc6f65d62`、branch=`agent/zcode/DIAG-M2-LOCK-CHANGED-REPRO-002`、worktree=`G:/CODEX/New Manga.worktrees/DIAG-LOCK-CHANGED-REPRO-002-zcode`。Release evidence：[release-b9fc9770](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/release-b9fc9770.md)。
- **2026-09-30 交付（Owner=ZCode，head=`18975a7a`）**：`in_progress → in_review`。S1（HEAD）`NOT_REPRODUCED` EXIT=0 + S2（`d268a170` 修复前）`REPRODUCED` EXIT=0 判别矩阵闭合；结论=**缺口真实存在过、已由 M2-P1 修复（`a174fb9c`）、机制上非 mock-detect 特有、非未修时序条件性**（M2-TA3-A 未复现根因=修复后 main）。处置建议：L-1 闭为已核实；M2-AC1 handoff 原文不改写；`acceptance_bridge.py:338-340` 过时 docstring 为遗留候选；无需新修复 Task。Handoff：[DIAG-M2-LOCK-CHANGED-REPRO-002-zcode-delivery-20260930](../handoffs/DIAG-M2-LOCK-CHANGED-REPRO-002-zcode-delivery-20260930.md)。
- **2026-09-30 DSH r1 Review**：[approved_with_conditions](../../doc/reviews/DIAG-M2-LOCK-CHANGED-REPRO-002-57a83485-dsh-r1.md)（0×P0/P1、3×P2、4×P3、3×P4；纯静态——沙箱无法执行命令）。条件：F-001 归因 diff 证据、F-002 自愈探针/措辞、F-003 verdict fail-open、F-004~F-007 证据补齐。
- **2026-09-30 Owner 返修（r2，v5 终版）**：F-001 归因改写+[f001-attribution-diff.log]（src 变更恰 3 文件、本链相关唯一=重绑）；F-002 Run4 `retry_failed_targets` 探针前置实证（S2 轮 retry 驱动 region 链 8 步 COMPLETED）；F-003 `NOT_REPRODUCED` 升级为正向合取+`INCONCLUSIVE` fail-closed；F-004 零写取证（S2 revisions=1）；F-005 [00-provenance.txt]（v5 sha256=`d71825ff…`）；F-006 [ac5-scope-proof.log]；F-007 落地位置写实（本行+集成记录）；F-008 base 双 hash 口径注明；F-009 AC4 限定词；F-010 归一化。v5 重跑：S1 `NOT_REPRODUCED` EXIT=0、S2 `REPRODUCED` EXIT=0，判别矩阵不变、结论不变。
- Review：r1 [approved_with_conditions](../../doc/reviews/DIAG-M2-LOCK-CHANGED-REPRO-002-57a83485-dsh-r1.md) → r2 返修 → r2 [approved_with_conditions](../../doc/reviews/DIAG-M2-LOCK-CHANGED-REPRO-002-fb36d21f-dsh-r2.md)（0×P0/P1/P2 新发现，准予集成）。
- **2026-09-30 集成（代行 Codex）**：merge=`1faf6c1b`（parents `d69a3e1c`+`2c13530b`，无冲突，12 文件全允许路径）+ 集成修正 `56edc335`（DSH r2 N-1 范围自查 at tip、N-2 delivery_head/提交链、N-3 死链、N-4 归因注；均标注集成方修正）。集成复跑：S1 `NOT_REPRODUCED` EXIT=0（tip 绑定）、S2 `REPRODUCED` EXIT=0（锚点 `d268a170`，run4 retry 自愈复现）、diff --check EXIT=0。**Task `done` @integration `1faf6c1b`（收口 `56edc335`）；M2-TA3-A L-1 = 已核实关闭**。记录：[integration-56edc335](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/integration-56edc335/integration.md)。
- 实际测试：见上方测试表（S1/S2/S3/归因/范围自查全 executed）。
- 后续实际记录包含日期、commit、环境、结果、遗留项；最终由 Codex 填写 integration_commit 并改 done。
