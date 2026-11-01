---
task_id: FEA-02-CORE
author: Codex（实现会话；未独审）
recipient: DeepSeek Harness
base_commit: bf1c8eb0081fcc2b0a9d8dccf1fb43d5b9041b35
delivery_head: 5efb8f58c88e1acb11eaf53b1eab9135f26f29db
status: in_review
---

# Handoff：FEA-02-CORE

实现已固定，**未满足全部交付门槛**：新内核 25 项测试通过，solution build 通过；solution test 仍有与基线完全相同的 3 项 Host 清理失败。AC5 保守标 PARTIAL，AC7 待 DSH 指定的独立上下文复核；本 Task 未 approved、未集成、未 done。

## 实现与范围

实现提交：`5efb8f58c88e1acb11eaf53b1eab9135f26f29db`，`feat(application-core): share Run polling and coordinate in-flight intents`。

起点为用户指定 `bf1c8eb00`，先快进到 `2546410c4` 纳入 DSH 的 Task ready/FEA-01 收口元数据，再开始实现。`2546410c4..5efb8f58c` 是本次新增实现与验证材料；本 Handoff 和 Task/STATUS/Plan/ledger/checkpoint 更新在后续文档提交，不改变被测实现。

| 路径 | 交付 |
|---|---|
| apps/desktop-avalonia/src/NewManga.ApplicationCore/ | 纯 .NET 状态/轮询/意图去重/请求结果；调用及生命周期说明 |
| apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/ | 25 项 L2 自动化测试；使用虚拟时钟、闸门、并发计数 |
| apps/desktop-avalonia/NewManga.sln | 两个新项目及各自配置/嵌套行；原有项目与平台行不变 |
| verification/FEA-02-CORE/ | 基线/交付 build/test 原始日志、逐项测试摘要、边界脚本、pin 审计 |

生产项目没有任何包/项目依赖；测试依赖复用仓库已有 Microsoft.NET.Test.Sdk 17.12.0、xunit 2.9.2、runner 2.8.2，没有新增依赖品类。没有修改 NewManga.App、CoreClient、Host、Python、既有测试、冻结契约或其他 Task。没有组合根/DI 改动，不接线 Current，没有第二条启动路径。

为遵守端口/写域边界，未把 App 中的 DTO 或错误映射搬入新库。新库通过泛型不可变快照和委托接收未来适配层；请求失败的源 code 原样保留，无 wire/category 映射或白名单。快照只接受适配层的成功查询结果，不自行推算完成状态/进度。

## AC 与验证

| AC | 结果 | 实际证据 |
|---|---|---|
| AC1 无 Avalonia | MET | 生产程序集引用清单只含 System*；csproj 无 ProjectReference / PackageReference |
| AC2 多观察者一次轮询 | MET | 32 订阅 + 32 并发 refresh 共享一次底层调用，同一快照引用；虚拟时钟推进后只多一次调用 |
| AC3 进行中意图去重 | MET | 64 并发调用同一键，task/result 相同且启动计数 1；完成后允许新意图，原键传给适配器 |
| AC4 错误隔离 | MET | 并发成功/失败/超时/取消；单个等待者取消不影响共享请求；失败缓存保护、迟到结果和旧订阅代际隔离 |
| AC5 Current/全量回归 | PARTIAL | Current 396 passed / 7 skipped，与基线相同；结构/不接线断言通过。但全 solution 仍 FAIL（同基线 3 项），未满足全部 test 通过要求 |
| AC6 前置 | MET | L-1/L-2/L-5 本写域 NOT_APPLICABLE；无 schema、wire 新码/投影搬迁、恢复互斥；原再触发条件保留 |
| AC7 独立复核 | BLOCKED | 待 DSH Appointment；未生成自审报告 |

环境 Windows，SDK 10.0.401、目标 net9.0。实际 build/test 使用隔离 TEMP/TMP：

```powershell
$env:TEMP='G:/CODEX/New Manga.workspace/task-envs/FEA-02-CORE/tmp'
$env:TMP=$env:TEMP
$env:DOTNET_CLI_TELEMETRY_OPTOUT='1'
dotnet build apps/desktop-avalonia/NewManga.sln --verbosity minimal
dotnet test apps/desktop-avalonia/NewManga.sln --no-build --logger 'trx;LogFilePrefix=final' --results-directory 'build/FEA-02-CORE/final-results' --verbosity minimal
pwsh -NoProfile -File verification/FEA-02-CORE/collect-test-results.ps1
pwsh -NoProfile -File verification/FEA-02-CORE/verify-boundaries.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-02-CORE.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
```

- solution build：EXIT=0，0 warnings / 0 errors。
- solution test：**EXIT=1**，905 passed / 3 failed / 60 skipped；新增 ApplicationCore 25 passed / 0 failed / 0 skipped。943 项既有测试按稳定 TRX testId 对照，outcome 变化 0。
- 基线：880 passed / 3 failed / 60 skipped，同样 EXIT=1。原测试未修改、未过滤；60 个现有 skip 均有 sidecar fixture 原因，逐项保存在摘要，不计入 passed。
- 边界脚本 PASS；15/15 冻结 pin PASS。交付文档落盘后治理检查 PASS（2 warnings：11 个非终态 Task、STATUS 达预算 80%）；检查不替代独审。
- 没有执行真实 Host/Core 接线或 GUI 验证，只声明 L2；接线后的单一路径启动验证必须由后续授权 Task 完成。

完整日志与 AC 映射见 [验证说明](../../verification/FEA-02-CORE/README.md)，[逐项结果/skip/失败栈](../../verification/FEA-02-CORE/test-summary.json)；Task Canonical Evidence 以实现 head + SHA-256 登记所有本目录文件。原 TRX 位于工作树 build 下，hash 已入摘要，留供复核。

## 未满足项与风险

三项既有失败均发生在旧 Host 测试的 Dispose：Directory.Delete 递归清理 junction 时 UnauthorizedAccessException，路径名分别为 junc/sub。名称与完整栈见 test-summary.json：

- TileChannelTests.Containment_OutsideRoot_And_Junction_Rejected。
- D4SecurityHarnessTests.D4_3_Escape_RejectedAtIssue。
- D4SecurityHarnessTests.D4_3_Escape_RejectedAtReadTime_AfterPathReplacement。

这三项没有因新库而新增，但不能据此把全量 test 写 PASS。本 Task 不授权修改它们；请 DSH 处置是否另立基线失败诊断范围。若坚持全量测试门槛，必须保留 AC5 未满足，不得直接标 done。

内存去重只覆盖进行中的操作；超时不意味着远端操作已停止，后续适配层必须沿用 Core 原幂等键处理不确定结果，不能把本库当持久 exactly-once 保障。取消仅保证本层结束等待、请求底层取消并拒绝迟到结果。快照 T 必须不可变；UI 接收方负责 dispatcher 与窗口生命周期。已在执行的回调可能在退订后结束，回调须快速返回。这些边界在生产 README 中明确。

新 worktree 曾因 core.autocrlf=true 检出 CRLF 导致 15 个工作树 pin 不符。逐份验证仅 EOL 差异后，从同 HEAD 的原 Git blob 恢复，最终冻结字节与 pin 一致，git diff 为 0；没有改 pin、正文、冻结记录或 Git 配置。重新检出时仍可能复现，应另行治理，不能重算 pin 掩盖。

所有 worktree/build/bin/obj/task-env/agent-output 保留；没有删除/prune、安装、迁移、用户数据访问或 push。最终资源处置、主线集成与 Task done 均仍归 DSH。

## 接收与下一步

- 接收者：DSH，安排 `c01b-reviewer` 的独立上下文 Review；具体 Agent 来源由 DSH 在报告中登记。实现者本会话不能自审。
- Recovery point：主仓库 `G:/CODEX/New Manga`；工作树 `G:/CODEX/New Manga.workspace/FEA-02-CORE`；分支 `feat/fea-02-core`；固定 base `bf1c8eb0081fcc2b0a9d8dccf1fb43d5b9041b35`、release `2546410c41c0e78ffd8807f2cb2ec5485bb5762b`、实现 head `5efb8f58c88e1acb11eaf53b1eab9135f26f29db`。
- 审查范围：上述实现/对应测试/solution/验证材料，只读该固定 head；不要写 App/CoreClient/Host/Python/冻结契约/其它 Task 或顺手修基线失败。返修须由实现方执行并提供新 head、新 Handoff。
- 交付物：DSH 指定的 `doc/reviews/FEA-02-CORE-r1.md`，精确绑定 base/head，覆盖 AC1–AC6 及测试失败限制，不得把机械 PASS 或单测通过当 AC7。
- 完成 Gate：独立复核、全量测试失败处置、DSH 集成与资源 closeout；在这些条件前不批准 Task done、不释放其它实现 Task。

可直接转发给 DSH：

> 请接收 FEA-02-CORE：工作树 G:/CODEX/New Manga.workspace/FEA-02-CORE，分支 feat/fea-02-core，固定实现 head 5efb8f58c88e1acb11eaf53b1eab9135f26f29db（base bf1c8eb00，release 2546410c4）。请按 Appointment 安排独立上下文只读复核 AC1–AC6，报告 doc/reviews/FEA-02-CORE-r1.md 并登记审查来源。新增 25/25 单测及 solution build 已通过；solution test 仍有与基线相同的 3 个 Host junction 清理失败、60 个既有 sidecar skip，不能写全量 PASS。先审代码并处置 AC5 基线失败；未授权修改 Host/旧测试、冻结契约或其它候选。复现命令、原始日志、逐项结果和资源保留记录见本 Handoff 与 verification/FEA-02-CORE；未 push、未集成、未自审。

没有已授权的下一实现 Task；当前下一步仅为 DSH 接收本交付、安排独审及处置测试门槛。
