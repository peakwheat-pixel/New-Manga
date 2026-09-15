---
task_id: TASK-006
author: ZCode
recipient: Codex（转 DeepSeek Harness 复审）
base_commit: fb29dfedc496cde61cea9ea2558ef274e94eb49e
delivery_head: e1d3e2c99116d9b65140b0ae64a2188555f3c791
status: integrated
integration_commit: 32a73148b0685cf3a63e07cbf1bca25d8553b194
---

# Handoff：TASK-006 修订轮（R-101～R-106）

本 Handoff 交付 `e1d3e2c` 的修订轮，处理 DeepSeek Review 对 `ba1e769` 的 changes_requested 结论（报告 `doc/reviews/TASK-006-ba1e769.md`，Review 报告 commit `047d8c3`，位于 DeepSeek review worktree/分支，不随本分支存在）。原 `ba1e769` 为被拒 head，其 Handoff 结论不再有效；本修订不改变 `base_commit=fb29dfe`。

提交列表（本轮新增）：

| commit | 说明 |
|---|---|
| `e1d3e2c` | fix(TASK-006): address review findings R-101..R-106（新 reviewed_head，唯一内容变更） |

## Findings disposition

| ID | 级别 | 处置 | 实现与证据 |
|---|---|---|---|
| R-101 | P1 | **fixed** | 选择「改实现对齐 D03 §18」（不走 D03 范围变更）。`ManagedFileStorage.new_revision_relative_path` 现产出 `books/{book_id}/chapters/{chapter_id}/{固定目录}/{revision}{ext}`，经显式映射表 `ARTIFACT_TYPE_DIRS`（`thumbnail→thumbnails`、`mask→masks`、`render_preview→previews`、`detection_overlay→previews`、`debug_ocr/debug_detection→debug`）；`export` 按 D03 §18 落 book 级 `books/{book_id}/exports/`；未知类型抛 `ValueError` 拒绝生成目录外布局。`managed_storage.py` 与 `ports/.../storage.py` 两处 docstring 已同步为与 D03 §18 一致的表述。测试 `test_revision_paths_follow_d03_layout` 断言全部 10 个类型的前缀/目录归属 + 未知类型拒绝。 |
| R-102 | P2 | **fixed** | 删除契约外错误码 `ARTIFACT_NOT_FOUND`：`CommitStatus.TARGET_NOT_FOUND` + `error_code="TARGET_NOT_FOUND"` 复用冻结 §10 码；`test_commit_to_unknown_artifact_is_rejected` 断言更新。 |
| R-103 | P2 | **fixed（登记）** | `artifacts.py` 模块 docstring 由「follows the frozen §8.1 sequence」改为明确「artifact current-pointer 子集」，并登记承接：§8.1 的 Lock 重读依赖 Page/Region Lock（TASK-007/008 落库、TASK-011 计划守卫消费）；`StepResultCandidate` 落库依赖 StepRun 表（TASK-011）。此前它们仅在 Handoff 正文出现，现已写入代码内唯一事实源并在下表复核。Task 文件同步登记。 |
| R-104 | P2 | **fixed** | `_split_statements` 改用 `sqlite3.complete_statement` 逐行累积完整语句，分号于字符串字面量或 `BEGIN...END` 触发器体内不再截断；本轮 v1 新增触发器恰好依赖该修复（朴素 split 会截断触发器）。 |
| R-105 | P2 | **fixed** | `backup_records.managed_path` 记录 storage 相对受管路径 `backups/{backup_id}.db`（不再裸文件名）；`test_post_schema_backup_is_recorded` 断言相对路径与文件可解析。D03 §34.3 语义无需修订。 |
| R-106 | P2 | **fixed** | 责任归属裁决：**由 DB 触发器负责**（应用层守卫无法阻止直接 SQL；复合 deferred FK 在 NULL 方向按 MATCH SIMPLE 不检查）。v1 DDL 新增 `trg_media_artifacts_current_not_clearable`（BEFORE UPDATE，非空→NULL 即 RAISE ABORT），首版 NULL 保持合法。负向测试双向固化：`test_established_current_cannot_be_cleared_to_null`（清空被拒且状态不变）与 `test_first_version_null_current_still_legal`。 |

无新 finding 引入；未处理任何派单范围外的 Review 内容。

## 验证证据（本轮）

| 场景 | 命令 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 存储套件（任务计划命令） | `python -m pytest tests/storage` | `G:/CODEX/New Manga.task-envs/TASK-005-py312`（3.12.3）；head `e1d3e2c` | PASS，退出码 0，**31 passed** | author-verification 更新节 |
| 全量回归 | `PYTHONPATH=src python -m pytest tests` | 同上 | PASS，退出码 0，**37 passed**（core 6 + storage 31） | 同上 |
| whitespace | `git diff --check fb29dfe e1d3e2c --` | 本 worktree | PASS，退出码 0 | 复审可重放 |
| 范围 | `git diff --stat fb29dfe e1d3e2c` | 本 worktree | 全部在 TASK-006 allowed_paths；D03/D08/AGENTS/STATUS/其他 Task/TASK-005 代码零触碰 | 同上 |

NOT_RUN / N/A 维持首轮声明不变（并发竞争、v1→v2 升级链、清理/恢复执行、性能、Region/Candidate 持久化承接 TASK-008/011/021）。

## 集成收口

- DeepSeek Harness 复审报告 `doc/reviews/TASK-006-e1d3e2c.md`：`approved`；首轮报告 `doc/reviews/TASK-006-ba1e769.md`：`changes_requested`，两份报告均已纳入 master。
- Codex 串行集成：实现 merge=`3f97369`；Review reports merge=`32a7314`，作为本 Task 的 `integration_commit`。
- AC1～AC4：**已满足**；F-01：**resolved**，D03 §18 已明确 `detection_overlay` 归置于 `previews/` 的理由。
- 集成后验证：Python 3.12.3 下 `python -m pytest tests/storage` 为 31 passed；`PYTHONPATH=src python -m pytest tests` 为 37 passed；固定范围 `git diff --check fb29dfe e1d3e2c --` 通过。详见 [integration-32a7314](../../verification/TASK-006/integration-32a7314.md)。

## 复审建议

- 重放四项验证；重点复核 R-101 路径布局（可对 10 类型跑探针对照 D03 §18）、R-106 双向（清空被拒 / 首版 NULL 合法）、R-104（触发器 DDL 能完整应用即证明）。
- `schema.py` v1 DDL 因新增触发器变化 → `schema_migrations.checksum` 与 `default_migrations()[0].checksum` 一致更新；被拒 head `ba1e769` 从未集成主线，不存在已应用迁移的 checksum 漂移，无需新版本号。
