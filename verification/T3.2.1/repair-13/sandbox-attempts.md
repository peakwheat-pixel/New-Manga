# REPAIR-13 Windows Sandbox 尝试记录（已被用户裁决取代）

> **裁决（2026-09-25，用户）**：取消 Sandbox 验证，以**本机验证**代替；相关文档与任务
> 按此修订。以下三次启动尝试保留为历史证据。替代验证见
> [`local-verification.md`](local-verification.md)。

日期：2026-09-25（Asia/Shanghai）
执行者：ZCode（REPAIR-13 Owner，用户改派）
固定包：delivery `2f18e784b7a4bdcc71672a949550594e7958846e` 构建，
`packaging/build.ps1 -OutputDir G:/CODEX/repair13-build-out`，exit 0；
`NewManga.exe` SHA-256 = `da946c67e4e29f268609cbfc3dd4c7e3a094c69a9161d5de0ae06868099ef412`
（见 [`build5-delivery-exe.sha256`](build5-delivery-exe.sha256) 与
[`build5-delivery-artifact-manifest.sha256`](build5-delivery-artifact-manifest.sha256)，5437 条）。

## 尝试序列

1. `cmd start "G:\CODEX\repair13-sandbox.wsb"`（映射 `G:\CODEX\repair13-build-out`
   只读 + `G:\CODEX\repair13-sandbox-exchange` 可写；LogonCommand 启动 NewManga.exe）。
   实例启动成功（RemoteSession pid 30316，桌面就绪），但**桌面与资源管理器中均无映射文件夹**，
   LogonCommand 未生效 —— 该实例以默认配置运行，不能作为本 Task 的验证环境。
2. 关闭该实例（GUI 确认"确定"）。此后每次 `WindowsSandbox.exe G:\CODEX\repair13-sandbox.wsb`
   均弹 **"Windows 沙盒无法初始化。Exception of type 'System.Exception' was thrown."**
   - 重试含：等待 90–120 s 让 Hypervisor 资源释放、`taskkill /F WindowsSandboxRemoteSession.exe`
     后再启动、多次重启，共 3 次以上，错误一致（截图为本报告同期的 UI 观察记录）。
3. `net stop vmcompute`（修复虚拟化栈）→ **系统错误 5（拒绝访问）**，本会话无管理员权限。

## 判定

- R13-AC5 的 **Sandbox 真实 GUI 子项 = BLOCKED**（环境阻塞，非产品缺陷，非 NOT_RUN-PASS）。
- 不据此把 R13-AC5 或父 Gate 的任何项记为通过。
- 本地等价证据：[`probe_ui_states.py`](probe_ui_states.py) 在真实生产组装栈
  （`assemble_services` + `QQmlApplicationEngine` + context properties，真实 import/export
  use case 与文件系统）完成 R13-AC1～AC4 全流程，stdout/stderr 与 13 张截图入库。
- 后续：由 Codex/用户在管理员会话重启 `vmcompute`（或重启主机）后，用本目录
  [`repair13-sandbox.wsb`](repair13-sandbox.wsb) 与
  `G:\CODEX\repair13-sandbox-exchange`（已放入两张 fixture PNG，
  hash 见 [`fixtures.sha256`](fixtures.sha256)）做人工 Sandbox 复测；
  该复测结论不属于本切片 Review 的批准范围（Task §R13-AC6）。

## 命令与退出码摘要

```text
powershell -File packaging/build.ps1 -OutputDir G:/CODEX/repair13-build-out
  → EXIT=0（Git Delivery Head: 2f18e784b7a4bdcc71672a949550594e7958846e）
Start-Process WindowsSandbox.exe -ArgumentList G:\CODEX\repair13-sandbox.wsb
  → 实例 1：默认配置（映射/LogonCommand 未生效）
  → 实例 2..n：Windows 沙盒无法初始化（System.Exception）
net stop vmcompute → 系统错误 5（拒绝访问）
```
