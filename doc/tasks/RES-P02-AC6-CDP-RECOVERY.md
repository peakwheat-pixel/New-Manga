---
id: RES-P02-AC6-CDP-RECOVERY
title: 恢复固定 EXE 的 WebView2 CDP 采集并完成 AC6 重采样（闭合 R3-01）
kind: resolution
governance_version: 2
status: blocked
approval: derived_from_convergence_decision_20261015
owner: antigravity
reviewer: pending_route
integrator: dsh
depends_on: [P02-NEW-TIME-BASELINE, P02-NEW-TIME-X6, P02-NEW-TIME-X6-POSTRUN-REVIEW, P02-NEW-TIME-X6-BUILD-CARGO]
must_not_depend_on: [P02-NEW-TIME-X6-AC1-AC7]
inherits_finding: [R3-01]
blocked_task: P02-NEW-TIME-X6-AC1-AC7
created_by: dsh (Active Coordinator, coordinator epoch 2)
created_at: 2026-10-15
detail_plan: G:/CODEX/New Manga.workspace/agent-output/dsh/P02-NEW-TIME-X6-AC1-AC7/resolution-task-RES-P02-AC6-CDP-RECOVERY.md
---

# RES-P02-AC6-CDP-RECOVERY

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

## 验收状态

- `R3-01`：**未闭合（BLOCKED）**；
- AC6：**BLOCKED**（`[data-testid="page-id-input"]` 未能采得，无伪造数据）；
- 证据目录：`verification/RES-P02-AC6-CDP-RECOVERY/`，未改动任何 I1/I2 既有证据。
