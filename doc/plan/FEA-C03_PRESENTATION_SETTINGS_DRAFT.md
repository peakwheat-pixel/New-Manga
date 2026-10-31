# FEA-C03 外观持久化与字段迁移（草案）

状态：**DRAFT / 未冻结 / 不释放实现 Task**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md) 的 C-03、[V11R_AVALONIA_CONTRACT](../plan/V11R_AVALONIA_CONTRACT.md) §4（ThemeEngine 公开面冻结）、[FEA-C02 修订单草案](FEA-C02_V11R_AMENDMENT_DRAFT.md)（V-07）、代码现状（`NewManga.ThemeEngine/Persistence/ThemeSettingsStore.cs`、`Models/ThemeModels.cs`）

**边界声明**：本文件是**草案**，不改代码、不改冻结契约、不释放实现 Task。

---

## 1. 现状（2026-11-01 代码事实）

| 项 | 现状 | 证据 |
|---|---|---|
| 持久化文件 | `%APPDATA%/NewManga/theme-settings.json`（单文件） | `ThemeSettingsStore.cs:7,64,66` |
| 写者 | `ThemeSettingsStore : IThemePersistence`（唯一实现） | `ThemeSettingsStore.cs:11,131` |
| 模型 | `ThemeSettings(ThemeId, Appearance, Contrast, LayoutProfile, ReducedMotion, FollowSystemAccent)` | `Models/ThemeModels.cs:349-355` |
| 布局 | `LayoutProfile(Id, Navigation, Shelf, Density, Workbench, Reader)`，V1 仅实现 `LayoutNavigation.TopBand` | `ThemeModels.cs:330-346` |
| 动效 | 只有 `ReducedMotion` 布尔（`ThemeMotion` 是主题包内的时长，不持久化到设置） | `ThemeModels.cs:217,353` |
| 损坏容错 | 读失败回退默认，不让损坏文件阻断启动 | `ThemeSettingsStore.cs` 注释与 `Load()` |
| 迁移 | `LegacyThemeMigration` 存在（退役主题 id 迁移） | `LegacyThemeMigration.cs` |

## 2. 目标（C-03 要冻结的）

### 2.1 唯一写者与文件

- **唯一写者**：`presentation-settings.json`（新文件）作为**外观/布局/动效**的单一写点；`ThemeSettingsStore` 降为 **sink-only**（只读，不再写）。
- **旧文件停止写的时点**：新文件**首次成功写入**后，`theme-settings.json` 转为只读（保留为迁移输入，不删除）。
- **理由**：Fluent 主题包（`builtin.fluent`）需要持久化比现有 `ThemeSettings` 更多的字段（材质强度、圆角档、密度档、动效分类），塞进旧模型会破坏 V11R §4 的冻结签名。

### 2.2 字段迁移矩阵

| 旧字段（`theme-settings.json`） | 新字段（`presentation-settings.json`） | 迁移方式 |
|---|---|---|
| `ThemeId` | `theme.packageId`（含 `builtin.current-v2` / `builtin.fluent`） | **保留**（值映射） |
| `Appearance` | `appearance.mode` | **保留** |
| `Contrast` | `appearance.contrast` | **保留** |
| `LayoutProfile.Id/Navigation/Shelf/Density/Workbench/Reader` | `layout.*` 同名 | **保留**（结构不变） |
| `ReducedMotion` | `motion.mode`（**三态**，见 §2.3） | **迁移**：`true` → `reduce`；`false` → `auto` |
| `FollowSystemAccent` | `appearance.followSystemAccent` | **保留** |
| （新增） | `material.acrylicStrength` / `material.micaEnabled` | **新增**（仅 Fluent 生效） |
| （新增） | `corners.scale`（`sm/md/lg`） | **新增**（仅 Fluent 生效） |
| （新增） | `schemaVersion` | **新增**（写入 `2`，用于迁移判定） |

### 2.3 动效三态与分类模型

- **三态**：`auto`（跟随系统）/ `full`（始终开启）/ `reduce`（始终减弱）。
- **分类模型**：动效按**用途**分 3 类，各自独立开关（`motion.categories`）：
  | 类别 | 示例 | 三态作用 |
  |---|---|---|
  | `navigation` | 页面切换、Tab 切换 | `reduce` 下改为无动画切换 |
  | `feedback` | 按钮 hover、状态变化 | `reduce` 下保留颜色变化、去掉位移 |
  | `decorative` | 背景渐变移动、粒子 | `reduce` 下**完全禁用** |
- **兼容**：旧 `ReducedMotion=true` 映射为 `motion.mode=reduce` 且三类全禁（等价旧行为）。
- **适用域**：`motion.mode=auto` 时读取系统辅助功能设置（Avalonia `PlatformSettings`）；`full`/`reduce` 为显式覆盖。

## 3. 冻结前置与判据

| 项 | 判据 |
|---|---|
| 写者唯一性 | `presentation-settings.json` 只能由 ThemeEngine 的 `PresentationSettingsStore` 写；`ThemeSettingsStore` 的 `SaveAsync` 在迁移后必须抛 `NotSupportedException`（或用 `[Obsolete(error:true)]`） |
| 迁移幂等 | 旧文件存在 → 首次读时迁移 → 写新文件 → 旧文件只读；重复启动不再写旧文件 |
| 字段完整性 | 新模型覆盖 §2.2 全部行；缺字段 → 回退默认并记录 warning |
| 三态可验证 | 单测：`reduce` 下 `decorative` 类动效时长为 0；`full` 下不受系统设置影响 |
| 与 C-02 一致 | `builtin.fluent` 主题包 id 在 `theme.packageId` 合法；`builtin.current-v2` 下 material/corners 字段被忽略（不报错） |

## 4. 待用户裁决项

| # | 问题 | 推荐 | 影响 |
|---|---|---|---|
| **U-05a** | 首阶段是否纳入动效三态与分类（而不是只有 `ReducedMotion` 布尔）？ | **是**（三态 + 三类，等价旧行为的迁移路径已给出） | 若否，Fluent 的动效分级无法表达 |
| U-05b | 旧 `theme-settings.json` 是否在迁移后删除？ | **否**（转只读保留） | 删除会丢回退输入；保留成本极低 |

## 5. 与现役/冻结契约的关系

- 本草案**不改** V11R §4 的公开面（`ThemeKind`/接口签名不变）；新增的 `PresentationSettingsStore` 属 ThemeEngine 内部实现，公开面由 C-02 V-07 约束。
- 与 C-01b 无交叉（存储契约不涉及外观设置文件）。
- 与 C-02 联动：`builtin.fluent` 的材质/圆角/动效字段由本文件定义持久化形态，视觉例外由 C-02 V-05 定义。

## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案：现状表（代码事实）、目标文件与唯一写者、字段迁移矩阵 10 行、动效三态/三类、5 条判据、U-05a/U-05b 待裁决 | DSH |
