---
task_id: FEA-14-SET-1
reviewer: DSH 派发的 fresh 独立上下文子 agent（委托方 session `c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`）
reviewer_kind: subagent
author: dsh
base_commit: c4e40509b
reviewed_head: 64c32fa47
decision: changes_requested
---

# Review：FEA-14-SET-1（字体只读投影，r1）

## 范围与依据

- 被审 head：`64c32fa47`；base：`c4e40509b`；工作树 clean（审查开始时）。
- 范围依据：`doc/tasks/FEA-14-SET-1.md`（16 allowed_paths / 6 AC）与 `doc/reviews/FEA-14-SET-1-scope-r1.md` §1.6 窄化口径（只读投影 + 回退解析 + 本地样例预览；零写入 / 零持久化 / 零契约字节）。
- 审查方式：只读 diff + 证据复核 + 门禁实测；未改生产源码/测试/契约，未 commit/push；仅写本报告。

## 结论

**`changes_requested`**。实现落在窄化口径内（无越界、无契约字节、无写入路径可见），但核心投影在真实主题资源上存在一个 P1 正确性缺陷：`FontFamily.Name` 只返回字体栈首段，生产环境会把「主题栈原文 / 实际使用族 / 缺失段」全部截断；另有 AC1 的缩放/行高未投影、AC3/AC4 证据断言不成立、AC5 a11y 缺口等。P0=0，P1=2；按仓库 Review 门槛（P0/P1 未解决不可批准）不能批准。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | **P1** | `apps/desktop-avalonia/src/NewManga.App/Services/TypographySnapshot.cs:131-144`（关键行 141） | 真实 source 的 `FontFamily` 分支取 `family.Name`；Avalonia 11.3.22 的 `FontFamily.Name` 只是首族，完整栈在 `FamilyNames`。主题 token 是强类型 `FontFamily`（`Tokens.Global.axaml:22-24`、`ThemePaletteComposer.cs:181-183`），所以生产环境「主题栈原文」只剩首族；resolver 只探测首族，首族缺失时会误报 `sans-serif` / 缺失=首族，而 Avalonia 实际会落到下一已装族。**AC1/AC2 的真实路径不成立**。 | PowerShell 反射加载 `bin/Debug/net9.0/Avalonia.Base.dll`：`FontFamily.Parse("Segoe UI Variable Text, Microsoft YaHei UI, Noto Sans SC, system-ui, sans-serif")` → `Name=<Segoe UI Variable Text>`，`FamilyNames=<Segoe UI Variable Text\|Microsoft YaHei UI\|Noto Sans SC\|system-ui\|sans-serif>`；测试只用 fake string/fake source，未覆盖此分支。 | 改为 `string.Join(", ", family.FamilyNames)`（或把 `_resourceLookup` 提升为 `Func<string, object?>` 并抽取可测的转换）；新增一条以真实 `FontFamily` 为输入的 `AvaloniaTypographySource` 测试，断言 3 条栈完整、首族缺失时 resolved 为下一已装族。 | open |
| R-002 | **P1** | `TypographySnapshot.cs:107-129`；`SettingsPageView.cs:608-611` | `AvaloniaTypographySource.Read()` 调 `Resolve` 时从不传 `scale`/`lineHeight`，两字段在生产路径恒为 `null`；视图只在非空时追加，因此 AC1 明确要求的「缩放/行高」永远不会显示。`TypographyResolverTests` 只验证了参数透传，不构成投影证据。 | 代码路径；`ThemePaletteComposer.cs:185-207` 已把 `Typography.Scale` 落到 `Nm.FontSize.*`、把 `LineHeight` 落到 `Nm.LineHeight.*`，source 未读取。 | 读取 `Nm.FontSize.Md`/`Nm.LineHeight.Body`（或经 `DesignSystemThemeManager` 的只读 API）并填入行；或经 DSH 明确把 AC1 的「缩放/行高」降为非目标。 | open |
| R-003 | P2 | `SettingsTypographyPanelTests.cs:39-49`；`SettingsPageView.cs:588-640` | AC1 要求「字体组渲染 3 行」，但测试只断言 `viewModel.TypographyLines.Count==3`，从未构造 `SettingsPageView` 或 `BuildTypographyGroup`；61 行视图代码（占位/3 行/样例/文案）在测试中零执行。README 将 AC1 记为 **PASS** 属过度声明。 | `rg` 全测试目录：仅 `SettingsTypographyPanelTests`/`TypographyResolverTests` 提及 Typography，均为 VM/纯函数；`FluentPageTests` 只渲染默认 Appearance 组。 | 增加 headless `AvaloniaFact`：选 `SettingsGroupId.Typography`，断言 3 个 `SettingsField`、占位态、样例控件 `FontFamily` 只落在样例；若无法建 headless 环境，README 记 `NOT_RUN`，不得记 PASS。 | open |
| R-004 | P2 | `SettingsTypographyPanelTests.cs:77-89` | AC3 的测试只断言 `Application.Current` 引用不变（本测试中为 `null`，`Assert.Same(null,null)` 恒真）；未断言 `Application.Current.Resources[NmKeys.FontFamily.*]`、`Application.Current.Styles` 的引用/值不变，也未渲染样例验证「自定义字体不外溢」。README 将 AC3 记 PASS 缺判别力。 | 测试代码；无任何 `Styles`/`Resources` 读取/比较。 | 在带真实 `Application` 的 headless 测试中保存三字体资源与 `Styles` 引用、渲染前后 `Assert.Same`/值相等，并断言样例 `FontFamily` 不在全局资源；否则 AC3 只能记 `NOT_RUN`。 | open |
| R-005 | P2 | `SettingsTypographyPanelTests.cs:91-102` | AC4 要求真实 `%APPDATA%\NewManga` 下 `presentation-settings.json` / `themes\` 的字节与 mtime 不变；实测该目录在 head 只有 `theme-settings.json`（359 B），两个指定 artefact 均不存在，测试对它们是空断言。指纹只含路径/长度/mtime（无 sha256），目录不存在时返回 `"<absent>"` 也能通过；未复用既有 red-line 断言，也未覆盖 scope AC4 的 `--theme-home` 负例。 | `Get-ChildItem %APPDATA%\NewManga -Recurse` 仅 `theme-settings.json`；指纹实现无哈希。 | 在受控测试中准备/确认这两个 artefact 并做字节哈希 + mtime 前后断言，把真实基线写入 `logs/`；补 `--theme-home` 负例或由 DSH 明确降级 AC4。 | open |
| R-006 | P2 | `SettingsTypographyPanelTests.cs:39-89`；`SettingsPageView.cs:612-614` 经 `FluentUi.Field`（`Controls/FluentUi.cs:108-125`） | AC5 标题含 a11y，但 3 行输入的 `AutomationProperties.Name` 只等于 token key（`Nm.FontFamily.*`），不含解析结果；`TextBlock` 默认不可聚焦、非 Tab 落点。Host `WritesAllowed=false` 的只读路径、`IsReadOnly` 断言均未覆盖；搜索测试只断言组成员，不断言组内内容。 | 代码与测试路径；`FluentUi.Field` 仅 `SetName(input, label)`。 | 把 resolved/missing 拼入自动化名；为行提供可聚焦容器或 label 关联；增加只读 Host 的视图测试；若 a11y 不在本切片，冻结时从 AC5 删除。 | open |
| R-007 | P2 | `TypographyResolverTests.cs:15-26`；`TypographySnapshot.cs:78-89` | scope r1 §3 AC2 明确要求 `Resolve(["Missing A","Installed B","sans-serif"])` → `fallbackUsed=true`，且负例「断言 true 而非 false」；实现把 `Fallback` 定义为「落到 generic 尾巴」并断言 `False`。卡面 AC2 改写为「fallback 标记正确」，与 scope 原文存在语义冲突，需 DSH 裁决或改卡。 | 测试第 24 行 `Assert.False(line.Fallback)`；实现 `fallback` 条件含 generic 判断。 | 二选一：按 scope 让「首族缺失但后续命中」也置 `true` 并改测试；或明确冻结「仅 generic 尾巴」语义、同步改 scope/卡面与字段注释。 | open |
| R-008 | P2 | `SettingsViewModel.cs:103-109`；`SettingsPageView.cs:347-356` | `SearchFields(Typography)` 宣称 `typography.ui/data/display` 可搜，但视图内容过滤按 `SettingsField` 的 label（`Nm.FontFamily.Ui/...`）与自动化名匹配；搜索「字体」或 `typography.ui` 时组能命中，3 行投影与 3 行样例却全部被 `ApplyFieldSearch` 隐藏，面板只剩标题/说明。AC5 的搜索测试只断言组可见，未发现该问题。 | `ApplyFieldSearch` 只隐藏 `SettingsField`；Typography 行 label 为 `Nm.FontFamily.*`，样例 label 为「中文/拉丁/数字」，均不含 `typography.ui`/「字体」。 | 让行 label 采用可搜索 key（如 `typography.ui`），或在 `SearchFields` 中改列实际渲染标签；补一个视图级搜索断言（命中后至少一行可见）。 | open |
| R-009 | P2 | `doc/STATUS.md:7`；`doc/REBASELINE_PLAN.md:51-52` | head 已包含 VM/View 字体组且全部 AC 标记 `<<MET>>`，但 STATUS 与 PLAN 仍写「VM/View 字体组待补」；PLAN 新增行放在 `READY 节点：无` 之后、DAG 表之外，不是合法表行，DAG 事实与卡面不一致。 | 文档 diff；PLAN 第 7-45 行为 DAG 表，第 52 行为孤立管道行。 | 关闭前把两处改为「VM/View 已落、待 Review/集成」并把新行并入 DAG 表（或活动节点节）；注意 PLAN 80% 预算。 | open |
| R-010 | P3 | `TypographySnapshot.cs:107-129` | `missingTokens` 收集后从未使用；仅当 3 个 token 全缺失才 `Available=false`。若只有 1–2 个 token（部分主题初始化），返回 `Available=true` + <3 行，界面无任何「部分缺失」提示，不符合「3 行/稳定占位」的完整性预期。 | 代码；无部分 token 测试。 | 把部分缺失降级为 `Available=false`（附原因），或在行上标注缺失 token；删除死变量。 | open |
| R-011 | P3 | `TypographySnapshot.cs:78-81` | `Fallback` 条件 `missing.Count == segments.Count - 1` 对只含 generic 的栈 `"sans-serif"`（0 == 0）会置 `true`，与「缺失才回退」语义不符；无测试。 | 逻辑推演；现有 6 条测试未覆盖。 | 改为 `resolved is generic && missing.Count > 0`；补单测。 | open |
| R-012 | P3 | `SettingsViewModel.cs:76-87`；`SettingsPageView.cs:595,603,619`；`FluentShellSurface.axaml.cs:122`（allowed 但未改） | 每次属性访问都 `new AvaloniaTypographySource().Read()`；一次组渲染至少 3–4 次全量字体探测（`TryGetGlyphTypeface`），在 UI 线程同步执行。生产组合根未注入 source，依赖 VM 内部默认 new，削弱 UI/逻辑分离。 | 代码路径。 | 每轮渲染缓存一次 snapshot（或在 `LoadAsync`/组切换时刷新）；在 `FluentShellSurface` 组合根注入 source，VM 默认改为 unavailable 或保留但注明。 | open |
| R-013 | P3 | `verification/FEA-14-SET-1/` | 证据缺少 scope §5 的 `typography-fallback.log`、`appdata-redline.log`、`ipc-replay.log`、`generate_api_inventory` 日志与 grep 证明；M1/M2 日志只有失败输出、无变异 patch，无法独立复现。截图 `NOT_RUN` 已如实记录。 | 目录清单；本审查实跑 API inventory `EXIT=0`（1/54/6=61）可补。 | 补交 API inventory / AppData 基线 / 变异 patch 或脚本；或把未执行项统一列为 `NOT_RUN`。 | open |
| R-014 | P3 | `doc/tasks/FEA-14-SET-1.md:86-99,101-112` | 卡面仍保留「第一切片占位」「预估范围（待 scope review）」「## Acceptance Criteria：待 scope review 冻结（当前仅占位；不得实施）」与「Resource Manifest：未访问真实数据」，与已冻结 AC、已实现代码、已读 AppData 的证据冲突；`delivery_head`/`canonical_evidence_status` 仍为 null（若按流程由集成阶段填写可忽略）。 | 卡面原文。 | 关闭/复审前清理重复 AC 与占位文案，刷新 Resource Manifest/Closeout；`delivery_head` 按 DSH 生命周期填写。 | open |

## AC 逐项

| AC | 判别 | 依据 | 结果 |
|---|---|---|---|
| AC1 投影正确性 | 注入 source → 3 行；token/栈/实际族/缩放行高；Unavailable 占位 | VM 投影 3 行有测试；但真实 source 截断字体栈（R-001）、缩放/行高恒 null（R-002）、视图渲染零测试（R-003） | **PARTIAL** |
| AC2 回退解析纯函数矩阵 | 已装命中 / 全缺失 generic / 空栈 / fallback 标记 | 纯函数矩阵 6 条全绿；混合栈 `Fallback` 与 scope 期望相反（R-007） | **PARTIAL** |
| AC3 零全局副作用 | Resources/Styles 引用与值不变；样例字体不外溢 | 仅断言 `Application.Current` 恒等（R-004）；代码可见只读，但无判别断言 | **PARTIAL** |
| AC4 无 AppData 写入 | 真实 `%APPDATA%\NewManga` 的指定文件字节+mtime 不变 | 指定 artefact 在 head 不存在，断言空转；无哈希/负例（R-005） | **PARTIAL** |
| AC5 UI/逻辑分离 + 只读 + a11y | 无 Application 构造 VM；搜索；只读；Host 只读；a11y | VM 构造/搜索命中通过；a11y 名缺 resolved、非 Tab 落点；Host 只读未测（R-006）；搜索内容被隐藏（R-008） | **PARTIAL** |
| AC6 边界与零契约变更 | diff ⊆ 16 paths；无 `doc/plan`/`contracts`/`governance`/`FEA-13`；pins 18/18；check 默认+TaskPath；API inventory | 全部实测通过 | **MET**（证据日志缺 API inventory 记录，见 R-013） |

## 门禁实测（本审查，`64c32fa47`，工作树 clean）

| 命令 | 结果 | EXIT |
|---|---|---|
| `dotnet test ... --filter "FullyQualifiedName~TypographyResolverTests\|FullyQualifiedName~SettingsTypographyPanelTests"` | 11 通过 / 0 失败 / 0 跳过 | 0 |
| `dotnet test NewManga.App.Tests`（全量） | 849 通过 / 0 失败 / 11 跳过 / 860，4m29s | 0 |
| `pwsh -NoProfile -File tools/governance/check.ps1` | PASS（3 warnings：11 非终态、STATUS 80%、PLAN 80%） | 0 |
| `pwsh ... check.ps1 -TaskPath doc/tasks/FEA-14-SET-1.md` | PASS（同上 3 warnings） | 0 |
| `pwsh ... verify_pins.ps1` | `PIN AUDIT: PASS (all 18)` | 0 |
| `python tools/generate_api_inventory.py --check` | `OK: rendered counts match FEA-C07 doc`；IReaderProgressSink 1 / IHostController 54 (+4) / IRunController 6 = 61 | 0 |
| `git status --short` | clean（审查前；本报告写入后仅新增本文件） | 0 |

## 范围与越界

- diff 共 17 个文件，全部落入 16 条 allowed_paths（`verification/FEA-14-SET-1/**` 与 `doc/reviews/FEA-14-SET-1-*.md` 覆盖多条）；
- 禁止目录命中 **0**：`doc/plan/**`、`doc/contracts/**`、`tools/governance/**`、`doc/tasks/FEA-13*`；
- C-03/C-02/P15/C-07 **零字节**（diff 无 `doc/contracts`、无 C-03/C-02/P15 载体；`verify_pins` 18/18 含 C03/C02/C07）；18 pins 零变化；
- 未提供字体选择/持久化、未新增 IPC/Core 命令、未改 `IHostController`；新增代码只有 `Application.Current.Resources.TryGetResource` 只读调用与样例控件局部 `FontFamily`，无 `Application.Styles`/资源写入；
- 结论：**无越界**。`AvaloniaTypographySource.cs` allowed 但未单列（类在 allowed 的 `TypographySnapshot.cs` 内），`FluentShellSurface.axaml.cs` allowed 但未改（由 VM 默认 new source 兜底），均不构成越界，仅 R-012 的设计/性能提示。

## 证据复核

- `logs/dotnet-typography-tests.log`（11/0，EXIT 0）：本审查重跑一致。
- `logs/dotnet-app-tests.log`（849/0/11，EXIT 0）：本审查全量重跑一致（4m29s，11 个 skip 为既有条件跳过）。
- `logs/gates-check.log` / `logs/gates-pins.log`：本审查重跑一致。
- `mutations/M1`（missing 未记录）与 `M2`（栈首直接当真值）：两份日志均为 2 failed / 4 passed、EXIT 1，失败点与变异语义吻合；受只读约束未重放变异，且日志无 patch，判别力可接受但不可独立复现（R-013）。
- `verification/FEA-14-SET-1/README.md`：AC1/AC3/AC4 的 PASS 声明高于现有测试判别力（R-003/R-004/R-005）；截图 `NOT_RUN` 已如实声明。

## 未覆盖 / NOT_RUN

- 真实 Avalonia 渲染截图：`NOT_RUN`（README 已记）。
- 真实 `Application` 下的资源/Styles 前后比对：`NOT_RUN`（R-004）。
- `%APPDATA%\NewManga\presentation-settings.json` / `themes\` 的字节指纹：`NOT_RUN`（文件在 head 不存在，R-005）。
- Host `WritesAllowed=false` 下的字体组只读 UI：`NOT_RUN`（R-006）。
- 变异 M1/M2 的重放：`NOT_RUN`（只读审查；日志可读，patch 缺失，R-013）。

## 复审要求

1. 优先修 R-001（真实 source 的 `FamilyNames` 投影）并补真实 `FontFamily` 的 source 测试；这是 AC1/AC2 产品价值的前提。
2. 处理 R-002（缩放/行高）与 R-003（视图渲染测试），或由 DSH 明确缩减 AC1 并同步卡面。
3. 对 R-004/R-005/R-006 选择「补真实判别测试」或「AC 降级并记 NOT_RUN」，不要保留当前 PASS 声明。
4. R-007 的 `Fallback` 语义需 DSH 裁决；R-008 与 R-009 应在关闭前修正。
5. 复审提交新 head 后，重新跑定向/全量/门禁并更新 evidence；本报告仅对 `64c32fa47` 有效。
