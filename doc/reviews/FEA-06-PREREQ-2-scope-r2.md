---
task_id: FEA-06-PREREQ-2
reviewer: ZCode（主会话）
reviewer_kind: agent
author: dsh-lead
base_commit: cad5ebde3（卡声明）
reviewed_head: 4659e59d3
decision: changes_requested
counts: { P0: 0, P1: 4, P2: 7 }
---

# FEA-06-PREREQ-2 范围冻结复核 r2（独立上下文；本席位未参与本卡起草/实现）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06-PREREQ-2.md`（`proposed`；`approval: pending_review`） |
| reviewed_head | `4659e59d3`（`docs(goal): 记录复核通道故障（Q-34 待裁决）与 Round 19 进展…`）；`git status --short` 干净 |
| 上游 | `doc/tasks/FEA-06-PREREQ-1.md`（**done**，impl-r4 approved + Q-33 residual transfer）；Q-32（goal §22 `:164-172`）；Q-33（PREREQ-1 卡 `:7,:126-134`）；Q-34（goal §23 `:173`，本轮复核即通道恢复后的补审） |
| reviewer | **ZCode（主会话）**，DSH 派发（2026-10-31 上下文独立裁决：产出变更的会话不得自审）；未参与 FEA-06-PREREQ-2 的起草、r1 处置修订与任何实现 |
| 日期 | 2026-11-03 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 4 / P2 = 7** |

> **一句话结论**：r1 的三个 P0 全部实质闭合（写域扩充到位、Q-33 拆环成立、PREREQ-1 已 done），selector/CLI 优先级/禁止范围等主线修正正确；但**仍不可放行实现**：①P5 兼容写的生产注入点在 `NewManga.App/ViewModels/V2/ThemeStudio/`（`allowed_paths` 之外）；②Q-33 残余清单第 ③ 条（`nm.fluent.visual/1` manifest + `ThemeValidator` 显式测试）在本卡无任何落点，与「非无主豁免」声明自相矛盾；③P6 公开面变化与 C-02 V-07 冻结判据的关系未论证、登记载体不在写域；④测试要求表仍无 AC5/AC6 行（r1 P1-5 原样未动）。修完这四条 P1 后可直接 rev-r3，无需再动 P5/P6 主方向。

---

## 0. 方法与只读声明

- 只读核查被审 head；未修改卡/代码/设计/契约；未 commit/push；本报告为本轮唯一新增文件（落盘于本卡写域 `doc/reviews/FEA-06-PREREQ-2-*.md`）。
- 本轮实测：`check.ps1` → **PASS（3 warnings：10 非终态、STATUS 3028B/29 行 80%、PLAN 3946B/62 行 80%）**——r1 的第 4 警告（PREREQ-1 `evidence_dir` 3 个未登记过程文件）已消失（PREREQ-1 Resource Manifest `:117-120` 已登记 SOURCE_PIN）；`verify_pins.ps1` → **PASS（all 15）**，其中 C-02 pin 仍匹配冻结字节 `bb365ca8…`，证明 P6 的公开面「登记」尚未发生、契约字节无人触碰。
- 阅读：本卡全文；PREREQ-1 卡（done/Q-33 段/残余清单）；r1 报告；C-02 修订单 V-07（`:86-91`）+ §4（`:100-104`）+ §5 口径表（`:125`）+ 冻结记录（UNFREEZE 纪律）；C-03 草案 §2.1/§2.2/§2.3/§3；goal §21–§23；fluent-v1 README/04/02；`App.axaml.cs`/`Program.cs`/`AppOptions.cs`/`AppearanceCoordinator.cs`/`AppearanceStore.cs`/`Appearance.csproj`/`ThemeModels.cs`/`ThemeSettingsStore.cs`/`TokenMap.cs`/`NmKeys.g.cs`/`DesignSystemThemeManager.cs`/`R14ContractTests.cs`/`ThemeContracts.cs`/`ThemeService.cs`/`ThemeEngineThemeStudioService.cs`；STATUS/PLAN/LEDGER/goal 指针。

---

## 1. r1 逐项 disposition（19 项）

| r1 ID | 判定 | 理由（含行号实测） |
|---|---|---|
| **P0-1**（P5 写域/测试落点） | **CLOSED** | `allowed_paths` 已补 `NewManga.App/Services/**`（卡 `:23`）、三测试工程（`:36-39`）；P5 已写清迁移 + `SaveAsync→AppearanceStore.WriteAsync` + `[Obsolete]` + sink adapter（`:61`）。**遗留新事实**：sink 的生产注入点在 ViewModels（→ R2-P1-1，按新 finding 计） |
| **P0-2**（P6 写域/测试落点） | **CLOSED** | `ThemeEngine/Models|Serialization|Themes/**`（卡 `:25-27`）+ `DesignSystem/**`（`:28`）+ `DesignSystem.Tests/**`（`:38`）已入写域；P6 路径已选并落到模型/键/计数（`:62`） |
| **P0-3**（依赖环） | **CLOSED** | Q-33 拆环：PREREQ-1 `status: done`（`approval: …residual_transfer_Q-33_2026-11-03`，卡 `:6-7`）→ 本卡 `depends_on` 满足；PLAN `:21`（done）/`:22`（proposed 待 r2）/`:37`（DAG）一致；STATUS `:7` 当前 Task=PREREQ-2。**自洽性破口两条**：residual ③ 无落点（→ R2-P1-2）、checkpoint 无 Q-33 记录段且 §22 尾陈述过时（→ R2-P2-4） |
| **P1-1**（AC1 id 混用） | **CLOSED** | AC1（`:66`）按 frontendId（`builtin.current-v2`/`builtin.fluent`）决策，`builtin.fluent-dark` 显式标注 visualThemeId 不参与 selector；与 `AppearanceSettings.cs:15-19` 双 id 分离、C-02 V-07、C-03 §3 一致。残留：P4（`:60`）测试场景仍列 `fluent-dark`（→ R2-P2-7，建议标注为负例） |
| **P1-2**（CLI 优先级） | **CLOSED** | W-2b（`:82`）：`--frontend`（显式）> `AppearanceSettings.FrontendId` > 缺省 `builtin.current-v2`；`AppOptions.cs:36,:91,:228-236` 已有 `--frontend`（非空校验、不校验值域），非法值由 AC1「其余（含缺失/非法）→ V2 + 记录」承接，链路自洽 |
| **P1-3**（P5 唯一写者/sink） | **PARTIAL** | 唯一写者类/项目/方法已定（迁移 coordinator 入 Appearance + `SaveAsync` 调 `WriteAsync`，`:61`；`AppearanceCoordinator.cs:14-18` D-1 remarks 一致；`Appearance.csproj` 已无 ThemeEngine 引用，反向引用不会形成）；**但 sink 的生产注入点未定且在写域外**（→ R2-P1-1） |
| **P1-4**（P6 实现路径） | **CLOSED** | 已选 `ThemeTokenSet` 扩展路径：`ThemeMaterial` 加 `Fluent`（现仅 `Solid/None`，`ThemeModels.cs:93-99`）+ `ThemeTokenSet` 增 Material(Base/Tint) + `ThemePackageJson` 序列化 + `NmKeys` 两常量不进 `Tokens.Global.axaml`（`:62`）；`TokenMap.cs:204-206` 已预留注释、`R14ContractTests.cs:84-93` 的 35/59/65 断言与卡内「计数同步」口径一致，`ThemeLayerRequiredKeys/AllowedKeys`（`DesignSystemThemeManager.cs:114-130`）在写域内可改 |
| **P1-5**（AC5/AC6 测试命令） | **OPEN** | 测试要求表（`:88-91`）**仍只有 AC1–AC3（App.Tests）与 AC4（全量 sln）两行**，AC5/AC6 无 `dotnet test` 目标/前提/证据落点——与 r1 所指 `:82-83` 内容逐字相同，r2 一字未改（→ R2-P1-4） |
| **P1-6**（公开面/契约分析） | **PARTIAL** | P6 承认 `ThemeMaterial` 枚举值公开面变化并「在变更记录中登记」（`:62`），方向对；但未论证 V-07 判据适用性、未指明登记载体，且 `ThemeTokenSet` 主构造器签名变化（`:240-246`）与 schema 演进未提及（→ R2-P1-3） |
| **P1-7**（禁止范围矛盾） | **CLOSED** | 禁止范围（`:75`）改为「不改 ThemeEngine 的既有主题包语义（`newmanga-default` 字节不变；**新增 `ThemeMaterial.Fluent` 值属本卡 W-9 范围**）」，P5/P6 例外已显式声明 |
| P2-1（非法值记录面） | **OPEN** | AC1 仍只写「→ V2 + 记录」，记录通道未指定（→ R2-P2-1） |
| P2-2（AC2 具体测试） | **PARTIAL** | AC2 仍无具名回归测试；但测试表已含 AC1–AC3 的 App.Tests 命令（Avalonia.Headless 在 `App.Tests` 可用），可接受遗留 |
| P2-3（AC3 对照设计 04） | **OPEN** | P3/AC3 仍只写「导航 + 四页占位 / 可启动」，未对照设计 04 §1 骨架构成（顶条 36/左导航 200/状态条 28）（→ R2-P2-2） |
| P2-4（Appearance→ThemeEngine 引用） | **CLOSED** | `NewManga.Appearance.csproj` 已无任何 ProjectReference（impl-r4 P2-12 处置，goal §23 记录）；迁移 coordinator 入 Appearance 后无环 |
| P2-5（PREREQ-1 过程文件） | **CLOSED** | PREREQ-1 Resource Manifest `:117-120` 登记 3 个 SOURCE_PIN；本轮 `check.ps1` 该警告消失 |
| P2-6（STATUS/PLAN 指针） | **CLOSED** | STATUS `:7` 当前 Task=PREREQ-2（r2 待）；PLAN `:21/:22/:37` 三处一致 |
| P2-7（卡内补 W-9 行） | **PARTIAL** | 附加裁决点表（`:77-84`）仍只有 W-1/W-2b/W-2/W-3，**无 W-9 行也无 W-10 行**（goal §23 提及「新增 W-10」但卡内无此编号）；W-9 仅以括号引用散见 P5/P6/AC5/AC6（→ R2-P2-3） |
| P2-8（P5 文字/顺序） | **CLOSED** | 「双写者收敛」笔误已修为「写者收敛」（`:61`）；P5 内部「先迁移…再加…」已给出先后。措辞层面仍有「双写」方向歧义（→ R2-P2-5） |
| P2-9（PREREQ-1 closeout 更新） | **CLOSED** | 事实变化：PREREQ-1 已由 DSH 按 Q-33 完成 closeout（`:122-134`），本卡无需其路径。`base_commit: cad5ebde3`（`:13`）早于 PREREQ-1 实现的问题仍在，建议 release 时刷新（→ R2-P2-6） |

---

## 2. 新增 findings

### P1（4 条，必须修后放行）

| ID | 严重度 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **R2-P1-1** | P1 | 卡 `:61`（P5）；`apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/ThemeStudio/ThemeEngineThemeStudioService.cs:82`、`StubThemeStudioService.cs:56`；卡 `:21-44`（allowed_paths） | **P5 兼容写的生产注入点不在写域**：sink adapter `IThemeSettingsSink` 必须注入 ThemeEngine 写路径才能让 `ThemeSettingsStore.SaveAsync` 的双写（旧 `theme-settings.json` + 新 `presentation-settings.json`）在生产生效；但 `ThemeSettingsStore` 的两个 src 生产创建点都在 `App/ViewModels/V2/ThemeStudio/`，`ViewModels/**` 不在 allowed_paths（App 写域仅 `App.axaml.cs`/`App.axaml`/`Program.cs`/`Shell/**`/`Services/**`/`Views/Fluent/**`）。卡未写注入机制——实现者要么越域、要么静态服务定位（绕开写域但在 Persistence 内引全局状态）、要么 sink 不接线（AC5 生产路径失效、Theme Studio 改设置后新旧文件漂移，正中 C-03 `:72` 所防的静默丢失） | 在卡内明确注入机制并同步写域：推荐把 `App/ViewModels/V2/ThemeStudio/**`（或至少 `ThemeEngineThemeStudioService.cs`/`StubThemeStudioService.cs` 两文件）加入 allowed_paths，并写明 sink 由组合根传入 `CreateProduction`/`ThemeSettingsStore` 构造器；或明确「sink 经 Persistence 内静态注册」之类的写域内方案及其理由 |
| **R2-P1-2** | P1 | `doc/tasks/FEA-06-PREREQ-1.md:134`（残余清单 ③）；本卡 `:53-71`（P1–P6/AC1–AC6 全文无对应项）；C-02 `:100-104`（§4 manifest 契约） | **Q-33 residual ③ 无落点**：PREREQ-1 残余清单明写「（PREREQ-2 负责）：①…②…③ `nm.fluent.visual/1` manifest + `ThemeValidator` 显式测试」；①已入 P5、②已入 P6，**③ 在本卡任务拆解、AC、测试表中均无承接**。这直接与 Q-33 自我声明「转移目标已修订（P5/P6 + AC5/AC6 + 写域），非无主豁免」矛盾——③ 恰成无主 residual，且它是 C-02 §4 的冻结契约元素（manifest 缺失或被手改 → 主题包加载失败；校验器三判据），悬空损害 PREREQ-1 以 done 关闭的合法性基础 | 由 DSH 二选一并落卡：①新增 P7/AC7（或并入 AC6）承接 ③：`nm.fluent.visual/1` manifest 落盘 + `ThemeValidator` 显式测试（写域 `ThemeEngine/Themes|Serialization/**` 已覆盖）；②正式修订 PREREQ-1 Q-33 段，将 ③ 改判到其他有主载体（并同步 PLAN `:21` 注记），消除「非无主豁免」声明与事实的矛盾 |
| **R2-P1-3** | P1 | 卡 `:62`（P6「在变更记录中登记」）；C-02 `:90`（V-07 审查判据）、`:125`（§5「不新增枚举值」）；冻结记录 §1「修订须走 UNFREEZE 载体」；`ThemeModels.cs:93-99,:240-246`；卡 `:21-44` | **P6 公开面合规路径未闭合**：V-07 审查判据「`ThemeKind` 枚举值与公开方法签名不得变化」+ §5 口径表「不新增枚举值」；P6 要①`ThemeMaterial` 枚举加 `Fluent` 值、②`ThemeTokenSet` 主构造器加参数（record 公开构造签名变化，现 6 参）、③`ThemePackageJson` schema 演进。卡只写「（`ThemeMaterial` 枚举值）在变更记录中登记」：a) 未论证 V-07 是否覆盖 `ThemeMaterial`（字面只点名 `ThemeKind`）与 record 构造器；b) 登记载体不明——若落 C-02 草案/冻结记录文件，违反冻结语义（条款修订须走 `CONTRACT-UNFREEZE-<DATE>.md` 载体），且 `doc/plan/**` 与 UNFREEZE 载体路径均不在本卡 allowed_paths；c) L-1 先例（冻结记录 §4「已知限制」）只适用于**不改公开面**的实现细节缺口，与本例不同类。`verify_pins` 15/15 证明 C-02 字节未动，即「登记」尚无处发生 | 由 DSH 出架构裁决口径写入卡内：明确 V-07 冻结面=仅 `ThemeKind` 枚举 + ThemeEngine 公开接口方法签名，`ThemeMaterial` 加值与 `ThemeTokenSet` 增可选字段（带默认值保源兼容）不属 V-07 判据范围，或认定触碰并走 UNFREEZE/修订单；同时指定登记载体（C-02 冻结记录 §4「已知限制」或 §6 变更表为唯一合法落点）并把该载体文件加入 allowed_paths |
| **R2-P1-4** | P1 | 卡 `:88-91`（测试要求表）；AC5/AC6 `:70-71` | **AC5/AC6 无测试命令/证据落点（r1 P1-5 原样未动）**：测试表仍只有 AC1–AC3（App.Tests）与 AC4（全量 sln）两行。AC4 全量虽会执行三个测试工程的全部用例，但「全量通过」不提供 AC5/AC6 的判别性验收（双写收敛/兼容写/R14 计数同步各自的断言与证据）；Closeout 时 AC5/AC6 的「实际/证据」列无既定落点，违反本仓测试表先例（PREREQ-1 卡 `:93-99` 五行俱全） | 测试表补两行：AC5 → `dotnet test apps/desktop-avalonia/tests/NewManga.Appearance.Tests` + `NewManga.ThemeEngine.Tests`（写者唯一性/兼容写/双写一致性断言）；AC6 → `dotnet test apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests`（R14 计数）+ `ThemeEngine.Tests`（schema/序列化）；证据路径 `verification/FEA-06-PREREQ-2/**` |

### P2（7 条，建议修/接受遗留）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| R2-P2-1 | 卡 `:66`（AC1） | 「非法值 → V2 + 记录」的记录面仍未定义（日志/诊断/Shell 状态） | 指定可测记录通道（如 Trace/诊断 warning 列表）与断言 |
| R2-P2-2 | 卡 `:59,:68`（P3/AC3）；设计 `04-layout-responsive.md:9-25` | Fluent Shell 骨架未对照设计 04 §1（顶部命令条 36 + 左导航 200 + 状态条 28，令牌引用） | AC3 补骨架最小构成（或显式声明占位期豁免并留 FEA-06 对照） |
| R2-P2-3 | 卡 `:77-84`（附加裁决点表） | 表内无 W-9 行（Q-32 承接依据）也无 W-10 行（goal §23 提及的 D-1 强制项），编号只在正文括号引用 | 补 W-9（Q-32）/W-10（D-1 迁移）两行 |
| R2-P2-4 | `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md:164-172`（§22）；PREREQ-1 卡 `:130-134` | checkpoint 无 Q-33 记录段；§22 Q-32 尾陈述「PREREQ-1 以 <<PARTIAL>> 保持 in_review，不 done」与现状（done）直接冲突——四处自洽检查中 checkpoint 一侧滞后（PREREQ-1 卡/PLAN/STATUS 三处一致） | checkpoint 补 Q-33 段（拆环裁决 + residual 清单）或在 §22 追加更正行；PREREQ-1 allowed_paths 本含该 checkpoint 文件，补记合规 |
| R2-P2-5 | 卡 `:61`（P5）；C-03 `:68` | P5「在一个 release 内**双写** `presentation-settings.json`」与 C-03 `:68` 兼容写判据「（写**旧文件** + 记 warning）」措辞不同：卡意指「写旧 + 经 sink 同步写新」（数据一致性必需，防 Theme Studio 保存后新旧文件漂移），但未注明这是对 C-03 字面的补强及理由，实现/复审两头都可能误读 | P5 加一句定义：「兼容写 = `SaveAsync` 继续写旧 `theme-settings.json` 并经 sink 同步写新 `presentation-settings.json`（超出 C-03:68 字面的理由：新文件为权威源，单写旧文件会造成回读漂移）」 |
| R2-P2-6 | 卡 `:13`（base_commit） | `base_commit: cad5ebde3` 早于 PREREQ-1 实现（r1 P2-9 已指出）；实现将从当前 main（≥ `4659e59d3`）进行，卡基线滞后会使 merge-base 检查意义弱化 | release 实现时把 base_commit 刷新为届时 main head |
| R2-P2-7 | 卡 `:60`（P4） | P4 测试场景仍列「fluent/fluent-dark/v2/未知」——`fluent-dark` 作为 selector 输入与 AC1 修正后的口径有歧义（善意解读=负例，预期 V2） | P4 改为「fluent / v2 / 未知 / **fluent-dark 误用为 frontendId（负例 → V2）**」 |

---

## 3. 指定核查项结论（指令逐条对应）

- **r1 P0-1/P0-2**：CLOSED（写域四组 + 三测试工程全部入卡 `:23-39`；P5/P6 落到方法/字段/键/计数）。落地性残余分别转 R2-P1-1（注入点）与 R2-P1-3（公开面）。
- **r1 P0-3**：环已拆——`depends_on: FEA-06-PREREQ-1` 现满足（PREREQ-1 `done` @ `residual_transfer_Q-33`）；四处自洽：PREREQ-1 卡 ✓、PLAN ✓、STATUS ✓、**checkpoint ✗**（无 Q-33 段 + §22 过时陈述，R2-P2-4）；residual 承接 ①② ✓ / ③ ✗（R2-P1-2）。
- **P1-1**：CLOSED——AC1 `:66` 按 frontendId；`builtin.fluent-dark` 明确为 visualThemeId 不参与 selector（与 `AppearanceSettings.cs:15-19` 代码事实一致）。
- **P1-2**：CLOSED——W-2b `:82` 优先级链完整；`AppOptions.cs:36/:228-236` 承接（CLI 非法值不拒收 → selector fail-safe，组合自洽）。
- **P1-3/P1-4**：P1-3 PARTIAL（唯一写者路径已定 `:61`；`AppearanceCoordinator.cs:14-18` D-1 remarks、`AppearanceStore.WriteAsync:62-76`、Appearance csproj 零引用——迁移与 SaveAsync 接线在写域内可行；缺口=生产 sink 注入点 R2-P1-1）；P1-4 CLOSED（`ThemeTokenSet` 扩展路径 `:62`，TokenMap `:204-206` 已预留）。
- **P1-5/P1-7**：P1-5 OPEN（R2-P1-4）；P1-7 CLOSED（禁止范围 `:75` 已声明 W-9 例外）。
- **AC2–AC4 可机械验收性**：AC2/AC3 可验收（App.Tests + Avalonia.Headless，测试表有命令行；断言强度弱为 P2 级遗留）；AC4 可验收（全量 sln）；AC5/AC6 不可机械验收（R2-P1-4）。
- **治理脚本**：`check.ps1` PASS（3 warnings 均非本卡阻塞）；`verify_pins.ps1` PASS 15/15。

## 4. 处置建议

1. **修 4 条 P1**（按 R2-P1-1 → R2-P1-4 顺序均可，互不阻塞；R2-P1-2/R2-P1-3 需 DSH 裁决口径，R2-P1-1/R2-P1-4 纯卡面补写）。
2. P2 逐项并入或明示接受遗留；R2-P2-4（checkpoint 补记）建议随下一治理 commit 一并落。
3. 修完派 **scope-r3**（同一独立席位或新派独立席位均可；本轮 Q-34 复核通道已恢复）。P0/P1=0 后即可释放实现。

## 5. 边界声明

本报告只审**范围/卡/冻结契约/写域/可执行性/治理指针**，不实现本卡，不审 PREREQ-2 未来代码，不构成对 P5/P6 架构方案的最终集成授权（R2-P1-3 的契约口径属 DSH 架构裁决权）。`check.ps1`/`verify_pins.ps1` 为只读参考，不替代审查。未修改源码/卡/设计/契约，未 commit/push；行号基于 `4659e59d3` 实测。
