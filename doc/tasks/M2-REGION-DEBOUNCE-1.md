---
id: M2-REGION-DEBOUNCE-1
title: Workbench region 读循环逐键 debounce（RESOLVE-DEBOUNCE r1 C-1 登记残留闭合）
kind: fix
status: done
delivery_commit: 2891c886 (code; docs rework 2cfa7e6f)
review: DSH r1 approve_with_conditions @2891c886 -> r2 approve_with_conditions @2cfa7e6f (N-01 wording closed in closeout docs commit per r2 option 2)
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
integration_commit: 0cb15092 (merge; final docs head 80db177d, post-merge 1886+1sk / cargo 55+1ign / vitest 140)
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

## 交付记录（2026-10-07 闭环）

- **Delivery** `2891c886`：`regionDebounceMs` prop（产品默认 300/测试注入 0）+ region 读 effect debounce 外壳（refreshRegions 函数本体零改动——写后刷新直调全部即时）+ 2 用例；vitest 140 / build 0 / full 1886+1sk / cargo 55+1ign。
- **DSH r1** `approve_with_conditions`（PR-01 **P2** 用例 2 判别力不足+反推演不成立，给路径 A/B 二选一；PR-02..05 P4）→ **路径 B 返修** `2cfa7e6f`（用例 2 如实化+scope note；PR-02 裁定改写；PR-04 绑定日志）。
- **DSH r2** `approve_with_conditions`（PR-02/04 fixed、PR-03/05 deferred-accepted；N-01 **P2** Handoff :41/:49 反推演未同步+disposition 自述不符；N-02 rework hash 未落）→ **N-01/N-02 闭合** `80db177d`（按 r2 原文 option 2：精确口径更正由收口 docs commit 承载；rework head 落 pin）。
- **集成** merge `0cb15092`；post-merge 复跑：pytest **1886+1sk+0 failed** / cargo **55+1ign** / vitest **140**，等量全绿+post-merge tree 绑定日志。
- **登记**：手工 resource id/revision 输入逐键 image 读取（PR-03）、region 读 quiet-window busy（PR-05）= deferred 后续候选；300ms 下写后刷新即时性的独立判别用例缺口（PR-01 残留，harness 限制如实登记——结构论证兜底）。
- **移交**：worktree `G:/CODEX/New Manga.worktrees/REGION-DEBOUNCE-1` 保留为证据。
