## VERDICT: approve_with_conditions

交付代码本身正确、范围与 Task 冻结一致、AC1/AC2 证据链可核验；唯一条件项是**用例 2 的判别力与其 Handoff 反推演声明不符**（不影响产品行为，但影响 AC1「判别用例」的兑现度与文档真实性）。

> 说明：本 worktree 的 shell 被 sandbox 拒绝（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`，`workspace-write` 与一次 `danger-full-access` 提权重试均失败，无审批通道），因此**无法执行 `git diff/show`**。我改用「base 树行级对账 + 只读文件核对」完成审查：base `9d5d9aa6` = main tip（`.git/logs/refs/heads/main:313`），分支自该点创建（`.git/logs/refs/heads/zcode/region-debounce-1:1`），并以 `G:\CODEX\New Manga.worktrees\RESOLVE-DEBOUNCE-1`（前 Task 交付树）作为 base 内容对照。全程只读，未修改任何文件。

---

### 逐条发现

**PR-01（P2）用例 2 未进入 debounce 分支，判别力不足；Handoff 的反向推演不成立**
- 位置：`apps/desktop/frontend/src/workbench/WorkbenchPage.test.tsx:1111-1127`；`WorkbenchPage.test.tsx:114,62`（helper 默认 0）；`doc/handoffs/M2-REGION-DEBOUNCE-1-zcode-2891c886.md:18,38`
- 事实：用例 2 名为 "…immediate **under the debounce**"，但 `mountInteractiveWorkbench(invoke)` 未传 `regionDebounceMs`，helper 落回 `?? 0`，因此 `WorkbenchPage.tsx:422-430` 的 debounce 分支**一次都没执行**。它实际只钉住「0ms 原路径 + 写后刷新直调」。
- 反向推演（要求 3 的第二个问题）：把 timer 外壳**挪进** `refreshRegions` 函数内、并沿用同一 `regionDebounceMs > 0` 门闸与 `signal.cancelled` 守卫时——
  - 用例 2（0ms）：门闸为假 → 仍即时 → **绿**；
  - 用例 1（300ms）：effect 每键立即调 `refreshRegions`，各挂一个内部 timer；`advanceTimersByTime(300)` 后前 3 个被 cleanup 置为 `cancelled` 而丢弃，第 4 个以 `page-1` 触发 → advance 前 0 次、advance 后恰好 1 次 → **也绿**；
  - 而生产默认 300ms 下 `doSetRegionType`/`undoRetype`/`restoreHistoryRevision` 的 `await refreshRegions(...)` 会被整体延后 → 裁定 1 被破坏却**零红**。
  （若该错位变体丢了 `cancelled` 守卫，用例 1 才会因 advance 后 4 次而红——即用例 1 只有部分判别力，用例 2 完全没有。）
- 建议处置：新增/升级一个 300ms 判别用例——`vi.useFakeTimers()` 下以 `{ regionDebounceMs: 300 }` mount，`advanceTimersByTime(300)` 载入 `region-1`，然后点击 `inspector-mark-sfx`，**不再推进任何 timer** 即断言 `list_regions` 调用数由 1 增至 ≥2（并可断言新 `region_type` 已渲染）。注意 Task 冻结文 `doc/tasks/M2-REGION-DEBOUNCE-1.md:30` 原文把用例 2 写成「0ms 下……」，所以这是**冻结测试规格本身的判别力缺口**：请 Codex 要么在集成前开一条最小 scope note 补该用例，要么由 Owner 在 r2 修正 `Handoff:18/38` 的反推演措辞并把该缺口登记为残留。二者取一即可，勿两者都不做。

**PR-02（P4）Handoff 裁定 2「空输入清屏有 ≤300ms 延迟」与实际实现不符**
- 位置：`doc/handoffs/M2-REGION-DEBOUNCE-1-zcode-2891c886.md:31`；实现 `WorkbenchPage.tsx:530-566`（`setRegions([])`/`setPageSize(null)`/`setRegionError(null)` 在 546-548）
- 事实：`pageId` 的唯一 setter 是 `onPageIdChange:565`，它在每次 pageId 变化时**同步**清空 `regions/pageSize/regionError`（React 同一次 commit 生效），所以产品可见的清屏是**立即**的；timer 回调里 `refreshRegions("")` 的清空分支只是冗余（无害）。即该「≤300ms 取舍」在产品上并不存在，写进集成记录会误导后续 Review/产品判断。
- 建议处置：r2 修正 Handoff 措辞为「空输入清屏由 `onPageIdChange` 立即完成，deferred 空读为冗余无害」，或在 Review 报告中留存本结论。

**PR-03（P4，可选顺笔登记）仍有逐键残留面：手工 resource 地址输入**
- 位置：`WorkbenchPage.tsx:942-944`（`resource-id-input`）、`960-963`（`resource-revision-input`）→ `setResourceId/setResourceRevision` → image effect `439-489`（deps `[clients, replaceImageUrl, resourceId, resourceRevision]`，489）
- 事实：逐字符输入 resource id/revision 会每键触发一次资源通道读取（`loadPageImageUrl`）。Task `:31` 明确 image 不在本刀范围，且这是 debug 回退输入，因此**不构成本刀 AC 缺口**；建议登记为与 RESOLVE-DEBOUNCE C-1 同类的后续残留。
- 其余「逐键残留面」核对结论：**无**。chapters `[clients, selectedBookId]`（282）、pages `[clients, selectedChapterId]`（321）、books `[clients]`（240）均为离散点击驱动；`SettingsPanel.tsx:164` 的 onChange 是 `<select>` 且只改本地 draft。

**PR-04（P4，证据完整性，可选）缺 change-surface binding 日志**
- 位置：`verification/M2-REGION-DEBOUNCE-1/raw/` 仅 4 个日志（本 Task）；前 Task 有 `verification/M2-RESOLVE-DEBOUNCE-1/raw/change-surface-binding-1.log`（DSH r1 C-2 绑定件）
- 事实：AC2「零 Python/Rust/契约改动」目前只由套件等量 + commit message 支撑，无变更文件清单。我侧已用「全树无 `.py/.rs` 引用 `regionDebounce|debounce`」+ 套件等量 + 单 commit 范围信息做代理验证，但因 shell 不可用，**无法机械枚举 `2891c886` 的文件清单**。
- 建议处置：补 `raw/change-surface-binding-1.log`，内容为 `git diff --name-status 9d5d9aa6..2891c886`（预期仅 2 个 frontend 文件）。

**PR-05（P4，可选一致性）region 读缺 quiet-window busy 提示**
- 位置：`WorkbenchPage.tsx:415-435`；对照 resolve 的 `resource-resolve-busy`（`976-980`）
- 事实：300ms quiet 窗口 + 读取期间区域面板为空且无任何提示（resolve 侧在前 Task PR-02 已补 busy）。非冻结范围，是否补齐由产品裁定。

---

### 核对过、未发现问题的关键点

1. **commit/reflog 绑定**：分支自 `9d5d9aa6`（= main tip）创建；`2891c886` = 交付 commit（message: `fix(workbench): region read keypress debounce …`）；`3a43321c` = docs（task+handoff+verification）。Task frontmatter `base_commit: 9d5d9aa6` / `delivery_commit: 2891c886` 一致；`status: in_review`、`reviewer: DSH（非作者）` 正确。
2. **AC1 证据**：`verification/M2-REGION-DEBOUNCE-1/raw/vitest-run-1.log` HEAD=`2891c886a701…`，`140 passed`，`WorkbenchPage.test.tsx (35 tests)`；`frontend-build-1.log` `tsc && vite build` → `EXIT=0`。
3. **AC2 证据**：`full-pytest-1.log:399` `1886 passed, 1 skipped`、`:3` HEAD=`2891c886`、`EXIT=0`；`cargo-test-1.log:17,79` `running 56 tests` / `55 passed; 0 failed; 1 ignored`、`EXIT=0`。四项日志均自述同一 HEAD。
4. **基线等量可复算**：`verification/M2-RESOLVE-DEBOUNCE-1/raw/vitest-run-1.log` = `138 passed`、WorkbenchPage `33 tests` → `+2 = 140/35` ✓ 与 Handoff 一致。
5. **既有 33 用例零改动（结构性证明）**：新旧文件 33 个 `it(` 标题文本与顺序完全一致，且首 32 个标题间行距逐项相同（delta 恒定 +4 行），证明**所有既有用例体无任何插入/删除**；总差 `1099→1155 = +56`，正好 = 头部 +4（原 1 行 render 拆成 `111-115` 5 行、注释 `108-109` 原地改写）+ 插入 `1077-1128` 共 52 行（两个新用例）。
6. **WorkbenchPage.tsx 变更面 = 冻结范围（行级对账）**：`986→1005 = +19`，正好 = prop 块 `+5`（`44-58` 注释+声明，`85` 解构默认值同行）+ region effect `+14`（`415-435` vs base `410-416`）。`refreshRegions` 函数体（`379-413`）与 base 逐字一致；其余函数/JSX 无改动。
7. **debounce 外壳正确性**：`signal` 对象按 effect 实例创建；timer 闭包捕获当次 `pageId`（即最后一键）；0ms 分支 `431 + 432-434` 与 base `412-415` 等价。`clients` 由 `useMemo([invoke])`（`194-215`）稳定，`refreshRegions` 由 `useCallback([clients])`（`412`）稳定，不会因渲染抖动重置 timer。
8. **cleanup 双层取消成立**：cleanup 同时 `signal.cancelled = true` + `clearTimeout`（`426-429`）；timer 回调再查 `!signal.cancelled`（`424`，防御性冗余）；timer 已 fire 后的迟到回包由 `refreshRegions` 内既有 `requestId === regionReadRef.current` + `signal.cancelled` 守卫丢弃（`381-385`）。
9. **effect 依赖数组完整**：`[clients, pageId, refreshRegions, regionDebounceMs]`（`435`），无遗漏、无多余。
10. **写后刷新路径零波及（要求 2 的关键项）**：`refreshRegions` 仅 3 个直调点 `655`（`doSetRegionType`）、`690`（`undoRetype`）、`738`（`restoreHistoryRevision`），全部传新对象 `{ cancelled: false }` 且 `await`，与 effect 的 timer 无任何耦合；函数体零改动。900 行处的 `undoAvailable` 等派生 UI 亦不受影响。
11. **判别力正向核对（要求 3 第一个问题）**：删掉外层 `setTimeout` 后，用例 1 的 `expect(regionCalls).toHaveLength(0)`（`1093-1094`）必红（4 次逐键调用），且 advance 后「恰好 1 次 + 参数为最后一键」（`1100-1102`）也会红——该用例判别力成立，与 Handoff 声明一致。
12. **与 RESOLVE-DEBOUNCE prop 模式对称**：命名 `*DebounceMs?: number`、产品默认 300、注释指向来源 PR/裁定、测试注入 0，两 prop 可独立注入互不干扰；`0ms` 路径与 base 逐字等价（要求 4）。
13. **产品接线**：`App.tsx:517` 为 `<WorkbenchPage />`，故生产默认 300 生效；`src` 内无其他非测试挂载点；同一测试文件内 `renderToString` 挂载（`275-309`）不跑 effect，不受默认值影响。
14. **零 Python/Rust/契约改动的代理验证**：全树 `.py`/`.rs` 无 `regionDebounce|debounce` 引用；无契约/Schema 文件被新 prop 触碰（组件内部 prop）；AC2 套件等量（见 PR-04 的证据补强建议）。
15. **空输入行为**：`refreshRegions("")` 不发 `list_regions`，且清屏由 `onPageIdChange:546-548` 立即完成（见 PR-02，结论是「无产品可见延迟」，非缺陷）。

---

### 推荐下一步

由 Codex（Integrator）处置单一条件项后集成：**首选**在 `WorkbenchPage.test.tsx` 增补 PR-01 所述 300ms 写后刷新判别用例（约 +20 行，纯测试、不扩产品范围），并在 `raw/` 落盘 `change-surface-binding-1.log`（PR-04）；**若非作者 Owner 认为冻结规格不可动**，则退化为修正 `Handoff:18/38` 的反推演声明、登记 PR-01 缺口为 r2 残留，并由 Codex 记录该取舍。完成任一路径后请 DSH 出 r1 结论回填 `doc/reviews/`，再执行 merge + `STATUS`/`REBASELINE_PLAN` 收口。
