---
id: AUDIT12-PUBLISH-OUTPUT-1
title: publish.ps1 默认输出移出仓库并限制递归清理（AUDIT-12-CAND-001 P3）
kind: implementation
governance_version: 3
status: ready
resume_status: ready
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: [AUDIT07-EXPORT-HOOK-OPTIONS-1]
base_commit: 22cb0d3d1
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/AUDIT12-PUBLISH-OUTPUT-1
allowed_paths:
  - apps/desktop-avalonia/scripts/publish.ps1
  - tests/**
  - verification/AUDIT12-PUBLISH-OUTPUT-1/**
  - doc/tasks/AUDIT12-PUBLISH-OUTPUT-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# AUDIT12-PUBLISH-OUTPUT-1：publish.ps1 默认输出移出仓库并限制递归清理（AUDIT-12-CAND-001 P3）

## 来源与目标

`AUDIT-12-CAND-001`（P3，交付工具）：`apps/desktop-avalonia/scripts/publish.ps1` 默认 `OutputDirectory` 为仓库内 `apps/desktop-avalonia/artifacts/win-x64-single`，目录存在时 `Remove-Item -Recurse -Force` 后运行 `dotnet publish`；违反产物应放在相邻 workspace 的规则。目标：默认输出改到相邻 `G:\CODEX\New Manga.workspace\` 的专用目录；清理只允许作用在该专用目录（拒绝仓库内/任意路径的递归清理）；不执行真实 publish/安装/卸载（当前环境禁止）。

## Acceptance Criteria

- [ ] **AC1**：静态核对 publish.ps1 的默认输出、清理与参数语义，记录修改点与兼容性风险（调用方/CI 影响）。
- [ ] **AC2**：默认 `OutputDirectory` 改到相邻 workspace 专用目录；目标路径规范化校验（拒绝仓库内默认清理、拒绝 root/盘符根）；显式 `-OutputDirectory` 仍可用且受同样校验。
- [ ] **AC3**：用 disposable 目录验证脚本的路径/清理逻辑（不执行真实 publish、不写仓库 artifacts）；记录命令/EXIT；`dotnet publish` 本体 NOT_RUN（当前 Task 不执行发布）。
- [ ] **AC4**：证据 pin、四项门禁、资源 closeout、DSH 自动裁决。

## 允许修改范围

- `apps/desktop-avalonia/scripts/publish.ps1`
- `tests/**`（脚本逻辑测试，如伪 dotnet/仅路径校验；不执行真实发布）
- `verification/AUDIT12-PUBLISH-OUTPUT-1/**`
- 本 Task 卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 禁止范围

执行真实 `dotnet publish`、安装、卸载、发布、上传；产品源码；依赖；真实用户数据；远端；历史改写。

## 测试要求

脚本逻辑可用 PowerShell 在 disposable 目录验证（路径解析/拒绝分支）；真机 clean publish 与产物验证为 NOT_RUN，不得声称已生成安装包。
