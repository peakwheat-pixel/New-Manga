# 01 设计令牌基线（Fluent v1）

**来源**：C-02 `doc/plan/FEA-C02_V11R_AMENDMENT_DRAFT.md:50-53,73-75`（已冻结的 Fluent 视觉例外定义）。
**原则**：Fluent 视觉例外**只允许**通过 C-02 定义的令牌表达；裸值（颜色/圆角/阴影/字数）仍判违规（C-02 V-05 判据①）。

---

## 1. 令牌命名空间（以 C-02 冻结为准）

| 组 | 令牌 | 类型 | 适用 | 当前代码状态 |
|---|---|---|---|---|
| 圆角（冻结组，不变） | `Nm.Corner.None` / `Nm.Corner.Sm(2)` / `Nm.Corner.Md(3)` | `CornerRadius` | 全部 | 已存在（`NmKeys.g.cs:55-57,271-278`） |
| 圆角（Fluent 扩展） | `Nm.Corner.Fluent.Sm(4)` / `.Md(6)` / `.Lg(8)` | `CornerRadius` | 仅 `builtin.fluent` frontend + `builtin.fluent-dark` 视觉主题 | **待生成**（`NmKeys.g.cs` 尚无此组；FEA-05 落 token） |
| 材质 | `Nm.Material.Acrylic.Base` / `.Tint` / `.Opacity` / `Nm.Material.Mica.Enabled` | `IBrush`/`double`/`bool` | 仅 Fluent frontend+visualTheme | 保留键，当前空（`TokenDictionaryWriter.cs:214` 注释） |
| 层次 | `Nm.Elevation.1` / `.2` / `.3` | `BoxShadows` | 仅 Fluent frontend+visualTheme | 保留键，当前空 |
| 焦点环（第四组） | C-02 V-03 定义 `Nm.Focus.Ring.Width` / `.Offset` / `.Color` | `double`/`double`/`IBrush` | 全部（两 frontend） | **当前不存在**（`NmKeys.g.cs` 无此族）；既有 `Nm.Border.Focus` 是 `Thickness` 边框宽度，**不能**替代环色——须由 FEA-05 按 C-02 生成，或由 DSH 裁决改用现有键 |

> **焦点环说明**：C-02 V-03 第四组 `Nm.Focus.Ring.Width/Offset/Color` 在当前 `NmKeys.g.cs` **不存在**；按 C-02 V-03「冻结键缺失判违规」，本基线**不**用其他键替代，登记为 **G-1c**：由 FEA-05 生成该三键（或 DSH 裁决替代方案）后，03 §3 的焦点环取值（宽 2px / 偏移 1px / 颜色 `Nm.Focus.Ring.Color`）方可生效。

> **实现前置**：`Nm.Corner.Fluent.*`、`Nm.Material.*`、`Nm.Elevation.*` 的实际生成属于 FEA-05 的实现范围（tokens 生成器）；本基线只冻结**取值与用途**。若 FEA-05 无法在 C-02 已冻结的名义下生成这些键，须先由 DSH 裁决（不得在本基线私自改名）。
>
> **尺寸/断点缺口（G-1b）**：本基线不新增尺寸/断点令牌；全部复用既有 `Nm.Size.*`（`TopBand` 36 / `TreeWidth` 200 / `FilmStripCollapsed` 56 / `FilmStripExpanded` 200 / `InspectorCollapsed` 40 / `InspectorExpanded` 320 / `RowDense` 24 / `RowNormal` 26 / `StatusBandPage` 28 / `StatusBandBatch` 24 / `ControlHeight`）与三档断点 `Nm.Size.Breakpoint.Narrow/Compact/Full`（1024/1280/1600）。任何实现需要的额外尺寸须先在 FEA-05 中登记并由 DSH 裁决，不得在本基线写裸数。**已登记的设计常量**：批量矩阵列宽最小 96（现有 `Nm.Size.*` 无列宽令牌；`TreeWidth` 200 过宽，故作为设计常量，FEA-05 生成令牌时登记）。

## 2. 取值表（Fluent v1 冻结）

### 2.1 圆角

| 令牌 | 值 | 用途（示例） |
|---|---|---|
| `Nm.Corner.Fluent.Sm` | 4 px | 输入框、芯片、小按钮、状态点容器 |
| `Nm.Corner.Fluent.Md` | 6 px | 卡片、列表行、工具按钮、浮层内容 |
| `Nm.Corner.Fluent.Lg` | 8 px | 页面级容器、对话框、抽屉、阅读器面板 |
| `Nm.Corner.None` | 0 | 图像视图、分割线、全出血区域 |

禁止：Fluent 下使用 `Nm.Corner.Sm(2)`/`Md(3)` 作为**新增**圆角（它们属于冻结组，仅 Current 与既有控件沿用）。

### 2.2 材质

| 令牌 | 值 | 说明 |
|---|---|---|
| `Nm.Material.Acrylic.Base` | `#FF1F1F1F`（深色）/ `#FFF3F3F3`（浅色） | 亚克力底色，实际模糊由 `Opacity` 与系统合成决定 |
| `Nm.Material.Acrylic.Tint` | `#33007ACC`（深）/ `#33FFFFFF`（浅） | 亚克力染色层 |
| `Nm.Material.Acrylic.Opacity` | `0.85` | 材质不透明度；`reduce` 动效下不变（材质非动效） |
| `Nm.Material.Mica.Enabled` | `true` | 是否使用 Mica 底（仅 Windows 11；不可用时降级为 `Acrylic`） |

**降级规则**：系统不支持 Mica/Acrylic（如 Win10 或远程桌面）→ 退化为不透明表面色 `Nm.Color.Bg.*`（五级表面梯），并在设置页显示「材质不可用」状态；不得留透明导致可读性下降。

### 2.3 层次（阴影）

| 令牌 | 值 | 用途 |
|---|---|---|
| `Nm.Elevation.1` | `0 1 2 0 #26000000` | 悬浮卡片、悬停行 |
| `Nm.Elevation.2` | `0 4 8 0 #33000000` | 弹出菜单、Tooltip、抽屉 |
| `Nm.Elevation.3` | `0 8 16 0 #40000000` | 对话框、模态遮罩层内容 |

`reduce` 动效下阴影**不变**（阴影不是动效）；高对比模式下阴影退化为 1px 边框（见 `03-accessibility.md` §4）。

## 3. C-02 V-05 判据①对表（每个视觉数值 → 令牌）

| 页面/组件 | 视觉属性 | 令牌 | 裸值？ |
|---|---|---|---|
| 书架卡片 | 圆角 | `Nm.Corner.Fluent.Md` | 否 |
| 书架卡片 | 阴影 | `Nm.Elevation.1` | 否 |
| 工作台面板 | 圆角 | `Nm.Corner.Fluent.Lg` | 否 |
| 工作台面板 | 材质 | `Nm.Material.Acrylic.Base` + `.Tint` + `.Opacity` | 否 |
| 工作台工具栏按钮 | 圆角 | `Nm.Corner.Fluent.Sm` | 否 |
| 阅读器图像 | 圆角 | `Nm.Corner.None` | 否 |
| 阅读器浮动工具条 | 圆角/阴影 | `Nm.Corner.Fluent.Md` / `Nm.Elevation.2` | 否 |
| 设置分组卡片 | 圆角/阴影 | `Nm.Corner.Fluent.Md` / `Nm.Elevation.1` | 否 |
| 对话框 | 圆角/阴影 | `Nm.Corner.Fluent.Lg` / `Nm.Elevation.3` | 否 |
| 全部文字/间距/颜色 | 字号/间距/前景背景 | `Nm.FontSize.*` / `Nm.Space.*` / `Nm.Color.Text.*`（既有） | 否 |

**评审规则**：XAML/代码中出现字面量颜色、`CornerRadius="6"`、`BoxShadows="..."` 即违规（除 `Nm.Corner.None` 的 0 与 `Nm.Material.*` 的初始注入值）。

## 4. 与 Current 的边界（C-02 V-05 判据②）

- `builtin.current-v2` + Current 视觉主题下：**不使用** `Nm.Material.*`/`Nm.Elevation.*`/`Nm.Corner.Fluent.*`；既有 V2 控件继续用冻结组圆角与五级表面梯。
- Fluent 令牌只在 `theme.frontendId=builtin.fluent` **且** `theme.visualThemeId=builtin.fluent-dark`（或同 frontend 的其他 Fluent 视觉主题）时生效；其他组合下出现 Fluent 令牌 → 判违规。
- Current 视觉主题下 material/corners 字段被忽略、不报错（C-03 `:73`）。

## 5. 许可边界

- 设计资产（图标/字体）不得引入 GPL-3.0 不兼容许可；随包字体只允许系统字体或 OFL/Apache-2.0 兼容字体，且须在 FEA-05 中记录。
- 本基线不引入任何第三方图标字体；图标沿用 `NmIcon` 现有集合（`NewManga.DesignSystem/NmIcon.cs`）。
