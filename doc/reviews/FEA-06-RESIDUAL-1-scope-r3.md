---
task_id: FEA-06-RESIDUAL-1
reviewer: ZCode CLI（fresh independent scope review r3；headless plan；Codex 额度故障转移）
reviewer_kind: agent
author: DSH
base_commit: 82529a3d5864a39f362e414b67bca774d743f862
reviewed_head: e71585834
decision: approved
counts:
  P0: 0
  P1: 0
  P2: 4
---

> 来源：ZCode CLI headless（`--mode plan` 只读）回答，会话 `sess_3c0de2b4-6329-4d83-9a2a-d1431e6497cc`；由 DSH 原样落盘（去除 Markdown 代码围栏，未改正文）。Codex CLI 本轮额度用尽，按用户 2026-11-02 故障转移规则改派 ZCode。


# FEA-06-RESIDUAL-1 scope-r3：范围 v3 冻结复核

## 1. Reviewer 身份与来源

本报告由 **ZCode CLI headless（`--mode plan` 只读）** 独立上下文产出，reviewer_kind=agent。未参与本卡范围编制、scope-r1/scope-r2 或任何实现/返修。来源为用户 2026-11-02 委派（Codex CLI 本轮额度用尽，按用户故障转移规则改派 ZCode；checkpoint `GOAL-PROGRESS-2026-11-02.md` §78 与任务卡 Appointment 同步承载）。未派发子 agent，未进入其他 worktree，不承担范围作者、实现者或 DSH 的处置/集成权限。

本轮唯一输出为本报告（由 DSH 原样落盘为 `doc/reviews/FEA-06-RESIDUAL-1-scope-r3.md`）。未修改任何仓库文件、未 commit/push、未写真实 `%APPDATA%`、未运行任何会写仓库证据的测试命令；起始与结束时 `git status --short` 均为空。下文 Task 行号指 `doc/tasks/FEA-06-RESIDUAL-1.md` 在 **e71585834** 的内容（当前工作 HEAD `c8a7f6664` 与其仅差 reviewer 字段两行，见 §2）；其他文件行号以各自当前内容为准（代码自 `04d7c79e3` 起零变更，见 §2 证据链）。

## 2. 范围与 Reality Check

### 2.1 git 实跑（全部 exit 0）

| 命令 | 结果 |
|---|---|
| `git rev-parse HEAD` | `c8a7f6664ea42c246048d6eafa8f2e931b03155d` |
| `git status --short` | 空（起始与本轮结束时均清洁） |
| `git log --oneline -8` | `c8a7f6664`→`e71585834`→`04d7c79e3`→`0e52c9daa`→`82529a3d5`→`cb1a4bede`→`527a7ec37`→`91de6a345` |
| `git diff --stat 04d7c79e3..HEAD` | 5 files / +237 −65，仅 `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、checkpoint、scope-r2 报告、本 Task |
| `git diff --name-only 04d7c79e3..HEAD` | 同上 5 个 doc 文件，**无任何代码/测试/工具变更** |
| `git diff --name-only e71585834..c8a7f6664` | 仅 checkpoint + Task 2 文件（+9 −2） |

`e71585834..c8a7f6664` 对 Task 文件的全部差异为两处 Appointment 文字（reviewer 字段与 §Review Appointment 段：scope-r3 改派 ZCode），**不改范围内容**；被审范围 v3 实质内容与 `e71585834` 一致。「范围 v3 提交仅文档变更、本批未改代码」的声称**属实**。

### 2.2 构建/测试/生成器/治理脚本：本轮 NOT_RUN 及替代证据链（如实披露）

本轮 ZCode headless plan 模式的只读边界拦截了所有会产生写副作用的命令：`dotnet build`、`dotnet test`、两个生成器 `--check`、`tools/governance/check.ps1`、`tools/governance/verify_pins.ps1` 均被权限层拒绝执行（每条均有实际尝试与拒绝记录）。因此本轮**没有**复跑构建与测试，下述数字不得被解读为本轮实跑结果。

替代证据链（同一代码树的确定性等价）：

1. `git diff --name-only 04d7c79e3..HEAD` 输出仅 5 个 doc 文件 —— 即自 **scope-r2 实跑基线 `04d7c79e3`** 以来 `apps/**`、`tools/**` **零字节变更**；
2. scope-r2 报告（同机同仓、SDK 10.0.401）在 `04d7c79e3` 实跑并保存：build **0 warnings / 0 errors**；安全口径回归（`--filter "FullyQualifiedName!~FluentPages_RenderHeadlessPngEvidence"`）**1137 passed / 0 failed / 57 skipped，另排除 1 项**；TokenGen `--check` PASS（292 rows）；ThemeGen `--check` PASS；check.ps1 PASS（3 warnings：9 个非终态 Task、STATUS/PLAN 80% 预算）；verify_pins **15/15**；
3. 代码树逐字节一致 ⇒ 上述结果对当前 head 的代码状态直接适用；治理脚本结果中 STATUS/Plan 自 `04d7c79e3` 后又有两轮文档提交，**check.ps1/verify_pins 的指针结论本轮未复验**，但 §3/§8 的 R2-005 核对以直接读文件完成（STATUS:7,10、Plan:22,36–39、Task:142–144），不依赖脚本输出。

影响声明：本轮不能证实「无过滤全量在本轮复跑通过」；任何人不得从本报告推导该结论。PNG 用例排除口径与 Task v3 冻结的基线（1137/0/57 → I-7 后 1138/0/57 起点）一致，本轮起始 `git status` 清洁证明未发生证据漂移。

## 3. R2-001…R2-006 闭环表

| 原 finding | Verdict | v3 证据与剩余问题 |
|---|---|---|
| R2-001 / P1：I-3/I-5/I-11 验收不可判定 | **CLOSED** | I-3（Task:76）三分支=保存并离开/丢弃并离开/取消，逐项断言（保存调用与 host 写入发生、丢弃清 draft、取消留页留稿）；保存失败注入后留页/留稿/错误可见（对齐 08:68「保存失败保留未保存值并提示」）；Esc 优先级「浮层内=取消、页面内=触发离开流」对齐 03:40+08:75–76 组合语义；FEA-07 `IPresentationExitState` 聚合不退化入断言。I-5（Task:78）恢复设计真实三态 auto/full/reduce × 三类 × 分类开关；「读取失败→full+warning」=02:16 原文；「用户显式优先」=02:17；「categories[x]=关 在 full 下按 reduce 列执行」=02:18 原文；参数 240/180/200/160ms 与 02 §2.1 一一对应；旧值迁移判据⑤已有 resolver 层测试（`MotionResolverTests.cs:115` `LegacyReducedMotion_True_MigratesToReduce_WithEveryCategoryOff`），UI 消费矩阵不需重复迁移断言。I-11（Task:84）2px/offset 1/高对比 3px=03:53,62 原文；浮层焦点移入/返还=03:54；隐藏控件移出 Tab 序=03:55；并补「四页各至少 1 个焦点场景」覆盖面判据。 |
| R2-002 / P1：IN/OUT 非穷尽互斥 | **CLOSED** | v3 重构为 IN=I-1…I-14 / BLOCKED=B-1…B-7 / 无 DEFERRED。控制台入口归 I-12（NavigateSpace(Console) 现有实现在 `FluentShellSurface.axaml.cs:284–294`，纯导航可行）；9 行状态视觉骨架归 I-13、数据绑定唯一归 B-2（I-13 明文「数据绑定归 B-2，不重复归属」）；源不可用警示本体归 I-14、恢复动作归 B-3（明文分工）；满态统计/冲突数据归 B-6/B-7 且写恢复条件。逐子项映射核对见 §4，无重复归属、无漏项。无 DEFERRED 的选择成立：v2 的 DEFERRED 候选中可实施项已全部升 IN，缺数据/字段项全部 BLOCKED，「可做而延期」的中间态被消除而非隐藏。 |
| R2-003 / P1：I-8 违反冻结设计 | **CLOSED** | Task:81 已改为「**standard 与 reduce 均保留阴影令牌不变**；仅高对比模式回退 1px 边框（设计 03:62）」，断言列含「standard+reduce 阴影仍为原令牌」。与 `01-design-tokens.md:56` 原文（「`reduce` 动效下阴影**不变**（阴影不是动效）；高对比模式下阴影退化为 1px 边框」）逐字对齐。reduce 回退边框表述已删除。 |
| R2-004 / P2：写域路径错误/过宽 | **CLOSED（维持 r2 验收口径）** | Task:27 已用真实路径 `apps/desktop-avalonia/src/NewManga.App/Controls/FluentUi.cs`（实测存在，158 行）；R-8a VM 拆分由 Task:25 `ViewModels/Fluent/**` 覆盖（实测目录仅 `FluentPageViewModels.cs` 1408 行，与 Task 声称一致）；四页视图由 Task:24 覆盖（实测 9 文件俱在）；焦点/motion/样式消费由 Task:28–30 DS 三目录覆盖；`Controls.Fluent.axaml`（360 行）、`FocusRing.cs`（314 行）均在域内。DS `Controls/FluentComponents.cs` 仍未入域——r2 已裁定不据此要求开放（组件状态可在 Styles 层完成），v3 以禁改条款（Task:113–115）+「共享辅助改动先停等 DSH」回应，整目录宽度维持 r2 的 P2 非阻塞姿态，无恶化。 |
| R2-005 / P2：治理指针/Manifest | **PARTIAL→基本闭环，残留一处** | STATUS:7,10 已指向「范围 v3/scope-r3 进行中」；Plan:22 依赖列只保留 FEA-06、FEA-07（「FEA-09/10/11/12/13 仅为 BLOCKED 承接方，非本批依赖」）；checkpoint §77/§78 处置链完整；Manifest（Task:144）八类齐备且各有当前状态（worktree/verification/task-env/dataset/test-material/temp/agent-output/exchange/user data）。**残留**：Plan:39（当前 DAG 段活文本，非历史快照段）仍写「第一批范围 v1 已释放、scope-r1 复核中」，与同文件 Plan:37「范围 v3…scope-r3 复核中」自相矛盾 → R3-001（P2）。 |
| R2-006 / P2：组件断言弱点 | **CLOSED** | Task:77 I-4 已按 r2 最小建议原文重写：先按 `10-component-inventory.md` §1–§3 冻结「组件 × 适用状态」表（清单 §1–§3 实测存在且每行有状态列，如 DangerButton=normal/hover/disabled 无 pressed，适用状态表天然吸收该差异）；断言**有效属性**（Background/BorderBrush/Opacity/Transform 与资源引用）而非字符串选择器存在；disabled 验命令零触发；浮层验焦点移入/返还；「无法 headless 验证的视觉格标 NOT_RUN，不以选择器存在计 PASS」入断言列。 |

## 4. IN/BLOCKED 穷尽性与可行性

### 4.1 原残项 → 唯一归属矩阵（21 格全覆盖）

| 原残项 | 子项 | 归属 |
|---|---|---|
| R-1 | UI memento / 分栏折叠 / 200% DPI+原生桌面验收 | I-1 / I-2 / B-5 |
| R-2 | 回收站空面板+恢复/删除/扫描进度 / 控制台入口 / 满态统计 | B-1 / I-12 / B-6 |
| R-3 | Run 投影+暂停停止+BatchMatrix 绑定 / 9 行状态视觉+数据 / 未保存圆点 / 冲突对照 | B-2 / I-13+B-2（明文分工）/ I-9 / B-7 |
| R-4 | 双页+滚动+恢复动作 / 工具条自动隐藏 / 源不可用警示本体+恢复 | B-3 / I-10 / I-14+B-3（明文分工） |
| R-5 | 网络超时/并发+备份字段+错误/部分状态数据 / 离开确认/Esc | B-4 / I-3 |
| R-6 | 组件 full 状态 | I-4 |
| R-7 | motion 三类 / 焦点环 / 原生 a11y | I-5 / I-11 / B-5 |
| R-8 | VM 拆分 / PNG opt-in | I-6 / I-7 |
| R-9 | Elevation 消费 | I-8 |

每个子项唯一归属；两个「拆半」项（9 行状态、源不可用）均有明文分工声明，非重复认领。设置页错误/部分状态 **UI** 无需新归属——`SettingsPageView.cs:435–450` 已能消费 Error/ReadOnly（scope-r2 已核实，本轮代码零漂移沿用），B-4 精确限定为「数据」。冲突入口不做视觉骨架直接 B-7 是诚实收窄（无数据入口=假入口，r1 已裁定不得用本地文本假装对照）。

### 4.2 IN 项可行性（代码现状只读核对）

- **I-1/I-2**：`FluentShellSurface.axaml.cs:197–235` 缓存四页实例 + Content 替换，memento 有缓存树基础；写域（Views/Fluent/**）覆盖。
- **I-3**：现状 `:488–498` Esc 仅关浮层/Reader、Navigate 无 IsDirty 拦截——实施空间真实；VM `:1070` IsDirty、`:1148–1193` 保存返回 bool（scope-r2 核实）可直接复用。
- **I-5**：现状 `:509–516` 仅消费 navigation enabled + 全局 reduced class——与设计矩阵的真实差距存在；`MotionResolverTests.cs` 9 例（含 fake 平台源）提供表驱动扩展基础。
- **I-6**：实测 `FluentPageViewModels.cs` = **1408 行**，与 Task 基线声称一致；`ViewModels/Fluent/**` glob 覆盖拆分产物。
- **I-7**：实测 `FluentPageTests.cs:240–287` PNG 用例无 opt-in、无条件写 `verification/FEA-06/screens/`、AppearanceStore 指向旧 Task runtime——风险前提真实，改造目标可判定。
- **I-8**：实测 `Tokens.Global.axaml:16–21` 三档 Elevation 与 Focus.Ring 三键（Width=2/Offset=1/Color）俱在且值与 01 §2.3 冻结值一致——「消费现有令牌」前提成立。
- **I-9**：VM `:482` HasUnsavedDraft、`:1070` IsDirty 现存。
- **I-10**：`ReaderPageView.cs` 既有上下条（scope-r2 核实 :70–104），无自动隐藏——纯 UI 可实施（但见 R3-003 参数精度）。
- **I-11**：`FocusRingBehaviourTests.cs` 4 例（键盘画环/指针不画/滚动隐藏/重复启用无泄漏）提供断言先例。
- **I-12**：`FluentShellSurface.axaml.cs:284–294` NavigateSpace(Console) 现有可用；`WorkbenchPageView.cs:188–200` 控制台占位诚实披露「端口尚未接入」——I-12（入口）/B-2（投影）拆分与代码事实吻合。
- **I-13**：上述控制台 RunProjectionBar 占位即「无数据部分占位/禁用态」的既有先例，视觉骨架可复制该模式。
- **I-14**：VM `:891` IsSourceUnavailable（:985–1014 设置/清除链）现存，banner 视觉纯 UI。
- **BLOCKED 诚实性**：B-1/B-2/B-3/B-4/B-6/B-7 均以「端口 Task done + 契约冻结」为恢复条件；B-5（硬件/waiver）保留 r2 判定。`SettingsPageView.cs:342–346`「当前冻结 Host Profile 契约不含超时与并发字段」实测仍在——B-4 事实依据成立。未发现假实现授权或模拟数据通道。

**穷尽性与可行性结论：成立。** 无 DEFERRED 的三态简化（IN/BLOCKED 二分）在本卡语境下成立：r2 提出的全部「可做而延期」候选要么升 IN、要么其 UI 部分已存在于代码而无需实施。

## 5. allowed_paths / base_commit 核对

1. **base_commit `82529a3d5` 仍有效**：可解析；`82529a3d5..HEAD` 全部为 doc 提交（本轮实跑 diff 证明），代码基线与 base 一致，无须刷新。scope-r2 同结论沿用并经本轮零漂移复核。
2. **写域充分**：I-1..I-14 的实施面（Views/Fluent、ViewModels/Fluent、AppStyles.axaml、Controls/FluentUi.cs、DS Accessibility/Styles/Theming、两个测试目录、本卡证据与治理文档）逐项落在 allowed_paths（Task:22–38）内；未发现必须越域才能交付的 IN 项。
3. **禁改面有效**：Task:113–117 覆盖 Core/契约/schema/生成物/冻结设计字节/组合根/FrontendSelector/Current V2 三目录、共享 KeyMap/`IPresentation*`/协调器（停等 DSH）、全局主题/焦点唯一写者、不 push、不写真实 APPDATA、BLOCKED 不假实现、不以选择器存在计 PASS。语义禁改与 glob 写域组合的可执行性可接受。
4. **轻微保留**：Current V2 保护以静态断言（`Views/V2/**` 无改动）+ 语义禁改为主，r2 建议的「同进程切回 Current 后资源/焦点环/动画不被污染」行为对照未成为明确断言 → R3-004（P2，实施期补强；DS 已有 `RealAppResourceStackTests` 基础可复用）。

## 6. AC 判定口径

AC1–AC5（Task:105–109）在本轮判定口径下可判定：

- **AC1** 绑定 I-1/I-2/I-9/I-10/I-12/I-13/I-14 + B 侧登记义务；断言逐项落到具体行为（恢复、折叠几何、dirty 显隐、导航可达、占位禁用态）。
- **AC2** 绑定 I-4（组件×状态表+有效属性+NOT_RUN 口径）/I-5（三态×三类×分类矩阵逐格）/I-11（2/1/3px+浮层焦点+Tab 序+四页覆盖）；B-5 登记。
- **AC3** 绑定 I-3 三分支+失败保护+FEA-07 退出聚合不退化；B-4 登记。
- **AC4** 绑定 I-6（1408 行等价拆分，实测基线吻合）/I-7（opt-in+旧 pin SHA 对照）/I-8（standard+reduce 阴影不变+仅高对比回退）。
- **AC5** 基线口径诚实且可执行：pre-I-7 安全回归 1137/0/57（排除 PNG 用例+直接原因记录）→ I-7 后 1138/0/57 起点、新增测试只增不减、明文禁止虚称「无过滤全量已复跑」；FEA-07 非回归矩阵以语义面列出（切换往返/退出保护/全屏/输入/关闭聚合），r2 报告行 125 已给出对应具体测试名（`PresentationHostCompositionTests`/`PresentationWindowTests`/`PresentationInputRoutingTests`/`SettingsDraftSyncTests` 等），实施时按名引用即可；两生成器 `--check`、check.ps1、verify_pins 15/15、临时根、旧证据字节不变均在列。

TODO 标记在 `ready` 阶段合法（协作协议 §4.3），进 in_review 前须替换——维持既有治理口径。

## 7. 风险与实施顺序

- **I-5 headless 可验证性**：可行。resolver 层 9 例既有（含 fake 平台源、迁移、判据②③）；UI 消费层以 Transition/Animation 属性断言+可控时钟验证；「无定时器泄漏」有 `FocusRingBehaviourTests.cs:85` 同型先例。
- **I-4 有效属性断言**：可行。headless 下可断言 Background/BorderBrush/Opacity/RenderTransform 与资源引用；伪类可用 Classes.Set/输入模拟驱动；不可验证格 NOT_RUN 口径已冻结，防假 PASS。
- **I-6 等价性**：断言（行数记录+既有测试不改弱+全量不退化+引用路径兼容）+「纯移动」内容限定可判定；建议纯移动 commit 辅以 move 检测（如 `git diff --color-moved`）留证，属实施细节非范围缺口。
- **I-7 输出保护**：断言（默认运行 git status 干净+opt-in 生效+旧 PNG SHA 对照）直接可执行；口径张力见 R3-002。
- **I-12/I-13/I-14 纯 UI**：三者的现有代码支点（NavigateSpace、占位先例、IsSourceUnavailable）已实测确认，不依赖端口成立。
- **冻结可行性结论**：Codex 单 Agent 可在 allowed_paths 内按「I-6 独立首个 commit → Batch A（I-12/I-14/I-9/I-10/I-1/I-2/I-3）→ Batch B（I-4/I-5/I-11/I-13/I-7/I-8）」完成，每子批独立 delivery commit 可复核；「I-6 先于 I-4/I-5」已明文（Task:89）。I-7 位于 Batch B 尾部，在此之前全量验证必须沿用排除 filter——该口径已冻结，无歧义。安全回归 1137→1138 起点 + FEA-07 非回归矩阵 + 旧证据字节不变构成充分的关闭标准；无 P0/P1 阻塞冻结。

## 8. Findings

以下 4 项均为 **P2（实施期处置，不阻塞冻结）**，处置交 DSH/实施记录跟踪：

| ID | 级别 | 证据 | 问题与影响 | 最小建议 |
|---|---|---|---|---|
| R3-001 | P2 | `doc/REBASELINE_PLAN.md:39`（当前 DAG 段）vs `:37`、`:22`、STATUS:7 | R2-005 残留：行 39 仍写「第一批范围 v1 已释放、scope-r1 复核中」，与同文件上游 v3/scope-r3 表述自相矛盾；该行属活文本非历史快照段，误导后续 Reality Check。 | DSH 冻结范围 v3 时同步刷新该行为 v3/scope-r3 表述；历史快照段不动。 |
| R3-002 | P2 | Task:80；`VisualEvidenceTests.cs:390–396`（默认写 `%TEMP%\nm-designsystem-evidence`） | I-7「默认全量不写 PNG」字面与 DS VisualEvidenceTests 现状有张力：其默认写系统临时目录（不污染 git、不触旧 pin），断言「默认运行后 git status 干净」无法区分它是否写了 PNG。实现者可能按字面扩大 diff 或留下字面违约。 | DSH 固定口径：I-7 禁止对象=仓库/证据面（`verification/**`）PNG 写入，`%TEMP%` 渲染输出不在禁止之列；或明示 DS VisualEvidenceTests 一并 opt-in——二选一写入实施记录。 |
| R3-003 | P2 | Task:83；`07-page-reader.md:23,62` | I-10 断言「无操作超时隐藏；键盘/指针唤醒；全屏下一致」未固化设计参数，且「工具条」未区分两类条：顶部/底部条=2s 淡出+点击中部切换+reduce 直接切换（07:23）；右侧浮动工具条=常显可隐藏（07:62）。一刀切实现会违反 07:62。 | 实施时按 07 §1 分列两类条断言；2s、点击中部切换、reduce 直接显隐入断言表。 |
| R3-004 | P2 | Task:81,115；r2 报告「Current 保护必须是行为验证」（allowed_paths 核对第 5 点）；DS `RealAppResourceStackTests.cs` 既有 | Current V2 保护以静态断言（`Views/V2/**` 无 diff）+语义禁改为主，缺行为对照：同进程 Fluent→Current 切回后有效资源/焦点环/动画不被 DS 改动污染未列为断言。 | I-8/I-11 实施时补 Current 对照行为断言或复用既有资源栈测试入证据；不扩写域。 |

## 9. 结论

**Decision：approved（P0=0 / P1=0 / P2=4）。范围 v3 可以冻结。**

- R2-001/R2-002/R2-003（三项 P1）全部闭环，证据见 §3；R2-004/R2-006 闭环；R2-005 基本闭环（残留 R3-001 为同文档一行指针滞后，不改变权威事实认定）。
- IN=I-1…I-14 与 BLOCKED=B-1…B-7 对原残项 R-1…R-9 穷尽、互斥、唯一归属；IN 项全部有真实代码支点与可验证断言，BLOCKED 项事实依据经代码核实成立、恢复条件齐备；无 DEFERRED 的二分在本卡成立。
- I-8 已与冻结设计（01:56/03:62）逐字对齐；I-3/I-5/I-11 判据与冻结设计 02/03/08 原文一一对应。
- 基线口径（1137/0/57 排除口径 → I-7 后 1138/0/57 起点、禁止虚称无过滤复跑）诚实且与本报告替代证据链一致。
- 本轮构建/测试因 ZCode headless plan 只读边界 NOT_RUN，已如实披露并以「自 `04d7c79e3` 零代码漂移 + scope-r2 同代码实跑记录」构成等价证据链；DSH 释放实施时无需因本报告补跑（实施首个 commit 前的 Reality Check 按惯例重做即可）。
- 最小返修集：**无 P0/P1 返修**。R3-001…R3-004 作为实施期处置项由 DSH 在冻结/实施记录中逐项跟踪，不阻塞冻结与派发。

**推荐下一步**：DSH 处置本报告（P2×4 登记跟踪、顺手修 R3-001 一行指针）→ 冻结范围 v3 → 按 W-10 派 Codex 实施（若届时 Codex 额度未恢复，按 §78 故障转移规则改派 ZCode 并在 Task 卡标注）；实施顺序 I-6 → Batch A → Batch B，impl-r1 由 fresh 独立上下文复核。可直接转发：

> Task：FEA-06-RESIDUAL-1 scope-r3 处置与范围 v3 冻结释放；Agent：DSH（Lead/范围作者）。Recovery point：`G:\CODEX\New Manga`，main 主仓，base=`82529a3d5864a39f362e414b67bca774d743f862`，被审 head=`e71585834`（scope-r3 报告落盘后 HEAD 应为该报告提交）。处置 approved/P2×4：R3-001 修 Plan:39 残留指针为 v3/scope-r3；R3-002 固定 I-7 口径（禁止对象=verification/** 证据面 PNG 或明示 DS VisualEvidenceTests 一并 opt-in）；R3-003/R3-004 登记为实施期断言要求（I-10 分列两类条+2s/中部切换参数、I-8/I-11 补 Current 行为对照）。冻结范围 v3 后按 W-10 派实施：I-6 纯移动首个 commit → Batch A（I-12/I-14/I-9/I-10/I-1/I-2/I-3）→ Batch B（I-4/I-5/I-11/I-13/I-7/I-8）；交付时安全回归 1137/0/57 排除口径 → I-7 后 1138/0/57 起点、FEA-07 非回归矩阵（引用 scope-r2 报告行 125 具体测试名）、两生成器 --check、check.ps1、verify_pins、旧 FEA-06 证据字节不变；impl-r1 fresh 独立上下文复核后 DSH 集成验证。
```

---

**审查执行摘要**（落盘报告之外的说明）：我以 ZCode 独立只读上下文完成了 scope-r3 复核。git 全套检查与代码/设计逐项核对均实跑成功；`dotnet build/test`、两生成器 `--check` 与治理脚本因本轮 headless plan 模式只读边界被权限层拦截（每条均有实际尝试与拒绝记录），报告中已如实披露，并以「自 scope-r2 实跑基线 `04d7c79e3` 以来零代码漂移（git diff 实证）+ scope-r2 同代码实跑记录」构成替代证据链，未冒充本轮复跑。三项 P1 全部闭环，结论 **approved（P0=0/P1=0/P2=4）**，范围 v3 可冻结；四个 P2（Plan:39 指针残留、I-7 口径张力、I-10 参数精度、Current 行为对照）为实施期处置项，不阻塞冻结。推荐下一步：DSH 处置本报告并冻结范围 v3，按 W-10 派 Codex 实施（Codex 额度未恢复则按既定故障转移规则改派 ZCode）。
