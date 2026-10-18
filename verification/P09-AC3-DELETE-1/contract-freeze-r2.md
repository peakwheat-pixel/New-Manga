# P09-AC3-DELETE-1 AC1 契约冻结 r2

**日期：**2026-10-18（Asia/Shanghai）  
**Agent：**Codex — Lead / Architect / Integrator  
**Task：**`P09-AC3-DELETE-1`，仅 AC1，第二次冻结  
**基线：**`main`，HEAD `6cba806e5300ac0e0c2496499de50eb1ae483f5c`，Git common directory `.git`  
**状态：**M2-C1 rev 2.10 已冻结批量 API 与用户裁决的契约后果。仍有两项产品裁决阻断实现。本轮未写实现代码、未运行产品测试。

## 修订依据与裁决

M2-C1 rev 2.9 的 `PermanentlyDeleteBook` / `library_delete_book_permanently` 明确只收单个 `book_id`，拒绝数组。用户裁决永久删除必须支持批量。把现有参数改成 `book_ids` 会破坏已冻结的单条输入契约，因此选择 **(b)：新增独立批量命令，保留单条命令不变**。

本轮记录的用户裁决：①UI 入口仅在回收站，书架不暴露，勾选后进行第二次确认；②支持批量；③保留 Pipeline Run/Task 历史，绝不删除用户选定导出目录中的文件；④全库历史备份不属于本操作。

## 冻结 API

| 接口面 | 冻结值 |
|---|---|
| 既有单条命令 | Tauri `library_delete_book_permanently` → Core `PermanentlyDeleteBook`；`{book_id, confirm_permanent_delete: true}` 与 `{book_id, deleted: true}` 不变 |
| 新批量命令 | Tauri `library_delete_books_permanently` → Core `PermanentlyDeleteBooks`；仅 production |
| 批量入参 | `{book_ids: BookId[1..20], confirmed_book_ids: BookId[1..20], confirm_count: integer, confirm_permanent_delete: true}`；closed shape，不收路径或未知字段 |
| 批量成功结果 | `{requested_count, completed_count, items: [{book_id, status: "deleted", error_code: null}]}`，保持输入顺序 |
| 协议 | M2-C1 文档 rev `2.10`，Core major `2`、minor `9→10` |
| ACL | production capability 新增 `allow-library-delete-books-permanently`；`deny-library-delete-books-permanently` 由 Tauri 自动生成作为默认 deny 项 |

### 方案比较

- **(a)，扩展既有命令参数：不采用。** 把单个 `book_id` 改为数组会破坏 rev 2.9 已冻结的单条请求形状，也会要求单条调用方迁移。
- **(b)，新增独立批量命令：采用。** 满足批量需求，同时让旧单条 API 保持不变，并能独立规定批量权限、预检、上限和部分清理结果。
- **(c)，前端串行调用单条命令：不采用。** 后续目标失败时早先的书已被删，无法先做全体预检；也没有服务端批量上限与“不可一次清空书架”保护，逐条对话还会遮蔽整体结果。

## 批量安全、原子性与错误

- 批量最多 **20 个唯一 Book ID**。空列表、未知字段、非法 ID 被拒绝；重复 ID 返回 `DUPLICATE_BOOK_ID`，Core/host 不静默去重或重排。
- `confirmed_book_ids` 必须与 `book_ids` 同序完全相等；`confirm_count` 必须等于数组长度；`confirm_permanent_delete` 必须是布尔值 `true`。不匹配时在副作用前返回 `INVALID_REQUEST`。
- 如果批量 ID 集合等于全部现存 `books` 行，Core 返回 `BOOK_DELETE_BATCH_WHOLE_LIBRARY`，阻止一次批量调用清空书架。
- 删除前先预检所有目标、操作状态、关系图、外部引用、managed-resource 归属及路径安全。任一预检失败即不删除任何 Book；返回 `BOOK_DELETE_BATCH_PREFLIGHT_FAILED`、按输入顺序排列的逐项 `not_started` 状态及安全错误码。
- 所有项目内容行删除、历史记录脱离、清理 manifest 持久化处于一个 DB 事务。事务或清单失败返回 `BOOK_DELETE_FAILED`，事务回滚且不触碰文件。
- DB 提交后按输入顺序逐本回收 managed/derived 文件。文件系统失败不能回滚已删除文件；继续处理其他条目，并以 `BOOK_DELETE_BATCH_CLEANUP_PENDING` 逐项报告 `deleted` / `cleanup_pending`。任一条目未完成都不得报告整体成功。
- 用户再次显式确认后，只能用 pending IDs 重试。持久 manifest 使 pending 书目的清理幂等；已完成 ID 重放时返回 `BOOK_NOT_FOUND` 且无副作用。启动、退出、GC、软删除、导入或 Pipeline 命令不得隐式重试。
- 批量错误投影只允许 `phase`、请求/完成数量、有序 Book ID、稳定状态与白名单错误码；不得暴露路径、message、任意 Core details、SQLite 内容或 stderr。

完整错误映射（含请求校验、`BOOK_NOT_FOUND`、`BOOK_BUSY`、`BOOK_DELETE_CONFLICT`、`BOOK_DELETE_FAILED`、批量预检/清理错误、协议拒绝、ACL 拒绝及 host `CORE_UNAVAILABLE`）见 [M2-C1 §5.11](../../doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md#p09-ac3-delete-1-permanent-delete)。

## UI 确认与触发边界

唯一产品入口是回收站，书架不显示永久删除。用户勾选目标后，第二次确认显示确切作品身份、数量、删除范围与不可逆后果。确认复选框映射为 `confirm_permanent_delete: true`；前端将同一有序选择同时填入两个 ID 数组，并用相同数量填写 `confirm_count`，由 Core 再校验。

确认文案必须说明：App 回收站无法恢复；用户指定导出目录及文件会保留；全库历史备份不修改，旧备份可能含删除前快照。普通流程或后台任务不得隐式触发任一永久删除命令。

## 数据与文件后果

- 删除目标 Book 的当前内容行与项目状态：`books`、`chapters`、`pages`、`regions`、`region_revisions`、`media_artifacts`、`artifact_revisions`、`reading_progress`、`book_tags` 关系、Lock、current/pinned Revision 归属。共享 `tags` 与全局 metadata 保留。
- 保留 `pipeline_runs`、`pipeline_run_targets`、`pipeline_tasks`、`step_runs`、`step_run_input_refs`、`step_run_output_refs`、`step_result_candidates`、`pipeline_stage_states` 中的历史行。将其与删除的 Book/Chapter/Page/Region/Revision/Artifact 脱离，并清除资源 ID、路径和 locator；保留状态、操作类型、时间/顺序及安全结果/错误摘要。非终态或可恢复的 Run/Task 仍阻止删除。
- 用户源目录与源文件逐字节保留。只回收受控 root 下、可由清单/catalog 证明属于目标 Book 的 Managed Copy 和派生/缓存资源。不得删除用户指定导出目录内的文件。
- 不创建、检查、改写或删除全库历史备份。既有备份可能含旧数据库快照；本命令不承诺清理备份中的删除前内容。
- `export_history` 数据库行的处置、保留的 Pipeline 历史是否展示已删除作品标题仍未裁决。对应用户裁决写入 Task 前不释放实现。

## 兼容性与命令计数

前序请求面有 58 条命令。rev 2.9 增单条删除后为 59 条；rev 2.10 再加独立批量命令后为 60 条（53 production + 4 probe + 3 AC1）。前 58 条及 rev 2.9 单条命令的请求、结果、错误和 ACL 行为不变；只有批量命令及其错误字符串是新增项。Core major 仍为 2，minor `9→10`。旧 host 不注册批量 Tauri command；旧 Core 对未知批量命令 fail-closed。协议没有版本协商或自动回退。

`tauri-build` 通过 app manifest 生成批量权限文件和 schema 输出。本记录与契约只冻结 ACL 名称及注册方式，不授权 Rust/React/Core、capability 文件、生成权限、Schema/migration、测试或构建。

## 修改范围与验证

本次只更新以下文件：

- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`：rev 2.10、§3.2、command catalog、§5.11、§11/§12。
- `doc/tasks/P09-AC3-DELETE-1.md`：AC1 冻结、AC2/AC4/AC5 后果、证据 pin。
- `verification/P09-AC3-DELETE-1/contract-freeze-r2.md`：本记录。

没有修改产品代码、依赖、ACL/生成文件、Schema、`STATUS.md`、`REBASELINE_PLAN.md` 或 Coordinator 维护的 P20 文件。没有构建，也没有运行产品测试；先前工作区改动保持原样。

## 仍待用户裁决

1. `export_history` 数据库行是保留、删除还是脱离后保留；如保留，永久删除后的历史列表如何展示？
2. Pipeline 历史是否保留 Book 标题快照，还是统一显示“已删除作品”？

两项裁决完成且 Codex 更新实现 allowlist 前，AC2–AC7 不得开始实现。
