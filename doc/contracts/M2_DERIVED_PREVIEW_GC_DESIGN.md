# 轮换 preview 引用安全回收设计

Task：M2-DERIVED-GC-2-DESIGN；设计输入 `ab4b7c11`（生产树与审计 `32f9b932` 相同），release=`69d7cc08`。本稿是后继实现的设计输入，**不是现行 Schema/wire 修订，也不证明回收已实现**。

## 1. 实证与边界

| 事实 | 固定输入的代码/契约证据 | 结论 |
|---|---|---|
| 每次重渲染提交 Managed PNG，再复制随机 preview UUID | `src/application/rendering/service.py:544–590`；`src/bootstrap/core_service.py:876–938`；`src/infrastructure/resource_channel/render_preview.py:38–67` | preview 是副本；不移动、不覆盖、不删除 Managed artifact。 |
| Catalog 仅 resource_id/scope_class/rel_path | `src/infrastructure/resource_channel/catalog_store.py:34–40` | 无 page、artifact revision、退役状态；不能用当前行反推历史来源。 |
| Rust 单锁包住 rerender→revoke→map swap，map 仅进程内 | `apps/desktop/src-tauri/src/main.rs:332–349,397–437` | 前一 key 的 revoke 成功不等于持久退役或所有其他进程无引用。 |
| Core 生产与 channel 是两个 sidecar | `apps/desktop/src-tauri/src/main.rs:715–769`；`src/infrastructure/resource_channel/host_bridge.py:65–135` | Core GC 不能查看 channel 内存表；当前启动 channel 先于 production Core。 |
| Grant 在每个 ResourceChannelService 内存表，重启失效 | `src/application/resource_channel/service.py:11–15,80–82,180–208,255–284` | TTL/active_reference_count 仅本进程授权信息，不足以证明全命名空间无人使用。 |
| 当前/pinned 是主产品 artifact revision 指针和标志 | `src/infrastructure/sqlite/artifacts.py:81–118,229,258,293`；`src/ports/repositories/artifacts.py:56–66` | 可复用 get_artifact/list_revisions，不新增主产品表或 Artifact port。 |
| 旧 collector 只处理 orphan/dead row | `src/infrastructure/resource_channel/render_preview.py:106–163`；`src/bootstrap/core_service.py:1703–1724` | 有行有文件的旧 preview 仍增长；本设计不扩大原图 pages/ 回收。 |
| 每次 HTTP 读取 fresh resolve，已打开句柄不中断 | `apps/desktop/src-tauri/src/resource_protocol.rs:538–552,307–322`；M2-C1 §10.1 T6 | 不可删除仍有效 grant 的资源，也不能打断已打开流；Windows 当前只 FILE_SHARE_READ，不强制绕过分享冲突。 |

本次固定输入下 publish() 的生产调用点仅 CoreServiceServer.handle_rerender_page。手输 resource key、loader/实验 catalog、managed-read-only 与未知生产者均不是“可自动推断来源”的对象。

## 2. 选定最小方案：明确退役 + 启动静默窗口

**只在全部受管发布者和 channel 消费者都退出的受控启动窗口，回收“来源可核验、明确退役、源 revision 非 current/非 pinned”的 derived preview 副本。** 运行中不删除有行有文件的 preview；新旧 runtime 未统一接入保护时跳过 GC。当前第一刀 orphan/dead-row 行为保留，但在后继实现中也必须受同一窗口保护，不能把其现有启动扫描放在保护窗口外。

不用 TTL、文件时间、数量上限、目录名或“revoke_count=0”推导删除授权。不新建通用 GC 框架、后台调度、Reader 功能、全局 artifact 清理、引用计数系统或模型通道。

方案上限：同一长会话的文件增长仍保留；已 pinned 的历史副本也保留；只有安全重启窗口回收。故实现完成也只能说“轮换退役子集已回收”，不能声称磁盘绝对有界或 RC4-12 全部消失。若实测长会话磁盘成为问题，再单独设计在线读取租约/回收。

Rust 的 page→preview map 每次启动为空（`apps/desktop/src-tauri/src/main.rs:775`）；上一会话每页最后一个 key 没有触发轮换 retired，不能跨会话猜退役。无失败且每页只一实例的常规轨迹仍可能每页每次运行留下一个 retired=0 副本；mark/revoke失败、pinned/unknown 与多实例会更多，**不是“至多一个”容量上界**。验收分开统计退休候选已删/非退休残留/保护残留/未知跳过。

### 2.1 来源记录（拟议 catalog 辅助表，后继 Task 才能改）

保留现行 resource_catalog 三列与 CatalogEntry/lookup 形状，新增 `preview_lifecycle` 辅助表，resource_id 唯一。来源创建唯一权威是 production Core；resource channel 仅获更新既有自有行 retired 的窄写权限；loader 的既有 upsert/remove 只能使该行来源资格失效，不能创建来源或设置 retired。各自均经同一 ResourceCatalogStore 事务方法，不是允许任意 sidecar SQL：

| 字段 | 含义 |
|---|---|
| resource_id | 现有随机 preview key，与 catalog 行对应；不是 page-original key。 |
| producer_root | 生产数据根的规范化绑定；与本次 Core 数据根不一致即 UNKNOWN。路径只存 Core 本地，不发 WebView。 |
| artifact_id / artifact_revision_id | 生产 TRANSLATED artifact 与确切源 revision；Core 复用 `list_revisions(artifact_id)` 从 outcome.revision_no 找到唯一行，不拿 rev-N 字符串当全局 ID。 |
| managed_rel_path | 拟议来源表字段，逐字保存既有 revision.managed_path 与 outcome.managed_path 相同的值；不是重命名主产品字段，只用于证明，永不 unlink。 |
| retired | 默认 0；仅明确退役请求可改成 1；不从时间/TTL 自动转换。 |

数据根/源 revision 无法绑定，或无对应 artifact/revision，**不为其创建可回收来源记录**。未知历史 catalog 行不回填猜测，不根据 UUID 格式补造关系。

绑定必须在本次请求内对 `outcome.artifact_id` 的 list_revisions 找到**恰好一个同时匹配 revision_no 与 outcome.managed_path（逐字一致）**的行；同时验证 artifact 类型和 producer_root，保存该行的 artifact_revision_id。revision_no 是 per-artifact 且 purge 后可复用（`src/infrastructure/sqlite/library.py:576–580`），不能当全时唯一 ID。零匹配/多匹配/任一字段失配→不发布可回收来源，沿 PREVIEW_UNAVAILABLE 处理；不改 RenderOutcome/Artifact port。

发布顺序：Managed commit 已成功 → 原 publish 的 temp/fsync/replace → 在同一个 catalog SQLite 事务写 catalog + 来源记录（retired=0）→ 返回 preview。来源查找/写入失败应沿既有 PREVIEW_UNAVAILABLE fail-closed 语义；Managed commit 不回滚，未完整发布副本按当前失败清理路径处理。不可先返回 key 再异步补来源。

### 2.2 明确退役的触发与失败

后继 Task 拟议 channel 内部操作 `mark_preview_retired(resource_id)`（不是第二条 RPC），只把已登记自有 preview 的 retired 置 1；不删除字节、不撤销任何额外 grant、不改变 resolve/issue/touch 语义。前端没有调用该操作的 Tauri 命令/ACL；传路径、scope、producer_root 或 arbitrary SQL 一律拒绝。未知 key、原图/managed scope、来源表与 catalog 不一致均不得新增来源/退役记录；其拒绝/失败按下述 no-op/既有错误处理，不擅自加新 WebView 错误面。

Rust 复用现有 rerender 全局锁：Core committed/published → 旧 key 与新 key 不等时发送带退役位的 revoke previous → **channel 只在 revoke 成功后**标记旧 key → 返回原撤销结果 → 维持当前 map swap。相同 key、不知 previous、revoke 失败，均不标记可回收；None-preview 分支仍须完成旧 revoke 成功才可标记旧 key。mark 失败仅漏回收：记录诊断、保留旧来源 retired=0，不改已有成功 rerender/new preview 语义。不能把 mark 失败伪装成历史 revoke 失败，也不能再次撤销有效新 key。

retired=1 表示“此 key 曾被一个已知轮换显式退役”，**不表示现在无活跃消费者**；另一实例仍可持有/再 issue 同 key，整个活跃窗口不删除。新的 issue 不清除 retired：其保活由下一节的全命名空间窗口保证。不可把一般 revoke_ref/revoke_resource_refs、pin release 或 ttl 到期默认转为此回收标记。

为避免新增同步 round-trip 与锁内排队，`mark_preview_retired` 是 catalog/host_bridge 内部操作：Rust 在**既有旧 key revoke_resource 请求**附 trusted `retire_preview=true`，channel 先成功 revoke，再尝试 mark；普通 revoke（包括失败时撤销新 key）不带此位。mark 不成功仍返回原 revoke 成功结果，诊断只到 stderr；CoreChannel trait 窄追加轮换专用方法/默认 mock，不改旧 revoke_resource 语义，不加 WebView payload。SQLite mark 用独立短事务 **busy_timeout=0、零重试**，不得沿默认 5s busy 等待；仅操作一个 key，不扫描/核验文件、不等待 lease（全生命周期共享已取得）。`sqlite3.Error`、OSError 以及非预期 Exception 必须在 mark 分支捕获为 no-op+诊断，不能逃出 `_dispatch` 终止 channel。格式非法仍 REF_MALFORMED；未知来源只是 no-op。新增 DB 等待上界为 0；不承诺已有 stdio/OS I/O 的绝对墙钟上界，需 G2 实测锁争用下新增延迟和 grant 连续可用。不能为 mark 超时杀掉 channel/有效 grant。

mark 明确使用**独立 SQLite 连接**（既存 catalog URI mode=rw、timeout=0；不跑_SCHEMA、不改 journal_mode/WAL配置/schema，不创建缺失 DB；仅其正常metadata事务可产生journal/WAL写入），一次短事务，finally关闭；借用 store 的既有生命周期租约。不能修改 publisher/store 共享连接的 busy_timeout，正常 upsert 默认等待语义保持。G2 同时验证独立连接异常关闭、共享连接busy策略未变、普通WebView revoke不具退役能力。

### 2.3 命名空间静默保护：跨进程，而非 Python mutex

拟议保护为稳定的 Windows 内核文件锁，锚定**删除域 derived root** 下专用 `.preview-lifecycle.lock`（根目录内但不在 previews/pages/ 清理目录），并固定绑定 `{protocol_version=1, derived_root canonical+volume/file identity, catalog canonical+volume/file identity}`。同 derived/异 catalog 会竞争同一把锁且绑定不符→两个 sweep 都跳过；同 catalog/异 derived 由 catalog 内唯一 namespace 绑定校验不符→同样跳过，不重写绑定。首次绑定必须在受控 G7 迁移窗口，不能自动认领未知已有根。Root/lock/catalog 的替换/别名身份无法证明一致→UNKNOWN。所有支持该协议的 production Core 与 resource channel 进程，在访问 catalog/文件前取得共享租约，并持有到其最后一条业务/授权请求结束、清理完毕、进程退出；进程崩溃由 OS 释放租约。GC 只能在共享租约为零时取得独占租约，且持有到所有判定、unlink 与 metadata 更新完成。

入口覆盖的最小接线点是现有 `ResourceCatalogStore`：file-backed store 在**业务连接/初始化表/任意业务读写**前取得共享租约，close 后才释放。仅定位锁允许以下严格只读 bootstrap 例外，不是无租约业务访问。Core 的独占启动路径从已验证配置的 derived root 取独占，在装配生产 Core/业务打开 catalog **之前**；其 store 借用该保护直到降级/移交共享，不能自己再拿共享锁造成自锁。host_bridge 对最后请求/在途句柄保持同等生命周期；`:memory:` 仅隔离实验，不具备生产删除授权。

已知第三入口 `catalog_loader.py:79` 与 `bootstrap/acceptance_bridge.py:411` 也创建该 store，必须由同一构造入口覆盖，不在 CLI 各复制锁实现。loader 改写/移除 catalog 行须清掉该 key 的可回收来源资格，不能让外来重绑行继承旧 retired；其后即使路径恢复相同也保持 UNKNOWN。外部直接 SQLite/文件写入不属于受管协议，仍按 G7 禁用 sweep。实现者若证明现有 store 接线无法覆盖某入口，先补 Task 范围，不绕过保护。

无调用方保护上下文时，file-backed store 从既有 namespace 绑定取得删除域，顺序冻结如下：拒绝 catalog 路径 reparse/核验并固定文件 identity→SQLite **URI mode=ro & immutable=1** 临时 bootstrap 连接（仅读单行 namespace，不执行 `_SCHEMA`/DDL/PRAGMA写/WAL checkpoint/业务查询；禁止创建缺失 DB）→关闭连接→把绑定视为不可信定位 hint，取得相应 derived 锁→以业务连接**重新读取并验证** namespace/version/catalog+derived identity 全一致→才初始化允许表并服务。immutable bootstrap 可能忽略 WAL 中未 checkpoint 的新绑定，缺行/旧值只允许 refusal/UNKNOWN，不能猜测 root、修改绑定或无租约写入；没有第二阶段再读即不能服务。hint 变更、DB identity 替换/半绑定或任一错误拒绝业务、两个 sweep 禁用，不能回退无租约连接。只读定位不 issue/publish/删文件，所以尚未取得租约不构成资源读写窗口。

无绑定的 loader/实验 catalog 无 GC 权限且默认拒绝业务写入；测试/首次新库装配必须**显式传入已验证 derived root 与自有受控保护上下文**，由下述显式初始化完成，不能通过从 catalog 路径推导目录或伪造来源恢复旧库。Core/channel 配置已有 derived root，也可显式传入并在锁下验证 namespace；**已绑定**普通loader/acceptance_bridge默认调用无需root参数，由上述store bootstrap覆盖；首次隔离seed的新增可信flag见下段，未绑定普通调用仍拒绝。production Core/channel、loader、acceptance_bridge、probe/ac1 的 file-backed store、测试直接 store/publisher 构造均须覆盖；probe/ac1 与 :memory: 永不启动 GC。可检测信号是绑定缺失/版本不支持/identity失配/租约获取失败/受控入口覆盖清单缺项；**旧版非协作进程不存在可靠运行时检测信号**，只能 G7 用受控全退出迁移证明，否则 sweep 恒禁用（含 orphan），不拿零共享锁替代证据。

上述“不需root参数”只指**已绑定的普通业务调用**；首次隔离 fixture 初始化必须另有显式入口，冻结为现有 ResourceCatalogStore 内的窄函数 `initialize_namespace(catalog_db, derived_root)`：借用下述相同独占初始化步骤，只接受本次自有新建/空 catalog 与已验证隔离 derived 根，目录已有测试 asset 可以保留；catalog 已有资源行/来源/绑定或未知历史不自动迁移/覆盖。函数只建立 namespace、不开启任何 GC、不生成来源、不删除字节/行，不是通用GC框架。production Core首次新库也复用此步骤；旧产品库迁移仍须G7单独证明，不走fixture入口。

| 已知入口（最小覆盖清单） | 初始化/接线顺序 | 后继允许改动落点 |
|---|---|---|
| production Core | 验证配置derived root→独占→受控新库初始化或核验旧绑定→业务store借用保护→GC Gate→共享→ping | core_service.py / catalog_store.py |
| production channel / probe / ac1 channel | 既有env提供derived root；file-backed store核验已绑定 namespace并持共享。probe/ac1无Core时必须先由fixture launcher初始化/seed，永不GC | host_bridge.py；main.rs既有loader测试seed调用 |
| 只有 --db 的普通catalog_loader | 已绑定→只读hint bootstrap→共享→重读→原set/remove；未绑定默认拒绝 | catalog_store.py，不猜root |
| loader首次隔离seed（dev/packaged） | 窄追加可信CLI `--initialize-preview-namespace DERIVED_ROOT` →调用上述函数→关闭独占/转共享→普通seed；缺参数不初始化，失败不继续seed。不新增WebView能力 | catalog_loader.py；main.rs两处sidecar测试seed；下面两个packaged runner仅fixture参数 |
| AcceptanceBridge(catalog_db=...) | 其构造调用不变；测试/packaged launcher先显式初始化catalog，之后bridge按已绑定路径共享；不能桥内自动补猜测 | tests/m2_acceptance/test_acceptance_loop.py 的_LoopHarness；packaged fixture launcher |
| 直接store/publisher的隔离pytest | fixture先调用initialize_namespace，以实际自有tmp derived root绑定再构造file-backed store；:memory:不需要 | §5点名测试 |

packaged launcher具体为 `packaging/m2ac5/run_clean_start_e2e.py:279–307` seed_catalog_packaged 和 `packaging/release-gate/run_release_gate.py:826–868` roundtrip_catalog_loader；只把本次lab derived根传给上述初始化flag/调用，保持其余验收项、安装/发布行为与阈值不变。不因引入flag让默认loader任意claim生产旧根。已存在的fixture seed文件不会因绑定创建而变成可回收来源。

拟议 catalog `preview_namespace` 只有一行（singleton 主键），保存上述 protocol_version、derived canonical/identity、catalog canonical/identity，与 lock 文件内容一致。初始 catalog 不存在时，先持 derived 独占→创建空 catalog→取得实际 catalog identity→受控事务登记；竞争不同 derived 根以 singleton 唯一约束拒绝第二绑定。不一致不能改写旧绑定，也不能无租约继续访问共享 catalog：相关入口 typed unavailable/refusal，扫描一律跳过；不涉及产品 app.db Schema。初始化崩溃/半绑定/根重建均 UNKNOWN，待重新受控核验，不自动覆盖恢复。

Core 启动尝试独占租约（非阻塞）；拿不到则 **跳过 GC**，以共享租约正常服务。拿到则静默扫描，结束后转为共享租约，再进入服务循环。独占到共享不能制造“无保护的生产访问”：若 native 不支持原子降级，可先释放独占再取得共享，但这段窗口不能发业务请求/读取 grant/发布；竞争者可以安全完成另一轮扫描。共享租约获取失败不能无租约继续参与；返回既有 Core unavailable/fatal 路径，不改成绕过保护。

当前 Rust 是 channel-first，必须调整**生产路径**为 production Core 启动/握手完成 GC 后再启动 channel；probe/ac1 路径不得默默启用此 GC。第二个实例已有共享租约时，后来的 Core 跳过扫描并正常共享；不得为了 GC 禁止正常多实例，也不能等待固定 TTL 强制清理。

就绪复用 `LibraryChannel::ping` / 现行 `core.ping`（`apps/desktop/src-tauri/src/library_bridge.rs:356–357`）：Core 先取得 namespace 保护→assemble_production_core→受保护打开 catalog→_run_startup_gc→降级/取得共享→serve_forever 才应答 ping。Rust spawn library 后以此 ping 等待，成功才 spawn channel。当前 ping 的 read_line 无 deadline，后继**仅允许在 library_bridge.rs 增加启动握手 30s deadline 与本次自有 child 清理**（不改变正常 round_trip、公共 wire/命令）。失败/超时不启动 channel、不进入正常页面服务、不绕过租约；复用现有 Core unavailable 启动失败出口，关闭本次自有 Core，不终止其他实例。GC 超时留下中断态按 §3 恢复，不能为赶 deadline 降低核验。

启动专用 seam 拟名 `wait_startup_ping`：仅在尚未交给 AppState 的 StdioLibraryChannel 上协调一次现有 ping 与 30s等待（可用 std::thread/std::sync::mpsc，无新依赖），不改正常 round_trip 签名/请求序列化/读锁语义。超时先停止并回收**本次自有 child**（复用现有 wait_timeout_or_kill 思路），使阻塞 stdin/stdout 得到关闭/EOF；再回收该次读取 worker/读锁与句柄，确认不交付此失效 channel，不能遗留读线程抢下一业务响应。持 stdout 锁的 worker 不负责等待 child锁；协调器持 child锁执行退出，不等 stdout锁制造死锁。若实际 Gate 无法证明读取线程/句柄完成退出就 BLOCKED，不把挂起 worker 交给服务，也不另造通用 RPC 调度器。

Lock 路径必须是单一 namespace 权威，拒绝被替换/重解析的 lock 文件及上级异常；所有参与者验证相同 catalog/derived 根绑定。两个路径别名、混合数据根、旧版未加入租约的进程、绕过 host_bridge 的未知发行方式，均是 **UNKNOWN，live-preview 与 orphan/dead-row GC 一起禁用**。本设计不声称已经具备这个租约，不用 PID 列表、时间戳、心跳/进程名或锁文件存在作为“旧进程全退出”证据。

**上线 Gate**：实现者必须证明受支持发布/服务入口全部接入租约（含实例重连/测试构造路径），并给出受控版本切换时旧 runtime 全退出的可核验证据；不能证明则整个新 live-preview sweep 保持 fail-soft skipped，标 BLOCKED，不能凭设计批准启用删除。未知旧 runtime 的迁移保护是实施与分发验收 Gate，不由本稿自动豁免。

### 2.4 current/pinned 与路径检查

持有独占 namespace 租约后，Core 从正确 producer_root 的生产 repository 重新读 artifact/current/list_revisions；匹配 artifact_revision_id、managed_rel_path 与 artifact 类型 TRANSLATED。source 为 current 或 is_pinned=True 必须保留。失联、查询异常、多义/失配、artifact/revision 缺失、数据库只读/迁移版本不兼容，均 UNKNOWN→保留，不以“没查到”作无引用证明。

若还有不受 namespace 租约约束的产品写者能改 current/pin，必须在生产 SQLite `BEGIN IMMEDIATE` 的同一连接事务下完成判定至删除（使用既有连接归属约束；仅 SELECT，不改产品行），或者保留该候选。不得先查完所有候选释放保护，再在磁盘循环删除。SQLite busy 只导致保留/跳过，不降低保护。

候选只允许 `derived-read-only` + 来源表已登记 + retired=1 + catalog rel_path 等于 `previews/<完整 resource_id>.png`，目录/文件均拒绝 reparse/symlink/junction，原始 rel_path 经过既有 lexical gate。副本还必须通过同一打开句柄核验 size/SHA256 与该 immutable artifact revision 的既有记录一致；被人工修改/替换、无法读取或内容失配均 UNKNOWN→保留，不能仅凭旧来源行删掉修改后的副本。复用 revision 既有 hash/size，不增第二套内容真值。

最终删除必须针对上述核验的同一文件身份；不能用 resolve()+路径 unlink() 的检查后使用窗口作为最终安全证明。复用现有 Win32 句柄事实/identity/最终路径核验思路，以对核验句柄的 native delete disposition 完成删除；无法证明身份/分享模式安全则保留。

GC 打开候选使用读 + DELETE 权限、仅 FILE_SHARE_READ（不允许写/删分享），拒绝 reparse；从内容核验到 disposition 持有此句柄。上级目录身份也须核验并持有阻止替换/重命名的目录句柄；做不到就跳过。这样现有写者/读者的分享冲突导致保留，核验后新写者也不能改内容；不能只比较两次 stat/hash 然后开放写入窗口。

不修改现有读取的 FILE_SHARE_READ，不强制关闭其他进程句柄、不加 FILE_SHARE_DELETE 来迎合 GC。即使退休 grant 已失效，存在遗留已打开流时删除失败保留；重试只在下一安全窗口，不能终止流。managed/source/人工文件和其他 scope 永不进入候选，更不调用其删除器。

## 3. 删除/恢复顺序

在独占租约及必要产品事务保护下，对每个候选重读 catalog/来源、核验 current/pin、核验路径/句柄身份；**先删除 derived 副本，后在 catalog 单事务删除 catalog 行与来源记录**。不跨数据库伪造原子提交。

| 中断点 | 下一启动的行为 |
|---|---|
| Managed 已提交、publish 之前/失败 | 保留所有 Managed revision；按既有 PREVIEW_UNAVAILABLE 路线重试。 |
| 副本已 replace、catalog/来源尚未提交 | 新文件暂为 orphan；只在安全窗口内由现有第一刀处理；不能在活跃发布中扫描它。 |
| catalog/来源完整、返回/retire 之前 | retired=0，保留，允许漏回收。 |
| revoke 成功、mark 未完成/丢失 | retired=0，保留；失败不得影响新 preview。 |
| mark 已提交、其他实例仍 active | retired=1 只是候选；共享租约阻止扫描，grant/在途读继续。 |
| 副本已删除、catalog 删除事务失败/进程崩溃 | 当前无活跃通道；下一安全窗口第一刀 dead-row 清理。来源表的无 catalog 行记录可清掉（仅 metadata），不可据此删其他文件。 |
| catalog+来源已删除 | 重复扫描无操作；不会重绑旧 opaque ID，也不删除 Managed 源。 |
| 任一读取/锁/DB/删除错误 | fail-soft 保留，统计 skipped + 原因；不将 UNKNOWN 变成功、不阻断一般 Core 业务（共享租约缺失不能继续无保护业务）。 |

## 4. 可删 / 必留 / 未知矩阵

| ID | 对象/情形 | 判定 | 可执行条件或理由 |
|---|---|---|---|
| D1 | 已知自有 retired preview，源 revision 非 current/非 pinned，无活跃受管进程 | 可删 | 全部独占租约、正确 producer_root、源关系/DB保护、目录/句柄身份 Gate 成立。 |
| D2 | 同一 D1，unlink 已成功但 catalog/来源记录残留 | 可清 metadata | 下一安全窗口恢复；零 managed 删除。 |
| K1 | retired=0 或正在/刚刚发布的新 preview | 必留 | 不能仅按“目前没有 grant”删除。 |
| K2 | 源 revision 是 current 或 pinned | 必留 | 明确保护，即使只有 derived 副本、retired=1。 |
| K3 | 任一有效 grant 所属 channel/发布者仍 active | 必留 | 共享租约阻止整个 sweep；TTL 不改变判定。 |
| K4 | 已打开读取句柄尚未结束 | 必留/分享冲突跳过 | 不强制中断、不强制删除。 |
| K5 | managed-read-only、Managed/source/人工文件、Lock 及其主产品行、pages 原图、模型 | live-preview sweep 必留 | 不属于本 Task live-preview 删除集合，产品 DB 仅 SELECT。既有第一刀 orphan/dead-row 另按原授权、同安全窗口运行，不扩大 pages 回收。 |
| K6 | 同 key 轮换或 previous revoke 失败 | 必留 | 不设置 retired；保留当前 RC-4 语义。 |
| U1 | 历史有行有文件、无来源记录 | UNKNOWN→保留 | 不从文件名/mtime/rev-N 猜关联；不补填猜测。 |
| U2 | producer_root/源 revision 缺失、失配、DB查失败 | UNKNOWN→保留 | “未找到”不等于无引用。 |
| U3 | 多进程/mixed version/入口未加入租约、命名空间别名不确定 | UNKNOWN→禁用 sweep | 协议不覆盖所有读者就没有静默证明。 |
| U4 | symlink/junction/reparse、逃逸、身份被换、副本 hash/size 失配或分享冲突 | UNKNOWN→保留 | 保护人工修改；不降级为 pathname unlink。 |
| U5 | 错误/目录填充/未知 catalog loader 行 | UNKNOWN→保留 | 本设计不扩张第一刀/loader授权。 |

逐项证据口径（代码行均属于 §1 固定输入；拟议保护不是现存实现）：

| ID | 现有证据与尚未知项 |
|---|---|
| D1 | publisher `render_preview.py:38–67` 证明副本；`artifacts.py:81–118,293` 有 current/pin；来源/retired/租约/句柄删除均尚未实现，运行删除安全 **UNKNOWN/NOT_RUN**。 |
| D2 | `render_preview.py:147–163` 已有 dead-row 清理；来源表恢复与安全窗口 **NOT_RUN**。 |
| K1 | `render_preview.py:54–67` 文件先 replace 后登记；发布中不能据孤儿暂态删。后继互斥 **NOT_RUN**。 |
| K2 | `artifacts.py:101–118,293` 与 ArtifactRevisionRecord 提供 current/pin；拟议 GC 重读保护 **NOT_RUN**。 |
| K3 | `resource_channel/service.py:180–208,255–284` grant 是局部内存表；跨进程无 grant 证明 **UNKNOWN**，共享租约 **NOT_RUN**。 |
| K4 | `resource_protocol.rs:307–322,538–552` 已有核验/打开句柄及 fresh resolve；collector 对在途流保护实测 **NOT_RUN**。 |
| K5 | `render_preview.py:69–104` 原图 pages 与 preview 发布分开；`rendering/service.py:544–590` Managed 提交。其文件/产品行不在本删除授权。 |
| K6 | `main.rs:397–437` same-key/旧 revoke 失败分支；拟议 mark 对照 **NOT_RUN**。 |
| U1 | `catalog_store.py:34–40` 只有三列，无法证明历史 origin，**UNKNOWN**。 |
| U2 | `artifacts.py:81–118` 仅提供可查接口；特定副本 producer/source 对应关系 **UNKNOWN**，不把查不到变可删。 |
| U3 | `main.rs:715–769` 两独立 sidecar；现存代码无 namespace lifetime lease。旧 runtime/入口全覆盖 **UNKNOWN/NOT_RUN**。 |
| U4 | `resource_protocol.rs:307–322` 提供读取侧句柄核验思路；`artifacts.py:285–293` 有源 hash/size。Python GC 同句柄核验/删除、人工修改对照 **NOT_RUN**。 |
| U5 | `catalog_store.py` 允许 loader 行，`render_preview.py:106–163` 仅现有受限扫描；非受管来源关系 **UNKNOWN**。 |

## 5. 与现有实现差量与后继范围

拟议 M2-DERIVED-GC-2 Owner=ZCode、Reviewer=DeepSeek Harness、Integrator=Codex；设计集成前不 ready。实际 branch/worktree/base 在 Task/交接中由 Codex 填入，不能把未来路径当成已创建。

| 文件/路径（拟议 allowed_paths） | 最小变化 |
|---|---|
| src/infrastructure/resource_channel/catalog_store.py | 辅助来源表、事务型登记/退役、metadata 恢复；调用同包 native helper，无通用框架。 |
| src/infrastructure/resource_channel/catalog_loader.py | 仅隔离fixture显式initialize-preview-namespace参数接线，默认已绑定seed语义保持；未绑定不自动猜root/迁移。 |
| src/infrastructure/resource_channel/handle_resolver.py | 复用既有 `_identity_of/_size_of/_final_path_of/_digest_through` 等 ctypes 句柄事实，窄追加 namespace 文件租约及核验句柄 delete disposition；现有 reader 行为/share flags 不变。该模块已在 F-05 白名单，不复制第二套 Win32 identity/read 校验。 |
| src/infrastructure/resource_channel/render_preview.py | 已有 publish 扩显式来源、受保护窗口内 sweep；原 publish_original 行为不改。 |
| src/bootstrap/core_service.py | 发布时复用 artifact repo 确切源关联、Core 启动/退出共享租约、独占 GC/current-pinned 查询装配。 |
| src/infrastructure/resource_channel/host_bridge.py | 全生命周期共享租约；只追加内部 mark_preview_retired，不导入产品 domain/SQLite adapters。 |
| apps/desktop/src-tauri/src/core_bridge.rs | trusted mark 调用与 mock 定向支持；不改 public Tauri 命令表。 |
| apps/desktop/src-tauri/src/library_bridge.rs | 仅现有 core.ping 启动就绪 deadline/自有 child 清理；正常业务 round_trip/wire 不变。 |
| apps/desktop/src-tauri/src/main.rs | 生产启动顺序与成功 revoke 后 mark；保持 rerender 锁/失败/same-key/None语义。 |
| tests/core/test_derived_gc.py、tests/core/test_rc4_stdio_render_preview.py、tests/core/test_page_resource_resolve.py、tests/m2_resource_channel/test_catalog_authority.py、tests/m2_resource_channel/test_bridge_and_thresholds.py、tests/m2_resource_channel/test_handle_resolver.py、tests/m2_resource_channel/test_sidecar_isolation.py、tests/m2_acceptance/test_acceptance_loop.py | 改动所需判别断言及既有file-backed store隔离fixture显式初始化；原名单之外增测试文件需在实现 Task 点名；沿用已有 pytest。 |
| packaging/m2ac5/run_clean_start_e2e.py、packaging/release-gate/run_release_gate.py | 唯一packaging范围例外：隔离fixture seed初始化flag/root参数。禁止修改spec/build/install/deploy流程、通过阈值或跳过现有检查；本轮只设计、不执行这些runner。 |
| verification/M2-RC2/run_e2e.py、verification/M2-AC1/run_e2e.py | 只改当前可执行driver的新隔离fixture初始化接线；历史报告/原始运行日志/结果文件一律不改，后继新运行日志落自己的verification目录。 |
| doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md、doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md 的窄注记、正式 Task/Handoff/verification | 设计批准后由 Codex 追认内部生命周期字段与行为；不改现有 WebView wire。 |

明确允许的后继共享变更：**仅专用 catalog 来源/namespace 辅助元数据、channel 更新既有 retired 的窄写权限、trusted revoke 请求的内部 retire_preview 位/轮换方法及可信隔离loader初始化flag**；source_artifact_revision_id 不发 WebView、不新增 Tauri IPC/ACL、不变 CatalogEntry/issue 请求、不变 T6 撤销/TTL。现行产品 schema.py、migration、ArtifactRepositoryPort、ResourceChannelService 的公共语义、读取 share flags、React、依赖、packaging/spec/build/部署流程、Legacy、用户文件禁止修改；仅上述两个现成runner的fixture参数属于packaging例外。

如实现无法保持上述边界，或需要解决混合旧 runtime 的产品启动/升级取舍，先记 BLOCKED，交 Codex 明确扩展 Task/必要用户裁决；不扩大当前设计授权。

## 6. 后继验收 Gate（全部 planned / NOT_RUN）

| Gate | 必须留下的判别证据 |
|---|---|
| G1 来源/权限 | 老资源不补猜测、跨 producer_root/不匹配 artifact/source 不删；page-original/managed/source/人工/Lock相关主产品行不写；任意路径/scope注入拒绝。 |
| G2 生命周期 | 两次/三次真实 rerender→不同 key→旧 revoke成功→mark旧；same-key/revoke失败/mark失败/None-preview 各分支；注入 sqlite/OS/非预期异常及锁争用，mark零DB等待/零重试，仍返回同一成功响应且channel/grant连续有效；证明 current/pinned/source sha256 与 product DB行无改动。 |
| G3 静默窗口 | 至少两个独立真实 OS进程持共享租约，独占 GC被阻断；退出后独占成功；kill所属实验进程释放；第二实例正常服务且跳过 GC；同derived异catalog/同catalog异derived/别名替换两个sweep不删；Core/channel/loader/acceptance_bridge/probe/ac1/测试store入口覆盖，既有orphan扫描纳入；启动ping成功、失败、30s超时各分支。 |
| G4 保护/回收 | 知道 retired非current非pinned 时删；active grant（含无subscriber）、current、pin、unknown 时不删。改变单一条件的对照必须能红。 |
| G5 安全/恢复 | 目录+文件 junction/symlink/身份替换、人工修改副本 hash/size 失配、在途句柄、sharing violation、DB busy；publish/mark/unlink/catalog事务各 crash点恢复、重复运行幂等、失败日志/skip原因。 |
| G6 回归/隔离 | 定向 pytest + cargo（真实 sidecar）+ F-05 import名单不扩大到产品adapter + dev/packaged入口装配检查；生产行为变化若触及构建必须使用相应 fixed-head build证据。 |
| G7 启用边界 | 受控旧 runtime退出/新入口全部租约协议证明；unknown/mixed-version 实证下不删，不能把风险仅写进文档然后默认启用。 |

G3 补充 bootstrap 判别：只有 --db 的 loader/acceptance_bridge 能在已绑定 catalog 定位并取得同一共享锁；readonly hint不能创建DB/表/业务行，缺行或未checkpoint绑定拒绝，hint后绑定变更必须拒绝；缺少再验证的反例应红。无绑定测试库由显式自有derived保护初始化；不以测试兼容为由给生产未绑定库开无租约写通道。G2 补充：WebView 可达 `revoke_resource_refs` 仍调用普通 revoke，不携 retire_preview；失败撤销新key同样不携该位。

G3/G6必须覆盖首次新库链：loader显式初始化+seed→probe/ac1 shared服务、_LoopHarness预初始化→catalog_pages、main.rs真实sidecar seed、两个packaged runner fixture传参；无flag旧未知库不claim/不删，有绑定冲突flag不覆盖。初始化只metadata不代表G7批准启用。G6定向pytest同时跑tests/m2_acceptance全目录；打包入口因引用的生产模块行为变化，固定head构建及对应runner不得用历史PASS替代，缺干净环境明确BLOCKED，不修改其成功门槛。

建议命令（路径须采用实现 worktree和实测环境，非本稿执行结果）：

```powershell
& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -m pytest -q tests/core/test_derived_gc.py tests/core/test_rc4_stdio_render_preview.py tests/core/test_page_resource_resolve.py tests/m2_resource_channel tests/m2_acceptance
cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml
git diff --check
```

实际入口/lease安全 Gate 必须真实双进程运行；Mock 锁不证明 OS共享/独占，实测 product DB保护不可用则 BLOCKED。固定 head 非作者 Review→条件闭合→Codex merge→集成后受影响回归后才能 done。设计本身只做引用/矩阵/范围核验，不在真实用户库运行 collector。

## 7. 入口清单与精度补充（R3-01/A1-A4，属于冻结范围）

dev launcher点名 verification/M2-RC2/run_e2e.py:114 的seed_catalog（只给新lab catalog seed追加初始化flag与其已有derived根）和 verification/M2-AC1/run_e2e.py:177 的launch_env（生成新fixture路径后、spawn任何sidecar前，通过可信loader显式初始化catalog）。production迁移登记由core_service.main在G7受控全退出/绑定身份核验后执行，旧catalog资源行保持UNKNOWN、不回填来源；fixture入口不替代迁移。acceptance_bridge.main/method_catalog_pages自身不改，通过launcher/_LoopHarness预初始化后的已绑定catalog调用；ac1_bridge.rs继承env形状不改。§2.3的清单加这两个dev driver和两个packaged driver，即文件级最小覆盖，不靠实施时追加未知范围。

所有SQLite URI复用stdlib绝对Path.as_uri的正斜杠/percent转义，再追加已冻结query参数；不把含空格/?/#的原始Windows路径直接插入URI。bootstrap只读保证须在G3实际记录；不能用immutable忽略WAL所得缺行触发初始化旧库。mark“不改WAL”只指journal_mode/WAL配置，不禁止一次正常metadata事务的journal文件。

启动超时明确显式kill+wait，退出child锁区后join读取worker，再以child已回收的终止态丢弃channel；终止态Drop不得再次发shutdown/等待第二个5s，也不能在持child锁期间触发Drop。普通成功channel既有Drop顺序不变；G3以挂起ping child/线程退出与无读锁泄漏作判别。

G2复用现有命令表数字断言：command_allowlist(false,false)仍恰好15条，无退役wrapper。test_bridge_and_thresholds.py的store实际是:memory:，只用于mark行为/mock，不做file-backed初始化；直接file-backed fixture为test_catalog_authority/test_derived_gc/test_page_resource_resolve/test_rc4_stdio_render_preview，间接file-backed为test_acceptance_loop::_LoopHarness。G3必须有首次装配红绿证据：绑定前loader/acceptance拒绝→自有新库显式initialize→绑定后可用；已有行/旧未知库/冲突fixture初始化拒绝，不因测试红放开旧库。
