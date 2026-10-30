# REALUSE-DATA-SAFETY-4 Handoff

- Task：[REALUSE-DATA-SAFETY-4](../tasks/REALUSE-DATA-SAFETY-4.md)
- 基线：`main b8039aec8`；交付 HEAD：`37dcd6d9f`；分支：`task/REALUSE-DATA-SAFETY-4`
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4`（保留，未删除）
- 独立审查：r1 `FAIL_WITH_MUST_FIX`（5 项）→ 修复 `3844851e8` → r2 `PASS`

## 交付内容

1. **⑤ 缓存与版本清理（真实接线，AC2）**：`cleanup.preview` / `cleanup.run` / `cleanup.retry_pending` 四层打通；预览（目标数、字节、待重试数）→ 确认门 → 执行结果；空预览不弹确认。
2. **⑦ 插件与 Hooks（真实接线，AC2）**：`plugins.list` / `set_enabled` / `set_plugin_enabled` 四层打通；清单、全局开关、单插件开关、被拒绝插件 reason、全局关闭时单插件开关禁用。
3. **④ 模型与设备（诊断式，AC1 部分）**：从 ProviderProfiles 推导检测能力绑定；未绑定明确说明 `PROVIDER_NOT_CONFIGURED` 并给跳转 ② 的入口；设备/权重如实标注 Core 未暴露。
4. **契约提案（AC3）**：`doc/proposals/REALUSE-DATA-SAFETY-4-device-status-contract.md`（`diagnostics.device_status`，只读、无绝对路径），未实施。

## 限制（AC1 未完全达成的原因）

设备与权重状态需要 Core 新增只读命令；本 Task 只交付了能由现有数据推导的那一半，并把缺失部分写成契约提案等裁决。

## 证据

- `dotnet build -warnaserror`：0W/0E
- `dotnet test`：859 passed / 0 failed（App 373）
- 审查报告：`doc/reviews/REALUSE-DATA-SAFETY-4-antigravity-r1.md`、`-r2.md`
