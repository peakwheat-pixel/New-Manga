---
task_id: P02
title: 真实 Workbench WebView 行为、300ms 刷新与对比度验证 (Stage A 定向修订 Handoff r8)
status: in_progress
stage: STAGE_A_SAFE_FOUNDATION_R8
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
reviewed_head_r7: 38959ba99b84f771aba7010b53b9b47ecdc75488
reviewed_head_r8: 89413f45a601966eb40d7af7abea65cbdfc754b3
dsh_decision_r8: approved
integration_commit: 89413f45a601966eb40d7af7abea65cbdfc754b3
dsh_decision_r7: approved_with_conditions
created_at: 2026-10-09T17:58:00+08:00
---

# P02 Stage A 安全基底定向修订交付报告 (r8)

## 1. 修订概述

本交付响应非作者实现 Reviewer DeepSeek Harness 对 Stage A r7 交付（`reviewed_head=38959ba99b84f771aba7010b53b9b47ecdc75488`）作出的 `approved_with_conditions` 审查意见（`verification/P02/implementation-stage-a-r7-dsh-review.stdout.md`，P0/P1/P2/P3=`0/0/0/2`，开放 2 项 P3 条件项 R7-01、R7-02；前序 R6-01~R6-04 全部 closed）以及 Codex exact replay（`r7-codex-exact-head-review.md`，5/5 工件哈希匹配）证据。

在严格恪守 **Hard Build Barrier（硬构建屏障）** 的前提下，本轮修订在已冻结的 Owner 授权路径内彻底处置闭合了 R7-01，并对 DSH 明确允许延期的 R7-02 进行了显式债务登记（Deferred P3），使仓库内的测试套件建立了对 PRE-03 生产 verdict 记录及顶层退出判决的持久自足回归守卫。

## 2. 历史 Review 编号映射与残余澄清

为消除多轮 Review 过程中的编号语义混淆并如实反映各阶段闭合状态（所有历史快照原样保留，历史闭合项不重新开放）：

| 审查轮次 | 审查报告文件 | 报告决策 | 原始 Finding 编号 | 作者侧对应标签 | 闭合状态说明 |
|---|---|---|---|---|---|
| **DSH r1** | `doc/reviews/P02-972049f9-dsh-review.md` | `changes_requested` | F-01 ~ F-12 | F-01 ~ F-12 | 全部闭合于 r2/r3 |
| **DSH r2** | `doc/reviews/P02-9b82e97b-dsh-r2-review.md` | `changes_requested` | 复核 F-01~12 并新增 7 项 | G-01 ~ G-07 | 全部闭合于 r3/r4 |
| **DSH r3** | `doc/reviews/P02-5fa8a41f-dsh-r3-review.md` | `approved_with_conditions` | 10 项条件项（含 r2 残余） | H-01 ~ H-07（Codex 独立列为 C1~C5） | 全部闭合于 r4 |
| **DSH r4** | `verification/P02/implementation-stage-a-r4-dsh-review.md` | `changes_requested` | **R4-01 ~ R4-11** (P2: 3 项, P3: 8 项) | **R4-01 ~ R4-11** | R4-01..03, 05, 07..11 于 r5 闭合；R4-04 与 R4-06 于 r6 彻底闭合 |
| **DSH r5** | `verification/P02/implementation-stage-a-r5-dsh-review.md` | `changes_requested` | **R5-01 ~ R5-06** (P2: 2 项, P3: 4 项) | **R5-01 ~ R5-06** | 全部闭合于 r6 |
| **DSH r6** | `verification/P02/implementation-stage-a-r6-dsh-review.md` | `approved_with_conditions` | **R6-01 ~ R6-04** (全部 P3，4 项) | **R6-01 ~ R6-04** | 全部闭合于 r7 |
| **DSH r7** | `verification/P02/implementation-stage-a-r7-dsh-review.stdout.md` | `approved_with_conditions` | **R7-01, R7-02** (全部 P3，2 项) | **R7-01, R7-02** | **R7-01 闭合于本轮 r8；R7-02 显式延期 (Deferred P3)** |

## 3. DSH r7 条件项 (R7-01, R7-02) 逐项处置与证据对照表

| Finding 编号 | 级别 | 核心问题 | r8 修订处置与证据 | 状态 |
|---|---|---|---|---|
| **R7-01** | P3 | `self_test_pre03_failure_propagation()` 仅断言布尔字典 `aggregate_pre03_verdict()`，不断言被记录的 verdict（status/exit_code）与 `main()` 顶层返回值；仓库内缺少自足的回归防线 | 1. 抽取生产 PRE-03 结构构建与判定 helper `build_pre03_verdict`，返回 `(pre03_pass, verdict_dict)`，权威派生 `status: PASS/FAIL` 与 `exit_code: 0/1`；<br>2. 抽取生产顶层退出决策 pure helper `compute_harness_exit_code(preflight_ok, tsc_gate_status)`，统一由 `main()` 消费；<br>3. 在 `WorkbenchHarness` 类上增加生产记录方法 `record_pre03_evaluation`，由 `run_preflight_checks` 直接消费；<br>4. 重构 `self_test_pre03_failure_propagation`：断言生产 `build_pre03_verdict` 在注入低对比度时生成 `status=="FAIL"` 与 `exit_code==1`，验证 `record_pre03_evaluation` 在 Harness 实例上追加 FAIL verdict 且 `compute_harness_exit_code` 返回 1；在全绿场景断言 PASS 与 0，构建自足回归守卫。 | **closed** |
| **R7-02** | P3 | runner 若在 Step 2/3 失败则提前退出，磁盘上保留上一轮的 `FINALIZED` JSON 报告，在 HEAD 相同的本地迭代中可能产生混淆 | 依据 DSH 裁决与授权范围，本轮**明确延期为记录的技术债务（Deferred P3）**，不在本轮改动 runner 行为。<br>**触发条件**：运行在 Step 2 (tsc) 或 Step 3 (static probe) 失败中断，未到达 Step 4/5。<br>**延期原因**：避免在未经独立架构设计的情况下扩大 runner 状态机。<br>**后续方案**：可在 runner 启动阶段重置既有报告为 `SUPERSEDED` 或在报告与日志中注入统一 `run_id`。 | **deferred (P3)** |

## 4. 验收场景执行结果（单一事实源）

以机器生成的 [`verification/P02/p02-harness-results.json`](../../verification/P02/p02-harness-results.json) 记录为准：

| 场景标识 | 场景名称 | 判定 | 执行层 | 退出码 | 关键记录 / 阻断原因 |
|---|---|---|---|---|---|
| `PRE-01` | 合成 Fixture 契约完整性 | **PASS** | `FILESYSTEM` | 0 | 全量遍历 1 book, 2 chapters, 4 pages, 3 regions, 3 revisions；fail-closed 派生权威枚举闭集（含 manual/imported/restored）；4/4 组 mutation 拒绝自检全部执行并通过；验证 relabel 转移与 normalized geometry |
| `PRE-02` | 静态源码契约控制检查 | **PASS** | `STATIC_AST` | 0 | 新鲜度严格绑定当前 HEAD/tree 与关键输入哈希；子进程退出码与报告解耦，stale 重试先 unlink；PASS 谓词严格要求 fresh + proc_exit=0 + report_exit=0 + status=PASS；自检验证子进程非零重试失败隔离 |
| `PRE-03` | 视觉 F Token / 内联色数学模型 | **PASS** | `TOKEN_MODEL` | 0 | 全量聚合 token、live palette 与 alpha evaluations；方向 F Token 真实计算：`ink` 14.72:1 (>=4.5), `ink-2` 7.45:1 (>=4.5), `ink-3` 5.57:1 (>=4.5), `ink-dis` 3.55:1 (>=3.0), `accent` 3.53:1 (>=3.0)；Live 内联正文 `#d8e0e8` 13.87:1 (>=4.5), `#8a94a2` 6.02:1 (>=4.5)；Pill 背景合成 `#7eb287` 5.83:1 (>=4.5), `#fbbf24` 7.97:1 (>=4.5)；普通文本一律 >=4.5:1；边框与容器背景 `NOT_VERIFIABLE`；自检全面验证生产 verdict 与退出码传播 |
| `AC1` | 真实 WebView2 启动与证明 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | **Hard Build Barrier 生效**：tauri_build 写入源码树且缺少受信 sidecar 输入，等待 Codex 登记 scratch worktree |
| `AC2` | Workbench 导航与真实输入 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |
| `AC3` | 300ms 静默期与页面失效窗口 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |
| `AC4` | 写后刷新即时性 (retype/undo/restore) | **BLOCKED** | `REAL_WEBVIEW_MOCK_IPC` | `null` | 依 Task 契约严禁以 NOT_RUN 替代，如实标记为 BLOCKED |
| `AC5` | 键盘操作与焦点链 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |
| `AC6` | 真实运行时 Computed Color 提取 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |

**总计 9 项场景**：**PASS: 3 项，BLOCKED: 6 项，FAIL: 0 项，NOT_RUN: 0 项**。

### 两阶段定稿工件哈希核验（5/5 匹配）

在完整运行后，`p02-harness-results.json` 记录的 5 项工件 SHA-256 与磁盘字节 100% 精确一致：
1. `verification/P02/env-identity-report.json`: `808765d40da9f73e713b2833f98da5aa63f5d26d4b5102148594dcc31d273207` (MATCH)
2. `verification/P02/static-control-report.json`: `ae9f56ec3ad8a86140028284e4ed1ac3737f0f82b835c6c79a58b922f37d3674` (MATCH)
3. `verification/P02/p02-harness-results.txt`: `9b58d273f2eff1a889aa427647bd9ffb6340348bf3bbd45644d502d0131bc7dc` (MATCH)
4. `verification/P02/probe-execution-probeonly.log`: `d850ac34b97a1a8ceb394b69d008469a595ba3e002454ba40116b99e15a4cbf8` (MATCH)
5. `verification/P02/probe-execution-full.log`: `e4fe95714713e25ef7f738cb79862fbe855f52c2e226c1b3727082dcb6c091df` (MATCH)

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

## 6. DSH r8 Review 与 Codex Stage A Integration Gate

DeepSeek Harness 已对固定 HEAD 89413f45a601966eb40d7af7abea65cbdfc754b3 / tree f1063c981b8f4164f51248f92b7825fc205dd07d / parent 38959ba99b84f771aba7010b53b9b47ecdc75488 完成非作者正式 Review，decision=approved（仅 Stage A），P0/P1/P2/P3=0/0/0/1、open=1。原文见 verification/P02/implementation-stage-a-r8-dsh-review.stdout.md；Codex exact-head 与 Integration Gate 见 verification/P02/r8-codex-exact-head-review.md 和 verification/P02/codex-integration-gate-r8.md。

R7-01 已闭合；R7-02 按 DSH 裁决为 deferred P3。新 finding R8-01 是非阻断 P3：record_verdict 与 build_pre03_verdict 当前字段一致但由两处构造，未来 schema 演化可能漂移；Codex 接受 DSH 建议将其延期到 verdict schema 下一次变更时，通过统一构造入口收敛。该处置不把 DSH 原报告的 open=1 改写为 0，也不需要单独复审。

Stage A integration_commit=89413f45a601966eb40d7af7abea65cbdfc754b3。Task 继续 in_progress / ACTIVE；AC1–AC6 仍 BLOCKED，Hard Build Barrier 生效。本次未运行任何 product build、Vitest、GUI 或真实 WebView。

## 7. 下一步建议

由 Codex 先把 P02 Stage B 的隔离 scratch-build 路径、Tauri build.rs 源码树副作用防护、sidecar 来源与 SHA-256、测试数据隔离及清理范围写入 Task-local 方案；交由独立 Reviewer 审查并通过 Gate 后，才决定是否执行构建。此处不授权在 Owner worktree 或任何含用户数据的路径构建。
