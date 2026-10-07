# VERDICT: approve_with_conditions

**审查方式声明（证据边界）**：本轮为严格只读审查，未修改任何文件。本会话的 shell 通道不可用（`pwsh` 在 workspace-write 下反复以 `SetNamedSecurityInfoW failed (Win32 5): grantWrite` 失败，`danger-full-access` 升级无审批通道），因此**无法执行 `git diff/log/status`**。替代手段：① 只读核对 raw 日志；② 与同仓库同文件的历史 worktree 做 pre-image 逐行比对（`G:\CODEX\New Manga.worktrees\CATEGORY-CLARIFY-1`，其 HEAD `af640916`，即 STATUS:17 记录的 M2-CATEGORY-CLARIFY-1 验证 head；注意它 **不等于** base `adabd913`，见 C-08）；③ 全仓 grep 标记法定位触碰面。凡需 git 才能定论的项我已标注并给出闭合命令（见 PR-04）。

---

## 逐条发现

### PR-01（P3）冻结范围的「非逐键触发面」理由与事实不符，残留面未显式登记
- 位置：`doc/tasks/M2-RESOLVE-DEBOUNCE-1.md:31`；对照 `apps/desktop/frontend/src/workbench/WorkbenchPage.tsx:410-416`＋`:391`＋`:850-853`
- 事实：`doc/tasks/...:31` 写「region/history/image 循环…（各自已有 requestId 守卫且**非逐键触发面**）」。但 region 读循环的依赖数组是 `[clients, pageId, refreshRegions]`，`refreshRegions` 又是 `useCallback([clients])` 稳定引用 ⇒ **每次击键都重跑并 invoke `list_regions`**（`:391`）。这不是我的推断：**PAGE-RESOLVE-1 DSH r1 的 PR-10 原文自己就写明「与既有 region 读循环同构（`refreshRegions` 亦逐键触发）」**（`doc/reviews/M2-PAGE-RESOURCE-RESOLVE-1-b58bb944-dsh-r1.md:105`），r2 的 deferred 裁定也复述了这一点（`...-ad00dcf3-dsh-r2.md:43`）。
- 残余用户可见面：`workbench-error` 条（`:850-853`）渲染 `regions: <code>`；若 Core 对半成品 pageId 返回 typed 错误，则逐键闪烁换了一条错误条继续存在；即使不报错，逐键 IPC 抖动（本 Task 的问题陈述之一「手输每键一次 IPC」）在 region 面仍然成立。
- 处置（**条件 C-1**）：不改代码（AC 未要求，PR-10 的原始建议文本本身也只指向 resolve，闭刀口径与 PR-10 一致）；但 Integrator 收口时①更正该括号措辞为「region 读循环同样逐键，属既有行为类别，本刀不闭合」；②把该项作为显式 deferred/后续候选登记（STATUS Planned next 现有条目 ⑤ 一带），避免「非逐键触发面」被后续读者当作已覆盖。

### PR-02（P3，覆盖缺口但非 Gate 失败）产品默认 300ms 路径只有 2 条用例覆盖；frozen 的 busy 窗口无任何断言
- 位置：`apps/desktop/frontend/src/workbench/WorkbenchPage.test.tsx:111`（`options.resolveDebounceMs ?? 0`）、`:996-1036`、`:1038-1068`；对照 `WorkbenchPage.tsx:339`
- 反向推演结论（回答你的第 3 问）：**Handoff 设计裁定 1 的辩护成立，但不能覆盖全部差异**。
  - 成立部分（已独立核验）：`fireResolve` 体与 pre-image **逐字一致**——pre-image `CATEGORY-CLARIFY-1/.../WorkbenchPage.tsx:330-345` vs 本 head `WorkbenchPage.tsx:342-357`，`stillCurrent()` 守卫位置、4 处 setState 顺序、`"PAGE_RESOURCE_UNAVAILABLE"` fallback 字面量全部相同；两分支确实共用该闭包与守卫。
  - 辩护**未覆盖**的两点：(a) 冻结范围 `doc/tasks/...:29` 明确写「`resource-resolve-busy` 在输入窗口即显示」，但**全仓只有一处断言 busy**（`test.tsx:781`，且断言的是 `toBeNull()`）——300ms 下「输入窗口即显示」这条被冻结的语义**零断言**，未来若有人把 `setResourceResolveBusy(true)` 挪进 `fireResolve`，31 条既有用例 + 2 条新用例**仍全绿**而产品 UX 已变；(b) `:811`（stale resolve 丢弃）、`:790`（typed 失败回退）、`:842`（下钻自动喂图）等横切行为只在 0ms 配置下验证，而 0ms 是**永不发布**的配置。
- 处置：非阻断（AC1 只要求 2 条判别用例，已满足）。建议二选一：在用例 1 的 `advanceTimersByTime(300)` **之前**加一条 `resource-resolve-busy` 非空断言（一行，直接钉住 frozen 语义），或把 `:811` 改用产品默认 + fake timers。可作为收口顺笔项，不进条件。

### PR-03（P4）cleanup 第二层（`cancelled`）在 debounce 路径下无独立判别用例
- 位置：`WorkbenchPage.tsx:365-368`；`WorkbenchPage.test.tsx:1038-1068`
- 用例 2 切页发生在 `t≈0`（timer 未 fire），因此它**只**钉住 `clearTimeout` 层。设计裁定 2 声称的「两层独立」中，第二层（timer 已 fire、回包未落时切页 → 回包丢弃）在 300ms 配置下没有独立用例。反推确认：只删 `cancelled = true` 而保留 `clearTimeout`，用例 2 **仍绿**。
- 但该层由 0ms 的 `test.tsx:811-845` 覆盖，且回包后的守卫代码与 pre-image 逐字同源，故**可接受、不需返修**。可选加固：把切页放在 `advanceTimersByTime(300)` 之后、`onResolvePage` 的 promise 落地之前。

### PR-04（P4）raw 日志缺少 tree 绑定与变更面绑定，两项 AC 断言无法被 Reviewer 独立复核
- 位置：`verification/M2-RESOLVE-DEBOUNCE-1/raw/{vitest-run,frontend-build,full-pytest,cargo-test}-1.log`
- 事实：4 份日志头部都自述 `HEAD=a7a3462d31e076254ccba172cad39e23b7fe095b` + COMMAND + 尾部 EXIT（一致性 ✓），但**没有** `git status --porcelain`／`git diff --name-status`，因此「数字来自该 commit 的干净树」「零 Python/Rust/契约改动」「既有 31 用例零改动」三项断言在日志内**不可自证**。
- 处置（**条件 C-2**，集成收口前一条命令即可闭合）：
  `git diff --name-status adabd913..a7a3462d`（应恰为 `apps/desktop/frontend/src/workbench/WorkbenchPage.tsx` + `WorkbenchPage.test.tsx`）＋ `git status --porcelain`（空）。这条同时闭合 AC2 的「零 Python/Rust 改动」与 AC1 的「既有用例零改动」。

---

## 核对过、未发现问题的关键点

1. **AC1 证据链成立**：`vitest-run-1.log:20-23` = `WorkbenchPage.test.tsx 33 tests`、12 files、**138 passed**、EXIT=0；与基线 `verification/M2-CATEGORY-CLARIFY-1/raw/vitest-run-1.log:20-23`（31 tests / 12 files / 136）**逐文件计数完全一致**，唯一增量为 WP 31→33。`frontend-build-1.log`：`tsc && vite build` 50 modules、dist 产出、EXIT=0。
2. **AC2 证据链成立（等量判据）**：`full-pytest-1.log:399` = `1886 passed, 1 skipped, 3 warnings`，与 CATEGORY 基线行**逐字同数**；`cargo-test-1.log:24,86` = `running 56 tests` / `55 passed; 0 failed; 1 ignored`，与 PAGE-NAV-PROJECTION-1、DERIVED-GC-1、CATEGORY-CLARIFY-1 三份基线一致；唯一 warning 是既有 `unused import: CHUNK_SIZE`（`main.rs:883`），非本刀引入。
3. **`fireResolve` 闭包提取为纯搬运**：见 PR-02 的逐行比对（pre-image `:330-345` ≡ head `:342-357`）。
4. **debounce 外壳正确**：`:359-364` `resolveDebounceMs > 0` 走 `setTimeout`，否则立即调用；`timer` 以 `undefined` 初值 + cleanup 条件判断，0/负/NaN 一律退化为立即路径（对内部 prop 足够）。
5. **cleanup 时序无缺陷**：`:366-367` 先 `cancelled = true` 再 `clearTimeout`——单线程下顺序无语义差异；对已 fire 的 timer `clearTimeout` 为 no-op；unmount 由本 effect 自身 cleanup 覆盖，`:472-481` 的 unmount-only effect 不需要也不重复处理 resolve timer。
6. **依赖数组完整**：`:369` `[clients, pageId, resolveDebounceMs]` 齐全（`setState` 稳定，无需列入）。关键副作用已核：`:339` 的 `setResourceResolveBusy(true)` 引发的重渲染**不会**重置 timer（deps 未变）；生产路径 `App.tsx:517 <WorkbenchPage />` 不传 `invoke`/`resolveDebounceMs` ⇒ `clients`（`useMemo([invoke])`）与 ms 值恒定，不存在「每渲染重排 timer、永远不 fire」的隐患。
7. **判别力反向推演（逐条对应你的第 3 问）**：
   - 删 `setTimeout` 外壳（`fireResolve` 直调）→ **`test.tsx:1019` 红**（实际 4 次）；且若实现退化为「只排第一次击键」，`:1027` 的参数断言 `{pageId: "page-1"}` 会红（首键为 `"p"`）——即用例 1 同时钉住「合并」与「最后一键胜出」。
   - 删 cleanup `clearTimeout` → **`test.tsx:1059` 红**（实际 2 次；因 page-1 的 timer 先入队，`:1061` 的参数断言也会红——page-1 的 `fireResolve` **无条件发 invoke**，`cancelled` 只拦 then/catch，我已逐行确认）。
   - 只删 `cancelled = true` → 用例 2 恒绿（见 PR-03）。
8. **「既有用例零改动」成立**：head 的 33 个 `it` 中，前 31 个标题与 pre-image 的 31 个标题**同名同序**（grep 逐条比对），新增 2 条插在末条 pre-existing 用例之前；总行数 1018→1096（+78）与「helper +4 行、2 用例 +73 行」算术自洽。新增用例未触及既有断言。
9. **fake timers 纪律与既有先例一致**：新用例 `try/finally + vi.useRealTimers()`，且 helper 的 `unmount()` 本就调用 `vi.useRealTimers()`（`:141`）——与既有 expires-undo 用例（`:600-616`）同款纪律，且新用例额外加外层 `finally`（更严，可覆盖 mount 抛异常路径）。`vi.useFakeTimers()` 在 JSDOM/global stub 之前调用不影响 `nextTurn()` 的纯微任务推进（实测 138 全绿）。
10. **busy 显示窗口与 frozen 语义一致**：`:339-340` 在 timer 之前置 busy/清 error，「输入窗口即显示」按 spec 落地；`onPageIdChange` 的立即清屏（`:542-545` + image effect `:420-470` 随即清图）与「切页即时清空、解析延后 300ms」相符。文案在 quiet period 内严格说是 pending 而非 resolving，属 spec 已冻结的取舍，仅作观察、不作缺陷。
11. **StrictMode / 双挂载**：`main.tsx:4` 明确注释「No StrictMode: the ?probe=1 evidence matrix must execute exactly once」，本应用不启用；即便未来启用，双挂载只会「装 timer → cleanup 取消 → 再装 timer」，**不会双发 invoke**。
12. **同步抛错语义未被 setTimeout 改变**：`LibraryClient.resolvePageResource` 是 `async`（`library/client.ts:75`），任何同步 throw 都转为 rejected promise，因此把调用搬进 timer 回调**不会**把原本 effect 内的同步异常变成 timer 回调里的未捕获全局错误（`:87-93` catch 覆盖）。
13. **越界核查**：全仓 grep `M2-RESOLVE-DEBOUNCE-1` 仅命中 2 个 TS 文件（`WorkbenchPage.tsx:48,322` / `WorkbenchPage.test.tsx:996,1038`）+ Task/Handoff 文档；无 Python/Rust/契约文件引用或改动痕迹；TS 侧唯一进程外契约调用 `resolve_page_resource` 的 wire 名与参数形状未变（`library/client.ts:33,77`）。

---

## 结论

- Gate 判定：**AC1 PASS**（138/138 + build EXIT=0 + 2 条判别用例反向推演成立）、**AC2 PASS（等量判据）**（pytest 1886+1sk 与 cargo 55+1ign 均与基线等量）、**AC3**＝本 Review（0×P0/P1/P2；1×P3 文档/残留面登记 + 2×P3 覆盖观察 + 2×P4）。
- 放行条件（均为文档/证据层，不要求代码返修）：
  - **C-1**：更正 `doc/tasks/M2-RESOLVE-DEBOUNCE-1.md:31` 的「非逐键触发面」措辞，并把 region 读循环逐键 IPC / `regions: <code>` 错误条闪烁显式保留为 deferred 登记（PR-01）。
  - **C-2**：集成收口附 `git diff --name-status adabd913..a7a3462d` 与 `git status --porcelain` 原始输出，闭合「零 Python/Rust/契约改动」与「既有用例零改动」（PR-04）。

**推荐下一步（基于当前仓库状态）**：将该 Review 定稿落 `doc/reviews/M2-RESOLVE-DEBOUNCE-1-a7a3462d-dsh-r1.md`，由 Integrator（Codex）在收口 commit 内闭合 C-1/C-2 → merge main → post-merge 复跑三套件等量并更新 STATUS/PLAN；随后按授权释放下一最高优先候选 **②derived 预览按引用回收（RC4-12 轮换增长主路径）**，Owner=Codex Executor（ZCode 代行）、Reviewer=DeepSeek Harness（非作者）、Integrator=Codex，范围须含「page 关联或 grant 联动」设计冻结，并在 Gate 中保留本轮教训（回归面须同时覆盖产品默认配置、测试注入默认值不得替代产品默认路径的语义断言）。
