---
id: TASK-022
title: 补齐工具窗口、设置与视觉交互验收
kind: implementation
status: proposed
approval: pending_user_review
suggested_owner: Qoder
owner: null
reviewer: null
depends_on: [TASK-009, TASK-010, TASK-013, TASK-015, TASK-021, TASK-024]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-022：补齐工具窗口、设置与视觉交互验收

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

2026-09-19 用户指定 Qoder 为 UI/UX、GUI 与 QML 视觉/交互设计责任方。先由 [TASK-059](TASK-059.md) 冻结视觉方向与信息架构（**原 [TASK-047](TASK-047.md) 已被用户否决 `rejected`，设计门改挂 TASK-059**）；本 Task 仍保持 `proposed`，待 TASK-059 `done`、全部硬依赖满足并由用户批准释放后，才可进入实现。

## 来源与目标

D05 §4～5/13～14/30/43～55/64～67；D01 §2字体上传；D08 AC-WIN/DPI/CLOSE。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-WIN-001、AC-WIN-002、AC-WIN-003、AC-WIN-004、AC-WIN-005、AC-WIN-006、AC-CLOSE-001、AC-CLOSE-002。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 接入Constraint/TM/Revision/Provider/Network/回收站/Backup工具窗及设置；所有动作有实际用例，不以空占位作为完成。
- [ ] 落实非模态双屏、尺寸/最大化、屏幕消失恢复、Footer可达、编辑外部不关闭、Dirty保存/放弃/取消。
- [ ] 字体选择/上传按已批准范围验证文件和资源；显示设置继承来源、远程数据与危险TLS/代理选项。
- [ ] 关闭应用分别处理未保存编辑与运行任务；不新建第五个一级Route。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/ui/qml/windows/**
- src/ui/qml/settings/**
- src/ui/viewmodels/windows/**
- src/ui/viewmodels/settings/**
- src/ui/qml/common/**
- src/application/fonts/**
- tests/windows_settings/**
- doc/ui-baseline.md
- doc/tasks/TASK-022.md
- doc/handoffs/TASK-022-*.md
- verification/TASK-022/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/windows_settings；ViewModel契约与窗口行为测试。
- 100/125/150/175/200%DPI、不同DPI双屏、失去显示器、长中日韩文本/文件名、键盘焦点与Disabled截图。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-009](TASK-009.md)、[TASK-010](TASK-010.md)、[TASK-013](TASK-013.md)、[TASK-015](TASK-015.md)、[TASK-021](TASK-021.md)、[TASK-024](TASK-024.md)。依赖必须已经集成 done 才可开始。

视觉基线不是已有UI截图；新增视觉选择需按TASK-012流程确认。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。

> **2026-09-19 ZCode 全权窗口条目**：本 Task 已纳入 [STATUS](../STATUS.md) 的窗口队列（W12+ 尾项），但**门槛未达成**：需 **TASK-021 三子集（TASK-055/056/057）** + **TASK-059 设计门（Qoder；原 TASK-047 已被否决，改挂 TASK-059）** + **TASK-050（W3，绑定写入面）** 全部完成。门槛满足前一律记 `BLOCKED（前置未达成）`，**不得跳过前置强行开工**；窗口内如需调整门槛，由 Codex 在 T1 后处理。
