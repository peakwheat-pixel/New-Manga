---
task_id: FEA-14-SET-1
reviewer: fresh 独立上下文子 agent（同一审查上下文续接 r2；未参与实现/返修）
reviewer_kind: subagent
author: dsh
base_commit: caee4c86a
reviewed_head: 396e31efe
decision: approved
---

# Review：FEA-14-SET-1（r3 增量复核，`caee4c86a..396e31efe`）

## 0. 审查对象、环境与写域

- 被审 head：**`396e31efe`**（`main`）；增量 base：`caee4c86a`（r2 被审 head）。固定链：`64c32fa47`→`a0e59ac3b`→`caee4c86a`→`4b8f2831c`（P3）→`b0d5c7d6a`（r2 处置）→`128469abd`（证据/卡面）→`19d7d2f90`（r2 报告）→`396e31efe`（最终证据）。
- 环境事实：审查开始 `2026-11-10T09:01:52+08:00`、结束 `2026-11-10T09:12:04+08:00` 两次实测 `git rev-parse HEAD` 均为 **`396e31efe…`**、`git status --short` 均 **clean**；审查期间主树无新提交、无未提交改动。
- 写域：**仅写本文件**。未改生产源码/测试/契约/卡面/证据，未 commit/push；临时日志与探针输出只写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-SET-1-r3\`。
- 依据：`doc/tasks/FEA-14-SET-1.md`（6 AC、16 allowed_paths、r1/r2 处置记录）、`doc/reviews/FEA-14-SET-1-r1.md`、`doc/reviews/FEA-14-SET-1-r2.md`（本审查者上一轮报告）、scope r1 §1.6/§3/§5；代码事实以 `git show 396e31efe:<path>` 为准。
- 方法：增量 diff + 代码静态核对 + **独立实测**（重跑定向/全量/门禁/API inventory/AppData 脚本/IPC 单测；复用 r2 的 headless 探针工程对 head 重跑）+ 证据日志与命令/EXIT 对照。静态推演均显式标注。

## 1. 结论

**`approved`。**

| 计数 | 值 |
|---|---|
| P0 | **0** |
| P1 | **0** |
| P2 | **0** |
| P3 | **6**（均为文档/证据声称精度、测试可移植性、共享 Application 测试卫生、门禁过滤覆盖与已登记残余；不阻断） |

r2 的 11 个 finding 中 **10 个 CLOSED、R2-011 为 PARTIAL**（其残余项已由 DSH 在卡面登记为不阻断 NOT_RUN）；**无 P0/P1/P2 未关闭**。本增量未发现新的 P0/P1/P2；r2 指出的 P1（真实资源路径测试缺失）与两个产品侧缺陷（locale 丢行高、face→size 错配）均已修复并经本审查独立实测。最终交付 head 的净 diff 全部落入 16 条 `allowed_paths`，契约零字节、pins 18/18、全量 App.Tests 858/0/11。

## 2. r2 findings 关闭判定

| r2 ID | r2 级别 | 判定 | 依据（本审查实测/代码） |
|---|---|---|---|
| R2-001 | P1 | **CLOSED** | `SettingsTypographyPanelTests.cs:138-162` 新增 `TheSourceProjectsTheRealThemeResources`：`DesignSystemThemeManager.Initialize(Dark)` 真实资源 → `AvaloniaTypographySource().Read()` 断言 3 行、Ui 行含完整栈逗号、三行 scale/lineHeight 非空、Data=12/Display=24。测试**真运行**：定向扩展过滤 41/0/0、全量 858/0/11（本审查实测）；独立探针 `fontprobe-r3.log` 亦证实 3 行完整栈 |
| R2-002 | P2 | **CLOSED** | `TypographySnapshot.cs:177-187` 对 `IFormattable` 用 `InvariantCulture` 格式化；`TheSourceIsIndependentOfTheCurrentCulture`（`:164-191`）置 de-DE 后断言 scale/lineHeight 全非空，`finally` 还原文化。独立探针 head 重跑：de-DE 下三行 `lineHeight=1.45/1.25/1.25`（旧版为 null） |
| R2-003 | P2 | **CLOSED** | `TypographySnapshot.cs:105-116`：Data→`Nm.FontSize.Sm`、Display→`Nm.FontSize.Xxl`，与 `ThemeTokenBaseline.g.cs:49,54` 的 `LineHeightTiers` 一致；测试断言 Data=12/Display=24；探针实测同一结果 |
| R2-004 | P2 | **CLOSED** | `caee4c86a` 的越界文件 `SettingsTypographyRenderTests.cs` 已在 `4b8f2831c` 删除，测试并入 allowed 的 `SettingsTypographyPanelTests.cs`（两个类同文件）；`git diff --name-only c4e40509b 396e31efe` = **33 文件，全部映射进 16 条 allowed_paths（OUT=0）**；卡面 AC6/README 已改写为「交付链 diff 落入 allowed_paths」并记录处置 |
| R2-005 | P2 | **CLOSED** | `SettingsTypographyPanelTests.cs:323-361`：真实 `TryGetResource` 取三字体资源对象后渲染，`Assert.Same` 前后；`Styles.ToList()` 引用序列相等；样例 `FontFamily` 为 `Installed B` 且 `NotSame` 全局对象（不外溢）。不再是 0==0 恒真 |
| R2-006 | P2 | **CLOSED** | `scripts/appdata-redline.ps1` + `logs/appdata-redline.log`：真实 `%APPDATA%\NewManga` 全量 sha256+size+mtime 前后 `UNCHANGED`；本审查以 `-Out` 指向仓外临时路径**复现 EXIT 0**，输出与证据一致（唯一文件 `theme-settings.json` 359 B、hash `902A…1CF0`、mtime 不变）。指定 artefact `presentation-settings.json`/`themes\` 不存在 → 卡面/README 已如实记 **NOT_RUN**，未冒充 PASS |
| R2-007 | P2 | **CLOSED** | `SettingsTypographyPanelTests.cs:250-299`：投影行精确 3 个（`ProjectionLabel` 过滤样例）、缩放/行高文本、三种样例及样例字体、占位分支（`:363-380`）；README AC1/AC5 已引用渲染测试 |
| R2-008 | P2 | **CLOSED** | 卡面「DSH 裁决（R-007 fallback 语义，2026-11-10）」落文；`TypographyLine.Fallback` XML doc（`TypographySnapshot.cs:12-16`）与实现/测试/scope AC2 一致；README 实现要点同步 |
| R2-009 | P3 | **CLOSED** | `verification/FEA-14-SET-1/**` 已刷新（final logs 时间 08:55–09:01，属 `19d7d2f90` 树；该提交与最终 head 之差仅为 `verification/**`）。本审查复现：定向 35/0/0、全量 858/0/11、check PASS、pins 18/18、API inventory EXIT 0、AppData 脚本 EXIT 0、IPC 单测 1 passed——计数/EXIT 与日志一致。残余声称精度见 R3-001/R3-004 |
| R2-010 | P3 | **CLOSED** | `FluentShellSurface.axaml.cs:122` 组合根注入 `new AvaloniaTypographySource()`；`SettingsPageView.BuildTypographyGroup:592-596` 用 `ReadTypographySnapshot()` 每轮渲染只读一次；`SettingsViewModel:92-105` 缓存 + `:440` 外观 canonical 变化失效；测试 `RenderingTheTypographyGroupReadsTheSourceOncePerRender` 断言组切换 +1 次读取 |
| R2-011 | P3 | **PARTIAL（残余已登记，不阻断）** | 已做：a11y 名含解析族 + `Focusable=true` 并被渲染测试断言；样例标注 Ui 面、删除重复赋值；AC8 笔误随旧文件删除消失。残余：Host `WritesAllowed=false` 字体组视图测试、真实 Tab 遍历（仅属性断言）、R-015 按 face 样例、R-011 单 generic 栈单测——卡面「残余（不阻断，已登记）」+ README NOT_RUN 已如实登记；文档残余见 R3-006 |

## 3. R3 Findings（本增量新发现，均为 P3）

| ID | 级别 | 位置 | 事实与影响 | 证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R3-001 | P3 | `verification/FEA-14-SET-1/README.md` 门禁表；`dotnet-typography-final.log`；`doc/tasks/FEA-14-SET-1.md:123` | **证据/卡面声称与命令不一致**：README 称 final 定向「35 passed（TypographyResolver + Panel/**Render** + …）」，但该日志记录的 filter 为 `TypographyResolverTests\|SettingsTypographyPanelTests\|SettingsDraftSyncTests\|FluentResidualSettingsLeaveTests`，**不含** `SettingsTypographyRenderTests`；本审查实测该 filter = 35（不含 6 条渲染测试），加渲染过滤 = 41。卡面 Closeout 又写「定向 20 passed」（来自 P3 worktree 的中间 run）。final logs 记录的 HEAD 为 `19d7d2f90`（与最终 head 之差仅 `verification/**`，可解释）。影响：证据描述精度不足，但计数本身可由日志命令复现，且渲染测试被全量 858 覆盖，无 PASS 造假 | 本审查 gate1=35、gate1b=41（命令/EXIT 见 §5）；README:30；卡 `:123`；`git diff --name-only 19d7d2f90 396e31efe` = 仅 verification | 统一 README/卡面文案：定向 35（不含渲染类）/41（含）；或把渲染类重命名/过滤项并入；Closeout 的「20」改为 35 | open |
| R3-002 | P3 | `SettingsTypographyPanelTests.cs:270-272` | **渲染断言对系统 locale 敏感**：`Assert.Contains("缩放 14")`/`"行高 1.6"` 依赖 `SettingsPageView` 的 `ToString("0.##")`（无 IFormatProvider，用 `CurrentCulture`）；在逗号小数分隔 locale（de-DE 等）机器上会渲染「1,6」而使测试假红。产品显示随 locale 正确，问题在测试可移植性 | 代码 `SettingsPageView.cs:617`；测试 `:271-272`；静态推演 + .NET 格式化语义 | 测试内固定 `CultureInfo.CurrentCulture = zh-CN`（或断言时用同一文化格式化期望串） | open |
| R3-003 | P3 | `SettingsTypographyPanelTests.cs:144-145,170-171,330-331` | **共享 Application 测试卫生**：3 个 headless 测试各自 `new DesignSystemThemeManager(application)` + `Initialize(Dark)`，仅 `Dispose`（只解绑事件），不还原全局 `Resources`/`RequestedThemeVariant`，测试后全局态残留（多份 palette/global provider 累积）。当前全量 858/0/11 通过（本审查复现），但依赖固定测试顺序；后续测试重排/并行化可能暴露顺序依赖 | 代码位置；`DesignSystemThemeManager.Dispose` 语义；全量实测 858/0/11 | 测试内保存并恢复 `Resources.MergedDictionaries`/`RequestedThemeVariant`（或改用局部 ResourceDictionary + 注入 lookup 的测试形态） | open |
| R3-004 | P3 | Lead 指定定向门禁 / `dotnet-typography-final.log` | **定向门禁未覆盖渲染类**：`SettingsTypographyRenderTests` 类虽与 Panel 测试同文件，但 FQN 过滤不含其类名；按本任务给定的定向过滤只跑 35 条，渲染断言（AC1 3 行/占位/样例、AC3 资源不变、R-012 单次读取、IPC 0 命令）只在全量或扩展过滤下执行。全量已覆盖，故非功能缺口，属门禁设计覆盖问题 | gate1=35 vs gate1b=41（§5）；类定义 `SettingsTypographyPanelTests.cs:217` | 定向过滤增加 `FullyQualifiedName~SettingsTypographyRenderTests`，或将该类改名使 `~SettingsTypographyPanelTests` 覆盖（如与文件同名族）；README 同步 | open |
| R3-005 | P3 | 卡面「残余」/README NOT_RUN | **已登记残余（不阻断）**：Host `WritesAllowed=false` 下字体组只读视图测试、真实 Tab 遍历（仅断言 `Focusable=true` 属性，未做键盘遍历）、真实 `FontManager` 独立探测、真实用户主题包经 `ThemeService` 后的投影、UI 截图——均为 NOT_RUN；R-015「按 face 各一行样例」未做（改为标注 Ui 面）；R-011 单 generic 栈无单测。未冒充 PASS | 卡面 `:112`；README「NOT_RUN」5 条；代码/测试位置 | 收口时保留清单；如需，另立卡补 Host 只读视图与真实 Tab 遍历 | open |
| R3-006 | P3 | `doc/tasks/FEA-14-SET-1.md:45,123`；`doc/STATUS.md:7`；`doc/REBASELINE_PLAN.md:51-52` | **治理文档/卡面残余**：卡 H1 仍「（占位）」；STATUS/PLAN 仍写「r1 findings 处置中」；PLAN 的 SET-1 行仍是「READY 节点：无」之后的裸行、未入 DAG 表；`delivery_head`/`canonical_evidence_status` 仍空。卡面已把 STATUS/PLAN/ledger 切换列为 closeout 待办，未冒充完成 | 文件原文；`git diff --name-only caee4c86a 396e31efe` 含 card 但未含 STATUS/PLAN（本增量未刷新） | 收口时统一刷新（H1 去「占位」、STATUS/PLAN 改 r2/r3 处置完成、PLAN 行入表、填 delivery_head 等） | open |

## 4. AC 逐项（不把未实测项记 PASS）

| AC | 判别 | 本审查结果 | 依据/说明 |
|---|---|---|---|
| AC1 投影正确性 | 3 行（token/栈/实际族+缩放行高）；Unavailable → 稳定占位；真实资源路径 | **MET** | 真实资源测试 + 渲染测试（3 行/缩放/行高/样例/占位）通过；独立探针 head 重跑：3 行完整栈、scale=13/12/24、lineHeight=1.45/1.25/1.25 |
| AC2 回退解析纯函数矩阵 | 已装命中 / 全缺失 generic / 空栈 / fallback 标记 | **MET** | 6 条 resolver 测试 + 定向 35/41/全量绿；DSH 裁决落卡且与实现/测试/scope AC2 一致 |
| AC3 零全局副作用 | Resources 引用/值 + Styles 不变；样例字体不外溢 | **MET** | 渲染测试以真实资源对象 `Assert.Same` + Styles 引用序列 + 样例 `NotSame` 断言；本审查 41/41、858/0/11 实测通过 |
| AC4 无 AppData 写入 | 真实 `%APPDATA%\NewManga` 指定 artefact 字节+mtime 不变 | **PARTIAL（指定 artefact NOT_RUN，已如实声明）** | `theme-settings.json` 全量 sha256+size+mtime 前后不变（脚本复现 EXIT 0，`UNCHANGED`）；`presentation-settings.json`/`themes\` 本机不存在 → 卡面/README 记 NOT_RUN，未冒充 PASS |
| AC5 UI/逻辑分离 + 只读门禁 + a11y | VM 构造/搜索/只读/a11y | **PARTIAL（Host 只读视图 NOT_RUN，已登记）** | VM 无 Application 构造、`字体`/`typography.ui` 命中、`Focusable=true` + a11y 名含解析族且被渲染测试断言；Host `WritesAllowed=false` 字体组视图测试未做（NOT_RUN 登记）；真实 Tab 遍历未做 |
| AC6 边界与零契约变更 | diff ⊆ allowed_paths；禁改目录 0；pins 18/18；check PASS | **MET** | 净交付 diff 33 文件全部映射进 16 条 allowed_paths（OUT=0）；禁改目录命中 0；pins 18/18；check 默认 + TaskPath 均 PASS |

## 5. 门禁实测（本审查实际执行）

| # | 命令 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --filter "FullyQualifiedName~TypographyResolverTests\|FullyQualifiedName~SettingsTypographyPanelTests\|FullyQualifiedName~SettingsDraftSyncTests\|FullyQualifiedName~FluentResidualSettingsLeaveTests"` | 09:04:34 → 09:04:41 | **35 通过 / 0 失败 / 0 跳过**（不含渲染类，见 R3-004） | **0** |
| 1b | 同项目 `--filter "...\|FullyQualifiedName~SettingsTypographyRenderTests\|..."`（扩展，覆盖渲染类） | 09:04:47 → 09:04:54 | **41 通过 / 0 失败 / 0 跳过** | **0** |
| 2 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-14-SET-1.md` | 09:05:01 → 09:05:02 | **PASS**（3 warnings：11 非终态 / STATUS 2920 B·29 L 80% / PLAN 6705 B·61 L 80%） | **0** |
| 2b | `pwsh -NoProfile -File tools/governance/check.ps1`（默认） | 09:10:36 → 09:10:37 | **PASS**（同上 3 warnings） | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 09:05:02 → 09:05:03 | **PIN AUDIT: PASS (all 18)** | **0** |
| 4 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj`（全量） | 09:05:13 → 09:10:05（4 m 49 s） | **858 通过 / 0 失败 / 11 跳过 / 869 总计**（与 `dotnet-app-tests-final.log` 一致） | **0** |
| 5 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 09:01:52 / 09:12:04 | 两次均 **clean**；HEAD 两次均 `396e31efe0bb32889a2c6d06862bcd95ea401643` | — |

补充复现（本审查实测，仓外日志）：
- `python tools/generate_api_inventory.py --check` → `1/54/6=61`、`OK: rendered counts match FEA-C07 doc`、**EXIT 0**（09:10:35）。
- `pwsh -NoProfile -File verification/FEA-14-SET-1/scripts/appdata-redline.ps1 -Out <temp>` → 前后指纹一致、`VERDICT: UNCHANGED (no AppData writes)`、**EXIT 0**（09:05:38–09:05:42）；真实 AppData 审查结束时仍只有 `theme-settings.json`（359 B、mtime `2026-10-30T03:00:27Z`）。
- `dotnet test ... --filter "FullyQualifiedName~SettingsTypographyRenderTests.OpeningTheTypographyGroupIssuesNoHostCommands"` → **1 passed / EXIT 0**（09:10:24–09:10:28）。
- 独立 headless 探针（r2 工程对 head 重跑）：3 行完整栈、Data=12/Display=24、zh-CN 与 de-DE 下 lineHeight 均非空、**EXIT 0**（09:05:55–09:05:57）。
- 变异 patch：`git apply --check` M1/M2 均 **EXIT 0**（可应用于 head）；**未重放**（只读纪律，重放会临时改生产源码，见 NOT_RUN）。

## 6. 范围与越界

- 净交付 diff `c4e40509b..396e31efe`：**33 个文件，全部映射进 16 条 allowed_paths（OUT=0）**；禁改目录 `doc/plan/**`、`doc/contracts/**`、`tools/governance/**`、`doc/tasks/FEA-13*` 命中 **0**。
- 增量 diff `caee4c86a..396e31efe`：22 个文件 = 4 个 src（均 allowed）+ 2 个测试文件（Panel 修改、越界 RenderTests 删除）+ 卡面/README/logs/scripts/mutations/r2 报告（均为 allowed 模式）；**唯一 OUT 是删除 `SettingsTypographyRenderTests.cs`**——净交付已归零，历史中间态越界已由 `4b8f2831c` 消除。
- 契约：C-03/C-02/P15/C-07 零字节（pins 18/18、禁改目录 0）；零新增 IPC/Core 命令（API inventory 61 不变）；未改 `IHostController`。
- 只读语义保持：无字体写入/持久化、无 `Application.Styles`/全局资源写入（渲染测试以真实资源对象不变断言）；样例字体仅局部。
- 结论：**无越界**；本审查写域仅 `doc/reviews/FEA-14-SET-1-r3.md`。

## 7. 证据复核（final logs 可复现性）

| 证据 | 本审查核对 | 判定 |
|---|---|---|
| `logs/dotnet-app-tests-final.log`（858/0/11，EXIT 0） | 重跑全量 → 858/0/11，EXIT 0；HEAD 记录为 `19d7d2f90`，与最终 head 差值仅 `verification/**` | 可复现 |
| `logs/dotnet-typography-final.log`（35/0/0，EXIT 0） | 按日志 filter 重跑 → 35，EXIT 0；但 filter 不含渲染类（README 描述失准，R3-001/R3-004）；扩展过滤 → 41 | 计数可复现，描述需修正 |
| `logs/gates-check-final.log` / `gates-pins-final.log` | 默认 + TaskPath 均 PASS/EXIT 0；pins 18/18/EXIT 0 | 可复现 |
| `logs/api-inventory.log` | `--check` EXIT 0、1/54/6=61 | 可复现 |
| `logs/appdata-redline.log` | 脚本 `-Out` 仓外重跑 EXIT 0、UNCHANGED、hash/mtime 与日志一致 | 可复现 |
| `logs/ipc-replay.log`（1 passed） | 单测重跑 1 passed/EXIT 0 | 可复现 |
| `logs/mutations-replay.log`（M1/M2 RED、基线绿） | 两份 patch `git apply --check` EXIT 0，日志失败点与测试行号吻合；**未重放**（见 NOT_RUN） | 部分可复现（apply-check 实测 + 日志静态核对） |
| `logs/typography-fallback.log` | FamilyNames 探针为环境事实；§3 的 20 passed 来自 P3 worktree（中间 run），与 final 35/41 不同源（provenance 混合，R3-001） | 探针事实可信，provenance 需注明 |
| `README.md` AC 表 | AC4「PARTIAL / NOT_RUN」、AC5 Host 只读 NOT_RUN 已如实；但与卡面 AC4/AC5 的 `[x] … <<MET>>` 标注不完全一致（R3-001/R3-006） | 基本如实，需统一表述 |

## 8. NOT_RUN 声明（不得冒充 PASS）

- UI 截图基线 = **NOT_RUN**（README 已声明；本审查未做真实交互式 UI）。
- Host `WritesAllowed=false` 下的字体组只读视图测试 = **NOT_RUN**（卡面/README 已登记）。
- 真实 Tab 遍历落点（仅断言 `Focusable=true` 属性；未做键盘遍历）= **NOT_RUN**。
- 真实 `FontManager` 独立探测 = **NOT_RUN**（README 已声明；生产探测由 headless 真实资源测试覆盖）。
- 真实用户主题包经 `ThemeService` 应用后的投影 = **NOT_RUN**（真实资源测试用 `DesignSystemThemeManager.Initialize` 的 token 层）。
- `%APPDATA%\NewManga` 指定 artefact（`presentation-settings.json`/`themes\`）前后字节 = **NOT_RUN**（本机不存在；全目录指纹前后不变仅覆盖现有 `theme-settings.json`，已如实声明）。
- 变异 M1/M2 完整重放 = **NOT_RUN**（只读纪律；仅 `git apply --check` 实测 EXIT 0）。
- `--theme-home` 临时目录负例 = **NOT_RUN**。

## 9. 残余与收口建议

1. **R3-001**：统一 README/卡面/日志表述——定向 35（不含渲染类）或 41（含）；Closeout「20 passed」改 35；`typography-fallback.log` 注明 20 为 P3 worktree 中间 run；AC4/AC5 在 README（PARTIAL/NOT_RUN）与卡面（`[x]…<<MET（…NOT_RUN）>>`）的标注统一为「MET（带 NOT_RUN 子项）」或「PARTIAL」。
2. **R3-002**：渲染测试固定/显式文化（避免非点号小数 locale 假红）。
3. **R3-003**：headless 测试恢复共享 `Application` 状态（降低顺序依赖）。
4. **R3-004**：定向门禁加入 `SettingsTypographyRenderTests`（或改名使 Panel 过滤覆盖），使渲染断言进入定向门禁。
5. **R3-006**：收口时刷新 STATUS/PLAN/卡面（H1 去「（占位）」、PLAN 行入 DAG 表、填 `delivery_head`/`canonical_evidence_status`/`integration_commit`）——卡面已登记为待办，不阻断本次 approved。
6. R3-005 的 NOT_RUN/残余保持清单；如需补测另立卡（不扩本卡写域）。

## 10. 审查者声明

本报告由未参与 FEA-14-SET-1 实现/返修的独立上下文子 agent 出具（同一审查子 agent 续接 r2，r2 报告为本审查者上一轮产出、不构成对实现的参与）。本审查只读，唯一写入为本文件；所有 PASS 均由本次实测或已核对的可复现日志支撑，静态推演已显式标注；未把 NOT_RUN 记为 PASS。
