# AUDIT-01/02：架构与源代码质量阶段报告

**产品基线：** `10e4ee013835605800d3830fb960ae8d3aa04167`
**审计检查 HEAD：** `bb99ab8eaf07ddc95722ad7bd49e972a1c0054a7`
**范围：** AUDIT-01 系统架构；AUDIT-02 有效源码静态质量扫描。只读产品代码；生成物限于审计目录及隔离 workspace 输出。

## 结论与状态

- **AUDIT-01：FAIL（sidecar 生命周期缺陷已由隔离 helper 复现）。** 当前代码链为 Avalonia App → C# Host → Python `core_service` / `host_bridge`。Wire smoke 有 6/6 项运行通过；Core smoke 的 7 项受 sandbox grant 阻断，Avalonia TestHost 8 个项目均在测试启动前失败且 TRX 为 0 项。独立 helper 通过实际 `SidecarProcess` API 复现：启动取消后及直接 dispose 返回后，忽略 EOF 的子进程仍存活；测试随后将 helper 进程终止并确认清理成功。该复现证明受控条件下的生命周期缺陷，不代表真实 sidecar/UI 已验收（见 `NM-AUD-0001`）。
- **AUDIT-02：BLOCKED（全量质量规则扫描未完成）。** Python 源文件 AST 语法检查通过；Avalonia solution 编译通过；格式检查 FAIL。Python lint/type/security 工具均未安装，且 `Directory.Build.props` 关闭了 .NET SDK analyzers。代码质量其他维度与高风险路径仍需补查。
- 两项均不构成 V1 Release Gate 通过。未更改产品源码、测试、契约、Schema、依赖或构建配置。

## 命令与证据

| 检查 | 结果 | 证据 / 边界 |
|---|---|---|
| Python source AST 与依赖图 | EXIT 0；268 个 Python 源文件、0 语法错误、655 条静态本地 import edge、9 处动态 import 调用点；报告 1 个静态 SCC | `logs/source-architecture-scan-20261112.log`、`evidence/source-architecture-scan-20261112.json`。SCC 涉及 `infrastructure.providers.mock_local` 与 `infrastructure.providers.registry`；两侧有关 import 都位于函数内部，当前证据不足以认定模块加载时循环故障。扫描不做类型、运行时动态导入完整性或语义判断。 |
| .NET project reference 图 | EXIT 0；10 个 source projects、13 条引用边、0 cycle、0 unresolved/invalid reference | 同上；不代表方法级依赖或运行行为正确。 |
| Avalonia solution build | `dotnet build apps/desktop-avalonia/NewManga.sln --no-restore --verbosity minimal -warnaserror` EXIT 0；0 warnings / 0 errors | `logs/dotnet-build-audit01-02-20261112.log`。输出写到 `G:\CODEX\New Manga.workspace\agent-output\codex\NEW-MANGA-V1-FULL-AUDIT\build-20261112\bin\`。证明编译，不证明测试通过。 |
| sidecar lifecycle isolated probe | audit runner run `20261112T143133097703Z` EXIT 0；pre-cancel 后 child 仍存活；dispose-only case 在 `DisposeAsync` 返回约 2,011 ms 后 child 仍存活；两项 helper cleanup 均确认 child 已终止 | `tests/sidecar_lifecycle_probe.ps1`、`logs/sidecar-lifecycle-probe-20261112T143133097703Z.log`、`evidence/sidecar-lifecycle-probe-20261112T143133097703Z.json`。调用本次 solution build 的 `NewManga.CoreClient.dll`；child 是全新 workspace 目录中的 Windows PowerShell helper（忽略 EOF 并 sleep 60 秒），不调用真实 sidecar、不访问用户数据。 |
| 产品源码范围对照 | `git diff --quiet 10e4ee013835605800d3830fb960ae8d3aa04167 bb99ab8eaf07ddc95722ad7bd49e972a1c0054a7 -- src apps/desktop-avalonia tests` EXIT 0 | `logs/audit01-source-scope-diff-20261112.log`。在该产品基线至本阶段检查 HEAD 间，受审产品源码及测试目录无 tracked diff；审计脚本、日志、报告和状态文件不在该 diff 范围内。 |
| .NET whitespace format verification | `dotnet format whitespace apps/desktop-avalonia/NewManga.sln --verify-no-changes --no-restore --verbosity minimal` EXIT 2；1,556 项 `WHITESPACE` 诊断，涉及 43 个 `.cs` 文件、9 个 `.csproj` | `logs/dotnet-format-whitespace-20261112.log`。命令未修改源文件，执行前后 status 相同。这里记录工具按默认格式规则报告的差异；未运行自动格式化。 |
| Python quality tool discovery | ruff / mypy / bandit / pyright / pylint / vulture / semgrep 均未安装 | `logs/python-tool-discovery-20261112.log`，本地 `importlib.util.find_spec` 检查；未安装或下载任何工具。 |
| .NET analyzer configuration | `EnableNETAnalyzers=false` | `apps/desktop-avalonia/Directory.Build.props`。本轮 build 仅有 compiler/build diagnostics，不应称为完整 analyzer 扫描。 |
| 既有 Core/Wire runtime smoke | suite EXIT 1 / 程序报告 FAIL；Wire 6/6 PASS；Core 4 PASS、7 项 `BLOCKED-SANDBOX-GRANT`；frontend / packaged SKIP | `reports/SMOKE-RESULT-SEGMENT-B-2026-11-12.md` 和原始 log。Core 的 7 项没有执行其目标 hook 行为。 |
| 既有 .NET test suite | `BLOCKED-TESTHOST-ACCESS`；8/8 runner EXIT 1、8/8 TRX 0 tests | `reports/DOTNET-RESULT-SEGMENT-B-2026-11-12.md`。未把编译成功或 TestHost 前置阻断记为测试通过。 |

## AUDIT-01 逐项记录

| 检查面 | 状态 | 证据与边界 |
|---|---|---|
| 当前运行架构与入口 | PARTIAL | `Program.Main` 启动 Avalonia classic desktop lifetime；`App.OnFrameworkInitializationCompleted` 组装 shell 与 `HostController`；`HostRuntime` 分别启动 `CoreServiceClient`、`HostBridgeClient`。这是当前代码链的静态核对；真实桌面 UI 本轮未启动。 |
| React / TypeScript / Tauri 与 Python Core 边界、旧代码误调用 | PARTIAL | 当前 Avalonia 启动链使用 C# Host 与 Python sidecars；历史 Tauri/Rust/前端测试保持 `NOT_RUN-legacy`。当前命令面以真实 Core/Wire smoke 作有限运行证据。尚未完成仓库内所有旧代码的调用闭包审计，不能据此宣称全仓旧实现均不可达。 |
| 前后端消息稳定性 | PARTIAL | Wire smoke 6/6 PASS，覆盖真实 Python 子进程与 wire v1 / Core protocol 2.3 的有限命令；其余 Core hook、所有 C# Host 侧集成行为没有有效测试结果。 |
| 模块循环依赖 | PARTIAL | 静态导入图报告一个 Python SCC；源位置显示相互引用均在函数内惰性导入。没有静态 .NET project-reference cycle。没有以此推断整个运行时无循环或无动态依赖。 |
| 状态重复、过度耦合、全局状态 | NOT_TESTED | 本阶段扫描器不分析语义级状态所有权、共享可变状态和完整跨模块耦合。需要按核心流程继续定向审阅。 |
| 异步与资源生命周期 | FAIL（隔离复现） | 见 `NM-AUD-0001` 和 sidecar probe 日志。测试宿主仍受阻；复现使用真实 `SidecarProcess` API 和受控 helper，不是现有 .NET unit suite 或真实生产 sidecar。 |
| 异常跨模块传播 | PARTIAL | C# client/Host 的若干 typed error 路由和 Python wire error envelope 有静态结构；既有 Wire 错误信封 smoke PASS。未完成所有异常分支的调用链审计，C# TestHost 未执行用例。 |

## AUDIT-02 扫描覆盖与缺口

已完成 Python 源文件语法解析、静态本地 import 图、.NET 项目引用图、solution 编译和 whitespace verification。扫描器明确不做 Python 类型检查、C# 方法级/Roslyn 语义扫描、动态导入完整闭包、死代码/重复逻辑判定、输入校验完整性、并发竞态或异常处理完备性判定。

源码搜索到的唯一 `NotImplementedError` 字符串位于 `src/infrastructure/providers/ocr_local.py` 的说明文档，描述 Paddle / oneDNN 外部历史问题；该处不是 raise 语句，不作为占位实现缺陷。此单点确认不代替完整 TODO、占位实现审查。

本阶段没有执行 Python pytest、Avalonia tests 或真实 GUI；使用的是已固定的 suite 报告，且保持各自 EXIT、PASS、BLOCKED、SKIP 状态。sidecar 隔离 probe 不是对 TestHost 的绕过，也不验证真实 UI 或 sidecar 功能。源码范围对照证明本阶段未改变受审产品源码/测试。后续应在不安装依赖的前提下继续手工高风险路径审阅；若所需工具或运行环境不可用，逐项保留 `BLOCKED` / `NOT_TESTED`。

一次中间 runner 重放 `20261112T142759897356Z` 因探针固定 PID 标记目录复用了前次已终止的 PID，结果中的 `child_alive=false` 检查的是旧 PID，故该 run 的两项生命周期测量**明确排除**。固定目录中的 marker 随后被新 helper 覆写为 PID `37212` / `43576`；这些 60 秒 sleep helper 未被该次脚本正确追踪/终止。`logs/sidecar-lifecycle-invalid-run-investigation-20261112.log` 记录了 marker 与后续进程查询；2026-11-12T14:36Z 查询时匹配的 helper 进程数为 0，符合其 60 秒自然结束，不代表产品清理成功。脚本随后改为每轮唯一 workspace 输出路径并拒绝已有 PID 标记；本报告只采用上表修正 run `20261112T143133097703Z` 的新 PID 复现结果。首次直接调用的原始输出亦留在 `logs/sidecar-lifecycle-probe-20261112.log`，不作为 Canonical Evidence。

## 需 ZCode 复核

1. 对 `NM-AUD-0001` 的严重等级候选、实际影响范围和问题分类作独立只读裁决。
2. 复核本报告是否把静态证据、运行证据和阻断边界分开表达，尤其是 import SCC 与 sidecar 清理结论。
3. 当前结论只是 AUDIT-01/02 阶段交付，不代表全审完成或 Release Gate 通过。
