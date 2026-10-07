---
id: M2-REGION-DEBOUNCE-1
title: Workbench region 读循环逐键 debounce（RESOLVE-DEBOUNCE r1 C-1 登记残留闭合）
kind: fix
status: in_review
delivery_commit: 2891c886
handoff: ../handoffs/M2-REGION-DEBOUNCE-1-zcode-2891c886.md
approval: user_2026-10-07_autonomous_mode_continuation（STATUS Planned next 候选①，授权自动选下一最高优先任务）
suggested_owner: Codex Executor
owner: Codex Executor（ZCode 代行）
reviewer: DeepSeek Harness（非作者）
integrator: Codex
depends_on: [M2-RESOLVE-DEBOUNCE-1]
base_commit: 9d5d9aa6
branch: zcode/region-debounce-1
worktree: G:/CODEX/New Manga.worktrees/REGION-DEBOUNCE-1
integration_commit: null
---

# M2-REGION-DEBOUNCE-1

## 来源与目标

RESOLVE-DEBOUNCE-1 DSH r1 C-1（P3 条件）：region 读 effect 依赖 `[clients, pageId, refreshRegions]` 且回调稳定——手输 page id 逐字符逐次 invoke `list_regions`（含 regions 错误条逐键闪烁），与 resolve 逐键问题同构（PAGE-RESOLVE r1 PR-10 原文即写明）。本刀给该 effect 加 **300ms debounce**（同款 prop 模式）；**写后刷新路径（retype/undo/restore 的 refreshRegions 直调）保持即时**。

## 冻结范围

### React（apps/desktop/frontend/src/workbench）
- `WorkbenchPage.tsx`：`regionDebounceMs?: number`（默认 300）；region 读 effect 内 `regionDebounceMs > 0` 走 setTimeout 包裹 `refreshRegions(pageId, signal)`（cleanup clearTimeout+cancelled），否则原路径逐字不变；`refreshRegions` 函数本体零改动（写后刷新直调全部即时）。
- `WorkbenchPage.test.tsx`：mount helper 加 `options.regionDebounceMs`（测试默认 0，既有 33 用例零扰动）；+2 判别用例（fake timers 逐字符 4 键→1 次+参数最后一键；0ms 下 retype 后写后刷新仍即时≥2 次）。
- **明确不做**：`refreshRegions` 函数本体/写后刷新调用点零改动；Core/Rust/契约零接触；image/下钻循环不涉及。

## 验收 Gate

1. AC1 前端：2 新判别用例+既有用例零扰动；vitest 全绿 + build EXIT=0。
2. AC2 回归：全量 pytest 等量（1886 基线）、cargo 基线不变（零 Python/Rust）。
3. 非作者 Review（DSH）通过。

## 完成定义

AC 全过 + Review 通过 + 集成 merge main + STATUS/PLAN 收口。

## 交付记录（闭环后回填）

- Delivery `2891c886`（release 范围与本文件同 commit 入库——Task 文件创建晚于代码交付，Handoff base 注明 `9d5d9aa6`）。
