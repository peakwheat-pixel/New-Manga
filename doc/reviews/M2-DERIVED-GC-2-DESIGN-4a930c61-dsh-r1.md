# M2-DERIVED-GC-2-DESIGN 非作者独立 Review — 结论：**approve_with_conditions**

```yaml
task_id: M2-DERIVED-GC-2-DESIGN
reviewer: DeepSeek Harness（非作者；设计作者=Codex，Reviewer 未参与任何设计或实现）
author: Codex
base_commit: ab4b7c110a7c828f20d2d0787bd71144336d2e44
reviewed_head: 4a930c611c1e7a353f5fe5584932f4cf6d8048c1
delivery_head: 8dd88c56becbb5a5c1942aeb7664c24ce86b9944（设计交付）
decision: approve_with_conditions
conditions: C-1..C-5（见 §9；C-1..C-3 必须在释放 M2-DERIVED-GC-2 前写入设计文本）
```

## 0. 决定摘要

| 项 | 结论 |
|---|---|
| **决定** | **approve_with_conditions**（0×P0 / 0×P1；5×P2/P3 条件；2×P4 advisory） |
| 设计方向 | **成立且最小**：只在"全部受管读者/发布者退出"的启动静默窗口，回收"来源可核验 + 明确退役 + 源 revision 非 current/非 pinned"的 derived preview 副本；未知一律保留。 |
| 架构面 | **PASS**（分层/依赖方向/F-05 边界/零 wire 承诺保持；无 scope creep 到源文件/Managed/模型/Reader） |
| Verification 面 | **设计范围内 PASS（静态）**；本会话命令级复跑 **BLOCKED**（沙箱不可用）；产品/native 租约/回收 **NOT_RUN**（本 Task 零产品改动，不适用于设计缺陷判定） |
| 不可执行项 | 本会话 `pwsh` 在启动阶段即失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`），`danger-full-access` 升级被拒（无审批通道）。未执行任何 git 命令、未重跑任何测试。 |
| 条件性质 | C-1/C-2/C-3 是**设计判据缺失**（必须在设计文本冻结后才可释放后继实现 Task）；C-4/C-5 可在设计文本或后继 Task 的 allowed_paths 中闭合。 |
| 未采信项 | 我**没有**把 G1–G7 的 `NOT_RUN` 当作设计缺陷；G1–G7 是后继 Gate，产品测试缺失不等于设计错误（与用户口径一致）。 |

## 1. 审查方法与能力限制（必须先读）

- 本会话 `pwsh` 不可用：默认 workdir 下即 `SetNamedSecurityInfoW failed (Win32 5)`，一次性 `danger-full-access` 升级返回 `requires approval, but no approval channel is available`。因此**未执行** `git status/rev-parse/merge-base/diff`，**未运行** `check_design.py`、pytest、cargo、双进程租约实验。
- 替代证据（均为独立只读读取，非作者摘要）：
  - `G:\CODEX\New Manga\.git\worktrees\DERIVED-GC-2-DESIGN-review-r1\logs\HEAD` → 本 review worktree 固定在 `4a930c61`（`reset: moving to HEAD`）。
  - `G:\CODEX\New Manga\.git\refs\heads\codex\m2-derived-gc-2-design` → `4a930c611c1e7a353f5fe5584932f4cf6d8048c1`。
  - `G:\CODEX\New Manga\.git\worktrees\DERIVED-GC-2-DESIGN\logs\HEAD` → `69d7cc08 →(a35915c2)→ 8dd88c56 →(4a930c61)`，提交信息分别为 `release M2-DERIVED-GC-2-DESIGN…`、`docs: design conservative reference-safe…`、`docs: repair design verifier and retain failed check attempts`、`docs: pin GC design handoff and request independent review`。
  - `G:\CODEX\New Manga\.git\logs\HEAD:877-879` → main `32f9b932 → ab4b7c11`（rebaseline）→ `69d7cc08`（release）→ `27cc01a1`（checkpoint GC design at independent review boundary）。
  - 逐行阅读 `doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md` 引用的**真实源码**（`render_preview.py`、`catalog_store.py`、`host_bridge.py`、`service.py`、`handle_resolver.py`、`catalog_loader.py`、`core_service.py`、`artifacts.py`、`library.py`、`main.rs`、`core_bridge.rs`、`library_bridge.rs`、`resource_protocol.rs`、`test_sidecar_isolation.py`）。
- 因此：**静态核对设计可审**；所有"未运行"如实标 `NOT_RUN/BLOCKED`，未虚构任何 PASS 或独立批准。

## 2. 固定点与独立核验的事实

| 事实 | 来源（我本人读取） | 判定 |
|---|---|---|
| reviewed_head = `4a930c61` | review worktree reflog + branch ref | **核验成立** |
| base_commit = `ab4b7c11` 是 release `69d7cc08` 的父提交，且 release 在 main 上 | main `.git/logs/HEAD:877-878` | **核验成立** |
| 交付 head `8dd88c56` 与 Handoff 入库 head `4a930c61` 不同 | design worktree reflog:4-5 | **核验成立**（口径见 F-07） |
| `32f9b932..ab4b7c11` 仅治理差量 | 作者 `reality-source.log:18-28`（列出 doc/verification 文件） | 采信作者日志；未独立 diff |
| 工作区干净 | —— | **NOT_RUN**（无 shell） |
| Task 状态：Task 文件 `status: in_review`、Plan 说 `ready`、STATUS 说"唯一 Active" | `doc/tasks/M2-DERIVED-GC-2-DESIGN.md:5`、`REBASELINE_PLAN.md:5`、`STATUS.md:3-5` | 按用户口径：**已知治理延迟，不构成授权冲突**，本报告不计 finding |

## 3. 设计 §1 调用链事实核对（逐条，均命中真实源码）

| 设计主张 | 我核到的源码事实 | 判定 |
|---|---|---|
| 每次重渲染提交 Managed PNG，再复制随机 preview UUID | `application/rendering/service.py:546-608`（`_commit_translated`→`commit_revision`）；`bootstrap/core_service.py:884-919`；`render_preview.py:40-66`（`preview-{uuid4().hex}` + temp/fsync/replace） | **成立** |
| Catalog 仅 `resource_id/scope_class/rel_path`，无 page/revision/退役态 | `catalog_store.py:35-41`（`_SCHEMA` 三列）、`:44-47`（`CatalogEntry`） | **成立** |
| Rust 单锁包住 rerender→revoke→map swap，map 仅进程内 | `main.rs:332-350`（持锁 call rerender 后 `rotate_render_preview`）、`:397-439`（revoke previous → swap）、`:174,775`（`Mutex<HashMap>` 进程内） | **成立** |
| Core 生产与 channel 是两个 sidecar | `main.rs:711-722`（channel=`StdioCoreChannel`）、`:746-767`（production Core=`StdioLibraryChannel`）；`host_bridge.py:46-72,167-201` | **成立** |
| **当前启动 channel 先于 production Core** | `main.rs:711` vs `:746`（顺序确认） | **成立**（F-03 的前提） |
| Grant 在每个 ResourceChannelService 内存表，重启失效 | `service.py:11-15`（内存表 docstring）、`:77`、`:143-148`、`:253-257`、`:288-295` | **成立** |
| current/pinned 是主产品 artifact revision 指针与标志 | `sqlite/artifacts.py:81-99`（`get_artifact`）、`:101-115`（`get_current_revision`/`list_revisions`）、`artifacts.py:257-259`（UPDATE current）、`ports/repositories/artifacts.py:54-67`（`is_pinned`） | **成立** |
| 旧 collector 只处理 orphan/dead row | `render_preview.py:106-163`、`core_service.py:1703-1720` | **成立** |
| 每次 HTTP 读取 fresh resolve，已打开句柄不中断；Windows 只 `FILE_SHARE_READ` | `resource_protocol.rs:533-555`（每请求 `channel.resolve`）、`:308-329`（`CreateFileW(..., FILE_SHARE_READ, ...)`）、`M2-C1_TYPED_IPC_CONTRACT.md:386`（T6 "already-opened handle/stream … not forcibly interrupted"） | **成立** |
| `publish()` 的生产调用点仅 `handle_rerender_page` | 全仓 grep：`publish(` 生产调用仅 `core_service.py:916`；`publish_original` 另在 `:1037` | **成立**（且设计已声明不扩张 `pages/`） |

**结论：AC1 的调用链取证方向与文件/行证据真实、可复核。** 缺口是设计未把 `catalog_loader.py`（第三个 catalog 写入入口）与 `library_bridge.rs`（production Core 的 spawn/就绪面）纳入调用链（见 F-02/F-03）。

## 4. 专项核对（用户点名项，逐项给判定）

| # | 核对项 | 判定 | 依据与缺口 |
|---|---|---|---|
| 1 | 双 sidecar grant 局部性 | **成立** | grant 表只在 channel 进程内存（`service.py:77,143`）；product Core 无 grant 可见性；设计 §1:13 结论正确。 |
| 2 | published managed source binding | **方向成立，判据待冻结** | 拟议 `preview_lifecycle`（§2.1:30-40）绑定 producer_root + artifact/revision + managed_rel_path + retired；但 `revision_no` 反查"唯一行"不成立（F-04）。 |
| 3 | current/pinned 保护 | **成立** | §2.4:66（重新读 artifact/current/`list_revisions`，匹配 `artifact_revision_id`+`managed_rel_path`+TRANSLATED；current 或 `is_pinned=True` 必留）；K2:96。 |
| 4 | retirement marker 不是无引用证明 | **成立** | §2.2:50 明文"retired=1 表示曾被显式退役，**不表示现在无活跃消费者**"；K1/K3/U3 与 §2.3 独占窗口配套。 |
| 5 | Windows 共享/独占 namespace lifetime lease 与 core-first 启动 | **方向成立，两处判据缺失** | 内核文件锁 + OS 崩溃释放 + 非阻塞独占 + 拿不到即跳过（§2.3:54-58）合理；缺 (a) lease 与 derived-root 的绑定判据（F-02）；(b) Core→channel 就绪信号与租约获取点（F-03）。 |
| 6 | 混合旧 runtime UNKNOWN 不删 | **成立** | U3:103 + §2.3:60 + 上线 Gate:62（不能证明则 fail-soft skipped、标 BLOCKED）。**我明确不建议移除这一保守性**：它与仓库已记录的 TOCTOU/句柄核验标准（M2-S1 S1-B11、M2-S2 分层）一致，属必要保护而非过度工程。 |
| 7 | 全部 reader/producer 参与 | **部分成立** | 未加入租约的 Rust host 作为 route-A 读者由 `FILE_SHARE_READ` + 句柄/分享冲突保护（§1:16、§2.4:72）——可接受；但**参与方清单与"未加入租约"的可检测信号未冻结**（F-02）。 |
| 8 | 已有 orphan 扫描也须 lease | **成立** | §2:22 明文要求第一刀同受窗口保护、"不能把其现有启动扫描放在保护窗口外"；G3:132 含"包括现有 orphan 扫描"。 |
| 9 | 目录/文件 TOCTOU 按核验句柄删除 | **成立，落点待定** | §2.4:70 拒绝 `resolve()+unlink`、要求对核验句柄做 native delete disposition；现有 `handle_resolver.py:104-156` 提供 identity/final-path 能力，但删除 helper 不在 §5 allowed_paths（F-05）。 |
| 10 | 在途句柄保护 | **成立** | K4:98 + §2.4:72（不改 `FILE_SHARE_READ`、不加强制、不加 `FILE_SHARE_DELETE`；删除失败即保留）。 |
| 11 | 三数据库/文件失败恢复 | **基本成立，mark 路径有洞** | §3:76-87 八行中断矩阵覆盖 Managed commit / publish / catalog 事务 / unlink / mark / 删除后事务失败；"不跨数据库伪造原子提交"正确。缺口：mark 的 DB 失败映射（F-01）。 |
| 12 | 失败不能更改 RC4 wire | **成立** | §2.2:46（不删字节、不撤销额外 grant、不改 resolve/issue/touch；失败返回既有 typed refusal、不加新 WebView 错误面）；§5:122（不变 CatalogEntry/issue/T6/TTL/公共语义）。 |
| 13 | F-05 import 隔离 | **方向成立，需显式授权** | §5:116（host_bridge "只追加内部 mark_preview_retired，不导入产品 domain/SQLite adapters"）、:113（租约 helper 用 stdlib/ctypes，同模块）。但 channel 由 catalog **只读**变为**写者**，属新授权面（F-01）；新增模块需同步白名单（F-05，`test_sidecar_isolation.py:85-96` 是精确名单）。 |
| 14 | 最小性 | **成立** | 不新建通用 GC 框架/后台调度/引用计数/Reader 功能；候选被 §2.4:70 收窄到 `derived-read-only` + 已登记 + `retired=1` + `previews/<完整 id>.png`，天然排除 `pages/`（`publish_original` 用 `page-original-<page_id>` 键）。 |

**"设计不可实现 / 授权范围未冻结"总答**：整体**可实现**（Python stdlib `ctypes` 内核锁 + 专用 SQLite 辅助表 + Rust 启动顺序调整）。但有三处必须在设计文本冻结后才可释放实现：F-01（标记写入权威与失败映射）、F-02（租约命名空间绑定与参与方判据）、F-03（Core 就绪信号与租约获取点）；另有 F-04/F-05 两处 allowed_paths/判据精度问题。

## 5. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 修订要求 | 状态 |
|---|---|---|---|---|---|---|
| **F-01** | **P2** | 设计 `M2_DERIVED_PREVIEW_GC_DESIGN.md:30`（"新增**仅由 Core 写入**的 `preview_lifecycle`"）vs `:46`（trusted host→**channel** 的 `mark_preview_retired`）；`src/infrastructure/resource_channel/host_bridge.py:132-141`、`:145-160`；`src/infrastructure/resource_channel/catalog_store.py:53-58`；`apps/desktop/src-tauri/src/main.rs:332-350,397-439` | 触发：产品 Core 正在写 catalog（发布/`upsert`）时，Rust 在 rerender 成功路径请求 channel 标记 retired。影响：①写入权威自相矛盾（"仅由 Core" vs channel 写），直接决定后继 Task 是否授权隔离 sidecar 获得 catalog 写权限；②`catalog_store` 用 `sqlite3.connect`（默认 5s busy、无 typed 包装），`sqlite3.OperationalError("database is locked")` **不在** `_dispatch` 的捕获集合（只捕 `TypedResourceChannelError` 与 `(KeyError, TypeError, ValueError)`），且 `serve_forever` 无 try → 异常逃出 → **整个 channel 进程退出**，与设计 §2.2:48"mark 失败仅漏回收…不改已有成功 rerender/new preview 语义"直接冲突（全部在途 grant 一起失效）；③mark 在 `render_preview_resources` 互斥锁内同步执行，无延迟上界。 | 设计自述矛盾（`M2_DERIVED_PREVIEW_GC_DESIGN.md:30` vs `:46`）；`host_bridge.py:136-139` 捕获集合；`catalog_store.py:55-58` 无 busy/typed 处理；`main.rs:339-349` 持锁调用链 | ①在 §2.1/§2.2 明确 `preview_lifecycle` 的**唯一写入者与写入路径**，并显式把"channel 获得 catalog 写权限"列为后继 Task 的共享变更授权项（或改由 product Core 写入）；②冻结失败映射：mark 必须把 `sqlite3.Error`/OS 错误转成非致命结果（no-op + 诊断），**任何异常不得逃出 `CoreChannelServer._dispatch`**；③给出 mark 的有界超时/重试口径，并写出"mark 失败不影响已成功 rerender 响应"的判别断言（G2 补行）。 | open |
| **F-02** | **P2** | 设计 `:54`（"锚定规范化 **catalog 路径**的专用 lock 文件"）、`:60`（"所有参与者验证相同 catalog/**derived** 根绑定"）、`:103`（U3"混合数据根/入口未加入租约→UNKNOWN→禁用 sweep"）、`:132`（G3"所有支持入口覆盖"）；`src/bootstrap/core_service.py:1683-1689`；`src/infrastructure/resource_channel/catalog_loader.py:64-79`；`apps/desktop/src-tauri/src/main.rs:664-697`；`render_preview.py:150-155` | 触发：同一 derived root + 不同 catalog DB（或反之）的实例/入口并存；或 `catalog_loader` / probe / ac1 / 测试构造入口启动 channel 时生产 Core 取得独占租约。影响：单一 catalog 旁 lock 文件**无法让参与者发现 derived 根不一致**；设计把"混合数据根/未加入租约入口"判为 UNKNOWN→禁用 sweep，却**未定义检测信号**，因此"共享租约为零"不能作为"此刻无其他读者/写者"的证明。现有 orphan 文件扫描按目录删除（`render_preview.py:150-155`），在"共享 derived root、不同 catalog"下会删掉另一 catalog 登记的活文件。 | `core_service.py:1683-1689` 两个 env 独立；`main.rs:664-697` packaged 同根 / dev 独立 env；`catalog_loader.py:79` 第三个 `ResourceCatalogStore`；`test_sidecar_isolation.py:98-106` 证明 loader 是受支持入口 | ①冻结 lease 身份内容（至少：规范化 derived root + catalog 标识 + 版本），并冻结不一致时的动作（判 UNKNOWN → live-preview sweep **与** orphan 扫描**都跳过**）；或把租约锚定在删除域（derived root）并同时校验 catalog；②逐一点名参与方清单（production Core、resource channel、`catalog_loader`、probe/ac1、测试构造入口）及其"未加入租约"的**可检测信号**，不得仅以"支持该协议的进程"泛化；③把该判据写成 G3/G7 的判据而不是散文。 | open |
| **F-03** | **P2** | 设计 `:58`（"必须调整**生产路径**为 production Core 启动/**握手完成 GC** 后再启动 channel"）、`:118`（§5 allowed_paths 只列 `core_bridge.rs`/`main.rs`）；`apps/desktop/src-tauri/src/main.rs:711-722,746-767`；`apps/desktop/src-tauri/src/library_bridge.rs:207-260`（spawn 无就绪信号）、`:356-357`（`ping()`→`core.ping`）；`src/bootstrap/core_service.py:1688-1697`（`serve_forever` 在 `_run_startup_gc` 之后才开始应答） | 触发：按 §5 在 `main.rs` 把 library 提前到 channel 之前；若不等待 Core 完成"独占→共享"降级，channel 的共享租约获取失败 → 按设计 fail-closed → Rust `.expect("python core sidecar failed to start")` → **应用启动崩溃**。另：`assemble_production_core`/`ResourceCatalogStore.__init__`（执行 `CREATE TABLE …` DDL 写）在现状装配顺序中都早于任何租约，与"访问 catalog/文件前取得共享租约"的字面要求不一致。影响：设计强制了顺序但未冻结就绪信号；实现者若为此新增握手会越过 allowed_paths（`library_bridge.rs` 未授权），若并行 spawn 则产生启动竞态 → **设计不可实现/授权未冻结**。 | `main.rs:711`（channel）先于 `:746`（Core）；`library_bridge.rs:241-259` 只 spawn 不握手；`main.rs:204` 显示 `ping` 仅由 Tauri 命令触发；`core_service.py:1692`→`:1697` 顺序 | ①在 §2.3/§5 **指名既有 `core.ping`**（`LibraryChannel::ping`，`library_bridge.rs:356`；Core 在 `_run_startup_gc` 完成后才应答）作为就绪信号，并确认**无需修改 `library_bridge.rs`**；②冻结 ping 失败/超时的行为（不启动 channel、不启用 GC、不绕过保护）；③冻结租约获取点相对 `assemble_production_core` / `ResourceCatalogStore.__init__` / `_run_startup_gc` 的顺序；若确需改 `library_bridge.rs`，必须在后继 Task 增列该路径。 | open |
| **F-04** | **P3** | 设计 `:36`（"Core 复用 `list_revisions(artifact_id)` 从 `outcome.revision_no` 找到**唯一行**"）；`src/infrastructure/sqlite/artifacts.py:217-222`；`src/infrastructure/sqlite/library.py:576-580`；`src/application/rendering/service.py:582-591` | 触发：同 artifact 在 page purge 后重新提交。`revision_no` 由 `MAX(revision_no)+1`（per-artifact）产生，而 `purge_pages` 会 `DELETE FROM artifact_revisions WHERE artifact_id IN (...)` → **revision_no 可被复用**，不具全时唯一性。影响：设计把"唯一行"当作既成事实，后继实现可能据此省略校验；若绑定到同 artifact 的另一 revision，GC 会以错误 revision 判 current/pinned（理论上的过度回收路径）。当前实际风险极低（Core 是串行 `serve_forever`，`core_service.py:1663-1673`，提交与反查同请求内），但判据本身不成立。 | `artifacts.py:217-222`；`library.py:576-580`；`RenderOutcome` 只回 `revision_no`/`managed_path`（`rendering/service.py:584-591`） | 冻结绑定必须**附加校验 `managed_path` 与本次提交逐字一致**（或由实现 Task 明确 `RenderOutcome` 增补 `artifact_revision_id` 是否在授权内，注意 `src/application/rendering/service.py` 不在 §5 allowed_paths）；在 §2.1 写明 revision_no 非全时唯一的理由与消解手段。 | open |
| **F-05** | **P3** | 设计 `:70`（"复用现有 Win32 句柄事实/identity/最终路径核验思路"）、`:113`（helper 只点名 `catalog_store.py`）；`src/infrastructure/resource_channel/handle_resolver.py:104-156`；`tests/m2_resource_channel/test_sidecar_isolation.py:85-96` | 触发：实现 GC 的"核验句柄 + native delete disposition"。现有 Win32 identity/final-path helper 在 `handle_resolver.py`（`_open_read_handle` 只请求 `GENERIC_READ` + 窄分享）。影响：该文件**不在 §5 allowed_paths**；实现者若在 `catalog_store.py` 另写一套 Win32 代码，与"复用"和最小性冲突；若新增模块，需同步精确白名单测试（该测试在 allowed_paths 内）。 | `handle_resolver.py:104-122`（只读句柄）、`:125-156`（identity/final path）；`test_sidecar_isolation.py:84-96`（精确模块名单） | 在 §5 二选一并写明：把 `src/infrastructure/resource_channel/handle_resolver.py` 列入 allowed_paths；**或**明确删除 helper 在 `catalog_store.py`/`render_preview.py` 内新增且不改 `handle_resolver.py`。同时说明 DELETE 访问/分享模式与现有读取 `FILE_SHARE_READ` 的兼容判据。 | open |
| **F-06** | **P4** | 设计 `:26`、`:48`（"不知 previous…均不标记可回收"）、`:84`；`apps/desktop/src-tauri/src/main.rs:775` | 影响：重启后 `render_preview_resources` 为空 → 新会话 rerender 的 `previous=None` → **上一会话每页最后一个 preview 的 retired 永远为 0，永不回收**；GC 实际只能回收"上一会话内发生过轮换"的键。残余增长应按 `pages × 应用运行次数` 陈述。设计已声明不承诺磁盘有界，但未点明该机制，后继验收/指标容易误期待收敛。 | `main.rs:775`（map 每次启动为空）；设计 `:48` 自身规则 | 在设计/后继 Task 明确该构造性上限与可测量口径（例："每页每应用运行至多保留 1 个不可回收副本"），避免声称"轮换子集全部回收"。 | open |
| **F-07** | **P4** | `verification/M2-DERIVED-GC-2-DESIGN/design-check.log:5-6,26-27`；`doc/handoffs/M2-DERIVED-GC-2-DESIGN-codex-8dd88c56.md:6,14`；`doc/tasks/M2-DERIVED-GC-2-DESIGN.md:67` | 影响：`design-check.log` 绑定 `HEAD=8dd88c56`，其中 `git ls-files --others` 显示 Handoff **当时未跟踪**；即交付 head `8dd88c56` 本身不含 Handoff，Handoff 到 `reviewed_head=4a930c61` 才入库（branch reflog:5）。Task/Handoff 的"固定交付=8dd88c56 + Handoff"只在 `4a930c61` 成立。属记录口径，不影响安全性。 | design worktree reflog:3-5；`design-check.log:26-27` | 在 Task/Handoff 记录"设计交付 head"与"Handoff 入库 head"的从属关系（沿 M2-CATEGORY-CLARIFY-1 N-01 先例），避免复审者按 `8dd88c56` 找 Handoff 落空。 | open |

**非 findings 的观察（不占 finding 位）**

- **O-01**：§4 矩阵 K5 写"Managed/source/人工文件"，未显式写 AC2 点名的 **Lock**；该判据已存在于 §6 G1:130（"…人工/Lock相关主产品行不写"）与 §2.4:68（"仅 SELECT，不改产品行"）。建议后续措辞收敛时在矩阵补一行，使 AC2 的三个词各有矩阵锚点。**不构成本轮阻断。**
- **O-02**：设计把"Windows namespace 租约 helper"放进 `catalog_store.py`（§5:113）。功能上可行（stdlib/ctypes、不破坏 F-05），但语义上 catalog 存储模块承载进程生命周期锁略偏。若实现中出现分层不适，建议在 §5 允许范围内选择 `handle_resolver.py`（见 F-05），无需新增框架。
- **O-03**：`M2-C1_TYPED_IPC_CONTRACT.md` 被 §5:120 列为"窄注记"后继改动，但该文件不在**本** Task 的允许修改范围（`:38`）；后继 Task 必须显式授权，本设计未越权（正确）。

## 6. 逐 AC 判定

| AC | 判定 | 依据 | 残留 |
|---|---|---|---|
| **AC1** 固定 HEAD 下追踪 publisher/catalog、render current/pinned、Core/Rust 独立进程、grant/轮换/读取调用链，给文件/行证据 | **PASS**（executed=静态逐行） | §1:9-16 七行事实全部命中真实源码（§3 表）；引用行界均有效 | 设计未点名 `catalog_loader.py`（第三 catalog 写入口）与 `library_bridge.rs`（Core spawn/就绪面）→ F-02/F-03 |
| **AC2** 可删/必留/未知矩阵；仅 TTL/年龄/数量不足以授权删除；Managed/源文件/人工修改/Lock 与 current/pinned 受保护 | **PASS** | §4:93-105（D1/D2/K1-K6/U1-U5 共 13 行）；§24 明文不用 TTL/时间/数量/目录名/`revoke_count=0`；K2/K5 + §2.4:66-68 + §5:122 | O-01（矩阵未显式写 Lock，G1 已覆盖）；F-04（current/pinned 判定所依赖的 source 绑定判据） |
| **AC3** 最小生命周期方案明确 issue/delete 互斥、在途读取、崩溃恢复、未知历史资源保留、目录/文件逃逸；共享 seam/Schema 需明确后继授权，不改现行契约 | **PASS**（带条件） | §2.2:44-50（退役触发与失败）、§2.4:64-72（current/pinned/路径/句柄）、§3:76-87（八行崩溃矩阵）、§5:122（仅专用辅助表 + 内部 lifecycle 方法） | F-01（mark 失败映射）、F-02（静默窗口绑定/参与方判据）；两者须在释放实现前冻结 |
| **AC4** 拟定后继实现 Task 的 base/分支/worktree/allowed_paths/交付/验证 Gate 与可转发指令；本轮只准备不启动 | **PASS（带限制）** | §5:109-124（allowed_paths + 共享变更边界）、§6:126-144（G1–G7 + 建议命令）、Handoff:32-46（可转发指令） | 实际 base/branch/worktree 明确延迟到设计集成后由 Codex 填（符合"本轮只准备"），未伪造未来路径（正确）；但 §5 allowed_paths 缺 `handle_resolver.py` 与潜在 `library_bridge.rs` → F-05/F-03 |
| **AC5** 设计范围 diff 对 src/apps/tests/依赖/Schema 为零；文档检查有命令+HEAD+EXIT；非作者 DSH 固定 head 审查、条件闭合、Codex 集成后才 done | **PARTIAL（未闭合）** | 零产品 delta：作者 `design-check.log:16-25,29`（EXIT=0）+ 我静态交叉核验"设计引用的行号在 4a930c61 工作树全部命中且语义一致"；失败尝试 `design-check-attempt1.log:27-32`、`attempt2.log:28-33` 如实保留；固定 head 审查=本报告 | 命令级复跑 **BLOCKED**（本会话）；"条件闭合"与"Codex 集成后 done"尚未发生 → AC5 的流程后半仍开 |

## 7. Architecture / Verification 两面结论

**Architecture — PASS。** 分层与依赖方向未被破坏：设计只提出内部 seam（专用 catalog 辅助表 + trusted channel 内部方法 + Rust 启动顺序），明确禁止改主产品 schema/migration/`ArtifactRepositoryPort`/`ResourceChannelService` 公共语义/读取 share flags/React/依赖/packaging/Legacy/用户文件（§5:122）。零新增 WebView wire/ACL/Tauri 命令。持久化边界正确：catalog DB 单事务写 catalog+来源、产品 DB **仅 SELECT**、不跨库伪造原子提交（§3:76）。安全边界符合仓库已记录标准（M2-S1 S1-B11、M2-S2 句柄核验分层）：删除以核验句柄的 delete disposition 为准，不以 `resolve()+unlink` 作为证明（§2.4:70）。**未发现过度工程**：不新建 GC 框架/后台调度/引用计数/在线租约；对未知来源与混合旧 runtime 的保守保留是必要的 fail-safe，**我明确不建议移除**。

**Verification — 设计范围内 PASS（静态）；命令级 BLOCKED。** 我独立核对的是设计所引用的**真实源码事实**与设计内部一致性，不是作者的自述数字。产品实现、native 双进程租约、实际回收均 **NOT_RUN**，且按用户口径**不作为设计缺陷**。作者证据本身符合 Q-009 纪律（`design-check.log` 带 SHELL/PYTHON/COMMAND/HEAD/EXIT；两次失败尝试原样保留、未抹除，未声称产品失败/通过）。

## 8. 验证表（我本人执行能力，如实）

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| Git 基线/清洁度/祖先/范围 | `git status`/`rev-parse`/`merge-base`/`diff` | review worktree | **BLOCKED**（`pwsh` 启动即 `SetNamedSecurityInfoW Win32 5`；`danger-full-access` 升级无审批通道） | 替代：`.git/worktrees/DERIVED-GC-2-DESIGN-review-r1/logs/HEAD`（HEAD=`4a930c61`）；`.git/refs/heads/codex/m2-derived-gc-2-design`；`.git/worktrees/DERIVED-GC-2-DESIGN/logs/HEAD`；`.git/logs/HEAD:877-879` |
| 设计矩阵/Gate/链接完整性 | `python verification/M2-DERIVED-GC-2-DESIGN/check_design.py` | 作者 @`8dd88c56` | 作者日志 **EXIT=0 / PASS**；我的复跑 **NOT_RUN**（shell 不可用） | `design-check.log:29-31`；我另行静态核对其断言对象（13 矩阵行、G1–G7、8 处 `src|apps` 引用全部命中真实文件与行界） |
| 真实调用链静态核对 | 逐行 `read`/`grep` | 工作树 @`4a930c61` | **executed** | §3 表（`render_preview.py`、`catalog_store.py`、`host_bridge.py`、`service.py`、`handle_resolver.py`、`catalog_loader.py`、`core_service.py`、`artifacts.py`、`library.py`、`main.rs`、`core_bridge.rs`、`library_bridge.rs`、`resource_protocol.rs`、`test_sidecar_isolation.py`） |
| 产品回归 / native 双进程租约 / 实际回收 | pytest / cargo / 双进程 lease / 真实删除 | —— | **NOT_RUN**（本 Task 零产品改动；G1–G7 属后继 Gate，不作为设计缺陷） | 设计要求本身：`M2_DERIVED_PREVIEW_GC_DESIGN.md:126-144` |
| 审查派发可见性 | DSH CLI/Web 会话 | 本会话 | 非 CLI 派发（由用户在本 review worktree 内直接派发）→ Web 可见性判断 **N/A** | —— |

## 9. 条件清单与复审口径

**C-1（阻断释放 M2-DERIVED-GC-2 的条件，源自 F-01）**：在 §2.1/§2.2 冻结 `preview_lifecycle` 的唯一写入者与写入路径；显式把"resource channel 获得 catalog 写权限"登记为后继 Task 的共享变更授权项（或改由 product Core 写入）；冻结 mark 的失败映射——**任何 `sqlite3.Error`/OS 错误不得逃出 `CoreChannelServer._dispatch`**，mark 失败必须非致命且不影响已成功的 rerender/new preview 响应；给出 mark 的有界延迟口径。

**C-2（阻断释放，源自 F-02）**：冻结 lease 身份内容（规范化 derived root + catalog 标识）与不一致时的动作（UNKNOWN → live-preview sweep 与现有 orphan 扫描都跳过），或把租约锚定在 derived root 并同时校验 catalog；逐一点名参与方清单（production Core、resource channel、`catalog_loader`、probe/ac1、测试构造入口）及其"未加入租约"的可检测信号。

**C-3（阻断释放，源自 F-03）**：指名既有 `core.ping` 作为 Core 就绪信号，确认无需修改 `library_bridge.rs`（否则增列 allowed_paths）；冻结 ping 失败/超时行为；冻结租约获取点相对 `assemble_production_core` / `ResourceCatalogStore.__init__` / `_run_startup_gc` 的顺序。

**C-4（源自 F-04）**：冻结 source 绑定必须附加 `managed_path` 与本次提交逐字一致的校验；说明 `revision_no` 非全时唯一（`library.py:576-580`）及消解手段。

**C-5（源自 F-05）**：在 §5 明确核验句柄删除 helper 的落点——把 `handle_resolver.py` 列入 allowed_paths，或明确不改该文件并在 allowed 模块内新增。

**非阻断项**（可在同一次设计文本修订或后继 Task 内闭合）：F-06（残余增长口径）、F-07（交付/ Handoff head 从属关系）、O-01/O-02/O-03。

**复审口径**：条件 C-1..C-3 必须在设计文本落地后由非作者在**新的 reviewed_head** 上做限定复核（只覆盖新 head 与本表 disposition，不抹掉本记录）；C-4/C-5 可在设计文本或 M2-DERIVED-GC-2 的正式 Task 文件中冻结，并在该 Task 的 Review 中检查。**本批准只对 `4a930c611c1e7a353f5fe5584932f4cf6d8048c1` 有效**；分支后续变化不延用。按协议 §6.8，本报告无未解决 P0/P1，故不阻断"设计可行"的判断；但因存在 5 条 P2/P3 安全判据缺失，**不建议在条件闭合前释放 M2-DERIVED-GC-2（实现）**。

## 10. 结论与推荐下一步

**结论**：`approve_with_conditions`。设计的**方向、边界与最小性均成立**（起点/终点、可删/必留/未知矩阵、current/pinned、句柄核验式删除、失败 fail-soft 均与仓库既有标准一致，且明确拒绝 TTL/年龄/数量/文件名推断）；双 sidecar grant 局部性、marker 非无引用证明、混合旧 runtime 不删、已有 orphan 扫描纳入窗口、目录/文件按核验句柄删除、三库失败恢复、不改 RC4 wire 等关键点均已在设计中正确处理。需要闭合的是**判据冻结**，不是架构返工：F-01（标记写入权威与失败映射）、F-02（租约命名空间绑定与参与方判据）、F-03（Core 就绪信号与租约获取点）必须在设计文本落地。

**推荐下一步（可直接转发）**：

```text
Codex：处理 DSH 非作者 Review（reviewed_head=4a930c611c1e7a353f5fe5584932f4cf6d8048c1，决定 approve_with_conditions，0×P0/0×P1、5×P2/P3）。
在 worktree `G:/CODEX/New Manga.worktrees/DERIVED-GC-2-DESIGN`（branch `codex/m2-derived-gc-2-design`）按条件修改设计文本：
① C-1：在 doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md §2.1/§2.2 冻结 preview_lifecycle 的唯一写入者与写入路径（并登记"channel 获得 catalog 写权限"为后继 Task 授权项），冻结 mark 失败映射（sqlite3.Error/OS 错误不得逃出 CoreChannelServer._dispatch，mark 失败非致命）与有界延迟口径；
② C-2：冻结 lease 身份内容（规范化 derived root + catalog 标识）与不一致动作（UNKNOWN→live-preview sweep 与现有 orphan 扫描都跳过），并逐一点名参与方（production Core、resource channel、catalog_loader、probe/ac1、测试构造入口）及"未加入租约"的可检测信号；
③ C-3：指名既有 core.ping（LibraryChannel::ping；Core 在 _run_startup_gc 后才应答）作为 Core 就绪信号，确认无需改 library_bridge.rs（否则增列 allowed_paths），冻结 ping 失败/超时行为与租约获取点相对 assemble_production_core/ResourceCatalogStore.__init__/_run_startup_gc 的顺序；
④ C-4：冻结 source 绑定附加 managed_path 逐字校验（revision_no 非全时唯一，library.py:576-580）；C-5：在 §5 明确核验句柄删除 helper 落点（handle_resolver.py 列为 allowed_paths，或明确不改该文件）；
⑤ 顺手闭合 F-06/F-07 与 O-01（残余增长口径、交付 head 与 Handoff 入库 head 从属关系、矩阵补 Lock 行）。
不修改任何 src/apps/tests/Schema/wire/依赖；提交后给出新的设计 delivery head 与 Handoff，交 DSH 在固定新 head 上做限定复核（仅覆盖 C-1..C-5 + disposition）。条件闭合前不释放 M2-DERIVED-GC-2。
```

---

Reviewer：DeepSeek Harness（**非作者**）｜base_commit `ab4b7c11`｜reviewed_head `4a930c61`（本 review worktree 独立核验：worktree reflog + branch ref）｜delivery_head `8dd88c56`｜决定 **approve_with_conditions**｜findings 0×P0 / 0×P1 / 3×P2 / 2×P3 / 2×P4｜命令级复跑 **BLOCKED**（`SetNamedSecurityInfoW Win32 5`，无审批通道），产品/native/回收 **NOT_RUN**（不冒充设计缺陷）｜本报告未修改任何文件，未实施、未合并、未删除任何历史 worktree。