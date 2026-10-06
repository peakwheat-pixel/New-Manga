---
id: M2-SFX-MISROUTE-UI-IMPL-1
title: "SFX 误路由缓解 UI 产品实现：E1-E4 视觉+不对称状态机+改标交互（设计契约 M2-SFX-MISROUTE-UI-MITIGATION 的实现切片）"
kind: feature
status: in_review
owner: ZCode
reviewer: DeepSeek Harness（非作者，技术主审）；Qoder（非作者 UI/UX 复审，派发通道可用时补审）
integrator: 编排会话代行 Codex（用户全权授权）
approval: user_2026-10-06「释放：Workbench React 页（依赖已就绪）、UI-MITIGATION 实现（blocked 已解除）、BJ13 召回恢复链」三件之一（候选 B；**blocked_on M2-WORKBENCH-REACT-1 集成，接力派发**）
depends_on: [M2-SFX-MISROUTE-UI-MITIGATION, M2-WORKBENCH-REACT-1]
base_commit: ecbfe9cb
branch: agent/zcode/M2-SFX-MISROUTE-UI-IMPL-1
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-MISROUTE-UI-IMPL-1-zcode
review_events: [r1 2026-10-06 DSH 非作者 changes_requested（1×P1+5×P2+6×P3+6×P4；A1-A13 逐条判定+RC-1 裁定核验成立；返修见 r1 返修段）]
created: 2026-10-06
---

# Task: M2-SFX-MISROUTE-UI-IMPL-1 — UI-MITIGATION 产品实现

## claim 与 base 对账（2026-10-06）

- frontmatter `base_commit: 3a65150b`（释放登记值）→ 更正为 **`ecbfe9cb`**（实际 worktree 起点）：释放链 `3a65150b→630c3f51→2a1a9f73` 两 commit 为纯文档释放登记（零代码面），其后 A/C 两 Task 全链闭环至 `ecbfe9cb`——派发时序（接力等 WORKBENCH-REACT-1 集成）由编排方在派发前把本 worktree 分支 reset --hard 到 `ecbfe9cb`，本 Task 在其上叠加。沿 M2-WORKBENCH-REACT-1 先例（frontmatter 写实际起点，漂移注记移正文）。
- 前置就绪面已核：region/client.ts setRegionType+RegionListSummary 六字段（含 rev1.5 可选 geometry）+WorkbenchPage 五区+RegionOverlay 只读画框（pointerEvents:none=第一刀定位）+RegionInspector 预留禁用按钮——与本合同 AC1/AC2 落点一一对应。


## 背景与授权

用户 2026-10-06 释放三件中的候选 B。设计契约 M2-SFX-MISROUTE-UI-MITIGATION（done @merge `4d77a778`）登记「产品实现 blocked_on Workbench React 页+region 通道」——该前置由 M2-WORKBENCH-REACT-1（候选 A，同批释放）交付：React 页壳（`<WorkbenchPage>` 五区+`<RegionOverlay>` SVG 只读画框+`<RegionInspector>`）+ region client（`listRegions`/`setRegionType`）+ D5 几何读取面。

**派发时序（真依赖，非配额）**：本 Task status=ready 但 **Owner 派发等 M2-WORKBENCH-REACT-1 merge 后接力**——E1-E4 落点组件（`<RegionOverlay>`/`<RegionInspector>`）与数据通道（region client+几何）在前置集成前不存在于集成态。同批释放=合同冻结与授权就位，避免二次请示。

## 验收条件

- **AC1 改标交互全套（不对称状态机，FROZEN §4.1）**：speech→sfx 即时执行无确认（R2）、sfx→speech 显式确认框明示后果（R3，含 §4.2 反馈条文案——EV-8 已 CLOSED：改标按当前配置重快照，translate 行可达须明示「将按拟声词翻译链重新翻译」）、撤销=revision 恢复回触发态（R5，undo=restore 到改标前 revision 非二次改标）、失败即原态+来源守卫（R6）；消费 `setRegionType`（expected_revision 并发保护，INPUT_REVISION_CHANGED 处理沿 §5.4 错误码映射）。
- **AC2 E1-E4 视觉按设计实现**：落点 `<RegionOverlay>`（SVG 层）+`<RegionInspector>`（§3.2）；E4 反馈条于 ViewerPanel 画布底部居中（:119-121）；改标入口示意 :126-142。E1 疑似警示的数据源=`suspect.sfx` 字段（RC-1）——**RC-1 契约修订归本 Task 裁量**：字段未落地前 E1 不渲染、不虚构数据（设计 :150 原文约束）；若 Owner 判定本 Task 含 RC-1 additive 修订（M2-C1 rev 追加+Core runtime+minor 处置），沿 WORKBENCH-REACT-1 AC1 的核实-择一-登记流程；若判定不含，E1 登记为「数据源 NOT_IN_SCOPE 待后续字段 Task」并在交付注记——二择一须在 Task 内显式登记理由。
- **AC3 Design-to-impl 保真核验**：设计文档 §2 状态机、§3 视觉、§4 反馈文案逐条对照实现，偏差逐条登记（设计为 FROZEN 契约，实现偏差=偏差登记非静默改动）；设计 §7 断言（13 条）中 UI 可测面落入 vitest。
- **AC4 测试与回归**：vitest 交互状态机单测（四分支+撤销+失败路径先红后绿）+组件测试；前端基线等量递增；pytest 基线不破坏；若触 Core runtime（RC-1）则受影响套件等量递增+契约修订草案登记。〔实现口径注（r2 N-1）：本前端零 DOM 测试环境（无 jsdom/happy-dom），「失败路径」覆盖=纯函数决策面（planRetypeAction 四分支）+反馈条 error/success 变体 SSR 断言；WorkbenchPage 交互接线（catch→isError 传播）静态可读但无 DOM 级测试——如实登记为 PARTIAL。〕
- **AC5 文档**：Task 回填+Handoff+设计文档尾注（实现完成状态注记，设计原文不回改——沿 EV-8 集成注记先例 :340）。

## 纪律与限制

- 允许路径：`apps/desktop/frontend/**`、`src/bootstrap/core_service.py` 与 Core 应用层（仅 AC2 选含 RC-1 时，逐文件声明）、`apps/desktop/src-tauri/**`（仅 RC-1 需要新命令时，逐文件声明）、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（仅 RC-1 additive 修订）、`doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md`（仅文尾实现注记）、`tests/**`、`verification/M2-SFX-MISROUTE-UI-IMPL-1/**`、`doc/tasks/M2-SFX-MISROUTE-UI-IMPL-1.md`、`doc/handoffs/`。
- 禁改：设计契约 §4.1 状态机语义（FROZEN）、`src/ui/qml/**`、GATE runner 场景集、`doc/STATUS.md`/`doc/REBASELINE_PLAN.md`（集成方收口面）、M2-WORKBENCH-REACT-1 已交付的页壳读取面行为（在其之上叠加）。
- **范围边界**：Reader 页级提示条（§3.3）——Reader React 页不存在，本 Task 不实现、不虚构；RC-4/RC-5 不在范围；detect/翻译链行为零变更（本 Task 纯 UI 层+可能的 RC-1 数据面）。
- Owner 分工注记：同 M2-WORKBENCH-REACT-1（ZCode 实现、Qoder 非 author UI/UX 复审可选）。


## 交付回填（2026-10-06，Owner=编排接管[配额耗尽后同身份续做]，status→in_review）

### AC 逐条判定

- **AC1 改标交互全套（不对称状态机 FROZEN §4.1）——PARTIAL（undo 执行面登记缺失，语义面全合规）**：正向 speech→sfx 即时执行（R2，planRetypeAction→execute，无确认框）✓；反向 sfx→speech 显式确认框（R3/A5，`RelabelConfirmDialog`，文案含「重新进入对白翻译链，可能产生新的译文」+「改标只修改标注，不改动原图文件」固定安全文案，st-fail 边）✓；失败即原态（R6：零乐观变更+typed 错误块 `relabel-feedback`/`retypeError` 显式呈现无自动重试；守卫②取消=仅关框零回滚）+expected_revision 并发保护（region.revision_no 作 expected）✓；**undo=禁用态+原因 title**（`UNDO_DISABLED_TITLE`：Core 无 restore 命令 runtime [PROTOCOL_MINOR=3 无此命令]，A6 红线禁止以反向改标模拟撤销——禁用是唯一合规呈现，通道属后续命令面 Task [RC-4 域]）→ 状态机四分支中 undo 转换为登记性禁用，判 PARTIAL 如实登记。
- **AC2 E1-E4 视觉——PASS**：E1 警示外圈（warn 2px 实线，基框外 2px 间距，选中内圈 accent+警示外圈 warn 两层并存）+E2 warn pill（♪? 疑似拟声词）+E3 sfx pill（♪ SFX·保留原文/手动处理模式/拟声词翻译链 三档查找表）+E4 反馈条（ViewerPanel 画布底部居中 36px，结果文案=policy 快照分档+[撤销][重渲染本页] 双禁用态+title 原因）——全部落 RegionOverlay SVG/ViewerPanel/RegionInspector；三重编码 A8（字形+颜色+文本齐备，vitest 断言）。**RC-1 裁定=不含（裁量理由）**：设计 R1 原文「警示置位本身不写 region revision（是 UI 辅助信号不是领域变更）」「初始唯一置位来源是人工」→ suspect 实现为**纯前端 UI 内存态**（`WorkbenchPage.suspects: Set<regionId>`，零 Core 调用零持久化），RC-1 契约修订仅在需要持久化/heuristic 来源/跨端共享时才必要（设计 OPEN-2 边界原文）；E1 不渲染不虚构约束满足（A2：置位不依赖 OCR/候选——planRetypeAction/derivePhase 签名根本不接受 OCR/候选输入）。Reader 页级提示条未实现（合同范围边界：Reader React 页不存在）。
- **AC3 Design-to-impl 保真——PASS（偏差 9 条全登记，见下）**：§7 断言 UI 可测面落 vitest：A2（planRetypeAction 无 suspect 外部输入参数=构造性满足）、A3（suspect toggle 零 Core 调用=实现事实静态保证，**非 vitest 断言**——零 DOM 环境见 AC4 口径注）、A5（plan confirm 分支钉测）、A8（badge glyph+文本 SSR 断言）、A9（E3/E4 全部为 Core 快照查找表，零决策逻辑）、A12（canRetype 禁用+原因逐类型钉测）。
- **AC4 测试与回归——PARTIAL（r2 N-1 口径：交互接线零 DOM 测试）**：测试数字与构建全绿（如下），但 WorkbenchPage 失败接线（catch→isError）无 DOM 环境测试——失败路径=静态可读+变体渲染 SSR 断言，接线本身零测试；vitest 77→**105 passed**（终态；首轮 +25=relabelMachine 20+overlay 5，r1fix +3=feedback 两变体+artefact 文案）EXIT=0（先红后绿：`vitest-machine-red.log` 首轮红→green 16/16——**16/20 红先行，retypeFeedback 组 4 例随实现同轮补，P3-3 已精确化**）；`npm run build` EXIT=0（485ms）；pytest 1847 passed+1 skipped+1 failed（test_catalog 既有 BASELINE_FAILURE）=基线等量（跑 env=T1.1.1-impl-py312 venv；前端零 Python 触碰）。
- **AC5 文档——PASS**：本回填+Handoff+设计文档尾注（原文不回改）。

### Design-to-impl 偏差登记（设计 FROZEN，偏差=登记非静默改动；共 11 条）

1. **SFX_ARB 态不可达**：状态机拓扑含 SFX_ARB（机器改标），但 RegionListSummary 六字段不含 label 前缀（`sfx-arb-`），读取面无法区分仲裁改标 sfx 与检测直产 sfx→`derivePhase` 不返回 SFX_ARB、E3 的 ⧉ 机器笔字形不渲染（A7 的可区分性在当前读取面不可实现，属 RC-4 域缺口；机器笔追溯不经 UI 丢失——Core revision 历史仍全量保存）。
2. **undo 禁用**（AC1 已述）：restore 命令 runtime 缺位；E4 反馈条与 Inspector 均呈现禁用态+原因。
3. **重渲染按钮禁用**：`rerender_single` run 通道 runtime 未实现（契约 §5.1 PROPOSAL 层，设计 §5 D10「已承载（设计层）」）。
4. **revision 历史入口禁用**：`ListRegionRevisions` 命令名有但 DTO 未定义（设计 §5 D7/RC-4）。
5. **RC-1=不含**（AC2 已述裁量）：suspect=纯 UI 态；OPEN-2 持久化需求出现时另行释放字段 Task。
6. **Reader 页级提示条不实现**（合同范围边界+设计 §3.3 数据面 RC-5 缺口）。
7. **undo 窗口 10s 定时器未做**（EV-4）：undo 通道本身禁用，窗口计时随 restore 命令面 Task 一并落地；E4 反馈条常驻至下一次交互（无自动消失——比设计更保守，无超时误关）。
8. **token 真值链未落地**：颜色以 `var(--token, fallback)` CSS 自定义属性引用（fallback=设计对照参考 hex），未新建 tokens.css（真值链属 M2-UI1 后续）；E2/E3 pill 尺寸（20px/12px/8px/3px 8px）登记为组件常量（EVOLVING-3 登记义务）；**A13(a) E3 新组合首次取证 deferred**——token 实值未定，对比度取证在 token 真值链落地后执行（登记为 Visual-baseline Task 义务）。
9. **A13(b) 取证口径**（r2 N-3 并入）：全前端无 CSS/token 定义，`var(--x, fallback)` 恒解析 fallback（即当前实际生效值）；画布衬底已 token 化 `var(--bg-canvas, #0b0e12)`；A13(b) 静态估算 E1 fallback `#fbbf24` vs 衬底 ≈11.6:1（≥3:1，DSH r2 按 WCAG 公式复算 11.59:1 一致，非权威），权威取证随 token 真值链落地。
10. **OTHER_TYPE 第四相位**（r2 N-3 并入）：`derivePhase` 对非 speech/sfx 类型返回 OTHER_TYPE——§4.1 拓扑之外的 UI 派生根，是 A12 禁用逻辑的判定基础，非拓扑新增/篡改。
11. **EV-5 全局不一致提示行未做**：E3/E4 只读 region 自身快照（A9 优先级规则满足），「与全局设置不一致」辅助解释行 deferred（EVOLVING-5，需要 settings_get 全局值接入，非本断言范围）。

### 既有断言更新（前置 Task 测试 1 处）

- `WorkbenchPage.test.tsx`「keeps the retype entries RESERVED and disabled (IMPL-1 owns enablement)」→ 本 Task 即 IMPL-1，预留禁用控制已被真实双入口取代；断言更新为「reserved 控制不复存在+未选中 region 时不渲染入口」（更新理由=前置断言的本 Task 交付前提成立，沿 WORKBENCH-REACT-1 按 1.5 口径更新 2 处断言先例）。

### 证据与 commit

- raw：`verification/M2-SFX-MISROUTE-UI-IMPL-1/raw/{npm-install,vitest-machine-red,vitest-machine-green,vitest-impl,vitest-impl2,vitest-verify,npm-build,pytest-full,vitest-r1fix,npm-build-r1fix,r1fix-diff-name-status}.log/txt`（r2 N-5 补列 r1fix 三件）
- Handoff：`doc/handoffs/M2-SFX-MISROUTE-UI-IMPL-1-zcode-20261006.md`
- 设计尾注：`doc/design/M2-SFX-MISROUTE-UI-MITIGATION/design.md` 文尾实现状态注记（原文零回改）

### r1 返修段（DSH 非作者 2026-10-06：changes_requested——1×P1+5×P2+6×P3+6×P4，全部闭合或登记；r1fix commit `5dd325b8`+本文档 docs 补充）

- **P1-1（闭合，代码+测试双闭合）**：改标失败错误呈现不可达（retypeError 唯一消费点在确认框、catch 先卸框=死代码）——修复：①正向失败走 E4 反馈条 error 变体（`isError:true`，fail 边框+无动作按钮，r1 指出的死分支激活）；②确认框路径失败**保留对话框**框内显示 typed 错误（不再关框）；③补 error/success 两变体 SSR 断言（ViewerPanel feedback describe ×2）。Task 原「typed 错误块显式呈现」声明自此成立。
- **P2-1（闭合）**：WorkbenchToolbar 陈旧占位 `toolbar-retype-reserved` 删除（断言静默缩窄同步修复——工具栏 not.toContain 断言恢复）。
- **P2-2（闭合）**：Inspector「可随时撤销」承诺改条件句「撤销/历史入口待 Core restore 命令面 Task 落地后启用（当前 UI 通道未开通）」。
- **P2-3（闭合）**：retypeFeedback 四分支文案全部补「原图完好；已渲染成品图需重跑渲染才恢复原文」（§4.3-4/§4.4 FROZEN 义务；读面无产物字段→无条件附=保守方向）+vitest 断言（5 分支逐条包含断言）。
- **P2-4（闭合可测面+表述修正）**：补 feedback error/success SSR 断言×2；**A3 覆盖表述修正**——onToggleSuspect 零 invoke 为实现事实（函数体仅 setSuspects 集合增删，静态保证），交互时序测试因本前端零 DOM 测试环境（无 jsdom/happy-dom）不设，沿「结构 SSR+逻辑纯函数」既定分工如实登记，不声称落 vitest；AC4 表述按 r1 下调 PARTIAL 认同（返修后闭合）。
- **P2-5（闭合，r2 N-2 修正口径）**：`raw/r1fix-diff-name-status.txt` 初版仅覆盖 r1 锚 e70356e5 面（漏 WorkbenchToolbar/r1fix 两 log）——r2fix 已重生成覆盖 **ecbfe9cb..3474affa** 全 diff 面（11 前端+3 文档+verification raw，零 Python src/**/src-tauri/qml/GATE 触碰）。
- **P3-1（闭合登记）**：A13(b) 并入偏差 8 扩充——全前端无 CSS/token 定义，`var(--x, fallback)` 恒解析 fallback；画布衬底本次已 token 化 `var(--bg-canvas, #0b0e12)`（r1fix 顺笔）；A13(b) 静态估算 E1 fallback vs 衬底 ≈11.6:1（≥3:1，非权威），权威取证随 token 真值链。
- **P3-2（闭合登记）**：OTHER_TYPE 补偏差第 10 条（A12 派生根，非拓扑新增）。
- **P3-3（表述修正）**：先红后绿=「16/20 红先行（retypeFeedback 组 4 例随实现同轮补）+终态全绿」，AC4 行已按此精确化。
- **P3-4（闭合）**：doSetRegionType 增 `opts.confirmed` 结构化闸门——confirm 类转换未带 confirmed=true 不达 wire（A5 从调用点纪律升为结构纪律）。
- **P3-5（闭合）**：stage 空白右键关菜单+Escape 关菜单（tabIndex+onKeyDown）。
- **P3-6（登记）**：offerUndo/offerRerender 无条件 true（读面无产物字段）——与 P2-3 文案无条件附同口径。
- **P4-1（r2 N-4 补登）**：resource 通道错误码判定 `instanceof TypedChannelError ? code : (error as {code?})?.code`（WorkbenchPage.tsx:186-193）——按 r1 P4-1 建议以代码修复处置（非纯登记），此前清单漏列。
- **P4 登记**：P4-2 选中描边 2.5px/间距 2.25px（视觉基线冻结）；P4-3 refreshRegions 本地 signal 永不取消（登记）；P4-5 feedback 跨页不清理（登记）；P4-6 草稿互斥退化（无草稿态，登记）。
- **N-6（r2，闭合）**：用户可见口径统一——`UNDO_DISABLED_TITLE` 改「应用层已有 restore_revision，缺 IPC 命令面（待命令面 Task）」；Inspector 注记「撤销/历史」分称（撤销=restore 命令面；历史=ListRegionRevisions 命令面）。
- **P4-4（表述精确化）**：「Core 无 restore」→「Core **应用层已有** `RegionEditingService.restore_revision`（editing/service.py:694-716），缺的是 IPC/Tauri 命令面（PROTOCOL_MINOR=3 未暴露）」——undo 禁用理由表述随此精确化（结论不变）。
- r1fix 复跑：vitest **105**（102+3）EXIT=0、build EXIT=0（431ms）；pytest 免重跑（零 Python 触碰）。
