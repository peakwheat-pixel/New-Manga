---
id: TASK-010
title: 实现翻译约束、TM 与 Context
kind: implementation
status: done
approval: approved
decision: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-008, TASK-009]
base_commit: 2bdfd6f82b67a550c0550ee930d49bdb12656322
branch: agent/zcode/TASK-010-translation-context
worktree: G:/CODEX/New Manga.worktrees/TASK-010-zcode
reviewed_head: cd76d30fdc561eb8f22a849eeb5989473957dc5b
implementation_merge: 1ea9c80fe29d33da33d533e22278cd2f474cb31a
integration_commit: a225790d5eaf90227249039255bb554307f5b2cc9
review_report_commit: 008b1013a9863f4f506764d17d01245cb2403db1
---

# TASK-010：实现翻译约束、TM 与 Context

本 Task 已完成实现、独立 Review 与 Codex 串行集成（`done`）。Review decision=`approved`；Owner 为 ZCode，Reviewer 为 DeepSeek Harness。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §12～14/28；D06 §9～18/85；D08 AC-SFX/CONSTRAINT/TM/TRANS。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-SFX-001、AC-SFX-002、AC-SFX-003、AC-CONSTRAINT-001、AC-CONSTRAINT-002、AC-CONSTRAINT-003、AC-CONSTRAINT-004、AC-TM-001、AC-TM-002、AC-TM-003、AC-TM-004、AC-TRANS-003、AC-TRANS-004。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 约束Chapter>Book>Global，同层人工优先；候选active/pending/rejected/disabled与Revision符合冻结契约。
- [x] TM仅写入人工确认/已校对文本，支持作品Exact/Fuzzy再全局匹配、来源回溯与批准的禁用操作。
- [x] Context按Page/Region顺序和预算构建，冻结Run有效约束并限定输出目标；SFX全部分支遵守TASK-002决定。
- [x] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后完成。

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

Exact/Fuzzy 阈值已在 D03 §12.5/§14.4 登记为 `0.90`/`0.80` 的可调实现参数；不能自行添加 Embedding/RAG。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：[TASK-010-cd76d30.md](../handoffs/TASK-010-cd76d30.md)（delivery_head=`cd76d30fdc561eb8f22a849eeb5989473957dc5b`，已集成）。
- Review：[TASK-010-cd76d30.md](../reviews/TASK-010-cd76d30.md)，`report_commit=008b101`，decision=`approved`，无 P0/P1。
- 实际执行/实验/测试：[verification/TASK-010/author-verification.md](../../verification/TASK-010/author-verification.md)——2026-09-15，Windows 10.0.26200，Python 3.12.3 / pytest 9.1.1；tests/knowledge 78 passed；全量 322 passed, 6 skipped×3 稳定（6 项均因 `openssl unavailable`）；架构守卫 4 passed；`git diff --check 2cceb1e..cd76d30` 无输出。集成复验见 [integration-a225790.md](../../verification/TASK-010/integration-a225790.md)。
- 最近状态：2026-09-16 实现合并 `1ea9c80`、Review 报告合并并收口 `a225790`；F-01/F-02 已关闭。tests/rendering 顺序依赖仍未复现，已指派 ZCode 补充最小复现，期间不修改该套件，见 [rendering-order-repro.md](../../verification/TASK-010/rendering-order-repro.md)。
- 认领记录：2026-09-15 ZCode 认领实施，Reviewer=DeepSeek Harness（非作者）。

## Review findings disposition

| finding | disposition |
|---|---|
| F-01 全量计数口径 | **closed**：集成后为 `322 passed, 6 skipped`；6 项均因 `openssl unavailable`。 |
| F-02 两个未登记阈值 | **closed**：D03 §12.5/§14.4 已登记 `0.90`/`0.80`，均为可调实现参数。 |
| tests/rendering 顺序依赖 | **NOT_REPRODUCED**：Reviewer 与 Codex 均未复现；等待原报告者提供最小复现，未修改套件。 |
