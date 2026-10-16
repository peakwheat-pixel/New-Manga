# AC4 — WebView 负向证据

运行环境：Windows PowerShell；分支 `codex/HOST-ISSUER-1-tauri-ref-issuer`；实现源码位于 `apps/desktop/src-tauri/**`，WebView 源码位于 `apps/desktop/frontend/src/**`。

扫描命令：

```powershell
$sensitive = 'OpenHostSession|RegisterImportSource|RevokeImportSource|RegisterExportTarget|RevokeExportTarget|CloseHostSession|HostControl|ImportSourceRef|ExportTargetRef|host_signature|target_ref|source_path|target_path|host_session_credential|signing_key'
rg -n -i $sensitive apps/desktop/frontend/src
# exit 1: no matches

$wire = 'ImportSourceRef|ExportTargetRef|host_signature|target_ref|source_path|target_path|host_session_credential|signing_key|OpenHostSession|RegisterImportSource|RevokeImportSource|RegisterExportTarget|RevokeExportTarget|CloseHostSession'
rg -n -i $wire apps/desktop/src-tauri/capabilities
# exit 1: no matches
```

结果：两次扫描均 exit `1`（ripgrep 的“无匹配”状态）。HostControl 六个操作名、ref、签名、文件路径和 credential 均未出现在 WebView 源码或 Tauri capability 声明中。Capability 只声明三个用户动作命令；其说明文字将 HostControl 标为 Rust stdio 内部通道。

实现级断言：`cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml host_` 中 `tests::host_control_operations_are_never_webview_commands` 与 `host_issuer::tests::webview_summaries_exclude_paths_and_refs` 通过。WebView 只得到导入计数/章节 ID或导出 ID/状态的摘要 DTO；Tauri 命令签名不接受路径，原生 picker 返回的路径仅在 Rust 函数内使用。

HostControl 独立 envelope 由 `StdioLibraryChannel` 写入它直接启动的 `bootstrap.core_service` 子进程 stdio；它不经过 `core_bridge` 的 resource-channel sidecar，也没有注册为 `#[tauri::command]`。
