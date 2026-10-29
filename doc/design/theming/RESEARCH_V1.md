# V11R-C-RESEARCH-1：Avalonia 主题框架参考研究 v1

状态：`ACCEPTED`（2026-10-30，DSH）。任务卡：`doc/tasks/V11R-C-RESEARCH-1.md`。
用途：为新 `NewManga.ThemeEngine` 与 Theme Studio 提供「可借鉴 / 可复用 / 必须自研」的裁决依据；**不是**选型投票。

## 0. 结论先行（裁决 R-03）

1. **V1 不引入任何第三方 UI/主题框架依赖**。新主题引擎建立在 Avalonia 原生原语上：`ThemeVariant` + `ResourceDictionary.ThemeDictionaries` + `ControlTheme` + `DynamicResource`。理由见 §4。
2. 5 个上游项目全部 **MIT** 许可，与 GPL-3.0 分发的产品兼容（MIT 为 GPL 兼容的宽松许可，保留版权与许可声明即可）。许可证**不构成**采用障碍，真正的障碍是「视觉语言冲突 + 维护面」。
3. 借鉴对象（读代码/文档，不引依赖）：
   - **Avalonia 原生**：`ThemeVariant`/`ThemeDictionaries` 是唯一必须在用的机制；SukiUI / Semi / FluentAvalonia / PleasantUI 的动态切换本质都是它的封装。
   - **Semi.Avalonia**：令牌化资源覆盖模型（通过覆盖 `DynamicResource` 颜色资源做自定义）+ 设计语言到令牌的映射方法。
   - **SukiUI**：主题注册/切换的 API 形态（`SukiTheme` 单例 + 颜色主题集合 + 背景风格），以及对话框/通知宿主（DialogHost/Toast 宿主）的组织方式。
   - **FluentAvalonia**：WinUI 控件语义（InfoBar→我们的 AlertBanner、ContentDialog→Modal、NavigationView→我们不做）；只作交互语义参考。
   - **PleasantUI**：小体量控制库的组织结构（控件 + 主题同仓）参考；社区活跃度低，不作为依赖。

## 1. 事实表（GitHub API 实测 2026-10-30）

| 项目 | SPDX | Stars | Forks | Open issues | 最近 push | 创建 | 语言 |
|---|---|---|---|---|---|---|---|
| [AvaloniaUI/Avalonia](https://github.com/AvaloniaUI/Avalonia) | MIT | 31728 | 2871 | 1941 | 2026-10-29 | 2013-12 | C# |
| [kikipoulet/SukiUI](https://github.com/kikipoulet/SukiUI) | MIT | 2697 | 283 | 38 | 2026-10-28 | 2022-03 | C# |
| [irihitech/Semi.Avalonia](https://github.com/irihitech/Semi.Avalonia) | MIT | 1964 | 166 | 33 | 2026-10-26 | 2022-11 | C# |
| [amwx/FluentAvalonia](https://github.com/amwx/FluentAvalonia) | MIT | 1619 | 170 | 43 | 2026-08-22 | 2020-05 | C# |
| [Onebeld/PleasantUI](https://github.com/Onebeld/PleasantUI) | MIT | 81 | 5 | 0 | 2026-08-01 | 2023-05 | C# |

> 数据来源：GitHub REST `GET /repos/{owner}/{repo}`，2026-10-30 采集。Star/issue 数为快照，用于活跃度判断，不作为质量结论。

## 2. 逐项目评估

### 2.1 Avalonia（平台本体，必须在用）

- **主题机制**：`ThemeVariant`（Light/Dark/自定义）+ `ResourceDictionary.ThemeDictionaries` + `Application.RequestedThemeVariant`；`DynamicResource` 实现运行时替换；`ControlTheme` 替代旧 `Style` 作为控件模板主体；`Styles` 用于类选择器与附加行为。官方文档：<https://v11.docs.avaloniaui.net/zh-Hans/docs/guides/styles-and-resources/how-to-use-theme-variants/>。
- **对 V11R 的意义**：我们的契约（`Nm.*` 资源键 + 替换字典 + 不重建窗口）**就是** Avalonia 原生机制的正确用法；不需要额外框架即可实现「全局实时切换/深浅/系统跟随」。
- **版本**：产品用 11.3.22（`Directory.Build.props` `AvaloniaVersion`）。
- **结论**：唯一硬依赖。

### 2.2 SukiUI（MIT，活跃）

- **架构（文档级，UNVERIFIED_IN_CODE）**：以 `SukiTheme` 为中心的单例主题管理：注册颜色主题（ColorTheme）集合、背景风格（BackgroundStyle，如 mica/acrylic）、`SukiTheme.ChangeTheme(...)` 运行时切换；自带控件样式与 `DialogHost`/`Toast` 宿主。
- **优点**：切换 API 简洁；背景材质与对话框宿主对桌面应用体验好。
- **与本项目冲突**：视觉语言（大圆角、材质、彩色主题）与冻结的 A+C 设计（≤3px 圆角、无阴影/无模糊/无渐变、琥珀强调 + 七态状态）**根本冲突**；引入即意味着与设计系统 §9「反面清单」直接对撞。
- **借鉴**：主题注册表 + 预览/提交的 API 形态；BackgroundStyle 概念改造为我们的 `Surface.Material`（Solid/None；**不得**使用 Mica/Acrylic 破坏「无模糊」约束 —— 旧项目 macOS 主题曾用过 Mica，新系统明确不做）。
- **结论**：不引入依赖；借鉴 API 形态。

### 2.3 FluentAvalonia（MIT，维护中，节奏较慢）

- **架构（文档级，UNVERIFIED_IN_CODE）**：把 WinUI/Fluent 控件（NavigationView、InfoBar、ContentDialog、SettingsExpander 等）与 Fluent 资源带入 Avalonia，依赖原生 `ThemeVariant` 做深浅。
- **优点**：Windows 原生观感与无障碍基线可靠；控件语义成熟。
- **冲突**：Fluent 视觉（阴影、圆角、动效、字体度量）与我们冻结设计不同；其资源键大量是 `System*`/`Fluent*`，与 `Nm.*` 并存会造成**两套令牌真值**（违反 DESIGN_SYSTEM §0 唯一权威）。
- **借鉴**：InfoBar→`AlertBanner`；ContentDialog→`Modal`；SettingsExpander→Console 分区折叠交互；焦点与键盘规范。
- **结论**：不引入依赖；仅作交互语义参考。

### 2.4 Semi.Avalonia（MIT，活跃）

- **架构（文档级，UNVERIFIED_IN_CODE）**：Semi Design 令牌 → Avalonia 资源的映射；通过覆盖 `DynamicResource` 颜色资源实现换肤（官方文档：<https://docs.irihi.tech/semi/en/docs/advanced/resource-customization/>），控件样式与令牌解耦，支持 light/dark。
- **优点**：与我们「令牌 → 资源键 → 动态替换」的架构**同构**；是「令牌化主题」最接近的参考实现。
- **冲突**：Semi 设计语言与 A+C 不同；其令牌命名与 `Nm.*` 不兼容，且引入会把第三方控件模板带进产品。
- **借鉴**：令牌→资源字典的生成方式、资源覆盖/自定义的边界、控件样式与令牌解耦的组织方式。**这是新 Theme Engine 的主要参考。**
- **结论**：不引入依赖；作为 Theme Engine 架构的主要参照。

### 2.5 PleasantUI（MIT，活跃度低）

- **架构**：自有控件库 + 主题管理，体量小；社区 81 stars、0 open issues（可能 issues 关闭或未使用）。
- **结论**：不引入；组织结构仅供小体量参考。维护风险最高。

## 3. 对比矩阵

| 维度 | Avalonia 原生 | SukiUI | FluentAvalonia | Semi.Avalonia | PleasantUI |
|---|---|---|---|---|---|
| 主题架构 | ThemeVariant + 资源字典（原语） | SukiTheme 单例封装 | Fluent 资源体系 | 令牌→资源映射 | 自有主题管理 |
| 实时切换 | 原生支持（DynamicResource） | 支持 | 支持 | 支持 | 支持 |
| 高低对比度 | 需自建（我们做） | 无 | 部分（系统） | 有限 | 无 |
| 控件一致性 | 需自建样式 | 强（其自身风格） | 强（Fluent） | 强（Semi） | 中 |
| 个性化（用户自定义主题） | 需自建 | 颜色主题集合 | 有限 | 令牌覆盖 | 有限 |
| 与冻结 A+C 设计兼容 | ✅（我们用原语） | ❌ 视觉冲突 | ❌ 视觉冲突 | ⚠️ 架构同构、视觉冲突 | ❌ |
| 许可证 | MIT | MIT | MIT | MIT | MIT |
| 维护成本 | 自研但可控 | 引入+覆盖=双份维护 | 引入+覆盖=双份维护 | 引入+覆盖=双份维护 | 高风险 |
| GPL-3.0 分发兼容 | ✅ | ✅ | ✅ | ✅ | ✅ |

## 4. 为什么不「拼装」第三方框架（对应用户 C1 禁令）

1. **单一令牌真值**：引入任一家即引入其资源键体系，与 `Nm.*` 并存会让「组件颜色从哪来」出现第二答案（DESIGN_SYSTEM §0 明令禁止）。
2. **视觉反向清单**：四家默认样式都含阴影/圆角/材质/动效，与 DESIGN_SYSTEM §9 的 10 条反面清单冲突，覆盖成本高于自研。
3. **发布面与体积**：产品为单文件自包含发布（约 29MB 基线），第三方控件库增加 trimming 风险与打包体积。
4. **可恢复性**：自研引擎的 10 个子系统（注册/解析/校验/持久化/回退）都在我们控制内，故障可回退默认主题；引入框架后故障面跨库。
5. **真实收益点**：四家真正值得借鉴的只有「令牌→资源映射」「切换 API 形态」「对话框/通知宿主组织」三点，均可低成本自研实现。

## 5. 对新 Theme Engine 的映射建议（供 V11R-C-1 实施）

| 契约能力 | 采用机制 | 备注 |
|---|---|---|
| Semantic Tokens | `ResourceDictionary` + C# 键常量 | 生成器从 `tokens.json` 产出，单一来源 |
| Theme Registry | 内置主题（嵌入资源）+ 用户主题（`%APPDATA%/NewManga/themes/*.json`） | SukiUI 的注册表形态可借鉴 |
| Package Schema | `newmanga.theme/1` JSON（契约 §4） | 校验器独立，schema 版本显式 |
| Resource Resolver | `ThemeVariant` + `ThemeDictionaries` + 字典替换 | 原生机制，不重建窗口 |
| State Manager | `IThemeService` 单例（DI），事件 `Changed` | 参照 SukiTheme 的 API 简洁性 |
| Persistence | JSON 设置文件 + 旧 ID 迁移映射 | 失败回退默认，不阻塞启动 |
| Preview Engine | 临时字典叠加 + 会话提交/回滚 | 不触碰主视觉树结构 |
| Import/Export | `.nmtheme`（JSON）流式读写 + 校验 | 参照 Semi 的资源覆盖边界 |
| Validation | 独立 `IThemeValidator`（必填键/对比度/非法值） | 对比度用 WCAG 公式实测 |
| Fallback/Recovery | 逐键回退默认 + 整包回退 | 任一步失败不得抛到启动路径 |

## 6. 取证与局限

- 已验证：仓库元数据（许可证/活跃度/规模）来自 GitHub API；Avalonia 主题机制来自官方文档。
- 未验证（`UNVERIFIED_IN_CODE`）：SukiUI/FluentAvalonia/Semi/PleasantUI 的内部实现细节（未逐仓读源码）。若后续需要「复用某具体实现」，必须在该任务内补代码级核实并记录，不得以本文档替代。
- 本文件不构成法律意见；MIT 与 GPL-3.0 的兼容结论为通用的宽松许可兼容判断，发布前由 Release Owner 复核 `THIRD_PARTY_LICENSES.md`。
