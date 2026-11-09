# FEA-14-SET-1 独立范围审查（scope-r1）

- **审查者**：DSH 派发的独立上下文子代理（fresh session；未参与 FEA 线或本卡实现/返修）
- **被审 head**：`c4e40509b`（`main`；审查开始前工作树 clean）
- **审查对象**：`doc/tasks/FEA-14-SET-1.md`（proposed 占位：FEA-14 切片 1「设置/字体面板」）
- **日期**：2026-11-10
- **性质 / 写域**：只读 scope review；仅写本文件。未改生产源码、测试、契约、卡；未 commit / push。
- **结论**：**`NEEDS_UNFREEZE`**（按卡面范围「字体选择/预览/持久化」）。若 DSH 采纳 §1.6 的窄化口径（字体面板=只读投影+预览+回退诊断，零新持久化字段），则同一份 AC/allowed_paths 可 **`READY-TO-FREEZE`**、零契约字节。

| 项 | 结果 |
|---|---|
| verdict | **NEEDS_UNFREEZE**（卡面范围）；**READY-TO-FREEZE**（窄化口径 §1.6） |
| 是否需 UNFREEZE | **是**：C-03 §2.1/§2.2/§3（持久化载体）+ C-02 V-06 或 V-07（apply 面载体，二选一，见 §1.4）；P15/C-07 零字节 |
| allowed_paths | **16 条**（§4；窄化口径，文件级精确；Variant A 的增补 delta 见 §4.2） |
| AC | **6 条**（§3，均机器判别，含负例） |
| 门禁 | `check.ps1` PASS（3 warnings）／`check.ps1 -TaskPath` PASS／`verify_pins` 18/18 PASS／`git status --short` clean |
| 能否实施 | **否**（scope 未冻结；且卡面范围需先完成 UNFREEZE 或窄化） |

---

## 1. 范围判定

### 1.1 判定结论

1. **「设置页外观字段对齐 C-03/P15」这部分不需要任何契约变更**：C-03 v6 全部字段与 P15 的 provider/network/binding 面已是既有实现（`SettingsPageView.BuildAppearanceGroup` 覆盖 `theme.*`/`appearance.*`/`motion.*`/`corners.*`/`material.*`/`layout.*`/`schemaVersion`；Provider/Network/Backup/About 组已接线），本卡在这部分最多是"补齐既有面板的字段呈现"，无契约动作。
2. **「字体选择 + 持久化」在今天的冻结面里没有任何合法载体**，必须新增契约条款：
   - 表现层唯一持久化文档 `presentation-settings.json` 的字段矩阵（C-03 §2.2）**没有 typography/font 行**；
   - Core 设置面的 `font_family` 被 `SETTINGS_SECTION_SCHEMAS` §3 明确列为「**本批不开放**：字体列表/上传需要新增 wire」，P15 G25 的「排版 / Text Style / 自动字号」同样列为不开放；
   - 字体族在设计与实现上都归属**视觉主题**（`THEME_STUDIO_SPEC` §14/§72、方案 §336/§341），Theme Studio 已实现编辑与主题包持久化。
3. **主题包路线也不构成"零契约变更"捷径**：Fluent 前端没有 Theme Studio（`FluentShellSurface` 把 `ShellCommandIds.ThemeStudio` 映射为「设置 → 外观」组，`:467`），视觉主题值域只有 `newmanga-default` / `builtin.fluent-dark` 两个内置包（C-02 V-07 双 id；`SettingsViewModel.ValidateAppearance :334-339`），因此 Fluent 用户今天**无从改字体**——这正是本卡的产品动机，但也说明"用主题包承载"要么等于把 Theme Studio 搬进 Fluent（远超本切片），要么等于新增用户级字体覆盖（回到 C-03 追加字段）。
4. **仅追加 C-03 仍不足以让覆盖生效**：`DesignSystemThemeManager.ApplyThemeLayer` 对 layer 做 `ValidateValues(..., ThemeLayerRequiredKeys, ...)` 的 59 键必需校验（`DesignSystemThemeManager.cs:307-311` + `ApplyThemeLayerCore`），**部分层的字体覆盖会被拒绝**；现有应用路径是 `ThemeService` 内部 `ThemePaletteComposer.Compose` → `ApplyThemeLayer`（`ThemeService.cs:511`/`:519`），外部无法在中途替换 3 个字体键。故 apply 面还需 C-02 的公开面条款（V-06 或 V-07）承载覆盖入口，或由 DSH 裁决一个显式的 app 侧覆盖器（后者绕层序，见 §6 R2，不推荐）。

### 1.2 事实基线（均为本 head 实测）

| # | 事实 | 证据 |
|---|---|---|
| F1 | C-03 冻结 v6，pin `b77e7968a00b…`；任何字节改动须 UNFREEZE + 重新独立复核 + 重新冻结 | `doc/plan/FEA-CONTRACT-FROZEN-C03.md:14-18`；`doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md:3` |
| F2 | C-03 §2.2 字段矩阵只含 `theme.*`/`appearance.*`/`layout.*`/`motion.*`/`material.*`/`corners.*`/`schemaVersion`，**无 typography/font** | `FEA-C03_…DRAFT.md:34-44` |
| F3 | C# 模型与之一一对应，`AppearanceSettings` 无字体字段 | `NewManga.Appearance/AppearanceSettings.cs:7-50` |
| F4 | 写侧是 canonical 白名单：只写 F2 列出的键，**未知键在下次保存时被丢弃** | `NewManga.Appearance/AppearanceJson.cs:125-165` |
| F5 | 唯一写者 = `AppearanceCoordinator.SaveAsync`（temp+replace 原子写） | `AppearanceCoordinator.cs:67-79`；`AppearanceStore.cs:65-79` |
| F6 | 字体族已有冻结 token：`Nm.FontFamily.Ui/Data/Display`，属于 theme layer 必需键 | `NewManga.DesignSystem/Generated/NmKeys.g.cs:67-69`；`DesignSystemThemeManager.cs:43-50,125-142` |
| F7 | 主题包以 `typography.ui/data/display` 携带字体族，经 `ThemePaletteComposer` 落成 token，`ThemeValidator` 校验字体栈 | `ThemePaletteComposer.cs:181-183`；`ThemePackageJson.cs:127-129`；`ThemeValidator.cs:338-340` |
| F8 | Theme Studio 已有字体选择器（系统字体列表，禁止随包字体）+ 字号缩放 80–130% 校验 | `ThemeStudioEditorViewModel.cs:144-146,195,211-212,260-290,803-810`；`THEME_STUDIO_SPEC.md:72`；`ThemeValidator.cs:35-36,342-349` |
| F9 | 设计口径：主题=性格（颜色/**字体**/圆角/材质/阴影/动效）；布局与外观独立持久化 | `THEME_STUDIO_SPEC.md:14`；方案 §336/§341（字体族属视觉主题；漫画排版字体属 Core 样式资产） |
| F10 | Core 设置面：`font_family` 本批不开放（需新增 wire）；`text.style`/`font.auto_size` 只在 G24 只读解析键集 | `doc/design/SETTINGS_SECTION_SCHEMAS.md:69,77,85,167`；`P15_SETTINGS_IPC_CONTRACT.md:248-249,288` |
| F11 | C-07 冻结 1/54/6=61；本 head 实测 `--check` EXIT=0、计数 1/54/6（+4 非方法） | `doc/plan/FEA-C07_API_INVENTORY.md:17-24`；本次运行 |
| F12 | Fluent 前端无 Theme Studio：`ShellCommandIds.ThemeStudio` → 设置/外观 | `Views/Fluent/FluentShellSurface.axaml.cs:467`；`App.axaml.cs:377-398`（Theme Studio 仅在 V2 shell） |
| F13 | `--theme-home` 同时隔离 `theme-settings.json`、`themes/`、`theme-studio-favorites.json`，`presentation-settings.json` 与之同目录 | `Services/ThemeHome.cs:19-30,72-76`；`App.axaml.cs:64-74` |
| F14 | 应用路径：`ThemeService` 内部 Compose→ApplyThemeLayer；`ApplyThemeLayer` 要求 59 必需键齐全 | `ThemeEngine/Service/ThemeService.cs:511,519`；`DesignSystemThemeManager.cs:307-311` |

### 1.3 为什么"字体选择/持久化"必须新增 C-03 条款（逐条排除）

| 候选载体 | 能否承载 | 依据 |
|---|---|---|
| C-03 `presentation-settings.json`（追加 `typography.*`） | **能，但须 UNFREEZE** | F2/F3/F4：字段矩阵与 canonical writer 都是白名单；加字段不改契约就会"写进磁盘但下次保存被丢弃" |
| P15 `settings_update_section` 的 typeset 节（`font_family`） | **否（本切片）** | F10：`font_family` 明确"本批不开放，需新增 wire"；P15 §7 排版节列为不开放；还须 Core 校验 + 新 Host 端口（C-07 变更） |
| 主题包（用户自定义主题携带字体） | **否（Fluent 不可达）** | F12：Fluent 前端无 Theme Studio；C-02 V-07 只允许两个内置视觉主题 id |
| 现有 C-03 字段 | **否** | F2：无字体字段；`layout.*` 亦无 |

### 1.4 UNFREEZE 载体与最小条款增量

**主载体（持久化）——C-03，最小增量四处：**

| 条款 | 现状 | 建议增量（供 DSH 裁决措辞） |
|---|---|---|
| C-03 §2.1 唯一写者 | 只写 appearance/material/corners/layout/motion | 明示 `typography.*` 同属该文档、同一 `AppearanceCoordinator` 写（不新增写者、不新增文件） |
| C-03 §2.2 字段矩阵 | 无字体行 | 追加 3 行：`typography.ui` / `typography.data` / `typography.display`，类型 `string \| null`；`null` = **继承当前视觉主题**（不写死默认值）；值域 = **单一字体族名**（不得是栈、不得含路径/分隔符），必须是本机已安装族；另加一行说明 `schemaVersion` 仍写 `2`，缺字段 = null |
| C-03 §2.3 适用域 | 只定义动效三态/平台读取 | 明确覆盖的**回退链**：覆盖族后追加当前视觉主题该角色的原栈尾（保证缺字体时仍可渲染，且与 F7 的 `ThemeValidator` 字体栈校验同语义） |
| C-03 §3 判据 | 5 条 | 追加第 6 条：①未安装族在保存前被拒（typed 提示，不落盘）；②`null` 保存后磁盘无该键或为 null 且主题字体生效；③旧版读取（无 typography）→ null；④覆盖层不得绕过 `ApplyThemeLayer` 的 59 键校验（见下） |

**次载体（apply 面）——C-02，二选一：**

- **方案 i（推荐，改动最小）**：C-02 V-07 追加一句——ThemeEngine 在 `Compose` 后按 settings 的 `typography.*` 替换 `Nm.FontFamily.*` 三键再交 `ApplyThemeLayer`（合成仍在同一 layer，保持 59 键齐全与原子交换）。属 ThemeEngine 内部合成行为，公开接口/enum 不变。
- **方案 ii**：C-02 V-06 追加 `DesignSystemThemeManager` 的字体覆盖入口（显式 API）。公开面变大，需同步复核 C-02 的公开面清单。

**不需要动的**：P15（零新命令/零新键域）、C-07（零新端口）、C-01b、`tools/governance/**`、18 pins 中除 C-03（及方案 ii 时的 C-02）外的 17 个。

### 1.5 切片归属冲突（须 DSH 裁决，不阻塞本报告结论）

| 来源 | 设定 |
|---|---|
| 本卡（`FEA-14-SET-1.md:3,37-44`） | 切片 1 = 设置/字体面板；Fluent 设置页 + 字体选择/预览/持久化 |
| `FEA-00` 方案 §705/§706 | `FEA-14-FONT` = 独立**漫画字体库**（家族/变体/摘要/许可，导入复制字体到库）；`FEA-14-SET` = Host 能力（托盘/退出、启动页/语言、通知/更新、快捷键冲突表、诊断预览），**不含外观/字体面板** |
| `FEA-15-INTEGRATION-ACCEPTANCE.md:28-29` | 同上，并写明 SET「**不涉 DDL/契约字节**」、FONT「需存储位置与 DDL/元数据决定」、A7 要求六切片按各自冻结 Task 验收 |

**结论**：卡面把 SET 重定义为"外观/字体设置页"，与方案/验收文档的 SET 归属不一致；而 FEA-15 `:28` 的"零契约字节"判断在本卡范围下不成立。冻结时必须二选一：①改卡面范围并保留"零契约字节"承诺（§1.6 窄化）；②保留字体持久化，则同步修正 FEA-15 `:28` 的表述并在 UNFREEZE 载体里登记。

### 1.6 可立即冻结的窄化口径（**推荐先走这条**，`READY-TO-FREEZE`）

**范围**：Fluent 设置页新增「字体」组，**只做投影与诊断，不做写入**：

1. 读取当前生效视觉主题的 `Nm.FontFamily.Ui/Data/Display` 与字号缩放/行高预设（F6/F7 已公开的 token；只读）；
2. 对每条栈做**回退解析**：逐段判断本机是否安装（`FontManager.Current` / `TryGetGlyphTypeface`），输出「实际使用族 + 缺失段列表」，全缺失则显示栈尾 generic 家族；
3. 本地**样例预览**（中文/拉丁/数字各一行），字体只设在样例控件上，**不写** `Application.Styles`/全局资源（方案 §6.3 同级约束，`THEME_STUDIO_SPEC` §72「缺字体回退链可见」）；
4. 明确文案「字体族属于视觉主题；切换主题见『外观』组」——**不放假按钮**（`SETTINGS_SECTION_SCHEMAS.md` 的假控件禁令同一纪律；且 Fluent 无 Theme Studio，F12）。

**该口径下**：零新持久化字段、零 Core/IPC 命令、零 `IHostController` 成员、零契约字节、零 pin 变化；Theme Studio 仍是字体的唯一编辑者，不会出现第二个写者。产品价值真实可测（用户能看到"为什么字形不一致/实际在用哪个字体"），且不需要任何 UNFREEZE。

### 1.7 解除 / 触发条件

- 若 DSH 决定"字体选择"必须由**设置页**提供并持久化 → 本卡 verdict 转 `NEEDS_UNFREEZE`，先按 §1.4 立 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<date>.md`）+ 独立复核 + 重冻 C-03（方案 ii 时加 C-02）+ 重算 pin，再冻结本卡。
- 若 DSH 主张"字体选择属 FEA-14-FONT（漫画字体库）"，则本卡只保留 §1.6 投影；字体库的存储位置/许可/DDL 由 FONT 切片单独冻结（`THEME_STUDIO_SPEC.md:72` 与 `extensions.md` U-5 已定：系统字体列表、**禁止随包商业字体**、上传字体 50 MB/200 个上限——均不在本卡）。

### 1.8 依赖与时序

- `depends_on: FEA-13-SRC-6` **已满足**：卡片 `status: done`、`integration_commit: ef0618e57`、`canonical_evidence_status: complete`（`doc/tasks/FEA-13-SRC-6.md:6,17-19`）。
- **文档瑕疵（交 DSH 处置）**：`doc/REBASELINE_PLAN.md:20` 仍写 `FEA-13-SRC-6 = proposed`，与卡面 done 冲突；不阻塞本卡，但冻结/激活前应更正，否则 DAG 事实与卡面不一致。

---

## 2. 实现骨架

### 2.1 目标形态（窄化口径，推荐）

```
SettingsPageView (view, 代码构建 UI)
  └─ SettingsGroupId.Typography  （新组；搜索字段 typography.ui/data/display）
       ├─ 3 × 行：token key + 主题字体栈 + 实际使用族 + 缺失段徽标
       ├─ 字号缩放/行高预设（只读值）
       ├─ 样例预览（局部 FontFamily，中/拉丁/数字）
       └─ 说明：字体族属视觉主题（无假按钮）
SettingsViewModel
  └─ ITypographySource（注入；默认 AvaloniaTypographySource）
       ├─ Read(): 从 Application resources 读 Nm.FontFamily.* + 主题缩放
       └─ IsFamilyAvailable(string): FontManager 探测
TypographyResolver（纯函数，无 Avalonia 依赖）
  └─ Resolve(stack, isAvailable) → (resolved, fallbackUsed, missing[])
```

**关键约束**：投影不写任何资源、不写磁盘、不新增端口；`TypographyResolver` 纯函数保证可在无 Avalonia 的测试里覆盖全部分支。

### 2.2 需要改的文件（精确）

| # | 文件 | 变更 | 备注 |
|---|---|---|---|
| 1 | `apps/desktop-avalonia/src/NewManga.App/Services/TypographySnapshot.cs` | 新增：`TypographySnapshot` record、`ITypographySource`、纯函数 `TypographyResolver` | 无 Avalonia 依赖（除 string/double），测试友好 |
| 2 | `apps/desktop-avalonia/src/NewManga.App/Services/AvaloniaTypographySource.cs` | 新增：资源读取 + `FontManager.Current` 探测；失败降级返回 `null`/`Unavailable` | 读 `Application.Current.Resources[NmKeys.FontFamily.*]`（只读） |
| 3 | `apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/SettingsViewModel.cs` | 加 `SettingsGroupId.Typography`、`SearchFields` 条目、`Typography` 只读投影属性、`ITypographySource?` 第 4 构造参数（可选，默认 null→不可用态） | 不碰 `SaveAppearanceAsync`/`ValidateAppearance`；`IsDirty` 语义不变 |
| 4 | `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/SettingsPageView.cs` | `RenderGroupContent` 增一支 + `BuildTypographyGroup()`；`ApplyFieldSearch`/`DisableWriteControls` 复用 | 组内**无** Button/ComboBox/TextBox/Slider（自然满足只读门禁） |
| 5 | `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/FluentShellSurface.axaml.cs` | `new SettingsViewModel(host, appearance, themeManager)` 处传入 app 侧 `AvaloniaTypographySource`（`:122`） | 组合根唯一改动点 |
| 6 | `apps/desktop-avalonia/tests/NewManga.App.Tests/TypographyResolverTests.cs` | 新增：安装/缺失/全缺失/generic 尾/空栈/含空段的解析矩阵 | 纯逻辑 |
| 7 | `apps/desktop-avalonia/tests/NewManga.App.Tests/SettingsTypographyPanelTests.cs` | 新增：组可见/搜索命中/只读态/零写盘/无全局资源突变/样例预览只作用于自身/a11y 名 | 见 §3 |
| 8 | `apps/desktop-avalonia/tests/NewManga.App.Tests/SettingsDraftSyncTests.cs`（**仅当**枚举扩展导致既有断言需更新） | 组集合断言 | 可选 |
| 9 | `doc/tasks/FEA-14-SET-1.md` | 冻结 scope（本报告的 §1.6/§3/§4） | 由 DSH 或 owner 落 |

### 2.3 若 DSH 选 Variant A（settings-owned 覆盖，需双 UNFREEZE）

在 §2.2 基础上追加：`AppearanceSettings.cs`（`TypographySettings` 记录 + 默认 null）、`AppearanceJson.cs`（读写/容错/迁移）、`SettingsViewModel`（草稿字段 + 校验 + 保存）、`SettingsPageView`（选择器 + 保存按钮）、以及 §1.4 次载体决定的 apply 改动（方案 i：`ThemeEngine/Service/ThemeService.cs` 的 Compose→替换三键；方案 ii：`DesignSystemThemeManager.cs` 新 API + `DesignSystemThemeLayerSink`）。**该变体的写域跨 ThemeEngine/DesignSystem，必须与 C-02 UNFREEZE 同批**，且需 §6 R2 的层序验证。

### 2.4 与 Theme Studio 的边界（本卡的硬边界）

| 关注点 | 归属 | 本卡行为 |
|---|---|---|
| 字体族（Ui/Data/Display）、字号缩放、行高预设 | **视觉主题**（`THEME_STUDIO_SPEC.md:14,72`；方案 §336/§341） | 只读投影；不写主题包、不调 `IThemeStudioService.ApplyAsync`/`SaveDraftAsUserThemeAsync` |
| 主题预览/应用 | Theme Studio（V2 shell；`App.axaml.cs:377-398`） | 不复制预览机制；样例预览仅局部控件 |
| 漫画排版字体/字号（Core 样式资产） | `FEA-14-FONT`（方案 §705）+ Core typeset（`SETTINGS_SECTION_SCHEMAS.md:69`，本批不开放） | out_of_scope |
| 外观（明暗/对比/跟随强调色）、布局 | C-03 / 本页「外观」组（既有） | 不改既有行为 |
| 主题包文件、`themes/` 目录 | ThemeEngine（唯一写者） | 本卡零写入（§3 AC6 负例） |

### 2.5 out_of_scope（冻结时必须写明）

- 任何字体**写入/持久化**（除非先完成 §1.4 的 UNFREEZE 并改本卡 verdict）；
- 字体库/导入/上传、随包字体、字体文件路径（`extensions.md` U-5；`SETTINGS_SECTION_SCHEMAS.md:25` 字体以族名出现）；
- 修改 `Application.Styles` 或全局字体资源（预览隔离）；
- Fluent 内新增 Theme Studio 入口/预览窗；
- C-03/C-02/P15/C-07 任何字节、pin、DDL、Core 命令面；
- 设置页"关于/Provider/Network/Backup"组的既有行为。

---

## 3. Acceptance Criteria（6 条，均可机器判别，含负例）

> 以下按 §1.6 窄化口径编写；若走 Variant A，AC1 换成"持久化+重启读回"、AC3 换成"层序/原子应用"，其余保留。

- [ ] **AC1 投影正确性（正例+退化负例）**：在注入的 `ITypographySource` 返回已知快照时，「字体」组渲染 3 行，逐行显示 token key、主题栈原文、解析后实际使用族与缩放/行高值；负例：source 返回 `null`/`Unavailable`（未初始化主题）时，组显示稳定"不可用"文案且**不抛异常、不显示伪造值**（测试断言无异常 + 文案存在 + 行数为 0 或徽标为"不可用"）。
- [ ] **AC2 回退解析（纯函数矩阵）**：`TypographyResolver.Resolve` 对 `["Missing A","Installed B","sans-serif"]` → `resolved="Installed B"`、`missing=["Missing A"]`、`fallbackUsed=true`；全缺失 → `resolved="sans-serif"`（栈尾）、`missing=2`；空栈/含空段 → 稳定结果且不抛；测试不依赖真实系统字体（fake `isAvailable`）；**负例**：不允许把"缺失"静默当真值（断言 `fallbackUsed` 为 true 而非 false）。
- [ ] **AC3 零全局副作用（负例为主）**：打开/切换/搜索「字体」组并渲染预览前后，`Application.Current.Resources[NmKeys.FontFamily.Ui/Data/Display]` 与 `Application.Current.Styles` 的引用与值不变；样例预览的 `FontFamily` 只出现在样例控件上（断言全局资源取到的仍是原对象）；`presentation-settings.json` 的 sha256+mtime 不变；**负例**：若出现任何保存按钮/写盘调用即 FAIL。
- [ ] **AC4 无 AppData 写入违规**：测试进程运行前后，真实 `%APPDATA%\NewManga` 下的 `presentation-settings.json`、`themes\` 的字节数与 mtime 均不变（复用 `StartupDiagnosticsTests.cs:27-30` 的红线口径）；使用 `--theme-home`/临时目录时只允许写该目录；cwd 下不得出现 `com.newmanga.desktop`（`StartupCompatibilityMatrixTests.cs:57` 同纪律）。负例：把 `--theme-home` 指向临时目录后，仍断言真实 AppData 零增长。
- [ ] **AC5 UI 与逻辑分离 + 只读门禁 + a11y**：`SettingsViewModel` 在无 Avalonia `Application` 的测试中可构造（fake source），断言组枚举/搜索命中（`Search="字体"` 或 `typography.ui`）/只读态；Host `WritesAllowed=false` 时组内零可写控件；3 行控件 `AutomationProperties.Name` 含 token key 与解析结果（可 Tab 落点），且不因新组破坏既有 `IsDirty`/离开确认（`HasUnsavedEdits` 不变）。
- [ ] **AC6 边界与零契约变更（机器判别）**：`git diff --name-only` ⊄ `doc/plan/**`、`doc/contracts/**`、`tools/governance/**`、`doc/tasks/FEA-13*`；`verify_pins` 18/18；`python tools/generate_api_inventory.py --check` EXIT=0 且计数 1/54/6=61（F11）；`<theme-home>/themes` 目录字节/mtime 不变；`grep` 证明未新增 `IThemeStudioService.ApplyAsync|SaveDraftAsUserThemeAsync` 调用与 `ThemePaletteComposer.Compose` 新调用点。

---

## 4. allowed_paths（16 条，文件级精确；窄化口径）

1. `doc/tasks/FEA-14-SET-1.md`
2. `doc/reviews/FEA-14-SET-1-*.md`
3. `doc/handoffs/FEA-14-SET-1-*.md`
4. `verification/FEA-14-SET-1/**`
5. `apps/desktop-avalonia/src/NewManga.App/Services/TypographySnapshot.cs`（新）
6. `apps/desktop-avalonia/src/NewManga.App/Services/AvaloniaTypographySource.cs`（新）
7. `apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/SettingsViewModel.cs`
8. `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/SettingsPageView.cs`
9. `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/FluentShellSurface.axaml.cs`
10. `apps/desktop-avalonia/tests/NewManga.App.Tests/TypographyResolverTests.cs`（新）
11. `apps/desktop-avalonia/tests/NewManga.App.Tests/SettingsTypographyPanelTests.cs`（新）
12. `apps/desktop-avalonia/tests/NewManga.App.Tests/SettingsDraftSyncTests.cs`（仅当组集合断言需更新）
13. `apps/desktop-avalonia/tests/NewManga.App.Tests/FluentResidualSettingsLeaveTests.cs`（仅当离开/脏态断言需更新）
14. `verification/FEA-14-SET-1/README.md`
15. `verification/FEA-14-SET-1/logs/**`
16. `verification/FEA-14-SET-1/screenshots/**`

> 4/14/15/16 为同一证据域，允许 14–16 与 4 重叠计数；若 DSH 需要更严，可把 4 替换为 14–16 三条。

### 4.2 Variant A（若 UNFREEZE 通过）需追加的 delta

- 契约（UNFREEZE 载体，独立于实现卡）：`doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md`、`doc/plan/FEA-CONTRACT-FROZEN-C03.md`、`doc/reviews/CONTRACT-UNFREEZE-*.md`；方案 ii 再加 `FEA-C02_V11R_AMENDMENT_DRAFT.md` + `FEA-CONTRACT-FROZEN-C02.md`。
- 实现：`NewManga.Appearance/AppearanceSettings.cs`、`NewManga.Appearance/AppearanceJson.cs`、`SettingsViewModel.cs`、`SettingsPageView.cs`、`NewManga.ThemeEngine/Service/ThemeService.cs`（方案 i）或 `NewManga.DesignSystem/Theming/DesignSystemThemeManager.cs` + `NewManga.ThemeEngine/Service/DesignSystemThemeLayerSink.cs`（方案 ii）、对应 Appearance/ThemeEngine 测试。

---

## 5. 证据计划（L2）

| # | 证据 | 判定力 | 产物 |
|---|---|---|---|
| L2-1 | **截图**：Fluent 设置 →「字体」组；浅/暗 × 1440×900、1280×800；含"已安装/缺失一段/全缺失"三态 | 视觉与回退徽标可读 | `screenshots/font-panel-*.png` + README 说明环境（Windows 版本/字体存在性） |
| L2-2 | **交互测试**：`NavSettings`/命令面板进入设置 → 选「字体」组 → 搜索"字体"→ Tab 落点/a11y 名；离开时 `HasUnsavedEdits` 不受新组影响 | 交互与 a11y 可机器断言 | `logs/dotnet-app-tests.log`（含 EXIT） |
| L2-3 | **IPC 回放**：用既有 `FakeHostController`/命令录制，断言打开字体面板期间 **0** 条 Core 命令；若实现任何写盘则断言 `presentation-settings.json` sha256 前后相同 | 证明"只读投影"非"偷偷写" | `logs/ipc-replay.log` + sha256 前后值 |
| L2-4 | **字体回退**：纯函数矩阵（fake availability）+ 1 次真实系统探测（记录 `FontManager.Current.SystemFonts` 数量与所选族，环境依赖项标注为环境相关；不可复现则 `NOT_RUN` + 原因） | 回退链与"缺字体可见"可判别 | `logs/typography-fallback.log`（EXIT + 环境头） |
| L2-5 | 门禁：`check.ps1`（默认 + `-TaskPath`）、`verify_pins`、`generate_api_inventory.py --check`、`git status --short` | 治理与零契约变更 | `logs/gates-*.log` |
| L2-6 | AppData 红线：真实 `%APPDATA%\NewManga` 前后（文件数/字节/mtime）表 | 无 AppData 违规 | `logs/appdata-redline.log` |

证据纪律：每份日志带 EXIT 与 shell/env 头（Review 模板 2026-09-19 纪律）；缺失判别力 artefact 即记 `NOT_RUN`，不得以 `N passed` 代替。

---

## 6. 风险与回退

| # | 风险 | 影响 | 处置 |
|---|---|---|---|
| R1 | **双 UNFREEZE 成本**（C-03 + C-02）：pin 重算、独立复核、重冻各一轮 | 排期拉长 | 优先采纳 §1.6 窄化（零 UNFREEZE）；确需字体覆盖则把两条 amendment 合批，一次性复核/重冻 |
| R2 | **apply 层序**：若用 app 侧"apply 后改资源"的旁路覆盖，调色板切换/主题重应用会覆盖或半覆盖 | 字体显示与设置不一致（静默失效） | Variant A 只允许"Compose 时替换三键"（方案 i）；禁止 apply 后再改全局资源（AC3 反向断言） |
| R3 | **字体许可/随包**：`extensions.md` U-5 与 `THEME_STUDIO_SPEC.md:72` 禁止随包商业字体 | 合规风险 | 只投影系统已安装族；allowed_paths 无字体文件；上传/库 = FONT 切片 |
| R4 | **canonical writer 丢弃未知键**（F4）：未来加字段后旧版本保存会抹掉新键 | 用户设置静默丢失 | 若走 Variant A，UNFREEZE 条款须写明"旧版本保存会丢弃 typography（与 material/corners 同类风险）"；或另立"未知键保真"条款（不在本卡） |
| R5 | **双字体编辑器**（设置页 vs Theme Studio） | 行为分歧、两个真值 | 本卡只读；Variant A 时须在契约里写明"设置页覆盖层 vs 主题包字体"的优先级与"主题切换不改用户覆盖" |
| R6 | 主题未初始化/headless 测试 | 面板崩溃或假值 | AC1 负例强制"不可用"降级；`AvaloniaTypographySource` 失败返回 `Unavailable` |
| R7 | Fluent 无 Theme Studio（F12），文案出现"去 Theme Studio 编辑"即假控件 | 用户被误导 | out_of_scope 明列；文案只指向「外观」组的主题切换 |
| 回退 | 实现提交 revert；窄化口径下无 schema/契约/端口变化 | 回退无残余 | 不改 pin、不改 DDL、不改 Core 面，`git revert` 即净 |

---

## 7. 门禁只读复核（本 scope review 实际执行，`c4e40509b`）

| 命令 | 结果 | 证据 |
|---|---|---|
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS**（3 persistent warnings：11 个非终态 Task；STATUS 80% 预算；REBASELINE_PLAN 80% 预算）；`Task: doc\tasks\FEA-14-SET-1.md` | `EXIT=0`（本次运行） |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-14-SET-1.md` | **PASS**（同上 3 warnings） | `EXIT=0`（本次运行） |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**（含 C03 `b77e7968a00b`、C02 `bb365ca891a7`、C07 `3fdb44e49afe`） | `EXIT=0` |
| `python tools/generate_api_inventory.py --check` | **EXIT=0**；`IReaderProgressSink 1` / `IHostController 54 (+4 非方法)` / `IRunController 6` = 61 | 本次运行 |
| `git status --short` | **clean**（审查开始时；本报告写入后新增唯一未跟踪文件 = 本文件） | 本次运行 |
| `git rev-parse --short HEAD` | `c4e40509b`；分支 `main` | 本次运行 |

> 门禁只读复核只证明"指针/字节此刻自洽"，不构成范围批准、不等于运行时验证通过。

---

## 8. 不构成什么 / 下一步

- **不构成**实现授权、不构成 scope 冻结、不构成 UNFREEZE 授权；本文件只是给 DSH 的裁决输入。
- **不构成**对卡面范围的修改（本审查只读；卡的 allowed_paths/AC 由 DSH 在冻结时落）。
- 下一步（DSH）三选一：
  1. **推荐**：采纳 §1.6 窄化，把卡面「字体选择/持久化」改为「字体投影/预览/回退诊断」，按 §3/§4 冻结 → `READY-TO-FREEZE`，无需 UNFREEZE；
  2. 需要真字体选择：先立 C-03（必要时 +C-02）UNFREEZE 载体并独立复核，再冻结本卡（`NEEDS_UNFREEZE`）；
  3. 判字体选择归 `FEA-14-FONT`：本卡只留投影，FONT 切片另冻结（存储/许可/DDL）。
- 顺带处置：`doc/REBASELINE_PLAN.md:20` 的 `FEA-13-SRC-6 = proposed` 与卡面 done 不一致（§1.8）。
