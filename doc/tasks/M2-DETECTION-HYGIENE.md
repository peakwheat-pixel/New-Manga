---
id: M2-DETECTION-HYGIENE
title: "检测/调度面 hygiene 一揽子（TILING R1/R3 env-parse 加固 + BACKFILL N1 except 收窄 + SETTINGS-IPC R7/R8 文档口径）"
kind: feature
status: in_review  # r1 有条件通过（5×P2）→ 返修中：R1 lazy 拆分/R2 桩重建（post-R3 语义）/R3 :800 包护/R4 行为级红态归档/R5 commandSurface 补 IPC1 对/R6 handoff

delivery_head: PLACEHOLDER
approval: orchestrator_next_release_2026-10-02
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-DETECT-WEBTOON-TILING, M2-TASKS-BACKFILL-MULTIREGION, M2-SETTINGS-IPC-CHANNEL]
base_commit: 24a89d7d
branch: agent/zcode/M2-DETECTION-HYGIENE
worktree: G:/CODEX/New Manga.worktrees/M2-DETECTION-HYGIENE-zcode
---

# M2-DETECTION-HYGIENE：检测/调度面 hygiene 一揽子

## 背景（三 Task review 的 P3/P4 紧邻 follow-up 打包）

三处已登记的小体量加固，打包为一揽子 hygiene（避免碎片 Task）：

1. **TILING R1/R3**（DSH r1 P3）：`detection_manga.py` `_tiling_config()` 的 env 解析——R1=非法值裸 `ValueError` 打破「普通页零变化」（env 非法值在普通页也 raise）；R3=空/空白 env 值静默回落默认与 never-silent-default 矛盾。修法：空/空白→显式 typed（或明确登记回落语义+注释）；非法值→带 env 名的 typed 错误（沿用 SFX conf 先例语义）且**仅在 tiling 配置被实际读取路径上 fail**（普通页零变化主张恢复）。
2. **BACKFILL N1**（DSH r2 P4）：`service.py` backfill 的 `except PipelineError` 收窄为 `error.code in {"TARGET_DELETED", "TARGET_NOT_FOUND"}` + 补一条测试（monkeypatch catalog 抛错⇒该 region 跳过、run COMPLETED、首 region 不受影响）。
3. **SETTINGS-IPC R7/R8**（DSH r1 P4）：`commandSurface.test.ts` 注释/测试名陈旧更正；`main.rs` dispatch 注释计数更正。R5（组件交互 e2e）/R6（mockDom 去重）登记不做（需新 e2e 栈/重构，另行评估）。

## 交付（AC）

1. **AC1**：上述 1-3 逐项落地；每项先红后绿或登记（文档类除外）。
2. **AC2**：全量回归——pytest 三套件（576+1sk 基线+新增）、cargo/vitest 不回退。
3. **AC3**：Task/Handoff 回填；逐项登记「来源 Review 条目」。

## 允许修改面

`src/infrastructure/providers/detection_manga.py`、`src/application/tasks/service.py`、`apps/desktop/src-tauri/src/main.rs`、`apps/desktop/frontend/src/resourceChannel/commandSurface.test.ts`、`tests/**`（相关）、`verification/M2-DETECTION-HYGIENE/**`、Task/Handoff。

## 禁改面

其他 provider/模块、`src/ports/**`、`src/bootstrap/**`、`doc/contracts/**`、`packaging/**`、`apps/**` 其余、`doc/STATUS.md`。

## 纪律

- 行为零变化（除加固语义本身）：普通页 tiling 触发判定、backfill 正常路径、settings 命令行为全部不变。
- 基线：main 三套件 603+1skipped 0 failed。
