---
id: TASK-032
title: 修复 SFX Policy Gate 缺失 region_type 前置（F-1）
kind: bugfix
status: in_review
approval: approved_by_user
suggested_owner: ZCode
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-011, TASK-019]
base_commit: ca17d454edc03bc1b057e9e3fc463c81da652e53
branch: agent/deepseek/TASK-032-sfx-policy-gate-region-type
worktree: G:/CODEX/New Manga.worktrees/TASK-032-deepseek
integration_commit: null
---

# TASK-032：修复 SFX Policy Gate 缺失 region_type 前置（F-1）

**状态提示（2026-09-17）**：`status=in_review`——修复已实现并取证（delivery head `771977c`），待**非作者**（Codex）独立 Review；AC 逐条证据、判别力与越界发现见 [verification/TASK-032/author-verification.md](../../verification/TASK-032/author-verification.md) 与 [Handoff](../handoffs/TASK-032-771977c.md)。

**READY（2026-09-17 用户批准释放；同日按用户指示改派 Owner）**：Owner=`DeepSeek Harness`、Reviewer=`Codex`（**非作者**——Owner 改为 DSH 后，若仍由 DSH 审会构成同体审查，故一并更换）；base=`ca17d45`（释放时的 master HEAD，已与实际代码核对：`src/application/tasks/service.py:353-361` 的缺陷仍在，`sfx_policy` 判断未检查 `region_type`）；branch/worktree 见顶部元数据（已按 `agent/deepseek/...` 命名重建并同步；首次按 `agent/zcode/...` 创建且**无任何提交**的 worktree/分支已移除）。Owner 开始实施前，在本任务分支把 `status` 改为 `in_progress`。

**Codex 已完成意图裁决：本 Task 修的是缺陷、不是产品取舍**——依据 D06 §85「SFX Policy Gate」的前置 `region_type = sfx` 与 D08 AC-SFX-001（`region_type = sfx` 且未额外配置 → `SKIP_POLICY` / `reason = sfx_skip`）；D03 §7 的默认 `skip` **对 SFX 类型是正确的**，问题在策略泄漏到非 SFX 类型。因此**不需要产品决策**。

**Review 口径**：本 Task 的独立 Review 必须按[协作协议](../09_COLLABORATION.md) §6 的**四轴**执行——**Standards**（`code-review` 技能两轴之一，强制；含 Fowler smell baseline 作为判断项）/ **Spec**（两轴之二）/ Architecture / Verification，并逐轴声明 `executed`/`N/A`、每轴一行小结、**不跨轴排名**；两轴应优先由**独立执行者/线程并行**执行（模板见 [Review 模板](../templates/REVIEW.md)）。

## 来源与目标

- 来源：[doc/reviews/TASK-019-726baf5.md](../reviews/TASK-019-726baf5.md) 的 R-5 / F-1；[doc/STATUS.md](../STATUS.md) 的 F-1 登记行。
- **规范依据（裁决基础）**：D06 §85「SFX Policy Gate」的前置明确写着 `region_type = sfx`；D08 AC-SFX-001 同样以 `region_type = sfx` 且未额外配置为前提，返回 `SKIP_POLICY` / `reason = sfx_skip`；D03 §7 定义 SFX 策略默认 `skip`——**对 SFX 类型而言该默认是正确的**。
- **缺陷**：`src/application/tasks/service.py:353-361` 在判断 `sfx_policy in {"skip","manual"}` 时**没有检查 `region_type`**，导致普通（`speech`/`narration`/`title`/`note`/`other`）Region 的 `translate`/`segment`/`mask_refine`/`inpaint`/`render` 也被判为 `SKIP_POLICY("sfx_skip")`。
- **影响**：按真实默认值（新建 Region 为 `speech`、`sfx_policy` 默认 `skip`），整条重翻译链在**规划阶段**即被跳过；`src/ui/**` 无任何写入 `sfx_policy` 的路径，用户无从纠正。
- **附带需统一的口径**：`src/infrastructure/sqlite/pipeline.py` 的快照默认与实体/Schema 默认不一致。缺字段时的解释必须唯一：**SFX 类型** 回落文档默认 `skip`；**非 SFX 类型** 该字段不参与判定。

## Acceptance Criteria

- [x] 规划阶段仅当 `region_type == sfx` 时应用 SFX 策略：`skip`/`manual` → `SKIP_POLICY(reason="sfx_skip")`；`translate` → 按 AC-SFX-002 进入 Translation。
      → `_decide_step` 改为 `region is not None and step_type in _SFX_GATED_STEPS and _sfx_gate_suppresses(region)`；`_sfx_gate_suppresses` 只在 `region_type == "sfx"` 时委托给 Translate Step 共用的 `decide_sfx_translation`（消除同一规则两份实现的漂移）。证据：`test_sfx_region_policies_suppress_the_automatic_chain`、`test_sfx_region_translate_policy_enters_the_translation_chain`、真实 SQLite `test_real_default_sfx_policy_still_gates_an_sfx_region`。
- [x] 非 SFX 类型 Region 的 `sfx_policy` 取任意值都不影响 `translate/segment/mask_refine/inpaint/render` 的规划结果（用**真实默认值**构造用例，不用测试辅助的 `translate` 默认）。
      → `test_sfx_policy_never_gates_a_non_sfx_region`：`speech/narration/title/note/other` × `skip/manual/translate` = 15 例，全链 `{RUN}`、无 `sfx_skip`；真实 SQLite 用例插入 region 时不写 `sfx_policy`（取 Schema 默认 `skip`，`region_type='speech'`）→ 全链 `{RUN}`。
- [x] 缺字段口径唯一：SFX 类型回落 `skip`；非 SFX 类型不参与判定；`infrastructure/sqlite/pipeline.py` 的快照默认与实体/Schema 一致。
      → `_effective_sfx_policy` 对缺失/空白回落 `SfxPolicy.SKIP.value`；`sqlite/pipeline.py::_region()` 缺省由 `"translate"` 改为 `SfxPolicy.SKIP.value`。实测三方默认（实体/Schema/反序列化）= `skip`（[`schema-defaults.txt`](../../verification/TASK-032/schema-defaults.txt)）。**残留**：`src/domain/tasks/models.py:182` 字段级默认仍为 `translate`（越界，见取证 §4 N-2）。
- [x] 回归：`tests/pipeline` 新增"真实默认值"用例（新建 `speech` Region + 默认 `sfx_policy` → 各步骤不被 `SKIP_POLICY` 跳过）；既有 `sfx` 用例（`tests/pipeline/test_pipeline.py` 中 `region_type="sfx", sfx_policy="skip"`）行为不变。
      → 新增 30 例（`tests/pipeline` 30 → 60 passed）；既有 `test_planner_marks_lock_sfx_and_provider_decisions_separately` 未改动且通过；判别力：修前 `src/` + 新用例 → **17 failed / 43 passed**。
- [x] 交付 Handoff、实际测试/审阅记录与未完成项，经**非作者**独立 Review 与 Codex 集成验证后才能 done。
      → Handoff：[TASK-032-771977c](../handoffs/TASK-032-771977c.md)；取证：[verification/TASK-032/](../../verification/TASK-032/author-verification.md)。**Review 与集成尚未执行**，本 Task 不自行标记 `approved`/`done`。

## 允许修改范围

- `src/application/tasks/service.py`
- `src/infrastructure/sqlite/pipeline.py`
- `tests/pipeline/**`
- `doc/tasks/TASK-032.md`、`doc/handoffs/TASK-032-*.md`、`verification/TASK-032/**`

Codex 已按 base `ca17d45` 的实际结构核对：三个代码/测试允许路径（`src/application/tasks/service.py`、`src/infrastructure/sqlite/pipeline.py`、`tests/pipeline/**`）均存在。超出范围（Schema/migration、D03/D08 文本、`src/ui/**`、`src/domain/**`、其他 Task）先由 Codex 明确范围变更。本 Task **预计不需要 Schema 变更**（`skip` 默认本身正确）。

## 禁止范围

- 不得修改 Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、生产数据、其他 Task。
- 不得在未获用户批准时改变 `sfx_policy` 的**默认值语义**（D03 §7 已定 `skip`）；若认为需要改变，先取得用户裁决。
- 不得放宽既有测试、删除既有断言或新增 skip 掩盖失败。
- 不得顺手修复 `tests/reading_export` 的 flaky（见 STATUS「已知 flaky 测试（跟踪条目）」；属测试基础设施，另行处理）。

## 测试要求

- 主套件：`python -m pytest tests/pipeline -q`，必须包含"真实默认值"用例与既有 `sfx` 类型用例。
- 回归：`python -m pytest tests/core tests/storage tests/providers -q` 与全仓 `python -m pytest -q`；记录中**分列 passed/skipped 与 skip 原因**。
- 实际记录包含 commit、OS/依赖、准确命令、退出码、结果与证据路径。

## 依赖、风险与阻塞

硬依赖：[TASK-011](TASK-011.md)（planner 归属）、[TASK-019](TASK-019.md)（缺陷发现与 F-1 登记）——均已集成 `done`。

阻塞：**已解除**——2026-09-17 用户批准释放（`approval=approved_by_user`）并改派 Owner；实现已完成，当前 `status=in_review` 待非作者 Review。本 Task 无未解除阻塞；越界项（渲染层同类缺陷 N-1、`RegionSnapshot` 字段默认 N-2）已登记为后续切片/Codex 裁决，不影响本次规划层修复的完成判定。

## 交付与运行记录

- Handoff：[TASK-032-771977c](../handoffs/TASK-032-771977c.md)（delivery_head=`771977c`）。
- Review：尚无（待 Codex 非作者独立 Review，按协作协议 §6 四轴：Standards / Spec / Architecture / Verification）。
- 实际执行/测试：
  - 取证总表：[verification/TASK-032/author-verification.md](../../verification/TASK-032/author-verification.md)；默认值三方实测：[schema-defaults.txt](../../verification/TASK-032/schema-defaults.txt)；日志：[pytest-pipeline.log](../../verification/TASK-032/pytest-pipeline.log)、[pytest-regression.log](../../verification/TASK-032/pytest-regression.log)、[pytest-full.log](../../verification/TASK-032/pytest-full.log)、[discriminative-prefix.log](../../verification/TASK-032/discriminative-prefix.log)；路径核对：[changed-paths.txt](../../verification/TASK-032/changed-paths.txt)。
  - 命令与结果（`TASK-012-py312`，Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1，`PYTHONDONTWRITEBYTECODE=1`，全部 `-p no:cacheprovider`）：基线（`c004d4e` 导出树）全仓 **641 passed / 6 skipped**；`tests/pipeline` **60 passed / 0 skipped**（改动前 30 例）；`tests/core`+`tests/storage`+`tests/providers` **159 passed / 0 skipped**；全仓 **671 passed / 6 skipped**（2 次一致；6 条 skip 全为既有 `tests/network` 的 `openssl unavailable`）。判别力：修前 `src/` + 新用例 → **17 failed / 43 passed**。边界：`git diff --name-only c004d4e..HEAD` 5 个路径全在允许范围、越界 0；全范围禁止路径命中 0；`git diff --check ca17d45..HEAD` 退出码 0。
  - 既有 `tests/reading_export` 两个已登记低频 flaky **未改动、未新增 skip**，本 Task 不将其记为通过（本轮全仓 2 次运行未触发）。
- **最近状态（当前，唯一）**：2026-09-17 实现完成并置 **`in_review`**，交 Codex 非作者独立 Review（集成由 Codex 执行）。分支 `agent/deepseek/TASK-032-sfx-policy-gate-region-type`、worktree `G:/CODEX/New Manga.worktrees/TASK-032-deepseek`、fixed base `ca17d45`、delivery head `771977c`（`a5823d1` 开工文档、`771977c` 修复与用例）。**未 push、未合并 master**。越界发现登记（未修改，供 Codex/用户裁决）：**N-1** 渲染层同类缺陷 `src/application/rendering/service.py:219,238,347-351` 只按 `sfx_policy` 判定、无 `region_type` 前置，且既有 `tests/rendering/test_rerender.py:180-199/246-264/458-473` 以真实默认形态（`speech` + `skip`/`manual`）固定该行为 → 规划已修好但渲染执行仍被拦截；**N-2** `src/domain/tasks/models.py:182` 的 `RegionSnapshot.sfx_policy` 字段默认仍为 `"translate"`（生产路径已不受影响）；**N-3** 已声明的行为变化：取值域外策略在规划阶段被共享 gate 拒绝（与执行层一致，已由测试固定）。
- 历史状态（2026-09-17）：由 Codex 依据 TASK-019 的 F-1 登记创建为 `proposed`；当日获用户批准释放为 `ready`（首版 Owner=`ZCode`、Reviewer=`DeepSeek Harness`，分支 `agent/zcode/TASK-032-sfx-policy-gate-region-type`，**无任何提交**），随后按用户指示改派 Owner 并重建分支/worktree，见上。
