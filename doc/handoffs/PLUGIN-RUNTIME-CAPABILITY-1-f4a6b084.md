---
task_id: PLUGIN-RUNTIME-CAPABILITY-1
author: dsh（Lead / Owner）
recipient: reviewer-settings-a（独立 Review）
base_commit: b5f3814b2a798ce17e6ebe0f7d8ce183ca091c02
delivery_head: f4a6b0842a57a4d0f39b09947a4aeb99b793d706
status: done
authorization: 用户 2026-10-23「1234都授权」
---

# Handoff — PLUGIN-RUNTIME-CAPABILITY-1（capability 接线）

## 1. 交付摘要

- **manifest**：新增 `SUPPORTED_PERMISSIONS = ("network",)`；`permissions` 允许空或仅 `network`；其余（`files_read`/`files_write`/`model`）→ `PLUGIN_PERMISSIONS_UNSUPPORTED`（detail 列出被拒权限）。词表 `ALLOWED_PERMISSIONS` 不变（未知权限仍 `PLUGIN_UNKNOWN_PERMISSION`）。
- **sandbox**：`run(..., capabilities=...)`；`_build_security_capabilities` 用 `LocalAlloc` 构造 `SID_AND_ATTRIBUTES[]`（`network` → `S-1-15-3-1` internetClient，`SE_GROUP_ENABLED`），`CreateProcessW` 后立即 `LocalFree`（内核已复制）；无能力时数组为空。
- **service**：`_invoke_sandboxed` 把 `manifest.permissions` 传给沙箱。
- **投影/UI**：`plugins.list` 返回 `permissions`；前端显示权限徽标（网络/无权限）。
- 测试：真实 AppContainer 对照（无权限 → `PermissionError`；network → 放行）、manifest 接受/拒绝矩阵、多次 Hook、前端徽标。

## 2. 验证

| 命令 | 结果 |
|---|---|
| 定向 pytest（sandbox + runtime + wire） | **47 passed** |
| 全量 pytest | `core-pytest.log` |
| 前端 vitest | **45 files / 435 tests**；tsc 0 |

## 3. 已知边界（如实）

- 仅 `network` 可强制；`files_read`/`files_write`/`model` 仍拒绝加载（无可靠强制手段，避免假承诺）。
- 网络测试以错误类型判别（本机公网可达时 `network` 插件实际联通；不可达时为超时/连接错误，仍证明网络栈已放行）。
- GUI 端到端冒烟留在候选 1（最后执行）。

## 4. 推荐下一步

Review approved 后 closeout，进入候选 4（打包解释器）。

## 5. Closeout（2026-10-23）

- Review r1 **approved**（`verification/PLUGIN-RUNTIME-CAPABILITY-1/review-r1.md`，审查头 `0d3bbe49`）。
- P2 已修：UI 文案改为「仅 network 可强制；files_read/files_write/model 仍拒绝」、Task 错误码统一 `PLUGIN_PERMISSIONS_UNSUPPORTED`、AC1 改为网络栈放行对照、STATUS 统一、Closeout 合并、capability 数组失败路径释放。
- 下一步：候选 4（打包解释器）。
