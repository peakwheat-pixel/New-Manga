---
task_id: P20-AC4-FPS-1
reviewer: Codex
author: ZCode
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
reviewed_head: 16b99524794a7ff2132a19753ce6a7fcd53fc244
decision: approved
---

# P20-AC4-FPS-1 第四轮 Review

## 范围与结论

本 Review 固定审查实现 `16b995247`；Task 元数据提交为 `293d27208`。当前检出脚本字节与实现提交中的 Canonical Evidence pin 一致。实现仅触及验证 Runner、测量指南及 Review/验证材料；没有产品代码、IPC、Schema、ACL 或依赖变更。`apps/desktop/src-tauri/**` 不在本次审查范围内。

**结论：`decision = approved`；FPS-R1-02 已闭合，可以批准该实现集成。** 当前 Task 仍未完成：AC3 单页与 Webtoon 真实桌面测量为 `NOT_RUN`，由 Coordinator 执行；AC5 按用户裁决继续记 `NOT_VERIFIED_BY_RULING`。不得把这两项写成 PASS，也不得在 AC3 完成前将 Task 标为 `done`。

Owner 的 `P20-AC4-FPS-1-R3FIX.json`（2 字节）和 `response.md` 缺失按本轮输入说明如实记录。本结论完全依据代码、提交和磁盘证据；缺少 Owner 自述不构成独立拒绝理由。

## FPS-R1-02：CLOSED（P1）

- `run-ac4-fps.ps1:214-245` 的 `Assert-ForegroundIsPid` 用 `GetForegroundWindow` 与 `GetWindowThreadProcessId` 取得并校验前台 PID。前台 PID 不匹配时，滚轮路径允许一次 `TryActivate`；`run-ac4-fps.ps1:127-165` 的激活过程依次调用 `ShowWindow(SW_RESTORE)`、`SetForegroundWindow`、`BringWindowToTop`，前两次受限后发合成 Alt 再尝试；守卫随后在 `:234-244` 轮询并重新校验 PID，仍不匹配则调用 `Fail` 并返回 false。
- 滚轮调用点 `run-ac4-fps.ps1:921-930` 在调用 `M2Wheel.Wheel` 前执行守卫，失败即 `break`，不会设置光标或调用 `SendInput`。按键调用点 `:931-940` 检查 `AppActivate` 返回值；false 时记录失败并退出该循环，true 后再检查前台 PID，校验失败不调用 `SendKeys`。
- 最终可复核的真实窗口自检位于 `selfcheck-20261018-194056/fps-trace.log:23-33`。同一轮启动同标题 stub 与 decoy，以及独立 outsider 窗口；`:27` 证明 outsider PID 实际持有前台，`:28-30` 记录守卫拒绝并由 `Fail()` 登记失败，同时三个窗口的滚轮计数无增量；`:31` 证明通过激活和前台 PID 校验后，1 个滚轮事件只到 stub。逐窗口日志相符：`selfcheck-focus-stub.log:1-2` 为 handle + wheel，`selfcheck-focus-decoy.log:1` 与 `selfcheck-focus-outsider.log:1` 只有 handle、没有 wheel。
- 同轮 `:26` 还证明同一次全扫描返回 stub 并把同标题 decoy 登记为 `NOT_OURS_WINDOW`。对应实现 `run-ac4-fps.ps1:179-204` 扫描全部同标题窗口，只返回 PID 等于本轮 app PID 的项，没有首匹回退。
- 两个较早目录 `selfcheck-20261018-193652/fps-trace.log:23-26`、`selfcheck-20261018-193804/fps-trace.log:23-26` 都明确记录 `SELFCHECK FAIL`：三个子窗口进程启动后退出，未进入有效焦点断言；因此不把它们当作 PASS。后续 `194056` 记录完整 `SELFCHECK PASS`，Task 说明为 16 项断言。自检成功分支在 `run-ac4-fps.ps1:797-804` 显式 `exit 0`，失败分支 `exit 6`。

## 不回归检查

| 项目 | 结论 | 依据 |
|---|---|---|
| FPS-R1-01 隔离根与 fail-closed 快照 | PASS，未回退 | 四路径隔离校验与 AppData 快照完整性检查仍在 `run-ac4-fps.ps1:296-356`；比较遇到不可读项按变化处理见 `:366-380`。同 head SmokeTest 的 `smoke-20261018-194111/fps-trace.log:6-17` 与 `smoke-20261018-194147/fps-trace.log:6-17` 记录隔离写入、24 项 AppData unchanged 及本轮进程全退。两份磁盘前后清单均为 24 项且内容相同。 |
| FPS-R1-03 JSON artifact 与 SmokeTest 失败条件 | PASS，未回退 | CSV/JSON 解析、结构和本轮样本交叉校验见 `run-ac4-fps.ps1:976-1037`；窗口缺失、进程早退、隔离根空置进入 `Fail` 见 `:882-897`、`:1118-1125`，累计失败返回非零见 `:1146-1157`。 |
| `Find-WindowByTitleForPid` PID 绑定 | PASS | `run-ac4-fps.ps1:179-204` 全扫描并只返回本轮 PID 窗口；同标题 decoy 的 SmokeTest 轨迹 `smoke-20261018-194147/fps-trace.log:6-8` 记录 `NOT_OURS_WINDOW` 后绑定本轮 PID。 |
| `T` / `F` 命名 | PASS | 现用 `Write-Trace`（`:272`）与 `Find-UiaByName`（`:251`）；全文件静态检索未发现 `T()`、`F()` 或同名函数残留。 |

## 验证记录

| 检查 | 结果 | 证据/说明 |
|---|---|---|
| PowerShell Parser 与 `git diff --check` | PASS | Runner 语法错误数为 0；目标提交 diff check 无输出且退出码为 0。 |
| 同 head `-SafetySelfCheck` | PASS（已提交证据）；本轮复跑 `NOT_RUN` | `selfcheck-20261018-194056/` 是本 Task pin 的同 head 证据，16 项断言完成；R4 当轮未启动该命令：前置检查时前台是 DeepSeek Harness，系统空闲计时为 0 秒，等待器未满足桌面空闲门槛。为避免抢占正在使用的桌面，取消等待器。 |
| 同 head `-SmokeTest` 与 decoy | PASS（已提交证据）；本轮复跑 `NOT_RUN` | 两份 R3 SmokeTest 轨迹均记录 PASS；decoy 轮记录 AppData 24 项 unchanged、本轮进程全退及隔离根 4 文件/4 目录。R4 当轮未启动 SmokeTest，原因同上；没有由本轮启动的目标进程残留。 |
| Canonical Evidence 磁盘字节与 Git pin | PASS | Task `doc/tasks/P20-AC4-FPS-1.md:116-134` 共 19 项；逐项用 `Get-FileHash -Algorithm SHA256` 对磁盘原始字节重算，19/19 匹配。19 个 pin 的 commit 对象及 `commit:path` 均通过 `git cat-file -e`。 |
| Review 报告所含 40 位 Git SHA | PASS | Frontmatter 中的 `base_commit` 与 `reviewed_head` 均通过 `git cat-file -e <sha>^{commit}`。 |
| AC3 单页/Webtoon 实际测量 | `NOT_RUN` | 无本轮样本 CSV 或汇总；Coordinator 后续执行。不能以 SmokeTest 或焦点自检替代。 |
| AC5 撕裂验证 | `NOT_VERIFIED_BY_RULING` | 依用户裁决只登记 limitation，不做客观验证。 |

## 复审 Finding 状态

| ID | 级别 | R4 状态 | 处理结论 |
|---|---|---|---|
| FPS-R1-02 | P1 | CLOSED | 注入前验证前台 PID；必要时尝试激活并重验；未证实焦点时不发送滚轮/按键并进入非零失败路径。decoy + outsider 的真实窗口反例与正例均有同 head 磁盘日志。 |
| FPS-R1-02-AUDIT | P2 | CLOSED | 同标题窗口全扫描后再返回本轮 PID 窗口；自检日志同轮确认 foreign decoy 被登记。 |

本轮没有新发现的开放 finding。复跑未执行是本轮验证限制，不是被省略的 PASS；判断 R1-02 已关闭所依赖的是可核对的同 head 源码和已固定 SHA 的实测证据。

## 治理检查

`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-AC4-FPS-1.md` 返回 `PASS (3 warnings)`，exit 0。两条 warning 为 `STATUS.md` / `REBASELINE_PLAN.md` 体量预算提示；另一条报告 evidence_dir 含未登记文件，包括本 R4 Review 和历史过程文件。因本轮只获准写 Review，没有修改 Task 的 Canonical Evidence 表或整理历史文件；集成时由 Codex 登记本 Review pin，并按 §4.1 更新当前审查指针。

## 集成裁决与后续约束

**代码集成：可批准。Task 完成：不可批准。** 当前 `doc/tasks/P20-AC4-FPS-1.md` 的 `canonical_evidence_status` 仍是 `pending`，且该 Task/状态文件不在本轮获准写入范围；Codex 集成时需按协作协议登记本 Review 的证据 pin 并更新 Task 生命周期指针。集成后由 Coordinator 完成 AC3 单页与 Webtoon 测量；报告 `avg/p95/max`、样本及排除理由，保持 AC5 为 `NOT_VERIFIED_BY_RULING`，进程清理和 AppData unchanged 证据齐全后再判断 Task 是否完成。
