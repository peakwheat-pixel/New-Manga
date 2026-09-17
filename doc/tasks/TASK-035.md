---
id: TASK-035
title: 修复渲染层 SFX Policy Gate 缺失 region_type 前置（F-1 渲染面）
kind: bugfix
status: proposed
approval: pending_user_review
suggested_owner: ZCode
owner: null
reviewer: null
depends_on: [TASK-019, TASK-032]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-035：修复渲染层 SFX Policy Gate 缺失 region_type 前置（F-1 渲染面）

**PROPOSED（未释放）**：本 Task 承接 TASK-032 Review 的 **R-04（P1）/ R-05（P2）/ R-02（P2）**，**需用户批准释放**；未释放前不得实施。**F-1 只有在 TASK-035 完成并集成后才算关闭**（TASK-032 只关闭了规划面）。

## 来源与目标

- 来源：[doc/reviews/TASK-032-771977c.md](../reviews/TASK-032-771977c.md) 的 R-04/R-05/R-02；[doc/STATUS.md](../STATUS.md) 的 F-1 登记（现为"部分关闭"）。
- 规范依据：D06 §85「SFX Policy Gate」的前置 `region_type = sfx`；D08 AC-SFX-001；D03 §7 默认 `skip`。
- 现状（Codex 实测，非作者自述）：`src/application/rendering/service.py:219` 与 `:347` 仅做 `SfxPolicy(stored.sfx_policy)` 判定，**没有 `region_type` 前置** → 普通 `speech` Region 取真实默认 `skip` 时 `rerender` 仍返回 `SKIP_POLICY` / `skip_policy`；且该行为被既有用例固定为期望（`tests/rendering/test_rerender.py:246-265`：fixture 未设 `region_type`（默认 `speech`）+ `sfx="skip"` → 断言 `skipped`）。

## Acceptance Criteria

- [ ] 渲染层与 planner 采用**同一判据**：仅 `region_type == sfx` 参与 SFX 策略；非 SFX 类型任何策略取值都不影响渲染结果。
- [ ] 复用**单一规则来源**（`application/translation/context/gate.py::decide_sfx_translation` 或与之等价的共享实现），不得再出现第二份实现（F-1 根因即两份实现漂移）。
- [ ] 修正 `tests/rendering` 中把缺陷固化的用例（fixture 的 region 显式建为 `region_type="sfx"`），并新增"`speech` + 真实默认 `skip` → 正常渲染"的回归用例；**不得放宽或删除其他断言**。
- [ ] `src/domain/tasks/models.py:182` 的 `RegionSnapshot.sfx_policy` 字段默认与实体/Schema 一致（`SfxPolicy.SKIP.value`）。
- [ ] `tests/pipeline` 的 `region()` 夹具默认对齐生产默认（或显式注明差异），消除 R-02 的"夹具漂移"面。
- [ ] 交付 Handoff、实际测试/审阅记录与未完成项，经**非作者** Review（按协作协议 §6 四轴）与 Codex 集成验证后才能 done。

## 允许修改范围

- `src/application/rendering/**`
- `src/domain/tasks/models.py`
- `tests/rendering/**`、`tests/pipeline/**`
- `doc/tasks/TASK-035.md`、`doc/handoffs/TASK-035-*.md`、`verification/TASK-035/**`

超出范围（Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、其他 Task、`src/ui/**`）先由 Codex 明确范围变更。

## 禁止范围

- 不得修改 Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、生产数据、其他 Task。
- 不得改变 `sfx_policy` 的默认值语义（D03 §7 的 `skip` 保持）。
- 不得放宽/删除既有断言或新增 skip 掩盖失败；不得顺手修 `tests/reading_export` 的两个已登记 flaky。

## 测试要求

- 主套件：`python -m pytest tests/rendering tests/pipeline -q -p no:cacheprovider -rs`。
- 必须双侧验证：**`speech` + `skip` → 渲染不被拦**；**`sfx` + `skip`/`manual` → 仍被拦**（保留原意）。
- 回归：全仓 `python -m pytest -q`，分列 passed/skipped 与 skip 原因。
- 记录 commit、OS/依赖、命令、退出码与证据路径。

## 依赖、风险与阻塞

硬依赖：[TASK-019](TASK-019.md)、[TASK-032](TASK-032.md)——均已集成 `done`。

阻塞：**未获用户释放**（`status=proposed`）。

风险：修改 `tests/rendering/**` 会触碰 TASK-014/015 交付的渲染用例，必须保留其原意（SFX 类型仍被策略拦截），只补正 fixture 的类型。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际执行/测试：尚无（`proposed`，未释放）。
- 最近状态：2026-09-17 由 Codex 依据 TASK-032 Review 的 R-04/R-05/R-02 创建为 `proposed`；释放需用户批准，释放时由 Codex 填 owner/reviewer/base/branch/worktree。
