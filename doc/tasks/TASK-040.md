---
id: TASK-040
title: 接通 TASK-039 的 clean_probe 生产注入（含 F-12 口径修正）
kind: bugfix
status: ready
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: Codex
depends_on: [TASK-039]
base_commit: 40d97d52d272035db723018102970ba40c9c9f62
branch: agent/zcode/TASK-040-clean-probe-injection
worktree: G:/CODEX/New Manga.worktrees/TASK-040-zcode
integration_commit: null
---

# TASK-040：接通 TASK-039 的 `clean_probe` 生产注入（含 F-12 口径修正）

**READY（2026-09-18 用户指示"先 TASK-040 还是 43"后由 Codex 释放，排列为次优先）**：Owner=`ZCode`、Reviewer=`Codex`（**非作者**）、base=`40d97d5`、branch/worktree 见顶部元数据。开工前置 `in_progress` 并 `git merge master`。

## 背景（本切片是"已修好但生产不可达"的第三例）

[TASK-039](TASK-039.md) 修好了 planner 的 Clean 可用性判定（`_clean_available` 改为探测 artifact 而非"无人写入的 stage"），但修复是以 `PipelineService.clean_probe` **可选参数**形式落地的，而**生产装配从未注入它**（`git grep clean_probe src` 仅命中 `application/tasks/service.py`）。

- 后果：生产环境里 render-only 命令（`RERENDER_*`）跨 run 仍规划 `BLOCKED(missing_clean_artifact)` —— **不比修前差、也不是回归**，但修复等于未生效。
- 同时登记有 **[F-12](../../doc/reviews/POSTHOC-WINDOW-DSH-2026-09-18.md)**：`src/application/tasks/service.py:~486` 的 docstring 声称 `clean_probe` "injected at assembly (AC 2)"，而事实并非如此 → **口径与实现不一致**。
- 本窗口同类问题已出现三次（tile 工厂、文档导入、`clean_probe`）→ 本切片须把"**接线断言**"作为交付的一部分（见 AC ②）。

## Acceptance Criteria

- [ ] **AC ①（注入）**：在装配处（`src/bootstrap/app.py`）为 `PipelineService` 注入 `clean_probe`。**必须复用既有能力**（如 artifact 仓储/locator 对 `clean` 的 current 查询），**不得新造第二套 Clean 判定**；探针的**来源与语义须在 Handoff 写明**（谁提供、判什么、返回什么）。
- [ ] **AC ②（接线断言，必做）**：在装配契约测试（`tests/core/test_bootstrap.py`）中新增断言：**生产装配得到的 `PipelineService` 携带非 `None` 的 `clean_probe`**。这是本切片的核心价值——让"接线漏做"不再可能悄悄通过。
- [ ] **AC ③（生产行为 + 判别力）**：给出对照证据——当页**存在 current Clean artifact** 时，render-only 命令**不再** `BLOCKED(missing_clean_artifact)`；**缺失**时仍 fail-closed 且原因入 provenance（既有守卫不得放宽）。新用例对**修前代码**失败并留证。
- [ ] **AC ④（F-12 口径修正）**：把 `service.py` 中"injected at assembly (AC 2)"的表述改为与实现一致（注明：**由本切片接通**）；并同步 [TASK-039](TASK-039.md) 的 AC ② 注记口径（在其 Task 文件或 STATUS 记一处修订，**不得**回改已入档的 Review 结论）。
- [ ] **AC ⑤（回归与证据）**：`tests/core`、`tests/pipeline`、`tests/providers` 与全仓 **passed 不减少**；全仓串跑 **≥5 次**逐次记录（同一 shell + 同一 venv：PowerShell + `TASK-012-py312`），**passed/skipped 分列 + skip 原因**；不得新增 `skip`/`xfail`。
- [ ] **AC ⑥** 交付 Handoff、取证，经**非作者** Review 与 Codex 集成后才能 done；并在 STATUS 记录 F-12 关闭。

## 允许修改范围

- `src/bootstrap/app.py`
- `src/application/tasks/service.py`（**仅** docstring/口径，**不得**改判定逻辑——那已在 TASK-039 收口）
- `tests/core/**`、`tests/pipeline/**`
- `doc/tasks/TASK-040.md`、`doc/handoffs/TASK-040-*.md`、`verification/TASK-040/**`、`doc/STATUS.md`（仅登记关闭与口径修订）

## 禁止范围

- 不得修改 Schema/migration、依赖清单、pipeline seam 本体、路由判定算法、SFX 策略语义（TASK-032/035 已冻结）、`AGENTS.md`、其他 Task。
- 不得放宽/删除既有断言，不得新增 `skip`/`xfail`；不得把 `BLOCKED`/`NOT_RUN` 记为通过。
- **不得**借本切片顺手改 `_clean_available` 的判定逻辑或把探针默认值改成"永远有 Clean"之类的宽松实现（探针必须真实反映 current Clean 的存在性）。

## 依赖、风险与阻塞

硬依赖：TASK-039（`done`，提供 `clean_probe` 可选参数）。

风险：注入后**生产行为会变化**（render-only 命令由 BLOCKED 转 RUN）→ AC ③ 的对照证据必须证明"仅当 Clean 真实存在时才转 RUN"，并覆盖"缺失 Clean"的负例。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际执行/测试：尚无（`ready`，实施未开始）。
- **最近状态（当前，唯一）**：2026-09-18 由 Codex 释放（用户指示排序"先 040 还是 43" → Codex 裁定 **043 先**、040 与之并行）；`base=40d97d5`。**实施尚未开始。**
