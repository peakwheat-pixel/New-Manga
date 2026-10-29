---
id: UPGRADE-REHEARSAL-1
title: 真实旧版用户数据升级演练（旧 Tauri 数据根 → 新壳，dry-run 已有、真实数据未跑）
kind: verification
governance_version: 3
status: blocked
approval: user_authorized_2026-10-29_abc_sequence
suggested_owner: region-workbench-owner
owner: null
reviewer: dsh
depends_on: [RELEASE-VERIFY-1, NSIS-INSTALLER-1]
base_commit: 145bccb29
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/UPGRADE-REHEARSAL-1
allowed_paths:
  - doc/tasks/UPGRADE-REHEARSAL-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/scripts/migrate-legacy-dryrun.ps1
  - apps/desktop-avalonia/docs/UPGRADE.md
  - verification/UPGRADE-REHEARSAL-1/**
  - G:/CODEX/New Manga.workspace/task-envs/UPGRADE-REHEARSAL-1/**
---

# UPGRADE-REHEARSAL-1：真实旧版数据升级演练

## 来源与目标

- 来源：用户 2026-10-29 授权按 A/B/C 顺序推进；本卡 = B（AD002-FOLLOWUPS-1 #13「真实用户数据升级演练（旧 Tauri 版 → 新壳，dry-run 已有，真实数据未跑）」）。
- 现状：`apps/desktop-avalonia/scripts/migrate-legacy-dryrun.ps1` 已实现 copy-only dry-run（不写盘、不删除、幂等）；`apps/desktop-avalonia/docs/UPGRADE.md` 已记录覆盖安装与数据根保留约定；`src/infrastructure/sqlite/migrator.py` 具备 schema 迁移能力。**但从未用真实旧版（v1 Tauri）数据跑过。**

## 阻塞点（BLOCKED）

**需要用户提供的输入**：一份**旧壳（v1 Tauri 版）真实数据根副本**（通常位于 `%APPDATA%\com.newmanga.desktop`，含 `library.db`、托管副本目录等），复制到本机任意路径（**不要直接给正在使用的数据根**，先复制一份）。

- 若本机曾安装旧版：告知旧数据根路径（可含隐私数据——只需路径，证据中只记录结构/哈希与统计，不复制内容进仓库）。
- 若从未安装旧版：明确回复"无旧数据"，本卡改为「用合成旧 schema 数据演练」并把范围降级为合成数据演练（需另写生成脚本）。

## 演练方案（数据到位后执行）

1. **冻结副本**：把旧数据根整体复制到 `task-env/UPGRADE-REHEARSAL-1/legacy-data/`，记录文件清单 + 每文件 SHA-256 + `library.db` 的表/行数快照（只读）。
2. **dry-run 复核**：`migrate-legacy-dryrun.ps1 -LegacyRoot <副本> -TargetRoot <新副本>` → 校验输出 JSON（copy-only、writes_performed=0、文件数/字节一致）。
3. **真实迁移演练**：对副本执行迁移（`src/infrastructure/sqlite/migrator.py` 的升级路径或 `migrate-legacy-dryrun.ps1` 的正式模式，按其当前实现）→ 新壳用隔离数据根启动（`--data-root=<新副本>`）→ Host 就绪 + 书架可见。
4. **数据完整性断言**：书/章/页计数不变；region 标注、Lock、current/pinned revision 保留；托管副本与源文件未被改写（源目录哈希不变）；`library.db` schema 版本前进且无数据丢失。
5. **回滚路径**：演练前保留副本 → 失败可原样恢复；记录回滚命令。
6. **证据**：`verification/UPGRADE-REHEARSAL-1/{report.md, legacy-snapshot.json, dryrun.json, migrate-run.json, integrity.json, screenshots/}`，64-hex pin。

## Acceptance Criteria

- [ ] **AC1 旧数据副本与快照**：旧数据根副本、文件清单/哈希、库表行数快照（不泄露内容）。<<BLOCKED: 需用户提供真实旧数据根副本>>
- [ ] **AC2 dry-run 复核**：copy-only、0 写入、文件/字节一致。
- [ ] **AC3 真实迁移**：新壳隔离启动成功（Host ready + 书架页面可见），数据计数与关键状态保留。
- [ ] **AC4 回滚与证据**：回滚命令可执行并记录；报告/JSON/截图 pin。
- [ ] **AC5 门禁**：`check.ps1` PASS；不修改产品代码（仅脚本/文档如必要，需按 allowed_paths）。

## 允许修改范围

本卡、STATUS/PLAN/LEDGER、`verification/UPGRADE-REHEARSAL-1/**`、`task-env/UPGRADE-REHEARSAL-1/**`；如需修 dry-run 脚本或 UPGRADE.md，先在卡内登记（当前范围允许）。

## 风险与阻塞

- 阻塞：真实旧数据根副本（见上）。
- 风险：旧 schema 可能比当前迁移器支持的更旧（需先核对 `library.db` 的 `PRAGMA user_version`）；隐私——证据只记录结构/统计，不复制数据内容进仓库。

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
| task-env | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-REHEARSAL-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-REHEARSAL-1 | 待数据到位时登记 | 旧数据副本与演练工作区 |

## Closeout Record

- Closeout date / DSH：待解除阻塞后填写。
