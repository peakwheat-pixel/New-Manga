# TASK-036 作者取证：`<head>`（设置输入校验与导出发布顺序硬化）

- Task：TASK-036「设置输入校验与导出发布顺序硬化」（承接 TASK-034 R-02 / R-05 / R-07）
- Owner／作者：DeepSeek Harness ／ Reviewer：Codex（**非作者**）
- 固定 base：`edfdcf2fe923c8c6e97d19377c61c4b8bba25abc`（代码基线）；分支起点 `81ffd83`（释放纯文档提交）
- 分支 / 工作区：`agent/deepseek/TASK-036-settings-validation-and-export-order` ／ `G:/CODEX/New Manga.worktrees/TASK-036-deepseek`
- 交付 head：待提交后回填（`git rev-parse --short HEAD`）

## 1. 实施概览

| AC | 文件 | 改动 |
|---|---|---|
| ① R-02 | `src/application/translation/inpaint/router.py` | `from_settings` 用哨兵区分"键缺失"与"键存在但类型错误"：`inpaint` 存在且非 mapping → `ProviderInputError("inpaint must be a mapping (got X)")`；与 `route_policy` 的错误消息**分属两级**、互不混淆。同一改动同时关闭 TASK-034 实现里的 `route_policy: null` 静默通道（`raw is None` 曾当作缺失） |
| ② R-07a | 同上 | 新增模块级 `_route_sequence(policy, field)`：`allowed_routes`/`fallback_routes` 必须是**真序列**且元素全为 `str`；字符串本身、非序列、非 `str` 元素一律 `ProviderInputError`（字段名 + 期望类型入消息），不再逐字符展开、不再 `str()` 强转 |
| ③ R-07b | 同上 | 新增模块级 `_requirement_flags(policy)`：`requirements` 必须是 mapping，值必须是**真 bool**；`"false"`/`"true"`/`0`/`1`/`None` 一律拒绝，不再 `bool()` 强转；非 mapping 也由裸 `ValueError` 改为 typed error |
| ④ R-05 | `src/ui/viewmodels/export/viewmodel.py` | `_finish`：`_status` → `changed` → `exportFinished` → `_running = False` → `changed`（`running` 的 notify 信号）；`_fail`：`_status` → `refreshStaleWarning()` → `changed` → `exportFailed` → `_running = False` → `changed` |
| ⑤ 冻结解除 | `tests/providers/test_route_policy_settings.py` | 更新上一轮锁定冻结行为的三处用例（见 §5），并在 Handoff 声明解除 |
| ⑥ 语义不变性 | — | 12 类输入前后对照矩阵见 [`input-matrix-before-after.txt`](input-matrix-before-after.txt) |
| ④ 测试侧 | `tests/reading_export/test_viewmodels.py` | 三个导出用例的等待**收回** `pump_until(not vm.running)` 自然终态等待（预算 5 s 不变、断言不变、诊断消息保留）；`test_export_outcome_wait_does_not_accept_the_half_published_state` 按新顺序**更新而非删除**，并新增成功路径同型用例 |

**未改动**（禁止项复核）：路由判定算法（`decide_route`/`acceptable_routes`/`preferred_route_order`/`route_gate`/`RouterFeatures`）、TASK-034 裁决 R-1～R-6 的既有**合法**语义、Schema/migration、依赖清单、seam 本体、`AGENTS.md`、其他 Task；未处理 R-03/R-06。

## 2. AC ⑥：12 类输入前后对照矩阵

完整输出见 [`input-matrix-before-after.txt`](input-matrix-before-after.txt)（探针分别在 base `edfdcf2` 导出树与本次 src 上运行同一脚本）。

**合法输入（含义一字未变，8 类）**：

| # | 输入 | 前 | 后 |
|---|---|---|---|
| 1 | 无 `inpaint` 键 | `default` | **相同** |
| 2 | `inpaint={}` | `default` | **相同** |
| 7 | `route_policy={}` | allowed=基线两条 / () / None / {} | **相同** |
| 8 | `allowed_routes=["edge-bleed"]` | `('edge-bleed',)` | **相同** |
| 9 | `allowed_routes=[]` | 回落 `default.allowed_routes`（R-3） | **相同** |
| 10 | `color_route="flux-fill"` | `('simple-fill','edge-bleed','flux-fill')`、color=`flux-fill` | **相同** |
| 11 | `color_route=""` | color=`None`（Option B） | **相同** |
| 12 | `requirements={"brushnet": True}` | `{'brushnet': True}` | **相同** |

**非法输入（处理由静默/改写改为报错）**：

| # | 输入 | 前（base `edfdcf2`） | 后（本 Task） |
|---|---|---|---|
| 3 | `inpaint="oops"`（段类型错） | **静默回落默认** | `INVALID_INPUT: inpaint must be a mapping (got str)` |
| 4 | `route_policy="simple-fill"` | `INVALID_INPUT: inpaint.route_policy must be a mapping` | 同型（消息附具体类型） |
| 5 | `route_policy=[]` | 同上 | 同上 |
| 6 | `route_policy=None` | **静默回落默认**（TASK-034 实现的 `None` 漏洞） | `INVALID_INPUT: inpaint.route_policy must be a mapping (got NoneType)` |
| 13 | `allowed_routes="simple-fill"` | **逐字符展开** 11 个单字符路线 | `…allowed_routes must be a sequence of strings (got str)` |
| 14 | `fallback_routes="edge-bleed"` | 逐字符展开 10 项 | `…fallback_routes must be a sequence of strings (got str)` |
| 15 | `allowed_routes=[1]` | `str(1)` → `('1',)` | `…allowed_routes entries must be strings (got int)` |
| 16 | `requirements={"brushnet": "false"}` | `bool("false")` → `True`（**反向语义**） | `…requirements['brushnet'] must be a bool (got str)` |
| 17 | `requirements={"brushnet": 0}` | `False`（静默改写） | `…requirements['brushnet'] must be a bool (got int)` |
| 18 | `requirements=["brushnet"]` | 裸 `ValueError`（非 typed error） | `…requirements must be a mapping (got list)` |

## 3. AC ①/②/③ 判别力证据

[`discriminative-prefix.log`](discriminative-prefix.log)：把本次**新测试**放到 **base `edfdcf2` 的 src** 上运行 → `test_route_policy_settings.py` + `test_handlers_pipeline.py` **28 failed / 37 passed**（全部为新增的拒绝类用例与运行路径段类型回归；合法输入用例 37 条在旧 src 上也通过，证明矩阵未把合法输入误判为非法）。即新测试对旧行为具备判别力，不是空跑。

## 4. AC ①：装配 + 运行两条回归

| 路径 | 用例 | 现状 |
|---|---|---|
| 装配（`build_provider_runtime`） | `test_runtime_assembly_reports_a_malformed_section_instead_of_ignoring_it` | `{"inpaint": "oops"}` → `ProviderInputError`，消息含 `inpaint must be a mapping` |
| 运行（Inpaint Step，真实 SQLite + seam） | `test_handlers_pipeline.py::test_run_settings_non_mapping_inpaint_section_fails_the_step_loudly` | `step.status=FAILED`、`error_code=INVALID_INPUT`、消息含 `inpaint must be a mapping` 且**不含** `route_policy`，且未写出 clean artifact |
| 既有 `route_policy` 非 mapping（不回归） | `test_non_mapping_route_policy_raises_the_same_typed_error`、`test_run_settings_malformed_route_policy_fails_the_step_loudly` | 保持 |

## 5. AC ⑤：冻结解除声明

本轮**解除 TASK-034 R-07 冻结**（用户批准的 TASK-036 目标语义：非法输入 fail-closed）。同步更新的既有用例：

| 旧用例（锁定冻结行为） | 新用例（锁定新语义） |
|---|---|
| `test_missing_section_or_key_returns_the_explicit_default` 中 `{"inpaint": "not-a-mapping"}` → 断言 `is DEFAULT_ROUTE_POLICY` | 断言改为抛错：`test_present_non_mapping_section_fails_loud_with_its_own_message`（消息分级、且 R-1 缺失语义仍为 `is DEFAULT`） |
| `test_allowed_routes_as_string_keeps_the_frozen_char_expansion` | `test_route_lists_reject_a_bare_string[allowed_routes/fallback_routes]` |
| `test_fallback_routes_and_requirements_defaults_are_frozen` 中的 `bool("false") → True` | `test_requirements_values_must_be_real_bools[...]`；合法默认（`()`/`{}`）保留在新的 `test_fallback_routes_and_requirements_defaults` |

其余既有断言**未放宽/未删除**，未新增任何 `skip`/`xfail`。

## 6. AC ④：发布顺序证据

**源码顺序**（`_finish`/`_fail`）：终态 `_status` → `changed` → 终态信号 → `_running = False` → `changed`（后者是 `running` 的 notify 信号，保证 QML 观察者仍能收到标志变化）。

**定向探针**（[`export-publish-order.txt`](export-publish-order.txt)，同步调用 `_fail`/`_finish`，`running` 置为进行中，逐事件记录槽内观测值）：

| 事件序列 | 修复前（`edfdcf2`） | 修复后（本 Task） |
|---|---|---|
| `_fail` | `changed(False)` → `changed(False)` → `exportFailed(False)` | `changed(True)` → `changed(True)` → `exportFailed(True)` → `changed(False)` |
| `_finish` | `changed(False)` → `exportFinished(False)` | `changed(True)` → `exportFinished(True)` → `changed(False)` |

即**修复前**任何槽内观测 `running` 都已是 `False`（终态尚未发布）；**修复后**终态在 `running=True` 期间发布完毕，只有最后一个 `changed` 观测到 `False` —— 与 AC ④ 要求一致。

**测试侧**：

- 三个导出用例的等待已收回自然终态等待 `pump_until(qapp, lambda: not vm.running)`（预算 5 s 未变、断言未变、`export_diagnostics` 轨迹保留）。
- `test_export_outcome_wait_does_not_accept_the_half_published_state`（**更新而非删除**）现锁定新不变量：任何 `changed` 快照中 `running=False` 必伴随终态消息；并以 `Qt.DirectConnection` 断言终态信号在 `_running` 清空前触发（`in_call == [True]`）；另保留"检测器非空转"断言（旧顺序样本仍会被识别为半发布）。
- 新增成功路径同型用例 `test_success_path_also_publishes_before_clearing_running`。
- 判别力：把这两个用例放到 base `edfdcf2` 的 viewmodel 上 → **2 failed**（见 [`discriminative-prefix.log`](discriminative-prefix.log)）。

## 7. AC ⑦：回归与分列

（数值将在全仓串跑完成后回填；命令与日志路径见下。）

- mandated：`python -m pytest tests/providers tests/core tests/reading_export tests/editing -q -p no:cacheprovider -rs`
- 全仓：`python -m pytest -q -p no:cacheprovider -rs -rf` ×6 → [`full-suite-runs.log`](full-suite-runs.log)

## 8. 环境与边界

环境：Windows 11 `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`PYTHONDONTWRITEBYTECODE=1`；全部 `-p no:cacheprovider`。

边界：改动仅 `src/application/translation/inpaint/router.py`、`src/ui/viewmodels/export/viewmodel.py`、`tests/**`、`doc/tasks/TASK-036.md`、`doc/handoffs/TASK-036-*.md`、`verification/TASK-036/**`；未越界、未 push、未释放冻结 Task。
