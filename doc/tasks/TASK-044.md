---
id: TASK-044
title: TASK-021 修订尾项（F-2 purge FK 完整性 P1 + F-6 生成资产删除范围 + F-7 manifest 原子性 + F-10 软删过滤）
kind: bugfix
status: ready
approval: approved_by_user
suggested_owner: DeepSeek Harness
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-021]
base_commit: 1c171dcdeafc1cbffe6111d503dd0cd598e22dea
branch: agent/deepseek/TASK-044-purge-integrity
worktree: G:/CODEX/New Manga.worktrees/TASK-044-deepseek
integration_commit: null
---

# TASK-044：TASK-021 修订尾项（F-2 / F-6 / F-7 / F-10）

**READY（2026-09-18，Codex 依外部复审裁定开立）**：Owner=`DeepSeek Harness`（**非缺陷作者**）、Reviewer=`Codex`（**非作者**）、base=`1c171dc`。开工前置 `in_progress`。

**在接线任何 purge UI 之前必须完成本切片**（F-2 会使"永久删除"在真实数据上确定失败）。

## AC ①（F-2，P1，核心）：`purge_pages` 补全 FK 图并改为"先删行、后删文件"

**Codex 独立枚举的已验证 FK 图（2026-09-18，真实 schema + `PRAGMA foreign_key_list`）**：

```text
引用 pages(page_id) 的表（6 张 / 7 个 FK，全部 on_delete=NO ACTION，无 CASCADE）：
  media_artifacts          page_id ×2
  pipeline_run_targets     page_id
  pipeline_tasks           page_id
  step_runs                page_id
  step_result_candidates   page_id
  regions                  page_id      <- purge_pages 已处理
其余相关依赖：
  region_revisions            -> regions(region_id)
  artifact_revisions          -> media_artifacts(artifact_id)      [循环一份]
  media_artifacts             -> artifact_revisions(current_revision_id)   [循环另一份]
  media_artifacts             -> artifact_revisions(artifact_id)
  artifact_revisions          -> artifact_revisions(source_artifact_revision_id)  [自引用]
```

- 缺陷：`src/infrastructure/sqlite/library.py:432-457` 只删 `region_revisions → regions → pages`；任一 `media_artifacts`/pipeline 行存在即 `IntegrityError: FOREIGN KEY constraint failed`（`connection.py:37` 强制 `PRAGMA foreign_keys = ON`）。`trash.py:137-147` 又**先 unlink 托管件、再删行** → 文件已失、行仍软删、batch 仍留 ledger，`restore_batch` 复原出**指向已删文件的活页**，且 purge 永久无法重试。
- **Codex 独立复现（2026-09-18）**：`purge_batch` → `IntegrityError`；`managed file after: False`（文件已消失）、`page row after: 1`、`batches in ledger: 1`、`restore_batch → live page points at missing file: True`。
- 修法（要点）：①**单事务内**按 FK 逆序清理：`step_result_candidates → step_runs → pipeline_tasks → pipeline_run_targets →`（**先** `UPDATE media_artifacts SET current_revision_id = NULL` 打破循环）`→ artifact_revisions → media_artifacts → region_revisions → regions → pages`；②`trash.py` 改为**先删行、成功后再删文件**（文件删除失败须可诊断，**不得**留下"文件已失、行仍在"）；③保持 `remove_managed` 的**越界拒绝**（`ImmutablePathViolation`）不变。
- **完整性验证方式（不得只测一张表）**：新测试须在**每一张引用 `pages` 的表**都插入行后再 purge，或在测试内用 `PRAGMA foreign_key_list` 枚举并断言"purge 后不存在任何指向该页的行"；**禁止**沿用"只建 pages 行"的夹具（这正是本缺陷在套件中恒绿的原因）。

## AC ②（用户指定必测）：purge 成功且 restore 不产生悬空引用

- 新增用例：**有 `media_artifacts` / pipeline 行的页** → `purge_batch` **成功**；purge 后该页**不可**被 `restore_batch` 复原出"指向缺失文件"的活页；若仍可 restore，其 `managed_original_ref` 必须**真实存在**。

## AC ③（F-6，P3）：purge 的删除范围须含**生成资产**

- 依据 `doc/04_USER_FLOW.md:1677-1688` 与 `doc/07_NON_FUNCTIONAL_REQUIREMENTS.md:1065`：永久删除 = 项目数据 + Managed Copy + **生成资产** + Cache；**不删**用户原始源文件。
- 现实现只删 `managed_original_ref`；须收集该页全部 `artifact_revisions.managed_path` 一并删除（**仍受 managed root 越界约束**）。

## AC ④（F-7，P3）：manifest 原子性与"可重建"口径

- `trash.py:39-49/87-105`：manifest 非原子写 + 裸 `json.loads`；DB 软删与 manifest 写入跨介质无事务。
- 修法：manifest **原子写**（临时文件 + `os.replace`）+ 读侧容错（截断/坏 JSON 不得使整功能失效）；并把 docstring `trash.py:15` 声称的 "rebuildable bookkeeping" **与实际能力对齐**——要么实现重建，要么改口径（**二选一，必须一致**）。

## AC ⑤（F-10，P3）：软删行不得参与导入去重

- `library.py:296-310` 的 `existing_source_hashes`/`max_source_order` 未过滤 `deleted_at` → 软删页仍占去重与 `source_order`（用户会看到"重导被跳过但章节里没有页"）。
- 修法：两查询加 `deleted_at IS NULL`（**推荐**）或修正注释口径；二选一并给理由与用例。

## AC ⑥（回归与证据）

- 新用例对**修前代码**失败（purge 用例在修前因 `IntegrityError` 失败 = 天然判别力，须留证）。
- `tests/storage`、`tests/core`、`tests/library` 与全仓 **passed 不减少**；全仓 **≥5 次**逐次记录（同一 shell + 同一 venv），**passed/skipped 分列 + skip 原因**。
- 不得新增 `skip`/`xfail`；不得放宽既有断言（`tests/storage/test_trash.py:136-156` 的"根外源文件逐字节幸存"必须继续通过）。

## AC ⑦

交付 Handoff、取证，经**非作者** Review 与 Codex 集成后才能 done；并在 STATUS 记录 F-2/F-6/F-7/F-10 关闭。

## 允许修改范围

- `src/application/maintenance/**`
- `src/infrastructure/sqlite/library.py`（**不得**改 `schema.py`/migration）
- `src/infrastructure/filesystem/managed_storage.py`（仅在确需时；越界拒绝语义不得放宽）
- `tests/storage/**`、`tests/core/**`
- `doc/tasks/TASK-044.md`、`doc/handoffs/TASK-044-*.md`、`verification/TASK-044/**`、`doc/STATUS.md`（仅登记关闭）

## 禁止范围

- 不得改 Schema/migration、依赖清单、seam 本体、`AGENTS.md`、其他 Task。
- **不得**以"无用户可触发路径/已登记"为由延后 F-2；**不得**用 `PRAGMA foreign_keys = OFF`、捕获 `IntegrityError` 后忽略、或先删文件再删行等方式绕过。
- 不得放宽 `remove_managed` 的越界拒绝，不得触碰 managed root 之外任何路径。

## 依赖、风险与阻塞

硬依赖：TASK-021（`done`，trash 子集）。风险：删除顺序若漏一张表，`IntegrityError` 会**再次**出现 → AC ① 的完整性验证方式是硬要求。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际执行/测试：尚无（`ready`，实施未开始）。
- **最近状态（当前，唯一）**：2026-09-18 由 Codex 依 DSH 外部复审的 F-2/F-6/F-7/F-10 开立；`base=1c171dc`。**实施尚未开始。**

