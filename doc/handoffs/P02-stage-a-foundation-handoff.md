---
task_id: P02
title: 真实 Workbench WebView 行为、300ms 刷新与对比度验证 (Stage A Safe Foundation Handoff)
status: in_progress
stage: STAGE_A_SAFE_FOUNDATION
author: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
worktree: G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity
branch: agent/antigravity/P02-real-webview-harness
base_commit: 241ff3b70b6fc0490ea238efd486cc707f849031
scope_contract_sha256: 27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425
created_at: 2026-10-09T14:27:00+08:00
---

# P02 Stage A 安全基底 (Safe Foundation) 交付报告

## 1. 阶段概述

本阶段为 P02 真实 Workbench WebView2 行为验证 Harness 的 **Stage A: Safe Foundation** 实施交付。在恪守 **Hard Build Barrier**（禁止在本 Owner 工作树运行 Cargo/Tauri/Sidecar 构建）的前提下，完成了所有与构建解耦的脚手架、合成数据、只读环境探针、前端 E2E 驱动协议与 CDP 验证运行器。

## 2. 交付产物清单与 AC 映射

| 文件路径 | 归属类别 | 对应 AC | 描述 |
|---|---|---|---|
| `verification/P02/fixtures/workbench_synthetic_data.json` | 合成 Fixture | AC2, AC3, AC4, AC6 | 隔离的合成漫画书籍、章节、页面、区域数据，AC4 写后刷新场景定义及视觉方向 F Token 规范 |
| `verification/P02/probes/env_identity_probe.py` | 环境与身份探针 | AC1, AC7 | 采集 Windows OS、Edge WebView2 Runtime (154.0.4258.62)、Git HEAD/Tree/Branch、构建输出目录存在状态与硬构建屏障状态 |
| `verification/P02/probes/static_control_probe.py` | 静态契约探针 | AC2, AC3, AC4 | 静态核验 WorkbenchPage 默认防抖参数 (`resolveDebounceMs=300`, `regionDebounceMs=300`) 及 App.tsx 视图切换与导航选择器 |
| `apps/desktop/frontend/e2e/workbench_driver_protocol.ts` | 前端 E2E 驱动协议 | AC1–AC7 | 定义真实 WebView2 运行时断言、单调时钟静默期时序测量、写后刷新即时性检验、键盘焦点遍历及 WCAG 2.1 相对亮度/对比度算法 |
| `verification/P02/harness/workbench_cdp_harness.py` | 行为验证 Harness | AC1–AC7 | 结构化调度 AC1–AC7 场景，管理 CDP 通信并输出符合固定格式的判定证据文件 |
| `verification/P02/run-webview.ps1` | 综合运行脚本 | 全部 | 提供一键运行探针、静态检查与 Harness 的 PowerShell 入口，支持 `-ProbeOnly` 模式 |
| `verification/P02/env-identity-report.{json,txt}` | 验证证据 | AC1 | 只读环境探针执行输出报告 |
| `verification/P02/static-control-report.{json,txt}` | 验证证据 | AC3, AC7 | 前端静态契约控制组执行输出报告 (PASS) |
| `verification/P02/p02-harness-results.{json,txt}` | 验证证据 | AC1–AC7 | 行为验证 Harness 执行输出报告 (3 PASS, 6 BLOCKED) |
| `doc/tasks/P02.md` | 任务追踪 | N/A | 更新实际交付与执行记录 |

## 3. 验收场景执行结果摘要

| 场景标识 | 场景名称 | 判定 | 执行层 | 退出码 | 关键记录 / 阻断说明 |
|---|---|---|---|---|---|
| `PRE-01` | 合成 Fixture 完整性 | **PASS** | `FILESYSTEM` | 0 | 包含 books, chapters, pages, regions, scenarios, tokens |
| `PRE-02` | 静态源码契约检查 | **PASS** | `STATIC_AST` | 0 | `resolveDebounceMs=300`, `regionDebounceMs=300`, App 导航测试 ID 均符合契约 |
| `AC1` | 真实 WebView2 启动与证明 | **BLOCKED** | `REAL_WEBVIEW2` | 126 | **Hard Build Barrier 生效**：等待 Codex 登记 scratch worktree 及受信 sidecar 构建路径 |
| `AC2` | Workbench 导航与真实输入 | **BLOCKED** | `REAL_WEBVIEW2` | 126 | 同上，无受信任可运行二进制 |
| `AC3` | 300ms 静默期与页面失效窗口 | **BLOCKED** | `REAL_WEBVIEW2` | 126 | 同上，无受信任可运行二进制 |
| `AC4` | 写后刷新即时性 (retype/undo/restore) | **BLOCKED** | `REAL_WEBVIEW_MOCK_IPC` | 126 | 依 Task 契约严禁以 NOT_RUN 替代，如实标记为 BLOCKED |
| `AC5` | 键盘操作与焦点链 | **BLOCKED** | `REAL_WEBVIEW2` | 126 | 同上，无受信任可运行二进制 |
| `AC6` | 视觉 F Token 数学模型对比度 | **PASS** | `TOKEN_MODEL` | 0 | 正文对比度 14.28:1 (要求 $\ge 4.5:1$)，次要文本对比度 5.76:1 (要求 $\ge 3.0:1$) |
| `AC6` | 运行时 Computed Color 提取 | **BLOCKED** | `REAL_WEBVIEW2` | 126 | 同上，无受信任可运行二进制 |

**场景统计**：总计 9 项，**PASS: 3 项，BLOCKED: 6 项，FAIL: 0 项，NOT_RUN: 0 项**。

## 4. 边界与硬构建屏障确认

1. **零源码污染**：未修改 `apps/desktop/frontend/src/**`、未修改 `apps/desktop/src-tauri/**`、未修改依赖清单文件。
2. **零越界数据访问**：未接触任何用户漫画库、SQLite 生产数据或用户凭据。
3. **真实性原则**：绝不使用 JSDOM、普通浏览器、SSR 或 fake timers 冒充真实 Tauri/WebView2 证据。
4. **构建隔离遵守**：在 Codex 完成隔离构建目录与受信 sidecar 规范登记并通过 DeepSeek Harness 审查前，本工作树绝对不运行 Cargo/Tauri 构建。

## 5. 推荐下一步

等待 Codex 审查本 Stage A 交付记录，并在独立隔离环境（scratch worktree）中提供经 DeepSeek Harness 审查批准的可信 Tauri 构建产物与命令；届时通过 P02 Harness 连接 CDP 运行真实 WebView2 动态验证。
