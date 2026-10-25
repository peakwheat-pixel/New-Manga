复审完成。全部 diff 与修改后文件已逐行核对，两个新引入问题成立（均有静态证据链）。以下为复审报告。

---

## 新结论

**不通过**——P1-1 的泄漏本身堵住了，但作用域前缀 `html[data-view="design"]` 使元素级 reset 的特异性升到 (0,1,2)，反超全部单类 button/select 组件规则，设计视图内按钮样式系统性失效（jsdom 测试与 tsc 均无法发现，这解释了 486 全绿）；另有 PrimaryNav 方向键焦点丢失一处 P1。

## 逐条核对

**P1-1 CSS 泄漏：部分修复**。泄漏方向已封死：`base.css:14-95` 全部元素级 reset 均加 `html[data-view="design"]` 前缀（逐条比对无遗漏，含 `*`/html/body/#root/button 组/svg/::selection/:focus-visible/滚动条四条）；`DesignPreview.tsx:52-59` 用独立 useLayoutEffect 设置并在卸载时恢复原值。`data-view` 全库唯一写入点就是该 effect（grep 证实），RuntimeApp 路径不触碰；无 StrictMode（main.tsx:10 明示），即便有也是 set→delete→set 收敛正确；测试 beforeEach/afterEach 均清理（DesignPreview.test.tsx:31,50）。首帧无闪烁（layout effect 先于 paint）。**但修复手段引入 P0 新问题，见下**。

**P1-2 字号：已修复（一处遗留）**。pages.css 中 `.nm-book-foot`(390)、`.nm-chapter__index`(543)、`.nm-chapter__pages`(556)、`.nm-filmstrip__no`(825)、`.nm-ocr-box__meta`(1037)、`.nm-region__text`(1089)、`.nm-stage`(1153) 9/10/11px→12px；base.css `.nm-kbd` 10→12px(367)；StatusMark.css mark 13→12px(22)。封面装饰字（title 22px/volume 9px/kicker 8px）与 `.nm-page-sheet__bubble` 11px 保留，与 DSH 裁决一致。遗留：`.nm-stat__value` 20px/22px 行高 + mono 字族（经 `.nm-data` 类，Shelf.tsx:469）不匹配任何规格档（Title 是 20/28/700 UI 字体），降级记入仍存在 P2。**12px 溢出静态核算：均安全**——胶片条三位页码 12px Cascadia Mono ≈22.6px < item 宽 64px；章节索引 ≈21.6px < grid 首列 32px；kbd「Ctrl」≈37px 但 kbd 无固定宽（min-width 18 自适应）；book-foot 双端合计 ≈97px < 卡内可用 144px；流水线 10 个 stage 变宽后窄窗口仍由既有 `overflow: hidden` 裁剪。

**P1-3 阴影：已修复**。base.css:350 分段控件、pages.css:102 tab、pages.css:277 书卡三处 `0 1px 2px` 删除；`0 4px 10px`(419) 与两处 `0 2px 8px`(859,912) → `var(--nm-elevation-8)`。修复后全库 grep：box-shadow 仅剩两档 elevation、`0 0 0 Npx` ring 描边（focus/选中语义，非 elevation）与豁免的封面 text-shadow(337)。

**P1-4 可访问性：部分修复**。Workbench rail：主题/设置按钮移出 tablist 至 `.nm-inspector__rail` 直下，tablist 移入新 `.nm-rail-group` 容器（Workbench.tsx:196-223, pages.css:1502-1506），roving tabindex + ArrowUp/Down/Home/End（Workbench.tsx:60-75）——**这部分正确**：activeRail 是页内状态、DOM 不重建，focus 落在真实存活的 tab 上。Reader：`←/→` window keydown 实现（typing/修饰键过滤、清理正确，Reader.tsx:27-50），F 全屏假提示删除（diff -170-177）。PrimaryNav：roving tabindex + Arrow/Home/End 结构齐全（PrimaryNav.tsx:33-49,64），**但 `moveTo` 的焦点时序缺陷使其失效**，见新问题 P1。

**P2（三项）：已修复**。`will-change: background-position` 删除（acrylic.css diff -103）；`@supports` 降级中 strong 档拆出独立规则改用 `--nm-acrylic-tint-strong`（acrylic.css:158-162，两条降级链不再打架）；`useAcrylicBudget.ts:49-51` 过滤空白 id。

## 新引入的问题

### P0（必须修）

- **[base.css:41-55]** 作用域化把 reset 特异性从 (0,0,1) 抬到 **(0,1,2)**（`html` type ×1 + `[data-view]` attr ×1 + `button` type ×1），反超所有单类 button/select 组件规则 (0,1,0)。后果（设计视图内、`data-view="design"` 存在时必然发生，特异性优先于源顺序，无 `!important` 救场）：
  - `.nm-btn` 的 border/background/padding/color/font 全部被 `base.css:50-55` 的 `border: 0; background: none; padding: 0; color: inherit; font: inherit` 压掉 → 普通「导入/新建」按钮无边框无底色无内边距；
  - `.nm-book-card`（pages.css）border/background 失效 → 书卡 meta 白字直接叠在 mica 背景上；`[data-active]` 只有 border-color (0,2,0) 胜出但 border-style/width 来自被压的基类 → **选中描边也不显示**；
  - `.nm-tab`/`.nm-chip`/`.nm-command-trigger`/`.nm-chapter`/`.nm-region`/`.nm-command__item`/`.nm-filmstrip__item` 的 padding/border/background/color 同理失效；`.nm-select` 与 `.nm-segmented button`（(0,1,1)）的 font/color 被 41-48 行的 `font: inherit; color: inherit` 压掉——`.nm-tab` 字体回退 body 14px 还顺带抵消了 P1-2 的部分成果；
  - 唯一笑存的是 (0,2,0)+ 修饰类（`.nm-btn--primary` 的 background/color），但 padding 仍丢。
  → 修法：前缀改用 **`:where(html[data-view="design"])`**（特异性归零，WebView2/Chromium 88+ 支持），如 `:where(html[data-view="design"]) button { … }`；同时给 tokens/acrylic 测试基建加一条文本断言：base.css 中所有含元素名的 reset 选择器必须以 `:where(html[data-view="design"])` 开头，防复发。

### P1（应该修）

- **[PrimaryNav.tsx:35-40]** `moveTo` 中 `onNavigate(tab.id)`（跨页面 setState，DesignPreview 条件渲染整页替换）之后**同步** `tabRefs.current[tab.id]?.focus()`——此刻 React 尚未 flush，focus 落在**旧页面**的 tab 上；随后 flush 卸载该节点，焦点被浏览器重置到 body。结果：方向键切页成功但焦点每次都丢，第二次方向键（keydown 绑在 tab button 上）收不到——roving tabindex 实际只能用一次。新增测试只断言 `data-page` 而未断言 `document.activeElement`（DesignPreview.test.tsx:176-192），故全绿。→ 修法：focus 延迟到 flush 之后（`onNavigate` 后在 effect 中 focus 新页面对应 tab，例如 PrimaryNav 挂载时若由键盘进入则 focus active tab），测试补 `expect(document.activeElement.getAttribute("data-testid")).toBe("tab-workbench")` 且断言焦点位于**新页面**的 tab。

### P2（新引入，轻微）

- **[Reader.tsx:27-50 + PrimaryNav.tsx:46]** 阅读器内的 window 级方向键监听与 PrimaryNav 的 tab 方向键叠加：React `onKeyDown` 的 `preventDefault()` 不阻止事件继续冒泡到 window，焦点在阅读器 tab 上按 ←/→ 会**同时翻页并切页**。因 Reader 随即卸载、页码状态丢弃，用户可见后果有限，但语义冲突应在 Reader 监听里排除（如 target 在 tablist 内时跳过）。

**测试是否足以锁住修复**：三条新测试分别锁住 data-view 生命周期、tab 方向键切页 + roving 属性、Reader 方向键翻页，方向正确；但两处新问题都在其盲区——jsdom 不应用样式表（P0 不可见），焦点未被断言（P1 不可见）。`tsc=0`、`vitest 486 passed` 我无法在本会话复跑（命令仍被 Plan mode 策略拦截），静态阅读与 diff 无矛盾、采信自述，但对上述两问题无证明力。

## 仍存在的 P2

- `.nm-stat__value` 20px/22px 行高 + mono 字族仍不匹配任何规格字阶档（Title 为 20/28/700 UI 字体），建议走令牌（新增数据大数字档）或回落 Caption。
- 上轮指出、本轮未在修复范围：间距硬编码 1/2/5/6px 未走 `--nm-space-*`；`.nm-shelf` 与 `.nm-mica` 背景重复定义（Shelf.tsx 同挂两类）；命令面板 `aria-modal` 无焦点圈禁、关闭后焦点不返回触发器；区块 padding 16 与规格「区块 24–32」的口径待 DSH 裁决；StatusMark.test「uses the 24x24 marker class hook」名不副实；Reader typing 过滤分支无测试。

---

**推荐下一步**：本复审报告交 DSH 处置，**不建议在当前状态合入**。P0（`:where()` 作用域化）与 P1（PrimaryNav 焦点时序 + activeElement 断言）修复成本都很小，可指派 ZCode 在同分支继续（可直接转发：「按复审报告修复 e6a80fc1e 引入的两处回归：base.css 作用域前缀改 :where(html[data-view="design"]) 并加选择器形态断言；PrimaryNav.moveTo 的 focus 延迟到跨页 flush 后并补 document.activeElement 断言；顺带处理 Reader 与 tab 方向键的事件叠加。修完在浏览器里肉眼验证设计视图按钮/书卡边框背景」——最后一句是关键，这两类问题只有真实渲染能兜住）。修复后我或另一未参与者再做一次快速复审（只需核对这两个点）。
