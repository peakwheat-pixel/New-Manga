---
task_id: FEA-14-LIB-1
reviewer: 独立子 agent（lead 会话 session-408d4e24-3789-4111-acde-983899601dad 派发；全新上下文，未参与实现或返修；只读）
reviewer_kind: subagent
author: dsh
base_commit: f97f54476b097b7da9a9b7e1be1aff7e0ba16ba1
reviewed_head: de595f69dd4e5527a163e4c8ed6f390ce50a8a19
decision: approved
---

# Review：FEA-14-LIB-1（r3 独立复核）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，分支 `main`。审查者由 lead 会话 `session-408d4e24-3789-4111-acde-983899601dad` 派发，为**全新上下文子 agent**，未参与本卡实现、r1/r2 处置或返修。
- **被审 head = `de595f69dd4e5527a163e4c8ed6f390ce50a8a19`**（r2 处置证据提交）。产品/文档提交 `e49855485293c0ab0a5e97b4333ca11a219d1c9b`；r2 被审 head `e779674d56243c705abb0dd9aeb2b14fdcc3c204`；r1 被审 head `83e45cfe54fb05bd0f4b0f6620e333b2c8e8d03e`。
- **diff 基线 = `f97f54476b097b7da9a9b7e1be1aff7e0ba16ba1`**（`83e45cfe5` 的父提交）。卡面 `base_commit: 8e39bb72c` 为 FONT-1 收口点；实测 `8e39bb72c..f97f54476` 只含 FONT-1 收口文档（`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/TASK_LEDGER.md`、FONT-1 r5 报告/卡、LIB-1 冻结卡），`src/ apps/ tests/ tools/ doc/plan/ doc/contracts/` **零变更**，故两种基线的产品 diff 等价。
- 变更面：`f97f54476..de595f69d` 共 **32 文件 / +1613 / −133**。其中 `e49855485` 为 **15 文件**（14 个产品/文档 + r2 报告），`de595f69d` 为 **6 文件**（卡面 + README + 4 日志，**无产品字节**，`git show --name-only` 复核）。
- 审查开始 `2026-11-10T16:20:15+08:00`（首个 git 命令；轮次采样 16:19:46），报告定稿前 `16:35:20+08:00`；`git rev-parse HEAD` 在开始、`16:31:43`（写报告前）与写报告后复核均为 `de595f69d`。开始与写报告前 `git status --porcelain` 均 **clean（0 行）**；写报告后唯一未提交变更为本报告。
- 只读纪律：仓库内唯一写入为本报告；探针脚本与隔离库全部位于 `%TEMP%`（`C:\Users\49745\AppData\Local\Temp\lib1_r3_*`），未写真实 `%APPDATA%`，未 commit、未 push，未改源码/测试/契约/卡面/证据。
- 本报告只对 `de595f69d` 的字节有效；head 变化即自动失效。

## 1. 结论

**`approved`**（**P0=0 / P1=0 / P2=0 / P3=1（accepted，不阻断）**）。

r2 的五项产品/文档修正与两项表述修正全部经实测或逐行核对关闭；r1 已关闭的 R-01、R-03、R-05–R-13 无一回退；v1–v11 迁移 NAME/SQL 与 base 逐字节一致；C-07 正式成员表与 `generate_api_inventory.py` stdout **逐行一致**（`ALL_MATCH: True`，69 方法 + 4 非方法成员）；C-07 契约字节 `7c033bf76af1726b71e1ce92a5b3c221d880cf7a36bfc44ef3d4467582d5457d` 与 pin 一致，`verify_pins` 18/18；32 个变更文件全部落在 `allowed_paths`；4 个 Canonical 日志的生成 HEAD 均为 `e49855485`；四道复跑门禁计数与证据表一致（13 / 1251 / 878 / 18）。

唯一新增项为 **R3-001（P3，accepted）**：P7/P8 对 `custom_rank`/`import_order` 未做 SQLite 64 位边界校验，手工 wire 传入 `2^63` 级整数会得到 `UNKNOWN/internal`，且 P8 会留下已创建的章节；`import_order=2^63−1` 被接受后会使该书后续创建永久返回 `UNKNOWN/internal`。当前 Host 侧 `int`（上限 2^31−1）不可达，故不阻断本卡，建议在 LIB-2 或后续加固中处理（§4.1）。

## 2. R2-001–R2-007 逐项关闭表

判定均为**本次实测/逐行核对**，不采信卡面自述。

| ID | r2 级别与问题 | 本次判定 | 证据 |
|---|---|---|---|
| **R2-001** | P1：P5 未知 `tag_id` → `UNKNOWN/internal`；同 patch 文本字段半写；非字符串文本值未拒绝；t1→t2 替换 | **CLOSED** | `%TEMP%` 隔离库经 `CoreServiceServer.dispatch_request` 探针：未知 tag → `TARGET_NOT_FOUND / not_found`；`{"title":"HalfWrite!","tags":["missing-tag"]}` 报错后 title 仍为 `Half`、tags 仍为空；既有 t1 的书再传 `{"title":"After","tags":["missing"]}` 报错后 title 仍为 `H`、既有 t1 保留（半写/半替换均消除）；`{"title":5}` → `INVALID_REQUEST / validation` 且未落库；t1→t2 全量替换成立；`tags=[]` 清空、重复 tag id 幂等；缺书（仅 tags）→ `TARGET_NOT_FOUND`。代码：`src/bootstrap/core_service.py:5155-5156` 捕 `TagNotFound`；`src/application/library/service.py:227-230` 在任何写前逐个 `_require_tag`、`:222-224` 文本字段仅 `str`；测试 `tests/core/test_library_wire.py:115-128`、`tests/storage/test_library_metadata.py:138-145`。 |
| **R2-002** | P2：`create_chapter` 以 `max(import_order)+1` 同时作 `sort_order`，重复/较小 `import_order` 撞序 | **CLOSED** | 探针精确复现 r2 场景：C1/C2 后三次 P8 `import_order=1` + 一次普通创建，DB 行（title, import, sort）= `(C1,1,1) (C2,2,2) (Extra0,1,3) (Extra1,1,4) (Extra2,1,5) (Tail,3,6)`；P8 三次响应 `sort_order=[3,4,5]`；`sort_order` 1..6 唯一；tail `import_order=3`。代码：`service.py:146-154`（两个独立 max+1）；测试 `tests/storage/test_library_metadata.py:161-176`；wire `sort_order=3` 负例 `tests/core/test_library_wire.py:139`；卡面 `:89`/README `:33` 的“唯一”表述与实测一致。 |
| **R2-003** | P3-1：Host P5 patch 类型无法表达 tags；Host/Client 拒绝空 `ordered_ids` | **CLOSED**（含 1 项观察，见 §4.3） | 六处签名逐字一致为 `IReadOnlyDictionary<string, object?>`：`IHostController.cs:219`、`HostController.cs:621-622`、`NullHostController.cs:112`、`HostRuntime.cs:671-672`、`CoreServiceClient.cs:1590-1591`、`FakeHostController.cs:260`。`CoreServiceClient.cs:1597-1636` 将 `string` 写字符串、`IReadOnlyList<string>` 写 JSON 数组、其他类型抛 `ArgumentException`（`null` 例外见 §4.3）。空 `ordered_ids` 守卫已移除：`HostController.cs:642-647`、`CoreServiceClient.cs:1647-1651`；探针：空书 `[]` → `updated:true`；非空书 `[]` → `INVALID_REQUEST`；缺书 `[]` → `TARGET_NOT_FOUND`；C# 4 个端口测试含空列表 no-op（`LibraryMetadataPortTests.cs:48-57`），App.Tests 878/0/11 通过。 |
| **R2-004** | P3-2：Fake `CreateChapterWithMetadataAsync` 返回 `SortOrder=importOrder`，与 Core 语义相反；无测试体现 IPC 未覆盖 | **CLOSED** | `FakeHostController.cs:279-295` 改为 `ChaptersByBook[bookId]` 的 `max(SortOrder)+1`，忽略 `importOrder`，并追加到 `ChaptersByBook`；测试 seed `c1 sort=1` 后断言 `importOrder:7 → SortOrder:2`（`LibraryMetadataPortTests.cs:59-70`）；README `:43` 明确 **不覆盖 `CoreServiceClient` 真实 IPC 读写映射**（NOT_RUN），测试名 `FakeHost_CreateWithMetadata_AppendsTheSortOrder` 不再暗示 IPC。 |
| **R2-005** | P3-3：卡面 Scope §2 写“v12 加 books 四列”，与实现不符 | **CLOSED** | `doc/tasks/FEA-14-LIB-1.md:71` 现为“复用既有 books 元数据列（author/series_title/description/notes 自 v2 迁移起已存在）；v12 仅 additive 增加 chapters.custom_rank”；`MIGRATION_V2_SQL` 确含四列，`MIGRATION_V12_SQL` 仅 `ALTER TABLE chapters ADD COLUMN custom_rank INTEGER;`。 |
| **R2-006** | P3-4：`schema.py` V12 常量块插在 V10 与 V11 之间 | **CLOSED** | head 文件顺序 V9(858)→V10(873)→V11(904)→V12(928)→`default_migrations`(933)；常量 NAME 顺序 `1..12`；`default_migrations()` 顺序 `[1..12]`；v1–v11 NAME/SQL 与 base 逐字节一致（自写 AST 比对 5 个 head 均 `MISMATCHES: none`）。 |
| **R2-007** | P3：README AC1 “非法值 → INVALID_REQUEST”过宽 | **CLOSED** | `verification/FEA-14-LIB-1/README.md:12` 已拆分：未知字段/非字符串 → `INVALID_REQUEST`；未知 tag id → `TARGET_NOT_FOUND`（且文本字段不被半写）；与本次探针一致。 |

### 2.1 r1 R-01–R-13 不回退确认（r2 已关闭项）

| ID | 本次判定 | 本次证据（实测/逐行） |
|---|---|---|
| R-01（P1，P5/P6/P8 缺书 typed） | **不回退** | 探针：P5/P6/P8 `book_id="nope"` 均 `TARGET_NOT_FOUND/not_found`；P7 缺章同；`core_service.py:5153-5156/5171-5172/5214-5215` 捕 `BookNotFound`/`ChapterNotFound`。 |
| R-02（P1，P5 tags） | **不回退（已真正关闭）** | 见 R2-001：有效替换、未知 tag typed、半写消除、文本类型、t1→t2 均实测。 |
| R-03（P2，P8 `sort_order`） | **不回退** | P8 响应含 `chapter_id,title,kind,number,sort_order`（探针）；客户端 `CoreServiceClient.cs:1726-1732` 读 `sort_order`；`ChapterSummary` 仍四字段（`:28`），`kind` 不投影已在卡面 `:59`/`:80` 与 README `:15` 登记。 |
| R-04（P2，创建排序） | **不回退（已真正关闭）** | 见 R2-002：`import_order` 与 `sort_order` 独立取序，1..6 唯一。 |
| R-05（P2，C-07 成员表） | **不回退** | 自写脚本逐行比对 `doc/plan/FEA-C07_API_INVENTORY.md` 与 `generate_api_inventory.py` stdout：`IReaderProgressSink 1`、`IHostController 69+4`、`IRunController 6`，含顺序与返回类型 **`ALL_MATCH: True`**；S5 节仅 `P16–P25`；统计 `25=4+4+7+5+5`、已落地 15、剩余 10、目标 `69+10=79`、三接口 86 自洽。 |
| R-06（P2，allowed_paths） | **不回退** | 自写逐路径脚本：`changed=32`，`OUT_OF_ALLOWED=0`；通配 `doc/reviews/FEA-14-LIB-1-*.md`、`CONTRACT-UNFREEZE-*.md`、`verification/FEA-14-LIB-1/**` 生效。 |
| R-07（P3，FROZEN 自洽） | **不回退** | FROZEN §1 含 v1.1–v1.6 原值 + r1 锚（`:15-21`）；§1B 记录 r1→r2→r3 现状（`:29-31`）；§2 条件 3 为 `1/69/6 = 76`（`:41`）；§3 已落地 15（`:49`）；§5 含 v1.3–v1.6 四行 + v1.6 待重冻行（`:86-90`）。`verify_pins` 18/18；`Get-FileHash` C07=`7c033bf76af1726b71e1ce92a5b3c221d880cf7a36bfc44ef3d4467582d5457d`。另：`git log` 证明 C-07 inventory/UNFREEZE 最后一次改动是 r1 处置 `00a99622a`，`00a99622a..HEAD` 对这两类文件 **零 diff**。 |
| R-08（P3，证据/README 表述） | **不回退** | 4 日志头均 `HEAD=e49855485293c0ab0a5e97b4333ca11a219d1c9b` 并带 dirty 列表（dotnet `[]`；pytest `[]`；regression 记 dotnet/pytest；pins 记三份日志）；计数 13/1251/878/0/11/18/69-76 与本次复跑一致；README AC1/AC3 与实测一致（空书 `[]` no-op、非空书 `[]`/缺/多/重复 → `INVALID_REQUEST`，该路径不返回 `ChapterNotFound`）。 |
| R-09（P3，`utc_now()`） | **不回退** | `service.py:290` 用 `utc_now()`；探针读回 `2026-11-10T…+00:00` 毫秒格式；文件无局部 `datetime` 导入。 |
| R-10（P3，测试保真度） | **不回退** | `tests/storage/test_fonts.py:50` `read_schema_version(conn) == LATEST == 12`；`test_library_metadata.py:33-58` 先到 v11、插入真实 books/chapters 行、升级后断言字段保留且 `custom_rank IS NULL`；`LibraryMetadataPortTests.cs` 4 个 `[Fact]`；全量 878（较 r2 的 877 +1）通过。 |
| R-11（P3，三项 deferral） | **不回退（已登记）** | 卡面 `:100-108` 三项 deferral；与 PREQ §8 wire 键形状不冲突。 |
| R-12（P3，`custom_rank` write-only） | **不回退（已登记）** | 探针：写入 `custom_rank=99` 后 `reorder` 顺序完全按请求重写，不参考 `custom_rank`；卡面 out_of_scope `:57`、R-12 `:108`、README `:34` 一致。 |
| R-13（P3，wire 边界） | **不回退** | 探针：空书 `[]` OK；非空书 `[]`/缺/多/重复 id → `INVALID_REQUEST`；P8 `import_order=True/1.0/"1"` → `INVALID_REQUEST`；P7 `custom_rank=True/1.5/-1/"3"` → `INVALID_REQUEST`，`0`/`null` OK；重复 `import_order` 允许且 `sort_order` 唯一（R2-002）。 |

## 3. AC 逐项判定

| AC | 判定 | 依据 |
|---|---|---|
| **AC1 书元数据** | **MET** | patch 保留未提供字段；title 非空；未知字段/非字符串 → `INVALID_REQUEST`；tags 全量替换（t1→t2）；未知 tag id → `TARGET_NOT_FOUND` 且**无半写**；无书 → `TARGET_NOT_FOUND`。见 §2 R2-001 探针与 `test_library_wire.py:91-128`、`test_library_metadata.py:61-73/125-145`。 |
| **AC2 章元数据** | **MET** | kind/custom_rank/number/title/subtitle/notes 均落库；非法 kind → `INVALID_REQUEST`；无章 → `TARGET_NOT_FOUND`；文本字段严格 `str`，`custom_rank` 严格非负整数/null；`updated_at` 毫秒 UTC。见 `test_library_metadata.py:76-90/179-195`、`test_library_wire.py:149-157` 与探针。 |
| **AC3 章重排** | **MET** | 缺/多/重复 → `INVALID_REQUEST`；空书 `[]` → no-op；非空书 `[]` → `INVALID_REQUEST`；成功后 `sort_order` 连续 1..n、读取顺序与请求一致；先校验后写。见探针与 `test_library_metadata.py:93-108`。 |
| **AC4 创建带元数据章** | **MET（带 limitation）** | title/kind/number/import_order 落库；返回 `chapter_id/title/kind/number`（+可选 `sort_order`）；父书不存在 typed；重复/较小 `import_order` 不撞序；Host 读 `sort_order`；`kind` 不进入 `ChapterSummary` 已登记 limitation（README `:15`、卡面 `:59/:80`）。边界项 R3-001 不影响现实路径（Host `int` 不可达），见 §4.1。 |
| **AC5 迁移/契约/门禁** | **MET** | v12 仅 additive `custom_rank`；v1–v11 NAME/SQL 逐字节未变；旧 v11 真实行升级后字段保留、`custom_rank IS NULL`；P5–P8 键形状符合 PREQ §8（P8 `sort_order` 为 additive）；C-07 表逐行等于 stdout；`--check` EXIT 0；`verify_pins` 18/18 且 C07 pin 匹配。 |
| **AC6 证据** | **MET** | 4 日志含生成 HEAD/dirty/EXIT；定向 13、回归 1251、App.Tests 878/0/11、pins 18/18、API 69/76 均与本次复跑一致；5 份 Canonical 证据 SHA-256 与文件逐一匹配；NOT_RUN 如实登记（README `:39-46`）。 |

## 4. 必查项判定

| # | 必查项 | 判定 | 说明 |
|---|---|---|---|
| 1 | 迁移字节：v12 additive、v1–v11 未变、`custom_rank` 多路径一致 | **PASS** | 自写 AST 脚本对 base 与 5 个 head：v1–v11 NAME/SQL `IDENTICAL`；v12 仅一条 `ALTER TABLE`；文件顺序 V10→V11→V12；`default_migrations` 1..12；`_CHAPTER_COLUMNS`/`add_chapter`/`update_chapter`/`_row_to_chapter` 均含 `custom_rank`；旧 v11 真实行测试通过。 |
| 2 | wire P5–P8 形状 vs PREQ §8 | **PASS** | P5 `book_id,patch{title?,author?,series_title?,description?,notes?,tags?}`（另见 §4.3 的 additive 扩展）；P6 `book_id,ordered_ids[]`；P7 `chapter_id,patch{kind?,custom_rank?,number?,title?,subtitle?,notes?}`；P8 `book_id,title,kind?,number?,import_order?` → `chapter_id,title,kind,number` + 可选 `sort_order`；四命令均为普通通道 minor 3，探针响应版本 minor=3。 |
| 3 | Host 六处签名/降级/空列表 | **PASS（带 NOT_RUN）** | 六处 `IReadOnlyDictionary<string, object?>` 逐字一致（§2 R2-003 行号）；`NullHost` 返回 false/null 由 `LibraryMetadataPortTests.cs:18-29` 覆盖；空 `ordered_ids` 守卫移除（静态）+ Core 探针；**真实 Host↔Core 进程级 IPC 未跑**（NOT_RUN）。 |
| 4 | C-07 正式成员表逐行 == 脚本 stdout；S5 仅 P16–P25；统计自洽 | **PASS** | 自写解析器：`doc=73`（69 方法 + 4 非方法）== `gen=73`，`IReader 1`、`IRun 6`，含顺序/返回类型 **`ALL_MATCH: True`**；S5 ids `[16..25]`；`25=4+4+7+5+5`、15 已落地、10 剩余、`69+10=79`、`86` 自洽。 |
| 5 | FROZEN §1 pin 链/§1B/§2 条件 3/§3/§5；契约字节未变；pins | **PASS** | 见 §2 R-07。另：r2 处置提交 `e49855485` 只改 FROZEN（簿记：`:29-31/:90`）与产品/卡面/报告，**未改** `FEA-C07_API_INVENTORY.md` 或 `CONTRACT-UNFREEZE-*`；`de595f69d` 亦未改。 |
| 6 | 证据 provenance（HEAD/dirty/计数/哈希） | **PASS（口径见 §4.3）** | 4 日志生成 HEAD=`e49855485` + dirty 列表；计数与本次复跑一致；5 份 Canonical SHA-256 **5/5** 匹配当前文件。`commit` 列语义为“生成时产品 HEAD”，5 个文件本身在 `de595f69d` 入库（与 r1/r2 约定一致）；EV-LB-005 README 的 hash 是簿记后当前字节（`e49855485` 时 README 不同，`6c6910…`），属已声明的证据簿记，不影响产品证据链。 |
| 7 | diff ⊆ allowed_paths；无未授权契约字节 | **PASS** | 32/32 覆盖，`OUT_OF_ALLOWED=0`；契约邻近变更仅 C-07 inventory/FROZEN/UNFREEZE LIB1/r1/r2 报告/卡面/证据/STATUS/PLAN/ledger，均在 allowed_paths；**C-07 inventory 与 UNFREEZE 字节自 r1 处置后未再变**。 |
| 8 | 扫新 P0/P1/P2 | **P0=0 / P1=0 / P2=0** | 新发现仅 R3-001（P3，accepted），见 §4.1；另有 §4.3 观察项，不构成 finding。 |

### 4.1 新发现（R3 定级）

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处置 |
|---|---|---|---|---|---|---|
| **R3-001** | **P3（accepted，不阻断）** | `src/application/library/service.py:146-154`（`max(import_order)+1`）、`:302-320`（先 `create_chapter` 再改 `import_order`）；`src/bootstrap/core_service.py:5204-5209`（只校验 bool/float/负值，无 64 位上界）、`:7015-7086`（`OverflowError` 落入泛化 `UNKNOWN/internal`） | 手工 wire 传超大非负整数时：① P8 `import_order=2^63` → `UNKNOWN/internal`，但章节已先落库（实测留下 `Leak`，`sort_order=2`、`import_order=2`）——**确定性半写**；② P8 `import_order=2^63−1` 被接受，随后该书任何普通创建因 `max+1=2^63` 溢出而永久返回 `UNKNOWN/internal`（实测 `('Max', 2^63−1, 1)` 后 append 失败）；③ P7 `custom_rank=2^63` → `UNKNOWN/internal`（无落库）；`2^63−1` 可正常存取。**可达性**：Host `CreateChapterWithMetadataAsync` 参数是 C# `int?`（上限 2^31−1），生产 Host 不可达；仅手工 JSON/未来客户端可达。 | `%TEMP%\lib1_r3_big2.py`、`lib1_r3_big3.py`、`lib1_r3_poison.py`；输出片段：`P8 import_order=2**63 -> UNKNOWN internal; chapters before/after: 1 2; leaked chapter: Leak 2 2`；`P8 max import_order: OK` → `normal append after max: UNKNOWN internal`；`P7 custom_rank=9223372036854775808 -> UNKNOWN internal`。 | ① handler 校验 `import_order <= 2^63−2`（并防 `max+1` 溢出）与 `custom_rank <= 2^63−1`；② 把 P8 的“创建 + 写 `import_order`”放入同一事务（失败回滚章节）；③ 至少将 `OverflowError` 映射为 `INVALID_REQUEST/validation`。 | 建议 DSH 在卡面 R-13/limitation 或 LIB-2 登记；不要求本 head 返修。 |

### 4.2 证据口径与合同字节专项

- **合同字节**：`Get-FileHash doc/plan/FEA-C07_API_INVENTORY.md` = `7C033BF76AF1726B71E1CE92A5B3C221D880CF7A36BFC44EF3D4467582D5457D`，与 FROZEN §1 / `verify_pins` 输出完全一致；`git log -- doc/plan/FEA-C07_API_INVENTORY.md` 最后改动为 `00a99622a`，`00a99622a..HEAD` 零 diff；`CONTRACT-UNFREEZE-2026-11-10-LIB1.md` 同样最后改动于 `00a99622a`。
- **FROZEN 变更合法性**：`e49855485` 对 FROZEN 的 7 行改动只更新 §1B 复核状态与 §5 新增“v1.6 待重冻”行，不改 C-07 pin、统计或条款；`allowed_paths` 明列 FROZEN，故不构成未授权契约字节。
- **证据表**：EV-LB-001..005 的 sha256 与工作树文件 **5/5** 匹配；4 日志均含 `EXIT=0`（dotnet 另含 878/0/11；pins 另含 `PIN_EXIT=0`、`API_CHECK_EXIT=0`、`C07_PIN=7c033bf7…`）。
- **“31+21”口径**：相对 base 的累计 diff 为 32 文件；r2 处置新增 `e49855485` 15 文件 + `de595f69d` 6 文件（卡面重叠 1），合计 21 个 file-change，与任务描述一致。

### 4.3 观察项（不构成 finding，不改变结论）

1. `CoreServiceClient.UpdateBookMetadataAsync` 的类型检查（`CoreServiceClient.cs:1599-1606`）显式放行 `null`（`is not null`），并在 `:1616-1620` 写 JSON null；Core 对文本 null → `INVALID_REQUEST`，对 `tags:null` 视为未提供 → `updated:true` no-op。当前无 Host 路径发送 null，未发现用户可见错误；建议 LIB-2 明确 null 语义或收紧客户端。
2. P5 服务端白名单含 `original_title`/`publisher`（`service.py:212-213`），超出卡面 Scope §1 列举的 6 个键；二者是 v2 既有列、additive、不改变 PREQ §8 键形状，r2 已记 NOT_RUN；建议在后续文档登记或收窄。
3. `test_patch_book_keeps_unprovided_fields`（`test_library_metadata.py:72-73`）与 `test_create_chapter_with_metadata`（`:121-122`）对“缺书”仍用 `pytest.raises(Exception)`；wire 层已用 `TARGET_NOT_FOUND` 钉住端到端 typed，不影响本次结论，建议后续改为 `BookNotFound`。
4. 证据表的 `commit` 列是“生成时产品 HEAD”而非“证据文件所在提交”；5 个文件实际在 `de595f69d` 入库，README 的 hash 是簿记后字节。该口径在 r1/r2 已使用，本报告按同一口径核验 hash 5/5，特此明示。

## 5. 门禁与测试（本次审查实测）

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `git rev-parse HEAD` + `git status --porcelain`（开始） | 16:20:15 | HEAD=`de595f69d`；clean（0 行） | — |
| 2 | `python -m pytest tests/storage/test_library_metadata.py tests/core/test_library_wire.py -q` | 16:25:35–16:25:38 | **13 passed** in 1.89s | **0** |
| 3 | `python -m pytest tests/storage tests/core tests/fea09/test_v7_migration.py tests/fea11/test_source_gate_unify.py -q` | 16:22:28–16:24:03 | **1251 passed, 1 warning** in 101.11s | **0** |
| 4 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo` | 16:22:21–16:27:21（测试执行 4m52s） | **878 passed / 0 failed / 11 skipped / 889 total** | **0** |
| 5 | `pwsh -NoProfile -File tools/governance/check.ps1` | 16:25:27–16:25:28 | **PASS**（3 warnings：11 非终态 / STATUS 3190 B·31 L / PLAN 6983 B·64 L） | **0** |
| 6 | `... check.ps1 -TaskPath doc/tasks/FEA-14-LIB-1.md` | 16:25:29–16:25:30 | **PASS**（同上 3 warnings） | **0** |
| 7 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 16:25:31 | **PIN AUDIT: PASS (all 18)**；C07=`7c033bf76af1` | **0** |
| 8 | `python tools/generate_api_inventory.py --check` | 16:31:42 | `OK: rendered counts match FEA-C07 doc`；1/69/6=76 | **0** |
| 9 | `Get-FileHash doc/plan/FEA-C07_API_INVENTORY.md` | 16:31:42 | `7C033BF7…2D5457D`（= pin） | — |
| 10 | 迁移字节脚本（base vs 5 heads，v1–v11 + v12 块序/顺序） | 16:23 前后 | `MISMATCHES: none`；`default_migrations order [1..12] OK` | **0** |
| 11 | diff 路径 vs `allowed_paths` 脚本 | 16:23 前后 | `changed=32`；**`OUT_OF_ALLOWED=0`** | **0** |
| 12 | C-07 正式表 vs 脚本 stdout 脚本 | 16:24 前后 | **`ALL_MATCH: True`**（73/1/6 行；69+4 非方法） | **0** |
| 13 | wire 探针（`%TEMP%\lib1_r3_probe*.py`、`lib1_r3_half.py`、`lib1_r3_big*.py`、`lib1_r3_poison.py`、`lib1_r3_null.py`） | 16:24–16:35 | R2-001/002、R-01/R-03/R-09/R-12/R-13 全部 PASS；R2-003 的 Core 空列表/非空书/缺书负例 PASS（Host 六处签名为静态 + 全量 C# 编译）；P5 null 观察项复现；R3-001 复现 | 0（探针本身 0；R3-001 为产品行为 UNKNOWN） |
| 14 | Canonical 5 份证据 SHA-256 与卡面表比对 | 16:21 前后 | **5/5 匹配**（EV-LB-001..005） | — |
| 15 | `git rev-parse HEAD` + `git status --porcelain`（写报告前） | 16:31:43 | HEAD 未变=`de595f69d`；clean | — |

> 说明：第 3/4 行的时点为 `Tee-Object` 日志创建/最后写入时间，分别与日志内 `101.11s`、`4 m 52 s` 自洽；未用卡面日志替代本次运行。

## 6. NOT_RUN（如实登记，不得记 PASS）

- **真实 Host↔Core 进程级联调**：4 个新 `CoreServiceClient` 方法未对活 Core 调用；C# 4 个端口测试只覆盖 NullHost 降级、Fake 记录（含 tags patch/空列表）与 Fake 的追加 `sort_order`，**不覆盖真实 IPC 读写映射**（README `:43` 已如实登记）。
- LIB 可见 UI（书架/工作台账单编辑、拖拽重排）= NOT_RUN（LIB-2/UI 卡）。
- tags 的 UI 管理与筛选 = NOT_RUN（数据面已实现并测试）。
- Volume 实体、`kind` 的 volume/episode/extra、`number_value`、`books.normalized_title` 唯一索引 = NOT_RUN（R-11 三项 deferral/另行裁决）。
- 真实大库（万级章）重排性能、sqlite 磁盘写失败/半迁移演练 = NOT_RUN。
- FEA-15 正式验收声明未审。
- P5 额外允许的 `original_title`/`publisher` 未做 wire 负例（additive 既有列，未发现与 PREQ 键形状冲突）。
- P5 文本写入与 tag 替换未包进同一事务；并发删除 tag（校验后、替换前）或 DB 故障导致的残余半写窗口未演练（确定性未知 tag 半写已消除）。
- **R3-001 的 Host 可达性 = 不可达**（C# `int` 上限 2^31−1）；该项仅以手工 wire 探针验证。
- 未做 Host P5 `null` 值的负例（观察项 §4.3，当前无调用方）。

## 7. 处置建议

1. **接受 r3 结论**：`approved`（P0=0/P1=0/P2=0/P3=1 accepted）。建议 DSH 将本报告作为 `de595f69d` 的 canonical r3 审查，更新卡面 `reviewer`/Closeout/`canonical_evidence_status`，按治理流程进入 `closed_with_limitations` 或 `done`；本报告不授权 push。
2. **R3-001（P3）**：不要求本 head 返修。建议在卡面 R-13/limitation 或 LIB-2 登记，至少做三件事之一：P7/P8 增加 64 位上界校验（并防 `max+1` 溢出）、P8 创建+`import_order` 更新入事务、`OverflowError` 映射 `INVALID_REQUEST`。
3. **文档口径**：建议后续登记 §4.3 的 P5 additive 扩展（`original_title`/`publisher`）、C# 客户端 `null` 语义、以及证据表 `commit` 列 = 生成 HEAD 的口径，避免后续审查重复解释。
4. **证据**：保留本轮 `e49855485` 生成、`de595f69d` 入库的 13/1251/878/18 日志与 C-07 pin `7c033bf7…`；C-07 v1.6 可随本卡收口重冻。
5. **下一步**：本卡收口后，按 DSH 的 S5 计划派发 FEA-14-LIB-2（UI/tags/Volume 承接）或下一冻结切片；本轮不 push、不关闭 Task。

## 8. 审查者声明

本报告由 lead 会话 `session-408d4e24-3789-4111-acde-983899601dad` 派发的**全新上下文子 agent**出具；审查者未参与 FEA-14-LIB-1 的实现、r1/r2 处置或返修，审查期间只读。唯一仓库写入为本报告；探针脚本、隔离数据库与日志全部在 `%TEMP%`（`lib1_r3_*`），未写真实 `%APPDATA%`，未 commit/push。PASS 仅基于本次 2026-11-10 16:20–16:35 的实测、脚本逐行比对与代码核对；未执行项已在 §6 记 NOT_RUN，未把未实测项写成 PASS。本报告只对 `de595f69dd4e5527a163e4c8ed6f390ce50a8a19` 的字节有效；head 变化即自动失效。
