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

## 执行计划与测试要求

- 先生成自制横排/竖排/韩文/艺术字/长图 Tile 样本并固定 manifest SHA-256，再运行无下载 Provider 探测。
- 单 Region 输出必须保留 `region_id`；Tile-local polygon 必须转换为 page-global；检测作为 OCR 前置路线单独记录。
- 只有显式 `--run-models` 且已有依赖、权重或授权 endpoint 时才允许真实调用；缺任一前提标 `BLOCKED/NOT_RUN`。
- 记录实际实验命令、数据/模型 Hash、环境、输出和指标；模型质量测试不等于产品集成验证。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

### Owner 执行记录（2026-09-16）

- 样本生成：`experiments/TASK-016/generate_samples.py`，退出码 0；生成 5 个自制 PNG 与 manifest，Hash 和参考 Region/Tile 标注见 [研究记录](../research/TASK-016.md)。
- 协议自检：`python -m unittest discover -s experiments/TASK-016 -p 'test_*.py' -v` → **4 passed, 0 skipped**，退出码 0；覆盖单 Region、Tile 全局坐标、阅读顺序和 fallback 门控。
- Provider 探测：`run_experiment.py` 默认 no-download 模式 → **0 passed, 0 skipped, 15 BLOCKED**，退出码 0；`manga_ocr` 缺失 5 条、PaddleOCR/Paddle 缺失 5 条、Vision endpoint/model 配置缺失 5 条。
- 环境：Windows 11 `10.0.26200`、AMD64、Python 3.12.3、PySide6 6.11.2、RTX 5070 Ti 16303 MiB；未设置 `QT_QPA_PLATFORM`；没有下载模型或发出 API 请求。
- 证据：[author-verification](../../verification/TASK-016/author-verification.md)、[samples](../../experiments/TASK-016/samples/manifest.json)、[probe](../../experiments/TASK-016/results/probe.json)。

### 当前阻塞

真实 OCR/检测质量、错误率、坐标/顺序误差、耗时、RAM/VRAM 仍为 `BLOCKED/NOT_RUN`：当前隔离环境缺 Provider 依赖/模型权重，且无合法 Vision endpoint；不能用协议自检或 Mock 输出替代。取得隔离依赖、实际模型 Hash 或授权 endpoint 后，应复用同一 manifest 重跑并追加新证据。

## 依赖、风险与阻塞

硬依赖：[TASK-003](TASK-003.md)、[TASK-004](TASK-004.md)。依赖必须已经集成 done 才可开始。

不写生产适配器；联网模型或API测试需已配置授权及资源。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：待实现提交后创建 `doc/handoffs/TASK-016-<short-head>.md`。
- Review：待 Codex 对固定 delivery head 独立 Review。
- 实际执行/实验/测试：见 [研究记录](../research/TASK-016.md) 与 [验证记录](../../verification/TASK-016/author-verification.md)。
- 最近状态：2026-09-16 用户授权，DeepSeek Harness 已认领；当前 `in_progress`，模型质量实验因缺 Provider 前提保持 `BLOCKED/NOT_RUN`。
- 最近状态：2026-09-16 用户授权释放；DeepSeek Harness 认领，`in_progress`。base=`f9edd68`、分支/工作区见顶部元数据。
- 最近状态：2026-09-16 实验交付并置 `in_review`。产物：`experiments/TASK-016/`（协议自检 4 passed/0 skipped；harness 在 probe-only 与 `--run-models` 下各输出 15 条 BLOCKED）、`doc/research/TASK-016.md`（候选/版本/许可调研）、`verification/TASK-016/experiment-log.md`（环境、命令、退出码、skip 原因、BLOCKED/NOT_RUN 清单）。**模型质量/性能全部 BLOCKED**：依赖全缺且 `huggingface.co` 不可达，未以 Mock 冒充。无 GPU/API 阻塞之外的残留；未修改生产 src/tests/Schema/依赖/AGENTS，未 push/合并。待 Codex 独立 Review；本 Task 不自行标记 approved/done。

- 最近状态：2026-09-16 按 Codex Review（R-001~R-004、S-001）完成修订，置 `in_review` 待复审。
  - **R-001**：新增检测器候选 `detector-dbnet`/`detector-ctd`/`detector-yolo`（`stage: "detection"`）与 `verification_matrix`（3 行，逐阶段声明覆盖与缺口）；**遗留范围裁决请求**：`detector-yolo` 在 `doc/01:255` 标注"本仓库无此文件"，无实现来源，需 Codex 裁决是否保留。
  - **R-002**：`fallback_status()` 收窄为"调用方必须点名且名称在配置集内"，新增 `validate_route_configuration()` 与 2 项非法配置测试。
  - **R-003**：候选元数据统一标为 unverified（`metadata_status: "UNVERIFIED"` + `UNVERIFIED —` 前缀），research 记录追加专门声明。
  - **R-004**：统一哨兵 `MODEL_SHA256_UNAVAILABLE = "NOT_AVAILABLE"`，不再读环境变量，样本哈希只存 `sample_sha256`。
  - **S-001**：本节记录已修正为实际交付。
  - 验证：`python -m unittest experiments/TASK-016/test_protocol.py -v` → **5 passed / 0 skipped**；`run_experiment.py` probe-only → **30 BLOCKED**（6 候选 × 5 样本）。模型质量/性能仍 **BLOCKED**（依赖缺失 + `huggingface.co` 不可达），未以 Mock 冒充。
  - 本轮工作区存在**另一位作者**的未提交改动（manga-ocr Region crop、research 重写、author-verification、model-run-blocked.json），按"未提交内容归原作者"予以保留并一并提交。
  - 未修改生产 src/tests/Schema/依赖/AGENTS/其他 Task/冻结 Task；未 push、未合并分支。
