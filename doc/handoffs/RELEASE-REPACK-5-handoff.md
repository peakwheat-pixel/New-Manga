# Handoff — RELEASE-REPACK-5（含三布局主题重打包与安装验收）

- Task: `doc/tasks/RELEASE-REPACK-5.md`（team task-57）
- Branch/Worktree: `task/RELEASE-REPACK-5` / `G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-5`
- 构建 HEAD: **`6120f91e5`**（含 `679967c6e` 主题合并 / `7a79e5522` 三布局 superset）
- Delivery head: 见任务卡 Canonical Evidence 的 commit 列
- 新包: `G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-5/out/`
  - `NewManga-0.1.0-win-x64.zip`（103,374,546B，sha256 `7e178f29…bbff`）
  - `NewManga-0.1.0-win-x64-models.zip`（**725,382,787B**，sha256 `41b330f5…d32e`）
- 旧包对照（未动）: `task-envs/RELEASE-REPACK-4/out`
- 未 push、未 gc/prune、未删旧包；真实 `%APPDATA%` 书库/凭据库未触碰。

## 1. 结论摘要

| AC | 判定 | 关键结果 |
|---|---|---|
| AC1 重打包 | MET | 新 sidecar base `28ba3bb9…8cda` / models `bde2d866…bc7a`（未复用旧 exe）；VERSION `repo_head=6120f91e5…`；torch-free PASS |
| AC2 主题验收 | MET | 设置页实际 **9 packs**（预期 7，实际 6 legacy + 3 macOS 三布局超集）；macOS 风/启动台/分栏均切换生效，2 张以上布局截图 |
| AC3 冒烟 | **PARTIAL** | 书架/阅读/沉浸 Esc/H（PASS，sha 判据）/导出 ZIP 成功（7,070,562B sha256 `5cfffa9f…33609`）；**导入 BLOCKED**（状态卡「正在导入文件…」>40s、无 ImportPages 请求），已保留失败证据，需 triage |
| AC4 门禁 | MET | 干净 worktree `TEST PASS 249/249`；pytest 0F/2773P/10S；check.ps1 PASS；64-hex pin；Handoff |
| AC5 | 记录 | Launchpad/Split 仅截图记录，完整视觉验收另卡 |

## 2. 关键证据

| 文件 | 内容 |
|---|---|
| `verification/RELEASE-REPACK-5/smoke.json` | 主题 9 packs + 切换截图、导入 BLOCKED 明细、Esc/H sha、导出 ZIP sha、稳定性、设备 |
| `verification/RELEASE-REPACK-5/package-hashes.json` | 新/旧 zip + sidecar sha、torch-free |
| `verification/RELEASE-REPACK-5/environment.json` | OS/显示器/Mica actual=Mica/IME |
| `verification/RELEASE-REPACK-5/REPORT.md` | 完整报告（含导入 BLOCKED 与主题 7→9 口径说明） |
| `verification/RELEASE-REPACK-5/import-wire-tail.ndjson` | 导入卡死时的 Core wire（仅 Register/RevokeImportSource） |
| `screens/01-settings-themes.png` | 设置页 9 packs 全列表 |
| `screens/02-theme-macos-{sonoma,launchpad,split}.png` | 三套 macOS 布局切换生效 |
| `screens/03-bookshelf.png`、`06-reader.png`、`10-reader-restored.png` | 书架/阅读器 |
| `screens/04*-import-*.png`、`05-import-result.png` | 导入面板与卡死状态 |
| `screens/08-export-panel.png` | 导出面板（ZIP 完成） |
| `dotnet-all.log` / `pytest.log` | 249/249；0F/2773P/10S |

## 3. 复现

```powershell
# 构建（HEAD 6120f91e5）
pwsh -File packaging/m2ac5/build_sidecar.ps1 -Force -SkipWeights   # base
pwsh -File packaging/m2ac5/build_sidecar.ps1 -Force                # models
pwsh -File apps/desktop-avalonia/scripts/package.ps1 -OutputRoot <out> -SidecarDir <base>
pwsh -File apps/desktop-avalonia/scripts/package.ps1 -OutputRoot <out> -SidecarDir <models> -WithModels
# 安装/启动（独立 mutex）
pwsh -File apps/desktop-avalonia/scripts/install.ps1 -PackageDir <out\...-models> -InstallDir <install> -DataRoot <data> -SkipBackup
& <install>\app\NewManga.App.exe --data-root=<data> --sidecar-dir=<install>\app\core-sidecar --parity --mutex-name=NewManga.ReleaseRepack5.Smoke --log-dir=<logs>
```

## 4. 遗留 / 需 DSH 裁决

1. **导入 BLOCKED（优先）**：书架/工作台两个入口、默认主题、已知重复 fixture 均复现；wire 无 `ImportPages`。`ImportExportPanels/HostController` 与 REPACK-4（导入正常）无 diff → 建议用**干净新数据根**复测，判定是否为 HEAD 回归或本数据根（REPACK-4 副本 + catalog 重建）问题。
2. **主题数量口径**：实际 9（6 legacy + 3 macOS），任务预期 7；需确认验收按 9。
3. **4K@200%** 仍受 Mi TV 未加入桌面扩展限制（REPACK-4/VERIFY-RECHECK-1 记录）。
4. **凭据 2 条历史残留**（p15-host-2-smoke、3819f991…）：只上报未删。
