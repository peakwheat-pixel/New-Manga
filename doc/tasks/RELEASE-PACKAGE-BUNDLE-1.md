---
id: RELEASE-PACKAGE-BUNDLE-1
title: 组装含 sidecar 的可分发 Windows portable 包（当前 HEAD）并做包内启动验证
kind: governance
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - RELEASE-PACKAGE-CURRENT-HEAD-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 B「Gate 条件 4 的可做部分」
base_commit: e2c9fd058
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/RELEASE-PACKAGE-BUNDLE-1
allowed_paths:
  - doc/tasks/RELEASE-PACKAGE-BUNDLE-1.md
  - doc/reviews/RELEASE-GATE-DISPOSITION-2026-11-15.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/RELEASE-PACKAGE-BUNDLE-1/**
---

# RELEASE-PACKAGE-BUNDLE-1：含 sidecar 的可分发包

## 来源

`RELEASE-PACKAGE-CURRENT-HEAD-1` 的 r1 复核 **P1-02a** 指出：

> **单文件包不含 sidecar** —— 94.94 MB 的 exe 无法独立运行，需 792 MB sidecar 外挂
> （`publish-release.ps1:61` 自述 `needs the sidecar bundle at runtime`）⇒ **不是可分发包**。

本卡补上这一块：把 exe + sidecar + 许可证 + 启动脚本组装成**可分发的 portable 包**，
并用**包内路径**实际启动验证（不是拿外挂 sidecar 跑）。

## 目标（一个可观察结果）

产出 `NewManga-<head>-win-x64/`（含 `core-sidecar/`）与对应 zip；
**用包内 exe + 包内 sidecar 启动一次**，窗口出现、Host ready、数据库创建成功；记录 zip sha256。

## Acceptance Criteria

- [ ] **AC1 包结构完整**：包内至少含 `NewManga.App.exe`、`core-sidecar/`（5 个 exe + `_internal` + `models`）、
      `LICENSE`、`LICENSE-AGPL-3.0.txt`、`NOTICE.md`、`Run-NewManga.cmd`、`README.md`、`RELEASE-<head>.md`。
- [ ] **AC2 包内启动验证**：用**包内**路径启动（`--sidecar-dir=<包>/core-sidecar`，隔离 data/log/theme），
      进程存活、窗口标题为 `New Manga`、`host.log` 出现 `core_service ready` + `host_bridge ready` +
      `self-check status=Passed`、`library.db` 被创建。
- [ ] **AC3 zip 与指纹**：产出 zip，记录条目数、大小、sha256；抽样校验 zip 内含 `NewManga.App.exe`、
      `core-sidecar/core_service.exe`、`Run-NewManga.cmd`、`core-sidecar/models/`。
- [ ] **AC4 边界如实**：明确本包是 **portable 文件夹**，**不是安装器**；clean install / 升级回退 / 卸载 /
      签名仍未做；E-7 并发项仍开放 ⇒ **不改变 Gate 条件 4 的最终判定**。
- [ ] **AC5 不回归**：`check.ps1` PASS；`verify_pins.ps1` 18/18；`api_inventory` 1/80/6=87。
- [ ] **AC6 独立复核**：固定 head 交独立上下文 Review。

## 允许修改范围

见 frontmatter `allowed_paths`。要点：**只新增证据与文档**；包体在 `G:\CODEX\New Manga.workspace\artifacts\release\`（仓外，不入 Git）。

## 禁止范围

- 不得把 portable 包说成「安装器」或「可发布版本」；
- 不得声称已完成 clean install / 升级 / 卸载矩阵；
- 不得修改产品代码；
- 不得把 zip 提交进仓库（887 MB / 694 MB）。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 包内启动 | 启动 `<包>/NewManga.App.exe --sidecar-dir=<包>/core-sidecar --data-root …` | 窗口 "New Manga"、host.log 有 ready、library.db 创建 |
| zip 校验 | 抽样读 zip 条目 | 含 exe / core_service.exe / Run 脚本 / models |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## 证据

包清单、启动日志（host.log / startup.log / ndjson）、zip 指纹写入 `verification/RELEASE-PACKAGE-BUNDLE-1/`。
