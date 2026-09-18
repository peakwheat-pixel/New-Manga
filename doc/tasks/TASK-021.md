---
id: TASK-021
title: 完善备份恢复、回收站、清理与诊断
kind: implementation
status: done
approval: approved_by_user
suggested_owner: Codex
owner: ZCode
reviewer: Codex
depends_on: [TASK-006, TASK-011, TASK-015]
base_commit: 047164ea080651741b38b20a36470115d4830a0d
branch: agent/zcode/TASK-021-backup-trash-cleanup-diagnostics
worktree: G:/CODEX/New Manga.worktrees/TASK-021-zcode
integration_commit: 5bc17f8cb0af682578166357a2c4ba8eedab644c
---

# TASK-021：完善备份恢复、回收站、清理与诊断

**READY（2026-09-18 ZCode 全权窗口 W7——条件执行）**：用户批准解冻（依赖 TASK-006/011/015 均已 `done`）。Owner 由建议的 `Codex` 改为 `ZCode`；Reviewer=窗口内子 agent（结论仅 `approved_subagent`）；`base=047164e`；branch/worktree 见顶部元数据。

**启动门**：**仅当 TASK-038 与 TASK-039 均于 `06:30` 前完成集成**才启动；且必须在 **08:20 前完成一个"连贯可集成子集"的集成**。

**"连贯子集"要求（重要）**：本 Task 的 4 个 AC 覆盖面很大（软删除/回收站、SQLite 一致性备份与恢复、缓存/版本/模型清理分离、日志轮转与诊断包），**不要试图一次全做**。启动时先选定**一个自洽子集**（建议从 AC「软删除和同batch恢复、明确永久删除只作用受控数据」开始），把它**完整做完并集成**（含测试、取证、子 agent Review），再视剩余时间决定是否继续下一个子集。**宁可只交付一个完整子集，也不要留下多个半成品**；窗口结束时未开始的子集按原样留在 Task 中，未完成的子集须在窗口报告中如实登记为 `frozen`。

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §32～34/45；D07 §37～62/90～92；D08 AC-BACKUP/TRASH/CACHE/DISK/LOG/CLEAN。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-DB-003、AC-DB-004、AC-BACKUP-001、AC-BACKUP-002、AC-BACKUP-003、AC-BACKUP-004、AC-TRASH-001、AC-TRASH-002、AC-TRASH-003、AC-TRASH-004、AC-CACHE-001、AC-CACHE-002、AC-CACHE-003、AC-DISK-001、AC-LOG-001、AC-LOG-002、AC-LOG-003、AC-CLEAN-001、AC-CLEAN-002、AC-CLEAN-003。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 软删除和同batch恢复、明确永久删除只作用受控数据；保留用户源文件。
- [ ] SQLite一致性备份、迁移前备份、恢复前备份、完整性和版本检查；失败不留下半迁移可写DB。
- [ ] 缓存/版本/模型清理分开，保护current/pinned/活动输入输出/备份引用，低磁盘可诊断。
- [ ] 日志轮转、错误定位、诊断包默认无Secret/原图/完整Prompt；数据/版本/模型metadata可追溯。
- [x] **子集交付**（软删除/同 batch 恢复/永久删除只作用受控数据）：Handoff=[doc/handoffs/TASK-021-887e0d6.md](../handoffs/TASK-021-887e0d6.md)；Review=[doc/reviews/TASK-021-887e0d6.md](../reviews/TASK-021-887e0d6.md)（**approved_subagent**，报告 commit `a9b4141`，四轴 executed；R-001 P2 open 登记处置计划、R-002~R-004 P3 不阻断）；集成=`5bc17f8`（merge，parents `22eafa8`+`a9b4141`），集成后复验全仓 **786 passed / 0 skipped**、exit 0。**其余子集（备份/恢复、缓存/版本/模型清理、日志/诊断包）frozen**——窗口时间预算下的取舍（round2 指令：只交付一个完整子集）。
- [ ] 备份/恢复子集：frozen（未开始，恢复条件=后续窗口或常规释放）。
- [ ] 缓存/版本/模型清理子集：frozen（同上）。
- [ ] 日志轮转与诊断包子集：frozen（同上）。

## 允许修改范围

**已由 Codex 按实际结构收紧（2026-09-18，窗口授权）**：原草案的 6 条路径（`src/application/maintenance/**`、`src/infrastructure/backup/**`、`src/infrastructure/diagnostics/**`、`src/infrastructure/sqlite/migrations/**`、`src/infrastructure/filesystem/cleanup/**`、`tests/reliability/**`）**当前全部不存在**，已替换为下列实测结构。"不得扩展到整个 `src/tests`"仍然有效。

- `src/application/maintenance/**`（**新建**：备份/恢复/回收站/清理/诊断的用例层）
- `src/infrastructure/filesystem/**`（存在：managed storage；回收站/清理/诊断包的落盘实现归此）
- `src/infrastructure/sqlite/**`（存在：一致性备份/恢复的 SQLite 侧工具；**注意本 Task 禁止 Schema/migration 变更**）
- `src/bootstrap/app.py`（存在：新用例的装配点）
- `tests/storage/**`、`tests/core/**`（存在；本 Task 的可靠性/故障注入用例归此）
- `doc/tasks/TASK-021.md`、`doc/handoffs/TASK-021-*.md`、`verification/TASK-021/**`

**若实现需要 Schema/migration 变更**（例如为软删除/回收站补列或表）→ **停下并回抛 Codex 裁决**，不得自行改动（窗口排除项明确禁止 Schema/migration）。

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/reliability；迁移/恢复/永久清理故障注入、活跃任务清理、损坏/缺文件。
- 源Hash、Pin保留、备份可实际恢复、secret扫描、旧App拒写新Schema。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-006](TASK-006.md)、[TASK-011](TASK-011.md)、[TASK-015](TASK-015.md)。依赖必须已经集成 done 才可开始。

永久删除实现只在测试目录演练，不对用户真实漫画库运行。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
- **最近状态（当前，唯一）**：2026-09-18 04:5x 由 ZCode 在窗口第二轮开工（W7，status→`in_progress`；启动门达标：TASK-038 `f835ac9` + TASK-039 `c8024fe` 均于 06:30 前集成）；分支 `git merge master` 快进至 `22eafa8`。**自洽子集选定**：AC「软删除和同 batch 恢复、永久删除只作用受控数据」（Page 级）。**Schema 预检通过**：books/chapters/pages 均已有 `deleted_at` 列（schema :36/:46/:56）、`soft_delete_page` 已存在（library.py:371）——无需回抛 Schema。
- **最近状态（当前，唯一）**：子集实现 head=`887e0d6`（repository trash 4 方法 + `remove_managed` 防逃逸 + `application/maintenance/` 新子包 + `TrashService` 装配 + `tests/storage/test_trash.py` 5 例 + 装配契约 1 例，全过；library 回归含在 mandated）。Review `a9b4141`=**approved_subagent**（四轴 executed；R-001 **P2 open**＝跨 batch 重叠 page_id 的 API 层串扰——集成后修复/并入 trash 后续子集，处置计划已登记；R-002~R-004 P3 不阻断）。集成 `5bc17f8`（复验 786 passed）；**R-001 P2 已修订收口**（修订 head=`0fe634f`、复审 `79ec0d2`=approved_subagent、修订集成=`b940497`、复验全仓 **787 passed/0 skipped** exit 0）。**本子集已收口 done；其余子集 frozen；期满后须 Codex + DSH 外部 post-hoc 复审（可推翻）。**
