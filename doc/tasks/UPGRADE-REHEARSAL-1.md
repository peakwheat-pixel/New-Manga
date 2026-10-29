---
id: UPGRADE-REHEARSAL-1
title: 真实用户数据升级演练（旧布局 → 新壳；含 GUI 端到端）
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
  - G:/CODEX/New Manga.workspace/task-envs/UPGRADE-REHEARSAL-GUI-1/**
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
4. **确认升级缺口**：`src/bootstrap/core_service.py:666` 固定读取 `data_root / "library.db"`（根），**不识别旧布局 `data/library.db`**（`git grep` 0 命中）→ 已由 [UPGRADE-LEGACY-LAYOUT-1](UPGRADE-LEGACY-LAYOUT-1.md)（done）修复。
5. **GUI 端到端升级演练（2026-10-29，`UPGRADE-REHEARSAL-GUI-1`）**：
   - 用含修复的 sidecar（自建 PyInstaller 6.22.3，HEAD `474d57b02`）组装 App，以 `--data-root=<隔离旧布局根>` 启动真实 Avalonia App；
   - Core 日志：`[core.upgrade] migrated legacy data layout: library.db`；根 `library.db` 生成、旧 `data/` 保留（`gui-upgrade-migration.log`）；
   - Host 日志：`data_root=<隔离根>`、`core_service ready (1 wire frames)`、`host_bridge ready`（`gui-upgrade-host.log`）；
   - **GUI 书架显示迁移后的 1 本书（"家族战记"，"已加载 1 本（经 command dispatcher）"）**（`screenshots/gui-bookshelf-after-upgrade.png`）；
   - 完整性：根库 SHA 与旧库一致（`96fc4120…`）、books=1、`integrity_check=ok`（`gui-upgrade-verify.json`）。

## Limitations

1. **无 AD-001 旧 schema 原始数据**：本机旧 Tauri 数据已被新壳数据根覆盖；备份库 schema 已是 v6（无需 schema 迁移）。真实"旧 schema → 新 schema"路径未用真实数据验证（migrator v1–v6 链存在，可用合成数据补充）。
2. **GUI 演练的副本路径限制**：为不改真实 `%APPDATA%`，数据根为副本 → 备份里的 `catalog.sqlite` 命名空间绑定/derived 锁绑定的是原始绝对路径，副本中需删除（重建 catalog、重算预览）才能启动。真实升级根路径不变，无此问题。首次 Core 启动因此失败过一次（`namespace binding identity mismatch`），删除副本 catalog 后成功。
3. **GUI 演练使用 `-SkipWeights` 构建的 sidecar**：检测/OCR 权重缺失仅影响"运行翻译"，不影响书架读取；日志有两条预期 WARNING。
4. App 参数格式：`--data-root=<path>`（等号形式）；`--data-root <path>` 会被解析成 `true`（AppOptions 只解析 `--key=value`）——已记录为使用注意。

## Acceptance Criteria

- [ ] **AC1 旧数据副本与快照**：用 2026-10-26 升级前备份（旧布局）替代；本机无 AD-001 原始数据。<<PARTIAL: 本机无旧 Tauri 原始数据；以首次安装前备份替代并快照化>>
- [x] **AC2 dry-run 复核**：copy-only、0 写入、4 文件/368956 B、目标未创建。<<MET>>
- [x] **AC3 真实迁移 + GUI 端到端**：旧布局→新布局文件迁移 + 库完整性 PASS；**真实 App 启动后迁移生效、书架显示 1 本书、Host/Core 就绪**。<<MET>>
- [x] **AC4 回滚与证据**：源副本未修改（SHA 一致）；回滚=丢弃 rehearsal-root；快照/dry-run/校验 JSON/截图落盘。<<MET>>
- [x] **AC5 门禁**：check PASS；未改产品代码。<<MET>>

## 已发现缺口（后续）

- ~~安装器/首启迁移旧布局~~ → 已由 [UPGRADE-LEGACY-LAYOUT-1](UPGRADE-LEGACY-LAYOUT-1.md)（done，3 轮 Review PASS）修复。
- 合成旧 schema（v1–v5）数据 + migrator 迁移测试（真实旧 schema 数据不可得）。
- 真实用户（非副本）升级演练：需在真实 `%APPDATA%` 环境用真实旧版本升级（本机不适用）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| legacy-snapshot | AC1 | verification/UPGRADE-REHEARSAL-1/legacy-snapshot.json | - | ac65f81c289eb69b1aa419c3c9fb3f811c0f4dd2aa24a00a9e84af1f032aec55 | CANONICAL |
| dryrun | AC2 | verification/UPGRADE-REHEARSAL-1/dryrun.json | - | fcb56bd61760fac48053e21027a9ba4d6630613402ac73062dabca9df841cc48 | CANONICAL |
| verify-migration | AC3 | verification/UPGRADE-REHEARSAL-1/verify-migration.json | - | 2c6af04570d417bfadc272fc8cc8446e200b42723282a2e725f0bf88e26a4dae | CANONICAL |
| gui-upgrade-verify | AC3 | verification/UPGRADE-REHEARSAL-1/gui-upgrade-verify.json | - | a2f827825356b0125eb0019e2416883923fb8f5b0fee6714a9d85db02eca7e7b | CANONICAL |
| gui-upgrade-migration-log | AC3 | verification/UPGRADE-REHEARSAL-1/gui-upgrade-migration.log | - | 76522edcfb6fcf05ae3c27e310ed5aa9739794b1c99bee1894d9fbd10883617c | CANONICAL |
| gui-upgrade-host-log | AC3 | verification/UPGRADE-REHEARSAL-1/gui-upgrade-host.log | - | 54951882ab2175d60a260c9871be16a8aec49e7deae2821bbe2bde63dfa84b06 | CANONICAL |
| gui-bookshelf-screenshot | AC3 | verification/UPGRADE-REHEARSAL-1/screenshots/gui-bookshelf-after-upgrade.png | - | c7d8e676b4c75d6c8848e4eda2356009834af614c94e291d94dfbe6a9cd64b7e | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-REHEARSAL-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-REHEARSAL-1 | legacy-snapshot.json / backup-layout / rehearsal-root | 演练副本与输出 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-REHEARSAL-GUI-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-REHEARSAL-GUI-1 | app / legacy-root2 / logs / screenshot | GUI 端到端演练工作区 |

## Closeout Record

- Closed：2026-10-29 as **closed_with_limitations**（用户"不知道旧数据在哪"；本机探测后以升级前真实备份替代 AD-001 原始数据；完成 dry-run + 真实布局迁移 + **GUI 端到端**（书架显示迁移数据）；升级缺口已由 UPGRADE-LEGACY-LAYOUT-1 修复）。
- 剩余限制：本机无 AD-001 原始数据；副本路径需清理 catalog 绑定（真实升级无此问题）；真实用户升级演练未做。
- 后续：合成旧 schema 迁移测试；真实用户升级演练（如有真实旧用户机器）。
