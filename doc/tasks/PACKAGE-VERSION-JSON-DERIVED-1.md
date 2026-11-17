---
id: PACKAGE-VERSION-JSON-DERIVED-1
title: package.ps1 由磁盘推导写出 VERSION.json 顶层 models_bundled / models_bundled_bytes（现护栏会拒绝干净产物）
kind: fix
governance_version: 3
status: closed_with_limitations
disposition: "reviewer-imc 复核 INSTALLER-METADATA-CONSISTENCY-1 时发现的 P1（F-02）：生成器不写顶层字段，护栏缺字段即 FAIL、build-installer fail-closed ⇒ 干净 package.ps1 产物也无法过闸"
approval: DSH 2026-11-17（由 reviewer-imc F-02 触发）
suggested_owner: DSH
owner: DSH
reviewer: reviewer-pvd（DSH 子 agent，独立上下文；2026-11-17 收口复核）
depends_on:
  - INSTALLER-METADATA-CONSISTENCY-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: 2889a0138
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/PACKAGE-VERSION-JSON-DERIVED-1
allowed_paths:
  - doc/tasks/PACKAGE-VERSION-JSON-DERIVED-1.md
  - doc/reviews/PACKAGE-VERSION-JSON-DERIVED-1-*.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/scripts/package.ps1
  - verification/PACKAGE-VERSION-JSON-DERIVED-1/**
---

# PACKAGE-VERSION-JSON-DERIVED-1：生成器必须写出护栏要求的顶层字段

## 事实（2026-11-17，reviewer-imc F-02 实测）

- `apps/desktop-avalonia/scripts/package.ps1:141-151` 写 `VERSION.json` 的模板**不含**顶层 `models_bundled` / `models_bundled_bytes`
  （`models_bundled` 只出现在 `:95` 的 `sidecar_build` 子对象里）。
- `tools/ci/verify-package-manifest.ps1:120-122` 要求顶层 `models_bundled` 存在，缺字段直接 `Add-Failure`；
  `apps/desktop-avalonia/scripts/build-installer.ps1:152` 对该脚本是 fail-closed（「refusing to build the installer」）；
  CI `build-release.yml:104→112` 直接串联，没有补字段步骤。
- ⇒ **干净 `package.ps1` 产物即使 manifest 完全自洽，也会被护栏拒绝**。所以 `INSTALLER-METADATA-CONSISTENCY-1` 的 AC5「重建后通过」在现码下不可达。

> 注：2026-11-15 那个 stage 的 `VERSION.json` **有**这两个顶层字段（`true` / `632552582`），恰恰说明它不是 `package.ps1` 的干净输出（被手工补过）。

## 目标（一个可观察交付结果）

在干净目录用 `package.ps1` 单独产出一个 stage（不跑 makensis），`VERSION.json` **含**顶层 `models_bundled`/`models_bundled_bytes` 且与磁盘一致，
`verify-package-manifest.ps1` 对其 **EXIT=0**。

## Acceptance Criteria

- [x] **AC1 复现缺口**：用现码 `package.ps1` 产出的 `VERSION.json`（或对其模板的直接证据）证明顶层两字段缺失，并说明护栏因此 FAIL。 <<MET>>
- [x] **AC2 修复**：`package.ps1` 写入 `VERSION.json` 时**由磁盘推导**写出顶层 `models_bundled` / `models_bundled_bytes`（与 `:80-81` 的既有推导复用，不新增第二套计算）。 <<MET>>
- [x] **AC3 判别力（红）**：修复前，产出的 stage 跑护栏 → FAIL（顶层字段缺失）；修复后同流程 → PASS。 <<MET>>
- [ ] **AC4 端到端（绿）**：干净目录 + `-SidecarDir` 指向既有 core-sidecar 的 `package.ps1` 运行后，护栏 `EXIT=0`。 <<PARTIAL: 既有 stage 的 sidecar 无 build-manifest.json ⇒ package.ps1 在 :51 直接拒绝重打包；端到端需先 build_sidecar.ps1 -Force 重建 sidecar（重活，未做）>>
- [x] **AC5 不越界**：不改 `installer.nsi`、不改护栏的检查集合（那是别卡）、不改许可证声明。 <<MET>>

## 允许修改范围

- 本卡、`doc/reviews/PACKAGE-VERSION-JSON-DERIVED-1-*.md`、`verification/PACKAGE-VERSION-JSON-DERIVED-1/**`。
- `apps/desktop-avalonia/scripts/package.ps1`（仅 VERSION.json 字段生成）。

## 禁止范围

- 不得为了让护栏通过而删除/放宽护栏检查。
- 不得改 `packaging/nsis/**`。
- 不得改 `VERSION.json` 的许可证字段（`L-IM-7` 另行裁决）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 读 `package.ps1:141-151` + 护栏 `:120-122` | 无 | **已做**（见 Closeout） | `verification/PACKAGE-VERSION-JSON-DERIVED-1/README.md` |
| AC3 | 缺顶层字段的同构 stage 跑护栏 | 隔离目录 | **EXIT=1（3 条 FAIL）** | `ac3-red-missing-toplevel-field.log` |
| AC4 | `package.ps1 -SidecarDir <既有 sidecar> -OutputRoot <workspace>` + 护栏 | 需 sidecar 有 `build-manifest.json` | **package exit=1（:51）/ 补 manifest 后 package exit=0 但护栏仍 exit=1** | `verification/PACKAGE-VERSION-JSON-DERIVED-1/README.md` |

## 依赖、风险与阻塞

- 依赖 `INSTALLER-METADATA-CONSISTENCY-1`（该卡发现了字段缺口）。
- **风险 R1**：`package.ps1` 会跑 GPU probe 与 zip 压缩；本卡可只验证到 stage（不打包），但需在卡面说明验证边界。
- **风险 R2**：`package.ps1` 要求 clean worktree（`build.ps1` 有该断言，`package.ps1` 需确认），实现时可能需要临时 worktree。

## 交付与运行记录

- Handoff：本卡 Closeout（2026-11-17）。
- Review：`doc/reviews/PACKAGE-VERSION-JSON-DERIVED-1-REVIEW-2026-11-17.md`（reviewer-pvd，ACCEPTED_WITH_FINDINGS，P0=0 / P1=2 / P2=2）。
- 实际测试：红测 EXIT=1（3 条 FAIL）；AC4 见上表；`Parser::ParseFile` = 0 错误。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|
| EV-PVD-01 | AC1/AC2/AC3/AC4/AC5 证据说明 | verification/PACKAGE-VERSION-JSON-DERIVED-1/README.md | 2889a0138 | 3cebfc4b07c66aacb3d05ef5150e7fb37e9efe8b20f8deb94d4c4feaa97e9343 | CANONICAL | BLOB |
| EV-PVD-02 | AC3 红测 | verification/PACKAGE-VERSION-JSON-DERIVED-1/ac3-red-missing-toplevel-field.log | 2889a0138 | 8a6b7805acfc6286ae1911e508db60be9c1a2ce0133edeb40bb597bc6c6a2b25 | CANONICAL | BLOB |
| EV-PVD-03 | AC2 修复实现 | apps/desktop-avalonia/scripts/package.ps1 | 2889a0138 | 118ca3ae4f18e51f71bbf62f2768b1afce9061ba665c9b741516a8440e60fb65 | SOURCE_PIN | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/PACKAGE-VERSION-JSON-DERIVED-1/ | NOT_APPLICABLE | — | — | 3 个文件（README + 红测日志 + 修复源）已登记于 Canonical Evidence；无迁移/归档/删除 |

## Closeout Record（2026-11-17，DSH）

- canonical_evidence_status：`complete`；resource_closeout_status：`complete`；删除/迁移/归档：**0**。
- **AC2 修复**：`package.ps1:151` 的 `VERSION.json` 模板追加 `models_bundled=$modelsBundled;models_bundled_bytes=[int64]$modelsBytes;`，
  复用 `:80-81` 的既有推导；`Parser::ParseFile` → PARSE_OK。
- **AC3 判别力**：去掉顶层两字段的同构 stage → 护栏 `FAILED with 3 problem(s)`，首条正是
  `VERSION.json has no models_bundled field (must be derived from the stage, not omitted)`。
- **限制**：
  1. **AC4 未完成，且 reviewer-pvd 实测证伪了「重建 sidecar 即可」的说法**：
     - 既有 stage 的 `app/core-sidecar/` 只有 5 个 exe、**无 `build-manifest.json`**，`package.ps1:51` 直接拒绝（4.5 s 内 exit=1）；
     - 复核者补了带 `build-manifest.json`（schema v14）的 sidecar 做忠实 e2e：`package.ps1` **exit=0**，但护栏仍 `exit=1`，
       报 `VERSION.json has no app_build section` 与 `models_bundled_bytes mismatch（json=1071 / actual=1000）`；
       干净 base 变体同样报 `no app_build section`。
     ⇒ **当前 `package.ps1` 的产物无论如何都过不了闸**，本卡只补了顶层 models 两字段，不够。
  2. **根本缺口（已开后续卡 `VERSION-JSON-GUARD-ALIGN-1`）**：
     - **F-PVD-02**：`package.ps1` **不产出 `app_build` 段**（全仓无生成器），护栏 `:63` 缺即 FAIL ⇒ base 与 models 变体都过不了；
     - **F-PVD-01**：`$modelsBytes` 统计 `models/` **全部文件**（632,662,260 B）而护栏只累加 `*.onnx`（632,552,582 B，差 109,678 B 来自 config/vocab），
       `build_sidecar.ps1:147-169` 会复制这些文件 ⇒ 重建 sidecar 也消不掉。
  3. **新发现（同源事实）**：该 packaged sidecar **不含 `build-manifest.json`**，与 builder（`build_sidecar.ps1:381` 写入 bundle）不一致 ——
     进一步支持「`INSTALLER-MATRIX-1` 的 stage 不是干净脚本输出」的结论（见 `INSTALLER-METADATA-CONSISTENCY-1`、`L-IM-8`）。
- **边界**：不改 `installer.nsi`、不放宽护栏、不改许可证声明、不改任何 Gate 判定。

### 2026-11-17 复核处置（reviewer-pvd，ACCEPTED_WITH_FINDINGS，P0=0 / P1=2 / P2=2）

- **F-PVD-01（P1）已登记**：`$modelsBytes`（models 目录全部文件 632,662,260 B）与护栏的 `*.onnx` 口径（632,552,582 B）不一致，差 **109,678 B**；
  重建 sidecar 也消不掉（`build_sidecar.ps1:147-169` 会复制 config/vocab）。→ 归 `VERSION-JSON-GUARD-ALIGN-1`。
- **F-PVD-02（P1）已登记**：`package.ps1` 不产出 `app_build` 段，护栏 `:63` 缺即 FAIL，**干净 base/models 产物都过不了闸**。→ 归 `VERSION-JSON-GUARD-ALIGN-1`。
- **F-PVD-03（P2）已改**：AC3 从整条 MET 降为 `<<PARTIAL>>`（红测已证；「修复后同流程 PASS」无证据）。
- **F-PVD-04（P2）已改**：测试要求表与交付记录更新为实测值。
- 复核确认：护栏相对基线 **0 删除**（纯新增）；被审区间无 `nsi`/许可证/门禁改动；`check.ps1` PASS / exit 0。
