# FEA-02-CORE 实现验证

被测代码：本目录所在实现提交（由后续 Handoff / Task 的 `delivery_head` 固定）。源代码基线 `bf1c8eb0081fcc2b0a9d8dccf1fb43d5b9041b35`；先快进纳入任务释放提交 `2546410c41c0e78ffd8807f2cb2ec5485bb5762b`。该提交只更新 FEA-01 收口与 FEA-02-CORE 释放文档，不含程序代码。

工作树 `G:/CODEX/New Manga.workspace/FEA-02-CORE`，分支 `feat/fea-02-core`。Windows、.NET SDK 10.0.401，项目目标 net9.0；测试复用仓库已有 xunit / Test SDK 版本，生产项目无 PackageReference / ProjectReference。没有安装器、迁移、用户数据或 GUI 操作。

## 实际命令与结果

各次构建/测试均设置：

```powershell
$env:TEMP='G:/CODEX/New Manga.workspace/task-envs/FEA-02-CORE/tmp'
$env:TMP=$env:TEMP
$env:DOTNET_CLI_TELEMETRY_OPTOUT='1'
dotnet build apps/desktop-avalonia/NewManga.sln --verbosity minimal
dotnet test apps/desktop-avalonia/NewManga.sln --no-build --logger 'trx;LogFilePrefix=final' --results-directory 'build/FEA-02-CORE/final-results' --verbosity minimal
```

基线使用相同命令，前缀 `baseline`，结果目录 `build/FEA-02-CORE/baseline-standard-results`，当时 solution 尚未新增两项目。实现后使用上列命令。

| 项目 | 基线 passed / failed / skipped | 交付 passed / failed / skipped |
|---|---|---|
| ApplicationCore.Tests | 不存在 | 25 / 0 / 0 |
| App.Tests（Current） | 396 / 0 / 7 | 396 / 0 / 7 |
| CoreClient.Tests | 116 / 0 / 25 | 116 / 0 / 25 |
| Host.Tests | 48 / 3 / 28 | 48 / 3 / 28 |
| DesignSystem.Tests | 85 / 0 / 0 | 85 / 0 / 0 |
| ThemeEngine.Tests | 235 / 0 / 0 | 235 / 0 / 0 |
| 合计 | 880 / 3 / 60 | 905 / 3 / 60 |

两次 solution build 均 EXIT=0，0 warnings / 0 errors。两次 solution test 均 **EXIT=1，不能写 PASS**。943 项既有测试按 TRX `testId` 对照，outcome 变化 0；理论测试显示名会截断，不能仅按显示名 join。`test-summary.json` 保存逐项结果、全部 60 个 skip 的原因及 3 个失败的消息/调用栈。skip 均为现有环境缺少 sidecar fixture，未将 skip 计入 passed，未新增过滤器或跳过项。

三个相同失败都发生于旧测试的 `Dispose()`，`Directory.Delete(..., recursive: true)` 清理 junction 时抛 `UnauthorizedAccessException`：

- `NewManga.Host.Tests.TileChannelTests.Containment_OutsideRoot_And_Junction_Rejected`
- `NewManga.Host.Tests.D4SecurityHarnessTests.D4_3_Escape_RejectedAtIssue`
- `NewManga.Host.Tests.D4SecurityHarnessTests.D4_3_Escape_RejectedAtReadTime_AfterPathReplacement`

既有测试、Host 源码和用户数据均未修改。全量测试必须通过的要求尚未满足；交 DSH 判断是否单独释放基线失败诊断，不在本 Task 越域返修。

早先把 `--artifacts-path` 放到仓外、以及工作树根部 build 下，曾因既有测试向上定位 solution 的约定产生额外失败；这些尝试不作为 Current 回归结论，原始日志留在 agent-output。采用默认项目输出路径后，定位失败消失，仅余上述三项。

## AC 对照

| AC | 可执行验证 | 结论与边界 |
|---|---|---|
| AC1 | `RequestExecutorTests.Assembly_has_no_presentation_transport_or_storage_dependency` | 生产程序集仅引用 System*；csproj 无包/项目依赖 |
| AC2 | `RunMonitorTests.Many_observers_share_one_query_and_the_same_snapshot_then_one_next_tick` | 32 个订阅 + 32 个 refresh；底层计数 1，引用相同快照；虚拟时钟下一 tick 只增一次 |
| AC3 | `IntentCoordinatorTests.Concurrent_retries_of_pending_intent_share_one_start_task_and_result` | 64 个并发调用一次启动，task/result 相同；新意图可启动。超时后释放本地飞行记录，原键须继续传 Core 做持久幂等 |
| AC4 | RequestExecutor / IntentCoordinator / RunMonitor 的失败、超时、取消及迟到结果测试 | 并发成功保留自身结果；单个等待者取消不取消共享请求；失败不覆盖最后成功快照；退订/重订后的旧结果不覆盖新缓存 |
| AC5 | `verify-boundaries.ps1` + 基线/交付日志 + `test-summary.json` | Current 回归与结构断言通过；不接线、没有第二调度路径；全 solution 未通过（既有 3 失败），接线后运行验证不在本 Task |
| AC6 | `verify-boundaries.ps1`、程序集依赖断言、代码检查 | L-1/L-2/L-5 本范围 NOT_APPLICABLE；没有 DB/schema、wire 新码/category 投影、恢复维护锁 |
| AC7 | DSH 按固定实现 head 安排上下文独立 Review | **NOT_RUN**；本会话未出具独审报告或 approved |

除上述主路径，新测试还覆盖最后订阅取消、缓存重放、多个 Run 隔离、回调异常/重入、重复 Dispose、取消不合作适配器和原始拒绝码透传。只完成 L2 自动化单元验证；未执行 GUI/真实 Host/Core 接线验证，不标 L3/L4。

可复现的汇总/边界/机械校验：

```powershell
dotnet test apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/NewManga.ApplicationCore.Tests.csproj --verbosity minimal
pwsh -NoProfile -File verification/FEA-02-CORE/collect-test-results.ps1
pwsh -NoProfile -File verification/FEA-02-CORE/verify-boundaries.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-02-CORE.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
```

`collect-test-results.ps1` 需要保留的两次原始 TRX；摘要入库，原 TRX 位于工作树 build 目录并留存其 SHA-256，原始 build/test 日志也已入库。新增基线/交付轮次时应使用独立目录，避免覆盖。

## 冻结字节与资源

新工作树默认 `core.autocrlf=true`，首次检出 15 份冻结契约成为 CRLF，造成工作树 pin 15 项不符；主仓库原文件与 Git blob 均匹配。先逐份确认仅 CRLF 差异，再从同一 HEAD 的原始 blob 恢复本工作树的冻结字节，最终 `pins.log` 为 **15/15 PASS**，`git diff HEAD -- doc/plan` 为 0。没有修订正文、pin、冻结记录或 Git 配置。此问题在新检出环境可能再现，应由 DSH 另行治理，不能重算 pin 掩盖。

`boundaries.log` 记录受保护路径、既有测试、solution 旧项目/平台配置、无接线及 Task 写域断言。solution 仅添加两项目及这两项目自身的配置/嵌套行，旧项目行与平台配置全部保持。

产物只在 `New Manga.workspace` 内：工作树、工作树内 build/bin/obj、`task-envs/FEA-02-CORE`、`agent-output/codex/FEA-02-CORE`；未清理资源或 linked worktree，无 push。详细资源处置待 DSH，见 Task Resource Manifest。
