# HOST-CORE-1 验收矩阵

- Owner 实现 head：`4af86abb374cfccf92de07d4e5b975dfbaf0dd2b`
- 基线：`ed79b76f9191f0a5ebb6932a53a992a33a274041`
- 测试：`verification/HOST-CORE-1/pytest-tests-core.log`，`393 passed / 0 failed / exit 0`

| AC | 状态 | 实现与判别证据 |
|---|---|---|
| AC1 | PASS | `test_host_control_stdio_handshake_and_eof_revoke` 与 `test_new_core_process_has_a_new_session_and_no_old_import_grants` 经 Core 子进程 stdio 发送独立 `channel: "host-control"` envelope；验证 §5.7 v2.3 响应、握手与字段拒绝。HostControl 在普通 dispatcher 前分流。 |
| AC2 | PASS | `test_session_close_revokes_grants_and_restart_gets_a_fresh_registry` 断言 `CloseHostSession` 返回前 Import/Export ref 即变为 `REF_REVOKED`；`test_host_control_stdio_handshake_and_eof_revoke` 覆盖 EOF；`test_new_core_process_has_a_new_session_and_no_old_import_grants` 覆盖真实 Python Core 子进程重启后 session ID 改变、旧 import ref 为 `REF_UNKNOWN_ID`。 |
| AC3 | PASS | `test_host_control_routes_existing_register_and_revoke_seams` 覆盖四个既有 `_register_*` / `_revoke_*` seam；消费者成功解析原字段 ref，撤销后拒绝；重复撤销仍成功。未修改 ref DTO、签名输入或 `REF_*` 消费实现。 |
| AC4 | PASS | `test_three_host_only_rejections_do_not_call_seams_or_mutate_data` 覆盖 `HOST_ONLY_REQUIRED`、`HOST_SESSION_INVALID`（credential 缺失/错误、session closed）和 `CORE_SESSION_MISMATCH`；逐例断言 seam 调用为空、registry/SQLite/文件快照不变。详见 `ac4-denials.md`。 |
| AC5 | PASS | `test_host_only_commands_are_not_in_the_json_rpc_dispatcher` 对六个 HostControl command 逐项走普通 JSON-RPC，均得到 `HOST_ONLY_REQUIRED` 而非成功路由；详见 `ac5-dispatcher-negative.md`。 |
| AC6 | PASS | `scope-audit.md` 记录实现提交路径均在 `src/bootstrap/core_service.py` 与 `tests/core/**`；未改 `core_assembly.py`、契约、Schema、依赖或 `apps/**`。 |
| AC7 | PASS | task-env Python 3.12.3 完整运行 `pytest tests/core -q`：`393 passed / 0 failed`，唯一 warning 为既有 Pillow `Image.getdata` 弃用提示；原始日志含命令、环境和退出码。 |
| AC8 | PARTIAL | 实现 head 已固定，Handoff 已提交；非作者 Review 与 Coordinator integration 尚未运行，不能标为 PASS。接收者与 Gate 见 Handoff。 |

## 保持范围的理由

`core_assembly.py` 已在每个 Core 实例装配 `ImportSourceGrantRegistry` 和 `ExportTargetGrantRegistry`；HostControl session/control state 放在 `CoreServiceServer` 即可，不需改变装配层。
