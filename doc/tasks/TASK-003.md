---
id: TASK-003
title: 补齐验收规格与测试素材规范
kind: verification-design
status: proposed
approval: pending_user_review
suggested_owner: DeepSeek Harness
owner: null
reviewer: null
depends_on: [TASK-002]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-003：补齐验收规格与测试素材规范

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D08 全文，尤其 §4/6/67～72；D07 §98～101；G14/G17。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：本任务为设计/实验/基础工作，验收以下专属条件；关联产品 AC 不因本任务完成就自动 PASS。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 审阅现有185条及所有组级要求，补齐未编号要求的稳定标识、执行方式、环境与证据口径；不降低 P0/P1。
- [ ] 为日漫/韩漫/Webtoon/损坏图/透明PNG/Unicode/重复图/大metadata提供素材清单、许可与生成方案；未取得素材标缺失。
- [ ] 为模型质量制定可审查的评估方法和待批准阈值，为性能固定运行次数/环境/P95口径；未测量不填结果。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- doc/08_ACCEPTANCE_CRITERIA.md
- doc/13_ACCEPTANCE_TRACEABILITY.md
- doc/verification-plan/**
- doc/fixtures/**
- doc/tasks/TASK-003.md
- doc/handoffs/TASK-003-*.md
- verification/TASK-003/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 每个原始 AC 有主责任 Task；所有未编号组和扩展需求有处理路径。
- 人工检查测试向量能失败于真实需求违例，而非只镜像实现。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-002](TASK-002.md)。依赖必须已经集成 done 才可开始。

允许在 Codex分配下修改共享 AC 文档；本文任务范围是补齐规格与素材规范，不执行真实模型实验。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
