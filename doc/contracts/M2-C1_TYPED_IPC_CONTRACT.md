> **内部生命周期窄注记（2026-10-07，M2-DERIVED-GC-2 实现；零 wire 修订，协议 major/minor 不变）**：M2-DERIVED-GC-2 在专用 resource catalog 内引入 `preview_lifecycle` 来源行与 `preview_namespace` 绑定行，并给宿主→channel 的**内部** `revoke_resource` 控制请求加了受信 `retire_preview` 布尔位（CoreChannel 轮换专用方法；channel 仅在其自身 revoke 成功后据此把已登记自有 preview 行的 `retired` 置 1）。这些都是 host↔sidecar 控制面/SQLite 元数据内部实现：**不新增任何 Tauri IPC 命令、不改 WebView payload/ACL/十五条生产命令表、不发 `source_artifact_revision_id`/`producer_root` 等来源字段到 WebView、不改 issue/resolve/touch/revoke/TTL 的既有语义**（失败撤销新 key 与 WebView `revoke_resource_refs` 均不携带该位）。preview 回收（retired 副本删除）只发生在受 namespace 租约保护的独占启动窗口，见 [M2_DERIVED_PREVIEW_GC_DESIGN.md](M2_DERIVED_PREVIEW_GC_DESIGN.md)。

> **rev 2.3（2026-10-16，HOST-ISSUER-1-C1 host→Core grant control）**：冻结独立 `HostControl` 会话握手、导入来源/导出目标 grant 注册与撤销，以及关闭时的 session 失效。控制请求仅走 Tauri host 持有的 live-Core 私有进程通道，带 `host_session_id`、`host_session_credential` 与 `core_session_id`；普通 JSON-RPC/WebView 面拒绝 host-only 操作。注册 payload 复用现有 Core 私有 seam 所需数据；`ImportSourceRef` / `ExportTargetRef` 字段与 `REF_*` 语义不变。协议 minor 从 2 增至 3；§12 仅授权最小 Core handler/session 改动与 `tests/core/**`，本次不实现 runtime。修订范围：§3、§5、§10.3、§10.4、§11、§12。兼容性见 [HOST-ISSUER-1-C1 compatibility impact](../../verification/HOST-ISSUER-1-C1/compatibility-impact.md)。
>
> **rev 2.2（2026-10-16，P12-C1 导入 IPC 契约）**：冻结 `ImportPages`、host 签发的只读 `ImportSourceRef` 与逐源/逐页 `ImportReport`；`ImportProgressChanged` 明确保持 `UNKNOWN / PROPOSAL`，原因见 §6.2。按 §3.2 将协议 minor 从 1 提升到 2，只新增冻结命令，不改变既有冻结 wire。修订范围：§3、§5、§6.2、§10.4、§12。明确授权导入侧 Python IPC Runtime，精确 allowlist 见 §12；本修订不代表 Runtime 或 Tauri host issuer 已实现。兼容影响见 [P12-C1 compatibility note](../../verification/P12-C1/compatibility-impact.md)。

> **rev 2.0（2026-10-16，P13-C1 Runtime IPC 授权修订）**：冻结 Run 命令、幂等键、快照/投影查询与 Run 状态事件 wire 面；`StartRun.idempotency_key` 为必填，且 stdio 输出流增加异步事件，因此按 §3.2 将协议 major 从 1 提升到 2。修订范围：§3、§4、§5 Run catalog、§5.5、§6.1、§6.2、§11、§12。Restart 重放响应可表达 child Run 当前状态；TaskProjection 冻结错误/重试与可得 Provider/Model/Device 字段。既有命令的 payload/result/error 语义不变；旧 major 客户端不能调用 major 2 endpoint，兼容影响见 [P13-C1 compatibility note](../../verification/P13-C1/compatibility-impact.md)。明确授权已释放的 P13 Task 实现 Python IPC Runtime，边界见 §12；本修订自身不代表 runtime 已实现。

> **rev 1.8（2026-10-07，M2-PAGE-NAV-PROJECTION-1 授权增量）**：新增 `list_chapters` / `list_chapter_pages`（页导航读取面第一刀），协议 minor 5→6（commands added 惯例）；`{book_id}` → `{"chapters": [{chapter_id, title, chapter_number, sort_order}]}`、`{chapter_id}` → `{"pages": [{page_id, source_filename, sort_order}]}`，均按 `sort_order` 升序；**零新错误码**——未知 book_id/chapter_id 返回空数组（fail-soft，1.4 r1 P3-4 先例），payload 校验 → `INVALID_REQUEST` 复用。本增量优先于下方目录中同能力的 PROPOSAL 状态（`ListChapters` 行转冻结）；既有 rev 1.7 及更早命令语义不变。

> **rev 1.7（2026-10-07，M2-PAGE-RESOURCE-RESOLVE-1 授权增量）**：新增 `resolve_page_resource`（页→资源目录键解析），协议 minor 4→5；请求 `{page_id}` → result `{resource_id, revision}`，错误面 `PAGE_NOT_FOUND`（not_found，新码）/`INVALID_REQUEST`/`ARTIFACT_WRITE_FAILED`（internal，retryable）/`UNKNOWN`。发布语义复用 RC-4 preview 先例：首次解析把不可变 managed 原图逐字节发布进 derived 只读根并登记 ResourceCatalogStore（确定性键 `page-original-{page_id}`，后续解析为目录查找，幂等返回同键；`revision` 为不透明修订标签，本命令恒 `"original"`；derived 产物被清后同键重发布自愈）；通道语义（opaque URL/chunk/TTL/§10 大媒体保护）零变化。既有 rev 1.6 及更早命令语义不变。

> **rev 1.6（2026-10-07，RC-4 授权增量）**：新增 list_region_revisions / restore_region_revision / rerender_page，协议 minor 3→4；冻结 DTO、并发、保护与 UI 消费语义见 [RC-4](M2-RC4_DOMAIN_COMMANDS.md)。本增量优先于下方目录中同能力的 PROPOSAL 状态；既有 rev 1.5 命令语义不变。

# M2-C1 — Typed IPC Contract

**当前修订范围：HOST-ISSUER-1-C1 rev 2.3**（§3 版本、§5.7 host-only grant control、§10.3/§10.4 注册通道交叉引用、§11 状态表、§12 最小 Core 授权）。P13 Run、P16 Reader/Export 与 P12 `ImportPages` 的现有 payload/result/error、`ExportTargetRef` / `ImportSourceRef` 字段和 `REF_*` 语义均零变化。

状态：rev `2.3`（HOST-ISSUER-1-C1）冻结 host→live-Core grant control wire；协议为 major `2` / minor `3`。rev 2.2 的 P12 导入 wire、rev 2.1 的 Reader/Export wire、rev 2.0 的 P13 Run wire 与更早既有冻结命令语义不变。Host issuer 与新 control runtime 尚未实现；§12 仅明确后续最小 Core 实现授权。下方历史 revision 条目保留当时状态，不覆盖本行与当前 rev 2.3。

## Revision history

- `2.3`（HOST-ISSUER-1-C1，2026-10-16）：**授权契约修订（host-only grant control）**——冻结 `OpenHostSession`、`RegisterImportSource` / `RevokeImportSource`、`RegisterExportTarget` / `RevokeExportTarget`、`CloseHostSession`；注册请求沿用 P09-FU2/P16 已有 seam 的字段；host session credential 与 Core session id 只存在 HostControl envelope/私有会话状态，不进入两种 ref。只新增独立 host-control wire，普通 JSON-RPC 对这些操作返回 `HOST_ONLY_REQUIRED`；协议 minor `2→3`，major 不变。既有 P12/P16/P13 wire、ref 字段及 `REF_*` 语义不变；§12 的最小 Core allowlist 仅含 `src/bootstrap/core_service.py` 与 `tests/core/**`。不授权 React/WebView、Tauri 命令、Schema/migration、依赖或其他产品行为；实现状态 `NOT_IMPLEMENTED`。
- `2.2`（P12-C1，2026-10-16）：冻结 `ImportPages` request/result、`ImportSourceRef` 只读来源授权与 `ImportReport` 逐源/逐页 DTO；来源限制为 P09 已批准的图片、显式选定文件集合/文件夹直接子项和 PDF，重复策略沿用 P09 的 `skip` / `import_as_new`。`ImportProgressChanged` 保持 `UNKNOWN / PROPOSAL`，因为 P09 没有持久 operation/snapshot wire；孤立事件不能成为导入真值。协议 minor `1→2`：只增加新冻结命令，没有改写既有冻结字段或事件；proposal 阶段的裸路径/URL 调用不获兼容承诺。更新 §12，授权导入侧 Python IPC Runtime 的冻结 allowlist；不授权 Tauri/Rust issuer 或产品代码。本修订未实现 Runtime。
- `2.1`（P16-C1，2026-10-16）：冻结 Reader/Export wire，新增 `GetReaderProjection` / `SaveReadingProgress`、`StartExport` / `CancelExport`、`GetExportSnapshot` / `GetExportHistory` 和 `ReadingProgressChanged` / `ExportProgressChanged`。`StartExport.target_ref` 为 Tauri host 签发、单一目标、300 秒过期且一次消费的 `ExportTargetRef`；Core 经与 `ImportSourceRef` 同源的受信 grant resolver 验证、解析、消费。协议 minor `0→1`，只新增命令/事件；旧命令语义和 P13 Run wire 不变，runtime 未实现。细节见 §5、§6.3、§10.3、§12。
- `2.0`（P13-C1，2026-10-16）：**授权契约修订**——① `StartRun` 增加必填 `idempotency_key`，并冻结 `ControlRun`、`ResumeBlockedRun`、`GetRunSnapshot`、`GetTaskProjection`、`RetryFailedTargets` 的 request/result；同键同 fingerprint 返回原 Run，同键不同 fingerprint 返回 `IDEMPOTENCY_KEY_REUSED`；restart 重放还返回 child 当前状态；`request_id` 保持纯请求关联用途；②按 P11 §4.2/§4.5 冻结控制动作与完整非法转换拒绝表；③冻结 `TaskProjection` 的任务错误/重试、可得 Provider/Model/Device 字段，以及 Task failure / Run pause / Run completion / current Page·Step changed 事件；事件在持久状态提交后经现有 JSONL stdio stream 推送，快照仍为真值；④协议 major `1→2`，因为新必填字段和响应/事件混合输出不能按 §3.2 minor widening；既有命令字段、结果、错误语义不变，但 1.x 客户端必须升级至 2.0 后才可连接该 endpoint；⑤**明确授权** P13 Task 实现 Python IPC Runtime，范围与 allowlist 由 P13 Task 冻结；不授权 React/Tauri/Rust 改动、其他产品功能或依赖。实现状态仍为 `NOT_IMPLEMENTED`。
- `1.8`（M2-PAGE-NAV-PROJECTION-1，2026-10-07）：**授权契约修订（新命令，协议 minor 5→6）**（[Task](../tasks/M2-PAGE-NAV-PROJECTION-1.md)，用户 2026-10-07 持续自治授权 STATUS 主路径候选①第二刀）——§5 新增 `ListChapters` / `ListChapterPages` 两行（原 §5 PROPOSAL 组合行的 `ListChapters` 转冻结；`ListChapterPages` 为新名，避开 `GetReaderProjection` 的 ReaderProjection 大对象）：①wire `list_chapters`：`{book_id}` → `{"chapters": [{chapter_id, title, chapter_number, sort_order}]}`（result 包装对象沿 ListRegions 1.4 r1 P1-1 先例）；②wire `list_chapter_pages`：`{chapter_id}` → `{"pages": [{page_id, source_filename, sort_order}]}`（导航摘要行——managed_original_ref/宽高/锁态不在本刀，几何与页尺寸由 `list_regions` 面承载，页图经 `resolve_page_resource` 通道获取）；③排序语义冻结：两命令均按 `sort_order` 升序（D03 AC-PAGE-001 用户当前排序；repository 既有 `list_chapters`/`list_pages` 已 ORDER BY sort_order，Core 透传不加新查询方法）；④**零新错误码**：未知 book_id/chapter_id 返回空数组（沿 1.4 r1 P3-4「不存在的父 id 归类空列表」先例——缺失父是空数据不是错误），payload 校验 → `INVALID_REQUEST`（validation）复用；⑤协议 minor 5→6（commands added 惯例，RC-4/1.7 先例）；⑥Rust 命令面 13→15 生产命令（新生产-only 组 `PAGE_NAV_PRODUCTION_ONLY_COMMANDS`，probe/AC1 冻结面零变化——option-B 先例）；⑦`GetReaderProjection` 冻结不变（Reader 页 display mode/进度面不在本刀）；不改变 §5.2 纯 UI 动作边界（book/chapter 下钻选择是 React 本地状态，Core 无写路径）；§10 通道语义零变化。
- `1.7`（M2-PAGE-RESOURCE-RESOLVE-1，2026-10-07）：**授权契约修订（新命令，协议 minor 4→5）**（[Task](../tasks/M2-PAGE-RESOURCE-RESOLVE-1.md)，用户 2026-10-07 持续自治授权 STATUS 主路径候选①第一刀）——§5 新增 `ResolvePageResource` 行（wire `resolve_page_resource`）：①请求 `{page_id}` → result `{resource_id, revision}`；②Core 侧经装配期 `read_original_page` 同款 storage 缝解析 `Page.managed_original_ref`（Managed Copy 根逃逸检查；wire 不携带路径与新业务身份，只返回不透明目录键）；③发布语义复用 RC-4 preview 先例（derived 只读根 + `ResourceCatalogStore` 登记，scope `derived-read-only`，temp+fsync+replace+逃逸门同款）；④**确定性资源键 `page-original-{page_id}`**：managed 原图不可变 → 首次解析发布、后续解析为目录查找返回同键（幂等，零重复产物；`revision` 恒为不透明字面量 `"original"`，Python 侧两分支共用 `ORIGINAL_REVISION` 常量；目录命中以产物存活为条件——derived 缓存被清后同键重发布自愈，byte-for-byte 确定性使幂等语义不变）——与 preview 的每次随机键轮换语义 deliberate 不同；⑤新错误码 `PAGE_NOT_FOUND`（not_found；页面不存在或无 managed 原图——与 region 面的 `TARGET_NOT_FOUND` 族区分，不靠 message 文本区分码）；`INVALID_REQUEST`（payload 校验）复用既有码；`ARTIFACT_WRITE_FAILED`（internal，retryable，发布 OSError）沿 RC4-08 拆分先例；⑥协议 minor 4→5（commands added 惯例，RC-4 先例）；⑦Rust 命令面 12→13 生产命令（生产-only 组 `PAGE_RESOLVE_PRODUCTION_ONLY_COMMANDS`，probe/AC1 冻结面零变化——option-B 先例）；host 侧**不**走 preview 轮换（稳定目录键不得被 per-page revoke 删除）；⑧不改变 §5.2 纯 UI 动作边界（页选择仍是 React 本地状态）；§10 通道语义零变化。
- `1.6`（RC-4，2026-10-07）：三条新域命令、DTO 与保护语义见 [冻结增量](M2-RC4_DOMAIN_COMMANDS.md)，minor 3→4；其余已实现命令语义不变。

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

以下 envelope 是 **PROPOSAL**，用语言无关的 JSON-compatible primitive 表示，尚未选择具体序列化库。Reader/Export 命令与事件 DTO 在 rev 2.1 中冻结，导入命令在 rev 2.2 中冻结；其他仍未冻结的类型继续按各节状态处理：

```text
Request<T> = {
  protocol: "new-manga.core",
  version: { major: 2, minor: 3 },
  request_id: OpaqueId,
  command: CommandName,
  payload: T
}

Response<T> = {
  protocol: "new-manga.core",
  version: { major: 2, minor: 3 },
  request_id: OpaqueId,
  result: T | null,
  error: ErrorEnvelope | null
}

Event<T> = {
  protocol: "new-manga.core",
  version: { major: 2, minor: 3 },
  event_id: OpaqueId,
  event_type: EventName,
  emitted_at: Timestamp,
  payload: T
}
```

### 3.1 Type aliases

- `OpaqueId`: 非空 UTF-8 string；不得由 UI 拼装领域主键语义。Core 负责校验实体存在性。
- `IdempotencyKey`: 调用方生成的不透明 string；字段独立于 `request_id`，不规定 UUID 或其他编码格式。
- `Timestamp`: RFC 3339 UTC 字符串。时间精度、时钟源及排序保证尚未由现状验证；不可据此推导全局顺序。
- `PageId`、`BookId`、`ChapterId`、`RegionId`、`RunId`、`TaskId`：opaque ID string；`RevisionNo`：Core 返回的 integer，合法范围由对应 Region/Core 数据决定，不由 UI 推断。保持与领域对象 ID 字段一致；不把路径编码进实体 ID。
- `NormalizedPoint`: `{ x: number, y: number }`。Core 按现有规则先计算 `floor(n * size + 0.5)` 的 half-up 页面像素坐标，再将整数坐标 clamp 到页面边界 `[0, size]`；不先把归一化输入 clamp 到 `[0,1]`。page width/height 必须为正整数。
- Enum wire value 使用现有领域字符串值，未知 enum 值必须返回 typed validation error，不得静默降级。

### 3.2 Compatibility proposal

- `major` 不同必须在执行命令前拒绝，返回 `PROTOCOL_VERSION_UNSUPPORTED`；不得猜测兼容。
- 同 major 下 minor 可向前增加可选字段和新 command/event；接收端忽略未知可选字段，但未知 command/event/status 必须显式返回/保留 `UNKNOWN`，不能重解释成其他状态。
- 字段删除、改名、类型变化、枚举旧值语义变化或必填性变化属于 major 变更。**例外**：经授权 Task 在 Revision history 登记的 nullability widening（`T → T | null`）不升 major，现仅有 §5 `ListBooks` 的 `BookSummary.page_count`（`1.2` 修订，[M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN](../tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md)）；1.1 版消费者遇 `null` 属该登记修订的授权破坏面。
- P13-C1 将冻结的 Run 命令面从 proposal major 1.0 升至 major 2.0：`StartRun.idempotency_key` 的新增必填性及单一 JSONL 输出流中新增异步事件均不能由 major 1 接收端安全忽略。既有命令 payload/result/error 语义不变；major 1 客户端收到 `PROTOCOL_VERSION_UNSUPPORTED`，必须升级后使用 major 2。当前生产 Core stdio 命令实现仍为 major 1 / minor 6；本修订只冻结目标 wire，不声称当前服务已支持 major 2。
- P16-C1 在 major 2 / minor 1 冻结新增 Reader/Export 命令与事件；既有冻结命令、结果、错误和 P13 Run 事件语义不变。rev 2.0 客户端不能调用这些新增命令；要使用 Reader/Export 面，客户端与 Core 必须配置到 rev 2.1。协议没有版本协商，本文不承诺不同 minor 的同进程双版本服务。
- P12-C1 在 major 2 / minor 2 冻结新增 `ImportPages`，其余既有冻结命令、结果、错误、状态和事件语义不变。协议 minor 从 1 增至 2，符合“只新增命令”的兼容规则；rev 2.1 客户端与 Core 必须升级并配对到 rev 2.2 才能调用导入面。minor 不代表旧的 proposal 裸路径/URL 形态受支持：旧形态从未冻结，P18 实际运行也报告 `UNKNOWN_COMMAND`。协议没有版本协商或自动迁移。
- HOST-ISSUER-1-C1 在 major 2 / minor 3 新增独立 `HostControl` envelope 与 host-only 会话/注册/撤销操作；minor 从 2 增至 3。现有 §3 `Request<T>` / `Response<T>` 及其 command payload 均不增加字段；旧客户端不支持 HostControl，也不能调用其操作。使用 HostControl 的 host 与 Core 必须配对支持 rev 2.3；普通 application JSON-RPC 对这些保留操作 fail-closed。无版本协商或自动迁移，现有 rev 2.2 及更早冻结 wire 不变。
- 版本握手/协商与自动迁移仍 `NOT_IMPLEMENTED`；客户端须以已知配置发送版本。`PROTOCOL_VERSION_UNSUPPORTED` 是稳定错误码。

## 4. Request/response 语义

- 每个命令对应一个 `Request<T>` 与一个最终 `Response<R>`；同步响应表示 Core 已接受并返回明确结果，不表示长任务已完成。
- `request_id` 只做单次请求/响应关联，**不得**充当幂等键；`idempotency_key` 只用于 §5.5 明确列出的创建 Run 操作。业务幂等不承诺外部 Provider 调用 exactly-once；调用方仅可按 §5.5 的同键规则重放。
- 查询返回不可变 DTO/Projection，不暴露 ORM、QObject、Python class pickle、数据库行对象或本地对象引用。
- 长任务创建返回 `RunAccepted { run_id, status }`。首次 durable acceptance 的 status 为 `pending`；同键重放返回该 Run 当前状态。后续进度由事件提示，规范状态通过 `GetRunSnapshot` / `GetTaskProjection` 查询。
- 错误响应满足 `result=null` 且 `error!=null`；成功响应满足 `error=null`。该互斥不变量是 **PROPOSAL**。

## 5. Typed command / query catalog

当前 Qt ViewModel 的方法不是一对一 IPC API。除明确标为 FROZEN 的行外，下表仍为 **PROPOSAL**；现有代码只证明“现有 ViewModel/Core service 有对应操作”，不证明 wire shape 或 IPC 已实现。页面选择、排序、过滤和未保存输入等纯前端交互留在 React 本地状态中。每行“现状”说明的是代码调用或领域服务存在性，不表示已经有 IPC。

| Name | Typed payload → result | As-Is evidence / To-Be boundary |
|---|---|---|
| `ListBooks` | `{}` → `BookSummary[]` | ViewModel 调 Library service 取书目；当前搜索、归档/收藏过滤、排序由 ViewModel 本地完成。AS-IS service call，IPC 未实现。**`1.2` 修订（M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN）**：`BookSummary.page_count: int \| null`——COUNT 谓词无行的书 → `null`（unknown），有合格页的书 → 真实计数；known `0` 与 `null` 可区分（详见 Revision history `1.2`）。 |
| `CreateBook` / `DeleteBook` | `{title, original_title?}` / `{book_id}` → `BookSummary` / `Unit` | `BookshelfViewModel.createBook/deleteBook` 调用 Library service。删除需 Core 检查关联和保留规则。 |
| `SetBookFavorite` / `SetBookArchived` | `{book_id, value: boolean}` → `BookSummary` | 对应 Library service 调用。 |
| `ListChapters` / `CreateChapter` / `DeleteChapter` | `{book_id}` / `{book_id,title,chapter_number?}` / `{chapter_id}` → `ChapterSummary[]` / `ChapterSummary` / `Unit` | ViewModel 使用 `list/get/create/delete_chapter`。**`1.8` 注记**：`ListChapters` 已转冻结为 wire `list_chapters`（见下方 `ListChapters` 行，最小导航摘要面）；`CreateChapter`/`DeleteChapter` 仍为 PROPOSAL。 |
| `ImportPages` | `{chapter_id, sources: ImportSourceRef[], duplicate_policy?: "skip"\|"import_as_new"}` → `ImportReport` | **2.2 FROZEN**：payload、逐源/逐页结果与拒绝面见 §5.6；只接受 host 授权的只读来源引用，详情见 §10.4。协议冻结不表示 runtime 已实现。 |
| `HostControl`（仅 host↔Core） | `OpenHostSession`、单条 `RegisterImportSource` / `RevokeImportSource`、`RegisterExportTarget` / `RevokeExportTarget`、`CloseHostSession`；DTO 见 §5.7 | **2.3 FROZEN**：独立 host-control envelope + session credential；只在 host 持有的 live-Core 私有进程通道，不是 application/Tauri command，不得由 React/WebView 调用。runtime 未实现。 |
| `StartRun` | `{command: PipelineCommand, scope: PipelineScope, overrides?: JsonObject, idempotency_key: IdempotencyKey}` → `RunAccepted` | 当前 Workbench 有 `PipelineService.create_run`/`plan_run`，但无此 IPC handler；冻结 wire 与 acceptance 见 §5.5。 |
| `GetRunSnapshot` | `{run_id}` → `RunSnapshot` | 读取 Core 持久 Run 状态；wire DTO 与拒绝语义见 §5.5。 |
| `GetTaskProjection` | `{run_id}` → `TaskProjection` | `build_projection` 是应用层唯一投影；读取面见 §5.5 和 §6.1。 |
| `ControlRun` | `{run_id, action: pause\|stop\|continue\|restart\|abandon, idempotency_key?: IdempotencyKey}` → `ControlResult` | `restart` 必须带幂等键；其他控制动作不得带键。合法状态表见 §5.5。 |
| `ResumeBlockedRun` | `{run_id}` → `ControlResult` | 仅条件解除且重新规划成功后使原 Run 回到 Pending；见 §5.5。 |
| `RetryFailedTargets` | `{run_id, idempotency_key: IdempotencyKey}` → `RunAccepted` | 仅对 CompletedWithFailures Run 新建只含失败 Page 的 linked Run；wire 与幂等见 §5.5。 |
| `SetRegionType` | `{region_id, new_region_type, expected_revision?: RevisionNo}` → `{region_id, revision_no: RevisionNo, region_type, sfx_policy}` | **`1.4` 修订草案（M2-REGION-RETYPE-CONTRACT）**：region 改标。改标=经既有 commit seam 产生一笔新 revision（origin 恒 `user`），非原地改字段；`new_region_type` 枚举复用 `RegionType` 六值 wire 字符串；错误码零新错误语义（映射表，wire `code` 字面量全部复用既有导出）；改标后 policy 快照规则（EV-8 裁决）与并发/持久性语义以 §5.4 为准。**runtime 已由 M2-REGION-RETYPE-CORE 落地（`PROTOCOL_MINOR=3`，`1.5` 回填）。** |
| `ListRegions` | `{page_id}` → `{"regions": RegionListSummary[], "page_size": {width,height} \| null}`（`1.4` 最小集：`{region_id, region_type, sfx_policy, origin, revision_no}` + `1.5` 可选 `geometry`/`page_size`；**result 包装形状以 §5.4 为准**） | **`1.4` 修订草案（M2-REGION-RETYPE-CONTRACT）**：region 读取面最小 DTO（`RegionListSummary`，`1.4` r1 定名——与 `CreateRegion` result 的 `RegionSummary` 解耦，避免隐式收窄其结构），按 reading_order 升序；不含文本/标注状态（读取面不含训练语义，取舍理由见 §5.4）。**`1.5` additive widening（M2-WORKBENCH-REACT-1）**：可选 `geometry`（归一化，D5 闭合）+ 可选 `page_size`（像素投影），协议 minor 不 bump。注：`CreateRegion` 行 result 引用的 `RegionSummary` 结构在本修订前后均未定义，`CreateRegion` 的 result 语义不在本修订改变范围。 |
| `CreateRegion` | `{page_id, shape: {kind:"rectangle", corners: [NormalizedPoint, NormalizedPoint]} \| {kind:"polygon", points: NormalizedPoint[3+]}}` → `RegionSummary` | 归一化换算使用 app `normalized_to_page_geometry`，几何校验在 Core；image/page bytes 不随命令传输。 |
| `DeleteRegion` | `{region_id}` → `Unit` | Workbench VM 调用 Region deleter；权限、Lock 与 revision 条件由 Core 检查。 |
| `SaveManualTranslation` | `{region_id, text, expected_revision?: RevisionNo}` → `{revision_no: RevisionNo}` | Workbench VM 当前调用编辑 service 保存手工译文。`expected_revision` 是防覆盖 Proposal，精确并发策略 **UNKNOWN**。 |
| `ListRegionRevisions` / `RestoreRegionRevision` | `{region_id}` / `{region_id, revision_no, expected_revision}` → 历史包装摘要 / 恢复结果 | **1.6 RC-4 冻结**：wire `list_region_revisions` / `restore_region_revision` 的精确 DTO、完整快照与 Lock 恢复、事务内 expected 守卫以 [RC-4 契约](M2-RC4_DOMAIN_COMMANDS.md) 为准。新建 restored revision，不改写历史。 |
| `SetRevisionPinned` | `{region_id, revision_no, pinned}` → `Unit` | 仍为未释放 Proposal；RC-4 不新增 pin 写命令。 |
| `ResolvePageResource` | `{page_id}` → `{resource_id, revision}` \| `PAGE_NOT_FOUND` | **`1.7` 冻结（M2-PAGE-RESOURCE-RESOLVE-1）**：wire `resolve_page_resource`，页显示图 → 可 issue 的资源目录键（确定性 `page-original-{page_id}`，幂等；`revision` 恒 `"original"`，产物丢失自愈同键重发布）。发布/查找语义、错误面与 host 不轮换裁定以 Revision history `1.7` 为准，协议 minor 5。 |
| `ListChapters` | `{book_id}` → `{"chapters": [{chapter_id, title, chapter_number, sort_order}]}` | **`1.8` 冻结（M2-PAGE-NAV-PROJECTION-1）**：wire `list_chapters`，book→chapter 导航读取面第一刀；`sort_order` 升序，未知 book_id 返回空数组（零新错误码），协议 minor 6；上方原 PROPOSAL 组合行中的 `ListChapters` 转本行冻结，`CreateChapter`/`DeleteChapter` 仍为 PROPOSAL。 |
| `ListChapterPages` | `{chapter_id}` → `{"pages": [{page_id, source_filename, sort_order}]}` | **`1.8` 冻结（M2-PAGE-NAV-PROJECTION-1）**：wire `list_chapter_pages`，chapter→page 导航读取面第一刀（新名避开 `GetReaderProjection` 的 ReaderProjection 大对象）；导航摘要行不含 managed_original_ref/宽高/锁态，`sort_order` 升序，未知 chapter_id 返回空数组，协议 minor 6。 |
| <a id="rerender-page-command"></a>`RerenderPage` | `{page_id}` → artifact/reports/preview | **1.6 RC-4 冻结**：wire `rerender_page`，同步复用既有 RenderService，无 AI/PipelineRun；错误、skip 原图回填与资源撤销以 [RC-4 契约](M2-RC4_DOMAIN_COMMANDS.md) 为准，协议 minor 4。**category 澄清（M2-CATEGORY-CLARIFY-1，2026-10-07；RC-4 r1 RC4-10）**：失败 envelope 的 `MISSING_REQUIRED_INPUT` → `category="unavailable"`（required input missing 属 §8 值域中的可用性失败，非 not_found 的「目标不存在」；category 值此前从未被任何 revision 冻结，taxonomy 表仍为 Proposal，本注记为实现口径登记，非修订）；`TARGET_NOT_FOUND`→`not_found`、`INPUT_REVISION_CHANGED`→`conflict`、`ARTIFACT_WRITE_FAILED`/其余→`internal` 不变；category/retryable 观察见[RC-4 命令行](M2-RC4_DOMAIN_COMMANDS.md#rc4-rerender-page-command)与[§8 注记](#rerender-page-error-envelope-observation)。 |
| `GetReaderProjection` | `{chapter_id, mode: original\|translated, start_position: resume\|beginning}` → `ReaderProjection` | **2.1 FROZEN**：Core 投影规范阅读布局、逻辑 Page 的尺寸/只读资源引用与该 mode 独立的进度；Webtoon 长图仍是一张 Page，缓存 tile 不成为 Page。DTO 与坐标语义见 §6.3。 |
| `SaveReadingProgress` | `{chapter_id, mode: original\|translated, page_id, scroll_offset_y?, elapsed_seconds_delta?}` → `ReadingProgressSnapshot` | **2.1 FROZEN**：Core 按 `(book_id, chapter_id, mode)` 独立保存位置与阅读时长；Webtoon y 偏移使用逻辑 Page 原图像素坐标。读取面为 `GetReaderProjection`；成功后发 `ReadingProgressChanged`。 |
| `GetSettings` / `SaveSettings` | `{section?}` / `{section, values}` → `SettingsProjection` / `SettingsProjection` | AS-IS 仅证明 Settings VM 在进程内调用 profiles/defaults/credentials services；没有已定义的 `CredentialRef` 类型或 IPC exchange。Credential DTO/exchange 为 UNKNOWN / DEFERRED；secret 不得进入普通事件或日志。**`1.3` 修订（M2-SETTINGS-IPC-CHANNEL）**：本行 transport-neutral 命令名与其 PROPOSAL 等级不变；产品 Tauri 面落地为 §5.3 的 `settings_get` / `settings_update_section`（请求/响应/错误码与写入端校验以 §5.3 为准）。 |
| `StartExport` | `{book_id, chapter_ids, ordered_page_ids, format, format_options, stale_policy, target_ref: ExportTargetRef}` → `ExportAccepted` | **2.1 FROZEN**：format=`png\|zip\|cbz\|pdf\|text`；输出当前可用的翻译成果，`png` 要求恰一页。页序是请求指定的冻结顺序。`target_ref` 是 Tauri host 签发的单次写授权；Core 验证、解析并消费，见 §10.3。 |
| `CancelExport` | `{export_id}` → `ExportProgressSnapshot` | **2.1 FROZEN**：请求取消活动导出；响应与后续查询都返回 Core 快照。已原子发布的成功结果不回滚；终态和清理见 §6.3。 |
| `GetExportSnapshot` | `{export_id}` → `ExportProgressSnapshot` | **2.1 FROZEN**：读取接受中的进度或终态结果；事件仅作提示，见 §6.3。 |
| `GetExportHistory` | `{}` → `{"exports": ExportHistoryEntry[]}` | **2.1 FROZEN**：读取 Core 持久的 ExportHistory，含选择的输出路径；此命令只供可信 Tauri host 使用，host 不得将路径或写引用转发给 WebView。 |

### 5.5 Run Runtime wire surface（P13-C1，冻结）

本小节 supersede §5 中 Run 相关 proposal 行；名称大小写是 `command` 字段的 wire 值。所有请求继续使用 §3 的 `Request<T>` / `Response<T>`，错误使用 §8 `ErrorEnvelope`。新运行操作是 Core 唯一调度入口的 IPC adapter；不得在 UI、bridge 或外围队列重建目标、另建 scheduler 或直接写 Run。

| `command` | `payload` | 成功 `result` | P11 行为来源 |
|---|---|---|---|
| `StartRun` | `{command: PipelineCommand, scope: PipelineScope, overrides?: JsonObject, idempotency_key: IdempotencyKey}` | `RunAccepted` | §2.1–§2.2、§3.1–§3.3 |
| `ControlRun` | `{run_id: RunId, action: pause\|continue\|stop\|restart\|abandon, idempotency_key?: IdempotencyKey}` | `ControlResult` | §2.1、§3.1、§4.2–§4.5、§6.2 |
| `ResumeBlockedRun` | `{run_id: RunId}` | `ControlResult`（`action="resume_blocked"`） | §3.1、§4.2、§4.5 |
| `GetRunSnapshot` | `{run_id: RunId}` | `RunSnapshot` | §3.1、§3.2–§3.3、§6.1 |
| `GetTaskProjection` | `{run_id: RunId}` | `TaskProjection` | §3.1、§7.2 |
| `RetryFailedTargets` | `{run_id: RunId, idempotency_key: IdempotencyKey}` | `RunAccepted` | §2.1–§2.2、§3.1、§3.3、§5.3 |

DTO 与幂等语义：

- `RunAccepted = {run_id: RunId, status: PipelineRunStatus}`。新 Run 的首次成功响应 `status="pending"`；同键重放返回该 Run 当前状态。响应只能在 §2.2 所列 Run、幂等记录、固定顺序的目标及执行快照作为同一持久化事务提交后发送。事务提交前失败必须返回错误；提交后响应丢失时，同键重放须找回原 Run。
- `idempotency_key` 是调用方生成的 opaque string，在同一 Core 数据库中跨创建 Run 操作唯一并随 Run History 保留。`StartRun` 与 `RetryFailedTargets` 必填；`ControlRun(action="restart")` 必填；其他 `ControlRun` 动作及 `ResumeBlockedRun` 不得传入该字段。新键尝试一次 durable acceptance；同键同 fingerprint 返回同一 `run_id` 和当前状态，不重新展开目标或重取快照；同键异 fingerprint 返回 `IDEMPOTENCY_KEY_REUSED`，不改写原 Run；同内容不同键创建独立 Run。`request_id` 不参与 fingerprint 或去重。
- fingerprint 输入依 P11 §2.1：操作类型（含 `PipelineCommand`）、规范化 scope（含显式目标及顺序）、适用时的来源 Run、用户执行选项（`overrides`）。它不含首次接受时才读取并冻结的当前 Revision、Lock、settings、Provider、constraint、context 或展开后的目标结果。`RetryFailedTargets` 的 fingerprint 包含来源 Run 与其冻结的失败 Page 集合；`restart` 的 fingerprint 包含被处置的 Interrupted Run。
- `ControlResult = {run_id: RunId, status: PipelineRunStatus, new_run_id?: RunId, new_run_status?: PipelineRunStatus}`。`run_id/status` 始终指被请求的原 Run；仅 `restart` 返回 `new_run_id` 与 `new_run_status`。首次接受时 child 状态为 `pending`；同键重放返回同一 child 的当前状态。原 Run 保持 `interrupted`，旧 Run disposition 与 child Run 必须原子持久化。其他动作不得返回两个 `new_run_*` 字段。成功控制响应中的状态是响应时 Core 权威状态；pause/stop 请求已持久化但尚未到安全边界时原 Run 仍可为 `running`。
- `RunSnapshot` 是只读的 Core 持久 Run 视图，至少含 `{run_id, command, scope, status, targets: [{target_id, target_type, order}], source_run_id?, retry_reason?}`。`targets` 是接受时冻结且有序的成员，不随当前 UI selection 变化；不得在该 DTO 中暴露凭据、secret 或本地绝对路径。它不是恢复真值的替代品；Core 仍以完整持久 Run/Task/StepRun 与执行快照恢复。
- `GetTaskProjection` 返回 §6.1 冻结的只读 `TaskProjection`。统计、Page rows、Task/Step 详情、current Page / Step 与 controls 必须由同一权威 Run/Task/StepRun 数据源生成，PageList 不得另行查询或重算另一份状态。
- `RetryFailedTargets` 只接受 `completed_with_failures` 且至少含一个失败 Page 的 Run；新 Run 只冻结该来源 Run 的失败 Page，写入 `source_run_id` / `retry_reason="retry_failed_targets"`，源 Run 与其历史不变。没有失败 Page 复用 `TARGET_NOT_FOUND`；状态不合法使用 `INVALID_RUN_TRANSITION`。

Control 与恢复状态矩阵（完整枚举来自 P11 §4.2/§4.5；未列为合法的动作均拒绝且不得有副作用）：

| 请求时的 Run 状态 | 合法 Core/IPC 操作 | 必须拒绝的操作 | 状态结果与边界 |
|---|---|---|---|
| `Pending` | scheduler start；`ControlRun(stop)` | `pause`、`continue`、`restart`、`abandon`、`ResumeBlockedRun`、`RetryFailedTargets`、恢复扫描改写 | scheduler start → `running`；stop → `cancelled`，未开始 Task 转 `cancelled`。 |
| `Running` | `ControlRun(pause)`、`ControlRun(stop)`；仅启动恢复可标记 `interrupted` | `continue`、`restart`、`abandon`、`ResumeBlockedRun`、`RetryFailedTargets`、第二次 scheduler start | pause 先持久化请求，当前不可安全中断的 Step 可完成，到安全边界后不再开始下一 Step 并转 `paused`；stop 先持久化请求，停止剩余工作并转 `cancelled`，已提交成果保留。 |
| `Paused` | `ControlRun(continue)`、`ControlRun(stop)` | 再次 `pause`、`restart`、`abandon`、`ResumeBlockedRun`、`RetryFailedTargets`、崩溃恢复改写 | continue → `running`，使用原接受快照从首个未完成/stale Step 继续；stop → `cancelled`。 |
| `Blocked` | 条件解除且重新规划成功后的 `ResumeBlockedRun`；`ControlRun(stop)` | `pause`、`continue`、`restart`、`abandon`、`RetryFailedTargets`、直接执行未重新规划的旧计划 | Resume 成功 → `pending`；条件未解除或重新规划失败时拒绝且无副作用。stop → `cancelled`。 |
| `Interrupted` 且无处置 disposition | `ControlRun(continue)`、`ControlRun(restart)`、`ControlRun(abandon)` | `pause`、`stop`、普通 scheduler start、`ResumeBlockedRun`、`RetryFailedTargets` | continue 校验后同 Run → `running`；restart 原 Run 保持 `interrupted` 且标记 restarted，原子创建 `pending` child；abandon 原 Run → `cancelled` 并记录 abandonment，不建 child、不回滚成果。 |
| `Interrupted` 且 disposition=`restarted` | 仅用原 restart key/fingerprint 重放并取回既有 child Run | 新的 `continue`、`restart`、`abandon`、`pause`、`stop`、普通 scheduler start、`ResumeBlockedRun`、`RetryFailedTargets` | 不得重复创建 child；原 Run 保持 `interrupted`。 |
| `Completed` | 无 | 对该 Run 的所有控制、恢复、再次启动/执行与 `RetryFailedTargets` | 终态不变；独立的新 `StartRun` 仍可创建另一个 Run。 |
| `CompletedWithFailures` | `RetryFailedTargets` | 对该 Run 的所有控制、恢复、restart 或再次执行 | 原 Run 不变；新 `pending` Run 只含失败 Page。 |
| `Failed` | 无 | 对该 Run 的所有控制、恢复、再次启动/执行与 `RetryFailedTargets` | 终态不变；新尝试必须显式 `StartRun` 创建另一 Run。 |
| `Cancelled` | 无 | 对该 Run 的所有控制、恢复、再次启动/执行与 `RetryFailedTargets` | 终态不变；不得复活已取消 Run；新 Run 必须通过新的 `StartRun` 创建。 |

- 对任一状态：未知 `ControlRun.action` 或 payload 不合法返回 `INVALID_REQUEST`（`validation`）；已知操作在当前状态非法、blocked 条件未满足、restart disposition 不符或 retry 状态门不符，返回 `INVALID_RUN_TRANSITION`（`conflict`，`retryable=false`）；Run 不存在返回既有 `TARGET_NOT_FOUND`（`not_found`）；幂等键复用冲突返回 `IDEMPOTENCY_KEY_REUSED`（`conflict`）。错误响应 `result=null`；拒绝不得改写 Run、Task、StepRun、current Revision 或历史。
- scheduler start 与 startup recovery 是 Core 内部生命周期，不是客户端可伪造的 `ControlRun` action。startup recovery 只可在 P11 §6.1 的旧 scheduler owner 已确认退出后处理原 `running` Run。
- 以上 wire 只暴露 P11 已冻结操作，不新增用户可见动作、目标类型、暂停/停止策略或状态；当前 `PipelineService` 个别实现与 P11 的差异不构成 wire 行为来源，P11 §4–§7 是规范行为。

### 5.1 Task command types

1.6 RC-4 的 UI 重渲染本页使用同步 `rerender_page`，承载既有设计稿的页重渲染意图；不以 `rerender_single` 的通用 PipelineRun runtime 作为本切片前提，不声称该命令族已接通。

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

### 5.6 ImportPages（P12-C1，冻结）

本小节只冻结 Python Core command wire。`ImportPages` 是同步 request/response：成功返回最终 `ImportReport`；错误使用 §8 `ErrorEnvelope`。此定义既不声称 command 已实现，也不增加 Tauri command name、文件选择器行为或导入 UI。

```text
ImportPages = {
  chapter_id: ChapterId,
  sources: ImportSourceRef[],                 # 必填且非空
  duplicate_policy?: "skip" | "import_as_new" # 缺省 "skip"，沿用 P09
}

ImportReport = {
  chapter_id: ChapterId,
  duplicate_policy: "skip" | "import_as_new",
  cancelled: boolean,
  sources: ImportSourceResult[]
}

ImportSourceResult = {
  source_index: integer,                       # 与 request.sources 对应，0-based
  source_name: string,                         # 仅选中项 basename，不含路径
  files: ImportFileResult[]
}

ImportFileResult = {
  filename: string,                            # basename；保留 Unicode，不含路径
  outcome: imported | skipped | rejected | pending | partial,
  source_sha256: Sha256 | null,                # 本次读取源文件字节的 SHA-256
  pages: ImportPageResult[],
  error: ImportItemError | null,
  side_effects: none | listed_pages_committed | temporary_artifact_possible | managed_orphan_possible
}

ImportPageResult = {
  page_index: integer,                          # 1-based；图片为 1，PDF 使用原始页序
  outcome: imported | skipped_duplicate | rejected | pending,
  page_id: PageId | null,
  source_order: integer | null,
  sort_order: integer | null,
  sha256: Sha256 | null,                        # 成功或已读到可哈希字节时为小写 64 位 hex
  width: integer | null,                        # 成功时为真实正整数像素尺寸
  height: integer | null,
  duplicate: boolean,                           # 按 Chapter 活动 Page 和本批已导入 Page 判定
  error: ImportItemError | null,
  side_effects: none | page_committed | managed_orphan_possible
}

ImportItemError = {
  code: string,                                 # 稳定源 code；不得用 message 分支
  category: validation | not_found | conflict | unavailable | cancelled | internal | unknown,
  message?: string,                             # 安全短消息，不得包含路径或 stack
  retryable: true | false | unknown
}

Sha256 = string                                 # exactly 64 lowercase hexadecimal characters
```

- `sources` 必须非空，所有 `ImportSourceRef` 与目标 Chapter、payload 和授权均在首次读取之前验证。畸形请求/策略返回 `INVALID_REQUEST`；Chapter 不存在返回 `TARGET_NOT_FOUND`；引用拒绝使用 §10.4 的稳定 `REF_*` code。此类命令级拒绝 `result=null`，且不读来源、不创建 temp/Managed Original、不写 SQLite；错误不得暴露路径、引用内容或签名。
- `sources` 中每个引用对应一个用户显式选择的图片/PDF 文件、显式选择的图片文件集合中的单文件，或文件夹。文件夹只允许 P09 冻结的**直接子项**，不递归；文件夹任一路径段/子项出现 symlink、junction 或 reparse point 时拒绝该文件夹整体。图片仅接受 P09 已列扩展名 `.png`、`.jpg`、`.jpeg`、`.webp`、`.gif`、`.bmp`；文档仅接受 PDF。MOBI、CBZ、网页、缩略图和其他格式不在此 wire。
- `ImportSourceResult.source_index` 定位请求中的选择项；文件夹展开后的每个子文件单独出现在 `files`，单文件引用只含对应文件结果。只返回 basename，不返回用户源绝对路径、相对路径、URI、引用或可还原路径的内容。文件名按 Unicode 原样保留。
- `ImportFileResult.source_sha256` 是 Core 从该文件本次只读取得的源字节 SHA-256，用于 AC-IMPORT-002 的后续源保护对照；未知或在拒绝前未读取时为 `null`。`ImportPageResult` 是每个待导入页的结果。图片对应一页；PDF 按原始页序输出。成功页的 `sha256` 是 Page/Managed Original 字节的 SHA-256：图片为源图逐字节副本，PDF 为该页渲染 PNG；因此 PDF 源 hash 与页 hash 不同。成功的 `width`/`height` 是 decoder/raster 的真实尺寸。成功页同时返回其 `page_id`、不可变 `source_order` 与提交时的 `sort_order`。失败/跳过/待处理且未建 Page 的字段为 `null`；已解码的重复页仍报告 hash、实际尺寸与 `duplicate=true`。
- `duplicate_policy` 沿用 P09 既有策略：缺省 `skip`，按页面内容 SHA-256 在目标 Chapter 的活动 Page 与本批前序成功页中检测；重复页为 `skipped_duplicate`，不得写 Page 或创建/覆盖 Managed Original。仅显式 `import_as_new` 才为重复页新建 Page ID 与不可变 Managed Original；不得覆盖既有项。软删除 Page 不阻止重导入，但 `source_order` 不复用。
- 文件级来源校验、解码、重复判定、Managed Copy 原子发布与 SQLite Page 提交遵循 P09 顺序。图片解码失败和 PDF 格式/加密/损坏/零页/任一页渲染失败以具体 code/category 拒绝；PDF 完整预检失败时整份文件在首次 Copy 前拒绝，零 Page、Managed Original 与 temp。对这些 preflight 拒绝，`side_effects="none"` 可判定；其它来源可独立成功，因此报告不承诺整批原子回滚。
- P09 导入错误的 wire `category` 固定为：`SOURCE_READ_FAILED`=`unavailable`，`INVALID_IMAGE` / `INVALID_DOCUMENT` / `ENCRYPTED` / `UNSUPPORTED_FORMAT`=`validation`，`MISSING_DEPENDENCY`=`unavailable`，`COPY_FAILED`=`internal`。`INVALID_REQUEST`=`validation`、`TARGET_NOT_FOUND`=`not_found`；引用类 `REF_MALFORMED` / `REF_SIGNATURE_INVALID` / `REF_SCOPE_DENIED` / `REF_OUT_OF_SCOPE` / `REF_REPARSE_POINT`=`validation`，`REF_EXPIRED` / `REF_REVOKED`=`conflict`，`REF_UNKNOWN_ID` / `REF_NOT_FOUND`=`not_found`，`FILE_IDENTITY_CHANGED` / `FILE_SIZE_CHANGED` / `CONTENT_DIGEST_MISMATCH`=`conflict`。其它未映射异常保留原 code，并按 §8 使用 `unknown`，不得靠 message 推导。
- `COPY_FAILED` 不创建 Page；pending 页没有 Page 或 Managed Original。若 Page SQLite 事务在 Managed Original 原子发布后失败，依 P09 允许保留完整、不可见的 Managed Original 孤儿；对应错误不得伪报零副作用，`side_effects="managed_orphan_possible"`。Page 永远不得先于其完整 Managed Original 提交。
- 若操作在中途被取消，`cancelled=true`，已成功提交的 Page 保留，未处理页为 `pending` 且其 `side_effects="none"`；已处理项的副作用逐项报告。事件、重连、重放或取消控制命令不由本节新增。
- 同步响应错误使用 §8；未映射异常保留源 code 或 `UNKNOWN`，不得把未知错误伪装为零副作用拒绝。拒绝错误及 `ImportItemError.message`/`details` 不得包含本地路径、grant 内容、签名材料、stack 或 Secret。

### 5.7 HostControl：host-only grant registration / revoke（HOST-ISSUER-1-C1，冻结）

本节冻结 host 到**同一 live Core 实例**的授权控制面。它不属于 §3 普通 application `Request<T>` command catalog，也不是 Tauri command。唯一通道是 Tauri host 直接 spawn 并持有 `bootstrap.core_service` 子进程的既有 stdio JSON-lines channel（`StdioLibraryChannel`）；HostControl 用独立 envelope 在这条 host-owned 进程通道中传输，不新增监听端口或第二个 sidecar。它不是 `core_bridge.rs` 的 resource-channel sidecar。Tauri 内部 bridge 负责传输，React/WebView 无此进程句柄、原始 stdio 或 credential，也没有接收任意 HostControl envelope 的 Tauri command；**HostControl commands MUST NOT 由 React/WebView 调用**。注册的绝对路径、grant 事实、HMAC signing key 与签名只允许在该可信通道中出现；不得回显到 WebView、普通事件、日志或错误。

```text
HostSessionCredential = string                 # URL-safe Base64 of 32 CSPRNG bytes

OpenHostSession = {
  protocol: "new-manga.core",
  version: { major: 2, minor: 3 },
  request_id: OpaqueId,
  channel: "host-control",
  command: "OpenHostSession",
  payload: {
    host_session_id: OpaqueId,
    host_session_credential: HostSessionCredential
  }
} -> { core_session_id: OpaqueId }

HostControlRequest<T> = {
  protocol: "new-manga.core",
  version: { major: 2, minor: 3 },
  request_id: OpaqueId,
  channel: "host-control",
  core_session_id: OpaqueId,
  host_session_id: OpaqueId,
  host_session_credential: HostSessionCredential,
  command: HostControlCommand,
  payload: T
}

HostControlResponse<R> = Response<R>                   # §3 envelope
HostControlCommand = RegisterImportSource | RevokeImportSource
                  | RegisterExportTarget | RevokeExportTarget | CloseHostSession

RegisterImportSource = {
  grant_id: OpaqueId,
  session_id: OpaqueId,                       # must equal authenticated host_session_id
  scope_class: "user-source",
  operation: "ImportPages",
  access: "read-only",
  source_path: AbsolutePath,                   # host/Core only
  source_kind: "file" | "directory",
  scope_identity: [volume_serial: uint, file_index: uint] | null,
  entries: [{
    path: AbsolutePath,
    facts: { volume_serial: uint, file_index: uint, size: uint, sha256: Sha256 }
  }],
  expires_at: UnixTimeSeconds,
  signing_key: HostSigningKey,                 # base64url; decoded length >= 32 bytes
  signature: string
} -> { registered: true }

RevokeImportSource = { grant_id: OpaqueId } -> { revoked: true }

RegisterExportTarget = {
  grant_id: OpaqueId,
  session_id: OpaqueId,                       # must equal authenticated host_session_id
  target_path: AbsolutePath,                   # host/Core only
  format: ExportFormat,                       # §5 StartExport enum
  replace_existing: boolean,
  expires_at: UnixTimeSeconds,
  signing_key: HostSigningKey,                 # base64url; decoded length >= 32 bytes
  signature: string
} -> { registered: true }

RevokeExportTarget = { grant_id: OpaqueId } -> { revoked: true }
CloseHostSession = {} -> { closed: true }

HostSigningKey = string                       # base64url encoding of host HMAC key
AbsolutePath = string                         # absolute OS path; host/Core private boundary only
UnixTimeSeconds = number                      # finite seconds since Unix epoch
```

注册 payload 与 P09-FU2 `CoreServiceServer._register_import_source`、P16 `_register_export_target` 的既有私有 seam 输入一一对应；撤销 payload 与对应 `_revoke_*` seam 一一对应。导入 `scope_identity` 对目录必填、对单文件为 `null`；`entries` 的直接子项、自然序、格式、来源身份与 hash 约束严格沿用 §10.4/P09。Grant scope、签名输入、有效期上限及 `ExportFormat` 严格沿用 §10.3/§10.4 和 §5，不在本节另行定义。

**Wire reference 不变**：成功注册只回 `{registered: true}`；导入 host 用该请求中同一 `grant_id` 与 `signature` 形成既有 `{grant_id, host_signature: signature}` `ImportSourceRef`，导出 host 按 §10.3 原样构造 `ExportTargetRef`。Host session credential、`core_session_id`、路径、scope facts 与 signing key 均不得加进两种 ref，也不得改其签名字段或既有消费者 payload。每条注册请求只处理一个 grant；本节不设用户选择数量、grant 上限或多来源选择策略。

**Host-only 拒绝**：Core 为每个进程生成新的 `core_session_id`。Tauri host 在向 WebView 暴露普通 Core 操作前，只能经其 direct-child stdio channel 内部调用一次 `OpenHostSession`；host 生成并保管 credential，Core 将其与 `host_session_id` 及当前 `core_session_id` 绑定。之后每个 `HostControlRequest` 必须带这三项，Core 对 credential 做常数时间比较并校验当前进程/活动 session。React 侧只有现存、显式登记的 Tauri command wrapper，不得有通用 raw-Core passthrough；HostControl 方法只留在 Rust 内部 bridge。普通 §3 `Request<T>` dispatcher 不注册上述命令；收到没有 `channel: "host-control"` 的同名 command 时返回 `HOST_ONLY_REQUIRED`，不得尝试解析路径或调用注册 seam。HostControl envelope 中缺失/错误/关闭的 host session 返回 `HOST_SESSION_INVALID`；指向另一 Core 进程的 request 返回 `CORE_SESSION_MISMATCH`。HostControl credential 与 grant 的 HMAC key 是不同 secret。

**Session 生命周期**：一个 Core 进程最多接受一个 host session。每个 grant 同时绑定该 host session 与当前 Core 进程 session；前者使用现有注册表的 `session_id`，后者仅保存在 Core 内存 registry/control state，不进入 ref 或签名对象。`CloseHostSession` 在返回成功前撤销该 session 登记的所有未完成 grant，并清除活动 credential；host control channel 断开执行同一失效动作。该 Core 进程不接受第二个 session；host session 轮换时关闭并重启 Core，再用新 `core_session_id` 建立新 session。Core 关闭/崩溃/重启时内存 registry 消失；新 Core 的 `core_session_id` 不同且旧 refs 不可用（旧 grant 在新 registry 中按现有 `REF_UNKNOWN_ID` 语义拒绝）。同一实例在显式 session close 后、停机前仍保留 revoked tombstone，使旧 ref 按既有 §10.3/§10.4 返回 `REF_REVOKED`。

**错误与副作用**：HostControl 错误使用 §3 `Response` / §8 `ErrorEnvelope`，`result=null`。HostControl 外层 envelope 畸形或包含未知字段时使用 `INVALID_REQUEST`；注册/撤销 grant payload 的形状错误继续使用既有 `REF_MALFORMED`，不重解释 `REF_*`。message 不含路径、credential、grant、签名或 stack。

| 条件 | `code` / `category` | 结果与副作用 |
|---|---|---|
| 同一 Core process 第二次打开 host session（包括先前已关闭后） | `HOST_SESSION_ALREADY_OPENED` / `conflict` | 拒绝；不替换或重建 session；host 轮换必须重启 Core。 |
| 注册 ID 已存在 | `GRANT_ALREADY_REGISTERED` / `conflict` | 拒绝；不覆盖、不续期、不改变原 grant。 |
| 撤销未知 grant | `REF_UNKNOWN_ID` / `not_found` | 拒绝；registry、库与文件均不变。 |
| 普通 JSON-RPC 尝试调用 host-only 操作，或 HostControl 缺少 `channel` | `HOST_ONLY_REQUIRED` / `validation` | 拒绝；不调用 seam。 |
| HostControl credential 缺失/错误，或 host session 已关闭/无效 | `HOST_SESSION_INVALID` / `conflict` | 拒绝；不调用 seam。 |
| `core_session_id` 与当前 Core 不符 | `CORE_SESSION_MISMATCH` / `conflict` | 拒绝；不调用 seam。 |
| payload `session_id` 不等于已认证 host session，或 scope 越权/逃逸 | `REF_SCOPE_DENIED` / `validation`、`REF_OUT_OF_SCOPE` / `validation` | 沿用既有 `REF_*`；不登记 grant。 |
| DTO 畸形或签名无效 | `REF_MALFORMED` / `validation`、`REF_SIGNATURE_INVALID` / `validation` | 沿用既有 `REF_*`；不登记 grant。 |
| 注册时 grant 已过期/超过既有有效期约束 | `REF_EXPIRED` / `conflict` | 沿用 §10.3/§10.4；不登记 grant。 |
| 引用消费时 grant 已过期/已撤销 | `REF_EXPIRED` / `conflict`、`REF_REVOKED` / `conflict` | 沿用 §10.3/§10.4；拒绝消费。 |

注册只有在所有 session、DTO、scope、expiry、签名与重复 ID 检查通过后才可原子写入对应的进程内 registry。任一拒绝不改变 registry，不读入来源内容、不写临时文件/目标文件、不写 SQLite。成功撤销在 registry 标记已生效后才响应；其后开始的解析/消费立即看到 `REF_REVOKED`。与 registry 锁竞争的已完成原子消费，及已打开的 Import 验证 handle/已接受的 Export operation，按 §10.3/§10.4 现有生命周期继续；撤销不删除已发布结果，也不新增取消语义。重复撤销沿用现有 seam 的幂等成功 `{revoked: true}`。

运行状态：本节只冻结 wire，不声称任何 HostControl handler、credential 生命周期或 host issuer 已实现；见 §12 授权边界。

## 6. Typed projections 与 events

### 6.1 Task projection

**P13-C1 FROZEN — wire DTO。** 下列形状冻结 P13 的 Run 查询投影，但不表示 IPC 已实现。基础字段来自 `application.tasks.projection.TaskProjection`；page counts 归组到 `counts`、`can_*` 能力归组到 `controls`，tuple 编码为 JSON array，`step_flow` 三元组编码为具名对象。新增的 `tasks` / `steps` 暴露 P11 §7.2 所需的错误、retry 与可得执行详情；它们仍是同一权威 Run/Task/StepRun 投影，不是新的状态存储。

```text
run_id: RunId
run_status: PipelineRunStatus
run_title: string
overall_progress: number             # 0..1，terminal/planned step units
current_page_id: PageId | null
current_step_type: string             # 无当前 Step 时为空字符串
step_flow: StepFlowItem[]             # {type,label,state}
rows: PageProjectionRow[]
tasks: TaskProjectionTask[]
counts: {total: integer, completed: integer, failed: integer, skipped: integer,
         blocked: integer, waiting: integer, processing: integer}
blocked_reasons: string[]
controls: {can_pause: boolean, can_stop: boolean, can_continue: boolean,
           can_restart: boolean, can_abandon: boolean, can_retry_failed: boolean}
extra: Record<string, string>

PageProjectionRow = {
  page_id: PageId, page_order: integer, filename: string,
  status: PageProjectionStatus, is_locked: boolean,
  is_pipeline_current: boolean, error_code: string | null
}
PageProjectionStatus = waiting | processing | completed | failed | blocked | skipped
StepFlowItem = {type: string, label: string,
                state: pending | running | completed | failed | skipped}
TaskProjectionTask = {
  task_id: string, page_id: PageId, status: PipelineTaskStatus,
  error_code: string | null, error_message: string | null,
  steps: TaskProjectionStep[]
}
TaskProjectionStep = {
  step_run_id: string, step_type: string, status: StepRunStatus,
  retry_no: integer, error_code: string | null, error_message: string | null,
  provider: string | null, model: string | null, device: string | null
}
```

`PipelineRunStatus`、`PipelineTaskStatus`、`StepRunStatus` 分别复用领域枚举的现有 wire 值。其值域为：Run `pending | running | paused | blocked | completed | completed_with_failures | failed | cancelled | interrupted`；Task `pending | running | completed | failed | blocked | skipped | cancelled | interrupted`；StepRun `pending | running | completed | failed | cancelled | interrupted`。这些 status 域互不替代。`overall_progress` 在无 planned step units 时为 `0`，否则是 terminal/planned step units 比值；counts 为非负整数。`rows` 按 `page_order` 升序、`page_id` 次序稳定打破并列；`tasks` 保持其 Run 内顺序，每个 Task 的 `steps` 保持 StepRun 创建顺序。`blocked_reasons` 只列权威投影中可得的阻塞原因，没有已知原因时为空数组。`controls` 只提示 P11 状态矩阵下动作是否可用，Core 仍须在命令边界重新验证。`extra` 保留既有 string map，不赋予新的业务语义。

字段映射（左侧为 AS-IS dataclass，右侧为冻结 wire DTO）：

| AS-IS flat field(s) | Frozen wire field | Mapping |
|---|---|---|
| `run_id`, `run_status`, `run_title`, `overall_progress`, `current_page_id`, `current_step_type` | 同名字段 | 字符串/数值/nullable scalar 原样编码；无当前 Step 时为空字符串。 |
| `step_flow: tuple[tuple[str, str, str], ...]` | `step_flow: StepFlowItem[]` | 每个 `(type, label, state)` tuple 改写为 `{type, label, state}` 对象；`state` 使用上方闭集。 |
| `rows: tuple[PageProjectionRow, ...]` | `rows: PageProjectionRow[]` | tuple 序列化为数组；完整行字段和 Page status 闭集见上方 DTO。无 error code 编码为 `null`。 |
| `PipelineRun.tasks` 与各 `PipelineTask` | `tasks: TaskProjectionTask[]` | 每个 Task 投影其 task/page ID、Task status、错误码/安全短消息及其 StepRun 明细；不得从另一查询源拼接。 |
| `PipelineTask.step_run_ids` / `PipelineRun.step_runs` | `TaskProjectionTask.steps: TaskProjectionStep[]` | 按所属 Task 取回已持久 StepRun；透传 `retry_no` 与状态；错误消息须符合 §8 安全短消息要求。 |
| 冻结 Provider binding / 可得 StepRun 执行 provenance | `provider`, `model`, `device` | 各为可空字符串；只返回本 Run 的权威冻结绑定或已记录的实际执行值。没有可核实值为 `null`，不得从当前全局设置推断或伪造。 |
| `PipelineTask.error_code/error_detail`, `StepRun.error_code/error_detail` | 各自 `error_code/error_message` | `error_code` 保留稳定码；`error_message` 只允许 §8 的安全短消息，不得直出原始 `error_detail`、异常栈、路径或 secret；无安全消息时 `null`。 |
| `total_page_count`, `completed_page_count`, `failed_page_count`, `skipped_page_count`, `blocked_page_count`, `waiting_page_count`, `processing_page_count` | `counts: {total, completed, failed, skipped, blocked, waiting, processing}` | 仅分组与缩短 wire key；逐项分别对应上述 count 字段。 |
| `blocked_reasons: tuple[str, ...]` | `blocked_reasons: string[]` | tuple 序列化为数组。 |
| `can_pause`, `can_stop`, `can_continue`, `can_restart`, `can_abandon`, `can_retry_failed` | `controls: {can_pause, can_stop, can_continue, can_restart, can_abandon, can_retry_failed}` | 嵌套分组；逐项同名映射；值须与 §5.5 合法动作矩阵一致。 |
| `extra: Mapping[str, str]` | `extra: Record<string, string>` | 保留额外字符串键值；序列化为 JSON object。 |

`retry_no` 是所属 Step 的零起始 retry ordinal（`0` 为首次 attempt）；每次真实重试有独立 StepRun，先前失败 StepRun 保留。Progress 分母/分子使用 step units；不得换成已处理页数/总页数。页面优先级为 `failed > processing > blocked > completed > skipped > waiting`；此优先级是 Page row 归并，不改变 Run `status`。Provider / Model / Device 缺值只表示当前持久记录没有可验证真值，不代表产品选择或执行 fallback。执行详情不得包含 Provider endpoint URL、credential、secret、异常栈或本地绝对路径。

### 6.2 Event catalog

以下 event 中明确标为 **FROZEN** 的 payload 仅冻结 wire；其他仍为 **PROPOSAL**。事件是状态变化通知，不代替快照：

| Event | Payload | Evidence level |
|---|---|---|
| `RunStatusChanged` | `{run_id, status: PipelineRunStatus, changed_at}` | 状态失效通知；Run runtime event 未实现。 |
| `RunProgressChanged` | `{run_id, projection: TaskProjection}` | **UNKNOWN / PROPOSAL**；本修订不冻结此普通进度推送事件。调用方可重新查询 `GetTaskProjection`；普通百分比刷新目标和四类立即事件见本节末尾及 P11 §7.3。 |
| `RunFinished` | `{run_id, final_status}` | 当前 RunController/VM 有 finished 信号；IPC event 未实现。 |
| `RunCrashed` | `{run_id, error: ErrorEnvelope}` | 当前 UI crash signal 只有 text；将结构化错误带入 IPC 是 Proposal，现存 crash 未映射到稳定业务 code。 |
| `TaskFailed` | `{run_id, task_id, page_id?, error_code?}` | **P13-C1 frozen minimum**；在失败 Task 状态持久化后立即推送。 |
| `RunPaused` | `{run_id, status: "paused"}` | **P13-C1 frozen minimum**；只在实际 Run 状态持久化为 paused 后推送，不表示 pause request 刚提交。 |
| `RunCompleted` | `{run_id, status: "completed"\|"completed_with_failures"}` | **P13-C1 frozen minimum**；在终态完成聚合持久化后立即推送；失败页仍保留其成功成果。 |
| `CurrentPageStepChanged` | `{run_id, current_page_id: PageId\|null, current_step_type: string}` | **P13-C1 frozen minimum**；current Page/Step 投影值改变后立即推送。 |
| `CoreAvailabilityChanged` | `{state: starting\|ready\|stopping\|unavailable, reason?: ErrorEnvelope}` | **UNKNOWN / PROPOSAL**；当前 Core process/session event 不存在。 |
| `ImportProgressChanged` | `{operation_id, completed?, total?, status}` | **UNKNOWN / PROPOSAL（P12-C1 明确保留未冻结）**：P09 只有同步 `ImportReport` 与可取消的应用层 use case，没有持久 `operation_id`、导入 snapshot/query 或恢复 wire。单独冻结事件会隐含未定义的 operation 生命周期且无法给出真值；未来需先由独立授权冻结可查询的 Core snapshot，再决定是否加事件。 |
| `ExportProgressChanged` | `{export_id, status, completed_pages, total_pages}` | **2.1 FROZEN**；仅为失效提示，不携带目标路径；调用方读取 `GetExportSnapshot`。 |
| `ReadingProgressChanged` | `{book_id, chapter_id, mode}` | **2.1 FROZEN**；仅为失效提示；调用方重新读取 `GetReaderProjection`。 |

P13-C1 的四类事件为 §3 `Event<T>` envelope 内的 unrequested messages；它们与 `Response<T>` 共用现有 Python Core stdio JSONL stream：每条 stdout line 是一个完整 Request、Response 或 Event JSON object，Response 以 `request_id` 配对，Event 以 `event_id` 识别；事件可与请求响应交错，Core 必须串行化写出完整行。stdout 只承载协议行，诊断继续写 stderr。没有单独的事件 subscribe 命令。

普通百分比投影刷新目标为最多约 4 Hz；调用方使用 `GetTaskProjection` 读取当前投影。上述四类重要事件在对应持久状态/投影变更提交后立即推送，不因普通进度节流而延迟。Event 是提示与失效通知，不是状态真值；不承诺至少一次/至多一次、顺序号、重放或重连送达。连接恢复后，客户端必须重新调用 `GetRunSnapshot` / `GetTaskProjection`；不得从事件自行重建持久状态。当前 Qt signal 名称不是 wire contract，未来不得以 QVariant/QObject 对象作为消息类型。

P16-C1 的 `ExportProgressChanged` 与 `ReadingProgressChanged` 同样封装为 §3 `Event<T>`，与请求/响应共用 JSONL stream；仅在相应进度快照持久化后发出。两事件只提示调用方重新查询，不保证送达/重放/排序，也不携带文件路径、`ExportTargetRef` 或可重建业务状态的内容。Reader 以 `GetReaderProjection`、Export 以 `GetExportSnapshot` / `GetExportHistory` 的 Core 快照为真值。上述规则不改变 P13 四类 Run 事件。

### 6.3 Reader / Export projections 与任务快照（P16-C1，冻结）

以下 DTO 在 rev 2.1 冻结；资源引用沿用 §10.2 的只读 `ResourceRef` 安全语义。路径、文件 bytes 与 OS 对象不进入 Reader DTO。

```text
ReadingMode = original | translated
ReaderLayout = rtl | ltr | webtoon_vertical
Sha256 = lowercase hex string, exactly 64 characters

ReaderPageProjection = {
  page_id: PageId,
  order: integer,                         # 0-based canonical chapter reading order
  width_px: positive integer,
  height_px: positive integer,
  original: {resource_ref: ResourceRef, artifact_revision_id: OpaqueId, sha256: Sha256},
  translated: {
    resource_ref: ResourceRef | null,
    artifact_revision_id: OpaqueId | null,
    rendered_from_revision_id: OpaqueId | null,
    current_source_revision_id: OpaqueId | null,
    sha256: Sha256 | null
  }
}

ReadingProgressSnapshot = {
  book_id: BookId,
  chapter_id: ChapterId,
  mode: ReadingMode,
  last_page_id: PageId | null,
  scroll_offset_y: number,
  progress_percent: number,
  last_read_at: Timestamp | null,
  total_read_seconds: number
}

ReaderProjection = {
  book_id: BookId,
  chapter_id: ChapterId,
  mode: ReadingMode,
  layout: ReaderLayout,
  pages: ReaderPageProjection[],
  saved_progress: ReadingProgressSnapshot | null,
  initial_position: {page_id: PageId, scroll_offset_y: number}
}
```

- `GetReaderProjection.start_position="resume"` uses the saved `(book_id, chapter_id, mode)` position when present; otherwise it starts at the first logical Page. `"beginning"` returns the first Page and offset `0` without mutating `saved_progress`; a later `SaveReadingProgress` persists the displayed position. `Original` and `Translated` are separate progress keys.
- `pages` is in canonical chapter reading order. `layout=rtl` means next/previous navigation is presented right-to-left; `ltr` means left-to-right. A Webtoon chapter projects `webtoon_vertical` and its long source image as exactly one logical Page; transient cache tiles never appear as pages. The layout does not reorder the canonical array.
- `original` and `translated` references identify the corresponding immutable input/render artifact; a missing translated artifact is represented by null fields, never by a path or fabricated reference. If present, `rendered_from_revision_id` and `current_source_revision_id` expose the revisions needed to identify a stale translation; they do not prescribe a Reader fallback UI.
- For `webtoon_vertical`, `scroll_offset_y` is a non-negative source-image pixel coordinate within the one logical Page. The view maps its width-fitted display coordinate back to this source coordinate before saving and maps the same coordinate into display space on resume. Paged chapters save the selected `page_id` with `scroll_offset_y=0`.
- `SaveReadingProgress` rejects a page outside the requested chapter, an invalid mode/layout combination, a negative/non-finite offset or elapsed time, and a Webtoon offset outside the Page height. `elapsed_seconds_delta` is the non-negative time accumulated by the caller since its previous successful save; Core adds the value once per accepted command. The caller must not resend an already accepted interval; this command does not promise request replay deduplication. The result is the committed `ReadingProgressSnapshot`. Reopening the chapter with `resume` reads that persisted page/coordinate.

Export wire types:

```text
ExportFormat = png | zip | cbz | pdf | text
ExportFormatOptions =
    {compression: standard | fast | store}                 # zip
  | {}                                                     # png, cbz
  | {pdf_content: image_only | searchable_dual_layer}      # pdf
  | {text_representation: txt | json | markdown}           # text

StalePolicy = abort | continue_existing
ExportStaleDetail = {page_id: PageId, reason: stale | missing}
ExportPageLineage = {
  page_id: PageId,
  order: integer,
  source_artifact_id: OpaqueId,
  source_artifact_revision_id: OpaqueId,
  source_sha256: Sha256,
  rendered_from_revision_id: OpaqueId | null,
  current_source_revision_id: OpaqueId | null,
  source_run_id: RunId | null,
  stale: boolean
}
ExportAccepted = {
  export_id: OpaqueId,
  status: pending,
  accepted_at: Timestamp,
  book_id: BookId,
  chapter_ids: ChapterId[],
  ordered_page_ids: PageId[],
  format: ExportFormat,
  format_options: ExportFormatOptions,
  lineage: ExportPageLineage[]
}
ExportProgressSnapshot = {
  export_id: OpaqueId,
  status: pending | running | publishing | completed | cancelled | failed,
  completed_pages: non-negative integer,
  total_pages: positive integer,
  current_page_id: PageId | null,
  accepted_at: Timestamp,
  completed_at: Timestamp | null,
  output: {format: ExportFormat, output_path: string, sha256: Sha256} | null,
  lineage: ExportPageLineage[],
  error_code: string | null
}
ExportHistoryEntry = {
  export_id: OpaqueId,
  book_id: BookId,
  chapter_ids: ChapterId[],
  ordered_page_ids: PageId[],
  format: ExportFormat,
  format_options: ExportFormatOptions,
  created_at: Timestamp,
  completed_at: Timestamp | null,
  output_path: string,
  status: pending | running | publishing | completed | cancelled | failed,
  sha256: Sha256 | null,
  lineage: ExportPageLineage[]
}
```

- `StartExport` freezes the exact, non-empty `ordered_page_ids` and their lineage before work begins. IDs must be distinct and belong to the supplied book/chapters. Export consumes current translated artifacts and does not add an original-image export choice. `png` requires exactly one Page. ZIP entries, CBZ entries, PDF pages and text sections follow the frozen order. Each request creates one output file. The output SHA-256 is computed over the completed file bytes and is recorded with the exact per-page source artifact/revision hashes and any available source Run ID; clients cannot supply or rewrite lineage.
- `format_options` is a tagged-by-`format` closed shape: ZIP requires a compression choice and contains an ordered, clear structure plus a read-only manifest; CBZ writes a standard Comic Book ZIP and `ComicInfo.xml` from available Core metadata; PDF requires image-only or searchable dual-layer content, preserves page integrity and embeds fonts; text requires TXT, JSON or Markdown representation and is UTF-8. JSON contains the selected pages' coordinates and original/translated text from authoritative Core records. PNG is lossless and high-fidelity at the source image resolution/color space. Format-specific output requirements remain those in FMT-01..05; this DTO does not relax them or define new metadata values.
- If translated inputs are stale and `stale_policy="abort"`, `StartExport` returns `EXPORT_STALE` with typed details naming stale Page IDs and creates no job/history record. The target reference is consumed on a valid invocation; after explicit user choice to continue, the host issues a new one-time reference and the retry uses `continue_existing`. The accepted lineage then freezes the exact older artifact revision/hash. Missing translated input is rejected as `EXPORT_INPUT_UNAVAILABLE`; the contract does not invent an original-image fallback for export.
- Command errors use existing `INVALID_REQUEST` for malformed fields/enums, `TARGET_NOT_FOUND` for an unknown book/chapter/page, `EXPORT_STALE` (`conflict`, `retryable=false`, `details: ExportStaleDetail[]`) when stale confirmation is required, and `EXPORT_INPUT_UNAVAILABLE` when a selected translated input is absent. Unknown `export_id` uses `EXPORT_NOT_FOUND`. A write or verification failure before publication uses `EXPORT_WRITE_FAILED`; error messages/details never contain local paths. Stale/missing rejection creates no accepted job/history row.
- `GetExportSnapshot` and `GetExportHistory` return persisted Core state. An accepted job has a durable history row; history entries record D08 AC-EXPORT-002's type, exact scope and order, creation/completion time, target output path and status. Output paths are available only to the trusted Tauri host; no WebView-facing projection may contain a path or write reference.
- Core writes only within the resolved target grant and its temporary sibling, verifies the complete temporary output SHA-256, then atomically publishes the single output file. Cancellation before publication removes the temporary file and ends `cancelled`; failure also removes it. After atomic publication the job enters `publishing`; `completed` is reported only after the matching hash/path/status is durably recorded in ExportHistory. If history persistence fails, keep the job `publishing`, preserve the published output and reconcile its path/hash before reporting a terminal state. Cancellation during/after publication cannot roll the file back. Export never modifies original source files, translated inputs, their hashes, current artifact pointers or lineage; only the chosen output and ExportHistory are written. Terminal state is recorded before its event is emitted.
- `CancelExport` on a pending/running job requests cooperative cancellation and returns the latest snapshot; it does not promise immediate interruption. Once status is `publishing`, or any terminal state is reached, cancellation returns the current snapshot without changing it. Repeated cancellation is safe. `ExportProgressChanged` contains no path; `GetExportSnapshot` remains the source of truth.

`ReadingProgressChanged` and `ExportProgressChanged` payloads above are frozen but are only §3 `Event<T>` JSONL invalidation hints. A reconnect or suspected missed event always re-queries the relevant snapshot; no Reader or Export status is reconstructed from the event stream.

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

<a id="rerender-page-error-envelope-observation"></a>
**命令级实现观察（2026-10-10；非全局规范）**：本节仍为 `PROPOSAL`；以下只记录当前 handler 的命令级 envelope 映射，不冻结 `ErrorEnvelope` taxonomy。交叉引用：[§5 `RerenderPage` 行](#rerender-page-command)、[RC-4 `rerender_page` 行](M2-RC4_DOMAIN_COMMANDS.md#rc4-rerender-page-command)。`category` 与 `retryable` 是独立字段；`category="unavailable"` 不推出 `retryable=true`。

| 命令 | 源 code | 当前 category | 当前 retryable |
|---|---|---|---|
| `rerender_page` | `MISSING_REQUIRED_INPUT` | `unavailable` | `false` |
| `rerender_page` | `ARTIFACT_WRITE_FAILED` | `internal` | `false` |
| `resolve_page_resource` | `ARTIFACT_WRITE_FAILED` | `internal` | `true` |

以上值是命令级实现现状，不能推广为同一 code 的全局映射。证据：[Core rerender category mapping](../../src/bootstrap/core_service.py#L905-L923)、[rerender envelope wrapper](../../src/bootstrap/core_service.py#L1515-L1528)、[category test](../../tests/core/test_rc4_category_clarify.py#L78-L91)、[resolve publish mapping](../../src/bootstrap/core_service.py#L1660-L1664) 与 [retryable test](../../tests/core/test_page_resource_resolve.py#L249-L269)。宿主 `CORE_UNAVAILABLE` 在 Tauri `rerender_page` invocation 中作为拒绝的 code string 返回（[host command](../../apps/desktop/src-tauri/src/main.rs#L341-L348)）；此处不为它推断或添加 Core `ErrorEnvelope` 映射。

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
- Export destinations may use only the one-shot Tauri-host-issued write reference defined in §10.3. An arbitrary path string is never a write authorization.
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

### 10.3 Export destination write reference (P16-C1 rev 2.1)

本小节冻结的是 P16 的授权边界与 wire 语义，不代表签名实现或 Python Runtime 已落地。

- `ExportTargetRef` 是不透明、受限的写授权引用；它不是路径字符串，也不得编码/暴露路径。唯一 issuer 是受信 **Tauri host**。Host 在用户选择目标后签发，并将引用只注入可信 host→Python Core 的 `StartExport` 请求；React/WebView 不得接收、保存、构造、转发或使用该引用，也不得接触其映射到的路径。
- 引用 scope 是**一个精确的最终输出文件目标**和**一次 `StartExport` 调用**，并仅授权该文件所需的临时 sibling staging 与发布。签名/授权绑定当前 host session、单一 grant ID、目标 scope、允许的 `format`、是否允许替换既有目标及绝对过期时间；不允许目录递归、其他文件、任意路径访问或扩权。默认有效期为签发后 **300 秒，不滑动续期**；一次有效调用后即消费。临时文件名只能由 Core 在同一授权目标目录内生成并须清理。
- Host 通过 §5.7 受信 host→live-Core `HostControl` 通道登记受限目标 grant；引用仅含不透明 grant ID 与 host 签名。Core 在任何目标写入前必须验证当前 host session 的签名/issuer、scope、format、目标替换授权、未过期、未撤销且未消费，并以原子方式消费 grant；随后只能通过 Core 侧 grant resolver 将该 grant 解析为受限目标能力。注册还绑定当前 Core process session，但该绑定只在 Core 内存控制状态，不新增 ref 字段或签名输入。具体 token 编码/签名算法可由 Runtime Task 在不改变上述语义的前提下选择。
- Core 必须拒绝缺失/畸形引用（`REF_MALFORMED`）、非 host 签发或签名无效（`REF_SIGNATURE_INVALID`）、过期（`REF_EXPIRED`）、未知/撤销 grant（`REF_UNKNOWN_ID` / `REF_REVOKED`）、重放（`REF_ALREADY_CONSUMED`）、scope/format/host session 不匹配或未获 host 替换授权的既有目标（`REF_SCOPE_DENIED`）。拒绝错误不得暴露 grant 内容、签名材料或任何本地路径。不得以请求中的任何其他字段回退为 path-based write。
- Core 解析后只能写授权目标及其临时 staging；解析/打开阶段须验证句柄最终位置仍在该 grant scope 内，并拒绝 reparse/路径逃逸。所有原始 source、Managed Copy、现有译图 artifact 与 current/pinned Revision 均为零写对象。目标校验或发布失败时清理临时文件，绝不回写 source；已发布的输出不因后续取消而删除。
- Host 可在其可信边界内持有所选路径；`ExportProgressSnapshot` / `ExportHistoryEntry` 的 `output_path` 只回到可信 Tauri host 以满足 D08 AC-EXPORT-002 和 D04 §37。Host 不得把绝对路径或 `ExportTargetRef` 转发给 React/WebView；前端若需展示状态/触发打开文件夹，必须经独立 host command 按不透明 `export_id` 操作，不能借此取得路径。
- 与 §5 `ImportPages` 的 `ImportSourceRef`、§10.1/§10.2 显式同源：两者均由 Tauri host 授权、opaque、受限、过期、由 Core 解析并拒绝伪造/越 scope 引用；**差异只有能力方向和生命周期**：`ImportSourceRef` 是 Core 控制的只读输入，可按 §10.1 T6 滑动续期并按来源撤销；`ExportTargetRef` 是单个目标的一次性写授权，无续期、单次消费，只能写授权输出与 staging。Export ref 不复用、也不放宽 import 的读引用。

### 10.4 Import source read reference（P12-C1 rev 2.2）

本小节冻结导入来源的只读授权边界；签名算法、具体 host grant resolver 实现与 Tauri issuer 仍由后续获授权的 runtime/host Task 落地，本节不声称已实现。

- `ImportSourceRef = {grant_id: OpaqueId, host_signature: string}`。它是不透明、受限、可过期的**读授权引用**，不是路径或 URI；不得携带原始文件 bytes、Base64、绝对/相对路径或可解码出路径的字段。来源引用只在可信 Tauri host→Python Core 边界上出现；React/WebView 不得接收、保存、构造或转发引用，也不得接触其映射路径。Host 是唯一 issuer，并只可为用户显式选择的源文件或文件夹签发。
- Grant 绑定当前 host session、唯一 grant ID、`ImportPages` 读操作、精确选中的文件或文件夹 scope、签发时来源身份与绝对过期时间；不授权其它文件、目录递归、任意 OS 路径、写入/移动/删除或其它命令。文件夹只涵盖 P09 已冻结的直接子项集合；Core 不得由请求字段扩大或替换该 scope。Host 可撤销 grant；撤销对下一次解析立即生效。引用默认 TTL 为 **300 秒并在活动消费期间滑动续期**（沿 §10.1 T6）；过期后返回 `REF_EXPIRED`，不能静默续期过期引用或退回 path-based 访问。Host session 结束、显式取消选择或 grant 撤销后返回 `REF_REVOKED`。已经由 Core 打开的只读 handle 不因撤销被强制中断，沿用 §10.1 T6；该 handle 仍只允许完成当前已验证的导入读取。
- Host 经 §5.7 受信 `HostControl` 通道登记受限来源 grant；引用只含 opaque `grant_id` 与 host 签名。Core 在任何来源读取、Managed Copy/temp 写入或 SQLite 写入前验证 issuer/session/signature、grant 存在、scope、未过期、未撤销，以及来源对象身份与选择范围。注册还绑定当前 Core process session，但该绑定只在 Core 内存控制状态，不新增 ref 字段或签名输入。解析必须 open-then-verify-from-handle：从同一 handle 校验最终 containment、file identity、size 与 §10.2 要求的内容 digest，再且仅从该 handle 读取；读取后复核 identity。拒绝 symlink、junction、reparse point、相对路径、`.`/`..` 穿越、盘符/UNC 逃逸、链接替换、来源缺失及身份/尺寸/hash 漂移。路径与文件句柄只存在于受信 host/Core 内部，绝不出现在请求、结果、事件或错误 message/details。
- Core 拒绝缺失/畸形引用（`REF_MALFORMED`）、非 host 签发或签名无效（`REF_SIGNATURE_INVALID`）、过期（`REF_EXPIRED`）、未知/撤销（`REF_UNKNOWN_ID` / `REF_REVOKED`）、scope/host session 不匹配（`REF_SCOPE_DENIED`）、范围逃逸（`REF_OUT_OF_SCOPE`）、reparse point（`REF_REPARSE_POINT`）、文件不存在（`REF_NOT_FOUND`）、身份/尺寸/digest 不一致（复用 §10.2 `FILE_IDENTITY_CHANGED` / `FILE_SIZE_CHANGED` / `CONTENT_DIGEST_MISMATCH`）时，在副作用前拒绝。ErrorEnvelope 使用 §8；不得暴露 grant、签名材料、路径或堆栈，也不得从请求的其它字段回退为路径访问。
- 对有效来源仅以只读方式读取。图片 Managed Original 逐字节复制；PDF 来源只读，Managed Original 是按原始页序渲染的 PNG。来源文件始终零写、零移动、零删除。该引用授权不变更 §5.6 的类型范围、P09 的预检/重复/提交顺序，也不引入新的来源格式或大媒体阈值。

## 11. Explicitly deferred / undecided

| Decision | Status | Contract treatment |
|---|---|---|
| Page-level `blocked` UI meaning, glyph, copy and behavior | `DEFERRED / USER_DECISION_REQUIRED` | Page projection may carry typed status `blocked`; do not reuse Run `blocked` UI mapping (`⊘`, `⏸`, or any other glyph). No user-visible behavior is selected here. |
| React UI Owner | `DEFERRED / USER_DECISION_REQUIRED` | This Task does not select an owner. |
| Large-media transport and import path capability | `PARTIALLY RULED` (M2-C2) | Thresholds (T1–T7, §10.1) and security semantics (§10.2) were ruled at M2-C2 from the M2-S1 §7 ruling and the M2-S1/M2-S2 spikes. The runtime form remains `DEFERRED` to a future runtime Task: transport selection stays conditional (M2-S1 §8.1), the Tauri asset protocol is `NOT_RUN` (S1-B1), and S1-B11 product-level protection is `UNVERIFIED` (S1-B3/S1-B8 outstanding). |
| Runtime serialization library, product Tauri command names, process supervision | `UNKNOWN / NOT_IN_SCOPE`（仅 `settings_get`/`settings_update_section` 的 product Tauri command name/wire 由 §5.3 裁决；`set_region_type`/`list_regions` 的产品与 Core stdio 名称另有既有决策。上述其余 runtime 选择仍未知） | No implementation claimed beyond the sections explicitly frozen here; separate runtime Tasks must decide the rest against this transport-neutral contract. |
| Host grant registration/revoke authentication and session binding | `FROZEN`（HOST-ISSUER-1-C1 rev 2.3，§5.7） | Only the direct host-owned live-Core HostControl process channel, explicit host-session credential and Core-session binding are frozen. This does not select a serialization library, product Tauri command name, or process-supervision implementation beyond the stated lifecycle semantics. |
| Event ordering/replay/retention | `UNKNOWN / NOT_FROZEN` | rev 2.0 P13 Run events and rev 2.1 P16 Reader/Export invalidation events are emitted after their corresponding persisted state; none promises delivery, order, sequence IDs, replay or retention. Snapshot resync remains authoritative. Run-creation idempotency is frozen in §5.5. |
| Lock/revision conflict response details and concurrent edit policy | `PARTIALLY FROZEN`（`1.4` 草案：region 写命令面已冻结于 §5.4——人工优先、AI 侧 fail-closed、Revision/Lock 守卫交互、错误码映射；runtime 已由 M2-REGION-RETYPE-CORE 落地，`1.5` 时回填） | Core remains authority; §5.4 freezes the region-retype slice only; the rest of the command surface and finer conflict details stay open without weakening protection. |

The UI mapping decision does not block freezing a transport-level Page status distinct from Run status. Any proposal to alter the status value or user-visible mapping returns to the user; M2-C1 does not resolve it.

## 12. Release boundary

本节由 P13-C1 修订，**明确授权 Python IPC Runtime 实现**：已释放的 P13 Task 可按本契约实现 §5.5 Run handlers、durable idempotency/control/query、§6.1 TaskProjection 查询、§6.2 JSONL event 输出，并在其已冻结 allowlist 内接入 `src/application/tasks/**`、`src/bootstrap/core_service.py`、`src/bootstrap/core_assembly.py`、`src/infrastructure/sqlite/pipeline.py`（含确需 migration）、provider retry/runtime seams 与 `tests/core/**`。该授权只给 P13 Task 所列的 Python Core 路径与验收范围；P13-C1 本身仍是文档 Task，不授权本次实现代码。

本授权不包括 React/WebView、Tauri/Rust、QML、额外产品行为、其他 Schema/迁移路径或第三方依赖；也不代表任何 runtime 已实现或已验证。集成须遵守 P13 独立 Review、测试与 Coordinator Gate。既有非 Run 命令的 payload/result/error 语义保持原样。大媒体传输选择、M2-S1、其他 release boundary 与 integration 仍未授权。

P16-C1 rev 2.1 **另行明确授权未来已释放的 P16 Python IPC Runtime**，仅限实现本契约 §5 Reader/Export handlers、§6.3 progress snapshots/events、§10.3 `ExportTargetRef` Core-side validation/resolution 与 ExportHistory，并只在以下冻结 allowlist 内改动：`src/application/reading/**`；`src/application/export/{__init__.py,ports.py,service.py}`；为复用 host grant 解析而确有必要的 `src/application/resource_channel/**`、`src/infrastructure/resource_channel/**`（不得弱化既有 §10.1/§10.2 读语义）；`src/infrastructure/sqlite/reading_export.py`；无 Qt/PySide6 的 `src/infrastructure/export/**`；`src/bootstrap/core_service.py`、`src/bootstrap/core_assembly.py`；以及 `tests/core/**`。该 allowlist 不含 `src/application/export/pdf_qt.py`、`tests/reading_export/**`、PySide6/QML/Legacy 路径、`apps/**`、Tauri/Rust、React/WebView、Schema/migration、依赖、其他产品行为或授权外的 Python 模块。Tauri host 的 issuer 实现不在本 P16 Python Runtime 授权内，须由其自身 Task 授权。

P12-C1 rev 2.2 **另行明确授权未来已释放的导入侧 Python IPC Runtime**，只限实现 §5.6 `ImportPages` handler、将 §10.4 `ImportSourceRef` 接入既有 P09 importer，以及 `ErrorEnvelope`/最终 `ImportReport` 序列化；冻结 allowlist 为：`src/bootstrap/core_service.py`、`src/bootstrap/core_assembly.py`；仅为复用/验证受信 grant 而确需改动的 `src/application/resource_channel/**`、`src/infrastructure/resource_channel/**`（必须维持 §10.1/§10.2 安全要求并增加 `user-source` 只读 scope）；`tests/core/**`。既有 `src/application/importing/**`、`src/application/library/**`、`src/infrastructure/sqlite/**` 为本 Runtime 的只读复用面，不在写 allowlist 内；不得修改导入产品语义、SQLite Schema/migration 或其它 Python 模块。此授权不包括 `apps/**`、React/WebView、Tauri command/host issuer、Rust、QML/PySide6/Legacy、打包、第三方依赖、额外产品行为或任何 allowlist 外路径。Host issuer 必须由独立 Task 授权；本契约修订自身不授权或实现 Runtime。

HOST-ISSUER-1-C1 rev 2.3 **另行明确授权实现 §5.7 HostControl 的 Core 侧最小控制面**，冻结 allowlist 仅为：`src/bootstrap/core_service.py`（接收/校验独立 HostControl envelope、建立/关闭单一 live-Core host session、跟踪本 session 成功注册的 grant ID、将四个注册/撤销命令接至既有 `_register_*` / `_revoke_*` seam；普通 JSON-RPC 对保留命令 fail-closed；撤销 session 时调用现有 revoke seam）；以及 `tests/core/**`（覆盖 host-only/错误 credential/跨 Core session/重复和未知 grant/scope 与过期拒绝/撤销即时性/拒绝零副作用）。只有此 allowlist 足以实现时不得修改其他 Core 模块。此授权**不包括** `src/bootstrap/core_assembly.py`、`src/infrastructure/**`、`apps/**`、React/WebView、Tauri command/ACL/capabilities、Rust、Schema/migration、依赖或其他产品行为；不改变 P12-C1/P16-C1 的 handler、ref 字段、`REF_*` 消费语义；本契约本身不实现或验证 Runtime。Host issuer 的 Rust 实现仍由 HOST-ISSUER-1 独立 Task 授权。

本次把 Reader/Export **proposal 提升为新增冻结命令/事件**，协议 minor 从 rev 2.0 的 `0` 增至 `1`；未改动任何既有冻结命令、字段、状态或 P13 Run 事件，不升 major。rev 2.0 客户端不能调用新命令/事件；rev 2.1 客户端和 Core 必须配对，且没有协商或自动迁移。实现状态仍为 `NOT_IMPLEMENTED`；本 P16-C1 仅修订文档，不授权自身执行 Runtime。
