---
id: M2-FIX-STUB-DECODER
title: core_service stub decoder signature fix（ImportPages 扩面前置）
kind: fix
status: proposed
release_state: NOT_RELEASED
approval: null
suggested_owner: ZCode
owner: null
reviewer: DeepSeek Harness
integrator: Codex（届时新会话代行）
depends_on: [M2-IPC1]
base_commit: null
branch: null
worktree: null
delivery_head: null
review: null
integration_merge: null
dispatch_state: NOT_RELEASED
---

# M2-FIX-STUB-DECODER — core_service stub decoder 签名修复

## 来源与目标

**proposed / NOT_RELEASED 候选**——登记于 M2-AC2 集成收口（2026-09-28，integration `9d3c1db5`，[集成记录](../verification/M2-AC2/integration-c3ee8dbe/integration.md) §⑤）。本文件仅为登记，未冻结 base/branch/worktree，**禁止在任何会话中未经 §5.1 释放流程实施**。

缺陷（M2-AC2 Owner 实现发现 + DSH r2 P3-3 实证）：`src/bootstrap/core_service.py:54` 附近的 `_PassthroughImageDecoder` stub 向 `DecodedImage` 传 `format=` 参数，而 `DecodedImage` 真实字段只有 `width/height/mime_type`（`src/application/importing/images/ports.py:12-17`）→ **任何经该 stub 的导入都会 TypeError**。M2-IPC1 冻结命令面不含 import 故未受影响；M2-AC2 验收经 assembly adapter-injection 自备 decoder 绕开。

## 修复方向（释放时由 Codex 冻结为正式 AC）

- 修正 stub 构造 `DecodedImage` 的字段（删 `format=` 或按真实契约扩展），并以最小回归测试锁定（经 stub 的导入路径不再 TypeError）。
- **硬前置**：未来 core_service 扩 ImportPages 类命令前必须先完成本修复并集成。
- 允许范围届时冻结：`src/bootstrap/core_service.py` 最小修复 + 对应 tests + 本 Task/verification/Handoff 路径。

## 交付与运行记录

- 尚无。释放时按 TASK 模板补全 Contract 并登记 release checkpoint。
