---
id: RELEASE-REPACK-1
title: sidecar 重打包与同构建复验
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: 97de0fa99
branch: task/RELEASE-REPACK-1
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RELEASE-REPACK-1
allowed_paths:
  - doc/tasks/RELEASE-REPACK-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - packaging/**; apps/desktop-avalonia/scripts/**
  - verification/RELEASE-REPACK-1/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-1/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-1/**
---

# RELEASE-REPACK-1：sidecar 重打包与同构建复验

## 背景

CORE-PIPELINE-FIX-1（color analyzer + 空检测语义）与 RUN-BINDING-FIX-1（Host 注入 bindings）后，**冻结 `core_service.exe`（`2b36bfeb…`）仍是旧构建**，修复未进发布件。用户推荐「打包+翻译」批的第一步。

## Acceptance Criteria

- [ ] **AC1 重打包**：用当前 `src/` 重打包 `core_service` sidecar（base 与 models 两个配置，`packaging/m2ac5/core_sidecar.spec` + `build_sidecar.ps1`），产出新 exe；记录新旧 sha256 与大小；闭包仍 torch-free。
- [ ] **AC2 同构建复验**：用**新构建** exe 对 BOOK-FIXTURE 8 页跑 Run（走 Host 命令面）：`ocr` 3/3 completed（无 PROVIDER_NOT_CONFIGURED）、`color` 3/3 completed、页 4–8 completed(0 region)；如实记录 translate 是否仍 typed 缺口。
- [ ] **AC3 发布件**：重打 base zip + models zip 到 `task-envs/FINAL-VALIDATION-1/out/`（或新目录 `RELEASE-REPACK-1/out`），跑 `install-verify`/`install-smoke`（安装/卸载幂等、sidecar 随包、console 窗口 0、许可证一致）。
- [ ] **AC4 元数据**：更新 `VERSION.json`（devices/构建信息）、`THIRD_PARTY_LICENSES`/`NOTICE` 若闭包变化；README 安装说明同步。
- [ ] **AC5 门禁**：`scripts/test.ps1` 全绿（≥177）；pytest 基线（3F/2753P/9S）无新增失败；`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。

## 允许修改范围

`packaging/**`、`apps/desktop-avalonia/scripts/**`、本卡、STATUS/PLAN/LEDGER、`verification/RELEASE-REPACK-1/**`、workspace。

## 禁止范围

不改 Python Core 语义/Host 契约/旧壳、不 push、不 gc/prune；不得只改文档不重打包；不得复用旧 exe 冒充新构建（必须给新旧 sha256 对照）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
