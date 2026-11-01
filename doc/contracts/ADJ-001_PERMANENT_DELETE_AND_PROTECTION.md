# ADJ-001 — 永久删除与保护状态裁定

Status: **FROZEN_SEMANTICS / PENDING_IMPLEMENTATION / PROTOCOL_CHANGE_PROPOSED**（rev r2：按 Codex 独立 Review r1 修订，见 §11）
Owner: **DSH**（Lead / Architect / Integrator）· Decision authority: 语义来自**用户 2026-10-31 决定**；契约措辞由 DSH 裁定
Date: 2026-10-31 · 上游：[AD-002](../AD-002_TARGET_DESKTOP_ARCHITECTURE.md)、[AD-003](../AD-003_REFERENCED_SOURCE_ARCHITECTURE.md)
裁定对象：[`M2-C1_TYPED_IPC_CONTRACT.md`](M2-C1_TYPED_IPC_CONTRACT.md) **§5.11（:678–:799）** 单条/批量项目级永久删除
相关：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md`（pin/Lock 语义）· `src/infrastructure/sqlite/library.py`（`:704-847` 预检、`:1069-1101` 事务）· `src/application/maintenance/trash.py`、`cleanup.py`
审查记录：[FEA-00 r1](../reviews/FEA-00-dsh-r1.md) F-02 · [FEA-00 r2 技术复核](../reviews/FEA-00-dsh-r2-technical-recheck.md) · [FEA-00 Codex r1 独立 Review](../reviews/FEA-00-codex-r1.md)（`changes_requested`）· [处置记录](../reviews/FEA-00-codex-r1-adjudication.md)

本文件是**裁定与冻结的语义要求**，不是实现、不是验收、不是 Task 释放。§5 的语义自本文件生效；§6 的协议与代码**均未实现**（`NOT_RUN`），在 D04/D07 契约冻结并实施前，`M2-C1 §5.11` 现行语义继续按原字节生效。

---

## 1. 裁定结论（三句话）

1. **`M2-C1 §5.11.2` 的删除语义保持有效，不推翻**：预检成功后，在单一 SQLite 事务中删除项目内容行**并移除**该项目 Lock / current / pinned Revision；DB 全有/全无；提交后逐本清理，失败标 `cleanup_pending` 并只允许用户显式重试。
2. **用户 2026-10-31 决定 #5 是对现行契约的"增量前置"，不是反向语义**：现行契约已要求用户确认与"预检期间不得单独解锁、解除 pin、改写 current"；本次**新增**的是①受保护内容的**逐项影响清单**，②针对"将被删除的保护"的**专门确认**，③确认与事务之间不得有任何提前变化。
3. **方案此前"受保护即拒绝彻底删除"的主张不再作为推荐**（用户已改选）：受保护项**不是永久禁止删除**，而是必须先充分披露并经专门确认。

因此：F-02 的处理不是"修改冻结契约以允许删除保护"，而是**在既有契约之上补一层可验证的保护披露与确认契约**。

## 2. 现行语义基线（逐条摘录，均取自 `M2-C1` 现文本）

| 现行条款 | 内容 | 本裁定处置 |
|---|---|---|
| §5.11.1（:684–:725） | 单条 `PermanentlyDeleteBook{book_id, confirm_permanent_delete:true}`（closed shape，**明确不接受数组**）；批量 `{book_ids[1..20], confirmed_book_ids, confirm_count, confirm_permanent_delete}"`；ID 唯一、同序、不去重、不重排；**仅批量命令**拒绝"目标覆盖全部 Book 行"（防批量清空书架，单条按其既有确认语义不变）；UI 入口只在回收站；确认字段是 Core 硬门 | **保持**。§5 在其上增加"影响清单摘要绑定"，且**按单条/批量分别定义**（PD-02） |
| §5.11.2 第 1 步（:733） | 无副作用校验：closed shape、上限、ID 格式、唯一性、确认列表/数量 | **保持**，并纳入清单摘要校验（§5 PD-02） |
| §5.11.2 第 2 步（:734） | 全量预检：Book/待清理 manifest、非终态操作、关系图、目标外引用、Managed/derived 路径归属、reparse 安全；任一不可删则整批不开始。冲突条件是**不一致 / 无法安全拆分 / 未列明**（:752、:764），**不是"存在共享引用"即冲突** | **保持并扩展**：新增受保护内容清单计算（PD-01）；仍不把"存在保护"当作阻断条件，**也不把可安全拆分的共享引用**当作阻断条件（PD-08） |
| §5.11.2 第 3 步（:735） | **DB 全有/全无**：单一事务删除内容行、脱离并保留 Pipeline 历史、**移除项目 Lock/current/pinned Revision**、持久化清理清单；失败整体回滚 | **保持**。这是用户决定 #5 的"同一数据库事务中删除项目内容和相应保护"的现行依据 |
| §5.11.2 第 4 步（:736–:740） | 提交后逐本清理；单项失败不撤销 DB 事务、不阻断其余；`cleanup_pending`；仅显式确认后可重试 pending ID；不得后台自动重试，不得藏在其他命令/启动/GC/软删中 | **保持**（PD-06） |
| §5.11.3（:742–:760） | 错误表：`INVALID_REQUEST`、`DUPLICATE_BOOK_ID`、`BOOK_BUSY`、`BOOK_DELETE_CONFLICT`、`BOOK_DELETE_FAILED`、`BOOK_DELETE_CLEANUP_PENDING`、`BOOK_DELETE_BATCH_PREFLIGHT_FAILED`、`BOOK_DELETE_BATCH_WHOLE_LIBRARY`、`PROTOCOL_VERSION_UNSUPPORTED`；失败 `result=null`；不得回退软删 | **保持**；新增错误码候选见 §6.3（提案，未冻结） |
| §5.11.4（:762–:772） | 删除范围含 Lock 与 current/pinned Revision；**保留 Pipeline 历史**；用户源目录/源文件与 SHA-256 输入不在删除范围；**导出目录与导出文件一律保留**；不枚举/清理全库备份；项目源文件绝不移动/改写/删除；**预检期间不得单独解锁、解除 pin 或改写 current**；不得触发隐式 stop/GC/备份 | **保持**，其中"用户源文件不在删除范围"即用户决定 #6 的现行依据 |
| §5.11.5（:774–:799） | 安全错误投影、逐项状态、无路径/明文 | **保持** |

**现行实现与此一致**：`library.py:1069-1101` 在事务内直接删除 `regions`/`region_revisions`/`artifact_revisions`/`pages`/`books` 等（含保护数据），`library.py:704-847` 预检不含 Lock/pin 阻断项。因此"现行契约要求删除保护、方案主张拒绝"的冲突，在本裁定下以**现行契约的删除语义 + 新增披露要求**解决。

## 3. 四种流程的区分（不得混同）

| 流程 | 触发 | 删除什么 | 保护状态 | 原文件 | 现行依据 |
|---|---|---|---|---|---|
| **A. 应用回收站软删** | 用户在书架/详情删除 | 仅置软删标记；书籍信息、内容类型/顺序、阅读位置、问题、人工数据、结果、来源绑定**全部保留**，可恢复 | **全部保留**，不得因软删而解锁/取消 pin | 不动 | 现行 `LibraryService.delete_book`（软删）；**产品面未接线，见 §9** |
| **B. 自动清理 / 回收站到期 / 缓存与备份轮转** | 时间到期、空间策略 | 仅应用内数据与明确不受保护对象 | **必须保留** Lock、current/pinned、草稿、备份依赖、恢复链；显示未清理原因；**不得自动解除保护** | **从不触碰**，也不触碰 Windows 回收站 | 用户决定 #4；现行 cache 清理仅前缀白名单，不含保护判定 |
| **C. 用户显式彻底删除** | 回收站内明确操作 | 项目内容行 + 项目 Lock/current/pinned + 可由 catalog 归属的 managed/派生文件 | **先披露、后专门确认、再在同一 DB 事务中删除**（§5） | **不删除**；用户源文件/源目录永不移动、改写、删除 | `M2-C1 §5.11` + 用户决定 #5 |
| **D. 原文件独立删除** | 独立授权流程 | 用户选择的物理文件/文件夹，移入 **Windows 回收站** | 不适用；但必须检查共享引用与活跃 Run/lease | 唯一允许触碰原文件的流程 | 用户决定 #6；`AD-003 §3.7`；**当前零实现** |

**禁止的混同**：A/B 不得删除保护；C 不得动原文件；D 不得被 C 顺带触发，也不得在失败时降级为永久删除。

## 4. 保护状态的判定

- **有效保护**由 Core 判定，UI 只展示：Region 行 Lock 标记与 `text.translation_locked` 的**并集**（双投影已知差异见 Region 契约 §6/GAP-3），任何一侧为真即视为锁定；`manual_edited`/`final_source` 等同层标记按现行语义计入。
- **current Revision**：目标对象当前指针所指 revision；**pinned Revision**：`is_pinned=1` 的 revision；**活动草稿**：存在未提交 draft/edit token 的页。
- UI **不得**提供"删除时顺手解锁/取消 pin"的布尔绕过；也不得在确认前改变任何保护状态。

## 5. 冻结的语义要求（PD-01 – PD-10）

> 生效范围：本组要求是**实现必须满足的语义**，自本文件生效；在契约与实现冻结前状态为 `PENDING`，不得表述为已具备。

- **PD-01 影响清单（preflight inventory）**：对每个目标 Book 逐项计算并**不得写入任何状态**：人工修改区域数、锁定区域数（有效锁定并集）、current Revision、pinned Revision 数与列表、受保护 artifact 数、活动草稿页数、非终态 Run/Task（同时作为 `BOOK_BUSY` 阻断项）、将被删除的 managed/派生文件数与字节量、其他项目对该源的引用数。
- **PD-02 专门确认（按命令形状分别绑定，不得混用）**：
  - **单条**：沿用 §5.11.1 的 closed shape `{book_id, confirm_permanent_delete:true}`，**追加** `inventory_digest`（绑定该 `book_id` 的清单摘要）；**禁止**在单条命令中引入 `book_ids`/`confirmed_book_ids`/`confirm_count`（该命令明确拒收数组，见 `M2-C1:723`）。
  - **批量**：沿用 `{book_ids, confirmed_book_ids, confirm_count, confirm_permanent_delete:true}` 的有序绑定，**追加** `inventory_digest`（绑定该有序集合的清单摘要）。
  - 两处确认文案都必须明示"将删除人工修改/锁定/固定版本"的具体内容与数量；**通用"不可逆"确认不得替代**专门确认。字段名与协议版本均为提案（§6.1）。
- **PD-03 只读预览**：影响清单必须由 Core 权威计算并以**无副作用**方式对外提供（见 §6.1 提案）；不得由 UI 自行估算，也不得在预览时预置任何删除或解锁。
- **PD-04 确认前零变化**：从预览到事务提交之间，不得解锁、取消 pin、改写 current、删除行或移动文件；若期间任何目标状态变化（保护新增、集合变化、清单摘要不匹配），必须**拒绝执行并重新预览**。
- **PD-05 事务边界**：确认后，内容行与保护状态在**同一 `BEGIN IMMEDIATE` 事务**内删除；Pipeline 历史按 §5.11.4 脱离保留；清理清单在同一事务内持久化。
- **PD-06 失败回滚**：事务任一环节失败 → 整体回滚，保护状态与内容行**均不变更**，不开始任何文件清理。
- **PD-07 `cleanup_pending` 与重试**：沿用 §5.11.2 第 4 步与 §5.11.3；重试仅限显式确认的 pending ID，文件删除幂等；**不得后台自动重试**，不得夹带在其他命令/启动/GC/软删中；已完成项混入重试返回 `BOOK_NOT_FOUND` 且零副作用。
- **PD-08 共享引用（与 `M2-C1` 现行判定一致，不扩大）**：**可安全拆分**的共享引用**不是**删除阻断条件——删除目标项目自有的内容行与清单内自有文件，**保留共享物理原文件与其他项目的绑定**；这与 `M2-C1:764`（"无法安全拆分共享关系或发现未列明的目标外引用时，预检整体失败"）和 `:752`（"…**不一致**"）一致。**就共享引用冲突而言**，无法安全拆分、关系图/归属不一致、或存在未列明的目标外引用，使整批 `BOOK_DELETE_BATCH_PREFLIGHT_FAILED`；其他预检失败（如 `BOOK_BUSY`、目标不存在）仍按 `M2-C1 §5.11.3` 处理。"项目已软删"不构成引用消失的证据；共享源默认保留。**原文件是否删除只由 D 流程（独立授权）决定，与本流程无关。**
- **PD-09 批量原子性与逐项状态**：DB 全有/全无；清理阶段允许逐项部分完成并逐项报告 `deleted` / `cleanup_pending` / `not_started`；不得伪报整体完成。
- **PD-10 自动清理与软删**：B 流程永远保留 PD-01 所列保护项，并显示未清理原因；任何"到期自动清理"不得跨入 C 流程的权限。

## 6. 协议与实现影响（提案，未冻结、未实现）

### 6.1 需要的新增能力

| 能力 | 形态（提案） | 理由 |
|---|---|---|
| 影响清单预览 | 新增**只读**命令（如 `PreviewPermanentDeleteBooks`），closed shape 入参（同目标集合），返回清单 + `inventoryDigest` + `computedAt`；零副作用、不缓存、不预解锁 | PD-01/PD-03：清单必须由 Core（DB 权威）计算 |
| 确认绑定 | 现有删除命令增加 `inventory_digest` 字段并纳入 closed shape 校验（`INVALID_REQUEST` 或新 `BOOK_DELETE_STALE_PREVIEW`） | PD-02/PD-04：防止确认后目标或保护被替换 |
| 分阶段状态 | 现有 `confirm_permanent_delete: true` 语义**保持**；新增字段为**追加**，不改旧字段含义 | 兼容 §5.11.3 "不得回退软删" |

> 任何字段/命令新增都是 **Core protocol 变更**（当前 §5.11 为 `{major:2, minor:10}`），必须按逐命令 minor 语义冻结并由 DSH 批准；本文件**不**冻结具体字段名。

### 6.2 兼容与失败

- 旧 Host/Core/PROTOCOL 不识别新命令或新字段 → `PROTOCOL_VERSION_UNSUPPORTED` 或 fail-closed，**不得**以"忽略 digest 继续删除"或"回退软删"降级。
- 清单计算失败（DB 错误、目标消失）→ 返回 `BOOK_NOT_FOUND` / `BOOK_DELETE_CONFLICT`，零副作用。
- UI 展示清单失败或用户未完成专门确认 → 不得提交删除。

### 6.3 待冻结的错误码候选

`BOOK_DELETE_STALE_PREVIEW`（conflict, retryable=false，需重新预览）、`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`（internal/unavailable, retryable=true）。**未冻结**；最终码表由 D04/D07 冻结，且必须继续遵守 §5.11.5 的安全投影约束（无路径、无明文）。

## 7. 与现行实现和冻结契约的关系

- **不修改 `M2-C1` 字节**。本文件是其 **additive amendment**；§5.11 的条款编号与语义继续有效，PD-01/02/04 为其前置补强，PD-03 为其外部可观测面。
- **不修改 Region 写契约**：pin/Lock 语义、append-only revision、恢复历史版本另立新 revision 均不变。
- **已知现状风险（不得掩饰）——必须按四层分别陈述，不得混为一谈**：

| 层 | 现状 | 依据 |
|---|---|---|
| Core 命令面 | `PermanentlyDeleteBook` / `PermanentlyDeleteBooks` / `ListRecycleBinBooks` 存在；**无**书籍/页级软删命令、**无**恢复命令 | `src/bootstrap/core_service.py:298,4403,4559` |
| 应用服务层 | 页级软删/恢复 `TrashService.soft_delete_pages` / `restore_batch` **已存在**；书籍软删 `LibraryService.delete_book`（`book.soft_delete()`）**已存在** | `src/application/maintenance/trash.py:119,188`；`src/application/library/service.py:97-100` |
| Host 接口 | 未暴露回收站列表/恢复/永久删除方法 | V2 自述"Host 未暴露 list_recycle_bin / restore / purge 方法"（`LibraryViewModel.cs:793-796`） |
| V2 UI | 回收站读取、恢复、永久删除**全部返回"能力待接入"**，用户当前**不可达任何删除** | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs:793-796,1214-1224` |

  因此：**不能说**"V2 只有不可逆硬删"（V2 连硬删都不可达），**也不能说**"软删能力不存在"（服务层已存在）。准确表述是：**服务层有软删/恢复实现，命令面与 Host/V2 接线缺失，用户当前无可用删除路径**。这属现状风险，不是本裁定授权；服务行为与真实运行结果另行验证（`NOT_RUN`）。
- **双 Lock 投影**：Region 列与 `text.translation_locked` 的有效并集规则必须先由 Core 统一，UI adapter 不得静默改写语义。

## 8. 未实现与 NOT_RUN

| 项 | 状态 |
|---|---|
| 影响清单计算（Core） | 未实现 |
| `PreviewPermanentDeleteBooks` 或等价只读命令 | 未实现（提案） |
| `inventory_digest` 确认绑定 | 未实现（提案） |
| 专门确认 UI 与文案（单条/批量分别） | 未实现 |
| A 流程：Core 软删/恢复**命令**与 Host/V2 接线 | 未实现（**服务层方法已存在**，见 §7 四层表） |
| D 流程（Windows 回收站） | 零实现 |
| B 流程的统一保护 preflight | 未实现（现状为三套异构机制：cache 前缀白名单 / 页级无保护 purge / book 级 6 项预检） |
| 全部 AC 与故障注入测试 | `NOT_RUN` |

## 9. Gate 与审查安排

| Gate | 状态 |
|---|---|
| G-DELETE-SEMANTICS（本裁定） | **SATISFIED**（语义已冻结；用户决定已记录） |
| G-DELETE-CONTRACT（协议字段/码表/D04-D07 冻结） | **CLOSED（2026-11-01）**——D04（C-13）/D05（C-06+C-14+C-01b）/D06（C-08 v7）/D07（C-09 v5+C-01b+C-04b）全部有冻结承载；见 [Gate 裁定](../plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md)。**保留项 L-1…L-9，其中 L-5（整库恢复须持 SC-17 锁）为本裁定的明文认定** |
| G-DELETE-IMPL（Core 实现 + 故障回归） | **OPEN**（未释放） |
| G-REVIEW（独立 Review 本文件） | **ADDRESSED_PENDING_R2** — Codex 独立 Review r1（[`doc/reviews/FEA-00-codex-r1.md`](../reviews/FEA-00-codex-r1.md)，SHA-256 `f2fd02e0…17693ba2`）判 `changes_requested`：R-01 P0、R-02/R-03/R-04 P1、R-05–R-07 P2。本 r2 已逐项修订（[处置记录](../reviews/FEA-00-codex-r1-adjudication.md)）；**尚未获批**，待 Codex 对新 hash 复审。ZCode 仍 `reviewer_unavailable` |

## 10. 字节保留声明

`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`、V11R/Region 冻结契约、历史 Review/日志/manifest/evidence pin 与 `doc/tasks/**` 均未修改；本文件为新增裁定文档。

## 11. 变更记录

| 日期 | 变更 | 依据 |
|---|---|---|
| 2026-10-31 | 初版：对照 §5.11.2 明确现行删除语义保持有效；冻结 PD-01–PD-10；区分 A/B/C/D 四流程；提出只读预览 + 清单摘要确认提案；记录未实现项与 Gate | 用户 2026-10-31 决定 4/5/6；`M2-C1 §5.11`；FEA-00 r1 F-02 |
| 2026-10-31 | **r2（按 Codex 独立 Review r1 修订）**：R-01 重写 PD-08——可安全拆分的共享引用**不再**被判为全批冲突，只有不一致/无法拆分/未列明才 fail-closed，与 `M2-C1:752,:764` 对齐；R-02 把 PD-02 拆为单条/批量两种确认绑定并明确单条拒收批量字段；R-03 修正 5 处相对链接；R-05 用四层现状表替换"V2 只有硬删"的错误表述；§9 更新 Review 状态 | Codex R-01/R-02/R-03/R-05；[处置记录](../reviews/FEA-00-codex-r1-adjudication.md) |
