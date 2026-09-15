---
id: TASK-029
title: 实现统一 SQLite 持久化
kind: implementation
status: in_progress
approval: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-028]
base_commit: 79529bc9805fda6b72b99860f649fca0922c6cf9
branch: agent/zcode/TASK-029-unified-sqlite-persistence
worktree: G:/CODEX/New Manga.worktrees/TASK-029-zcode
reviewed_head: null
integration_commit: null
---

# TASK-029：实现统一 SQLite 持久化

本 Task 已获用户授权并进入 `ready`；由 ZCode 实施、DeepSeek Harness 独立 Review、Codex 串行集成。它只实现已冻结的 TASK-028 统一 SQLite 持久化设计，不扩展产品功能。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

实现依据：[TASK-028 统一 SQLite 持久化设计](../contracts/TASK-028_UNIFIED_SQLITE_PERSISTENCE_DESIGN.md)、[TASK-002 最小数据与执行契约](../contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md)、D03/D07/D08 相关 SQLite、Revision、Artifact 和源文件保护条款，以及 TASK-006/007/008 的已集成代码与测试。

可观察交付结果：同一个由 `open_database()`/`MigrationRunner` 管理的 SQLite 数据库，在不修改 v1 migration 的前提下，通过新增 v2 migration 持久化 Book/Chapter/Tag/BookTag/Page/Region/RegionRevision；现有消费侧 Port 可在重启后读回相同状态；Region current/revision 写回具备真实单事务 compare-and-write；现有 Artifact safe commit 在 v2 上回归通过。

本 Task 将迁移、Library/Page、Region adapter 放在同一个实现切片，是因为它们共享 v2 Schema、同一连接和 current/revision 事务不变量；不得先交付互不兼容的半套持久化。

## Acceptance Criteria

- [ ] 追加 `v2__library_region_persistence` migration；v1 migration 内容不变；迁移继续由现有 `MigrationRunner` 执行，保留迁移前备份、checksum、失败回滚和旧程序 `TOO_NEW/query_only` 门控。
- [ ] 实现 `SqliteLibraryRepository`，按现有 `LibraryRepository`、`ImportPageSink` 和新增 `PageRepository` consumer-side Protocol 持久化 Book/Chapter/Tag/BookTag/Page；Tag 重复检查仍由 `LibraryService` 负责，不新增 `UNIQUE(tags.name)`。
- [ ] 实现 Page 完整 round-trip 和重启读取；兼容 v1 结构占位 Page，不伪造 Hash、Managed Copy、尺寸或源文件；保留 `source_order` 与 `sort_order` 分离、软删除和源文件只读保护。
- [ ] 实现 `SqliteRegionRepository`，正确映射 Region/RegionRevision 的 JSON、枚举、Lock、Pin、current 和恢复来源；落实复合外键、`UNIQUE(region_id, revision_no)`、`DEFERRABLE INITIALLY DEFERRED`、current 不可清空、Pin 不改历史和恢复创建新 Revision。
- [ ] 在既有消费侧 editing Port 与必要的 `RegionEditingService` seam 中实现 `commit_region_revision`：使用 `BEGIN IMMEDIATE`，事务内重读 current/Lock，区分 `APPLIED`、`INPUT_REVISION_CHANGED`、`LOCK_CHANGED`、`DB_FAILED`，冲突或失败保留旧 current；不得用 `add_revision()` + `update_region()` 两次独立提交冒充原子操作。
- [ ] 让保存、自动写回、恢复、Pin 和 `reorder_regions()` 遵守 TASK-028：revision-owned 状态只能通过 Revision commit 同步，重排产生新的 user Revision，Pin 只更新 `is_pinned`，不得同 ID upsert 改写不可变历史。
- [ ] 在 v2 数据库上回归 TASK-006 Artifact safe commit 及既有 storage/library/editing 测试；失败、冲突、取消不能改变 current，数据库不能指向不存在文件。
- [ ] 提供绑定 delivery head 的 Handoff、verification 证据和未运行项；实现完成不等于 done，必须等待 DeepSeek Harness 非作者 Review approved 与 Codex 集成。

## 允许修改范围

以下路径是本 Task 的完整白名单；“仅在确实需要时”不等于可以扩大到同层其他文件：

- `src/infrastructure/sqlite/**`：v2 migration、Library/Page adapter、Region adapter；复用现有 connection/migrator/artifact 实现。
- `src/application/library/ports.py`：仅增加 TASK-028 规定的 `PageRepository`。
- `src/application/importing/images/ports.py`：仅在 Page 类型映射确实需要时修改；现有 `ImportPageSink` 三个方法默认保持不变。
- `src/application/editing/ports.py`：仅增加原子 Region commit 所需的结果类型/Protocol。
- `src/application/editing/service.py`：仅把现有 Region 写入路径接入原子 seam，并让重排/恢复/Pin 遵守 TASK-028。
- `tests/storage/**`、`tests/library/**`、`tests/editing/**`：迁移、Port round-trip、重启、事务冲突、源文件保护和 Artifact 回归证据。
- `doc/tasks/TASK-029.md`、`doc/handoffs/TASK-029-*.md`、`doc/reviews/TASK-029-*.md`、`verification/TASK-029/**`：本 Task 的交接与验证记录。

## 禁止范围

不得修改 `src/domain/**` 的语义、QML/UI、Provider、Pipeline、StepResultCandidate、Constraint、TM、依赖清单、用户源文件、AGENTS 或其他规则；不得修改现有 v1 migration；不得创建第二个数据库、巨型跨职责 Repository 或把消费侧 Protocol 整体搬到 `src/ports`；不得修改 TASK-028 设计语义、D03 命名差异或 TASK-008 的 R-201/R-202 决策。不得把测试直接读私有 SQLite 表作为 Port round-trip 的唯一证据。

超出白名单、需要改变 Domain/契约/Schema 归属或发现 v1 无法兼容时，暂停越界修改，在本 Task 记录 blocker，由 Codex提出范围变更；不得自行顺手处理其他 Task。

## 实施顺序与工具调用规则

1. 批量侦察：一次读取现有 schema、connection、migrator、Artifact adapter、三处 consumer-side ports、Domain mapper、editing service 和相关测试，列出完整 change set。
2. 先写失败测试并按逻辑批次实现：Schema/迁移与 Library/Page、Region/原子 seam、Artifact 回归分别形成可验证批次；同一文件的已知修改尽量合并为一次 Patch，避免碎片化微编辑和重复 Read。
3. 集中验证：每个 logical batch 完成后再运行相关测试；测试失败允许重新读取、定位和迭代修复，不因批处理规则跳过必要验证。
4. 交付前集中运行迁移/重启/冲突探针、storage/library/editing 测试和全量回归，记录确切命令、环境、退出码、PASS/FAIL/NOT_RUN 与证据路径。

## 测试要求

固定 Python 3.12.3 项目环境：`G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe`；测试数据库、Managed Storage、临时源文件和缓存必须使用 TASK-029 独立临时根目录，禁止写用户漫画库或共享 `app.db`。

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| v1 空库与 v1→v2 迁移 | `python -m pytest tests/storage/test_schema_migration.py -v` 及 v1/v2 探针 | Python 3.12.3、独立临时 DB | NOT_RUN | 待交付 verification |
| Library/Page Port round-trip 与重启 | `python -m pytest tests/library -v` | v2 adapter、独立临时 DB/Managed Storage | NOT_RUN | 待交付 verification |
| Region Revision 原子性、Lock、Pin、恢复、重排 | `python -m pytest tests/editing -v` 及冲突/回滚探针 | v2 adapter、并发连接隔离 | NOT_RUN | 待交付 verification |
| Artifact v2 回归与源文件保护 | `python -m pytest tests/storage -v` | v2 数据库、独立源文件 | NOT_RUN | 待交付 verification |
| 全量回归 | `PYTHONPATH=src python -m pytest tests` | Python 3.12.3 | NOT_RUN | 待交付 verification |
| 范围与空白 | `git diff --check <base> <delivery_head>`；检查变更路径 | 固定 delivery head | NOT_RUN | Handoff/Review |

必须额外覆盖：迁移备份/checksum/失败回滚/旧程序只读、Page v1 占位兼容、FK/软删除/顺序分离、Region current 冲突和 Lock 冲突回滚、Pin 不改 snapshot、恢复新增 Revision、Artifact 失败保留旧 current，以及 SQLite 不写入 Pipeline/Secret/二进制内容。任何未执行项必须保留 `NOT_RUN`，不能改写为 PASS。

## 依赖、风险与阻塞

硬依赖：[TASK-028](TASK-028.md) 已在 master 完成设计 Review 与 Codex 集成；TASK-002/006/007/008 已作为 TASK-028 的已集成依赖满足。

共享 Schema、application Port 和 Region 原子 seam 是本切片的高风险交界。现有内存 fake 只证明应用行为，不证明 SQLite；v2 迁移、重启、并发冲突和 Artifact v2 回归必须以本 Task 固定 commit 的真实证据补齐。`managed_original_ref` 与 D03 `managed_original_artifact_id` 仍不得静默合并；R-201/R-202 不在本 Task 裁决。

## 交付与运行记录

- Handoff：尚无；ZCode 完成后新增 `doc/handoffs/TASK-029-<delivery-head>.md`，引用固定 delivery head。
- Review：尚无；DeepSeek Harness 必须在独立 worktree 按固定 base/delivery head 审查，不能审核自己的变更。
- 实际测试：尚无；所有命令先标 planned/NOT_RUN，交付时按真实环境回填。
- Codex 集成：尚无；只有 Review approved、Handoff/verification 完整且 Codex 集成验证通过后，才能填写 `integration_commit` 并置 `done`。
- 认领记录：2026-09-15 ZCode 在指定 worktree 接管开始执行。基线核验通过：HEAD=`c6db2c0`（=release commit，含 base `79529bc` 与 TASK-028 集成），分支/worktree 如派单，common dir=`G:/CODEX/New Manga/.git`，工作区干净。状态 ready → in_progress。
