---
id: DOC-FIX-LOCK-CHANGED-STALE-COMMENTS
title: 两处过时「known planner gap」注释的最小 docs 修正（DIAG-002 遗留候选落地）
kind: docs-minor
status: in_progress
approval: released_by_codex_proxy
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness (non-author)
integrator: Codex（代行，用户全权授权）
depends_on: [DIAG-M2-LOCK-CHANGED-REPRO-002]
base_commit: d1c56e5d8399e8f03550528c47ee9aa3b34d0fcf
branch: agent/zcode/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS
worktree: G:/CODEX/New Manga.worktrees/DOC-FIX-STALE-COMMENTS-zcode
integration_commit: null
delivery_head: null
---

# DOC-FIX-LOCK-CHANGED-STALE-COMMENTS：过时「known planner gap」注释最小修正

## 来源与目标

[DIAG-M2-LOCK-CHANGED-REPRO-002](DIAG-M2-LOCK-CHANGED-REPRO-002.md)（`done` @`1faf6c1b`）遗留候选的落地：两处注释仍宣称 regionless detect→backfill 链存在「known production planner gap」，而该缺口已由 [M2-P1](M2-P1.md)（merge `a174fb9c`）修复、并经 DIAG-002 实证核实关闭（`done` @`1faf6c1b`）。用户 2026-09-30 指令批准释放本最小修正。

**目标（可观察交付）**：仅修改两处注释/docstring 文本，逻辑零改动，并有机器可核的「零逻辑变化」证据。

1. `src/bootstrap/acceptance_bridge.py` `method_run_pipeline` docstring：句子「…and the region-less detect→backfill chain has a known production planner gap (Handoff §风险与遗留) that must not be reported as covered by this Task.」→ 更新为已修复+已核实口径。**保留**「The ``resume_blocked`` branch … is NOT exercised by the released acceptance evidence (DSH r1 F-007)」——该证据边界陈述至今真实，不动。
2. `experiments/M2-TA3-A/run_smoke.py:273` 行注释「`(real detect; ocr hits the known gap)`」→ 更新为已修复引用。
3. 与 [M2-TA3-A](M2-TA3-A.md) L-7 的关系：L-7 当时「登记不改」的裁量理由是「被提交脚本 == 产出证据脚本」锚定简洁性；本 Task 以**注释-only diff 证明**（逻辑字节码零变化）处置 L-7 ①，M2-TA3-A 的既有证据由其 provenance（dc2b9aca 锚定）继续可追溯，不受注释演进展影响。M2-TA3-A.md 正文不改写，效力以本 Task+STATUS 为准。

## Acceptance Criteria

- [x] **AC1（注释-only diff 证明）**：`git diff` 变化行全部为注释/docstring 文本（无任何代码行增删改）。证据：[ac1-comment-only-diff.log](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/ac1-comment-only-diff.log)。
- [x] **AC2（零逻辑变化的机器证据）**：①`py_compile` 双版通过；②字节码探针 `co_code` 逐对象全等（`acceptance_bridge.py` 37 对象 + `run_smoke.py` 15 对象 = 52 全等，`BYTECODE-PROBE: ALL-EQUAL`）；③`test_acceptance_loop.py` **4 passed** EXIT=0。证据：[ac2-bytecode-probe.log](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/ac2-bytecode-probe.log)、[ac2-acceptance-regression.log](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/ac2-acceptance-regression.log)。
- [x] **AC3（文本正确性）**：新注释与 DIAG-002 结论一致（已由 M2-P1 @`a174fb9c` 修复、DIAG-002 @`1faf6c1b` 核实：修复前锚点复现/HEAD 不复现）；保留 M2-AC1 验收证据边界（resume_blocked 分支 NOT exercised，至今真实）；推断限定未引入注释。
- [x] **AC4（范围纪律）**：产品面仅 2 个目标文件；`git diff --check` EXIT=0。证据：[ac4-scope-proof.log](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/ac4-scope-proof.log)。

## 允许修改范围

- `src/bootstrap/acceptance_bridge.py`（**仅** `method_run_pipeline` docstring 文本行）
- `experiments/M2-TA3-A/run_smoke.py`（**仅** `:273` 注释行）
- `doc/tasks/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS.md`、`verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/**`、`doc/handoffs/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS-*.md`、`doc/reviews/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS-*`
- 导航面（STATUS/00_INDEX/tasks README）按协议 §3.6 仅状态与链接回填

## 禁止范围

- 任何代码行（含 docstring 之外的字符串字面量、类型注解、import、空行重排）零改动；`src/**` 其他文件；`experiments/M2-TA3-A/**` 其他文件（含同文件其他注释——L-7 ②③ 维持不改）；`tests/**`；契约。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| 注释-only diff（AC1） | `git diff 4ed3c044 -- <两文件>` | — | **executed**：变化行全为注释/docstring | [ac1-comment-only-diff.log](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/ac1-comment-only-diff.log) |
| 字节码探针（AC2） | `python` 探针：compile+递归 co_code 对比 | TASK-012-py312 venv | **executed**：52 code object 全等，ALL-EQUAL | [ac2-bytecode-probe.log](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/ac2-bytecode-probe.log) |
| 回归（AC2③） | `python -m pytest tests/m2_acceptance/test_acceptance_loop.py -q` | 同上（offscreen） | **executed**：4 passed | [ac2-acceptance-regression.log](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/ac2-acceptance-regression.log) |
| 范围（AC4） | `git diff --check`；name-status+意外路径 grep | — | **executed**：EXIT=0；意外路径零 | [ac4-scope-proof.log](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/ac4-scope-proof.log) |

## 依赖、风险与阻塞

- depends_on：`DIAG-M2-LOCK-CHANGED-REPRO-002`（done @`1faf6c1b`——结论来源）。
- 风险：`run_smoke.py` 属 M2-TA3-A 证据锚定面——以 AC1/AC2 的注释-only 证明处置（见 §来源与目标 3）。
- 无用户裁决依赖。

## 交付与运行记录

- **2026-09-30 release（代行 Codex，用户指令批准）**：`proposed → ready / DOC_FIX_LOCK_CHANGED_STALE_COMMENTS_RELEASED`。冻结：base=`d1c56e5d8399e8f03550528c47ee9aa3b34d0fcf`、branch=`agent/zcode/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS`、worktree=`G:/CODEX/New Manga.worktrees/DOC-FIX-STALE-COMMENTS-zcode`（release commit=`4ed3c044`）。Release evidence：[release-d1c56e5d](../../verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/release-d1c56e5d.md)。
- **2026-09-30 交付（Owner=ZCode，claim `74022cdc`）**：`in_progress → in_review`。两处注释修正 + 全套零逻辑证明（AC1-AC4 全 executed）。Handoff：[DOC-FIX-LOCK-CHANGED-STALE-COMMENTS-zcode-delivery-20260930](../handoffs/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS-zcode-delivery-20260930.md)。
- Review：尚无（待 DSH 非作者静态 Review）。实际测试：见上方测试表。
