# P19-AC3-1 事件面覆盖

| Core event | Tauri event | 输出字段 | 结论与证据 |
|---|---|---|---|
| `TaskFailed` | `core:TaskFailed` | `run_id,task_id,page_id?,error_code?` | PASS — 白名单内逐字段重建，未知类型/必需字段缺失时丢弃；apps/desktop/src-tauri/src/library_bridge.rs:778-809; apps/desktop/src-tauri/src/library_bridge.rs:769-872 |
| `RunPaused` | `core:RunPaused` | `run_id,status='paused'` | PASS — 白名单内逐字段重建，未知类型/必需字段缺失时丢弃；apps/desktop/src-tauri/src/library_bridge.rs:810-820; apps/desktop/src-tauri/src/library_bridge.rs:769-872 |
| `RunCompleted` | `core:RunCompleted` | `run_id,status∈{completed,completed_with_failures}` | PASS — 白名单内逐字段重建，未知类型/必需字段缺失时丢弃；apps/desktop/src-tauri/src/library_bridge.rs:821-831; apps/desktop/src-tauri/src/library_bridge.rs:769-872 |
| `CurrentPageStepChanged` | `core:CurrentPageStepChanged` | `run_id,current_page_id,current_step_type` | PASS — 白名单内逐字段重建，未知类型/必需字段缺失时丢弃；apps/desktop/src-tauri/src/library_bridge.rs:832-843; apps/desktop/src-tauri/src/library_bridge.rs:769-872 |
| `ExportProgressChanged` | `core:ExportProgressChanged` | `export_id,status,completed_pages,total_pages` | PASS — 白名单内逐字段重建，未知类型/必需字段缺失时丢弃；apps/desktop/src-tauri/src/library_bridge.rs:844-855; apps/desktop/src-tauri/src/library_bridge.rs:769-872 |
| `ReadingProgressChanged` | `core:ReadingProgressChanged` | `book_id,chapter_id,mode∈{original,translated}` | PASS — 白名单内逐字段重建，未知类型/必需字段缺失时丢弃；apps/desktop/src-tauri/src/library_bridge.rs:856-872; apps/desktop/src-tauri/src/library_bridge.rs:769-872 |

`credential_put` / `credential_clear` 没有事件；事件目录仅上述六种，credential request/result/error DTO 证据：apps/desktop/src-tauri/src/settings_bridge.rs:167-208、apps/desktop/src-tauri/src/settings_bridge.rs:287-349、apps/desktop/src-tauri/src/library_bridge.rs:756-763。Tauri emitter 只从该投影 sink 发出：apps/desktop/src-tauri/src/main.rs:1412-1424。

命令触发事件：Run 发起/控制/恢复/重试命令可以异步产生 Run 事件；`library_save_reading_progress` 产生 `ReadingProgressChanged`；导出开始/取消可产生 `ExportProgressChanged`。其他命令格为 N/A（无每命令事件），矩阵仍逐格登记。

观察到的 credential 明文、OS path、raw exception event counterexample：0。
