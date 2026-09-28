---
id: M2-FIX-STUB-DECODER
title: core_service stub decoder signature fix（ImportPages 扩面前置）
kind: fix
status: ready
release_state: M2_FIX_STUB_DECODER_RELEASED
approval: released_by_orchestrator_2026-09-29_goal_g2 (Codex 代行,用户授权 2026-09-28;代理裁决,用户可撤销)
execution_approval: released_by_orchestrator_2026-09-29_goal_g2
suggested_owner: ZCode
owner: ZCode（待认领）
reviewer: DeepSeek Harness
integrator: Codex（另一子 agent 以 Codex 身份执行，保持 Owner≠Integrator）
depends_on: [M2-IPC1]
base_commit: f5d91425
branch: agent/zcode/M2-FIX-STUB-DECODER
worktree: G:/CODEX/New Manga.worktrees/M2-FIX-STUB-DECODER-zcode
delivery_head: null
review: null
integration_merge: null
dispatch_state: RELEASED
---

# M2-FIX-STUB-DECODER — core_service stub decoder 签名修复

## 来源与目标

登记于 M2-AC2 集成收口（2026-09-28，integration `9d3c1db5`，[集成记录](../verification/M2-AC2/integration-c3ee8dbe/integration.md) §⑤），经编排会话按 [GOAL](../GOAL.md) G2 于 2026-09-29 释放（代理裁决，用户可撤销；理由=范围最小、已登记候选、解除 ImportPages 扩面前置）。

缺陷（M2-AC2 Owner 实现发现 + DSH r2 P3-3 实证；起草时经代码复核）：`src/bootstrap/core_service.py:51-54` 的 `_PassthroughImageDecoder` stub 构造 `DecodedImage(width=1, height=1, format="rgb")`，而 `DecodedImage` 真实字段只有 `width/height/mime_type`（`src/application/importing/images/ports.py:11-16`）→ **双重 TypeError**：多余字段 `format=` + 缺失必填参数 `mime_type`。任何经该 stub 的导入都会崩。M2-IPC1 冻结命令面不含 import 故 production 未受影响；M2-AC2 验收经 assembly adapter-injection 自备 decoder 绕开。

目标：stub 构造修正为真实契约 + 最小回归测试锁定，使未来 core_service 扩 ImportPages 类命令前缺陷已清除。

## Acceptance Criteria（释放时冻结）

- [ ] **AC1 — stub 签名修正：** `_PassthroughImageDecoder.decode` 构造 `DecodedImage` 严格按真实契约（`width/height/mime_type`，无 `format=`）；`mime_type` 取值语义合理。修复最小化：不改 `assemble_production_core` 其他注入、不改 `DecodedImage` 契约本身。
- [ ] **AC2 — 回归测试先红后绿：** 新增测试直接调用 production 装配产出的 `image_decoder.decode(...)`（或等价最小路径）断言返回 `DecodedImage` 且字段合法；**先红证明**：base commit 上该测试必须红（TypeError），修复后绿。证据落 `verification/M2-FIX-STUB-DECODER/`。
- [ ] **AC3 — 证据纪律：** 所有命令日志带 shell、解释器、固定 HEAD、EXIT 码；`git diff --check <base>..<delivery-head>` exit 0；范围自检：变更仅落允许路径。

## 允许修改范围

- `src/bootstrap/core_service.py`（仅 `_PassthroughImageDecoder` 类体，最小修复）
- `tests/` 新增测试文件（建议 `tests/core/test_stub_decoder.py`；不修改既有测试行为）
- `doc/tasks/M2-FIX-STUB-DECODER.md`、`verification/M2-FIX-STUB-DECODER/**`、`doc/handoffs/M2-FIX-STUB-DECODER-*.md`

## 禁止范围

- 扩 ImportPages/IPC 命令面、`DecodedImage` 契约/schema 变更、真实 decoder 引入（另立 Task）、`apps/**`、`doc/contracts/**`、依赖、既有测试行为修改、Legacy QML。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC2 先红（base 上） | planned：base commit 工作树预览下跑新测试，预期 TypeError 红 | TASK-012-py312 | NOT_RUN | 无 |
| AC2 修复后绿 | planned：`$py -m pytest tests/core/test_stub_decoder.py -v` | 同上 | NOT_RUN | 无 |
| AC3 回归+diff-check | planned：相关既有测试 + `git diff --check` | 同上 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- depends_on=`M2-IPC1`（done）。风险低：单点 stub 修复，production 命令面不含 import，回归面小。
- 注意 `assemble_production_core` 中 `font_catalog/layout_engine/compositor=object()` 的同类 stub 缺陷**不在本 Task 范围**（登记观察，如需修复另立 Task）。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。
- 后续实际记录包含日期、commit、环境、结果、遗留项；最终由 Integrator 填 integration_merge 并改 done。
