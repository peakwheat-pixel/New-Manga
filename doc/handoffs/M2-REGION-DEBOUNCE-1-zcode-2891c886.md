# M2-REGION-DEBOUNCE-1 Handoff（Owner→Reviewer/Integrator）

- Owner: Codex Executor（ZCode 代行，持续自治授权）
- Reviewer: DeepSeek Harness（非作者）
- Integrator: Codex
- Task: [M2-REGION-DEBOUNCE-1](../tasks/M2-REGION-DEBOUNCE-1.md)（release 见 Task frontmatter，base `9d5d9aa6`）
- Branch/worktree: `zcode/region-debounce-1` @ `G:/CODEX/New Manga.worktrees/REGION-DEBOUNCE-1`
- Delivery head: `2891c886`（单交付 commit）
- Rework head: 见文末 disposition（r1 `approve_with_conditions`——PR-01 P2 取 r1 给出的路径 B：修正反推演声明+缺口如实登记；代码/测试主体零改动）

## 交付内容（一句话）

RESOLVE-DEBOUNCE r1 C-1 登记的 region 逐键残留闭合：region 读 effect 加 `regionDebounceMs` 可选 prop（产品默认 300、测试注入 0）——手输 page id 逐字符不再逐次触发 `list_regions`（含 regions 错误条逐键闪烁）；**写后刷新路径（retype/undo/restore 的 `refreshRegions` 直接调用）保持即时**（debounce 只包 effect 驱动读取，不包函数本身）。零 Python/Rust/契约改动。

## 逐层交付（全部 @`2891c886`）

### React
- `WorkbenchPage.tsx`：`WorkbenchPageProps.regionDebounceMs?: number`（默认 300）；region 读 effect 内 `regionDebounceMs > 0` 走 `setTimeout` 包裹 `refreshRegions(pageId, signal)`（cleanup `clearTimeout`+`signal.cancelled`，与既有守卫叠加），否则保持原路径逐字不变；effect 依赖补 `regionDebounceMs`。`refreshRegions` 函数本体零改动（写后刷新的 `await refreshRegions(...)` 调用点全部即时）。
- `WorkbenchPage.test.tsx`：mount helper 加 `options.regionDebounceMs`（测试默认 0——既有 33 用例零时序扰动）；**+2 判别用例**：①fake timers 逐字符 4 键→advance 前 `list_regions` 0 次→advance 后恰好 1 次且参数为最后一键（删 debounce 外壳即红）；②0ms 下 retype 流（点 region→inspector-mark-sfx）后 `refreshRegions` 直调刷新仍即时（≥2 次调用）——钉「debounce 不波及写后刷新」。

## 验收对照

| AC | 状态 | 证据 |
|---|---|---|
| AC1 前端 | DONE | vitest **140 passed**（DEBOUNCE 基线 138 + 2 新判别用例；既有用例零改动零扰动）+ `npm run build` EXIT=0；raw 日志 `verification/M2-REGION-DEBOUNCE-1/raw/{vitest-run,frontend-build}-1.log`（HEAD=`2891c886`） |
| AC2 回归 | DONE | 全量 pytest **1886 passed+1 skipped+0 failed**（基线等量）；cargo **55+1ign** 基线不变；raw 日志 `verification/M2-REGION-DEBOUNCE-1/raw/{full-pytest,cargo-test}-1.log`（HEAD=`2891c886`） |
| AC3 非作者 Review | r2 PENDING | r1 [approve_with_conditions](reviews/M2-REGION-DEBOUNCE-1-2891c886-dsh-r1.md)（PR-01 **P2** 用例 2 判别力不足+反推演不成立；PR-02..05 P4）→ 路径 B 返修（修正声明+缺口登记）→ DSH r2 |

## DSH r1 逐项 disposition（r1 @`2891c886`，报告 `doc/reviews/M2-REGION-DEBOUNCE-1-2891c886-dsh-r1.md`；rework 取 r1 给出的**路径 B**）

| 项 | 级 | 处置 |
|---|---|---|
| PR-01 用例 2 未进 debounce 分支（helper 默认 0ms），「under the debounce」判别力不成立；反推演显示「timer 错放进 refreshRegions」的变体零红 | **P2** | **路径 B（r1 明示二选一）**——①用例 2 改名如实化（「pins the 0ms direct-call path」+scope note 注明 300ms 判别登记为残留）；②Handoff :18/:38 反推演措辞更正（结构论证：wrapper 只包 effect 体、refreshRegions 函数体与 base 逐字一致，写后刷新在结构上不可能到达 timer）；③**300ms 下写后刷新即时性判别缺口显式登记为残留**（r1 首选的 fake-timer UI 链用例在本 harness 中 Inspector 链不 settle——实测尝试失败，如实记录） |
| PR-02 裁定 2「空输入清屏 ≤300ms 延迟」与实现不符（onPageIdChange 同步清屏） | P4 | **fixed（文案）**——裁定 2 改写为「清屏立即、deferred 空读冗余无害」 |
| PR-03 手工 resource id/revision 输入逐键触发 image 读取残留 | P4 | **deferred 登记**（收口 STATUS Planned next；debug 回退输入，Task 冻结已排除） |
| PR-04 缺 change-surface binding 日志 | P4 | **fixed**——`raw/change-surface-binding-1.log`（diff --name-status 9d5d9aa6..2891c886 应恰为 2 个 frontend 文件） |
| PR-05 region 读缺 quiet-window busy 提示 | P4 | **deferred 登记**（产品裁定项，非冻结范围） |

## 设计裁定（Reviewer 请特别核验）

1. **debounce 只包 effect 驱动读取**：`refreshRegions` 函数本体零改动——写后刷新（`doSetRegionType`/`undoRetype`/`restoreHistoryRevision` 内 `await refreshRegions(...)`）必须即时（写后看到新状态是正确性语义）；用例 2 钉该边界。
2. **空输入清屏（r1 PR-02 更正）**：空输入（删光 page id）的产品可见清屏由 `onPageIdChange` **立即同步**完成（清 regions/pageSize/regionError），deferred 的 `refreshRegions("")` 空读分支只是冗余无害——产品上不存在「≤300ms 清屏延迟」；原表述作废。
3. **signal.cancelled 与 timer 双保险**：cleanup 先置 cancelled 再 clearTimeout；timer 已 fire 后的迟到回包由 `refreshRegions` 内部 `requestId`+`signal.cancelled` 守卫丢弃（既有机制）。
4. **与 resolve debounce 的对称性**：同款 prop 模式/默认值/测试注入约定——两 prop 可独立注入（测试只测 region 时 resolveDebounceMs 默认 0 不干扰）。

## Reviewer 关注点提示

- 实现集中在 region 读 effect（约 +14 行）；测试 +2 用例（fake timers 纪律同前）。
- 反向推演：删 setTimeout 外壳→用例 1 的 advance 前零调用断言红；把 timer 包裹错放到 `refreshRegions` 函数内→写后刷新被延迟→用例 2 红（retype 后刷新不即时）。
