---
id: TASK-044
title: TASK-021 修订尾项（F-2 purge FK 完整性 P1 + F-6 生成资产删除范围 + F-7 manifest 原子性 + F-10 软删过滤）
kind: bugfix
status: done
approval: approved_by_user
suggested_owner: DeepSeek Harness
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-021]
base_commit: 1c171dcdeafc1cbffe6111d503dd0cd598e22dea
branch: agent/deepseek/TASK-044-purge-integrity
worktree: G:/CODEX/New Manga.worktrees/TASK-044-deepseek
integration_commit: 5784018fb528ef7b2521134515ee7776222ffd1d
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

- Handoff：[TASK-044-7cd59d5](../handoffs/TASK-044-7cd59d5.md)（delivery_head=`7cd59d5`）。Review：尚无（待 Codex 按 §6 执行**非作者** Review）。
- 实际执行/测试（`TASK-012-py312`，Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1，`PYTHONDONTWRITEBYTECODE=1`，全部 `-p no:cacheprovider`）：
  - 证据总表：[verification/TASK-044/README.md](../../verification/TASK-044/README.md)；FK 图与删除顺序实验：[purge-fk-probe.txt](../../verification/TASK-044/purge-fk-probe.txt)；完整性扫描：[page-key-tables-scan.txt](../../verification/TASK-044/page-key-tables-scan.txt)；判别力：[pre-fix-failure-summary.txt](../../verification/TASK-044/pre-fix-failure-summary.txt)；全仓逐次：[full-suite-runs.log](../../verification/TASK-044/full-suite-runs.log)；基线：[baseline-master-33c8dd4.txt](../../verification/TASK-044/baseline-master-33c8dd4.txt)。
  - 定向：`tests/storage tests/core tests/library tests/import_formats tests/providers` → **296 passed / 0 skipped**；逐目录 `storage 48 / core 23 / library 40 / providers 169`。
  - 全仓：**813 passed / 6 skipped ×5 次**（另 run 6 给出逐条 skip 原因），逐次 exit 0；独立基线 master `33c8dd4` → **804 passed / 6 skipped** ⇒ +9 = 恰好新增 9 例；6 条 skip 全为既有 `tests/network` `openssl unavailable`。
  - 判别力：新测试放到 base `33c8dd4` 的 `src` 上 → **8 failed / 1 passed**（唯一通过者是夹具守卫，理应修前通过）；5 项 purge 用例在修前均为 `IntegrityError: FOREIGN KEY constraint failed`（F-2 复现）。
  - 边界：改动恰为 `src/infrastructure/sqlite/library.py`、`src/application/maintenance/{trash,ports}.py`、`tests/storage/test_purge_integrity.py`、`verification/TASK-044/**`，**越界 0**；`git diff --check` 退出码 0；**未新增 skip/xfail**；未放宽既有断言；未用 `PRAGMA foreign_keys = OFF`、未捕获 `IntegrityError`、未放宽 `remove_managed` 越界拒绝；未改 Schema/migration/依赖/seam。
- **AC ① 的实证修正（请 Reviewer 裁定）**：任务书要求的「先 `UPDATE media_artifacts SET current_revision_id = NULL` 破循环」在本 schema 下**不可能执行**——`trg_media_artifacts_current_not_clearable` 对「非 NULL → NULL」直接 `RAISE(ABORT)`（`regions` 同，见 [purge-fk-probe.txt](../../verification/TASK-044/purge-fk-probe.txt) E1）；且**不必要**：该复合 FK 声明为 `DEFERRABLE INITIALLY DEFERRED`，同一事务内两侧同删即满足（E3/E4）。改 Schema 与关 FK 均被禁止，故实现改为依赖 deferred FK 并在 docstring 写明依据。
- **F-10 拆分与 port docstring 漂移（需要一次跨范围决定）**：`existing_source_hashes` 已加 `deleted_at IS NULL`；`max_source_order` **有意保留**软删行（否则新导入页会与日后 restore 的页撞 order）。但 `src/application/importing/images/ports.py` 的 `ImportPageSink` 文档要求「两方法都不得过滤」→ 该文件**不在本 Task 允许范围**，未改，建议给单文件 scope grant 或由 Codex 在集成时改（替换文案见 Handoff「待 Reviewer 裁定」①）。
- **另两处超出任务书枚举的补全（可回退）**：跨页 provenance 悬空指针先清（否则"永久删除"对该形态永久失败，E5 证据）；无 FK 的 `pipeline_stage_states` 键行一并清理（该表当前 0 行、无生产写入方）。
- **最近状态（当前，唯一）**：2026-09-18 **`in_progress`（实现已交付，待非作者 Review）**——F-2 / F-6 / F-7 / F-10 已实现并取证，delivery head `7cd59d5`，fixed base `1c171dc`（开工先 `git merge master` → `33c8dd4`，fast-forward 无冲突）。**未 push；`doc/STATUS.md` 未改**（按 AC ⑦，关闭登记在 Review/集成之后）。本 Task **尚未 done**、四项缺陷**尚未"关闭"**。
- 历史状态（2026-09-18）：由 Codex 依 DSH 外部复审 `doc/reviews/POSTHOC-WINDOW-DSH-2026-09-18.md` 的 F-2/F-6/F-7/F-10 开立为 `ready`；本次开工置 `in_progress`。


## Review 与集成记录（2026-09-18）

- **Review**：[doc/reviews/TASK-044-7cd59d5.md](../reviews/TASK-044-7cd59d5.md)（Reviewer=Codex，**非作者**；commit `731561b`；decision=**`approved`**；0 P0/P1、4×P3）。
- **Reviewer 独立复跑（非复用作者证据）**：`tests/storage` **48 passed / 0 skipped**、新文件 **9 passed**、全仓 **813 passed / 6 skipped**（6 条全为既有 `tests/network` `openssl unavailable`；基线 `804/6` ⇒ **+9 恰为新增 9 例**）；**判别力独立复现** 新测试 + master `src` → **8 failed / 1 passed**（唯一通过者为夹具完整性守卫）；**重跑作者探针** E0a 得 **6 表 / 7 FK 全部 `NO ACTION`**（与我先前独立枚举逐项一致）、E0b 显示 pipeline 子树多为 CASCADE、**E1 两张表的 `current_revision_id` 清空均被触发器 ABORT 拒绝**、E2 只删 revisions 失败 ⇒ 印证正确路径；既有测试**零断言/零测试删除**、**无新增 skip/xfail**、未碰 Schema/依赖/`AGENTS.md`、`src`+`tests` 空白干净、**无 `PRAGMA foreign_keys = OFF` / 无吞 `IntegrityError`**。
- **★ AC ① 实证修正（作者提出，Reviewer 采纳）**：本 Task 的 AC ① 原写「**先** `UPDATE media_artifacts SET current_revision_id = NULL` 破循环」，**该步骤在本 schema 下不可能**——`trg_media_artifacts_current_not_clearable`（及 `regions` 同名触发器）对「非 NULL → NULL」直接 `RAISE(ABORT)`（E1 实测两条均被拒）；正确路径是承认复合 FK 为 **`DEFERRABLE INITIALLY DEFERRED`**，**同一事务内两侧同删**即满足（E2 只删 revisions 失败 → E4 逆序全量提交成功）。**裁定：采纳作者的修正，我方该步骤作废**；Task 文件内作者已加「AC ① 的实证修正（请 Reviewer 裁定）」段，本 Review 明示认可。**流程修正（我方）**：涉及"删除/级联/清指针"的 AC 必须同时枚举 `sqlite_master` 的 **TRIGGER**（本次只读 FK 图、漏触发器）。
- **5 项待裁定 → 结论**：① F-10 的 port docstring 漂移 **采纳选项 (b)——由集成方改**（见下）；② `max_source_order` 有意不过滤 **接受**（restore 槽位保留，既有测试已把该口径写成有意行为）；③ 跨页 provenance 清指针 **接受**（登记 R-02）；④ `pipeline_stage_states` 一并清理 **接受**（全库扫描证明是唯一无 FK 残留表；正确性优先）；⑤ `pipeline_runs` 不删 **接受**（run 跨多页；登记 R-03）。
- **集成**：`integration_commit=5784018`（merge，parents `731561b` + `9c7d0fa`）。**R-01 由集成方落地**：`src/application/importing/images/ports.py` 的 `ImportPageSink` docstring 按作者建议替文改为"`max_source_order` 仍计入软删页；`existing_source_hashes` 只返回 live 页（F-10, TASK-044）"（**纯文档、行为零变更**；改动 `+6/−6`，空白检查 exit 0）。master 复验：`tests/storage` **48 passed**、全仓 **813 passed / 6 skipped**（**改 docstring 前后各跑一次，结果一致**）。
- **关闭**：**F-2 / F-6 / F-7 / F-10 关闭**；TASK-044 置 `done`。