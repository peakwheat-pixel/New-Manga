---
id: VERSION-JSON-GUARD-ALIGN-1
title: package.ps1 不产出 app_build 段、models 字节口径与护栏不一致 ⇒ 干净产物无法过闸
kind: fix
governance_version: 3
status: proposed
disposition: "reviewer-pvd 复核 PACKAGE-VERSION-JSON-DERIVED-1 时实测（F-PVD-01/02）：补 build-manifest 后 package.ps1 exit=0，但护栏仍 exit=1（缺 app_build；models_bundled_bytes 1071 vs 1000）"
approval: DSH 2026-11-17（由 reviewer-pvd F-PVD-01/02 触发）
suggested_owner: DSH
owner: null
reviewer: null
depends_on:
  - PACKAGE-VERSION-JSON-DERIVED-1
  - INSTALLER-METADATA-CONSISTENCY-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/VERSION-JSON-GUARD-ALIGN-1
allowed_paths:
  - doc/tasks/VERSION-JSON-GUARD-ALIGN-1.md
  - doc/reviews/VERSION-JSON-GUARD-ALIGN-1-*.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/scripts/package.ps1
  - verification/VERSION-JSON-GUARD-ALIGN-1/**
---

# VERSION-JSON-GUARD-ALIGN-1：生成器与护栏的两处口径不一致

## 事实（2026-11-17，reviewer-pvd 实测）

1. **F-PVD-02｜缺 `app_build` 段**：`package.ps1` 写 `VERSION.json` 时**不产出 `app_build`**（全仓无生成器：`git log -S app_build -- package.ps1` 为空），
   而 `tools/ci/verify-package-manifest.ps1:63` 缺该段即 `Add-Failure`。复核者实测：
   - 干净 **base** 变体：`package.ps1 exit=0`，护栏 `FAILED with 1 problem(s): VERSION.json has no app_build section`；
   - **models** 变体：另有 2 条失败（见下）。
2. **F-PVD-01｜models 字节口径不一致**：`package.ps1:81` 的 `$modelsBytes` 统计 `models/` **全部文件**（真实 sidecar：632,662,260 B），
   而护栏只累加 `*.onnx`（632,552,582 B），差 **109,678 B**（来自 config/vocab 等文件；`build_sidecar.ps1:147-169` 会复制它们）。
   复核实测：`models_bundled_bytes mismatch: json=1071 actual=1000`（小夹具）。
3. 对照实验：补 `app_build` 并把 models 字节改成 onnx 口径后 → 护栏 `OK / exit=0`，说明**这两条就是全部阻断项**。

## 目标（一个可观察交付结果）

干净目录用 `package.ps1` 产出的 base 与 models 两个变体，`verify-package-manifest.ps1` 都 **EXIT=0**；
且 `VERSION.json` 的 `app_build`（exe sha256/bytes 与嵌入 head）与 `models_bundled_bytes`（口径与护栏一致）都与实物相符。

## Acceptance Criteria

- [ ] **AC1 复现两处缺口**：给出干净 `package.ps1` 产物缺 `app_build` 与 models 字节不一致的实测（变量体/命令/输出），并说明护栏因此 FAIL。
- [ ] **AC2 修复 `app_build`**：`package.ps1` 写入 `app_build`（`exe_sha256`/`exe_bytes`/`repo_head`，head 取打包时 exe ProductVersion 内嵌值或可验证的等价来源）。
- [ ] **AC3 修复字节口径**：使 `models_bundled_bytes` 的语义在生成器与护栏之间**一致**（二者之一是「只算 onnx」，另一个必须同口径；不得两边各写一套）。
- [ ] **AC4 判别力**：修复前的产物跑护栏 FAIL；修复后 base 与 models 两个变体都 PASS（各留日志）。
- [ ] **AC5 不越界**：不改护栏的检查集合（只对齐生成器或明确口径）、不改 `installer.nsi`、不改许可证声明（`LICENSE-VARIANT-DECLARATION-1` 另办）。

## 允许修改范围

- 本卡、`doc/reviews/VERSION-JSON-GUARD-ALIGN-1-*.md`、`verification/VERSION-JSON-GUARD-ALIGN-1/**`。
- `apps/desktop-avalonia/scripts/package.ps1`。
- 若确需改护栏口径（例如把 onnx 改成 models 全文件），须在本卡 AC3 说明理由，并在证据里并列两版输出。

## 禁止范围

- 不得删除/放宽护栏检查以获得 PASS。
- 不得手工改 `VERSION.json` 充数（必须由生成器产出）。
- 不得改 `packaging/nsis/**` 与许可证字段。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 干净 `package.ps1` + 护栏（base/models） | sidecar 需 `build-manifest.json` | NOT_RUN | 无 |
| AC4 | 修复后同流程 | 同上 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- 依赖 `PACKAGE-VERSION-JSON-DERIVED-1`（已补顶层 models 字段）、`INSTALLER-METADATA-CONSISTENCY-1`（护栏）。
- **风险 R1**：`repo_head` 必须与 exe 内嵌值一致才可验证；需确认 `package.ps1` 能读到（`artifacts/publish/manifest-singlefile.json` 或 ProductVersion）。
- **风险 R2**：干净重建需要 sidecar 的 `build-manifest.json`；缺失时需 `build_sidecar.ps1 -Force`（重活）。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文）。
- 实际测试：尚无。
