---
id: GRANT-ISSUER-1
title: Host grant 签发 + shell 动作（7 条真缺口）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_ns_b1_grant
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: 45efe7f00
branch: task/GRANT-ISSUER-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GRANT-ISSUER-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GRANT-ISSUER-1
allowed_paths:
  - doc/tasks/GRANT-ISSUER-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/GRANT-ISSUER-1/**
  - G:/CODEX/New Manga.workspace/task-envs/GRANT-ISSUER-1/**
  - G:/CODEX/New Manga.workspace/worktrees/GRANT-ISSUER-1/**
---

# GRANT-ISSUER-1：Host 侧 grant 签发 + shell 动作（7 条真缺口）

## 背景

NS-RECLASSIFY-1 证明 7 条真缺口在 **Host 侧**：
- 5 条 import/export：Core 有 `ImportPages`/`StartExport`/`GetExportSnapshot`/`CancelExport`，但 grant 需 **host_issuer 签发**；冻结 Core 对未签名 ref 回 `REF_MALFORMED`，Avalonia Host 未实现签发。
- 2 条 host-local shell 动作：`library_reveal_export_folder`、`plugins_open_directory`（Core 无等价命令，Host 本地实现）。

## Acceptance Criteria

- [ ] **AC1 grant 签发**：实现 host_issuer 签发链路（与 host_bridge `issue`/`resolve` 既有契约对齐），使 `library_import_file`/`library_import_folder`/`library_start_export`/`library_get_export_snapshot`/`library_cancel_export` 可真实执行（用 BOOK-FIXTURE 隔离根）；证据含 bridge issue/resolve 日志与输出。
- [ ] **AC2 shell 动作**：2 条 host-local 动作实现（打开资源管理器目录/插件目录），走安全路径白名单（不得接受任意用户路径），真机验证并截图。
- [ ] **AC3 安全边界**：签发只对授权资源 id；失败 typed；不得放宽 TileChannel 摘要校验或资源通道授权。
- [ ] **AC4 parity/回归**：`--check` 零漂移；快照 5 条 NOT_SUPPORTED→IMPLEMENTED（2 条 shell 动作按 Host-local 归类并记录）；`scripts/test.ps1` 全绿；vitest 60/567；pytest 3F/2746P/9S 无新增失败。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision（签发边界/白名单）。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/GRANT-ISSUER-1/**`、workspace。

## 禁止范围

不改 Python Core 语义（发现缺陷先回报）、不改 host_bridge 冻结契约（如确需扩展 wire 版本，必须先在 Task 中回报 DSH 裁决）、不改旧壳、不 push、不 gc/prune。

## 并发注意

与 `RUN-EXPORT-E2E-1` 有交集（E2E 需要 grant 才能真跑 Export）：优先交付 **grant 签发最小可用链路 + 一个 import/export 成功样例**，让 RUN-EXPORT 可复用；与 `NS-WIRE-B1`/`S4-CMD-BATCH-1` 的 registry 改动冲突时以先落地者为准、后落地者 rebase。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/GRANT-ISSUER-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/GRANT-ISSUER-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
