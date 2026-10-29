---
id: UPGRADE-REHEARSAL-1
title: 真实用户数据升级演练（旧布局 → 新壳；已用 2026-10-26 升级前备份执行）
kind: verification
governance_version: 3
status: closed_with_limitations
approval: user_authorized_2026-10-29_abc_sequence
suggested_owner: dsh
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [RELEASE-VERIFY-1, NSIS-INSTALLER-1]
base_commit: 2ac44ff3e
branch: null
worktree: null
integration_commit: 2ac44ff3e
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/UPGRADE-REHEARSAL-1
allowed_paths:
  - doc/tasks/UPGRADE-REHEARSAL-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/UPGRADE-REHEARSAL-1/**
  - G:/CODEX/New Manga.workspace/task-envs/UPGRADE-REHEARSAL-1/**
---

# UPGRADE-REHEARSAL-1：真实用户数据升级演练（closed_with_limitations）

## 背景与数据来源（用户"不知道旧数据在哪"→ 本机探测结果）

| 位置 | 结论 |
|---|---|
| `%APPDATA%\com.newmanga.desktop` | 当前数据根（已被新壳接管；含 `backups/first-run-*.zip` 2026-10-26 升级前备份） |
| `%APPDATA%\com.newmanga.m2rc1.desktop` | M2-RC1 时期数据（新架构 27 表 schema，非 AD-001 旧 Tauri 原始数据） |
| `%LOCALAPPDATA%\com.newmanga.desktop\EBWebView` | 旧 Tauri（WebView2）缓存痕迹 |
| 旧壳 identifier | `com.newmanga.desktop`（与新版相同 → 旧数据被新壳数据根覆盖） |

**本机没有 AD-001 旧 Tauri 时期的原始 schema 数据**。采用最接近的真实数据：
`backups/first-run-20261026190335.zip`（新壳首次安装时的**升级前布局**：`data/library.db` + `catalog/catalog.sqlite` + `derived/`）。

## 执行结果

1. **快照**（`legacy-snapshot.json`）：备份布局 4 文件 / 368,956 B，逐文件 SHA-256。
2. **dry-run**（`dryrun.json`）：`migrate-legacy-dryrun.ps1` → copy-only、`writes_performed=0`、4 文件/368956 B、目标目录未创建。**PASS**
3. **真实迁移演练**：旧布局 `data/library.db` → 新布局根 `library.db`（+ catalog/derived），校验（`verify-migration.json`）：
   - 源/目标 SHA-256 一致（`96fc4120…`）、源文件未被修改
   - `PRAGMA integrity_check = ok`、`schema_version=6`、books=1 / chapters=0 / pages=0 / regions=0
4. **确认升级缺口**：`src/bootstrap/core_service.py:666` 固定读取 `data_root / "library.db"`（根），**不识别旧布局 `data/library.db`**（`git grep` 0 命中）。即：新壳不会自动迁移旧布局数据，升级需要安装器/迁移脚本显式处理（B 的关键发现）。

## Limitations

1. **无 AD-001 旧 schema 原始数据**：本机旧 Tauri 数据已被新壳数据根覆盖；备份库 schema 已是 v6（无需 schema 迁移）。真实"旧 schema → 新 schema"路径未用真实数据验证（migrator v1–v6 链存在，可用合成数据补充）。
2. **未做 GUI/Core 端到端启动**：演练验证了文件布局迁移 + 库完整性，未启动新壳 GUI 读取迁移后数据根（隔离 `NEWMANGA_DATA_ROOT` 启动属 GUI 环境）。
3. **升级缺口需修复**（follow-up）：安装器/首启应检测 `data/library.db` 旧布局并迁移/提示，否则旧用户升级后看不到旧书架。

## Acceptance Criteria

- [ ] **AC1 旧数据副本与快照**：用 2026-10-26 升级前备份（旧布局）替代；本机无 AD-001 原始数据。<<PARTIAL: 本机无旧 Tauri 原始数据；以首次安装前备份替代并快照化>>
- [x] **AC2 dry-run 复核**：copy-only、0 写入、4 文件/368956 B、目标未创建。<<MET>>
- [ ] **AC3 真实迁移**：旧布局→新布局文件迁移 + 库完整性 PASS；未跑 GUI 端到端。<<PARTIAL: 未验证新壳 GUI 读取迁移后数据根与可见书架>>
- [x] **AC4 回滚与证据**：源副本未修改（SHA 一致）；回滚=丢弃 rehearsal-root；快照/dry-run/校验 JSON 落盘。<<MET>>
- [x] **AC5 门禁**：check PASS；未改产品代码。<<MET>>

## 已发现缺口（建议 follow-up Task）

- 安装器/首启迁移旧布局：`data/library.db` → 根 `library.db`（若根不存在）+ catalog/derived 保留；含备份与回滚。
- 合成旧 schema（v1–v5）数据 + migrator 迁移测试（真实旧 schema 数据不可得）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| legacy-snapshot | AC1 | verification/UPGRADE-REHEARSAL-1/legacy-snapshot.json | - | ac65f81c289eb69b1aa419c3c9fb3f811c0f4dd2aa24a00a9e84af1f032aec55 | CANONICAL |
| dryrun | AC2 | verification/UPGRADE-REHEARSAL-1/dryrun.json | - | fcb56bd61760fac48053e21027a9ba4d6630613402ac73062dabca9df841cc48 | CANONICAL |
| verify-migration | AC3 | verification/UPGRADE-REHEARSAL-1/verify-migration.json | - | 2c6af04570d417bfadc272fc8cc8446e200b42723282a2e725f0bf88e26a4dae | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-REHEARSAL-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-REHEARSAL-1 | legacy-snapshot.json / backup-layout / rehearsal-root | 演练副本与输出 |

## Closeout Record

- Closed：2026-10-29 as **closed_with_limitations**（用户"不知道旧数据在哪"；本机探测后以升级前真实备份替代 AD-001 原始数据；完成 dry-run + 真实布局迁移完整性 + 确认升级缺口）。
- 后续：①安装器/首启旧布局迁移实现（建议新 Task `UPGRADE-LEGACY-LAYOUT-1`）；②合成旧 schema 迁移测试；③GUI 端到端升级验证。
