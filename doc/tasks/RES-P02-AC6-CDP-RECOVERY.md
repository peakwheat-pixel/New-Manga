---
id: RES-P02-AC6-CDP-RECOVERY
title: 恢复固定 EXE 的 WebView2 CDP 采集并完成 AC6 重采样（闭合 R3-01）
kind: resolution
governance_version: 2
status: done
approval: derived_from_convergence_decision_20261015
owner: antigravity
reviewer: dsh
integrator: codex
depends_on: [P02-NEW-TIME-BASELINE, P02-NEW-TIME-X6, P02-NEW-TIME-X6-POSTRUN-REVIEW, P02-NEW-TIME-X6-BUILD-CARGO]
must_not_depend_on: [P02-NEW-TIME-X6-AC1-AC7]
inherits_finding: [R3-01]
blocked_task: P02-NEW-TIME-X6-AC1-AC7
blocked_reason: resolved
owner_head: 4abb8d288e005dc58e3270b12389d33cd7a52ac1
delivery_head: 738759cd3cbd2ca47177b95c64402b57c491ba40
reviewed_head: 738759cd3cbd2ca47177b95c64402b57c491ba40
review_decision: approved
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7
awaiting_external: false
created_by: dsh (Active Coordinator, coordinator epoch 2)
created_at: 2026-10-15
detail_plan: G:/CODEX/New Manga.workspace/agent-output/dsh/P02-NEW-TIME-X6-AC1-AC7/resolution-task-RES-P02-AC6-CDP-RECOVERY.md
owner_evidence: G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-ANTIGRAVITY/verification/RES-P02-AC6-CDP-RECOVERY/report.md

owner_delivery_head: 4abb8d288e005dc58e3270b12389d33cd7a52ac1

integration_status: integrated

integration_commit: 9e3c5310d5652f5491f3dc11825d86c03dac22ee

integration_target: main

integration_worktree: G:/CODEX/New Manga

base_commit: a8d9219ba192c9a7feb1437240e51535938073fa

implementation_repairs_used: 0

max_implementation_repairs: 2

mainline_closeout_task: P02-MAINLINE-INTEGRATION
---

# RES-P02-AC6-CDP-RECOVERY
## 当前主线位置（2026-10-15）

已审成果已原生快进 main @ 9e3c5310d5652f5491f3dc11825d86c03dac22ee；主线核验 source 102/102、Gate capsule 19/19 PASS，详情见 [P02-MAINLINE-INTEGRATION](P02-MAINLINE-INTEGRATION.md)。以下隔离分支/未合 main 叙述保留其历史语义，当前位置以本节及 front matter 为准。原始 Review、I1/I2 与资源保留记录不变。


## 当前结论（DONE / epoch 3）

R3-01 已闭合；a7 原始采集 10/10 computed PASS、输入框 ratio=13.87。Owner 收口、DSH 内容 Review、E 勘误复核、Codex VERIFY/集成与资源保留核销均完成。父 AC1–AC7 同步收口；本 resolution 未进行实现返修，不增加父 I1/I2=2/2。当前交付与最新 Review 指向 738759cd3cbd2ca47177b95c64402b57c491ba40；集成证据 1135d9879ae02521b2a2b30a3eeeff55664aa36b。旧实验 BLOCKED/待收口段仅保留历史语义。

- [x] 固定 EXE、真实 WebView2 AC6 a7 原始样本与派生数据可核验。
- [x] R3-01、汇总/P-04/失败退出码/SHA 勘误、独立 bounded Review 已闭合。
- [x] immutable manifests VERIFY PASS，内容集成与 resource closeout 完成。

## 采集记录（2026-10-15 更新：交互式会话采集成功，R3-01 证据层闭合）

通过在**当前用户交互式桌面会话**中用计划任务（``schtasks /SC ONCE /IT``，用完即删）直接运行 ``node apps/desktop/frontend/e2e/p02-new-time/ac6-contrast.mjs``，AC6 采集首次成功：

- ``EXIT=0``；``samples=10 / computed=10 / fails=[] / not_verifiable=[] / alpha_compositing_triggered=false``。
- ``[data-testid="page-id-input"]`` 行取得真实取值：``foreground=rgb(216,224,232)``、``background=rgb(16,20,24)``（``backgroundSource=INPUT[page-id-input]``，``backgroundLayers`` alpha=1）、``alpha_compositing_applied=false``、``contrast_ratio=13.87`` ≥ 4.5 → ``contrast_result=PASS``。
- 证据目录：``verification/P02-NEW-TIME-X6-AC1-AC7/runs/p02-newtime-ac-20261014-i2/ac6-contrast-a7/``（``ac6-contrast.json`` 21,200B、``ac6-workbench.png``、``ac6.stdout/stderr.log``、``execution-metadata.json``；本次为直接运行采集，无外层 ``runner-execution.json``）。

**R3-01 判定（证据层）**：I1 的 ``present:false / NOT_VERIFIABLE / "element has no visible text content"`` 与 P-04 关于"半透明背景/祖先链无底色/合成保护性返回"的不实叙述均已消除。**待 Owner 收口**（按 a7 重算 rollup 与 findings 的 P-04、更新 Task/Handoff、提交、在最终 head 生成并 ``--verify`` manifest），随后由 DSH 做最后一轮 bounded review。

> 本会话（DSH 派发链）内启动该 GUI E2E 会因 Windows/WebView2 窗口创建失败而 panic（``0x80070578``）；交互式会话路径是本次达成采集的关键。

AC6 重采样在当前执行环境下**不可能完成**：固定 EXE 启动即 panic ——
`Failed to setup app: … failed to create webview: WebView2 error: WindowsError(Error { code: HRESULT(0x80070578), message: "无效的窗口句柄。" })`
（Owner 证据 `attempts/exp1-proxy-clean/app.stderr.log`）→ `msedgewebview2.exe` 从未初始化 → 9333 无 listener → 采集器 45s `TypeError: fetch failed`。

**鉴别实验（Coordinator，决定性）**：在 DSH 会话的进程环境内启动 `notepad` → `hwnd=0`、进程立即退出。当前会话 `SessionId=1`、`UserInteractive=True`、`qwinsta` 显示 `console 49745 1 Active`、`explorer` 正常 → **桌面本身正常，受限的是 DSH 派发链的进程环境**（窗口站/桌面绑定或沙箱作业限制）。对照：I1（10-14 23:22）由 **Codex Desktop** 派发成功。

**待外部条件**：在可创建窗口的交互式桌面会话中运行一次 AC6：

```pwsh
cd "G:\CODEX\New Manga.workspace\worktrees\P02-NEW-TIME-X6-AC1-AC7-ANTIGRAVITY"
node apps/desktop/frontend/e2e/p02-new-time/ac6-contrast.mjs
```

（建议先在同一会话启动 `notepad` 确认窗口可见；若 `notepad` 也无窗口，需先处理桌面会话。）

由 `decide-convergence.py --mode converge` 的权威裁决派生（`task_outcome=BLOCKED`、`further_implementation_repair_allowed=false`、`forbid_implementation_repair_beyond=I2`、`actions=[CREATE_RESOLUTION_TASK, REPLAN_DAG, BACKLOG_NONBLOCKERS]`），`lineage_state` 已登记 `R3-01 → resolution_task_id=RES-P02-AC6-CDP-RECOVERY`（cap=1）。

## 目标

在当前主机环境恢复固定 packaged EXE 的 WebView2 CDP 可采集性，用 I2 已修复的 AC6 采样器完成一次有效采样，从而闭合独立 Review r3 的 `R3-01`（P2）。**本 Task 是 resolution**：不改 AC 口径、不改产品代码、不新增 implementation 返修轮（禁止 I3）。

## 冻结输入

- 固定 EXE（只读）：`G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO/apps/desktop/src-tauri/target/release/m2rc1-desktop.exe`，sha256 `92AC7B8EFB646FE77DF8245B13C9AF9314BEF415B2F0E007B1CDCEA729BC13FD`（9,367,040 bytes）。
- 采集脚本 head：`agent/antigravity/P02-NEW-TIME-X6-AC1-AC7` @ `8ec9f3b8cefe3d2165eb8f6b15fac805394619ee`（含 I2 修复：表单控件按 `value`/`placeholder` 判可见文本、`alpha_compositing_applied`；`lib/env.mjs#CDP_PORT=9333`）。
- 只读证据基线：`verification/P02-NEW-TIME-X6-AC1-AC7/runs/p02-newtime-ac-20261014-i1/**`（I1 成功证据）与 `runs/p02-newtime-ac-20261014-i2/attempts/**`（4 次失败尝试）。

## 执行结果与结论（2026-10-15）

Owner（Antigravity）已完成三组严格对照实验：
1. **实验 1（清空代理环境对照）**：在同一 shell 中显式清空 `HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY`、`ZCODE_HTTP_PROXY`，设置 `NO_PROXY=localhost,127.0.0.1,::1` 后运行，45 秒超时，退出码 1。发现固定 EXE 在启动创建 webview 时触发 Rust Panic：`HRESULT(0x80070578) 无效的窗口句柄`。
2. **实验 2（启动期实时进程与端口监控）**：捕获 `m2rc1-desktop.exe`（PID 20920），确认没有 `msedgewebview2.exe` 产生，9330–9340 端口无 listener，再次复现 0x80070578 崩溃。
3. **实验 3（直接 node 启动进程追踪）**：捕获 `m2rc1-desktop.exe`（PID 12972）启动后即 panic 退出，45 秒内端口 9333 无 listener。

**结论**：当前障碍为确凿的主机环境级阻断（Win32 窗口句柄无法完成消息泵与 WebView2 控制器附加）。固定 EXE 无法启动 WebView2，故 CDP 端口无法建立。根据验收标准与规则，**Task 如实标记为 `BLOCKED`，禁止伪造 PASS，禁止 I3**。

详细报告见：`verification/RES-P02-AC6-CDP-RECOVERY/report.md`。

## 历史实验验收状态（a7 前，不代表当前）

- `R3-01`：**未闭合（BLOCKED）**；
- AC6：**BLOCKED**（`[data-testid="page-id-input"]` 未能采得，无伪造数据）；
- 证据目录：`verification/RES-P02-AC6-CDP-RECOVERY/`，未改动任何 I1/I2 既有证据。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| FINAL-01 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/codex-verification.json | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | c246e299752768fb4675822ccc2204807df9da8884823255d185c4d7ed939e1d | CANONICAL |
| FINAL-02 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/completion-adjudication.md | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | 799b56e19120a81ef5d95643eb90633f4ccbb6d9b2461a736c1b487628b3c0e9 | CANONICAL |
| FINAL-03 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/convergence-dry.json | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | 86954bfb7ef5aeaeaf41c81658afd2a4a2a0d2709a153d3e328b726f41d01cd9 | CANONICAL |
| FINAL-04 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/convergence-input.json | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | 5a86224c72d4132d8ad4e3d908aca1a4ea0a6eb10b43c77cedf5850541e9cd3d | CANONICAL |
| FINAL-05 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/convergence-output.json | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | 71206ce8ad187e5c8070c89a6f96c9c57ad2ab80450fa02cd5fa4d04e2114340 | CANONICAL |
| FINAL-06 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/current-summary.json | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | 46b47088e76fb783ab5a8e6a29cb15a654ac7310d78afa4977e098b3212472e1 | CANONICAL |
| FINAL-07 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/dsh-bounded-review.md | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | f885ea2a3d49affa76a7df77f775e8d9dd35c140d9b45b1acbfcd972625fa610 | CANONICAL |
| FINAL-08 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/dsh-e-erratum-review.md | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | be9995acc29d4282d5a631041383cb404ca8df22f6787cbd886605536db9cc32 | CANONICAL |
| FINAL-09 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/gate-evidence-manifest.json | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | d334037061ab01ba4aed3da12e78392633817047e027157c11cf0fbf14967c8c | CANONICAL |
| FINAL-10 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/integration-adjudication.md | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | 96cc982aa93d4d8ae984961d4e446ebf3a273bad5bc5a5360e30364082154f19 | CANONICAL |
| FINAL-11 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/resolution-convergence-input.json | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | 0c9cdd1d1d6053959a3e2421df5dd86236ba9b8dba4452488cb7929cc42133f3 | CANONICAL |
| FINAL-12 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/resolution-convergence-output.json | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | 7bed0870d5fcf1323278bcaca9e9e6181b3f16b96915d61cc5b5c8fc5b8d6215 | CANONICAL |
| FINAL-13 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/resource-inventory.json | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | 02aba7355e084820be913781d1c746703bfff0691e9b32848a90f5846ee07dd6 | CANONICAL |
| FINAL-14 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/result-input.json | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | d6fd98e3afdcb21a0a14acae0675aeb6da51a8a0494ffb72451aaf4170060fc3 | CANONICAL |
| FINAL-15 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/result-output.json | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | c2c7473f861644e569092465fc799e25fb9c7365a85e57851823de589f4e50df | CANONICAL |
| FINAL-16 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/review-dispatch.json | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | 2e26857fbed1a82e25732e8a300c2869aabc199ba94c465c1a6e71270e73be70 | CANONICAL |
| FINAL-17 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/revision-input.json | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | 725c1b17e5341762f54a7ca54ad4f09778f8f71eb585782f4315c1306a60dd4c | CANONICAL |
| FINAL-18 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/revision-output.json | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | 5d964f23b3de0c48c5b89c63400824d128bd5f50f391b8fbbc63c8a8601da1fe | CANONICAL |
| FINAL-19 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/source-evidence-manifest.json | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | 06a1cedfc53fc79607a9fcb99299ae0f9e3b0ba4df50d7dedc5a32c530698ac1 | CANONICAL |
| FINAL-20 | AC6/AC7 + Review/Integration | verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/source-manifest-verify.json | 9e3c5310d5652f5491f3dc11825d86c03dac22ee | b59f3556f91be12be61dbeb9f44fc0bfec59d8348ba60b2610d6a1c384782e99 | CANONICAL |


## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| owner_worktree | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-ANTIGRAVITY | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-ANTIGRAVITY | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-INTEGRATION/verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/resource-inventory.json | fixed reviewed HEAD, raw evidence and original untracked manifest; Owner launcher exit 0; no second writer started；所有权/引用未解除，原位保留 |
| prior_integration_worktree | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-POSTRUN-REVIEW | PRESERVE_UNKNOWN | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-POSTRUN-REVIEW | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-INTEGRATION/verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/resource-inventory.json | dirty/untracked historical Review and governance retained; not staged/reset/cleaned；所有权/引用未解除，原位保留 |
| integration_worktree | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-INTEGRATION | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-INTEGRATION | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-INTEGRATION/verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/resource-inventory.json | new content integration and immutable final evidence branch retained; readonly E reviewer may be active；所有权/引用未解除，原位保留 |
| synthetic_task_env | G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-AC1-AC7 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-AC1-AC7 | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-INTEGRATION/verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/resource-inventory.json | isolated synthetic run-i1/run-i2/failed diagnostics; no cleanup or GUI rerun；所有权/引用未解除，原位保留 |
| fixed_build_artifacts | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-INTEGRATION/verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/resource-inventory.json | pinned executable/sidecar immutable input; EXE SHA checked; Build cache residuals retained；所有权/引用未解除，原位保留 |
| codex_agent_output | G:/CODEX/New Manga.workspace/agent-output/codex/TAKEOVER-20261015 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/TAKEOVER-20261015 | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-INTEGRATION/verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/resource-inventory.json | original dispatch logs/prompts/exits/pre-AUTO governance snapshots/recovery scripts retained；所有权/引用未解除，原位保留 |
| dsh_agent_output | G:/CODEX/New Manga.workspace/agent-output/dsh/P02-NEW-TIME-X6-AC1-AC7 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/dsh/P02-NEW-TIME-X6-AC1-AC7 | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-INTEGRATION/verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/resource-inventory.json | previous takeover/convergence/interactive collection proof retained；所有权/引用未解除，原位保留 |

## Closeout Record

- Closeout date / Codex：2026-10-15；Coordinator epoch=3。
- canonical_evidence_status / resource_closeout_status：complete / complete。
- 内容 merge：38d926026e9032a528ce578dba7290c5ce65356b；已审 E head：738759cd3cbd2ca47177b95c64402b57c491ba40；最终集成证据 commit：1135d9879ae02521b2a2b30a3eeeff55664aa36b。
- source manifest 官方 VERIFY：102/102 PASS；gate capsule：19/19 PASS；DSH 内容/E Review 均 APPROVED，新增 P0/P1/P2=0。
- 删除、迁移、归档：0 项 / 0 B；全部资源原位保留，不删除 worktree/模型/用户内容。
- 未关闭产品项：P-01 Escape、P-02 tokens、P-03 theme 与其它 P3/P4 backlog；BC-AC5=PARTIAL、旧 H1/P2-1/13 项缺失来源不变。Git 自动维护的旧 checkpoint 坏引用保留，当前 pins 可解析。
- 当前指针：主 checkout STATUS / Plan / Task Index 与 rolling checkpoint 收口；该副本是主控 fenced state 的版本化镜像；无 shadow runtime/lease。
- 下一任务建议：当前无已释放 READY，不为 P3/P4 开新实现轮；无需下一步操作。
