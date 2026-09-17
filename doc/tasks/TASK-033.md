---
id: TASK-033
title: 完整链收口：Color / Term Extract / Render handler
kind: implementation
status: proposed
approval: pending_user_review
suggested_owner: ZCode
owner: null
reviewer: null
depends_on: [TASK-010, TASK-014, TASK-019]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-033：完整链收口（Color / Term Extract / Render handler）

**PROPOSED（未释放）**：需用户批准释放；未释放前不得实施。Codex 已完成范围裁决（见「范围裁决」），释放时由 Codex 指定实际 owner 与非作者 reviewer。

## 来源与目标

- 来源：D08 §AC-RFULL-001 [P0] 要求完整链 `OCR → Color → Term Extract → Translate → Segment → Mask Refine → Inpaint → Render → Save`；TASK-019 的 R-2 / F-2 已确认缺失 `color`/`term_extract`/`render` 三个 handler，且 `render` 在**规划阶段**即 `BLOCKED(missing_clean_artifact)`。
- 目标：把这三步按已冻结的 pipeline seam 接线（provider/handler 侧），使完整链在规划与执行层面可端到端跑通；**真实模型质量、成本、时延仍按 `BLOCKED`/`NOT_RUN` 交付**，不得以替身冒充。
- 上游可直接引用：TASK-010（Context/TM/约束）、TASK-014（渲染切片）、TASK-019（provider 集成层与 `build_production_handlers` 装配模式）。

## Acceptance Criteria

- [ ] `color` step：产出并记录 color/route 判定与 provenance；无外部调用、无模型依赖时 fail-closed（不静默降级为单色基线）。
- [ ] `term_extract` step：产出 term/TM 候选并记录 provenance；不修改正式术语库或 TM 数据，不发出网络请求。
- [ ] `render` step：上游 artifact 齐备时不再 `BLOCKED(missing_clean_artifact)`；写回遵守单 Region 写作用域、Lock 与 current/pinned Revision 保护；缺上游时 fail-closed 且原因入 provenance。
- [ ] 完整链用例（`tests/providers`）：以真实 SQLite + 真实 seam 跑通 9 步，断言目标 Region 写入、同页其他 Region 的 text/pointer/stage 不变、人工译文与锁保留。
- [ ] 回归：改动 `src/bootstrap/app.py` 或 `src/infrastructure/providers/**` 后复跑 `tests/pipeline`、`tests/core`、`tests/storage` 与全仓套件，分列 passed/skipped 与 skip 原因。
- [ ] 交付 Handoff、实际测试/审阅记录与未完成项，经**非作者**独立 Review 与 Codex 集成验证后才能 done。

## 范围裁决（Codex，2026-09-17）

- 本 Task **承接** TASK-019 无法覆盖的翻译域与渲染域接线；`color`/`term_extract` 的服务本体已由 TASK-010、渲染切片已由 TASK-014 交付，本 Task 只做主链接线与 handler 实现。
- **渲染侧改动需先申请范围变更**：`src/ports/rendering/**`、`src/infrastructure/rendering/**` 属 TASK-014/015 已交付边界，**不在本 Task 允许路径内**；如确需修改，先在 Task 中记录并由 Codex 批准。

## 允许修改范围

- `src/application/translation/color/**`、`src/application/translation/knowledge/**`、`src/application/translation/context/**`
- `src/infrastructure/providers/**`（新增 handler 与接线）
- `src/bootstrap/app.py`（注入 handler）
- `tests/providers/**`
- `doc/tasks/TASK-033.md`、`doc/handoffs/TASK-033-*.md`、`verification/TASK-033/**`

## 禁止范围

- 不得修改依赖清单、Schema/migration、pipeline seam 本体（`src/infrastructure/pipeline/**`、`src/application/translation/pipeline/**`）、`AGENTS.md`、生产数据、其他 Task。
- 不得把 TASK-019 已登记的 `BLOCKED`/`NOT_RUN` 项改记为通过（AC-RFULL-001 的完整通过仍需真实模型/端点证据）。
- 不得放宽既有测试或新增 skip 掩盖失败；不得顺手修 `tests/reading_export` 的 flaky（见 STATUS「已知 flaky 测试」）。

## 测试要求

- 主套件：`python -m pytest tests/providers -q`（含完整链用例与 fail-closed 用例）。
- 回归：`python -m pytest tests/pipeline tests/core tests/storage -q` 与全仓 `python -m pytest -q`。
- 真实模型/端点可用时另跑端到端并记录设备、模型版本与权重 Hash；不可用时标 `BLOCKED`/`NOT_RUN` 并给出解锁条件。

## 依赖、风险与阻塞

硬依赖：[TASK-010](TASK-010.md)（Context/TM）、[TASK-014](TASK-014.md)（渲染切片）、[TASK-019](TASK-019.md)（provider 集成层）——均已集成 `done`。

阻塞：**未获用户释放**。已登记输入缺口（沿用）：真实 OpenAI-compatible 端点未配置 → 真实端点类 AC `BLOCKED`；本环境无 `torch`/`diffusers`/`numpy` 且依赖清单变更需用户批准 → 模型类 AC `BLOCKED`；另有 TASK-019 的 **F-1**（默认 `sfx_policy` 使规划跳过整链，已由 [TASK-032](TASK-032.md) 承接）——**F-1 未修前，完整链在真实默认值下不会执行**，两者需一并排期。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际执行/测试：尚无（`proposed`，未释放）。
- 最近状态：2026-09-17 由 Codex 依 TASK-019 R-2/F-2 创建为 `proposed`；释放需用户批准。
