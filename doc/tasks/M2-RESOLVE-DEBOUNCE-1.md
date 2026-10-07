---
id: M2-RESOLVE-DEBOUNCE-1
title: Workbench 页资源解析逐键 debounce（PAGE-RESOLVE r1 PR-10 deferred 闭合）
kind: fix
status: done
delivery_commit: acc3a578 (rework; initial delivery a7a3462d)
handoff: ../handoffs/M2-RESOLVE-DEBOUNCE-1-zcode-a7a3462d.md
approval: user_2026-10-07_autonomous_mode_continuation（STATUS Planned next 候选①，授权自动选下一最高优先任务）
suggested_owner: Codex Executor
owner: Codex Executor（ZCode 代行）
reviewer: DeepSeek Harness（非作者）
integrator: Codex
depends_on: [M2-PAGE-RESOURCE-RESOLVE-1]
base_commit: adabd913
branch: zcode/resolve-debounce-1
worktree: G:/CODEX/New Manga.worktrees/RESOLVE-DEBOUNCE-1
integration_commit: 65d500e6 (merge; final head b4a8d219, post-merge 1886+1sk / cargo 55+1ign / vitest 138)
---

# M2-RESOLVE-DEBOUNCE-1

## 来源与目标

PAGE-RESOLVE-1 DSH r1 PR-10（deferred 登记）：Workbench resolve effect 对 `pageId` 逐字符触发 `resolve_page_resource`（手输调试场景每键一次 IPC，含逐字符 PAGE_NOT_FOUND 错误闪烁与无谓的发布尝试）。本刀给该 effect 加 **300ms debounce**：停止输入 300ms 后才发起解析；effect 清理（切页/卸载/新键入）取消挂起 timer。产品 UX 改善，零契约面。

## 冻结范围

### React（apps/desktop/frontend/src/workbench）
- `WorkbenchPage.tsx`：新增可选 prop `resolveDebounceMs?: number`（**默认 300**）；resolve effect 内 `setTimeout` 包裹发起、cleanup `clearTimeout`（与既有 cancelled 守卫叠加——timer 触发后才发 invoke，迟到回包仍由 `stillCurrent()` 复检）。busy 指示随 timer 启动（`resource-resolve-busy` 在输入窗口即显示，解析发起后保持至回包——不变语义）。
- `WorkbenchPage.test.tsx`：`mountInteractiveWorkbench` 增加 `options.resolveDebounceMs`（**测试默认 0**=既有用例零时序扰动）；新增判别用例：debounce=300 + `vi.useFakeTimers`，逐字符输入 4 键只触发 **1 次** `resolve_page_resource`（原实现为 4 次），advance 后发起且正常喂图；既有 3 个 resolve 用例与 2 个下钻用例零改动全绿。
- **明确不做**：region/history/image 循环不加 debounce（各自已有 requestId 守卫；**r1 C-1 更正：region 读循环依赖 [clients, pageId, refreshRegions] 同样逐键重跑 invoke list_regions，属既有行为类别，本刀不闭合**——逐键 region IPC 与 regions 错误条闪烁显式保留为 deferred 后续候选）；Core/Rust/契约零接触；`onPageIdChange` 的立即清屏语义不变（切页即时清空，只是解析延后）。

## 验收 Gate

1. AC1 前端：新判别用例（逐字符 4 键→1 次调用）+ 既有用例零扰动全绿；vitest 全绿 + build EXIT=0。
2. AC2 回归：全量 pytest 等量（1886 基线）、cargo 基线不变（零 Python/Rust 改动）。
3. 非作者 Review（DSH）通过。

## 完成定义

AC 全过 + Review 通过 + 集成 merge main + STATUS/PLAN 收口。

## 交付记录（2026-10-07 闭环）

- **Delivery** `a7a3462d`：`resolveDebounceMs` 可选 prop（产品默认 300/测试注入 0）+ resolve effect debounce 外壳（fireResolve 闭包逻辑逐字不变）+ 2 条 fake-timers 判别用例（逐字符 4 键→1 次调用+quiet 窗口 busy 显示；切页取消挂起 timer）；vitest 138 / build 0 / full 1886+1sk / cargo 55+1ign。
- **DSH r1** `approve_with_conditions`（0×P0/P1/P2；C-1 Task「非逐键触发面」措辞更正+region 逐键残留 deferred 登记、C-2 变更面绑定日志、PR-02 busy 窗口断言顺笔、PR-03 accepted）→ **返修** `acc3a578`（C-1/C-2/PR-02 全闭；r1 报告入库）。
- **DSH r2** `approve`（C-1/C-2/PR-02 全 fixed 判定；判别力逐条反向推演复核；N-01..03 P4 记账精度）。
- **集成** merge `65d500e6`；post-merge 复跑：pytest **1886+1sk+0 failed** / cargo **55+1ign** / vitest **138**，等量全绿；post-merge tree 绑定日志入库（N-02）。
- **登记**：region 读循环逐键 invoke `list_regions`（与 regions 错误条闪烁）为 deferred 后续候选（r1 C-1——与本刀同类既有行为，需要同款 debounce+判别用例时一并做）。
- **移交**：worktree `G:/CODEX/New Manga.worktrees/RESOLVE-DEBOUNCE-1` 保留为证据。
