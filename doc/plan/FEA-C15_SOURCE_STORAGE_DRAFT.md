# FEA-C15 Source 存储契约（草案 v3，处置契约复核 r2）

状态：**草案 v2 / 待独立复核后由 DSH 冻结**（FEA-09-PREREQ-1 交付物；冻结后字节不得改，修订须 UNFREEZE）
日期：2026-11-03
作者：DSH（Lead / Architect / Integrator）
依据：[AD-003](../AD-003_REFERENCED_SOURCE_ARCHITECTURE.md) §3.2/§3.4/§3.5/§3.6/§4；[G-CONTRACT 关闭裁定](../plan/GATE-CONTRACT-CLOSURE-2026-11-01.md) §3.3；C-01b/C-05/C-06/C-14 冻结契约；`src/infrastructure/sqlite/{schema,migrator,library}.py`、`domain/pages/entities.py`、`src/infrastructure/importing.py`、`apps/.../NewManga.Host/**` 代码事实；[FEA-09 scope-r1](../reviews/FEA-09-scope-r1.md)、[契约复核 r1](../reviews/FEA-09-PREREQ-1-r1.md)（R1-001…R1-013）。

**边界**：本契约只补 Source 生产实现的存储缺口（DDL、迁移安全、身份/排序规则、完整性与可见性拆分、Host Registry 规范、跨存储次序、rendition cache 边界）。**不复写** C-01b/C-05/C-06/C-14 已冻结语义；对 C-05/C-06 的必要语义扩展通过 **v1.1 UNFREEZE** 载体（`doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md`）显式登记并重新复核，**不得**以新文档声明代替。

---

## 0. 范围、不变量与 UNFREEZE 依赖

| # | 不变量 | 来源 |
|---|---|---|
| I-1 | 新导入只建立引用/索引/必要元数据，不创建永久全尺寸输入副本；rendition 缓存可再生产、有上限、可全量丢弃重建 | C-01b SC-01/02；C-14 SC-S14…S17 |
| I-2 | 旧 Managed Copy 继续可读、不自动迁移/删除；旧页 ID/顺序/人工数据/Lock 迁移后守恒 | C-01b SC-07；提案 `:1026–:1028` |
| I-3 | 源身份 = 内容 digest + 授权 + lineage + Windows volume serial + file ID；不得仅凭路径/mtime/size 断言同一文件；**同内容不同物理文件不得合并** | C-01b SC-04；AD-003 §3.2 |
| I-4 | 完整性、数据库可见性、当前可读性（授权/资源）是**三个不同谓词**，不得合成一个 | C-05 v1.1；本契约 §4 |
| I-5 | 旧二进制打开新 Schema 必须拒写；迁移失败不得留下半迁移的 v7 结构 | C-01b SC-19；`migrator.py` |
| I-6 | Core DB 不保存源文件绝对路径；locator 仅容器内相对定位；路径与授权只在 Host 私有 Registry | AD-003 §3.5；C-06 |
| I-7 | Host Registry 与 Core DB 无跨存储事务；发布次序必须杜绝「Core complete 而 Host 未持久化」的假成功 | C-06；本契约 §6 |
| I-8 | cached rendition 不是业务数据；不得含唯一人工成果/结果/恢复文件；不得写用户源目录；**不得把 raw user-source 字节当 rendition 发布** | C-01b SC-02/03；C-14 SC-S15/S17 |

**UNFREEZE 依赖（本契约冻结的前置）**：

- **C-05 v1.1**：新增 referenced 页可见性分支，并把 `is_complete_page` / `V(p,t)` / `R(p,t)` 拆开（R1-001）。
- **C-06 v1.1**：grant 四维 scope、Host 铸造型发放、Host/Core 双侧 Verify 归属、`RevokeSourceReadGrant` 与即时撤销/失联语义（R1-002/R1-003）。
- 两份 UNFREEZE 载体与 C-15/C-16 同批独立复核；approved 后按冻结记录纪律重算 pin 并重新冻结（C-05/C-06 的新 pin 写入各自 FROZEN 记录；`verify_pins.ps1` 自动读取新 pin）。

## 1. 迁移与版本

- 新增 **`v7__source_storage`**（`SCHEMA_VERSION_V7=7`、`MIGRATION_V7_NAME/SQL` 追加到 `default_migrations()`）。v1–v6 字节不变；**每个迁移版本各自一个事务**（现有 `MigrationRunner` 语义，`migrator.py:82–100/141–174`），**不声称** v1→v7 整链一个事务。
- **失败停留状态**：从 v6 升级时 v7 失败 → DB 保持 v6（v7 语句与元数据全部回滚）；从更早版本升级时，先前各版本的 additive 迁移可能已提交，这是既有行为，不是 v7 引入的新风险；启动必须 typed 失败（`SOURCE_MIGRATION_FAILED`），**不得**以部分升级库继续服务。
- **pre-commit 验证回调（冻结 API 语义）**：`MigrationRunner` 增加可选 `validate: Callable[[sqlite3.Connection], None]`，在 `_apply_one` 的 `BEGIN IMMEDIATE` 事务内、全部 v7 语句执行后、写 `schema_migrations`/`application_metadata` **之前**调用：
  - 回调只能使用该同一 `sqlite3.Connection` 做**只读 DB 查询**；外部资源验证只允许经注入的 **`IResourceVerifier` 接缝**（对本机受管根做只读存在/可读检查；禁止任何写、网络、Host 调用或第二 SQLite 连接）；**禁止** commit/rollback/close、禁止 DDL/DML；违规由 runner 包装为 `MigrationValidationError`；
  - 回调抛 `MigrationValidationError(code, detail)` 或非 `sqlite3.Error` 异常 → runner rollback 并抛出 typed `MigrationError`（启动失败，不切换入口）；
  - **基线捕获**：迁移前在独立只读连接上捕获（页 ID/顺序、source_hash、managed_original_ref、width/height、Lock、人工数据行计数、reader projection 可见页 ID 顺序），作为内存对象传给回调；不得在回调内重新查询 Host。
- **v7 验证断言（最小集）**：
  1. 旧谓词可见页集合 = 迁移后 `source_mode='managed' AND integrity_status='complete'` 集合（逐 page_id/顺序）；
  2. 旧不可见/半写行仍为 `incomplete` 且进入待恢复清单（不删除、不误标 complete）；
  3. `sort_order`/`source_order`/`managed_original_ref`/`source_hash`/Lock/人工数据行数与基线逐项相等；
  4. **旧 Managed 资源可读性**：对基线中每个旧可见页，经既有可信受管根（`ManagedRootTrust` 或等价只读验证）验证 `managed_original_ref` 存在且可读；缺失/不可读 → `SOURCE_MIGRATION_RESOURCE_UNVERIFIED`（附 page_id 列表），**回滚并拒绝切换入口**（提案 `:1026–:1028` 的“缺文件暂停切换”）。
  - 产品门禁（build/全量测试/旧 FEA-06 四 PNG/check/vpins）属集成验证，不是 SQLite 回调内部动作。
- **旧二进制拒写**：v7 库交给仅认识 v1–v6 的旧迁移器 → `SchemaTooNewError`（现有 `migrator.py:76–80`）；不得“忽略新列”。
- **降级**：无自动降级；恢复迁移前 verified 备份到隔离新根（SC-37）。
- **预留**：`source_sync_plans`、`source_operations` 不在 v7 创建；FEA-11/FEA-12 前置契约以 v8+ 追加。FEA-09 的取消/幂等 receipt 为**会话内**状态机（C-16 §4），不写这两张表。

## 2. 迁移 v7 的规范 DDL

以下 SQL 为冻结对象；实现必须逐字落在 `MIGRATION_V7_SQL`（注释可保留）。TEXT 时间统一 UTC ISO-8601；布尔 INTEGER 0/1。

```sql
-- 2.1 pages：source mode + 完整性（新列默认 incomplete；迁移回填旧 complete 集）
ALTER TABLE pages ADD COLUMN source_mode TEXT NOT NULL DEFAULT 'managed'
    CHECK (source_mode IN ('managed', 'referenced'));
ALTER TABLE pages ADD COLUMN integrity_status TEXT NOT NULL DEFAULT 'incomplete'
    CHECK (integrity_status IN ('incomplete', 'complete'));
UPDATE pages SET integrity_status = 'complete'
 WHERE source_hash IS NOT NULL AND managed_original_ref IS NOT NULL
   AND width IS NOT NULL AND width > 0 AND height IS NOT NULL AND height > 0;

-- 2.2 源
CREATE TABLE sources (
    source_id TEXT PRIMARY KEY CHECK (length(source_id) > 0),
    source_kind TEXT NOT NULL CHECK (source_kind IN ('image', 'folder', 'zip', 'cbz', 'pdf')),
    display_name TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT
);

-- 2.3 源位置/授权绑定：不保存绝对路径；同物理身份唯一（I-3）
CREATE TABLE source_locations (
    location_id TEXT PRIMARY KEY CHECK (length(location_id) > 0),
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    registry_id TEXT NOT NULL CHECK (length(registry_id) > 0),
    authorization_generation INTEGER NOT NULL CHECK (authorization_generation >= 1),
    content_digest TEXT NOT NULL CHECK (length(content_digest) = 64),
    volume_serial INTEGER NOT NULL CHECK (volume_serial >= 0),
    file_id INTEGER NOT NULL CHECK (file_id >= 0),
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    mtime_hint TEXT,
    observed_at TEXT NOT NULL,
    last_verified_at TEXT,
    is_current INTEGER NOT NULL DEFAULT 1 CHECK (is_current IN (0, 1)),
    created_at TEXT NOT NULL,
    UNIQUE (source_id, location_id),
    UNIQUE (source_id, content_digest, volume_serial, file_id)
);
CREATE INDEX idx_source_locations_source ON source_locations(source_id, is_current);
CREATE UNIQUE INDEX uq_source_locations_current
    ON source_locations(source_id) WHERE is_current = 1;

-- 2.4 内容版本（content identity；rendition 观察在 entries 行）
CREATE TABLE source_versions (
    version_id TEXT PRIMARY KEY CHECK (length(version_id) > 0),
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    location_id TEXT NOT NULL,
    content_digest TEXT NOT NULL CHECK (length(content_digest) = 64),
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    observed_at TEXT NOT NULL,
    superseded_at TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (source_id, version_id),
    UNIQUE (source_id, content_digest),
    FOREIGN KEY (source_id, location_id) REFERENCES source_locations(source_id, location_id)
);
CREATE INDEX idx_source_versions_source ON source_versions(source_id, observed_at);

-- 2.5 容器成员/文件条目：行键 (source, version, entry)；稳定排序键版本内唯一
CREATE TABLE source_entries (
    source_id TEXT NOT NULL,
    version_id TEXT NOT NULL,
    entry_id TEXT NOT NULL CHECK (length(entry_id) > 0),
    locator TEXT NOT NULL CHECK (length(locator) > 0),
    ordinal INTEGER NOT NULL CHECK (ordinal >= 0),
    stable_sort_key TEXT NOT NULL CHECK (length(stable_sort_key) > 0),
    content_digest_kind TEXT NOT NULL CHECK (content_digest_kind IN ('encoded', 'page-identity')),
    content_digest TEXT NOT NULL CHECK (length(content_digest) = 64),
    encoded_digest TEXT CHECK (encoded_digest IS NULL OR length(encoded_digest) = 64),
    pixel_digest TEXT CHECK (pixel_digest IS NULL OR length(pixel_digest) = 64),
    pixel_digest_algorithm TEXT CHECK (pixel_digest_algorithm IS NULL
        OR pixel_digest_algorithm = 'pixel-digest/1'),
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    mime_type TEXT,
    width INTEGER CHECK (width IS NULL OR width > 0),
    height INTEGER CHECK (height IS NULL OR height > 0),
    orientation INTEGER CHECK (orientation IS NULL OR orientation IN (1, 3, 6, 8)),
    decoder_name TEXT NOT NULL DEFAULT '',
    decoder_version TEXT NOT NULL DEFAULT '',
    decoder_params_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    PRIMARY KEY (source_id, version_id, entry_id),
    UNIQUE (version_id, ordinal),
    UNIQUE (version_id, stable_sort_key),
    FOREIGN KEY (source_id, version_id) REFERENCES source_versions(source_id, version_id)
);
CREATE INDEX idx_source_entries_identity ON source_entries(source_id, entry_id);
CREATE INDEX idx_source_entries_digest ON source_entries(version_id, content_digest);

-- 2.6 页绑定：项目（book）内 entry 当前唯一；每页 current binding 唯一
CREATE TABLE page_bindings (
    binding_id TEXT PRIMARY KEY CHECK (length(binding_id) > 0),
    page_id TEXT NOT NULL REFERENCES pages(page_id),
    project_id TEXT NOT NULL REFERENCES books(book_id),
    binding_version INTEGER NOT NULL CHECK (binding_version >= 1),
    source_id TEXT NOT NULL,
    entry_id TEXT NOT NULL,
    accepted_source_version TEXT NOT NULL,
    status TEXT NOT NULL
        CHECK (status IN ('healthy', 'needs_confirmation', 'missing', 'superseded')),
    previous_binding_id TEXT REFERENCES page_bindings(binding_id),
    authorization_generation INTEGER NOT NULL CHECK (authorization_generation >= 1),
    authorized_at TEXT NOT NULL,
    verified_digest TEXT NOT NULL CHECK (length(verified_digest) = 64),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (page_id, binding_version),
    FOREIGN KEY (source_id, accepted_source_version)
        REFERENCES source_versions(source_id, version_id),
    FOREIGN KEY (source_id, accepted_source_version, entry_id)
        REFERENCES source_entries(source_id, version_id, entry_id)
);
CREATE UNIQUE INDEX uq_page_bindings_current
    ON page_bindings(page_id) WHERE status <> 'superseded';
CREATE UNIQUE INDEX uq_page_bindings_project_entry
    ON page_bindings(project_id, entry_id) WHERE status <> 'superseded';
CREATE INDEX idx_page_bindings_source ON page_bindings(source_id, accepted_source_version);

-- 2.7 rendition 缓存元数据（可再生产物；只允许 decoded/re-encoded rendition，禁 raw user-source 字节）
CREATE TABLE rendition_cache (
    cache_key TEXT PRIMARY KEY CHECK (length(cache_key) > 0),
    source_id TEXT NOT NULL,
    version_id TEXT NOT NULL,
    entry_id TEXT NOT NULL,
    rendition_kind TEXT NOT NULL
        CHECK (rendition_kind IN ('thumbnail', 'tile', 'pdf_raster', 'archive_page', 'page_preview')),
    decoder_name TEXT NOT NULL,
    decoder_version TEXT NOT NULL,
    params_digest TEXT NOT NULL CHECK (length(params_digest) = 64),
    rel_path TEXT NOT NULL CHECK (length(rel_path) > 0),
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    content_digest TEXT NOT NULL CHECK (length(content_digest) = 64),
    created_at TEXT NOT NULL,
    last_used_at TEXT NOT NULL,
    active_references INTEGER NOT NULL DEFAULT 0 CHECK (active_references >= 0),
    FOREIGN KEY (source_id, version_id, entry_id)
        REFERENCES source_entries(source_id, version_id, entry_id)
);
CREATE INDEX idx_rendition_cache_lru ON rendition_cache(last_used_at);
CREATE INDEX idx_rendition_cache_source ON rendition_cache(source_id, version_id, entry_id);
```

**约束语义（冻结）**：

- `page_bindings.verified_digest` 必须等于对应 `source_entries.content_digest`；referenced 页面可读谓词包含该一致性（§4）。
- `project_id` = 所属 `books.book_id`（项目粒度裁决为 **book**）；同一 book 内一个 entry 只能有一个非 superseded binding（软删页面的 binding 仍占位，重导入按“已引用”处理，不新建重复页）。
- `source_entries.entry_id` 跨版本保续规则见 §3.3；`(version_id, ordinal)` 与 `(version_id, stable_sort_key)` 双唯一防止排序键冲突。
- `rendition_cache.rel_path` 必须是 derived 根内相对路径且以 `source-renditions/` 开头（应用层校验；DDL 不替代该边界），`rendition_kind` 不含 raw 原始字节发布。
- `source_locations` 的唯一键 `(registry_id, content_digest, volume_serial, file_id)` 保证**同内容不同物理文件不合并**；同物理源在不同授权代次下允许新 location 行。

## 3. 源身份、排序与 occurrence 规则（可执行判据）

### 3.1 source_kind 与 content digest

| kind | content digest（`sources/source_locations/source_versions`） | entry 产生 |
|---|---|---|
| `image` | 文件原始字节 sha256 | 单 entry，locator=文件名，`encoded` |
| `pdf` | 文件原始字节 sha256 | 每页 entry，locator=十进制页码；`content_digest_kind='page-identity'`，`content_digest = sha256("pdf-page/1\0" + container_digest + "\0" + page_ordinal)`；pixel digest 仅作 rendition 观察 |
| `zip`/`cbz` | 归档原始字节 sha256 | 每成员 entry，locator=成员名（允许重复名），`encoded` |
| `folder` | **folder-manifest/1**：`sha256(canonical-json({"format":"folder-manifest/1","entries":[{"rel_path","size_bytes","sha256"}...按 rel_path 排序]}))`；目录 identity=volume serial+file id | 每个直接子文件 entry，locator=相对路径（`/` 分隔），`encoded` |

- PDF 的 **page-identity** 是不可变的内容身份：`sha256("pdf-page/1\0" + 容器原始字节 sha256 + "\0" + 页码 ordinal)`，不依赖 decoder/scale/像素；decoder/scale/编码参数变化只更新 rendition 观察列（`decoder_*`、`pixel_digest`、width/height、orientation），**不得**改变 `content_digest`/`entry_id`/binding 的 `verified_digest`（SC-28）。`pixel-digest/1` = `sha256("WxH\0" + RGB 字节)` 仅作精确匹配/确认的 rendition 观察，写入 `pixel_digest` + `pixel_digest_algorithm='pixel-digest/1'`；不得作为 binding 的 content digest。
- `pages.source_hash`：managed = 原文件字节 sha256；referenced = 对应 entry 的 `content_digest`（image/archive=`encoded`，pdf=`page-identity`）；`pages.source_size_bytes` = entry `size_bytes`；width/height 取 entry 解码结果。
- `stable_sort_key`：由导入层按“自然排序键 + 稳定 tie-break”生成（PDF=页码数值；文件夹=相对路径自然排序；归档=成员 ordinal/名称自然排序），必须满足 DDL 的版本内唯一；同键冲突时导入层追加 ordinal tie-break，不得静默覆盖。
- `locator` 安全规则：禁止绝对路径/盘符/UNC/`..`/NUL/控制字符；文件夹相对路径使用 `/`；最大 4096 字符。`source_filename` 仅 basename（禁止 `/`、`\`，≤255）；`display_name` 去控制字符、≤512；`decoder_params_json` 为 canonical JSON、无绝对路径、≤4KB（应用层校验）。

### 3.2 重复 occurrence 与 entry 身份保续

- 重复归档名/重复同图：每个 occurrence 独立 entry（以 `ordinal` 区分），**不得**按 digest 合并或丢弃 occurrence（ADR/提案 `:457`/`:469`；C-14 SC-S10）。
- 跨版本 `entry_id` 保续：仅在同一 `source_id` 内、按**不可变内容身份**匹配（image/archive 用 encoded digest；PDF 用 page-identity）确定候选；同一身份在多个 occurrence（重复名/重复同图）时按 `stable_sort_key` 锚定唯一匹配才保续；`pixel_digest` 只可用于**候选比较/人工确认**（重编码容器），不得单独作为身份或自动合并依据。仍歧义 → 新 entry_id + 受影响 binding 置 `needs_confirmation`，**不得**仅凭 digest 自动合并/迁移人工内容。
- 同内容不同物理源（volume/file id 不同）→ 不同 `source_id`（I-3）；`import_as_new` 不能绕过项目内 entry 唯一性（C-16 §4）。
- **源复用规则（v3）**：Core 写入前按**物理身份** `(content_digest, volume_serial, file_id)` 查 `source_locations`；命中则复用同一 `source_id`/version/entries，并**原地更新**该 location 的 `registry_id/authorization_generation/last_verified_at`（不新建重复 location；DDL 的 `UNIQUE(source_id, content_digest, volume_serial, file_id)` + 部分唯一 `is_current=1` 保证每个 source 只有一个当前物理位置）。未命中才新建 source/location。重授权/重新注册不改变 `source_id`；旧 binding 的 `authorization_generation` 允许 ≤ 当前 Host generation，读取时以 Host grant 的 identity/generation 复核为准（不要求等值）。

## 4. 完整性 / 可见性 / 可读性拆分与五读路径

### 4.1 三个谓词（冻结）

1. **`is_complete_page(p)`**（数据完整性；不看 deleted/时间/资源）：
   ```text
   -- managed：旧完整性谓词 + v7 状态列
   p.source_mode = 'managed' AND p.integrity_status = 'complete'
     AND p.source_hash IS NOT NULL AND p.managed_original_ref IS NOT NULL
     AND p.width > 0 AND p.height > 0
   -- referenced：C-05 v1.1 P7 ∧ P8（healthy binding + verified_digest 一致）
   OR (p.source_mode = 'referenced' AND p.integrity_status = 'complete'
       AND p.source_hash IS NOT NULL AND p.width > 0 AND p.height > 0
       AND EXISTS (SELECT 1 FROM page_bindings b JOIN source_entries e
           ON (e.source_id,e.version_id,e.entry_id)=(b.source_id,b.accepted_source_version,b.entry_id)
           WHERE b.page_id=p.page_id AND b.status='healthy'
             AND b.verified_digest=e.content_digest))
   ```
2. **`V(p,t)`**（C-05 v1.1 §3.1 权威，模式分派）：
   ```text
   V(p,t) ≡ (p.source_mode='managed'    AND V_artifact(p,t))
          OR (p.source_mode='referenced' AND V_ref(p,t))
   V_artifact = C-05 原 P1–P5（artifact/revision；不要求 pages.integrity_status，字节不变）
   V_ref      = C-05 v1.1 P1 ∧ P7 ∧ P8 ∧ P5（父级未删/页未删/referenced 完整性/健康 binding/时间）
   ```
3. **`R(p,t)`**（当前可读/可解析）：`V(p,t)` ∧ 资源授权有效 —— managed：受管根校验可读；referenced：C-16 的有效 source-read grant + identity digest 匹配。**读取层不得把 `V` 当 `R`**；导出/阅读器读取失败要 typed，不静默显示空页。

### 4.2 五读路径（FEA-09 必改/必回归）

| 路径 | v7 规则 |
|---|---|
| `existing_source_hashes` | `is_complete_page` ∧ `deleted_at IS NULL`；managed/referenced 同一谓词；去重策略由导入层决定，**不按 digest 合并 occurrence** |
| `max_source_order` | `is_complete_page`（**包含软删页**，沿用现有语义）；不得复用含 `deleted_at` 的 live 谓词 |
| `get_page` / `list_pages` | `V(p,t)`（含父级删除与时间） |
| `handle_resolve_page_resource` | managed：既有受管根解析与 derived publish 不变；referenced：**只允许经 source-read grant 读取并按 rendition_cache 规则发布 decoded/re-encoded rendition**（`rendition_kind` 白名单；预算/淘汰/校验按 C-14 SC-S14…S17），禁止把 raw user-source 字节直接发布；无有效 grant → `SOURCE_ACCESS_DENIED` 等 typed，**禁止**回退任意路径 |
| reader projection | 基于 `list_pages`/C-05 v1.1；referenced 页可见且可解析；人工数据/进度/顺序不因 mode 改变 |

### 4.3 旧 Managed 写入对完整性列的维护（R1-006）

- 所有 managed 创建路径必须在同一事务内显式写 `source_mode='managed'`、`integrity_status='complete'`，且只在 Managed Copy 已存在后提交：
  `application/importing/images/service.py`（`add_page` 前受管副本已存在）、`documents/service.py`、`bootstrap/core_service.py` 的旧 `ImportPages` 适配、任何其它 `Page(...)`/`add_page` 调用点。
- 半写/失败路径保持默认 `incomplete`，不可见但可恢复；`update_page` 不得把 incomplete 静默翻成 complete（只允许带验证的显式状态迁移）。
- 升级后旧 `ImportPages` 必须回归通过（AC-7 增加该用例）；v1 placeholder 行永久保持 incomplete（除非显式修复流程，FEA-09 不实现修复流程）。
- 完整性/可见性/授权拆分见 §4.1；`max_source_order` 的含软删集合单独实现（R1-006）。

## 5. Host `SourceAccessRegistry` 实现规范（C-06 落地）

- **位置**：`<HostOptions.DataRoot>/host/source-access/registry.v1.dat`；测试注入隔离 DataRoot；生产 `%APPDATA%\com.newmanga.desktop`。
- **文件格式**：`ASCII "NMSAR1\0"` + `uint32 LE JSON 长度` + **DPAPI CurrentUser** 密文；明文 JSON：
  ```json
  {"format_version":1,"written_at":"<iso>","entries":[
    {"registry_id","locator","generation","created_at","last_used_at","revoked_at",
     "roots":[{"root":"<normalized absolute>","volume_serial":1,"file_id":2,
               "identity_verified_at":"<iso>","readable":true}],
     "identity_facts":{"content_digest","volume_serial","file_id","size_bytes"}}]}
  ```
  每个 authorized root 有**独立身份记录**（R1-011）；`identity_facts` 描述当前已授权物理源（可为空直到首次使用）。禁止持久化 grant/session key/lease/密码/源内容。
- **加锁与重载（冻结顺序）**：
  1. 对 `<DataRoot>` 计算规范化路径（`Path.GetFullPath` + 大小写不敏感）→ `sha256(UTF8)` 前 16 hex 派生锁名 `Local\NewManga.Host.SourceAccessRegistry.<hex>`；先 `Global\` 同名候选，再 `Local\`（沿用 `SingleInstanceGuard` 候选模式）。
  2. 对 `registry.v1.lock` 取**独占文件句柄**（`FileShare.None`，跨 session 排他）；获取顺序：命名互斥 → 文件句柄 → 读文件；任一超时/冲突 ≤5s → `SOURCE_REGISTRY_BUSY`（retryable）。
  3. **持锁后重新读取磁盘并校验 generation**；内存快照不得覆盖更新的磁盘状态；写前比较 expected generation，失配 → `SOURCE_REGISTRY_BUSY` 并重载。
  4. 写：同目录临时文件 → `FileStream.Flush(true)` → `File.Replace`/`File.Move` 原子替换 → 释放文件句柄 → 释放互斥；写失败不更新内存快照。
- **状态机（R1-011）**：
  - **文件缺失** = 合法空 Registry（首次运行）：允许 `source_register_root` 创建；不视为损坏。
  - **magic/version/长度/DPAPI/JSON/roots identity 任一不合法** = 损坏：**fail-closed**，不创建空文件、不覆盖；所有 source 操作 `SOURCE_REGISTRY_UNAVAILABLE`；把原文件原字节保留为 `registry.v1.dat.corrupt-<utc>`（复制，不移动）供诊断。
  - **恢复**：显式命令 `source_reset_registry {confirm:true}` 把损坏文件移入 `host/source-access/quarantine/` 后创建新空 Registry（**用户显式操作**，UI-1 接线；FEA-09 实现 Host handler）；不得自动重建。
  - **撤销**：generation+1 并持久化 `revoked_at`；发布 `RevokeSourceReadGrant`（C-16）并等待 Core ACK 后才向调用方返回 `revoked:true`；ACK 失败 → 返回失败但持久化状态已撤销（读取面 fail-closed）。
- **ACL/加密边界**：`host/` 目录要求当前用户独占写（创建时校验；失败拒绝创建）；文件总是 DPAPI 包装；DPAPI 原生往返测试只能在 Windows 交互用户环境执行，测试以 `ISecretProtector` 接缝注入 fake；**未取得原生证据时标 LIMITED，不得写 PASS**。
- **备份交接（FEA-13）**：Registry 文件/DPAPI 边界/备份包加密需求作为设计输入；跨机恢复因 DPAPI CurrentUser 不自动继承授权（binding 需重新确认），不以“DPAPI 失败”作为唯一跨机判据。
- **日志**：仅 registry_id/generation/计数；不写绝对路径/密码/密文。

## 6. 跨存储发布/恢复次序与即时撤销

1. **Host 先持久化授权**：`source_register_root` 或操作前校验 Registry 并（必要时）原子持久化 generation；失败 → 不进入 Core 写阶段。
2. **Host 在 dispatch 前铸造 source-read grant**（签名、四维 scope、budget、expiry，C-16 §2）；Host 在铸造时完成 `VerifySourceRead` 的 **scope→授权根**解析。
3. **Core 侧 VerifySourceRead**：每次读取前/每次 commit 前校验签名/session/expiry/generation/identity（同一验证句柄的 digest/volume/file id），失败不读/不提交。既有 binding 的 `authorization_generation` 允许 ≤ 当前 Host generation；只要 Host 当前授权覆盖同一物理 identity 即可读，generation 递增本身不使 binding 失效。
4. **Core 读取/解码在 DB 事务之外**；**单事务提交**：source rows + pages（mode/integrity）+ binding（healthy, verified_digest 一致）；失败整体回滚，未提交页不可见。
5. **即时撤销（R1-003）**：用户撤销 → Host 持久化 generation+1 → 向 Core 推送 `RevokeSourceReadGrant`（含 registry_id/generation/grant ids）→ Core 立即废止本地 grant 并在**下一个提交边界**停止；Core ACK 后 Host 才返回撤销成功。提交边界前已提交的页合法保留；撤销成功后的新读/新 commit 一律拒绝（`SOURCE_GRANT_REVOKED`）。
6. **Host 失联**：Core 检测 stdin EOF/transport 失败 → 立即废止全部 source grant、停止后续读取与 commit（fail-closed）；不得以“grant 未过期”继续。
7. **禁止假成功**：Host 持久化前不得置 healthy；`verified_digest` 不一致不得置 complete；不得以“路径仍可打开”代替授权验证。
8. **崩溃恢复**：Host 崩溃 → 旧完整快照（generation 可能落后）→ 相关 binding 读取被拒（可用性下降，不数据损坏）；Core 崩溃 → 当前页事务回滚，已提交页保留；重试只补未提交单元（C-16 §4）；不重发 destructive 操作（本契约无）。

## 7. 与冻结契约的接口

| 契约 | 接口 |
|---|---|
| **C-05 v1.1（UNFREEZE）** | referenced 可见性分支与三谓词拆分写入 C-05 v1.1 §3.1/§3.2；本契约 §4.1 与其一致；不改 C-05 既有 managed/artifact 分支 |
| **C-06 v1.1（UNFREEZE）** | Host 铸造型发放/四维 scope/双侧 Verify/即时撤销写入 C-06 v1.1 §2.2/§2.3/§3；本契约 §5/§6 与 C-16 同批复核 |
| C-01b | SC-01/02/03/07/19/25/28/29 的存储落点；SC-04 由 §3 身份规则落地 |
| C-14 | SC-S09…S13 → §3 身份/排序/occurrence/绑定；SC-S14…S17 → `rendition_cache` + §4 读取缓存边界；DDL 由本契约冻结，语义不复写 |
| C-04b/ADJ-001 | 本契约不实现删除；binding/引用图只提供数据（引用图预检归 FEA-12） |

## 8. 不构成什么

不构成实现授权；不冻结 `source_sync_plans`/`source_operations`、FEA-11/12/13 结构；不改变 C-05/C-06 之外的冻结字节；不证明任何 AC 已达成；不改变旧 `ImportPages` 语义。

## 9. 冻结条件与变更记录

冻结条件：①C-05 v1.1/C-06 v1.1 UNFREEZE 与本契约同批独立复核 approved（P0/P1=0）；②DDL 内存实测与迁移失败注入证据；③`check.ps1`/`verify_pins` 门禁；④冻结记录含 §1A pin 口径与 §1B 复核字节。

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-03 | v1 草案：v7 DDL、Host Registry 约束、跨存储次序 | FEA-09 scope-r1 |
| 2026-11-03 | **v3（处置契约复核 r2）**：C-05 模式分派一致化（managed V 不改、referenced 不得借 artifact 绕过）；PDF page-identity 与 pixel rendition 分离；location 唯一键改为 `(source_id, content_digest, volume_serial, file_id)` + 当前位置部分唯一，重授权原地更新；callback 允许 `IResourceVerifier` 只读文件验证；binding generation ≤ 当前代次规则 | `doc/reviews/FEA-09-PREREQ-1-r2.md` R2-001/R2-003/R2-004/R2-006 |
