# M2-C1 — Typed IPC Contract

状态：文档冻结候选；DSH 独立 Review r1（changes_requested）返修已落，待复核。版本：`1.5`（**草案**——`1.5`（M2-WORKBENCH-REACT-1）：`ListRegions` 读取面 additive widening——`RegionListSummary` 可选 `geometry` 字段 + result 包装可选 `page_size` 投影字段，D5 读取面几何缺口闭合；协议 minor 不 bump，见 Revision history `1.5`。含 `1.4` 草案——M2-REGION-RETYPE-CONTRACT：`SetRegionType`/`ListRegions` wire shape、EV-8 policy 快照裁决、并发与人工覆盖语义、持久性语义、「忽略」定义；含 r1 返修文本修订。含 `1.3` M2-SETTINGS-IPC-CHANNEL 产品 Tauri settings 通道 `settings_get`/`settings_update_section` wire shape 授权登记。均不代表更广协议已实现）。

## Revision history

- `1.5`（M2-WORKBENCH-REACT-1，2026-10-06）：**授权契约修订（additive widening，协议 minor 不 bump）**（[Task](../tasks/M2-WORKBENCH-REACT-1.md)，用户 2026-10-06 释放候选 A 的 AC1 授权）——闭合 UI 设计稿 D5 读取面几何缺口（M2-SFX-MISROUTE-UI-MITIGATION §5 D5 行「缺失（读取面，归入 RC-3）」由本修订承载）：①§5.4 `ListRegions` result 的 `RegionListSummary` 追加**可选** `geometry` 字段（`{bbox: [x,y,w,h], polygon: [[x,y],...]}`，全部为归一化 0..1 值，反算定义 `normalized := pixel / size`——与 §9 正向 half-up 规则 `floor(n*size+0.5)` round-trip 精确自洽；单一数学权威 `application/editing/region_canvas.py` 正反向同文件）；②`ListRegions` result 包装对象追加**可选** `page_size: {width, height} | null`——页面像素尺寸投影（RegionOverlay letterbox 数学的「尺寸只从投影取」硬规则承载，M2-UI1 §2.2；`page_id` 未命中任何 page 时为 `null`，沿 `1.2`/§5.3 frozen-None 通道语义先例，footnote a 的无 page 存在性检查语义不变）；③**协议 envelope minor 维持 `3` 不 bump**：本修订零新命令、零新错误语义、零既有字段语义变化，纯可选字段扩展——§3.2 同 major「接收端忽略未知可选字段」即兼容 widening，`core_service.py` 既有 minor bump 注记惯例均对应「commands added」，如实登记本次不适用；旧 Core（不返回新字段）与旧读取端（忽略未知字段）双向兼容；④错误码映射表、C1–C7/P1–P4 断言、`SetRegionType` 全部零变化；⑤`geometry` 属 region 读取面的展示几何通道，不携带训练语义（§5.4 读取面取舍定案的原边界对 `geometry` 扩容面继续适用：suspect/review_state/文本仍不在读取面，RC-1/RC-4/RC-5 候选保持登记）。实施落点：`core_service.py` handler 注入 page 尺寸、`editing/service.py` 组装可选字段。
- `1.4`（M2-REGION-RETYPE-CONTRACT，2026-10-04，**草案——runtime 未实现**）：**授权契约修订草案**（[Task](../tasks/M2-REGION-RETYPE-CONTRACT.md)，用户裁决 `user_ruling_2026-10-04_训练质量效率优先_许可降权备案`）——新增 **§5.4 Region retype and read channel**：①`SetRegionType` 改标命令（改标=经既有 commit seam 产生一笔新 revision，origin 恒 `user`；`expected_revision` 乐观守卫可选；响应含 `revision_no` 与改标后生效态，沿 `SaveManualTranslation` result 先例与 §5.3 一次往返先例）；②`ListRegions` 读取面（`RegionListSummary` 最小 DTO（r1 定名，原表述 `RegionSummary`）：region_id/region_type/sfx_policy/origin/revision_no；读取面不含几何/文本/标注状态等训练语义；取舍定案=新命令而非扩容既有命令，理由见 §5.4）；③错误码零新错误语义（wire `code` 字面量全部复用既有导出；复用 `INVALID_REQUEST`/`INPUT_REVISION_CHANGED`/`TARGET_NOT_FOUND`/`UNKNOWN` 既有 typed 族，映射表见 §5.4）；④**EV-8 裁决（RULED）**：改标后 policy 快照=「按改标时全局配置重快照」（改标为 sfx）/「强制 skip」（改标为非 sfx），理由与技术事实链见 §5.4；⑤并发与人工覆盖语义（AI 任务运行期间人工改标：人工优先、AI 侧 fail-closed、Revision/Lock 守卫交互）与持久性语义（项目重开/重检测/撤销）落为可测断言 C1–C7/P1–P4；⑥「忽略」定案为**处理动作/过滤状态**（非领域类型），`RegionType` 六值枚举零新增。§5 表新增 `SetRegionType`/`ListRegions` 两行（`1.4` 指针）；§11 两行注记更新（Tauri command names 行、Lock/revision conflict 行）。协议 envelope minor 目标 `2` → `3`（同 major 向后兼容 widening，沿 `1.2`/`1.3` 先例；**runtime 未实现**，bump 由实现 Task 落地）。**本修订不授权 runtime 实现**（§12 release boundary 原文不变；实现由后续释放的 Task 承接）；§1–§4 与 §6–§10 既有保护语义零放松。**r1 返修（2026-10-04，DSH 独立 Review changes_requested 后同分支文本修订，裁定内容零变更——EV-8/「忽略」/错误码复用集/C1–C7/P1–P4 断言语义不变）**：P1-1 `ListRegions` result 统一为包装对象 `{"regions": …}`（§5 表行以 §5.4 为准）；P2-1 AC5 理由链继承分支自愈表述修正（再改标不脱离继承语义）；P2-2 AC4 依据改 Task 合同语境+明示设计稿无「忽略」表述+R-015 限定为同属闭集纪律；P2-3 机器改标溯源锚点修正为 `origin`+检测步 provenance/StepResult（`source_run_id` 不在 region 创建写路径）；P3-1 改标 revision `review_state=UNREVIEWED` 定案；P3-2 读取面 DTO 更名 `RegionListSummary`；P3-3 「零新码」收紧为「零新错误语义」+wire `code` 大小写字面量定案+`LOCK_CHANGED` 消歧脚注；P3-4 `page_id` 不存在归类空列表+脚注 a；P4-1 `expected_revision` 与 `SaveManualTranslation` 交叉指针；P4-3 错误码表覆盖范围表头注记。**runtime 落地注记（M2-REGION-RETYPE-CORE done @merge `d8019810`，`1.5` 时回填）**：两命令 runtime 已由实现 Task 交付（`core_service.py` `PROTOCOL_MINOR=3`、handler :630-716、dispatch :1001；Tauri `PRODUCTION_COMMANDS` 恰 9 命令），本节自 `1.5` 起不再是「runtime 未实现」状态。
- `1.3`（M2-SETTINGS-IPC-CHANNEL，2026-10-02）：**授权契约修订**（[Task](../tasks/M2-SETTINGS-IPC-CHANNEL.md)，用户裁决① `user_ruling_2026-10-02_three_confirmations`）——新增 **§5.3 产品 Tauri settings 通道**：`settings_get` / `settings_update_section` 两命令的 wire shape（请求/响应/错误码）与写入端前置校验纪律；§5 表 `GetSettings`/`SaveSettings` 行加 `1.3` 指针（transport-neutral 命令名保持 PROPOSAL 不变，产品 Tauri 面以 §5.3 为准）；§11 "Tauri command names" 行注记该两命令名已由本修订裁决。协议 envelope minor `1` → `2`（Python `core_service` 侧命令面新增，沿 M2-PROD-DETECT-3 `core.detect` 先例：同 major 向后兼容 widening，既有命令 `core.ping`/`ListBooks`/`core.detect`/`core.shutdown` 的 payload、result 与错误码不变）。写入端前置校验（typed fail-closed，持久化前拒绝）是 M2-SFX-ENTRY r1 R4 教训（写入端零校验 → 装配期阻断不可自愈）落约：`sfx.policy` 三值校验为首个实例。

- 集成例外登记（M2-PROD-DETECT-3，2026-10-01，acting Codex 集成裁决；仅登记例外，不改任何既有条款正文）：**§10 例外**——`core.detect`（协议 `new-manga.core` 1.1 新增命令，M2-PROD-DETECT-3 交付）登记为 **verification/tooling surface**：本地 stdio 单进程 spawn（无网络面）、单页 base64 上限 32 MiB（base64 解码后文件字节）+ 解码像素上限（32 MiB RGB24 等效）、provider 输出直通不写库、Tauri host 不注册该命令（产品 UI 的 detect 仍走 pipeline）。不构成 §10 产品大媒体通道先例：任何产品大媒体命令仍须 §10 要求的独立 spike（容量/权限/生命周期/威胁模型）与独立授权。**§8 注记**——core.detect 错误 envelope 的 `category` 采用最小映射（provider 输入门 `INVALID_INPUT` → `validation`，其余 ProviderError → `internal`，未映射异常维持 `internal`/`UNKNOWN` 现状）为 Proposal 级口径，与 §8 分类表的最终对齐沿用既有同源登记（M2-IPC1 r2 P3-4）；`message` 一律为固定安全短句（不得含本地绝对路径——provider 错误原文细节只走 stderr），即 §8 `message` 约束在该面强制生效。
- `1.2`（M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN，2026-09-29）：**授权契约修订**——§5 `ListBooks` 结果 DTO `BookSummary.page_count` 由 `int` widened 为 `int | null`（[Task 冻结裁决](../tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md)：None 通道）。语义：production COUNT 谓词（GROUP BY 仅覆盖有 ≥1 合格页的书）对某书无行的（无章、有章无合格页——含页行损坏被谓词排除的情况）→ `null`（unknown：数据不可用/未统计/导入未完成）；有合格页的书 → 真实计数 int。**known-0 通道保留**：SQL 数出的 0（若有）保持 JSON number `0`，与 `null` 序列化后可区分（单测锁定，三侧：Python/Rust/TS）；当前 production 谓词下无 known-0 场景属语义事实。命令名、payload、错误码与命令面清单不变（仅本字段 widening；§3 版本规则下属类型变化，由本授权 Task 承接，例外指针见 §3.2）。三侧落地：Python `BookSummaryDto.page_count: int | None`、Rust `library_bridge.rs` `BookSummary.page_count: Option<u32>`（serde → `null`）、TS `types.ts` `page_count: number | null`；`LibraryPanel` 对 `null` 渲染非数字占位（`—`），不得渲染为 `0`。
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
- 字段删除、改名、类型变化、枚举旧值语义变化或必填性变化属于 major 变更。**例外**：经授权 Task 在 Revision history 登记的 nullability widening（`T → T | null`）不升 major，现仅有 §5 `ListBooks` 的 `BookSummary.page_count`（`1.2` 修订，[M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN](../tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md)）；1.1 版消费者遇 `null` 属该登记修订的授权破坏面。
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
| `ListBooks` | `{}` → `BookSummary[]` | ViewModel 调 Library service 取书目；当前搜索、归档/收藏过滤、排序由 ViewModel 本地完成。AS-IS service call，IPC 未实现。**`1.2` 修订（M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN）**：`BookSummary.page_count: int \| null`——COUNT 谓词无行的书 → `null`（unknown），有合格页的书 → 真实计数；known `0` 与 `null` 可区分（详见 Revision history `1.2`）。 |
| `CreateBook` / `DeleteBook` | `{title, original_title?}` / `{book_id}` → `BookSummary` / `Unit` | `BookshelfViewModel.createBook/deleteBook` 调用 Library service。删除需 Core 检查关联和保留规则。 |
| `SetBookFavorite` / `SetBookArchived` | `{book_id, value: boolean}` → `BookSummary` | 对应 Library service 调用。 |
| `ListChapters` / `CreateChapter` / `DeleteChapter` | `{book_id}` / `{book_id,title,chapter_number?}` / `{chapter_id}` → `ChapterSummary[]` / `ChapterSummary` / `Unit` | ViewModel 使用 `list/get/create/delete_chapter`。 |
| `ImportPages` | `{chapter_id, sources: ImportSourceRef[]}` → `ImportReport` | 当前导入接受路径/URL 类来源；未来 IPC 必须由 Tauri host 授权并传递不透明、受限、可过期的 `ImportSourceRef`，不得把大型图片 bytes/Base64 放进 JSON。URI/token 具体形态 **DEFERRED to the runtime Task**；security/lifecycle semantics 现已 ruled in §10.1/§10.2（M2-C2）。 |
| `StartRun` | `{command: PipelineCommand, scope: PipelineScope, overrides?: JsonObject}` → `RunAccepted` | 当前 Workbench 依次调用 `PipelineService.create_run`、`plan_run` 并启动 worker。未来 handler 应先持久化并规划，再安排 Core 后台执行；精确 acceptance 时点是 Proposal，需 runtime Task 定义和验证。 |
| `GetRunSnapshot` | `{run_id}` → `RunSnapshot` | 从持久 Run 状态恢复查询的 **PROPOSAL**；`PipelineService` 能查 Run，IPC 查询尚未实现。 |
| `GetTaskProjection` | `{run_id}` → `TaskProjection` | `build_projection` 是应用层唯一投影，可含页面统计、焦点、步骤流、错误原因和控制按钮能力；禁止 UI 自行重算权威业务状态。 |
| `ControlRun` | `{run_id, action: pause\|stop\|continue\|restart\|abandon}` → `ControlResult` | `PipelineService.control_run` 为现有状态机权威。非法转换 typed failure。 |
| `RetryFailedTargets` | `{run_id}` → `RunAccepted` | `retry_failed_targets` 创建 source-linked 新 Run；无失败页面时返回现有 `TARGET_NOT_FOUND`。 |
| `SetRegionType` | `{region_id, new_region_type, expected_revision?: RevisionNo}` → `{region_id, revision_no: RevisionNo, region_type, sfx_policy}` | **`1.4` 修订草案（M2-REGION-RETYPE-CONTRACT）**：region 改标。改标=经既有 commit seam 产生一笔新 revision（origin 恒 `user`），非原地改字段；`new_region_type` 枚举复用 `RegionType` 六值 wire 字符串；错误码零新错误语义（映射表，wire `code` 字面量全部复用既有导出）；改标后 policy 快照规则（EV-8 裁决）与并发/持久性语义以 §5.4 为准。**runtime 已由 M2-REGION-RETYPE-CORE 落地（`PROTOCOL_MINOR=3`，`1.5` 回填）。** |
| `ListRegions` | `{page_id}` → `{"regions": RegionListSummary[], "page_size": {width,height} \| null}`（`1.4` 最小集：`{region_id, region_type, sfx_policy, origin, revision_no}` + `1.5` 可选 `geometry`/`page_size`；**result 包装形状以 §5.4 为准**） | **`1.4` 修订草案（M2-REGION-RETYPE-CONTRACT）**：region 读取面最小 DTO（`RegionListSummary`，`1.4` r1 定名——与 `CreateRegion` result 的 `RegionSummary` 解耦，避免隐式收窄其结构），按 reading_order 升序；不含文本/标注状态（读取面不含训练语义，取舍理由见 §5.4）。**`1.5` additive widening（M2-WORKBENCH-REACT-1）**：可选 `geometry`（归一化，D5 闭合）+ 可选 `page_size`（像素投影），协议 minor 不 bump。注：`CreateRegion` 行 result 引用的 `RegionSummary` 结构在本修订前后均未定义，`CreateRegion` 的 result 语义不在本修订改变范围。 |
| `CreateRegion` | `{page_id, shape: {kind:"rectangle", corners: [NormalizedPoint, NormalizedPoint]} \| {kind:"polygon", points: NormalizedPoint[3+]}}` → `RegionSummary` | 归一化换算使用 app `normalized_to_page_geometry`，几何校验在 Core；image/page bytes 不随命令传输。 |
| `DeleteRegion` | `{region_id}` → `Unit` | Workbench VM 调用 Region deleter；权限、Lock 与 revision 条件由 Core 检查。 |
| `SaveManualTranslation` | `{region_id, text, expected_revision?: RevisionNo}` → `{revision_no: RevisionNo}` | Workbench VM 当前调用编辑 service 保存手工译文。`expected_revision` 是防覆盖 Proposal，精确并发策略 **UNKNOWN**。 |
| `ListRegionRevisions` / `RestoreRegionRevision` / `SetRevisionPinned` | `{region_id}` / `{region_id, revision_no}` / `{region_id, revision_no, pinned}` → `RevisionSummary[]` / `RegionSnapshot` / `Unit` | `RegionRepository` port 的 `list_revisions` 读取历史；编辑 service 提供 `restore_revision` 与 `set_revision_pinned`。具体 ViewModel/QML 可见性并不完整。锁/Revision 保护要求来自 AD-001；任何操作的资格检查归 Core。 |
| `GetReaderProjection` / `SaveReadingProgress` | `{chapter_id}` / `{chapter_id, page_id?, scroll_offset?}` → `ReaderProjection` / `Unit` | Reader VM 读取章节页并保存滚动偏移；page navigation、display mode 为 presentation state。 |
| `GetSettings` / `SaveSettings` | `{section?}` / `{section, values}` → `SettingsProjection` / `SettingsProjection` | AS-IS 仅证明 Settings VM 在进程内调用 profiles/defaults/credentials services；没有已定义的 `CredentialRef` 类型或 IPC exchange。Credential DTO/exchange 为 UNKNOWN / DEFERRED；secret 不得进入普通事件或日志。**`1.3` 修订（M2-SETTINGS-IPC-CHANNEL）**：本行 transport-neutral 命令名与其 PROPOSAL 等级不变；产品 Tauri 面落地为 §5.3 的 `settings_get` / `settings_update_section`（请求/响应/错误码与写入端校验以 §5.3 为准）。 |
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

### 5.3 Product Tauri settings channel (M2-SETTINGS-IPC-CHANNEL)

本节 wire shape 由 [M2-SETTINGS-IPC-CHANNEL](../tasks/M2-SETTINGS-IPC-CHANNEL.md)（用户裁决①，`user_ruling_2026-10-02_three_confirmations`）授权并落地；命令名来自 [M2-SETTINGS-UI-SFX-POLICY handoff](../handoffs/M2-SETTINGS-UI-SFX-POLICY-8c798aed.md) 的 pin（前端常量+测试先行锁定，改名即漂移）。范围仅此两命令；不构成其他 settings 键、其他命令面或大媒体通道的先例（§10 与 §10.1 的独立授权要求不变）。两个命令都 riding 同一条既有产品 stdio JSON-lines 通道（React → Tauri `settings_get`/`settings_update_section` → Python `bootstrap.core_service` `settings.get`/`settings.update_section` → `PipelineDefaultsService`）；Core 是设置语义的权威，Tauri/Rust 只转发与映射 typed 错误（§1/§2 不变）。

- **`settings_get`** — 请求 payload `{}`（全量）或 `{"section": "<name>"}`（单节）。响应 result 为 `{"settings": <object>}`：全量形态返回 `PipelineDefaults.settings` 的 JSON 投影（如 `{"sfx": {"policy": "skip"}, "ocr": {"script": "..."}}`）；单节形态返回 `{"settings": {"<name>": <object | null>}}`——节未设置时该节值为 JSON `null`（沿 `1.2` 的 frozen None 通道语义：未设置/未统计可区分于空对象）。`section` 为空串或非 string 时 typed 拒绝（见下）。 `section: null` 同样按非 string typed 拒绝（JSON null 不是合法节名；读取全量请省略该键）。`settings_update_section` 为 upsert 幂等：同参数重复调用结果一致，重复写入同值不产生额外副作用。
- **`settings_update_section`** — 请求 payload `{"section": "<name>", "values": <object>}`；语义 = `PipelineDefaultsService.save_settings_section(section, values)` upsert（整节替换，非逐键合并；与既有 `ocr.script` 同通道）。响应 result 为更新后的全量投影 `{"settings": <object>}`（调用方一次往返即得最新状态）。
- **写入端前置校验（RULED，typed fail-closed，持久化之前拒绝）**：M2-SFX-ENTRY r1 R4 教训落约——写入端零校验会让非法值直达持久层，下一次装配 fail-fast 时成为不可自愈的启动阻断。因此：
  1. `section` 必须为非空 string；
  2. `values` 必须为 JSON object；
  3. `section == "sfx"` 且 `values` 携带 `"policy"` 键时，其值必须在 `{"skip", "translate", "manual"}` 内（**首个落地实例**；语义事实源 = M2-SFX-TRANSLATE-ENTRY，默认 `skip`，re-assemble 生效、仅新建 region）；
  4. 其余 section/键透传（结构校验同 1/2；未列键的值域校验由 Core 装配期语义继续负责，本节不白名单化 settings 键集合）。
- **错误码（沿 §8 既有枚举，不发明新码）**：请求校验失败（上述 1–4 与空 `section` 读取）→ `INVALID_REQUEST`、`category=validation`、`retryable=false`（`core.detect` payload 校验同码先例）；持久化失败 → `UNKNOWN`、`category=internal`；通道/spawn 失败 → `CORE_UNAVAILABLE`（Rust 侧既有映射不变）。`message` 遵守 §8（安全短句，无路径）。
- **宿主同步纪律**：Tauri 面三处手工同步视图（`command_allowlist` 常量 / `generate_handler!` 字面清单 / build.rs app-manifest）+ capabilities 声明必须同一 commit 内同步（RC2-AC1 R2-04 既有纪律）；两命令 production-only（probe/ac1 测试模式面保持冻结形状，沿 M2-IPC1 option-B 先例）。前端 commandSurface pin 与 Rust unit test 同时更新。

### 5.4 Region retype and read channel (M2-REGION-RETYPE-CONTRACT) — 草案

本节 wire shape 由 [M2-REGION-RETYPE-CONTRACT](../tasks/M2-REGION-RETYPE-CONTRACT.md)（用户裁决 `user_ruling_2026-10-04_训练质量效率优先_许可降权备案`）授权并冻结；**runtime 已由 M2-REGION-RETYPE-CORE（done @merge `d8019810`）交付落地（`core_service.py` `PROTOCOL_MINOR=3`；`1.5` 时回填）**。两命令与 §5.3 同 riding 既有产品 stdio JSON-lines 通道（React → Tauri → Python `bootstrap.core_service`）；Core 是 region 语义的唯一权威，Tauri/Rust 只转发与映射 typed 错误（§1/§2 不变）。所有请求在 Core 边界重新校验（§2 既有条款）；写入端对 payload 形状与枚举 typed fail-closed、持久化之前拒绝（§5.3 写入端校验纪律的同一教训落约）。

- **`SetRegionType`（改标）** — 请求 payload `{"region_id": <RegionId>, "new_region_type": <RegionType>, "expected_revision"?: <RevisionNo>}`。`new_region_type` 枚举**复用** `RegionType` 六值 wire 字符串——`REGION_TYPE_VALUES = "speech" | "narration" | "sfx" | "title" | "note" | "other"`（域事实：`src/domain/regions/entities.py:20-28`；本修订零新增枚举值，§3.1「未知 enum 值必须返回 typed validation error」原样适用）。响应 result 为改标后生效态 `{"region_id": <RegionId>, "revision_no": <RevisionNo>, "region_type": <RegionType>, "sfx_policy": "skip"|"translate"|"manual"}`——含 `revision_no`（沿 `SaveManualTranslation` 的 `{revision_no}` result 先例）与改标后 region 自身 policy 快照（调用方一次往返即得生效态，沿 §5.3 `settings_update_section` 先例；UI 反馈条零二次查询）。`expected_revision` 提供时为乐观守卫：不匹配当前 revision → typed 拒绝（C4；见错误码表）；省略时为用户直写（见下）。**交叉指针（`SaveManualTranslation`）**：本 `expected_revision` 语义与 §5 表 `SaveManualTranslation` 行的 `expected_revision` 防覆盖 Proposal 同一模式（可选乐观守卫 + 用户直写回退）；region 写命令面的该语义以本条目+C4 断言为权威，`SaveManualTranslation` 行自身「精确并发策略 **UNKNOWN**」的边界注记不变，其 runtime 实现须对照本节冻结语义。
- **改标 = 新 revision（单一写路径，origin 定案）**：成功改标经既有 `commit_region_revision` 原子 seam 产生**一笔新 revision**，不得原地改字段无历史（域事实：`src/application/editing/service.py` 单一提交路径；实体层 `Region.apply_type` 已定义类型变更，`entities.py:243-245`）。改标 revision 的 **`origin` 恒为 `user`**——`RegionOrigin` 四值 `machine/user/imported/restored` 零新增（MACHINE/RESTORED 之外无需新值；人工改标=用户类型决策，沿 `save_manual_translation` 用户写先例，`service.py:521-529`）。机器改标不走本命令：检测产出沿检测单一写路径（origin=machine，`core_assembly.py:1006-1010`），仲裁自动改标以 `sfx-arb-` label 前缀分发为 SFX 类型（`detection_sfx.py:202`），均不产生 user revision。改标 revision 的 snapshot 相对改标前**仅 `region_type` 与 `sfx_policy` 两字段变化**；text/style/locks/reading_order/geometry 全部原样保留（域事实：snapshot 字段集 `entities.py:267-288`；不得静默清空译文——§10 人工修改保护原样适用）。改标 revision 的 **`review_state` 定案 `UNREVIEWED`**（ReviewState 三值 `unreviewed/needs_review/confirmed` 零新增，`entities.py:40-44`；理由：①源码先例——类型/几何/顺序类用户写一律 `ReviewState.UNREVIEWED`（`create_region`/`save_geometry`/合并/拆分/reorder，`service.py:272/302/363/402/429`），`NEEDS_REVIEW` 仅用于文本内容变化写（`save_manual_translation` `service.py:527`、机器 OCR/翻译 `service.py:456/499`）；②改标不改变文本内容，若标 `NEEDS_REVIEW` 会把无文本变化的类型决策误报为需校对信号）。改标**不触发需校对变化**：`edited_confirmed`/`manual_edited` 等文本校对标志属 snapshot text 面原样保留（`entities.py:273-282`），既有已确认译文不因改标回到需校对。
- **撤销 = 既有 `RestoreRegionRevision` 语义引用，不重定义**：改标撤销 = 调用 §5 表既有 `RestoreRegionRevision` 恢复改标前 revision——产生 `origin=restored` 新 revision（`restored_from_revision_id` 溯源，历史不重写；域事实 `service.py:550-572`）。不得以「反向改标」（再调一次 `SetRegionType` 改回）模拟撤销——那会产生第二笔改标语义 revision 并丢失「改标曾被撤销」的可追溯事实（UI 设计稿 R5/A6 同语义）。
- **改标后 policy 快照规则（EV-8 裁决，RULED）**：二选一定案为 **「按改标时全局配置重快照」**：
  1. 改标为 `sfx`：改标 revision 的 `sfx_policy` = **改标提交时刻的全局 `sfx.policy` 配置值**（三值；§5.3 settings 通道为读取面）——类比新建语义（域事实：新建 SFX region 即携带创建时配置，`core_assembly.py:1041-1045`）；**不得继承改标前快照**。
  2. 改标为非 `sfx` 五值：改标 revision 的 `sfx_policy` **强制 `skip`**（维持「the policy can never leak onto non-SFX regions」装配不变量跨写路径成立，域事实 `core_assembly.py:1036-1045`）。
  3. **理由（技术事实链）**：gate 消费 region 自身快照字段、不读全局设置（`gate.py:32-42`），且 speech region 快照现状恒为 skip（上述强制规则）。若裁决「继承原快照」，speech→sfx 改标后快照仍为 skip，全局 `translate` 配置对该 region **永久不可达**——用户「拟声词也要翻译」的设置意图静默失效；继承分支下**无 region 级自愈路径**（除软删除后重新检出：删除后重检测按新建语义携带当时全局配置，`core_assembly.py:1041-1045`），如需恢复须新授权修订。重快照与新建语义一致（改标=重新类型化），行为可预期；且与 UI 设计稿 §4.2 联动表 translate 行的前置条件一致（设计稿明示「仅当裁决为按当前配置重快照时本行可达」），UI 侧零返工。设计稿 EV-8 项由本裁决闭合（设计稿不回改，闭合注记落本 Task verification）。
- **`ListRegions`（读取面）** — 请求 payload `{"page_id": <PageId>}`。响应 result 为包装对象 `{"regions": RegionListSummary[], "page_size": {width, height} | null}`（**result 形状唯一权威=本条目；§5 表行注记同此**；`page_size` 为 `1.5` 追加的可选字段——页面像素尺寸投影，RegionOverlay letterbox 数学的「尺寸只从投影取」承载（M2-UI1 §2.2）；`page_id` 未命中任何 page 时为 `null`，沿 `1.2`/§5.3 frozen-None 通道语义先例），按 `reading_order` 升序（域事实 `service.py:279-281`）。`RegionListSummary` **最小 DTO（本修订冻结的最小集与定名；`1.4` r1 由 `RegionSummary` 更名——原名留给 `CreateRegion` result，两者解耦避免隐式收窄）**：

  ```text
  RegionListSummary = {
    region_id: RegionId,
    region_type: REGION_TYPE_VALUES,                # 六值闭集
    sfx_policy: "skip" | "translate" | "manual",    # region 自身快照，非全局实时值
    origin: "machine" | "user" | "imported" | "restored",  # 当前 revision 的来源
    revision_no: RevisionNo,                         # 当前 revision 号
    geometry?: {                                     # 1.5 追加可选字段（D5 闭合）
      bbox: [x, y, w, h],                            # 归一化 0..1（pixel/size 反算）
      polygon: [[x, y], ...]                         # 归一化点环；空环 => []
    }
  }
  ```

  - **`1.5` additive widening（D5 读取面几何闭合，M2-WORKBENCH-REACT-1）**：`geometry` 与包装级 `page_size` 是**可选**字段——§3.2 同 major「接收端忽略未知可选字段」即兼容 widening，**协议 minor 维持 `3` 不 bump**（本修订零新命令、零新错误语义；`core_service.py` 既有 bump 注记惯例均对应「commands added」，如实登记本次不适用；旧 Core 与旧读取端双向兼容）。归一化反算定义 `normalized := pixel / size`，与 §9 正向 half-up 规则 round-trip 精确自洽（存储像素已在 `[0, size]`，输出天然在 `[0,1]`）；单一数学权威 = `application/editing/region_canvas.py`（正反向同文件）。`geometry` 服务 overlay 绘制（展示几何通道），不携带训练语义；§5.4 读取面原边界对扩容面继续适用——suspect/review_state/文本仍不在读取面（RC-1/RC-4/RC-5 候选保持登记）。

  - **取舍定案（扩容既有命令 vs 新命令）**：定案**新命令**。理由：①既有命令面无 region 读取通道——`CreateRegion` 的 `RegionSummary` result 结构在本修订前未定义（§5 表），`GetReaderProjection` 不含 region 面，`ListRegionRevisions` 是 revision 历史不是当前 region 列表；扩容任一既有命令都须改其既有 result 形状（类型变化=major 变更，§3.2），新命令是同 major 兼容 widening（§3.2 minor 规则）。②改标 UI 的数据需求（类型/policy/来源/revision）与 Workbench 画布几何通道解耦——`1.4` 时本最小集不含几何字段（UI 设计稿 D5 的读取面几何缺口当时保持登记状态）；该缺口**已由 `1.5`（M2-WORKBENCH-REACT-1）以可选 `geometry`/`page_size` additive widening 闭合**（见上方 `1.5` 条目）。③单 region 详情不设独立命令：按 `region_id` 从列表过滤即可，避免命令面冗余（最小面原则）。
  - **来源字段语义（机器 vs 人工可区分）**：`origin` 取该 region 当前 revision 的 `RegionOrigin` wire 值。机器改标（检测/仲裁产出）→ `machine`；人工改标 → `user`——UI 设计稿 A7「机器改标与人工改标必须可区分」的需求以此字段承载。**事实注记**：`sfx-arb-` 是检测候选 provider label 的仲裁前缀（`detection_sfx.py:202`），仅存在于检测管道内部分发环节——region 实体与 revision 快照均**不持久化 label**（域事实：snapshot 字段集 `entities.py:267-288` 无 label 字段）。读取面的机器改标可追溯权威 = **`origin` 字段**（+ 检测步 provenance/StepResult 记录；源码事实 `1.4` r1 核实：检测/仲裁创建 region 经 `core_assembly.py:1032-1048` → `create_region`，其签名**无** `source_run_id` 参数（`service.py:247-256`），用户/恢复写经 `_commit_user_or_raise` 构造 revision 时 `source_run_id=None`（`service.py:222-241`）——该字段仅存在于 text 写路径（`handlers.py:354/439`）。UI 设计稿 A7「机器改标与人工改标必须可区分」的可追溯落点**限定为 `origin` 字段**）。UI 不得依赖「恢复 label 前缀」。UI 设计稿 §2.5/§3.4/§5 D7 以「label 前缀」表述的读取面区分依据，在持久化层面由 `origin` 字段承载（差异注记落本 Task verification，设计稿不回改）。
  - **读取面不含训练语义**：本最小集**不含**标注/评审状态（review_state）、疑似信号（suspect）、OCR/译文文本——读取面服务改标决策与 overlay 绘制展示，不定义训练数据语义。**几何自 `1.5` 起移出本排除清单**：`geometry` 为 `1.5` 追加的可选展示几何通道（不携带训练语义，见上方 `1.5` additive widening 条目）。suspect/review_state/文本仍不在读取面，上述字段的任何扩容须另行授权修订（UI 设计稿 D2 suspect 字段、D7 RevisionSummary 结构、D8 reader 摘要等 RC-1/RC-4/RC-5 候选保持登记状态，本修订不裁决）。
- **错误码（零新错误语义：wire `code` 字面量全部复用既有导出，复用既有 typed 族）** — 沿 §8 `ErrorEnvelope`（定义不变）。**覆盖范围（表头注记）**：本表覆盖 `SetRegionType` + `ListRegions` 两命令——`ListRegions` 仅产生 `INVALID_REQUEST`（payload 校验）、空列表（非错误，见脚注 a）与 `UNKNOWN`；乐观冲突/目标缺失两行为 `SetRegionType` 专属。映射表：

  | 失败 | wire `code` | `category` | `retryable` | 复用依据 |
  |---|---|---|---|---|
  | payload 非 object；`region_id`/`new_region_type`/`page_id` 缺失或非字符串；`new_region_type` 不在 `REGION_TYPE_VALUES` 内；`expected_revision` 非 integer | `INVALID_REQUEST` | `validation` | `false` | §5.3 settings 写入校验同码先例；core service 既有字面量（`E_INVALID_REQUEST`，`core_service.py:105`） |
  | `expected_revision` 提供且 ≠ 当前 revision（乐观冲突） | `INPUT_REVISION_CHANGED` | `conflict` | `false` | `GuardStatus.INPUT_REVISION_CHANGED` 源码既有（`application/editing/errors.py:19`）；§8 冲突族 |
  | `region_id` 不存在或已 soft-delete | `TARGET_NOT_FOUND` | `not_found` | `false` | §8 表既有行（TARGET_NOT_FOUND→not_found，其「may need richer subcode」边界注记原样适用；runtime Task 若判定需 region 专属 subcode 走新修订，本修订不发明） |
  | Core 侧未分类失败（持久化失败等） | `UNKNOWN` | `internal` | `false` | §5.3 同款（UNKNOWN/internal）；§8 未映射规则 |

  脚注：
  - **a（空列表归类，`ListRegions`）**：`page_id` 不存在/不属于任何 book，与 page 存在但无存活 region，返回空列表（**非错误**，二者取值按 `page_id` 是否命中区分——`1.5` 集成收口 C1 按 runtime 实际字面收口：`page_id` 未命中（不存在/不属于任何 book/软删/不完整页）→ `{"regions": [], "page_size": null}`（frozen-None 通道语义）；page 命中但无存活 region → `{"regions": [], "page_size": {width, height}}`（与 `core_service.py:737-746` 的 `get_page` 命中语义一致））——沿既有 `list_regions` 源码语义（无 page 存在性检查，`service.py:279-281`）。严格 page 存在性校验（对齐 `list_chapters` 的 `get_book` 存在性先例，`library/service.py:155-160`）属读取面语义扩容，须新授权修订，本修订不引入。
  - **b（`LOCK_CHANGED` 消歧）**：`LOCK_CHANGED` **不在本表**——它是机器写守卫 `GuardStatus` 的内部结果值（`errors.py:20`，D06 §89 存候选语义，见 C3 断言），不是本两命令对调用方的 wire 错误码；C3 中「`LOCK_CHANGED` fail-closed」指机器写路径的守卫结果。
  - **c（wire `code` 大小写字面量）**：本表与 §8 的 `code` 字面量一律 **SCREAMING_SNAKE_CASE 大写**（对齐既有导出口径：`core_service.py` `E_INVALID_REQUEST = "INVALID_REQUEST"`（`core_service.py:105`）、`E_UNKNOWN = "UNKNOWN"`（`core_service.py:98`）、§8 表既有大写字面量；`GuardStatus` 成员名同此大写形式（`errors.py:19-20`），其枚举字符串值（`"input_revision_changed"`/`"lock_changed"`，小写）是内部守卫状态值，**不得**用作 wire `code`）。

  `message` 遵守 §8（安全短句，无路径、无 secret）。
- **并发与人工覆盖语义（可测断言）** — 每条 = 触发条件 → 期望行为。域守卫事实：机器写带乐观 revision 期望与 lock 快照，命中即 fail-closed 存候选不覆盖（D06 §89/§90，`service.py:483-496`）；用户写无乐观期望、不受 lock 阻塞（`service.py:222-241`）。
  - **C1（人工优先：写通道不互斥）** — 触发：某 Run 的机器写正在执行，用户对任一 region 提交 `SetRegionType`。期望：改标立即提交成功（产生 `origin=user` 新 revision），不被运行中 Run 阻塞或排队（用户写路径语义）；已进入执行的机器步骤决策不因改标回溯。
  - **C2（AI 侧 fail-closed：Revision 守卫）** — 触发：机器写（如 `apply_machine_translation`）提交时携带的期望 revision ≠ 当前 revision（期间用户已完成改标）。期望：机器写 fail-closed——`INPUT_REVISION_CHANGED` 语义，不覆盖 region 任何字段，机器结果仅持久化为候选（StepResultCandidate 既有语义），不自动重试覆盖；期望失效优先于 lock 判断（D06 §90 既有顺序）。
  - **C3（AI 侧 fail-closed：Lock 守卫）** — 触发：机器写目标 region 处于 `translation_locked` 或 `region_locked`。期望：`LOCK_CHANGED` fail-closed，存候选不覆盖（D06 §89 既有）；锁解除后须显式重跑才会消费改标后的新决策。
  - **C4（乐观期望显式拒绝）** — 触发：`SetRegionType` 携带 `expected_revision` 且不匹配当前 revision。期望：typed 拒绝 `INPUT_REVISION_CHANGED`，region 状态零变化（无部分写入）。
  - **C5（改标后决策生效）** — 触发：改标成功后，该 region 被后续步骤/后续 Run 读取。期望：按改标后 `region_type` + `sfx_policy` 快照决策（gate 消费 region 字段，`gate.py:32-42`）；改标只改变「此后」的翻译/渲染决策，已渲染成品图不因改标消失（UI 设计稿 §1.3 同语义）。
  - **C6（机器改标上的人工叠加）** — 触发：对当前 revision `origin=machine` 的 region 提交 `SetRegionType`。期望：产生新 `origin=user` revision 叠加为当前态，机器 revision 保留历史可追溯（不得原地覆写或删除机器笔）；撤销经 restore 回机器笔（`origin=restored`）。
  - **C7（目标缺失）** — 触发：`SetRegionType` 的 `region_id` 不存在或已 soft-delete。期望：`TARGET_NOT_FOUND`（not_found）拒绝，零写入。
- **持久性语义（可测断言）**：
  - **P1（重开持久）** — 触发：改标后 Core 进程/应用重启。期望：`region_type`、`sfx_policy` 快照、revision 历史（含改标笔 `origin=user`）与 current 指针全部保持（SQLite 持久权威，§2）；重新 `ListRegions` 返回改标后状态。
  - **P2（重检测不回滚人工改标）** — 触发：对已含存活 region（含人工改标 region）的页重新执行检测步。期望：检测步幂等复用既有存活 region、不重建不删除（域事实 `handlers.py:246-269`），人工改标的类型与 policy 快照保持；仅当页无存活 region 时才沿单一写路径新建（origin=machine，域事实 `core_assembly.py:1006-1010`）。
  - **P3（撤销完整恢复 + 历史保留）** — 触发：对改标 region 调 `RestoreRegionRevision` 至改标前 revision_no。期望：产生 `origin=restored` 新 revision（`restored_from_revision_id` 溯源），`region_type` 与 `sfx_policy` 快照一并回到改标前值；不删除/改写任何既有 revision。
  - **P4（撤销后再改标，规则幂等适用）** — 触发：撤销后再次 `SetRegionType`。期望：按新一笔改标正常产生 `origin=user` revision；policy 快照规则（本节 EV-8 裁决）对新改标再次适用（按再次改标时刻全局配置重快照），不残留撤销链状态。
- **「忽略」语义定案（契约注释，RULED）** — 「忽略」**不是** `RegionType` 值：六值枚举闭集零新增（域事实 `entities.py:20-28`）。**定案依据 = Task 合同 AC4（Codex 编排方案第 8 点）语境**；事实注记：**UI 设计稿全文无「忽略」表述**——用户可见近义为「保留原文 / 不翻译 / 停止翻译」（design.md:41/236）；设计稿 R-015 是疑似警示收窄 speech 的既成事实，与「忽略」无直接语义关系，仅**同属 `RegionType` 闭集纪律**（本修订不回改设计稿）。「忽略」在本契约中定为**处理动作或过滤状态**：①作为**处理动作**，它是管道对某 region 跳过自动翻译的决策结果（gate 的 `SKIP_POLICY(reason=sfx_skip)` 语义，`gate.py:39-42`），由 `region_type` + `sfx_policy` 快照组合派生，不落独立领域字段；②作为**过滤状态**，它是 UI/投影层的查询过滤（§5.2 UI-local actions 语义），不写持久状态。若未来需要把「忽略」持久化为独立领域状态，属领域类型扩容，须新授权修订（本注释构成对该方向的预拒绝：①/② 已覆盖现有需求）。与设计稿对齐注记：设计稿既有的「保留原文/停止翻译」用户可见语义（design.md:41/236）与上述①的 gate 派生语义一致；若未来 UI 引入「忽略」措辞描述上述①/②，实现时映射为①或②，不得新增 `RegionType` 值（注记落本 Task verification）。
- **宿主同步纪律（沿 §5.3）**：两命令 runtime 落地时，Tauri 面 `command_allowlist` / `generate_handler!` / app-manifest 三处同步视图 + capabilities 声明 + 前端 commandSurface pin + Rust unit test 必须同一 commit 内同步（既有纪律，§5.3 末条原样适用）。
- **修订纪律声明**：本节由 **rev 1.4 草案**（M2-REGION-RETYPE-CONTRACT）起步，其两命令 runtime 已由 M2-REGION-RETYPE-CORE（done @merge `d8019810`）落地——`core_service.py` 协议 minor 自该交付起为 `3`；**rev 1.5**（M2-WORKBENCH-REACT-1）在本节内对 `ListRegions` 读取面做 additive widening（可选 `geometry`/`page_size`），minor 维持 `3` 不 bump（理由见 Revision history `1.5`）。本修订不放松 §1–§4 与 §6–§10 既有保护语义：§2 Core 权威与边界重校验、§3 版本规则、§4 请求/响应互斥不变量、§10 数据保护（源文件/人工修改/Lock/Revision 保护）全部原样适用于两命令。

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
- **`1.5` 注记（M2-WORKBENCH-REACT-1）**：本节的正向规则不变；其**反向读取映射**（`page_geometry_to_normalized`，stored pixels → normalized，与正向 half-up 规则 round-trip 自洽）由同一 application 层模块 `application/editing/region_canvas.py` 持有，服务于 §5.4 `ListRegions` 的可选 `geometry` 展示几何通道——仍在 application 层，未违反本节「no protocol-side geometry implementation」禁令。

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
| Runtime serialization library, Tauri command names, process supervision, auth/permission handshake | `UNKNOWN / NOT_IN_SCOPE`（`1.3` 注记：仅 `settings_get`/`settings_update_section` 两命令的 Tauri command name 与 wire shape 已由 §5.3 裁决落地；`1.4` 草案冻结；`1.5` 时回填（集成收口 C2 事实同步）：两命令 runtime 已由 M2-REGION-RETYPE-CORE 落地（`PROTOCOL_MINOR=3`），产品 Tauri command name 与 Core stdio command name **均取 snake_case** `set_region_type`/`list_regions`（最终裁决=M2-WORKBENCH-REACT-1，`0f88cbcd` P4-2 deferral 闭合，§5 表保留 transport-neutral 逻辑名）；本行其余决定仍 UNKNOWN/NOT_IN_SCOPE） | No implementation claimed beyond §5.3/§5.4; separate runtime Tasks must decide the rest against this transport-neutral contract. |
| Event ordering/replay/retention and idempotency | `UNKNOWN / NOT_FROZEN` | Snapshot resync is the safe proposal; stronger guarantees need runtime tests. |
| Lock/revision conflict response details and concurrent edit policy | `PARTIALLY FROZEN`（`1.4` 草案：region 写命令面已冻结于 §5.4——人工优先、AI 侧 fail-closed、Revision/Lock 守卫交互、错误码映射；runtime 已由 M2-REGION-RETYPE-CORE 落地，`1.5` 时回填） | Core remains authority; §5.4 freezes the region-retype slice only; the rest of the command surface and finer conflict details stay open without weakening protection. |

The UI mapping decision does not block freezing a transport-level Page status distinct from Run status. Any proposal to alter the status value or user-visible mapping returns to the user; M2-C1 does not resolve it.

## 12. Release boundary

This document freezes design only. It does not authorize Python IPC Runtime, Tauri, React, QML changes, SQLite/Schema changes, dependencies, M2-S1, data transport selection, or integration. A successor implementation Task must reference this contract, identify its owner and scope, and verify the runtime semantics it implements.
