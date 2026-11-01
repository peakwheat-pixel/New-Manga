# FEA-04b 范围复核 r1（独立上下文）

| 字段 | 值 |
|---|---|
| base_commit | `fdf7591ac` |
| reviewed_head | `fe9535e14`（main，clean；被审 deliver 为 `568cf271e`，证据表提交为 `fe9535e14`） |
| reviewer | `fea04b-scope-reviewer` |
| reviewer 来源 | DSH Team Lead 派发，fresh 独立上下文；**未参与 FEA-04b 起草**；只读被审 head |
| 日期 | 2026-11-02 |
| 审查范围 | AC1–AC4（设计基线）。**AC5（用户确认）不在本报告范围** |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 7 / P2 = 14** |

## 0. 方法、只读声明与复现

- 只读核查被审 head；**未修改任何被审文件**，未 commit、未 push；本报告是本轮唯一新增文件。
- 核查输入：`doc/design/fluent-v1/`（README + 01–10，版本 `fluent-v1.0.0`）、`verification/FEA-04b/design-baseline-selfcheck.md`、`doc/tasks/FEA-04b.md`；上游 `FEA-C02`/`FEA-C03`/`FEA-CONTRACT-FROZEN-C02`/`C03`/`FEA-C05`/`V11R_AVALONIA_CONTRACT`/`FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL`；代码事实 `NmKeys.g.cs`、`TokenDictionaryWriter.cs`、`ShellCommands.cs`、`KeyMap.cs`、`AppShellViewModel.cs`、`ShellLayout.cs`、`Tokens.Global.axaml`、`FocusRing.cs`、`Badges.cs`、`ShellState.cs`。
- 复现命令与结果（本次实跑）：
  - `git rev-parse HEAD` → `fe9535e148552ede08e3856c0d03ea400f9eacbd`；`git status --porcelain` → 空。
  - `git diff --name-status fdf7591ac..fe9535e14` → 仅 `doc/design/fluent-v1/**`（11 新增）、`doc/tasks/FEA-04b.md`、`verification/FEA-04b/**`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`；**未触碰任何 `src/`/`apps/`/`doc/plan/` 冻结契约**。
  - `pwsh -NoProfile -File tools/governance/check.ps1` → `Governance check: PASS (2 warnings)`（WARN：9 个非终态 Task；STATUS 预算 80%）。
  - `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → `PIN AUDIT: PASS (all 15)`。
  - 证据表 sha256 **12/12 逐项复算一致**（README、01–10、selfcheck；见 §7）。

## 1. AC1 四页规格与 09 状态矩阵

**结论：部分通过。** 四页均含布局/组件令牌/状态/交互/响应式/a11y 章节，状态覆盖空/载入/错/满/部分/只读（05 §3 七行、06 §3 八行、07 §3 六行、08 §4 六行）；响应式断点四页齐（05 §5、06 §5、07 §5、08 §6）。但存在三类问题：

1.1 **「层级」未落到四页**（AC1 交付范围含「布局、层级、状态」）：四页正文均无层级专节，只有 `04-layout-responsive.md:56-63` 的全局 z-order 表；四页也没有引用该表。建议每页补「元素→层级（`Nm.ZIndex.*`）」或显式声明「层级统一引用 04 §6」。

1.2 **09 状态矩阵与四页正文不一致（P1-06）**。逐格核对结果（矩阵行 × 页）：

| 矩阵行（09） | 书架（05） | 工作台（06） | 阅读器（07） | 设置（08） |
|---|---|---|---|---|
| 空（09:8） | ✓ 05:40 | ✓ 06:44-45 | ✓ 07:41 | ✓ 08:63 |
| 空（筛选后）（09:9） | ✓ 05:41 | **✗ 06 正文无「批量筛选无结果」状态** | — | **✗ 08 正文无「搜索无匹配」状态**（08:75 只说前端过滤） |
| 载入（09:10） | ✓ 05:42 | ✓ 06:46 | ✓ 07:42 | ✓ 08:64 |
| 错误（09:11） | ✓ 05:43 | ✓ 06:47 | ✓ 07:43 | ✓ 08:65 |
| 满（09:12） | ✓ 05:44 | ✓ 06:48 | ✓ 07:44 | ✓ 08:66 |
| 部分/未决（09:13） | ✓ 05:45 | ✓ 06:49 | ✓ 07:45 | ✓ 08:67（举例仅 Fluent 材质，漏 Provider，非矛盾） |
| 冲突（09:14） | — | ✓ 06:50 | — | — |
| 只读（09:15） | ✓ 05:46 | ✓ 06:51 | ✓ 07:46 | ✓ 08:68 |
| 运行中（09:16） | **△ 与 09:13「扫描中」重复定义** | **✗ 06 正文无「运行中」状态，无「暂停/停止/重试」控制定义** | **✗ 07 正文无「进度写回中」状态**（07:54 只有写失败提示） | — |

  另有两条规则层不一致：
  - `09:20`「所有空/错误态都保留顶部命令条与**左导航**」——阅读器（浮层，07 §1）与设置页（独立 surface，08:10-22 布局无 Shell 左导航）不适用该通则。
  - `09:31`「批量 gate 未清不执行｜同（06 §4；gate 确认模态）」——06 §4 全文（06:55-59）无「gate」或「gate 确认模态」表述，引用不成立。

1.3 **共用骨架与两页布局矛盾**：`04:21` 说「顶部命令条与状态条在四页恒定；左导航可折叠」，但 07 阅读器是浮层（07:22、07:11-19 布局无左导航/无 Shell 顶部命令条）、08 设置页为独立 surface（08:3、08:10-22 无左导航）——四页共用骨架只对 05/06 成立。建议 04 §1 改为「05/06 共用骨架；07/08 为覆盖式/独立表面，各自定义骨架」（P2-07）。

**证据**：`doc/design/fluent-v1/09-state-matrix.md:8-16,20,31`；`05-page-shelf.md:36-46`；`06-page-workbench.md:40-51,55-59`；`07-page-reader.md:37-46,54`；`08-page-settings.md:3,59-68,75`；`04-layout-responsive.md:21,56-63`。

## 2. AC2 令牌

**结论：不通过。** 取值本身与 C-02 V-05 冻结定义一致，但令牌**名**有多处自造/错误，且尺寸/断点数值与既有令牌冲突且未登记缺口。

2.1 **通过项（取值与冻结定义一致）**：
- 圆角 `Nm.Corner.Fluent.Sm(4)/Md(6)/Lg(8)`（01:13,25-27）＝ C-02 `:53`/`:74` 冻结值。✓
- 材质键 `Nm.Material.Acrylic.Base/Tint/Opacity`、`Nm.Material.Mica.Enabled`（01:14,36-39）＝ C-02 `:50`；类型 `IBrush/double/bool` 一致。✓
- 层次 `Nm.Elevation.1/2/3`（01:15,47-49）＝ C-02 `:51`；`BoxShadows` 语法可解析。✓
- **「当前代码不存在这些令牌」说明诚实**：01:13「`Nm.Corner.Fluent.*` 待生成」、01:14「保留键，当前空（`TokenDictionaryWriter.cs:214` 注释）」与代码事实一致——`NmKeys.g.cs` 共 144 键，无 `Corner.Fluent.*`/`Material.*`/`Elevation.*`（`NmKeys.g.cs:55-57,271-278` 只有 Corner.Md/None/Sm）；`TokenDictionaryWriter.cs:214` 原文「Material/elevation keys are reserved (`Nm.Material.*` / `Nm.Elevation.*`) and currently empty」。✓

2.2 **令牌名自造/错误（P1-01）**。设计正文多处引用**不存在的令牌族**，且 `01:66` 把错误族名标为「既有」：
- `Nm.Surface.Raised` / `Nm.Surface.Sunken`（01:41、04:58、05:29,32、06:30,33,35、07:30,33、08:25、10:10-13,43）——V11R 合同 `:50` 与代码 `NmKeys.g.cs` 的冻结名是 **`Nm.Color.Bg.Raised` / `Nm.Color.Bg.Sunken`**（`NmKeys.g.cs` 键清单）；`Nm.Surface.*` 在代码/契约/方案中均不存在。
- `Nm.Accent.Subtle`（06:34、08:32、10:11）——冻结名是 `Nm.Color.Accent.Muted`（V11R `:53`；`NmKeys.g.cs`）。
- `Nm.Status.*`（05:34、06:36、08:34,37、10:12,16,18）——冻结名是 `Nm.Color.Status.*` / `Nm.Color.StatusMuted.*`（V11R `:54-55`）。
- `Nm.Text.*` / `Nm.Text.Color.*`（01:66、10:10,17）——冻结名是 `Nm.FontSize.*`/`Nm.LineHeight.*`/`Nm.TextLineBox.*` 与 `Nm.Color.Text.*`（V11R `:52`；`NmKeys.g.cs`）。
- `03:53`「2px `Nm.Focus.Ring` 颜色 + 1px 外扩」——C-02 `:52` 定义的焦点组是 **`Nm.Focus.Ring.Width/Offset/Color`** 三键（代码尚不存在，属待生成）；`01` 的令牌命名空间表（01:10-15）**漏列该第四组**，导致焦点环数值无落点。
- 结论：AC2 明确要求「令牌名不得自造」，而 `01 §3 判据①对表` 最后一行把不存在族名标为「既有」，FEA-05/06 照做会引用不存在的资源键。需改为冻结名，并补 Focus 组取值（Width=2/Offset=1/Color=`Nm.Border.Focus` 或 `Nm.Color.Accent.Ring` 的取舍需 DSH 裁决）。

2.3 **尺寸/断点裸值与既有令牌冲突（P1-02）**。设计给出一批**新数值**，既未走令牌，也未在 G-1 登记「需新增令牌/需 DSH 裁决」：

| 设计数值 | 位置 | 既有事实 | 冲突 |
|---|---|---|---|
| 顶部命令条高 48 | 04:12 | `Nm.Size.TopBand` = 36（`Tokens.Global.axaml:83`） | 是 |
| 状态条高 28 | 04:17 | `Nm.Size.StatusBandPage` = 28（`:81`）✓；但 Batch 变体 = 24（`Nm.Size.StatusBandBatch`） | 部分 |
| 左导航 72 / 240 | 04:15,21;05:15;06:15;08:14 | `Nm.Size.TreeWidth` = 200（`:84`） | 是 |
| 详情/检查器 320 | 05:14;06:66;08:14 | `Nm.Size.InspectorExpanded` = 320（`:68`）✓ | 否 |
| 检查器 360 | 06:14,67;05:61 | `Nm.Size.Drawer` = 360（`:63`）✓ | 否 |
| film-strip 96 / 120 | 06:22,66,67 | `Nm.Size.FilmStripCollapsed` = 56、`FilmStripExpanded` = 200（`:64-65`）；现有 `StudioFilmStrip` 明确 56↔200（`StudioFilmStrip.cs:15`） | 是 |
| 列表行高 40 / 36 / 48 | 05:31；10:26 | `Nm.Size.RowNormal` = 26、`RowDense` = 24（`:72-73`） | 是 |
| 断点 720/1024/1440/1920（四档） | 04:29-32 | 冻结三档：`Nm.Size.Breakpoint.Narrow`=1024、`Compact`=1280、`Full`=1600（`:58-60`）；`ShellLayout.cs:17-19` 明确「three frozen responsive breakpoints」 | 是 |

  且 `04:23` 自身要求「全部尺寸用 `Nm.Space.*` 令牌……不得散落裸数」，与 04/05/06/08 的大量裸数（320/360/96/120/1600/480/720/600/40）矛盾。G-1（自查:32）只登记 Corner.Fluent/Material/Elevation 三组，**未登记** Size/Breakpoint/焦点组缺口，也未登记「Fluent 布局尺寸与 Current 令牌不同值需 DSH 裁决」。这是 AC2 判据①与「令牌唯一来源」原则的实质失败。

2.4 **判据①对表覆盖不完整（P2-01）**：`01:55-66` 只列 10 行（书架卡、工作台面板、工具栏按钮、阅读器图像、浮动工具条、设置卡片、对话框、文字/间距/颜色）；未覆盖 05:32 详情栏、05:33/07:35 缩略图条、06:30 主画布容器、06:32 Region 框 1.5px、06:36 批量单元格、07:33 进度条、07:34 页码徽标、08:34 输入框、08:37 危险按钮、遮罩色（`Nm.Color.Scrim`）、焦点环。对表标题称「每个视觉数值 → 令牌」，实际未穷举四页主要视觉数值。

2.5 **裸值禁令明确性（部分）**：`01:68` 对「字面量颜色、`CornerRadius="6"`、`BoxShadows="..."`」明确判违规 ✓；但禁令未覆盖尺寸/字体/间距/层级/描边宽度；且 `06:32` 的「1.5px 描边」、`03:53` 的「1px 外扩」、`08:34` 的「1px 边框」均在禁令外。建议禁令扩为「任何视觉数值（颜色/圆角/阴影/尺寸/间距/字号/描边/层级）必须引用 `Nm.*` 或本节显式登记的设计常量」。

2.6 **材质深/浅两套值无落点（P2-02）**：`01:36-37` 给 `#FF1F1F1F`（深）/`#FFF3F3F3`（浅）两套；C-02 V-07（`:89-90`）只注册视觉主题 `builtin.fluent-dark`，浅色 Fluent 视觉主题不存在；`01:73` 又把材质令牌限定为「frontend=builtin.fluent 且 visualTheme=builtin.fluent-dark」。浅色值当前无承载主题，需说明「浅色 Fluent 视觉主题未注册，浅色值暂不落库」或登记缺口。

## 3. AC3 动效

**结论：部分通过。** 三类 × 三态参数表齐（02:23-50）；浮层归属符合 C-03 `:49`；`reduce` 降级不改变布局明确（02:4,65）。但判据⑤不可验证、`motion.categories` 关闭语义缺失，且表格不完整。

3.1 **判据逐条核对（对 C-03 §3 `:71`）**：

| 判据 | 02 落点 | 结论 |
|---|---|---|
| ① `reduce` 下 `decorative` 时长为 0、`feedback` 保留颜色变化但无位移 | 02:46-50（decorative 全禁用）；02:38（feedback 保留颜色、无位移） | **部分**：02:56 断言只写 decorative，未把 C-03 ① 的 feedback 半句纳入断言（参数表已覆盖） |
| ② `full` 下不跟随系统 | 02:12-16,27-28,57 | ✓ 有可验证断言（注入「系统关动画」→ full 仍 full 时长） |
| ③ `auto` 按注入的假平台设置切换 | 02:12,58 | ✓ 有断言（`IMotionPreferenceSource` true/false → 对应列） |
| ④ `navigation` 在 `reduce` 下无动画切换 | 02:27,29,30,59 | ✓ 有断言（页面切换无 transition 附加） |
| ⑤ 旧 `ReducedMotion=true` 迁移后三类全禁 | 02:14、02:60 | **不通过（P1-05）** |

3.2 **判据⑤问题（P1-05）**：C-03 `:57`/`:71` 要求旧 `true` → `reduce` **且三类全禁**（等价旧实现：`Motion.Reduced.axaml` 全部时长置 0）。但：
- `02:38` 在 `reduce` 列写「保留颜色变化、无位移（**120ms 颜色过渡允许**）」——若「三类全禁」按字面执行（categories 三类关闭/时长 0），该 120ms 过渡与「全禁」不等价（旧行为时长 0）。
- `02:60` 判据⑤断言只写「旧值 → reduce 且三类均取 `reduce` 列」——**无法验证「三类全禁」**，且未断言 `motion.categories` 三类 = false。
- `02` 全文（含 §2）未定义 `motion.categories` 三类开关**关闭**时的表现（02 只有 `motion.mode` 维度；08:50 把 categories 列为用户可配字段）。FEA-05 无法实现「categories 关闭」语义。
- 建议：补一行「`reduce` 下 `feedback` 颜色过渡 0ms（瞬时变色）」或明确「'全禁'仅指位移/装饰/动画时长，颜色状态切换保留」并同步 C-03 口径；补三个独立断言（categories 关闭、mode=reduce、迁移后 categories 全 false）。

3.3 **浮层归属**：`02:32` 明确「浮层过渡归 `navigation`，不归 `decorative`」——与 C-03 `:49`「浮层归属须在 FEA-04b 判定，不得默认 decorative」一致。✓

3.4 **reduce 不改变布局**：02:4、02:65 明确「只改时长/曲线，不改布局/层级/尺寸/位置」；02:29「0ms + 直接显示」未保留占位 ✓。通过。

3.5 **其他缺口**：
- **缺 `auto`（系统关）列**：02:25 表有三列（full / auto（系统开）/ auto（系统关）+reduce），但 02:38-42（feedback）与 02:46-50（decorative）只有三列且无「auto（系统关）」，无法机械核对 auto 系统关 = reduce 的等价性（P2-03）。
- **曲线命名歧义**：02:27-30 写「240ms `ease-out` `(.2,0,0,1)`」「`ease-in` `(.4,0,1,1)`」「`ease` `(.4,0,.2,1)`」——命名标签与 CSS 标准曲线值不一致（CSS `ease-out`=(0,0,.58,1)、`ease-in`=(.42,0,1,1)）；应删除命名标签只保留 cubic-bezier 数值（P2-03）。
- **令牌映射自相矛盾**：02:64「时长/曲线必须来自令牌或本表常量（`Nm.Motion.*` 既有键 + 本表参数）」——「或本表常量」使「不得散落魔法数」失效；代码 `Nm.Motion.Duration.*` 只有 4 档（Fast/Instant/Normal/Slow）与 1 条 `Easing.Standard`（`NmKeys.g.cs:86-91`），本表 8 个时长（240/180/200/160/120/150/90/1200ms 等）与 3 条曲线无映射表（P2-04）。
- **07:23 自动隐藏动效未归类**：阅读器顶/底条「2s 淡出」不属于 02 的 navigation/feedback/decorative 任何一条参数行（P2-04）。
- **遮罩未引用既有令牌**：02:29「遮罩淡入 160ms」未指定遮罩色令牌；R-21 已冻结 `Nm.Color.Scrim`（`Tokens.Global.axaml:9`，#8C000000；`NmKeys.g.cs` 全局派生色）。建议明确用 `Nm.Color.Scrim`（P2-04）。

## 4. AC4 a11y 与键盘

**结论：不通过。** 全局键位表有 2 处命令 Id 与 `ShellCommands.cs` 不一致；四页 Tab 序与页面正文/`KeyMap` 冲突；高对比与屏幕阅读器要求基本可执行但令牌落点不全。

4.1 **全局键位比对（03 §1 vs `ShellCommands.cs:57-116` `Definitions`）**：17 个有键位命令中 15 个一致、**2 个 Id 错误（P1-03）**：

| 03 表（03:15-16） | 代码事实 | 结论 |
|---|---|---|
| `Ctrl+P` → `quick.jump` | `ShellCommands.cs:13` `QuickJump = "go.to"`；`:65` 绑定 `Ctrl+P` | ✗ Id 错误 |
| `Ctrl+E` → `export` | `ShellCommands.cs:14` `Export = "export.run"`；`:66` 绑定 `Ctrl+E`（不可用，带原因） | ✗ Id 错误 |
| 其余：`Ctrl+1/2/3`→`space.*`（`:60-62`）、`Tab`→`studio.mode.toggle`（`:63`，Space=Studio）、`Ctrl+K`→`command.palette`（`:64`）、`Ctrl+,`→`settings.theme`（`:67`）、`F1`→`help.shortcuts`（`:68`）、`F5`/`Ctrl+Shift+F`→`attention.next`（`:69-77`）、`Esc`→`surface.back`（`:78`）、`J`/`K`→`object.*`（`:81-82`）、`[`/`]`→`page.*`（`:83-84`）、`Shift+[`/`Shift+]`→`chapter.*`（`:85-98`） | 一致 | ✓ |

  AC4 要求「与 `ShellCommands.cs` 的 `Definitions` 一一对应」——Id 不是同一字符串即失败；且 03:4 自称「唯一键位来源」，需逐字一致。

4.2 **Tab 序与页面骨架/KeyMap 冲突（P1-04）**：
- 03 §3（03:44-50）vs 页面正文：书架一致（05:65）；**工作台 03 缺 film-strip**（06:71 有「film-strip」）；**阅读器顺序相反**（03:48「顶部信息条 → 页面视图 → … → 返回按钮」 vs 07:66「返回 → 页面视图 → … → 顶部信息条」）；**设置 03 缺「返回」**（08:88 有）；03:44「左导航（**空间列表**）」与 05:21 左导航项（书架/回收站/导入）不是同一列表。
- `studio.mode.toggle` 用**无修饰 Tab** 注册且作用域 `SpaceId.Studio`（`ShellCommands.cs:63`）；`AppShellViewModel.cs:1048-1051` 只在文本输入聚焦时放行 Tab，其余路径 `:1071` 走 `_keyMap.TryMatch`——即 **Studio 空间内 Tab 被全局命令消费**，06 §3/§6 的「Tab 序」与 03:46 的工作台 Tab 序在 Studio 空间不可执行；06:72 自己也写「`Tab`（全局）切换 页面/批量」，与 06 §3 焦点序矛盾。
- 建议：明确 Studio 空间焦点遍历替代键（如 `F6` 或 `Ctrl+Tab`，需先在 `ShellCommands.cs` 注册并升 V-08b 上下文键）或声明「Studio 空间 Tab 不用于焦点遍历，焦点遍历由方向键/`F6` 承担」，并统一 03/05/06/07/08 的 Tab 序措辞。

4.3 **高对比/屏幕阅读器可执行性（基本通过，令牌缺口 P2-05）**：
- 03:61-63 对比度阈值（4.5:1 / 3:1）、高对比降级（阴影→1px 边框、材质→不透明、焦点环 3px）、颜色非唯一线索（图标/文字）——可执行、可测（WCAG 工具）。
- 03:68-72 `AutomationProperties.Name`/`HelpText`/`LiveSetting=Polite` 具体到控件类型——可执行 ✓。
- 缺口：焦点环「2px + 1px 外扩 + 高对比 3px」（03:53,62）无令牌映射（既有 `Nm.Border.Focus`=2,2,2,2，`Tokens.Global.axaml:7`；`FocusRing.cs:13,26` 是 2px accent 描边、无 offset），且 01 未登记 `Nm.Focus.Ring.*`（见 P1-01）。
- 缺口：03 未定义 V-08b 要求的上下文路由三元 `(frontendId, windowRole, focusScope)` 的具体取值（当前 `KeyMap.TryMatch` 只有 `(space, mode)`，`KeyMap.cs:132-150`；V-08b 见 C-02 `:102-103`），Fluent 侧无法实现三元路由。
- AC4 未覆盖的既有行为（不退化风险）：`AppShellViewModel.cs:1053-1069` 中阅读器 `J`/`K`/`Space` 也翻页、`←`/`→`/`PgUp`/`PgDn` 翻页；03 §2（03:36）只写「←/→/PgUp/PgDn 翻页；↑/↓ 滚动」，未列 `J`/`K`/`Space`——若 FEA-06 按设计实现可能丢失既有键行为（P2-08）。

## 5. 上游一致性

**结论：部分通过。**

5.1 **未新增枚举值**：设计只引用 `SpaceId.Library`（05:3）、`SpaceId.Studio` + `StudioMode.Page/Batch`（06:3）、`ShellSurface.ReaderOverlay`（07:3）；`ShellState.cs:8-28` 三枚举值未变。✓ 但 **08 设置页页 ID 表述含糊（P1-07）**：`08:3`「`SpaceId` 外露为『设置』页面；`ShellSurface` 内为独立 surface（不新增 `SpaceId`，入口来自顶部/左导航）」——未指明宿主枚举；V11R `:251` 的 `ShellSurface` 只有 `Spaces/ThemeStudio/ReaderOverlay`，`:269` 明确 `ThemeStudio` 是独立覆盖式表面、入口 TopBand「主题」按钮 + `Ctrl+,`；03:17 又把 `Ctrl+,` 映射 `settings.theme`「主题工作室」。设置页与 `ThemeStudio` 的对应关系需在 08 写死（例如「设置页 = `ShellSurface.ThemeStudio` 的扩展或新 surface 需 DSH 裁决」）。

5.2 **未改冻结契约字节**：`git diff --name-status fdf7591ac..fe9535e14` 未触及 `doc/plan/**`、`doc/contracts/**`、任何代码；交付全部在 `doc/design/fluent-v1/**` + `verification/FEA-04b/**` + 任务卡/台账/计划。✓

5.3 **与 FEA-04 Current 不退化**：09:25-33 的对照表声明 5 项不退化（空态导入、未保存确认、批量 gate、阅读器 page ID、设置保存失败）——方向正确，但：`09:31` 的「批量 gate」引用 06 §4 不成立（见 §1.2）；且设计新数值（TopBand 48、左导航 72/240、film-strip 96/120、行高 40/36/48、四档断点）与 Current 的令牌/三档断点不同（见 §2.3），FEA-04 `ShellLayout.cs:7-12` 明确「every number resolved from Nm.* token；only three frozen breakpoints as constants」——Fluent 若照本设计实现，需要新的令牌/断点值，**未登记为缺口**（P1-02）。

5.4 **引用错误（P2-09）**：
- `README:5` 与 `verification/FEA-04b/design-baseline-selfcheck.md:26` 把 C-05（**页可见性/完整性谓词**，`FEA-C05_PAGE_VISIBILITY_DRAFT.md:24-47` 是 `pages` 数据谓词）当作「四页不新增页/阅读器 overlay」的结构依据——C-05 不约束 UI 四页结构（约束来自 C-02 `:96-97` V-08a 与产品四页需求）。`05:73` 又把「`reading_progress` 不新增字段」归到 C-05（C-05 不定义 reading_progress）。
- `06:59`「批量操作必须经 Run intent key（**C-03**/R-22）」——Run 幂等/intent key 属 **C-08**（`FEA-C08_RUN_SNAPSHOT_DRAFT.md:112-141`）与 R-22（V11R_PROGRAM:186）；C-03 是外观持久化。Id 引用错误。
- `07:74`「语义锚点（FEA-01 冻结字段）」——FEA-01 是契约清单；语义锚点相关定义在 FEA-04 S4/`ReaderOverlayViewModel` 迁出（`07:4` 自引方案 §15.3），「FEA-01 冻结字段」无对应证据。
- `08:39`「`InfoBar` 风格（`Skeleton`/`Status.cs` 组件）」——`Skeleton.cs`/`Status.cs` 是文件/组件，不是 InfoBar 实现；`InfoBar` 不是既有组件（`DesignSystem/Controls` 下无 InfoBar）。
- `04:38`「折叠后由顶部命令条按钮恢复，快捷键不新增（**通过命令面板**）」——命令面板由 `ShellCommands.Definitions` 生成（`ShellCommands.cs:100-115` 只有 library/studio 动作，无折叠/展开命令），该快捷键不存在。
- `01:17`「`Nm.Corner.Fluent.*` 等实际生成属于 **FEA-05** 的实现范围（tokens 生成器）」——方案 `:644` 的 FEA-05 是「三层注册与资源隔离（Appearance、scheme/theme/scale registry、设置迁移、preview sink）」，不含 tokens 生成器；令牌生成属 DS/design-platform 范围（`TokenGenerator.cs`/`TokenDictionaryWriter.cs` 已在 DesignSystem）。职责错配（P2-12）。

## 6. 可执行性（FEA-05/06 能否直接按规格实现）

**结论：不能直接实现，需修订后重走复核。** 阻断点：
1. 令牌名不存在（P1-01）——直接照做会引用不存在的资源键；FEA-05 首先就无法在「C-02 已冻结名义」下找到 `Nm.Surface.*`/`Nm.Accent.Subtle`/`Nm.Status.*`。
2. 尺寸/断点新值无令牌/无裁决（P1-02）——违反 README:37 与 04:23 的令牌唯一来源；且与 Current 冻结三档断点冲突。
3. 焦点顺序两套且 Studio Tab 被占用（P1-04）——FEA-06 无法确定实现哪套；实现前需 DSH 裁决替代键。
4. 判据⑤断言不足 + categories 语义缺失（P1-05）——FEA-05 无法按 C-03 判据写单测。
5. 09 矩阵与正文不一致（P1-06）——「唯一状态清单」不可机械核对。
6. 08 字段清单与 C-03 §2.2 不一致（P1-07）——字段名/完整性判据（C-03 `:70`）无法通过。

**缺口登记（G-1…G-4）不充分（P2-13）**：
- G-1 漏 Focus 组、Size/Breakpoint 组、设置页宿主 surface、材质实现机制（Acrylic/Mica 在 Avalonia 11 的实现路径）、令牌生成职责归属。
- G-3「设计资产未产出」已登记 ✓（`NmIcon.cs` 存在，沿用合理）；但 10 §5 要求「复用既有组件」，未列 `Badges.cs`（StatusBadge/Chip/Kbd）与 `FocusRing.cs`（Theming）等既有实现（P2-10）。
- 方案 `:645` FEA-06 AC 含「四页和四页预览」——本基线未定义「四页预览」交互/视觉规格，G 清单未登记（P2-13）。
- `01:17` 的 FEA-05 职责错配（见 §5.4）。

**自相矛盾清单**（核查项 6 要求）：
- 令牌名：01:66「`Nm.Text.*`/`Nm.Text.Color.*`（既有）」 vs `NmKeys.g.cs` 实际族名（P1-01）。
- 尺寸：04:23「不得散落裸数」 vs 04/05/06/08 的裸尺寸（P1-02）。
- 状态名：09:13 vs 09:16（书架重复）；09 无正文的 4 个格（P1-06）。
- 层级：04:63 层 5 Tooltip `Elevation.3` vs 01:48 `Elevation.2`「弹出菜单、Tooltip、抽屉」（P2-06）；10:51 `CommandPalette` `Elevation.3` vs 04:61 层 3「浮层（抽屉/命令面板）」`Elevation.2`。
- 骨架：04:21「四页共用」 vs 07/08 无左导航（§1.3）。
- 字段名：08:47「`Appearance`」/08:48「`Contrast`」 vs C-03 `:36-38`「`appearance.mode`/`appearance.contrast`」；03:62 同用旧名 `Appearance.Contrast`（P1-07/P2-05）。
- 视觉语义：07:34 把 `Nm.Material.Acrylic.Opacity`（double，01:38）当「半透明背景」——类型误用（P2-08）。

## 7. 治理

| 检查 | 命令/方法 | 结果 |
|---|---|---|
| 治理检查器 | `pwsh -NoProfile -File tools/governance/check.ps1` | PASS（2 warnings：非终态 Task 计数；STATUS 预算 80%） |
| 契约 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | PASS（15/15） |
| 证据表哈希 | `Get-FileHash -Algorithm SHA256` 逐项复算 | **12/12 一致**（README `2d7650aa…`、01 `d413f75d…`、02 `9d960d7f…`、03 `5073ce75…`、04 `ce3d7e53…`、05 `00cb4928…`、06 `ee7b594f…`、07 `3d3b4e0e…`、08 `502b3590…`、09 `911e4e8d…`、10 `1ef327a1…`、selfcheck `b3473cb5…`，均与 `doc/tasks/FEA-04b.md:88-99` 一致） |
| 证据路径 | 12 项逐一 `Test-Path` | 全部存在 |
| 状态指针一致性 | 任务卡 `status: in_review`（FEA-04b.md:6）；`doc/TASK_LEDGER.md:43` `in_review`；**`doc/STATUS.md:7` 仍写 `ready`；`doc/REBASELINE_PLAN.md:17` 仍写 `ready`** | **不一致（P2-14）** |

补充：`FEA-04b.md` 的 `delivery_head: null`、`integration_commit: null`、`canonical_evidence_status: pending` 与 `in_review` 阶段相符（收口时填），非缺陷；证据表 commit 字段统一写 `568cf271e` 与「文件内容自该 commit 未变」一致（`fe9535e14` 仅改 FEA-04b.md 证据表本身）。⚠ 本报告只审设计基线（AC1–AC4）；STATUS/PLAN 的 `ready` 残留属治理指针问题，不阻断设计内容，但收口前应修正。

## 8. Findings

| 编号 | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| P1-01 | P1 | `01-design-tokens.md:66,41,13-15`；`04:58`；`05:29,32`；`06:30,33,34,35,36`；`07:30,33`；`08:25,32,34,37`；`10:10-13,43`；`03:53` | 令牌名自造/错误：`Nm.Surface.*`（应为 `Nm.Color.Bg.*`）、`Nm.Accent.Subtle`（`Nm.Color.Accent.Muted`）、`Nm.Status.*`（`Nm.Color.Status.*`）、`Nm.Text.*`/`Nm.Text.Color.*`（`Nm.FontSize.*`/`Nm.LineHeight.*`/`Nm.Color.Text.*`）；01:66 把错误族名标「既有」；`Nm.Focus.Ring.*`（C-02:52 第四组）未在 01 登记而 03 引用。 | 全部改为 C-02/V11R 冻结名；01 §1 补第四组（`Nm.Focus.Ring.Width/Offset/Color`）及取值；对表逐项复名。 |
| P1-02 | P1 | `04:12,15,17,21,23,29-32,34,40,51`；`05:31,61`；`06:22,66,67`；`08:14,83`；`10:26` | 尺寸/断点新值未走令牌且与既有令牌冲突：TopBand 48 vs 36、左导航 72/240 vs TreeWidth 200、film-strip 96/120 vs 56/200、行高 40/36/48 vs 26/24、四档断点 720/1024/1440/1920 vs 冻结三档 1024/1280/1600；G-1 未登记需新增 Size/Breakpoint 令牌或 DSH 裁决；04:23 与裸值自相矛盾。 | 二选一：①改用既有令牌（数值回调至 36/200/56/200/26/24/1024/1280/1600）或在 G-1 登记新增令牌组并请 DSH 裁决；②把布局常量集中到 `LayoutProfile`/新常量表并登记豁免；补「Fluent 与 Current 断点差异」裁决项。 |
| P1-03 | P1 | `03-accessibility.md:15,16` vs `ShellCommands.cs:13,65`（`go.to`）、`:14,66`（`export.run`） | 全局键位表 2 个命令 Id 与 `Definitions` 不一致（`quick.jump`→`go.to`、`export`→`export.run`），不满足 AC4「一一对应」。 | 逐字改为 `go.to`/`export.run`；建议 03 §1 直接从 `ShellCommands.Definitions` 生成或加「本表由 Definitions 复制的校验脚本」。 |
| P1-04 | P1 | `03:44-50` vs `05:65`、`06:71,72`、`07:66`、`08:88`；`ShellCommands.cs:63`；`AppShellViewModel.cs:1048-1051,1071` | 四页 Tab 序与正文不一致（03 缺 film-strip、阅读器顺序相反、设置缺返回、书架左导航描述不同）；Studio 空间无修饰 Tab 被 `studio.mode.toggle` 全局占用，06 §3/§6 的 Tab 焦点序在该空间不可执行，06:72 自身矛盾。 | 统一四页 Tab 序（以页面正文为准回写 03）；为 Studio 空间定焦点遍历替代键（需先在 `ShellCommands.cs` 注册 + 升 V-08b 上下文键）或将全局 Tab 改为 `Ctrl+Tab`（需 DSH 裁决，C-02 V-08b 冻结项）。 |
| P1-05 | P1 | `02-motion.md:14,38,60`；C-03 `:57,71` | 判据⑤不可验证：`reduce` 下 feedback 保留 120ms 颜色过渡，与旧 `ReducedMotion=true`「三类全禁（时长 0）」不等价；02:60 断言只写「取 reduce 列」，未断言 categories 三类全 false；02 全文未定义 `motion.categories` 关闭语义（08:50 已把 categories 作为用户字段）。 | 明确「全禁」口径（建议 categories 全 false + feedback 位移 0 + 颜色瞬时切换 0ms）；补三条独立断言；定义 categories 关闭后的表现。 |
| P1-06 | P1 | `09-state-matrix.md:9,13,16,20,31`；对比 `06:40-51,55-59`、`07:37-46,54`、`08:59-68,75` | 矩阵与正文不一致：工作台「批量筛选无结果」、工作台「运行中（暂停/停止/重试）」、阅读器「进度写回中」、设置「搜索无匹配」均无正文定义；书架「扫描中」在 09:13 与 09:16 重复；09:20 左导航通则不适用于 07/08；09:31 gate 引用 06 §4 不成立。 | 逐格二选一：补正文状态规格，或删矩阵格；补「运行中 vs 部分」定义边界；修正 09:20/09:31；09 增加「矩阵格 ↔ 正文行号」列便于机械核对。 |
| P1-07 | P1 | `08-page-settings.md:3,47,48,51`；C-03 `:36-44,70`；`03:62` | 设置字段清单与 C-03 §2.2 不一致：`Appearance`→`appearance.mode`、`Contrast`→`appearance.contrast`；缺 `layout.*`、`appearance.followSystemAccent`、`schemaVersion`、`material.acrylicStrength`、`material.micaEnabled`、`corners.scale`；08:3 设置页宿主 surface 未引用 `ShellSurface.ThemeStudio`（V11R `:251,269`）。 | 按 C-03 §2.2 行逐项重写字段表（含字段全名/取值/存储位置）；08:3 写死「设置入口 = `settings.theme` → `ShellSurface.ThemeStudio`」或登记新 surface 裁决项。 |
| P2-01 | P2 | `01:55-66` | 判据①对表覆盖不完整（10 行；漏详情栏/缩略图条/主画布容器/Region 框/批量单元格/进度条/页码徽标/输入框/危险按钮/遮罩/焦点环），且 01:68 裸值禁令未覆盖尺寸/描边/字号/层级。 | 补齐四页主要视觉数值行；禁令扩为「任何视觉数值」；标注「族名/精确键名」。 |
| P2-02 | P2 | `01:36-39,41,72-73`；C-02 `:89-90`；`08:47` | 材质给深/浅两套值，但 C-02 V-07 只注册 `builtin.fluent-dark`；01:41 用错名 `Nm.Surface.*` 表述降级；01:73 把材质限定为 visualTheme=fluent-dark，与浅色值无落点。 | 声明「浅色 Fluent 视觉主题未注册，浅色值暂不落库」或登记新增视觉主题；降级目标改为 `Nm.Color.Bg.*`（五级表面梯）。 |
| P2-03 | P2 | `02:25-30,38-42,46-50` | `auto`（系统关）列在 feedback/decorative 表缺失，无法机械核对 auto=reduce 等价；曲线命名标签与 cubic-bezier 数值不符（`ease-out`=(0,0,.58,1) 等）。 | 两表补「auto（系统关）」列；删除 `ease/ease-out/ease-in` 标签，仅保留 cubic-bezier 数值。 |
| P2-04 | P2 | `02:29,49,64`；`07:23` | 令牌映射自相矛盾（「必须来自令牌或本表常量」）；`Nm.Motion.*` 4 档时长/1 条曲线与本表 8 个时长/3 条曲线无映射；07 顶/底条 2s 自动隐藏未归入三类；遮罩未引用 `Nm.Color.Scrim`（R-21）。 | 补「本表参数 → `Nm.Motion.*` 令牌/本地常量」映射表；为自动隐藏归类并给参数；遮罩显式引用 `Nm.Color.Scrim`。 |
| P2-05 | P2 | `03:53,62`；`01:10-15`；`KeyMap.cs:132-150`；C-02 `:102-103` | 焦点环 2px/1px/高对比 3px 无令牌落点（既有 `Nm.Border.Focus`=2,2,2,2、`FocusRing.cs` 2px 无 offset）；03 未定义 V-08b 三元路由 `(frontendId, windowRole, focusScope)` 的取值（代码当前只有 space/mode）；03:62 用旧字段名 `Appearance.Contrast`。 | 在 01 补 Focus 组取值映射；03 增「Fluent 上下文键取值表」（如 `windowRole=Main/Overlay`、`focusScope=Shelf/Canvas/Inspector/...`）；改 `appearance.contrast`。 |
| P2-06 | P2 | `04:58-63`；`01:48-49`；`10:51` | 层级矛盾：04:63 层 5 Tooltip/通知条 `Elevation.3` vs 01:48 Tooltip 在 `Elevation.2`；10:51 CommandPalette `Elevation.3` vs 04:61 层 3「浮层（命令面板）」`Elevation.2`；四页未引用 `Nm.ZIndex.*` 既有令牌族。 | 统一 Tooltip/命令面板的 Elevation 归属；层级表增加 `Nm.ZIndex.*` 列并映射 0–5 层。 |
| P2-07 | P2 | `04:21,38,40,51` vs `07:11-22`、`08:3,10-22`；`09:20` | 04:21「四页共用骨架」与 07（浮层）/08（独立 surface，无左导航）矛盾；04:38 折叠入口「通过命令面板」无对应命令（`ShellCommands.cs:100-115`）；折叠/最小窗口宽度未令牌化。 | 04 拆「05/06 共用骨架」与「07/08 覆盖式表面」；删除命令面板折叠说法或补注册命令（需 DSH 单点提交 ShellCommands）。 |
| P2-08 | P2 | `06:22,59`；`07:34`；`05:21,46,73`；`AppShellViewModel.cs:1053-1069`；`StudioFilmStrip.cs:15` | 细节不一致：06 film-strip 96/120 vs 既有 56/200；06:59 引用 C-03（应为 C-08/R-22）；07:34 把 double 的 `Nm.Material.Acrylic.Opacity` 当背景刷；05:21 左导航项与 03:44「空间列表」不同；05:46「旧壳」未引用 ADR-0001:42；03 §2 未列阅读器既有 `J/K/Space` 翻页键（不退化风险）。 | 逐项修正引用/数值；03 §2 补既有阅读器键并声明保留。 |
| P2-09 | P2 | `README:5`；`selfcheck:26`；`05:73`；`07:74`；`08:39`；`01:17`；方案 `:644,645` | 上游引用错误/职责错配：C-05（页可见性谓词）被当作四页结构依据（README/selfcheck/05:73）；07:74「FEA-01 冻结字段」锚点无出处；08:39 `Skeleton`/`Status.cs` 当 InfoBar；01:17 把令牌生成归 FEA-05（方案 :644 不含）。 | 删除/改正 C-05 引用（四页结构依据改为 C-02 V-08a + 产品需求）；锚点引用 FEA-04 S4；InfoBar 改为既有 `Status.cs` 语义或新组件登记；令牌生成归 DS/design-platform。 |
| P2-10 | P2 | `10:4,19,51`；`Badges.cs`；`Theming/FocusRing.cs` | 10 组件清单与既有组件/正文不一致：未列 `StatusBadge`/`Chip`/`Kbd`（`Badges.cs` 已存在）与 `FocusRing`；`Skeleton.cs` 当令牌；新组件（TopBand/NavRail/SurfaceCard 等）未按 C-02 V-06 说明落位（本地 Controls vs DS）；CommandPalette Elevation 与 04 矛盾（见 P2-06）。 | 清单加「既有/新增/归属」列；补 Badges/FocusRing；按 V-06 规则说明新组件落位。 |
| P2-11 | P2 | `10:39`；`08:63,75`；`09:9` | 08 搜索无匹配状态正文未定义（09:9 有）；08 部分态举例漏 Provider（09:13 只举 Fluent 材质）；10:39 引 `Skeleton`/`Status.cs` 文件名。 | 补 08 搜索空态与 Provider 不可用表现；10 改为组件名。 |
| P2-12 | P2 | `07:23`；`03:53,62`；`06:32`；`08:34` | 视觉数值禁令缺口：1.5px 描边/1px 外扩/1px 边框/2s 自动隐藏等裸值未纳入 01 禁令与令牌映射。 | 见 P2-01 建议；增加「描边宽度/动效时长」令牌或登记常量。 |
| P2-13 | P2 | `01:17`；`selfcheck:30-36`；方案 `:645` | 缺口登记不足：G-1 漏 Focus/Size/Breakpoint/设置页宿主/材质实现机制/令牌生成职责；FEA-06 AC「四页预览」无规格。 | 扩 G-1/G-5；补「四页预览」范围或登记为后续任务。 |
| P2-14 | P2 | `doc/STATUS.md:7`；`doc/REBASELINE_PLAN.md:17`；`FEA-04b.md:6`；`TASK_LEDGER.md:43` | 任务状态指针不一致：任务卡/LEDGER 为 `in_review`，STATUS/PLAN 仍为 `ready`。 | 重跑 `check.ps1` 前更新 STATUS/PLAN（或在收口时统一）；确认 `ready` 是否为 DAG 节点语义并加注。 |

## 9. 边界声明

- 本报告只审 **设计基线（AC1–AC4）**；**AC5（用户确认）不在本报告范围**，`FEA-04b.md:65` 的 AC5 仍为 `[ ]`/PARTIAL，用户确认与 DSH 冻结由 Lead 处理。
- 只读：未修改任何被审文件；被审 head `fe9535e14` 工作区 clean；未 commit/push。
- 未验证项：高对比模式的实际渲染与对比度（需实现后截图/工具验证）；`Nm.Material.*`/`Nm.Elevation.*`/`Nm.Corner.Fluent.*` 生成后的实际资源加载（代码尚不存在）；FEA-05/06 的实现可行性为设计层推断，非实测。
- 复核建议：上述 P1 全部处置（或 DSH 明确裁决为「设计意图，另行建卡」）后，重跑 `check.ps1`/`verify_pins.ps1` 与证据表哈希，再提交 r2 复核。
