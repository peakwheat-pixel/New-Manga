# PLUGIN-RUNTIME-SANDBOX-2 独立 Review r1

- Reviewer：`reviewer-settings-a`（非实现者）
- 审查头：**`127c51114373b987251e84ad2083827e0d1e2c02`**
- 实现 commit：**`9ab2748d6325e8e817537fed40cd9269edc0d1ea`**；base：`acc1e36a7`
- 结论：**approved**。per-plugin AppContainer profile、解释器 ACL 按 SID 缓存、生产默认 per-plugin、`shared_profile` 显式 opt-in 均已实现；真实沙箱用例与生产装配测试通过。剩余为 P2/P3：STATUS 仍 `in_progress`、Task 两个 Closeout 标题、canonical 证据缺 UI/tsc、跨插件测试判别力不足、AC4 测试未覆盖两个不同 SID、MAX_PROFILES/性能未说明。

## 1. 功能核验

### 1.1 per-plugin profile

`sandbox.py`：

- `_profile_name`：`shared_profile=False` 时使用 `NewMangaPlugin-<sha256(plugin_id)[:12]>`；`True` 时才使用旧 `NewMangaPluginSandbox`。
- `_ensure_profile` 以 `cache_key = "__shared__" if shared else plugin_id` 缓存，不同插件产生不同 SID。
- `shared_profile` property 暴露给测试/装配断言。

验证：

- `test_sandbox_uses_per_plugin_profiles`：两个插件的 `_ensure_profile` 返回两个不同 SID。
- `test_shared_profile_is_an_explicit_opt_in`：只有显式 `shared_profile=True` 才共用 SID。
- `test_production_assembly_wires_the_sandbox`：真实 `assemble_core_services` 的 `core.plugins._sandbox.shared_profile is False`，并执行 sandboxed hook。
- UI `PluginSettingsPanel.tsx` 安全说明改为“每个插件使用独立的 AppContainer 容器，无法读取其他插件目录”，与实现一致。

### 1.2 解释器 ACL 按 SID 缓存

`_interpreter_sids` 改为按 SID 集合：

```python
def _prepare_interpreter(self, sid: str) -> None:
    if sid in self._interpreter_sids:
        return
    ...
    self._interpreter_sids.add(sid)
```

`_grant` 本身按 `(path, sid)` 缓存。per-plugin 模式下每个新 SID 首次 prepare 授一次解释器 ACL，同 SID 后续 Hook 不再重复。`test_interpreter_acl_is_granted_once_per_profile_sid` 覆盖同 SID 两次 Hook 只授一次（但见 P2-4）。

### 1.3 共享模式 opt-in

`shared_profile=True` 保留旧共享 SID；默认 False；生产 `core_assembly` 不传该参数，默认 per-plugin。`allow_unsandboxed=False` 仍保持，生产漏传 sandbox 会在 `_invoke` 抛 `PLUGIN_HOOK_UNAVAILABLE`，不会回退无沙箱。

## 2. 独立验证

| 检查 | 结果 |
|---|---|
| 定向 pytest（sandbox/runtime/wire/assembly） | **52 passed** |
| 全量 pytest | **2663 passed / 9 skipped / 3 既有失败**（与交付说明一致） |
| vitest | **45 files / 434 tests passed** |
| `tsc --noEmit` | exit 0 |
| `check.ps1` | PASS（4 warnings：STATUS/REBASELINE 预算、2 非终态） |
| 沙箱用例 | 根外读 `BLOCKED`、跨插件读 `BLOCKED`、联网 `NET_BLOCKED`、benign、timeout、job 树杀、最小 env、字节输出上限、per-plugin SID、共享 opt-in、生产装配均通过 |

## 3. P2 / P3 findings

1. **STATUS 仍 `in_progress`**：`doc/STATUS.md:7` 当前 Task 写 `in_progress`，而 Task `:4`、Handoff `:7`、TASK_LEDGER `:33` 均为 `in_review`；用户也称 Task 在 Review。closeout 前需统一 `in_review`。
2. **Task 证据表只有 2 行 canonical**：`EV-SANDBOX-2-CORE-PYTEST-TARGETED` 与 `EV-SANDBOX-2-CORE-PYTEST`；AC5 声称 vitest/tsc，但 `verification/PLUGIN-RUNTIME-SANDBOX-2/` 没有 UI/tsc 证据行。建议补 `EV-SANDBOX-2-UI-TEST-FRONTEND`/`EV-SANDBOX-2-UI-TSC`（或明确 AC5 只由 core 日志覆盖）。
3. **Task 仍有两个 `## Closeout Record`**（`:44`/`:57`）；合并为一处。
4. **跨插件测试判别力不足**：`test_plugin_cannot_read_another_plugins_directory` 只写了 B 插件目录，但**没有先 prepare/run B**；在旧共享 profile 下 B 目录未授给共享 SID，A 读 B 同样会 `BLOCKED`，所以该测试无法单独证明 per-plugin 生效。建议先启用/执行 B（使共享 SID 获得 B 目录 ACL），再让 A 读 B；per-plugin 应仍 `BLOCKED`，共享模式会 `READ_OK`，测试才有判别力。
5. **AC4 测试没有覆盖两个不同 SID**：`test_interpreter_acl_is_granted_once_per_profile_sid` 只对同一个插件跑两次，断言 `_interpreter_sids` 长度为 1。它证明“同 SID 不重复”，但未证明“不同插件各授一次”。建议两个插件各 run 一次，断言 `_interpreter_sids` 最终有 2 个 SID / `icacls` 调用计数为 2。
6. **MAX_PROFILES / 性能边界未在 Task 明确**：`MAX_PROFILES=64`；每个新插件首次 prepare 约 2s（Handoff 已写），64 个插件可能累计约 128s，且 `_profiles` 不淘汰；超过 64 个插件时 `_ensure_profile` 抛 `SandboxError`，Hook fail-closed。建议在 Task/UI 记录 64 上限及“首次 Hook 可能约 2s”，并确认 >64 插件是拒绝而非静默退化。
7. **`shared_profile` opt-in 没有生产防护断言**：core_assembly 未传即默认 False，测试已断言；但 API 允许任意调用者传 True。建议在 core_assembly 加显式 `shared_profile=False` 或断言，防止未来误改。
8. **P3**：`_interpreter_sids` 是普通 set，并发两个 Hook 首次 prepare 可能重复 `icacls`（重复授予通常无害，但不是严格一次）；`_profiles`/`_interpreter_sids` 无锁。可留后续。

## 4. 结论

**approved。**

- 每插件独立 SID、解释器 ACL 按 SID 缓存、生产默认 per-plugin、共享 opt-in、`allow_unsandboxed=False` 均成立，未发现新 blocker。
- P2-1/2/3 是文档/证据一致性，closeout 前应修；P2-4/5 是测试判别力，建议补强；P2-6/7 是性能/防误用说明。
- 修复 P2 后可 closeout，进入候选 3（capability 接线）。**当前可 approved/closeout。**
