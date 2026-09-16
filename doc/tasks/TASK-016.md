---
id: TASK-016
title: OCR 与检测路线独立实验
kind: experiment
status: in_review
approval: approved
suggested_owner: DeepSeek Harness
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-003, TASK-004]
base_commit: f9edd68845d4a1ee5d42d9fdcf1a304dc3fa2f86
branch: agent/deepseek/TASK-016-ocr-detection-experiment
worktree: G:/CODEX/New Manga.worktrees/TASK-016-deepseek
integration_commit: null
---

# TASK-016：OCR 与检测路线独立实验

本 Task 已获用户授权并由 DeepSeek Harness 认领，当前处于 `in_progress`。固定基线为
`f9edd68845d4a1ee5d42d9fdcf1a304dc3fa2f86`，工作分支与路径见顶部元数据；共用流程见
[协作协议](../09_COLLABORATION.md)。本实验不修改生产实现，不把实验结论直接升级为产品需求。

## 来源与目标

D01 §5；D02 §6；D06 §6～7/67～68；D08 AC-OCR/WEBTOON。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：本任务为设计/实验/基础工作，验收以下专属条件；关联产品 AC 不因本任务完成就自动 PASS。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 针对已有文档列出的日漫OCR、PaddleOCR Korean和OpenAI-compatible Vision路线建立明确候选/版本/许可表；检测器作为OCR前置共同验证。
- [ ] 在授权/自制横竖排、韩文、艺术字和Tile样本上记录识别错误、坐标/顺序、耗时/RAM/VRAM、缺依赖行为。
- [ ] 对低质量/失败fallback只使用已配置路线；输出可复现建议和失败样例，不复制旧仓库未提供代码。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- experiments/TASK-016/**
- doc/research/TASK-016.md
- doc/tasks/TASK-016.md
- doc/handoffs/TASK-016-*.md
- verification/TASK-016/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 记录实际实验命令、数据/模型Hash、环境、输出和指标；不具备GPU/API条件的项目标BLOCKED/NOT_RUN。
- 单Region输出映射与长图Tile全局坐标验证；说明模型质量测试不等于产品集成验证。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-003](TASK-003.md)、[TASK-004](TASK-004.md)。依赖必须已经集成 done 才可开始。

不写生产适配器；联网模型或API测试需已配置授权及资源。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
- 最近状态：2026-09-16 用户授权释放；DeepSeek Harness 认领，`in_progress`。base=`f9edd68`、分支/工作区见顶部元数据。
- 最近状态：2026-09-16 实验交付并置 `in_review`。产物：`experiments/TASK-016/`（协议自检 4 passed/0 skipped；harness 在 probe-only 与 `--run-models` 下各输出 15 条 BLOCKED）、`doc/research/TASK-016.md`（候选/版本/许可调研）、`verification/TASK-016/experiment-log.md`（环境、命令、退出码、skip 原因、BLOCKED/NOT_RUN 清单）。**模型质量/性能全部 BLOCKED**：依赖全缺且 `huggingface.co` 不可达，未以 Mock 冒充。无 GPU/API 阻塞之外的残留；未修改生产 src/tests/Schema/依赖/AGENTS，未 push/合并。待 Codex 独立 Review；本 Task 不自行标记 approved/done。
