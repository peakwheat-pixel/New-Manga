---
task_id: P02
title: 真实 Workbench WebView 行为、300ms 刷新与对比度验证 (Stage A 定向修订 Handoff r5)
status: in_progress
stage: STAGE_A_SAFE_FOUNDATION_R5
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
created_at: 2026-10-09T16:30:00+08:00
---

# P02 Stage A 安全基底定向修订交付报告 (r5)

## 1. 修订概述

本交付响应非作者实现 Reviewer DeepSeek Harness 对 Stage A r4 交付（`reviewed_head=cc1bd7505f3fc48079db7ea2719040e77a8c58dd`）作出的 `changes_requested` 审查意见（`verification/P02/implementation-stage-a-r4-dsh-review.md`，P0/P1/P2/P3=`0/0/3/8`，开放 11 项全部为 R4-01~R4-11）以及 Codex independent review 与 clean commit replay 证据。

在严格恪守 **Hard Build Barrier（硬构建屏障）** 的前提下，本轮修订在已冻结的 Owner 授权路径内彻底闭合了 R4-01 至 R4-11 全部 11 项 findings，并澄清历史 Review 编号映射，加固了整个 Stage A 验证脚手架。

## 2. 历史 Review 编号映射说明

为消除多轮 Review 过程中的编号语义混淆，特此说明历史各阶段 Review 报告归属与作者侧追踪标签的对应关系（所有历史快照原样保留，历史闭合项不重新开放）：

| 审查轮次 | 审查报告文件 | 报告决策 | 原始 Finding 编号 | 作者侧对应标签 | 当前状态 |
|---|---|---|---|---|---|
| **DSH r1** | `doc/reviews/P02-972049f9-dsh-review.md` | `changes_requested` | F-01 ~ F-12 | F-01 ~ F-12 | 全部闭合于 r2/r3 |
| **DSH r2** | `doc/reviews/P02-9b82e97b-dsh-r2-review.md` | `changes_requested` | 复核 F-01~12 并新增 7 项 | G-01 ~ G-07 | 全部闭合于 r3/r4 |
| **DSH r3** | `doc/reviews/P02-5fa8a41f-dsh-r3-review.md` | `approved_with_conditions` | 10 项条件项（含 r2 残余） | H-01 ~ H-07（Codex 独立列为 C1~C5） | 全部闭合于 r4 |
| **DSH r4** | `verification/P02/implementation-stage-a-r4-dsh-review.md` | `changes_requested` | **R4-01 ~ R4-11** (P2: 3 项, P3: 8 项) | **R4-01 ~ R4-11** | **全部闭合于本轮 r5** |

## 3. DSH r4 Findings (R4-01 ~ R4-11) 逐项处置与证据对照表

| Finding 编号 | 级别 | 核心问题 | r5 修订处置与证据 | 状态 |
|---|---|---|---|---|
| **R4-01** | P2 | TS2556 元组推断错误；E2E 文件未纳入常规构建检查 | `apps/desktop/frontend/e2e/workbench_driver_protocol.ts` 第 162 行显式指定 `const effectiveFg: [number, number, number]` 元组类型，彻底消除 `TS2556`；在 `run-webview.ps1` 中集成可运行的 focused TypeScript 类型检查（`node .../tsc ...`），实测运行通过 (EXIT=0)。 | **closed** |
| **R4-02** | P2 | `sfx_policy`/`origin` 白名单与源码闭集定义不符（接受非法 `ignore`/`legacy`，拒绝合法 `manual`/`imported`/`restored`） | 重构为严格依据 `apps/desktop/frontend/src/region/types.ts:33,37` 闭集进行校验；合法枚举支持 `manual`、`imported`、`restored`，非法枚举（`ignore`、`legacy`）坚决拒绝。 | **closed** |
| **R4-03** | P2 | `artifact_hashes` 时序矛盾（运行中提前哈希未定稿日志/TXT）；自引用死结 | 实施两阶段 Finalization（Two-Phase Artifact Finalization）：在 runner 将完整运行日志定稿落盘（含 `EXIT=0`）后，通过 `--finalize` 独立步骤计算生成工件的真实字节 SHA-256 并更新 `p02-harness-results.json`；杜绝未落盘提前哈希，不将结果文件哈希记录于自身，实测 5 项工件 SHA-256 与磁盘字节 100% 精确一致。 | **closed** |
| **R4-04** | P3 | 探针新鲜度仅比对 HEAD/tree，同 HEAD 下 dirty 输入可能误用旧 PASS；缺失 `exit_code` 时被合成为推测值 | 探针报告新鲜度不仅校验 HEAD 与 tree，还严格比对 `probe_inputs_sha256`（杜绝同 HEAD 下 dirty 文件误用旧 PASS）；缺失 `exit_code` 时保持 `None` 并判定为未验证，不进行状态猜测合成。 | **closed** |
| **R4-05** | P3 | PRE-02 自检未走真实读取/消费路径；`report_freshness_verified` 恒为字面量常量 `True` | 提取独立的 `evaluate_static_probe_report` 评估函数，自检真实调用该函数覆盖 stale head、dirty input mismatch、missing exit_code、malformed 等失效场景；`report_freshness_verified` 根据真实观察结果动态计算。 | **closed** |
| **R4-06** | P3 | PowerShell 异常路径未记录失败命令/输出/子进程 EXIT | `run-webview.ps1` 维护当前步骤名、命令、参数，在 catch 块中完整记录失败步骤、命令、参数、异常类型与详细 Message/StackTrace，显式调用 `Flush-Log` 后再退出；在 Windows PowerShell 5.1 环境下实测微探针验证通过。 | **closed** |
| **R4-07** | P3 | 权威枚举解析失败时静默回退硬编码值 | `load_authoritative_enums()` 采取 fail-closed 策略；若源文件缺失或正则解析失败直接抛出异常中断，绝不静默回退硬编码值。 | **closed** |
| **R4-08** | P3 | Mutation 自检存在条件守卫，报告无条件声称 4 组均被拒绝 | `self_test_pre01_mutations` 精准统计执行、拒绝与跳过组数；仅当 4 组均执行且拒绝且无跳过时才报告 4/4 拒绝；实测 `4/4 executed and rejected (skipped: 0)`。 | **closed** |
| **R4-09** | P3 | 协议层给 `large_text` 设了 3.0:1 阈值，给文本放水 | 协议层 `workbench_driver_protocol.ts` 与夹具 `workbench_synthetic_data.json` 中统一 `large_text` 阈值为严格的 `>= 4.5:1`，坚决杜绝给文本放宽至 3.0:1。 | **closed** |
| **R4-10** | P3 | pre-`try` 故障或强行中断时旧 PASS 日志留存 | `run-webview.ps1` 启动时立即向磁盘写入头并截断日志，标记 `Status: IN_PROGRESS`，杜绝任何 pre-`try` 异常或中断导致残留旧 PASS 日志。 | **closed** |
| **R4-11** | P3 | `page_count` 强制整数与契约允许 `null` 不符；geometry 缺少数值范围与 polygon 结构校验 | `validate_fixtures_data` 允许 `page_count` 为 `null`（符合 `library/types.ts:23`）；geometry 增加 `bbox` 4 个 0..1 数值范围及 `polygon` 点结构严密校验。 | **closed** |

## 4. 验收场景执行结果（单一事实源）

以机器生成的 [`verification/P02/p02-harness-results.json`](../../verification/P02/p02-harness-results.json) 记录为准：

| 场景标识 | 场景名称 | 判定 | 执行层 | 退出码 | 关键记录 / 阻断原因 |
|---|---|---|---|---|---|
| `PRE-01` | 合成 Fixture 契约完整性 | **PASS** | `FILESYSTEM` | 0 | 全量遍历 1 book, 2 chapters, 4 pages, 3 regions, 3 revisions；fail-closed 派生权威枚举闭集（含 manual/imported/restored）；4/4 组 mutation 拒绝自检全部执行并通过；验证 relabel 转移与 normalized geometry |
| `PRE-02` | 静态源码契约控制检查 | **PASS** | `STATIC_AST` | 0 | 新鲜度严格绑定当前 HEAD/tree 与关键输入哈希；`resolveDebounceMs=300`, `regionDebounceMs=300`, 导航测试 ID 符合契约；真实退出码 0，freshness verified 真实计算 |
| `PRE-03` | 视觉 F Token / 内联色数学模型 | **PASS** | `TOKEN_MODEL` | 0 | 方向 F Token 真实计算：`ink` 14.72:1 (>=4.5), `ink-2` 7.45:1 (>=4.5), `ink-3` 5.57:1 (>=4.5), `ink-dis` 3.55:1 (>=3.0), `accent` 3.53:1 (>=3.0)；Live 内联正文 `#d8e0e8` 13.87:1 (>=4.5), `#8a94a2` 6.02:1 (>=4.5)；Pill 背景合成 `#7eb287` 5.83:1 (>=4.5), `#fbbf24` 7.97:1 (>=4.5)；普通文本一律 >=4.5:1；边框与容器背景 `NOT_VERIFIABLE` |
| `AC1` | 真实 WebView2 启动与证明 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | **Hard Build Barrier 生效**：tauri_build 写入源码树且缺少受信 sidecar 输入，等待 Codex 登记 scratch worktree |
| `AC2` | Workbench 导航与真实输入 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |
| `AC3` | 300ms 静默期与页面失效窗口 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |
| `AC4` | 写后刷新即时性 (retype/undo/restore) | **BLOCKED** | `REAL_WEBVIEW_MOCK_IPC` | `null` | 依 Task 契约严禁以 NOT_RUN 替代，如实标记为 BLOCKED |
| `AC5` | 键盘操作与焦点链 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |
| `AC6` | 真实运行时 Computed Color 提取 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |

**总计 9 项场景**：**PASS: 3 项，BLOCKED: 6 项，FAIL: 0 项，NOT_RUN: 0 项**。

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
- [`verification/P02/RESUME.md`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/verification/P02/RESUME.md)
- [`doc/tasks/P02.md`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/doc/tasks/P02.md)
- [`doc/handoffs/P02-stage-a-foundation-handoff.md`](file:///G:/CODEX/New%20Manga.worktrees/P02-real-webview-harness-antigravity/doc/handoffs/P02-stage-a-foundation-handoff.md)

所有变更严格位于 Owner 允许路径内，未修改任何生产源码、依赖或共享契约。

## 6. 推荐下一步

提交固定交付 commit，由 Codex 在 clean detached exact head 独立复跑 Stage A probes 并完成 Gate 复算与 `git diff --check` 证据归档；交由 DeepSeek Harness 进行 Stage A r5 复审。待隔离 scratch worktree 构建方案获批后，再推进 Stage B 真实 WebView2 运行时验证。
