---
id: PACKAGE-VERSION-JSON-DERIVED-1
title: package.ps1 由磁盘推导写出 VERSION.json 顶层 models_bundled / models_bundled_bytes（现护栏会拒绝干净产物）
kind: fix
governance_version: 3
status: proposed
disposition: "reviewer-imc 复核 INSTALLER-METADATA-CONSISTENCY-1 时发现的 P1（F-02）：生成器不写顶层字段，护栏缺字段即 FAIL、build-installer fail-closed ⇒ 干净 package.ps1 产物也无法过闸"
approval: DSH 2026-11-17（由 reviewer-imc F-02 触发）
suggested_owner: DSH
owner: null
reviewer: null
depends_on:
  - INSTALLER-METADATA-CONSISTENCY-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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

- [ ] **AC1 复现缺口**：用现码 `package.ps1` 产出的 `VERSION.json`（或对其模板的直接证据）证明顶层两字段缺失，并说明护栏因此 FAIL。
- [ ] **AC2 修复**：`package.ps1` 写入 `VERSION.json` 时**由磁盘推导**写出顶层 `models_bundled` / `models_bundled_bytes`（与 `:80-81` 的既有推导复用，不新增第二套计算）。
- [ ] **AC3 判别力（红）**：修复前，产出的 stage 跑护栏 → FAIL（顶层字段缺失）；修复后同流程 → PASS。
- [ ] **AC4 端到端（绿）**：干净目录 + `-SidecarDir` 指向既有 core-sidecar 的 `package.ps1` 运行后，护栏 `EXIT=0`。
- [ ] **AC5 不越界**：不改 `installer.nsi`、不改护栏的检查集合（那是别卡）、不改许可证声明。

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
| AC1 | 读 `package.ps1:141-151` + 护栏 `:120-122` | 无 | NOT_RUN | 无 |
| AC3 | 修复前跑护栏（红） | 需要一次 `package.ps1` 产物或模板级证据 | NOT_RUN | 无 |
| AC4 | `package.ps1 -SidecarDir <既有 sidecar> -OutputRoot <workspace>` + 护栏 | clean worktree、~1.4 GB 复制 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- 依赖 `INSTALLER-METADATA-CONSISTENCY-1`（该卡发现了字段缺口）。
- **风险 R1**：`package.ps1` 会跑 GPU probe 与 zip 压缩；本卡可只验证到 stage（不打包），但需在卡面说明验证边界。
- **风险 R2**：`package.ps1` 要求 clean worktree（`build.ps1` 有该断言，`package.ps1` 需确认），实现时可能需要临时 worktree。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文）。
- 实际测试：尚无。
