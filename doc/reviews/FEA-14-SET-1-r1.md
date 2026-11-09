---
task_id: FEA-14-SET-1
reviewer: DSH 派发的 fresh 独立上下文子 agent（委托方 session `c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`）
reviewer_kind: subagent
author: dsh
base_commit: c4e40509b
reviewed_head: 64c32fa47
decision: changes_requested
---

# Review：FEA-14-SET-1（设置页字体只读投影，r1）

## 范围与依据

- 被审 head：`64c32fa47`；base：`c4e40509b`；审查开始时工作树 clean。
- 依据：`doc/tasks/FEA-14-SET-1.md`（16 allowed_paths / 6 AC）、`doc/reviews/FEA-14-SET-1-scope-r1.md` §1.6 窄化口径（字体**只读投影** + 回退解析 + 本地样例预览；零写入 / 零持久化 / 零契约字节）。
- 方式：只读 diff + 证据复核 + 门禁实测；未改生产源码/测试/契约，未 commit/push；仅写本报告。

## 结论

**`changes_requested`**（仅对 `64c32fa47` 有效）。实现方向落在窄化口径内：无字体选择/持久化、无 IPC/Core 改动、无 `Application.Styles`/全局资源写入、契约零字节；但核心投影在**真实主题资源**上有一个 P1 正确性缺陷（字体栈被截断为单族），另有 AC1 明确要求的「缩放/行高」在生产路径恒为 `null`。P0=0，P1=2；按 P0/P1 未解决不可批准的门槛不能批准。

> **环境事实（影响门禁归因）**：审查期间仓库被并发推进——`02:48:54` 出现提交 `a0e59ac3b`（`fix(fea-14-set-1): r1 处置（R-001 栈全族/R-002 缩放行高/R-007 fallback 裁决/R-009/R-014）`），改动 `TypographySnapshot.cs`（+37/−?）、`TypographyResolverTests.cs`（3 行）与 STATUS/PLAN/卡面。本报告的代码判定与行号全部取自 `git show 64c32fa47:...`；门禁实测在**当前树 `a0e59ac3b`** 上完成（定向测试与门禁结果一致，见「门禁实测」），不能单独归于 `64c32fa47`。新 head 未在本次范围内复审。

## Findings

| ID | 级别 | 位置（`64c32fa47`） | 事实与影响 | 证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-001 | **P1** | `Services/TypographySnapshot.cs:131-144`（关键 141） | `DefaultLookup` 对 `FontFamily` 资源取 `family.Name`。Avalonia 的 `FontFamily.Name` 只是**首族**，完整栈在 `FamilyNames`；而 `ThemePaletteComposer` 把 `Nm.FontFamily.Ui/Data/Display` 落成 `new FontFamily(TokenValues.ParseFontFamily(raw))`（按逗号切分的完整栈）。于是生产路径：主题栈原文只剩首族、resolver 只探测首族；首族未装时会误报「缺失=首族 / 回退 generic」，而 Avalonia 实际会用到下一已装族。**AC1/AC2 的真实路径不成立** | 反射加载 `bin/Debug/net9.0/Avalonia.Base.dll`：`FontFamily.Parse("Segoe UI Variable Text, Microsoft YaHei UI, Noto Sans SC, system-ui, sans-serif")` → `Name=Segoe UI Variable Text`，`FamilyNames=Segoe UI Variable Text\|Microsoft YaHei UI\|Noto Sans SC\|system-ui\|sans-serif`；`ThemePaletteComposer.cs` 的 `layer[NmKeys.FontFamily.Ui] = ParseFontFamily(...)`；测试只用 fake string / fake source，未覆盖此分支 | 改取 `string.Join(", ", family.FamilyNames)`（或把 `_resourceLookup` 放宽为 `Func<string, object?>` 并抽出可测转换）；补一条以真实 `FontFamily` 为输入的 source 测试 | open（新 head 声称已处） |
| R-002 | **P1** | `TypographySnapshot.cs:107-129`（119）；`Views/Fluent/SettingsPageView.cs:608-611` | `Read()` 调 `Resolve(...)` 从不传 `scale`/`lineHeight`，两字段生产恒 `null`；视图仅在非空时追加「缩放/行高」，故 AC1 明确要求且 scope 范围第 1 条列出的「字号缩放/行高预设」**永不显示**。`TypographyResolverTests.ScaleAndLineHeightAreCarriedThroughUntouched` 只证明参数透传，不是投影证据 | 代码路径；`ThemePaletteComposer` 已把 `Typography.Scale` 落到 `Nm.FontSize.*`、`LineHeight` 落到 `Nm.LineHeight.*`，source 未读取 | 读 `Nm.FontSize.Md`/`Nm.LineHeight.Body` 等填入行，或由 DSH 明确把 AC1 该子项降为非目标并改卡 | open（新 head 声称已处） |
| R-003 | P2 | `SettingsTypographyPanelTests.cs:39-49`；`SettingsPageView.cs:588-640` | AC1 要求「字体组渲染 3 行」，测试只断言 `viewModel.TypographyLines.Count==3`，从未构造视图/`BuildTypographyGroup`；约 66 行视图代码（标题、3 行、占位态、3 行样例、双段文案）在测试中零执行。README 把 AC1 记 **PASS** 高于判别力 | `rg` 测试目录：Typography 仅出现在两个 VM/纯函数测试；无 `SettingsPageView` 相关断言 | 补 headless `AvaloniaFact`（选 `SettingsGroupId.Typography`，断言 3 个 `SettingsField`、占位态、样例 `FontFamily` 不外溢）；做不到则 README 记 `NOT_RUN` | open |
| R-004 | P2 | `SettingsTypographyPanelTests.cs:77-89` | AC3 测试只断言 `Application.Current` 引用不变，而该测试中前后都是 `null`（`Assert.Same(null,null)` 恒真）；未断言 `Application.Current.Resources[NmKeys.FontFamily.*]` 的值/引用与 `Application.Styles` 不变，也未验证「样例自定义字体不外溢」。README 的 AC3 PASS 缺判别力 | 测试代码；无任何 `Styles`/`Resources` 读写比较 | 在带真实 `Application` 的 headless 测试中保存三字体资源与 `Styles` 引用后比对；做不到则 AC3 记 `NOT_RUN` | open |
| R-005 | P2 | `SettingsTypographyPanelTests.cs:91-102` | AC4 要求真实 `%APPDATA%\NewManga` 的 `presentation-settings.json`/`themes\` 字节与 mtime 不变。实测该目录只有 `theme-settings.json`，两个指定 artefact 均不存在 → 断言对它们是空转；指纹只含路径/长度/mtime（无 sha256），目录缺失返回 `"<absent>"` 也能通过；未复用既有 red-line 断言的完整形态，也无 `--theme-home` 负例 | `Get-ChildItem %APPDATA%\NewManga -Recurse` 仅 `theme-settings.json`；指纹实现无哈希 | 准备或确认两个 artefact 后做哈希+mtime 前后断言并留基线日志；或补负例；或由 DSH 明确降级 AC4 | open |
| R-006 | P2 | `SettingsTypographyPanelTests.cs:63-89`；`SettingsPageView.cs:588-640` | AC5 标题含 a11y，但行输入控件（`FluentUi.Field`）的自动化名只有 token key（`Nm.FontFamily.*`），不含解析结果/缺失段；`TextBlock` 不可聚焦、非 Tab 落点。Host `WritesAllowed=false` 的只读路径与 `IsReadOnly` 均无测试（视图侧 `DisableWriteControls` 无写入控件可禁，行为未被验证） | 代码路径；测试无 Host/只读断言 | 把 resolved/missing 拼入自动化名并做 label 关联；补只读 Host 的视图测试；或在冻结时把 a11y 从 AC5 移出 | open |
| R-007 | P2 | `TypographyResolverTests.cs:15-26`（24）；`TypographySnapshot.cs:78-81` | scope r1 AC2 明确写 `Resolve(["Missing A","Installed B","sans-serif"])` → `fallbackUsed=true`，并给出负例「断言 `fallbackUsed` 为 true 而非 false」；实现把 `Fallback` 定义为「落到 generic 尾巴」，同一用例断言 `False`。卡面 AC2 改写为「fallback 标记正确」，与 scope 原文语义冲突，需 DSH 裁决并同步卡面/scope/字段注释 | scope r1 AC2 原文；测试第 24 行；实现条件含 generic 判断 | 二选一：按 scope 让「首族缺失但后续命中」也置 true 并改测试；或冻结「仅 generic 尾巴」语义并改 scope/卡面 | open（新 head 声称已处） |
| R-008 | P2 | `SettingsViewModel.cs:103-109`；`SettingsPageView.cs:347-356` | `SearchFields(Typography)` 宣称 `typography.ui/data/display` 可搜，但组内内容过滤 `ApplyFieldSearch` 只按 `SettingsField` 的 label/自动化名匹配；字体行 label 为 `Nm.FontFamily.Ui/...`、样例 label 为「中文/拉丁/数字」，都不含 `字体`/`typography.ui`。搜索这两个词时组可见但**组内 3 行投影与 3 行样例全被隐藏**，只剩标题/说明 | `ApplyFieldSearch` 实现 + 行 label 取值；搜索测试只断言组成员可见 | 让行 label 采用可搜索 key（如 `typography.ui`）或让 `SearchFields` 列实际渲染标签；补视图级搜索断言（命中后至少一行可见） | open |
| R-009 | P2 | `doc/STATUS.md:7`；`doc/REBASELINE_PLAN.md:51-52` | head 已包含 VM/View 字体组且 AC 全标 `<<MET>>`，但 STATUS 仍写「VM/View 字体组待补」，PLAN 仍写「VM/View 待补」；PLAN 新行以孤立 `|FEA-14-SET-1|...|` 形式落在 `READY 节点：无` 之后，不在 DAG 表内，文档事实与代码不一致 | `git show 64c32fa47:doc/STATUS.md` / `doc/REBASELINE_PLAN.md` 原文 | 关闭前把两处改为「VM/View 已落、待 Review/集成」，把新行并入 DAG 表（注意 80% 预算） | open（新 head 声称已处） |
| R-010 | P3 | `TypographySnapshot.cs:110,121` | `missingTokens` 收集后从未使用；仅当 3 个 token **全**缺失才 `Available=false`。只有 1–2 个 token 时返回 `Available=true` + <3 行，界面无「部分缺失」提示，与 AC1「3 行/稳定占位」的完整性预期不符 | 代码；无部分 token 测试 | 部分缺失降级为 `Available=false`（附原因）或行上标注，删除死变量；补测试 | open |
| R-011 | P3 | `TypographySnapshot.cs:78-81` | `Fallback` 条件 `missing.Count == segments.Count - 1` 对只含 generic 的栈 `"sans-serif"`（0 == 0）会置 `true`，与「缺失才回退」语义不符；且视图从不渲染 `Fallback` 标记，字段目前只有测试可见 | 逻辑推演；6 条测试未覆盖单 generic 栈 | 改为 `resolved is generic && missing.Count > 0`；补单测，或让视图显示降级提示 | open |
| R-012 | P3 | `SettingsViewModel.cs:77-88`；`SettingsPageView.cs:595-631` | `TypographySnapshot` 是**每次访问都 `Read()`** 的计算属性（生产组合根未注入 source → 每次 `new AvaloniaTypographySource()`，一次组渲染 3–4 次全量 `TryGetGlyphTypeface` 探测，且均在 UI 线程同步执行）；一次渲染内多次读取还可能不一致。`FluentShellSurface.axaml.cs` 在 allowed 内但未改，削弱 UI/逻辑分离 | 代码路径；构造调用 `new SettingsViewModel(host, appearance, themeManager)` | 每轮渲染缓存一次 snapshot（组切换/加载时刷新），并在组合根注入 source | open |
| R-013 | P3 | `verification/FEA-14-SET-1/` | 证据缺 scope §5 的 `typography-fallback.log`/`appdata-redline.log`/`ipc-replay.log`/API inventory 与 grep 证明；M1/M2 日志只有失败输出、无变异 patch 或脚本，无法独立复现；`gates-check.log` 的 STATUS/PLAN 字节数与 head 现状不同（因 head 前移，可解释）。截图 `NOT_RUN` 已如实声明 | 目录清单；两份变异日志 | 补 API inventory/AppData 基线/变异 patch；未执行项统一记 `NOT_RUN` | open |
| R-014 | P3 | `doc/tasks/FEA-14-SET-1.md:86-112` | 卡面同时保留「第一切片占位」「预估范围（待 scope review）」「## Acceptance Criteria：待 scope review 冻结（当前仅占位；不得实施）」与「Resource Manifest：未访问真实数据」，与已冻结 AC、已实现代码、已读 AppData 的证据冲突；`delivery_head`/`canonical_evidence_status` 仍 null（若由集成阶段填写可接受，需注明） | 卡面原文 | 关闭/复审前清理重复 AC 与占位文案，刷新 Resource Manifest/Closeout | open（新 head 声称已处） |
| R-015 | P3 | `SettingsPageView.cs:618-633` | 3 行样例（中文/拉丁/数字）一律套用**第一条**投影行（Ui 面对应的 `ResolvedFamily`）的字体，Data/Display 面没有各自样例；同时 `FluentUi.Text(sample, ...)` 后又 `text.Text = sample` 重复赋值。不影响只读性，但与「解析结果的可见性」目标有落差 | 代码；`primary = TypographyLines.FirstOrDefault()` | 按 face 各给一行样例（或至少标注样例使用 Ui 面），删除重复赋值 | open |

## AC 逐项

| AC | 判别 | 依据 | 结果 |
|---|---|---|---|
| AC1 投影正确性 | 注入 source → 3 行（token/栈/实际族+缩放行高）；null/Unavailable → 稳定占位 | VM 侧 3 行有测试；真实 source 截断字体栈（R-001）、缩放/行高恒 null（R-002）、视图渲染零测试（R-003） | **PARTIAL** |
| AC2 回退解析纯函数矩阵 | 已装命中 / 全缺失 generic / 空栈 / fallback 标记 | 6 条纯函数测试全绿、EXIT 0；但 `Fallback` 语义与 scope AC2 要求相反（R-007），真实路径不喂完整栈（R-001） | **PARTIAL** |
| AC3 零全局副作用 | Resources/Styles 引用与值不变；样例字体不外溢 | 代码可见只读（无资源/样式写入，样例 FontFamily 仅局部设置）；测试仅断言 `Application.Current` 恒等（R-004），无判别断言 | **PARTIAL** |
| AC4 无 AppData 写入 | 真实 `%APPDATA%\NewManga` 指定 artefact 字节+mtime 不变 | 指定 artefact 在 head 不存在，断言空转；无哈希/负例（R-005）；实现本身无写入路径（设计上成立） | **PARTIAL** |
| AC5 UI/逻辑分离 + 只读 + a11y | 无 Application 构造 VM；搜索命中；只读；Host 只读；a11y | VM 构造/搜索命中通过；a11y 名缺 resolved、非 Tab 落点（R-006）；搜索会隐藏内容（R-008） | **PARTIAL** |
| AC6 边界与零契约变更 | diff ⊆ 16 paths；无 `doc/plan`/`contracts`/`governance`/`FEA-13`；pins 18/18；check 默认+TaskPath | 实测全部通过（见门禁与越界节） | **MET** |

## 门禁实测

| 命令 | 实测结果 | EXIT |
|---|---|---|
| `dotnet test ... --filter "FullyQualifiedName~TypographyResolverTests\|FullyQualifiedName~SettingsTypographyPanelTests"` | 11 通过 / 0 失败 / 0 跳过（196 ms；当前树 `a0e59ac3b`；head 证据 `02:33` 同 11/0） | **0** |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-14-SET-1.md` | PASS（3 warnings：11 非终态、STATUS 80%、PLAN 80%） | **0** |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)` | **0** |
| `git status --short` | 审查开始 clean；审查中 owner 提交 `a0e59ac3b`；当前 clean + 本报告 untracked | — |

注：全量 `dotnet test` 未重跑（单次约 4.5 min，超出本次目标预算），采用 `logs/dotnet-app-tests.log` 的 849/0/11 记录（与定向结果及 head 一致）；该日志无法由本审查独立复现，已并入 R-013。

## 范围与越界

- diff 共 17 个文件，全部落入 16 条 allowed_paths（`verification/FEA-14-SET-1/**`、`doc/reviews/FEA-14-SET-1-*.md` 覆盖多条）。
- 禁止目录命中 **0**：`doc/plan/**`、`doc/contracts/**`、`tools/governance/**`、`doc/tasks/FEA-13*`。
- C-03/C-02/P15/C-07 零字节；`verify_pins` 18/18 全绿。
- **未提供字体选择/持久化**（无写设置、无新字段、无重启读回）；未新增 IPC/Core 命令；未改 `IHostController`；未改 `Application.Styles` 或全局资源（仅 `Application.Current.Resources.TryGetResource` 只读读取；样例仅局部 `TextBlock.FontFamily`）。
- 结论：**无越界**。`AvaloniaTypographySource.cs` 在 allowed 内但未单列（类并入 allowed 的 `TypographySnapshot.cs`），`FluentShellSurface.axaml.cs` allowed 未改，均不构成越界，只在 R-012 记为设计/性能提示。

## 证据复核

- `logs/dotnet-typography-tests.log`（11/0，EXIT 0）：本审查重跑一致。
- `logs/dotnet-app-tests.log`（849/0/11，EXIT 0）：未重跑（见门禁节注）。
- `logs/gates-check.log` / `logs/gates-pins.log`：本审查重跑一致（STATUS/PLAN 字节数因 head 前移而不同，属预期）。
- `mutations/M1`（缺失族不记录）、`M2`（栈首直接当真值）：均 2 failed / 4 passed、EXIT 1，失败点与变异语义吻合；受只读约束未重放，且无 patch（R-013）。
- `README.md`：AC1/AC3/AC4 的 PASS 声明高于现有测试判别力（R-003/R-004/R-005）；截图 `NOT_RUN` 已如实声明。

## 未覆盖 / NOT_RUN

- 真实 Avalonia 渲染截图：`NOT_RUN`（README 已记）。
- 真实 `Application` 下的资源/Styles 前后比对：`NOT_RUN`（R-004）。
- `%APPDATA%\NewManga\presentation-settings.json` / `themes\` 字节指纹：`NOT_RUN`（head 下不存在，R-005）。
- Host `WritesAllowed=false` 下的字体组只读 UI：`NOT_RUN`（R-006）。
- 全量 `dotnet test` 重跑：`NOT_RUN`（采用证据日志）。
- 变异 M1/M2 重放：`NOT_RUN`（只读审查，无 patch）。
- 新 head `a0e59ac3b` 的复审：**不在本次范围**（本报告仅对 `64c32fa47` 有效）。

## 复审要求

1. 先修 R-001（`FamilyNames` 全栈投影）并补真实 `FontFamily` 输入的 source 测试——这是 AC1/AC2 产品价值前提。
2. 处理 R-002（缩放/行高）与 R-003（视图渲染测试），或由 DSH 明确缩减 AC1 并同步卡面/README。
3. R-004/R-005/R-006 二选一：补真实判别测试，或 AC 降级并统一记 `NOT_RUN`，不得保留现有 PASS 声明。
4. R-007 的 `Fallback` 语义需 DSH 裁决；R-008/R-009 关闭前修正。
5. 新 head 复审须重跑定向/全量/门禁并刷新 `verification/FEA-14-SET-1/`；本报告不对 `a0e59ac3b` 及以后负责。
