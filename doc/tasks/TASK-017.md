---
id: TASK-017
title: Translation 与上下文输出协议实验
kind: experiment
status: proposed
approval: pending_user_review
suggested_owner: DeepSeek Harness
owner: null
reviewer: null
depends_on: [TASK-003, TASK-004]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-017：Translation 与上下文输出协议实验

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D01 §5；D06 §10～18/54～57/84；D08 AC-TRANS/CONSTRAINT/TM/FALLBACK。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：本任务为设计/实验/基础工作，验收以下专属条件；关联产品 AC 不因本任务完成就自动 PASS。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 以已有设计中的OpenAI-compatible/本地Sakura候选检验文本与RegionID输出协议，记录具体可用Provider/模型版本。
- [ ] 对术语一致性、上下文排序、预算截断、缺失/重复/越界ID、畸形响应建立可复现样本和质量评估。
- [ ] 明确retry/fallback输入不变、网络策略和远程数据范围；结论包含成本/时延实测或未测说明，不声称所有Provider兼容。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- experiments/TASK-017/**
- doc/research/TASK-017.md
- doc/tasks/TASK-017.md
- doc/handoffs/TASK-017-*.md
- verification/TASK-017/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 实际命令与本地mock协议测试；真实端点未配置则只报告已测层。
- 日/韩文本、多页上下文和单目标写回校验；人工评分规则可复现。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-003](TASK-003.md)、[TASK-004](TASK-004.md)。依赖必须已经集成 done 才可开始。

实验不修改正式术语/TM或真实用户数据；不自行配置付费Provider。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
