---
id: M2-SFX-EPFAIL-AUDIT-1
title: "SFX 推理 run-time EPFail 通道审计：ORT 包装层 run() 期内部静默重跑 CPU 的可观测性闭合"
kind: feature
status: ready
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
approval: user_2026-10-04_批准进行2（已登记非阻塞候选①：GPU-EP-1 r2 N-P3-1 run-time EPFail 未审计通道）
depends_on: [M2-SFX-GPU-EP-1]
base_commit: 72807d30
branch: agent/zcode/M2-SFX-EPFAIL-AUDIT-1
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-EPFAIL-AUDIT-1-zcode
review_events: []
created: 2026-10-04
---

# Task: M2-SFX-EPFAIL-AUDIT-1 — SFX 推理 run-time EPFail 通道审计

## 背景与授权

M2-SFX-GPU-EP-1（done @merge `931a6d03`）交付了「DML 失败回退 CPU 三键审计」，但其覆盖面**只到会话构建**（构造后 `session.get_providers()` 读回反推一次）。部署记录 §1.3（r2 N-P3-1 收窄）如实登记：**ORT Python 包装层在 `run()` 期对 `EPFail` 另有内部静默重跑 CPU**（wrapper `onnxruntime_inference_collection.py:278-305` 附近，仅 stdout 两行提示），该 run-time 通道不在三键审计内；「逐 detect 复读 get_providers」方案因代价已权衡不采。用户 2026-10-04 批准进行2，释放本 Task 闭合该已登记缺口。

**已钉死的事实与教训（设计约束来源）**：
- wrapper 的 stdout 提示在 frozen 面不可靠（GPU-EP-1 r2 N-P4-2：banner 走 stdout print 会被 native 窗口丢弃两形态）——**审计设计不得依赖 stdout 捕获**。
- 除包装层内部重试外，run() 失败维持既有 detect 期 typed 失败路径不变（deploy-record §1.3）。
- 现有三键（`device`/`sfx_ep`/`sfx_ep_fallback`）语义与写入时点（引擎构建后一次）不变。

## 验收条件

- **AC1 审计机制（Owner 设计裁量，先登记后实现）**：为 run-time EPFail 通道提供**不依赖 stdout** 的可观测性。候选方向（可组合）：(a) 条件性读回——仅在该 session 发生过 run 期异常/typed 失败后，detect 期补一次 `get_providers()` 读回并在 options 审计追加键（如 `sfx_ep_runtime_check`）；(b) 低频采样读回（每 N 次 detect 一次，N 为 env 可配常量，默认值须给出代价测算）；(c) 会话级 EPFail 探测（包装层行为可达的其他 API 面）。**硬约束**：稳态每页时延增量 ≤1%（vs GPU-EP-1 AC3 基准 1.106-1.211s/页）；不改三键既有语义；不改 `NEWMANGA_SFX_EP` 解析与 fail-fast 时序；零 stdout 依赖。所选设计+落选理由写入部署记录。
- **AC2 单测先红后绿**：覆盖 run-time 通道审计行为（stub 注入包装层形态）；红证据=对基线实现跑新测试，绿证据=实现后全绿。
- **AC3 数值与回归零变化**：AC2/GPU-EP-1 的 parity 基准复跑结论不变（GPU vs CPU 漂移量级不因本 Task 变化，抽 1 页复核即可）；全量回归与 main 基线等量递增（1823+1sk+1 failed test_catalog 既有 + 本 Task 新增用例数）。
- **AC4 文档**：部署记录（背景/设计/实测/已知限制）+ Task 回填 + Handoff；GPU-EP-1 deploy-record §1.3 的「已知未审计通道」登记以**注记方式**闭合（不改历史文件语义，新报告内声明由本 Task 闭合）。

## 纪律与限制

- 允许路径：`src/infrastructure/providers/detection_sfx.py`、`tests/providers/test_detection_sfx.py`、`tests/core/test_sfx_assembly.py`（如需）、`experiments/M2-SFX-EPFAIL-AUDIT-1/**`、`verification/M2-SFX-EPFAIL-AUDIT-1/**`、`doc/tasks/M2-SFX-EPFAIL-AUDIT-1.md`、`doc/handoffs/`。
- 禁改：`contracts/**` 与既有冻结端口面、`apps/**`、`packaging/**`、`requirements.txt`、其他 provider 文件；`doc/STATUS.md`/`doc/REBASELINE_PLAN.md`（集成方收口面）。
- 分支 `agent/zcode/M2-SFX-EPFAIL-AUDIT-1`，worktree 独立；impl/test/verify 分 commit；交付后 status→in_review 停写。
- 长命令（>60s：全量回归/parity 复跑）一律后台执行+log 落盘+轮询；GPU 机器可用 `NEWMANGA_SFX_EP=dml`（生产默认），CPU-only 路径由 stub 覆盖。
