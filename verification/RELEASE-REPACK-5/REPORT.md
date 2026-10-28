# RELEASE-REPACK-5 报告：第五次重打包（含三布局主题）与安装验收

- Task: `doc/tasks/RELEASE-REPACK-5.md`（team task-57）
- Branch/Worktree: `task/RELEASE-REPACK-5` / `G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-5`
- 构建 HEAD：**`6120f91e5`**（含 `679967c6e` 主题合并；`7a79e5522` superset 三布局）
- 新包：`task-envs/RELEASE-REPACK-5/out/`；旧包对照 `task-envs/RELEASE-REPACK-4/out`（未动）
- 未 push、未删旧包；真实 `%APPDATA%` 书库/凭据库未触碰。

## 1. AC1 重打包（MET）

| 产物 | 大小 | sha256 |
|---|---|---|
| base zip | **103,374,546B** | `7e178f29aba35a1fb9eb1941ee66828d3c1127e387c187233c12fe427b42bbff` |
| models zip | **725,382,787B** | `41b330f575f28e62e1b5b566f1ba5c4ba90dd6b5d251d0adf069b99974a9d32e` |
| 旧 REPACK-4 | 103,330,812 / 725,339,894B | `cbd1b9e1…` / `aaa02c8b…` |

- sidecar：base `28ba3bb9…8cda`、models `bde2d866…bc7a`（≠ REPACK-4 的 `bd23e66f…`/`3909a4a2…`，未复用旧 exe）
- 安装后 `VERSION.repo_head=6120f91e5…`、`core_service_sha256=bde2d866…`
- **torch-free PASS**：models bundle 无 `_internal/torch`，含 onnxruntime

## 2. AC2 安装 + 主题验收（MET，实际 9 packs）

- 全新安装 **2,549.2ms**；启动→Host 就绪 **4,112.6ms**；窗口 "New Manga"、Host 就绪
- 设置页主题列表**全部可见 9 packs**（任务预期 7；实际注册表 `ThemePacks.All` = 6 legacy + 3 macOS 三布局 = 9，属超集，按实际记录）：
  `saber-purple(默认), saber-light, midnight, sakura, emerald, mono, macos-sonoma(风), macos-launchpad(启动台), macos-split(分栏)`
- 切换生效（截图）：
  - `screens/01-settings-themes.png` 全列表
  - `screens/02-theme-macos-sonoma.png`（顶部标题栏导航 · 居中 1400）
  - `screens/02-theme-macos-launchpad.png`（**底部 Dock 导航** + 居中卡片，布局生效）
  - `screens/02-theme-macos-split.png`（**左侧 Sidebar 导航** + 分栏设置，布局生效）
  - `screens/10-theme-default-restored.png` 切回默认

## 3. AC3 冒烟

| 步骤 | 结果 |
|---|---|
| 书架 | 正常（BOOK-FIXTURE-1，10 页）`screens/03-bookshelf.png` |
| **导入** | **BLOCKED（本包/本机实测）**：选择文件→「开始导入」后 ImportStatus 长时间停在「正在导入文件…」>40s，DB pages 保持 10 不增；书架入口、工作台入口、默认主题、已知重复 fixture 均复现；wire 仅见 `RegisterImportSource`/`RevokeImportSource`，**无 `ImportPages`/`ImportFiles` 请求**（`import-wire-tail.ndjson`）。同数据根在 REPACK-4 包（f1b89c5e5）导入正常，且 `ImportExportPanels/HostController` 与该包无 diff → **疑似回归/环境问题，需 DSH triage**；未伪造成功。证据 `screens/04*.png`、`05-import-result.png` |
| 阅读器 | 进入阅读成功（10 页 webtoon）`screens/06-reader.png`、`10-reader-restored.png` |
| 沉浸 Esc/H | 沉浸按钮进入；`SetForegroundWindow(阅读器)` 后真实 `keybd_event`：H 后 UI 变化（sha16 `238C10E2…`→`CCC9E3AE…`），Esc 后回到 before sha（`1D3E3CBF…`，退出沉浸）→ **PASS** |
| 导出 ZIP | **导出完成**：`…-第 1 章-20261028-010058.zip` **7,070,562B**、sha256 `5cfffa9f52fd2ab5967d40b6b6fcf1341a45e31b8670128feb0a5c4263e33609`、4 entries（3 翻译页+manifest）；耗时 ~9.4s；`screens/08-export-panel.png` |

## 4. AC4 门禁（MET）

- 干净 worktree `test.ps1`：**TEST PASS 249/249**（CoreClient 61 + Host 56 + App 132；186.6s）→ `dotnet-all.log`
- pytest：**0 failed / 2773 passed / 10 skipped**（212.04s）→ `pytest.log`（与既有基线一致，无新增）
- `check.ps1 -TaskPath doc/tasks/RELEASE-REPACK-5.md`：PASS
- 64-hex pin（见任务卡 Canonical Evidence）；Handoff 已交付

## 5. AC5 遗留说明

Launchpad / Split 仅按真机截图记录布局效果（见 §2），不做完整视觉验收（另行小卡）。

## 6. 稳定性

WM_CLOSE 退出 **4,116.1ms**；本安装 0 残留；卸载 exit=0、目录消失、数据根保留；注册表 `*NewManga*` **0**；凭据管理器 2 条历史/他 Agent 残留（`p15-host-2-smoke`、`3819f991…`），只上报未删。
设备：console 窗口 **0**；工作集 App **311.7MB**、core_service 41.7MB、host_bridge 23.5MB；Mica fresh launch **actual=Mica**（`2026-10-28T00:59:54Z` 日志）；IME N/A（需人工）。

## 7. 遗留风险

1. **导入 BLOCKED**：本包与 REPACK-4 导入代码无 diff，但本环境稳定复现卡死（无 ImportPages 请求）→ 需 DSH 判定是 HEAD 回归还是环境/数据根问题；建议用**干净新数据根**（非本例 REPACK-4 副本）复测导入。
2. 主题数量：实际 9（>预期 7），需确认验收口径是否按 9（含 6 legacy）。
3. 4K@200% 仍受 Mi TV 未加入桌面扩展限制（见 REPACK-4/补证）。
