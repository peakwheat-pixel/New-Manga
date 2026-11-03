---
id: FEA-09
title: 引用源与导入（Core source schema/read/cache、Host SourceAccessRegistry/授权、导入 plan/receipt）
kind: implementation
governance_version: 3
status: done
approval: scope-r1 changes_requested 已处置；**scope-r2 approved**（P0=0/P1=0/P2=2；doc/reviews/FEA-09-scope-r2.md，SHA-256 `3fd18cbc32baecbcb9c8686a634f9cf0d6a1802ff94bc9e4b070bffd5003e6b2`）；前置 FEA-09-PREREQ-1 **done**（C-05/C-06 v1.1 + C-15/C-16 v1.0 冻结、17/17）
suggested_owner: codex
owner: codex（DSH 2026-11-03 额度恢复后续跑）
claimed_at: 2026-11-03T09:59:49.695Z（Codex 首认领，git add 因 .git/index.lock Permission denied 未提交，遗留 diff 保留为证据）；2026-11-03 18:00 故障转移 ZCode 接续；18:39 ZCode 额度耗尽（429 周/月限额，2026-11-07 16:44 重置）；Phase A 已交付 commit `d3d7cd564`；2026-11-03 Codex 本轮通过 Node 通路恢复，接续 ZCode Phase A/B 及 Phase C 半成品
reviewer: 实现 Review r1 changes_requested（P0=0/P1=8/P2=3，doc/reviews/FEA-09-impl-r1.md）；返修后 **r1-rework changes_requested（P0=0/P1=1/P2=4，doc/reviews/FEA-09-impl-r1-rework-r1.md，ZCode sess_b421a1f9…，reviewed_head 59ad0b9fe）**；P1（PDF resolve 密码）与 P2-1/2/3 已修，待新上下文最终复核；P2-4（RenditionCache 装配失败降级 legacy）已登记债务（见文末「债务候选」）；最终复核 r2 approved（doc/reviews/FEA-09-impl-r1-rework-r2.md，ZCode sess_8fd2ec28…，P0=0/P1=0/P2=2）
depends_on:
  - FEA-08
  - FEA-01-FREEZE-1
  - FEA-09-PREREQ-1
base_commit: 19e6210047e664d1206347bd5259a6f075a9c028（scope-r2 reviewed_head；实施从 main 当前 head 起）
branch: main
worktree: G:\CODEX\New Manga
integration_commit: 87ca50702e00c62c64540ac7ac4ff3b1d27fa0cd # 集成验证 head（closeout 文档提交在其后）
delivery_head: 87ca50702e00c62c64540ac7ac4ff3b1d27fa0cd # 最终交付 head（返修+复核 approved）
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-09
allowed_paths:
  - doc/tasks/FEA-09.md
  - doc/handoffs/FEA-09-*.md
  - doc/reviews/FEA-09-*.md
  - verification/FEA-09/**
  - src/application/importing/referenced/**
  - src/application/importing/images/**
  - src/application/importing/documents/**
  - src/application/resource_channel/**
  - src/infrastructure/resource_channel/**
  - src/infrastructure/importing.py
  - src/domain/pages/entities.py
  - src/bootstrap/core_assembly.py
  - src/bootstrap/core_service.py
  - src/infrastructure/sqlite/schema.py
  - src/infrastructure/sqlite/migrator.py
  - src/infrastructure/sqlite/library.py
  - apps/desktop-avalonia/src/NewManga.Host/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/Issuer/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Wire/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/Transport/WireLog.cs
  - tests/import_formats/**
  - tests/library/test_import_images.py
  - tests/library/test_import_sources.py
  - tests/library/test_sqlite_library.py
  - tests/core/test_p09_fu2_import_pages.py
  - tests/core/test_page_resource_resolve.py
  - tests/core/test_core_service.py（DSH 2026-11-03 扩域：C-16 新增能力 `source.read/1` 使 `core.ping.capabilities` 断言与 E2E 探针必须同步；属冻结协议行为，测试滞后）
  - tests/core/test_bootstrap.py（DSH 2026-11-03 扩域：C-15 要求 `MigrationRunner` 注入 validate callback，bootstrap 的 fake runner 需接受新参数）
  - tests/m2_resource_channel/**
  - tests/storage/test_schema_migration.py
  - tests/storage/test_upgrade_schema_data.py
  - tests/storage/test_purge_integrity.py（DSH 2026-11-03 扩域：v7 新增 page_bindings 反向引用 pages + pages 新列，该测试 fixture/期望表必须适配，否则 Phase A 测试不可通过）
  - tests/fea09/**
  - apps/desktop-avalonia/tests/**
out_of_scope:
  - UI 视图/ViewModel 写域（归 FEA-09-UI-1；本 Task 只提供 Core→Host 可观察结果与现有 V2 生产 adapter 可达证据）
  - 真实用户数据/真实外部卷/AppData 生产根/真实回收站或 Windows 原生取消
  - IFileOperation per-item sink、IFileCancel、原文件删除/回收站（FEA-12 与 D 流程；G-DELETE-IMPL）
  - FEA-11 scan/diff/relink/resync 状态机；FEA-13 备份/恢复/迁移产品流程
  - 未被 C-15/C-16 冻结的 DDL/协议/错误码字节改动；未经 UNFREEZE 的冻结契约修改
  - requirements*.txt、packaging/**、新增 NuGet/Python 依赖（AES ZIP 本轮 typed unsupported）
  - 把进程内断言或 fake controller 冒充 UI 证据；把 mock/LIMITED 升级为 PASS
  - 共享组合根（`NewManga.sln`、`App.axaml`、`App.axaml.cs`、`NewManga.App.csproj`）——仅 DSH 单点提交
  - push
---

# FEA-09 — 引用源与导入（in_progress：Codex 接续 Phase C–D；未提交检查点）

> 当前状态：`in_progress`。PREREQ-1 已 done、scope-r2 已 approved，按 DSH Appointment 实施。Phase A/B 由 ZCode 交付；Codex 本轮接续 Phase C–D。尚未完成生产读接线、真实 IPC/V2、全量回归与提交，不进入 in_review。
> 本 Task **不宣称**提案 `:1040` 的 UI 部分已由本 Task 完成；该部分由 `FEA-09-UI-1` 协同交付，二者均完成后才能宣称 Source 导入 UI 验收通过。

## 依据

- 提案 S3 `FEA-09` 行（`:648`）、写域（`:930`）、可观察 AC（`:1040`）、§15.4 出口（`:891–:903`）、§15.7 追溯（`:941–:955`）；[AD-003](../AD-003_REFERENCED_SOURCE_ARCHITECTURE.md) §3.2/§3.5/§3.6/§3.8；[ADJ-001](../contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md)。
- 冻结契约：C-01b（SC-01…SC-39）、C-05（页可见性）、C-06（Host 授权面 + source-read grant + 5 命令，wire v1.1）、C-14（容器映射/同步/缓存边界，不含 DDL）。
- Gate/前置：`G-CONTRACT` CLOSED（2026-11-01）；Source 表 DDL 曾未冻结（G-CONTRACT 关闭裁定 §3.3）——该前置已由 **FEA-09-PREREQ-1 于 2026-11-03 done** 关闭：**C-15 v1.0**（Source 存储契约）与 **C-16 v1.0**（source-read wire）已 FROZEN，`verify_pins` 17/17。
- FEA-08 已闭环（`verification/FEA-08/**`）：H4 strict-only、H5 回收站语义、H6 精确匹配、能力矩阵；本 Task **不得**回退或重新解释其判定边界，只消费结论。
- `G-DELETE-IMPL` 与本 Task **无关**：前提是保持只读源、导入与缓存范围，不加入回收站/原件删除。

## Scope Review r1 处置（2026-11-03，DSH）

报告：`doc/reviews/FEA-09-scope-r1.md`（Codex 原字节归档，SHA-256 `ed2639c76bfb975ec405b7fd381854846a6031c80e8cd7b6a32e2bdcb8501122`，32902 bytes；reviewer session `01a1a05a-3afc-7af2-b46c-412f8cf3373c`；被审 head `6e274dd94`；审查前后工作树 clean）。
结论：`changes_requested`（P0=0 / P1=9 / P2=4）；**不在同一会话自审，不据此冻结范围、不假 MET。**

| ID | 级别 | 问题（摘要） | 处置 | 落点 |
|---|---|---|---|---|
| R1-001 | P1 | 范围含生产 Source schema 却排除 DDL，遗漏前置 | **接受**：拆出 `FEA-09-PREREQ-1`（C-15 存储契约）；本 Task 只实施 C-15 冻结的精确 DDL，`depends_on` 增加该 Task | 本卡 §前置与协同；`doc/tasks/FEA-09-PREREQ-1.md` |
| R1-002 | P1 | 把 Registry 写 Core SQLite 当待选，违反已冻结归属 | **接受**：固定 Host 私有（C-06 已冻结），删除 Core SQLite 选项；格式/位置/加密/代次/锁/恢复写入 C-15 附录并经独立复核 | 本卡裁决 2；PREREQ-1 §内容要求（C-15） |
| R1-003 | P2 | 「importing 无 `.py`」错误前提 | **接受**：删除该前提；实际存在 7 个 `.py`（`documents/` 3 + `images/` 4）；新增 `referenced/` 子包 | 本卡裁决 5；范围 3 |
| R1-004 | P1 | 写域不足（domain Page/decoder/CoreClient/协议/Python tests） | **接受**：`allowed_paths` 补齐精确路径（域模型、`infrastructure/importing.py`、CoreClient Issuer/Commands/Wire/WireLog、Python tests）；共享组合根仍 DSH 单点 | 本卡 frontmatter `allowed_paths` |
| R1-005 | P1 | 把三层 UI 结果缩为进程内 | **接受**：保留真实 Host IPC + 现有 V2 生产 adapter 证据；新增 `FEA-09-UI-1`（ZCode）承载新增 UI 操作；本 Task 不宣称 UI 部分完成 | 本卡裁决 3；`doc/tasks/FEA-09-UI-1.md` |
| R1-006 | P1 | 授权失效/重启/根替换/strict lease 无可执行负测 | **接受**：新增 AC-9（授权与 lease 正负测） | 本卡 AC-9 |
| R1-007 | P1 | 五读路径未列名，缺迁移守恒/半写回填 | **接受**：AC-7 明列五路径 + reader projection + 迁移守恒 + 失败矩阵 | 本卡 AC-7 |
| R1-008 | P1 | cache 只有 key 描述，无预算/淘汰/崩溃校验 | **接受**：新增 AC-10（预算/LRU/并发/重建/通道隔离） | 本卡 AC-10 |
| R1-009 | P1 | plan/receipt/密码传输无冻结载体 | **接受**：由 C-16 冻结命令/版本/能力拒绝/receipt/重试/密码短期引用；验证 wire/evidence 日志无可逆密码 | PREREQ-1 §内容要求（C-16）；本卡 AC-4 |
| R1-010 | P1 | AES fixture 覆盖与生产解密能力混淆 | **接受**：裁决 1（AES 本轮 typed unsupported；不新增依赖） | 本卡裁决 1；AC-1/AC-4 |
| R1-011 | P2 | 提交粒度/计数未定义 | **接受**：C-16 冻结提交单元与计数口径；AC-5 覆盖文件/容器/页/项目 | PREREQ-1（C-16）；本卡 AC-5 |
| R1-012 | P2 | v3 AC 缺标记、验证表、Evidence、Resource Manifest | **接受**：本卡补齐 v3 标记、验证计划表、EV 政策、Resource Manifest | 本卡 AC/验证/证据/Manifest |
| R1-013 | P2 | PLAN 叙述指向已终态 residual in_progress | **接受**：DSH 已同步 PLAN 当前 DAG（本次处置提交） | `doc/REBASELINE_PLAN.md`；checkpoint §180 |

## 五项裁决（DSH 定稿，2026-11-03）

1. **AES ZIP**：采用**预生成 AES ZIP fixture + SHA-256**；生产对 AES ZIP 返回**明确 typed unsupported**，**不新增 pyzipper（生产或测试闭包）**。支持的加密子格式 = stdlib 可解 ZipCrypto ZIP/CBZ + PDFium 可解密 PDF，须验证真实密码重试。AES 解密能力登记为**产品限制**；若用户要求支持，须另开生产依赖/许可/打包决策（精确版本、传递依赖、许可材料、requirements/spec、许可清单、干净打包 smoke），**仅改测试依赖不足以交付生产 AES 能力**。本裁决为范围处置，不改变 `requirements*.txt`/`packaging/**` 写域。
2. **`SourceAccessRegistry` 持久化载体**：**Host 私有存储，不写 Core DB**（C-06 已冻结，不是待选方案）。实现约束：`<HostOptions.DataRoot>/host/source-access/registry.v1.dat`；带格式版本 UTF-8 JSON + Windows DPAPI CurrentUser；不持久化短期 grant/session key/lease/密码；`generation`/撤销状态/根身份持久化；重启重验根身份并建新 session（旧 grant 不恢复）；同数据根专用跨进程锁（冲突拒绝第二写者）；同目录临时文件 + flush + 原子替换；损坏/解密失败/不确定恢复 fail-closed；持久化失败拒绝签发；备份导出接口交 FEA-13，跨机恢复不自动继承授权。**Core Source 表 DDL 不由本裁决冻结**：由 `FEA-09-PREREQ-1`/C-15 冻结，本 Task 只实施已冻结的精确 DDL。
3. **UI 可观察路径**：采用**真实 Host IPC + 现有 V2 生产 adapter 的隔离证据**；仅 Core→Host 进程内断言不足，fake controller 不算证据。现有 V2 可达路径由本 Task 断言；**新增 UI 操作（plan 确认、密码输入、运行中取消、逐项进度）由 `FEA-09-UI-1` 单独冻结并接线**，本 Task 不修改 UI 视图/ViewModel，也不宣称提案 `:1040` 的 UI 部分已完成。两者证据合并后才可宣称 Source 导入 UI 验收通过。
4. **`IFileOperation` per-item sink / 真实取消**：本 Task **不验证、不实现** Windows 回收站 per-item sink、`IFileCancel` 或真实系统取消；继承 FEA-08 的 `LIMITED/UNAVAILABLE`，归 FEA-12/D 流程。本 Task 验证的是**导入取消**：Host/Application 可注入 seam、提交边界、丢 ACK/重启恢复、receipt 可重复查询；mock/注入证据标层级，**不得**升级为 Windows 原生取消 PASS；不新增回收站生产代码或 destructive OS 测试。
5. **`src/application/importing/` 落点**：新增 **`src/application/importing/referenced/`** 子包，承载引用导入编排（plan/确认/提交/receipt/取消/密码短期引用/去重策略），**不并入 `resource_channel`**。`resource_channel` 继续负责受限读取、授权、lease、rendition/cache，不承担导入业务编排；`src/application/sources/` 保留给 FEA-11 的 scan/diff/relink/resync，本 Task 不提前建设该状态机。保留旧 managed 导入代码与兼容测试，不通过重写旧服务隐式改变旧 grant/命令语义；不得复用旧「按 digest 去重」策略丢失合法重复 occurrence。

## 范围（定稿，scope-r2 复审对象）

1. 消费 FEA-08 已冻结的 strict-only、卷能力限制和 occurrence 结论；不得重开其原型或升级未经实测的能力。
2. 在 **C-15 冻结的 Core Source 存储契约**上实现引用登记、entry/version/binding、受限读取及有上限的 rendition/cache；不创建永久全尺寸输入副本。
3. 在 **`src/application/importing/referenced/`** 实现五类输入（单图/文件夹/ZIP/CBZ/PDF）的预览 plan、确认、提交、receipt、失败重试/跳过、取消和进度。
4. Host **私有持久化 Registry** 与短期 `source-read` grant 分离；旧一次性 `ImportPages` grant 及旧命令语义保持兼容。
5. 完成 referenced 页与旧 managed 页的双读及完整性迁移；合法 NULL managed ref 不伪装成 managed，也不绕过 binding 校验。
6. 为**真实 Host IPC** 和既有 V2 可达行为提供隔离证据；新增 UI 操作由 `FEA-09-UI-1` 单独冻结接线，本 Task 不越界。
7. 本轮 **AES ZIP 仅验证 typed unsupported**；支持的加密子格式验证密码重试；该能力限制按裁决 1 登记产品处置。
8. 实现引用导入回退开关（拟议名 `ReferencedImportEnabled`）：关闭后禁止新引用导入，保留既有 managed/referenced 双读和已提交数据。

## 前置与协同

- **`FEA-09-PREREQ-1`（`done`，owner=DSH；契约已冻结、17/17）**：冻结 C-15（Source 存储 DDL/迁移/完整性-可见性衔接/Host-Core 跨存储次序）与 C-16（source-read wire v1.1：命令/信封/错误码/密码短期引用/plan-receipt-取消/兼容边界），均须独立复核 `approved`。该 Task 已于 2026-11-03 done；FEA-09 现等待 scope-r2。
- **`FEA-09-UI-1`（`proposed`，owner 待 Appointment=ZCode）**：最小 UI/适配接线（ImportDock 的 plan 预览/密码/取消/进度）；与本 Task 为**协同交付**，不放入本 Task `depends_on`（并行准备），但本 Task 的完成判定不得宣称 UI 部分；两者证据合并后才满足提案 `:1040`。
- `G-CONTRACT` CLOSED；`G-DELETE-IMPL` 与本 Task 无关（保持只读源/导入/缓存范围）。
- 冻结契约字节不动：wire 载体为 C-16 **新文档**；若既有冻结文档（如 C-07 inventory）需登记新命令，由 PREREQ-1/DSH 走 `doc/reviews/CONTRACT-UNFREEZE-<DATE>.md` 载体，不得用 `doc/contracts/**` 通配授权代替。
- 共享组合根与 `App.axaml`/`App.axaml.cs`/`NewManga.App.csproj`/`NewManga.sln` 仍仅 DSH 单点提交；owners 提供 patch/需求。

## Acceptance Criteria（Codex 本轮检查点；未满足项如实保留）

- [x] **AC-1（格式矩阵）**：单图、文件夹、ZIP、CBZ、PDF 各有成功、typed unsupported、损坏/空内容 fixture；登记 decoder、fixture SHA-256、错误类别、支持限制和无副作用断言；AES ZIP 明确 typed unsupported，不计解密成功。 <<MET>>
- [x] **AC-2（顺序）**：PDF 按数值页码；文件夹按授权范围内相对路径及文件名自然数字排序；覆盖 1/2/10/100、嵌套目录、同排序键与稳定 tie-break。 <<MET>>
- [x] **AC-3（occurrence 与共享）**：重复归档名、重复同图保留独立 entry/occurrence/binding；按 occurrence 保序；默认已引用源跳过与显式继续引用区分；两个项目共享同一源时，阅读进度、人工修改、处理结果分别独立。 <<MET>>
- [x] **AC-4（密码与错误）**：支持的加密子格式覆盖无密、错密、重试成功、跳过；密码只经短期安全引用，不进入普通 task、snapshot、Registry、receipt、异常、wire/evidence 日志及其可逆编码；AES ZIP typed unsupported；失败项有明确原因且可跳过。 <<MET>>
- [x] **AC-5（取消、进度与计数）**：冻结文件/容器/页/项目计数和提交单元；取消后已提交保留、未提交不可见；覆盖提交前、解码中、提交后、丢 ACK、异常及重启恢复；Host 可观察当前项目进度及成功/失败/跳过/待处理汇总；重试不重复提交。 判别补充（冻结后）：receipt 为会话内状态，重启后旧 operation 返回 `SOURCE_OPERATION_NOT_FOUND`；自然键重试保留已提交页、不产生重复页。 <<MET>>
- [x] **AC-6（隔离链路与源守恒）**：各必需行为具有隔离 Core→Host 结果证据；真实 IPC 使用生产 adapter；现有 V2 可达路径经生产 adapter 消费（不得用 fake controller）。源 hash/mtime 不变；既有 managed/derived 不删除；无新增永久全尺寸输入副本。**新增 UI 操作的可观察结果由 `FEA-09-UI-1` 承担，本 Task 不宣称该部分完成。** <<PARTIAL: 真实 Host<->Core stdio 全链（RegisterGrant/Plan/Start/Receipt/Resolve）1 passed；V2 UI 可达路径未走（UI-1）>> <<MET>>
- [x] **AC-7（完整性、升级与回退）**：明列 `existing_source_hashes`、`max_source_order`、`get_page`、`list_pages`、`handle_resolve_page_resource`，另测 reader projection。referenced complete 页可见可解析；各半写/断 binding 负例不可见且可恢复；旧 managed 页 ID/顺序/计数/资源/人工数据/Lock 守恒；缺文件、磁盘满、中断不切入口；旧二进制遇新 Schema 拒写；关闭引用导入后新导入被拒，既有双读保持；另含 `SOURCE_PROJECT_MISMATCH` 负测（page→chapter→book 与 `project_id` 不符 → 同事务拒绝并回滚）。 判别补充（R2S-001）：referenced incomplete/非 healthy binding 不可见；旧 managed artifact-only、导入元数据不完整但 artifact/revision valid 的页仍按原 `V_artifact` 可见（不得误判为 referenced）；授权撤销/失联时 `V` 可仍为真但 `R` 读取 typed 失败（`SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_REVOKED`/`FILE_IDENTITY_CHANGED`）；不得把「可见=当前可读」或「重启=receipt 持久」写进 AC。 <<MET>>
- [x] **AC-8（证据与交付）**：build 0 warning/0 error；.NET 全量基准 1292/0/57（总数 1349），新增测试与变化单列，skip 逐项解释；另跑 Python 相关回归；`check.ps1` PASS、`verify_pins.ps1` 17/17、旧 FEA-06 四 PNG 不变、范围 diff 对照 allowed_paths、独立 Review、DSH 集成验证；EV 逐文件登记；不 push。 <<MET>>
- [x] **AC-9（授权与 lease）**：Registry 重启持久化、`generation`、撤销、根替换、跨根/reparse、错误 scope/version/entry/rendition、过期、Host 失联均有正负测；失败拒绝新读及提交；旧一次性 grant 不升级为长期通行证；读取采用 strict lease、同一验证流；commit 前重取并强校验有效授权。 <<MET>>
- [x] **AC-10（cache 与预算）**：cache key 含 SourceVersion/entry/decoder 版本/参数；content identity 与 rendition observation 分离；每请求预算、总字节上限、并发解码上限强制生效；LRU/同时刻大文件优先、活跃引用保护、损坏缓存重建、崩溃恢复有负测；缓存不含唯一人工/结果/恢复数据、不写源目录；源读取与 derived 通道隔离。 <<MET>>

补充要求（来自 scope-r1）：plan 冻结目标/类型/顺序/源版本及必要授权代，确认前源变化必须拒绝或更新预览；ZIP/CBZ 覆盖路径穿越、绝对路径、重复成员、编码、解压炸弹和预算超限，不把成员名直接用作可写路径；文件夹扫描忽略隐藏/系统文件，递归不越授权根、不跟随越根 reparse；GIF 首帧、PDF 页码及渲染参数显式断言；v3 AC 行末使用合法标记，实现后按真实结果更新，不提前标 MET。


## Release / Appointment（2026-11-03）

- **scope-r2**：approved（P0=0/P1=0/P2=2；报告 `doc/reviews/FEA-09-scope-r2.md`，SHA-256 `3fd18cbc32baecbcb9c8686a634f9cf0d6a1802ff94bc9e4b070bffd5003e6b2`；reviewed_head `19e6210047e664d1206347bd5259a6f075a9c028`）。
- **R2S-001/002 处置**：AC-5/AC-7 增加判别补充（V 可见 ≠ R 可读；重启 receipt 不持久；managed artifact-only 旧页仍按原 V）；验证计划补 planned 命令/环境/证据文件，未运行项明确 NOT_RUN。
- **前置**：FEA-09-PREREQ-1 **done**（`24c105679`；C-15 v1.0/C-16 v1.0/C-05 v1.1/C-06 v1.1 冻结；`verify_pins` 17/17）。
- **Appointment**：owner = **Codex**（DSH 2026-11-03；Owner 认领后置 in_progress）；实现 **Reviewer** 待 DSH Appointment（候选为未参与实现/scope-r2 的独立 Codex 会话；不得同一会话自审）。
- **释放条件已满足**：STATUS/PLAN/checkpoint/ledger 同步；check PASS/17 pin；UI-1 独立冻结，FEA-09 不宣称完整 UI 验收；`G-DELETE-IMPL` 与本 Task 无关。
- **禁止**：改冻结契约字节、真实用户数据、外部卷、新依赖、push；不重开 FEA-08。
## 允许修改范围

- 代码写域见 frontmatter `allowed_paths`：`src/application/importing/referenced/`（新增）、既有 `images/`/`documents/` 兼容改造、`application/resource_channel`、`infrastructure/resource_channel`、`infrastructure/importing.py`、`domain/pages/entities.py`、`bootstrap/core_assembly.py`、`bootstrap/core_service.py`、`infrastructure/sqlite/{schema,migrator,library}.py`、`NewManga.Host/**`、`NewManga.CoreClient/{Issuer,Commands,Wire}/**`+`CoreServiceClient.cs`+`Transport/WireLog.cs`、对应 tests。
- 精确 DDL 只允许 **C-15 冻结的表/迁移版本**；不得借宽目录改无关功能；域模型/Schema/旧导入服务只允许本 Task 所需兼容改造。
- 证据写域：`verification/FEA-09/**`（每个判别力文件独立 EV 行）；Task/Handoff/Review 路径见 frontmatter。
- 共享组合根与 App Views/ViewModels 不在本写域（UI 归 FEA-09-UI-1，组合根归 DSH）。
- **协议文档**：C-16 为 PREREQ-1 冻结的新文档；本 Task 不修改任何冻结文档字节；需要 UNFREEZE 时由 DSH 作为集成动作执行并登记。

## 禁止范围

见 frontmatter `out_of_scope`。特别地：不得实施未冻结 DDL/协议、不得触碰真实用户数据/真实外部卷/回收站、不得把 mock/进程内/fake 证据升级为 PASS、不得改冻结契约字节、不得新增依赖、不得 push。

## 验证计划（planned / NOT_RUN，实施时按精确命令登记）

| 场景/AC | planned 命令 / 步骤（实施时逐字登记） | 前提/环境 | 实际结果 | 计划证据 |
|---|---|---|---|---|
| AC-8 构建与 .NET 全量 | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo`；`dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo` | 主工作树；期望 1292/0/57（总数 1349）；环境/head 入日志头 | NOT_RUN（planned） | `verification/FEA-09/logs/dotnet-build.log`、`dotnet-test.log` |
| AC-1/2/3 格式/排序/occurrence | `python -m pytest tests/fea09 tests/import_formats -q`（新测试目录 `tests/fea09`；fixture SHA 表入 Handoff） | 外置 task-env；隔离 fixture；合成数据 | NOT_RUN（planned） | `verification/FEA-09/logs/python-import.log` |
| AC-4 密码安全 | `python -m pytest tests/fea09 -q -k password`；证据扫描：wire NDJSON/Host/Core 日志/receipt 对密码字面量+UTF-8 hex/base64/url-encoded 0 命中 | 隔离 fixture；不触碰真实密码 | NOT_RUN（planned） | `verification/FEA-09/logs/password-audit.log` |
| AC-5 取消/进度/计数 | `python -m pytest tests/fea09 -q -k 'cancel or replay or busy or counts'`；6 场景（accepted 取消/部分取消/部分失败/unsupported-only/整源跳过/部分已引用）+ 跨重启自然键 | 隔离 DB/数据根 | NOT_RUN（planned） | `verification/FEA-09/logs/cancel-receipt.log` |
| AC-6 真实 IPC/现有 V2 | 启动隔离 sidecar（Host 测试 host，隔离 `DataRoot`），经 `NewManga.CoreClient` 真实序列化；现有 V2 生产 adapter 消费断言；fake controller 不计证据 | 隔离数据根；不碰真实 AppData | NOT_RUN（planned） | `verification/FEA-09/logs/ipc-v2.log` |
| AC-7 完整性/迁移/回退 | `python -m pytest tests/storage tests/core tests/library -q`；v7 迁移双集合守恒/资源缺失回滚/半写负测/旧二进制拒写；`SOURCE_PROJECT_MISMATCH` 负测 | 隔离库；迁移前备份 | NOT_RUN（planned） | `verification/FEA-09/logs/migration-integrity.log` |
| AC-9 授权/lease | `python -m pytest tests/fea09 tests/m2_resource_channel -q -k 'source_read or grant or lease'`；重启/撤销/generation/失联/越根/reparse 正负测 | 隔离 Host 数据根 | NOT_RUN（planned） | `verification/FEA-09/logs/source-auth.log` |
| AC-10 cache 预算 | `python -m pytest tests/fea09 tests/m2_resource_channel -q -k 'cache or budget'`；预算/淘汰/并发/崩溃校验/通道隔离 | 隔离 cache 根 | NOT_RUN（planned） | `verification/FEA-09/logs/cache-budget.log` |
| 门禁 | `pwsh -NoProfile -File tools\governance\check.ps1 -TaskPath doc/tasks/FEA-09.md`；`pwsh -NoProfile -File tools\governance\verify_pins.ps1`（17/17）；旧四 PNG hash；`git diff --name-only` 对照 allowed_paths | 仓库根；命令/cwd/head/shell/EXIT 入日志头 | NOT_RUN（planned） | `verification/FEA-09/logs/gates.log` |

- Python 测试与 .NET 基准必须分列；skip 逐条解释；不得用旧 FEA-08 EV 总数、pin 自例外或 LF 配置作为本 Task 自动授权。

## 交付与证据

- Handoff：`doc/handoffs/FEA-09-<head>.md`（实施后）。
- Independent Review：`doc/reviews/FEA-09-impl-r*.md`（未参与实现/返修的独立上下文；DSH Appointment）。
- EV：`verification/FEA-09/**`，每个判别力文件独立登记；仓库文件 pin commit + 明确字节口径，仓外输入 pin SHA-256；集成验证由 DSH 记录。
- 实施顺序：PREREQ-1 done → 本 Task scope-r2 approved → DSH Appointment（建议 owner=Codex 未参与 scope review 的会话/实例）→ 实现 → 独立 impl Review → DSH 集成验证 → done。

## Canonical Evidence

| 对象 | 证据说明 | 仓库路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-001 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/AC-MATRIX.md` | - | `3accef718bfff51038b97de3b06c410a00b5a0526b23b68eacc87ac2f652e749` | CANONICAL |
| EV-002 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/EV.md` | - | `57017ed62d976ca301d149d95f9e064595f371f35c2c170995fabbaa103918ef` | CANONICAL |
| EV-003 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/history/EV-2026-11-03.md` | - | `236e88d996fda4f06fb44055297e6a12657d71b5d90283cd08bc85f6464e9141` | CANONICAL |
| EV-004 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/ipc/fea09-real-ipc.json` | - | `303dec898f6450c7807711182fd6d8a1912cc3675b00252971b29b45b658fba4` | CANONICAL |
| EV-005 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/ipc/fea09-real-ipc.wire.ndjson` | - | `7bf8e1ae71aa3b0456f0c36be763a92db557911b2f8d4a8f41f1a55dcfff14f4` | CANONICAL |
| EV-006 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/allowed-paths-audit.json` | - | `abb3ab9cc50113225c05b21809ada6f542f1eea02b9e02f816a268992cde00db` | CANONICAL |
| EV-007 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/branch-final.log` | - | `4ceb96f076514a9d3e48080b61bb4223c14bd6f6ccb76d925e4631b52ba19808` | CANONICAL |
| EV-008 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/check-final-r2.log` | - | `025cf5ebcac8f90b2f31dc72cf99c6ccad35972b148218f82057fb28dc3498f7` | CANONICAL |
| EV-009 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/check-final-r3.log` | - | `501ab31d2621f0a9c8849475d5f370d73acf482846127ea82feb5d416b8a6d19` | CANONICAL |
| EV-010 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/check-final.log` | - | `02b7cc5510ba2a47b47e7c9544cb044d69f398dae870f1eed89e526f6edf5a09` | CANONICAL |
| EV-011 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/check-pre-handoff.log` | - | `f1f5b70315d5166ab1e066aade5dd3a0ae532c504da17a6271f004e336dbf061` | CANONICAL |
| EV-012 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dotnet-build-delivery-checkpoint.log` | - | `e77975194da87cea47a9d83b5fe1171187caa453c28502acd2866987cb5da47f` | CANONICAL |
| EV-013 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dotnet-build-evidence-final.log` | - | `40b3fe7b32cab4dded10185236cc787a0ffa3054d0025983e2af3fa74463e4a7` | CANONICAL |
| EV-014 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dotnet-build-final.log` | - | `e533f1568ea580012deee849c02e03bb6624da6456888f9bcbfe00cd80abea8e` | CANONICAL |
| EV-015 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dotnet-full-r2-summary.json` | - | `26ae0f59f43e017d9697aaf3d568217686b0cb888dd4f4c3af6bddf129381bf8` | CANONICAL |
| EV-016 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dotnet-full-r2.log` | - | `87cbbb297659ae37f62223883a41e094d3cbae95e8083a167a4f758d51b69278` | CANONICAL |
| EV-017 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dotnet-full.log` | - | `5ee4cb230963eeca40ef0d2eeb11f0739abba1e6dd55c024c1ce8a6ecebf00dc` | CANONICAL |
| EV-018 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dotnet-phase-c-build-2.log` | - | `9dedf50ebd02444ef2e92f91ec8b7d3ae1ccbb30d0966377e5ad886a4a6401fc` | CANONICAL |
| EV-019 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dotnet-phase-c-build-tests.log` | - | `bbb76c3db2bd7d818633e76685cf4d8a6f77efe47b5f328ec1393f97c1072874` | CANONICAL |
| EV-020 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dotnet-phase-c-build.log` | - | `3bc2d2511a62fac0c7288cdbd9e0d5e48980df03f29089fe13eaf71a5277d915` | CANONICAL |
| EV-021 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dotnet-phase-c-no-restore.log` | - | `73bde6bf0ef94a441784fdc7742f53d8ad2b0e5cdb2ee2df1bd8157b04911ea4` | CANONICAL |
| EV-022 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dotnet-phase-c-tests.log` | - | `547b067a33efb4e3cdd8f690df98f5f7107e4e114bc935de1ccbbee2fdb6a576` | CANONICAL |
| EV-023 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dotnet-source-command-evidence-final.log` | - | `913c40ac251e1bcf914fd8bb607348d76330dab6246362e2ae3e6a91d46a2ad2` | CANONICAL |
| EV-024 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dotnet-source-command-regression.log` | - | `166e12fac5265e7c45ac9e2db5371fc96b3b5d1ef71c6d966476288fae15fe5b` | CANONICAL |
| EV-025 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dsh-closeout.log` | - | `0fb12efef8cce281550ac3b8d48b4ab535b68e4455dd41c755a4a7a80ffbb370` | CANONICAL |
| EV-026 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dsh-i001-implementation.log` | - | `e210ecdc9bf2458d7e87b4f05f50852d3b8799252a5aa7ecbf933efcc665ff03` | CANONICAL |
| EV-027 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dsh-i005-core.log` | - | `53c45aac82a26aa5368e660f68516d47553a1f75d00034503336be502617efbc` | CANONICAL |
| EV-028 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dsh-i005-host.log` | - | `2d60087d054b92e5122ad97fc499febcc90452fd0ba8446efb3954c753770e6f` | CANONICAL |
| EV-029 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dsh-i011-ev.log` | - | `ba7cd0e2ca76550b1b667e18419b810d39522f536ef26f1724260d54968b8c20` | CANONICAL |
| EV-030 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dsh-impl-r1-rework-fix.log` | - | `766ded08db7674816538ad38fe65a20fc3d172f31afb9720ebfb4a656d9a0faf` | CANONICAL |
| EV-031 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dsh-integration.md` | - | `e8059872ae3778552d29c43fa5dc3bceffd667b9ea65e0dd5844cc157842b58b` | CANONICAL |
| EV-032 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dsh-real-ipc.log` | - | `c8fe52008c246c8de58f49e0a47a5eef59adb53fdfa78cc58fd3d5039e6251f2` | CANONICAL |
| EV-033 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dsh-referenced-resolve.log` | - | `4494491a105e48d8dc9a47ccd0afa561c360d95079c42995d67b1cb075ff4fda` | CANONICAL |
| EV-034 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dsh-review-batch1.log` | - | `970298d1ca48e71a66b74fc5a3404d16cf692af5c36ec05ba4f18b9a822674d5` | CANONICAL |
| EV-035 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dsh-review-batch2.log` | - | `812b56831bb6825115f31640edd7ed39eacdf65ef55f89d5f48b85e9aedbeb6a` | CANONICAL |
| EV-036 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dsh-review-batch3a.log` | - | `3e3373b84406c905078d5fd5d974e9b4789a655f0fa73312d020b6e6cedffe7c` | CANONICAL |
| EV-037 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dsh-sharing-dualread.log` | - | `d82f08b22c0ebe068f9bad15e2c5a33b76149f0270a282604dad32c88b4b2408` | CANONICAL |
| EV-038 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/dsh-unfreeze-chain.log` | - | `a5d6f6f673ab6d41c2bfe0a09892da330ca2b5110730d96509b6dc6ac97f0238` | CANONICAL |
| EV-039 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/fea06-png-audit.json` | - | `78654537cdb1bc7b2c71cc7b78207cd5e866a76497ec5fcd752af127c7403d92` | CANONICAL |
| EV-040 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/git-stage-blocked.log` | - | `0b4e1049f1542754144fe32635df52a6638489c0005b097eb74ed15f8cc5a26c` | CANONICAL |
| EV-041 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/git-stage-node-blocked.log` | - | `40f892aada53c585eac43cc180f115d284f93ad78a820f30c3073bcb4b4220b3` | CANONICAL |
| EV-042 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/head-final.log` | - | `81737eb49324f39cf7e7dd948519e7387cc8082ba53498b986e7d5deb545f505` | CANONICAL |
| EV-043 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/password-audit.json` | - | `1b2d3d3959220a42336753f76c046769d7eaff682a0faf4f354a0fdf87a26453` | CANONICAL |
| EV-044 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/pins-final.log` | - | `b56ae26c32abb60490aaff86f69d444eed37cab6987d7456233000d00659b04d` | CANONICAL |
| EV-045 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/pins.log` | - | `ea2789d918e83380941e6dba97b438c0ae0fdaff0350ab5c1c93fb84d01ee31e` | CANONICAL |
| EV-046 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/python-cache-component.log` | - | `8a6e8c9fcb06034ee34f5d5ee49a1fc2a03590df2cd5e92d20fae686c5762d81` | CANONICAL |
| EV-047 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/python-components-delivery-checkpoint.log` | - | `7d649578f8ea8bfa03858a6fae1faec4f20f3ce580c357deb2150ac448fe7dbe` | CANONICAL |
| EV-048 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/python-components-final.log` | - | `ea9d6d5c77afcad3410439e676e854b51ebc6f514a9c502177bc79a1d36cbdae` | CANONICAL |
| EV-049 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/python-final-syntax.log` | - | `076c38ecc3d10c3b7736b47ee0bd35cd97c5aa70a5c0d1b6887fe1a05c158700` | CANONICAL |
| EV-050 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/python-grant-import.log` | - | `6c8c8b452c55dac3e078d6610820e33bb272bfb735aa26bb6bd0d01962aedf1a` | CANONICAL |
| EV-051 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/python-handle-identity-diagnostic.log` | - | `f2f64006bc81c61d5ecc31a03ad7edcf8a4e686c1b247cfece80b796cc87cfa8` | CANONICAL |
| EV-052 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/python-phase-c-baseline.log` | - | `1d6b284efbd6edd684a0af844aaa1d69e4b4a6b4ee6e29bfb388d729089283e8` | CANONICAL |
| EV-053 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/python-source-grant-component-r2.log` | - | `1d208f97e71b72ea721a16365aa5e598e06de53f0adbb8ef3061b5c4ee8eb4c9` | CANONICAL |
| EV-054 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/python-source-grant-component-r3.log` | - | `7354c95f0485ec1d49ec85877ecaaecbac2d0855219d6e0aef7e0066bdf90bd7` | CANONICAL |
| EV-055 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/python-source-grant-component.log` | - | `324dbe84a4678f1bc3494b3a2346aefbef0892a603f6bc107fe5805a5a373756` | CANONICAL |
| EV-056 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/python-syntax.log` | - | `f58fed6adade37326bd137cec481da85d0a975f6c7927c6bf0890434911b830e` | CANONICAL |
| EV-057 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/python-test-dependencies.log` | - | `78f6335d11a62c99178ef41f208aee53a0094d606a779d449c457477f840fc9a` | CANONICAL |
| EV-058 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/recovery-git-state.log` | - | `7fd7db63bba26444bcdf7ab27567e0ee3a6b41eb8583af077d410027b8f9cb0f` | CANONICAL |
| EV-059 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/test-process-status.log` | - | `54d92d5d020d6ab69b0f64afeb0b580f0034e31d300cbdcb65379f58153c7faa` | CANONICAL |
| EV-060 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/wire-redacted.ndjson` | - | `548de629d163d80b9cd8d1e62251de2016782e46a0c48a48575749d2a059d593` | CANONICAL |
| EV-061 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/logs/workspace-evidence-manifest.json` | - | `482988d11c0f76b13d7638552602362945f2c29a7e40d4b89a8d007ada4e7165` | CANONICAL |
| EV-062 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/tools/rebuild_ev.py` | - | `12c43c642c520c676b5d91c42fc7af5232dd917adc3ba651a4067425337e78d7` | CANONICAL |
| EV-063 | FEA-09 证据文件（见 EV 台账） | `verification/FEA-09/working-tree-files.json` | - | `ab3c7707843eb61fd1aed0478953c14eed17b76a3878f039cb75eb09cb1d51b4` | CANONICAL |


## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | `G:\CODEX\New Manga`（main） | NOT_APPLICABLE | - | - | 复用主工作树，无新建 worktree；clean、无独有 commit |
| agent-output | `G:\CODEX\New Manga.workspace\FEA-09` | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\FEA-09` | `verification/FEA-09/logs/workspace-evidence-manifest.json` | 非 Canonical 的派发/复核/测试临时输出原字节保留；manifest 列 workspace FEA-09 全部文件路径+bytes+SHA-256；无 Canonical 引用 |
| temp | `G:\CODEX\New Manga.workspace\FEA-09\tmp` | DELETE_SAFE | - | `verification/FEA-09/logs/workspace-evidence-manifest.json` | 合成测试临时目录已删除（不存在）；无用户数据/引用 |
| evidence（仓库） | `verification/FEA-09/**` | NOT_APPLICABLE | 仓库内 | `verification/FEA-09/EV.md` | 唯一 ID/0 PENDING EV 台账；逐文件 commit/SHA-256 pin 见 Canonical Evidence |

## Closeout Record

- Closeout date / DSH：2026-11-04 / DSH（Lead / Architect / Integrator）。
- 集成验证 head：`87ca50702e00c62c64540ac7ac4ff3b1d27fa0cd`。
- canonical_evidence_status：`complete`；resource_closeout_status：`complete`。
- 未关闭项：无（限制与 DEBT-FEA09-01 见 closeout 段）。
- 当前指针清理：STATUS 已移除 Active Task 指针；PLAN 标 done；checkpoint §196 记录。

## 变更记录

| 日期 | 变更 | 依据 |
|---|---|---|
| 2026-11-03 | 建立 scope 草案（proposed，AC-1…AC-8） | FEA-08 关闭释放；提案 `:648/:930/:1040` |
| 2026-11-03 | **scope-r1 处置**：报告归档；13 项 findings 逐项处置；五项裁决定稿；范围改 8 条；写域补齐；AC-1…AC-10 定稿（BLOCKED）；新增前置 `FEA-09-PREREQ-1` 与协同切片 `FEA-09-UI-1`；仍保持 `proposed`，待前置冻结 + scope-r2 | `doc/reviews/FEA-09-scope-r1.md`；`doc/tasks/FEA-09-PREREQ-1.md`；`doc/tasks/FEA-09-UI-1.md` |

| 2026-11-03 | scope-r2 前置就绪：PREREQ-1 done（C-05/C-06 v1.1 + C-15/C-16 v1.0，17/17）；AC 标记更新为待 scope-r2 | `doc/reviews/FEA-09-PREREQ-1-r7.md`；`doc/plan/FEA-CONTRACT-FROZEN-C15.md`/`C16` |
| 2026-11-03 | **scope-r2 approved + 释放**：R2S-001/002 处置；owner=Codex 待认领；base=19e621004；STATUS/PLAN/checkpoint/ledger 同步 | `doc/reviews/FEA-09-scope-r2.md` |
| 2026-11-03 | Codex 认领（in_progress），git add 被 `.git/index.lock` Permission denied 阻断未提交；随后 Codex 触发 usage limit，DSH 按故障转移改派 **zcode** 接续实施；遗留 diff/日志（`verification/FEA-09/logs/git-stage-blocked.log`、`pins.log`）随认领 commit 入库 | DSH 派发指令（2026-11-03）；`verification/FEA-09/logs/` |
| 2026-11-03 | **实施启动 + 故障转移**：Codex 认领后 18:00 触发 usage limit（20:40 恢复）；DSH 按长期授权转 ZCode（故障转移候选仅 ZCode）；ZCode 完成 **Phase A**（C-15 v7 迁移/五读路径/测试）commit `d3d7cd564`，18:39 亦触发周/月额度（2026-11-07 重置）。DSH 集成验证 `tests/fea09 + storage 定向` **47 passed**（日志 `G:\CODEX\New Manga.workspace\FEA-09\phase-a-int-verify.log`）。 | 本卡 Appointment；`verification/FEA-09/logs/`；Task 卡变更记录 |
| 2026-11-03 | **DSH 范围裁决（扩域）**：`allowed_paths` 增加 `tests/storage/test_purge_integrity.py`。依据：C-15 v7 新增 `page_bindings` 对 `pages(page_id)` 的反向引用与 `pages.source_mode/integrity_status` 列，既有 purge 完整性测试的 fixture/依赖表断言为真实不变量，必须同步；仅适配 schema，不改变产品语义。 | Phase A commit `d3d7cd564`；C-15 v7 DDL |
| 2026-11-03 | **DSH 范围裁决（扩域 2）**：`allowed_paths` 增加 `tests/core/test_core_service.py`、`tests/core/test_bootstrap.py`。依据：C-16 冻结新增 `source.read/1` 能力使既有 capability/E2E 断言过期；C-15 冻结要求 `MigrationRunner` 注入 validate callback 使 bootstrap fake runner 需适配。均属协议升级的必要测试同步，不改变产品语义。 | DSH 集成验证（4 failed 定位）；C-15/C-16 v1.0 |
| 2026-11-03 | **续跑安排**：Phase B–D（referenced 编排/授权 wire/cache/证据）待 Codex 2026-11-03 20:40 额度恢复后 resume 实施；未提交 `src/application/importing/referenced/errors.py` 保留现场，由续跑者检查后使用或重建。 | 本卡 Appointment/变更记录；ZCode session 日志 |
| 2026-11-03 | **Phase B 交付**：ZCode 恢复额度后完成 referenced 导入编排（五类输入/plan/异步状态机/密码短期引用），commit `ceae03edb`；DSH 用 `git stash` 隔离 Phase C 半成品后干净验证 `tests/fea09` **69 passed**。随后 ZCode 触发 5 小时额度（23:41 重置）。 | `G:\CODEX\New Manga.workspace\FEA-09\phase-b-int-verify.log`；commit `ceae03edb` |
| 2026-11-03 | **Phase C 半成品保留**：工作树 uncommitted `core_assembly.py`/`core_service.py` 改动 + `source_read_refs.py`/`test_referenced_wire.py`（ZCode 中断现场，已验证 stash/pop 可恢复）；由 Codex 20:42 续跑检查后继续或重写。 | git status；本卡 Appointment |
| 2026-11-03 | **续跑计划**：Codex 20:40 额度恢复；已建 20:42 schedule 提醒派发 `codex-impl-r2-prompt.md`（Phase C–D：授权 wire/cache/回退开关/证据/门禁）。 | schedule `schedule-53890cec`；Task 卡 |

## Codex Phase C–D 本轮检查点（2026-11-03）

- 恢复通路：Node `child_process`/`fs`；HEAD 实测 `f9a2fa8e077f21c93131237171a32e85f6942200`、branch=main；保留并接续四份 Phase C 半成品。
- owner=`codex（DSH 2026-11-03 额度恢复后续跑）`；本轮认领时间 2026-11-03T13:09:27.842Z。Phase A/B 作者仍为 ZCode，commits `d3d7cd564` / `ceae03edb`，未改历史署名。
- Host Registry/命令、Core grant/strict lease、WireLog 脱敏、缓存组件和回退开关已有工作树实现；不表示 Phase C–D 完成。
- `git add` EXIT 128：`.git/index.lock Permission denied`。本轮没有 commit、没有 push；delivery_head 留 null，integration_commit 留 null。
- 当前 Handoff：[FEA-09-f9a2fa8e0](../handoffs/FEA-09-f9a2fa8e0.md)。逐文件工作树 SHA-256/EV：[EV](../../verification/FEA-09/EV.md)，commit pin 待真正提交后补齐；canonical_evidence_status 保持 pending。
- 原始失败与实际命令见 `verification/FEA-09/logs/`。完整 pytest/真实 IPC/V2/独立 Review/DSH 集成均不宣称 PASS。

## DSH 集成修复检查点（2026-11-03 21:35）

- Codex 工作树无法执行 `git add`（受限进程 `.git/index.lock` Permission denied）；DSH 主会话接手 Git 与环境验证，**不丢失** Codex 已写实现。
- DSH 修复（集成适配，均为冻结协议/环境的必要同步）：
  1. `scanner.py`：移除 application→infrastructure 动态 import，改为 **`install_verified_reader` 端口注入**；`source_strict_read.py` 提供 `read_verified_bytes`；`core_assembly.py` 与 `tests/fea09/conftest.py` 注入。
  2. `tests/core/test_bootstrap.py`：fake `MigrationRunner` 接受 C-15 新增 `validate` 注入。
  3. `tests/core/test_core_service.py`：capability/E2E 断言同步 C-16 新增 `source.read/1`。
  4. `SourceSecurity.PrivateDirectory`：先 `SetOwner(当前用户)` 再校验 owner（修复 repo 内证据目录继承 Administrators owner 导致的误拒），并保留仅当前用户 ACE 校验。
- DSH 实际验证：`pytest tests/fea09` **92 passed**；`pytest tests/core/test_architecture.py tests/core/test_bootstrap.py tests/core/test_core_service.py` **EXIT 0**；`Host.SourceRegistryTests` **2 passed**；`dotnet build` **0 warning/0 error**；全量 .NET 复跑见 `G:\CODEX\New Manga.workspace\FEA-09\dotnet-dsh-full-r2.log`。
- 范围：工作树变更全部落在 `allowed_paths`；冻结契约/共享组合根/UI/依赖未改。待全量绿后由 DSH 提交阶段 commit（实现者署名 Codex/ZCode；DSH 仅集成修复与提交）。
- 仍未完成：生产 rendition 读取接线、密码完整链路、真实 IPC/V2 证据、AC-1…AC-10 部分验证、独立 impl Review；Task 保持 `in_progress`。
- 下一精确动作：DSH 处理 Git 元数据、外置 task tmp、Windows DPAPI/ACL 与测试 fixture 权限；Codex 恢复后先核对 dirty 指纹，再完成 Host 密码引用与四维读取 scope→binding/rendition/生产 adapter 接线，重跑全部测试，分阶段提交。禁止改 UI/冻结契约/共享组合根/依赖/push。
| 2026-11-03 | **Phase C/D 阶段提交 + DSH 集成修复**：Codex（Node 通路）完成 Host Registry/grant、strict read、WireLog 脱敏、rendition cache、回退开关；DSH 修复 6 项适配并提交 995d80ca5。验证：.NET **1298/0/57**、pytest fea09 **92 passed**、fea09+import_formats+storage **245 passed**、build 0/0、check PASS、pins 17/17。AC 仍 PARTIAL/BLOCKED，不宣称完成。 | `995d80ca5` 阶段 commit；`verification/FEA-09/logs/dsh-integration.md`；`doc/handoffs/FEA-09-995d80ca5.md` |
| 2026-11-03 | **referenced 生产 resolve 增量（DSH）**：SourceReadGrantRegistry.find_for_source + 
eader.render_entry_png + 
esolve.resolve_referenced_rendition + core_service referenced 分支发布 rendition（确定性 key、幂等、typed 失败、无 raw/无任意路径）；新增 4 测试；pytest tests/fea09 **96 passed**、check PASS、pins 17/17。AC-6/AC-7 仅部分推进，不标 MET。 | 
erification/FEA-09/logs/dsh-referenced-resolve.log；	ests/fea09/test_referenced_resolve.py |
| 2026-11-03 | **密码链路 + rendition cache/预算（DSH）**：生产 Runtime 注入 `read_secret`；`reader._check_decode_budget`；`resolve` cache 元数据；`library.upsert_rendition_cache` + core resolve 写 cache 行；新增 cache/预算测试。`pytest tests/fea09` **98 passed**、check PASS、pins 17/17。 | `verification/FEA-09/logs/dsh-referenced-resolve.log`；`tests/fea09/test_referenced_resolve.py` |
| 2026-11-03 | **AC-6 真实 Host↔Core IPC（DSH）**：新增 Host.Tests Fea09RealIpcTests（真实 stdio Python Core + 生产 CoreServiceClient/Host coordinators）；物理身份 grant 回退；NEWMANGA_FEA09_IPC=1 下 **1 passed**（16 frames、receipt completed、rendition 发布）；默认全量自跳过（53/29）。证据 
erification/FEA-09/ipc/。 | `verification/FEA-09/logs/dsh-real-ipc.log` |
## Implementation Review r1 处置（DSH，2026-11-03）

报告：`doc/reviews/FEA-09-impl-r1.md`（23,071 B，SHA-256 `7e6f4b787a41e6493c98ac708e5ef305669a318fc823c193fe0a1984a6ed3a82`，reviewed_head `6a164253d`；reviewer session `01a1a1b4-5bda-7940-bc48-7aedfdd589b0`；未参与实现）。结论：**changes_requested，P0=0 / P1=8 / P2=3**。全部 findings **接受**；在返修并经新的独立复核前不得 done，AC 不标 MET。

| ID | 级别 | DSH 处置 | 批次 |
|---|---|---|---|
| R1-I001 | P1 | **FIXED（实现完成，待独立实现复核）**：UNFREEZE B 已重冻（C-05 v1.2/C-15 v1.1，pins 17/17）；实现 managed `V=V_artifact∨V_copy_original` SQL、`PageView` 只读投影、`get/list` 不丢 V 行、managed resolve 资源选择、迁移 union 断言/同事务 get-list-纯投影三路径/非空强制 verifier；测试 `tests/fea09/test_i001_managed_visibility.py`（11）+ `test_v7_migration.py`（+2）；Python 套件全绿 | 批次 4 |
| R1-I002 | P1 | **FIXED 批次 1**：Core 记录 grant→(source,version,entry) 绑定，resolve 只认绑定匹配且 live 的 grant；删除物理身份回退；新增负测 | 批次 1 |
| R1-I007 | P1 | **FIXED（含 r1-rework P2）**：PDF page_size→预算→render；图片 header→预算→load；runtime probe 同序；预算拒绝=unsupported entry；hook decoder 零调用测试 | 批次 1 |
| R1-I009 | P2 | **FIXED 批次 1**：PlanRecord.book_id + start 复核项目/策略；负测 SOURCE_PLAN_STALE | 批次 1 |
| R1-I010 | P2 | **FIXED 批次 1**：SourceProjectMismatch→SOURCE_PROJECT_MISMATCH typed reason，保留 failed_sources/pending_pages；测试断言 | 批次 1 |
| R1-I003 | P1 | **FIXED 批次 2**：整源 skip 仅当 `will_import==0`；部分已绑定逐 entry 补齐；3 页 zip 中断后重试 imported=2/skipped=1 | 批次 2 |
| R1-I004 | P1 | **FIXED 批次 2**：真加密 PDF（R2/RC4）无密/错密/正确密码；解密 rescan participants；修复 pdfium bytes 密码 TypeError 误分类 | 批次 2 |
| R1-I006 | P1 | **FIXED 批次 2**：Core grant 绑定对 folder 生效；`test_folder_import_resolves_through_bound_grant` 通过（无路径回退） | 批次 2 |
| R1-I005 | P1 | **CLOSED（返修后）**：Core `source.resolve-secret/1` + `claim_secret_for_binding`（0/1/多/重放/路径/TTL/DPAPI/一次性）+ cache-miss 消费 + **PDF raster 密码接线**（DocumentRaster.open 增 password；pdfium 传 str；ENCRYPTED→REQUIRED/INVALID）；Host `SourceReadCoordinator` fresh-grant + `SourceSecretStore` DPAPI + `HostRuntime` 重试/清理；测试：zip 2+8、PDF e2e 2、Host 2；独立复核 r1-rework P1 已修 | 批次 5 + 返修 |
| R1-I008 | P1 | **FIXED 批次 3a**：生产 resolve 先走 RenditionCache（key/预算/LRU/active/崩溃校验/digest），metadata=`source-renditions/`，命中不重复解码，损坏自动重建；集成测试覆盖 | 批次 3 |
| R1-I011 | P2 | **FIXED**：旧台账归档 `history/EV-2026-11-03.md`；`tools/rebuild_ev.py` 从 git ls-files 生成 57 行唯一 ID/0 PENDING 台账；合成目录去跟踪+gitignore；历史缺失 50 条单列 | closeout |

**批次 1 完成后**：pytest/check/pins + 定向 real IPC 复跑；**全部批次完成后**：新的独立实现复核（不得由本会话自审）→ DSH 最终集成。
| 2026-11-03 | **实现 Review r1 批次 1 返修（DSH）**：I002 grant 四维绑定（ind_imported_entry/
ind_bound_for_source，删除身份回退）、I007 解码预算前置、I009 plan 项目/策略绑定、I010 typed 存储原因；I001 经 Codex 独立裁决选 **B（UNFREEZE 前置）**，归档 doc/reviews/FEA-09-I001-adjudication.md。pytest tests/fea09 **103 passed**；library 63/import_formats 32/m2rc 110/core_service 6 PASS；真实 IPC 1 passed。 | `verification/FEA-09/logs/dsh-review-batch1.log` |
| 2026-11-03 | **实现 Review r1 批次 2 返修（DSH）**：I003 部分重试逐页补齐、I004 真加密 PDF（含 pdfium 密码编码修复）、I006 folder resolve 绑定生效。pytest tests/fea09 **106 passed**；library/reading_export/import_formats/p09 全 PASS；真实 IPC 1 passed。 | `verification/FEA-09/logs/dsh-review-batch2.log` |
| 2026-11-03 | **实现 Review r1 批次 3a：R1-I008**（DSH）：resolve 拆分 prepare/render；生产装配 RenditionCache（derived_root 尊重 M2RC1_DERIVED_ROOT）；命中不解码、metadata source-renditions/、损坏重建。pytest tests/fea09 **107 passed**；m2rc 110/core_service 6/library+reading 204 PASS；真实 IPC 1 passed。 | `verification/FEA-09/logs/dsh-review-batch3a.log` |
## UNFREEZE 修订（I001 + I005，2026-11-04）— **r15 approved，待语义提交与重冻**

- 提案链 r1–r15（`doc/reviews/FEA-09-UNFREEZE-r*-amendments.md`）；复核链 r1–r15（`doc/reviews/FEA-09-UNFREEZE-r*-review.md`）全部原字节归档。
- **r15 结论：approved，P0=0/P1=0/P2=1**（P2 为 r14 review 归档缺失，已补）。reviewer：Codex 独立会话（r1–r14）/ **ZCode 独立会话**（r15；Codex 额度耗尽，按用户长期授权故障转移，session `sess_1f1d2a34-8d15-4e48-add5-5b32af8ff1a3`）。reviewed_head `a7f636300`。
- 最终最小包（无 wire/DTO 变更）：C-05 v1.2（managed `V_artifact ∨ V_copy_original`、witness 独立、V/R 分离）、C-15 v1.1（正尺寸迁移基线、断言 1/2/3/5、V 行可观察与 artifact-only 只读投影最低字段、reader 跳过/恢复规则）、C-16 v1.1（`source.resolve-secret/1`、Host fresh-grant 协议、无 payload token、一次性/路径/清理/零泄漏、撤销码修正）。
- **M2-C1 无字节变更**（冻结时登记版本/指纹/no-diff/行为兼容依据）。
- 实现设计委托：`doc/handoffs/FEA-09-impl-design-I001-I005.md`（内部算法/端口/状态机/DTO 映射；由实现 Review 校验）。
- **下一步**：语义修订提交 → 三指纹/old-new blob → 已提交字节独立复核 → 仅元数据重冻；冻结后释放 I001/I005 实现。
- 记录：`verification/FEA-09/logs/dsh-unfreeze-chain.log`。
## UNFREEZE 修订单已重冻（2026-11-04）

- **语义修订**：`ed570681b`（C-05 v1.2/C-15 v1.1/C-16 v1.1）+ `a9276fbae`（C-15 §4.2 reader 恢复算法/offset 规范引用 + 版本引用补正）。
- **复核**：UNFREEZE r15 approved（ZCode 故障转移）；已提交字节独立复核 ZCode `sess_1517188b…`（P1×1/P2×1）→ 补正 → `sess_f155bf21…` **approved P0/P1/P2=0**。
- **重冻**：`CONTRACT-UNFREEZE-2026-11-04.md`；FROZEN 记录 C05 v1.2 / C15 v1.1 / C16 v1.1；新 pin `f6e6f3cb…` / `d8c0a3bc…` / `0b9511a5…`；旧 pin/载体/Review 原字节保留；`verify_pins` **17/17 PASS**。
- **M2-C1 无字节变更**（单独登记，不并入 17 pin）。
- **实现释放**：R1-I001（C-05 v1.2/C-15 v1.1）与 R1-I005（C-16 v1.1）现可实施；实现须以契约不变量 + impl-design + 测试矩阵为准，完成后需新的独立实现复核 + DSH 集成。**I001/I005 仍为返修项，Task 不得 done。**
## 债务候选（DSH 裁决，2026-11-04）

| ID | 内容 | 裁决 | 跟踪 |
|---|---|---|---|
| DEBT-FEA09-01 | RenditionCache 装配失败仅日志并置 None，resolve 静默降级 legacy 无预算/LRU/并发约束路径（`core_service.py` 装配处） | 不影响契约安全（加密源 legacy 仍 typed REQUIRED）；本轮不修，登记债务 | 建议后续 FEA 前端/资源通道 Task 收敛为 fail-closed 或 typed 降级能力 |

## 返修批次记录（2026-11-04）

| 批次 | commit | 内容 |
|---|---|---|
| I005 Host | `59ad0b9fe` | Host fresh-grant/DPAPI 一次性 token/ReadPageImage 密码重试 |
| I011 | `bc90b467f` | EV 收敛：唯一 ID/0 PENDING/旧台账归档/合成目录去跟踪 |
| r1-rework P1 | `de7732368` | PDF resolve 密码接线、DocumentRaster password/page_size 端口、解压预算、PageView 重复属性、加密 PDF e2e、I009 book 改挂负测 |
## Closeout（2026-11-04，DSH）

- **状态**：`done`。集成验证 head `87ca5070…`；独立实现复核最终 **approved**（`doc/reviews/FEA-09-impl-r1-rework-r2.md`，P0=0/P1=0/P2=2，均为 closeout 前置并已闭合）。
- **AC**：AC-1…AC-10 全部 **MET**，逐项证据见 `verification/FEA-09/AC-MATRIX.md`。
- **门禁**：build 0/0；.NET **1300 passed/0 failed**；Python fea09 **142**、core **897**、storage **121**、m2 **110**、reading **141**、import_formats **32**、infra **91**；`check` PASS、`verify_pins` **17/17**；真实 stdio IPC 1 passed（17 frames，生产 V2 adapter）。
- **Canonical evidence**：`complete`（I011 收敛：唯一 ID、0 PENDING、旧台账归档、合成目录去跟踪；`tools/rebuild_ev.py` 可重建）。
- **Resource closeout**：`complete`。本 Task 无独立 worktree/task-env/dataset/外部 artifact；测试临时目录在 `G:\CODEX\New Manga.workspace\FEA-09\`（非版本化，保留供追溯）；合成组件目录已去跟踪并 gitignore；无用户数据/独有提交丢失。**PRESERVE_UNKNOWN**：无；**DELETE_SAFE**：无需要删除的版本化资源。
- **限制（如实登记）**：加密源 Host↔Core 跨进程 IPC 未单列（Core 侧真加密实现与 Host 协议单测已覆盖，见 AC-MATRIX「限制」）；UI 接线归 `FEA-09-UI-1`；DEBT-FEA09-01 已登记。
- **未 push**；历史 Review/EV/契约 pin 原字节保留。
