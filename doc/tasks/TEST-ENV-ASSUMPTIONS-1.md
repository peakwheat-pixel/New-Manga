---
id: TEST-ENV-ASSUMPTIONS-1
title: 把可选运行时假设从测试中断言移出
kind: implementation
governance_version: 3
status: closed_with_limitations
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
integration_commit: 9c594cd4f
delivery_head: 9c594cd4f
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1 无运行时一侧** <<MET>>
- [x] **AC2 有运行时一侧** <<MET>>
- [x] **AC3 确定性** <<MET>>
- [x] **AC4 不伪装环境** <<MET>>
- [x] **AC5 不回归** <<MET>>
- [x] **AC6 零 `src/`** <<MET>>

### AC 证据

| AC | 证据 |
|---|---|
| AC1 | `env_sim.modules_state(absent=…)` / `with_optional_runtimes(available=False)` / `gpu_state(available=False)`；4 个原测试各强制其前提 |
| AC2 | 新增 4 个存在侧测试；`tests/providers` 从 6 failed 变为 2 failed（余 2 属离线环境 Task）|
| AC3 | 7 个 sabotage 全部被抓（`two-sided-coverage.md` §四）——含 4 个针对原始缺失侧方向 |
| AC4 | 未卸载依赖、未改断言值；`env_sim` 只在测试进程内 patch |
| AC5 | 440 passed / 3 skipped；3 个 skip 均为改动前既有，本 Task 未新增 skip |
| AC6 | `git diff --stat` 只含 `tests/providers/` 与 `verification/`（见 Closeout Record）|

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
| EV-ENV-SIM | AC3 | `tests/providers/env_sim.py` | 20b087d7e | - | CANONICAL |
| EV-ENV-DEV | AC1/AC2 | `tests/providers/test_devices.py` | 20b087d7e | - | CANONICAL |
| EV-ENV-BOOT | AC1/AC2 | `tests/providers/test_bootstrap_providers.py` | 20b087d7e | - | CANONICAL |
| EV-ENV-REG | AC2 | `tests/providers/test_registry_readiness.py` | 20b087d7e | - | CANONICAL |
| EV-ENV-DOC | AC3 | `verification/TEST-ENV-ASSUMPTIONS-1/two-sided-coverage.md` | 20b087d7e | - | CANONICAL |

## Resource Manifest

**本 Task 无资源删除、迁移或归档。**

| resource_type | source_path | disposition | destination_path | sha256/manifest_path | notes |
|---|---|---|---|---|---|
| （无） | — | NOT_APPLICABLE | — | — | 只改测试与新增证据 |

**closeout_counts**：`deleted=0`、`moved=0`、`migrated=0`、`archived=0`。

## Closeout Record

- **Closeout date**：2026-10-20 · **Reviewer**：待 ZCode（按协作协议 §5）
- **canonical_evidence_status**：`complete`
- **resource_closeout_status**：`complete`
- **删除、迁移、归档数量/字节数**：**0**

### 改动清单

| 文件 | 性质 |
|---|---|
| `tests/providers/env_sim.py` | **新增**，测试专用环境模拟 |
| `tests/providers/test_devices.py` | 2 个测试加前提强制 + **新增 2 个存在侧测试** |
| `tests/providers/test_bootstrap_providers.py` | 1 个测试加前提强制 + **新增 1 个存在侧测试** |
| `tests/providers/test_registry_readiness.py` | 1 个测试加前提强制 + **新增 1 个存在侧测试** |

**`src/` 零改动**（可用 `git diff --stat` 核实）。

### 限制

| # | 限制 |
|---|---|
| **L1** | **未独立 Review**——本 Task 由 DSH 实现，按协作协议须由 ZCode 审 |
| **L2** | **剩余 2 个 `tests/providers` 失败属 `M2-PROD-DETECT-ENV-1`**（`transformers` 版本，本机离线）|
| **L3** | **`env_sim` 依赖两个私有名**（`_module_present`、`probe_module`）。若未来重构改其位置，测试会以 `AttributeError` 红——**这是有意的**：宁可红，不可静默失效 |
| **L4** | **判别力脚本未入库**（一次性工具）；其逻辑在证据 §四 可复现 |

### 后续建议

1. **交 ZCode 独立 Review**（L1）
2. `M2-PROD-DETECT-ENV-1` 在有网络环境执行

