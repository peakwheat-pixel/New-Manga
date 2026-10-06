---
id: M2-SFX-EPFAIL-AUDIT-1
title: "SFX 推理 run-time EPFail 通道审计：ORT 包装层 run() 期内部静默重跑 CPU 的可观测性闭合"
kind: feature
status: done
integration: merge 9a29e742（2026-10-06，集成 Gate：允许面 17 文件 git 核验+禁改面零 diff+whitespace 沿 GPU-EP-1 raw log 先例+全量回归 1 failed+1828 passed+1 skipped[唯一 failed=test_catalog 既有，基线 1823+5 等量递增]；DSH r1 changes_requested P1-1/P2-1 返修闭+r2 approved 建议集成 0×新 P0-P3，r2 P4×4 顺笔闭合 cfeed03b/35e9310f/ce11334d——composite 稳态零追加断言+parity 同 HEAD 重跑+链表补全+失败路径措辞精确化；报告 doc/reviews/M2-SFX-EPFAIL-AUDIT-1-cf013b01-dsh-r1.md 与 doc/reviews/M2-SFX-EPFAIL-AUDIT-1-d388a7bf-dsh-r2.md）
owner_claim: ZCode 2026-10-04 @worktree M2-SFX-EPFAIL-AUDIT-1-zcode（base=d298ecd0=释放登记 tip；授权=user 2026-10-04 批准进行2 非阻塞候选①；AC1 设计实测前置=get_providers() 耗时+fallback 状态读回可见性）
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
approval: user_2026-10-04_批准进行2（已登记非阻塞候选①：GPU-EP-1 r2 N-P3-1 run-time EPFail 未审计通道）
depends_on: [M2-SFX-GPU-EP-1]
base_commit: 72807d30（r1 P4-1 双值注记：72807d30=Task 合同释放登记 base；d298ecd0=owner 分支实际 fork 点=释放 commit（`merge-base --is-ancestor`：72807d30 是 d298ecd0 祖先；分支自 d298ecd0 checkout，merge-base(HEAD, d298ecd0)=d298ecd0 实证），owner claim/HANDOFF 统一以 d298ecd0 为准）
branch: agent/zcode/M2-SFX-EPFAIL-AUDIT-1
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-EPFAIL-AUDIT-1-zcode
review_events: [r1 DSH changes_requested 2026-10-06（1×P1 审计键 composite 装配面被丢弃→编排裁决采透传方案、1×P2 1% 预算口径差 100×、2×P3、8×P4；报告 doc/reviews/M2-SFX-EPFAIL-AUDIT-1-cf013b01-dsh-r1.md）→ 返修 6c2825ce..d388a7bf → r2 DSH approved 建议集成（r1 逐条全闭 0×新 P0-P3、4×P4 顺笔闭合；报告 doc/reviews/M2-SFX-EPFAIL-AUDIT-1-d388a7bf-dsh-r2.md）]
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

**结果：AC1-AC4 全 PASS（r1 review-fix 后维持，DSH r1 changes_requested 1×P1/P2/P3×2/P4×8 逐项处置见下）。所选设计=稳态每 detect 一次 `session.get_providers()` 读回（公共 API，口径=单次原语调用、实测 0.0304 μs/次=纯 Python 属性读；两个占比并列：页占比 2.75e-6%（vs GPU-EP-1 KO 基准 1.106 s/页）、1% 预算占比 2.7486e-4%（预算=11,060 μs，r1 P2-1 口径修正：1% 预算=页时延×1% 而非整页微秒数）），首 provider 与构建期 effective 比对，稳态零追加、变化才追加单一新键 `sfx_ep_runtime_check`（"session providers changed at run time: <built> -> <now> (ORT wrapper run-time EPFail fallback)"）——静默成功主形态当页即观测，重跑亦失败经下一页成功 detect 观测（session 状态持续）；composite 面条件性透传该键（r1 P1-1 返修：仅当 sfx 面实际产出，不透传 device/sfx_ep/sfx_ep_fallback——device 与 primary torch 面同名冲突）；三键构建期语义与写入时点逐字不变、`NEWMANGA_SFX_EP` 解析与 fail-fast 时序零改动、零 stdout 依赖。GPU-EP-1 deploy-record §1.3 登记的「已知未审计通道」由本 Task 闭合（注记声明，历史文件零改动）。全量回归 1828 passed（基线 1823+首轮 3+返修 2）+1 skipped+1 failed（test_catalog 既有 BASELINE_FAILURE）等量递增。status 保持 in_review 停写，待 DSH r2。**

| AC | 判定 | 核心证据 |
|---|---|---|
| AC1 审计机制 | **PASS** | 实测前置（合同硬要求；r1 P2-1 口径修正后重跑值）：`get_providers()` 单次 0.0297/0.0304 μs（cpu/dml，5 轮×1e6 次中位数，口径=单次原语调用 P4-6）——wrapper :214-216 `return self._providers` 纯 Python 读，GPU-EP-1 时「逐 detect 复读代价高」判断不成立；wrapper EPFail 分支 `set_providers(['CPUExecutionProvider'])` 重放后读回 `[Dml,CPU]→[CPU]` 公共 API 可见（set_providers 一次性 0.117 s 非稳态项）；1% 硬门 PASS：页占比 2.75e-6%（vs 1.106 s/页）/ 1% 预算（11,060 μs）占比 2.7486e-4% 并列（`raw/epfail-audit-get-providers-cost.{json,log}` 为重跑再生证据）。设计+落选理由登记部署记录 §1（异常触发式漏静默成功主形态；低频采样 0.03 μs 下无必要且新增 env 面；私有属性探测依赖 wrapper 内部而公共 API 已暴露同一信息）。commit `0f4702d0` |
| AC2 单测先红后绿 | **PASS** | 3 用例（stub 注入 wrapper run 期 EPFail 形态）：静默成功主形态（构建后 DML 读回 `[Dml,CPU]`=实测真实形态，首次 run 内部翻转 `[CPU]`+重跑成功零异常→当页 `sfx_ep_runtime_check` 精确文案+三键构建期语义不变+第二页持续可见）；稳态零新键；无读回面替身跳过。红=对基线 claim `a336bd41` 跑新测试 1 failed（`KeyError: 'sfx_ep_runtime_check'`）+3 passed 按构造（`raw/tests-epfail-red.log`）；绿=对 impl `0f4702d0` 全文件 82 passed（79 基线+3 新增）（`raw/tests-epfail-green.log`；红 log 3 passed=2 辅助用例+1 被 `-k runtime` 选中的既有用例 test_hash_mismatch_fails_before_any_runtime_import，r1 P3-2 精确化）。commit `0afb22dd`；r1 返修复核见下 r1 段 |
| AC3 数值与回归零变化 | **PASS** | parity 抽 KO pre-k01 页（tile 路由）复核与 GPU-EP-1 基准行**逐数字一致**：max|Δconf|=1e-06、max|Δxyxy|=0.0001px、gate_flips=0、derived 2/2+npd 5/48 matched set equal；真实稳态两 face 零新键、三键照常；dml 1.122s 落 GPU-EP-1 KO 基准区间（0.333-2.325，directional）（`raw/epfail-audit-parity-prek01.{json,log}`）。全量回归 `1 failed, 1826 passed, 1 skipped`=基线 1823+3 新增+1 skipped+test_catalog 既有 BASELINE_FAILURE，等量递增（`raw/pytest-full-regression.log`）；r1 返修后复跑 `1 failed, 1828 passed, 1 skipped`=基线 1823+首轮 3+返修 2（`raw/pytest-full-regression-r1fix.log`）。commit `2bed03d0` |
| AC4 文档 | **PASS** | [部署记录](../../verification/M2-SFX-EPFAIL-AUDIT-1/deploy-record.md)（背景闭合声明/设计+落选/实测/红绿/parity/回归/已知限制/交付链）+本回填+[Handoff](../handoffs/M2-SFX-EPFAIL-AUDIT-1-zcode-20261004.md)；GPU-EP-1 §1.3 通道闭合以注记声明（deploy-record §0，历史文件零改动） |

**偏差与限制登记**：①实机真实 EPFail（GPU 掉卡）NOT_RUN——探测面可见性由 wrapper 同 API 调用重放+stub 单测覆盖（deploy-record §5.4，与 GPU-EP-1 验证矩阵②同一诚实口径）；②`sfx_ep_runtime_check` 归因「wrapper run-time EPFail fallback」基于本仓从不调用 `set_providers`+wrapper 仅 EPFail 分支调用（同 wheel 版本内成立，升级需复核）；③wrapper fallback 每 session 一次（`disable_fallback`），第二次 EPFail 走既有 typed 失败路径（GPU-EP-1 语义原样）。

**交付链**：`a336bd41` claim → `0f4702d0` impl → `0afb22dd` test（红+绿证据）→ `2bed03d0` verify（实测+parity+回归+部署记录）→ `cf013b01` docs（本回填+Handoff）→ r1 review-fix 段（下）。

## r1 review-fix（DSH changes_requested：1×P1、1×P2、2×P3、8×P4；报告由集成方导入 doc/reviews/）

**P1-1（必闭，已闭，编排裁决采透传方案 (a)）——composite 未透传 run-time 审计键**：`MangaSfxParallelDetectionProvider.detect` 的 tail options 重建处条件性透传 `sfx_ep_runtime_check`（仅当 sfx 面实际产出该键时追加该单键、值原样；稳态 composite options 逐字节不变）；只透传该 sfx 专属键，**不透传** device/sfx_ep/sfx_ep_fallback（device 与 primary torch 面同名冲突=DSH r1 提醒，三键保持 sfx 面 engine-build 写入点）；typed 降级分支不承载（无成功 detect 无该键，形态 2 由下一成功页观测）。commit `6c2825ce`+测试 `2356fb8f`（composite 透传用例+P3-1 形态 2 钉子：首次 run fallback+重跑失败当页无 options→同实例第二成功页出现新键；红=对 cf013b01 composite 用例 KeyError+形态 2 钉子按构造绿如实登记 `raw/tests-epfail-r1fix-red.log`；绿=新用例 2 passed+全文件 84 passed+tests/core/test_sfx_assembly.py 19 passed 零破坏 `raw/tests-epfail-r1fix-green.log`）。

**P2-1（应返修，已闭）**：1% 预算口径差 100×——`one_percent_budget_us` 修正为 11,060 μs（1.106 s×1%；前版误用整页 1,106,000 μs），gate 同步；微基准脚本重跑再生 raw JSON/log（非手改）：cpu 0.0297/dml 0.0304 μs，页占比 2.75e-6% 与 1% 预算占比 2.7486e-4% 并列（P4-6 口径注明=单次原语 get_providers() 调用）。commit `22ea8a09`。

**P3 闭**：P3-1 形态 2 钉子（同上 2356fb8f）；P3-2 红 log 叙述精确化（3 passed=2 新辅助用例+1 既有用例被 `-k runtime` 选中，deploy-record §2+本表 AC2 行+Handoff 同步）。

**P4 顺笔闭**：P4-1 base_commit 双值注记（本 frontmatter）；P4-2 deploy-record §1.2 注「属性存在但不可调用形态不兜底（真实 ORT session 不命中）」；P4-3 detection_sfx.py 比较处 wheel 升级复核面注释（只比对 providers[0]，本 wheel fallback 恒 [CPUExecutionProvider]，wrapper :541-577）；P4-4 DSH 已判可接受不动；P4-5 green log `EXIT_K Runtime=0` 排版歧义说明（deploy-record §2 注，不重生成证据）；P4-6 口径注明（§1.1/表行）；P4-7 parity 脚本跨 worktree 依赖注释（GPU-EP-1 基准行读自主 checkout）；P4-8 parity 脚本注释区分脚本门（同量级）与人工对表（逐数字一致）。

**Gate 复验**：全量回归 `1 failed, 1828 passed, 1 skipped`=基线 1823+5 新增等量递增（`raw/pytest-full-regression-r1fix.log`，HEAD=2356fb8f）；微基准重跑 verdict PASS（§1.1 新数字）。
