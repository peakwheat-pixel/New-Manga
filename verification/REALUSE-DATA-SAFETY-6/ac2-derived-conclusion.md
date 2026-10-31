# AC2（MA-19）`derived/` 全尺寸副本：结论与证据

- Task：REALUSE-DATA-SAFETY-6 / AC2（审计条目 MA-19）
- 分支：`task/REALUSE-DATA-SAFETY-6`（base `main@841cbdc4b`）
- 结论日期：2026-11-01
- 真实数据只读盘点原始输出：[ac2-derived-realdata.json](ac2-derived-realdata.json)

## 1. 结论（TL;DR）

**现阶段 `derived/` 下的全尺寸原图副本是必需的，本 Task 不能安全去掉；因此没有做任何代码删改（最小化改动的正确形态是"不改"）。**

三条独立理由，任一条单独成立都足以否决"删除副本"：

1. **服务通道只按 catalog 行 + 作用域根提供字节**，而现网 catalog 里 169 条全部是 `derived-read-only`、0 条 `managed-read-only`；"直接读 managed 原件"这条路径在代码里存在（`HostRuntime` 支持两个作用域根），但没有生产者把 managed 文件登记进 catalog。
2. **`preview_namespace` 把 catalog 身份与 `derived/` 根身份绑定在同一把锁里**；managed 根没有对应的命名空间绑定/租约，改成从 managed 根供字节等于改资源通道契约与身份模型（冻结契约范围，本 Task 明确禁止）。
3. **AD-003 明文禁止以"消除双份"为由删除 `derived/`**：`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md` §3.2 把 `derived/` 定义为"有上限的可再生产物"，并在同一节写死"未实现新源读取前，不得以'消除双份'为由删除现有 `derived/` 或 managed 文件"。

另外需要修正 MA-19 原始描述的两处口径（不改变结论，只更新事实）：

- "无自动清理"**不准确**：`derived/` 已有启动期 GC（孤儿文件 + 死行清理，见 §2.5）。真正无法回收的是**活页**的 `page-original-*` 副本——它是阅读器供字节的唯一产物，按设计在页面存活期间必须存在。
- 磁盘 2× 是**确定性可复现的**（不是漂移/泄漏）：每个活页恰好 1 个 managed 原件 + 1 个 derived 副本，样本 sha256 完全一致，删掉副本下一次 resolve 会用同一个确定性键把它原样重建。

## 2. 代码证据（读资源通道）

### 2.1 解析（resolve）把 managed 原件按确定性键发布进 derived

- `src/bootstrap/core_service.py:3189` `handle_resolve_page_resource()`：注释写明键是确定性的 `page-original-{page_id}`，"first resolve publishes the file byte-for-byte into the derived read-only root … every later resolve is a catalog lookup"。
- `src/bootstrap/core_service.py:3225` 用 `managed_root_trust.read_bytes()` 读取 managed 原件（经校验句柄，防 junction 逃逸）；`src/bootstrap/core_service.py:3234` 拼键 `page-original-{page_id}`；`:3248` 调 `publish_original(...)`。
- `src/bootstrap/core_service.py:3236` 的 catalog 命中分支还带 `artifact_exists()` 探针：**derived 文件被清掉会自动按同键重建**（`src/infrastructure/resource_channel/render_preview.py:31`）。
- `src/infrastructure/resource_channel/render_preview.py:115` `publish_original()`：`temp + fsync + os.replace` 逐字节复制到 `<derived>/pages/<resource_id><suffix>`，并写 catalog 行（scope 固定 `derived-read-only`，`render_preview.py:149`）。
- `src/infrastructure/resource_channel/render_preview.py:15-19` `ORIGINAL_REVISION = "original"`：注释明确"contract rev 1.7 freezes the literal"——解析键与修订标签属冻结契约面。
- 阅读器投影对**每一页**调用一次上述解析：`src/bootstrap/core_service.py:3270`（`handle_get_reader_projection` 内循环）。

### 2.2 Host 侧按作用域根供字节（两个根都支持，但只有 derived 有数据）

- `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs:511` `ReadPageImageAsync()`：Core `resolve_page_resource` → bridge `issue` → `resolve` → 按 `ScopeClass` 选根。
- `HostRuntime.cs:523-528`：`derived-read-only` → `<dataRoot>/derived`；`managed-read-only` → `ManagedRoot`（缺省 `<dataRoot>/managed`）；其他作用域直接 `SCOPE_NOT_SERVABLE`。
- `HostRuntime.cs:534-546`：拼绝对路径后交给 `TileChannel`（`apps/desktop-avalonia/src/NewManga.Host/Resources/TileChannel.cs`）做句柄校验的整文件读（身份/大小/摘要 + 拒绝 reparse）。

> 也就是说："从 managed 根直接供字节"在 Host 侧**已经具备能力**，缺的是 Core 侧的 catalog 登记与命名空间绑定（§2.3）。

### 2.3 catalog 与命名空间只登记了 derived

- 允许的作用域类：`src/application/resource_channel/dto.py:69` `ALLOWED_SCOPE_CLASSES = ("derived-read-only", "managed-read-only")`。
- 写入入口：`src/infrastructure/resource_channel/catalog_store.py:684` `upsert()`（`:696-698` 拒绝非法 scope）；`catalog_store.py:128` `PREVIEW_ORIGIN_SCOPE = "derived-read-only"`，`:726` 明确 `scope_class_of_origin(rel_path) != PREVIEW_ORIGIN_SCOPE` 拒绝。
- 命名空间绑定：`src/infrastructure/resource_channel/catalog_store.py:198` `initialize_namespace(catalog_db, derived_root)` 把 catalog 身份与 **derived 根身份**（volume serial + file index）写进 `preview_namespace` 单行；`src/infrastructure/resource_channel/handle_resolver.py` 的共享/独占租约（`acquire_shared_lease(...)`、`try_acquire_exclusive_lease(...)`）都以 `expected_catalog_identity` 校验这条绑定；`src/bootstrap/core_service.py:5757`/`:5798` 启动时正是这样加锁。
- 真实数据：`catalog.sqlite.resource_catalog` 169 行，`GROUP BY scope_class` 只有 `derived-read-only`（见 JSON 的 `catalog_scope_classes`）；`preview_namespace` 单行绑定 `derived_root=%APPDATA%\com.newmanga.desktop\derived`。

### 2.4 derived 根同时是"服务面"与"GC 面"

- 启动顺序：`src/bootstrap/core_service.py:5752-5800`（先命名空间保护，再独占租约跑 sweep，降级为共享租约后开始服务）。
- 孤儿/死行清扫：`src/infrastructure/resource_channel/render_preview.py:158` `collect_orphans()`——只清 `previews/`、`pages/` 下**无 catalog 行**的文件与**指向不存在文件**的行；活页行永不清（`:180-183`）。
- 旧预览回收：`render_preview.py:235` `delete_retired_preview_copy()` + `core_service.py:5891` 的 retired sweep（按 sha256/size 校验句柄删除）。
- 根身份不符即拒绝：`core_service.py:5541` "different derived root" / `:5553` `_ensure_preview_namespace()`。

### 2.5 结论性推断

- 删除 derived 活页副本 → 下一次 `resolve_page_resource` 会用同一个 `page-original-{page_id}` 键**原样重建**（`render_preview.py:31` + `core_service.py:3236`）。所以"删副本省空间"在现行实现下**不成立**：要么立刻重建，要么读图失败。
- 想真正取消这份副本，必须动冻结契约/命名空间模型（见 §4），不是清理动作。

## 3. 真实数据只读印证（未写入、未删除任何真实数据）

数据根：`C:\Users\49745\AppData\Roaming\com.newmanga.desktop`（产品默认 `%APPDATA%\com.newmanga.desktop`）。
方法：只读枚举 + 只读 SQLite（`file:...?mode=ro`）+ 对样本文件做流式 sha256。原始 JSON 见 [ac2-derived-realdata.json](ac2-derived-realdata.json)。

| 项 | 值 |
|---|---|
| managed 根 | 169 文件 / 100,434,899 字节 |
| derived 根 | 170 文件 / 100,435,214 字节（= 169 张 `pages/page-original-*.jpg` + `.preview-lifecycle.lock` 315 B） |
| derived/previews | 不存在（还没有渲染预览） |
| 重复量 | 100,434,899 字节 ≈ 2×（managed 与 derived/pages 完全等量） |
| `pages` 行 / 有 `managed_original_ref` 的页 | 169 / 169 |
| managed 与 derived 成对存在且同尺寸 | 169 / 169（`missing_managed` 空、`missing_derived` 空） |
| 逐字节证明（样本页 `48b5b58e82e94e6f9a0d70676426676c`） | managed sha256 = derived sha256 = `70c2fd73…e6eb07`，size 82,862 双向一致 |
| catalog scope 分布 | `derived-read-only` = 169，其余 0 |
| `preview_namespace` | derived_root 绑定真实 derived 路径（volume 1485189147 / index 72620543991401102） |

辅助事实（与 AC1/AC3 相关，同一只读盘点）：

| 库 | books | chapters | pages | reading_progress |
|---|---|---|---|---|
| `library.db`（当前根） | 1 | 1 | 169 | 1 |
| `data/library.db`（旧布局，MA-11） | 1 | 0 | 0 | 0 |

## 4. 若要真正去掉这份副本：前置条件（本 Task 不做，供 DSH/用户裁决）

| 方案 | 做法 | 前置/影响 | 风险 |
|---|---|---|---|
| O-1 契约级：managed 直接供字节 | Core 为 managed 原件登记 `managed-read-only` catalog 行（rel_path 相对 managed 根），Host 现有 `HostRuntime.cs:526` 分支即可直接服务 | 需改冻结契约（`resolve_page_resource` 的作用域语义、M2-C1 rev 1.7 的 `page-original-*`/`original` 字面量）、为 managed 根新增命名空间绑定/租约、GC 必须显式排除 managed 行（否则 `collect_orphans` 会误判） | 高：动服务面身份模型与 GC 边界；需独立 Review + 真机验证 |
| O-2 ReferencedSource 通道 | 新引用页经 AD-003 §3.5 的 `SourceAccessRegistry` + `source-read` grant 直读原文件；managed 旧数据继续双读 | AD-003 `G-CONTRACT` 仍 OPEN，`SourceAccessRegistry`/`source-read` 均未实现；属 Source 线实现范围 | 中高：架构级，先决条件未满足，禁止现在改生产导入/资源路径 |
| O-3 只做计量/诊断 | 增加 derived 占用与重算统计（不改服务面） | 低风险，但**不减少**任何字节，只改善可观测性 | 低 |

建议（不构成裁决）：保持现状 + 把 O-1/O-2 记为资源通道契约演进的候选，等 `G-CONTRACT` 关闭、Source 线解冻后由 DSH 正式立 Task；在此之前**不删副本、不改 GC、不改 resolve 契约**。

## 5. 本 Task 实际改动

- **无生产代码改动**（AC2 为结论型）。仅有本文件 + `ac2-derived-realdata.json` 两份证据。
- 未触碰真实数据：全部操作为读取（枚举、只读 SQLite、读取样本文件算 sha256）；DB 副本复制到仓外的 `G:\CODEX\New Manga.workspace\tmp\REALUSE-DATA-SAFETY-6\dbcopy`，**未**在真实数据根写入任何文件，也未创建 `-wal/-shm`。

## 6. 复现步骤（只读）

```powershell
$root = Join-Path $env:APPDATA 'com.newmanga.desktop'
Get-ChildItem (Join-Path $root 'managed') -Recurse -File | Measure-Object -Sum Length
Get-ChildItem (Join-Path $root 'derived\pages') -Recurse -File | Measure-Object -Sum Length
# 样本对照：pages.managed_original_ref 与 derived/pages/page-original-<page_id>.<suffix>
# sha256 对照见 ac2-derived-realdata.json 的 digest_proof 段
```

注意：任何清理/迁移动作都必须在获得用户授权后另立 Task，并遵守 AD-003 §3.1/§3.2 与 ADJ-001。
