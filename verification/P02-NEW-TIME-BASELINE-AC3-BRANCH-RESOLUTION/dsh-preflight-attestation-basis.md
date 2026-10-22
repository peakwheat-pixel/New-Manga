# DSH preflight attestation

- quota_status=OK：本会话中此前的 P02 bounded review 已成功完成；距本次派发很近，未观察到额度错误。
- permission_mode=OK：用户明确授权本自治 Task 的 ZCode 实现、DSH 独立 Review 与 Codex 集成；当前没有权限拒绝状态。
- conversation_usable=true：当前 DSH CLI 可运行，且本会话此前成功返回 Review 结果。
- DSH CLI version probe: dsh --version => 0.2.0-rc.2；headless help 可读。
