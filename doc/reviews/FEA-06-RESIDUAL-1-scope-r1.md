---
task_id: FEA-06-RESIDUAL-1
reviewer: Codex CLI（fresh independent scope review r1；model gpt-6.1-sol, reasoning effort high）
reviewer_kind: agent
author: DSH
base_commit: 82529a3d5864a39f362e414b67bca774d743f862
reviewed_head: 0e52c9daa
decision: changes_requested
counts:
  P0: 0
  P1: 3
  P2: 3
---

# FEA-06-RESIDUAL-1 scope-r1 范围冻结复核

## Reviewer 身份、来源与边界

本报告由用户本轮指定的 fresh Codex CLI 独立上下文完成，未参与本卡范围编制，未参与本轮实现或返修；来源为本轮委派及 rolling checkpoint `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md:526-532`。未派发子 agent，不虚构会话 ID。DSH 为 Lead / Architect / Integrator，保留 Appointment、findings 处置、范围冻结和集成权。本报告是 scope review，不是实现验收或实施授权。

使用 `code-review` 技能的固定点与来源核对方法；按仓库协作协议 §6 对技能的明确覆盖，由本独立会话完成。Architecture / Verification / Standards / Spec 均为 executed；对象是第一批范围及其可实施性，不以代码 smell 为本轮阻塞项。用户已准确使用技术术语，无需额外术语教学。

唯一主动编辑/交付文件为本报告。未修改源码、测试、Task、状态、契约、设计、用户数据；未 commit/push，未进入其他 worktree，未启动连接真实数据的产品，未主动写真实 `%APPDATA%`。按要求运行的 build/test 产生常规构建输出与测试夹具。须披露：既有 `FluentPageTests.cs:240-278` 的 PNG 用例会重新写 `verification/FEA-06/screens` 四张图；本轮运行后 Git 无内容漂移，未手工恢复或更新旧证据。不能据此声称这套测试没有文件写入副作用，见 S-005。

以下 Task 行号均指 `doc/tasks/FEA-06-RESIDUAL-1.md`；App 源码简称相对 `apps/desktop-avalonia/src/NewManga.App/`；DS 相对 `apps/desktop-avalonia/src/NewManga.DesignSystem/`；所有引用行号以被审 `0e52c9daa` 为准。

## 范围与 Reality Check

- 仓库：`G:\CODEX\New Manga`；branch=`main`；common directory=`.git`。实际完整 HEAD=`0e52c9daab372f83edcd1bae2030f8bb98754771`。起始及必跑检查结束后 `git status --short` 均为空；恢复判断 **RESUME_SAFE**。
- 实跑 `git rev-parse HEAD`、`git status --short`、`git log --oneline -10`、`git diff --stat b26840acd..HEAD`、`git diff --name-only b26840acd..HEAD`，均 exit 0。累计 **104 files changed / 10980 insertions(+) / 570 deletions(-)**，包括 FEA-07 Presentation 项目、稳定主窗、内容树切换、退出/输入状态、Fluent surface 拆出及测试/治理/证据。
- `git diff --quiet aedc7251c HEAD -- apps/desktop-avalonia` exit 0：FEA-07 集成后应用代码未漂移。`82529a3d5..HEAD` 仅 5 个治理文档（Task、STATUS、PLAN、LEDGER、checkpoint），+38/-20；base 是当前 HEAD 的直接前序，代码基线充分，无须仅因 scope 文档提交刷新代码 base。
- 最近十个提交依次为 `0e52c9daa`、`82529a3d5`、`cb1a4bede`、`527a7ec37`、`91de6a345`、`ebda36be9`、`563f248c7`、`aedc7251c`、`b6b63574d`、`462141f57`。前七项为范围、Review/处置、集成/指针文档；代码返修位于 `aedc7251c`、`462141f57`。
- 已读 AD-002 当前边界、STATUS、PLAN 当前 DAG、checkpoint 当前释放段、协作协议 §4/§5.1/§6、Review 模板；按 Task 引用读取 FEA-06/07 Task、最新源 Review、集成/最终证据及本轮指定设计和实际调用链。未扫描历史 verification 或其他 worktree。

实跑时间：2026-11-02（Asia/Shanghai）；shell=`C:\Program Files\PowerShell\7\pwsh.exe`；SDK=`10.0.401`，项目及测试目标为 `net9.0`。下表为本轮执行记录，未另建日志文件，以遵守单文件写入约束；工具会话保留原始输出。

| 检查/实际命令 | EXIT | 本轮结果 |
|---|---:|---|
| `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | 0 | PASS；0 warnings / 0 errors |
| `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings` | 0 | PASS；**1138 passed / 0 failed / 57 skipped** |
| `dotnet run --project apps/desktop-avalonia/src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen -- --check` | 0 | PASS；292 rows；every generated artifact matches the frozen token source byte-for-byte |
| `dotnet run --project apps/desktop-avalonia/src/NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen -- --check` | 0 | PASS；generated theme artifacts match the frozen token source byte-for-byte |
| `pwsh -NoProfile -File tools/governance/check.ps1` | 0 | PASS，3 warnings：9 个非终态 Task；STATUS/PLAN 达 80% 预算 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 0 | PASS，all 15 |

| 测试程序集 | passed | failed | skipped |
|---|---:|---:|---:|
| Appearance | 21 | 0 | 0 |
| ApplicationCore | 31 | 0 | 0 |
| CoreClient | 128 | 0 | 22 |
| Host | 51 | 0 | 28 |
| DesignSystem | 87 | 0 | 0 |
| ThemeEngine | 253 | 0 | 0 |
| App | 529 | 0 | 7 |
| Presentation.Avalonia | 38 | 0 | 0 |
| 合计 | **1138** | **0** | **57** |

`NEWMANGA_CORECLIENT_SIDECAR_DIR=UNSET` 已核实；57 skip 的直接原因是 sidecar 环境前置未设置（名单见附录），不能解释成原生 DPI/a11y 的 57 项豁免。原生双屏/DPI/a11y 本轮 **BLOCKED/NOT_RUN**，没有原生截图或硬件结论。两生成器仍从 `doc/design/redesign-v1/40-fusion/tokens.json` 生成：它是既有生成管线输入，不构成本卡修改 V11R 设计的许可。

### 来源 Task 与最终证据

| 来源 | 核对结果及对本卡的约束 |
|---|---|
| FEA-06 | Task `:112-121` 及 Closeout `:268` 起：AC8–AC10 MET，AC1–AC7 PARTIAL，integration=`b26840acd`。`verification/FEA-06/integration-verification.log` 为实际最终集成证据，1034/0/57、build 0/0、两 check、pins 15/15；该目录没有名为 `final-evidence.log` 的文件，未以不存在的文件作证。impl-r2 approved 只接受当时返修与 residual 登记，不等于四页全部规格已满足。 |
| FEA-07 | Task `:293-304`、Residual/Closeout：integration=`aedc7251c`，**closed_with_limitations**；AC7 MET，AC1–AC4/AC6/AC8 PARTIAL，原生 AC5 D-1 未满足。已核对 `verification/FEA-07/final-evidence.log` 与 `integration-verification.log`，均 1138/0/57；最新 impl-r12 approved。其窗口 memento 是窗口几何/模式，不等于 Fluent 页面折叠/滚动快照。历史正文仍有 done/proposed 字样，以当前 front matter、Closeout、STATUS/PLAN 最新释放段为准，本轮不重写来源。 |

## IN/OUT 逐项判断

| 项 | 当前代码与冻结设计差距 | scope-r1 判断 |
|---|---|---|
| R-1a UI memento | `FluentShellSurface.axaml.cs:105-120` 缓存四页实例；`:197-235` 导航替换 Content，进入 Workbench 强制 Page Tab。Shelf 网格开关/Reader 方向等部分状态已有 VM 保存，但没有完整页面折叠/滚动恢复模型。设计 `04:40-44` 要求跨页面保留折叠。 | **IN 成立，无新 Host 端口前置**。须冻结字段、保存/恢复触发点、生命周期，至少页切换及缓存 Fluent↔Current↔Fluent 不丢；与窗口 memento、业务 reading_progress 分离。进程重启持久化或跨 frontend 状态翻译未授权，不能由“等页面状态”推导新增 schema。 |
| R-1b 分栏折叠 | Shell 当前仅按宽度隐藏 nav（`:329-340`）；`ShelfPageView.cs:149-174` 固定主区/详情双列，`:271` 仅按选择显示详情；`WorkbenchPageView.cs:141-176` 固定 film-strip/画布/inspector。没有完整折叠/恢复操作及抽屉映射。 | **IN 成立**。按 `04:22,31-44`、`05:55-61`、`06:61-67` 列明确栏位、令牌、恢复入口和隐藏后焦点去向。设计 04 通用 Medium inspector=40 与 06 页面 Medium=320 存在需解释的具体差异，先登记并由 DSH 固定采用口径，不由实现者任取数值。 |
| R-2 书架 | 回收站空 drawer `ShelfPageView.cs:73-76`；扫描 indeterminate `:230-237` 确需真实进度源。但错误卡 `:218-223` 缺控制台按钮，现有 Shell Console 跳转已可用；满态已有 Books/Chapters 投影可显示相应已知统计。 | **拆分**：回收站操作、逐项扫描投影继续 OUT/BLOCKED；错误卡入口和仅基于现有投影的统计可 IN。不得伪造全库总计。若 DSH 刻意留第二批，应标分批 DEFERRED，不能统称 FEA-12/10 阻塞。空态导入受目标章节前置限制继续保留已记录偏差。 |
| R-3 工作台 | Run/BatchMatrix 控制数据未接；`WorkbenchViewModel.HasUnsavedDraft`（VM `:471-482`）已有真实本地脏状态，未保存圆点不依赖 Run。冲突“查看对照”的完整新旧 revision 投影本轮未证明就绪。 | **拆分**：Run/批量投影 OUT/BLOCKED 成立；未保存圆点可 IN。冲突对照须列明确缺少的读模型/端口，继续 OUT，不能用本地文本假装完成对照。现有本地草稿确认及 Esc 可与 R-5a/R-6/R-7 共测，避免笼统“9 行均等 FEA-10”。 |
| R-4 阅读器 | `ReaderPageView.cs:20-88` 单 Image、常驻顶/底条，滚轮为翻页；双页第二图/长条真实数据面未闭环。但工具条 2s 自动隐藏/点击恢复是 `07-page-reader.md:23` 已冻 UI 行为。 | **拆分**：双页/滚动/源不可用真实状态保持 OUT，依 FEA-09/11；自动隐藏可利用现有 UI 与本轮 motion/focus 完成，或明确分批延期，不能直接称数据端口阻塞。隐藏时不得移走当前键盘焦点或把焦点留在不可见工具条。 |
| R-5a 设置确认/Esc | Shell `:197-235` 无离开 IsDirty 拦截；`:488-498` Esc 只处理 Shell 浮层/Reader；Settings `:465-470` 仅有取消按钮恢复外观，内层 confirmation 不在 Shell 浮层状态中。VM `:1070` 有 IsDirty、`:1148-1193` 有返回 bool 的保存与失败保留。设计 `08:75-79,91-94` 已定义确认/Esc。 | **IN 成立**。仅用既有 AppearanceCoordinator、draft 状态与保存返回值；FEA-07 是退出阻断能力，不能当成已提供页面三选一对话框。须覆盖导航按钮/空间键/命令面板/返回等所有离开入口，以及内层对话框优先 Esc。Provider/网络编辑器的局部缓冲须逐项列明纳入或延期，不可把外观 IsDirty 误称全分组未保存保护。 |
| R-5b 与遗漏字段 | 备份目录/频率缺口确需 FEA-13。`SettingsPageView.cs:345-346` 明说网络 Profile 没有 timeout/concurrency；`Services/SettingsProfileContracts.cs:88` 起现有 Draft 面也不能据此扩字段。完整错误/部分状态在 `:433-451` 等只有局部承载。 | 备份 OUT 成立；**网络 timeout/concurrency 及页面错误/部分态未在本批 IN/OUT 得到完整归属**。应补独立子项、对应端口 Owner/恢复条件；无契约授权则 BLOCKED，不借 R-5a 增加字段。已有可触发错误/字段不可用态的 UI 可纳入，数据缺口单列。 |
| R-6 组件 full 状态 | `DS/Styles/Controls.Fluent.axaml` 已有多类按钮 hover/pressed/disabled；不能视为全部未实现。`DS.Tests/FluentComponentsTests.cs` 主要测类身份、开关及控件存在，未逐组件断言 full 状态最终外观。 | **IN 成立**，需要 DS 路径，不能只改 App。以 `10-component-inventory.md` 加现有 20 项 registry 固定集合，按适用状态列矩阵；非交互容器不强塞 pressed，N/A 要有理由；业务投影阻塞不妨碍用合成夹具验证组件外观，但不得把夹具当端口交付。 |
| R-7 焦点环/motion | FocusRing 已全局 opt-in（`DS/Styles/Focus.axaml:4-26`），环色/宽度用 V11R 共享资源而非 Fluent 环族，不能声称焦点环完全不存在。Shell `:509-515` 只初始化类别 class/全局 reduced-motion；Fluent 样式没有完整三类动画。环令牌已存在。 | **IN 成立**，不依赖新增数据端口。需 Fluent 限域实现及实际动画/焦点断言；不能改全局 ring/reduced-motion 规则让 Current V2 视觉变化。原生 AT/混合 DPI 继续 BLOCKED，headless 可断言的可访问名称、焦点转移和隐藏控件排除不应一起延期。 |
| R-8 四 VM 拆分 | 当前文件 **1408 行**，不是 Task `:66,78` 的 1373 行；还含 FluentPageState、FluentViewModel、DraftErrorMap、SettingsGroupId。FEA-07 对 Settings 同步/confirmed-draft 有新增。PNG opt-in 仅在残项 `:66`，未在 IN `:78` 释放。 | **IN 成立**，`ViewModels/**` 覆盖新增/移动 `ViewModels/Fluent/*.cs`。四页各文件，公共基类/枚举/map 可另文件，保留 namespace/API/事件顺序/保存与取消行为；不把本次拆分变成新的架构抽象。PNG 单列决定，见 S-005。 |
| R-9 Elevation | 设计 `01:48-56` 已冻结三档值/用途与高对比回退；`DS/Themes/Tokens.Global.axaml:16-21` 有三 BoxShadows 和焦点三键，`DS/Generated/NmKeys.g.cs:305-325` 有常量。FEA-06 impl-r1 已确认“键存在、样式零消费”。 | **OUT/BLOCKED 理由不成立**。已有冻结设计与令牌，正常 Fluent 阴影消费/高对比边框回退可在 DS Fluent 样式内实现，无须改生成物。建议纳入组件子批次；若只因预算延期，DSH 明确 DEFERRED，不能再写“冻结确认缺失”。 |
| 原生 DPI/a11y | FEA-07 的 headless memento/manifest 不等于 100/125/150/200% 原生矩阵；未取得原生屏幕阅读器/硬件证据。 | **OUT/BLOCKED 成立**。登记 D-1、待补环境、具体矩阵与恢复条件；不扩大为所有 headless layout/focus/a11y 均不可验证。无须在本卡改 `app.manifest`。 |

结论：第一批明确列出的 IN 项没有被证明必须依赖未落地 FEA-09/10/11/12/13 端口。主要问题是范围未拆到可验证粒度，且把部分可实施 UI 误归为端口阻塞。以上“可 IN”是交 DSH 冻结建议，Reviewer 未自行扩权或实施。

## base_commit / allowed_paths 核对

1. **base 合适**：`82529a3d5864a39f362e414b67bca774d743f862` 可解析，包含 FEA-07 closeout；代码同当前 head。复审须使用返修后精确文档 head，实施前重新 Reality Check。YAML 当前值带中文括注是仓库已有写法，本轮未据此虚构解析失败。
2. **R-8 无缺写域**：Task `:30` 的 ViewModels glob 覆盖 Fluent 新增/移动文件；既有 csproj 默认纳入普通 C# 文件，无须为了拆分修改 sln/csproj。
3. **R-6/R-7 不只涉及 App**：主样式和控件在 DS `Styles/Controls.Fluent.axaml`、`Controls/FluentComponents.cs`；焦点行为在 `Theming/FocusRing.cs`。Task `:35,37` 已覆盖 DesignSystem 和相应测试，没有漏列 DS。建议精确列 Fluent 样式/控件及必要 Fluent opt-in 辅助文件；全局 Focus/ThemeManager 若确需改动，须先由 DSH 明确不改变 Current 的兼容边界与测试，不能凭整目录 glob 重写。
4. **过宽风险**：Task `:29-37` 同时允许所有 Views/ViewModels/Shell/Services/DS；`:82,96` 的禁改语义有效，不是空白授权，但新增文件仍可能建立第二 Host/退出协调器。建议显式只准 `Views/Fluent/**`、`ViewModels/Fluent/**`、Fluent helpers 与逐文件确认项；禁止 `Views/Presentation/**`、`Shell/V2/**`、`Services/FrontendHostCoordinator.cs`、SafeStartupPlanner、IPresentation* 共享 seam、共享 KeyMap/ShellCommands 的语义改动，除非 DSH 单独释放。
5. **现有禁改面应保持**：Core/Host 契约/Appearance schema、生成器/生成物（包含 `DS/Generated/**`、`DS/Themes/Tokens.*.axaml`）、冻结设计、组合根、FrontendSelector、Current V2、V11R 设计、依赖/TFM/第三方资产。`NewManga.ThemeEngine/**`、Appearance 项目、Presentation 项目、manifest 不在本批写域，未发现必须新增这些路径的理由。不得因 motion 时长与既有 fast/normal/slow 不一致而改生成令牌；使用 `02-motion.md:65` 已允许的集中冻结参数。
6. **治理写域分工**：证据/Handoff/Review 路径齐备；Owner 更新自身 Task/证据，STATUS/PLAN/LEDGER、审查 Appointment、关闭及资源裁定交 DSH。allowlist 含这些文档不等于转让 DSH 权限。旧 `verification/FEA-06/**` 不在本卡写域，PNG 采证必须移出默认回归副作用。

## AC 映射与验证策略

现有 AC1–AC5 可保留编号，但 `:80,88-92` 尚不足以冻结：AC1“其中不依赖端口的部分”、AC3“可实现的确认流/错误态”、AC4“完成或转后续”不能唯一决定交付边界，也允许把已列 IN 的 R-8 再延期。建议在编号下固定以下子项与证据，不以测试总数代替行为验收。

| AC | 建议固定的第一批子 AC | 最低判别性验证 |
|---|---|---|
| AC1 | R-1a 字段/生命周期；R-1b 栏位及各断点映射；DSH 接受的 R-2/R-3/R-4 纯 UI 子项 | 设置非默认折叠、滚动/筛选/视图/Tab 状态→离页→返回，布局完成后恢复；边界宽度 1023/1024、1279/1280、1599/1600；折叠/展开/抽屉及恢复入口、主内容最小宽；隐藏栏移出焦点序。缓存 frontend 往返及失败/取消回滚保留状态，不接触业务存储。 |
| AC2 | 固定组件集合×适用状态×主题/对比度×测试；R-7 三类 motion 与焦点；R-9 若 DSH 纳入 | 真实 pointer/keyboard 输入和禁用命令零触发；断言最终 Background/BorderBrush/Opacity/选中样式与资源解析，不只断言 class 非空。浮层开关、遮罩、焦点入内/回触发器、隐藏不占位；focus 2px/offset1、高对比3px；Current V2 对照不变。 |
| AC3 | R-5a 具体编辑缓冲与全部离开入口；已有错误/部分态；缺字段逐项 BLOCKED | 脏设置保存/丢弃/取消三分支；保存失败/只读/取消均留旧页和输入；成功只调用既有唯一写者；连续/重入导航仅执行最终已确认动作；内层弹窗 Esc 先取消弹窗，外层 Esc 按设计取消当前编辑；不得触发危险确认或保存。 |
| AC4 | R-8 必做行为等价移动；PNG opt-in 单列；R-9 明确纳入或延期 | 先冻结旧行为测试，保持类型/namespace/签名和订阅生命周期；方法体差异核对，纯移动阶段无逻辑修改；SettingsDraftSync、Workbench Draft save/discard、Reader progress、Fluent Shell、FEA-07 切换失败/取消/退出矩阵不弱化。PNG opt-in 不应删掉正常 headless 行为断言。 |
| AC5 | 固定当前 **1138/0/57** 为起点，新增测试另计；build 0/0、两 check、治理/pins；scope audit | 全量 sln，不减少既有覆盖/不增加无理由 skip；原有 57 skip 逐条来源与原因，新 skip 单独解释；临时 data/theme/journal 与证据输出目录；索引、head、SHA、EXIT/shell、组件矩阵、Handoff、上下文独立实现 Review、DSH 集成验证。 |

Motion 必须测试实际消费，而非仅 `MotionResolver` 或 class：按 `02:24-61` 覆盖 full、auto(系统开/关)、reduce、三类分别禁用、旧 ReducedMotion 迁移全禁；full 覆盖系统、navigation reduce=0、feedback 无缩放/抖动且禁类时颜色过渡=0、decorative 不创建/停止。用可注入平台偏好、确定性时钟/动画对象断言，关闭/解绑后无循环；`02:67` 的失焦/不可见暂停也属 headless 可验证。不能用共享全局 ReducedMotion 布尔代替三类别独立语义。

BLOCKED 台账每项应有来源原 AC、residual 子 ID、缺失端口/字段或硬件、Owner Task、恢复条件、未运行用例、已证明部分。已释放子 AC 与未来 OUT 分开：整张 residual 卡若仍承载所有 OUT，整体 AC 必须如实 PARTIAL，不能为关闭改 MET；或由 DSH 在冻结时将本批 AC 明确限于已释放子项，未来要求保留到后续批次。TODO 在 ready 阶段不触发机械失败，进入 in_review 前须换为 §4.3 合法状态。治理 PASS 不是语义范围已冻结。

## 风险与实施顺序

不要求新建子 Task，但建议在同卡内分固定 commit/子批次，DSH 逐批接受：

1. **先做范围与设计差异表**：放本卡 evidence_dir，列设计章节→当前代码→目标状态→测试→IN/BLOCKED/DEFERRED；包括 Medium inspector 口径、设置编辑缓冲、Elevation 与空态既有偏差。不修改 FROZEN v1；真正设计偏差交 DSH 走 v1.1 重冻结。
2. **R-8 纯移动**：以 1408 行真实基线拆四 VM 与公共类型，独立 commit。跑针对性及全量基线，禁止与 UI 逻辑修复混在同一个“纯重构”差异中。PNG opt-in 为另一个明确行为改动提交。
3. **R-1a/R-1b 与 R-5a**：先状态模型/导航确认，再布局与焦点迁移；避免折叠重新建树清掉编辑缓冲。外观 draft 与 Core Draft 不是同一存储，不能复制 Core owner/token 机制解决设置取消。
4. **R-6/R-7（及批准后的 R-9）**：共享 DS 控件只做 Fluent 范围改造；用真实状态矩阵收口，测试动画/焦点及 Current V2 对照。若纳入 Reader 自动隐藏，与 motion/focus 一起验，不改双页/数据面。
5. **集成前回归**：固定 delivery head，重跑 FEA-07 的稳定 Window、staging 输入隔离、layout/Loaded/render 提交门禁、失败/取消全屏补偿、隐藏 dirty tree 退出阻断、confirmed-draft 同步测试。不得为新导航确认绕过 FrontendSwitchCoordinator、手动保存 frontendId 或 Dispose/重建 Host。实现后新的独立上下文审查，由 DSH 集成；本会话不参与实现/返修。

Architecture 结论：本批可在 App Fluent + DS 外观层落地，不需新增端口、schema、依赖或组合根改造；写域宽泛与跨页状态定义仍需冻结。Verification 结论：当前构建/回归基线 PASS；新行为验收尚未实现，本轮未声称任何新 AC MET；原生验收仍 BLOCKED。

## 治理与 Appointment

- owner=codex 合适：用户 2026-11-02 指派有 `doc/tasks/FEA-06.md:53` 与本卡 `:53` 承载；优先于通用 ZCode UI 主责，不需重新征求产品 Owner。
- 本轮 Appointment 有用户委派 + checkpoint §75，可确定身份和写入目标；本卡 `reviewer:null`、`approval:...pending` 与 STATUS“scope-r1 进行中”没有伪造 approved。实施释放前 DSH 应登记本轮审查来源、返修处置与后续实现 Review Appointment，不能把本 scope Reviewer 当默认实现者或默认实现 Reviewer。
- Task `depends_on` 同时包含未落地 FEA-09…13，而 `ready` 是第一批：应显式区分本批已集成依赖与后续残项依赖，避免与协作协议 §4 的 ready 前置混读。FEA-07 只提供已证明部分，不以 closed_with_limitations 当全能力通过。
- evidence_dir 及 allowed_paths 已有；Canonical Evidence 和 Closeout 在 ready 阶段 pending 合理。**Resource Manifest 缺失**，应按 §4.2 增补 worktree（主仓 checkout）、task-env/temp、agent-output、PNG/其他 artifact、用户数据不适用项及资源保留策略。后续不能只填“待关闭”而跳过 manifest。
- DSH 处置本报告并固定新文档 head 后再派 scope-r2；未解决 P1 之前不能冻结实施。不要为了机械检查通过修改本报告或来源 Review 字节。

## Findings

下列为 **6 个独立 finding**；各节重复说明不另计数。全部状态 open，findings_disposition 交 DSH。

| ID | 级别 | 证据（0e52c9daa） | 触发与影响 | 最小建议 |
|---|---|---|---|---|
| S-001 | **P1** | Task `:67,79`；设计 `01:48-56`；DS `Themes/Tokens.Global.axaml:16-21`、`Generated/NmKeys.g.cs:305-325`；FEA-06 impl-r1 `:83,134` | R-9 被以“令牌/设计冻结确认缺失”阻塞，但对应值与键已就绪。按此冻结会继续把已明确的设计消费缺口当外部依赖，且 R-6 full 状态与阴影边框口径不闭合。 | R-9 纳入组件批次；或 DSH 明确出于分批预算 DEFERRED，记录真实理由及后续承接，删除错误 blocker。高对比回退与 Current 不变纳入验收。 |
| S-002 | **P1** | Task `:73-80,88-104`；Shell surface `:197-235,488-515`；Settings VM `:1070,1148-1193`；设计 `02:24-68`、`03:42-79` | 已列 IN 但验收仍是“等页面状态”“full”“可实现部分”；没有冻结 memento 生命周期、导航/Esc 优先级、组件适用状态和实际三类 motion 断言。实现者可交 class 标记/保留任意一部分而仍声称达成。 | 保持 AC1–AC5，增子 AC、字段/入口/状态/断言表、1138/0/57 基线及 FEA-07 不退化矩阵；明确本批与整体 residual 关闭口径。 |
| S-003 | **P1** | Task `:60-63,75,79,88,90`；Shelf `:218-223`；Shell surface `:284-303`；VM `:471-482`；Reader 设计 `07:23`；Settings `:345-346` | R-2/R-3/R-4 将可用现有状态实现的 Console 入口、未保存圆点、自动隐藏与真实数据面整体 BLOCKED；R-5 网络超时/并发及错误/部分态又没有完整进入 IN/OUT。第一批范围与 residual 台账非穷尽互斥。 | 拆子项：纯 UI 纳入或诚实 DEFERRED；真实 Run/回收站/Reader 数据端口继续 BLOCKED；缺字段写明契约/端口 Owner 与恢复条件，不新增模拟数据或共享字段。 |
| S-004 | **P2** | Task `:29-37,82,96`；DS `Styles/Focus.axaml:4-26`、`Theming/FocusRing.cs:84-85,119-143` | 整目录写域允许编辑全局焦点/主题和稳定窗口接线，虽有语义禁止，仍不利于确定最小差异；全局 ring 被直接替换会影响 Current V2。 | 限定 Fluent 子路径/必要逐文件项，补共享 KeyMap、IPresentation*、协调器、依赖/TFM 与 V11R 设计禁止项；需要共享辅助改动时先由 DSH 明确兼容边界。 |
| S-005 | **P2** | Task `:66,78,91`；VM 文件 1408 行；App.Tests `FluentPageTests.cs:240-278` | R-8 IN 只说 VM 拆分，丢失同一残项内 PNG opt-in 的实施/延期决定。默认全量测试会写旧 Task 的 pinned PNG 路径，异机可 dirty 旧证据，且本轮 scope 承诺“不改其他证据”与该测试副作用存在实际张力。 | R-8a=1408 行基线纯移动；R-8b=显式 opt-in 采证，输出临时/本卡目录，保留正常行为测试；或明确 R-8b 后续 Owner/时点。禁止覆盖旧 FEA-06 证据。 |
| S-006 | **P2** | Task `:10-18,24-26,106-114`；协作协议 `:67-97`；checkpoint `:526-532` | 本轮来源可确认，但卡中 Reviewer 未登记、所有后续依赖混在 depends_on，且新 Task 无 Resource Manifest。实施前治理交接与最终资源收口未完整建模。 | DSH 记录 scope Appointment/处置，分本批依赖与未来依赖，补 manifest、实现 Review Appointment/交付 Gate；保持 canonical/closeout pending，勿预填完成。 |

## 结论与最小返修集

**Decision：changes_requested（P0=0 / P1=3 / P2=3），当前不建议冻结第一批实施。** 这是范围/验收返修，不要求先实现页面，也不要求等待全部后续端口。

最小返修集：①纠正 R-9 blocker；②把 R-2/R-3/R-4/R-5/R-8 拆到穷尽、互斥且可解释的 IN/BLOCKED/DEFERRED 子项；③冻结 memento/布局/设置确认/组件/motion 的子 AC、测试与关闭口径；④明确 Fluent 写域、PNG 输出及资源/Appointment。范围返修应先于代码改动，FROZEN fluent-v1 原字节保留。

推荐下一步（可直接转发给 DSH；不自动启动实施）：

> Task：FEA-06-RESIDUAL-1 scope-r1 处置与范围 v2；Agent：DSH（范围作者/Lead）；工作目录 `G:\CODEX\New Manga`，branch `main`，common `.git`；恢复点 base=`82529a3d5864a39f362e414b67bca774d743f862`、被审 head=`0e52c9daab372f83edcd1bae2030f8bb98754771`。先 Reality Check 并保留本 scope-r1 报告原字节，处置 S-001…S-006：纠正 R-9 阻塞理由；逐子项拆分可落地 UI 与端口 BLOCKED/分批 DEFERRED；固定第一批 AC/测试/关闭边界、1408 行 R-8a 与 PNG R-8b、Fluent 最小写域、依赖/Appointment/Resource Manifest。仅修改本卡和已授权的当前治理/处置/Handoff 文档，必要差异矩阵放 `verification/FEA-06-RESIDUAL-1/`；不改代码/测试/契约/schema/依赖/生成物/冻结设计/Current V2/历史证据，不 commit 本报告的改写，不 push。交付精确文档 head、逐 finding disposition、范围 v2 与下一次 scope-r2 Appointment；运行 `pwsh -NoProfile -File tools/governance/check.ps1`、`pwsh -NoProfile -File tools/governance/verify_pins.ps1`，核实代码/测试无漂移。代码基线仍为 1138 passed / 0 failed / 57 skipped；BLOCKED/NOT_RUN 不记 PASS。再指派 fresh Codex CLI 独立上下文只读 scope-r2；P1 闭环并经 DSH 冻结后才派 Codex 实现。

## 附录：本轮 57 skipped 来源与直接原因

以下每个方法的直接原因均为 **S＝`NEWMANGA_CORECLIENT_SIDECAR_DIR` 未设置，sidecar 前置检查先行拒绝**；即使名称涉及 fixture/provider/Explorer，也未到后续环境判定。来源为对应测试程序集同名类及 sidecar Fact/fixture 检查；不是通过用例。

| 程序集/类 | skipped 方法（每个均原因 S） | 数量 |
|---|---|---:|
| CoreClient / CommandIntegrationTests | DomainServices_CoverEveryCommandExactlyOnce；NotSupportedSurface_ReturnsTypedErrorsWithReasons；ChineseTitle_ThroughCommandDispatcher_RoundTripsWithoutMojibake；TwelveImplementedCommands_ExecuteAgainstFrozenSidecars | 4 |
| CoreClient / CommandWiringB1Tests | B1Commands_RejectInvalidArgumentsBeforeAnyCoreFrame；B1Commands_ExecuteAgainstFrozenCore | 2 |
| CoreClient / CommandWiringB2Tests | ListRegionRevisions_ExecutesAgainstRegionFixture；B2Commands_ExecuteAgainstFrozenCore；B2Commands_RejectInvalidArgumentsBeforeAnyCoreFrame | 3 |
| CoreClient / CoreServiceIntegrationTests | RawUtf8Request_ReplicatesUnknownError；ChineseTitle_CreateThenList_RoundTripsExactly_AndWireIsAsciiEscaped；Ping_ReturnsReady_WithProtocol23；WireFrames_AreSingleLineUtf8AndAsciiForEveryEscapedRequest | 4 |
| CoreClient / RunBindingFixTests | StartRun_InvalidOverrides_AreRejectedBeforeAnyCoreFrame；StartRun_DefaultDisabled_OmitsProviderBindings；StartRun_InjectsDefaultBindings_WhenOverridesAbsentOrEmpty；StartRun_KeepsExplicitUserBindings_AndOtherOverrides | 4 |
| CoreClient / SidecarFailureTests | StartupTimeout_IsTyped_NotAHang | 1 |
| CoreClient / HostBridgeIntegrationTests | WireFrames_AreSingleLineJson_AsciiOnly；TypedErrors_UnknownResource_AndCoreOwnedPathSmuggling；Ping_IssueResolveRevoke_FullLifecycle | 3 |
| CoreClient / S4RegionReaderCommandTests | RegionWriteFace_AndReaderProgressFace_ExecuteAgainstFrozenCore | 1 |
| Host / HostRegionWorkbenchIntegrationTests | RegionReads_SerializeOnTheCorePipe；RegionWrites_ReadOnlyHost_AreTypedRefusals_WithZeroCoreFrames；RegionReadWriteFace_ExecutesAgainstFrozenCore_AndProjectsOverlayGeometry；RegionWrite_StaleExpectedRevision_IsTypedInputRevisionChanged | 4 |
| Host / LegacyShellRealTests | LegacyShellRunning_ForcesReadOnlyMode_AndBlocksWrites | 1 |
| Host / StartupSelfCheckTests | MajorMismatch_DowngradesToReadOnly_AndRefusesWrites；RealHost_PassesCheapChecks_AndStaysWritable；MissingCapability_DowngradesToReadOnly_AndRefusesWrites | 3 |
| Host / CredentialPortTests | CredentialPutAndClear_AgainstFrozenSidecar_FullChain | 1 |
| Host / HostReaderProgressIntegrationTests | SaveReadingProgress_PersistsAcrossHostRestart_AndResumes；SaveReadingProgress_UnknownPage_IsTypedCoreRejection；SaveReadingProgress_ReadOnlyHost_IsTypedRefusal_NoCoreCall | 3 |
| Host / ExportStalePolicyWireTests | BothPolicies_AreSentToTheCore_AsStartExportFrames | 1 |
| Host / HostRuntimeIntegrationTests | ReadOnlyUntilParity_Ready_WithBothSidecars_AndWriteBlocked；ParityReached_ChineseRoundTrip_IsExact_ThroughHost；SecondInstance_IsAlreadyRunning_WithoutSpawningSidecars | 3 |
| Host / GrantIssuerTests | ShellActions_Open_Whitelisted_Directories_And_Refuse_Outside_Paths；Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages；Import_IntoNewChapter_Executes_AndRegistersGrant；ShellActions_RealOpener_OpensExplorer_WhenEnabled | 4 |
| Host / WritePolicyTests | DefaultStart_IsReadWrite_AndCanCreateBook；ExplicitParityFalse_RefusesWrites_WithTypedReadOnlyError；FirstRunBackup_CreatesRealBackupFile_OnFirstWritableStartWithCatalog | 3 |
| Host / HostReaderChaptersIntegrationTests | ConcurrentChapterAndProjectionReads_AreSerialized；ListChapters_MatchesReaderProjection | 2 |
| Host / ExportE2ETests | Export_Zip_Produces_RealArtifact_AndSnapshotHistory；Export_Cancel_LeavesNoArtifact | 2 |
| Host / RealTranslateProviderTests | RealOpenCodeProvider_HostConfiguration | 1 |
| App / RunControllerHostIntegrationTests | RunCommands_WhenReadOnly_PublishHostReadOnly；RunCommands_StartSuccessfulRun_ProjectRealPerPageState_AndReuseKey；RunCommands_MapCoreErrors_AndReuseIdempotencyKeys | 3 |
| App / WritePolicyUiIntegrationTests | DefaultController_IsWritable_AndParityFalse_IsReadOnlyWithReason | 1 |
| App / CreateChapterHostIntegrationTests | HostController_CreateChapter_SucceedsThenMapsCoreFailures；HostController_CreateChapter_WhenReadOnly_PublishesHostReadOnly | 2 |
| App / StartupSelfCheckUiTests | SelfCheckFailure_IsVisibleInTheSnapshot | 1 |
| 合计 | CoreClient 22 / Host 28 / App 7 | **57** |
