---
task_id: FEA-06
reviewer: subagent_zcode
reviewer_kind: subagent
author: dsh-lead
base_commit: 5a47170096bb28c42d108756f522cf4250cab983
reviewed_head: 53060cd6749b9daa304fe11fd80525d9cdc9fb08
decision: changes_requested
counts: { P0: 1, P1: 1, P2: 10 }
---

# FEA-06 范围冻结复核 r2（独立上下文）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06.md`（`proposed`，Fluent UI 四页实现；`owner: codex`（用户 2026-11-02 指派，W-10）） |
| base_commit | `5a47170096bb28c42d108756f522cf4250cab983`（`git merge-base --is-ancestor` → 0，为被审 head 的直接父） |
| reviewed_head | `53060cd6749b9daa304fe11fd80525d9cdc9fb08`（`docs(fea-06): 范围修订 r2…`；4 文件 +67/−32，全部 doc/**） |
| reviewer | **subagent_zcode**——DSH Lead 通过 `subagent_zcode` 派发的**独立上下文子代理**；本席位未参与 FEA-06 的任何起草、范围处置或实现（含 PREREQ-1/2），符合 2026-10-31 上下文独立裁决 |
| 日期 | 2026-11-02（r2 轮） |
| 审查对象 | r2 范围修订的 r1 闭环充分性、可执行性（Codex 可直接开工？）、写域、治理一致性 |
| 结论 | **changes_requested**（P0=1 / P1=1 / P2=10） |
| 前置核实 | `git rev-parse HEAD` = `53060cd67…` ✓；`git status --short` 空（clean）✓；`92cac5ab1..53060cd67` 区间非 doc/verification 文件变更数 = **0**（docs-only 确认，代码与 PREREQ-2 集成验证时逐字节一致） |

> **一句话结论**：r1 的两大 P0（C-03 外观持久化、Fluent 双壳激活）已由 PREREQ-1/2 **真实交付**，令牌/组件 AC/字段清单/治理指针等 r1 项绝大部分闭环且实测成立；**但存在一个 r2 新发现的 P0**：组合根 `App.axaml.cs:137` 的 Fluent 分支只以 `(options, selection)` 调用 `FluentShell.CreateRoot`，**`HostController` / `AppearanceCoordinator` / `DesignSystemThemeManager` 均未进入 Fluent 壳**，而 W-9 又把 `App.axaml.cs`/组合根明确排除在写域外——AC2/AC3/AC4（数据与 Draft 命令面）和 AC5（经 coordinator 保存外观）在当前写域内**没有合法实现通路**（自建第二 `HostController` = 重复启动 sidecar；自建第二 `AppearanceCoordinator` 破坏唯一写者单实例语义）。另有一处 P1：AC2–AC5 的状态清单与 `09-state-matrix.md`（及 05–08 正文状态表）不一致（AC4 仅列 4 态缺「空/满/部分缺页」、AC5 无状态绑定、AC3 差 2 行、AC2 缺「满」且「未就绪」术语错位），W-8「逐页写死 09 状态集合」的处置声明与事实不符。修复均为 docs-only 卡修订 + DSH 一处小裁决，不需要动设计基线。

---

## 0. 方法与只读声明

- 只读核查被审 head；未修改任何源码/卡/契约/STATUS/PLAN/LEDGER/证据；未 commit/push；`git status --porcelain` 为空。本报告为本轮唯一新增文件。
- 本轮实测（全部在 `53060cd67` 工作区）：
  - `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` → **exit 0，0 错误**。
  - `dotnet test …NewManga.sln --no-build --settings …NewManga.runsettings` → **App.Tests 452/0/7 全绿**；CoreClient.Tests 首跑 **127/1/22**（1 failed），单独重跑该套件 **128/0/22 全绿**（首跑失败为既有时间敏感 flaky，非被审提交回归——区间 docs-only 已实证）。其余套件汇总被日志截尾；代码与 PREREQ-2 集成验证（**1022/0/57**，`f320aa462`）一致，基线口径可信。
  - `TokenGen -- --check` → **up to date（rows 292）**；`ThemeGen -- --check` → **up to date**。
  - `pwsh tools/governance/check.ps1` → **PASS（3 warnings：9 非终态；STATUS 3196B/29 行 80%；PLAN 4100B/62 行 80%）**；`verify_pins.ps1` → **PASS（all 15）**。
- 阅读范围：FEA-06 卡（r2 版 137 行）、r1 复核报告、PREREQ-1/2 卡、`doc/design/fluent-v1/`（01–10 + README 全部 11 文件）、`FEA-05_DRAFT_WIRE_CONTRACT.md`、`FEA-C02_V11R_AMENDMENT_DRAFT.md`（V-05/V-07/V-08b）、STATUS/PLAN/TASK_LEDGER/checkpoint §30–32、`NewManga.Appearance/**`、`FrontendSelector.cs`、`App.axaml.cs`、`FluentShell.axaml.cs`、`ShellCommands.cs`、`NmKeys.g.cs`、`TokenMap.cs`、`fluent-dark.nmtheme`、`IHostController.cs`。

---

## 1. r1 逐项闭环核验表

| r1 发现 | 判定 | 仓库事实证据（行号基于 `53060cd67`） |
|---|---|---|
| **P0-1** C-03 外观持久化不存在 | **已闭环** | `NewManga.Appearance/`（`AppearanceSettings.cs`/`AppearanceCoordinator.cs`/`AppearanceStore.cs`/`AppearanceJson.cs`）真实存在；`AppearanceSettings.cs:10-49` 逐字段覆盖 C-03 §2.2：`FrontendId`/`VisualThemeId`/`Mode`/`Contrast`/`FollowSystemAccent`/`MotionMode`（`:68`，`Auto/Full/Reduce` 三态）/`MotionCategories`（`:81-84`，`Navigation/Feedback/Decorative`）/`CornersScale`/`MaterialAcrylicStrength`/`MaterialMicaEnabled`/`Layout`（navigation/shelf/density/workbench/reader）/`SchemaVersion=2`；唯一写者收敛在 `AppearanceCoordinator.cs:21`（类注释明示 owns `SaveAsync`，`:67-71` 落 `AppearanceStore.WriteAsync`），PREREQ-2 已将其迁入 `NewManga.Appearance`（D-1 关闭）。AC5 字段、AC7 动效判据可落（注入通路问题见 r2-P0） |
| **P0-2** Fluent 激活/双壳未裁决、组合根不在写域 | **部分闭环** | `FrontendSelector.cs` 决策表（`builtin.current-v2`→V2、`builtin.fluent`→Fluent、其余含 `builtin.fluent-dark`→V2 fallback + Diagnostic）✓；组合根 `App.axaml.cs:115-139` `CreateShell` 双壳，`:109-112` `--shell=legacy`（`UseV2Shell` 分支）优先于 selector ✓；`FluentShell.axaml.cs` 四页占位 + 导航序冻结（`Library/Workbench/Reader/Settings`），headless 可启动（`FrontendSelectorTests.cs`/`FluentShellTests.cs` 在 App.Tests）✓；集成 `92cac5ab1`、全量 1022/0/57 ✓。**但** Fluent 分支依赖注入通路断裂（见 **r2-P0**）——壳可启动 ≠ 四页内容可接数据 |
| **P1-1** 令牌生成缺口（G-1/G-1b/G-1c） | **已闭环** | `Generated/NmKeys.g.cs`：`Nm.Corner.Fluent.Lg/Md/Sm`（`:55-57`）、`Nm.Elevation.1/2/3`（`:61-63` + 类定义 `:305-312`）、`Nm.Focus.Ring.Color/Offset/Width`（`:64-66`）、`Nm.Material.Acrylic.Base/Opacity/Tint` + `Nm.Material.Mica.Enabled`（`:95-98`）；`TokenMap.cs:162`（`DerivedGlobals`）与 `:206-211`（Elevation 以 `TokenValueKind.BoxShadows` 派生）；`fluent-dark.nmtheme:55-56/117-118` 承载 `Nm.Material.Acrylic.Base/Tint` 主题层取值；两生成器 `-- --check` 本轮实测 up to date（rows 292）✓ |
| **P1-2** AC2–AC5 未绑定 09 状态矩阵 | **部分闭环** | W-8 裁决正确、处置表声称「逐页写死状态清单（取自 09）」，但实测清单与 `09-state-matrix.md:6-16`（及 05 §3 七态 / 06 §3 八态 / 07 §3 六态 / 08 §4 六态）不一致：AC2 括号 6 项缺「满」且「未就绪」非 09/05 术语（应为「只读」，05 表述「只读/旧壳运行」）；AC3「8 态」对应 06 正文 §3，但 09 工作台列共 9 行（另有「空（批量筛选无结果）」`09:9` 与「运行中（Run 投影条 + 控制）」`09:16`）；AC4 括号仅 4 项，缺「空（本章节暂无页面+返回）」「满」「部分/缺页（缺页占位+可重试，referenced source 语义）」；AC5 无状态清单（仅「保存/校验/错误态」），08 §4 的 空防御/载入骨架/满/部分（字段禁用+原因 Tooltip）/只读（保存禁用）均未绑定。→ **r2-P1** |
| **P1-3** Draft typed error 映射表未冻结 | **已闭环（P2 措辞）** | AC3 冻结「17 码→Category→UI」按 category 归组：validation=行内提示、not_found=刷新/清选、conflict=重读提示、unavailable=可重试横幅、internal=错误页。对照 `FEA-05_DRAFT_WIRE_CONTRACT.md:41-63`：17 码 category 分布 validation×5 / not_found×3 / conflict×6 / unavailable×2 / internal×1，全部落入 AC3 五类，逐码机械可验 ✓。「internal=错误页」与 06 设计「错误卡（画布保留上一帧，不清屏）」「flush 失败留旧 UI 不切换」存在措辞张力 → r2-P2-2 |
| **P1-4** P6 无 AC / 无组件拆解 | **已闭环** | AC6 列 19 项（`SurfaceCard`/`Drawer`/`Dialog`/`EmptyState`/`ErrorState`/`Toast/InfoBar`/`BookCard`/`BookRow`/`RegionBox`/`BatchMatrix`/`RunProjectionBar`/`SettingsGroup`/`SettingsField`/`PrimaryButton`/`SecondaryButton`/`DangerButton`/`SearchField`/`TabStrip`/`SegmentedControl`）与 `10-component-inventory.md` 名称逐项一致，且「以 10 为准逐项登记（名称、令牌依赖、状态、尺寸、测试）」+ normal/hover/pressed/disabled + 浮层开/关 + 无裸值 + 不复制业务组件，与 10 §5 评审检查点对齐；P6 任务行 + W-11 组件登记表承载 |
| **P1-5** 四页↔三空间↔左导航映射冲突 | **已闭环（P2 补引）** | 设计基线映射完备：三空间 = `space.library/space.studio/space.console`（`03:12`，`Ctrl+1/2/3`）；书架页 = `SpaceId.Library`（`05:3`「不得新增空间」）；工作台 = 工位 Studio（`06:12/21`，控制台 Tab 仅跳转入口不改 SpaceId）；**阅读器 = Library 内 `ShellSurface.ReaderOverlay` 浮层、不改 SpaceId（`07:3/22`）；设置 = `ShellSurface.ThemeStudio` 外壳承载外观分组、不新增 SpaceId（`08:3`）**。W-6「四页与空间映射以设计为准、不新增第五页」与之自洽、无矛盾。W-6 只引 `04:13`/`05:21` 未引 `07:3`/`08:3` 两个关键锚点 → r2-P2-3 |
| **P1-6** AC5 字段范围不清 | **已闭环（P2 摘要）** | AC5「`08-page-settings.md:41-58` 字段逐字渲染（C-03 §2.2 字段名一致）」——行号范围 +「逐字」判据可机械核对；08:41-58 冻结 14 行（visualThemeId/frontendId/appearance/contrast/motion.mode/motion.categories/corners/material/layout.*/followSystemAccent/schemaVersion/Provider 凭据/网络/备份恢复/关于）全部在验收范围，且 `AppearanceSettings` 已有对应承载字段。P5 括号摘要漏列「深/浅（appearance）」「对比度（contrast）」→ r2-P2-1（不影响验收基准） |
| **P1-7** PLAN/STATUS 指针不一致 | **已闭环** | `REBASELINE_PLAN.md:17` FEA-04b **done**（`:20` FEA-06 proposed owner=Codex、`:21-22` PREREQ-1/2 done、`:37` 当前 DAG 尾段一致）；`STATUS.md:7`（FEA-06 proposed、owner=Codex、scope-r2 复核中）与 `:10`（下一候选 FEA-06）；`TASK_LEDGER.md:45` FEA-06 proposed；checkpoint §32 记录用户指派与 Codex 通路核验；`check.ps1` PASS(3 warnings)、`verify_pins` 15/15 本轮复跑一致 ✓ |
| **P2-1**（写域缺口 Styles 等） | **部分采纳** | W-9 追加 `Controls/**`/`Styles/**`/`Services/**` ✓；但组合根问题以新形态残留（r2-P0），ThemeEngine/项目文件维持排除（本卡确实不需写） |
| **P2-2**（`IPageNavigation*` 死路径） | **已闭环** | r2 重写后 allowed_paths 用 `Services/**` 通配，死路径 glob 已消失 |
| **P2-3**（owner 记录） | **已闭环** | 用户 2026-11-02 指派落盘三处：卡 `approval`/`owner: codex` + W-10 全文、STATUS:7、PLAN:20、checkpoint §32（含 Codex CLI 探测结论） |
| **P2-4/P2-5**（04 §3 折叠/§5 DPI、07 交互细节） | **已采纳** | AC1「三断点布局、折叠、z-order」含 §3 折叠；AC4「页导航/缩放/全屏/双击/键盘滚轮→翻页、缩放/双击、方向 memento」覆盖 07 §4 主体（双屏 G-4 归 FEA-07 未注明 deferral → 遗留 P2-10 同类） |
| **P2-6**（采证口径） | **已闭环** | W-11：每页 ≥1 headless 状态测试（`AvaloniaFact`）+ ≥1 张 headless 渲染截图 PNG 落 `verification/FEA-06/` + 组件登记表 Markdown + 日志含命令与 exit；`Avalonia.Headless.XUnit` 已在 App.Tests 可用（r1 已核，本轮 FrontendSelectorTests/FluentShellTests 在场佐证） |
| **P2-7**（G-3 资产） | **未处置** | 卡未声明「沿用 `NmIcon` 既有集合、不新增资产」，写域无 `Assets/**` → r2-P2-6 |
| **P2-8**（FEA-04b AC5 裁决引用） | **已采纳** | 来源段写明「FEA-04b done，集成 `112221b9a`，独立复核 r5 approved」 |
| **P2-9**（分期） | **未采纳（可接受）** | 单卡仍含四页+Shell+19 组件+动效+设置；W-10 用户指派单卡成立，建议在派发 brief 给交付顺序而非拆卡 → r2-P2-10 |
| **P2-10**（偏差登记口径） | **已采纳（取严）** | W-1「偏差走 v1.1 修订 + 重冻结」严于 README §4 的 MINOR/PATCH 分级，不冲突 |
| **P2-11**（depends_on 补 FEA-04） | **未采纳** | depends_on 仍为 FEA-04b/FEA-05-PORT-1/PREREQ-1/2；FEA-04 经 FEA-05-WIRE-1→FEA-03/FEA-04 传递可达，不阻塞 → r2-P2-5 |

---

## 2. 可执行性审查（核心）

### 2.1 **P0（1 条，阻塞释放）**

| ID | 位置 | 问题 | 建议（责任方） |
|---|---|---|---|
| **P0** | `App.axaml.cs:77-78`（controller/appearance 构造）、`:137`（`return selection.IsFluent ? FluentShell.CreateRoot(options, selection) : …`）；`FluentShell.axaml.cs:69`（构造 `(AppOptions?, FrontendSelection?)`）、`:101`（`CreateRoot(AppOptions?, FrontendSelection?)`）；卡 `:111`（W-9「不含 `App.axaml`/组合根（PREREQ-2 已冻结）」）、`:24-40`（allowed_paths） | **Fluent 壳的依赖注入通路断裂：四页数据/命令/外观面在当前写域内不可接入。** 组合根在 `App.axaml.cs:77` 构造 `HostController`、`:70` 附近构造 `AppearanceCoordinator`，V2 分支 `CreateV2Shell(application, controller, options, themeManager, appearance, themeHome)` 全量注入；**Fluent 分支只传 `(options, selection)`**——`IHostController`（AC2 书库读、AC3 Draft 7 方法 `IHostController.cs:420-458`、AC4 `IReaderProgressSink` `:104`）与 `AppearanceCoordinator`（AC5「不越权写 presentation-settings.json（经 coordinator）」）均无法到达 FluentShell 内的四页 ViewModel；`App` 类无静态暴露位、无服务定位器。写域内自解的两条路都不成立：①自建第二 `HostController` = 第二个 sidecar 启动（不可接受）；②自建第二 `AppearanceCoordinator(new AppearanceStore(...))` = 双实例并发写同一文件、`Changed`/`Settings` 与组合根实例失联，破坏 PREREQ-2 W-10 唯一写者单实例语义。r1-P0-2 修复了「壳可启动」，但「四页内容可接数据」这一半未闭合 | **DSH 二选一（释放前）**：①DSH 单点小 commit：`App.axaml.cs:137` 改为向 `FluentShell.CreateRoot` 传 `controller, appearance, themeManager`，并同步把 `FluentShell.CreateRoot`/构造扩为可选参数（默认 null 保持 PREREQ-2 既有测试兼容）——`Views/Fluent/**` 在 FEA-06 写域内，DSH 只需动组合根一行；②卡 `allowed_paths` 增 `apps/desktop-avalonia/src/NewManga.App/App.axaml.cs` 并在 W-9 登记改动面限定（仅 Fluent 分支传参，禁改 V2/legacy 分支与 selector 语义）。两者均为最小改动，推荐 ①（组合根继续由 DSH 单点持有，与 `ShellCommands.cs` 先例一致） |

### 2.2 **P1（1 条，必须修）**

| ID | 位置 | 问题 | 建议（责任方） |
|---|---|---|---|
| **P1** | 卡 `:83-86`（AC2–AC5 状态括号）；`09-state-matrix.md:6-16`；`05 §3`/`06 §3`/`07 §3`/`08 §4` | **AC2–AC5 状态清单与 09 状态矩阵不一致，W-8「逐页写死 09 的具体状态集合」未兑现。** 逐页缺项：**AC2** 缺「满」（网格/列表+统计）；「未就绪」不是 09/05 术语（应为「只读」，05 §3「只读/旧壳运行」）。**AC3**「8 态」= 06 正文 §3，但 09 工作台列 9 行——缺「空（批量筛选无结果→保留 chips+清空选择）」（`09:9`）与「运行中（Run 投影条+暂停/停止/重试；intent key 复用）」（`09:16`）。**AC4** 括号 4 项缺「空（本章节暂无页面+返回）」「满」「部分/缺页（缺页占位『页面未就绪』+可重试；其余页可翻）」——referenced source 缺页是 AD-003 语义下的关键态。**AC5** 完全无状态清单，08 §4 的 空防御/载入骨架/满/部分（字段禁用+原因 Tooltip，Fluent 材质在 Current 下）/只读（保存禁用+警示）未绑定。机械验收时 Codex 按括号清单实现将系统性漏态，09 作为「AC1 的机械核对表」的用途落空 | DSH docs-only 修订卡（不动设计）：AC2 括号改为「空（首次）/空（筛选后）/载入/错误/满/部分（扫描中，含运行中同态）/只读」；AC3 改为「09 工作台列 9 行全部：空×2/载入/错误/满/部分未决/冲突/只读/运行中（Run 投影条+控制）」；AC4 补「空/满/部分（缺页占位+可重试）」；AC5 增「空（防御）/载入/满/部分（字段禁用+原因）/只读（保存禁用）」。或统一改写为「`09-state-matrix.md` 本页列全部行（含『—』除外）」并保留括号作导读 |

### 2.3 其余可执行性结论（通过项）

- **allowed_paths 足量性（除 P0 外）**：四页 View/ViewModel（`Views/**` 含 `Views/Fluent/FluentShell`、`ViewModels/**`）、外观层组件与样式（`Controls/**`、`Styles/**`、`DesignSystem/**`）、页面数据/导航适配器（`Services/**`）、快捷键注册表（`Shell/**` 含 `Shell/V2/ShellCommands.cs`/`KeyMap.cs`）、两侧测试目录、证据目录、治理三件套与 review/handoff——覆盖 P1–P7 所需；无关/过宽路径未见（`DesignSystem/**` 含生成器源与 `Generated/`，但 AC10 明令禁改生成物，属「写域宽 + AC 收窄」自洽结构）。
- **AC 逐条可机械验证**：AC1 令牌 `Nm.Size.TopBand/TreeWidth/StatusBandPage` 在 `NmKeys.g.cs:140-143` 在场；17 个带手势命令在 `ShellCommands.cs` Definitions 在场（全局 10 + StudioModeToggle + Library 对象导航 6 = 17，与 AC1「17」吻合）；断点 1024/1280/1600 与冻结令牌一致（04 §2「Medium」为行为区间不新增令牌）。AC3 映射按 category 归组与 17 码表吻合。AC6 组件名与 10 一致。AC7 三态/三类在 `MotionMode`/`MotionCategories` 枚举在场。AC8 基线 1022/0/57 与 PREREQ-2 集成验证一致。AC9/AC10 口径明确。
- **W-11 证据口径可执行**：`Avalonia.Headless.XUnit` 在 App.Tests 可用；headless 渲染截图（RenderTargetBitmap 抓取）可行；日志含命令与 exit 与既有 verification 惯例一致。
- **自洽性**：`base_commit` 为被审 head 直接父 ✓；`depends_on` 四项均 done ✓；owner=codex 与用户指派/STATUS/PLAN/checkpoint 四处一致 ✓；`reviewer: null` 待释放时由 DSH 指定（流程位）；禁止范围与 AC10 一致、与 C-02 V-05（Fluent 视觉令牌例外）、V-07（ThemeEngine 公开面不改——本卡不触 ThemeEngine ✓）、V-08b（进程级唯一快捷键注册表、两 frontend 映射一致——Shell/KeyMap 在写域、不改注册表结构 ✓）、C-03 §2.2（字段名与 `AppearanceSettings` 一致 ✓）、C-05（不新增 SpaceId/surface，与 W-6 一致 ✓）、AD-002 四页边界（W-6「不新增第五页」✓）无冲突。

---

## 3. P2（10 条，接受/建议）

| ID | 问题 | 建议 |
|---|---|---|
| P2-1 | P5 摘要漏列「深/浅（appearance）」「对比度（contrast）」两字段（在 08:41-58 验收范围内、`AppearanceSettings` 有承载） | 摘要补全，避免实现者误以为可略 |
| P2-2 | AC3「internal=错误页」与 06 设计「错误卡（画布保留上一帧，不清屏）」「flush 失败留旧 UI 不切换」措辞张力；r1 建议的「DRAFT_APPLY_FAILED 保留旧 UI 不切页」未吸收 | 映射表 internal 行补注「错误卡在位显示，保留旧 UI/上一帧，不清屏」 |
| P2-3 | W-6 未引 `07:3`（阅读器=`ReaderOverlay` 浮层不改 SpaceId）与 `08:3`（设置=ThemeStudio surface 承载外观组）两个映射锚点 | W-6 依据列补引，防实现者误把阅读器/设置做成空间 |
| P2-4 | 08:3「其余分组（Provider/网络/备份/关于）沿用既有设置 surface」在 Fluent 壳内的承载方式未裁（复用 V2 控件 vs 按 08 规格重实现） | 派发 brief 注明 DSH 口径（建议：按 08 §3 分组在 Fluent 设置页内实现，数据语义沿用既有 surface 契约） |
| P2-5 | `depends_on` 未列 FEA-04/FEA-05-WIRE-1（传递依赖成立，不阻塞） | 释放时补登或维持现状 |
| P2-6 | G-3 资产边界未声明：写域无 `Assets/**`，若 Fluent 需新图标/字体无落点且许可评估缺 | 卡禁止范围补一句「沿用 `NmIcon` 既有集合，不新增资产/字体；确需新增即停等 DSH」 |
| P2-7 | AC1「17 全局快捷键」措辞：实际 17 = 全局 10 + 空间级 7（Tab + J/K/[/]/Shift+[/]） | 改「17 个既有冻结快捷键」或注明明细，防验收争议 |
| P2-8 | 「缺令牌停等」未写明：W-7 隐含本卡不需新令牌，但若实现中发现缺口，AC10 禁改生成物与「继续实现」冲突 | 派发 brief 注明「发现令牌缺口 → 停等 DSH 裁决（v1.1 或生成任务），不得自行改 TokenMap/生成物」 |
| P2-9 | 实测现象记录：CoreClient.Tests 首跑 1 failed（时间敏感 flaky）、单独重跑 128/0/22 全绿；区间 docs-only 实证非回归 | Codex 采证遇单测失败先重跑归因再登记，勿直接判基线漂移 |
| P2-10 | 单卡体量仍大（四页+Shell+19 组件+动效+设置）且无交付顺序；双屏 G-4 归 FEA-07 未在卡内注明 deferral | 派发 brief 给建议顺序（P1 Shell→P6 组件→P2/P3→P4/P5）并注明 G-4 不在本卡；不拆卡 |

---

## 4. 治理与一致性

- `check.ps1` **PASS（3 warnings）**（9 非终态 Task 提示为既有口径；STATUS/PLAN 预算 80% 提示）；`verify_pins.ps1` **PASS（all 15）**——本轮在 `53060cd67` 复跑。
- 用户 owner 指派已四处落盘（卡 `approval`/`owner` + W-10、STATUS:7、PLAN:20、checkpoint §32），与 2026-10-25/10-31 裁决的 DSH 派发权、Codex 协作 Agent 定位一致；W-10「main 直接实现、单一 commit、不 push、DSH 保留 Review/集成/推送」与治理先例（PREREQ-1/2 同模式）一致。
- DAG/台账一致：PLAN:20/37、STATUS:7/10、LEDGER:45 均为 FEA-06 proposed（scope-r2 复核中）。
- 冻结契约冲突检查：C-02 V-05（材质/层次 per-scheme 例外——本卡只消费令牌 ✓）、V-07（ThemeEngine 公开面不在写域 ✓）、V-08b（KeyMap 单一注册表 + 上下文路由在 `Shell/**` 写域内可落 ✓）；C-03 §2.2 字段名与 `AppearanceSettings` 一致 ✓；C-05 不新增 SpaceId/surface ✓；AD-002 四页唯一 ✓；许可边界（无新依赖/资产）✓。

---

## 5. 边界声明

本报告只审**范围/可执行性/治理一致性**：不审设计数值本身（FEA-04b r5 approved 冻结）、不审未写的实现、未运行 UI 像素/交互验证；`check.ps1`/`verify_pins` 为只读参考，不替代审查。行号基于 `53060cd67` 实测。本席位未参与 FEA-06 起草/范围处置/实现，除本报告外未修改任何文件、未 commit/push。本报告不构成实现授权。

---

## 6. 结论

**FEA-06 尚不可按 W-10 直接释放 Codex 实施**：r1 的 P0×2/P1×7 中，P0-1、P1-1/P1-4/P1-5/P1-6/P1-7 已由 PREREQ-1/2 真实交付或 r2 卡修订实质闭环（本轮逐项实测通过），P0-2 的「壳可启动」半边已闭合；**但 r2-P0（Fluent 壳依赖注入通路断裂 + 组合根不在写域）使 AC2–AC5 的数据/命令/外观面在写域内无合法实现通路**，且 r2-P1（AC2–AC5 状态清单与 09 矩阵不一致）未兑现 W-8 的处置声明。两项修复均为**小改动**：P0 需 DSH 一处组合根传参（推荐 DSH 单点改 `App.axaml.cs:137` + 预扩 `FluentShell.CreateRoot` 可选参数）或授权写域扩张；P1 为 docs-only 卡修订。修完后无需重开全量范围复核，**增量复审（scope-r3，仅核 P0/P1 两项处置）通过即可置 `ready`**。

**实施前 DSH 还需做**（按序）：
1. 处置 r2-P0（组合根传参二选一，见 §2.1 建议①②）。
2. docs-only 修订卡处置 r2-P1（AC2–AC5 状态清单对齐 09 矩阵）。
3. 刷新 `base_commit` 至届时 main HEAD；`approval` 置 ready 口径；指定 reviewer。
4. 写派发 brief：P2-3/P2-4/P2-6/P2-8 的口径注记（映射锚点、设置页其余分组承载、资产边界、缺令牌停等）+ P2-10 交付顺序建议 + P2-9 flaky 归因提示；Codex 派发一律 `-m gpt-6-luna`、cwd=仓库根（checkpoint §32 既有结论）。
5. Codex 交付后：上下文独立实现复核 → DSH 集成验证（全量 + 两 `--check` + `check.ps1`/`verify_pins`）→ done。
