---
id: M2-FIX-STUB-DECODER
title: core_service stub decoder signature fix（ImportPages 扩面前置）
kind: fix
status: done
release_state: M2_FIX_STUB_DECODER_RELEASED
approval: released_by_orchestrator_2026-09-29_goal_g2 (Codex 代行,用户授权 2026-09-28;代理裁决,用户可撤销)
execution_approval: released_by_orchestrator_2026-09-29_goal_g2
suggested_owner: ZCode
owner: ZCode（子agent代行,用户授权 2026-09-28）
reviewer: DeepSeek Harness
integrator: Codex（另一子 agent 以 Codex 身份执行，保持 Owner≠Integrator）
depends_on: [M2-IPC1]
base_commit: f5d91425
branch: agent/zcode/M2-FIX-STUB-DECODER
worktree: G:/CODEX/New Manga.worktrees/M2-FIX-STUB-DECODER-zcode
delivery_head: 5cacebfa25ef17ea3a487ac4fcb11a4590636661
review: doc/reviews/M2-FIX-STUB-DECODER-69250a39-dsh-r1.md (DSH r1 approved_with_conditions, 0xP0/P1/P2, C1-C2 closed)
integration_merge: 121a281cbf65f62c57b177efc44fa4649b11c9ae
dispatch_state: INTEGRATED
---

# M2-FIX-STUB-DECODER — core_service stub decoder 签名修复

## 来源与目标

登记于 M2-AC2 集成收口（2026-09-28，integration `9d3c1db5`，[集成记录](../verification/M2-AC2/integration-c3ee8dbe/integration.md) §⑤），经编排会话按 [GOAL](../GOAL.md) G2 于 2026-09-29 释放（代理裁决，用户可撤销；理由=范围最小、已登记候选、解除 ImportPages 扩面前置）。

缺陷（M2-AC2 Owner 实现发现 + DSH r2 P3-3 实证；起草时经代码复核）：`src/bootstrap/core_service.py:51-54` 的 `_PassthroughImageDecoder` stub 构造 `DecodedImage(width=1, height=1, format="rgb")`，而 `DecodedImage` 真实字段只有 `width/height/mime_type`（`src/application/importing/images/ports.py:11-16`）→ **双重 TypeError**：多余字段 `format=` + 缺失必填参数 `mime_type`。任何经该 stub 的导入都会崩。M2-IPC1 冻结命令面不含 import 故 production 未受影响；M2-AC2 验收经 assembly adapter-injection 自备 decoder 绕开。

目标：stub 构造修正为真实契约 + 最小回归测试锁定，使未来 core_service 扩 ImportPages 类命令前缺陷已清除。

## Acceptance Criteria（释放时冻结）

- [x] **AC1 — stub 签名修正：** PASS——`_PassthroughImageDecoder.decode` 构造 `DecodedImage(width=1, height=1, mime_type="image/rgb")`（注释注明取值理由）；仅类体一行修复，`assemble_production_core` 其他注入与 `DecodedImage` 契约零改动。
- [x] **AC2 — 回归测试先红后绿：** PASS——`tests/core/test_stub_decoder.py`（2 场景：production 装配路径 `core.importer._decoder` + 直构 passthrough 语义）；先红 TypeError `unexpected keyword argument 'format'` @ `core_service.py:54`（2 failed, EXIT=1，`raw/02-red-before-fix.log`）→ 修复后 2 passed（EXIT=0，`raw/03-green-after-fix.log`）。
- [x] **AC3 — 证据纪律：** PASS——日志带头（shell/解释器/HEAD/ISO 时间戳）尾记 EXIT；`git diff --check f5d91425..5cacebfa` EXIT=0；Owner 变更（`fc419905..5cacebfa`）仅落允许路径（`raw/06-scope-self-check.log`）。最终 tip 复跑按协议归 Integrator。

## 允许修改范围

- `src/bootstrap/core_service.py`（仅 `_PassthroughImageDecoder` 类体，最小修复）
- `tests/` 新增测试文件（建议 `tests/core/test_stub_decoder.py`；不修改既有测试行为）
- `doc/tasks/M2-FIX-STUB-DECODER.md`、`verification/M2-FIX-STUB-DECODER/**`、`doc/handoffs/M2-FIX-STUB-DECODER-*.md`

## 禁止范围

- 扩 ImportPages/IPC 命令面、`DecodedImage` 契约/schema 变更、真实 decoder 引入（另立 Task）、`apps/**`、`doc/contracts/**`、依赖、既有测试行为修改、Legacy QML。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC2 先红（base 上） | planned：base commit 工作树预览下跑新测试，预期 TypeError 红 | TASK-012-py312 | **EXECUTED**：`TypeError: DecodedImage.__init__() got an unexpected keyword argument 'format'` @ `core_service.py:54`，2 failed，EXIT=1（src 未改，HEAD=claim `0f4f881a`） | `verification/M2-FIX-STUB-DECODER/raw/02-red-before-fix.log` |
| AC2 修复后绿 | planned：`$py -m pytest tests/core/test_stub_decoder.py -v` | TASK-012-py312 | **EXECUTED**：2 passed，EXIT=0 | `verification/M2-FIX-STUB-DECODER/raw/03-green-after-fix.log` |
| AC3 回归+diff-check | planned：相关既有测试 + `git diff --check` | TASK-012-py312 | **EXECUTED**：`tests/core/ -q` 76 passed EXIT=0；`tests/m2_acceptance -q` 32 passed + 2 xfailed EXIT=0；`git diff --check f5d91425..5cacebfa` EXIT=0 | `raw/04-regression-tests-core.log`、`raw/05-regression-tests-m2_acceptance.log`、`raw/06-scope-self-check.log` |

## 依赖、风险与阻塞

- depends_on=`M2-IPC1`（done）。风险低：单点 stub 修复，production 命令面不含 import，回归面小。
- 注意 `assemble_production_core` 中 `font_catalog/layout_engine/compositor=object()` 的同类 stub 缺陷**不在本 Task 范围**（登记观察，如需修复另立 Task）。

## 交付与运行记录

- Handoff：`doc/handoffs/M2-FIX-STUB-DECODER-owner-delivery.md`（Owner=ZCode 子 agent 代行，用户授权 2026-09-28）。
- Review：DSH r1（非作者静态）**approved_with_conditions**，0×P0/P1/P2，6×P3 不阻塞；归档 `doc/reviews/M2-FIX-STUB-DECODER-69250a39-dsh-r1.md`（SHA256 `d17b4262466ce4b9382b63319859f44c40aeb3c498db03692b61908c3a7d7fe6`）。C1/C2 由 Integrator 代跑关闭，P3-1..P3-6 处置见 [集成记录](../verification/M2-FIX-STUB-DECODER/integration-69250a39/integration.md)。
- 实际测试（2026-09-28，TASK-012-py312，Windows x64 · Git Bash · Python 3.12.3 · pytest 9.1.1）：
  - 先红：TypeError @ `core_service.py:54`，2 failed，EXIT=1 → 修复后 2 passed，EXIT=0（`tests/core/test_stub_decoder.py`）。
  - 回归：`tests/core/` 76 passed；`tests/m2_acceptance` 32 passed + 2 xfailed（F-1/F-2 受控缺陷证据，未触碰）；均 EXIT=0。
  - 范围：Owner 变更仅允许路径；`git diff --check f5d91425..5cacebfa` EXIT=0（交付 commit 有 amend 轨迹：初版 `550b4269` 日志行尾空白 whitespace-only 清理后 amend 为 `5cacebfa`）。
  - 语义发现：`CoreServices` 无 `image_decoder` 属性，production 装配中 decoder 在 `core.importer._decoder`（AC2「等价最小路径」采用）；`assemble_production_core` 中 `font_catalog/layout_engine/compositor=object()` 同类 stub 隐患维持范围外观察。
- 三 commit ledger：claim `0f4f881a` → 实现+证据+handoff（交付 tip）`5cacebfa` → task 回填 `status: in_review`/`DELIVERED_FOR_REVIEW`（delivery_head 保持 null，由 Integrator merge 后回填；交付 tip hash 以回填 commit message 与本节记录 `5cacebfa` 为准）。最终由 Integrator 填 integration_merge 并改 done。
