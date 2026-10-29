# Host 就绪真实性核查（V11R-L4-EVIDENCE 追加项）— 修复后复验

- 日期：2026-10-30（UTC 2026-10-29/30）
- 分支：`v11r/core-bridge`，复验 HEAD `4374dfeae5e1eec68138b9e8056cbbf4f24d372f`（已合入 INT-2 / A-8 / L4）
- 核查人：`core-bridge`（Owner，未自审）
- **当前结论：两个壳（v2 默认壳与 legacy 回滚壳）都已真实 Host 就绪**：`launch-matrix.json`
  `host_ready_cases = 7/7`、`summary.passed = 7/7`、`exit_kind = natural` 7/7、`exit_code = 0` 7/7。
- 历史结论（本卡最初核查，已由后续修复合入）：曾发现两个叠加缺陷 —— **P0 v2 默认壳从不启动 Host**、
  **P1 CLI 空格分隔值被静默误解析**；另有 **P2 WriteFatal 空路径二次崩溃**。三者现已全部修复，
  修复归属与证据见 §4。

## 1. 当前复验证据（修复后，真实窗口 + 真实 sidecar）

复验命令（`verification/V11R-L4-EVIDENCE/launch-matrix.json` 即本次产物）：

```powershell
pwsh -NoProfile -File tools/e2e/v2-launch-matrix.ps1 `
  -SidecarDir "G:\CODEX\New Manga.workspace\task-envs\HOST-CORECLIENT-1\sidecar-copy"
```

| 组 | exit_code | exit_kind | Host 就绪 | 结果 |
|---|---:|---|---|---|
| v2-1600x1000-dark | 0 | natural | 是 | PASS |
| v2-1600x1000-light | 0 | natural | 是 | PASS |
| v2-1280x800-dark | 0 | natural | 是 | PASS |
| v2-1280x800-light | 0 | natural | 是 | PASS |
| v2-1024x700-dark | 0 | natural | 是 | PASS |
| v2-1024x700-light | 0 | natural | 是 | PASS |
| legacy-1280x800-dark（回滚冒烟） | 0 | natural | 是 | PASS |

`summary = {total:7, passed:7, failed:0, host_ready_cases:7, natural_exit_cases:7,
graceful_close_cases:0, harness_terminated_cases:0}`；截图 9 张（7 组矩阵 + 2 张就绪对比图）。

- v2 就绪截图：`screens/host-readiness-v2.png`（左下角"● Host 就绪"）
- legacy 就绪截图：`screens/host-readiness-legacy.png`（右上角"Host 就绪"）
- 两壳 `host.log` 均含：`core_service ready`、`host_bridge ready`、`credential port ready`、
  `host-control session opened`、`self-check status=Degraded ... required_minor=3`（Degraded 是预期：
  Core 2.3 与请求 minor 一致、写入保持 `mode=ReadWrite`，没有 ReadOnlyReason 降级）
- 机器可读：`host-readiness.json`（legacy/v2 两行均为 `exit_code=0 / host_ready=true /
  data_root_created=true`）、`launch-matrix.json`、`logs/host-readiness/{legacy,v2}/host.log`。

## 2. 历史失败点（已修复，保留根因分析）

### 2.1 P0：v2 默认壳从不启动 Host（已由 INT-2 修复）

修复前链路：`App.axaml.cs` 创建 `HostController` → v2 `AppShellV2.OnAttachedToVisualTree` →
`AppShellViewModel.InitializeCoreAsync` → `Library.InitializeAsync` → `HostController.RefreshBooksAsync`
在 `_runtime is null` 时直接返回；全库唯一 `_controller.StartAsync()` 调用点在 legacy
`Views/MainWindow.axaml.cs:764-766`。后果：无 `host.log`、不建 `--data-root`、状态栏永远
"Host 未就绪：等待 Core sidecar"、exit 0。

修复（INT-2，`8c8f2d899`，main `4d2dfe8b2`）：v2 初始化显式 `await _controller.StartAsync(...)`，
当前代码位于 `AppShellViewModel.cs`（含"StartAsync is idempotent"注释）；本次复验 6 组 v2 全部
`host_ready=true`。

### 2.2 P1：CLI 空格分隔值被静默误解析（已由 A-8 修复）

修复前：`AppOptions.Parse` 只接受 `--key=value`；`--sidecar-dir "G:\...\core-sidecar"` 被解析成
`SidecarDirectory="true"`，路径 token 被丢弃；`--data-root`/`--log-dir` 同样变成相对目录 `true`，
日志落在 `<cwd>\true\host.log`，Host 报 `SidecarBundleMissing`，且无 InvalidReason。

证据（修复前）：`logs/host-readiness/space-form-true-host.log`。

修复（A-8，`c50892389`）：`Parse` 同时接受 `--key=value` 与 `--key value`；空值/裸值型 key/未知选项/
未知位置参数/非法数值 → `InvalidReason` + `Program.Main` exit 2。复验：真实进程空格写法
`--data-root "…data with space" --log-dir "…logs with space" --sidecar-dir "…sidecar"` + legacy →
exit 0、目录创建、Host 就绪（A-8 证据 `verification/V11R-A-8/cli-exit-codes.json`）。

### 2.3 P2：`Program.WriteFatal` 空路径二次崩溃（已由 A-8 修复）

修复前：`--log-dir=`（空值）→ `HostLog` 构造 `Directory.CreateDirectory("")` 抛
`ArgumentException` → legacy `async void OnLoaded` 未捕获 → `Program.Main` catch →
`Program.WriteFatal` 再对空路径建目录 → 未处理异常，进程 `exit=-532462766`、无 fatal 日志。
证据（修复前）：`logs/host-readiness/writefatal-empty-logdir.log`。

修复（A-8，`c50892389`）：空/空白 LogDirectory 降级 `Console.Error`；任何写日志异常宽 catch，
`WriteFatal` 绝不抛异常；空 `--log-dir=` 在解析阶段即 exit 2。

### 2.4 A-6 自检不是原因（历史确认，仍然成立）

正确启动时自检输出 `self-check status=Degraded code=- detail=core_protocol=2.3 required_minor=3`，
写入保持开启（`mode=ReadWrite`），无 `ReadOnlyReason`；因此"未就绪"与 A-6 无关。

## 3. 修复后的行为边界

| 场景 | 现在的结果 |
|---|---|
| v2 默认壳 + 真实 sidecar | Host 就绪（7/7 复验），data-root 创建，状态栏"● Host 就绪" |
| legacy 回滚壳 + 真实 sidecar | Host 就绪（复验通过） |
| `--key value`（空格写法，含空格路径） | 与 `=` 写法等价，正常启动 |
| 裸值型 key / 未知选项 / 空值 / 非法数值 / 未知位置参数 | `InvalidReason` + exit 2（不静默继续） |
| 无 sidecar | 合法失败：`SidecarBundleMissing`，Host 不就绪（矩阵此时会判失败） |
| `--log-dir=` 空值 | exit 2（不再二次崩溃） |
| 自然退出 | `--exit-after` 到点后 exit 0，`exit_kind=natural` |

## 4. 缺陷归属与修复证据

| 缺陷 | 归属 | 修复 commit | 复验证据 |
|---|---|---|---|
| P0 v2 不启动 Host | ui-shell（`fix(V11R-INT-2)`） | `8c8f2d899`（main `4d2dfe8b2`） | 本文件 §1；`verification/V11R-INT-2/` |
| P1 CLI 空格解析 | core-bridge（`V11R-A-8`） | `c50892389` | `verification/V11R-A-8/`（单测 20/20、真实进程 exit 2/0） |
| P2 WriteFatal 空路径 | core-bridge（`V11R-A-8`） | `c50892389` | `verification/V11R-A-8/`（空/非法/超长/锁定路径均不抛） |

## 5. 证据清单（当前状态）

```
verification/V11R-L4-EVIDENCE/
  host-readiness.md                      （本文件：修复后复验 + 历史根因）
  host-readiness.json                    （legacy/v2：exit 0、host_ready=true、data_root_created=true）
  launch-matrix.json                     （7/7 pass、host_ready 7/7、natural 7/7、exit 0）
  persistence-check.json                 （重启持久化：NOT_RUN + 原因，见 README §4）
  screens/host-readiness-legacy.png      （legacy Host 就绪）
  screens/host-readiness-v2.png          （v2 Host 就绪，修复后）
  screens/v2-*.png / legacy-*.png        （7 张矩阵截图，dark/light 已有可见差异）
  logs/host-readiness/{legacy,v2}/host.log
  logs/host-readiness/space-form-true-host.log      （P1 修复前证据，保留）
  logs/host-readiness/writefatal-empty-logdir.log   （P2 修复前证据，保留）
  logs/<case>/host.log / wire / stderr              （7 组矩阵逐组日志）
```

## 6. 备注

- `--variant=dark|light` 现在在 v2 下有可见差异（修复前 dark/light 截图 SHA-256 完全相同；
  修复后 6 张矩阵截图两两不同），与 INT-2 的 "working --variant" 一致。
- 本文件不再把 Host 就绪列为"未解决缺陷"；若后续出现回归（例如 v2 又回到 Starting），
  直接重跑 `tools/e2e/v2-launch-matrix.ps1` 看 `host_ready_cases` 即可定位。
