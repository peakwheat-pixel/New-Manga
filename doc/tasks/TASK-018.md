---
id: TASK-018
title: Mask / Inpainting 路线独立实验
kind: experiment
status: done
approval: approved_by_user
suggested_owner: DeepSeek Harness
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-003, TASK-004]
base_commit: dce95acbb57a3494cb0f9d8d2d42e27d164176bb
branch: agent/deepseek/TASK-018-mask-inpainting-experiment
worktree: G:/CODEX/New Manga.worktrees/TASK-018-deepseek
integration_commit: 5a9f5c8
---

# TASK-018：Mask / Inpainting 路线独立实验

**当前状态以顶部 frontmatter 的 `status` 为准（现为 `in_review`）**，正文各段中的状态表述保留为其发生时的历史记录。

**READY（2026-09-17 用户批准释放）**：硬依赖 TASK-003、TASK-004 均已集成 `done`。Owner=DeepSeek Harness，Reviewer=Codex；本任务仅在下列允许路径内开展独立实验。模型或硬件不可用时，按验收要求将相应结果标记为 BLOCKED/NOT_RUN，不以 Mock 代替真实模型、视觉或性能证据。Owner 开始实施前，在本任务分支将状态改为 `in_progress`。
当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D01 §5；D02 §6.1；D06 §19～22/53/69；D07 §107。D 编号对应 [文档索引](../00_INDEX.md)。TASK-003 与 TASK-004 已集成完成；实验产物尚待本任务执行。

主责任编号 AC：本任务为设计/实验/基础工作，验收以下专属条件；关联产品 AC 不因本任务完成就自动 PASS。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 比较文档已有Simple Fill、Manga LaMa、AOT、BrushNet/PowerPaint、FLUX候选的实际可用范围；未能测试项明确保留未知。（`simple-fill`、`edge-bleed` 实测；四条学习型路线因缺依赖与权重全部 `BLOCKED`，未以 Mock 或基线数字代替）
- [x] 固定白底/线稿/网点/渐变/结构穿越样例，对Mask精修和修复分别记录残字、背景/边框损伤、耗时及峰值资源。（样例与 manifest、raw/final Mask 记录、残字代理、耗时与峰值 RSS 均已入库；**Mask 外**保护违规 10/10=0；Mask **内部**结构损伤量化仍 `NOT_RUN`——见下方未完成项，不得视为质量通过）
- [x] 提出有实测依据的Router条件、fallback与资源要求，保留参数调节和原始/最终Mask；不把大型模型设成未经验证默认。（`default_eligible` 仅两个基线为 `true`；建议为候选条件，生产 Router 属 TASK-019，本 Task 未扩展）
- [x] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。（首轮 Review [`doc/reviews/TASK-018-6c33e7f.md`](../reviews/TASK-018-6c33e7f.md) `approved`（被审 head `6c33e7f`）→ integration=`4d189ce`；修订切片复审 [`doc/reviews/TASK-018-5063315.md`](../reviews/TASK-018-5063315.md) `approved`（被审 head `5063315`）→ integration=`14b92e4`）

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

- Handoff：[TASK-018-6c33e7f](../handoffs/TASK-018-6c33e7f.md)（首轮交付）、[TASK-018-d7c10d4](../handoffs/TASK-018-d7c10d4.md)（修订切片）。
- Review：[doc/reviews/TASK-018-6c33e7f.md](../reviews/TASK-018-6c33e7f.md)（pproved，R-001～R-007）；修订切片复审为 changes_requested（仅文档口径，代码无需改动）。
- 实际执行/实验/测试：见 [研究记录](../research/TASK-018.md)、[实验日志](../../verification/TASK-018/experiment-log.md)、[修订取证](../../verification/TASK-018/revision-d7c10d4.md)、[集成验证](../../verification/TASK-018/integration-4d189ce.md)。
- 最近状态：2026-09-17 用户批准释放；`ready`，Owner=DeepSeek Harness，Reviewer=Codex，base=`dce95ac`，branch=`agent/deepseek/TASK-018-mask-inpainting-experiment`，worktree=`G:/CODEX/New Manga.worktrees/TASK-018-deepseek`。TASK-003/004 均为 `done`；实验尚未开始，全部计划测试仍为 NOT_RUN。

### 首轮交付与实测（2026-09-17）

- 实现/实验提交：`6c33e7f`（24 文件；`git diff --check` 退出码 0；白名单越界 0）。
- **产物**：`experiments/TASK-018/`（`mask_protocol.py` 纯 Python 协议、`generate_samples.py` 五类固定样例、`run_experiment.py` 五路线 × 五样例实验、`test_mask_protocol.py` 12 例自检、`samples/manifest.json` 含 SHA-256、`results/experiment.json` 含全部参数与实测）。
- **五条路线可用范围**：`simple-fill` 与 `edge-bleed`（**非模型基线**）**实测可运行**；`manga-lama`、`aot`、`brushnet-powerpaint`、`flux` 因缺 `torch`/`diffusers` 与权重**全部 BLOCKED**。**未验证的大型模型一律 `default_eligible = false`**。
- **实测结论**：`--repeat 3`，10 条 MEASURED 记录；**非目标像素保护违规 10/10 全为 0**；峰值 RSS 45.45–57.70 MB（CPU 路径，显存未分配）；残字为像素统计代理，`simple-fill` 全 0（构造性结果，**不代表质量达标**，且会在线稿/网点/渐变/结构穿越样例上抹平结构）。
- **未验证项**：四条学习型路线的质量/耗时/显存（BLOCKED）、Mask 内部结构损伤量化（NOT_RUN，当前模型无图像输入能力，不给目视结论）、真实 OOM（无法触发）、真实漫画样例（NOT_RUN）。**未以 Mock 冒充**模型、视觉或性能结果。
- 边界：仅修改本 Task 白名单；未改生产 src/tests、Schema、依赖、AGENTS、其他 Task；**未扩展到 TASK-019**；未 push/合并。
- Review：待 Codex 对固定 delivery head `6c33e7f` 独立 Review；本 Task 不自行标记 approved/done。

## 集成收口与来源（2026-09-17）

**2026-09-17 `done`**。Codex 按协作协议 §6.6 保留来源分支变更并创建 `integration_commit=4d189ce`（merge，parents `461e639` + `ef6d1c3`）；独立 Review [doc/reviews/TASK-018-6c33e7f.md](../reviews/TASK-018-6c33e7f.md) 对固定 `reviewed_head=6c33e7f` 的结论为 `approved`。

- 集成后复验见 [verification/TASK-018/integration-4d189ce.md](../../verification/TASK-018/integration-4d189ce.md)：协议自检 **12 passed / 0 skipped**；`run_experiment.py --repeat 3` 在 `%TEMP%` 副本中复跑得 `{"MEASURED": 10, "BLOCKED": 20}`，保护违规 10/10 全 0，确定性字段与交付 JSON 完全一致（仓库内 `results/experiment.json` 保持交付字节）；集成后全仓套件 **530 passed / 6 skipped**（6 项均因 `openssl unavailable`），7 次运行中 1 次出现与本 Task 无关的低频 flaky，已如实登记。
- Review findings：R-001/R-004/R-005/R-006（报告部分）已按文档口径修正收口；**R-002（静态门控）、R-003（`--output-dir` 越界崩溃）、R-006（`experiment.json` requirements 体积标签）、R-007（非 `simple-fill` 路线回落到 `edge_bleed_fill` 的潜在伪造风险）为 `deferred`**，限制登记在 [实验日志](../../verification/TASK-018/experiment-log.md) §7 与 [研究报告](../research/TASK-018.md) §9。
- **解锁条件**：本 Task 后续任何重跑（尤其在未来具备 `torch`/权重或网络的环境验证学习型路线）**必须先修 R-007**（未实现路线 fail-closed），再按 R-002 补真实探测并重新取证；`routes[*].runnable_here`/`blocked_reason` 不得作为环境证据引用。
- 未完成项保持原样、不得视为通过：四条学习型路线的修复质量/残字/背景损伤/耗时/显存 **`BLOCKED`**；Mask **内部**结构损伤量化、真实 OOM、真实漫画样例 **`NOT_RUN`**；模型 Hash `NOT_AVAILABLE`。
- 生产 Router 属 **TASK-019**：本 Task 只提出候选条件，**未扩展到 TASK-019**，也未释放 TASK-019 或其他冻结 Task。

- **当前状态（唯一）**：2026-09-17 `done`。已按协作协议 §6.6 完成三轮独立 Review 与集成（首轮 + 修订切片 + 尾项切片），本 Task 无未决 Review。
  - **尾项切片（R-104）**：base `6f130ad`、被审 head `965bcd2`（元数据 `c8c2a8e`），Review [`doc/reviews/TASK-018-965bcd2.md`](../reviews/TASK-018-965bcd2.md) `approved`，integration=`5a9f5c8`。内容：`run_experiment.py` 新增 `assert_implementations_registered()` 并在**模块导入期**调用（`implementation` 非 None ⇒ 该 route 必须在 `FILLERS` 注册，否则 `RuntimeError` 拒绝启动）；反例经 Reviewer 以 CLI 路径独立复现（退出码 1、**未写任何 PNG**，作者的 import 路径反例亦成立）；`test_route_gating.py` **13 → 16 passed**（通过数未减少）。
  - **尾项集成后复验**（见 [verification/TASK-018/integration-5a9f5c8.md](../../verification/TASK-018/integration-5a9f5c8.md)）：协议测试 **12 passed / 0 skipped**、门控测试 **16 passed / 0 skipped**、实验 **10 MEASURED + 20 BLOCKED**、保护框 20/20=0、确定性字段与提交 JSON 0 差异、全仓套件 **530 passed / 6 skipped**（6 项均 `openssl unavailable`）。
  - **首轮**：base `dce95ac`（起点 `9ee17189`）、被审 head `6c33e7f`（元数据 `ef6d1c3`），Review [`doc/reviews/TASK-018-6c33e7f.md`](../reviews/TASK-018-6c33e7f.md) `approved`（R-001～R-007），integration=`4d189ce`。
  - **修订切片**：base `8c63f9b`、被审 head `d7c10d4`（元数据 `3b38d39`）→ 复审 `changes_requested`（R-101/R-102 证据表述、R-103/R-104 文档与防护；工程实现已复核 PASS、代码无需改动）→ 收口 head `5063315`（元数据 `b10f1ba`），Review [`doc/reviews/TASK-018-5063315.md`](../reviews/TASK-018-5063315.md) `approved`，integration=`14b92e4`。
  - 修复内容：R-007 fail-closed（显式 `FILLERS` 映射，依赖齐备也不授权未实现路线）、R-002 真实探测（`importlib.util.find_spec` + 本地权重文件）、R-003 越界输出目录、R-006 去未核实体积标注并重生成 `experiment.json`、R-001 剩余项保护框逐框断言、R-101 依赖声明更正、R-102 数字归属与区间同步、R-103 状态块合并。
  - 集成后复验（见 [verification/TASK-018/integration-14b92e4.md](../../verification/TASK-018/integration-14b92e4.md)）：`test_mask_protocol.py` **12 passed / 0 skipped**；`test_route_gating.py` **13 passed / 0 skipped**；`run_experiment.py --repeat 3` → **10 MEASURED + 20 BLOCKED**、保护违规 0、**保护框 20/20 全 0**、`blocked_stage` 20/20 `not_implemented`、确定性字段与提交 JSON 0 差异；全仓套件 **530 passed / 6 skipped**（6 项均 `openssl unavailable`）。
  - 未关闭项：**无待处理 Review finding**（R-201 已在集成收口关闭，R-104 已 `fixed`）。仍不具备证据的维度照旧保留、**不得视为通过**：四条学习型路线的质量/耗时/内存/显存 **`BLOCKED`**；Mask 内部结构损伤量化、真实 OOM、真实漫画样例 **`NOT_RUN`**；模型 Hash `NOT_AVAILABLE`。生产 Router 属 **TASK-019**（未释放）。
  - 边界：未改生产 `src/`、`tests/`、Schema、依赖清单、`AGENTS.md`；未扩展到 TASK-019；未释放 TASK-019 或其他冻结 Task；未 push。
