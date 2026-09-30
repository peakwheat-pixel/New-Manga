---
task_id: DOC-FIX-LOCK-CHANGED-STALE-COMMENTS
author: ZCode (Owner)
recipient: DeepSeek Harness (non-author Review) → Codex proxy (Integrator)
base_commit: d1c56e5d8399e8f03550528c47ee9aa3b34d0fcf
delivery_head: 74022cdc + 本 Handoff 文档提交（实现/证据见 worktree tip）
status: delivered_awaiting_review
---

# Handoff：DOC-FIX-LOCK-CHANGED-STALE-COMMENTS — 两处过时「known planner gap」注释最小修正

## 交付结果

仅修改两处注释/docstring 文本（DIAG-002 遗留候选落地，用户 2026-09-30 指令批准）：

1. `src/bootstrap/acceptance_bridge.py` `method_run_pipeline` docstring：「…has a known production planner gap (Handoff §风险与遗留) that must not be reported as covered by this Task.」→「The historical region-less detect→backfill ``LOCK_CHANGED`` gap … was fixed by M2-P1 (merge ``a174fb9c``) and verified closed by DIAG-M2-LOCK-CHANGED-REPRO-002 (merge ``1faf6c1b``: pre-fix anchor reproduces, HEAD does not).」；**保留** resume_blocked 分支「NOT exercised by the released acceptance evidence (DSH r1 F-007)」（该证据边界陈述至今真实）。
2. `experiments/M2-TA3-A/run_smoke.py:273` 行注释「`(real detect; ocr hits the known gap)`」→「`(real detect; page-level chain; the historical LOCK_CHANGED planner gap is FIXED by M2-P1 @a174fb9c, verified by DIAG-M2-LOCK-CHANGED-REPRO-002 @1faf6c1b)`」。

**指令流零变化证明（AC2，DSH P2-2 限定口径）**：字节码探针（已入库 [bytecode_probe.py](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/bytecode_probe.py)，运行记录 [ac2-bytecode-probe-r2.log](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/ac2-bytecode-probe-r2.log) 带头+EXIT）对两文件改前（`4ed3c044` blob）vs 改后分别 `compile()` 并递归对比全部代码对象 `co_code`——37+15=**52 全等**。**口径限定**：`co_code` 只证明指令流零变化；`co_consts`（本 Task docstring 变更所在维度，属预期差异）、`co_names`、行号信息不在比较面。完整零逻辑结论由 **AC1 注释-only diff + 本探针**共同支撑。回归：`test_acceptance_loop.py` **4 passed** EXIT=0。

与 M2-TA3-A L-7 的关系（DSH P2-1 限定口径）：L-7 ① 由注释-only diff + 指令流全等处置——dc2b9aca pin 仍为有效历史标识、行为等价由 AC1/AC2 支撑；但 **M2-TA3-A provenance 的字节级 sha256 自检在 main/tip 上不再全绿**（run_smoke.py `f1b5976d…`→`30d55acd…`，一行 FAILED 属预期），字节级 15/15 须在其交付 worktree 复算——详见 [00-provenance-note.txt](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/00-provenance-note.txt)；集成记录同步此口径。L-7 ②③ 维持不改。

## 提交链（branch `agent/zcode/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS`，worktree `G:/CODEX/New Manga.worktrees/DOC-FIX-STALE-COMMENTS-zcode`）

| commit | 内容 |
|---|---|
| `74022cdc` | claim：Task `ready → in_progress` |
| `65f0facb` | 实现（两处注释）+ AC1-AC4 证据 |
| `1dd30dc7` | 本 Handoff 首版 |
| `768a0933` | generated diff log whitespace-only 规范化（文件内披露）=r1 被审 tip |
| （本轮） | DSH 条件返修：探针脚本入库+重跑 r2 log、00-provenance-note、ac4-r2、措辞/元数据回填 |

证据捕获时点披露：各 log 的 shell 头记录 `worktree @ 74022cdc`（实现后、提交前）；提交链随后成型。范围证据：r1 [ac4-scope-proof.log](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/ac4-scope-proof.log)（当时仅已提交 range）、r2 [ac4-scope-proof-r2.log](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/ac4-scope-proof-r2.log)（tip 全量未过滤枚举，DSH P3-3 闭合）。

## AC 对照

| AC | 结果 | 证据 |
|---|---|---|
| AC1 注释-only diff | **满足** | [ac1-comment-only-diff.log](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/ac1-comment-only-diff.log) |
| AC2 零逻辑机器证明 | **满足**（52 co_code 全等 + py_compile + 4 passed） | [ac2-bytecode-probe.log](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/ac2-bytecode-probe.log)、[ac2-acceptance-regression.log](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/ac2-acceptance-regression.log) |
| AC3 文本正确性 | **满足**（M2-P1 @`a174fb9c` 修复、DIAG-002 @`1faf6c1b` 核实；证据边界保留；推断限定未入注释） | 两文件 diff（AC1 log） |
| AC4 范围纪律 | **满足** | [ac4-scope-proof.log](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/ac4-scope-proof.log) |

## 实际测试命令与结果

环境：Git Bash (win32)；venv `G:/CODEX/New Manga.task-envs/TASK-012-py312`（Py3.12.3+PySide6 6.11.2 offscreen）。

| 命令 | 结果 | EXIT |
|---|---|---|
| 字节码探针（compile+递归 co_code 对比，见 ac2 log 头部内嵌脚本） | 52 objects ALL-EQUAL | 0 |
| `python -m pytest tests/m2_acceptance/test_acceptance_loop.py -q` | 4 passed in 3.06s | 0 |
| `git diff --check 4ed3c044` | 空 | 0 |

**未跑项（如实）**：`run_smoke.py` 真实 smoke 重跑（需 docTR 权重+资产；本 Task 字节码全等已证明逻辑零变化，重跑无增量信息）；全仓回归（两文件改动面仅注释，`acceptance_bridge` 消费方 4 passed 已覆盖运行行为）。

## 风险与遗留

- 无。M2-TA3-A L-7 ②③ 维持登记不改；DIAG-002 其余遗留不变。

## 启动/复现方式

```bash
cd "G:/CODEX/New Manga.worktrees/DOC-FIX-STALE-COMMENTS-zcode"
git diff 4ed3c044 -- src/bootstrap/acceptance_bridge.py experiments/M2-TA3-A/run_smoke.py
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/bytecode_probe.py  # EXIT=0
```

## 下一接收者

DeepSeek Harness（非作者静态 Review，base=`d1c56e5d`、release=`4ed3c044`、被审=分支 tip）→ 代行 Codex 集成。

## 可直接转发给 Reviewer 的指令

```
致 DeepSeek Harness（非作者 Reviewer）：对 DOC-FIX-LOCK-CHANGED-STALE-COMMENTS 执行独立静态 Review。
仓库 G:/CODEX/New Manga，branch agent/zcode/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS，worktree
G:/CODEX/New Manga.worktrees/DOC-FIX-STALE-COMMENTS-zcode，base=d1c56e5d，release commit=4ed3c044，
被审=分支 tip。任务文件 doc/tasks/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS.md；Owner Handoff
doc/handoffs/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS-zcode-delivery-20260930.md；证据
verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/（AC1 diff/AC2 字节码探针+回归/AC4 范围）。
重点复核：(1) AC1 diff 变化行是否全部为注释/docstring 文本、无任何代码行变化；
(2) 新注释事实正确性——M2-P1 merge a174fb9c 修复、DIAG-M2-LOCK-CHANGED-REPRO-002 merge 1faf6c1b
核实关闭（对照 doc/tasks/DIAG-M2-LOCK-CHANGED-REPRO-002.md 与 STATUS checkpoint）；
(3) 保留句「NOT exercised by the released acceptance evidence (DSH r1 F-007)」是否仍真实；
(4) 字节码探针方法有效性（docstring/注释不进 co_code）与 52 对象全等结论；(5) L-7 ①处置与
M2-TA3-A 锚定关系是否成立。沙箱受限可静态 Review。报告按 REVIEW 模板落 doc/reviews/，
结论 approved / changes_requested + 逐条 P0-P4。
```
