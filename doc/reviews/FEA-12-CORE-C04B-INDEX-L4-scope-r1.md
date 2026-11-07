---
task: FEA-12-CORE-C04B-INDEX-L4
title: C-04b L-4（media_artifacts.book_id 索引）scope review（r1）
reviewer: fresh subagent（独立上下文）
session: session-3ac1953a-094e-4339-889a-284df2b7b34d
reviewer_kind: 独立 scope review（fresh context / 只读 / 未参与 C-04b、RESIDUAL-1/2/3 的实现或复核，未参与 C-15/C-17 契约起草）
date: 2026-11-08
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 02c1a26d1
reviewed_head_note: 评审开始与结束均为 `02c1a26d1`；`origin/main` 同为 `02c1a26d1`（AHEAD=0 / BEHIND=0），工作树 clean。评审期间无并发写入。
verdict: recommended
verdict_scope: 推荐**一张** implementation 小卡（`FEA-12-CORE-C04B-INDEX-L4-1`，**0 pin / 无 UNFREEZE**）：v9 append-only 迁移 `CREATE INDEX idx_media_artifacts_book ON media_artifacts(book_id)`；优先级 **P3（不紧急）**，但它排在 B2（无消费者）之前，且若另有 schema 卡要 bump v9 应合并。**不推荐**现在走 C-15 UNFREEZE，也**不推荐**只登记不实施。
---

# C-04b L-4（`media_artifacts.book_id` 索引）：scope review（r1）

> 只读 scope review。我未参与 `FEA-12-CORE`、`FEA-12-CORE-C04B-RESIDUAL-1/2/3` 的任何实现、返修或复核，也未参与 C-15/C-17/C-16 契约起草。本次**未修改**生产代码、测试、契约、卡面或冻结记录；**未** `git add`/`commit`/`push`。本文件是本次唯一写入仓库的文件；临时脚本、临时 SQLite 库与运行日志在仓外 `G:\CODEX\New Manga.workspace\C04B-RESIDUAL\index-scope\`。
> **本报告不声称索引已加、性能已修复、L-4 已关闭**。它只回答：这条登记是否成立、加索引是否触碰冻结字节、正确迁移形状是什么、值多少、成本多少、值不值得现在做、以什么卡面做。

## 0. 结论先行

1. **L-4 成立，且性质比登记文字更精确**：R-1 修复（`25dc1523c`，`library.py:1199` 改为 `WHERE ma.book_id = ?`）没有让"每本书变慢"固定下来，而是让**单本书的成本与全库 `media_artifacts` 总量成正比**。我用生产 `default_migrations()` 建 v8 库、直接调用发布方法 `SqliteLibraryRepository.list_book_artifact_current_pointers` 复现：**每本 300 artifacts 的书**在 6,000 行库中 0.50 ms/书，在 60,000 行库中 **5.94 ms/书（11.8×）**；同一本书用旧谓词则是 0.42 → 0.50 ms（1.19×）。这是"全库放大"，不是"本书变重"。
2. **契约判定：0 pin，不需要 C-15 UNFREEZE**。C-15 的冻结字节是 **v7 迁移的规范 DDL 块**（`FEA-C15_SOURCE_STORAGE_DRAFT.md:54` 起、`:56-196`），`media_artifacts` 根本不在该块内；C-15 `:50` 的"以 v8+ 追加"只针对它预留的两张同步表（由 C-17 在 v8 落地）；C-15 `:343`（§8）与冻结记录 `:56` 明确"不冻结 FEA-11/12/13 结构"。18 pin 只映射 18 份契约文档（`tools/governance/verify_pins.ps1` 的映射表），**不含 `schema.py`**。因此加索引是**实现细则 + 新迁移版本**，不需要改任何冻结字节。
3. **迁移形状（唯一正确形状）**：新增 `SCHEMA_VERSION_V9 = 9` / `MIGRATION_V9_NAME` / `MIGRATION_V9_SQL`（单条 `CREATE INDEX`）并追加到 `default_migrations()`（`schema.py:841-851`）。**不得**编辑 v1–v8 的 SQL/name（`Migration.checksum` 是 SQL 的 sha256，`schema.py:562-564`；运行器会按 `schema_migrations` 逐版本比对，`migrator.py:203-218`）。幂等由"版本门"提供（`migrator.py:161-163` 跳过已应用版本），不靠 `CREATE INDEX IF NOT EXISTS`。旧库升级失败自动回滚、DB 停在 v8（`migrator.py:227-276`），启动 typed 失败；旧二进制打开 v9 仍自动 `SchemaTooNewError` / `TOO_NEW`（`migrator.py:156-159`、`connection.py:358-363`），C-01b SC-19 不被破坏。
4. **收益（实测，可复核）**：索引把 `SCAN ma` 恢复为 `SEARCH ma USING INDEX idx_media_artifacts_book`，并把"全库放大"项消掉——同一本 300 artifacts 的书在 60k 库中从 5.68 ms 回到 **0.376 ms**（与 6k 库的 0.347 ms 基本持平）。厚数据集（20 书 × 3,000 artifacts）批量 20 书从 **178.1 ms → 87.3 ms**；同时把删除面 4 处全表扫描（`book_delete_inventory` 计数 `library.py:1549-1551`、`list_book_artifact_revision_ids:1232-1239`、pinned `:1252-1254`、`DELETE FROM media_artifacts WHERE book_id = ?` `:1940`）从 `SCAN` 变为 `SEARCH`（其中 DELETE/COUNT 走覆盖索引）。
5. **但它不是"恢复到修复前"**：加索引后新谓词仍是 60k 厚数据集 4.36 ms/书（旧谓词 2.85 ms/书），因为新谓词必须从 `media_artifacts` 驱动 + 对 7 键 `ORDER BY` 做临时排序。索引解决的是**扫描放大**，不是全部差值。
6. **成本**：`schema.py` 约 8 行 + 1 个新迁移测试 + **5 处硬编码 v8 断言**（4 处 pytest、1 处 .NET）+ 卡/证据，约 6 个文件、跨 Python 与 C# 两种测试。索引本身 1 行；**成本主要在版本号与断言的同步**，所以它必须是一张独立的 schema 卡，不能"顺手"塞进别的实现卡（`doc/plan/FEA-11_IMPL_PREREQS.md:18` 的同条纪律）。
7. **风险低**：索引体积 60k 行 ≈ **754 KB**（12.5 B/行）；2,000 行插入的写放大测不出（38.9 vs 37.1 ms，噪声级）；`CREATE INDEX` 在 60k 行上 29–33 ms，一次性；无需 `ANALYZE`（计划已选中索引，无竞争索引）。
8. **判定 `recommended`（P3，不紧急）**：值得做，理由是"删除事务内的全表扫描随库增长"比"preview 多 90 ms"更值得消除；但不是用户可见缺陷，绝对量级小（60k artifacts 才到百毫秒级），因此**不建议插队**，也不建议为它单开 UNFREEZE 或改任何契约。若未来有别的卡必须 bump v9，应把这条索引并进去，避免两次版本 bump。

## 1. 核对范围与方法

**已读（只读）**
- 迁移机制：`src/infrastructure/sqlite/schema.py`（全文 851 行：版本常量 `:24-37`、v1 DDL 与索引 `:41-154`、`media_artifacts` 块 `:71-86`、`Migration` 数据类与 `checksum` `:556-564`、v6/v7/v8 SQL `:567-838`、`default_migrations()` `:841-851`）、`src/infrastructure/sqlite/migrator.py`（全文 691 行：`apply_pending` `:148-179`、`_verify_checksum` `:203-218`、`_apply_one` `:220-284`、v7 validator 接线 `:236-252`）、`src/infrastructure/sqlite/connection.py`（`:324-364` schema 门）、`src/infrastructure/sqlite/backup.py`（`:183-227` 备份校验/旧备份升级）、`src/infrastructure/sqlite/nmbak.py`（`:678-694` 恢复后升级）、`src/bootstrap/core_assembly.py`（`:1110-1127` v7 validator 选择、`:1162-1200` 迁移装配与备份 hook）。
- 查询与调用面：`src/infrastructure/sqlite/library.py`（`list_book_artifact_current_pointers` `:1178-1204`、唯一调用点 `:1531`、`book_delete_inventory` 计数 `:1549-1551`、`list_book_artifact_revision_ids` `:1232-1239`、`list_book_pinned_revision_ids` `:1252-1254`、删除事务 `:1920-1940`）。
- 契约：`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md`（v1.5 全文 354 行）、`doc/plan/FEA-CONTRACT-FROZEN-C15.md`、`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md:36`、`doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md`（SC-19 `:68`、迁移方向 `:60`）、`doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md`（§0 第 1 条、§2.1）、`doc/plan/FEA-CONTRACT-FROZEN-C04b.md`（§4A `:116-146`）、`doc/plan/FEA-C07_API_INVENTORY.md`、`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（仅按 `schema_version`/索引关键词检索）。
- 测试与工具：`tests/fea09/test_v7_migration.py`、`tests/fea11/test_v8_migration.py`、`tests/fea11/test_source_gate_unify.py:213`、`tests/fea11/test_source_sync.py:993`、`tests/storage/test_schema_migration.py`、`tests/fea11/support/ipc_seed.py:88-96`、`apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11SourceIpcTests.cs:60`、`tools/governance/verify_pins.ps1`、`tools/generate_api_inventory.py`。
- 登记来源：`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-3-r1.md:163`（R3-002 原始实测）、`doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md:130-131`、`doc/STATUS.md:7`（"索引卡 L-4 待 scope review"）。

**实跑**（全部用仓外临时库，**未打开真实用户 DB**）：见 §3.1 命令；`verify_pins.ps1`、`check.ps1`、`generate_api_inventory.py --check` 见 §7.3。
**未跑**（如实声明）：全量 `pytest tests`、全量 .NET、`dotnet build`、真机/真实用户库升级演练、并发写压测。测试基线采信 STATUS `:20` 的 pytest 3369/10、.NET 1683/0/96。

## 2. 契约与治理判定

### 2.1 C-15 冻结字节到底冻了什么

| 条款 | 原文（要点） | 对本议题的含义 |
|---|---|---|
| `FEA-C15_SOURCE_STORAGE_DRAFT.md:33-35` | §1：新增 `v7__source_storage`，`SCHEMA_VERSION_V7=7`、`MIGRATION_V7_NAME/SQL` 追加到 `default_migrations()`；v1–v6 字节不变 | 冻结对象是 **v7 这一个版本**；v1–v6 只被要求"不变"，未被本契约重述内容 |
| `:50` | "预留：`source_sync_plans`、`source_operations` 不在 v7 创建；FEA-11/FEA-12 前置契约以 v8+ 追加" | 句子主语是**这两张表**；它没有说"任何 v8+ 迁移都要有契约" |
| `:52-54` | §2："以下 SQL 为冻结对象；实现必须逐字落在 `MIGRATION_V7_SQL`" | 冻结字节 = 紧随其后的 DDL 块 |
| `:56-196` | 冻结块内容：`pages` 加列、`sources`、`source_locations`、`source_versions`、`source_entries`、`page_bindings`、`rendition_cache` | **`media_artifacts` 不在其中**；该块内没有任何索引涉及 `media_artifacts` |
| `:343` | §8："不冻结 `source_sync_plans`/`source_operations`、FEA-11/12/13 结构" | 再次排除本表的契约归属 |
| `FEA-CONTRACT-FROZEN-C15.md:14-20` | 冻结字节 = 上述文件 v1.5 的 sha256/`git hash-object`；"条款字节自本记录起不得改动；修订须走 UNFREEZE 载体 + 重新独立复核 + 重新冻结" | 只有**改动这些条款字节**才触发 UNFREEZE；加一个索引不改动任何一行 |
| `FEA-CONTRACT_FREEZE_MATRIX.md:36` | C-15 行：冻结对象 = "DDL/迁移/完整性-可见性/Registry/跨存储次序/根级不可用拆分"，pin 条件 18/18 | 同上；"DDL" 指 v7 的规范 DDL |

### 2.2 其它契约是否冻结 `media_artifacts` 的索引集合

| 契约 | 是否规定 | 结论 |
|---|---|---|
| C-01b（存储契约，pin #1） | 只冻结迁移**方向**与不变量：SC-19 旧二进制拒写（`:68`）、§2.4 迁移方向（`:60`）、SC-37 回退（`:106`）；全文 `grep 索引/index/DDL` 无 `media_artifacts` 索引条目 | 不冻结索引集合；v9 反而**加强** SC-19（旧端认识 8，见到 9 必拒） |
| C-04b（删除协议，pin #4） | 冻结的是**成员谓词**与 DTO/摘要规则（§0 第 1 条、§2.1）；v1.2 明确"不改规则/字段名/错误码/语义" | 加索引不改变任何谓词；行集与顺序实测不变（§3.3） |
| C-05 v1.2（可见性，pin #5） | 只引用 `media_artifacts` 的列（`:22`）与 `a.page_id` join（`:131`） | 不涉及索引 |
| C-07（API 清单，pin #7） | 全文无 `schema_version`、无表/索引条目 | 无接口变更 |
| C-16 v1.7 / M2-C1 rev 2.15 | 全文无 `schema_version` 字面值；wire 字段/命令/能力/错误闭集与 schema 无关 | 无 wire 变更 |
| `FEA-C11_IMPL_PREREQS.md:18` | "L-1/L-2 涉及的 **schema 与 wire 字节修订**本身属'新增/修改共享契约'，须走 `CONTRACT-UNFREEZE-*` 或新建契约，不得在实现 Task 内顺手改" | 约束的是**修订已冻结 DDL 字节**（四张 Source 表），不是"在旧表上加索引"；但它确立了同一条纪律：**schema 变更必须有自己的卡与 DSH 冻结范围** |

**反向核查（是否漏了"任何 DDL 变更须 UNFREEZE"的明文）**：在 `doc/**` 全库检索 `additive index`、`索引.*UNFREEZE`、`UNFREEZE.*(DDL|schema|迁移)` 共 32 命中，**没有任何一处**说"新增索引须 UNFREEZE"，也没有"additive index 允许"的成文豁免。项目实际口径是：**改冻结字节 → UNFREEZE；改 schema 形状/语义 → 走契约（如 C-17 立 v8）或独立卡；纯性能索引 → 实现卡**。旁证：`PLUGIN-RUNTIME-1` 在 FEA 契约线之外以自身冻结设计（`doc/design/SETTINGS_SECTION_C_SCHEMAS.md` §4.1-§4.4）落了 v6 两张表与索引，未动任何 pin。

### 2.3 判定：**0 pin**

- 不修改任何冻结契约字节 → 18/18 pin 不动（实测见 §7.3）。
- 不改 v1–v8 任何迁移语句/名称 → 既有库的 `schema_migrations.checksum` 全部仍然匹配（`migrator.py:203-218`）。
- 不加表/列/约束/枚举值、不改任何谓词、不加命令/能力/错误码/`PROTOCOL_MINOR`（`core_service.py:320` 保持 3）。
- 旧二进制拒写语义保持（C-01b SC-19），旧备份可恢复（`backup.py:219-220`、`nmbak.py:684-686` 会把 v8 备份升到 v9）。
- **仍须**：DSH 在卡面冻结范围（`allowed_paths`），因为这是 schema 变更；这与"0 pin"不矛盾。

**若 DSH 反判为 1/18 pin（C-15 UNFREEZE）**，载体要求是：`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`（触发/授权、精确 diff、影响面、回退 sha）+ 独立 byte-level 复核（P0/P1=0）+ 重冻 + 重算 pin；最小 diff 只能在 C-15 里新增一条"v9 索引属实现细则、不需要契约"的说明——**这本身就是把实现细则写进契约，收益为负**。本报告**不推荐**该路径。

### 2.4 迁移机制事实（加索引的正确形状）

| 事实 | 文件:行 | 对卡面的约束 |
|---|---|---|
| 版本常量与 `MIGRATIONS` 元组 | `schema.py:24-37`、`:557-564`、`:841-851` | 追加 `SCHEMA_VERSION_V9=9` + `MIGRATION_V9_NAME` + `MIGRATION_V9_SQL` + 1 元组项 |
| `checksum = sha256(sql)` | `schema.py:562-564` | v9 的 SQL 一旦被应用就不能再改；改则校验失败（`migrator.py:214-218`） |
| 每版本一个事务（`BEGIN IMMEDIATE`），失败 `rollback` | `migrator.py:227-276` | `CREATE INDEX` 与 `schema_migrations` 插入同事务 → **要么 9 且索引在，要么 8 且无索引残留** |
| 版本门即幂等 | `migrator.py:161-163` | 不需要 `IF NOT EXISTS`；重复启动只跳过 |
| 更新 `application_metadata.schema_version` | `migrator.py:263-269` | v9 后两处记录一致（既有契约测试会校验双源） |
| 迁移前备份 hook | `migrator.py:165-172`；`core_assembly.py:1174-1181` | 生产路径每次升级前已建 `pre_migration` 备份 |
| 旧端拒写 | `migrator.py:156-159`、`connection.py:358-363` | 只认识 8 的二进制打开 v9 → `SchemaTooNewError`/`TOO_NEW`，零写 |
| 旧备份/包恢复 | `backup.py:189-194`、`:219-220`；`nmbak.py:684-693` | v8 备份在新代码上恢复 → 自动补 v9；v9 备份在旧代码上 → `SCHEMA_TOO_NEW` |
| `validate` 回调只在 v7 调用 | `migrator.py:236-252`；`core_assembly.py:1122` | v9 不会触发 v7 基线校验，无需改 validator |
| 迁移脚本按 `sqlite3.complete_statement` 切分 | `migrator.py:181-201` | 单条 `CREATE INDEX ...;` 安全 |

**`IF NOT EXISTS` 取舍（写入卡面的决策点）**：仓内 v1–v8 **零** `IF NOT EXISTS`（grep 为空），迁移一次性且被 checksum 守护。建议**用裸 `CREATE INDEX`（fail-loud）**：若某库已被人手动建过同名索引，启动会 typed 失败而不是"静默跳过、性能没修却记成 v9"。代价是该异常状态需要人工 `DROP INDEX` 后重试（登记为 limitation）。改用 `IF NOT EXISTS` 的唯一收益是容忍这种非支持态，代价是可能**假成功**——与本项目"不得声称已修"的纪律冲突。

**索引形态取舍**：
- `(book_id)` 单列：同时服务 preview（`book_id = ? AND current_revision_id IS NOT NULL`）、删除计数、revision id join、pinned join、以及事务内 `DELETE ... WHERE book_id = ?`（可走覆盖索引）。**推荐**。
- `(book_id) WHERE current_revision_id IS NOT NULL` 部分索引：preview 更小，但**无法**服务 `DELETE`/`COUNT`（无 current 过滤），删除事务仍全表扫 → 否决。
- `(book_id, artifact_type)`：对 `ORDER BY` 无帮助（排序键是 join 出来的 chapter/page 列），只增加体积 → 否决。
- 不需要 `ANALYZE`：`book_id = ?` 是索引首列的等值谓词，且没有竞争索引可让优化器选错；实测计划直接命中（§3.2）。迁移里也不应顺手 `ANALYZE`（会写统计表、放大迁移时间且无收益）。

### 2.5 wire / 命令 / 能力 / 错误码 / `PROTOCOL_MINOR`

**均不受影响**：不加命令、不加能力、不加错误码、不改 `PROTOCOL_MINOR`（`core_service.py:320` = 3）、不改任何请求/响应字段。唯一"值层"变化是某些 receipt/seed 里已有的 `schema_version` 字段会从 8 变 9（如 `tests/fea11/support/ipc_seed.py:88-96`），那是数据库版本的真实投影，不是 wire 形状变更；`FEA-C07`/`C-16`/`M2-C1` 全文无 `schema_version` 字面值（grep 为空），因此不构成契约冲突。`python tools/generate_api_inventory.py --check` 实测 EXIT 0（§7.3）。

## 3. 收益基准（实测）

### 3.1 复现方式（仓外，可复核）

```
# 生产迁移链建 v8 临时库（20 书 × 1000 页/书；300 或 3000 artifacts/书）
python G:\CODEX\New Manga.workspace\C04B-RESIDUAL\index-scope\bench_index_l4.py
# 隔离探针：每本 300 artifacts，6k 库 vs 60k 库（200 书）
python G:\CODEX\New Manga.workspace\C04B-RESIDUAL\index-scope\bench_wide_index.py
# 干净数据上 old / new / new+index 的行集与顺序等价
python G:\CODEX\New Manga.workspace\C04B-RESIDUAL\index-scope\check_order_equality.py
```

- 建库只用 `infrastructure.sqlite.schema.default_migrations()` + `MigrationRunner`（生产代码），库文件在 `...\index-scope\tmp\`，**从不打开真实用户库**。
- 计时口径：预热一遍后，20 本书 × 10 轮 = 200 样本，取均值；`ms/书`；`batch20` = 一次 20 书批量预览的均值。新谓词调用的是**发布方法本身**（`SqliteLibraryRepository.list_book_artifact_current_pointers`），不是手抄 SQL。
- 环境：Windows / CPython 3.14.6 / 同一 tmp 目录；行数：6k 库 = 6,000 artifacts + 20,000 pages；60k 厚库 = 60,000 artifacts + 20,000 pages；60k 宽库 = 60,000 artifacts + 200,000 pages（200 书）。

### 3.2 执行计划（`EXPLAIN QUERY PLAN`）

| 查询 | 无索引（现状 v8） | 加 `idx_media_artifacts_book` 后（tmp 库模拟） |
|---|---|---|
| 旧谓词（`c.book_id = ?`，`25dc1523c^`） | `SEARCH c USING INDEX idx_chapters_book_id` → `SEARCH p USING INDEX idx_pages_chapter_source_order` → `SEARCH ma USING INDEX idx_media_artifacts_page` → `USE TEMP B-TREE FOR ORDER BY` | — |
| 新谓词（现状 `library.py:1199`） | **`SCAN ma`** → `SEARCH p ... LEFT-JOIN` → `SEARCH c ... LEFT-JOIN` → `USE TEMP B-TREE FOR ORDER BY` | **`SEARCH ma USING INDEX idx_media_artifacts_book (book_id=?)`** → 同上两个 LEFT-JOIN → `USE TEMP B-TREE FOR ORDER BY` |
| `DELETE FROM media_artifacts WHERE book_id = ?`（`:1940`） | `SCAN media_artifacts` + `SEARCH artifact_revisions USING COVERING INDEX ...` | **`SEARCH media_artifacts USING COVERING INDEX idx_media_artifacts_book`** |
| `SELECT COUNT(*) ... WHERE book_id = ?`（`:1549-1551`） | `SCAN media_artifacts` | **覆盖索引 `SEARCH`** |
| `list_book_artifact_revision_ids`（`:1232-1239`） | `SCAN ma` | **`SEARCH ma USING INDEX idx_media_artifacts_book`** |
| `list_book_pinned_revision_ids` 的 artifact 分支（`:1252-1254`） | `SCAN ar` + `SEARCH ma USING sqlite_autoindex_media_artifacts_1` | **`SEARCH ma USING INDEX idx_media_artifacts_book`** + `SEARCH ar ...` |

### 3.3 耗时（同 schema v8、同机同轮）

| 数据集 | 旧谓词 ms/书 | 新谓词（现状）ms/书 | 新谓词 + 模拟 v9 索引 ms/书 | batch20：旧 / 新 / 新+索引 |
|---|---|---|---|---|
| 6k（20 书 × 300 artifacts） | 0.422 | 0.502 | **0.354** | 8.5 / 10.0 / 7.1 ms |
| 60k 厚（20 书 × 3,000） | 2.852 | 8.903 | **4.364** | 57.0 / **178.1** / **87.3 ms** |
| 60k 宽（200 书 × 300，隔离探针） | 0.502 | **5.939** | **0.376** | — |

**读法**：
1. 旧谓词的成本由**本书的页数**决定（0.42 → 2.85 是因为每本从 1,000 页增长受 artifacts/页影响，而 60k 宽探针下仍是 0.50，证明它不随全库增长）。
2. 新谓词的成本由**全库 artifacts 总量**决定：同样 300 artifacts/本，6k 库 0.50 ms、60k 库 5.94 ms（11.8×，与行数 10× 同阶）。
3. 索引把 (2) 的放大消掉：60k 宽探针 5.68 → **0.376 ms**（与 6k 的 0.347 持平，1.08×）。
4. 索引**不能**把 60k 厚数据集拉回旧谓词水平（8.90 → 4.36，仍 1.53× 旧谓词）：差值来自"从 artifacts 驱动 + 排序"，属于谓词语义的固有成本，不是索引能消除的。**卡面不得承诺"恢复到修复前性能"。**

**与 R3-002 原始数字对账**：Reviewer 记录 6k 0.24→0.43、60k 0.26→5.32 ms/书（`FEA-12-CORE-C04B-RESIDUAL-3-r1.md:163`）。我的 60k 新谓词 5.94（宽探针）/ 8.90（厚数据集）与其 5.32 同量级，形态吻合（其 60k 库应是"多书、每本 artifacts 不多"）；6k 绝对值差约 0.2 ms（数据形状/缓存预热不同）。**方向与"全库放大"结论独立复现成立**，绝对值以各报告口径为准。

### 3.4 成本侧的实测

| 指标 | 6k | 60k 厚 |
|---|---|---|
| `CREATE INDEX` 耗时（一次性，迁移内） | 9.4–10.0 ms | 28.8–33.4 ms |
| 库文件增量 | +77,824 B | +753,664 B（≈12.5 B/行） |
| 2,000 artifacts + 2,000 revisions 插入 | 无索引 29.1 ms / 有索引 29.3 ms | 无索引 38.9 ms / 有索引 37.1 ms |
| 行集/顺序等价（干净数据，20 书） | OK | OK |

写放大在噪声内（两个方向都出现过），说明该索引在该写入规模下无可见代价；`dbstat` 在本机 Python 构建中不可用（返回 `None`），体积以文件增量为准。大库首启建索引成本**未实测**，按行数线性外推：600k ≈ 0.3 s、6M ≈ 3 s（外推，不作为证据）。

## 4. 成本

### 4.1 文件清单（预计）

| 文件 | 变更 |
|---|---|
| `src/infrastructure/sqlite/schema.py` | +`SCHEMA_VERSION_V9=9`（带注释）、+`MIGRATION_V9_NAME`、+`MIGRATION_V9_SQL`（单条 `CREATE INDEX idx_media_artifacts_book ON media_artifacts(book_id);`）、+1 元组项。约 8 行 |
| `tests/storage/test_v9_index_migration.py`（新建，或并入 `tests/storage/test_schema_migration.py`） | 见 §4.2 |
| `tests/fea09/test_v7_migration.py` | 4 处 `MAX(schema_version) == 8` → 9（`:76`、`:139`、`:248`、`:263`） |
| `tests/fea11/test_source_gate_unify.py` | `:213` `assert [record.schema_version ...] == [8]` → 起点相关（若从 v7 起则 `[8, 9]`） |
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11SourceIpcTests.cs` | `:60` `Assert.Equal(8, receipt...schema_version)` → 9（值来自 `ipc_seed.py:88-90` 的真实库版本） |
| 卡/评审/Handoff/`verification/FEA-12-CORE-C04B-INDEX-L4-1/**` | 证据与台账 |

可选（非必须）：`tests/fea11/test_source_sync.py:993` 的 `latest_known_schema_version=8` 语义上已"陈旧"，但该处是空库分支（`connection.py:356-357` 返回 `EMPTY`），**不会失败**，卡面可注明"顺手对齐但不作为 AC"。

### 4.2 迁移测试要点（AC 的判别力来源）

1. **逐起点升级**：用生产 `MigrationRunner` 从 v1…v8 每个起点升到 v9；断言 9 被记录、`application_metadata` 双源一致、索引存在（`sqlite_master` / `PRAGMA index_list('media_artifacts')`）。
2. **字节不变**：断言 `default_migrations()[:8]` 每项的 `schema_version/name/checksum` 与硬编码期望值一致（等价于"v1–v8 未被编辑"），并要求卡面留 `git diff` 只含 v9 新增的证据。
3. **数据守恒**：升级前后 `books/chapters/pages/media_artifacts/artifact_revisions` 行数与抽样内容逐项相等（索引不改数据）。
4. **幂等**：`apply_pending()` 第二次返回空；重复 `open_database` 不重建索引、不报错。
5. **失败回滚**：在 v9 SQL 后注入一条必失败语句（测试内构造）或 monkeypatch 使 `INSERT INTO schema_migrations` 失败 → 断言版本停在 8、`idx_media_artifacts_book` **不存在**、库仍可读写（`migrator.py:271-276` 路径）。
6. **旧端拒写**：`MigrationRunner(conn, MIGRATIONS[:8])` 对 v9 库 → `SchemaTooNewError`；`open_database(..., latest_known_schema_version=8)` → `SchemaTooNew`/`query_only`。
7. **计划断言**：对 CM 生产 SQL（不是手抄）断言 `EXPLAIN QUERY PLAN` 含 `USING INDEX idx_media_artifacts_book`；这是"索引真的被用上"的唯一机械判据。
8. **等价性**：干净数据上 old/new/indexed 行集与顺序一致（本报告 §3.4 已用同一手法验证，可直接移植为判别测试）。

### 4.3 回滚路径

- 升级前：生产路径已有 `pre_migration` 备份（`migrator.py:165-172`）；失败自动回滚，DB 停在 v8。
- 需要撤回 v9 时：**没有自动降级**（C-01b SC-37 口径）。人工回滚 = 用升级前备份恢复（恢复到 v8 文件）→ 旧代码可用；或在新代码上 `DROP INDEX` 并删除 `schema_migrations` 的 v9 行与 `application_metadata` 回写 8（不推荐，破坏 checksum 账本一致性）。卡面应写"回滚只走备份恢复"。

## 5. 风险

| 风险 | 评估 | 处置 |
|---|---|---|
| 旧库升级失败使应用无法启动 | 低：`CREATE INDEX` 只可能因磁盘满/DB 损坏失败；失败即 `MigrationError` typed 失败，DB 停 v8，不半迁移 | fail-closed 是既有设计；生产有 `pre_migration` 备份；limitation 写明"磁盘不足会在启动时暴露" |
| 索引体积 | 60k 行 ≈ 754 KB（12.5 B/行），百万行 ≈ 12 MB 级 | 可忽略；不做部分索引以保删除路径 |
| 写放大 | 测不出（±5% 噪声）；每行多维护一个 1 列索引 | 可接受；卡面 AC 不承诺写性能 |
| 与 `(page_id, artifact_type)` 索引关系 | **互补不冲突**：前者服务 `page_id` 定位（V/资源路径），后者服务 `book_id` 定位（删除/preview）；`DELETE` 用覆盖索引，`page_id` 查询仍走旧索引 | 无需删旧索引 |
| 是否需要 `ANALYZE` | 不需要（等值首列 + 无竞争索引；实测计划直接命中） | 迁移内**不**执行 `ANALYZE` |
| 同名索引已存在（人工 hotfix） | 裸 `CREATE INDEX` 会 typed 失败并阻止启动 | 登记 limitation + 运维说明（drop 后重试）；不用 `IF NOT EXISTS` 以免假成功 |
| 大库首启一次性耗时 | 60k ≈ 30 ms；按线性外推 6M ≈ 3 s（未实测） | 可接受；limitation 写明外推而非实测 |
| 结果语义变化 | **无**：7 键 `ORDER BY` 以 `artifact_id`（PK）收尾，是全序；干净数据实测行集/顺序一致 | AC-4 保留等价断言 |
| 损坏行语义 | **不变**：R-1 的 `book_id` 归属仍是唯一成员判据；索引不改变任何行集 | 卡面 Out 明确"不碰 L-5/损坏行语义" |
| 与未来 schema 卡的版本冲突 | 若别的卡先占 v9，本卡需改为 v10 或合并 | 卡面写"若已有 v9 计划则合并" |

## 6. 是否值得做 / 是否应改判

### 6.1 与候选的对比

| 候选 | 价值 | 成本 | pin | 建议 |
|---|---|---|---|---|
| **本卡：L-4 索引（v9）** | 消除 preview 与**删除事务内**的全库扫描；60k 库 batch20 178→87 ms；删除面 4 处 `SCAN`→`SEARCH`；随库增长的放大器被移除 | 中-小：`schema.py` 8 行 + 1 新迁移测试 + 5 处版本断言（2 语言）+ 卡/证据 ≈ 6 文件 | **0** | **推荐**，P3 |
| RH-3 根治（Host `_targets` 收缩） | 只解预算稀释；"枚举省略≠删除"要求 Core 侧新增删除信号 | 高：C-17 additive/新契约 + Host 删除 API + Core 信号 + 测试 | 1+ | 不建议（无 `deleted_at` 生产者，价值空转） |
| SCAN-RH P3-1（`CreateLinkedTokenSource` 移入内层 try） | 只关一个"线程挂起 ≥4 s"的理论 ODE 窗口 | 极小：1 行 + 1 用例 | 0 | 可做，但**不值得单开窗口**；跟随任意一次 Host 改动顺手 |
| 2C / L-R11 剩余 P3 | 诊断口径/文档，无运行时收益 | 小 | 0 | 仅登记；不排期 |
| B2 `roots_available` | 无消费者 | 小-中 | 0 | 继续延后 |

### 6.2 优先级建议

1. **本卡可作为下一个可执行项**（它是当前唯一"诊断已完成、范围清楚、0 pin"的候选；STATUS `:7` 已把它列为待 scope review 的索引卡）。排 B2 之前。
2. **不插队**：它不是用户可见缺陷；若队列里有用户价值更高的项（UI/功能），让路。
3. **合并优先于重复 bump**：若近期另有必须 bump schema 的卡（例如 C-15/C-17 的新增补），把这条索引并进那张卡的迁移，避免 v9/v10 两次版本跳变与两轮断言更新。
4. **不要为它做 UNFREEZE**：0 pin 已成立，UNFREEZE 只会把实现细则写进契约文本。

### 6.3 若 DSH 判"不值得现在做"

- **登记方式**：保持 `doc/plan/FEA-CONTRACT-FROZEN-C04b.md:145` 的 §4A **L-4 原文不动**（它是"未修"的准确记录），在 `doc/STATUS.md:7` 的候选表述里保留"索引卡 L-4（已有 scope review，未释放）"，必要时在 `doc/REBASELINE_PLAN.md` 的候选行注明"待释放"；**不要**改写成"已排期/已修"。
- **本报告的价值仍然有效**：判定（0 pin）、迁移形状、基准数字与卡面草案可直接复用，不必重做诊断。
- **禁止表述**：不得写"L-4 已修/索引已加/性能已恢复"；L-4 的状态在实施卡 closeout 之前只能是**未修**。

## 7. 卡面建议

### 7.1 frontmatter 草案

```yaml
id: FEA-12-CORE-C04B-INDEX-L4-1
title: C-04b L-4：media_artifacts.book_id 索引（v9 迁移，0 pin）
kind: implementation
governance_version: 3
status: proposed
approval: 独立 scope review doc/reviews/FEA-12-CORE-C04B-INDEX-L4-scope-r1.md（fresh subagent session session-3ac1953a-…，verdict recommended）；DSH 裁决后释放
dependency_contract: 无（0 pin；C-15/C-04b/C-01b 字节零改动）
suggested_owner: null
owner: null
reviewer: null
depends_on:
  - FEA-12-CORE-C04B-RESIDUAL-3
  - FEA-12-CORE
base_commit: 02c1a26d1
branch: null
worktree: null
integration_commit: null
delivery_head: null
evidence_dir: verification/FEA-12-CORE-C04B-INDEX-L4-1
allowed_paths:
  - src/infrastructure/sqlite/schema.py
  - tests/storage/test_v9_index_migration.py
  - tests/fea09/test_v7_migration.py
  - tests/fea11/test_source_gate_unify.py
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11SourceIpcTests.cs
  - doc/tasks/FEA-12-CORE-C04B-INDEX-L4-1.md
  - doc/reviews/FEA-12-CORE-C04B-INDEX-L4-1-*.md
  - doc/handoffs/FEA-12-CORE-C04B-INDEX-L4-1-*.md
  - verification/FEA-12-CORE-C04B-INDEX-L4-1/**
out_of_scope:
  - library.py 查询 SQL（preview 谓词/排序键零改动）
  - 任何契约字节（C-15/C-17/C-04b/C-01b/C-07/C-16/M2-C1）与冻结记录
  - wire/命令/能力/错误码/PROTOCOL_MINOR、依赖、UI/App
  - 其它索引（page/chapter/region 面）、ANALYZE、部分索引、v10+
  - L-1/L-2/L-5、RH-3/SCAN-RH、2C/L-R11 残余
  - 真实用户数据库、备份包、push（Lead 统一）
```

### 7.2 AC（5–6 条，可机械判定）

- **AC-1 迁移形状与字节保留**：`schema.py` 新增 `SCHEMA_VERSION_V9=9`、`MIGRATION_V9_NAME="v9__media_artifacts_book_index"`、`MIGRATION_V9_SQL` 仅含 `CREATE INDEX idx_media_artifacts_book ON media_artifacts(book_id);` 并追加到 `default_migrations()`；**v1–v8 的 `schema_version`/`name`/`checksum` 逐项不变**（测试硬编码期望 + 卡面留 `git diff` 只含新增行的证据）。
- **AC-2 旧库升级与守恒**：生产 `MigrationRunner` 从 v1…v8 每个起点升到 v9；`schema_migrations` 与 `application_metadata` 双源=9；`books/chapters/pages/media_artifacts/artifact_revisions` 行数与抽样内容守恒；`PRAGMA index_list('media_artifacts')` 含该索引；二次 `apply_pending()` 为空（幂等）。
- **AC-3 失败回滚与旧端拒写**：注入 v9 事务内失败 → 版本仍 8、索引不存在、库仍可读写；`MigrationRunner(conn, MIGRATIONS[:8])` 对 v9 库抛 `SchemaTooNewError`，`open_database(..., latest_known_schema_version=8)` 返回 `TOO_NEW` 且零写。
- **AC-4 计划生效与结果等价**：对**发布方法**所用的 SQL 断言 `EXPLAIN QUERY PLAN` 含 `USING INDEX idx_media_artifacts_book`；同一 SQL 在干净数据上的行集与顺序与升级前逐项相等；`book_delete_inventory` 的 artifact 计数与 `list_book_artifact_revision_ids` 计划由 `SCAN` 变 `SEARCH`（测试或卡面证据二者其一必须机械可复算）。
- **AC-5 版本断言同步**：`tests/fea09/test_v7_migration.py:76/139/248/263`、`tests/fea11/test_source_gate_unify.py:213`、`Fea11SourceIpcTests.cs:60` 全部按 v9 更新；**禁止**以删除/跳过断言的方式"通过"；定向 pytest（storage + fea09/fea11 受影响文件）全绿。
- **AC-6 门禁/证据/不夸大**：`verify_pins.ps1` **18/18**（零 pin 变动）、`check.ps1` PASS、`generate_api_inventory.py --check` EXIT 0、全量 pytest 不降（基线 3369/10）、全量 .NET 不降（1683/0/96）；EV/Handoff/Manifest 完整；**不得**写"性能已恢复/旧谓词水平/索引已消除全部开销"，只能在 closeout 写"preview 与删除面不再全表扫描，60k artifacts 下 batch20 178→87 ms（本卡实测）"。

### 7.3 limitation（卡面必须登记）

- 只加 `book_id` 单列索引；新谓词仍保留 7 键 `ORDER BY` 的临时排序与逐行 pages/chapters 探针，60k 厚数据集 4.36 ms/书未回到旧谓词 2.85 ms/书。
- 不改损坏行语义（`book_id` 与页归属不一致仍按 `book_id` 归属）；不碰 L-5 的 preview 缓存漏清。
- 裸 `CREATE INDEX` 遇同名索引会 fail-loud；不支持的状态需人工 `DROP INDEX`。
- 大库首启建索引成本未实测（60k ≈ 30 ms；外推 600k ≈ 0.3 s / 6M ≈ 3 s，均为外推）。
- 未做并发写压测；写放大只在 2,000 行插入规模上测过（噪声级）。
- 回滚只走升级前备份恢复（无自动降级，C-01b SC-37）。

### 7.4 门禁与 PREREQ

- **无 PREREQ 卡**：0 pin、无 UNFREEZE、无 wire。
- 门禁：`verify_pins.ps1`、`check.ps1`、`generate_api_inventory.py --check`、定向 pytest、全量 pytest、全量 .NET（按卡面基线）。

## 8. 实测与未跑

| 项 | 状态 | 结果/证据 |
|---|---|---|
| `git log --oneline -3 -- src/infrastructure/sqlite/schema.py` | 已跑 | `40cc6508d`（v8 迁移）、`d3d7cd564`（v7）、`a80cfd0bb`（v6） |
| v8 索引定义 grep | 已跑 | `media_artifacts` 仅 `idx_media_artifacts_page ON media_artifacts(page_id, artifact_type)`（`schema.py:86`）；`book_id` 无索引 |
| `MIGRATIONS` 结构 | 已跑 | `default_migrations()` 8 项（`schema.py:841-851`）；`Migration.checksum = sha256(sql)`（`:562-564`） |
| 既有 migration 测试样例 | 已跑（读） | `tests/fea11/test_v8_migration.py`（v1..v7→v8、旧行守恒、旧 runner 拒写）；`tests/fea09/test_v7_migration.py`（4 处硬编码 8） |
| tmp SQLite 复现 `EXPLAIN QUERY PLAN` | 已跑 | 见 §3.2（`SCAN ma` → `SEARCH ... idx_media_artifacts_book`） |
| tmp SQLite 计时（6k/60k 厚/60k 宽） | 已跑 | 见 §3.3 |
| 索引模拟（tmp 库内建索引） | 已跑 | §3.3/§3.4（含建索引耗时、体积、写放大、顺序等价） |
| `verify_pins.ps1` | 已跑 | **PIN AUDIT: PASS (all 18)**，EXIT=0 |
| `check.ps1`（默认） | 已跑 | **Governance check: PASS (3 warnings)**，EXIT=0（warnings：9 个非终态 Task / STATUS 与 REBASELINE_PLAN 达 80% 预算） |
| `generate_api_inventory.py --check` | 已跑 | EXIT=0（无接口漂移） |
| 全量 pytest / 全量 .NET / build | **未跑** | 采信 STATUS `:20` 基线 3369/10、1683/0/96；本报告不据此声明任何门禁 |
| 真实用户库升级演练 / 并发压测 | **未跑** | 明确不碰真实数据；卡面需在实现时补临时库演练 |

## 9. 真实性声明

1. **写入范围**：本次唯一写入仓库的文件是本报告 `doc/reviews/FEA-12-CORE-C04B-INDEX-L4-scope-r1.md`。未修改代码、测试、契约、冻结记录、卡面、STATUS/PLAN/LEDGER；未 `git add`/`commit`/`push`。所有脚本、临时 SQLite 库与日志在 `G:\CODEX\New Manga.workspace\C04B-RESIDUAL\index-scope\`（`bench_index_l4.py`、`bench_wide_index.py`、`check_order_equality.py`、`bench-run.log`、`bench-wide-index.log`、`bench-order-equality.log`、`bench-summary.json`、`tmp/**`）。
2. **独立性**：我是本次派发的独立上下文 fresh subagent，未参与 `FEA-12-CORE`、`FEA-12-CORE-C04B-RESIDUAL-1/2/3` 的实现、返修或复核，未参与 C-15/C-17/C-16 契约起草；与 L-4 的登记人、R-1 修复作者均非同一上下文。
3. **实测与未跑**：§3 的全部数字来自本机本次实跑（命令见 §3.1，日志在仓外），临时库由生产 `default_migrations()` 建立；**未跑**项已在 §8 逐条列出（全量 pytest/.NET/build、真实用户库、并发压测）。我采信 STATUS 的测试基线但**未复跑**，不把它当作本报告的实测结论。
4. **不夸大**：
   - **不声称**索引已添加、L-4 已修复、性能已恢复、60k 库的 preview 已变快——这些都要等实现卡落地并复跑。
   - **不声称**加索引能把新谓词恢复到旧谓词水平（实测 4.36 vs 2.85 ms/书）。
   - **不声称**索引改进了任何正确性语义；它不改变行集、顺序或损坏行归属（干净数据实测等价，损坏行按 R-1 设计）。
   - **不声称**本报告覆盖真实用户库形态、并发或大库首启成本（前者未跑，后者为外推）。
   - `recommended` 只表示"值得按 §7 卡面实施"，不表示已排期、已释放或已获 DSH 裁决。
