# M2-RESOLVE-DEBOUNCE-1 Handoff（Owner→Reviewer/Integrator）

- Owner: Codex Executor（ZCode 代行，持续自治授权）
- Reviewer: DeepSeek Harness（非作者）
- Integrator: Codex
- Task: [M2-RESOLVE-DEBOUNCE-1](../tasks/M2-RESOLVE-DEBOUNCE-1.md)（release 见 Task frontmatter，base `adabd913`）
- Branch/worktree: `zcode/resolve-debounce-1` @ `G:/CODEX/New Manga.worktrees/RESOLVE-DEBOUNCE-1`
- Delivery head: `a7a3462d`（单交付 commit）
- Rework head: `acc3a578`（DSH r1 `approve_with_conditions` 条件闭合+PR-02 顺笔；r1 报告 `doc/reviews/M2-RESOLVE-DEBOUNCE-1-a7a3462d-dsh-r1.md`；**本文件以下数字均以 `acc3a578` 为准**）

## DSH r1 逐项 disposition（r1 @`a7a3462d`；rework `acc3a578`）

| 项 | 级 | 处置 |
|---|---|---|
| C-1（PR-01）Task「非逐键触发面」措辞与事实不符——region 读循环同样逐键 invoke（PR-10 原文即写明同构） | P3 | **fixed**——Task 冻结范围措辞按 r1 口径更正（region 逐键=既有行为类别本刀不闭合）；region 逐键 IPC/错误条闪烁**显式登记 deferred 后续候选**（STATUS Planned next） |
| C-2（PR-04）raw 日志无 tree/变更面绑定，「零 Python/Rust/契约改动」不可自证 | P4 | **fixed**——`raw/change-surface-binding-1.log`（`git diff --name-status adabd913..a7a3462d` 恰为 workbench 两文件+Task 文档+`git status --porcelain` 干净） |
| PR-02 产品默认 300ms 路径 frozen busy 窗口语义零断言 | P3 | **fixed（顺笔）**——用例 1 advance 前补 `resource-resolve-busy` 非空断言（挪走 setBusy 即红） |
| PR-03 cleanup 第二层（cancelled）在 debounce 路径无独立判别用例 | P4 | **accepted**——r1 自证该层由 0ms 既有用例覆盖+守卫代码 pre-image 逐字同源，不需返修 |

## 交付内容（一句话）

PAGE-RESOLVE r1 PR-10（deferred）闭合：Workbench resolve effect 加 **300ms debounce**（`resolveDebounceMs` 可选 prop，产品默认 300、测试可注入 0 保持历史即时时序）——手输 page id 每键不再逐次触发 `resolve_page_resource`（含逐字符 PAGE_NOT_FOUND 闪烁与无谓发布尝试），停止输入 300ms 后恰好一次；effect cleanup 取消挂起 timer（切页/卸载），迟到回包仍由既有 `stillCurrent()` 复检。零 Python/Rust/契约改动。

## 逐层交付（全部 @`a7a3462d`）

### React
- `WorkbenchPage.tsx`：`WorkbenchPageProps.resolveDebounceMs?: number`（默认 300）；resolve effect 提取 `fireResolve` 闭包（`.then/.catch` 与原逻辑逐字相同），`resolveDebounceMs > 0` 时 `setTimeout(fireResolve, ms)` 否则立即调用；cleanup `clearTimeout` + `cancelled = true`；effect 依赖补 `resolveDebounceMs`。busy 语义：输入窗口即显示 `resource-resolve-busy`（等 quiet period），回包后清除——不变。
- `WorkbenchPage.test.tsx`：`mountInteractiveWorkbench` 加 `options.resolveDebounceMs`（**测试默认 0**——既有 31 用例零时序扰动）；**+2 判别用例**（`vi.useFakeTimers`）：①逐字符 4 键→advance 前 resolve 调用 **0** 次（删 debounce 即红——原实现逐键 4 次）→advance 300ms 后恰好 1 次且喂图成功；②quiet period 内切页→旧 timer 被取消，advance 1s 后仅 page-2 一次 resolve（page-1 的挂起 timer 不触发）。

## 验收对照

| AC | 状态 | 证据 |
|---|---|---|
| AC1 前端 | DONE | vitest **138 passed**（CATEGORY 基线 136 + 2 新判别用例；既有用例零改动零扰动）+ `npm run build` EXIT=0；raw 日志 `verification/M2-RESOLVE-DEBOUNCE-1/raw/{vitest-run,frontend-build}-1.log`（HEAD=`acc3a578`） |
| AC2 回归 | DONE | 全量 pytest **1886 passed+1 skipped+0 failed**（基线等量，零 Python 改动）；cargo **55+1ign** 基线不变；raw 日志 `verification/M2-RESOLVE-DEBOUNCE-1/raw/{full-pytest,cargo-test}-1.log`（HEAD=`acc3a578`）+ `change-surface-binding-1.log`（C-2 变更面绑定） |
| AC3 非作者 Review | r2 PENDING | r1 [approve_with_conditions](reviews/M2-RESOLVE-DEBOUNCE-1-a7a3462d-dsh-r1.md)（0×P0/P1/P2；C-1/C-2+PR-02 顺笔已闭，PR-03 accepted）→ DSH r2 |

## 设计裁定（Reviewer 请特别核验）

1. **双轨时序的注入口**：产品默认 300ms、`mountInteractiveWorkbench` 默认 0——既有用例（stale resolve 回包丢弃、下钻自动喂图等）保持 microtask 即时语义零改动；debounce 行为本身由 2 条 fake-timers 专项用例钉住。若 Reviewer 认为「产品默认路径未被既有用例覆盖」是缺口：debounce 分支与立即分支共用同一 `fireResolve` 闭包与守卫，差异仅 setTimeout 外壳。
2. **取消语义分层**：cleanup 里 `clearTimeout`（timer 未 fire=零 IPC）+ `cancelled=true`（timer 已 fire 但回包未落=丢弃回包，既有守卫）——两层独立，quiet period 内切页是纯取消（用例 2 钉住）。
3. **busy 显示窗口**：输入期间即显示 resolving（等 quiet period），300ms 静止后发起——比「输完才显示 busy」更诚实；失败条 `resource: <code>` 只在回包后出现（逐字符闪烁问题随单次调用消失）。
4. **fireResolve 闭包与原逻辑逐字相同**：改动面=调用时机（debounce 外壳），非解析逻辑本身。

## Reviewer 关注点提示

- 实现集中在 `WorkbenchPage.tsx` resolve effect（约 +20 行）；`WorkbenchPagePage.test.tsx` +2 用例（fake timers 局部启用，`finally` 恢复 real timers——与既有 expires-undo 用例同款纪律）。
- 反向推演：删 `setTimeout` 外壳（fireResolve 直接调）→ 用例 1 的 advance 前零调用断言红；删 cleanup 的 `clearTimeout` → 用例 2 红（page-1 挂起 timer 会 fire）。
