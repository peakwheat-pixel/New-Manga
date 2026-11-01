# FEA-04b 范围复核 r2（同一独立席位，续任）

| 字段 | 值 |
|---|---|
| base_commit | `fe9535e14` |
| reviewed_head | `e173d156d`（main，clean；r1 处置提交） |
| 上一轮 | `doc/reviews/FEA-04b-scope-r1.md`（reviewed_head `fe9535e14`） |
| reviewer | `fea04b-scope-reviewer` |
| reviewer 来源 | DSH Team Lead 派发，fresh 独立上下文；**r1 同一席位续任**；未参与 FEA-04b 起草；只读被审 head |
| 日期 | 2026-11-02 |
| 审查范围 | AC1–AC4（设计基线）。**AC5（用户确认）不在本报告范围** |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 4 / P2 = 17** |

> 说明：r1 的 P1×7 中 **2 条完全关闭、5 条部分关闭**（P1-01/P1-02/P1-04/P1-05/P1-06/P1-07 见 §1）；部分关闭项与 1 条新引入的 P1（`Ctrl+Tab`）仍阻断 `approved`。**未达到 P0/P1=0，故判 changes_requested。**

## 0. 方法、只读声明与复现

- 只读核查被审 head；**未修改任何被审文件**，未 commit、未 push；本报告是本轮唯一新增文件。
- 复现（本次实跑）：
  - `git rev-parse HEAD` → `e173d156db11c92d0e0a33a8dcab750d7b3d4957`；`git status --porcelain` → 空。
  - `git diff --name-status fe9535e14..e173d156d` → 仅 `doc/design/fluent-v1/` 10 文件 + `doc/reviews/FEA-04b-scope-r1.md`（已在提交中）+ `doc/tasks/FEA-04b.md` + `verification/FEA-04b/design-baseline-selfcheck.md`；**未触碰 `doc/plan/**` 冻结契约、`apps/**`、`src/**`**；`SpaceId/StudioMode/ShellSurface` 枚举未新增。
  - `pwsh -NoProfile -File tools/governance/check.ps1` → `PASS (2 warnings)`。
  - `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → `PASS (all 15)`。
  - 证据表 12 项哈希复算：**11/12 一致**；`verification/FEA-04b/design-baseline-selfcheck.md` **不一致**（证据表写 `b3473cb5…`，实际 `752c2de7…`）。

## 1. r1 逐项 disposition（P1×7 + P2-14）

| r1 finding | r2 结论 | 证据 |
|---|---|---|
| **P1-01 令牌名自造/错误** | **部分关闭**：全库已替换为冻结名（`Nm.Color.Bg.*`/`Nm.Color.Accent.*`/`Nm.Color.Status.*`/`Nm.Color.Text.*`/`Nm.FontSize.*`/`Nm.Icon.Size`），设计目录 grep 无 `Nm.Surface.*`/`Nm.Accent.*`/`Nm.Status.*`/`Nm.Text.*` 残留；但新增的「焦点环（第四组）」说明与 C-02 V-03 冻结文本冲突且类型写错 → **R2-P1-01** | `01:16,18`；`03:53`；C-02 `:52,56-57`；`Tokens.Global.axaml:7` |
| **P1-02 尺寸/断点** | **部分关闭**：01 新增 G-1b 且 12 项令牌值与 `Tokens.Global.axaml:58-84` **全部一致**（36/200/56/200/40/320/24/26/28/24/28 + 1024/1280/1600）；04 重写为三档断点；但 **05–08 未同步**（仍用旧四档 `Compact/Medium/Expanded/Wide`，仍写 240/96/120 裸值）→ **R2-P1-02** | `01:22`；`04:12-25,29-38`；`05:15,59,61`；`06:15,22,24,65-67`；`07:60,62`；`08:14,85-87` |
| **P1-03 命令 Id** | **已关闭**：`03:15`=`go.to`、`03:16`=`export.run`；03 §1 全表 17 个有键位命令与 `ShellCommands.cs:57-116` 逐条一致 | `03:12-23`；`ShellCommands.cs:13,14,60-98` |
| **P1-04 焦点顺序/Tab 冲突** | **部分关闭**：03 §3 四页 Tab 序已对齐 05–08 正文（`03:46`=「顶部页签条→左导航→film-strip→…」，`03:48` 阅读器以「返回」起、顶部信息条最后，`03:50` 设置补「返回」）；03:34/06:72 明确页签条内用 `←`/`→`、不使用无修饰 Tab；**但 06:49 新引入 `Ctrl+Tab`** → **R2-P1-03** | `03:34,44-50`；`05:65`；`06:49,71-72`；`07:66`；`08:91` |
| **P1-05 判据⑤** | **部分关闭**：02:60 已补断言「旧值→`reduce`+categories 三类关」；02:17 新增 categories 关闭语义；**但「三类全禁」仍不等价 C-03 `:57` 的旧行为（时长 0）**——`02:38` reduce 列 feedback 仍保留 120ms 颜色过渡 → **R2-P1-04** | `02:14,17,38,60`；C-03 `:57,71` |
| **P1-06 09 矩阵** | **部分关闭**：09:9/14/16 已补 4 格说明（阅读器无筛选/无冲突、设置无冲突/无运行态；书架「扫描中」与「运行中」去重）；09:31 gate 引用改为 06 §3/§4；**但 06/07/08 正文仍缺 3 处**（工作台「运行中」控制、阅读器「进度写回中」、设置「搜索无匹配」）→ **R2-P2-01** | `09:9,14,16,31`；`06:40-51`；`07:37-54`；`08:59-78` |
| **P1-07 08 设置字段** | **部分关闭**：字段从 6 项扩到 14 项，覆盖 `appearance`/`contrast`/`corners`/`material`/`motion.mode`/`motion.categories`/`layout.*`/`followSystemAccent`/`schemaVersion`；宿主改为 `ShellSurface.ThemeStudio`；**但 3 处字段全名缺前缀**（`appearance`→`appearance.mode`、`contrast`→`appearance.contrast`、`followSystemAccent`→`appearance.followSystemAccent`）→ **R2-P2-02** | `08:3,47-54`；C-03 `:36-44` |
| **P2-14 治理指针** | **未处置（事实未变）**：`doc/STATUS.md:7` 仍 `ready`、`doc/REBASELINE_PLAN.md:17` 仍 `ready`；本 diff **未包含** STATUS/PLAN（`git diff --name-only` 无匹配）；仅 `TASK_LEDGER.md:43` 为 `in_review` | `doc/STATUS.md:7`；`doc/REBASELINE_PLAN.md:17`；`doc/TASK_LEDGER.md:43` |

## 2. 仍存在的 P1（4 条，含最小修法）

### R2-P1-01（r1 P1-01 部分关闭）焦点环「第四组」与 C-02 V-03 冲突 + 类型错误

- `01:16` 新增表行「焦点环（第四组） | `Nm.Border.Focus` + `Nm.Color.Accent.Ring` | **`IBrush`** | 全部 | 已存在」：`Nm.Border.Focus` 实际类型是 **`Thickness`**（`Tokens.Global.axaml:7` = `2,2,2,2`），不是 `IBrush`；`Nm.Color.Accent.Ring` 才是刷。
- `01:18`「C-02:52 的第四组在**现有令牌**中由 `Nm.Border.Focus`（环色）与 `Nm.Color.Accent.Ring`（强调环）承载，**不存在** `Nm.Focus.Ring.Width/Offset` 族」：C-02 V-03 `:52` 明确**新增**焦点组 `Nm.Focus.Ring.Width/Offset/Color`；`:56` 称四组为「Fluent 专属最小集」；`:57` 判据「**Fluent 主题包缺任一键 → 判违规**」。设计把该组说成「由现有键承载、不存在此族」，等于指示 FEA-05 不生成该组 → 触发 C-02 冻结判据违规；且 `Nm.Border.Focus` 是厚度不是环色。
- `03:53`「2px `Nm.Border.Focus` 颜色 + 1px 外扩」沿用同一错误（把 `Thickness` 当颜色）。
- **最小修法**：`01:16-18` 改为「C-02 V-03 第四组 `Nm.Focus.Ring.Width/Offset/Color` 由 FEA-05 在 Fluent 主题包生成（缺一判违规）；本基线取值为 Width=2、Offset=1、Color=`Nm.Color.Accent.Ring`（高对比 3px 见 03 §4）；现有 `Nm.Border.Focus` 是控件边框厚度令牌（Thickness 2,2,2,2），不作为环色引用」；`03:53` 改为「2px `Nm.Focus.Ring.Color`（=`Nm.Color.Accent.Ring`）描边 + 1px `Nm.Focus.Ring.Offset`」。

### R2-P1-02（r1 P1-02 部分关闭）尺寸/断点只在 04/01 落地，05–08 未同步（跨文档矛盾）

- 04 已改为三档：`Narrow` <1024 / `Medium` 1024–1279 / `Compact` 1280–1599 / `Full` ≥1600（`04:30-33`），令牌列 `Breakpoint.Narrow/Compact/Full` 与 `Tokens.Global.axaml:58-60` 一致；`04:22` 左导航改 `TreeWidth` 200、`04:23` 状态条用 `StatusBand*`、`04:25` 禁止裸数。
- 但 05–08 的 §响应式表与布局图**未同步**，仍用旧四档名与旧裸值，与 04 直接矛盾：
  - `05:59`「Compact | 单列；详情栏变抽屉」vs `04:33` Compact=1280–1599 三栏；`05:15`「72/240」、`05:61`「左导航 240」vs `TreeWidth` 200。
  - `06:24`「检查器在 **Compact** 断点变为抽屉」vs 04（Narrow 才抽屉）；`06:65`「Compact 检查器抽屉」同上；`06:15` 图「左导航 240」；`06:22/66/67` film-strip「96 / 96 / 96/120」vs `01:22` G-1b 的 `FilmStripCollapsed` 56 / `Expanded` 200（`Tokens.Global.axaml:64-65`）。
  - `07:60,62`、`08:85-87` 仍 `Compact/Medium/Expanded/Wide` 旧命名。
  - `08:14/86`「分组列表 240」、`05:61`「最小卡宽 160」、`06:67`/`04:34`「画布最大宽 1600」、`08:87`「内容最大宽 960」——均无令牌落点，与 `01:22`「不得在本基线写裸数」及 `04:25` 自相矛盾。
- **最小修法**：05/06/07/08 §响应式统一改写为 04 的 `Narrow/Medium/Compact/Full` 四区间（含行为）；240→`Nm.Size.TreeWidth`（或折叠隐藏）、96/120→`Nm.Size.FilmStripCollapsed/Expanded`、320/360→`InspectorExpanded`/`Drawer`；160/1600/960 等布局常量在 01 G-1b 登记或改用令牌；`04:71` 检查点同步。

### R2-P1-03（新引入）`06:49` 新增未注册键位 `Ctrl+Tab`

- `06:49`：「…确认前不切页（fail-closed）；**`Ctrl+Tab` 也可触发模式切换（与全局 `Tab` 一致）**」。
- 事实：`ShellCommands.cs:57-116` **没有** `Ctrl+Tab` 命令（`studio.mode.toggle` 只绑无修饰 `Tab`，`:63`）；`03-accessibility.md:13` 只列 `Tab`；`KeyMap` 唯一注册表无该手势。这与「快捷键以 C-02 V-08b `KeyMap` 为唯一来源」「不得新增全局键」直接冲突（AC4），且与同页 `06:72`「页签条内用 `←`/`→`、不使用无修饰 Tab」自相矛盾。
- **最小修法**：删除 `06:49` 中 `Ctrl+Tab` 子句；若确需该键，必须先在 `ShellCommands.cs` 注册（DSH 单点提交 + Task 登记）并同步 03 §1，否则不得写入设计基线。

### R2-P1-04（r1 P1-05 部分关闭）「三类全禁」仍不等价 C-03 旧行为（时长 0）

- `02:60` 新断言：「旧值 → `motion.mode=reduce` 且 `motion.categories` 三类均为『关』；…『关』时该类在 `full` 下也按 `reduce` 列执行（即三类全禁）」；`02:17` 定义「关 = 该类在 `full` 下也按 `reduce` 列执行」。
- 但 `02:38` 的 `reduce` 列 feedback 仍为「**保留颜色变化、无位移（120ms 颜色过渡允许）**」。C-03 `:57` 对旧 `ReducedMotion=true` 的等价性明文是「**`Motion.Reduced.axaml` 把所有时长置 0**」；按当前定义「三类全禁 = 三类关 + 按 reduce 列」仍保留 120ms 颜色过渡，**不等价旧行为**，判据⑤的「等价旧行为」不可验证。
- **最小修法**：`02:38` reduce 列 feedback 改为「颜色瞬时切换（0ms，无过渡）」；或在 `02:17`/§3⑤ 明确「『全禁』只指位移/装饰/过渡时长，颜色状态切换不算动效」并请 DSH 对 C-03 `:57` 口径做裁决（C-03 已冻结，不得私改）。

## 3. 新引入问题（P2；对应 §6 编号 R2-P2-03/04/05）

| 编号 | 位置 | 问题 | 建议 |
|---|---|---|---|
| R2-P2-03 | `verification/FEA-04b/design-baseline-selfcheck.md:52,53,55` | §5 r1 处置表含**控制字符**：`0x1B`（`go.to/` 后，破坏 `export.run`）、`0x0C`（`ull` 前，破坏 `full`）、`0x07`（`ppearance` 前，破坏 `appearance`）、`0x0C`（`ollowSystemAccent` 前）。文件已损坏（`Get-Content` 显示为乱码/截断），且 E-FLUENT-SELFCHECK 哈希因此失效。 | 用纯文本重写 §5（避免 `\e`/`\f`/`\a`/`\r` 转义），保存后重算哈希。 |
| R2-P2-04 | `doc/tasks/FEA-04b.md:88-99` | 证据表 12 项 **commit 列仍为 `568cf271e`**（r1 交付提交），但 sha256 列已更新为 `e173d156d` 后的内容（11 项复算一致）；`E-FLUENT-SELFCHECK` 的 sha256 仍为旧值 `b3473cb5…`（实际 `752c2de7…`）。commit 与 sha256 不再配对，且 selfcheck 哈希过期。 | 12 项 commit 统一改 `e173d156d`；重算 selfcheck 哈希；`delivery_head` 填 `e173d156d`（收口时）。 |
| R2-P2-05 | `02-motion.md:17` | 「…强制减弱。`\n`**分类开关语义**：…」——含**字面反斜杠+n**（两字符），Markdown 渲染会显示 `\n`；该段本应是新段落。 | 把字面 `\n` 改为真实换行（拆两段）。 |

## 4. 逐项核查（对应派发 8 点）

### 4.1 P1-01 令牌名全库复核

- 设计目录（`doc/design/fluent-v1/*.md`）全量正则扫描 `Nm.Surface.*`/`Nm.Accent.*`/`Nm.Status.*`/`Nm.Text.*`/`Nm.Icon.*`/`Nm.Focus.Ring`：**无自造名残留**（`Nm.Icon.Size` 是真实键；`Nm.Focus.Ring` 仅出现在 01:18 的「不存在」说明中）。✓ 替换完成。
- 冻结名核对：`Nm.Color.Bg.Raised/Sunken`、`Nm.Color.Accent.Muted`、`Nm.Color.Status.Failed`、`Nm.Color.Text.*`、`Nm.FontSize.*` 均存在于 `NmKeys.g.cs`/`Tokens.Global.axaml`。✓
- 残留问题：焦点环组（R2-P1-01）与 01:16 类型错误。

### 4.2 P1-02 尺寸/断点

- 01 G-1b 12 项值与 `Tokens.Global.axaml` **逐项一致**（TopBand 36 / TreeWidth 200 / FilmStripCollapsed 56 / FilmStripExpanded 200 / InspectorCollapsed 40 / InspectorExpanded 320 / RowDense 24 / RowNormal 26 / StatusBandPage 28 / StatusBandBatch 24 / ControlHeight 28；断点 1024/1280/1600）。✓
- 04 三档断点表与 G-1b 一致；`04:36` 明确「不新增令牌」。✓
- **但 05–08 未同步**（R2-P1-02），且 `04:30` 的 `Narrow <1024` 行为区间与 `ShellLayout.cs` 的 `IsNarrow(width) => width < BreakpointCompact`（<1280）不同——设计可自定 Fluent 断点行为，但应在 04 说明「Fluent 断点行为与 Current `ShellLayout` 三档判定的差异」，否则 FEA-06 复用 Current 逻辑会得到不同结果（P2，并入 R2-P1-02 修法或单列观察项）。

### 4.3 P1-03/P1-04 键盘与 a11y

- 03 §1 全表与 `ShellCommands.cs:57-116` 逐字比对：17 个有键位命令 **全部一致**（`go.to`/`export.run` 已改对）。✓
- 四页 Tab 序：`03:44-50` 与 `05:65`（书架）、`06:71`（工作台，含 film-strip）、`07:66`（阅读器，返回起、顶部信息条最后）、`08:91`（设置，含返回）一致。✓
- 高对比/屏幕阅读器：03 §4/§5 具体可执行；03:53 焦点环令牌引用错误（R2-P1-01）。
- **新问题**：06:49 `Ctrl+Tab`（R2-P1-03）。
- 残留：`03:62` 仍用旧字段名 `Appearance.Contrast`（应为 `appearance.contrast`）——P2（R2-P2-02 同类）。

### 4.4 P1-05 动效

| 判据（C-03 `:71`） | 02 落点 | r2 结论 |
|---|---|---|
| ① `reduce` 下 decorative 0、feedback 保留颜色无位移 | `02:46-50`、`02:38` | ✓（断言仍只写 decorative，但参数表覆盖；P2 残留） |
| ② `full` 不跟随系统 | `02:57` | ✓ |
| ③ `auto` 按注入假平台切换 | `02:58` | ✓ |
| ④ `navigation` reduce 无动画 | `02:59` | ✓ |
| ⑤ 旧 `true` 迁移后三类全禁（等价旧行为） | `02:60` | **部分**：已补 categories 三类关断言，但「全禁」按 `02:17`/`02:38` 仍含 120ms 颜色过渡，不等价「时长 0」→ R2-P1-04 |

- 浮层归属 `navigation` 符合 C-03 `:49` ✓（`02:32`）；`reduce` 不改变布局 ✓（`02:4,65`）。
- 残留 P2：`02:36,46` 表仍只有三列、缺 `auto`（系统关）列；`02:27-30` 曲线命名标签与 cubic-bezier 数值不一致；`02:64`「来自令牌或本表常量」与 `Nm.Motion.*` 无映射；`02:29` 遮罩未引用 `Nm.Color.Scrim`；`07:23` 阅读器条 2s 自动隐藏未归类。

### 4.5 P1-06 状态矩阵（09 与四页正文逐格）

| 09 行 | 书架 05 | 工作台 06 | 阅读器 07 | 设置 08 |
|---|---|---|---|---|
| 空（09:8） | ✓ | ✓ | ✓ | ✓ |
| 空（筛选后）（09:9） | ✓ | **△ 06 正文无「批量筛选无结果」状态**（09 已自述「保留 chips + 清空选择」，正文仅 06:23 提筛选 chips） | ✓（「—，阅读器无筛选」已注明） | **△ 08 正文无「搜索无匹配」状态**（08:78 只述过滤） |
| 载入/错误/满（09:10-12） | ✓ | ✓ | ✓ | ✓ |
| 部分/未决（09:13） | ✓ | ✓ | ✓ | ✓（举例漏 Provider，08:70 有，非矛盾） |
| 冲突（09:14） | ✓（已注明不适用） | ✓ | ✓（已注明不适用） | ✓（已注明不适用） |
| 只读（09:15） | ✓ | ✓ | ✓ | ✓ |
| 运行中（09:16） | ✓（已注明与「扫描中」同态、不重复计数） | **△ 06 正文无「运行中」状态，无「暂停/停止/重试」控制** | **△ 07 正文无「进度写回中」状态**（07:54 只有写失败提示） | ✓（已注明无运行态） |

→ 3 处 △（06 筛选空/运行中、07 运行中、08 搜索空态），降为 P2（R2-P2-01）。`09:31` gate 引用已改为「06 §3 部分/未决 + §4；gate 确认模态『保存/丢弃/取消』」，但 06 正文仍无「gate」术语（语义可映射到 06:49 确认模态）——P2 观察。

### 4.6 P1-07 设置字段（08 与 C-03 §2.2）

| C-03 §2.2 新字段 | 08 落点 | 结论 |
|---|---|---|
| `theme.visualThemeId` / `theme.frontendId` | 08:45-46 | ✓ |
| `appearance.mode` | 08:47「`appearance`」 | **△ 缺 `.mode`** |
| `appearance.contrast` | 08:48「`contrast`」 | **△ 缺 `appearance.`** |
| `layout.*` | 08:52 | ✓ |
| `motion.mode` / `motion.categories` | 08:49-50 | ✓（08:50 同步 categories 关闭语义） |
| `appearance.followSystemAccent` | 08:53「`followSystemAccent`」 | **△ 缺 `appearance.`** |
| `material.acrylicStrength` / `material.micaEnabled` / `corners.scale` | 08:51「`corners`/`material`」 | △ 组名（可读，不精确） |
| `schemaVersion` | 08:54 | ✓ |
| 宿主 surface | 08:3 `ShellSurface.ThemeStudio` | ✓（「其余分组沿用既有设置 surface」仍含糊，P2） |

→ 字段基本补齐，3 处全名缺前缀 → P2（R2-P2-02）。

### 4.7 治理

- `check.ps1` PASS（2 warnings）；`verify_pins.ps1` PASS 15/15。
- 证据表：11/12 哈希一致，selfcheck 哈希过期（R2-P2-04）；12 项 commit 仍 `568cf271e`（内容已变，R2-P2-04）。
- selfcheck 含控制字符（R2-P2-03）；`doc/tasks/FEA-04b.md` `delivery_head: null`、Closeout Record 未记录 r1 处置（收口前补，P2 观察）。
- **STATUS/PLAN 未同步**（仍 `ready`，与 `TASK_LEDGER.md:43` 的 `in_review` 不一致）——r1 P2-14 **未处置**（R2-P2-12）。

### 4.8 是否引入新问题

**是**：
1. `06:49` 未注册键位 `Ctrl+Tab`（R2-P1-03）。
2. selfcheck 控制字符损坏（R2-P2-03）。
3. 02:17 字面 `\n`（R2-P2-05）。
4. 证据表 commit/哈希失配（R2-P2-04）。
5. 04:64 层 2「左导航/检查器」用 `Nm.ZIndex.Base` 与层 1「主内容」同值（层级表不自洽，应 `Nm.ZIndex.Panel`/`Drawer`）——P2（并入 R2-P2-06）。
6. 01:16 焦点环类型 `IBrush`（R2-P1-01）。

## 5. r1 P2 逐条 disposition（14 条）

| r1 P2 | r2 状态 | 说明 |
|---|---|---|
| P2-01 判据①对表覆盖/裸值禁令 | 未关闭 | 01:60-71 仍 10 行；01:73 禁令仍未覆盖尺寸/描边/字号 |
| P2-02 材质深浅两套值无落点 | 未关闭 | 01:41-42 未变；C-02 V-07 仍只注册 `builtin.fluent-dark` |
| P2-03 02 缺 auto（系统关）列/曲线命名 | 未关闭 | 02:36,46 仍三列；02:27-30 命名标签未删 |
| P2-04 02 令牌映射/自动隐藏/Scrim | 未关闭 | 02:64 未变；07:23 未归类；02:29 未引 `Nm.Color.Scrim` |
| P2-05 焦点环/三元路由/旧字段名 | 部分 | 焦点环说明已加但错误（R2-P1-01）；03 三元路由仍未定义；03:62 旧名未改 |
| P2-06 层级 Elevation/ZIndex | 部分 | 04:58-67 已用 `Nm.ZIndex.*`；但 04:67 Tooltip `Elevation.3` vs 01:53 `Elevation.2`、10:51 CommandPalette `Elevation.3` vs 04:65 `Elevation.2` 未统一；新增 04:64 `ZIndex.Base` 同值问题 |
| P2-07 04 共用骨架 vs 07/08 | 部分 | 04:42 删「命令面板」恢复说法 ✓；但 04:9「四页共用」、04:71「四页都使用 §1 骨架」与 07/08 无左导航仍矛盾 |
| P2-08 film-strip/C-03 引用/Opacity/左导航项/阅读器键 | 部分 | 06:22/66/67 film-strip 96/120 未改（并入 R2-P1-02）；06:59 仍「C-03/R-22」；07:34 Opacity 当背景刷未改；05:21 vs 03:44「空间列表」未统一；03 §2 未补阅读器既有 `J/K/Space` |
| P2-09 C-05 误引/07:74/08:39/01:17 | 未关闭 | README:5、selfcheck:26、05:73、07:74、08:39、04:5、01:17 均未改 |
| P2-10 10 组件清单/Badges/FocusRing | 未关闭 | 10:4 未列 `Badges.cs`/`FocusRing`；10:19 `Skeleton.cs` 当令牌；新组件归属未说明 |
| P2-11 08 搜索空态/Provider/10:39 | 部分 | 08 搜索空态未补；10:39 未改；Provider 例子原已有 |
| P2-12 视觉数值禁令缺口 | 部分 | 04:25 声明禁止裸数；但 05/06/08 裸值残留（并入 R2-P1-02） |
| P2-13 缺口登记不足 | 部分 | G-1b 已补 Size/Breakpoint ✓；但 Focus 组处理错误（R2-P1-01）、四页预览未登记、01:17 FEA-05 职责未改 |
| P2-14 STATUS/PLAN ready | **未处置** | 实际仍 `ready`（见 §1） |

## 6. Findings（r2）

| 编号 | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| R2-P1-01 | P1 | `01:16,18`；`03:53`；C-02 `:52,56-57`；`Tokens.Global.axaml:7` | 焦点环「第四组」写成「现有键承载、无 `Nm.Focus.Ring.*` 族」，与 C-02 V-03 冻结组冲突（缺键判违规）；`Nm.Border.Focus` 是 `Thickness` 却被当环色/标 `IBrush`。 | 见 §2 最小修法：由 FEA-05 生成 `Nm.Focus.Ring.Width/Offset/Color`（取值 2/1/`Nm.Color.Accent.Ring`），`Nm.Border.Focus` 仅作厚度引用。 |
| R2-P1-02 | P1 | `05:15,59,61`；`06:15,22,24,65-67`；`07:60,62`；`08:14,85-87`；对照 `04:30-33`、`01:22` | 04/01 已改三档+令牌，05–08 未同步：仍用旧四档 `Compact/Medium/Expanded/Wide`、240/96/120 裸值，与 04 及 G-1b 直接矛盾（如 05:59「Compact 单列」vs 04 Compact 三栏）。 | 05–08 §响应式统一改写为 04 四区间；240→`TreeWidth` 或折叠隐藏；96/120→`FilmStripCollapsed/Expanded`；其余裸值登记或改令牌。 |
| R2-P1-03 | P1 | `06:49`；对照 `ShellCommands.cs:57-116`、`03:13` | 新引入 `Ctrl+Tab`（未在 `ShellCommands.cs`/KeyMap/03 注册），违反「KeyMap 唯一键位来源」，且与 06:72 自相矛盾。 | 删除该句；若确需，先在 `ShellCommands.cs` 注册（DSH 单点提交）并同步 03 §1。 |
| R2-P1-04 | P1 | `02:17,38,60`；C-03 `:57,71` | 「三类全禁」按新定义仍含 120ms 颜色过渡，不等价 C-03 旧行为（时长 0），判据⑤「等价旧行为」不可验证。 | `02:38` reduce 列 feedback 改 0ms 瞬时变色；或明确「全禁=动画时长 0」口径并请 DSH 裁决 C-03 措辞。 |
| R2-P2-01 | P2 | `09:9,16`；`06:40-51`；`07:37-54`；`08:59-78` | 09 矩阵 3 处仍无正文定义：工作台「批量筛选无结果/运行中控制」、阅读器「进度写回中」、设置「搜索无匹配」。 | 06/07/08 补对应状态行（或删矩阵格并注明「非设计态」）。 |
| R2-P2-02 | P2 | `08:47,48,53,51`；C-03 `:36-44` | 字段全名不精确：`appearance`→`appearance.mode`、`contrast`→`appearance.contrast`、`followSystemAccent`→`appearance.followSystemAccent`、`corners/material`→`corners.scale`/`material.acrylicStrength`/`material.micaEnabled`；`03:62` 仍用旧名 `Appearance.Contrast`。 | 按 C-03 §2.2 补全全名。 |
| R2-P2-03 | P2 | `verification/FEA-04b/design-baseline-selfcheck.md:52,53,55` | 文件含控制字符（0x1B/0x0C/0x07），`export.run`/`full`/`appearance`/`followSystemAccent` 被破坏，文件损坏。 | 重写 §5 为纯文本，重算哈希。 |
| R2-P2-04 | P2 | `doc/tasks/FEA-04b.md:88-99` | 证据表 commit 仍 `568cf271e`（内容已变为 `e173d156d`）；selfcheck sha256 过期（`b3473cb5…` vs 实际 `752c2de7…`）。 | commit 改 `e173d156d`；重算 selfcheck 哈希；填 `delivery_head`。 |
| R2-P2-05 | P2 | `02:17` | 含字面 `\n`（两字符），Markdown 渲染异常。 | 改为真实换行。 |
| R2-P2-06 | P2 | `04:64`；`04:67`；`01:53`；`10:51` | 层级：层 2 与层 1 同用 `Nm.ZIndex.Base`；Tooltip/通知条 `Elevation.3` vs 01:53 `Elevation.2`；CommandPalette `Elevation.3` vs 04:65 层 3 `Elevation.2`。 | 层 2 用 `Nm.ZIndex.Panel`；统一 Tooltip/CommandPalette 的 Elevation 归属。 |
| R2-P2-07 | P2 | `01:60-71,73` | 判据①对表仍 10 行（未覆盖详情栏/缩略图条/主画布/批量单元格/焦点环/遮罩）；裸值禁令未覆盖尺寸/描边/字号。 | 补齐对表；禁令扩为「任何视觉数值」。 |
| R2-P2-08 | P2 | `01:41-42,72-73`；C-02 `:89-90` | 材质深/浅两套值仍无浅色视觉主题落点；01:72 仍限定 visualTheme=fluent-dark。 | 声明浅色值暂不落库或登记新视觉主题裁决项。 |
| R2-P2-09 | P2 | `02:36,46`；`02:27-30`；`02:64`；`02:29`；`07:23` | 缺 auto（系统关）列；曲线命名标签与数值不符；令牌映射自相矛盾；遮罩未引 `Nm.Color.Scrim`；阅读器 2s 自动隐藏未归类。 | 逐项补列/删标签/补映射/引 Scrim/归类。 |
| R2-P2-10 | P2 | `README:5`；`selfcheck:26`；`05:73`；`07:74`；`08:39`；`06:59`；`04:5`；`01:17` | 引用错误未修：C-05（页可见性谓词）被当四页结构依据；06:59 引 C-03（应为 C-08/R-22）；07:74「FEA-01 冻结字段」；08:39 `Skeleton/Status.cs` 当 InfoBar；01:17 令牌生成归 FEA-05。 | 逐项改正引用（见 r1 建议）。 |
| R2-P2-11 | P2 | `10:4,19,51-53`；`Badges.cs`；`Theming/FocusRing.cs` | 组件清单未列 `StatusBadge/Chip/Kbd`/`FocusRing`；`Skeleton.cs` 当令牌；新组件归属未按 V-06 说明。 | 清单加「既有/新增/归属」列并补既有组件。 |
| R2-P2-12 | P2 | `doc/STATUS.md:7`；`doc/REBASELINE_PLAN.md:17` | **r1 P2-14 未处置**：STATUS/PLAN 仍 `ready`，与 `TASK_LEDGER.md:43` 的 `in_review` 不一致；本次 diff 未含这两文件（与派发说明「已同步」不符）。 | 更新 STATUS/PLAN 为 `in_review`（或说明 `ready` 的 DAG 语义）。 |
| R2-P2-13 | P2 | `04:30,36`；`ShellLayout.cs:17-19` | 04 定义 `Narrow <1024`，而 Current `IsNarrow(width) => width < BreakpointCompact`（<1280）；Fluent 复用 Current 判定会得到不同结果。 | 04 增说明「Fluent 断点行为与 Current 差异」或对齐代码。 |
| R2-P2-14 | P2 | `05:21` vs `03:44` | 书架 Tab 序「左导航（空间列表）」与 05:21 左导航项（书架/回收站/导入）仍不一致。 | 统一措辞（空间列表/书架导航）。 |
| R2-P2-15 | P2 | `06:22,65-67`；`StudioFilmStrip.cs:15` | film-strip 设计值 96/120 与既有实现 56/200 未对齐（并入 R2-P1-02 修） | 同 R2-P1-02。 |
| R2-P2-16 | P2 | `08:3` | 「其余分组沿用既有设置 surface」——V11R `ShellSurface` 无 Settings/既有设置 surface，表述仍含糊。 | 写死「Provider/网络/备份/关于沿用 `ShellSurface.ThemeStudio` 或既有 V2 设置视图（需 DSH 裁决）」。 |
| R2-P2-17 | P2 | `selfcheck:30-36`；`01:17`；方案 `:645` | 缺口登记仍不足：Focus 组处理错误（R2-P1-01）、FEA-06 AC「四页和四页预览」无规格、令牌生成职责未改。 | 扩 G-1；补「四页预览」或登记后续任务。 |

## 7. 边界声明

- 本报告只审 **设计基线（AC1–AC4）**；**AC5（用户确认）不在本报告范围**（`FEA-04b.md:65` 仍 `[ ]`/PARTIAL）。
- 只读：未修改任何被审文件；被审 head `e173d156d` 工作区 clean；未 commit/push。
- 未验证项：高对比实际渲染与对比度（需实现后验证）；`Nm.Material.*`/`Nm.Elevation.*`/`Nm.Corner.Fluent.*`/`Nm.Focus.Ring.*` 生成后的资源加载（代码尚不存在）；FEA-05/06 实现可行性为设计层推断。
- 复核建议：R2-P1-01…04 全部处置（或 DSH 明确裁决）后重跑 `check.ps1`/`verify_pins.ps1`、修正证据表 commit/哈希、重算 selfcheck 哈希，再提交 r3；r2 P2 建议同批处置以免反复。
