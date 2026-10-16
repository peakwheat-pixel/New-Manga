# AC5 — HostControl 拒绝码处理

Rust host 的 `decode_response` 将 Core 的拒绝错误原样保留为 `LibraryError.code/category/retryable`。新增 `library_bridge::tests::host_control_denial_codes_are_preserved_for_host_handling` 对三个响应逐项断言：

| Core error code | Host 接收结果 | Core 不调用 seam 的依据 |
|---|---|---|
| `HOST_ONLY_REQUIRED` | 保留 `code=HOST_ONLY_REQUIRED`, `category=validation`, `retryable=false` | `verification/HOST-CORE-1/ac5-dispatcher-negative.md`：普通 JSON-RPC 对六个 HostControl 操作均拒绝；`ac4-denials.md` 对应 `calls == []`、存储与文件快照不变 |
| `HOST_SESSION_INVALID` | 保留 `code=HOST_SESSION_INVALID`, `category=conflict`, `retryable=false` | `verification/HOST-CORE-1/ac4-denials.md`：缺失/错误 credential 和已关闭 session 均拒绝且 seam 未调用 |
| `CORE_SESSION_MISMATCH` | 保留 `code=CORE_SESSION_MISMATCH`, `category=conflict`, `retryable=false` | `verification/HOST-CORE-1/ac4-denials.md`：错绑 core session 拒绝且 seam 未调用 |

Rust 测试原始结果见 `cargo-test-host-unit.txt`（12 passed，包含三拒绝码断言）。Core 接收端无副作用断言来自已完成的 HOST-CORE-1，相关源测试为 `tests/core/test_host_control.py::test_three_host_only_rejections_do_not_call_seams_or_mutate_data`。

HostControl 操作不在 `command_allowlist`、Tauri `generate_handler!` 的 WebView 命令表或 capability 中。普通业务请求不会被 host 用来注册 grant；拒绝会作为 typed error 返回，不会重试成普通 JSON-RPC 操作。
