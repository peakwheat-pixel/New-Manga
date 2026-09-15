---
id: TASK-006
title: 实现持久化与 Artifact 安全提交基础
kind: implementation
status: ready
approval: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-005]
base_commit: fb29dfedc496cde61cea9ea2558ef274e94eb49e
branch: agent/zcode/TASK-006-persistence-artifact
worktree: G:/CODEX/New Manga.worktrees/TASK-006-zcode
integration_commit: null
---

# TASK-006：实现持久化与 Artifact 安全提交基础

本 Task 已获用户批准并释放，由 ZCode 承接；当前仅完成交接准备，尚未开始实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §16～18/34/37～43；D07 §28～38；D08 AC-ART/DB/REV。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-REV-001、AC-REV-002、AC-ART-001、AC-ART-002、AC-ART-003、AC-DB-001、AC-DB-002、AC-DB-005。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 实现首个切片实际使用的 Schema、外键、索引和短事务边界；按 TASK-002 的契约使用不可变版本路径及 current 引用。
- [ ] Artifact 写入/验证/正式版本发布/metadata commit 任一点失败均保留旧 current；数据库不能指向不存在的新文件。
- [ ] 定义 migration 版本/checksum与备份入口、新 Schema 旧 App 拒写；保护 current/pinned/活动输入引用。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

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
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-005](TASK-005.md)。依赖必须已经集成 done 才可开始。

初版仅建实际切片需要的表，剩余表通过版本化迁移；迁移/恢复端到端由 TASK-021补足。

如本 Task 需要新的契约或用户范围决定而输入仍未就绪，登记具体 blocker 并停止实施；不得借此扩大允许范围。Owner 与 Reviewer 必须保持不同。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-15 用户批准释放；ready，Owner=ZCode，Reviewer=DeepSeek Harness，base=`fb29dfedc496cde61cea9ea2558ef274e94eb49e`；尚未开始实施。
