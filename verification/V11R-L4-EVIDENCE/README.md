# V11R-L4-EVIDENCE：真实窗口发布前证据（多尺寸 × 明暗 + legacy 回滚 + Host 就绪复验）

- Task：`V11R-L4-EVIDENCE`（Lead 2026-10-30 分配；真实窗口证据）
- Owner：`core-bridge`
- 分支：`v11r/core-bridge`，本版复跑 HEAD `4374dfeae5e1eec68138b9e8056cbbf4f24d372f`
  （已合入 INT-2 `v2 启动 Host`、A-8 CLI 健壮性、L4 初版证据）
- 脚本：`tools/e2e/v2-launch-matrix.ps1`
- 边界：本任务只写 `tools/e2e/**` 与 `verification/V11R-L4-EVIDENCE/**`。

## 1. 启动矩阵结果（真实窗口，非 headless；修复 INT-2 后复跑）

**7/7 通过，7 组全部 Host 就绪，全部自然退出 exit 0**，截图共 9 张（7 张矩阵 + 2 张就绪对比）：

| 组 | 尺寸 | 外观 | exit_code | exit_kind | Host 就绪 | 结果 | 截图 |
|---|---|---|---:|---|---|---|---|
| v2-1600x1000-dark | 1600×1000 | dark | 0 | natural | 是 | PASS | `screens/v2-1600x1000-dark.png` |
| v2-1600x1000-light | 1600×1000 | light | 0 | natural | 是 | PASS | `screens/v2-1600x1000-light.png` |
| v2-1280x800-dark | 1280×800 | dark | 0 | natural | 是 | PASS | `screens/v2-1280x800-dark.png` |
| v2-1280x800-light | 1280×800 | light | 0 | natural | 是 | PASS | `screens/v2-1280x800-light.png` |
| v2-1024x700-dark | 1024×700 | dark | 0 | natural | 是 | PASS | `screens/v2-1024x700-dark.png` |
| v2-1024x700-light | 1024×700 | light | 0 | natural | 是 | PASS | `screens/v2-1024x700-light.png` |
| legacy-1280x800-dark（回滚冒烟） | 1280×800 | dark | 0 | natural | 是 | PASS | `screens/legacy-1280x800-dark.png` |

- 机器可读：`launch-matrix.json`
  - `summary = {total:7, passed:7, failed:0, host_ready_cases:7, host_ready_expected_cases:7,
    natural_exit_cases:7, graceful_close_cases:0, harness_terminated_cases:0}`
  - 逐组字段：`pass / exit_code / exit_kind / terminated_by_harness / host_ready / window_width /
    window_height / screenshot / host_log / elapsed_ms / failure_reason`。
- 每组一次性隔离 `--data-root`（临时，跑完删除）+ 证据内 `--log-dir`（保留 host.log/wire）；
  每组唯一 `--mutex-name`；跑前清理残留 `NewManga.App`；窗口检测要求"本轮启动 + 标题 New Manga"。
- 截图方式：Win32/GDI `PrintWindow(PW_RENDERFULLCONTENT)`，失败回退 `CopyFromScreen`；**未使用 CUA**。
- dark/light 现在截图两两不同（INT-2 的 "working --variant" 生效；修复前 6 张 SHA-256 相同）。

## 2. 退出判定（Lead 裁定后的实现）

脚本不再"到点 kill"：每组截图后按以下阶梯退出，并在 JSON 记录 `exit_kind`：

1. **natural**：等待 App 自己的 `--exit-after` 自然退出（exit 0）→ 可 PASS；
2. **graceful_close**：超过 `--exit-after + ExitGraceSeconds`（默认 20s）仍未退出 → 对主窗口
   `PostMessage(WM_CLOSE)`，等待 8s 内退出（exit 0）→ 可 PASS；
3. **harness_terminated**：WM_CLOSE 后仍不退出 → 强制 kill，`terminated_by_harness=true`，
   **永远不 PASS**。

PASS 定义（与 Lead 一致）：窗口出现 + Host 就绪 + 截图成功 + 退出码 0 + 非 harness 终止。
任何非 0 退出、无窗口、截图失败、Host 未就绪、harness 终止 → 脚本 exit 1，并在
`launch-matrix.json.failures` 与 stdout 记录 `case + failure_reason`。

## 3. 脚本用法

```powershell
pwsh -NoProfile -File tools/e2e/v2-launch-matrix.ps1 `
  -SidecarDir "D:\NewManga.workspace\task-envs\HOST-CORECLIENT-1\sidecar-copy"
```

| 参数 | 说明 |
|---|---|
| `-SidecarDir` | 必需；打包 sidecar 目录（`core_service.exe` + `host_bridge.exe`）。默认取 `$env:NEWMANGA_CORECLIENT_SIDECAR_DIR`；缺文件直接失败并给出可读原因。 |
| `-OutputRoot` | 证据根，默认 `<repo>/verification/V11R-L4-EVIDENCE`。 |
| `-TimeoutSeconds` | 窗口出现超时（默认 30s）。 |
| `-ExitGraceSeconds` | `--exit-after` 之后等待自然退出的宽限（默认 20s），超时才发 WM_CLOSE。 |
| `-SettleMs` | 窗口出现后等待首帧布局再截图（默认 1800ms）。 |
| `-SkipBuild` | 复用已有构建（默认先 `dotnet build NewManga.sln -warnaserror`）。 |
| `-IncludeLegacy` | 是否跑 legacy 回滚冒烟（默认 true；`-IncludeLegacy:$false` 跳过）。 |
| `-Configuration` | 默认 `Debug`。 |

前置：Windows 10/11 x64 交互桌面会话（真实窗口必须可见）、.NET 9 SDK、可用 sidecar bundle；
脚本不触碰用户真实数据根（全部临时目录）。

如何解读失败：看 `launch-matrix.json.cases[].failure_reason` 与 `exit_kind`；若 `host_ready=false`
先看 `logs/<case>/host.log`（常见为 sidecar 缺失/路径错误）。

## 4. Host 就绪复验（Lead 追加项，已闭环）

完整结论与历史根因见 [`host-readiness.md`](host-readiness.md)。摘要：

- **修复后两个壳都真实就绪**：`host_ready_cases = 7/7`，v2 默认壳截图左下角"● Host 就绪"
  （`screens/host-readiness-v2.png`），legacy 壳右上角"Host 就绪"
  （`screens/host-readiness-legacy.png`）；两壳 `host.log` 均含 `core_service ready` /
  `host_bridge ready` / `self-check status=Degraded`（ReadWrite，无 ReadOnlyReason）。
- **历史缺陷（均已修复）**：
  1. **P0**：v2 默认壳从不调用 `IHostController.StartAsync()` → 无 host.log、无 data-root、状态栏
     永远"Host 未就绪"；由 ui-shell `fix(V11R-INT-2)`（`8c8f2d899`）修复；
  2. **P1**：CLI 只接受 `--key=value`，`--sidecar-dir "path"` 被静默误解析成 `"true"`（日志落在
     `<cwd>/true/host.log`，报 `SidecarBundleMissing`）；由本卡 `V11R-A-8`（`c50892389`）修复；
  3. **P2**：空 `--log-dir=` 触发 `Program.WriteFatal` 空路径二次崩溃（exit -532462766、无日志）；
     由 `V11R-A-8` 修复（空值 → exit 2；WriteFatal 永不抛）。
- 修复前证据保留：`logs/host-readiness/space-form-true-host.log`、
  `logs/host-readiness/writefatal-empty-logdir.log`。
- 修复后机器可读：`host-readiness.json`（legacy/v2 均 `exit_code=0`、`host_ready=true`、
  `data_root_created=true`）。

## 5. 重启持久化 E2E（尽力而为 → NOT_RUN，不伪造输入）

尝试：隔离 `%APPDATA%`（仅子进程环境变量覆盖）+ 隔离 `--data-root` + legacy 壳（Host 就绪）启动一次，
检查是否产生/更新 `%APPDATA%\NewManga\theme-settings.json`。结果：

- Host 就绪、exit 0，但 `theme-settings.json` **未创建**；
- 结论 **NOT_RUN**：启动阶段只**读取**已持久化设置；写盘仅发生在 Theme Studio 的"应用"动作（UI 交互）。
  本任务禁止伪造点击/键盘输入，因此无法在无人值守下制造一次真实设置变更并验证"重启后保持"。
- 证据：`persistence-check.json`（含隔离 APPDATA 路径、`theme_settings_created=false`、
  `ui_input_simulated=false` 与原因）。
- 复跑建议：由自动化 UI 测试（真实输入或 headless ViewModel 命令）修改主题 → 关闭 → 重启 → 断言
  `theme-settings.json` 内容与首屏外观；或由 owner 提供受支持的自动化入口。

## 6. 环境限制（LT 单列）

1. **必须有交互桌面会话**：真实窗口 + `PrintWindow`/`CopyFromScreen` 在无桌面/服务会话（Session 0）不可用；
   CI runner 默认无交互桌面，因此本证据是"LT 真机"证据，不进入 CI job。
2. **窗口必须前台可见**：截图用 Win32/GDI；窗口完全被遮挡/最小化时 `PrintWindow` 失败会回退
   `CopyFromScreen` 捕获遮挡内容；脚本通过"本轮进程 + 标题 + 前置清理"降低误捕，并在 JSON 记录实际尺寸。
3. **sidecar 必需**：无 sidecar 时 Host 合法地报 `SidecarBundleMissing`（`host_ready=false`），矩阵会判失败。
4. **CLI 写法**：`--key=value` 与 `--key value` 现均支持（A-8），但自动化请优先 `=` 写法。
5. **harness 终止不算通过**：若某环境 App 无法在宽限内自然退出，请检查 `exit_kind`，不要放宽断言。
6. **UI 输入类 E2E（主题写盘）仍需真实交互**：见 §5 NOT_RUN。

## 7. 文件清单

```
tools/e2e/v2-launch-matrix.ps1              （启动矩阵脚本：真实窗口 + GDI 截图 + graceful exit + JSON）
verification/V11R-L4-EVIDENCE/
  README.md                                  （本文件）
  host-readiness.md                          （Host 就绪复验结论 + 历史根因）
  launch-matrix.json                         （7 组逐项结果 + summary + failures）
  host-readiness.json                        （legacy vs v2 就绪对比，均 true）
  persistence-check.json                     （重启持久化：NOT_RUN + 原因）
  screens/                                   （9 张 PNG = 7 矩阵 + 2 就绪对比）
  logs/build.log                             （矩阵前 -warnaserror 构建日志）
  logs/<case>/host.log / wire / stderr       （逐组 Host 日志与真实 Core wire 帧）
  logs/host-readiness/**                     （修复前误解析/WriteFatal 证据 + legacy/v2 就绪日志）
```

## 8. 真机实机清单（2026-10-30）

在真实 Windows 交互桌面上按本文档执行并补测了原先受限的项目，结果（详见
[`real-machine/checklist.md`](real-machine/checklist.md) / [`real-machine/checklist.json`](real-machine/checklist.json)）：

| 项 | 结果 |
|---|---|
| 启动矩阵 / Host 就绪 | **PASS 7/7**（复跑） |
| 重启持久化 E2E（UIA 真实点击） | **PASS**（apply light → 重启保持；测试写入已恢复） |
| 中文 IME 真实输入 | **PASS**（`nihao`+空格 上屏「你好」） |
| DPI 感知 | **PASS @100%**（PerMonitorV2、DPI=96）；**150%/200% NOT_RUN**（需改系统缩放，未擅改） |
| 屏幕阅读器（UIA 结构级） | **PARTIAL**：71 元素/52 命名；发现 7 个按钮可访问名称为类型名（P2，`FOLLOW-UP-A11Y-1`） |
| 单文件自包含发布 | **PASS**（93.5 MB 单 exe，窗口+Host 就绪+exit 0） |
| Trimmed 发布 | **FAIL（默认，IL2026）** / **PASS-with-caveat（抑制分析后 smoke）** |
| AOT 发布 | **FAIL（默认参数冲突）** / **PASS（PublishTrimmed=true+抑制，28.8 MB 原生 exe 可运行）** |
| GitHub Actions 真实运行 | **NOT_RUN**（无 runner） |