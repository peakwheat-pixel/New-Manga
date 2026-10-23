---
task_id: PLUGIN-RUNTIME-SANDBOX-1
author: dsh（Lead / Owner）
recipient: reviewer-settings-a（独立 Review）
base_commit: 1a17decf1
delivery_head: PLACEHOLDER_SANDBOX_R1
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

## 5. Review r1 处置（changes_requested）

- **P1-1 生产装配**：`core_assembly.py:1212` 现在真正构造 `AppContainerSandbox(interpreter=resolve_hook_interpreter(), anchors=(data_root, data_root.parent))` 并注入 `PluginService(sandbox=...)`；`test_production_assembly_wires_the_sandbox` 走真实 `assemble_core_services` 验证。
- **P1-2 最小 env**：`CreateProcessW` 改为传 UTF-16 环境块（`CREATE_UNICODE_ENVIRONMENT`），白名单仅 `PYTHONIOENCODING/PYTHONDONTWRITEBYTECODE/SYSTEMROOT/SYSTEMDRIVE/LOCALAPPDATA`（实测 LOCALAPPDATA 是 AppContainer 启动必需，其余用户/测试/代理/凭据变量全部丢弃）；`test_hook_child_sees_only_the_minimal_environment` 断言无 `DSH_/M2RC1_/NEWMANGA_/代理/API key`。
- **P1-3 诚实性**：UI 文案改为「容器只被授予只读访问本插件目录与 Python 运行时（解释器/DLLs/Lib 与 runner 为只读例外）；插件共用同一容器（v1）；环境最小化；fail-closed」。
- **P2**：`allowed_paths` 补 `src/bootstrap/core_assembly.py`；Task canonical 证据补生产装配/环境/Job 树杀/前端行；两个 Closeout 标题合并；`_traversal_chain`/anchors 改 `(X)`（traverse-only）；`AssignProcessToJobObject` 失败抛 `SandboxError`；沙箱用 `_hook_interpreter()` 解析的解释器（ACL 一致）；`CREATE_SUSPENDED` + 先入 Job 再 `ResumeThread`（消除孙进程竞态）；job 句柄禁止继承（`KILL_ON_JOB_CLOSE` 生效）。
- **验证（r1 修复后）**：定向 **49 passed**；全量见 `core-pytest.log`；前端 vitest 8 passed（panel）；tsc 0。
