---
document_id: FEA-GOV-4-c02-review
kind: independent_review
task_id: FEA-GOV-4
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-15（独立上下文；未参与 C-02 草案撰写，未参与 V11R 合同 / FEA-00 方案 / C-01b / C-03 / C-11 撰写）"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: 0c491d0db
reviewed_head_full: 0c491d0db5cc945a59d97a0630327ff3006cc179
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 0c491d0db）"
reviewed_document: doc/plan/FEA-C02_V11R_AMENDMENT_DRAFT.md
reviewed_sha256: 28e1d8aef18c837900363010a3fadc3f12d52fc35ae6f772d100ce3454341259
reviewed_sha256_basis: "HEAD 的 LF blob（130 行）；与 0c491d0db 相同（blob 7ed46603b）"
baseline: "doc/plan/V11R_AVALONIA_CONTRACT.md（FROZEN v1，§1.1–§6.3）· doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md（r4 @ 74a772167，r8 approved）"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 4
p2_count: 6
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T03:47:30+08:00
captured_by: c01b-reviewer
---

# 独立复核：FEA-C02 V11R 契约条款级修订单（草案）

**本报告不是** 冻结动作、不是对 V11R 冻结合同的修改，也不构成执行授权。本轮逐条核对 V-01…V-08 对 V11R 合同「现行文本」的概括是否准确、修订是否与 FEA-00 方案 r4 一致、是否只做「适用域限定 + 例外登记」、以及数据安全与 `check.ps1`。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 4** / P2 × 6）。**

修订单的**结构与骨架是对的**（V-01…V-08 覆盖 §1.1/§1.2/§2.2/§2.3/§2.4/§3/§4/§6.1/§6.3 九处，与 FEA-01 C-02 行和方案 §15.2 九行一致；统一格式「现行文本 → 修订/适用域 → 审查判据 → 例外登记」可审查；R-03 Fluent 定位、`nm.fluent.visual/1` 归属、U-04 落点、§2.4「新增例外须本节登记」的机制都立住了）。但存在 **4 条 P1**（其中 3 条是「与基准文档不一致」，1 条是「令牌契约缺口」），需修订后才能作为冻结候选：

| # | P1 | 一句话 |
|---|---|---|
| P1-1 | V-01 判据「不得新增 `NewManga.*.csproj`」 | 与方案 §15.2 §1.1 行（明确允许新增经批准的 `Frontends.Fluent`、Application/Presentation 项目）及 §15.6 FEA-06 写域直接冲突；§5 又称「方案 §15.2 改为引用本文件」，会把这两项项目授权**吞掉** |
| P1-2 | `builtin.fluent` / `builtin.current-v2` 被当作**主题包 id** | 方案里它们是**界面（frontend）id**（`newmanga.frontend/1`，`:284-286`；`perFrontend` 映射 `:315-318`）；代码里现有内置视觉主题是 `newmanga-default`（`BuiltInThemes.cs:15`），Fluent 的视觉主题按方案是 `builtin.fluent-dark`。四条款（V-01/V-03/V-05/V-07）的归属判据都建立在这个混淆上 |
| P1-3 | V-08 对 §6.1/§6.3 的「现行文本」概括错误，且漏 §6.3 修订 | §6.1 = 空间/模式（`SpaceId`/`StudioMode`/`ShellSurface`/`ShellState`/`AppShellV2`）；§6.3 = **快捷键**（`Shell/V2/KeyMap.cs` 单一注册表），不是「Shell/导航结构」；方案 §15.2 §6.3 行要求的「按 scheme/窗口/焦点上下文路由」修订在 V-08 中缺失 |
| P1-4 | V-05 使用 `Nm.Corner.Sm(4)/Md(6)/Lg(8)` | V11R §2.2 冻结的圆角组是 `Nm.Corner.None/Sm(2)/Md(3)`（**无 `Lg`**），V-03 只新增材质/层次/焦点三组、**未登记圆角组扩展** → 例外条款依赖不存在的令牌键 |

6 条 P2 为计数/引用/边界精度问题（见 §3），均可在同一次修订中处理。

| 审查项 | 判定 |
|---|---|
| 1. 逐条准确性 | **不通过** —— V-01（P1-1）、V-05（P1-4）、V-07（P1-2）、V-08（P1-3）四处有问题；V-02/V-03/V-04/V-06 的现行文本概括与 V11R 基本一致（计数除外） |
| 2. Fluent 定位（R-03） | **通过**（§3 明确「Fluent = 视觉风格，不是 FluentAvalonia 依赖」）；建议补 SukiUI（P2-3） |
| 3. `nm.fluent.visual/1` 归属 | **通过**（§4：ThemeEngine 项目内校验器，构建期 + 单测，不进 `check.ps1`；与方案 `:1032` 的 validator 归属方向一致）；建议注明与 FEA-01/FEA-05 的分工（P2） |
| 4. U-04 落点 | **通过**（V-05 两行、per-scheme、令牌强制、current 禁用；与 R-14「新增例外须登记」机制相容）；数值时序建议说明（P2-5） |
| 5. 三处口径统一（R7-08） | **部分** —— 三行都有，但「V11R §4.1」应为 §4（P2-2）；且「以本修订单为准」与 P1-1 的项目授权冲突 |
| 6. 无新增语义 | **部分** —— V-02 新增固定 Owner、V-03 新增三组键、V-05 圆角取值超出 §2.2，均超出「仅适用域限定 + 例外登记」，需显式标注为「Fluent 专属、不改变全局义务」（P1-4/P2-4/P2-6） |
| 7. 数据安全 + `check.ps1` | **通过** —— 本轮提交只改 `doc/**`，无 `src/**`/`apps/**`、无用户数据；未 push；`check.ps1` PASS(3 warnings) EXIT=0 |

---

## 2. 逐条核对（V-01…V-08）

### V-01 §1.1 项目 —— ⚠️ P1-1

- 现行文本：「三个项目（DesignSystem / ThemeEngine / App），单向引用 `App → ThemeEngine → DesignSystem`」✓ 与 V11R `:15-23` 一致（省略「旧主题/测试」两行属合理摘要）。
- **修订/判据问题**：写「**不新增项目**」并以「`git diff --stat` **不得新增 `NewManga.*.csproj`**」为判据 —— 与方案 §15.2 的 §1.1 行冲突：该行明确「Current 路径保持；**增经批准的 `Frontends.Fluent`、Application/Presentation 项目与单向依赖图**；UI 不直连 Core 存储」，验收为「build 与依赖图无环；**新增项目路径须列 Task 写域**」（方案 `:844`）。方案 §15.6 FEA-06 写域即 `apps/desktop-avalonia/src/NewManga.Frontends.Fluent/`、FEA-07 为 `NewManga.Presentation.Avalonia/`（方案 `:927-928`）。→ 见 P1-1。

### V-02 §1.2 共享写权 —— ✅（2 处 P2）

- 现行文本与 V11R `:27-33` 一致 ✓（组合根 `design-platform`（M0 后仅 DSH）；`Views/V2`/`ViewModels/V2`/`Shell/V2` 归 ui-shell + ui-studio）。
- 修订新增 `theme-fluent`（建议 ZCode）写 Fluent 主题包资源 —— 与方案 §15.2 §1.2 行「其他写域**逐 Task 明确由 DSH 指派**，FEA-04 保持现有写权直至重新指派」的口径不完全一致（P2-4）；路径写作 `src/NewManga.ThemeEngine/Themes/Fluent/**`，而 V11R §1.1 的完整路径是 `apps/desktop-avalonia/src/NewManga.ThemeEngine/…`，仓库根另有 Python `src/`，易误读（P2-4）。
- 事实核对：`apps/desktop-avalonia/src/NewManga.ThemeEngine/Themes/` 确实存在（含 `BuiltInThemes.cs`、`newmanga-default.nmtheme`）✓，「落在既有主题目录结构内」成立 ✓。

### V-03 §2.2 令牌组 —— ⚠️ 计数错 + 新增键性质（P2-1/P2-6，圆角缺口见 P1-4）

- 现行文本「V1 最低集 14 组」：V11R §2.2 `:48-64` 实为 **15 行**（背景、描边、文本、强调、状态、状态底、字体族、字号、字重/行高、间距、圆角、尺寸、内边距、动效、图标）→ 计数错（P2-1）。
- 修订新增材质/层次/焦点三组 ✓ 方向合理；「适用域限定（仅 `builtin.fluent` 必须存在；`current-v2` 可缺省）」可审查 ✓。但这属于**新增键集合**而非纯适用域限定 → 建议在条款内显式写「Fluent 专属最小集，不改变 V1 最低集的全局义务」（P2-6）；且其归属 id 受 P1-2 影响。
- **圆角缺口**：V-05 要用 `Nm.Corner.Sm(4)/Md(6)/Lg(8)`，而 §2.2 的圆角组只有 `None/Sm(2)/Md(3)` → 见 P1-4。

### V-04 §2.3 状态令牌 —— ✅

- 现行文本与 V11R `:71-72` 一致（色相 + 符号 + 文字标签；`StatusGlyph` 提供符号；UI 不得自造）✓；修订「保持不变、仅色相可由主题包不同」与方案 §15.2 §2.3 行（「所有 scheme 继承状态语义及文字/符号」）一致 ✓。

### V-05 §2.4 例外登记（U-04 落点）—— ✅ 机制正确，⚠️ 令牌缺键（P1-4）

- 现行文本 7 项与 V11R `:82-88` **逐项一致** ✓（`0/1/Auto`、`Transparent`、`Margin=-2`、高对比令牌、密度令牌、语义行高别名、muted 底色）；「唯一允许例外 + 任何新增例外须在本节登记」与 `:78,:90` 一致 ✓。
- 两行新增（材质与层次 / Fluent 圆角）为 **per-scheme 限定 + 令牌强制 + current-v2 禁用**，符合方案 §15.2 §2.2 行（「Fluent 默认圆角≤3 DIP；超过该值或使用材质、阴影/模糊须先经 DSH 逐项登记例外」）与 §2.4 行（「附加按 scheme、token、范围登记的例外表；原例外不泛化」）✓ 机制与 R-14 不冲突。
- 问题：第一行「取值必须来自 V-03 的 `Nm.Material.*`/`Nm.Elevation.*`」✓ 自洽；第二行「允许 `Nm.Corner.Sm(4)/Md(6)/Lg(8)` 三档」**与 §2.2 冻结键集不符** → P1-4。
- U-04 数值时序：方案 `:1032` 说「实际例外与**数值**由 FEA-04b 用户确认并经 DSH 正式登记」，本单把 4/6/8 写死并请用户裁决 → 建议注明「数值以 FEA-04b 用户确认为准，本单只冻结例外机制」（P2-5）。

### V-06 §3 Design System 公开面 —— ✅

- 现行文本与 V11R `:93-113` 一致（§3.1 内置控件 + Classes；§3.2 自定义控件清单 + 分阶段上收规则「`Views/V2/<Area>/Controls/**` 本地实现，≥2 工作面使用后上收 DS」）✓；「不新增控件、Fluent 用主题包 + 既有控件模板变体」与方案 §15.2 §3 行（「保留跨界面语义基础与 Current 控件；Fluent 独立模板通过版本化组件/slot 合约对接」）方向一致 ✓。
- 计数精度：§3.2 清单实为 **40 个名称**（`StatusGlyph`…`TaskPanel`），写「40+」略高（P2-1 同条）。

### V-07 §4 Theme Engine 公开面 —— ⚠️ P1-2

- 现行文本「`ThemeKind { BuiltIn, User }`；公开面冻结（enum/接口签名）」✓ 与 V11R `:117-160` 一致。
- 修订「`builtin.fluent` 作为 `ThemeKind.BuiltIn` 的第二个内置主题包，主题包 id 为 `builtin.fluent`，与 `builtin.current-v2` 并列」—— **id 命名空间混淆**：方案 `:284-286` 的 `newmanga.frontend/1` manifest 里 `id: builtin.fluent` 是**界面 id**；`:315-318` 的 `perFrontend` 把 `builtin.current-v2` 映射到 `visualThemeId: newmanga-default`（代码 `BuiltInThemes.cs:15` 的内置主题即 `newmanga-default`），Fluent 的视觉主题按 `:302` 是 `builtin.fluent-dark` → P1-2。
- 判据「`ThemeKind` 枚举值与公开方法签名不得变化；主题包注册表新增条目」在 id 澄清后可执行 ✓。

### V-08 §6.1 / §6.3 —— ⚠️ P1-3

- 现行文本「新 UI 代码落在 `Views/V2/**`、`ViewModels/V2/**`、`Shell/V2/**`；§6.3 为 Shell/导航结构」：
  - 前半是 **§1.1 的 App 行**（V11R `:19`）内容，不是 §6.1；§6.1 实为「空间与模式」（`SpaceId`/`StudioMode`/`ShellSurface`、唯一状态源 `ShellState`、`IWorkspaceView`、`AppShellV2` 唯一窗口内容，`:245-265`）；
  - 后半错：§6.3 是「快捷键」（`Ctrl+1/2/3`、`Ctrl+K`… + `Shell/V2/KeyMap.cs` 单一注册表，`:274-277`）；Shell/导航结构在 §6.1（空间/表面）与 §6.2（Theme Studio 表面）。
- 且方案 §15.2 §6.3 行要求「**进程级单一注册表按 scheme/窗口/输入焦点上下文路由**；冲突启动拒绝/提示」，V-08 未提出任何 §6.3 修订 → 覆盖缺口（P1-3）。
- 修订内容（不新建 `Views/V2-Fluent/**`、用 `Classes` + 主题包资源、不复制页面类）本身合理 ✓。

---

## 3. Findings

### P1

#### P1-1 — V-01 的「不新增项目」判据与方案 §15.2 §1.1 行、§15.6 FEA-06/FEA-07 写域冲突；§5「方案 §15.2 改为引用本文件」会吞掉项目授权

- 位置：C-02 `:33-34`（V-01 修订与判据）、`:115`（§5 第 2 行）。
- 证据：方案 `:844`（§15.2 §1.1 行）：「Current 路径保持；**增经批准的 `Frontends.Fluent`、Application/Presentation 项目与单向依赖图**；UI 不直连 Core 存储 | build 与依赖图无环；**新增项目路径须列 Task 写域**」；方案 `:927`（§15.6 FEA-06 写域）：`apps/desktop-avalonia/src/NewManga.Frontends.Fluent/`；`:928`（FEA-07）：`apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/`。
- 影响：若 C-02 以「不得新增 `NewManga.*.csproj`」冻结，且 §5 声明「方案 §15.2 改为引用本文件」，则 FEA-02/FEA-06/FEA-07 计划中的新项目将**失去授权依据**（或使 FEA-06 的实现必然违反 C-02）。这是「无新增语义」检查中唯一会**减少**既有方案授权的地方，风险高于其他条目。
- 建议：V-01 限定范围：「**主题包工作不新增项目**（Fluent 为 ThemeEngine 内主题包）；**前端/应用内核项目由 FEA-02/FEA-06/FEA-07 各自契约批准，可新增**（方案 §15.2 §1.1、§15.6 写域为准）」，判据改为「C-02/C-03 相关 diff 不得新增 csproj；新增项目须在对应 Task 写域内并经 DSH 批准」。

#### P1-2 — 把「界面 id」（`builtin.current-v2` / `builtin.fluent`）当作「主题包 id」，四条款归属判据失效

- 位置：C-02 `:33`（V-01）、`:53`（V-03 适用域）、`:67-71`（V-05 例外行）、`:86`（V-07）。
- 证据（方案）：`:275-279` 三层注册——**FrontendRegistry（界面）/ ThemeRegistry（视觉主题）/ ScaleRegistry（比例）**；`:284-286` `newmanga.frontend/1` manifest `"id": "builtin.fluent"` → **界面 id**；`:299` `"visualTokenSchemas": ["nm.fluent.visual/1"]`（视觉主题 schema）；`:302` `"defaultVisualTheme": "builtin.fluent-dark"`；`:315-318` `perFrontend` 把 `builtin.current-v2` 映射到 `visualThemeId: newmanga-default`。
- 证据（代码）：`apps/desktop-avalonia/src/NewManga.ThemeEngine/Themes/BuiltInThemes.cs:15` 内置主题资源为 `newmanga-default.nmtheme`；`ThemeRegistry.cs:118` 按 `Descriptor.Id` 注册内置主题 → 现有内置**视觉主题** id 是 `newmanga-default`，仓库中**不存在** id 为 `builtin.current-v2` 的内置主题包。
- 影响：V-05 的「例外仅限 `builtin.fluent`、`current-v2` 禁用」如果以界面 id 为键，校验器无法在 ThemeEngine 侧判定（ThemeEngine 管视觉主题，不管界面）；V-07 的「第二个内置主题包 id = builtin.fluent」也会与 `nm.fluent.visual/1` 的 visual theme 命名不一致。
- 建议：在 V-01 或 §4 显式写清两套 ID：
  - 界面 id：`builtin.current-v2`（现状，映射视觉主题 `newmanga-default`）/ `builtin.fluent`（新增界面，方案 §6.1）；
  - 视觉主题包 id：`newmanga-default`（现状）/ `builtin.fluent-dark`、`builtin.fluent-light`（方案 `:302`）等；
  并在 V-03/V-05/V-07 中，凡指「主题包」处一律用视觉主题 id；「per-scheme 例外」用「界面/scheme = `builtin.fluent`」表述。**同时须与 C-03 对齐**（C-03 目前沿用同一套混淆词汇）。

#### P1-3 — V-08 的 §6.1/§6.3「现行文本」概括错误，且缺失方案要求的 §6.3 KeyMap 修订

- 位置：C-02 `:90-95`（V-08）。
- 证据：V11R `:245-265` §6.1 = 空间与模式（`SpaceId { Library, Studio, Console }`、`StudioMode { Page, Batch }`、`ShellSurface { Spaces, ThemeStudio, ReaderOverlay }`、`ShellState` 唯一状态源、`IWorkspaceView`、`AppShellV2` 唯一窗口内容）；`:274-277` §6.3 = 快捷键（`Ctrl+1/2/3`、`Tab`、`Ctrl+K/P/E/,`、`F1`、`F5`… + `Shell/V2/KeyMap.cs` 单一注册表，`ui-shell` 所有，冲突启动断言失败）。方案 `:852`（§15.2 §6.3 行）：「全局 KeyMap 单一注册 → **进程级单一注册表按 scheme/窗口/输入焦点上下文路由**；方案只申明 bindings｜冲突启动拒绝/提示；文本输入优先；窗口切换一次命令仅执行一次」。
- 影响：修订单的「现行文本」是被冻结条款的引用基础；概括错误会让审查者与实现者按错条款执行，且 §6.3 的实质修订要求（多 scheme/窗口/焦点路由）完全缺失 —— 这正是 Fluent 双界面场景必须解决的键位冲突点。
- 建议：V-08 拆成 V-08a（§6.1：现行文本按 `SpaceId/ShellState/AppShellV2` 概括；修订：不新建 `Views/V2-Fluent/**`、用 `Classes` + 主题包资源）与 V-08b（§6.3：现行文本 = 单一 `KeyMap.cs` 注册表 + 冲突断言；修订按方案 `:852` 写「按 scheme/窗口/输入焦点上下文路由 + 冲突拒绝/提示 + 文本输入优先」）。

#### P1-4 — V-05 依赖的 `Nm.Corner.Sm(4)/Md(6)/Lg(8)` 在 V11R §2.2 不存在，V-03 未登记圆角组扩展

- 位置：C-02 `:71`（V-05 第二行例外）↔ `:47-55`（V-03 只新增材质/层次/焦点）。
- 证据：V11R `:60`：`| 圆角 | Nm.Corner.None/Sm(2)/Md(3) | CornerRadius |` —— 键集含 `None/Sm/Md`，**无 `Lg`**，且 `Sm=2 / Md=3`；`§2.2 :66` 硬规则禁 `border-radius > 3px`。
- 影响：V-05 允许 Fluent 用 4/6/8 档圆角，但令牌契约没有 `Lg` 键、`Sm/Md` 的名义值是 2/3。若实现按 V-05 写 `{DynamicResource Nm.Corner.Lg}`，会命中未定义键；若改 §2.2 的键值集，则属**修改冻结条款**而 V-03 未登记 → 修订单内部不自洽，validator 也无法按 V-03 判据检查（V-03 判据只覆盖三组新键）。
- 建议：V-03 增加第四组「圆角（Fluent 扩展）」：新增 `Nm.Corner.Lg(8)`，并声明「`builtin.fluent` 下 `Sm/Md/Lg` 取 4/6/8；`current-v2` 保持 `None/Sm(2)/Md(3)`」；V-05 例外行改为引用该组键，并在审查判据中要求「Fluent 圆角必须来自 `Nm.Corner.*`，current-v2 保持 ≤3px 且无 `Lg` 使用」。

### P2

#### P2-1 — 两处计数精度：§2.2 实为 15 组（写 14）、§3.2 实为 40 个名称（写 40+）

- 位置：C-02 `:46`、`:78`。
- 证据：V11R `:48-64` 共 15 个令牌组数据行；`:110` 控件清单共 40 个名称（含 `FilmStrip`/`FilmItem` 分别计）。
- 建议：改为「15 组」「40 个」或「约 40 个」。

#### P2-2 — §5 表引用「V11R §4.1」不存在

- 位置：C-02 `:114`。
- 证据：V11R 章节为 `## 4. Theme Engine 公开面（冻结）`（`:117`），无 `§4.1` 子节。
- 建议：改为「V11R §4」。

#### P2-3 — §3 Fluent 定位漏 SukiUI

- 位置：C-02 `:99-102`。
- 证据：方案 `:856`：R-03 明确「**不引入 FluentAvalonia 或 SukiUI 依赖**」；本单只写 FluentAvalonia。
- 建议：改为「禁止引入 `FluentAvaloniaUI` / `SukiUI`」。

#### P2-4 — V-02 的 `theme-fluent` 固定 Owner 与方案「逐 Task 由 DSH 指派」不一致；路径前缀缺 `apps/desktop-avalonia/`

- 位置：C-02 `:40`。
- 证据：方案 `:845`（§15.2 §1.2 行）：「保留 DSH 组合根独占；**其他写域逐 Task 明确由 DSH 指派**」；V11R `:18` 的完整项目路径为 `apps/desktop-avalonia/src/NewManga.ThemeEngine/…`，而仓库根另有 Python `src/`。
- 建议：改为「由 DSH 在 Fluent 主题包 Task 中指派（建议 ZCode）」，路径写全 `apps/desktop-avalonia/src/NewManga.ThemeEngine/Themes/Fluent/**`。

#### P2-5 — U-04 的圆角数值（4/6/8）与方案「数值由 FEA-04b 用户确认」的时序未说明

- 位置：C-02 `:74`（U-04 待裁决）。
- 证据：方案 `:1032`：「`nm.fluent.visual/1` 是版本化数据 schema 草案，Owner 建议为 DSH 指定的 design-platform，FEA-01 负责契约与 validator，FEA-05 负责实现；**实际例外与数值由 FEA-04b 用户确认并经 DSH 正式登记**」。
- 建议：U-04 注明「本单冻结**例外机制与范围**；具体数值（4/6/8）以 FEA-04b 用户确认为准并登记」。

#### P2-6 — V-03 新增三组属「新增键集合」，建议显式标注为 Fluent 专属、不改变全局义务

- 位置：C-02 `:47-55`。
- 建议：条款内加一句「本三组为 `builtin.fluent` 视觉主题专属最小集，**不进入** V1 最低集全局义务；`current-v2` 缺省合规」，并同步到 §5「统一后」的表述，避免与「以本修订单为准」产生范围扩张误读。

---

## 4. 数据安全与治理检查

- 本轮提交（`0c491d0db`：`REBASELINE_PLAN` / `STATUS` / `TASK_LEDGER` / `FEA-GOV-3` 卡 / `FEA-GOV-4` 卡）与 C-02 草案所在提交均**未触碰 `src/**`、`apps/**`**（`git diff --stat` 自 `96265d879` 起为空）✓，无用户数据。
- **未 push**：`0c491d0db` 不是 `origin/main` 祖先 ✓。
- **`check.ps1` 实跑**：`Governance check: PASS (3 warnings)`，EXIT=0（3 条 warning 为既有：7 个非终态 Task、`STATUS.md` 2883 B / 80%、`REBASELINE_PLAN.md` 6547 B / 80%）；运行后 `git status` 为空 ✓。
- 被审文件：`doc/plan/FEA-C02_V11R_AMENDMENT_DRAFT.md` @ `0c491d0db`，LF blob SHA-256 `28e1d8aef18c…3454341259`（130 行），与 HEAD 相同 ✓。

---

## 5. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**，`task-15`）身份出具本报告，`reviewer_kind: subagent`，独立上下文。
- **未参与** C-02 草案撰写（作者 = DSH）、未参与 V11R 合同 / FEA-00 方案 / C-01b / C-03 / C-11 撰写，未参与 `src/**`、`apps/**` 任何实现。
- **利益披露**：我出具过 C-01b r1–r5、FEA-GOV-1（AD-003）、FEA-GOV-2、FEA-GOV-3 复核；本轮对 V11R 合同与方案 r4 的引用均**直接读取原文**（未引用我此前报告），并对 `BuiltInThemes.cs` / `ThemeRegistry.cs` 与方案三层 schema 做了代码↔文档交叉核对。若认为该重叠影响独立性，可另指派未参与上述各线的上下文复核本报告。
- 本轮**只读**：唯一写入为新建本报告；未修改 C-02 / V11R / 方案 / Task 卡 / 状态表；未 `git add`/`commit`/`push`；未触碰真实数据根。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == 0c491d0db`；被审文件 blob `7ed46603b`。

---

## 6. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建（纯文档治理 Task）。
- 未执行任何冻结或合同修订动作（本稿为 DRAFT，冻结须独立复核 + 用户裁决 U-04 + DSH 执行）。
- 未审计 V11R 合同全文其余条款（§5 服务层、§7 构建与证据、§8 变更记录未在本单覆盖范围）。
- 未复核 C-03/C-11 草案（另由 FEA-GOV-4 的其它 Review 承担）；仅指出 C-03 与本单共享同一 id 混淆词汇（P1-2）。
- 未验证 `nm.fluent.visual/1` 的实际 schema 文件与校验器实现（当前仓库无该 schema 文件，属计划态）。
- 未核远端历史细节（仅核本地 main 未 push）。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×4 / P2×6）。
