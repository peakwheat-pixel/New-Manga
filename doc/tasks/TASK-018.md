---
id: TASK-018
title: Mask / Inpainting 路线独立实验
kind: experiment
status: in_review
approval: approved_by_user
suggested_owner: DeepSeek Harness
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-003, TASK-004]
base_commit: dce95acbb57a3494cb0f9d8d2d42e27d164176bb
branch: agent/deepseek/TASK-018-mask-inpainting-experiment
worktree: G:/CODEX/New Manga.worktrees/TASK-018-deepseek
integration_commit: null
---

# TASK-018：Mask / Inpainting 路线独立实验

**READY（2026-09-17 用户批准释放）**：硬依赖 TASK-003、TASK-004 均已集成 `done`。Owner=DeepSeek Harness，Reviewer=Codex；本任务仅在下列允许路径内开展独立实验。模型或硬件不可用时，按验收要求将相应结果标记为 BLOCKED/NOT_RUN，不以 Mock 代替真实模型、视觉或性能证据。Owner 开始实施前，在本任务分支将状态改为 `in_progress`。
当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D01 §5；D02 §6.1；D06 §19～22/53/69；D07 §107。D 编号对应 [文档索引](../00_INDEX.md)。TASK-003 与 TASK-004 已集成完成；实验产物尚待本任务执行。

主责任编号 AC：本任务为设计/实验/基础工作，验收以下专属条件；关联产品 AC 不因本任务完成就自动 PASS。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 比较文档已有Simple Fill、Manga LaMa、AOT、BrushNet/PowerPaint、FLUX候选的实际可用范围；未能测试项明确保留未知。
- [ ] 固定白底/线稿/网点/渐变/结构穿越样例，对Mask精修和修复分别记录残字、背景/边框损伤、耗时及峰值资源。
- [ ] 提出有实测依据的Router条件、fallback与资源要求，保留参数调节和原始/最终Mask；不把大型模型设成未经验证默认。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- experiments/TASK-018/**
- doc/research/TASK-018.md
- doc/tasks/TASK-018.md
- doc/handoffs/TASK-018-*.md
- verification/TASK-018/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 实际实验入口、样例/模型Hash、硬件/参数/重复次数；输出图与失败样例归档。
- 非目标像素/Region保护、OOM/缺模型行为；无硬件路线标BLOCKED。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-003](TASK-003.md)、[TASK-004](TASK-004.md)。依赖必须已经集成 done 才可开始。

模型效果是待验证事实；生产Router在TASK-019才实现。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-17 用户批准释放；`ready`，Owner=DeepSeek Harness，Reviewer=Codex，base=`dce95ac`，branch=`agent/deepseek/TASK-018-mask-inpainting-experiment`，worktree=`G:/CODEX/New Manga.worktrees/TASK-018-deepseek`。TASK-003/004 均为 `done`；实验尚未开始，全部计划测试仍为 NOT_RUN。

## 交付与运行记录（补充，2026-09-17）

- 实现/实验提交：`6c33e7f`（24 文件；`git diff --check` 退出码 0；白名单越界 0）。
- **产物**：`experiments/TASK-018/`（`mask_protocol.py` 纯 Python 协议、`generate_samples.py` 五类固定样例、`run_experiment.py` 五路线 × 五样例实验、`test_mask_protocol.py` 12 例自检、`samples/manifest.json` 含 SHA-256、`results/experiment.json` 含全部参数与实测）。
- **五条路线可用范围**：`simple-fill` 与 `edge-bleed`（**非模型基线**）**实测可运行**；`manga-lama`、`aot`、`brushnet-powerpaint`、`flux` 因缺 `torch`/`diffusers` 与权重**全部 BLOCKED**。**未验证的大型模型一律 `default_eligible = false`**。
- **实测结论**：`--repeat 3`，10 条 MEASURED 记录；**非目标像素保护违规 10/10 全为 0**；峰值 RSS 45.45–57.70 MB（CPU 路径，显存未分配）；残字为像素统计代理，`simple-fill` 全 0（构造性结果，**不代表质量达标**，且会在线稿/网点/渐变/结构穿越样例上抹平结构）。
- **未验证项**：四条学习型路线的质量/耗时/显存（BLOCKED）、Mask 内部结构损伤量化（NOT_RUN，当前模型无图像输入能力，不给目视结论）、真实 OOM（无法触发）、真实漫画样例（NOT_RUN）。**未以 Mock 冒充**模型、视觉或性能结果。
- 边界：仅修改本 Task 白名单；未改生产 src/tests、Schema、依赖、AGENTS、其他 Task；**未扩展到 TASK-019**；未 push/合并。
- Review：待 Codex 对固定 delivery head `6c33e7f` 独立 Review；本 Task 不自行标记 approved/done。
