# FEA-C02 V11R 契约条款级修订单（草案）

状态：**DRAFT / 未冻结 / 不释放实现 Task**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[V11R_AVALONIA_CONTRACT](../plan/V11R_AVALONIA_CONTRACT.md)（FROZEN v1，298 行）、[FEA-00 方案 r4](../design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md)（`74a772167`，r8 `approved`）、[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md) 的 C-02、[FEA-C01b 存储契约草案](FEA-C01b_STORAGE_CONTRACT_DRAFT.md)（r5 `approved`）

**边界声明**：本文件是**修订单草案**，不是对 V11R 合同的修改。V11R 合同为 `FROZEN`，任何改动须走本修订单 + 独立复核 + 用户确认后由 DSH 执行。**不冻结契约、不释放实现 Task。**

---

## 1. 范围

C-02 覆盖 V11R 合同的 **§1.1 / §1.2 / §2.2 / §2.3 / §2.4 / §3 / §4 / §6.1 / §6.3**，目标是把 Fluent 方案（E 方案）引入后必须调整的口径**逐条**写清，而不是整份重写合同。

统一格式：

```
### V-xx <条款>
- 现行文本：<引用或摘要>
- 修订文本 / 适用域：<新文本 或 适用域限定>
- 审查判据：<独立审查如何判定>
- 例外登记：<指向 §2.4 例外表 或 说明无需登记>
```

---

## 2. 逐条修订单

### V-01 §1.1 项目（新增 Fluent 主题包项目？）

- **现行文本**：三个项目（DesignSystem / ThemeEngine / App），单向引用 `App → ThemeEngine → DesignSystem`。
- **修订文本 / 适用域**：**不新增项目**。Fluent 作为 ThemeEngine 内的一个**主题包**（`builtin.fluent`）实现，与 `builtin.current-v2` 并列；令牌值差异通过主题包数据表达，不通过新 csproj 表达。
- **审查判据**：`git diff --stat` 不得新增 `NewManga.*.csproj`；`builtin.fluent` 的资源文件落在 ThemeEngine 既有主题目录结构内。
- **例外登记**：无需（§2.4 例外表不涉及项目结构）。

### V-02 §1.2 共享写权边界

- **现行文本**：`App.axaml`/`App.csproj`/`App.axaml.cs` 由 `design-platform`（M0 后仅 DSH）写；`Views/V2/**` 由 ui-shell/ui-studio 写。
- **修订文本 / 适用域**：新增一行——**Fluent 主题包资源**（`src/NewManga.ThemeEngine/Themes/Fluent/**`）由 **`theme-fluent`**（新 Owner，建议 ZCode）写；`App.axaml` 的 Fluent 切换入口仍由 DSH 写。
- **审查判据**：Fluent 相关 PR 的写者必须匹配；跨线改动需 DSH 在 Task 中显式记录。
- **例外登记**：无需。

### V-03 §2.2 令牌组（Fluent 的新增组）

- **现行文本**：V1 最低集 14 组（背景 5 级、描边、文本、强调、状态 7、状态底、字体族、字号、字重/行高、间距、圆角、尺寸、内边距、动效、图标）。
- **修订文本 / 适用域**：**新增 3 组**（Fluent 需要，`nm.fluent.visual/1` 主题包提供）：
  | 组 | 键示例 | 类型 |
  |---|---|---|
  | 材质 | `Nm.Material.Acrylic.Base/Tint/Opacity`、`Nm.Material.Mica.Enabled` | `IBrush`/`double`/`bool` |
  | 层次 | `Nm.Elevation.1/2/3`（阴影参数） | `BoxShadows` |
  | 焦点 | `Nm.Focus.Ring.Width/Offset/Color` | `double`/`IBrush` |
  **适用域限定**：这三组仅在 `builtin.fluent` 主题包内**必须**存在；`builtin.current-v2` 可缺省（回退为单色边框）。
- **审查判据**：Fluent 主题包缺任一键 → 判违规；current-v2 缺省 → 合规。
- **例外登记**：材质/层次组进入 §2.4 例外表的 `Fluent 视觉令牌` 行（见 V-05）。

### V-04 §2.3 状态令牌的使用方式

- **现行文本**：每个状态必须同时有色相 + 符号 + 文字标签；符号由 `StatusGlyph` 提供，UI 不得自造。
- **修订文本 / 适用域**：**保持不变**，Fluent 主题包必须沿用同一状态语义与符号集；仅允许色相不同（由主题包令牌值决定）。
- **审查判据**：Fluent 界面截图/测试中状态仍为「色 + 符号 + 文字」三要素。
- **例外登记**：无需。

### V-05 §2.4 例外登记（**核心冲突点**，对应 U-04）

- **现行文本**：硬规则禁止 `border-radius > 3px`、阴影、渐变、模糊；唯一例外 7 项（0/1px/Auto、Transparent、Margin=-2、高对比令牌、密度令牌、语义行高别名、muted 底色）。
- **修订文本 / 适用域**：**新增 2 行例外**（**per-scheme 限定**，仅 `builtin.fluent` 生效）：
  | 例外 | 范围 | 理由 |
  |---|---|---|
  | **Fluent 材质与层次** | 仅 `builtin.fluent` 主题包与使用其令牌的 UI | 亚克力/Mica/阴影是 Fluent 视觉语言的核心；**取值必须来自 V-03 的 `Nm.Material.*`/`Nm.Elevation.*` 令牌**，不得裸值；`builtin.current-v2` **不得**使用 |
  | **Fluent 圆角** | 仅 `builtin.fluent` | 允许 `Nm.Corner.Sm(4)/Md(6)/Lg(8)` 三档；`border-radius > 3px` 的禁令**仅对 current-v2 与 DM（Design System 原生控件模板）继续有效** |
- **审查判据**：① 任何 Fluent 视觉例外必须指向令牌（`{DynamicResource Nm.Material.*}` / `Nm.Elevation.*` / `Nm.Corner.*`），裸值仍判违规；② current-v2 下出现材质/阴影/圆角>3px → 判违规；③ 例外是否收敛到这两个主题包，由 L2/L3 审查按截图 + XAML 双证。
- **例外登记**：**本行即登记**（这是 U-04 的落点）。
- **待用户裁决**：U-04 —— 是否批准这两行例外（推荐：批准，per-scheme 限定 + 令牌强制）。

### V-06 §3 Design System 公开面

- **现行文本**：§3.1 标准控件 styles/classes；§3.2 自定义控件清单（40+）与分阶段上收规则。
- **修订文本 / 适用域**：**不新增控件**。Fluent 通过**主题包 + 既有控件模板的 Fluent 变体**实现；若 Fluent 需要新控件，走「先在 `Views/V2/<Area>/Controls/**` 本地实现，≥2 工作面使用后上收 DS」的既有规则。
- **审查判据**：Fluent 相关 diff 不得在 `NewManga.DesignSystem` 中新增控件类型（上收需单独 Task）。
- **例外登记**：无需。

### V-07 §4 Theme Engine 公开面

- **现行文本**：`ThemeKind { BuiltIn, User }`；ThemeEngine 公开面冻结（enum/接口签名）。
- **修订文本 / 适用域**：`builtin.fluent` 作为 `ThemeKind.BuiltIn` 的**第二个内置主题包**，不新增枚举值、不改接口签名；主题包 id 为 `builtin.fluent`，与 `builtin.current-v2` 并列。
- **审查判据**：`ThemeKind` 枚举值与公开方法签名不得变化；主题包注册表新增 `builtin.fluent` 条目。
- **例外登记**：无需（但仍受 V-05 视觉例外约束）。

### V-08 §6.1 UI 结构 / §6.3

- **现行文本**：新 UI 代码落在 `Views/V2/**`、`ViewModels/V2/**`、`Shell/V2/**`；§6.3 为 Shell/导航结构。
- **修订文本 / 适用域**：Fluent 界面为**同一套 UI 代码 + 不同主题包**，不新建 `Views/V2-Fluent/**` 目录树；若某页面在 Fluent 下需要不同布局，用 **`Classes` + 主题包资源**表达，不复制页面类。
- **审查判据**：不得出现 `*Fluent.axaml` 页面复制；页面类数量不因 Fluent 增加。
- **例外登记**：无需。

---

## 3. Fluent 定位（R-03 重申，防止误读）

- **Fluent = 视觉风格**，**不是** FluentAvalonia 依赖。禁止引入 `FluentAvaloniaUI` NuGet；所有 Fluent 观感通过 `nm.fluent.visual/1` 主题包令牌 + 既有控件模板实现。
- 「Fluent 风格」与「FluentAvalonia 库」是两个概念；审查时若发现 `FluentAvalonia` 引用即判违规（除非用户另行裁决）。

## 4. `nm.fluent.visual/1` 的定位与校验器归属

- **定位**：ThemeEngine 内的主题包 manifest（`nm.fluent.visual/1`），声明该包提供的令牌组、材质/层次/圆角例外（V-03/V-05）、与 `builtin.current-v2` 的差异清单。
- **校验器归属**：**ThemeEngine 的项目内校验器**（构建期 + 单测），不是 `tools/governance/check.ps1`。检查器只做机械治理检查，不解析主题包语义。
- **判据**：manifest 缺失或被手改 → 主题包加载失败；校验器覆盖「令牌齐全性 + 例外仅限 Fluent + 无裸值」三条。

## 5. 三处口径统一（R7-08）

| 口径来源 | 现状 | 统一后 |
|---|---|---|
| V11R §4.1（ThemeEngine 公开面） | 冻结的 enum/接口 | **以本修订单 V-07 为准**：不新增枚举值 |
| FEA 方案 §15.2（九条） | 方案侧九条口径 | **以本修订单逐条为准**；方案 §15.2 改为引用本文件 |
| FEA-01 C-02 | 描述性 | 冻结后以本文件为唯一契约文本 |

## 6. 冻结条件

1. 本修订单经**独立复核**确认与 V11R 合同、FEA 方案 r4 一致、无新增语义；
2. **用户裁决 U-04**（V-05 的两行 per-scheme 例外）——推荐批准；
3. `check.ps1` PASS（机械检查，仅结构条件）。

冻结后：C-02 关闭；C-03（外观持久化）可在本单之上冻结；Fluent 实现 Task 方可释放（且仍受 C-01b 冻结约束）。

## 7. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案：V-01…V-08 逐条修订单；明确 Fluent 定位（非 FluentAvalonia）、`nm.fluent.visual/1` 归属、三处口径统一；U-04 落点为 V-05 | DSH |
