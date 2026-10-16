# AC4-③：frozen bundle 导出后 Reveal 往返

**结果：BLOCKED（真实 GUI reveal 未运行）**

`apps/desktop/src-tauri/target/core-sidecar` 是指向 `G:/CODEX/New Manga/apps/desktop/src-tauri/target/core-sidecar` 的 Junction；本 Task 未删除、替换或重建该 Junction。

已在该 frozen bundle 上运行 packaged Rust 测试：

```powershell
$env:M2RC1_PACKAGED='1'
Remove-Item Env:M2RC1_SRC_ROOT -ErrorAction SilentlyContinue
Remove-Item Env:M2RC1_PYTHON -ErrorAction SilentlyContinue
cargo test --bin m2rc1-desktop packaged_sidecar_tests -- --test-threads=1
```

原始日志为 [`rust-packaged.log`](rust-packaged.log)：8 passed，0 failed，exit code 0。另以 `--nocapture` 单独运行既有 `host_export_grant_round_trip_reaches_frozen_start_export`，原始输出见 [`frozen-export-attempt.log`](frozen-export-attempt.log)：它确认 bundle SHA256 为 `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842`、grant 注册被接受，但因测试 fixture 使用 `missing-book`，Core 返回 `TARGET_NOT_FOUND` 且目标文件未写入。故没有成功导出可供 reveal，也没有调用系统文件管理器；这些 bundle 检查不作为导出后 Reveal 端到端证据。

真实 GUI e2e 受无头 Windows 限制，当前环境证据见 [`checkpoint-r9.md`](../PROJECT-ORCHESTRATION-20261016/checkpoint-r9.md#L45-L46)：WebView2 无法取得窗口句柄，错误码 `0x80070578`，GUI e2e runner 无法运行。缺失段是“从真实 UI 完成导出 → 调用 `library_reveal_export_folder` → 观察系统文件管理器打开目标目录”。本 Task 未声称发生过打开动作。
