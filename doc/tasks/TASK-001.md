---
id: TASK-001
title: 修订目标文档引用与已确定的一致性问题
kind: design
status: in_progress
approval: approved
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: []
base_commit: 496b4ed
branch: agent/codex/TASK-001-doc-consistency
worktree: G:/CODEX/New Manga
integration_commit: null
---

# TASK-001：修订目标文档引用与已确定的一致性问题

本 Task 已由用户于 2026-09-13 授权，由 Codex 执行；其他 Task 与新功能开发继续冻结。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D01 §5；D02 §5；D03 §10/20/22/24/34；D04 §30；D06 §10/71/105；D07 §115；G03/G04/G05/G09/G14。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-DOC-001、AC-DOC-003。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 将历史长文件名引用改为实际文件；旧代码能力注明来源未提供，不能声明本仓库实现。
- [x] 对 D03 已补齐项逐项关闭过时同步建议，避免重复添加字段。
- [x] 对重试新 Run、冻结约束、NFR 与 Release Gate 冲突给出逐条修订；需要用户产品决定的项保留待决，不擅自改标准。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径。Codex 于 2026-09-13 核对范围，仅补入 `doc/STATUS.md` 用于登记本 Task 授权与进度；不涉及应用源码。

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
- doc/12_ROADMAP.md
- doc/13_ACCEPTANCE_TRACEABILITY.md
- doc/STATUS.md
- doc/tasks/README.md
- doc/tasks/TASK-001.md
- doc/handoffs/TASK-001-*.md
- doc/reviews/TASK-001-*.md
- verification/TASK-001/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 逐份检查受影响段落与链接，并比较原始指纹快照。
- 列出修改前后语义及对应 D08 条目；独立 Reviewer 确认未扩大/缩减产品范围。
- 在 `verification/TASK-001/` 留下可重复执行的最小文档检查。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：无前置 Task；用户已释放本 Task。其他 Task 必须继续保持 proposed。

初始项目基线为 `496b4ed`；本任务修改目标文档不代表冻结 Schema。

DeepSeek Harness 已在 `G:/CODEX/New Manga.worktrees/TASK-001-deepseek-review` 接入同一 Git common directory，分支为 `agent/deepseek/TASK-001-review`。首次 Review 固定 `base_commit=496b4ed`、`reviewed_head=615a073`，decision 为 `changes_requested`。

Reviewer 获准运行 `pwsh -NoProfile -File ./verification/TASK-001/verify.ps1`，并且只在 `doc/reviews/TASK-001-*.md` 写本 Task 的独立 Review / 复审报告。每份报告固定自己的 reviewed_head；发现问题时记录 finding，不修改 TASK-001 作者交付。

## 交付与运行记录

- Handoff：[TASK-001-615a073](../handoffs/TASK-001-615a073.md)，交付提交 `615a073c0cef479157d472d3fc9823e0087b46a1`。
- Review：[615a073 独立 Review](../reviews/TASK-001-615a073.md) 已完成，decision=`changes_requested`（P0=0、P1=1、P2=9）；Codex 正在逐项修订，之后提交新 head 复审。
- 实际执行：已修订 D01～D08 及索引/Gap/派生视图；[检查脚本](../../verification/TASK-001/verify.ps1) 已执行，退出码 0。勾选项为作者完成并自查，尚非独立批准。
- 最近状态：2026-09-13 DeepSeek Review 要求修改；Owner 已恢复 in_progress。独立复审与集成未完成，integration_commit 仍为空。
