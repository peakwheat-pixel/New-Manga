---
id: GPU-ORT-PROBE-1
title: GPU 状态改 ORT EP 探测（打包后正确显示）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_followups_batch_a2
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: 171529b5d
branch: task/GPU-ORT-PROBE-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GPU-ORT-PROBE-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GPU-ORT-PROBE-1
allowed_paths:
  - doc/tasks/GPU-ORT-PROBE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/GPU-ORT-PROBE-1/**
  - G:/CODEX/New Manga.workspace/task-envs/GPU-ORT-PROBE-1/**
  - G:/CODEX/New Manga.workspace/worktrees/GPU-ORT-PROBE-1/**
---

# GPU-ORT-PROBE-1：GPU 状态改 ORT EP 探测

## 背景

`devices/manager.py` 仍用 torch 探 CUDA；主包闭包已无 torch → 打包后设置页 GPU 状态显示"不可用"（对 ONNX 推理无影响）。INFER-BASELINE/CORE-SLIM-2 已确定默认 EP=DirectML。

## Acceptance Criteria

- [x] **AC1 探测替换**：设备探测改为 **onnxruntime EP**（`get_available_providers()`：DmlExecutionProvider/CUDAExecutionProvider/CPUExecutionProvider），返回设备名与可用状态；torch 仅在开发环境（有 torch 时）作为补充信息，不作为主判据。→ **MET**：`manager.py` 以 ORT EP 为唯一可用性判据（DML>CUDU>ROCm>MIGraphX>TensorRT→CPU），注册表补名称/显存，torch 仅名称补充；`probe_snapshot()` 供证据。
- [x] **AC2 打包验证**：用发布包（无 torch 闭包）启动 → 设置页 GPU 状态显示 **DML 可用**（本机 RTX 5070 Ti）；证据：截图 + 探测 JSON。→ **MET**：重建 torch-free 闭包并重打包（base 97.88MB），发布件设置页显示「GPU：NVIDIA GeForce RTX 5070 Ti · DirectML 可用」；`screens/01-settings-gpu.png` + `settings-page-evidence.json` + `device-probe-buildenv.json`。
- [x] **AC3 单测**：EP 组合矩阵（DML only / CUDA+DML / CPU only）单测覆盖。→ **MET**：新增 7 项（DML only / CUDA+DML / CPU only / 空 providers / torch-only 补充 / snapshot）；`test_devices.py` 28 passed。
- [x] **AC4 回归**：pytest 相对基线（3F/2739P/9S）无新增失败；`scripts/test.ps1` 全绿；闭包仍无 torch（spec 断言）。→ **MET**：pytest **3F/2746P/9S**（基线 2739P+新增 7，失败集合同基线 0 新增）；test.ps1 **149/149 passed, 0 skipped**；`build_sidecar.ps1 -Force` 闭包断言 `(856 pure modules, torch-free) + DirectML.dll`。
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。→ **MET**：check.ps1 PASS；pin 见下；`doc/handoffs/GPU-ORT-PROBE-1-handoff.md`。

## 允许修改范围

`src/**`（仅设备探测模块与相关测试）、本卡、STATUS/PLAN/LEDGER、`verification/GPU-ORT-PROBE-1/**`、workspace。

## 禁止范围

不改推理默认 EP、不改模型清单、不改协议/Host 契约、不改旧壳、不 push、不 gc/prune。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/GPU-ORT-PROBE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/GPU-ORT-PROBE-1 | `out/`（base 包 97.88MB，VERSION.json.devices 记录 DML 能力）、`evidence-private/`（test.ps1 证据副本） | 发布件与证据引用；关闭时按裁决保留/清理 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
