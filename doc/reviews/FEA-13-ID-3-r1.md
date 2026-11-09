---
task_id: FEA-13-ID-3
reviewer: DSH 独立上下文子 agent（parent `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`）
reviewer_kind: subagent
author: dsh
base_commit: 54453abb3
reviewed_head: 9867e48ed
implementation_head: 3d8b5507e
decision: changes_requested
---

# Review：FEA-13-ID-3（DatabaseId 原语 + manifest/恢复过滤 + backup.list 投影）

## 范围与依据

- 只读审查；本次唯一写入文件为本报告。未改生产源码/测试/契约，未 commit/push。
- 被审实现 `3d8b5507e`（父提交 `54453abb3`）；`reviewed_head: 9867e48ed` 仅追加 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、Task 卡状态与 Handoff，代码面无差异（`git diff --stat 3d8b5507e..9867e48ed` = 5 个文档）。
- 依据：C-01b **SC-18**（`FEA-C01b_STORAGE_CONTRACT_DRAFT.md:67`，「首次写 metadata 生成 UUID，旧库由迁移第一笔原子回填；回填前身份 unknown，不得以书名或 hash 代替」）、`doc/reviews/FEA-13-scope-r1.md:238-248`（§7 片 3）、`ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT.md:25`、Task 卡 `doc/tasks/FEA-13-ID-3.md`。
- 未审到：全量 `dotnet test`；`tests/storage` 全量（环境约束，按卡只跑备份面）；真实用户库/真实多进程并发。

### 视角状态

- **Architecture**：`executed`（分层、事务/原子性、恢复零副作用、契约边界）。
- **Verification**：`executed`（实跑 6 项门禁 + 4 个 EV hash 复核）。
- **Spec**（可选）：`executed`（AC1–AC6 逐条对照卡 + scope）。
- **Standards**（可选）：`N/A`（无仓库级编码标准冲突，工具已强制项跳过）。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | **P2** | `src/bootstrap/core_assembly.py:172-182`（`_NmbakMigrationBackup.create_backup`）；`src/infrastructure/sqlite/nmbak.py:263-266,708-719` | pre-migration 备份构造 `NmbakBackupService` 时**未传 `database_id_reader`**，故 **每个 `pre_migration` v2 包恒写 `"database_id": null`**，即使 `application_metadata.database_id` 已存在（除首次启动外的每次升级都如此）。影响：①Task 卡 AC3 字面「v2 包 `database_id` 与库一致」对迁移包不成立；②该类包绕过跨库门禁（null=unknown 一律放行）；③链式风险：把 A 库的 pre_migration 包恢复到 B 库被放行，包内 DB 携带 A 的身份 → 覆盖后当前身份=A；若该次 restore 中途失败（`nmbak.py:404-406` 注释确认「DB 已覆盖」），文档指定的回滚点 `pre_restore` 包（manifest=B）会被新门禁判为 mismatch 而**拒绝回滚**；④`core_assembly.py:1200-1203` 注释「pre-migration hook 因此如实报告 unknown」只在首次启动成立，重复启动时是**假陈述** | 代码走查 + `nmbak.py` 构造点：`database_id_reader` 默认 `None` → `_current_database_id()` 返回 `None`；全仓 `NmbakBackupService(` 仅 2 处，测试只覆盖传 reader 的路径 | 一行修复：在 `_NmbakMigrationBackup` 构造处传 `database_id_reader=lambda: read_database_id(conn)`；补 1 例「已有身份时 `pre_migration` 包携带该身份」的测试；同步修正 `:1200-1203` 注释。若 DSH 决定「pre_migration 包身份恒为 unknown」为有意口径，则须在卡内显式裁决并改写 AC3 与注释 | open |
| R-002 | P3 | `src/infrastructure/sqlite/nmbak.py:355-367` | 门禁只读 manifest 字段，manifest 本身不被任何摘要/签名覆盖（`_verify_package` 只校验 `database_sha256` 与逐文件 sha256，`:827-868`），故手工把 `database_id` 改成 `null` 即可静默关闭门禁；且比较用**未 strip 的 manifest 值** vs **已 strip 的当前值**，带空白/纯空白的 manifest 值会误判为 mismatch | 代码走查；`_current_database_id()`（`:711-719`）strip，而 `:356-361` 未 strip | 归一化两侧（`str(value).strip()`）；如需更强保证，可追加「包内 DB 的 `application_metadata.database_id` 与 manifest 一致」校验。属纵深防御，不阻断本片 | open |
| R-003 | P3 | `src/bootstrap/core_assembly.py:1204,1214-1220` | `database_id = ensure_database_id(conn)` 的返回值**未被使用**（无日志、无返回）；既有日志仍打「this session performed no write」，对旧库回填场景为**假**；`:1195-1199` 注释「schema bootstrap 是只读会话唯一写操作」同样已失真。可观测性不一致，不影响功能 | 代码走查：`database_id` 后续 0 引用；`applied` 为空时走 else 分支打印该句 | 打印身份（或至少回填事件）并修正注释/日志；或把返回值用于任何必须的装配期断言 | open |
| R-004 | P3 | `src/infrastructure/sqlite/identity.py:44-62` | `ensure_database_id` 用 `with conn:` 提交**调用方连接**，文档未声明「不得在调用方事务内调用」。当前装配点（`apply_pending` 之后，`migrator.py:270` 已 commit）安全，但 scope r1 `:243` 的原意是「迁移第一笔事务内回填」；若后续片按该语义在迁移事务中调用，会**提前提交**迁移事务。另：`read_database_id` 把损坏/非字符串值映射为 `None`（unknown），会静默关闭该库的跨库门禁而非暴露损坏 | 代码走查 + `migrator.py:227-272`（每个迁移 `BEGIN IMMEDIATE`/`commit`） | 二选一：改用 `SAVEPOINT`/不自持提交，或在 docstring 明确「必须在无活跃事务时调用」，并在片 6 回填实现时遵守；损坏身份建议留一条可诊断日志 | open |
| R-005 | P3 | `tests/storage/test_nmbak_identity.py`；`apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs:44,1634` | 证据缺口：①无「真实 v1 包（无 `database_id` 键）经门禁读作 unknown 并放行」的显式断言（仅靠代码可推）；②无 `backup.list` 对 v1/legacy 包返回 `null` 的断言；③C# 侧无解析测试，`dotnet build` 只证明编译，**未执行** `ParseBackupPackage` 的 null 保持语义；④「schema 仍 v9」与并发幂等为间接覆盖（`ensure` 两次顺序调用，非并发）；⑤V11R `backup.list` wire 行（`V11R_COMMAND_CONTRACT_V1.md:63-66`）未同步新字段（README 已自述，卡 AC5 未要求） | 测试文件通读；`ReadString` 实现 `:1733-1736` 语义正确（非 String → null），但无测试触达 | 至少补 ① 与 ③（1 个 Python 例 + 1 个 C# 单测）；②④可留后续；⑤按需另案 | open |

无 P0 / P1。P2 仅 R-001，且为单文件一行修复。

## Acceptance Criteria 判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 原子写入/幂等 | **MET** | `identity.py:44-62`：`INSERT OR IGNORE`（`metadata_key` 为 PK，`schema.py:128-132`）+ 回读；重复调用返回同值；无新 DDL，`default_migrations()` 最大值仍 **9**。EXIT 0（41 passed） |
| AC2 旧库回填 | **MET** | 无行时 `read_database_id`→`None`（非空串/书名/hash）；`ensure` 恰好写入 1 行；`test_legacy_library_backfills_only_on_ensure` 断言通过。注：回填位置为「装配后」而非 scope r1 字面「迁移第一笔事务内」，与 Task 卡实现口径一致（见 R-004） |
| AC3 manifest 携带 | **PARTIAL** | 主 `create` 路径正确（reader 懒读、unknown→null、`list` 从 manifest 取）；v1 无字段→`None` 成立。但 `pre_migration` 路径恒 null 且注释失真 → **R-001** |
| AC4 跨库 restore 拒绝 | **MET**（含 R-001/R-002 限定） | 门禁在 `_verify_package` 之后、`create("pre_restore")` 之前（`nmbak.py:355-370`），双方均已知且不等才拒绝；`BACKUP_DATABASE_MISMATCH` 映射 `("conflict", False)`（`core_service.py:450`）；测试断言 typed 码、无 `pre_restore`、包字节不变、DB/managed 未写。变异证据 RED（EXIT 1，1 failed/5 passed）判别力成立 |
| AC5 list 投影 | **MET**（证据 R-005） | `nmbak.py:214` 每项含 `database_id`；`handle_backup_list` 直通（`core_service.py:3165-3166`）；C# `BackupPackageInfo.DatabaseId? = null` + `ReadString`（`CoreServiceClient.cs:44,1634,1733-1736`），旧构造点因默认参数兼容；Host 仅转发同一类型，无需改 `HostRuntime.cs`。build 0/0 |
| AC6 门禁 | **MET** | 见下表 6 项 EXIT 全 0；实现提交 diff 11 文件 ⊆ `allowed_paths`；`9867e48ed` 另改 `STATUS`/`REBASELINE_PLAN`/`TASK_LEDGER`（Integrator 生命周期记账，非实现面，仅记录不计 finding） |

## 验证

| 场景 | 命令或步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 定向 pytest（卡要求 4 文件） | `python -m pytest tests/storage/test_nmbak_identity.py tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_format.py tests/storage/test_nmbak_coverage.py -q` | Windows / Python 3.14 / `9867e48ed`（代码同 `3d8b5507e`） | **PASS**，`41 passed in 6.04s`，**EXIT 0** | 本 Review 实跑 |
| 相邻备份面补充 | `python -m pytest tests/storage/test_backup_restore.py tests/core/test_core_backup_wire.py tests/infrastructure/test_nmbak_startup_backup.py -q` | 同上 | **PASS**，`39 passed in 5.35s`，**EXIT 0**（与 EV 的 80 例合计一致：41+39=80） | 本 Review 实跑 |
| C# 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Debug --nologo` | 同上 | **PASS**，`0 个警告 / 0 个错误`，**EXIT 0** | 本 Review 实跑 |
| `check.ps1 -TaskPath` | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-13-ID-3.md` | 同上 | **PASS**（3 warnings），**EXIT 0** | 本 Review 实跑 |
| `check.ps1`（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | 同上 | **PASS**（3 warnings），**EXIT 0** | 本 Review 实跑 |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 同上 | **PASS**，`PIN AUDIT: PASS (all 18)`，**EXIT 0** | 本 Review 实跑 |
| EV 字节一致性 | 4 个 `Get-FileHash -Algorithm SHA256` 对照 Task 卡 | 同上 | **PASS，4/4 MATCH**（README `b2dfe961…`、suite `db2682d3…`、mutation `6fcc5b0c…`、build `a1f492e5…`） | 本 Review 实跑 |
| 证据日志自洽 | 读 `logs/pytest-backup-suite.log`、`logs/mutation-db-gate.log` | 同上 | PASS：suite 头 `EXIT=0` + `80 passed`；变异头 `EXIT=1` + 1 failed（关闭门禁后唯一红），与卡一致 | 本 Review 复读 |
| 全量 `dotnet test` / `tests/storage` 全量 | — | — | **NOT_RUN**（卡与 Handoff 已声明环境/口径限制；本片 C# 仅 DTO+解析，由 build 与本 Review 代码走查覆盖） | — |

## 结论与复审

- **Architecture**：分层正确（原语在 `infrastructure/sqlite/identity.py`，身份读取以回调注入 nmbak，装配在 bootstrap），无新 DDL、不动 18 pins 与 C-01b/C-09 字节；恢复门禁位置保证零副作用，typed 错误映射符合 DSH 裁决（`conflict`、非 retryable）。唯一结构性缺口是 R-001 的迁移包身份未接线。
- **Verification**：6 项门禁全部实跑 EXIT 0，EV 4/4 字节一致，变异证据具备判别力。AC1/2/4/5/6 MET，**AC3 PARTIAL**。
- **决定：`changes_requested`（不批准当前 head 交集成）**。阻塞项仅为 **R-001（P2）**，修复面为 `core_assembly.py` 一行 + 1 个测试 + 1 处注释，仍在本片 `allowed_paths` 内；R-002/R-003/R-004/R-005 可与返修同批处置或由 DSH 显式 defer。
- 复审口径：返修补提交后以新 head 重审 R-001 与 AC3，重跑上表 6 项门禁；若 DSH 裁决「pre_migration 包身份恒 unknown」为有意口径，则须改写 Task 卡 AC3/实现口径与 `core_assembly.py:1200-1203` 注释，本 P2 可转为 deferred。
