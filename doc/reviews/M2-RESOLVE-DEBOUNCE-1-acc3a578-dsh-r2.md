## 审查方式声明（证据边界）

本轮严格只读，未修改任何文件。本会话 `pwsh` 在 workspace-write 下仍以 `SetNamedSecurityInfoW failed (Win32 5): grantWrite` 失败，`danger-full-access` 升级被拒（无审批通道）⇒ **无法执行 git 命令**。替代手段（可复核）：① 直读 worktree reflog `G:/CODEX/New Manga/.git/worktrees/RESOLVE-DEBOUNCE-1/logs/HEAD`（仓库外路径可读）恢复提交链；② 只读核对 raw 日志与 `change-surface-binding-1.log` 的 porcelain；③ 行号重建法（以 r1 报告记录的 a7a3462d 行号图为基线做偏移量核算）；④ 全仓 grep 标记法。凡需 git 才能定论的项已标注（N-02）。

VERDICT: approve

## 逐项判定

| 项 | 判定 | 证据 |
|---|---|---|
| C-1（PR-01，P3） | **fixed（①；②归集成收口）** | `doc/tasks/M2-RESOLVE-DEBOUNCE-1.md:31` 已改为「region 读循环依赖 `[clients, pageId, refreshRegions]` 同样逐键重跑 invoke `list_regions`，属既有行为类别，本刀不闭合——逐键 region IPC 与 `regions` 错误条闪烁显式保留为 deferred 后续候选」；与实现事实逐条相符：`WorkbenchPage.tsx:407` `refreshRegions useCallback([clients])` 稳定引用 + `:416` 读循环 deps + `:391` `listRegions(trimmed)` + `:852` `regions: ${regionError}`。 |
| C-2（PR-04，P4） | **fixed（证据强于 r1 要求）** | `raw/change-surface-binding-1.log:4-6` = `M WorkbenchPage.test.tsx` / `M WorkbenchPage.tsx` / `A doc/tasks/M2-RESOLVE-DEBOUNCE-1.md`（Task 文档来自 release commit `9c7efc3d`，与任务书预期「两文件+Task 文档」完全一致）；`:7-11` porcelain = `M test.tsx` / `M Task` / `?? r1 报告` / `?? 本日志`——这份 porcelain 恰好就是 acc3a578 的改动面，信息量大于 r1 要求的「空 porcelain」。 |
| PR-02（P3） | **fixed** | `WorkbenchPage.test.tsx:1020-1022` 在 `advanceTimersByTime(300)`（`:1025`）**之前**断言 `resource-resolve-busy` 非空；impl `:957` 该元素仅在 `resourceResolveBusy` 为真时渲染 ⇒ 判别力成立（把 `setResourceResolveBusy(true)` 挪进 `fireResolve` 即红）。既有 `:781` 的 `toBeNull()` 断言保留。 |
| PR-03（P4） | **accepted** | impl `:365-368` 与用例 2（`:1041-1071`）在本轮零改动；结论与 r1 相同——第二层 `cancelled` 仍由 0ms 用例 `:811` 覆盖、守卫代码 pre-image 同源，本刀不返修。 |

## 新发现

**N-01（P4，文档口径）** Handoff disposition 表 C-2 行把 porcelain 描述为「**干净**」，但日志实际为 2×`M` + 2×`??`；同表/AC 表若沿用「日志 HEAD 全为 `acc3a578`」亦会把第 5 份日志说错。该日志 `:2` 自述 `HEAD=3eb620c5`，而 `3eb620c5` 是 acc3a578 的**父提交**（reflog 第 5、6 行）——因为绑定日志是 **pre-commit 捕获**，属正常且不影响 diff 范围（`adabd913..a7a3462d` 为不可变 commit 区间）。建议收口时改为精确口径：「4 份重跑日志 @`acc3a578`；变更面绑定日志于父提交 `3eb620c5` 工作树捕获（pre-commit）」。

**N-02（P4，证据自证边界）** 四份 @`acc3a578` 重跑日志自身仍**不带** `git status --porcelain`／tree 绑定——C-2 类绑定只在交付区间 `adabd913..a7a3462d` 上闭合。本轮以「父提交 porcelain = acc3a578 改动面」+ reflog + 行号重建替代证实，结论不受影响；建议集成 post-merge 复跑时把 `git rev-parse HEAD` + `git status --porcelain` 一并入库（一条命令）。

**N-03（P4，可追溯性）** a7a3462d 时代的 4 份 raw 日志已被 `b4a8d219` **原地同名覆盖**，r1 当时读到的版本现存于 `3eb620c5:verification/M2-RESOLVE-DEBOUNCE-1/raw/`。建议收口记录注明该溯源点，避免后续读者误以为 r1 数字无从复核。

## 核对过、未发现问题的关键点

1. **提交链（reflog 实证）**：`adabd913`(base) → `9c7efc3d`(Task release) → `a7a3462d`(交付) → `3eb620c5`(docs：handoff+首轮 raw logs) → `acc3a578`(返修) → `b4a8d219`(HEAD，docs：disposition+重跑日志)。**任务书未提到的中间 docs commit `3eb620c5` 确实存在且仅含文档**，它同时解释了绑定日志的 HEAD 值。
2. **增量核算：impl 零增量**。acc3a578 前捕获的 porcelain 只列 `test.tsx` + Task 文档（impl 未列）；r1 记录的 impl 行号图在当前树**逐条命中**（`:48/:322/:339/:369/:391/:407/:416/:851-852`）⇒ `WorkbenchPage.tsx` 与 r1 审的 a7a3462d 版本同源，本刀未再触碰实现。
3. **测试文件「只加断言、不删既有断言」**：case 1 起点仍 `996`（前方零位移）；case 1 跨度 41→44 行；case 2 `1038→1041`、末条 `it` 位移至 `1073`、文件 `1096→1099`——所有位移恰为 **+3**，即 `1020-1022` 的注释 2 行 + 断言 1 行，无删除、无其他插入；r1 记录的 case 1 锚点（`resolveCalls` 0 次、`{pageId:"page-1"}`、喂图）全部在且位移一致。等行数改写无法在无 git 下排除，但已无可用反证空间。
4. **四份重跑日志全部自述 `HEAD=acc3a578524407b7cce7e3502349c9b2e32e3e22` 且数字不变**：`vitest` 12 files / WP 33 tests / **138 passed** / EXIT=0；`build` 50 modules / EXIT=0；`pytest` **1886 passed, 1 skipped, 3 warnings** / EXIT=0；`cargo` running 56 → **55 passed; 0 failed; 1 ignored** / EXIT=0。当前 WP 测试文件恰 33 个 `it(`，与 vitest 的 33 相符。
5. **零 Python/Rust/契约改动**：全仓 grep `M2-RESOLVE-DEBOUNCE-1` / `resolveDebounceMs` 仅命中 2 个 TS 文件 + Task/Handoff/Review/日志；diff 名单无 `.py`/`.rs`/契约文件。
6. **产品默认路径未被测试注入替代**：`WorkbenchPage.tsx:80` `resolveDebounceMs = 300`，`App.tsx:517` `<WorkbenchPage />` 不传 prop ⇒ 300ms 分支即产品路径；测试默认 0（`test.tsx:111`）仅保住既有 31 用例的即时时序。
7. **新断言确定性与 fake-timer 纪律**：断言在 `act` 内、fake timers 未推进（busy 窗口必然存续）；`try/finally` 双层 `vi.useRealTimers()`（`:1001/:1036-1038`，`unmount()` 亦有）与既有 expires-undo 用例同款；实测 138 全绿支持无 flake。
8. **C-1 措辞依据复核**：`refreshRegions` 的 `useCallback` deps 为 `[clients]`（`:407`），读循环 deps 含 `pageId`（`:416`）⇒ 「逐键重跑 list_regions」是事实，「属既有行为类别、本刀不闭合」措辞准确。
9. **口径更正（与任务书前提不符，非缺陷）**：本 worktree **存在** `doc/STATUS.md`（base 版），其 Planned next 第 ① 项仍是本 Task 的 release 候选，**尚无** region 逐键 debounce 的 deferred 条目 ⇒ C-1② 的登记确实尚未落地，属集成收口内容（与任务书「由集成收口承载」一致）。

## 集成收口必须闭合（非返修项）

1. `doc/STATUS.md` Planned next 增补「region 读循环逐键 `list_regions`/`regions` 错误条闪烁」显式 deferred 条目（C-1②）。
2. 集成 commit 内附 post-merge 复跑日志 + `git status --porcelain`/`rev-parse HEAD`（N-02），并把 handoff 的「porcelain 干净 / HEAD=acc3a578」口径按 N-01 更正。
3. 按 r1 推荐释放下一最高优先候选 **②derived 预览按引用回收（RC4-12 轮换增长主路径）**，Owner=Codex Executor（ZCode 代行）、Reviewer=DeepSeek Harness（非作者）、Integrator=Codex，范围须含「page 关联或 grant 联动」设计冻结。

**推荐下一步（基于当前仓库状态）**：由 Integrator（Codex）以 `acc3a578`/`b4a8d219` 为交付 tip 执行收口——闭合上列 1/2 后 merge main → post-merge 三套件等量复跑（vitest 138 / build EXIT=0 / pytest 1886+1sk / cargo 55+1ign）→ 更新 STATUS/PLAN；本 Task 的 Review 链（r1 approve_with_conditions → r2 approve）即可按 done 收口。无需第三方返修。
