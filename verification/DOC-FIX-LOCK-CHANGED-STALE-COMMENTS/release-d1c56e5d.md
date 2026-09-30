# Release evidence — DOC-FIX-LOCK-CHANGED-STALE-COMMENTS

- released: `ready / DOC_FIX_LOCK_CHANGED_STALE_COMMENTS_RELEASED`
- release date: 2026-09-30 (Asia/Shanghai)
- release authority: 用户指令（转发本 Task 可执行指令=批准释放）；代行 Codex 登记。来源=[DIAG-M2-LOCK-CHANGED-REPRO-002](../../doc/tasks/DIAG-M2-LOCK-CHANGED-REPRO-002.md) 遗留候选（其集成记录 §遗留）。
- base (frozen): `d1c56e5d8399e8f03550528c47ee9aa3b34d0fcf`（main @ DIAG-002 收口）
- branch: `agent/zcode/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS`
- worktree: `G:/CODEX/New Manga.worktrees/DOC-FIX-STALE-COMMENTS-zcode`
- owner: ZCode；reviewer: DeepSeek Harness（非作者）；integrator: 代行 Codex。

## 冻结范围

- 允许：`src/bootstrap/acceptance_bridge.py` 仅 `method_run_pipeline` docstring 文本行、`experiments/M2-TA3-A/run_smoke.py` 仅 `:273` 注释行、本 Task/verification/handoff/reviews/导航面回填。
- 禁止：任何代码行变更、`src/**` 其他文件、`experiments/M2-TA3-A/**` 其他文件、`tests/**`、契约。零逻辑改动为硬约束（字节码 `co_code` 逐对象全等为集成前置）。

## 目标文本修正依据

两处「known production planner gap」/「ocr hits the known gap」表述过时：缺口已由 M2-P1（merge `a174fb9c`）修复，经 [DIAG-M2-LOCK-CHANGED-REPRO-002](../../doc/tasks/DIAG-M2-LOCK-CHANGED-REPRO-002.md)（`done` @`1faf6c1b`，DSH r2 0×P0/P1/P2）以 mock detect 两段式复现核实（修复前红/修复后绿+retry 自愈实证）。
