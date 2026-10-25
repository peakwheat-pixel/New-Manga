---
id: UIUX-V2-RUNTIME-1
title: 设计系统 v2 接入运行时：四页真实数据、设置页与单一 UI 收口
kind: implementation
governance_version: 3
status: done
approval: user_directed_20261025_auto_authorized
suggested_owner: dsh
owner: dsh
reviewer: zcode-external
depends_on: [DESIGN-V2-IMPL-1]
base_commit: b51d202c9ffab869d26bdb15b38459147991685c
branch: main
worktree: null
integration_commit: af421b9e6b973b5705e44e4c57bfebbb614ed33d
delivery_head: af421b9e6b973b5705e44e4c57bfebbb614ed33d
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/UIUX-V2-RUNTIME-1
allowed_paths:
  - apps/desktop/frontend/src/**
  - apps/desktop/frontend/index.html
  - doc/tasks/UIUX-V2-RUNTIME-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/handoffs/UIUX-V2-RUNTIME-1-*.md
  - verification/UIUX-V2-RUNTIME-1/**
---

# UIUX-V2-RUNTIME-1：设计系统 v2 接入运行时

## 来源与目标

- **需求来源**：用户 2026-10-25 授权会话（「全自动推进到产品完成」）中的 P0 目标：把已冻结并集成（[DESIGN-V2-IMPL-1](DESIGN-V2-IMPL-1.md)，集成 commit `e1fd738a7`）的设计系统 v2 **真正接进运行时**，替换旧内联样式界面、接通 Tauri IPC，让书架 / 工作台 / 阅读器 / 设置四页按 v2 设计语言真实可用，并只有一套 UI。
- **基线事实（已核对）**：base `b51d202c9` 时 v2 只是 `?view=design` 的静态骨架（三页、固定 fixtures、无设置页）；真实数据由历史内联样式容器 `shell/AppShell.tsx` + `bookshelf/BookshelfPage.tsx` + `workbench/WorkbenchPage.tsx` + `reader/ReaderPage.tsx` + `settings/SettingsPage.tsx` 渲染，两套外观并存。
- **可观察交付**：Tauri 生产窗（及浏览器 dev 预览）默认渲染 v2 运行时根；四页各自从真实 IPC 取数并渲染 v2 设计语言；设置页从"不存在"变为 12 分节可用的 v2 页面；历史内联样式容器不再挂在任何默认路由上（只保留显式 `?view=legacy` 回退通道），并有机械守卫防止回归。

## Acceptance Criteria

- [x] **AC1 令牌单一真相 + 主题可切换**：`theme/tokens.ts` 改为 v2 令牌的运行时镜像（`tokens.css` 为唯一真相源），dark/light 两套取值与 CSS 变量逐值相等，字号收敛到 28/20/14/12、圆角收敛到 8/4/2/0；模块级样式常量不再被冻结在 import 时的主题（真机自查发现的 P0 级缺陷，改为按当前主题现算）。证据：`src/theme/tokens.test.ts`（29 例）、`src/theme/themeReactiveStyles.test.ts`（3 例）、截图 02/08。 <<MET>>
- [x] **AC2 v2 运行时根**：新增 `src/ui/UiRoot.tsx` 作为唯一运行时根（主题 / 当前页 / 跨页上下文 / 命令面板 / 全局快捷键 / IPC 客户端装配），`?view=design`、`?view=legacy`、probe/AC1 证据路径语义各自保持不变。证据：`src/ui/UiRoot.test.tsx`（6 例）、`src/App.test.tsx`（生产窗断言改为 app-root）。 <<MET>>
- [x] **AC3 书架页真实数据**：`pages/Shelf.tsx` 双数据源（fixtures / IPC），真实读取 `library_list_books` + `core_ping` + `list_chapters` + `list_chapter_pages`；导入 / 新建 / 回收站沿用既有真实对话框。证据：`src/pages/DesignPreview.test.tsx`（fixtures 不退化）、截图 01/02、`src/ui/UiRoot.test.tsx`。 <<MET>>
- [x] **AC4 工作台页真实数据**：`pages/Workbench.tsx` 运行时分支接 `list_chapters` → `list_chapter_pages` → `resolve_page_resource` → `issue_resource_url` → `fetchAll`（Blob URL）+ `list_regions` + `library_start_run` / `library_get_run_snapshot` / `library_get_task_projection`（1s 轮询、卸载即停）。证据：`src/pages/Workbench.test.tsx`（9 例）、截图 03/04/09。 <<MET>>
- [x] **AC5 阅读器页真实数据**：`pages/Reader.tsx` 运行时分支接 `library_get_reader_projection` + `library_save_reading_progress` + 页图资源通道；保留 ←/→ 翻页与章末不越界；webtoon_vertical 无接线时显式 BLOCKED 而不是假装可读。证据：`src/pages/Reader.test.tsx`（8 例）、截图 05/10。 <<MET>>
- [x] **AC6 设置页 v2 实现**：`pages/Settings.tsx` 新建 v2 页面（标题栏 + 12 分节导航 + 内容带），挂载既有 12 个真实设置面板；`settings_get` 失败整页 PageError（显示错误码）且不挂载 panel；侧栏页脚显示真实 SFX 策略/未设置状态。证据：`src/pages/Settings.test.tsx`（7 例）、截图 06/08。 <<MET>>
- [x] **AC7 单一 UI 收口**：App 生产窗默认渲染 `UiRoot`；`AppShell` 只允许出现在显式 `?view=legacy` 分支；`UiRoot.test.tsx` 有源码级守卫断言运行时根不 import 任何历史页面容器，并断言 AppShell 不再出现在默认分支。证据：`src/ui/UiRoot.test.tsx`。 <<MET>>
- [x] **AC8 三/四态与诚实数据**：四页共用 `src/ui/PageState.tsx`（loading / empty / error / blocked），错误面必须显示错误码；无 IPC 来源的字段（跨书进度、跨书流水线状态、封面图、OCR 文本与置信度、区域文本、缩略图、作品标题等）一律省略或标「未知/未识别」，不得沿用 fixtures 数值。证据：`src/pages/Shelf.test.tsx`（3 例，运行时书卡/章节反 fixtures 回填，含变异核验）、`Workbench.test.tsx` 的反断言、`Reader.test.tsx`/`Settings.test.tsx` 的诚实态断言 + 截图 03/05/09/10。 <<MET>>
- [x] **AC9 命令面板与键盘全通路**：全局命令面板（Ctrl+K）抽出为 `src/ui/CommandPalette.tsx`，具备 Tab 焦点圈禁、↑↓/Home/End/Enter/Esc 全通路、`aria-activedescendant`、关闭后焦点还给唤起元素；Ctrl/Cmd+1..4 切四页。证据：`src/ui/CommandPalette.test.tsx`（7 例）、`src/ui/UiRoot.test.tsx`、截图 07。 <<MET>>
- [x] **AC10 设计层债务清理（DESIGN-V2-IMPL-1 P2 清单）**：`base.test.ts` 守卫补齐缩进块与 `@media`/`@supports` 嵌套盲区；命令面板焦点圈禁（见 AC9）；`:root` 的 `color-scheme` 作用域化到 `:where(html[data-view])`，不再泄漏到冻结的 probe/AC1 路径；`.nm-shelf` 与 `.nm-mica` 的重复背景收敛为一份；`pages.css` 的 gap 字面值（1/2/4/5/6px）全部改走 `--nm-space-*` 令牌。证据：`src/design/base.test.ts`（7 例，含守卫自指对照）、`design/tokens.css` 末尾作用域块。 <<MET>>
- [x] **AC11 构建与测试**：`tsc --noEmit` 退出 0 且无诊断；`vitest run` **60 文件 / 564 测试全部通过**（0 skipped）。证据：`tsc-run.txt`、`vitest-run.txt`。 <<MET>>
- [x] **AC12 真机视觉自查（可替代部分）**：dev server（`localhost:5189`，主工作树）+ 真实 Chromium 打开运行时路径，逐页截图核对：深/浅两主题、书架（真实书/章节/页数）、工作台（真实页图/区域/运行投影/七态）、阅读器（真实页图/页码/章名/进度）、设置（12 分节、真实控件、错误码态）、命令面板、设计预览不退化。证据：`visual-verification.md` + `shots/01..11`。 <<MET>>
- [x] **AC13 独立审查**：由未参与实现的 ZCode 对冻结 head 做只读审查：r1 `changes_requested`（0×P0/1×P1/1×P2/5×P3，`review-zcode-r1.md`）→ 处置提交 `af421b9e6` → r2 增量复审 `approved`（`review-zcode-r2.md`，独立复跑 tsc exit 0 / vitest 60 文件 564 passed，独立复做变异核验证明 F-1 守卫有判别力）；DSH 未自审。 <<MET>>

## 允许修改范围

- `apps/desktop/frontend/src/**`：设计层（`design/`）、运行时根与共享件（新增 `ui/`）、四页（`pages/`）、令牌镜像（`theme/`）、dev 预览垫片（`dev/`）、`components/PrimaryNav.tsx`（第四页）、`settings/SectionField.tsx`（主题响应样式，唯一一处触碰既有 settings 代码）、`App.tsx` / `App.test.tsx`。
- 本 Task、Handoff、`verification/UIUX-V2-RUNTIME-1/**`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`。
- 不新增 npm 依赖（`package.json` / `package-lock.json` 零改动，见 AC 外的 closeout 核对）。

## 禁止范围

- 不改 Rust（`apps/desktop/src-tauri/**`）、不改 Python Core、不改 IPC 契约/Schema、不改 `src/settings/**` 的业务逻辑（仅 `SectionField.tsx` 的主题响应样式）。
- 不做原生亚克力（`window-vibrancy` / Windows App SDK / 透明多窗口）；不用 emoji 表达状态；同屏 `backdrop-filter` ≤2 层。
- 不处理用户原始漫画页数据；不删除既有测试来让测试变绿（唯一被改写的既有断言是 `App.test.tsx` 的生产窗路由断言与 `DesignPreview.test.tsx` 的四页 tab 断言，二者都是产品行为变更的直接后果，已在 Handoff 说明）。
- 不合并未知分支、不 force push、不改他人未提交内容。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 令牌 | `npx vitest run src/theme` | Node + jsdom/vitest | PASS（32 例） | `vitest-run.txt` |
| AC2/AC7/AC9 运行时根 | `npx vitest run src/ui` | 同上 | PASS（13 例） | `vitest-run.txt` |
| AC3 书架 | `npx vitest run src/pages/DesignPreview.test.tsx` | 同上 | PASS（10 例，fixtures 未退化） | `vitest-run.txt` |
| AC4 工作台 | `npx vitest run src/pages/Workbench.test.tsx` | 同上 | PASS（9 例） | `vitest-run.txt` |
| AC5 阅读器 | `npx vitest run src/pages/Reader.test.tsx` | 同上 | PASS（8 例） | `vitest-run.txt` |
| AC6 设置页 | `npx vitest run src/pages/Settings.test.tsx` | 同上 | PASS（7 例） | `vitest-run.txt` |
| AC10 设计层守卫 | `npx vitest run src/design` | 同上 | PASS | `vitest-run.txt` |
| AC11 类型 | `node node_modules/typescript/bin/tsc --noEmit` | frontend 目录 | exit 0，无输出 | `tsc-run.txt` |
| AC11 全量测试 | `npx vitest run --reporter=basic` | frontend 目录 | 60 文件 / 564 passed / 0 skipped | `vitest-run.txt` |
| AC12 真机视觉 | dev server + Chrome，逐页截图 | `localhost:5189`，dev mock 数据 | PASS（11 张，见 index） | `visual-verification.md` |
| AC12 真实 Core 端到端 | 打包 Tauri + Python Core 后点选四页 | 需要真实 app 构建 | **NOT_RUN**（本轮未构建 Tauri 安装包；HUMAN_VERIFY 登记） | `visual-verification.md` §未验证项 |

## 依赖、风险与阻塞

- 硬依赖：[DESIGN-V2-IMPL-1](DESIGN-V2-IMPL-1.md) 已 `done`（集成 `e1fd738a7`）；本 Task 只消费其令牌/材质/状态组件与页面骨架，不改其冻结取值。
- **风险 R1（已处置）**：令牌从静态对象变为主题 Proxy 后，模块级 `const style = {...tokens.x}`（`settings/SectionField.tsx` 两处）会被冻结在深色值；真机自查在浅色主题下抓到深色下拉框。已改为按主题现算的访问器属性对象，并加 `themeReactiveStyles.test.ts` 守卫。**备选**（未采用）：把 settings 各 panel 的全部行内样式改成 CSS 类——范围过大且会重写 12 个既有面板。
- **风险 R2（已登记，不阻塞）**：真实 Core 端到端（打包 Tauri + Python Core 后四页点选）**未执行**：本轮无 Tauri 构建产物、无 Python Core 运行环境，且构建/打包属于发布线（与本 Task 的 UI 接线目标不同）。因此页面图像的 host 侧 HTTP 通道只在 dev 合成图下验证过；**HUMAN_VERIFY**：需要在真实 app 中确认页图渲染、阅读进度写回、导入对话框原生选择器。不得宣称该项已通过。
- **风险 R3（已登记）**：`?view=legacy` 回退通道保留 `AppShell`，因此历史容器与其测试仍在仓库内（未被删除）。这是有意的低风险选择（删除会同时删掉 100KB+ 行为测试），并在 `UiRoot.test.tsx` 用源码级守卫保证它们不回到默认路由。**备选**（未采用）：立即删除历史容器——与"单一 UI"目标等价但牺牲回归覆盖，留作后续清理 Task。
- **风险 R7（债务，来自独立审查 P3）**：base 冻结遗留的两处字面色值（`.nm-window-btn--close:hover` 的 `#FFFFFF`、`.nm-command-backdrop` 的 `rgba(0,0,0,0.32)`）与设计预览 fixture 底栏未实现的「Esc 返回」keyhint，均为 DESIGN-V2-IMPL-1 既有、本 Task 未新增；运行时分支无该假提示。并入后续「控件几何 + 装饰色令牌」与「设计预览清理」Task，不在本 Task 扩大范围。
- **风险 R6（如实登记，未修复）**：`pages/pages.css` 仍有 21 处**非 gap** 的间距字面值（`padding` / 绝对定位微调，如 `padding: 2px`、`top: 10px`、`bottom: 14px`）。本轮只把 `gap` 字面值（1/2/4/5/6px，共 22 处）改走 `--nm-space-*`；其余多与固定高度控件（`.nm-tabs` 28px、`.nm-canvas__tools` 36px）的盒模型耦合，直接换成 4/8/12/16 会溢出或改变控件高度，需要逐控件重排才能安全收敛。**备选**（未采用）：本轮强行全量替换——会在无真机逐控件复核的条件下改变控件几何，风险高于收益。解除条件：另立"控件几何 + 间距令牌"Task，按控件逐个核对高度与内边距。
- **风险 R4**：页面级设计语言是 v2，但设置/导入等次级面板仍是既有内联样式组件（经令牌桥接后配色/圆角/字阶与 v2 一致）；它们与 v2 的差异是结构与密度，不是色板。若要求像素级一致，需另立"面板 v2 重绘"Task。
- 无阻塞本 Task 集成的项。

## 交付与运行记录

- Handoff：[UIUX-V2-RUNTIME-1](../handoffs/UIUX-V2-RUNTIME-1-delivery.md)
- Review：待 ZCode 独立审查（`verification/UIUX-V2-RUNTIME-1/APPOINTMENT.md` 指定唯一写路径）。
- 实际测试：2026-10-25，`apps/desktop/frontend`，tsc exit 0，vitest 59 文件 / 561 passed。
- 分工（如实记录）：Lead（DSH）实现运行时根、共享状态组件、命令面板、令牌桥接、书架页、dev 预览垫片、设计层债务与全部文档/证据；`impl-workbench`（子 Agent）实现工作台页与 9 条测试；`impl-reader-settings`（子 Agent）实现阅读器页、设置页与 15 条测试。三者写作用域互斥，Lead 独立复跑 tsc/vitest 与真机截图，未采信子 Agent 报告结论。
- 2026-10-25 独立审查与集成：
  - r1 ZCode `changes_requested`（0×P0/1×P1/1×P2/5×P3，`review-zcode-r1.md`）→ DSH 处置提交 `af421b9e6`（F-1 补 `Shelf.test.tsx` 三条守卫并自做变异核验、F-2 修 dev mock 枚举并重截 `shots/03`、F-3 重采证据、F-4 加 `role="status"`、F-5/F-7 登记 R7 债务、F-6 更新任命书与注释）。
  - r2 ZCode 增量复审 `approved`（`review-zcode-r2.md`）：独立复跑 tsc exit 0 / vitest 60 文件 564 passed；独立复做变异核验（`progress: null → 42` → 1 failed，还原 → 3 passed）；F-1..F-7 全部 CLOSED；仅两处记录精确性 P3（N-1/N-2，已在收口时订正）。
  - 集成方式：fast-forward 无冲突（本轮全部提交直接落在 `main`），`integration_commit` = `af421b9e6b973b5705e44e4c57bfebbb614ed33d`（修复 head，含 r1 全部处置）；其后 df48a14b3、$short2（r2 复审入库 + N-1/N-2 订正）与本次收口提交均为文档/指针。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC11 | verification/UIUX-V2-RUNTIME-1/tsc-run.txt | 1853f0a07 | - | CANONICAL |
| EV-02 | AC1–AC11 | verification/UIUX-V2-RUNTIME-1/vitest-run.txt | 1853f0a07 | - | CANONICAL |
| EV-03 | AC12 | verification/UIUX-V2-RUNTIME-1/visual-verification.md | 1853f0a07 | - | CANONICAL |
| EV-04 | AC12 | verification/UIUX-V2-RUNTIME-1/shots/01-shelf-dark.png | 1853f0a07 | - | CANONICAL |
| EV-05 | AC12 | verification/UIUX-V2-RUNTIME-1/shots/02-shelf-light.png | 1853f0a07 | - | CANONICAL |
| EV-06 | AC4/AC12 | verification/UIUX-V2-RUNTIME-1/shots/03-workbench-real-data.png | 1853f0a07 | - | CANONICAL |
| EV-07 | AC4/AC12 | verification/UIUX-V2-RUNTIME-1/shots/04-workbench-running.png | 1853f0a07 | - | CANONICAL |
| EV-08 | AC5/AC12 | verification/UIUX-V2-RUNTIME-1/shots/05-reader-real-data.png | 1853f0a07 | - | CANONICAL |
| EV-09 | AC6/AC12 | verification/UIUX-V2-RUNTIME-1/shots/06-settings-provider-dark.png | 1853f0a07 | - | CANONICAL |
| EV-10 | AC9/AC12 | verification/UIUX-V2-RUNTIME-1/shots/07-command-palette.png | 1853f0a07 | - | CANONICAL |
| EV-11 | AC1/AC6/AC12 | verification/UIUX-V2-RUNTIME-1/shots/08-settings-ocr-light.png | 1853f0a07 | - | CANONICAL |
| EV-12 | AC3/AC8/AC12 | verification/UIUX-V2-RUNTIME-1/shots/09-workbench-no-context.png | 1853f0a07 | - | CANONICAL |
| EV-13 | AC5/AC8/AC12 | verification/UIUX-V2-RUNTIME-1/shots/10-reader-no-context.png | 1853f0a07 | - | CANONICAL |
| EV-14 | AC3/AC12 | verification/UIUX-V2-RUNTIME-1/shots/11-design-preview-shelf.png | 1853f0a07 | - | CANONICAL |
| EV-16 | AC8/AC13 | verification/UIUX-V2-RUNTIME-1/review-zcode-r1.md | af421b9e6 | - | CANONICAL |
| EV-17 | AC8 | apps/desktop/frontend/src/pages/Shelf.test.tsx | af421b9e6 | - | CANONICAL |
| EV-18 | AC13 | verification/UIUX-V2-RUNTIME-1/review-zcode-r2.md | ae4e3a077 | - | CANONICAL |
| EV-15 | AC13 | verification/UIUX-V2-RUNTIME-1/APPOINTMENT.md | 66013fc33 | - | CANONICAL |

> `sha256` 列留空：本 Task 的证据是仓内文本与 PNG，判别依据为 commit 内文件内容（与 EV-01/02 同 commit）。完整 214KB vitest 原始输出在仓外 `G:\CODEX\New Manga.workspace\UIUX-V2-RUNTIME-1\vitest-run-full.txt`（体积原因不入库）。

## Resource Manifest

机器可读清单：`verification/UIUX-V2-RUNTIME-1/resource-manifest.json`（schema_version 1，本 Task 唯一权威 resource 记录；下表为人读摘要）。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| evidence | verification/UIUX-V2-RUNTIME-1 | PRESERVE_REFERENCED | verification/UIUX-V2-RUNTIME-1 | verification/UIUX-V2-RUNTIME-1/resource-manifest.json | canonical 证据入库；EV-01..EV-18 均被独立审查复现 |
| agent-output | G:/CODEX/New Manga.workspace/UIUX-V2-RUNTIME-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/UIUX-V2-RUNTIME-1 | verification/UIUX-V2-RUNTIME-1/resource-manifest.json | 仓外保留：截图原图、ZCode 审查原始 stdout、214KB vitest 全文；无进程引用 |
| build-artifact | — | NOT_APPLICABLE | — | — | 未构建、未打包，无 build artifact |
| dataset-model-user-data | — | NOT_APPLICABLE | — | — | 未使用用户素材/模型/数据集；dev 预览为合成假数据并常驻角标 |
| exchange | — | NOT_APPLICABLE | — | — | 无跨机交换产物 |
## Closeout Record

- Closeout date / DSH：2026-10-25 / DeepSeek Harness。
- canonical_evidence_status：`complete`（EV-01..EV-18 全部入库并被独立审查复现；AC12 的 NOT_RUN 项显式登记，未冒充通过）。
- resource_closeout_status：`complete`（无删除/迁移/归档；仓外 agent-output 与 dev 截图标 PRESERVE_REFERENCED）。
- 删除、迁移、归档数量/字节数：0（0 字节删除、0 迁移、0 归档）。
- 未关闭项及保留原因：① AC12「真实 Tauri + Python Core 端到端」= HUMAN_VERIFY（本轮无构建产物与 Core 环境）；② R3 历史内联容器保留待后续清理 Task；③ R4 次级面板未像素级 v2 重绘；④ R6（21 处非 gap 间距字面值）与 R7（两处字面色值 + 设计预览假 keyhint）已登记为债务。
- 当前指针清理：STATUS / REBASELINE_PLAN / TASK_LEDGER 已在本次收口更新；Handoff 指向最终证据与 closeout。
- Push：按安全裁决**未执行**（`main` 含历史材料、干净快照 Gate 未清，push 不可逆；理由见 STATUS「Gate 与保留项」与最终报告）。
- 当前指针清理：STATUS / REBASELINE_PLAN / TASK_LEDGER 已在本次收口更新；Handoff 指向最终证据与 closeout。
