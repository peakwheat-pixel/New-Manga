---
task_id: FEA-06-PREREQ-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-implementer
base_commit: b547e229e
reviewed_head: 3c0c7d50c
decision: changes_requested
counts: { P0: 0, P1: 5, P2: 19 }
---

# FEA-06-PREREQ-1 实现复核 r2（独立上下文；本席位未参与实现/返修）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06-PREREQ-1.md`（范围 r3 approved `97677e402`；`status: ready`） |
| base_commit | `b547e229e`（impl-r1 被审 head） |
| reviewed_head | `3c0c7d50c`（`fix(fea-06-prereq-1): P1-9 — fluent-dark 由 ThemeGen 生成…全量 977/0/57`） |
| 实现者 | DSH（Codex 通道故障、ZCode 未安装） |
| reviewer | `fea05-wire-scope-reviewer`（DSH 派发 fresh 子 agent；未参与 PREREQ-1 实现/返修；此前只读评审范围 r1–r3 与 impl-r1；符合 2026-10-31 上下文独立裁决） |
| 日期 | 2026-11-02 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 5 / P2 = 19（共 24）** |

> **一句话结论**：**changes_requested**。impl-r1 的 10 条 P1 中 **5 条确认关闭**（P1-1 词表、P1-8 判据⑤/navigation、P1-9 ThemeGen 生成覆盖、P1-10 写域；P1-7 的 96 已生成但实现为「令牌派生」而非范围 r3 的「非令牌派生」，降为 P2）。**仍有 5 条 P1 未关闭**：①`LayoutSettings` 默认值仍是 `expanded/split/fit`（未做 P1-2 修复）；②`AppOptions.FrontendId` 只有属性声明、无解析/注入（P1-4）；③`Nm.Material.Acrylic.Base/Tint` 仍完全缺失、`ThemeLayerAllowedKeys`/`R14ContractTests`/主题包 schema 未更新（P1-5）；④Elevation 原始串虽改成设计值，但 `TokenValues.ParseHexColor` 按 CSS `#RRGGBBAA` 解析设计值 `#26000000`（AARRGGBB），生成结果仍为 `0 1 2 #00260000`（alpha=0），实际阴影颜色/透明度仍错（P1-6）；⑤旧 `theme-settings.json` 读取已补，但 `ThemeSettingsStore` 一个 release 兼容写/双写者收敛仍未实现（P1-3）。独立全量 **977/0/57**、`TokenGen`/`ThemeGen` 均 EXIT 0 与声明一致；另发现交付证据日志仍为旧计数。

---

## 0. 方法与只读声明

- 只读核查被审 head；未修改源码/卡/设计；`git status --porcelain` 为空；未 commit/push；本报告为本轮唯一新增文件。
- 独立实测：`dotnet test apps/desktop-avalonia/NewManga.sln` → **EXIT 0**；各项目合计 **977 passed / 0 failed / 57 skipped**（Appearance 13、App 432、ThemeEngine 237、DesignSystem 85、ApplicationCore 31、CoreClient 128、Host 51）。`TokenGen -- --check` → **EXIT 0（rows 290）**；`ThemeGen -- --check` → **EXIT 0**。`check.ps1` PASS（3 warnings）；`verify_pins` 15/15。
- 阅读：r2 diff 全量、`AppearanceJson/Store/Settings`、`AppOptions`、`MotionResolver`、`TokenMap`/生成物、`BuiltInThemeGenerator`/`fluent-dark.nmtheme`、测试与 `verification/**`、卡 allowed_paths/STATUS/PLAN/LEDGER。

---

## 1. r1 逐项 disposition

| r1 ID | 判定 | r2 证据 |
|---|---|---|
| **P1-1** `motion.categories` 词表 | **CLOSED** | `MotionCategories` 改为 `Navigation`/`Feedback`/`Decorative`；JSON 写入/读取 `navigation`/`feedback`/`decorative`（`AppearanceJson.cs:136-138,231-233`）；Resolver/测试同步 ✓ |
| **P1-2** `layout.*` 词表/默认值 | **OPEN → P1-1（r2）** | `AppearanceSettings.cs:100,106,108` 仍为 `"expanded"`/`"split"`/`"fit"`；r2 diff 未触碰该文件默认值；`LayoutProfile.Default`（`ThemeModels.cs:340-345`）为 `top-band/stacked/fit-page`。Lead 所称已修未落卡 |
| **P1-3** 旧文档迁移/兼容写 | **PARTIAL → P1-2（r2）** | 已补：旧 `theme-settings.json` 读取（`AppearanceStore.cs:34-48`）、true→categories None（`AppearanceJson` + 新测试）、`themeId=builtin.fluent-dark→frontendId=builtin.fluent`、`FollowSystemAccent` 旧键回退、13 测试。未补：`ThemeSettingsStore` 一个 release 兼容写/双写者收敛（`ThemeEngine/Persistence` 无 diff）；迁移读结果未落新文件；`LegacyDocument` 对新文件的语义仍为「首次读取内容」 |
| **P1-4** AC2 FrontendId/启动注入 | **PARTIAL → P1-3（r2）** | `AppOptions.FrontendId` 属性已加（`:33-36`），但**全仓无任何赋值/解析**（`git grep` 只有声明；`Parse` 未处理）；Coordinator/启动未接入。AC2「可注入」仍未实现 |
| **P1-5** Material Base/Tint/主题层 | **OPEN → P1-4（r2）** | `Nm.Material.Acrylic.Base/Tint` 全仓仍无实现（`git grep` 仅 `TokenMap.cs:206` 注释）；无 `Theming/**`、无 `R14ContractTests`/`ThemeLayerAllowedKeys` 变更；主题包 `material:"solid"`；仅 Opacity 修为 0.85 |
| **P1-6** Elevation 值 | **OPEN → P1-5（r2）** | `TokenMap` 原始串已改为设计值 `0 1 2 0 #26000000` 等，但 `TokenValues.ParseHexColor`（`:8-10,259-271`）按 CSS `#RRGGBBAA` 解析 8 位 hex，设计值按 AARRGGBB 书写（同设计 01:42 `#33007ACC`）；生成 `<BoxShadows>` 仍为 `0 1 2 #00260000`/`0 4 8 #00330000`/`0 8 16 #00400000`（alpha=0，且 `FormatBoxShadows` 丢 spread）。**实际颜色仍错** |
| **P1-7** G-1b 96 | **CLOSED（P2 残留）** | `Nm.Size.MatrixColumnMin` 已生成（`TokenMap` DerivedGlobals + `NmKeys`）；但实现为**令牌派生**，范围 r3 AC3 要求「作为设计常量登记（**非令牌派生**）」→ 见 P2-16 |
| **P1-8** AC4 判据⑤/④ | **CLOSED** | 新增 `LegacyReducedMotion_True_MigratesToReduce_WithEveryCategoryOff`、`NavigationCategory_IsDisabledUnderReduce_AndHonouredUnderFull`（`MotionResolverTests` +2）；Appearance 旧测试名不再是被唯一证据；类别改为 Navigation/Feedback/Decorative ✓（注释判据编号仍不准，P2-10） |
| **P1-9** AC5 主题包生成 | **CLOSED（manifest P2）** | `BuiltInThemeGenerator.GeneratedFilePaths` 已含 `Themes/fluent-dark.nmtheme`；`ThemeGen --check` EXIT 0 且覆盖该文件（生成器内构建 `fluentPackage`）；`ThemeElevation.Raised`、dark-only descriptor、tags 更新；`BuiltInThemes` 加载/注册不变 ✓。仍无 `nm.fluent.visual/1` manifest 与 `ThemeValidator` 显式测试（P2-17，Lead 已记录） |
| **P1-10** 写域外改动 | **CLOSED** | 卡 `allowed_paths` 已补 `MotionResolver.cs`/`WindowsMotionPreferenceSource.cs`/`AppOptions.cs`/`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md`（卡 diff +4 行）✓ |

---

## 2. P1（5 条，必须修）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| **r2-P1-1** | `AppearanceSettings.cs:100-108`；`ThemeModels.cs:330-345`；`JsonSupport.cs:93-121`；C-03 `:39` | **`layout.*` 默认值仍是 `expanded`/`split`/`fit`**：`expanded`/`fit` 在 `LayoutNavigation`/`ReaderLayout` 中不存在；`workbench` 默认 `split` 与 `LayoutProfile.Default` 的 `stacked` 不同；C-03 §2.2「旧 LayoutProfile 六字段同名保留」不成立。r2 仅改 categories，未改此文件 | 默认值改为 `top-band`/`grid`/`comfortable`/`stacked`/`fit-page`；补布局词表校验与迁移测试 |
| **r2-P1-2** | `AppearanceStore.cs:34-48`；ThemeEngine `ThemeSettingsStore`/`ThemeService`（未改） | **旧 `theme-settings.json` 兼容写/双写者收敛仍未实现**：Appearance 侧读取迁移已补，但 ThemeEngine 仍在写旧文件、`IThemePersistence` 未变为 sink；C-03 §3 的「一个 release 兼容写」与唯一写者纪律未落地；迁移结果也未落 `presentation-settings.json`（只读一次后返回 settings） | 在 ThemeEngine `ThemeSettingsStore.SaveAsync` 实现一个 release 兼容写/停写标记，Appearance 首次迁移后写新文件；补兼容写与双写测试 |
| **r2-P1-3** | `AppOptions.cs:33-36`；`AppOptions.Parse`；AC2 | **`AppOptions.FrontendId` 是死属性**：只声明 `{ get; private set; }`，无 `--frontend` 解析/Appearance 注入/`Parse` 赋值；`git grep FrontendId` 仅声明处。AC2「可注入」未成立 | 在 `Parse` 中解析（如 `--frontend=<id>`）并校验 `builtin.current-v2`/`builtin.fluent`，默认 `builtin.current-v2`；加测试 |
| **r2-P1-4** | `TokenMap.cs:206`；`Generated/NmKeys.g.cs`/`Tokens.Global.axaml`；`fluent-dark.nmtheme:70-71,130-131`；`DesignSystem/Theming`/`R14ContractTests`（未改）；C-02 V-03/V-05；范围 r3 AC3 | **Material 仍不完整**：`Nm.Material.Acrylic.Base/Tint` 在代码/生成物/主题包均不存在；Material 仅 `.Opacity`/`Mica.Enabled` 两键；主题包 `material:"solid"`；范围 r3 AC3 要求的 `ThemeLayerAllowedKeys`/`R14ContractTests` 59/65 计数与主题包 schema 更新未发生 | 落地 Base/Tint（全局或主题包 schema，按 C-02 V-03 择一并写清）；更新 `ThemeLayerAllowedKeys`/R14 计数/`NmKeys`/主题包 schema 与测试；补 Current 不生效断言 |
| **r2-P1-5** | `TokenValues.cs:8-10,259-271`；`Tokens.Global.axaml` 当前 Elevation 行；`TokenDictionaryWriter.FormatBoxShadows`；设计 01:52-54 | **Elevation 生成结果仍错**：设计值 `#26000000`/`#33000000`/`#40000000` 是 AARRGGBB，`ParseHexColor` 按 CSS #RRGGBBAA 解析 → 生成 `#00260000` 等 alpha=0；且 `FormatBoxShadows` 丢 spread，`<BoxShadows>` 输出 `0 1 2 #00260000` 与设计 `0 1 2 0 #26000000` 不等价 | 派生值改用 `rgba(0,0,0,0.149)` 等 CSS 形式或按设计 AARRGGBB 约定解析；保持 spread 字段；加 BoxShadows 单测断言 Avalonia `BoxShadows` 实际值 |

---

## 3. AC1–AC6 逐项

| AC | 判定 | 说明 |
|---|---|---|
| AC1 | **P1** | categories 词表/迁移/旧文件读取已修；layout 默认值与兼容写仍缺（r2-P1-1/P1-2）；测试 13 覆盖迁移/兼容写？仅旧文件读取/迁移，无兼容写 |
| AC2 | **P1** | FrontendId 死属性（r2-P1-3）；Coordinator 仍未接入启动（P2-9） |
| AC3 | **P1** | 96 已生成（P2-16 词义）；Material Base/Tint 缺失（r2-P1-4）；Elevation 实际值仍错（r2-P1-5）；`ThemeLayerAllowedKeys`/R14 未更新 |
| AC4 | **通过（P2 残留）** | 判据⑤/navigation 测试已补；auto/full/reduce/平台降级测试齐；注释判据编号仍不准（P2-10） |
| AC5 | **通过（P2 残留）** | fluent-dark 已由 ThemeGen 生成/覆盖；manifest `nm.fluent.visual/1` 与 ThemeValidator 显式测试仍缺（P2-17） |
| AC6 | **通过** | 独立 977/0/57；两个生成器 EXIT 0；`build.log` 0 警告/0 错误 |

---

## 4. P2（19 条，建议/接受遗留）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| P2-1 | `ThemeRegistryTests`；`ThemeRegistry.cs:40` | 两 builtin ordinal 排序后 `All[0]` 为 `builtin.fluent-dark`；测试仅 `Skip(1)` 未断言 `ids[0]`，未核查消费者 | 断言 `ids[0]`/按 id 查找；评估 default 优先 |
| P2-2 | `fluent-dark.nmtheme:18`；`BuiltInThemes.cs:6-9` | 仍保留 `light` token 块但 `supportsLight=false`；注释称 built-in 生成/不校验与实际不符 | 删除死 light 块；修正注释 |
| P2-3 | `TokenMap` Focus.Ring.Color | Color 值仍为实现推导 `rgba(217,160,75,0.45)`，设计只给键名未给值 | 引用 accent 令牌/补冻结依据 |
| P2-4 | `TokenDictionaryWriter.FormatBoxShadows`；`TokenValues.ParseBoxShadows` | 丢 spread/依赖 `ToString()`；无 DS 往返/非法输入测试（颜色问题已升 P1-5） | 显式格式化 `x y blur spread color` 并加单测 |
| P2-5 | `AppearanceJson.cs:112-155` | 规范 JSON 仍混用扁平 dotted key 与嵌套对象；C-03 无 JSON schema | 统一形状并在验证文档记录 |
| P2-6 | `AppearanceJson` reader | 未知类别警告仅在累积 None 时触发；`schemaVersion>2` 无处理；`ReadLayout` 仍接受任意字符串（r2-P1-1 的 validation 部分） | 逐键警告；未来版本回退；layout 词表校验 |
| P2-7 | `AppearanceStore.Read` | `File.ReadAllText` 的 IO/权限异常未捕获（读失败可能阻断启动） | catch IOException/UnauthorizedAccessException 返回默认+警告 |
| P2-8 | `AppearanceStore.WriteAsync`；测试 | `File.Move(overwrite)` 无 `File.Replace`/fsync；测试只查 `.tmp` 不存在 | 改进原子写并测试中断语义 |
| P2-9 | `AppearanceCoordinator` | 无 Save API、未接入启动；`Reload_DoesNotTouchResources` 仅断言 settings 未断言资源 | 明确写者/读取者；接入启动；补资源断言 |
| P2-10 | `AppearanceStore.cs:9`；`MotionResolver.cs:13-15` | 注释仍引不存在 `C-03 §2.5`；MotionResolver 判据注释仍把 ①/②/③ 映射错（设计 ② full 不跟随系统、③ auto 假源） | 修正注释/引用 |
| P2-11 | `WindowsMotionPreferenceSource.cs:18-52` | `[Out] bool[]` 传 `BOOL*`、`SetLastError` 未用；无平台源单测 | 改 `out int`/校验返回；补非 Windows/失败测试 |
| P2-12 | `NewManga.Appearance.csproj` | 引用 `NewManga.ThemeEngine` 但 Appearance 源码未使用其类型 | 删除引用或复用 LayoutProfile |
| P2-13 | 卡 frontmatter/Canonical Evidence；`verification/**` | 卡仍 `status: ready`、`approval` 自由文本、Canonical Evidence 空；`appearance-tests.log`（12）/`motion-tests.log`（7）/`tokengen-check.log`（289）/`themegen-check.log`（仅 default）**仍为旧计数/旧覆盖**，与 r2 实际 13/9/290/含 fluent 不符 | 更新卡状态与证据日志；填 Canonical Evidence |
| P2-14 | `AppearanceSettings.cs:120`；设计 01:43 | `MaterialAcrylicStrength` 默认 0.5，与设计 `Acrylic.Opacity=0.85` 不一致 | 取 0.85 或明确两者映射 |
| P2-15 | `AppearanceJsonTests.cs:54-60` | 旧测试名 `...WithAllCategoriesOff` 仍未断言 categories None（新 MotionResolver 测试覆盖了等价断言） | 补断言或改名 |
| P2-16 | `TokenMap` 96 | 范围 r3 AC3 要求「非令牌派生」，实现为 `DerivedGlobals` 令牌派生 | 保留令牌则改 AC 表述；否则改为常量类 |
| P2-17 | `fluent-dark.nmtheme`；`ThemePackageJson`；`BuiltInGeneratorTests` | `nm.fluent.visual/1` manifest（metadata.extra）与 `ThemeValidator` 显式测试未加（Lead 已记录）；包 `material:"solid"` 仍非 Fluent 材质语义 | 补 manifest/校验测试；Material 随 P1-4 落地 |
| P2-18 | `AppearanceStore` 迁移路径 | 迁移读取结果未写 `presentation-settings.json`；`LegacyDocument` 对新文件仍存「首读内容」（名不副实） | 迁移后写新文件；拆分 `LegacyDocument` 语义 |
| P2-19 | `verification/**` 证据 | 见 P2-13：旧日志未更新会误导 AC 证据（虽 `sln-test.log` 已更新 977、两个生成器独立复跑通过） | 重跑并更新各测试/生成器日志，注明日期/commit |

---

## 5. 写域/证据审计

- 写域：卡 `allowed_paths` 已补 `MotionResolver.cs`/`WindowsMotionPreferenceSource.cs`/`AppOptions.cs`/`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md`（P1-10 关闭）；r2 变更文件均落在允许范围内 ✓。
- 生成产物：`NmKeys.g.cs`/`Tokens.Global.axaml`/`TokenMap.md` 经 TokenGen 生成，`--check` EXIT 0 ✓；`fluent-dark.nmtheme` 现由 `BuiltInThemeGenerator` 生成且被 `ThemeGen --check` 覆盖 ✓；Elevation 生成值仍错（r2-P1-5）。
- 证据：独立全量 977/0/57、TokenGen rows 290、ThemeGen EXIT 0 与声明一致；但 `verification` 下多个专项日志仍为旧计数/旧覆盖（P2-13/P2-19），Canonical Evidence 未填。
- 卡状态仍 `ready`（实现完成但未进入交付/复核状态）、`approval` 为非枚举自由文本（P2-13）。

## 6. 处置建议

1. 修 **r2-P1-1**（layout 默认值）、**r2-P1-2**（ThemeSettingsStore 兼容写/双写者）、**r2-P1-3**（FrontendId 解析/注入）、**r2-P1-4**（Material Base/Tint + ThemeLayer/R14/主题包 schema）、**r2-P1-5**（Elevation 颜色/spread 与解析约定）。
2. 修完重跑全量/生成器并更新 `verification/**` 日志（P2-13/P2-19），填 Canonical Evidence。
3. P2 逐项处置（manifest/validator、registry 顺序、注释、IO、原子写等）。
4. 修完派 **impl-r3**（同一独立席位）复核；P0/P1=0 且 AC1–AC6 可验收后批准。

## 7. 边界声明

本报告只审被审 head 的实现/测试/证据/写域与冻结契约一致性，不审 PREREQ-2/FEA-06 主卡；未修改源码/卡/设计，未 commit/push；`check.ps1`/`verify_pins` 为只读参考，独立命令与结果见 §0；行号基于 `3c0c7d50c` 实测。
