# 04 旧主题/令牌现状与技术约束（LEGACY 事实清单）

> **文档性质**：只读事实记录。回答两个问题：① 旧界面的视觉令牌体系到底是什么、哪些**明确不得沿用**；② 新设计能被允许做什么、绝对不能做什么（技术边界）。
> 本文**不提出视觉方案**，只交付约束与自由度。任何视觉决策属于 Lead。
>
> **证据基准**：`G:\CODEX\New Manga`，branch `main`，HEAD `65d9efa191c6867243bf67aced54fd89308838b7`。`file:line` 相对仓库根目录。
> 未能实证的一律标 `UNVERIFIED`。

---

## 1. 现有主题与令牌现状

### 1.1 结构：一个 80 行的 TS 常量对象

令牌全部定义在一个文件里：`apps/desktop/frontend/src/theme/tokens.ts:5-80`，结构为 5 组：

| 组 | 行 | 内容 |
|---|---|---|
| `color` | `:6-44` | `bg`(app/rail/toolbar 3)、`surface`(card/border 2)、`accent`(primary/selected/hover 3)、`text`(primary/secondary/muted/inverse 4)、`state`(favorite/archived/running/completed/failed/skipped/blocked 7)、`focus.ring`(1)、`border`(default/divider/selected 3) |
| `typography` | `:45-57` | `fontFamily`（`system-ui, "Segoe UI", "Microsoft YaHei UI", sans-serif`）、`monospace`；`size` 6 档（badge 10 / secondary 11 / monospace 12 / base 13 / cardTitle 14 / panelTitle 18）；`lineHeight: 1.5` |
| `spacing` | `:58-64` | xs 4 / sm 8 / md 12 / lg 16 / xl 24 |
| `radius` | `:65-69` | button 4 / card 6 / pill 9999 |
| `dimensions` | `:70-79` | minAppWidth 1024 / minAppHeight 680 / railWidth 64 / bookshelfToolbarHeight 48 / bookDetailPanelWidth 320 / cardGridWidth 168 / cardGridHeight 210 / chapterRowHeight 32 |

**没有的维度**（这就是"不得沿用"的根源）：无暗色模式（无 `modes`/`theme` 键）、无 elevation/shadow 标尺（阴影全是散落字面量，例 `CreateTitleDialog.tsx:86`、`BookGrid` 无）、无 z-index 标尺、无 motion/duration/easing、无 density/紧凑模式、无 font-weight 标尺、无 border-width、无 opacity 标尺、无可视密度断点、无高 DPI 相关量。

**已有但从未使用的令牌（死令牌）**：

| 令牌 | 使用次数 | 证据 |
|---|---|---|
| `tokens.color.focus.ring` | **0** | 全仓 grep；而 `outline: "none"` 有 10 处（见 03 文档 KB-03） |
| `tokens.color.accent.hover` | **0** | 同上（悬浮态无令牌化实现） |
| `tokens.color.border.selected` | **0** | 同上 |
| `tokens.color.state.running` | **0** | 同上 |

### 1.2 是否 DTCG：**不是**

- `tokens.ts` 是 TypeScript `const ... as const`（`tokens.ts:5,80`），只能被 TS 组件 `import`，不能导出为设计工具可消费的格式，也没有 `$value`/`$type` 结构。
- `doc/design/` 下另有 6 份候选令牌 JSON（`tokens-cand-a.json` … `tokens-cand-f.json`，各约 4.4 KB）与 `ui-reference.html`（116 KB）。它们是**自定义 schema**（顶层 `geometry`/`modes.dark.color`/`modes.light.color`/`glass_material`），同样不是 DTCG。
- 候选 F（`doc/design/tokens-cand-f.json:1-20`）是本轮 e2e 对比度的映射基准（`e2e/p02-new-time/ac6-contrast.mjs:37` 读取该文件），但**运行时完全没有接入**：AC6 明确记录 `UNMAPPED: "inline React runtime colors; F token system not wired into this surface"`（`e2e/p02-new-time/ac6-contrast.mjs:362`）。
- 候选 F 的 `--st-warn` / `--warn-soft` / `--skip-soft` 等键名与旧代码里的 CSS 变量 fallback 同名（`tokens-cand-f.json` 的 `st-warn`、`warn-soft`、`skip-soft` vs `region/RegionOverlay.tsx:44-48`），说明曾计划把 F 令牌落为 CSS 变量，**但变量从未定义**：全仓无 `:root`、无 `setProperty`。

### 1.3 视觉落地方式：内联样式，没有样式表层

| 事实 | 数值 / 证据 |
|---|---|
| `.css` / `.scss` 文件 | **0 个**（`apps/desktop/frontend` 全树） |
| CSS 变量定义 | **0 处**（无 `:root`、无 `setProperty`）；只有 10 处 `var(--x, fallback)` 引用，永远命中 fallback（`RegionOverlay.tsx:42-48`、`RegionInspector.tsx:228,299`、`RelabelConfirmDialog.tsx:22`） |
| 内联 `style={{…}}` | **710 处**（非测试 tsx） |
| `tokens.*` 引用 | 1254 处（说明令牌在用，但只是"内联时读常量"） |
| 硬编码 hex 颜色 | **280 处** |
| `font-size` 字面量档位 | **15 档**（10/11/12/13/14/15/16/18/20/24/30/32/36/40/48） |
| `z-index` 档位 | **12 档**：2、4、5、10、15、20、30、40、1000(×4)、1500、2000、9999 —— 见下表 |
| `data-testid` 属性 | **512 处**（UI 结构与测试选择器高度耦合） |
| `aria-*` / `role=` | 68 / 32 处 |

z-index 现状（同一层级语义被不同数值表达，且遮罩互相压盖）：

| z-index | 使用者 | 证据 |
|---|---|---|
| 2 / 4 / 5 | 阅读器页图、左右翻页热区、徽标 | `PagedReaderView.tsx:118,107,149`；`ReaderPageImage.tsx:130` |
| 10 / 15 / 20 | 阅读器工具栏 / 工作台反馈条 / 右键菜单与任务详情弹层 | `ReaderToolbar.tsx:54`；`ViewerPanel.tsx:279`；`RelabelContextMenu.tsx:71`、`TaskProgressPanel.tsx:141` |
| 30 / 40 | 改标确认 / 修订恢复确认 | `RelabelConfirmDialog.tsx:49`；`RegionInspector.tsx:279` |
| 1000 | 新建对话框、导入对话框、导出对话框、Core 状态横幅（四者同层） | `CreateTitleDialog.tsx:72`；`ImportDialog.tsx:141`；`ExportDialog.tsx:68`；`AppShell.tsx:362` |
| 1500 / 2000 | 回收站模态 / 永久删除确认 | `BookshelfPage.tsx:415`；`PermanentDeleteConfirmDialog.tsx:53` |
| 9999 | FPS 采样浮层 | `perf/FpsRecorderPanel.tsx:200` |

### 1.4 暗色/亮色事实

- 主应用是**亮色单主题**：`bg.app = #f5f5f4`、`text.primary = #1f2328`（`tokens.ts:8,22`）。
- 同一构建里存在**暗色孤岛**：遗留 Console 的 `LibraryPanel` / `SettingsPanel` 使用 GitHub 暗色板（`#161b22` 面板、`#0d1117` 输入框、`#e6edf3` 文本）——`library/LibraryPanel.tsx:48-54,133-136`、`settings/SettingsPanel.tsx:100-110,170-177`。
- 工作台页自身在根节点重复写死了亮色值而非引用令牌：`background: "#f5f5f4", color: "#1f2328", fontFamily: 'system-ui, "Segoe UI", "Microsoft YaHei UI", sans-serif'`（`workbench/WorkbenchPage.tsx:1190-1192`），与 `tokens.ts:8,22,46` 三处重复定义。
- 无主题切换控件：`e2e/p02-new-time/ac6-contrast.mjs:378-383` 记录 `light_theme.entry_point_present: false` 且状态 `NOT_APPLICABLE (no light theme entry in the React app)`（该记录针对 Console 表面）。
- 无 `prefers-color-scheme` / `prefers-reduced-motion` 查询代码（全仓 0 处）。

### 1.5 「明确不得沿用」清单

> 以下每一条都是旧实现的既定事实，新设计**不得**把它当作起点或默认值。

| # | 不得沿用 | 依据 |
|---|---|---|
| N-01 | `src/theme/tokens.ts` 的取值本身（`#f5f5f4`/`#4f6bed`/`#ececea` 等 6 组常量） | `tokens.ts:5-80`；它们是为"四页 QML 映射"临时定的浅色基线，没有任何对比度验证记录 |
| N-02 | 8 档硬编码 `font-size` 体系（10/11/12/13/14…）与 `lineHeight: 1.5` 单一值 | `tokens.ts:48-56`；10–11px 正文化已构成可读性缺陷（03-C ID-04） |
| N-03 | `spacing` 5 档（4/8/12/16/24）+ `radius` 3 档（4/6/9999）作为完整尺度 | `tokens.ts:58-69`；实际代码里又出现 6/8/2/3/5/20/40 等十余个散落值 |
| N-04 | 固定像素尺寸常量：`railWidth 64` / `bookDetailPanelWidth 320` / `cardGridWidth 168` / `cardGridHeight 210` / `chapterRowHeight 32` / `minAppWidth 1024` / `minAppHeight 680` | `tokens.ts:70-79`；这些数值把"布局"写成了常量，新 IA 无法在其上成立 |
| N-05 | emoji 图标（📚🛠️📖⚙️🗑️📄📁⌛⚠️🔒 等 25 处）与文本符号混用（★☆⊞☰✕−＋） | `AppShell.tsx:218,249,281,311`；`BookshelfToolbar.tsx:105,156,253,272` |
| N-06 | 内联 `style` 作为唯一落样式手段（710 处） | 全仓无 CSS 文件；内联样式无法表达 `:hover`/`:focus-visible`/`::selection`/媒体查询/容器查询 |
| N-07 | 12 档 z-index 与"模态=1000/1500/2000"的隐式约定 | 见 §1.3 表；`AppShell.tsx:362` 的健康横幅与对话框并列 1000 已实际产生压盖竞争 |
| N-08 | GitHub 暗色板（`#161b22`/`#0d1117`/`#e6edf3`）作为暗色方案 | `LibraryPanel.tsx:48-54`；`SettingsPanel.tsx:100-110` |
| N-09 | `var(--…)` + 未定义变量 + 硬编码 fallback 的三层写法 | `RegionOverlay.tsx:42-48`；`RegionInspector.tsx:228,299`；`RelabelConfirmDialog.tsx:22` |
| N-10 | "暗色 fallback 落在亮色背景"的组合（区域框 `#7aa2c8`、警告 `#fbbf24` 直接画在 `#f5f5f4` 上） | 同上 + `tokens.ts:8` |
| N-11 | 以 `title` 属性承载解释/提示的交互惯例 | 03-C A11Y-04、D-14 |
| N-12 | "禁用按钮 + 常显原因小字"的 `DisabledFeature` 形态（12 处，且暴露 `GAP-G7` 一类编号） | `workbench/DisabledFeature.tsx:1-22`；`BookDetailPanel.tsx:230,249` |
| N-13 | 四页 64px 图标 rail + 常驻四页 keep-alive 的布局骨架 | `AppShell.tsx:162-314,376-436` |
| N-14 | 分栏尺寸（240 页面列 / 320 Inspector 列 / 220 进度条带 / 480/520/560/900 的对话框宽度） | `PageListPanel.tsx:116-119`；`WorkbenchPage.tsx:1263`；`TaskProgressPanel.tsx:78`；`ImportDialog.tsx:149`；`ExportDialog.tsx:69`；`BookshelfPage.tsx:426` |
| N-15 | 候选令牌 a–f 的任何一套取值（含候选 F）作为"既定方向" | 6 份候选共存且均未接入运行时（`e2e/.../ac6-contrast.mjs:362`）；方向由 Lead 裁决，**不是事实** |

---

## 2. 技术约束

### 2.1 运行时与语言栈

| 事实 | 值 | 证据 |
|---|---|---|
| React | `18.3.1`（`react` / `react-dom`） | `apps/desktop/frontend/package.json:11-13` |
| 挂载方式 | `react-dom/client` `createRoot(...).render(...)`，**无 `<StrictMode>`** | `src/main.tsx:1,22-27`；注释 `main.tsx:7`：`// No StrictMode: the ?probe=1 evidence matrix must execute exactly once.` |
| 语言/编译 | TypeScript `^5.9.3`，`strict: true`，另有 `noUnusedLocals` / `noUnusedParameters` / `noFallthroughCasesInSwitch`，`jsx: react-jsx`，`target/lib ES2021` | `apps/desktop/frontend/tsconfig.json:1-22` |
| 运行时依赖总量 | **3 个**：`@tauri-apps/api ^2.0.0`、`react`、`react-dom` | `package.json:10-14` |
| 路由库 | **无**（无 react-router / wouter 等）→ 导航靠 `useState<PageId>` | `package.json:10-14`；`shell/AppShell.tsx:19` |
| 状态管理库 | **无**（无 redux/zustand/jotai/mobx）→ 全靠 props/局部 state | `package.json:10-14` |
| UI 组件库 / 样式方案 | **无**（无 Tailwind/Radix/MUI/CSS-in-JS/styled-components）→ 手写内联样式 | `package.json:10-14`；710 处 `style={{` |
| Lint / Format | **无配置文件**（仓库内无 `.eslintrc*` / `eslint.config.*` / `.prettierrc*`） | 全仓查找结果为空 |
| `@tauri-apps/api` 实际使用 | 仅一处动态 import 作为事件桥 fallback：`await import("@tauri-apps/api/event")` | `src/events.ts:90-92`；主通道是 `window.__TAURI__.core.invoke`（`withGlobalTauri: true`） |

**含义**：新设计若要引入设计系统库/样式方案/路由/状态库，等于**新增依赖**，属于需要 Lead 明确授权的范围变更（依赖面属于共享契约的一部分，见 `AGENTS.md` 的"修改共享接口、Schema、依赖…先在 Task 中由 DSH 明确范围"）。

### 2.2 构建链

| 事实 | 值 | 证据 |
|---|---|---|
| 构建命令 | `tsc && vite build`（类型检查失败即构建失败） | `package.json:7` |
| 打包器 | Vite `^5.4.0` + `@vitejs/plugin-react ^4.3.0` | `package.json:18-19` |
| 产物 | `outDir: "dist"`，`target: "es2021"` | `vite.config.ts:5-10` |
| dev server | 端口 `5188`，`strictPort: true` | `vite.config.ts:7` |
| Tauri 装配 | `frontendDist: "../frontend/dist"` | `apps/desktop/src-tauri/tauri.conf.json:6-8` |
| 入口 HTML | 单个 `index.html`，无任何样式表/字体链接，`<html lang="en">` | `apps/desktop/frontend/index.html:1-10` |

### 2.3 测试栈

| 事实 | 值 | 证据 |
|---|---|---|
| 测试框架 | vitest `^2.0.0`，命令 `vitest run` | `package.json:8,20` |
| 环境 | **默认 node 环境**；仓库内无 `vitest.config.*`、无 `setupFiles`、无 `environment: jsdom` 配置 | `apps/desktop/frontend/` 文件清单（只有 `index.html` / `package*.json` / `tsconfig.json` / `vite.config.ts`） |
| DOM 模拟 | 每个测试文件自己 `new JSDOM(...)` + `vi.stubGlobal("window"…)`；或使用手写 `testSupport/mockDom.ts`（`MockNode`/`MockElement`，明确"Event dispatch is NOT simulated"） | `shell/AppShell.test.tsx:1-30`；`testSupport/mockDom.ts:1-11` |
| 规模 | 45 个测试文件 / 11,791 行（对比非测试 81 文件 / 19,913 行） | 统计 |
| 组件测试能力 | 无 `@testing-library/*`、无 `user-event`、无 `happy-dom`；交互覆盖靠"client 层 invoke 参数断言" | `testSupport/mockDom.ts:9-10`；`package.json` devDeps |
| 浏览器级测试 | Node ≥22 脚本 + CDP，驱动**固定 packaged EXE**（见 §2.7） | `e2e/p02-new-time/README.md:1-4` |

**含义**：新交互（拖拽、右键菜单、焦点陷阱、虚拟化）**没有现成测试基础设施**；构件级测试只能验证"渲染出了什么字符串/DOM 属性"，真实交互必须走 CDP e2e（需要打包产物）。

### 2.4 IPC 客户端封装与错误模型

**通道**：`window.__TAURI__.core.invoke(command, args)`（`withGlobalTauri: true`，`tauri.conf.json:5`）。前端不直接 import `@tauri-apps/api/core`。

**封装形态**：按业务域各写一个 class，构造时接收可注入的 `invoke`，每个方法单独做一次形状校验再返回：

| Client | 文件:行 | 命令数 | 备注 |
|---|---|---|---|
| `LibraryClient` | `library/client.ts:95-413` | 11 | 书籍/章节/页面导航/导入/永久删除 |
| `ReaderClient` | `reader/client.ts:42-124` | 2 | 阅读投影、阅读进度 |
| `RegionClient` | `region/client.ts:41-213` | 5（`list_regions:82`/`set_region_type:109`/`list_region_revisions:141`/`restore_region_revision:164`/`rerender_page:188`） | 由 `WorkbenchPage` 注入 |
| `WorkbenchClient` | `workbench/client.ts:211+` | 10（Run 6 + 导出 4） | 含幂等键 `newIdempotencyKey()`（`client.ts:92-97`，`crypto.randomUUID()`，不可用即 `IDEMPOTENCY_KEY_UNAVAILABLE`） |
| `SettingsClient` | `settings/client.ts:596+` | 40+ | Provider/网络/凭据/备份/清理/插件 |
| `ResourceChannelClient` | `resourceChannel/client.ts:48-102` | 2（`issue_resource_url` / `revoke_ref`） | fetch 走 `http://m2res.localhost` |

**错误模型（五套并行，无统一基类）**：

| 类 | 文件:行 | 携带字段 |
|---|---|---|
| `TypedChannelError` | `resourceChannel/client.ts:21-27` | `code`（如 `REF_UNKNOWN_ID` / `REF_REVOKED` / `REF_EXPIRED` / `RESOURCE_TOO_LARGE`） |
| `LibraryClientError` | `library/client.ts:27-45` | `code` + `details`（批量删除的 per-item `items`） |
| `ReaderClientError` | `reader/client.ts:29-37` | `code` |
| `WorkbenchClientError` | `workbench/client.ts:66-72` | `code` |
| `SettingsClientError` | `settings/client.ts:143+` | `code` |

**错误 → 文案的唯一映射入口**：`bookshelf/error.ts:148-187` `parseSemanticError()`，按 `code` 查 22 项 `KNOWN_CODE_MAP`（`error.ts:15-144`），未知码降级为 `系统报告代码：${code}`（`error.ts:180-186`）。设置域另有闭集投影 `settings/errors.ts`（`SettingsSurfaceError`：`category/phase/action/message_key`，`SettingsErrorBar.tsx:15-73` 是它唯一的出口）。工作台另有 `safeWorkbenchErrorCode()`（`workbench/client.ts:85-90`，白名单正则 `SAFE_ERROR_CODE`）。

**约束**：新 UI 的每条错误展示都必须最终落在这套 code→文案映射上（或扩展它）；**不得**直接渲染后端 `message` 文本（多处注释明令禁止：`bookshelf/error.ts:2-4`、`settings/SettingsErrorBar.tsx:9-14`）。

**事件面（推送通道）只有 7 个**，且语义是"失效提示，必须再查快照"：

| 事件名 | 载荷 | 证据 |
|---|---|---|
| `core:TaskFailed` | `run_id/task_id/page_id?/error_code?` | `events.ts:53-56,116-121` |
| `core:RunPaused` | `run_id/status` | `events.ts:123-128` |
| `core:RunCompleted` | `run_id/status` | `events.ts:130-135` |
| `core:CurrentPageStepChanged` | `run_id/current_page_id?/current_step_type` | `events.ts:137-142` |
| `core:ExportProgressChanged` | `export_id/status/completed_pages/total_pages` | `events.ts:144-149` |
| `core:ReadingProgressChanged` | `book_id/chapter_id/mode` | `events.ts:151-156` |
| `core:lifecycle_status` | `status/message` | `events.ts:62,158-163` |

**不存在的事件**（新设计不能假设有推送）：书籍/章节/页面增删改、Region 变更、设置变更、插件变更、备份/清理进度、导入进度。→ 跨页数据一致性目前只能靠"重新拉取"（03 文档 IA-07）。

### 2.5 Tauri 能力与权限（硬边界）

| 事实 | 值 | 证据 |
|---|---|---|
| 生产命令面 | **66 条**（`PRODUCTION_COMMANDS`） | `apps/desktop/src-tauri/src/main.rs:70-165` |
| 测试/证据命令面 | probe 4 条 + AC1 3 条，仅对应启动环境下注册 | `main.rs:170-175,186,321+` |
| ACL 允许清单 | 73 条 `allow-*` + `core:event:allow-listen` / `allow-unlisten`，**仅 `windows: ["main"]`** | `capabilities/m2rc1-commands.json:1-90` |
| **没有的能力** | 无 `dialog:*`、无 `opener:*`、无 `fs:*`、无 `shell:*`、无 `http:*` 权限 | 同上（permissions 列表中不存在） |
| 原生文件/文件夹选择器 | 由 Rust 在命令内部 `blocking_pick_files()` / `blocking_pick_folder()` 启动；WebView 只传 `chapterId` + `duplicatePolicy` | `main.rs:1197-1203`（文件，多选）、`main.rs:1226`（文件夹）；前端 `library/client.ts:264-317` |
| 打开文件夹 | 只有两条命令：`library_reveal_export_folder`、`plugins_open_directory`（Rust 侧 `opener().open_path`） | `main.rs:156-157,104`；`main.rs:1303-1304`、`main.rs:829-830` |
| CSP | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: http://m2res.localhost; connect-src 'self' ipc: http://ipc.localhost http://m2res.localhost; font-src 'self'` | `tauri.conf.json:16-18` |
| 自定义协议 | `assetProtocol.enable: false`（不能用 `asset://`） | `tauri.conf.json:19-22` |
| Rust 插件依赖 | `tauri-plugin-dialog = "2"`、`tauri-plugin-opener = "2"` 已在 Rust 侧注册并只由 Rust 使用（`DialogExt` / `OpenerExt`）；**前端 permission 未开放 `dialog:*`/`opener:*`** | `apps/desktop/src-tauri/Cargo.toml:15-16`；`main.rs:65-66,1737-1738`；`capabilities/m2rc1-commands.json:8-90` |
| 前端访问数据库 / 任意路径 / 模型 | **不可能**：无 fs/shell 权限、无 SQLite 依赖、无 HTTP 出站权限；一切经 RC/Core | 同上 + `AGENTS.md`（"React/WebView 不直接访问数据库、任意 OS 路径或模型"） |

**CSP 的具体后果（设计必须遵守）**：
- 只能加载**同源资源**与 `blob:` 图片 + `http://m2res.localhost` 图片；`font-src 'self'` → **不能用 Google Fonts / 任何网络字体**，只能用系统字体或随包字体文件。
- `connect-src` 不含任意 https 域名 → **不能直连任何第三方 API**（LLM、翻译服务都不行）。
- `style-src 'self' 'unsafe-inline'` → 内联样式仍可用（这也是现状 710 处内联样式能工作的原因），但**外部 CSS 必须同源**（放在 `dist` 内可通过；新增 CSS 文件是允许的，属构建内资源）。
- `script-src 'self'` → 无 CDN 脚本、无内联 `<script>` 执行（`eval`/`new Function` 也受限）。

### 2.6 图片资源通道（大图唯一合法路径）

```
resolve_page_resource(pageId) → {resource_id, revision}          # library/client.ts:184-203
  → issue_resource_url(resourceId, revision) → {url, size, opaque_id}   # resourceChannel/client.ts:57-66
  → fetch(`${url}?chunk=n`)  逐块，每块 ≤ 16 MiB                  # resourceChannel/client.ts:13,81-101
  → 组装 Blob → URL.createObjectURL(blob) → <img src=...>         # workbench/pageImage.ts:15-27
```

| 约束 | 值 | 证据 |
|---|---|---|
| 单块上限 | `CHUNK_SIZE = 16 * 1024 * 1024`（16 MiB） | `resourceChannel/client.ts:13` |
| 单资源上限 | 256 MiB（超出即 `RESOURCE_TOO_LARGE`） | `bookshelf/error.ts:126-131`；`App.tsx:332-348`（256 MiB 边界场景 E-08） |
| 可见面 | 只有"不透明协议 URL + 展示尺寸"；**无路径、无 digest、无 revision 指纹** | `resourceChannel/client.ts:1-11` |
| 引用生命周期 | 每次 issue 生成新 opaque 引用；有 TTL；可 `revoke_ref`；过期/撤销后 fetch 返回 typed code | `resourceChannel/client.ts:56-70`；`App.tsx:265-296` |
| 生产代码从不主动 revoke | 仅 probe 场景调用（`App.tsx:274`） | 03 文档 B.2 |
| 无缓存/预热机制 | 每页每次重新 issue + 全量取 | `ReaderPageImage.tsx:49-105` |
| objectURL 生命周期 | 由组件手动 `revokeObjectURL`；工作台用 `imageUrlRef` 做"换 url 即 revoke"，卸载时 revoke | `workbench/pageImage.ts:26`；`WorkbenchPage.tsx:231-236,778-787`；`ReaderPageImage.tsx:99-104` |

**结论**：新设计可以任意设计图片呈现（缩放、并排、缩略图布局），但**必须**走 `resolve_page_resource → issue → chunk → blob` 这条链；`<img src>` 不能指向文件路径、不能指向 http(s) 外网；加载必须自己实现分块进度（通道给了 `onProgress(loadedChunks,totalChunks)`，`pageImage.ts:19`）。

### 2.7 既有可访问性/交互测试基线（已承诺过的契约）

这些是**已经写进验收脚本的承诺**，新设计要么满足，要么由 Lead 显式废止。

| AC | 覆盖内容 | 关键判据 | 证据 |
|---|---|---|---|
| AC1 | 运行时身份（进程/窗口/WebView2/OS/allowlist 公告）+ 截图 | 真实 IPC | `e2e/p02-new-time/README.md:8` |
| AC2 | **真实鼠标/键盘导航** Workbench + 按钮状态 | 真实 IPC | `README.md:9` |
| AC3 | **300ms 静默期**、切页取消、迟到响应 | 页面内 `performance.now()` 单调时钟；不使用 fake timer | `README.md:10,30-32`；`ac3-debounce.mjs` |
| AC4 | retype / undo / restore **写后即时 readback** | `REAL_WEBVIEW_MOCK_IPC` | `README.md:11` |
| AC5 | **Tab / Shift+Tab / Enter / Space / Escape 与焦点** | 每一步都抓焦点位置 | `README.md:12`；`ac5-keyboard.mjs:4-6` |
| AC6 | **computed color + WCAG 对比度 + F 令牌映射** | 文本 ≥ **4.5:1**，禁用/非文本 ≥ **3.0:1**；底色按 Porter-Duff 逐层合成到不透明祖先；无法解析记 `NOT_VERIFIABLE` 而非判过 | `ac6-contrast.mjs:11-16,206-219,364-369` |

运行方式（决定了"改了 UI 之后怎么证明没退化"）：

- 必须驱动**固定 packaged EXE**（`PINNED_EXE` + `PINNED_EXE_SHA256` + `SOURCE_BASELINE_COMMIT` 三个值都从 `lib/env.mjs` 读取）→ `ac6-contrast.mjs:21-32`。
- 通过 `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port=9333` 走 CDP → `README.md:3`。
- 所有可写路径隔离到 `G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-AC1-AC7/run-r1/<scenario>/`，且启动前断言目录为空 → `README.md:3,26-28`。
- 逐场景标注 mock 层（`NONE` / `REAL_WEBVIEW_MOCK_IPC`），不得混称 → `README.md:18-22`。

**含义**：新 UI 的 e2e 验收需要"打包可执行 + 固定 SHA + CDP 端口 + 干净场景目录"这套较重的基础设施；`apps/desktop/frontend/e2e/workbench_driver_protocol.ts:1-8` 另有一份 Stage A 数据契约（含 `ContrastSample`/`ScenarioVerdict` 类型），其自身注明"Stage A 未启用真实 CDP 驱动"。

### 2.8 窗口与高 DPI 事实

| 事实 | 值 | 证据 |
|---|---|---|
| 窗口标题 | `M2-RC1 resource channel runtime`（写死在配置里） | `tauri.conf.json:11` |
| 实际窗口尺寸 | `1180 × 860`，**无 `minWidth`/`minHeight`/`theme`/`decorations`/`transparent`/`zoomHotkeysEnabled` 等任何扩展字段** | `tauri.conf.json:8-14` |
| 最小尺寸 | 只靠 CSS：`minWidth: 1024` / `minHeight: 680`（`tokens.ts:71-72` → `AppShell.tsx:153-154`）；`overflow: hidden`（`AppShell.tsx:158`） | 同上 |
| Rust 侧窗口构造 | **完全没有** `WebviewWindowBuilder`/`WindowBuilder` 调用（全仓 grep 0 处）→ 窗口的一切来自 `tauri.conf.json` | `apps/desktop/src-tauri/src/main.rs` 全文 |
| DPI/缩放处理 | **0 处理**：无 `devicePixelRatio`、无 `scaleFactor`、无 `image-rendering`、无缩放感知布局 | 全仓 grep 0 处 |
| 双屏 | 无任何多显示器/窗口位置持久化代码 | 同上 |
| 打包 | NSIS 安装包（`bundle.targets: ["nsis"]`），sidecar 资源 `core-sidecar` | `tauri.conf.json:24-33` |

**含义**：`1024×680` 是"内容被裁切的下限"，不是"可用的最小尺寸"；任何新布局的密度假设必须先确认在 200% 缩放 + 1024 逻辑宽度下的可用性（当前代码**没有任何缩放适配机制**，`UNVERIFIED` 实机表现）。

### 2.9 其他会影响设计的既成事实

| 事实 | 影响 | 证据 |
|---|---|---|
| 512 个 `data-testid` 遍布生产组件 | 现有测试（含 e2e）大量按 testid 定位；重构 UI 会连带打断测试选择器 | 统计；例 `PageListPanel.tsx:132,144,169,219` |
| 无路由：导航只是 `useState` | 无法深链、无法恢复会话、无法"返回" | `AppShell.tsx:19,132-144` |
| 无 StrictMode | 开发期检测不到"effect 双执行/未清理副作用"类问题；新设计若依赖 StrictMode 校验不会生效 | `main.tsx:7` |
| `document.title` 被运行时改写 | 任何依赖标题的功能（任务栏、截图证据）都会看到 `M2RC1|...` | `App.tsx:99,144-146` |
| 事件桥是"失效提示"语义 | 不允许把事件载荷当状态真相；收到就必须重新查询 | `events.ts:5-9` |
| 幂等键必须由前端生成 | 启动 Run / 重试等写操作需要 `crypto.randomUUID()`；缺失即抛 `IDEMPOTENCY_KEY_UNAVAILABLE` | `workbench/client.ts:92-97` |
| 凭据永不进 WebView | 不能设计"密码输入框"；只能设计"配置/替换/清除 + 原生弹窗收集" | `settings/CredentialField.tsx:8-15,125-126` |

---

## 3. 新设计的自由度与硬约束

### 3.1 可以做（技术上是自由的）

| # | 自由项 | 说明/依据 |
|---|---|---|
| F-01 | 完全重写视觉层与令牌体系 | 令牌只被组件 `import` 使用，无外部消费者；可换 DTCG/JSON/CSS 变量任一形态 |
| F-02 | 引入 CSS 文件 / CSS 变量 / CSS Modules | CSP 允许同源样式；`style-src 'self' 'unsafe-inline'`（`tauri.conf.json:16-18`） |
| F-03 | 用系统字体或随包字体文件 | `font-src 'self'`（不可用网络字体） |
| F-04 | 任意 IA / 导航模型 / 命令面板 / 多窗格 / 并排对照 | 前端无路由/状态库，是"从零搭"的自由，不是约束 |
| F-05 | 任意图片呈现（缩放、并排、缩略图、裁剪） | 只要走 `resolve_page_resource → issue → chunk → blob`（§2.6） |
| F-06 | 任意进度/状态表达 | 有 Run 快照/任务投影/导出快照三套读接口 + 7 个事件 |
| F-07 | 任意错误交互形态 | 只要最终仍走 `code → 文案` 映射（§2.4） |
| F-08 | 引入虚拟化/图表/编辑器等纯前端库 | 属新增依赖，需 Lead 授权（`AGENTS.md` 依赖条款） |
| F-09 | 深色/浅色双主题 | 技术上无障碍；注意 AC6 的 4.5:1/3.0:1 阈值是已承诺基线 |
| F-10 | 键盘优先（命令面板、快捷键表、焦点管理） | 现状已有 AC5"键盘/焦点"验收先例，扩展它是顺向的 |

### 3.2 不能做（硬约束）

| # | 禁区 | 依据 |
|---|---|---|
| H-01 | 直接读写 SQLite / 文件系统 / 任意 OS 路径 | 无 `fs`/`shell` 权限；`capabilities/m2rc1-commands.json:12-90`；`AGENTS.md` |
| H-02 | 直接调用模型 / 直连第三方 API / 下载网络字体 | CSP `connect-src` 与 `font-src` 限制（`tauri.conf.json:16-18`） |
| H-03 | 自己弹原生文件/文件夹选择器 | 无 `dialog:*` 权限；只能走 `library_import_file|folder`（`main.rs:145-147`） |
| H-04 | 用 `asset://` 或任意路径直接 `<img src>` 大图 | `assetProtocol.enable: false`；`img-src` 只允许 `self`/`blob:`/`m2res.localhost` |
| H-05 | 假设存在列表变更推送（书籍/章节/Region/设置） | 事件面只有 7 个（§2.4） |
| H-06 | 显示真实文件路径、opaque 引用、sha256 之外的内部标识作为用户信息 | `resourceChannel/client.ts:1-11`；`reader/types.ts:5-9`；导出历史里的 `sha256` 也应视为开发者信息 |
| H-07 | 设计"密码/Secret 输入框" | `CredentialField.tsx:8-15,125-126`（secret 由宿主原生输入） |
| H-08 | 绕过 `code → 文案` 映射，直接渲染后端 message | `bookshelf/error.ts:2-4`；`settings/SettingsErrorBar.tsx:9-14` |
| H-09 | 把事件载荷当状态真相 | `events.ts:5-9` |
| H-10 | 依赖 `window` 尺寸之外的窗口能力（置顶、全屏、多窗、拖拽分栏持久化） | 无窗口 API 权限，Rust 侧无 WindowBuilder（§2.8） |
| H-11 | 破坏 `library_*` / `settings_*` 的 wire 名字与参数形状 | 命令名是"RULED wire name"，被 Rust 测试逐个钉住（`main.rs:2678-2693`、`library/client.ts:47-71` 注释） |
| H-12 | 在生产构建里保留探测/deny 矩阵/`?view=console`/FPS 浮层等证据表面 | 它们是 `App.tsx` 的宿主逻辑（§A.6）；新设计若替换 `App.tsx` 必须显式决定这些表面的去向（属 Lead 决策，非本盘点结论） |

---

## 4. 最容易踩坑的三条（技术侧）

| # | 坑 | 为什么容易踩 | 证据 |
|---|---|---|---|
| 1 | **以为"改 CSS 就行"，其实没有样式层** | 项目 0 个 CSS 文件、710 处内联样式、280 处硬编码色值；`outline: none` 10 处无法被 CSS 覆盖修正；`var(--x, fallback)` 的变量从未定义。任何"设计系统落地"都必须先建样式层，否则只能继续散弹式改组件 | §1.3；`RegionOverlay.tsx:42-48`；`AppShell.tsx:215` |
| 2 | **以为能弹原生对话框/存文件/读路径** | capability 只给了 66 条业务命令 + 事件监听，没有 `dialog`/`fs`/`opener` 权限；CSP 也掐死了外链字体与第三方 API。"导入 = 调 `library_import_*`"、"打开文件夹 = 调 `library_reveal_export_folder`/`plugins_open_directory`"、"凭据 = 原生窗口收集"是三条唯一通路 | §2.5、§2.6；`CredentialField.tsx:8-15` |
| 3 | **以为有 push 就有实时状态** | 事件面只有 7 个且明文规定"事件是失效提示"；列表/Region/设置变更全无事件 → 跨页一致性必须自己设计（重查策略、失效标记或轮询），否则会像现状那样出现"书架与工作台各存一份书单"（03 IA-07）。同理进度只能读快照，现有实现是 250ms 硬轮询 | `events.ts:5-9,53-74`；`WorkbenchPage.tsx:478-488` |

---

## 附：本文未验证项

| 项 | 状态 | 说明 |
|---|---|---|
| 200% DPI 下 1024×680 的实际可用性 | `UNVERIFIED` | 无 DPI 代码，未实机采样 |
| 候选令牌 F 是否为新方向 | `UNVERIFIED`/非事实 | 存在于 `doc/design/`，AC6 用作映射基准，但未接入；方向由 Lead 裁决 |

| 是否存在 CI 流程自动跑前端 vitest / e2e | `UNVERIFIED` | 仓库内未发现引用 `vitest`/`npm test` 的流水线脚本；`tools/` 只找到 `dev-preview.ps1` |
| CSP 下新增同源 CSS/字体文件是否会被 Tauri `frontendDist` 打包 | 技术上应可（属 `dist` 内资源），但未实测 | `tauri.conf.json:6-8,16-18` |
