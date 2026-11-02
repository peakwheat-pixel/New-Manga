---
decision: A_catalog_notstarted_secondary
reviewer: Codex CLI (adjudication)
reviewer_kind: agent
date: 2026-11-03
context: D-14
task_id: FEA-06-RESIDUAL-2
base_commit: 669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431
reviewed_head: 195422c2fdf72f0460d2e265b53e22a2c5eff6fd
provenance:
  source: 用户本轮 D-14 只读裁决委托；rolling checkpoint §143
  implementation_participation: none_in_this_adjudication_session
  mode: read_only_except_this_report
---

# D-14：NotStarted 状态色裁决

## 1. 裁决

**选择 A：将 `StatusCatalog.ColorKey(StatusKind.NotStarted)` 改为 `NmKeys.Color.Text.Secondary`；保留 `Controls.Status.axaml` 中 glyph 与普通状态文字的 Secondary 映射。** 同步修正 `ColorKey` XML 注释，不新增颜色令牌、枚举值或 API 字段。

“未开始”是需要用户辨认的业务状态，不代表控件 `IsEnabled=false`。Secondary 在两套普通主题的全部六种不透明背景上均达到 4.5:1；Disabled 均未达到。catalog 自称状态语言的单一来源，应与真实渲染一致，不能用降低可读性的方式消除差异。

本报告裁定技术方向，**不释放实现、不批准当前 Task、不代替 DSH 范围冻结与 findings 处置**。推荐新建后续 Task，不扩 FEA-06-RESIDUAL-2 的写域；当前卡保留可追溯特判，直到后续修复集成。

| 方案 | 结论 | 原因与影响 |
|---|---|---|
| A：catalog → Secondary | **采用** | 恢复状态键与 glyph/Chip 文字的一致性；现有 DS 渲染保持原样。必须处理下文两处 V2 既有映射缺口。 |
| B：glyph 样式 → Disabled | **否决** | 普通主题下对比度不足；使已有可读 glyph 退化。若只改 glyph，Chip/CountChips 的 `nm-status-notstarted` 仍为 Secondary，依然不一致；若一起改，扩大可读性回归。 |
| C：catalog=语义状态色、glyph=可读渲染色 | **否决** | 现有 `ColorKey` 没有这种双重契约；Disabled 是交互禁用层级，不能据名称认作 NotStarted 的业务语义色。该拆分不能解释 Chip 文字为何也需要 Secondary，且会永久化临时例外。 |

若未来确有 C 的产品需求，**需要额外的显式 API 字段/访问器**（例如保留并明确命名的语义色键，加 `ForegroundColorKey` 或按用途查询的映射），并列出 glyph、label、fill、border 各消费者的取值与测试。只在文档写“glyph 自行提升亮度”、继续让唯一 `ColorKey` 隐含两种含义不可接受；仅增加另一个 `StatusKind` 也不能解决。当前无此需求依据，D-14 不应引入这套契约。

## 2. 固定基线与证据

- 工作区 `G:\CODEX\New Manga`，分支 `main`，HEAD `195422c2fdf72f0460d2e265b53e22a2c5eff6fd`；Git common directory `G:/CODEX/New Manga/.git`。开始时 `git status --short` 为空。
- 已读当前 STATUS、Plan、FEA-06-RESIDUAL-2、scope-r3、Task 指向的 impl-r1（重点 R2-016）、rolling checkpoint 当前条目 §140–143。读取时 impl-r2 报告尚不存在；本报告不冒充其结论。
- `Controls/Status.cs:25–28,75–85`：catalog 声明状态语言单一来源；NotStarted 实际返回 Disabled。`:11–22,55,70`：它是九值之一，有独立符号 `○` 与标签“未开始”。
- `Styles/Controls.Status.axaml:35–38`：glyph 使用 Secondary，注释明确要求该真实状态保持 ≥4.5:1；`:65–66`：普通状态文字同样用 Secondary；`:113–115`：NotStarted badge 背景为 `Bg.Sunken`。
- [03-accessibility §4](../design/fluent-v1/03-accessibility.md#4-高对比与可读性)：正文 ≥4.5:1，状态不只靠颜色；glyph 本身是小字号 TextBlock，并已有更严格的 4.5:1 样式说明与复合背景测试，不能套用一般图形的 3:1 下限放宽。
- [10-component-inventory](../design/fluent-v1/10-component-inventory.md)：开头要求复用 DS 组件，§1/§2 列状态条、状态徽标、批量状态，§4 要求状态同时有图标/文字。该文件**未单独冻结 NotStarted=Disabled**。
- [01-design-tokens](../design/fluent-v1/01-design-tokens.md) §2.2/§3 要求用既有令牌及不透明背景降级；它没有列出这两个文字色的 RGB。实际色值以 `Themes/Tokens.Dark.axaml`、`Tokens.Light.axaml` 的生成资源为本轮核算输入，未据设计文件推断不存在的数值表。

### 实测对比度矩阵（executed）

环境：Windows、`C:\Program Files\PowerShell\7\pwsh.exe`，PowerShell 7.6.8。读取两个 AXAML 的 SolidColorBrush，按仓库 `Accessibility/ContrastMath.cs` 同样的 sRGB 线性化公式计算：`L=0.2126R+0.7152G+0.0722B`，`ratio=(Lmax+0.05)/(Lmin+0.05)`。本表颜色 alpha 均为 FF，无混合近似。计算命令退出码 **0**；以下是该次输出的持久化摘要，并非产品测试通过声明。

| 主题 | 背景 `Nm.Color.Bg.*`（RGB） | Secondary 对比度 | Disabled 对比度 |
|---|---|---:|---:|
| Dark | App `#141518` | 7.6312:1 | 2.3522:1 |
| Dark | Canvas `#0F1012` | 7.9566:1 | 2.4525:1 |
| Dark | Panel `#1A1C1F` | 7.1372:1 | 2.1999:1 |
| Dark | Raised `#22252A` | 6.4253:1 | 1.9805:1 |
| Dark | Overlay `#2A2E34` | 5.7039:1 | 1.7581:1 |
| Dark | Sunken `#0B0C0E` | 8.1790:1 | 2.5211:1 |
| Light | App `#FAF9F7` | 6.6963:1 | 1.8951:1 |
| Light | Canvas `#F4F3F0` | 6.3497:1 | 1.7970:1 |
| Light | Panel `#FFFFFF` | 7.0459:1 | 1.9940:1 |
| Light | Raised `#F2F1EE` | 6.2380:1 | 1.7654:1 |
| Light | Overlay `#FFFFFF` | 7.0459:1 | 1.9940:1 |
| Light | Sunken `#ECEAE5` | 5.8606:1 | 1.6585:1 |

Dark 前景：Secondary `#A3A8AF` / Disabled `#4E5359`；Light：Secondary `#55595F` / Disabled `#B4B8BD`（两文件 `:36,39`）。Secondary 最低 5.7039:1，Disabled 最高仅 2.5211:1。B 在 NotStarted badge 实际 Sunken 背景上也失败，并非只在假定 Panel 上失败。

可复核的只读等价命令（仓库根目录，PowerShell；只向标准输出写入）：

```powershell
function Lum([string]$hex) {
    $rgb = $hex.Substring($hex.Length - 6)
    $v = @()
    for ($i = 0; $i -lt 3; $i++) {
        $s = [Convert]::ToInt32($rgb.Substring($i * 2, 2), 16) / 255.0
        if ($s -le 0.04045) { $v += $s / 12.92 }
        else { $v += [Math]::Pow(($s + 0.055) / 1.055, 2.4) }
    }
    0.2126 * $v[0] + 0.7152 * $v[1] + 0.0722 * $v[2]
}
foreach ($theme in 'Dark','Light') {
    [xml]$xml = Get-Content "apps/desktop-avalonia/src/NewManga.DesignSystem/Themes/Tokens.$theme.axaml" -Raw
    $map = @{}
    foreach ($n in $xml.SelectNodes('//*[local-name()="SolidColorBrush"]')) {
        $map[$n.GetAttribute('Key','http://schemas.microsoft.com/winfx/2006/xaml')] = $n.GetAttribute('Color')
    }
    foreach ($surface in 'App','Canvas','Panel','Raised','Overlay','Sunken') {
        $b = Lum $map["Nm.Color.Bg.$surface"]
        foreach ($tier in 'Secondary','Disabled') {
            $f = Lum $map["Nm.Color.Text.$tier"]
            '{0}/{1}/{2}: {3:F4}:1' -f $theme,$surface,$tier,(([Math]::Max($f,$b)+0.05)/([Math]::Min($f,$b)+0.05))
        }
    }
}
```

## 3. 消费者与回归边界（rg + 调用链复核）

实际执行的有效检索（均有命中，exit 0）：

```powershell
rg -n 'StatusCatalog|StatusKind.NotStarted|StatusGlyph|StatusBadge|CountChips' apps/desktop-avalonia/src apps/desktop-avalonia/tests
rg -n 'ColorTokenKey|StatusCatalog\.ColorKey' --glob '*.cs' --glob '*.axaml' .
rg -n 'notstarted|not-started' apps/desktop-avalonia/src/NewManga.App/Views/V2/Studio apps/desktop-avalonia/src/NewManga.App/Views/V2/Shell/Theme/V2LocalStyles.axaml apps/desktop-avalonia/src/NewManga.DesignSystem/Styles
rg -n 'Status|Badge|Chip|Glyph|未开始|Text.Disabled|Text.Secondary' apps/desktop-avalonia/src/NewManga.App/Views/Fluent/ReaderPageView.cs apps/desktop-avalonia/src/NewManga.App/Views/Fluent/WorkbenchPageView.cs
```

| 消费者 | 已核实调用链与锚点 | A/B/C 的影响 |
|---|---|---|
| DS `StatusGlyph` / `StatusBadge` | `Status.cs:135–142` 只设置 Symbol/ClassName；`Badges.cs:53–60` 给内部 glyph 设置 Status、给标签设置 Label。实际色走 Styles。 | A 不改变当前画面；B 直接降低 glyph 对比度。C 会保留 catalog 与实际前景不同的问题，所有按 catalog 校验的消费者都要选用途。 |
| DS `Chip` / `CountChips` | `Badges.cs:137–146` 设置 `nm-status-*` 标签类；`Feedback.cs:246–264` 用 `CountChipItem.Status` 构造 Chip；`Controls.Status.axaml:65` 指定 Secondary。普通 Chip 背景为 Raised，active 为 Accent.Muted（`Controls.Custom.axaml:9–25`）。 | A 不改变画面或筛选行为；B 只改 glyph 对它们无效，若再改文字则引入低对比度。后续验证 active 背景须用实际合成色，不能拿本表不透明背景代替。 |
| DS `AlertBanner` / IN-2A | `Feedback.cs:181–191` 给内部 glyph 赋 Severity；测试 `FluentResidual2StateEffectiveTests.cs:475–477,504–509` 保留 Secondary 期望，并跳过 NotStarted 的 catalog 交叉比较；`expected-tokens.md` 已记录 D-14。 | A 恢复九值同一交叉规则；B 会破坏当前 Secondary 期望，并降低 Panel 上的可读性；C 则要求永久改写该断言契约。 |
| `StudioStates.ColorTokenKey` | `ViewModels/V2/Studio/StudioStateKind.cs:58` 是检索到的唯一生产代码 `ColorKey` 调用者；`V2StudioMathTests.cs:127` 只断言键前缀；没有找到把其返回值直接赋给生产 Foreground 的调用点。 | A 改变此查询的 NotStarted 返回键，现有前缀测试不应失败；不能由此宣称 Studio 实际颜色已修好。 |
| Current V2 工作台状态文字 | `StudioTheme.axaml:49–50` 的 `studio-state-notstarted` 仍是 Disabled；`Controls/StudioUi.cs:111` 用 `StudioStates.StyleClass` 给文字加类。 | **既有缺口**：A 单改 catalog 后，其注释“ColorTokenKey backing StyleClass”会与样式不符；这不是 A 导致颜色变暗，而是暴露既有重复映射。后续卡应同时把该文字样式对齐 Secondary。`:78` 的 fill 是 Line.Subtle，属背景用途，不在本裁决中改为文字色。 |
| Current V2 本地 `StatusBadge` / ReaderOverlay | `Views/V2/Shell/Controls/StatusBadge.cs` 用另一套 `NmStatusInfo`，不是 DS StatusBadge；`V2LocalStyles.axaml:191–192` 的 `st-not-started TextBlock.symbol` 仍用 Disabled。`Views/V2/Library/ReaderOverlay.axaml:62` 当前显式使用 Blocked。 | A/B 都不会自动改动此本地符号；NotStarted 低可读性属于第二处既有缺口，建议后续卡对齐 Secondary。ReaderOverlay 的 Blocked 不受 NotStarted 选择影响。不得把两种同名 StatusBadge 混算。 |
| Fluent Reader / Workbench | Reader `:344,349,358` 经 `FluentUi.Banner` 用 Failed/Blocked/Locked；Workbench `:375,386,391,396` 用 Failed/Stale/Locked/Blocked。未发现直接调用 catalog 或构造 NotStarted。 | A 对这些分支无预期视觉变化；B 对这些非 NotStarted 分支也无直接变化。保留页面 smoke；不得宣称尚未接入的数据投影已经覆盖。 |
| 其他符号调用者 / 生成物 | StudioInspector/RegionOverlay 使用 `StatusCatalog.Symbol(Locked)`；`Generated/StatusCatalog.g.cs` 实际生成的是 `NmStatusSymbols`，不生成 `ColorKey`。 | A 不改锁定语义、符号或资源键集合；不需改生成物。 |

检索未发现生产调用者依据 `ColorKey(NotStarted)==Disabled` 决定禁用、筛选、持久化或任务状态迁移。该结论限于本 head 的静态调用链，**不是运行时全场景无回归证明**。本次同时记录 V2 两处缺口，避免将“DS glyph 已可读”误报为“所有 NotStarted 消费者已一致”。

## 4. 实施文件与测试要求

建议后续卡显式冻结以下文件；本次全部只读：

1. 必改 `apps/desktop-avalonia/src/NewManga.DesignSystem/Controls/Status.cs`：NotStarted → Secondary，更新 `ColorKey` 注释。
2. 必改 `apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/FluentResidual2StateEffectiveTests.cs`：修复集成时移除 `kind != StatusKind.NotStarted` 条件，九值无例外交叉断言；仍保留独立的逐状态期望键表，避免测试仅复制 catalog。
3. 测试落点：`CustomControlsTests.cs`（明确 NotStarted 键、符号、标签）、`ContrastTokenTests.cs` / `BadgeCompositeContrastTests.cs`（复用已有对比度机制）；必要的新 Chip/CountChips 有效属性覆盖限于同测试项目，由 DSH 冻结具体文件。
4. 建议纳入同一后续卡的两处前景映射：`apps/desktop-avalonia/src/NewManga.App/Views/V2/Studio/StudioTheme.axaml` 与 `apps/desktop-avalonia/src/NewManga.App/Views/V2/Shell/Theme/V2LocalStyles.axaml`，仅 NotStarted 文字/符号改用 Secondary；对应验证可落 `tests/NewManga.App.Tests/V2StudioMathTests.cs` 与 DSH 指定的 V2 headless 测试。它们是当前 Avalonia frontend 的既有消费者，并非旧 Tauri/QML 实现；但 FEA-06-RESIDUAL-2 禁止改 Current V2，故不能顺手在当前卡修。
5. `Styles/Controls.Status.axaml` 是比对锚点，**无需修改**；不改 `Tokens.*.axaml`、`Generated/**`、冻结设计、Schema、Core、Host/IPC 或包依赖。旧 Task/Review/日志/PNG/pin 保持原字节；后续新增自己的证据与 Handoff，记录原 D-14 特例已在哪个 head 消除。

后续卡 AC（均为 **planned / NOT_RUN**，本次未实施）：

- catalog 明确断言 NotStarted=Secondary；其他八值映射、`○`、“未开始”、`ClassName`、`MutedColorKey(NotStarted)==null` 保持原义。覆盖 `StudioStates.ColorTokenKey(NotStarted)`。
- 真实加载生产样式栈，九个状态的 catalog 键与 glyph 有效前景逐值一致，无 NotStarted 跳过；AlertBanner 九值交叉检查全部执行。
- NotStarted 的 glyph、badge 标签、Chip/CountChips 标签，以及纳入范围的 V2 两处文字/符号，在 light/dark 标准及高对比下断言 **≥4.5:1**。覆盖 Panel/Raised/Overlay，badge 使用实际 Sunken 背景；Chip 的 active/hover、透明背景或继承 opacity 按实际合成色测量。高对比保留既有更高文字门槛，不用 4.5 降低原 7:1 要求。
- 复用 `BadgeCompositeContrastTests.Status_badge_glyph_contrast_is_measured_against_the_rendered_composited_background`：它已经遍历九值、标准/高对比、三种父表面并对真实背景采样，glyph 与 label 均要求 ≥4.5:1。它证明的是样式可读性，仍须新增 catalog 一致性断言。
- A 的对照判别：新增的精确 catalog 断言在本 reviewed_head 应失败（实际 Disabled），修复后通过；B 的反证已由本报告对比度矩阵给出，未来渲染测试也须能拦住把 glyph 换成 Disabled 的回退。
- Reader/Workbench 页面 smoke，Chip 过滤与 CountChips 计数行为不变；真正 disabled 控件继续使用原禁用令牌/opacity，不能全局替换 Disabled。

**特判可移除，但不能现在移除。** 条件是 A 的实现、九值一致性与 ≥4.5:1 测试通过，并由 DSH 集成后在同一交付链移除。若后续卡只改 catalog 而遗漏已记录的 V2 样式，不得宣称产品所有状态前景已统一。FEA-06-RESIDUAL-2 的旧证据继续作为修复前快照保留，不回写为“当时已通过”。

可复制的后续验证命令（PowerShell，仓库根；输出统一在 DSH 新卡 workspace；**本轮未运行**）：

```powershell
$taskArtifacts = 'G:\CODEX\New Manga.workspace\FEA-STATUS-NOTSTARTED-1\artifacts'
dotnet build apps/desktop-avalonia/NewManga.sln --artifacts-path $taskArtifacts -warnaserror
dotnet test apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/NewManga.DesignSystem.Tests.csproj --artifacts-path $taskArtifacts --no-build --filter 'FullyQualifiedName~CustomControlsTests|FullyQualifiedName~FluentResidual2StateEffectiveTests|FullyQualifiedName~ContrastTokenTests|FullyQualifiedName~BadgeCompositeContrastTests'
dotnet test apps/desktop-avalonia/NewManga.sln --artifacts-path $taskArtifacts --no-build
pwsh -NoProfile -File tools/governance/check.ps1
```

定向命令不代替无过滤全量。保存 shell/解释器、环境、base/head、逐命令 EXIT、逐程序集 passed/failed/skipped、逐条 skip 原因与相对释放基线的差值；默认运行不得改旧证据，截图须 opt-in 到新卡证据目录。具体新增测试命名与环境由 DSH 释放时冻结。

## 5. 本轮验证与边界

| 项目 | 状态 | 结果/证据 |
|---|---|---|
| Git 基线、当前卡与有效设计、调用链只读核验 | executed | 固定上文 reviewed_head；rg 摘要及锚点见 §2–3。 |
| 两套普通主题的颜色对照计算 | executed | exit 0；§2 的 24 项比值及等价只读命令。Secondary 全部 ≥4.5；Disabled 全部 <4.5。 |
| 治理检查 | executed / PASS | `pwsh -NoProfile -File tools/governance/check.ps1`，exit 0，`Governance check: PASS (3 warnings)`；15 current documents，无历史目录扫描。警告：9 个非终态 Task；STATUS/Plan 达体量预算 80%。本报告不处置这些既有项。 |
| 编译、产品单元/headless/原生 UI、截图 | NOT_RUN | 本轮只裁决；未改源码，未构建、未产生产品测试计数或新 PNG；不得引用既有 1274/0/57 作为本次实跑。 |
| Architecture | executed | 方向限于 DS 状态键与现有 UI 前景映射；无共享 wire/schema/依赖/数据访问变化，无新增双重色契约。实现仍受 DSH 写域冻结约束。 |
| Verification | executed（只读裁决覆盖） | 足以否决 B 与无依据的 C、确定 A 的修复方向；不签发实现验收。合成背景、运行时换肤及 V2 实际渲染留给后续卡实测。 |

## 6. 实施卡建议与可转发指令

**推荐新建 `FEA-STATUS-NOTSTARTED-1`（建议 ID，尚未进入 DAG / 未释放），不扩 FEA-06-RESIDUAL-2。** 当前 Plan 无 READY 节点；先由 DSH 接收本裁决，处置 D-14/R2-016，确认当前卡交付 head 与评审结果，冻结新卡范围、依赖和基线。当前卡可据原范围继续审查，但不能把 D-14 实现或全产品一致性写成 MET。

- **Agent**：DSH 负责登记/释放、范围与集成；建议 ZCode 实施 DS + Avalonia 样式和测试；Reviewer 由 DSH Appointment，使用未参与实现/返修的独立上下文 Codex 或 ZCode 会话。
- **Recovery point**：来源仓库 `G:\CODEX\New Manga`，`main`，本次固定 base/head 均取诊断 head `195422c2fdf72f0460d2e265b53e22a2c5eff6fd`（原当前卡 base 见 front matter）；新卡 branch/worktree **待 DSH 创建**，不得直接沿用诊断 head 假定其已含后续集成。释放时若 main 前进，DSH 应重验受影响代码并冻结新的实际 base/head。
- **Scope**：仅 §4 列出的 catalog、两处 V2 NotStarted 前景和必要测试，加新卡 Task/Handoff/Review/`verification/FEA-STATUS-NOTSTARTED-1/**`；DSH 显式列入 allowed_paths。禁止改原证据、冻结设计、生成物、Core/Host/IPC/Schema/依赖与任何用户文件；禁止 push。无需新共享接口/Schema/依赖授权，若实现出现这种需要则暂停该部分交 DSH。
- **Deliverables**：固定实现 commit、精确变更清单、新卡测试/判别力日志、必要的真实主题截图、Handoff；九值一致性、≥4.5:1 和回归证据齐备。上下文独立 Review → DSH 集成验证 → 资源 closeout 才能关闭新卡。

可直接转发给 **DSH**（范围冻结请求，非已释放实现指令）：

> 请在 `G:\CODEX\New Manga` 接收 `doc/reviews/ADJ-2026-11-03-D14-STATUS-NOTSTARTED.md`，裁决 A：NotStarted 的 `StatusCatalog.ColorKey` 对齐 Secondary。诊断来源为 main，固定 base/head `195422c2fdf72f0460d2e265b53e22a2c5eff6fd`；新卡建议 `FEA-STATUS-NOTSTARTED-1`，branch/worktree 待你创建并冻结实际 base/head。请不扩 FEA-06-RESIDUAL-2，登记新卡并推荐 ZCode 实施：只改 Status.cs 映射/注释、报告 §4 两处 V2 NotStarted 前景、必要 DS/App 测试，并在修复交付中移除 IN-2A NotStarted 交叉断言特判；不改旧 Task/证据/冻结设计/生成物/Core/Host/IPC/Schema/依赖/用户数据，不 push。交付固定 commit、新卡 verification 与 Handoff。按报告 §4 执行九值映射一致性、标准/高对比和实际合成背景 ≥4.5:1、Reader/Workbench/Chip 回归与无过滤全量，记录命令/环境/EXIT/逐程序集计数/skip；定向测试不冒充全量。请另行 Appointment 未参与实现/返修的独立上下文 Reviewer，审查后由你集成验证和关闭；释放前不得实施。

本次仅新增本报告；未修改源码、Task、既有证据，未 commit，未 push。
