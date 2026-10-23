---
task_id: PLUGIN-RUNTIME-SANDBOX-2
author: dsh（Lead / Owner）
recipient: reviewer-settings-a（独立 Review）
base_commit: acc1e36a7dc9f333c41f8131ff1b4d0b0bcd3423
delivery_head: 9ab2748d6325e8e817537fed40cd9269edc0d1ea
status: in_review
authorization: 用户 2026-10-23「1234都授权」
---

# Handoff — PLUGIN-RUNTIME-SANDBOX-2（per-plugin AppContainer profile）

## 1. 交付摘要

- `sandbox.py`：默认 **每插件独立 AppContainer profile**（`NewMangaPlugin-<sha256(plugin_id)[:12]>`）；`shared_profile=True` 仅为显式 opt-in；解释器只读 ACL 按 **SID** 缓存（每个插件容器只授一次）；`shared_profile` property 供测试/装配断言。
- `core_assembly`：生产装配不传 `shared_profile`（默认 per-plugin），`allow_unsandboxed=False` 保持。
- 测试：跨插件目录读取 `BLOCKED`；per-plugin SID 断言；解释器 ACL 缓存；生产装配 `shared_profile is False`。
- UI：安全说明改为「每个插件使用独立的 AppContainer 容器，无法读取其他插件目录」。

## 2. 验证

| 命令 | 结果 |
|---|---|
| 定向 pytest（sandbox + runtime + wire + assembly） | **52 passed** |
| 全量 pytest | `core-pytest.log` |
| 前端 panel vitest | 8 passed；tsc 0 |

## 3. 已知边界

- 插件数量多时，每个新插件首次 prepare 会一次性授予解释器 ACL（实测约 2s/插件）；插件量少可接受。
- `CAPABILITY_SIDS` 仍未接线（候选 3 处理）。
- GUI 端到端冒烟留给候选 1（最后执行）。

## 4. 推荐下一步

Review approved 后 closeout，进入候选 3（capability 接线）。
