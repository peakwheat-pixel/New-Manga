# AC5：普通 JSON-RPC 不路由 HostControl

判别用例：`tests/core/test_host_control.py::test_host_only_commands_are_not_in_the_json_rpc_dispatcher`。

| 普通 JSON-RPC `command` | 负向结果 |
|---|---|
| `OpenHostSession` | `HOST_ONLY_REQUIRED`, `result: null` |
| `RegisterImportSource` | `HOST_ONLY_REQUIRED`, `result: null` |
| `RevokeImportSource` | `HOST_ONLY_REQUIRED`, `result: null` |
| `RegisterExportTarget` | `HOST_ONLY_REQUIRED`, `result: null` |
| `RevokeExportTarget` | `HOST_ONLY_REQUIRED`, `result: null` |
| `CloseHostSession` | `HOST_ONLY_REQUIRED`, `result: null` |

`dispatch_request` 先将不带 `channel: "host-control"` 的保留命令拒绝，再进入普通命令 catalog；HostControl 不注册成普通 application command。AC4 用例进一步用 spy 证明普通 JSON-RPC 注册尝试没有调用 `_register_*` seam。该负向断言属于 `pytest tests/core -q` 的最终运行：`395 passed / 0 failed / exit code=0`。
