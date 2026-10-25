验证齐了：21 个选择器全部套入 `:where()`（grep 的 22 次含第 6 行注释一次），其他 CSS 文件无裸前缀。以下为第二次复审报告。

---

## 结论

**通过**——两处回归（特异性反超、焦点丢失）均已正确修复且带了能拦主要复发路径的守卫测试，顺带两项无新规格问题；剩余事项均为人工肉眼验证或低风险建议，不阻断合入。

## 逐点核对

**1) P0 特异性：已解决**。
- 逐条核对：上一版 21 个裸前缀选择器（`*`/`*::before`/`*::after`、html/body/#root、html 自身、body、四个表单元素、button、button:disabled、svg、::selection、:focus-visible、`*` 滚动条、三条 webkit 滚动条）与 `base.css:14-90` 的 21 个 `:where(html[data-view="design"])` 选择器**一一对应，无漏改**；grep 全部 CSS 文件确认 `html[data-view` 仅存在于 `:where(` 内，跨文件亦无裸前缀（tokens/acrylic/pages/StatusMark 零出现）。摘要所称“22 处”实为 21 个选择器 + 1 处注释（base.css:6），base.test.ts 的 `>=20` 下限计数同样把注释计入，无碍。
- 特异性：`:where()` 内部恒为 0 → 元素级 reset 回到 (0,0,1)、`*` 级回到 (0,0,0)，全部低于 `.nm-btn`/`.nm-tab`/`.nm-chip`/`.nm-book-card`/`.nm-select` 的 (0,1,0)，级联关系与最初未作用域化时等价，反压消除。WebView2（Chromium ≥88）支持 `:where()`，目标平台无兼容问题。
- html 自身那条（base.css:28）：特异性降为 (0,0,0)，`data-view="design"` 存在时仍命中（`:where` 参与匹配但不计特异性），当前 html 无任何竞争背景规则，生效无虞。
- base.test.ts 守卫评估：能拦住**主要复发路径**——行首裸前缀（正则 1）、多行选择器列表续项（正则 2 的 `\s` 跨换行，`:\n  html[` 可抓）、非 `:where`/非类开头的顶层规则（正则 3）。**存在两个盲区**（建议级，不阻断）：① 正则 1 无 `^\s*`，行首**带缩进**且不在逗号后的裸前缀（如块内独立写的 `  html[data-view…] .x {`）抓不到；② 规则提取正则 `^([^\s@/{}…)` 只匹配无缩进行，`@media` 块内带缩进的规则整体不在守卫范围（当前 @media 内只有 reduced-motion 的全局 `*` reset，属有意全局，但未来在 @media 里新增未作用域元素规则不会被拦）。修法都是一行正则的事。

**2) P1 焦点时序：已解决**。
- 旧实例不抢先消费（PrimaryNav.tsx:47-51）：页面切换时 DesignPreview 条件渲染整页替换，旧 PrimaryNav 走 unmount 而非 update，其 effect 不会再执行；只有新页面实例的挂载 effect 读到 `pendingFocusTarget === activePage` 并消费置 null。
- refs 先于 effects：React 提交阶段先跑 ref attach 再跑 passive effects，`tabRefs.current[activePage]` 在 focus 时必已填充。
- 无残留误聚焦：click 当前 tab 不走 `moveTo`（onClick 直接 onNavigate，不设标记）；键盘 `moveTo` 环形移动必然换页 → 新页面挂载 effect 必然消费并清空。仅存的理论边角是“未来某处 onNavigate 不改 activePage”时标记会滞留到下次该页激活才误聚焦一次——当前三个调用方均为直接 `setPage`，路径不存在。
- 测试断言时机可靠（DesignPreview.test.tsx:178-180）：`act()` 内 dispatch 事件，act 退出前同步 flush 包括 passive effects 在内的更新，focus 已执行；且旧树已卸载，断言的 `data-testid="tab-workbench"` 只能来自新页面 DOM——断言同时锁住了“焦点在新页面”这一语义。

**3) 顺带两项：已解决、无新规格问题**。
- Reader.tsx:40：`target instanceof Element && target.closest('[role="tablist"]')` —— window/document 目标防御正确（instanceof 覆盖 SVG 与所有元素），方向键在 tablist 内时归 tab 导航、不再叠加翻页，上一轮的 P2 叠加问题一并修掉。
- pages.css:479：`.nm-stat__value { font: var(--nm-text-title) }` = 700 20px/28px UI 字体，完整命中 Title 档，字阶合规（级联上 pages.css 后于 base.css 导入，压过 `.nm-data` 的 font shorthand，生效无疑）。一条微备注：font shorthand 重置了 `.nm-data` 的 `font-variant-numeric: tabular-nums`，统计数字从等宽 mono 变比例 UI 字体——三个静态数字左对齐展示，无可察觉影响，非规格问题。

## 新引入问题

**未发现**。（两条范围外备注，不构成本轮问题：① base.test.ts 守卫的上述两个正则盲区，属加固建议；② `tokens.css:8` 的 `:root { color-scheme: dark }` 自第一版起全局生效、未经作用域化，会把 RuntimeApp 的 UA 控件/滚动条暗色化——同属“设计层全局泄漏”家族但在本轮两修复点范围之外，且方向与 RuntimeApp 深色控制台一致，建议 DSH 下轮裁决豁免或并入 `:where` 作用域。）

## 仍需人工肉眼验证的点

1. **WebView2 真机打开 `?view=design`**：按钮边框/底色、书卡边框、胶囊、active 描边恢复显示——特异性修复的最终证明，jsdom 与 vitest 永远测不出这一类问题。
2. 键盘连续手测：方向键在三个页面间连续切换多次，焦点始终跟随当前 tab（自动化断言只覆盖了单次跳转）。
3. 浅色主题切换后 1 的同样肉眼检查（两条主题链的颜色都换了）。
4. `prefers-reduced-transparency` 与无 `backdrop-filter` 环境的降级渲染抽查（含 strong 档改 tint-strong 后的模态对比度）。
5. RuntimeApp 路径（`?view=console`/默认）在真机确认无视觉变化，尤其滚动条与表单控件（验证 `data-view` 作用域 + 上述 color-scheme 备注）。

---

**推荐下一步**：本 Task 的审查循环已收敛（初审 4×P1 → 修复引入 1×P0+1×P1 → 复审打回 → 本轮通过）。建议 DSH 做集成验证时完成上面 5 项人工肉眼检查（重点第 1、5 项），通过后即可按流程关闭 Task 并处置合入；`color-scheme` 作用域化与 base.test 正则加固可并入下一个设计层 Task，不必重开本 Task。无需其他下一步操作。
