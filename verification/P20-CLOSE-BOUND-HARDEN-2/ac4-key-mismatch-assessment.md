# AC4 评估结论：译图预览在永久删除时不被回收（R6 FAIL）

起草者：dsh（Coordinator, epoch 8）· 2026-10-19 · HEAD：`34de66348` · **本文件是 R124 授权「重新评估 AC4」的产出：未改产品代码、未申请豁免、未改指针**

---

## 一、R6 的现象

> 「真实 `GetReaderProjection` 发布后再执行永久删除，观察到 `retired=False`、catalog 项仍存在、预览文件仍存在、该项不是 retired GC candidate。」

**AC4 判定：FAIL。**

---

## 二、根因：两侧的 key 从不相等

| 侧 | 代码 | 生成的 key |
|---|---|---|
| **发布** | `render_preview.py:69` — `resource_id = f"preview-{uuid.uuid4().hex}"` | **`preview-<32 位随机>`** |
| **清理** | `library.py:1124` — `res_id = f"page-original-{pid}"` | **`page-original-<page_id>`** |

**两者永不相等** → `catalog.lookup(res_id)` 返回 `None` → **跳过** → **永久删除后译图预览仍在磁盘、catalog 项仍在** → **GC 也不认它**（`retired=0`，而 GC 只处理 `retired=1`）。

**流程本身是接好的** —— `handle_permanently_delete_book`（`core_service.py:1107`）在 `execute_permanent_delete_db` 之后**确实调用了 `cleanup_book_files` 并传了 `render_previews=self._render_previews`**（L1143-1147）。**问题不在「有没有接」，而在「按什么 key 去找」。**

---

## 三、我此前为什么判它通过

**AC4 的原始缺陷**（`test_p09_ac4_translated_preview.py` 的 docstring）：reader 发布时 `origin=None` → **不写 `preview_lifecycle` 行** → 永久删除找不到它 → **每页每次译图阅读泄漏一个 artifact**。

**已修的部分**：**现在会写 origin 行** ✅ —— 我的测试验证的正是这个（行存在、绑定正确的 artifact/revision、`managed_rel_path` 是相对的、`producer_root / rel_path` 指向真实文件）。

**未修的部分**：**key 仍然不匹配**。

**所以我的判断「AC4 通过」是对的但不充分**：**「lifecycle 行存在」不等于「删得掉」** —— **还需要「用正确的 key 去找」。我验证了前者，把后者当作它的推论。**

**这与本会话反复出现的模式一致**：**我验证了「修复的副作用」，而不是「能力本身」**（同 F-002 的测试、同 N-004 的静态探针）。

---

## 四、修法方向与可行性（已实测确认）

### 方向 ①（推荐）：清理侧按 artifact 反查

**不做任何发布行为改动**，只让清理能通过 `preview_lifecycle` 找到该资源。

**可行性已确认**：

| 事实 | 证据 |
|---|---|
| `preview_lifecycle` **有 `artifact_id` 与 `artifact_revision_id`** | `catalog_store.py:76-83` 的 schema |
| `media_artifacts` **有 `page_id`** | `test_p09_ac4_translated_preview.py` 的 INSERT |
| **catalog 与 library 是不同 DB** | 测试用 `catalog.sqlite` 独立文件；`SqliteLibraryRepository(conn)` 是 library DB |
| **`render_previews._catalog.entries()` 可用** | `render_preview.py:194` 已在用 |

**因此反查是两步**（跨 DB，不能一条 SQL）：

```
1. library DB:  page_id → artifact_id          （查 media_artifacts）
2. catalog:     artifact_id → resource_id      （需新增一个按 artifact_id 查的方法，
                                                或遍历 entries() 后逐个 preview_lifecycle_row）
```

**代价**：需要给 `ResourceCatalogStore` **加一个查询方法**（或接受遍历）。**这是本方向唯一的额外改动。**

### 方向 ②：发布侧改用确定性 key

**风险更高**：`publish` 每次生成新 key **可能是 rerender 轮换的设计前提**（`rotate_render_preview` 靠「新 key ≠ 旧 key」判断是否退休旧资源）。

**若把 `publish` 改成确定性 key，rerender 会产生 same-key 情形** → 触发「同 key 不退休」分支 → **N-002/F-002 那套已验证的行为会改变**。

**因此方向 ② 需要先确认「uuid key 是设计还是偶然」** —— **不能凭偏好选**。

**旁证**：`publish_original` **接受调用方传入 `resource_id`**（`core_service.py:1944`）—— 说明「确定性 key」在本项目里是既有模式，**但 `publish` 显然被有意设计为每次不同**。

---

## 五、推荐

**方向 ①** —— 它不动发布语义，**不触及 rerender 轮换、退休、GC 那一整套已验证的行为**，**只在清理侧补上「按 artifact 找」的能力**。

**需要的授权**：**新增一个 catalog 查询方法**（改动共享契约的表访问面，虽非 IPC 契约变更，但属 API 面扩张）→ **这一点应由你或 Codex 定**。

---

## 六、影响面（供优先级判断）

**每页每次译图阅读泄漏一个 artifact 变体**（`publish` 每次调用生成新 key、新 catalog 行、新文件）。

**具体规模未实测** —— 我**没有**做过「一次阅读会话产生多少条 `preview-*` 行」的测量。**若要判断严重性，这是应先测的数字**，而它只读、无需授权。

---

## 七、决定性发现：代码注释自己记录了缺陷的另一半

`core_service.py:1968-1976`（`handle_get_reader_projection` 的 `publish` 调用处）原文：

```
# AC4 (N-003): publish WITH an origin so the preview lands in
# preview_lifecycle and can be reclaimed by reference.  Without
# it the row is catalog-only - which the publisher itself
# documents as "never reclaimable" - so every translated read
# leaked one permanent artifact per page, and the permanent
# delete could not find any of them because cleanup only knows
# the deterministic page-original key.  Passes None when no
# single source revision matches, which keeps the previous
# behaviour and never blocks the reader from opening.
```

**这段注释把两件事都写出来了**：

1. **有 origin → 写 lifecycle 行**（**已做**）
2. **「cleanup only knows the deterministic `page-original` key」**（**已识别，但未修**）

**而结论句写的是「can be reclaimed by reference」** —— **它把「写了 origin 行」当成了「可以被回收」，而注释上一句刚刚说明「清理只认确定性 key」。**

**这是「半修复 + 注释记录了另一半但没做」** —— 而且**注释的措辞让后读者以为已经完成**。**若非 R6 用真实 `GetReaderProjection` 走了一遍永久删除，这个缺口会一直看不出来**：**测试验证了行存在，注释说它能被回收，两者互相印证，而实际上谁也找不到它。**

## 八、事实 #1 的完整答案（已查明）

**`ARTIFACT_TYPE_DIRS`（`managed_storage.py:29-40`）共 10 种类型**：

```
original · thumbnail · detection_overlay · mask · clean ·
translated · render_preview · export · debug_ocr · debug_detection
```

**但只有 2 处调用 `publish`**（即只有它们会创建 `preview-*` catalog 行）：

| 位置 | handler | origin 来源 |
|---|---|---|
| `core_service.py:1721` | **`handle_rerender_page`** | `self._resolve_preview_origin(outcome)` |
| `core_service.py:1977` | **`handle_get_reader_projection`** | `self._resolve_preview_origin_for_page(page)` |

**两处都传了 `origin`** → **都会写 `preview_lifecycle` 行**。

**结论**：**`mask` / `clean` / `thumbnail` / `export` 等类型不创建 preview catalog 行**，**因此方案里 `WHERE artifact_type = 'translated'` 的范围判断方向正确** —— **但需确认这两处在 `media_artifacts` 里登记的 `artifact_type` 是否都是 `translated`**（`handle_rerender_page` 的渲染产物类型我尚未确认 —— **它是 `translated` 还是 `render_preview`？这决定 `WHERE` 条件是否命中它**）。

**⚠️ 这正是方案第四节第 1 条标注的价值**：**若不查这一步，`handle_rerender_page` 产生的预览会被静默跳过。**

## 九、边界声明

**只读评估**：未改任何产品代码、未创建 Task、未申请豁免、未改指针。写入 `verification/P20-CLOSE-BOUND-HARDEN-2/`。
