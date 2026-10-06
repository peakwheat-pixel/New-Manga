---
id: M2-SFX-EPFAIL-AUDIT-1
title: "SFX 推理 run-time EPFail 通道审计：ORT 包装层 run() 期内部静默重跑 CPU 的可观测性闭合"
kind: feature
status: in_review
owner_claim: ZCode 2026-10-04 @worktree M2-SFX-EPFAIL-AUDIT-1-zcode（base=d298ecd0=释放登记 tip；授权=user 2026-10-04 批准进行2 非阻塞候选①；AC1 设计实测前置=get_providers() 耗时+fallback 状态读回可见性）
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

## 交付记录（Owner=ZCode，2026-10-06）

**结果：AC1-AC4 全 PASS。所选设计=稳态每 detect 一次 `session.get_providers()` 读回（公共 API，实测 0.03 μs/次=纯 Python 属性读，占 GPU-EP-1 KO 基准页 1% 时延预算的 ~2.8e-6%），首 provider 与构建期 effective 比对，稳态零追加、变化才追加单一新键 `sfx_ep_runtime_check`（"session providers changed at run time: <built> -> <now> (ORT wrapper run-time EPFail fallback)"）——静默成功主形态当页即观测，重跑亦失败经下一页成功 detect 观测（session 状态持续）；三键构建期语义与写入时点逐字不变、`NEWMANGA_SFX_EP` 解析与 fail-fast 时序零改动、零 stdout 依赖。GPU-EP-1 deploy-record §1.3 登记的「已知未审计通道」由本 Task 闭合（注记声明，历史文件零改动）。全量回归 1826 passed（基线 1823+3 新增）+1 skipped+1 failed（test_catalog 既有 BASELINE_FAILURE）等量递增。status owner_claim→in_review 停写，待 DSH 非作者 Review。**

| AC | 判定 | 核心证据 |
|---|---|---|
| AC1 审计机制 | **PASS** | 实测前置（合同硬要求）：`get_providers()` 单次 0.0303/0.0305 μs（cpu/dml，5 轮×1e6 次中位数）——wrapper :214-216 `return self._providers` 纯 Python 读，GPU-EP-1 时「逐 detect 复读代价高」判断不成立；wrapper EPFail 分支 `set_providers(['CPUExecutionProvider'])` 重放后读回 `[Dml,CPU]→[CPU]` 公共 API 可见（set_providers 一次性 0.121 s 非稳态项）；1% 硬门 PASS（`raw/epfail-audit-get-providers-cost.{json,log}`）。设计+落选理由登记部署记录 §1（异常触发式漏静默成功主形态；低频采样 0.03 μs 下无必要且新增 env 面；私有属性探测依赖 wrapper 内部而公共 API 已暴露同一信息）。commit `0f4702d0` |
| AC2 单测先红后绿 | **PASS** | 3 用例（stub 注入 wrapper run 期 EPFail 形态）：静默成功主形态（构建后 DML 读回 `[Dml,CPU]`=实测真实形态，首次 run 内部翻转 `[CPU]`+重跑成功零异常→当页 `sfx_ep_runtime_check` 精确文案+三键构建期语义不变+第二页持续可见）；稳态零新键；无读回面替身跳过。红=对基线 claim `a336bd41` 跑新测试 1 failed（`KeyError: 'sfx_ep_runtime_check'`）+3 passed 按构造（`raw/tests-epfail-red.log`）；绿=对 impl `0f4702d0` 全文件 82 passed（79 基线+3 新增）（`raw/tests-epfail-green.log`）。commit `0afb22dd` |
| AC3 数值与回归零变化 | **PASS** | parity 抽 KO pre-k01 页（tile 路由）复核与 GPU-EP-1 基准行**逐数字一致**：max|Δconf|=1e-06、max|Δxyxy|=0.0001px、gate_flips=0、derived 2/2+npd 5/48 matched set equal；真实稳态两 face 零新键、三键照常；dml 1.122s 落 GPU-EP-1 KO 基准区间（0.333-2.325，directional）（`raw/epfail-audit-parity-prek01.{json,log}`）。全量回归 `1 failed, 1826 passed, 1 skipped`=基线 1823+3 新增+1 skipped+test_catalog 既有 BASELINE_FAILURE，等量递增（`raw/pytest-full-regression.log`）。commit `2bed03d0` |
| AC4 文档 | **PASS** | [部署记录](../../verification/M2-SFX-EPFAIL-AUDIT-1/deploy-record.md)（背景闭合声明/设计+落选/实测/红绿/parity/回归/已知限制/交付链）+本回填+[Handoff](../handoffs/M2-SFX-EPFAIL-AUDIT-1-zcode-20261004.md)；GPU-EP-1 §1.3 通道闭合以注记声明（deploy-record §0，历史文件零改动） |

**偏差与限制登记**：①实机真实 EPFail（GPU 掉卡）NOT_RUN——探测面可见性由 wrapper 同 API 调用重放+stub 单测覆盖（deploy-record §5.4，与 GPU-EP-1 验证矩阵②同一诚实口径）；②`sfx_ep_runtime_check` 归因「wrapper run-time EPFail fallback」基于本仓从不调用 `set_providers`+wrapper 仅 EPFail 分支调用（同 wheel 版本内成立，升级需复核）；③wrapper fallback 每 session 一次（`disable_fallback`），第二次 EPFail 走既有 typed 失败路径（GPU-EP-1 语义原样）。

**交付链**：`a336bd41` claim → `0f4702d0` impl → `0afb22dd` test（红+绿证据）→ `2bed03d0` verify（实测+parity+回归+部署记录）→ docs（本回填+Handoff）。
