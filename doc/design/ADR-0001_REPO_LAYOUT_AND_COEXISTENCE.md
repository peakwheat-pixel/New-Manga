# ADR-0001：仓库布局与新旧共存（AD-002 前置件 P2）

Status: ACCEPTED · Date: 2026-10-26 · Owner: DSH · 依据：[AD-002](../../AD-002_TARGET_DESKTOP_ARCHITECTURE.md)、[EXECUTION_DIRECTIVE_AD002_V2](EXECUTION_DIRECTIVE_AD002_V2.md) §3-P2、AC11 干净机复核结论

## 背景

- 新壳为 C#/.NET 9 + Avalonia；旧壳为 Tauri + React（S5 前需并行可运行）。
- 旧壳与新壳都要 spawn 同一批 Python Core sidecar，共享同一数据根（`%APPDATA%\com.newmanga.desktop`）。
- 本机 AC11 已证：从带 Low 强制标签的仓库树启动的 exe 会继承 Low IL，写数据根失败 → 非提权测试必须用无标签副本。

## 决策

### D1 目录布局

```
apps/
  desktop/                   # 旧壳（Tauri + React）——S5 前保留，S5 后 archive/
  desktop-avalonia/          # 新壳（.NET 9 + Avalonia 11）
    NewManga.sln
    src/NewManga.App/        # UI：四页 + 主题中心
    src/NewManga.Host/       # Host 服务层：sidecar 生命周期、IPC 编解码、资源/tile 读取
    src/NewManga.CoreClient/ # stdio JSON-lines 客户端（协议 2.3 + wire v1）
    src/NewManga.Theme/      # ThemePack 加载（ResourceDictionary/ControlTheme/DynamicResource）
    tests/                   # xunit + Avalonia.Headless
    artifacts/               # publish 输出（gitignored）
```

- 产品代码 Task 使用独立分支 `task/<TASK-ID>` + workspace worktree；证据/研究类 Task 可在 `main`。
- 构建产物统一落 workspace：`G:/CODEX/New Manga.workspace/task-envs/<TASK-ID>/`（不进仓库）。

### D2 安装标识与窗口标识

- **`identifier` 保持 `com.newmanga.desktop` 不变**（数据根路径由它派生，改标识=用户数据迁移风险）。
- 新旧壳用**窗口标题 + 安装包文件名**区分：旧壳 `New Manga (legacy)`、新壳 `New Manga`；beta 通道 `New Manga Beta`（仅安装包名/快捷方式名，不改 identifier）。
- 单文件发布配方（S0 spike 实测）：`PublishSingleFile + SelfContained + PublishTrimmed + IncludeNativeLibrariesForSelfExtract + ReadyToRun + 压缩` → 29.31MB。

### D3 数据根共用与写入纪律

- 数据根：`%APPDATA%\com.newmanga.desktop`（`derived/`、`managed/`、`catalog/`）**共用**。
- **单实例互斥**：Host 启动时申请全局命名 Mutex `Global\NewManga.Host`；已存在则聚焦已有窗口并退出（不得双写）。
- 迁移期：新壳在 **S2 parity 全绿前对生产数据只读**；首次运行自动备份（复用既有 `.nmbak` 能力）；任何写操作必须经 Core（SQLite 单写语义不变）。
- 旧壳运行中时新壳检测 `new-manga.exe` 进程存在 → 启动为只读模式或提示退出（二选一，S1 内定并测试）。

### D4 测试与运行规则

- 非提权运行/令牌相关测试：**必须从无标签副本运行**（zip 释放或重新拷贝到无标签目录）；直接从仓库树运行会被本机工作区保护降为 Low（AC11）。
- 端到端测试使用隔离 env（APPDATA/LOCALAPPDATA/TEMP/数据根/catalog/WebView2 UDD 全部重定向），不碰真实数据。

### D5 旧壳退役

- S5 才执行：`apps/desktop/**`（Tauri/React/Rust host）→ `archive/history/2026-XX/legacy-tauri-shell/`，并完成引用迁移与证据 pin 更新；**不删除、不 gc/prune**。

## 后果

- 并行 Task 的写路径现在互不重叠（旧壳 `apps/desktop`、新壳 `apps/desktop-avalonia`）。
- 数据根共用带来的双写风险由「单实例 Mutex + 只读期 + Core 单写」三重约束覆盖。
- 本机测试必须遵守「无标签副本」规则，否则会误判为产品故障。
