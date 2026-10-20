---
id: TEST-ENV-ASSUMPTIONS-1
title: 把可选运行时假设从测试中断言移出
kind: implementation
governance_version: 3
status: ready
language: zh-CN
parent: P13
blocked_by: null
approval: released_by_r42_20261020
suggested_owner: DSH
owner: DSH
reviewer: ZCode
depends_on: []
base_commit: 0e93a5687
branch: agent/dsh/TEST-ENV-ASSUMPTIONS-1
worktree: G:/CODEX/New Manga.workspace/worktrees/TEST-ENV-ASSUMPTIONS-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/TEST-ENV-ASSUMPTIONS-1
allowed_paths:
  - tests/providers/
  - verification/TEST-ENV-ASSUMPTIONS-1/
---

# TEST-ENV-ASSUMPTIONS-1：把可选运行时假设从测试中断言移出

## 来源与目标

**来源**：`verification/PDF-STREAM-FIX-1/full-suite-failure-classification.md`（B 类）与
r42 裁定 §二。

**4 个测试把「这台机器没装可选重运行时」写成了硬断言。**
**本机装了 `manga-ocr` 且有 CUDA 可用，所以它们必然红。**

| 测试 | 断言 | 本机实际 |
|---|---|---|
| `test_production_stack_starts_without_heavy_runtimes` | `states["manga-ocr"] == "missing_dependency"` | **`'ready'`** |
| `test_real_environment_reports_optional_providers_as_not_ready` | `status.ready is False` | **`True`** |
| `test_gpu_is_unavailable_without_a_runtime_but_reported_not_invented` | `info.state == GPU_UNAVAILABLE` | **`'available'`** |
| `test_cpu_fallback_only_when_the_provider_declares_it` | `plan.device == DEVICE_CPU` | **`'gpu'`** |

**两个测试的**名字**已经承认了前提**（`without_a_runtime` / `without_heavy_runtimes`），
**而代码从未检查那个前提。**

**目标是让这 4 个测试在两种机器上都**真实通过**，
而不是让它们在两种机器上都变绿。**

## Acceptance Criteria

- [ ] **AC1 无运行时一侧**：在模拟「无 manga-ocr / 无可用 CUDA」前提下，
  Provider 如实报告缺依赖、GPU 如实报告不可用；
  声明支持 CPU fallback 时选 CPU 并记录 fallback provenance，不支持时保持拒绝。
- [ ] **AC2 有运行时一侧**：在模拟「有 manga-ocr / CUDA 可用」前提下，
  Provider 与 GPU 如实报告可用；A1 的相反断言在此前提下同样成立。
- [ ] **AC3 确定性**：两侧均由确定性测试覆盖（monkeypatch / 注入探测器 / 等价 seam），
  **不得把一侧留给「另一台裸机碰巧覆盖」**。
  **不得为此新增生产接口。**
- [ ] **AC4 不伪装环境**：不得通过卸载依赖或改断言值来让测试通过；
  在有可选依赖的开发机与无可选依赖的环境均可运行。
- [ ] **AC5 不回归**：`tests/providers` 其余测试保持通过（当前 432 passed / 3 skipped）。
- [ ] **AC6 零 `src/`**：不修改 `src/**`、产品依赖声明、Provider 就绪规则或设备选择语义。

## 允许修改范围

- `tests/providers/` 下 4 个目标测试与必要的 fixture
- `verification/TEST-ENV-ASSUMPTIONS-1/`

## 禁止范围

- **不得修改 `src/**`**（含 `DeviceManager`、Provider 就绪规则、设备选择语义）
- **不得修改** `requirements.txt` 或任何依赖声明
- **不得把断言值改成当前机器的实际值**（那会在 CI 上红）
- **不得用 `skip` 代替分支覆盖**——`skip` 只能用于「该路径在此环境不可达」，
  而两侧逻辑仍须由 AC1/AC2 的确定性测试实际执行

## 测试要求

- 两侧前提各自可确定性构造
- 真实的「当前环境探测」断言（若有）只验证**探测报告与实际事实一致**，
  不断言某个特定值
- 实施后在有依赖的本机与模拟的裸机前提下分别运行
- 验证记录须明确区分 `pass` / `skip` / `fail`

## 依赖、风险与阻塞

| # | 风险 |
|---|---|
| **R1** | `DeviceManager` 可能直接读真实环境而无 seam——**AC3 要求不加生产接口，可能导致某些分支无法确定性构造**。若如此，须记录哪一侧只能用真实环境断言，并说明理由 |
| **R2** | `manga-ocr` 的可用性探测可能在 import 时就固化（模块级 lazy cache），monkeypatch 需在正确时机 |
| **R3** | 改测试可能暴露「原本被 skip 掩盖」的真实缺陷——若发现，应记录而非掩盖 |

## 交付与运行记录

（未开始）

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

**本 Task 无资源删除、迁移或归档。**

| resource | source_path | disposition | destination_path | sha256/manifest_path | notes |
|---|---|---|---|---|---|
| **（无）** | — | **NOT_APPLICABLE** | — | — | 只改测试与新增证据 |

**closeout_counts**：`deleted=0`、`moved=0`、`migrated=0`、`archived=0`。

## Closeout Record

（未开始）
