---
task_id: FEA-06-PREREQ-2
reviewer: ZCode（DSH Lead 经 subagent_zcode 派发的独立上下文子代理；本席位）
reviewer_kind: agent
author: dsh-lead
base_commit: cad5ebde3（卡声明；r4 时点另见 §6 观察项——release 已将 base_commit 刷新为 a33778608）
reviewed_head: a33778608
decision: approved
counts: { P0: 0, P1: 0, P2: 1 }
---

# FEA-06-PREREQ-2 范围冻结复核 r4（独立上下文第二席位；未参与本卡起草/实现）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06-PREREQ-2.md`（`a33778608` 时点：`proposed`；`approval: pending_review`） |
| reviewed_head | `a33778608`（`docs(handoff): 更新交接材料中的 scope-r3 结果与下一步（r4）`）；本席位开始时 `git status --short` 干净、HEAD 即该 commit |
| 审查范围 | 窄面确认：只核 R3-P1-1 一条的闭合 + 是否引入新问题（r1/r2/r3 已闭合项不重开，P2 只记延续状态） |
| reviewer | **ZCode 独立上下文子代理（subagent_zcode 子任务）**——DSH Lead（本项目 DeepSeek Harness Lead 会话）通过 `subagent_zcode` 派发的独立上下文子代理；未参与 FEA-06-PREREQ-2 的起草、r1/r2/r3 处置修订与任何实现 |
| reviewer 来源 | **DSH Lead 会话派发 / subagent_zcode 子任务**（2026-10-31 上下文独立裁决：产出变更的会话不得自审，作者可派独立上下文子代理执行 Review） |
| 日期 | 2026-11-02（被审 head 提交后同日） |
| 结论 | **approved** |
| 计数 | **P0 = 0 / P1 = 0 / P2 = 1**（另有观察项 R4-OBS-1，不计入 P 计数） |

> **一句话结论**：R3-P1-1 **实质闭合**——禁止范围（卡 `:79`）中与 P6/W-11 矛盾的「新增 `ThemeMaterial.Fluent` 值属本卡 W-9 范围」授权声明已删除，改写为与 P6、W-11 及 C-02 V-07 判据完全一致的禁止表述，全卡无任何诱导新增枚举值/改签名的残留；`a6652022d`/`a33778608` 两变更集只动允许文件、无代码或契约字节变化；R3-P2-5 指针如实修正。**无新增 P0/P1。** 唯一新 P2：R3-P2-3 处置后的 P6 计数括号归因「（全局令牌数不增）」与 R14 断言的代码事实不符（59 实为 `ThemeLayerRequiredKeys.Count`，非全局令牌数）——行为要求（59 不变、65→67）本身无歧义，不阻塞放行。另披露：本席位复核期间仓库出现并行 r4 报告与 release 提交（R4-OBS-1），详见 §6。

---

## 0. 方法、只读声明与时间线披露

- 只读核查被审 head `a33778608` 的树；未修改卡/代码/设计/契约；未 commit/push；本报告为本席位唯一写入的文件（落盘于本卡写域 `doc/reviews/FEA-06-PREREQ-2-*.md`）。
- **并行席位与时间线披露（如实记录）**：本席位开始时 HEAD = `a33778608`、工作区 clean（实测）。复核进行中仓库前进至 `da148d8c7`，新增两提交：`b2a45af6d`（09:43:41，`release(fea-06-prereq-2): scope-r4 approved（P0/P1/P2=0）→ 置 ready…`，**内含一份同名 r4 报告**，reviewer 署名「ZCode（主会话）」，decision approved / 0-0-0）与 `da148d8c7`（09:43:53，交接材料更新为实现阶段）。即本任务被执行了两次（另一席位先行完成并支撑了 release）。本席位结论独立形成于读取该并行报告之前（下列全部证据均为本席位自行实测）；按派发指令「若已存在同名文件则覆盖」，本报告覆盖工作区同名文件，`b2a45af6d` 中的既有版本在 git 历史中字节保留。两席位结论同向（approved），差异仅在 P2 计数与 §6 观察项（详见 §2/§6）。
- 本席位实测（`a33778608` 时点）：`check.ps1` → **PASS（3 warnings：10 非终态 Task、STATUS 3028B/29 行 80%、PLAN 3941B/62 行 80%，与 r3 同源无新增）**；`verify_pins.ps1` → **PASS（all 15）**，C-02 冻结字节（`bb365ca891a7`）未被触碰。release 后时点（`da148d8c7`）复跑 `check.ps1` 仍 **PASS（3 warnings 同源；STATUS 3036B、PLAN 3945B 系指针文字刷新所致）**。
- 阅读：本卡全文（行号实测于 `a33778608`）；r3 报告全文；`a6652022d`/`a33778608` 全量 diff；C-02 修订单 V-03 材质组（`FEA-C02_V11R_AMENDMENT_DRAFT.md:45-52`）、V-07（`:84-91`）、§4（校验器归属）、§5（`:121-127`）；STATUS/PLAN/LEDGER 双时点；checkpoint §25–§27；代码事实（行号实测）：`R14ContractTests.cs`、`DesignSystemThemeManager.cs`、`ThemeModels.cs`、`ThemeEngineThemeStudioService.cs`、`StubThemeStudioService.cs`、`ThemeValidator.cs`（定位）、`BuiltInThemeGenerator.cs`（定位）；并行席位 r4 报告（仅用于差异披露，见 §0 第二条）。

---

## 1. R3-P1-1 闭合核验（附实测行号）—— **CLOSED**

**旧文**（`df089039c` 卡 `:79`，本席位 `git show df089039c:doc/tasks/FEA-06-PREREQ-2.md` 实证）：

> 不改 ThemeEngine 的既有主题包语义（`newmanga-default` 字节不变；新增 `ThemeMaterial.Fluent` 值属本卡 W-9 范围）

**新文**（`a33778608` 卡 `:79`）：

> 不改 ThemeEngine 的既有主题包语义（`newmanga-default` 字节不变；**不新增 `ThemeMaterial` 枚举值、不改 `ThemeTokenSet` 构造器签名**——Material 走主题层令牌，见 P6/W-11）

**判定依据**（全部本席位实测）：

1. **矛盾源已删除**：原括号子句（r2 版 P6 加枚举值路径的配套授权声明）整句消失；`git show a6652022d` 的卡面 diff 实证该行仅此一处改写，「许可 vs 禁止」冲突不复存在。
2. **与 P6 一致**（卡 `:65`）：P6 写明「**明确不新增 `ThemeMaterial` 枚举值、不改 `ThemeTokenSet` 构造器签名**（C-02 V-07…），因此**不需要契约 UNFREEZE**」——禁止范围新文以「见 P6/W-11」显式交叉引用，两处同向。
3. **与 W-11 一致**（卡 `:90`）：「`ThemeMaterial` 枚举与 `ThemeTokenSet` 签名**不变**，故**无需 UNFREEZE**；若后续确需改公开面，须先出 UNFREEZE 记录再改」——禁止范围新文与该裁决口径零冲突。
4. **与冻结契约判据对齐**：C-02 修订单 V-07 审查判据「`ThemeKind` 枚举值与公开方法签名不得变化；视觉主题注册表新增 `builtin.fluent-dark` 条目；frontend id 不进入 ThemeEngine 公开面」（`FEA-C02_V11R_AMENDMENT_DRAFT.md:90` 附近）及 §5 汇总「以本修订单 V-07 为准：**不新增枚举值**」——`ThemeMaterial`（`ThemeModels.cs:94-99`，现值 `Solid/None`）与 `ThemeTokenSet`（`ThemeModels.cs:240-246`，sealed record 主构造器 6 参：Colors/Typography/Corners/Material/Elevation/Motion）均属 ThemeEngine 公开面，禁止范围新文本与之零冲突。`verify_pins` 15/15（两时点）佐证 C-02 冻结字节自 r3 以来无人触碰。
5. **残留扫描**：全卡检索 `ThemeMaterial` 共 4 处——`:63`（P5 sink 行，`ThemeSettingsStore` 引用语境，不含枚举语义）、`:65`（P6，否定式）、`:79`（禁止范围，否定式）、`:90`（W-11，不变式）——**无任何授权新增枚举值或改签名的残留表述**。

---

## 2. 对 `a6652022d` / `a33778608` 变更集的核验

### 2.1 变更范围（`git show --stat` 实测）

- `a6652022d`（4 文件，+100/−5）：`doc/tasks/FEA-06-PREREQ-2.md`（卡，写域内）、`doc/STATUS.md`（写域内）、`doc/REBASELINE_PLAN.md`（写域内）、`doc/reviews/FEA-06-PREREQ-2-scope-r3.md`（r3 报告入库，写域通配 `doc/reviews/FEA-06-PREREQ-2-*.md` 内）。**无代码、无契约字节变化**；卡面 diff 仅 `:65`（R3-P2-3 计数措辞）与 `:79`（R3-P1-1）两处，无暗改。
- `a33778608`（1 文件，+2/−2）：仅 `doc/handoffs/FEA-06-PREREQ-2-session-handoff.md`——§4.1 表 r3 行由「未产出（子代理未完成）」改为实际结果（changes_requested，P0=0/P1=1/P2=5，与 r3 报告 frontmatter 一致），§4.3 下一步由「复核 scope-r3」改为「复核 scope-r4（只核 R3-P1-1 闭合）」——与派发事实一致。交接材料不在卡写域，属 DSH 治理职权文档，沿 r3 报告 R2-P2-4 对 checkpoint/handoff 的先例口径不列为 finding，如实登记。

### 2.2 R3-P2-3（R14 计数措辞）—— **实质闭合，残余一处归因瑕疵（→ R4-P2-1）**

- 旧文：「`R14ContractTests` 的 59/65 计数随主题层键面 +2 同步」（字面可误读为两计数各 +2）。
- 新文（卡 `:65` 末段）：「`R14ContractTests` 的计数：**59 不变**（全局令牌数不增），**65 → 67**（主题层可覆写键面 +2，即 `Nm.Material.Acrylic.Base/.Tint`）」。
- **歧义已消除、核心方向正确**：本席位代码实测——`R14ContractTests.cs:92-93` 断言 `Assert.Equal(59, DesignSystemThemeManager.ThemeLayerRequiredKeys.Count)` 与 `Assert.Equal(65, …ThemeLayerAllowedKeys.Count)`；`DesignSystemThemeManager.cs:113-121` Required = PaletteColor(35)+Font(3)+FontSize(6)+LineHeight(9)+Corner(3)+Motion(3) = 59，`:129-130` Allowed = Required + LineBox(6) = 65。Base/Tint 只能进 Allowed（可选键面 65→67）、不得进 Required（`:333-343` Required 键缺失时 `cannot inherit theme-layer key` → 拒绝加载，若入 Required 将破坏 `newmanga-default`/V2 加载并违反 C-02 V-03「Current 主题可缺省」）。**「59 不变、65→67」与代码事实的方向完全一致**；实现者同步断言时的行为要求无歧义。
- **残余**：新文括号把 59 不变归因为「全局令牌数不增」——**与断言语义不符**：59 对应 `ThemeLayerRequiredKeys`（主题层必需键），并非全局令牌（`Tokens.Global.axaml` 键）数；59 不变的真实机制是 Base/Tint 为 `Nm.Material.*` 前缀键、不加入 Required 组（`PaletteColorKeys` 仅按 `Nm.Color.` 前缀过滤自 `NmKeys.All`，`DesignSystemThemeManager.cs:107-111`）。r3 R3-P2-3 的建议措辞即「Base/Tint 为可选键，不进 Required 59」。此归因不改变任何行为要求，记 P2（见 §3）。

### 2.3 R3-P2-5（STATUS/PLAN 指针）—— **CLOSED（如实修正）**

- `a33778608` 时点实测：STATUS `:7`「…r4 待」；PLAN `:22`（DAG 表行）「scope-r3 P1×1 已修，待 r4」；PLAN `:37`（当前 DAG 段）「待 r4」——与本席位复核时点的事实（r4 在途）一致，且修掉了 r3 指出的「待 r2」滞后。
- `check.ps1` 两时点均 PASS（3 warnings 同源、无新增），指针修正未引入治理破口。
- 后续滚动（release 后指针已再刷新为 ready/scope-r4 approved，`b2a45af6d`）属 DSH 收口职权，不在本被审 head 范围内，仅登记。

### 2.4 是否引入新自洽性破口

禁止范围新文的括号是对「主题包语义不变」的操作化界定，「Material 走主题层令牌，见 P6/W-11」把 Material 实现路径显式指向 P6 授权的主题层令牌方案——禁止（公开面）与授权（令牌路径）不再交叠；P5（迁移/双写/sink）、P6（`NmKeys` 常量 + `ThemeLayerAllowedKeys` 放行 + 主题包 colors）、P7（fluent-dark manifest 条目）均可在此边界内无歧义实施。**未发现新的自相矛盾。**

---

## 3. 新增 findings

| ID | 严重度 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| R4-P2-1 | P2 | 卡 `:65`（P6 计数括号）；代码基线 `R14ContractTests.cs:92`、`DesignSystemThemeManager.cs:113-121,:129-130` | 「**59 不变**（全局令牌数不增）」的归因与 R14 断言语义不符：59 = `ThemeLayerRequiredKeys.Count`（35+3+6+9+3+3），不是全局令牌数；59 不变的真实原因是 Base/Tint 属 `Nm.Material.*` 键、不加入 Required 组（`PaletteColorKeys` 仅过滤 `Nm.Color.*`）。行为要求（断言 59 不变、Allowed 65→67）无歧义，不阻塞实现 | 括号改为「Base/Tint 为可选键，不进 Required 59」或「（`ThemeLayerRequiredKeys` 不增）」——与 r3 R3-P2-3 建议措辞对齐；随实现轮顺手修正即可 |

**是否无新增 P0/P1：是（P0 = 0 / P1 = 0）。**

上轮 P2 延续状态（不重开，仅记录）：R3-P2-1（P5 sink 传入形态/AC5 工程列举）OPEN 接受遗留；R3-P2-2（P7/AC7 Validate 语义定界 + `ThemeValidator.cs` 位于 `ThemeEngine/Validation/` 不在写域的隐式边界）OPEN 接受遗留；R3-P2-4（PREREQ-1 卡 `:133` 声明行时点漂移）OPEN 接受遗留；R2-P2-3 的 W-9 行缺失（仅括号引用散见 P5/P6/AC5/AC6）OPEN 接受遗留；R2-P2-6（base_commit 刷新）已在 release `b2a45af6d` 落实为 `a33778608`。

---

## 4. 附加独立审查（放行依据）

### 4.1 卡面自洽（P/AC/测试表/W 编号闭环）

- 任务拆解 P1–P7 齐全（表格呈现顺序 P5→P7→P6，编号无缺漏、无重复）；AC1–AC7 齐全且与 P 一一映射（P1→AC1 selector 决策表、P2→AC2 组合根、P3→AC3 Shell 骨架、P4→AC1–AC4 测试载体、P5→AC5、P6→AC6、P7→AC7）；测试要求表五行（`:96-100`）覆盖 AC1–AC3 / AC5 / AC6 / AC7 / AC4 全部七个 AC，命令、前提与证据落点齐备。
- 附加裁决点 W-1/W-2b/W-2/W-3/W-10/W-11 均有行且被 P/AC 引用闭环；W-9 仍无独立行（r3 R2-P2-3 已记 PARTIAL 延续，非本轮范围）。
- 禁止范围（`:79`）与 P5/P6/P7 授权边界经 §2.4 核对无矛盾。

### 4.2 allowed_paths 对 P1–P7 的实现可行性（代码实测）

- **P5（sink 注入两文件）**：`allowed_paths` `:30-31` 的 `ThemeEngineThemeStudioService.cs`/`StubThemeStudioService.cs` 实测正是 `ThemeSettingsStore` 仅有的两个 src 创建点——`ThemeEngineThemeStudioService.cs:71`（`CreateProduction`）`:82`（`new ThemeSettingsStore(settingsFilePath, registry)`）、`StubThemeStudioService.cs:56`；迁移源头 `App/Services/**`（`:23`）与目标 `NewManga.Appearance/**`（`:29`）均在写域。可行。
- **P6（ThemeLayerAllowedKeys/R14）**：`NmKeys` 与 `DesignSystemThemeManager` 均在 `NewManga.DesignSystem/**`（`:28`）覆盖内，R14 测试在 `NewManga.DesignSystem.Tests/**`（`:40`）；Allowed 放行（65→67）经 `:129-130` 的显式 concat 可达，Required 59 不动时 `:333-343` fail-closed 继承保证 V2/`newmanga-default` 不受影响。可行；计数归因措辞见 R4-P2-1。
- **P7（`ThemeEngine/Themes|Serialization|Models/**`）**：承载位 `ThemeMetadata.Extra`（`IReadOnlyDictionary<string,string>`，`ThemeModels.cs:290`）真实存在；fluent-dark 种子定义 `BuiltInThemeGenerator.cs` 位于 `Themes/`（写域 `:27`）；`ThemeValidator.cs` 位于 `ThemeEngine/Validation/`（不在写域四子目录）——隐式锁定「不改 validator、只加测试」的最小路径，与 r3 R3-P2-2 登记口径一致。可行。

### 4.3 治理指针一致性（双时点）

- **被审时点（`a33778608`）**：STATUS `:7` / PLAN `:22,:37` =「待 r4」，与事实一致；`check.ps1` PASS（3 warnings）；`verify_pins.ps1` PASS（all 15，C-02 `bb365ca891a7` 未动）。
- **复核期间 release 后（`da148d8c7`）**：卡 `status: ready`、`approval: scope_review_r4_approved_2026-11-02`、`base_commit: a33778608`；STATUS/PLAN/TASK_LEDGER（`:47` ready 行、状态计数 proposed 2/ready 2）同步；`check.ps1` 复跑仍 PASS（3 warnings 同源）。指针自洽，无 dangling。

---

## 5. 结论

**P0 = 0 / P1 = 0 / P2 = 1 → `approved`。** R3-P1-1 实质闭合（§1），处置变更集干净（§2），无新增 P0/P1（§3），卡面自洽、写域可行、治理指针一致（§4）。范围冻结通过；R4-P2-1 为实现轮可顺手修正的措辞项，不构成放行障碍。release 已由 DSH 于 `b2a45af6d` 执行（ready + base_commit=a33778608），与本结论同向。

## 6. 观察项与过程披露（不计入 P 计数）

**R4-OBS-1（并行双席位 r4 与 release 时序）**：本席位复核进行中，`b2a45af6d`（09:43:41）已入库另一席位的同名 r4 报告（署名「ZCode（主会话）」，approved / 0-0-0）并执行 release（置 ready、指针同步、checkpoint §27 记「scope-r4 approved，P0=0/P1=0/P2=0」）。本席位报告落盘晚于该 release——按派发指令覆盖工作区同名文件，`b2a45af6d` 版本在 git 历史字节保留。两席位结论同向（approved），release 有效性不受影响；差异两点需 DSH 知悉/注记：①本报告 **P2=1**（R4-P2-1 计数归因），与 §27/release message 的「P2=0」口径不同——并行报告未覆盖该代码级核验；②同一复核任务双席位并行、报告同名覆盖的事实建议在 checkpoint 或 STATUS 补一行注记，避免后续考古时误读为单份报告被改写。背景（checkpoint §26 所载）：主会话切换模型供应商后子代理额度不稳、subagent_zcode 为较可靠复核通道——多通道并行派发可理解为对该环境的冗余保障。

## 7. 边界声明

本报告只审**范围/契约/写域/可执行性/治理指针**，不实现本卡，不审 PREREQ-2 未来代码，不构成对 FEA-06 视觉例外的集成授权（C-02 V-05 的 per-scheme 例外仍由其自身判据约束）。`check.ps1`/`verify_pins.ps1` 为只读参考，不替代审查。本席位未修改源码/卡/契约/STATUS/PLAN/LEDGER，未 commit/push；行号基于 `a33778608` 实测（§4.3 双时点与 §6 观察项中 release 后事实另行标注时点）。对并行席位报告的引用仅限 §0/§6 的差异披露，本报告全部判定依据为本席位独立实测。
