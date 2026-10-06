---
task_id: M2-SFX-EPFAIL-AUDIT-1
author: ZCode
recipient: Codex（集成）/ DeepSeek Harness（非作者 Review）
base_commit: d298ecd0（释放登记 tip：user 2026-10-04 批准进行2，非阻塞候选①释出）
delivery_head: 2bed03d0（最终证据锚：verify commit=实测+parity+回归证据+部署记录；其后 docs commit 仅文档，tip 以 git log 分支头为准）
status: delivered，待 DSH 非作者 Review
---

# Handoff：M2-SFX-EPFAIL-AUDIT-1 — SFX 推理 run-time EPFail 通道审计

## 交付结果

AC1-AC4 全 PASS。GPU-EP-1 deploy-record §1.3（r2 N-P3-1）登记的「ORT 包装层 run() 期 EPFail 内部静默重跑 CPU」未审计通道由本 Task 闭合（注记声明，历史文件零改动）：

- **机制面**（生产 wheel onnxruntime-directml 1.24.4 源码实证）：wrapper `InferenceSession.run`（:291-305）捕获 `C.EPFail` → `set_providers(_fallback_providers)`（dml 请求=CPU 列表）→ `disable_fallback()`（每 session 一次）→ CPU 重跑并**正常返回**——调用方无异常，仅 stdout 两行（frozen 面丢弃，禁依赖）。
- **审计设计（AC1，Owner 裁量，实测前置）**：每 detect 一次 `session.get_providers()` 读回（wrapper :214-216 `return self._providers`，**纯 Python 属性读，实测 0.0303/0.0305 μs**（cpu/dml），占 GPU-EP-1 KO 基准 1.106-1.211 s/页的 1% 时延预算 ~2.8e-6%——GPU-EP-1 时「逐 detect 复读代价高」的判断经实测不成立）；首 provider 与构建期 effective 比对：稳态零追加（options 与审计前逐字节一致），变化才追加单一新键 `sfx_ep_runtime_check`（`"session providers changed at run time: <built> -> <now> (ORT wrapper run-time EPFail fallback)"`）。静默成功主形态当页即观测；重跑亦失败走既有 typed 失败（该页无 options），session providers 状态持续→下一页成功 detect 观测。
- **硬约束全守住**：三键（device/sfx_ep/sfx_ep_fallback）构建期语义与写入时点逐字不变（新键纯追加）；`NEWMANGA_SFX_EP` 解析与 fail-fast 时序零改动；零 stdout 依赖；`_sfx_boxes`/`_detect_tiles` 的 run 调用零改动；禁改面（contracts/apps/packaging/requirements.txt/其他 provider/STATUS/REBASELINE_PLAN）零 diff。
- 变更路径：`src/infrastructure/providers/detection_sfx.py`（`_runtime_ep_audit` + detect options 追加点 + EP 段注释闭合登记）、`tests/providers/test_detection_sfx.py`（+3 用例）、`experiments/M2-SFX-EPFAIL-AUDIT-1/**`（2 脚本）、`verification/M2-SFX-EPFAIL-AUDIT-1/**`（部署记录+5 证据文件）、`doc/tasks/`、`doc/handoffs/`。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 设计实测（get_providers 耗时+fallback 可观测性+1% 硬门） | `experiments/M2-SFX-EPFAIL-AUDIT-1/measure_get_providers_cost.py`（生产 venv + v2b pin 944e8114；warmup 1e4 + 5 轮×1e6 次/face；wrapper EPFail 分支 `set_providers(['CPUExecutionProvider'])` 原样重放） | onnxruntime-directml 1.24.4，HEAD=`d298ecd0`（基线，设计实测先于实现） | **PASS**（0.0303/0.0305 μs；重放后读回 `[Dml,CPU]→[CPU]`；1% 预算占比 2.8e-6%） | `verification/M2-SFX-EPFAIL-AUDIT-1/raw/epfail-audit-get-providers-cost.{json,log}` |
| AC2 红（对基线实现跑新测试） | `python -m pytest tests/providers/test_detection_sfx.py -k runtime -q` | HEAD=`a336bd41`（claim，实现 stash 隔离） | **1 failed, 3 passed**（failed=核心用例 `KeyError: 'sfx_ep_runtime_check'`；2 辅助用例按构造基线通过） | `verification/M2-SFX-EPFAIL-AUDIT-1/raw/tests-epfail-red.log` |
| AC2 绿（实现后） | 同上 `-k runtime` + 全文件 `-q` | HEAD=`0f4702d0`（impl） | **PASS**（新用例 4 passed；全文件 82 passed=79 基线+3 新增） | `verification/M2-SFX-EPFAIL-AUDIT-1/raw/tests-epfail-green.log` |
| AC3 parity 抽 1 页复核（KO pre-k01，690x62133 tile） | `experiments/M2-SFX-EPFAIL-AUDIT-1/verify_epfail_audit_parity.py`（双 EP face 走生产 env 门，diff_preds/match_gt 沿 GPU-EP-1 verbatim） | HEAD=`0afb22dd`，v2b pin 944e8114 | **PASS**（与 GPU-EP-1 基准行逐数字一致：dconf 1e-06/dxyxy 0.0001px/gate_flips 0/derived 2/2+npd 5/48 matched set equal；真实稳态两 face 零新键三键照常；dml 1.122s 落基准区间 0.333-2.325，directional） | `verification/M2-SFX-EPFAIL-AUDIT-1/raw/epfail-audit-parity-prek01.{json,log}` |
| AC3 全量回归 | `python -m pytest tests -q`（worktree 根） | HEAD=`0afb22dd`，生产 venv `T1.1.1-impl-py312` | **PASS**（`1 failed, 1826 passed, 1 skipped`=基线 1823+3 新增+1 skipped+test_catalog 既有 BASELINE_FAILURE，等量递增） | `verification/M2-SFX-EPFAIL-AUDIT-1/raw/pytest-full-regression.log` |
| AC4 文档 | 部署记录+Task 回填+Handoff | — | **PASS** | `verification/M2-SFX-EPFAIL-AUDIT-1/deploy-record.md`、`doc/tasks/M2-SFX-EPFAIL-AUDIT-1.md`、本文件 |
| 实机真实 EPFail 触发（GPU 掉卡实测） | NOT_RUN——探测面可见性由 wrapper 同 API 调用重放（`raw/epfail-audit-get-providers-cost.json` runtime_epfail_fallback_observability）+stub 形态单测覆盖；与 GPU-EP-1 验证矩阵②同一诚实口径 | — | **NOT_RUN** | deploy-record §5.4 |

## 接收方式

- 分支 `agent/zcode/M2-SFX-EPFAIL-AUDIT-1` @ worktree `G:/CODEX/New Manga.worktrees/M2-SFX-EPFAIL-AUDIT-1-zcode`；base=`d298ecd0`，delivery_head=`2bed03d0`（docs commit 为其后继，tip 以分支头为准）。
- 复现：生产 venv `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe`；EP 单测 `python -m pytest tests/providers/test_detection_sfx.py -k "runtime or ep_" -q`；回归 `python -m pytest tests -q`（worktree 根，~2.5 min）；权重 `G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx`（不入 Git）。
- Review 检查建议：①`_runtime_ep_audit` 与构建期读回共用同一 `get_providers()` 面（session 无面则跳过——裸测试替身形态，真实 ORT session 恒有）；②稳态零追加是全量回归等量递增的构造前提（`test_runtime_steady_state_adds_no_runtime_key` 钉住）；③落选设计理由见部署记录 §1.4。

## 下一任务建议（必填）

- Task ID / 标题：M2-SFX-EPFAIL-AUDIT-1 r1 独立 Review（DSH 非作者）
- 推荐 Agent / Reviewer：DeepSeek Harness（Owner=ZCode 非作者隔离成立）
- 推荐原因与前置依赖：本 Task 交付完成、status=in_review 停写；依赖=本分支 delivery_head=`2bed03d0`（docs commit 为其后继）；无新授权需求。
- Recovery point：`G:/CODEX/New Manga.worktrees/M2-SFX-EPFAIL-AUDIT-1-zcode`，branch `agent/zcode/M2-SFX-EPFAIL-AUDIT-1`，base `d298ecd0`，delivery_head=`2bed03d0`（见 frontmatter）。
- 允许修改路径：`doc/reviews/M2-SFX-EPFAIL-AUDIT-1-<head>-dsh-r1.md`（新建）。
- 禁止范围与新增授权条件：零 src/零 tests 修改；结论写 review 文件，status 变更与集成由 Codex 处置。
- 交付物：Review 报告（AC1-AC4 判定+证据核对+P 编号 findings）。
- 验证命令、环境与完成 Gate：上表命令可在 review worktree 复跑；Gate=Review 报告落档、判定明确（approved / changes_requested）。
- 可直接转发给 Agent 的指令：「对 M2-SFX-EPFAIL-AUDIT-1 做非作者 r1 Review：worktree `G:/CODEX/New Manga.worktrees/M2-SFX-EPFAIL-AUDIT-1-zcode` 分支 `agent/zcode/M2-SFX-EPFAIL-AUDIT-1`，delivery_head=`2bed03d0`。合同=`doc/tasks/M2-SFX-EPFAIL-AUDIT-1.md`，Owner 报告=`verification/M2-SFX-EPFAIL-AUDIT-1/deploy-record.md`，Handoff=`doc/handoffs/M2-SFX-EPFAIL-AUDIT-1-zcode-20261004.md`。核对 AC1 设计与硬约束（三键语义/时点、NEWMANGA_SFX_EP 时序、零 stdout、1% 时延门）、AC2 红绿证据、AC3 parity 与回归等量递增、AC4 文档闭合声明；结论写 `doc/reviews/M2-SFX-EPFAIL-AUDIT-1-<head>-dsh-r1.md`，不改 src/tests。」

## 风险与遗留

- `sfx_ep_runtime_check` 的「wrapper run-time EPFail fallback」归因依赖：本仓代码从不调用 `set_providers`，wrapper 仅在 run() EPFail 分支调用它（onnxruntime-directml 1.24.4 内成立）——wheel 升级时与既有 EP 语义同面复核。
- wrapper fallback 每 session 仅一次（`disable_fallback`）；第二次 EPFail 异常传播=既有 typed detect 失败路径（GPU-EP-1 交付语义，非本 Task 变更）。
- 稳态读回为每页新增一次 Python 属性读+比对（实测 0.03 μs 级）——性能影响登记为可忽略，无页级 perf 门回归需求。
- GPU-EP-1 deploy-record §1.3 历史文件零改动；闭合声明仅存于本 Task 部署记录 §0（集成时如需在 STATUS/集成说明同步闭合口径，属 Codex 收口面）。
