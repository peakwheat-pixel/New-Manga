---
id: FEA-06-RESIDUAL-1
title: Fluent 四页规格补齐（FEA-06 AC1–AC7 residual，第一批）
kind: implementation
governance_version: 3
status: ready
approval: scope_review_r1_changes_requested_2026-11-02_scope_v2_pending_scope_r2
suggested_owner: codex
owner: codex
reviewer: codex-cli（scope-r1 changes_requested，P0=0/P1=3/P2=3，已处置为范围 v2；报告 doc/reviews/FEA-06-RESIDUAL-1-scope-r1.md；当前 Appointment：scope-r2 待派）
depends_on:
  - FEA-06
  - FEA-07
base_commit: 82529a3d5864a39f362e414b67bca774d743f862
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-06-RESIDUAL-1
allowed_paths:
  - doc/tasks/FEA-06-RESIDUAL-1.md
  - apps/desktop-avalonia/src/NewManga.App/Views/Fluent/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/**
  - apps/desktop-avalonia/src/NewManga.App/Styles/AppStyles.axaml
  - apps/desktop-avalonia/src/NewManga.App/Styles/FluentUi.cs
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

- **来源**：`FEA-06` done（集成 `b26840acd`；scope-r3 + impl-r2 approved）；AC8–AC10 MET，**AC1–AC7 为 PARTIAL**，经 DSH 处置转为本卡 residual（见 `doc/tasks/FEA-06.md` Closeout Record 与 `doc/reviews/FEA-06-impl-r1.md` / `-r2.md`）。
- **设计基线**：`doc/design/fluent-v1/`（FROZEN v1.0.0，唯一设计输入；偏差走 v1.1 重冻结）。本批只消费既有设计，不新增设计决策。
- **前序依赖**：`FEA-07` closed_with_limitations（集成 `aedc7251c`，全量 1138/0/57）：本批使用其稳定窗口、切换/退出保护、memento 边界，不改其语义。
- **Owner**：Codex（沿用用户 2026-11-02 指派）。实现完成后由 DSH 指派 fresh Codex CLI 独立上下文做 impl 复核。
- **顺序**：用户 2026-11-02 裁决「按原来的顺序进行」→ FEA-07 已先行关闭；本卡为下一节点。
- **范围版本**：scope-r1（2026-11-02）**changes_requested，P0=0/P1=3/P2=3** → DSH 处置为 **范围 v2**（本文件），待 scope-r2 独立复核后冻结。scope-r1 报告原字节保留。

## 残项清单（来自 FEA-06 impl-r1/r2 与 Closeout）

| # | AC | 残项（原始表述） | 原始依赖/阻塞 |
|---|---|---|---|
| R-1 | AC1 | 分栏折叠、UI memento 恢复、200% DPI 原生验收、原生桌面验收 | FEA-07（窗口/memento/DPI） |
| R-2 | AC2 | 回收站入口仅空面板（恢复/删除操作缺失）、扫描进度逐项、错误卡「控制台入口」、满态统计 | FEA-12（回收站端口）、FEA-10（Run 投影） |
| R-3 | AC3 | Run 投影/暂停停止控制、BatchMatrix 数据绑定、9 行状态全实现、未保存圆点、冲突「查看对照」 | FEA-10（Run/批量端口）、FEA-07（未保存确认） |
| R-4 | AC4 | 双页第二图、滚动模式、工具条自动隐藏、源不可用只读警示 | FEA-09/11（阅读器数据面） |
| R-5 | AC5 | 网络超时/并发、备份目录/频率字段、完整错误/部分状态、离开未保存确认/Esc | FEA-13（备份字段）、FEA-07（离开确认） |
| R-6 | AC6 | 组件 full 状态（normal/hover/pressed/disabled/浮层开关）逐项补齐 | 本卡 UI |
| R-7 | AC7 | 焦点环、三类 motion 状态覆盖、原生 a11y 验收 | 本卡 UI + 原生验收 |
| R-8 | P2 | 四 Fluent VM 拆分（`FluentPageViewModels.cs` **1408 行**）、PNG 采证测试改 opt-in | 本卡技术债 |
| R-9 | P2 | `Nm.Elevation.*` 阴影样式（当前 1px 边框替代） | 见 I-8：令牌已存在，非外部阻塞 |

## 范围 v2：穷尽、互斥的 IN / DEFERRED / BLOCKED

> 规则：每个子项只能落在一种状态；IN 子项必须有可验证断言；DEFERRED = 可在本卡内实现但本批不做（写明承接时点/Owner）；BLOCKED = 依赖未落地端口/硬件（写明依赖 Task 与恢复条件）。禁止用模拟数据或假实现填充 BLOCKED/DEFERRED 项。

### A. 第一批 IN（本卡实施）

| 子项 | 原残项 | 内容 | 可验证断言 |
|---|---|---|---|
| I-1 | R-1a | Fluent 页面级 UI memento：Shelf/Workbench 分栏折叠状态、列表滚动偏移、选中项在**同一运行期**内切换 frontend（FEA-07 缓存树复用）与页面往返后保留；**不落盘**（不写用户数据/schema） | 切换 away/back 与页面往返后三字段恢复；新窗口强制默认值；断言无数据文件写入（临时根） |
| I-2 | R-1b | Shelf/Workbench 列表-详情分栏可折叠：折叠/展开按钮、分隔条最小/最大约束、键盘（Enter/Space + 方向键）可达、与 I-1 memento 联动 | 折叠后详情区 0 宽且列表占满；约束边界；键盘切换；恢复断言；FEA-07 窗口/切换不退化 |
| I-3 | R-5a | 设置页「离开未保存确认 + Esc」：dirty 设置草稿在导航离开或 Esc 时弹确认（设计 08 的确认浮层），取消留在页面、确认丢弃草稿；不得绕过 FEA-07 退出保护 | dirty→离开触发确认；取消不离开且 draft 保留；确认后草稿清除；Esc 优先级；FEA-07 `IPresentationExitState` 聚合仍阻断关闭 |
| I-4 | R-6 | 组件 full 状态：按设计 01/04 的 Fluent 组件集（按钮/输入/导航项/标签页/芯片/对话框/表面）× normal/hover/pressed/disabled/浮层开合；功能性状态（disabled/浮层/焦点）headless 断言，hover/pressed 视觉以样式选择器存在性测试 + 设计核对清单 | 每组件每状态至少 1 个样式选择器/功能断言；组件×状态表入证据；无 Current V2 样式改动 |
| I-5 | R-7 | 三类 motion（`navigation` / `feedback` / `decorative`）按设计 02 三态（full/reduced/disabled）实现并逐类断言；reduced-motion 读系统/设置 | 三类各至少 1 个断言（时长/曲线/开关生效）；三类 × 三态矩阵入证据；无动画泄漏（测试结束无定时器残留） |
| I-6 | R-8a | 四 Fluent VM 拆分：`ViewModels/Fluent/FluentPageViewModels.cs`（1408 行）→ Shelf/Workbench/Reader/Settings 四个 VM 文件 + 共享基类，纯移动/等价重构，行为不变 | 拆分后行数目标与文件结构；**既有测试不改弱**且全量 1138/0/57 全绿；公共 API 兼容（视图引用路径） |
| I-7 | R-8b | PNG 采证测试改显式 opt-in：默认全量测试**不写**任何 PNG；opt-in 输出到 `verification/FEA-06-RESIDUAL-1/png/` 或临时目录；**禁止覆盖 FEA-06 已 pin 的 PNG 路径** | 默认全量运行后 `git status` 干净；opt-in 开关生效写指定目录；旧 FEA-06 PNG 字节不变 |
| I-8 | R-9 | 消费现有 `Nm.Elevation.*` 令牌（设计 01 §2.3）替换 Fluent 表面的 1px 边框阴影；高对比/减弱模式下回退 1px 边框；Current V2 视觉不变 | 表面使用 Elevation 令牌（样式断言）；高对比回退断言；`Views/V2/**` 无改动；设计值对照表入证据 |
| I-9 | R-3b | 未保存圆点（dirty 指示）在设置/工作台等设计指定页面的可见状态（基于现有 dirty 状态，不新增端口） | dirty=true 显示、false 隐藏；切前端/往返后状态正确；无假数据 |
| I-10 | R-4b | Reader 工具条自动隐藏（设计 07 的交互部分，纯 UI，不依赖数据面） | 无操作超时隐藏、键盘/指针唤醒、全屏下行为一致；不涉及真实 Reader 数据 |

**实施子批（同一 Task 顺序交付，便于评审）**：Batch A = I-1/I-2/I-3/I-9/I-10（功能 UI）；Batch B = I-4/I-5/I-6/I-7/I-8（状态/动效/技术债）。每子批一个 delivery commit，均可独立复核；Batch B 的 I-6 可与 A 并行但必须在 I-4/I-5 前完成（避免样式/绑定反复）。

### B. DEFERRED（本卡可做但本批不做，不伪造）

| 子项 | 原残项 | 继承方/时点 | 理由 |
|---|---|---|---|
| D-1 | R-2 错误卡「控制台入口」 | FEA-10（Run/控制台投影）done 后第二批 | 入口导航与错误卡语义依赖 Run 投影端口 |
| D-2 | R-2 满态统计 | FEA-12（回收站端口）done 后第二批 | 需要真实统计数据面 |
| D-3 | R-3 冲突「查看对照」 | FEA-10 后第二批 | 依赖冲突投影数据 |
| D-4 | R-3 9 行状态全实现（数据驱动部分） | FEA-10 后第二批 | 状态行需要 Run/Batch 真实投影 |
| D-5 | R-5 网络超时/并发、完整错误/部分状态 | FEA-13 后第二批 | 依赖设置/备份真实字段与错误端口 |
| D-6 | R-4 源不可用只读警示的可交互恢复 | FEA-09/11 后第二批 | 恢复动作依赖阅读器数据面 |

### C. BLOCKED（外部依赖/硬件，不用假实现）

| 子项 | 原残项 | 阻塞 | 恢复条件 |
|---|---|---|---|
| B-1 | R-2 回收站恢复/删除/扫描进度 | FEA-12、FEA-10 | 对应端口 Task done + 契约冻结 |
| B-2 | R-3 Run 投影/暂停停止/BatchMatrix 数据绑定 | FEA-10 | 同上 |
| B-3 | R-4 双页第二图/滚动模式 | FEA-09/11 | 阅读器数据面端口 |
| B-4 | R-5 备份目录/频率字段 | FEA-13 | 备份字段契约/端口 |
| B-5 | R-1c 200% DPI、原生桌面验收；R-7 原生 a11y；AC8 原生截图 | D-1（无硬件） | 硬件可用或用户书面 waiver |

## 验收标准

- [ ] **AC1（四页与 Shell residual）**：I-1/I-2/I-9/I-10 逐项完成并登记断言证据；D-1…D-6、B-1…B-4 以 DEFERRED/BLOCKED 登记原因与承接方，不写达成。 `<<TODO>>`
- [ ] **AC2（组件/动效/A11y）**：I-4/I-5 完成，提交「组件×状态×测试」与「motion 三类×三态」矩阵；原生 a11y 按 B-5 BLOCKED 登记。 `<<TODO>>`
- [ ] **AC3（设置与确认流）**：I-3 完成（dirty 确认/Esc/取消/确认分支 + FEA-07 退出保护不退化）；D-5 登记 DEFERRED。 `<<TODO>>`
- [ ] **AC4（技术债）**：I-6/I-7/I-8 完成（1408 行拆分、PNG opt-in 不写旧证据、Elevation 消费与高对比回退）。 `<<TODO>>`
- [ ] **AC5（证据与回归）**：`verification/FEA-06-RESIDUAL-1/**` 日志/矩阵；全量 **1138/0/57 不退化**（新测试只增不减）；FEA-07 非回归矩阵（切换往返/退出保护/全屏/输入）；两生成器 `--check`；check.ps1 PASS；verify_pins 15/15；测试均用临时根。 `<<TODO>>`

## 禁止范围

- 不改 Core/契约/schema/用户数据/生成物（`DesignSystem/Generated/**` 等）/冻结设计 `doc/design/**` 字节/组合根/`FrontendSelector`/Current V2（`Views/V2/**`、`ViewModels/V2/**`、`Shell/V2/**`）。
- 不改共享 `KeyMap`、`IPresentation*`、`PresentationWindow`/`FrontendHostCoordinator`/`ExitCoordinator` 等 FEA-07 稳定窗口接线；确需共享辅助改动时先停等 DSH 裁决。
- 不改全局主题色/布局/Focus 全局 ring 以至于影响 Current V2；焦点环只做 Fluent 页面接入（`NewManga.DesignSystem` 唯一写者语义不变）。
- 不 push；不扩大设计基线之外交互；不写真实 `%APPDATA%`。
- 依赖端口未就绪的残项**不得**用模拟数据/假实现充数；必须按 DEFERRED/BLOCKED 登记。

## 依赖与分工

| 依赖 | 状态 | 本批用法 |
|---|---|---|
| FEA-06 | done（`b26840acd`） | residual 来源、设计基线 `doc/design/fluent-v1/` |
| FEA-07 | closed_with_limitations（`aedc7251c`） | 稳定窗口、切换/退出保护、memento 边界（只读使用，不改） |
| FEA-09/10/11/12/13 | 未创建/未 done | 只作为 DEFERRED/BLOCKED 的承接方；本批不依赖其运行 |

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际 | 证据 |
|---|---|---|---|---|
| AC1/AC3 功能 UI | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests`（Avalonia.Headless，临时 `--theme-home`/`--data-root`） | .NET 9 | NOT_RUN | 待补 |
| AC2 组件/动效 | 同上 + DesignSystem.Tests（样式/令牌/焦点） | .NET 9 | NOT_RUN | 待补 |
| AC4 技术债 | 同上；R-8a 拆分后全量 1138/0/57；R-8b 默认运行 `git status` 干净 | .NET 9 | NOT_RUN | 待补 |
| AC5 回归/治理 | 全量 sln + `TokenGen/ThemeGen -- --check` + `check.ps1` + `verify_pins.ps1` + FEA-07 非回归子集 | 全量 | NOT_RUN | 待补 |

## Review Appointment

- **scope-r2**：fresh Codex CLI 只读，被审文档 head = 范围 v2 提交；只写 `doc/reviews/FEA-06-RESIDUAL-1-scope-r2.md`。P0/P1=0 后由 DSH 冻结范围 v2 并释放实施。
- **impl-r1**：实现完成后 fresh Codex CLI 只读全量复核（只写 `doc/reviews/FEA-06-RESIDUAL-1-impl-r1.md`）；DSH 处置后集成验证 → done/closed_with_limitations。
- 作者（Codex 实现会话）不得自审；DSH 不审自己实现（本卡实现归 Codex）。

## Resource Manifest

- 关闭时填写（当前 pending）：worktree=无 linked worktree（main 内联）；verification artifacts=`verification/FEA-06-RESIDUAL-1/**` PRESERVE_REFERENCED；task-env/user data=未创建/未访问。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Closeout Record

- 待关闭时填写。
