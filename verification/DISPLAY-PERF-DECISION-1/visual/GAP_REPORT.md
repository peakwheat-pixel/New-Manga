# DISPLAY-PERF-DECISION-1 / AC4 — 四页视觉差距清单（材质 · 圆角阴影 · 转场动效）

- **Task**：`DISPLAY-PERF-DECISION-1`（父卡）→ 本报告负责 AC4「四页视觉差距清单」
- **Repo**：`G:/CODEX/New Manga`，HEAD = `c0251b9e7`（工作树中 `doc/` 有他人在改的 4 个文件，本报告未触碰）
- **撰写**：teammate `visual-gap`（DSH Lead 派出）；性质 = **只读分析**，未修改任何产品代码 / 配置 / 设计文档 / Figma
- **证据目录**：`verification/DISPLAY-PERF-DECISION-1/visual/`（本报告 + `figma-ref/` 参考截图）
- **时间**：2026-10-26

---

## 0. 基准、输入与降级说明（先读）

### 0.1 三个基准源及其效力

| 源 | 位置 | 效力 | 本次使用情况 |
|---|---|---|---|
| **设计基线**（权威） | `doc/design/AD001_FOUR_PAGE_UI_BASELINE.md`（563 行，四页 + 状态矩阵 + §8 令牌 + §1.2 冻结语义） | 结构/交互/令牌的**唯一权威** | 全量读取 |
| **Figma v2 视觉稿** | fileKey `sHQvkMfq5wue6DXhKUP9PV`「New Manga · 三产品面设计稿 v2 · Fluent」 | 用户确认的**视觉目标**（颜色/材质/圆角/字阶/动效） | 只读读到了 00 概览、01 材质与动效、03 书架（S1）、04 工作台（W1）、05 阅读（R1–R3 缩略） |
| **现状** | exe `C1AB2749…`（NARROW-1 冻结）的 DPR2 截图 + 当前前端源码 | 被审查对象 | 14 张截图 + 10 个源文件 |

### 0.2 Figma 可得性（**降级范围，必读**）

Figma MCP **可用**（`create_session` 成功，sessionId `3ab00419…`），全程只读，未写入。

已拉取并核对的画板（`figma-ref/` 内有副本，便于复核）：

| 画板/页 | nodeId | 说明 |
|---|---|---|
| `00 概览` | `0:1` | 12 画板索引 + 已知限制清单 |
| `01 材质与动效` | `1:2` | **本次判定的关键依据**：材质三层 / 仿亚克力四件套 / 圆角分级 / 字阶 / 动效清单 / 降级链 |
| `S1 书架·方案 A·黑夜` | `3:2` | `figma-ref/S1-shelf-dark.png` |
| `W1 工作台·单页·黑夜` | `9:2` | `figma-ref/W1-workbench-dark.png` |
| `R1/R2/R3` 阅读三画板 | `1:6` | `figma-ref/R-pages-reader.png`（三画板合图，缩略） |

**降级 1（重要）**：Figma 的 **12 块画板全部是「书架 / 工作台 / 阅读」三面（S1–S5、W1–W4、R1–R3），没有任何「设置」页画板**，且 Figma 顶部导航只有 3 个 tab（书架/工作台/阅读），没有设置入口。

→ **设置页（§4 表）的基准只能是 `AD001` §5 + §8 令牌 + Figma「02 组件」的组件规格**，没有视觉稿可对。设置页结论的置信度低于其他三页，已在表中逐条标注。

**降级 2**：未读取 Figma「02 组件」页的 68 个变体明细（体积过大且对「材质/动效」主命题边际收益低）。组件级尺寸差异（Button/Chip/Field 的 padding、字号）**未逐项比对**，标注为「未覆盖」。

**降级 3**：Figma 画板是 1600×1000，现状实测是 900×700 / 1280×800。宽度差异导致「列数、面板可见性」不能逐像素比对，本报告只比对**结构、层级、材质、字号、圆角、动效**，不比对绝对坐标。

### 0.3 现状截图口径

截图由 NARROW-1 用 **CDP `Page.captureScreenshot`** 产出 → **只包含 WebView 内容区，不含系统窗口边框/系统标题栏**。因此「窗口 chrome 层」的结论不能仅由截图得出，另用配置 + Rust/前端源码 + 旧构建整窗实拍交叉验证（见 SH-01）。

---

## 1. 判定口径

每条差距给一个**主判定**，必要时附「子标注」：

| 标记 | 含义 |
|---|---|
| **欠账** | 当前栈（Tauri 2 + WebView2 + CSS）**已具备**该能力，只是没实现/没接上。属实现排期问题，**不构成换栈理由**。 |
| **栈限制** | 当前栈在**原理上做不到**，或只能做到「近似且有肉眼差距」。 |
| **栈限制·有原生替代** | CSS/前端层做不到，但**同一栈内的原生层**（Tauri window API、Rust/DWM）可以做到 → 对产品是**欠账**，不是换栈理由。 |
| **待验证** | 静态证据不足，需真机/实测确认；不硬判。 |
| **设计源冲突** | 设计基线（AD-001 基线）与 Figma v2 互相矛盾 → 需用户/DSH 裁决，**既不是欠账也不是栈限制**。 |

严重度：**P0** = 用户第一眼就否定的观感断层；**P1** = 明显偏离设计、影响专业感；**P2** = 细节不一致。

### 1.1 总览统计（按正文逐条标记汇总，共 43 个编号）

| 类别 | 条数 | 编号 |
|---|---|---|
| **实现欠账** | **27** | SH-02/03/04/05；SB-01/02/03/04/05/06/07/09；WB-01/02/03/04/05/06/07；RD-02/03/04/05；ST-01/02/03/05 |
| **栈限制（严格）** | **2** | SH-07（真 Acrylic 光学质感，设计已接受仿制）、SH-08（OS 窗口圆角，设计未要求） |
| **栈限制·有原生替代（= 实质欠账）** | **2** | SH-01（窗口 Mica）、SH-09（多窗口悬浮窗） |
| **设计源冲突（需 DSH/用户裁决）** | **5** | SH-06（Rail vs 横向 tab）、SH-10（深色模式越权但已成事实）、RD-01（阅读器沉浸式）、RD-06（阅读器底部条）、ST-06（同 SH-06 在设置页的复现） |
| **待验证** | **2** | RD-07（翻页动效无设计依据）、ST-07（设置保存模型） |
| **不判 / 数据状态** | **1** | SB-08（仅 1 本书时的空库观感） |
| **合规样本（已对齐，供 AC6 估算达标率）** | **4** | SB-10、WB-08、RD-08、ST-04 |
| **合计** | **43** | — |

> 「栈限制」合计 **4 条**（严格 2 + 有原生替代 2），其中**没有一条**要求更换 UI 栈（详见 §7）。

**一句话结论**：用户抱怨的「材质 / 圆角阴影 / 转场动效」三项里，**材质配方已经 100% 按 Figma 实现、但被「窗口层不透明」整体废掉**；圆角/阴影/字阶/间距的令牌体系也已落地、偏差集中在**布局与卡片形态**；**转场动效几乎 0 实现**（全仓只有 1 个 `@keyframes`）。因此这三项的主因是**实现欠账**，不是栈限制 —— 但「真亚克力的光学质感」确属栈上限。

---

## 2. 跨页 / Shell 层差距（SH）

这一层是**用户「外观不满意」的最大来源**，优先级高于任何单页细节。

### 2.1 SH 表

| ID | 维度 | 现状 | 设计基线 / Figma | 严重度 | 判定 | 依据 |
|---|---|---|---|---|---|---|
| **SH-01** | 窗口材质（Mica） | 窗口层是**不透明实色**：`.nm-app` 背景 `--nm-bg-canvas`（#1B1B1B），页面再叠 `.nm-mica` = `#202020` + 2 个 radial-gradient 的**CSS 拟造**。桌面壁纸完全不可见。 | Figma「01 材质与动效」A 层：**Mica = 窗口底，能透出桌面壁纸**，「可选：`apply_mica` → 失败退实色 `#202020`」；00 概览亦承认画板壁纸是「拟造」，**真实实现取系统壁纸**。 | **P0** | **栈限制·有原生替代** | `tauri.conf.json:11-17` 无 `transparent`/`windowEffects`；Rust 全仓 grep `DwmsetWindowAttribute\|apply_mica\|windowEffects\|set_effects` = **0 命中**；`.nm-mica` 见 `base.css:113-118`。Tauri 2 自带 `window.setEffects({effects:{effects:[...]}})`，Windows 走 DWM，**不需要 Windows App SDK、不需要换栈**（与 Figma 结论「不引 Windows App SDK」不冲突）。 |
| **SH-02** | 材质层关系 | 因为窗口不透明，**浮层亚克力失去了可透的内容**：`.nm-acrylic` 背后是纯色 `.nm-mica`，blur(40px)+saturate(140%) 的视觉结果 ≈ 纯色 + 极轻噪声。截图里检查器/状态条与背景几乎同色，只有 1px 描边可辨。 | 「Acrylic 必须压在内容上，能透出**它下面的应用内容**」；「Mica 承担窗口底（透壁纸），Solid 承担内容区」。现状是三层里**两层塌成一层**。 | **P0** | **欠账** | `acrylic.css:27-46`（配方正确）但 `.nm-shelf/.nm-workbench/.nm-settings` 全部直接是 `.nm-mica` 实色（`Shelf.tsx:569`、`Workbench.tsx:255`、`reader-settings.css:82-86`）→ 浮层下面没有「内容层」，只有同一张底图。**修 SH-01 后此项自动缓解一半**，另一半需要把页面底改成「Mica 半透明 + 内容区 Solid」的两层结构。 |
| **SH-03** | 窗口 chrome（标题栏） | 应用内自绘 titlebar（48px）里的最小化/最大化/关闭是 **`<span aria-hidden="true">` 纯装饰**，不可点、无行为；同时 `tauri.conf.json` 没有 `decorations: false` → Tauri 默认**保留系统标题栏**。前端也**没有任何** `@tauri-apps/api/window` 调用（无 `startDragging`、无 `data-tauri-drag-region`）。 | Figma 每页 titlebar 右上角是 **12×12 极简窗口图标（无按钮底）**，与自绘壳一体；基线 §1.1 要求自定义 Shell。 | **P0** | **欠账**（真机复核见下） | `Shelf.tsx:605-613`、`Workbench.tsx:135-143`、`Reader.tsx:96-105`、`Settings.tsx:299-307`（全部 `aria-hidden`）；`tauri.conf.json:11-17` 无 `decorations`；前端 grep `getCurrentWindow\|startDragging\|drag-region` = **0 命中**。旧构建整窗实拍 `verification/P19-BOOT-1/ui-bookshelf-real-window.png` 显示**系统标题栏 + 应用自绘 titlebar 共存**（该图是 RC2 壳，与当前 v2 壳的配置面一致但**非同一构建 → 待真机复核**）。 |
| **SH-04** | 页面转场 | 四页之间**零转场**：`UiRoot.tsx` 用 `{activePage === "shelf" && <Shelf/>}` **条件渲染**，切页 = 卸载旧页 + 挂载新页，瞬间跳变。 | Figma 动效清单：浮层抽屉 250ms decelerate、Tab 切换 cross-fade 150ms、卡片→详情共享元素 300ms standard；基线 §1.2 冻结「**四页组件常驻挂载（keep-alive），切换仅改变可见性**」【08 AC-NAV-003】。 | **P0** | **欠账** | `UiRoot.tsx:174-201`；`base.css:420-429` 只有 reduced-motion 保护。全仓只有 1 个 `@keyframes`（`acrylic.css:105 nm-noise-drift`）。**现状连 keep-alive 都不满足基线**，所以「转场」缺少实现基座。 |
| **SH-05** | 动效清单覆盖率 | Figma「E · 动效清单」11 项，现状**已实现 1.5 项**：hover/按下 120ms `ease`（规范 100–150ms ease-out ✓，曲线不同）、噪声漂移 24s（规范 16s）、命令面板/批量条/抽屉/共享元素/状态切换全部**无动画**（`pages.css` 全文件仅 1 处 `transition`，见 :276）。 | 11 项逐项见 Figma「01 材质与动效」E 段。 | **P1** | **欠账** | `pages.css:276`（唯一 transition）；`acrylic.css:102`（24s vs 规范 16s）；`ui.css:145-154` 命令面板无进出动画；`base.css:193/309` 控件 120ms 合规。 |
| **SH-06** | 导航形态 | 一级导航是 **titlebar 内横向 4 个带图标 tab**（书架/工作台/阅读器/设置）。 | **基线 §1.1 冻结「左侧固定导航 Rail 64px（垂直图标+文字）」**；**Figma v2 改为 titlebar 内横向 3 个纯文字 tab + 数字 kbd（无图标），且无设置 tab**。**两个基准互相矛盾**，现状是第三种形态。 | **P1** | **设计源冲突**（+实现偏离） | 基线 §1.1；Figma S1 `titlebar/tabs`（`3:12`：3 tab，宽 79/91/77，无 icon 层）；现状 `pages.css:71-102` + `Shelf.tsx` titlebar。→ 建议 DSH 裁定「以 Figma 的横向 tab 取代基线 Rail」，否则实现必然继续夹在中间。 |
| **SH-07** | 真亚克力的光学质感 | CSS 合成：`blur(40px) saturate(140%)` + 单张 feTurbulence 噪声 + 单色 tint。**没有** WinUI Acrylic 的 luminosity 层、动态 tint、色散/边缘折射。 | Figma 00 概览「C · 已知限制」自认：「Figma 的 BACKGROUND_BLUR 只有半径，没有饱和/噪声参数；亚克力着色靠叠 acrylic/tint 实现，**与真机 WinUI Acrylic 有肉眼差距**」。 | **P2** | **栈限制（严格）** | `acrylic.css:27-46`；CSS 无「对背景做 luminosity blend」的能力（`mix-blend-mode: luminosity` 作用于同文档图层而非 backdrop）。**设计稿已明确选择仿制路线**（「结论：只做仿亚克力……不引 Windows App SDK」）→ 不应按此项要求换栈，最多加分项。 |
| **SH-08** | 窗口圆角 / 阴影 / 边框（OS chrome） | 窗口是直角矩形（系统 chrome）；应用内所有面板圆角 8px，但**外壳本身没有圆角**。切到无边框后若只靠 CSS，窗口四角仍是直角。 | Fluent/WinUI 3 应用的窗口是圆角 + 细边框；Figma 画板用 1px 外框暗示（`app-surface x=1 y=1 w=1600 h=1000`）。 | **P2** | **栈限制（严格）** | CSS 无法给 OS 窗口加圆角。原生可解：`DwmSetWindowAttribute(DWMWA_WINDOW_CORNER_PREFERENCE)`（Win11 22000+，但**只要无边框窗口 + 自定义 chrome 就必须显式调用**）。因设计稿未显式要求窗口圆角，降为 P2。 |
| **SH-09** | 窗口 UI 承载能力 | 现状只有单 WebView 单窗口。基线允许「悬浮窗可拖出主窗口/双屏/可调大小」（§1.1、§3.6-16）。 | 基线 §1.1 悬浮窗规则；Figma 材质页明示「**不做多窗口**」。 | **P2** | **栈限制·有原生替代** | 基线要求与 Figma「不做多窗口」冲突；Tauri 2 支持多 WebviewWindow（`WebviewWindowBuilder`），现状 Rust 侧**没有任何窗口创建代码**（grep `WebviewWindow\|WindowBuilder` = 0 命中）。→ 先由 DSH 裁定是否需要，再谈实现。 |
| **SH-10** | 深色模式 | 现状 dark/light 两套令牌齐备，`tokens.css` 有 `data-theme` 双主题，titlebar 有主题切换按钮。 | **基线 §8.1 明示「深色模式不在本基线范围（无 REQUIREMENT 来源，如引入属新需求决策）」**；Figma 反而每面都做了黑夜+白天两版。 | — | **设计源冲突**（已实现超出基线，无需修） | `tokens.css:70-164`、`UiRoot.tsx:162-169`。仅登记：**深色是 Figma 主张、基线未授权**，当前实现站在 Figma 一侧，属既成事实。 |

### 2.2 材质三层落位对照（便于裁决「要不要碰窗口层」）

| 层 | Figma 规定 | 现状 | 差距 |
|---|---|---|---|
| **Mica**（窗口底，透壁纸，整屏一次） | 原生 backdrop 或退 `#202020` | 无原生，退化成纯色 + 2 个 radial-gradient 高光 | **P0**（SH-01） |
| **Acrylic**（浮层，透应用内容） | blur 40/24 + saturate 140% + tint + 噪声 8% hard-light + 1px 描边 + 顶部高光 | **配方逐项正确**（`acrylic.css`），还有 ≤2 层预算与 3 条降级链（比设计更完整） | 配方 ✓ / 可透内容 ✗（SH-02） |
| **Solid**（内容区） | 纯色零模糊 | 卡片/面板用 `--nm-bg-card`/`--nm-bg-layer` | ✓ 基本符合 |

---

## 3. 书架（Shelf）

### 3.1 现有实现骨架

`.nm-shelf(.nm-mica)` → `.nm-titlebar`(48) → `.nm-toolbar`(48) → `.nm-shelf__main`(flex) = `.nm-shelf__library`(flex:1, overflow:auto) + `.nm-detail`(340 固定) → `.nm-floating-status`(底部)。见 `pages.css:18-29/215-233/393-403`。

### 3.2 差距表

| ID | 维度 | 现状 | 设计基线 / Figma | 严重度 | 判定 | 依据 |
|---|---|---|---|---|---|---|
| **SB-01** | 信息密度 / 栅格 | `.nm-book-grid` 是 `repeat(5, 168px)` + gap 16 = **904px 固定宽度**；1280 视口下库区只有 `1280-32-16-340 = 892px` → **网格溢出 12px**，`.nm-shelf__library` 会出横向滚动条；同时列宽固定，卡片不会随容器拉伸。 | Figma S1：5 列**等分** 1212px 容器（`row/0` 卡片 x=0/261/522/783/1044，pitch 261 = 168 卡 + 93 视觉间距），即「列宽随容器铺满」。 | **P1** | **欠账** | `pages.css:259-265`；库区宽度来自 `pages.css:215-233` + `.nm-detail` 的 `flex: 0 0 340px`（:397-398）。**静态推导；1280 截图只有 1 本书，滚动条未实际可见 → 待真机确认溢出**。 |
| **SB-02** | 图标与图形 / 封面 | 无封面图时用 **竖排书名压在封面上**：`writing-mode: vertical-rl`、22px、`width: 1.1em`、`top:34/left:12`，外加 8px kicker、9px volume、wash 渐变与网点。长书名直接溢出被裁（900/1280 截图均可见「端到端验收-659134」竖排溢出版面）。 | Figma S1 封面**只有左上角编号（01–15）+ 渐变色块**，无书名、无 kicker；书名在封面**下方**（`.nm-book-title` 位置），meta 为「5 话 · 23 页」+ 状态点。 | **P1** | **欠账** | `pages.css:290-358`；对照 Figma `3:83 bookcard`（cover 168×222 + body 40 + pad 27，cover 内仅 `text "01"`）。 |
| **SB-03** | 状态与文案 | `page_count` 为 null 时显示 **「页数未知」**（20px title 字号下换行成两行，观感差）。 | **基线 §2.3 明文：「`page_count` 为 null 时显示「—」，不得渲染为 0」**。 | **P1** | **欠账** | 现状文案见 900/1280 截图右侧详情面板；基线 §2.3 BookCard 行；`.nm-stat__value` 用 `--nm-text-title`（`pages.css:478-481`）导致换行。 |
| **SB-04** | 材质与层级（详情面板） | 右侧详情是**带边框 + 圆角 + 亚克力底**的独立卡片（`.nm-detail` + `.nm-acrylic`），与外层 Mica 之间靠 1px 边和色差分隔。 | Figma S1：详情面板 **340px、无外框、直接铺在画布上**（分隔只靠留白与字号层级），主/次按钮为实心/描边两档。 | **P2** | **欠账** | `pages.css:393-403`；`DesignPreview.test.tsx:67` 证实 `shelf-detail` 挂 `.nm-acrylic`。 |
| **SB-05** | 间距与栅格 | 卡片内 padding `10px 12px 12px`，meta 行 `gap 4px`；卡片**有 1px 边框**（`--nm-line-control`），hover 上浮 2px + elevation-8。 | Figma 卡片**无边框**（仅圆角封面 + 底部 3px 进度条），hover 未在静态稿体现；间距规范 16/12/8/4（现状合规）。 | P2 | **欠账（轻）** | `pages.css:267-288`、`359-364`。**是否保留 hover 上浮待设计确认**（Figma 无条件态画板 → 未覆盖，不判）。 |
| **SB-06** | 材质与层级（状态条） | 底部 `.nm-floating-status` 是 48px 亚克力条，内容「完成 · Core 在线 … · Core ready · 1 部作品」。 | Figma S1 底部是**浮动亚克力批量条**（`bulk-bar` 1568×48，Elevation 8），内容是「6 部作品 · 286 页 · 完成 16 · 失败 2 · 过期 1 + 右侧进度」。 | **P1** | **欠账** | `pages.css:571-596`；Figma `7:1472 bulk-bar`（该条只在 S5 批量态与 S1 右下出现）。现状把「运行状态」塞进书架状态条，与 Figma 的「藏书统计 + 批量操作」语义不同。 |
| **SB-07** | 状态与文案（开发者语） | 状态条与空态直接暴露内部概念：**「来自 Core 的最新读取」「Core 在线」「Core ready」**。 | 基线 §8.2 要求用户向文案；Figma 无 Core 概念。G16 虽登记「Core 可用性指示」为缺口，但缺口不等于可以把内部术语原样上屏。 | **P1** | **欠账** | 900/1280 截图；`Shelf.tsx` 状态条区（`data-testid` 见 NARROW-1 断言，文案在组件内）。 |
| **SB-08** | 内容 / 骨架 | 库区只有 1 张卡时，网格仍是 5 列 168px 固定 → **右侧大片空白**，看起来「不是书架而是空壳」。 | Figma 用 15 张卡填满 3 行。这是数据量差异，**不是设计差距**；但 grid 固定列宽让空数据情形放大成观感缺陷（见 SB-01）。 | P2 | 数据状态（不判欠账） | 截图；`pages.css:259-265`。 |
| **SB-09** | 动效 | 卡片 hover 有 140ms `ease` 上浮 + elevation-8；其余（进入页面、详情切换、章节行）无动效。 | Figma：悬停/按下 100–150ms ease-out；卡片→详情**共享元素 300ms standard**。 | P1 | **欠账** | `pages.css:276-283`；共享元素需 View Transitions（`document.startViewTransition`）→ WebView2 版本支持**待验证**，见 §11 第 3 项。 |
| **SB-10** | 圆角/阴影一致性 | 圆角只用 8/4/2/0 四档 ✓；阴影只用 elevation-8/16 ✓；但 `.nm-book-cover` 用 `linear-gradient(155deg, …)` 造封面——Figma 也用渐变，此项一致。 | — | — | ✓ 合规 | `tokens.css:52-68`、`pages.css:290-298`。登记为「已对齐」样本，供 AC6 估算「已达标比例」。 |

### 3.3 书架结论

书架的**令牌层（颜色/字阶/圆角/阴影/间距）已基本对齐**，差距集中在三处：① 网格列宽策略（固定 168 vs 等分）造成 1280 下 12px 溢出与空库观感；② 封面 fallback 自创「竖排书名压在封面上」这一表现手法，Figma 没有；③ 详情面板/状态条把内部概念（Core）与语义错位（状态条显示运行状态而非藏书统计）搬上屏。**全部为欠账，无栈限制。**

---

## 4. 工作台（Workbench）

### 4.1 现有实现骨架

`.nm-workbench(.nm-mica)` → `.nm-titlebar` → 工具栏（含折叠的 PageList 竖条）→ `.nm-canvas`(flex) + `.nm-inspector`(nac 320 + rail 48) → `.nm-floating-status`(44 折叠)。`.nm-filmstrip` 有样式（72px）但窄窗下折叠为 24px 竖条。

### 4.2 差距表

| ID | 维度 | 现状 | 设计基线 / Figma | 严重度 | 判定 | 依据 |
|---|---|---|---|---|---|---|
| **WB-01** | 信息密度（PageList） | 900 视口下 PageList **折叠成约 24px 竖条 + 工具栏里的一个「书架 / 第1话 · …」下拉**；1280 下仍不展开为 240 固定列（截图中只有折叠条）。 | 基线 §3.2 冻结：PageListPanel **240px 固定（可调 200–320）**，且 §1.3 明确「布局**不提供 < 1024 的降级形态**（低于最小尺寸由窗口系统阻止）」。Figma W1：**72px 胶片条（filmstrip）+ 9 个 52×72 缩略项**。 | **P0** | **欠账** | `pages.css:740-830`（filmstrip 样式存在）；截图 900 工作台左侧只有 ~24px 竖条；窄断点见 `pages.css:1500-1508`（仅覆盖 `.nm-book-grid`）。→ 三个基准（基线 240 / Figma 72 / 现状 24 折叠）**都不一致**，需 DSH 裁一个。 |
| **WB-02** | 图与图形（缩略图） | PageList 与检查器**没有页缩略图**，缩略位画「未知占位」而非假图案（作者注释已声明「Core 没有缩略图通道」）。 | Figma W1 胶片条每项都有 52×52 缩略图；基线 §3.3 要求 PageList 显示页序/文件名/状态，缩略图登记为 **G18 缺口**。 | P1 | **欠账（受 G18 wire 缺口约束）** | `Workbench.tsx:546`、`:1053` 注释；基线 §7 G18。→ 属「先冻结缩略图通道再实现」，**不是视觉欠账的全部**：可以用「页序大字 + 状态色」做出 Figma 同级的信息密度（不依赖 wire）。 |
| **WB-03** | 状态与文案（开发者语） | 检查器卡片直书：**「当前 IPC 未返回 OCR 文本与置信度」**；空态与阻塞卡片把 wire/协议词汇上屏。 | 基线 §5.4/§8.2：错误与空态用**本地化短文案 + 可采取动作**，不暴露 code/路径/协议。Figma W1 检查器：kv 结构「原文（OCR）0.94 / 机器译文 / 人工译文 / 最终译文」。 | **P0** | **欠账** | 900 工作台截图「识别结果 → 未识别 → 当前 IPC 未返回 OCR 文本与置信度」；`Workbench.tsx:546` 注释同源。 |
| **WB-04** | 材质与层级（检查器） | 检查器 = 48 rail + 320 面板，**面板内每块是带边框/底的卡片**（识别结果卡、运行卡），层级靠卡片边界。 | Figma W1：**361 检查器（rail 48 + pane 312）无卡片边界**，用分隔空行 + kv 行（label 12px 三级灰 + value 14px 主色）+ 一个实心「确认 Enter」按钮；层级靠留白与字重。 | **P1** | **欠账** | `pages.css:919-1010`（`.nm-inspector` + `.nm-inspector__section` + `.nm-kv`）；Figma `9:222 insp-pane`。 |
| **WB-05** | 信息密度（工具条 / 状态带） | 工具栏信息被压缩为「书架 / 章节 / OCR 图标 / 阅读器」。底部是 **44px 折叠条**（仅「尚未开始运行」+ 展开钮）。 | Figma W1：toolbar 48 内是「文件名 + 单页/批次 segmented + 本章·23页 下拉 + 暂停 + 阅读此页」；**底部 band 40 常驻 10 阶段流水线 dot + step 5/10 + 进度条 + 完成18/失败2 + 停止/任务**。基线 §3.5 要求 TaskProgressPanel 固定底部、折叠 44 / 展开 220，且**折叠态要保留任务名/百分比/当前页/当前 Step/控制钮**。 | **P1** | **欠账** | 截图底部条只有一行文字；`pages.css` 有 `.nm-pipeline`（1126-1187）但未被渲染到折叠态；基线 3.5 折叠态要求。 |
| **WB-06** | 状态与空态 | 空态是居中 `.nm-state` 卡（实色 layer + 边框 + 图标方块 + 标题 + 说明），内容偏解释性。 | Figma 无空态画板（假设有数据）。基线 §3.4 empty：`ListChapterPages` 空 → 「引导导入 + 主行动作」；`ListRegions` 空 → Overlay 提示「本页暂无 Region」。 | P2 | **欠账（弱）** | `ui.css:32-80`（`.nm-state` 统一样式，全站复用）。→ 样式合规，**缺的是「主行动作」按钮与差异化文案**（截图空态卡确实没有「导入页面」按钮）。 |
| **WB-07** | 动效 | 工作台内无任何动画：抽屉/批处理条/进度条都瞬切；进度条 `width` 无 transition。 | Figma：批量条出现 `translateY 12→0 + opacity` 200ms decelerate；进度变化 `width` ≤200ms linear；浮层抽屉 250ms。 | P1 | **欠账** | `pages.css` 无相关 transition；`base.css:386-400 .nm-progress` 无 transition。 |
| **WB-08** | 圆角与阴影 | 画布/检查器/卡片全部 8/4/2 四档 ✓；`page-surface` 用 elevation-16。 | Figma 同。 | — | ✓ 合规 | `tokens.css:52-68`；`pages.css:1189+`。 |

### 4.3 工作台结论

工作台的**骨架结构已接近基线**（标题栏/工具条/画布/检查器 rail/底部条都在），差距集中在：① PageList 在窄窗被折叠成 24px 竖条，三基准互不一致（P0，需裁决）；② 检查器把「IPC/协议」这类内部词直接上屏，且用卡片墙代替 Figma 的 kv 堆叠（P0/P1，纯欠账）；③ 底部流水线带在 idle 时退化为一行文字，丢失基线要求的折叠态信息（P1）；④ 无任何进度/批量条动效（P1）。

---

## 5. 阅读器（Reader）

### 5.1 现有实现骨架

`.nm-reader(.nm-mica)` → `.nm-titlebar`（**完整应用标题栏：4 tab + 搜索 + 窗口按钮**）→ `.nm-reader__body` → `.nm-reader__page-area`(padding 88/96/72) + `.nm-reader__top`(48 浮层, acrylic-24) + `.nm-reader__bottom`(40 浮层) + 左右 `.nm-reader__nav`(36×64, opacity .82) → 底部状态。见 `pages.css:1330-1475`。

### 5.2 差距表

| ID | 维度 | 现状 | 设计基线 / Figma | 严重度 | 判定 | 依据 |
|---|---|---|---|---|---|---|
| **RD-01** | 布局（沉浸度） | 阅读器**保留完整应用标题栏**（48px 含 4 tab + 命令胶囊 + 窗口按钮），下面再有 48px 阅读浮层 —— **两层 chrome 共 96px**，占 700 高视口的 13.7%，阅读区被压缩。 | **Figma R1/R2/R3 是全景沉浸式**：没有 titlebar，只有 48px 浮层（左「← 返回 / 第12话·雨の停車場 / 007-23 / ●已确认」，右「分页 纵向 原文 译文 双语 RTL右开」）。**但基线 §4.2 要求「Nav Rail 64px + ReaderToolbar 48」**。 | **P0** | **设计源冲突** | 900 阅读器截图顶部 titlebar；`pages.css:1371-1383`；Figma R1 缩略图。→ 需要 DSH 裁决「阅读器是否进入沉浸模式（隐藏 titlebar）」。**在此之前不应按任一基准改。** |
| **RD-02** | 排版与字号（工具栏） | 顶部浮层里章节/页码未就绪时显示 **「— · —」与「—/—」** 两个破折号占位（截图中极显眼）。 | Figma 工具栏永远有值（`007 · 23`）；基线 §4.2 空状态要求「尚未选择阅读章节 + 选择入口」，不应显示裸破折号。 | **P1** | **欠账** | 900 阅读器截图左上「← — · — —/— ▭」；`pages.css:1385-1412`。 |
| **RD-03** | 圆角与阴影 / 翻页热区 | 左右翻页按钮是 **36×64 圆角 8 的按钮，贴在视口边缘（left/right 16px）**，`opacity: .82`、`background: --nm-bg-layer`（实色，非亚克力）。 | Figma：**32×64 箭头贴在页面左右两侧**（距页面约 20px），默认很淡、hover 才实，且不抢页面焦点。 | **P1** | **欠账** | `pages.css:1418-1447`；Figma R1 缩略图可见箭头紧贴页面而不是视口边缘。 |
| **RD-04** | 材质与层级（浮层） | 顶/底浮层已用 `.nm-acrylic-24`（**配方正确**），但背后是 `.nm-mica` 纯色 → 看不到模糊（同 SH-02）。 | Figma R1 顶/底浮层在深灰画布上能透出页面边缘与画布色差。 | **P1** | **欠账（同 SH-02 根因）** | `pages.css:1371-1383/1449-1461`；`Reader.tsx` 用 `useAcrylicBudget` 挂 `nm-acrylic-24`（`Reader.test.tsx:310/368` 断言）。 |
| **RD-05** | 状态与空态 | 空态卡：「该章节暂无页面 / 导入验收章节-62057 还没有可阅读页面：请先在书架或工作台导入页面。」+「返回书架」实心按钮。文案里带**内部章节名（导入验收章节-62057）**。 | Figma R? 无空态画板。基线 §4.2：空态为「尚未选择阅读章节 + 选择入口」；错误/空态文案不得暴露内部标识。 | P2 | **欠账（弱）** | 900 阅读器截图。 |
| **RD-06** | 信息密度（底部） | 底部 40px 浮层只有「本话进度 —」+ 两个小按钮「←|→ 翻页」。 | Figma R1 **没有底部条**（只有顶栏 + 左右箭头）；基线 §4.2 只要求工具栏含位置显示。 | P2 | **设计源冲突（轻）** | 截图；`pages.css:1449-1466`。→ 与 RD-01 一并裁决：沉浸模式下可删底部条。 |
| **RD-07** | 动效（翻页） | 翻页是瞬时替换（无淡入/滑动）；长条滚动无惯性/位置提示动画。 | Figma 动效清单未定义翻页动画（只有「状态切换 0ms」）；基线未要求翻页动效 → **设计依据不足**。 | P2 | **待验证/不判** | `pages.css:1330-1475` 无 transition。→ 建议列入「体验增强」，不属于「补齐设计」。 |
| **RD-08** | 字号与字阶 | 阅读器内文字基本用 caption(12)/body(14)/body-strong(14)；页码等用 `.nm-data`(12 mono) ✓。 | Figma 同（Data 12/16 mono）。 | — | ✓ 合规 | `tokens.css:42-50`。 |

### 5.3 阅读器结论

阅读器的问题**不是材质**（浮层配方正确），而是**结构**：它把「应用外壳」和「阅读浮层」叠在一起，而 Figma 的阅读器是**沉浸式全屏**（无 titlebar）、基线是**左 Rail 常驻**。这是本次唯一需要**产品裁决**而非实现修复的页面级冲突（RD-01）。其余（破折号占位、箭头位置、空态文案）都是欠账。

---

## 6. 设置（Settings）

> **降级提醒**：Figma **没有设置页画板**。本节基准 = `AD001` §5（布局/组件/状态矩阵）+ §8 令牌 + Figma「01 材质与动效」的通用规范。**没有视觉稿可比对**，故本节只判「与基线/规范的一致性」与「明显的产品化缺陷」，不判「与视觉稿的像素差异」。

### 6.1 现有实现骨架

`.nm-settings`（Mica 底 + 2 radial）→ `.nm-titlebar`（完整应用标题栏）→ `.nm-settings__body` = `.nm-settings__nav`（200px + acrylic）+ `.nm-settings__content`（padding 24，滚动）→ 面板卡（`.nm-settings__panel`）。见 `reader-settings.css:75-207`。

### 6.2 差距表

| ID | 维度 | 现状 | 设计基线（无 Figma 稿） | 严重度 | 判定 | 依据 |
|---|---|---|---|---|---|---|
| **ST-01** | 状态与文案（开发者语） | 内容头右侧显示 **「section · provider」**；左下角 **「settings_get 已同步」**、**「SFX 策略 · 未设置（按 Core 默认）」**；「Capability 默认绑定」说明里出现 **`StartRun.overrides.provider_profiles`**、**「scope 范围」下拉**、**「要绑定的 profile_id」/ placeholder「ProfileId」**、按钮 **「设置绑定 (set)」/「清除绑定 (clear)」**。整页读起来像**调试面板**。 | 基线 §5.3/§5.4/§8.2：设置是产品页，文案本地化、面向用户；`G21/G22/G23/G25` 未冻结的分区应呈现为**禁用 + tooltip「等待能力接入」**，而不是把 wire 字段名做成表单。 | **P0** | **欠账** | 900 设置截图；`Settings.tsx:217/228/353/357/370`（`settings_get 已同步`、`section · ${activeSection}`、`SFX 策略 · 未设置（按 Core 默认）`、`settings_get · 读取 sfx 分节做通道探针`）。 |
| **ST-02** | 信息密度 | 单页 12 分类（顺序正确 ✓），但内容区把「未实现的 Provider/Capability/绑定」做成了**可交互下拉 + 输入框 + 两个按钮**，用户会以为能用；实际没有 wire（G21/G22/G23）。 | 基线 §5.4 disabled：无 wire 的分区**分类可见但内容为占位说明 + 灰置**，不得假装可用。 | **P0** | **欠账** | 截图（下拉 + 输入框 + set/clear 按钮均为可点样式）；基线 §7 G21/G22/G23/G25。 |
| **ST-03** | 排版与字号 | 内容标题「Provider」用 display? 截图看约 20–24px 且与右上元数据同行；面板卡用实色 `--nm-bg-layer` + 1px 边 + 圆角、卡内说明文字为 caption 灰。 | 基线 §8.2：面板/空状态标题 18（600）；caption 11。Figma 材质页 D 段：Title 20/28、Body 14/20、Caption 12/16。 | P2 | **欠账（轻）** | `reader-settings.css:171-207`；截图。→ 字号体系基本在规范内，**偏差在于「区块标题与元数据同行」的排布**。 |
| **ST-04** | 材质与层级 | 左侧 200px 导航是 `.nm-acrylic`（浮起 8px 圆角 + 外边距，v2 语言）✓；内容面板用实色 layer 卡。 | 基线 §5.2：「SettingsCategoryNav 200px 固定」✓；材质按 Figma「浮层用 acrylic / 内容用 solid」分层 ✓。 | — | ✓ 合规（少见的对齐样本） | `reader-settings.css:96-108`；`Settings.tsx:46-47/149`（预算降级注释）。 |
| **ST-05** | 状态与空态 | 「暂无 Provider Profile。」空态文案 ✓；但空态没有**主行动作的可用性说明**（旁边「新建 Profile」按钮实际无 wire）。 | 基线 §5.4 empty/disabled 组合：空 + 不可用要解释为什么。 | P1 | **欠账** | 截图；基线 §5.4。 |
| **ST-06** | 导航守卫 / chrome | 设置页同样带完整应用 titlebar（4 tab + 搜索 + 假窗口按钮）→ 与 Figma「3 tab」和基线「Rail 64」都不一致（同 SH-06）。 | — | P1 | **设计源冲突**（同 SH-06） | 截图；`Settings.tsx:299-307`。 |
| **ST-07** | 是否需要「保存」模型 | 现状多数控件是即时 set/clear 按钮；基线 §5.5-3 要求「其他节键用『保存』按钮整节提交」。 | 基线 §5.5。 | P2 | **待验证**（需先确定哪些节真的开放） | `Settings.tsx`；基线 §5.5。→ 与 ST-01/02 同根：先定「哪些节是产品化的」，再定保存模型。 |

### 6.3 设置结论

设置页是四页里**产品化程度最低**的一页：令牌/材质/200px 导航都合规，但**内容层把内部契约（IPC 命令名、wire 字段、section 标识）直接做成了 UI**，在 Figma 完全缺位的情况下自行发明了表单。这是「用户第一眼觉得像半成品/调试工具」的直接原因，且**全部是欠账**（没有一条受栈限制）。

---

## 7. 栈限制专项（含替代路径）

> 全表共 43 条，其中 **栈限制 4 条**：严格 2 条（SH-07、SH-08）+ 有原生替代 2 条（SH-01、SH-09）。
> **没有任何一条构成「换 UI 栈」的充分理由。**

| ID | 主判定 | 栈限制内容 | 为什么 CSS/WebView2 做不到 | **栈内替代路径（不需换栈）** | 成本 |
|---|---|---|---|---|---|
| **SH-01** | **栈限制·有原生替代** | 窗口 Mica（透出桌面壁纸） | `backdrop-filter` 只能采样**同文档**内容，无法采样窗口后的桌面；`.nm-mica` 只能是纯色 + 渐变 | **Tauri 2 `window.setEffects` / `tauri.conf.json → app.windows[].windowEffects`**：Windows 上支持 `mica`/`micaDark`/`micaLight`/`acrylic`/`tabbed`，走 DWM，不引 Windows App SDK。配合 `transparent: true` + 页面背景改为半透明（`--nm-bg-mica` 用 alpha），失败时按 Figma F 段降级到 `#202020`。**Figma 已写明「可选：apply_mica → 失败退实色」**，即设计预期就是要接这条原生通道。 | **低**（Rust/配置 ~30 行 + 一处背景令牌）+ 需处理「透明窗口下的文字对比度」回归 |
| **SH-02** | **欠账**（SH-01 的下游） | 亚克力没有可透内容 | Mica 不生效时，`backdrop-filter` 的输入是一张纯色图，模糊不可见 | 修 SH-01 后自动成立；另需把页面底从「整页 mica 实色」改为「**Mica 半透明底 + 内容区 Solid**」的两层结构（Figma A 段「Solid：内容区，什么都不透」） | **低-中**（CSS 分层重构 + 各页底改 `transparent`） |
| **SH-07** | **栈限制（严格）** | 真 WinUI Acrylic 的 luminosity/色散 | CSS 无「对 backdrop 做 luminosity blend」能力；`mix-blend-mode: luminosity` 只作用于图层自身与兄弟层 | ① 接受仿制（Figma 已选）；② 增强配方：双层噪声（粗细各一层）+ 顶部/底部双高光 + 噪声漂移 16s（对齐规范）；③ 若要真效果，只能原生（Windows App SDK AcrylicBrush 或 DWM acrylic），**但设计明示「不引 Windows App SDK」** | 低（②） |
| **SH-08** | **栈限制（严格）** | OS 窗口圆角/边框/阴影 | CSS 不能改 OS 窗口几何 | `DwmSetWindowAttribute(DWMWA_WINDOW_CORNER_PREFERENCE, DWMWCP_ROUND)`（Win11 22000+）或 `tauri-plugin-window-state` 类插件；无边框窗口需自行处理 resize 热区 | 中 |
| **SH-09** | **栈限制·有原生替代** | 多窗口悬浮窗（可拖出主窗/双屏） | 浏览器单窗口模型下 CSS 无法创建 OS 窗口 | Tauri 2 `WebviewWindowBuilder` 可建多 WebView 窗口；**但 Figma 材质页明示「不做多窗口」，基线 §1.1 要求可拖出** → 先裁决再实现 | 中-高 |

**已排除的伪「栈限制」**（常被误当成换栈理由，实际都是欠账）：

| 观感问题 | 为什么不是栈限制 |
|---|---|
| 页面切换生硬 | CSS `transition`/`animation` + React 常驻挂载完全够；WebView2 也支持 View Transitions（版本相关 → RD-09 待验证） |
| 浮层/抽屉没有进出动画 | 纯 CSS，无需任何新能力 |
| 控件 hover/按下反馈弱 | 已有 120ms transition，只是覆盖面窄 |
| 卡片/面板边框过多、层级靠线 | 纯 CSS 设计问题 |
| 字排/竖排漫画封面裁切 | 纯 CSS（现状是自创表现手法） |
| 亚克力噪点不够「真」 | 已有 feTurbulence，可调 `baseFrequency`/`numOctaves`/opacity（规范给了 0.35/0.5/0.8 三档与 0.03/0.055/0.08 三档） |
| 双标题栏 | Tauri `decorations:false` + `startDragging`，标准能力 |

---

## 8. 「只改 5 处，收益最大」清单

排序依据 = **观感收益 ÷ 工作量**（收益按「P0 条数消除 + 全站视觉影响面」，工作量按改动文件数与人日粗估）。

| # | 改动 | 消除的条目 | 为什么收益最大 | 工作量 |
|---|---|---|---|---|
| **1** | **接上窗口 Mica**：`tauri.conf.json` 加 `transparent: true` + Rust `window.set_effects(Mica)`（Win11 22621+，失败降级实色），并把 `.nm-app`/页面底改为半透明 | SH-01、SH-02、RD-04 | **一次性激活全站所有浮层亚克力**。现状配方 100% 正确却因为「底下是纯色」全部失效；这一改让「材质」从 0 分到 70 分，且改动面极小（配置 + 1 处 Rust + 2 个 CSS 令牌） | **0.5–1 人日**（含对比度回归） |
| **2** | **设置页去技术化**：删掉 `section · xxx` / `settings_get 已同步` / `StartRun.overrides.*` / `profile_id`/`ProfileId` / `(set)`/`(clear)`；无 wire 分区改「灰置 + 等待能力接入」占位 | ST-01、ST-02、ST-05 | 设置页是「像调试面板」的重灾区，**纯文案与禁用态改动、零架构风险**，观感提升立竿见影 | **0.5–1 人日**（纯前端） |
| **3** | **四页改 keep-alive + 150–250ms cross-fade 转场**：`UiRoot` 改为四页常驻、`data-active` 切可见性，用 opacity/transform 做转场（含 `prefers-reduced-motion` 归零） | SH-04（并顺带满足基线 §1.2 的冻结语义）、SH-05 部分 | 同时解决「生硬跳变」与「切页丢状态/重复拉取」两个问题；是**基线明文要求**而非锦上添花 | **1–2 人日**（需回归四页状态保留 + 资源重新签发） |
| **4** | **窗口 chrome**：`decorations:false` + titlebar 加 `data-tauri-drag-region` + 三个窗口按钮改真 IPC（min/max/close）+ 双击最大化 | SH-03 | 消除「系统标题栏 + 假窗口按钮」的双层 chrome，这是**第一眼的「不像正经应用」**来源 | **1 人日**（含高 DPI/最大化/还原回归） |
| **5** | **书架视觉对齐**：grid 改等分列（`repeat(5, minmax(0,1fr))` + 卡片 aspect 保持）、封面去掉竖排书名改 Figma 的「编号 + 渐变」、`page_count=null` 显示「—」、状态条改藏书统计语义 | SB-01、SB-02、SB-03、SB-06 | 书架是启动默认页，也是唯一有完整 Figma 画板（S1/S2/S3/S4/S5）可对齐的页面；四项都是小改动但密集改善 | **1–1.5 人日** |

> 不入选但值得排下一批：WB-01（PageList 三基准裁决）、WB-03（工作台 IPC 文案）、RD-01（阅读器沉浸式裁决）、SH-05 动效全表补齐。

---

## 9. 现状截图索引（断言点）

来源：`verification/UIUX-V2-RUNTIME-NARROW-1/run-i3-shots/`（NARROW-1 产出，本报告只读引用，未复制）。
全部为 **DPR2**，即物理像素 = 2 × CSS 逻辑像素。

| 文件 | 页面 | 视口(CSS) | 物理尺寸 | 本报告使用的断言点 |
|---|---|---|---|---|
| `11-900x700-dpr2-shelf.png` | 书架 | 900×700 | 1800×1400 | 无壁纸/无 Mica 透出；详情面板 340 卡片化；封面竖排书名溢出；「页数未知」换行；「来自 Core 的最新读取」；「Core 在线 / Core ready」；标题栏 4 tab + 假窗口按钮 |
| `11-900x700-dpr2-workbench.png` | 工作台 | 900×700 | 1800×1400 | PageList 折叠为 ~24px 竖条；检查器「当前 IPC 未返回 OCR…」；无 banner；底部 44 折叠条仅一行 |
| `11-900x700-dpr2-reader.png` | 阅读器 | 900×700 | 1800×1400 | titlebar + 阅读浮层双层 chrome；「— · —」「—/—」破折号占位；翻页箭头贴视口边缘且低对比；底部 40 浮层 |
| `11-900x700-dpr2-settings.png` | 设置 | 900×700 | 1800×1400 | 「section · provider」「settings_get 已同步」「StartRun.overrides…」「profile_id/ProfileId」「设置绑定 (set)」；200px 亚克力导航（合规样本） |
| `11-shelf-900x700-dpr2.png` | 书架（S10 详查副本） | 900×700 | 1800×1400 | 与上同；用于交叉核对标题栏/库区/详情不重叠 |
| `12-1280x800-dpr2-shelf.png` | 书架 | 1280×800 | 2560×1600 | 5 列固定 168 网格：库区 892 vs 网格 904（SB-01 静态推导源）；详情面板 340 位置；内容右边界实测 x=2526px(=1263 CSS)，确认无右侧留白异常 |
| `12-1280x800-dpr2-workbench.png` | 工作台 | 1280×800 | 2560×1600 | PageList 仍折叠；画布空态；检查器卡墙 |
| `12-1280x800-dpr2-reader.png` | 阅读器 | 1280×800 | 2560×1600 | 双层 chrome；居中空态卡 |
| `12-1280x800-dpr2-settings.png` | 设置 | 1280×800 | 2560×1600 | 内容区滚动；下拉/输入框可用样式 |

另有 4 张 `11-core-recovered-*.png`（Core 恢复态）与 1 张 `11-core-*`，本报告未使用（属状态矩阵另一支，与本任务「材质/布局/动效」命题无关）。

**Figma 参考截图副本**（本报告新增，便于复核，均为只读下载）：

| 文件 | 来源 nodeId | 用途 |
|---|---|---|
| `figma-ref/S1-shelf-dark.png` | `3:2` | 书架视觉基准（5 列等分 / 无边框卡 / 详情面板无外框 / 窗口控件 12×12） |
| `figma-ref/W1-workbench-dark.png` | `9:2` | 工作台视觉基准（72 胶片条 / 505×764 页面 / 361 检查器 kv 堆叠 / 40 流水线带 / BLOCK banner） |
| `figma-ref/R-pages-reader.png` | `1:6` | 阅读三画板缩略（沉浸式无 titlebar / 48 浮层 / 32×64 贴页箭头） |

---

## 10. 复核方法与自证

### 10.1 本报告未改任何产品文件

```powershell
cd "G:/CODEX/New Manga"
git status --short
# 预期：只多出 verification/DISPLAY-PERF-DECISION-1/visual/（本报告 + figma-ref/*.png）
# 以及他人在改的 doc/REBASELINE_PLAN.md、doc/STATUS.md、doc/TASK_LEDGER.md、doc/tasks/DISPLAY-PERF-DECISION-1.md（非本 agent 所为）
```

### 10.2 关键结论的可重跑命令

```powershell
# 1) 窗口层无原生材质（无 DWM / windowEffects）
Get-ChildItem 'apps/desktop/src-tauri/src' -Recurse -Filter *.rs | Select-String 'DwmSetWindowAttribute|set_effects|windowEffects|apply_mica'
Get-Content 'apps/desktop/src-tauri/tauri.conf.json'   # 无 transparent / decorations / windowEffects

# 2) 前端无窗口 chrome API、窗口按钮是装饰 span
Get-ChildItem 'apps/desktop/frontend/src' -Recurse -Include *.ts,*.tsx | Select-String 'getCurrentWindow|startDragging|drag-region|setDecorations'
Select-String -Path 'apps/desktop/frontend/src/pages/Shelf.tsx' -Pattern 'nm-window-btn' -Context 0,2

# 3) 全仓动效总量（只有 1 个 keyframes）
Get-ChildItem 'apps/desktop/frontend/src' -Recurse -Include *.css | Select-String '@keyframes|animation:|view-transition'
Select-String -Path 'apps/desktop/frontend/src/pages/pages.css' -Pattern 'transition|animation'

# 4) 页面切换不是 keep-alive
Select-String -Path 'apps/desktop/frontend/src/ui/UiRoot.tsx' -Pattern 'activePage ==='

# 5) 设置页技术文案
Select-String -Path 'apps/desktop/frontend/src/pages/Settings.tsx' -Pattern 'section ·|settings_get|StartRun|profile_id|ProfileId'

# 6) 书架网格固定 5×168（1280 下库区 892 → 溢出 12px）
Select-String -Path 'apps/desktop/frontend/src/pages/pages.css' -Pattern 'repeat\(5, 168px\)|flex: 0 0 340px'

# 7) 亚克力配方与预算（证明实现正确、问题在窗口层）
Get-Content 'apps/desktop/frontend/src/design/acrylic.css'
Get-Content 'apps/desktop/frontend/src/design/useAcrylicBudget.ts'
```

### 10.3 Figma 复核说明

Figma 访问使用 MCP 只读接口（`get_metadata` / `get_screenshot`，未调用任何写接口）。`figma-ref/` 下的 3 张 PNG 是从 Figma MCP 返回的**临时资源 URL** 下载的当次快照；URL 已过期，但 PNG 本身可长期复核。若要重新取图：`get_screenshot({fileKey:"sHQvkMfq5wue6DXhKUP9PV", nodeId:"3:2"})`（书架）、`"9:2"`（工作台）、`"1:2"`（材质规格页）。

---

## 11. 未覆盖 / 待验证清单（诚实边界）

| # | 项 | 原因 | 建议 |
|---|---|---|---|
| 1 | 系统标题栏是否与自绘 titlebar 共存（SH-03） | CDP 截图不含系统 chrome；`P19-BOOT-1` 整窗实拍是旧构建 | 本任务外另跑一次**桌面级整窗截图**（PrintWindow/OS 截图）确认 |
| 2 | 1280 下书架库区是否真出横向滚动条（SB-01） | 静态推导（892 vs 904）；截图只有 1 本书 | 用 5+ 本书的 fixture 重跑 NARROW-1 的 1280 档 |
| 3 | WebView2 是否支持 `document.startViewTransition`（共享元素转场） | 需查本机 WebView2 版本能力 | 在 e2e 里 `typeof document.startViewTransition` 探测 |
| 4 | `backdrop-filter` 在深色大面积下的实测帧率 | 与 F9 的 17.53ms/33.3ms 不是同一测量对象 | 属 AC3 范围，由对应测量补齐 |
| 5 | Figma「02 组件」68 变体的尺寸/字号差异 | 主动降级（边际收益低） | 若 AC6 需要「组件级对齐度」，单独补一轮 |
| 6 | 设置页视觉目标 | **Figma 无设置画板** | 需用户/DSH 决定：补一版设置页 Figma，或以 `AD001` §5 + 现有设计语言为准 |
| 7 | 阅读器是否沉浸式（RD-01）、导航是否改回 Rail（SH-06/ST-06） | **基线 vs Figma 冲突** | **提交 DSH/用户裁决**，裁决前不应动手 |

---

## 12. 给 AC6/AC7 的直接输入（供路线裁决引用）

| 问题 | 本报告的回答 |
|---|---|
| 「材质不满意」是栈限制吗？ | **主因不是**。配方正确（`acrylic.css` 与 Figma 逐项一致）、预算与降级链比设计更完整；**断点是窗口层没接原生 Mica**（SH-01，Tauri 有官方 API，不需换栈）。只有「真 WinUI Acrylic 的光学质感」（SH-07）是栈上限，且设计稿已接受仿制。 |
| 「圆角阴影不满意」是什么？ | 令牌体系（8/4/2/0 + elevation-8/16）**已落地且合规**；不满意来自**布局与卡片形态**（固定列宽、封面自创表现、卡片边框过多、详情面板卡片化）→ **欠账**。 |
| 「页面转场与动效不满意」是什么？ | **100% 欠账**：全仓仅 1 个 `@keyframes`；且页面切换是**卸载式**（违约基线 keep-alive），连转场的实现基座都没有。CSS 完全够用，**不涉及栈**。 |
| 有多少条必须靠换栈解决？ | **0 条**。栈限制共 4 条：严格 2 条（SH-07 设计已接受仿制、SH-08 设计未要求窗口圆角）；另 2 条「有原生替代」（SH-01 窗口 Mica、SH-09 多窗口）都能在 Tauri 内解决。 |

---

*报告结束。所有编号（SH/SB/WB/RD/ST-xx）可在 CMS 裁决文档与后续 Task 中直接引用。*
