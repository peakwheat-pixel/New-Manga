---
task_id: P02
title: 真实 Workbench WebView 行为、300ms 刷新与对比度验证 (Stage A 定向修订 Handoff r3)
status: in_progress
stage: STAGE_A_SAFE_FOUNDATION_R3
author: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
worktree: G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity
branch: agent/antigravity/P02-real-webview-harness
base_commit: 241ff3b70b6fc0490ea238efd486cc707f849031
scope_contract_sha256: 27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425
reviewed_head_r1: 972049f991b5c119555647eeea816e89dd4769f3
dsh_decision_r1: changes_requested
reviewed_head_r2: 9b82e97b8aadc5b6b8710e03b5128a608697f56e
dsh_decision_r2: changes_requested
created_at: 2026-10-09T15:25:00+08:00
---

# P02 Stage A 安全基底定向修订交付报告 (r3)

## 1. 修订概述

本交付响应非作者实现 Reviewer DeepSeek Harness 对 Stage A r2 交付（`reviewed_head=9b82e97b8aadc5b6b8710e03b5128a608697f56e`）提出的 `changes_requested` 评审意见（`doc/reviews/P02-9b82e97b-dsh-r2-review.md`，P0/P1/P2/P3=`0/0/2/8`，含 G-01~G-07 及 F-05 等）以及 Codex exact-commit preflight 补证要求。

在严格恪守 **Hard Build Barrier（硬构建屏障）** 的前提下，本修订彻底闭合了全部 open findings：
1. 消除测试工件中的自引用死结，区分被测源码基线、关键文件 SHA-256 清单与后续交付 commit；
2. 消除底色硬编码，动态获取语义角色底色，并引入基于 `RegionOverlay.tsx` 真实源码的半透明合成计算；
3. 将 AC4 fixture 的 `retype` 操作严格对齐 `relabelMachine.ts` 源码状态机规则（`speech` ↔ `sfx`）；
4. 深度对齐 Region、RevisionSummary 与页面/章节真实 wire 契约；
5. 规范纯容器背景/边框判定为 `NOT_VERIFIABLE`，消除伪对比度缺陷；
6. 优化探针执行链为单次执行，并在 PRE-01 引入深度结构与枚举校验；
7. 重构 `run-webview.ps1` 采用内存缓冲纯 LF 输出，根除 Windows PowerShell 5.1 下的 trailing-whitespace 报警。

## 2. DSH r2 Findings 逐项处置对照表

| Finding 编号 | 严重度 | 核心问题 | 修订处置与证据 |
|---|---|---|---|
| **G-01 / F-05** | P2 | 证据 provenance 与交付 Hash 自引用死结 | `p02-harness-results.json` 移除自引用 delivery hash 占位，如实记录当前检出的 `source_head`、`source_tree` 与关键源码文件 SHA-256 清单 (`key_source_files_sha256`)；明确区分测试运行输出与后续提交的 delivery commit，指出 Codex 将在新提交产生后于 clean detached exact head 独立复跑验证。 |
| **G-02 / F-08** | P3 | `live_bg_hex` 硬编码，缺乏真实半透明合成 | 消除硬编码 `#101418`，背景色从 fixture 中按语义角色 (`role == "app_base_background"`) 动态查找；引入 `synthetic_alpha_cases`（真实提取自 `RegionOverlay.tsx:45, 47` 的 `rgba(126, 178, 135, 0.16)` 与 `rgba(251, 191, 36, 0.16)`），在已知底色上执行 `blend_alpha` 运算；对缺失已知不透明底色的半透明元素判定为 `NOT_VERIFIABLE`。 |
| **G-03 / F-10** | P3 | AC4 `retype` 操作违反 UI 状态机规则 | `relabelMachine.ts` 源码明确限制仅允许 `speech` ↔ `sfx` 双向转移（其他转移被禁用）。将 AC4 fixture 中的 `retype` 操作由原 `speech -> narration` 修正为合法的 `speech -> sfx`。 |
| **G-04 / F-10** | P3 | 契约字段未完全对齐真实 wire 结构 | 补充 `RevisionSummary` 真实字段（`created_at`, `region_type`, `sfx_policy`, `is_current`）；将书/章/页属性名统一对齐 wire 契约（`book_id`, `chapter_id`, `page_id`, `chapter_number` 作为 string 等）。 |
| **G-05** | P3 | 纯容器背景与边框被误判为文本对比度缺陷 | 容器背景（如 `#161b22`）与边框（如 `#30363d`）在没有独立文本配对时，不能作为文本对比度计算。将其判定为 `contrast_result: NOT_VERIFIABLE` 并说明原因，消除伪对比度缺陷。 |
| **G-06** | P3 | PRE-02 重复执行静态探针，PRE-01 缺乏深度断言 | PRE-02 优化为单次执行链，直接消费静态探针生成的 JSON 报告，避免重复执行；PRE-01 引入深度结构与枚举断言，在根部阻断契约漂移。 |
| **G-07** | P3 | PowerShell 5.1 生成 CRLF 与 trailing-whitespace | `run-webview.ps1` 使用内存缓冲与 `[System.IO.File]::WriteAllText` 确保生成纯 LF 换行的 `probe-execution.log`，彻底根除 trailing-whitespace 报警；明确区分 `-ProbeOnly` 与完整执行模式，聚合传播子探针退出码。 |

## 3. 验收场景执行结果（单一事实来源）

以 [`verification/P02/p02-harness-results.json`](../../verification/P02/p02-harness-results.json) 记录为准：

| 场景标识 | 场景名称 | 判定 | 执行层 | 退出码 | 关键记录 / 阻断原因 |
|---|---|---|---|---|---|
| `PRE-01` | 合成 Fixture 契约完整性 | **PASS** | `FILESYSTEM` | 0 | 验证 books, chapters, pages, regions, post_write_scenarios, tokens, palette 深度契约与 relabelMachine 规则完整 |
| `PRE-02` | 静态源码契约控制检查 | **PASS** | `STATIC_AST` | 0 | 验证 `resolveDebounceMs=300`, `regionDebounceMs=300`, App 导航测试 ID 均符合契约 |
| `PRE-03` | 视觉 F Token / 内联色数学模型 | **PASS** | `TOKEN_MODEL` | 0 | 方向 F Token 真实计算：`ink` 14.72:1、`ink-2` 7.45:1、`ink-3` 5.57:1、`ink-dis` 3.55:1、`accent` 3.53:1；Live 内联正文 `#d8e0e8` 13.87:1 (`token_mapping: UNMAPPED`)；半透明色合成计算正确 |
| `AC1` | 真实 WebView2 启动与证明 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | **Hard Build Barrier 生效**：等待 Codex 登记 scratch worktree 及受信构建路径 |
| `AC2` | Workbench 导航与真实输入 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |
| `AC3` | 300ms 静默期与页面失效窗口 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |
| `AC4` | 写后刷新即时性 (retype/undo/restore) | **BLOCKED** | `REAL_WEBVIEW_MOCK_IPC` | `null` | 依 Task 契约严禁以 NOT_RUN 替代，如实标记为 BLOCKED |
| `AC5` | 键盘操作与焦点链 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |
| `AC6` | 真实运行时 Computed Color 提取 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |

**总计 9 项场景**：**PASS: 3 项，BLOCKED: 6 项，FAIL: 0 项，NOT_RUN: 0 项**。

## 4. 交付文件清单

- [`verification/P02/fixtures/workbench_synthetic_data.json`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/fixtures/workbench_synthetic_data.json)
- [`verification/P02/probes/env_identity_probe.py`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/probes/env_identity_probe.py)
- [`verification/P02/probes/static_control_probe.py`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/probes/static_control_probe.py)
- [`apps/desktop/frontend/e2e/workbench_driver_protocol.ts`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/apps/desktop/frontend/e2e/workbench_driver_protocol.ts)
- [`verification/P02/harness/workbench_cdp_harness.py`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/harness/workbench_cdp_harness.py)
- [`verification/P02/run-webview.ps1`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/run-webview.ps1)
- [`verification/P02/probe-execution.log`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/probe-execution.log)
- [`verification/P02/env-identity-report.json`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/env-identity-report.json) / [`.txt`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/env-identity-report.txt)
- [`verification/P02/static-control-report.json`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/static-control-report.json) / [`.txt`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/static-control-report.txt)
- [`verification/P02/p02-harness-results.json`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/p02-harness-results.json) / [`.txt`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/p02-harness-results.txt)
- [`verification/P02/RESUME.md`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/RESUME.md)
- [`doc/tasks/P02.md`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/doc/tasks/P02.md)
- [`doc/handoffs/P02-stage-a-foundation-handoff.md`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/doc/handoffs/P02-stage-a-foundation-handoff.md)

## 5. 推荐下一步

提交固定交付 commit，由 Codex 在 clean detached exact head 独立复跑 Stage A probes 并完成 Gate 复算；交由 DeepSeek Harness 进行 Stage A r3 复审。待隔离 scratch worktree 构建方案获批后，再推进 Stage B 真实 WebView2 运行时验证。
