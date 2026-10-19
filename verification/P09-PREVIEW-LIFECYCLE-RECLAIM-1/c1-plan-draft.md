# C1 实施方案草案：删除后引用即失效

**Task**：`P09-PREVIEW-LIFECYCLE-RECLAIM-1` · **起草**：dsh · 2026-10-19 · **HEAD**：`0dc7c22f7`
**本文是准备，不是实施**：未改产品代码、未申请豁免、未冻结契约

---

## 一、C1 是什么

**用户裁定「永久删除后，已打开的译图预览允许失效」** —— 那么 AC4 的修复**不需要任何新建基础设施**：

- ❌ 不需要 catalog DB 迁移通道（**方案 A 的阻塞点**）
- ❌ 不需要 Core⟷host 通道（**方案 B 的阻塞点**）
- ✅ **只需让清理能找到 `preview-*` 行并回收**

**这就是 R7 建议的「映射前置快照」，加上一个已确认的归属判据。**

---

## 二、关键问题：如何知道哪些 `preview-*` 属于被删的书

**两条可行路径**（都已确认存在）：

### 路径 ①：按 `managed_rel_path` 前缀（**推荐**）

**`preview_lifecycle.managed_rel_path` 是相对的派生路径**，**结构含 book/chapter/page**。

**优点**：
- **不依赖 `media_artifacts`** —— **因此不受「删除时映射已消失」影响** ✅
- **单表扫描即可**，**无需 join** ✅

**待确认**：**该路径的实际前缀格式**（**需实测一条真实记录**，**不猜**）

### 路径 ②：按 `artifact_id` 经 `media_artifacts`

**R7 指出**：`execute_permanent_delete_db`（`core_service.py:1139`）**先删 `media_artifacts` 行**，**L1143 才 `cleanup_book_files`** → **反查时映射已不存在**。

**若走此路径，必须在删除前快照** —— **多一步，且引入时序依赖。**

**所以路径 ① 更简单。**

---

## 三、改动草案

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

## 六、实施前必须补的两项（未验证）

1. **`managed_rel_path` 的实际前缀格式** —— **需查一条真实记录**，**不猜**（**若前缀不含 book_id，路径 ① 不成立，需回到路径 ② + 快照**）
2. **`catalog.entries()` 在大库上的代价** —— **它是全表读**；**若 `preview_lifecycle` 行数很大，需要按前缀查询而非遍历**（**可能要给 `ResourceCatalogStore` 加一个前缀查询方法 —— 那是 API 面扩张，需确认**）

**第 2 点可能是本文最大的未决项**：**它决定这次是「接线」还是「加一个查询方法」。**

---

## 七、边界声明

**只读准备**：未改 `library.py` / `catalog_store.py` / 任何产品代码，未加列，未改 IPC，未创建 Task，未申请豁免，未改指针。
