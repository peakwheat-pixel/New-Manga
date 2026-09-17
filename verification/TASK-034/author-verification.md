# TASK-034 作者取证：`f83a33e`（测试与分层硬化）

- Task：TASK-034「测试与分层硬化（route policy 收敛 / 架构守卫 / flaky 诊断）」
- Owner／作者：DeepSeek Harness ／ Reviewer：Codex（**非作者**，最终集成由 Codex 执行）
- 固定 base：`b34b27e2bc7c1dbd4c3b15a91f08e158d966f365`（代码基线）；分支起点 `c94c183`（释放纯文档提交）
- 分支 / 工作区：`agent/deepseek/TASK-034-test-layer-hardening` ／ `G:/CODEX/New Manga.worktrees/TASK-034-deepseek`
- 交付 head：`f83a33e`（`cff86e4` 为开工的 `in_progress` 文档提交）
- 依据：TASK-019 尾项切片 Review 的 T-2/T-4、TASK-019 尾项切片与 TASK-035 Review 的 flaky 登记、TASK-035 R-02

## 0. 执行顺序与当前状态（**AC ① 第 2 步仍被冻结**）

| AC | 状态 | 说明 |
|---|---|---|
| ① T-2 `route_policy` 语义唯一 | **第 1 步已交付；第 2 步 BLOCKED（等待 Codex 裁决）** | 裁决请求与只读分歧探针见 [`route-policy-decision-request.md`](route-policy-decision-request.md) / [`route-policy-divergences.txt`](route-policy-divergences.txt)。**`src/` 一字未改**（`git diff --name-only b34b27e..HEAD -- src` 为空），两处调用点的可观测行为保持原样 |
| ② T-4 架构守卫加固 | **完成** | 迁入 `tests/core/test_architecture.py` 并复用/扩展 AST 版；旧的行前缀守卫从 `tests/providers` 删除 |
| ③ flaky 有界诊断 | **完成（未复现；机制已锁定）** | 两个已登记用例均加入有界诊断，断言未放宽、未新增 skip；另加 1 例确定性"半发布窗口"判别测试 |
| ④ TASK-035 R-02 `conftest` 脆弱性 | **完成** | 共享替身移入唯一命名 `tests/providers/providers_helpers.py`；两种收集顺序均 0 collection errors |
| ⑤ 回归与分列 | **完成** | 全仓 **6 次**串跑逐次记录；mandated 套件全绿；passed 总数 679 → 682 |
| ⑥ 交付与独立 Review | **待办** | 本取证 + Handoff；Review/集成由 Codex 执行 |

## 1. AC ② 架构守卫加固（T-4）

**改动**：`tests/core/test_architecture.py`

- `find_forbidden_imports` 在保留原静态行为（`ast.Import`/`ast.ImportFrom`，含相对形式、与既有 4 条单测完全兼容）的同时，新增**字面量动态导入**检测：`importlib.import_module("infrastructure…")` 与 `__import__("infrastructure…")`（`ast.Call` + 字符串常量），报告格式 `…: forbidden dynamic import <module>`。
- 新增 3 条用例：`test_application_layer_does_not_import_infrastructure`（`src/application/**` 对 `infrastructure` 的守卫）、`test_dynamic_import_of_a_forbidden_root_is_detected`（字面量动态导入必须被报出）、`test_non_literal_dynamic_import_is_not_a_false_positive`（计算出的模块名不误报）。
- 删除 `tests/providers/test_ports_contract.py` 中的行前缀守卫（**不留两套**），仅留指向新位置的说明注释；该文件不再需要 `pathlib.Path` 导入。

**判别力证据**（[`guard-discriminative.txt`](guard-discriminative.txt)，只读探针同时运行新旧两套逻辑）：

| 候选根 | 新 AST 守卫 | 旧行前缀守卫（已删除） |
|---|---|---|
| 现树 `src/application`（HEAD） | **0** | 0 |
| 历史树 `726baf5:src/application`（S-1 修复前） | **2**（`translation/inpaint/step.py:23,29`） | 2 |
| 合成模块 `importlib.import_module("infrastructure.providers.registry")` | **1**（`forbidden dynamic import …`） | **0**（看不见） |

⇒ 迁移后守卫既能抓住它诞生时的真实回归（S-1），也补上了旧实现的动态导入盲区。

## 2. AC ③ 两个已登记 flaky 的有界诊断

**未复现（如实登记）**：本 Task 共执行**全仓串跑 12 次**（诊断前 6 次 [`flaky-repro-before.log`](flaky-repro-before.log)、诊断后 6 次 [`flaky-repro-after.log`](flaky-repro-after.log)），**均 `exit=0`**（`681/682 passed, 6 skipped`），两个 flaky 用例一次未触发。因此本轮**不能**声称"已修复"，只能交付**可诊断性**与**机制证据**。

### 2.1 `tests/reading_export/test_qml_contract.py::test_reader_webtoon_swaps_in_vertical_viewer`

- **实测失败点（历史证据，TASK-035 取证日志）**：`assert pump(window, 2.0, lambda: reading.progress.scroll_offset_y == 240.0)` 失败（`scroll_offset_y is saved through the service`）——即**有界等待 2 s 内未观察到节流保存结果**。对应 QML 路径：`ReaderView.qml:209-214` 的 `Timer{interval:500; onTriggered: if (active) model.saveScrollOffset(webtoonScroll.contentY)}` + `onContentYChanged: scrollSaveTimer.restart()`。
- **本轮改动（诊断，不改预算、不改断言）**：
  - 新增 `pump_traced(window, seconds, condition)`：与原 `pump` 同预算、同轮询，额外返回 `iterations`/`elapsed_ms`/`ok` 轨迹；
  - 该用例内 3 处等待（对象出现、`contentHeight > 0`、保存结果）与 R-003 重开循环改为 `pump_traced`，失败消息附带轨迹 + `webtoon_save_diagnostics()`（`contentY`、服务端 `scroll_offset_y`、`Image.status`、对象名清单）；
  - 首处 `assert scroll is not None` 由"一次 `processEvents()` 后断言"改为**同样断言的 5 s 有界等待**（对象由 QML 在 `openChapter` 后创建，单次事件处理是竞态假设）；
  - **等待预算保持 5.0/5.0/2.0 秒不变**，断言文字与原意保留。
- **机制说明（供后续定位）**：失败意味着节流定时器在预算内没有把 `contentY` 落到服务（可能是事件循环被拖慢、或 `onContentYChanged` 的 `restart()` 被后续变化不断推迟、或 `active` 在该时刻为假）。诊断消息在下次复现时会直接给出这三者中的哪一个。

### 2.2 `tests/reading_export/test_viewmodels.py::test_start_export_stale_abort_surfaces_failure`

- **根因（代码级，已锁定）**：`src/ui/viewmodels/export/viewmodel.py` 的发布顺序是"先清 `_running`、后写 `_status`／发信号"：
  - `_finish()`：`self._running = False`（`:380`）→ `self._status = …`（`:382-387`）→ `changed.emit()`（`:388`）→ `exportFinished.emit()`（`:389`）；
  - `_fail()`：`self._running = False`（`:392`）→ `self._status = …`（`:393`）→ `refreshStaleWarning()`（`:396`）→ `exportFailed.emit()`（`:398`）。
  测试原先等 `not vm.running`，**可能在该窗口中被唤醒**，于是 `failures` 尚为空 / `statusMessage` 还是"正在导出…"→ 断言随机失败。
- **本轮改动（诊断 + 消除竞态等待，不改断言）**：
  - 新增 `await_export_outcome(app, signals, timeout=5.0)`：等待**断言本身关心的终态信号**（`exportFinished`/`exportFailed`）而非 `running` 代理；新增 `export_diagnostics(vm, signals)` 状态轨迹；
  - 3 个导出用例（完成、stale 中止、取消）改用该等待（取消用例等待"`running` 已清 **且** 状态不再是进行中"），**所有断言逐字保留**，失败消息附带轨迹；
  - 新增确定性判别测试 `test_export_outcome_wait_does_not_accept_the_half_published_state`：构造 `running=False` + 信号为空的"半发布"状态，证明**旧谓词立即为真**而新等待会继续等到超时（即旧等待确实不够，新等待不会掩盖失败）。
- 说明：`running` 与状态/信号同序发布属 `src/ui/**` 的**生产行为**，不在本 Task 允许路径（`src/` 需先申请），故**未修改**，仅作为越界发现登记（见 §5 N-1）。

## 3. AC ④ `tests/providers` 收集顺序脆弱性（TASK-035 R-02）

- **改动**：共享替身（`RecordedCall`/`FakeTransport`/`chat_completion`/`frame`/`mask_from_boxes`/`FakePageImages`/`FakeGeometry`/`FakeOcrProvider`/`FakeTranslationProvider`）移入**唯一命名**的 `tests/providers/providers_helpers.py`；4 个测试模块由裸 `from conftest import …` 改为显式 `from providers_helpers import …`；`conftest.py` 只保留 pytest 注入的 fixture，并从 helper 导入 `FakeTransport`。
- **对照证据**：

| 顺序 | 基线 `b34b27e`（[`collection-orders-before.txt`](collection-orders-before.txt)） | 本 head（[`collection-orders.txt`](collection-orders.txt)） |
|---|---|---|
| `pytest tests/providers tests/editing` | **4 collection errors**（`ImportError: cannot import name 'FakeTransport' from 'conftest'`） | **136 passed**，0 collection errors |
| `pytest tests/editing tests/providers` | 137 passed | **136 passed**，0 collection errors |
| `pytest tests/providers tests/core tests/reading_export`（mandated） | — | **193 passed / 0 skipped** |
| `pytest tests/core tests/storage tests/providers`（回归） | — | **161 passed** |

（两种顺序都通过；顺序 A/B 的 137 → 136 是 AC ② 把旧守卫迁出 `tests/providers` 所致，见 §4。）

## 4. AC ⑤ 回归与分列

**逐目录 passed 对照**（[`test-counts.txt`](test-counts.txt)，基线均为 `b34b27e` 导出树）：

| 目录 | 基线 collected / passed | 本 head collected / passed | 差异说明 |
|---|---|---|---|
| `tests/providers` | 111 / 111 | 110 / 110 | **−1**：AC ② 把行前缀守卫迁出（其断言由 `tests/core` 的新守卫 + 2 条动态覆盖用例承接，**未删除任何断言语义**） |
| `tests/core` | 15 / 15 | 18 / 18 | **+3**：迁移后的 application 守卫 + 动态导入判别 + 非字面量不误报 |
| `tests/reading_export` | 64 / 64 | 65 / 65 | **+1**：AC ③ 的确定性"半发布窗口"判别测试 |
| `tests/editing` / `tests/storage` | 26 / 33 | 26 / 33 | 不变 |
| mandated 三套件合计 | 190 | **193** | +3 |
| 全仓 | 679 | **682** | +3 |

**全仓串跑 ≥5 次逐次记录**（`python -m pytest -q -p no:cacheprovider -rs`，环境见 §6；诊断后 6 次见 [`flaky-repro-after.log`](flaky-repro-after.log)，诊断前 6 次见 [`flaky-repro-before.log`](flaky-repro-before.log)）：

| # | 命令 | 退出码 | passed | skipped | 失败用例 |
|---|---|---:|---:|---:|---|
| 1 | 全仓（诊断后） | 0 | **682** | 6 | 无 |
| 2 | 全仓（诊断后） | 0 | **682** | 6 | 无 |
| 3 | 全仓（诊断后） | 0 | **682** | 6 | 无 |
| 4 | 全仓（诊断后） | 0 | **682** | 6 | 无 |
| 5 | 全仓（诊断后） | 0 | **682** | 6 | 无 |
| 6 | 全仓（诊断后） | 0 | **682** | 6 | 无 |
| 1–6 | 全仓（诊断前，同环境） | 0 ×6 | **681** | 6 | 无 |

**skip 明细（每轮相同，6 条全部来自既有 `tests/network`）**：`test_connection_tester.py:106`、`test_transport_tls.py:39`、`:47`、`:62`、`:69`、`:83`，原因均为 `openssl unavailable`（既有环境 skip，与本 Task 无关）。**本 Task 未新增任何 skip、未放宽任何断言。**

## 5. 越界发现（只登记，未修改）

| ID | 级别 | 位置 | 内容 | 建议 |
|---|---|---|---|---|
| **N-1** | P2（生产行为，越界） | `src/ui/viewmodels/export/viewmodel.py:380/389`、`:392/398` | `_running = False` 先于 `_status`／终态信号发布，构成"半发布"窗口——这是导出用例 flaky 的**机制根因**。本 Task 已用测试侧等终态信号消除竞态等待，但生产侧同序发布仍在（其他消费者同样可能观察到半发布状态） | 由后续切片（需 `src/ui/**` 范围批准）把 `_status`/信号发布提前，或让 `running` 在发布后再清；本 Task 不动 `src/` |
| **N-2** | P3（诊断口径） | `tests/reading_export/test_qml_contract.py` | webtoon 保存 flaky 的**真实原因未确定**（12 次全仓未复现）。三条候选：事件循环被拖慢、`onContentYChanged` 的 `restart()` 被后续变化持续推迟、`active` 在该时刻为假。已交付的轨迹会在复现时区分它们 | 下次复现时用 `pump_traced` 轨迹 + `webtoon_save_diagnostics` 判定；若确系 QML 侧需改动，另立带 `src/ui/qml` 范围的切片 |
| **N-3** | P3（AC ① 前置） | `inpaint.route_policy` 设置语义 | 仓库无权威声明（`doc/contracts/**`、D01–D08 均无该键契约），AC ① 第 2 步的"统一语义"必须先由 Codex 裁决 | 见 [`route-policy-decision-request.md`](route-policy-decision-request.md) §7 的回填模板 |

## 6. 环境与命令

环境：Windows 11 `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`PYTHONDONTWRITEBYTECODE=1`；未设置 `QT_QPA_PLATFORM`（渲染/阅读套件按产品边界使用默认 Windows 平台）；全部 `-p no:cacheprovider`。

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$py = "G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe"
& $py -m pytest tests/providers tests/core tests/reading_export -q -p no:cacheprovider -rs   # 193 passed / 0 skipped
& $py -m pytest tests/providers tests/editing -q -p no:cacheprovider                          # 136 passed（AC ④ 顺序 A）
& $py -m pytest tests/editing tests/providers -q -p no:cacheprovider                          # 136 passed（AC ④ 顺序 B）
& $py -m pytest -q -p no:cacheprovider -rs                                                    # 682 passed / 6 skipped（×6）
```

## 7. 边界与合规

- Owner 改动（`c94c183..HEAD`）全部落在允许路径：`tests/**`、`doc/tasks/TASK-034.md`、`verification/TASK-034/**`；越界 **0**；`git diff --check b34b27e..HEAD` 退出码 0（[`changed-paths.txt`](changed-paths.txt)）。
- **`src/` 零改动**（AC ① 裁决前冻结）；未修改 Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、其他 Task、生产数据。
- 未 push、未合并 master；未释放任何冻结 Task（TASK-020～023、025～027、033 保持冻结/`proposed`）。
- 未放宽/删除既有断言语义，未新增 skip；两个 flaky 用例的断言与等待预算均未被弱化（导出用例只把"等待代理量"改为"等待断言所关心的终态信号"）。
