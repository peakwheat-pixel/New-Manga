---
task_id: READER-F11-STYLE-SCOPE-1
reviewer: reviewer-f11s
reviewer_kind: subagent
author: DSH
base_commit: null
reviewed_head: d511876d1
decision: ACCEPTED_WITH_FINDINGS
---

# Review：READER-F11-STYLE-SCOPE-1（F11 沉浸窗补 V2LocalStyles 作用域）

- **reviewer**：`reviewer-f11s`（DSH 子 agent，**独立上下文**；未参与 `READER-F11-STYLE-SCOPE-1` 的实现、取证或收口）。
- **reviewed_head**：`d511876d1`（`d511876d18dc5d80326ad7947f7904b286dff00b`，main）。
- **审查时间**：2026-11-17 20:48（+08:00）。
- **环境**：Windows 11 专业版 10.0.26300.9711（`cmd /c ver` + `Win32_OperatingSystem` 实测）；DPI 96（`AppliedDPI=96`、`GetDpiForSystem()=96`）；`PrimaryScreen = 2560×1440`（`[System.Windows.Forms.Screen]::PrimaryScreen.Bounds` 实测，与 RTX 5070 Ti 输出分辨率一致）；真实桌面会话（`query session` → `console` ID 1 **Active**，`[Environment]::UserInteractive=True`）。
- **HEAD 说明**：审查过程中 main 由 `d511876d1` 前进到 `8f342d01`（`docs(handoff): STARTER R22`，仅改 `doc/handoffs/NEXT-SESSION-STARTER.md`，`git diff --stat d511876d1 8f342d01` = 1 file / +54 / −1，**无代码、无证据、无 Gate 文档变化**）。本 Review 的判定只对 `reviewed_head: d511876d1` 有效；代码 delta 与 `8f342d01` 下完全相同。

## 结论摘要

**ACCEPTED_WITH_FINDINGS**：修复本身**成立**——改动最小、只影响 `ImmersiveReaderWindow`，且在**我自己的 Debug 构建 + UI Automation 实跑**下复现出文档声称的像素变化；回归 6/6 通过；Gate 与条件 3 结论未被改动。发现项均为 P2（卡片/证据**文档精度**与测试副作用），不阻塞接受。

| # | 必测项 | 判定 | 一句话依据 |
|---|---|---|---|
| 1 | 改动最小且正确 | **PASS** | `d511876d1` 的 C# diff 只有 `+using` 与 `+Styles.Add(new StyleInclude(...))`（+11/−0）；`V2LocalStyles.axaml` 字节未动；无其它页面/空间的样式引入变化 |
| 2 | 真的修好了 | **PASS** | 自建 Debug 构建 0 warn/0 err；自跑 UIA：点 `阅读` → F11 → 整屏截图，顶带 `(600,20)=(255,255,255)`、底带 `(300,1410)=(255,255,255)`、`(600,60)=(255,255,255)`；修复前对照为 `(244,243,239)`（画布色） |
| 3 | 回归 | **PASS** | `--filter ImmersiveReader|ReaderOverlay` → **6 passed / 0 failed / 0 skipped**，`TEST_EXIT=0` |
| 4 | 证据诚实性 | **PASS**（含 P2 精度项） | README 明写「**Debug 构建**、**已发布产物仍是修复前行为**」；3 个 sha256 与卡面 Canonical Evidence 逐字一致；修复前对照明确指向 `c3-06` |
| 5 | 卡片状态 | **PASS**（含 P2） | `check.ps1` → `Governance check: PASS (3 warnings)`，`CHECK_EXIT=0`；`closed_with_limitations` 恰当，**不应**改 `done`（理由见 §5/§7，相关文档项见 F-01） |
| 6 | 不得越界 | **PASS** | 提交只含 1 个源码文件 + 4 个文档（任务卡 / REBASELINE_PLAN / STATUS / TASK_LEDGER）；`Technical Gate=NOT_SATISFIED`、条件 3 关闭口径、Gate 六条映射**均未改** |

## 1. 改动最小且正确

`git show d511876d1 -- apps/desktop-avalonia/src/NewManga.App/Shell/V2/ImmersiveReaderWindow.cs`：

```diff
+using Avalonia.Markup.Xaml.Styling;
...
+        // READER-F11-STYLE-SCOPE-1: ...
+        Styles.Add(new StyleInclude(new Uri("avares://NewManga.App/"))
+        {
+            Source = new Uri("avares://NewManga.App/Views/V2/Shell/Theme/V2LocalStyles.axaml"),
+        });
```

- `git show --name-only d511876d1` 共 5 个文件：`ImmersiveReaderWindow.cs`、`doc/tasks/READER-F11-STYLE-SCOPE-1.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/TASK_LEDGER.md`。**没有** `V2LocalStyles.axaml`，也没有任何其它 `.axaml` / 页面 / 空间样式文件。
- `git diff 9581336ae d511876d1 -- apps/desktop-avalonia/src/NewManga.App/Views/V2/Shell/Theme/V2LocalStyles.axaml` 输出 0 行；`V2LocalStyles.axaml` 的 mtime 仍为 2026/10/30 02:19:49（与修复前一致）。
- 现有 `V2LocalStyles.axaml` 引入点仍只有两处 XAML：`AppShellV2.axaml:16`、`ThemeStudioView.axaml:19`（递归 `Select-String` 实测）；本次新增的是**代码构造窗口自己的 `Styles` 集合**，不与 AppShellV2 共享作用域，因此不存在同一 scope 内重复加载。
- `StyleInclude` 的 `Source` 路径与磁盘文件一致（`apps/desktop-avalonia/src/NewManga.App/Views/V2/Shell/Theme/V2LocalStyles.axaml`，15,762 B）；运行结果证明 URI 可解析（见 §2）。

## 2. 修复有效性（自建构建 + 自跑真实窗口）

### 2.1 构建

```
dotnet build apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Debug
→ 已成功生成。0 个警告 0 个错误；BUILD_EXIT=0；用时 10.92 s
（NewManga.App.dll 2026/11/17 20:22:59，sha256 9F6FCDBD…806AD5）
```

### 2.2 界面取证（我自己跑，不是复读文档）

- 启动：`src/NewManga.App/bin/Debug/net9.0/NewManga.App.exe`
  `--data-root "<BOOK-FIXTURE-1/isolated-data 的副本>" --sidecar-dir "<INSTALLER-MATRIX-1 stage>/app/core-sidecar" --log-dir "<workspace logs>"`。
- **操作**：UI Automation 精确按名查找 `ControlType=Button, Name='阅读'`（实测 rect `814,239,42,30`）→ `InvokePattern.Invoke()` → 等 8 s → 主窗口置于前台（`GetForegroundWindow()` 校验 = 目标 hwnd）→ `SendKeys('{F11}')` → 等 8 s → `PrimaryScreen.Bounds` 整屏截图（2560×1440 PNG）。
- 结果图可见：无边框全屏、页面内容、顶部 `返回（Esc）`/面包屑/`分页`/`Webtoon 纵向`/`RTL`、底部 `上一页`/`下一页`/`第 1 / 8 页 · 0%`/`进度：续读到第 1 页（Core 已保存）`。UIA 在该帧找到三个模式 chip 的屏幕矩形（x≈2372…2552, y≈6…36），与整屏 overlay 一致。
- **操作说明**：本环境里 `Start-Process`（ShellExecute 路径）会挂起，因此启动改用 `[System.Diagnostics.Process]::Start(ProcessStartInfo{UseShellExecute=false})`；参数与任务书完全一致。这只影响**启动方式**，不影响被测二进制与像素结论。
- 辅助（画布基线）另跑一次并取主窗口资料柜页：`(600,700)=(244,243,240)`、`(100,700)=(244,243,240)`，即 **同一 Debug 构建的画布确为 `#F4F3F0`**（不是白色）。该次尝试按 F11 未取得前台（`foreground=False`，overlay 未打开），仅用于画布基线，不作为修复证据。

### 2.3 像素实测（原生像素，PNG 无损）

| 取样点 | 我实测（Debug @ d511876d1） | 仓内「修复后」JPG | 仓内「修复前」`c3-06` JPG | 文档值（README） |
|---|---|---|---|---|
| 顶带 `(600,20)` | **`(255,255,255)`** | `(255,255,255)` | `(244,243,239)` | 修复后 `(255,255,255)` / 修复前 `(244,243,240)` |
| 底带 `(300,1410)` | **`(255,255,255)`** | `(255,255,255)` | `(244,243,239)` | 同上 |
| `(600,60)`（README 记为「画布」） | **`(255,255,255)`** | `(255,255,255)` | `(255,255,255)` | 不变 `(255,255,255)` |
| 补充 `(1800,20)` | `(255,255,255)` | `(255,255,255)` | `(244,243,239)` | 修复后白 |
| 补充 `(1200,1430)` | `(255,255,255)` | — | — | — |
| 整带统计：顶带 y0–39 | 95.37% 纯白 | 85.14% 纯白（JPEG） | 87.88% `#F4F3EF` | — |
| 整带统计：底带 y1408–1439 | 87.72% 纯白 + 10.42% `#ECEAE5` 轨道 | 65.94% 纯白 + 轨道色 | 69.90% `#F4F3EF` + 轨道 | — |
| 模式 chip `Webtoon 纵向` 填充 | **`(242,236,227)`** | JPEG 噪声分散，最高频色仅 5.38%（`(243,236,226)` 一带） | `(242,241,237)`（41.47%，无填充 ≈画布） | 「无 Accent 高亮 → Accent 高亮」 |

**判别力分析**（回答「白色会不会本来就是画布」）：

1. 同一构建的画布实测为 `#F4F3F0=(244,243,240)`（§2.2 辅助运行），不是白色；
2. 修复前对照 `c3-06` 的顶/底带正是 `(244,243,239)`（JPEG 对 `(244,243,240)` 的正常 1 LSB 偏移），且其 `(2,2)` 角像素为画布色——正是「`topband` 透明 ⇒ 露出 `ReaderOverlay` 根 Grid 的 Canvas 背景」的表现；
3. 修复后我的两张同点（含角点 `(2,2)`）均为 `(255,255,255)`，即 `Nm.Color.Bg.Panel`（`Tokens.Light.axaml`：`#FFFFFFFF`）；
4. `Button.chip.on` 的 `Background` 是 `Nm.Color.Accent.Muted = #1F96651A`（12.2% alpha）。按 over-white 合成：`242.2 / 236.2 / 227.1` → 实测 `(242,236,227)` **逐通道吻合**，证明是 `V2LocalStyles` 的 chip 规则生效，而不是默认 Button 样式。
5. 结论：顶/底带的白色来自 `Border.topband` / `Border.statusband` 的 Panel 画笔，不是画布或页面卡片；本次修复**可判别、可复现**。

### 2.4 收尾

- 截图/日志/JSON 全部写在 `G:\CODEX\New Manga.workspace\task-envs\READER-F11-STYLE-SCOPE-1\reviewer-f11s\`（**未写入仓库**）：
  - `shots/rf11s-review-02-after-f11.png`（sha256 `AB197D76…F980621F`，修复后 F11 整屏）
  - `shots/rf11s-review-01-inwindow.png`（sha256 `BEAB1327…B1E7C72A8`，主窗口内阅读器）
  - `shots/rf11s-review-04-f11-empty.png`（sha256 `989DF381…0FF82B83`，画布基线，非 F11）
  - `shots/uia-result.json`、`shots/step2-progress.log`、`logs/startup.log`
- 运行结束后 `Get-Process -Name 'NewManga*'` 计数 **0**；`git status --porcelain` 在写本报告前为**空**。

## 3. 回归

```
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Debug --no-build \
  --filter "FullyQualifiedName~ImmersiveReader|FullyQualifiedName~ReaderOverlay"
→ 已通过! - 失败: 0，通过: 6，已跳过: 0，总计: 6，持续时间: 2 s；TEST_EXIT=0
```

与卡面/README 记录的「6 passed / EXIT=0」一致。

## 4. 证据诚实性（README 与卡面核对）

- **Debug 限制**：README §「边界（重要）」第 1 条**明确**写「**本证据来自 Debug 构建**」且「**已发布产物（stage / setup.exe）仍是修复前的行为**；要让安装包带上本修复，需重新 publish + 打包（不在本卡范围）」。该限制不含糊。
  - 事实核对：stage 的 `NewManga.App.exe` 构建时间 **2026-11-15 04:56:57**、sha256 `A3EC2133…739230`（与条件 3 README 登记的发布产物同一字节），**早于**修复提交 `d511876d1`（2026-11-17 20:20）⇒「已发布产物仍是修复前行为」成立。
- **sha256**：实测 `README.md FEFEBA92…7504DB`、`rf11s-01-after-f11.jpg BD9751DC…FD98BE3`、`rf11s-02-after-inwindow.jpg B7F6BBCE…C5A82DC7`，与卡面 Canonical Evidence 三行**逐字一致**。
- **修复前对照**：README 明确指向 `verification/MAINT-1-RELEASE-MONITOR/condition3/c3-06-f11-immersive-content.jpg`，实测其 sha256 = `8CE0FC0A…DAE15535`，与 README 的 `8ce0fc0a…5535` 前缀一致。
- 与我的独立实测交叉：修复后三点全白、修复前两点画布色、chip 填充恢复——与 README 判别表一致。
- **精度问题（P2，见 F-02）**：README/卡面把 `(600,60)` 标为「画布」。该点实际落在页面 `Border.raised` 的白色内边距上（修复前后都白），不能证明「画布不变」。真正的画布证据是修复前 `(2,2)` 为 `#F4F3F0`、修复后同点为 `#FFFFFF`（顶带覆盖），以及本次辅助运行的主窗口 `#F4F3F0`。

## 5. 卡片状态

```
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/READER-F11-STYLE-SCOPE-1.md
→ WARN ×3（2 个非终态 Task；STATUS 80% 预算；REBASELINE_PLAN 80% 预算）
→ Governance check: PASS (3 warnings)；CHECK_EXIT=0
```

写本报告后复跑同一命令，结果不变（`PASS (3 warnings)`，`CHECK_EXIT=0`）。

**`closed_with_limitations` 是否恰当：是。**

- 证据只覆盖 **Debug 构建**；**用户实际安装的 v0.1.1 产物仍是有缺陷的版本**（上述字节时间可证），修复要进安装包必须重新 publish + 打包，本卡明确未做 ⇒ 这不是「已交付完成」，不能写 `done`。
- 未覆盖面（深色主题同组对照、分页模式 chip、缩放/DPI）已逐条写在卡面「限制」与 README；`closed_with_limitations` 正好表达「缺陷已修、验证有界、发布未带」。
- 卡面 `AC1…AC5` 的 `<<MET>>` 与 Closeout Record 与我的实测相符。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| F-01 | P2 | `doc/tasks/READER-F11-STYLE-SCOPE-1.md:18` | `delivery_head: 9581336ae` 指向的提交**不含修复代码**（`git show 9581336ae` 仅 README + 2 JPG；取出 `git show 9581336ae:apps/desktop-avalonia/src/NewManga.App/Shell/V2/ImmersiveReaderWindow.cs` 后检索 `StyleInclude` 得 0 行）。实际交付修复的是 `d511876d1`。会影响后续按 `delivery_head` 追溯的审计者。 | `git show --name-only 9581336ae`；上述 `git show <commit>:<path>` 的 `StyleInclude` 检索 = 0 | 把 `delivery_head` 更新为 `d511876d1`（或同时记录 `evidence_commit: 9581336ae`），不改任何已入库证据字节 | open |
| F-02 | P2 | `verification/READER-F11-STYLE-SCOPE-1/README.md:34`；任务卡 `:107` | 把 `(600,60)` 标为「画布」不准确：该点属于页面 `Border.raised` 白色内边距（修复前后同为 `(255,255,255)`），不能支撑「画布不变」。真正可判别的画布点是 `(2,2)`（修复前 `#F4F3F0`、修复后 `#FFFFFF`）。 | 本次实测 `c3-06 (2,2)=(244,243,239)`、`rf11s-01 (2,2)=(255,255,255)`；同一构建主窗口 `(600,700)=(244,243,240)` | 下轮修文档时更正为「页面卡片内边距」或用 `(2,2)`/空态中心点作画布证据；不改结论 | open |
| F-03 | P2 | `verification/READER-OVERLAY-HEADLESS-PNG-1/render-info.md` | 任务书要求的回归 filter 命中 `ImmersiveReaderVisualEvidenceTests`，该测试把本文件**改写**（`渲染 HEAD` 变为当前 head，并删掉「全量测试回归确认」一节），使工作区出现非预期修改。这是既有 `GOV-TEST-SIDE-EFFECT-1` 的已知副作用，与本次修复无关。 | 运行测试后 `git status --porcelain` 出现 ` M verification/READER-OVERLAY-HEADLESS-PNG-1/render-info.md`；我执行 `git checkout -- <该文件>` 恢复，之后 `git status` 为空 | 本卡不需处理；建议 `GOV-TEST-SIDE-EFFECT-1` 按原计划修复测试输出目录；证据运行流程应显式记录「测试后恢复」步骤 | open（既有卡） |

P0 = **0**；P1 = **0**；P2 = **3**（均为文档/流程精度项，不涉及修复正确性）。

**范围外观察（不计入本 head 判定）**：`8f342d01` 的 `NEXT-SESSION-STARTER.md` 中「当前 head：`234b316b6`」仍旧，且同一提交里既有「非终态卡（3 张）…`READER-F11-STYLE-SCOPE-1`（`proposed`）」又有「R22 收尾追加…已修复并收口」——同一文件内自相矛盾。属 `d511876d1` 之后的新文档，建议 DSH 顺手校正。

## 6. Gate 与条件 3 边界

- 提交 `d511876d1` **未触碰**任何 Gate 判据文档（`doc/reviews/RELEASE-GATE-DISPOSITION-2026-11-15.md`、`RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md`、条件 3 三份裁定均不在改动清单）。
- 现状核对（HEAD 文档）：`doc/STATUS.md` 仍为 **`Technical Gate=NOT_SATISFIED`**、`Release Gate BLOCKED`；条件 3 仍写「**3 份独立裁定关闭**（非人眼；限制见 `MAINT-1`）」。
- 条件 3 关闭依据文档只把本卡作为「已单独立卡的外观缺陷，**不影响**结论」引用（`RELEASE-GATE-SIX-CONDITIONS:145`、`MAINT-1:444-445`），没有把本卡当条件 3/4 的证据。本修复也没有被写成 Gate 通过理由。
- 因此：**Gate 判定与条件 3 关闭结论均未被本次改动改变**。

## 7. 明确回答

- **该修复是否成立？** **成立。** 单点、可回退（`Styles.Add` 一行语义），只给代码构造的沉浸窗补同一份局部样式作用域；独立构建 + 独立 UIA 实跑复现了「顶/底带 `(244,243,240)` → `(255,255,255)`」与 chip 的 Accent.Muted 填充；回归与治理检查均通过。
- **能否保持 `closed_with_limitations`？** **能，且应当保持。** 修复只在 Debug 构建中验证，`stage/setup.exe`（2026-11-15 构建）仍是修复前行为；深色主题、分页模式 chip、缩放/DPI 未覆盖。写成 `done` 会把「安装包未带修复」说成已完成，属过度声明。保持 `closed_with_limitations` 并先处置 F-01/F-02（纯文档）即可。

## 8. 声明与剩余风险

- **本复核不构成产品发布验收。** 它只对 `reviewed_head: d511876d1` 的代码/文档/证据做独立复核，不代表 Release Gate 通过、不代表安装包验收、也不替代人眼视觉验收或环境矩阵。
- 我使用的是 **Debug 构建**；结论不外推到 `stage/setup.exe` 或重新打包后的产物（后者需重新 publish + 打包 + 复跑本组取证）。
- 未覆盖：深色/高对比主题下的同组对照、分页模式下的 chip 高亮、非 100% 缩放/HiDPI、主题切换过程中的瞬时状态、`StyleInclude` 的启动开销测量（量级可忽略但未测）。
- 我未修改仓库源码/已入库证据；唯一新增写入是本报告。本次要求的回归命令产生的既有测试副作用（F-03）已用 `git checkout --` 恢复到 HEAD 字节，`git status --porcelain` 在写报告前为空；写报告后仅本文件为 `??`（未提交，符合「不得提交」约束）。
