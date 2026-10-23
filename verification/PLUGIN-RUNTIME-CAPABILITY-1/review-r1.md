# PLUGIN-RUNTIME-CAPABILITY-1 独立 Review r1

- Reviewer：`reviewer-settings-a`（非实现者）
- 审查头：**`0d3bbe4947c3070824aa869980bb6473fefcb6e0`**
- 实现 commit：**`f4a6b0842a57a4d0f39b09947a4aeb99b793d706`**；base：`b5f3814b2`
- 结论：**approved**。`network` capability 的 manifest 接受/拒绝矩阵、AppContainer `internetClient` SID 注入、无权限网络拒绝、3 次 Hook 生命周期、`plugins.list` 投影与前端徽标均成立；无新 blocker。剩余 P2 为 UI 旧文案、Task 错误码/测试描述、STATUS/Closeout 文档不一致。

## 1. 能力强制真实性

### 1.1 manifest 语义

`manifest.py`：

- `SUPPORTED_PERMISSIONS = ("network",)`；`ALLOWED_PERMISSIONS` 词表保持。
- `permissions` 为空或仅 `network` 接受；`files_read`/`files_write`/`model` → `PLUGIN_PERMISSIONS_UNSUPPORTED`，detail 列出 unsupported 项；未知权限仍 `PLUGIN_UNKNOWN_PERMISSION`。
- 这避免了“声明 files/model 但无强制手段”的假承诺；Task/Handoff 也写明仅 network 可强制、其余继续拒绝。

### 1.2 Sandbox capability 构造

`sandbox.py`：

- `CAPABILITY_SIDS = {"network": "S-1-15-3-1"}`（internetClient）。
- `_build_security_capabilities` 用 `LocalAlloc(_LMEM_FIXED, sizeof(SID_AND_ATTRIBUTES)*n)` 构造数组；每项 `SID_AND_ATTRIBUTES(Sid, SE_GROUP_ENABLED)`；`CapabilityCount=n`；无能力时 `Capabilities=None/Count=0`。
- `SECURITY_CAPABILITIES` 通过 `PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES` 传给 `CreateProcessW`；`cleanup_pointers` 在 `CreateProcessW` 返回后 `LocalFree`（数组块 + 每个 `ConvertStringSidToSidW` 分配的 SID）。
- `_invoke_sandboxed` 仅把 `manifest.permissions` 传给 sandbox；未声明即空数组。

### 1.3 真实行为

- `test_network_capability_requires_the_network_permission`：无权限插件连接 `1.1.1.1:443` → `PermissionError`（网络栈被拒）；`network` 插件 → 错误类型不是 `PermissionError`（已放行；公网不可达时可能是 timeout/connection error，仍证明网络栈不再是 PermissionError）。
- `test_network_capability_survives_repeated_hooks`：3 次 Hook 无错误，capability 数组生命周期未崩溃/泄漏。
- 既有 `test_sandbox_blocks_network_access` 仍覆盖无权限网络拒绝；真实 AppContainer，不是 mock。

## 2. 投影/UI

- `PluginService.list_plugins` 对 valid/rejected 均投影 `permissions`（rejected 为空数组）。
- `SettingsClient`/`PluginEntry` 归一化 `permissions`；`PluginSettingsPanel` 显示 `PERMISSION_LABELS`：`network` → 「网络」，空 → 「无权限」，其他 fallback 原词。
- 徽标与实际能力一致（network 显示网络；空无权限）。

## 3. 独立验证

| 检查 | 结果 |
|---|---|
| 定向 pytest（sandbox/runtime/wire/assembly） | **55 passed**（含额外 core_assembly；交付表称 47，因命令包含文件不同，无失败） |
| 全量 pytest | **2666 passed / 9 skipped / 3 既有失败**（与交付说明一致） |
| vitest | **45 files / 435 tests passed** |
| `tsc --noEmit` | exit 0 |
| `check.ps1` | PASS（4 warnings：STATUS/REBASELINE 预算、2 非终态） |
| 网络对照 | 无权限 `PermissionError`；`network` 非 `PermissionError` |
| 生命周期 | 3 次 Hook 无错误 |

## 4. P2 / P3 findings

1. **UI 仍有旧文案，和 network 能力矛盾**：`PluginSettingsPanel.tsx:231` 仍写“首发只加载无权限插件（permissions: []）”；`:432` 安全说明仍写“带权限声明的插件一律拒绝加载”。现在 `network` 插件可以加载且 UI 会显示“网络”徽标，这两句会误导用户；应改为“仅 network 可强制，files_read/files_write/model 仍拒绝”。这是 AC5/AC3 文档一致性的 P2。
2. **Task 错误码大小写/单复数不一致**：Task `:29`/`:43` 写 `PLUGIN_PERMISSION_UNSUPPORTED`，实现与 Task 测试表 `:55`/Handoff 使用 `PLUGIN_PERMISSIONS_UNSUPPORTED`；统一为复数。
3. **Task AC1 说“连接同一 local TCP server”，实际测试连接 `1.1.1.1:443`**：测试只断言错误类型不是 `PermissionError`，不验证本地连通；对“capability 已放行”足够，但对“network 插件可成功连接”不充分。建议用本地 `loopback` server 做对照（同时保留公网错误类型测试），或把 AC1 改为“网络栈放行（非 PermissionError）”。
4. **STATUS 仍 `in_progress`**：`doc/STATUS.md:7` 当前 Task 写 `in_progress`，Task `:4`/Handoff `:7`/TASK_LEDGER `:33` 为 `in_review`；closeout 前统一。
5. **Task 仍有两个 `## Closeout Record`**（`:48`/`:61`），合并为一处。
6. **P3**：`_build_security_capabilities` 在 `UpdateProcThreadAttribute` 失败时，已分配的数组/SID 指针没有 `LocalFree`；正常路径和多次 Hook 已通过，但失败路径可补 `try/finally`。
7. **P3**：网络测试依赖公网可达性；不可达时仅验证非 `PermissionError`，Task/Handoff 已注明，但本地 server 会更确定性。

## 5. 结论

**approved。**

- `network` 能力真实接入 AppContainer，无权限插件仍被网络栈拒绝；files_read/files_write/model 继续拒绝，避免了假能力。
- 投影/徽标/生产 sandbox 路径一致；无新 P1。
- 建议 closeout 前修 P2-1/2/3/4/5（尤其 UI 旧文案与 STATUS），P3 可留后续。
- 关闭后进入候选 4（打包解释器）或候选 1（GUI 端到端）。**当前可 approved/closeout。**
