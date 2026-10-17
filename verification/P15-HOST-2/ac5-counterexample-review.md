# P15-HOST-2 AC5 反例覆盖

测试证据针对实际接入路径：Rust command 使用 `parse_credential_request` 完整解析 Tauri `Request`；解析错误经 `SettingsSurfaceError` 封闭投影；成功响应类型只有契约状态字段。命令本身不发送凭据事件。

| 反例 | 覆盖方式 | 证据 |
|---|---|---|
| WebView 请求夹带 `secret` | `deny_unknown_fields` 拒绝 put/clear 顶层未知字段；嵌套 `CredentialTarget` 夹带 `credential_ref` 也拒绝。错误投影不回显 marker。 | `settings_bridge::tests::credential_requests_reject_secret_and_reference_fields`；`rust-source-final.log` |
| WebView 响应泄露明文或 `CredentialRef` | put 仅序列化 `{"state":"configured"}`，clear 仅 `{"state":"missing"}`；不输出可选 hint。 | `settings_bridge::tests::credential_results_expose_only_contract_state`；`rust-source-final.log` |
| 错误/投影泄露引用或 Core 明文 | Core 的 `credential_ref` 额外字段无法通过封闭投影；错误响应只保留固定枚举值，不能带任意错误文本。 | `settings_bridge::tests::closed_projection_rejects_credential_refs_and_projects_only_safe_errors`；`settings_bridge::tests::credential_requests_reject_secret_and_reference_fields` |
| `intent` 与当前状态不匹配 | `credential_put` 在打开安全输入前检查一次，提交前再检查；不匹配返回 `conflict`。同进程 put/clear 由互斥锁串行化。 | `settings_bridge::tests::credential_intent_conflicts_before_any_input_or_binding_step`；`src/bootstrap` Core 对应的 `test_credential_replace_failure_preserves_old_binding_and_removes_new_ref` |
| replace 失败破坏旧绑定 | Core 反例在写新引用失败时断言旧引用和 profile 绑定都保留，并从 Core 凭据存储移除新引用。 | `tests/core/test_p15_core_settings.py::test_credential_replace_failure_preserves_old_binding_and_removes_new_ref`；`core-pytest-final.log` |
| clear 后回退到同 Provider 的其他 profile | Core 反例断言 resolver 仍指向被清除凭据的原 profile，且不会换到另一个 profile。 | `tests/core/test_p15_core_settings.py::test_cleared_provider_does_not_resolve_to_another_provider`；`core-pytest-final.log` |
| Provider/Proxy 引用越权或泄露 | Core 反例覆盖 owner 校验、只返回 configured/missing 状态、clear 移除关联；Proxy 反例验证引用按 network profile 隔离。 | `test_credential_binding_validates_owner_and_never_returns_reference`、`test_proxy_credential_binding_is_profile_scoped_and_secret_free`；`core-pytest-final.log` |
| 清除凭据时发出含凭据的事件 | `credential_put` / `credential_clear` 不发布事件；Tauri 回包仅走各自命令结果/错误投影。 | `apps/desktop/src-tauri/src/settings_bridge.rs` command body；无新增事件命令 |

执行结果：Rust source `103 passed / 0 failed / 1 ignored`；Core pytest `508 passed`。完整原始日志及退出码见同目录 `rust-source-final.log`、`core-pytest-final.log`。
