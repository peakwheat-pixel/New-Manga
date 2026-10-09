---
task_id: P02
title: 真实 Workbench WebView 行为、300ms 刷新与对比度验证 (Stage A 定向修订 Handoff r6)
status: in_progress
stage: STAGE_A_SAFE_FOUNDATION_R6
author: Antigravity
reviewer: DeepSeek Harness
integrator: Codex
worktree: G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity
branch: agent/antigravity/P02-real-webview-harness
base_commit: 241ff3b70b6fc0490ea238efd486cc707f849031
scope_contract_sha256: 27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425
reviewed_head_r1: 972049f991b5c119555647eeea816e89dd4769f3
dsh_decision_r1: changes_requested
reviewed_head_r2: 9b82e97b8aadc5b6b8710e03b5128a608697f56e
dsh_decision_r2: changes_requested
reviewed_head_r3: 5fa8a41f1fbda56dd88fb3a87e1604fd0a14a59e
dsh_decision_r3: approved_with_conditions
reviewed_head_r4: cc1bd7505f3fc48079db7ea2719040e77a8c58dd
dsh_decision_r4: changes_requested
reviewed_head_r5: 172eee84240e101186b12f1aa09e8a2f9ec92d68
dsh_decision_r5: changes_requested
created_at: 2026-10-09T17:05:00+08:00
---

# P02 Stage A 安全基底定向修订交付报告 (r6)

## 1. 修订概述

本交付响应非作者实现 Reviewer DeepSeek Harness 对 Stage A r5 交付（`reviewed_head=172eee84240e101186b12f1aa09e8a2f9ec92d68`）作出的 `changes_requested` 审查意见（`verification/P02/implementation-stage-a-r5-dsh-review.md`，P0/P1/P2/P3=`0/0/2/4`，开放 6 项全部为 R5-01~R5-06）以及 Codex independent review 与 clean commit exact replay 证据。

在严格恪守 **Hard Build Barrier（硬构建屏障）** 的前提下，本轮修订在已冻结的 Owner 授权路径内彻底处置闭合了 R5-01 至 R5-06 全部 6 项 findings，澄清了历史 Review 编号与残余状态，加固了整个 Stage A 验证脚手架的确定性与证据可靠性。

## 2. 历史 Review 编号映射与残余澄清（R5-06）

为消除多轮 Review 过程中的编号语义混淆并如实反映各阶段闭合状态（所有历史快照原样保留，历史闭合项不重新开放）：

| 审查轮次 | 审查报告文件 | 报告决策 | 原始 Finding 编号 | 作者侧对应标签 | 闭合状态说明 |
|---|---|---|---|---|---|
| **DSH r1** | `doc/reviews/P02-972049f9-dsh-review.md` | `changes_requested` | F-01 ~ F-12 | F-01 ~ F-12 | 全部闭合于 r2/r3 |
| **DSH r2** | `doc/reviews/P02-9b82e97b-dsh-r2-review.md` | `changes_requested` | 复核 F-01~12 并新增 7 项 | G-01 ~ G-07 | 全部闭合于 r3/r4 |
| **DSH r3** | `doc/reviews/P02-5fa8a41f-dsh-r3-review.md` | `approved_with_conditions` | 10 项条件项（含 r2 残余） | H-01 ~ H-07（Codex 独立列为 C1~C5） | 全部闭合于 r4 |
| **DSH r4** | `verification/P02/implementation-stage-a-r4-dsh-review.md` | `changes_requested` | **R4-01 ~ R4-11** (P2: 3 项, P3: 8 项) | **R4-01 ~ R4-11** | R4-01..03, 05, 07..11 于 r5 闭合；R4-04 于 r5 为 partial 并升为 R5-01；R4-06 于 r5 为 partial 并升为 R5-03 |
| **DSH r5** | `verification/P02/implementation-stage-a-r5-dsh-review.md` | `changes_requested` | **R5-01 ~ R5-06** (P2: 2 项, P3: 4 项) | **R5-01 ~ R5-06** | **全部闭合于本轮 r6** |

## 3. DSH r5 Findings (R5-01 ~ R5-06) 逐项处置与证据对照表

| Finding 编号 | 级别 | 核心问题 | r6 修订处置与证据 | 状态 |
|---|---|---|---|---|
| **R5-01** | **P2** | PRE-02 新鲜度失败重试时，若子进程未覆写报告崩溃，重读会用旧报告 exit 覆盖真实 `returncode`；PASS 谓词未含 `report_is_fresh` | 1. PRE-02 解耦子进程实际返回码 `observed_proc_exit` 与报告字段 `report_exit`，绝不相互覆盖；<br>2. 重新执行子探针前，先显式 `unlink()` 磁盘旧报告，防止崩溃后误读残留工件；<br>3. 子进程非零退出时立即 fail-closed，记录真实退出码与 stdout/stderr；<br>4. PASS 谓词严格要求：`report_is_fresh and observed_proc_exit == 0 and report_exit == 0 and srep.overall_status == "PASS"`；<br>5. 增加自检函数 `self_test_pre02_retry_failure`，实测旧有效报告 + 模拟子进程返回 42 时判定为 FAIL 且退出码为 42。 | **closed** |
| **R5-02** | **P2** | `--finalize` 非零（未抛异常）时，日志已定稿宣称成功且不再写入，失败运行永久假报成功；header `Status: IN_PROGRESS` 未被终结 | 1. 调整日志时序：runner 不在 `--finalize` 前写入成功声明；<br>2. 由 `--finalize` 在定稿哈希计算前向日志写入定稿结论与 `Status: COMPLETED (EXIT=0)`，哈希精确覆盖该定稿字节，消除时序矛盾；<br>3. runner 严密监听 finalizer 退出码，若非零（实测 `-FinalizeFailTest` 退出 42），追加记录 `[FAILURE] ... Finalizer failed with exit code $finExit` 与 `Status: FAILED (EXIT=$finExit)` 并强制落盘；<br>4. 成功路径由两阶段定稿确保 5/5 工件哈希 100% 精确匹配磁盘字节。 | **closed** |
| **R5-03** | P3 | 异常路径未持久化子进程完整 stdout/stderr（Message 仅首行）；`$LASTEXITCODE` 可能取到陈旧值；无 StackTrace；微探针无归档证据 | 1. `run-webview.ps1` catch 块完整持久化失败步骤名、命令、参数、异常类型、全量异常信息、子进程完整多行输出（如 Node require stack 全量 20+ 行诊断，不截断）、脚本堆栈（StackTrace）；<br>2. 仅在步骤执行过原生命令时记录真实子退出码，否则显式记录 `null (exception aborted execution...)`，杜绝复用前一命令遗留的 `$LASTEXITCODE`；<br>3. 在 Windows 11 / PowerShell 5.1 环境下执行故障注入与异常微探针，将完整命令、输出与退出码归档于持久证据文件 [`verification/P02/microprobes/ps51-exception-handling.log`](../../verification/P02/microprobes/ps51-exception-handling.log)。 | **closed** |
| **R5-04** | P3 | 缺失 `tsc` 时仅 Warning 并走通 exit 0 (fail-open)；候选 2 硬编码机器绝对路径；无机器可读 TS 检查门 | 1. 消除硬编码 `G:\CODEX\New Manga` 路径，动态从当前工作区或 `git rev-parse --git-common-dir` 上溯解析主仓库 `apps/desktop/frontend/node_modules/typescript/bin/tsc`；<br>2. 采取 fail-closed 策略：若找不到编译器，记录显式 `[FAILURE] ... (fail-closed per R5-04)`，置 `Status: FAILED (EXIT=1)` 并以退出码 1 中断；<br>3. 在 [`verification/P02/p02-harness-results.json`](../../verification/P02/p02-harness-results.json) 的 `provenance` 中增加 `typescript_contract_gate` 结构化机器证据。 | **closed** |
| **R5-05** | P3 | PRE-03 顶层 `status` 恒为 `"PASS"`，不受单项 token/live/alpha FAIL 影响，`all_passed` 亦未置假 | 1. PRE-03 顶层 `status` 与退出码严格由所有 token、live inline palette 以及 alpha pill 样例对比度结果聚合派生；<br>2. 只要有任何一项低于 WCAG 阈值，顶层判定置为 `FAIL` (exit 1)，且 `all_passed = False`；<br>3. 增加自检函数 `self_test_pre03_failure_propagation`，断言任何单项失败必然传播至顶层 FAIL。 | **closed** |
| **R5-06** | P3 | Handoff/Task/RESUME 历史编号与残余状态过度闭合（R4-04 与 R4-06 仅 partial 却声称彻底 closed） | 1. 更新文档精确标注：R4-04 与 R4-06 在 r5 为 partial 并在本轮 r6 作为 R5-01 与 R5-03 彻底闭合；<br>2. 区分早期微探针声明与本次归档的持久证据文件；<br>3. 保持所有历史报告与快照原貌，杜绝过度声明。 | **closed** |

## 4. 验收场景执行结果（单一事实源）

以机器生成的 [`verification/P02/p02-harness-results.json`](../../verification/P02/p02-harness-results.json) 记录为准：

| 场景标识 | 场景名称 | 判定 | 执行层 | 退出码 | 关键记录 / 阻断原因 |
|---|---|---|---|---|---|
| `PRE-01` | 合成 Fixture 契约完整性 | **PASS** | `FILESYSTEM` | 0 | 全量遍历 1 book, 2 chapters, 4 pages, 3 regions, 3 revisions；fail-closed 派生权威枚举闭集（含 manual/imported/restored）；4/4 组 mutation 拒绝自检全部执行并通过；验证 relabel 转移与 normalized geometry |
| `PRE-02` | 静态源码契约控制检查 | **PASS** | `STATIC_AST` | 0 | 新鲜度严格绑定当前 HEAD/tree 与关键输入哈希；子进程退出码与报告解耦，stale 重试先 unlink；PASS 谓词严格要求 fresh + proc_exit=0 + report_exit=0 + status=PASS；自检验证子进程非零重试失败隔离 |
| `PRE-03` | 视觉 F Token / 内联色数学模型 | **PASS** | `TOKEN_MODEL` | 0 | 全量聚合 token、live palette 与 alpha evaluations；方向 F Token 真实计算：`ink` 14.72:1 (>=4.5), `ink-2` 7.45:1 (>=4.5), `ink-3` 5.57:1 (>=4.5), `ink-dis` 3.55:1 (>=3.0), `accent` 3.53:1 (>=3.0)；Live 内联正文 `#d8e0e8` 13.87:1 (>=4.5), `#8a94a2` 6.02:1 (>=4.5)；Pill 背景合成 `#7eb287` 5.83:1 (>=4.5), `#fbbf24` 7.97:1 (>=4.5)；普通文本一律 >=4.5:1；边框与容器背景 `NOT_VERIFIABLE`；自检验证失败传播 |
| `AC1` | 真实 WebView2 启动与证明 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | **Hard Build Barrier 生效**：tauri_build 写入源码树且缺少受信 sidecar 输入，等待 Codex 登记 scratch worktree |
| `AC2` | Workbench 导航与真实输入 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |
| `AC3` | 300ms 静默期与页面失效窗口 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |
| `AC4` | 写后刷新即时性 (retype/undo/restore) | **BLOCKED** | `REAL_WEBVIEW_MOCK_IPC` | `null` | 依 Task 契约严禁以 NOT_RUN 替代，如实标记为 BLOCKED |
| `AC5` | 键盘操作与焦点链 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |
| `AC6` | 真实运行时 Computed Color 提取 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |

**总计 9 项场景**：**PASS: 3 项，BLOCKED: 6 项，FAIL: 0 项，NOT_RUN: 0 项**。

### 两阶段定稿工件哈希核验（5/5 匹配）

在完整运行后，`p02-harness-results.json` 记录的 5 项工件 SHA-256 与磁盘字节 100% 精确一致：
1. `verification/P02/env-identity-report.json`: `4cfc44e4b8a6658ac5899cba280fff8e689978a8916d99afc0a4a54a851ef7f6` (MATCH)
2. `verification/P02/static-control-report.json`: `7f5adc19258cb4a63af5fc08612a772901f68b1a5e74fc0eb63a72a3bf759988` (MATCH)
3. `verification/P02/p02-harness-results.txt`: `58959776d3b918092412db9bcbdd5080e6c4b01e6bfa9d4866be8819b0d5125e` (MATCH)
4. `verification/P02/probe-execution-probeonly.log`: `733af6a91bbc4b6cfc260dd8dfff38312dc079765fd8484968717e856f95709a` (MATCH)
5. `verification/P02/probe-execution-full.log`: `c768acc78b0e7d88b24ac1ba81ab91c833800db92c5772b0acf46874ad6f6441` (MATCH)

## 5. 交付文件清单

- [`apps/desktop/frontend/e2e/workbench_driver_protocol.ts`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/apps/desktop/frontend/e2e/workbench_driver_protocol.ts)
- [`verification/P02/fixtures/workbench_synthetic_data.json`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/fixtures/workbench_synthetic_data.json)
- [`verification/P02/harness/workbench_cdp_harness.py`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/harness/workbench_cdp_harness.py)
- [`verification/P02/probes/env_identity_probe.py`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/probes/env_identity_probe.py)
- [`verification/P02/probes/static_control_probe.py`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/probes/static_control_probe.py)
- [`verification/P02/run-webview.ps1`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/run-webview.ps1)
- [`verification/P02/probe-execution-probeonly.log`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/probe-execution-probeonly.log)
- [`verification/P02/probe-execution-full.log`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/probe-execution-full.log)
- [`verification/P02/probe-execution.log`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/probe-execution.log)
- [`verification/P02/env-identity-report.json`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/env-identity-report.json) / [`env-identity-report.txt`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/env-identity-report.txt)
- [`verification/P02/static-control-report.json`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/static-control-report.json) / [`static-control-report.txt`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/static-control-report.txt)
- [`verification/P02/p02-harness-results.json`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/p02-harness-results.json) / [`p02-harness-results.txt`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/p02-harness-results.txt)
- [`verification/P02/microprobes/ps51-exception-handling.log`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/microprobes/ps51-exception-handling.log)
- [`verification/P02/RESUME.md`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/RESUME.md)
- [`doc/tasks/P02.md`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/doc/tasks/P02.md)
- [`doc/handoffs/P02-stage-a-foundation-handoff.md`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/doc/handoffs/P02-stage-a-foundation-handoff.md)

所有变更严格位于 Owner 允许路径内，未修改任何生产源码、依赖或共享契约。

## 6. 推荐下一步

提交固定交付 commit，由 Codex 在 clean detached exact head 独立复跑 Stage A probes 并完成 Gate 复算与 `git diff --check` 证据归档；交由 DeepSeek Harness 进行 Stage A r6 复审。待隔离 scratch worktree 构建方案获批后，再推进 Stage B 真实 WebView2 运行时验证。
