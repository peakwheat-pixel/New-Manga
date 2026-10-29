---
id: CUDA-PACKAGE-DECISION-1
title: CUDA 可选包决策（基于 INFER-BASELINE-EP-1 实测）
kind: decision
governance_version: 3
status: done
approval: user_authorized_2026-10-29_abc_sequence
suggested_owner: dsh-lead
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [INFER-BASELINE-EP-1, CORE-SLIM-2, GPU-ORT-PROBE-1]
base_commit: 145bccb29
branch: null
worktree: null
integration_commit: 145bccb29
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/CUDA-PACKAGE-DECISION-1
allowed_paths:
  - doc/tasks/CUDA-PACKAGE-DECISION-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/CUDA-PACKAGE-DECISION-1/**
---

# CUDA-PACKAGE-DECISION-1：CUDA 可选包决策

## 决策（2026-10-29，DSH Architect）

**决定：暂不构建 CUDA 可选包（defer）；主包保持 DirectML 默认 EP。** 触发重新评估的条件与备选方案见下。决策依据全部来自已完成的 [INFER-BASELINE-EP-1](INFER-BASELINE-EP-1.md) 实测（RTX 5070 Ti 16GB，2026-10-26）。

## Acceptance Criteria

- [x] **AC1 决策产出**：基于 INFER-BASELINE-EP-1 实测数据给出明确决策（defer + 理由 + 触发条件 + 备选方案），落 `verification/CUDA-PACKAGE-DECISION-1/decision.json`。<<MET>>
- [x] **AC2 指针与登记**：AD002-FOLLOWUPS #9 状态更新（decided/defer）、STATUS/PLAN/LEDGER 同步；不新增构建分支、不改产品代码。<<MET>>

## 依据（实测数据，`verification/INFER-BASELINE-EP-1/`）

| 事实 | 数据 | 影响 |
|---|---|---|
| 默认 EP = DirectML | 检测链从 CPU ≈161–252 ms/页压到 ≈23–26 ms/页（7.4–11×），无需 CUDA 运行时，覆盖 NVIDIA/AMD/Intel | 主包默认成立 |
| CUDA 对 2 个模型必要 | `manga-ocr`：DML 97.87 ms vs CUDA 23.17 ms（4.2×）；`LaMa-fp32-512`：**DML 直接运行失败**（DmlFusedConv 80070057），CUDA 76.92 ms | 若用户需要高质量 OCR/修复，CUDA 有真实收益 |
| PP-OCRv4 GPU 反而更慢 | CPU 135.85 / DML 250.92 / CUDA 496.09 ms（动态 shape） | 不是所有模型都该上 GPU |
| 体积预算 | AD-002 §3.5：Core CPU 分发 ≤2 GB、CUDA 可选包 ≤8 GB；实测可选 CUDA 包：仅 ORT-CUDA **2296.0 MB** / 含 torch **7005.8 MB**（均 ≤8 GB）；必须 torch 的模型 = **无** | 轻量 CUDA 包（仅 ORT）2.3 GB 可行 |
| 许可 | 仅 `yolo11s-seg` = AGPL-3.0；其余权重 Apache-2.0；CUDA/cuDNN = NVIDIA 专有（不可再分发） | 可选包不能捆绑 NVIDIA 运行时，只能靠用户系统/驱动 |

## 决策理由

1. **当前阶段（0.1.0，无用户基数、签名未通过）**：维护一个 2.3–7 GB 的并行包需要额外的构建/测试/发布/签名渠道与 CUDA 驱动矩阵，收益尚无人证。
2. **主包已能覆盖基础功能**：DirectML 让检测/OCR 在主流 GPU 上可用；LaMa 修复在主包走 CPU 兜底（速度慢但不失败），manga-ocr 降级为较慢的 DML/CPU 路径。
3. **配置可逆**：产品已按 ORT EP 探测设备（GPU-ORT-PROBE-1），CUDA 包一旦需要，可在不改产品契约的前提下新增变体。

## 重新评估的触发条件（任一满足）

- 有 ≥3 个 NVIDIA 用户明确报告 OCR/修复性能或质量瓶颈（可从 issue/反馈统计）；
- 或修复链（inpaint）在真实页上质量成为用户可见问题，需要 LaMa 级模型；
- 或产品进入 1.0 商业/正式分发，需要"高性能包"作为卖点；
- 或 INFER-BASELINE 后续复测显示 CUDA 相对 DML 的收益扩大到检测链。

## 备选方案（若触发）

- **方案 B（推荐）**：轻量 CUDA 可选包 = `-cuda` zip，仅含 ONNX Runtime CUDA EP（2.3 GB），不含 torch；作为独立下载，不替换主包；CUDA/cuDNN 由用户系统提供（文档检查驱动版本）；签名沿用同一 SignPath 项目。
- 方案 C（不推荐）：含 torch 的全量包（7.0 GB），仅在确有 torch-only 模型时考虑（当前无）。
- 无论方案，主包默认 EP 不变（DirectML），避免安装体积/兼容性回退。

## 结论

- 状态：**decided = defer**；不新增构建分支、不改产品代码。
- AD002-FOLLOWUPS-1 的 #9 从"待定"改为"decided（defer）+ 触发条件已登记"。
- 后续若触发：释放 `CUDA-ORT-PACKAGE-1` 实施 Task（构建脚本 + 发布 + 文档 + 测试），预计 2–3 人日。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| decision | AC1 | verification/CUDA-PACKAGE-DECISION-1/decision.json | - | 20325ac85f6801061884fa6db9d8ed34d6cd7a02ddb0e0ed262251c38433ff95 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| none | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | verification/CUDA-PACKAGE-DECISION-1/decision.json | 纯决策卡：无 worktree/task-env/产物；证据仅 decision.json |

## Closeout Record

- Closed：2026-10-29（DSH Architect 决策；用户 2026-10-29 授权按 A/B/C 顺序推进）。
- 资源：无删除/迁移；证据落 `verification/CUDA-PACKAGE-DECISION-1/`（decision.json，64-hex pin）。
- 指针：STATUS/PLAN/LEDGER 已更新；AD002-FOLLOWUPS-1 #9 标记 decided（defer）。
