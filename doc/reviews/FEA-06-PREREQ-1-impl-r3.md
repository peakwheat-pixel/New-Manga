---
task_id: FEA-06-PREREQ-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-implementer
base_commit: 3c0c7d50c
reviewed_head: 933de92e2
decision: changes_requested
counts: { P0: 0, P1: 5, P2: 16 }
---

# FEA-06-PREREQ-1 实现复核 r3（独立上下文；本席位未参与实现/返修/收口）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06-PREREQ-1.md`（`status: in_review`；范围 r3 approved `97677e402`） |
| base_commit | `3c0c7d50c`（impl-r2 被审 head） |
| reviewed_head | `933de92e2`（收口提交；实现 head `06b7a1b10`） |
| 实现者 | DSH（Codex 通道故障、ZCode 未安装） |
| reviewer | `fea05-wire-scope-reviewer`（DSH 派发 fresh 子 agent；未参与 PREREQ-1 实现/返修/收口；此前只读评审范围 r1–r3 + impl-r1/r2；符合 2026-10-31 上下文独立裁决） |
| 日期 | 2026-11-03 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 5 / P2 = 16（共 21）** |

> **一句话结论**：**changes_requested**。r2 的 5 条 P1 中 **2 条确认关闭**（r2-P1-1 layout 默认值、r2-P1-5 Elevation 颜色/spread 已知剩 P2），但 **r2-P1-3（FrontendId）仍未实现**：`AppOptions` 把 `frontend` 列入 `ValueKeys`（`:91`），`TryApply` 却没有 `case "frontend"`，`--frontend` 会落入 `default` 被报 `unknown option`（`:311-313`），属性仍无赋值/注入。**W-9/Q-32 的转移不成立**：goal §16 明确 Q-32 仍「待裁决」（`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md:162`），而卡 W-9（`:88`）已写「DSH 裁决」；`FEA-06-PREREQ-2.md` 未被修改，其 `allowed_paths`（`:21-34`）不含 `NewManga.ThemeEngine/**`、`NewManga.DesignSystem/**`、`NewManga.Appearance/**`，无法承接 `ThemeSettingsStore` 兼容写（r2-P1-2）与 Material Base/Tint + `ThemeLayerAllowedKeys`/R14/主题包 schema（r2-P1-4）。因此卡内 AC1/AC3 的 `<<MET>>` 不成立；AC5 文本要求 `nm.fluent.visual/1` manifest + `ThemeValidator` 显式测试，仍无实现（卡却标 `<<MET>>`）。此外 `canonical_evidence_status: complete` 与测试表全 `NOT_RUN`、`appearance-tests.log`（12）/`motion-tests.log`（7）/`themegen-check.log`（仅 default）等**旧证据**自相矛盾（8 项 sha256 虽均匹配）。独立全量 **977/0/57**、`TokenGen`/`ThemeGen --check` EXIT 0 与声明一致；`check.ps1` PASS（4 warnings）、`verify_pins` 15/15。

---

## 0. 方法与只读声明

- 只读核查被审 head；未修改源码/卡/设计；`git status --porcelain` 为空；未 commit/push；本报告为本轮唯一新增文件。
- 独立实测：`dotnet test apps/desktop-avalonia/NewManga.sln` → **EXIT 0**；各项目合计 **977 passed / 0 failed / 57 skipped**（Appearance 13、App 432、ThemeEngine 237、DS 85、ApplicationCore 31、CoreClient 128、Host 51）。`TokenGen -- --check` → **EXIT 0（rows 290）**；`ThemeGen -- --check` → **EXIT 0**。`check.ps1` PASS（4 warnings：11 非终态、STATUS/PLAN 80%、`evidence_dir` 含 3 个未登记过程文件）；`verify_pins` **15/15**。
- 阅读：r3 diff、卡 frontmatter/AC/W-9/证据表/Closeout、goal §16 Q-32 记录、PREREQ-2 卡、STATUS/PLAN/LEDGER、`AppOptions`/`AppearanceSettings`/`TokenMap`/`Tokens.Global`/主题生成器与 `verification/**`。

---

## 1. r2 逐项 disposition

| r2 ID | 判定 | r3 证据 |
|---|---|---|
| **r2-P1-1** layout 默认值 | **CLOSED** | `AppearanceSettings.cs:100/106/108` 已改 `top-band`/`stacked`/`fit-page`，与 `LayoutProfile.Default` 一致 ✓ |
| **r2-P1-2** ThemeSettingsStore 兼容写 | **OPEN（W-9 转移不成立）** | 卡 W-9 称转入 PREREQ-2；但 goal Q-32 **仍待裁决**；PREREQ-2 卡未修改、`allowed_paths` 不含 ThemeEngine/Persistence；`ThemeEngine/Persistence` 无 diff，兼容写/双写者收敛未实现。AC1 仍标 `<<MET>>` |
| **r2-P1-3** FrontendId | **OPEN（未实现）** | `AppOptions` 仅把 `frontend` 加入 `ValueKeys`（`:91`），`TryApply` 无 `case "frontend"`，`--frontend` 落入 `default` → `unknown option`（`:311-313`）；`AppOptions.FrontendId` 无赋值；无新测试（App.Tests 仍 432，未覆盖 `--frontend`）。AC2 仍标 `<<MET>>` |
| **r2-P1-4** Material Base/Tint/主题层 | **OPEN（W-9 转移不成立）** | 代码/生成物仍无 `Nm.Material.Acrylic.Base/Tint`；`Theming/**`、`R14ContractTests`、`ThemePackageJson` 无 diff；主题包仍 `material:"solid"`；W-9 以「不扩 schema」为由转移，与 r3 approved AC3 明确要求冲突。AC3 仍标 `<<MET>>` |
| **r2-P1-5** Elevation | **CLOSED（spread P2）** | `TokenMap` 改用 `rgba(0,0,0,0.15/0.20/0.25)`，生成 `0 1 2 #26000000`/`0 4 8 #33000000`/`0 8 16 #40000000`（alpha 正确）；spread 省略与 `<BoxShadows>` 格式化留 P2-4 |
| r2-P2-1…P2-19 | 见 §4 | 大部分未变；registry 顺序/light 块/JSON 形状/IO/原子写/Coordinator/P/Invoke/注释/未用引用/96 语义/迁移未落盘等仍在；证据陈旧升级为 P1-5 |

---

## 2. P1（5 条，必须修）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| **r3-P1-1** | `AppOptions.cs:33-36,91,311-313`；AC2；`App.Tests` | **`--frontend` 未实现**：`frontend` 进入 `ValueKeys` 但 `TryApply` 无对应 case；`TryApply` 的 `default` 直接报 `unknown option '--frontend'`，`FrontendId` 属性永远 null、无注入点。AC2 `<<MET>>` 不成立。 | 在 `TryApply` 增 `case "frontend"`：校验 `builtin.current-v2`/`builtin.fluent` 并赋值；默认 fail-safe；补 `--frontend` 解析/非法值测试。 |
| **r3-P1-2** | 卡 W-9 `:88`；goal `:162`（Q-32 待裁决）；`FEA-06-PREREQ-2.md:21-34`；ThemeEngine Persistence（无 diff）；AC1 | **W-9 对 r2-P1-2 的转移不成立**：Q-32 在 goal 仍「待裁决」，卡却记「DSH 裁决 2026-11-03」；PREREQ-2 未改卡、`allowed_paths` 不含 `NewManga.ThemeEngine/**`/`NewManga.Appearance/**`，无法实现 `ThemeSettingsStore` 兼容写/双写者收敛。AC1（含「`ThemeSettingsStore` 一个 release 兼容写」）`<<MET>>` 不成立。 | 二选一：①在本卡恢复实现（写域已含 ThemeEngine/Appearance；`Appearance→ThemeEngine` 的未使用引用可移除以打破循环，或把 sink adapter 放 App）；②先补 Q-32 正式裁决 + 修订 PREREQ-2 卡（W-9 行、任务、AC、allowed_paths 含 ThemeEngine/Persistence），再改 AC1 为「转 PREREQ-2」并留痕。 |
| **r3-P1-3** | 卡 W-9 `:88`；AC3 `:67`；`TokenMap`/`NmKeys`/`Tokens.Global`/主题包；`DesignSystem/Theming`/`R14ContractTests`/`ThemePackageJson`（无 diff） | **W-9 对 r2-P1-4 的转移不成立**：AC3 是 r3 approved 的硬要求（Material Base/Tint、`ThemeLayerAllowedKeys`/`R14ContractTests` 59/65、主题包 schema）；W-9 以「本卡不扩 schema」为由转移，属**未经范围修订的验收豁免**，且 PREREQ-2 写域/任务/AC 未承接。代码上 Base/Tint 仍完全缺失、主题包仍 `material:"solid"`。AC3 `<<MET>>` 不成立。 | 按 r3 scope 在本卡闭环（扩 schema/R14 计数/主题包）；或先由 DSH 做范围变更裁决并修订 PREREQ-2 卡（任务/AC/写域），再改本卡 AC3 状态；不能仅以 W-9 行 + `<<MET>>` 收口。 |
| **r3-P1-4** | 卡 AC5 `:69`；`Themes/fluent-dark.nmtheme`；`BuiltInThemeGenerator`/`BuiltInThemes`/`ThemePackageJson`；`themegen-check.log` | **AC5 `<<MET>>` 不成立**：AC5 文本要求 manifest `nm.fluent.visual/1` + `ThemeValidator.Validate`/`BuiltInThemes` 加载 + Current 不生效测试；现状无 `nm.fluent.visual/1`（schema 仍 `newmanga.theme/1`）、无 `ThemeValidator` 显式测试、`themegen-check.log` 仅 default-only 且未更新（P2 已有记录，不应同时标 MET）。 | 补 manifest 字段 + `ThemeValidator`/加载/Current 测试并重跑 `ThemeGen --check`；若本轮不实现，则 AC5 改回未 MET/转 P2 并记录，不能收口为 MET。 |
| **r3-P1-5** | 卡 `:92-118`（测试表/证据表/Closeout）；`verification/**`；`canonical_evidence_status: complete` | **收口证据/状态不自洽**：测试要求表仍全 `NOT_RUN`/「待补」，Canonical Evidence 却 `complete`；`appearance-tests.log` 仍 12（实际 13）、`motion-tests.log` 仍 7（实际 9）、`themegen-check.log` 仍 default-only；8 项 sha256 虽均匹配文件，但内容不能支撑 AC1/AC4/AC5 的 MET；Closeout 仍留「待关闭时填写」且末尾有落表外的 AC6 行（`:118`）。 | 重跑并更新各专项日志（Appearance 13/Motion 9/ThemeGen 含 fluent），把测试表改为实际命令/结果，Closeout 去除占位符/表外行，再更新 `canonical_evidence_status`。 |

---

## 3. AC1–AC6

| AC | 判定 | 说明 |
|---|---|---|
| AC1 | **MET 不成立（P1-2）** | layout 默认值已修；旧文件读取/true→三禁已补；`ThemeSettingsStore` 兼容写仍未实现/转移无效 |
| AC2 | **MET 不成立（P1-1）** | `AppOptions.FrontendId` 仍为死属性；`--frontend` 会被报 unknown；无解析/注入测试 |
| AC3 | **MET 不成立（P1-3）** | 96 已生成（P2-14 语义）；Material Base/Tint 缺失、ThemeLayer/R14/主题包 schema 未更新 |
| AC4 | **MET（P2-10/15 残留）** | 判据⑤/navigation 测试已补；`motion-tests.log` 仍为旧 7（证据 P1-5） |
| AC5 | **MET 不成立（P1-4）** | manifest/ThemeValidator 显式测试仍缺；主题包 `material:"solid"`；证据日志陈旧 |
| AC6 | **MET** | 独立 977/0/57；生成器 EXIT 0；`build.log`/`sln-test.log` 已更新 |

---

## 4. P2（16 条，建议/接受遗留）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| P2-1 | `ThemeRegistryTests`；`ThemeRegistry.cs:40` | 两 builtin ordinal 排序后 `All[0]` 为 `builtin.fluent-dark`；测试仅 `Skip(1)` 未断言 `ids[0]` | 断言 `ids[0]`/按 id 查找；评估 default 优先 |
| P2-2 | `fluent-dark.nmtheme:18`；`BuiltInThemes.cs:6-9` | 仍保留 `light` 块且 `supportsLight=false`；注释称生成/不校验与实际不符 | 删除死 light 块；修正注释 |
| P2-3 | `TokenMap` Focus.Ring.Color | Color 值仍为 `rgba(217,160,75,0.45)` 实现推导，设计仅给键名 | 引用 accent 令牌/补冻结依据 |
| P2-4 | `TokenDictionaryWriter.FormatBoxShadows`；`Tokens.Global` Elevation | `<BoxShadows>0 1 2 #26000000</BoxShadows>` 省略 spread、依赖 `ToString()`；无 DS 往返测试 | 显式 `x y blur spread #AARRGGBB` 并加单测 |
| P2-5 | `AppearanceJson.cs:112-155` | JSON 仍混用扁平 dotted key 与嵌套对象；C-03 无 JSON schema | 统一形状并记录 |
| P2-6 | `AppearanceJson` reader | 未知类别警告 bug、`schemaVersion>2` 无处理、`ReadLayout` 接受任意字符串 | 逐键警告/未来版本回退/layout 词表校验 |
| P2-7 | `AppearanceStore.Read` | `File.ReadAllText` IO/权限异常未捕获 | catch 并返回默认+警告 |
| P2-8 | `AppearanceStore.WriteAsync` | `File.Move(overwrite)` 无 `File.Replace`/fsync；测试仅查 `.tmp` | 改进并测试中断语义 |
| P2-9 | `AppearanceCoordinator` | 无 Save、未接入启动；`Reload_DoesNotTouchResources` 仅断言 settings | 明确写者/读取者；接入启动；补资源断言 |
| P2-10 | `AppearanceStore.cs:9`；`MotionResolver.cs:13-15` | 仍引不存在 `C-03 §2.5`；MotionResolver 判据注释映射仍错 | 修正注释/引用 |
| P2-11 | `WindowsMotionPreferenceSource.cs:18-52` | `[Out] bool[]`/`SetLastError` 未验；无平台源单测 | 改 `out int`/校验返回；补非 Windows/失败测试 |
| P2-12 | `NewManga.Appearance.csproj` | 引用 ThemeEngine 但 Appearance 源码未使用其类型 | 删除引用或复用 LayoutProfile |
| P2-13 | `AppearanceSettings.cs:120` | `MaterialAcrylicStrength` 默认 0.5 vs 设计 `Acrylic.Opacity=0.85` | 统一/明确映射 |
| P2-14 | `TokenMap` 96 | 范围 r3 AC3 要求「非令牌派生」，实现为 `DerivedGlobals` 令牌派生 | 保留令牌则改 AC 表述；否则改常量 |
| P2-15 | `AppearanceJsonTests.cs:54-60` | 旧测试名 `...WithAllCategoriesOff` 仍未断言 categories None（新 MotionResolver 测试覆盖） | 补断言/改名 |
| P2-16 | 治理 | `PLAN:37` DAG 仍写 PREREQ-1 `proposed`（行 `:21` 已 `in_review`）；`check.ps1` 第 4 警告列 `appearance-coordinator-tests.log`/`delivery-notes.md`/`theme-tests.log` 未登记；goal Q-32「待裁决」与卡 W-9「DSH 裁决」不一致 | 同步 PLAN DAG；登记/移出过程文件；统一 Q-32 记录 |

---

## 5. 写域/治理

- 写域：r3 变更均在卡 `allowed_paths` 内（含 Motion/AppOptions/GOAL）✓；本卡新增 `AppOptions`/`AppearanceSettings`/`TokenMap`/生成物/证据/断点文件。
- 证据：8 项 sha256 均匹配当前文件 ✓；但 `appearance-tests.log`(12)/`motion-tests.log`(7)/`themegen-check.log`(default-only) 未更新，`sln-test.log`/`build.log`/`tokengen-check.log` 已更新 977/290；`check.ps1` 4 warnings 中 `evidence_dir` 未登记过程文件属证据卫生（P2-16）。
- 治理：`check.ps1` PASS、`verify_pins` 15/15；STATUS `:7` in_review ✓、LEDGER `:43` in_review ✓，但 PLAN DAG `:37` 仍 proposed（P2-16）；goal Q-32 待裁决 vs 卡 W-9 宣称 DSH 裁决（P1-2/P1-3 与 P2-16）。

## 6. 处置建议

1. **r3-P1-1**：补 `case "frontend"` 解析/校验/赋值 + 测试，使 AC2 真正 MET。
2. **r3-P1-2/P1-3**：先正式裁决 Q-32 并修订 PREREQ-2 卡（W-9 行、任务、AC、`allowed_paths` 含 ThemeEngine/Persistence/DesignSystem/Appearance 或明确本卡闭环），再改本卡 AC1/AC3 状态；不能以 W-9 行 + `<<MET>>` 收口。
3. **r3-P1-4**：补 `nm.fluent.visual/1` manifest + `ThemeValidator`/加载/Current 测试，或把 AC5 改回未 MET。
4. **r3-P1-5**：重跑并更新全部专项证据日志，修正测试表/Closeout/`canonical_evidence_status`。
5. P2 逐项处置；修完派 **impl-r4**（同一独立席位）复核。P0/P1=0 且 AC1–AC6 可验收后再批准。

## 7. 边界声明

本报告只审被审 head 的实现/测试/证据/写域/收口与冻结契约一致性，不审 PREREQ-2/FEA-06 主卡本身；未修改源码/卡/设计，未 commit/push；`check.ps1`/`verify_pins` 为只读参考，独立命令与结果见 §0；行号基于 `933de92e2` 实测。
