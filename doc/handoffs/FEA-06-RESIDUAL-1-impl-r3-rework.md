---
task_id: FEA-06-RESIDUAL-1
author: Codex CLI（fresh 实现会话；未承担本轮独立 Review）
recipient: DeepSeek Harness
base_commit: 227eab304a77d00e05d72336d5e6b14e39e09d98
delivery_head: 3c3afe17007ee785f018c3bf78c7018caa1c65d5
status: delivered_for_review
---

# Handoff：FEA-06-RESIDUAL-1 impl-r3 R3-001 返修

## 交付结果

仅返修 `doc/reviews/FEA-06-RESIDUAL-1-impl-r3.md` 的 P1 R3-001（AC1 / I-10，冻结设计 `07-page-reader.md:23`）。用户实施指令、Task 当前 reviewer 记录及 rolling checkpoint 第116节共同确定本轮范围。Task 原始 base 为 `82529a3d5864a39f362e414b67bca774d743f862`；本返修起点为 `227eab304a77d00e05d72336d5e6b14e39e09d98`，初始工作树干净，branch=`main`，Git common directory=`.git`。

实现 commit：`3c3afe17007ee785f018c3bf78c7018caa1c65d5` — `fix(fea-06-residual-1): R3-001 preserve center press visibility toggle`。本 Handoff 与新日志随后的证据提交追加；`delivery_head` 固定生产与测试字节，不要求包含自身文档 commit。未 push。

变更仅有：

- `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/ReaderPageView.cs`：移除 PageSurface 上第二次处理 press 的订阅；Reader 的单个 tunnel press 处理先根据原始 Source 是否属于 PageSurface/图片后代及中部坐标调用一次切换。中部切换后只重置 deadline；其他来源继续唤醒并重置。release 保持 `reveal:false`，只给仍可见工具条续时。未改公共点击方法语义、2s 空闲窗口、160ms full 退出或 reduce/navigation-off 瞬时逻辑。
- `apps/desktop-avalonia/tests/NewManga.App.Tests/FluentR2ReworkTests.cs`：保留原测试，追加两组 theory，共12个用例。新增加载 helper 使用 FakeHost 的实际一页 PNG，不保存设置、不写证据 PNG。
- 新日志 `verification/FEA-06-RESIDUAL-1/impl-r3-rework-verification.log` 与本 Handoff；旧 verification、Review、冻结设计与旧 PNG 保持原字节。

Core、契约/Schema、依赖、生成物、Current V2、Shell/组合根、FEA-07 seam 均无改动。未修改 Task/STATUS/Plan 或任何 evidence pin。

## 验证证据

环境：Windows NT 10.0.26300.0，PowerShell Core 7.6.8，dotnet SDK 10.0.401，测试目标 net9.0，Avalonia 11.3.22。`NEWMANGA_CORECLIENT_SIDECAR_DIR`、`NEWMANGA_CAPTURE_FLUENT_PNGS`、`NEWMANGA_EVIDENCE_SYNC`、`VIRTUAL_ENV` 未设置。验证固定于上述实现 commit；全量原始输出与每条命令 EXIT 均在新日志。

日志 Git blob（LF 归一后）SHA256：`06b26212994268ad7e0fc349d470c0e1beb0bbdb0f0eea86142ae32e23692349`；原始 Windows 工作树日志 SHA256：`5202a3cdcf30649788b8d8ece258da5246b77d8e97eab0e8e074b1ae4acb6f84`。后者只记录当次实跑原始字节，不作为跨 checkout 的 pin；接收者可用 `git show <证据提交>:verification/FEA-06-RESIDUAL-1/impl-r3-rework-verification.log` 读取前者对应字节。8个程序集的单次全量输出汇总为1245/0/57；原测试文件9个公开测试方法保留，新增2组theory为12个用例。Handoff 落盘后另跑 governance，仍 PASS（3个既有 warnings）。

| 场景 | 实际执行 | 结果 |
|---|---|---|
| 反例有效性 | 先加三态中部测试，再改生产；相同 `--filter FullyQualifiedName~R3001` | 原生产3失败（自动隐藏后首次 Down 预期 true、实际 false，EXIT=1）；修复后3通过，EXIT=0 |
| AC1 / I-10 中部双向切换 | `R3001_SamePointCenterClicks_ToggleFromPrePressState_ReleaseOnlyExtendsDeadline`，full / reduce / full+navigation-off | 3通过。自动隐藏后 click1 唤回、click2 隐藏、click3 唤回；真实 MouseDown/MouseUp，同一坐标，无中途 MouseMove/Poke；每次 Down 一次显隐变化，Up 零变化；每次实际命中页面且位于中部 |
| release / 2s / detach | 同一三态用例，按下后400ms释放；旧 press deadline、last-release+1999ms、+2000ms；显示时 detach 后再推进3000ms | 全通过。Up 重置为释放时间+2s；旧 deadline 不隐藏；detach 停 timer、清 deadline，后续检查不隐藏 |
| reduce / navigation-off | 上述 click2 的 MouseDown 后，未推进任何帧即检查两条 IsVisible=false、Opacity=0 | 全通过，瞬时切换 |
| 普通控件 / wheel / 被 shell 接管按键 | `R3001_OtherControlPress_Wheel_AndShellHandledKey_WakeHiddenBarsAndRenewDeadline`，三态×3种输入 | 9通过。均从2s自动隐藏后的状态开始，以真实鼠标按下/释放、滚轮、Ctrl+K唤醒并续2s；普通控件选用恢复浮动工具条按钮，真实 click 仍恢复侧栏；Ctrl+K 实际打开命令面板 |
| 新旧定向回归 | R3001 与 R2003 合并运行，完整命令见下方 | 17 passed / 0 failed / 0 skipped，EXIT=0（新增12+原R2003的5） |
| 构建 | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | PASS，0 warnings / 0 errors，BUILD_EXIT=0 |
| 无过滤全量 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo` | **1245 passed / 0 failed / 57 skipped，总1302**；基线1233只增12，skip不增；TEST_EXIT=0 |
| 治理 | `pwsh -NoProfile -File tools\governance\check.ps1` | PASS，CHECK_EXIT=0；既有3项 warnings，不替代独审与授权 |
| 冻结契约 | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | PASS，15/15，PINS_EXIT=0 |
| 两生成器 | 现有 TokenGen/ThemeGen DLL 各 `--check`（完整命令在日志） | 均 up-to-date，EXIT=0 |
| 旧 PNG 与历史字节 | `git diff --exit-code 82529a3d5864a39f362e414b67bca774d743f862 -- verification/FEA-06/screens`；4 PNG SHA256；返修 base 对比既有 verification/Review/design | 全部零漂移，EXIT=0；只追加新日志/Handoff，不覆盖旧证据 |

已实跑的定向命令：

```powershell
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --filter 'FullyQualifiedName~R3001|FullyQualifiedName~R2003' --settings apps/desktop-avalonia/tests/NewManga.runsettings --nologo
```

新增测试中的 `Pump(20)` 仅将布局更新提交给 headless renderer，保证 InputHitTest 使用当前控件位置；不触发唤醒、不替代 MouseDown/MouseUp、不推进用于 deadline/动画的手动时钟。所有新测试均无 `PokeToolBars` 或测试前 `NotifyInteraction`。

全量57个 skip 的完整名称与逐条原因在日志中：缺少 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 指定的 AC11 sidecar fixture，相关 attribute 优先在该条件短路。它们不计为通过，也未把 FakeHost 成功表述为真实 sidecar 集成通过。

## 接收方式

仓库 `G:\CODEX\New Manga`，branch=`main`，同一 worktree，无新建 linked worktree。通过 `git show 3c3afe17007ee785f018c3bf78c7018caa1c65d5` 读取固定实现与测试；按上表命令恢复验证。新日志为本次返修证据候选，canonical evidence/pin 的更新及 Task 状态由 DSH 登记。

## 下一任务建议

- Task：`FEA-06-RESIDUAL-1` impl-r4，上述交付齐备后由 DSH Appointment；本会话不自审。
- 推荐 Agent：fresh Codex CLI 独立上下文 Reviewer；DSH 负责报告处置、集成验证与生命周期。
- Recovery point：`G:\CODEX\New Manga`，`main`，原 Task base=`82529a3d5864a39f362e414b67bca774d743f862`，本返修 base=`227eab304a77d00e05d72336d5e6b14e39e09d98`，implementation head=`3c3afe17007ee785f018c3bf78c7018caa1c65d5`；证据/Handoff 在随后的文档提交中。无需新 worktree。
- Scope：审查者只读被审生产与测试，允许写 DSH 指定的 `doc/reviews/FEA-06-RESIDUAL-1-impl-r4.md`；不改实现/旧报告/旧证据，不 push，不改变 Core/契约/依赖/生成物/冻结设计/Current/组合根/FEA-07 seam。
- Deliverables：记录上下文来源与固定 reviewed_head 的 impl-r4 报告、R3-001 处置核验、四命令实际 EXIT/全量计数、旧 PNG 对比与剩余限制。若 findings，交 DSH；不得同一 Reviewer 会话参与返修。
- Verification / Gate：重跑本 Handoff 三态反例与四条验收；全量至少1245/0/57、check PASS、pins15/15、旧PNG零漂移；保留 skip/NOT_RUN/BLOCKED。Review 通过后仍需 DSH 集成验证、evidence pin 和资源 closeout 才可关闭 Task。

可直接转发给 DSH / 待 Appointment Reviewer：

> 在 G:\CODEX\New Manga 的 main 接收 FEA-06-RESIDUAL-1 R3-001 返修。先核对 HEAD/工作树；Task base=82529a3d5864a39f362e414b67bca774d743f862，返修 base=227eab304a77d00e05d72336d5e6b14e39e09d98，固定实现 head=3c3afe17007ee785f018c3bf78c7018caa1c65d5。读取 doc/reviews/FEA-06-RESIDUAL-1-impl-r3.md、doc/handoffs/FEA-06-RESIDUAL-1-impl-r3-rework.md 与 verification/FEA-06-RESIDUAL-1/impl-r3-rework-verification.log。DSH 登记 fresh Codex impl-r4 Appointment 后，Reviewer 只读生产/测试，核验中部按事件前状态一次切换、release只续时，真实同坐标click1/2/3、自动隐藏后唤回、full/reduce/navigation-off、last-release+2s与detach，以及其他控件/wheel/shell-handled-key唤醒；实跑四项验收（上表完整命令），计数至少1245/0/57，check PASS、pins15/15、旧FEA-06 PNG零漂移。只写 doc/reviews/FEA-06-RESIDUAL-1-impl-r4.md，记录审查者来源/上下文与精确head；禁止修实现或改旧报告/旧证据/Core/契约/依赖/生成物/冻结设计/Current/组合根/FEA-07 seam，不push。报告交DSH处置，不将本次测试通过视为全部AC达成。

## 风险与遗留

R3-001 的实现和回归已交付，独立 impl-r4 Review 尚未运行，本报告不是 Review 批准。DSH 集成、canonical evidence/pin、Task 生命周期与资源 closeout 均待接收者处理。原 I-4 其余可测格/完整Tab遍历 NOT_RUN、D-8 PENDING_DISPOSITION、B-1…B-7（含B-5硬件/原生200%DPI/a11y）继续保留；没有扩大本返修以宣称解决。未执行原生视觉、触摸硬件或 PNG opt-in 验收。

资源：无新增依赖、数据集/模型、task-env、exchange、用户数据或 linked worktree。操作脚本位于既有 workspace 的 `agent-output/codex/FEA-06-RESIDUAL-1/verify-r3-rework.ps1`，保留供复算（脚本拒绝覆盖现有证据）；唯一验收原始输出已版本化，不依赖仓外文件才能接收。未执行删除、prune/GC 或资源迁移。需要回退实现时由 DSH 针对上述实现 commit 创建 revert；历史证据仍原位保留。
