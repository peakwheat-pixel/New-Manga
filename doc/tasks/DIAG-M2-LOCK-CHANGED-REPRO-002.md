---
id: DIAG-M2-LOCK-CHANGED-REPRO-002
title: M2-AC1 登记的 regionless LOCK_CHANGED 缺口——mock detect 两段式复现核实（M2-TA3-A L-1）
kind: diagnosis
status: ready
approval: released_by_codex_proxy
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness (non-author)
integrator: Codex（2026-09-28 起由 ZCode 代行，用户全权授权）
depends_on: [M2-TA3-A]
base_commit: b9fc977017f101a9731d4cb4bf5d270cc6f65d62
branch: agent/zcode/DIAG-M2-LOCK-CHANGED-REPRO-002
worktree: G:/CODEX/New Manga.worktrees/DIAG-LOCK-CHANGED-REPRO-002-zcode
integration_commit: null
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

- [ ] **AC1（主判定 S1）**：实验脚本（`experiments/DIAG-M2-LOCK-CHANGED-REPRO-002/repro_two_phase.py`，零 `src/**` 改动）在当前 HEAD 用 `mock_local_providers=True` 注册路径装配生产栈，regionless fixture 页跑两段式：Run1 `TRANSLATE_ALL`（PAGE_SELECTION）+ Run2 `RETRANSLATE_REGION_FULL`（REGION，逐 Region）。逐字段记录 run 状态、`step_runs`（step_type/status/error_code/error_detail）、ocr StepRun 的 `target_id`/`region_id`/`input_refs`，机器可读 verdict（`REPRODUCED`/`NOT_REPRODUCED`）落盘。
- [ ] **AC2（先红反证 S2）**：同一脚本在修复前锚点 `d268a170`（M2-P1 merge `a174fb9c` 的 main 侧 parent）上跑 Run1 部分，**预期 `REPRODUCED`**：ocr StepRun `FAILED` + `error_code=LOCK_CHANGED`，且诊断报告三特征齐备（`target_id==page_id`、`input_refs` 无 `"region"` 键、`error_detail` 含 `expected None`）。若不红，则实验判别力不足，结论按「反证未达成」降级并如实登记（不得强行归因）。
- [ ] **AC3（时序自愈 S3）**：S1 同一 DB 上，Page 已有 Region 后再次创建 `TRANSLATE_ALL` run（重规划走 region 级链）并执行，记录其状态（预期 `completed`），作为「重规划/重试路径无缺口」的最小时序证据。
- [ ] **AC4（结论登记）**：按 S1/S2/S3 证据在 Task+Handoff 落四选一结论，并给出对两处登记的处置建议（撤销 / 标注已修复 / 维持）；若 REPRODUCED 则附最小复现步骤与触发条件描述。结论如实，**允许「登记有误/已过时」这一结论**。
- [ ] **AC5（范围与证据纪律）**：`git diff --check` EXIT=0；Owner delta 全部落在允许路径；所有运行日志带 shell 头+EXIT 尾入库 `verification/DIAG-M2-LOCK-CHANGED-REPRO-002/`。

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
| S1 主判定（AC1） | `python experiments/DIAG-M2-LOCK-CHANGED-REPRO-002/repro_two_phase.py --scenario s1`（planned） | TASK-012-py312 venv（Py3.12.3+PySide6 6.11.2 offscreen）；HEAD worktree | NOT_RUN | 无 |
| S2 先红反证（AC2） | 临时 worktree @`d268a170` + 同脚本 `--scenario s1`（Run1 判定复用）（planned） | 同 venv；修复前锚点 | NOT_RUN | 无 |
| S3 重规划时序（AC3） | 同脚本 `--scenario s1` 内置 Run3（planned） | 同 S1 | NOT_RUN | 无 |
| 范围/whitespace（AC5） | `git diff --check <base>..HEAD`；`git diff --name-status <base>..HEAD`（planned） | — | NOT_RUN | 无 |

## 依赖、风险与阻塞

- depends_on：`M2-TA3-A`（done @`5dc69d16`——L-1 登记来源）；`M2-P1`（done @`a174fb9c`——修复本体，S2 锚点选择依据）。
- 风险 1：S2 反证不红（如 `d268a170` 与 HEAD 的装配面漂移导致脚本不可运行）→ 按 AC2 降级路径如实登记，不虚构归因。
- 风险 2：mock detect 三件套的 ocr/translate provider 解析依赖 registry 唯一性/绑定，若 HEAD 装配在 regionless+detect 执行路径上有未接线行为（该路径无既有运行证据），S1 可能出现 `PROVIDER_*` 类 fail-closed——这本身就是有效证据，如实记录并归因（environment/defect）。
- 风险 3：跨 commit DB 复用（S2 失败 DB → HEAD 重规划）存在 schema 漂移风险——**不做**跨 commit DB 复用；S3 在 S1 同 commit 同 DB 内完成。
- 无用户裁决依赖；无外部资源依赖。

## 交付与运行记录

- **2026-09-30 release（代行 Codex）**：`proposed → ready / DIAG_M2_LOCK_CHANGED_REPRO_002_RELEASED`。起草（含登记来源、时间线核实、S1/S2/S3 实验矩阵冻结）与释放同批完成（用户指令授权新建本缺陷核实 Task 并全链交付）。冻结：base=`b9fc977017f101a9731d4cb4bf5d270cc6f65d62`、branch=`agent/zcode/DIAG-M2-LOCK-CHANGED-REPRO-002`、worktree=`G:/CODEX/New Manga.worktrees/DIAG-LOCK-CHANGED-REPRO-002-zcode`。Release evidence：[release-b9fc9770](../../verification/DIAG-M2-LOCK-CHANGED-REPRO-002/release-b9fc9770.md)。
- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。
- 后续实际记录包含日期、commit、环境、结果、遗留项；最终由 Codex 填写 integration_commit 并改 done。
