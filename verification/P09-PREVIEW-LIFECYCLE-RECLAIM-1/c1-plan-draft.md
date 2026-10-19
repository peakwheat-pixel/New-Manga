# C1 实施方案草案：删除后引用即失效

**Task**：`P09-PREVIEW-LIFECYCLE-RECLAIM-1` · **起草**：dsh · 2026-10-19 · **HEAD**：`0dc7c22f7`
**本文是准备，不是实施**：未改产品代码、未申请豁免、未冻结契约

---

## 一、C1 是什么

**用户裁定「永久删除后，已打开的译图预览允许失效」（**裁决记录见 `c1-ruling-record.md`**）** —— 那么 AC4 的修复**不需要任何新建基础设施**：

- ❌ 不需要 catalog DB 迁移通道（**方案 A 的阻塞点**）
- ❌ 不需要 Core⟷host 通道（**方案 B 的阻塞点**）
- ✅ **只需让清理能找到 `preview-*` 行并回收**

**这就是 R7 建议的「映射前置快照」，加上一个已确认的归属判据。**

---

## 二、归属判据：只能走「删除前快照」（R189 实测修正）

**本文初版提出的「按 `managed_rel_path` 前缀匹配」已被实测否定。**

**实测**：`preview-*` 的 `rel_path` 由 `render_preview.py` 构造：

```python
L69-70:  resource_id = f"preview-{uuid.uuid4().hex}"
         rel_path    = f"previews/{resource_id}.png"
L138:    rel_path    = f"pages/{resource_id}{suffix}"
```

**即 `previews/preview-<32 位 uuid>.png`** —— **不含 book / chapter / page 的任何成分，无法按书筛选。**

**对比**：`page-original-{pid}` 的路径含 `page_id`，可以反查所属 book。**`preview-*` 完全不能。**

**所以归属只能经 `artifact_id`**：

```
page_ids → media_artifacts.artifact_id → preview_lifecycle.resource_id
```

**而 `execute_permanent_delete_db`（`core_service.py:1139`）会先删掉 `media_artifacts` 行**，
**`cleanup_book_files`（L1143）运行时映射已不存在** →

> **必须在删除【之前】快照出待回收的 `resource_id` 列表。**

**这正是 R7 当年对方案 A 的批评**（「使 artifact/resource 映射在数据库删除前可用」）——
**它现在成了 C1 唯一的实现路径。**

## 三、改动草案

**改动位置有两处**（初版只写了 1 处）：

**(a) `core_service.py` 的永久删除流程** —— 在 `execute_permanent_delete_db` 之前，按 `page_ids` 快照出待回收的 `resource_id` 列表；
**(b) `library.py:cleanup_book_files`** —— 接收该列表并逐个回收。

### 1. `cleanup_book_files`（`src/infrastructure/sqlite/library.py:1082`）

**当前**：对每个 `pid` 查 `catalog.lookup(f"page-original-{pid}")` —— **只能命中确定性 key**。

**增加**：**按 book 前缀扫描 `preview-*` 行**。

```python
# 伪码：在现有 page-original-{pid} 循环之外，增加一次前缀扫描
preview_rows = [
    row for row in catalog.entries()
    if row.resource_id.startswith("preview-")
    and _belongs_to_book(row, book_id)      # 按 managed_rel_path 前缀判定
]
for row in preview_rows:
    removed = unlink_preview_without_following(str(row.rel_path), root_res)
    if removed:
        catalog.remove(row.resource_id)
```

**注意**：**现有的 `page-original-{pid}` 查找必须保留** —— **实测它确实存在且能被回收**（那是 `publish_original` 建的）。

### 2. 计数语义（**沿用本 Task 已修的规则**）

**被拒绝的行不计入任何「已删除」统计** —— 这是 `P09-AC3-DELETE-HARDEN-1` 里用探针量出来的教训。

### 3. 不需要改的地方

- **`preview_lifecycle` 不加列** ✅
- **`ResourceChannelService` 不动**（**它在另一个进程，本来就够不着**）✅
- **不改 IPC** ✅
- **不改 `publish` 的 key 生成方式**（**`preview-{uuid4}` 保持不变**）✅

---

## 四、已知代价（诚实记录）

**C1 的语义代价**：**若用户在永久删除的同一时刻正打开该书的预览，那张图可能加载失败。**

**为什么我认为可接受**：

- **永久删除需要显式 `confirm_permanent_delete`**（`core_service.py:1117`）—— **是用户明确确认的破坏性操作**
- **用户不会在删除一本书的同时要求它的预览继续可读**
- **替代方案（A/B）的代价是新建一条跨进程通道**，**用于一个本身可疑的场景**

**⚠️ 但这是产品判断，不是技术判断** —— **若用户选 C2，本文作废。**

---

## 五、验证方案（**修前必须先跑出红**）

| 项 | 方法 |
|---|---|
| **泄漏归零** | 扩展现有 `ac4-leak-count-probe.py`：**读 N 次 → 永久删除 → 断言 `preview-*` 行与文件均归零**。**当前它只测量不断言，必须先改为断言并跑出红** |
| **确定性条目仍被回收** | 断言 `page-original-{pid}` 仍被删（**防回退**）|
| **跨书隔离** | **删 A 书不得影响 B 书的 `preview-*`** |
| **被拒绝的不计入统计** | 专门断言 |
| **不回归** | `tests/storage` + `tests/core` + `P09-AC3-DELETE-HARDEN-1` 的 9 个探针 |

---

## 六、两项未验证事实：已测出（R189）

**① `managed_rel_path` 的前缀格式** —— **已测：不含 book_id** ❌
**→ 路径 ① 不成立，归属改走 `artifact_id` + 删除前快照**（见第二节）。

**② `catalog.entries()` 的代价** —— **已测：全表读，无过滤**（`catalog_store.py:794-800`）：

```python
rows = self._connection.execute(
    "SELECT resource_id, scope_class, rel_path FROM resource_catalog ORDER BY resource_id"
).fetchall()
```

**且 `catalog_store.py` 内没有 `LIKE` / `startswith` 之类的前缀查询** →
**若要避免全表遍历，需新增查询方法（API 面扩张）** —— **但按 `resource_id` 精确查已有先例**
（`preview_lifecycle_row`、`lookup`），**所以按快照列表逐个查是既有机上的用法，不需要新方法** ✅

**结论**：**两项测量都没有把 C1 变成「加 API」，但第一项把改动位置从 1 处变成了 2 处。**
## 七、边界声明

**只读准备**：未改 `library.py` / `catalog_store.py` / 任何产品代码，未加列，未改 IPC，未创建 Task，未申请豁免，未改指针。
