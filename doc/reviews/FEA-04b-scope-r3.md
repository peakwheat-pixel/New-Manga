# FEA-04b 范围复核 r3（同一独立席位，续任）

| 字段 | 值 |
|---|---|
| base_commit | `e173d156d` |
| reviewed_head | `f08c6648b`（main，clean；r2 处置提交） |
| 上一轮 | `doc/reviews/FEA-04b-scope-r2.md`（reviewed_head `e173d156d`） |
| reviewer | `fea04b-scope-reviewer` |
| reviewer 来源 | DSH Team Lead 派发，fresh 独立上下文；**r1/r2 同一席位续任**；未参与 FEA-04b 起草；只读被审 head |
| 日期 | 2026-11-02 |
| 审查范围 | AC1–AC4（设计基线）。**AC5（用户确认）不在本报告范围** |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 1 / P2 = 15** |

> 说明：r2 的 P1×4 中 **3 条完全关闭**（焦点环 G-1c、`Ctrl+Tab`、判据⑤），**1 条部分关闭**（05–08 断点/尺寸同步——响应式表已改，但 `06:24` 的 Compact 行为与图内 240/72 裸值仍未清）。因仍有 P1=1，**不写 approved**。

## 0. 方法、只读声明与复现

- 只读核查被审 head；**未修改任何被审文件**，未 commit、未 push；本报告是本轮唯一新增文件。
- 复现（本次实跑）：
  - `git rev-parse HEAD` → `f08c6648b06264f053a5e8fac44e7d1b720dc9fc`；`git status --porcelain` → 空。
  - `git diff --name-status e173d156d..f08c6648b` → `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/design/fluent-v1/01,02,03,05,06,07,08`、`doc/reviews/FEA-04b-scope-r2.md`（已在提交中）、`doc/tasks/FEA-04b.md`、`verification/FEA-04b/design-baseline-selfcheck.md`；**未触碰 `doc/plan/**` 冻结契约、`apps/**`、`src/**`**。
  - `pwsh -NoProfile -File tools/governance/check.ps1` → `PASS (2 warnings)`。
  - `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → `PASS (all 15)`。
  - 证据表 **12/12 sha256 复算一致**（commit 列已统一 `e173d156d`）。
  - selfcheck 控制字符扫描 → **CLEAN**（无 0x00–0x08/0x0B/0x0C/0x0E–0x1F）；但 §5 文本仍丢字（见 R3-P2-03）。

## 1. r2 逐项 disposition（P1×4 + P2×17）

### 1.1 r2 P1

| r2 finding | r3 结论 | 证据 |
|---|---|---|
| **R2-P1-01 焦点环** | **已关闭**：01:16 改为「C-02 V-03 定义 `Nm.Focus.Ring.Width/Offset/Color`；当前不存在；`Nm.Border.Focus` 是 `Thickness` 不能替代环色」；01:18 登记 **G-1c**（FEA-05 生成或 DSH 裁决）；03:53 同步引用三键并指向 G-1c | `01:16,18`；`03:53`；C-02 `:52,56-57`；`Tokens.Global.axaml:7` |
| **R2-P1-02 05–08 断点/尺寸** | **部分关闭**：05:59-61、06:65-67、07:60-62、08:85-87 响应式表已改 `Narrow/Medium/Compact/Full` 并令牌化（TreeWidth 200 / FilmStripCollapsed 56 / FilmStripExpanded 200 / InspectorExpanded 320 / Breakpoint.Full）；**但 `06:24` 仍写「检查器在 Compact 断点变为抽屉」（与 04:33 Compact=三栏、06:65 Narrow=抽屉矛盾），且 05:15「72/240」、06:15「240」、08:14「240」图内裸值与响应式表 `Nm.Size.TreeWidth`（200）矛盾** → **R3-P1-01** | `04:30-33`；`05:15,61`；`06:15,24,65-67`；`08:14,86-87` |
| **R2-P1-03 `Ctrl+Tab`** | **已关闭**：`06:49` 已删除该子句；06:72/03:34 只保留页签条内 `←`/`→`、全局 `Tab`=`studio.mode.toggle` | `06:49,72`；`03:13,34`；`ShellCommands.cs:63` |
| **R2-P1-04 判据⑤** | **已关闭**：`02:61` 判据⑤改为「旧值→`reduce`+三类关；断言所有类别时长（含 `feedback` 颜色过渡）= 0ms」等价 C-03 `:57`「所有时长置 0」；`02:39` feedback 行补「categories=关 或旧值迁移后颜色过渡亦 0ms」 | `02:39,61`；C-03 `:57,71` |

### 1.2 r2 P2

| r2 P2 | r3 状态 |
|---|---|
| R2-P2-01（09 vs 06/07/08 正文 3 处） | 未关闭（09 未改；06/07/08 正文未补「运行中/搜索空态」） |
| R2-P2-02（08 字段全名 + 03:62 旧名） | 未关闭（`08:47/48/53` 仍 `appearance`/`contrast`/`followSystemAccent`；`03:62` 仍 `Appearance.Contrast`） |
| R2-P2-03（selfcheck 控制字符） | **部分关闭**：控制字符已清（CLEAN），但文本仍丢首字母：`xport.run`/`educe`/`ull`/`ppearance`/`ollowSystemAccent` |
| R2-P2-04（证据表 commit/哈希） | **已关闭**：12 项 commit=`e173d156d`；12/12 哈希复算一致（含 selfcheck `c127a8f6…`） |
| R2-P2-05（02 字面 `\n`） | **已关闭**：02:17-18 已拆为两段 |
| R2-P2-06（层级 ZIndex/Elevation） | 未关闭（04 未改：`04:64` 层 2 与层 1 同用 `ZIndex.Base`；`04:67` Tooltip `Elevation.3` vs `01:53` `Elevation.2`；`10:51` CommandPalette `Elevation.3` vs `04:65` `Elevation.2`） |
| R2-P2-07（01 判据①对表/裸值禁令） | 未关闭（01:60-71 仍 10 行；01:73 禁令未覆盖尺寸/描边/字号） |
| R2-P2-08（材质深浅两套值） | 未关闭（01:41-42 未变） |
| R2-P2-09（02 auto 列/曲线/映射/Scrim/自动隐藏） | 未关闭（02:26/47 仍三列；02:28-31 命名标签；02:65 映射；02:30 未引 `Nm.Color.Scrim`；07:23 未归类） |
| R2-P2-10（引用错误） | 未关闭（README:5、selfcheck:26、05:73、07:74、08:39、06:59、04:5、01:17 均未改） |
| R2-P2-11（10 组件清单） | 未关闭（10 未改） |
| R2-P2-12（STATUS/PLAN ready） | **已关闭**：`doc/STATUS.md:7` 与 `doc/REBASELINE_PLAN.md:17` 已改 `in_review` |
| R2-P2-13（04 断点 vs `ShellLayout.IsNarrow`） | 未关闭（04 未改） |
| R2-P2-14（05:21 vs 03:44 左导航措辞） | 未关闭（03:44 仍「空间列表」，05:21 仍书架/回收站/导入） |
| R2-P2-15（film-strip 96/120） | **已关闭**（06:22「`FilmStripCollapsed`（56）」；06:66/67 `FilmStripExpanded` 200） |
| R2-P2-16（08:3 其余分组 surface） | 未关闭（08:3 表述未变） |
| R2-P2-17（缺口登记：Focus/四页预览/FEA-05 职责） | **部分关闭**（G-1c 已登记 ✓；四页预览/01:17 职责未改） |

## 2. 仍存在的 P1（1 条，含最小修法）

### R3-P1-01（r2 P1-02 部分关闭残留）`06:24` 断点行为矛盾 + 页内 240/72 裸值与令牌冲突

- `06:24`：「检查器在 **Compact** 断点变为抽屉；批量模式在 **Compact** 下矩阵横向滚动 + 列固定首列」——三档体系下 `Compact`=1280–1599（`04:32-33` 为三栏、检查器 `InspectorExpanded` 320 固定），抽屉发生在 `Narrow`（`<1024`，`04:30`、`06:65`）。同页 §1 与 §5 直接矛盾，且与 04 冲突；实现者按 §1 会在 1280–1599 宽屏做抽屉（与 §5/04 三栏相悖）。
- 图内裸值与令牌/响应式表矛盾：
  - `05:15`「72/240」 vs `05:61`「左导航 `Nm.Size.TreeWidth` 200」；
  - `06:15`「240」 vs `04:22`/G-1b `TreeWidth` 200；
  - `08:14`「分组列表 240」 vs `08:86`「`Nm.Size.TreeWidth` 200」。
  （派发说明称「尺寸裸值 240/96/120/320/360 全部改为令牌」——320/360/120 已改，240 仍在 05/06/08 图内。）
- **最小修法**：`06:24` 两处 `Compact` 改 `Narrow（<1024）`；`05:15`/`06:15`/`08:14` 图中数字改为 `Nm.Size.TreeWidth`（200）或删除数值；同批处理 R3-P2-01 列出的 96/40/36 等残留。

## 3. 新发现 P2（对应 §5 编号 R3-P2-01/02）

| 编号 | 位置 | 问题 | 建议 |
|---|---|---|---|
| R3-P2-01 | `06:37`；`07:12,18` | 残留裸值：`06:37`「矩阵列宽最小 96」、`07:12`「高 40」、`07:18`「高 36」——均无令牌落点，与 `01:22` G-1b「不得在本基线写裸数」及 `04:25`「禁止写死 36/200/28 等裸数」冲突（40/36 可考虑映射 `Nm.Size.TopBand`/`SubBand`/`StatusBandPage`，或登记常量）。 | 改令牌名或登记豁免常量。 |
| R3-P2-02 | `selfcheck:46-56`；`FEA-04b.md:105-109,17` | 治理记录不完整：selfcheck §5 只有「r1 复核处置」，**无 r2 处置记录**；`doc/tasks/FEA-04b.md` Closeout Record 未记录 r1/r2 处置；`delivery_head` 仍 `null`（收口前应填 `f08c6648b` 或最终交付 head）。 | 补 selfcheck §6「r2 处置」；Closeout 记录两轮处置；收口时填 `delivery_head`。 |

## 4. 逐项核查（对应派发 7 点）

### 4.1 R2-P1-01 焦点环（G-1c）——**通过**

- `01:16` 表行：令牌=`Nm.Focus.Ring.Width/.Offset/.Color`，类型 `double`/`double`/`IBrush`，状态「当前不存在（`NmKeys.g.cs` 无此族）；既有 `Nm.Border.Focus` 是 `Thickness` 边框宽度，不能替代环色——须由 FEA-05 按 C-02 生成，或 DSH 裁决」。与 C-02 `:52`（新增焦点组）、`:56-57`（缺键判违规）一致；`Nm.Border.Focus` 类型与 `Tokens.Global.axaml:7`（Thickness 2,2,2,2）一致。✓
- `01:18` G-1c 登记清晰（FEA-05 生成或 DSH 裁决；03 §3 取值 2px/1px/`Nm.Focus.Ring.Color`）。✓
- `03:53` 已改引用三键并指 G-1c。✓

### 4.2 R2-P1-02 05–08 断点/尺寸——**部分通过（R3-P1-01）**

- 响应式表全部改为 `Narrow(<1024)/Medium(1024–1279)/Compact/Full(≥1280)`（`05:59-61`、`06:65-67`、`07:60-62`、`08:85-87`），与 `04:30-33` 一致；尺寸改用 `TreeWidth` 200 / `FilmStripCollapsed` 56 / `FilmStripExpanded` 200 / `InspectorExpanded` 320 / `Breakpoint.Full`。✓
- 残留：`06:24` Compact 行为矛盾；`05:15`/`06:15`/`08:14` 图内 72/240 与 200 冲突；`06:37` 96、`07:12/18` 40/36 裸值（R3-P1-01 / R3-P2-01）。

### 4.3 R2-P1-03 `Ctrl+Tab`——**通过**

- `06:49` 已删；`03:34` 和 `06:72` 仅 `←`/`→` 页签切换 + 全局 `Tab`=`studio.mode.toggle`；`ShellCommands.cs:57-116` 无 `Ctrl+Tab`，设计不再引用不存在键位。✓

### 4.4 R2-P1-04 判据⑤——**通过**

| 判据（C-03 `:71`） | r3 落点 | 结论 |
|---|---|---|
| ① reduce 下 decorative 0 / feedback 保留颜色无位移 | `02:47-51`、`02:39` | ✓ |
| ② full 不跟随系统 | `02:58` | ✓ |
| ③ auto 按注入假平台切换 | `02:59` | ✓ |
| ④ navigation reduce 无动画 | `02:60` | ✓ |
| ⑤ 旧 true 迁移后三类全禁（等价旧行为） | `02:61`（所有类别时长含 feedback 颜色过渡 = 0ms）+ `02:14` | ✓ 满足 C-03 `:57`「所有时长置 0」 |

- 浮层归 `navigation`（`02:33`，C-03 `:49`）✓；`reduce` 不改变布局（`02:4,66`）✓。
- 残留 P2：`02:37/47` 仍缺 `auto`（系统关）列；`02:28-31` 曲线命名标签；`02:65`「令牌或本表常量」映射；遮罩未引 `Nm.Color.Scrim`（R3-P2-04）。

### 4.5 P2：selfcheck / 证据表 / 02 字面 `\n`——**部分通过**

- selfcheck 控制字符：**已清除**（字节扫描 CLEAN；sha256 `c127a8f6…`）。但 `selfcheck:52,53,54,55,57` 文本仍丢首字母（`go.to/xport.run`、`educe`、`ull`、`ppearance`、`ollowSystemAccent`）——控制字符被删时吞掉了原字符，需补回（R3-P2-03）。
- 证据表：12 项 commit 已统一 `e173d156d`；**12/12 sha256 复算一致**；selfcheck 哈希 `c127a8f6…` 与实际一致。✓
- 02 字面 `\n`：已拆为两段（`02:17-18`）。✓

### 4.6 P2-14 治理指针——**通过**

- `doc/STATUS.md:7` = `in_review`（「独立复核 r1→r2 处置中」）；`doc/REBASELINE_PLAN.md:17` = `in_review`；`doc/TASK_LEDGER.md:43` = `in_review`。三者一致。✓
- 备注：STATUS 文案「r1→r2 处置中」建议在 r3 处置后更新为「r1→r3」。

### 4.7 是否引入新问题

**未发现新的 P1**；新发现 2 条 P2（R3-P2-01 残留裸值、R3-P2-02 治理记录）。另确认未触碰冻结契约/代码/枚举；`git diff` 仅文档与证据。

## 5. Findings（r3）

| 编号 | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| R3-P1-01 | P1 | `06:24`；`05:15`；`06:15`；`08:14`；对照 `04:30-33`、`05:61`、`06:65-67`、`08:86` | **r2 P1-02 残留**：`06:24` 把抽屉发生在 `Compact`（1280–1599）写出，与 04/06:65 的 `Narrow` 抽屉、`Compact` 三栏矛盾；`05:15`「72/240」、`06:15`「240」、`08:14`「240」与 `Nm.Size.TreeWidth`（200）矛盾。 | `06:24` 两处 `Compact`→`Narrow（<1024）`；图中 72/240 改 `Nm.Size.TreeWidth`（200）或删数值。 |
| R3-P2-01 | P2 | `06:37`；`07:12,18` | `06:37`「矩阵列宽最小 96」、`07:12`「高 40」、`07:18`「高 36」为裸值，与 G-1b/04:25「不得写裸数」冲突。 | 改令牌名或登记豁免常量。 |
| R3-P2-02 | P2 | `selfcheck:46-56`；`FEA-04b.md:17,105-109` | selfcheck 无 r2 处置记录；Closeout 未记 r1/r2；`delivery_head` 仍 `null`。 | 补 §6 r2 处置；Closeout 记录；收口填 `delivery_head`。 |
| R3-P2-03 | P2 | `selfcheck §5（:52-57）` | 控制字符已清但文本丢字：`xport.run`/`educe`/`ull`/`ppearance`/`ollowSystemAccent`（应为 `export.run`/`reduce`/`full`/`appearance`/`followSystemAccent`）。 | 重写 §5 该 3 行，补回字母。 |
| R3-P2-04 | P2 | `02:37,47`；`02:28-31`；`02:65`；`02:30`；`07:23` | （r2 P2-09 未关闭）02 表缺 `auto`（系统关）列；曲线命名标签与数值不符；「令牌或本表常量」无映射；遮罩未引 `Nm.Color.Scrim`；阅读器 2s 自动隐藏未归类。 | 逐项补列/删标签/补映射/引 Scrim/归类。 |
| R3-P2-05 | P2 | `08:47,48,53`；`03:62` | （r2 P2-02 未关闭）字段全名仍不精确：`appearance`→`appearance.mode`、`contrast`→`appearance.contrast`、`followSystemAccent`→`appearance.followSystemAccent`；03:62 仍 `Appearance.Contrast`。 | 按 C-03 §2.2 补全。 |
| R3-P2-06 | P2 | `09:9,16`；`06:40-51`；`07:37-54`；`08:59-78` | （r2 P2-01 未关闭）09 矩阵 3 处仍无正文定义：工作台「批量筛选无结果/运行中控制」、阅读器「进度写回中」、设置「搜索无匹配」。 | 06/07/08 补状态行或删矩阵格。 |
| R3-P2-07 | P2 | `04:64,67`；`01:53`；`10:51` | （r2 P2-06 未关闭）层 2 与层 1 同用 `ZIndex.Base`；Tooltip/CommandPalette 的 `Elevation.3` 与 01/04 的 `Elevation.2` 不统一。 | 层 2 用 `Nm.ZIndex.Panel`；统一 Elevation 归属。 |
| R3-P2-08 | P2 | `01:60-71,73` | （r2 P2-07 未关闭）判据①对表仍 10 行；裸值禁令未覆盖尺寸/描边/字号。 | 补齐对表；禁令扩为「任何视觉数值」。 |
| R3-P2-09 | P2 | `01:41-42,72-73` | （r2 P2-08 未关闭）材质深/浅两套值无浅色视觉主题落点。 | 声明暂不落库或登记裁决项。 |
| R3-P2-10 | P2 | `README:5`；`selfcheck:26`；`05:73`；`07:74`；`08:39`；`06:59`；`04:5`；`01:17` | （r2 P2-10 未关闭）引用错误：C-05 被当四页结构依据；`06:59` 引 C-03（应为 C-08/R-22）；`07:74`「FEA-01 冻结字段」；`08:39` `Skeleton/Status.cs` 当 InfoBar；`01:17` 令牌生成归 FEA-05。 | 逐项改正引用。 |
| R3-P2-11 | P2 | `10:4,19,51-53` | （r2 P2-11 未关闭）组件清单未列 `StatusBadge/Chip/Kbd`/`FocusRing`；`Skeleton.cs` 当令牌；新组件归属未按 V-06 说明。 | 清单补既有组件与归属列。 |
| R3-P2-12 | P2 | `04:30,36`；`ShellLayout.cs:17-19` | （r2 P2-13 未关闭）04 定义 `Narrow <1024`，Current `IsNarrow` 用 `<1280`；Fluent 复用 Current 判定会不同。 | 04 说明差异或对齐代码。 |
| R3-P2-13 | P2 | `05:21` vs `03:44` | （r2 P2-14 未关闭）03:44「左导航（空间列表）」与 05:21 左导航项（书架/回收站/导入）不一致。 | 统一措辞。 |
| R3-P2-14 | P2 | `08:3` | （r2 P2-16 未关闭）「其余分组沿用既有设置 surface」——V11R `ShellSurface` 无 Settings/既有设置 surface，表述含糊。 | 写死宿主或登记 DSH 裁决。 |
| R3-P2-15 | P2 | `selfcheck:30-36`；`01:17`；方案 `:645` | （r2 P2-17 部分关闭）G-1c 已登记 ✓；四页预览未登记、`01:17` FEA-05 职责未改。 | 补 G-1 四页预览/职责说明。 |

## 6. 边界声明

- 本报告只审 **设计基线（AC1–AC4）**；**AC5（用户确认）不在本报告范围**（`FEA-04b.md:65` 仍 `[ ]`/PARTIAL）。
- 只读：未修改任何被审文件；被审 head `f08c6648b` 工作区 clean；未 commit/push。
- 未验证项：高对比实际渲染与对比度（需实现后验证）；`Nm.Material.*`/`Nm.Elevation.*`/`Nm.Corner.Fluent.*`/`Nm.Focus.Ring.*` 生成后的资源加载（代码尚不存在）；FEA-05/06 实现可行性为设计层推断。
- 复核建议：R3-P1-01（+同批 R3-P2-01/03/05）处置后重跑 `check.ps1`/`verify_pins.ps1`、重算证据表哈希（含 selfcheck），再提交 r4；其余 P2 可在收口前同批清理，不阻断设计基线冻结。
