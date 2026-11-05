---
id: FEA-12-PREREQ-1
title: FEA-12 删除/回收站 wire 契约注册（M2-C1 rev 2.13 + Host 投影/白名单 + 负向对照）
kind: implementation
governance_version: 3
status: ready

approval: 用户 2026-11-05 指令（FEA-12 scope review → 冻结范围 → 实施）；范围冻结 ADJ-2026-11-05-FEA-12-SCOPE；C-04b `:99`/C-09 `:110-129` 明文要求"实现前独立字节修订 Task"；DSH 2026-11-05 释放
suggested_owner: dsh（dsh-agent-team teammate `fea12-prereq-impl`）
owner: null
reviewer: 独立上下文 fresh subagent（未参与实现；会话 id 记录在 Review 报告）
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

- [ ] **AC1 M2-C1 rev 2.13 additive 文本**：§5/§5.11/§5.12/§11/§12/revision history 按 Scope 1–9 完整登记；`git diff` 证明只追加、不改既有条款字节（逐段 diff 证据）；文档 rev=2.13，默认 `PROTOCOL_MINOR` 不变。
- [ ] **AC2 Host 投影 additive**：registry/dispatcher/client 新命令与 capability 注册；既有命令 wire/映射零语义改动；`CommandParityContractTests` 等治理测试同步且全绿。
- [ ] **AC3 负向对照**：在改动前 head 上复现"新码被降级 `category=unknown` 且 code 不改写 / 旧 Core 不识别新命令 fail-closed"，日志与命令入 `verification/FEA-12-PREREQ-1/`；证明 M2-C1 修订是必要前置。
- [ ] **AC4 治理门禁**：`verify_pins.ps1` **18/18**；`check.ps1` PASS；全量 .NET 实测（passed/failed/skipped 分列，首跑 flaky 需复跑并记录）；pytest 全量基线不变（本卡无 Python 改动，记录实测数字）。
- [ ] **AC5 交付件**：Task/Handoff、`verification/FEA-12-PREREQ-1/`（diff 证据、负向对照日志、门禁日志）、Canonical Evidence 表；不含未跑项冒充实测。

## 允许修改范围

frontmatter `allowed_paths` 为准；`evidence_dir` 已显式列入。**共享文件单写者**：本卡释放时 `FEA-11-HOST-AUTH-1` 已无在途 .NET 改动；若发现他人 dirty，停止并报 Lead。

## 禁止范围

见 `out_of_scope`。另：不改 C-04b/C-09/C-13/C-14/C-17/ADJ-001 正文；不写 Python 业务实现；不新建 schema/迁移/依赖；不碰真实数据/回收站；不 push；不得把 `skipped` 计入 passed；不得删测试/放宽断言制造通过。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `git diff --stat` + 逐段 diff 复核；`Select-String` 校验 rev 2.13 条目与 9 项登记点 | 仓库根；base=035468a81 | NOT_RUN | verification/FEA-12-PREREQ-1/ |
| AC2/AC3 | `dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~Command"`；负向对照脚本（旧 head 复核） | .NET 9；隔离 | NOT_RUN | 同上 |
| AC4 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1`；`pwsh -NoProfile -File tools/governance/check.ps1`；`dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build`；`C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no` | 仓库根 | NOT_RUN | logs/gates.log |
| AC5 | 人工复核交付件完整性 | — | NOT_RUN | Handoff/Review |

## 依赖、风险与阻塞

- 硬依赖：无 Task 依赖；上游为已冻结 C-04b（`:99`）与 C-09（`:110-129`）。`FEA-12-CORE` 硬依赖本卡。
- 风险：①M2-C1 修订解释（ADJ §5.4）若被用户否决 → 立即停止；②C-04b 的 `DeletePreviewItem` 无 pending operation 字段（C-14 SC-S08）→ 本卡登记"待 DSH 单独裁决/后续 UNFREEZE"，不擅自加字段；③wire minor 11/13 若与未来分配冲突 → 由 Lead 裁决后改；④Host 投影白名单若治理测试按总数断言 → 需同步允许列表（属本卡 additive）。
- 阻塞解除标准：本卡 Review approved + 集成后，`FEA-12-CORE` 才可 ready。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | `G:\CODEX\New Manga.workspace\agent-output\fea12-prereq-impl\FEA-12-PREREQ-1\` | PRESERVE_REFERENCED | 同上 | 待交付时填写 | 仅重复执行日志；判别力证据入 verification |
| worktree | NOT_APPLICABLE（在 main 工作树实施） | NOT_APPLICABLE | — | — | — |
| temp | 待交付时填写 | 待定 | — | — | 不得留仓库内临时文件 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：STATUS / Plan / Task 导航已更新后填写。
