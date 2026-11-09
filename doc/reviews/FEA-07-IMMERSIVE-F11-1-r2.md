# FEA-07-IMMERSIVE-F11-1 Review r2（独立子代理）

- reviewer：DSH fresh 子代理（父会话 `session-b84cf221-d82c-42be-82f7-e1bb773761ff` 派发；未参与实现/返修，只读）
- reviewed_head：`a4b59f860`（实现 head `dc3526b76`）；base `70a89d009`
- decision：**changes_requested**（P0=0 / P1=1 / P2=2 / P3=6）

## 结论
r1 的 11 条 finding 形式上全部关闭（R-002/R-003/R-010 经变异验证有判别力）。**新 P1（N-001）**：AC5 原生证据采集于默认 **v2 壳**，该壳不实例化 `MainWindow`，F11/沉浸实现只在 legacy 壳 ⇒ 原生复测未触及被审代码，「键盘事件未进入应用」无依据，默认壳 F11 功能本身不存在。

## 实跑
- `git show --name-status a4b59f860` / `--stat dc3526b76`：范围在 allowed_paths；工作区干净。
- `dotnet test --filter F11HotkeyTests` → 9/9；`--filter "ReaderLibraryTests|ReaderChapterSelectorTests"` → 20/20；全量 App.Tests → 832 通过 / 11 跳过 / 0 失败。
- `task_ledger.py`：557/557/0、terminal 542、non-terminal 14，与改后 ledger 一致。
- `check.ps1` 与 `-TaskPath`：PASS；证据表 11/11 SHA 独立核对一致。
- 变异（`%TEMP%` 复制）：M-A 去掉 `WindowState=Normal` → 失败（Minimized）；M-C 去掉成功后 `RefreshStatusText()` → 失败；M-E `ImmersiveRequested` 改回 `OpenImmersiveReader()` → 失败；**M-D 删除 `IsVisible` 守卫 → 9/9 仍绿（无覆盖）**。

## N-001（P1，证据/诊断有效性）
- `AppOptions.DefaultShellId = "v2"`；`MainWindow` 仅在 `!UseV2Shell` 创建（`App.axaml.cs`）；`AppShellV2.CreateRoot` 明确不涉及 MainWindow；F11 只出现在 `MainWindow`/`ReaderWorkbenchPages`。
- 几何/文案佐证：v2 窗口 1116×799、导航含 资料柜/工位/控制台；legacy 导航为 书架/工作台/阅读器/设置。
- 后果：v2 壳按 F11 无反应是预期；「无窗口/无提示/无日志/未最小化」不能推出环境阻塞。
- 建议：证据补 shell/args；用 `--shell=legacy` 重跑；更正 AC5 与 ADJ 因果；v2 缺口另立范围。

## 其他 findings
| ID | 级别 | 摘要 |
|---|---|---|
| N-002 | P2 | `capture-after-f11.ps1` 不记录 exe/args/shell，canonical 证据无法绑定壳/构建 |
| N-003 | P2 | `!IsVisible` 分支零测试（M-D 存活） |
| N-004 | P3 | 「早期构建」表述与同 pid 事实不符（应为早期采样） |
| N-005 | P3 | 证据表行间空行导致渲染碎裂 |
| N-006 | P3 | AC4「返回 false」无对应断言 |
| N-007 | P3 | `approval` 重复同句 |
| N-008 | P3 | 失败提示两处字面量（`RefreshStatusText` 与 catch 内直写） |
| N-009 | P3 | 7 个未跟踪显示产物落在另一终态卡证据目录；Resource Manifest 的显示状态断言不可核实 |

## 未核实
未复跑全量 .NET；未做原生复测；未验证 v2/legacy 启动壳配置；未审截图视觉内容。
