---
id: TASK-008
title: 实现 Region 编辑、Revision 与人工保护
kind: implementation
status: proposed
approval: pending_user_review
suggested_owner: ZCode
owner: null
reviewer: null
depends_on: [TASK-007]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-008：实现 Region 编辑、Revision 与人工保护

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §6～11/15；D06 §29/87～90；D08 AC-REGION/TRANS/REV/AUTO。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-REGION-001、AC-REGION-002、AC-REGION-003、AC-REGION-004、AC-OCR-002、AC-TRANS-001、AC-TRANS-002、AC-REV-003、AC-REV-004。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 实现统一Region几何、类型、阅读顺序及新建/删除/合并/拆分，按原图坐标保存并重启恢复。
- [ ] 保存/确认四级文本与样式时产生正确Revision，人工编辑自动translation_locked；明确保存或获批autosave在切换前flush。
- [ ] 通过已冻结的原子写入契约检查输入Revision与Lock；恢复历史保留可追踪记录并按契约处理Pin/失效。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/domain/regions/**
- src/application/editing/**
- tests/editing/**
- doc/tasks/TASK-008.md
- doc/handoffs/TASK-008-*.md
- verification/TASK-008/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/editing；几何往返、reading_order、合并拆分、人工文本保存后重启。
- 重OCR保留人工final、后台10→人工12覆盖拒绝、空字符串/未确认文本的final解析、Dirty切换。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-007](TASK-007.md)。依赖必须已经集成 done 才可开始。

不自行定义review_state/Pin存储；以TASK-002冻结的约束为准。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
