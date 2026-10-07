# M2-REGION-DEBOUNCE-1 Handoff（Owner→Reviewer/Integrator）

- Owner: Codex Executor（ZCode 代行，持续自治授权）
- Reviewer: DeepSeek Harness（非作者）
- Integrator: Codex
- Task: [M2-REGION-DEBOUNCE-1](../tasks/M2-REGION-DEBOUNCE-1.md)（release 见 Task frontmatter，base `9d5d9aa6`）
- Branch/worktree: `zcode/region-debounce-1` @ `G:/CODEX/New Manga.worktrees/REGION-DEBOUNCE-1`
- Delivery head: `2891c886`（单交付 commit）

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
| AC3 非作者 Review | PENDING | DSH r1（本文档即派发依据） |

## 设计裁定（Reviewer 请特别核验）

1. **debounce 只包 effect 驱动读取**：`refreshRegions` 函数本体零改动——写后刷新（`doSetRegionType`/`undoRetype`/`restoreHistoryRevision` 内 `await refreshRegions(...)`）必须即时（写后看到新状态是正确性语义）；用例 2 钉该边界。
2. **空页清屏不在 timer 内**：`refreshRegions` 对空 trimmed 的清空分支在函数内部——debounce 下空输入（用户删光 page id）的清屏延迟至 timer 触发？否：`pageId` 变化即重跑 effect，空输入时 `refreshRegions(pageId, signal)` 在 timer 回调内首行 `trimmed` 空→`isCurrent()` 清空。空输入清屏有 ≤300ms 延迟（与 resolve 同款取舍，Task 冻结已声明「解析延后」语义）。
3. **signal.cancelled 与 timer 双保险**：cleanup 先置 cancelled 再 clearTimeout；timer 已 fire 后的迟到回包由 `refreshRegions` 内部 `requestId`+`signal.cancelled` 守卫丢弃（既有机制）。
4. **与 resolve debounce 的对称性**：同款 prop 模式/默认值/测试注入约定——两 prop 可独立注入（测试只测 region 时 resolveDebounceMs 默认 0 不干扰）。

## Reviewer 关注点提示

- 实现集中在 region 读 effect（约 +14 行）；测试 +2 用例（fake timers 纪律同前）。
- 反向推演：删 setTimeout 外壳→用例 1 的 advance 前零调用断言红；把 timer 包裹错放到 `refreshRegions` 函数内→写后刷新被延迟→用例 2 红（retype 后刷新不即时）。
