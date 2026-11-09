# FEA-07-IMMERSIVE-F11-1 Review r1（独立子代理）

- reviewer：DSH fresh 子代理（父会话 `session-b84cf221-d82c-42be-82f7-e1bb773761ff` 派发；未参与实现/返修，只读审查被审 head）
- reviewer_kind：`subagent`
- author：`dsh`
- base_commit：`70a89d009`
- reviewed_head：`c298fe8f63011f4f08bf63dc7a609314454c830e`
- decision：**changes_requested**

## 结论

**changes_requested**：P0=0，P1=1，P2=4，P3=6。

代码主路径可接受：`TryOpenImmersiveReader` 在注入 `Show()` 失败时确实清空 `LastImmersiveWindow`、恢复主窗、写状态栏与 `immersive-open.log`，reader 入口不再向 UI 事件抛异常；`F11HotkeyTests` 实测 9/9，直接调用 `OpenImmersiveReader()` 的两组测试 20/20。阻断项是 **R-001**：任务已是 terminal 且 `canonical_evidence_status: complete`，但 `EV-IF11-01` 把 AC1–AC3 指向一份“F11 未进入应用”的原生 JSON（该 JSON 自身记录 `hintVisible=false`、`logExists=false`、`immersiveCount=0`），AC4 无 pin——canonical evidence 表与 AC 不对应。

## 0. 实跑命令与结果

| # | 命令 | 结果 |
|---|---|---|
| 1 | `git rev-parse HEAD`；`git log -1 c298fe8f6` | HEAD=`c298fe8f63011f4f08bf63dc7a609314454c830e`；父提交=`70a89d0094` |
| 2 | `git show --name-status c298fe8f6` | 12 文件：2 代码/测试、3 文档、1 新 Task、4 JSON、3 ps1 |
| 3 | `dotnet test ... --filter "FullyQualifiedName~F11HotkeyTests"` | exit 0；9/9 通过 |
| 4 | `dotnet test ... --filter "ReaderLibraryTests\|ReaderChapterSelectorTests"` | exit 0；20/20 通过 |
| 5 | `python tools/governance/task_ledger.py` | 557 files / terminal 542 / non-terminal 14 |
| 6 | `pwsh -NoProfile -File tools/governance/check.ps1` | PASS (3 warnings)，但检查对象是 `FEA-07-RESIDUAL-4`，不校验本卡 |
| 7 | 逐文件 SHA-256 | Canonical 表 5/5 命中；2 个证据文件未入表 |
| 8 | `%APPDATA%\com.newmanga.desktop\logs\window-material.log` 只读检查 | 15:07:00 由既有用例写入（`L-R4b-1`），非新测试 |

**副作用披露**：既有用例 `F11_IsIgnoredWhileSearchBoxHasFocus_AndDoesNotEatText` 用 `new AppOptions()` 调 `Show()`，会写真实 AppData 1 行；本 commit 新增测试用临时 `--log-dir`，无残留。

## 1. 范围

- 12 个文件全部在 `allowed_paths` 内；无 `doc/contracts/**`、依赖 pin、`tools/e2e/**`、`scripts/**` 变更；无删除；父提交正确。
- 原生脚本未运行（超出只读审查范围）。

## 2. 实现正确性

| 项 | 结论 |
|---|---|
| (a) 清空 `LastImmersiveWindow` | 通过 |
| (b) 恢复主窗不残留 `Minimized` | 代码通过，但测试未前置最小化（R-002） |
| (c) 状态栏提示 | 失败写文本；成功后不清、Host catch 可覆盖（R-003） |
| (d) 写 `immersive-open.log` | 通过（共用 `ResolveDiagnosticsRoot`） |
| (e) 不向 UI 事件抛异常 | 主路径通过；残留面 R-009 |
| `ToggleImmersiveAsync` 失败回退来源页 | 通过 |
| 成功路径兼容 | 通过（20/20） |
| `ImmersiveShowOverride` 暴露面 | `internal`，通过 |

## 3. 回归与测试隔离

- `F11HotkeyTests` 9/9，新增测试断言非空转；但 `NotEqual(Minimized, ...)` 恒真（R-002）；未断言状态栏文本（R-008）；未覆盖失败→成功（R-003）；第二次调用未覆盖 reader 页入口（R-010）。
- 新测试隔离良好；套件整体仍因既有用例写 1 行真实 AppData（既有 L-R4b-1）。
- 卡片所称全量 .NET 结果未复跑（列入未核实）。

## 4. 诚实性

- AC5 `PARTIAL` + `NOT_RUN` 披露通过；JSON 与叙述一致（150419：`hintVisible=false`、`logExists=false`、`immersiveCount=0`）。
- **Canonical Evidence 表与 AC 不对应**（R-001）：`EV-IF11-01` 标 AC1/AC2/AC3 但指向“F11 未进入应用”的 JSON；AC4 无 pin；terminal + `complete` 使错误成为关账记录。
- `delivery_head`/`integration_commit` 为 null，pin commit 列为 `-`；2 个证据未入表（R-006/R-007）。
- terminal 状态早于独立 Review（R-005）。

## 5. Findings

| ID | 级别 | 位置 | 摘要 | 建议 |
|---|---|---|---|---|
| R-001 | **P1** | 卡 :88 / :18 | EV-IF11-01 映射错误、AC4 无 pin、`canonical_evidence_status: complete` 与 terminal 不匹配 | 重映射/删除 EV-IF11-01；为 AC1–AC3 补 headless 测试输出 pin、AC4 pin 测试文件；补 `delivery_head` |
| R-002 | P2 | F11HotkeyTests.cs:256/269 | 未前置 `Minimized`，`NotEqual` 恒真 | F11 前设最小化并断言恢复 `Normal` |
| R-003 | P2 | MainWindow.axaml.cs:518/557/910-918 | 成功后不清失败提示；Host catch 可覆盖 | 收敛状态文本更新；补失败→成功测试 |
| R-004 | P2 | MainWindow.axaml.cs:504-559 | 兜底只在异常时触发；`Show()` 静默不可见不覆盖 | `Show()` 后检查 `IsVisible`，失败走同一 fallback |
| R-005 | P2 | 卡 :6/:10；协议 §4 | Review 前即 terminal；approval 未记录 PARTIAL 裁决 | 改 in_review 或补用户/DSH 裁决记录 |
| R-006 | P3 | TASK_LEDGER.md:14 | tracked/untracked 计数过期 | 重跑 `task_ledger.py --write` |
| R-007 | P3 | 卡 :17/:88-92 | `delivery_head` null；pin commit `-`；2 证据未入表 | 填 commit + SHA；纳入或标 superseded |
| R-008 | P3 | MainWindow.axaml.cs:31/71 | `_status` 无法断言 | 加 internal accessor，测试断言文本 |
| R-009 | P3 | MainWindow.axaml.cs:528/583/598 | `LastImmersiveWindow` 早发布；catch 无二次保护；日志过滤窄 | Show 成功后发布；restore 包 try；日志兜底 |
| R-010 | P3 | F11HotkeyTests.cs:266；MainWindow.axaml.cs:107 | 卡片称 reader 入口同样兜底，测试未覆盖 | 触发 `Reader.RequestImmersive()` 或收窄措辞 |
| R-011 | P3 | 卡 :55 | AC1 说 `OpenImmersiveReader()` 捕获，实际在 `TryOpenImmersiveReader()` | 修正措辞 |

## 6. 未核实

- 未复跑全量 .NET 套件；未做原生 AC5 复测；未验证 `check.ps1` 对本卡 pin 的语义校验；未审查并发产生的未跟踪文件；未核对截图视觉内容。
