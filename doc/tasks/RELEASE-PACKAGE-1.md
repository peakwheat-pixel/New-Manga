---
id: RELEASE-PACKAGE-1
title: S5-D 发布件：打包基线 + 升级路径 + 许可一致性 + 实机核验清单
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: [CORE-TILE-EMIT-1]
base_commit: 7b07da6a4
branch: task/RELEASE-PACKAGE-1
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-PACKAGE-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RELEASE-PACKAGE-1
allowed_paths:
  - doc/tasks/RELEASE-PACKAGE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - scripts/**
  - verification/RELEASE-PACKAGE-1/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-PACKAGE-1/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-PACKAGE-1/**
---

# RELEASE-PACKAGE-1：S5-D 发布件与实机核验

## 来源

S5 拆分（`LEGACY-SHELL-REMOVAL-1` BLOCKED 段）。D4 安全（S5-A/B）与 Core tile（CORE-TILE-EMIT-1）已完成，进入发布件收口。

## Acceptance Criteria

- [ ] **AC1 打包基线**：提供一键脚本产出可安装包（优先 MSIX 或 zip+安装脚本），产物 ≤150MB（不含模型）或明确模型分离说明；脚本可在干净环境复跑。
- [ ] **AC2 升级路径**：版本号策略 + 数据根兼容（`%APPDATA%\com.newmanga.desktop` 不变）+ 首次运行备份 + 旧版（Tauri 版）数据迁移说明（dry-run 脚本）。
- [ ] **AC3 许可一致性**：包内 `LICENSE`/`NOTICE`/`THIRD_PARTY_LICENSES` 与仓库一致（逐字节比对）；字体仅系统栈；AGPL 组件处置结论落文档。
- [ ] **AC4 自动化安装 smoke**：安装→启动→书架→退出无残留（可在无人值守下完成的部分），日志与进程表为证。
- [ ] **AC5 实机人工核验清单**：产出 `MANUAL_VERIFY.md`（Mica 取色、DPR2 400% 像素、进程工作集峰值 ≤1.5GB、微软拼音 20 字、沉浸阅读 Esc），标注需用户在真机执行。
- [ ] **AC6 门禁**：`check.ps1 -TaskPath` PASS；`scripts/test.ps1` 全绿；pytest 相对基线无新增失败；证据 64-hex pin；Handoff。

## 允许修改范围

`apps/desktop-avalonia/**`（打包脚本/清单）、`scripts/**`、本卡、STATUS/PLAN/LEDGER、`verification/RELEASE-PACKAGE-1/**`、workspace。只读：LICENSE/NOTICE/THIRD_PARTY、ADR-0001/0002。

## 禁止范围

不改 Python Core 语义、不改旧壳、不 push、不 gc/prune、不随包商业字体、不伪造成安装成功。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 打包脚本 + 产物校验 | 干净目录 | NOT_RUN | 待填 |
| AC2 | 升级/备份 dry-run | 隔离 env | NOT_RUN | 待填 |
| AC3 | 三件套逐字节比对 | 包内解压 | NOT_RUN | 待填 |
| AC4 | 安装→启动→书架→退出 | 无人值守 | NOT_RUN | 待填 |
| AC5 | 清单产出（人工待执行） | 真机 | NOT_RUN | 待填 |
| AC6 | 门禁 | 全量 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/RELEASE-PACKAGE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/RELEASE-PACKAGE-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
