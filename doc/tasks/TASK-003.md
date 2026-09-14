---
id: TASK-003
title: 补齐验收规格与测试素材规范
kind: verification-design
status: in_review
approval: approved
suggested_owner: DeepSeek Harness
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-002]
base_commit: 9472df5c44a1bad24cda639201b0824a9ea5eecc
branch: agent/deepseek/TASK-003-verification-spec
worktree: G:/CODEX/New Manga.worktrees/TASK-003-deepseek
integration_commit: null
---

# TASK-003：补齐验收规格与测试素材规范

本 Task 已由用户授权并分派给 DeepSeek Harness；当前为 `ready`，Owner 在指定 linked worktree 核验基线后改为 `in_progress`。本 Task 不开发应用功能，不释放任何后续 Task。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D08 全文，尤其 §4/6/67～72；D07 §98～101；G14/G17；TASK-002 独立复审 finding F-08。D 编号对应 [文档索引](../00_INDEX.md)；TASK-002 已集成的最小契约是本 Task 的固定输入。

用户批准的最小方案：以 `doc/verification-plan/TASK-003_ACCEPTANCE_AND_FIXTURE_SPEC.md` 为验收方法、环境、证据与阈值状态的单一权威文件，以 `doc/fixtures/MANIFEST.md` 为素材元数据/许可/生成方案清单；D08 保持产品验收目标与优先级权威，D13 只做追踪回链。不得复制第二套产品定义。

主责任编号 AC：本任务为设计/实验/基础工作，验收以下专属条件；关联产品 AC 不因本任务完成就自动 PASS。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 审阅现有185条及所有组级要求，补齐未编号要求的稳定标识、执行方式、环境与证据口径；不降低 P0/P1。
- [x] 为日漫/韩漫/Webtoon/损坏图/透明PNG/Unicode/重复图/大metadata提供素材清单、许可与生成方案；未取得素材标缺失。
- [x] 为模型质量制定可审查的评估方法和待批准阈值，为性能固定运行次数/环境/P95口径；未测量不填结果。
- [x] 关闭 F-08：仅在 D02 §5.3、D04 §30.1、D11 §10 的派生状态图补齐与冻结契约一致的 `Blocked → Cancelled`，不引入其他状态或转换。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- doc/08_ACCEPTANCE_CRITERIA.md
- doc/02_TECHNICAL_ARCHITECTURE_.md
- doc/04_USER_FLOW.md
- doc/11_ARCHITECTURE_MAPS.md
- doc/13_ACCEPTANCE_TRACEABILITY.md
- doc/verification-plan/**
- doc/fixtures/**
- doc/tasks/TASK-003.md
- doc/handoffs/TASK-003-*.md
- doc/reviews/TASK-003-*.md
- verification/TASK-003/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 每个原始 AC 有主责任 Task；所有未编号组和扩展需求有处理路径。
- 人工检查测试向量能失败于真实需求违例，而非只镜像实现。
- 现有 185 个 AC 的编号、标题和优先级保持不变；组级要求使用稳定 `ACG-*` 标识，结果枚举固定为 `PASS / FAIL / BLOCKED / NOT_RUN / N/A`。
- 性能方法明确环境、预热、运行次数与 P95；默认普通操作 3 次预热后测量 20 次，AI 步骤 1 次预热后测量 5 次。没有来源支持的模型阈值标记 `UNAPPROVED_THRESHOLD`，不得虚构数字或结果。
- 验证脚本至少检查 allowed_paths、185 个 AC 不变、稳定标识唯一、Fixture Manifest 必需字段、F-08 三处状态边、文档链接/代码围栏及 `git diff --check`。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-002](TASK-002.md)。依赖必须已经集成 done 才可开始。

允许在 Codex分配下修改共享 AC 文档；本文任务范围是补齐规格与素材规范，不执行真实模型实验。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：[TASK-003-6caefe1](../handoffs/TASK-003-6caefe1.md)，固定 `base_commit=9472df5`、`reviewed_head=6caefe1`（取代首次交付 `588383f`）。
- Review：首次 Review 由 Codex 完成（commit `f56bef4` 的 `doc/reviews/TASK-003-588383f.md`，decision=`changes_requested`，P1×7/P2×3；该报告位于 Reviewer 分支，不在本分支）；R-001～R-010 已逐项处置，等待固定 head 复审。Owner 不自审、不批准自己的交付。
- 实际执行：`pwsh -NoProfile -File ./verification/TASK-003/verify.ps1` 在 `6caefe1` 干净工作区退出码 0（12 条 PASS）；`git diff --check 9472df5 6caefe1 --` 退出码 0；F-08 三文件 3 新增 / 0 删除。产品、SQL、模型、性能与打包测试 `NOT_RUN / N/A`。
- 最近状态：2026-09-14 按首次 Review 修订（方法规范去除结果副本、`ACG-*` 扩至 24 个并补执行路由、性能协议补 estimator/计时边界/冷启动、Fixture 全部标 `missing` 并加许可与 SHA256 防线、护栏拒绝删除与去重假通过），内容提交 `6caefe1`，状态 `in_review`；其他 24 个 Task 保持 proposed。
