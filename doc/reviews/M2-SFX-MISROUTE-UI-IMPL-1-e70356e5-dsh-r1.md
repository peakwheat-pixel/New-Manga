# M2-SFX-MISROUTE-UI-IMPL-1 非作者独立复核报告（r1，静态只读）

## 1. 方法段

**审查方式**：全程只读静态审查，未修改任何文件。本会话 `pwsh` 因沙箱初始化失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`）无法执行任何 shell 命令，因此**无 git / npm / pytest 执行能力**：所有「等量递增」「零 diff」「EXIT=0」结论只做**静态核对**（读 log 原文 + 读 git 元文件），写入方法边界。commit 链与 tip 通过直接读取 git 元文件核对。

**已读文件（逐 path）**：
- 合同/设计/交接：`doc/tasks/M2-SFX-MISROUTE-UI-IMPL-1.md`、`doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md`（全文 343 行）、`doc/handoffs/M2-SFX-MISROUTE-UI-IMPL-1-zcode-20261006.md`
- 前端实现：`apps/desktop/frontend/src/workbench/{relabelMachine.ts,RelabelConfirmDialog.tsx,RelabelContextMenu.tsx,RegionInspector.tsx,ViewerPanel.tsx,WorkbenchPage.tsx,WorkbenchToolbar.tsx}`、`apps/desktop/frontend/src/region/{RegionOverlay.tsx,types.ts,client.ts,geometry.ts}`
- 前端测试：`apps/desktop/frontend/src/workbench/{relabelMachine.test.ts,WorkbenchPage.test.tsx}`、`apps/desktop/frontend/src/region/client.test.ts`
- 证据：`verification/M2-SFX-MISROUTE-UI-IMPL-1/raw/` 全 8 log（`npm-install`、`vitest-machine-red`、`vitest-machine-green`、`vitest-impl`、`vitest-impl2`、`vitest-verify`、`npm-build`、`pytest-full` 全文/尾部）
- Core 事实核对：`src/bootstrap/core_service.py`（643-747）、`src/application/editing/service.py`（305-374、383-431、680-721）
- 禁改面静态核对：`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（grep 命中，均仍为「待派发」，与作者未越界一致）
- git 元文件：worktree `.git`、`.git/worktrees/.../HEAD`、`logs/HEAD`、`.git/refs/heads/agent/zcode/M2-SFX-MISROUTE-UI-IMPL-1`

**commit 链核对（静态、来自 reflog/ref 文件）**：`ecbfe9cb`（reset 起点）→ `4cc776fe` claim → `4e60fa74` impl → `7f70c90f` test → `dcb406c8` verify → `e70356e5` docs；分支 ref 文件内容 = `e70356e5ae1ac95fa1c9c66e0e92f29d1540ec5c`，与 tip `e70356e5` 一致 ✓。

**无法核对项（如实声明）**：①worktree 工作区与 `e70356e5` 的 tree 是否干净；②`ecbfe9cb..e70356e5` 的 `--name-status` diff（因此 A1「零源文件写路径」、禁改面「QML/GATE/STATUS 零 diff」只有**静态内容核对**，无 diff 面证据；见 P2-5）；③pytest 实际重跑（只核读 log 原文与既有基线 log 对照）。

---

## 2. 终判

**changes_requested** —— 存在 1 条 P1（R6「失败即呈现错误块」在交付代码中**完全不可见**，Task/Handoff 的对应声明与实现不符），须返修；另有 5 条 P2、6 条 P3 建议同批处理。Owner 的 AC1=PARTIAL / AC2=PASS / AC5=PASS 判定本人认同，AC4 本人下调为 PARTIAL。

---

## 3. A1–A13 逐条判定表

| # | 判定 | 证据与理由 |
|---|---|---|
| A1 | **PASS**（静态限定） | 改标写面唯一为 `RegionClient.setRegionType` → `set_region_type`（`region/client.ts:102-132`），最终写 Core 管的 SQLite revision（`editing/service.py:355-361`）；前端无 `fs`/写文件 API（全 `frontend/src` grep 仅命中既有 probe/ac1/settings/region invoke）；`relabelMachine.ts`、`RegionOverlay.tsx`、新组件零 I/O。**无 diff 面证据，故为静态判定**。 |
| A2 | **PASS** | `suspectWarningVisible(region, suspects)` 仅依赖 `region_type` + UI 集合（`relabelMachine.ts:61-66`）；`planRetypeAction(region, to)` 签名不含 OCR/候选（`relabelMachine.ts:173-179`）；Core 读面本身无文本字段（`editing/service.py:417-423`）——空 OCR/零候选可警示、可改标，构造性成立。 |
| A3 | **PASS** | `onToggleSuspect` 只做 `setSuspects` 集合增删，零 invoke、零 revision（`WorkbenchPage.tsx:216-226`）；警示消失仅由改标成功后重推导引起（因，非果）。 |
| A4 | **PASS** | sfx+skip/manual 文案为「保留原文，不再翻译」「手动处理模式，不再自动翻译」（`relabelMachine.ts:141-161`）；工作台无任何「已（自动）翻译」态呈现（Inspector 只列 `sfx_policy` 原值 + 快照注记，`RegionInspector.tsx:94-109`），与 `gate.py` SKIP 语义一致。 |
| A5 | **PASS** | `planRetypeAction` 对 sfx→speech 返回 `confirm`（`relabelMachine.ts:173-179`）；唯一入口 `onRetypeRequest` 路由到 `setConfirmTarget`（`WorkbenchPage.tsx:285-300`），写调用只发生于 `doSetRegionType`，其直接调用者仅 `onRetypeRequest`（仅 execute 分支）与确认框 `onConfirm`（`WorkbenchPage.tsx:412-425`）；无右键/Inspector/键盘旁路。注：确认闸门位于调用点而非 `doSetRegionType` 内部（见 P3-4）。 |
| A6 | **PASS** | 全仓无「反向改标模拟撤销」路径；undo 呈禁用态+原因（`ViewerPanel.tsx:219-235`、`relabelMachine.ts:191-194`）；Core 侧改标必产新 revision `origin=USER`（`editing/service.py:313-357`），非原地改字段。 |
| A7 | **PARTIAL（已登记）** | 读面 5+geometry 字段**确无** label 前缀（`editing/service.py:417-423`），`RegionPhase` 永不返回 `SFX_ARB`、`sfxBadgeLabel` 永不发 ⧉（`relabelMachine.ts:26-31,98-101`）——机器笔/检测直产 sfx 在 UI 不可分；但 UI **未**把机器笔误呈为人工（`origin` 原值直显，`RegionInspector.tsx:96-97`），无 A7 反向违例。偏差 1 登记如实。 |
| A8 | **PASS** | E1 与 E2 同帧出现（`RegionOverlay.tsx:109-129,151-164,187-210`，E2 含字形 `♪?`+文本「疑似拟声词」）；E3 含 `♪`+三档文本；E4 含 `✅`+文本；Inspector 疑似行 `♪? 疑似拟声词`（`RegionInspector.tsx:84-92`）。无仅靠颜色承载的状态。 |
| A9 | **PASS** | `sfxBadgeLabel`/`retypeFeedback` 为对 Core 快照值的 switch 查找表（`relabelMachine.ts:101-162`），无 gate 等价决策；E4 文案输入的 policy 取自 `set_region_type` 返回值（`WorkbenchPage.tsx:247`），非前端重算。 |
| A10 | **N/A（合规）** | 本切片无 Reader 组件（`frontend/src` 无 Reader 文件），未新增任何 Reader 写操作；Reader 提示条按合同范围边界不实现。 |
| A11 | **PASS**（静态限定） | `SfxPolicy` 三值闭集未变（`region/types.ts:33`）；settings client/panel/test 未被本 Task 引用或改动；全仓无 relabel 标识符泄漏进 settings/Python/QML。 |
| A12 | **PASS** | `canRetype` 仅 speech↔sfx 启用，其余（含同类型）禁用且带 reason（`relabelMachine.ts:77-91`）；Inspector 与右键菜单都对「双禁用」渲染原因（`RegionInspector.tsx:153-160`、`RelabelContextMenu.tsx:109-116`）；无其它启用入口（工具栏占位为 disabled，非旁路）。 |
| A13 | **PARTIAL（登记不完整）** | (a) E3 新组合首取证据 deferred 已登记（Task 回填 偏差 8）；(b) **未单独取证/登记**：全前端无任何 `*.css`/token 定义，`var(--x, fallback)` 恒解析为 fallback，且画布衬底是硬编码 `#0b0e12`（`ViewerPanel.tsx:127`）而非 `bg-canvas` token。静态估算 E1 fallback `#fbbf24` vs `#0b0e12` ≈ 11.6:1（≥3:1，仅供参考、非权威）。 |

---

## 4. AC1–AC5 判定表

| AC | Owner 判定 | 本人判定 | 依据 |
|---|---|---|---|
| AC1 改标交互全套 | PARTIAL | **PARTIAL（认同，且缺陷更重）** | 正向即时（execute 无确认）、反向确认框（文案含「重新进入对白翻译链，可能产生新的译文」+固定安全文案）、守卫②、`expected_revision=region.revision_no`（`WorkbenchPage.tsx:239`）、undo 禁用均落地；但**失败路径的错误呈现完全不可见**（P1-1），故「失败即原态+typed 错误块显式呈现」的 ✓ 声明不成立。undo 禁用是 A6 红线下的合规落法（无 IPC restore 命令面；`restore_revision` 仅存在于应用层，见 P4-4）。 |
| AC2 E1–E4 视觉 | PASS | **PASS** | E1 外圈 warn 2px 实线叠加于基框外（`RegionOverlay.tsx:151-164`）、E2 `♪?` pill、E3 三档查找表 pill、E4 反馈条画布底部居中 36px + 双禁用按钮+title（`ViewerPanel.tsx:181-255`）；RC-1 裁定成立（见 §6 风险）。条件：P2-1/P2-2/P2-3。 |
| AC3 Design-to-impl 保真 | PASS | **PASS（带条件）** | 偏差 9 条与代码注释逐一对应、登记诚实；但漏登记项与一处测试覆盖声明不实（P2-4、P3-1、P3-2、P4-6）。 |
| AC4 测试与回归 | PASS | **PARTIAL** | 数字自洽已复算：`relabelMachine.test.ts` 20（4+1+4+4+3+4）+ `WorkbenchPage.test.tsx` +5 = **+25**，102=77+25，逐文件计数与 `vitest-verify.log:6-19` 一致；pytest `1 failed, 1847 passed, 1 skipped`（`pytest-full.log:399`）与父 Task 基线（`verification/M2-WORKBENCH-REACT-1/raw/main-regression-postmerge-pytest.log:399` 同为 1847+1+1，失败项同为既有 `test_catalog`）等量一致；build `EXIT=0`（`npm-build.log:10-11`）。但合同要求的「撤销 + 失败路径」交互测试**不存在**（P2-4），且 `vitest-machine-green.log` 只覆盖 16 例（交付文件 20 例，P3-3）。 |
| AC5 文档 | PASS | **PASS** | Task 回填 + Handoff + 设计尾注齐备（`design.md:343` 为追加注记，原文未见回改痕；`doc/STATUS.md`/`REBASELINE_PLAN.md` 仍标记 ready，与禁改面一致）。 |

---

## 5. 分级发现

### P1（必须返修）
**P1-1 改标失败的 typed 错误块在 UI 中永不渲染（违反 R6，且 Task/Handoff 声明与实现不符）**
- `apps/desktop/frontend/src/workbench/WorkbenchPage.tsx:263-278`：`catch` 中先 `setConfirmTarget(null)` 再 `setRetypeError(...)`；而 `retypeError` 的**唯一**消费点是确认框 `errorText`（`WorkbenchPage.tsx:412-425`，渲染条件 `confirmTarget &&`）→ 确认框同批卸载，错误文本永远不可见。
- 正向 speech→sfx 失败时根本没有确认框（`confirmTarget` 为 null），错误同样不可见；`ViewerPanel` 反馈条的 error 分支（`ViewerPanel.tsx:181-217`）因 `isError:true` 全仓从未被设置（仅 `WorkbenchPage.tsx:248` 的 `isError:false`）而成为死代码。
- 影响：用户遇到 `INPUT_REVISION_CHANGED`/`TARGET_NOT_FOUND` 等失败时，界面表现为「点了没反应」；这正是 AC1 强调的并发保护路径。Task 回填 :52 与 Handoff :28 的「typed 错误块 `relabel-feedback`/`retypeError` 显式呈现」不成立。
- 处置建议：把失败写入反馈条（`setFeedback({isError:true,text})`）或新增 workbench 级错误块（沿 `library-error`/`sfx-save-error` 先例），并在确认框路径保留对话框；同时补失败路径组件测试。

### P2（应返修）
**P2-1 工具栏残留「改标工具（预留）」陈旧占位，与回填「预留控制不复存在」冲突**
- `apps/desktop/frontend/src/workbench/WorkbenchToolbar.tsx:32-50` 仍渲染 `toolbar-retype-reserved`（disabled，title 仍写「改标入口属 M2-SFX-MISROUTE-UI-IMPL-1（本刀预留禁用态）」）。
- 证据对照：旧断言曾同时断言两个预留控件（`verification/.../raw/vitest-impl.log:15-16,56` 显示旧测试断言 `inspector-retype-reserved` **与** `toolbar-retype-reserved`），更新后的断言（`WorkbenchPage.test.tsx:53-62`）只覆盖 inspector，静默丢掉工具栏这一条；Task 回填 :72「reserved 控制不复存在」为过宽陈述。
- 处置建议：删除该占位（或改为有当前语义的禁用项），并恢复一条工具栏断言。

**P2-2 Inspector 文案承诺「可随时撤销」，与 undo/历史双禁用矛盾**
- `RegionInspector.tsx:108`「可随时撤销（经 revision 历史）」，但 `RegionInspector.tsx:181-198` 的历史按钮 disabled、`ViewerPanel.tsx:219-235` 的撤销 disabled；用户可读到一条无法履行的承诺（设计 §4.3-2 要求该事实真实可读）。
- 处置建议：在注记中标注通道未落地原因，或改写为条件句。

**P2-3 §4.4/R4「改标 ≠ 抹除已贴译文、成品图需重渲染」语义缺失且未登记**
- `relabelMachine.ts:130-162` 全部反馈文案无「原图完好，成品图需重跑渲染才恢复原文」语义；`ViewerPanel.tsx:236-252` 只给一个永久禁用按钮；Task 偏差 9 条（回填 :58-68）仅登记「rerender 按钮禁用」，未登记该文案义务缺口（设计 §4.3-4 / §4.4 为 FROZEN）。

**P2-4 AC4/AC3 覆盖声明不实（撤销、失败路径、A3 测试均不存在）**
- 全仓无 `onToggleSuspect` 测试（grep 仅命中实现文件），故 Task 回填 :54「A3（suspect toggle 零 Core 调用）」落 vitest 的声明无证据；无失败路径测试；`RelabelConfirmDialog`/`RelabelContextMenu`/`ViewerPanel` 反馈条零组件测试。
- 处置建议：补测试或显式登记覆盖缺口，并修正 AC3/AC4 表述。

**P2-5 缺 diff 面证据（A1/禁改面无法用证据闭合）**
- `verification/M2-SFX-MISROUTE-UI-IMPL-1/raw/` 仅 8 个构建/测试 log，无 `git diff --name-status ecbfe9cb..e70356e5` 或 allow/deny 面清单；相比之下同类 Task 均带 scope-proof（如 `verification/M2-RC2/raw/final-diff-name-status.txt`）。
- 处置建议：集成时补一份 diff 面 raw（本轮我已用静态内容核对作临时替代：新标识符仅出现在 frontend + doc，未泄漏进 `src/**`、`src/ui/qml/**`、`src-tauri/**`、`contracts/**`）。

### P3（建议）
- **P3-1 A13(b) 未取证/未登记**：全前端无 CSS/token 定义（glob 零命中），fallback 即实际生效值却声明非真值；画布衬底硬编码 `#0b0e12`（`ViewerPanel.tsx:127`）未走 `bg-canvas`。建议随 A13(a) 一并登记 `(b)` 的静态或基线取证。
- **P3-2 `OTHER_TYPE` 为 §4.1 之外的第四相位**（`relabelMachine.ts:36,55`），未列入 9 条偏差；属 A12 的派生根，非拓扑篡改，建议补登记以免误读为静默新增状态。
- **P3-3 先红后绿证据不完整**：`vitest-machine-green.log:6,9` 为 16 例，交付文件为 20 例，后 4 例（`retypeFeedback` 组）无红先行证据（终态绿见 `vitest-verify.log`）；Task :55 已如实写 16/16，但 AC4 的「先红后绿」只部分成立。
- **P3-4 确认闸门位置脆弱**：`doSetRegionType` 把 `plan.kind==="confirm"` 也视为可执行（`WorkbenchPage.tsx:232`），A5 依赖调用点纪律；建议改为显式 `confirmed` 入参或拆分 execute/confirm 函数，避免后续调用者一键直达。
- **P3-5 右键菜单无失焦/Escape 关闭**（`ViewerPanel.tsx:64-90`；`RelabelContextMenu` 无 backdrop/keydown）：空画布点击只清选中、菜单常驻。
- **P3-6 `[重渲染本页]` 无条件渲染**：`offerUndo/offerRerender`（`relabelMachine.ts:122-123`）从未被 `ViewerPanel` 消费；§4.4「在有已渲染产物时附」无法满足（读面无产物字段），建议登记。

### P4（备注）
- **P4-1** `SFX_RELABEL_OK` 仅以瞬态 feedback state 表达，无 undo 窗口计时（已登记偏差 7）。
- **P4-2** 选中框描边 2.5px（`RegionOverlay.tsx:173`）vs 设计「选中内圈 accent 2px」；E1 外圈实际间距 ≈2.25px（`x=box.x-4`、stroke 2）vs 「2px」——继承/取整差，建议视觉基线时冻结。
- **P4-3** 改标成功后 `refreshRegions` 使用永不取消的本地 signal（`WorkbenchPage.tsx:260-261`），极端情况下迟到响应可能落到已卸载/已切页的状态。
- **P4-4** 「Core 无 restore runtime」表述建议精确化：应用层**已有** `RegionEditingService.restore_revision`（`editing/service.py:694-716`），缺的是 IPC/Tauri 命令面（`PROTOCOL_MINOR=3` 未暴露）；不影响 AC1=PARTIAL 结论，但「Core 无 restore」易被误读为能力完全不存在。
- **P4-5** feedback 跨页不清理：切页后 `feedbackRegion` 变 null，反馈条保留文案但动作按钮消失（`ViewerPanel.tsx:88-90,217`）。
- **P4-6** 草稿多边形右键互斥语义退化为「仅 region 框上开菜单」（`RelabelContextMenu.tsx:5-7`），仅代码注释说明，未进 9 条偏差清单（本切片无草稿态，无实际冲突）。

---

## 6. 残留风险与集成建议

1. **RC-1 裁定核验结论：成立。** 设计 R1 原文「警示置位本身不写 region revision（是 UI 辅助信号不是领域变更）」「初始唯一置位来源是人工」（`design.md:223`）+ OPEN-2 边界支撑「suspect=纯 UI 内存态」；实现零持久化（全 `frontend/src` 无 `localStorage/sessionStorage/indexedDB`）、零 Core 调用、不写 revision（`WorkbenchPage.tsx:61,216-226`），E1 不渲染不虚构约束满足。若未来需要 heuristic/跨端/持久化，再按 OPEN-2 释放字段 Task 是正确的判据链。
2. **A6 vs R5 张力**：undo 禁用是当前唯一的 A6 合规落法（反向改标模拟撤销被红线禁止；`RestoreRegionRevision` 无命令面）。但请注意 P1-1 使「失败可感知」这一兜底体验缺失，叠加 undo 不可用后，用户在改标失败/改错时缺少任何恢复线索——强烈建议 P1 修复与「历史/undo 命令面」Task 一起排期。
3. **状态机拓扑保真**：四分支与守卫①②已忠实落地；`SFX_ARB`/`SFX_ARB_RELABEL` 不可达、`SFX_RELABEL_OK` 退化为瞬态反馈、undo 窗口缺失，均已登记；未发现静默删除既有转换，`OTHER_TYPE` 为 A12 派生根（建议补登记，P3-2）。
4. **WORKBENCH 读取面零破坏**：RegionOverlay 三条硬规则字面成立——尺寸仅来自 `pageSize` 投影（`RegionOverlay.tsx:58,89`）、仅归一化值过界（`geometry.ts:76-100` 单一数学）、新增 pill 几何全部由 `projectRegionBox` 的 box 派生（`RegionOverlay.tsx:107,119-123,192-199`），无散落换算 ✓。既有 SSR 测试更新 1 处为最小替换，但静默缩窄了工具栏断言（P2-1）。
5. **数字自洽**：vitest 102=77+25 逐文件复算成立；pytest `1847+1sk+1 failed` 与父 Task 基线逐字等于同一既有 `test_catalog`（manifest 122 vs 期望 97）失败；红/绿 log 时间戳有序（23:11:20 < 23:12:37 < 23:19:30 < 23:21:31 < 23:22:58）。
6. **NOT_IN_SCOPE 检查：无越界。** Reader 提示条未实现（无 Reader 页）、RC-4/RC-5 未触碰、detect/翻译链行为零改动、设置页三值零改动；新命令面零新增（前端只消费既有 `set_region_type`/`list_regions`）。
7. **集成建议**：①P1-1 修复+失败路径测试为合并前置；②P2-1/P2-2/P2-3 文案与占位清理同批做掉；③补 diff 面 raw；④Qoder 非作者 UI/UX 复审（E1/E2/E3 pill 几何、E4 反馈条形态）仍待派发通道可用；⑤undo/rerender/`ListRegionRevisions` 命令面建议作为单个 RC-4 域 Task 释放，之后才可启用三个禁用入口；⑥A13(a) 取证与 token 真值链（当前前端连 `tokens.css` 都不存在）绑定落地。

**推荐下一步**：把本报告 P1-1（失败错误呈现）+ P2-1/P2-2/P2-3 作为 r1fix 返回 Owner（ZCode/编排接管身份）返修并补失败路径测试与 diff 面证据；返修后再交本轮同一 Reviewer 做 r2 复跑核验，之后才进入集成 Gate。
