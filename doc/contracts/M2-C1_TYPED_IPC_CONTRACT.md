# M2-C1 — Typed IPC Contract

状态：文档冻结候选；独立 Review 前。版本：`1.1`（M2-C2 resource-channel revision；不代表已实现协议）。

## Revision history

- `1.1`（M2-C2，2026-09-26）：§10 新增 **10.1 Ruled resource-channel thresholds**（[M2-S1 §7 产品阈值裁决](../../verification/M2-S1/product-thresholds-ruling-67c3d56.md) T1–T7 落约）与 **10.2 Resource reference security semantics**（[M2-S1 报告](../research/M2-S1_RESOURCE_CHANNEL_SPIKE.md) R-001/R-002/§6.3 与 [M2-S2 报告](../research/M2-S2_SECURITY_VERIFICATION_SPIKE.md) S1-B11/S1-B12 结论落约：open-then-verify-from-handle 解析、不透明映射 ID、路径下发禁止、类型化错误码最小集）；§11 large-media 行更新为 `PARTIALLY RULED`。§1–§9 与 §12 语义不变；§10 新条款对 §8 `ErrorEnvelope.code` 的引用是值域使用，未改 §8 定义。全部新条款为**设计要求**（`RULED`/`TO-BE`/`UNVERIFIED` 标签，语义在 §10.1 头部定义），不代表已实现或已通过产品验证（`AS-IS: NOT_IMPLEMENTED` 不变）。
- `1.0`（M2-C1，2026-09-26）：原始冻结候选（blob `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`）。

## 1. 范围与证据等级

本文冻结未来 React ↔ Tauri ↔ Python Core 的 transport-neutral 消息边界。唯一产品权威是 Python Core；Python Core 执行业务校验并拥有 SQLite 持久化写入。Tauri/Rust 只负责传输、宿主权限与系统能力，不实现领域规则；React 只呈现 Core 查询投影并发送用户意图。

本文每个描述使用以下证据标签：

- **AS-IS**：固定基线 `eec1aa49d07119f0aa66ff461ebbb55e4595e624` 的代码、测试或已集成契约直接证明。
- **TO-BE**：AD-001 已决定的目标架构约束。
- **PROPOSAL**：M2-C1 为后续实现冻结的协议设计；尚无 runtime 支持。
- **UNKNOWN / UNVERIFIED / DEFERRED**：证据缺失、未验证或有待用户决定。

当前没有 Tauri、React ↔ Python IPC runtime、IPC schema、消息版本协商、事件重放或断线协议（**AS-IS: UNKNOWN / NOT_IMPLEMENTED**）。本文中的 envelope、命令和事件都是 **PROPOSAL**，不可作为实现已存在的声明。来源、行号、commit 和证据分类见 [`verification/M2-C1/source-trace.md`](../../verification/M2-C1/source-trace.md)。

## 2. 依赖方向及边界

```text
React presentation
  ├─ local interaction state (selection, filters, viewer mode, dirty text)
  └─ typed request / typed projection / typed event
          ↓
Tauri transport + host permissions (no domain logic, no DB writer)
          ↓
Python Core application services
          ↓
domain + ports + reusable infrastructure adapters
          ↓
SQLite (persistent authority; written only under Python Core)
```

- **TO-BE** Python Core 是业务、Revision、Lock、任务恢复和持久化权威；React 与 Rust 不直接访问 SQLite、用户文件或领域服务。来源：AD-001 “TARGET_INTENT and decision” 表（第 17–25 行）及 “Migration constraints” 第 6 项（第 35 行）。
- **AS-IS** 当前 QML/ViewModel 调用 Core 服务，任务投影已位于 `src/application/tasks/projection.py`，画布归一化坐标换算已位于 `src/application/editing/region_canvas.py`；这些不是 IPC runtime。M2-I2 的 UI 路径仅做兼容 re-export。
- **PROPOSAL** 所有请求在 Core 边界重新校验 ID、枚举、权限、当前 Revision/Lock 和状态转换；UI enablement 只用于体验，不代替校验。
- 作为 Qt-free seam 的 `application.tasks.projection` 与 `application.editing.region_canvas`，以及未来新增的 IPC-facing application contract/adapter，不得 import `src.ui` 或 PySide6，也不得以 UI adapter 实现规则。当前 `application.export.pdf_qt` 仍是已知 Qt 耦合，AD-001 将其列入后续 headless migration audit；本 Task 不改写该既有例外。基础设施依赖通过 application ports 注入；不得从 React/Rust 建立 SQLite writer。

## 3. Message envelope 与版本

以下类型是 **PROPOSAL**，用语言无关的 JSON-compatible primitive 表示，尚未选择具体序列化库：

```text
Request<T> = {
  protocol: "new-manga.core",
  version: { major: 1, minor: 0 },
  request_id: OpaqueId,
  command: CommandName,
  payload: T
}

Response<T> = {
  protocol: "new-manga.core",
  version: { major: 1, minor: 0 },
  request_id: OpaqueId,
  result: T | null,
  error: ErrorEnvelope | null
}

Event<T> = {
  protocol: "new-manga.core",
  version: { major: 1, minor: 0 },
  event_id: OpaqueId,
  event_type: EventName,
  emitted_at: Timestamp,
  payload: T
}
```

### 3.1 Type aliases

- `OpaqueId`: 非空 UTF-8 string；不得由 UI 拼装领域主键语义。Core 负责校验实体存在性。
- `Timestamp`: RFC 3339 UTC 字符串。时间精度、时钟源及排序保证尚未由现状验证；不可据此推导全局顺序。
- `PageId`、`BookId`、`ChapterId`、`RegionId`、`RunId`、`TaskId`：opaque ID string；`RevisionNo`：Core 返回的 integer，合法范围由对应 Region/Core 数据决定，不由 UI 推断。保持与领域对象 ID 字段一致；不把路径编码进实体 ID。
- `NormalizedPoint`: `{ x: number, y: number }`。Core 按现有规则先计算 `floor(n * size + 0.5)` 的 half-up 页面像素坐标，再将整数坐标 clamp 到页面边界 `[0, size]`；不先把归一化输入 clamp 到 `[0,1]`。page width/height 必须为正整数。
- Enum wire value 使用现有领域字符串值，未知 enum 值必须返回 typed validation error，不得静默降级。

### 3.2 Compatibility proposal

- `major` 不同必须在执行命令前拒绝，返回 `PROTOCOL_VERSION_UNSUPPORTED`；不得猜测兼容。
- 同 major 下 minor 可向前增加可选字段和新 command/event；接收端忽略未知可选字段，但未知 command/event/status 必须显式返回/保留 `UNKNOWN`，不能重解释成其他状态。
- 字段删除、改名、类型变化、枚举旧值语义变化或必填性变化属于 major 变更。
- 本 Task 未实现版本握手、协商、兼容矩阵或自动迁移（**AS-IS: NOT_IMPLEMENTED**）。`PROTOCOL_VERSION_UNSUPPORTED` 是拟议稳定错误码。

## 4. Request/response 语义

- 每个命令对应一个 `Request<T>` 与一个最终 `Response<R>`；同步响应表示 Core 已接受并返回明确结果，不表示长任务已完成。
- `request_id` 只做请求/响应关联。幂等键、重复提交抑制、超时后重试的 exactly-once 语义均 **UNKNOWN / NOT_FROZEN**；调用方不得在断线后盲目重放有副作用的命令。
- 查询返回不可变 DTO/Projection，不暴露 ORM、QObject、Python class pickle、数据库行对象或本地对象引用。
- 长任务创建返回 `RunAccepted { run_id, initial_status }`。后续进度由事件提示，规范状态通过 `GetRunSnapshot` / `GetTaskProjection` 查询。
- 错误响应满足 `result=null` 且 `error!=null`；成功响应满足 `error=null`。该互斥不变量是 **PROPOSAL**。

## 5. Typed command / query catalog

当前 Qt ViewModel 的方法不是一对一 IPC API。下表的 command name、payload/result DTO 均为 **PROPOSAL**；现有代码只证明“现有 ViewModel/Core service 有对应操作”，不证明 wire shape 或 IPC 已实现。页面选择、排序、过滤、查看器模式和未保存输入等纯前端交互留在 React 本地状态中。每行“现状”说明的是代码调用或领域服务存在性，不表示已经有 IPC。

| Name | Typed payload → result | As-Is evidence / To-Be boundary |
|---|---|---|
| `ListBooks` | `{}` → `BookSummary[]` | ViewModel 调 Library service 取书目；当前搜索、归档/收藏过滤、排序由 ViewModel 本地完成。AS-IS service call，IPC 未实现。 |
| `CreateBook` / `DeleteBook` | `{title, original_title?}` / `{book_id}` → `BookSummary` / `Unit` | `BookshelfViewModel.createBook/deleteBook` 调用 Library service。删除需 Core 检查关联和保留规则。 |
| `SetBookFavorite` / `SetBookArchived` | `{book_id, value: boolean}` → `BookSummary` | 对应 Library service 调用。 |
| `ListChapters` / `CreateChapter` / `DeleteChapter` | `{book_id}` / `{book_id,title,chapter_number?}` / `{chapter_id}` → `ChapterSummary[]` / `ChapterSummary` / `Unit` | ViewModel 使用 `list/get/create/delete_chapter`。 |
| `ImportPages` | `{chapter_id, sources: ImportSourceRef[]}` → `ImportReport` | 当前导入接受路径/URL 类来源；未来 IPC 必须由 Tauri host 授权并传递不透明、受限、可过期的 `ImportSourceRef`，不得把大型图片 bytes/Base64 放进 JSON。URI/token 具体形态 **DEFERRED to the runtime Task**；security/lifecycle semantics 现已 ruled in §10.1/§10.2（M2-C2）。 |
| `StartRun` | `{command: PipelineCommand, scope: PipelineScope, overrides?: JsonObject}` → `RunAccepted` | 当前 Workbench 依次调用 `PipelineService.create_run`、`plan_run` 并启动 worker。未来 handler 应先持久化并规划，再安排 Core 后台执行；精确 acceptance 时点是 Proposal，需 runtime Task 定义和验证。 |
| `GetRunSnapshot` | `{run_id}` → `RunSnapshot` | 从持久 Run 状态恢复查询的 **PROPOSAL**；`PipelineService` 能查 Run，IPC 查询尚未实现。 |
| `GetTaskProjection` | `{run_id}` → `TaskProjection` | `build_projection` 是应用层唯一投影，可含页面统计、焦点、步骤流、错误原因和控制按钮能力；禁止 UI 自行重算权威业务状态。 |
| `ControlRun` | `{run_id, action: pause\|stop\|continue\|restart\|abandon}` → `ControlResult` | `PipelineService.control_run` 为现有状态机权威。非法转换 typed failure。 |
| `RetryFailedTargets` | `{run_id}` → `RunAccepted` | `retry_failed_targets` 创建 source-linked 新 Run；无失败页面时返回现有 `TARGET_NOT_FOUND`。 |
| `CreateRegion` | `{page_id, shape: {kind:"rectangle", corners: [NormalizedPoint, NormalizedPoint]} \| {kind:"polygon", points: NormalizedPoint[3+]}}` → `RegionSummary` | 归一化换算使用 app `normalized_to_page_geometry`，几何校验在 Core；image/page bytes 不随命令传输。 |
| `DeleteRegion` | `{region_id}` → `Unit` | Workbench VM 调用 Region deleter；权限、Lock 与 revision 条件由 Core 检查。 |
| `SaveManualTranslation` | `{region_id, text, expected_revision?: RevisionNo}` → `{revision_no: RevisionNo}` | Workbench VM 当前调用编辑 service 保存手工译文。`expected_revision` 是防覆盖 Proposal，精确并发策略 **UNKNOWN**。 |
| `ListRegionRevisions` / `RestoreRegionRevision` / `SetRevisionPinned` | `{region_id}` / `{region_id, revision_no}` / `{region_id, revision_no, pinned}` → `RevisionSummary[]` / `RegionSnapshot` / `Unit` | `RegionRepository` port 的 `list_revisions` 读取历史；编辑 service 提供 `restore_revision` 与 `set_revision_pinned`。具体 ViewModel/QML 可见性并不完整。锁/Revision 保护要求来自 AD-001；任何操作的资格检查归 Core。 |
| `GetReaderProjection` / `SaveReadingProgress` | `{chapter_id}` / `{chapter_id, page_id?, scroll_offset?}` → `ReaderProjection` / `Unit` | Reader VM 读取章节页并保存滚动偏移；page navigation、display mode 为 presentation state。 |
| `GetSettings` / `SaveSettings` | `{section?}` / `{section, values}` → `SettingsProjection` / `SettingsProjection` | AS-IS 仅证明 Settings VM 在进程内调用 profiles/defaults/credentials services；没有已定义的 `CredentialRef` 类型或 IPC exchange。Credential DTO/exchange 为 UNKNOWN / DEFERRED；secret 不得进入普通事件或日志。 |
| `StartExport` / `CancelExport` | `{export_request: ExportRequestDto}` / `{export_id}` → `ExportAccepted` / `Unit` | ViewModel 调 Export service 与本地 worker；实际输出文件选择/宿主能力需后续 host contract，当前导出 IPC 未实现。 |

### 5.1 Task command types

`PipelineCommand` wire enum 复用现有 `CommandType` 字符串：

`translate_all`, `translate_untranslated`, `translate_selected`, `translate_single`, `rerender_all`, `rerender_selected`, `rerender_single`, `reinpaint_all`, `reinpaint_selected`, `reinpaint_single`, `reocr_all`, `reocr_selected`, `reocr_single`, `ocr_region`, `retranslate_region`, `retranslate_region_full`, `reinpaint_region`, `rerender_region`.

`PipelineScope` 为带判别字段的联合：

```text
{kind:"book", book_id}
| {kind:"chapter", chapter_id}
| {kind:"page_selection", page_ids: PageId[]}
| {kind:"page", page_id}
| {kind:"region", region_id}
```

Core 必须验证 command/scope 配对；Task contract 不授权新增命令类型。没有传入可选 override 时使用当前冻结设置快照，不能让 UI 改写历史 Run 的快照。

### 5.2 UI-local actions

以下现有交互只改变前端/页面状态，**不单独成为 Core command**：Workbench `selectPage`, `stepPage`, `togglePageSelected`, `selectRangeTo`, `clearSelection`, `setPageFilter`, `filterByStatus`, `locatePipelinePage`, `setViewerMode`, `setInspectorText`, `selectRegion`, `resolveDirtyConfirm`；Bookshelf search/filter/sort/view mode；Reader `nextPage`, `previousPage`, `jumpToPage`, display mode；Export 表单编辑。若未来动作写持久状态，则必须提升为有类型 Core 命令，不得用通用 property bag 隐式写入。

## 6. Typed projections 与 events

### 6.1 Task projection

**PROPOSAL — wire DTO。** 下列 `TaskProjection` 是候选传输形状，不是现有 DTO 的逐字段序列化，也不代表 IPC 已实现。AS-IS 来源是 `application.tasks.projection.TaskProjection` 的扁平 dataclass 字段（包括 `extra: Mapping[str, str]`）；本 Proposal 将 page counts 归组到 `counts`、`can_*` 能力归组到 `controls`，把 tuple 序列化为数组，并把 `step_flow` 三元组表达为具名对象。除显式列出的结构重组外，源字段不得遗漏：

```text
run_id: RunId
run_status: PipelineRunStatus
run_title: string
overall_progress: number             # 0..1，terminal/planned step units
current_page_id: PageId | null
current_step_type: string
step_flow: StepFlowItem[]             # {type,label,state}
rows: PageProjectionRow[]
counts: {total,completed,failed,skipped,blocked,waiting,processing}
blocked_reasons: string[]
controls: {can_pause,can_stop,can_continue,can_restart,can_abandon,can_retry_failed}
extra: Record<string, string>
```

字段映射（左侧为 AS-IS dataclass，右侧为本节 PROPOSAL wire DTO）：

| AS-IS flat field(s) | PROPOSAL wire field | Mapping |
|---|---|---|
| `run_id`, `run_status`, `run_title`, `overall_progress`, `current_page_id`, `current_step_type` | 同名字段 | 原样保留字段语义；wire scalar encoding 仍需由 runtime contract 定义。 |
| `step_flow: tuple[tuple[str, str, str], ...]` | `step_flow: StepFlowItem[]` | 每个 `(type, label, state)` tuple 改写为 `{type, label, state}` 对象。 |
| `rows: tuple[PageProjectionRow, ...]` | `rows: PageProjectionRow[]` | tuple 序列化为数组；行字段为 `page_id`, `page_order`, `filename`, `status`, `is_locked`, `is_pipeline_current`, `error_code?`。 |
| `total_page_count`, `completed_page_count`, `failed_page_count`, `skipped_page_count`, `blocked_page_count`, `waiting_page_count`, `processing_page_count` | `counts: {total, completed, failed, skipped, blocked, waiting, processing}` | 仅分组与缩短 wire key；逐项分别对应上述 count 字段。 |
| `blocked_reasons: tuple[str, ...]` | `blocked_reasons: string[]` | tuple 序列化为数组。 |
| `can_pause`, `can_stop`, `can_continue`, `can_restart`, `can_abandon`, `can_retry_failed` | `controls: {can_pause, can_stop, can_continue, can_restart, can_abandon, can_retry_failed}` | 嵌套分组；逐项同名映射。 |
| `extra: Mapping[str, str]` | `extra: Record<string, string>` | 保留额外字符串键值；序列化为 JSON object。 |

Progress 分母/分子使用 step units；不得换成已处理页数/总页数。页面优先级为 `failed > processing > blocked > completed > skipped > waiting`；此优先级是 Page row 归并，不改变 Run `status`。

### 6.2 Event catalog

以下为 **PROPOSAL** 的 typed invalidation/progress event；事件是状态变化通知，不代替快照：

| Event | Payload | Evidence level |
|---|---|---|
| `RunStatusChanged` | `{run_id, status: PipelineRunStatus, changed_at}` | 当前 Qt VM 有 `runStatusChanged`、`runFinished` 信号；IPC event 未实现。 |
| `RunProgressChanged` | `{run_id, projection: TaskProjection}` | 当前 Qt VM 用 timer refresh projection 并 emit `taskProgressChanged`；IPC event 未实现。可在实现中改为 revision/cursor 失效通知，但须保留可重取快照。 |
| `RunFinished` | `{run_id, final_status}` | 当前 RunController/VM 有 finished 信号；IPC event 未实现。 |
| `RunCrashed` | `{run_id, error: ErrorEnvelope}` | 当前 UI crash signal 只有 text；将结构化错误带入 IPC 是 Proposal，现存 crash 未映射到稳定业务 code。 |
| `CoreAvailabilityChanged` | `{state: starting\|ready\|stopping\|unavailable, reason?: ErrorEnvelope}` | **UNKNOWN / PROPOSAL**；当前 Core process/session event 不存在。 |
| `ImportProgressChanged`, `ExportProgressChanged` | `{operation_id, completed?, total?, status}` | **UNKNOWN / PROPOSAL**；现有 UI 有 import summary/export worker signals，但跨进程传输没有验证。 |

当前 Qt signal 名称不是 wire contract，未来不得以 QVariant/QObject 对象作为消息类型。

## 7. Lifecycle、断线与恢复

### 7.1 Existing Run state

AS-IS `PipelineRunStatus` 的值为 `pending`, `running`, `paused`, `blocked`, `completed`, `completed_with_failures`, `failed`, `cancelled`, `interrupted`。Task/Page 投影的值域另有 `waiting`, `processing`, `completed`, `failed`, `blocked`, `skipped`。两者是不同状态域：Run 级 `blocked` 不能作为 Page 的 glyph/交互定义。

AS-IS `PipelineService` 的控制行为：

- `pause`: Run 只可从 `pending`/`running` 暂停；两种状态都会先设置并持久化 `pause_requested=True`。pending 同步转为 `paused`；running 暂留 `running`，由执行循环在协作检查点观察该标志后转为 `paused` 并持久化。
- `stop`: 已 completed/completed_with_failures/failed/cancelled 的 Run 拒绝；pending/paused 可被立即取消，运行中设置 cancel request。
- `continue`: paused 变成 pending；interrupted 重新规划并继续；其他状态返回 `INVALID_RUN_TRANSITION`。
- `restart`: 仅 interrupted 有效，创建带 `source_run_id` 与 `retry_reason` 的新 Run，旧 Run 标记 restarted disposition。
- `abandon`: 仅 interrupted 有效，旧 Run 转为 `cancelled` 并设置 `termination_reason="abandoned_after_interruption"`；不会设置 `interruption_disposition`。该 disposition 字段由 `restart` 写入 `"restarted"`。
- `retry_failed_targets`: 根据失败 Page 创建 linked 新 Run；没有失败 Page 返回 `TARGET_NOT_FOUND`。
- `recover_running_runs`: 启动恢复时将持久化 `running` Run、Task 与 Step 转为 `interrupted` 并保存。

上述规则由 `PipelineService` 负责。前端控制按钮是方便操作的投影；Core 必须对每次控制请求再次验证合法转换。

### 7.2 Proposed transport lifecycle

1. Core startup 完成应用装配与既有恢复逻辑后才向 host 发 `CoreAvailabilityChanged(ready)`。当前启动握手顺序 **UNVERIFIED**。
2. 客户端订阅前先调用 `GetRunSnapshot` / `GetTaskProjection`；事件漏失、重复或重排时，以重新取回的快照为准。
3. 传输断开不等于取消/暂停 Run。重连后重新读取 Core 状态；不自动重放副作用命令。
4. 当前不承诺事件至少一次/至多一次、稳定序列号、历史事件回放、订阅确认或进程重启存活保证；这些具体传输性质留待 M2-S1/Runtime 设计与测试。
5. 长任务工作线程/取消令牌映射是实现责任。当前 QML RunController 使用 QThread，但没有跨进程控制语义可迁移为现状保证。

## 8. Error envelope

以下为 **PROPOSAL**；不得丢掉源 code。`category` 是传输层粗分类，原始 `code` 保持 Core 原值。

```text
ErrorEnvelope = {
  code: string,                        # 源稳定 code；未知时保留原始字符串
  category: validation | not_found | conflict | unavailable | cancelled | internal | unknown,
  message?: string,                    # 面向调用方的安全短消息；不得含 secret/本地绝对路径
  retryable: true | false | unknown,
  details?: ErrorDetail[]              # typed field/path issue；默认不返回堆栈或任意对象
}
```

已观察到的错误表达：`PipelineError(ValueError)` 带 `.code` 与 `.detail`；Run Service 观测到 `INVALID_RUN_TRANSITION`, `RUN_NOT_INTERRUPTED`, `TARGET_NOT_FOUND`；画布使用 `RegionCanvasError` code；step 执行记录 `error_code`。部分 SQLite/导出/设置错误没有统一序列化代码。未知或未映射错误应使用 `category="unknown"` 和源错误 code（如不存在稳定 code，则 `code="UNKNOWN"`、附 correlation id），不得伪装为 validation 或 network error。

| Source code/example | Proposed category | Mapping confidence |
|---|---|---|
| `INVALID_RUN_TRANSITION` | `conflict` | Source code is stable in Core; taxonomy mapping is Proposal. |
| `RUN_NOT_INTERRUPTED` | `conflict` | Source code observed; taxonomy mapping is Proposal. |
| `TARGET_NOT_FOUND` | `not_found` | Source code observed in Run service; some current uses mean invalid scope, so mapping may need richer subcode. |
| `RegionCanvasError.code` | `validation` | Preserve exact code; enumerate from source/test before runtime schema is generated. |
| unclassified Python exception / worker crash | `unknown` or `internal` | Exact mapping/redaction policy **UNKNOWN**; never leak traceback to UI. |

`retryable` defaults to `unknown` unless Core has an evidence-backed decision. `message` is diagnostic text, not a stable programmatic selector. UI branches on `code` / `category`, never English text.

## 9. Region geometry contract

AS-IS `normalized_to_page_geometry(points, page_w, page_h)` owns conversion in application and returns domain `RegionGeometry`. Each coordinate is converted using half-up rounding `floor(n * size + 0.5)` then clamped to page bounds; do not use Python `round()`.

- 2 distinct points form rectangle corners; input order may vary.
- 3 or more points form a polygon preserving the input ring order.
- zero-area rectangles, collapsed/zero-area polygons, collinear polygons, missing/non-positive page dimensions, and fewer than two points raise typed `RegionCanvasError` with stable `.code`.
- UI adapter must map/reject typed `RegionCanvasError`; raw `ValueError` must not escape as an untyped UI error.
- Full code-to-message mapping is source-driven and may be generated from current `RegionCanvasError` definitions/tests. Do not add a protocol-side geometry implementation.

## 10. Data protection and large media

- Python Core alone is authoritative for business facts and SQLite writes. Commands carry IDs and small metadata; Core resolves current state and enforces revision/lock invariants at commit time.
- Never overwrite or mutate original source files. Managed Copy writes/derivatives remain under Core-controlled storage; do not treat a frontend path as permission to write.
- Preserve human edits, `Lock`, current Revision, pinned Revision, and recoverable task state across commands, errors, retries, cancellation and reconnect. Lock/revision decisions must be checked at the write boundary, not trusted from stale UI projections.
- Do not encode large images, Webtoon page/tile resources, or model weights in ordinary JSON/Base64 IPC. No IPC command/event in this contract accepts those byte arrays.
- This contract does not pick file URI/token, OS handle, shared-memory, streaming, tile or chunk transport. Capacity, permission, lifecycle, cleanup, threat model and recovery must be independently spiked and verified before any large-media command is released.
- Import sources may use only Core/host mediated, scoped references; their security and lifecycle semantics are now ruled in §10.1 (T5/T6) and §10.2, while the exact wire value-object form remains **DEFERRED** to a future runtime Task.
- Credentials/secrets are excluded from ordinary DTOs, event payloads, errors and logs. Credential storage remains host/Core secure flow; exact typed secret exchange is **UNKNOWN** pending credential contract.

### 10.1 Ruled resource-channel thresholds (M2-S1 §7 product threshold ruling, T1–T7)

**RULED** 标签语义（本节局部定义，补充 §1 的既有标签；不改变其含义）：条款来自 2026-09-26 的
[M2-S1 §7 产品阈值裁决](../../verification/M2-S1/product-thresholds-ruling-67c3d56.md)（用户授权的治理决定）——作为**未来大媒体 runtime Task 的验收线需求输入**具有约束力；它既不是现状证明（不用 `AS-IS`），也不是 AD-001 决定（不用 `TO-BE` 单独标注），且**没有任何条款代表已实现**（`AS-IS: NOT_IMPLEMENTED` 整体保持）。产品验收在 runtime Task 执行；本修订不授权任何 runtime 实现。

每条来源锚点为裁决编号（`T#`）；逐条与裁决原文的追溯见 `verification/M2-C2/clause-source-trace.md`。

- **RULED（T1）— 单资源字节上限**：A single resource (a single page or a single Webtoon tile) must be servable up to **256 MiB**; a larger resource must be rejected with a typed error (suggested stable code `RESOURCE_TOO_LARGE`) and no partial delivery. The 64 MiB value used by M2-S1 probes remains a probe configuration, not a product threshold. The default may be revised by a runtime Task after re-measurement, but changing the *commitment line* itself requires a new ruling.
- **RULED（T2）— 并发资源与订阅者**：The channel must support **≥ 32 active references** and **≥ 16 concurrent subscribers per resource**; exceeding either returns a typed throttling error rather than unbounded silent queueing.
- **RULED（T3）— 首帧延迟预算（含未测标注）**：For a typical page (≤ 25 MiB) the *channel-layer* first-byte-to-host budget is **≤ 200 ms P95 with a hot OS file cache**, and **≤ 1 s P95 as the cold-cache target**; first frame excludes image decoding and rendering. **诚实边界：冷缓存 1 s 是目标值——S1-B6（冷缓存实测）为 `NOT_RUN`，在 S1-B6 复测完成前该值不得表述为"达标"**；热缓存 200 ms 同为预算承诺，产品实测验收归 runtime Task。
- **RULED（T4）— 内存预算**：Core-side peak additional memory per resource ≤ resource bytes + 64 MiB (streaming/chunked implementation target: resident buffer ≤ 32 MiB); host ≈ 0 incremental via the out-of-band route, ≤ 32 MiB bounded buffer via a streaming route. Materializing a whole resource as Base64/JSON is prohibited (reiterating the existing §10 prohibition as an acceptance line, per ruling T4).
- **RULED（T5）— 分层信任与路径暴露**：
  1. The React/WebView layer must never touch any OS path (neither user source files nor derived caches); bytes are delivered only through restricted asset URLs (Tauri asset-protocol *form*; its verification status is `NOT_RUN`, S1-B1).
  2. The Tauri host is a trusted layer: it may hold restricted references and resolve *derived-cache* relative paths, and must not forward absolute paths to the WebView.
  3. Core approvals must not return user-source absolute paths to any layer; a `user-source` scope must have no frontend-visible implementation.
  4. The WebView-visible part of a resource reference must be an opaque mapping ID (see §10.2).
- **RULED（T6）— 引用生命周期**：A resource reference is bound to `resource_id` + a revision fingerprint; the default TTL is **300 s with sliding renewal** (active consumption auto-renews); revision switch, deletion, pin release and management operations trigger **immediate revocation** (the next resolve returns a typed `REF_REVOKED`); an already-opened handle/stream for the current consumption is not forcibly interrupted. TTL 300 s 是默认配置，产品可配置。
- **RULED（T7）— 模型权重独立通道**：Model weights travel over an independent channel with an independent lifecycle; they do not share the page/tile reference channel, and T1–T4 thresholds and T6 TTL/revocation semantics do not apply. Weight loading is a Core-side controlled read (with hash verification) at startup/first use and never passes through the frontend reference mechanism. The concrete transport mechanism (direct controlled file read vs streaming) and packaging/sandbox impact (S1-B8, `NOT_RUN`) are left to the runtime Task.

### 10.2 Resource reference security semantics (M2-S1 R-001/R-002; M2-S2 S1-B11/S1-B12)

本小节条款是**设计要求**，不是已验证的产品保证：M2-S2 在隔离原型层验证了该方向（TOCTOU 16 场景、映射 ID 8 场景全 PASS），但 **S1-B11 的产品级防护保持 `UNVERIFIED`**（S1-B3 DACL/完整性级别、S1-B8 打包/沙箱复跑均未做）；落约的是设计要求本身。M2-S2 证据的归纳性边界（如映射 ID 不透明性证明）原文适用，逐条对照见 `verification/M2-C2/clause-source-trace.md`。

- **RULED/TO-BE（M2-S1 §6.3 条 3、§8.1 限定 1，M2-S2 §3）— 引用解析必须 open-then-verify-from-handle**：A runtime implementation must resolve a resource reference by opening the target **once** and verifying **from that handle**: containment (final path re-derived from the handle must stay inside the scope root), file identity, and size (issue-time facts plus the T1 limit) — on Windows with `FILE_FLAG_BACKUP_SEMANTICS` and reparse handling as needed; then read **only through that handle**; verify the content digest against the issue-time digest (covers an equal-size in-place rewrite that identity and size cannot see) and re-check identity after reading. A check-then-use flow (validating a path, then opening it in a separate operation) must not be the security boundary. `S1-B11` release conditions ③ (target packaging/sandbox re-run) and ④ (DACL/integrity level, S1-B3) remain `NOT_RUN` and are prerequisites for any product-level security claim.
- **RULED/TO-BE（M2-S1 F-01/R-002/§6.3 条 4，M2-S2 §5，裁决 T5.4）— WebView 层引用保密 = Core 侧不透明映射 ID**：The reference visible to the WebView layer must be an opaque, random mapping ID resolved by a Core-side table; it must not encode or otherwise reveal any path or resource identifier. The Core↔host trusted-layer reference format is exempt from this clause. **The encrypted-payload alternative is closed by ruling T5.4**; reopening it requires a new ruling (i.e., only if the mapping-ID approach is proven infeasible).
- **RULED/TO-BE（M2-S1 §6.3 条 2，裁决 T5，明确化既有 §10 语义）— 绝对路径下发禁止**：User-source absolute paths must not be sent down through IPC to any layer (Core approvals, host, or WebView); derived-cache relative paths may exist only inside the trusted host/Core layers, never in WebView-visible material.
- **TO-BE（M2-S2 §3/§4/§5 实测提取）— 类型化错误码最小集**：Resource-reference resolution must surface a stable typed error-code minimum set, riding the §8 `ErrorEnvelope.code` field (no change to §8's definition): `REF_MALFORMED`, `REF_SIGNATURE_INVALID`, `REF_EXPIRED`, `REF_REVOKED`, `REF_UNKNOWN_ID` (mapping-ID miss), `REF_SCOPE_DENIED`, `REF_READ_ONLY`, `REF_OUT_OF_SCOPE` (lexical, absolute-path and handle-derived containment escapes), `REF_REPARSE_POINT`, `REF_NOT_FOUND`, `RESOURCE_TOO_LARGE` (T1 channel-level limit, suggested code), `MEDIA_TOO_LARGE_BY_HANDLE`, `FILE_IDENTITY_CHANGED`, `FILE_SIZE_CHANGED`, `CONTENT_DIGEST_MISMATCH`, `OPEN_FAILED_SHARING_VIOLATION`. Error responses must never leak mapping-table entries or paths (§8 `message` constraint; M2-S2 M-05). Runtime Tasks may add codes but must preserve these semantics; wire naming may be refined in a later contract revision without weakening the semantics.
- **RULED（T7，条款正文见 §10.1）**：模型权重独立通道——不与页/tile 共用引用通道，不适用 T1–T4 与 T6 语义。

## 11. Explicitly deferred / undecided

| Decision | Status | Contract treatment |
|---|---|---|
| Page-level `blocked` UI meaning, glyph, copy and behavior | `DEFERRED / USER_DECISION_REQUIRED` | Page projection may carry typed status `blocked`; do not reuse Run `blocked` UI mapping (`⊘`, `⏸`, or any other glyph). No user-visible behavior is selected here. |
| React UI Owner | `DEFERRED / USER_DECISION_REQUIRED` | This Task does not select an owner. |
| Large-media transport and import path capability | `PARTIALLY RULED` (M2-C2) | Thresholds (T1–T7, §10.1) and security semantics (§10.2) were ruled at M2-C2 from the M2-S1 §7 ruling and the M2-S1/M2-S2 spikes. The runtime form remains `DEFERRED` to a future runtime Task: transport selection stays conditional (M2-S1 §8.1), the Tauri asset protocol is `NOT_RUN` (S1-B1), and S1-B11 product-level protection is `UNVERIFIED` (S1-B3/S1-B8 outstanding). |
| Runtime serialization library, Tauri command names, process supervision, auth/permission handshake | `UNKNOWN / NOT_IN_SCOPE` | No implementation claimed; separate runtime Task must decide against this transport-neutral contract. |
| Event ordering/replay/retention and idempotency | `UNKNOWN / NOT_FROZEN` | Snapshot resync is the safe proposal; stronger guarantees need runtime tests. |
| Lock/revision conflict response details and concurrent edit policy | `UNKNOWN` | Core remains authority; later contract may refine typed conflict details without weakening protection. |

The UI mapping decision does not block freezing a transport-level Page status distinct from Run status. Any proposal to alter the status value or user-visible mapping returns to the user; M2-C1 does not resolve it.

## 12. Release boundary

This document freezes design only. It does not authorize Python IPC Runtime, Tauri, React, QML changes, SQLite/Schema changes, dependencies, M2-S1, data transport selection, or integration. A successor implementation Task must reference this contract, identify its owner and scope, and verify the runtime semantics it implements.
