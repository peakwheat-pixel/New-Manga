---
id: FEA-14-LIB-1
title: FEA-14 切片 LIB-1：书/章元数据编辑与顺序（复用 PREQ 预冻结 wire P5–P8）
kind: implementation
governance_version: 3
status: closed_with_limitations
approval: **DSH 2026-11-10 冻结**（`ADJ-2026-11-10-FEA14-S5-SCOPE` §2.1/§2.2；PREQ-1 wire 预冻结 LIB P5–P8；侦察 `recon.md` §2.2）
suggested_owner: dsh
owner: dsh
reviewer: r3 独立复核 approved（`doc/reviews/FEA-14-LIB-1-r3.md`，P0/P1/P2=0；P3=1 accepted）
depends_on:
  - FEA-14-S5-PREQ-1
base_commit: 8e39bb72c
branch: null
worktree: null
integration_commit: e49855485
delivery_head: de595f69d
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-14-LIB-1
allowed_paths:
  - doc/tasks/FEA-14-LIB-1.md
  - doc/reviews/FEA-14-LIB-1-*.md
  - doc/handoffs/FEA-14-LIB-1-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/plan/FEA-C07_API_INVENTORY.md
  - doc/plan/FEA-CONTRACT-FROZEN-C07.md
  - verification/FEA-14-LIB-1/**
  - src/application/library/service.py
  - src/application/library/ports.py
  - src/infrastructure/sqlite/library.py
  - src/bootstrap/core_assembly.py
  - src/bootstrap/core_service.py
  - apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs
  - tests/storage/test_library_metadata.py
  - tests/core/test_library_wire.py
  - src/infrastructure/sqlite/schema.py
  - src/domain/books/entities.py
  - doc/reviews/CONTRACT-UNFREEZE-*.md
  - tests/storage/test_fonts.py
  - tests/storage/test_upgrade_schema_data.py
  - tests/fea09/test_v7_migration.py
  - tests/fea11/test_source_gate_unify.py
  - apps/desktop-avalonia/tests/NewManga.App.Tests/LibraryMetadataPortTests.cs
out_of_scope:
  - 不引入 Volume 实体（PREQ 未纳入；另行裁决）
  - 不改冻结契约字节（C-07 统计节/成员表按实现落地更新，pin 重算须记录）
  - 不做批量重排 UI（只做数据面 + 既有命令）
  - 不修改 FEA-15 正式验收声明
  - 不实现 P6 自定义排序语义（`custom_rank` 只写不读、不参与排序；数字排序由 `sort_order` 承担）——留 LIB-2
  - 不实现 DDL 计划中的 volume/episode/extra kind、`number_value` 列、`books.normalized_title` 唯一索引（R-11 三项 deferral，见「范围裁决」）
  - 不投影 chapter `kind` 到 Host `ChapterSummary`（既有 DTO 仅四字段；LIB-2 扩展 DTO）
---

# FEA-14-LIB-1：书/章元数据编辑与顺序

## 背景

FEA-14 S5 LIB 切片（FEA-00 §12.2/§15.6）需要书/章元数据编辑与章顺序：`UpdateBookMetadataAsync`/`ReorderChaptersAsync`/`UpdateChapterMetadataAsync`/`CreateChapterWithMetadataAsync`（PREQ §3/§8 P5–P8，minor 3）。现有库已能创建书/章，但缺元数据 patch/重排/chapter kind。

## Scope 冻结（2026-11-10，DSH）

1. Core：`LibraryMetadataService`（书 patch：title/author/series_title/description/notes/tags；章 patch：kind/custom_rank/number/title/subtitle/notes；重排：ordered_ids 全量校验；创建带元数据章）。
2. 数据面：复用既有 `books` 元数据列（`author/series_title/description/notes` 自 v2 迁移起已存在）；v12 仅 additive 增加 `chapters.custom_rank` 列；`book_tags` 既有表复用（P5 tags 全量替换）。
3. Host：P5–P8 四条命令（additive；旧签名不变），按 C-07 冻结记录流程更新 inventory 并重算 pin。
4. 证据：pytest 定向/全量、App.Tests、check/pins/API inventory。

## Acceptance Criteria

- [x] **AC1 书元数据**：patch 部分字段（其余保留）；title 非空校验；tags 替换语义（tag id 列表，先校验后写）；无书 → typed 错误。 <<MET>>
- [x] **AC2 章元数据**：kind（paged/webtoon）/custom_rank/number/title/subtitle/notes 更新；非法 kind 拒绝；无章 → typed。 <<MET>>
- [x] **AC3 章重排**：`ordered_ids` 必须覆盖全书章（缺/多/重复 → typed；空书 `[]` no-op）；sort_order 连续重写；重排后读取顺序一致。自定义排序语义见 R-12 limitation。 <<MET>>
- [x] **AC4 创建带元数据章**：title/kind/number/import_order 落库；返回 chapter_id/title/kind/number（+可选 sort_order）；父书不存在 → typed。Host 投影不丢 `SortOrder`；`kind` 未进入既有 `ChapterSummary` DTO（见 limitation）。 <<MET>>
- [x] **AC5 迁移/契约/门禁**：v12 additive（旧行字段级无损）；P5–P8 按 PREQ §8 形状；`generate_api_inventory.py --check` EXIT 0；`verify_pins` 18/18（C-07 pin 更新记录）。 <<MET>>
- [x] **AC6 证据**：定向 pytest/App.Tests 通过；`verification/FEA-14-LIB-1/` 日志含 EXIT 与生成时 HEAD；NOT_RUN（LIB-2 UI/Volume 实体/tags-in-UI）如实登记。 <<MET>>

## r1 处置记录（2026-11-10，对 `83e45cfe5` 的 changes_requested）

- **R-01（P1，已修）**：P5/P6/P8 的“书不存在”改捕 `BookNotFound`（`ChapterNotFound` 兄弟类，原实现逃逸到泛化兜底 → `UNKNOWN/internal`）；补 wire 负例：三条命令传 `book_id="nope"` → `TARGET_NOT_FOUND/not_found`。
- **R-02（P1，已修 + r2 补修）**：P5 实现 `tags` 替换语义——`patch_book_metadata` 白名单加入 `tags`（tag id 列表），`_replace_book_tags` **先全量校验再删旧/加新**；r2 补修：未知 tag id 的 `TagNotFound` 映射为 `TARGET_NOT_FOUND/not_found`，tag id 校验前移到任何写入之前（半写消除），文本字段只接受 `str`（拒绝隐式 `str()` 强转）；补 t1→t2 替换、未知 tag typed、半写与类型负例。
- **R-03（P2，已修）**：Core P8 响应增加可选键 `sort_order`；`CoreServiceClient.CreateChapterWithMetadataAsync` 改读该键（原读不存在的 `import_order` → `SortOrder` 恒 0）；`kind` 仍不投影，登记 limitation（既有 DTO 仅四字段）。
- **R-04（P2，已修 + r2 补修）**：`create_chapter_with_metadata` 不再用 `import_order` 覆盖 `sort_order`；r2 补修：`create_chapter` 的 `import_order` 与 `sort_order` 各自取自己的 max+1（`sort_order` 不再受重复/较小 `import_order` 影响），补「三次同 `import_order=1` + 随后普通创建 → sort_order 1..6 唯一」测试。
- **R-05（P2，已修）**：C-07 正式成员表按脚本 stdout 重建并同步 P1–P15（69 方法 + 4 非方法成员，逐行一致，核对脚本 `ALL_MATCH: True`）；「S5 计划追加」节只留 P16–P25；统计/变更类别/§2/§3 口径同步；UNFREEZE **v1.6**（pin `7c033bf76af1…`）。
- **R-06（P2，已修）**：allowed_paths 补 8 项（schema.py、entities.py、UNFREEZE 载体、4 个 v12 适配测试、新增 C# 端口测试）；登记“释放清单不完整”更正，不追溯判为越权内容。
- **R-07（P3，已修）**：冻结记录 §1 补 v1.3–v1.6 pin 链（v1.3 `59ab90f7…` / v1.4 `8d92a32f…` / v1.5 `9c1eb974…` / v1.6 `7c033bf7…`，原值保留）、§1B 复核引用、§2 条件 3 改 **1/69/6=76**、§3 已落地 15 条口径、§5 补 v1.3–v1.6 四行。
- **R-08（P3，已修）**：证据日志在 r1 处置后的最终 head 重新生成（记录生成时 HEAD 与 `git status`）；README AC1/AC3 描述修正（wire 无书 → `TARGET_NOT_FOUND`；strict reorder 未知/缺失 id → `INVALID_REQUEST`，`ChapterNotFound` 在该路径不可达）。
- **R-09（P3，已修）**：`patch_chapter_metadata` 的 `updated_at` 改用 `domain.books.entities.utc_now()`（毫秒，与全库一致）；移除局部 `datetime` 导入。
- **R-10（P3，已修）**：`test_fonts` 恢复精确版本断言；v12 legacy 测试插入真实 v11 书/章行后升级，断言字段保留 + `custom_rank IS NULL`；新增 C# `LibraryMetadataPortTests`（3 测试：NullHost 降级不抛、Fake 记录元数据/重排调用、CreateWithMetadata 投影四字段）消费 Fake 新字段。
- **R-11（P3，已裁决/登记）**：见「范围裁决」——P7 语义按既有 `ChapterType`（paged/webtoon）+ `chapter_number` 文本编号；DDL 计划 volume/episode/extra、`number_value`、`normalized_title` 三项登记为正式 deferral。
- **R-12（P3，已登记）**：`custom_rank` 为写投影（读回/重排不参考），P6 “自定义排序保位/数字排序重排”未实现——留 LIB-2；AC3 只声称 ordered_ids 严格重排。
- **R-13（P3，已修）**：P6 允许空 `ordered_ids`（空书 no-op；非空书仍 exact-cover 拒绝）；P8 显式拒绝 bool/float/str `import_order`；`custom_rank` 拒绝 bool/float/负值/字符串（取消静默 `int()` 截断），仅接受非负整数或 null；P8 重复 `import_order` 允许（来源顺序可重复，`sort_order` 唯一）。

## 范围裁决（R-11/R-12，DSH 2026-11-10）

R-11 不让 PREQ/DDL 与实现静默分叉，三项正式登记为 deferral（不改变 PREQ 预冻结 wire 形状）：

1. `kind`：按既有 `ChapterType` 枚举 `paged`/`webtoon`；DDL v10 计划中的 `volume`/`episode`/`extra` 属 Volume/ChapterKind 概念，随 Volume 实体另行裁决。
2. `number`：落既有 `chapters.chapter_number` 自由文本；`number_value` 数字排序列推迟（P6 排序由 `sort_order` 承担）。
3. `books.normalized_title` 唯一索引推迟；重名规范化（含是否 NFKC）待用户裁决（ADJ §3）。

R-12：`custom_rank` 本卡只做写入与持久化；读取投影、参与排序、UI 拖拽留 LIB-2；AC3 不声称自定义排序语义。

## r2 处置记录（2026-11-10，对 `e779674d5` 的 changes_requested）

r2 结论 `changes_requested`（P0=0 / P1=1 / P2=2 / P3=4；报告 `doc/reviews/FEA-14-LIB-1-r2.md`）；R-01/R-03/R-05–R-13 均确认关闭，以下为残余与新增。

- **R2-001（P1，已修；R-02 残余）**：`TagNotFound`（`LibraryError`，非 `ValueError`）原先逃逸为 `UNKNOWN/internal`；P5 handler 增捕 → `TARGET_NOT_FOUND/not_found`。tag id 全量校验前移到**任何写入之前**（消除 `{"title":…,"tags":[missing]}` 的半写），P5 文本字段只接受 `str`；补 wire 未知 tag typed + title 不变负例、storage `pytest.raises(TagNotFound)` + 半写断言。
- **R2-002（P2，已修；R-04 残余）**：`create_chapter` 原用 `max(import_order)+1` 同时作为 `sort_order`，重复/较小 `import_order` 会撞序；改为 `import_order` 取 `max(import_order)+1`、`sort_order` 取 `max(sort_order)+1` 两个独立值。补「两次普通创建 + 三次 `import_order=1` + 一次普通创建 → sort_order 1..6 唯一、import_order=3」测试。
- **R2-003（P3，已修；P3-1）**：Host P5 端口 patch 类型统一为 `IReadOnlyDictionary<string, object?>`（可表达 tags 字符串数组；`CoreServiceClient` 序列化 string/字符串数组并拒绝其他类型）；Host/`CoreServiceClient` 不再拒绝空 `ordered_ids`（空书 no-op 可达）；Fake 增 `LastReorderIds`；C# 测试覆盖 tags patch 与空列表 no-op。
- **R2-004（P3，已修；P3-2）**：Fake `CreateChapterWithMetadataAsync` 改按 Core 语义返回**追加** `sort_order`（`ChaptersByBook` 的 max+1，忽略 `importOrder`），测试断言 2（seed c1 sort=1）而非 7；真实 `CoreServiceClient` IPC 映射仍 NOT_RUN（不伪造覆盖）。
- **R2-005（P3，已修；P3-3）**：卡面 Scope §2 更正为「`books` 四列自 v2 已存在；v12 仅加 `chapters.custom_rank`」。
- **R2-006（P3，已修；P3-4）**：`schema.py` 的 V12 常量块移到 V11 之后，文件顺序恢复 V10→V11→V12（`default_migrations()` 顺序不变）。
- **R2-007（P3，已修；README 表述）**：README AC1 的「非法值 → INVALID_REQUEST」拆分：未知字段/非字符串 → `INVALID_REQUEST`；未知 tag id → `TARGET_NOT_FOUND`。

## r3 复核与收口（2026-11-10）

- r3：**approved**（P0=0 / P1=0 / P2=0 / **P3=1 accepted**；报告 `doc/reviews/FEA-14-LIB-1-r3.md`，被审 head `de595f69d`，产品提交 `e49855485`）。R2-001–R2-007 全部关闭，r1 R-01/R-03/R-05–R-13 无回退；C-07 正式表逐行 `ALL_MATCH: True`、pin `7c033bf7…` 不变、32/32 文件 ⊆ allowed_paths、5/5 证据 SHA 匹配；门禁复跑 13/1251/878/18/69-76 全 EXIT 0。
- **R3-001（P3，accepted 登记，不阻断）**：P7/P8 缺 SQLite 64 位边界校验——wire 传 `import_order=2^63` 会先创建后更新失败留下残行、`2^63−1` 会使后续 `max+1` 溢出；`custom_rank=2^63` → `UNKNOWN/internal`（未落库）。Host C# `int` 上限 2^31−1，生产 Host 不可达。**处置**：登记为 LIB-2 输入（`import_order`/`custom_rank` 加 64 位上界、P8 创建+更新入同一事务、`OverflowError` → `INVALID_REQUEST`）；本卡不修，NOT_RUN 如实保留。

## 证据计划（L2）

`verification/FEA-14-LIB-1/`：`logs/`（pytest 定向/全量、App.Tests、门禁、API inventory、pins、v12 回归）、迁移前后字段表、NOT_RUN、复现命令。

## 风险与回退

| 风险 | 处置 |
|---|---|
| 元数据覆盖用户手改 | patch 只改提供字段；测试断言未提供字段保留 |
| 重排丢章 | 全量覆盖校验（缺/多/重复 → typed，不改库） |
| 迁移风险 | v12 additive + pre_migration 备份 + 失败即停 |
| 旧行无损 | 迁移前后字段级对比测试 |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| temp | `G:\CODEX\New Manga.workspace\FEA-14-LIB-1\`（隔离数据根） | NOT_APPLICABLE | — | — | 仓外，不提交 |
| user-data | C:/Users/49745/AppData/Roaming/com.newmanga.desktop | PRESERVE_USER_DATA | — | — | 只读；测试用隔离根 |
| build | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 复用现有环境 |
| worktree | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 主树实现 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-LB-001 | LIB-1 | `verification/FEA-14-LIB-1/logs/dotnet-app-tests.log` | `e49855485` | `093e6c5c53b4f1dd757ad3cc944eefdbe6fad3b964e92a532a8f5f9199f3daa2` | CANONICAL |
| EV-LB-002 | LIB-1 | `verification/FEA-14-LIB-1/logs/pins-api.log` | `e49855485` | `891f5fb0de74a32d594b9089d22dd0e4bdaa9ebecc653816395b5ae7a733fb20` | CANONICAL |
| EV-LB-003 | LIB-1 | `verification/FEA-14-LIB-1/logs/pytest-lib.log` | `e49855485` | `1355515127b5e6836265c3a89164274d5cabfdb85fa0493ee568f04c648aa47e` | CANONICAL |
| EV-LB-004 | LIB-1 | `verification/FEA-14-LIB-1/logs/regression-v12.log` | `e49855485` | `5df2c633d5227642c50698108b8eb38b0a25e3f1dc64941f74eb0b37b127ca7d` | CANONICAL |
| EV-LB-005 | LIB-1 | `verification/FEA-14-LIB-1/README.md` | `e49855485` | `85026cdad1fe2e0f7495c04934d85a57358abc6e33c37310d3d2de52d380740f` | CANONICAL |

## Closeout Record

- 2026-11-10：scope 冻结（`ready`）→ 实现 `83e45cfe5` → **r1 `changes_requested`**（P0=0 / P1=2 / P2=4 / P3=7，`doc/reviews/FEA-14-LIB-1-r1.md`）→ r1 处置（`00a99622a` + 证据 `e779674d5`）→ **r2 `changes_requested`**（P0=0 / P1=1 / P2=2 / P3=4，`doc/reviews/FEA-14-LIB-1-r2.md`；R-01/R-03/R-05–R-13 确认关闭）→ r2 处置（`e49855485` + 证据 `de595f69d`）→ **r3 `approved`**（P0/P1/P2=0；P3=1 accepted，`doc/reviews/FEA-14-LIB-1-r3.md`）。
- 结论：**完成（带 limitation）**（2026-11-10）。交付 head `de595f69d`（r3 被审字节）；收口提交只含卡面/STATUS/PLAN/ledger/C-07 记录/本报告，无产品字节。
- 交付：schema **v12**（仅 additive `chapters.custom_rank`）+ `LibraryService.patch_book_metadata`（含 tags 全量替换/先校验后写）、`patch_chapter_metadata`（kind/方向不变量/custom_rank 严格类型）、`reorder_chapters_strict`、`create_chapter_with_metadata`（`import_order`/`sort_order` 分离取序）+ wire P5–P8 + Host 六处端口（P5 patch 支持 tags 与空 `ordered_ids`）+ C-07 UNFREEZE v1.6（69/76，pin `7c033bf7…`）；定向 13、回归 1251、App 878/0/11、pins 18/18。
- **Limitation**：① Host `ChapterSummary` 不投影 `kind`（LIB-2 扩 DTO）；② `custom_rank` write-only、P6 自定义/数字排序未实现（LIB-2 输入）；③ R-11 三项 deferral（kind 语义体积、`number_value`、`books.normalized_title` 唯一索引）；④ R3-001 64 位边界校验缺失（LIB-2 输入）；⑤ 真实 Host↔Core 进程级联调、LIB UI/tags UI、Volume 实体、万级章性能 = NOT_RUN。
- 零未授权契约字节（C-07 仅 UNFREEZE v1.2–v1.6 记录在案）；未 push。
