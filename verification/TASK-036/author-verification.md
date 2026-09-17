# TASK-036 作者取证：`<head>`（设置输入校验与导出发布顺序硬化）

- Task：TASK-036「设置输入校验与导出发布顺序硬化」（承接 TASK-034 R-02 / R-05 / R-07）
- Owner／作者：DeepSeek Harness ／ Reviewer：Codex（**非作者**）
- 固定 base：`edfdcf2fe923c8c6e97d19377c61c4b8bba25abc`（代码基线）；分支起点 `81ffd83`（释放纯文档提交）
- 分支 / 工作区：`agent/deepseek/TASK-036-settings-validation-and-export-order` ／ `G:/CODEX/New Manga.worktrees/TASK-036-deepseek`
- 交付 head：`c931db0`（`dd608f4` 为开工 `in_progress` 文档提交）

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

**mandated 四套件**：`python -m pytest tests/providers tests/core tests/reading_export tests/editing -q -p no:cacheprovider -rs` → **274 passed / 0 skipped**（基线 `edfdcf2`：243 passed）。本会话该命令共 7 次：**6 次 274 passed（exit 0）、1 次命中已登记 flaky**（`1 failed, 273 passed`，失败点 `test_qml_contract.py:312`，详见 §9）；逐次记录见 [`mandated-four-runs.log`](mandated-four-runs.log)。

**逐目录 passed 对照**（纯净 `edfdcf2` 导出树 vs 本 head，[`test-counts.txt`](test-counts.txt)）：

| 目录 | 基线 | 本 head | 差异 |
|---|---|---|---|
| `tests/providers` | 134 | **164** | +30（AC ①②③ 拒绝类用例与两条调用点回归；旧冻结用例被替换） |
| `tests/core` | 18 | 18 | 不变 |
| `tests/reading_export` | 65 | **66** | +1（AC ④ 成功路径同型用例；半发布用例为更新而非新增/删除） |
| `tests/editing` | 26 | 26 | 不变 |
| `tests/ui_shell` / `tests/workbench` | 46 / 51 | 46 / 51 | 不变（`src/ui/**` 改动的相邻套件） |
| mandated 四套件合计 | 243 | **274** | +31 |

**全仓串跑 ≥5 次逐次记录**（`python -m pytest -q -p no:cacheprovider -rs -rf`，[`full-suite-runs.log`](full-suite-runs.log)）：

| # | 退出码 | passed | skipped | 失败用例 |
|---|---:|---:|---:|---|
| 1 | 0 | 737 | 6 | 无 |
| 2 | 0 | 737 | 6 | 无 |
| 3 | 0 | 737 | 6 | 无 |
| 4 | 0 | 737 | 6 | 无 |
| 5 | 0 | 737 | 6 | 无 |
| 6 | 0 | 737 | 6 | 无 |
| 7（带 `-rs` 明细） | 0 | 737 | 6 | 无 |

基线对照：纯净 `edfdcf2` 导出树全仓 **706 passed / 6 skipped**（exit 0）→ 本 head **737 passed / 6 skipped**（+31）。

**全仓串跑逐次记录（三段合计 17 次）**：

1. 实现完成后 7 次（`-rs -rf`）：[`full-suite-runs.log`](full-suite-runs.log) —— 6 次 `737 passed / 6 skipped`（exit 0）+ 第 7 次带 skip 明细（同数）→ **7/7 通过**；其中第 8 次（并入下段计数）失败。
2. 复现尝试 6 次（`--tb=long -rf`）：[`intermittent-failure-repro.log`](intermittent-failure-repro.log) —— 5 次通过、**第 6 次命中已登记 flaky**（真实签名，见 §9）。
3. 诊断稳健化之后 4+ 次：`full-suite-runs-post-diagnostics.log` —— 全部 `737 passed / 6 skipped`（exit 0）。

合计：**20 次中 17 次 `737 passed / 6 skipped`（exit 0）、3 次失败且 3 次都落在同一已登记用例**（`test_reader_webtoon_swaps_in_vertical_viewer`；1 次被诊断掩蔽、1 次拿到真实签名、1 次仅捕获用例名）。**基线与归属对照**：纯净 `edfdcf2` 导出树（无本 Task 任何改动）6 次全仓串跑中**同样复现同一用例 1 次**（`1 failed, 705 passed, 6 skipped`，[`flaky-rate-baseline.log`](flaky-rate-baseline.log)）——即该 flaky **不是本 Task 引入**；基线与本 head 的产出对照为 **706 passed / 6 skipped → 737 passed / 6 skipped（+31）**。**3 次失败均未记为通过、未归因本 Task。**

**skip 明细（每轮相同，6 条全部为既有环境 skip）**：`tests/network/test_connection_tester.py:106`、`test_transport_tls.py:39`、`:47`、`:62`、`:69`、`:83`，原因均为 `openssl unavailable`。**未新增任何 skip / xfail。**

## 9. 已登记 flaky 的首次捕获签名（本 Task 的附带发现）

1. **复现 #1（第 8 次全仓串跑）**：报告 `tests/reading_export/test_qml_contract.py:153: RuntimeError`。该行在**诊断辅助函数**内 —— 即被测断言**已经失败**（flaky 触发），但构造失败消息时访问了**已销毁的 QML C++ 对象**，`RuntimeError` 取代了 `AssertionError`，**把 flaky 的真实签名掩蔽了**。
2. **诊断稳健化（本 Task 的小改动，请 Reviewer 裁定接受/回退）**：在 `tests/reading_export/test_qml_contract.py` 增加 `safe_property()`（`RuntimeError` → `<unavailable: …>` 占位），并让 `object_names()`、webtoon 用例的两处等待条件与 `webtoon_save_diagnostics()` 都走它。**不改变任何断言、等待预算或测试语义**；不解决、不重分类 R-06。
3. **复现 #2（第 14 次全仓串跑，稳健化之后）**：拿到了**真实签名**（原文见 [`registered-flaky-signature.md`](registered-flaky-signature.md)）：
   - 失败点 = 既有断言 `pump(window, 2.0, lambda: reading.progress.scroll_offset_y == 240.0)`（`test_qml_contract.py:312`）；
   - 轨迹 = `iterations=98 elapsed_ms=2000 ok=False scroll_contentY=-0.0 saved_scroll_offset_y=0.0`；
   - **关键签名 `contentY = -0.0`**：`setProperty("contentY", 240.0)` 被 Flickable 夹回 0（`boundsBehavior: StopAtBounds`），前一断言只保证 `contentHeight > 0`、**未保证内容能容纳 240 的偏移**；若无值变化则 `onContentYChanged` 不触发、`scrollSaveTimer` 不启动，服务端 `scroll_offset_y` 自然保持 0.0。这比"事件循环饥饿/定时器被反复重启"更贴近证据（98 次迭代、预算耗尽）。
4. STATUS 的 flaky 跟踪节此前把 TASK-034 集成时那 1/14 次失败登记为"用例名未捕获"；本次**4 次复现全部落在同一已登记用例**并给出可读签名 ——
   - 本 head 全仓串跑 **3/20（≈15%）**、mandated 四套件命令 **1/7（≈14%）**；
   - **纯净基线 `edfdcf2` 全仓 **1/6（≈17%）**（[`flaky-rate-baseline.log`](flaky-rate-baseline.log)）→ 失败率与本 head 相当，**不归因本 Task**；
   - 该 flaky **不限于全仓串跑**（mandated 命令同样命中），且失败点**始终是同一条断言** `test_qml_contract.py:312`。
   建议由 Codex 决定是否更新 STATUS 条目（本 Task 不自行改 STATUS）。

## 8. 环境与边界

环境：Windows 11 `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`PYTHONDONTWRITEBYTECODE=1`；全部 `-p no:cacheprovider`。

边界：改动仅 `src/application/translation/inpaint/router.py`、`src/ui/viewmodels/export/viewmodel.py`、`tests/**`、`doc/tasks/TASK-036.md`、`doc/handoffs/TASK-036-*.md`、`verification/TASK-036/**`；未越界、未 push、未释放冻结 Task。
