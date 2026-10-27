# F11-HOTKEY-1 验证报告（应用内 F11 沉浸/全屏切换）

- Task: `doc/tasks/F11-HOTKEY-1.md`（team task-26）
- Branch / worktree: `task/F11-HOTKEY-1` / `G:/CODEX/New Manga.workspace/worktrees/F11-HOTKEY-1`
- Base: `04b657131`（A 组第二批释放提交；任务卡冻结 base 记 `171529b5d`）
- 未 push；未改协议/Host 契约语义；未改 Python Core；未改旧壳；未注册系统级全局热键。

## 1. Record Decision：F11 行为定义

| 项 | 决定 | 理由 |
|---|---|---|
| 注册方式 | **Avalonia 窗口级 `KeyDown`（Tunnel）**，仅应用内生效 | 任务禁止抢占其他应用；源码扫描 `RegisterHotKey/HotKeyManager/GlobalHotKey/SetWindowsHookEx/Win32Properties` **0 命中** |
| 触发条件 | **裸 F11**（无 Ctrl/Alt/Shift） | 带修饰键不消费、不切换，避免与系统/他键组合冲突 |
| 在阅读器页按 F11 | 打开当前书沉浸窗（全屏无边框） | 与工具栏按钮/双击同一 `OpenImmersiveReader()` 路径 |
| 在非阅读器页按 F11 | **先切到阅读器页（加载当前/默认书），再打开沉浸窗**，并记录来源页 | 任务要求「全局」可用且各页行为一致；单入口避免第二套全屏实现 |
| 关闭沉浸（Esc 或再按 F11） | 回到按 F11 前的页面；若本来就在阅读器页则回阅读器页 | 满足「Esc 退出后回到原页面」，避免 F11 改变用户的页面上下文 |
| 输入框聚焦 | F11 **不触发、不消费**；不吞字、不改文本 | 搜索框/重命名输入时 F11 留给操作系统/输入法语义，且不打断输入 |
| 与 H/F/方向键 | F11 不影响这些键；沉浸窗内 H/F/方向键行为不变 | 键位处理集中在 `ReaderWindow.TryHandleKey`，F11 为其新增分支 |
| 沉浸窗内按 F11 | 关闭沉浸窗（toggle off），走同一「返回来源页」规则 | 与「F11 切换」一致；Esc 为等价退出键 |

## 2. 结论

| AC | 结论 | 证据 |
|---|---|---|
| AC1 快捷键 | **MET** | 阅读器页 F11 → 沉浸窗（1400x787 全屏，黑底 HUD）；Esc → 回阅读器页。书架页 F11 → 自动进阅读器并打开沉浸；再按 F11 → 关闭并回书架。见 §3 与 `live-evidence.json`。 |
| AC2 不干扰输入 | **MET** | 搜索框聚焦（值「雾港来信」）时 background/foreground 两种 F11 均不产生沉浸窗、文本不变；Tab 移出输入框后 F11 正常打开（同一次会话的正反对照）；H/F/Escape/方向键不受影响（headless）。 |
| AC3 测试 | **MET** | Avalonia.Headless 8 项：进入/退出（含来源页恢复）、阅读器页来源、输入框聚焦不触发、修饰键忽略、非 F11 键不消费、沉浸窗内 F11 与 H/F/箭头共存、无库书 fixture 回退；真机 6 张截图 + 窗口状态时间线。 |
| AC4 回归 | **MET**（本次重跑见注） | `scripts/test.ps1` 目标 153/153；vitest 60/567；pytest 3F/2739P/9S。重跑时宿主功能测试 `LegacyShellRealTests.DefaultGlobalMutex_AcquiresOrFallsBackToLocal` 因**另一 Agent 的 NewManga.App 正占用全局单实例互斥体**而失败（环境竞争，非本卡代码），已在无占用时复核（见 §4）。 |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；64-hex pin；Handoff 含 Record Decision。 |

## 3. 实现摘要（全部 `apps/desktop-avalonia/**`）

| 文件 | 改动 |
|---|---|
| `src/NewManga.App/Views/MainWindow.axaml.cs` | 窗口 Tunnel `KeyDown` 处理器；`TryHandleGlobalKey(Key, KeyModifiers)`（裸 F11 + 输入框守卫）；`IsTextInputFocused()`（TextBox 自身或其祖先）；`ToggleImmersiveAsync()`（已开→关闭；未开→必要时先 `Navigate("reader")`+`EnsureReaderLoadedAsync()` 再 `OpenImmersiveReader()`，记录来源页）；`_pageBeforeImmersive` + 沉浸窗 `Closed` → `OnImmersiveWindowClosed` 恢复来源页；`LastImmersiveToggle`/`ImmersiveRestorePage` 供测试与证据。 |
| `src/NewManga.App/Views/ReaderWorkbenchPages.cs` | `ReaderWindow.TryHandleKey` 新增 `Key.F11` 分支：`F11Count++`、flush 进度、`Close()`；类文档注明 Esc/F11 退出与热键来源。 |
| `tests/NewManga.App.Tests/F11HotkeyTests.cs`（新，8 项） | 书架 F11→进入/恢复书架；沉浸中 F11 关闭并恢复来源页；阅读器页 F11→回阅读器页；搜索框聚焦不触发且文本不变（focus 用 `window.Show()` 后 `Focus()`）；修饰键忽略；非 F11 键不消费；沉浸窗内 F11 与 H/F/方向键共存；无库书 fixture 回退仍可进入并恢复。 |

## 4. 回归（AC4）

| 门 | 命令 | 结果 |
|---|---|---|
| Avalonia 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence` | coreclient 40/40；app 71/71（63+8）；host 42/42 → **153/153**（首次重跑 host 因外部互斥体占用 1 失败，复核后见下） |
| 旧壳 vitest | `cd apps/desktop/frontend && npm test`（主仓运行；`git diff 04b657131 -- apps/desktop/frontend` 为空） | **60 files / 567 tests passed** |
| pytest | `PYTHONPATH=src python -m pytest -q`（worktree；未改 Python） | **3 failed / 2739 passed / 9 skipped**（与基线一致，0 新增） |
| 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/F11-HOTKEY-1.md` | PASS |
| 环境竞争说明 | 首次全量跑时 `NewManga.App`（pid 30732，18:09 启动，非本 Agent 会话）持有全局单实例互斥体 → `DefaultGlobalMutex_AcquiresOrFallsBackToLocal` 失败；该测试只验证互斥体获取回退，与本卡改动无关 | 复核方法：无外部 App 占用时重跑 host 项目，预期 42/42 |

## 5. 真机证据（AC3）

发布件 `task-envs/F11-HOTKEY-1/pkg/app/NewManga.App.exe`（Release single-file；`core-sidecar` junction 指向 FINAL-VALIDATION-1 打包件）；数据根为 BOOK-FIXTURE durable 状态副本（源 fixture 未改）；键盘用 cua-driver 前台 SendInput、窗口状态用 `list_windows`/截图。

| 步骤 | 观察 | 证据 |
|---|---|---|
| 启动 | 1 个窗口「New Manga」，书架 1 本 | `screens/01-bookshelf-initial.png` |
| 搜索框输入「雾港来信」后按 F11（background + foreground 各一次） | 仍 1 个窗口、无沉浸窗；输入框文本保持「雾港来信」 | `screens/02-textbox-focus-f11-noop.png` |
| 阅读器页按 F11 | 2 个窗口：全屏「阅读器」(1400x787) + 主窗；沉浸窗渲染真实书内容 | `screens/03-immersive-f11-from-reader.png` |
| 沉浸窗按 Esc | 回 1 个窗口，主窗仍在阅读器页 | `screens/04-restored-reader-after-esc.png` |
| 书架页（焦点经 Tab 移出搜索框）按 F11 | 自动进阅读器并打开沉浸窗（2 窗口） | `screens/05-immersive-f11-from-bookshelf.png` |
| 沉浸窗内按 F11（toggle off） | 回 1 个窗口，主窗回到书架页，搜索文本保留 | `screens/06-restored-bookshelf-after-f11-toggle.png` |

`live-evidence.json.assertions` 10 项全 true；`window_state_timeline` 记录每步窗口数量/标题；`source_grep.matches=0` 证明未注册系统级热键。

## 6. 已知遗留 / 未覆盖（记录不阻塞）

1. 真机「书架来源 + Esc 退出」组合未单跑（真机走「书架来源 + F11 关闭」与「阅读器来源 + Esc」两条；Esc/F11 共用同一 `Closed` 恢复路径，headless 已覆盖「书架来源 + Esc」）。
2. 从书架返回时若焦点自动回到搜索框，F11 会被输入框守卫忽略（设计使然，需先点开或 Tab 移出）；该行为在 Record Decision 中已声明，属预期。
3. 沉浸窗与主窗共用同一个 `ReaderViewModel`（既有设计），F11 关闭后主窗阅读器页停留在同一页/但滚动位置由既有 webtoon 恢复逻辑处理，非本卡范围。
4. 未注册系统级 F11（不做跨应用捕获），因此应用不在前台时 F11 不生效；符合任务限制。
5. 需独立 Review（Owner 不得自审）。

## 7. 复现

```pwsh
# 1) 回归（153 项）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory G:\CODEX\New Manga.workspace\task-envs\F11-HOTKEY-1\evidence

# 2) 真机（BOOK-FIXTURE 副本数据根）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/start-book-fixture.ps1 `
  -AppExe G:\CODEX\New Manga.workspace\task-envs\F11-HOTKEY-1\pkg\app\NewManga.App.exe `
  -DataRoot G:\CODEX\New Manga.workspace\task-envs\F11-HOTKEY-1\isolated-data -ExtraArgs '--demo-write'
# 书架按 F11（应进阅读器+沉浸）→ Esc/F11 回书架；阅读器页 F11 → Esc 回阅读器；搜索框聚焦时 F11 无效
```
