# P09-PREVIEW-LIFECYCLE-RECLAIM-1 草案：AC4 译图预览的永久删除回收

起草者：dsh（Coordinator, epoch 8）· 2026-10-19 · HEAD：`942aa32f3` · **本文件是草案：未创建正式 Task、未申请豁免、未改产品代码**

---

## 一、问题（R6 FAIL / R7 独立复现，均未解决）

**译图预览在永久删除后不被回收，且 GC 也不认它。**

`P09-AC3-DELETE-HARDEN-1` 的 AC4 判定：**FAIL**。

---

## 二、根因（两行 key，永不相等）

| 侧 | 代码 | key |
|---|---|---|
| **发布** | `render_preview.py:69` — `resource_id = f"preview-{uuid.uuid4().hex}"` | **`preview-<32 位随机>`** |
| **清理** | `library.py:1124` — `res_id = f"page-original-{pid}"` | **`page-original-<page_id>`** |

**`catalog.lookup(res_id)` 返回 `None`** → 跳过 → **文件与 catalog 行都留下**，**且 `retired=0`**（GC 只处理 `retired=1`）。

**流程本身是接好的**：`handle_permanently_delete_book`（`core_service.py:1107`）**确实调用了 `cleanup_book_files` 并传了 `render_previews`**（L1143-1147）。**缺陷在 key，不在连接。**

---

## 三、量化（实测，非估算）

用真实 `GetReaderProjection` 驱动：

```
initial:        0 publish-style rows, 1 file
after 5 reads:  5 publish-style rows, 7 files
rows per read = 1.00
```

**R7 独立复现**：**读取 5 次后永久删除，仍有 5 条预览行 + 5 个预览 PNG。**

**结论**：**每次译图阅读泄漏 1 行 + 1 文件，永不回收。**

---

## 四、代码注释自己记录了缺陷的一半

`core_service.py:1968-1976`：

> 「**AC4 (N-003)**: publish WITH an origin so the preview lands in `preview_lifecycle` and **can be reclaimed by reference**. ... **the permanent delete could not find any of them because cleanup only knows the deterministic `page-original` key.**」

**它同时写下了「已做」和「未做」**，**而结论句读起来像已完成**。

**这是本问题存活多轮复审的原因**：**测试断言行存在，注释说可以被回收，两者互相印证 —— 而端到端从未成立。**

---

## 五、两版修复方案**均已被否**（继任者不必重走）

### 方案 A（第一版）：清理侧按 `artifact_id` 反查

**做法**：给 `ResourceCatalogStore` 加只读方法 `preview_lifecycle_rows_for_artifact(artifact_id)`，在 `cleanup_book_files` 里由 `page_id` → `media_artifacts.artifact_id` → lifecycle 行。

**被否原因（两条，独立）**：

1. **`retired` 无法区分「在用」与「遗留」** —— `rendering/service.py:170-182` **复用已存在的 artifact**，**所以同一 `artifact_id` 会随每次 publish 累积新行**；**而 `retired` 只由 `revoke_resource_retiring_preview`（rerender 轮换路径）置 1**，**reader 路径的行永远停在 0**。**全删会把 WebView 仍持有的那一行也删掉。**
2. **R7 指出时序缺陷**：**生产流程先 `execute_permanent_delete_db`（`core_service.py:1139`）删掉 `media_artifacts` 行，之后才 `cleanup_book_files`（L1143）** —— **反查时映射已经不存在。**

### 方案 B（第二版）：映射前置快照

**做法**：**在 `execute_permanent_delete_db` 之前**把「本次要清理的 preview 行」快照下来，**再删 DB，最后按快照清文件**。

**状态**：**未实施。它解决了时序，但没有解决「哪一行在用」。**

**R7 的推荐正是这个方向**，**但它同时要求「明确永久删除时 grant、在途读取及旧 WebView 引用的失效规则」** —— **那一部分尚无答案。**

---

## 六、核心设计问题（**本 Task 的第一个交付物**）

> **如何判定某个 `preview_lifecycle` 行「仍在使用」？**

**已排查、均不可用**：

| 候选 | 为何不行 |
|---|---|
| `artifact_revision_id` 匹配 | **R7 实测：5 条残留行具有相同的 `artifact_id` 与 `artifact_revision_id`** |
| `retired` 标志 | **reader 路径从不置 1** |
| `producer_root` / `managed_rel_path` | 只描述位置，不描述引用 |
| 表内时间戳 | **该表没有时间戳列**（无法表达「保留最新」）|
| ResourceChannel 的 grant 表 | **可能提供按 key 的临时授权，但 `cleanup_book_files` 未使用它，也没有生命周期关联** |
| WebView 当前引用 | **不传给清理路径** |

**R7 的结论**（我同意）：**「grant 或 WebView 当前引用目前不能证明哪个 lifecycle row 是唯一 live row。」**

---

## 七、候选方向（需设计决策，不是实现细节）

| 方向 | 做法 | 代价 / 风险 |
|---|---|---|
| **① 保留每 artifact 最新一行** | 需要**新增可排序字段**（表无时间戳）→ **Schema 变更** | 中等；**但「最新」是否等于「在用」需论证** |
| **② 让 reader 走轮换语义** | **每次投影新 publish 时退休上一个**（复用 `rotate_render_preview` 模式）| **语义最干净**；**但改动 reader 路径，且需处理并发投影** |
| **③ 引用计数** | WebView 持有/释放时上报 | 改动最大；**但能真正回答「在用」** |
| **④ 永久删除时全删 + 前端失效容忍** | 接受「删除后旧引用失效」 | **最简单**；**但需确认「已加载成 Blob 的图片是否需要继续保留」** —— **R7 明确说现有证据不足以断言** |

**方向 ② 值得优先评估** —— **它复用本 Task 已验证过的轮换机制**，**且把「什么算在用」变成「谁持有最新引用」这个已有答案**。

**⚠️ 方向 ④ 不能默认采用** —— **它把一个可见的产品行为（已打开的预览）当作可牺牲项**，**必须先有产品裁决**。

---

## 八、验收方向

- **AC1**：**「读多次后永久删除」残留归零** —— 复用 `ac4-leak-count-probe.py` 改为**断言**（**修前必须先跑出红**）
- **AC2**：**删除后仍被前端引用的预览**按所选方向的规则处理，**行为有明确断言**
- **AC3**：**跨页 / 跨书隔离** —— 删 A 书不得影响 B 书同页预览
- **AC4**：**`page-original-{pid}` 的既有确定性条目仍被回收**（**防回退**）—— 实测它**确实存在且能被找到**
- **AC5**：**不回归** `P09-AC3-DELETE-HARDEN-1` 的 9 个探针
- **AC6**：若需 Schema 变更，**先冻结契约**再实现

---

## 九、建议

**若用户选 B/C**：**正式创建本 Task**，**第一个交付物是第六节的答案（或在文档中明确「采用方向 ② 并论证其满足 AC2」）**，**而不是补丁**。

**若用户选 A**：**按方案 B（映射前置快照）+ 方向 ②（reader 轮换）组合设计**，**但需先确认方向 ② 不会破坏 `rotate_render_preview` 已验证的轮换行为**（那 6 个 Rust 测试覆盖了它）。

---

## 十、边界声明

**只读草案**：未创建正式 Task、未改产品代码、未申请豁免、未改指针。写入 `verification/P20-CLOSE-BOUND-HARDEN-2/`。
