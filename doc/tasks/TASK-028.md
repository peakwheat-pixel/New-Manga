---
id: TASK-028
title: 冻结统一 SQLite 持久化设计
kind: design
status: done
approval: approved
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [TASK-002, TASK-006, TASK-007, TASK-008]
base_commit: 4a1df8fb5bc90e1542113c5ae3b15cb837146f79
branch: master
worktree: G:/CODEX/New Manga
reviewed_head: f9f28115304b90f25a36bdd186cc55dbd2cee72e
integration_commit: 509de668ea9529e7b2a38abd2368df0ff02a64ae
---

# TASK-028：冻结统一 SQLite 持久化设计

本 Task 已完成设计冻结、独立 Review 与 Codex 串行集成；仅交付后续实现所需的 SQLite 数据归属、Schema 迁移方向、Adapter seam、事务不变量和范围边界，SQLite 实现尚未释放。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

来源：TASK-002 最小数据与执行契约 §2、§8、§10；TASK-006/007/008 的已集成实现、Task 边界和 Review 遗留；D02 §6/13、D03 §3～16/34、D07 §28/34/37～50、D08 AC-DB/REV/ART。唯一设计交付物为[统一 SQLite 持久化设计](../contracts/TASK-028_UNIFIED_SQLITE_PERSISTENCE_DESIGN.md)。

当前可观察目标：统一数据库承载 Book/Chapter/Page/Tag/Region/RegionRevision/Artifact 元数据，保持现有消费侧契约和 Artifact 安全提交语义；不提前实现 Pipeline 或 UI。

## Acceptance Criteria

- [x] 记录当前 v1 Schema、TASK-006 Artifact adapter、TASK-007/008 消费侧契约及其真实差距。
- [x] 固定“共享连接 + 按契约拆分 Adapter”的架构，并记录拒绝独立数据库、巨型 Repository 和无必要端口搬迁的原因。
- [x] 固定 v2 迁移的表归属、字段映射、Region current/revision 约束、v1 结构占位 Page 的兼容规则和 Artifact 不变边界。
- [x] 解决 Page round-trip 的 Port 边界、`managed_original_ref` 与 D03 `managed_original_artifact_id` 的命名差异，以及 Tag 重复约束是否属于本设计的问题。
- [x] 固定短事务、`BEGIN IMMEDIATE` compare-and-write、重启、回滚和源文件保护原则，并明确 Region 两调用不能冒充原子提交。
- [x] 固定 Region Revision commit 的逻辑输入/输出、Lock 快照、Pin 更新和 `reading_order` 与 Revision snapshot 的一致性要求。
- [x] 列出后续实现允许/禁止路径和真实验收门槛；不修改业务代码、UI、现有规则或产品 AC 结果。
- [x] 独立 Review 与 Codex 集成记录完成；本设计 Task 已 done，但任何后续实现 Task 仍须独立创建、授权和验收。

## 允许修改范围

本设计 Task 仅允许修改以下相对项目根目录的文档：

- `doc/contracts/TASK-028_UNIFIED_SQLITE_PERSISTENCE_DESIGN.md`
- `doc/tasks/TASK-028.md`
- `doc/tasks/README.md`
- `doc/00_INDEX.md`
- `doc/STATUS.md`
- `doc/12_ROADMAP.md`
- `doc/reviews/TASK-028-*.md`
- `doc/handoffs/TASK-028-*.md`
- `verification/TASK-028/**`

后续实现的拟议源码白名单见设计文档 §5；释放实现时必须重新填写 owner、reviewer、base、branch、worktree，并收紧实际路径。

## 禁止范围

不得修改 `src/`、`tests/`、QML/UI、依赖、用户源文件、现有 v1 migration、AGENTS 或其他既有规则语义。不得创建 SQLite adapter、运行迁移或把文档级验收写成产品 PASS。实现范围不得借本 Task 扩展到 Pipeline、StepResultCandidate、Constraint、TM、Provider 或发布打包。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| 文档 diff 无空白错误 | `git diff --check` | 当前仓库、2026-09-15 Codex 预审修订工作树 | PASS，退出码 0 | 本次 Codex 预审记录 |
| 设计与现状路径一致 | `Test-Path` 核对证据路径，`rg` 核对 schema/ports/Task/索引与设计断言 | 当前仓库、2026-09-15 | PASS，退出码 0 | 本次 Codex 预审记录 |
| SQLite 行为/重启/回滚 | 后续实现 Task 的 pytest 与迁移验证 | v2 adapter 已实现 | NOT_RUN；不属于本设计 Task | 无 |

## 依赖、风险与阻塞

硬依赖：[TASK-002](TASK-002.md)、[TASK-006](TASK-006.md)、[TASK-007](TASK-007.md)、[TASK-008](TASK-008.md)，均已在 master 集成 done。TASK-011 不是本设计 Task 的硬依赖，但其 Pipeline Lock 重读与 StepResultCandidate 落库必须继续遵守本设计的 current/文件边界。

主要风险是把已有两个 Region Repository 调用误当作一个 SQLite 原子提交；设计已将确切的 `commit_region_revision` 逻辑 seam 列为后续实现前置条件。v1 结构占位 Page 不得通过猜测源数据回填；`managed_original_ref` 与 D03 字段名差异在产品文档同步前不得静默合并。

## Review findings disposition

- **F-01 fixed**：删除重复且含 `UNIQUE(name)` 的 `tags` 表定义，保留应用层 `DuplicateTagName` 检查；复审 approved。
- **F-02 fixed**：补齐 Page `review_state`/`overall_status` 非 NULL 值域 CHECK 约定，并明确 Region current/restored 复合外键使用 `DEFERRABLE INITIALLY DEFERRED`；复审 approved。
- **F-03 fixed**：明确不预留实现 Task 编号；后续实现必须由 Codex 新建 implementation Task，并在 `ready` 前登记承接编号、owner、reviewer、基线和收紧范围；复审 approved。
- **F-04 resolved at integration**：TASK-028 状态已按协作协议完成从 `changes_requested` 到最终 `done` 的收口；集成记录已补齐。

## 交付与运行记录

- 设计：[TASK-028 统一 SQLite 持久化设计](../contracts/TASK-028_UNIFIED_SQLITE_PERSISTENCE_DESIGN.md)。
- Handoff：尚无；当前未释放实现。
- Review：[首轮 TASK-028-f9f2811](../reviews/TASK-028-f9f2811.md)，`report_commit=52754ca`，decision=`changes_requested`；[复审 TASK-028-e7f9e41](../reviews/TASK-028-e7f9e41.md)，`reviewed_head=e7f9e41`，`report_commit=09108d1`，decision=`approved`。
- 实际测试：DSH 对 `4a1df8f..e7f9e41` 执行 `git diff --check`、范围与 F-01～F-03 复核均 PASS；Codex 对集成范围执行 `git diff --check 4a1df8f 509de66` 并确认仅文档变更。产品 SQLite 迁移、round-trip、重启、回滚和 Region 原子提交测试仍 NOT_RUN，不因本设计集成而宣称完成。
- 集成结果：Review 报告 merge=`509de668ea9529e7b2a38abd2368df0ff02a64ae`；`integration_commit` 已记录为该提交，TASK-028 status=`done`。当前授权仍不包含 SQLite implementation Task，因此未创建或释放后续实现 Task。
- 最近状态：2026-09-15 DeepSeek Harness 复审 `e7f9e41` approved；Codex 已按协作协议串行集成 Review 报告并完成 TASK-028 设计收口。本 Task 完成设计但不代表 SQLite 实现可用。
