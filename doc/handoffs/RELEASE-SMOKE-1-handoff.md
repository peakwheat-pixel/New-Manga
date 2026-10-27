# RELEASE-SMOKE-1 Handoff（新包真机全流程快检）

- Task: `doc/tasks/RELEASE-SMOKE-1.md`（team task-51）
- Branch: `task/RELEASE-SMOKE-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/RELEASE-SMOKE-1`
- Base: 卡面 `13cf26f6c`；实际基于 Lead 指定的当前 HEAD **`170878dc4`**
- Delivery head: 见任务卡 Canonical Evidence 的 commit 列
- 安装包：`G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-2/out/NewManga-0.1.0-win-x64-models`
- 未改产品源码/协议/Host 契约/旧壳；未 push；不删旧包；证据不含任何 secret。

## 1. 结论摘要

| AC | 判定 | 关键数字 |
|---|---|---|
| AC1 安装 | **MET** | 全新目录安装 **2.60s**；启动→Host 就绪 **4.10s**；console 窗口 **0**；sidecar 随包 1965 files / 868,862,035B |
| AC2 全流程 | **PARTIAL / BLOCKED（包过期）** | 书架/阅读器/滚动翻页/进度落库/沉浸模式真机通过；**导入与导出 UI 不在 REPACK-2 包内**（包 repo_head=`0f4b836a5`，UI 合入 commit=`13cf26f6c`）→ 导入、导出 ZIP、打开导出目录 BLOCKED，未伪造 |
| AC3 稳定性 | **MET** | 关闭 4.08s、残留进程 0；卸载 exit=0、目录消失、数据根保留；注册表 0；凭据仅 1 条历史遗留（非本 Task） |
| AC4 真机 5 项 | **PARTIAL** | Mica **N/A**（Windows 10，backdrop type=0）；4K@200% **N/A**（2560×1440@96）；WS：app 147.5/411.9MB、core 41.1MB、bridge 22.7MB；IME 待用户确认；沉浸按钮（Esc/H/F 组）真机验证，键盘 Esc/H 待前台确认 |
| AC5 门禁 | **MET** | check.ps1 PASS；64-hex pin；Handoff |

## 2. 关键证据

| 文件 | 内容 |
|---|---|
| `screens/09-fresh-install-bookshelf.png` | 全新安装后启动书架（1 本 8 页） |
| `screens/02-bookshelf-loaded.png` | 书架加载与 Host 就绪 |
| `screens/03-workbench.png` | 工作台：旧 UI（无导入入口）→ AC2 导入 BLOCKED 证据 |
| `screens/04-reader.png` | 阅读器 + 工具栏（无导出按钮） |
| `screens/05-reader-page2.png` | 滚动翻页后内容 |
| `screens/06-immersive.png` | 沉浸模式（无边框全屏、chrome 隐藏） |
| `screens/08-mica-window.png` | Mica/窗口像素采样（Windows 10 不透明背景） |
| `package-evidence.json` | 包 VERSION repo_head、UI 字符串探测 0 命中、结论 |
| `smoke.json` | AC1–AC4 全部数字汇总 |
| `host.log` / `install-timed.log` / `uninstall-timed.log` / `core-service.ndjson` | 启动/安装/卸载时间线与 wire |

## 3. 复现

```powershell
$env:NEWMANGA_DATA_ROOT='<task-env>/data-root'   # REPACK-2 completed-run 私有副本
# 1) 全新安装
pwsh -File apps/desktop-avalonia/scripts/install.ps1 `
  -PackageDir 'G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-2/out/NewManga-0.1.0-win-x64-models' `
  -InstallDir '<task-env>/install' -DataRoot $env:NEWMANGA_DATA_ROOT -SkipBackup
# 2) 启动（无 console；Host 就绪）
& '<task-env>/install/app/NewManga.App.exe' `
  --data-root=$env:NEWMANGA_DATA_ROOT `
  --sidecar-dir='<task-env>/install/app/core-sidecar' --parity --log-dir='<task-env>/app-logs'
# 3) 书架→书→阅读器；滚动翻页；工具栏「沉浸模式」；进度落库 reading_progress
# 4) WM_CLOSE 关闭；uninstall.ps1；检查残留
```

自动化说明：本机前台被用户 DSH 窗口占用，键盘输入无法送达 App；使用
UIA InvokePattern（按钮）+ WM_MOUSEWHEEL（滚动）+ WM_CLOSE（关闭）完成真机操作，键盘
Esc/H 与 IME 标注为待用户前台确认。

## 4. 遗留 / 建议

1. **发布阻塞**：REPACK-2 包不含 IMPORT-EXPORT-UI-1；需 **RELEASE-REPACK-3**（HEAD `170878dc4` 或更新）
   后重跑导入→阅读→导出 ZIP 全流程，才能关闭 AC2。
2. AC4：Mica 与 4K@200% 需对应硬件/Windows 11 环境复验；IME 与键盘 Esc/H 需用户前台人工确认。
3. 凭据管理器历史遗留 `NewManga/provider/p15-host-2-smoke/…` 建议 DSH 裁决清理（非本 Task 产生）。
4. 本 Task 零产品代码改动；仅脚本目录未改（只新增 `verification/RELEASE-SMOKE-1/**`）。
