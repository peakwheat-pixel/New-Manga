# V11R-A-8 证据包：CLI 健壮性（P1 空格分隔解析 + P2 WriteFatal 空路径）

- Task：`V11R-A-8`（Lead 2026-10-30 分配；L4 核查发现的 P1/P2）
- Owner：`core-bridge`（本卡授权修改产品代码：`AppOptions.cs`、`Program.cs` + App 测试）
- 分支：`v11r/core-bridge`，基线 `67b86c519`（L4 证据已合入 main）
- 状态：实现 + 单测 + 真实进程 E2E 已完成；Owner 未自审。

## 1. 问题（来自 `verification/V11R-L4-EVIDENCE/host-readiness.md`）

| # | 现象 | 根因 |
|---|---|---|
| P1 | `--sidecar-dir "G:\...\core-sidecar"` 被静默忽略：Host 报 `SidecarBundleMissing`、`--data-root`/`--log-dir` 指定的目录不存在、日志出现在 `true\host.log` | `AppOptions.Parse` 只接受 `--key=value`：无 `=` 时 value=`"true"`，后续独立 token 被 `continue` 丢弃，且无 `InvalidReason` |
| P2 | `--log-dir=`（空值）启动时进程 `exit=-532462766`、无 fatal 日志 | 空路径进入 `Program.WriteFatal` → `Directory.CreateDirectory("")` 抛未处理 `ArgumentException`，掩盖真正的启动错误 |

## 2. 修复

### 2.1 `AppOptions.Parse`（`apps/desktop-avalonia/src/NewManga.App/AppOptions.cs`）

- 同时支持 **`--key=value`** 与 **`--key value`**：`--key` 后若下一个 token 不以 `--` 开头则作为值消费；
- **显式空值**（`--log-dir=`、`--data-root=` 等）→ `InvalidReason`（"requires a non-empty value"）；
- **值型 key 裸写**（`--data-root` 后无值/紧跟另一个 `--`）→ `InvalidReason`（"requires a value …"）；
- **未知选项**（`--bogus`、`--bogus=1`）与**未知位置参数**（不以 `--` 开头的游离 token）→ `InvalidReason`；
- **数值校验**：`--width`/`--height` 必须正整数，`--exit-after` 必须非负整数，非法 → `InvalidReason`；
- **`--shell`** 只接受 `v2`/`legacy`，其他 → `InvalidReason`；
- **布尔开关保持裸写兼容**：`--parity`、`--demo-write`、`--auto-roundtrip`、`--smoke` 裸写= true
  （既有 `scripts/smoke.ps1` 等证据脚本语义不变）；`--legacy-shell-check` 裸写= on、`=off` 关闭；
- `Program.Main` 对 `InvalidReason` 已返回 **exit code 2**（既有分支），现在所有上述错误都会走到它。

> 说明：Lead 指示"裸 `--key` → InvalidReason"。实现上对**值型 key** 严格执行；对**已知布尔开关**
> （`--parity` 等）保留裸写=true，否则会破坏仓库内既有证据脚本（`smoke.ps1` 传 `--parity --demo-write
> --auto-roundtrip`）与历史文档用法。此差异已在 §6 明确列出，若要求严格禁止裸布尔开关请再裁定。

### 2.2 `Program.WriteFatal`（`apps/desktop-avalonia/src/NewManga.App/Program.cs`）

- 空/空白 `LogDirectory` → 不写文件，降级 `Console.Error`；
- 任何写日志异常（`IOException`/`UnauthorizedAccessException`/`ArgumentException`/`PathTooLongException`/
  其他）→ 宽 catch，降级 `Console.Error`，**绝不因写日志而崩溃**；
- `WriteFatal` 改为 `internal` 并在 `src/NewManga.App/AssemblyInfo.cs` 加
  `InternalsVisibleTo("NewManga.App.Tests")` 以便直接单测（仅测试可见性，不改变产品行为）。

## 3. 测试（真实执行）

### 3.1 单测：`dotnet test NewManga.App.Tests --filter "AppOptionsCliRobustness|ProgramWriteFatal"`

**20/20 PASS**（EXIT 0）：

- 两种写法等价（含含空格路径）：`--data-root "C:\tmp\nm data"` == `--data-root=C:\tmp\nm data`，覆盖
  data-root/log-dir/sidecar-dir/width/height/variant/shell；
- 裸值型 key、值型 key 紧跟另一个 `--`、未知选项、未知位置参数 → 均有可读 `InvalidReason`；
- 空值（log-dir/data-root/sidecar-dir/width）、非法数值（`abc`/`-5`/`0`/`-1`）、非法 `--shell` → `InvalidReason`；
- 布尔开关裸写仍工作（`--parity`/`--smoke`/`--legacy-shell-check`），`--demo-write` 仍要求显式 data-root；
- `WriteFatal`：空/空白目录、路径在文件下、超长路径（400 字符）、日志文件被独占锁定 → **均不抛异常**。

### 3.2 真实进程 E2E（`cli-exit-codes.json` + `logs/cli-exit-codes.log`）

| 用例 | 参数 | exit | 结果 |
|---|---|---:|---|
| space-form-legacy | `--data-root "…data with space" --log-dir "…logs with space" --sidecar-dir "…sidecar" --width 1280 --height 800` + legacy | 0 | data/log 目录创建、`host.log` 含 `core_service ready`（**P1 修复生效**） |
| bare-key | `--data-root` | **2** | 参数错误（不再静默继续） |
| unknown-option | `--bogus=1` | **2** | 参数错误 |
| empty-log-dir | `--log-dir=` | **2** | 参数错误（**P2：不再二次崩溃**） |
| invalid-numeric | `--width=abc` | **2** | 参数错误 |

## 4. 质量门

| # | 命令 | exit | 结果 |
|---|---|---:|---|
| 1 | `dotnet build NewManga.sln -warnaserror` | 0 | 0 warning / 0 error |
| 2 | `dotnet test tests/NewManga.App.Tests --filter "AppOptionsCliRobustness|ProgramWriteFatal"` | 0 | 20/20 PASS |
| 3 | 真实进程 E2E（§3.2） | 0/2/2/2/2 | 与预期一致 |
| 4 | `dotnet test NewManga.sln --no-build --settings tests/NewManga.runsettings`（全解） | 0 | **827 passed / 9 skipped / 0 failed**（ThemeEngine 235、DesignSystem 82、CoreClient 136+5skip、App 301、Host 73+4skip；skip 为未提供可选夹具的显式环境跳过） |

日志/TRX：`verification/V11R-A-8/logs/`、`trx/cli-robustness.trx`。

## 5. 影响面

- 合法调用零行为变化（`--key=value` 全兼容；布尔开关裸写兼容）；
- 之前被静默忽略的写法（空格分隔、裸值型 key、未知参数、非法数值、空值）现在**明确失败 exit 2**；
- `--shell` 非法值此前会静默变 `legacy`，现在报错（更严格，符合"不静默降级"目标）；
- 既有证据脚本（`scripts/test.ps1`、`smoke.ps1` 等）只用 `=` 写法与已知裸布尔开关 → 不受影响
  （全量测试在 L4 复跑时一并验证）。

## 6. 偏差 / 遗留

1. 已知布尔开关（`--parity`/`--demo-write`/`--auto-roundtrip`/`--smoke`/`--legacy-shell-check`）允许裸写，
   与"所有裸 `--key` 都报错"的严格解读不同；理由：兼容仓库内既有证据脚本与文档，避免无关回归。
2. `--variant`/`--theme`/`--page` 未做枚举校验（保持既有宽松语义；L4 已记录 v2 下 variant 无视觉差异，
   属主题栈问题，不在本卡范围）。
3. P0（v2 不启动 Host）由 ui-shell 修复；本卡不涉及；其修复合入 main 后会复跑 L4 矩阵（见 L4 证据更新）。
