---
id: TASK-002
title: 冻结最小数据与执行契约
kind: design
status: in_progress
approval: approved
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [TASK-001]
base_commit: b1b3f5d
branch: agent/codex/TASK-002-contract-freeze
worktree: G:/CODEX/New Manga
integration_commit: null
---

# TASK-002：冻结最小数据与执行契约

本 Task 已由用户于 2026-09-13 授权，由 Codex 执行；其他 Task 与功能开发继续冻结。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §6～24/38～43；D06 §24～33/48～79/85～94；D05 §14/30/53；G06～G13。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-DOC-002。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 定义 Region current revision、每目标输入/输出映射、原子 compare-and-write、人工来源/确认状态、Pin 与 TM 禁用存储；列出 FK/唯一性/NULL/枚举约束。
- [ ] 给出 Run/Task/Step/Stage/Decision 的分层状态表，覆盖 paused/cancelled/blocked/skip、空计划、全锁定、部分失败、Region/Book target 展开、Restart/Abandon。
- [ ] 统一几何/样式失效矩阵、SFX skip/manual 的图像处理策略、每 Step commit 与最终 Save、Region局部合成和故障清理契约。
- [ ] 记录最小 DTO/Port 和错误码、设置/Provider/Constraint 快照时点；每个契约给正常、边界、失败测试向量，更新对应 AC 后提交用户审核冻结。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- doc/03_DATA_MODEL.md
- doc/04_USER_FLOW.md
- doc/05_UI_MAPPING.md
- doc/06_TRANSLATION_PIPELINE.md
- doc/08_ACCEPTANCE_CRITERIA.md
- doc/00_INDEX.md
- doc/10_CURRENT_STATE_AND_GAPS.md
- doc/11_ARCHITECTURE_MAPS.md
- doc/12_ROADMAP.md
- doc/13_ACCEPTANCE_TRACEABILITY.md
- doc/STATUS.md
- doc/contracts/**
- doc/tasks/README.md
- doc/tasks/TASK-002.md
- doc/handoffs/TASK-002-*.md
- doc/reviews/TASK-002-*.md
- verification/TASK-002/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 用纸面事件序列演算：Revision10→人工12→后台返回、全锁定零 Step、38成功2失败、暂停/停止竞态、单 Region 合成。
- 检查所有新增数据字段/命令能映射至 UI、协议和 AC；不生成 SQL 或业务代码。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-001](TASK-001.md)，已在 `a1cb24c` 集成并标记 done；本 Task 基线为 `b1b3f5d`。

未解决的用户选择阻止相关契约冻结；不能仅增加一个字段就宣称并发保护完成。

用户已批准后续 TASK-002 设计取舍由 Codex 依据现有需求作最小冻结，不再逐项询问；不得据此扩大到其他 Task 或功能开发。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 用户批准启动；Codex 已认领，状态 `in_progress`。Reviewer 预留为 DeepSeek Harness。
