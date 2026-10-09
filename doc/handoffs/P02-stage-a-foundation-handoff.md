---
task_id: P02
title: 真实 Workbench WebView 行为、300ms 刷新与对比度验证 (Stage A 定向修订 Handoff r2)
status: in_progress
stage: STAGE_A_SAFE_FOUNDATION_R2
author: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
worktree: G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity
branch: agent/antigravity/P02-real-webview-harness
base_commit: 241ff3b70b6fc0490ea238efd486cc707f849031
scope_contract_sha256: 27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425
reviewed_head_r1: 972049f991b5c119555647eeea816e89dd4769f3
dsh_decision_r1: changes_requested
created_at: 2026-10-09T15:05:00+08:00
---

# P02 Stage A 安全基底定向修订交付报告 (r2)

## 1. 修订概述

本交付响应非作者实现 Reviewer DeepSeek Harness 对 Stage A r1 交付（`reviewed_head=972049f991b5c119555647eeea816e89dd4769f3`）提出的 `changes_requested` 评审意见及 12 项 findings（F-01 为 P1，F-02–F-07 为 P2，F-08–F-12 为 P3），以及 Codex 独立 Review 发现的 trailing-whitespace 问题。本修订在严格恪守 **Hard Build Barrier** 的前提下，彻底纠正所有定义偏差、数值不一致、字段契约及环境探测缺陷。

## 2. DSH 12 项 Findings 逐项处置对照表

| Finding 编号 | 严重度 | 核心问题 | 修订处置与证据 |
|---|---|---|---|
| **F-01** | P1 | Stage A 范围定位偏差，冒称管理 CDP 通信 | 纠正 Harness docstrings、运行日志与 Handoff 定位为“Stage A preflight/verdict report generator；CDP/行为驱动尚未实现”。清除未使用的 `target_exe`、`cdp_port` 及死导入 `urllib.request`。运行时场景继续规范登记为 `BLOCKED`。 |
| **F-02** | P2 | 夹具颜色非 F Token，部分色值无来源 | 将真实方向 F Token（`bg-page #1a1a1d`、`ink #ececee`、`ink-2 #a9a9b3`、`ink-3 #91919c`、`ink-dis #70707b`、`accent #4d63e8`）与当前 Live 源码内联调色板 (`live_inline_palette`) 彻底分开；内联色逐项标注来源（如 `App.tsx:475`、`PageListPanel.tsx:53`），删除无来源色，未映射者明确标记 `token_mapping: UNMAPPED`。 |
| **F-03** | P2 | 对比度数值手写冲突 | 消除 Handoff 手写数值与报告差异，以机器生成的 [`p02-harness-results.json`](../../verification/P02/p02-harness-results.json) 为单一事实来源（Single Source of Truth），直接链接引用机器计算值。 |
| **F-04** | P2 | 前置控制与 AC6 混淆 | 将数学模型前置检查重命名为 `PRE-03`（layer: `TOKEN_MODEL`）。真实运行时 `AC6`（`runtime_computed_color_extraction`）继续单独登记为 `BLOCKED`，未执行时不出现 PASS；保留 `token_mapping` 与 `contrast_result` 字段。 |
| **F-05** | P2 | 报告 provenance 记录不准 | 报告明确区分行为基线 `241ff3b7…`、被测源码 commit 与 tree、测试命令及工件 hash。在探针中准确采集并记录当前检出对象。 |
| **F-06** | P2 | 未执行场景硬编码 exit_code 126 | 未执行的阻断场景 `exit_code` 设为 `null`。生成含准确命令、PowerShell 5.1/Python 3.14.6/Node v24.15.0/npm 12.0.1 版本头及输出的原始日志 [`probe-execution.log`](../../verification/P02/probe-execution.log)。`run-webview.ps1` 聚合子探针退出码并传播失败。 |
| **F-07** | P2 | RESUME.md 滞后引发重复派发风险 | 保留历史检查点段落，新增当前 Stage A 修订就绪检查点，登记 DSH findings 闭合状态、真实探针结果与下一步指令。 |
| **F-08** | P3 | 数学模型硬编码 RGB，缺乏 alpha 合成 | 从夹具实际读取 hex，实现包含 Alpha Blending 底色合成的 WCAG 2.1 相对亮度与对比度计算算法（`blend_alpha`），并提供 `self_test_contrast_math()` 自检断言。改动夹具色值能直接联动改变计算结果。 |
| **F-09** | P3 | WebView2 GUID 错误，npm 探测静默异常 | 修正 WebView2 Client GUID 为真实的 `{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}`；使用 `npm.cmd` 探测并在异常时显式记录错误而非空串；PowerShell 与 Python 统一使用当前解释器，不重复调用静态探针。 |
| **F-10** | P3 | Fixture 契约与真实 Region wire 不符 | 采用真实 RegionSummary 字段（`region_id`、`revision_no`、`sfx_policy`、`origin`、`geometry`），枚举使用真实值（`speech/narration/sfx` 等，清除 `dialogue/thought` 假名）；补全 `synth-page-102` 区域数据；明确 AC4 `retype`（`set_region_type`）、`undo`（UI 动作底层调 `restore_region_revision`）、`restore`（`restore_region_revision`）的 IPC 请求、返回及 `list_regions` readback 期望；移除顶层 `$schema`。 |
| **F-11** | P3 | TS 驱动协议类型与 Stage A 不匹配 | 修正 `apps/desktop/frontend/e2e/workbench_driver_protocol.ts` 的 layer union 为包含 `FILESYSTEM` / `STATIC_AST` / `TOKEN_MODEL` / `REAL_WEBVIEW2` / `REAL_WEBVIEW_MOCK_IPC` / `BLOCKED_NO_BUILD`；明确标注为 Stage A 契约规范。 |
| **F-12** | P3 | Task 测试表仍写 NOT_RUN/无 | 将已执行的 preflight controls (PASS) 与运行时场景 (BLOCKED) 分行记录，链接到准确报告与日志。 |
| **Codex Whitespace** | N/A | 行尾产生 trailing-whitespace 诊断 | 所有变更/新生成文件统一转换为纯 LF 并去除行尾空格，`git diff --check` 返回 `EXIT=0`。 |

## 3. 验收场景执行结果（单一事实来源）

以 [`verification/P02/p02-harness-results.json`](../../verification/P02/p02-harness-results.json) 记录为准：

| 场景标识 | 场景名称 | 判定 | 执行层 | 退出码 | 关键记录 / 阻断原因 |
|---|---|---|---|---|---|
| `PRE-01` | 合成 Fixture 契约完整性 | **PASS** | `FILESYSTEM` | 0 | 验证 books, chapters, pages, regions, post_write_scenarios, tokens, palette 结构完整 |
| `PRE-02` | 静态源码契约控制检查 | **PASS** | `STATIC_AST` | 0 | 验证 `resolveDebounceMs=300`, `regionDebounceMs=300`, App 导航测试 ID 均符合契约 |
| `PRE-03` | 视觉 F Token / 内联色数学模型 | **PASS** | `TOKEN_MODEL` | 0 | 方向 F Token 真实计算：`ink` 14.72:1、`ink-2` 7.45:1、`ink-3` 5.57:1、`ink-dis` 3.55:1、`accent` 3.53:1；Live 内联正文 `#d8e0e8` 13.87:1 (`token_mapping: UNMAPPED`) |
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

等待 Codex 对本 Stage A r2 定向修订交付进行 Gate 复算与集成复核，并交由 DeepSeek Harness 进行正式复审；待隔离 scratch worktree 构建方案获批后，再推进 Stage B 真实 WebView2 运行时验证。
