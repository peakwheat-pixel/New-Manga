---
task_id: PLUGIN-RUNTIME-SANDBOX-1
author: dsh（Lead / Owner）
recipient: reviewer-settings-a（独立 Review）
base_commit: 1a17decf1
delivery_head: 22f09e9056ad0c581db13eb61532035b032ba4b9
status: in_review
authorization: 用户 2026-10-23「1」（选择候选 1 = 本 Task）
---

# Handoff — PLUGIN-RUNTIME-SANDBOX-1（AppContainer OS 级沙箱）

## 1. 交付摘要

在 PLUGIN-RUNTIME-1 的 trusted-code 边界之上实现真正的 OS 级隔离（方案 A）：

- `src/infrastructure/plugins/sandbox.py`（新）：
  - 共享 AppContainer profile `NewMangaPluginSandbox`（解释器只读 ACL 只授一次）；
  - `CreateProcessW` + `PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES` 在容器内启动 Hook；
  - Job Object `KILL_ON_JOB_CLOSE` 拥有进程树（超时/关闭全灭）；
  - **非阻塞管道泵**（`PeekNamedPipe` 轮询 + 0ms wait）：挂起插件永不阻塞 Core；
  - ACL：插件目录 RX（递归）、解释器根/DLLs/Lib RX、数据根两级 traverse、runner 单文件 RX；失败即 `SandboxError`。
- `service.py`：`PluginService(..., sandbox=...)`；`_invoke_sandboxed` fail-closed（`PLUGIN_HOOK_UNAVAILABLE` + `plugin_error` 审计），绝不在失败后回退无沙箱执行。
- `core_assembly.py`：生产装配注入 `AppContainerSandbox(anchors=(data_root, data_root.parent))`。
- 前端：`PluginSettingsPanel` 安全说明改为 AppContainer/fail-closed 真实边界（AC6）。
- 测试：`tests/infrastructure/test_plugin_sandbox.py`（6 个真实容器用例）。

## 2. 验证

| 命令 | 结果 |
|---|---|
| 定向 pytest（sandbox + runtime + wire） | **37 passed** |
| 全量 pytest | `core-pytest.log` |
| 前端 vitest（panel） | 8 passed；tsc 0 |
| 探针 | `probe-appcontainer.log`：`{"fs": "BLOCKED:None", "net": "NET_BLOCKED"}` |

## 3. 已知边界（非阻塞，需在 Review 中确认接受）

1. **共享容器**：所有插件共用一个 AppContainer profile（解释器 ACL 成本原因）；跨插件目录读取不在 v1 威胁模型内（可后续 per-plugin profile 收紧）。
2. **ACL 依赖**：沙箱依赖 `icacls` 与 AppContainer 可用性（Windows 10+）；失败 fail-closed。
3. **能力 SID 未接线**：`CAPABILITY_SIDS` 支持 `network`，但 manifest 层仍拒绝非空 permissions（首发限制不变）。
4. **未覆盖**：GUI 端到端启用沙箱后的 Hook 真机冒烟（沙箱由 API/单测覆盖；GUI 面板文案已更新）。

## 4. 推荐下一步

- 本 Task Review approved 后 closeout；
- 后续候选：per-plugin profile（跨插件隔离）、带权限插件的 capability 接线（`PLUGIN-RUNTIME-3`）、打包解释器。
