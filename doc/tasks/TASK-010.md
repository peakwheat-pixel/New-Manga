---
id: TASK-010
title: 实现翻译约束、TM 与 Context
kind: implementation
status: in_progress
approval: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-008, TASK-009]
base_commit: 2bdfd6f82b67a550c0550ee930d49bdb12656322
branch: agent/zcode/TASK-010-translation-context
worktree: G:/CODEX/New Manga.worktrees/TASK-010-zcode
integration_commit: null
---

# TASK-010：实现翻译约束、TM 与 Context

本 Task 已获用户批准释放，当前状态为 `ready`；尚未认领或实施。Owner 为 ZCode，Reviewer 为 DeepSeek Harness。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §12～14/28；D06 §9～18/85；D08 AC-SFX/CONSTRAINT/TM/TRANS。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-SFX-001、AC-SFX-002、AC-SFX-003、AC-CONSTRAINT-001、AC-CONSTRAINT-002、AC-CONSTRAINT-003、AC-CONSTRAINT-004、AC-TM-001、AC-TM-002、AC-TM-003、AC-TM-004、AC-TRANS-003、AC-TRANS-004。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 约束Chapter>Book>Global，同层人工优先；候选active/pending/rejected/disabled与Revision符合冻结契约。
- [ ] TM仅写入人工确认/已校对文本，支持作品Exact/Fuzzy再全局匹配、来源回溯与批准的禁用操作。
- [ ] Context按Page/Region顺序和预算构建，冻结Run有效约束并限定输出目标；SFX全部分支遵守TASK-002决定。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/domain/constraints/**
- src/application/translation/context/**
- src/application/translation/knowledge/**
- tests/knowledge/**
- doc/tasks/TASK-010.md
- doc/handoffs/TASK-010-*.md
- verification/TASK-010/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/knowledge；覆盖优先级冲突、重复Rejected、未确认TM不写、上下文越界输出拒绝。
- Run中改术语不影响已冻结值；Webtoon以Region窗口而非Tile作为上下文。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-008](TASK-008.md)、[TASK-009](TASK-009.md)。依赖必须已经集成 done 才可开始。

Exact/Fuzzy阈值依获批规格，不能自行添加Embedding/RAG。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-15 ZCode 在指定 worktree 接管开始执行，状态 ready → in_progress。基线核验通过：HEAD=`2cceb1e`（release commit）、base=`2bdfd6f` 为祖先，分支/worktree 如派单，common dir=`G:/CODEX/New Manga/.git`，工作区干净。白名单核对：src/domain/constraints、src/application/translation/{context,knowledge} 与 tests/knowledge 当前均不存在，属本 Task 拟议新增边界。
- 认领记录：2026-09-15 ZCode 认领实施，Reviewer=DeepSeek Harness（非作者）。
