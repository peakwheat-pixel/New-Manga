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
- **修订文本 / 适用域**：**本修订单不新增项目**；Fluent 的主题包部分落在 ThemeEngine 内（见 V-07）。**界面项目**（`Frontends.Fluent`、Application/Presentation）的新增**按方案 §15.2 的 §1.1 行**——需 DSH 批准并单独建 Task，不在本修订单范围内。
- **审查判据**：**本修订单的改动**不得新增 `NewManga.*.csproj`；Fluent 主题包资源落在 `apps/desktop-avalonia/src/NewManga.ThemeEngine/Themes/**` 既有结构内。新增界面项目须有对应的独立 Task 与 DSH 批准记录。
- **例外登记**：无需（§2.4 例外表不涉及项目结构）。

### V-02 §1.2 共享写权边界

- **现行文本**：`App.axaml`/`App.csproj`/`App.axaml.cs` 由 `design-platform`（M0 后仅 DSH）写；`Views/V2/**` 由 ui-shell/ui-studio 写。
- **修订文本 / 适用域**：新增一行——**Fluent 主题包资源**（`apps/desktop-avalonia/src/NewManga.ThemeEngine/Themes/**`）由 **DSH 逐 Task 指派**（建议 ZCode）写；`App.axaml` 的 Fluent 切换入口仍由 DSH 写。
- **审查判据**：Fluent 相关 PR 的写者必须匹配；跨线改动需 DSH 在 Task 中显式记录。
- **例外登记**：无需。

### V-03 §2.2 令牌组（Fluent 的新增组）

- **现行文本**：V1 最低集 15 组（背景 5 级、描边、文本、强调、状态 7、状态底、字体族、字号、字重/行高、间距、圆角、尺寸、内边距、动效、图标）。
- **修订文本 / 适用域**：**新增 4 组**（Fluent 需要，`nm.fluent.visual/1` 主题包提供）：
  | 组 | 键示例 | 类型 |
  |---|---|---|
  | 材质 | `Nm.Material.Acrylic.Base/Tint/Opacity`、`Nm.Material.Mica.Enabled` | `IBrush`/`double`/`bool` |
  | 层次 | `Nm.Elevation.1/2/3`（阴影参数） | `BoxShadows` |
  | 焦点 | `Nm.Focus.Ring.Width/Offset/Color` | `double`/`IBrush` |
  | 圆角（Fluent 扩展） | `Nm.Corner.Fluent.Sm(4)/Md(6)/Lg(8)` | `CornerRadius` |

> 上述四组为 **Fluent 专属最小集**，不改变 V11R §2.2 对 Current 主题的全局义务（V-03 末尾）。
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
  | **Fluent 圆角** | 仅视觉主题 `builtin.fluent-dark`（及同 frontend 的其他 Fluent 视觉主题） | 冻结组 `Nm.Corner.None/Sm(2)/Md(3)` **不变**；Fluent 额外使用 `Nm.Corner.Fluent.Sm(4)/Md(6)/Lg(8)`（**新增组，随 V-03 登记**）；`border-radius > 3px` 的禁令**仅对 Current 主题包与 DS 原生控件模板继续有效** |
- **审查判据**：① 任何 Fluent 视觉例外必须指向令牌（`{DynamicResource Nm.Material.*}` / `Nm.Elevation.*` / `Nm.Corner.*`），裸值仍判违规；② current-v2 下出现材质/阴影/圆角>3px → 判违规；③ 例外是否收敛到这两个主题包，由 L2/L3 审查按截图 + XAML 双证。
- **例外登记**：**本行即登记**（这是 U-04 的落点）。**数值时序**：4/6/8 与材质参数的具体取值由 FEA-04b 四页设计基线确认（方案 `:1032`），本修订单只冻结「键存在 + 仅 Fluent 生效」的结构。
- **待用户裁决**：U-04 —— 是否批准这两行例外（推荐：批准，per-scheme 限定 + 令牌强制）。

### V-06 §3 Design System 公开面

- **现行文本**：§3.1 标准控件 styles/classes；§3.2 自定义控件清单（40 个）与分阶段上收规则。
- **修订文本 / 适用域**：**不新增控件**。Fluent 通过**主题包 + 既有控件模板的 Fluent 变体**实现；若 Fluent 需要新控件，走「先在 `Views/V2/<Area>/Controls/**` 本地实现，≥2 工作面使用后上收 DS」的既有规则。
- **审查判据**：Fluent 相关 diff 不得在 `NewManga.DesignSystem` 中新增控件类型（上收需单独 Task）。
- **例外登记**：无需。

### V-07 §4 Theme Engine 公开面

- **现行文本**：`ThemeKind { BuiltIn, User }`；ThemeEngine 公开面冻结（enum/接口签名）。
- **修订文本 / 适用域**：**区分两个 id 体系**——① **frontend id**（`newmanga.frontend/1` schema）：`builtin.current-v2` / `builtin.fluent`，由方案 §15.2 定义（`activeFrontendId`、`perFrontend`），**不在 ThemeEngine 契约内**；② **视觉主题 id**（`ThemeKind.BuiltIn`）：现有 `newmanga-default`，新增 **`builtin.fluent-dark`**（方案 `:302` `defaultVisualTheme`），不新增枚举值、不改接口签名。`perFrontend` 映射：`builtin.current-v2 → newmanga-default`、`builtin.fluent → builtin.fluent-dark`。
- **审查判据**：`ThemeKind` 枚举值与公开方法签名不得变化；视觉主题注册表新增 `builtin.fluent-dark` 条目；frontend id 不进入 ThemeEngine 公开面。
- **例外登记**：无需（但仍受 V-05 视觉例外约束）。

### V-08a §6.1 空间与模式

- **现行文本**：§6.1 定义**空间与模式**（`SpaceId{Library,Studio,Console}`、`StudioMode{Page,Batch}`、`ShellSurface{Spaces,ThemeStudio,ReaderOverlay}`、`ShellState` 唯一状态源、`IWorkspaceView`、`AppShellV2` 唯一窗口内容）；§6.3 定义**快捷键**（`Ctrl+1/2/3`、`Tab`、`Ctrl+K` 等，由 `Shell/V2/KeyMap.cs` 单一注册表实现）。
- **修订文本 / 适用域**：Fluent 界面为**独立 frontend 项目**（方案 §15.2 的 `Frontends.Fluent`），但 **§6.1 的空间/模式语义必须一致**——`SpaceId{Library,Studio,Console}`、`StudioMode{Page,Batch}`、`ShellSurface{Spaces,ThemeStudio,ReaderOverlay}` 三枚举值不得变化；`ShellState` 仍为唯一状态源；不得自造第二套空间模型。
- **审查判据**：`SpaceId`/`StudioMode`/`ShellSurface` 枚举值不得变化；`ShellState` 仍是唯一状态源（不得有第二份 Selection）；共享文件由 DSH 单点提交。

### V-08b §6.3 快捷键（按方案 `:852` 立条款）

- **现行文本**：§6.3 定义**快捷键**（`Ctrl+1/2/3` 空间、`Tab` Studio 模式、`Ctrl+K` 命令面板等），由 `Shell/V2/KeyMap.cs` **单一注册表**实现，注册冲突在启动时断言失败。
- **修订文本 / 适用域**：方案 §15.2 的 §6.3 行要求「进程级单一注册表按 **scheme / 窗口 / 输入焦点上下文** 路由」。修订为：`KeyMap` 扩展为**按上下文路由**的单一注册表（`contextKey = (frontendId, windowRole, focusScope)`），但**仍为进程级唯一**；Fluent 的默认快捷键上下文与 Current 不得冲突（注册冲突仍启动断言失败）。
- **审查判据**：注册表仍唯一（不得每 frontend 一份）；`Ctrl+1/2/3` 等 §6.3 既有快捷键在两个 frontend 下映射一致；上下文路由键覆盖 `(frontendId, windowRole, focusScope)` 三元。
- **例外登记**：无需。
- **例外登记**：无需。

---

## 3. Fluent 定位（R-03 重申，防止误读）

- **Fluent = 视觉风格**，**不是** FluentAvalonia 依赖。禁止引入 `FluentAvaloniaUI` 与 **SukiUI** NuGet；所有 Fluent 观感通过 `nm.fluent.visual/1` 主题包令牌 + 既有控件模板实现。
- 「Fluent 风格」与「FluentAvalonia 库」是两个概念；审查时若发现 `FluentAvalonia` 引用即判违规（除非用户另行裁决）。

## 4. `nm.fluent.visual/1` 的定位与校验器归属

- **定位**：ThemeEngine 内的主题包 manifest（`nm.fluent.visual/1`），声明该包提供的令牌组、材质/层次/圆角例外（V-03/V-05）、与 `builtin.current-v2` 的差异清单。
- **校验器归属**：**ThemeEngine 的项目内校验器**（构建期 + 单测），不是 `tools/governance/check.ps1`。检查器只做机械治理检查，不解析主题包语义。
- **判据**：manifest 缺失或被手改 → 主题包加载失败；校验器覆盖「令牌齐全性 + 例外仅限 Fluent + 无裸值」三条。

## 5. 三处口径统一（R7-08）

| 口径来源 | 现状 | 统一后 |
|---|---|---|
| V11R §4（ThemeEngine 公开面） | 冻结的 enum/接口 | **以本修订单 V-07 为准**：不新增枚举值 |
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
