---
task_id: P02
title: 真实 Workbench WebView 行为、300ms 刷新与对比度验证 (Stage A 定向修订 Handoff r4)
status: in_progress
stage: STAGE_A_SAFE_FOUNDATION_R4
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
created_at: 2026-10-09T15:45:00+08:00
---

# P02 Stage A 安全基底定向修订交付报告 (r4)

## 1. 修订概述

本交付响应非作者实现 Reviewer DeepSeek Harness 对 Stage A r3 交付（`reviewed_head=5fa8a41f1fbda56dd88fb3a87e1604fd0a14a59e`）作出的 `approved_with_conditions` 审查意见（`doc/reviews/P02-5fa8a41f-dsh-r3-review.md`，P0/P1/P2/P3=`0/0/0/10`，开放 10 项全部为 P3，含 H-01~H-07 与 r2 残余）以及 Codex supplemental review 提出的 P2 blocker 与 exact-commit 独立复跑要求。

在严格恪守 **Hard Build Barrier（硬构建屏障）** 的前提下，本修订彻底完成了以下定向改进：
1. **统一 AC6 文本阈值**：所有普通文本一律提高至严格的 `>= 4.5:1`，仅 disabled 文本与非文本组件保留 `3.0:1`，保证 `min_required`、阈值配置与判定结果绝对一致；
2. **PRE-01 深度全量遍历与 Mutation 自检**：对 fixture 进行全量结构、类型、枚举、外键与场景遍历，动态从 `src/region/types.ts` 派生 `REGION_TYPE_VALUES`，并实装 4 组 mutation self-test 确保破坏性变异百分之百被拒绝；
3. **PRE-02 探针新鲜度严格绑定与真实 EXIT 传播**：严格校验报告绑定的 `source_head` 与 `source_tree`，陈旧/缺失时重新执行并记录真实观察到的退出码，子探针失败严格中断并传播；
4. **失败日志与退出码可靠落盘**：`run-webview.ps1` 采用 `try...catch...finally` 与统一 `Flush-Log`，确保无论步骤非零退出还是异常均先将失败命令、输出与 EXIT 落盘至纯 LF（无 BOM）日志，并通过本地微探针严格验证；
5. **逐次运行专属日志**：`-ProbeOnly` 输出专属 `probe-execution-probeonly.log`，完整运行输出专属 `probe-execution-full.log`，杜绝相互覆盖；
6. **F-05 Exact Provenance 完善**：补齐 `key_execution_inputs_sha256`（harness, probes, runner, fixture, protocol TS），如实标注 `is_clean_worktree`、`verification_mode: PRE_COMMIT_LOCAL_EVIDENCE` 与 `replay_status: PENDING_CODEX_EXACT_HEAD_REPLAY`，去除自身结果文件哈希引用；
7. **DSH Finding 编号映射与一致性细节修复**：修正边框值为真实来源 `#2a3038`，删除过度闭合断言；fixture 显式声明全局 SFX policy 前置配置；更新 `RegionOverlay.tsx:45-48` pill 背景文字配对；对齐 TS 契约接口字段至 snake_case emission。

## 2. DSH Findings 逐项处置与状态对照表

| Finding 编号 | 严重度 | 核心问题 | r4 修订处置与证据 | 状态 |
|---|---|---|---|---|
| **F-01..F-04** | P1/P2 | Stage A 定位、调色板来源、单一事实源、PRE-03/AC6 分离 | 已在 r2 修订中闭合，本轮保持不变。 | **closed** |
| **F-05** | P2 | 报告 provenance 绑定与避免自引用 | `p02-harness-results.json` 补齐 `key_execution_inputs_sha256`（6 项执行输入），如实记录 `is_clean_worktree`、`verification_mode: PRE_COMMIT_LOCAL_EVIDENCE` 与 `replay_status: PENDING_CODEX_EXACT_HEAD_REPLAY`，移除自身工件自引用；明确交付 commit 由 Codex 在 clean detached exact head 独立复跑核验。 | **closed (pending Codex exact replay)** |
| **F-06..F-12** | P2/P3 | 退出码 null、RESUME 检查点、Alpha 模型、GUID、wire 契约、TS layer、测试表分行 | 已在 r2/r3 修订中闭合，本轮保持不变。 | **closed** |
| **G-01** | P2 | 交付 Hash 过度闭合断言 | 已在 r3 消除自引用占位，本轮继续保持。 | **closed** |
| **G-02** | P3 | Git clean 与 porcelain 状态展示 | 已在 r3 实装，本轮继续在环境报告与 harness 中如实记录。 | **closed** |
| **G-03** | P3 | 纯 LF 换行与 diff-check 证据 | 本轮所有文件统一采用纯 LF，`run-webview.ps1` 采用 `New-Object System.Text.UTF8Encoding($false)` 生成无 BOM 日志；Codex 已在 r3 独立复跑中归档 `git diff --check` EXIT=0，本次继续保证通过。 | **closed** |
| **G-04** | P3 | Task 测试表拆分与运行证据独立化 | 将 `-ProbeOnly` 与完整运行的证据日志彻底拆分：`-ProbeOnly` 输出专属 [`probe-execution-probeonly.log`](../../verification/P02/probe-execution-probeonly.log)，完整运行输出专属 [`probe-execution-full.log`](../../verification/P02/probe-execution-full.log)，分别链接，杜绝相互覆盖。 | **closed** |
| **G-05** | P3 | 容器背景/边框判定与普通文本阈值 | 纯容器背景与边框（如 `#161b22`, `#2a3038`）维持 `NOT_VERIFIABLE`；所有普通文本（包括 secondary `ink_2`、tertiary `ink_3`、muted `#8a94a2`）统一提高要求至 `>= 4.5:1`，仅 disabled 与 non-text 保留 3.0:1。 | **closed** |
| **G-06** | P3 | 真实 alpha 合成与语义命名 | 进一步修正为 `RegionOverlay.tsx:45-48` pill 背景文字配对（`#7eb287` 与 `#fbbf24`），命名为 `pill_skip_background` 与 `pill_warn_background`，实测 5.83:1 与 7.97:1，全部通过 4.5:1。 | **closed** |
| **G-07** | P3 | `revisions[]` 10 个 RevisionSummary 字段完整性 | 已在 r3 补齐；r4 在 PRE-01 中增加全量遍历与 mutation 自检校验。 | **closed** |
| **H-01** | P3 | 编号映射一致性、边框 hex 修正与闭合声明口径 | 以 r2 原编号进行映射；修正边框色为真实的 `#2a3038`（`App.tsx:488`）；删除“彻底闭合”表述，如实陈述逐项状态与残余依赖（如等待 Codex exact replay）。 | **closed** |
| **H-02** | P3 | PRE-02 报告新鲜度绑定与实际 EXIT 记录 | 严格校验报告绑定的 `source_head` 与 `source_tree`，陈旧/缺失时重新执行并记录真实观察到的退出码，子探针失败严格中断并传播。 | **closed** |
| **H-03** | P3 | PRE-01 枚举权威派生与全量遍历 | 动态从 `src/region/types.ts` 派生 `REGION_TYPE_VALUES`；全量遍历验证所有 books, chapters, pages, regions, revisions；内置 4 组 mutation self-test；消费 `contrast_thresholds` 与 `expected_background_role`。 | **closed** |
| **H-04** | P3 | alpha 样例前景与角色命名对应 pill 背景 | alpha 样例前景与角色命名准确对应 `RegionOverlay.tsx:45-48` pill 背景与文字令牌（`#7eb287` 与 `#fbbf24`，分别实测 5.83:1 与 7.97:1，均通过 4.5:1 阈值）。 | **closed** |
| **H-05** | P3 | 依赖全局配置的期望值声明前提 | fixture 显式声明全局 SFX policy 前置配置前提 (`assumed_global_config`) 与 `sfx_policy_is_config_dependent: true`。 | **closed** |
| **H-06** | P3 | Task 交付记录中早期行状态自洽 | Task 交付记录中早期行明确标注为 `[历史快照]`。 | **closed** |
| **H-07** | P3 | TS 契约接口字段与 JSON emission 对齐 | `workbench_driver_protocol.ts` 的 `ScenarioVerdict` 接口字段名与 JSON emission 对齐为 snake_case，清理未使用的惰性字段。 | **closed** |

## 3. 验收场景执行结果（单一事实源）

以机器生成的 [`verification/P02/p02-harness-results.json`](../../verification/P02/p02-harness-results.json) 记录为准：

| 场景标识 | 场景名称 | 判定 | 执行层 | 退出码 | 关键记录 / 阻断原因 |
|---|---|---|---|---|---|
| `PRE-01` | 合成 Fixture 契约完整性 | **PASS** | `FILESYSTEM` | 0 | 全量遍历 1 book, 2 chapters, 4 pages, 3 regions, 3 revisions；派生权威枚举；4 项 mutation 拒绝自检全部通过；验证 relabel 转移 |
| `PRE-02` | 静态源码契约控制检查 | **PASS** | `STATIC_AST` | 0 | 新鲜度严格绑定当前 HEAD/tree；`resolveDebounceMs=300`, `regionDebounceMs=300`, 导航测试 ID 符合契约；真实退出码 0 |
| `PRE-03` | 视觉 F Token / 内联色数学模型 | **PASS** | `TOKEN_MODEL` | 0 | 方向 F Token 真实计算：`ink` 14.72:1 (>=4.5), `ink-2` 7.45:1 (>=4.5), `ink-3` 5.57:1 (>=4.5), `ink-dis` 3.55:1 (>=3.0), `accent` 3.53:1 (>=3.0)；Live 内联正文 `#d8e0e8` 13.87:1 (>=4.5), `#8a94a2` 6.02:1 (>=4.5)；Pill 背景合成 `#7eb287` 5.83:1 (>=4.5), `#fbbf24` 7.97:1 (>=4.5)；边框与容器背景 `NOT_VERIFIABLE` |
| `AC1` | 真实 WebView2 启动与证明 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | **Hard Build Barrier 生效**：tauri_build 写入源码树且缺少受信 sidecar 输入，等待 Codex 登记 scratch worktree |
| `AC2` | Workbench 导航与真实输入 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |
| `AC3` | 300ms 静默期与页面失效窗口 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |
| `AC4` | 写后刷新即时性 (retype/undo/restore) | **BLOCKED** | `REAL_WEBVIEW_MOCK_IPC` | `null` | 依 Task 契约严禁以 NOT_RUN 替代，如实标记为 BLOCKED |
| `AC5` | 键盘操作与焦点链 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |
| `AC6` | 真实运行时 Computed Color 提取 | **BLOCKED** | `REAL_WEBVIEW2` | `null` | 同上 |

**总计 9 项场景**：**PASS: 3 项，BLOCKED: 6 项，FAIL: 0 项，NOT_RUN: 0 项**。

## 4. 交付文件清单

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

## 5. 推荐下一步

提交固定交付 commit，由 Codex 在 clean detached exact head 独立复跑 Stage A probes 并完成 Gate 复算与 `git diff --check` 证据归档；交由 DeepSeek Harness 进行 Stage A r4 复审。待隔离 scratch worktree 构建方案获批后，再推进 Stage B 真实 WebView2 运行时验证。
