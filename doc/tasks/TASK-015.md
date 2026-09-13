---
id: TASK-015
title: 实现阅读器与五种成果导出
kind: implementation
status: proposed
approval: pending_user_review
suggested_owner: ZCode
owner: null
reviewer: null
depends_on: [TASK-012, TASK-014]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-015：实现阅读器与五种成果导出

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §29/31；D04 §33～37；D05 §37～42/51；D06 §96～97；D08 AC-READ/EXPORT。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-LIB-004、AC-EXPORT-001、AC-EXPORT-002、AC-EXPORT-003、AC-READ-001、AC-READ-002、AC-READ-003、AC-READ-004、AC-READ-005。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 实现Original/Translated两模式、RTL/LTR、独立阅读进度/时长与书架摘要；Webtoon完整按宽滚动由TASK-020验证。
- [ ] 单图/ZIP/CBZ/PDF/文本全部有范围、顺序、输出路径/命名/覆盖策略与ExportHistory。
- [ ] 导出stale明确提示先渲染或继续当前版本，写失败/取消保留原有目标文件和源文件。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/application/reading/**
- src/application/export/**
- src/ui/qml/reader/**
- src/ui/viewmodels/reader/**
- src/ui/qml/windows/ExportWindow.qml
- src/ui/viewmodels/export/**
- tests/reading_export/**
- doc/tasks/TASK-015.md
- doc/handoffs/TASK-015-*.md
- verification/TASK-015/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/reading_export；重启继续阅读、双模式独立、缺译图、五格式内容/页序/元数据。
- 非法/Unicode文件名、已有目标文件、磁盘错误和stale选择；验证导出产物可重新读取。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-012](TASK-012.md)、[TASK-014](TASK-014.md)。依赖必须已经集成 done 才可开始。

本任务实现导出不等于发布Gate通过；进度与Webtoon跨模块回归由TASK-020/026补齐。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
