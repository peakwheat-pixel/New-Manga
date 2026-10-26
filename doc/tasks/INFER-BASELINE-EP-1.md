---
id: INFER-BASELINE-EP-1
title: 推理基线选型——ORT-DML vs ORT-CUDA vs torch（检测/OCR/修复三类模型实测）
kind: research
governance_version: 3
status: ready
approval: user_authorized_2026-10-26
suggested_owner: antigravity
owner: null
reviewer: null
depends_on: []
base_commit: c5aade851
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/INFER-BASELINE-EP-1
allowed_paths:
  - doc/tasks/INFER-BASELINE-EP-1.md
  - verification/INFER-BASELINE-EP-1/**
  - G:/CODEX/New Manga.workspace/task-envs/INFER-BASELINE-EP-1/**
---

# INFER-BASELINE-EP-1：推理基线选型（ORT-DML / ORT-CUDA / torch）

## 来源与目标

**来源**：用户 2026-10-26 裁决链路——目标架构改为 [AD-002](../AD-002_TARGET_DESKTOP_ARCHITECTURE.md)（C#/.NET + Avalonia + 既有 Python Core，GPL-3.0）；用户明确问「Saber 那种（torch+CUDA）好，还是 ONNX 好」，Lead 建议「ONNX 优先、torch 仅作可选高性能包」，用户同意先做 3 人日的实测基线再定清单。

**现状事实**：
- 本项目 SFX 检测已走 ONNX Runtime **DirectML**：CPU 10.37 s/页 vs DML 1.21 s/页（8.6×，`verification/M2-SFX-GPU-EP-1/`）。
- 检测链另有 torch（python-doctr 1.1.0 / RT-DETR-v2 via transformers 5.17.0，CPU wheels）路径。
- Saber 走 torch **2.12+cu130** 全家桶：整包 27.2 GB（models 3.76 GB + torch 2.66 GB）。
- AD-002 §3.5 已冻结预算规则：Core CPU 分发 ≤2 GB、CUDA 可选包 ≤8 GB、新模型优先 ONNX。
- 本机 GPU：**NVIDIA GeForce RTX 5070 Ti**（驱动 32.0.16.1692）→ ORT-CUDA/TensorRT 与 torch-CUDA 都可实测。

**目标**：用同一批真实漫画页，对「检测 / OCR / 修复」三类各选 ≥1 个候选模型，测出 `ORT-DML`、`ORT-CUDA`（或 TensorRT）、`torch-CUDA` 三档的**速度/精度/体积/启动成本**，产出可执行的模型清单与默认 EP 决策。**只做选型研究，不改产品代码。**

## Acceptance Criteria

- [ ] **AC1 三类模型基线**：每类 ≥1 个候选（检测：现网 RT-DETR-v2 或 YOLO；OCR：现网 PaddleOCR 系 + 尝试 MangaOCR；修复：LaMa/litelama 或现网 inpaint 模型），在同一组真实页（建议 10 页，覆盖日漫/条漫）上测：
  速度（warm-up 1 次不计 + 计测 ≥3 次取中位，ms/页）、精度（与原框架输出一致性：检测 IoU/召回、OCR 字符准确率、修复 PSNR/SSIM）、模型体积（MB）、依赖体积（MB）、冷启动/import 耗时（ms）。
- [ ] **AC2 ONNX 导出可行性**：对每个候选尝试 ONNX 导出（固定 + 动态 shape 两种），记录 opset、是否成功、失败原因、导出后精度差异；MangaOCR 这类 encoder-decoder 必须给明确结论。
- [ ] **AC3 决策矩阵**：产出「模型 × EP」矩阵与最终建议：主包默认 EP、哪些模型进主包（≤2GB）、哪些进可选高性能包（≤8GB）、哪些必须 torch（若无则明确写"无"）。
- [ ] **AC4 可复跑**：venv/脚本/原始输出全部落 workspace + `verification/INFER-BASELINE-EP-1/`；命令可重跑；未跑项标 NOT_RUN/BLOCKED。
- [ ] **AC5 许可核查**：逐模型记录权重许可（Ultralytics = AGPL-3.0；PaddleOCR/RapidOCR ≈ Apache-2.0；MangaOCR/LaMa 逐项核实），与 GPL-3.0 产品分发的兼容结论。

## 允许修改范围

- 本 Task 卡、`verification/INFER-BASELINE-EP-1/**`、`G:/CODEX/New Manga.workspace/task-envs/INFER-BASELINE-EP-1/**`。
- 只读引用：`src/**`（现网 provider/inpaint/ocr 实现）、`requirements.txt`、`verification/M2-SFX-GPU-EP-1/**`、`verification/M2-SFX-T5-TILE-KO/**`、`test_assets/**`。

## 禁止范围

- 不得修改产品源码、配置、依赖清单（`requirements*.txt`）、契约、AD 文档。
- 不得下载商业字体；不得把模型权重提交进仓库（大文件放 workspace，索引只写 SHA-256 与来源 URL）。
- 不得在证据里写"显著提升"等无统计支撑的措辞；只报实测值与中位数。
- 不得触碰用户真实 `%APPDATA%`/媒体库。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 三类模型 × 3 EP 的基准脚本（warm-up + ≥3 计测） | 独立 venv（workspace）、RTX 5070 Ti、10 页真实图 | NOT_RUN | 待填 |
| AC2 | `torch.onnx.export` / `ultralytics export` / Paddle2ONNX / 自定义导出 | 同上 | NOT_RUN | 待填 |
| AC3 | 汇总矩阵 + 预算核算 | AC1/AC2 完成 | NOT_RUN | 待填 |
| AC5 | 许可逐项核对（license 文件/模型卡） | 一手来源 | NOT_RUN | 待填 |

## 依赖、风险与阻塞

- 无需前序 Task；可在 S0 spike 并行（二者无共享写路径）。
- 风险 1：CUDA/cuDNN 版本与 ORT/torch 匹配（需固定组合并记录）；本机驱动版本已记录。
- 风险 2：DirectML 与 CUDA EP 不能在同一 venv 共存（`onnxruntime` / `onnxruntime-directml` / `onnxruntime-gpu` 三选一）→ 必须建**三个独立 venv**。
- 风险 3：benchmark 变异（GPU 时钟/热降频）→ 固定顺序、warm-up、≥3 次中位，记录环境。
- 风险 4：MangaOCR / LaMa 导出失败 → 这正是要回答的问题，失败也要有证据（错误日志 + 替代路径）。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（Owner 与 Reviewer 必须不同；建议 ZCode 或 Codex 独审）。
- 实际测试：尚无。
- 释放条件：`status` 改 `ready` 并入 REBASELINE_PLAN DAG（由 DSH 在用户确认排期后执行）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/INFER-BASELINE-EP-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/INFER-BASELINE-EP-1 | 待填（venv ×3 + 模型权重清单） | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时补 DAG/STATUS 指针。

