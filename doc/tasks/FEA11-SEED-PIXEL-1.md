---
id: FEA11-SEED-PIXEL-1
title: 种子旧侧条目补 pixel 画像 —— FullSyncChain 转绿（12/1）
kind: fix
governance_version: 3
status: done
disposition: "FEA11-FULLSYNC-TRIAGE-1 的正解：让种子带 pixel 画像，使 changed 可被观测"
approval: DSH 2026-11-15
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - FEA11-FULLSYNC-TRIAGE-1
base_commit: a482b9f36
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA11-SEED-PIXEL-1
allowed_paths:
  - doc/tasks/FEA11-SEED-PIXEL-1.md
  - doc/reviews/FEA11-SEED-PIXEL-1-*.md
  - doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/FEA11-SEED-PIXEL-1/**
  - tests/fea11/**
---

# FEA11-SEED-PIXEL-1

## 交付

- `tests/fea11/conftest.py`：`add_source_tree` 新增 `pixel_profiles` 参数；`source_entries` INSERT 补上
  `pixel_digest` / `pixel_digest_algorithm` / `orientation` / `decoder_name` / `decoder_version` /
  `decoder_params_json` 六列。**向后兼容**（不传时行为不变）。
- `tests/fea11/support/ipc_seed.py`：用**生产解码器** `_decode_pixel_profile` 算真实画像；
  `budget.max_decode_bytes=0` 跳过预算检查；**拿不到画像就 `SystemExit`**，不静默降级。

## 结果

| 项 | 前 | 后 |
|---|---|---|
| `Fea11SourceIpcTests.FullSyncChain_…` | FAIL | **PASS** |
| 三类 13 个合计 | 11/2 | **12/1** |

## 判别力

注释掉 `pixel_profiles=_old_pixel_profiles` 后该测试**重新变红**（`changed page` 断言），已还原，`PROBE`=0。

## ★ 上一轮推断被推翻

上一轮 `FEA11-FULLSYNC-TRIAGE-1` 曾**推断** `Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_…`
同因（已标注"推断而非实测"）。本轮实测证明**不同因**：

```
SourceAccessException : SOURCE_ENTRY_MISSING
  at SourceReadCoordinator.DescribeContainer line 382
```

失败在**读容器**阶段，与 pixel 无关；pixel 修复**没有**让它转绿。

**教训（第二次）**：同族失败不能按错误文本相似推断同因。

## 未做

- `Fea11Residual4AIpcTests` 的 `SOURCE_ENTRY_MISSING` 未归因。
