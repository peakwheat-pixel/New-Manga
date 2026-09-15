---
id: TASK-006
title: 实现持久化与 Artifact 安全提交基础
kind: implementation
status: in_review
approval: approved
suggested_owner: Codex
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-005]
base_commit: fb29dfedc496cde61cea9ea2558ef274e94eb49e
branch: agent/zcode/TASK-006-persistence-artifact
worktree: G:/CODEX/New Manga.worktrees/TASK-006-zcode
integration_commit: null
---

# TASK-006：实现持久化与 Artifact 安全提交基础

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §16～18/34/37～43；D07 §28～38；D08 AC-ART/DB/REV。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-REV-001、AC-REV-002、AC-ART-001、AC-ART-002、AC-ART-003、AC-DB-001、AC-DB-002、AC-DB-005。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 实现首个切片实际使用的 Schema、外键、索引和短事务边界；按 TASK-002 的契约使用不可变版本路径及 current 引用。（v1 迁移最小表集；复合 DEFERRABLE FK 编码「current 同属」不变量；`BEGIN IMMEDIATE` 短事务；Managed 路径按 revision_id 命名且不可覆盖）
- [x] Artifact 写入/验证/正式版本发布/metadata commit 任一点失败均保留旧 current；数据库不能指向不存在的新文件。（失败矩阵 11 项测试全过：写失败、声明 hash 不符、发布后 DB 前崩溃注入、冲突、重复 revision_no、非法 FK、跨 artifact current 等；失败文件以 orphan 路径返回、不入库）
- [x] 定义 migration 版本/checksum与备份入口、新 Schema 旧 App 拒写；保护 current/pinned/活动输入引用。（checksummed MigrationRunner + pre-migration 备份钩子 + SQLite backup API BackupRecord；`TOO_NEW` 库以 query_only 只读打开（AC-DB-005）；pinned/完整性字段与备份入口就位，清理/恢复执行属 TASK-021）
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。（Handoff 已交付 [TASK-006-ba1e769](../handoffs/TASK-006-ba1e769.md)；待 DeepSeek Review + Codex 集成）

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/infrastructure/sqlite/**
- src/infrastructure/filesystem/**
- src/ports/repositories/**
- tests/storage/**
- doc/tasks/TASK-006.md
- doc/handoffs/TASK-006-*.md
- verification/TASK-006/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/storage；临时文件写失败、发布后DB前崩溃、事务失败、重复提交、非法FK、current跨artifact引用。
- 使用测试临时根目录与 Unicode 路径；验证源文件Hash不变。
- 以上已执行（2026-09-15，owner ZCode，head `ba1e769`）：`python -m pytest tests/storage -v` 退出码 0（29 passed）；`PYTHONPATH=src python -m pytest tests` 退出码 0（35 passed，含 TASK-005 架构守卫）。临时写失败、发布后 DB 前崩溃、事务失败、重复提交、非法 FK、current 跨 artifact 引用、Unicode 路径与源文件 Hash 不变均已覆盖。命令、环境、退出码与证据见 [verification/TASK-006/author-verification.md](../../verification/TASK-006/author-verification.md)。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-005](TASK-005.md)。依赖必须已经集成 done 才可开始。

初版仅建实际切片需要的表，剩余表通过版本化迁移；迁移/恢复端到端由 TASK-021补足。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：[TASK-006-ba1e769](../handoffs/TASK-006-ba1e769.md)（delivery_head=`ba1e7695a1ad806a2640fe077811ade95d3b90d4`）。
- Review：尚无；等待 DeepSeek Harness 独立 Review，报告将写入 `doc/reviews/TASK-006-*.md`（Owner 不写该路径）。
- 实际执行/实验/测试：[verification/TASK-006/author-verification.md](../../verification/TASK-006/author-verification.md)（命令、退出码、环境、NOT_RUN/N-A 清单）。
- 最近状态：2026-09-15 ZCode 完成实现并交付：ports（artifacts/storage/database 契约）+ SQLite 基础设施（PRAGMA 组合、v1 checksummed 迁移、pre-migration 备份入口、旧 App 只读门、§8.1 原子提交 ArtifactRepository）+ ManagedFileStorage（不可变发布、Unicode、完整性）+ 29 项 storage 测试全过、全量 35 passed。reviewed_head=`ba1e769`，状态 in_progress → in_review，等待独立 Review；未合并 master。
- 最近状态：2026-09-15 Codex 派单开始执行（base_commit=`fb29dfe`、worktree 与分支如上，Owner ZCode、Reviewer DeepSeek Harness）。基线核验通过：HEAD=`fb29dfe`（=派单 base）、工作区干净、common dir=`G:/CODEX/New Manga/.git`。流转补记：派单时本文件仍为 `proposed/pending_user_review`（ready 未单独落盘），按派单口径将 owner/approval/base/branch/worktree 填入并直接置 `in_progress`；ready 的释放事实以 Codex 派单指令为准。允许范围即本文件白名单，未扩大。
