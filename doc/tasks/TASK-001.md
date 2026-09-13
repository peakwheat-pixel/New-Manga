---
id: TASK-001
title: 修订目标文档引用与已确定的一致性问题
kind: design
status: proposed
approval: pending_user_review
suggested_owner: Codex
owner: null
reviewer: null
depends_on: []
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-001：修订目标文档引用与已确定的一致性问题

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D01 §5；D02 §5；D03 §10/20/22/24/34；D04 §30；D06 §10/71/105；D07 §115；G03/G04/G05/G09/G14。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-DOC-001、AC-DOC-003。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 将历史长文件名引用改为实际文件；旧代码能力注明来源未提供，不能声明本仓库实现。
- [ ] 对 D03 已补齐项逐项关闭过时同步建议，避免重复添加字段。
- [ ] 对重试新 Run、冻结约束、NFR 与 Release Gate 冲突给出逐条修订；需要用户产品决定的项保留待决，不擅自改标准。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- doc/01_FUNCTIONAL_ARCHITECTURE.md
- doc/02_TECHNICAL_ARCHITECTURE_.md
- doc/03_DATA_MODEL.md
- doc/04_USER_FLOW.md
- doc/05_UI_MAPPING.md
- doc/06_TRANSLATION_PIPELINE.md
- doc/07_NON_FUNCTIONAL_REQUIREMENTS.md
- doc/08_ACCEPTANCE_CRITERIA.md
- doc/00_INDEX.md
- doc/10_CURRENT_STATE_AND_GAPS.md
- doc/11_ARCHITECTURE_MAPS.md
- doc/tasks/TASK-001.md
- doc/handoffs/TASK-001-*.md
- verification/TASK-001/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 逐份检查受影响段落与链接，并比较原始指纹快照。
- 列出修改前后语义及对应 D08 条目；独立 Reviewer 确认未扩大/缩减产品范围。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：无前置 Task，但仍需用户审核与阶段释放。依赖必须已经集成 done 才可开始。

无项目 HEAD，先由 Codex在获准后提交接管基线；本任务修改目标文档不代表冻结 Schema。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
