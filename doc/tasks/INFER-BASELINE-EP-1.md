---
id: INFER-BASELINE-EP-1
title: 推理基线选型——ORT-DML vs ORT-CUDA vs torch（检测/OCR/修复三类模型实测）
kind: research
governance_version: 3
status: done
approval: user_authorized_2026-10-26
suggested_owner: antigravity
owner: null
reviewer: null
depends_on: []
base_commit: c5aade851
branch: null
worktree: null
integration_commit: 1b91d93a9
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1 三类模型基线**：每类 ≥1 个候选（检测：现网 RT-DETR-v2 或 YOLO；OCR：现网 PaddleOCR 系 + 尝试 MangaOCR；修复：LaMa/litelama 或现网 inpaint 模型），在同一组真实页（建议 10 页，覆盖日漫/条漫）上测： <<MET>>
  速度（warm-up 1 次不计 + 计测 ≥3 次取中位，ms/页）、精度（与原框架输出一致性：检测 IoU/召回、OCR 字符准确率、修复 PSNR/SSIM）、模型体积（MB）、依赖体积（MB）、冷启动/import 耗时（ms）。
- [x] **AC2 ONNX 导出可行性**：对每个候选尝试 ONNX 导出（固定 + 动态 shape 两种），记录 opset、是否成功、失败原因、导出后精度差异；MangaOCR 这类 encoder-decoder 必须给明确结论。 <<MET>>
- [x] **AC3 决策矩阵**：产出「模型 × EP」矩阵与最终建议：主包默认 EP、哪些模型进主包（≤2GB）、哪些进可选高性能包（≤8GB）、哪些必须 torch（若无则明确写"无"）。 <<MET>>
- [x] **AC4 可复跑**：venv/脚本/原始输出全部落 workspace + `verification/INFER-BASELINE-EP-1/`；命令可重跑；未跑项标 NOT_RUN/BLOCKED。 <<MET>>
- [x] **AC5 许可核查**：逐模型记录权重许可（Ultralytics = AGPL-3.0；PaddleOCR/RapidOCR ≈ Apache-2.0；MangaOCR/LaMa 逐项核实），与 GPL-3.0 产品分发的兼容结论。 <<MET>>
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
| AC1 | `scripts/run-matrix.ps1`（yolo/ppocr/mangaocr/lama × cpu/dml/cuda）+ `run-torch.ps1`（RT-DETR-v2、manga-ocr × cpu/cuda）+ `parity2.py` | 4 个独立 venv、RTX 5070 Ti(sm_120)、10 页真实漫画页、warm-up 1 + 4 次计测 | **DONE**：19 次 bench 全绿（2 处按设计不可用：lama_fp32 在 DML 运行失败、onnxruntime-gpu 1.31 需 CUDA13）；速度/启动/体积/跨 EP 一致性齐全 | `verification/INFER-BASELINE-EP-1/bench-matrix.json`、`parity.json`、`sizes-and-startup.json`、`dml-lama-probe.json` |
| AC2 | `torch.onnx.export`（fixed + dynamic）经 `export_onnx.py`；已发布 ONNX 仅记录 opset/形状事实 | torch 2.11.0+cu128 / transformers 5.21.0 | **DONE**：RT-DETR-v2 fixed+dynamic 导出成功(opset17,163.7MB)但**动态图 ORT 不可加载**→发 fixed；manga-ocr encoder/decoder 导出成功、`generate()` 整图失败(aten::full)；YOLO/PP-OCR/LaMa 为上游导出的 ONNX（无源权重，重导 NOT_RUN） | `verification/INFER-BASELINE-EP-1/export-rtdetr.json`、`export-mangaocr.json`、`export-shipped.json` |
| AC3 | 汇总矩阵 + 预算核算（主包 ≤2GB / 可选包 ≤8GB） | AC1/AC2 完成 | **DONE**：主包实测合计 1216.4 MB（≤2GB）；可选 CUDA 包 仅 ORT 2296.0 MB / 含 torch 7005.8 MB（≤8GB）；必须 torch 的模型 = 无 | `verification/INFER-BASELINE-EP-1/decision-matrix.json`、`REPORT.md` §4 |
| AC5 | 许可逐项核对（HF model card metadata + ONNX metadata + PyPI 元数据） | 一手来源 | **DONE**：仅 `yolo11s-seg` 为 AGPL-3.0（ONNX metadata 自证），其余权重 Apache-2.0；CUDA/cuDNN 为 NVIDIA 专有 | `verification/INFER-BASELINE-EP-1/licenses.md` |

## 依赖、风险与阻塞

- 无需前序 Task；可在 S0 spike 并行（二者无共享写路径）。
- 风险 1：CUDA/cuDNN 版本与 ORT/torch 匹配（需固定组合并记录）；本机驱动版本已记录。
- 风险 2：DirectML 与 CUDA EP 不能在同一 venv 共存（`onnxruntime` / `onnxruntime-directml` / `onnxruntime-gpu` 三选一）→ 必须建**三个独立 venv**。
- 风险 3：benchmark 变异（GPU 时钟/热降频）→ 固定顺序、warm-up、≥3 次中位，记录环境。
- 风险 4：MangaOCR / LaMa 导出失败 → 这正是要回答的问题，失败也要有证据（错误日志 + 替代路径）。

## 交付与运行记录

- Handoff：`verification/INFER-BASELINE-EP-1/REPORT.md`（含复跑命令）+ `decision-matrix.json`；
  测量机 RTX 5070 Ti / sm_120 / 驱动 616.92 / Python 3.12.3；10 页真实漫画页；warm-up 1 + 4 次计测取中位。
- Review：尚无（Owner 与 Reviewer 必须不同；建议 ZCode 或 Codex 独审）。
- 实际测试：19 次 ORT/torch bench + 8 项跨 EP/跨运行时一致性 + 3 组导出尝试，全部证据已 64-hex pin
  （见 Canonical Evidence）。NOT_RUN/BLOCKED 8 项在 `REPORT.md` §6 逐条注明原因
  （无源权重、无 CUDA13 运行时、批处理未实现、GT 标注与样本不匹配等）。
- 关键结论：默认 EP = **DirectML**；主包 1216.4 MB（≤2GB）；可选 CUDA 包 2296.0/7005.8 MB（≤8GB）；
  **必须 torch 的模型：无**（RT-DETR-v2 fixed ONNX 三档可加载且 10/10 页框数与 torch 一致；
  manga-ocr ONNX 与 torch 逐字符 100% 一致）。
- 运行环境：`G:/CODEX/New Manga.workspace/task-envs/INFER-BASELINE-EP-1/`
  （venvs ×4 + models + results + logs + scripts，均已 PRESERVE_REFERENCED）。
- 释放条件：`status` 改 `ready` 并入 REBASELINE_PLAN DAG（已由 DSH 完成；`ready` 为当前状态）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EV-AC1-BENCH | AC1 | verification/INFER-BASELINE-EP-1/bench-matrix.json |  | 78e831e877973134b75742596ca91719634c9ce51864b4d008adaa8b9a8e29b7 | CANONICAL |
| EV-AC1-PARITY | AC1 | verification/INFER-BASELINE-EP-1/parity.json |  | 6f6aec1e97e384031433af58df05caf2ff83c4c202ab7c09f099b240f541a171 | CANONICAL |
| EV-AC1-SIZES | AC1 | verification/INFER-BASELINE-EP-1/sizes-and-startup.json |  | 9f952f287a51ca589ccd4715d36efbd3b489843a7f977444df62e7e7109073b2 | CANONICAL |
| EV-AC1-DMLPROBE | AC1 | verification/INFER-BASELINE-EP-1/dml-lama-probe.json |  | 02cb6777c7ae591510c1657f39eac5a8cbb7b129a13f8101b60e2176eb519a3d | CANONICAL |
| EV-AC2-RTDETR | AC2 | verification/INFER-BASELINE-EP-1/export-rtdetr.json |  | 8b9dcb84aacfb4fc5ec48574c2e129aa2c91ad717d2998a367ceb8b5760b8f52 | CANONICAL |
| EV-AC2-MANGAOCR | AC2 | verification/INFER-BASELINE-EP-1/export-mangaocr.json |  | 540e7d45c04fad71aca913882ff52aafe494feea13cf078ce2a2dcff40529d1e | CANONICAL |
| EV-AC2-SHIPPED | AC2 | verification/INFER-BASELINE-EP-1/export-shipped.json |  | 5b3d526b227eb2dba63cf41e4b93da2289c758864e29cf0497d6017586a43f1b | CANONICAL |
| EV-AC3-MATRIX | AC3 | verification/INFER-BASELINE-EP-1/decision-matrix.json |  | 9fa59fd6461e807301fd5639d15c16600aa407452185bfba40ec0c02cff0dc3d | CANONICAL |
| EV-AC3-REPORT | AC3/AC4 | verification/INFER-BASELINE-EP-1/REPORT.md |  | 2d683edf51ec23bf90c4e57ebaacd768f16f5b4f829b001235f600c5cf02ff90 | CANONICAL |
| EV-AC4-MANIFEST | AC4 | verification/INFER-BASELINE-EP-1/models-manifest.json |  | 0d61136a7cdf98166e65727c2a7921baee4d352fff29b8cdc37bafd2718c01eb | SOURCE_PIN |
| EV-AC5-LICENSES | AC5 | verification/INFER-BASELINE-EP-1/licenses.md |  | 7585ecbfb7d0c16de0a3e6e996a0bef1d61ad8bd351020c177545a49ef5042bc | CANONICAL |

说明：证据为工作树未提交状态，故用 64-hex SHA-256 pin，commit 列留 —。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/INFER-BASELINE-EP-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/INFER-BASELINE-EP-1 | verification/INFER-BASELINE-EP-1/models-manifest.json | 已核：全部路径在 workspace 下，仓库内无权重（只有 REPORT/JSON/MD 证据）；关闭时按 PRESERVE_REFERENCED 保留 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时补 DAG/STATUS 指针。
## Review（DSH 集成复核，2026-10-27）— PASS

- 证据：11 项 64-hex pin 全对；check.ps1 -TaskPath PASS；env 8.74GB 于 workspace 	ask-envs/INFER-BASELINE-EP-1（PRESERVE_REFERENCED）。
- 三档实测（10 页真实页，warm-up1+4 中位，ms/页）：YOLO11s-seg CPU 161.42/DML 26.48/CUDA 27.71；RT-DETR-v2 ONNX-CPU 168.95/DML 22.95/CUDA 25.28（torch-CPU 251.78/torch-CUDA 40.82）；PP-OCRv4 CPU 135.85/DML 250.92/CUDA 496.09（**GPU 反而慢**）；manga-ocr CPU 72.52/DML 97.87/CUDA 23.17；LaMa 512 CPU 1161.19/**DML 失败**/CUDA 76.92。
- 启动：ORT import 66–89ms、会话 78–4479ms；torch import 1292–1313ms + 模型 2823–3321ms（比 ORT 多 ~4.1–4.6s）。
- 导出：RT-DETR-v2 fixed/dynamic 均成功（opset17/163.7MB），但**动态图 ORT 不可加载** → 发 fixed；manga-ocr encoder/decoder 与 torch **逐字符 100% 一致**，generate() 整图失败 → 解码循环留 Python；YOLO/PP-OCR/LaMa 上游 ONNX（重导 NOT_RUN）。
- 决策采纳：**默认 EP=DirectML**；主包 ORT-DML 362.6MB + 模型 853.8MB = **1216.4MB ≤2GB**；可选 CUDA 包 2296MB（含 torch 7005.8MB ≤8GB）；**必须 torch 的模型：无**（torch 退为训练/导出期）。
- 工程规范新增（写入后续验收）：① onnxruntime-gpu ≥1.31 静默回退 CPU 必须硬断言拦截；② OCR 默认 CPU；③ 发 fixed-shape 图，动态图需先过 ORT 加载验证；④ LaMa DML 不可用，修复走 CPU/可选 CUDA。
- 集成：证据入库（本轮提交）。

