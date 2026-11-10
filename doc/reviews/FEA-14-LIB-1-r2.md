---
task_id: FEA-14-LIB-1
reviewer: 独立子 agent（lead 会话 session-408d4e24-3789-4111-acde-983899601dad 派发；全新上下文，未参与实现；只读）
reviewer_kind: subagent
author: dsh
base_commit: f97f54476b097b7da9a9b7e1be1aff7e0ba16ba1
reviewed_head: e779674d56243c705abb0dd9aeb2b14fdcc3c204
decision: changes_requested
---

# Review：FEA-14-LIB-1（r2 独立复核）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，分支 `main`。审查者由 lead 会话 `session-408d4e24-3789-4111-acde-983899601dad` 派发，为全新上下文子 agent，未参与本卡实现。
- **被审 head = `e779674d56243c705abb0dd9aeb2b14fdcc3c204`**（证据提交）；产品/文档提交 `00a99622ad9b06b6b27ca34a5b4c192a87a60f9b`；r1 被审 head `83e45cfe54fb05bd0f4b0f6620e333b2c8e8d03e`。
- **diff 基线 = `f97f54476b097b7da9a9b7e1be1aff7e0ba16ba1`**（`83e45cfe5` 的父提交）。卡面 `base_commit: 8e39bb72c` 是 FONT-1 收口点；实测 `8e39bb72c..f97f54476` 仅含 `f3b1ab810`、`f97f54476` 两个 FONT-1 文档提交（FONT-1 卡/r5 报告/STATUS/PLAN/ledger + LIB-1 冻结），不含 LIB-1 产品字节。用 `f97f54476` 可把 LIB-1 变更从 FONT-1 收口文档中隔离；两种基线的产品 diff 等价。
- 变更面：`f97f54476..e779674d5` 共 **31 文件 / +1309 / −108**；其中 r1 处置提交 `00a99622a` 为 12 文件，证据提交 `e779674d5` 为 6 文件（卡面 + 5 份证据，无产品字节）。
- 审查开始 `2026-11-10T15:40:12+08:00`、结束（写报告前）`15:54:04+08:00`；两次 `git rev-parse HEAD` 均为 `e779674d5`，两次 `git status --porcelain` 均 **clean（0 行）**。
- 只读纪律：仓库内唯一写入为本报告；探针脚本与临时库全部写在 `%TEMP%` 的隔离目录（`lib1_r2_*`），未写真实 `%APPDATA%`；未 commit/push，未改源码/测试/契约/卡面/证据。
- 本报告只对 `e779674d5` 的字节有效；head 变化即自动失效。

## 1. 结论

**`changes_requested`**（**P0=0 / P1=1 / P2=2 / P3=4**）。

正面：r1 的 R-01、R-03、R-05、R-06、R-07、R-08、R-09、R-10、R-11、R-12、R-13 经逐项核对**已真正关闭**；v1–v11 迁移 NAME/SQL 逐字节未变；C-07 正式成员表与 `generate_api_inventory.py` stdout **逐行一致**（69 方法 + 4 非方法成员，`ALL_MATCH: True`）；C-07 pin `7c033bf7…` 与当前文件 SHA-256 一致，`verify_pins` 18/18；31 个变更文件全部落在 `allowed_paths`；4 个证据日志均记录 `HEAD=00a99622a` 与 dirty 状态，计数与本次实测一致；全量 App.Tests **877 passed / 0 failed / 11 skipped**。

阻断项：

1. **R-02 未完全关闭（P1）**：P5 传未知 `tag_id` 时 `TagNotFound` 未被捕获，wire 返回 `UNKNOWN/internal`（不是 typed）；且当同一 patch 还带文本字段时，文本字段已在报错前写入（实测 title 变为 `HalfWrite`），违反“先校验后写”的原子语义。
2. **R-04 未关闭（P2）**：`create_chapter` 的 `next_order` 取 `max(import_order)+1`，导致 P8 传重复/较小 `import_order` 时 `sort_order` 冲突；实测连续三次 `import_order=1` 的创建及随后一次普通创建，`sort_order` 全为 3（`[1,2,3,3,3,3]`），卡面/README 声称的“sort_order 唯一”不成立。

## 2. R-01–R-13 逐项关闭表

| ID | r1 级别 | r1 问题（摘要） | 本次判定 | 证据 |
|---|---|---|---|---|
| R-01 | P1 | P5/P6/P8 书不存在时抛 `BookNotFound` 逃逸为 `UNKNOWN/internal` | **CLOSED** | 临时库 `CoreServiceServer.dispatch_request` 探针：P5/P6/P8 传 `book_id="nope"` 均 `TARGET_NOT_FOUND/not_found`；P7 缺章 `TARGET_NOT_FOUND/not_found`。代码 `core_service.py:5153/5169/5212` 已捕 `BookNotFound`；测试 `tests/core/test_library_wire.py:91-101` 覆盖三命令。 |
| R-02 | P1 | P5 `tags` 替换语义完全未实现，AC1 仍标 MET | **OPEN（部分修复）** | 有效 tag 的 t1→t2 全量替换已成立（探针 + `test_library_wire.py:102-114`）。但未知 tag id → **`UNKNOWN/internal`**：`TagNotFound`（`application/library/errors.py:22-25`）是 `LibraryError` 而非 `ValueError`，`core_service.py:5153-5156` 只捕 `BookNotFound`/`(TypeError, ValueError)`，异常落到 `core_service.py:7084` 的泛化兜底。另：`service.py:221-223` 先 `update_book` 写文本字段、后 `_replace_book_tags` 校验 tag id；探针 `{"title":"HalfWrite","tags":["missing-tag"]}` 返回 `UNKNOWN/internal` 但 title 已落库。服务层测试 `test_library_metadata.py:135-137` 只用 `pytest.raises(Exception)`，未钉住异常类型；wire 层无未知 tag 负例。 |
| R-03 | P2 | P8 响应无 `sort_order`；客户端读 `import_order` → SortOrder 恒 0；kind 被丢弃 | **CLOSED** | `core_service.py:5221` P8 响应含 `sort_order`；`CoreServiceClient.cs:1702` 读 `ReadInt(result,"sort_order")`；探针 P8 `import_order=1` 返回 `sort_order=3`。`ChapterSummary` 仍四字段（`CoreServiceClient.cs:28`），`kind` 不投影已在卡面 out_of_scope（`:59`）、AC4（`:80`）与 README limitation 如实登记。 |
| R-04 | P2 | `create_chapter_with_metadata` 用 `import_order` 覆盖 `sort_order`，重复/断档 | **OPEN（部分修复）** | 单次创建不再覆盖：`service.py:295-299` 只改 `import_order`。但 `create_chapter` 的 `next_order` 取 `max(import_order)+1`（`service.py:146-147`），`sort_order` 与 `import_order` 同值（`:155-156`）；实测 C1/C2 后连续三次 P8 `import_order=1`，三次均得 `sort_order=3`，随后普通创建也 `sort_order=3`，最终 `[1,2,3,3,3,3]`、`sort_order unique? False`。测试 `test_library_metadata.py:140-150` 只创建一个带 `import_order` 的章，未覆盖第二次创建/后续普通创建；卡面 `:89`“重复 import_order 不破坏 sort_order 唯一”与 README `:33`“创建时追加 max+1、保证唯一”均被实测证伪。 |
| R-05 | P2 | C-07 正式成员表仍 54 行、S5 节口径未同步、`--check` 只比计数 | **CLOSED** | 自写脚本逐行比对 `FEA-C07_API_INVENTORY.md` 正式表与 `generate_api_inventory.py` stdout：`IReaderProgressSink 1`、`IHostController 69 + 4 非方法`、`IRunController 6`，**`ALL_MATCH: True`**（含顺序与返回类型）。S5 节只剩 P16–P25（10 条，无 P1–P15）；统计口径 25=4+4+7+5+5、已落地 15、剩余 10、目标 79、三接口 86 自洽；`--check` EXIT 0（1/69/6=76）。 |
| R-06 | P2 | 29 文件中 7 个不在 `allowed_paths` | **CLOSED** | 逐路径脚本：`changed=31`，`out_of_allowed=0`。`doc/reviews/FEA-14-LIB-1-*.md`、`doc/reviews/CONTRACT-UNFREEZE-*.md`、`verification/FEA-14-LIB-1/**` 通配均生效；schema.py、entities.py、4 个 v12 适配测试、`LibraryMetadataPortTests.cs` 已补入清单。 |
| R-07 | P3 | 冻结记录缺 v1.3–v1.5 行、§1B/§2 条件 3/§5 不自洽 | **CLOSED** | `FEA-CONTRACT-FROZEN-C07.md` §1 含 v1.1–v1.6 原值 + r1 锚（`:15-21`）；§1B 记录 v1.5/v1.6 由本 r2 覆盖（`:29`）；§2 条件 3 为 `1/69/6=76`（`:41`）；§3 已落地 15 条（`:49`）；§5 含 v1.3–v1.6 四行（`:86-89`）。`verify_pins` 18/18；自行 `Get-FileHash` 得 C07=`7c033bf76af1726b71e1ce92a5b3c221d880cf7a36bfc44ef3d4467582d5457d`，与 §1 pin 完全一致。 |
| R-08 | P3 | 证据日志头记 base HEAD；README AC1/AC3 描述不实 | **CLOSED** | 4 个日志头均为 `HEAD=00a99622ad9b06b6b27ca34a5b4c192a87a60f9b` 并记录 dirty 列表（dotnet `dirty=[]`；pytest 记 dotnet 日志；regression 记前两份；pins 记 README+4 日志）；计数 12/1250/877/0/11/18/69-76 与本次实测一致。README AC1 已写“无书 → `TARGET_NOT_FOUND`”，AC3 已写“未知/缺失/重复 id → `INVALID_REQUEST`，`ChapterNotFound` 在该路径不可达”，均与实测一致。README `:12` 的“非法值 → `INVALID_REQUEST`”仍过宽（未知 tag id 是反例），归入 R-02/P3 表述问题。 |
| R-09 | P3 | `patch_chapter_metadata` 用微秒 `datetime.now` 写 `updated_at` | **CLOSED** | `service.py:270` 改为 `chapter.updated_at = utc_now()`；文件已无局部 `datetime` 导入；探针读回 `2026-11-10T07:44:19.487+00:00`（毫秒，与 `entities.py:15-16` 一致）。 |
| R-10 | P3 | `test_fonts` 版本断言恒真；v12 legacy 测试空库；Fake 新字段无测试 | **CLOSED** | `tests/storage/test_fonts.py:50` 恢复 `read_schema_version(conn) == LATEST == 12`；`test_library_metadata.py:33-58` 先迁移到 v11、插入真实 books/chapters 行、再升级到 12，断言字段保留且 `custom_rank IS NULL`；新增 `LibraryMetadataPortTests.cs` 3 个 `[Fact]`，消费 Fake 新成员并覆盖 NullHost 降级；全量 App.Tests 877（较 r1 的 874 +3）。测试保真度残余见 §2.1 P3-2。 |
| R-11 | P3 | PREQ/DDL 与实现静默分叉，未登记 deferral | **CLOSED（已裁决/登记）** | 卡面「范围裁决」`:100-108` 登记三项 deferral：`kind` 按既有 `ChapterType`（paged/webtoon）、`number` 落 `chapter_number`（`number_value` 推迟）、`books.normalized_title` 唯一索引推迟；与 `verification/FEA-14-S5-PREQ-1/ddl-v10-plan.md` §2.5 对应，且不改 PREQ §8 wire 键形状。 |
| R-12 | P3 | `custom_rank` write-only；P6 自定义排序未实现 | **CLOSED（已登记）** | 卡面 out_of_scope `:57` 与 R-12 `:108` 明确“只写入/持久化、读取投影/参与排序/UI 留 LIB-2”；README limitation 同步。探针验证 `custom_rank` 0/null 可写可读回，重排不参考它。 |
| R-13 | P3 | 空 `ordered_ids` 拒绝；bool/float `import_order`；`custom_rank` 静默截断；重复 `import_order` | **CLOSED（wire 边界）** | 探针：空书 `[]` → OK；非空书 `[]`/未知 id/重复 id → `INVALID_REQUEST`；P8 `import_order=True/1.0/"1"` → `INVALID_REQUEST`；P7 `custom_rank=True/1.5/-1/"3"` → `INVALID_REQUEST`，`0`/`null` → OK。重复 `import_order` 被允许，但其 `sort_order` 冲突归 R-04。Host 层空列表仍被拒，见 §2.1 P3-1。 |

### 2.1 r2 新发现（不在 r1 清单内）

| ID | 级别 | 文件/行 | 问题 | 证据 |
|---|---|---|---|---|
| P3-1 | P3 | `IHostController.cs:219`；`HostController.cs:642`；`CoreServiceClient.cs:1618` | **Host 端口与 wire 语义覆盖不一致**：① P5 Host 端口是 `IReadOnlyDictionary<string,string>`，无法表达 `tags`（tag id 列表），AC1 的 tags 替换只在 Core/wire 可达，未登记为 limitation；② Host/CoreServiceClient 对空 `ordered_ids` 直接拒绝（`Count == 0`），而 R-13 明确空书 `[]` 是唯一 no-op 编码，Host 路径不可达。 | 代码逐行；探针 P6 空书 `[]` 在 Core 成功。 |
| P3-2 | P3 | `FakeHostController.cs:278`；`LibraryMetadataPortTests.cs:47-57` | **C# 测试保真度**：Fake 的 `CreateChapterWithMetadataAsync` 返回 `SortOrder = importOrder ?? 0`，仍是 R-04 修复前的“sort_order=import_order”语义；测试断言 `importOrder:7 → SortOrder:7`，与真实 Core（sort_order 为追加位）相反，给出虚假信心。没有任何测试覆盖 `CoreServiceClient.CreateChapterWithMetadataAsync` 读 `sort_order` 的映射；README 已如实把“真实 IPC 映射”记 NOT_RUN，但测试名/断言未体现该边界。 | 代码逐行；`dotnet test` 3 个新测试通过。 |
| P3-3 | P3 | `doc/tasks/FEA-14-LIB-1.md:71`；`src/infrastructure/sqlite/schema.py:179-186` | **卡面 Scope §2 与实现不符**：卡面写“`books` 加 `author/series_title/description/notes` 列（additive migration v12）”，但这些列在 v2 迁移已存在；v12 实际只加 `chapters.custom_rank`。不影响 AC5 的“v12 additive”结论，但会误导后续审查。 | `MIGRATION_V2_SQL` 含四列；`MIGRATION_V12_SQL` 仅一条 `ALTER TABLE chapters ADD COLUMN custom_rank INTEGER;`。 |
| P3-4 | P3 | `src/infrastructure/sqlite/schema.py:879-884` | **V12 常量块插在 V10 与 V11 之间**：文件定义顺序为 10→12→11，`default_migrations()` 顺序仍为 11→12（`:942-943`），功能正确；但按文件顺序阅读/未来按版本号排序时易误判，建议把 V12 块移到 V11 之后。 | 代码逐行；迁移脚本比对 v1–v11 未受影响。 |

## 3. AC 逐项判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 书元数据 | **PARTIAL** | patch 保留未提供字段、title 非空、未知字段拒绝、有效 tag 的 t1→t2 替换、无书 `TARGET_NOT_FOUND` 均实测成立；但未知 tag id → `UNKNOWN/internal`，且文本字段会在报错前落库（R-02 残余），卡面 `<<MET>>` 不成立。 |
| AC2 章元数据 | **MET** | kind/custom_rank/number/title/subtitle/notes 均落库；非法 kind → `INVALID_REQUEST`；无章 → `TARGET_NOT_FOUND`；`custom_rank` 边界按 R-13 收紧；`updated_at` 毫秒格式。 |
| AC3 章重排 | **MET** | 缺/多/重复 → `INVALID_REQUEST`；空书 `[]` → 成功 no-op；非空书 `[]` → `INVALID_REQUEST`；成功后 `sort_order` 连续重写、读取顺序与请求一致；验证先于写库。R-12 的自定义/数字排序不在 AC3 字面内且已登记 limitation。 |
| AC4 创建带元数据章 | **PARTIAL** | title/kind/number/import_order 落库、P8 响应含 `sort_order`、父书不存在 typed、Host 读 `sort_order`、kind 不投影已登记 limitation；但 R-04 残余使重复/较小 `import_order` 后的 `sort_order` 冲突，卡面 `<<MET>>` 不成立。AC4 文字“返回 chapter_id/title/kind/number”指 Core 响应（确实含 kind）；Host `ChapterSummary` 四字段不含 kind，卡面已用 limitation 明确，不构成新的文字冲突，但建议 AC4 把“Core 响应”与“Host 投影”分开写。 |
| AC5 迁移/契约/门禁 | **MET** | v12 仅 `ALTER TABLE chapters ADD COLUMN custom_rank INTEGER;`，v1–v11 NAME/SQL 11/11 逐字节相同；旧 v11 书/章行升级后字段保留、`custom_rank IS NULL`；P5–P8 键形状符合 PREQ §8（P8 的 `sort_order` 为可选 additive）；C-07 正式表逐行等于 stdout；`--check` EXIT 0；`verify_pins` 18/18 且 C07 pin 匹配。 |
| AC6 证据 | **MET** | 4 个日志含 EXIT 与生成时 HEAD/dirty；定向 12 passed、回归 1250 passed、App.Tests 877/0/11、pins 18/18、API 69/76 均与本次实测一致；NOT_RUN 已登记。README AC1 的“非法值 → INVALID_REQUEST”过宽归 R-02 表述问题。 |

## 4. 必查项判定

| # | 必查项 | 判定 | 说明 |
|---|---|---|---|
| 1 | v12 additive、v1–v11 迁移字节未变、`custom_rank` 四路径一致 | **CLOSED** | 自写脚本比对 base/head 的 `MIGRATION_V1..V11_{NAME,SQL}`：11/11 `IDENTICAL`；v12 仅一条 `ALTER TABLE`；`_CHAPTER_COLUMNS`、`add_chapter`、`update_chapter`、`_row_to_chapter` 均含 `custom_rank`。 |
| 2 | wire P5–P8 形状 vs PREQ §8 | **PARTIAL** | 键形状匹配（P5 `book_id,patch{…tags?}`；P6 `book_id,ordered_ids[]`；P7 `chapter_id,patch{…}`；P8 `book_id,title,kind?,number?,import_order?` → `chapter_id,title,kind,number` + 可选 `sort_order`）；P5 未知 tag 的 typed 错误不成立（R-02）。 |
| 3 | Host 三层/四层签名一致、降级不抛 | **CLOSED（带 P3）** | `IHostController`/`HostController`/`NullHostController`/`FakeHostController`/`HostRuntime`/`CoreServiceClient` 六个位置的四组签名逐字一致；NullHost 返回 false/null；HostController 对未就绪/异常返回 false/null 不抛。P3-1 的 tags/空列表覆盖差异见 §2.1。 |
| 4 | C-07 正式成员表逐行等于脚本 stdout；S5 节只剩 P16–P25；统计自洽 | **CLOSED** | 自写脚本 `ALL_MATCH: True`（69 方法 + 4 非方法，含顺序与返回类型）；S5 节 10 行 P16–P25；25=4+4+7+5+5、15 已落地、10 剩余、69+10=79、86 合计均自洽。 |
| 5 | FROZEN-C07 §1 pin 链/§1B/§2/§3/§5；`verify_pins` 18/18；C07 SHA 匹配 | **CLOSED** | §1 六代 pin + r1 锚；§1B 记录 v1.5/v1.6 由 r2 覆盖；§2 条件 3 `1/69/6=76`；§3 已落地 15；§5 四行 v1.3–v1.6；`verify_pins` PASS 18/18；C07 实际 SHA-256=`7c033bf7…` 与 pin 一致。 |
| 6 | 证据 provenance（HEAD/dirty/计数/哈希） | **CLOSED（带表述 P3）** | 4 日志头 HEAD=`00a99622a` + dirty；计数 12/1250/877/0/11/18/69-76 与实测一致；5 份 Canonical 证据 SHA-256 与卡面表 5/5 匹配。README `:12`“非法值 → INVALID_REQUEST”与未知 tag 实测不符，归 R-02。 |
| 7 | diff ⊆ `allowed_paths`；无未授权契约字节 | **CLOSED** | 31/31 覆盖，`out_of_allowed=0`；契约字节仅 C-07 inventory/freeze + UNFREEZE LIB1 + r1 报告 + 卡面/证据/STATUS/PLAN/ledger，无 C-02/C-03 等其他契约改动。 |
| 8 | 扫新 P0/P1/P2 | **P0=0 / P1=1 / P2=2** | P1=R-02 残余（未知 tag 非 typed）；P2=R-04 残余（`sort_order` 冲突）、P5 文本字段先写后报错；P3 见 §2.1 四项。 |

## 5. 门禁与测试（本次审查实测）

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `git rev-parse HEAD` + `git status --porcelain`（开始） | 15:40:12 | clean；HEAD=`e779674d5` | — |
| 2 | `python -m pytest tests/storage/test_library_metadata.py tests/core/test_library_wire.py -q` | 15:47:48–15:47:50 | **12 passed** in 1.82s | **0** |
| 3 | `python -m pytest tests/storage tests/core tests/fea09/test_v7_migration.py tests/fea11/test_source_gate_unify.py -q`（首跑） | 15:47:56–15:49:52 | 通过（计数未捕获） | **0** |
| 4 | 同上（重跑捕获计数） | 15:50:01–15:51:57 | **1250 passed, 1 warning** in 115.30s | **0** |
| 5 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo`（全量） | 15:47:45–15:53:23 | **877 passed / 0 failed / 11 skipped / 888 total**，5m26s | **0** |
| 6 | `pwsh -NoProfile -File tools/governance/check.ps1` | 15:50:05–15:50:06 | PASS（3 warnings：11 非终态 / STATUS 3190 B·31 L / PLAN 6983 B·64 L） | **0** |
| 7 | `... check.ps1 -TaskPath doc/tasks/FEA-14-LIB-1.md` | 15:50:13–15:50:14 | PASS（同上 3 warnings） | **0** |
| 8 | `python tools/generate_api_inventory.py --check` | 15:50:15 | `OK: rendered counts match FEA-C07 doc`；1/69/6=**76** | **0** |
| 9 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 15:56:41 | **PIN AUDIT: PASS (all 18)**；C07=`7c033bf7…` | **0** |
| 10 | `Get-FileHash` C-07 inventory | 15:56:41 | `7c033bf76af1726b71e1ce92a5b3c221d880cf7a36bfc44ef3d4467582d5457d`（= pin） | — |
| 11 | 迁移字节比对脚本（base vs head，v1–v11） | 15:43 前后 | **v1–v11 identical: True**；head 版本集合 `1..12` | **0** |
| 12 | diff 路径 vs `allowed_paths` 脚本 | 15:43 前后 | `changed=31`；**`out_of_allowed=0`** | **0** |
| 13 | C-07 正式表 vs 脚本 stdout 逐行脚本 | 15:42 前后 | **`ALL_MATCH: True`**（69+4 / 1 / 6） | **0** |
| 14 | wire 探针（`%TEMP%\lib1_r2_probe.py`、`lib1_r2_probe2.py`） | 15:44–15:46 | R-01 三命令 typed；R-02 未知 tag=`UNKNOWN/internal` 且文本半写；R-03 `sort_order=3`；R-04 重复 import_order 全部 `sort_order=3`；R-13 边界符合 | **0** |
| 15 | Canonical 5 份证据 SHA-256 与卡面表比对 | 15:41 前后 | **5/5 匹配**（EV-LB-001..005） | — |
| 16 | `git rev-parse HEAD` + `git status --porcelain`（结束，写报告前） | 15:54:04 | clean；HEAD 未变=`e779674d5` | — |

## 6. NOT_RUN

- 真实 Host↔Core 进程级联调：4 个新 `CoreServiceClient` 方法未对活 Core 调用；C# 3 个新测试只覆盖 NullHost 降级/Fake 记录/Fake 投影，不覆盖真实 IPC 映射（README 已登记 NOT_RUN）。
- LIB 可见 UI（书架/工作台账单编辑、拖拽重排）= NOT_RUN（LIB-2/UI 卡）。
- `tags` 的 UI 管理与筛选 = NOT_RUN（数据面已实现并测试）。
- Volume 实体、`kind` 的 volume/episode/extra、`number_value`、`books.normalized_title` 唯一索引 = NOT_RUN（R-11 三项 deferral / 另行裁决）。
- 万级章重排性能、真实大库迁移、sqlite 磁盘写失败/半迁移 = NOT_RUN。
- FEA-15 正式验收声明未审。
- 未对 P5 额外允许的 `original_title`/`publisher` 做 wire 负例（属 additive 扩展，未发现与 PREQ 键形状冲突）。

## 7. 处置建议（按优先级）

1. **P1（必须先修）**：在 `handle_update_book_metadata` 增加 `except TagNotFound`（建议映射 `TARGET_NOT_FOUND/not_found`，与 Book/Chapter 缺失一致；若 DSH 视为校验错误则 `INVALID_REQUEST`），并补 wire 未知 tag 负例；同时把 tag id 全量校验移到任何写入之前（先 `_require_tag` 全部 tag，再 `update_book`/替换 tag），或把文本 patch 与 tag 替换包进同一事务，消除“报错但 title 已改”的半写。
2. **P2（必须先修）**：修正 `create_chapter` 的排序来源——`import_order` 取 `max(import_order)+1`，`sort_order` 取 `max(sort_order)+1`（或在 metadata 路径创建后重算 `sort_order`）；补“两次 P8 同 `import_order` + 随后一次普通创建”的测试；同步修正卡面 `:89` 与 README `:33` 的“唯一”表述。
3. **P3（建议修/登记）**：① Host P5 增加可表达 `tags` 的端口（或明确登记为 LIB-2 limitation），Host/CoreServiceClient 对空 `ordered_ids` 与 wire 空书 no-op 对齐或登记；② Fake 的 `CreateChapterWithMetadataAsync` 改为按真实 `sort_order` 语义返回，并补一个 `CoreServiceClient` 映射测试（或明确把该映射列入 NOT_RUN 且修正测试名/断言）；③ 修正卡面 Scope §2 的 books 列描述；④ 把 schema.py 的 V12 常量块移到 V11 之后。
4. 修复后在**新 head** 重生成 4 份证据日志与 Canonical Evidence 哈希，重跑 §5 全部门禁，再派 r3 独立复核；本 r2 报告不覆盖修复后的字节。

## 8. 审查者声明

本报告由 lead 会话 `session-408d4e24-3789-4111-acde-983899601dad` 派发的全新上下文子 agent 出具；审查者未参与 FEA-14-LIB-1 的实现或返修，审查期间只读。唯一仓库写入为本报告；探针脚本与临时库均在 `%TEMP%` 隔离目录，未写真实用户数据。PASS/FAIL 基于本次 2026-11-10 15:40–15:56 的实测、脚本比对与逐行代码核对；未执行项已在 §6 记 NOT_RUN，未把未实测项写成 PASS。本报告只对 `e779674d56243c705abb0dd9aeb2b14fdcc3c204` 有效。
