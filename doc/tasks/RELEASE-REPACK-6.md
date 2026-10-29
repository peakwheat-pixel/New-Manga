---
id: RELEASE-REPACK-6
title: 重建发布包 0.1.1（含旧布局迁移修复 sidecar + NSIS 安装包）
kind: release
governance_version: 3
status: done
approval: user_authorized_2026-10-29_repack_011
suggested_owner: dsh
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [REAL-USER-UPGRADE-1, UPGRADE-LEGACY-LAYOUT-1, NSIS-INSTALLER-1, AGPL-RELEASE-1]
base_commit: 6862a4f95
branch: task/RELEASE-REPACK-6
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-6
integration_commit: 93cfb1bce516b68a06b5a41951470bfe44910155
delivery_head: 93cfb1bce516b68a06b5a41951470bfe44910155
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/RELEASE-REPACK-6
allowed_paths:
  - doc/tasks/RELEASE-REPACK-6.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj
  - verification/RELEASE-REPACK-6/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-6/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-6/**
---

# RELEASE-REPACK-6：重建发布包 0.1.1（done）

## 来源

`REAL-USER-UPGRADE-1` 发现：官方 0.1.0 安装包 sidecar `bde2d866…`（旧 HEAD `7f0d1daef`）不含旧布局迁移修复。
用户 2026-10-29 指定重建 0.1.1。

## 交付（集成 main `93cfb1bce`）

| 构件 | 结果 |
|---|---|
| App 版本 | `NewManga.App.csproj` **0.1.1**（commit `78f82d3c4`） |
| sidecar | 重建（HEAD `78f82d3c4`，PyInstaller 6.22.3，含权重）；`core_service.exe` **SHA `8889944d…`** ≠ 旧 `bde2d866…` |
| base 包 | `NewManga-0.1.1-win-x64.zip` **98.7 MB**（stage 215.6 MB / 1970 文件） |
| models 包 | `NewManga-0.1.1-win-x64-models.zip` **691.9 MB**（含 detector/ocr/sfx 权重） |
| NSIS 安装包 | `NewManga-0.1.1-setup.exe` **65.45 MB**，SHA-256 `5b5931b9…`，未签名（SignPath 审核中） |
| VERSION.json | version 0.1.1；sidecar_build.core_service_sha256=8889944d…；repo_head=78f82d3c4 |

## 验收

- **安装**：静默安装到隔离目录成功；包内 sidecar SHA = 新构建；注册表 DisplayVersion=0.1.1。
- **卸载**：静默卸载成功；安装目录/注册表清理；**真实数据根 `%APPDATA%\com.newmanga.desktop` 未被触碰**。
- **场景 A（真实数据副本）**：0.1.1 安装产物启动 → `core_service ready` + `host_bridge ready`；`library.db` SHA `df9d424c…` 与真实库**字节级一致**；3 个备份保留。
- **场景 B（真实旧布局备份，1 本书）**：迁移日志 `[upgrade-legacy] migrated from data/: library.db`；根库生成、旧库 SHA 不变；**GUI 书架显示 1 本（家族战记）**、Host 就绪；integrity ok、schema v6。

## 发布构件（GitHub Release）

- **https://github.com/peakwheat-pixel/New-Manga/releases/tag/v0.1.1**（id 427755017，published）
- 资产：`NewManga-0.1.1-setup.exe`（68,629,676 B，digest `sha256:5b5931b9…`，与本地一致）+ `SHA256SUMS.txt`（287 B）。
- 未 push 产品 main（用户约束）；Release target = `public-release` HEAD `a12c8fdfd`（tag v0.1.1）。

## Acceptance Criteria

- [x] **AC1 版本**：App `<Version>`=0.1.1；VERSION.json/installer/安装包一致。<<MET>>
- [x] **AC2 sidecar 修复**：新 sidecar `8889944d…` ≠ `bde2d866…`；VERSION.json 记录 HEAD/时间。<<MET>>
- [x] **AC3 包构建**：base/models stage+ZIP、预算内、许可证文件齐全（AGPL 声明同 0.1.0）。<<MET>>
- [x] **AC4 NSIS 安装包**：0.1.1 setup 生成；静默安装/卸载成功、数据根保留、注册表清理。<<MET>>
- [x] **AC5 真实升级验收**：A 数据字节一致；B 迁移 + 书架 1 本。<<MET>>
- [x] **AC6 发布构件**：GitHub Release v0.1.1 已发布（setup.exe + SHA256SUMS；digest 校验一致）。<<MET>>
- [x] **AC7 证据**：构建日志/SHA256/install-smoke/升级验收/截图；check PASS。<<MET>>

## 禁止范围（已遵守）

未 push 产品 main；未使用 `git add -A`；未改 Core 语义；未处理签名（SignPath 审核中）。

## 交付与运行记录

- worktree：`G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-6`，HEAD `93cfb1bce`（含版本 bump `78f82d3c4` + 证据 commit）。
- 构件：`G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-6/{out,installer}`（保留）。
- 验收数据：`u-data`（真实数据副本）、`legacy-data`（真实旧布局备份迁移后）保留；安装目录已卸载清理。

## Review

- 验证型发布任务（无产品语义改动，仅版本号 bump + 构建）；由 DSH 执行并自检；发布资产 digest 与本地 SHA 一致。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| verify-json | AC1–AC6 | verification/RELEASE-REPACK-6/verify.json | 93cfb1bce | 39b0c6a11ac747e12fc35e7074c89d000f6f0cb6d1a1b03d92e89da2c6b5d3e5 | CANONICAL |
| SHA256SUMS | AC6 | verification/RELEASE-REPACK-6/SHA256SUMS.txt | 93cfb1bce | 67704527380c1c376040a5afecc4ac1e6d14f3ac7d760e812bf828e70ef884c2 | CANONICAL |
| installer-build-info | AC4 | verification/RELEASE-REPACK-6/installer-build-info.json | 93cfb1bce | 2c7e4bfcca2d75e5b985c0ce0c828b81c2d2aa204f9203b3f5c0c12fe1b7b3e6 | CANONICAL |
| sidecar-build-log | AC2 | verification/RELEASE-REPACK-6/sidecar-build.log | 93cfb1bce | 18836a3c2920499c2dcf7a38a7b6511beee195edbed9732396ffea80b346b906 | CANONICAL |
| verify-A-host-log | AC5 | verification/RELEASE-REPACK-6/verify-A-host.log | 93cfb1bce | 6557a052eb219dce25ca36f83572eb6b66bf270fa7b808e2890cda7bfae32b8b | CANONICAL |
| verify-B-host-log | AC5 | verification/RELEASE-REPACK-6/verify-B-host.log | 93cfb1bce | cb6aee601c993365189ba4fa72ac865e690ee46b4e21151a5f0d223aadfdbb0d | CANONICAL |
| verify-B-migration-log | AC5 | verification/RELEASE-REPACK-6/verify-B-migration.log | 93cfb1bce | 76522edcfb6fcf05ae3c27e310ed5aa9739794b1c99bee1894d9fbd10883617c | CANONICAL |
| legacy-upgrade-screenshot | AC5 | verification/RELEASE-REPACK-6/screenshots/legacy-upgrade-011-shelf.png | 93cfb1bce | ccfe7c4b0dcb67c640a1f3e648855d8001d8547304b6891cf91971660805eced | CANONICAL |
| package-summary-base | AC3 | verification/RELEASE-REPACK-6/package-summary-base.json | 93cfb1bce | 8ac6404cf0dbe7c6a429ec378dad5a14fd42f256dfca6dd69f615b7a5693944f | CANONICAL |
| package-summary-models | AC3 | verification/RELEASE-REPACK-6/package-summary-models.json | 93cfb1bce | cf1629be5b98f6e8137c8b3fcf42b1f8f218803f762c04fbaf79910e5a121283 | CANONICAL |

## Closeout Record

- Closed：2026-10-29 as **done**（0.1.1 构建 + 安装包 + 真实升级验收 + GitHub Release v0.1.1 发布；官方 0.1.0 的升级缺口已在新构件修复）。
- 遗留：SignPath 签名（审计中，获批后对 0.1.1 重新签名并替换资产）；public-release 分支尚未含 0.1.1 版本号改动（仅 tag）。
