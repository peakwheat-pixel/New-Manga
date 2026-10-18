---
id: P09-AC3-DELETE-1
title: 项目级永久删除（Core 硬删除）与 P09 AC3 源文件零改动回补
kind: feature
governance_version: 2
status: closed_with_limitations
approval: user_ruling_20261018_create_p09_ac3_delete
blocked_by: null
suggested_owner: Antigravity（ZCode CLI 不可用，按项目故障转移顺序）
owner: Antigravity
reviewer: Codex（非作者；同时负责先冻结本 Task 需要的新契约）
depends_on: [P09]
base_commit: baf4ec90c
branch: null
worktree: G:/CODEX/New Manga（真实工作流验证须在隔离环境执行；执行方写 verification/P09-AC3-DELETE-1/**、本 Task、doc/handoffs/P09-AC3-DELETE-1-*.md）
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/P09-AC3-DELETE-1
---

# P09-AC3-DELETE-1：项目级永久删除与 P09 AC3 回补

## 来源与依据

- 用户裁决（2026-10-18）：就 `P09` 的 AC3 残留缺口**立即另立本 Task 补齐**（不等待未来功能）。
- 缺口事实（`P09` 的 AC3 = `AC-IMPORT-002` [P0]「源文件零修改」）：
  - ✅ 已实测通过：两个隔离源样本在**导入、软删除、Page 级永久清理、真实 `TRANSLATE_ALL` / `REINPAINT_REGION` / `RERENDER_SINGLE`** 后 hash 完全相同（证据 `verification/P09/evidence/AC3-source-hashes.json`、`37-ac3-workflow-source-hashes-final.txt`）。
  - ❌ **BLOCKED**：**"项目级永久删除"路径无法验证** —— `LibraryService.delete_book` 仅**软删除**，`TrashService.purge_batch` 仅 **Page 级**；Core **不存在**项目级永久删除，且 P09 的授权路径不允许为验证它而新增功能。
- 因此本 Task = **先实现该功能（含源文件保护），再回补 P09 的 AC3 验证**。

## Acceptance Criteria

- [x] AC1：**契约先行（阻断性）**——rev 2.10 保留既有单条删除命令请求形状，并新增独立批量 IPC command，冻结命令、参数、返回、错误、ACL、数据留存及批量原子性。共享契约见 [M2-C1 §5.11](../contracts/M2-C1_TYPED_IPC_CONTRACT.md#p09-ac3-delete-1-permanent-delete)；本轮裁决与相对 r1 的差异见 [AC1 冻结记录 r2](../../verification/P09-AC3-DELETE-1/contract-freeze-r2.md)。AC1 完成**不授权实现**；本 Task 剩余产品裁决完成、实现范围由 Codex明确释放前不得开始 AC2–AC7。
- [x] AC2：**项目级永久删除可用**——提供"永久删除项目"操作：删除该项目内容 DB 行（book/chapter/page、区域、Revision、Managed Copy 元数据及其余当前内容关系），回收其 **Managed Copy** 与派生资源；按契约脱离并保留 Pipeline Run/Task 历史，用户导出目录文件与全库历史备份不触碰。软删除（`delete_book`）与 Page 级 purge 的既有语义**不得改变**。
- [x] AC3：★ **源文件零改动（P0）**——永久删除项目后，**项目源目录内的源文件 hash 完全不变**（与删除前逐文件比对）；用 P09 同款隔离样本与真实工作流验证，产出可比对报告。
- [x] AC4：**无项目内容残留**——删除后无 Book/Chapter/Page/区域/Revision 等内容行；Pipeline 历史记录保留且已脱离删除内容与资源 locator；Managed Storage 与派生/缓存目录**无孤儿文件**（给出清理前后文件数与字节数）；用户源文件和用户导出目录文件逐文件未变；`core` 日志与 GC 路径无错误。`export_history` DB 行的处置须待裁决后按冻结口径核查。
- [x] AC5：**误删防护与语义区分**——永久删除入口只在回收站提供、书架不暴露；用户勾选目标后必须通过显示精确目标和数量的第二次确认，IPC 目标 ID/数量与确认一致；提示应用回收站不可恢复、用户导出文件保留、旧全库备份可能保留删除前数据；不提供隐式触发路径。
- [x] AC6：**回补 P09 AC3**——把该路径证据并入 `verification/P09/evidence/**` 与 `P09.md` 的 Canonical Evidence；把 `P09.md` 的 AC3 从 `BLOCKED` 更新为**实际达成状态**（若仍有未覆盖路径则如实保留局部限制，并说明剩什么）。
- [x] AC7：**不回归 P09 已通过项**——导入 / 翻译 / 重修 / 重渲染 / 软删除 / Page 级永久清理的源 hash 零变化结论**不得退化**：复用 P09 的既有验收命令重跑并给出对照。

## AC1 契约冻结 rev 2（2026-10-18，第二次冻结）

### 本轮裁决与修订依据

r1 冻结的 `PermanentlyDeleteBook` 明确只接收一个 `book_id`。用户确认必须支持批量后，该请求不能悄悄改成数组：这会破坏已冻结 payload，故采用**独立批量命令**，原单条命令和参数保持不变。共享规范为 [M2-C1 §5.11](../contracts/M2-C1_TYPED_IPC_CONTRACT.md#p09-ac3-delete-1-permanent-delete) rev 2.10；逐条前后差异见 [contract-freeze-r2.md](../../verification/P09-AC3-DELETE-1/contract-freeze-r2.md)。

### 冻结命令与协议

| 项 | 冻结值 |
|---|---|
| 单条 Tauri/Core | `library_delete_book_permanently` / `PermanentlyDeleteBook`；`{book_id, confirm_permanent_delete: true}` 不变 |
| 批量 Tauri/Core | `library_delete_books_permanently` / `PermanentlyDeleteBooks`，production-only |
| 协议 | M2-C1 文档 rev `2.10`；Core major `2` / minor `10`（minor `9→10`） |
| 批量 payload | `{book_ids: BookId[1..20], confirmed_book_ids: BookId[1..20], confirm_count: integer, confirm_permanent_delete: true}`；closed shape，无路径/未知字段 |
| 上限/输入 | 1..20 个唯一 ID；超过 20 拒绝；重复 ID 拒绝、不去重；目标集合等于当前全部 Book 行时拒绝 |
| 成功结果 | `{requested_count, completed_count, items: [{book_id, status: "deleted", error_code: null}]}`，items 保持输入顺序 |
| 批量错误逐项结构 | `{book_id, status: "not_started" | "cleanup_pending" | "deleted", error_code: string | null}`；错误投影只带安全的阶段、计数、items |

### 批量执行语义与完整拒绝面

- 先对**全部**目标预检；缺失、忙碌、关系不完整、目标外引用、资源不安全等任一项失败时，整个批量 DB 操作不开始，返回 `BOOK_DELETE_BATCH_PREFLIGHT_FAILED` 和按输入顺序排列的 `not_started` 逐项结果。
- 项目内容删除与历史脱离、Lock/Revision 清除、全部清理 manifest 持久化在**单一 DB 事务**：全有/全无。提交前失败用 `BOOK_DELETE_FAILED` 并回滚，不开始删文件。
- DB 提交后按输入顺序逐本清理，单本失败不回滚其他已完成项，也继续处理其余项目。所有清理完成才返回成功；有 pending 项则返回 `BOOK_DELETE_BATCH_CLEANUP_PENDING`，明确给出 `deleted` 与 `cleanup_pending` 逐项状态。
- pending 重试必须由用户显式确认，且只提交 pending IDs；清理 manifest 的文件删除幂等。已完成 ID 重放返回 `BOOK_NOT_FOUND` 且无副作用；混入重复 ID 用 `DUPLICATE_BOOK_ID`。
- 错误码：`INVALID_REQUEST`（shape/确认不匹配/空列表）、`DUPLICATE_BOOK_ID`、`BOOK_DELETE_BATCH_LIMIT_EXCEEDED`、`BOOK_DELETE_BATCH_WHOLE_LIBRARY`、`BOOK_DELETE_BATCH_PREFLIGHT_FAILED`、`BOOK_DELETE_BATCH_CLEANUP_PENDING`、复用 `BOOK_NOT_FOUND` / `BOOK_BUSY` / `BOOK_DELETE_CONFLICT` / `BOOK_DELETE_FAILED`、`PROTOCOL_VERSION_UNSUPPORTED` / `UNKNOWN` / `CORE_UNAVAILABLE`。类别、重试性、逐项 `error_code` 白名单与 Tauri 安全投影详见共享契约 §5.11。

### 二次确认与禁止隐式触发

- 入口只在**回收站**，书架不显示永久删除操作。用户在回收站勾选后，第二步显示精确作品身份与数量、删除范围和不可恢复影响；必须勾选确认后提交。
- `confirmed_book_ids` 必须与 `book_ids` 同序完全相等，`confirm_count == len(book_ids)` 且 `confirm_permanent_delete == true`。前端在最终确认后从同一冻结的选择快照组装这三项，Core 再校验；确认失败零副作用。
- 必须提示 App 回收站无法恢复、用户选择目录内导出文件保留、全库历史备份不处理且可能含旧快照。不得由软删除、导入失败、GC、启动/退出、Pipeline 或其他 command 隐式触发；不回退软删除或 Page purge。

### 数据、文件及备份裁决后果

| 对象 | 永久删除结果 |
|---|---|
| 项目当前内容 | 删除 `books`、`chapters`、`pages`、`regions`、`region_revisions`、`media_artifacts`、`artifact_revisions`、`reading_progress`、项目 `book_tags` 关联、Lock、current/pinned Revision 与其项目关系；共享 `tags`、全局设置/metadata 保留 |
| Pipeline 历史 | 保留 `pipeline_runs`、`pipeline_run_targets`、`pipeline_tasks`、`step_runs`、`step_run_input_refs`、`step_run_output_refs`、`step_result_candidates`、`pipeline_stage_states` 的历史记录；脱离被删 Book/Page/Revision/Artifact 外键，移除资源 ID、路径和 locator；保留状态、操作类型、时间、顺序及安全结果/错误摘要。非终态/可恢复操作仍阻断删除 |
| 用户源目录与文件 | 永不移动、改写或删除；逐文件磁盘 hash 验收 |
| Managed Copy 与派生/缓存 | 只回收 DB 清单及 resource catalog 可权威归属的目标；校验受控 root 与 reparse point；持久 manifest 支持显式重试 |
| 用户导出目录文件 | 必须保留；命令不接收/枚举/删除该目录或文件 |
| `export_history` DB 行 | **已裁决（2026-10-18，用户）**：**保留**并脱离已删 Book（与 Pipeline 历史同口径）；用户导出目录中的输出文件保留不受此项影响 |
| 全库历史备份 | 不属于本命令：不创建、扫描、修改或删除；旧备份可能保留删除前快照，不能承诺从中抹除 |

若 Pipeline 历史与内容外键不能脱离，整批必须回滚，不得级联删除历史。**已裁决（2026-10-18，用户）**：保留 Pipeline 历史并**保留 Book 名称快照**（不采用"已删除作品"占位）。

### ACL 与向后兼容

- 新批量 allow identifier：`allow-library-delete-books-permanently`，自动生成 deny counterpart `deny-library-delete-books-permanently`；只加入 production capability `m2rc1-commands.json`。Tauri 命令清单、production handler、`build.rs` app manifest 和 allowlist 计数同步；由 `tauri-build` 生成 `permissions/autogenerated/library_delete_books_permanently.toml` 与 schema，禁止手写；不进入 probe/AC1 handler。
- 计数：前序 58 条 + r1 单条 `PermanentlyDeleteBook` = 59 条 + 本轮批量 = 60 条（53 production + 4 probe + 3 AC1）。既有 58 条与 rev 2.9 单条 command 的 payload/result/error/ACL 不变。rev 2.10 只新增命令与错误字符串，major 不变、minor `9→10`；旧 host 不注册批量命令，旧 Core 对未知命令 fail-closed。
- 当前只冻结契约；不改 runtime、Schema/migration、ACL 生成物、capability、React/Rust 或测试。若实现需迁移以脱离历史，须先更新 Task allowlist 并由 Codex授权。

### P09 AC3 回补与证据分工

- 回补后在隔离根运行真实 Core assembly 工作流，使用 P09 两个源样本；永久删除前后对源目录**逐文件**按相对路径记录 size 和磁盘字节 SHA-256，并核对文件集合相同、无缺失/新增/改名，不能只比较 DB `source_hash`。
- 工作流须包括导入、软删除/Page purge 已通过路径，以及本 Task 的单条与批量项目级永久删除；第二个样本在项目删除前执行真实 `TRANSLATE_ALL`、`REINPAINT_REGION`、`RERENDER_SINGLE`。最终逐文件 hash 必须与删除前完全一致。
- `verification/P09/evidence/**` 存 P09 Canonical Evidence；`verification/P09-AC3-DELETE-1/**` 存本 Task 原始产物：脚本、命令/环境/时间戳/退出码、Core 日志、DB 内容/历史核查、Managed/derived 清理计数与孤儿扫描、源文件逐项 hash。保留既有阶段记录与 source pins，不覆盖原始日志。
- P09 AC3 仅在实际全路径通过后更新；任何未实测路径保持 `BLOCKED` 或局部限制。AC7 重跑 P09 已通过工作流并对照。

### 已裁决与仍待用户裁决

已裁决：①入口仅回收站，勾选后第二次确认，书架不暴露；②支持批量；③保留 Pipeline Run/Task 历史、不删除用户导出目录文件；④全库历史备份不纳入永久删除处理。

已裁决（2026-10-18，用户）——实现前置已解除：

1. ✅ `export_history` 数据库记录**保留**，并脱离已删 Book；UI 历史列表可正常呈现（书名取自快照）。
2. ✅ 保留的 Pipeline Run/Task 历史**保留 Book 名称快照**。

本轮没有实现代码、运行产品测试或修改 ACL/Schema。AC1 契约冻结完成；以上两项解决且 Codex更新实施授权范围前，Owner 不得开始 AC2–AC7。

## 允许修改范围

- Core（`src/**`）中与项目级删除、purge、资源回收相关的实现与测试。
- Tauri 侧与前端**仅在契约冻结后**、且仅限"永久删除"入口与确认交互所需的最小改动。
- `verification/P09-AC3-DELETE-1/**`、本 Task、`doc/handoffs/P09-AC3-DELETE-1-*.md`、以及**契约冻结所必需的** `doc/**` 记录（由 Codex 落笔）。
- `P09.md` 的 AC3 状态与 Canonical Evidence 更新（回补时）。

## 禁止范围

- **契约未冻结前不得**新增/修改 IPC 命令、Schema、错误码、ACL 白名单。
- 不得改依赖版本；不得降低任何既有阈值；不得放宽 `AC-IMPORT-002`（源文件零修改）的判定。
- 不得改变既有软删除 / Page 级 purge 的语义或删除它们的能力。
- 不得用"删掉测试/跳过断言/只改判定口径"来让 AC 通过；源 hash 必须以**磁盘字节**重算。
- 不 push；不动用户 43 项未提交改动（含 `verification/P19/codex-review-r2.md`）；GUI/工作流验证用 `%TEMP%` 隔离根（禁止放 `apps/desktop/src-tauri/target/**`），并保护用户真实 `%APPDATA%\com.newmanga.m2rc1.desktop` 数据。

## 测试要求

planned：永久删除的真实工作流验收（隔离源样本 + 真实 Core assembly）；删除前后**逐文件 hash 对照**；DB 行与孤儿文件核查（清理前后计数）；软删除/purge 语义不回归；P09 既有 AC 重跑对照。全部结论须附原始产物（脚本、日志、时间戳、退出码）。

## 依赖、风险与阻塞

- 依赖：`P09`（提供 AC3 事实、隔离样本与验收脚本）。
- 风险一：**契约变更**是本 Task 最大风险 —— AC1 rev 2.10 已冻结；批量以独立命令增加到 60 条，不破坏前序 58 条或既有单条请求。`export_history` 行处置与历史标题快照仍阻断实现。
- 风险二：永久删除属**不可逆破坏性操作**，验证必须全程在隔离根内，且不得对用户真实数据执行。
- 已知阻塞：AC1 rev 2.10 已冻结；`export_history` 行处置与 Pipeline 历史标题快照待用户裁决，在此之前 AC2–AC7 不得释放实现。

## 交付与运行记录

- 2026-10-18 Coordinator（dsh, epoch 7）按用户裁决创建本 Task；`status: ready`。
- 运行记录：Codex 已于 2026-10-18 完成 AC1 第二次冻结；待两项产品裁决补入 Task 后，由 Codex更新实施 allowlist 并释放 Owner。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| P09-AC3-DELETE-AC1-R2 | AC1 | `verification/P09-AC3-DELETE-1/contract-freeze-r2.md` | `694de50789de4e9b6ecde831364ddbca167fcb44` | `0ddca1f561bdd3992c34b6795ac2ae1272bf7679cabb437156b707e653bfbbda` | CANONICAL |
| P09-AC3-DELETE-M2-C1-2.10 | AC1 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | `694de50789de4e9b6ecde831364ddbca167fcb44` | `f954c2fda2fb213120cae33f859928c97c35a6aa73fbea980098af8b0bc01c08` | CANONICAL |
| P09-AC3-DELETE-ALL-AC | AC2-AC7 | `verification/P09-AC3-DELETE-1/evidence/p09_ac3_delete_evidence.json` | `d9f7a628c7c0b9e00d91a1bddd102daec76139c5` | null | CANONICAL |
| P09-AC3-SOURCE-HASHES | AC6 | `verification/P09/evidence/AC3-source-hashes.json` | `d9f7a628c7c0b9e00d91a1bddd102daec76139c5` | `56e40a827c20725cc1a66ddd527c521b84fcd059f624873732cfcecb814266e3` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| 不新建 worktree | 复用 `G:/CODEX/New Manga` | `NOT_APPLICABLE` | 不适用 | 不适用 | 收口时实测未创建/未删除资源；`m2rc1-desktop`/`core_service`/`host_bridge` 进程数 = 0；隔离验证根均在 `%TEMP%` 且已清理。 |

## Coordinator 独立复核（2026-10-18）

### ★ AC3（P0 源文件零改动）—— 独立复核成立

1. **源样本 hash 独立重算**：Coordinator 自行对 `verification/P09/evidence/AC3-source.png` 与 `AC3-workflow-source.png` 计算磁盘字节 SHA-256，结果分别为 `36452bb8…d7` 与 `ee5f4ae0…95`，**与 `AC3-source-hashes.json` 中 `sample1_after_hash` / `sample2_after_hash` 完全一致**。
2. **阶段不变性**：证据记录每一 case 的 **6 个阶段**（`before_import` → `after_import` → `after_project_soft_delete` → `after_page_soft_delete` → `after_permanent_page_purge` → **`after_permanently_delete_book`**）hash **全部相同**，即**永久删除项目后源文件仍未改变**。
3. 两个 case 的测试为 `test_source_hash_survives_import_hide_and_permanent_page_purge` 与 `test_source_hash_survives_translation_repair_and_rerender`。

### 附带证据：用户真实数据未被改动

Owner 证据含 `appdata_protection`：`%APPDATA%\com.newmanga.m2rc1.desktop` **24 个文件 / 1,768,641 字节**。Coordinator 独立复核该目录的**文件数、总字节数与 `LastWriteTime`（2026-09-29 10:37:15）逐项一致** → **未被改动**。

⚠️ **一处证据瑕疵（不影响结论）**：该字段的 `tree_sha256`（`7136daeb…`）**无法被独立复现** —— Coordinator 按"相对路径:文件hash"字典序拼接重算得 `176e96de…`，与声称值不同。差异源于**拼接算法未在证据中说明**（未文档化的规范化方式），属**可复核性缺陷**而非数据问题；文件数/字节数/时间戳三项已足以证明数据未变。**已登记，建议后续证据文件明示 tree hash 的规范化算法。**

### ⚠️ Coordinator 独立复跑发现的未报告失败（已派修）

`python -m pytest tests/core -q` → **1 failed, 544 passed**（exit 1）：
`tests/core/test_bootstrap.py::test_assemble_services_injects_and_exports_diagnostics` 断言 `schema_version == "4"` 而实际为 **v5**（本 Task 引入 Schema v5）。Owner 报告**未提及此失败**，说明其验收**未跑全量 Core 测试**。已派最小范围修正（同步版本期望 + 全仓搜索其他硬编码 + 重跑全量 + 自查验收遗漏）。

## Closeout Record

- Closeout date / Coordinator：**2026-10-18**，Coordinator = dsh（epoch 8），按用户裁决收口。
- `canonical_evidence_status`：`complete`（**含 limitation**：1 条 pin 已失效，见下节）。
- `resource_closeout_status`：`complete`（未创建、未删除资源）。
- 删除、迁移、归档数量/字节数：0 / 0 / 0。
- 未关闭项及保留原因：见下节「未闭合项清单」。
- 当前指针清理：`doc/STATUS.md` 与 `doc/REBASELINE_PLAN.md` 已同步为 `closed_with_limitations`。

## Coordinator 收口说明（2026-10-18，用户裁决）

### 收口依据

本 Task 经三轮独立复审（R1/R2/R3）与 R1fix、R2fix **两次返修**，已达 **DIR-4**「同一失败面最多 2 次返修」上限。第三轮复审（`verification/P09-AC3-DELETE-1/codex-review-r3.md`，reviewed_head `a04e4ea78d5b33a0f91efcdc06b396391c4b165e`）结论为 **`changes_requested`**。用户裁决：**拆加固 Task 接手未闭合项，原 Task 以 `closed_with_limitations` 收口，不突破 DIR-4**。

**本 Task 不记为技术通过；`P09` 的 AC3 保持 `BLOCKED`，不得翻为 `PASS`，不得收口为全项通过。**

### R3 finding 状态（原样保留，未改写）

| 状态 | 项 |
|---|---|
| closed | R-001、R-002、R-004、R-005、R-006 |
| partial | R-003、R-007、R-010 |
| open | R-008、R-009、R-011、R-012 |
| **新增 P1（R3 发现）** | N-001、N-002、N-003、N-004 |
| **新增回归（T2 取证）** | `tests/packaging/test_frozen_runtime_contract.py::test_explicit_data_root_isolation` |

### 未闭合项清单（交接给 `P09-AC3-DELETE-HARDEN-1`）

1. **R-007 partial**：回收站命令未注册到 Tauri production command/handler 与 Core IPC handler；真实 UI 会静默显示空回收站。
2. **N-001 P1**：`UNIQUE(pipeline_run_id, target_id)` 使多页 Run 的永久删除整体失败。
3. **N-002 P1**：`cleanup_pending` 无法按契约逐项重试。
4. **N-003 P1**：译图 preview 资源残留。
5. **N-004 P1（数据安全）**：先 `resolve()` 再 `lstat()` 可被 symlink 替换绕过，可能误删 derived root 内其它登记资源。
6. **R-003 partial**：`pipeline_stage_states` 未实际 detach；`run_json` 嵌套定位引用未清。
7. **R-008 open**：`verify_all.py` 多表 `rows = else 0` 恒真，AC4 的 PASS 不可采信。
8. **R-011 open**：仍 `os.walk` 递归遍历 `storage.root/books/<book_id>`。
9. **R-009 open**：Rust `details.phase` 未做白名单投影。
10. **R-010 / R-012 partial / open**：交付指针、证据 pin 与实现范围释放未自洽。

### 证据 pin 状态（如实记录，未篡改历史）

- `P09-AC3-DELETE-AC1-R2`、`P09-AC3-DELETE-M2-C1-2.10`、`P09-AC3-SOURCE-HASHES`：pin 与磁盘字节**一致**（收口时实算确认）。
- `P09-AC3-DELETE-ALL-AC`（`verification/P09-AC3-DELETE-1/evidence/p09_ac3_delete_evidence.json`）：**原 pin `560dd8acdd3915817c3819be477b58fd9f5fa46124ea4d20eb2be24af1b264b5` 已失效** —— 该文件在 `d9f7a628c` 提交后被 R2fix 更新，收口时磁盘 SHA-256 为 `67d4dbdb008a0603aa662471e22f80c2af669fb1eab784d92cec52f94d4d6261`。遵循「禁止为消除失败而改写历史 pin」，本表**未把该值刷成当前值**，仅将 sha 列置 `null` 并在本段完整保留原值与现值。
- 全部 commit 列改为**确实包含该路径**的 40 位 SHA（原 `UNCOMMITTED` 占位无法通过终态校验）。

### 交接

未闭合项由 **`P09-AC3-DELETE-HARDEN-1`**（`ready`，Owner=Antigravity / Reviewer=Codex）接手，见 `doc/tasks/P09-AC3-DELETE-HARDEN-1.md`。原 Task 的 12 项 finding 与 4 项新 P1 的原始状态在该 Task 前置中不得抹除。
