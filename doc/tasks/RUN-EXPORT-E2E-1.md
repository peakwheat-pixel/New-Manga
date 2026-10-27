---
id: RUN-EXPORT-E2E-1
title: Run/Export 命令端到端验证（fixture 书 + models）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_followups_batch_a2
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: 171529b5d
branch: task/RUN-EXPORT-E2E-1
worktree: G:/CODEX/New Manga.workspace/worktrees/RUN-EXPORT-E2E-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RUN-EXPORT-E2E-1
allowed_paths:
  - doc/tasks/RUN-EXPORT-E2E-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/RUN-EXPORT-E2E-1/**
  - G:/CODEX/New Manga.workspace/task-envs/RUN-EXPORT-E2E-1/**
  - G:/CODEX/New Manga.workspace/worktrees/RUN-EXPORT-E2E-1/**
---

# RUN-EXPORT-E2E-1：Run/Export 命令端到端验证

## 背景

S2 遗留的 42 条 NOT_SUPPORTED 中含 Run/Export 类命令；10 条最小集登记为 S4-C（全 PLANNED）。本任务做端到端：在 BOOK-FIXTURE 隔离数据根上验证运行/导出链路。

## Acceptance Criteria

- [x] **AC1 清单与接线**：列出 Run/Export 相关命令（名/参数/返回/Core 路由），在 C# Host 接线；无模型时返回 typed `NOT_CONFIGURED`（不得静默失败）。→ **MET**：9 条 Core-backed 命令接线（StartRun/ControlRun/ResumeBlockedRun/GetRunSnapshot/GetTaskProjection/RetryFailedTargets/StartExport/CancelExport/GetExportSnapshot，minor=3），dispatcher 复刻旧壳签名；无模型 probe 全 8 页 `PROVIDER_NOT_CONFIGURED`（typed）；未知 id `TARGET_NOT_FOUND`/`EXPORT_NOT_FOUND`；集成测试 6 类 typed 断言；`command-list.json`。
- [x] **AC2 Export 真跑**：用 BOOK-FIXTURE 书（8 页）在隔离根执行导出 → 产出可校验文件（如 PDF/图片包/项目文件），校验大小/页数/可打开；证据 JSON + 产物 SHA-256。→ **BLOCKED（如实）**：冻结 Core 导出要求 **translated 页产物**（BOOK-FIXTURE 仅 original → typed `EXPORT_INPUT_UNAVAILABLE`）且 `target_ref` 需 host-control `RegisterExportTarget` grant（HOST-ISSUER 通道未迁移）；两次真实 probe 均 typed 错误，无产物/SHA，未伪造成功。证据 `probe-base.json`/`probe-models.json`。
- [x] **AC3 Run 真跑（含模型）**：用 models 包（`FINAL-VALIDATION-1/out/NewManga-0.1.0-win-x64-models.zip` 中的模型）对同一本书跑最小运行链（检测→OCR→翻译桩/本地翻译→渲染），产出可见结果；记录耗时与失败步骤。→ **BLOCKED（部分链，如实）**：models sidecar + BOOK-FIXTURE 8 页：StartRun 被接受，run 3.1s（热）/6.5s（冷）终态 `completed_with_failures`；页1–3 detect 真实完成（ONNX 模型），OCR 步骤 `PROVIDER_NOT_CONFIGURED`；页4–8 detect `INVALID_INPUT`；未到 translate/render，无可见产物；失败步骤/耗时入 `probe-models.json`。
- [x] **AC4 parity/回归**：parity 快照相应命令 NOT_SUPPORTED→IMPLEMENTED（`--check` 零漂移）；`scripts/test.ps1` 全绿；vitest 60/567；pytest 无新增失败。→ **MET**：`--check` PASS（66 命令零漂移，sha `4c6a4da0…` 未变）；registry **24→33 IMPLEMENTED / 42→33 NOT_SUPPORTED**（9 条变更）；test.ps1 **145/145 passed**；vitest **60/60 文件、567/567**；pytest **3F/2739P/9S**（0 新增）；`parity-update.json` + `evidence/`。
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision（Run/Export 命令面、模型依赖边界）。→ **MET**：check.ps1 PASS；pin 见下；`doc/handoffs/RUN-EXPORT-E2E-1-handoff.md`（含 Record Decision §3）。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/RUN-EXPORT-E2E-1/**`、workspace（含隔离数据根）。

## 禁止范围

不改 Python Core 语义（如发现 Core 缺陷，先回报）、不改 Host 契约语义、不改旧壳、不碰真实用户数据、不 push、不 gc/prune；不得伪造运行成功。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/RUN-EXPORT-E2E-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/RUN-EXPORT-E2E-1 | `probe-base.json`/`probe-models.json`/`core-*.stderr.log`/`data-root-*/`（BOOK-FIXTURE 副本）/`evidence-private/`（test.ps1 新鲜证据） | 证据副本已复制到 `verification/RUN-EXPORT-E2E-1/`；隔离根无真实用户数据；关闭时按裁决保留/清理 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
