---
id: CORE-SLIM-2
title: 检测链瘦身——doctr/torch → ONNX Runtime（目标 Core 运行时 ≤700MB）
kind: research
governance_version: 3
status: ready
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: [INFER-BASELINE-EP-1]
base_commit: 4b0d5f0eb
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/CORE-SLIM-2
allowed_paths:
  - doc/tasks/CORE-SLIM-2.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/**
  - tests/**
  - requirements.txt
  - packaging/**
  - verification/CORE-SLIM-2/**
  - G:/CODEX/New Manga.workspace/task-envs/CORE-SLIM-2/**
---

# CORE-SLIM-2：检测链 ONNX 化 / torch 裁剪

## 背景

CORE-SLIM-1 实测：Core 运行时 970.1 MiB（目标 ≤700MB），缺口 270.1 MiB 全为 ML 栈（torch 365 / cv2 112 / scipy 70 / onnxruntime 63 MiB）。`INFER-BASELINE-EP-1` 将给出 ORT-DML / ORT-CUDA / torch 三档实测与 ONNX 导出可行性。

## 目标

把检测链（python-doctr / RT-DETR-v2 via transformers）迁移到 ONNX Runtime（优先 DirectML），使 torch/torchvision/transformers 从 Core 闭包移除或降为可选包；Core 运行时目标 **≤700MB（不含模型）**，能力不降级。

## Acceptance Criteria

- [ ] **AC1 可行性**：基于 `INFER-BASELINE-EP-1` 结论，给出「torch → ORT」的迁移方案与精度/速度对比（检测 IoU/召回、ms/页）。
- [ ] **AC2 实现**：检测链改 ORT（含模型导出/固定 shape/预处理对齐），保留 torch 路径作为可选回退（不随主包）。
- [ ] **AC3 体积**：Core 运行时 ≤700MB；产出 before/after 表与依赖移除清单。
- [ ] **AC4 回归**：pytest 无新增失败（基线 3F/2710P/9S）；`scripts/test.ps1` 全绿；检测样例与 S2/S4 证据口径一致。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision。

## 禁止范围

不删除 OCR/检测/修复能力；不改协议/命令语义；不改 Host 契约；不 push。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/CORE-SLIM-2 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/CORE-SLIM-2 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
## 实施要点（依据 INFER-BASELINE-EP-1 结论）

- 目标：Core 运行时 970.1MiB → **≤700MB**；路径 = 检测链改 fixed-shape ONNX（RT-DETR-v2 163.7MB @opset17）+ 主包移除 torch/torchvision/transformers（仅保留可选导出/训练包）。
- 硬数据：RT-DETR-v2 fixed 三档可跑、10/10 页框数与 torch 完全相同（DML 22.95ms vs torch-CPU 251.78ms）；manga-ocr encoder/decoder 逐字符 100% 一致，解码循环留 Python。
- 不变量：检测/OCR/修复能力不降级；OCR 默认 CPU；onnxruntime-gpu 版本硬断言；LaMa 走 CPU/可选 CUDA。
- 验收基线：pytest 3F/2710P/9S 无新增失败；scripts/test.ps1 全绿；体积 before/after 表。
