---
id: LEGACY-SHELL-ARCHIVE-1
title: 旧壳彻底归档（apps/desktop Tauri + src/ui PySide6 → archive，构建输出路径解耦）
kind: refactor
governance_version: 3
status: ready
approval: user_authorized_2026-10-29_abc_sequence
suggested_owner: region-workbench-owner
owner: null
reviewer: dsh
depends_on: [PUBLIC-RELEASE-P0-1]
base_commit: 145bccb29
branch: task/LEGACY-SHELL-ARCHIVE-1
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/LEGACY-SHELL-ARCHIVE-1
allowed_paths:
  - doc/tasks/LEGACY-SHELL-ARCHIVE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - archive/history/**
  - apps/desktop-avalonia/scripts/**
  - apps/desktop-avalonia/docs/**
  - packaging/m2ac5/build_sidecar.ps1
  - packaging/m2ac5/README.md
  - apps/desktop-avalonia/docs/UPGRADE.md
  - README.md
  - .github/workflows/**
  - tools/dev/dev-preview.ps1
  - verification/LEGACY-SHELL-ARCHIVE-1/**
  - G:/CODEX/New Manga.workspace/task-envs/LEGACY-SHELL-ARCHIVE-1/**
  - G:/CODEX/New Manga.workspace/worktrees/LEGACY-SHELL-ARCHIVE-1/**
---

# LEGACY-SHELL-ARCHIVE-1：旧壳彻底归档

## 来源与目标

- 来源：用户 2026-10-29 授权按 A/B/C 顺序推进；本卡 = A（AD002-FOLLOWUPS-1 #11「旧壳彻底归档（当前原位冻结；移动需授权 + 引用迁移清单）」）。
- 目标：把旧壳源码（`apps/desktop` Tauri/React/WebView2 + `src/ui` PySide6/QML）移入 `archive/history/legacy-shell/`，同时**解耦当前构建链**（sidecar 输出路径不再依赖旧壳目录）并迁移全部活跃引用；历史证据与 pin 保持原字节。

## 已完成的影响分析（DSH，2026-10-29）

1. **旧壳 tracked 规模**：`apps/desktop` 284 文件 / 3.2 MB；`src/ui` 47 文件 / 0.3 MB。
2. **关键耦合（必须先解耦才能移动）**：
   - `packaging/m2ac5/build_sidecar.ps1` 输出到 `apps/desktop/src-tauri/target/core-sidecar/…`；`apps/desktop-avalonia/scripts/package.ps1` 的 `-SidecarDir`、`README.md` 构建命令、`.github/workflows/build-release.yml`（公开树）都引用该路径 → **整体移动会破坏 sidecar 构建与公开 CI**。
   - `tools/dev/dev-preview.ps1` 是旧壳开发预览脚本（6 处引用）。
   - `packaging/m2ac5/README.md` 记录旧路径。
3. **测试耦合**：`tests/ui_shell/**`（PySide6 旧壳 UI 测试）依赖 `src/ui`；归档 `src/ui` 前必须把该测试目录一并归档/跳过，并复验 pytest 基线（当前 2773P/10S）。
4. **活跃引用误报**：`doc/tasks/*` 中 812 行 "apps/desktop" 绝大多数是 `apps/desktop-avalonia`（新壳），不是旧壳；精确清单以 `apps/desktop`（非 avalonia）为准。
5. **历史证据**：`verification/**`、`audit/**` 中大量历史记录引用旧壳路径——按治理保留原字节不动（历史事实不重写），在归档记录的「已失效引用清单」中登记即可。

## Acceptance Criteria

- [ ] **AC1 精确引用清单**：产出 `verification/LEGACY-SHELL-ARCHIVE-1/reference-inventory.json`：旧壳路径的活跃引用（doc 除历史证据/README/workflow/scripts/tests）逐条列出（file:line、类别、处置：迁移/归档/保留历史），并证明 `apps/desktop-avalonia` 不被误伤。
- [ ] **AC2 构建链解耦**：sidecar 输出/读取路径改为新壳侧（建议 `apps/desktop-avalonia/build/core-sidecar`，或参数化并更新全部调用方）；`build_sidecar.ps1`、`package.ps1` 调用方、`README.md`、`.github/workflows/build-release.yml`、`packaging/m2ac5/README.md` 同步。
- [ ] **AC3 归档移动**：`git mv` 移动 `apps/desktop`（保留 `src-tauri/target` 输出目录约定或改为新路径）与 `src/ui` → `archive/history/legacy-shell/{apps-desktop,src-ui}`；`tests/ui_shell` 同步归档或明确 skip 并更新 pytest 配置；移动提交保留历史。
- [ ] **AC4 回归与门禁**：`python -m pytest` 基线不新增失败（归档的旧壳测试从统计中移除并注明）；`apps/desktop-avalonia/scripts/test.ps1` 全绿；`package.ps1`+`build-installer.ps1` 在本地 stage 可产出安装包（或注明因环境限制由公开 CI 验证）；`check.ps1` PASS；公开 `public-release` 分支同步后 dispatch 一次 CI 并全绿（若改了 workflow/README 的 SidecarDir）。
- [ ] **AC5 文档与证据**：`archive/history/legacy-shell/README.md`（来源/原路径/指纹/引用迁移/失效历史引用清单）；AGENTS/UPGRADE/README 中旧壳表述更新；Handoff；64-hex pin。

## 禁止范围

不删除历史 evidence/audit；不修改已 done Task 卡字节（仅可追加备注）；不改产品运行时代码（Core/App）；不 push main；公开分支推送仅限同步本次归档改动（需用户可见记录）。

## 依赖、风险与阻塞

- 硬依赖：`PUBLIC-RELEASE-P0-1`（公开分支与 CI 基线，done）。
- 风险：①构建输出路径是当前发布链的一部分——解耦不彻底会导致公开 CI 失败；②`tests/ui_shell` 归档会改变 pytest 基线数字，需要在证据中说明（从 2773 变为 2773−旧壳测试数）；③历史证据引用会"失效"但必须保留原字节（治理允许，需登记）；④公开分支需再跑一轮 CI（约 15 分钟）。
- 阻塞：无（分析已完成，待实施）。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/LEGACY-SHELL-ARCHIVE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/LEGACY-SHELL-ARCHIVE-1 | verification/LEGACY-SHELL-ARCHIVE-1/reference-inventory.json | 待实施时创建 |

## Closeout Record

- Closeout date / DSH：待实施后填写。
