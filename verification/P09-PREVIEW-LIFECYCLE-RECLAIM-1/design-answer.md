# AC4 设计答案：如何判定 `preview_lifecycle` 行「仍在使用」

**Task**：`P09-PREVIEW-LIFECYCLE-RECLAIM-1` · **Owner**：dsh · **日期**：2026-10-19 · **HEAD**：`222fa02c1`
**本文是第一个交付物**（Task 规定：设计答案，不是补丁）

---

## 一、问题

**译图预览在永久删除后不被回收，GC 也不认它。**

- **根因**：`publish` 生成 `preview-{uuid4}`（`render_preview.py:69`），清理查 `page-original-{page_id}`（`library.py:1124`），**永不相等**
- **量化**：**每次译图阅读泄漏 1 个 catalog 行 + 1 个文件**（实测；R7 独立复现：读 5 次后永久删除仍剩 5 行 + 5 PNG）
- **注释自证**：`core_service.py:1968-1976` 写出了该缺陷，**结论却写成「can be reclaimed by reference」**

---

## 二、前两版方案为何失败（不必重走）

| 方案 | 失败原因 |
|---|---|
| **按 `artifact_id` 反查** | ① **`retired` 无法区分在用与遗留**（reader 路径从不置 1）② **R7 指出时序**：`execute_permanent_delete_db`（`core_service.py:1139`）先删 `media_artifacts` 行，L1143 才 `cleanup_book_files`，**反查时映射已不存在** |
| **映射前置快照** | **解决时序，未解决「哪一行在用」** |

---

## 三、本轮三项发现（全部实测，含一项否证）

### 发现 1：预览本来就在可签发 scope 内 ✅

| 项 | 值 | 位置 |
|---|---|---|
| `ALLOWED_SCOPE_CLASSES` | `("derived-read-only", "managed-read-only")` | `dto.py:69` |
| `PREVIEW_ORIGIN_SCOPE` | **`"derived-read-only"`** | `catalog_store.py:128` |

**→ 预览的 scope 在白名单内，`issue` 不会拒绝它。**

### 发现 2：授权机制与量值 ✅

| 常量 | 值 | 位置 |
|---|---|---|
| `DEFAULT_TTL_SECONDS` | **300.0 s（5 分钟）** | `dto.py:29` |
| `MAX_ACTIVE_REFERENCES` | **32**（全局） | `dto.py:22` |
| `MAX_SUBSCRIBERS_PER_RESOURCE` | **16** | `dto.py:26` |

**判据语义**：`active = [e for e in _table.values() if not e.revoked and e.expires_at > now]`
**+ `resolve(renew=True)` 滑动续期** → **「在过去 5 分钟内被请求过，或仍有未释放的 subscriber」** = **「最近在用」**。

### 发现 3（否证）：那份数据在**另一个进程**里 ❌

| 证据 | 内容 |
|---|---|
| `apps/desktop/src-tauri/src/core_bridge.rs:135` | `Command::new(python).arg("infrastructure.resource_channel.host_bridge")` —— **独立进程** |
| `host_bridge.py:60` | `self._service = service or ResourceChannelService()` —— **service 活在该进程内** |
| `service.py:77` | `self._table: dict[str, _Entry] = {}` —— **实例内存** |
| `tests/m2_resource_channel/test_service.py:131` | `restarted = ResourceChannelService()  # fresh process == fresh table` |

**结论**：

> **Core 无法查询 host 签发的 grant —— 不是「没接线」，是「不在同一个地址空间」。**

**这同时解释了 R7 那句话的完整含义**：**「grant 或 WebView 当前引用不能证明哪个 lifecycle row 是唯一 live row」** —— **因为 Core 手上根本没有那份数据。**

**也解释了为什么前两版方案不可能成功**：**它们都在 Core 侧找一个 Core 拿不到的答案。**

---

## 四、三个可行方案

| 方案 | 做法 | 代价 | 契约影响 |
|---|---|---|---|
| **A. Core 侧记录「最后请求时刻」** | Core 在每次发布预览时记录该 `resource_id` 的时间；永久删除时「N 分钟内 → 保留」 | **给 `preview_lifecycle` 加一列时间戳** | **Schema 变更 → 需先冻结契约** |
| **B. host 通过 IPC 通知引用释放** | host 在 `release_subscriber` / revoke 时向 Core 发事件 | **新增 IPC 事件 + 跨进程协议** | **IPC 契约变更 → 需先冻结契约** |
| **C. 全删 + 容忍旧引用失效** | 直接回收全部 `preview-*` | **最简单**；**但已加载的 Blob / 正在显示的页面可能失效** | **方案 C 本身不改变 IPC 契约、不改变数据库列**（见下注）|

**⚠️ 关于方案 C 那一行的「契约影响」——限定（R17 Finding 1 后补）**

**该列描述的是【各方案本身】的契约影响。方案 C 的做法是「直接回收全部 `preview-*`」，它确实不新增持久化状态、不改列、不改 IPC。**

**但最终交付的不是方案 C，而是其修正版 C1** —— **C1 在「全删」之外加入了「删除前快照预览 id」，于是把 `preview_resource_ids` 写入 `targets_json` 并在重试路径读取它，改变了持久化格式的兼容语义**（旧 manifest 无此字段 → `preview_ids_known` 为 False）。

**所以上表方案 C 行的「不改变 IPC 契约、不改变数据库列」【不能读作「本次交付没有契约影响」】。** **AC6 据此裁定为未满足**，见 `ac6-ruling.md`。

### 推荐：**修正为方案 B（原推荐 A 的代价被算少了）**

**理由**：

1. **语义与既有 TTL（300 s）一致** —— **两者可以对齐，不需要发明新的时间语义**
2. **不引入跨进程协议** —— **Core 在 `GetReaderProjection` 时本来就知道自己发布了哪个预览**
3. **判据的偏差方向是安全的** —— **保留不该留的，而不是删掉还在用的**
4. **它的失败模式是可观测的** —— **若时间戳不更新，泄漏只是继续存在（与现状相同），不会变成误删**

**⚠️ 但方案 A 需要的不止一个 Schema 变更 —— 它需要先造一条迁移通道。**（R185 修正，见第八节）

**`preview_lifecycle` 当前没有时间戳列**，而 catalog DB **没有迁移机制**：`catalog_store.py` 只用 `CREATE TABLE IF NOT EXISTS`（对已存在的表不生效），**全文件 `ALTER TABLE` 出现 0 次**，且该文件头部（L11）明确声明 `schema/migrations (out of this Task's allowed paths)`。

**对照**：library DB 有迁移先例（`src/infrastructure/sqlite/schema.py:152` 起大量 `ALTER TABLE ... ADD COLUMN`）。**但那是另一个库。**

**所以方案 A 的实际工作量 = 冻结 Schema 契约 + 建立 catalog DB 的迁移机制 + 加列。****我在本节原先只写了第一项。**

**修正理由（R185）**：方案 A 的代价低估了一层（见上）。**方案 B 的代价则相对确定** —— **Core 与 host 之间已有 IPC 通道**（`core_bridge.rs` 就是这个通道），**加一个事件是既有机上的扩展**，而方案 A 要新建一条迁移通道。

**但这不改变一件事：B 同样需要契约冻结（IPC 契约），所以最终仍由 Codex 裁定。**

### 我为什么不自行选 C

**方案 C 牵涉产品行为**：**「已加载成 Blob 的图片是否必须继续可用」** —— **R7 明确说现有证据不足以断言**。**这不是我能替产品决定的。** **若产品接受「删除后旧引用失效」，C 是成本最低的；若不接受，C 不可用。**

---

## 五、方案 A 的待确认项（实施前必须补）

1. **`preview_lifecycle` 加列的迁移方式** —— **该表是 `CREATE TABLE IF NOT EXISTS`**（`catalog_store.py:76`），**已存在的库如何补列需确认**（`ALTER TABLE ... ADD COLUMN` 或重建）
2. **「最后请求时刻」写在哪一侧** —— **`publish` 时写，还是 `GetReaderProjection` 返回时写**？**前者更简单，后者更准确**（**同一预览可能被多次请求**）
3. **N 取值** —— **对齐 host 的 300 s？还是更长**（**永久删除时用户可能仍在读该书**）？
4. **`cleanup_book_files` 能否拿到「当前时刻」** —— **需要可注入的 clock**（**便于测试，`ResourceChannelService` 已有 `clock` 参数可借鉴**）

---

## 六、本轮未做的事（明确声明）

- **未改任何产品代码**
- **未加任何列**
- **未创建 IPC 事件**
- **未自选方案 C**（**需产品裁决**）

**用户已于 2026-10-19 裁定 C1（允许引用失效）—— 见 `verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/c1-ruling-record.md`。**

---

## 七、边界与证据

**证据来源**：`dto.py` · `service.py` · `catalog_store.py` · `render_preview.py` · `library.py` · `core_service.py` · `host_bridge.py` · `core_bridge.rs` · `test_service.py`

**读取方式**：只读；所有行号均为本次实测。
