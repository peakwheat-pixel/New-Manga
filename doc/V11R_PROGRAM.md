# V11R 程序计划：V1.1 整改 + 全新 Avalonia UI/UX + Theme Studio 重建

状态：`ACTIVE`（2026-10-30 起，DSH 为 Lead / Architect / Integrator）
权威性：本文件是本程序内**唯一任务 DAG**；运行状态以 [STATUS](STATUS.md) 为准；本程序取代 [REBASELINE_PLAN](REBASELINE_PLAN.md) 中"READY 节点：无"的旧结论。
上游依据：[AD-002 目标架构](AD-002_TARGET_DESKTOP_ARCHITECTURE.md)、[V1.1 审计](V11_AUDIT_V1_1.md)（见 §1.3）、**冻结设计基线** `doc/design/redesign-v1/40-fusion/{FUSION_SPEC,DESIGN_SYSTEM}.md` + `tokens.json`。

---

## 1. 基线与事实

### 1.1 Git 基线

| 项 | 值 |
|---|---|
| 程序起点 | `main@eaacd872d`（2026-10-30 工作区干净，`git status` 空） |
| 设计基线合并 | `c78db96ed` 合并 `agent/dsh/UIUX-REDESIGN-1`（A+C 融合冻结规范 v1，2026-10-25 用户裁决 A+C） |
| 六维体系合并 | `c73239999` 采用 `50-system/00_SIX_DIMENSIONS.md` + `10_SHELF_REFERENCE.md` |
| 构建基线 | `dotnet build apps/desktop-avalonia/NewManga.sln` = 0 warning / 0 error（net9.0, Avalonia 11.3.22, 2026-10-30 实测） |
| 生产前端 | `apps/desktop-avalonia`（C#/.NET + Avalonia 11.3.22）。`apps/desktop`（Tauri/React）为历史壳，`LEGACY_FROZEN.md` 冻结，不得回到生产路径 |
| 不可推送 | 本程序**不 push** 任何远端分支（用户未授权 main 推送/发布） |

### 1.2 现有前端事实（整改依据）

- 视图为**代码构建的巨型单文件**：`Views/Pages.cs` 72 KB、`Views/ReaderWorkbenchPages.cs` 102 KB、`Views/ProfileSections.cs` 32 KB、`Views/ImportExportPanels.cs` 27 KB（审计风险 M-01）。
- 旧主题全部集中在 `src/NewManga.Theme/ThemePack.cs`（34 KB，1 文件）：`ThemePack` 记录 + 6 个旧预设（Saber/Midnight/Sakura/Emerald/Mono/macOS）+ `LayoutKind/NavPlacement/ShelfStyle/SettingsStyle` **把颜色、导航、书架布局、密度耦合在一个包里** —— 与本程序 C2「必须解耦」要求直接冲突，判定为整体废弃对象。
- `IHostController` 36 个自有方法，**缺** `CreateChapterAsync` 与 6 个 Run 控制方法（审计 §6）；Run 命令在 Core/注册层存在（C056–C061）但无 UI 面。

### 1.3 审计附件

《New Manga 前后端功能与接口现状审计 V1.1 修订完整版》zip 已解压至
`G:\CODEX\New Manga.workspace\tasks\AUDIT-V11-INTAKE-1\`（md 88 KB / html / json / `功能追溯矩阵.csv` 108 项 / `命令清册_C001-C066.csv`）。
审计基线 `clean-snapshot-20261029@22de860`。**审计为静态源码调查，所有 AC/E2E 为 NOT_RUN**；本程序的验收证据必须以真实执行产生。
解压副本不入 Git（素材不传播），引用时以本 § 记录的工作区路径为准。

### 1.4 冻结设计基线（工作流 B/D 的上游）

| 资产 | 路径 | 状态 |
|---|---|---|
| 融合设计规范 | `doc/design/redesign-v1/40-fusion/FUSION_SPEC.md` | `FROZEN`（A+C，三空间+双模式，共享 selection） |
| 设计系统 | `doc/design/redesign-v1/40-fusion/DESIGN_SYSTEM.md` | `FROZEN`（令牌规则、7 态、40 组件、反向清单） |
| 令牌源 | `doc/design/redesign-v1/40-fusion/tokens.json` | `FROZEN`（DTCG；dark 35 / light 35 / 全局 71 变量） |
| 方向原型 | `doc/design/redesign-v1/20-directions/{A-darkroom,B-parlor,C-atelier}/` | 视觉参考（HTML/CSS，非生产代码） |
| 六维体系 | `doc/design/redesign-v1/50-system/00_SIX_DIMENSIONS.md` | 受理 |
| 旧实现记录 | `doc/design/redesign-v1/40-fusion/IMPLEMENTATION_PLAN.md` §5 | React/Tauri 原型已实现 F1/F2，**Avalonia 侧为 0** |

**裁定 R-01**：本程序**不重新发明设计方向**。工作流 B 的实现基线 = FUSION_SPEC + DESIGN_SYSTEM + tokens.json；工作流 C（Theme Studio）在此之上扩展，不另建第二套设计系统。若实施中发现规范缺口，先改冻结文件并记录理由（`40-fusion/DECISION_LOG.md` 追加），禁止各页面独立发挥。
**裁定 R-02**：设计规范中的 CSS 令牌命名 `--nm-*` 在 Avalonia 侧统一映射为资源键 `Nm.*`（详见 `doc/plan/V11R_AVALONIA_CONTRACT.md`）。

---

## 2. 目标与范围

| 工作流 | 目标 | 完成判据 |
|---|---|---|
| **A · V1.1 整改** | 以真实源码逐项关闭审计 P0/P1；四维（实现/接入/运行/验证）分别留证 | P0 项有真实 IPC + UI 链 + 执行证据；66 命令契约包签发 |
| **B · 全新 UI/UX** | 在 Avalonia 落地冻结的 A+C 融合设计：三空间 + Studio 双模式 + 阅读浮层 + 命令面板 | 新壳替换旧壳为默认入口，六工作面可用，接真实 Core |
| **C · Theme Studio** | 从零重建主题引擎（10 子系统）+ 独立 Theme Studio 页面（7 分区）+ 旧主题彻底退役 | 新引擎为唯一运行路径；旧 `ThemePack` 删除；旧配置 ID 安全迁移 |
| **D · Design System** | 一套设计系统同时供 B、C 使用 | `NewManga.DesignSystem` 为唯一令牌/组件来源；B/C 无第二套定义 |

---

## 3. 任务 DAG

状态枚举：`blocked / ready / in_progress / in_review / done / closed_with_limitations / failed`。
验证等级按用户 §9：L1 任务级、L2 功能级、L3 里程碑、L4 发布验收；高风险任务额外强制独立审查。

### 3.1 波次 1（立即并行）

| ID | 目标 | 依赖 | Owner | Reviewer | 验证 | 写域（workspace-relative） |
|---|---|---|---|---|---|---|
| `V11R-BASELINE-1` | 基线核查、审计受理、设计合并、DAG 建立 | — | DSH | — | L1 | `doc/**` | **done** |
| `V11R-D-1` | **Design System (Avalonia)**：tokens.json→Avalonia 资源管线、字体/间距/圆角/状态七态、基础 10 + 结构 12 + 数据 10 + 画布 8 组件、图标库、a11y | — | `design-platform` | 独立 Reviewer（Codex） | L3 | `apps/desktop-avalonia/src/NewManga.DesignSystem/**`、`App/Styles/**`、`App.axaml`、`NewManga.sln`、`App.csproj` |
| `V11R-C-RESEARCH-1` | SukiUI / FluentAvalonia / Semi.Avalonia / PleasantUI / Avalonia 主题架构与许可证对比研究 | — | Codex | DSH | L1 | `doc/design/theming/**` |
| `V11R-A-1` | **CreateChapter 服务层**：`CreateChapterAsync` + 新建章节对话框契约 + 空库→建书→建章→导入链路测试 | — | `core-bridge` | 独立 Reviewer | L2 | `App/Services/IHostController.cs`、`HostController.cs`、`NullHostController.cs`、`CoreClient/**`、`tests/NewManga.App.Tests/**` |
| `V11R-A-2` | **Run 控制服务层**：`IRunController`（Start/Control/Resume/Snapshot/TaskProjection/RetryFailed）+ 幂等键 + 状态投影轮询 | — | `core-bridge` | 独立 Reviewer | L2 | 同上 + `App/Services/Run*/**` |
| `V11R-A-3` | **66 命令契约包**：DTO/错误码/样例/minor 兼容表 + parity 测试补强 | — | `core-bridge` | 独立 Reviewer | L2 | `CoreClient/**`、`doc/contracts/**`、tests |
| `V11R-A-5` | **P0 生产写入策略**（Lead 新发现）：默认 `ReadOnlyUntilParity` 使发布版 GUI 完全不可写；改为默认 ReadWrite + 三重护栏（旧壳运行 / `--parity=false` / 启动未就绪）+ first-run 备份 | — | `core-bridge` | 独立 Reviewer | L2 + 高风险（数据策略） | `NewManga.Host/**`、`AppOptions.cs`、`doc/plan/V11R_WRITE_POLICY.md` |

### 3.2 波次 2（DS 骨架合入后释放）

| ID | 目标 | 依赖 | Owner | Reviewer | 验证 |
|---|---|---|---|---|---|
| `V11R-B-1` | 新外壳：TopBand + 三空间路由 + 上下文保留 + 命令面板 + 键位注册表 + 焦点管理；Library 空间（作品/章节/页/导入 dock/回收站/阅读浮层） | `V11R-D-1`(M0 骨架) | `ui-shell` | 独立 | L3 |
| `V11R-C-1` | **Theme Engine**：Semantic Tokens / Registry / Package Schema / Resolver / State Manager / Persistence / Preview / Import-Export / Validation / Fallback（10 子系统） | `V11R-D-1` | `design-platform` | 独立 | L2 |
| `V11R-F0-1` | **Region 写面契约**（高风险）：Core 新增 create/delete/geometry/merge/split/reorder/save_manual_translation/confirm_final/set_lock/pin_revision + Host/IPC + typed error + 乐观锁 | — | Codex（架构/协议） | 独立（DSH 指派第三方） | L2+高风险 |
| `V11R-F0-2` | **Region 文本只读投影**（GAP-2）：单次命令返回一页 region 四轨文本/锁/review_state/is_pinned/几何，Studio Page 初次载入必需 | `V11R-F0-1` | `core-writer` | 独立 | L2 |
| `V11R-A-4` | 新快照 CI 与可重建测试（V-01）：GitHub Actions 同 SHA、无本机绝对路径 | — | `core-bridge` | 独立 | L2 |

### 3.3 波次 3（B-1 与 A-2 可用后）

| ID | 目标 | 依赖 | Owner | Reviewer | 验证 |
|---|---|---|---|---|---|
| `V11R-B-2` | Console 空间（设置中心）：任务队列、Provider/凭据、网络、模型与设备、缓存与版本、备份、插件、诊断 | `V11R-B-1` | `ui-shell` | 独立 | L3 |
| `V11R-B-3` | Studio · Page 模式：胶片条、画布三态、Region 覆盖与几何编辑、HUD 环、检查器五页签、四轨条、锁定、Revision | `V11R-D-1`、`V11R-A-2`、`V11R-F0-1` | `ui-studio` | 独立 | L3 |
| `V11R-B-4` | Studio · Batch 模式：阶段轨道、状态矩阵、概览胶囊、批量动作、Run 带、任务面板 | `V11R-A-2`、`V11R-D-1` | `ui-studio` | 独立 | L3 |
| `V11R-C-2` | **Theme Studio 页面**：主题库/预览/我的主题/编辑/外观/导入导出/实时预览 7 分区 | `V11R-C-1`、`V11R-B-1` | `ui-shell`（或专派 `theme-studio`） | 独立 | L3 |

### 3.4 波次 4（收口）

| ID | 目标 | 依赖 | Owner | Reviewer | 验证 |
|---|---|---|---|---|---|
| `V11R-B-5` | 导出预检/术语与约束工作面 | `V11R-A-3`、`V11R-B-3` | `ui-studio` | 独立 | L2 |
| `V11R-C-3` | **旧主题退役**（高风险）：依赖图、替换清单、配置 ID 安全迁移、删除 `ThemePack`/旧 UI 入口/旧测试 | `V11R-C-1`、`V11R-C-2` | `design-platform` | 独立（强制） | L2+高风险 |
| `V11R-INT-1` | 集成：新壳切成默认入口、全部工作面接真实 Core、旧测试迁移 | 全部 | DSH | — | L3 |
| `V11R-VERIFY-1` | L3 里程碑独立审查（设计系统冻结、四大工作面、Theme Studio） | `V11R-INT-1` | Codex / ZCode | — | L3（只读） |
| `V11R-L4-1` | L4 发布验收：全量回归、E2E 十旅程、Windows 实机、安装/升级/卸载、性能/无障碍/安全 | `V11R-VERIFY-1` | DSH + 独立 | 强制独立 | L4 |
| `V11R-REPORT-1` | 《New Manga 全功能整改 + 全新 UI/UX + Theme Studio 重建验收报告》 | `V11R-L4-1` | DSH | — | — |

---

## 4. 里程碑与 Gate

| 里程碑 | 内容 | Gate |
|---|---|---|
| **M1 基座** | DS M0 骨架 + A-1/A-2 服务层 + C1 研究 | DS 令牌可切换双主题且无裸值；`CreateChapterAsync`/`IRunController` 有单测；构建 0 warning |
| **M2 新壳可用** | 新外壳 + Library + Console 可运行 | 三空间可切且保上下文；建书/建章/导入真实链路 PASS；L3 独立审查 |
| **M3 全工作面** | Studio Page + Batch + Theme Studio | 六工作面可用；主题实时切换不改变画布像素；L3 独立审查 |
| **M4 退役与集成** | 旧主题删除、旧壳切换、配置迁移 | 旧主题零引用；旧配置可启动；L3 审查 |
| **L4 发布验收** | 全量回归 + 实机 | 报告 PASS/FAIL/BLOCKED/NOT_RUN 分明；无伪造 PASS |

---

## 5. Agent 角色（动态，Owner ≠ Reviewer）

| Role | 承担者 | 说明 |
|---|---|---|
| Lead / Architect / Integrator | DSH | DAG、契约、集成、最终验收；**不审自己实现的变更** |
| Owner: 设计平台 | DSH teammate `design-platform` | DS + Theme Engine + 退役 |
| Owner: 新 UI | DSH teammate `ui-shell` / `ui-studio` | 外壳/Library/Console；Studio Page/Batch |
| Owner: 服务层与契约 | DSH teammate `core-bridge` | IHostController/Run/契约包/CI |
| Owner: 高风险协议 | Codex | Region 写面、独立审查、参考研究 |
| Reviewer | Codex / 独立 DSH teammate（不参与实现） | 关键里程碑与高风险变更 |
| Fallback | ZCode / Antigravity | Owner 不可用时按 capability 重新路由 |

故障规则：Agent 不可用/额度不足 → 重新路由或拆分任务，不让 DAG 停滞；不伪造启动或 PASS。

---

## 6. 旧主题退役依赖图（C4 前置，随实施细化）

旧主题资产清单（`V11R-C-3` 必须逐项核实后处置）：

| 资产 | 引用方 | 退役动作 |
|---|---|---|
| `src/NewManga.Theme/ThemePack.cs`（ThemePack/ThemePacks/ThemePackService/LayoutKind/NavPlacement/ShelfStyle/SettingsStyle/MotionProfile/ThemePackMetrics/LayoutProfiles） | `App.axaml.cs`(3)、`AppOptions.cs`(1)、`MainViewModels.cs`、`CredentialSection.cs`、`ImportExportPanels.cs`、`MainWindow.axaml.cs`、`Pages.cs`、`ProfileSections.cs`、`ProviderBindingsSection.cs`、`ReaderWorkbenchPages.cs` | 新引擎等价后删除；`NewManga.Theme` 项目退役或改名替换 |
| 旧测试：`ThemeMacosTests.cs`(88 处)、`ThemeLayoutsTests.cs`(61)、`ThemeMacosAuditTests.cs`(9)、`S3ShellTests.cs`(20)、`S4ReaderWorkbenchTests.cs`(1) | `tests/NewManga.App.Tests` | 以新 DS/Theme 测试替代后删除 |
| 旧预设 ID（saber/midnight/sakura/emerald/mono/macos…）配置值 | `AppOptions`/设置持久化 | 安全迁移映射到新默认主题，不得启动失败 |
| 布局枚举（LayoutKind/NavPlacement/ShelfStyle/SettingsStyle） | 旧壳 + 设置 | 迁移到新 `LayoutProfile`（与颜色包解耦） |

硬约束：**新系统具备等效能力并通过迁移/回滚测试后**，才允许逐项删除；删除前不得留下生产页面引用的孤儿资源。

---

## 7. 证据与恢复

- 每个任务证据：`verification/<TASK-ID>/`（`allowed_paths` 必须含该目录）。
- 恢复指针：本文件 §1.1 Git 基线 + `doc/STATUS.md` 当前 Task + rolling checkpoint（`verification/checkpoints/`）。
- 不写入用户数据；不改 DB schema（除非任务显式授权并独立审查）；不 push 远端。
- 高频并行：每个 Owner 在自己 linked worktree 工作，DSH 负责合并；共享契约以本文件与 `doc/plan/V11R_AVALONIA_CONTRACT.md` 冻结。

## 8. 裁定记录

| 编号 | 裁定 | 理由 |
|---|---|---|
| **R-01** | 工作流 B 的实现基线 = 冻结的 FUSION_SPEC + DESIGN_SYSTEM + tokens.json（2026-10-25 用户已裁决 A+C），不重新发明设计方向 | 已有冻结规范与用户裁决，重做等于浪费且违反"B/C 共用一套设计系统" |
| **R-02** | CSS 令牌命名 `--nm-*` → Avalonia 资源键 `Nm.*`（PascalCase 逐段） | Avalonia 无 CSS 变量，需资源键承载动态切换 |
| **R-03** | V1 **不引入** SukiUI/FluentAvalonia/Semi.Avalonia/PleasantUI 依赖，新 Theme Engine 建在 Avalonia 原生原语上（ThemeVariant + ResourceDictionary + ControlTheme + DynamicResource），第三方仅作参考 | 视觉语言与冻结设计冲突、单一令牌真值、发布体积与可恢复性；详见 `doc/design/theming/RESEARCH_V1.md` |
| **R-04** | 命令注册表随 `V11R-F0-1` 由 **66 → 76**；`V11R-A-3` 契约以 C001–C066 为基线并单列 C067–C076（PENDING，指向 `V11R_REGION_WRITE_CONTRACT.md`）；所有 parity 测试改为**从注册表派生**，禁止硬编码数量 | 避免 A-3 与 F0-1 并行写域互相打爆；数量不是契约真值 |
| **R-05** | 旧主题退役执行顺序见 `doc/plan/V11R_THEME_RETIREMENT_PLAN.md`：新系统等效 + 迁移/回滚测试通过后才删除；任何旧 ID 一律安全映射默认主题 | 用户 C4 硬约束 + 不得导致启动失败 |
| **R-06** | Theme Studio 为独立覆盖式表面（非第五空间），规范见 `doc/design/theming/THEME_STUDIO_SPEC.md` | 用户 C3 要求"独立 Theme Studio 页面"，同时保持三空间 IA 不被破坏 |
| **R-07** | Codex CLI 在本机需 `--dangerously-bypass-approvals-and-sandbox` 才能启动子进程（默认沙箱报 `helper_unknown_error`）；因此 Codex 仅用于**独立审查/只读研究**，实现任务由 DSH 专责 Owner 承担 | 实测沙箱故障；不因单 Agent 不可用而停滞（用户 §1.7） |
| **R-08** | `IRunController` 幂等键改为显式参数：`ControlRunAsync(runId, action, string? idempotencyKey = null, ct)`、`RetryFailedTargetsAsync(runId, string idempotencyKey, ct)`；导出方法不进 `IRunController` | 避免重载分叉与双重真值 |
| **R-09** | 修订冻结 `tokens.json` 的对比度不达标值（dark queued/skipped/failed、light skipped/accent 族），以 DESIGN_SYSTEM §2.3 ≥4.5:1 为准；修订记入 `40-fusion/DECISION_LOG.md` | 规范条款优先于数据值；无障碍不可协商 |
| **R-10** | Motion 时长以 `tokens.json` 的 140ms 为准，契约 §2.2 的 150ms 为示例笔误 | 单一来源 |
| **R-11** | 视觉/交互差异一律以冻结 FUSION_SPEC + DESIGN_SYSTEM 为准；发现缺口先改冻结文件并记 DECISION_LOG，禁止各页自行发挥 | 防止 B/C 分叉 |
| **R-12** | DS 与 ThemeEngine 职责边界：DS 拥有令牌/样式/控件/资源应用机制；ThemeEngine 拥有主题包语义与数据；依赖方向 `App → ThemeEngine → DesignSystem`；DS 暴露 `ApplyThemeLayer/ApplyPalette/RevertPalette` 供引擎调用 | 防止两套主题真值 |
| **R-13** | **生产写入策略**：`ReadOnlyUntilParity` 使发布版完全不可写（P0，审计未覆盖）。改为默认 ReadWrite，保留三重护栏（旧 Tauri 壳运行 / `--parity=false` / Host 未就绪）与首次写前 first-run backup；`--parity=false` 为回滚手段。此为 DSH 依授权做出的产品策略修复，须在最终报告显著标注 | 用户核心工作流被真实阻断，且无任何文档告知用户 |
| **R-14** | 冻结基线键名/例外登记：字号键统一 `Nm.FontSize.Xxl`（非 `2Xl`）；行高保留 `Tight/Normal/Loose` 并提供语义别名 `Body/Label/Meta/Data`；高对比/密度令牌为 DS 生成器按设计规则派生的**冻结扩展**；`Transparent` 与图标按钮 `Margin="-2"` 为唯一裸值例外；其余裸值违规 | 独立审查发现契约与实现键名不一致、派生令牌被误判为"第二真值"；集中登记避免反复争议 |
| **R-15** | 主题层白名单 = 59 键（颜色35 + 字体族3 + 字号6 + 行高乘数3/绝对6 + 圆角3 + 动效3）；`material/elevation` 无冻结键只校验不发布；`Nm.Motion.Duration.Slow=220ms` 登记为冻结扩展 | 让 Theme Studio 的字号缩放/行高预设真实生效，且不发明令牌 |
| **R-16** | **单一选择模型**：`ShellState.Selection` 为唯一权威；`StudioSelection` 降为投影 + 变更路由；显式 `ScopeKind {Chapter, SelectedPages, Page, Region}`，显式多选优先于 Region | 两套 selection 会让 FUSION 硬规则 1（跨模式作用域一致）必然失效 |
| **R-17** | `IWorkspaceView` 增加 `bool TryHandleKey(KeyEventArgs, ShellState)`：工位专属键（Tab/Esc/J/K/[ ]/+/-/0）先交工作面，shell 仅在 false 时处理；其余键由 shell 统一注册表处理 | 否则 shell 的全局 Tab/Esc 会吞掉 Studio 的 HUD/逐级退出 |
| **R-18** | 断点统一 `>=1600` 完整 / `1280–1599` 紧凑 / `<1280` 覆盖式；令牌 `Nm.Size.Breakpoint.Full=1600/.Compact=1280/.Narrow=1024`，禁止各 Owner 自造 1400/1200 | 审查发现三套断点不一致 |
| **R-19** | 证据纪律：每个任务只写 `verification/<TASK-ID>/`；**禁止复制其它任务证据/二进制 DB 入库**；测试证据写入默认落仓库而非 `%TEMP%`；交付后证据须随 fix commit 重生成；被审 pin 冻结 | 审查发现 B-1 证据 42% 为外任务复制品 |
| **R-20** | `App` 项目引用 `NewManga.ThemeEngine`（依赖 `App → ThemeEngine → DesignSystem`）；Theme Studio 可直接调用引擎，禁止条件编译桩冒充生产适配器 | Theme Studio 需要真实引擎能力 |## 9. 变更记录
| **R-21** | `Nm.Color.Scrim` 为**主题不变量全局派生色**（rgba(0,0,0,0.55)，Modal 遮罩），不属于 appearance palette、不属于主题包 59 键白名单；引擎的必需颜色集必须用 DS 公开 `PaletteColorKeys`（35）而非 `NmKeys.Color.*` 全量 | DS 返修新增该键导致引擎 46 测试失败；Scrim 无语义个性 |
| **R-22** | **幂等键语义统一**（改写 R-08 的 UI 侧解释）：UI 可以为"一次新的用户意图"生成幂等键，但必须 ①意图创建时生成并存住、②同一意图的重试**复用同一键**、③提交进行中按钮禁用（防双击）；禁止每次点击新生成 GUID。Console 手填键与 Batch 自动键都需满足②③；Batch 必须在 UI 显示/记录键来源 | 审查发现 Batch 每次点击 Guid.NewGuid() 使幂等保护失效，且与 Console 纪律相反 |
| **R-23** | **状态词表只表达状态**：`done/blocked/not_started` 等七态不得用于"是否接入/是否已保存/分区可用性"等非状态语义；这类语义用中性文字徽标或 `StatusBadge` 之外的组件 | DESIGN_SYSTEM §2.1/§2.2 明确禁止状态参与装饰 |
| **R-24** | **Run 投影单一来源**：收敛为一个可注入间隔的 `IRunProjectionPoller` + `IRunDataSource`，Console / Batch 共用同一投影与同一控制面（Start/Stop/Pause/Retry/Resume 语义一致，Stop 必须确认）；禁止两个空间各自轮询同一 `IRunController` | 审查发现 Console 1s/Batch 750ms 双源、Stop 纪律分裂 |
| **R-25** | 证据禁止"字面量-backed 字段"：JSON/截图中的每个字段必须从被测对象读取（如 `batch.GateImpactText`），禁止 `writer.WriteString("field","字面量")`；恒真断言（`x is null` 与取值、`Contains("A","A")`）一律删除 | 连续两轮审查发现证据作假模式 |
| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-10-30 | 建立程序；合并冻结 A+C 设计基线；建立 DAG；裁定 R-01/R-02 | DSH |
| 2026-10-30 | 完成 C1 研究（R-03）、C3 规格（R-06）、C4 退役计划（R-05）；裁定 R-04/R-07；释放 5 条并行实现线 | DSH |

## 10. Follow-up 清单（不阻塞 L4，但须在 V1.x 关闭）

| 编号 | 内容 | 来源 |
|---|---|---|
| FOLLOW-UP-C1-1 | 系统强调色跟随（`FollowSystemAccent`）V1 仅作用域生效、不持久化；V1.x 扩 `IThemeService` 后写入设置 | C-2 GAP-3（Lead 裁定） |
| FOLLOW-UP-C1-2 | 主题编辑器的"未安装草稿"为了实时预览走作用域 PaletteScope；V1.x 评估持久草稿模型 | C-2 DEV-2 |
| FOLLOW-UP-DS-1 | 状态文字在 `bg.overlay/sunken` 等极端表面的对比度（6 行/7 对）；V1 约束=只落 panel/raised+statusMuted | D-1 r2/r3 |
| FOLLOW-UP-CORE-1 | 过期/待确认计数无投影口径；需 Core 投影扩展 | B-4 |
| FOLLOW-UP-CORE-2 | Host 缩略图命令缺失（页缩略图网格） | B-1 |
| FOLLOW-UP-CORE-3 | 术语/不译表无 Core 读写命令（UI 诚实 NOT_WIRED） | A-3 / B-5 |
| FOLLOW-UP-TEST-1 | 跨项目并行测试偶发 1 例失败（runsettings 串行化后仍偶发）；需定位共享状态 | 多次观测 |
| FOLLOW-UP-REPO-1 | `ReaderWorkbenchPages.cs` 本机路径 fallback（verify-clean-clone ALLOW_PENDING） | A-4 |
