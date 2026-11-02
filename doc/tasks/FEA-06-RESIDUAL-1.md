---
id: FEA-06-RESIDUAL-1
title: Fluent 四页规格补齐（FEA-06 AC1–AC7 residual，第一批）
kind: implementation
governance_version: 3
status: in_progress
approval: scope_review_r3_approved_2026-11-02（范围 v3 冻结；P2×4 实施期处置）
suggested_owner: codex
owner: codex
reviewer: scope-r3 **approved**（ZCode CLI，P0=0/P1=0/P2=4；报告 doc/reviews/FEA-06-RESIDUAL-1-scope-r3.md）；当前 Appointment：**实现续作（DSH）→ 待独立 impl Review**（Codex 00:23 恢复优先，否则 ZCode 03:02）（Codex 额度 00:23 恢复、ZCode 额度 03:02 恢复；双 agent 均不可用，实施期独立 Review 待恢复后补）
depends_on:
  - FEA-06
  - FEA-07
base_commit: 82529a3d5864a39f362e414b67bca774d743f862
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: 981719a13（Batch B 收尾：I-4 有效属性+disabled/I-5 矩阵+消费/I-8/I-11 含 shell 浮层焦点；hover 视觉/decorative D-8 NOT_RUN）
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-06-RESIDUAL-1
allowed_paths:
  - doc/tasks/FEA-06-RESIDUAL-1.md
  - apps/desktop-avalonia/src/NewManga.App/Views/Fluent/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/**
  - apps/desktop-avalonia/src/NewManga.App/Styles/AppStyles.axaml
  - apps/desktop-avalonia/src/NewManga.App/Controls/FluentUi.cs
  - apps/desktop-avalonia/src/NewManga.DesignSystem/Accessibility/**
  - apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/**
  - apps/desktop-avalonia/src/NewManga.DesignSystem/Theming/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/**
  - verification/FEA-06-RESIDUAL-1/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-06-RESIDUAL-1-*.md
  - doc/handoffs/FEA-06-RESIDUAL-1-*.md
---

# FEA-06-RESIDUAL-1：Fluent 四页规格补齐（FEA-06 AC1–AC7 residual，第一批）

## 来源与授权链

- **来源**：`FEA-06` done（集成 `b26840acd`；scope-r3 + impl-r2 approved）；AC8–AC10 MET，**AC1–AC7 为 PARTIAL**，经 DSH 处置转为本卡 residual。
- **设计基线**：`doc/design/fluent-v1/`（FROZEN v1.0.0，唯一设计输入；偏差走 v1.1 重冻结）。本批**只消费既有设计**：motion 三态 `auto/full/reduce` × 三类 `navigation/feedback/decorative`（`02-motion.md` §1–§2）、焦点环 2px/offset 1/高对比 3px（`03-accessibility.md:53,62`）、层次阴影（`01-design-tokens.md` §2.3）、组件清单（`10-component-inventory.md` §1–§3）。
- **前序依赖**：`FEA-07` closed_with_limitations（集成 `aedc7251c`）：本批使用其稳定窗口、切换/退出保护、memento 边界，不改其语义。
- **Owner**：Codex（沿用用户 2026-11-02 指派）。实现完成后由 DSH 指派 fresh Codex CLI 独立上下文做 impl 复核。
- **顺序**：用户 2026-11-02 裁决「按原来的顺序进行」→ FEA-07 已先行关闭；本卡为下一节点。
- **范围版本**：scope-r1 changes_requested（P1×3/P2×3）→ 范围 v2 → scope-r2 **changes_requested（P0=0/P1=3/P2=3；R2-001…R2-006）** → DSH 处置为 **范围 v3**（本文件），待 scope-r3 独立复核后冻结。scope-r1/r2 报告原字节保留。

## 残项清单（来自 FEA-06 impl-r1/r2 与 Closeout）

| # | AC | 残项（原始表述） | 原始依赖/阻塞 |
|---|---|---|---|
| R-1 | AC1 | 分栏折叠、UI memento 恢复、200% DPI 原生验收、原生桌面验收 | FEA-07；原生验收 D-1 |
| R-2 | AC2 | 回收站入口空面板、扫描进度逐项、错误卡「控制台入口」、满态统计 | FEA-12/FEA-10 端口 |
| R-3 | AC3 | Run 投影/暂停停止、BatchMatrix 数据绑定、9 行状态、未保存圆点、冲突「查看对照」 | FEA-10；未保存圆点可用现有状态 |
| R-4 | AC4 | 双页第二图、滚动模式、工具条自动隐藏、源不可用只读警示 | FEA-09/11；工具条/警示本体为纯 UI |
| R-5 | AC5 | 网络超时/并发、备份字段、完整错误/部分状态、离开未保存确认/Esc | FEA-13；确认流不依赖端口 |
| R-6 | AC6 | 组件 full 状态（normal/hover/pressed/disabled/浮层开关） | 本卡 UI |
| R-7 | AC7 | 焦点环、三类 motion、原生 a11y 验收 | 本卡 UI；原生 a11y D-1 |
| R-8 | P2 | 四 Fluent VM 拆分（1408 行）、PNG 采证改 opt-in | 本卡技术债 |
| R-9 | P2 | `Nm.Elevation.*` 阴影（令牌已存在，非外部阻塞） | 本卡 UI |

## 范围 v3：穷尽、互斥的 IN / BLOCKED（本批无 DEFERRED）

> 规则：每个子项只落一种状态；IN 必须有可验证断言；BLOCKED 必须写依赖 Task 与恢复条件。**本批不设 DEFERRED**：所有可实施子项均 IN；所有缺数据/硬件依赖子项均 BLOCKED。禁止模拟数据/假实现。

### A. 第一批 IN（本卡实施）

| 子项 | 原残项 | 内容 | 可验证断言 |
|---|---|---|---|
| I-1 | R-1a | Fluent 页面级 UI memento：Shelf/Workbench 分栏折叠状态、列表滚动偏移、选中项在同一运行期内的 frontend 切换（FEA-07 缓存树复用）与页面往返后保留；不落盘 | 切换 away/back 与页面往返后三字段恢复；新窗口强制默认值；无数据文件写入（临时根） |
| I-2 | R-1b | Shelf/Workbench 列表-详情分栏折叠：折叠/展开按钮、分隔条约束、键盘（Enter/Space+方向键）可达、与 I-1 memento 联动 | 折叠后详情区 0 宽且列表占满；最小/最大约束；键盘切换；恢复断言；FEA-07 窗口/切换不退化 |
| I-3 | R-5a | 设置页离开确认：**三分支**（保存并离开 / 丢弃并离开 / 取消）+ **保存失败保护**（留页、draft 保留、错误可见）；导航离开与 Esc 的优先级；不绕过 FEA-07 退出保护 | 三分支逐项断言（保存调用/host 写入发生、丢弃清 draft、取消留在页面且 draft 保留）；保存失败注入后留页/留稿/错误可见；Esc 在浮层内=取消、页面内=触发离开流；FEA-07 `IPresentationExitState` 聚合仍阻断窗口关闭 |
| I-4 | R-6 | 组件 full 状态：先按 `10-component-inventory.md` §1–§3 冻结「组件 × 适用状态」表，再实现 normal/hover/pressed/disabled/浮层开合；断言**有效属性**（Background/BorderBrush/Opacity/Transform 与资源引用）而非字符串选择器存在；disabled 验命令零触发；浮层验焦点移入/返还 | 组件×适用状态表入证据；每格有效属性/命令断言；无法 headless 验证的视觉格标 NOT_RUN，不以选择器存在计 PASS；无 Current V2 样式改动 |
| I-5 | R-7a | motion：按 `02-motion.md` 三态 `auto/full/reduce` × 三类 × 分类开关矩阵实现；auto 跟随系统动画设置（读取失败→full+warning）；用户显式优先；`motion.categories[x]=关` 在 full 下按 reduce 列执行 | 表驱动断言（fake 系统开/关 × mode auto/full/reduce × 三类 × 分类开/关）逐格匹配设计参数表（navigation 240/180/200/160ms 或 0ms；feedback 颜色保留/无位移/无缩放；decorative 禁用）；无定时器泄漏 |
| I-6 | R-8a | 四 Fluent VM 拆分：`ViewModels/Fluent/FluentPageViewModels.cs`（1408 行）→ Shelf/Workbench/Reader/Settings 四文件 + 共享基类，纯移动/等价重构 | 文件结构与行数记录；既有测试不改弱；全量基线不退化；视图引用路径兼容 |
| I-7 | R-8b | PNG 采证测试改显式 opt-in：**禁止对象 = 仓库/证据面 PNG 写入（`verification/**`，尤其 `verification/FEA-06/screens/**` 已 pin 文件）**；opt-in 输出到 `verification/FEA-06-RESIDUAL-1/png/`；`%TEMP%` 渲染输出（如 DS `VisualEvidenceTests`）不属禁止范围（scope-r3 R3-002 口径） | 默认运行后 `git status` 干净（仅 `%TEMP%` 允许）；opt-in 开关生效写本卡证据目录；旧 FEA-06 PNG 字节不变（SHA 对照） |
| I-8 | R-9 | 消费现有 `Nm.Elevation.*` 令牌（设计 01 §2.3）替换 Fluent 表面 1px 边框；**standard 与 reduce 均保留阴影令牌不变**；仅高对比模式回退 1px 边框（设计 03:62）；Current V2 不变 | 表面使用 Elevation 令牌（样式断言）；standard+reduce 阴影仍为原令牌；高对比→1px 边框；`Views/V2/**` 无改动；**Current 对照行为断言**（同进程切回 Current 后资源/焦点环/动画不被污染，复用 `RealAppResourceStackTests` 基础）；设计值对照表入证据 |
| I-9 | R-3b | 未保存圆点（dirty 指示）在设置/工作台等设计指定页面的可见状态（现有 dirty 状态，不新增端口） | dirty=true 显示/false 隐藏；切前端/往返后状态正确；无假数据 |
| I-10 | R-4b | Reader 工具条自动隐藏（设计 07）：**顶部/底部条** = 无操作 2s 淡出、点击中部切换显隐、reduce 直接切换（07:23）；**右侧浮动工具条** = 常显可隐藏（07:62）；纯 UI，不涉及真实数据 | 两类条分别断言：2s 超时/点击中部切换/reduce 直接显隐；右侧条常显语义；键盘唤醒；全屏下一致 |
| I-11 | R-7b | 焦点环：`Nm.Focus.Ring.Width`=2 / `Offset`=1 / 高对比 3px（设计 03:53,62）；浮层打开焦点移入首个可聚焦控件、关闭返还触发控件；隐藏/不可见控件移出 Tab 序 | 焦点环几何/颜色断言；高对比 3px；浮层焦点移入与返还；隐藏控件不在 Tab 序；覆盖四页至少各 1 个焦点场景；**Current 对照行为断言**（切回 Current 后焦点环不被 Fluent 改动污染） |
| I-12 | R-2b | 控制台入口导航与错误卡入口态：`SpaceConsole` 空间入口可用导航（现有 shell surface），Tab 页占位按设计；错误卡「控制台入口」按钮导航到控制台空间；**控制台内容投影仍由 B-1/B-6 承担** | 入口点击导航到 Console 空间/页；错误卡入口按钮可达；占位态无假数据；导航不破坏 FEA-07 输入/切换 |
| I-13 | R-3c | 9 行状态**视觉骨架**（无数据部分的占位/禁用态，按设计 03 工作台状态表）；**数据绑定归 B-2**，不重复归属 | 9 行视觉/禁用态登记；无数据时安全空态；不与 B-2 重复认领 |
| I-14 | R-4c | 源不可用只读**警示本体**（banner/文案/禁用操作视觉，按设计 07）；恢复动作归 B-3 | 警示可见/文案/禁用态断言；不涉及真实恢复动作；不依赖数据面 |

**实施子批**：Batch A = I-12/I-14/I-9/I-10/I-1/I-2/I-3（功能 UI，先做 I-6 拆分）；Batch B = I-4/I-5/I-11/I-13/I-7/I-8（状态/动效/焦点/技术债）。每子批一个 delivery commit，可独立复核；I-6 先于 I-4/I-5 完成。**基线口径**：pre-I-7 安全回归 = **1137/0/57**（排除写旧证据的 `FluentPages_RenderHeadlessPngEvidence`，见 scope-r2 Reality Check）；I-7 落地后恢复全量 **1138/0/57** 起点（新增测试另行计数），不得声称「无过滤全量已复跑」除非实际运行。

### B. BLOCKED（外部依赖/硬件，不用假实现）

| 子项 | 原残项 | 阻塞 | 恢复条件 |
|---|---|---|---|
| B-1 | R-2 回收站恢复/删除/扫描进度 | FEA-12、FEA-10 | 对应端口 Task done + 契约冻结 |
| B-2 | R-3 Run 投影/暂停停止/BatchMatrix 数据绑定/9 行状态数据绑定 | FEA-10 | Run/批量端口 + 真实投影 |
| B-3 | R-4 双页第二图/滚动模式/源不可用**恢复动作** | FEA-09/11 | 阅读器数据面端口 |
| B-4 | R-5 备份目录/频率字段、网络超时/并发、完整错误/部分状态**数据** | FEA-13 | 备份字段与错误端口 |
| B-5 | R-1c 200% DPI、原生桌面验收；R-7 原生 a11y；AC8 原生截图 | D-1（无硬件） | 硬件可用或用户书面 waiver |
| B-6 | R-2 满态统计 | FEA-12 | 真实统计数据面 |
| B-7 | R-3 冲突「查看对照」数据 | FEA-10 | 冲突投影端口 |

## scope-r3 P2 处置（2026-11-02，实施期跟踪）
- **R3-001**：PLAN 当前 DAG 段 v1/scope-r1 残留 → 冻结时已刷新为 v3/scope-r3（历史快照段不动）。
- **R3-002**：I-7 口径固定为「禁止仓库/证据面（`verification/**`）PNG 写入；`%TEMP%` 渲染输出允许；旧 FEA-06 pin 不得覆盖」。
- **R3-003**：I-10 按设计 07 分「顶部/底部条（2s 淡出、点击中部切换、reduce 直接切换）」与「右侧浮动工具条（常显可隐藏）」两类断言。
- **R3-004**：I-8/I-11 增加 Current 对照行为断言（复用 `RealAppResourceStackTests` 基础），不扩写域。
## 验收标准

- [ ] **AC1（四页与 Shell residual）**：I-1/I-2/I-9/I-10/I-12/I-13/I-14 逐项完成并登记断言；B-1/B-2/B-3/B-6/B-7 按 BLOCKED 登记原因与恢复条件，不写达成。 `<<TODO>>`
- [ ] **AC2（组件/动效/焦点/A11y）**：I-4（组件×状态有效属性断言）/I-5（三态×三类×分类矩阵）/I-11（焦点环/浮层焦点/Tab 序）完成；B-5 原生 a11y 按 BLOCKED 登记。 `<<TODO>>`
- [ ] **AC3（设置与确认流）**：I-3 三分支 + 保存失败保护 + FEA-07 退出保护不退化；B-4 登记 BLOCKED。 `<<TODO>>`
- [ ] **AC4（技术债）**：I-6（1408 行拆分等价重构）/I-7（PNG opt-in，不覆盖旧 pin）/I-8（Elevation 消费；standard+reduce 阴影不变、仅高对比回退边框）完成。 `<<TODO>>`
- [ ] **AC5（证据与回归）**：`verification/FEA-06-RESIDUAL-1/**` 日志/矩阵；安全回归基线 **1137/0/57**（PNG 用例排除，直接原因记录）→ I-7 后 **1138/0/57** 起点且新增测试只增不减；FEA-07 非回归矩阵（切换往返/退出保护/全屏/输入/关闭聚合）；两生成器 `--check`；check.ps1 PASS；verify_pins 15/15；测试均用临时根；旧 FEA-06 证据字节不变。 `<<TODO>>`

## 禁止范围

- 不改 Core/契约/schema/用户数据/生成物（`DesignSystem/Generated/**` 等）/冻结设计 `doc/design/**` 字节/组合根/`FrontendSelector`/Current V2（`Views/V2/**`、`ViewModels/V2/**`、`Shell/V2/**`）。
- 不改共享 `KeyMap`、`IPresentation*`、`PresentationWindow`/`FrontendHostCoordinator`/`ExitCoordinator` 等 FEA-07 稳定窗口接线；确需共享辅助改动时先停等 DSH 裁决。
- 不改全局主题色/布局以至于影响 Current V2；焦点环仅做 Fluent 页面接入，`NewManga.DesignSystem` 唯一写者语义不变。
- 不 push；不扩大设计基线之外交互；不写真实 `%APPDATA%`。
- BLOCKED 子项**不得**用模拟数据/假实现充数；不把「字符串选择器存在」当视觉 PASS（无法验证的格标 NOT_RUN）。

## 依赖与分工

| 依赖 | 状态 | 本批用法 |
|---|---|---|
| FEA-06 | done（`b26840acd`） | residual 来源、设计基线 `doc/design/fluent-v1/` |
| FEA-07 | closed_with_limitations（`aedc7251c`） | 稳定窗口、切换/退出保护、memento 边界（只读使用，不改） |
| FEA-09/10/11/12/13 | 未创建/未 done | 只作为 BLOCKED 承接方；本批不依赖其运行，不改 Plan 依赖 |

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际 | 证据 |
|---|---|---|---|---|
| AC1/AC3 功能 UI | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests`（Avalonia.Headless，临时根） | .NET 9 | NOT_RUN | 待补 |
| AC2 组件/动效/焦点 | 同上 + `NewManga.DesignSystem.Tests`（令牌/焦点/motion 解析） | .NET 9 | NOT_RUN | 待补 |
| AC4 技术债 | 拆分后全量基线不退化；PNG 默认运行后 `git status` 干净、旧 SHA 不变 | .NET 9 | NOT_RUN | 待补 |
| AC5 回归/治理 | 安全回归 `--filter "FullyQualifiedName!~FluentPages_RenderHeadlessPngEvidence"`（1137/0/57）→ I-7 后全量 1138/0/57 + 两生成器 `--check` + `check.ps1` + `verify_pins` + FEA-07 非回归子集 | 全量 | NOT_RUN | 待补 |

## Review Appointment

- **scope-r3**：**ZCode CLI**（Codex CLI 额度用尽，按用户 2026-11-02 故障转移裁决；headless `--mode plan` 只读，报告由 DSH 原样落盘为 `doc/reviews/FEA-06-RESIDUAL-1-scope-r3.md`）。P0/P1=0 后 DSH 冻结范围 v3 并释放实施。
- **impl-r1**：实现完成后 fresh Codex CLI 只读全量复核（只写 `doc/reviews/FEA-06-RESIDUAL-1-impl-r1.md`）；DSH 处置后集成验证 → done/closed_with_limitations。
- 作者（Codex 实现会话）不得自审；DSH 不审自己实现。

## Resource Manifest

- 关闭时逐类填写（当前 pending）：worktree（无 linked worktree，main 内联）、verification artifacts（`verification/FEA-06-RESIDUAL-1/**` PRESERVE_REFERENCED）、task-env（未创建）、dataset/model/test-material（未创建/未使用）、temp（测试临时根，运行后清理）、agent-output（无）、exchange（无）、user data（未访问）。

## 实施记录（Batch A，2026-11-02）

- 实现执行：ZCode CLI（`--mode yolo`，Codex 额度故障转移）；会话在收尾前崩溃（`0xC0000409`），未写证据/Handoff；工作树遗留 WIP。
- DSH 收尾：核对全部改动在 allowed_paths；恢复被默认全量运行覆盖的 `verification/FEA-06/screens/{shelf,workbench,reader}.png`（HEAD 字节）；修 1 个异步测试竞态（`PumpUntil`，实现语义未改）；补写 Handoff 与证据日志。
- commits：`83fa1b186`（I-6 四 VM 等价拆分，1408 行→四文件）；`9337cbbe1`（Batch A 功能 + 证据/Handoff，I-1/I-2/I-3/I-9/I-10/I-12/I-13/I-14）。
- 验证：build 0/0；新增测试 33/33；安全全量（排除 PNG 用例）**1170/0/57**（基线 1137 + 33）；FEA-07 非回归子集全绿；TokenGen/ThemeGen up-to-date；check PASS(3)；pins 15/15；证据 `verification/FEA-06-RESIDUAL-1/batch-a-verification.log`（SHA `4a7744f1…`）。
- 未完成（Batch B）：I-4 组件 full 状态、I-5 motion、I-7 PNG opt-in、I-8 Elevation、I-11 焦点环/浮层焦点/Tab 序。I-7 落地前全量验证必须排除 `FluentPages_RenderHeadlessPngEvidence`，不得声称无过滤全量已复跑。

## Batch B 记录（2026-11-02 深夜）

- **I-7 完成**：`ce0bee67d`（`FluentPages_RenderHeadlessPngEvidence` 默认不写仓库/证据面 PNG；`NEWMANGA_CAPTURE_FLUENT_PNGS=1` opt-in 写 `verification/FEA-06-RESIDUAL-1/png/`；默认路径保留帧尺寸断言；`verification/FEA-06/screens/**` 字节未变）。验证：默认测试通过、opt-in 生成 4 PNG、git status 干净。
- **Batch B 部分完成**（`a315bee02`，DSH 实施）：I-5（`MotionTimings` 冻结参数表 + FluentShell 页面过渡消费 + 运行时设置重放）、I-8（`Nm.Elevation.*` 消费 card/detail/drawer/dialog + 高对比运行时注入 focus=3px/Elevation 置空，生成文件与 V2 零改动）、I-11 部分（焦点环 2px↔高对比 3px 断言、设置页离开浮层焦点移入/取消返还）、I-4 部分（组件×状态声明覆盖测试 + DesignRules 阴影规则对齐冻结设计）。全量无过滤 **1177→1178/0/57**（续作：I-4 segmented/slider/tabitem + I-11 隐藏控件焦点 + I-5 feedback 过渡）；证据 `batch-b-verification.log`（SHA `df752887…`）。
- **未完成（NOT_RUN）**：I-4 其余组件状态（IconButton/ToggleSwitch/Slider/Segmented/TabStrip/SearchField/CommandPalette/ContextMenu/Tooltip/Toast/BatchMatrix/RunProjectionBar）与 hover/pressed 视觉截图；I-11 隐藏控件 Tab 序显式断言；I-5 feedback/decorative 实际动画消费。当前**双 agent 额度耗尽**（Codex 00:23、ZCode 03:02 恢复），独立 Review 与最终验收待 agent 恢复后补。
- **待裁决 D-7**：故障转移候选（Codex/ZCode）同时不可用时，是否允许 DSH 直接实施 Batch B 剩余项并在 agent 恢复后补独立 Review。DSH 推荐：**允许**（否则任务停摆；变更均在冻结范围/写域内，保留可复核提交粒度）。依据：用户 2026-11-02「可推进项不耗尽不停」+ 协作协议允许 DSH 作为 Lead/Integrator 实施（不得自审，Review 留待独立 agent）。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-FEA06R1-BATCHA | AC1/AC3/AC5 | `verification/FEA-06-RESIDUAL-1/batch-a-verification.log` | `9337cbbe1` | `4a7744f1128c861b6a4fb9e7ddae55284c76dadf3f6b19b7fb86b2a343e72e08` | CANONICAL |
| EV-FEA06R1-I7 | AC4/AC5 | `apps/desktop-avalonia/tests/NewManga.App.Tests/FluentPageTests.cs` | `ce0bee67d` | `f3563e5e5fc5d8d8df53d170c9778e84e96d53c13810e983cc10a3634932a560` | SOURCE_PIN |
| EV-FEA06R1-BATCHB | AC2/AC4/AC5 | `verification/FEA-06-RESIDUAL-1/batch-b-verification.log` | `918e4a2e3` | `da5ecaeb2c88cf22f63b1dedb401607db980438c1177af6331eee3e52b2cc374` | CANONICAL |
| EV-FEA06R1-MATRIX | AC2 | `verification/FEA-06-RESIDUAL-1/component-state-matrix.md` | `981719a13` | `4e16174f40ed2829918759fc0fbd5d3aa8d985d2f1cbf951483c00c8215f6d0c` | CANONICAL |
| EV-FEA06R1-ITEMSTATUS | AC1/AC2 | `verification/FEA-06-RESIDUAL-1/item-status.md` | `b79241c9a` | `abb93fd7c8bdc1b37f707a60303c06bce7ce19659e1b9f26a7189e1e98f21350` | CANONICAL |
| EV-FEA06R1-ACCOV | AC1–AC5 | `verification/FEA-06-RESIDUAL-1/ac-coverage.md` | `922a116ca` | `4288b2fa04da48540a99475fec6dc1c228a8e89fdfe1894ff70796812357826a` | CANONICAL |

## 待裁决（DSH 已按推荐口径推进，不阻塞）

- **D-7（已裁决执行）**：双故障转移候选（Codex/ZCode）同时额度耗尽时，允许 DSH 在冻结范围/写域内继续实施并在 agent 恢复后补独立 Review。DSH 推荐/采用：允许（不得自审）；依据：用户 2026-11-02「可推进项不耗尽不停」+ 协作协议允许 DSH 作为 Lead/Integrator 实施。结论记录于 checkpoint §81/§83.1。
- **D-8（新，待独立裁决/Review 确认）**：decorative 类别实际动画（书架背景渐变 8s 循环、阅读器翻页粒子 400ms、空态插画漂浮 6s）**暂缓实现**，仅保留参数表、类别开关与 reduce 禁用语义。DSH 推荐：**暂缓并转后续视觉任务（ZCode 主责）**。依据：三类均为视觉创作型动画，需视觉设计/像素评审与 reduce 降级截图，headless 下无法证明“未改变布局/层级/可读性”；在无独立视觉 Review 前提下由 DSH 自创会引入不可复核风险。当前 I-5 其余判据（①–④ 及旧值迁移相关断言）已由 `MotionTimings`/`MotionResolver` 测试覆盖。
- **Review 准备**：独立 impl Review prompt 已备好：`G:\CODEX\New Manga.workspace\FEA-06-RESIDUAL-1\impl-review-prompt.md`；Codex 探针 23:31 仍限额至 2026-11-03 00:23，恢复即派发。

## Closeout Record

- 待关闭时填写。
