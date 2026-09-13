---
id: TASK-021
title: 完善备份恢复、回收站、清理与诊断
kind: implementation
status: proposed
approval: pending_user_review
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [TASK-006, TASK-011, TASK-015]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-021：完善备份恢复、回收站、清理与诊断

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §32～34/45；D07 §37～62/90～92；D08 AC-BACKUP/TRASH/CACHE/DISK/LOG/CLEAN。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-DB-003、AC-DB-004、AC-BACKUP-001、AC-BACKUP-002、AC-BACKUP-003、AC-BACKUP-004、AC-TRASH-001、AC-TRASH-002、AC-TRASH-003、AC-TRASH-004、AC-CACHE-001、AC-CACHE-002、AC-CACHE-003、AC-DISK-001、AC-LOG-001、AC-LOG-002、AC-LOG-003、AC-CLEAN-001、AC-CLEAN-002、AC-CLEAN-003。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 软删除和同batch恢复、明确永久删除只作用受控数据；保留用户源文件。
- [ ] SQLite一致性备份、迁移前备份、恢复前备份、完整性和版本检查；失败不留下半迁移可写DB。
- [ ] 缓存/版本/模型清理分开，保护current/pinned/活动输入输出/备份引用，低磁盘可诊断。
- [ ] 日志轮转、错误定位、诊断包默认无Secret/原图/完整Prompt；数据/版本/模型metadata可追溯。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/application/maintenance/**
- src/infrastructure/backup/**
- src/infrastructure/diagnostics/**
- src/infrastructure/sqlite/migrations/**
- src/infrastructure/filesystem/cleanup/**
- tests/reliability/**
- doc/tasks/TASK-021.md
- doc/handoffs/TASK-021-*.md
- verification/TASK-021/**

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
