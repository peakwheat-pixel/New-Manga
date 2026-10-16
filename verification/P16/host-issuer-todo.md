# P16 后续 Tauri host issuer 待办

P16 实现 Core 接收已签名、单目标、限格式、绑定 session、可过期且一次消费的 `ExportTargetRef`，实现签名验证、目标解析、安全复核、原子消费与 revoke registry。Core 私有 `_register_export_target` / `_revoke_export_target` 方法是未来可信 host adapter 的注入缝；它们**没有**注册到公开 JSONL 命令面，React/WebView 不可调用，也不能传路径取得写授权。

## 后续 host Task 范围

1. 由 Tauri host 经用户明确的 Save As / 目标选择动作确定精确文件目标；host 签发单一目标 ref，限定 session、format、replace 权限与不超过 300 秒的 expiry，并使用独立信任密钥签名。
2. 经可信 host-only IPC adapter 将 grant 注入 Python Core；禁止把签名密钥、绝对路径或注册能力暴露给 React/WebView 或公开 Core JSONL 请求。
3. `StartExport` 仅接收 opaque `target_ref`。不得按路径字符串、已存在文件名或客户端字段推导授权；session 结束时撤销剩余 grant。
4. host 需定义用户可恢复的错误/取消体验，并按 opaque `export_id` 提供打开文件夹/查看状态所需 host 行为；wire 事件/历史不能泄漏本机路径。
5. Reader host 负责把 Webtoon width-fitted display coordinate 转换为逻辑 Page 原图像素 `scroll_offset_y`，并在恢复时反向映射显示；Core 已按 §6.3 持久化与返回该原图像素坐标。

## Host Task 验收建议

- 另行授权 `src-tauri/**` 与明确的 host adapter 路径；本 Task 没有修改它们。
- host issuer 的密钥生命周期、session 绑定、签名输入规范、过期/撤销和并发发行需由正式 host Task 冻结并测试；此文不是新增 wire 契约。
- 验收：无 UI 侧路径/密钥/issuer 可达性、跨 session/格式/过期/revoke/replay 拒绝、ref 与当前导出确切目标绑定、用户取消/窗口关闭行为和 Windows 打包验证。
