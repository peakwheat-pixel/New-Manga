# FEA-C09 删除 / 备份 / 迁移的数据边界（草案）

状态：**DRAFT / 未冻结 / 不释放实现 Task**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md) 的 C-09、[C-01b 存储契约](FEA-C01b_STORAGE_CONTRACT_DRAFT.md)（SC-10a/10b、SC-30/31/33）、[ADJ-001](../contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md)、[AD-003](../AD-003_REFERENCED_SOURCE_ARCHITECTURE.md) §3.3/§3.4、代码现状（`nmbak.py`、`cleanup.py`、`library.py`）

**边界声明**：本文件是**草案**；不改冻结契约、不改代码。

---

## 1. 现状（代码事实）

| 面 | 现状 | 出处 |
|---|---|---|
| 备份打包 | `nmbak.py` 只打包 `library.db` + sidecar + `managed/`；**不含** `settings/*.json`、`catalog.sqlite`；`managed/trash-manifest.json` 被白名单排除（`:660-665`） | C-01b SC-10a/10b 已核 |
| 清理路径 | `cleanup.py:41` **`CACHE_SAFE_PREFIXES = ("cache/",)` 缓存前缀**；`:16-20` 是 docstring（非校验逻辑）；真实受管相对路径校验在 `:73-116` | C-01b SC-03/SC-24 |
| 软删/彻底删除 | `library/service.py:97-99` 软删；`trash.py:119/196` 页级；`library.py:1069-1101` 项目级永久删除 | C-01b SC-30 已核 |
| 数据根迁移 | 有迁移入口（历史 Task 已做幂等空操作验证） | SAFETY-6 AC3（MA-11 待裁决） |
| 回收站桥 | **无**（AD-003 §4 已记） | 依据：AD-003 §3.7 / ADJ-001 §3 流程 C（PD-06 = 失败回滚，不是回收站桥的依据） |

## 2. 契约条款（冻结候选）

### SC-B01 备份覆盖清单

- **必须包含**（默认）：`library.db`、sidecar、`managed/`（含 `trash-manifest.json`，**需扩白名单**）、**源引用与授权元数据**（AD-003 §3.3；Host 私有 registry 随备份纳入，备份包内加密）。
- **默认不包含**：外部原文件、`settings/*.json`（凭据）、`catalog.sqlite`（缓存，可重建）。
- **扩展点**：`nmbak` 白名单改为**显式清单**（每项一个条目 + 版本号），新增项须走独立 Task。

**SC-B01a 完整归属表**（D07 声明范围「备份覆盖清单含 settings/catalog 归属」的承载；解决 FEA-00 `:901` 的「catalog 归属待 D07 冻结」）：

| 项 | 是否入包 | 归属/理由 |
|---|---|---|
| `library.db` | **是** | 主数据 |
| sidecar（`.nmbak` 附属） | **是** | 校验与元数据 |
| `managed/`（含 `trash-manifest.json`） | **是**（需扩白名单） | 派生产物中不可重建者 |
| 源引用与授权元数据 | **是**（包内加密） | AD-003 §3.3；Host 私有 registry |
| `derived/`（缓存） | **否** | 可再生产物（C-01b SC-02） |
| `catalog.sqlite` | **否** | **派生索引，可从 `library.db` 重建**——本条即解决 `:901` 的「待 D07 冻结」：**判定为不纳入**，理由是「可重建」而非「缓存」 |
| `settings/*.json` | **否（凭据）**，但**非凭据类设置**（外观/语言/布局偏好）**纳入** | 拆分凭据类与非凭据类；C-03 的外观设置属非凭据类 → 入包 |
| 外部原文件 | **否** | 引用模型，从不复制 |

**验证**：构造含全部项的库 → 导出备份 → 断言包内容与上表一致；断言 `settings/credentials*` 缺失、`settings/appearance*.json` 存在。


### SC-B02 备份恢复的完整性

- 恢复前校验：备份包的 manifest 完整性（文件数/字节/hash）+ Schema 版本兼容。
- **恢复冲突语义**（AD-003 §3.3）：默认**逐项 Defer**（不整库覆盖）；`UseBackup` 前必须先存受保护版本；冲突项需用户逐项确认。
- 不兼容 Schema → 拒绝恢复（`BACKUP_SCHEMA_INCOMPATIBLE`），**不**尝试自动降级。


### SC-B03 数据根迁移

- 迁移 = **复制到新根 → 校验 → 切换指针**；旧根**保留只读**（不删除）。
- 迁移 journal 记录「源根/目标根/开始时间/阶段/结果」+ **`DatabaseId`**（C-01b SC-18；回填前 identity 为 unknown）；崩溃后可从 journal 恢复。
- **独占维护锁 + staging + 校验 + commit marker**（C-01b SC-17）：迁移期间禁止其他写入；staging 完成后校验（文件数/字节/hash）；commit marker 落库后才切换指针。
- **不得**部分迁移后切换（原子性）。


### SC-B04 删除的三层边界

| 层 | 触达 | 依据 |
|---|---|---|
| **软删**（应用回收站） | 只置 `deleted_at`；不触文件 | ADJ-001 |
| **自动清理** | 只清可再生产物（derived/cache），不清人工修改/revision | ADJ-001 §3 |
| **显式彻底删除** | DB 行 + 清单内 managed 文件；**永不**触原文件 | ADJ-001 PD-02、C-04b |

**SC-B04a 三路径统一 `ProtectionPolicy`**（D07 声明范围「三路径统一 ProtectionPolicy」的承载）：

三条路径**共用同一判定函数** `ProtectionPolicy(scope) -> {blocked, reasons[]}`，不得各自实现：

| 保护来源 | 软删 | 自动清理 | 显式彻底删除 |
|---|---|---|---|
| `region_locked` / `translation_locked` / `inpaint_locked` | 不阻止（不触文件） | **阻止**（不清人工成果） | **阻止**（须先列清单并经 PD-01 披露） |
| 人工 revision / 当前 revision | 不阻止 | **阻止** | **阻止**（含在 `protection` 披露） |
| 活动草稿（C-13 `status=active`） | 不阻止 | **阻止** | **阻止**（`draftPageCount`） |
| 共享引用（ADJ-001 PD-08） | 不阻止 | 不阻止 | **阻止**（`BOOK_DELETE_CONFLICT`） |

**验证**：三条路径对同一 scope 调用同一函数 → 断言返回值一致；构造「有锁 + 有草稿」的页 → 断言自动清理被阻止、软删通过、彻底删除需 PD-01 披露。

**不复写**：ADJ-001 的保护**语义**（哪些东西算保护）由 ADJ-001 定义；本条款只定义**三条路径共用同一判定**这一结构要求。


### SC-B05 回收站桥（未实现）

- Windows 回收站桥是 PD-06 的前置；**未实现前**，显式彻底删除不得声称「已移入回收站」。
- 实现须满足 H5（recycle 失败不永久删除；无法保证 → 禁用该类型原件删除）。


### SC-B06 软删 / 恢复 / TrashEntry 命令面（D07 声明范围）

**命令**（与 M2-C1 的 wire 风格一致；具体 payload 字段名 snake_case）：

| 命令 | 方向 | payload | 成功结果 |
|---|---|---|---|
| `MoveToTrash` | Host → Core | `{ entries: TrashEntryRef[1..N], idempotency_key }` | `{ moved: TrashEntryRef[], skipped: {ref, reason}[] }` |
| `RestoreFromTrash` | Host → Core | `{ entries: TrashEntryRef[1..N], idempotency_key }` | `{ restored: TrashEntryRef[], conflicts: {ref, reason}[] }` |
| `ListTrash` | Host → Core | `{ cursor?, limit? }` | `{ items: TrashEntryInfo[], nextCursor? }` |
| `PurgeTrash` | Host → Core | `{ entries: TrashEntryRef[1..N], confirm: true, idempotency_key }` | 委托 C-04b 的永久删除语义 |

**错误码**（本契约新增；须在实现前走 M2-C1 的独立字节修订 Task）：

| code | category | retryable | 含义 |
|---|---|---|---|
| `TRASH_ENTRY_NOT_FOUND` | `validation` | false | 目标条目不在回收站 |
| `TRASH_RESTORE_CONFLICT` | `conflict` | false | 恢复目标路径已被占用（逐项返回，不整批失败） |
| `TRASH_RESTORE_LAYER_MISMATCH` | `conflict` | false | 备份来自不同数据层或 `DatabaseId` 不匹配 |

**不变量**：
- `MoveToTrash` / `RestoreFromTrash` **只改 `deleted_at`/归属**，不触文件（SC-B04 第一层）；
- `PurgeTrash` 必须走 C-04b 的 PD-01 披露 + 专门确认，**不得**绕过；
- 批量操作为**逐项原子**：一项失败不影响其他项，返回 `skipped`/`conflicts`。

**验证**：批量 `MoveToTrash` 含一个不存在的 ref → 断言其余项成功、该项进 `skipped`、无整批回滚；`PurgeTrash` 未带 `confirm: true` → 断言拒绝。

**不复写**：回收站/软删的**语义**在 ADJ-001；本条款只定义**命令面**。


### SC-B07 `backup/2` 格式契约（D07 声明范围）

- **版本标识**：包根 `manifest.json` 的 `format: "nmbak"` + `version: 2`；`backup/1` 为 `version: 1`。
- **`backup/2` 相对 `backup/1` 的强制增量**：① 显式清单（SC-B01 的扩展点已要求）；② 每项 `sha256` + 字节数；③ `DatabaseId`（C-01b SC-18）与 `schemaVersion`；④ 包内加密的源授权元数据段。
- **版本协商**：读取端先读 `version`；`version > 2` → 拒绝（`BACKUP_FORMAT_UNSUPPORTED`）；`version == 1` → **legacy adapter 路径**（只读、不写回）。
- **旧包读取（legacy adapter）**：`backup/1` 只能**读取/恢复**，**不得**就地升级为 `backup/2`（升级须「导出新包 + 校验 + 原子替换」）。
- **写端**：只写 `version: 2`；**不得**写出 `version: 1`。

**验证**：用 `version: 1` 包恢复 → 断言成功且原包字节未变；用 `version: 3` 包 → 断言 `BACKUP_FORMAT_UNSUPPORTED`；写端产物 → 断言 `version: 2`。


### SC-B08 自动备份调度归属（D07 声明范围）

- **归属 Core**：自动备份的**计划与执行**由 Core 的调度器驱动（与 Run 调度同一 owner 约束），Host 只负责触发入口与进度展示；
- **不得**由 Host 独立起定时器（避免双 scheduler，与 C-08 的 Run owner 约束同源）；
- **与手动备份的关系**：手动备份**不**重置自动备份的计时；自动备份**不**覆盖手动备份产生的包（保留策略见下）；
- **保留策略**：自动包保留最近 `N` 份（`N` 可配置，默认待实现实测）；手动包**不自动清理**；
- **失败语义**：自动备份失败**不得**影响主流程，须记录 receipt 并在 UI 提示；连续失败 `K` 次后降级为「仅提示」；
- **与 `DatabaseId` 的关系**：引用 C-01b SC-18，**不复写**；`DatabaseId` 不匹配的自动包不得被恢复流程选中。

**验证**：模拟自动备份失败 → 断言主流程不受影响、receipt 存在；构造 `DatabaseId` 不匹配的包 → 断言恢复列表不展示。


### SC-B09 恢复路径（补 SC-B02 的入口）

- 恢复入口统一走 `RestoreFromBackup`：`{ backupPath, mode: "defer"|"overwrite", conflictPolicy }`；
- `mode="overwrite"` 前**必须**先存受保护版本（SC-B02 已要求）；
- 恢复**不得**跨 `DatabaseId`（`TRASH_RESTORE_LAYER_MISMATCH`）。

**验证**：跨 `DatabaseId` 恢复 → 断言拒绝。

**不复写**：SC-B02 的完整性/冲突语义本条款不重述。

## 3. 与 C-01b / C-04b / C-08 的接口

- **C-01b**：SC-10a/10b（备份清单）、SC-30/31/33（删除边界）、SC-33（迁移）由本草案细化。
- **C-04b**：删除协议是 SC-B04 的协议层落地。
- **C-08**：备份恢复后的 Run 快照必须可读（快照不含上下文页内容——已知缺口）。

## 4. 冻结条件

1. 独立复核通过；
2. C-01b 已冻结；
3. **上游契约已冻结**：C-01b、C-04b、C-06、C-14 均已冻结（本契约显式依赖它们的 source/缓存/删除/授权面）；且 **`G-CONTRACT` 已关闭（2026-11-01）**。**本契约不再要求 `G-DELETE-CONTRACT` 关闭**——本契约正是 D07 的承载者之一；D07 的完整覆盖由「本契约冻结 + C-04b + C-01b 相关条款」共同满足，届时才重新判定 `G-DELETE-CONTRACT`（见 [D07 解环 Task](FEA-D07-UNBLOCK.md)）。**不引入「部分关闭」Gate 状态**。
4. `check.ps1` PASS。

## 5. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | **v3（FEA-D07-UNBLOCK AC2–AC6）**：新增 SC-B06 软删/恢复/TrashEntry 命令面（4 命令 + 3 码）、SC-B07 `backup/2` 格式契约（含 legacy adapter）、SC-B08 自动备份调度归属、SC-B09 恢复入口；SC-B01 补「完整归属表」（解决 FEA-00 `:901` 的 catalog 归属问题）、SC-B04 补「三路径统一 ProtectionPolicy」；§4 条件③改上游契约条件（解环） | DSH |
| 2026-11-01 | 建立草案：现状表 5 项、SC-B01…SC-B05 五条、与三份契约接口、冻结条件 | DSH |
| 2026-11-01 | v2：处置 FEA-GOV-7 r1（P1-2 授权元数据入包 / P1-3 SC-17/18 / P2×4） | DSH |
