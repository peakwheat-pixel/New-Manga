全部静态证据已收集完毕。测试与 tsc 命令被当前会话的 Plan mode 工具策略拦截（vitest/tsc/npm 均被拒绝执行），无法运行——报告中如实说明。以下为最终审查报告。

---

## 结论

**有条件通过**——规格核心（令牌、亚克力四件套、七态编码、性能闸门、三页几何）实现质量高且有行为测试锁定，但存在 4 个 P1：设计 CSS 经静态导入全局泄漏到既有 probe/ac1/生产路径（违背“零变化”承诺）、字阶与阴影存在一批规格外自创值、tablist 键盘交互与 ARIA 结构违规、阅读器键提示为假承诺。

## 严重度统计

P0 0 · P1 4 · P2 9

## 问题清单

### P0（阻断：必须修）

无。

### P1（应该修）

- **[DesignPreview.tsx:6-9 + App.tsx:8]** 设计层 4 个 CSS 文件（tokens/base/acrylic/pages）经 `App.tsx` → `DesignPreview` 的**静态导入链进入主 bundle，对所有视图全局生效**，直接违背“全部挂在 `?view=design` 独立入口下，不影响既有 Tauri 运行时路径”。具体泄漏：`base.css:26` `body { overflow: hidden }`（probe/ac1 控制台日志超出一屏后**不可再滚动**，改变冻结窗口呈现）；`base.css:43-48` button 全局 reset（production AppShell 按钮仅部分内联覆盖，`padding: 0` 等未覆盖属性泄漏）；`base.css:54-57` `svg { display: block }`、`base.css:59-67` 全局 `::selection`/`:focus-visible`、`base.css:69-88` 全局滚动条样式。既有 jsdom 测试不应用 CSS 所以不会红，风险只在真实渲染。→ 修法：把 4 个 CSS 导入改为 `?view=design` 分支内动态 `import()`（Vite 会拆独立 chunk），或给所有 body/全局规则套 `html[data-view="design"]` / `.nm-preview` 作用域并在 DesignPreview 挂载/卸载时维护该属性（参考其 `data-theme` 恢复模式）。
- **[pages.css:392,482,545,558,827,1039,1091,1156,1294; base.css:361; StatusMark.css:22]** UI 文本使用规格外字号：11px（书卡脚注/区域文本/流水线阶段/气泡）、10px（章节索引与页数/OCR meta/kbd）、9px（胶片条页号）、18px/22px（统计数值）、13px（状态符号）。规格字阶只有 28/20/14/12 四档。封面与页面占位图上的 7/8/9/22px（pages.css:324,335,347,1223,1327）属内容装饰字，可豁免但请 DSH 明确认定。→ 修法：UI 文本收敛到 Caption 12/16（或 Data 12/16），`nm-stat__value` 若需大数字请向规格方申请第五档令牌，不得散落硬编码。
- **[base.css:346; pages.css:102,277,339,421,861,914]** 阴影规格外自创档位：`0 1px 2px rgba(0,0,0,.14/.12/.10)`（分段控件/tab/书卡静息态）、`0 2px 8px rgba(0,0,0,.14)`（画布工具条×2）、`0 4px 10px rgba(0,0,0,.22)`（详情封面）、`text-shadow 0 2px 10px .35`（封面标题，装饰可豁免）。规格只允许两档 elevation。→ 修法：静息态小阴影删除或并入 elevation-8；工具条用 elevation-8。
- **[PrimaryNav.tsx:27-44; Workbench.tsx:171-199; Reader.tsx:168-180]** 键盘可访问性三连：(a) PrimaryNav 与 Workbench rail 均声明 `role="tablist"/"tab"` 但**无任何方向键处理与 roving tabindex**（规格审查点 4 的直接答案：方向键不能切换）；(b) Workbench rail 的 tablist 容器内混入两个**无 role="tab" 的按钮**（主题切换、设置，Workbench.tsx:188-199），违反 ARIA tablist 子元素约束；(c) 阅读器底栏画着 `← → 翻页`、`F 全屏` 键提示但组件**没有任何键盘处理**（Esc 恰好借 DesignPreview.tsx:69 兜底成立）——假承诺应删提示或补实现。→ 修法：tablist 补 ArrowLeft/Right（rail 补 Up/Down）+ roving tabindex；rail 的非 tab 按钮移出 tablist 容器；Reader 补 keydown 翻页或移除 keyhint。

### P2（建议）

- **[base.css:291; pages.css:84,200,467,565,604,1097,1152,1383,1392 等]** 间距规格外硬编码值 1/2/5/6px（规格 4/8/12/16），未走 `--nm-space-*` 令牌，两处体系并存。
- **[base.css:104-109 + pages.css:26-29 + Shelf.tsx:271]** `.nm-shelf` 与 `.nm-mica` 定义了完全相同的 background-image，且 Shelf 同时挂两个类——同一背景写两遍，维护时易漂移；应只留 `.nm-mica`。
- **[acrylic.css:103]** `will-change: background-position` 常驻所有亚克力伪元素：background-position 动画不可合成（必然 repaint），will-change 无收益且常驻合成层有内存成本，建议删除。
- **[acrylic.css:150-158]** `@supports not (backdrop-filter)` 把 strong 档降为普通 `--nm-acrylic-tint`，丢失 tint-strong 的高不透明度；与 `.nm-acrylic-off`（保 tint-strong）的降级策略不一致，modal 在不支持 blur 的环境对比度反而低于预算降级层，建议统一用 tint-strong。
- **[useAcrylicBudget.ts:43-53]** hook 对空字符串 id（`[""]` join 后 length 为 0，该层被静默判 off）与 activeId 不在 layers 时的行为无防御性约束（当前三个调用方均正确，测试也覆盖了保守路径）；建议入口处过滤空 id、开发期断言 active ∈ layers。
- **[StatusMark.test.tsx:68-77]** "uses the 24x24 marker class hook" 只断言元素存在，与标题不符且无信息量；24×24 实际由 CSS 文本测试（79-84 行）覆盖，建议删除或改为断言渲染尺寸钩子。
- **[DesignPreview.test.tsx 全文]** 快捷键路径（Ctrl+1/2/3、T）与 URL 参数路径（`?page=workbench&theme=light`）无测试；tokens/acrylic/pages 三个测试是 CSS 源文本断言（作为规格锁合理），但不验证选择器级联真实生效——建议至少加一条 jsdom 下切换 `data-theme` 后断言 `getComputedStyle` 派生色的冒烟测试（如可行）。
- **[pages.css:221,403,981]** 规格栏距“区块 24–32”未达：书架主区/详情面板/检查器面板 padding 均为 16px，请 DSH 裁决该条指区块间距还是区块内边距。
- **[Shelf.tsx:550-602]** 命令面板声明 `aria-modal="true"` 但无焦点圈禁（Tab 可逃逸到背景），关闭后焦点不返回触发器；骨架阶段可接受，接真实交互前需补。

## 规格符合性逐项核对

| 项目 | 判定 | 说明 |
|---|---|---|
| 颜色令牌 | **符合** | dark/light 各 37 个变量与规格逐值比对全部一致（tokens.css:64-159），含七态+七 muted；测试锁定并校验两套键位同步。`data-theme` 写入/恢复逻辑正确，RuntimeApp 不读 `--nm-*`，index.html 改动本身无影响。 |
| 版式形状 | **部分符合** | 字体栈、六档字阶令牌、圆角 8/4/2/0（全库 59 处 border-radius 无一违规，含测试白名单锁定）、栏距 48、阴影两档令牌均符合；但存在规格外字号（P1-2）、6 处规格外阴影（P1-3）、间距 1/2/5/6px 与区块 padding 16（P2）。 |
| 亚克力四件套 | **符合** | 三档（40/24/40+strong）四件套齐全，含 -webkit- 前缀；噪声层参数全对（feTurbulence 内联 data URI、baseFrequency=0.5×3 处、opacity var(--nm-acrylic-noise)=0.08、hard-light、140% 140%、24s step-end）；三类降级齐备（@supports / reduced-transparency / reduced-motion）；仅 strong 档 @supports 降级不一致（P2）。 |
| 性能闸门 | **符合** | hook 算法正确：预算内全保留，超预算时 active 优先 + 声明顺序填充，Set 保证计数不超；`layerKey` 字符串 memo 使内联数组不致每渲染重算；无 effect 无泄漏；降级层用 tint-strong 保可读性；同一次 commit 原子切换类名，无双模糊窗口。三页声明（2/1/2 层）均正确，palette 打开时状态条实时降级有行为测试验证（DesignPreview.test.tsx:61-79）。 |
| 七态编码 | **符合** | 符号 `· ◐ ● ✗ ▲ ▨ – ○` 与规格逐一对应，颜色（专属令牌+muted）+符号+文字三重编码，`showLabel=false` 时文字转 sr-only 而非消失；24×24 标记块、圆角 4、无 emoji（有正则测试）。 |
| 三页骨架 | **符合** | 书架 5×168 网格、2:3 封面、340 详情（acrylic）、44 浮动条（acrylic-24）、标题栏/工具条 48；工作台 48/72/360（rail 48+panel 312）/40；阅读器 48 标题栏 + 顶 48/底 40 亚克力浮层，定位基准确为标题栏下方 `.nm-reader__body`（pages.css:1344-1355 有注释说明）。 |
| 动效 | **部分符合** | 悬停 120/140ms（区间内）、噪声漂移 24s step-end、状态切换 0ms（StatusMark 无过渡）、进度即时（≤200ms）均符合；抽屉 250ms decelerate 与共享元素 300ms 在骨架中**未实现**（无此交互），属未实现而非违规。 |

## 你实际做了什么验证

- `git log --oneline 65d9efa19..HEAD`：7 个提交（8647a4356…ee6473d1a），与任务描述一致。
- `git diff --stat 65d9efa19...HEAD`：23 文件、+4630/−2，与“约 20 新文件 + 3 修改”一致。
- `git diff`（App.tsx/index.html）+ `git show 65d9efa19:App.tsx`：逐行比对确认原 `App` 函数体仅改名 `RuntimeApp`、新增 15 行薄壳，probe/ac1/interactive 逻辑字节级未动；`?view=design` 时 RuntimeApp 不挂载、无探测副作用。
- 通读全部 23 个变更文件（tokens/base/acrylic.css、pages.css 全 1500 行、useAcrylicBudget.ts、3 页面组件、4 组件、6 测试文件）。
- `grep` 全量审计：59 处 border-radius 全部在 8/4/2/0/inherit 白名单内；`!important` 仅 reduced-motion 无障碍块 4 处（惯例允许）；全部 box-shadow/text-shadow 已列出；`nm-` 类名与既有代码（既有组件全内联样式、无 className、无 CSS 文件）无冲突；设计 CSS 仅被 DesignPreview.tsx 一处导入。
- **未能执行**：`npm test` / `npx vitest run` / `npx tsc --noEmit` 在本审查会话中被 Plan mode 工具策略拦截（多次尝试均被拒绝，理由“只允许只读非破坏性工具”）。因此 482/483 测试总数、全套通过状态、类型零错误**均未经我验证**，静态阅读未发现会导致测试失败或类型错误的问题（App.test.tsx 仍渲染默认导出且 URL 无 view 参数，语义路径不变）。浮层实际对比度、blur 渲染效果、无障碍树输出需浏览器验证——**无法静态验证**。

---

**推荐下一步**：本报告交 DSH 处置。若接受结论，建议在同一 Task 范围内指派 **ZCode** 修复（均在已冻结的设计层文件内，不扩产品范围）：P1-1 CSS 隔离（改动态导入或作用域化）、P1-2/3 字号与阴影收敛（封面装饰字是否豁免请 DSH 先裁决）、P1-4 tablist 键盘与 Reader 假键提示。可转发指令：「按 DESIGN-V2-IMPL-1 独立审查报告（P1-1~P1-4）在 agent/dsh/design-v2-impl-1 分支修复：设计 CSS 与默认运行时路径隔离、规格外字号/阴影收敛、tablist 方向键与 ARIA 结构、移除或实现阅读器键提示；修复后运行 npm test 与 tsc 并附结果」。修复完成后再由未参与修复的 Agent 复审 P1-1 的隔离效果。
