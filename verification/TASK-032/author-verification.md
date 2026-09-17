# TASK-032 作者取证：`771977c`（SFX Policy Gate 的 region_type 前置）

- Task：TASK-032「修复 SFX Policy Gate 缺失 region_type 前置（F-1）」
- Owner／作者：DeepSeek Harness ／ Reviewer：Codex（**非作者**，最终集成由 Codex 执行）
- 固定 base：`ca17d454edc03bc1b057e9e3fc463c81da652e53`（代码基线；分支起点 `c004d4e` = Codex 的释放/改派纯文档提交）
- 分支 / 工作区：`agent/deepseek/TASK-032-sfx-policy-gate-region-type` ／ `G:/CODEX/New Manga.worktrees/TASK-032-deepseek`
- 交付 head：`771977c`（`a5823d1` 为开工的 `in_progress` 文档提交）
- 依据：[doc/reviews/TASK-019-726baf5.md](../../doc/reviews/TASK-019-726baf5.md) R-5 / F-1；D06 §85；D08 AC-SFX-001/002/003；D03 §7

## 1. 缺陷与修法

**缺陷（`src/application/tasks/service.py:353-361`，修前）**：规划器只用 `sfx_policy in {"skip","manual"}` 判定 SFX 策略，**没有 `region_type` 前置**；而新建 Region 的真实默认是 `region_type='speech'` + `sfx_policy='skip'`（实体与 Schema 均如此），于是普通对白的 `translate/segment/mask_refine/inpaint/render` 在规划阶段全部被判为 `SKIP_POLICY("sfx_skip")`，且 `src/ui/**` 无任何写入该字段的路径。

**修法（仅两个允许的代码文件）**：

| 文件 | 改动 |
|---|---|
| `src/application/tasks/service.py` | 新增 `_SFX_GATED_STEPS`、`_SFX_REGION_TYPE`、`_effective_sfx_policy`、`_sfx_gate_suppresses`；`_decide_step` 改为 `region is not None and step_type in _SFX_GATED_STEPS and _sfx_gate_suppresses(region)` → `SKIP_POLICY(SFX_SKIP_REASON)`。**策略规则不再重实现**：委托给 Translate Step 早已使用的 `application.translation.context.gate.decide_sfx_translation`（F-1 的根因正是"同一规则两份实现、彼此漂移"） |
| `src/infrastructure/sqlite/pipeline.py` | `_region()` 的 `sfx_policy` 缺省由 `"translate"` 改为 `SfxPolicy.SKIP.value`（与实体/Schema 一致，AC ③）；补注释说明 |

**语义边界（明确声明）**：

- **前置**：只有 `region_type == "sfx"` 参与该 gate；非 SFX 类型**任何** `sfx_policy` 取值都不进入判定（AC ②）。
- **默认**：SFX 类型的 `sfx_policy` 缺失/空白 → 回落 `skip`（D03 §7，AC ③）；非 SFX 不参与。
- **取值域**：Schema CHECK 只允许 `skip`/`manual`/`translate`。落在取值域外的 SFX 取值由共享 gate 的 `SfxPolicy(...)` 校验**在规划阶段拒绝**（`ValueError`）；这与 Translate Step 既有行为一致（旧代码会让它进入规划、在步骤执行时才失败）。该行为已由测试固定并在此显式声明。
- **未改变**：`sfx_policy` 的默认值语义（仍是 `skip`，D03 §7）、Schema、migration、依赖清单、pipeline seam 本体。

## 2. 验收点对照（逐条）

| AC | 判定 | 证据 |
|---|---|---|
| ① 仅 `region_type == sfx` 应用策略：`skip`/`manual` → `SKIP_POLICY("sfx_skip")`；`translate` → 进入 Translation | **PASS** | `tests/pipeline/test_pipeline.py::test_sfx_region_policies_suppress_the_automatic_chain[skip/manual]`（5 个受控步骤全部 `SKIP_POLICY` 且 `reason == "sfx_skip"`）；`::test_sfx_region_translate_policy_enters_the_translation_chain`（全链 `RUN`）；真实 SQLite 版 `tests/pipeline/test_pipeline_production_seam.py::test_real_default_sfx_policy_still_gates_an_sfx_region` |
| ② 非 SFX 类型任何 `sfx_policy` 都不影响 `translate/segment/mask_refine/inpaint/render` 的规划 | **PASS** | `::test_sfx_policy_never_gates_a_non_sfx_region`：`speech/narration/title/note/other` × `skip/manual/translate` = **15 例**，断言全链 `{RUN}` 且无 `sfx_skip`；其中 `speech × skip` 即 F-1 的**真实默认值**组合 |
| ③ 缺字段口径唯一：SFX 回落 `skip`；非 SFX 不参与；`sqlite/pipeline.py` 快照默认与实体/Schema 一致 | **PASS（含 1 条越界残留，见 §4 N-2）** | `::test_sfx_region_without_a_policy_falls_back_to_skip[""/None]`；`test_pipeline_production_seam.py::test_region_snapshot_deserialiser_uses_the_documented_sfx_default`；默认值三方实测见 [`schema-defaults.txt`](schema-defaults.txt)：实体 `skip`、Schema `skip`、快照反序列化 `skip`（修前为 `translate`） |
| ④ `tests/pipeline` 新增"真实默认值"用例；既有 `sfx` 用例行为不变 | **PASS** | 单元矩阵中的 `speech × skip`（真实默认组合）；真实 SQLite 用例 `test_real_default_sfx_policy_does_not_gate_a_speech_region`（**插入 region 时不写 `sfx_policy`，取 Schema 默认**，实测 `('speech','skip')`，全链 `{RUN}`）；既有 `test_planner_marks_lock_sfx_and_provider_decisions_separately`（`region_type="sfx"`, `sfx_policy="skip"`）未改动且继续通过 |
| ⑤ `tests/pipeline` 全绿 + 全仓分列 passed/skipped 与 skip 原因 | **PASS** | `tests/pipeline` **60 passed / 0 skipped**；`tests/core`+`tests/storage`+`tests/providers` **159 passed / 0 skipped**；全仓 **671 passed / 6 skipped**（基线 `c004d4e` = 641 passed / 6 skipped，增量 30 全部为本 Task 新增用例）；6 条 skip 全为既有 `tests/network` 的 `openssl unavailable`。已登记的 `tests/reading_export` 低频 flaky **未改动、未新增 skip**，本 Task 不把它记为通过 |

**判别力**（新增用例对修前代码必须失败）：把**修前的 `src/`**（`git archive HEAD` 于 `c004d4e` 导出树）与新测试文件组合运行 → **17 failed / 43 passed**，失败覆盖真实默认值用例、快照默认用例、非 SFX 矩阵中的 `skip/manual` 组合与未知取值用例（日志 [`discriminative-prefix.log`](discriminative-prefix.log)）。其中 `sfx × skip/manual` 与 `sfx × translate` 用例在修前也通过——证明新用例同时固定了"缺陷"与"既有正确行为"。

## 3. 验证证据（逐命令、退出码、passed/skipped）

环境：Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`PYTHONDONTWRITEBYTECODE=1`；未设置 `QT_QPA_PLATFORM`；全部 `-p no:cacheprovider`。原始日志见同目录 `pytest-*.log`。

| # | 命令（原样） | 退出码 | passed | skipped | 结果 |
|---|---|---:|---:|---:|---|
| 0 | 基线：`git archive HEAD`（`c004d4e`）导出树内 `python -m pytest -q -p no:cacheprovider` | 0 | **641** | **6** | 改动前全仓基线 |
| 1 | `python -m pytest tests/pipeline -q -p no:cacheprovider -rs` | **0** | **60** | **0** | 主套件全绿（改动前同目录 30 例） |
| 2 | `python -m pytest tests/core tests/storage tests/providers -q -p no:cacheprovider -rs` | **0** | **159** | **0** | 强制回归 |
| 3 | `python -m pytest -q -p no:cacheprovider -rs`（2 次） | **0 / 0** | **671** | **6** | 两次均 `671 passed, 6 skipped`；`641 → 671` 的 30 例全部为本 Task 新增 |
| 4 | 判别力：修前 `src/` + 新测试 → `tests/pipeline` | 1 | 43 | 0 | **17 failed**（见上） |
| 5 | 默认值三方实测（`schema-defaults.txt`） | 0 | — | — | 实体 `skip`／Schema `skip`／快照反序列化 `skip`（修前 `translate`） |
| 6 | 边界：`git diff --name-only c004d4e..HEAD` + 允许范围正则；`git diff --check ca17d45..HEAD` | 0 | — | — | 5 个路径全部在允许范围内、越界 **0**；全范围禁止路径命中 **0**（[`changed-paths.txt`](changed-paths.txt)） |

**skip 明细（命令 0 与 3 相同，6 条全部来自既有 `tests/network`）**：

| 位置 | skip 原因 |
|---|---|
| `tests/network/test_connection_tester.py:106` | `openssl unavailable` |
| `tests/network/test_transport_tls.py:39` | `openssl unavailable` |
| `tests/network/test_transport_tls.py:47` | `openssl unavailable` |
| `tests/network/test_transport_tls.py:62` | `openssl unavailable` |
| `tests/network/test_transport_tls.py:69` | `openssl unavailable` |
| `tests/network/test_transport_tls.py:83` | `openssl unavailable` |

本 Task 新增/改动套件 **0 skipped**；未放宽任何既有断言、未删除断言、未新增 `skip`。

## 4. 越界发现（只登记，不修改；供 Codex/用户裁决）

- **N-1（同源缺陷，渲染层，`P1` 建议）**：`src/application/rendering/service.py:219` + `:238`（`rerender_region`）与 `:347-351`（`_prepare_region`）同样只按 `SfxPolicy(stored.sfx_policy)` 判定、**没有 `region_type` 前置**。既有测试把它当作正确行为固定下来，且用的正是**真实默认形态**（`tests/rendering/test_rerender.py:180-199` 的 `make_region` 只设策略、`region_type` 取 `Region` 默认 `speech`；`:246-264` 断言 `skip` → `skip_policy`；`:458-473` 断言 `manual` → 阻塞）。因此：**规划已修好，但"普通 speech Region 的渲染执行"仍会被该策略拦截**——F-1 同类缺陷在渲染层尚存。TASK-032 的允许路径不含 `src/application/rendering/**`，本 Task 未改动，仅登记证据与影响；建议由 Codex 决定并入 TASK-033（完整链收口）或另立 Task。
- **N-2（口径残留，`P2`）**：`src/domain/tasks/models.py:182` 的 `RegionSnapshot.sfx_policy` 字段默认仍为 `"translate"`（实测见 `schema-defaults.txt`）。本 Task 已把它在**生产路径**上消除（DB 读取显式传值；快照反序列化默认改为 `skip`），但任何直接 `RegionSnapshot(...)` 且不传该字段的构造仍会得到 `translate`。`src/domain/**` 不在本 Task 允许路径，未改动；建议 Codex 在后续切片统一（或明确接受该字段级默认）。
- **N-3（显式声明的行为变化，非缺陷）**：SFX 类型 + 取值域外策略（非 `skip`/`manual`/`translate`）现在**在规划阶段**被共享 gate 拒绝（`ValueError`），旧代码会让它进入规划、由 Translate Step 在执行时同样报错。Schema CHECK 只允许三个取值，故仅在被破坏的快照上可触发；已由测试固定。

## 5. 未完成 / 未运行

| 项 | 状态 | 原因 |
|---|---|---|
| 渲染层同类缺陷（N-1） | **未修（越界）** | `src/application/rendering/**` 不在允许路径；已交付可复现证据 |
| `RegionSnapshot` 字段级默认（N-2） | **未修（越界）** | `src/domain/**` 不在允许路径；生产路径已无影响 |
| 端到端真实翻译/渲染（真实模型/端点） | **NOT_RUN** | 与本 Task 无关的环境限制（TASK-019 已登记：无依赖/权重/端点）；本 Task 只改规划判定 |
| `tests/reading_export` 两个已知 flaky | **未处理（禁止范围）** | 任务明确禁止顺手修复；本 Task 未改动这些测试，也未新增 skip |

## 6. 边界与合规

- 仅修改允许路径：`src/application/tasks/service.py`、`src/infrastructure/sqlite/pipeline.py`、`tests/pipeline/**`、`doc/tasks/TASK-032.md`、`doc/handoffs/TASK-032-*.md`、`verification/TASK-032/**`；越界 **0**。
- **未修改** Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、`src/domain/**`、`src/ui/**`、其他 Task、生产数据/用户源文件。
- 未 `push`、未合并 `master`；未释放其他冻结 Task。
- 未改变 `sfx_policy` 默认值语义（仍为 `skip`）；未放宽既有测试、未删除断言、未新增 skip。
