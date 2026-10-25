# UIUX-V2-RUNTIME-1 真机视觉自查（AC12）

日期：2026-10-25（Asia/Shanghai）
环境：主工作树 `G:\CODEX\New Manga`，`apps/desktop/frontend`，Vite dev server `http://localhost:5189/`，真实 Chromium（`C:\Program Files\Google\Chrome\Application\chrome.exe`，1600×1000 窗口，设备像素比 1）。
数据来源：`src/dev/devMockBridge.ts`（dev-only 垫片，右上角常驻黄色角标「浏览器预览 · 假数据」；所有截图均保留角标，以证明不是生产数据）。

## 为什么必须真机看一眼

jsdom 不应用样式表。本项目历史上因此漏过一个 P0（按钮样式全部被元素级 reset 压掉而 489 条测试全绿）。本轮所有"设计语言是否正确"的结论只来自真实渲染截图，不来自单元测试。

## 已验证项（逐张）

| # | 截图 | 页面/状态 | 观察结论 |
|---|---|---|---|
| 01 | `shots/01-shelf-dark.png` | 书架 / 深色 / 真实数据 | v2 标题栏（品牌 + 四页 PrimaryNav + 命令入口 + 主题切换 + 窗口按钮）、工具栏（搜索/筛选/排序/导入/新建）、168px 网格、亚克力详情面板（真实章节与页数）、底部浮动状态条（真实 `core_ping` 状态）全部正确渲染；封面为由 `book_id` 派生的确定性渐变（不冒充真实封面） |
| 02 | `shots/02-shelf-light.png` | 书架 / 浅色 / 真实数据 | 切换主题后整页（含亚克力面板、按钮、输入框、状态条）真实换色，`color-scheme` 作用域化生效 |
| 03 | `shots/03-workbench-real-data.png` | 工作台 / 真实章节与页 | 胶片条为真实 6 页（缩略图用「未知」虚线占位，不画假缩略图）；画布加载真实页图（经 `resolve_page_resource` → `issue_resource_url` → `fetchAll` → Blob URL）；检查器显示真实区域 3 条与「未识别」OCR 说明；无运行记录时显示 PageBlocked「尚未开始运行」+ 运行按钮 |
| 04 | `shots/04-workbench-running.png` | 工作台 / 运行中 | 点击「运行」后：状态符号 ◐ 进行中、整体进度 40%、任务总数 6 / 已完成 2 / 失败 0 / 阻塞 0、任务列表七态（完成/进行中/排队）、底部流水线阶段（识别/翻译/排版）均为真实投影字段；`step_flow` 段数来自 Core 而非设计稿的 10 段 |
| 05 | `shots/05-reader-real-data.png` | 阅读器 / 真实章节 | 顶部浮层显示真实书名、章节号与标题、页码 1/6、真右→左布局；页图真实加载；左右翻页热区可点且首/末页正确禁用；底部显示「本话进度 —」（投影无进度时不编造百分比） |
| 06 | `shots/06-settings-provider-dark.png` | 设置 / Provider / 深色 | 12 分节导航 + 内容带；Provider 分节挂载真实面板；后端不可用时显示错误码态而不是假成功；侧栏页脚显示真实 `settings_get` 同步状态与 SFX 策略「未设置（按 Core 默认）」 |
| 07 | `shots/07-command-palette.png` | 命令面板（Ctrl+K） | 亚克力强档面板、四页导航 + 主题切换、当前页命令禁用并说明原因、焦点在搜索框、键盘提示与「4/5 可用」计数正确 |
| 08 | `shots/08-settings-ocr-light.png` | 设置 / OCR / 浅色 | OCR 分节真实控件（识别脚本、文字方向）按浅色主题渲染；「该节未设置（Core 返回 JSON null）」与「当前持久化值：未设置」为真实读回，不编造默认值 |
| 09 | `shots/09-workbench-no-context.png` | 工作台 / 无上下文 | PageEmpty + 明确指引「先在书架选择作品」+ 返回书架按钮；不渲染任何占位漫画内容 |
| 10 | `shots/10-reader-no-context.png` | 阅读器 / 无上下文 | PageEmpty + 「本页不会用占位内容冒充可读章节」；保留 v2 顶/底浮层带 |
| 11 | `shots/11-design-preview-shelf.png` | `?view=design` 静态骨架 | 设计预览未退化：10 本 fixtures、七态状态标记、进度条、章节列表、5 列网格、亚克力预算 2 层 |

## 本轮真机自查抓到的缺陷（已修复，并补守卫）

1. **模块级样式常量冻结在深色主题**（P0 级可见缺陷）：浅色主题下设置页下拉框仍是深黑底。根因：`src/settings/SectionField.tsx` 的 `settingsInputStyle` / `settingsSelectStyle` 是模块级 `{...tokens.x}` 常量，import 时即固定。修复：改成按当前主题现算的访问器属性对象（不用 Proxy —— React 行内样式遍历会触发 `ownKeys` 不可变性检查）；新增 `src/theme/themeReactiveStyles.test.ts` 三条守卫。
2. **dev mock 的 wire 形状错误**：`list_chapters` / `list_chapter_pages` 返回裸数组，客户端期望 `{chapters}` / `{pages}`，导致章节区显示 `PAGE_NAV_MALFORMED`。修复后章节、页数正常（这也顺带验证了错误面确实会显示错误码）。
3. **阅读器/设置页标题栏缺命令入口**：四页不一致。已要求实现方补齐（两页均已含 `data-testid="command-trigger"`）。

## 未验证项（HUMAN_VERIFY，不得声称通过）

| 项 | 原因 | 解除条件 |
|---|---|---|
| 真实 Tauri 生产窗口 + Python Core 端到端四页点选 | 本轮未构建 Tauri 安装包、无 Python Core 运行环境；构建/打包属发布线，不在本 Task 范围 | 在有 Core 的环境执行一次 `tauri build`/dev 启动，人工点选四页；重点确认：页图经 host HTTP 通道渲染、阅读进度写回、导入对话框原生选择器、Core 掉线时状态条与错误码 |
| WebView2 与 Chromium 的渲染差异 | 自查用 Chromium；WebView2 同内核但版本与 GPU 路径不同 | 同上一次真机确认（尤其 `backdrop-filter` 与亚克力噪声层） |
| 高 DPI / 窄窗口响应式 | 仅按 1600×1000、DPR=1 检查 | 需要时另立 Task |

## 复现步骤

```powershell
cd 'G:\CODEX\New Manga\apps\desktop\frontend'
npm run dev -- --port 5189
# 真实窗口（可交互）：
& 'C:\Program Files\Google\Chrome\Application\chrome.exe' --user-data-dir=$env:TEMP\nm-visual-profile --window-size=1600,1000 http://localhost:5189/
# 单页无头截图（可脚本化）：
& 'C:\Program Files\Google\Chrome\Application\chrome.exe' --headless=new --disable-gpu --window-size=1440,900 --virtual-time-budget=4000 --screenshot=out.png 'http://localhost:5189/?view=design'
```

注意：`devMockBridge` 只在 `import.meta.env.DEV` 下安装；真实 Tauri 桥存在时绝不覆盖。

## ZCode 独立审查 r1 的处置（2026-10-25）

审查结论：`changes_requested`，0×P0 / 1×P1 / 1×P2 / 5×P3（`review-zcode-r1.md`）。逐条处置：

| finding | 严重度 | 处置 | 证据 |
|---|---|---|---|
| F-1 书架页运行时诚实数据零测试守卫（审查者变异核验：`progress: null → 42` 后 561 条测试全绿） | P1 | **已修复**：新增 `src/pages/Shelf.test.tsx` 三条守卫（真实书卡字段、无 `.nm-progress`/百分比/VOL./七态、章节页数来自 IPC 而非 fixtures、空书架态）。DSH 复做变异核验：改回 `progress: 42` → 新测试 1 failed；还原 → 3 passed，工作树零残留 | `vitest-run.txt`（60 文件/564 passed）、本文件下方"变异核验" |
| F-2 dev mock 的 `region_type`/`origin` 用冻结闭集外的值 → 区域行残缺、本文件未登记 | P2 | **已修复**：改为 `speech`/`narration`/`sfx` + `machine`/`user`，`sfx_policy` 改为闭集内 `translate`/`skip`；重截 `shots/03` 并更新本文件第 03 行 | `shots/03-workbench-real-data.png` |
| F-3 tsc 证据首行留有 `REVIEW_HEAD_PENDING` 占位 | P3 | **已修复**：重采 `tsc-run.txt`/`vitest-run.txt`，去掉占位并标注采集时点 | `tsc-run.txt` |
| F-4 `PageEmpty` 无显式 role | P3 | **已修复**：`PageEmpty` 根节点加 `role="status"`，四态 role 一致 | `src/ui/PageState.tsx` |
| F-5 两处字面色值（close 悬停 `#FFFFFF`、命令面板遮罩 `rgba(0,0,0,0.32)`）未令牌化 | P3 | **登记为债务**：均为 DESIGN-V2-IMPL-1 冻结既有值，本 Task 未新增；并入 R6 的后续"控件几何 + 间距/装饰色令牌"Task | Task 卡 R6 |
| F-6 入库版任命书范围描述与冻结区间不符；PrimaryNav 注释过时 | P3 | **已修复**：任命书范围描述已在本次提交修订；`PrimaryNav.tsx` 注释更新为"五个消费点（运行时四页经 UiRoot + 设计预览）" | `APPOINTMENT.md`、`components/PrimaryNav.tsx` |
| F-7 设计预览 fixture 底栏保留未实现的「Esc 返回」keyhint | P3 | **登记为债务**：base（DESIGN-V2-IMPL-1 骨架）既有、运行时分支无此假提示；并入设计预览清理 Task | Task 卡 R7 |

修复后回归：`tsc --noEmit` exit 0；`vitest run` **60 文件 / 564 passed / 0 skipped**，exit 0。

### 变异核验（DSH 复做，证明 F-1 守卫有判别力）

```
改 src/pages/Shelf.tsx 运行时 progress: null → progress: 42
npx vitest run src/pages/Shelf.test.tsx
→ Tests 1 failed | 2 passed   （新守卫拦截）
还原后
→ Tests 3 passed              （工作树 git status 对 src/ 无输出）
```
