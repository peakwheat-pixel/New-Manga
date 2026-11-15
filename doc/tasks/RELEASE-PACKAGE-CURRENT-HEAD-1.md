---
id: RELEASE-PACKAGE-CURRENT-HEAD-1
title: 在当前 HEAD 重新打包 Windows 单文件包并做真实窗口冒烟（替换不绑定基线的 0.1.1 旧证据）
kind: governance
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - RELEASE-GATE-DISPOSITION-1
  - SIDECAR-REBUILD-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 B「Gate 条件 4 的 Agent 可做部分」
base_commit: da7f88fb5
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/RELEASE-PACKAGE-CURRENT-HEAD-1
allowed_paths:
  - doc/tasks/RELEASE-PACKAGE-CURRENT-HEAD-1.md
  - doc/reviews/RELEASE-GATE-DISPOSITION-2026-11-15.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/RELEASE-PACKAGE-CURRENT-HEAD-1/**
---

# RELEASE-PACKAGE-CURRENT-HEAD-1：当前 HEAD 打包 + 真实窗口冒烟

## 来源

`RELEASE-GATE-DISPOSITION-1` 判定 Gate 条件 4 的「打包与冒烟」是 **Agent 可做**部分，
且 `MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md` §3 明记：

> `G:\CODEX\New Manga.workspace\artifacts\release\NewManga-0.1.1-win-x64\` 是 `0.1.1` 的旧产物，
> **不绑定当前基线**，不得当作当前 commit 的安装包证据。

本卡消除这一缺口：在**当前 HEAD** 重新产出单文件包，并跑真实窗口冒烟。

## 前置（已具备）

- `SIDECAR-REBUILD-1` 已用 PyInstaller 重建 sidecar，产物在
  `apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar/`（**792 MB / 1024 文件**，git-ignored）；
- 实测该 sidecar 可运行：`core.ping` 有响应、`schema v14 already current`。

## 目标（一个可观察结果）

产出**绑定当前 HEAD commit** 的 Windows 单文件包（含 sha256）与**真实窗口冒烟证据**
（窗口找到 + host ready + 自然退出 + 截图），并如实说明它**不等于**安装矩阵。

## Acceptance Criteria

- [ ] **AC1 打包成功且绑定基线**：`tools/ci/publish-release.ps1 -Mode singlefile -Smoke -SidecarDir <bundle>`
      退出 0；`manifest-singlefile.json` 的 `git_head` == 当前 HEAD 完整 sha。
- [ ] **AC2 真实窗口冒烟 PASS**：`smoke-singlefile.json` 中 `window_found=true`、`window_title="New Manga"`、
      `host_ready=true`、`exit_code=0`、`exit_kind="natural"`、`pass=true`；并留存截图。
- [ ] **AC3 产物指纹**：记录 exe 尺寸、sha256、`publish_exit_code`、耗时。
- [ ] **AC4 零产品代码改动 + 零工作区污染**：`git diff` 不触及 `src/**`、`apps/**`、`tools/**`；
      提交后工作区仅含本卡与证据目录。
- [ ] **AC5 边界如实说明**：明确本卡**只**替换「不绑定基线的旧包」缺口，
      **不等于** clean install / 升级回退 / 卸载矩阵；**不改变 Gate 条件 4 的判定**。
- [ ] **AC6 独立复核**：固定 head 交独立上下文 Review。

## 允许修改范围

见 frontmatter `allowed_paths`。要点：**只新增证据与文档，不改产品代码**。

## 禁止范围

- 不得声称「条件 4 已完成」或「Gate 可解锁」；
- 不得把单文件包的冒烟当作安装/卸载验证；
- 不得修改 `.csproj`/`.sln`/源码以让打包通过；
- 不得删除或改写 `0.1.1` 旧包（保留为历史证据）。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 打包 + 冒烟 | `pwsh -NoProfile -File tools/ci/publish-release.ps1 -Mode singlefile -Smoke -SidecarDir <bundle> -EvidenceDir verification/RELEASE-PACKAGE-CURRENT-HEAD-1` | EXIT 0，`publish: 1/1 PASS` |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## 证据

`manifest-singlefile.json`、`smoke-singlefile.json`、`manifest-summary.json`、`build-singlefile.log`、
`published-singlefile.png` 与 `publish-release.log` 写入 `verification/RELEASE-PACKAGE-CURRENT-HEAD-1/`。
