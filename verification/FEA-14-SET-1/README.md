# FEA-14-SET-1 证据索引（字体只读投影 · 窄化口径）

- Task：`FEA-14-SET-1`（设置页「字体」组 = 只读投影 + 回退解析 + 本地样例预览）
- Base：`c4e40509b`（scope 冻结点）；scope 依据 `doc/reviews/FEA-14-SET-1-scope-r1.md`（窄化口径 = READY-TO-FREEZE）
- 交付链：`64c32fa47`（首版+证据）→ `a0e59ac3b`（r1 处置）→ `caee4c86a`（r1 P2 判别力）→ `4b8f2831c`（P3 清理）→ `b0d5c7d6a`（r2 处置；本目录日志的 head）
- 契约：C-03/C-02/P15/C-07 **零字节变更**（不提供字体选择/持久化；那需 UNFREEZE，另立卡）
- 日期：2026-11-10

## 结论状态

| AC | 判别 | 结果 |
|---|---|---|
| AC1 投影正确性 | 注入 source → 3 行（token/栈/实际族+缺失/缩放行高）；未初始化 → 稳定占位；真实资源路径 | **PASS**：真实 `ResourceDictionary` 下 `TheSourceProjectsTheRealThemeResources`（3 行、完整栈、scale/lineHeight 非空、Data=12/Display=24）；渲染侧 3 行/缩放/行高/样例/占位分支断言 |
| AC2 回退解析纯函数矩阵 | 已装命中 / 全缺失回退 generic / 空栈不伪造 / fallback 标记 | **PASS**：`TypographyResolverTests` 6 条；fallback 语义按 DSH 裁决（见卡面「r1 处置裁决记录」）；具体矩阵见 `logs/typography-fallback.log` |
| AC3 零全局副作用 | `Application.Resources[Nm.FontFamily.*]` 引用/值与 `Application.Styles` 不变；样例字体不外溢 | **PASS**：`RenderingTheTypographyGroupDoesNotMutateGlobalResourcesOrStyles` 用真实 token 资源对象 `Assert.Same` + Styles 引用序列相等 + 样例 `FontFamily` 局部（`NotSame` 全局对象） |
| AC4 无 AppData 写入 | 真实 `%APPDATA%\NewManga` 指定 artefact 字节+mtime 不变 | **PARTIAL / NOT_RUN（指定 artefact）**：`logs/appdata-redline.log` 记录真实目录全量 sha256+size+mtime 前后一致（现仅 `theme-settings.json`，359 B，mtime 保持 2026-10-30）；AC4 指定的 `presentation-settings.json`/`themes\` 本机**不存在** → 对这两个对象记 NOT_RUN，不冒充 PASS |
| AC5 UI/逻辑分离 + 搜索 + 只读 + a11y | 无 Avalonia `Application` 构造 VM；`字体`/`typography.ui` 命中；只读态；a11y | **PASS**：VM 无 Application 构造、搜索命中、只读态；投影行 a11y 名称含解析族、`Focusable=true`（Tab 落点）；Host `WritesAllowed=false` 的视图测试仍 **NOT_RUN** |
| AC6 边界与零契约变更 | diff ⊆ allowed_paths；禁改目录 0；pins 18/18；check PASS | **PASS**：r2 指出 `caee4c86a` 新增渲染测试文件越界，P3 已把渲染测试并入 allowed 的 `SettingsTypographyPanelTests.cs` 并删除该文件；交付链 diff 全部落入 16 条 allowed_paths（含 `doc/reviews/FEA-14-SET-1-*.md`、`verification/FEA-14-SET-1/**`）；主树 `verify_pins` 18/18、`check.ps1`（默认 + `-TaskPath`）PASS；禁改目录命中 0 |

## 门禁与证据（本目录）

| 日志 | 内容 | EXIT |
|---|---|---|
| `logs/typography-fallback.log` | FamilyNames 真实行为探针 + 环境头 + 定向 20 passed + 真实 FontManager 独立探测 NOT_RUN 声明 | 0 |
| `logs/appdata-redline.log` | 真实 `%APPDATA%\NewManga` 全量 sha256/size/mtime 前后一致（`UNCHANGED`） | 0 |
| `logs/ipc-replay.log` | 字体组切换/渲染期间 `FakeHostController` 命令计数增量 0（1 passed） | 0 |
| `logs/api-inventory.log` | `python tools/generate_api_inventory.py --check`（1/54/6=61） | 0 |
| `logs/mutations-replay.log` | M1/M2 patch 重放：各 2 failed（RED），复原后 6 passed | 0 |
| `logs/dotnet-app-tests-final.log` | **主树交付 head 全量 App.Tests：858 passed / 0 failed / 11 skipped（869 total，EXIT 0）** | 0 |
| `logs/dotnet-typography-final.log` | **主树定向 35 passed / 0 failed**（TypographyResolver + Panel/Render + SettingsDraftSync + FluentResidualSettingsLeave） | 0 |
| `logs/gates-check-final.log` / `logs/gates-pins-final.log` | **主树** `check.ps1`（默认 + `-TaskPath`）PASS（3 warnings：11 非终态/STATUS 80%/PLAN 80%）；`verify_pins` **PIN AUDIT: PASS (all 18)** | 0 / 0 |

> 说明：全量 App.Tests 与治理门禁的最终证据在**主树交付 head** 上生成并记录（`*-final.log`）；worktree 中的全量运行不作为证据（worktree 会改变若干路径敏感测试的仓库根探测结果）。

## 变异（`mutations/`）

| 变异 | 判别 | 结果 |
|---|---|---|
| M1 缺失族不记录（回落变不可见） | `TypographyResolverTests` | **RED**（2 failed / 4 passed，EXIT 1） |
| M2 投影直接取栈首（不做探测） | `TypographyResolverTests` | **RED**（2 failed / 4 passed，EXIT 1） |

- 可复现：`mutations/M1-missing-not-recorded.patch`、`mutations/M2-stack-head-not-resolved.patch`、`mutations/replay-mutations.ps1`（apply → 测试 → `git checkout --` 复原 → 校验干净）。
- 复原后定向 6 passed（replay 脚本内基线步骤，EXIT 0）。

## 实现要点（含 r1/r2 处置）

- `TypographyResolver`：纯函数；逐段判断本机安装 → 首个已装为实际使用族，缺失段按序记录；**fallback = 解析族之前至少一段缺失**（仅落到 generic 尾巴不算 fallback，DSH 裁决 2026-11-10，卡面有记录）；全缺失回退 generic tail。
- `AvaloniaTypographySource`：只读 `Nm.FontFamily.Ui/Data/Display`；`FamilyNames` 取**完整栈**（不是首族）；资源数值 typed 化并按 InvariantCulture 格式化（locale 无关，de-DE 不再丢行高）；face→size 对齐 `ThemeTokenBaseline.LineHeightTiers`（Data→`Nm.FontSize.Sm`=12、Display→`Nm.FontSize.Xxl`=24、Ui→`Nm.FontSize.Md`）；部分 token 缺失 → `Available=false` + 缺失清单原因（R-010）；**不写资源/样式/设置**。
- `SettingsViewModel`：组合根注入 `AvaloniaTypographySource`；`ReadTypographySnapshot()` 每轮渲染只读一次（R-012），外观 canonical 变化时失效缓存。
- `SettingsPageView.BuildTypographyGroup`：3 行投影 + 缩放/行高 + 未初始化/部分缺失占位 + 三种样例预览（标注使用 `Nm.FontFamily.Ui` 实际字体，字体只设在样例控件）+「字体族属于视觉主题」文案；投影行 a11y 名称含解析族且为 Tab 落点。
- **不提供**字体选择/持久化：字体族归视觉主题（Theme Studio 是唯一写者；Fluent 无 Theme Studio = 已知 limitation）。

## NOT_RUN（不得记 PASS）

- **UI 截图基线 = NOT_RUN**：本机无被审查的交互式 Avalonia 渲染会话；交互由 headless 渲染测试覆盖；FEA-15 可在真实 UI 环境补。
- **真实 FontManager 独立探测 = NOT_RUN**（见 `logs/typography-fallback.log` §4）；生产探测路径由 headless 真实资源测试覆盖。
- **`%APPDATA%\NewManga` 指定 artefact（`presentation-settings.json` / `themes\`）= NOT_RUN**：本机不存在这两个对象；仅 `theme-settings.json` 有基线（前后不变）。
- **Host `WritesAllowed=false` 下的字体组只读视图测试 = NOT_RUN**（只读门禁由组内零写控件与 `DisableWriteControls` 的既有测试覆盖）。
- **真实用户主题包经 `ThemeService` 应用后的投影 = NOT_RUN**（真实资源测试用 `DesignSystemThemeManager.Initialize` 的 token 层，未启动用户主题包应用链）。

## 复现

```powershell
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --filter "FullyQualifiedName~TypographyResolverTests|FullyQualifiedName~SettingsTypographyPanelTests|FullyQualifiedName~SettingsTypographyRenderTests"
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-14-SET-1.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
python tools/generate_api_inventory.py --check
pwsh -NoProfile -File verification/FEA-14-SET-1/scripts/appdata-redline.ps1
pwsh -NoProfile -File verification/FEA-14-SET-1/mutations/replay-mutations.ps1
```
