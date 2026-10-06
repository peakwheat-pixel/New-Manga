---
id: M2-PROD-SFX-PROBE-1
title: "packaged sfx-detect 探针：frozen 进程内 SFX 真实推理（DML）运行证据"
kind: feature
status: in_progress
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
approval: user_2026-10-04_批准进行2（已登记非阻塞候选②：M2-PROD-DETECT-2 裁决⑥ NOT_RUN 结构缺口的 sfx slice）
depends_on: [M2-SFX-GPU-EP-1]
base_commit: 72807d30
branch: agent/zcode/M2-PROD-SFX-PROBE-1
worktree: G:/CODEX/New Manga.worktrees/M2-PROD-SFX-PROBE-1-zcode
review_events: []
created: 2026-10-04
---

# Task: M2-PROD-SFX-PROBE-1 — packaged sfx-detect 探针

## 背景与授权

M2-PROD-DETECT-2（done @merge `9e44fb21`）裁决⑥：frozen 命令面（`core.ping`/`ListBooks`/`core.shutdown`，M2-IPC1 冻结）无 detect RPC，**frozen 进程内 ML import/detect 结构性不可达**，AC5 判 PARTIAL，登记后续 slice「命令面扩展 + frozen 进程内 detect 验证」。M2-SFX-GPU-EP-1 收口再次登记该缺口（候选②）：**frozen 进程内 DML 运行证据需命令面扩展**。用户 2026-10-04 批准进行2，释放本 Task。

现状：manga 检测器的闭包外等价探针 6/6 PASS（PROD-DETECT-2 L1-L4）；GATE 25 场景探针全为资源通道；SFX 权重 v2b+onnxruntime-directml 已随包（GPU-EP-1 AC4 闭包断言含 `onnxruntime_pybind11_state.pyd`+`DirectML.dll`）。

## 验收条件

- **AC1 命令面扩展（契约敏感——先核实冻结范围再动手）**：为 sidecar 提供一条**新增** probe 路径触发 sfx detect。实现路径 Owner 裁量，顺序约束：①先核实 M2-IPC1/M2-C1 对 sidecar 命令面的冻结粒度（IPC 命令集 vs CLI 入口）；②优先选择**不触碰既有冻结命令语义**的 additive 方案（新增 probe 子命令/独立探针入口均可）；③若判定必须修订冻结契约，仅允许「纯新增」修订——在 Task 内登记契约修订草案（rev 号+diff 面），交集成轮核验，**不得改写既有命令行为**。
- **AC2 frozen 进程内 sfx detect 真实运行**：对安装后环境（GATE runner 安装目录或 NSIS 静默安装）触发一次真实 sfx detect（v2b 生产权重，输入=合成漫画页或 K01 页），记录：EXIT 码、候选数、耗时、**options 三键**（`device`/`sfx_ep`/`sfx_ep_fallback`——预期 device=dml，无 fallback；如遇 wrapper 回退形态则如实登记不视为失败）。候选=0 不得静默判 PASS（登记原因并评估）。
- **AC3 既有面零破坏**：既有 frozen 命令行为零变化（单测/探针复核）；GATE 重跑 PASS 25/25（新 probe 不进 runner 场景集亦可，独立探针证据即可，但 GATE 必须复跑证明无回归）；包体积变化如实登记。
- **AC4 回归与纪律**：受影响 pytest 套件与基线一致（等量递增）；`git diff --check` EXIT=0；禁改面专项 diff 为空。
- **AC5 文档**：探针结果 JSON+log 落 `verification/M2-PROD-SFX-PROBE-1/`；部署/探针记录+Task 回填+Handoff；PROD-DETECT-2 AC5 NOT_RUN 子项以注记方式声明由本 Task 闭合。

## 纪律与限制

- 允许路径：`packaging/m2ac5/**`（如探针入口需要）、sidecar 命令注册面文件（`src/**` 逐文件声明）、`apps/desktop/src-tauri/**` 仅当探针需要 Tauri 侧触发（尽量不需要；如需则先在 Task 偏差登记说明最小 diff 面）、`tests/**`、`experiments/M2-PROD-SFX-PROBE-1/**`、`verification/M2-PROD-SFX-PROBE-1/**`、`doc/tasks/M2-PROD-SFX-PROBE-1.md`、`doc/handoffs/`、契约文档仅在「纯新增修订」时按 AC1③ 登记。
- 禁改：`contracts/**` 既有 DTO/命令语义、`doc/STATUS.md`/`doc/REBASELINE_PLAN.md`（集成方收口面）、M2-AC5 runner 场景集（25/25 保持）。
- 分支 `agent/zcode/M2-PROD-SFX-PROBE-1`，worktree 独立；构建/GATE/安装类长命令一律后台+log 落盘+轮询；`build_sidecar.ps1` 后必须 `tauri build` 才能拿到含 probe 的安装包（先例：tauri build 姿势见三确认批次教训）。
- 权重/页图零入库（外部树）；fresh checkout 须先跑 build_sidecar.ps1（如实登记 NOT_RUN 前置）。
