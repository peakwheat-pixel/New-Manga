# AC4 方向①实施方案：清理侧按 artifact 反查

起草者：dsh（Coordinator, epoch 8）· 2026-10-19 · HEAD：`92d1eacb9` · **本文件只做准备：未改产品代码、未申请豁免、未改指针**

**目标**：让永久删除能回收 `publish` 创建的 `preview-<uuid>` 预览，**且不改变发布语义**（不改 `publish`、不动 rerender 轮换）。

---

## 一、已确认的事实（全部有证据）

| 事实 | 来源 |
|---|---|
| `publish` 生成 `preview-{uuid4}` | `render_preview.py:69` |
| 清理查 `page-original-{pid}` | `library.py:1124` |
| **两者永不相等** | 实测：5 次阅读产生 5 个 `preview-*` 行，清理只能找到 `page-original-p1` |
| `preview_lifecycle` 有 `artifact_id` | `catalog_store.py:79` |
| `media_artifacts` 有 `page_id` | `tests/core/test_p09_ac4_translated_preview.py` |
| catalog 与 library 是**不同 DB** | 测试用独立 `catalog.sqlite` |
| 泄漏率 = **1 行 + 1 文件 / 次译图阅读** | `ac4-leak-count-probe.py` 实测 |
| `cleanup_book_files` 已有 `render_previews` | `library.py:1105` 已用 `render_previews._catalog` |

**关键**：`cleanup_book_files` **已经能访问 catalog**（`getattr(render_previews, "_catalog", None)`）—— **所以不需要新的跨 DB 通道**。

---

## 二、需要的唯一新 API

**给 `ResourceCatalogStore` 加一个按 `artifact_id` 查 lifecycle 行的方法**（与既有 `preview_lifecycle_row(resource_id)` 并列）：

```python
def preview_lifecycle_rows_for_artifact(self, artifact_id: str) -> list[PreviewLifecycleRow]:
    """Preview lifecycle rows registered for one artifact.

    AC4: publishes mint a uuid4 key per call, so the cleanup cannot find them by the
    deterministic page-original-<page_id> name it has always used.  The lifecycle row
    records the artifact it came from, so that is the link back.  Read-only; the
    caller's write rights and the channel's single-lifecycle-write rule are untouched.
    """
    with self._lock:
        rows = self._connection.execute(
            "SELECT resource_id, producer_root, artifact_id, artifact_revision_id,"
            " managed_rel_path, retired"
            " FROM preview_lifecycle WHERE artifact_id = ?"
            " ORDER BY resource_id",
            (artifact_id,),
        ).fetchall()
    return [self._lifecycle_row_from(row) for row in rows]
```

**注意**：**这是只读方法** —— **不触碰「channel 唯一的生命周期写操作是 `mark_preview_retired`」这条设计约束**（`catalog_store.py:25` 明确写了它）。

**若不愿扩 API**：备选是遍历 `entries()` 后逐个 `preview_lifecycle_row()` —— **同样只读，但 O(n)**。**建议加方法**（项目已有 `retired_preview_candidates` 这类专用查询，风格一致）。

---

## 三、`cleanup_book_files` 的改动

**当前**（`library.py:1116-1143`）：对每个 `pid` 查 `page-original-{pid}`。

**改为两步**：

```python
            for pid in page_ids:
                # AC4: publishes mint preview-<uuid4>, so the deterministic name
                # below only ever matches the original-side entry.  Resolve the
                # artifact for this page first and take every preview row
                # registered against it - that is what the lifecycle row is for.
                candidates = []
                legacy = catalog.lookup(f"page-original-{pid}")
                if legacy is not None:
                    candidates.append(legacy.resource_id)

                row = self._conn.execute(
                    "SELECT artifact_id FROM media_artifacts WHERE page_id = ?"
                    " AND artifact_type = 'translated'",
                    (pid,),
                ).fetchone()
                if row is not None and hasattr(catalog, "preview_lifecycle_rows_for_artifact"):
                    for life in catalog.preview_lifecycle_rows_for_artifact(row["artifact_id"]):
                        if life.resource_id not in candidates:
                            candidates.append(life.resource_id)

                for res_id in candidates:
                    entry = catalog.lookup(res_id)
                    if entry is not None and entry.rel_path:
                        removed = unlink_preview_without_following(str(entry.rel_path), root_res)
                        if not removed:
                            all_deleted = False
                            continue
                    catalog.remove(res_id)
```

**三个要点**：

1. **保留旧的确定性查找**（`page-original-{pid}`）—— **别删**：`publish_original` 用它，实测它**确实存在且能被找到**
2. **`artifact_type = 'translated'`** —— 只回收译图侧；**若同页有其它 artifact 类型也需回收，需另行确认**（**这一点我未验证，实施前应查 `media_artifacts` 在真实数据里有哪些 type**）
3. **`hasattr` 守卫**（可选）—— **使旧 catalog 实现仍能工作**；**若确定同步升级则可去掉**

---

## 四、验证方案

| 项 | 方法 |
|---|---|
| **泄漏归零** | 复用 `ac4-leak-count-probe.py` 扩展：阅读 N 次 → **永久删除** → 断言 `preview-*` 行归零、文件归零 |
| **确定性条目仍被回收** | 断言 `page-original-p1` 仍被删除（**防回退**）|
| **不误删** | 断言**其它页/其它 book 的 `preview-*` 不受影响**（**跨页隔离**）|
| **回归** | `tests/storage`、`tests/core`、AC4 既有测试 |
| **R6 的复现** | 用真实 `GetReaderProjection` + 永久删除，断言不再是 `retired=False` 且文件消失 |

**注意**：`ac4-leak-count-probe.py` **当前是「测量」不是「断言」** —— 修好后应改成**断言泄漏为 0**，并**在修前跑一次留作红证据**。

---

## 五、未验证项（实施前必须补）

1. **`media_artifacts` 在真实数据里有哪些 `artifact_type`** —— 我只在测试里见过 `translated`。**若同页还有其它类型需要回收，`WHERE` 条件会漏掉它们。**
2. **一个 `artifact_id` 是否可能对应多个 `preview-*` 行**（rerender 轮换会不断新建）→ **反查可能返回多行** —— **这是期望行为（全部回收），但需确认不会误删仍被引用的行**（`retired` 字段可作区分依据，**但当前逻辑不区分**）。
3. **`catalog.remove(res_id)` 与文件删除的原子性** —— 既有代码已是「删文件成功才 remove 行」，**沿用即可**。

**第 2 点最需要注意**：**若一个 artifact 有多行（历史轮换遗留），全删是对的**；**但若某行仍指向当前在用的预览，删掉会导致当前页面预览失效** —— **需要用 `retired` 或「是否为当前 revision」过滤**。

---

## 五之二、两项未验证事实的结论（2026-10-19 补充）

### 事实 #1：**已查明** ✅

**`ArtifactType` 枚举（`ports/repositories/artifacts.py:17-25`）共 6 种**：`original` · `thumbnail` · `detection_overlay` · `mask` · `clean` · `translated`。
**`ARTIFACT_TYPE_DIRS`（`managed_storage.py:29-40`）共 10 种**（多出 `render_preview` · `export` · `debug_ocr` · `debug_detection`）。

**但只有 2 处调用 `publish`**，**且两处登记的 artifact 类型都是 `translated`**：

| 位置 | handler | 产物类型 |
|---|---|---|
| `core_service.py:1721` | `handle_rerender_page` | **`ArtifactType.TRANSLATED`**（`rendering/service.py:177` 与 `:349` 两处 `create_artifact` 均为此类型）|
| `core_service.py:1977` | `handle_get_reader_projection` | 译图（translated）|

**结论**：**`mask` / `clean` / `thumbnail` / `export` 等类型从不创建 preview catalog 行** → **方案里 `WHERE artifact_type = 'translated'` 的范围正确，不会漏掉 `handle_rerender_page` 的预览** ✅

### 事实 #2：**分析结论（未实测，实施前必须验证）** ⚠️

**关键链条**（依据 `rendering/service.py:170-182`）：

```python
translated = self._locator.locate_current(page_id, ArtifactType.TRANSLATED)
if translated is None:
    translated_record = self._artifacts.create_artifact(...)   # 仅当不存在时新建
    ...
else:
    ...                                                        # 已存在 → 复用同一 artifact_id
```

**所以同一 `artifact_id` 会被多次 `publish`**，**每次产生一个新的 `preview-{uuid}` 行**。**这与实测一致**（5 次投影 → 5 行，同一页同一 artifact）。

**而 `retired` 无法区分「在用」与「遗留」**：

- **`retired` 只在 `revoke_resource_retiring_preview` 里被置 1**
- **该调用只发生在 `rotate_render_preview`（rerender 轮换）路径**
- **reader projection 路径不轮换** → **历史行全部保持 `retired=0`**

**因此「全删」有真实风险**：**若 WebView 仍持有某个历史 `preview-*` 的引用，删掉它会让当前页面预览失效** —— 而 **`preview_lifecycle` 里没有任何字段能告诉我们是哪一个**。

**这不是接线能解决的问题** —— **它需要一个新的判定依据**，例如：

- **保留每个 artifact 最新的一行**（按 `created_at` 或插入顺序）—— **但表里没有时间戳** ⚠️
- **让 reader 投影走轮换语义**（每次新 publish 时退休上一个）—— **改动较大，但语义最干净**
- **引入引用计数**（WebView 持有/释放时上报）—— **改动最大**

**⚠️ 本方案因此不能直接实施。** 需要先回答「如何判定某行为在用」，**这是一个设计决策，不应在方案里替它决定**。

**建议的下一步**：**把这一项并入 `P09-MANAGED-READ-ROOT-TRUST-1` 之前先做一次独立评估**，或者**单独开一个 AC4 修复 Task**（因为它的性质是「产品行为 + 生命周期设计」，与删除路径加固不同类）。

---

## 六、边界声明

**只读准备**：未改 `library.py` / `catalog_store.py` / 任何产品代码，未创建 Task，未申请豁免，未改指针。
