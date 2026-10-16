# AC4：拒绝码、未调用 seam 与零副作用

证据来自 `tests/core/test_host_control.py::test_three_host_only_rejections_do_not_call_seams_or_mutate_data`。测试将 `_register_import_source` 与 `_register_export_target` 替换为可观测 spy；每个拒绝断言 `calls == []`，并对比 SQLite `total_changes`、两个 registry 的 grant ID 集合，以及隔离目录内所有文件的 SHA-256 快照。

| 拒绝码 / category | 可证伪用例 | 未调用 seam 断言 | 零副作用断言 | pytest 结果 |
|---|---|---|---|---|
| `HOST_ONLY_REQUIRED` / `validation` | `test_three_host_only_rejections_do_not_call_seams_or_mutate_data[ordinary_json_rpc]` | `calls == []` | SQLite 变化 `0`；Import/Export registry 不变；磁盘文件 hash 快照不变 | 完整 Core suite `exit_code=0` |
| `HOST_SESSION_INVALID` / `conflict` | `...[credential_missing]`、`...[credential_wrong]`、`...[session_closed]` | 每例 `calls == []` | 每例 SQLite、registry、文件 hash 快照均不变 | 完整 Core suite `exit_code=0` |
| `CORE_SESSION_MISMATCH` / `conflict` | `...[core_session_mismatch]` | `calls == []` | SQLite 变化 `0`；Import/Export registry 不变；磁盘文件 hash 快照不变 | 完整 Core suite `exit_code=0` |

所有拒绝均返回 `result: null`，error message 不包含目标路径或 host credential。完整原始输出与统一退出码见 `pytest-tests-core.log`：`395 passed / 0 failed / exit 0`。
