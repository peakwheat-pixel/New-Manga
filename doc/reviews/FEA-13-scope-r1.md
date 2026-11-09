---
task: FEA-13
title: FEA-13（备份/恢复/迁移）独立 scope review r1（backup/1↔backup/2 现状、覆盖清单、调度、merge restore、迁移 journal、拆片与契约影响）
reviewer: fresh subagent（独立上下文；未参与 FEA-13 相关实现；只读）
session: 本审查子会话（DSH fresh subagent；会话 id 由 DSH 台账登记）
parent_session: session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5
reviewer_kind: subagent
date: 2026-11-09
repo: G:\CODEX\New Manga
branch: main
worktree: clean（写入本报告前；`git status --porcelain` 仅本文件）
reviewed_head: 461684432
verdict: NEEDS_UNFREEZE
---

# FEA-13 Scope Review r1（独立只读）

> **结论先行：`NEEDS_UNFREEZE`（窄口径）。**
>
> - **不需要重开大契约**：`DatabaseId` 可存放在**既有** `application_metadata` 表（`schema.py:128-132`），**不需要新 DDL、不需要 schema pin**；`backup.*` 是应用通道命令，**不在 M2-C1**，其 wire 行在 `V11R_COMMAND_CONTRACT_V1.md:63-66`（C006–C009，minor 3），新增字段/码属该文档的行级修订，不动 18 pins。
> - **但必须先处置 4 个裁决点**（详见 §6）：① C-09 SC-B07 把 `backup/1` 写成 `format:"nmbak"+version:1`，而**真实 v1 字节**是 `format:"nm-backup"+format_version:1`（`nmbak.py:54-55,208-226`；测试断言 `test_nmbak_backup.py:122-123`）；② C-01b SC-14 标 `[现行]` 并写「恢复默认逐项 Defer…不得整库覆盖」，而代码是**明确整库覆盖**（`nmbak.py:19-22`；`backup.py:129-146,252-259`）——这条 `[现行]` 是**假陈述**；③ C-09 SC-B01a 自称「完整归属表」却**漏掉 `drafts/`**（C-01b SC-10b 与方案 `:520` 都要求入包；代码中 draft journal 是库外文件 `core_assembly.py:1606`）；④ SC-B01a 的 `settings/*.json` 拆分把**两个不同层**混成一行：`<data_root>/settings/*.json` 是 Core 侧 provider/network/binding 配置（`core_assembly.py:1913-1915`、`json_profile_stores.py:11,142-250`），而「外观设置」在 `%APPDATA%/NewManga/`（`ThemeSettingsStore.cs:7`、`App.axaml.cs:67-73`）——后者在 Core 的 `nmbak` 写域之外，现架构下无法入包。
> - **backup/2 写端、legacy adapter、覆盖清单、调度、merge restore 全是「未实现」而非「缺测试」**；只有 backup/1 的 create/list/restore/delete 与「启动时自动包 + 保留轮转」是真实的。
> - **建议拆 6 片，其中 5 片可立即冻结实施、1 片（数据根迁移）建议单列/阻塞**；首片建议 `FEA-13-BK2-1`（backup/2 写端 + 版本协商 + v1 只读 adapter），**但它必须先拿到 errata 后的 v1 字面值口径**，否则 AC 与 C-09 字面直接冲突。

---

## 1. 只读核验基线

| 项 | 事实 | 证据 |
|---|---|---|
| 分支 / 工作区 | `main` / clean（写入本报告前无 modified/untracked） | `git status --short`（空） |
| HEAD | `461684432`（`docs(fea-11-2c-residual-1): 收口 done…`） | `git log --oneline -3` |
| 治理检查（默认） | **PASS（3 warnings；exit 0）** | `pwsh -NoProfile -File tools/governance/check.ps1` |
| 治理检查（`-TaskPath`） | **PASS（3 warnings；exit 0）**，用 `doc/tasks/FEA-11-HOST-AUTH-3.md`（FEA-13 尚无卡） | `... check.ps1 -TaskPath 'doc/tasks/FEA-11-HOST-AUTH-3.md'` |
| pins | **PIN AUDIT: PASS (all 18)**，C09 = `dc51226b336c` | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` |
| 定向 pytest（备份面） | **41 passed**（`tests/storage/test_nmbak_backup.py` + `tests/infrastructure/test_nmbak_startup_backup.py` + `tests/core/test_core_backup_wire.py`，4.79s） | 本 review 实跑 |
| 定向 pytest（旧布局迁移） | **18 passed**（`tests/infrastructure/test_upgrade_legacy_layout.py`） | 本 review 实跑 |
| 全量基线 | pytest 3395/10、.NET 1794/0/107（本 review **未重跑**全量） | `doc/STATUS.md:20` |
| 依赖节点 | FEA-09 / FEA-10 / FEA-12（四卡）均 `done`；`G-CONTRACT`/`G-DELETE-CONTRACT` CLOSED；`G-DELETE-IMPL` 仍 OPEN | `doc/STATUS.md:7-11,16`；`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md:129` |

本 review 未改生产源码/测试/契约/STATUS/PLAN/LEDGER/证据，未 commit/push；唯一写入是本文件。

---

## 2. Q1：backup/1 与 backup/2 的现状（含 SC-B07 缺口）

### 2.1 两套实现，一套在生产里是死码

| 实现 | 产物形状 | 生产接线 | 结论 |
|---|---|---|---|
| `NmbakBackupService`（`src/infrastructure/sqlite/nmbak.py`，730 行） | zip 包 `<id>.nmbak`：`manifest.json` + `library.db` + `library.db.sidecar.json` + `managed/**` | **唯一生产路径**：`core_assembly.py:1921-1927`（`backup=`）、迁移前钩子 `core_assembly.py:148-181`；Core handler `core_service.py:3150-3182` | 真正的 backup/1 |
| `SqliteBackupService`（`src/infrastructure/sqlite/backup.py`，370 行） | 裸 `<id>.db` + `<id>.db.manifest.json` sidecar，**无任何 format/version 字段** | **生产 0 接线**：全仓引用仅 `tests/storage/test_backup_restore.py`、`tests/storage/test_schema_migration.py`、两个 `verification/**` 探针 | 前 nmbak 的 DB-only 旧路径，**不构成 backup/N 版本** |
| `BackupLedger` Protocol（`src/application/maintenance/backup.py:21-39`） | 仅协议 | 生产**无实现者** | 死契约面 |

> 任务前提里写的 `src/application/maintenance/nmbak.py` **不存在**；`src/application/maintenance/backup.py` 只有 39 行 Protocol（见 §10）。
> 附带事实：`backup_records` 表（`schema.py:134-145`）**只被死码写入**（`backup.py:91-109`），`nmbak` 从不写它 → 生产库中该表恒为空。

### 2.2 backup/1 的真实字节（这是 Q1 的关键事实）

| 事实 | path:line |
|---|---|
| `FORMAT_NAME = "nm-backup"`、`FORMAT_VERSION = 1` | `src/infrastructure/sqlite/nmbak.py:54-55` |
| manifest 写 `"format": FORMAT_NAME` + `"format_version": FORMAT_VERSION` | `nmbak.py:209-210` |
| 读取端校验 `format != FORMAT_NAME` → `BACKUP_CORRUPT`（"not a nm-backup"） | `nmbak.py:572-573` |
| 读取端校验 `format_version != FORMAT_VERSION` → `BACKUP_CORRUPT` | `nmbak.py:580-588` |
| 测试把 v1 布局钉死：`manifest["format"] == FORMAT_NAME`、`format_version == 1` | `tests/storage/test_nmbak_backup.py:108-135`（`:122-123` 精确断言） |
| 包内含 `manifest.json`/`library.db`/sidecar/`managed/**` | `nmbak.py:1-10`；测试 `test_nmbak_backup.py:115-120` |

**判定**：现有 `.nmbak` = **backup/1 的唯一现实形态**，其字面值是 `nm-backup` / `format_version:1`。
C-09 SC-B07（`doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md:136-141`）把它写成 `format:"nmbak"` + `version:1`，并规定 v2 为 `format:"nmbak"` + `version:2`，还要求「不得混用三种写法」。

### 2.3 SC-B07 三条要求逐项核对

| SC-B07 要求 | 现状 | 证据 |
|---|---|---|
| 版本协商（读 `version`；`>2` → `BACKUP_FORMAT_UNSUPPORTED`；`==1` → legacy adapter 只读） | **全缺**。只有「恰好等于 1」这一条路，且错误是 `BACKUP_CORRUPT` 而非 `BACKUP_FORMAT_UNSUPPORTED`；`BACKUP_FORMAT_UNSUPPORTED` 在全仓 `src/**` **0 命中**；wire 错误表也无该码（`core_service.py:441-452`） | `nmbak.py:576-588`；`grep BACKUP_FORMAT_UNSUPPORTED src` = 0 |
| legacy adapter 只读、不就地升级、写端只写 v2 | **全缺**：只有一个写入版本（v1），无 adapter 概念，也没有 v2 写端 | `nmbak.py:54-55,174-265` |
| 强制增量 ① 显式清单 ② 每项 `sha256`+字节 ③ `DatabaseId`+`schemaVersion` ④ 包内加密源授权元数据段 | ① 部分有（`revision_refs`/`page_original_refs`）；② **已有**；③ `schema_version` 有、`DatabaseId` **无**（`src/**` 0 命中）；④ **无**（Host DPAPI registry 不在包内） | `nmbak.py:208-226`；`grep DatabaseId src` = 0；`SourceAccessRegistry.cs:21-26` |

**一句话缺口**：现有包是「v1 字面值 + 硬等值版本校验」的单一形态，**版本协商、`BACKUP_FORMAT_UNSUPPORTED`、legacy adapter 只读、v2 写端、`DatabaseId`、加密源授权段六项全缺**。

---

## 3. Q2：SC-B01/B01a 备份覆盖清单逐项对照

### 3.1 现有包实际覆盖（create 侧）

| 入包内容 | 来源 | 证据 |
|---|---|---|
| `manifest.json` | 显式清单 + `sha256`/`size_bytes` | `nmbak.py:208-229` |
| `library.db`（SQLite backup API 一致性快照） | 活库整库 | `nmbak.py:184-187,394-401` |
| `library.db.sidecar.json`（schema/hash/app_version） | — | `nmbak.py:188-196` |
| `managed/<rel>`：**current + pinned** artifact revision 文件 | `artifact_revisions` JOIN `media_artifacts` | `nmbak.py:450-498,500-540` |
| `managed/<rel>`：导入页原件（`pages.managed_original_ref`） | `pages` | `nmbak.py:403-448`（含 REALUSE-DATA-SAFETY-1 修复） |

### 3.2 与 C-09 归属表（`FEA-C09_…DRAFT.md:33-44`）逐项对照

| 契约行 | 契约判定 | 现状 | 差异/证据 |
|---|---|---|---|
| `library.db` | 是 | **是** | `nmbak.py:184` |
| sidecar | 是 | **是** | `nmbak.py:188-196` |
| `managed/`（含 `trash-manifest.json`） | 是（需扩白名单） | **部分**：只打包被引用的 revision/original 文件；`<managed_root>/trash-manifest.json` **不入包** | `nmbak.py:500-540`；manifest 位置 `core_assembly.py:1368`；白名单校验 `nmbak.py:660-665` |
| 源引用与授权元数据（包内加密） | 是 | **否**。Host 私有 registry `<DataRoot>/host/source-access/registry.v1.dat`（DPAPI CurrentUser）在 Core 写域外 | `SourceAccessRegistry.cs:21-26`；`FEA-C09:70`（L-3：实现路径未核） |
| `derived/` | 否 | **否** ✅ | `nmbak.py` 无 derived 处理 |
| `catalog.sqlite` | 否（可从 `library.db` 重建） | **否** ✅ | `<data_root>/catalog/catalog.sqlite`（`HostRuntime.cs:885`）不在包内 |
| `settings/*.json` | 凭据类否 / 非凭据类**是** | **全否**。Core 侧 `<data_root>/settings/{provider_profiles,network_profiles,provider_capability_bindings}.json` **不入包**；`%APPDATA%/NewManga/theme-settings.json`、`presentation-settings.json` 也不在包内 | `core_assembly.py:1913-1915`；`json_profile_stores.py:11`（secrets 不入这些文件）、`:142-146,181-185,246-250`；`ThemeSettingsStore.cs:7`；`AppearanceStore.cs:17`；`App.axaml.cs:67-73` |
| 外部原文件 | 否 | **否** ✅ | 引用模型 |
| `backup/1` 旧包 | 否（不复制进新包） | ✅ 不复制 | `nmbak.py:144`（list 用 glob） |
| `backup/2` 新包 | 不适用 | — | — |
| **`drafts/`（C-13 draft journal）** | **表内无此列**（但在 C-01b SC-10b `:54` 与方案 `:520` 要求入包） | **否**：`<data_root>/drafts/` 是库外文件，未入包 | `core_assembly.py:1606`（`DraftJournal(Path(db_path).parent / "drafts")`） |
| **`plugins/`（已安装插件文件）** | 表内无 | **否**；而 `plugin_state` 行随库入包 → 恢复后可能出现悬空插件状态 | `core_assembly.py:1928-1932`（`<data_root>/plugins`） |

**判定**：SC-B01a 自称「完整归属表」，实测**漏 2 类库外应用内数据**（`drafts/`、`plugins/`），且把 Core 的 `settings/` 与 Host 的 `%APPDATA%` 外观设置混为一行；「需扩白名单」的两项（`trash-manifest.json`、非凭据设置）**都未实现**。
另：方案 `:901` 要求 backup/2「逐项记录 profiles、catalog、草稿、Run、人工版本及 source 授权元数据的**包含/缺失**」——现 manifest 只有「包含」清单，**没有「显式不包含」记录**。

---

## 4. Q3：SC-B08 自动备份调度

### 4.1 现有实现（不是调度器，是启动钩子）

| 事实 | 证据 |
|---|---|
| `_ensure_automatic_backup(core)` 只在 `main()` 启动时调一次，**不循环、不定时** | `core_service.py:8020`（调用）、`:7851-7916`（实现） |
| 保留份数硬编码 `_AUTOMATIC_BACKUP_KEEP = 5`；刷新窗口硬编码 `_AUTOMATIC_BACKUP_REFRESH_HOURS = 24` | `core_service.py:7830,7834` |
| 「最新 verified 包」取**任意类型**（含 manual），据此算年龄决定是否轮转 | `core_service.py:7878-7897` |
| 失败只打 stderr，无 receipt、无 K 次降级、无 UI 提示 | `core_service.py:7911-7916` |
| 清理集合把 `pre_migration`、`pre_restore` 一并当自动包删除 | `core_service.py:7926-7942`（`:7931` 类型集合） |
| Host 侧**无**备份定时器（只有 source scan/watcher timer） | `SourceScanScheduler.cs:1234`、`SourceWatcher.cs:792`；Host 备份面仅 `HostRuntime.cs:344-413` 透传 |
| 注释仍写「automatic backups have no scheduler consumer yet」 | `core_service.py:3151-3153`（与 `:7851` 现状矛盾） |

### 4.2 SC-B08 五项要求核对

| SC-B08 要求 | 现状 | 判定 |
|---|---|---|
| 归属 Core、单 scheduler、Host 不起定时器 | Host 无 timer ✅；但 Core 侧**没有**「与 Run 同一 owner 约束」的调度器，只有启动钩子 | **部分**（形式满足、实质缺调度） |
| 手动备份不重置自动计时 | **违反**：`verified` 集合含 manual，手动包会让年龄变小 → 不轮转 | ❌（`core_service.py:7878-7883`） |
| 保留策略 N 可配置、手动包不自动清理 | 手动不清理 ✅；N **硬编码 5**，不可配置 | **部分** |
| 自动失败不影响主流程、记 receipt、连续 K 次降级仅提示 | 不影响主流程 ✅（try/except）；receipt/K 降级/UI 提示 **全缺** | ❌ |
| `DatabaseId` 不匹配的自动包不得被恢复流程选中 | `DatabaseId` 不存在 | ❌ |

**附加风险（P2，需在冻结时写死）**：清理把 `pre_restore` 计入可删集合（`:7931`），而恢复失败文案把 pre_restore 包当作回滚点（`nmbak.py:283-323`）。ADJ-001 `:42`（自动清理/备份轮转）要求「必须保留 Lock、current/pinned、草稿、**备份依赖、恢复链**」——**现实现可能删掉最近一次恢复的回滚包**。测试只断言「manual 不被删」（`test_nmbak_startup_backup.py:142-171`），无 pre_restore 保护断言。

**方案 `:1044` 的 AC（每天/每周/自定义、关闭开关、错过计划启动提示、保留数与最近 verified 包保护、注入时钟、关闭自动备份不关闭恢复入口）现状：0/6。**

---

## 5. Q4：merge restore 与数据根迁移 journal

### 5.1 restore 是覆盖式，不是 merge

| 事实 | 证据 |
|---|---|
| 模块 docstring 明写 `restore` is overwrite-only（+ 强制 pre_restore） | `nmbak.py:19-23` |
| 同样明写 overwrite：`SqliteBackupService.restore_backup` docstring | `backup.py:129-146` |
| 实际写入：`source.backup(self._conn._current())` 直接覆盖活库 | `nmbak.py:677-694`；`backup.py:252-259` |
| 无 `mode`/`conflictPolicy` 入参；Core handler 只收 `backup_id` + `confirm_restore` | `core_service.py:3166-3175`；wire `V11R_COMMAND_CONTRACT_V1.md:65`（C008） |
| 无 RestorePlan、无逐项 add/update/conflict、无 defer、无「UseBackup 前保全当前」 | 全仓 `src/**` 无 `restore_plan`/`defer` 恢复面 |
| managed 文件逐个直接写回活库根（非 staging、非原子） | `nmbak.py:696-726`（`:715-726` 逐文件 `write_bytes`） |
| 恢复前只挡「有非终态 Run」；不挡其他写者、不停 lease、无维护窗口 | `nmbak.py:278-281`；`core_assembly.py:1926`（`is_run_active`） |

**判定**：SC-B02/SC-B09（默认 defer、逐项、UseBackup 前保全、不得整库覆盖）与方案 `:526`、`:530`（隔离 staging + 可恢复原子入口）**全部未实现**；现有实现正是方案要求「不能靠全库覆盖实现逐项合并」所禁止的那一种。

### 5.2 数据根迁移：只有「旧布局提升」，没有「换根」

| 事实 | 证据 |
|---|---|
| `migrate_legacy_layout(data_root)`：`<root>/data/*` → `<root>/*`，一次性、幂等、**从不删除旧树** | `upgrade_legacy_layout.py:1-32,206-307` |
| 有 staging 目录 `.upgrade-legacy-staging` + DB `PRAGMA integrity_check` + 「目录先、库最后」原子提升 | `:218,234-251,278-293`；`:24-31`（规则） |
| 有日志追加（自由文本，不是结构化 journal） | `:200-203,296,300` |
| **缺**：迁移 journal（`MigrationId/from-to/DatabaseId/source fingerprint/staging root/planned mappings/applied checkpoints/verified manifest/**commit marker**`） | 方案 `:613`；`grep DatabaseId src` = 0；`:240` 只提「v1–v6 无数据搬迁」 |
| **缺**：独占维护锁（该钩子只在启动、Host 单实例 mutex 之外无显式锁） | `SingleInstance.cs:12`；`host/source-access` 有自有 mutex，但迁移不用 |
| **缺**：切换到**新数据根**的指针（Core 只认 `NEWMANGA_DATA_ROOT`/`HostOptions.DataRoot`，无「切换入口」） | `core_service.py:7946-7947`；`HostOptions.cs`（DataRoot 由 Host 持有） |
| 崩溃恢复只有「重跑幂等」，没有「从已验证 checkpoint 继续」 | `:206-212` |

**判定**：SC-B03 的「复制到新根 → 校验 → 切换指针；journal 含 DatabaseId；独占锁 + staging + 校验 + commit marker；崩溃继续旧根」中，**只有 staging+校验+旧根保留**这一半以另一种语义（旧布局提升）存在；**journal/DatabaseId/commit marker/换根指针/崩溃续跑**全缺，且「换根指针」在 Host 层，超出 FEA-13 §15.6 写域（`方案:935` 只给 `src/infrastructure/sqlite/`、`src/bootstrap/`、Host 备份桥）。

---

## 6. Q5：契约影响（是否需要 UNFREEZE）

### 6.1 不需要动的东西（先排除误判）

| 事项 | 结论 | 证据 |
|---|---|---|
| `DatabaseId` 需要新 DDL / schema pin？ | **不需要**：可写进既有 `application_metadata(metadata_key, value_json, updated_at)`，schema 保持 v9 | `schema.py:128-132,872`；C-01b SC-18 `:67` |
| backup 命令要改 M2-C1？ | **不需要**：`backup.*` 不在 M2-C1（`grep` M2-C1 `backup.` = 0）；其 wire 行在 `V11R_COMMAND_CONTRACT_V1.md:63-66`，且该文档不在 18 pins | `verify_pins.ps1` 输出 18 项不含 V11R |
| 调度配置需要新 settings 契约？ | **不需要**：`settings_sections` 对未冻结 section 走 pass-through（`settings_sections.py:103-105,127-129`），新增 `backup` section 不破冻结 section 集 | 同上 |
| merge restore 的 plan 需要新 DDL？ | **不需要**：plan 是内存/临时 JSON；受保护版本用既有 revision 机制 | — |

### 6.2 必须处置的 4 个裁决点

| # | 契约缺陷 | 事实 | 建议载体 |
|---|---|---|---|
| **D1** | C-09 SC-B07 的 `backup/1` 识别错误（`format:"nmbak"+version:1` vs 真实 `nm-backup`+`format_version:1`） | `nmbak.py:54-55,209-210,572-588`；`test_nmbak_backup.py:122-123`；C-09 冻结记录 §5 L-3 自认「本 checkout 无 `src/`，未做实现级复核」 | **errata（0 pin）**：在 `FEA-CONTRACT-FROZEN-C09.md` 追加 §8 式注记，裁定「v1 字面值 = `format:"nm-backup"`+`format_version:1`；v2 = `format:"nmbak"`+`version:2`；读取端双字面值/双键名兼容，写端只写 v2」 |
| **D2** | C-09 SC-B01a「完整归属表」漏 `drafts/`（以及 `plugins/`） | C-01b SC-10b `:54`、方案 `:520` 均要求；代码 `core_assembly.py:1606,1928-1932` | **errata（0 pin）**：补两行并声明「不新增要求，与 SC-10b 对齐」 |
| **D3** | SC-B01a 把「Core `<data_root>/settings/*.json`（provider/network/binding）」与「`%APPDATA%` 外观设置」混为一行；后者在 `nmbak` 写域之外 | `core_assembly.py:1913-1915`；`json_profile_stores.py:11,142-250`；`ThemeSettingsStore.cs:7`；`App.axaml.cs:67-73` | **additive 修订（重算 C-09 pin）**：二选一——(a) 明确「外观设置不入包，恢复不改外观」（范围缩减，需 DSH 裁决）；(b) 新增 Host→Core staging 输入面（新 wire + Host 备份桥写域，成本高）。若 DSH 认定属「澄清」则降为 errata |
| **D4** | 保留策略可能删掉恢复链；手动备份会重置自动计时 | `core_service.py:7878-7883,7926-7942`；ADJ-001 `:42` | **errata/卡内 AC**：SC-B08 补「手动包不参与自动年龄判定」「最近一次 restore 的 pre_restore 与最近 verified 包不得被自动轮转删除」 |
| **D5**（附带） | C-01b SC-14 `[现行]` 是假陈述（代码整库覆盖） | `FEA-C01b_STORAGE_CONTRACT_DRAFT.md:58`；legend `:18-24`（`[现行]`＝代码已如此）；`nmbak.py:19-22`；`backup.py:129-146` | **errata（0 pin）**：SC-14 状态改 `[新增]`；否则 FEA-13 的「merge restore」会被误当成「回归保护」 |

### 6.3 结论

- **不是「纯实现补齐（0 pin）」**：D1/D2/D5 至少需要 3 条 errata，D3 需要 1 条 additive 修订（或 DSH 裁决 + errata）。
- **也不需要重开大契约**：无 DDL、无 schema pin、无 M2-C1 字节改动、无 18 pins 的机械失效（除 D3 若选 additive 需重算 C-09 单 pin）。
- `G-DELETE-IMPL` 仍 OPEN（`ADJ-001:129`），FEA-13 释放须按 FEA-12 先例做**逐 Task 释放**，不由本 review 构成授权。

---

## 7. Q6：建议拆片（6 片，5 可冻结 + 1 单列）

> 通用约束：`src/infrastructure/sqlite/nmbak.py` 与 `src/bootstrap/core_service.py` 是 4 片共用的单点，**必须一次只开一片**（同文件写权不并行）。证据等级统一 L2（隔离 fixture）；`verification/FEA-13-<片>/**`。

### 片 1（首片）`FEA-13-BK2-1` — backup/2 写端 + 版本协商 + v1 只读 adapter

- **allowed_paths（精确）**：`src/infrastructure/sqlite/nmbak.py`；`tests/storage/test_nmbak_backup.py`（把 v1 布局断言改成 v1-adapter 断言）；`tests/storage/test_nmbak_format.py`（新增）；`verification/FEA-13-BK2-1/**`
- **AC（可观察）**：
  1. 写端产物 `manifest.json` = `format:"nmbak"`、`version:2`、每项 `sha256`+`size_bytes`、`database_id`、`schema_version`；不再写 `format_version`。
  2. 真实 v1 包（`format:"nm-backup"`、`format_version:1`，含无 `page_original_refs` 的旧包）恢复成功；**包字节 sha256 与 mtime 不变**（不就地升级）。
  3. `version:3` 包 → typed `BACKUP_FORMAT_UNSUPPORTED`（`category=validation`、`retryable=false`），**零副作用**：DB 不变、managed 不变、不产生 pre_restore 包、包字节不变。
  4. 未知 `format` 字符串 → 同一个 `BACKUP_FORMAT_UNSUPPORTED`（不得伪装成 `BACKUP_CORRUPT`）。
  5. 变异 RED：把 v3 分支换成 `BACKUP_CORRUPT` → AC3 红；把写端 `version` 写成 1 → AC1 红。
- **证据计划**：v1 golden fixture（由现 writer 生成的字节 + sha256 快照）＋ v3 负向 ＋ 变异；`verification/FEA-13-BK2-1/`。
- **风险**：D1 必须先落 errata，否则 AC2 与 C-09 字面冲突；改 manifest 键会破 `test_nmbak_backup.py:122-123`（已在 allowed_paths）；旧二进制读新包会在 `_read_manifest` fail-closed 拒绝（符合方案 `:615`，需在 handoff 明确为预期）。
- **依赖**：无（可先行）。

### 片 2 `FEA-13-COV-2` — 覆盖清单二期（settings/drafts/trash-manifest/plugins + verified 语义）

- **allowed_paths**：`src/infrastructure/sqlite/nmbak.py`；`src/bootstrap/core_assembly.py`；`tests/storage/test_nmbak_coverage.py`（新增）；`verification/FEA-13-COV-2/**`
- **AC**：
  1. 包内包含 `<data_root>/settings/{provider_profiles,network_profiles,provider_capability_bindings}.json`（存在才入）、`<data_root>/drafts/**`、`<managed_root>/trash-manifest.json`、`<data_root>/plugins/**`（待 D2 裁决后确认），每项 `sha256`+`size_bytes`。
  2. `catalog/catalog.sqlite`、`derived/**`、外部原文件、OS 凭据 vault **不在包内**，且 manifest 有**逐项「不纳入」记录**（方案 `:901` 的「包含/缺失」要求）。
  3. `verified=true` 仅当全部必含类别均覆盖；任一必含类别缺失 → 不产出包（typed `BACKUP_CREATE_FAILED`）。
  4. 恢复侧本期**不写回** drafts/settings/plugins（写回归片 4 的合并语义）；断言 restore 后这些路径字节不变且报告 `deferred_categories`。
- **证据计划**：每类别正/负 fixture + 包内容枚举断言 + 「不纳入」记录断言。
- **风险**：直接写回会与活库草稿冲突 → 明确 deferred；settings 入包大小/隐私需在卡内声明（secrets 已不入这些文件，`json_profile_stores.py:11`）。
- **依赖**：片 1（需要 v2 显式清单）。

### 片 3 `FEA-13-ID-3` — `DatabaseId` 原语 + manifest/恢复过滤

- **allowed_paths**：`src/infrastructure/sqlite/identity.py`（新增）；`src/infrastructure/sqlite/nmbak.py`；`src/bootstrap/core_assembly.py`；`src/bootstrap/core_service.py`（仅 backup 面）；`apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs`；`apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`；`tests/storage/test_nmbak_identity.py`（新增）；`tests/core/test_core_backup_wire.py`；`verification/FEA-13-ID-3/**`
- **AC**：
  1. 首次可写启动在 `application_metadata` **原子**写入 `database_id`（UUID4），schema 仍 v9；重复启动不改变。
  2. 旧库（无该键）：迁移第一笔事务内回填；回填前身份读作 **unknown**（非空、非书名、非 hash）。
  3. 备份 manifest 携带 `database_id`；v1 包无该字段 → adapter 读作 unknown。
  4. `restore` 跨 `database_id` → typed 拒绝且零副作用（码名由 DSH 定：复用 `TRASH_RESTORE_LAYER_MISMATCH` 或新码）。
  5. `backup.list` 每项含 `database_id`（`null`=unknown）；Host 投影同步（V11R `:264-265` 记 `backup_list` 为 PARTIAL，未类型化）。
- **风险**：码名归属（`TRASH_*` 属 trash family，借用需 DSH 裁决）；identity 回填与 `MigrationRunner` 事务耦合；UI 展示不在本片写域。
- **依赖**：片 1（manifest v2）。

### 片 4 `FEA-13-RESTORE-4` — merge restore（RestorePlan/默认 defer/UseBackup 前保全）+ staging

- **allowed_paths**：`src/application/maintenance/restore_plan.py`（新增）；`src/infrastructure/sqlite/nmbak.py`；`src/bootstrap/core_service.py`；`apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs`；`apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs`；`apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`；`tests/core/test_core_restore_plan.py`（新增）；`tests/storage/test_nmbak_merge_restore.py`（新增）；`verification/FEA-13-RESTORE-4/**`
- **AC**：
  1. `restore_plan` 只读：逐项 add/update/conflict + 依赖；**零写**（DB/managed/包字节不变）。
  2. 默认 `mode="defer"`：只应用无冲突项，冲突项保留现值并逐项列出；**不整库覆盖**。
  3. 选 `UseBackup` 前先保存当前人工/结果为受保护可恢复版本，确认成功才推进该项。
  4. 目标 generation 变化 → 该项 typed 拒绝并要求重预览，其余已确认项继续（不整批失败）。
  5. L-5（`FEA-C11_IMPL_PREREQS.md:26`）：恢复窗口内其他写命令 **fail-closed**（拒绝而非静默降级）；staging 校验通过后才允许 commit marker；marker 前/后各注入一次崩溃，状态可判定、旧根可读。
- **证据计划**：L2 正/负 fixture + 崩溃注入（marker 前/后）+ 零副作用断言。
- **风险**：最高。与 C-13（protected revision）、C-04b（删除 preflight）相邻——**不得越权改**；book/page 级冲突没有 revision 表可用（只有 region/artifact 有），冲突模型需 DSH 先裁决；wire 增 `mode` 与 staging 相关字段；L-5 需与 FEA-12-CORE 的维护窗口互斥协调。
- **依赖**：片 1+2+3。

### 片 5 `FEA-13-SCHED-5` — 调度/保留/失败语义

- **allowed_paths**：`src/application/maintenance/backup_schedule.py`（新增）；`src/bootstrap/core_service.py`；`src/bootstrap/core_assembly.py`；`tests/infrastructure/test_nmbak_startup_backup.py`；`tests/application/test_backup_schedule.py`（新增）；`verification/FEA-13-SCHED-5/**`
- **AC**：
  1. 每天/每周/自定义 + 关闭开关；注入时钟不真等待；关闭自动备份后**恢复入口仍可用**（方案 `:1044`）。
  2. 错过计划 → 启动时 typed receipt/提示，不静默跳过。
  3. 保留 N 可配置；手动包永不自动删；**最近 verified 包与最近一次 restore 的 pre_restore 不得被轮转删除**（ADJ-001 `:42`）。
  4. 手动备份**不**重置自动计时（修 `core_service.py:7878-7883`）。
  5. 自动失败不影响主流程、写 receipt；连续 K 次降级为仅提示；Host 无定时器；同步修 `:3151-3153` 过期注释。
- **风险**：与 Run scheduler owner 约束同源（`core_service.py:1280-1283` 的 `.run-owner.lock`）；改动会破 `test_nmbak_startup_backup.py:142-171`（在 allowed_paths）；N 的持久化载体需在卡内一次定死。
- **依赖**：片 2（类别先入包）；可与片 4 并行（文件不重叠，仅 `core_service.py` 互斥）。

### 片 6 `FEA-13-MIGRATE-6`（建议单列/阻塞，**不进 FEA-13 首轮冻结**）— 数据根迁移 journal

- **allowed_paths**：`src/infrastructure/sqlite/data_root_migration.py`（新增）；`src/bootstrap/core_service.py`；`apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`、`HostOptions.cs`；`tests/infrastructure/test_data_root_migration.py`（新增）；`verification/FEA-13-MIGRATE-6/**`
- **AC**：SC-B03 + L-5 四条（独占锁、staging、文件数/字节/hash 校验、commit marker 后才切换、崩溃注入 marker 前/后、journal 含 `DatabaseId`）。
- **阻塞原因（CONCRETE）**：换根指针由 Host 持有（`HostOptions.DataRoot` / `NEWMANGA_DATA_ROOT`），Core 无切换权；方案 `:935` 只给 Host 备份桥，没给数据根指针；C-01b SC-17 `[新增]`、SC-18 `[未实现]`（`:66-67`）。**需 DSH 先裁决「指针归属 + 是否与 FEA-14-SET 的文件与存储切片合并」**，否则该片在冻结时就跨层越界。

**顺序**：BK2-1 → COV-2 → ID-3 → RESTORE-4 → SCHED-5（COV-2 与 ID-3 可互换）→ MIGRATE-6（另行裁决）。

---

## 8. Q7：verdict

**`NEEDS_UNFREEZE`**（窄口径：3 errata + 1 additive 修订；不含大契约重开）。

- **建议冻结范围**：§7 的片 1–5（不含片 6）。冻结前置 = D1/D2/D4/D5 的 errata 落盘 + D3 的裁决；片 6 单列。
- **首片**：`FEA-13-BK2-1`（backup/2 写端 + 版本协商 + v1 只读 adapter）。理由：它是所有其余片的格式地基；不依赖任何新内容类别；AC 全部可用「包字节 + typed 错误 + 零副作用」观测；不触碰 Host/UI。
- **首片冻结前必须先有的裁决**：D1（v1 字面值与 D1 的 v2 字面值）。没有它，片 1 的 AC2 会与 C-09 SC-B07 的冻结文字互相矛盾，实现者无论怎么写都会被判「不符」。
- **不建议 `NOT_RECOMMENDED`**：FEA-13 的五片各自边界清晰、依赖已 done、写域与方案 §15.6 一致；卡点全是「文档口径」而非「能力不可达」。
- **不建议 `READY-TO-FREEZE`（当前）**：D3 是真实跨层冲突（外观设置在 `%APPDATA%`，`nmbak` 读不到），若不给裁决就冻结，片 2 会把「外观设置入包」写成不可能达成的 AC。

---

## 9. Q8：门禁只读复核

| 命令 | 结果 |
|---|---|
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（3 warnings），EXIT=0**；warnings = 11 个非终态 Task、STATUS 80%、PLAN 80% |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath 'doc/tasks/FEA-11-HOST-AUTH-3.md'` | **PASS（3 warnings），EXIT=0**（FEA-13 无卡，故用当前非终态候选；**建卡后须重跑**） |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)，EXIT=0**；C09 `dc51226b336c`（与冻结记录 `:16` 一致） |

写入本报告后重新实跑 `check.ps1`：**PASS（3 warnings），EXIT=0**（本文件不属 15 份 current documents）。

---

## 10. 任务前提更正（两条，均有证据）

1. **`src/application/maintenance/nmbak.py` 不存在**。`.nmbak` v1 在 `src/infrastructure/sqlite/nmbak.py`（730 行）；`src/application/maintenance/backup.py` 只有 39 行、是 `BackupLedger` Protocol，**生产 0 实现者**。按任务前提去改 `application/maintenance/nmbak.py` 会找不到文件。
2. **backup wire 不在 M2-C1**。`grep backup\. doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` = 0 命中；backup 面冻结行在 `doc/contracts/V11R_COMMAND_CONTRACT_V1.md:63-66`（C006 `backup_create` / C007 `backup_list` / C008 `backup_restore` / C009 `backup_delete`，协议 minor 3，应用通道）。M2-C1 只承载删除/回收站面（`:1032` 的 `TRASH_RESTORE_LAYER_MISMATCH`）。
3. 附带：任务前提列的 `tests/**/test_*backup*.py` 与 `test_nmbak_startup_backup.py` 全部存在且实跑 41 passed；`tests/storage/test_backup_restore.py`（595 行）测的是**生产死码** `SqliteBackupService`，其「restore 覆盖」断言不能作为 nmbak 的行为证据。

---

## 11. UNKNOWN / 未核实项（缺什么）

| # | 项 | 缺什么 |
|---|---|---|
| U1 | **恢复进行中崩溃后的活库状态** | 无崩溃注入测试；`nmbak` 无 staging DB/commit marker（`nmbak.py:270-326,677-694`），崩溃后是否「原库仍可读」取决于 SQLite backup API 事务回滚语义，**未实测 = UNKNOWN**。L-5 AC③ 不能凭代码推断为满足。 |
| U2 | `plugins/**` 是否应入包 | 冻结表无该行；`plugin_state` 随库入包（`schema.py:582-593`），插件文件在 `<data_root>/plugins`（`core_assembly.py:1928-1932`）→ 恢复后可能悬空。需 DSH 裁决（本 review 不擅自定性为「必须入包」）。 |
| U3 | 外观设置的最终归属 | 取决于 D3 裁决；若选「Host staging」，需要新 wire 字段与 Host 备份桥写域，本 review 未评估其成本。 |
| U4 | 跨机恢复的 DPAPI 语义 | C-15 `:317` 已记「DPAPI CurrentUser 不自动继承授权」；FEA-13 是否要在本线处理跨机，未裁决 = UNKNOWN。 |
| U5 | 真实 Windows 回收站/外部卷 | 与本 scope 无关（FEA-12 口径：隔离 fixture + 模拟路径），未评估。 |
| U6 | `backup.list` 的 Host C# 类型化 | V11R `:264-265` 标 `PARTIAL`（未类型化）；片 3 若要暴露 `database_id` 需同时补 C# 投影类型，属 Host 备份桥写域，可行但须在 allowed_paths 内显式列出。 |

---

## 12. 边界声明

- 本报告是**只读 scope review**，不构成实现授权、不构成任何 Task 释放（`G-DELETE-IMPL` 仍 OPEN，`ADJ-001:129`）、不构成 push 授权、不构成对任何冻结契约的修改。
- 本报告的所有现状判断均有 `file:line` 或本 review 实跑命令支撑；无法实测的项已在 §11 标 `UNKNOWN`，没有把推测写成事实。
- 释放时 `base_commit` 必须由 DSH 按释放时 HEAD 重新固定，**不得沿用** `reviewed_head: 461684432`。
- 唯一写入文件：`doc/reviews/FEA-13-scope-r1.md`。
