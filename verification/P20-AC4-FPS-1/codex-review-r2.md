---
task_id: P20-AC4-FPS-1
reviewer: Codex
author: ZCode
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
reviewed_head: 4c54f3dd10e5e7168500e96687b67097ccae2c00
decision: changes_requested
---

# P20-AC4-FPS-1 第二轮独立 Review

## 审查范围与复跑结果

复审实现 `4c54f3dd10e5e7168500e96687b67097ccae2c00`；Task 与 Canonical Evidence 更新来自 `5cc567f3ed8b190bcfadda621c68bf7e7eccd9c3`。按实现 head 固定源码审查，12 项 Canonical Evidence 磁盘 SHA-256 均匹配 Task 表内 pin。`tools/governance/check.ps1` 返回 `PASS (2 warnings)`，警告为 STATUS 与 REBASELINE_PLAN 文档预算达到 80%。

- `-SafetySelfCheck -OutDir %TEMP%\codex-review-p20fps-r2-selfcheck-2da1ca9db4194c0a8aff77e097ff6b03`：6 项 PASS，exit 0。
- `-SmokeTest -OutDir %TEMP%\codex-review-p20fps-r2-smoke-37527cb66e81413a9df247c0ee07df1f`：窗口出现且 app 存活；记录 11 个后代 PID；`TEARDOWN all our processes exited`；AppData 24 文件 UNCHANGED；隔离根 4 文件 / 4 目录；exit 0。收尾后 `m2rc1-desktop`、`core_service`、`host_bridge` 均为 0。
- Owner 保存的 `smoke-20261018-173917/appdata-baseline.txt` 与 `appdata-after.txt` 各有 24 个 SHA-256 条目且逐项相同；我重算了当前真实 AppData 24 个文件，均与清单相符。该次“未写 AppData”证据真实且可独立复现。
- AC3 单页与 Webtoon 真实滚动测量 **NOT_RUN**；本轮 SmokeTest 未执行采样或滚动。`npm test` 未复跑，Owner 日志记录 32 files / 324 tests passed。

## FPS-R1-01（隔离根）— PARTIAL

四个路径在 `run-ac4-fps.ps1:90`、`:99`、`:100`、`:101`、`:102` 全部设置；`Test-IsolationEnv` 在 `:110`、`:115`、`:118`、`:125` 读回并限制在隔离根内。运行前 `%TEMP%` 新建根的设置及 fail-closed 分支见 `:355`、`:361`。本轮自检通过缺项、越界拒绝；SmokeTest 也确实将写入落在隔离根，用户 AppData 24 项不变。

仍有一处证明保护缺口：`Get-TreeManifest` 在 `run-ac4-fps.ps1:140` 对目录枚举错误使用 `SilentlyContinue`，在 `:142`、`:144` 将哈希错误记作 `UNREADABLE`；若同一路径前后均读失败，`Compare-Manifests` 的 `:156`、`:170` 可把不完整快照当成未变化。当前两次实际快照没有该问题，但实现应在扫描或哈希不完整时 fail closed。**未验证项：** 未对 AppData 枚举 / 哈希错误做故障注入。

## FPS-R1-02（进程清理）— PARTIAL

本轮进程树采集、家族白名单复核和统一 teardown 得到实测支持：`Get-DescendantPids` / `Update-OurPids` 见 `run-ac4-fps.ps1:174`、`:193`；白名单清理、孤儿复扫及残留失败判定见 `:200`、`:208`、`:222`、`:235`、`:249`；主流程 `try/finally` 见 `:398`、`:557`、`:560`。本轮开始时没有既有目标进程，故未验证 `NOT_OURS` 的实机路径；脚本在 `:369`、`:371` 会登记 `m2rc1-desktop`、`core_service`、`host_bridge`。

残留风险：窗口查找 `Win()` 在 `run-ac4-fps.ps1:377`、`:382` 只按窗口标题取首个匹配窗口，没有核对 `AutomationElement.Current.ProcessId` 是否等于本轮 `$appProcess.Id`。后续 shell 检查与 UIA 操作使用该结果（`:402`、`:416`、`:420`、`:465`）。若同标题且带测量面板的旧窗口存在，清理虽不会杀它，测量流程仍可能点击或滚动它。应将窗口绑定到本轮 PID，不匹配时拒绝操作。该并发场景未在本轮实测。

## FPS-R1-03（失败即非零）— PARTIAL

退出码表与实现基本一致：OutDir 已存在 `4`（`:83`）、构建失败 `5`（`:326`、`:337`）、缺 exe / 无窗口 `2`（`:342`、`:418`）、采样未开启 `3`（`:419`）、隔离拒绝 `7`（`:350`、`:358`、`:360`）、累计失败 `6`、无失败 `0`（`:601`–`:610`）。CSV 缺失、无 kept 样本、均值超限、AppData 变化和进程残留会累积到非零退出。

但 JSON required artifact 仍可能错误地通过：`CaptureRound` 在 `run-ac4-fps.ps1:490` 忽略 `Show JSON` 按钮返回值，`:492`、`:496` 只校验文本非空；若 Show JSON 失败，textarea 仍可能保留先前 CSV，脚本会将 CSV 写成 `.json`。主流程 `:549`、`:550` 只检查 JSON 文件存在，不解析 JSON 或核对内容，因此可产生错误 artifact 并最终 exit 0。按钮失败必须记为失败，且需验证 JSON 格式与本轮数据。

此外 `-SmokeTest` 有 false-pass 路径：`:409`、`:413` 只记录 `window_seen` / `app_exited`，未据此 `Fail`；`:575`、`:576` 对隔离根无写入仅输出 warning；最终 `:601`、`:610` 在 failure list 为空时仍 exit 0。若 app 启动后立即退出或未产生预期隔离写入，SmokeTest 仍可能成功退出。当前复跑确实见到窗口、存活进程和 4 个隔离文件；未对该失败注入路径做运行验证。应将窗口缺失、启动进程退出或隔离根未产生预期文件纳入失败条件。

## FPS-R1-04（显式 Save As）— PASS

`FpsRecorderPanel.tsx:53`、`:87` 仅通过 `window.showSaveFilePicker()` 写入用户选择的 opaque handle；`AbortError` 返回 `cancelled`，不写文件；API 不可用时返回 `unsupported`，没有默认下载回退。导出入口见 `:164`、`:181`。测试分别检查显式保存、取消无写入及 API 缺失无写入（`FpsRecorderPanel.test.tsx:182`、`:218`、`:240`），并断言没有 `createObjectURL` / anchor click（`:212`、`:214`、`:253`、`:255`）。旧静默下载路径已删除。目标 WebView2 上的原生 picker 未在本轮 GUI 验证；SmokeTest 不涉及导出。

## FPS-R1-05（隐藏区间 gap 排除与双口径）— PASS

`fpsRecorder.ts:243`–`:249` 通过采样到的 hidden interval 与帧间隔做交叠判断；`:264`–`:269` 只在 delta ≥ 1000ms 且确有交叠时排除。可见前台长停顿保持在 kept 统计中。`allMaxMs` / `excludedMaxMs` 分别在 `:305`、`:306` 输出；runner 独立复算和报告见 `run-ac4-fps.ps1:514`、`:515`、`:525`–`:527`。测试覆盖 hidden 相交排除、可见停顿保留和双最大值（`fpsRecorder.test.ts:234`、`:266`、`:282`）。源码与 Owner 的 324 项测试日志相符；测试本轮未重跑。

## Standards

- **P1，阻断：** FPS-R1-02 所述 UIA 窗口未绑定本轮进程，无法保证 `NOT_OURS` 用户实例不被自动化操作；依据 `run-ac4-fps.ps1:377`–`:382`、`:402`、`:465`。这与保护用户数据、人工状态和可恢复性的仓库约束冲突。
- **非阻断 smell：** `run-ac4-fps.ps1:86` 的 `T`、`:384` 的 `F` 属于 possible Mysterious Name；建议改成能表明日志与 UIA 查找职责的名称。其他 smell baseline 未发现阻断项。

## Spec 与治理指针

- 原 R1 finding 状态：`FPS-R1-01 PARTIAL`、`FPS-R1-02 PARTIAL`、`FPS-R1-03 PARTIAL`、`FPS-R1-04 PASS`、`FPS-R1-05 PASS`。
- AC3 仍为 `NOT_RUN`，必须由 Coordinator 完成真实桌面测量后再判定 Task AC3。
- `doc/STATUS.md:9` 仍将该子 Task 的交付 head 写为 `011293151`，而 Task frontmatter 已更新为 `4c54f3dd1`。当前状态指针需由 Codex / Coordinator 同步；本 Review 按用户指定的完整实现 SHA 复审。

## 集成裁决

**不可批准集成，decision = `changes_requested`。** 阻断项为：AppData 清单读错误未 fail closed；UIA 窗口未绑定本轮 PID；JSON 抓取失败和 SmokeTest 启动/隔离失败都存在错误 exit 0 的路径。另 AC3 尚未由 Coordinator 执行。完成修复后应由 Codex 再审，再由 Coordinator 执行 AC3；`NOT_VERIFIED_BY_RULING` 撕裂限制继续保留。

## 双轴计数

Standards：1 条阻断 finding，最严重项是 UIA 窗口未绑定本轮 PID；另有 1 条非阻断命名 smell。Spec：3 条未完全满足项，最严重项是 JSON 抓取失败仍可能产生错误 artifact 并 exit 0；其余为 AppData 快照错误不 fail closed、SmokeTest 可能错误 PASS。AC3 为未执行项。

DECISION: changes_requested
