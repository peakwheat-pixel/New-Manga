# FEA-04b 范围复核 r5（同一独立席位，续任）

| 字段 | 值 |
|---|---|
| base_commit | `f224280df` |
| reviewed_head | `d4da1f1cb`（main，clean；r4 处置提交） |
| 上一轮 | `doc/reviews/FEA-04b-scope-r4.md`（reviewed_head `f224280df`） |
| reviewer | `fea04b-scope-reviewer` |
| reviewer 来源 | DSH Team Lead 派发，fresh 独立上下文；**r1–r4 同一席位续任**；未参与 FEA-04b 起草；只读被审 head |
| 日期 | 2026-11-02 |
| 审查范围 | AC1–AC4（设计基线）。**AC5（用户确认）不在本报告范围** |
| 结论 | **approved** |
| 计数 | **P0 = 0 / P1 = 0 / P2 = 16** |

> **批准声明**：按派发口径「P0/P1=0 即 approved」——r4 的唯一 P1（R4-P1-01 列宽令牌错配）已关闭，本轮未发现 P0/P1；故对本轮设计基线（AC1–AC4 文档范围）**批准 `approved`**。P2×16 均为文档一致性/收口记录事项，不阻断设计基线冻结；建议在收口前同批清理（清单见 §3）。

## 0. 方法、只读声明与复现

- 只读核查被审 head；**未修改任何被审文件**，未 commit、未 push；本报告是本轮唯一新增文件。
- 复现（本次实跑）：
  - `git rev-parse HEAD` → `d4da1f1cb0101eafa462cd9e22f3b551b99f904f`；`git status --porcelain` → 空。
  - `git diff --name-status f224280df..d4da1f1cb` → `doc/design/fluent-v1/01,06`、`doc/reviews/FEA-04b-scope-r4.md`（已在提交中）、`doc/tasks/FEA-04b.md`、`verification/FEA-04b/design-baseline-selfcheck.md`；**未触碰 `doc/plan/**` 冻结契约、`apps/**`、`src/**`**；枚举未新增。
  - `pwsh -NoProfile -File tools/governance/check.ps1` → `PASS (2 warnings)`。
  - `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → `PASS (all 15)`。
  - 证据表 **12/12 sha256 复算一致**（README/01–10/selfcheck 全部与当前文件一致）。
  - selfcheck 字节扫描 → **CLEAN**（无控制字符）；全文 grep `rreduce`/`Aappearance`/`ull 下`/`173d156d`/`xport` → **无命中**（丢字已修）。

## 1. r4 逐项 disposition（P1×1 + P2×17）

### 1.1 r4 P1

| r4 finding | r5 结论 | 证据 |
|---|---|---|
| **R4-P1-01** `06:37` 列宽改为行高令牌 `Nm.Size.RowNormal`（26） | **已关闭**：`06:37` 恢复「列宽最小 **96**（设计常量，FEA-05 登记/DSH 裁决，见 01 G-1b）」；`01:22` G-1b 增补「已登记的设计常量：批量矩阵列宽最小 96（现有 `Nm.Size.*` 无列宽令牌；`TreeWidth` 200 过宽，故作为设计常量，FEA-05 生成令牌时登记）」——令牌语义错配与 26px 不可用问题均解除 | `06:37`；`01:22`；`Tokens.Global.axaml:73` |

### 1.2 r4 P2

| r4 P2 | r5 状态 |
|---|---|
| R4-P2-01（`07:12,18` 条高用 `ControlHeight` 语义不精确） | **未处置**（07 未改）——P2 保留 |
| R4-P2-02（selfcheck 文本损坏：`full`/`rreduce`/`Aappearance`/`173d156d`/ESC） | **已关闭**：selfcheck 全文重写，字节扫描 CLEAN，grep 无错字；`export.run`/`reduce`/`full`/`appearance`/`followSystemAccent` 均正确 |
| R4-P2-03（selfcheck 未同步：旧断点命名、G-1b/G-1c 未登记） | **已关闭**：`selfcheck:11` 改 Narrow/Medium/Compact/Full；`§3` 补 G-1b/G-1c（`:33-34`） |
| R4-P2-04（证据表 commit 与内容不配对） | **部分关闭**：12 项 sha256 已按最终文件重算且**12/12 复算一致** ✓；commit 列统一 `f224280df`——与本次内容（`d4da1f1cb`）仍不配对；DSH 已声明「收口时统一为最终交付 head」，属收口事项（P2 保留，非阻断） |
| R4-P2-05（02 auto 列/曲线/映射/Scrim/自动隐藏） | 未处置（02 未改）——P2 |
| R4-P2-06（08 字段全名 + `03:62` 旧名） | 未处置——P2 |
| R4-P2-07（09 vs 06/07/08 正文 3 处） | 未处置——P2 |
| R4-P2-08（层级 ZIndex/Elevation） | 未处置——P2 |
| R4-P2-09（01 判据①对表/裸值禁令） | 未处置——P2 |
| R4-P2-10（材质深浅两套值） | 未处置——P2 |
| R4-P2-11（引用错误 C-05/C-03/FEA-01/InfoBar/FEA-05 职责） | 未处置——P2（selfcheck §2 仍写 C-05「四页不新增页」的误引语义） |
| R4-P2-12（10 组件清单） | 未处置——P2 |
| R4-P2-13（04 断点 vs `ShellLayout.IsNarrow`） | 未处置——P2 |
| R4-P2-14（05:21 vs 03:44 左导航措辞） | 未处置——P2 |
| R4-P2-15（08:3 其余分组 surface） | 未处置——P2 |
| R4-P2-16（缺口登记：四页预览/01:17 职责） | 未处置——P2 |
| R4-P2-17（`delivery_head` 仍 `null`） | 未关闭（设计 Task 收口前状态；收口时必须填最终 head）——P2 |

## 2. 通过项（本轮核对）

1. **R4-P1-01 关闭**：`06:37` =「列宽最小 96（设计常量，FEA-05 登记/DSH 裁决，见 01 G-1b）」；`01:22` G-1b 已登记该设计常量，并说明「`Nm.Size.*` 无列宽令牌、`TreeWidth` 200 过宽」的理由。与 01 G-1b「任何额外尺寸须先登记并由 DSH 裁决」一致。✓
2. **selfcheck 修复**：全文重写后结构完整（AC 对应/上游一致性/缺口登记 G-1/G-1b/G-1c/G-2/G-3/G-4/复核处置 r1–r4/评审要点）；控制字符 CLEAN；断点口径与 04 一致；错字修复。✓
3. **证据表**：12 项 sha256 与当前文件 12/12 一致；commit 列统一 `f224280df`（最终 head 待收口统一，见 §3 R5-P2-02）。✓
4. **未引入新问题**：diff 仅 01/06 各 1 行 + selfcheck + FEA-04b 证据表/Closeout；未触碰冻结契约、代码、枚举；`check.ps1`/`verify_pins.ps1` PASS。✓

## 3. P2 残留清单（16 条，不阻断）

| 编号 | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| R5-P2-01 | P2 | `07:12,18` | 阅读器顶/底条高用 `Nm.Size.ControlHeight`（控件高度 28）语义不精确（原 40/36）；建议 `TopBand`（36）/`StatusBandPage`（28）。 | 改令牌或书面说明理由。 |
| R5-P2-02 | P2 | `FEA-04b.md:88-99` | 证据表 commit 列 `f224280df` 与最终内容（`d4da1f1cb`）不配对；DSH 声明收口时统一。 | 收口时 commit 列改最终交付 head 并复核哈希。 |
| R5-P2-03 | P2 | `02:37,47`；`02:28-31`；`02:65`；`02:30`；`07:23` | 02 缺 `auto`（系统关）列；曲线命名标签与 cubic-bezier 数值不一致；「令牌或本表常量」无映射；遮罩未引 `Nm.Color.Scrim`；阅读器 2s 自动隐藏未归类。 | 逐项补列/删标签/补映射/引 Scrim/归类。 |
| R5-P2-04 | P2 | `08:47,48,53`；`03:62` | 字段全名不精确：`appearance`→`appearance.mode`、`contrast`→`appearance.contrast`、`followSystemAccent`→`appearance.followSystemAccent`；`03:62` 仍 `Appearance.Contrast`。 | 按 C-03 §2.2 补全。 |
| R5-P2-05 | P2 | `09:9,16`；`06:40-51`；`07:37-54`；`08:59-78` | 09 矩阵 3 处仍无正文定义（工作台「批量筛选无结果/运行中控制」、阅读器「进度写回中」、设置「搜索无匹配」）。 | 补正文状态行或删矩阵格。 |
| R5-P2-06 | P2 | `04:64,67`；`01:53`；`10:51` | 层 2 与层 1 同用 `ZIndex.Base`；Tooltip/CommandPalette 的 `Elevation.3` 与 01/04 的 `Elevation.2` 不统一。 | 层 2 用 `Nm.ZIndex.Panel`；统一 Elevation。 |
| R5-P2-07 | P2 | `01:60-71,73` | 判据①对表仍 10 行；裸值禁令未覆盖尺寸/描边/字号。 | 补齐对表；禁令扩为「任何视觉数值」。 |
| R5-P2-08 | P2 | `01:41-42,72-73` | 材质深/浅两套值无浅色视觉主题落点（C-02 V-07 仅注册 `builtin.fluent-dark`）。 | 声明暂不落库或登记裁决项。 |
| R5-P2-09 | P2 | `README:5`；`selfcheck:26`；`05:73`；`07:74`；`08:39`；`06:59`；`04:5`；`01:17` | 引用错误：C-05（页可见性谓词）被当四页结构依据；`06:59` 引 C-03（应为 C-08/R-22）；`07:74`「FEA-01 冻结字段」；`08:39` `Skeleton/Status.cs` 当 InfoBar；`01:17` 令牌生成归 FEA-05。 | 逐项改正引用。 |
| R5-P2-10 | P2 | `10:4,19,51-53` | 组件清单未列 `StatusBadge/Chip/Kbd`（`Badges.cs`）与 `FocusRing`；`Skeleton.cs` 当令牌；新组件归属未按 V-06 说明。 | 清单补既有组件与归属列。 |
| R5-P2-11 | P2 | `04:30,36`；`ShellLayout.cs:17-19` | 04 定义 `Narrow <1024`，Current `IsNarrow` 用 `<1280`；Fluent 复用 Current 判定会不同。 | 04 说明差异或对齐代码。 |
| R5-P2-12 | P2 | `05:21` vs `03:44` | 03:44「左导航（空间列表）」与 05:21 左导航项（书架/回收站/导入）不一致。 | 统一措辞。 |
| R5-P2-13 | P2 | `08:3` | 「其余分组沿用既有设置 surface」——V11R `ShellSurface` 无 Settings/既有设置 surface，表述含糊。 | 写死宿主或登记 DSH 裁决。 |
| R5-P2-14 | P2 | `01:17`；方案 `:645`；`selfcheck:30-36` | 四页预览（FEA-06 AC）无规格；`01:17` FEA-05 职责未改。 | 补 G-1 条目或登记后续任务。 |
| R5-P2-15 | P2 | `FEA-04b.md:17` | `delivery_head` 仍 `null`（收口前状态）。 | 收口时填最终 head。 |
| R5-P2-16 | P2 | `FEA-04b.md:109-111`；`selfcheck:15` | 收口记录滞后：Closeout 仍写「待 r4 复核」，未记 r4/r5；selfcheck AC5 行仍「独立 Review r1–r4 已走」（r5 后应更新为 r1–r5）。 | 收口时补记 r5、更新 AC5 行。 |

## 4. 逐项核查（对应派发 4 点）

### 4.1 R4-P1-01 列宽令牌错配——**通过**

- `06:37` 已恢复 96 并标注「设计常量，FEA-05 登记/DSH 裁决，见 01 G-1b」；`01:22` G-1b 增补登记与理由（无列宽令牌、TreeWidth 200 过宽）。语义错配与可用性问题解除；设计常量已按规定登记（符合 01 G-1b「额外尺寸须先登记并由 DSH 裁决」）。✓

### 4.2 R4-P2-16 selfcheck 未同步——**通过**

- 断点口径：`selfcheck:11`「Narrow/Medium/Compact/Full 见 04 §2」✓；`§2` 上游一致性行更新（V-03/V-05 缺键登记、V-08b 17 条、C-03 §2.3/§2.2）✓；`§3` 补 G-1b/G-1c ✓；`§4` 记 r1–r4 处置 ✓；错字与控制字符清除 ✓。

### 4.3 R4-P2-17 证据表——**哈希通过；commit 元数据待收口**

- 12/12 sha256 复算一致（含 selfcheck `3471b1ac…`）✓；commit 列 `f224280df` 与本次内容（`d4da1f1cb`）不配对——DSH 已声明收口时统一，列入 R5-P2-02（非阻断）。

### 4.4 是否仍有 P0/P1 / 新问题

- **P0 = 0 / P1 = 0**；未引入新问题（diff 仅 01/06 各 1 行 + selfcheck + 证据表/Closeout；未触碰冻结契约/代码/枚举；`check.ps1`/`verify_pins.ps1` PASS）。
- 新发现仅收口记录滞后（R5-P2-16）与 commit 元数据（R5-P2-02），均为 P2。

## 5. 批准与边界声明

- **批准范围**：设计基线文档 `doc/design/fluent-v1/`（README + 01–10，版本 `fluent-v1.0.0`）对 **AC1–AC4** 的覆盖，reviewed_head `d4da1f1cb`。依据：P0=0、P1=0；AC1–AC4 的规格/令牌/动效/键盘 a11y 均已通过逐项核对（见 §1–§4）。
- **不在本报告范围**：**AC5（用户确认）**——`FEA-04b.md:65` 仍 `[ ]`/PARTIAL，用户确认与 DSH 冻结由 Lead 处理，本 approved 不替代 AC5。
- **未验证项**：高对比实际渲染与对比度（需实现后验证）；`Nm.Material.*`/`Nm.Elevation.*`/`Nm.Corner.Fluent.*`/`Nm.Focus.Ring.*` 生成后的资源加载（代码尚不存在）；FEA-05/06 实现可行性为设计层推断。
- **收口前建议**（不阻断批准）：按 §3 清单清理 P2（优先 R5-P2-02 commit 元数据、R5-P2-04 字段全名、R5-P2-09 引用错误、R5-P2-15/16 收口记录），重算证据表哈希并重跑 `check.ps1`/`verify_pins.ps1`；AC5 由用户确认后由 DSH 冻结。
