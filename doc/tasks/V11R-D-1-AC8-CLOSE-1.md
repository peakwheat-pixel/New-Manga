---
id: V11R-D-1-AC8-CLOSE-1
title: 核证 V11R-D-1 AC8（reduced-motion）在新壳已实现并闭合
kind: governance
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - AC-BLOCKED-CLASSIFY-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 C「AC blocked 项中可归因闭合项」
base_commit: 37c4cf0b3
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/V11R-D-1-AC8-CLOSE-1
allowed_paths:
  - doc/tasks/V11R-D-1-AC8-CLOSE-1.md
  - doc/tasks/V11R-D-1.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/V11R-D-1-AC8-CLOSE-1/**
---

# V11R-D-1-AC8-CLOSE-1：核证 reduced-motion 在新壳已实现

## 来源

`AC-BLOCKED-CLASSIFY-1` 把 `V11R-D-1` AC8 判为 `IMPL` 类（**当前树 live gap**），依据是：
`App.axaml:20` 仍 include 旧 `AppStyles.axaml`，其 `Border.nm-bookcard` 固定 `BrushTransition 0:0:0.12`
使「全应用 reduced-motion 未达」（DEVIATIONS D-12）。

## 调查结论（改变了判定方向）

深入读代码后发现**不是 live gap，而是「旧壳残留 + 新壳已修」**：

| 壳 | 入口 | reduced-motion |
|---|---|---|
| **新壳（产品默认）** `FluentShellSurface` | `App.axaml.cs:233` | **已完整实现**：`MotionTimings.Resolve` 在 reduce 时把 `FeedbackHoverMilliseconds` 归零（`MotionTimings.cs:62`）；`ApplyFeedbackTransitions` 在 attach 与每次 re-resolve 时清除按钮过渡（`FluentShellSurface.axaml.cs:790-820`）；维护 `motion-reduced`/`motion-feedback`/`motion-navigation` class（`:731-737`） |
| 旧壳（`--shell=legacy`） `MainWindow` | `App.axaml.cs:448` | 未响应：`AppStyles.axaml` 的 `Border.nm-bookcard` 固定 0.12s（D-12） |

⇒ `AppStyles.axaml` 的固定过渡**只影响已退役的旧壳路径**，不是产品默认路径的缺陷。

## 目标（一个可观察结果）

AC8 由 `blocked` 改判 `verified`，附「新壳机制点 + 测试通过数 + 旧壳残留如实披露」三项证据。

## Acceptance Criteria

- [ ] **AC1 机制核证**：给出新壳 reduced-motion 的实现点（文件:行），证明 reduce 时反馈过渡时长为 0。
- [ ] **AC2 测试实证**：跑 reduced-motion 相关测试，记录 passed/failed 与耗时、EXIT。
- [ ] **AC3 改判 + 如实披露**：AC8 改判 `verified`；注释同时写明**旧壳 `--shell=legacy` 的残留未响应**，
      不声称「全应用无条件达成」。
- [ ] **AC4 不改代码**：本轮**不修改任何 `.cs`/`.axaml` 生产代码**（只核证与改判）。
- [ ] **AC5 不回归**：全局 `check.ps1` PASS；`verify_pins` 18/18；`api_inventory` 1/80/6=87；
      `verify_final.py` 计数 189→190 verified / 65→64 blocked。
- [ ] **AC6 独立复核**：固定 head 交独立上下文 Review。

## 禁止范围

- 不得为「让旧壳也达成」而改 `AppStyles.axaml` 或旧壳代码（旧壳已按 AD-002 退役）；
- 不得修改 `verification/V11R-D-1/**` 既有证据；
- 不得声称旧壳也满足。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| reduced-motion 测试 | `dotnet test … --filter "FullyQualifiedName~MotionMatrixResidual\|FullyQualifiedName~FluentMotionResidual\|FullyQualifiedName~MotionTimings"` | 13 passed / 0 failed |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## 证据

测试日志与机制核证写入 `verification/V11R-D-1-AC8-CLOSE-1/`。
