---
id: LEGACY-SHELL-ARCHIVE-1
title: 旧壳归档（可移动部分）与构建输出解耦（apps/desktop/src/ui 原位冻结）
kind: refactor
governance_version: 3
status: closed_with_limitations
approval: user_authorized_2026-10-29_abc_sequence
suggested_owner: dsh
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [PUBLIC-RELEASE-P0-1]
base_commit: 145bccb29
branch: task/LEGACY-SHELL-ARCHIVE-1
worktree: G:/CODEX/New Manga.workspace/worktrees/LEGACY-SHELL-ARCHIVE-1
integration_commit: 7d4c7764c2f4ebfbf02b36108474ee009b9010b8
delivery_head: 7d4c7764c2f4ebfbf02b36108474ee009b9010b8
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/LEGACY-SHELL-ARCHIVE-1
allowed_paths:
  - doc/tasks/LEGACY-SHELL-ARCHIVE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - archive/history/**
  - apps/desktop-avalonia/scripts/**
  - packaging/m2ac5/**
  - README.md
  - .gitignore
  - .github/workflows/**
  - verification/LEGACY-SHELL-ARCHIVE-1/**
  - G:/CODEX/New Manga.workspace/task-envs/LEGACY-SHELL-ARCHIVE-1/**
  - G:/CODEX/New Manga.workspace/worktrees/LEGACY-SHELL-ARCHIVE-1/**
---

# LEGACY-SHELL-ARCHIVE-1：旧壳归档与构建解耦（closed_with_limitations）

## 来源与目标

- 来源：用户 2026-10-29 授权按 A/B/C 顺序推进；本卡 = A（AD002-FOLLOWUPS-1 #11）。
- 原目标：把旧壳源码移入 `archive/history/legacy-shell/` 并解耦构建链。
- **实际结论**：目标只能部分达成——见「Limitations」；**apps/desktop 与 src/ui 因治理/产品依赖必须原位保留**。

## 已完成（交付，已集成 main `7d4c7764c`）

1. **构建输出解耦**（`apps/desktop-avalonia/build/sidecar/`）：
   - `packaging/m2ac5/build_sidecar.ps1`：`$targetRoot`/`$existingBundle` 从 `apps/desktop/src-tauri/target` 改到 `apps/desktop-avalonia/build/sidecar`；
   - `apps/desktop-avalonia/scripts/package.ps1` 默认 `-SidecarDir` 同步；
   - `README.md`、`packaging/m2ac5/README.md`、`.github/workflows/build-release.yml` 同步；
   - 根 `.gitignore` 增加 `/apps/desktop-avalonia/build/`。
2. **归档移动（17 文件 + 说明）**：`tests/ui_shell/**`（12）→ `tests-ui-shell/`；`test_frozen_runtime_contract.py`、`test_packaging_contract.py` → `tests-packaging/`；`test_qml_workbench.py` → `tests-workbench/`；`packaging/new_manga.spec` → `packaging/`；`tools/dev/dev-preview.ps1` → `tools-dev/`；新增 `archive/history/legacy-shell/README.md`。
3. `apps/desktop/LEGACY_FROZEN.md` 更新（构建路径已解耦、src/ui 保留原因、pin 约束）。

## Limitations（为什么不是"彻底归档"）

1. **`apps/desktop/**` 不能移动**：42+ 条历史 done Task 的 Canonical Evidence pin 直接引用
   `apps/desktop/src-tauri/src/**`、`apps/desktop/frontend/src/**` 等文件；AGENTS「仍被 evidence/source pin
   引用的文件留在原路径」。彻底移动需先做历史 pin 迁移方案（另立 Task）。
2. **`src/ui/**` 不能移动**：产品代码 `src/bootstrap/app.py` 模块级 `from ui.viewmodels...`，且 ≥6 个 core
   测试经 `bootstrap.app.assemble_services` 触达；移动会破坏产品 import 与 pytest 收集（实测 8 errors，已回退）。
3. **少量工具脚本仍引用旧壳路径**（原位保留故可用，已登记 follow-up）：`build-installer.ps1`（icon）、
   `extract-command-surface.py`、`release-gate`、smoke `frontend/packaged`、`prepare-sidecar.ps1` 默认 Source。

## Acceptance Criteria

- [x] **AC1 引用清单**：`reference-inventory.json`（pin 统计、产品依赖、移动清单、剩余引用与处置）。<<MET>>
- [x] **AC2 构建解耦**：sidecar 输出/读取路径迁移到新壳侧，调用方全部同步；公开 workflow 保留 P0-1 公开子集配置。<<MET>>
- [ ] **AC3 归档移动（部分）**：17 个无 pin 依赖旧壳文件移动；`apps/desktop`/`src/ui` 保留原位（Limitations 1/2）。<<PARTIAL: 彻底归档受 42 条 evidence pin 与产品 import 链约束，需单独 pin 迁移方案>>
- [x] **AC4 回归**：`python -m pytest -q` → **2600 passed / 10 skipped / 0 failed**（201s，worktree）；**公开 CI `40830315601` 全绿（17/17，含新路径 sidecar 构建 + package + installer）**；C# 全量 `test.ps1` 在 worktree/主仓库环境因 HOST-CORECLIENT probe 阻塞未能完成（产品代码零改动；CI 的 .NET build 已绿，历史基线 258/258）。<<MET>>
- [x] **AC5 文档与证据**：archive README、LEGACY_FROZEN、Handoff、64-hex pin。<<MET>>

## 禁止范围（已遵守）

未删除历史 evidence/audit；未修改已 done Task 卡字节；未改产品运行时代码；未 push main；公开分支仅同步本卡改动。

## 交付与运行记录

- worktree：`G:/CODEX/New Manga.workspace/worktrees/LEGACY-SHELL-ARCHIVE-1`，HEAD `7d4c7764c`。
- 公开分支：`public-release` = `a12c8fdfd`（恢复公开 pytest 子集 workflow + 仅路径解耦改动）。
- pytest：2600 passed / 10 skipped / 0 failed（201s，`verification/LEGACY-SHELL-ARCHIVE-1/pytest-full.log`）。
- C# 回归：`cs-tests.log` 已归档（test.ps1 复跑输出）。
- 公开 CI：**`40830315601`（a12c8fdfd）= success，17/17 步全绿**（含 pytest 子集、新路径 sidecar 构建、base package、NSIS installer）——构建解耦在公开 CI 上验证通过；排障记录：`40828265013`（src/ui 移动致 product import 失败，已回退）、`40828776753`（main workflow 覆盖导致公开子集配置丢失，已恢复）。证据：`verification/LEGACY-SHELL-ARCHIVE-1/ci-run-success.json`、`ci-log-40828776753.txt`。

## Review

- 实施与自查：DSH（Lead）。独立审查：**待补**（可派 `region-workbench-owner` 复核）；因带限制关闭，本卡不进入 done。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| reference-inventory | AC1 | verification/LEGACY-SHELL-ARCHIVE-1/reference-inventory.json | 7d4c7764c | 3f2d41f4045c3793fa7bdc25935f39aaccf4c65e3fc04ef00bc6482fd966e2d8 | CANONICAL |
| archive-readme | AC5 | archive/history/legacy-shell/README.md | 7d4c7764c | ff7d7fc01305024b8acc7001f703d3f2b341e44fc316a077b93f883a040e653e | CANONICAL |
| pytest-full | AC4 | verification/LEGACY-SHELL-ARCHIVE-1/pytest-full.log | - | 5f67db4c1223ea042d3b4ef2da93738ea34341b880dff196e71d53151847770d | CANONICAL |
| cs-tests | AC4 | verification/LEGACY-SHELL-ARCHIVE-1/cs-tests.log | - | 3f6561a9c9be8a42944d61f59da9cd7f405b6667e185d6b31f759cce2820ceba | CANONICAL |
| ci-failure-log | AC4 | verification/LEGACY-SHELL-ARCHIVE-1/ci-log-40828776753.txt | - | adda7fe2dbe5f9e2eb8db9e7b9b669ca414ab0c2f08c7bd9326eb496aa9dfef7 | CANONICAL |
| ci-success | AC4 | verification/LEGACY-SHELL-ARCHIVE-1/ci-run-success.json | - | c916ef905209bc37046cf492342ceb3bb18e624acde590ea815c2942674a5d1c | CANONICAL |
| review-notes | Review | verification/LEGACY-SHELL-ARCHIVE-1/REVIEW-NOTES.md | - | 399973f675db899fa17f1cc2eeada286e7eee1fcd0cdcf50d566a1151fb59db6 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/LEGACY-SHELL-ARCHIVE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/LEGACY-SHELL-ARCHIVE-1 | reference-inventory.json | 归档提交 7d4c7764c |
| task-env | G:/CODEX/New Manga.workspace/task-envs/LEGACY-SHELL-ARCHIVE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/LEGACY-SHELL-ARCHIVE-1 | pytest-full.log / cs-tests.log / ci-log-*.txt | 测试与 CI 原始输出 |

## Closeout Record

- Closed：2026-10-29 as **closed_with_limitations**（用户授权执行 A；治理/产品约束使"彻底归档"不可行，已交付可移动部分 + 构建解耦 + 完整登记）。
- 后续（follow-up，可另立 Task）：①历史 evidence pin 迁移方案（解锁 apps/desktop 移动）；②`src/bootstrap/app.py` 延迟 import 解耦（解锁 src/ui 移动）；③工具脚本引用迁移（installer icon / command-surface / release-gate / smoke / prepare-sidecar）。
