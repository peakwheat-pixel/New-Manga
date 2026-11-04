# C-17 Source 同步契约提案

状态：**DRAFT v0.1 / 未冻结**。日期：2026-11-04。Owner：Codex（本次新实现上下文）。
授权：[FEA-11-PREREQ-1](../tasks/FEA-11-PREREQ-1.md)、[Appointment](../reviews/FEA-11-PREREQ-1-appointment.md)。最终 ID、版本分配及冻结由 DSH 决定。

## 0. 权威、版本与边界

本契约承载 C-14 SC-S01…S07/S11 的可执行增量；依赖 C-15 v1.1 §1/§3.2/§4.2/§5–6、C-16 v1.1 §0/§4、C-05 v1.2、C-13 SC-D07/08、M2-C1 rev 2.12 §3.2/§4/§5。引用文档位于本目录（M2-C1 位于 `doc/contracts/`）。既有冻结语义优先；冲突必须交 DSH，不以本提案覆盖。

| 版本面 | 本提案决定 | 生效条件 |
|---|---|---|
| 文档 | C-17 v0.1；候选冻结版本 v1.0 | 最终字节独立 Review + DSH 冻结 |
| Schema | `v8__source_sync`，版本号 **8 候选，不预占** | DSH 确认当前迁移链未被其他 Task 占用；若改号，只改新增登记与证据并复核 |
| 新命令 per-command wire | `new-manga.core` major=2、minor=3，additive | C-16 默认面 minor=3 先例；强制 capability 门禁，不能仅凭 minor 判断支持 |
| 全局默认 | Core `PROTOCOL_MINOR=3`、客户端 DefaultMinor=3 均无增量 | 不改旧命令（含 PrepareRun/AcceptRun 的专属 minor=12） |
| M2-C1 | **命令面由 C-17 承载，M2-C1 无增量** | 不改 envelope/旧命令/全局 taxonomy；新命令与局部错误闭集在此登记 |

没有生产代码、生产迁移或产品测试实现授权。UI、删除/GC/回收、备份/跨机迁移、依赖变更均不在本卡。FEA-11 实施仍须 PREREQ done → scope-r2 approved → DSH ready/Appointment。四路检测（启动/访问前、操作前、定时扫描、watcher）是 FEA-11 的实现责任；本契约定义 scan 接口，不替其延期或判定完成。

## 1. 身份、计划与摘要

一个 plan 面向**一个原 SourceId**，可覆盖一个或多个 book（project=book），repoint 可有另一个目标 SourceId。跨多个源的工作必须分别预览为多个 plan，不宣称跨 plan 原子。共享的“全部引用”必须冻结当时全部引用集合（含软删仍占位的 binding），不能解释为执行时再查询并自动扩展。

`PlanBody` 是 §5 的 closed DTO；以 `canonical-json/1`：UTF-8、对象键按 Unicode code point 升序、无空白、原字符串不归一化、只准整数/布尔/null/字符串/数组/对象、禁浮点/NaN、禁重复 JSON key。实现需跨语言 golden bytes 验证。字符串以 JSON 标准最小转义（非 ASCII 保留 UTF-8，控制字符用小写 `\u00xx`）；摘要是小写 sha256。wire 仍按现有 stdio 非 ASCII 转义，不把 wire 原行当 canonical bytes。

`plan_digest=sha256(canonical(PlanBody))`，包含 plan_id、kind、范围、三类代次、全部引用集合摘要、旧/新内容证据、diff/mapping、人工/保护/draft 基线和用户决定/顺序；不包含可更新状态/时间/临时 grant/secret。body 创建后不可修改；任何决定修改均新建 plan_id。`request_digest=sha256(canonical({operation_id,plan_id,plan_digest,kind}))`，三条专用 apply 与通用 apply 按相同语义 kind 计算，不含 request_id/会话/grant/重试动作。相同 operation_id+同摘要只能有一个业务结果；同 ID 不同摘要 → SOURCE_OPERATION_CONFLICT。一个成功提交的 plan 只能对应一个 operation。

## 2. 规范 SQL（完整增量）

以下单一 SQL 块为拟议新增 migration 的完整 SQL；不改 v1–v7 SQL/name/checksum。SQLite foreign_keys 必须在事务外打开。无 ON DELETE CASCADE：本卡不决定删除历史；清理须另行契约。JSON TEXT 的 closed shape/canonical/交叉行守卫由应用层验证，DDL 不声称完成它们。

```sql
CREATE TABLE source_sync_plans (
    plan_id TEXT NOT NULL PRIMARY KEY CHECK (length(plan_id) BETWEEN 1 AND 128),
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    kind TEXT NOT NULL CHECK (kind IN ('relink','repoint','resync')),
    state TEXT NOT NULL CHECK (state IN ('draft','previewed','confirmed','applied','stale')),
    plan_digest TEXT NOT NULL CHECK (length(plan_digest)=64 AND plan_digest NOT GLOB '*[^0-9a-f]*'),
    body_json TEXT NOT NULL CHECK (length(body_json)>1),
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    previewed_at TEXT,
    confirmed_at TEXT,
    applied_at TEXT,
    stale_reason TEXT CHECK (stale_reason IS NULL OR stale_reason IN
        ('expired','source','binding','authorization','scope','manual','decision','cancelled')),
    CHECK (state NOT IN ('previewed','confirmed','applied') OR previewed_at IS NOT NULL),
    CHECK (state NOT IN ('confirmed','applied') OR confirmed_at IS NOT NULL),
    CHECK ((state='applied')=(applied_at IS NOT NULL)),
    CHECK ((state='stale')=(stale_reason IS NOT NULL)),
    UNIQUE (plan_id,plan_digest,kind)
);
CREATE INDEX idx_source_sync_plans_source_state ON source_sync_plans(source_id,state);
CREATE INDEX idx_source_sync_plans_expiry ON source_sync_plans(state,expires_at);

CREATE TABLE source_operations (
    operation_id TEXT NOT NULL PRIMARY KEY CHECK (length(operation_id) BETWEEN 1 AND 128),
    plan_id TEXT NOT NULL UNIQUE,
    plan_digest TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('relink','repoint','resync')),
    request_digest TEXT NOT NULL CHECK (length(request_digest)=64 AND request_digest NOT GLOB '*[^0-9a-f]*'),
    state TEXT NOT NULL CHECK (state IN
        ('started','host-authorized','core-committed','acknowledged','failed','recovered')),
    authorization_digest TEXT NOT NULL CHECK (length(authorization_digest)=64 AND authorization_digest NOT GLOB '*[^0-9a-f]*'),
    authorization_json TEXT NOT NULL CHECK (length(authorization_json)>1),
    host_receipt_id TEXT NOT NULL CHECK (length(host_receipt_id) BETWEEN 1 AND 128),
    commit_receipt_json TEXT,
    commit_digest TEXT CHECK (commit_digest IS NULL OR
        (length(commit_digest)=64 AND commit_digest NOT GLOB '*[^0-9a-f]*')),
    error_code TEXT,
    retryable INTEGER NOT NULL DEFAULT 0 CHECK (retryable IN (0,1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    committed_at TEXT,
    acknowledged_at TEXT,
    CHECK ((commit_digest IS NULL)=(commit_receipt_json IS NULL)),
    CHECK ((committed_at IS NULL)=(commit_digest IS NULL)),
    CHECK (state NOT IN ('core-committed','acknowledged','recovered') OR committed_at IS NOT NULL),
    CHECK ((state IN ('acknowledged','recovered'))=(acknowledged_at IS NOT NULL)),
    CHECK ((state='failed')=(error_code IS NOT NULL)),
    FOREIGN KEY (plan_id,plan_digest,kind)
        REFERENCES source_sync_plans(plan_id,plan_digest,kind)
);
CREATE INDEX idx_source_operations_state ON source_operations(state,updated_at);

CREATE TABLE source_binding_publications (
    binding_id TEXT NOT NULL PRIMARY KEY REFERENCES page_bindings(binding_id),
    operation_id TEXT NOT NULL REFERENCES source_operations(operation_id),
    previous_binding_id TEXT REFERENCES page_bindings(binding_id),
    relation TEXT NOT NULL CHECK (relation IN ('same_content','changed','repoint','added','missing')),
    read_gate TEXT NOT NULL CHECK (read_gate IN ('pending','open')),
    opened_at TEXT,
    CHECK ((read_gate='open')=(opened_at IS NOT NULL)),
    CHECK ((relation='added')=(previous_binding_id IS NULL)),
    CHECK (binding_id<>previous_binding_id)
);
CREATE INDEX idx_source_binding_publications_operation ON source_binding_publications(operation_id,read_gate);
CREATE INDEX idx_source_binding_publications_previous ON source_binding_publications(previous_binding_id);

CREATE TABLE source_revision_lineage (
    revision_id TEXT NOT NULL PRIMARY KEY REFERENCES region_revisions(region_revision_id),
    region_id TEXT NOT NULL REFERENCES regions(region_id),
    binding_id TEXT REFERENCES page_bindings(binding_id),
    provenance TEXT NOT NULL CHECK (provenance IN ('captured_v7','native','migrated','legacy_unverified')),
    from_revision_id TEXT REFERENCES region_revisions(region_revision_id),
    operation_id TEXT REFERENCES source_operations(operation_id),
    created_at TEXT NOT NULL,
    CHECK ((provenance='legacy_unverified')=(binding_id IS NULL)),
    CHECK ((provenance='migrated')=(from_revision_id IS NOT NULL)),
    CHECK (revision_id<>from_revision_id)
);
CREATE INDEX idx_source_revision_lineage_binding ON source_revision_lineage(binding_id,region_id);
CREATE INDEX idx_source_revision_lineage_origin ON source_revision_lineage(from_revision_id);
```

### 2.1 迁移、回滚与旧端拒写

追加一个 `Migration(candidate_version,"v8__source_sync",SQL)`（最终号变更时同步 name），沿现有 `MigrationRunner`：逐 migration `BEGIN IMMEDIATE`→全部语句→（实际 runner 仅对 v5 执行 `PRAGMA foreign_key_check`、对 v7 执行 validate 回调；v8 为纯新增空表，不触发两者）→`schema_migrations` 及 `application_metadata.schema_version`→COMMIT；任一步异常 rollback 并中止启动。不能用会隐式提交的 executescript 包裹迁移，不额外嵌套业务 repository 自带提交。仅用新增表/索引，初始空，无 v7 回填/旧数据修改。lineage 在首次受影响同步的统一事务捕获，见 §7。

v7→候选 v8 失败后：sqlite_master（表/索引/SQL）、旧数据、schema_migrations 和 application_metadata 与迁移前完全一致；不是只检查版本数字。从更早版本启动时，先前已成功 migration 保留，不声称整条升级链回滚。失败 typed SOURCE_MIGRATION_FAILED，不能进入可写服务。沿用已有迁移前备份政策；本卡不做备份/降级实现。

旧端必须在任何业务连接写入前比较 `MAX(schema_migrations.schema_version)` 与其 latest_known_version=7；>7 抛 `SchemaTooNewError`，不执行 DDL/DML。application_metadata 不一致也中止启动，不靠忽略新表继续。隔离验证调用真实 v7 runner 验证前一判据；后一个启动一致性要求归 FEA-11，不声称当前旧二进制已有该附加判据。无自动 down migration。当前迁移链/旧端拒写是代码事实，未来 v8 接线仍需 FEA-11 验证。

### 2.2 应用层强约束（同一写事务）

- PlanBody 校验、重算 plan_digest；FK JSON 引用也逐项重读，目标扫描尚未提交的新 source/version/entry 在 body 中仅是候选，apply 才插入；规范 ID/locator 不含路径。
- publication 的新/旧 binding 同 PageId、同 project，previous 等于新 binding.previous_binding_id；added 页属于已冻结 chapter；relation 与 mapping 一致。门控 open 仅允许 operation.state=acknowledged/recovered，所有该 operation 的 publication 同事务开门。
- lineage 的 revision 属于 region，region.page_id 等于 binding.page_id；migrated 新旧 revision 处于明确映射的旧/新 binding，来源不得自指/成环。已存在 lineage 不能原地改归属。legacy_unverified 只读，不作为新图坐标证据。
- SQL CHECK 管存储形状，应用层状态守卫管合法转移；禁止客户端直接写 state。两者分别验证，不把跨表约束误报为 DDL 已覆盖。

## 3. 状态与持久归属

### 3.1 plan 转移表

所有 plan 状态由 Core 写；body/digest 不变。所有未列前态/事件组合拒绝 SOURCE_SYNC_STATE_CONFLICT。用户可在预览前修改输入，修改后必须用新 plan_id。

| 前态 | 事件 | 守卫 | 写入方 | 持久确认点 | 后态 |
|---|---|---|---|---|---|
| 无 | PlanSourceSync | scan 活、范围/基线有效、同 ID 未绑定其他 body | Core | 创建 plan 的事务 COMMIT | draft |
| draft | PreviewSourceSyncPlan | digest 一致、全部明细计数/映射可展示 | Core | previewed_at 事务 COMMIT，才返回完整预览 | previewed |
| previewed | ConfirmSourceSyncPlan | 同摘要、未过期、所有歧义有显式决定、确认 kind/范围 | Core | confirmed_at 事务 COMMIT | confirmed |
| confirmed | apply | plan 未过期（expires_at）、§6 全部 CAS、Host durable 授权在先 | Core | **整 plan 业务事务**（含 receipt/gates）COMMIT | applied |
| draft/previewed/confirmed | InvalidateSourceSyncPlan | 明确取消或主动失效；无已提交 operation | Core | stale_reason 事务 COMMIT | stale |
| 任意已有态 | 同命令重放 | body/digest/事件相同 | Core | 返回已有结果；无新增业务写 | 原态 |

stale Apply **自身不写 stale 标记/审计/receipt**，连 plan/operation 元数据也不写；返回 SOURCE_PLAN_STALE 及 cause。若需持久标 stale，调用方另发显式 Invalidate，形成独立、可审计的写入基线。applied/stale 终态不能重开；响应丢失可重查/重放，applied 的 apply 必须先按 operation 身份重放，不能当作再次提交。

### 3.2 operation 转移表与存储归属

Host 私有 journal `<DataRoot>/host/source-operations/<operation_id>.v1.dat`：C-15 §5 同等 DPAPI/ACL、锁后重读、同目录原子替换+Flush(true)。存储 closed `HostJournal`（§5），只保存操作/授权元数据，不是第二个 Book/Page DB；没有密码、grant、源内容/绝对路径。文件名 ID 用安全白名单 `[A-Za-z0-9_-]{1,128}`；业务 opaque ID 不因文件名编码获得语义。

Core `source_operations` 为业务 receipt 权威。Core 对 started/host-authorized 的写入在完成全部 CAS 后同一业务事务内推进至 core-committed；这两个 Core 中间状态不对其他连接可见。Host journal 记录其提交前的 durable 阶段，查询结果注明 origin，不伪造 Core 行。journal 的 Operation.commit/commit_digest/acknowledged_at 在提交前均为null；Core已提交后必须保存完整CommitReceipt，commit_digest不可变。

| 前态 | 事件 | 守卫 | 写入方/持久归属 | 持久确认点 | 后态 |
|---|---|---|---|---|---|
| 无 | dispatch 准备 | confirmed plan、kind/摘要一致 | Host journal | started 原子落盘 | started |
| started | authorize | 锁后重读 Registry；根/物理 identity/expected generation 合法 | **先 Registry durable，再 Host journal** | Registry flush/replace 成功，authorization receipt 关联 operation 摘要 | host-authorized |
| host-authorized | Apply/Relink/Repoint/Resync | live grant/稳定 lease、§6 全 CAS | Core（事务中 started→host-authorized→core-committed） | source rows/pages/bindings/lineage + plan applied + receipt + pending gates **一次 COMMIT** | core-committed |
| started/host-authorized | 取消/提交前错误 | 尚无 Core commit；Core 应用事务全部回滚 | Host journal；**Core 零写** | error_code/retryable durable | failed |
| core-committed | Host 确认 receipt | Host 核对 Core commit_digest、目标授权集合、当前 Registry/identity；落盘 commit_digest | Host journal | acknowledged receipt flush/replace 后才能发 ACK | core-committed（Core 尚未 ACK） |
| core-committed | AcknowledgeSourceOperation | host-control 身份 + Host durable receipt + fresh grant/授权重验（见下） | Core | 全部 gates open + acknowledged_at 同事务 | acknowledged |
| core-committed | 确认不可完成 | 授权已撤销/丢失等；不回滚已提交业务行 | Host；显式 RecordSourceOperationFailure 才写 Core | Core failure 事务（保持 gates pending） | failed |
| failed（未提交） | retry | 同 operation/request digest、plan 仍 confirmed/有效、重新授权 | Host journal | 新授权 durable；Core 重新执行 CAS | host-authorized |
| core-committed/failed（已提交） | recover | 只核对已存 commit，不重复业务 SQL；同操作授权仍合法 | Host durable recovered receipt → Core | CompleteSourceOperationRecovery 与全 gates open 同事务 | recovered |
| acknowledged/recovered | 任何同摘要重试/查询 | 同 operation_id | Host/Core | 返回原 commit receipt；**不创建 binding** | 原态 |

failed（已提交）后不能执行 apply 业务段，也不能把 state 改成 started。acknowledged/recovered 为终态；之后授权撤销影响每次 R/grant 校验，不倒改 receipt 或撤回已提交数据。未提交失败的 Host journal 必须留存；Core 查询可返回 not_found，Host 合并查询可给 origin=host。

ACK/recovery 的授权重验不是重新执行apply CAS：同registry、同物理identity且未撤销，fresh generation允许≥已提交基线（沿C-15读兼容）；低于基线/identity不符/Registry丢失拒绝。generation变大时Host必须锁后取得当前明确授权，不能自动恢复撤销的授权。CompletionRequest.authorization保存此次fresh授权，Core原authorization_json与commit receipt保持原字节；Host journal保存fresh授权确认。换registry/物理源必须另预览，不复用旧completion。failed→recovered须清error_code、retryable=0，并原子开门；acknowledged/recovered成功DTO两错误字段为null/false。新预览可在显式failed已提交操作之后，按当前binding为基线创建后继plan，不撤回旧提交；旧pending gate不因此打开。

### 3.3 ACK 前读门控与逐崩溃点

Core 业务提交时新 binding 可以 healthy/complete（C-15 不改），但每个新 binding 同事务插入 publication(read_gate=pending)。R、resolve、issue 新资源、Run 输入和 live edit/apply 在授权校验外，必须检查当前 binding 的 publication gate；pending → **SOURCE_ACCESS_DENIED**。它不是 V 的附加 SQL 条件：V 真仍可诊断，reader 按 C-16 既有不可读码跳过，不能新增 reader wire/改变 V。旧未参与同步且无 publication 行的 v7 binding 沿旧规则；新同步 binding 缺 publication 行属于损坏，fail-closed（由 plan receipt/new previous 链检测），不能当作 legacy 放行。

| 崩溃点/故障 | 重启持久事实 | 唯一恢复/重放结果 |
|---|---|---|
| Host started 落盘前 | 无 journal/Core operation | 重试相同 ID 可重新准备；没有业务成功 |
| Registry flush 前/失败 | 无 durable 授权确认 | 不 dispatch；Core 零写；保留 Host 失败（若能写） |
| Registry durable 后 journal authorized 前 | 可能只有 Registry 新快照 | 锁后核对物理身份/代次，补 journal；不能靠旧内存断言授权 |
| Host authorized 后 Core BEGIN 前 | Host journal 授权；Core 无 operation | fresh grants + 全 CAS，过期/漂移则零写拒绝 |
| Core BEGIN 内任一点/最后一页失败 | SQLite 未提交事务回滚 | 所有项目 bindings/人工/receipt/gates 与事务前相等；Host 记录失败 |
| Core COMMIT 后响应前 | applied + 一个 commit receipt + pending gates | 先 GetSourceOperation，**不再 apply**；同 ID 返回原 receipt |
| Host 收 Core receipt 前后、Host ACK 落盘前 | Core pending gate；Host 未确认 | 读仍拒绝，重读 Core receipt 后核对 Registry/授权 |
| Host ACK durable 后、Core ACK 前/ACK事务中 | Host 已保存同 commit_digest，Core pending 或事务回滚 | 重发同 ACK，原子开全部门；禁止局部开门 |
| Core ACK COMMIT 后响应丢失 | acknowledged + open gates | 同 ACK 返回原 receipt，不增 binding；当前 grant 校验仍执行 |
| Registry 旧快照/丢失、撤销、磁盘满、EOF | 代次不足/不可核验、不能 durable 或 grants 无效 | fail-closed；保留 pending/failed。已提交数据不撤销；不能自动重新授权；恢复须用户授权且满足同 plan 授权基线，否则另做新预览 |

没有 Host/Core 分布式事务：Host 先 durable 授权消除假授权；Core 原子业务+receipt+pending gate消除假发布；Host durable ACK + Core 原子开门消除重启绕门；短期 grant、同句柄稳定 lease 与提交边界撤销/CAS 保证源/授权事实。跨库 journal 的 orphan 允许存在，不能靠补偿删除用户数据来伪造整批回滚。没有任何 destructive OS 操作可重放。

## 4. 命令版本、能力与兼容

均 Host→Core，沿用现有 stdio envelope。ScanSourceSync（含Host缺失观察）、ApplySourceSyncPlan/RelinkSource/RepointSource/ResyncSource 以及 ACK/recovery/failure **必须走 host-control 私有会话**，普通 application 面返回 HOST_ONLY_REQUIRED；其余新Core命令沿Request/Response。不新增反向 RPC。每次新请求 request_id 可以不同，operation_id 不变。

`core.ping.capabilities` additive 字符串：`source.sync.scan/1`、`source.sync.plan/1`、`source.sync.apply/1`、`source.sync.relink/1`、`source.sync.repoint/1`、`source.sync.resync/1`、`source.sync.operation/1`。Host 先 probe，再结合本地 Registry/lease/schema/feature 状态输出 §5 Capability DTO。任一 probe 异常/缺能力 → CORE_CAPABILITY_MISSING；不创建 journal/secret、不 dispatch。写操作同时要求 source.read/1 + plan/apply/operation + 对应 kind 能力。不以 UNKNOWN_COMMAND 探测能力，不默认 Degraded-but-writable 放行。

| Host × Core | 旧 Core（无 C-17） | 新 Core（C-17 启用） |
|---|---|---|
| 旧 Host | 旧导入/读取不变 | 仅旧面；不发新命令，不能确认/打开 pending gate；若 Host 代次/协议无法核验则 R typed 拒绝 |
| 新 Host | capability 缺失拒绝同步；旧面继续 | 新面按能力与授权执行；默认 minor=3 不等于功能已实现 |

旧 **v7 Core** 另受 schema gate：打开已升级 v8 必须启动拒写，上表“旧面继续”仅指它能打开的 schema。新 Host 不通过旧 Core 修改新库；不自动降级。新 Host×旧 Core 的 ACK/recovery 同样不可猜测执行。

## 5. closed shape 命令与 DTO

以下表是规范字段表。`!`=必填且不可 null，`?`=必填但可 null；没有省略型可选字段。请求/嵌套 DTO 未知字段、缺字段、重复 key、错误类型、未知枚举 → INVALID_REQUEST；不作隐式字符串/数字/布尔转换。响应未知字段由 Host 安全投影忽略（M2-C1 additive 接收规则），未知状态/必填缺失/类型错 → PROTOCOL_VERSION_UNSUPPORTED，保留 UNKNOWN 诊断且绝不写/开门。未来新字段须新 capability/版本登记，不能变相突破此闭集。

类型缩写：ID=非空不含路径/控制字符的 string(1..128)；H=小写64hex；T=RFC3339 UTC string（本面精确毫秒，时间只作 TTL 不作排序真值）；N=integer 0..2^53-1（bool 不算整数）；I=integer -(2^53-1)..2^53-1（保留既有有符号顺序）；G=integer 1..2^53-1；数组上限10000，project_ids 1..20唯一按ID排序，其他集合按本节所述排序；单消息/持久 body 最多8MiB UTF-8，超限 SOURCE_BUDGET_EXCEEDED，禁止截断/拆成非原子提交。ID 不由 UI 推导 DB 主键；plan_id/operation_id 由 Host 创建，其他由 Core 返回。

### 5.1 命令表（每行字段全部必填）

| Core / Host 名 | 请求字段（required/nullability/type） | 成功 result | 取消、重试 |
|---|---|---|---|
| ScanSourceSync / source_scan_sync | source_id! ID; project_ids! ID[]; scope! current\|all; kind! relink\|repoint\|resync; grant_ids! ID[]; missing! MissingObservation[] | Scan | 同步有界扫描；transport 取消在安全检查点停止，Core DB零写；重试新 scan |
| PlanSourceSync / source_plan_sync | body! PlanBody | Plan | body.scan_id 须 live且与body一致；同plan_id同body返回原Plan，异body冲突；取消提交前零写，响应丢失同ID重试 |
| PreviewSourceSyncPlan / source_preview_sync_plan | plan_id! ID; plan_digest! H | Plan | draft→previewed；重复返回原值 |
| ConfirmSourceSyncPlan / source_confirm_sync_plan | plan_id! ID; plan_digest! H; confirmation! Confirmation | Plan | 独立确认点，不暗用导入确认；相同确认幂等 |
| InvalidateSourceSyncPlan / source_invalidate_sync_plan | plan_id! ID; plan_digest! H; reason! StaleReason | Plan | 明确失效写；不能失效已applied plan |
| ApplySourceSyncPlan / source_apply_sync_plan | ApplyRequest | Dispatch | 仅kind=resync；通用提交名，不等于导入 |
| RelinkSource / source_relink | ApplyRequest | Dispatch | 仅kind=relink、确认“找同一个文件”；内容变则拒绝并新建resync预览 |
| RepointSource / source_repoint | ApplyRequest | Dispatch | 仅kind=repoint、确认“改为引用另一个文件”；内容变化还必须确认resync_content |
| ResyncSource / source_resync | ApplyRequest | Dispatch | 仅kind=resync、确认“按预览同步内容”；与通用apply同语义去重 |
| GetSourceOperation / source_get_operation | operation_id! ID | Operation | Core durable查询跨重启；Host同名入口合并Host journal；未找到SOURCE_OPERATION_NOT_FOUND |
| CancelSourceOperation / source_cancel_operation | operation_id! ID; request_digest! H | CancelResult | 提交前设取消意图，在事务提交前裁决；提交后accepted=false。不是撤销业务提交 |
| AcknowledgeSourceOperation / Host内部 | CompletionRequest | Operation | host-control；先Host durable ACK；幂等开门 |
| CompleteSourceOperationRecovery / Host内部 | CompletionRequest | Operation | host-control；只恢复已提交operation，不重复业务SQL |
| RecordSourceOperationFailure / Host内部 | operation_id! ID; request_digest! H; code! FailureCode | Operation | 显式记录已提交但尚未确认的失败；不属stale Apply拒绝路径 |
| GetSourceSyncCapabilities / source_get_sync_capabilities | {} | Capabilities | Host本地聚合ping+Registry；不是Core新RPC；无写；**Core 不注册该名**，向 Core 发送按 M2-C1 既有未知命令语义拒绝（UNKNOWN_COMMAND） |

Dispatch 是接受响应，不是全部完成；Core 后台只允许一个 SQLite 写者，串行处理提交与cancel，不能长期阻塞stdio无法查询/撤销。提交前取消只改Host journal，Core业务事务回滚；完成查询可observed origin=host failed(code=SOURCE_SYNC_CANCELLED)。提交已赢得竞争则cancel返回accepted=false，继续确认/恢复。Apply可先返回accepted；业务前每个守卫失败由查询返回Host失败，Core receipt不存在；同步阶段直接发现stale则直接错误且Core零写。Host不能把accepted展示成成功。

### 5.2 DTO 字段表

| DTO | 全部字段（每项 ! 或 ?） |
|---|---|
| Capability | name! scan\|plan\|apply\|relink\|repoint\|resync\|operation; available! boolean; reason? capability_missing\|registry_unavailable\|schema_incompatible\|lease_unavailable\|disabled |
| Capabilities | items! Capability[恰好7，按上表顺序] |
| SourceBase | source_id! ID; version_id! ID; content_digest! H |
| AuthorizationBase | registry_id! ID; generation! G; identity_digest! H |
| MissingObservation | source_id! ID; registry_id! ID; generation! G; expected_identity_digest! H; observed_at! T |
| PageBase | page_id! ID; project_id! ID; chapter_id! ID; binding_id! ID; binding_version! G; source_id! ID; version_id! ID; entry_id! ID; source_order! I; sort_order! I; deleted! boolean; manual_digest! H; protection_digest! H; drafts_digest! H; runs_digest! H |
| PixelProfile | algorithm! pixel-digest/1; decoder! ID; decoder_version! ID; params_digest! H; width! G; height! G; orientation! 1\|3\|6\|8; pixel_digest! H |
| EntryEvidence | entry_id! ID; locator! string(1..4096,C-15相对locator); ordinal! N; content_digest_kind! encoded\|page-identity; content_digest? H; pixel? PixelProfile; reason? encrypted\|unsupported\|missing_evidence\|incomparable |
| SourceObservation | source_id! ID; version_id? ID; content_digest? H; identity_digest? H; entries! EntryEvidence[]; status! ok\|missing\|encrypted\|unsupported; reason_code? ExistingSourceCode |
| DiffItem | item_id! ID; classification! unchanged\|added\|missing\|changed\|ambiguous; page_id? ID; old_entry_id? ID; new_entry_id? ID; evidence! direct\|unique_pixel\|duplicate_group\|missing_old\|incomparable\|none |
| Totals | unchanged! N; added! N; missing! N; changed! N; ambiguous! N |
| Scan | scan_id! ID; expires_at! T; source! SourceObservation; base_sources! SourceBase[]; authorizations! AuthorizationBase[]; missing! MissingObservation[]; bases! PageBase[]; reference_set_digest! H; diff! DiffItem[]; totals! Totals |
| Decision | item_id! ID; action! keep\|add\|tombstone\|bind\|defer; target_page_id? ID; target_chapter_id? ID; new_source_order? I; new_sort_order? I; migrate_revision_ids! ID[] |
| Confirmation | kind! relink\|repoint\|resync; project_ids! ID[]; reference_set_digest! H; resync_content! boolean |
| PlanBody | format! source-sync-plan/1; plan_id! ID; scan_id! ID; source_id! ID; kind! relink\|repoint\|resync; project_ids! ID[]; scope! current\|all; base_sources! SourceBase[]; authorizations! AuthorizationBase[]; missing! MissingObservation[]; bases! PageBase[]; target! SourceObservation; reference_set_digest! H; diff! DiffItem[]; totals! Totals; decisions! Decision[]; confirmation! Confirmation |
| Plan | body! PlanBody; plan_digest! H; state! draft\|previewed\|confirmed\|applied\|stale; created_at! T; expires_at! T; previewed_at? T; confirmed_at? T; applied_at? T; stale_reason? StaleReason |
| ApplyRequest | operation_id! ID; plan_id! ID; plan_digest! H; grant_ids! ID[]; authorization! HostAuthorization |
| HostAuthorization | host_receipt_id! ID; operation_id! ID; request_digest! H; authorization_digest! H; authorizations! AuthorizationBase[]; authorized_at! T |
| Dispatch | operation_id! ID; request_digest! H; accepted! true; state! OperationState |
| BindingResult | page_id! ID; binding_id! ID; binding_version! G; source_id! ID; version_id! ID; entry_id! ID; status! healthy\|needs_confirmation\|missing |
| CommitReceipt | operation_id! ID; plan_id! ID; plan_digest! H; request_digest! H; bindings! BindingResult[]; committed_at! T |
| Operation | operation_id! ID; plan_id! ID; plan_digest! H; request_digest! H; kind! relink\|repoint\|resync; origin! host\|core; state! OperationState; commit? CommitReceipt; commit_digest? H; error_code? FailureCode; retryable! boolean; acknowledged_at? T |
| CompletionRequest | operation_id! ID; request_digest! H; commit_digest! H; host_receipt_id! ID; authorization! HostAuthorization; grant_ids! ID[] |
| CancelResult | operation_id! ID; accepted! boolean; state! OperationState |
| HostJournal | format! source-operation/1; authorization? HostAuthorization; operation! Operation; updated_at! T |

OperationState 六值与 §3.2 相同；StaleReason 八值与 SQL 相同；ExistingSourceCode/FailureCode 见 §8（FailureCode=该表全部code，存储error_code也只允许此闭集，成功为null）。HostAuthorization 不是可自签授权令牌：Core 必须在 live host-control 所属会话下验证既有 source-read grants 的 registry/generation/identity 与其 authorizations 一致、request_digest与operation一致、重新计算authorization_digest；application面不能凭自填json越权。authorization_digest=sha256(canonical(authorizations按registry_id排序))；identity_digest=sha256(canonical({content_digest,volume_serial,file_id,size_bytes}))，完整facts来自签名grant，不从调用方任意json读取。

commit_digest=sha256(canonical(CommitReceipt))。Host journal 用本DTO完整保存收到的receipt及摘要；paths/passwords/signatures/grants/session credentials 不进 journal、Core DB、receipt、错误、日志/证据。wirelog采用C-16 §7在进入Frames/NDJSON前脱敏，覆盖所有新命令嵌套grant/authorization的潜在敏感扩展；未知字段本已拒绝。

### 5.3 组合守卫与界限

- Scan TTL、Plan TTL 均≤300s（Plan不晚于scan.expires_at）；按Core时间校验，恢复已提交receipt/ACK不受plan TTL影响，但授权/grant必须有效。
- `totals` 必须严格等于各 classification 明细计数；diff按item_id、bases按(project_id,page_id)、base_sources按(source_id,version_id)、authorizations按registry_id、decisions按item_id排序，均唯一；target.entries按ordinal、bindings按page_id排序。所有参考ID均由Core核实。
- scope=current时project_ids恰好一个；all时等于冻结引用集合book去重值。reference_set_digest覆盖所有引用的(project,page,binding,version,status,deleted)，current也捕获全源共享集合；任何引用变化要求重新预览。scope=all 时若冻结引用集合的 book 去重数超过 project_ids 数组上限 20，Scan/PlanBody 以 INVALID_REQUEST 拒绝并提示按 project_ids 分批（不静默截断、不回退 current 语义）。
- added: page/old_entry=null，new_entry非null；missing相反；其余旧新均非null。unchanged须direct/unique_pixel；duplicate/missing_old/incomparable不可自动keep。defer不发布该歧义的新绑定，旧绑定保持needs_confirmation；tombstone保留旧页/人工/问题，不删除。
- decisions与diff一一对应。add有target_chapter/new_order且target_page=null；bind/keep/tombstone有target_page且与diff一致，新增顺序由plan明确，existing顺序不随容器重排；defer无迁移。migrate_revision_ids仅changed/repoint且显式bind允许，必须新建revision；其他数组为空。
- SourceObservation.status=ok时version_id/content_digest/identity_digest必非null，reason_code=null；missing时三者均null、entries为空、reason_code=SOURCE_ENTRY_MISSING；encrypted/unsupported时仅有可实际验证的容器摘要/identity，缺项为null，不造值。新增候选版本/entry的ID由Core在scan时分配，apply复用，不由Host伪造。
- 缺失源不能伪造有效source-read grant。新增C-17 Host-only `MissingObservation`只证明Host在当前Registry授权根内、按既有opaque locator观察到期望源缺失；Core与已有source location的registry/generation/identity逐项核对。missing数组按source_id排序、唯一，与缺失的SourceBase集合完全对应；其余源必须有精确live grant覆盖，grant_ids不可重复。整源缺失且仅tombstone/defer时可grant_ids=[]，不能读取/发布新原图或转healthy；非缺失源不能为空。apply前Host再次核对durable授权与缺失观察（源已恢复/被替换→stale）。这是新命令的无读缺失证明，不修改C-16 grant形状/校验；文件随后恢复不撤回tombstone，后续scan可重新预览恢复。缺失无需持有不存在文件的lease；其安全性来自不发布新内容、不删除任何旧数据。授权撤销/Registry丢失只诊断，不凭旧快照自动apply。ACK同理，仅missing binding开门也不使R成立。
- encrypted/unsupported或缺目标内容digest/profile无法完整验证时，只能有限scan诊断/草案；不能确认内容变更。missing只允许所有该源差异均tombstone/defer的确认，Core只沿已有source/version/entry建立missing代次，禁止无证据healthy。加密强扫描由用户发起，Host复用C-16一次性secret grant；本面没有secret_ref字段、不在后台请求密码。有限结果要求新的完整scan/new plan再确认，不把确认后解密出来的未知mapping直接apply。旧导入的加密有限预览/逐页提交仍按C-16不变。
- `Confirmation`须与body.kind/project_ids/reference_set_digest完全一致，重复确认不得更改resync_content；repoint若内容变必须true；纯relink需物理同一且内容未变，跨卷重新强验证，无法证明同一则转repoint预览。同bytes不同物理源不同source/entry；resync新条目按C-15保续，不能拿ordinal偷换身份。

## 6. CAS、事务与失败原子性

### 6.1 比较对象（相互独立）

| 基线 | 精确比较对象/反例 | 提交事务内重读/外部校验位置 |
|---|---|---|
| SourceVersion | 每个base_source(source_id,version_id,content_digest)及目标容器/member digest；同mtime/size字节变也失配 | BEGIN IMMEDIATE后重读source_versions/entries及当前binding接受版本；事务前取稳定lease验digest，提交前再Verify同句柄/有效lease |
| binding_version | 每页(binding_id,binding_version,source/version/entry,status,previous) + page→chapter→book归属/删态/顺序 + 完整引用集合 | 在任何业务INSERT/UPDATE前，重读**全部**bases及共享引用，不能只读第一项目；版本+1只在同事务成功时发布 |
| Host authorization generation | 每registry的expected generation + identity_digest；apply时当前必须**等于**plan授权基线 | Host锁后重读持久Registry，再铸grant；Core在BEGIN后及COMMIT前验证live grant/generation/撤销/EOF；ACK同代次重验 |
| 人工 revision | 每region的current_revision_id、revision_no与完整current文本/geometry/style/manual标记 | manual_digest=hash(canonical逐region按ID排序{region_id,current_revision_id,revision_no,geometry_json,text_json,style_json,deleted_at}))；事务内重算；第三项失配整批回滚 |
| Lock/保护 | page锁、区域三锁、manual位、current/pinned revision集合、问题/进度基线 | protection_digest=hash(canonical这些字段的完整投影)；按现有Protection语义判断，不拿摘要绕过Lock；此处不是重定义C-13 protectionDigest |
| draft/Run | DraftId/SessionId/sequence/baseRevision/bindingVersion/status与Run已接受/在途目标及来源快照 | drafts_digest/runs_digest由Core权威投影（空集合也摘要）；写事务前获得现有draft协调屏障，事务内重读journal/Run投影及权威内存epoch，直到commit保持屏障 |

C-15读兼容仍为binding.authorization_generation **≤** 当前Host generation且同物理identity授权有效；此处 **apply CAS 等值**只限定本次预览事务，不改变旧binding日常读规则。SourceVersion不是authorization generation，也不是binding_version；decoder观察升级不改变SourceVersion/content_digest。

### 6.2 唯一原子单元与零写基线

单plan的**所有选中项目/页/区域**是一个SQLite业务事务：重读全部守卫 → source/location/version/entries → 旧binding superseded + 新binding → pages/tombstone/必要人工迁移新revision/lineage → operation receipt + pending publications → plan applied → COMMIT。新旧位置原地复用/唯一性沿C-15；未选项目accepted version/人工/进度不变。新页ID预先分配但只在commit可见。对保留页保护/顺序/进度不做重置。未选项目诊断变化只可由独立scan/diagnostic流程显式记录，本次apply不顺带写。

**整批最后一项失败的唯一结果：上述Core事务全部回滚，成功页数=0，无新binding/人工revision/receipt/gate/plan状态变化。** Host事先持久化授权/journal保留，允许failed诊断；不是回滚Host授权或源文件。没有逐页提交/部分成功；不调用现有`commit_referenced_page_unit`逐页拼批次。C-16导入的一页事务与会话receipt不变，与此不同操作域。

stale Apply 零写以此前合法持久化confirmed plan为基线：pages/bindings/source/location/version/entries、regions/text/current/revisions、Lock/pin/问题/进度、lineage/publications、source_operations以及plan表均前后相等；不创建拒绝receipt。Host receipt为授权面诊断，不是Core业务写。预提交取消/授权/DB错误同样没有部分业务提交；若错误记录需Core持久化，必须另发显式管理命令，本面仅提供提交后failure命令。两个并发apply：SQLite串行写者+完整CAS+plan唯一receipt确保最多一个成功，后者同operation返回原receipt，异operation返回SOURCE_PLAN_STALE/OPERATION_CONFLICT，均无第二代。

源读取/解码在DB事务外完成并验证，输入提取后不在网络调用期间长期锁源；apply前重新取得稳定lease并持到commit。所有参与读取的源/路径需一致lease（纯missing无读分支严格按§5.3）；远程/可移动卷无法证明稳定则SOURCE_SYNC_UNSTABLE拒绝，不用DB事务掩盖OS替换。提交中撤销按C-15/C-16在下一个提交边界阻断；Host需在响应撤销成功前收到Core ACK，不能仅依赖TTL。具体锁/句柄API、取消队列实现留FEA-11设计，但不能删去这些守卫或缩小原子单元。

## 7. lineage、在途任务与资源选择

### 7.1 lineage 存储和隔离

`source_revision_lineage` 一行对应一个不可变Region revision；`source_binding_publications` 同时保存旧→新binding边、relation和durable读门。首次同步切换前，在同一业务事务将受影响旧region的**当前revision**快照归属旧binding(provenance=captured_v7)，其他无证据历史revision登记legacy_unverified(binding_id=null)。captured_v7仅证明切换时当前基线，不证明任意历史图；若已有previous链或已知revision的source基线不符，当前revision也必须legacy_unverified，不能猜。已由native/migrated记录的归属不改。无current_revision的旧region仅作历史/诊断，不冒充新图可编辑区域。
- `source_revision_lineage.operation_id` 归属：captured_v7 行回填当次 operation_id（可审计）；native 日常写入留 NULL。

所有后续新revision写入必须同事务登记native/migrated lineage。对本卡涉及的同步页，编辑/渲染/导出/Run读取“当前区域”必须满足region.current_revision的lineage binding等于当前binding，或沿publication.previous仅经过**same_content**边可达；并验证region/revision/page归属。same_content只有direct/unique_pixel且尺寸/方向/坐标profile等价、无内容改变时成立。changed/repoint/missing切断坐标继承；同bytes不同源的repoint也不自动复用旧区域。

未迁移旧region/revision仍可按旧binding在历史/管理诊断读取（含legacy_unverified标签），不通过普通新图ListRegions/渲染/导出/Run查询拼回去；应用装配须确保现有page_id-only repository不会成为旁路。源缺失无旧原图时可读元数据/人工文本，诚实显示原图不可验证，不用新图模拟历史。managed页原有编辑路径不改变。

人工迁移使用C-13 RegionCandidate prepare（新目标RegionId，origin=user，源revision可追溯），live apply事务校验全部BaseRevisionId、Lock、draft和binding基线；同plan事务新建目标region/revision、lineage(provenance=migrated,from_revision_id=旧revision)，不移动/覆盖旧region/revision。第三个region冲突前两个也不发布。新目标BaseRevisionId=null仅允许目标仍不存在；源revision必须仍为确认的当前值。

| 交错/样例 | 唯一预期 |
|---|---|
| old binding B1/revision R1 → changed B2，未迁移 | R1只在B1历史；B2新图区域集合不含R1；PageId/人工/Lock/问题/进度保留 |
| B1/R1 → same_content B2 | 允许通过等价边读取R1；用户顺序不随新容器ordinal变化 |
| 手动 R1→B2 | 新region G2、新revision R2，from_revision_id=R1；R1原字节/归属不变 |
| Prepare Run(B1)后同步B2 | 旧Accept/结果live apply拒绝STALE_RUN_SNAPSHOT/既有source guard；结果留candidate，不改已接受快照 |
| 旧draft/edit token绑定B1，当前B2为changed | flush/live apply冲突，不写B2；保留draft恢复入口，不自动丢弃；重开B2新草稿 |
| candidate基于B1而B2已切换 | 不自动重基；新prepare/显式迁移 + 全部CAS后才可发布 |
| apply扫描后draft/Lock/current/pin/Run任一变 | §6重读失配，Core零写，用户重预览 |

### 7.2 resolve/issue 资源版本选择

保持`resolve_page_resource {page_id} → {resource_id,revision:"original"}`形状及managed `page-original-{page_id}`稳定键不变。referenced新实现一律选择

`resource_id="page-rendition-v2-"+sha256(canonical({page_id,binding_id,source_id,version_id,entry_id,verified_digest,rendition_kind,decoder_name,decoder_version,params_digest}))`。

门控/授权/identity检查在cache/catalog命中前；产物仍只能decoded/re-encoded rendition。key带binding和decoder/profile，发生变化必然另key；同key既有摘要不同→既有typed资源冲突，绝不替换。catalog丢文件自愈先验证已登记摘要一致。不能仅遇到`page-rendition-{page_id}`已存在便返回它。

示例：B1先发布旧键K0=`page-rendition-P1`摘要D0；升级后B1 resolve可另发布Kv1（选择函数v2，内容仍D0）；同步到B2并ACK后选择Kv2，解码新内容摘要D2。K0/Kv1仍返回其原摘要或typed过期/缺失，**绝不读到D2**；Kv2只对应B2/D2。同PageId不意味着同resource_id。resolve与issue/实际资源读取必须使用同一选择结果；已发资源引用遵循原TTL/revoke，不追溯撤回已读字节，也不因同步自动授予旧资源新源权限。旧源不可重现时不能用B2重建K0。

### 7.3 C-15 §3.2 证据映射（不建立第二套匹配规则）

| 路径 | C-15条件 | C-17决定/AC索引 |
|---|---|---|
| 同source且容器digest不变 | entry直接保续，decoder变化只观察 | direct；保留EntryId/PageId/顺序；P4/P5/P6 |
| 容器变化且pixel证据可比 | 同algorithm/decoder/version/params、尺寸方向，一对一唯一 | unique_pixel；只在坐标等价时same_content；P4/P5 |
| 重复name/pixel occurrence | 全组needs_confirmation，不按ordinal/locator锚定 | duplicate_group；逐项bind/defer，禁自动搬人工；P3/P5 |
| 旧pixel缺失或profile不可比 | 可取得真实旧输入时按冻结参数重算；仍不可比或旧输入不可得 | missing_old/incomparable，待确认/不可验证；禁从新图伪造旧证据；P1/P3/P5/P6 |

现有`referenced/runtime.py::_entry_row`确实写pixel/orientation=None；FEA-11必须包含真实v7导入旧库fixture。旧证据缺失不是“匹配未找到”的等价证据；不自动删页或覆盖人工。感知hash/OCR相似仅候选。人工确认不会把不存在的旧pixel补成已验证。

## 8. 局部错误闭集与诊断

沿用既有ErrorEnvelope字段，不改全局taxonomy；下表仅C-17命令投影，旧命令不重映射。details仅允许`{operation_id?:ID, plan_id?:ID, cause?:StaleReason, count?:N}`（此处?为可省略的错误诊断字段，出现时非null；仅本错误details例外），无任意message/path/签名材料；message用固定安全文本。ExistingSourceCode为表中标“既有”的Source/identity码；FailureCode为全表code。

| code | category | retryable | 来源/处理 |
|---|---|---|---|
| INVALID_REQUEST | validation | false | 既有；字段/枚举/范围错误 |
| CORE_CAPABILITY_MISSING | protocol | false | 既有；先升级配对，不重试dispatch |
| PROTOCOL_VERSION_UNSUPPORTED | protocol | false | 既有；含新响应未知状态 |
| HOST_ONLY_REQUIRED | validation | false | 既有M2-C1 §5.7；普通面调用控制命令 |
| HOST_SESSION_INVALID | conflict | false | 既有M2-C1 §5.7；credential/session失效 |
| CORE_SESSION_MISMATCH | conflict | false | 既有M2-C1 §5.7；Core进程不匹配 |
| SOURCE_PLAN_STALE | conflict | true | 既有；必须重新scan/preview，不盲重放旧body |
| SOURCE_OPERATION_CONFLICT | conflict | false | 既有；同ID异摘要/plan已有另一operation |
| SOURCE_OPERATION_NOT_FOUND | not_found | false | 既有；Core无receipt可查询Host，不冒充完成 |
| SOURCE_ACCESS_DENIED | authorization | false | 既有；含pending gate/identity/scope不符 |
| SOURCE_GRANT_EXPIRED | authorization | true | 既有；fresh grant，同语义ID重试 |
| SOURCE_GRANT_REVOKED | authorization | false | 既有；含EOF，无自动重授权 |
| SOURCE_REGISTRY_UNAVAILABLE | internal | true | 既有；保留原件/failed/pending，损坏需显式恢复 |
| SOURCE_REGISTRY_BUSY | internal | true | 既有；锁后重载再核对plan generation |
| SOURCE_PASSWORD_REQUIRED | validation | false | 既有；显式用户密码入口，不在后台重试 |
| SOURCE_PASSWORD_INVALID | validation | false | 既有；沿C-16次数/冷却策略 |
| SOURCE_FORMAT_UNSUPPORTED | validation | false | 既有；不能新依赖绕过 |
| SOURCE_ENTRY_MISSING | not_found | false | 既有；诊断/重预览 |
| SOURCE_BUDGET_EXCEEDED | validation | false | 既有；不截断原子plan |
| SOURCE_PROJECT_MISMATCH | validation | false | 既有；事务内归属守卫 |
| FILE_IDENTITY_CHANGED | conflict | true | 既有；重新验证/预览 |
| REF_SIGNATURE_INVALID | validation | false | 既有grant校验；不能降级授权 |
| STALE_BASE_REVISION | conflict | true | 既有编辑冲突；重prepare/确认。本面 retryable=true 表示"重新 prepare/确认后可重试"；FEA-05 drafts_apply 面对同 code 的 retryable=false 表示"同请求原样重发不可重试"。retryable 是命令级投影（M2-C1 §8），同一 code 在两面并存不构成全局映射 |
| SOURCE_SYNC_STATE_CONFLICT | conflict | false | **C-17新增局部码**；非法状态事件/操作kind不符 |
| SOURCE_SYNC_UNSTABLE | conflict | true | **新增**；无法取得覆盖全目标的稳定lease，条件改变后重试 |
| SOURCE_SYNC_CANCELLED | conflict | false | **新增**；提交前取消，业务零写；显式重试同ID须plan仍有效 |
| SOURCE_SYNC_STORAGE_FAILED | internal | true | **新增**；DB/Host journal IO失败；先查询receipt判定是否已提交 |
| SOURCE_MIGRATION_FAILED | internal | false | 既有存储启动码；不启动服务、不自动降级 |

runtime错误优先级沿C-16签名→过期→撤销→授权→identity→预算；其次请求/plan基线与CAS错误。检测到stale/人工基线漂移统一SOURCE_PLAN_STALE(cause=...)，只有显式人工迁移live apply的BaseRevisionId冲突沿STALE_BASE_REVISION；不在旧命令中新塞C-17错误。未知异常安全投影SOURCE_SYNC_STORAGE_FAILED，不返回异常原文。RecordSourceOperationFailure不能接受任意字符串。

## 9. 冻结可执行清单与下游验证

隔离脚本和日志在`verification/FEA-11-PREREQ-1/`，只用`:memory:`。COMMAND/EXIT/解释器/SQLite/基线在日志头；不是生产升级或真实IPC证据。

| AC | 冻结输入/可执行断言 | 本次证据与DSH复核方式 |
|---|---|---|
| P1 | §2 SQL全文；真实v1–v7生成的内存合成库追加候选；FK/UNIQUE/CHECK负例；DDL中途/元数据后失败整回滚；旧v7 runner拒写 | validate_contract.py + sql-validation.log；DSH独立复跑，确认版本号未占用 |
| P2 | §3两状态表、逐崩溃点、存储归属、ACK durable顺序/门控 | 文档条款Review + examples.log的最小门控/重放模型；真实杀进程NOT_RUN，归FEA-11 |
| P3 | §4/§5/§8命令/DTO/错误闭集、unknown字段、四象限、版本面分离 | wire-schema.json + validate_wire.py + wire-validation.log；每命令正例及missing/null/type/enum/unknown负例 |
| P4 | §6三代次/人工/draft/Run基线、完整范围、单plan多项目整批回滚；stale零Core写 | sql-validation.log整批最后项失败；examples.log CAS模型；真实并发/lease/撤销NOT_RUN |
| P5 | §7.1/§7.3 lineage持久表达/坐标隔离、候选/Run/draft、旧证据降级 | SQL lineage负例 + examples.log；DSH核对B1/R1→B2/R2；实际旧库/生产装配NOT_RUN |
| P6 | §7.2选择函数与旧键D0/新键D2、密码/grant/gate无旁路 | examples.log确定性选择对照；真实resolve/issue字节NOT_RUN，归FEA-11 |
| P7 | 最终字节独立Review approved、冻结记录、三指纹、pin18 | 本卡仅候选指纹；DSH固定语义commit/reviewed_head并复算最终字节、追加pin18；当前17/17不是18项完成 |
| P8 | allowed_paths范围、旧17冻结契约/旧迁移/FEA08/09/10证据零diff、无生产实现/依赖/用户数据 | scope-validation.log + baseline.json + governance/pins日志；DSH复核实际diff含untracked |

冻结记录必须填写：最终语义commit、实际reviewed_head、Reviewer身份/来源、该head blob ID/blob SHA-256、工作树SHA-256、最终冻结字节三指纹与复核字节差异。只允许经明确记录的状态行/冻结链接元数据差异；任何条款/SQL/DTO变动都需新head复核。最后编辑后重新计算，工作树pin与LF blob摘要可能不同，不能混用。DSH单点给verify_pins追加`C17=FEA-C17_SOURCE_SYNC_DRAFT.md`，missing-record/no-pin/mismatch继续失败；不得为了草稿把新pin做成跳过。

下游FEA-11必须验证：真实v7升级与旧导入库/人工数据守恒、同源多book批次最后冲突、真实Host/Core新进程崩溃矩阵、真实grant/lease/即时撤销/DPAPI、在途Run/draft/candidate生产装配、resolve→issue→新旧实际字节、managed五读路径与全量回归。新接口仅到Host/API，不宣称UI用户流程已完成。本卡的隔离模型不能替代这些证据。
