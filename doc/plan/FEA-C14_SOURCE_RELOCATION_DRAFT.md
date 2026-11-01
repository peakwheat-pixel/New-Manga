# FEA-C14 Source 重定位 / 同步 / 容器页映射 / 缓存边界 · 草案

状态：**FROZEN v3 / 冻结于 2026-11-01（[冻结记录](FEA-CONTRACT-FROZEN-C14.md)）**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[FEA-00 方案 r4 §13.2](../design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md) `:768`（D05 行）、`:419`–`:422`（源表）、`:432`（导入/重定位 journal）、`:459`（文件夹同步）、`:461`（改名/移动 vs 换引用）；[C-01b](FEA-C01b_STORAGE_CONTRACT_DRAFT.md)（已冻结，SC-02/SC-03/SC-20/SC-21/SC-22/SC-25/SC-29/SC-31）；[C-06](FEA-C06_SOURCE_AUTH_DRAFT.md)（已冻结）；[C-04b](FEA-C04b_DELETE_PROTOCOL_DRAFT.md)（已冻结）

**边界声明**：本文件只定义契约条款，不改代码、不改任何已冻结契约的字节。

---

## 0. 覆盖矩阵（D05 → 已有 → 缺失 → 本契约条款）

`G-CONTRACT` 关闭要求 D05 五项「必须冻结」**全部**有承载。逐项：

| # | D05 必须冻结 | 已有承载（已冻结） | 缺失 | 本契约 |
|---|---|---|---|---|
| 1 | 持久身份与授权分离 | **C-06**（`identityFacts` + `grant`） | — | 引用 |
| 2 | scope / version / lease | **C-06**（grant `scope`）+ **C-01b**（SC-25/29/31 lease） | — | 引用 |
| 3 | **重定位 / 同步**（正文 §2） | **部分**：C-01b **SC-34**（operation journal + receipt、崩溃恢复先核对 OS 事实）、**SC-26**（Dirty→扫描→diff→预览→事务发布新绑定）、**SC-27**（缺失页 tombstone 不连带删除；变化页新建 binding generation） | **relink/repoint 区分、范围选择、sync plan 字段、可执行判据** | **SC-S01…SC-S08**（引用上述三条，只补增量） |
| 4 | **容器页映射**（正文 §1） | **无**（C-06 只到 entry 授权） | 全部 | **SC-S09…SC-S13** |
| 5 | 缓存边界 / 资源上限（正文 §3） | 部分（见 §0.1） | 淘汰策略 / 持久化 / 全局上限 | **SC-S14…SC-S17** |

### 0.1 第 5 项的已承载子面（逐条证明，不复写）

| 子面 | 承载条款 | 冻结状态 |
|---|---|---|
| 单次读取预算（字节/解码尺寸，超限拒绝不截断） | C-06 `:64` 第 7 条 `budget{maxBytes,maxDecodeBytes}` | 已冻结 |
| 可再生产物 + cache key（`SourceVersion`/entry/decoder/参数） | C-01b **SC-02** | 已冻结 |
| 缓存 vs 非缓存边界（处理结果/人工版本/恢复文件不得按缓存清理） | C-01b **SC-03** | 已冻结 |
| 两通道隔离（`user-source` 不得进 derived-cache grant） | C-01b **SC-20** + C-06 `:65` | 已冻结 |

**本契约只补三个缺口**：淘汰策略、持久化、全局资源上限。**不复写**上表四项，避免双权威。

---

## 1. 容器页映射（D05 第 4 项）

### SC-S09 locator ≠ 身份

- **`locator`**（PDF 页码、ZIP 成员名、目录内相对路径）是**位置**，不是**身份**；
- **身份** = `EntryId`（`source_entries`），由 **`SourceId` + 稳定排序键**（内容指纹用于区分「同名不同内容」）共同确定；**`SourceVersionId` 是内容版本，不参与身份**——否则改名/移动产生新版本后身份会漂移，与本条「改名后 `EntryId` 不变」及 SC-S01/SC-S12 矛盾；
- **行键** = (`SourceVersionId`, `EntryId`)——同一身份在不同内容版本下是不同行；
- **跨版本时的身份保续**：稳定排序键只在**单个 `SourceVersion` 内**稳定；跨版本重排（如插入一页导致后续页码平移）时，`EntryId` 的保续依据是**内容指纹匹配**（`encoded/pixel digest`），不是排序键。匹配不上的成员按 SC-S12 的「新增/缺失」处理。
- 同一文件被改名/移动后 `locator` 变、`EntryId` **不变**；同名不同内容的两个条目 `locator` 相同、`EntryId` **不同**。

**验证**：改名 ZIP 内成员 → 断言 `EntryId` 不变、`locator` 变；同目录两份同名文件 → 断言两个不同 `EntryId`。

### SC-S10 容器页与 Page 的绑定

- 容器的一个成员（PDF 页 / ZIP 成员）↔ 一个 `EntryId`；一个 `EntryId` 可被**多个** `PageId` 引用（不同项目），但**同一项目内** `PageId ↔ EntryId` 在一个 `PageBindingVersion` 内是 1:1（方案 `:420`）；
- `page_bindings` 必须携带 `{PageId, PageBindingVersionId, SourceId, EntryId, acceptedSourceVersion, status, previousBinding}`；
- `status` 取值：`healthy` / `needs_confirmation` / `missing` / `superseded`。

**验证**：建两个项目引用同一 ZIP 的同一成员 → 断言两个独立 `PageId`、共享一个 `EntryId`；同项目内重复绑定同一成员 → 拒绝。

### SC-S11 稳定排序键

- 容器成员的排序必须用**稳定排序键**（`source_entries` 列），不得用 `locator` 字符串排序（PDF 页码 "10" < "2" 的字典序陷阱、ZIP 成员无天然顺序）；
- 排序键在 `SourceVersion` 内唯一且稳定；`SourceVersion` 变化时可重排，但**已绑定的 `PageId` 顺序不因重排而变**。

**验证**：构造 1…12 页 PDF → 断言排序为 1,2,…,12 而非 1,10,11,12,2,…。

### SC-S12 容器内容变更的健康判定

- 容器内容变化（成员增删改）→ 受影响 `page_bindings` 置 `needs_confirmation`，**不得**只改路径就标 `healthy`（方案 `:461` 明文）；
- 判定依据：`SourceVersion` 的 `encoded/pixel digest` 与成员集合 diff；
- 未变的成员：保留 `PageId`/人工版本/进度；新增成员：新建 `PageId`；缺失成员：保留 `tombstone` + `status=missing`，**不连带删除**人工修改（方案 `:459`）。

**验证**：替换 ZIP 内一个成员 → 断言该页 `needs_confirmation`、其余页 `healthy`、无自动删除。

### SC-S13 原文件缺失

- 原文件不在且无备份 → 旧版本原图不可用，但**索引、人工版本、区域、进度保留**（`status=missing`）；
- 恢复路径见 **SC-S01/SC-S02**（relink/repoint 入口与范围选择）。

**验证**：移走源文件 → 断言 `status=missing`、人工数据完整。

---

## 2. 重定位与同步（D05 第 3 项）

### SC-S01 三种操作严格区分

方案 `:461` 明文：**「找同一个文件」与「把项目改为引用另一个文件」是两种操作**。

| 操作 | 语义 | `EntryId` | `acceptedSourceVersion` |
|---|---|---|---|
| **relink**（重定位） | 文件被改名/移动，仍是同一个文件 | **不变** | 不变/更新为该文件的当前版本 |
| **repoint**（改引用） | 项目改指向**另一个**文件 | **变** | 变 |
| **resync**（同步） | 同一容器的内容变化后重新对齐 | 逐成员判定 | 逐成员更新 |

**验证**：对同一操作入口，relink 与 repoint 必须走不同命令/不同确认文案；断言 relink 后 `EntryId` 不变、repoint 后 `EntryId` 变。

### SC-S02 重定位预览与范围选择

- 重定位**先预览**：展示受影响项目数、受影响页数、是否共享引用；
- 共享引用时用户选「**仅当前项目**」或「**全部引用**」（方案 `:461`）；
- 「仅当前」只为本项目建必要 binding，**不得更改其他项目的 `acceptedSourceVersion`**；其他项目继续指向旧版本并显示「需确认」。

**验证**：两个项目共享一源 → 选「仅当前」重定位 → 断言另一项目的 binding 与 `acceptedSourceVersion` 未变。

### SC-S03 重定位不改变身份

- relink 成功后 `EntryId`、`PageId`、人工版本、区域、进度**全部保留**；
- 仅当**内容指纹**也变化时才升级为 `needs_confirmation`（此时等同 resync 路径）。

**验证**：改名后 relink → 断言人工修改与进度逐项相等。

### SC-S04 失败与回滚

- **引用 C-01b SC-34**（operation journal + receipt；崩溃恢复先核对 OS 事实再决定是否重发）——本契约**不重写**其语义；
- 本契约只补 relink/repoint 两类操作各自的步骤序列与幂等键：`source_operations` 记录 `{operationId, kind: relink|repoint|resync, 步骤, receipt, 状态, 失败/重试原因}`（方案 `:422`）；
- 任一步失败 → 保留 operation receipt；**未达双方确认的 binding 不可读取**（方案 `:432`）；
- 重试**同一 `operationId`** 必须幂等，不得产生第二个 binding。

**验证**：注入 Host 确认失败 → 断言 binding 不可读、receipt 存在、重试同一 operationId 只产生一个 binding。

### SC-S05 同步的 diff 预览

- **引用 C-01b SC-26**（Dirty→扫描→diff→用户预览→事务发布新绑定）——本契约不重写，只补 sync 特有的可执行判据：
- 文件夹/容器变更后**先列 diff**（数量 + 明细），用户确认后才同步（方案 `:459`）；
- diff 必须包含：新增、缺失、内容变化三类，各自计数与明细；
- **确认与应用之间再变更 → 拒绝**（`source_sync_plans` 的 `digest` 校验，方案 `:421`）。

**验证**：预览后修改源 → 应用 → 断言拒绝并返回「预览已过期」。

### SC-S06 source_sync_plans 字段

`{planId, baseVersions, baseGeneration, diff{added,removed,changed}, mapping, userDecisions, digest}`（方案 `:421`）：

- `digest` 覆盖 `diff` + `mapping` + `baseVersions`，用 canonical JSON + sha256；
- `userDecisions` 记录用户在预览里做的逐项选择（哪些新页要建、哪些缺失页保留 tombstone）。

**验证**：改 plan 的 `mapping` 一个字符 → 断言 digest 变化、应用被拒。

### SC-S07 同步不连带删除人工成果

- **引用 C-01b SC-27**（缺失页 tombstone；变化页新建 binding generation）——本契约不重写，只补 resync 下的具体操作序列：
- 缺失页：保留 tombstone + 人工修改 + 问题标记，**不连带删除**（方案 `:459`）；
- 变化页：建立**新的 binding generation**，旧区域只留在**旧内容 lineage**；手动确认迁移的区域也须**新建 revision**（不得原地改旧 revision）。

**验证**：删掉源里一页 → 断言该页人工修改仍在、`status=missing`、未产生删除副作用。

### SC-S08 与 C-04b 删除 preflight 的接口

- **本契约不扩展 C-04b 的协议形状**。C-04b 冻结的预检出参 `DeletePreviewItem`（`:43`）是 `{bookId, title, protection{...}, contentSummary{...}, sharedFileRefs[]}`，**没有** pending operation 字段。因此：
  - **需求声明（不含协议改动）**：若存在未完成的 relink/resync，删除 preflight 应向用户披露；该字段的加入属 **C-04b 的 UNFREEZE 或 M2-C1 §5.11.2 的独立字节修订 Task**（照 C-08 块② 模式），不由本契约规定；
  - **唯一来源不变量（可判定形式）**：删除后，每条 `page_bindings` 记录要么仍能解析到存在的 `SourceEntry`/`SourceVersion`，要么被显式置为 `status=missing`；**不得**出现「binding 存在但指向已删除源」的悬空状态。主依据 **C-04b `:72`** 的关系图预检（`BOOK_DELETE_CONFLICT`）+ **ADJ-001 PD-08**（共享引用）；本契约只声明该不变量，**不改其协议字节**。

**验证**：有 pending operation 时发起删除预览 → 断言清单含该 operation。

---

## 3. 缓存边界（D05 第 5 项的缺失子面）

### SC-S14 淘汰策略

- 淘汰只针对**可再生产物**（C-01b SC-02 定义的范围）；**不得**清理 SC-03 列出的非缓存；
- 触发条件（按优先级）：① 全局上限触顶（SC-S16）；② 单文件超限；③ 会话结束的可选清理；
- 清理顺序：**最近最少使用（LRU）优先**；同 last-use 时**先清大文件**（回收效率）；
- **正在被读取/解码的产物不得淘汰**（引用计数 > 0 跳过）；
- **不得**在删除 preflight 进行中淘汰被列为「将删除」的产物（避免清单不一致）。

**验证**：触顶 → 断言 LRU 先清；**同 last-use 时大文件先清**；被引用产物跳过；preflight 期间不淘汰。

### SC-S15 持久化

- 缓存**可跨会话保留**，但**必须可随时全量丢弃并重建**（不承载任何唯一数据）；
- 位置必须在**受管根**内（C-01b **SC-03** 的清理前缀白名单，`cleanup.py:41`），不得写用户源目录；
- 进程崩溃后缓存可能不完整 → **读取时必须校验**（cache key + 尺寸/digest），校验失败视为未命中并重建，**不得**返回损坏内容。

**验证**：杀掉进程 → 重启 → 断言读到的缓存全部通过校验或全部重建；写用户源目录的尝试被拒。

### SC-S16 全局资源上限

- **总缓存字节上限**：可配置，且进程内**强制**（超限即按 SC-S14 淘汰，不等待）；
- **并发解码数上限**：可配置；超限排队，**不得**静默丢弃请求；
- **单次读取预算**（C-06 `:64`）与全局上限是**两层**：单次超限立即拒绝，全局触顶触发淘汰；
- 上限值本身是**配置项**（可调），但「必须有上限」是**契约条款**（不可配置关闭）。

**验证**：把总上限调到极小 → 断言持续淘汰且不 OOM；并发超限 → 断言排队而非丢弃。

### SC-S17 与 C-06 通道隔离的边界

- 源读取（`user-source`）与 derived 缓存是**两条通道**（C-01b SC-20 / C-06 `:65`）：本契约的缓存规则**只作用于 derived**，不影响源读取路径；
- `user-source` 的读取**不缓存到 derived 前缀**；derived 产物**不得**被当作源证据引用。

**验证**：读源文件 → 断言 derived 前缀无新增；断言 derived 文件不作为 `SourceVersion` 的来源证据。

---

## 4. 与已冻结契约的接口

| 契约 | 接口 |
|---|---|
| **C-01b**（已冻） | **注意**：C-01b **未冻结** `source_entries`/`page_bindings`/`source_sync_plans`/`source_operations` 的表结构（AD-003 `:117` 明文「这些表均未定，由 DSH 在 D05 范围冻结」）→ **表结构留给后续存储契约，本契约只定义语义与不变量，不定义 DDL**。本契约引用的 C-01b 条款：**SC-02/SC-03/SC-20**（缓存）、**SC-26/SC-27/SC-34**（同步/缺失/operation journal）、**SC-21/SC-22**（授权面，**非**表结构） |
| **C-06**（已冻） | C-06 的 `scope.entry` 语义是「**可解析到授权根内路径的定位键**」（`:52`）；本契约的 `EntryId` 经 `source_entries.locator` 解析后可与之对应——**对齐规则须在 C-06 侧或协议实现 Task 中确认，本契约不单方面重定义已冻结字段**；per-request 预算与全局上限是两层（SC-S16） |
| **C-04b**（已冻） | pending operation 披露只是**需求声明**（SC-S08）；其字节修订属 C-04b 的 **UNFREEZE / M2-C1 §5.11.2 独立 Task**，**本契约不改 C-04b 字节**；唯一来源不变量由 ADJ-001 PD-08 + C-04b `:72` 承载 |
| **C-08**（已冻） | Run 快照的 `PreparedRun` 与本契约的同步预览是**不同层**（Run 层 vs 源层），不互相替代 |

## 5. 冻结条件

1. 独立复核通过（上下文独立）；
2. C-01b、C-06、C-04b、C-08 均已冻结（**✅ 2026-11-01 全部满足**）；
3. 覆盖矩阵与 C-06 冻结记录的「D05 授权面子集」表述**无冲突**；
4. `check.ps1` PASS；`verify_pins.ps1` 对 C-14 当前为 `MISSING-RECORD (not yet frozen; skipped)`（**未冻结不该 PASS**），冻结记录建立后须转为实际校验（已纳入清单）；
5. 冻结记录须含 §1A（pin 口径）与 §1B（冻结字节 vs 复核字节）。

**注**：`verify_pins.ps1` 是机械校验，**不能替代**最终字节的独立复核——两者都要。

## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | **v3（处置 FEA-C14-r2 的 K-1…K-3）**：K-1 §4 的 C-04b 行明确「需求声明 + 字节修订属 UNFREEZE/独立 Task」；K-2 SC-S08 的「唯一来源」改为可判定形式（binding 要么可解析、要么显式 missing）；K-3 SC-S09 补「跨版本身份保续靠内容指纹、排序键仅单版本内稳定」 | DSH |
| 2026-11-01 | **v2（处置 FEA-C14-r1 的 P1×5 + P2×4）**：P1-1 §4 改正「C-01b 未冻结四张表」（AD-003 `:117`）；P1-2 §0 行 3 补 C-01b SC-26/27/34 + SC-S04/S05/S07 改引用不复写；P1-3 SC-S08 改为「需求声明 + 属 C-04b UNFREEZE/独立字节修订」并改正引用为 ADJ-001 PD-08 + C-04b `:72`；P1-4 C-06 `scope.entry` 改为「对齐规则待协议层确认」；P1-5 身份公式改为 `SourceId`+稳定排序键（`SourceVersionId` 不参与身份）+ 行键 (`SourceVersionId`,`EntryId`)；P2-1…P2-4 措辞/引用/编号 | DSH |
| 2026-11-01 | 建立草案：覆盖矩阵（D05 五项 + 第 5 项逐条证明）、SC-S01…SC-S17（重定位/同步 8 条、容器页映射 5 条、缓存边界 4 条）、四契约接口、冻结条件 | DSH |
