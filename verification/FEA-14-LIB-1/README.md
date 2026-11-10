# FEA-14-LIB-1 证据索引（书/章元数据编辑与顺序）

- Task：`FEA-14-LIB-1`（FEA-14 S5 LIB 切片；复用 PREQ 预冻结 wire P5–P8）
- 实现提交：`e49855485`（r2 处置；base `f97f54476`；更早提交：`83e45cfe5`（初版）→ `00a99622a`（r1 处置）→ `e779674d5`（r1 证据）→ `e49855485`（r2 处置））
- 日期：2026-11-10
- 日志生成口径：4 个 Canonical 日志均于本轮门禁在 **r2 处置提交**生成，头行记录生成时 HEAD 与 `git status --short`（同批顺序生成，故后生成的日志会看到前序日志未提交；产品字节均为该提交）。README 与证据表在日志之后写入，属证据簿记，不含产品字节。

## 结论状态

| AC | 判别 | 结果 |
|---|---|---|
| AC1 书元数据 | patch 部分字段（其余保留）；title 非空；tags 替换语义；无书 typed | **MET**：`LibraryService.patch_book_metadata`（白名单 title/author/series_title/description/notes/original_title/publisher/**tags**；`apply_edit` 保留未提供字段；空 title → ValueError；未知字段/非字符串值 → ValueError；tags 为 tag id 列表，**先全量校验（存在性）再写**，`_replace_book_tags` 全量替换）；wire P5：无书 → `TARGET_NOT_FOUND`，未知 tag id → `TARGET_NOT_FOUND`（且文本字段不被半写），非法类型 → `INVALID_REQUEST`，tags t1→t2 替换与半写负例均实测 |
| AC2 章元数据 | kind/custom_rank/number/title/subtitle/notes；非法 kind 拒绝；无章 typed | **MET**：`patch_chapter_metadata`（kind→chapter_type 并维护方向不变量：webtoon→vertical、离开 webtoon→rtl；custom_rank 仅接受非负整数或 null（bool/float/str/负值 → ValueError）；number/title/subtitle/notes 仅接受 str；标题非空；未知字段拒绝）；wire P7 无章 → `TARGET_NOT_FOUND`、非字符串字段 → `INVALID_REQUEST` |
| AC3 章重排 | `ordered_ids` 必须全覆盖（缺/多/重复 → typed）；空书 `[]` no-op；sort_order 连续；读取顺序一致 | **MET**：`reorder_chapters_strict`（重复 → ValueError；集合不等 → ValueError；空书 `[]` → 成功 no-op，Core/Host 端口均可达）；wire P6 未知/缺失/重复 id → `INVALID_REQUEST`（该路径**不会**返回 `ChapterNotFound`），无书 → `TARGET_NOT_FOUND`；成功后 `list_chapters` 顺序与请求一致 |
| AC4 创建带元数据章 | title/kind/number/import_order 落库；返回 chapter_id/title/kind/number；父书不存在 typed | **MET（带 limitation）**：`create_chapter_with_metadata`（继承书默认 kind；`import_order` 仅记录来源顺序，**不覆盖** `sort_order`；`sort_order` 与 `import_order` 各自 max+1，重复/较小 `import_order` 不撞序）；wire P8 返回 chapter_id/title/kind/number/**sort_order**；无书 → `TARGET_NOT_FOUND`；bool/float/str `import_order` → `INVALID_REQUEST`。**limitation**：Host `ChapterSummary` 仅四字段，`kind` 不投影（LIB-2 扩展 DTO） |
| AC5 迁移/契约/门禁 | v12 additive（旧行无损）；P5–P8 按 PREQ §8；inventory EXIT 0；pins 18/18 | **MET**：v12 仅 `ALTER TABLE chapters ADD COLUMN custom_rank INTEGER;`（v1–v11 迁移 NAME/SQL 逐字节未变；旧 v11 书/章行升级后字段保留、`custom_rank IS NULL`）；wire 四命令；inventory **69/76** 且正式成员表与脚本 stdout 逐行一致；C-07 UNFREEZE **v1.6**（pin `7c033bf7…`，v1.3–v1.5 原值保留）；`verify_pins` 18/18 |
| AC6 证据 | 定向/全量测试、日志 EXIT、NOT_RUN | **MET**：见下表与 NOT_RUN |

## 门禁与证据（本目录）

| 文件 | 内容 | EXIT |
|---|---|---|
| `logs/pytest-lib.log` | `test_library_metadata.py` + `test_library_wire.py` **13 passed** | 0 |
| `logs/regression-v12.log` | v12 回归：storage+core+fea09+fea11 **1251 passed** | 0 |
| `logs/dotnet-app-tests.log` | App.Tests 全量 **878 passed / 0 failed / 11 skipped** | 0 |
| `logs/pins-api.log` | `verify_pins` 18/18（C07=`7c033bf76af1`）、`generate_api_inventory.py --check` EXIT 0（69/76） | 0 |

**r1/r2 处置后同步更新**：`doc/plan/FEA-C07_API_INVENTORY.md`（正式成员表 = 脚本 stdout，69 方法 + 4 非方法成员；S5 计划节仅剩 P16–P25）、`doc/plan/FEA-CONTRACT-FROZEN-C07.md`（§1 pin 链 v1.3–v1.6、§1B r2 结果、§2 条件 3 `1/69/6=76`、§3、§5）、`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-LIB1.md`（v1.6 附录）、卡面「r1 处置记录」「r2 处置记录」「范围裁决」。

## 设计说明与 limitation

- **tags 替换语义**：P5 `patch{tags:[tag_id…]}` 为**全量替换**（删除既有 book_tags 关联后重建）；未知 tag id 在任何文本字段写入之前就抛 `TagNotFound`（wire `TARGET_NOT_FOUND`），不会半写；tag 名称/UI 管理仍留 LIB-2。Host P5 端口用 `IReadOnlyDictionary<string, object?>`，可表达 tags 字符串数组。
- **`import_order` vs `sort_order`**：`import_order` 是来源顺序（可重复，P8 允许），`sort_order` 是显示/读取顺序（创建时取 `max(sort_order)+1`、重排时连续重写，保证唯一）。
- **`custom_rank`**：v12 additive 列；本卡只写入/读回，不参与排序、不投影到 Host——P6「自定义排序保位/数字排序重排」登记为 LIB-2 输入（R-12）。
- **R-11 三项 deferral**（不改变 PREQ 预冻结 wire 形状）：① `kind` 按既有 `ChapterType`（paged/webtoon），DDL 计划的 volume/episode/extra 随 Volume 实体另行裁决；② `number` 落 `chapters.chapter_number` 自由文本，`number_value` 数字排序列推迟；③ `books.normalized_title` 唯一索引与重名规范化待用户裁决（ADJ §3）。
- 章 kind 变更会同步 reading_direction（webtoon↔vertical 不变量），避免实体校验失败。
- 不做 Volume 实体（PREQ 未纳入，另行裁决）；不做批量重排 UI。

## NOT_RUN（不得记 PASS）

- LIB 可见 UI（书架/工作台账单的元数据编辑与拖拽重排）= NOT_RUN（FEA-14-LIB-2/UI 卡）。
- tags 的 UI 管理与筛选 = NOT_RUN（数据面已实现并测试）。
- **真实 Host↔Core 进程级联调**：4 个新 `CoreServiceClient` 方法未对活 Core 调用；C# 4 个端口测试覆盖 NullHost 降级、Fake 记录（含 tags patch/空列表）、Fake 的追加 `sort_order` 语义，但 **不覆盖 `CoreServiceClient` 的真实 IPC 读写映射**（Fake 是测试替身，不能替代活进程联调）。
- Volume 实体 = NOT_RUN（未纳入本卡范围）。
- 真实大库（万级章）重排性能未压测；sqlite 磁盘写失败/半迁移未演练。
- FEA-15 正式验收声明未审。

## 复现

```powershell
python -m pytest tests/storage/test_library_metadata.py tests/core/test_library_wire.py -q
python -m pytest tests/storage tests/core tests/fea09/test_v7_migration.py tests/fea11/test_source_gate_unify.py -q
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo
python tools/generate_api_inventory.py --check
pwsh -NoProfile -File tools/governance/verify_pins.ps1
```
