---
id: CORE-SLIM-2
title: 检测链瘦身——doctr/torch → ONNX Runtime（目标 Core 运行时 ≤700MB）
kind: research
governance_version: 3
status: done
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: [INFER-BASELINE-EP-1]
base_commit: 21960f4cb
branch: task/CORE-SLIM-2
worktree: G:/CODEX/New Manga.workspace/worktrees/CORE-SLIM-2
integration_commit: fe346c50a
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/CORE-SLIM-2
allowed_paths:
  - doc/tasks/CORE-SLIM-2.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/**
  - tests/**
  - requirements.txt
  - doc/handoffs/**
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

- [x] **AC1 可行性**：基于 `INFER-BASELINE-EP-1` 结论，给出「torch → ORT」的迁移方案与精度/速度对比（检测 IoU/召回、ms/页）。→ **MET**：fixed-shape ONNX（RT-DETR opset17 + manga-ocr enc/dec）+ ORT-DML；10/10 页候选数相同、recall 1.0、meanIoU 1.0、OCR 逐字符 10/10；检测 263.14 → 61.47 ms/页（DML）。见 `verification/CORE-SLIM-2/REPORT.md` §1、`parity.json`。 <<MET>>
- [x] **AC2 实现**：检测链改 ORT（含模型导出/固定 shape/预处理对齐），保留 torch 路径作为可选回退（不随主包）。→ **MET**：新增 `onnx_sessions` / `detection_manga_onnx` / `ocr_manga_onnx`；默认后端 ONNX，`NEWMANGA_DETECTOR_BACKEND=torch` / `NEWMANGA_OCR_BACKEND=torch` 保留旧适配器（不随包；spec 负向断言防回流）。协议/命令语义/Host 契约未改。 <<MET>>
- [x] **AC3 体积**：Core 运行时 ≤700MB；产出 before/after 表与依赖移除清单。→ **MET**：Core 运行时 **970.1 → 186.3 MiB**（余量 513.7 MiB）；闭包 torch 栈 0 命中；`models/` 642.3 MiB 计入模型预算。见 `size-report.md`。 <<MET>>
- [x] **AC4 回归**：pytest 无新增失败（基线 3F/2710P/9S）；`scripts/test.ps1` 全绿；检测样例与 S2/S4 证据口径一致。→ **MET**：pytest **3F/2739P/9S**（失败集合=基线 3 项，0 新增，新增 29 用例）；`test.ps1` **102/102 passed, 0 skipped**；检测候选 10/10 一致（`parity.json`）。 <<MET>>
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision。→ **MET**：`doc/handoffs/CORE-SLIM-2-handoff.md`（含 Record Decision）；pin 见下。 <<MET>>
## 禁止范围

不删除 OCR/检测/修复能力；不改协议/命令语义；不改 Host 契约；不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC4 检测等价 | `python verification/CORE-SLIM-2/tools/parity.py`（build venv：torch 参考 + ORT） | build venv `task-envs/m2ac5-build` | **PASS**：候选 10/10 一致、recall 1.0、meanIoU 1.0；263.14→61.47 ms/页 | `verification/CORE-SLIM-2/parity.json` |
| AC1/AC4 OCR 等价 | 同上（torch greedy 参考 vs 产品 ONNX） | build venv | **PASS**：逐字符 10/10 一致 | `parity.json` |
| AC3 体积 | `python verification/CORE-SLIM-2/tools/measure_bundle.py --bundle <bundle> --label after --out ...` | 新构建 bundle | **PASS**：Core 运行时 186.3 MiB（≤700） | `bundle-before.json`/`bundle-after.json`/`size-report.md` |
| AC2 冻结闭包 | `python verification/CORE-SLIM-2/tools/capability_smoke.py`（无标签副本） | 无标签 sidecar 副本 | **PASS**：7/7 | `capability-smoke.json` |
| AC4 pytest | `python -m pytest -q` | dev env | **PASS**：3F/2739P/9S（无新增失败） | `pytest-after.log` |
| AC4 单命令 | `pwsh -File apps/desktop-avalonia/scripts/test.ps1 -SidecarDirectory <新构建副本>` | dotnet + 无标签副本 | **PASS**：102/102 passed, 0 skipped | `scripts-test.log` |
| AC5 门禁 | `pwsh -File tools/governance/check.ps1 -TaskPath doc/tasks/CORE-SLIM-2.md` | — | PASS | 见 Handoff |
## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E-AC1-PARITY | AC1/AC4 检测+OCR 等价 | `verification/CORE-SLIM-2/parity.json` | `9ebc2caa4` | `801769900815c6ee3e099c542bdeb731cbd9ae37ac2438598085e9b3996982e9` | CANONICAL |
| E-AC2-REPORT | AC1/AC2 方案与实现 | `verification/CORE-SLIM-2/REPORT.md` | `9ebc2caa4` | `333a628941aa04ec5e813094ba3cf8d369fe74f56927401f6eecde205285fcaa` | CANONICAL |
| E-AC3-SIZE | AC3 体积报告 | `verification/CORE-SLIM-2/size-report.md` | `9ebc2caa4` | `bfe98bf8a084fbf89eeaa2d281ba685c437f5c170c9dcea60cfaab2864667986` | CANONICAL |
| E-AC3-BUNDLE | AC3 构建度量 | `verification/CORE-SLIM-2/bundle-after.json` | `9ebc2caa4` | `03bcdf30c941ca16e0b0e55dba68f20122e962464ffd71b1d42d8a2bbcf2d056` | CANONICAL |
| E-AC2-SMOKE | AC2/AC3 冻结能力 smoke | `verification/CORE-SLIM-2/capability-smoke.json` | `9ebc2caa4` | `c05690ac37a735428dbdb50b653e1c7f636d20c0c535a04c91ac176f8bdd7472` | CANONICAL |
| E-AC4-PYTEST | AC4 pytest | `verification/CORE-SLIM-2/pytest-after.log` | `9ebc2caa4` | `abc7b5dd48420e800af0cc85b7453d3ac915bfb27c885bf6d42d0341f0165d85` | CANONICAL |
| E-AC4-DOTNET | AC4 scripts/test.ps1 | `verification/CORE-SLIM-2/scripts-test.log` | `9ebc2caa4` | `ba14fe64066dfb3b4bbdb254227314f5aa87683cd2791b0f78216c0de7634ae8` | CANONICAL |
| E-AC2-BUILD | AC2 打包构建 | `verification/CORE-SLIM-2/build.log` | `9ebc2caa4` | `1bdef965a256bcd3dc0b9dee06a700984a139acf61a70bbf443919272773e8bc` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/CORE-SLIM-2 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/CORE-SLIM-2 | `models/`（staged ONNX，sha256 见 `verification/CORE-SLIM-2/REPORT.md`）、`sidecar-copy/`（无标签副本）、`results/`、`scripts/` | 构建/parity/smoke 均引用该 task-env；关闭时按 workspace 治理裁决 |

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
## Review（DSH 集成复核，2026-10-27）— PASS

- 单命令：scripts/test.ps1 → **102/102**；pytest **3F/2739P/9S**（失败集合=基线 3 项、0 新增、+29 用例）。
- **AC3 达成且余量巨大**：Core 运行时（不含模型）**970.1 → 186.3 MiB（−783.8，余量 513.7）**，远超 ≤700MB 目标；闭包 torch/torchvision/transformers/doctr/cv2/scipy **0 命中**；models 642.3 MiB 计入模型预算；整包 828.6 MiB。
- 等价性：检测 10/10 页候选数一致、recall 1.0、meanIoU 1.0；OCR 逐字符 10/10 一致；检测 263.14 → **61.47 ms/页**（DML）。
- 不变量：默认 ONNX、torch/doctr 为显式可选回退且不随包（spec 负向断言）；协议/命令语义/Host 契约零改动。
- 遗留（记录不阻塞）：绝对精度 vs 人工 GT 未测（无对齐 GT，不冒充）；CUDA 可选包未构建；devices/manager.py 仍用 torch 探 CUDA（建议后续改 ORT EP 探测）；发布前需按新 spec 重建侧车。
- 集成：测试与治理复核通过；未 push。

