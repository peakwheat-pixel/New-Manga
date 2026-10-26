# Saber 视觉参考规格（书架·着重参考 / 工作区·参考 / 阅读器·设置·令牌映射）

- **任务**：DISPLAY-PERF-DECISION-1 / task-7（父任务：新架构方案收口）
- **Owner**：saber-ui-spec（DSH 团队）
- **日期**：2026-10-26
- **状态**：规格完成，待 Lead 复核与实现任务引用
- **参考对象**：Saber-Translator（GPL-3.0）本机只读安装 `E:\software\Saber-Translator`
- **目标消费方**：Windows / C# .NET + Avalonia（AD-002 架构）；产品四页 = 书架 / 工作台 / 阅读器 / 设置
- **本文档性质**：**视觉与交互参考规格 + 令牌数据**，不是逐像素还原清单，不含 Saber 源码片段。

> **范围声明（用户 2026-10-26 两次收窄后的最终口径）**
> 1. **书架**：**着重参考**——只提取「信息架构 + 布局范式 + 交互流程 + 视觉语言」四件事；尺寸给 CSS 权威值与「约」值，不作为验收像素基线。
> 2. **工作区（工作台）**：**参考**——提取信息架构、动作顺序、层级观感；不要求逐像素。
> 3. **阅读器 / 设置**：**不逆向布局**——沿用既有 Figma v2 结构，本文只给「令牌映射建议」。
> 4. **令牌文件** `tokens-saber-purple.json`：四页共用资产，优先级最高（含 dark 变体建议）。
> 5. 文中每条标注 **〔参考项〕**（照其思路做）或 **〔可自由发挥〕**（不照做也行）；不使用「逐像素还原」类表述。

---

## 0. TL;DR

| 页面 | 处理方式 | 一句话结论 |
|---|---|---|
| 书架 | 〔参考项〕着重参考 | 紫渐变 64px 顶栏（logo+站名 / 局域网地址胶囊 / 教程·仓库·主题占位）→ 1400px 居中内容区：📚 我的书架 + 右侧 3 个动作（+新建书籍·🏷️管理标签·快速翻译）→ 白卡筛选区（搜索框+🔍 / 标签 chip 行）→ 自适应书卡网格（封面 3:4、白底 12px 圆角、hover 上浮+「查看详情」遮罩）→ 空态/无结果态；书籍详情为 900px 对话框（封面 140px + 元信息 + 3 动作 + 章节列表行内操作）。 |
| 工作台 | 〔参考项〕参考 | 三栏 + 可切深色编辑态：左 300px「翻译设置」+ 按色分族的动作按钮栈；中 画布（顶栏：查看原图 / 切换编辑模式 / 图片大小滑杆 / 进度）+ 78% 灰底；右 230px「图片概览」缩略图栏；编辑态叠加深色 chrome（工具栏 + 气泡检查器）。 |
| 阅读器 | 〔令牌映射〕 | 不逆向。沿用 Figma v2；只套用 nm- 令牌，并把 Saber 的阅读底色四预设（#1A1A2E/#FFFFFF/#F5F5DC/#2D2D2D）映射成 `nm-bg-reader-*`。 |
| 设置 | 〔令牌映射〕 | 不逆向。沿用 Figma v2 分组卡片结构；把 Saber 的 settings-group/item/input 观感映射到 nm- 令牌（含 focus ring 与 toggle）。 |
| 主题中心 | 〔可自由发挥〕 | Saber 无此页（其「☀️ 主题」按钮 title 就是「功能开发中」）。给出占位页骨架：令牌色板 + Light/Dark 双预览 + 强调色选择 + 阅读底色预设 + 「即将开放」状态。 |

---

## 1. 证据与方法

### 1.1 只读来源（未启动其 exe / 后端）

| 来源 | 路径 | 用途 |
|---|---|---|
| 全局样式 | `…\_internal\src\app\static\vue\assets\index.LryjAgvf.css` | `:root` 令牌、`body` 主题变量、`.btn`/`.card`/`.form-group`/`.settings-*`/toast |
| 顶栏样式 | `…\assets\AppHeader.oavnQySz.css` | 顶栏三种变体（默认 / insight / bookshelf）、链接胶囊、主题按钮 |
| 书架样式 | `…\assets\BookshelfView.MhjJHDb8.css` | 书卡、筛选卡、搜索、标签 chip、详情、章节、标签管理、确认框 |
| 对话框样式 | `…\assets\BaseModal.DWFYGyoJ.css` | 遮罩、尺寸档、头/体/脚、打开动画 |
| 阅读器样式 | `…\assets\ReaderView.B7LAIstj.css` | 顶栏 56px、阅读底色变量、返回顶部、底色选项（仅令牌映射用） |
| 工作区样式 | `…\assets\TranslateView.B0xfhEt3.css` | 侧栏 300/缩略图 230/编辑面板 600、深色 chrome、拖放区、气泡框 |
| 模板/文案 | `…\static\vue\js\BookshelfView.*.js`、`index.*.js`、`TranslateView.*.js`、`ReaderView.*.js`、`AppHeader.*.js` | 编译后模板字符串：类名层级、界面文案、props、动作顺序 |
| 设置项清单 | `E:\software\Saber-Translator\config\user_settings.json` | 30 个设置键（附录 A），供设置页/工作区对照 |
| 页面入口 | `…\static\vue\index.html` | 标题 `Saber-Translator`、lang `zh-CN` |
| 截图（已下载） | `verification/DISPLAY-PERF-DECISION-1/ui-stack/saber-ref/*.png` | 书架的观感、工作区/编辑态的信息架构 |

### 1.2 提取方法

1. **CSS 反解**：把 9 个 minified CSS 逐条解析成选择器 + 声明（只读脚本输出到临时目录，不写入仓库），提取 `:root`/`body` 变量、颜色频次（全库 top：`#fff` 297、`#e0e0e0` 68、`#333` 60、`#6366f1` 59、`#666` 53、`#667eea` 44、`#3498db` 36、`#f5f5f5` 27、`#e2e8f0` 26、`#f8fafc` 21、`#4f46e5` 20、`#22c55e` 18、`#ef4444` 18、`#764ba2` 15）。
2. **模板反推**：Vue 编译产物保留 `class:`/`placeholder:`/`title:` 字符串与 DOM 顺序，可精确还原组件结构与文案（见 §3 文案表）。
3. **截图结构标定**（仅用于核对 CSS 是否与实际观感一致，不作为像素基线）：对 `bookshelf-display.png` 做像素扫描，推得 **截图 DPR ≈ 1.5、CSS 视口 ≈ 1659×930**：内容区左右边界 232/2260 px（图内）→ CSS 宽 1352px = `max-width:1400 − padding:24×2`；网格 5 张卡宽 258、间距 37.5（图内）→ CSS 172.6 / 25 ≈ `minmax(160px,1fr)` 在 1352px 下 **7 列**、`gap:24px`。左起第 5 张后留白即第 6/7 空列。**结论：安装版 CSS 与截图同构**，可放心以 CSS 值为「约值」依据。
4. **配色采样**：对三张截图做分块聚类与扫描线采样（结果见 `SCREENSHOT_INDEX.md`）。顶栏实测渐变由 `#6778e5` 平滑过渡到 `#744da6`，与 CSS `linear-gradient(135deg,#667eea,#764ba2)` 一致；页面底色实测 `#f5f5f8` ≈ CSS `#f4f7f9`。

### 1.3 证据编号（全文引用）

| ID | 含义 |
|---|---|
| `E-CSS-01..06` | 上述 6 份 CSS（01 index / 02 AppHeader / 03 BookshelfView / 04 BaseModal / 05 ReaderView / 06 TranslateView） |
| `E-TPL-01..05` | 编译产物模板：01 BookshelfView / 02 index（路由·导航·设置 store）/ 03 TranslateView / 04 ReaderView / 05 AppHeader |
| `E-IMG-01..03` | 截图：01 bookshelf-display / 02 interface / 03 Editor |
| `E-CFG-01` | `config/user_settings.json` |
| `E-HTML-01` | `static/vue/index.html` |

### 1.4 已知偏差与限制（实现前必读）

1. **版本漂移**：截图与安装版静态包存在小差异。
   - 截图顶栏右侧有「本项目完全开源免费，请勿上当受骗」白胶囊；安装版该文案只出现在设置弹窗「关于」分组（`E-TPL-03`），书架页模板里没有。→ 若沿用该顶栏，建议**不放**该胶囊（或放到设置/关于）。
   - 截图标签 chip 带计数气泡（`123 3`），安装版模板只渲染标签名（`tag-count` 样式残留但无节点）。→ **计数属于可自由发挥**。
   - 首张书卡封面右上角蓝色数字，判定为封面图内容（`BookCard` 模板只有 cover + info 两层，无角标节点）。→ 不添加角标。
2. **无暗色**：Saber 只有浅色；书架/顶栏的「☀️ / 主题」按钮 `title="功能开发中"`，点击 toast「🌙 该功能正在开发中，敬请期待！」（`E-TPL-01`/`E-TPL-05`）。dark 变体是我们新增的，见令牌文件 `themes.dark`（其锚点为工作区深色 chrome 与阅读器深蓝）。
3. **字体授权**：Saber 安装目录 `static\fonts\` 共 26 个字体文件，混有 Arial Unicode、汉仪瑞意宋/汉仪正圆、华康抖抖体、字体管家天天晴宋、ST* 系列等**商业/系统字体**，不可随包。令牌只给系统字体栈；漫画渲染字体须另行按可再分发许可（OFL 等）引入。见附录 B。
4. **未取得可运行界面**：按要求未启动 Saber，因此**无交互态实测**（hover/focus/动画时序）——CSS 里有声明，截图里不可见；本文所有交互态均标注为「CSS 声明」而非实测。
5. **NOT_RUN**：书籍详情对话框、新建书籍对话框、标签管理对话框、空态、加载态、Toast——**无截图**，全部由 CSS + 模板反推，已逐条标注。〔参考项〕

---

## 2. 全局视觉语言

### 2.1 色彩体系（令牌见 `tokens-saber-purple.json`）

| 角色 | 值 | 证据 |
|---|---|---|
| 品牌渐变 | `linear-gradient(135deg,#667eea,#764ba2)` | `E-CSS-01` 的 `.btn-primary`、`E-CSS-02` `.app-header--bookshelf`、`E-CSS-03` `.book-cover`/`.search-btn` |
| 主色（实心） | `#6366F1`；深一档 `#4F46E5`；浅一档 `#667EEA` | `E-CSS-03` 聚焦边框、`E-CSS-01` `--border-radius-*` 区块；全库频次 #6366f1=59 |
| 页面底 | `#F4F7F9`（body）；卡片/面板 `#FFFFFF`；内嵌输入 `#F9FAFC`；hover `#F0F4F8`；active `#E2E8F0` | `E-CSS-01` body/`body{}` 变量 |
| 边框 | 默认 `#E2E8F0`；输入 `#E0E6ED`；强 `#CBD5E0`；旧灰 `#E0E0E0` | `E-CSS-01` `--border-color` |
| 文字 | 主 `#1A202C`、标题 `#2C3E50`、正文 `#333333`、次 `#718096`、弱 `#A0AEC0` | `E-CSS-01` `--text-*` / `--color-gray-*` |
| 状态 | 成功 `#22C55E`（旧 `#28A745/#27AE60`）、危险 `#EF4444`（旧 `#DC3545/#E74C3C`）、警告 `#F59E0B`（旧 `#F0AD4E`）、信息 `#3498DB` | `E-CSS-01/03/06` |
| 顶栏玻璃 | 胶囊底 `rgba(255,255,255,.18)`、hover `25%`、文字 `rgba(255,255,255,.95)`、`backdrop-filter: blur(4px)` | `E-CSS-03` `.lan-access-info/.tutorial-link/.github-link/.theme-toggle` |

> 〔参考项〕品牌渐变只做「强调面」：顶栏、主按钮、进入类动作、封面占位；页面大背景永远是中性浅灰。

### 2.2 形状 / 阴影 / 间距 / 字号（CSS 权威值）

| 类别 | 标度 | 证据 |
|---|---|---|
| 圆角 | 4 / 6 / 8 / 10 / 12 / 14 / 16 / 20 / 999px（控件 8、卡片·对话框 12、侧栏卡 14、胶囊 20、圆形 999） | `E-CSS-01` `--radius-*` `--border-radius-*`；`E-CSS-03/06` |
| 阴影 | sm `0 2 4 rgba(0,0,0,.05)`；md `0 4 12 rgba(0,0,0,.08)`；lg `0 8 16 rgba(0,0,0,.12)`；卡片 hover `0 12 32 rgba(0,0,0,.15)`；顶栏 `0 2 20 rgba(102,126,234,.30)`；对话框 `0 4 20 rgba(0,0,0,.15)` | `E-CSS-01/02/04` |
| 间距 | 4 / 6 / 8 / 10 / 12 / 14 / 16 / 20 / 24 / 28 / 32 / 40 / 80px | `E-CSS-01` `--spacing-*` + 各组件 padding |
| 字号 | 11.2（.7rem）12（.75）12.8（.8）13.6（.85）14.4（.9）15.2（.95）16（1rem）19.2（1.2em）20.8（1.3rem）24.8（1.55rem）28.8（1.8rem） | `E-CSS-01/03/04` |
| 字重 | 400 / 500 / 600 / 700 | 同上 |
| 字体栈 | 界面 `Arial, sans-serif`（Saber 实际如此，中文落到系统字体）；等宽 `Consolas, Monaco, monospace` | `E-CSS-01` `--font-sans/--font-mono` |
| 层级 | base 1 / dropdown 100 / sticky 200 / sidebar 300 / overlay 1000 / modal 1100 / popover 1200 / toast 1300 | `E-CSS-01` `--z-*` |

> 实现口径：Avalonia 用系统栈 `"Microsoft YaHei UI","Segoe UI","PingFang SC","Noto Sans SC",sans-serif`；字号用上面 px 取整到 11/12/13/14/15/16/19/21/25/29 即可，不追 0.4px 差。

### 2.3 顶栏（书架形态）〔参考项〕

| 项 | 值 | 证据 |
|---|---|---|
| 高度 | 64px（页面 sticky top，z=200） | `E-CSS-02` `.app-header--bookshelf` |
| 底色 | 品牌渐变；投影 `0 2 20 rgba(102,126,234,.30)` | 同上 |
| 内边距 | `0 24px`；内部内容条 `max-width:1400px; margin:0 auto` | 同上 |
| 左区 | 40×40 logo（圆角 8、投影 `0 2 8 rgba(0,0,0,.20)`）+ 站名（21px / 700 / 白 / 字距 -0.5px），两者间距 12px | 同上；`E-IMG-01` |
| 中区 | 局域网地址胶囊：`🌐局域网设备可通过该网址访问` + `http://<ip>:<port>/`（等宽字体）+ `📋` 复制按钮；胶囊底 18% 白、hover 25%、圆角 20、内边距 `6px 12px`、字号 13.6px、`blur(4px)` | `E-CSS-03` `.lan-access-info/.copy-btn`；`E-TPL-01`；`E-IMG-01` |
| 右区 | 间距 16px：`使用教程` 链接胶囊（白 15% 底）→ GitHub 圆形图标（24px 图标 + 6px 内边距 + 白 15% 圆形底）→ 主题按钮 38×38 圆形（白 20% 底，`title="功能开发中"`） | 同上 |
| 交互 | 胶囊 hover：底色加深 + `translateY(-2px)`；主题按钮 hover：`rotate(15deg)` | `E-CSS-02/03` |
| 书架页 header 由独立实现（`BookshelfView` 自带 header-links 插槽） | 〔实现建议〕我们统一为一个 `NmTopBar` 组件，三页共用 | `E-TPL-01` |

> 〔可自由发挥〕局域网地址胶囊在新架构下是否需要（Avalonia 无浏览器远端访问）——建议保留视觉位，改为「本地库路径 / Core 状态」或直接省略。主题按钮 → 改为打开「主题中心」占位页。
> 其他页顶栏形态参考：insight 变体为 56px 白底 + 底边线 + 深色文字（`E-CSS-02 .app-header--insight`）；阅读器顶栏 56px 渐变（`E-CSS-05 .reader-header`）。

### 2.4 页面容器与滚动

- 书架：`main{max-width:1400px; margin:0 auto; padding:24px}`，`min-height:calc(100vh - 64px)`；页面整体滚动由外层承担，内容区无独立滚动。（`E-CSS-03 .bookshelf-main`）
- 对话框：`max-height:90vh`，body 区 `overflow-y:auto`，头/脚固定。（`E-CSS-04`）
- 章节列表：`max-height:280px` + 内滚（滚动条 6px，轨道 `--hover-bg`，滑块 `--border-color`，圆角 3px）。（`E-CSS-03`）
- 〔参考项〕桌面端可改为「内容区自适应高度 + 章节列表虚拟化」，不必照抄 280px 上限。

### 2.5 动效（CSS 声明，未实测）

| 场景 | 值 |
|---|---|
| 按钮 hover | `transform:translateY(-2px)` + 阴影升级；`transition:all .2s ease` |
| 按钮按下 | `scale(.97)`（书架页 `.btn:active`） |
| 书卡 hover | `translateY(-6px) scale(1.02)`、阴影 `0 12 32 rgba(0,0,0,.15)`、2px `rgba(102,126,234,.5)` 描边、封面图 `scale(1.05)`、「查看详情」遮罩 200ms 淡入 |
| 书卡按下 | `translateY(-2px) scale(1.01)` |
| 对话框 | 遮罩透明度 200ms + 面板 `scale(.95)→1` |
| Toast | 上滑 20px + 淡入 300ms，退出 200ms |
| 页面切换 | `fadeIn / slideIn / slideUp` 关键帧（`E-CSS-01`） |

### 2.6 暗色策略（新增，非 Saber）

- 令牌 `themes.dark` 已给全套值；锚点：工作区编辑 chrome `#16213E→#1A1A2E`、阅读器深蓝 `#1A1A2E`。
- 切换机制建议 `Application.RequestedThemeVariant` + `ThemeDictionaries`；主题中心页只做预览，不改运行期全局（占位阶段）。
- 对比度：dark 下正文用 `nm-text-primary`（比 light 的 `#333` 更亮一档）；accent 提亮到 `#7C8CF8`。

---

## 3. 书架页（**着重参考**）

### 3.1 分区与元素顺序（自上而下，块级顺序=DOM 顺序）

```
┌─ NmTopBar (64px, 品牌渐变, sticky) ──────────────────────────────┐
│ [logo 40] 书架首页            [🌐 LAN 胶囊 📋]   [教程] [GitHub] [主题] │
└──────────────────────────────────────────────────────────────────┘
┌─ main: max-width 1400, padding 24 ───────────────────────────────┐
│  H1「📚 我的书架」(28.8px/700)         [ + 新建书籍 ][🏷️ 管理标签][快速翻译] │
│  ┌ filter card (白, r12, shadow-md, padding 16, gap 16) ────────┐ │
│  │ [ 搜索书籍名称或标签...            ] [🔍] [clear ✕]           │ │
│  │ 标签筛选:  (chip)(chip)(chip)                                │ │
│  └──────────────────────────────────────────────────────────────┘ │
│  ┌ books-grid: repeat(auto-fill,minmax(160px,1fr)) gap 24 ──────┐ │
│  │ [card][card][card][card][card] …                             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│  (空态/无结果态替换网格)                                          │
└──────────────────────────────────────────────────────────────────┘
浮层：BookModal(新建/编辑) · BookDetailModal(详情) · TagManager · QuickTag · Confirm · Toast
```

证据：`E-TPL-01`（DOM 顺序）、`E-CSS-03`（尺寸）、`E-IMG-01`（观感）。

### 3.2 顶栏细节

见 §2.3。书架页特有的三点：

1. 站名传参为「书架首页」（`logo-title="书架首页"`，也可理解为文档标题/面包屑语义）——`E-TPL-01`。
2. 右侧动作顺序固定：局域网胶囊（含复制）→ 使用教程 → GitHub → 主题（占位）。`E-IMG-01`。
3. 顶栏在书架页是页面级 sticky；其余页面若要复用需确认是否 fixed/56px。`E-CSS-02`。

### 3.3 标题 + 动作区

| 元素 | 规格 | 证据 |
|---|---|---|
| 容器 `.bookshelf-toolbar` | flex 两端对齐，`margin-bottom:32px`，`gap:16px`，窄屏换行 | `E-CSS-03` |
| 标题 `<h1 class="page-title">` | 28.8px / 700 / `#1A202C`；行内 emoji 前缀 `📚`（Saber 用 `::before`，字号 24px，间距 12px） | `E-CSS-03` |
| 动作组 | `display:flex; gap:12px` | `E-CSS-03` |
| `+ 新建书籍` | primary：品牌渐变、白字、`padding 10 20`、r8、15.2px/500，左侧 `+` 号（17.6px/600）；hover 上浮 2px + `0 6 20 rgba(102,126,234,.4)` | `E-CSS-03`；`E-TPL-01` |
| `🏷️ 管理标签` | secondary：白底 + `1px #E2E8F0` 边框、深色字；hover 底色 `#F0F4F8`、边框转 `#718096` | 同上 |
| `快速翻译` | secondary 同款；点击直接跳 `/translate`（工作区） | `E-TPL-01` |

> 〔参考项〕三按钮的语义梯度（主 CTA 唯一渐变、其余白底描边）值得照搬；emoji 图标建议替换为矢量图标（Avalonia 无 emoji 彩色字体一致性）。

### 3.4 搜索 + 标签筛选卡

| 元素 | 规格 | 证据 |
|---|---|---|
| 卡片 | 白底、r12、`shadow 0 4 12 rgba(0,0,0,.08)`、`padding 16`、纵向 `gap 16`、`margin-bottom 24` | `E-CSS-03` `.filter-bar` |
| 搜索行 | flex、`gap 8` | 同上 |
| 输入框 | 占满剩余宽；`padding 10 16`、r8、`1px #E2E8F0`、底 `#F9FAFC`、15.2px；placeholder `#A0AEC0`；聚焦：边框 `#667EEA` + `0 0 0 3 rgba(102,126,234,.10)` | 同上 |
| 搜索按钮 | 品牌渐变底、白 `🔍`、`padding 10 14`、r8；hover `scale(1.05)` | 同上 |
| 清除按钮 | 仅在有输入时出现；底 `#F0F4F8`、字 `#718096`、内容 `✕`；hover 转深 | 同上；`E-TPL-01` |
| 行为 | 输入 **300ms 防抖**触发搜索；`Enter` 立即搜索；点 🔍 立即搜索；点 ✕ 清空并重置搜索 | `E-TPL-01` |
| 标签筛选行 | 仅当存在标签时渲染：`标签筛选:`（13.6px、`#718096`）+ chip 组（`gap 8`，可换行） | 同上 |
| 标签 chip | `padding 4 12`、r20、12.8px、默认底 `#F0F4F8`、字 `#1A202C`、2px 透明边框；hover/选中：底色=该标签颜色、白字、选中加 `0 2 8 rgba(102,126,234,.30)`；每标签色由标签数据提供，回退 `#667EEA` | `E-CSS-03`；`E-TPL-01`（`--tag-color` 绑定） |
| 多选 | 可同时选中多个标签（`selectedTagIds` 数组） | `E-TPL-01` |

> 〔可自由发挥〕chip 计数气泡（截图有、安装版无）；chip 颜色若与品牌紫冲突，可统一用 `nm-accent-soft` 底 + accent 字，选中才实心。

### 3.5 书卡网格规则

| 项 | 值 | 证据 |
|---|---|---|
| 网格 | `grid-template-columns: repeat(auto-fill, minmax(160px,1fr))`、`gap:24px` | `E-CSS-03 .books-grid` |
| 列数换算 | 内容宽 1352px（1400−48）→ **7 列**，列宽 172.6px；视口 <1400 时按 `(宽+gap)/(160+gap)` 向下取整 | 计算 + `E-IMG-01` 标定 |
| 区块最小高 | `.books-container{min-height:400px}`（防跳） | `E-CSS-03` |
| 密度建议 | 每列卡片数随行数与滚动；书少时左对齐留空，不拉伸卡片 | `E-IMG-01`（5 张卡占 5 列，右侧留空） |

### 3.6 书卡构成（`BookCard`）〔参考项：书架标志性组件〕

| 层 | 规格 | 证据 |
|---|---|---|
| 卡本体 | 白底、r12、`shadow 0 4 12 rgba(0,0,0,.08)`、`overflow:hidden`、`cursor:pointer`、`transition:all .3s` | `E-CSS-03 .book-card` |
| 封面区 | `aspect-ratio:3/4`；无封面时显渐变底 + 居中 `📖`（48px，白 80%）；封面图 `object-fit:cover` | 同上 |
| hover 遮罩 | 覆盖整张封面，`rgba(0,0,0,.60)` 底 + 居中白字「查看详情」（14.4px/500），200ms 淡入 | 同上（`::before`） |
| info 区 | `padding:12px`、纵向 `gap:4px` | 同上 |
| 标题 | 15.2px / 600 / 单行省略 / 深色 | 同上 |
| 章节数 | 12.8px / `#718096` / 文本 `{n} 章节` | 同上；`E-TPL-01` |
| 标签行 | `gap:4px`、`margin-top:4px`、可换行 | 同上 |
| 标签 pill | `padding 2 8`、r10、11.2px、白字、底色=标签色（回退 `#667EEA`） | 同上 |
| 无标签 | 整个标签行不渲染 | `E-TPL-01` |

> 〔可自由发挥〕把「查看详情」遮罩换成右下角图标按钮（桌面鼠标场景更轻）；封面比例建议保留 3:4（与 Saber 观感一致）。
> 注意：`BookCard` 模板没有「章节数角标」，不要凭封面数字去加角标。

### 3.7 书籍详情（对话框 `BookDetailModal`）

> **NOT_RUN（无截图）**：结构与尺寸全部来自 `E-TPL-01` + `E-CSS-03`；尺寸档推断为 `large`（900px），因 `BookshelfView` 内仅出现 1 次 `size:"large"`。

| 区块 | 规格 |
|---|---|
| 容器 | 纵向 `gap:24px`；`info section` 为 flex 横排 `gap:24px`、顶部对齐 |
| 大封面 | 宽 140px、`aspect-ratio:3/4`、r12、无封面显品牌渐变、`shadow 0 8 24 rgba(0,0,0,.15)` |
| 元信息列 | flex:1；书名 20.8px/600、`margin-bottom:16px`、可换行 |
| 元信息行 | 14.4px、`#718096`，`margin:6px 0`、行内 `gap 8`；行首标签（`章节数：`/`创建时间：`/`最后更新：`/`标签：`）为主色 500 字重、`min-width:70px` |
| 标签 | pill `2 8`、r10、12px、白字彩底；无标签显示斜体「暂无标签」+ 22px 圆形虚线「+」按钮（hover 转 accent 描边） |
| 动作行 | `gap:8px`、`margin-top:16px`：`● 漫画分析`（primary 小号）、`编辑书籍`（secondary 小号）、`删除书籍`（danger 小号）——小号=`padding 6 14`、13.6px |
| 章节区 | 顶部 `1px` 分隔线 + `padding-top:16px`；头部行两端对齐：`章节列表`（16.8px/600）+ 右侧 `+ 新建章节`（primary 小号） |
| 章节列表 | 纵向 `gap:8px`、`max-height:280px` 内滚；每行：`⋮⋮` 拖拽把手（title=拖拽排序）→ `#序`（12.8px 次色，宽 32px）→ 章节名（14.4px/500 单行省略）→ `{n} 张图片`（12px 次色）→ 右侧动作：`进入翻译`（紫渐变）、`进入阅读`（绿渐变，0 图时禁用：灰底+50% 透明+禁用光标）、`编辑`、`删除`（普通文字按钮，`删除` hover 转红） |
| 章节行 | 底 `#F0F4F8`、r8、`padding 12 16`；hover 底色 `#E2E8F0`；拖拽中/悬停目标有高亮类 |
| 空章节 | 居中提示「暂无章节，点击上方按钮创建」 |
| 交互 | 行可拖拽重排（拖动结束保存）；`进入翻译`→ `/translate` 并带 chapter 上下文；`进入阅读`→ `/reader`；`删除`→确认框 |

来源：`E-CSS-03`（`.book-detail-container`/`.book-info-section`/`.chapter-item` 等）、`E-TPL-01`（按钮顺序与文案）。

### 3.8 新建 / 编辑书籍对话框（`BookModal`）

> **NOT_RUN（无截图）**：来自 `E-TPL-01` + `E-CSS-03` + `E-CSS-04`（`BaseModal`）。
> 标题动态：新建=`新建书籍`，编辑=`编辑书籍`。推断宽度 600px（BaseModal `medium`），`max-height:90vh`。

| 区块 | 规格 |
|---|---|
| 头 | `padding 16 20` + 底线；标题 19.2px/600 `#2C3E50`；右上 `×`（hover 浅灰底） |
| 体 | `padding 20`，内滚；表单纵向排列 |
| ① 书籍名称 | label（15.2px/500，红色 `*` 必填标记，间距 8px）+ 文本框 `padding 10 12`、r6、14px、占位 `请输入书籍名称`；聚焦边框 accent；校验失败 toast「请输入书籍名称」warning |
| ② 封面图片 | label → 虚线拖放区（`2px dashed #E2E8F0`、r8、`padding 16`、居中、hover 边框 accent、可点可拖入）；内部为空态 `📷`（32px）+ `点击或拖拽上传封面`，选中后显示预览 150×200（r4、底 `#F5F5F5`、`object-fit:cover`）；下方提示 12px 次色：`支持 JPG、PNG、WebP 格式，建议比例 3:4` |
| ③ 标签 | label + 输入容器（`1px #E2E8F0`、r6、`padding 8`）：已选标签行（chip `4 8`、r4、12px、accent 底白字、右侧 `×`）+ 输入框（透明底、占位 `输入标签名称...`、`Enter` 添加）；聚焦时下拉建议列表（绝对定位、白底、`1px` 边框、r6、`shadow 0 4 12 rgba(0,0,0,.1)`、最大高 200px 内滚、行 `padding 10 12`、hover 浅灰）；提示 12px：`输入后按回车添加新标签，或从已有标签中选择`。输入不存在的标签并回车 → 直接创建并选中 |
| 脚 | 右对齐 `gap 10`：`取消`（secondary）、`保存`（primary）；回车提交表单 |
| 成功/失败 | toast：`书籍创建成功`/`书籍更新成功`（success）、`创建失败`/`更新失败`（error） |

### 3.9 其余浮层

| 浮层 | 结构（`E-TPL-01`/`E-CSS-03`） |
|---|---|
| 标签管理 `TagManager` | 标题`标签管理`；表单行：`输入新标签名称`（文本框，flex:1）+ 40×40 颜色选择器 + `添加` 按钮；列表（最大高 300px 内滚）：颜色圆点 16px + 名称 + `{n} 本` + `编辑`（紫渐变小按钮 12px）+ `删除`（红渐变小按钮）；编辑态：颜色块 + 名称输入 + `保存`（绿）+ `取消`（灰）；空态 `暂无标签，请在上方添加`；文案 `标签名称不能为空` / `该标签已存在` |
| 快速添加标签 `QuickTag` | 标题`快速添加标签`（small 400px）；输入框（`padding 12 16`、r8、占位 `输入标签名称进行搜索或创建...`）+ 列表行：颜色点 12px + 名称 + hover 显 `+`；新建项为虚线渐变底提示「创建并添加」；底部单个`关闭`按钮；无匹配 `未找到匹配的标签` |
| 确认框 `ConfirmModal` | small 400px；正文居中 14px；脚 `取消`（secondary）+ 确定（`确认删除` 类动作用危险样式） |
| Toast | 见 §2.1/令牌 `components.toast`；成功/失败/警告/信息四色 |

### 3.10 关键流程（交互序列）

**A. 新建书籍（主路径）**
`+ 新建书籍` → BookModal（填名称 → 可选上传封面 → 可选加标签）→ `保存` → 校验名称（空则 warning toast）→ 成功 toast + 关闭 → 网格刷新并出现新卡。
**B. 导入漫画（两条入口，Saber 分流）**
1. **走书架**：详情 → `+ 新建章节` → 输入章节名（占位 `例如：第1话、序章`）→ 保存后章节行为 `0 张图片` → `进入翻译` 进工作区导入图片（图片导入发生在工作区，见 §4.6）。
2. **快速通道**：书架顶部 `快速翻译` → 直接 `/translate` → 工作区拖放区导入图片（拖拽 图片/PDF/MOBI，或「选择文件」「📁 选择文件夹」）→ 翻译完成后写回书架（Saber 有「书架模式自动保存」开关，`E-CFG-01 autoSaveInBookshelfMode`）。
**C. 进入详情 → 进入工作区/阅读**
点卡 → 详情对话框（封面/元信息/标签/动作/章节）→ `进入翻译`（紫）或 `进入阅读`（绿，0 图禁用）；`● 漫画分析`、`编辑书籍`、`删除书籍`（danger + 二次确认 `确定要删除这本书籍吗？所有章节数据将一并删除，此操作不可恢复。`）。
**D. 标签体系**
`管理标签` 增删改 → 卡片与详情显示彩色 pill → 搜索卡顶部 chip 多选筛选（与搜索词叠加，交集）→ 无结果走「未找到匹配」态。

### 3.11 状态与边界

| 状态 | 表现 | 证据 |
|---|---|---|
| 首屏加载 | 书架数据异步；无骨架屏证据（NOT_RUN）→ 建议 Avalonia 用 6–8 个书卡骨架（〔可自由发挥〕） | `E-TPL-01` |
| 空书架 | 居中：`📚`(64px) → `书架空空如也`(24px) → `点击"新建书籍"开始你的翻译之旅`(次色) → primary 按钮 `+ 新建第一本书`；上下 padding 80/20 | `E-CSS-03`/`E-TPL-01` |
| 搜索/筛选无结果 | `🔍`(64px) → `未找到匹配的书籍` → `尝试调整搜索条件或标签筛选`（无按钮） | 同上 |
| 错误 | toast（`加载书籍失败` 等）；详情加载失败：「加载书籍详情失败: {msg}」 | `E-TPL-01`/`store` 文案 |
| 分页 | 无分页控件；一次加载全量书列表（`books-container` 固定 min-height 防跳） | `E-TPL-01`/`E-CSS-03` |

### 3.12 文案清单（原文，可直接用于对照验收）

> 来源 `E-TPL-01`（书架页竞品文案，均为界面可见字符串）。实现时可全部沿用中文文案。

| 位置 | 文案 |
|---|---|
| 顶栏站名 | `书架首页` |
| 顶栏胶囊 | `🌐局域网设备可通过该网址访问` + 地址；tooltip `其他设备可通过此地址访问`；按钮 title `复制地址`；toast `局域网地址已复制！` |
| 顶栏链接 | `使用教程`；GitHub（图标无文字） |
| 主题按钮 | 图标 `☀️`，title `功能开发中`，点击 toast `🌙 该功能正在开发中，敬请期待！` |
| 页标题 | `我的书架` |
| 动作 | `新建书籍`、`🏷️ 管理标签`、`快速翻译` |
| 搜索 | placeholder `搜索书籍名称或标签...`；按钮 `🔍`；清除 `✕` |
| 标签筛选 | `标签筛选:` |
| 书卡 | `{n} 章节`；hover 遮罩 `查看详情`；无封面 `📖` |
| 空态 | `书架空空如也` / `点击"新建书籍"开始你的翻译之旅` / `新建第一本书` |
| 无结果 | `未找到匹配的书籍` / `尝试调整搜索条件或标签筛选` |
| 详情 | `书籍详情`、`封面`、`章节数：`、`创建时间：`、`最后更新：`、`标签：`、`暂无标签`、`添加标签`、`● 漫画分析`、`编辑书籍`、`删除书籍`、`章节列表`、`新建章节`、`拖拽排序`、`{n} 张图片`、`进入翻译`、`进入阅读`、`编辑`、`删除`、`暂无章节，点击上方按钮创建` |
| 详情确认 | `确认删除` / `确定要删除这本书籍吗？所有章节数据将一并删除，此操作不可恢复。` / `确定要删除这个章节吗？此操作不可恢复。` / `确定` / `取消` |
| 新建/编辑书籍 | `新建书籍`、`编辑书籍`、`书籍名称`、`请输入书籍名称`、`封面图片`、`封面预览`、`点击或拖拽上传封面`、`支持 JPG、PNG、WebP 格式，建议比例 3:4`、`标签`、`输入标签名称...`（或 `输入标签名称`）、`输入后按回车添加新标签，或从已有标签中选择`、`保存`、`取消` |
| 章节编辑 | `编辑章节`、`章节名称`、`例如：第1话、序章`、`请输入章节名称`、`保存`、`取消` |
| 标签管理 | `标签管理`、`输入新标签名称`、`选择颜色`、`添加`、`暂无标签，请在上方添加`、`{n} 本`、`编辑`、`删除`、`保存`、`取消`、`标签名称不能为空`、`该标签已存在` |
| 快速加标签 | `快速添加标签`、`输入标签名称进行搜索或创建...`、`创建并添加`、`未找到匹配的标签`、`所有标签已添加或暂无标签`、`关闭` |
| Toast | `书籍创建成功`/`书籍更新成功`/`书籍已删除`/`章节创建成功`/`章节更新成功`/`章节已删除`/`章节排序已更新`/`标签已添加`/`标签已移除`/`标签创建成功`/`标签更新成功`/`标签已删除`/`加载失败`/`未知错误` 等 |

### 3.13 书架页截图证据索引

`E-IMG-01 bookshelf-display.png`（2488×1395，DPR≈1.5 → CSS 1659×930）可观察到：
顶栏渐变与三段布局（logo+站名 / LAN 胶囊 / 教程+GitHub+主题位）、页标题 emoji 前缀、三动作按钮的主次梯度、筛选白卡（搜索框+左对齐 🔍 按钮、标签 chip 行）、7 列网格（本图 5 张卡，右侧 2 列空白）、书卡封面 3:4 + 标题 + `{n} 章节` + 彩色标签 pill、页面底色与外边距。
**不可观察**：hover/焦点/按下态、滚动条、空态、对话框、Toast、拖拽排序、任何暗色。

### 3.14 书架页「参考项 / 可自由发挥」清单

| # | 内容 | 判定 |
|---|---|---|
| 1 | 64px 紫渐变顶栏 + 三段式布局 | 〔参考项〕 |
| 2 | 1400px 居中内容区 + 24px 内边距 | 〔参考项〕（可随产品分栏调整） |
| 3 | 标题+右侧三动作的主次梯度 | 〔参考项〕 |
| 4 | 白卡筛选区（搜索 + 标签 chip 同行/两行） | 〔参考项〕 |
| 5 | 自适应书卡网格，封面 3:4，hover 上浮+遮罩 | 〔参考项〕 |
| 6 | 书卡 meta 只有 `{n} 章节` 一行 | 〔可自由发挥〕（可加更新时间/进度） |
| 7 | 标签 pill 彩底 2px8px/r10 | 〔参考项〕（颜色可统一到 nm-accent-soft） |
| 8 | 详情=900px 对话框、大封面 140px、章节内滚 280px | 〔可自由发挥〕（Avalonia 可改为右侧详情面板或独立页） |
| 9 | 章节行内直接给「进入翻译/进入阅读」 | 〔参考项〕 |
| 10 | 拖拽排序章节 | 〔参考项〕 |
| 11 | LAN 地址胶囊 | 〔可自由发挥〕（新架构无浏览器远端，可换为库路径/Core 状态） |
| 12 | 主题按钮占位 + 「功能开发中」toast | 〔参考项〕→ 改为进入主题中心占位页 |
| 13 | 标签 chip 计数气泡、封面角标 | 〔可自由发挥〕/ 不添加 |
| 14 | emoji 作图标（📚🏷️🔍📖📷） | 〔可自由发挥〕建议换矢量图标 |

---

## 4. 工作区（工作台）——**参考项**（不逐像素）

### 4.1 信息架构

```
┌ 工作区（/translate） ────────────────────────────────────────────────┐
│ [左 300px 固定侧栏「翻译设置」]  [中：画布列]           [右 230px 缩略图「图片概览」] │
│  · 标题「翻译设置」              · 控制条：查看原图/切换编辑模式/图片大小滑杆/%  · 面包屑/文件夹/缩略图网格  │
│  · 折叠面板「文字设置」          · 失败重译按钮(条件)                          · 状态指示（已译/失败/待译）│
│  · 分组「字体排版」等            · 图片画布（灰底、居中、按 % 缩放）            │
│  · 按色分族的动作按钮栈          · 编辑态：顶部深色工具条 + 右侧检查器 600px    │
└─────────────────────────────────────────────────────────────────────┘
```
证据：`E-CSS-06`（`.settings-sidebar` fixed left 300 / `.thumbnail-sidebar` fixed right 230 / `.edit-panel-container` 600）、`E-TPL-03`、`E-IMG-02`、`E-IMG-03`。

### 4.2 动作顺序（左栏按钮栈，`E-TPL-03` 的 `hi` 数组 + `E-IMG-02`）

| 序 | 动作 | 起始文案 | 色族（Saber） | 备注 |
|---|---|---|---|---|
| 1 | 翻译当前图片 | `启动翻译当前图片` | 绿 | 无页面选择 |
| 2 | 翻译所有图片 | `启动批量翻译` | 绿 | 支持「选择页面」 |
| 3 | 高质量翻译 | `启动高质量翻译` | 紫 | 支持页面选择 |
| 4 | AI 校对 | `启动 AI 校对` | 紫 | 支持页面选择 |
| 5 | 仅消除当前文字 | `启动当前图片…` | 蓝 | |
| 6 | 消除所有图片文字 | — | 蓝 | |
| 7 | 删除当前图片 | — | 红 | 危险 |
| 8 | 清除所有图片 | — | 红 | 危险 |
| 9 | 清理临时文件 | — | 橙 | 维护 |
| 10 | 插件管理 | — | 蓝 | |
| 11 | 上一张 / 下一张 | — | 灰（小） | 底部 |

> 〔参考项〕「按动作风险/成本分色族」这个组织方式值得借鉴（绿=产出、紫=高质量/校对、蓝=处理、红=破坏、橙=维护）；具体色值请用 `nm-status-*`，不必照抄 Saber 的 5 套渐变。

### 4.3 画布与控制条

- 控制条（`E-TPL-03`）：`查看原图 / 查看翻译图`（互斥切换，蓝渐变 `#2980B9→#3498DB`，激活态转绿 `#27AE60→#2ECC71`）→ `切换编辑模式 / 退出编辑`（同款按钮，激活态绿）→ `图片大小:` + 滑杆（50–200，默认 100，右侧百分比文本）→（失败图存在时）`重新翻译失败图片 (n)`。
- 画布：页面浅灰底 `#F4F7F9`，图片居中，按百分比缩放；右侧固定缩略图栏独立滚动。
- 〔可自由发挥〕滑杆范围/步长、按钮顺序可按我们的工作流重排；「查看原图」建议改为长按/键位临时对比。

### 4.4 缩略图栏（`#thumbnail-sidebar`）

- 固定右侧、宽 230px、`top:20px right:20px`、高 `calc(100vh-40px)`、内滚（滚动条 6–8px，`#CBD5E0` 滑块 / `#F8FAFC` 轨道）。
- 标题 `图片概览`；网格缩略图；支持目录层级时显示面包屑（`📁` 前缀 + `/` 分隔，末级 active）与「返回上级」按钮。
- 缩略图状态标识：已翻译 / 翻译失败 / 已标注 / 页码（`page-selection` 体系里对应 `translated-indicator`、`translation-failed-indicator`、`labeled-indicator`、`page-number-indicator`）。
- 〔参考项〕缩略图栏作为「导航 + 进度总览」的双重角色；建议保留，并加当前页高亮。

### 4.5 编辑模式（`E-IMG-03`，深色 chrome）

- 顶栏 1：图片导航（`图 1 / 1`、上一张/下一张、菜单）+ 气泡导航（`气泡 1 / 9`、上/下）+ 视图工具（适应宽度、适应窗口、链接、全屏、放大/缩小/100%）+ 右侧 `退出编辑`。
- 顶栏 2（工具）：`检测`、`批量检测`、`翻译`、`添加`、`删除`、`修复`、`修复笔刷`、`还原笔刷`、`快捷键`（白胶囊），右侧绿色主按钮 `应用并下一张 →`（`Ctrl+Enter`；CSS 为 `linear-gradient(135deg,#0f8,#00cc6a)` 底 + 深色字）。
- 主体双栏：`原图(日文)` 与 `翻译图(中文)` 两幅画布并排，气泡高亮框（默认黄 `#FFC800` 半透明；选中绿 `#00FF88`+辉光；多选红 `#FF1744`；序号标签黑底白字/选中绿底深字）。
- 右侧检查器（约 1/3 宽）：`漫画原文` 文本域（占位 `OCR识别的日语原文...`，`🔄 重新OCR此气泡`、`📋 复制`、`⌨️ 50音`）→ `译文` 文本域（`🔄 重新翻译此气泡`、复制、`✓ 应用文本`）→ 样式区（字体下拉、字号 + `A+`/`A-`、颜色、描边、气泡填充方式、排版方向、间距/旋转/位置微调）→ `字号预设`（折叠）→ `样式同步到本页全部气泡` / `重置`。
- 深色实现要点：工具栏渐变 `#16213E→#1A1A2E`、底边 `rgba(255,255,255,.1)`、主按钮荧光绿、次要按钮透明+白 30% 描边、气泡框用 1px/缩放校正的描边。

> 〔参考项〕「双画布对照 + 右侧检查器 + 顶部按阶段分组的工具条」这一 IA 是工作区的核心价值；我们可只实现「气泡列表 + 单个检查器」的简化版。
> 〔可自由发挥〕深色编辑态是否保留；若保留，令牌用 `themes.dark`。

### 4.6 导入（工作区入口）

- 拖放区：虚线 `2px #B0BEC5`、r12、`padding 40`、宽 85% 居中、底 `#F7FAFC`；hover/拖入：边框 `#3498DB`、底 `#ECF5FE`、上浮 3px、辉光；loading 态 70% 透明 + 禁点。
- 文案：`拖拽图片、PDF或MOBI文件到这里，或 选择文件 | 📁 选择文件夹`。
- 〔参考项〕支持 图片/PDF/MOBI（Saber 还有网页导入、CBZ 由插件处理 → 见其 `pdf.U7tdldy2.js` 与插件目录；我们按产品范围裁剪）。

### 4.7 观感要点（参考，不需要逐像素）

1. 左栏是「设置 + 动作」混合面板：先从「文字样式」开始（影响新文本），再是动作栈——先定样式、再执行。
2. 按钮满宽、等高（约 38–44px）、圆角 8、文字居中、无图标也成立；颜色即分组。
3. 画布永远居中，两侧栏固定宽度（300 / 230），中间自适应；窗口小于某宽度时侧栏会挤压/覆盖（Saber 用 fixed + 滚动，未做响应式折叠）。
4. 反馈密集：每个动作都有进度条/百分比/失败计数/重试按钮。
5. 编辑态整体转深色，形成「浏览=浅色，编辑=深色」的心智分区。

### 4.8 工作区「参考项 / 可自由发挥」

〔参考项〕三栏 IA、左右栏固定宽、动作分族、缩略图导航、双画布对照、编辑检查器分栏。
〔可自由发挥〕深色编辑态、侧栏折叠、滑杆范围、页面选择对话框（网格 `minmax(150px,1fr)`、gap 14、选中角标、页签/面包屑）、50 音键盘、气泡笔刷等高级功能。

---

## 5. 阅读器 / 设置 / 主题中心——只给令牌映射

> 阅读器与设置**沿用既有 Figma v2 布局**，本节只回答「Figma v2 的哪些槽位换成 nm- 令牌」。

### 5.1 阅读器令牌映射建议

| Figma v2 槽位 | 取令牌 | 说明 |
|---|---|---|
| 页面底色 | `nm-bg-reader-*` 四选一（深蓝 `#1A1A2E` / 白 `#FFFFFF` / 米色 `#F5F5DC` / 深灰 `#2D2D2D`） | Saber 的阅读底色预设即此四值（`E-TPL-04`），默认深蓝 |
| 顶栏 | `nm-gradient-brand` + `nm-header-text`；高 56px | Saber 阅读器顶栏 56px 渐变（`E-CSS-05`） |
| 章节导航按钮 | 白 10% 底 + 白 20% 描边 + 白字（`nm-control-on-dark` / `nm-header-pill`） | 深色阅读底上仍可读 |
| 回到顶部 | `nm-accent-weak` 圆形 FAB + `nm-shadow-fab` | 48px，右下 24/80 |
| 阅读设置面板 | 复用 `nm-bg-surface` + `nm-shadow-5` + `nm-radius-xl`；滑杆/选项用 `nm-accent` | 面板内三组：图片宽度(%)、图片间距(px)、背景颜色色块（32×32、选中 2px accent 描边+外环） |
| 图片容器 | 最大宽 1200px；宽度=百分比、间距=px（Saber 变量 `--reader-image-width/-gap`） | |
| 页码/进度 | `nm-text-secondary`；进度条 `nm-accent` | |

### 5.2 设置页令牌映射建议

| Figma v2 槽位 | 取令牌 |
|---|---|
| 页面底 | `nm-bg-canvas` |
| 分组卡片 | 底 `nm-bg-inset`、`1px nm-border-default`、r10、`padding 20`、组间距 25px（Saber `settings-group` 观感） |
| 分组标题 | 17.6px/600、颜色可用 `nm-accent`（Saber 用其 primary 蓝），下方 1px 分隔 + 10px 间距 |
| 字段 label | 15.2px/500、`nm-text-primary`、下间距 6px |
| 输入/下拉 | `padding 10 12`、r6、`1px nm-border-default`、底 `nm-bg-surface`、聚焦 `0 0 0 3 nm-focus-ring` + 边框 accent |
| 帮助文案 | 13.6px、`nm-text-secondary` |
| 行内多列 | 自适应网格 `minmax(200px,1fr)`、gap 15 |
| 开关 | 胶囊 toggle：开 `nm-accent`、关 `nm-border-strong` |
| 测试/次要按钮 | `nm-status-info` 底白字（Saber 测试连接按钮用 info 蓝）或 secondary 白底描边 |
| 危险动作 | `nm-gradient-danger` / `nm-status-danger` |
| 保存栏 | 底部右对齐：`取消`(secondary) + `保存设置`(primary) |

### 5.3 主题中心占位页〔可自由发挥〕

Saber 没有主题中心（主题按钮 = 「功能开发中」）。我们把它做成一个**只读预览页**，为后续开放留桩：

```
标题：主题中心  （副标题：外观与阅读体验将在此统一管理）
① 当前主题：Light / Dark / 跟随系统  —— 三张预览卡（含缩略线框，非真实截图）
② 强调色：色板（#6366F1 默认 / 紫渐变 brand / 自定义 hex 输入）—— 只预览，不落库
③ 阅读底色：4 个色块（深蓝 / 白 / 米色 / 深灰）—— 与 §5.1 同源
④ 密度与字号：舒适 / 紧凑；正文字号 A- / A+
⑤ 底部：状态条「⏳ 即将开放：主题将在 vX 版本提供保存」
```
状态：整页可交互预览但保存按钮 disabled + tooltip「即将开放」；避免出现「改了没生效」的困惑。令牌取自 `tokens-saber-purple.json` 的 `themes.light/dark` 与 `components.*`。

---

## 6. Avalonia 实现注意（从 Saber 结构迁移到 XAML 的坑）

| # | 坑 | 建议 |
|---|---|---|
| 1 | CSS `::before/::after`（📚 标题、书卡「查看详情」遮罩、封面占位 📖） | 改为独立控件 + `IsVisible` 绑定 + `Transitions` 动画 |
| 2 | `repeat(auto-fill,minmax(160px,1fr))` | Avalonia 无等价物：`ItemsControl` + `WrapPanel`，由 VM 按容器宽算列数/ItemWidth；或 `Grid` 动态 `ColumnDefinitions`。建议书卡固定 172px、列数=floor((W+24)/(172+24)) |
| 3 | CSS `rgba()` 颜色 | XAML 用 `#AARRGGBB`；不要直接粘 rgba |
| 4 | `135deg` 渐变 | `LinearGradientBrush StartPoint="0%,0%" EndPoint="100%,100%"` |
| 5 | 多层/彩色阴影 | `Border.BoxShadow="0 4 12 0 #14000000"`；彩色阴影直接用带 alpha 的品牌色 |
| 6 | `hover` | 样式选择器 `:pointerover`；按下 `:pressed`；禁用 `:disabled`；焦点 `:focus-visible` |
| 7 | 书卡 hover 上浮 + 缩放 | `RenderTransform` 组合 `TranslateTransform`+`ScaleTransform`，配合 `TransformOperationsTransition` |
| 8 | 滚动条样式 | Avalonia `ScrollBar` 模板重写成本高；先接受默认，再逐步套 6–8px 细滚动条 |
| 9 | emoji 图标 | Windows emoji 字体与矢量图标混排不稳定 → 全部换 `PathIcon`/矢量 |
| 10 | 字体 | 只用系统栈；漫画渲染字体另行引入（OFL），禁止从 Saber `fonts/` 拷贝 |
| 11 | 深浅切换 | `ThemeVariant` + `ThemeDictionaries`；渐变两端都要给 dark 值 |
| 12 | 大列表性能 | 书架若上百本：`ListBox`+`VirtualizingStackPanel`（不支持 Wrap）→ 用分页或 `ItemsRepeater`；避免一次生成全部卡片 |
| 13 | 对话框 | 用 `Window`（`ShowDialog`）或 App 内 `Overlay` 层；遮罩色 `nm-scrim`，面板 `nm-shadow-5` |
| 14 | 屏幕像素 | 令牌单位即 DIP；截图 DPR 1.5 的数值已换算，不要直接抄图像像素 |

---

## 7. 不确定 / 推断项（实现前需拍板）

| # | 内容 | 依据 | 风险 | 建议 |
|---|---|---|---|---|
| U1 | 详情对话框宽度 900px（`large` 档） | 模板仅出现 1 次 `size:"large"`，未直接绑定到详情组件 | 中 | 实现时按内容自适应或固定 900，均可 |
| U2 | 新建书籍对话框宽度 600px（`medium`） | BaseModal 默认无尺寸类，推断取 medium | 低 | 固定 600 更稳 |
| U3 | 截图 DPR=1.5（IMG-02/03 同假设） | 由 IMG-01 内容宽=1352 精确反推；另两张同分辨率族 | 低 | 仅影响换算，不影响令牌 |
| U4 | 顶栏「开源免费」胶囊 | 截图有、安装版模板无 | 低 | 不放，或放设置/关于 |
| U5 | 标签 chip 计数气泡、封面数字角标 | 截图有、模板无 | 低 | 不添加 |
| U6 | 交互态（hover/focus/按下/动画时长） | 只有 CSS 声明，无运行实测 | 中 | 以 CSS 声明为准，实现后视觉走查 |
| U7 | 工作区左右栏在窄窗时的行为 | Saber 用 fixed + 独立滚动，无折叠声明 | 中 | 我们自行定义（≥1280 显示三栏，<1280 折叠侧栏） |
| U8 | 阅读器/设置页的真实布局 | 按要求不逆向 → 无证据 | — | 沿用 Figma v2，仅套令牌 |
| U9 | 工作区动作按钮的精确配色 | 截图采样受压缩影响；CSS 里同类按钮分散 | 低（本来只参考） | 用 `nm-status-*` 重设，不追求一致 |
| U10 | 「漫画分析」按钮的目标页 | 项目历史里洞察页（InsightView）已存在，但新架构四页无此页 | 中 | 暂置灰或移除 |

---

## 8. 证据总索引

| ID | 类型 | 路径 / 选择器 | 用途 |
|---|---|---|---|
| E-CSS-01 | CSS | `…\assets\index.LryjAgvf.css`：`:root`（--color-*/--spacing/--radius/--shadow/--font/--z）、`body{--text-color…}`、`.btn*`、`.card`、`.form-group`、`.settings-*`、toast | 令牌与通用组件 |
| E-CSS-02 | CSS | `…\assets\AppHeader.oavnQySz.css`：`.app-header--bookshelf/.header-content/.app-logo/.app-name/.header-links` | 顶栏 |
| E-CSS-03 | CSS | `…\assets\BookshelfView.MhjJHDb8.css`：`.book-card/.book-cover/.book-info/.book-tag/.filter-bar/.search-box/.tag-chip/.book-detail-*/.chapter-*/.tag-manage-*/.lan-access-info/.bookshelf-main/.books-grid/.empty-state` | 书架全量 |
| E-CSS-04 | CSS | `…\assets\BaseModal.DWFYGyoJ.css`：`.modal-overlay/.modal-container/.modal-{small,medium,large,full}/.modal-{header,title,body,footer}` | 对话框 |
| E-CSS-05 | CSS | `…\assets\ReaderView.B7LAIstj.css`：`.reader-header/.reader-image-wrapper/.nav-btn/.scroll-top-btn/.bg-option` | 阅读器令牌映射 |
| E-CSS-06 | CSS | `…\assets\TranslateView.B0xfhEt3.css`：`.settings-sidebar(300)/.thumbnail-sidebar(230)/.edit-panel-container(600)/.edit-toolbar/.control-btn/.drop-area/.bubble-highlight-box/.settings-card/.sidebar-title` | 工作区 |
| E-TPL-01 | JS 模板 | `…\js\BookshelfView.BJOW0Ad2.js`：BookshelfView / BookCard / BookSearch(FilterBar) / BookModal / BookDetail / TagManager / QuickTag / ConfirmToast 文案与 DOM 顺序 | 书架结构与文案 |
| E-TPL-02 | JS | `…\js\index.ChbXHnMO.js`：路由（`/`、`/translate`、`/reader`、`/insight`、`/insight/character-studio`）、导航名（书架/翻译/阅读器/漫画分析/角色工坊）、设置 store 键 | 页面清单与设置项 |
| E-TPL-03 | JS | `…\js\TranslateView.CFI2LFrT.js`：工作区动作数组 `hi`、控制条、拖放区、编辑工具栏、检查器、设置弹窗 tabs、页面选择 | 工作区 IA |
| E-TPL-04 | JS | `…\js\ReaderView.CaXsb8AD.js`：阅读设置（图片宽度/间距/底色四预设）、上一章/下一章/回到顶部 | 阅读器令牌 |
| E-TPL-05 | JS | `…\js\AppHeader.DSyIszD_.js`：返回书架/保存进度/设置/使用教程/赞助/仓库 | 顶栏动作 |
| E-IMG-01 | 截图 | `…\ui-stack\saber-ref\bookshelf-display.png`（2488×1395） | 书架观感 |
| E-IMG-02 | 截图 | `…\saber-ref\interface.png`（2556×1377） | 工作区观感 |
| E-IMG-03 | 截图 | `…\saber-ref\Editor.png`（2559×1401） | 编辑模式观感 |
| E-CFG-01 | 配置 | `E:\software\Saber-Translator\config\user_settings.json` | 30 个设置键 |
| E-HTML-01 | HTML | `…\static\vue\index.html` | 标题/语言 |

---

## 附录 A：Saber 设置项键（30 个，供设置页/工作区对照，`E-CFG-01`）

`aiVisionOcr` `autoSaveInBookshelfMode` `auxYoloConfThreshold` `auxYoloOverlapThreshold` `baiduOcr`
`boxExpand` `enableAuxYoloDetection` `enableSaberYoloRefine` `enableVerboseLogs` `hqTranslation` `hybridOcr`
`lamaDisableResize` `ocrEngine` `paddleOcrVl` `parallel` `pdfProcessingMethod` `pluginAgent` `preciseMask`
`proofreading` `providerConfigs` `removeTextWithOcr` `saberYoloRefineOverlapThreshold` `settingsSchemaVersion`
`showDetectionDebug` `sourceLanguage` `targetLanguage` `textboxPrompt` `textDetector` `textStyle`
`translatePrompt` `translation` `useTextboxPrompt`

> 含义速览：OCR 引擎/语言、混合 OCR、YOLO 辅助检测（置信/重叠阈值）、气泡遮罩与修复（LAMA/填充/缩放）、翻译/高质量翻译/校对服务商与提示词、文本样式默认、PDF 处理方式、并行数、插件 Agent、书架模式自动保存、详细日志。
> 〔可自由发挥〕新架构设置页字段不必逐项对齐；此表用于「别漏掉重要能力」。

## 附录 B：许可证与字体

1. Saber-Translator 为 GPL-3.0；本规格文件不含其源码，仅含观感数值与界面文案。实现阶段若移植其 CSS/组件代码，须保留版权与许可声明，并整体按 GPL-3.0（或含 AGPL 组件时的 AGPL-3.0）分发。
2. 随包字体：`_internal\src\app\static\fonts\` 26 个文件，含 Arial Unicode、汉仪瑞意宋 75W、汉仪正圆-65W、华康抖抖体、字体管家天天晴宋、ST*（华文）系列、msgothic/msyh（系统字体）等 → **均不得随我们产品分发**。界面字体用系统栈；漫画排版字体须另采 OFL/Apache 字体（如思源黑体、Noto Sans JP）并记录授权。
3. 图标：Saber 用 emoji 与 `/pic/*.png`（logo、GitHub 头像、收款码）；我们只用自有资源，不拷贝其图片。

## 附录 C：本任务未覆盖 / NOT_RUN 清单

- 未启动 Saber → 所有运行时行为（加载时序、错误重试、并发、进度反馈节奏）未实测。
- 书籍详情 / 新建书籍 / 标签管理 / 快速加标签 / 确认框 / 空态 / Toast：无截图，仅静态反推（上表已标 NOT_RUN）。
- 阅读器与设置页布局：按要求不逆向。
- 工作区编辑态的精确像素（面板宽度 600 是 CSS 值，截图裁切无法复核）；页面选择对话框仅取结构。
- 暗色：Saber 无实现，dark 令牌为新增建议值（未做截图对照）。
