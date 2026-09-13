---
id: TASK-007
title: 实现书架领域与本地图片导入
kind: implementation
status: proposed
approval: pending_user_review
suggested_owner: ZCode
owner: null
reviewer: null
depends_on: [TASK-006]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-007：实现书架领域与本地图片导入

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §3～5/30；D04 §4～10；D07 §37～39；D08 AC-LIB/CH/IMPORT/PAGE。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-LIB-001、AC-LIB-002、AC-LIB-003、AC-CH-001、AC-CH-002、AC-CH-003、AC-CH-004、AC-IMPORT-001、AC-IMPORT-002、AC-IMPORT-003、AC-IMPORT-004、AC-IMPORT-005、AC-PAGE-001。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 支持 Book/Chapter CRUD、paged/webtoon、阅读方向、标签/收藏/归档分离、章节/页序与原始导入顺序。
- [ ] 图片/文件夹导入执行 Managed Copy、decode验证、hash去重与排序；取消/损坏/复制失败不留可处理坏Page。
- [ ] 应用用例通过已批准Repository契约工作；不写QML、不新增Volume。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/domain/books/**
- src/domain/pages/**
- src/application/library/**
- src/application/importing/images/**
- tests/library/**
- doc/tasks/TASK-007.md
- doc/handoffs/TASK-007-*.md
- verification/TASK-007/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/library；CRUD重启持久化、Tag删除不删Book、混合章节、重复/损坏/透明图。
- 中文/日文/韩文/emoji路径与源文件前后Hash一致；导入中断可恢复。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-006](TASK-006.md)。依赖必须已经集成 done 才可开始。

PDF/MOBI/网页导入属于 TASK-023；Schema新增需Codex协调 TASK-006边界。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
