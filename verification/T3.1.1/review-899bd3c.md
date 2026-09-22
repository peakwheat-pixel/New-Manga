---
task_id: T3.1.1
reviewer: DeepSeek Harness
author: Antigravity
base_commit: e771179beaa92b7c592a1986a32ffbf1b6302566
reviewed_head: 899bd3c99752ce435da25e41166bafa1c2963abc
decision: approved
---

# Review：T3.1.1 阅读进度与导出历史统一进入 SQLite

本 Review 由 **DeepSeek Harness** 在真实 DSH 运行环境中独立执行，Reviewer 与实现作者
（Antigravity）不同一。**未采用 Codex 内部模拟 Review，未由 Antigravity 或 Codex 自审。**
本文件只审查 `git diff e771179..899bd3c` 范围内的产品代码；Handoff commit
`81c3197` 仅作为交付说明读取，未纳入产品代码审查。

## 执行元数据（实际调用入口 / Reviewer / ID / 时间 / 环境）

| 项 | 实际值 |
|---|---|
| 实际调用入口 | DeepSeek Harness Web GUI `http://127.0.0.1:3080`；在本 DSH 会话内直接下发 T3.1.1 Review 指令 |
| DSH 实现版本 | `@deepseek-ai/dsh` `0.1.6-alpha.2`（`C:\Users\49745\AppData\Roaming\npm\node_modules\@deepseek-ai\dsh`） |
| Reviewer 名称 | DeepSeek Harness（`deepseek/deepseek-v4.1-flash`，非作者） |
| session ID | `session-07d9ad59-edde-4d0e-afc6-491dd34c6bd9` |
| 后台 job ID | `pwsh-1`（focused 套件）、`pwsh-2`（core 套件）；均 `[status: completed, exit code: 0]` |
| 启动时间 | 2026-09-22 21:57:16 (+08:00)（DSH session 目录创建时刻，首个工具调用紧随其后） |
| 结束时间 | 2026-09-22 22:14 前后 (+08:00)（本报告写入完成；末条验证命令 22:09） |
| 时区 | China Standard Time (UTC+08:00) |
| 实际工作目录 | `G:\CODEX\New Manga.worktrees\T3.1.1-deepseek-review-899bd3c`（分支 `agent/deepseek/T3.1.1-review-899bd3c`，HEAD = `899bd3c`，审查开始时 worktree clean） |
| 主仓库 | `G:\CODEX\New Manga`（HEAD `3dc3256`，`master`；未修改，未添加 worktree） |
| 使用的 Python / venv | `G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe` = **Python 3.12.3**；`pytest 9.1.1`。该 venv 为交付报告 [delivery-report.md](delivery-report.md#L9) 声明的环境，本文已独立核验其存在与版本 |
| Base Commit | `e771179beaa92b7c592a1986a32ffbf1b6302566` |
| Delivery Head | `899bd3c99752ce435da25e41166bafa1c2963abc` |
| 被审分支 | `agent/antigravity/T3.1.1-storage-sqlite` |
| Handoff commit（只读） | `81c319705afd2be2abc168414310164acdce9d90`（仅新增 `doc/handoffs/T3.1.1-antigravity-delivery.md` 137 行，无产品代码） |

## 范围与依据

审查绑定命令：

```text
git diff e771179beaa92b7c592a1986a32ffbf1b6302566..899bd3c99752ce435da25e41166bafa1c2963abc
```

变更面 16 个文件（+1860 / −21），全部落在冻结允许范围内：

```text
src/bootstrap/app.py                                     |  22 +-
src/infrastructure/sqlite/__init__.py                    |  28 +-
src/infrastructure/sqlite/reading_export.py              | 535 ++++++
src/infrastructure/sqlite/schema.py                      |  45 ++
tests/core/test_bootstrap.py                             |   2 +-
tests/reading_export/test_sqlite_reading_export.py       | 779 +++++
tests/storage/test_backup_restore.py                     |   4 +-
tests/storage/test_schema_migration.py                   |  31 +-
verification/T3.1.1/{compileall,core,focused-reading-storage,full-suite,probes,smoke-test}.log
verification/T3.1.1/{delivery-report.md,run_probes.py}
```

依据：本 Task [T3.1.1.md](../../doc/tasks/T3.1.1.md)、[release-gate-e771179.md](release-gate-e771179.md)、
D03 §29/§31（[03_DATA_MODEL.md](../../doc/03_DATA_MODEL.md)）、D08 `AC-READ-002`/`AC-EXPORT-002`
（[08_ACCEPTANCE_CRITERIA.md](../../doc/08_ACCEPTANCE_CRITERIA.md)）、[AGENTS.md](../../AGENTS.md)、
[09_COLLABORATION.md](../../doc/09_COLLABORATION.md)、[REBASELINE_PLAN.md](../../doc/REBASELINE_PLAN.md)、
[STATUS.md](../../doc/STATUS.md)。

> **链接可达性注**：`doc/tasks/T3.1.1.md` 与 `verification/T3.1.1/release-gate-e771179.md` 由
> master 治理线引入，**不在** `899bd3c` 的树内（本 Review 通过 `git show master:<path>` 读取）。
> 因此这两条链接在集成目标 `master` / 主工作区上有效，在 delivery head 的 worktree 中不可达；
> 其余引用目标均存在于 `899bd3c`。

**未审到的部分**：QML/UI 渲染、Provider/credential、Pipeline graph/handler、打包与 backup UI
（均不在本 diff 内，且按冻结范围不得修改）；`verification/T3.1.1/full-suite.log` 的全量套件
未由本 Review 重跑（其已知 torch/OpenSSL 环境差异见「限制」）。

**视角状态**：Architecture `executed`；Verification `executed`；Standards `executed`（按本仓库
记录标准：AGENTS.md 允许/禁止范围、09 协作协议、冻结 scope）；Spec `executed`（按 Task AC1–AC7
与 D03 §29/§31 逐条对照）。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-001 | P2 | [delivery-report.md](delivery-report.md#L21) 对 [schema.py](../../src/infrastructure/sqlite/schema.py#L417-L452) 的描述 | 交付报告称 v4 两表「含 UNIQUE 约束、**外键关联、级联删除**」。实际 `reading_progress`/`export_history` 均无任何 `FOREIGN KEY`：`PRAGMA foreign_key_list()` 返回空列表。影响：证据陈述与实现不符（AC6 证据可信度）；由于连接层 `PRAGMA foreign_keys = ON`，孤儿进度行（引用已删除/不存在的 book）不会被数据库阻止，与报告给人的保护印象相反 | 独立探针 `AC1.e`：`reading_progress foreign_key_list=[]; export_history foreign_key_list=[]` | 二选一：(a) 修正交付报告措辞并在 Task 中显式登记「v4 有意不建 FK，以免 legacy 孤儿记录使一次性导入失败」的设计取舍；(b) 若确需 FK，须单独评估 legacy 孤儿数据与级联语义后再补 migration。**不得**只改文字而不登记取舍 | open |
| R-002 | P2 | [reading_export.py](../../src/infrastructure/sqlite/reading_export.py#L308-L352)（progress_id 校验缺失）；[reading_export.py](../../src/infrastructure/sqlite/reading_export.py#L107-L129)（`write` 批内 PID 复用） | legacy JSON 中两条不同 `(book_id, chapter_id, mode)` 记录复用同一 `progress_id` 时，导入在 DB 阶段抛**原生** `sqlite3.IntegrityError: UNIQUE constraint failed: reading_progress.progress_id`，不是 `LegacyImportError` 子类，消息也不含文件名/记录序号。因为该失败在启动路径上且可确定性重放，每次启动都会重抛 → **应用无法启动**（数据安全本身无损）。AC4 要求「抛出明确的 typed exception、错误包含足够上下文」，此处未满足。同一根因也存在于 `SqliteReadingProgressStore.write` 的批内 PID 复用（整批回滚正确，但同样是原生异常） | 独立探针 `AC4.h`：`raises IntegrityError (typed=False); no rows, no marker, file byte-identical, and identical on the next startup`；`AC2.f`：`two rows reusing one progress_id raise IntegrityError and the whole batch rolls back (0 rows)` | 在导入校验阶段按 `progress_id` 去重并抛 `LegacyInvalidRecordError`（错误串带文件路径与记录序号）；`write` 可同样预检键/PID 冲突。**触发条件**：真实旧写入器为每行生成 `rp-<uuid12>`，故正常 legacy 文件不会命中；命中场景为手工编辑或损坏的遗留文件 | open |
| R-003 | P2 | [delivery-report.md](delivery-report.md#L56)、[run_probes.py](run_probes.py#L203-L205) | 交付报告称「Probe 3 与自动化测试**跟踪文件系统**，确认无任何 `.json` 进度/历史文件创建或写入」。实际 Probe 3 只是 `assert not (data_root / "reading_progress.json").exists()` —— 断言文件从未存在，并未监控文件系统写入；对一个从未被创建的文件这是平凡成立。影响：AC6 证据可信度，弱断言被表述为强证据 | 独立探针 `AC3.a` 补做了真正的调用级监控（monkeypatch `os.replace/os.rename/os.remove/os.unlink/os.rmdir`、`shutil.move/rmtree`、`pathlib.Path.write_text/write_bytes/unlink/rename/replace/touch/mkdir/chmod`），导入期间对两个 legacy 文件**零命中**；`AC5.a`/`AC5.d` 亦确认新数据根下无 JSON 文件生成 | 以 Review 的 `AC3.a` 调用级监控证据替换交付报告中的「跟踪文件系统」表述，或由 Codex 在集成证据中补同等强度的断言 | open |
| R-004 | P2 | [reading_export.py](../../src/infrastructure/sqlite/reading_export.py#L84-L137)、[reading_export.py](../../src/infrastructure/sqlite/reading_export.py#L181-L240) | 两个 adapter 采用 document-store 的「读—改—写 + 全量替换 + `DELETE … WHERE id NOT IN (…)`」语义。这与旧 JSON store 行为一致，且生产装配只有一个 `ReadingService`/`ExportService` 实例（[app.py](../../src/bootstrap/app.py#L836-L837)），**不是回归**。但 release gate 提到「事务边界…连接使用真实安全」；跨实例/跨进程并发写会互相删除对方刚新增的行（丢失更新） | 代码审查 `reading_export.py:132-137`、`235-240`；`ExportService._record` 为 read-append-write（[export/service.py](../../src/application/export/service.py#L439-L460)） | 在 Task 中登记为已知并发边界，或后续任务改为「只 upsert、不 DELETE」的增量语义。当前不构成数据破坏：单实例串行下每批都来自完整快照 | open |
| R-005 | P2 | [migrator.py](../../src/infrastructure/sqlite/migrator.py#L82-L85) | `_verify_checksum` 只在迁移处于 pending 时执行；`if migration.schema_version <= current: continue` 跳过了所有已应用迁移。因此**已应用**的 v1/v2/v3 checksum 在后续升级（v3→v4）中不会被复核，checksum 守卫只在「同一迁移再次 pending」时生效。**既有行为，本 diff 未修改 migrator.py**，非 T3.1.1 引入 | 代码审查 `migrator.py:82-85` + 独立探针 `AC1.d`（篡改 v3 checksum 后重跑不报错，因无 pending） | 无需在 T3.1.1 处理；建议登记为后续 migration 加固项（例如无条件复核全部已记录 checksum） | deferred（非本任务） |
| R-006 | P2 | [reading/service.py](../../src/application/reading/service.py#L436-L440)、[export/service.py](../../src/application/export/service.py#L38) | `default_progress_store()` 仍返回 `JsonProgressDocumentStore`；`application/export/service.py` 仍 import `JsonHistoryDocumentStore`。二者**均无生产调用点**（全 `src` grep 确认），因此不违反 AC5；但残留死路径可能误导后续维护者以为 JSON 仍可用 | 独立探针 `AC5.c`：`no bootstrap module instantiates a JSON store`；`grep JsonProgressDocumentStore\|JsonHistoryDocumentStore src` 仅命中定义/导出/死函数 | 后续清理任务中删除该死函数与未用 import；当前不阻断 | deferred（非本任务） |

**在记录范围内未发现**：v1/v2/v3 SQL 被编辑、迁移守卫被削弱、遗留 JSON 被改写/删除、
导入写假 marker、失败留半行数据、QML/Provider/Pipeline/backup UI/依赖被改动、用户源文件
或 Managed Copy 被改动。

## 验证

全部命令在 `G:\CODEX\New Manga.worktrees\T3.1.1-deepseek-review-899bd3c` 下、以
`PYTHONDONTWRITEBYTECODE=1`、`PYTHONPATH=src;.` 与上述 Python 3.12.3 venv 执行，均为本
Review 独立运行（不依赖交付方日志）。

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| AC1 v1/v2/v3 SQL SHA-256 | `python <tmp>\hash_migrations.py`（`git show <rev>:src/infrastructure/sqlite/schema.py` 后对每个 SQL 常量 `sha256(utf-8)`） | base `e771179` vs head `899bd3c` | **PASS** | v1 `f68cb4ab…94bd`、v2 `b984eaee…5d5b`、v3 `359d97f4…a0c2` 在 base/head **逐位相同**；v4 为新增 `c8e0b489…8394`。已注册迁移 checksum 与之一致。EXIT 0 |
| AC1 v4 表结构/主键/UNIQUE/CHECK/索引 | 独立探针 `AC1.a`/`AC1.b`/`AC1.c` | head `899bd3c` | **PASS** | `reading_progress` 11 列精确匹配、PK=`progress_id`、`UNIQUE(book_id,chapter_id,mode)`、`idx_reading_progress_book`；`export_history` 13 列、PK=`export_id`、`idx_export_history_created_at`/`idx_export_history_book`；`mode`/`status` CHECK 经真实插入拒绝非法值；v4 SQL 无 `DROP`/`ALTER`/`UPDATE`/`DELETE` |
| AC1 迁移守卫（checksum/事务回滚/新 Schema 拒绝/迁移前备份） | 独立探针 `AC1.d`/`AC1.f` | head `899bd3c` | **PASS** | 篡改 checksum → `IntegrityError: checksum mismatch`；注入坏 v5 → 回滚至 v4 且无半迁移表；v5 库以 `latest_known=4` 打开 → `state=too_new`、`writable=False`、`apply_pending()` 抛 `SchemaTooNewError`；`SqliteBackupService` 真实 provider 下 4 次 `pre_migration`、`backup_records` 记录 v1/v2/v3 三个快照、磁盘 4 个 `.db` |
| AC2 ReadingProgress 全字段 round-trip | 独立探针 `AC2.a` | head `899bd3c` | **PASS** | 11/11 字段在写入后与**重开数据库**后逐字段相等 |
| AC2 Original/Translated 独立 + Webtoon 字段与时长 | 独立探针 `AC2.b` | head `899bd3c` | **PASS** | original(`p-orig`, y=100.0, 60s) 与 translated(`p-trans`, y=9999.0, 7200s) 互不干扰；webtoon `last_page_id=wt-42`、`scroll_offset_y=12345.75`、`total_read_seconds=42.5` 冷重开后完整还原 |
| AC2 `(book_id, chapter_id, mode)` 不产生重复 | 独立探针 `AC2.c` | head `899bd3c` | **PASS** | 同键连续 3 次写入 → 1 行且为最新值；新增键后 2 行共存 |
| AC2 ExportHistory 全字段 / 4 状态 / 排序 / repeat snapshot | 独立探针 `AC2.d`/`AC2.e` | head `899bd3c` | **PASS** | 13 字段 × completed/skipped/cancelled/failed 逐字段相等；`read()` 返回 `e-4,e-3,e-2,e-1` 新→旧；`ExportService.repeat()` 从持久化 snapshot 重放并追加 SQLite 行，无 JSON 文件 |
| AC3 合法 JSON 首次导入 / 重启不重复 / 文件只读 | 独立探针 `AC3.a` | head `899bd3c` | **PASS** | 各导入 1 条；`sha256`+`mtime_ns`+`size`+`st_ino` 完全不变；目录列表不变；**14 个文件变异入口零命中**；重开连接后重复导入返回 0 且行数不变 |
| AC3 文件缺失 | 独立探针 `AC3.b` | head `899bd3c` | **PASS** | 返回 0、不创建文件、写 `missing_empty` marker |
| AC4 损坏 / 顶层结构 / 单条非法 | 独立探针 `AC4.a`/`AC4.b`/`AC4.c`/`AC4.g` | head `899bd3c` | **PASS** | `LegacyCorruptJsonError`（`__cause__` = `json.JSONDecodeError`，未被吞）、`LegacyInvalidStructureError`、`LegacyInvalidRecordError`（4 个 progress 用例 + 1 个 history 用例）；错误串含文件路径、`Entry 0`、字段名；均无 marker、无行、文件不变 |
| AC4 SQLite 写入失败 / marker 写入失败 / 导入中途失败 | 独立探针 `AC4.d`/`AC4.e`/`AC4.f` | head `899bd3c` | **PASS（含 R-002）** | 三类注入失败均整批回滚：0 行、无 marker、legacy 文件字节不变、原有行保留。异常类型为 `sqlite3.IntegrityError`（见 R-002） |
| AC4 legacy `progress_id` 复用（边界） | 独立探针 `AC4.h`/`AC2.f` | head `899bd3c` | **PASS（暴露 R-002）** | `raises IntegrityError (typed=False)`；无行、无 marker、文件不变、重启确定性重放 |
| AC5 生产装配与零 JSON 真值 | 独立探针 `AC5.a`/`AC5.b`/`AC5.c`/`AC5.d` | head `899bd3c` | **PASS** | `assemble_services` 返回 `SqliteReadingProgressStore`/`SqliteExportHistoryStore`；真实写入在 `library.db` 可见（schema v4）；启动自动导入既有 legacy 行且两个 JSON 文件字节不变；**真实 `ReadingService` 会话**（open→next_page→add_time→close）持久化后冷重启恢复到 `p-2` 且累计时长保留，全程无 JSON 文件；`assemble_engine` 仅注入 viewmodel，不构造 store |
| AC6 探针（交付方脚本，独立复跑） | `python verification/T3.1.1/run_probes.py` | head `899bd3c` | **PASS** | 4/4 Probe 通过，`ALL T3.1.1 PROBES PASSED.`，EXIT 0 |
| AC6 针对性测试套件 | `pytest tests/reading_export tests/storage -q` | head `899bd3c` | **PASS** | **220 passed in 27.97s**，EXIT 0（与交付方 220 passed 一致，耗时不同口径：交付 26.09s） |
| AC6 Core 套件 | `pytest tests/core -q` | head `899bd3c` | **PASS** | **49 passed in 7.94s**，EXIT 0（交付方 49 passed / 6.56s） |
| AC6 字节码编译 | `python -m compileall -q src tests` | head `899bd3c` | **PASS** | EXIT 0，无输出 |
| AC6 Bootstrap 冒烟（隔离 data root） | `python -m bootstrap.app --smoke-test --data-root <temp>` | head `899bd3c` | **PASS** | EXIT 0；数据根生成 `library.db`（`schema_version=4`、两 v4 表存在、`legacy_*_imported` + `schema_version` metadata）与 `managed/`，**无任何 `.json` 真值文件**；路径走真实 `assemble_services` + `assemble_engine`（[app.py](../../src/bootstrap/app.py#L1122-L1125)） |
| 允许路径与禁止范围 | `git diff --name-only e771179..899bd3c` + 独立探针 `AC7` | head `899bd3c` | **PASS** | 16 个文件全部落在 `src/infrastructure/sqlite/`、`src/bootstrap/app.py`、`tests/{reading_export,storage,core}/`、`verification/T3.1.1/`；**无** `.qml`/`.qmldir`、**无**依赖文件（requirements/pyproject/lock）、**无** settings/provider/pipeline 目录改动 |
| 空白/格式门 | `git diff --check e771179..899bd3c` | head `899bd3c` | **FAIL（R-003 同类，见下）** | EXIT **2**：`delivery-report.md:3-8` 行尾空白、`core.log:8` 与 `focused-reading-storage.log:11` 末尾多余空行。**全部位于 `verification/**` 证据文件；`src/` 与 `tests/` 无空白问题** |
| 全量回归套件 | `pytest tests -q -p no:cacheprovider -rs` | head `899bd3c` | **NOT_RUN（本 Review 未重跑）** | 依赖交付方 [full-suite.log](full-suite.log)（1229 passed / 6 skipped / 1 known failure = torch 缺失）。release gate 已记录该环境限制为基线既有 |

### Architecture 面结论

`executed`，**无 P0/P1**。分层方向正确：SQLite adapter 落在 `src/infrastructure/sqlite/`，
应用层 `ProgressDocumentStore`/`HistoryDocumentStore` 协议**未被修改**（`src/application/**` 零改动），
业务语义未扩散；一次性导入只在 composition root（[app.py](../../src/bootstrap/app.py#L830-L837)）
发生；`with conn:` 经 [ThreadRoutedConnection](../../src/infrastructure/sqlite/connection.py#L291-L295)
正确路由到调用线程的真实连接，事务语义真实有效。v4 是纯 additive migration，v1/v2/v3 逐字节未变。
`PRAGMA foreign_keys = ON` 已启用，但 v4 未声明 FK（R-001）。并发丢失更新边界见 R-004。

### Verification 面结论

`executed`，**关键验证齐备且可复现**：迁移、round-trip、唯一性、只读保护、异常诊断、
故障回滚、生产装配均有本 Review 亲自运行的判别性证据。测试**不是**只证明 fake store：AC5 测试
走真实 `assemble_services` 并断言 SQLite 中的实际行与 JSON 文件 mtime 不变；AC6 测试注入真实
SQLite 触发器失败。唯一未由本 Review 重跑的是全量套件（已知环境限制）。

### Standards / Spec 面结论

`executed`。允许/禁止路径全部合规（见上表最后两行 `PASS`）；AC1/AC2/AC3/AC5 完整满足，
AC4 的 malformed-JSON 三分支 typed 异常完整满足，DB 层异常的 typed/上下文要求见 R-002；
AC6 的「证据可信度」存在 R-001/R-003 两处陈述强于实际。**无 scope creep**，无未授权共享契约修改。

## 结论与复审

**decision: `approved`** —— reviewed_head `899bd3c99752ce435da25e41166bafa1c2963abc` 可交 Codex 集成。

理由：

- **P0 / P1 阻断项 = 0**；本 Review 的 27 项独立检查全部通过，交付方 4 项 Probe 与
  focused/core/compileall/smoke 全部独立复现为 PASS。
- 本任务的风险核心——**遗留 JSON 只读保护、导入幂等、失败原子性、生产写入真值切换**——
  均以判别性证据确认：文件 hash/mtime/inode/目录列表不变且调用级零变异；失败无假 marker、
  无半行、不动源文件；生产装配确以 SQLite 为唯一写入真值且真实 `ReadingService` 会话冷重启可恢复。
- R-001/R-003 是**证据陈述与实现不符**（P2），R-002 是**边界健壮性与诊断类型**（P2），
  均不破坏已交付的数据正确性。

交 Codex 集成时的建议与升级条件：

1. 请 Codex 在集成记录中**修正 R-001/R-003 的措辞**，或在 Task 中显式登记「v4 有意不建 FK」
   与「Probe 3 为平凡存在性断言」两项取舍。
2. R-002 建议返修（导入前按 `progress_id` 去重 → `LegacyInvalidRecordError`）。**若 Codex 或用户
   认定 AC4 的「typed exception」要求对本场景是硬性 P1，则 R-002 须升级为 P1 并先返修、再复审**；
   本文按「实际旧写入器不会产生重复 progress_id、且数据安全无损」判定为 P2 不阻断。
3. R-004/R-005/R-006 建议作为后续任务登记，不在本 Task 扩大范围。

**剩余风险**：全量套件（含 torch/OpenSSL 环境差异）未由本 Review 重跑，集成后由 Codex 记录；
`verification/**` 证据文件未通过 `git diff --check`（仅空白问题），集成前宜一并清理。

**复审规则**：若 Antigravity 按 R-001/R-002/R-003 产出新 head，本 Review 追加新 head 与对应
findings disposition，不抹掉本记录；集成后测试由 Codex 另行记录。

## 附：本 Review 产出的独立证据脚本

- [review-probes-899bd3c.py](review-probes-899bd3c.py) —— 27 项独立检查，覆盖 AC1–AC5 与允许路径，
  与本 Review 同源；`python verification/T3.1.1/review-probes-899bd3c.py` → EXIT 0。
  该文件是**审查产物**，不是 Antigravity 的交付内容。
