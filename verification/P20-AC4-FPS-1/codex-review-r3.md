---
task_id: P20-AC4-FPS-1
reviewer: Codex
author: ZCode
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
reviewed_head: de5c06a4d
decision: changes_requested
---

# P20-AC4-FPS-1 第三轮独立 Review

## 范围与结论

固定审查实现 `de5c06a4d572c849de7d7fed8e5027f92e0de156`；Task/Handoff 登记文档提交为 `d79d9b8d7`。当前工作区 `HEAD=d79d9b8d7`，本结论只针对上述实现 head。R2 变更触及 Runner 与测量指南及其证据，没有改产品代码；复审期间未改 `apps/desktop/src-tauri/**`、`.qoder-credits/report.json`、`doc/REBASELINE_PLAN.md` 或 `doc/STATUS.md`。

**不能批准集成：FPS-R1-02 仍有 P1 阻断。** 窗口查询和二次 PID 校验已修正，但真实测量的滚轮/按键注入仍可能作用于未归本轮 app 所有的焦点窗口。

## Architecture

`de5c06a4d` 变更仅在测量 Runner、指南和验证证据中；没有修改应用层、Tauri IPC、共享契约、Schema、ACL 或依赖。产品分层审查为 N/A。Runner 的全局输入焦点问题属于本任务的窗口所有权与测量安全边界，已列为 P1。

## 逐项复审

### FPS-R1-02：PARTIAL，P1 未关闭

- `verification/P20-AC4-FPS-1/run-ac4-fps.ps1:101-120` 的 `Find-WindowByTitleForPid` 只会返回 `Current.ProcessId == ownerPid` 的顶层窗口，没有“取第一个同标题窗口”的回退；异 PID 窗口在扫描到时写 `NOT_OURS_WINDOW`。测量路径在窗口就绪后确实调用 `Assert-OurWindow`（`:123-129,624-629`）。`Stop-OurProcesses` 只处理本轮记录的 app/后代 PID（`:295-344`）。
- **P1：滚动注入没有绑定焦点窗口 PID。** `wheel` 分支只把鼠标指针移到窗口矩形中心，再用全局 `SendInput` 发滚轮事件（`:643-650,655-668`）；它没有先激活或确认本轮 app 是焦点窗口。Windows 将 `WM_MOUSEWHEEL` 发送给焦点窗口，因此如果操作者刚从终端按 Enter、或其他窗口此时获得焦点，滚轮会发给那个窗口而不是 `$win`。`keys` 分支虽调用 `AppActivate`，但忽略返回值并继续 `SendKeys`，激活失败时同样没有 fail-closed（`:667-668`）。这既可能滚动/操作异 PID 窗口，也可能使测量无效。[Microsoft `WM_MOUSEWHEEL` 文档](https://learn.microsoft.com/en-us/windows/win32/inputdev/wm-mousewheel)。应在每轮输入前确认焦点 PID 属于本轮 app；激活失败或焦点不符时立即失败，不发送输入。
- 另有审计覆盖细节：找到本轮窗口时函数立即 `return`（`:110-119`），因此同一 UIA 枚举中排在它之后的异 PID 同标题窗口不会被登记。当前代码仍能保证返回窗口的 PID 匹配，但“枚举全部并登记异 PID”的表述不完全成立；应保存本轮窗口并扫描完全部结果后再返回。
- Owner 的 decoy-in-the-loop 证据有可复核 trace。本轮独立复跑也复现了同标题 decoy PID `49408` 被记为 `NOT_OURS_WINDOW`、本轮 app 窗口 PID `34344` 与 app PID 相等、app 家族收尾全退、AppData 24 个文件 `UNCHANGED`；SmokeTest 结束后 decoy 仍存活。该证据证明窗口查找与 SmokeTest 清理没有碰 decoy，但 SmokeTest 不注入滚动/按键，不能证明真实测量路径不会向异 PID 窗口发送输入。

### FPS-R1-01：PASS（实现与本轮实际枚举注入）

`Get-TreeManifest` 记录 `ENUM_FAIL`/`HASH_FAIL`，哈希调用使用 `-ErrorAction Stop`（`run-ac4-fps.ps1:214-230`）；基线快照不完整在启动前 `exit 7`（`:580-589`）；终末快照不完整加入 failures，最终以 `exit 6` 失败（`:836-842,878-880`）。`Compare-Manifests` 将 `UNREADABLE` 作为变化/不可证明未变处理（`:250-264`）。

Owner 在 Task `:99`、Runner `:432-464` 与 R2 trace 中明确披露：其令牌启用 `SeBackupPrivilege`，所以把枚举注入降为 `PASS-by-channel`，没有冒称完成 deny-ACL 注入。这项披露诚实；当前 Reviewer 令牌未走该降级分支，本轮自检实际对目录施加临时 deny ACL 并在 `selfcheck` trace 第 15 行观察到 `ENUM_FAIL ... Access is denied`。同一 trace 第 12–14 行验证 `HASH_FAIL` 入表和双侧 `UNREADABLE` 判为非 unchanged，12 项自检全部通过。因此 Owner 环境限制本身不再留下本轮验证缺口。基线不完整 exit 7 与终末不完整 exit 6 的完整 Runner 退出路径本轮按代码核验，未另做端到端故障注入。

### FPS-R1-03：PASS（实现路径）；端到端 UIA 导出未运行

`Show CSV` / `Show JSON` 调用失败都会进入 failure list，失败时不写 textarea 旧内容；CSV 检查列结构，JSON 解析后校验 `meta.task`、计数、`samples[]` 长度与 CSV 行数、首末 `frameTsMs`（`run-ac4-fps.ps1:691-765`）。SmokeTest 的窗口缺失、启动/settle 期间早退会调用 `Fail`（`:605-620`）；隔离根没有新增文件或目录会调用 `Fail ISO_EMPTY`（`:845-853`），最终统一返回非零（`:874-880`）。本轮 SmokeTest 验证的是成功路径；缺窗、早退、空隔离根及真实测量中的 UIA/JSON 交叉核对未做故障注入或端到端运行。

### T/F 命名 smell：PASS

`T` 已改为 `Write-Trace`，`F` 已改为 `Find-UiaByName`，相关定义与调用点同步（`:133-156` 及 Runner 各调用处）；旧函数定义/调用无残留。PowerShell parser 报告 0 个语法错误。

### AC3 与 Canonical Evidence

- **AC3 真实桌面单页/Webtoon 测量：`NOT_RUN`**，仍归 Coordinator。没有样本 CSV、`avg/p95/max` 或测量 PASS；SmokeTest 不是 AC3 测量证据。
- Task `doc/tasks/P20-AC4-FPS-1.md:110-124` 的 Canonical Evidence 共 15 条。本轮按 Windows 磁盘真实字节运行 SHA-256，15/15 与表内 pin 一致，且每行记录的 commit 均包含对应文件。
- `pwsh -NoProfile -File tools/governance/check.ps1` 返回 `PASS (2 warnings)`；Task 定向检查 `...check.ps1 -TaskPath doc/tasks/P20-AC4-FPS-1.md` 返回 `PASS (3 warnings)`。warning 包括 STATUS/PLAN 文档预算达到 80%、本 r3 Review 尚未 pin 入 Task，以及已有 `selfcheck-20261018-173814/` 过程文件未登记；检查器为只读。按用户写入范围未改 Task 或状态指针。`doc/STATUS.md:9` 仍记 R2 `changes_requested (4c54f3dd1)`，集成前需由授权者同步权威指针并按协作协议登记 r3 Review。

## 验证记录

| 场景 | 命令/环境 | 结果 | 证据 |
|---|---|---|---|
| SafetySelfCheck | `pwsh -NoProfile -File verification\P20-AC4-FPS-1\run-ac4-fps.ps1 -SafetySelfCheck -OutDir <TEMP>\safety` | **12/12 PASS，exit 0**；本令牌实际跑 deny-ACL 枚举注入 | `%TEMP%\P20-AC4-FPS-1-codex-r3-02e73facf38443b0ab675573717fdc97\safety\fps-trace.log:12-22` |
| SmokeTest + 同标题 decoy | 同脚本 `-SmokeTest -OutDir <TEMP>\smoke`；外部 decoy PID `49408` 在场 | **exit 0**；窗口绑定 `34344==34344`；AppData 24 文件 unchanged；本轮进程全退；decoy 检查后仍存活 | `%TEMP%\P20-AC4-FPS-1-codex-r3-02e73facf38443b0ab675573717fdc97\smoke\fps-trace.log:6-17`；执行器另确认 `DECOY_ALIVE_AFTER=True` |
| T/F 与脚本语法 | 静态搜索旧调用；`[System.Management.Automation.Language.Parser]::ParseFile(...)` | PASS；无旧 `T()`/`F()` 调用，0 parser errors | `run-ac4-fps.ps1:133-156` 与全文件搜索结果 |
| Canonical Evidence | 按磁盘字节 `Get-FileHash -Algorithm SHA256`，并核对 pin commit 中的路径 | **15/15 MATCH** | Task `:110-124` |
| AC3 真实桌面测量 | 未运行（Coordinator 执行） | **NOT_RUN** | 本轮未生成测量样本或汇总 |

临时运行输出均位于 `%TEMP%\P20-AC4-FPS-1-codex-r3-02e73facf38443b0ab675573717fdc97\`；没有把 SmokeTest 记成真实桌面测量，也没有将 `NOT_RUN` 写成 PASS。

## 未验证项

- AC3 单页与 Webtoon 的真实交互式滚动测量，以及其 `avg/p95/max` 样本汇总：`NOT_RUN`，归 Coordinator。
- `Show CSV/JSON` 在真实 UIA 测量会话中的端到端抓取与交叉核对：未运行；当前为代码路径审查。
- SmokeTest 窗口缺失、启动早退、隔离根空置的负向注入，以及基线不完整 `exit 7`、终末快照不完整 `exit 6` 的整流程故障注入：未运行；调用链已静态核验，hash/枚举/双侧 unreadable 的 manifest 故障注入已实跑。
- `npm test`：本轮未重跑；R2 实现未改前端，Task 中既有 324 测试 pin 保留。

## Findings 与集成裁决

| ID | 级别 | 状态 | 依据 | 触发与影响 | 建议 |
|---|---|---|---|---|---|
| FPS-R1-02 | **P1** | **OPEN** | `run-ac4-fps.ps1:643-668` | 当 app 不是焦点窗口时，全局滚轮/按键输入可能发给异 PID 窗口；SmokeTest 不覆盖输入注入。 | 注入前确认前台 PID 是本轮 app；激活失败/焦点不符即中止；补测 decoy 在场时的滚动路径，并确保外部窗口未收到输入。 |
| FPS-R1-02-AUDIT | P2 | OPEN | `run-ac4-fps.ps1:110-119` | 自有窗口先被找到时提前返回，之后的异 PID 同标题窗口不会记入 `NOT_OURS_WINDOW`。 | 扫描完全部同标题顶层窗口后再返回匹配 PID 的窗口。 |

**结论：`decision = changes_requested`，当前 `de5c06a4d` 不可批准集成。** 修复 P1 后由 Codex 对新 head 复审；获批后 Coordinator 仍须完成 AC3 真实桌面测量。AC3 完成前 Task 不得标记为完成。

DECISION: changes_requested
