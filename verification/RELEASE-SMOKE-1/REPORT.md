# RELEASE-SMOKE-1 报告：新包真机全流程快检

- Task: `doc/tasks/RELEASE-SMOKE-1.md`（team task-51）；Branch/Worktree: `task/RELEASE-SMOKE-1` /
  `G:/CODEX/New Manga.workspace/worktrees/RELEASE-SMOKE-1`
- Base: 卡面 `13cf26f6c`；按 Lead 指示基于当前 HEAD **`170878dc4`**（含 IMPORT-EXPORT-UI-1）。
- 安装包：`task-envs/RELEASE-REPACK-2/out/NewManga-0.1.0-win-x64-models`（724,989,976B）。
- 隔离数据根：`task-envs/RELEASE-SMOKE-1/data-root`（REPACK-2 completed-run 私有副本，真实 `%APPDATA%` 零触碰）。
- 未改产品源码/协议/Host 契约/旧壳；未 push；不删旧包；证据无 secret。

## 0. 结论（重要发现）

| AC | 判定 | 要点 |
|---|---|---|
| AC1 安装 | **MET** | 全新目录安装 models 包：**2.60s** 完成；启动到 Host 就绪 **4.10s**；**console 窗口 0**；sidecar 随包 **1965 files / 868,862,035B**；窗口 "New Manga"、书架 1 本书 8 页 |
| AC2 全流程 | **PARTIAL / BLOCKED（包过期，非本机问题）** | 书架→阅读器→滚动翻页→进度落库→沉浸模式 全部真机通过；**导入/导出不可用**：REPACK-2 包构建于 `0f4b836a5`，早于 IMPORT-EXPORT-UI-1（`13cf26f6c`），安装包内**无导入/导出 UI**（exe 内无 导入文件/开始导出/打开导出目录 字符串；工作台/阅读器无对应控件）→ 导入、导出 ZIP、打开导出目录均 **BLOCKED**（未伪造） |
| AC3 稳定性 | **MET** | WM_CLOSE 优雅退出 **4.08s**，**残留进程 0**（app/core_service/host_bridge 全退）；卸载 exit=0、安装目录消失、数据根未动；注册表 NewManga 项 **0**；凭据管理器仅 1 条**历史遗留**（`NewManga/provider/p15-host-2-smoke/…`，旧 Tauri 测试产生，非本 Task 写入，未删） |
| AC4 真机 5 项 | **PARTIAL（环境不满足 + 需用户确认）** | **Mica：N/A**（本机 Windows 10 26H2 build 26300；DWM backdrop type=0，窗口像素不透明：标题栏 #FFFFFF / 主体 #F5F3FA）；**4K@200%：N/A**（实际 2×2560×1440 @96DPI=100%，需 4K@200% 机器复验）；工作集 App 空闲 147.5MB / 阅读滚动时 411.9MB、core_service 41.1MB、host_bridge 22.7MB；**IME：需用户确认**（任务已标注）；**Esc/H：沉浸按钮（Esc/H/F 同组）真机触发为无边框全屏、导航/状态栏隐藏**；键盘 Esc/H 在自动化会话中无法取得前台焦点（用户 DSH 窗口持有前台），需用户前台确认 |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；64-hex pin；Handoff；未 push、未删旧包 |

## 1. AC1 安装（全新目录）

| 项 | 值 |
|---|---|
| 安装目录 | `task-envs/RELEASE-SMOKE-1/install`（全新，安装前不存在） |
| 安装耗时 | **2,602.8ms**（`install.ps1`，含 868,862,035B sidecar 复制与 license 校验） |
| 启动→Host 就绪 | **4,098.0ms**（`host.log` host-control session opened） |
| console 窗口 | **0**（EnumWindows 按 pid 统计 Console 类） |
| sidecar 随包 | **1965 files / 868,862,035B**，models_bundled=true |
| 进程 | app 147.5MB / core_service 41.1MB / host_bridge 22.7MB（空闲） |
| 截图 | `screens/09-fresh-install-bookshelf.png`（书架 1 本 8 页） |

## 2. AC2 全流程

| 步骤 | 结果 | 证据 |
|---|---|---|
| 书架 | 真机加载 fixture 书 `BOOK-FIXTURE-1 日漫_JA 测试书`（8 页） | `screens/02-bookshelf-loaded.png` |
| 导入 fixture 书 | **BLOCKED**：安装包为 REPACK-2（repo_head=`0f4b836a5`），不含 IMPORT-EXPORT-UI-1（`13cf26f6c`）的导入入口；工作台仅旧「缩略图/气泡检查器」 | `screens/03-workbench.png`、`package-evidence.json`（exe 字符串 0 命中） |
| 阅读器 | 打开书→第 1 章 webtoon 长滚动；工具栏 `Esc 退出 · F fit · H 隐藏 UI` | `screens/04-reader.png` |
| 翻页 | WM_MOUSEWHEEL 8 格 → 滚动到后续页内容 | `screens/05-reader-page2.png` |
| 进度 | `reading_progress` 落库：last_page_id=`f52f2772…`、scroll_offset_y=37.5、progress_percent=2.26、total_read_seconds=68.32 | `smoke.json` |
| 沉浸 Esc/H | UIA Invoke `ImmersiveButton`（标签「沉浸模式 (Esc/H/F)」）→ 无边框全屏、导航/状态栏隐藏 | `screens/06-immersive.png` |
| 导出 ZIP | **BLOCKED**：包内无「导出/开始导出」入口（同陈旧包原因）；未执行任何导出 | `screens/04-reader.png`、`package-evidence.json` |
| 打开导出目录 | **BLOCKED**（同上） | — |

说明：`App` 的导入/导出 UI 是 main 上 `13cf26f6c` 才合入的，而 REPACK-2 包构建于 `0f4b836a5`。
本机用该包无法完成导入/导出；需重新打包（REPACK-3）后复跑本 AC。

## 3. AC3 稳定性

- 关闭方式 WM_CLOSE（等价点 X）：**4,084.3ms** 优雅退出；app/core_service/host_bridge **0 残留**。
- 卸载 `uninstall.ps1`：exit=0、安装目录不存在、数据根保留（用户数据不删）。
- 系统残留：HKCU/HKLM `*NewManga*` 注册表键 **0**；凭据管理器 **1 条历史遗留**（`NewManga/provider/p15-host-2-smoke/4131fe…`，旧 Tauri smoke 产生，未由本 Task 创建/未删）；`%TEMP%` 仅旧 task-env 目录，无本次安装残留。
- 证据：`host.log`、`install-timed.log`、`uninstall-timed.log`、`core-service.ndjson`。

## 4. AC4 真机 5 项

| 项 | 实测 | 判定 |
|---|---|---|
| Mica 取色 | OS = Windows 10 Pro 26H2（build 26300）；`DwmGetWindowAttribute(DWMWA_SYSTEMBACKDROP_TYPE)` hr=0、type=0；窗口边缘采样不透明（标题栏 #FFFFFF、主体 #F5F3FA） | **N/A（Windows 10 无 Mica）** |
| 4K@200% DPI | 2 屏 2560×1440、系统 DPI=96（100%） | **N/A（环境不符，需 4K@200% 机器）** |
| 工作集 | app 空闲 147.5MB / 阅读滚动 411.9MB；core_service 41.1MB；host_bridge 22.7MB | **MET（记录）** |
| IME | 任务明确「标注需用户确认」；自动化无 IME 注入/验证能力 | **待用户确认** |
| Esc/H | 沉浸按钮（Esc/H/F 同组）真机触发：无边框全屏 + chrome 隐藏（`screens/06-immersive.png`）；键盘 Esc/H 需前台焦点，自动化会话被用户 DSH 窗口占前台，未验证 | **PARTIAL / 待用户前台确认** |

## 5. AC5 门禁

`check.ps1 -TaskPath doc/tasks/RELEASE-SMOKE-1.md` **PASS**（2 条既有 WARN）；证据 pin 见任务卡；Handoff 已交付；
未 push、未删旧包、未触碰真实 `%APPDATA%` 书库/凭据库。

## 6. 遗留 / 建议

1. **发布阻塞**：REPACK-2 包不含 IMPORT-EXPORT-UI-1（`13cf26f6c`）→ 导入/导出 UI 与真机导出 ZIP 无法验收。
   建议 **RELEASE-REPACK-3**（当前 HEAD `170878dc4`）后重跑本 AC2，届时可走真实导入→阅读→翻译/导出链路。
2. AC4：Mica 与 4K@200% 需在支持环境复验；IME 与键盘 Esc/H 需用户前台人工确认。
3. 凭据管理器 1 条历史遗留（`p15-host-2-smoke`）建议由 DSH 裁决清理（非本 Task 产生）。
4. 未改任何产品代码；本 Task 只新增证据。
