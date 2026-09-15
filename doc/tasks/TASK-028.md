---
id: TASK-028
title: 冻结统一 SQLite 持久化设计
kind: design
status: proposed
approval: approved
suggested_owner: Codex
owner: Codex
reviewer: null
depends_on: [TASK-006, TASK-007, TASK-008]
base_commit: 4a1df8fb5bc90e1542113c5ae3b15cb837146f79
branch: master
worktree: G:/CODEX/New Manga
integration_commit: null
---

# TASK-028：冻结统一 SQLite 持久化设计

本 Task 只冻结后续实现所需的 SQLite 数据归属、Schema 迁移方向、Adapter seam、事务不变量和范围边界；实现尚未释放。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

来源：TASK-002 最小数据与执行契约 §2、§8、§10；TASK-006/007/008 的已集成实现、Task 边界和 Review 遗留；D02 §6/13、D03 §3～16/34、D07 §28/34/37～50、D08 AC-DB/REV/ART。唯一设计交付物为[统一 SQLite 持久化设计](../contracts/TASK-028_UNIFIED_SQLITE_PERSISTENCE_DESIGN.md)。

当前可观察目标：统一数据库承载 Book/Chapter/Page/Tag/Region/RegionRevision/Artifact 元数据，保持现有消费侧契约和 Artifact 安全提交语义；不提前实现 Pipeline 或 UI。

## Acceptance Criteria

- [x] 记录当前 v1 Schema、TASK-006 Artifact adapter、TASK-007/008 消费侧契约及其真实差距。
- [x] 固定“共享连接 + 按契约拆分 Adapter”的架构，并记录拒绝独立数据库、巨型 Repository 和无必要端口搬迁的原因。
- [x] 固定 v2 迁移的表归属、字段映射、Region current/revision 约束、v1 结构占位 Page 的兼容规则和 Artifact 不变边界。
- [x] 固定短事务、`BEGIN IMMEDIATE` compare-and-write、重启、回滚和源文件保护原则，并明确 Region 两调用不能冒充原子提交。
- [x] 列出后续实现允许/禁止路径和真实验收门槛；不修改业务代码、UI、现有规则或产品 AC 结果。
- [ ] 独立 Review 与 Codex 集成记录完成；在此之前不得把本设计 Task 或任何后续实现 Task 置为 done。

## 允许修改范围

本设计 Task 仅允许修改以下相对项目根目录的文档：

- `doc/contracts/TASK-028_UNIFIED_SQLITE_PERSISTENCE_DESIGN.md`
- `doc/tasks/TASK-028.md`
- `doc/tasks/README.md`
- `doc/00_INDEX.md`
- `doc/STATUS.md`
- `doc/12_ROADMAP.md`

后续实现的拟议源码白名单见设计文档 §5；释放实现时必须重新填写 owner、reviewer、base、branch、worktree，并收紧实际路径。

## 禁止范围

不得修改 `src/`、`tests/`、QML/UI、依赖、用户源文件、现有 v1 migration、AGENTS 或其他既有规则语义。不得创建 SQLite adapter、运行迁移或把文档级验收写成产品 PASS。实现范围不得借本 Task 扩展到 Pipeline、StepResultCandidate、Constraint、TM、Provider 或发布打包。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| 文档 diff 无空白错误 | `git diff --check` | 当前仓库 | planned；本 Task 收口时执行 | 待记录 |
| 设计与现状路径一致 | `rg` 核对 schema、ports、Task 和索引 | 当前仓库 | planned；本 Task 收口时执行 | 待记录 |
| SQLite 行为/重启/回滚 | 后续实现 Task 的 pytest 与迁移验证 | v2 adapter 已实现 | NOT_RUN；不属于本设计 Task | 无 |

## 依赖、风险与阻塞

硬依赖：[TASK-006](TASK-006.md)、[TASK-007](TASK-007.md)、[TASK-008](TASK-008.md)，均已在 master 集成 done。TASK-011 不是本设计 Task 的硬依赖，但其 Pipeline Lock 重读与 StepResultCandidate 落库必须继续遵守本设计的 current/文件边界。

主要风险是把已有两个 Region Repository 调用误当作一个 SQLite 原子提交；设计已将“Region + Revision + current pointer”原子 seam 列为后续实现前置条件。v1 结构占位 Page 不得通过猜测源数据回填。

## 交付与运行记录

- 设计：[TASK-028 统一 SQLite 持久化设计](../contracts/TASK-028_UNIFIED_SQLITE_PERSISTENCE_DESIGN.md)。
- Handoff：尚无；当前未释放实现。
- Review：尚无；`reviewer=null` 是事实记录，不代表已审查通过。
- 实际测试：尚无；设计 Task 收口前至少执行 `git diff --check` 与文档路径核对。
- 最近状态：2026-09-15 用户要求冻结统一 SQLite 持久化设计；本 Task 保持 `proposed`，仅冻结设计，不启动 ZCode/DeepSeek Harness 实现。
