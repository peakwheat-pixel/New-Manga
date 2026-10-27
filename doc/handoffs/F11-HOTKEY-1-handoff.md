---
task_id: F11-HOTKEY-1
author: saber-ui-spec (DSH team)
recipient: DeepSeek Harness
base_commit: 171529b5d
delivery_head: ec94991c399c94f771e7bc1958dcf868585eae34
status: ready-for-integration
---

# Handoff：F11-HOTKEY-1（全局 F11 快捷键：沉浸/全屏切换）

## 交付结果

实现提交 **`ec94991c399c94f771e7bc1958dcf868585eae34`**（branch `task/F11-HOTKEY-1`，worktree `G:/CODEX/New Manga.workspace/worktrees/F11-HOTKEY-1`，base 释放提交 `04b657131`，任务卡冻结 base `171529b5d`）；本 Handoff 与任务卡 pin 在后续文档提交中记录。未 push、未改 Python Core/旧壳/协议语义/Host 契约语义。

| AC | 结论 | 说明 |
|---|---|---|
| AC1 快捷键 | **MET** | 裸 F11 切换沉浸；阅读器页打开当前书，非阅读器页先切阅读器再打开并记录来源页；Esc/F11 关闭后回来源页。 |
| AC2 不干扰输入 | **MET** | 搜索框聚焦时 F11 不触发不消费、文本不变；修饰键 F11 忽略；H/F/Esc/方向键不受影响。 |
| AC3 测试 | **MET** | Headless 8 项；真机 6 截图 + 窗口状态时间线（1↔2 窗口）、全屏尺寸 1400x787、内容真实渲染。 |
| AC4 回归 | **MET** | test.ps1 **153/153**；vitest **60/567**；pytest **3F/2739P/9S**（基线一致）。 |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；14 条 64-hex pin；本 Handoff（含 Record Decision）。 |

### Record Decision（摘要，完整版在任务卡）

- 注册方式：Avalonia 窗口级 Tunnel `KeyDown`，**不注册系统级热键**（`RegisterHotKey/HotKeyManager/GlobalHotKey/SetWindowsHookEx/Win32Properties` 源码 0 命中）。
- 触发：**裸 F11**；带 Ctrl/Alt/Shift 不消费不切换。
- 非阅读器页：先 `Navigate("reader")` + 加载当前/默认书，再 `OpenImmersiveReader()`，记录来源页；关闭（Esc 或 F11）→ 回来源页。
- 阅读器页：打开/关闭沉浸，关闭后仍在阅读器页。
- 输入框聚焦：不触发、不消费、不影响文本。
- 沉浸窗内 F11 = toggle off；H/F/方向键行为不变。

### 代码变更（全部 `apps/desktop-avalonia/**`）

- `src/NewManga.App/Views/MainWindow.axaml.cs`：Tunnel KeyDown；`TryHandleGlobalKey(Key, KeyModifiers)`；`IsTextInputFocused()`（TextBox 及祖先）；`ToggleImmersiveAsync()`（打开/关闭 + 来源页记录/恢复）；`OnImmersiveWindowClosed`；`LastImmersiveToggle`/`ImmersiveRestorePage` 测试与证据钩子。
- `src/NewManga.App/Views/ReaderWorkbenchPages.cs`：`ReaderWindow.TryHandleKey` 新增 `Key.F11`（`F11Count++`、flush 进度、`Close()`）；类文档更新。
- `tests/NewManga.App.Tests/F11HotkeyTests.cs`（新，8 项）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC4 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory G:/CODEX/New Manga.workspace/task-envs/F11-HOTKEY-1/evidence` | Windows 10.0.26300；`ec94991c3` | PASS 153/153（coreclient 40 / host 42 / app 71） | `verification/F11-HOTKEY-1/test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC4 vitest | `cd apps/desktop/frontend && npm test`（主仓；`git diff 04b657131 -- apps/desktop/frontend` 为空） | 旧壳未改动 | PASS 60 files / 567 tests | `test/vitest.log` |
| AC4 pytest | `PYTHONPATH=src python -m pytest -q`（worktree；C:\Python314） | 未改 Python | 3F/2739P/9S（基线一致） | `test/pytest.log` |
| AC1/AC2/AC3 真机 | 启动 `start-book-fixture.ps1 -AppExe <pkg>/NewManga.App.exe -DataRoot <isolated-data> -ExtraArgs '--demo-write'`；搜索框输入「雾港来信」+ F11（bg/fg）→ 阅读器页 F11 → Esc → 书架页 F11（Tab 移焦后）→ F11 关闭 | BOOK-FIXTURE 副本数据根；发布件 + FINAL-VALIDATION-1 sidecar | 见任务卡 §真机表：1↔2 窗口、1400x787 全屏、输入框 F11 无效、Tab 后有效、Esc/F11 回来源页 | `live-evidence.json`、`screens/01-06`、`runtime-logs/*` |
| AC5 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/F11-HOTKEY-1.md` | `ec94991c3` + 文档提交 | PASS | 见任务卡 pin |

环境说明：首次全量跑时另一 Agent 的 `NewManga.App` 占用全局单实例互斥体，导致宿主 `LegacyShellRealTests.DefaultGlobalMutex_AcquiresOrFallsBackToLocal` 失败（与 F11 改动无关）；无占用后重跑 **153/153** 通过。真实运行日志见 `test/test.ps1-final.log`。

明确未运行：真机「书架来源 + Esc」组合（与「书架来源 + F11 关闭」共用同一 `Closed` 恢复路径；headless 已覆盖）；系统级全局 F11（任务禁止）。

## 接收方式

- 分支/worktree：`task/F11-HOTKEY-1` / `G:/CODEX/New Manga.workspace/worktrees/F11-HOTKEY-1`；delivery head `ec94991c3`。
- 复现：见 `verification/F11-HOTKEY-1/REPORT.md §7`。
- 真机前置：发布单文件 App + `app/core-sidecar`；数据根用 BOOK-FIXTURE 副本；输入用真实键盘事件（cua-driver foreground SendInput）。
- 需要 DSH 做：独立 Review（Owner 不自审）→ 运行 test.ps1 复核 → 合入/集成 → closeout。

## 下一任务建议（必填）

- Task ID / 标题：**本批次无新增实现任务需要由我释放**；A 组第二批 F11-HOTKEY-1 已交付（GPU-ORT-PROBE-1 / RUN-EXPORT-E2E-1 由 core-admin-rca 承接）。
- 推荐 Agent / Reviewer：集成 = DSH；独立 Reviewer = 未参与实现的 Codex / ZCode / Antigravity（按 DSH 排班）。
- 推荐原因与前置依赖：F11-HOTKEY-1 依赖的阅读器/沉浸基础已在前两批合入（base `04b657131` 已含 READER-LIBRARY-WIRE-1 / READER-PROGRESS-1 / CHAPTER-SELECTOR-1）；等 A2 其余两卡交付后由 DSH 统一集成与 Review；是否释放下一批由 DSH 裁决。
- Recovery point：仓库 `G:/CODEX/New Manga`；delivery head `ec94991c3`；base `04b657131`。
- 允许修改路径：`apps/desktop-avalonia/**`、`doc/tasks/F11-HOTKEY-1.md`、STATUS/PLAN/LEDGER、`verification/F11-HOTKEY-1/**`、workspace task-env。
- 禁止范围：不改 Python Core/旧壳/协议与 Host 契约语义；不 push；不 gc/prune；不注册系统级热键。
- 交付物：本卡实现 + 证据 + Handoff 已完成；DSH 集成验证结论与 closeout 记录。
- 验证命令与完成 Gate：`test.ps1` 153/153、vitest 60/567、pytest 3F/2739P/9S、`check.ps1 -TaskPath` PASS、14 条 pin、独立 Review 通过。
- 可直接转发给 Agent 的指令：

```text
作为独立 Reviewer（未参与实现），复核 F11-HOTKEY-1（delivery ec94991c3，walkthrough 见 doc/handoffs/F11-HOTKEY-1-handoff.md 与 verification/F11-HOTKEY-1/REPORT.md）。
只读：不要修改代码。核对 AC1–AC5 与 14 条 pin（sha256 与文件一致）；重跑 pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1（应 153/153，注意其他 Agent 的 NewManga.App 占用全局互斥体时 LegacyShellRealTests 会假失败）与 check.ps1 -TaskPath doc/tasks/F11-HOTKEY-1.md（应 PASS）；重点审查 MainWindow.TryHandleGlobalKey 的输入框守卫、来源页恢复顺序，以及 ReaderWindow 的 F11 分支是否影响 H/F/方向键；给出 PASS / 有条件 PASS / 返修 结论与具体证据行。
```

## 风险与遗留

1. 系统级 F11 未注册（按任务限制），应用不在前台时 F11 不生效；如需全局捕获必须另开任务并获用户授权。
2. 从书架返回时若焦点自动回到搜索框，F11 会被输入框守卫忽略（设计使然；Record Decision 已声明）。
3. 沉浸窗与主窗共享 `ReaderViewModel`（既有设计，非本卡范围）。
4. 真机「书架来源 + Esc」组合未单跑（同一恢复路径，headless 覆盖）。
5. 需独立 Review（Owner 不得自审）。
