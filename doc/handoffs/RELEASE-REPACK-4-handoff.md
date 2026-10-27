# Handoff — RELEASE-REPACK-4（最终发布包 + 端到端含 PDF）

- Task: `doc/tasks/RELEASE-REPACK-4.md`（team task-55）
- Branch/Worktree: `task/RELEASE-REPACK-4` / `G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-4`
- 构建 HEAD: **`f1b89c5e5`**（含 Lead 修复 `4be1c3f4f`；原 base `84dd38978` 编译失败，证据 `build-head-failure.log`）
- Delivery head: 见任务卡 Canonical Evidence 的 commit 列
- 新包: `G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-4/out/`
  - `NewManga-0.1.0-win-x64.zip`（103,330,812B）
  - `NewManga-0.1.0-win-x64-models.zip`（**725,339,894B**）
- 旧包对照（未动）: `task-envs/RELEASE-REPACK-3/out`
- 未 push、未 gc/prune、未删旧包；真实 `%APPDATA%` 书库/凭据库未触碰。

## 1. 结论摘要

| AC | 判定 | 关键数字 |
|---|---|---|
| AC1 | MET | 新 sidecar base `bd23e66f…` / models `3909a4a2…`（≠ REPACK-3 `65d7b55a…`/`8cfc9080…`）；VERSION `repo_head=f1b89c5e5…`；torch-free PASS |
| AC2 | MET（含 PDF） | 安装 2,545.5ms、Host 就绪 1,100.1ms、console 0；导入 1 文件 9→10 页；阅读/滚动；沉浸（按钮）；**PDF 20,728,075B sha256 `c0a97eb3…b210` 3 页 searchable_dual_layer**；ZIP 7,070,562B sha256 `72d81db9…945c`；打开导出目录 2.9s |
| AC3 | 部分 | Mica **本次 actual=None**（REPACK-3 曾 actual=Mica，需复核）；4K@200% **NOT_AVAILABLE**（4K 屏未在桌面扩展；主屏 100%）；WS App 526.7 / core 44.5 / bridge 23.7MB；Esc/H 前台已取得+真键盘已发但 UI 无变化（PARTIAL）；IME N/A |
| AC4 | MET | WM_CLOSE 4,267.9ms、本安装 0 残留；卸载 exit=0、目录消失、数据根保留；注册表 0；凭据 2 条历史残留只上报 |
| AC5 | MET | 干净 worktree `TEST PASS 232/232`；pytest 0F/2773P/10S；check.ps1 PASS；64-hex pin；Handoff |

## 2. 关键证据

| 文件 | 内容 |
|---|---|
| `verification/RELEASE-REPACK-4/smoke.json` | 全流程步骤/耗时/PDF+ZIP 产物的 sha256、稳定性、设备项 |
| `verification/RELEASE-REPACK-4/package-hashes.json` | 新/旧 zip + sidecar sha、torch-free |
| `verification/RELEASE-REPACK-4/environment.json` | OS/显示器/DPI/Mica/Esc-H 结论 |
| `verification/RELEASE-REPACK-4/REPORT.md` | 完整报告（含 base 阻塞与修复） |
| `screens/01–14` | 书架/导入面板/导入结果/阅读器/滚动/沉浸/PDF 面板/PDF 完成/ZIP 完成/导出目录/前台 Esc-H 截图 |
| `dotnet-all.log` / `pytest.log` | 232/232、0F/2773P/10S |
| `build-head-failure.log` | 原 base `84dd38978` 的 CS1061 证据 |
| `host.log` / `install-timed.log` / `uninstall-timed.log` | 时间线 |

## 3. 复现

```powershell
# 构建（HEAD f1b89c5e5）
pwsh -File packaging/m2ac5/build_sidecar.ps1 -Force -SkipWeights   # base
pwsh -File packaging/m2ac5/build_sidecar.ps1 -Force                # models
pwsh -File apps/desktop-avalonia/scripts/package.ps1 -OutputRoot <out> -SidecarDir <base>
pwsh -File apps/desktop-avalonia/scripts/package.ps1 -OutputRoot <out> -SidecarDir <models> -WithModels
# 安装/启动（独立 mutex 规避并发 Agent Host 单实例）
pwsh -File apps/desktop-avalonia/scripts/install.ps1 -PackageDir <out\...-models> -InstallDir <install> -DataRoot <data> -SkipBackup
& <install>\app\NewManga.App.exe --data-root=<data> --sidecar-dir=<install>\app\core-sidecar --parity --mutex-name=NewManga.ReleaseRepack4.Smoke --log-dir=<logs>
```

面板：格式选择 `ExportFormatSelector`（ZIP/PDF）、`ExportPdfModeSelector`（searchable=index0）、开始导出 `ExportStartButton`；PDF 参数 `format=pdf` + `format_options.pdf_content=searchable_dual_layer`。

## 4. 遗留 / 需 DSH 裁决

1. **Mica 疑似回归**：REPACK-4 本次 actual=None；REPACK-3 同机 actual=Mica。建议复核是否与 `4be1c3f4f` 回退 UI 文件有关。
2. **4K@200%**：本机 4K（Mi TV 3840×2160）当前不在桌面扩展；需活跃 4K 桌面复验 200%（REPACK-3 时为 150%）。
3. **Esc/H 键盘**：前台已取得、真实键事件已发送但截图无变化；需用户真机确认（按钮路径已验证沉浸）。
4. **凭据 2 条历史残留**（p15-host-2-smoke、3819f991…）：只上报，未删除。
5. 导入选择器临时文件 `ui-import-4.png` 已删除并还原 `IMPORT-EXPORT-UI-1/import-src`。
