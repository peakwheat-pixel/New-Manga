# UI / UX / GUI 设计契约（TASK-059 候选提案）

> 状态：**候选提案 + ND-1 已选组合稿 F**。本文档与视觉参考由 TASK-059 产出，尚未被任何实现 Task 释放。
> 视觉真值：[doc/design/ui-reference.html](../design/ui-reference.html)（离线可开，浏览器直接打开）。
> 机器可读副本：[tokens-cand-a.json](../design/tokens-cand-a.json) / [tokens-cand-b.json](../design/tokens-cand-b.json) / [tokens-cand-c.json](../design/tokens-cand-c.json) / [tokens-cand-d.json](../design/tokens-cand-d.json) / [tokens-cand-e.json](../design/tokens-cand-e.json) / [tokens-cand-f.json](../design/tokens-cand-f.json)（由 `verification/TASK-059/export-tokens.py` 生成；每份 42 色令牌 × 2 主题 + 21 项几何，含 `card-w`）。
> 边界：本文档不修改 D01～D08、[ui-baseline](../ui-baseline.md) 的任何条文；与其冲突时以 D 文档为准，冲突记入 §13 待决项。所有色值/尺寸当前为 HTML/Chromium 呈现，**非 Qt 实现值**，不构成任何 D08 AC 的 PASS。
> 版本：R4（2026-09-19）。R1 交付 A/B/C 三候选；R2 按用户当日指示增补 D/E 两候选（「完全不一样」的范式级差异，见 §6A/§6B 与 DDR-8），审计矩阵由 30 组合扩至 50 组合。**R3 按 Review（`TASK-059-db366da`）收口**：徽标对比度改按真实 `*-soft` 合成底审计并统一加深亮色状态文字令牌（§7.2）、补齐命令面板契约与 D/E 实现切片（§6B/§10/§11）、实现真实重叠检测并补判别力证据（§15）。**R4 执行用户裁决 ND-1（DDR-9）**：新增组合候选 F「Graphite Atelier」（A 色板 + B 几何、IA 继承 A，§3/§6C），F 为**已选方向**；审计矩阵扩至 60 组合，F 套用 R3-001 扩展对比度口径（24 对，§7.2）；A–E 保留为候选档案，不再等待裁决。**R5 按 Review（`TASK-059-04743a8`，DDR-10）收口**：F 的书架卡片宽 `--card-w` 由 A 档 132px 改为 **B 档 158px**（R4-001：ND-1「比例大小按 B」覆盖卡片宽度，IA 仅指浏览结构），`card-w` 纳入令牌几何相等断言（20→21 项）；补 `f-light-bookshelf.png`（R4-002，截图 49→50）；辅助脚本说明统一为 a–f / D1–D3 并清理死变量（R4-003）；证据全量重跑。

---

## 1. 文档定位与真值链

| 层 | 文件 | 角色 |
|---|---|---|
| 决策与规格 | 本文 | 六候选（含 ND-1 组合稿 F）的规格、IA 声明、Gap、DDR、待决项 |
| 视觉真值 | `doc/design/ui-reference.html` | 全部令牌、组件、页面视图的唯一呈现载体；带评审 chrome（候选/主题/玻璃/DPI/审计按钮） |
| 机器可读副本 | `doc/design/tokens-cand-*.json` | 每候选 42 色令牌 × 2 主题 + 21 项几何（含 `card-w`）+ 玻璃参数；与 HTML 不一致时以 HTML 为准 |
| 验证证据 | `verification/TASK-059/` | 审计与判别脚本、60 组合审计矩阵（含徽标真实合成底）、50 张截图、令牌导出脚本 |

评审 chrome（候选切换、审计按钮、framecap 标注）是参考页的评审工具，**不是产品画面**；产品画面只有 `#frame` 内的内容。

## 2. 方向宣言：对 TASK-047 三条否决理由的回答

TASK-059 取代被否决的 TASK-047 设计切片（裁决记录见 [TASK-047](../tasks/TASK-047.md) 末尾）。五个候选正面回答三条否决理由，且在候选中**可指认**：

- **R-1（视觉方向不对：继承灰蓝色板）** → 五候选各自给出完整色彩系统，没有一个沿用 ui-baseline 的 `#4f6bed` 蓝。A 用中性暖灰黑 + 靛蓝 `#4d63e8`；B 用暖纸白 `#f7f5f1` + 青瓷 `#0f766e`；C 用中性冷灰 + 靛青 `#5b5fe8` 且以材质（玻璃）为第二识别维度；D 用纸白 + 墨黑 + 朱砂红 `#b3391b`；E 用深蓝黑 + 琥珀 `#e2b34d`。全部令牌对（panel 直底 + 徽标 `*-soft` 真实合成底）通过 4.5:1（文本）/3.0:1（非文本）审计。
- **R-2（布局照搬现状）** → 六候选不是同一布局换色：A 重排工作台 Inspector 信息层级（译文置顶，§4）；B 把书架章节从行升级为大卡（§5）；C 根本改变书架导航模型为两级浏览（§6）；D 把一级导航从左侧 rail 重排为顶部导航条并改用编辑部排版网格（§6A）；E 把书架从卡片网格改为数据表格并以命令面板为核心交互（§6B）；F 是 ND-1 的组合方向（A 色板 × B 几何、IA 继承 A，§6C）。四页一级骨架不变（D01 §1 约束，所有候选遵守）。
- **R-3（太保守：取证盖过提案）** → 本契约以提案为主体：§4～§6C 是六个完整可裁决的方向（F 经 ND-1 已被选定）；TASK-047 的 81 条 As-Is 取证不复制，只保留仍然成立的硬事实（§12）与 Gap 矩阵（§11）。

五条候选共同的设计第一原则：**内容（漫画页）是主角，界面退后**——低饱和底色、状态色只用于语义信息、强调色克制（仅主操作与选中态）。

## 3. 六候选总览

| 维度 | A · Graphite 石墨 | B · Atelier 画廊 | C · Duo 双面+玻璃 | D · Vermilion 朱砂 | E · Amber 琥珀 | **F · Graphite Atelier（ND-1 已选）** |
|---|---|---|---|---|---|---|
| 一句话 | 暗色优先的高密度工作室 | 亮色优先的暖纸画廊 | 画廊（书架/阅读器）× 车间（工作台）+ 局部玻璃 | 顶栏导航的编辑部/印刷排版 | 等宽表格 + 命令面板的控制台 | **ND-1 组合稿：A 的色彩与视觉语言 × B 的密度与圆角** |
| 默认主题 | 暗色（亮色完整提供） | 亮色（暗色完整提供） | 双面各自默认：画廊亮、车间暗 | 亮色（暗色完整提供） | 暗色（亮色完整提供） | **暗色（亮色完整提供）** |
| 强调色（暗/亮） | `#4d63e8` / `#4356d6` | `#3ecfbd` / `#0f766e` | `#5b5fe8` / `#4f46e5` | `#d9542e` / `#b3391b` | `#e2b34d` / `#996c0d` | **`#4d63e8` / `#4356d6`（继承 A）** |
| 底色气质（默认主题） | 中性暖灰黑 `#1a1a1d` | 暖纸白 `#f7f5f1` | 书架暖纸白 `#f3f4f6`/车间冷黑 `#15161a` | 纸白 `#f7f5f2` + 墨黑 | 深蓝黑 `#0c0e12` | **中性暖灰黑 `#1a1a1d`（继承 A）** |
| 控件高 / 行高 / 基准字号 | 28 / 32 / 12px | 36 / 42 / 13px | 32 / 36 / 13px | 32 / 34 / 13px | 26 / 26 / 12px | **36 / 42 / 13px（继承 B）** |
| 圆角（sm/md/win） | 4 / 6 / 10px（硬朗） | 8 / 11 / 16px（圆润） | 6 / 9 / 14px（中间） | 2 / 4 / 8px（印刷锐利） | 2 / 3 / 6px（终端直角） | **8 / 11 / 16px（继承 B，圆润）** |
| 一级导航形态 | 左 rail | 左 rail | 左 rail | **顶部导航条** | 左 rail（48px）+ 全局命令条 | **左 rail（继承 A；ND-1 不启用 D 顶栏）** |
| 玻璃材质 | 无 | 无 | 有（浮层专用，开关可切） | 无 | 无 | **无（ND-1 不启用 C 玻璃）** |
| 字体 | 系统 UI 字 | 系统 UI 字 | 系统 UI 字 | 系统 UI 字（标题衬线） | **全 UI 等宽** | **系统 UI 字（继承 A）** |
| 书架 IA | 单级：作品网格 → 章节列表（现状模型） | 单级：作品网格 → 章节大卡 | **两级浏览：书墙 → 章节页** | 单级网格 + 编辑部大标题排版 | **数据表格清单** | **单级：作品网格 → 章节列表（继承 A；ND-1 明确不继承 B 的章节大卡）** |
| 工作台 IA | Inspector 译文置顶（校对流优化） | Inspector 按数据模型分组 | 同 B | 同 B + hairline 网格面板 | 同 B + 等宽数据密集 | **Inspector 译文置顶（继承 A）** |
| 命令面板（Ctrl+K） | 无 | 无 | 无 | 无 | **有（新交互机制，ND-9）** | **无（ND-1 不启用 E 命令面板）** |
| 一屏信息量 | 最高 | 最低 | 中 | 中 | 最高（文本行） | **中高（A 的信息结构 × B 的宽松尺寸）** |
| 触达目标高度 | 28px | 36px | 32px | 32px | 26px（显式例外，§9） | **36px（继承 B，六候选最宽松）** |
| 视图截图 | `a-dark-*.png` ×5 + `a-light-workbench` | `b-light-*.png` ×5 + `b-dark-workbench` | `c-light-*.png` ×5 + `c-dark-workbench` + 玻璃对照 ×4 | `d-light-*.png` ×5 + `d-dark-workbench` + 工具窗 | `e-dark-*.png` ×5 + `e-light-workbench` + `e-dark-palette` | **`f-dark-*.png` ×5 + `f-light-workbench` + DPI150 + TaskDetail（§15）** |
| 适合谁 | 长时间批处理监控、多任务并行的重度用户 | 以阅读与整理为主、偏好纸质氛围的用户 | 想要「书架像书房、车间像工作台」两种心智的用户；愿承担玻璃实现风险 | 偏好出版物气质、希望内容区全宽不被侧栏挤压的用户 | 键盘重度用户、数据密集取向、把库当流水线管理的用户 | **用户 ND-1 裁决的组合方向：A 的沉稳暗色工作台气质与状态语言 + B 的宽松可读密度（DDR-9）；A–E 自此为候选档案** |

## 4. 候选 A · Graphite 石墨

**角色定位**：暗色优先工作室。漫画页（多为白底）在暗环境中成为视觉焦点，长时间盯批处理进度不易疲劳；高密度让 1024×640 DIP 的最小窗口装下尽可能多的信息。

**令牌**：完整值见 `tokens-cand-a.json`。关键锚点：暗色 accent `#4d63e8`（`--on-accent` 白字对比 4.92:1）、亮色 accent `#4356d6`；暗色文字层级 `--ink #ececee / ink-2 #a9a9b3 / ink-3 #91919c / ink-dis #70707b`；状态色与 B/C 共用同一组字面值（§7）。

**IA 声明**：
- 书架：维持现状模型——作品卡片网格，选中作品后下方（或侧方）章节列表。
- 工作台：四区 + TaskProgress 不变；唯一重排是 **Inspector 分组顺序**——译文编辑器置顶，OCR 原文、Region 数据模型、样式控制依次在下。理由：人工校对的主要动作是「看译文、改译文」，原文是参照物；现状顺序（参照物在前）让高频内容沉在面板底部。
- 实现注记：参考 HTML 用 CSS `order` 表达该重排；QML 实现时用显式布局顺序（ColumnLayout 子项排列），不依赖任何 order 语义。

**代价取舍**：暗色优先意味着亮色是次等公民（仍完整提供并通过审计）；28px 控件高度对指针精度是 A/B/C/D 四候选中最紧的（仍 ≥28px 底线，§9；E 的 26px 为显式例外）；中性灰黑缺少 B 的「气质」，靠密度与秩序取胜。

## 5. 候选 B · Atelier 画廊

**角色定位**：亮色优先画廊。暖纸白底色贴近纸质漫画的阅读记忆；青瓷强调色避开「默认蓝紫」的工程感；宽松密度与 11–16px 圆角制造「作品集」而非「工具」的氛围。

**令牌**：完整值见 `tokens-cand-b.json`。关键锚点：亮色 accent 青瓷 `#0f766e`（白字 4.99:1）、暗色 accent 亮青 `#3ecfbd`（深字 `--on-accent #062e2a` 4.5:1 级）；暗色 `--ink-3` 已从初稿 `#8a8478`（4.32:1，审计 FAIL）调亮至 `#948e80`（4.92:1）——这是审计驱动修正的实例。

**IA 声明**：
- 书架：作品网格保持；章节列表升级为**大卡**（封面缩略 + 标题 + 摘要 + 状态徽标 + 操作按钮，行高 58px）。信息密度换可读性与「翻书」体感。
- 工作台：Inspector 按数据模型分组（Region → OCR 原文 → 译文 → 样式），与现状顺序一致——B 的差异化在书架与整体气质，不动工作台信息层级。
- 亮/暗两套主题都完整；暗色是暖灰黑（`#191817` 底），不是 A 的中性黑。

**代价取舍**：42px 行高 + 58px 章节卡在 1280×800@150%（仅 853×533 DIP 可用，§12）下可视条目数明显少于 A；暖底色对黑白日漫页的周围色彩感知有轻微影响（演示于 `b-light-*` 截图，属可接受范围）。

## 6. 候选 C · Duo 双面 + 玻璃

**角色定位**：书架与阅读器是「画廊/书房」（亮、暖、展示性），工作台是「车间」（暗、冷、高密度工具性）。两种心智各有自己的默认主题；玻璃材质只出现在浮层，作为画廊面的点缀与车间面工具窗的可读性手段。

**玻璃契约（本候选的差异化核心，也是实现风险所在）**：

1. **玻璃只承载容器与控件，永不直接承载裸文本**。需要可读文字的场合，内容落在 scrim 上：`color-mix(in srgb, var(--bg-panel) 55%, transparent)`。这让对比度审计无需猜测玻璃背后的像素——文本永远落在确定性底色上。
2. 参数：行内浮条（阅读器顶部条、书架顶栏）blur 22px / saturate 1.5；工具窗 blur 26px / saturate 1.6。玻璃底 `--glass-bg`（暗 `rgba(26,27,33,.56)`、亮 `rgba(255,255,255,.58)`）+ 1px 内描边 `--glass-bd` + 顶部高光 `--glass-hi`。
3. **玻璃必须可整体关闭**（设置项，见 §13 ND-2）：off 时全部浮层退化为实体 `--bg-panel` + `--divider` 描边，无半透明。开关只影响材质，不影响布局与令牌语义。对照截图：`c-glass-on/off-*`。
4. 应用范围（仅此四处）：阅读器浮动 chrome（`.rfloat`）、工具窗（TaskDetail 等 `.fwin.glass`）、书架顶部工具栏（`.tb.glassable`）、阅读器顶部条（`.rtb`）。**不用于** rail、面板、页面本体。

**IA 声明（书架两级浏览）**：
- 一级「书墙」：作品大卡网格，纯展示（封面 + 书名 + 进度概要）。
- 二级「章节页」：进入单部作品后显示章节大卡列（同 B 的章节卡），带返回层级的面包屑。
- 这是 A/B/C 三候选中唯一改变书架导航模型的提案（D/E 的书架形态变化见 §6A/§6B），**需要用户裁决**（§13 ND-3）；若否决两级浏览，C 退化为「B 的书架 + 车间工作台 + 玻璃」仍成立。
- 工作台：Inspector 同 B（数据模型分组）。

**代价取舍（务必在裁决前读完）**：
- **实现风险是五候选中最高的**：Qt Quick 没有 CSS `backdrop-filter` 的原生等价物，需要 MultiEffect/ShaderEffectSource 分层采样或等价方案；且受 D07 §4.4（主线程禁令）与 §95（虚拟化/性能）约束。进入实现前必须先过独立 PoC 切片（§11 S-GLASS），PoC 不过则玻璃降级为「半透明纯色浮层」（无 backdrop 采样），契约允许该降级。
- 双面语言意味着两套默认主题，全局令牌维护成本高于 A/B。
- 两级浏览比单级多一次点击才能到章节操作。

## 6A. 候选 D · Vermilion 朱砂

**角色定位**：编辑部/印刷。一级导航从左侧 rail **重排为顶部导航条**，内容区获得 1280 DIP 全宽；排版借鑑杂志与报纸的编辑网格——大号衬线标题、黑色规则线、直角细边框、朱砂红作为唯一强调色。面向「希望工具退成一份出版物」的用户。

**令牌**：完整值见 `tokens-cand-d.json`。关键锚点：亮色（默认）accent 朱砂 `#b3391b`（白字 5.7:1）、暗色 accent `#d9542e`（深字 `--on-accent #24100a` 5.3:1）；纸白 `#f7f5f2` 页底 + 纯白面板 + 墨黑 `#1c1a17` 正文；圆角 2–8px 全线锐利；投影极轻（印刷平感）。

**IA 声明**：
- **一级导航：顶部导航条**（本候选的范式差异，ND-8 需用户裁决）。四页同级不变（D01 §1），仅导航件的形态与位置变化：横排 tab + 底边 2px 朱砂选中指示 + 左端品牌色块。四页常驻与 `nav-*` objectName 不变——变的是容器布局（QML 中 rail 从 Left 改 Top 或等价实现）。
- 书架：单级网格（现状模型）+ **编辑部页头**——衬线大标题「书架」+ 概要行 + 黑规则线（朱砂短段），正文不使用衬线。标题字体栈 `"Source Han Serif SC","Noto Serif SC","SimSun",serif`（系统字体 fallback，字体资产的打包与许可属实现 Task 范围，可用性不阻塞——fallback 到系统 UI 字仅损失气质不损失功能）。
- 工作台：五区不变；面板语言从「底色块」改为 **hairline 网格**——面板与页底同色，以 1px `--divider` 分隔（报纸版面），视觉噪音更低。
- 亮/暗两套完整；暗色是暖黑（`#16130f` 底），「夜读版印刷」。

**代价取舍**：
- 顶栏导航是**导航范式变化**：横向空间被导航占用（约 52px 高），但纵向 rail 让出的空间对漫画页（竖长条）净收益更大；用户若习惯 rail 的肌肉记忆需要迁移。
- 衬线标题在低分屏（100% DPI 小字号）渲染质量依赖系统字体，实现时需验证 SimSun fallback 的观感。
- 直角 + 细线的语言对触屏不友好——本产品是桌面端（D07），可接受。

## 6B. 候选 E · Amber 琥珀

**角色定位**：控制台/幕后操作台。全 UI 等宽字体、最高信息密度（26px 行高）、书架从卡片网格改为**数据表格**、全局命令面板（Ctrl+K）作为键盘操作的核心入口。面向「把库当流水线管理、手不离键盘」的重度用户。

**令牌**：完整值见 `tokens-cand-e.json`。关键锚点：暗色（默认）accent 琥珀 `#e2b34d`（深字 `--on-accent #201804` 8.7:1）、亮色 accent 琥珀 `#996c0d`（白字 4.7:1）；深蓝黑 `#0c0e12` 底 + 冷灰文字层级；圆角 2–6px；全 UI `font-family:"Cascadia Mono","Consolas",monospace`（Windows 系统自带，CJK 回退系统中文字体——中英混排基线由系统对齐，`tabular-nums` 天然满足）。状态色沿用共享字面值（DDR-6）。

**IA 声明**：
- 书架：**表格清单**——色标 + 书名 + 话数 + 进度条 + 状态徽标 + 最近活动 + 行内操作；表头 sticky。点击行 → 右侧详情面板（与 A/B 交互一致）。表格形态是「库=数据集」心智的表达。
- **全局命令条 + 命令面板**（本候选的范式差异，ND-9 需用户裁决）：内容区顶部常驻命令条（`›` 提示符 + Ctrl K 角标）；Ctrl+K 唤出命令面板——跳转页面、打开作品、启动/筛选任务、执行最近动作。面板是**交互机制的新增**（不是新一级页面、不改 D01 四页同级；数据来源全部是已有 VM 能力的另一个入口），但按协作协议仍列为待决项由用户点头。完整交互契约见下「命令面板契约」。
- 工作台：五区不变；等宽 + 26px 密度把 Inspector 做成「字段表」（TM/约束/OCR/Provider/锁定），数据密集取向。
- 亮/暗两套完整；亮色是「纸上终端」（暖灰白底 + 琥珀）。

**命令面板契约（S-CMDPALETTE 规格，ND-9 裁决输入；实现面在对应实现 Task 内落地）**：

1. **命令模型**：`CommandDef { id, title, section, keywords, shortcutText, enabled, danger }`——纯 UI 层聚合对象；`section`（导航/打开/任务/导出/设置）对应面板分组（见 `e-dark-palette.png`）。命令注册源全部来自**既有 VM 的既有方法/信号**（导航切换、打开作品、TaskProgress 的 pause/stop/continue/restart/abandon/retry/filter、导出、设置跳转）；面板不新增、不包装业务逻辑。
2. **VM**：新增 `CommandPaletteViewModel`（上下文属性 `commandPaletteViewModel`）：`query`（输入）、`results`（只读列表模型：title/section/shortcutText/enabled/danger + 命令 id）、`selectedIndex`、`accepted(commandId)` 信号。过滤＝title+keywords 的不区分大小写子串匹配；无结果呈空态文案；`enabled=false` 的命令照常列出但置灰，并给不可用原因 tooltip。
3. **状态与失败语义**：命令的可用性**实时跟随源 VM**（如无选中作品时「打开作品」禁用）；执行目标不可用（作品已删除等）时复用既有 `commandErrorBar` 呈现错误，面板保持打开、该命令转禁用。危险动作（放弃任务等）：面板只负责**跳转/预填既有确认流**（复用 DirtyConfirmDialog 同类的危险确认窗），面板自身永不直接执行破坏性动作。
4. **快捷键与焦点**：Ctrl+K 为窗口级快捷键，焦点在任何控件（含文本编辑器）内均唤出面板；面板打开时为模态 overlay，Esc 关闭**优先级最高**；↑/↓ 在结果内循环、Enter 执行选中项；关闭（执行或 Esc）后焦点还原到唤出前的焦点对象（记录 focus owner），还原对象已销毁时回落到当前页首个可聚焦控件。
5. **IME/CJK**：过滤查询只在 IME **composition 结束后**更新（composition 期间不触发重新过滤、不移动选中项）；候选词键（如上下方向）在组合期间归 IME，不驱动面板。
6. **objectName**：候选 E 获 ND-9 批准后，S-CMDPALETTE 实现切片新增 `commandBarHost / commandPaletteHost / commandPaletteInput / commandPaletteList`，在该 Task 的 allowed_paths 与测试注册表（TASK-047 §4.7 体系的延伸）登记——本契约 §10 的「不因视觉方案新增必需 objectName」规则的**显式例外**（§10 已注明）。
7. **测试切面**：打开/关闭与焦点还原；query→results 过滤（含 CJK 组合输入不半途触发）；禁用态呈现与执行拒绝；危险命令必须经确认流；Ctrl+K 在编辑器焦点内可唤出；空态；`accepted` 到既有 VM 方法的一跳映射（不重复实现业务）。

**代价取舍**：
- **触达高度显式例外**：26px 控件高度低于本仓 §9 的 28px 底线（仍高于 WCAG 2.5.8 的 24px），是候选 E 换取密度的显式取舍，鼠标用户误触风险略升——已计入 §3 对照表与 ND-10。
- 等宽字体的中文回退在不同 Windows 机器上观感有差异（雅黑/等线 fallback），实现时需实测；数字/英文的等宽优势是确定收益。
- 命令面板需要新增命令注册与搜索的 ViewModel 面（纯 UI 层聚合已有能力，不动业务逻辑），实现成本中等；键盘习惯（G S / G W 式跳转）需要用户学习。
- 表格书架对封面驱动的浏览体验弱于 A/B/C（封面缩为色标）——有详情面板与 Tooltip 兜底。

## 6C. 候选 F · Graphite Atelier（ND-1 已选方向）

**角色定位**：ND-1 用户裁决的组合方向（DDR-9）——**色彩、状态色、亮/暗主题与视觉语言采用 A · Graphite；字号、控件高、行高、间距与面板尺寸等几何令牌采用 B · Atelier；IA 与骨架继承 A**。目标是 A 的「沉稳暗色工作台」气质叠加 B 的宽松可读密度，同时不引入 B/C/D/E 的任何范式差异。

**构成规则（组合的唯一合法口径）**：
1. **色彩令牌逐字面值继承 A**（`tokens-cand-f.json` 的 `modes` 与 `tokens-cand-a.json` 完全一致，含 R3 深化后的亮色状态文字令牌与全部 `*-soft`）；交叉核对由 `export-tokens.py` 生成物保证，审计日志另有 `F = A color palette + B geometry (incl card-w): OK` 断言。
2. **几何令牌逐项继承 B**（fs/ctl-h/row-h/rail-w/pad-page/gap/rad/tb-h/list-w/insp-w/prog-h/det-w 20 项 + 书架卡片宽 `--card-w`=158px，共 **21 项**——R5 起 `card-w` 纳入 `tokens-cand-f.json` 的几何相等断言，Review R4-001）。
3. **IA 继承 A**：书架**单级浏览结构**（作品网格 → 章节列表）——ND-1 明确**不继承 B 的章节大卡**（指两级浏览结构与分区，不含尺寸）；卡片宽度属几何、随 B 取 158px（R5 修正，DDR-10）。工作台 Inspector 译文置顶重排同 A（§4）。ND-1 同时排除：C 玻璃、D 顶栏导航、E 命令面板——F 的参考页无任何这三者的响应规则，玻璃变量虽随色板保留但永不启用（同 A）。
4. **圆角气质变化是几何继承的必然结果**：A 的 4/6/10px 硬朗圆角被 B 的 8/11/16px 取代，这是 ND-1「间距/面板尺寸按 B」的题中之义；除此之外无任何 B 视觉语言（暖纸白、青瓷、画廊投影）进入 F。

**R3-001 扩展审计口径（组合稿专属）**：F 在既有 22 对（15 直底 + 7 徽标合成底）之上追加两对，阈值均 4.5:1——`st-skip-direct/panel`（`--st-skip` 作直接文本色 × panel 直底）与 `ink/selected-row`（`.sel` 选中行底 = `accent-soft` 以 alpha 叠 panel 的合成底 × 行内主文本 `--ink`）。实测 dark 7.22:1 / 11.34:1、light 同口径全 PASS；判别力 D3：注入低对比 skip 回归值 → `st-skip-direct/panel=3.01` FAIL（§15）。A–E 维持 22 对既有证据口径不变。

## 7. 令牌体系（跨候选通用结构）

### 7.1 命名空间

令牌 kebab-case，与 HTML `--var` 去前缀一致；六组语义族（每族完整值见 JSON）：

| 族 | 令牌 | 语义 |
|---|---|---|
| 底色 | `bg-page/rail/panel/raised/inset/canvas/hover/active/press` | 页面、导航、面板、浮起、内嵌、画布衬底、三态反馈 |
| 线 | `border / border-strong / divider` | 控件描边、强描边（焦点外框/危险）、分隔 |
| 文字 | `ink / ink-2 / ink-3 / ink-dis / ink-inv` | 主文、次文、辅助、禁用（≥3:1）、反色 |
| 强调 | `accent / accent-hov / accent-press / accent-text / accent-soft / on-accent` | 主操作唯一来源 + 三态 + 低饱和底 + 其上文字 |
| 状态 | `st-ok / st-run / st-warn / st-fail / st-skip / st-lock / st-block`（+`-t` 文本级变体）+ `*-soft` 底 | 见 §7.2 映射 |
| 其他 | `focus / shadow / shadow-sm` | 焦点环（2px）、两级投影 |

### 7.2 状态映射（三重编码）

**任何状态不得仅靠颜色承载**：badge = 字形 + 颜色（`*-soft` 底 + `st-*` 字）+ 文本，三者齐备。对比度按**徽标真实背景**审计：`*-soft` 是 rgba，以 alpha 叠加 panel 合成后与文字令牌比较，阈值 4.5:1（徽标字号 `--fs-sm`，不适用大字号 3:1 豁免）；panel 直底场景另按 15 对直底令牌审计。审计矩阵 60 组合：A–E 各 50 组合 × 22 对（15 直底 + 7 徽标合成底），**组合稿 F 另加 R3-001 扩展对共 24 对**（§6C）——全部 PASS（§15）。

**审计驱动修正记录（R3）**：徽标真实底口径下，五个候选的亮色主题均有状态文字低于 4.5:1（如 warn 4.22 / ok 4.44 / lock 4.36 / block 4.31，E 候选 7 对中 6 对不达标）；修法为**亮色状态文字令牌统一加深一档**（`st-run #0969da→#0550ae`、`st-ok-t #1a7f37→#116329`、`st-warn-t #9a6700→#7d5200`、`st-fail #cf222e→#c01c28`、`st-lock #8250df→#6639ba`、`st-block #bc4c00→#953800`，B 亮色的候选个性字面值一并对齐），`*-soft` alpha 不动、暗色主题不动；修正后徽标底对比度全候选 ≥5.1:1。判别力证据：回退旧值即 FAIL（`badge-warn/st-warn-t=4.22`），见 `verification/TASK-059/discriminate-r001-r004.sh`。

**R3-001 扩展对（R4，仅组合稿 F）**：Review `07397ac` 的非阻塞项 R3-001 要求组合稿覆盖两类此前未直接审计的场景——① `--st-skip` 作为**直接文本色**（此前只经 `ink-2` 代言徽标字面，skip 色自身无直底对）；② **选中行合成底**（`.sel` 行以 `accent-soft` 半透明底叠 panel，行内 `--ink` 文字的真实对比此前未入对）。F 的审计面因此为 24 对；两对实测 dark 7.22 / 11.34、light 同口径 PASS，判别 D3 见 §15。

PipelineRun 九态（D01 §4 / 05 §61 语义，UI 呈现归本契约）：

| Run 态 | 底/字令牌 | 字形+文本 | 主操作 |
|---|---|---|---|
| Pending 等待 | `bg-inset`/`ink-2` + `ink-3` 点 | ○ 等待 | — |
| Running 运行中 | `run-soft`/`st-run` | ● 动点 + 运行中 | 暂停 / 停止 |
| Paused 已暂停 | `bg-inset`/`ink-2` | ⏸ 已暂停 | 继续 / 停止 |
| Blocked 阻塞 | `block-soft`/`st-block` | ⊘ 阻塞 n | 查看原因 · 重新规划 |
| Interrupted 中断 | `warn-soft`/`st-warn-t` | ⚠ 已中断 | 继续 / 重新开始 / 放弃 |
| Completed 完成 | `ok-soft`/`st-ok-t` | ✓ 已完成 | — |
| CompletedWithFailures | `warn-soft`/`st-warn-t` | ✓! 已完成（有失败） | 查看失败 · 重试失败页 |
| Failed 失败 | `fail-soft`/`st-fail` | ! 失败 | 查看错误 |
| Cancelled 已停止 | `skip-soft`/`ink-2` | ■ 已停止 | 保留已提交成果（提示） |

页级六态：○ 等待（中性）/ ● 处理中（run）/ ✓ 已完成（ok）/ ↷ 跳过（skip）/ ! 失败（fail）/ 🔒 已锁定（lock）。阶段徽标：已 OCR / 已翻译用 run 色，已修复 / 已渲染用 ok 色。

**叠加语义不合并**：处理状态、校对状态、Lock 是三种语义，UI 不用单一徽标合并；锁定用角标，需校对用画布虚线框（见 states 评审页与 `a-dark-workbench.png`）。「已完成（有失败）」必须整批呈现为成功底 + 警示字，不得整批判失败（D01 §4）。

### 7.3 主题与玻璃开关矩阵

每候选 2 主题（A/F 暗默认 / B 亮默认 / C 双面 / D 亮默认 / E 暗默认）；候选 C 另有玻璃 on/off。用户级主题记忆与切换入口属实现切片，设计默认值见 §3 表；玻璃 off 不是「低配主题」而是同一主题的材质开关。

## 8. 布局、窗口与 DPI

### 8.1 固定骨架（六候选一致，承接 D05）

四页一级导航 rail（书架/工作台/阅读器/设置，含 4Hz 刷新节流徽标位；候选 D 将该 rail 重排为顶部导航条，见 §6A/ND-8；**ND-1 为 F 保留 rail**）；工作台五区（Toolbar / PageList / Viewer / Inspector / TaskProgress）同时常驻；最小组件宽继承 TASK-047 §5.2 硬事实（PageList 展开 176 / 折叠 36，Inspector 264–288 按候选，TaskProgress 展开 132–150 / 折叠 40）。六候选差异只在密度令牌、导航形态与内部布局顺序，不改骨架与 objectName（§10）。F 的最小组件宽取 B 档（Inspector 288、TaskProgress 150）——B 几何继承的组成部分。

### 8.2 DPI 模型与参考复现

沿用 D07 §8 五档（100/125/150/175/200%）与禁止后果。物理约束硬事实：1280×800 物理 @150% 仅 853×533 DIP 可用，低于 1024×640 DIP 最小窗——所有候选在 150% 下按 853×533 排版校验（HTML 参考用 `#frame`=物理窗 + `#app` transform scale 复现该模型；`a-dark-workbench-dpi150/200.png` 展示 A 档密度压力，`f-dark-workbench-dpi150.png` 展示 B 档几何在 A 信息结构下的压力——42px 行高使 150% 下的可视条目更少，降级序列更早触发）。150% 下布局策略：PageList 自动折叠、Inspector 降为覆盖层、TaskProgress 折叠为进度条——该降级序列是**实现切片规格**，六候选一致。

### 8.3 工具窗与浮层

C/D 类浮窗（05 §D 类容器）尺寸上限必须满足「853×533 DIP 内完整可用」；TaskDetail 窗设计宽 ≤470 DIP（`win=detail` 截图）。窗超界的处理是实现侧窗口管理问题（§13 ND-7），设计侧约束是：窗内内容支持滚动，任何按钮不得被裁切（审计 `clipped=0`）。

## 9. 可访问性与文本

- **对比度**：文本 ≥4.5:1、disabled/非文本 ≥3.0:1；审计矩阵 6 候选 × 2 主题 × 5 视图（A–E 每组合 22 对；**组合稿 F 24 对**，含 R3-001 扩展的 `st-skip-direct` 与选中行合成底对）全部 PASS（§15）。
- **三重编码**：§7.2；焦点环 `--focus` 2px，键盘可达全部交互件。
- **触达目标**：≥28×28 DIP（A 的 28px 控件是底线；B/F 36px 最宽松）。**候选 E 显式例外：26×26 DIP**——高于 WCAG 2.5.8 AA 的 24×24，低于本仓 28 底线，是 E 换取最高密度的显式取舍（ND-10）。**F 为 36px，无例外**。
- **CJK**：正文行高 ≥1.5；中文允许 `WrapAnywhere` 断行；标签/按钮禁止单字竖排（`b-light-bookshelf` 修复记录即此类缺陷）。
- **截断规则**（沿用 TASK-047 §5.4，全候选一致）：书名 ElideRight + ToolTip 全名；文件名 ElideMiddle；按钮文字不得 elide（放不下就缩写文案）；数字列 `tabular-nums` 右对齐。
- **动效**：浮层出现 120–160ms ease-out；rail 选中指示位移 ≤100ms；进度条平滑推进；遵循系统 reduce-motion 设置（实现侧映射 Qt 整果关闭）；虚拟化长列表不做进入动画（D07 §95）。

## 10. ViewModel / objectName 映射

**规则**：设计不重命名任何既有 objectName，不因视觉方案新增必需的 objectName；实现切片如需新 objectName（如玻璃开关设置项控件），在对应实现 Task 的 allowed_paths 内登记。**显式例外（R3 消解与 §11 的矛盾）**：候选 E 获用户裁决（ND-9）后，`S-CMDPALETTE` 切片新增 `commandBarHost / commandPaletteHost / commandPaletteInput / commandPaletteList` 四个 objectName（契约见 §6B「命令面板契约」），在该实现 Task 的 allowed_paths 与测试注册表登记；ND-9 未批准前不得预建。测试钉住面以 TASK-047 §4.7 注册表 + 现行代码为准：

| 设计概念 | QML 组件（现状） | objectName（钉住） | VM 绑定（现状，WorkbenchView.qml:20-40） |
|---|---|---|---|
| 一级导航 | Rail 按钮 | `nav-bookshelf/workbench/reader/settings`、`page-*` | 导航状态 |
| 工作台根 | `WorkbenchView.qml:17` | `workbenchView` | `workbenchViewModel` 上下文属性 |
| 工具栏 | WorkbenchToolbar | `workbenchToolbarHost` | `contextInfo/viewerMode/selectedPageCount/runStatus` |
| 命令错误条 | commandErrorBar（TASK-052 provisional） | `commandErrorBar / commandErrorText / commandErrorCopyButton` | `commandErrorText`；其**视觉语言按本契约重绘但 objectName 不变** |
| 页面列表 | PageListPanel | `pageListPanelHost` | `pageListModel/viewerPageId` + select/toggle/range |
| 画布 | ViewerPanel | `viewerPanelHost` | `viewerImageUrl(For)/viewerPageName/viewerMode` |
| Inspector | RegionInspector | `regionInspectorHost` | `inspectorRegions/inspectorRegionId/inspectorText/hasDirtyEditor` |
| 进度面板 | TaskProgressPanel | `taskProgressPanelHost` | `taskProgress` + pause/stop/continue/restart/abandon/retry/filter |
| 脏确认 | DirtyConfirmDialog | `dirtyConfirmDialogHost` | `resolveDirtyConfirm` |
| 其他 | 书架/新建/统计/导出等 | `bookshelfView / newBookDialog / statFailed / exportFormat(count==5)` 等 | 按 TASK-047 §4.7 注册表 |

A 候选的 Inspector 译文置顶是**布局顺序变化**，不改 `regionInspectorHost` 接口与 VM 绑定。**组合稿 F 继承 A 的全部 objectName 面**（IA 与骨架同 A，§6C）：不新增、不重命名任何 objectName；ND-1 排除的三项范式（C 玻璃开关控件、D 顶栏容器、E 命令面板四件）在 F 下均无实现物，其 objectName 注记对 F 不适用。

**Q-011 硬编码颜色令牌映射**（`src/ui/qml/workbench/WorkbenchView.qml` 中绕过令牌系统的取值，实现改动不在本设计 Task 范围内，由 S-TOKEN/实现 Task 执行）：

| 位置 | 现值 | 用途 | 目标令牌（按所选候选） |
|---|---|---|---|
| `WorkbenchView.qml:18` | `#f5f5f4` | 工作台根底色 | `bg-page` |
| `WorkbenchView.qml:89` | `#fef2f2` | commandErrorBar 底 | `fail-soft` |
| `WorkbenchView.qml:90` | `#dc2626` | commandErrorBar 描边 | `st-fail` |
| `WorkbenchView.qml:107` | `#991b1b` | commandErrorBar 文字 | `st-fail` |
| `WorkbenchView.qml:159,171,191` | `#e7e5e4` | 五区分隔线 | `divider` |

## 11. Gap 矩阵与实现切片建议

Gap 沿用 TASK-047 §7 编号中仍然成立的部分，按候选差异化重述；完整建议切片（每个都是独立实现 Task，需 Codex 释放）：

| 切片 | 内容 | 适用候选 | 依赖/风险 |
|---|---|---|---|
| S-TOKEN | 建立 QML 单一令牌源（Theme singleton），灌入所选候选 JSON；全 UI 去硬编码色（含 `WorkbenchView.qml:18` 的 `#f5f5f4` 根色） | 选中候选（**F 已由 ND-1 选定**） | 无；其余切片的前置 |
| S-A11Y | 对比度/焦点环/触达/截断规则落地 + 对应测试 | 全部 | S-TOKEN |
| S-WIN | 最小窗与 DPI 五档降级序列（§8.2） | 全部 | S-TOKEN；TASK-047 G-8 系 |
| S-WB-INSPECTOR | Inspector 视觉重建：译文置顶重排（A/**F**）/分组梳理（B/C）/**hairline 网格面板（D，§6A）**/**等宽字段表（E，§6B）** | A/F/B/C/D/E 各自形态 | S-TOKEN；objectName 不变；E 依赖等宽字体栈 |
| S-SHELF-BOOK | 书架视觉重建：行为网格（A/**F**）/章节大卡（B）/书墙（C）/**编辑部页头+黑规则线网格（D，§6A）**/**表格行视觉语言（E，IA 归 S-SHELF-TABLE）** | A/F/B/C/D/E 各自形态 | S-TOKEN；D 页头衬线字体栈可用性不阻塞（fallback 系统 UI 字） |
| S-SHELF-L2 | 书架两级浏览 IA（仅 C，若 ND-3 批准） | C | S-SHELF-BOOK；IA 变化需用户裁决 |
| S-GLASS | 玻璃 PoC：Qt Quick backdrop 等价方案 + 性能验证（D07 §4.4/§95 约束下），不过则降级半透明纯色 | 仅 C | **最高风险**，必须最先验证 |
| S-TOPNAV | 一级导航 rail→顶部导航条重排（QML 布局重排，nav-* objectName 不变） | 仅 D | S-TOKEN；导航范式变化需用户裁决（ND-8） |
| S-CMDPALETTE | 命令面板：命令注册/搜索/执行（聚合既有 VM 能力，不动业务逻辑）+ 命令条常驻 | 仅 E | S-TOKEN；新交互机制需用户裁决（ND-9） |
| S-SHELF-TABLE | 书架表格视图（行选择→详情面板，交互同 A/B） | 仅 E | S-SHELF-BOOK 同期 |
| S-CLOSE / S-SET / S-PERF 等 | 沿用 TASK-047 §7 既有切片定义（关闭语义/设置页/性能），按所选候选令牌执行 | 全部 | 对应原文 |

**F 的切片映射（R5）**：F = ND-1 已选方向，其实现面是 S-TOKEN（灌 `tokens-cand-f.json`）+ S-WB-INSPECTOR 的 **A 形态**（译文置顶）+ S-SHELF-BOOK 的 **A 形态**（作品网格单级结构、`--card-w` 158px 随 B 几何）+ 全部共享切片按 F 令牌执行；§8.2 降级序列按 F 的 B 档几何触发（150% 压力见 `f-dark-workbench-dpi150.png`）。F 不涉及 S-SHELF-L2/S-GLASS/S-TOPNAV/S-CMDPALETTE/S-SHELF-TABLE（ND-1 已排除对应范式）。

**D/E 范式切片与共享切片的边界（R3 补，保证 Gap→实现计划不断链）**：D 的**导航重排**全责在 `S-TOPNAV`，**书架页头/hairline 工作台**的视觉语言在 `S-SHELF-BOOK`/`S-WB-INSPECTOR`；E 的**表格 IA**（列结构/行选择→详情面板）在 `S-SHELF-TABLE`，**表格行视觉语言**在 `S-SHELF-BOOK`，**字段表 Inspector** 在 `S-WB-INSPECTOR`，**命令面板**在 `S-CMDPALETTE`（契约 §6B）。每个切片的验收面＝契约 §7–§9 对应条款 + 该候选对应视图截图组合（§15 清单）。

设计相关但**不在任何候选**中变更的：四页一级骨架、TaskProgress 常驻、悬浮窗行为矩阵（05 §D）、Lock 语义。

## 12. 沿用或推翻的硬事实（AC④ 对照）

| TASK-047 / D07 硬事实 | 本契约处置 |
|---|---|
| 1280×800 物理 @150% < 1024×640 DIP 最小窗 | **沿用**；§8.2 降级序列为候选一致的规格 |
| 4 个 As-Is 文本令牌对比度不达 4.5:1 | **沿用事实，问题已被候选令牌消解**（全矩阵 PASS；B 暗 `ink-3` 修正记录见 §5） |
| 三重编码、截断规则、tabular-nums | **沿用**并升格为 §7.2/§9 契约条文 |
| 4Hz 进度刷新节流、主线程禁令、虚拟化 | **沿用**（D07 §4.4/§95；rail 4Hz 徽标位演示） |
| PipelineRun 九态语义与「已完成（有失败）」 | **沿用**；UI 呈现映射见 §7.2 |
| ui-baseline 色板 `#f5f5f4/#4f6bed` | **候选一致推翻其作为目标方向**（授权来自 TASK-059 可推翻范围；As-Is 文档本身不修改，裁决后由集成方归档） |

## 13. 待决项

**必须用户裁决**：

| # | 问题 | 关联 | 状态（R4） |
|---|---|---|---|
| ND-1 | 选择哪个候选（或组合——组合需重新审计一致性） | §3 | **已裁决（2026-09-19）**：组合稿 F「Graphite Atelier」＝A 色彩/状态色/主题/视觉语言 + B 几何（字号/控件高/行高/间距/面板尺寸）+ A 的 IA（不继承 B 章节大卡；不启用 C 玻璃、D 顶栏、E 命令面板）；一致性审计已按本契约口径重做并全 PASS（§15）。裁决记录见 STATUS 台账 2026-09-19 行与 DDR-9 |
| ND-2 | 玻璃是否进 MVP：进 → S-GLASS PoC 前置；不进 → C 降级半透明纯色或改选 A/B | §6 | **对 F 不适用**（ND-1 不启用玻璃）；仅当放弃 F 改选 C 时重开 |
| ND-3 | C 的书架两级浏览是否接受（唯一 IA 结构变化） | §6 | **对 F 不适用**（F 书架 IA 继承 A 单级） |
| ND-4 | 默认主题策略：按候选默认（A/F 暗、B/D 亮、C/E 双面）还是全局统一 + 用户记忆 | §7.3 | 仍待决（建议随 F 走暗默认，产品取舍归用户） |
| ND-5 | 主题/玻璃切换入口放在设置页还是 rail（设计建议：设置页；F 下玻璃开关不存在，只剩主题切换） | §13 | 仍待决 |
| ND-6 | A 的 Inspector 译文置顶假设（「校对主动作是改译文」）是否被工作流确认 | §4 | 仍待决——**F 继承了该重排**，此项成为 F 的实现前待决项 |
| ND-7 | 150% 下工具窗超物理窗时的窗口管理策略（设计只约束内容可滚动+按钮不裁切） | §8.3 | 仍待决 |
| ND-8 | D 的顶栏导航（rail→topbar，导航范式变化）是否接受 | §6A | **对 F 不适用**（ND-1 明确不启用顶栏；仅当改选 D 时重开） |
| ND-9 | E 的命令面板（新交互机制，聚合既有能力的新入口）是否接受 | §6B | **对 F 不适用**（ND-1 明确不启用命令面板） |
| ND-10 | E 的 26px 触达高度例外（低于本仓 28 底线、高于 WCAG 24）是否接受 | §6B/§9 | **对 F 不适用**（F 触达 36px，六候选最宽松） |

**设计可自决（实现切片内处理，不阻塞裁决）**：TK-047 Q-1～Q-10 中属视觉细节的项（间距节奏、空态插画风格、图标集选型、tooltip 触发时延、动效时长微调等）由实现 Task 按本契约 §7–§9 执行并在 Handoff 附对照截图；其中 Q 项若涉及产品语义（如「导出格式列表是否增删」）仍归用户，设计侧不扩大（TASK-059 禁止新增产品功能）。

## 14. 决策记录（DDR）

| # | 决策 | 理由 |
|---|---|---|
| DDR-1 | 交付多个实质不同的候选而非单一提案（R1 三候选；R2 由 DDR-8 按用户指示扩展为五候选） | 用户开工指令明确要求 2–3 个「视觉语言或 IA 实质不同」的方向；R2 追加指示「再增加两种完全不一样的设计」 |
| DDR-2 | 玻璃不承载裸文本、文字落 scrim（55% panel） | 使对比度审计确定性（无需猜测背后像素）；同时压低玻璃可读性风险 |
| DDR-3 | HTML 为视觉真值，JSON 由脚本生成 | 令牌一致性可复现验证（`export-tokens.py`），避免双真值漂移 |
| DDR-4 | A 的 Inspector 重排以显式布局顺序为 QML 规格 | CSS `order` 是参考实现的表达手段，不应暗示 QML 依赖运行时重排 |
| DDR-5 | `c-glass-both` 压力截图用 125% 而非 150% | 150% + 双窗超物理窗容量（§8.2/ND-7 范畴），150% 压力由专项截图单独呈现 |
| DDR-6 | 状态色字面值五候选共用 | 减少维护面；语义色跨主题一致性优先于候选个性（个性由底色/强调/密度承担） |
| DDR-7 | 不修改 D01～D08 与 ui-baseline | TASK-059 禁止范围；方向推翻只记录于 §12，文档归档由集成方处理 |
| DDR-8 | R2 增补 D/E 两候选（范式级差异：导航重排/表格化/命令面板/等宽） | 用户 2026-09-19 在 in_review 后追加指示「再增加两种完全不一样的设计」；D/E 与 A/B/C 及彼此的差异维度是范式而非样式；章节号 §6A/§6B 保持既有 §7+ 引用稳定 |
| DDR-9 | **R4 新增组合候选 F「Graphite Atelier」并标记为 ND-1 已选方向**：A 色彩/状态色/主题/视觉语言 + B 几何（密度令牌）+ A 的 IA 结构（书架单级、Inspector 译文置顶）；不继承 B 章节大卡（两级浏览结构），不启用 C 玻璃/D 顶栏/E 命令面板；组合稿按 ND-1 条款重做全套一致性审计（60 组合矩阵、F 专属 24 对含 R3-001 扩展、判别 D3）；A–E 保留为候选档案 | 用户 ND-1 裁决（2026-09-19，STATUS 台账行 + TASK-059 开工指令）；契约 ND-1 本身规定组合必须重新审计一致性，不能拼装 A/B 两份候选当实现规范 |
| DDR-10 | **R5 修正 F 规格偏差（Review `TASK-059-04743a8` R4-001，P1）**：书架卡片宽 `--card-w` 由 A 档 132px 改为 **B 档 158px**——ND-1「比例大小按 B」覆盖卡片宽度，IA 仅指浏览结构（单级 vs 两级）非尺寸；`card-w` 纳入 `tokens-cand-f.json` 几何相等断言（20→21 项，几何断言不得事后缩小验收面）；补 `f-light-bookshelf.png`（R4-002，截图 49→50 张）；辅助脚本说明统一 a–f / D1–D3、清理 `geom_sel` 死变量（R4-003）；60 组合审计、F 24 对、D1/D2/D3 全量重跑 | Review R4-001/002/003 + 用户返修指令（2026-09-19）：改 158px、断言纳入 card-w、补亮色书架截图 |

## 15. 验证证据索引

- 审计：`verification/TASK-059/run-reference-audit.sh` → JS 语法门 + 60 组合（6 候选 × 2 主题 × 5 视图）矩阵 + 50 张截图。矩阵内容＝对比度（A–E：15 直底对 + 7 徽标 `*-soft` 真实合成底对；**F：另加 R3-001 扩展的 `st-skip-direct/panel` 与 `ink/selected-row` 共 24 对**，文本 ≥4.5 / 非文本 ≥3.0）+ 溢出（outside）+ 裁切（clipped）+ **重叠（overlap，同级元素两两相交检测，R-004）**；最近一次全量结果 **60/60 ALL PASS**（F 全部组合 24/24 对；`AUDIT_EXIT=0`，日志 `audit-result.txt`）。
- 证据纪律（R-005）：`audit-result.txt` / `discriminate-result.txt` 同一日志内含**环境头**（shell/node/chrome/python 及 venv 路径）、**命令**、全量输出与 **`AUDIT_EXIT`/`DISCRIM_EXIT`**；本次口径＝Git Bash 5.2 (msys，MINGW64_NT-10.0-26200) + Chrome 153.0.8010.48 headless + node v24.15.0 + `TASK-012-py312` venv Python 3.12.3（Chrome 版本取自文件版本资源，避免 `--version` 进程在 Windows 下挂起/噪音）。
- 判别力：`verification/TASK-059/discriminate-r001-r004.sh`（日志 `discriminate-result.txt`，`DISCRIM_EXIT=0`）——**D1** 回退 A 亮色 warn 旧令牌 → 徽标对 `badge-warn/st-warn-t=4.22` FAIL（数值与复审独立复算一致）；**D2** 向 states 页注入两个相交徽标 → `overlap=1` 且输出相交元素对；**D3（R4 新增，R3-001）** 向 F 暗色注入低对比 `--st-skip` 回归值 → F 专属对 `st-skip-direct/panel=3.01` FAIL。三个检测均证明**有判别力**（非恒 PASS）。
- 截图清单（50 张）：`{a,b,c,d}-默认主题-{bookshelf,workbench,reader,settings,states}`（A 暗、B/C/D 亮）+ `e-dark-*` 同构 + **`f-dark-{bookshelf,workbench,reader,settings,states}`**（ND-1 组合稿五视图）；第二主题代表 `a-light-workbench / b-dark-workbench / c-dark-workbench / d-dark-workbench / e-light-workbench / f-light-bookshelf / f-light-workbench`；玻璃对照 `c-glass-off-{bookshelf,workbench}` + `c-glass-{taskdetail,both}`；DPI 压力 `a-dark-workbench-dpi150.png / a-dark-workbench-dpi200.png / e-dark-workbench-dpi150.png / f-dark-workbench-dpi150.png`；工具窗 `a-dark-workbench-taskdetail / b-light-danger / d-light-workbench-taskdetail / f-dark-workbench-taskdetail`；E 命令面板 `e-dark-palette`。
- 令牌：`doc/design/tokens-cand-{a,b,c,d,e,f}.json`（每份 42 色令牌 × 2 主题 + 21 项几何含 `card-w` + 玻璃参数）← `verification/TASK-059/export-tokens.py`；F 与 A 的 `modes` 逐值一致、F 与 B 的 `geometry` **逐项一致（含 `card-w`=158px，R5 起）**由生成物与审计日志断言（`F = A color palette + B geometry (incl card-w): OK`）。
- **口径**：全部结果为 HTML/Chromium 呈现，非 Qt；不构成任何 D08 AC 的 PASS，也不预支未来实现 Task 的验证。
