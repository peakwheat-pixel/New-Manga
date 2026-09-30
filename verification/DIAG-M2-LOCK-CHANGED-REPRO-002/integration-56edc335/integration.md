# Integration record — DIAG-M2-LOCK-CHANGED-REPRO-002

- integrated: `done` @ merge `1faf6c1b`（parents `d69a3e1c` + `2c13530b`，--no-ff 无冲突）+ 集成修正 commit `56edc335`
- integration date: 2026-09-30 (Asia/Shanghai)
- integrator: 代行 Codex（ZCode，用户 2026-09-28/29/30 全权授权）；Owner=ZCode（另一会话侧交付链）；Reviewer=DeepSeek Harness（非作者，r1+r2）
- 性质：纯诊断 Task——零 `src/**`/`apps/**`/`tests/**`/`doc/contracts/**`/`requirements` 改动（[ac5-scope-proof-r2.log](../raw/ac5-scope-proof-r2.log) 禁改 grep EXIT=1 零命中）；缺陷确认后无需修复（已由 M2-P1 修复）。

## 交付链（Owner branch `agent/zcode/DIAG-M2-LOCK-CHANGED-REPRO-002`）

| commit | 内容 |
|---|---|
| `6cbeafe0` | claim（ready→in_progress） |
| `18975a7a` | r1 实验（v3 脚本）+ S1/S2 证据 |
| `57a83485` | r1 Task 回填 + Handoff |
| `8d2162c1` | r2 返修（v5 脚本+重跑证据+F-001/F-005/F-006 证据+r1 报告归档） |
| `145b3ed5` | r2 Handoff/Task 回填 |
| `fb36d21f` | generated diff log whitespace-only 规范化（文件内披露） |
| `2c13530b` | DSH r2 报告原字节归档（Owner 终 tip） |

## Review 轨迹（Reviewer=DSH 非作者，两轮均纯静态、沙箱无命令执行）

- r1：[approved_with_conditions](../../doc/reviews/DIAG-M2-LOCK-CHANGED-REPRO-002-57a83485-dsh-r1.md)（0×P0/P1、3×P2、4×P3、3×P4；被审 `57a83485`；原字节 SHA256=`8091fb05…`）
- r2：[approved_with_conditions](../../doc/reviews/DIAG-M2-LOCK-CHANGED-REPRO-002-fb36d21f-dsh-r2.md)（**0×P0/P1/P2 新发现**，F-001~F-010 实质全数闭合，「准予集成」；被审 tip `fb36d21f`；原字节 SHA256=`8153f70d…`）
- r2 集成前条件闭合：N-1=集成 tip 全区间范围自查 [ac5-scope-proof-r2.log](../raw/ac5-scope-proof-r2.log)（name-status 17 文件全允许、diff --check EXIT=0、禁改零命中）；N-2=delivery_head/提交链回填；N-3=Task 死链修正；N-4=归因注修正（均标注集成方修正，`56edc335`）。

## 集成复跑（merge 后，integrator 独立执行）

| 项 | 命令/锚点 | 结果 | EXIT | 证据 |
|---|---|---|---|---|
| S1 主判定（tip 绑定） | repro_two_phase.py `--label s1-integration-replay --expect not-reproduced` @main | verdict=`NOT_REPRODUCED`；run1 全链 9 步 COMPLETED、run2/run3 COMPLETED | 0 | [s1-integration-replay-run.log](../raw/s1-integration-replay-run.log)、[verdict](../raw/s1-integration-replay-verdict.json) |
| S2 反证（锚点 `d268a170`） | 同脚本 `--expect reproduced`（脚本字节=仓库 blob `d71825ff…`，与 Owner 证据同哈希） | verdict=`REPRODUCED`；run1 ocr `failed LOCK_CHANGED`（零写 revisions=1）、run4 retry 驱动 region 链 8 步 COMPLETED（自愈复现） | 0 | [s2-integration-replay-run.log](../raw/s2-integration-replay-run.log)、[verdict](../raw/s2-integration-replay-verdict.json) |
| 范围/whitespace | `git diff --check d69a3e1c..56edc335` + 禁改 grep | 空 / 零命中 | 0 | [ac5-scope-proof-r2.log](../raw/ac5-scope-proof-r2.log) |

脚本字节披露：主 worktree 工作区文件经 `core.autocrlf` checkout 为 CRLF（sha256 `8cccafb1…`）；仓库 blob 与 Owner 运行时字节均为 LF（sha256 `d71825ff…`=00-provenance.txt 记录值）；S2 集成复跑从 `git show HEAD:` 取 blob 原字节执行，与 Owner 证据同源。

## 结论（Task 终态登记）

**AC4 四选一=③「已由 M2-P1 修复」变体**：M2-AC1 handoff §风险与遗留登记的 regionless detect→backfill→ocr 链 `LOCK_CHANGED` 缺口——真实存在过（S2 修复前锚点复现+诊断三特征+零写取证齐备）、机制上非 mock-detect 特有（归因 diff：区间 src/ 变更 3 文件中本链相关唯一= M2-P1 重绑；真 docTR 修复前触发为推断未实测）、非「未修」时序条件性（retry/重规划自愈实证）、**已由 [M2-P1](../../../doc/tasks/M2-P1.md)（merge `a174fb9c`）修复**。M2-TA3-A 未复现根因=其运行于修复后 main。**M2-TA3-A L-1 = 已核实关闭**（登记处置：M2-TA3-A.md 原文不改写，效力以本记录+STATUS 为准）；M2-AC1 handoff 原文不改写（历史忠实记录）。无需新修复 Task。

## 遗留（均 cosmetic 候选，不阻塞）

- `src/bootstrap/acceptance_bridge.py:338-340` 与 `experiments/M2-TA3-A/run_smoke.py:273` 过时注释（维持不改、引用本 Task 结论；随未来触碰相应文件的 Task 顺手更新或最小 docs 修正释放）。
- DSH r2 N-5（P4 可选硬化：REPRODUCED 判据增补三特征合取/零写计数入 log/provenance hash 行格式）——不影响结论，并入未来触碰。
- 真 docTR × 修复前锚点组合未测（推断限定已写入 Task AC4/Handoff）。

Owner branch/worktree 保留于 `2c13530b`（`G:/CODEX/New Manga.worktrees/DIAG-LOCK-CHANGED-REPRO-002-zcode`）。
