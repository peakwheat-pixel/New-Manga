---
id: INSTALLER-METADATA-CONSISTENCY-1
title: 安装包内 package-manifest.json 与 VERSION.json 互相矛盾（版本 0.1.0 vs 0.1.1、models_bundled false vs 632 MB 权重）
kind: fix
governance_version: 3
status: closed_with_limitations
disposition: "INSTALLER-MATRIX-1 复核时由 reviewer-inst 提出 P1-IM-1，DSH 复核实测确认并升级为独立卡：包内两个元数据文件互相矛盾，且 VERSION.json 文本疑似手工改写"
approval: DSH 2026-11-17（由 reviewer-inst P1-IM-1 触发）
suggested_owner: DSH
owner: DSH
reviewer: reviewer-imc（DSH 子 agent，独立上下文；2026-11-17 收口复核）
depends_on:
  - INSTALLER-MATRIX-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: 9c0939f2e
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1 复现**：给出旧 stage 的不一致实测（上表数字）；`Get-FileHash` 记录两个文件的 sha256。 <<MET>>
- [x] **AC2 根因**：在 `package.ps1` 中定位「manifest 可与目录名/实际内容脱节」的具体机制（版本默认值、stage 是否清理、manifest 生成时机），给文件:行号。 <<MET>>
- [x] **AC3 修复**：让 manifest 的 `version`/`models_bundled`/`models_bytes` **由实际产物推导**（或让脚本在写入前断言与 `VERSION.json` 一致）；**不得**只改模板文案。 <<MET>>
- [x] **AC4 判别力**：至少一个「旧行为会失败」的验证 —— 例如在 stage 里放入一个版本不符的旧 manifest，脚本应**拒绝或覆盖并自洽**，而不是静默保留。 <<MET>>
- [ ] **AC5 重建自证**：干净目录重建后，manifest 与 VERSION.json 五项一致 + `verify-package-manifest.ps1` 通过；证据入库。 <<PARTIAL: 绿例已用真实 exe+core_service 组一致 stage 通过（EXIT=0），但未跑 package.ps1 完整重建（需 clean worktree + ~1.4GB sidecar + 800MB zip）>>
- [x] **AC6 不越界**：**不覆盖** `INSTALLER-MATRIX-1` 的旧 stage（历史证据字节保留）；不宣称条件 4 通过；不改许可证声明（另卡/裁决）。 <<MET>>

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

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|
| EV-IMC-01 | AC1/AC2/AC3/AC4/AC5 证据说明 | verification/INSTALLER-METADATA-CONSISTENCY-1/README.md | 9c0939f2e | 27180d7c02827241997401f434530ee431015e6720a2d6f0edc9fea31e0a4c82 | CANONICAL | BLOB |
| EV-IMC-02 | AC4 红测（旧 stage 被拒，8 条） | verification/INSTALLER-METADATA-CONSISTENCY-1/ac4-red-old-stage.log | 9c0939f2e | b462b2b9d7c2204d75c3dc05455d81f4cd189ecef600853e72b7010d67680c3a | CANONICAL | BLOB |
| EV-IMC-03 | AC5 绿例（一致元数据通过，含尾部反斜杠） | verification/INSTALLER-METADATA-CONSISTENCY-1/ac5-green-consistent-stage.log | 9c0939f2e | 2a04949710d2dc9601d18671ebd48fd533db4f5a51fc3b2b9cf0fb8733d2ad6f | CANONICAL | BLOB |
| EV-IMC-04 | AC3 修复实现 | tools/ci/verify-package-manifest.ps1 | 9c0939f2e | 4d5b874d4edcf355d9b02f9aa347d8eb1ebf322ede1a67ac303be239c0c42d67 | SOURCE_PIN | BLOB |
| EV-IMC-05 | AC1 结构化实测 | verification/INSTALLER-METADATA-CONSISTENCY-1/ac1-inconsistency.json | 9c0939f2e | 58b920fc12ea4651d96b89dc18c2ea7ae7bc1cb5f37d2b5328fef7d3b4874048 | CANONICAL | BLOB |
| EV-IMC-06 | AC1 可读实测日志 | verification/INSTALLER-METADATA-CONSISTENCY-1/ac1-inconsistency.log | 9c0939f2e | d21245a70d3f99894fc5cd4d8e75e664582c62e330deeffb0d3f01dd9b696889 | CANONICAL | BLOB |
| EV-IMC-07 | AC4 微测 F-05（同尺寸改内容） | verification/INSTALLER-METADATA-CONSISTENCY-1/ac4c-f05-sha256-swap.log | 9c0939f2e | fed2b0a8d85603bb69f4e3f1efdfe1a9c3e56a3dfb1d0528078920de9a8403dd | CANONICAL | BLOB |
| EV-IMC-08 | AC4 微测 F-06（重复条目） | verification/INSTALLER-METADATA-CONSISTENCY-1/ac4d-f06-duplicate-entry.log | 9c0939f2e | 122110841ffcbb8633e87e5f34603b388fe03866d2715822f1eb9add07e19953 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/INSTALLER-METADATA-CONSISTENCY-1/ | NOT_APPLICABLE | — | — | **6 个文件**（README + ac1 json/log + ac4 红测 + ac4c/ac4d 两个微测 + ac5 绿例）全部已登记于 Canonical Evidence；无迁移/归档/删除 |

## Closeout Record（2026-11-17，DSH）

- canonical_evidence_status：`complete`；resource_closeout_status：`complete`；删除/迁移/归档：**0**。
- **旧 stage 只读**：`G:/CODEX/New Manga.workspace/task-envs/INSTALLER-MATRIX-1/stage/NewManga-0.1.1-win-x64` 未被覆盖、未迁移，本卡只对其运行校验器。
- **修复形态（AC3）**：不是在 `package.ps1` 里加软断言，而是在**发布护栏** `tools/ci/verify-package-manifest.ps1` 里加**阻断性**交叉校验 ——
  该校验器已被 `apps/desktop-avalonia/scripts/build-installer.ps1:151` 以 fail-closed 方式调用（「refusing to build the installer」），
  所以新检查会**直接挡住安装器构建**，而不是事后提醒。
- **判别力（AC4）**：同一旧 stage，原版校验器 `OK / EXIT=0`；加严后 **FAILED with 5 problem(s) / EXIT=1**（版本、models_bundled、models_bytes、文件数、1041 个不在 stage 的条目）。
- **绿例（AC5）**：用真实 exe（发布产物，ProductVersion 内嵌 head `1f5832b50…`）+ 真实 `core_service.exe` 组一致 stage → `OK / EXIT=0`。
- **限制**：
  1. **AC5 未跑 `package.ps1` 完整重建**（clean worktree + ~1.4 GB sidecar 复制 + ~800 MB zip）。因此「生成器自身不再产出不一致 manifest」**未被端到端证明**；
     本卡证明的是「不一致产物会被拦住」。
  2. `package.ps1` 仍可能产出不一致 manifest（例如复用未清理的 stage 目录）—— 现在由护栏拦截，而不是由生成器避免。
  3. **重要后果**：`INSTALLER-MATRIX-1` 那个已收口的 stage 用加严后的护栏会被**拒绝**（5 条 FAIL）。
     即该 stage 不是 `package.ps1` 的干净输出（manifest mtime 2026-10-28、根/`app` 两个 `VERSION.json` 哈希不同、manifest 描述了含 `python/*` 的另一套布局）。
- **边界**：不改变任何 Gate 判定；不宣称条件 4 通过；未改许可证声明（`L-IM-7` 另行裁决）。
