# Gate 关闭裁定 · `G-CONTRACT`（单 Gate）

状态：**ACTIVE / DSH 裁定**
裁定人：DSH（Lead / Architect / Integrator）
日期：2026-11-01
依据：[FEA-GATE-READINESS-review](../reviews/FEA-GATE-READINESS-review.md)（独立复核，判定 `G-CONTRACT` **✅ 满足**、`G-DELETE-CONTRACT` **❌ 不满足**）+ 用户 2026-11-01 裁决「先关闭 `G-CONTRACT`，`G-DELETE-CONTRACT` 保持 OPEN；B 列为下一阶段」

---

## 1. 裁定

| Gate | 定义（原文） | 原状态 | **裁定后** |
|---|---|---|---|
| **`G-CONTRACT`** | 「D05 Source/grant/资源契约冻结」（[AD-003 §5](../AD-003_REFERENCED_SOURCE_ARCHITECTURE.md)） | OPEN | **✅ CLOSED（2026-11-01）** |
| **`G-DELETE-CONTRACT`** | 「协议字段/码表/**D04-D07** 冻结」（[ADJ-001 §9](../contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md)） | OPEN | **❌ 保持 OPEN**（理由见 §4） |

## 2. `G-CONTRACT` 关闭的依据（逐条）

D05 五项「必须冻结」（FEA-00 §13.2 `:768`）全部有冻结契约承载：

| # | D05 项 | 承载 | 冻结记录 |
|---|---|---|---|
| 1 | 持久身份与授权分离 | C-06（`identityFacts` + `grant`） | [C06](FEA-CONTRACT-FROZEN-C06.md) |
| 2 | scope / version / lease | C-06 grant `scope` + C-01b SC-25/29/31 | [C06](FEA-CONTRACT-FROZEN-C06.md)、[C01b](FEA-CONTRACT-FROZEN-C01b.md) |
| 3 | 重定位 / 同步 | **C-14 SC-S01…S08** | [C14](FEA-CONTRACT-FROZEN-C14.md) |
| 4 | 容器页映射 | **C-14 SC-S09…S13** | [C14](FEA-CONTRACT-FROZEN-C14.md) |
| 5 | 缓存边界 / 资源上限 | C-06 `:64`（per-request 预算）+ C-01b SC-02/03/20 + **C-14 SC-S14…S17**（淘汰/持久化/全局上限） | 三份记录 |

独立复核结论：**§0.1 四条「已承载」逐行实核全部为真**，C-14 的三个缓存缺口写清。

## 3. 关闭的三个边界（用户 2026-11-01 明确要求）

### 3.1 C-09 继续 blocked

`G-CONTRACT` 关闭**不解除** C-09 的任何条件。C-09 §4 条件③要求「`G-DELETE-CONTRACT` 关闭 **+** `G-CONTRACT` 关闭」——后者现已满足，前者**仍不满足** → **C-09 仍不可冻**。

### 3.2 只解除 `G-CONTRACT` 这一项阻塞，不代表 Source 线任务全部可启动

| 任务 | 原阻塞 | 现在 |
|---|---|---|
| FEA-09 / FEA-11 | `G-CONTRACT: OPEN` | **解除该阻塞**（仍需按各自依赖逐项检查） |
| **FEA-12** | `G-CONTRACT` **与** `G-DELETE-CONTRACT` **双重** | **仍受 `G-DELETE-CONTRACT` 阻塞** → **不可启动** |
| FEA-08 | 待 DSH 冻结范围 | 不变 |
| 其他（FEA-13 等） | 各自依赖 | **逐项检查**，不得据本裁定推断已解锁 |

依据：方案 `:939`「FEA-09/11 受 `G-CONTRACT: OPEN` 阻塞，**FEA-12 同时受 `G-CONTRACT` 与 `G-DELETE-CONTRACT` 阻塞**」。

### 3.3 DDL 尚未冻结——不能把「语义覆盖完成」写成「存储结构已冻结」

AD-003 `:117` 承诺「`source_entries`/`page_bindings`/`source_sync_plans`/`source_operations` 的表名、索引、外键、约束与迁移版本**由 DSH 在 D05 范围冻结**」，而 **C-14 只定义了语义与不变量，未定义 DDL**（C-14 冻结记录 §5 L-1）。

**因此**：
- `G-CONTRACT` 的关闭**只代表 D05 的「契约语义」覆盖完成**；
- **四张表的 DDL 仍属未冻结项**，是 Source 线**任何生产实现**的前置；
- 承载方式与时点：由 Source 线实现前的**存储契约**（C-01b 扩展或新契约）承担，须在释放对应实现 Task 前完成并复核；
- 本边界写入 C-14 冻结记录 §5 L-1 与本裁定的 Gate 记账。

## 4. `G-DELETE-CONTRACT` 保持 OPEN 的理由

| 包 | 状态 | 缺口 |
|---|---|---|
| D04 草稿/保护 | ✅ 满足（C-13） | — |
| D05 Source | ✅ 满足（C-06 + C-14 + C-01b） | — |
| **D06** Run 快照 | ❌ | **4 项无条款**：控制 pending 状态 / 真实完成口径 / retry 是否复用 source run 快照 / 断线 receipt |
| **D07** 删除/备份/迁移 | ❌ | 多项未冻：三路径统一 ProtectionPolicy、备份覆盖清单（settings/catalog 归属）、`backup/2`、旧包 legacy adapter、自动备份调度归属、软删/恢复命令面 |
| **循环** | ❌ | D07 剩余项由 **C-09** 承载，而 **C-09 条件③要求两 Gate 关闭** → 死锁，须先解环 |

**下一阶段（B）**：解 D07/C-09 循环 + 补 D06 四项 → 已建文档 Task（见 §6）。

## 5. 不构成什么

- **不构成** `G-DELETE-CONTRACT` 的关闭或部分关闭。
- **不构成** C-09 的可冻授权。
- **不构成**任何实现 Task 的释放授权（实现仍须 C-11 选候选 → 建 Task → 独立 Review）。
- **不构成** DDL 已冻结。
- **不构成**远端 push 授权。

## 6. 后续 Task

| Task | 范围 |
|---|---|
| [FEA-D06-GAP](TASKS-D06-D07.md#fea-d06-gap) | 补 D06 四项（C-08 UNFREEZE 或新增条款 + 独立复核） |
| [FEA-D07-UNBLOCK](TASKS-D06-D07.md#fea-d07-unblock) | 解 D07/C-09 循环（三选一方案 + 裁定留痕） |

## 7. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：`G-CONTRACT` 关闭、`G-DELETE-CONTRACT` 保持 OPEN、三个边界、后续 Task | DSH |
