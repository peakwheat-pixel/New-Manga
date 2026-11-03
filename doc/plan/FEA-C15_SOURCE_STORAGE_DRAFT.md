# FEA-C15 Source 存储契约（草案）

状态：**草案 / 待独立复核后由 DSH 冻结**（FEA-09-PREREQ-1 交付物；冻结后字节不得改，修订须 UNFREEZE）
日期：2026-11-03
作者：DSH（Lead / Architect / Integrator）
依据：[AD-003](../AD-003_REFERENCED_SOURCE_ARCHITECTURE.md) §3.2/§3.4/§3.5/§3.6/§4；[G-CONTRACT 关闭裁定](../plan/GATE-CONTRACT-CLOSURE-2026-11-01.md) §3.3（四表 DDL 未冻）；C-01b（存储契约，已冻）、C-05（页可见性，已冻）、C-06（授权面，已冻）、C-14（容器映射/同步/缓存，已冻，不含 DDL）；`src/infrastructure/sqlite/schema.py`（v1–v6 事实）；FEA-09 scope-r1 R1-001/R1-002/R1-007/R1-008。

**边界声明**：本契约只补「Source 生产实现的存储缺口」：DDL、迁移版本、完整性-可见性衔接、Host Registry 落地约束、Host/Core 跨存储发布次序、rendition cache 元数据边界。**不复写** C-01b/C-05/C-06/C-14 已冻结语义；**不定义** `source_sync_plans`/`source_operations` 的 DDL（FEA-11/FEA-12 前置契约）。

---

## 0. 范围与不变量

| # | 不变量 | 来源 |
|---|---|---|
| I-1 | 新导入只建立引用/索引/必要元数据，**不创建永久全尺寸输入副本**；rendition 缓存可再生产、有上限、可随时全量丢弃重建 | C-01b SC-01/SC-02；C-14 SC-S14…S17 |
| I-2 | 旧 Managed Copy 继续可读，不自动迁移、不自动删除；旧页 ID/顺序/人工数据/Lock 在迁移后守恒 | C-01b SC-07；提案 `:1026–:1028` |
| I-3 | 源身份 = 内容 digest + 授权 + lineage + Windows volume serial + file ID；**不得仅凭路径/mtime/size 断言同一文件** | C-01b SC-04；AD-003 §3.2 |
| I-4 | referenced 页只有在 binding/entry/version 完整且授权验证通过时 visible；半写行不可见但可恢复 | C-05；提案 `:893` |
| I-5 | 旧二进制打开新 Schema **必须拒写**；升级失败不留下半迁移库 | C-01b SC-19；`migrator.py` |
| I-6 | Core DB **不保存源文件绝对路径**；locator 仅容器内相对定位（成员名/页码/相对路径），路径与授权只存 Host 私有 Registry | AD-003 §3.5；C-06 §2.1 |
| I-7 | Host Registry 与 Core DB **无跨存储事务**；发布次序必须保证不出现「Core binding complete 而 Host 授权未持久化」的假成功 | 本契约 §5；C-06 §2.1 |
| I-8 | cached rendition 不是业务数据：不得含唯一人工成果/结果/恢复文件；不得写用户源目录 | C-01b SC-02/SC-03；C-14 SC-S15 |

## 1. 迁移与版本

- 新增迁移 **`v7__source_storage`**：`SCHEMA_VERSION_V7 = 7`、`MIGRATION_V7_NAME`、`MIGRATION_V7_SQL`，追加到 `default_migrations()`。**v1–v6 字节不变**；迁移仍由 `MigrationRunner` 在**单事务**内执行，checksum 机制不变。
- **旧库升级**：任意 v1–v6 库升级后 schema_version = 7；迁移前 `pre_migration` 备份沿用现有 `backup_provider` 钩子（D07 §46/§50）。
- **旧二进制拒写**：schema_version=7 > 旧代码已知 6 时 `SchemaTooNewError`（现有 `connection.py`/`migrator.py` 行为），不得「忽略新列」继续运行。
- **原子性 / 守恒验证**：FEA-09 在 `MigrationRunner` 增加**可选的 pre-commit 验证回调**（仅在本迁移事务内执行，失败即回滚，不提交半迁移）。v7 的验证至少断言：
  1. 迁移前旧谓词可见页集合 = 迁移后 `source_mode='managed' AND integrity_status='complete'` 页集合（逐 page_id 比对）；
  2. 旧不可见/半写行迁移后仍为 `incomplete`，且进入待恢复清单（不删除、不误标 complete）；
  3. `pages` 行数、`sort_order`/`source_order`、`managed_original_ref`、`source_hash`、人工数据/Lock 列逐项不变；
  4. 旧 reader projection（可见页 ID/顺序）不变。
  验证失败 → 回滚、typed 启动失败、**不切换入口**；恢复走既有备份流程（SC-37），不自动降级。
- **降级**：无自动降级；恢复迁移前 verified 备份到隔离新根（SC-37）。v7 不删除、不改写任何旧表行。
- **预留**：`source_sync_plans`、`source_operations` **不在 v7 创建**；FEA-11/FEA-12 前置契约以 `v8+` 追加。FEA-09 不得写这两张表名对应的任何持久化结构；导入取消/幂等的 receipt 为**会话内**语义（见 C-16 §5）。

## 2. 迁移 v7 的规范 DDL

以下 SQL 是冻结对象；实现必须逐字落在 `MIGRATION_V7_SQL`（注释可保留）。时间字段统一为 TEXT（UTC ISO-8601，沿用现有 `utc_now` 口径）；id 为 TEXT；布尔为 INTEGER 0/1。

```sql
-- 2.1 pages：source mode + 完整性状态（新列默认 incomplete；迁移回填旧 complete 集）
ALTER TABLE pages ADD COLUMN source_mode TEXT NOT NULL DEFAULT 'managed'
    CHECK (source_mode IN ('managed', 'referenced'));
ALTER TABLE pages ADD COLUMN integrity_status TEXT NOT NULL DEFAULT 'incomplete'
    CHECK (integrity_status IN ('incomplete', 'complete'));
UPDATE pages SET integrity_status = 'complete'
 WHERE source_hash IS NOT NULL
   AND managed_original_ref IS NOT NULL
   AND width IS NOT NULL AND width > 0
   AND height IS NOT NULL AND height > 0;   -- v1 placeholder / 半写行保持 incomplete

-- 2.2 源
CREATE TABLE sources (
    source_id TEXT PRIMARY KEY CHECK (length(source_id) > 0),
    source_kind TEXT NOT NULL
        CHECK (source_kind IN ('image', 'folder', 'zip', 'cbz', 'pdf')),
    display_name TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT
);

-- 2.3 源位置/授权绑定：不保存绝对路径（I-6）
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
    UNIQUE (source_id, registry_id, authorization_generation)
);
CREATE INDEX idx_source_locations_source ON source_locations(source_id, is_current);
CREATE INDEX idx_source_locations_registry ON source_locations(registry_id, content_digest);

-- 2.4 内容版本（content identity 与 rendition observation 分离：渲染观察在 entries 行）
CREATE TABLE source_versions (
    version_id TEXT PRIMARY KEY CHECK (length(version_id) > 0),
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    location_id TEXT NOT NULL REFERENCES source_locations(location_id),
    content_digest TEXT NOT NULL CHECK (length(content_digest) = 64),
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    observed_at TEXT NOT NULL,
    superseded_at TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (source_id, version_id),
    UNIQUE (source_id, content_digest)
);
CREATE INDEX idx_source_versions_source ON source_versions(source_id, observed_at);

-- 2.5 容器成员 / 文件条目：行键 (version_id, entry_id)；entry_id 跨版本按内容指纹保续（C-14 SC-S09）
CREATE TABLE source_entries (
    version_id TEXT NOT NULL REFERENCES source_versions(version_id),
    entry_id TEXT NOT NULL CHECK (length(entry_id) > 0),
    locator TEXT NOT NULL CHECK (length(locator) > 0),
    ordinal INTEGER NOT NULL CHECK (ordinal >= 0),
    stable_sort_key TEXT NOT NULL CHECK (length(stable_sort_key) > 0),
    content_digest_kind TEXT NOT NULL CHECK (content_digest_kind IN ('encoded', 'pixel')),
    content_digest TEXT NOT NULL CHECK (length(content_digest) = 64),
    encoded_digest TEXT CHECK (encoded_digest IS NULL OR length(encoded_digest) = 64),
    pixel_digest TEXT CHECK (pixel_digest IS NULL OR length(pixel_digest) = 64),
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    mime_type TEXT,
    width INTEGER CHECK (width IS NULL OR width > 0),
    height INTEGER CHECK (height IS NULL OR height > 0),
    orientation INTEGER CHECK (orientation IS NULL OR orientation IN (1, 3, 6, 8)),
    decoder_name TEXT NOT NULL DEFAULT '',
    decoder_version TEXT NOT NULL DEFAULT '',
    decoder_params_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    PRIMARY KEY (version_id, entry_id),
    UNIQUE (version_id, ordinal)
);
CREATE INDEX idx_source_entries_identity ON source_entries(entry_id);
CREATE INDEX idx_source_entries_digest ON source_entries(version_id, content_digest);

-- 2.6 页绑定：每页一条 current binding（partial unique），历史为 superseded 链
CREATE TABLE page_bindings (
    binding_id TEXT PRIMARY KEY CHECK (length(binding_id) > 0),
    page_id TEXT NOT NULL REFERENCES pages(page_id),
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
    FOREIGN KEY (accepted_source_version, entry_id)
        REFERENCES source_entries(version_id, entry_id)
);
CREATE UNIQUE INDEX uq_page_bindings_current
    ON page_bindings(page_id) WHERE status <> 'superseded';
CREATE INDEX idx_page_bindings_source ON page_bindings(source_id, accepted_source_version);

-- 2.7 rendition 缓存元数据（可再生产物；可随时丢弃重建；文件在 derived 根内）
CREATE TABLE rendition_cache (
    cache_key TEXT PRIMARY KEY CHECK (length(cache_key) > 0),
    source_id TEXT NOT NULL,
    version_id TEXT NOT NULL,
    entry_id TEXT NOT NULL,
    decoder_name TEXT NOT NULL,
    decoder_version TEXT NOT NULL,
    params_digest TEXT NOT NULL CHECK (length(params_digest) = 64),
    rel_path TEXT NOT NULL CHECK (length(rel_path) > 0),
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    content_digest TEXT NOT NULL CHECK (length(content_digest) = 64),
    created_at TEXT NOT NULL,
    last_used_at TEXT NOT NULL,
    active_references INTEGER NOT NULL DEFAULT 0 CHECK (active_references >= 0),
    FOREIGN KEY (version_id, entry_id) REFERENCES source_entries(version_id, entry_id)
);
CREATE INDEX idx_rendition_cache_lru ON rendition_cache(last_used_at);
CREATE INDEX idx_rendition_cache_source ON rendition_cache(source_id, version_id, entry_id);
```

约束说明（冻结语义，不是新 DDL）：

- `page_bindings.verified_digest` 必须等于 `source_entries.content_digest`；完整性谓词把二者一致性作为 referenced 页可读条件（防「Core 已 complete、条目 digest 不符」的假成功）。
- `source_entries.content_digest_kind`：图片/ZIP 成员=`encoded`；PDF 页/需规范解码的容器页=`pixel`；`pages.source_hash` 必须取同一值。
- **源复用规则**：Core 写入前先按 `(registry_id, content_digest)` 查 `source_locations`；命中则复用同一 `source_id`（不新建 source 行），未命中才新建。同一物理来源被多个项目引用时共享 source/version/entry，`page_bindings` 与页/进度/人工数据仍按项目独立（AD-003 §3.2）。
- `rendition_cache` 不是业务数据：`active_references` 仅诊断用途，淘汰的权威引用计数在进程内；崩溃后按元数据校验/重建，不得返回未校验内容。

## 3. 完整性谓词与五读路径

**referenced 页可见/可读谓词**（应用层唯一实现；SQL 等价形式）：

```sql
-- can_read_page(page) —— 在 C-05 的 V(p,t) 之上补 mode 分支；managed 分支语义不变
pages.deleted_at IS NULL
AND pages.integrity_status = 'complete'
AND pages.source_hash IS NOT NULL
AND pages.width IS NOT NULL AND pages.width > 0
AND pages.height IS NOT NULL AND pages.height > 0
AND (
    (pages.source_mode = 'managed' AND pages.managed_original_ref IS NOT NULL)
    OR (pages.source_mode = 'referenced' AND EXISTS (
        SELECT 1 FROM page_bindings b
        JOIN source_entries e
          ON e.version_id = b.accepted_source_version AND e.entry_id = b.entry_id
        WHERE b.page_id = pages.page_id
          AND b.status = 'healthy'
          AND b.verified_digest = e.content_digest))
)
```

- managed 分支与现行 `_COMPLETE_PAGE_WHERE` 等价（旧行为不变）；referenced 分支要求 healthy binding + digest 一致。
- 半写/断 binding 行（`integrity_status='incomplete'` 或 binding 非 healthy）不可见，但行保留、可诊断/可恢复；不得删除或自动改标 complete。
- C-05 的 artifact/revision 可见性谓词继续独立生效；referenced 页不伪造 `media_artifacts/artifact_revisions` 行（避免把引用源伪装成 managed 产物）。C-05 的 referenced 分支衔接以本谓词为准，**不改 C-05 冻结字节**。

**五读路径 + reader projection**（FEA-09 必须逐项回归；迁移守恒见 §1）：

| 路径 | v7 行为 |
|---|---|
| `existing_source_hashes(chapter_id)` | 取 live（未软删）complete 页的 `source_hash`；managed/referenced 同一谓词；**不得**因 occurrence 重复而按 digest 合并（去重策略由 C-16/导入层决定） |
| `max_source_order(chapter_id)` | complete 页（含软删）的最大 `source_order`；语义不变 |
| `get_page(page_id)` / `list_pages(chapter_id)` | 用 §3 谓词；referenced 页正常返回；旧 placeholder/半写行不返回 |
| `handle_resolve_page_resource` | managed 页走既有受管根解析；referenced 页必须经 C-16 `source-read` grant 读取，失败返回 `SOURCE_ACCESS_DENIED` / `SOURCE_GRANT_EXPIRED` / `SOURCE_ENTRY_MISSING` 等 typed 错误；**禁止**回退到任意路径读取 |
| reader projection | 依赖 `list_pages`/C-05 投影；referenced 页可见且可解析，人工数据/进度/顺序不因来源模式改变 |

**迁移守恒（pre-commit 验证回调的最小断言集）**：§1 四条 + 五读路径在「迁移前后旧 managed 集合」上的输出逐项相等 + 旧 FEA-06 四 PNG 不变（产品门禁）。

## 4. Host `SourceAccessRegistry` 实现约束（C-06 落地）

C-06 已冻结归属与语义；本节只冻结**实现载体与协议**，由 FEA-09 在 Host 侧实现：

- **位置**：`<HostOptions.DataRoot>/host/source-access/registry.v1.dat`（只读测试注入隔离 DataRoot；生产 `%APPDATA%\com.newmanga.desktop`）。
- **文件格式**：`ASCII magic "NMSAR1\0"`（7 bytes）+ `uint32 little-endian` 明文 JSON 长度 + **Windows DPAPI CurrentUser**（`CryptProtectData`）密文；明文 JSON 为 UTF-8：
  `{"format_version":1,"written_at":"<iso8601>","entries":[{"registry_id","locator","authorized_roots":[...],"identity_facts":{"content_digest","volume_serial","file_id","size_bytes"},"generation","created_at","last_used_at","revoked_at"?}]}`。
- **禁止持久化**：短期 grant、session signing key、lease、密码、任何源文件内容。`authorized_roots` 仅存用户授权根（规范化绝对路径），不写日志、不返回给 Core/UI 之外的层。
- **写协议**：同目录临时文件 → `FileStream.Flush(true)` → 原子替换（`File.Replace`/`File.Move` 覆盖）；单文件状态只有「旧完整快照 / 新完整快照」两态，不产生半文件。
- **并发**：Host 全局单实例（`SingleInstanceGuard`）保持不变；Registry 另加**专用跨进程命名互斥**（`Local\NewManga.Host.SourceAccessRegistry`，与 DataRoot 绑定），写超时 → typed `SOURCE_REGISTRY_BUSY`，**拒绝第二写者**；同进程用 `lock` 串行化。
- **重启**：启动时读取并校验 magic/version/length/DPAPI/JSON；不修复、不重建、不吞错。旧 session grant 一律不恢复；首用时重新验证授权根 identity（volume serial + file id）并建立新 session。
- **撤销**：`generation` 单调递增（`+1`），同时置 `revoked_at`；撤销立即使用于该 registry 的全部未过期 grant 失效（Host 校验 generation；Core 侧以签名/过期/identity 校验兜底）。
- **损坏/不确定**：解密失败、JSON 非法、magic/version 不符、长度越界、根 identity 不可验证 → **fail-closed**：所有 source 读取拒绝（`SOURCE_REGISTRY_UNAVAILABLE`）；不得用空 Registry 覆盖，不得静默重新授权。恢复只能由用户重新 `source_register_root`（新 registry 条目，旧 binding 转 needs_confirmation）。
- **持久化失败**：授权/撤销命令在磁盘写失败时**不得**返回成功、不得签发 grant；错误 `SOURCE_REGISTRY_UNAVAILABLE`（retryable=true）。
- **备份交接（FEA-13）**：Registry 文件及其 DPAPI 边界作为「源授权元数据」纳入备份清单的设计输入；备份包加密与跨机恢复由 FEA-13 实现。**跨机恢复不得自动继承可用授权**（DPAPI CurrentUser 绑定原机器/用户）：恢复后旧 registry 视为不可用，binding 需重新确认。
- **日志**：Host 日志/错误码不出现绝对路径；仅 registry_id/generation/计数。

## 5. Host/Core 跨存储发布与失败恢复次序

无跨存储事务；冻结以下次序与判定：

1. **Host 先持久化授权**：`source_register_root` 或每次操作前 Host 校验 registry 并（必要时）原子持久化 `generation`；返回 `{registry_id, generation}`。**失败 → 不进入 Core 写阶段**。
2. **Host 签发 source-read grant**（带 registry_id/generation/scope/budget/expires_at，见 C-16），随操作 dispatch 交给 Core；Core 校验签名/generation/expiry/identity 后才读取。
3. **Core 读取/解码在 DB 事务之外**：取得内容 digest 与 rendition 观察；不得在持有 SQLite 写事务时阻塞于 Host/文件 IO。
4. **Core 单事务提交**：`sources/source_locations/source_versions/source_entries` + `pages`（`source_mode='referenced'`, `integrity_status='complete'`）+ `page_bindings`（healthy, `verified_digest=e.content_digest`）在同一事务内提交；任一步失败整体回滚，未提交页不可见。
5. **提交后**：页面可读；每次读取仍以「当前授权 generation + 条目 digest」重验；Host 撤销/失联/generation 失配 → 拒绝新读（typed），已提交行保留（不自动删除、不自动改标），由 FEA-11 的重同步/确认路径处置。
6. **禁止的假成功**：不得在 Host 持久化之前写 `healthy` binding；不得在 `verified_digest` 与条目 digest 不一致时置 `complete`；不得以「文件路径仍能打开」代替授权验证。
7. **恢复/崩溃**：Host 崩溃 → 下次启动旧快照（授权可能尚未含新 generation）→ 旧 binding 读取被拒，症状为可用性下降而非数据损坏；Core 崩溃 → 事务回滚，无半写 complete 行。重试同一操作幂等（C-16 §5）；不得重发 destructive 操作（本契约无 destructive 操作）。

## 6. 与已冻结契约的接口

| 契约 | 接口 |
|---|---|
| C-01b | SC-01/02/03（缓存边界）、SC-04（身份）、SC-07（双读）、SC-19（旧二进制拒写）、SC-25/29（lease/强校验）、SC-28（content identity vs rendition）由本契约落成可存储形式；SC-03 的「非缓存」清单不得进入 `rendition_cache` |
| C-05 | `integrity_status` 与 `page_bindings` 为 C-05 谓词的 referenced 分支提供数据；**不改 C-05 字节** |
| C-06 | `source_locations.registry_id/generation` 与 identity facts 对齐 C-06 §2.1；绝对路径不落 Core DB（I-6）；source-read grant 的通信/字段由 C-16 冻结 |
| C-14 | `source_versions/source_entries/page_bindings` 是 SC-S09…S13 的存储载体；`source_sync_plans/source_operations` 预留；缓存淘汰/上限语义沿用 SC-S14…S17，本契约只补 `rendition_cache` 元数据载体 |
| C-04b / ADJ-001 | 本契约不实现删除；共享源保护与 binding 关系图只提供数据（引用图预检归 FEA-12） |

## 7. 不构成什么

- 不构成实现授权（FEA-09 scope-r2 approved 前不得写 `src/**`）。
- 不冻结 `source_sync_plans`/`source_operations`、不冻结 FEA-11/12/13 的表结构。
- 不改变 C-05/C-06/C-14 冻结字节，不改变旧 `ImportPages` 语义。
- 不证明任何 AC 已达成；本契约只有语义/结构，验收在 FEA-09。

## 8. 冻结条件与变更记录

冻结条件：①独立复核 `approved`（P0/P1=0）；②与 C-01b/C-05/C-06/C-14 无冲突；③`check.ps1` PASS；④冻结记录含 §1A pin 口径与 §1B 复核字节。

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-03 | 建立草案：v7 DDL（7 表 + pages 两列 + rendition_cache）、完整性/五读路径、Host Registry 实现约束、跨存储次序、冻结条件 | DSH；FEA-09 scope-r1 R1-001/R1-002/R1-007/R1-008；G-CONTRACT 关闭裁定 §3.3 |
