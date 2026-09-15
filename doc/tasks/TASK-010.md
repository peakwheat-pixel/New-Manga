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

本 Task 已获用户批准释放并由 ZCode 认领实施（`in_progress`）。Owner 为 ZCode，Reviewer 为 DeepSeek Harness。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §12～14/28；D06 §9～18/85；D08 AC-SFX/CONSTRAINT/TM/TRANS。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-SFX-001、AC-SFX-002、AC-SFX-003、AC-CONSTRAINT-001、AC-CONSTRAINT-002、AC-CONSTRAINT-003、AC-CONSTRAINT-004、AC-TM-001、AC-TM-002、AC-TM-003、AC-TM-004、AC-TRANS-003、AC-TRANS-004。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 约束Chapter>Book>Global，同层人工优先；候选active/pending/rejected/disabled与Revision符合冻结契约。
- [x] TM仅写入人工确认/已校对文本，支持作品Exact/Fuzzy再全局匹配、来源回溯与批准的禁用操作。
- [x] Context按Page/Region顺序和预算构建，冻结Run有效约束并限定输出目标；SFX全部分支遵守TASK-002决定。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。（Handoff 与自验已交付，待 Review + 集成）

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
- 实际结果：全部已执行并覆盖，见 [verification/TASK-010/author-verification.md](../../verification/TASK-010/author-verification.md)（含 AC→测试映射）。

## 依赖、风险与阻塞

硬依赖：[TASK-008](TASK-008.md)、[TASK-009](TASK-009.md)。依赖必须已经集成 done 才可开始。

Exact/Fuzzy阈值依获批规格，不能自行添加Embedding/RAG。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：[TASK-010-cd76d30.md](../handoffs/TASK-010-cd76d30.md)（delivery_head=`cd76d30fdc561eb8f22a849eeb5989473957dc5b`，awaiting_review）。
- Review：尚无（等待 DeepSeek Harness 独立 Review）。
- 实际执行/实验/测试：[verification/TASK-010/author-verification.md](../../verification/TASK-010/author-verification.md)——2026-09-15，Windows 10.0.26200，Python 3.12.3 / pytest 9.1.1；四命令（tests/knowledge 78 passed；全量 328 passed×3 稳定；架构守卫 4 passed；`git diff --check 2cceb1e..cd76d30` 无输出）退出码全 0；范围核对全部位于白名单。
- 最近状态：2026-09-15 实现与自验完成，分支 HEAD=`cd76d30`；停止等待独立 Review，不自行合并 master。移交项：tests/rendering 全量顺序依赖缺陷（pre-existing，base `2bdfd6f` 干净树复现 `2 failed`，单独跑全过；证据与命令在 author-verification）。
- 认领记录：2026-09-15 ZCode 认领实施，Reviewer=DeepSeek Harness（非作者）。
