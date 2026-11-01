# FEA-04b 范围复核 r4（同一独立席位，续任）

| 字段 | 值 |
|---|---|
| base_commit | `f08c6648b` |
| reviewed_head | `f224280df`（main，clean；r3 处置提交） |
| 上一轮 | `doc/reviews/FEA-04b-scope-r3.md`（reviewed_head `f08c6648b`） |
| reviewer | `fea04b-scope-reviewer` |
| reviewer 来源 | DSH Team Lead 派发，fresh 独立上下文；**r1–r3 同一席位续任**；未参与 FEA-04b 起草；只读被审 head |
| 日期 | 2026-11-02 |
| 审查范围 | AC1–AC4（设计基线）。**AC5（用户确认）不在本报告范围** |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 1 / P2 = 17** |

> 说明：r3 的唯一 P1（`06:24` Compact 断点 + 图内 240 裸值）已修复；但 r3 P2-01 的处置在 `06:37` 引入一个新的实质错误——矩阵列宽改为行高令牌 `Nm.Size.RowNormal`（26），语义错配且 26px 列宽不可用。因仍有 P1=1，**不写 approved**。

## 0. 方法、只读声明与复现

- 只读核查被审 head；**未修改任何被审文件**，未 commit、未 push；本报告是本轮唯一新增文件。
- 复现（本次实跑）：
  - `git rev-parse HEAD` → `f224280df72159199f7d8d7bdce1c006364b3546`；`git status --porcelain` → 空。
  - `git diff --name-status f08c6648b..f224280df` → `doc/design/fluent-v1/05,06,07,08`、`doc/reviews/FEA-04b-scope-r3.md`（已在提交中）、`doc/tasks/FEA-04b.md`、`verification/FEA-04b/design-baseline-selfcheck.md`；**未触碰 `doc/plan/**` 冻结契约、`apps/**`、`src/**`**。
  - `pwsh -NoProfile -File tools/governance/check.ps1` → `PASS (2 warnings)`。
  - `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → `PASS (all 15)`。
  - 证据表 **12/12 sha256 复算一致**（README/01–10/selfcheck 全部与当前文件一致）。
  - selfcheck 字节扫描：**含 1 个 ESC 控制字符（0x1B@line61）**；另有错字（`rreduce`/`Aappearance`/`ull`/`173d156d`），见 R4-P2-03。

## 1. r3 逐项 disposition（P1×1 + P2×15）

### 1.1 r3 P1

| r3 finding | r4 结论 | 证据 |
|---|---|---|
| **R3-P1-01** `06:24` Compact 抽屉矛盾 + 图内 72/240 裸值 | **已关闭**：`06:24` 两处改为「`Narrow（<1024）`」；`05:15`/`06:15`/`08:14` 图中裸值改为 `Nm.Size.TreeWidth`（200），与 `04:30-33`、`05:61`、`06:65-67`、`08:86` 一致 | `06:24`；`05:15`；`06:15`；`08:14` |

### 1.2 r3 P2

| r3 P2 | r4 状态 |
|---|---|
| R3-P2-01（`06:37` 96 / `07:12,18` 40/36 裸值） | **部分关闭**：`07:12/18` 改为 `Nm.Size.ControlHeight`（28）；**`06:37` 改为 `Nm.Size.RowNormal`（26）——行高令牌当列宽，语义错配且 26px 列宽不可用 → R4-P1-01**；`07` 条高用 `ControlHeight`（控件高度）语义不精确（P2） |
| R3-P2-02（selfcheck 记录/Closeout/`delivery_head`） | **部分关闭**：selfcheck 新增 §6 记 r2/r3 处置 ✓；FEA-04b Closeout 增记 r1–r3 ✓；`delivery_head` 仍 `null`（设计 Task 收口前可接受，收口时填最终 head） |
| R3-P2-03（selfcheck 丢字） | **未关闭且回退**：`selfcheck:52` 已修回 `export.run`/`reduce`/`appearance`/`followSystemAccent` ✓，但 `full` 仍为 `ull`（`:53`）；**新写入 §6 又引入 ESC 控制字符（`0x1B@:61`）与错字 `rreduce`（`:13,:24`）、`AappearanceCoordinator`（`:25`）、`173d156d`（`:61`，丢 `e`）** → R4-P2-03 |
| R3-P2-04（02 auto 列/曲线/映射/Scrim/自动隐藏） | 未关闭（02 未改） |
| R3-P2-05（08 字段全名 + `03:62` 旧名） | 未关闭（08/03 未改） |
| R3-P2-06（09 vs 06/07/08 正文 3 处） | 未关闭（09/06/07/08 正文未补） |
| R3-P2-07（层级 ZIndex/Elevation） | 未关闭（04/01/10 未改） |
| R3-P2-08（01 判据①对表/裸值禁令） | 未关闭（01 未改） |
| R3-P2-09（材质深浅两套值） | 未关闭（01 未改） |
| R3-P2-10（引用错误） | 未关闭（README/selfcheck/05/07/08/06/04/01 未改） |
| R3-P2-11（10 组件清单） | 未关闭（10 未改） |
| R3-P2-12（04 断点 vs `ShellLayout.IsNarrow`） | 未关闭（04 未改） |
| R3-P2-13（05:21 vs 03:44 左导航措辞） | 未关闭（03/05 未改） |
| R3-P2-14（08:3 其余分组 surface） | 未关闭（08:3 未改） |
| R3-P2-15（缺口登记：四页预览/01:17 职责） | 未关闭（01:17/方案 645 未改） |

## 2. 仍存在的 P1（1 条，含最小修法）

### R4-P1-01（r3 P2-01 处置引入）`06:37` 矩阵列宽改为行高令牌 `Nm.Size.RowNormal`（26）

- `06:37`：「矩阵表头 | 吸顶；列宽最小 `Nm.Size.RowNormal`（26），阶段名可换行」。
- 事实：`Nm.Size.RowNormal` = **26**，语义是「行高」（`Tokens.Global.axaml:73`；G-1b 亦列「RowDense 24 / RowNormal 26」为行高）；矩阵列宽原设计 96。改为 26 后：①令牌语义错配（行高不是列宽）；②26px 列宽对「阶段名可换行」的批量矩阵不可用（原 96px 才是设计意图），会误导 FEA-05/06 实现出不可用 UI。
- **最小修法**：恢复「列宽最小 96」，并在 `01:22` G-1b 增加一行「矩阵列宽 = 96（设计常量，FEA-05 登记并由 DSH 裁决）」；或改用合适既有令牌（当前 `Nm.Size.*` 无列宽令牌，`TreeWidth` 200 过宽，不建议）。同时 `07:12/18` 的条高建议用 `Nm.Size.TopBand`（36）/`Nm.Size.StatusBandPage`（28），而非控件高度 `ControlHeight`（语义更贴切；非阻断，P2）。

## 3. 新引入 / 新发现 P2（2 条）

| 编号 | 位置 | 问题 | 建议 |
|---|---|---|---|
| R4-P2-16 | `selfcheck:11,13,24,25,32-35` | 自查清单未随设计更新：`selfcheck:11` 仍写「断点 Compact/Medium/Expanded/Wide」（04 已是 Narrow/Medium/Compact/Full）；`:13,:24` 写 `rreduce`；`:25` 写 `AappearanceCoordinator`；`§3 已知缺口`（:32-35）只列 G-1…G-4，未登记 **G-1b/G-1c**（01 已新增）。 | 同步 §1/§2/§3 与 04/01 的最终口径；补 G-1b/G-1c 行。 |
| R4-P2-17 | `FEA-04b.md:88-99` | 证据表 commit 列统一 `f08c6648b`，但 12 项哈希均对应 `f224280df`（本次）的内容——commit 与 sha256 不配对（`f08c6648b` 是上一提交）。 | commit 列改 `f224280df`（或收口时的最终交付 head），并重算/复核哈希。 |

## 4. 逐项核查（对应派发 6 点）

### 4.1 R3-P1-01——**通过**

- `06:24`：「检查器在 `Narrow（<1024）` 断点变为抽屉；批量模式在 `Narrow` 下矩阵横向滚动 + 列固定首列」——与 `04:30`（Narrow 抽屉）、`06:65`（Narrow 抽屉）一致。✓
- `05:15`「`Nm.Size.TreeWidth`（200）」、`06:15`「`Nm.Size.TreeWidth`(200)」、`08:14`「`Nm.Size.TreeWidth`（200）」——与 `Tokens.Global.axaml:84`（TreeWidth 200）、`05:61`/`08:86` 一致。✓

### 4.2 R3-P2-01——**部分通过（R4-P1-01）**

- `07:12/18`：「高 `Nm.Size.ControlHeight`」——已去掉 40/36 裸值 ✓；但 `ControlHeight` 是控件高度（28），作「顶部/底部条高」语义不精确（原设计 40/36）；不阻断，P2。
- `06:37`：`Nm.Size.RowNormal`（26）当列宽 → **R4-P1-01**（语义错配 + 26px 不可用）。

### 4.3 R3-P2-02——**部分通过**

- selfcheck §6 已补 r2/r3 处置（`:57-61`）；`FEA-04b.md:109` Closeout 增记 r1/r2/r3。✓
- `delivery_head` 仍 `null`（`FEA-04b.md:17`）：设计 Task 收口前可接受，收口时必须填最终交付 head；`canonical_evidence_status`/`resource_closeout_status` 仍 `pending`（收口项）。
- 遗留：§6 文本本身损坏（ESC + 错字）→ R4-P2-03。

### 4.4 R3-P2-03——**未关闭（回退）**

- 已修复：`:52` `export.run`/`reduce`/`appearance`/`followSystemAccent` 均恢复正确。
- 仍损坏：`:53`「…在 `ull` 下也按 reduce 列」应为 `full`；`:13`/`:24` `rreduce` 应为 `reduce`；`:25` `AappearanceCoordinator` 应为 `AppearanceCoordinator`；`:61`「commit 统一 `173d156d`」应为 `e173d156d`；`:61` 含 **ESC 0x1B**（由 `\e` 转义写入）。
- 建议：用纯文本重写 §5/§6 该 4 行（不要经 `\e`/`\f` 转义），保存后重算 selfcheck 哈希并更新证据表。

### 4.5 证据表——**哈希通过，元数据待修**

- 12/12 sha256 与当前文件一致（含 selfcheck `f5b3508f…`）✓。
- commit 列 `f08c6648b` 与内容（`f224280df`）不配对 → R4-P2-17。

### 4.6 是否仍有 P0/P1 / 新问题

- P0：0；P1：1（R4-P1-01）。
- 新引入：R4-P1-01（`06:37`）、R4-P2-16（selfcheck §1/§3 未同步）、R4-P2-17（证据表 commit）。R4-P2-03 为未关闭项回退（新增 ESC）。
- 未引入契约/代码/枚举改动（diff 仅文档与证据）；`check.ps1`/`verify_pins.ps1` PASS。

## 5. Findings（r4）

| 编号 | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| R4-P1-01 | P1 | `06:37`；`Tokens.Global.axaml:73`；`01:22` | 矩阵列宽最小改为行高令牌 `Nm.Size.RowNormal`（26）：语义错配（行高≠列宽）+ 26px 列宽不可用（原设计 96）。 | 恢复 96 并在 G-1b 登记为设计常量（FEA-05 登记/DSH 裁决），或选合适令牌。 |
| R4-P2-01 | P2 | `07:12,18` | 阅读器顶/底条高用 `Nm.Size.ControlHeight`（控件高度 28），语义不精确（原 40/36）；建议 `TopBand`（36）/`StatusBandPage`（28）。 | 改令牌或说明用 ControlHeight 的理由。 |
| R4-P2-02 | P2 | `selfcheck §5/§6`（:52-61） | 文本损坏：`full`→`ull`（:53）、`rreduce`（:13,:24）、`AappearanceCoordinator`（:25）、`173d156d`（:61）、ESC 0x1B（:61）。 | 纯文本重写，补回/修正字母，重算哈希。 |
| R4-P2-03 | P2 | `selfcheck:11,13,24,25,32-35` | 自查清单未同步：旧断点命名（Compact/Medium/Expanded/Wide）；§3 未登记 G-1b/G-1c。 | 同步 §1/§2/§3。 |
| R4-P2-04 | P2 | `FEA-04b.md:88-99` | 证据表 commit 列 `f08c6648b`，哈希对应 `f224280df`；不配对。 | commit 改 `f224280df`/最终 head。 |
| R4-P2-05 | P2 | `02:37,47`；`02:28-31`；`02:65`；`02:30`；`07:23` | （r3 P2-04 未关闭）02 缺 `auto`（系统关）列、曲线命名、令牌映射、遮罩未引 `Nm.Color.Scrim`、自动隐藏未归类。 | 逐项补。 |
| R4-P2-06 | P2 | `08:47,48,53`；`03:62` | （r3 P2-05 未关闭）字段全名 `appearance`/`contrast`/`followSystemAccent` 缺前缀；`03:62` 旧名 `Appearance.Contrast`。 | 按 C-03 §2.2 补全。 |
| R4-P2-07 | P2 | `09:9,16`；`06:40-51`；`07:37-54`；`08:59-78` | （r3 P2-06 未关闭）09 与 06/07/08 正文 3 处不一致（工作台筛选空/运行中、阅读器运行中、设置搜索空态）。 | 补正文或删矩阵格。 |
| R4-P2-08 | P2 | `04:64,67`；`01:53`；`10:51` | （r3 P2-07 未关闭）层 2 与层 1 同 `ZIndex.Base`；Tooltip/CommandPalette Elevation 不统一。 | 改 `ZIndex.Panel`；统一 Elevation。 |
| R4-P2-09 | P2 | `01:60-71,73` | （r3 P2-08 未关闭）判据①对表 10 行；禁令未覆盖尺寸/描边/字号。 | 补齐。 |
| R4-P2-10 | P2 | `01:41-42,72-73` | （r3 P2-09 未关闭）材质深浅两套值无浅色视觉主题落点。 | 声明或登记裁决。 |
| R4-P2-11 | P2 | `README:5`；`selfcheck:26`；`05:73`；`07:74`；`08:39`；`06:59`；`04:5`；`01:17` | （r3 P2-10 未关闭）引用错误（C-05 误引、06:59 C-03、07:74 FEA-01、08:39 InfoBar、01:17 FEA-05 职责）。 | 逐项改正。 |
| R4-P2-12 | P2 | `10:4,19,51-53` | （r3 P2-11 未关闭）组件清单未列 Badges/FocusRing；`Skeleton.cs` 当令牌；新组件归属未说明。 | 补清单。 |
| R4-P2-13 | P2 | `04:30,36`；`ShellLayout.cs:17-19` | （r3 P2-12 未关闭）04 的 `Narrow <1024` 与 Current `IsNarrow <1280` 不一致。 | 说明差异或对齐。 |
| R4-P2-14 | P2 | `05:21` vs `03:44` | （r3 P2-13 未关闭）左导航描述不一致。 | 统一。 |
| R4-P2-15 | P2 | `08:3` | （r3 P2-14 未关闭）「其余分组沿用既有设置 surface」含糊。 | 写死宿主/裁决。 |
| R4-P2-16 | P2 | `01:17`；方案 `:645`；`selfcheck:30-36` | （r3 P2-15 未关闭）四页预览无规格、FEA-05 职责未改、G-1 未登记 G-1b/G-1c。 | 补 G-1 条目。 |
| R4-P2-17 | P2 | `FEA-04b.md:17` | `delivery_head` 仍 `null`（收口前状态，收口时必须填）。 | 收口时填最终 head。 |

## 6. 边界声明

- 本报告只审 **设计基线（AC1–AC4）**；**AC5（用户确认）不在本报告范围**（`FEA-04b.md:65` 仍 `[ ]`/PARTIAL）。
- 只读：未修改任何被审文件；被审 head `f224280df` 工作区 clean；未 commit/push。
- 未验证项：高对比实际渲染与对比度；`Nm.Material.*`/`Nm.Elevation.*`/`Nm.Corner.Fluent.*`/`Nm.Focus.Ring.*` 生成后资源加载（代码尚不存在）；FEA-05/06 实现可行性为设计层推断。
- 复核建议：R4-P1-01 + R4-P2-02/03/04（同批易修）处置后重跑 `check.ps1`/`verify_pins.ps1`、重算证据表哈希（commit 改最终 head）再提交 r5；其余 P2 可在收口前同批清理。若 DSH 认为 `06:37` 的 96 应保留为设计常量，请在 G-1b 登记后由复核确认，不必再逐轮返修。
