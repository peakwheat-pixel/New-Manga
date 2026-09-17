---
id: TASK-039
title: 修复 planner `_clean_available` 继承缺陷（render-only 命令跨 run 误判 BLOCKED）
kind: bugfix
status: ready
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: ZCode（窗口内子 agent，结论仅 approved_subagent）
depends_on: [TASK-019, TASK-033]
base_commit: 047164ea080651741b38b20a36470115d4830a0d
branch: agent/zcode/TASK-039-clean-availability
worktree: G:/CODEX/New Manga.worktrees/TASK-039-zcode
integration_commit: null
---

# TASK-039：planner `_clean_available` 继承缺陷

**READY（2026-09-18 ZCode 全权窗口 W6，用户指示"再布置任务"）**：Owner=`ZCode`、Reviewer=窗口内子 agent（结论**只能** `approved_subagent`/`changes_requested`）、base=`047164e`。开工前置 `in_progress` 并 `git merge master`。

## 来源

[TASK-033 Handoff](../handoffs/TASK-033-933819f.md) 登记的 **R-001（P2，白名单外移交 Codex）**，并被 [窗口报告 v1/v2](../../verification/ZCODE-WINDOW-2026-09-17/window-report.md) 列为最高优先遗留：

> `src/application/tasks/service.py` 的 `_clean_available` 检查**无人写入的 `clean` stage** → render-only `RERENDER_*` 命令**跨 run** 仍规划 `BLOCKED(missing_clean_artifact)`。

## Acceptance Criteria

- [ ] **AC ①（根因）**：诊断并记录根因——planner 判定 Clean 可用性时看的是**stage 状态**而不是**当前 Clean artifact/指针的实际存在**。（TASK-019 的 handler 会提交 `ARTIFACT_CLEAN`，但 `clean` **stage** 未必被写成有效态。）**根因须以证据写明**（哪一行、为何误判），不得只改判据不谈机理。
- [ ] **AC ②（修复）**：render-only 命令（`RERENDER_PAGE` / `RERENDER_REGION` / `RERENDER_SELECTED` 等，**按实际命令枚举**）在**确实存在 current Clean artifact** 时规划为 `RUN`（不再误 `BLOCKED(missing_clean_artifact)`）；**确实缺失**时仍 `BLOCKED` 且原因入 provenance（**不得放宽既有守卫**）。
- [ ] **AC ③（不波及其他判定）**：其他命令族（`TRANSLATE_*` / `REINPAINT_*` / `RETRANSLATE_*` / `REOCR_*`）的规划决策与理由**逐项不变**（给出对照矩阵）。
- [ ] **AC ④（判别力 + 回归）**：新增用例对**修前代码**失败（把新用例放到 base `047164e` 的 `src` 上跑一次并留证）；`tests/pipeline`、`tests/core`、`tests/providers` 与全仓 passed **不减少**；全仓串跑 **≥5 次**逐次记录（同一 shell/venv）。
- [ ] **AC ⑤** 交付 Handoff、取证，经窗口内子 agent Review 与集成后才能 done；并在 [TASK-033 Handoff](../handoffs/TASK-033-933819f.md) 或 STATUS 记录"R-001 已由本 Task 关闭"。

## 允许修改范围

- `src/application/tasks/service.py`
- `tests/pipeline/**`、`tests/core/**`
- `doc/tasks/TASK-039.md`、`doc/handoffs/TASK-039-*.md`、`verification/TASK-039/**`
- `doc/STATUS.md`（仅登记关闭关系）

## 禁止范围

- 不得修改路由判定算法（`decide_route`/`acceptable_routes`/`preferred_route_order`/`route_gate`）、SFX 策略门控语义（TASK-032/035 已冻结）、Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、其他 Task。
- 不得放宽/删除既有断言，不得新增 `skip`/`xfail`。

## 测试要求

- `python -m pytest tests/pipeline -q -p no:cacheprovider -rs`（含新回归）
- 全仓 `python -m pytest -q -p no:cacheprovider -rs -rf`（≥5 次逐次记录）

## 依赖、风险与阻塞

硬依赖：TASK-019（handler 与 Clean 写入）、TASK-033（本缺陷的发现与登记）——均 `done`。

风险：`_clean_available` 同时服务其他命令族（`REINPAINT_*` 等），**改动可能外溢** → AC ③ 的对照矩阵是必做项，不得省略。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际执行/测试：尚无（`ready`，实施未开始）。
- **最近状态（当前，唯一）**：2026-09-18 由 Codex 在 ZCode 全权窗口第二轮创建为 `ready`；`base=047164e`。**实施尚未开始。**
