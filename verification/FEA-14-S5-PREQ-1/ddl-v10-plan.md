# FEA-14 S5 DDL v10 计划（PREQ AC5）

- Task：`FEA-14-S5-PREQ-1`；日期：2026-11-10；作者：DSH
- 性质：**计划**（不改 `schema.py`/不写实现）；供各切片实现卡消费。

## 1. 现状与先例

- `src/infrastructure/sqlite/schema.py` 当前 **v9**（v9 = 单条 `CREATE INDEX idx_media_artifacts_book`，`FEA-12-CORE-C04B-INDEX-L4-1`，**0 pin** 先例）。
- C-15 冻结契约文本描述 v7/v8 的 DDL 块；后续 additve 迁移已在卡面登记，未改契约字节。
- 裁决：**v10 为 additive 迁移**（新表/新列/索引），**不属于 C-15 v7 冻结 DDL 块**，沿用 0 pin 先例；仅在 PREQ/实现卡登记。

## 2. v10 迁移清单（按切片）

### 2.1 FONT（`FEA-14-FONT-1`）

| 对象 | 类型 | 列/说明 |
|---|---|---|
| `font_assets`（新表） | 表 | `id`、`family`、`subfamily`（variant）、`format`（ttf/otf/ttc）、`sha256`（唯一）、`size_bytes`、`license_note`（用户声明）、`source_name`（原文件名）、`imported_at`、`last_seen_at`、`deleted_at`（软删） |
| 索引 | 索引 | `(family, subfamily)`、`sha256` |
| 文件位置 | — | 数据根 `fonts/`（复制 + SHA-256；原文件不动；≤50MB/≤200 个） |

### 2.2 READ（`FEA-14-READ-1`）

| 对象 | 类型 | 列/说明 |
|---|---|---|
| `reading_preferences`（新表） | 表 | `book_id`（PK/FK）、`mode`、`direction`、`zoom`、`double_page`、`layout`、`updated_at` |
| `reading_bookmarks`（新表） | 表 | `id`、`book_id`、`chapter_id`、`page_id`、`side`（left/right/both，可空）、`note`（可空）、`created_at` |
| `reading_progress`（additive 列） | 列 | `anchor_json`、`viewport_json`（可空；旧行 NULL） |

### 2.3 EDIT（`FEA-14-EDIT-1`）

| 对象 | 类型 | 列/说明 |
|---|---|---|
| `issue_markers`（新表） | 表 | `id`、`book_id`、`chapter_id`、`page_id`、`position_x/position_y`（整页标记可空）、`kind`、`note`（可空）、`state`（open/resolved）、`created_at`、`resolved_at` |
| 索引 | 索引 | `(book_id, state)`、`(page_id)` |

### 2.4 AI（`FEA-14-AI-1`）

| 对象 | 类型 | 列/说明 |
|---|---|---|
| `prompt_templates`（新表） | 表 | `id`、`name`（唯一）、`body`、`version`（不可变）、`created_at`、`updated_at`、`deleted_at`；**只存用户自建模板** |
| 内置模板 | 不落库 | Core 代码常量（只读、可复制为自建副本）；`ListPromptTemplates` 返回常量与库内行的合并投影 |
| 引用 | 表/列 | 删除前引用检查（译文/任务/规则引用），须选替代 |

> R-004 裁决后取消「settings 或 DB 二选一」：模板统一落库，内置模板不入库（见 `ADJ-2026-11-10-FEA14-NEW-DATA-CATEGORIES` §2）。

### 2.5 LIB（`FEA-14-LIB-1`，需先 LIB-PREREQ 裁决）

| 对象 | 类型 | 列/说明 |
|---|---|---|
| `chapters`（additive 列） | 列 | `kind`（volume/episode/extra，可空 = 旧数据）、`custom_rank`（可空）、`number_value`（可空，数字排序用） |
| `books`（additive 列 + 索引） | 列/索引 | `normalized_title`（trim + casefold；唯一索引，事务提交时重验） |
| 封面引用（可选） | 列 | `cover_artifact_id`/`cover_source`（当前封面为首页推导；是否新增由 LIB-PREREQ 定） |

## 3. 迁移与回退纪律（所有 v10 表共用）

1. **迁移前**：`pre_migration` 备份（既有 `test_schema_migration.py:105` 语义），checksum 篡改检测保留。
2. **失败**：typed 失败 + DB 停留旧版，不半迁移（`migrator.py` 语义）；不得静默降级。
3. **旧 binary 拒写**：新 schema 被旧 binary 拒写（`test_schema_migration.py:75` 语义）沿用。
4. **备份归属**：新增表默认进入备份类别（C-01b SC-10b）与完整归属表（C-09 SC-B01a，sha256+size）；恢复冲突 defer、不整库覆盖。
5. **清理**：`fonts/`、`bookmarks`、`issue_markers`、`prompt_templates` **不得**被 `cleanup.py` 的缓存清理误删（`CACHE_SAFE_PREFIXES` 仅 `cache/` 的既有事实需以测试固化）。
6. **旧数据守恒**：升级前后业务行数/关键表 count 对比；`test_upgrade_schema_data.py:742` 同法参数化。

## 4. 0 pin 声明

- v10 迁移**不修改** C-15 冻结 DDL 块字节；`verify_pins` 的 18 pins 不因 v10 变化（除 PREQ AC2 的 C-07 一次 UNFREEZE 外）。
- 若实现中发现必须改动冻结 DDL 文本/语义 → 停止并回到本 PREQ 裁决（不得在实现卡内顺手改）。

## 5. 证据与关联

- 本计划：`verification/FEA-14-S5-PREQ-1/ddl-v10-plan.md`（本文件）。
- 裁决：`doc/reviews/ADJ-2026-11-10-FEA14-S5-SCOPE.md` §2.6。
- 先例：`doc/tasks/FEA-12-CORE-C04B-INDEX-L4-1.md:7`；`src/infrastructure/sqlite/schema.py:43`。
