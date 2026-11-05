---
id: FEA-12-PREREQ-1
title: FEA-12 删除/回收站 wire 契约注册（M2-C1 rev 2.13 + Host 投影/白名单 + 负向对照）
kind: implementation
governance_version: 3
status: changes_requested

approval: 用户 2026-11-05 指令（FEA-12 scope review → 冻结范围 → 实施）；范围冻结 ADJ-2026-11-05-FEA-12-SCOPE；C-04b `:99`/C-09 `:110-129` 明文要求"实现前独立字节修订 Task"；DSH 2026-11-05 释放；DSH 2026-11-05 窄批批准 2 个治理测试计数/声明派生文件（见卡内「DSH 裁决」）；r1 Review changes_requested（P1=1/P2=1/P3=4）→ r2 最小返修
suggested_owner: dsh（dsh-agent-team teammate `fea12-prereq-impl`）
owner: dsh-agent-team teammate `fea12-prereq-impl`（claimed 2026-11-05；r2 返修续作）
reviewer: 独立上下文 fresh subagent（r1 `doc/reviews/FEA-12-PREREQ-1-r1.md`，reviewer session `68898595-4d2b-46a7-8a72-0d4b6ba05db8`；未参与实现）
depends_on: []
base_commit: 035468a81e43e8d70fb711536824cdf613a7a0c4
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-12-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-12-PREREQ-1.md
  - doc/reviews/FEA-12-PREREQ-1-*.md
  - doc/handoffs/FEA-12-PREREQ-1-*.md
  - doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandWiringB1Tests.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandWiringB2Tests.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandParityContractTests.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs
  # DSH 2026-11-05 窄批：治理计数/声明派生（additive 命令集的必要同步；不放宽断言）
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/DraftCommandRegistryTests.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandContractV11RTests.cs
  - verification/FEA-12-PREREQ-1/**
out_of_scope:
  - 删除/回收站业务实现（归 FEA-12-CORE）
  - C-01b/C-04b/C-08/C-09/C-13/C-14/C-17/ADJ-001 冻结契约字节
  - src/bootstrap/core_service.py、src/** 任何 Python 生产代码（本卡只做契约与 .NET 投影）
  - 新 schema/migration/依赖/字体/模型
  - 真实用户数据/AppData/外部卷/回收站；push
---

# FEA-12-PREREQ-1：删除/回收站 wire 契约注册

## 来源与目标

- 来源：`doc/reviews/ADJ-2026-11-05-FEA-12-SCOPE.md`（范围冻结与 D1–D8 裁决）；`doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md` §2.0–§2.4；`doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md` SC-B06；`doc/plan/FEA-C14_SOURCE_RELOCATION_DRAFT.md` SC-S08；`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md` PD-01…PD-10；`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §5.11/§5.12/§11/§12。
- 目标：在**不写业务实现**的前提下，把 C-04b/C-09 已冻结、但尚未登记进 M2-C1 的 remove/trash wire 一次性 additive 登记，并同步 Host 投影/白名单，附负向对照。完成后 `FEA-12-CORE` 才能按冻结 wire 实现。
- 先例：`FEA-10-PREREQ-1`（M2-C1 rev 2.12，Codex 实现 / DSH 集成，`728c8bb0`）。

## Scope（冻结，见 ADJ §2.1/§D4）

### 1. M2-C1 rev 2.13（additive；只追加，不重写既有条款）

1. **§5 新只读命令** `PreviewPermanentDeleteBooks`：入参 `{ bookIds: BookId[1..20] }`（非空/去重/上限 20）；出参 `{ inventoryDigest, inventoryDigests{bookId→digest}, computedAt, items: DeletePreviewItem[] }`；`DeletePreviewItem` 按 C-04b `:43`（含 PD-01 三项强制：`protection.manualRegionCount`、`protection.draftPageCount`、`contentSummary.deletedFiles`+`deletedBytes`）；零副作用语义。**目标 wire minor = 11**（C-04b `:47`；文档 rev 2.13 ≠ wire minor）。
2. **删除命令 digest 扩展**：单条 `PermanentlyDeleteBook` 追加 `inventory_digest: string`；批量 `PermanentlyDeleteBooks` 追加集合级 `inventory_digest` + 逐书 `inventory_digests`；两级校验顺序 = 集合级（键集合与顺序）→ 逐书；缺失/格式错 → `INVALID_REQUEST`，不匹配 → `BOOK_DELETE_STALE_PREVIEW`；既有命令 wire minor 保持 10（additive 字段，旧 Host 不传即 fail-closed，不降级软删）。
3. **2 个删除新码**（C-04b §2.3）：`BOOK_DELETE_STALE_PREVIEW`（conflict/false）、`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`（unavailable/true）；§5.11.3 表两行 + 两个 `ErrorView.code` 封闭联合 + 批量 `items[].error_code` 白名单四处同步。
4. **回收站命令面**（C-09 SC-B06）：`MoveToTrash`/`RestoreFromTrash`/`ListTrash`/`PurgeTrash`（`PurgeTrash` 明确"委托 C-04b Preview+Delete，不是新删除路径"）；closed shape 与逐项 `moved/skipped/restored/conflicts`；**目标 wire minor = 13**（独立 family，不改默认 `PROTOCOL_MINOR=3`；不与 delete=10 / source-sync 族冲突）。`ListRecycleBinBooks` 保持 rev 2.11 原字节，`ListTrash` 关系按 C-09 `:118` 在实现 Task 确认，本卡只登记"并存、不冲突"。
5. **3 个 `TRASH_*` 码**（C-09 `:110-118`）：`TRASH_ENTRY_NOT_FOUND`（not_found/false）、`TRASH_RESTORE_CONFLICT`（conflict/false）、`TRASH_RESTORE_LAYER_MISMATCH`（conflict/false）。
6. **capability 名称（DSH 冻结）**：`library.delete.preview/1`、`library.trash.read/1`、`library.trash.write/1`；Host 先 probe，缺失 → `CORE_CAPABILITY_MISSING`；不得以 UNKNOWN_COMMAND 探测。
7. **§11 对账**（ADJ §D2）：`Permanent-delete user policy` 行状态改为 `FROZEN（用户 2026-10-18 裁决）`，引用 `P09-AC3-DELETE-1.md:84/87/106-109` 与本卡/ADJ 记录；不重写其他字节。
8. **§12 Release boundary additive**：登记 `FEA-12-PREREQ-1` 只授权文档/投影，`FEA-12-CORE` 由后续释放；显式写明本修订不授权 Core runtime。
9. **Revision history**：追加 rev 2.13 条目（日期/来源/范围/未实现声明）。

### 2. Host 投影/白名单（additive）

- `HostCommandRegistry`：登记 `PreviewPermanentDeleteBooks`（Core 名 → Host 映射，目标 wire 11）、`MoveToTrash`/`RestoreFromTrash`/`ListTrash`/`PurgeTrash`（目标 wire 13）、三个 capability 字符串；既有映射零改动。
- `HostCommandDispatcher`：新增命令的 closed-shape 校验与调用路径（键集严格、未知键拒绝）；既有单/批量删除 dispatch 不重写，只允许 additive 参数（digest）透传。
- `CoreServiceClient`：命令常量/注册表 additive 同步（不得改既有命令）。
- **负向对照（强制）**：在未扩 M2-C1 的基线（本卡改动前 head）上，新码/新命令必须被 Host 投影拒绝或降级：未知 code → `category=unknown` 且 **code 原文不改写**；旧 Core 不识别新命令 → `PROTOCOL_VERSION_UNSUPPORTED`/typed 失败，不得静默丢弃。负向对照日志入证据。

## Acceptance Criteria

- [ ] **AC1 M2-C1 rev 2.13 additive 文本**：§5/§5.11/§5.12/§11/§12/revision history 按 Scope 1–9 完整登记；`git diff` 证明只追加、不改既有条款字节（逐段 diff 证据）；文档 rev=2.13，默认 `PROTOCOL_MINOR` 不变。 <<PARTIAL: r1 Review R-001：9 项登记点 8/9，§5.11.3 表缺 BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE 行（契约内部二义）；其余 additive/无越权已核>>
- [x] **AC2 Host 投影 additive**：registry/dispatcher/client 新命令与 capability 注册；既有命令 wire/映射零语义改动；`CommandParityContractTests` 等治理测试同步且全绿。 <<MET>>
- [x] **AC3 负向对照**：在改动前 head 上复现"新码被降级 `category=unknown` 且 code 不改写 / 旧 Core 不识别新命令 fail-closed"，日志与命令入 `verification/FEA-12-PREREQ-1/`；证明 M2-C1 修订是必要前置。 <<MET>>
- [x] **AC4 治理门禁**：`verify_pins.ps1` **18/18**；`check.ps1` PASS；全量 .NET 实测（passed/failed/skipped 分列，首跑 flaky 需复跑并记录）；pytest 全量基线不变（本卡无 Python 改动，记录实测数字）。 <<MET>>
- [x] **AC5 交付件**：Task/Handoff、`verification/FEA-12-PREREQ-1/`（diff 证据、负向对照日志、门禁日志）、Canonical Evidence 表；不含未跑项冒充实测。 <<MET>>

## r1 Review 处置计划（DSH，2026-11-05；Review = changes_requested）

- Review：`doc/reviews/FEA-12-PREREQ-1-r1.md`（fresh subagent session `68898595-4d2b-46a7-8a72-0d4b6ba05db8`；reviewed_head `5a7c7e028`；P0=0/P1=1/P2=1/P3=4；AC1 PARTIAL，AC2–AC5 MET）。
- **R-001（P1，必须修）**：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §5.11.3 表缺 `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` 行（C-04b §2.4 `:97` 要求追加两行），导致表/白名单二义。修复：additive 追加一行（`unavailable` / `retryable=true`，零副作用、可显式重试、不得降级软删）+ `verification/FEA-12-PREREQ-1/tools/rev213-diff-audit.ps1` 增加「§5.11.3 表 code 集合 ⊇ 两个 ErrorView code 集合（含 5 个新码）」判别性断言（在 `5a7c7e028` 上必失败、修复后必通过）+ 重跑 AC-MATRIX/gates 记录。
- **R-002（P2，defer 到 CORE）**：`CORE_CAPABILITY_MISSING` 未进 delete/trash 白名单。本卡 DSH 裁决已明确运行时 probe 归 CORE；在 Handoff「风险」与 `FEA-12-CORE` 卡登记二选一集成要求（加入白名单或绕开 `ProjectDeleteTrashError`）+ 判别性测试。不在本卡改白名单。
- **R-003/R-004/R-005/R-006（P3，随 P1 同批修措辞/日志）**：check 警告数 4 vs 3 的 closeout 说明；§5.11.1a「Core closed shape 拒收 + Host legacy 透传」措辞澄清；B1/B2 负向对照注释改为「reconstructed pre-registration allow-list（新投影器减 5 码）」；基线日志 `existing=l` 笔误修正/标注。
- **复审**：r2 交付后另派 fresh subagent 复审（只审新 head；R-001 修复后 AC2–AC5 结论可延用除非实现变动）。

## 允许修改范围

frontmatter `allowed_paths` 为准；`evidence_dir` 已显式列入。**共享文件单写者**：本卡释放时 `FEA-11-HOST-AUTH-1` 已无在途 .NET 改动；若发现他人 dirty，停止并报 Lead。

## 禁止范围

见 `out_of_scope`。另：不改 C-04b/C-09/C-13/C-14/C-17/ADJ-001 正文；不写 Python 业务实现；不新建 schema/迁移/依赖；不碰真实数据/回收站；不 push；不得把 `skipped` 计入 passed；不得删测试/放宽断言制造通过。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `git diff --stat` + 逐段 diff 复核；`Select-String` 校验 rev 2.13 条目与 9 项登记点 | 仓库根；base=035468a81 | **PASS**：`165 insertions / 2 deletions`；仅文档状态行 + §11 policy 行两处已授权既有行变更，其余全插入；rev 2.13；`PROTOCOL_MINOR=3` 未变 | `logs/rev213-diff-audit.log`、`REGISTRATION-COMPARISON.md` |
| AC2/AC3 | `dotnet test .../NewManga.CoreClient.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~Command"`；负向对照脚本（base worktree 复核）；sidecar 定向 live 负向对照 | .NET 9；隔离 | **PASS**：命令治理测试 135/0/15；实测冻结 Core 负向对照 3/3（typed；旧 Core 返回 `UNKNOWN_COMMAND`/`INVALID_REQUEST`）；基线 5 新码→unknown 且 code 保留 | `logs/dotnet-full-2.log`、`logs/baseline-negative-control-base-035468a81.log`、`test-evidence/commands/fea12-old-core-negative-control.json` |
| AC4 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1`；`pwsh -NoProfile -File tools/governance/check.ps1`；`dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build`；`C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no` | 仓库根 | **PASS**：pins 18/18；check PASS；全量 .NET 首跑 1 flaky（跨程序集证据写竞争，单测复跑 1/1 通过）→ 复跑 **1403 passed / 0 failed / 79 skipped**；pytest **3073 passed / 10 skipped** | `logs/gates.log` |
| AC5 | 人工复核交付件完整性 | — | **PASS**：Task/Handoff/verification/Canonical Evidence 齐备；无未跑项冒充实测 | Handoff/Review |

## 依赖、风险与阻塞

- 硬依赖：无 Task 依赖；上游为已冻结 C-04b（`:99`）与 C-09（`:110-129`）。`FEA-12-CORE` 硬依赖本卡。
- 风险：①M2-C1 修订解释（ADJ §5.4）若被用户否决 → 立即停止；②C-04b 的 `DeletePreviewItem` 无 pending operation 字段（C-14 SC-S08）→ 本卡登记"待 DSH 单独裁决/后续 UNFREEZE"，不擅自加字段；③wire minor 11/13 若与未来分配冲突 → 由 Lead 裁决后改；④Host 投影白名单若治理测试按总数断言 → 需同步允许列表（属本卡 additive）。

## DSH 裁决与实施记录（2026-11-05）

### DSH 裁决（Lead，2026-11-05；实施前确认，Review 依据）

| # | 问题 | 裁决 | 落地位置 |
|---|---|---|---|
| 1 | C-09 SC-B06 只给 `TrashEntryRef`/`TrashEntryInfo` 名字、未定义结构 | **A 确认**：rev 2.13 冻结最小**作品级** DTO——`TrashEntryRef = {book_id}`（请求侧 snake；请求/结果共用同一 ref 形状）、`TrashEntryInfo = {bookId, title, deletedAt}`（结果侧 camel，文本已明确侧别惯例）；不定义页级/章节级 ref | M2-C1 §5.14 |
| 2 | `PurgeTrash` 与 C-04b digest 的绑定方式 | **A 确认 + 追加约束**：按 C-09 原字节登记 payload，**不得**擅自加 `inventory_digest`；**首版 FEA-12-CORE 不实现 `PurgeTrash`（仅登记命令面）**，实现前须由 DSH 就 digest 绑定方式（内联字段 vs 映射 `PermanentlyDeleteBooks`）另做 additive 修订/裁决；CORE 只做 UI 组合调用所需的 Preview+Delete | M2-C1 §5.14 / §11 新行 |
| 3 | capability gating 边界 | **A 确认**：本卡只做契约 + Host 常量/命令→能力映射；运行时 `core.ping` probe（缺失 → `CORE_CAPABILITY_MISSING`）归 CORE 卡。CORE 卡 allowed_paths 已由 Lead 补 `NewManga.Host/HostRuntime.cs` 与 `HostErrorCodes.cs`（与本卡识别一致，无其他 Host 文件需求） | `HostCommandRegistry.RequiredCapabilities` / `DeleteTrashCapabilities` |
| 4 | preview 入参字段名 | 确认按 C-04b `:41` 冻结字节用 camel `bookIds`；rev 2.13 文本显式说明"此处 camel 由冻结来源规定，与本契约请求侧 snake 惯例的差异不是笔误" | M2-C1 §5.13 |
| 5 | 2 个治理测试的窄批 | **批准**（见下「窄批登记」） | 卡 allowed_paths 两行窄批注记 |

### 窄批登记（DSH 2026-11-05）

- 批准文件（均属 `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/`）：
  - `DraftCommandRegistryTests.cs`
  - `CommandContractV11RTests.cs`
- **批准原因**：M2-C1 rev 2.13 向 `HostCommandRegistry.All` 追加 5 个 additive 命令；这两个治理测试以「registry − frozen 66 snapshot = additive 族并集」与「每个注册命令必须被权威声明」为严格派生断言，必须把新增的 `HostCommandRegistry.DeleteTrashCommandNames` 纳入派生输入。属 additive 命令集的**必要派生同步**，不是放宽治理。
- **条件与落实**：只做计数/声明同步；(a) `DraftCommandRegistryTests` 的硬编码 `40` 改为 `expected.Count` 派生（并集追加 DeleteTrash 族）；(b) `CommandContractV11RTests` 的 declared 集合追加 `DeleteTrashCommandNames`，保留 undeclared==0 的严格断言。未删测试、未改 skip、未放宽任何等式。
- **未修改则 2 fail 的证据**（实现后、窄批修改前实测；原始输出 `verification/FEA-12-PREREQ-1/logs/narrow-batch-before.log`）：
  - `CommandContractV11RTests.RegistrySurface_IsFullyDeclared_WithoutHardcodingTheTotal` → FAIL（5 个新命令 undeclared）
  - `DraftCommandRegistryTests.Additive_Set_IsTheUnionOfTheDeclaredFamilies` → FAIL（`Expected: 40 / Actual: 45`）
  - 该次运行汇总：`失败: 2，通过: 133，已跳过: 15，总计: 150`。

### 实施记录

- **M2-C1 rev 2.13**：additive 修订（`165 insertions / 2 deletions`；仅顶部状态行与 §11 `Permanent-delete user policy` 行两处既有行变更，其余全部为插入）。新增 §3.2 目标 wire bullet、§5 目录 5 行（preview + 4 trash）、§5.11.1a digest 两级确认、§5.11.3 两码两行 + items 白名单同步、§5.11.5 两个 ErrorView 纯插入扩值、§5.13、§5.14、§11 新行、§12 释放边界、Revision history 2.13。
- **Host 投影 additive**：
  - `HostCommandRegistry.cs`：5 命令注册（preview→`PreviewPermanentDeleteBooks` minor 11；`MoveToTrash`/`RestoreFromTrash`/`ListTrash`/`PurgeTrash`→ minor 13）、`DeleteTrashCommandNames`、`DeleteTrashCapabilities`（3 个 capability 名）、`RequiredCapabilities(name)` 命令→能力映射、`AllowedDeleteTrashErrorCodes`（20 码白名单）、`Fea12DeleteTrashErrorCodes`、`IsDeleteTrashCommand`。
  - `HostCommandDispatcher.cs`：新命令严格 closed-shape（未知键拒绝、`bookIds` 1..20 去重、`TrashEntryRef` 每项恰 `{book_id}`、`ListTrash` cursor/limit、`PurgeTrash` `confirm:true` 硬门）；既有单/批量删除仅 additive 透传 `inventory_digest`/`inventory_digests`（不生成、不补全）；新增 `ProjectDeleteTrashError`（未注册码 → `category=unknown` 且 code 原文不改写）。
  - `CoreServiceClient.cs`：`DeleteTrashWireTargets`（目标 wire 11/13 + 3 capability 常量）作为单一常量源，供 registry 引用。
- **测试**：`CommandWiringB1/B2/Parity/Integration` 同步；B1/B2 各含负向对照单测（用"注册前允许集"复现 unknown 降级）；Integration 新增 `[SidecarFact] Fea12NewCommands_FrozenCoreFailsClosedWithTypedError`（真实冻结 Core 负向对照）。
- **负向对照（AC3）**：基线双份证据 + 改动后 live 负向对照，见 AC3 行与 `verification/FEA-12-PREREQ-1/`。

## 交付与运行记录

- Handoff：`doc/handoffs/FEA-12-PREREQ-1-035468a81.md`（记录实现 commit 列表、门禁数字、负向对照、残余风险、Review 就绪声明）。
- Review：尚未（按纪律由 Lead 另派独立上下文 fresh subagent；本实现者不自审）。
- 实际测试：见「测试要求」表与 `verification/FEA-12-PREREQ-1/logs/gates.log`；关键数字：pins 18/18、check PASS、全量 .NET 复跑 1403 passed / 0 failed / 79 skipped、pytest 3073 passed / 10 skipped、命令治理测试 135/0/15、live 负向对照 3/3。
- 快照基线 worktree：`G:\CODEX\New Manga.workspace\task-envs\FEA-12-PREREQ-1\baseline-worktree-035468a81`（detached `035468a81`；保留不删，处置建议见 Handoff/Resource Manifest）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC1 | verification/FEA-12-PREREQ-1/logs/rev213-diff-audit.log | - | f5a5e6abd5876dc95716bee8862a83d4702974d753a8cc2f099081e607ecbded | CANONICAL |
| EV-02 | AC1 | doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md | - | 0dcfcfe81badc3496b1b5a0c8eb91a00f201b257233b3778067e8252342260c7 | CANONICAL |
| EV-03 | AC1/AC2 | verification/FEA-12-PREREQ-1/REGISTRATION-COMPARISON.md | - | ff5b7208dec84ac4408866fa1296dfc54b04db2504a96226c6a362a57c513ad3 | CANONICAL |
| EV-04 | AC2 | verification/FEA-12-PREREQ-1/logs/dotnet-full-2.log | - | 8c50b6ca0c96f567fffc762e83064d2a620388ff4194ee3b78073cf616ec36aa | CANONICAL |
| EV-05 | AC2 | verification/FEA-12-PREREQ-1/logs/narrow-batch-before.log | - | c9fa27919f3134c509f74b6c0224f79ba63bbc28b2ee2d2ccf332f943938611e | CANONICAL |
| EV-06 | AC3 | verification/FEA-12-PREREQ-1/logs/baseline-negative-control-base-035468a81.log | - | 9801667cb089ba98728e3c4813b7a24dd201fb0865bb43b26a70ba4fa628b015 | CANONICAL |
| EV-07 | AC3 | verification/FEA-12-PREREQ-1/logs/baseline-negative-control.log | - | a342ca71b5ad519916a8ed70b0b7c75ba48515ccced5c766a8feee819ce6128e | CANONICAL |
| EV-08 | AC3 | verification/FEA-12-PREREQ-1/test-evidence/commands/fea12-old-core-negative-control.json | - | ab817eacfac1c1504ce1d632237045985a2731ff40c3db9d84e3d3e6fbb9288b | CANONICAL |
| EV-09 | AC3 | verification/FEA-12-PREREQ-1/test-evidence/commands/ns-b1-integration.json | - | 5b7c9370f4681fb282b64ce2482b01a8828312f9a78807571859ada96d128d3c | CANONICAL |
| EV-10 | AC3 | verification/FEA-12-PREREQ-1/test-evidence/commands/ns-b2-integration.json | - | 5f8c3d1aa1c3f4d66de08a62d4739c093cbfedcc783b57d48445f989aa2a0438 | CANONICAL |
| EV-11 | AC4 | verification/FEA-12-PREREQ-1/logs/gates.log | - | 59fefefa34299abd76da7edbc36e0edfceba2506754fcdecbf21d9e6188e597b | CANONICAL |
| EV-12 | AC4 | verification/FEA-12-PREREQ-1/logs/pytest-full.log | - | bd9b762ddfaeac2d46c0dae91e73dcac5ccb4a83f5cc959f8bfcdc0df8a6fabb | CANONICAL |
| EV-13 | AC5 | verification/FEA-12-PREREQ-1/AC-MATRIX.md | - | 4e6ab4b9b992f8e66c29a60838a9efa312622809d1704b419bd0400cf5493d8a | CANONICAL |
| EV-14 | AC5 | verification/FEA-12-PREREQ-1/ENVIRONMENT.md | - | 0ae69389e2d560cc1d9884be1871967d4cf5442c353411d1d135582a383bad71 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | `G:\CODEX\New Manga.workspace\agent-output\fea12-prereq-impl\FEA-12-PREREQ-1\` | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\agent-output\fea12-prereq-impl\FEA-12-PREREQ-1\` | verification/FEA-12-PREREQ-1/agent-output-manifest.json | 逐文件 bytes+sha256 见 manifest（11 files：运行日志副本 + 探针脚本）；判别力证据以仓内 `verification/FEA-12-PREREQ-1/**` 为准；无需迁移。 |
| worktree | `G:\CODEX\New Manga.workspace\task-envs\FEA-12-PREREQ-1\baseline-worktree-035468a81` | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\task-envs\FEA-12-PREREQ-1\baseline-worktree-035468a81` | verification/FEA-12-PREREQ-1/agent-output-manifest.json | detached HEAD `035468a81`，用于 AC3 基线复现；**保留不删**（Lead 2026-11-05 指示）。处置建议：Review/集成完成后由 DSH 用普通 `git worktree remove`（工作树 clean、无独有提交）或归档；关闭前不得删除。 |
| temp | `G:\CODEX\New Manga.workspace\temp\FEA-12-PREREQ-1\` | DELETE_SAFE（交付后） | — | verification/FEA-12-PREREQ-1/agent-output-manifest.json | 仅基线 live Core 隔离数据根（`baseline-live-core`）与日志副本；仓内无临时文件。DSH closeout 时可直接删除。 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：STATUS / Plan / Task 导航已更新后填写。
