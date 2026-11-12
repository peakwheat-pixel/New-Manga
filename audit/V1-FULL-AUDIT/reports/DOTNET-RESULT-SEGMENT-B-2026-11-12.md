# 段 B Avalonia .NET suite 结果

## 执行与裁决

- Runner：`python audit/V1-FULL-AUDIT/tests/audit_runner.py dotnet`
- 8 个项目生成时 HEAD：`da589416344b8254c9c1061f1d4e3dd61b3e7a93`；branch：`main`
- 第一项目开始时间：`2026-11-12T08:31:19.769271+00:00`；所有 argv、cwd、逐项起始时间、elapsed、HEAD、branch、status before/after 和 EXIT 均见下列日志与 JSON。
- **8/8 项目 EXIT=1，TIMED_OUT=False；8/8 `status_identical=True`。** 所有 TRX 均为 `total=0, executed=0, passed=0, failed=0`，即未发现或执行测试用例。
- ZCode 对本结果的只读 adjudication：`BLOCKED-TESTHOST-ACCESS`（环境/基础设施阻断）；保留原始 EXIT=1，不记 PASS，也不作为产品测试失败。原始裁决、session/turn/trace、命令和 EXIT 见 [`dotnet-result-adjudication-20261112.log`](../logs/dotnet-result-adjudication-20261112.log)。

| 项目 | elapsed (s) | EXIT | TRX | 完整日志 / JSON |
|---|---:|---:|---|---|
| App | 18.037 | 1 | `App-20261112T083119769139Z.trx` | [`log`](../logs/dotnet-app-20261112T083119769139Z.log) / [`json`](../evidence/dotnet-app-20261112T083119769139Z.json) |
| Appearance | 4.346 | 1 | `Appearance-20261112T083119769139Z.trx` | [`log`](../logs/dotnet-appearance-20261112T083119769139Z.log) / [`json`](../evidence/dotnet-appearance-20261112T083119769139Z.json) |
| ApplicationCore | 5.194 | 1 | `ApplicationCore-20261112T083119769139Z.trx` | [`log`](../logs/dotnet-applicationcore-20261112T083119769139Z.log) / [`json`](../evidence/dotnet-applicationcore-20261112T083119769139Z.json) |
| CoreClient | 4.461 | 1 | `CoreClient-20261112T083119769139Z.trx` | [`log`](../logs/dotnet-coreclient-20261112T083119769139Z.log) / [`json`](../evidence/dotnet-coreclient-20261112T083119769139Z.json) |
| DesignSystem | 4.669 | 1 | `DesignSystem-20261112T083119769139Z.trx` | [`log`](../logs/dotnet-designsystem-20261112T083119769139Z.log) / [`json`](../evidence/dotnet-designsystem-20261112T083119769139Z.json) |
| Host | 5.826 | 1 | `Host-20261112T083119769139Z.trx` | [`log`](../logs/dotnet-host-20261112T083119769139Z.log) / [`json`](../evidence/dotnet-host-20261112T083119769139Z.json) |
| PresentationAvalonia | 6.079 | 1 | `PresentationAvalonia-20261112T083119769139Z.trx` | [`log`](../logs/dotnet-presentationavalonia-20261112T083119769139Z.log) / [`json`](../evidence/dotnet-presentationavalonia-20261112T083119769139Z.json) |
| ThemeEngine | 5.348 | 1 | `ThemeEngine-20261112T083119769139Z.trx` | [`log`](../logs/dotnet-themeengine-20261112T083119769139Z.log) / [`json`](../evidence/dotnet-themeengine-20261112T083119769139Z.json) |

## 失败位置与证据边界

8 组日志显示 TestHost 在 `DefaultEngineInvoker.SetParentProcessExitCallback` 注册父进程退出监视时，经 `ProcessManager.OpenProcess` 抛 `System.ComponentModel.Win32Exception (5)` 后退出。栈帧属于 Microsoft TestPlatform/TestHost；未到 NewManga 测试用例。`App` 日志显示产品程序集和 App.Tests 程序集构建输出后才发生该异常；编译成功不能证明产品行为正确。

PowerShell 在外部 workspace 对 8 个 TRX 做只读 XML 计数，均为 0。ZCode 未直接读取仓外 TRX；其裁决采信该计数为执行方本地检查结果。每组日志中异常消息的中文字符有编码替换现象，因此分类依据是稳定的 Win32 error code 5 与调用栈，不依赖乱码文本。**未判定错误码 5 的底层成因**；不推断 EDR/AV、权限令牌、沙箱策略、TestHost 位数或 runsettings 是原因。

`status_identical=True` 的组间基线数量依次为 0、2、4、6、8、10、12、14；解码每组 `GIT_STATUS_BEFORE_HEX` 后，所有既存条目都仅为 `audit/V1-FULL-AUDIT/**` 内前序 runner 输出。组内前后字节相同；没有发现审计目录外的工作树变化。

TRX 文件保留在 `G:\CODEX\New Manga.workspace\task-env\NEW-MANGA-V1-FULL-AUDIT\dotnet\results-20261112T083119769139Z\`，未复制进仓库；目录按 Task resource manifest 标为 `PRESERVE_REFERENCED`。JSON/log 原始证据已提交，提交号见 Task Canonical Evidence。

## 后续范围

- 按 ZCode 裁决继续 smoke `core,wire` 和 governance；它们不依赖此 TestHost 父进程监视路径。
- 当前 .NET suite 保持 `BLOCKED-TESTHOST-ACCESS`。不提权、不关闭安全控制、不改 runner/测试参数、不修产品或测试项目、不重跑以绕过此限制。
- 此 suite 结果不映射到 AUDIT-01–14；所有逐项仍为 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`。Release Gate 继续 `BLOCKED`。
