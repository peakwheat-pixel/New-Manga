# TASK-035 作者取证：`6ddd955`（渲染层 SFX Policy Gate 的 region_type 前置）

- Task：TASK-035「修复渲染层 SFX Policy Gate 缺失 region_type 前置（F-1 渲染面）」
- Owner／作者：DeepSeek Harness ／ Reviewer：Codex（**非作者**，最终集成由 Codex 执行）
- 固定 base：`2e1bf2d3d9610c1c53537f45abc12e82e8e5ee4f`（代码基线；分支起点 `e8e1750` = 释放纯文档提交）
- 分支 / 工作区：`agent/deepseek/TASK-035-render-sfx-gate-region-type` ／ `G:/CODEX/New Manga.worktrees/TASK-035-deepseek`
- 交付 head：`6ddd955`（`16cd171` 为开工的 `in_progress` 文档提交）
- 依据：[doc/reviews/TASK-032-771977c.md](../../doc/reviews/TASK-032-771977c.md) 的 R-04（P1）/ R-05（P2）/ R-02（P2）；D06 §85、D08 AC-SFX-001/002、D03 §7

## 1. 缺陷与修法

**缺陷（渲染层，`src/application/rendering/service.py`）**：`rerender_region`（`sfx = SfxPolicy(stored.sfx_policy)` → `SKIP`/`MANUAL` 拦截）与 `_prepare_region`（同一判定）**都没有 `region_type` 前置**。普通 `speech` Region 取真实默认 `skip` 时，`rerender_page` 记为 `skipped/skip_policy`、`rerender_region` 返回 `BLOCKED/skip_policy`——F-1 的用户可见症状仍在。既有 `tests/rendering/test_rerender.py` 以真实默认形态（`Region` 默认 `speech`）把该行为固定为期望，因此套件照不到缺陷。

**修法（单一规则来源，AC ②）**：

| 文件 | 改动 |
|---|---|
| `src/application/rendering/service.py` | 新增模块级 `_sfx_gate_allows(region_type, sfx_policy, *, allow_manual)`：调用 **planner 与 Translate Step 共用的** `application.translation.context.gate.decide_sfx_translation`（该函数已含 `region_type == sfx` 前置与策略映射），渲染层只在其上叠加 D06 §47 的**显式手动逃生口**；`rerender_region` 与 `_prepare_region` 的两处 `SfxPolicy(...)` 判定全部改走它；模块 docstring 同步（含"非 SFX 永不被该策略拦截"） |
| `src/domain/tasks/models.py` | `RegionSnapshot.sfx_policy` 字段默认 `"translate"` → `SfxPolicy.SKIP.value`（与实体/Schema 一致，D03 §7）——R-05 |
| `tests/rendering/test_rerender.py` | fixture `make_region` 新增 `region_type`（默认 `speech` = 真实类型）并把 `sfx` 改为可为 `None`（`None` = 不改写实体默认，即真实的 `skip`）；两个固化缺陷的用例显式改为 `region_type="sfx"`；新增 7 例（见 §2） |
| `tests/pipeline/test_pipeline.py` | `region()` 夹具默认 `"translate"` → `SfxPolicy.SKIP.value`（R-02 关闭），并新增"实体/Snapshot/夹具三方默认一致"守卫用例 |

**语义边界（请 Reviewer 确认）**：

1. **前置**：只有 `region_type == "sfx"` 参与该策略；非 SFX 类型**任何**策略取值都不影响批量渲染与单 Region 渲染（AC ①，实测矩阵见 [`defaults-and-gate-matrix.txt`](defaults-and-gate-matrix.txt)）。
2. **逃生口保留**：`sfx` + `manual` 仍只在 `allow_manual_sfx=True`（§47 显式单 Region 强制渲染）时通过；`sfx` + `skip` 任何情况下都拦截——原意未放宽。
3. **单一规则**：`decide_sfx_translation` 现在是 planner、Translate Step 与渲染层三处唯一实现；渲染层不再有任何 `SfxPolicy(...)` 策略判定（仅保留 `SfxPolicy(sfx_policy) is SfxPolicy.MANUAL` 的**逃生口**判断，不是策略映射）。
4. **取值域外**：SFX + 非 `skip`/`manual`/`translate` 的取值，由共享 gate 拒绝（`ValueError`，与 TASK-032 规划层一致）；非 SFX 未受该策略影响（旧代码对任意类型都 `SfxPolicy(...)`，因此非 SFX 的未知取值此前会误报错——现在与 AC ① 一致）。
5. **未改变**：`sfx_policy` 默认值语义（仍为 `skip`）、Schema、migration、依赖清单、pipeline seam 本体、`src/ui/**`。

## 2. 验收点对照（逐条）

| AC | 判定 | 证据 |
|---|---|---|
| ① 渲染层与 planner 同一判据：仅 `region_type == sfx` 参与；非 SFX 任何取值都不影响渲染 | **PASS** | 门控矩阵（[`defaults-and-gate-matrix.txt`](defaults-and-gate-matrix.txt)）：`speech` × `skip/manual/translate` × `allow_manual∈{False,True}` 六种组合全部 `render allowed=True`；`sfx` × `skip` 始终 `False`、`sfx` × `manual` 仅 `allow_manual=True` 时 `True`、`sfx` × `translate` 为 `True`。用例：`test_non_sfx_policy_values_never_gate_rendering[skip/manual/translate]`、`test_speech_region_with_the_real_default_policy_renders`、`..._renders_single_region`、`test_sfx_region_with_the_real_default_policy_is_still_gated`、`test_sfx_translate_policy_enters_the_normal_render_flow` |
| ② 复用单一规则来源，不得出现第二份实现 | **PASS** | 渲染层的两处判定改为 `_sfx_gate_allows` → `decide_sfx_translation`（planner/Translate Step 同一函数）。`src/application/rendering/**` 内已无策略映射分支（`grep`：仅剩逃生口用的 `SfxPolicy(...) is SfxPolicy.MANUAL` 与类型注解） |
| ③ 修正固化缺陷的用例 + 新增真实默认回归 + 保留 SFX 拦截语义 | **PASS** | `make_region` 现支持 `region_type`（默认 `speech`）与 `sfx=None`（保留实体默认）；`test_sfx_skip_regions_follow_policy_gate`、`test_manual_sfx_requires_explicit_flag` 显式 `region_type="sfx"`（断言原封不动）；新增：真实默认 `speech`+`skip` 页面级与单 Region 渲染各 1 例、非 SFX × 3 策略 1 组 3 例、SFX 真实默认仍被拦 1 例、SFX+`translate` 正常渲染 1 例。**未放宽或删除任何既有断言**（两道 SFX 用例的断言逐字保留） |
| ④ `RegionSnapshot.sfx_policy` 默认对齐 `SfxPolicy.SKIP.value` | **PASS** | `src/domain/tasks/models.py` 已改；实测三方默认一致（实体/Snapshot/夹具/Schema 均 `skip`）见 [`defaults-and-gate-matrix.txt`](defaults-and-gate-matrix.txt) |
| ⑤ `tests/pipeline` 夹具默认对齐生产默认（消除 R-02） | **PASS** | `region()` 默认改为 `SfxPolicy.SKIP.value` 并在 docstring 说明依据；新增守卫用例 `test_region_defaults_agree_across_entity_snapshot_and_fixture` 断言实体/Snapshot/夹具三者相同 |
| ⑥ `tests/rendering` + `tests/pipeline` 全绿；全仓分列 passed/skipped 与原因 | **PASS** | 主套件 `tests/rendering tests/pipeline` **124 passed / 0 skipped**；回归 `tests/core tests/storage tests/providers` **159 passed / 0 skipped**、`tests/editing` **26 passed**；全仓 **679 passed / 6 skipped**（基线 `e8e1750` = 671 passed / 6 skipped，增量 8 全部为本 Task 新增用例）；6 条 skip 全为既有 `tests/network` 的 `openssl unavailable`（见 §3 与日志） |

**判别力**（新增/修正的用例对修前代码必须失败）：把**修前 `src/`**（`e8e1750` 导出树）与本次测试文件组合运行 → **5 failed / 119 passed**，失败为 4 条渲染层"非 SFX 不得被拦"的新期望 + 1 条三方默认一致守卫；而"SFX 仍被拦"与"SFX+translate 正常"两条在修前也通过——证明用例同时固定了**缺陷**与**必须保留的原意**（日志 [`discriminative-prefix.log`](discriminative-prefix.log)）。

## 3. 验证证据（逐命令、退出码、passed/skipped）

环境：Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`PYTHONDONTWRITEBYTECODE=1`；未设置 `QT_QPA_PLATFORM`（渲染套件按产品边界使用默认 Windows 平台）；全部 `-p no:cacheprovider`。原始日志见同目录。

| # | 命令（原样） | 退出码 | passed | skipped | 结果 |
|---|---|---:|---:|---:|---|
| 0 | 基线：`git archive HEAD`（`e8e1750`）导出树内 `python -m pytest -q -p no:cacheprovider` | 0 | **671** | **6** | 改动前全仓基线（2 次一致） |
| 1 | `python -m pytest tests/rendering tests/pipeline -q -p no:cacheprovider -rs` | **0** | **124** | **0** | 主套件全绿（`tests/rendering` 56 → 63、`tests/pipeline` 60 → 61） |
| 2 | `python -m pytest tests/core tests/storage tests/providers -q -p no:cacheprovider -rs` | **0** | **159** | **0** | 强制回归（含 `src/domain/tasks/models.py` 的消费方） |
| 3 | `python -m pytest tests/editing -q -p no:cacheprovider` | **0** | **26** | **0** | 域模型改动的直接消费方 |
| 4 | `python -m pytest -q -p no:cacheprovider -rs` | **0**（7 次）/ **1**（2 次） | **679** | **6** | 9 次运行：7 次 `679 passed, 6 skipped`；2 次 `1 failed, 678 passed, 6 skipped`，失败均为**已登记 flaky** `tests/reading_export/test_qml_contract.py::test_reader_webtoon_swaps_in_vertical_viewer`（见 §3.1：无代码路径关联 + 隔离实验） |
| 5 | 判别力：修前 `src/` + 本次测试 → `tests/rendering tests/pipeline` | 1 | 119 | 0 | **5 failed**（见 §2 判别力） |
| 6 | 门控矩阵与默认值实测（自写脚本） | 0 | — | — | [`defaults-and-gate-matrix.txt`](defaults-and-gate-matrix.txt)：四方默认均 `skip`；门控矩阵 12 组合与共享规则一致 |
| 7 | 边界：`git diff --name-only e8e1750..HEAD` + 允许范围正则；`git diff --check 2e1bf2d..HEAD` | 0 | — | — | 代码/测试 4 个路径 + 文档路径全部在允许范围内、越界 **0**；全范围禁止路径命中 **0**（[`changed-paths.txt`](changed-paths.txt)） |

**skip 明细（命令 0 与 4 相同，6 条全部来自既有 `tests/network`）**：`test_connection_tester.py:106`、`test_transport_tls.py:39/47/62/69/83`，原因均为 `openssl unavailable`。本 Task 新增/改动套件 **0 skipped**；未放宽/删除既有断言、未新增 skip。

### 3.1 关于全仓偶发失败（如实登记，不掩盖、不归因、未修复）

**现象**：全仓 `python -m pytest -q -p no:cacheprovider` 在本 Task head（`6ddd955`）上共执行 **9 次**，其中 **2 次**失败（`1 failed, 678 passed, 6 skipped`），失败均为 `tests/reading_export/test_qml_contract.py::test_reader_webtoon_swaps_in_vertical_viewer`（断言 `scroll is not None`，QML 垂直 Flickable 的时序敏感）；另 7 次 `679 passed, 6 skipped`。日志：[`pytest-full.log`](pytest-full.log)（失败那次）、[`pytest-full-clean.log`](pytest-full-clean.log)、[`flaky-ab-full.log`](flaky-ab-full.log)。

**为什么不是本 Task 的缺陷（三条独立证据）**：

1. **代码路径无关联**：失败用例位于阅读器子系统；`src/application/reading/**` 与 `src/ui/viewmodels/reader/**` 对 `application.rendering` / `domain.tasks` **零导入**（`grep` 0 命中），本 Task 改动的两个源文件不在其执行图上。
2. **同一用例在无本 Task 改动的 head 上也会失败**：TASK-017 `doc/reviews/TASK-017-protocol.md` R-007 记录 1/3 次失败；TASK-019 独立 Review（`doc/reviews/TASK-019-ab26601.md` T-1）在 **TASK-019 head 上 9 次运行 4 次失败（≈44%）**、在**切片前 `3755af9` 导出树 4 次运行 1 次失败**。即该 flaky 的触发与 TASK-035 无关，只是频率不稳定。
3. **顺序影响已做隔离实验**：本 Task 唯一落在 `reading_export` **之前**收集的新增用例只有 `tests/pipeline` 的 1 例（`tests/rendering` 在其之后收集）。针对性 A/B（`pytest tests/pipeline tests/reading_export`，两棵树各 6 次）**全部通过**（HEAD 125 passed ×6、基线 124 passed ×6，见 [`flaky-ab.log`](flaky-ab.log)）。对照：同一命令在 `e8e1750` 纯基线树上的全仓运行 **12 次全部 `671 passed, 6 skipped`**（[`flaky-ab-full.log`](flaky-ab-full.log)、[`flaky-control.log`](flaky-control.log)）。

**残余不确定性（不辩解、如实登记）**：`0/12`（基线）对 `2/9`（head）这样的小样本无法在统计上排除"顺序/时序暴露度略有变化"的可能；上述三条证据只说明**没有可复现的因果关系**，不能证明"频率完全不受影响"。该用例已被 TASK-017 R-007 与 TASK-019 T-1 登记为仓库级测试基础设施问题；本 Task 的禁止范围明确要求**不得顺手修复**。**Reviewer 复跑若复现，请按同一口径登记**；如需彻底定性，建议在测试硬化切片（TASK-034）中给该用例加显式等待/事件泵诊断并做更大样本的 A/B。

## 4. 越界发现（只登记，未修改）

- **N-1（测试基础设施，P2）**：`tests/providers/**` 的 4 个用例使用 `from conftest import …`（裸模块名），当 pytest **在同一调用中先收集到 `tests/editing/conftest.py` 时**会解析到错误的 conftest，导致 `ImportError: cannot import name 'FakeTransport' from 'conftest'`。复现（**修前树 `e8e1750` 上同样复现**，与本 Task 无关）：
  - `python -m pytest tests/editing tests/providers -q` → **137 passed**（可用顺序）
  - `python -m pytest tests/providers tests/editing -q` → **4 collection errors**（不可用顺序）
  建议由后续切片（如 TASK-034 的测试硬化）把共享替身移到唯一命名的 helper 模块（如 `providers_helpers.py`）并改为 `from providers_helpers import …`。证据：[`conftest-collision.log`](conftest-collision.log)。
- **N-2（既有语义细节，P3，已声明）**：渲染层此前对**任意类型**都执行 `SfxPolicy(stored.sfx_policy)`，因此非 SFX Region 的未知策略值会抛 `ValueError`；现在非 SFX 不参与该策略（AC ①），未知值只在 SFX 上被共享 gate 拒绝。这是 AC ① 的必然结果，已在 §1 语义边界第 4 条声明。
- **N-3（既有行为，P3，已声明）**：`rerender_region` 的策略校验位置在"缺 Clean / 无 final"之后（与修前一致，未调整顺序）；因此"SFX + skip 且缺 Clean"仍先返回 `MISSING_REQUIRED_INPUT`。本 Task 刻意保持返回顺序不变，以免改动其它用例的期望。

## 5. 未完成 / 未运行

| 项 | 状态 | 原因 |
|---|---|---|
| `tests/reading_export` 两个已登记 flaky | **未处理（禁止范围）** | 任务明确禁止顺手修复；本 Task 未改动这些测试，也未新增 skip |
| 真实模型/端点端到端渲染 | **NOT_RUN** | 环境限制（TASK-019 已登记：无依赖/权重/端点），与本 Task 无关 |
| `tests/providers` 的 conftest 命名冲突（N-1） | **未修（越界）** | `tests/providers/**` 不在本 Task 允许路径；已给出复现与建议 |

## 6. 边界与合规

- 仅修改允许路径：`src/application/rendering/service.py`、`src/domain/tasks/models.py`、`tests/rendering/test_rerender.py`、`tests/pipeline/test_pipeline.py`、`doc/tasks/TASK-035.md`、`doc/handoffs/TASK-035-*.md`、`verification/TASK-035/**`；越界 **0**。
- **未修改** Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、`src/ui/**`、其他 Task、生产数据/用户源文件。
- 未 `push`、未合并 `master`；未释放其他冻结 Task。
- 未改变 `sfx_policy` 默认值语义（仍为 `skip`）；未放宽/删除既有断言、未新增 skip。
