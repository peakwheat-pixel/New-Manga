---
id: M2-PROD-DETECT-ENV-1
title: 恢复 manga 检测链路的运行环境基线
kind: environment
governance_version: 3
status: blocked
language: zh-CN
parent: M2-PROD-DETECT-1
blocked_by: null
blocked_reason: 本机离线，pip index 不可达且缓存无 transformers wheel；需在有网络的环境执行
approval: released_by_r42_20261020
suggested_owner: DSH
owner: DSH
reviewer: ZCode
depends_on: []
base_commit: 0e93a5687
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/M2-PROD-DETECT-ENV-1
allowed_paths:
  - verification/M2-PROD-DETECT-ENV-1/
---

# M2-PROD-DETECT-ENV-1：恢复 manga 检测链路的运行环境基线

## 来源与目标

**来源**：`verification/PDF-STREAM-FIX-1/full-suite-failure-classification.md`（A 类）与 r42 裁定 §三。

**当前本机 manga 检测链路**完全不可用**——两个真实检测用例在**模型加载阶段**失败**：

```
AttributeError: module transformers has no attribute RTDetrV2ForObjectDetection
```

**三方对照（都已核实）**：

| 方 | 内容 | 判定 |
|---|---|---|
| **权重** `config.json` | `architectures: ["RTDetrV2ForObjectDetection"]`、`transformers_version: "4.49.0"` | 声明需要 V2 |
| **代码** `detection_manga.py:525` | `transformers.RTDetrV2ForObjectDetection` | **与权重一致，正确** |
| **`requirements.txt` L28** | **`transformers==5.17.0`** | 项目固定基线 |
| **本机** | **`4.48.3`** | **不符合项目自身基线** |

**顺带核实**：同组的 `torch` 装的是 `2.11.0+cu128`，**不是偏离**——
`requirements.txt` L9-12 明确写 GPU/CUDA wheels 是单独打包决定、不在文件内，
且记录的正是该版本与 RTX 5070 Ti。`safetensors` 一致。

**所以本 Task 的目标不是改代码，是让运行环境符合项目已声明的依赖基线。**

## Acceptance Criteria

- [ ] **AC1 环境记录**：记录执行环境、Python 版本、实际安装包版本及安装来源；
  核对 `requirements.txt` 的 `transformers==5.17.0`、`torch==2.14.0`、`safetensors==0.8.0` 基线，
  并说明实际平台与该基线的兼容性处理。
- [ ] **AC2 本地权重构造**：**在不联网下载权重的前提下**，确认本地权重目录及其 `config`
  与受测代码使用**同一模型快照**；从该本地快照成功构造 `model` 与 `processor`。
- [ ] **AC3 真实用例**：在该环境执行两个真实检测用例（候选检测 / 空白页零候选），
  **逐项记录实际结果**。若环境或权重无法满足，**标 `BLOCKED` 或 `NOT_RUN` 并保留日志**，
  **不得报告「检测链路可用」**。
- [ ] **AC4 落点与复现**：明确环境修复落点（隔离 venv / Task 环境 / CI 环境）及复现方式；
  **不以升级全局 Python 环境作为默认操作**。
- [ ] **AC5 不改 V2 为 V1**：**不得为迁就旧运行时把 `RTDetrV2ForObjectDetection` 改成 V1 类**，
  也不得只改测试断言。

## 允许修改范围

- `verification/M2-PROD-DETECT-ENV-1/`
- **本 Task 预期不改仓库代码**；若确需改动，须先由 Codex 重新冻结范围

## 禁止范围

- **不得修改 `src/infrastructure/providers/detection_manga.py` 的模型类选择**
- 不得修改 `tests/**` 以求变绿
- 不得联网下载权重替代本地快照

## 测试要求

- 复用 `tests/providers/test_detection_manga_real.py` 的两个用例作为验收探针
- 证据须含实际版本输出、加载成功/失败日志、两个用例的逐项结果

## 依赖、风险与阻塞

| # | 项 |
|---|---|
| **B1** | **本机离线**：`python -m pip index versions transformers` → `No matching distribution found`；pip 缓存中 `transformers` 相关 wheel 为 **0 个**。需在有网络的环境执行 |
| **B2** | `requirements.txt` 钉 `transformers==5.17.0`，可能与已装 `torch 2.11.0+cu128`（GPU 变体）存在兼容性差异，须实测而非假定 |
| **R1** | 若按锁定基线仍无法加载权重，再以新证据另行判断是否需要代码 Task |

## 修复前声明口径

**在此 Task 完成前，任何涉及检测链路的陈述都必须写成**：

> **「检测实现与权重预期使用 RT-DETR-v2；当前本机运行环境 `transformers` 版本不符合项目固定依赖，
> 两个真实检测用例未通过，**本机 manga 检测链路目前不可用**，
> 尚未验证正确环境下的真实推理结果。」**

**不得简写为「9 个旧测试红」，也不得写成「检测链路已可用」。**

## 交付与运行记录

（未开始）

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

**本 Task 无资源删除、迁移或归档。**

| resource | source_path | disposition | destination_path | sha256/manifest_path | notes |
|---|---|---|---|---|---|
| **（无）** | — | **NOT_APPLICABLE** | — | — | 仅环境恢复与证据 |

**closeout_counts**：`deleted=0`、`moved=0`、`migrated=0`、`archived=0`。

## Closeout Record

（未开始）
