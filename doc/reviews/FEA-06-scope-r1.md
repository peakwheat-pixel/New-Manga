---
task_id: FEA-06
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: 1a844f681
reviewed_head: cad5ebde3
decision: changes_requested
counts: { P0: 2, P1: 7, P2: 11 }
---

# FEA-06 范围冻结复核 r1（独立上下文；本席位未参与本卡起草）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06.md`（`proposed`，Fluent UI 四页实现；`suggested_owner: dsh（Codex 通道故障、ZCode 未安装）`） |
| base_commit | `1a844f681dafb1f64006f583c32e24f1eb30e1a8`（设计基线冻结提交；`git merge-base --is-ancestor` 通过） |
| reviewed_head | `cad5ebde328fc614410803e1be5588823663cdcd`（`docs(fea-06): owner 改 dsh…`；上一提交 `82817726c` 建卡） |
| reviewer | `fea05-wire-scope-reviewer`（DSH 派发 fresh 子 agent；本任务**只读**，未参与 FEA-06 起草；此前仅复核过 FEA-05-WIRE-1/05-PORT-1（只读评审，未实现），与 FEA-06 无实现关系；符合 2026-10-31 上下文独立裁决） |
| 日期 | 2026-11-02 |
| 审查对象 | 范围充分性、可执行性、Draft 接入 W-2、写域、依赖与顺序（含 V2 关系）、治理 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 2 / P1 = 7 / P2 = 11（共 20）** |

> **一句话结论**：**changes_requested**。卡的方向（四页+Shell+设计系统消费、W-1…W-4 裁决）正确，但**尚不具备可执行条件**：①**C-03 外观持久化实现不存在**（`NewManga.Appearance`/`AppearanceCoordinator` 未创建，ThemeEngine 只有 `ReducedMotion` 布尔），AC5/AC6 的 `motion.mode`/`motion.categories`/`frontendId` 字段不可落；②**Fluent frontend 激活/切换与 V2 并存未裁决**，且组合根 `App.axaml.cs`（`AppShellV2` 唯一入口）、`Program.cs`、`NewManga.ThemeEngine/**` 不在写域——四页写出来也**不可被启动/选择**。此外设计基线冻结时登记的 **G-1/G-1b/G-1c 令牌生成被指派给已 done 的 FEA-05 而未交付**（`Nm.Focus.Ring.*`/`Nm.Corner.Fluent.*`/`Nm.Material.*`/`Nm.Elevation.*` 均缺），**AC2–AC5 未绑定 09 状态矩阵强制状态**，**AC3 typed error 映射表未冻结**，**P6 无 AC**，**AC1「四页 Tab」与设计的「三空间/左导航」冲突**，**PLAN/STATUS 指针仍把 FEA-04b 写成 in_review**。需 DSH 先做前置裁决/补前置任务/扩写域，再派 rev-r2。

---

## 0. 方法与只读声明

- 只读核查被审 head；**未修改卡/设计/代码**；`git status --porcelain` 为空；未 commit/push。本报告为本轮唯一新增文件。
- 本轮实测：`pwsh tools/governance/check.ps1` → **PASS（3 warnings：9 非终态；STATUS 3172B/39 行 80%；PLAN 3710B/55 行 80%）**；`verify_pins.ps1` → **PASS（all 15）**；`git merge-base --is-ancestor 1a844f681 HEAD` → 0。
- 阅读范围：`doc/tasks/FEA-06.md`（102 行）、`doc/design/fluent-v1/**`（11 文件）、`doc/tasks/FEA-04b.md`、`doc/tasks/FEA-05-PORT-1.md`、`verification/FEA-04b/design-baseline-selfcheck.md`、`doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md`、`doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md`、现有 `apps/desktop-avalonia/src/{NewManga.App,NewManga.DesignSystem,NewManga.ThemeEngine,NewManga.CoreClient}` 结构、`doc/STATUS.md`/`doc/REBASELINE_PLAN.md`/`doc/TASK_LEDGER.md`。

---

## 1. 六项必核查逐项

### 1.1 范围充分性（P1–P6 vs 设计基线全部章节）

卡 `FEA-06.md:49-56` 的 P1–P6 与 `doc/design/fluent-v1/` 的映射如下（✓=有对应任务；△=只有一行、无拆解/AC；✗=缺失）：

| 设计输入 | 覆盖任务 | 判定与缺口 |
|---|---|---|
| `README:11-56`（目标/索引/原则/检查点） | P6 | △ 原则与检查点未转成 AC |
| `01-design-tokens.md`（令牌取值/裸值禁令） | P6 | △ 令牌**绑定**有，**生成**无（G-1/G-1b/G-1c，见 P1-1）；AC2 只写 `Nm.Color.*`/`Nm.Size.*`，未含 `Corner.Fluent.*`/`Material.*`/`Elevation.*` |
| `02-motion.md`（三态×三类） | P6 | △ 仅 AC6 一句；`motion.mode` 三态/`categories` 依赖不存在的 C-03 实现（P0-1） |
| `03-accessibility.md`（键位/焦点/高对比/SR） | P1/AC6 | ✓ 大体覆盖（17 全局键已在 `ShellCommands.cs:8-26` 存在）；焦点环三键缺失（P1-1） |
| `04-layout-responsive.md`（骨架/断点/折叠/双屏/DPI/z-order） | P1/AC1 | △ AC1 只有断点+z-order；§3 分栏折叠、§4 双屏（G-4 归 FEA-07，`selfcheck:37`）、§5 DPI 未写（P2-4） |
| `05-page-shelf.md` | P2/AC2 | △ 状态不全（P1-2）、交互（`05:50-53` 选择/右键/拖入/回收站）未进 AC |
| `06-page-workbench.md` | P3/AC3 | △ **状态完全未写**（`06:44-51` 八态，P1-2）；交互（`06:55-59`）只以"+"带过 |
| `07-page-reader.md` | P4/AC4 | △ 状态未写（P1-2）；交互（`07:50-53` 翻页/缩放/全屏/方向 memento）不全（P2-5） |
| `08-page-settings.md` | P5/AC5 | △ 字段范围不清（P1-6）、状态不全（P1-2） |
| `09-state-matrix.md` | P6 | ✗ **无 AC 绑定**（P1-2） |
| `10-component-inventory.md` | P6 | ✗ **无 AC/无组件拆解**（P1-4） |

**遗漏页/状态**：卡无遗漏四页本身；缺页面**空/载入/错误/未就绪/部分/冲突/只读/运行中**的逐页验收（`09:6-16` 已给出唯一清单）。另缺 FEA-04b 冻结时登记的 **G-1/G-1b/G-1c 缺口承接**（`selfcheck:28-37`），以及 FEA-04b 复核遗留的「四页预览」未处置（`doc/reviews/FEA-04b-scope-r4.md:54` 记 R3-P2-15 未关闭）。

### 1.2 可执行性（AC1–AC8 可机械验收？工作量/依赖？）

- **AC1**（`:60`）：17 快捷键可对照 `ShellCommands.cs:8-26`+`KeyMap` 机械核对 ✓；但「四页 Tab 顺序」与设计冲突（P1-5），且激活方式未定（P0-2）。
- **AC2**（`:61`）：状态/令牌可写成 Headless 断言（`Avalonia.Headless.XUnit` 已在 `App.Tests/AssemblyInfo.cs:1` 可用 ✓）；但 Fluent 令牌组缺失（P1-1）、状态缺项（P1-2）。
- **AC3**（`:62`）：组件+「typed error 映射到 UI 状态」**无映射表** → 不可机械验收（P1-3）；Workbench 状态缺失（P1-2）。
- **AC4**（`:63`）：`IReaderProgressSink` 存在（`IHostController.cs:104`）✓ 可机械；状态/交互缺（P1-2/P2-5）。
- **AC5**（`:64`）：**不可执行**——`C-03 §2.2` 所需持久化层不存在（P0-1），且字段范围未列全（P1-6）。
- **AC6**（`:65`）：焦点顺序/SR 名称可测（`03:42-70`）✓；焦点环令牌缺失（P1-1）、motion 三态依赖 C-03（P0-1）。
- **AC7**（`:66`）：可执行；基线 949/0/57 与当前实测一致 ✓。
- **AC8**（`:67`）：仅泛化证据表，无采证方法/标准（P2-6）。
- **工作量/依赖**：四页 + Shell + `10` 清单约 34 个组件（布局 10 + 数据 12 + 交互 12）（新增/外观化 ~15-20，见 P1-4）+ 动效 + 设置，单卡无分期/里程碑；且需先补 3 类前置（C-03 实现、令牌生成、frontend 激活）。**结论：当前范围过大且前置未就绪**（P2-9）。

### 1.3 Draft 接入（W-2，`FEA-06.md:79`）

- W-2 只写「经 `IHostController`，typed error（`DraftError` code/category）映射到 UI 状态」；AC3 只要求「含 typed error 映射」——**没有错误码→UI 状态/动作的映射表**（P1-3）。
- 实际错误面：`HostController` 7 方法（`HostController.cs:2218-2378`）不捕获异常；Core 错误由 `CoreServiceClient.SendAsync` 转成 `CoreOperationException(Code, Category, Retryable, Message, RequestId)`（`CoreServiceClient.cs:1437-1439`；`CoreProtocol.cs:128-149`）。既有先例：`HostController.ErrorCodeOf`（`:2107-2116`）、`UserMessageOf`（`:2118-2126`）、`RegionOperationResult.Failed(ErrorCodeOf(ex), …)`（`:628/665`）。
- 契约已冻结 17 码 × category/retryable（`FEA-05_DRAFT_WIRE_CONTRACT.md:41-63`：`DRAFT_INVALID`/`DRAFT_PATCH_INVALID`/`DRAFT_CANDIDATE_INVALID`/`EDIT_TOKEN_INVALID`/`DRAFT_NOT_FOUND`/`DRAFT_READ_ONLY`/`EDIT_TOKEN_EXPIRED`/`EDIT_TOKEN_REUSED`/`DRAFT_JOURNAL_UNWRITABLE`/`DRAFT_APPLY_FAILED`…）。
- **建议**：在卡内冻结「code/category→Workbench 状态」表（如 validation→字段级/操作禁用+文案；not_found→空态+刷新；conflict→冲突条/只读（`06:50-51`）；unavailable+retryable→错误卡+重试；internal→错误卡+控制台入口），并写明 `Retryable` 语义与 `DRAFT_APPLY_FAILED` 的"保留旧 UI 不切页"（`06:56-57`）。否则 AC3 与 UI 状态可能随实现漂移。

### 1.4 写域审计（`FEA-06.md:22-35`）

| 需要的改动点 | 是否在 allowed_paths | 说明 |
|---|---|---|
| 四页 View/ViewModel（新 `Views/Fluent/**`、`ViewModels/Fluent/**`） | ✓ `Views/**`、`ViewModels/**` | 可写；但卡未说明与 `Views/V2/**`、`ViewModels/V2/**` 的复用/隔离（P1-5） |
| Shell | ✓ `Shell/**` | 含 `Shell/V2/ShellCommands.cs`；但 `03:25` 要求该共享文件由 **DSH 单点提交**（P2-3 需注明） |
| 设计系统令牌/外观层组件 | ✓ `NewManga.DesignSystem/**` | 可写；`Tokens/TokenGenerator.cs`/`TokenDictionaryWriter.cs` 在内 ✓（P1-1 可放此处生成） |
| 导航注入 | △ `Services/IPageNavigation*.cs` | **该模式在仓库不存在**（`git grep` 无匹配；导航在 `Shell/V2/AppShellV2`/`ShellState`）→ 死路径（P2-2） |
| 组合根/程序入口（前端注册/切换、DI、`AppShellV2.CreateRoot` 分支） | ✗ | `App.axaml.cs:96` 无条件创建 `AppShellV2`；`Program.cs`/`AppOptions.cs`/`AssemblyInfo.cs`/`App.axaml` 均不在写域（P0-2、P2-1） |
| 主题/动效/外观持久化 | ✗ | `NewManga.ThemeEngine/**`（`ThemeSettingsJson` 只有 `reducedMotion` bool，`:79/:118`；`ThemeContracts.cs:35`）、`NewManga.Theme/**`、`NewManga.Appearance`（不存在）均不可写（P0-1、P2-1） |
| 样式资源 | ✗ | `NewManga.App/Styles/**` 不在写域（若 Fluent 需样式覆盖）P2-1 |
| 图标/字体资产 | ✗ | `Assets/**` 不存/不在写域；G-3 新资产与许可归 FEA-05（P2-7） |
| 测试 | △ | `App.Tests/**`、`DesignSystem.Tests/**` ✓；若改 ThemeEngine 需 `ThemeEngine.Tests`（不可写）P2-1 |
| 依赖/项目文件 | ✗ | 若新增包/项目（`Directory.Packages.props`、`NewManga.sln`）不可写 P2-1 |

**结论**：写域覆盖了"页面层"，但**未覆盖使其可运行/可切换/可持久化的三处关键边界**（组合根、ThemeEngine/Appearance、样式/资产）；且含一个不存在的 glob。

### 1.5 依赖与顺序（含与 FEA-04/V2 的关系）

- `depends_on`（`:11-13`）= FEA-04b + FEA-05-PORT-1：两者**实际状态均为 done**（`doc/tasks/FEA-04b.md:6`；`doc/tasks/FEA-05-PORT-1.md` `status: done`），依赖成立 ✓；但 **PLAN/STATUS 仍把 FEA-04b 写成 `in_review`**（见 1.6/P1-7）。
- **缺依赖**：C-03 外观持久化实现（`NewManga.Appearance`/`AppearanceCoordinator`）无任务、无卡；设计令牌生成（G-1/G-1b/G-1c）原指派 FEA-05（已 done 未交付）；frontend 激活/切换机制无任务；G-3 资产/许可无承接。
- **与 FEA-04/V2 的关系（重点，卡未写）**：设计明确 `builtin.current-v2` 与 `builtin.fluent` **并存**（`README:7`；`01:77-78`），但现有实现只有 Current V2 壳：`Views/V2/**`（Library/Console/Shell 浮层）、`ViewModels/V2/**`（Library/Console/Shell/Studio/ThemeStudio）、`Shell/V2/AppShellV2`，无 `frontendId` 选择、无 `FluentFrontend`、无第二个 shell 入口（`git grep builtin.fluent` 仅设计文档命中）。**四页是"另建 Fluent 前端"，还是"替换/复用 V2 页面"，卡内没有裁决**；写域虽含 `Views/**`/`ViewModels/**`，但若改 `Views/V2/**` 会触碰 Current 基线（设计 `README:18` 声明不替换 Current）。
- **建议前置裁决 W-5**：①Fluent frontend 的注册/激活/切换归属与入口（并是否回退 Current）；②四页与 V2 三空间/阅读器浮层/设置页的映射与复用边界（哪些 V2 ViewModel 可复用什么必须隔离）；③`ShellCommands.cs`/`AppShellV2` 的修改授权（DSH 单点提交）。

### 1.6 治理

- `check.ps1` **PASS（3 warnings）**；`verify_pins` **15/15**；`base_commit` 为 HEAD 祖先 ✓。
- **指针不一致（P1-7）**：`doc/REBASELINE_PLAN.md:17` 写 FEA-04b **in_review**（"独立复核 r1→r2"）而 `:35` 写 **done**——同一文件自相矛盾；`doc/STATUS.md:7` 仍"FEA-04b in_review；上一 FEA-04b in_review（r5 approved，AC5 待确认）"、`:10`"下一候选：FEA-04b…；FEA-05-PORT-1 待建卡"均为陈旧值（实际：FEA-04b done；FEA-05-PORT-1 done；当前 FEA-06 proposed）。`doc/TASK_LEDGER.md:45` FEA-06 proposed ✓ 一致。
- `suggested_owner: dsh（Codex 通道故障、ZCode 未安装）`（`:8`）：与角色/故障转移口径需对齐——`doc/09_COLLABORATION.md:17` 规定 ZCode 为 UI/UX 与 GUI 视觉/交互实现主责；AGENTS 2026-10-08 规定故障转移候选仅 ZCode；2026-10-25 授权 DSH 负责任务释放/分配。DSH 接管可实现（子 agent 独立复核满足独立性），但卡内应把"为何 dsh 而非 zcode"写成裁决记录（并注明 ZCode 可用时交接），当前只有提交信息（P2-3）。
- AC7 基线 949/0/57 与当前实测一致 ✓；AC8 证据目录/命名合规 ✓（泛化问题见 P2-6）。

---

## 2. Findings

### P0（2 条，阻塞范围冻结）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| **P0-1** | 卡 `:11-13`（depends_on）、`:22-35`（allowed_paths）、`:64`（AC5）、`:65`（AC6）；`doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md:28,32-44,68`；`apps/desktop-avalonia/src`（无 `NewManga.Appearance`）；`NewManga.ThemeEngine/Serialization/ThemeSettingsJson.cs:79,118`；`NewManga.ThemeEngine/Models/ThemeContracts.cs:35`；`08-page-settings.md:45-54` | **C-03 外观持久化实现不存在，AC5/AC6 不可执行。** C-03 冻结草案要求新建 `NewManga.Appearance` 项目 + `AppearanceCoordinator` 写 `presentation-settings.json`、ThemeEngine 只作 sink；实际仓库无此项目；ThemeEngine 只有 `ThemeSettings(ThemeId, Appearance, Contrast, LayoutProfile, ReducedMotion, FollowSystemAccent)`（C-03:18 引 `ThemeModels.cs:349-355`），缺 `motion.mode` 三态/`motion.categories`/`frontendId`/`visualThemeId` 持久化、`corners`/`material`、`schemaVersion`，也没有 `AppearanceCoordinator`/`presentation-settings.json`（`ThemeContracts.cs:35` 仅 `SetReducedMotionAsync(bool)`）。卡依赖只列 FEA-04b/FEA-05-PORT-1，写域也不含 Appearance/ThemeEngine/项目文件 → AC5（C-03 §2.2 字段保存/校验/错误态）不可执行；AC6 的 `motion.categories=off`/三态降级不可执行（其余 a11y 项可） | 二选一：①新增前置任务（C-03 实现）并把 FEA-06 `depends_on` 加上它；②把 C-03 实现纳入 FEA-06 并扩写域（`NewManga.Appearance/**`、`NewManga.ThemeEngine/**`、`Directory.Packages.props`、`.sln`），同卡声明 `AppearanceCoordinator` 唯一写者与迁移顺序（C-03:68/72）。推荐① |
| **P0-2** | 卡 `:22-35`（写域）、`:47-56`（P1）、`:60`（AC1）；`apps/desktop-avalonia/src/NewManga.App/App.axaml.cs:96,160`；`doc/design/fluent-v1/README.md:7`、`01-design-tokens.md:77-78`；`03-accessibility.md:25` | **Fluent frontend 的注册/激活/切换与 V2 并存未裁决，且组合根不在写域 → 四页不可被启动/选择。** 设计限定 Fluent 仅在 `theme.frontendId=builtin.fluent` + `visualThemeId=builtin.fluent-dark` 生效、Current V2 不受影响；但代码中无 `frontendId`/`FluentFrontend`/双壳入口，`App.axaml.cs:96` 无条件 `AppShellV2.CreateRoot(...)`，`App.axaml.cs:160` 另一入口也是 `MainWindow`；而 `App.axaml.cs`/`Program.cs`/`AppOptions.cs`/`NewManga.ThemeEngine/**`（视觉主题注册）均不在 `allowed_paths`。另 `ShellCommands.cs` 按 `03:25` 属 DSH 单点提交，卡未注明 | 在卡内先做 **W-5 裁决**：①`builtin.fluent` 的注册/激活/切换入口（含默认值、回退 Current、设置页字段来源）；②与 `builtin.current-v2` 并存的边界与 V2 文件禁改清单；③补写域（组合根/主题注册）或明确"激活由后续任务承担、本卡只交页面并由 Headless 测试验证"。未裁决前 AC1/AC2–AC6 的产品可达性无证据 |

### P1（7 条，必须修）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| **P1-1** | 卡 `:56`（P6）、`:61`（AC2）、`:65`（AC6）；`verification/FEA-04b/design-baseline-selfcheck.md:28-37`（G-1/G-1b/G-1c）；`01-design-tokens.md:13,18,22`；`03-accessibility.md:53`；`06-page-workbench.md:37`；`NmKeys.g.cs`（无 `Nm.Focus.Ring.*`/`Nm.Corner.Fluent.*`/`Nm.Material.*`/`Nm.Elevation.*`）；`Tokens.Global.axaml`（同缺） | **G-1/G-1b/G-1c 令牌生成无承接。** 设计明确这三组缺口由 **FEA-05 生成/登记或 DSH 裁决**；FEA-05-WIRE-1/PORT-1 已 done 且其写域不含令牌生成，仓库至今无这些键。FEA-06 卡 P6 只写"令牌绑定"，AC2 只列 `Nm.Color.*`/`Nm.Size.*`；`ThemeEngine/Models/ThemeTokenKeys.cs` 白名单不在写域。→ AC2/AC3（`Corner.Fluent.*`/`Material.*`/`Elevation.*`）与 AC6（焦点环 2px/1px）不可机械满足 | 在卡内新增 P7/AC：生成 G-1 三组 + G-1c 三键 + 登记 G-1b 列宽常量 96（`01:22`/`06:37`），写明生成器入口（`NewManga.DesignSystem/Tokens/TokenGenerator.cs`/`TokenDictionaryWriter.cs`）、回归（`NmKeys.g.cs`/`Tokens.Global.axaml`/ThemeTokenKeys 白名单同步）；或建前置任务并在 `depends_on` 登记。AC2 令牌名改为引用 `01 §2/§3` 分组表 |
| **P1-2** | 卡 `:61-64`（AC2–AC5）；`09-state-matrix.md:6-16`；`README.md:52-56`；`05:36-47`；`06:40-51`；`07:37-46`；`08:62-71` | **AC2–AC5 未绑定 09 状态矩阵强制状态。** AC2 缺「空（筛选后）/部分（扫描中）/只读（运行中）」；AC3 **无任何状态**（缺 空×2/载入/错误/满/部分未决/冲突/只读）；AC4 无状态（缺 空/载入/错误/满/部分缺页/只读）；AC5 只有错误态（缺 空/载入/满/部分/只读）。设计 README 评审检查点要求"四页各含全部状态"，当前 AC 无法机械验收 | 每页 AC 改为引用 `09` 对应列（如 AC3 增"空/载入/错误/满/部分未决/冲突/只读八态与 `06 §3` 表现一致，含恢复路径"），并给 Headless 断言点（状态切换/文案/按钮可用性） |
| **P1-3** | 卡 `:62`（AC3）、`:79`（W-2）；`FEA-05_DRAFT_WIRE_CONTRACT.md:41-63`；`HostController.cs:2107-2126`；`CoreServiceClient.cs:1437-1439`；`CoreProtocol.cs:128-149` | **AC3 的 typed error 映射无冻结表。** W-2 仅一句"映射到 UI 状态"；实际 C# 面是 `CoreOperationException.Code/Category/Retryable`（17 码已冻结），但没有任何 code→状态/动作的验收映射。不同实现会给出不同 banner/禁用/重试行为，AC3 不可机械验收 | 卡内冻结映射表：17 码 → Workbench UI 状态（字段级/操作禁用/错误卡/冲突条/只读/未决确认）+ 重试动作 + 文案来源；引用 `ErrorCodeOf/UserMessageOf` 既有先例；`DRAFT_APPLY_FAILED` 等按 `06:56-57` 明确"保留旧 UI 不切页" |
| **P1-4** | 卡 `:56`（P6）、`:65`（AC6）；`10-component-inventory.md:6-53`（约 34 组件：布局 10、数据 12、交互 12）；`NewManga.DesignSystem/Controls/*` | **P6 只有一行且无 AC：令牌绑定/动效三态/状态矩阵/组件清单均无验收标准。** 既有 DS 控件覆盖部分（`TopBand/Drawer/Modal/EmptyState/AlertBanner/StatusBadge/Chip/Kbd/SegmentedControl/SearchField/Skeleton/StatusGlyph`），`NavRail/StatusBand/SurfaceCard/Toast/ErrorState/BookCard/BatchMatrix/RegionBox/ReaderPage/SettingsGroup/SettingsField` 等需新增或外观化。卡未拆组件任务、未列"复用/新增"映射 | 把 P6 拆成 P7「设计系统外观层组件」并给 AC（`10 §5` 检查点：每组件令牌依赖无裸值、状态完整、不复制业务组件、与四页正文一致）；列出新增组件清单与既有复用映射 |
| **P1-5** | 卡 `:60`（AC1「四页 Tab 顺序」）；`04-layout-responsive.md:13`（TopBand 空间 1/2/3）、`:31-34`；`03-accessibility.md:12-13,44`（空间切换/左导航空间列表）；`05-page-shelf.md:21`（左导航=书架/回收站/导入）；`06:46`（顶部 Tab 条） | **AC1「四页 Tab 顺序」与设计的三空间/左导航自相矛盾，不可机械验收。** 设计骨架的顶部命令条是"空间 1/2/3"（`04:13`），全局键也按空间切（`03:12-13`），而产品四页是 书架/工作台/阅读器/设置（`09:6`），书架左导航又是 书架/回收站/导入（`05:21`）。冻结基线未给四页与空间/Tab 的映射，卡直接写"四页 Tab 顺序" | 卡内新增 W 裁决：四页 ↔ 三空间 ↔ 顶部/左导航/Tab 的映射（哪些是空间、哪些是页内 Tab、阅读器是否为浮层）；若需改设计数值则按 README §4 走 v1.1 重冻结。AC1 改为引用冻结后的映射表 |
| **P1-6** | 卡 `:64`（AC5）；`08-page-settings.md:41-58` | **AC5 字段范围不完整/不清。** `08:41-58` 冻结清单含 frontend/`visualThemeId`（C-02）、`motion.mode`/`categories`、`corners`/`material`、`layout.*`、`followSystemAccent`、`schemaVersion`，以及 Provider/凭据、网络、备份恢复（C-09/ADJ-001）、关于；AC5 只写"C-03 §2.2 字段"，漏 frontend/visualTheme 与宿主组，也未声明哪些组延后/由其他任务承担 | 把 AC5 拆成"外观组（C-02/C-03 字段，逐字段列出）"与"宿主组（Provider/网络/备份/关于；标注依赖任务或本卡只读展示）"；引用 `08 §3` 冻结清单逐项核对（保存/校验/错误态） |
| **P1-7** | `doc/REBASELINE_PLAN.md:17,35`；`doc/STATUS.md:7,10`；`doc/tasks/FEA-04b.md:6`；`doc/tasks/FEA-05-PORT-1.md`（status done） | **治理指针不一致。** PLAN `:17` FEA-04b 仍 `in_review`（"独立复核 r1→r2"）而 `:35` 写 `done`；STATUS `:7` 仍"FEA-04b in_review / AC5 待确认"、`:10`"下一候选：FEA-04b…；FEA-05-PORT-1 待建卡"；实际两卡均 done（FEA-04b 于 `1a844f681` 冻结收口，AC5 以 DSH 裁决替代）。`check.ps1` PASS 不校验此一致性 | DSH 在释放 FEA-06 前同步 PLAN/STATUS（FEA-04b→done、FEA-05-PORT-1→done、下一候选=FEA-06/后续），使依赖证据自洽；再跑 check.ps1 |

### P2（11 条，接受/建议）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| P2-1 | 卡 `:22-35` | 写域缺口：组合根/入口（`App.axaml.cs`/`Program.cs`/`AppOptions.cs`/`AssemblyInfo.cs`）、`NewManga.App/Styles/**`、`NewManga.ThemeEngine/**`、`NewManga.Theme/**`、`Assets/**`、`tests/NewManga.ThemeEngine.Tests/**`、`Directory.Packages.props`/`NewManga.sln`（若加项目/包） | 按 P0-1/P0-2 裁决结果补写域；至少加 `Styles/**` 与（若生成令牌需改白名单）ThemeEngine 相应文件 |
| P2-2 | 卡 `:27` | `Services/IPageNavigation*.cs` **在仓库不存在**（grep 无匹配；导航实际在 `Shell/V2/AppShellV2`/`ShellState`）→ 死路径 | 删除或替换为实际导航注入点（`Shell/**` 已覆盖） |
| P2-3 | 卡 `:8`；`doc/09_COLLABORATION.md:17`；AGENTS 2026-10-08/10-25 裁决 | `suggested_owner: dsh（Codex 通道故障、ZCode 未安装）` 与角色/故障转移口径不完全一致（ZCode 是 UI/UX 与 Avalonia 视觉/交互实现主责；故障转移候选仅 ZCode）。DSH 接管有 2026-10-25 授权且可用子 agent 独立复核，但卡内未记录该裁决与 ZCode 可用时交接 | 字段保持枚举语义（`zcode`）或增加 W 项记录 DSH 接管依据/交接条件；中文括注改为正文裁决行 |
| P2-4 | 卡 `:60`（AC1）；`04:40-68`；`selfcheck:37`（G-4） | AC1 未覆盖 04 §3 分栏折叠/§4 双屏/§5 DPI；G-4 双屏明确"FEA-07 实现时按 04 §4 扩展"，卡未注明 deferral | AC1 增 04 §3/§6 引用并注明 G-4 不在本卡（归 FEA-07），DPI 125/150/200% 作为验收点 |
| P2-5 | 卡 `:63`（AC4）；`07:48-55` | AC4 未覆盖 Reader 交互细节：翻页（←/→/PgUp/PgDn/滚轮/点击）、缩放（+/-/0/Ctrl+滚轮）、全屏 F/Esc、单页/双页方向、UI memento S4 | AC4 补 07 §4 逐项与 memento 状态保存 |
| P2-6 | 卡 `:66-67`（AC7/AC8） | AC7 基线 949/0/57 ✓（实测一致），但"新增用例数"未量化；AC8 仅"截图/日志"泛化，无采证命令/标准（Headless 断言 vs 截图） | AC7 写明新增用例数下限与 Headless 命令；AC8 每 AC 指定证据类型（测试名/截图/日志片段） |
| P2-7 | `selfcheck:36`（G-3）；`10:4`；AGENTS 许可边界 | G-3 设计资产（图标/字体）未产出、许可评估原归 FEA-05（done）；FEA-06 写域无 `Assets/**`。若 Fluent 需要新图标/字体，无落点 | 卡内声明"沿用 `NmIcon` 既有集合、不新增资产"或补资产任务+许可评估 |
| P2-8 | `doc/tasks/FEA-04b.md:113-123`；`selfcheck:35`（G-2） | G-2（用户确认 AC5）已由 FEA-04b Closeout 以 DSH 裁决（Q-23）关闭，但 FEA-06 卡未引用该依据，设计输入有效性链不完整 | 卡"来源与授权链"补一句：FEA-04b done（AC5 以 DSH 裁决替代，见其 Closeout） |
| P2-9 | 卡 `:47-56` | 工作量/分期：四页+Shell+~15-20 组件+动效+设置单卡无里程碑/交付边界 | 拆分为"P1 Shell+设计系统外观层+令牌/组件"与"P2 四页"，或声明首版范围（如四页骨架+关键状态，细交互归后续） |
| P2-10 | `README.md:48` vs 卡 `:78`（W-1） | 偏差登记口径不一致：README 允许"实现偏差在 Task 登记并重走复核"，W-1 要求"偏差须走 v1.1 修订" | 统一为 README §4 流程（MINOR/PATCH 判定+v1.1 重冻结），卡内引用 |
| P2-11 | 卡 `:11-13` | `depends_on` 未列 FEA-04（done；AC4 的 `IReaderProgressSink` 与 Workbench 语义来自 FEA-04/FEA-03）与前置任务号（C-03 实现、令牌生成、frontend 激活） | 补 FEA-04（done）；前置任务以"待 DSH 建卡/裁决"登记并加入依赖 |

---

## 3. AC 逐项（可机械验收？）

| AC | 判定 | 说明 |
|---|---|---|
| AC1（`:60`） | **部分可机械** | 17 快捷键可对照 `ShellCommands.cs:8-26`+`KeyMap` ✓；断点/z-order 可测；但「四页 Tab 顺序」歧义（P1-5）、激活未定（P0-2）、04 §3-5 缺（P2-4） |
| AC2（`:61`） | **部分可机械** | 状态/令牌可写 Headless 断言（依赖已有 ✓）；状态缺项（P1-2）、Fluent 令牌组缺失（P1-1） |
| AC3（`:62`） | **不可机械** | 错误映射无表（P1-3）；Workbench 状态缺（P1-2）；组件清单无 AC（P1-4） |
| AC4（`:63`） | **部分可机械** | `IReaderProgressSink` 存在 ✓；状态缺（P1-2）、交互细节缺（P2-5） |
| AC5（`:64`） | **不可执行** | C-03 实现缺失（P0-1）、字段范围不清（P1-6） |
| AC6（`:65`） | **部分可机械** | 焦点顺序/SR 名称可测（`03:42-70`）✓；焦点环令牌缺失（P1-1）、motion 三态依赖 C-03（P0-1） |
| AC7（`:66`） | **可执行** | 基线 949/0/57 与当前实测一致 ✓；新增用例数需量化（P2-6） |
| AC8（`:67`） | **部分** | 目录/命名合规 ✓；采证标准泛化（P2-6） |

---

## 4. 处置建议（按序）

1. **P0 前置裁决（DSH）**：①决定 C-03 实现归属（新前置任务 vs 纳入 FEA-06 + 扩写域/依赖）；②裁决 W-5（Fluent frontend 激活/切换、与 `builtin.current-v2` 边界、组合根/主题注册写权）；③裁决 P1-5（四页↔三空间↔左导航/Tab 映射，必要时 design v1.1 重冻结）。
2. **P1 补齐**：G-1/G-1b/G-1c 令牌生成任务+AC（P1-1）；逐页状态 AC（P1-2）；Draft 错误映射表（P1-3）；P6 组件拆解+AC（P1-4）；AC5 字段清单（P1-6）；同步 PLAN/STATUS（P1-7）。
3. **P2**：按表逐项并入（写域/死路径/owner 记录/AC 细化/分期）。
4. 修完派 **rev-r2**（独立上下文）；P0/P1=0 后由 DSH 冻结范围、设 owner/reviewer，再释放实现。

## 5. 边界声明

本报告只审**范围/卡/设计基线一致性/可执行性**，不审设计数值本身（FEA-04b 已 r5 approved 冻结）与代码实现；未运行 UI、未做像素/交互验证。`check.ps1`/`verify_pins` 结果为只读参考，不能替代审查。本席位未参与 FEA-06 起草或实现，未修改被审文件、未 commit/push；行号基于 `cad5ebde3` 实测。
