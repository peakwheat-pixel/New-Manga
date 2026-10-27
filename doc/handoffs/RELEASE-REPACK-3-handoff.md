# Handoff — RELEASE-REPACK-3（第三次重打包与全流程复验）

- Task: `doc/tasks/RELEASE-REPACK-3.md`（team task-53）
- Branch/Worktree: `task/RELEASE-REPACK-3` / `G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-3`
- Base / 构建 HEAD: **`dd2408869ce1d43f4d1dd0525ef1b13bb75bb38c`**
- Delivery head: 见任务卡 Canonical Evidence 的 commit 列（本 Handoff 随最终 pin commit 更新）
- 新包: `G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-3/out/`
  - `NewManga-0.1.0-win-x64.zip`（103,326,248B）
  - `NewManga-0.1.0-win-x64-models.zip`（**725,334,588B**）
- 旧包对照（未动）：`task-envs/RELEASE-REPACK-2/out`（models zip 724,989,976B）
- 未 push、未 gc/prune、未删旧包；真实 `%APPDATA%` 书库/凭据库未触碰。

## 1. 结论摘要

| AC | 判定 | 关键数字 |
|---|---|---|
| AC1 | MET | 新 sidecar：base `65d7b55a…` / models `8cfc9080…`（≠ 旧 `091a201d…`/`c5531930…`）；VERSION `repo_head=dd2408869…`；torch-free PASS（无 `_internal/torch`，有 onnxruntime） |
| AC2 | MET（PDF 除外） | 安装 2.45s、Host 就绪 1.13s、console 0；导入 1 文件（8→9 页，DB pages=9）；进度 13.55%/87.37s；沉浸全屏；**导出 ZIP 7,070,562B sha256 `d77ecf88…36f7`**（3 翻译页+manifest）；打开导出目录 2.9s；**PDF UI 未实现（PDF-EXPORT-UI-1 仅释放）** |
| AC3 | 结论已给 | OS=Windows 11 26H2 build 26300.9711；**Mica actual=Mica**（app 日志）；主屏 2560×1440@100%，副屏 3840×2160@**150%** → **4K@200% NOT_AVAILABLE**；纠正 smoke 的 Win10 判断 |
| AC4 | MET | console 0；WM_CLOSE 4.16s；本安装 0 残留；卸载 exit=0、目录消失、数据根保留；注册表 0；凭据 2 条历史残留只上报 |
| AC5 | MET | 干净 worktree `test.ps1` **234/234 PASS**；pytest 3F/2772P/9S 与基线失败集合一致；check.ps1 PASS；64-hex pin；Handoff |

## 2. 关键证据

| 文件 | 内容 |
|---|---|
| `verification/RELEASE-REPACK-3/package-hashes.json` | 新/旧 zip sha256+大小、sidecar sha、torch-free 断言 |
| `verification/RELEASE-REPACK-3/smoke.json` | 全流程每步结果/耗时、导出产物 sha、稳定性、设备/DPI/Mica |
| `verification/RELEASE-REPACK-3/environment.json` | OS/显示器/DPI/Mica 结论与矛盾修正 |
| `verification/RELEASE-REPACK-3/REPORT.md` | 完整报告 |
| `screens/01–11` | 书架/工作台/导入面板/导入结果/阅读器/滚动/沉浸/导出面板/导出进度/导出目录/导入选择器 |
| `dotnet-all.log` / `pytest.log` | 门禁原始日志（TEST PASS 234/234；3F/2772P/9S） |
| `host.log` / `install-timed.log` / `uninstall-timed.log` | 启动/安装/卸载时间线 |
| `mica-window-material.log` | app 诊断日志（`actual=Mica`） |

## 3. 复现要点

```powershell
# 1) sidecar 构建（当前 HEAD）
pwsh -File packaging/m2ac5/build_sidecar.ps1 -Force -SkipWeights   # base
pwsh -File packaging/m2ac5/build_sidecar.ps1 -Force                # models
# 2) 打包
pwsh -File apps/desktop-avalonia/scripts/package.ps1 -OutputRoot <out> -SidecarDir <base>
pwsh -File apps/desktop-avalonia/scripts/package.ps1 -OutputRoot <out> -SidecarDir <models> -WithModels
# 3) 全新安装 + 启动（独立 mutex 规避并发 Agent 的 Host 单实例占用）
pwsh -File apps/desktop-avalonia/scripts/install.ps1 -PackageDir <out\NewManga-0.1.0-win-x64-models> -InstallDir <install> -DataRoot <data> -SkipBackup
& <install>\app\NewManga.App.exe --data-root=<data> --sidecar-dir=<install>\app\core-sidecar --parity --mutex-name=NewManga.ReleaseRepack3.Smoke2 --log-dir=<logs>
```

自动化：UIA InvokePattern（导航/按钮）、UIA `SelectionItemPattern.Select()`+`WM_COMMAND IDOK`（系统文件选择器）、
WM_MOUSEWHEEL（滚动）、WM_CLOSE（关闭）；键盘 Esc/H 与 IME 标注待用户前台确认。

## 4. 遗留 / 需 DSH 裁决

1. **PDF 导出 UI 未实现**：PDF-EXPORT-UI-1（2591ef028 仅为释放）需实现后重打复验；当前导出面板仅 ZIP。
2. **4K@200% 未验**：本机副屏 4K@150%，无 200% 配置；MICA-FIX-1 的 DPI=192 为 DPR2 仿真证据。
3. **键盘 Esc/H 与 IME**：待用户前台人工确认。
4. **凭据管理器 2 条历史残留**（p15-host-2-smoke、3819f991…）：只上报，未删除。
5. **范围偏差需确认**：`apps/desktop-avalonia/src/NewManga.Host/HostCredentialCoordinator.cs`
   的证据 JSON 序列化改为 `Utf8JsonWriter(Indented=true)`，用于解 Release `PublishTrimmed` 的
   **error IL2026**（否则无法出包）；不改 Host 契约/语义。该文件超出本卡 allowed_paths。
6. 新包在 `task-envs/RELEASE-REPACK-3/out`；旧包保留。
