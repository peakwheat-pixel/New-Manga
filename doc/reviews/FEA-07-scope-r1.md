---
task_id: FEA-07
reviewer: codex-cli
reviewer_kind: agent
author: dsh-lead
base_commit: 682fe17ae94ddce5740aa0a2a4a74bde19057024
reviewed_head: e9d542ab47ced7a0041d145c3b1061de316482a8
decision: changes_requested
counts:
  P0: 0
  P1: 6
  P2: 2
---

# FEA-07 Scope Review r1

## Reviewer 与范围

- **Reviewer**：Codex CLI 独立 fresh session，模型 `gpt-6-luna`；由 DSH 派发。此次只读审查，未参与 FEA-07 起草、范围处置或实现，也不会实现 FEA-07。
- **被审对象**：main 的 `e9d542ab47ced7a0041d145c3b1061de316482a8`；review base 为 `682fe17ae94ddce5740aa0a2a4a74bde19057024`。行号均按被审 head 实测。
- **审查边界**：审查范围充分性、可执行性和契约/治理一致性；不审未编写的实现，也不评判设计数值本身。不得为放行降低现有判据。

## 结论

**Decision: `changes_requested` — P0 0 / P1 6 / P2 2。** FEA-07 当前还不能冻结为 `ready`。主题是可实现的：现有 App composition root、Host、两个壳和 Appearance writer 可作为接线基础，Task 也覆盖了新增 Presentation 模块；但当前写域不能把新模块接入 App，若干 AC 没有覆盖来源方案中的数据保护、窗口事务和混合 DPI 判据，W-6 与性能最终门槛也还不能机械判定。

## Findings

### P1-1 — 新模块无法在授权写域内接入 App

Task 允许新增 `NewManga.Presentation.Avalonia` 并登记到 solution，但没有允许修改 `apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj`。App 项目通过该文件中的 `ProjectReference` 接入 ApplicationCore、Host、Appearance 和 DesignSystem（该文件第 37–43 行）；新 Presentation 模块必须由 composition root 消费，单独加入 `.sln` 不会建立 App 到 Presentation 的编译引用。按当前 `allowed_paths`，Owner 无法完成生产接线。

**最小修订**：将 `NewManga.App.csproj` 明确加入写域；只添加指向新 Presentation 项目的引用，不改既有依赖方向或既有 TFM。

### P1-2 — A03 与切换事务的回滚验收不足

AC1 将 A01/A02/A03/A05 合并为“旧结果仅 candidate、失败保留旧 UI 与未保存状态”等断言，但 A03 明确要求在运行中修改草稿、译文、Lock 或恢复 revision 后让旧结果到达，并检查持久化文本、指针和文件。当前 AC 没要求验证这些内容和保护指针保持不变，也没有明确检查 unknown/stale result 不写回。AC3 对 A06 覆盖了 interrupted 不自动执行和步骤可追溯，却未验证暂停期间配置/source/Lock 变化后采用最新保护状态。

此外，方案 §15.5 给出的切换提交判据（完整 layout/Loaded/Render 回调/有效几何后才 commit）、逐阶段注入失败，以及恢复 window 材质、bounds、焦点、输入路由和旧资源，没有落到 AC1–AC3。只断言“失败保留旧 UI”不足以让这些要求可机械验收。

**最小修订**：在 AC1/AC3 加入 A03/A06 的合成夹具和可观察断言，明确检查 DB 文本、current/pinned revision、Lock、源文件及 candidate；将 §15.5 的每阶段失败注入、commit 判定与完整 rollback 结果纳入 AC/测试矩阵。

### P1-3 — A08/H2 未完整承接冻结的双屏、拔屏和 DPI 行为

AC5 有原生双屏验收、换主屏、拔副屏和“不可浮动则安全停靠”，AC1 也检查主窗标识；因此 H2/H3 纳入本 Task 而不另拆 Task 在结构上可行。但现有判据没有完整承接方案 §7.3、§12.3 A08、§15.5 和 `04-layout-responsive.md` §4/§5：

- 设计基线要求 DPI 为 **100/125/150/200%**；任务测试行只列 100/150/200%。
- 拔屏时第二窗口内容须回到主窗对应页面，未 flush 编辑态须 fail-closed 留在主窗缓冲；现有 AC 未明确这两个结果。
- 第二窗口只能承载只读或独立会话内容，同一 `(SessionId, RegionId)` 草稿保持单一写入 owner；AC5 未约束这一点。
- H2 的“稳定 Window + 内容替换”、混合 DPI/拔屏时各 Window 的提交/恢复，以及发布 manifest 实际启用 PerMonitorV2，均没有明确 AC 或证据项。

AC6 已纳入 H3 的 p50/p95/峰值、冻结时长、内存与句柄 baseline；但 W-5 同时把最终 p95 门槛留给 DSH 在范围冻结时确认，故该部分尚未达到可放行状态（见 P1-6）。

**最小修订**：逐项补齐上述冻结场景和 DPI 档位；继续要求原生桌面证据，不能用 headless 结果替代。A15 的完整真实业务链属于 FEA-15，不应因此扩大 FEA-07；本 Task 仍须验证合成数据下 Host/Session/Run 不因切换变化。

### P1-4 — 测试矩阵没有完整绑定隔离与兼容启动判据

Task 已禁止真实漫画、真实 `%APPDATA%` 和真实用户数据，W-2 也正确要求双屏/DPI 使用原生桌面证据。但 AC1–AC4 测试行只指向 `NewManga.App.Tests` 和 sidecar 环境变量，没有说明 switch journal 与 Appearance 设置目录如何注入隔离临时目录；仅 AC5 明写 `--data-root` / `--theme-home`。此外，新建的 `NewManga.Presentation.Avalonia.Tests` 没出现在 AC1–AC4 的测试命令中。

W-1 要求 `--shell=legacy`、`--frontend` 与 Current V2 不退化，但 AC7 只写“全量回归”，没有列出启动兼容矩阵。现有 `FrontendSelector.Select` 保留显式 `--frontend` 优先级及未知 ID 回退 Current V2；`App.axaml.cs` 也先处理 legacy 模式，再选择 Fluent/Current V2。此处属于已冻结语义，应有精确回归证据。

**最小修订**：AC1–AC4 明确所有 data/theme/journal 路径均落在测试临时根且断言不触真实 `%APPDATA%`；测试命令覆盖 App 与新 Presentation 测试项目；AC7 明列默认 Current V2、`--frontend` 覆盖/未知值 fallback、`--shell=legacy` 的启动回归，并记录 pass/fail/skip 与当前 1034/0/57 基线比较。不得以 NullHost 或真实漫画夹具替代相应验收。

### P1-5 — W-6 依赖方向只有文字约束，没有机械门禁

W-6 列出 Presentation 可引用的层，并禁止 Host/Core/ApplicationCore 引用 Presentation/UI；但验收表没有 project-reference graph 检查。编译通过不能证明禁止边没有形成，也不能证明既有项目 TFM/引用方向未变。

**最小修订**：在 AC7 增加可重复的静态检查或架构测试，解析 solution 中各项目 `ProjectReference` 并按允许/禁止边断言；同时断言现有项目 TFM 未变。该检查应允许 App 引用 Presentation，并拒绝 Host/Core/ApplicationCore 指向 Presentation/UI。

### P1-6 — W-5 的性能通过门槛尚未冻结

AC6 写了候选预算 `p95 ≤1s`，W-5 又规定最终门槛由 DSH 在范围冻结时确认，并要求记录机器、规模、冷热和峰值。AC6 的性能报告字段基本充分，但候选预算是否就是 pass threshold、超预算的处置是否会阻断 AC，仍未确定。没有固定判据时性能结果无法机械判为通过或失败。

**最小修订**：DSH 在 `ready` 前确认最终 p95 门槛及超预算判定/处置方式，并将其写进 AC；记录机器、合成数据规模、冷/热切换、样本统计和峰值。数值正确性不属于本次审查范围。

### P2-1 — `allowed_paths` 中有不必要的宽写域

新增 Presentation、对应测试和 solution 文件是必要的；但整个 `Directory.Build.props` 会影响所有桌面项目，而新项目位于其子目录，默认会继承该文件。当前 Task 又允许修改 Appearance、DesignSystem 及多个 App 的整片 Views/ViewModels/Controls/Styles 路径，而 W-1 明确限制为运行期内容树切换、窗口与启动安全。它们为实现提供了余量，但超出显式切换/生命周期接线所需的最小文件范围。

**最小修订**：除补入 `NewManga.App.csproj` 外，移除对 `Directory.Build.props` 的常规写授权（确有必要时另列变更理由），并把 App/Appearance/DesignSystem 写域缩到实现所需的具体文件或子目录。不得以该宽路径修改视觉设计、Appearance 唯一写者或共享契约。

### P2-2 — ready 前需收敛恢复指针与 Task 元数据

治理指针中，`STATUS` 当前 Task=FEA-07 `proposed`、READY 无，`REBASELINE_PLAN` 中 FEA-07 在 residual 前，`TASK_LEDGER` 两项均为 proposed；FEA-07 卡第 59 行已记录用户“按原来的顺序进行”，顺序裁决已落盘。当前没有更早的 FEA-07 review/adjudication。

但 `STATUS` 的 rolling checkpoint 仍指向 `FEA-02-CORE`；该 checkpoint 自述 `in_review`、未集成/未完成，而 Plan 已将 FEA-02 标记 done。这是过期恢复指针，`check.ps1` 不会判别其语义。另，`base_commit=682fe17a…` 后到 reviewed head 的 diff 包含 Task、residual、Ledger 与 checkpoint 文档变更（未含源码）；范围冻结后应将实施分支基线刷新到最终冻结 head，避免新 Owner 基于旧 Task 元数据。Task `owner` 仍为 null、branch/worktree 为空；当前用户指派实现 Owner 为 DSH，准备置 ready 时应登记为 `dsh` 并填写实际分支/worktree。方案 §12.1 的 FEA-07 行仍写 ZCode Owner，须按当前用户指派处理为已被 supersede，不得据旧行重新分配。

**最小修订**：DSH 在置 ready 时刷新 rolling checkpoint 指针；将 Task `base_commit` 更新到最终 scope-reviewed/frozen head；填入 `owner: dsh`、实际 branch/worktree，并保留本报告的 base/head 记录作为本轮范围审查绑定。

## 范围与契约对照

| 来源 | 复核结果 |
|---|---|
| 方案 §7.1–§7.3、§12.1 FEA-07 | Task 覆盖运行期切换、WindowBroker、switch journal、安全启动，方向吻合；事务提交/逐步回滚、完整 window memento 与生命周期验收不足，见 P1-2/P1-3。§12.1 的 Owner 为 ZCode 与本轮用户指派冲突，按 P2-2 处理。 |
| 方案 §12.3 A01/A02/A03/A05/A06/A08 | A01/A02/A05 有主要断言；A03 的持久化/保护指针断言不足；A06 漏暂停期间变化后的保护；A08 漏 125% 及拔屏 fail-closed 内容迁回。详见 P1-2/P1-3。 |
| 方案 §12.3 A07/A15 | A07 的未知 frontend ID、theme/scale 不兼容及有效设置保留没有明确启动验收；纳入 P1-4 的启动矩阵。A15 完整真实链属于 FEA-15，FEA-07 不应扩大到导入/备份全链，但须按 synthetic data 验证复用同一 Host。 |
| `04-layout-responsive.md` §4/§5 | 双屏/拔屏处理与 100/125/150/200% 要求未完整映射到 AC5，见 P1-3。 |
| H2/H3 | 无独立 Task 并非本身问题；AC1+AC5+AC6 可承载其验证，但目前缺少窗口内容替换/PerMonitorV2 判据，且 H3 最终门槛未锁定，故现状不足。 |
| C-02 V-05/V-08b | `builtin.fluent` 的视觉令牌例外必须按 frontend/theme 组合生效，不可改变 Current 外观；V-08b 要进程级唯一 `KeyMap` 按 `(frontendId, windowRole, focusScope)` 路由。AC5 有“不重复快捷键”方向，但未明确唯一注册表/焦点路由验收。禁止修改冻结 selector 语义。 |
| C-03 | `presentation-settings.json` 的唯一 writer 是 `NewManga.Appearance.AppearanceCoordinator`。现有 `SaveAsync` 已提供原子持久化接缝；Task 可调用但不得迁移/复制 writer。W-1 与此一致。 |
| C-05 | FEA-07 不应改页可见性谓词或数据模型；Task 禁止第五页/新 `SpaceId`，与 C-05 的统一谓词边界不冲突。Window/Inspector 不等于新增一级页面。 |
| AD-002 | 现有边界仍是 Avalonia → Host/IPC → Python Core，UI 不直接访问 DB/任意 OS 路径。Task 不开放 Host/Core 写域；Presentation 依赖方向应按 P1-5 机械验证。 |

## 当前实现与可执行性

- `App.axaml.cs` 在启动时读 Appearance、调用 `FrontendSelector.Select`、只创建一个 `HostController`，然后选择 shell（第 59–81、109–139 行）；当前没有运行期切换编排。
- `FrontendSelector.Select` 是启动候选解析器，保留 `--frontend` 高优先级、persisted frontend 次之、未知 ID fallback Current V2（`FrontendSelector.cs:79`、`:83`、`:121`）。不要改变其冻结语义。`AppearanceCoordinator.SaveAsync` 是现有唯一写者路径（`AppearanceCoordinator.cs:67`），它只持久化外观设置，本身不构成切换事务。
- `AppShellV2` 是 `UserControl`，`FluentShell` 和 legacy `MainWindow` 当前都是 `Window`（`AppShellV2.axaml.cs:25`、`FluentShell.axaml.cs:40`、`MainWindow.axaml.cs:20`）。legacy MainWindow 在 Loaded 时启动 Host，并在 Closed 时同步 Dispose；重建窗口可能重复 Start/停止 Host（`MainWindow.axaml.cs:165`、`:166`、`:790`、`:833`）。因此需要把 Host ownership 迁到进程级协调器，并将可切换壳作为稳定窗口的内容；Task 的 App 壳目录可承载所需重构，但必须补入 App `.csproj`。
- 在 `apps/desktop-avalonia/src` 和测试目录没有找到既有 `WindowBroker`、`FrontendSwitchCoordinator`、switch journal 或 `ExitCoordinator`。这意味着需在新 Presentation 模块实现这些职责，而非复用现成实现；安全启动可复用当前 selector fallback 和 Program 的 fatal logging，但还需覆盖坏包构造失败后回退 Current V2 的路径。
- W-6 现在是可理解的架构限制，但不能由现有 `dotnet build` 自动验证。AC7 必须规定 project-reference 图的可执行断言。
- 写域整体方向可完成 P1–P4，但当前不能完成到生产 App 的模块引用；`Directory.Build.props` 与 Appearance/DesignSystem 广域授权也应收紧。

## 验收与证据

- AC1–AC7 当前均为待完成项，标有 `<<TODO>>`。这是 `proposed` 阶段，不是实现失败；本轮指出的重点是冻结前要把 AC 写成可观察、可判定的结果。
- **W-2** 与 AC5 一致：原生双屏、拔屏、DPI 只能由 Windows 原生桌面矩阵作证；headless 只做逻辑回归。
- **W-5** 的记录维度齐全方向正确，但最终阈值/超限处理未定，见 P1-6。
- 真实漫画/真实 `%APPDATA%` 禁令已经写入 Task。还需将 journal/theme/data 临时路径注入要求落到 AC1–AC4 测试行，防止测试默认写入用户配置目录。
- FEA-07 关闭时至少需保留：headless 故障/切换矩阵、原生双屏/拔屏/DPI 截图与矩阵、性能 baseline（硬件/数据规模/冷暖状态/统计值）、全量 build/test 与两项生成物 `--check`、治理及 pins 输出；对 skips 逐项说明并与本轮全量基线比较。

## 治理与实跑结果

- 初始 `git rev-parse HEAD` 为 `e9d542ab47ced7a0041d145c3b1061de316482a8`；`git status --short` 为空。当前 checkout 在 `main`、git common dir 为 `.git`，本 checkout 不是 linked worktree；仓库另有已登记 worktree，本次没有创建/删除/移动任何 worktree。
- `git log --oneline -6`：`e9d542ab4`、`48eb8f2a1`、`682fe17ae`、`2bdbe45d1`、`b26840acd`、`c878698ba`。`git show --stat e9d542ab4` 仅显示 `doc/tasks/FEA-07.md` 的 5 行新增。
- `git diff --name-status 682fe17ae… e9d542ab4…` 显示 Task、residual、Ledger、checkpoint 文档发生变化，**没有源码变化**。本轮 review 按要求以 `682fe17a…` 作为审查 base；Task 准备进入 ready 时，应将实施基线更新到最终冻结的 reviewed head。
- STATUS/PLAN/LEDGER 当前 Task 指针一致：FEA-07 `proposed`，READY 无，FEA-06-RESIDUAL-1 `proposed`；DAG 把 residual 放在 FEA-07 之后。卡第 59 行已记录用户顺序裁决。rolling checkpoint 指针不一致问题见 P2-2。
- `dotnet build apps\desktop-avalonia\NewManga.sln --nologo`：通过，0 warnings / 0 errors。
- `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings`：通过，**1034 passed / 0 failed / 57 skipped**，与当前 FEA-06 基线 1034/0/57 相同。
- `pwsh -NoProfile -File tools\governance\check.ps1`：PASS；3 条警告（10 个非终态 Task、STATUS/PLAN 接近体量预算），无失败。
- `pwsh -NoProfile -File tools\governance\verify_pins.ps1`：PASS，15/15 pins。
- 上述必跑命令均在报告写入前、初始工作树 clean 时执行。治理脚本为只读；运行后状态仍 clean。

## 冻结与实施建议

**FEA-07 现在不可置 ready。** DSH 应先处置 P1-1…P1-6，按 P2-1 收紧写域，并在置 ready 前完成 P2-2 的治理/Task 元数据收敛。最小冻结项是：补 App project reference 写域；把 A03/A06 与 §15.5 事务 rollback 条件变成可观察 AC；补完整双屏/DPI 行为；明确隔离测试根和 legacy/`--frontend` 回归；为 W-6 增加机械 project-reference 检查；冻结 W-5 最终阈值。

之后 DSH 需将 Task Owner 登记为 `dsh`，设置最终 base/branch/worktree 和 Reviewer Appointment，刷新 STATUS rolling checkpoint 指针，随后再决定是否将 FEA-07 转为 ready。实现前无需新增独立 H2/H3 Task，前提是修订后的 AC5/AC6 完整覆盖上述 H2/H3 观察项。
