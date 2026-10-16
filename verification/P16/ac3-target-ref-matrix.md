# P16 AC3：ExportTargetRef 拒绝与原子消费判别

基线：`093430c75a46d28ed759ec646039bf2f55e3d429`。聚焦执行：
`python -m pytest tests/core/test_p16_reader_export.py -q`，12 passed，exit code 0；
原始 shell/解释器/命令/完整输出见 `verification/P16/pytest-p16.log`。

## 六类拒绝：每一项均无目标写入

参数化用例为 `test_export_target_ref_rejections_make_zero_target_writes`。每次调用前在隔离目录内创建包含 sentinel 字节的目标文件；拒绝后断言目标字节完全相同、目标同目录不存在 `.tmp`、原图与译图源文件逐字节不变、错误不含目标路径。

| 引用拒绝 | pytest 用例名 | 零目标写入断言 |
|---|---|---|
| `REF_MALFORMED` | `test_export_target_ref_rejections_make_zero_target_writes[malformed-REF_MALFORMED]` | PASS：目标 sentinel 不变、无临时文件、源文件不变。 |
| `REF_SIGNATURE_INVALID` | `test_export_target_ref_rejections_make_zero_target_writes[signature_invalid-REF_SIGNATURE_INVALID]` | PASS：目标 sentinel 不变、无临时文件、源文件不变。 |
| `REF_EXPIRED` | `test_export_target_ref_rejections_make_zero_target_writes[expired-REF_EXPIRED]` | PASS：目标 sentinel 不变、无临时文件、源文件不变。 |
| `REF_UNKNOWN_ID` | `test_export_target_ref_rejections_make_zero_target_writes[unknown_id-REF_UNKNOWN_ID]` | PASS：目标 sentinel 不变、无临时文件、源文件不变。 |
| `REF_REVOKED` | `test_export_target_ref_rejections_make_zero_target_writes[revoked-REF_REVOKED]` | PASS：目标 sentinel 不变、无临时文件、源文件不变。 |
| `REF_ALREADY_CONSUMED` | `test_export_target_ref_rejections_make_zero_target_writes[already_consumed-REF_ALREADY_CONSUMED]` | PASS：目标 sentinel 不变、无临时文件、源文件不变。 |

附加拒绝：`test_export_target_ref_scope_denial_and_atomic_concurrent_consumption` 验证 overwrite 禁止与 format 不匹配为 `REF_SCOPE_DENIED`；目标不变/不存在。

## 原子消费与成功后重放

- `test_export_target_ref_scope_denial_and_atomic_concurrent_consumption` 使用 12 个线程同时消费同一 ref：恰好 1 个结果为 `consumed`，其余 11 个均为 `REF_ALREADY_CONSUMED`；直接解析/消费阶段未创建目标。
- `test_replayed_ref_is_never_reconsumed_after_successful_export` 先完成 PNG 导出，再提交相同 `StartExport`：返回 `REF_ALREADY_CONSUMED`；已发布文件字节保持相同且无临时文件。
- `test_stale_abort_consumes_ref_and_continue_records_frozen_lineage` 验证 stale 拒绝也消费本次有效调用的 ref；重试需新 ref。
- 六拒绝、原子竞争、成功后重放全部由同一聚焦 pytest 命令执行：**exit code 0**。完整 Core 回归：`pytest tests/core -q`，352 passed、1 warning，**exit code 0**。

## 安全边界

Core 只从注册表解析已验证且绑定 session/format/单一目标/overwrite/expiry 的 opaque ref，再原子消费；不会将 `StartExport` 中的路径字符串解释为授权。文件写入使用同目录 staging file 与原子 replace，并对目标父目录及目标 entry 做安全复核。可信 host 的签发/注入不在 P16；见 `host-issuer-todo.md`。
