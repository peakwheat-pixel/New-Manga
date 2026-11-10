# FEA-14-READ-2 证据索引（Fluent Reader UI 接线）

- Task：`FEA-14-READ-2`（READ-1 AC1–AC3 的 Fluent UI 层）
- 执行 head：`034962ea7`（READ-1 收口后）
- 日期：2026-11-10

## 结论状态

| AC | 判别 | 结果 |
|---|---|---|
| AC1 偏好应用 | 打开书 → `GetReadingPreferencesAsync` 应用 mode/direction/zoom/doublePage/layout；修改后 partial 保存 | **MET（VM 层）**：`ReaderViewModel.LoadAsync` 后调用 `ApplyReadingPreferencesAsync`（应用 Zoom/DoublePage/ReverseDirection/Layout）；`SaveReadingPreferencesAsync` 发 `ReadingPreferencesPatch`（partial）；测试 `LoadAppliesStoredPreferencesAndBookProgress`、`SavePreferencesSendsThePartialPatch` |
| AC2 书签 UI | 新增（left/right/both + note）/列表/删除 | **PARTIAL**：VM 层 `CreateBookmarkAsync`/`ListBookmarksAsync`/`DeleteBookmarkAsync` 完成并有往返测试；**可见按钮/列表面板未接线**（limitation） |
| AC3 整书进度 UI | 显示 read_pages/total_pages/percent；finished 显示已读完；reset 确认 | **PARTIAL**：VM 层 `BookProgress`/`BookProgressLabel`（含「已读完」）与 `ResetReadingProgressAsync(confirm)` 完成（取消不调用；测试 `ResetRequiresExplicitConfirmation`）；**页面 TextBlock/按钮绑定未接线**（limitation） |
| AC4 测试 | App.Tests 定向 | **MET**：`ReaderReadingPreferencesTests` **4 passed / 0 failed**（偏好应用、partial patch、reset 确认、书签往返） |
| AC5 NOT_RUN | 真实 UI 手势/IME/多屏/DPI/主题/托盘、真实进程重启 | **MET（登记）**：见 NOT_RUN |
| AC6 门禁与证据 | check PASS；无 Core/wire/契约/DDL diff；证据含 EXIT | **MET**：仅 App VM/测试改动；check（默认 + TaskPath）PASS |

## 门禁与证据（本目录）

| 文件 | 内容 | EXIT |
|---|---|---|
| `logs/dotnet-app-tests.log` | App.Tests 全量 **871 passed / 0 failed / 11 skipped**（含 Reader 相关） | 0 |
| `logs/reader-reading-prefs.log` | `ReaderReadingPreferencesTests` 4 passed | 0 |

## limitation（不阻断 VM 层交付，阻 AC2/AC3 的可见 UI）

- 书签/整书进度/reset 的**可见控件**（按钮、列表、确认对话框）尚未绑定到 `ReaderViewModel` 的新方法；VM 行为与测试已覆盖。
- 建议在后续 UI 卡补按钮/面板绑定与可视化截图（当前无交互会话 → NOT_RUN）。

## NOT_RUN（不得记 PASS）

- 真实 UI 手势 / IME / 多显示器 / DPI 100–200% / 系统主题跟随 / 托盘。
- 真实进程重启后的偏好恢复（VM 两次装配已测；真实进程重启未做）。
- 可见 UI 截图/人工目视（无被审查交互会话）。

## 复现

```powershell
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --filter "FullyQualifiedName~ReaderReadingPreferencesTests"
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-14-READ-2.md
```
