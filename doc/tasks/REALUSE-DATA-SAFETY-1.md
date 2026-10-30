---
id: REALUSE-DATA-SAFETY-1
title: 修复真实使用自查 P1 数据安全缺陷——命名空间迁移自愈、真实备份、迁移顺序与只读语义
kind: fix
governance_version: 3
status: in_progress
approval: user_authorized_2026-10-30_self_audit_repair
suggested_owner: dsh
owner: dsh-lead
reviewer: antigravity-headless-r1
review_history:
  - round: 1
    reviewer: Antigravity (agy headless, independent)
    range: b1c1f5a56..586adcc7c
    verdict: FAIL_WITH_MUST_FIX
    must_fix: [M1 nmbak path traversal, M2 non-atomic merge copy, M3 stale automatic backup]
    fixed_in: 8669388ae
    report: doc/reviews/REALUSE-DATA-SAFETY-1-antigravity-r1.md
depends_on: []
base_commit: b1c1f5a56
branch: task/REALUSE-DATA-SAFETY-1
worktree: G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1
integration_commit: null
delivery_head: 8669388ae
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/REALUSE-DATA-SAFETY-1
allowed_paths:
  - doc/tasks/REALUSE-DATA-SAFETY-1.md
  - doc/V11X_PROGRAM.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/handoffs/REALUSE-DATA-SAFETY-1-handoff.md
  - src/infrastructure/resource_channel/catalog_store.py
  - src/infrastructure/resource_channel/handle_resolver.py
  - src/infrastructure/sqlite/upgrade_legacy_layout.py
  - src/infrastructure/sqlite/nmbak.py
  - src/bootstrap/core_service.py
  - src/bootstrap/core_assembly.py
  - apps/desktop-avalonia/src/NewManga.Host/DataSafety.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostCommandRegistry.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/**
  - tests/infrastructure/**
  - tests/bootstrap/**
  - tests/core/**
  - tests/storage/**
  - apps/desktop-avalonia/tests/**
  - verification/REALUSE-DATA-SAFETY-1/**
  - doc/reviews/REALUSE-DATA-SAFETY-1-*.md
  - G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1/**
---

# REALUSE-DATA-SAFETY-1：修复真实使用自查 P1 数据安全缺陷（B1）

## 来源与目标

2026-10-30 真实使用自查（发布包 0.1.1，见 `G:\CODEX\New Manga.workspace\tmp\self-audit\DEFECTS.md`）确认 3 条 P1 中的 2 条与数据安全直接相关，用户裁决「B1 数据安全优先」。目标：让用户数据在**迁移/恢复/升级**场景下不丢、不坏、可回滚。

对应缺陷：

| 编号 | 缺陷 | 本 Task AC |
|---|---|---|
| MA-01 | 数据根复制/换机/整目录备份还原 → Core 命名空间绑定校验崩溃 exit 1，无自愈无 UI 指引 | AC1 |
| MA-03 | 当前 `library.db` + 100MB `managed/` 零可用备份；first-run backup 只复制 catalog | AC2 |
| MA-12 | Host 在 Core 迁移前预创建 `managed`/`backups`，使旧布局目录迁移必然被跳过 | AC3 |
| MA-13 | `ReadOnlyUntilParity` 只读会话仍创建/迁移 `library.db` | AC4 |

证据基线：`runs\02-realdata-library\logs\core_service.stderr.log`、`runs\03-realdata-clean-lock\logs\core_service.stderr.log`、`data-audit.md` D-01/D-03/D-04。

## Acceptance Criteria

- [x] **AC1 命名空间迁移自愈**：把数据根整目录复制到另一路径后以 `--data-root=<副本>` 启动，`core_service` 不再因 `namespace lock is bound to a different derived root` / `namespace binding identity mismatch` 崩溃；自动重绑定到新的 derived/catalog identity，`host.log` 出现明确迁移日志，书架数据完整（1 书 1 章 169 页），Host 就绪。绑定结构异常（catalog 表非 canonical、行数≠1、权限错误）时仍 fail closed 并给出可诊断 stderr。 <<MET: 4 单元测试 + 既有安全测试 7/7 + 真实数据副本源码级完整启动链（books=1/chapters=1/pages=169）；待独立审查>>
- [x] **AC2 真实备份**：首次写入前与迁移前生成含 `library.db` + `managed/**` + manifest 的 `.nmbak`（复用 Core `NmbakBackupService`），保留 N 份；`backup_list/create/restore` 经 `IHostController` 接到 Console「备份与恢复」分区；删除 `library.db` 后可从备份恢复出 169 页书架。 <<MET: Core 迁移前 + 首启自动备份（含 pages.managed_original_ref 原图）；Console ⑥ 分区接真实 Host 面（列表/创建/删除/恢复 + 二次确认）；真实数据副本验证 90.2 MiB / 169 原图 / 169 页；dotnet build 0W0E + 3 headless UI 测试通过；待独立审查>>
- [x] **AC3 迁移顺序**：旧布局 `<root>/data/{library.db,managed,backups}` 在生产 Host 路径下被完整迁移（`copied` 含 `managed/` 与 `backups/`），不再因 Host 预创建空目录而跳过；补 Host 级集成测试。 <<MET: `_promote_directory_merged`（空目标原子替换、非空目标只补缺失文件、绝不覆盖当前文件）；4 个新测试覆盖预创建空目录/非空合并/不覆盖/空 backups 目录；文件内 16/16 通过；全量 pytest exit 0；待独立审查>>
- [x] **AC4 只读语义**：`ReadOnlyUntilParity` 会话要么不写既有库（`query_only`/拒绝迁移），要么把「schema bootstrap 可写、用户数据只读」在日志与 UI 中明确区分；不再出现「日志称只读、实际写库」的矛盾。 <<MET: 选择「明确区分」并落地两侧——Core `[core.schema]` 启动日志说明 schema bootstrap 是只读会话唯一写入、用户行与托管原图不被修改；Host `CoexistenceRules` 决策文案与 UI 标签改为「用户数据只读 + Core 仍可建库/升级 schema」；新增契约测试 `ReadOnlyUntilParity_NamesTheSchemaWriteSeam`；Host 50 passed；待独立审查>>

## 允许修改范围

见 frontmatter `allowed_paths`。共享契约变化：新增 Core→Host 备份命令调用面（复用既有 `backup_*` 注册，不新增 wire 命令）；不修改 `doc/contracts/V11R_COMMAND_CONTRACT_V1.md` 的 C001–C076 语义。

## 禁止范围

- 不删除/不清空用户真实数据根 `%APPDATA%\com.newmanga.desktop`；所有实验用副本。
- 不修改 DB schema（不新增表/列）；复用既有 `backup_records` 与 `preview_namespace`。
- 不改 `ThemePack` 退役结论、不改 V11R 冻结设计令牌。
- 不 push 远端。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 单测：复制命名空间目录后重绑定不抛 | `python -m pytest tests/infrastructure/test_preview_namespace_rebind.py -q` | Python 3.14 / Windows 10.0.26300 | PASS 4/4（2026-10-30） | `tests/infrastructure/test_preview_namespace_rebind.py` |
| AC1 负向：catalog 结构异常仍 fail closed | 同上（`test_rebind_fails_closed_on_non_canonical_namespace_table` / `test_missing_lock_after_migration_fails_closed`） | 同上 | PASS | 同上 |
| AC1 既有安全边界回归 | `python -m pytest tests/core/test_core_namespace_bootstrap.py -q` | 同上 | PASS 7/7 | 该文件 |
| AC1 实机级：复制真实数据根后完整启动链读数 | `python verify_migrated_root.py %APPDATA%\com.newmanga.desktop <副本>` | 真实用户库 169 页 + 旧 lock | PASS：`books=1 chapters=1 pages=169 progress=1 title='家族战记'`，日志 `[core.namespace] data root identity changed ... re-bound` | `G:\CODEX\New Manga.workspace\tmp\self-audit\verify_migrated_root.py`、`runs\12-migrated-root` |
| AC2 单测：迁移前/首启自动备份 + 原图纳入包 + 恢复 | `python -m pytest tests/infrastructure/test_nmbak_startup_backup.py tests/storage/test_nmbak_backup.py tests/storage/test_backup_restore.py tests/core/test_core_backup_wire.py -q` | Python 3.14 / Windows 10.0.26300 | PASS：启动备份 5/5、包与原图 8 例、合计 52 passed（2026-10-30） | 上述测试文件 |
| AC2 真实数据：自动备份包含 169 张原图与 169 页库 | `python verify_backup_real.py %APPDATA%\com.newmanga.desktop <副本>` | 真实用户库 169 页 | PASS：包 90.2 MiB、`page_originals=169`、`original_bytes=100,434,899`、包内库 `books=1 pages=169` | `G:\CODEX\New Manga.workspace\tmp\self-audit\verify_backup_real.py`、`runs\13-backup-real` |
| AC2 UI：Console ⑥ 列表/创建/删除/恢复（含二次确认） | `dotnet test ... --filter "FullyQualifiedName~V2ConsoleUiTests.Backup"` | headless Avalonia | PASS 3/3 | `V2ConsoleUiTests.cs` |
| AC2 UI 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -warnaserror` | net9.0 | PASS 0 warning / 0 error | 控制台输出 |
| AC3 单测：预创建目录时仍迁移 managed/backups | `python -m pytest tests/infrastructure/test_upgrade_legacy_layout.py -q` | Python 3.14 / Windows 10.0.26300 | PASS 16/16（含 4 个 AC3 新例：预创建空目录 / 非空合并 / 不覆盖当前文件 / 空 backups 目录） | `tests/infrastructure/test_upgrade_legacy_layout.py` |
| AC4 契约：只读语义显式区分 schema 写入 | `dotnet test tests/NewManga.Host.Tests --filter "FullyQualifiedName~ReadOnlyUntilParity_NamesTheSchemaWriteSeam"` | net9.0 | PASS（Host 合计 50 passed） | `tests/NewManga.Host.Tests/HostUnitTests.cs` |
| AC4 运行日志：Core 声明 schema 是唯一写入 | 启动数据根后读 `core_service.stderr.log` | 同上 | PASS：`[core.schema] applied N migration(s) up to vX; schema bootstrap is the only write a read-only session performs` | `src/bootstrap/core_assembly.py` |
| Review r1 M1：备份路径穿越拦截 | `python -m pytest tests/storage/test_nmbak_backup.py -q` | Python 3.14 / Windows 10.0.26300 | PASS 21/21（含 5 个新增负向例：绝对路径 create、`..` create、revision 绝对路径、篡改 manifest `..` 恢复、篡改 manifest 绝对路径恢复） | `tests/storage/test_nmbak_backup.py` |
| Review r1 M2：合并拷贝原子性 | `python -m pytest tests/infrastructure/test_upgrade_legacy_layout.py -q` | 同上 | PASS 18/18（含 2 个新增：中断不留半写、发布前经过 os.replace） | `tests/infrastructure/test_upgrade_legacy_layout.py` |
| Review r1 M3：过期自动备份轮转 | `python -m pytest tests/infrastructure/test_nmbak_startup_backup.py -q` | 同上 | PASS 8/8（含 3 个新增：时间解析、陈旧包轮转、空库不轮转） | `tests/infrastructure/test_nmbak_startup_backup.py` |
| 全量回归 | `python -m pytest -q --tb=no`；`dotnet test NewManga.sln` | 同上 | PASS：pytest exit 0（2735+ passed）；dotnet test 全项目 0 failed | `G:\CODEX\New Manga.workspace\tmp\self-audit\pytest-full6.log` |

## 依赖、风险与阻塞

- 无硬依赖。
- 风险：AC1 自动重绑定若过宽，可能把「属于另一套数据的 catalog」也重绑定，导致资源引用失效。缓解：只对可识别的 binding 不一致重绑定；结构异常仍抛错；重绑定后资源解析仍 fail closed。
- 风险：AC2 备份 100MB+ 会带来磁盘与耗时开销，须设保留份数与失败降级策略。
- Reviewer 尚未指派（Lead 不得审自己实现，须由未参与实现的 ZCode / Antigravity / Codex 独立审查）。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。

## Canonical Evidence

进入独立审查前的当前证据（`commit` = 含该文件的提交；仓外证据给绝对路径）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-AC1-TESTS | AC1 | `tests/infrastructure/test_preview_namespace_rebind.py` | `38f09ac90` | 由 git 内容确定 | CANONICAL |
| E-AC1-SAFETY | AC1 | `tests/core/test_core_namespace_bootstrap.py`（7/7 通过，内容未改） | `38f09ac90` | 由 git 内容确定 | CANONICAL |
| E-AC1-REAL | AC1 | `G:\CODEX\New Manga.workspace\tmp\self-audit\verify_migrated_root.py` + `runs\12-migrated-root\` | `38f09ac90` | 仓外脚本 + 运行输出 | SOURCE_PIN |
| E-AC2-BACKUP-CORE | AC2 | `tests/infrastructure/test_nmbak_startup_backup.py`、`tests/storage/test_nmbak_backup.py` | `75aeff349` | 由 git 内容确定 | CANONICAL |
| E-AC2-REAL | AC2 | `G:\CODEX\New Manga.workspace\tmp\self-audit\verify_backup_real.py` + `runs\13-backup-real\` | `75aeff349` | 仓外（90.2 MiB / 169 原图） | SOURCE_PIN |
| E-AC2-UI | AC2 | `apps/desktop-avalonia/tests/NewManga.App.Tests/V2ConsoleUiTests.cs`（3 例） | `811078ebb` | 由 git 内容确定 | CANONICAL |
| E-AC3-MIGRATE | AC3 | `tests/infrastructure/test_upgrade_legacy_layout.py`（16 例，含 4 个 AC3 新例） | `ff3dee029` | 由 git 内容确定 | CANONICAL |
| E-AC3-IMPL | AC3 | `src/infrastructure/sqlite/upgrade_legacy_layout.py`（`_promote_directory_merged`） | `ff3dee029` | 由 git 内容确定 | CANONICAL |
| E-AC4-SEAM | AC4 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/HostUnitTests.cs`（`ReadOnlyUntilParity_NamesTheSchemaWriteSeam`） | `b1ff8921f` | 由 git 内容确定 | CANONICAL |
| E-AC4-LOG | AC4 | `src/bootstrap/core_assembly.py`（`[core.schema]` 启动日志） | `b1ff8921f` | 由 git 内容确定 | CANONICAL |
| E-REVIEW-R1 | Gate | `doc/reviews/REALUSE-DATA-SAFETY-1-antigravity-r1.md`（Antigravity 独立审查，FAIL_WITH_MUST_FIX） | `8669388ae` | 由 git 内容确定 | CANONICAL |
| E-BUILD | AC1–AC4 | `dotnet build -warnaserror` 0W/0E；`dotnet test NewManga.sln` 811 passed / 0 failed；`python -m pytest -q` exit 0 | `b1ff8921f` | 运行输出 | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1 | PRESERVE_REFERENCED | 同左 | 待关闭时记录 | 待关闭时检查 |
| temp | G:/CODEX/New Manga.workspace/tmp/self-audit | PRESERVE_REFERENCED | 同左 | 待关闭时记录 | 自查证据，保留 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
