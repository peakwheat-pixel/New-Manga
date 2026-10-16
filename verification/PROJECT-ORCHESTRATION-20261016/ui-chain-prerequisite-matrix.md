# UI 链前置完整性矩阵（W1–W32 → host 命令面）

**生成**：2026-10-16，Coordinator dsh（epoch 6）。
**目的**：把设计基线 [AD001_FOUR_PAGE_UI_BASELINE.md](../../doc/design/AD001_FOUR_PAGE_UI_BASELINE.md) §6 的**每一条绑定**逐条映射到实际可用的 host 命令面，以回答一个问题：**UI 链（P14 工作台 / P17 阅读器 / P15 设置）是否还有未登记的"契约已冻结但 WebView 不可达"缺口？**

**背景**：该核对已被**三次**证实必要——同一根因（设计 §6 只核"契约是否冻结"，未核"host 是否已有出口"）先后暴露 **RUN-IPC-1**（Run 控制面）、**EXPORT-IPC-1**（导出控制/查询面）、**READER-IPC-1**（阅读器投影面）。据此它已升级为**释放任何 UI Task 前的强制前置步骤**（BACKLOG **BL-14**）。

## 结论

**没有第四处缺口。** 全部 32 条 W 行与 G20 均已由下述四类之一覆盖。UI 链的**全部剩余前置**就是四个已释放/在飞 Task：`RUN-IPC-1`、`EXPORT-IPC-1`、`READER-IPC-1`、`EXPORT-REVEAL-1`。

## 页面归属与 P14/P17 边界裁决（2026-10-16，Coordinator）

DAG 中 **P17 的任务名为「阅读导出UI」**，而设计 §6 W 表把**导出的 W21–W25 与缺口 G20 绑定到「工作台」**、把 **W18–W20 绑定到「阅读器」** → 存在**同一导出面板被两个 Task 重复实现（或都漏做）**的风险。为避免该风险，按设计 §6 的**页面列**（冻结权威）裁决如下，并将在两个 Task 文件中各自冻结：

| Task | 交付页面 | 覆盖绑定 | 明确排除 |
|---|---|---|---|
| **P14 工作台** | 设计 **§3** | W5–W17、**W21–W25（导出面板）**、W30/W31、**G20 reveal 入口** | 阅读器页（§4） |
| **P17 阅读导出UI** | 设计 **§4** | **W18/W19/W20**（+ 消费既有 W2/W3 导航与 W5 页图通道） | **导出面板（W21–W25）与 G20 —— 归 P14，P17 不得重复实现** |

**依赖时序（据此修正）**：
- **P14 前置** = RUN-IPC-1（done）+ **EXPORT-IPC-1**（在飞）+ EXPORT-REVEAL-1（done）+ EVENTS-FWD-1（done）；
- **P17 前置** = **READER-IPC-1**（在飞）+ EVENTS-FWD-1（done，W20 事件）+ 既有 W2/W3/W5 命令。**P17 不依赖导出侧两个 Task**，故 READER-IPC-1 一关闭即可释放。
- P17 名称中的"导出"由其依赖 **P16 阅读导出 Core**（done）而来；**UI 归属以设计 §6 的页面列为准**。

## 逐条矩阵

| W | 页面 | 绑定 | 状态 | 落点 |
|---|---|---|---|---|
| W1 | Shell/书架 | `ListBooks` | ✅ 已有 | `library_list_books` |
| W2 | 书架/工作台 | `list_chapters` | ✅ 已有 | 生产命令 |
| W3 | 书架/工作台 | `list_chapter_pages` | ✅ 已有 | 生产命令 |
| W4 | 书架/工作台 | `ImportPages` | ✅ 已有 | `library_import_file` / `library_import_folder`（HOST-ISSUER-1） |
| W5 | 工作台 | `ResolvePageResource` | ✅ 已有 | `resolve_page_resource` |
| W6 | 工作台 | `ListRegions` | ✅ 已有 | `list_regions` |
| W7 | 工作台 | `SetRegionType` | ✅ 已有 | `set_region_type` |
| W8 | 工作台 | `list_region_revisions` | ✅ 已有 | 生产命令 |
| W9 | 工作台 | `restore_region_revision` | ✅ 已有 | 生产命令 |
| W10 | 工作台 | `rerender_page` | ✅ 已有 | 生产命令 |
| W11 | 工作台 | `StartRun` | ⏳ **RUN-IPC-1** | `library_start_run` |
| W12 | 工作台 | `ControlRun` | ⏳ **RUN-IPC-1** | `library_control_run` |
| W13 | 工作台 | `ResumeBlockedRun` | ⏳ **RUN-IPC-1** | `library_resume_blocked_run` |
| W14 | 工作台 | `GetRunSnapshot` | ⏳ **RUN-IPC-1** | `library_get_run_snapshot` |
| W15 | 工作台 | `GetTaskProjection` | ⏳ **RUN-IPC-1** | `library_get_task_projection` |
| W16 | 工作台 | `RetryFailedTargets` | ⏳ **RUN-IPC-1** | `library_retry_failed_targets` |
| W17 | 工作台 | 4 类 Run 事件 | ✅ **EVENTS-FWD-1 done** | `core:TaskFailed` / `RunPaused` / `RunCompleted` / `CurrentPageStepChanged` |
| W18 | 阅读器 | `GetReaderProjection` | ⏳ **READER-IPC-1** | `library_get_reader_projection` |
| W19 | 阅读器 | `SaveReadingProgress` | ⏳ **READER-IPC-1** | `library_save_reading_progress` |
| W20 | 阅读器 | `ReadingProgressChanged` | ✅ **EVENTS-FWD-1 done** | `core:ReadingProgressChanged` |
| W21 | 工作台 | `StartExport` | ✅ 已有 | `library_start_export`（HOST-ISSUER-1） |
| W22 | 工作台 | `CancelExport` | ⏳ **EXPORT-IPC-1** | `library_cancel_export`（去路径投影） |
| W23 | 工作台 | `GetExportSnapshot` | ⏳ **EXPORT-IPC-1** | `library_get_export_snapshot`（去路径投影） |
| W24 | 工作台 | `GetExportHistory` | ⏳ **EXPORT-IPC-1** | `library_get_export_history`（**必须剔除 `output_path`**，§5 行 164 + §10.3 L853） |
| W25 | 工作台 | `ExportProgressChanged` | ✅ **EVENTS-FWD-1 done** | `core:ExportProgressChanged` |
| W26 | 设置 | `settings_get` | ✅ 已有 | 生产命令 |
| W27 | 设置 | `settings_update_section` | ✅ 已有 | 生产命令 |
| W28 | 全部页 | §8 `ErrorEnvelope` | ✅ 已有 | 错误语义（无需命令） |
| W29 | 全部页 | §5.2 UI-local actions | ✅ 已有 | 无 wire（本地行为） |
| W30 | 书架/工作台 | `library_import_file` / `library_import_folder` | ✅ 已有 | HOST-ISSUER-1 交付 |
| W31 | 工作台 | `library_start_export` | ✅ 已有 | HOST-ISSUER-1 交付 |
| W32 | 全部页 | host-only 边界单测 | ✅ 已有 | `host_control_operations_are_never_webview_commands` |

**另计**：设计 §7 的 **G20**（导出后"打开所在文件夹"）由 **EXPORT-REVEAL-1** 交付（`library_reveal_export_folder`，已 Review approved，待集成）。

## 命令面总量（集成四个 Task 后）

当前 18 条 + RUN-IPC-1 的 6 条 + EXPORT-IPC-1 的 3 条 + READER-IPC-1 的 2 条 + EXPORT-REVEAL-1 的 1 条 = **30 条生产命令**（probe/AC1 面保持冻结的 7/6 形状不变）。

## 未纳入本矩阵的设计 §7 缺口（非本任务范围，仍需独立裁决/契约）

`G1–G5`（书架聚合/详情）、`G13`（revision pin，PROPOSAL）、`G18`（缩略图，需契约）、`G21–G25`（设置/Provider/凭据/网络/分段 schema，**P15 前置**）、`G26`（导入细分进度，PROPOSAL）。这些**不是"host 无出口"型**缺口，而是**契约/产品缺口**，须走契约修订或用户裁决，不得以本矩阵替代。
