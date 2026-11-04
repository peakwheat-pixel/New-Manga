---
task_id: FEA-11
reviewer: Codex（用户指定的全新上下文；未参与 FEA-11 建卡、实现或返修）
reviewer_kind: agent
author: DSH（Task 建卡与范围冻结责任方）
base_commit: 811f5d3357598354e11debaad3248a0520d943f5
reviewed_head: 811f5d3357598354e11debaad3248a0520d943f5
decision: changes_requested
review_type: scope
date: 2026-11-04
---

# FEA-11 Scope Review r1

## 身份、对象与边界

- 来源：用户在本独立 Codex 会话直接委任 Scope Review；非实现会话的自审，未派发子 agent。Task 的 `reviewer: null` 尚待 DSH 登记，不代替 Appointment。
- 工作区：`G:/CODEX/New Manga`，branch `main`，Git common directory `.git`；审查开始与写报告前 HEAD 均为上列完整 SHA，工作区 clean。
- 对象：该 HEAD 中的 `doc/tasks/FEA-11.md`，不是生产实现的批准。`base_commit=reviewed_head` 表示对当前卡片快照及其依据审查，不宣称存在实现 diff。
- 唯一写入：本报告。未改 Task/STATUS/PLAN、生产代码、测试、证据或契约；未 commit/push。
- 依据：AD-002 的 AD-003 更新边界、当前 STATUS/PLAN、rolling checkpoint 当前收口记录、提案 §8.1–8.4/§12.1/§12.3 A10/§15.5–15.6、FEA-09 closeout、FEA-10 Task 与 Handoff 最终 Closeout、C-05 v1.2/C-13/C-15 v1.1/C-04b。
- 沿引用补查 C-14 v3、C-06/C-16 v1.1：C-14 是同步/重定位的直接语义契约，C-15 §3/§7、C-14 §4 又明确指向授权/wire 边界。未扫描历史 Review/verification 全集。

## 结论

**changes_requested：P0=0 / P1=8 / P2=3。当前不能冻结 scope 或转 ready。**

Architecture：方向符合 AD-003，scan/diff/plan、tombstone、共享引用和源字节保护均有初步承载；但契约前置、操作分类、CAS/事务、旧内容 lineage、跨进程 journal 和生产读图出口仍未闭合。

Verification：本轮完成静态追溯与只读治理检查，未运行功能测试。以下缺口是“范围/验收定义不足”，不等于已复现尚不存在的 FEA-11 实现缺陷。治理 PASS、17 pins PASS 也不证明本卡语义完整。

FEA-09/10 **done 前置满足**：FEA-09 closeout 固定 `87ca50702e00c62c64540ac7ac4ff3b1d27fa0cd`；FEA-10 当前 Task 固定 delivery `d1972f0f7cd9b3e17c5289818b5b3b25e164d5e9`、integration `3a9ab00258d0b3967e624128951dabae82196436`，最终 Handoff Closeout 已覆盖前文历史未完成说明。不能把其已登记债务自动解释为 FEA-11 能力已验证。

## Findings

全部 `open`，由 DSH 处置；P0 无。

### S11-001 · P1 · DDL/wire 前置仍是待定项，尚无可执行的硬 Gate

**位置**：Task `:11–13/:47/:64–66`；C-15 §1“预留”及 §8；C-16 §0/§4；`src/bootstrap/core_service.py:311–320`；`NewManga.Host/Sources/SourceReadCoordinator.cs:226–267`。

**问题/影响**：卡片只依赖 FEA-09/10。C-15 明确不创建/冻结 `source_sync_plans/source_operations`，要求 FEA-11/12 前置契约以 v8+ 追加；现有 Core/Host Source 命令只覆盖授权与引用导入，没有 scan/plan/apply/relink/repoint/resync 或持久 operation 查询。AC11-9 的真实 IPC 在当前冻结命令面上无法实现，不能保留“是否新增 wire”直到 Owner 实施时决定。

**建议**：建立并登记独立 `FEA-11-PREREQ-1`（名称待 DSH 决定），使其 done 成为 FEA-11 ready 的硬前置。冻结：两表 DDL/索引/FK/约束、迁移版本预留、plan/operation 状态与存储归属、命令/closed shape、能力探测、错误 category/retryable、兼容策略。v8 是当前下一候选，不是本报告替 DSH 预占的版本。**新增命令是所要求外部链路的必要能力；具体数量、命名与 minor 是否 bump 须契约裁决**，不能自行认定必须 bump（C-16 已有 additive minor=3 先例）。若窄扩现有命令，仍须先走相应契约修订，不能暗用导入 API 表达同步。冻结旧契约字节继续不在 FEA-11 实现写域。

### S11-002 · P1 · 遗漏 C-14 的 repoint 与操作身份断言

**位置**：Task `:41/:47/:56/:65`；C-14 SC-S01–S03、SC-S11。

**问题/影响**：卡片把“找同一文件”和“改指向另一个文件”概括为 relink，没有把 C-14 列入直接依据，也未定义 repoint。C-14 要求不同命令/确认文案；纯 relink 保留 EntryId/PageId/人工版本/区域/进度，repoint 改 EntryId，内容已变须走 resync 确认。缺此边界会允许只改路径就接受替换文件。另未规定容器重排不自动改变已绑定 PageId 的用户顺序。

**建议**：AC11-6 分列 relink/repoint/resync，绑定各自 preview、身份/版本和共享范围断言；补纯改名/同文件移动、跨卷重新验证、同 bytes 不同物理文件、替换容器、仅当前/全部引用的矩阵。全部引用也只能更新预览中确认的集合；确认前引用集合变化应重新预览。按 SC-S11 验证已有页顺序不随成员重排变化；新页插入顺序由 plan 明示。若拟延期 repoint，先由 DSH 记录需求承接与范围裁定，不能默认为 FEA-12/13/14。

### S11-003 · P1 · 匹配 AC 比冻结的跨版本证据规则宽，且未处理旧证据缺失

**位置**：Task `:53`；C-15 §3.2（尤其第 4 项，`:230`）；`src/application/importing/referenced/runtime.py:831–867`。

**问题/影响**：AC11-3 的“成员内容/规范解码像素 digest”允许把两者当无条件替代，也只禁止 occurrence 合并。C-15 对容器 digest 变化已冻结可比 pixel profile、一对一唯一匹配；重复 occurrence 整组 needs_confirmation，不能靠 ordinal/locator 自动保续。现有 `_entry_row` 写 `pixel_digest/pixel_digest_algorithm/orientation=None`，FEA-09 done 不代表已有完整旧页匹配证据。源被覆盖后，旧版本可能无法重算。

**建议**：明确同源同容器 digest 的直接保续，与容器变化后的跨版本匹配是两条路径；后者逐项验证 algorithm/decoder/version/params/尺寸/方向及唯一性。旧证据不存在、profile 不可比且不能按冻结参数重算时，必须降为待确认/不可验证，不能从新图伪造旧证据。重复名、重复像素即使未合并成一行，也须断言整组不会按位置自动搬运人工成果。补 FEA-09 真实导入的旧库 fixture，而不只构造已填满 pixel 字段的理想数据。任何放宽应先契约裁决。

### S11-004 · P1 · L2 的代次 CAS、失败原子性和“零写”缺少可判定边界

**位置**：Task `:52/:54–56/:58`；提案 §8.4/§15.6 FEA-11；C-13 SC-D08；`src/infrastructure/sqlite/library.py:1865`。

**问题/影响**：目前只有“基础 versions/generation”“stale 零写”和“事务发布”的描述，没有列比较对象、同事务检查位置、事务单元以及竞态断言。现有导入单元是“一页一个事务”，不能据此声称整份 sync plan 或共享批次原子；通用单条 repository 写法也不能直接拼成批量提交。无法区分源版本变化、binding_version 变化、Host 授权 generation 变化与人工 revision/Lock/draft 变化。

**建议**：在 PREREQ/impl-design 冻结三类代次的意义及 CAS；Core 提交事务内重读完整受影响 binding/版本/项目归属及必要人工基线，结合有效 lease 持有至提交边界。明确单 plan/多项目的原子单元；批次最后一页/最后一项目冲突时，前面的写入是否整体回滚必须有唯一口径。AC11-4/5 增补两个并发 apply 只有一个成功、源/绑定/范围/决定各自漂移、授权撤销/失联、第三个区域 BaseRevisionId 冲突、DB 失败的断言。stale Apply 以前一时刻已持久化 plan 为基线，比较 pages/bindings/source rows、regions/text/current/revisions、保护/进度及 operation/receipt，明确不能在拒绝路径偷偷发布部分新代次。若希望拒绝审计也落盘，须 DSH 明确其与 A10“零写”的边界，不能由实现者自行放宽。

### S11-005 · P1 · “旧区域留旧 lineage”缺少存储和读写隔离落点

**位置**：Task `:55`；C-14 SC-S07；C-13 SC-D07/08；`src/infrastructure/sqlite/schema.py:227–263`、`regions.py:126–138`；`src/bootstrap/core_assembly.py:1527–1553`。

**问题/影响**：当前 regions 仅经 page_id 归属，`list_regions(page_id)` 未按 binding lineage 分派；page_bindings.previous_binding_id 并不自动给区域加旧内容归属。只新增 binding generation 而保留同 PageId，会使旧区域仍可被当作新图当前区域。卡片也未验证同步与在途 Run/旧草稿/旧 candidate 交错。

**建议**：冻结旧 region/revision→binding lineage 与迁移来源的可恢复映射（可采用旁表/既有快照扩展，具体结构由 DSH 定，不能预设只需两张新表）。定义未迁移旧区域的诊断/历史入口，以及新图编辑、渲染、导出、Run 目标读取不套旧坐标的规则。手动迁移走新的 RegionCandidate/revision、BaseRevisionId 与 Lock 检查；第三项失败整批回滚。复用现有 Run guard 与 draft 机制，增加“Prepare 后同步→旧 Accept/结果 apply 被阻止、结果留 candidate”“旧 edit token 不写新 binding”的生产装配测试。不得因本 Task 自动改写已接受 Run 快照或扩成 provider 新能力。

### S11-006 · P1 · durable operation 与 Host/Core 双确认的状态机未冻结

**位置**：Task `:58/:66`；提案 §8.2；C-14 SC-S04；C-15 §5–6；C-16 §4；`referenced/runtime.py:134`、`SourceReadCoordinator.cs:15–21`。

**问题/影响**：现有导入 `_operations`、Host grant/payload 映射都是会话内状态；FEA-10 的 durable receipt 属 Run，不证明源操作重启幂等。C-15 已规定 Host 先持久化授权，再 Core 提交 healthy binding；卡片“未达双方确认不可读”未定义确认点和状态存储，容易实现成 Core 先 healthy、Host 后持久化，或引入与冻结顺序相反的通用两阶段提交。

**建议**：保持 C-15 Host durable authorization 在先；在前置契约/impl-design 中冻结 operationId 与请求 digest/目标集合绑定、每步 durable receipt、ACK/重放与恢复核对顺序。若还需 Core 提交后的 Host ACK，明确 ACK 前读门控由何处保存并在重启后维持，不能靠内存标志。相同 key+相同请求返回原结果；相同 key+不同 plan/范围拒绝；响应丢失重试不再增 binding。分别在 Host 持久化前后、Core 事务前后、ACK 前后杀 Host/Core，并用真实新进程读取 journal/registry/DB 验证恢复；不是只重建一个对象。授权撤销、磁盘满、旧 registry snapshot、grant 过期/失联都须有结果断言，不重放破坏性 OS 操作。

### S11-007 · P1 · 新 binding 后生产 resolve 仍可能命中旧 PageId 资源

**位置**：Task `:55/:59`；`src/bootstrap/core_service.py:3413/:3547–3553/:3581`；`referenced/resolve.py:104–118`；C-15 §4.2。

**问题/影响**：rendition cache key 已带 version/entry，但生产 served catalog 使用 `page-rendition-{page_id}`；`_publish_rendition_bytes` 见同键产物存在便返回，未按新 binding 选择新资源。保持 PageId 同步到新内容时，即使 DB 与 cache 正确，读图出口也可能继续给旧图。此为现有 seam 对未来 FEA-11 的范围要求，本轮未执行动态复现。

**建议**：加入明确 AC：先 resolve 旧绑定并实际读取资源字节→同步新绑定→生产 resolve/issue/读取新内容；旧资源键/已发布摘要仍不可变。由 DSH 冻结 referenced resource key/版本选择方案，不能直接覆盖同键旧图；确认是否触及冻结资源语义，必要时归 PREREQ。将 `core_service.py` 的该窄 seam 纳入写域；测试不能只断言 rendition_cache 行不同。

### S11-008 · P1 · 写域缺少必要旧文件，且预览/缺失页的可观察出口未定

**位置**：Task `:22–31/:57/:59/:74–80`；提案 §15.6；C-05 §3.2；`library.py:395–412/:1767`；`SourceImportModels.cs`。

**问题/影响**：`src/application/sources/**`、`tests/fea11/**` 既未文件化，也漏掉 DB、bootstrap、Host 授权/路由和 C# 测试。AC11-7 要求“显示缺失”，但 C-05 P8 本就排除非 healthy referenced 页，现有 get/list_page 不能充当 tombstone 管理入口。现有 SourceImportModels 仅提供导入端口，不能据此声称已有同步确认 UI。卡片未说明 AC11-9 验收至 Host/API，还是包括真实用户可达 UI。

**建议**：采用下列文件级清单作为 DSH 冻结输入；每项标注职责/AC。明确管理诊断读取 missing/needs_confirmation/tombstone 的非 V 数据出口，保留 C-05 的 V/R 区分，不为“显示缺失”暗改可见性契约。DSH 决定 FEA-11 的预览确认端口边界；如含 UI，先指定 ZCode 的独立 UI 切片、精确 View/VM/端口与可达性 AC；如仅至 Host/API，明确 UI 后续承接且不得宣称用户流程完成。不得自行列整个 App 或整个 Host 目录。

### S11-009 · P2 · 检测调度范围仍自相矛盾

**位置**：Task `:51/:68`。

“四路”已写为 AC，而待裁决又说后台扫描可能后移，“只做前三路 + dirty hint 消费”仍包含后台扫描，不能识别究竟延期哪条。建议分别冻结启动/访问前、操作前、定时扫描、watcher 生产者/消费者；给触发点、扫描范围、取消/重入/节流、丢通知/overflow 后全量重枚举的测试。若只做 hint 消费，生产者的 Task 与当前不可宣称的能力须登记。dirty hint 不能直接改 binding，也不能替代强验证。

### S11-010 · P2 · 验证矩阵尚是文件名清单，缺少守恒与证据归属

**位置**：Task `:60/:70–81`；提案 §12.3 A10；协作协议 §4.1/§4.2。

AC11-7/10 无独立判据；源字节保留仅在目标中，未明确 hash/mtime/文件数前后守恒；“全量不减少”不能排除 skip 增加。隔离路径 `workspace/FEA-11/...` 也未指明仓外真实根。建议采用下方逐 AC 断言矩阵，新增 Canonical Evidence/Resource Manifest 计划表。测试 TEMP/TMP、DataRoot、DB、Host registry、fixtures、bin/obj、TRX、IPC 输出均固定到 `G:/CODEX/New Manga.workspace/FEA-11/` 的 Task 子目录；重复运行原始输出不复写 FEA-09/10 的 tracked 证据。每个 AC 有 EV、命令/解释器/shell/EXIT/commit，passed/failed/skipped 与原因分别记录；行为断言比单纯数量优先。

### S11-011 · P2 · 当前 DAG 的 FEA-11 行存在四列错位

**位置**：`doc/REBASELINE_PLAN.md:10`。

三列表头下实际是 `|FEA-C11-PREREQ-1|FEA-11|FEA-09、FEA-10|proposed...|`。本来 FEA-C11 是已完成的历史契约前置，该行会把 FEA-11/依赖/状态解析错位；正文链虽明确 FEA-11 proposed，不能代替唯一 DAG 的结构修正。交 DSH 按实际节点拆回三列，新增 FEA-11 前置时用独立新 ID，保留既有 C11 历史身份。Reviewer 不改 PLAN，也不凭此批准任何释放。

## 建议的精确 allowed_paths

**下表全是待 DSH 冻结项，不是本报告授权。** “现有”已现场定位；“新增”是建议落点，可在冻结前合并/更名，但最终 Task 必须逐文件列出。不要把建议文件数变成强制设计；优先沿现有注入端口复用。

### Core 实现候选

| 精确路径 | 状态、职责与限制 |
|---|---|
| `src/application/sources/__init__.py` | 新增；应用模块入口 |
| `src/application/sources/model.py` | 新增；diff/mapping/plan/operation typed 模型，区别 Run PreparedRun |
| `src/application/sources/ports.py` | 新增；repository/授权/稳定读/时钟端口；不直接依赖 Host/SQLite |
| `src/application/sources/scanner.py` | 新增；受授权扫描编排；复用 referenced scanner/reader，不自建任意路径读器 |
| `src/application/sources/matcher.py` | 新增；跨版本匹配与 occurrence 歧义 |
| `src/application/sources/planner.py` | 新增；范围/用户决定/digest/预览 |
| `src/application/sources/service.py` | 新增；入口与依赖编排 |
| `src/application/sources/runtime.py` | 新增；operation 状态、重试、恢复；不建第二个 Run scheduler |
| `src/application/sources/errors.py` | 新增；只投影 PREREQ 已冻结的错误 |
| `src/infrastructure/sqlite/source_sync.py` | 新增候选；plan/journal/批量 CAS/lineage 事务仓储；避免把全部新逻辑堆入 library.py |
| `src/infrastructure/sqlite/schema.py` | 现有；只追加已冻结 v8+；v1–v7 字节保留、旧端拒写 |
| `src/infrastructure/sqlite/library.py` | 现有；共享源/绑定读取、必要批量 seam、管理诊断读取；不动删除/回收/备份段 |
| `src/infrastructure/resource_channel/source_read_refs.py` | 现有；同步后的精确 source/version/entry grant 绑定及恢复；不能回退纯 identity 授权 |
| `src/bootstrap/core_service.py` | 现有；命令集合/dispatch/错误/capability、missing 诊断与 referenced resolve 窄 seam；**共享装配写权须 DSH 明列** |
| `src/bootstrap/core_assembly.py` | 现有；应用/仓储注入与既有 Run source guard 接线；**共享装配写权须 DSH 明列** |

下列只在 DSH 冻结具体设计后逐文件增补，默认只读复用：

- `src/infrastructure/sqlite/migrator.py`：现有 runner 已支持迁移与验证；若新回调/基线确需改动再窄批，不因新版本自动取得整文件写权。
- `src/infrastructure/sqlite/regions.py`、`src/application/editing/drafts.py`、`src/application/editing/ports.py`：S11-005 的 lineage/guard/多区域事务接缝；新映射可放 source_sync.py 时不强制改这些文件。
- `src/application/importing/referenced/model.py`、`scanner.py`、`reader.py`、`runtime.py`、`resolve.py`：此处每个文件的完整前缀均为 `src/application/importing/referenced/`；分别对应公共模型、扫描、预算/解码、旧证据采集、新 binding resolve。只选实现确需改动的文件，FEA-09 导入语义保持冻结。
- `src/infrastructure/resource_channel/source_strict_read.py`、`handle_resolver.py`、`rendition_cache.py`、`render_preview.py`：此处每个文件的完整前缀均为 `src/infrastructure/resource_channel/`；默认复用原生 lease/预算/缓存/不可变资源发布。S11-007 先解决调用方的版本选择，不先放宽底层不可变发布。
- `src/infrastructure/sqlite/pipeline.py`、`src/application/tasks/service.py`：仅生产交错测试证明既有 guard 无法满足时才追加，不重新实现 FEA-10 或修改 provider 语义。

### Host 授权与命令装配候选

以下路径前缀 `apps/desktop-avalonia/src/` 是实际仓库位置；每行都是独立文件。

| 精确路径（相对上述前缀） | 状态、职责与限制 |
|---|---|
| `NewManga.Host/Sources/SourceReadCoordinator.cs` | 现有；fresh grant、能力校验、同步命令映射、撤销/失联纪律 |
| `NewManga.Host/Sources/SourceAccessRegistry.cs` | 现有；只在新增重定位/expected generation 原子操作确需时窄批；保留 DPAPI/锁/重载规范 |
| `NewManga.Host/Sources/SourceOperationCoordinator.cs` | 新增候选；Host 确认/恢复编排；Core journal 为业务真值，Host 不另建 Book/Page 库 |
| `NewManga.Host/HostRuntime.cs` | 现有；生产命令路由、写 Gate、恢复装配；不得放宽 RequireWritesAllowed |
| `NewManga.CoreClient/Commands/HostCommandRegistry.cs` | 现有；Host 命令清单/分类；只注册前置冻结面 |

条件项：`NewManga.CoreClient/CoreServiceClient.cs`（确需 typed 方法/独立超时策略时）；`NewManga.CoreClient/Wire/CoreProtocol.cs`（仅 PREREQ 决定需要新版本常量时）；`NewManga.CoreClient/Commands/HostCommandDispatcher.cs`、`DomainServices.cs`（目前 Source 由 HostRuntime 拦截、SourceReadCoordinator 映射，不应机械给写权）。`SourceSecurity.cs/SourceSecretStore.cs` 默认只读复用，不因实现 journal 重写授权/密码边界。

若 DSH 决定纳入 App adapter，建议新建 `apps/desktop-avalonia/src/NewManga.App/Services/SourceSyncModels.cs` 与独立 `ISourceSyncController`，窄批 `HostController.cs`、`NullHostController.cs` 的接线并分别指定测试；这是条件方案，不在当前卡自动生效。不要扩写冻结 `IHostController.cs`、`RunContracts.cs`；不要把已有 `SourceImportModels.cs` 改成无边界的 Source 总接口。真正 View/VM 的文件须由 ZCode 先勘察冻结，本文不臆造已有同步 UI。

### 测试候选（逐文件）

| 精确路径 | 验证用途 |
|---|---|
| `tests/fea11/conftest.py` | 新增；所有根隔离、源 fixture 只读/指纹基线 |
| `tests/fea11/test_source_scan.py` | 新增；触发/通知丢失/mtime-size 反例/格式预算 |
| `tests/fea11/test_source_match.py` | 新增；可比证据、PDF 插页/ZIP 重排/重复 occurrence |
| `tests/fea11/test_source_plan.py` | 新增；digest/范围/用户决定/stale 全表零写 |
| `tests/fea11/test_source_sync.py` | 新增；CAS/整批 rollback/新代次/共享隔离 |
| `tests/fea11/test_source_relink.py` | 新增；relink/repoint/resync、当前/全部、物理身份 |
| `tests/fea11/test_source_operation.py` | 新增；durable receipt、key 冲突、崩溃点与恢复 |
| `tests/fea11/support/restart_core.py` | 新增；真实新进程恢复 helper，不落 tracked 输出 |
| `tests/fea11/test_v8_migration.py` | 新增候选名，最终随冻结版本改名；回滚/旧端拒写/旧数据守恒 |
| `tests/fea11/test_source_lineage.py` | 新增；区域、draft、在途 Run/candidate 不跨 binding |
| `tests/fea11/test_source_resolve.py` | 新增；missing 诊断、同步后新图、旧资源不可变 |
| `tests/core/test_core_assembly.py` | 现有；生产装配回归，按需窄批 |
| `tests/storage/test_schema_migration.py` | 现有；默认迁移链与 too-new 行为 |
| `tests/storage/test_upgrade_schema_data.py` | 现有；旧库迁移守恒 |
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11SourceIpcTests.cs` | 新增；真实 Host/Core IPC、读取实际字节与共享项目 |
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceOperationTests.cs` | 新增；Host durable/ACK/crash 与恢复矩阵 |
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs` | 现有；授权代 CAS/持锁重载、root 替换/撤销 |
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/HostRuntimeIntegrationTests.cs` | 现有；生产路由/只读 Gate |
| `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/WireTests.cs` | 现有；新命令/旧面兼容，按冻结方案决定 |
| `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/WireLogSourceRedactionTests.cs` | 现有；新增 payload/receipt 无路径/密码/签名材料泄漏 |

FEA-09/10 的现有测试应以**运行**回归为主，默认不取得修改其测试/证据/closeout 的权限。新增 C# helper/fixture 如有需要须先逐文件补清单，不能从上述测试文件推导整个 `Support/**` 的写权。

文档/证据：保留当前 Task、Review、Handoff 与 `verification/FEA-11/**` 的 Task 命名范围；冻结前列出 AC-MATRIX/EV/manifest/日志出口。PREREQ 自有 Task/契约提案/Review/pins 与 DSH 的 STATUS/PLAN/Appointment 更新由各自授权承担，不混进实施者写域。App.axaml/App.axaml.cs/App csproj/sln、删除/回收站/备份/迁移业务、FEA-14/provider 新能力均不在此建议范围。

## AC11-1…10 应补的可观察断言与证据出口（全部 planned）

| AC | 冻结时最少应明确的断言 | 建议出口 |
|---|---|---|
| 1 | 每路触发有调用证据；丢 hint 仍能检测；相同 mtime/size 但字节变可发现；Dirty 阻新写而非直接换绑定；操作前 lease/digest 不被缓存代替 | scan 测试 + 调度/授权日志，EV-AC11-1 |
| 2 | 目录/容器各 diff 分类的数量=明细；plan 绑定 book/页集合/旧新版本/代次/决定；预览和 apply 使用同一不可变 plan | scan/plan 测试，EV-AC11-2 |
| 3 | 精确唯一与重复组分流；profile 不可比/旧证据缺失不自动匹配；ZIP 重复名/重排、PDF 增删页、目录重复内容不合并 occurrence | match 测试及旧库 fixture 指纹，EV-AC11-3 |
| 4 | mapping/范围/决定/版本/代次每一项变化都拒绝；确认前源再变化、并发 apply 失败方均无业务写；精确比较前后 DB 集合 | plan/CAS 负测、DB 快照摘要，EV-AC11-4 |
| 5 | 既有 PageId/顺序/保护/进度守恒；新增独立页；missing tombstone 可找回；新绑定 lineage 隔离；迁移新 revision/来源；最后一项失败整批回滚；新图实际可读 | sync/lineage/resolve、Run/draft 交错，EV-AC11-5 |
| 6 | 三操作不同确认/身份断言；影响项目数/页数明确；当前/全部范围准确；其他项目 accepted binding、人工/进度不误改（诊断状态变化须单列允许字段） | relink 测试 + 真实 IPC，EV-AC11-6 |
| 7 | 无旧原图/无备份仍可从管理诊断入口列出 missing/问题/人工数据；reader typed 失败；不以新源或 derived 文件冒充旧源证据 | missing 诊断/resolve 测试，EV-AC11-7 |
| 8 | 同 key 同请求重放不新增、不同请求拒绝；逐崩溃点 receipt/ACK/读门控恢复；新进程复核 registry generation/OS 事实，不从路径 hint 恢复授权 | operation 测试 + 新进程日志/DB-journal 指纹，EV-AC11-8 |
| 9 | 真实生产装配 Host→Core→DB→resolve→资源字节；源原始 hash/mtime/文件数前后守恒，应用不写源；managed 五读路径/旧命令回归；缺能力/撤销/预算/密码错误 fail-closed | IPC+Python/.NET 分套日志，EV-AC11-9 |
| 10 | 逐项 evidence pin/范围 diff；v1–v7/冻结契约及历史 closeout 字节不变；新迁移失败回滚、旧端拒写；上下文独立 Review 与 DSH 集成；资源核销 | AC-MATRIX/EV/Resource Manifest/check/pins，EV-AC11-10 |

“零写”测试比较应用管理的数据/文件，不把 SQLite WAL/checkpoint 的物理文件字节是否变化误当作业务事务断言；用户源文件字节/mtime 则单独实测。新迁移/plan 的合法预先持久化与 stale Apply 的拒绝基线应分开记录。

## 复用与排除边界

| 已有能力 | 可复用与不可推导 |
|---|---|
| FEA-09 SourceReadService（逻辑称呼） | 实际落点是 SourceReadGrantRegistry、source_strict_read.source_lease、referenced scanner/reader/resolve 与 Host Sources；未找到同名 `SourceReadService` 类，不能把逻辑称呼当已具备同步服务的证据 |
| FEA-09 grant/lease/cache | 复用四维 scope、身份/预算/撤销、同句柄验证与缓存约束；同步后仍须建立新版本精确授权，不把旧 import grant 或 identity 回退当永久授权 |
| FEA-09 import planner/runtime | 只作实现参考；planner 与 receipt 是会话内，提交是每页事务，不可直接替代 durable sync journal/批量 CAS |
| FEA-10 Prepare/Accept | 复用不可变预览、digest、guard 与 candidate-only 原则；C-14 明确源 plan 与 Run PreparedRun 不互相替代，不复用 Run ID/receipt 充当源操作真值 |
| C-13 RegionCandidate | 迁移人工区域需要新 revision 与统一事务/保护检查；不把 Run candidate 与编辑层 RegionCandidate 混为同一种对象 |
| C-04b / FEA-12 | FEA-11 提供可查询的未完成 operation、binding 引用关系；SC-S08 pending-operation 删除披露是后续删除协议承接，不在本 Task 改 DeletePreviewItem/永久删除/回收桥/GC |
| FEA-13/14 | Registry 跨机授权、backup/2、数据根迁移、领域/provider 新能力继续排除；migration v8+ 仅指本 Task 必要的 Schema 升级，不等于获得 FEA-13 数据迁移范围 |

## 实际验证与 NOT_RUN

环境：Windows，`G:/CODEX/New Manga`，`main@811f5d3357598354e11debaad3248a0520d943f5`；执行器 PowerShell，治理脚本以 `pwsh -NoProfile` 运行；未启用 Python venv，未运行 Python/.NET 测试。

| 检查 | 实际命令/方式 | 结果 |
|---|---|---|
| HEAD/分支/common dir/dirty | `git rev-parse HEAD`、`git branch --show-current`、`git rev-parse --git-common-dir`、`git status --short` | PASS；HEAD 如上、main、.git；写报告前无 dirty |
| 文件/实现追溯 | 定向 `rg`/`Get-Content` 上文所列卡片、契约、源码/测试；`Test-Path src/application/sources` 与 `tests/fea11` 均 False | EXECUTED；仅静态范围审查，不标功能 PASS |
| 当前权威指针 | `pwsh -NoProfile -File tools/governance/check.ps1` | PASS，EXIT=0；完整短输出附下 |
| 冻结 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | PASS，EXIT=0；17/17；完整短输出附下 |
| FEA-11 功能/迁移/故障注入/原生 lease/真实 IPC | 未执行；当前无实现，且本次只获报告写权 | NOT_RUN |
| build、pytest/.NET 全量、GUI 可达预览确认 | 未执行；Scope Review 不把历史通过数字冒充本轮验证 | NOT_RUN |
| 本报告之外字节保留 | 报告完成后 `git status --short` / `git diff --stat` 核对 | 见交付核对；不得据此推导运行时数据安全 |

治理检查原始输出（本轮，EXIT=0）：

```text
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\FEA-11.md
WARN: 存在 9 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：5511 bytes / 54 lines
Governance check: PASS (2 warnings)
```

Pin 检查原始输出（本轮，EXIT=0）：

```text
OK C01b 3c9f5af7d74f
OK C02 bb365ca891a7
OK C03 b77e7968a00b
OK C04b 694ce5bc8c8b
OK C05 f6e6f3cb1fe1
OK C06 8faa8cd139f2
OK C07 3fdb44e49afe
OK C08 453f993c1a16
OK C09 dc51226b336c
OK C10 ec8fd862f95f
OK C11 44f4273f7ad1
OK C12 f49835860143
OK C13 8faf1e805eac
OK C14 05056cbf65f9
OK C15 d8c0a3bcfc21
OK C16 0b9511a55ea1
OK FEA01 0370c18932b1
PIN AUDIT: PASS (all 17)
```

## 下一步建议与可转发指令

- **Task / Agent**：DSH 先做 FEA-11 scope 修订与 PREREQ 建卡/冻结，保持 FEA-11 proposed；不是释放实现。前置完成后再安排全新上下文 scope-r2。
- **Recovery point**：`G:/CODEX/New Manga`、main；本轮 base/head 均 `811f5d3357598354e11debaad3248a0520d943f5`。新 worktree 待 DSH 创建，不臆造路径；DSH 接手先核对实时 HEAD/dirty。
- **Scope**：DSH 自有 Task/PLAN/STATUS/Appointment 与新 PREREQ 文档；本报告不修改旧冻结契约/历史证据，不扩大任何生产写权。需要共享 Schema/命令契约变更时先记录授权、独立复核、重冻/新 freeze，再实施。
- **Deliverables / Gate**：S11-001…011 disposition、新 PREREQ 卡与冻结对象、修订的逐文件 allowed_paths/AC/验证矩阵/证据与资源计划；check/pins 通过仍须 scope-r2 无未解决 P0/P1，之后 DSH 才可 Appointment/ready。

> 请 DSH 在 G:/CODEX/New Manga（main）接收 doc/reviews/FEA-11-scope-r1.md；审查基线/head=811f5d3357598354e11debaad3248a0520d943f5，先核对当前 HEAD 与他人未提交内容。保持 FEA-11 proposed，逐项处置 S11-001…011；新增独立 FEA-11 契约 PREREQ（最终 ID 由你登记），冻结 v8+ DDL/plan-operation 状态、wire/错误/能力/兼容、CAS 与跨存储发布边界；补 repoint、可比匹配、lineage/在途 Run-draft、同步后生产读图与缺失诊断 AC，并按报告候选清单逐文件冻结写域、证据和资源目录。修正 PLAN 当前 DAG 错位。此轮只做范围/前置文档与必要契约审查，不自动开始 FEA-11 生产实施，不改历史证据/closeout，不 push。交付固定新 head 与 disposition 后，派全新上下文 Codex 或 ZCode 做 scope-r2；运行 pwsh -NoProfile -File tools/governance/check.ps1 和 verify_pins.ps1，逐项记录 NOT_RUN/skip。新 worktree 待你登记；前置 done、scope approved 及 Appointment 全部满足后再释放 Owner。

## 交付核对

写报告后复核：`git status --short` 仅返回 `?? doc/reviews/FEA-11-scope-r1.md`；`git diff --stat` 无 tracked 变更；`git rev-parse HEAD` 仍为 `811f5d3357598354e11debaad3248a0520d943f5`。再次运行 check.ps1，EXIT=0、PASS（同上 2 warnings）。本报告为唯一新增文件，未提交；审查结论只适用于 frontmatter 的 reviewed_head。
