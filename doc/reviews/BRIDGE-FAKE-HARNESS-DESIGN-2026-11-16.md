# bridge 假 sidecar 夹具方案冻结（DSH，2026-11-16）

Task：`BRIDGE-FAKE-HARNESS-1`｜依据：Codex 裁决 `E-7-BRIDGE-ID-RULING-codex-2026-11-16.md` §4

> 裁决把「能通过现有启动方式运行的测试夹具方案」冻结派给 DSH，并明确：
> **不为测试扩大生产公共 API**。

## 约束（实测确认）

| 约束 | 出处 | 后果 |
|---|---|---|
| `HostBridgeOptions` **没有** `AdditionalArguments` | `HostBridgeClient.cs` 的 `HostBridgeOptions` 定义 | 无法像 core 侧那样传 `["-u", script, scenario]` |
| `HostBridgeClient.StartAsync` 构造 `SidecarSpec` 时**不设** `AdditionalArguments` | 同上 `StartAsync` | `spec.AdditionalArguments` 恒为空 |
| `SidecarProcess` 用 `UseShellExecute = false` | `SidecarProcess.cs` 的 `ProcessStartInfo` | `.cmd` / `.bat` **无法直接执行**（会 Win32Exception） |
| `SidecarProcess` 启动前 `File.Exists(spec.ExecutablePath)` | `SidecarProcess.cs:118` | `ExecutablePath` 必须是真实存在的**可执行文件** |
| `Environment` 只设三个变量：`M2RC1_DERIVED_ROOT` / `M2RC1_MANAGED_ROOT` / `M2RC2_CATALOG_DB` | `StartAsync` | 无法用 `PYTHONPATH` + `sitecustomize` 之类的注入技巧 |
| 握手要求：`ping` → `result.pong == true` | `PingAsync` | 假 bridge 必须能回这个方法 |

## 被排除的方案（附排除理由）

| 方案 | 排除理由 |
|---|---|
| A. `.cmd` 包装转调 python | `UseShellExecute = false` 下 `.cmd` 不能直接执行 |
| B. `ExecutablePath` 指向 `python.exe` + 靠 `AdditionalArguments` 传脚本 | `AdditionalArguments` 恒为空（见上表） |
| C. `PYTHONPATH` + `sitecustomize.py` 自动加载 | `Environment` 不设 `PYTHONPATH`，且改它是扩大生产 API |
| D. 修改 `SidecarProcess` 允许 `.cmd` | 改产品代码以方便测试，违反约束 |
| E. 提交预编译 exe 到仓库 | 二进制夹具不可审计、不可跨平台重建 |

## 选定方案：`FakeBridgeHost` 小型控制台项目

在 `apps/desktop-avalonia/tests/FakeBridgeHost/` 新建一个**极小的 C# 控制台项目**，
作为**测试专用**假 `host_bridge`：

- 输出一个真实 `.exe`，满足 `File.Exists` + `UseShellExecute=false` 的双重约束；
- 不依赖 Python（消除 core 侧夹具的 `where.exe python` 脆弱性，也消除 CI 无 Python 的风险）；
- 行为由**环境变量**驱动（`Environment` 里已有的三个变量之一编码场景），
  或用**命令行参数**——但后者不可用，所以用环境变量：
  - `M2RC1_DERIVED_ROOT` 的值末尾带 `/scenario-<name>`，假 bridge 读它决定行为；
  - 这是**测试侧约定**，不改生产 API（生产只是把该路径当目录用）。

### 为什么可以用 `M2RC1_DERIVED_ROOT` 编码场景

`HostBridgeOptions.DerivedRoot` 是 `required`，测试本来就传一个临时目录。把场景名编码进路径末尾
（`<tmp>/derived/scenario-mismatch`），假 bridge 启动时读该环境变量解析出场景名。
生产路径不受影响（它只把 DerivedRoot 当目录字符串用，不会去解析末段）。

### 场景

| 场景 | 行为 |
|---|---|
| `plain` | `ping` → `{"pong":true}`；其它 → 回显 `id` + `{"ok":true}` |
| `missing-then-match` | 首帧无 `id`（应触发 `MalformedResponse` + poison），随后正确帧 |
| `mismatch-then-match` | 首帧 `id+1`，随后正确帧 |

## 需要扩 allowed_paths

新增 `apps/desktop-avalonia/tests/FakeBridgeHost/**` 与 `NewManga.sln`（登记新项目）。

## 验收（本卡 AC1）

`HostBridgeClient.StartAsync` 能在 `plain` 场景下完成握手（`pong == true`）。
