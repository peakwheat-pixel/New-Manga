---
task_id: TASK-013
reviewer: DeepSeek Harness
author: ZCode
base_commit: 46646d58b3f645fa30fe7e10fae050218f9c55bb
reviewed_head: da1daf11e65fdc80f20450bec1f5e87234b826c7
decision: approved
---

# Review：TASK-013 工作台任务进度交互（da1daf1）

Reviewer 非本变更作者（作者为 ZCode）。被审范围固定 `46646d5..da1daf1`；Handoff 提交 `7e50523` 在 `da1daf1` 之后（位于作者分支 `agent/zcode/TASK-013-workbench-task-progress`），**仅作证据引用**，不纳入代码审查。Review 期间只读访问，未修改生产代码或测试。

**接收方式**：Reviewer 独立 worktree `G:/CODEX/New Manga.worktrees/TASK-013-deepseek-review`，分支 `agent/deepseek/TASK-013-review`（基于 `da1daf1` 新建）。

## 范围与依据

**变更**：`git diff 46646d5 da1daf1` = 27 文件、`+3923/−30`。`git diff --check 46646d5 da1daf1 --` **退出码 0**（无空白错误）。

| 类别 | 路径 |
|---|---|
| 投影与模型 | `src/ui/models/tasks/{__init__,projection,page_list_model}.py`（`projection.py` 336 行） |
| 视图模型 | `src/ui/viewmodels/workbench/{__init__,run_controller,viewmodel}.py`（`viewmodel.py` 778 行、`run_controller.py` 129 行） |
| QML | `src/ui/qml/workbench/**`（新增 6 个 + 改 `WorkbenchView.qml`） |
| 测试 | `tests/workbench/**`（5 个测试模块 + helpers/conftest） |
| 文档 | `doc/tasks/TASK-013.md`、`verification/TASK-013/**`，另 4 个项目状态文档（见 R-002） |

**依据**：TASK-013 的 AC（含 AC-NFR-UI-001 AI 不阻塞 UI、AC-PAUSE-002 安全边界、AC-PROGRESS-003 点击当前页）；D05 §56/§60/§62；D06 §74（进度优先级）；TASK-011 的 `PipelineService.get_task_progress` 与 `PipelineRun` 标志契约。

**环境**：Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；**`QT_QPA_PLATFORM` 未设置**（默认 Windows Qt，未使用 offscreen）。

## 四项重点核对

### ① 投影与 `PipelineService.get_task_progress` 口径一致性 —— **PASS**

`src/ui/models/tasks/projection.py` 明确定位为"与调度器同优先级"的只读投影：模块 docstring 记录优先级序（`failed > processing > blocked > completed > …`），`:241` 处再次声明 *"Same precedence as PipelineService.get_task_progress (D06 §74)"*。

真正的保障在测试侧：`tests/workbench/test_projection.py` 的模块 docstring 写明其目的为 *"against the scheduler's own `get_task_progress` so the two can never [diverge]"*，并在 `:63` **直接调用官方实现** `service.get_task_progress(run.run_id)` 与投影结果对照。这一点很关键——口径一致性不是靠"抄一遍逻辑"，而是由**对官方实现的差分断言**守住；若 `PipelineService` 将来调整优先级，该测试会立刻失败。

### ② `run_controller.py` 跨线程标志写与 queued 信号 —— **PASS（含一处见 R-001）**

- **任务投递走信号而非直连**：`start()` 通过 `_startRequested`（`Signal(object)`）把 job 交给已 `moveToThread` 的 `_Worker.execute`。注释（`:50-53`）解释了为什么不能把 lambda 直连 `QThread.started`——`started` 虽在关联线程发出，但其接收者（`QThread` 实例）的线程亲和性是 GUI 线程，AutoConnection 会因此把槽调度回 GUI 线程执行，导致重活在 GUI 上跑。**该说明与 Qt 的连接语义一致**，处理方式正确。
- **完成回报是 queued**：worker 的 `finishedRun` / `crashed` 连接 GUI 侧槽（`:82-83`），跨线程自动排队，`_on_finished` / `_on_crashed` 在 GUI 线程执行并在其中 `shutdown()`——不会在 worker 线程销毁线程自身。
- **控制标志写不需要锁**：`request_pause` / `request_stop` 直接写 `run.pause_requested` / `run.cancel_requested`（`:88-94`），docstring（`:8-13`）给出的理由是：这是契约约定的标志写，**布尔写在同一进程内是原子的**，且执行器**只读**该标志（单写者），因此在安全边界轮询即可（AC-PAUSE-002）。该论证成立：CPython 下布尔属性赋值不会撕裂，且不存在读-改-写竞争。异常路径亦被兜住（`_Worker.execute` 的 `except Exception` 上报 `crashed`，不会静默杀掉线程）。
- **待改进**：`shutdown()` 在 `wait(wait_ms)` 超时后调用 `QThread.terminate()`（见 **R-001**）。

### ③ QML 零业务逻辑 —— **基本 PASS（一处边界见 R-003）**

- **不触库/不触文件**：`git grep -E 'sqlite|QSql|import infrastructure|repository'` 在 `src/ui/qml/workbench` **零命中**。
- **无业务规则**：所有状态、计数、页/区数据均来自 `workbenchViewModel` 的 context property；QML 侧只有布局、绑定与信号转发。
- **可接受的展示映射**：`TaskProgressPanel.qml` 的 `statusColor` / `statusGlyph`（英文状态 → 颜色/符号查表）与 `statusLabel`（运行状态 → 中文标签）属**呈现层枚举映射**，不涉及数据变换或规则判定；`PageListPanel.locatePage` 仅调用 `positionViewAtIndex` 做视图定位，属纯 UI 行为。
- **越界的一项**：`WorkbenchView.qml` 的 `stepPage(delta)` 不止转发，而是自己做了索引运算与**边界钳制**（`current + delta` 后夹到 `[0, count-1]`，再取 `pageIdAt`）→ 见 **R-003**。

### ④ 白名单外零改动 —— **不成立（4 个文件，见 R-002）**

TASK-013 白名单为 `src/ui/qml/workbench/**`、`src/ui/viewmodels/workbench/**`、`src/ui/models/tasks/**`、`tests/workbench/**`、`doc/tasks/TASK-013.md`、`doc/handoffs/TASK-013-*.md`、`verification/TASK-013/**`。实际 27 个变更文件中 **23 个在白名单内**，另 **4 个在白名单外**：`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/STATUS.md`、`doc/tasks/README.md`。内容为项目级状态登记（TASK-013 的释放/实施/交接），属 Integrator 常规动作，但**严格结论是"不是零改动"**，故如实记录为 R-002（与 TASK-011 / TASK-012 / TASK-030 为同类问题）。

## Findings

| ID | 级别 | 文件/行 | 触发条件 | 影响 | 复现证据 | 建议 | disposition |
|---|---|---|---|---|---|---|---|
| R-001 | P2 | `src/ui/viewmodels/workbench/run_controller.py:96-106`（`shutdown` 的 `terminate()` 分支） | worker 在 `wait(5000)` 内未退出（例如执行器长时间不回到安全边界） | `QThread.terminate()` 是**强杀**：线程会在任意指令处被终止，不执行清理。当前 TASK-011 的执行器为 **in-memory** seam，被强杀只会丢失内存状态，**尚不构成数据损坏**；但 `TASK-011.md` 明文要求"**不可用线程强杀破坏事务**"，而本文件把该能力保留在生产 UI 代码中——一旦 PipelineRun/StepRun/Candidate 接入 SQLite（TASK-011 R-003 已登记的后续切片），同一路径就可能打断写事务 | 阅读 `shutdown()`；对照 `doc/tasks/TASK-011.md` 的"共享Schema与DTO变更…不可用线程强杀破坏事务" | 超时后**不 kill**：记录诊断并放弃等待（进程退出时由运行时回收），或改为等待 `cancel_requested` 生效后的有限次轮询；若确需兜底，应在**确认执行器已处于安全边界**后才允许强杀。建议标注"接持久化前必须移除 `terminate()`" | open（非阻塞；接持久化前必须修复） |
| R-002 | P2 | `doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/STATUS.md`、`doc/tasks/README.md` | 任何按 Task 白名单过滤范围的人 | 4 个文件不在 TASK-013 `允许修改范围` 内，使"白名单外零改动"这一核对项**不成立**。内容是 TASK-013 的状态登记，无产品语义影响 | `git diff --name-status 46646d5 da1daf1` 列出这 4 个文件 | 与 TASK-011 / TASK-012 / TASK-030 的同类建议合并：由 Codex 在协作协议或 Task 模板中**显式授权**"状态类文档（`00_INDEX` / `12_ROADMAP` / `STATUS` / `tasks/README`）属所有 Task 的默认允许路径"，或改为由独立状态提交承载 | open（非阻塞） |
| R-003 | P2 | `src/ui/qml/workbench/WorkbenchView.qml:174`（`stepPage`） | 任何按 D05 §60"QML 无业务逻辑"逐行审查的人 | `stepPage` 注释自称"pure viewmodel round-trip"，但实际执行了索引运算与**边界钳制**（`current + delta` → 夹到 `[0, count-1]` → `pageIdAt`），属**视图侧计算**而非转发。功能正确、无数据风险，但与 D05 §60 的严格解读存在张力，且使该边界规则无法被 python 侧单元测试直接覆盖（现由 QML 测试覆盖） | 阅读 `stepPage` 函数体；对比同目录 `PageListPanel.locatePage`（纯定位，无计算） | 把"当前页 ± delta 并钳制到有效范围"下沉为 ViewModel 的一个 `Slot`（如 `stepPage(delta)`），QML 只做调用；`statusColor/statusGlyph/statusLabel` 若 Codex 采取严格口径，也可改为 ViewModel 提供的 role | open（非阻塞） |

**未发现 P0/P1 问题。** 三项 P2 分别是：一处**前向数据安全**风险（R-001，当前 in-memory 下无实际损坏）、一处白名单口径（R-002，内容恰当）、一处 QML 边界计算（R-003，功能正确）。**没有发现投影口径分歧、跨线程竞态或 QML 触碰数据库/文件的问题。**

## 验证

| 场景 | 命令 | 环境 / commit | 退出码 | passed | skipped | skip 原因 |
|---|---|---|---|---|---|---|
| 必需命令 | `…TASK-012-py312/python.exe -m pytest tests/workbench` | Windows 10.0.26200 / Python 3.12.3 / PySide6 6.11.2 / **默认 Windows Qt**（`QT_QPA_PLATFORM` 未设置）/ `da1daf1` | **0** | **50** | **0** | 无 skip（`-rs` 无输出） |
| 必查 whitespace | `git diff --check 46646d5 da1daf1 --` | 同上 | **0** | — | — | — |
| 范围核对 | `git diff --name-status 46646d5 da1daf1` | 同上 | — | 23 在白名单 / 4 在白名单外 | — | 见 R-002 |

**与作者证据对照**：`verification/TASK-013/windows-pytest-workbench.txt` 记录 `collected 50 items`，与 Reviewer 实测 **50 passed / 0 skipped** 一致。

**未执行项**：

| 项 | 状态 | 说明 |
|---|---|---|
| 全量回归 `pytest tests -q -rs` | **NOT_RUN（本次未复跑）** | Reviewer 依指令只复跑了 `tests/workbench`。作者证据 `windows-pytest-full-suite.txt` 记录 **465 passed, 0 skipped**——注意其中**无 skip**，而 Reviewer 主机 PATH **无 `openssl`**（本会话内多次确认），若复跑全量预计出现 6 项 `openssl unavailable` skip；该差异属**主机环境差异**，非实现问题 |
| 真实 AI 负载下的 UI 不阻塞（AC-NFR-UI-001） | **N/A（Mock 证据边界）** | 现证据为"执行器记录线程 + GUI 心跳存活"，只证明**编排层面**不阻塞 GUI；真实 OCR/翻译/修复负载与 GPU/性能门槛不在本 Task 范围，Mock 不能代替（作者亦如实声明） |
| 真实 OCR/翻译/Inpaint 质量、DPI 全档截图、性能 Benchmark | **N/A** | 本 Task 无 AI 产物与性能门槛；属 D07 Benchmark 与其他切片 |
| 生产 `Main.qml` 下的工作台可见性 | **NOT_RUN（BLOCKED）** | 见 R-1：`bootstrap/app.py` 未注册 `workbenchViewModel`，生产入口的工作台仍显示空状态 |
| 跨一级页面的 Dirty 拦截（离开工作台时） | **NOT_RUN** | 需 AppShell/NavigationService 配合，超出本 Task 白名单（作者登记为 R-2） |

## 三轴结论

**Spec**：AC-PAUSE-002（暂停安全边界）、AC-PROGRESS-003（点击当前页定位）、AC-NFR-UI-001（AI 不阻塞 UI，编排层证据）与 D06 §74 的进度优先级均有对应实现与测试；进度口径以**对官方 `get_task_progress` 的差分断言**守护，是本切片最扎实的一处设计。范围声明诚实：未实现"选择作品/章节"悬浮窗（`workbenchPickContext` 保持 disabled，上下文经 `setContext` 注入）、跨页 Dirty 拦截与生产装配均明确登记为遗留。**四项重点中 ①②③ 成立，④ 不成立（R-002）。**

**Architecture**：分层正确——`src/ui/models/tasks/projection.py` 是纯 python 的只读投影（无 Qt 依赖假设），`src/ui/viewmodels/workbench/**` 通过 context property 单向供给 QML，QML **零库/零文件访问**；长任务通过 `QThread` + queued signal 移出 GUI 线程，控制面以契约标志（`pause_requested` / `cancel_requested`）表达，符合 TASK-011 的执行器边界设计。依赖注入采用 duck-typed seam（`list_pages` / `list_regions` / `get_region` / `save_manual_translation`），把"生产绑哪个实现"留给装配决策，边界克制。唯一架构级隐患是 `terminate()`（R-001）与 QML 侧的计算（R-003）。

**Verification**：必需命令 `pytest tests/workbench` 在指定任务环境、默认 Windows Qt 平台下 **50 passed / 0 skipped**，与作者证据一致；`git diff --check` 退出码 0。**passed 与 skipped 已分列**；本命令**无 skip 项**。全量未复跑（NOT_RUN）并已说明预计的环境差异。当前证据能证明"编排层不阻塞 GUI"，**不能**证明真实 AI 负载下的响应性或 AI 质量——本报告不作此类外推。

## R-1 生产装配接线范围的裁决

**Handoff 提供的 R-1**：`bootstrap/app.py` 未注册 `workbenchViewModel`（bootstrap 不在 TASK-013 白名单），因此生产 `Main.qml` 的工作台仍显示空状态；测试已证明"有/无 vm"两种形态行为均正确。

**Reviewer 建议：接受当前未接线的状态，由 Codex 在独立的最小装配切片中完成接线，不要并入本 Task 的 reviewed head。** 理由与范围：

1. **作者未越界是正确的**。`src/bootstrap/app.py` 确实不在 TASK-013 白名单，且 TASK-030 刚刚确立了唯一装配点（`assemble_services` / `assemble_engine`）。在 TASK-013 里就地改 bootstrap 会同时破坏两个 Task 的白名单与本切片的批准边界。
2. **接线应扩展 TASK-030 的装配点**，最小范围为：`src/bootstrap/app.py` 增加 `WorkbenchViewModel` 的构造与 `setContextProperty("workbenchViewModel", …)`；`src/ui/qml/AppShell`/`Main.qml` 无需改动（`WorkbenchView` 已在 AppShell 内）。预估与 TASK-030 对 bookshelf 的处理同构。
3. **接线前必须先确认 seam 的具体绑定**：`WorkbenchViewModel` 的依赖是 duck-typed 的 `list_pages` / `list_regions` / `get_region` / `save_manual_translation`。请 Codex 明确生产实现来自哪一处（SQLite library adapter / Region 仓储 / 翻译编辑用例），否则会重演 TASK-030 Review 中提示的"接上了但功能不可用"的假可见性。**这是本次裁决的前置条件。**
4. **验收门槛建议**：接线后应能在生产入口（`python -m bootstrap.app`）看到工作台的真实面板，并以 `pytest tests/workbench` 与全量回归作为证据；同时把 R-001（`terminate()`）在接持久化前关闭——因为接线会让工作台真正开始驱动长任务。

## 结论与复审

**`da1daf1` 可交 Codex 集成：decision = approved。**

- 四项重点：投影口径一致性 **PASS**（有官方差分测试）、跨线程与 queued 信号 **PASS**（`terminate()` 见 R-001）、QML 零业务逻辑 **基本 PASS**（`stepPage` 见 R-003）、白名单外零改动 **不成立**（4 个状态文档，见 R-002）。
- 无 P0/P1；R-001~R-003 均为 P2，可在集成前后的提交中关闭，**不需新的 reviewed head**。
- **本报告不包含任何 `integration_commit`**：被审 head 未合入主线，Handoff 亦未提供该值。该值只能由 Codex 在集成动作完成后填写，不得由本报告虚构。

**集成时须由 Codex 完成**：①核对 `da1daf1` 为当前 head，按协议 §6.6 集成并**由你填写 `integration_commit`**；②关闭 R-001（移除或限定 `terminate()`，并标注"接持久化前必须修复"）；③处置 R-002（状态文档授权口径）；④按本节建议决定 **R-1 接线范围**，并在接线前确认 duck-typed seam 的具体生产绑定；⑤处置 R-003（`stepPage` 下沉 ViewModel，可按严格口径一并处理展示映射）。

**剩余风险**：生产入口尚未注册 `workbenchViewModel`（R-1），工作台在生产 Main.qml 下不可见；真实 AI 负载下的 UI 响应性未被证明（Mock 证据边界）；`terminate()` 在接持久化后可能打断事务（R-001）；跨页 Dirty 拦截（作者 R-2）与"选择作品/章节"悬浮窗未实现，均属后续切片。本报告不释放 TASK-013 之外的任何 Task，未修改任何生产代码或测试。本报告事实仅适用于 `da1daf1`；分支后续变化（含 `7e50523`）不延用本批准。
