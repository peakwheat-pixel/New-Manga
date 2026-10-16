# AC2：Host session 生命周期

| 场景 | 判别用例与断言 |
|---|---|
| 首次握手与 Core session ID | `test_host_control_stdio_handshake_and_eof_revoke`：`OpenHostSession` 返回当前 Core 的 `core_session_id`，响应版本为 2.3；`test_open_host_session_accepts_canonical_base64url_padding` 覆盖 32-byte credential 的规范带填充与无填充形式。 |
| 显式关闭即时撤销 | `test_session_close_revokes_grants_and_restart_gets_a_fresh_registry`：`CloseHostSession` 返回 `{closed: true}` 后，既有 `ImportSourceRef` 的 `resolve_many` 立即报 `REF_REVOKED`，既有 `ExportTargetRef` 的 `resolve_and_consume` 立即报 `REF_REVOKED`；源文件和既有目标哨兵字节、磁盘快照不变。 |
| 同一 Core 不接受 session 轮换 | 同一用例在关闭后再次 `OpenHostSession`，断言 `HOST_SESSION_ALREADY_OPENED`。Host 轮换必须关闭并重启 Core。 |
| direct-child stdio 断开 | `test_host_control_stdio_handshake_and_eof_revoke`：完成 stdio 注册后让输入 EOF，`serve_forever` 返回 0，session credential 清空，grant 立即进入 revoked 状态。 |
| 真实 Core 子进程重启 | `test_new_core_process_has_a_new_session_and_no_old_import_grants`：启动两次 `python -m bootstrap.core_service` 子进程；第二次 session ID 与第一次不同，第一次签发/注册的 import ref 返回 `REF_UNKNOWN_ID`。测试确认 stdout/stderr 不包含 credential 或来源绝对路径。 |

完整测试结果：`395 passed / 0 failed / exit 0`，原始输出见 `pytest-tests-core.log`。
