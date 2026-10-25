# Review：UIUX-V2-RUNTIME-1（ZCode r1）

decision: changes_requested
reviewed_head: 1853f0a07
base_commit: b51d202c9

- Reviewer：ZCode（未参与本 Task 任何实现；独立只读审查 + 任命书允许的复跑与变异核验）。
- 审查日期：2026-10-25（Asia/Shanghai）。
- 审查方式：冻结 diff 全量精读（`git diff b51d202c9 1853f0a07`）、全部新增/改写源码与测试逐文件阅读、CSS 令牌逐值人工比对、tsc/vitest 独立复跑、两处变异核验（改坏→确认红/绿→原样还原）、证据截图 01/03/07 与活体截图（`localhost:5189` 默认路径与 `?view=console`）经视觉模型交叉核对。
- 范围披露（审查开始时已核实）：冻结区间除 `apps/desktop/frontend/src/**` 与 `verification/UIUX-V2-RUNTIME-1/**` 外，还包含前置治理提交 `f7e63c70c`（`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、两个 `GIT-CLEAN-RUST-*` 任务卡的 Reviewer 改派，纯治理无技术内容）。任命方 DSH 已在工作树未提交的 `APPOINTMENT.md` 修订中如实披露该事实并指示跳过；本 review 的技术结论仅针对 UI 交付提交 `1853f0a07`。工作树在审查开始时已有两处 DSH 未提交改动（`doc/tasks/UIUX-V2-RUNTIME-1.md` 新增 R6 登记与上述 APPOINTMENT 修订），本审查未触碰。

## 各轴结论

### 1. 正确性 — PASS

- 四页状态机互斥自洽：`Shelf.tsx` phase（loading/ready/empty/error）与 chaptersPhase（idle/loading/ready/error）互斥渲染（`pages/Shelf.tsx:713-767,857-898`）；`Workbench.tsx` 章节/页面/页图/区域/运行五段各自独立四态（`pages/Workbench.tsx:957-1016,1120-1300,1330-1361`）；`Reader.tsx` 用判别联合 `ReaderData`（`pages/Reader.tsx:301-320,628-712`）；`Settings.tsx` 整页 readiness 三态（`pages/Settings.tsx:224-244`）。
- Blob URL 生命周期：工作台三重回收——`replaceImageUrl` 链式回收旧 URL（`pages/Workbench.tsx:612-617`）、页图 effect cleanup 回收 `createdUrl`（`750-756`）、组件卸载兜底回收 `currentUrlRef`（`791-798`）；阅读器 effect cleanup 回收（`pages/Reader.tsx:537-540`）。切页 revoke 有测试实证（`Workbench.test.tsx:477-485`、`Reader.test.tsx:327-328`）。
- 轮询：`runPolling` 只在 run 存在且未终结时开 1s interval（`Workbench.tsx:878-890`），`runReadRef` 防重入（`814-844`），卸载 clearInterval 且卸载后不再取数有测试实证（`Workbench.test.tsx:413-421`：unmount 后 1200ms 窗口调用数不增）。
- 越界保护：阅读器 `safeIndex` 渲染前收敛（`Reader.tsx:482`）、`move`/键盘翻页双向 clamp 且章末不重复写回（`561-565,571-577`，测试 `Reader.test.tsx:331-334`）；工作台页序完全由 IPC 列表派生（`Workbench.tsx:905-909`）。换章/换页重置旧状态（`Workbench.tsx:619-622,800-812`；`Reader.tsx:389-476` 换上下文全量重置）。
- malformed 输入防御：章节/页面 `isSafeUiId` 校验，坏 ID → `PAGE_NAV_MALFORMED` 错误态而非静默渲染（`Workbench.tsx:639-645,688-692`）。

### 2. 诚实数据 — PASS（实现层）；测试守卫有缺口（见 F-1、F-2）

- fixtures 隔离：`PREVIEW_BOOKS`/`PREVIEW_CHAPTERS` 只在 `usePreviewView`（无 runtime）使用（`pages/Shelf.tsx:135-219`）；`STAGES`/`PAGES`/`REGIONS` 只在 `DesignWorkbench`（`pages/Workbench.tsx:50-84,249-468`）；Reader fixture 限 `ReaderFixture`。运行时组件树与 fixture 组件树互斥整页分发（`Workbench.tsx:1536-1539`、`Reader.tsx:45-50`、`Shelf.tsx:1080-1082`），不存在同树混渲染。
- 无来源字段处理逐一核实：书架 `volume/progress/state` 运行时为 null 且渲染条件省略（`Shelf.tsx:343-365,785-811`）、页数未知标「页数未知」（`354,375`）；工作台 OCR 文本/置信度「未识别 + 当前 IPC 未返回」、区域文本「未识别」、缩略图未知占位（`nm-wb-thumb--unknown`，不画假图案）、流水线参数只渲染 IPC 真实 provider/model/device、无 run 时不画进度条（`Workbench.tsx:1246-1326,1417-1457`）；阅读器进度未知显示「—」并标错误码、书名查不到显示「—」、webtoon_vertical 显式 PageBlocked 且不拉页图（`Reader.tsx:432-449,579-712`，测试 `Reader.test.tsx:416-475,435-462`）；设置页 sfx null = 「未设置（按 Core 默认）」、设计预览逐节显式 BLOCKED 不展示数值（`Settings.tsx:210-222,349-361`）。
- 反断言：`Workbench.test.tsx:364-382` 对 7 项 fixtures 假数据（雾港来信/manga-ocr/0.94/62%/第 12 话等）逐条 not.toContain。
- dev mock 常驻「浏览器预览 · 假数据」角标、未列出命令 `MOCK_DENIED` 拒绝（`dev/devMockBridge.ts:233-239,313-334`）。
- 缺口：书架页运行时数据纪律无任何测试（变异核验实证，见复跑记录 M-1 与 F-1）；dev mock region 数据违背冻结枚举（F-2）。

### 3. 单一 UI — PASS

- 生产窗默认只渲染 `UiRoot`：`App.tsx:529-535`（`legacyRequested ? <AppShell/> : <UiRoot/>`，AppShell 仅 `?view=legacy` 显式回退）。
- 运行时根不 import 任何历史页面容器：`ui/UiRoot.tsx:1-20` import 清单核实（只有 `pages/Shelf|Workbench|Reader|Settings` 与共享件）；源码级守卫 `ui/UiRoot.test.tsx:142-155` 用正则断言 `UiRoot.tsx` 不含 `shell/AppShell|bookshelf/BookshelfPage|workbench/WorkbenchPage|reader/ReaderPage|settings/SettingsPage`，并断言 `App.tsx` 中 AppShell 仅出现在 legacy 三元、默认分支为 `<UiRoot`。
- 冻结路径零改动：`App.tsx` 的冻结 diff 只有两个 hunk（+1 import、生产窗分支替换），probe/AC1/console 探测逻辑与 deny matrix 字节未动（`git diff b51d202c9 1853f0a07 -- src/App.tsx`）。
- 活体验证：`http://localhost:5189/?view=console` headless 截图（本次活体抽查）确认冻结控制台未被 v2 样式污染（无品牌栏/亚克力/角标，deny matrix IP-1..IP-5 照常渲染）；默认路径截图确认为 v2 书架 + 假数据角标。
- 测试：`App.test.tsx:176-178` 生产模式断言 `app-root` 存在 **且** `app-shell` 不存在。

### 4. 设计规则 — PASS（含 P3 登记项）

- 圆角：新增/改写 CSS 全部走 `--nm-radius-overlay|control|cell`（8/4/2）；`ui/ui.css`、`pages/workbench.css`、`pages/reader-settings.css` 逐条核对无字面圆角、无第 4 档值。唯一字面 `border-radius: 8px`（`pages.css:1254`，page-sheet 装饰内框）为 base 冻结既有且值在档。
- 字号：新增 CSS 全走 `--nm-text-*`（28/20/14/12）；字面小字号仅存在于封面装饰（8/9/22px，`pages.css:317-348`）与漫画页占位图案（7/11px，`pages.css:1189-1324`），属 AC1 声明的「封面与漫画页等装饰字豁免」范围。`theme/tokens.ts:35-42` 字阶全部取 28/20/14/12 内的值。
- 间距：`pages.css` 的 gap 字面值（1/2/4/5/6px）全部改走 `--nm-space-*`（冻结 diff 逐 hunk 实证，AC10）；新增 CSS 的 gap/padding/margin 全走令牌。base 既有的非 gap 字面 padding（约 21 处）与 `base.css` `.nm-chip gap:6px` 为 DESIGN-V2-IMPL-1 冻结值，本 Task 未新增，且已由 DSH 在未提交的 Task 卡修订以 R6 如实登记（建议提交该修订，见 F-6）。
- 颜色：新增三个 CSS 文件零字面色值；运行时 TSX 内联样式仅 CSS 变量引用（`--region-tone` 取自 `REGION_TYPE_TONE` 全 var 表，`Workbench.tsx:515-522`）。字面色值仅剩三类，均为 base 冻结装饰内容：封面 tint（`Shelf.tsx:83-92`，注释声明不冒充真实封面）、漫画页占位图案色（page-sheet/filmstrip-mini）、`.nm-window-btn--close:hover #FFFFFF` 与 `.nm-command-backdrop rgba(0,0,0,0.32)`（`pages.css:161-164,624`）——后两处建议后续顺手令牌化（F-5）。
- 无 emoji：组件与 CSS 逐文件核对无 emoji；七态由 `StatusMark` 三重编码（状态色类 + 几何符号 ◐●✗▲▨–○ + 文字 label，`components/StatusMark.tsx:23-32`；`showLabel=false` 时 label 走 `nm-sr-only` 供读屏）。
- backdrop-filter ≤2：三档亚克力（acrylic/acrylic-24/acrylic-strong）+ `.nm-acrylic-off` 降级（`design/acrylic.css`）；`useAcrylicBudget` 统一裁决（`design/useAcrylicBudget.ts:36-76`）；四页声明层与命令面板开启时的降级（Shelf `pages/Shelf.tsx:482-487`、Workbench `pages/Workbench.tsx:562-569`、Reader `pages/Reader.tsx:377-386`、Settings `pages/Settings.tsx:146-159`）全部有测试断言同屏 `.nm-acrylic*` 计数 ≤2（`DesignPreview.test.tsx:66,82,105,124`、`Workbench.test.tsx:357-361,468-475`、`Reader.test.tsx:309-311,386-389`、`Settings.test.tsx:277-279`）。命令面板 backdrop 本身无 backdrop-filter（`pages.css:616-625`）。
- 阴影：仅 `--nm-elevation-8/16` 两档 + focus ring（`0 0 0 Npx` 描边环，非投影）；内容面板（`.nm-state`/`.nm-stat`/`.nm-ocr-box` 等）零 box-shadow。

### 5. 令牌单一真相 — PASS

- 逐值人工比对：`theme/tokens.ts` 的 dark/light 全部色值与 `design/tokens.css` 对应变量逐字节一致（bg.app/rail/toolbar→canvas/mica/layer、surface.card、accent.primary/selected/hover、text.primary/secondary/muted/inverse、focus.ring、border.default/divider/selected；`state.favorite/archived` 是 `--nm-status-blocked/skipped` 的显式别名映射，其余五态同名直映）。间距 4/8/12/16/24 = `--nm-space-1..5`；圆角 4/8/2 = control/overlay/cell；字族栈归一化后相等。
- 守卫：`theme/tokens.test.ts` 用 23 条硬编码「TS 字段 ↔ CSS 变量」连线对 dark+light 逐值断言（`tokens.test.ts:34-89`，映射写死防命名猜测假断言），另覆盖间距/圆角/字阶四档/字族/Proxy 切换。
- 主题切换影响内联样式消费者：`tokens` 是 Proxy，顶层属性按 `activeTheme` 现取（`tokens.ts:177-194`）；`useThemeController` 渲染期同步 `setTokenTheme(theme)` 保证首帧即正确主题（`ui/theme.ts:44-46`），setter 先写令牌再触发 React 更新（`58-71`）；`<html data-theme>` 由 layout effect 同步驱动 CSS 变量层（`48-56`）。
- 模块级常量冻结（R1）：`settings/SectionField.tsx:29-63` 把 `settingsInputStyle/settingsSelectStyle` 改为「键集合固定、取值按当前主题现算」的访问器属性对象（注释说明不用 Proxy 的 ownKeys 原因），`theme/themeReactiveStyles.test.ts` 3 条直接断言常量随主题换值 + 键集稳定。这是唯一被触碰的既有 settings 文件，与 Task 声称一致。

### 6. 可访问性 — PASS

- 命令面板（`ui/CommandPalette.tsx`）：Tab 圈禁（`trapTab` 首末环绕，`113-130`）；面板 Esc + window 级 Esc 双保险（`81-87,134-137`）；`aria-activedescendant` 随高亮项更新、`role=combobox/listbox/option` + `aria-selected`（`199-243`）；关闭后焦点还原唤起元素（cleanup `isConnected` 防护，`89-95`）；开面板即聚焦输入框（effect 内同步 focus，注释说明为何不用 rAF，`69-74`）。7 条测试覆盖全通路（`CommandPalette.test.tsx:57-171`，含「焦点逃到面板外 Esc 仍生效」「Tab 从末项绕回首项」「关闭还原 opener 焦点」）。
- PrimaryNav：roving tabindex（当前页 tabIndex=0 其余 -1）、←→/Home/End 切页、跨页 pendingFocusTarget 机制（切页卸载旧页后焦点落到新页同名 tab）、点击也走焦点路径（`components/PrimaryNav.tsx:42-106`；测试 `DesignPreview.test.tsx:167-199`）。
- 设置页分节 tablist：roving tabindex + ↑↓/Home/End + 同步 focus，主题/页脚不进 tablist，tabpanel `aria-labelledby` 关联（`pages/Settings.tsx:184-206,321-348`；测试 `Settings.test.tsx:317-349`）。
- 错误面：`PageError` 为 `role="alert"` 且必显错误码（`ui/PageState.tsx:98-106`），四页全部经它呈现（测试断言 role 与 code：`Workbench.test.tsx:436-441`、`Reader.test.tsx:401-402`、`Settings.test.tsx:211-212`）。`PageLoading` 为 `role="status" aria-live="polite"`；书架浮动状态条同为 status。翻页按钮 disabled 时 aria-label/title 带原因（`Reader.tsx:596-609,813-825`）。
- 观察项：`PageEmpty` 无显式 role（F-4，非阻塞——空态文本对读屏可读，且空态非动态插入）。

### 7. 证据可核查性 — PASS（复现成功，见复跑记录）

- tsc/vitest 均已由本审查者独立复跑并复现（退出码与计数完全一致）。
- 截图核对：`shots/01`（书架深色）与 `visual-verification.md` 第 01 条一致；`shots/07`（命令面板）与第 07 条一致（含「4/5 可用」计数、当前页命令禁用并标注「已在当前页」）；`shots/03`（工作台）与第 03 条描述「显示真实区域 3 条」字面相符——但第 3 条区域行实为残缺渲染（首行类型标签缺失、色条不可见、末行 origin 空），自查未发现，见 F-2。
- NOT_RUN/HUMAN_VERIFY 如实：真实 Tauri + Python Core 端到端、WebView2 渲染差异、高 DPI 均登记为未验证（`visual-verification.md` §未验证项），Task 卡 AC12 对应行标注 NOT_RUN，未冒充通过。
- 小项：`tsc-run.txt` 首行为 `REVIEW_HEAD_PENDING` 占位标记（F-3）；活体抽查两路径（默认 + `?view=console`）与证据/冻结预期一致。

### 8. 范围合规 — PASS（含流程披露项 F-6）

- `git diff --name-status b51d202c9 1853f0a07`：技术改动全部落在 `apps/desktop/frontend/src/**`（32 文件）与 `verification/UIUX-V2-RUNTIME-1/**`（14 文件），均在 Task `allowed_paths` 内；另有前置治理提交 `f7e63c70c` 的 4 个 doc 文件（Reviewer 改派，无技术内容），DSH 已在 APPOINTMENT 未提交修订中披露并指示跳过（F-6 建议提交该修订以消除入库版范围描述与事实的偏差）。
- 零依赖改动：diff 中无 `package.json` / `package-lock.json`。无 Rust（`src-tauri`）、无 Python、无 IPC 契约/Schema 改动。
- 既有测试改动核对（冻结 diff 逐 hunk）：仅 `App.test.tsx` 与 `DesignPreview.test.tsx` 两个测试文件被修改，其余测试全为新增（A）。
  - `App.test.tsx:126-183`：生产窗断言由「AppShell 挂载 + app-nav-rail」等价迁移为「app-root 挂载 + **app-shell 不存在（新增反向断言）** + page-shelf 挂载」，`library_list_books` 包含与 `issue_resource_url` 不包含断言保留——断言密度增加，非弱化。删除的 `app-nav-rail` 断言随 AppShell 退出默认路由失效（其行为仍由保留的历史容器测试覆盖）。
  - `DesignPreview.test.tsx:180-193`：End 键落点 reader→settings 是一级导航三页扩四页的直接后果，并把按键链改为 tab-settings，新增 shelf 的 ArrowLeft 环绕断言——净增一条断言。
  - 无任何既有测试被删除；`SectionField.tsx` 是唯一被触碰的既有 settings 文件且仅为样式常量主题化。

## Findings

| id | 严重度 | 位置（文件:行） | 问题 | 依据 | 建议 |
|---|---|---|---|---|---|
| F-1 | P1 | `apps/desktop/frontend/src/pages/Shelf.tsx:356`（`progress: null`）及 `343-365` 整个 `viewBooks` 映射 | 书架页运行时「无 fixtures 回填」纪律**零测试守卫**：AC8 的字段清单明确包含「跨书进度」，四页中唯独书架没有反断言；现有测试的书架 mock 全为空列表（`UiRoot.test.tsx:20`、`App.test.tsx:151-153`），fixtures 断言只覆盖设计预览分支（`DesignPreview.test.tsx`） | 变异核验 M-1（见复跑记录）：把 `progress: null` 改为 `progress: 42`（运行时书卡将渲染假进度条 +「42%」），全量 561 条测试**全部保持绿色**，零拦截 | 补一条书架运行时测试：mock ≥1 本真实形状的书，断言书卡不渲染 `.nm-progress`/百分比/`volume`/state 标记（可并入 `UiRoot.test.tsx` 或新建 `Shelf.test.tsx`）。实现当前正确（截图 01 无假进度），属测试债而非行为缺陷 |
| F-2 | P2 | `apps/desktop/frontend/src/dev/devMockBridge.ts:126-128`；消费端 `pages/Workbench.tsx:1314-1322`；证据 `shots/03-workbench-real-data.png` | dev mock 的 `list_regions` 返回冻结闭集外的枚举值：`region_type: "dialogue"`（冻结六值闭集为 speech/narration/sfx/title/note/other，`region/types.ts:14-21`）与 `origin: "manual"`（闭集 machine/user/imported/restored，`region/types.ts:37`）。`RegionClient.listRegions` 只校验 regions 数组不校验枚举（`region/client.ts:87-92`），UI 查表（`REGION_TYPE_LABEL/TONE`、`ORIGIN_LABEL`）得 undefined → dev 预览区域行残缺：截图 03 经视觉模型核实，首行标签只剩「1」、竖直色条不可见，末行 origin 文字为空。垫片头部「只读命令返回**形状合法**的固定样例数据」（`devMockBridge.ts:14`）对 region 通道不成立；`visual-verification.md` 第 03 条未登记该缺陷。生产不受影响（Core 侧六值闭集门 + UI 对六个合法值全覆盖） | `region/types.ts:14-37` 冻结枚举；截图 03 视觉核对结论（本次审查）；`Workbench.tsx:1302-1326` 直接索引无 fallback | region-1 `region_type` 改 `"speech"`、region-3 `origin` 改 `"user"`（保留「人工改过」语义）；重截 `shots/03` 并在 `visual-verification.md` 补记本次缺陷与修复 |
| F-3 | P3 | `verification/UIUX-V2-RUNTIME-1/tsc-run.txt:1` | 证据首行为 `REVIEW_HEAD_PENDING` 占位标记：tsc 输出在 reviewed_head 确定前采集，入库为 CANONICAL 时未移除占位或披露时序（vitest-run.txt 无此问题） | 文件内容 | 后续证据模板加一行「采集时点」说明，或复跑时以实际 head 回填；本次不阻塞（命令/退出码/输出可独立复现） |
| F-4 | P3 | `apps/desktop/frontend/src/ui/PageState.tsx:66`（PageEmpty 根节点） | `PageEmpty` 无显式 role（PageLoading=status、PageError=alert、PageBlocked=status）；空态文本读屏可读且非动态插入，影响轻微 | 同文件其余三态对照 | 可选：加 `role="status"` 保持四态一致 |
| F-5 | P3 | `apps/desktop/frontend/src/pages/pages.css:161-164,624`；`pages/Shelf.tsx:83-92` | base 冻结既有的字面色值（close 悬停 `#FFFFFF`、命令面板遮罩 `rgba(0,0,0,0.32)`）与封面 tint 字面色板未走 `--nm-*`；任命轴 4 口径下无「装饰色」豁免条款（豁免只写了装饰字） | 冻结 diff 证实非本 Task 新增 | 后续令牌化或设计规范补「装饰内容色」豁免；与 R6 一并归入债务 Task |
| F-6 | P3 | `verification/UIUX-V2-RUNTIME-1/APPOINTMENT.md`（入库版第 9 行）；`doc/tasks/UIUX-V2-RUNTIME-1.md`（R6 修订） | 入库版任命书声称审查范围「全部为 frontend/src + verification」与冻结区间事实不符（含治理提交 f7e63c70c 的 4 个 doc 文件）；DSH 工作树未提交修订已修正该描述并在 Task 卡补 R6（21 处非 gap 字面间距）登记，两处修订尚未提交 | `git diff --name-status b51d202c9 1853f0a07` 与工作树 diff | 随本 review 处置一并提交这两处修订；另 `components/PrimaryNav.tsx:39-41`「当前三个调用方」注释已过时（现为四页运行时 + 设计预览共五个消费点），可顺手更新 |
| F-7 | P3 | `apps/desktop/frontend/src/pages/Reader.tsx:286-290`（对照 `134-137` 注释承诺） | 设计预览 fixture 底栏保留「Esc 返回」keyhint 但无 Esc 处理，与同文件「没实现的键不留提示」的自诫相悖。冻结 diff 证实为 base（DESIGN-V2-IMPL-1 骨架）既有、本 Task 原样保留；运行时分支无此假提示 | `git show b51d202c9:.../Reader.tsx` 第 199-204 行同内容 | 后续设计预览债务清理时移除该 keyhint 或实现 Esc |

## 复跑记录

| # | 命令（cwd=`apps/desktop/frontend`） | 结果 | 与证据比对 |
|---|---|---|---|
| R-1 | `node node_modules/typescript/bin/tsc --noEmit` | exit 0，无输出 | = `tsc-run.txt`（exit_code 0、output 空）✅ |
| R-2 | `npx vitest run --reporter=basic` | exit 0；Test Files 59 passed (59)；Tests 561 passed (561)；Duration 5.98s | = `vitest-run.txt`（59/561/exit 0）✅ |
| M-1（变异核验①） | 将 `pages/Shelf.tsx:356` 运行时 `progress: null` 改为 `progress: 42` → 先跑 `src/ui/UiRoot.test.tsx src/App.test.tsx src/pages/DesignPreview.test.tsx`，再全量 `npx vitest run` | 相关 3 文件 21 passed；全量 59 files / 561 passed 全绿、exit 0 —— **变异未被任何测试拦截** | 实证 F-1（书架诚实数据无守卫） |
| M-2（变异核验②） | 将 `ui/UiRoot.tsx:47` `initialPage = "shelf"` 改为 `"workbench"` → `npx vitest run src/ui/UiRoot.test.tsx` | 2 failed（mounts the shelf page by default…；flips the html data-theme…）/ 4 passed，exit 1 —— 守卫有效 | 证明运行时根测试有判别力 |
| M-1/M-2 还原 | 两处变异均用 Edit 原样改回（未使用 git checkout）；还原后 `git diff --stat -- src/` 为空、`git status --porcelain` 中 src 零条目；复跑 `src/ui/UiRoot.test.tsx src/pages/DesignPreview.test.tsx` | 16 passed，exit 0，恢复绿色 ✅ | 工作树 src 与 reviewed_head 逐字节一致（reviewed_head→HEAD 间仅 doc 类提交，src 零漂移，已核 `git diff --name-only 1853f0a07 HEAD`） |
| L-1（活体抽查） | `curl http://localhost:5189/` → 200；Chrome `--headless=new --window-size=1600,1000 --virtual-time-budget=6000` 截默认路径与 `?view=console`（截图存 `G:\CODEX\New Manga.workspace\UIUX-V2-RUNTIME-1\review-zcode-shots\`，仓外） | 默认路径 = v2 书架 + 黄色「浏览器预览 · 假数据」角标、书卡无假进度条（视觉模型核对）；console 路径 = 冻结控制台外观（M2-RC2 标题、IP-1..IP-5 deny matrix PASS 行、无 v2 样式/无角标） | 与 `visual-verification.md` 及冻结路径预期一致 ✅ |
| 证据截图核对 | `shots/01`、`shots/03`、`shots/07` 经视觉模型逐项核对 | 01/07 与描述逐项一致；03 与描述字面一致但暴露 F-2 的区域行残缺（描述未登记） | 见轴 7 与 F-2 |
| NOT_RUN 项 | 「临时改坏再还原」按用户授权执行（即 M-1/M-2）；除此之外未修改任何源码/测试/文档 | — | — |

## 对 AC1–AC13 的逐项判断

- **AC1 令牌单一真相 + 主题可切换 — 判定成立**。逐值比对一致 + 23 条连线守卫 + R1 修复（访问器常量 + 3 条守卫）+ 截图 02/08 佐证；本审查另做人工逐值核对（轴 5）。
- **AC2 v2 运行时根 — 判定成立**。`UiRoot` 唯一运行时根；`?view=design|legacy`、probe/AC1 语义保持（App.tsx diff 仅两 hunk，冻结路径零触碰）。
- **AC3 书架真实数据 — 判定成立（含保留）**。双数据源 + `library_list_books`/`core_ping`/`list_chapters`/`list_chapter_pages` 真实读取 + 既有对话框复用，fixtures 不退化（10 例）。保留：运行时数据纪律无测试（F-1）。
- **AC4 工作台真实数据 — 判定成立**。全链路（章节→页→资源→Blob→区域→运行投影）+ 9 例测试含反断言/轮询停/Blob revoke/malformed 防御。
- **AC5 阅读器真实数据 — 判定成立**。投影+写回+页图+翻页+章末不越界（8 例）；webtoon_vertical 显式 BLOCKED 且不拉资源（`Reader.test.tsx:435-462`）。
- **AC6 设置页 v2 — 判定成立**。12 分节挂既有真实 panel、`settings_get` 失败整页 PageError 不挂 panel（`Settings.test.tsx:205-230`）、SFX 真实状态、设计预览诚实 BLOCKED。
- **AC7 单一 UI 收口 — 判定成立**。默认路由仅 `UiRoot`；AppShell 仅 `?view=legacy`；源码级守卫 + App.test 反向断言 + 活体验证。
- **AC8 三/四态与诚实数据 — 实现成立，证据主张 PARTIAL**。四态共用 PageState、错误码必显、无来源字段省略/标未知（实现与三页测试均核实）；但 AC8 证据句「三个页面测试文件中的『无 fixtures 回填』断言」如实反映了书架不在其中——书架页无守卫（F-1，变异实证）。
- **AC9 命令面板与键盘全通路 — 判定成立**。Tab 圈禁/Esc/焦点还原/aria-activedescendant/↑↓/Home/End/Enter 全通路 + Ctrl+1..4（7 例 + UiRoot 集成 2 例）。
- **AC10 设计层债务清理 — 判定成立**。base.test 守卫自指对照（缩进/@media 盲区）；`:root` color-scheme 作用域化到 `:where(html[data-view])`（base→属性存在性泛化，活体验证 console 路径无泄漏）；`.nm-shelf`/`.nm-mica` 背景收敛；pages.css gap 全令牌化（diff 逐 hunk 实证）。
- **AC11 构建与测试 — 判定成立（本审查复现）**。tsc exit 0 无输出；vitest 59/561/exit 0，与入库证据一致。
- **AC12 真机视觉自查 — 判定成立（其自查范围内）**。11 张截图与描述核对一致（01/07 逐项、03 字面一致但见 F-2）；NOT_RUN（真实 Core 端到端）如实登记为 HUMAN_VERIFY，未冒充。
- **AC13 独立审查 — 本 review 即其交付**。判定完成后由 DSH 回填。

## 结论与放行条件

**decision: changes_requested**（0×P0；1×P1；1×P2；5×P3）。

总体评价：这是一次质量显著高于平均水准的交付——单一 UI 收口有源码级机械守卫、诚实数据纪律在实现层全面贯彻、令牌镜像有逐值连线测试、可访问性通路完整且有判别力测试、证据链可复现（tsc/vitest/截图/活体全部由本审查独立复现）、范围纪律良好（冻结路径零触碰、依赖零改动、既有测试无弱化）。变异核验 M-2 证明运行时根守卫真实有效。

不放行（changes_requested）的唯一硬性原因是 **F-1（P1）**：任命书 P1 定义「测试不足以支撑主张」——AC8 把「跨书进度」明确列入诚实字段清单并主张四页纪律，而书架页该纪律为零测试覆盖，变异核验实证 561 条测试无一拦截假进度回填。修复成本极低（一条测试），但不修复则该主张在书架页仅靠人工自查兜底。

放行条件（按 APPOINTMENT 处置规则）：

1. **必须（P1，F-1）**：补书架页运行时反 fixtures 回填测试（mock 真实形状书 ≥1 本，断言无 `.nm-progress`/百分比/volume/state 回填），通过后提交至新 head。
2. **必须（P2，F-2）**：`devMockBridge.ts` 的 region mock 枚举改合法值（`region_type`→`speech` 等、`origin`→`user`），重截 `shots/03` 并在 `visual-verification.md` 补记。
3. **建议随处置提交**：F-6 的 APPOINTMENT/R6 两处工作树修订（已由 DSH 撰写）；F-3 证据时序披露；F-4/F-5/F-7 登记为债务（可并入 R6 的后续「控件几何 + 间距令牌」Task 或设计预览清理 Task）。
4. 修复后重新定位审查（同一失败上限 2 次）：本审查者可只做增量复审（F-1/F-2 修复 + 全量复跑），无需重走全部八轴。
5. 真实 Tauri + Python Core 端到端维持 HUMAN_VERIFY 不变，不因本 review 解除。
