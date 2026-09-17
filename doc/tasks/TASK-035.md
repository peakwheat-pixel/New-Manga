---
id: TASK-035
title: 修复渲染层 SFX Policy Gate 缺失 region_type 前置（F-1 渲染面）
kind: bugfix
status: in_review
approval: approved_by_user
suggested_owner: ZCode
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-019, TASK-032]
base_commit: 2e1bf2d3d9610c1c53537f45abc12e82e8e5ee4f
branch: agent/deepseek/TASK-035-render-sfx-gate-region-type
worktree: G:/CODEX/New Manga.worktrees/TASK-035-deepseek
integration_commit: null
---

# TASK-035：修复渲染层 SFX Policy Gate 缺失 region_type 前置（F-1 渲染面）

**状态提示（2026-09-17）**：`status=in_review`——修复已实现并取证（delivery head `6ddd955`），待**非作者**（Codex）按协作协议 §6 四轴独立 Review；AC 逐条证据、门控矩阵、判别力与越界发现见 [verification/TASK-035/author-verification.md](../../verification/TASK-035/author-verification.md) 与 [Handoff](../handoffs/TASK-035-6ddd955.md)。

**READY（2026-09-17 用户批准释放）**：Owner=`DeepSeek Harness`、Reviewer=`Codex`（**非作者**——Owner 为 DSH 时若仍由 DSH 审会构成同体审查，故一并指定）；base=`2e1bf2d`（释放时的 master HEAD）、branch/worktree 见顶部元数据（已创建并同步到本次释放提交）。Owner 开始实施前，在本任务分支把 `status` 改为 `in_progress`。

**释放前核对（Codex 实测，非作者自述）**：R-04 仍在——`src/application/rendering/service.py:219` 与 `:347` 仅做 `SfxPolicy(...)` 判定，**该文件内 `region_type` 零命中**；R-05 仍在——`src/domain/tasks/models.py:182` 的 `sfx_policy: str = "translate"`；R-02 仍在——`tests/pipeline/test_pipeline.py:51` 的夹具默认 `"translate"`。四个允许路径（`src/application/rendering`、`src/domain/tasks/models.py`、`tests/rendering`、`tests/pipeline`）均存在。

**F-1 关闭条件**：本 Task 完成并集成后，F-1 才可从"部分关闭（规划面 closed / 渲染面 open）"改为 **closed**。**Review 口径**：按[协作协议](../09_COLLABORATION.md) §6 的**四轴**执行（Standards / Spec / Architecture / Verification，逐轴 `executed`/`N/A`、每轴一行小结、**不跨轴排名**），Standards 与 Spec 两轴应优先由**独立执行者/线程并行**（不可用时按兜底做两遍相互隔离检查并声明偏差）。

## 来源与目标

- 来源：[doc/reviews/TASK-032-771977c.md](../reviews/TASK-032-771977c.md) 的 R-04/R-05/R-02；[doc/STATUS.md](../STATUS.md) 的 F-1 登记（现为"部分关闭"）。
- 规范依据：D06 §85「SFX Policy Gate」的前置 `region_type = sfx`；D08 AC-SFX-001；D03 §7 默认 `skip`。
- 现状（Codex 实测，非作者自述）：`src/application/rendering/service.py:219` 与 `:347` 仅做 `SfxPolicy(stored.sfx_policy)` 判定，**没有 `region_type` 前置** → 普通 `speech` Region 取真实默认 `skip` 时 `rerender` 仍返回 `SKIP_POLICY` / `skip_policy`；且该行为被既有用例固定为期望（`tests/rendering/test_rerender.py:246-265`：fixture 未设 `region_type`（默认 `speech`）+ `sfx="skip"` → 断言 `skipped`）。

## Acceptance Criteria

- [x] 渲染层与 planner 采用**同一判据**：仅 `region_type == sfx` 参与 SFX 策略；非 SFX 类型任何策略取值都不影响渲染结果。
      → `_sfx_gate_allows` 内部调用 planner/Translate Step 共用的 `decide_sfx_translation`（自带 `region_type == sfx` 前置）；门控矩阵 12 组合实测：`speech` × {skip,manual,translate} × {allow_manual False,True} 全部放行，`sfx` × skip 始终拦住、`sfx` × manual 仅显式放行、`sfx` × translate 放行（[`defaults-and-gate-matrix.txt`](../../verification/TASK-035/defaults-and-gate-matrix.txt)）；用例 `test_non_sfx_policy_values_never_gate_rendering`、`test_speech_region_with_the_real_default_policy_renders`（含单 Region 版）。
- [x] 复用**单一规则来源**，不得再出现第二份实现。
      → 渲染层两处 `sfx = SfxPolicy(...)` 判定全部删除，改走 `application.translation.context.gate.decide_sfx_translation`；渲染层仅保留 D06 §47 的显式手动逃生口判断（非策略映射）。
- [x] 修正 `tests/rendering` 中把缺陷固化的用例（fixture 的 region 显式建为 `region_type="sfx"`），并新增"`speech` + 真实默认 `skip` → 正常渲染"的回归用例；**不得放宽或删除其他断言**。
      → `make_region` 新增 `region_type`（默认 `speech`）与 `sfx=None`（保留实体真实默认 `skip`）；`test_sfx_skip_regions_follow_policy_gate`、`test_manual_sfx_requires_explicit_flag` 显式 `region_type="sfx"` 且断言逐字保留；新增 7 例（真实默认页面级/单 Region、非 SFX × 3 策略、SFX 真实默认仍被拦、SFX+translate 正常渲染）。判别力：修前 `src/` + 本次用例 → **5 failed / 119 passed**。
- [x] `src/domain/tasks/models.py:182` 的 `RegionSnapshot.sfx_policy` 字段默认与实体/Schema 一致（`SfxPolicy.SKIP.value`）。
      → 已改并实测四方默认一致（实体/Snapshot/夹具/Schema 均 `skip`）。
- [x] `tests/pipeline` 的 `region()` 夹具默认对齐生产默认（或显式注明差异），消除 R-02 的"夹具漂移"面。
      → 夹具默认改为 `SfxPolicy.SKIP.value` 并在 docstring 注明依据；新增守卫用例 `test_region_defaults_agree_across_entity_snapshot_and_fixture` 断言实体/Snapshot/夹具三方相同。
- [x] 交付 Handoff、实际测试/审阅记录与未完成项，经**非作者** Review（按协作协议 §6 四轴）与 Codex 集成验证后才能 done。
      → Handoff：[TASK-035-6ddd955](../handoffs/TASK-035-6ddd955.md)；取证：[verification/TASK-035/](../../verification/TASK-035/author-verification.md)。**Review 与集成尚未执行**，本 Task 不自行标记 `approved`/`done`。

## 允许修改范围

- `src/application/rendering/**`
- `src/domain/tasks/models.py`
- `tests/rendering/**`、`tests/pipeline/**`
- `doc/tasks/TASK-035.md`、`doc/handoffs/TASK-035-*.md`、`verification/TASK-035/**`

超出范围（Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、其他 Task、`src/ui/**`）先由 Codex 明确范围变更。

## 禁止范围

- 不得修改 Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、生产数据、其他 Task。
- 不得改变 `sfx_policy` 的默认值语义（D03 §7 的 `skip` 保持）。
- 不得放宽/删除既有断言或新增 skip 掩盖失败；不得顺手修 `tests/reading_export` 的两个已登记 flaky。

## 测试要求

- 主套件：`python -m pytest tests/rendering tests/pipeline -q -p no:cacheprovider -rs`。
- 必须双侧验证：**`speech` + `skip` → 渲染不被拦**；**`sfx` + `skip`/`manual` → 仍被拦**（保留原意）。
- 回归：全仓 `python -m pytest -q`，分列 passed/skipped 与 skip 原因。
- 记录 commit、OS/依赖、命令、退出码与证据路径。

## 依赖、风险与阻塞

硬依赖：[TASK-019](TASK-019.md)、[TASK-032](TASK-032.md)——均已集成 `done`。

阻塞：**已解除**——2026-09-17 用户批准释放（`approval=approved_by_user`）；实现已完成，当前 `status=in_review` 待非作者 Review。越界项（测试基础设施的 `conftest` 命名冲突 N-1）已登记，不影响本 Task 的完成判定。

风险：修改 `tests/rendering/**` 会触碰 TASK-014/015 交付的渲染用例，必须保留其原意（SFX 类型仍被策略拦截），只补正 fixture 的类型。

## 交付与运行记录

- Handoff：[TASK-035-6ddd955](../handoffs/TASK-035-6ddd955.md)（delivery_head=`6ddd955`）。
- Review：尚无（待 Codex 非作者独立 Review，按协作协议 §6 四轴：Standards / Spec / Architecture / Verification）。
- 实际执行/测试：
  - 取证总表：[verification/TASK-035/author-verification.md](../../verification/TASK-035/author-verification.md)；门控矩阵与默认值：[defaults-and-gate-matrix.txt](../../verification/TASK-035/defaults-and-gate-matrix.txt)；判别力：[discriminative-prefix.log](../../verification/TASK-035/discriminative-prefix.log)；日志：[pytest-main.log](../../verification/TASK-035/pytest-main.log)、[pytest-regression.log](../../verification/TASK-035/pytest-regression.log)、[pytest-full.log](../../verification/TASK-035/pytest-full.log)、[pytest-full-clean.log](../../verification/TASK-035/pytest-full-clean.log)、flaky 对照：[flaky-control.log](../../verification/TASK-035/flaky-control.log)、[flaky-ab.log](../../verification/TASK-035/flaky-ab.log)、[flaky-ab-full.log](../../verification/TASK-035/flaky-ab-full.log)；越界证据：[conftest-collision.log](../../verification/TASK-035/conftest-collision.log)；路径核对：[changed-paths.txt](../../verification/TASK-035/changed-paths.txt)。
  - 命令与结果（`TASK-012-py312`，Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1，`PYTHONDONTWRITEBYTECODE=1`，全部 `-p no:cacheprovider`）：基线（`e8e1750` 导出树）全仓 **671 passed / 6 skipped**；主套件 `tests/rendering tests/pipeline` **124 passed / 0 skipped**（rendering 56→63、pipeline 60→61）；回归 `tests/core`+`tests/storage`+`tests/providers` **159 passed / 0 skipped**、`tests/editing` **26 passed**；全仓 **679 passed / 6 skipped**（6 条 skip 全为既有 `tests/network` 的 `openssl unavailable`）。判别力：修前 `src/` + 本次用例 → **5 failed / 119 passed**。边界：`git diff --name-only e8e1750..HEAD` 5 个路径全在允许范围、越界 0；全范围禁止路径命中 0；`git diff --check 2e1bf2d..HEAD` 退出码 0。
  - **已登记 flaky（未修复、未新增 skip）**：全仓串跑偶发 `tests/reading_export/test_qml_contract.py::test_reader_webtoon_swaps_in_vertical_viewer` 失败（TASK-017 R-007 / TASK-019 T-1 已登记；本 Task 允许路径不含该文件）。已做对照实验（`tests/pipeline tests/reading_export` 两棵树各 6 次 → 全绿）与全仓频率对照（`flaky-ab-full.log`），结论与不确定性见取证 §3.1；**不记为通过、也不归因于本 Task**。
- **最近状态（当前，唯一）**：2026-09-17 实现完成并置 **`in_review`**，交 Codex 非作者独立 Review（集成由 Codex 执行）。分支 `agent/deepseek/TASK-035-render-sfx-gate-region-type`、worktree `G:/CODEX/New Manga.worktrees/TASK-035-deepseek`、fixed base `2e1bf2d`、delivery head `6ddd955`（`16cd171` 开工文档、`6ddd955` 修复与用例）。**未 push、未合并 master**。越界发现登记（未修改，供 Codex 裁决）：**N-1** `tests/providers/**` 的裸 `from conftest import …` 在同一 pytest 调用中与 `tests/editing/conftest.py` 冲突（`tests/providers tests/editing` → 4 collection errors；修前树同样复现）；**N-2** 非 SFX 的取值域外策略不再报错（AC ① 的必然结果，已声明）；**N-3** `rerender_region` 的策略校验位置保持在"缺 Clean / 无 final"之后（返回顺序未变，已声明）。
- 历史状态（2026-09-17）：由 Codex 依据 TASK-032 Review 的 R-04/R-05/R-02 创建为 `proposed`（`approval=pending_user_review`，owner/reviewer/base/branch/worktree 均为空）；当日获用户批准释放为 `ready`（Owner=`DeepSeek Harness`、Reviewer=`Codex`、base=`2e1bf2d`、branch/worktree 见顶部元数据）。
