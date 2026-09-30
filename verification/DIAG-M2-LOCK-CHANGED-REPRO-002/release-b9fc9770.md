# Release evidence — DIAG-M2-LOCK-CHANGED-REPRO-002

- released: `ready / DIAG_M2_LOCK_CHANGED_REPRO_002_RELEASED`
- release date: 2026-09-30 (Asia/Shanghai)
- release authority: 代行 Codex（用户 2026-09-28/29/30 全权授权 ZCode 代行 Codex Lead/Integrator）；来源=用户指令「新建缺陷核实 Task『DIAG-M2-LOCK-CHANGED-REPRO-002』」+ [M2-TA3-A](../../doc/tasks/M2-TA3-A.md) L-1 候选 + STATUS `Planned next` 登记的「L-1 LOCK_CHANGED 已登记缺口以 mock detect 复现核实的缺陷 Task」。
- base (frozen): `b9fc977017f101a9731d4cb4bf5d270cc6f65d62`（main @ M2-TA3-A 收口 commit）
- branch: `agent/zcode/DIAG-M2-LOCK-CHANGED-REPRO-002`
- worktree: `G:/CODEX/New Manga.worktrees/DIAG-LOCK-CHANGED-REPRO-002-zcode`（从 release commit 检出）
- owner: ZCode；reviewer: DeepSeek Harness（非作者）；integrator: 代行 Codex。

## 冻结范围

- 允许：`experiments/DIAG-M2-LOCK-CHANGED-REPRO-002/**`、`verification/DIAG-M2-LOCK-CHANGED-REPRO-002/**`、本 Task 文件、`doc/handoffs/DIAG-M2-LOCK-CHANGED-REPRO-002-*.md`、`doc/reviews/DIAG-M2-LOCK-CHANGED-REPRO-002-*`；元数据导航面（STATUS/00_INDEX/tasks README）按协议 §3.6 仅状态与链接回填。
- 禁止：`src/**`、`apps/**`、`tests/**`、`doc/contracts/**`、`requirements*.txt`、既有实验资产（`experiments/M2-TA3-A/**` 等）。**缺陷确认后修复另行释放，本 Task 零生产代码改动。**

## 释放时已核实的锚点事实

| 锚点 | commit | 角色 |
|---|---|---|
| M2-AC1 handoff 登记 | `aaf21a13`（2026-09-28 11:06） | 被核实登记的原始写作点（缺陷未修时） |
| 修复前反证锚点（S2） | `d268a170`（2026-09-28 16:27，merge `a174fb9c` 的 main 侧 parent） | M2-P1 修复进入 main 前最后一个 main commit；已验证含 `acceptance_bridge`（`synthetic_page_png` 存在） |
| M2-P1 修复集成 | `a174fb9c`（2026-09-28 16:27） | `_backfill_detected_regions` 同时重绑 `target_id`+`region_id`（HEAD 现状已在 `src/application/tasks/service.py:952-954` 核实） |
| M2-TA3-A 集成 | `5dc69d16`（2026-09-30） | L-1 登记来源：真 docTR 5 case 未复现 |

## 验收命令环境

- venv: `G:/CODEX/New Manga.task-envs/TASK-012-py312`（Python 3.12.3，PySide6 6.11.2，QT offscreen）
- mock detect 注册路径（任务指定）：`assemble_core_services(mock_local_providers=True)`（经 `bootstrap.acceptance_bridge.assemble_acceptance_core` 正式封装）
