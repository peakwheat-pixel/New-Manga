---
task_id: FEA-06-PREREQ-2
reviewer: ZCode（主会话）
reviewer_kind: agent
author: dsh-lead
base_commit: cad5ebde3（卡声明）
reviewed_head: df089039c
decision: changes_requested
counts: { P0: 0, P1: 1, P2: 5 }
---

# FEA-06-PREREQ-2 范围冻结复核 r3（独立上下文；本席位未参与本卡起草/实现）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06-PREREQ-2.md`（`proposed`；`approval: pending_review`） |
| reviewed_head | `df089039c`（`fix(fea-06-prereq-2): 处置 scope-r2 的 P1×4…`，2026-11-02 09:29 +0800）；`git status --short` 干净 |
| 审查范围 | 仅 r2 的 4 条 P1 是否关闭 + 是否引入新问题（r1/r2 已闭合项不重开，r2 的 P2 只记延续状态） |
| reviewer | **ZCode（主会话）**，DSH 派发（2026-10-31 上下文独立裁决：产出变更的会话不得自审）；未参与 FEA-06-PREREQ-2 的起草、r1/r2 处置修订与任何实现 |
| 日期 | 2026-11-02（被审 head 提交后同日） |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 1 / P2 = 5** |

> **一句话结论**：r2 的四条 P1 **全部实质闭合**——sink 注入点两文件入写域（`ThemeSettingsStore` 仅有的两个 src 创建点）、Q-33 residual ③ 由 P7/AC7/测试表三处承接且「非无主豁免」恢复自洽、P6 改判主题层令牌路径后 **C-02 V-07 判据逐条不被触碰（我方独立判定：无需 UNFREEZE）**、AC5/AC6/AC7 测试行齐全。**唯一阻塞项**是禁止范围（卡 `:79`）残留的「新增 `ThemeMaterial.Fluent` 值属本卡 W-9 范围」——它是 r2 版 P6（加枚举值路径）的配套例外声明，与 r3 改判后的 P6「明确不新增枚举值」和 W-11「`ThemeMaterial` 枚举与 `ThemeTokenSet` 签名不变」**直接矛盾**；若实现者据此许可新增枚举值将触碰 C-02 §5/V-07 并违反 W-11 的 UNFREEZE 护栏。一行文字修正后即可 rev-r4 放行，P5/P6/P7 主方向均无需再动。

---

## 0. 方法与只读声明

- 只读核查被审 head `df089039c`；未修改卡/代码/设计/契约；未 commit/push；本报告为本轮唯一新增文件（落盘于本卡写域 `doc/reviews/FEA-06-PREREQ-2-*.md`）。
- 本轮实测：`check.ps1` → **PASS（3 warnings：10 非终态、STATUS 3028B/29 行 80%、PLAN 3946B/62 行 80%，与 r2 同源无新增）**；`verify_pins.ps1` → **PASS（all 15）**，C-02 冻结字节未被触碰——与 W-11「无需 UNFREEZE」的现状一致（本轮复核期间无人改契约）。
- 阅读：本卡全文；PREREQ-1 卡（done/Q-33 段/残余清单/D-1）；r2 报告；C-02 修订单 V-03/V-05/V-07（`:86-91`）+ §4（`:115-119`）+ §5（`:121-127`）；C-03 草案 §2.1/§3；goal checkpoint §25（r2 处置记录）；代码事实（行号实测于 `df089039c`）：`ThemeEngineThemeStudioService.cs`、`StubThemeStudioService.cs`、`ThemeModels.cs`、`DesignSystemThemeManager.cs`、`R14ContractTests.cs`、`NmKeys.g.cs`、`BuiltInThemeGenerator.cs`；STATUS/PLAN 指针。

---

## 1. r2 四条 P1 逐项 disposition

| r2 ID | 判定 | 理由（含行号实测） |
|---|---|---|
| **R2-P1-1**（sink 注入点写域/机制） | **CLOSED** | ①写域：`allowed_paths` `:30-31` 已补 `App/ViewModels/V2/ThemeStudio/ThemeEngineThemeStudioService.cs` 与 `StubThemeStudioService.cs`——实测这两个文件正是 `ThemeSettingsStore` 仅有的两个 src 创建点（`ThemeEngineThemeStudioService.cs:82` 于 `CreateProduction`（`:71-93`，注释明言「the only construction path the shipped UI uses」）；`StubThemeStudioService.cs:56` 沙箱链），sink 注入位置由此**事实唯一化**，不存在第三注入点。②机制：P5（`:63`）写明「App 侧 sink adapter `IThemeSettingsSink`，避免 ThemeEngine→Appearance 引用」——sink 的实现侧（App）、接口解耦方向（ThemeEngine 不引 Appearance，防循环引用）均已定义；「sink adapter + 注入到仅有的两个创建点」的组合排除了 r2 担心的三条坏路径（越域/静态服务定位/sink 不接线）。残余表述精度见 R3-P2-1 |
| **R2-P1-2**（Q-33 residual ③ 无落点） | **CLOSED** | P7（`:64`）+ AC7（`:75`）+ 测试表 AC7 行（`:99`，`ThemeEngine.Tests` 的 `ThemeValidator`/`BuiltInThemes`）三处承接。落地可行性实测：`ThemeMetadata.Extra`（`IReadOnlyDictionary<string,string>`，`ThemeModels.cs:290-291`，「Additional, ordered author metadata…preserved」）真实存在，P7「按 `ThemePackageJson` 现有 schema 能承载的最小形式」的假设成立；fluent-dark 种子定义在 `BuiltInThemeGenerator.cs`（`Themes/` 目录，写域 `:27` 覆盖），manifest 条目经种子定义 + ThemeGen 重生成落盘，不需改工具代码（`ThemeEngine/tools/**` 虽不在写域，但最小路径不触碰它）。自洽性：residual 三条现为 ①→P5、②→P6、③→P7 全部有主，Q-33「非无主豁免」声明（PREREQ-1 卡 `:133`）与事实的矛盾消除。残余见 R3-P2-2/R3-P2-4 |
| **R2-P1-3**（C-02 V-07 合规路径未闭合） | **CLOSED** | P6（`:65`）改判主题层令牌路径并写明「**明确不新增 `ThemeMaterial` 枚举值、不改 `ThemeTokenSet` 构造器签名**（C-02 V-07…），因此**不需要契约 UNFREEZE**」；W-11（`:90`）以 DSH 裁决（Q-35）记录同一口径 + 护栏「若后续确需改公开面，须先出 UNFREEZE 记录再改」。**我方独立逐判据核对（详见 §3）：V-07 的判据——`ThemeKind` 枚举值不变 ✓、公开方法签名不变 ✓、frontend id 不入 ThemeEngine 公开面 ✓——主题层令牌路径一条都不触碰；`NmKeys`（`DesignSystem/Generated/`）与 `ThemeLayerAllowedKeys`（`DesignSystemThemeManager.cs:129-130`）均在 DesignSystem 侧，不属 V-07（§4 Theme Engine 公开面）管辖；`ThemeTokenSet.Colors` 本就是 `IReadOnlyDictionary<string,string>`（`ThemeModels.cs:241`），主题包 colors 承载 Base/Tint 取值无需改构造器签名（现 6 参，`ThemeModels.cs:240-246`）；`ThemeMaterial` 现仅 `Solid/None`（`:94-99`），不加值；且 `Nm.Material.Acrylic.Base/Tint` 两键正是 C-02 V-03 材质组明列键（修订单 `:51`），键的存在有冻结契约依据。**verify_pins 15/15 佐证 C-02 冻结字节无人触碰**。**结论：同意改判，无需 UNFREEZE**。唯一残留是禁止范围未同步（→ R3-P1-1） |
| **R2-P1-4**（AC5/AC6 无测试行） | **CLOSED** | 测试要求表（`:94-100`）现为五行：AC1–AC3（`App.Tests`，Avalonia.Headless）、**AC5**（`Appearance.Tests` + `App.Tests`，.NET 9/Avalonia.Headless）、**AC6**（`DesignSystem.Tests` + `ThemeEngine.Tests` + `TokenGen -- --check` + `ThemeGen -- --check`，.NET 9 + 生成管线）、**AC7**（`ThemeEngine.Tests`，.NET 9）、AC4（全量 sln）——命令/前提/证据落点（`verification/FEA-06-PREREQ-2/**`，写域 `:42`）齐备，符合 PREREQ-1 卡先例格式。残余见 R3-P2-1（AC5 工程列举） |

### r2 P2×7 延续状态（不重开，仅记录）

| r2 ID | r3 状态 | 说明 |
|---|---|---|
| R2-P2-1（AC1 记录面未定义） | OPEN | AC1（`:69`）仍「→ V2 + 记录」，接受遗留 |
| R2-P2-2（AC3 对照设计 04 骨架） | OPEN | P3/AC3（`:61,:71`）未补骨架构成，接受遗留 |
| R2-P2-3（W-9/W-10 行缺失） | **PARTIAL** | W-10（`:89`）与 W-11（`:90`）已补；**W-9 行仍缺**（仍仅以括号引用散见 P5/P6/AC5/AC6） |
| R2-P2-4（checkpoint 无 Q-33/r2 记录） | **CLOSED** | checkpoint §25（`GOAL-PROGRESS-2026-11-02.md:192-200`）已补 scope-r2 结果、四条 P1 处置与 W-11/Q-35 记录；`:179` 有 W-10 记录 |
| R2-P2-5（P5「双写」措辞 vs C-03:68） | OPEN | P5 文字未变；写域补两文件已部分缓解误读风险，接受遗留 |
| R2-P2-6（base_commit 滞后） | OPEN | `:13` 仍 `cad5ebde3`；属 release 时点动作（届时刷新为当刻 main head） |
| R2-P2-7（P4 fluent-dark 负例标注） | OPEN | P4（`:60`）仍「fluent/fluent-dark/v2/未知」，接受遗留 |

---

## 2. 新增 findings

### P1（1 条，修后放行）

| ID | 严重度 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **R3-P1-1** | P1 | 卡 `:79`（禁止范围）vs `:65`（P6）、`:90`（W-11） | **禁止范围残留与改判直接矛盾**：禁止范围括号内「新增 `ThemeMaterial.Fluent` 值属本卡 W-9 范围」是 r2 版 P6（`ThemeMaterial` 加 `Fluent` 值路径）的配套授权声明；r3 已把 P6 改判为「**明确不新增** `ThemeMaterial` 枚举值、**不改** `ThemeTokenSet` 构造器签名」并以 W-11 记录「`ThemeMaterial` 枚举与 `ThemeTokenSet` 签名**不变**，故无需 UNFREEZE」，但禁止范围未同步。三处文本现呈「许可 vs 禁止」冲突：若实现者以禁止范围为授权边界新增该枚举值，将直接触碰 C-02 §5「以本修订单 V-07 为准：**不新增枚举值**」与 V-07 判据，并违反 W-11「若后续确需改公开面，须先出 UNFREEZE 记录再改」的护栏——正是 r2 花一整轮消除的合规分叉风险复发。范围冻结 Gate 的交付物就是无歧义基线，本条为一行文字修正成本 | 删除或改写该括号子句，例：「（`newmanga-default` 字节不变；W-9 例外**不含公开面变化**——`ThemeMaterial` 枚举与 `ThemeTokenSet` 签名不变，见 P6/W-11）」 |

### P2（5 条，建议修/接受遗留）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| R3-P2-1 | 卡 `:63`（P5）、`:97`（AC5 行） | ①P5 未逐字写 sink 传入形态（r2 建议的「由组合根传入 `CreateProduction`/构造器」），实现者仍可在「新增构造器重载 / 可选参数」间选择；若选择**修改既有** `ThemeSettingsStore` 构造器签名（现 `ThemeSettingsStore.cs` 两参），会与 W-11「不改公开签名」的保守口径产生争议。②AC5 行未列 `ThemeEngine.Tests`——`ThemeSettingsStore` 双写本体的单测自然落点在 ThemeEngine 测试工程（AC6/AC4 全量可兜底，判别性稍弱） | P5 补一句「sink 以**新增重载/可选参数**注入，不改既有构造器签名」；AC5 行可加 `ThemeEngine.Tests` 或注明由 AC4 全量覆盖 |
| R3-P2-2 | 卡 `:64`（P7）、`:75`（AC7）；C-02 `:119`（§4 判据） | P7/AC7 的「`ThemeValidator.Validate` 显式测试」语义未定界：仅正向验证（fluent-dark 含 manifest 条目通过 Validate），还是含 C-02 §4 判据字面的负例（「manifest 缺失或被手改 → 主题包加载失败」）。另实测 `ThemeValidator.cs` 在 `ThemeEngine/Validation/`——该子目录**不在** allowed_paths（写域仅 `Persistence/Models/Serialization/Themes` 四子目录），隐式锁定「不改 validator、只加测试」的最小路径（与 P7 文字一致），但该边界未显式声明，若实现者需为 manifest 存在性加校验逻辑将越域 | 卡内显式声明：P7 = manifest 条目落盘 + 现有 `Validate` 的显式测试用例（不改 `ThemeValidator`）；C-02 §4「缺失即失败」的完整校验器义务归属（FEA-06 或后续 Task）由 DSH 注记 |
| R3-P2-3 | 卡 `:65`（P6「59/65 计数随主题层键面 +2 同步」）；`DesignSystemThemeManager.cs:114-130,:333-343` | 计数同步表述不精确：Base/Tint 只能进 `ThemeLayerAllowedKeys`（可选键），**不能进 `ThemeLayerRequiredKeys`**——Required 键要求所有主题包（含 `newmanga-default`）供键，否则 palette 继承 fail-closed（`DesignSystemThemeManager.cs:333-343`「cannot inherit theme-layer key」会拒绝加载），既破坏 V2 又违反 C-02 V-03「Current 主题可缺省」。因此正确同步是 **59 不变、65→67**，而「59/65 计数…+2」字面可误读为两计数各 +2 | P6 改为「`ThemeLayerAllowedKeys` 65→67（Base/Tint 为可选键，不进 Required 59）」 |
| R3-P2-4 | PREREQ-1 卡 `:133`（Q-33 声明） | 「转移目标已修订（P5/P6 + AC5/AC6 + 写域）」为 r2 时点快照，未含 r3 新增的 ③ 承接（P7/AC7）；residual 清单（`:134`）本身列 ③，无事实错误，但声明行与现状有轻微漂移 | 该行补注「③→P7/AC7（scope-r3）」（PREREQ-1 卡在其自身 allowed_paths 内，可补） |
| R3-P2-5 | STATUS `:7`、PLAN `:22,:37` | 治理指针滞后：STATUS「r2 待」、PLAN「scope-r1 changes_requested，待 r2」——实际 r2 已出（changes_requested，2026-11-03 报告），现 r3 在途 | 随 r3 收口/release 一并刷新为实际状态 |

---

## 3. 指定核查项结论（指令逐条对应）

- **R2-P1-1**：CLOSED（§1 表；两文件 = `ThemeSettingsStore` 仅有的两个 src 创建点，`ThemeEngineThemeStudioService.cs:82`/`StubThemeStudioService.cs:56`；P5 写明 App 侧 sink adapter 与解耦理由）。
- **R2-P1-2**：CLOSED（§1 表；P7/AC7/测试表三处承接，`ThemeMetadata.Extra` 承载位真实存在，与 Q-33「非无主豁免」自洽恢复）。
- **R2-P1-3**：CLOSED，且**我方明确表态：无需 UNFREEZE，没有任何一条 V-07 判据被触碰**——逐条：①「`ThemeKind` 枚举值与公开方法签名不得变化」：P6 不改 `ThemeKind`、不加 `ThemeMaterial` 值、不改 `ThemeTokenSet` 构造器（6 参保持），`NmKeys` 常量与 `ThemeLayerAllowedKeys` 均在 DesignSystem 侧（V-07 管 ThemeEngine §4 公开面）；②「视觉主题注册表新增 `builtin.fluent-dark` 条目」：该义务 PREREQ-1 P5b/W-8 已承载，P6 不新增枚举值不与之冲突；③「frontend id 不进入 ThemeEngine 公开面」：frontendId 归 `NewManga.Appearance`/selector（P1/P5），不入 ThemeEngine。键本身的契约依据 = C-02 V-03 材质组明列键（`:51`）。W-11 已记录裁决（Q-35）与「先 UNFREEZE 再改」护栏。
- **R2-P1-4**：CLOSED（§1 表；AC5/AC6/AC7 三行 + AC1–AC3/AC4 共五行齐备）。
- **治理脚本**：`check.ps1` PASS（3 warnings 与 r2 同源，无新增、非本卡阻塞）；`verify_pins.ps1` PASS all 15（C-02/C-03 等冻结字节未动）。

## 4. 处置建议

1. **修 1 条 P1**（R3-P1-1，纯卡面一行文字修正，互不阻塞其他项）；P2 逐项并入或明示接受遗留（R3-P2-3 建议随 P1 一并改写，同为 P6 措辞；R3-P2-5 随收口统一刷新）。
2. 修完可直接 **rev-r4**（只核 R3-P1-1 一条的闭合即可，新派独立席位或本席位均可——本席位未参与实现，符合上下文独立）；P0/P1=0 后即可置 ready 释放实现。
3. r2 的 R2-P2-6（base_commit 刷新）留到 release 动作时执行。

## 5. 边界声明

本报告只审**范围/卡/冻结契约/写域/可执行性/治理指针**，不实现本卡，不审 PREREQ-2 未来代码；对 P6 主题层令牌路径的认可不构成对 FEA-06 视觉例外的集成授权（V-05 的 per-scheme 例外仍由其自身判据约束）。`check.ps1`/`verify_pins.ps1` 为只读参考，不替代审查。未修改源码/卡/设计/契约，未 commit/push；行号基于 `df089039c` 实测。
