---
task_id: P02
title: 真实 Workbench WebView 行为、300ms 刷新与对比度验证 (Stage A 定向修订 Handoff r7)
status: in_progress
stage: STAGE_A_SAFE_FOUNDATION_R7
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
reviewed_head_r6: 38672473f93971a4681aef682e5635e64b0bd896
dsh_decision_r6: approved_with_conditions
created_at: 2026-10-09T17:30:00+08:00
---

# P02 Stage A 安全基底定向修订交付报告 (r7)

## 1. 修订概述

本交付响应非作者实现 Reviewer DeepSeek Harness 对 Stage A r6 交付（`reviewed_head=38672473f93971a4681aef682e5635e64b0bd896`）作出的 `approved_with_conditions` 审查意见（`verification/P02/implementation-stage-a-r6-dsh-review.md`，P0/P1/P2/P3=`0/0/0/4`，开放 4 项条件项 R6-01~R6-04；早期 R5-01~R5-06 全部 closed）以及 Codex exact replay（`r6-codex-exact-head-review.md`，5/5 工件哈希匹配）证据。

在严格恪守 **Hard Build Barrier（硬构建屏障）** 的前提下，本轮修订在已冻结的 Owner 授权路径内彻底处置闭合了 R6-01 至 R6-04 全部 4 项条件项，加固了整个 Stage A 验证脚手架的跨目录解析鲁棒性、机器门判定真实性与自检覆盖真实生产路径的严密性。

## 2. 历史 Review 编号映射与残余澄清（R5-06, R6-01~04）

为消除多轮 Review 过程中的编号语义混淆并如实反映各阶段闭合状态（所有历史快照原样保留，历史闭合项不重新开放）：

| 审查轮次 | 审查报告文件 | 报告决策 | 原始 Finding 编号 | 作者侧对应标签 | 闭合状态说明 |
|---|---|---|---|---|---|
| **DSH r1** | `doc/reviews/P02-972049f9-dsh-review.md` | `changes_requested` | F-01 ~ F-12 | F-01 ~ F-12 | 全部闭合于 r2/r3 |
| **DSH r2** | `doc/reviews/P02-9b82e97b-dsh-r2-review.md` | `changes_requested` | 复核 F-01~12 并新增 7 项 | G-01 ~ G-07 | 全部闭合于 r3/r4 |
| **DSH r3** | `doc/reviews/P02-5fa8a41f-dsh-r3-review.md` | `approved_with_conditions` | 10 项条件项（含 r2 残余） | H-01 ~ H-07（Codex 独立列为 C1~C5） | 全部闭合于 r4 |
| **DSH r4** | `verification/P02/implementation-stage-a-r4-dsh-review.md` | `changes_requested` | **R4-01 ~ R4-11** (P2: 3 项, P3: 8 项) | **R4-01 ~ R4-11** | R4-01..03, 05, 07..11 于 r5 闭合；R4-04 与 R4-06 于 r6 彻底闭合 |
| **DSH r5** | `verification/P02/implementation-stage-a-r5-dsh-review.md` | `changes_requested` | **R5-01 ~ R5-06** (P2: 2 项, P3: 4 项) | **R5-01 ~ R5-06** | 全部闭合于 r6 |
| **DSH r6** | `verification/P02/implementation-stage-a-r6-dsh-review.md` | `approved_with_conditions` | **R6-01 ~ R6-04** (全部 P3，4 项) | **R6-01 ~ R6-04** | **全部闭合于本轮 r7** |

## 3. DSH r6 条件项 (R6-01 ~ R6-04) 逐项处置与证据对照表

| Finding 编号 | 级别 | 核心问题 | r7 修订处置与证据 | 状态 |
|---|---|---|---|---|
| **R6-01** | P3 | `run-webview.ps1` 中的 `git rev-parse --git-common-dir` 未带 `-C $RepoRoot`，导致从仓库外以绝对路径调用时解析到错误 common root，误报缺少编译器并退出 1 | 1. `run-webview.ps1` 改为 `git -C $RepoRoot rev-parse --git-common-dir`，与 Python 侧 `cwd=REPO_ROOT` 逻辑完全对齐；<br>2. 实测在外部目录（如 `C:\Users\49745`）以绝对路径调用 `run-webview.ps1 -ProbeOnly`，精准解析 Git common root 下的 `tsc` 并顺利通过（EXIT=0），彻底杜绝误报缺失编译器。 | **closed** |
| **R6-02** | P3 | `typescript_contract_gate.gate_status` 仅表示编译器存在，不表示已运行；harness 独立执行时不运行 TS 却报告 PASS，且未入总退出码 | 1. `run-webview.ps1` 在 Step 4 将 Step 2 实际观察到的 `tsc` 退出码通过 `--tsc-exit` 传入 harness；<br>2. `workbench_cdp_harness.py` 区分 `tsc_binary_resolution`（RESOLVED / NOT_FOUND）与实际 `execution_status`（PASS / FAIL / NOT_RUN）；<br>3. 若独立执行未传入退出码，机器门如实记录为 `NOT_RUN`（observed_exit_code: null）而绝不虚报 `PASS`；<br>4. 若传入非零退出码（如 1），harness 主程序严格退出 1，将 TS 门彻底纳入总退出码逻辑。 | **closed** |
| **R6-03** | P3 | `self_test_pre02_retry_failure` 与 `self_test_pre03_failure_propagation` 硬编码变量并复制布尔公式，未覆盖生产派发与聚合函数 | 1. 抽取生产 PRE-02 重试派发 helper `dispatch_and_evaluate_static_probe` 与生产 PRE-03 聚合 helper `aggregate_pre03_verdict`；<br>2. 生产 PRE-02 与 PRE-03 运行路径直接接入这两个 helper；<br>3. 重构自检函数，直接调用生产 helper，断言最终判决 verdict、exit code、报告未过时谓词、旧报告主动 unlink 清理与聚合布尔字典。 | **closed** |
| **R6-04** | P3 | `microprobes/ps51-exception-handling.log` 中的 Scenario C 为静态代码审查推断，未实际运行却标为 `Verdict: PASS` | 1. `run-webview.ps1` 增加 `-ExceptionTest` 参数；<br>2. 真实执行一次 Windows PowerShell 5.1 未捕获异常并拦截捕获（退出 1）；<br>3. 将真实执行命令、终端输出、完整 `[UNHANDLED_EXCEPTION]` 日志尾（Failed Step/Command、Exception Type/Message、Captured Process Output: UNAVAILABLE、StackTrace、Observed Child ExitCode: null）与静态代码结构审查一并归档至 `verification/P02/microprobes/ps51-exception-handling.log`，形成实测执行与静态结构双重闭环证据。 | **closed** |

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
1. `verification/P02/env-identity-report.json`: `2ad5bc8549a84d6d9bdd430b72dbd1de673a981074c78a5781781e2735de02f9` (MATCH)
2. `verification/P02/static-control-report.json`: `de7878612e175f989487e92512d00a2945554279e858e9fd48b6deaa9b8063a3` (MATCH)
3. `verification/P02/p02-harness-results.txt`: `de2ebd60ae5f6b5767c550fd7f0411014982954fa035f88fea8595e7824e94ea` (MATCH)
4. `verification/P02/probe-execution-probeonly.log`: `2bdcda3c084af7901b07eabc0f0a69b1915a374ec6f2278b4534afb2511c8e54` (MATCH)
5. `verification/P02/probe-execution-full.log`: `94c4cebc25e58d1c0c5980ef63231ff79dbd804f3ee9e19b8423f9371e90a1cf` (MATCH)

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

提交固定交付 commit，由 Codex 在 clean detached exact head 独立复跑 Stage A probes 并完成 Gate 复算与 `git diff --check` 证据归档；交由 DeepSeek Harness 进行 Stage A r7 复审。待隔离 scratch worktree 构建方案获批后，再推进 Stage B 真实 WebView2 运行时验证。
