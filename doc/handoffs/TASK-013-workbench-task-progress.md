---
task_id: TASK-013
author: ZCode
recipient: DeepSeek Harness（独立 Review）→ Codex（集成）
base_commit: 46646d58b3f645fa30fe7e10fae050218f9c55bb
delivery_head: da1daf1
status: integrated
---

# Handoff：TASK-013 实现工作台与任务进度交互

## 交付结果

Owner=ZCode 在固定 base `46646d5` 之上交付工作台切片，实现 commit `da1daf1`（分支 `agent/zcode/TASK-013-workbench-task-progress`，worktree `G:/CODEX/New Manga.worktrees/TASK-013-zcode`）。Codex 已以 `32a1eb5` 合并实现、以 `f0814a8` 合并独立 Review 报告，并完成 R-001/R-003 修正与集成验证。提交列表：

- `da1daf1` feat(TASK-013): workbench task progress interaction（唯一实现提交；23 文件，+3901/−11）
  - 新增 `src/ui/models/tasks/`：`projection.py`（TaskProjection 单一投影）、`page_list_model.py`（WorkbenchPageListModel）
  - 新增 `src/ui/viewmodels/workbench/`：`viewmodel.py`（WorkbenchViewModel）、`run_controller.py`（QThread worker 执行）
  - 重写/新增 `src/ui/qml/workbench/`：`WorkbenchView.qml`（重写，保留 TASK-012 空状态语义）、`WorkbenchToolbar.qml`、`PageListPanel.qml`、`ViewerPanel.qml`、`RegionInspector.qml`、`TaskProgressPanel.qml`、`DirtyConfirmDialog.qml`
  - 新增 `tests/workbench/`（50 项测试）与 `verification/TASK-013/`（Windows 验证输出）
  - 更新 `doc/tasks/TASK-013.md`（executed 记录）

### 架构要点（Review 入口）

1. **同一进度投影（AC-PROGRESS-007 / D06 §79）**：`build_projection(run, page_meta)` 是唯一投影构造点；PageList 行与 TaskProgressPanel 字段都从同一个 `TaskProjection` 实例填充。页分类优先级（failed > processing > blocked > completed > skipped > waiting）与 `PipelineService.get_task_progress` 同规则，`test_counts_match_scheduler_projection` 逐项断言两口径一致。百分比用 terminal/planned step units（D06 §75），不使用完成页/总页。
2. **UI 不冻结（AC-NFR-UI-001）**：`RunController` 用 QThread + worker QObject 执行同步的 `PipelineService.execute_run`。注意一个 PySide6 陷阱（测试已固化）：把 lambda 直连 `QThread.started` 会在**主线程**执行（functor 连接以 sender 的 thread affinity 做 queued），因此启动请求经 `_startRequested = Signal(object)` queued 投递到 worker 事件循环。暂停/停止是执行器在安全边界检查的布尔标志写（AC-PAUSE-002 语义）。
3. **节流与即时反馈（AC-NFR-UI-002 / AC-PAUSE-001）**：运行期间 UI 侧 250 ms QTimer 轮询重建投影（约 4 Hz）；runFinished 等关键事件立即刷新、暂停点击同步翻转 `pausing` 乐观状态（测试断言 ≤200 ms）。
4. **Viewer 当前页与 Pipeline 焦点分离（D05 §18.3）**：`viewerPageId` 是独立状态；投影的 `current_page_id`（Primary Focus = 第一个 running task）来自 run。点击统计 → `filterByStatus` 筛选 PageList；点击当前页 → `pageLocateRequested` 信号驱动滚动定位。
5. **Dirty 导航保护（D05 §55）**：Inspector 译文编辑自动 dirty；切 Page/Region 时发 `inspectorDirtyConfirmRequested`，QML 弹保存/放弃/取消三键对话框，`resolveDirtyConfirm(action)` 恢复导航。
6. **TASK-012 兼容**：无 `workbenchViewModel` context property 时 WorkbenchView 保持 D05 §62 空状态，`workbenchPickContext` 恒为 disabled——`tests/ui_shell/test_qml_shell.py::test_workbench_and_reader_are_honest_skeletons` 不受影响（全量回归已验证）。
7. **依赖注入 seam**：page catalog / region catalog / translation editor 为 duck-typed 构造参数（`list_pages`、`list_regions/get_region`、`save_manual_translation`）；生产绑定属 bootstrap 装配决策，不在本切片内发明。

### AC 对照

| AC | 结论 | 载体 |
|---|---|---|
| AC-PAGE-002 单选/Ctrl/Shift 多选（限当前章节） | 实现 | `selectPage/togglePageSelected/selectRangeTo` + PageListPanel TapHandler 修饰键；QML 端到端覆盖 |
| AC-PAGE-003 Page 状态六分类 | 实现 | 投影 status role（waiting/processing/completed/failed/skipped/blocked）+ isLocked overlay（已锁定为修饰，不替代运行分类） |
| AC-PROGRESS-001 固定底部面板 | 实现 | TaskProgressPanel 固定于 WorkbenchView 底部布局，非弹窗；无 run 时显示"当前无运行任务"（D05 §62） |
| AC-PROGRESS-002 显示内容 | 实现 | 任务名/百分比/step flow/当前页/完成/失败/阻塞(原因)/跳过/等待 + 暂停/停止/继续（QVariantMap 全字段见 `get_task_progress`） |
| AC-PROGRESS-003 当前 Page 定位 | 实现 | 点击当前页 → `pageLocateRequested` → ListView `positionViewAtIndex` |
| AC-PROGRESS-004 失败统计联动 | 实现 | `filterByStatus("failed")` → PageList 仅剩失败行（viewmodel + QML 两级测试） |
| AC-PROGRESS-005 完成/跳过统计联动 | 实现 | 同上，completed/skipped 筛选 |
| AC-PROGRESS-006 CompletedWithFailures | 实现 | 38 成功 + 2 失败 → `completed_with_failures`、`can_retry_failed`，整体不判失败 |
| AC-PROGRESS-007 PageList 同源 | 实现 | 单一投影构造点 + 与 `get_task_progress` 口径一致性测试 |
| AC-NFR-UI-001 AI 不阻塞 UI | Mock 证据 | execute_run 在非 GUI 线程逐步执行（executor 记录线程）+ GUI 心跳存活 + 运行中切页不阻塞；真实 AI 负载不在 Mock 范围 |
| AC-NFR-UI-002 Progress 节流 ~4 Hz | 实现 | 250 ms 刷新间隔常量断言 + 1 秒窗口刷新次数上限测试 |
| Dirty 导航不丢编辑（Task AC 3） | 实现 | dirty 确认对话框（保存/放弃/取消）拦截 Page/Region 切换；取消保持现场，保存走 editor seam |
| 暂停/停止/继续按钮匹配（D06 §103/D05 §32） | 实现 | 投影 can_pause/stop/continue/restart/abandon/retry 矩阵，9 种 run 状态单测 + QML 终态断言 |

### 范围边界（诚实声明）

- **Region 编辑**本切片交付 Inspector 内 Region 列表、人工译文编辑（dirty/保存/放弃）、Lock 显示与 Region 级命令入口（ocr_region/retranslate_region/retranslate_region_full）；Region 几何画布编辑（AC-REGION-002 的画布交互）不在本切片。
- **Viewer** 交付 Original/Clean/Translated/Compare 四模式；Clean/Translated 在本切片无产物（渲染产物接入属后续渲染/管线集成切片），UI 显示诚实占位而非假图。
- **"选择作品和章节"悬浮窗**（D05 §62）未实现；`workbenchPickContext` 保持 disabled，上下文经 `setContext(book_id, chapter_id, ...)` 注入（生产接线为 bootstrap 装配决策，见"风险与遗留"）。
- 跨一级页面的 Dirty 拦截（离开工作台时）需 AppShell/NavigationService 配合，超出白名单，见遗留 R-2。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| tests/workbench 全套 | `python -m pytest tests/workbench` | Windows 10.0.26200 x64 / Python 3.12.3 / PySide6 6.11.2 / 默认 Windows Qt（未设 offscreen）/ commit `da1daf1` | **50 passed, 0 skipped**，退出码 0 | verification/TASK-013/windows-pytest-workbench.txt |
| 全量回归（含 TASK-012 ui_shell、架构守卫） | `python -m pytest`（testpaths=tests） | 同上 / commit `da1daf1` | **465 passed, 0 skipped**，退出码 0 | verification/TASK-013/windows-pytest-full-suite.txt |
| 集成后 workbench 回归 | `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/workbench -v` | 主线 `integration_commit=f0814a8` 后 Codex R-001/R-003 修正版 | **51 passed, 0 skipped**，退出码 0 | verification/TASK-013/integration-f0814a8.md |
| 集成后全量回归 | `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests -q -rs` | 同上；默认 Windows Qt | **460 passed, 6 skipped**，退出码 0；6 项均因 `openssl unavailable` | verification/TASK-013/integration-f0814a8.md |
| AC-PROGRESS-006（38+2） | `test_completed_with_failures_is_not_total_failure` | 同上 | PASS | 同 workbench 输出 |
| AC-PROGRESS-004/005 统计联动 | `test_failure_statistic_filters_pagelist`、`test_statistic_click_filters_pagelist_through_qml` | 同上 | PASS | 同上 |
| AC-NFR-UI-001 Mock 不冻结 | `test_execute_run_runs_off_the_gui_thread`、`test_gui_thread_stays_alive_during_run`、`test_page_switch_remains_possible_while_run_active` | 同上 | PASS（Mock 证据） | 同上 |
| AC-PAUSE-001 ≤200 ms 暂停反馈 | `test_pause_shows_optimistic_feedback_immediately`（乐观翻转计时断言） | 同上 | PASS | 同上 |
| 暂停→继续→完成全链 | 同上测试（paused 后 continueRun 至 completed） | 同上 | PASS | 同上 |
| AC-STOP 保留已提交成果 | `test_stop_cancels_running_job`（≥1 页 commit 后停止，cancelled 且计数保留） | 同上 | PASS | 同上 |
| Dirty 保护（保存/放弃/取消） | `test_dirty_navigation_guard_intercepts_page_switch`、`test_dirty_navigation_discard_switches`、QML `test_dirty_confirm_dialog_blocks_and_resumes` | 同上 | PASS | 同上 |
| TASK-012 空骨架兼容 | `test_no_viewmodel_keeps_honest_empty_state` + 主线 `tests/ui_shell` 全套 | 同上 | PASS | 全量输出 |

未运行项与原因：真实 OCR/翻译/修复质量、GPU/性能 Benchmark、DPI 全档截图——本 Task 无 AI 产物与性能门槛，Mock 不能也不试图代替（D08 L15；性能数值属 D07 Benchmark 范围）。`pytest tests/workbench` 无 skip 项，无需逐项 skip 原因。

## 接收方式

- 分支/工作区：`agent/zcode/TASK-013-workbench-task-progress` @ `G:/CODEX/New Manga.worktrees/TASK-013-zcode`；被审范围 `46646d5..da1daf1`。
- 复现：`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/workbench`（Windows 默认 Qt，不设 offscreen）。
- 手动体验（可选）：测试外可用 `python -c` 构造 `make_vm`（tests/workbench/workbench_helpers.py）后按 TASK-012 模式注入 `workbenchViewModel` context property 加载 `src/ui/qml/workbench/WorkbenchView.qml`；生产 Main.qml 接线尚未存在（见遗留）。
- Reviewer（DeepSeek Harness）建议检查点：投影与 `PipelineService.get_task_progress` 的口径一致性；`run_controller.py` 的跨线程标志写（pause_requested/cancel_requested）与 queued 信号用法；QML 是否零业务逻辑（D05 §60）；白名单外零改动。
- 下一步：R-1 仅在完整生产 Pipeline seam 就绪并由 Codex 固定新 base 后，按独立装配切片执行；当前不接线、不释放 TASK-015 或其他冻结 Task。

## 风险与遗留

- **R-1 生产装配未接线（BLOCKED/NOT_RUN）**：页面、Region、人工译文编辑 seam 已存在，但完整生产 Pipeline catalog/store/snapshot/executor 尚未就绪；不得把内存实现注入生产。独立装配切片范围与门槛见 [r1-assembly-decision.md](../../verification/TASK-013/r1-assembly-decision.md)。
- **R-2 跨一级页面 Dirty 拦截**：离开工作台（导航到书架/设置）时不拦截 dirty 编辑，拦截点需 AppShell/NavigationService 参与，超出白名单。工作台内部 Page/Region 切换已受保护。关联后续装配/导航切片。
- **R-3 进度为轮询投影**：运行中进度靠 250 ms 轮询 run 对象重建投影（GIL 下布尔/引用读取安全；UI 读到短暂中间态由下一轮修正）。这是同步 `execute_run` 契约下的刻意取舍；若后续引入分步事件流，可替换为推送式刷新，接口不变。
- **R-4 缩略图为占位**：PageList tile 与 Viewer 原图占位/图像按 managed_original_ref 解析；异步缩略图加载与 Webtoon 长图策略（D05 §65）属渲染/性能切片。
- **R-5 线程模型前提**：`RunController` 同时只承载一个 run（重复 start 抛错），与 TASK-011 串行调度一致；并发 Run 队列属后续任务管理切片。

## Codex 集成收口

- `implementation_merge=32a1eb5`；`reviewed_head=da1daf11e65fdc80f20450bec1f5e87234b826c7`；`review_report_commit=9fbfa48`；`integration_commit=f0814a8`。
- R-001：移除 `terminate()`，暂停 run 不被 shutdown 误取消；接入持久化前仍需安全边界 shutdown 协议。
- R-002：四个全局状态/导航文档按 §3.6 由 Codex 回填，仅改元数据。
- R-003：`stepPage` 计算下沉至 ViewModel，QML 仅转发。
- 集成后：workbench **51 passed, 0 skipped**；全量 **460 passed, 6 skipped**；skip 原因均为 `openssl unavailable`。

## 实验附录（仅实验任务）

不适用（本 Task 为功能实现，无模型/数据实验）。
