# M2-SFX-MISROUTE-UI-IMPL-1 r2 定点复审报告（DSH 非作者）

## 1. 方法段

- **锚点与只读约束**：worktree `G:/CODEX/New Manga.worktrees/M2-SFX-MISROUTE-UI-IMPL-1-zcode`，r1 审查锚 `e70356e5`，r1fix tip=`3474affa`。全程只读，未修改任何文件。
- **工具限制（已如实登记，非 Owner 责任）**：本会话 `pwsh` 无法启动——沙箱每次执行都在会话工作目录上 `SetNamedSecurityInfoW failed (Win32 5) grantWrite`；一次沙箱升级请求因无审批通道被拒。因此**无法机械执行 git/diff**。
- **替代取证手段（均为一手仓内证据）**：
  1. Git 元文件纯文本读取：`.git/worktrees/M2-SFX-MISROUTE-UI-IMPL-1-zcode/logs/HEAD`（reflog）第 9–10 行确认 `e70356e5 → 5dd325b8(fix) → 3474affa(docs)`，与自报两 commit 面吻合；`.git`/`HEAD` 确认分支 `refs/heads/agent/zcode/M2-SFX-MISROUTE-UI-IMPL-1`。
  2. 仓内 raw 物证：`raw/vitest-verify.log`（r1 锚 102 逐文件）、`raw/vitest-r1fix.log`（tip 105 逐文件）、`raw/npm-build-r1fix.log`、`raw/vitest-machine-red/green.log`、`raw/pytest-full.log`、`raw/r1fix-diff-name-status.txt`、`raw/vitest-impl.log`（基线态工具栏 HTML）。
  3. 源码/测试全文阅读 + 全仓 grep（`isError`/`retypeError`/`setRegionType`/`toolbar-retype-reserved`/`restore`）。
  4. `glob` 的 mtime 序尾簇（`apps/desktop/frontend/src/**/*` 完整 36 文件）：尾簇=WorkbenchToolbar/relabelMachine/RegionInspector/WorkbenchPage/ViewerPanel/relabelMachine.test/WorkbenchPage.test 共 7 个，与 r1fix 自报面一致；`region/geometry.ts`、`region/client.ts`、`types.ts` 不在尾簇 → 读取面未被 r1fix 再动（旁证，非 git 级证明）。
- **未采信项**：`Task §r1 返修段`与自报文字均逐条落到文件核验，其中 3 项与落盘不符（见第 4 节 N-1/N-2/N-3）。

## 2. 终判

**approved_with_conditions**（代码面无 P0/P1/P2 缺陷、r1 的 P1-1 与 P2-1/2/3 真实闭合、无回归；但 P2-4/P2-5 的**覆盖/物证声明仍与落盘不符**，须按第 5 节条件修正文档与 raw 后方可集成）。

## 3. 逐条闭合表（r1 项号 → 判定 → 证据）

| r1 项 | 判定 | path:line 证据 |
|---|---|---|
| **P1-1** 错误呈现不可达 | **闭合（代码+测试）** | ①正向失败可达且走 error 变体：`WorkbenchPage.tsx:238`（结构闸门）→`:299-312`（execute 分流 `:311`）→`catch :269-292`，`:290-291 setFeedback({…,isError:true})`；error 变体渲染 `ViewerPanel.tsx:210`（`--wb-fail` 边框）`:214-216`（error 字色）`:228`（无 ✅）`:231`（`!isError` 才出动作按钮）。②确认框失败不再关框：`WorkbenchPage.tsx:282-287`（`fromConfirm` → `setRetypeError` 后 `return`，未 `setConfirmTarget(null)`），框内消费 `:430 errorText={retypeError}` → `RelabelConfirmDialog.tsx:80-87`（`relabel-confirm-error`）。③变体 SSR 断言 ×2：`WorkbenchPage.test.tsx:75-98`（error：有文案、无 undo/rerender）、`:100-124`（success：双禁用按钮）。`retypeError` 全仓唯一消费点即确认框（grep：`:65/242/285/306/430/438`），无孤儿态。 |
| **P2-1** 工具栏陈旧占位 | **闭合** | `WorkbenchToolbar.tsx:1-37`（全文无 button，`:3-6` 注释明示占位已退役）；断言恢复 `WorkbenchPage.test.tsx:61-63`（inspector+toolbar 双 `not.toContain`）。基线态确含该占位：`raw/vitest-impl.log:26`。 |
| **P2-2** 「可随时撤销」承诺矛盾 | **闭合** | `RegionInspector.tsx:108` 改为条件句「撤销/历史入口待 Core restore 命令面 Task 落地后启用（当前 UI 通道未开通）」；`历史（预留）` 按钮禁用+原因 `:181-198`；`ViewerPanel.tsx:233-266` 撤销/重渲染禁用+title。设计原文（`design.md:136`）未回改 ✓。 |
| **P2-3** 成品图语义缺失 | **闭合** | `relabelMachine.ts:139 ARTEFACT_NOTE="原图完好；已渲染成品图需重跑渲染才恢复原文"` 落全部 4 文案分支 `:142/150/156/163`；断言 `relabelMachine.test.ts:157-163`（3 policy×2 关键词 + speech 1 条）。设计锚：`design.md:46,253`。（自报「5 分支」实为 4 文案分支/7 处 contains 断言，口径微差、不实质。） |
| **P2-4** AC3/AC4 覆盖声明不实 | **未完全闭合（P2 残）** | 已做：A3 表述修正在 `Task:86`；+3 测试（差量精确）。未闭合：`Task:37` AC4 定义仍写「失败路径先红后绿」；`Task:54` 仍把 A3 列在「§7 断言 UI 可测面落 vitest」清单内；`Task:55` 判定回到 **PASS**。事实：`WorkbenchPage` 的失败接线（catch→isError）**零测试**（grep `setRegionType`：仅 `region/client.test.ts:124-186` 客户端层与 `WorkbenchPage.test.tsx:87` 手喂文案），失败路径只由静态阅读可读。详见 N-1。 |
| **P2-5** diff 面 raw | **未真实闭合（P2 残）** | `raw/r1fix-diff-name-status.txt` 落盘为真，但**不含** `M apps/desktop/frontend/src/workbench/WorkbenchToolbar.tsx`——该文件 r1fix 确已改（基线含占位 `raw/vitest-impl.log:26`；现文件 `WorkbenchToolbar.tsx` 已无），亦不含 `raw/vitest-r1fix.log`、`raw/npm-build-r1fix.log`。故 `Task:87`「ecbfe9cb..tip 全 diff 面」不成立（该面实为 r1 锚 e70356e5 面）。详见 N-2。 |
| **P3-1** A13(b) 未取证/登记 | **部分闭合** | 登记文案在 `Task:88`（含静态估算 ≈11.6:1；我按 WCAG 公式复算 `#fbbf24` vs `#0b0e12` = **11.59:1**，与自报一致）；衬底 token 化 `ViewerPanel.tsx:141 var(--bg-canvas,#0b0e12)` ✓。但**偏差 8 条目本身（`Task:67`）无 A13(b) 文字**，自报「并入偏差 8 扩充」不符 → N-3。 |
| **P3-2** OTHER_TYPE 未列偏差 | **部分闭合** | `Task:89` 有登记文字，但偏差清单仍是 **9 条**（`Task:60-68`），无「第 10 条」；设计尾注仍写「偏差 9 条」（`design.md:343`）→ N-3。 |
| **P3-3** 红绿 16/20 | **闭合（表述精确化）** | `Task:55` 已写「16/20 红先行，retypeFeedback 组 4 例随实现同轮补」。物证：`raw/vitest-machine-green.log:6,9`（16/16 pass）；`raw/vitest-machine-red.log:11,16-17,21` 首轮红为**模块解析失败**（`Failed to load url ./relabelMachine`，0 test）→ 属新模块先写测试的典型红态，非断言级红（口径可接受，见 N-0 备注）。 |
| **P3-4** 确认闸门在调用点 | **闭合（结构闸门）** | 字面在 `WorkbenchPage.tsx:238`：`if (plan.kind === "blocked" \|\| (plan.kind === "confirm" && !opts?.confirmed)) return;`；唯一确认传入 `:432 doSetRegionType(confirmTarget,"speech",{confirmed:true,fromConfirm:true})`；doSetRegionType 仅两个调用点（`:311` execute、`:432` 对话框）→ A5 唯一路径成立。 |
| **P3-5** 菜单无法关闭 | **闭合** | `ViewerPanel.tsx:124 tabIndex={-1}` + `:125-131 onKeyDown Escape→closeMenu` + `:132-137 onContextMenu（preventDefault+closeMenu）`。残余限制见 N-7（零 DOM 无法测焦）。 |
| **P3-6** offerUndo/Rerender 未消费 | **闭合（登记）** | `Task:93`；代码侧 `ViewerPanel.tsx:231-266` 只在 success 变体渲染且禁用+title（`relabelMachine.ts:199-202`）。 |
| **P4-1..6** | **P4-2/3/4/5/6 闭合；P4-1 漏登** | `Task:94`（P4-2 2.5px/2.25px、P4-3 signal、P4-5 feedback 跨页、P4-6 草稿退化）+`Task:95`（P4-4 精确化：`src/application/editing/service.py:694-716 restore_revision` 我逐行核对存在 ✓；`apps/desktop/src-tauri/src/**` grep `restore` 仅 ac1 注释、无 IPC 命令 → 「缺命令面」成立）。**P4-1 未登记**：`WorkbenchPage.tsx:186-193`（imageError 改判 TypedChannelError）代码注释自称「r1 P4-1」，故该项处置为代码修复而非登记，Task 清单未列 → N-4。 |

**approved 面无回归抽验**：A1 命令面未扩（`commandSurface.test.ts:24,39`，9 命令 pin，105 全绿）；A5 见 P3-4；A8 三重编码（`RegionOverlay.tsx:187-210`，`WorkbenchPage.test.tsx:179-180`）；A9 快照查找表（`relabelMachine.ts:101-113,130-168`，`relabelMachine.test.ts:127-145`）；A12 禁用+原因（`RegionInspector.tsx:77-91,153-160`、`RelabelContextMenu.tsx:109-116`、`relabelMachine.test.ts:71-99`）；WORKBENCH 读取面硬规则（`RegionOverlay.tsx:89-108` 仍唯一走 `geometry.ts` 三函数；`geometry.ts/client.ts/types.ts` 不在 mtime 尾簇）；`isError` 传播链 11 处全链自洽、无死消费点；`ARTEFACT_NOTE` 为函数内局部常量、作用域无泄漏；`tsc && vite build` 通过（编译级排除 JSX/引号/转义类回归）。

**数字自洽（逐文件复算）**：`vitest-r1fix.log:6-16` 8+4+8+3+21+10+11+7+15+8+10=**105** ✓；`vitest-verify.log:9,15` 基线 relabelMachine 20 / WorkbenchPage.test 13 → 差量恰为 **+3**（21、15），与自报「102+3=feedback 两变体+artefact 文案」逐一对应；`npm-build-r1fix.log:10-11` `built in 431ms`/`BUILD_EXIT=0` ✓；`pytest-full.log:399-400` `1 failed, 1847 passed, 1 skipped`/`PYTEST_EXIT=1`（既有 BASELINE_FAILURE，r1fix 零 Python 触碰故免重跑，理由成立）。

## 4. 新发现

- **N-1（P2，承 P2-4 残）** 覆盖声明仍不实：`Task:37`（AC4 定义含「失败路径」）、`Task:54`（A3 在「落 vitest」清单）、`Task:55`（AC4 回到 PASS）。r1fix 新增的 2 例只渲染 ViewerPanel 的被喂 `isError` 状态（`WorkbenchPage.test.tsx:85-98`），不触发任何失败；`WorkbenchPage.tsx:269-292` 的 catch 接线零测试。零 DOM 环境（`package.json:17-24` 无 jsdom/happy-dom/@testing-library）使交互测试不可行——**理由成立、结论表述不成立**：应把 AC4 判为 PARTIAL（或加限定语「失败路径=静态可读+变体渲染 SSR，接线无 DOM 测试」）并同步 AC4 定义行口径注。
- **N-2（P2，承 P2-5 残）** 物证面与自报不符：`raw/r1fix-diff-name-status.txt` 缺 `M WorkbenchToolbar.tsx` 与 r1fix 另两个 raw（自身亦不在列）；`Task:87`「ecbfe9cb..tip 全 diff 面」为假。后果：r1fix 的「零 Python/零 src/**/src-tauri/qml 触碰」缺少 diff 级物证（我只能以 mtime 尾簇+命令面 pin 旁证）。
- **N-3（P3）** `Task:88/89` 自报「A13(b) 并入偏差 8」「补偏差第 10 条」未落到**偏差清单**：`Task:60-68` 仍 9 条、`Task:67` 无 A13(b)、`design.md:343` 仍写「偏差 9 条」。后续按清单读会漏登。
- **N-4（P3）** r1 P4-1 处置（`WorkbenchPage.tsx:186-193`，resource 错误码改判 `TypedChannelError`）为**代码修复**，但 `Task:94` 的 P4 登记清单只列 P4-2/3/5/6+单列 P4-4，P4-1 缺席 → r1 返修段与实做不一致。
- **N-5（P4）** `Task:76`「证据与 commit」清单未纳入 r1fix 三个新 raw；`doc/handoffs/…-20261006.md:14,28-31` 未随 r1fix 更新（仍写 vitest 77→102、AC3「A2/A3/…落 vitest」、commit 链 5 条），集成读者会读到过期数字与过期覆盖声明。
- **N-6（P4）** 命令面表述混述：`RegionInspector.tsx:108` 把「撤销」与「历史」并称「Core restore 命令面」，而历史实为 `ListRegionRevisions`（同文件 `:185` title 正确）；`relabelMachine.ts:200 UNDO_DISABLED_TITLE`（用户可见）仍称「Core restore 命令待后续命令面 Task」，按 P4-4 精确口径宜写「应用层已有 restore_revision，缺 IPC 命令面」。
- **N-7（P4）** Escape 关菜单依赖 stage 获焦（`ViewerPanel.tsx:124-131`），零 DOM 环境无断言；建议登记为后续 DOM 环境（jsdom/happy-dom 引入时）的补测项，而非本 Task 阻塞。
- **N-8（P4/流程）** `doc/reviews/` 不存在 IMPL-1 的 r1 报告（`**/*M2-SFX-MISROUTE*` 仅命中 MITIGATION 的 r1/r2 与两个 Task/Handoff），r1 结论只以 `Task:14 review_events`+返修段形式存在；与 MITIGATION 先例（`doc/reviews/M2-SFX-MISROUTE-UI-MITIGATION-*-dsh-r{1,2}.md`）不一致。
- **N-0（备注，不计缺陷）** P3-3 的「16/20 红先行」物证是**集合失败态红**（模块未创建），非断言级红；对「先写测试后补实现」的新模块属可接受口径，Task 已精确化，不另计。

## 5. 集成建议

1. **可集成性**：代码面无需返工——r1 的 P1-1 与 P2-1/2/3 真实闭合，P3-4/5 结构闸门与菜单关闭落地，A1/A5/A8/A9/A12 无回归，105 全绿+tsc/build 绿+pytest 等量，数字自洽，r1fix 未越界（mtime 尾簇+命令面 pin 旁证）。**建议按 `approved_with_conditions` 放行**。
2. **集成前应闭合的两个条件（纯文档/物证，零代码改动）**：
   - 条件 1（N-2）：重新生成覆盖 `3474affa` 的 diff 面 raw（或把 `raw/r1fix-diff-name-status.txt` 明确标注为「r1 锚 e70356e5 面」），并把 `Task:87` 的「..tip」表述改为实际范围；同时把 r1fix 三个 raw 写入 `Task:76` 证据清单。
   - 条件 2（N-1）：修正 AC4/AC3 覆盖表述——`Task:55` 改为 PARTIAL（或加限定语），`Task:54` 的 A3 移出「落 vitest」表述并在 AC4 定义行（`Task:37`）加实现口径注。
3. **登记补齐（同批即可）**：N-3（偏差清单补第 10 条 + 偏差 8 内写 A13(b)，并同步 `design.md:343` 的「偏差 9 条」注记）、N-4（补 P4-1 处置）、N-6（用户可见 title 口径）。
4. **推荐下一步（可直接转发）**：

> ZCode：对 `M2-SFX-MISROUTE-UI-IMPL-1` 执行 r2 条件返修（仅文档/物证，禁动前端行为）：①重生成 `verification/M2-SFX-MISROUTE-UI-IMPL-1/raw/r1fix-diff-name-status.txt` 使覆盖 `ecbfe9cb..3474affa`（须含 `M apps/desktop/frontend/src/workbench/WorkbenchToolbar.tsx`）并补列 r1fix 两 log；②`doc/tasks/M2-SFX-MISROUTE-UI-IMPL-1.md`：AC4 判定改 PARTIAL+AC4 定义行加口径注、AC3 行 A3 去「落 vitest」表述、偏差清单补第 10 条并把 A13(b) 写入偏差 8、补 P4-1 登记、证据清单补 3 raw；③`doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md:343` 尾注「偏差 9 条」同步为 10 条（仅尾注，原文不回改）；④复跑 vitest+build 留新 raw 后交 Codex 集成。

> 无需额外释放 Task：N-7（Escape 焦点断言）与 N-8（r1/r2 报告落 `doc/reviews/`）建议分别并入侵入 DOM 测试环境的后续前端 Task 与本次集成收口动作。
