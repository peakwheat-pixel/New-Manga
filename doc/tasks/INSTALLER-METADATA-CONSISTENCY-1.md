---
id: INSTALLER-METADATA-CONSISTENCY-1
title: 安装包内 package-manifest.json 与 VERSION.json 互相矛盾（版本 0.1.0 vs 0.1.1、models_bundled false vs 632 MB 权重）
kind: fix
governance_version: 3
status: proposed
disposition: "INSTALLER-MATRIX-1 复核时由 reviewer-inst 提出 P1-IM-1，DSH 复核实测确认并升级为独立卡：包内两个元数据文件互相矛盾，且 VERSION.json 文本疑似手工改写"
approval: DSH 2026-11-17（由 reviewer-inst P1-IM-1 触发）
suggested_owner: DSH
owner: null
reviewer: null
depends_on:
  - INSTALLER-MATRIX-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/INSTALLER-METADATA-CONSISTENCY-1
allowed_paths:
  - doc/tasks/INSTALLER-METADATA-CONSISTENCY-1.md
  - doc/reviews/INSTALLER-METADATA-CONSISTENCY-1-*.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/scripts/package.ps1
  - tools/ci/verify-package-manifest.ps1
  - verification/INSTALLER-METADATA-CONSISTENCY-1/**
---

# INSTALLER-METADATA-CONSISTENCY-1：安装包元数据自相矛盾

## 事实（2026-11-17 实测）

对 `G:\CODEX\New Manga.workspace\task-envs\INSTALLER-MATRIX-1\stage\NewManga-0.1.1-win-x64`：

| 字段 | `VERSION.json` | `package-manifest.json` |
|---|---|---|
| version | **0.1.1** | **0.1.0** |
| variant | base | base |
| models | **BUNDLED**（rtdetr-v2-fixed 164 MB + manga-ocr encoder 328 MB + decoder 112 MB = 603.2 MB） | `models_bundled: **false**`、`models_bytes: **0**` |
| license | `GPL-3.0-or-later` | （manifest 无 license 字段） |
| files | — | 1,968 |

- 该 stage 目录下 `app/core-sidecar/models/` 实际有 **3 个 .onnx、合计 632,552,582 B**（与 VERSION.json 的「BUNDLED」一致，与 manifest 的 `false`/`0` 矛盾）。
- `VERSION.json` 的 `models` / `bundled_weights_license` 文本读起来是**手工改写**（含 "NOTE: this differs from the historical '-models separated' wording of 0.1.0 and the license/notice wording must be reviewed against this fact."、"which was WRONG for this build"），
  而 `apps/desktop-avalonia/scripts/package.ps1` 的模板产出的是「bundled: app/core-sidecar/models (X MiB in-package); no download at run time」。
- 脚本根因（已定位）：`package.ps1` 的 `-Version` 默认 **`'0.1.0'`**，而 `$stageName` 也用同一个 `$Version`；
  manifest 在阶段末尾由 `$files = Get-ChildItem $stage -Recurse -File` 生成 ⇒ 若 stage 目录**未清理**、或用不同 `-Version`/`-WithModels` 跑过多次，
  就会留下**旧 manifest + 新目录名**的组合。

## 目标（一个可观察交付结果）

从干净目录用 `package.ps1` 重建一次 stage，`package-manifest.json` 与 `VERSION.json` 在 **version / variant / models_bundled / models_bytes / 文件数** 上**自洽**，
并且 `tools/ci/verify-package-manifest.ps1` 对重建产物的检查通过。

## Acceptance Criteria

- [ ] **AC1 复现**：给出旧 stage 的不一致实测（上表数字）；`Get-FileHash` 记录两个文件的 sha256。
- [ ] **AC2 根因**：在 `package.ps1` 中定位「manifest 可与目录名/实际内容脱节」的具体机制（版本默认值、stage 是否清理、manifest 生成时机），给文件:行号。
- [ ] **AC3 修复**：让 manifest 的 `version`/`models_bundled`/`models_bytes` **由实际产物推导**（或让脚本在写入前断言与 `VERSION.json` 一致）；**不得**只改模板文案。
- [ ] **AC4 判别力**：至少一个「旧行为会失败」的验证 —— 例如在 stage 里放入一个版本不符的旧 manifest，脚本应**拒绝或覆盖并自洽**，而不是静默保留。
- [ ] **AC5 重建自证**：干净目录重建后，manifest 与 VERSION.json 五项一致 + `verify-package-manifest.ps1` 通过；证据入库。
- [ ] **AC6 不越界**：**不覆盖** `INSTALLER-MATRIX-1` 的旧 stage（历史证据字节保留）；不宣称条件 4 通过；不改许可证声明（另卡/裁决）。

## 允许修改范围

- 本卡、`doc/reviews/INSTALLER-METADATA-CONSISTENCY-1-*.md`、`verification/INSTALLER-METADATA-CONSISTENCY-1/**`。
- `apps/desktop-avalonia/scripts/package.ps1`（仅 manifest/VERSION.json 生成与一致性断言）与 `tools/ci/verify-package-manifest.ps1`（仅一致性检查项）。

## 禁止范围

- 不得覆盖或改写 `INSTALLER-MATRIX-1` 的 stage / setup.exe / 任何 `verification/**` 既有字节。
- 不得修改 `packaging/nsis/installer.nsi` 的安装行为。
- 不得在本卡内改许可证声明（`GPL-3.0-or-later` vs 内置 AGPL 权重）—— 那是 `L-IM-7`，需书面裁决。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 读 stage 两个 JSON + `Get-FileHash` | 无 | NOT_RUN | 无 |
| AC2 | 读 `package.ps1` | 无 | NOT_RUN | 无 |
| AC4 | 旧 manifest 注入 → 期望失败/自洽覆盖 | 隔离目录 | NOT_RUN | 无 |
| AC5 | 干净重建 + `verify-package-manifest.ps1` | makensis 不需要（只到 stage） | NOT_RUN | 无 |

## 依赖、风险与阻塞

- 依赖 `INSTALLER-MATRIX-1`（该 stage 由那轮产出）。
- **风险 R1**：重建 stage 需要 sidecar 目录与 Python；用 `-SidecarDir` 指向既有 stage 的 `core-sidecar` 可避免重跑 sidecar 构建。
- **风险 R2**：`package.ps1` 还会跑 GPU probe 与 zip 压缩，耗时较长；可考虑只验证 manifest 段（但那会削弱 AC5，需在卡面说明）。
- **关联**：`L-IM-6`（本卡主体）、`L-IM-7`（许可证，需裁决）。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文）。
- 实际测试：尚无。
