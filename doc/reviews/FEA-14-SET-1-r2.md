---
task_id: FEA-14-SET-1
reviewer: fresh 独立上下文子 agent（由 Lead 派发）
reviewer_kind: subagent
author: dsh
base_commit: c4e40509b
reviewed_head: caee4c86a
decision: changes_requested
---

# Review：FEA-14-SET-1（设置页「字体」组只读投影，r2）

## 0. 审查对象、环境与写域

- 被审 head：**`caee4c86a`**（`main`）；base：`c4e40509b`；提交链 `64c32fa47`（首版 + 证据）→ `a0e59ac3b`（r1 处置：R-001/R-002/R-007/R-009/R-014）→ `caee4c86a`（r1 P2 判别力：R-003/R-004/R-005/R-006/R-008）。
- 环境事实：
  - 审查开始（约 `2026-11-10T08:30+08:00`）与结束（`2026-11-10T08:46:41+08:00`）两次实测：`git rev-parse HEAD` = `caee4c86a…`，`git status --short` 均 **clean**；审查期间主树无新提交、无未提交改动。
  - `git worktree list` 显示 Lead 的 `FEA-14-SET-1-p3` worktree 在 `4b8f2831c`（detached），与主树隔离，不影响本次判定。
- 写域：**仅写本文件**（`doc/reviews/FEA-14-SET-1-r2.md`）。未改生产源码/测试/卡/契约/证据，未 commit/push/reset/stash。临时验证程序与日志只写在仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-SET-1-r2\`，未污染仓库。
- 依据：`doc/tasks/FEA-14-SET-1.md`（6 AC、16 allowed_paths、窄化口径）、`doc/reviews/FEA-14-SET-1-scope-r1.md` §1.6/§3/§5、`doc/reviews/FEA-14-SET-1-r1.md`（R-001…R-015）；代码事实以 `git show caee4c86a:<path>` 为准。
- 方法：只读 diff/代码 + **独立实测探针**（headless Avalonia 载入真实 `NewManga.App.App` 资源栈 + `FontFamily`/`FamilyNames` 行为 + locale 行为）+ 定向/全量测试 + 治理门禁；未把静态推演写成实测，静态推演均显式标注。

## 1. 结论

**`changes_requested`。**

| 计数 | 值 | 说明 |
|---|---|---|
| P0 | **0** | 未见数据损坏、伪造证据或契约/安全越界 |
| P1 | **1** | r1 **R-002（P1）未完全关闭**：生产读取已生效且经本审查实测，但 r1 明确指出的「测试只证明参数透传」未被修复；且该修复新引入 culture 依赖与 face→size 映射两处缺陷（见 R2-002/R2-003） |
| P2 | **6** | R2-002…R2-007（含 AC6 冻结写域越界、R-003/R-004/R-005 判别力仍不足、R-007 可追溯性） |
| P3 | **4** | R2-008…R2-011（证据未刷新、R-012/R-006/R-009/R-014/R-015 残余） |

一句话：**R-001 与 R-008 真实关闭**（其中 R-001 经真实 `FontFamily` 资源实测）；**R-002 仅 PARTIAL**；**R-003/R-004/R-005/R-007 均只到 PARTIAL**，README/卡面仍有高于判别力的 PASS/MET 声明；`caee4c86a` 新增的渲染测试文件不在冻结 `allowed_paths` 内，使卡面 AC6「diff ⊆ 16 paths」不再成立。另有 2 个由本轮修复引入的产品侧缺陷（locale 下丢行高、Data/Display 缩放 token 错配）。按「P0/P1 未关闭 → changes_requested」纪律不能批准。

## 2. r1 findings 逐项判定

| r1 ID | r1 级别 | 判定 | 依据（本审查实测/代码位置） | 说明 |
|---|---|---|---|---|
| R-001 | P1 | **CLOSED** | `TypographySnapshot.cs:157-162`；探针 `fontprobe2.log` Part1/Part2 | `FamilyNames.ToString()` 实测 = `"Segoe UI Variable Text, Microsoft YaHei UI, Noto Sans SC"`（完整栈，非首族）；真实 `Application.Resources`（合并字典）中 `Nm.FontFamily.Ui/Data/Display` 为 `FontFamily`，`Read()` 的 `StackRaw` = 完整栈。**缺回归测试**（无真实 `FontFamily` 输入的 source 测试），但产品缺陷已由本审查独立实测关闭 |
| R-002 | P1 | **PARTIAL** | `TypographySnapshot.cs:107-148`；探针 Part2；新缺陷 R2-002/R2-003 | 生产读取已生效（真实资源下 scale=13/18、lineHeight=1.45/1.25，见探针）；但**无 `AvaloniaTypographySource` 真实路径测试**（`rg AvaloniaTypographySource tests` 0 命中，r1 所述「只证明参数透传」未改），且修复引入 locale 缺陷与 token 映射错位（见 R2-002/R2-003，本行 P1 状态见 R2-001） |
| R-003 | P2 | **PARTIAL** | `SettingsTypographyRenderTests.cs:45-67`；README:12 | 已构造 `SettingsPageView` 并断言 3 个 token 字符串/resolved/missing/「视觉主题」；但未断言「恰好 3 行」、未断言占位态渲染、未断言样例 3 行及样例字体；README 的 AC1 PASS 未更新引用新测试 |
| R-004 | P2 | **PARTIAL** | `SettingsTypographyRenderTests.cs:69-89`；探针 Part2（`Resources.Count=0`） | 新增「资源/Styles 不变」测试，但 `Assert.Equal(resourcesBefore, application.Resources.Count)` 在真实测试 App 中是 **0==0 恒真**（`App.axaml` 的 token 全在 `MergedDictionaries`，直接条目为 0）；`Assert.Same(application, Application.Current)` 亦恒真；未断言 `Nm.FontFamily.*` 三资源的引用/值不变、未断言样例字体不外溢 |
| R-005 | P2 | **PARTIAL** | `SettingsTypographyPanelTests.cs:91-119`；实测 `%APPDATA%\NewManga` | 指纹已补 sha256+mtime（真实改进）；但 AC4 指定的 `presentation-settings.json`/`themes\` 在本机**不存在**（目录内仅 `theme-settings.json`，359 B，mtime `2026-10-30T03:00:27Z`，全量测试后未变），两 artefact 断言仍空转；无负例（临时 `--theme-home` 后仍断言真实 AppData 零增长）、无基线日志 |
| R-006 | P2 | **PARTIAL** | `SettingsPageView.cs:616-622`；`FluentComponents.cs:107`；README:16 | a11y 名已含 token key + 解析族（`文案 实际使用 X`，真实改进）；但 `SettingsField : Grid` 非 Tab 落点、无 a11y 断言测试、无 `WritesAllowed=false` 视图测试 |
| R-007 | P2 | **PARTIAL** | `TypographySnapshot.cs:78-81`；`TypographyResolverTests.cs:24-25`；`TypographySnapshot.cs:12` | 语义已改为 scope §3 AC2 口径（首族缺失但后续命中 → `Fallback=true`），实现/测试/卡面「fallback 标记正确」/scope 原文四者**语义一致**；但无文档级裁决记录（只有代码/测试注释引「DSH ruling 2026-11-10」），且 `TypographyLine.Fallback` 的 XML doc 仍写「True when the stack degraded to its generic tail」，与新语义矛盾 |
| R-008 | P2 | **CLOSED** | `SettingsPageView.cs:329-336`；`SettingsTypographyRenderTests.cs:91-108`；门禁 1 实测 35/35 | `Search="字体"` 命中后跳过组内字段过滤，投影行保持可见；渲染测试断言 `visibleRows > 0`（旧代码在构造期即过滤掉全部行，会失败——静态推演，依据 `caee4c86a^` 的 `RenderGroupContent`）；`typography.ui` 命中走同一分支（由 skip 条件保证） |
| R-009 | P2 | **PARTIAL** | `doc/STATUS.md:7`；`doc/REBASELINE_PLAN.md:51-52` | STATUS/PLAN 文案已改为「字体组已落；r1 处置中」，但 PLAN 的 `FEA-14-SET-1` 裸行仍是悬在「READY 节点：无」之后、未并入 DAG 表（结构问题未处置） |
| R-010 | P3 | **PARTIAL** | `TypographySnapshot.cs:107-137` | 已删除死变量 `missingTokens`；但「只有 1–2 个 token」时仍 `Available=true` + 少于 3 行，UI 无部分缺失提示，仍无测试 |
| R-011 | P3 | **CLOSED** | `TypographySnapshot.cs:81` | `fallback` 现为「至少一段缺失或无 resolved」，仅 generic 栈（0 缺失）不再误置 true；无对应单测（建议补，非阻断） |
| R-012 | P3 | **OPEN** | `FluentShellSurface.axaml.cs:122`；`SettingsViewModel.cs:86-87` | 组合根仍未注入 `AvaloniaTypographySource`（3 参构造）；`TypographySnapshot` 每次属性访问 `new AvaloniaTypographySource().Read()`，组渲染至少 4 次同步全量探测 |
| R-013 | P3 | **OPEN** | `verification/FEA-14-SET-1/**` | 证据目录未在 `a0e59ac3b`/`caee4c86a` 后刷新（见 §6） |
| R-014 | P3 | **PARTIAL** | `doc/tasks/FEA-14-SET-1.md:86-112` | 卡面仍保留「第一切片占位」「预估范围（待 scope review）」与 Resource Manifest「未访问真实数据」/Closeout「未开始」；仅替换了重复 AC 段一行 |
| R-015 | P3 | **OPEN** | `SettingsPageView.cs:627-641`（重复赋值 `:636`） | 3 行样例仍全部套用 Ui 面（首行）字体、Data/Display 面无独立样例；`FluentUi.Text(sample,…)` 后 `text.Text = sample` 重复赋值仍在 |

> 判定纪律说明：R-001 的「建议补真实 `FontFamily` 测试」未落实，但本审查以真实 App 资源栈实测了同一转换，故按产品缺陷判 CLOSED、测试缺口另记 P3 建议；R-002 因 r1 明确把「测试只证明参数透传」列入 finding（证据列），故不能判 CLOSED。

## 3. R2 Findings（本报告新发现/残余）

| ID | 级别 | 位置 | 事实与影响 | 证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R2-001 | **P1** | `apps/desktop-avalonia/src/NewManga.App/Services/TypographySnapshot.cs:107-148`；`tests/NewManga.App.Tests/TypographyResolverTests.cs:53-60` | **r1 R-002（P1）未完全关闭**：生产读取已实现并经实测可用（真实 App 资源下三行 scale/lineHeight 正确），但 r1 指出的「`ScaleAndLineHeightAreCarriedThroughUntouched` 只证明参数透传，不是投影证据」未修复——测试目录无任何 `AvaloniaTypographySource`/真实 `ResourceDictionary` 覆盖；且本次修复新增 R2-002（locale 丢行高）与 R2-003（face→size 错配）两个产品侧缺陷。影响：AC1 的「缩放/行高」无回归保护，且在部分环境/两行上给出错误或缺失值 | 代码 `TypographySnapshot.cs:107-148`；`rg AvaloniaTypographySource apps/desktop-avalonia/tests` 0 命中；门禁 1 的 35 条测试中无 source 测试；探针 `fontprobe2.log` | 改 `_resourceLookup` 为 typed（`Func<string, object?>`）或直接读资源；补一条 headless 真实资源测试：放入 `FontFamily` 三栈 + `double` 三组 `Nm.FontSize.*`/`Nm.LineHeight.*` → 断言 `Read()` 三行/StackRaw/scale/lineHeight；修复 R2-002/R2-003 | open |
| R2-002 | **P2** | `TypographySnapshot.cs:139-148`（`ReadNumber`）与 `:150-163`（`DefaultLookup` 的 `_ => value.ToString()`） | **locale 依赖缺陷（本轮修复引入）**：`DefaultLookup` 用 `value.ToString()`（`CurrentCulture`）把 `double` 转字符串，`ReadNumber` 又用 `InvariantCulture` 解析。实测把 `CurrentCulture` 置 `de-DE` 后，真实资源栈下 3 行 `lineHeight` 全部变 `null`（1.45→"1,45" 解析失败）；若主题 scale 产生小数，`Scale` 同样丢失。影响：逗号小数分隔 locale 下 AC1 的「行高」显示「—」，投影静默缺失 | 探针 `fontprobe2.log` Part2 `de-DE` 段；`TypographySnapshot.cs:143-147`、`:161` | `DefaultLookup` 对 `double` 用 `Convert.ToString(value, CultureInfo.InvariantCulture)`（或直接返回 typed 值，见 R2-001）；补 culture-scoped 测试（`CultureInfo.CurrentCulture` 临时切换后断言非 null） | open |
| R2-003 | **P2** | `TypographySnapshot.cs:110-115` vs `NewManga.ThemeEngine/Generated/ThemeTokenBaseline.g.cs:47-55` | **face→size token 映射与设计系统 tier 表不一致（本轮修复引入）**：`LineHeightTiers` 定义 `Display ↔ Nm.FontSize.Xxl`（24）、`Data ↔ Nm.FontSize.Sm`（12）；实现投影 Data 用 `Nm.FontSize.Md`（13）、Display 用 `Nm.FontSize.Xl`（18）。影响：Data/Display 两行「缩放」值错误（13/18 而非 12/24；主题 scale 后偏差放大），与 `Nm.TextLineBox.*` 派生口径不一致，属静默错误值 | `TypographySnapshot.cs:112-114`；`ThemeTokenBaseline.g.cs:49,54`；`DesignSystemThemeManager.cs:537-545` 的 LineBox 派生表；探针 Part2 显示 Display=18 | 按 tier 表改 `Nm.FontSize.Sm`/`Nm.FontSize.Xxl`；若 DSH 有意采用另一配对，须在卡面/裁决记录写明理由并加测试；补三行 scale 断言 | open |
| R2-004 | **P2** | `apps/desktop-avalonia/tests/NewManga.App.Tests/SettingsTypographyRenderTests.cs`（新文件，109 行）；卡 `doc/tasks/FEA-14-SET-1.md:21-37,69`；README:17 | **AC6/冻结写域越界**：该新测试文件不在卡面 16 条 `allowed_paths` 内（scope §4 为「文件级精确」），`git diff --name-only c4e40509b caee4c86a` = **19 个文件**，其中 18 在 allowed 内、1 个 OUT；卡面 AC6 仍标 `<<MET>>`「diff ⊆ 16 paths」、README AC6 仍 PASS。影响：AC6 声明不成立、冻结写域被扩大（未触契约/pins，无产品功能影响） | 命令实测（见 §5 范围与越界）；`git diff --name-status c4e40509b caee4c86a` = 19 行；卡 `:69` | DSH 二选一：①把该文件显式加入 `allowed_paths` 并留授权痕迹；②把 3 个渲染测试并入 allowed 的 `SettingsTypographyPanelTests.cs`。同步把卡面 AC6/README 改为当前事实 | open |
| R2-005 | **P2** | `SettingsTypographyRenderTests.cs:69-89` | **AC3 资源不变断言仍缺判别力**：探针实测真实测试 App `Application.Resources.Count == 0`（App.axaml 的 token 全在 `MergedDictionaries`），故 `Assert.Equal(resourcesBefore, Count)` 是 0==0 恒真；`Assert.Same(application, Application.Current)` 恒真；Styles 仅比 `GetHashCode` 列表（3 项，弱）。未保存/比较 `Nm.FontFamily.Ui/Data/Display` 的资源引用或值，未验证「样例字体不外溢」。影响：AC3 的核心风险（组渲染覆写全局字体资源 / 样例字体写回全局）仍不可检测 | 探针 `fontprobe2.log` Part2 `Resources.Count=0 MergedDictionaries=3 Styles=3`；测试代码 `:74,86-88`；`App.axaml`（资源仅 MergedDictionaries） | 在 headless 测试中 `TryGetResource` 保存三字体资源引用后 `Assert.Same`；断言样例 `TextBlock.FontFamily` 只出现在样例行且资源值未变；做不到则按 AC 口径把 AC3 降级并记 NOT_RUN | open |
| R2-006 | **P2** | `SettingsTypographyPanelTests.cs:91-119` | **AC4 指定 artefact 仍空转**：指纹已含 sha256+mtime（改进属实），但本机 `%APPDATA%\NewManga` 只有 `theme-settings.json`；`presentation-settings.json`/`themes\` 不存在，AC4 指定的两个对象无断言对象；未准备 artefact、无负例、无基线日志。影响：AC4 PASS 仍高于判别力（对指定 artefact 而言是空转断言） | 实测 `Get-ChildItem %APPDATA%\NewManga -Recurse`（仅 359 B `theme-settings.json`，mtime 2026-10-30T03:00:27Z，审查前后不变）；测试 `:104-119` | 准备/创建两个 artefact 后做 sha256+mtime 前后断言并落 `logs/appdata-redline.log`；或补 `--theme-home` 临时目录负例；否则 AC4 记 NOT_RUN/降级 | open |
| R2-007 | P2 | `SettingsTypographyRenderTests.cs:45-67`；README:12 | **R-003 的渲染断言不完整、README 未刷新**：只断言 3 个 token 字符串出现 / resolved / missing / 文案；未断言「恰好 3 个投影行」、未渲染未初始化占位分支、未断言样例 3 行及样例字体、未断言缩放/行高文本；README 仍把 AC1 PASS 归因于 `TypographyResolverTests`+`SettingsTypographyPanelTests`，未引用新渲染测试。影响：AC1 渲染正确性的判别力仍不完整，且证据说明与代码不一致 | 测试 `:45-67`；README `:12`（mtime 仍为 64c32fa47 时点） | 断言投影 `SettingsField` 数量=3（或排除样例后=3）+ 占位分支渲染文案 + 样例 3 行/字体只设样例；README 刷新引用 | open |
| R2-008 | P3 | `TypographySnapshot.cs:78-81,12`；`TypographyResolverTests.cs:24-25`；`doc/` | **R-007 裁决不可追溯 + 字段 doc 过时**：代码/测试注释引「DSH ruling (2026-11-10)」，但仓库无对应裁决/处置记录（`doc/reviews` / `doc/handoffs` / `doc/tasks` 内无 R-007 裁决文本；本轮提交仅代码+1 行卡面）；`TypographyLine.Fallback` XML doc 仍写 generic-tail 语义，与新实现矛盾；README「实现要点」也未更新 fallback 定义 | `rg R-007/fallback doc/**` 无裁决记录；`TypographySnapshot.cs:12`；`README.md:39` | 在卡面「r1 处置」或独立处置记录中落裁决原文（fallback = 至少一段缺失）；更新 XML doc 与 README 实现要点 | open |
| R2-009 | P3 | `verification/FEA-14-SET-1/**`；README:23-24,44-46 | **证据未刷新/缺项**：全部证据文件 mtime = 2026-11-09T18:3x UTC（= 2026-11-10 02:3x +08，即 `64c32fa47` 时点）；README/logs 记「定向 11 / 全量 849/0/11」，head 实测为「定向 35 / 全量 852/0/11」；scope §5 的 `typography-fallback.log`、`appdata-redline.log`、`ipc-replay.log`、API inventory/`grep` 证明缺失，README 只把截图记 NOT_RUN | 文件 mtime 清单；门禁实测（§4）；scope §5 L2-3/L2-4/L2-6；`README.md:44-46` | 在最终 head 重跑并覆盖日志（保留时间/EXIT 头），补缺失 artefact 或统一记 NOT_RUN；不要以旧日志支撑新 head 的 PASS | open |
| R2-010 | P3 | `FluentShellSurface.axaml.cs:122`；`SettingsViewModel.cs:86-87` | **R-012（P3）遗留未处置**：组合根仍以 3 参构造 `SettingsViewModel`，未注入 `AvaloniaTypographySource`；每访问一次投影属性就新建 source 并 `Read()`（组渲染 ≥4 次；每次 3 个资源读取 + 3 行×逐段 `TryGetGlyphTypeface` + 6 个数值读取），全在 UI 线程同步执行，且同一渲染内多次结果可能不一致 | 代码位置；`rg "new SettingsViewModel("` = `MainWindow.axaml.cs:69`（无参）与 `FluentShellSurface.axaml.cs:122`（3 参） | 组合根注入 app 侧 source + 每轮渲染缓存一次 snapshot（组切换/刷新时重读） | open |
| R2-011 | P3 | 见右列 | **其他 r1 残余**：①R-006：a11y 名已改进但无断言、`SettingsField:Grid` 非 Tab 落点、无只读 Host 视图测试；②R-009：`REBASELINE_PLAN.md:51-52` 的 SET-1 行仍未并入 DAG 表；③R-014：卡 `:86`「第一切片占位」、`:88-95`「预估范围（待 scope review）」、Resource Manifest/Closeout 仍未清理；④R-015：样例全用 Ui 面、`:636` 重复赋值仍在；⑤新测试注释写「AC1/AC3/**AC8**」，本卡仅 6 AC | `doc/tasks/FEA-14-SET-1.md:86-112`；`doc/REBASELINE_PLAN.md:51-52`；`SettingsPageView.cs:627-641`；`SettingsTypographyRenderTests.cs:14` | 随 r2 处置一并清理，或由 DSH 明确不阻断并登记 | open |

## 4. AC 逐项（不把未实测项记 PASS）

| AC | 判别 | 本审查结果 | 依据/说明 |
|---|---|---|---|
| AC1 投影正确性 | 3 行（token/栈/实际族+缩放行高）；null/Unavailable → 稳定占位 | **PARTIAL** | 真实资源下 `Read()` 三行、完整栈、scale/lineHeight 已由探针实测（`fontprobe2.log`）；但无真实路径测试（R2-001）、locale 下丢行高（R2-002）、Data/Display 缩放值错配（R2-003）、渲染测试未断言 3 行/占位/样例（R2-007） |
| AC2 回退解析纯函数矩阵 | 已装命中 / 全缺失 generic / 空栈 / fallback 标记 | **MET** | 6 条纯函数测试 + 定向 35/35 全绿；`Fallback` 语义已与 scope §3 AC2 一致（`TypographySnapshot.cs:78-81`，测试 `:25`）；仅裁决记录/字段 doc 未同步（R2-008，P3，不阻断 AC2 本体） |
| AC3 零全局副作用 | Resources/Styles 引用与值不变；样例字体不外溢 | **PARTIAL** | 代码无写入（只读 `TryGetResource`；样例 `FontFamily` 仅设局部 `TextBlock`——静态核对）；但新增测试的资源断言为 0==0 恒真、未检查字体资源值与样例外溢（R2-005），故不能记 MET |
| AC4 无 AppData 写入 | 真实 `%APPDATA%\NewManga` 指定 artefact 字节+mtime 不变 | **PARTIAL** | 实测测试前后 AppData 无变化（仅 `theme-settings.json`，mtime 保持 2026-10-30）；但指定 artefact 不存在、断言空转，无负例/基线（R2-006） |
| AC5 UI/逻辑分离 + 只读门禁 + a11y | VM 构造/搜索命中/只读/a11y | **PARTIAL** | VM 无 Application 构造与搜索命中（含 `字体`/`typography.ui`）有测试且通过；a11y 名已含 resolved（R-006 改进）；但 `SettingsField` 非 Tab 落点、无 a11y 断言、无 `WritesAllowed=false` 视图测试（R2-011） |
| AC6 边界与零契约变更 | diff ⊆ allowed；禁改目录 0；pins 18/18；check PASS | **FAIL** | 禁改目录命中 0、pins 18/18、check PASS 均实测通过；但 `git diff --name-only c4e40509b caee4c86a` = 19 文件，`SettingsTypographyRenderTests.cs` **不在** 16 条 allowed_paths 内 → 「diff ⊆ 16 paths」不成立（R2-004） |

## 5. 门禁实测（本审查实际执行）

| # | 命令 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --filter "FullyQualifiedName~TypographyResolverTests\|FullyQualifiedName~SettingsTypographyPanelTests\|FullyQualifiedName~SettingsTypographyRenderTests\|FullyQualifiedName~SettingsDraftSyncTests\|FullyQualifiedName~FluentResidualSettingsLeaveTests"` | 08:34:50 → 08:35:02 | **35 通过 / 0 失败 / 0 跳过**（含新 `SettingsTypographyRenderTests` 3 条） | **0** |
| 2 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-14-SET-1.md` | 08:35:07 → 08:35:08 | **PASS**（3 warnings：11 个非终态 Task；STATUS 2920 B/29 L 80%；PLAN 6705 B/61 L 80%） | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 08:35:09 | **PIN AUDIT: PASS (all 18)**（C02 `bb365ca891a7`、C03 `b77e7968a00b`、C07 `3fdb44e49afe`） | **0** |
| 4 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj`（全量） | 08:36:31 → 08:41:25（4 m 50 s） | **852 通过 / 0 失败 / 11 跳过 / 863 总计** | **0** |
| 5 | `git status --short` + `git rev-parse HEAD`（开始/结束各一次） | 约 08:30 / 08:46:41 | 两次均 **clean**；HEAD 两次均 `caee4c86ad13068b40c26831c79d1985a7b4c145` | — |

本地日志（仓外）：`G:\CODEX\New Manga.workspace\temp\FEA-14-SET-1-r2\gate1-targeted-tests.log`、`gate2-check-taskpath.log`、`gate3-pins.log`、`gate4-full-tests.log`。

独立探针（仓外，供复核）：`G:\CODEX\New Manga.workspace\temp\FEA-14-SET-1-r2\fontprobe2.log`
- 命令：`dotnet run --project "G:\CODEX\New Manga.workspace\temp\FEA-14-SET-1-r2\FontProbe\FontProbe.csproj" -c Release`，EXIT 0；
- 内容：①`FontFamily.FamilyNames.ToString()` 的实测；②`AppBuilder.Configure<NewManga.App.App>().UseHeadless(...).SetupWithoutStarting()` 后真实 `App.axaml` 资源栈（`Resources.Count=0`、`MergedDictionaries=3`、`Nm.FontFamily.*` 为 `FontFamily`、`Nm.FontSize.*`/`Nm.LineHeight.*` 为 `Double`）→ `AvaloniaTypographySource.Read()` 的实读输出（zh-CN 与 de-DE 两组）；③合并字典追加已知 `FontFamily` 栈后的读取。
- 边界：探针用的是 **App.axaml 全局 token 栈**（与 ThemeEngine 应用用户主题层时写入的键/类型相同：`FontFamily` + `double`），**未启动 `ThemeService` 应用用户主题包**；「真实用户主题包经 ThemeService 应用后再投影」记 NOT_RUN（见 §8），不对其作 PASS 声明。

## 6. 范围与越界

- `git diff --name-status c4e40509b caee4c86a`：**19 个文件**。
- 允许清单：卡面 `allowed_paths` 16 条（`doc/tasks/FEA-14-SET-1.md:21-37`）；逐文件匹配（含 `doc/reviews/FEA-14-SET-1-*.md` 与 `verification/FEA-14-SET-1/**` 通配）→ **18 在范围内、1 OUT**：
  - `OUT apps/desktop-avalonia/tests/NewManga.App.Tests/SettingsTypographyRenderTests.cs`（新文件；卡面与 scope §4 均未列）。
- 禁止目录：`doc/plan/**`、`doc/contracts/**`、`tools/governance/**`、`doc/tasks/FEA-13*` 命中 **0**；C-03/C-02/P15/C-07 零字节（pins 18/18 亦证）。
- 产品面：仍为只读投影——无字体选择/持久化、无 IPC/Core 命令、未改 `Application.Styles`/全局资源（仅 `TryGetResource` 只读读取；样例字体仅设局部 `TextBlock`）；未见新 `IThemeStudioService.ApplyAsync`/`SaveThemes` 调用。
- 结论：**存在 1 处冻结写域越界（新增未授权测试文件），无契约/pins/生产功能越界**。
- 本审查自身写域：仅 `doc/reviews/FEA-14-SET-1-r2.md`；主树在审查前后均 clean（见 §5 #5）。

## 7. 证据复核

| 证据 | 现状 | 判定 |
|---|---|---|
| `verification/FEA-14-SET-1/README.md` | mtime 2026-11-09T18:38Z（= 64c32fa47 时点）；AC1/AC3/AC4/AC5 仍 **PASS**；AC6 仍「diff ⊆ 16 paths」PASS；日志引用「定向 11 / 全量 849/0/11」 | **未刷新**：低于/背离 head 事实（全量 852/0/11，定向 35；19 文件）。PASS 声明高于判别力（R2-005/6/7/9） |
| `logs/dotnet-typography-tests.log` | 11/0，02:33:15，EXIT 0 | 旧 head 证据；不能支撑 `caee4c86a` |
| `logs/dotnet-app-tests.log` | 849/0/11，02:37:49，EXIT 0 | 旧 head；head 实测 852/0/11 |
| `logs/gates-check.log` / `gates-pins.log` | 02:37:51；STATUS 2929 B/PLAN 6735 B | 与 head 的 2920/6705 不同（a0e59ac3b 改过文档，可解释）但未在 head 重跑；本次已实测 PASS/PASS |
| `mutations/M1`, `M2` | 2 failed/4 passed、EXIT 1；失败点与变异语义吻合 | 语义仍有效（测试行号 22-23 未变），但**无 patch/脚本**、未在 head 重放；R-013 未关闭 |
| scope §5 要求 | `typography-fallback.log`、`appdata-redline.log`、`ipc-replay.log`、API inventory/grep 证明 | **缺失**，README 只声明截图 NOT_RUN |

## 8. NOT_RUN 声明（不得冒充 PASS）

- 真实 UI 截图基线：**NOT_RUN**（README 已声明）。
- 「真实用户主题包经 `ThemeService` 应用后」的投影：**NOT_RUN**（本审查探针只覆盖 App.axaml 全局 token 栈；未启动 ThemeService/未写用户主题包）。
- Host `WritesAllowed=false` 下的字体组只读 UI：**NOT_RUN**（无测试）。
- `%APPDATA%\NewManga` 两个指定 artefact（`presentation-settings.json`/`themes\`）前后字节比较：**NOT_RUN**（本机不存在）。
- `--theme-home` 临时目录负例：**NOT_RUN**。
- 变异 M1/M2 重放：**NOT_RUN**（只读审查，无 patch/脚本）。
- 真实 `Application.Styles` 内容级不变（逐 Style 属性）：**NOT_RUN**（新增测试只比对象 hash 列表）。

## 9. 复审要求（给 DSH / owner 的可执行建议）

1. **R-002（P1）闭合**：补真实资源路径测试（`ResourceDictionary` 注入 `FontFamily`+`double` → `AvaloniaTypographySource.Read()` 断言三行/StackRaw/scale/lineHeight），并修复 R2-002（locale）与 R2-003（Data→Sm、Display→Xxl；若有不同裁决须留痕）。
2. **R2-004**：把 `SettingsTypographyRenderTests.cs` 显式加入 `allowed_paths`（DSH 授权留痕）或并入 allowed 的 `SettingsTypographyPanelTests.cs`；同步修正卡面 AC6/README 的「diff ⊆ 16 paths」。
3. **R2-005/6/7**：把 AC3 的资源不变断言改为真实资源引用/值比较 + 样例字体不外溢；AC4 补指定 artefact 的 sha256+mtime 基线（或负例），否则按 AC 口径降级 NOT_RUN；渲染测试补 3 行/占位/样例断言。
4. **R2-008**：落 R-007 裁决记录并更新 `Fallback` XML doc；**R2-009**：在最终 head 重跑并替换 `verification/FEA-14-SET-1/**`（含缺失 artefact 或 NOT_RUN 声明）。
5. **P3 清理**（可与 P3 worktree 合并）：R-012 组合根注入/缓存、R-006 Tab 落点与只读测试、R-009 PLAN 行入 DAG 表、R-014 卡面占位清理、R-015 样例按 face、新测试注释「AC8」笔误。

> 若 DSH 认为 R-002 的剩余测试义务可书面豁免（明确降级为 P2/P3），仍需先处置 R2-002/R2-003 两个产品侧缺陷并修正 AC6/README 的失实声明，方可转入 approved 流程。
