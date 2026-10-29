# V11R-L4-EVIDENCE：真实窗口发布前证据（多尺寸 × 明暗 + legacy 回滚 + Host 就绪核查）

- Task：`V11R-L4-EVIDENCE`（Lead 2026-10-30 分配；真实窗口证据，不阻塞主线）
- Owner：`core-bridge`
- 分支：`v11r/core-bridge`，执行时 HEAD `287705e653d490941c6acf310d1acc2304355f05`
  （已含 INT-0/INT-1：`--shell=v2` 默认入口、`--shell=legacy` 回滚；含 A-6 启动自检）
- 脚本：`tools/e2e/v2-launch-matrix.ps1`
- 边界：本任务**只写** `tools/e2e/**` 与 `verification/V11R-L4-EVIDENCE/**`，未改产品代码/测试/契约。

## 1. 启动矩阵结果（真实窗口，非 headless）

7/7 通过（6 组 v2 + 1 组 legacy 回滚），7 张真实窗口截图，全部 exit 0：

| 组 | 尺寸 | 外观 | exit | 窗口实际像素（含边框） | Host 就绪 | 截图 |
|---|---|---|---:|---|---|---|
| v2-1600x1000-dark | 1600×1000 | dark | 0 | 1616×1039 | 否（见 §5 P0） | `screens/v2-1600x1000-dark.png` |
| v2-1600x1000-light | 1600×1000 | light | 0 | 1616×1039 | 否 | `screens/v2-1600x1000-light.png` |
| v2-1280x800-dark | 1280×800 | dark | 0 | 1296×839 | 否 | `screens/v2-1280x800-dark.png` |
| v2-1280x800-light | 1280×800 | light | 0 | 1296×839 | 否 | `screens/v2-1280x800-light.png` |
| v2-1024x700-dark | 1024×700 | dark | 0 | 1040×739 | 否 | `screens/v2-1024x700-dark.png` |
| v2-1024x700-light | 1024×700 | light | 0 | 1040×739 | 否 | `screens/v2-1024x700-light.png` |
| legacy-1280x800-dark | 1280×800 | dark | 0 | 1280×820 | **是** | `screens/legacy-1280x800-dark.png` |

- 机器可读：`launch-matrix.json`（逐组 pass/失败原因、EXIT_CODE、耗时、窗口标题/句柄、截图路径、
  host.log 路径、host_ready 诊断）；汇总 `summary = {total:7, passed:7, failed:0, host_ready_cases:1}`。
- 每组使用一次性隔离 `--data-root`（临时目录，跑完删除）与证据内 `--log-dir`（保留 host.log/wire）；
  每组唯一 `--mutex-name`，跑前清理残留 `NewManga.App`，窗口检测要求"本轮启动 + 标题 New Manga"。
- 截图方式：Win32/GDI `PrintWindow(PW_RENDERFULLCONTENT)`，失败回退 `CopyFromScreen`；**未使用 CUA**。

## 2. 脚本用法

```powershell
pwsh -NoProfile -File tools/e2e/v2-launch-matrix.ps1 `
  -SidecarDir "D:\NewManga.workspace\task-envs\HOST-CORECLIENT-1\sidecar-copy"
```

参数：

| 参数 | 说明 |
|---|---|
| `-SidecarDir` | 必需；打包 sidecar 目录（`core_service.exe` + `host_bridge.exe`）。默认取 `$env:NEWMANGA_CORECLIENT_SIDECAR_DIR`。缺文件时**直接失败**并给出可读原因。 |
| `-OutputRoot` | 证据根，默认 `<repo>/verification/V11R-L4-EVIDENCE`。 |
| `-TimeoutSeconds` | 窗口/退出超时（默认 90s）。 |
| `-SettleMs` | 窗口出现后等待首帧布局再截图（默认 1800ms）。 |
| `-SkipBuild` | 复用已有构建（默认先 `dotnet build NewManga.sln -warnaserror`）。 |
| `-IncludeLegacy` | 是否跑 legacy 回滚冒烟（默认 true；`-IncludeLegacy:$false` 跳过）。 |
| `-Configuration` | 默认 `Debug`。 |

前置：Windows 10/11 x64 交互桌面会话（真实窗口必须可见）、.NET 9 SDK、可用的 sidecar bundle；
脚本不触碰用户真实数据根（全部临时目录）。

如何解读失败：任何一组非 0 退出、窗口未出现/超时、截图失败 → 脚本 exit 1，并在
`launch-matrix.json.failures` 与 stdout 给出 `case + failure_reason`；`host_ready=false` 是**诊断**而非
矩阵失败条件（矩阵断言窗口+截图+exit 0），Host 就绪问题见 §5 与 `host-readiness.md`。

## 3. Host 就绪真实性核查（Lead 追加项）

完整结论见 [`host-readiness.md`](host-readiness.md)。摘要：

- **legacy 壳 + 正确 CLI 写法 + Lead 的 AGPL sidecar → Host 真实就绪**：`host.log` 含
  `core_service ready` / `host_bridge ready` / `self-check status=Degraded`（ReadWrite），`--data-root`
  被创建，截图 `screens/host-readiness-legacy.png` 显示"Host 就绪"。
- **v2 壳（当前默认）→ Host 从未启动**：不调用 `IHostController.StartAsync()`（唯一调用点在 legacy
  `MainWindow.axaml.cs:766`），因此无 host.log、无 data-root、状态栏永远"Host 未就绪"、exit 0。
  证据：`logs/host-readiness/v2/`（空）+ `screens/host-readiness-v2.png` + `host-readiness.json`。
- **Lead 命令的失败是另一层缺陷**：`--sidecar-dir "G:\..."` 这类**空格分隔值**被 `AppOptions.Parse`
  静默误解析（`--sidecar-dir`→`"true"`，路径 token 被忽略），`--data-root`/`--log-dir` 同样变成相对目录
  `true` → 指定目录不存在、日志出现在 `true\host.log`、sidecar 报 `SidecarBundleMissing`。证据：
  `logs/host-readiness/space-form-true-host.log`。
- A-6 自检**不是**原因（正确启动时为 Degraded，写入开启，无 ReadOnlyReason）。
- 另发现：空 `--log-dir=` 会触发 `Program.WriteFatal` 空路径二次崩溃（exit -532462766，无日志）：
  `logs/host-readiness/writefatal-empty-logdir.log`。

**产品缺陷（已报 Lead，本卡未改产品代码）**：
1. **P0**：v2 默认壳不启动 Host —— 默认安装的数据面（书架/导入/导出/Run）全部不可用且无错误提示；
2. **P1**：CLI 空格分隔值静默误解析（无 InvalidReason）——用户/文档常见的 `--sidecar-dir "path"` 写法失效；
3. **P2**：`Program.WriteFatal` 对空路径未防御，掩盖真实启动错误；
4. 观察：v2 下 `--variant=dark|light` 截图 SHA-256 相同（无可见差异），建议 owner 核实 DS 主题栈是否接
   `StartupVariant`。

## 4. 重启持久化 E2E（尽力而为 → NOT_RUN，不伪造输入）

尝试：隔离 `%APPDATA%`（仅子进程环境变量覆盖）+ 隔离 `--data-root` + legacy 壳（Host 就绪）启动一次，
检查是否产生/更新 `%APPDATA%\NewManga\theme-settings.json`。结果：

- Host 就绪、exit 0，但 `theme-settings.json` **未创建**；
- 结论 **NOT_RUN**：启动阶段只**读取**已持久化设置；写盘仅发生在 Theme Studio 的"应用"动作（UI 交互）。
  本任务禁止伪造点击/键盘输入，因此无法在无人值守下制造一次真实设置变更并验证"重启后保持"。
- 证据：`persistence-check.json`（含隔离 APPDATA 路径、`theme_settings_created=false`、`ui_input_simulated=false`
  与原因）。
- 复跑建议：由自动化 UI 测试（真实输入或 headless ViewModel 命令）修改主题 → 关闭 → 重启 → 断言
  `theme-settings.json` 内容与首屏外观；或由 owner 提供受支持的自动化入口。

## 5. 环境限制（LT 单列）

1. **必须有交互桌面会话**：真实窗口 + `PrintWindow`/`CopyFromScreen` 在无桌面/服务会话（Session 0）不可用；
   CI runner 默认无交互桌面，因此本证据是"LT 真机"证据，不在 CI 中跑（脚本不进入 CI job）。
2. **窗口必须前台可见**：截图用 Win32/GDI，若窗口被完全遮挡/最小化，`PrintWindow` 失败时回退
   `CopyFromScreen` 可能捕获遮挡内容；脚本通过"本轮进程 + 标题 + 前置清理"降低误捕，并在 JSON 记录实际
   窗口尺寸。
3. **sidecar 必需**：无 sidecar 时 Host 合法地报 `SidecarBundleMissing`（`host_ready=false`），矩阵仍会
   通过（窗口/截图/exit 断言）但 `host-readiness.md` 的"就绪"结论不成立；正式 L4 复跑请使用打包 sidecar。
4. **CLI 写法**：必须 `--key=value`（见 §3 P1）；空格写法会静默失效。
5. **v2 壳当前不启动 Host（P0）**：在修复前，v2 的六组截图只能证明"窗口/尺寸/明暗壳可启动 + exit 0"，
   不能证明数据面可用；数据面就绪证据目前只能由 legacy 壳提供。

## 6. 文件清单

```
tools/e2e/v2-launch-matrix.ps1              （启动矩阵脚本：真实窗口 + GDI 截图 + JSON + 失败非零退出）
verification/V11R-L4-EVIDENCE/
  README.md                                  （本文件）
  host-readiness.md                          （Host 就绪核查结论与确切失败点）
  launch-matrix.json                         （7 组逐项结果 + summary + failures）
  host-readiness.json                        （legacy vs v2 就绪对比）
  persistence-check.json                     （重启持久化：NOT_RUN + 原因）
  screens/                                   （7 张矩阵截图 + 2 张就绪对比截图 = 9 张 PNG）
  logs/build.log                             （矩阵前 -warnaserror 构建日志）
  logs/<case>/host.log / wire / stderr       （逐组 Host 日志与真实 Core wire 帧）
  logs/host-readiness/**                     （空格写法误解析、WriteFatal 崩溃、legacy 就绪日志）
```
