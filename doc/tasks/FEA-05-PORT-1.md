---
id: FEA-05-PORT-1
title: Draft 端口面（IHostController + CoreClient registry + Region 契约 UNFREEZE）
kind: implementation
governance_version: 3
status: done
approval: scope_review_r4_approved_2026-11-02; impl_review_r3_approved_2026-11-02
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-05-WIRE-1
base_commit: 9ff2f7eac
branch: null
worktree: null
integration_commit: 24600bbee
delivery_head: 24600bbee
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-05-PORT-1
allowed_paths:
  - doc/tasks/FEA-05-PORT-1.md
  - doc/contracts/V11R_REGION_WRITE_CONTRACT.md
  - doc/plan/FEA-C07_API_INVENTORY.md
  - doc/plan/FEA-CONTRACT-FROZEN-C07.md
  - doc/reviews/CONTRACT-UNFREEZE-*.md
  - doc/plan/FEA-CONTRACT-FROZEN-C*.md
  - apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/**
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - verification/FEA-05-PORT-1/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-05-PORT-1-*.md
---

# FEA-05-PORT-1：Draft 端口面（IHostController + CoreClient registry + Region 契约 UNFREEZE）

## 来源与授权链

- FEA-05-WIRE-1（已 done，`d9d7dde41`）交付 Core 命令面 + 契约；其 W-6 明确把「端口面 + CoreClient registry + Region 不变式」留给本卡。
- 方案 §15.2（Fluent 独立 frontend）/§15.6；C-02 V-08b（KeyMap 无关）；C-07（端口清单 = `generate_api_inventory.py`）。
- 上游冻结契约：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md`（FROZEN v1.5）——本卡需 UNFREEZE 到 v1.6。

## 前置

- FEA-05-WIRE-1 已 done（`d9d7dde41`）；`FEA-05_DRAFT_WIRE_CONTRACT.md` 与 §8.2 仍为 `PENDING`——本卡完成后由 DSH 一并升级状态（不含在写域或单列）。
- `FEA-04b`（in_review）与本卡无写域重叠；`FEA-06`（Fluent UI）须等本卡与设计基线 AC5 用户确认。

## 任务拆解

| 项 | 内容 | 依赖 |
|---|---|---|
| P1 契约 UNFREEZE | `V11R_REGION_WRITE_CONTRACT.md` v1.5 → v1.6，**5 处更新站点**：① 头部状态/版本；② §命令清册加 `DraftsCommandNames`（6）；③ 不变式改「追加集 = RegionWrite ∪ RegionRead ∪ Drafts」；④ §8 验证表（`:457`）同改；⑤ 变更记录 v1.6 行 | 无 |
| P2 端口面 | 以下 **7 个方法**（C082 双模式拆两个，均发 `drafts_status`）：`Task<DraftLease?> OpenDraftAsync(string sessionId, string pageId, string? regionId, string? baseRevisionId, int pageBindingVersion, CancellationToken)`；`Task<Draft?> PatchDraftAsync(string draftId, string sessionId, DraftPatchRequest patch, int? undoCursor, CancellationToken)`；`Task<RegionCandidate?> PrepareCandidateAsync(string regionId, DraftPatchRequest patch, string origin, string? draftId, string? baseRevisionId, CancellationToken)`；`Task<IReadOnlyDictionary<string,string>> ApplyCandidatesAsync(EditToken token, IReadOnlyList<string> candidateIds, CancellationToken)`；`Task<Draft?> GetDraftAsync(string draftId, CancellationToken)`；`Task<IReadOnlyList<Draft>> ListDraftsAsync(string sessionId, CancellationToken)`；`Task DiscardDraftAsync(string draftId, string sessionId, CancellationToken)`。DTO 归属 `NewManga.CoreClient/Commands/DraftCommands.cs`（`Draft`/`DraftLease`/`DraftPatchRequest`/`EditToken`/`RegionCandidate`（`DraftPatchRequest` 避免与 `NewManga.ApplicationCore/DraftBuffer.cs:21` 的 `DraftPatch` 同名） 强类型，非 JsonElement）。`HostController` 经 `HostCommandDispatcher` 调用并映射；`NullHostController` 逐方法安全默认（不抛异常，遵守其 "never throws" 契约）：Open→`Task.FromResult<DraftLease?>(null)`、Patch/Prepare→`null`、Apply→空字典、Get→`null`、List→`Array.Empty<Draft>()`、Discard→`Task.CompletedTask`；`IHostController` 侧注明 null 语义。dispatcher 增加显式校验 case（`default` 不静默透传未知 Draft 命令）。 | P1 |
| P3 CoreClient registry | `HostCommandModel` 6 条；`HostCommandRegistry`：`DraftsCommandNames`（6 新集合）+ `V11RAdditiveCommandNames` 11→17 + `All`（既有 registry 字典聚合属性，含 6 条新命令）+ `HostCommandDomain` 枚举加 `Drafts` + `CoreBindings`（6 条：`drafts_*` → 同名 core 命令、minor 3）+ `AddDomain` 注册；`HostCommandDispatcher` 显式 case（`drafts_status` 的 draftId/sessionId XOR 校验） | P1 |
| P4 契约测试更新 | `RegionWriteCommandTests`：`:109` 改 `V11RAdditiveCommandNames`（17）且 `:110-114` 改为「RegionWrite ∪ RegionRead ⊆ additive」子集断言；补 `DraftsCommandNames ⊆ additive`；测试类注释/测试名同步（`CommandParityContractTests` 派生断言自动成立） | P2/P3 |
| P5 端口清单 | 手工更新 `FEA-C07_API_INVENTORY.md`（脚本只 print，不生成）→ `generate_api_inventory.py --check` EXIT 0 | P2 |
| P6 冻结记录 | `CONTRACT-UNFREEZE-2026-11-xx`（两份冻结物）；C-07 pin 重算写入 `FEA-CONTRACT-FROZEN-C07.md`；`verify_pins` 15/15；**独立复核**（`FROZEN-C07:17`） | P1 |

## 验收标准

- [x] **AC1 契约 UNFREEZE（两个冻结物）**：① `V11R_REGION_WRITE_CONTRACT.md` v1.5→v1.6（不变式改并集 + `DraftsCommandNames` 6 + 变更记录）；② `doc/reviews/CONTRACT-UNFREEZE-2026-11-xx.md` 记录（两份冻结物的理由/影响；Region 契约**无 pin**，仅 C-07 重算 pin）；③ C-07 库存 `FEA-C07_API_INVENTORY.md` 更新（现网 IHostController **47**、合计 **54** → 加 7 方法后 **54**、合计 **61**；成员表 +7、变更类别 11→18、生成日期/HEAD 刷新）并**重算 C-07 pin**（写入 `FEA-CONTRACT-FROZEN-C07.md`）；④ 按 `FROZEN-C07:17` 派**独立复核**（本卡实现完成后）；⑤ `verify_pins.ps1` **15/15**（pin 数量不变）。<<MET>>
- [x] **AC2 端口面**：`IHostController` **7 方法**（Open/Patch/Prepare 三个返回可空：`Task<DraftLease?>`/`Task<Draft?>`/`Task<RegionCandidate?>`；Get/List/Discard 见 P2 表；C082 双模式拆 `GetDraftAsync`/`ListDraftsAsync` 共发 `drafts_status`）+ 实现 + Null 默认；`App.Tests` 覆盖（fake/failure 路径）；既有方法不回归。<<MET>>
- [x] **AC3 CoreClient registry**：6 条模型/注册/路由；`V11RAdditiveCommandNames` = 17；`CommandParityContractTests` 通过。<<MET>>
- [x] **AC4 契约测试**：`RegionWriteCommandTests` 改为并集断言且 Region 子集仍成立；`CommandContractV11RTests` 通过。<<MET>>
- [x] **AC5 端口清单**：`generate_api_inventory.py --check` EXIT 0（人工清单与代码一致；脚本只 print 不生成）。<<MET>>
- [x] **AC6 回归**：全量 `dotnet build` + `dotnet test ... --no-build --settings .../NewManga.runsettings` 不退化（基线 931/0/60）。<<MET>>
- [x] **AC7 证据**：`verification/FEA-05-PORT-1/**` 原始日志 + 证据表。<<MET>>

## 禁止范围

- 不改 Core handler/契约 §8.2（FEA-05-WIRE-1 已交付）；不改 UI 行为/页面；不改 schema；不动用户数据；不 push；不合并 main（本卡直接 main 实现，由 DSH 提交）。
- 不把 Draft 命令接入 UI 交互（FEA-06 负责）。

## 附加裁决点（DSH 已裁）

| # | 问题 | 裁决 | 依据 |
|---|---|---|---|
| W-1 | 是否必须 UNFREEZE Region 契约？ | **是**：不变式（追加集 = RegionWrite ∪ RegionRead）与新家族冲突，只能改契约；走 v1.6 + UNFREEZE 记录 + 新 pin | FEA-05-WIRE-1 impl-r4 复核发现（`RegionWriteCommandTests:107-117` vs 契约 `:62-63/344-346/457`） |
| W-2 | 端口方法名 | **7 个**：`OpenDraftAsync`/`PatchDraftAsync`/`PrepareCandidateAsync`/`ApplyCandidatesAsync`/`GetDraftAsync`/`ListDraftsAsync`/`DiscardDraftAsync`；C082 双模式由 `GetDraftAsync`（draftId）与 `ListDraftsAsync`（sessionId）分别调用同一 `drafts_status` 命令（XOR 参数） | 与 `IHostController` 既有命名风格一致 |
| W-3 | `V11RAdditiveCommandNames` 语义 | 扩为 17（RegionWrite 10 + RegionRead 1 + Drafts 6）；新增 `DraftsCommandNames`（6）；`RegionWriteCommandNames`/`RegionReadCommandNames` 保持原集合 | 契约 v1.6 的并集定义 |
| W-4 | 证据与冻结 | 卡内产出 UNFREEZE 记录（两份冻结物）+ 契约 v1.6 + C-07 pin 重算；DSH 复核后提交；`verify_pins` 必须 15/15（pin 数量不变，C-07 值更新） | 契约冻结纪律；`FROZEN-C07:17` 独立复核 |

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `verify_pins.ps1` + 契约 diff | 治理 | NOT_RUN | 待补 |
| AC2/AC3/AC4 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests` + `NewManga.CoreClient.Tests` | .NET | NOT_RUN | 待补 |
| AC5 | `python tools/governance/generate_api_inventory.py --check` | 治理 | NOT_RUN | 待补 |
| AC6 | `dotnet build apps/desktop-avalonia/NewManga.sln` EXIT=0 + `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings`：既有用例不退化（基线 931/0/60），新增 App.Tests/CoreClient 用例数单独记录 | 全量 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-FEA05P-UNFREEZE | AC1 | `doc/reviews/CONTRACT-UNFREEZE-2026-11-02.md` | `24600bbee` | `100fb2abfd2aa539b4f58cc6fa79a310efe7b5611082d86c5fe1986201e51d1e` | CANONICAL |
| E-FEA05P-REGION-V16 | AC1 | `doc/contracts/V11R_REGION_WRITE_CONTRACT.md` | `24600bbee` | `007d443db178dc958d05bd50aee33eb3e2f5aed9552c0574f5f73cf0be3f4205` | CANONICAL |
| E-FEA05P-C07 | AC1/AC5 | `doc/plan/FEA-C07_API_INVENTORY.md` | `24600bbee` | `3fdb44e49afe9fb25e715c5a41bd247cee269c194d045e1f79946f25067dd714` | CANONICAL |
| E-FEA05P-FROZEN-C07 | AC1 | `doc/plan/FEA-CONTRACT-FROZEN-C07.md` | `24600bbee` | `5460395aadbdc88db2d7c454e73ec8d3e7961791b777f30a79281ebc5e57ba4c` | CANONICAL |
| E-FEA05P-REGISTRY | AC3 | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs` | `24600bbee` | `9dd194279bc6903ea55eee060085cbbe1f2792ae91e095bcd8a96d21f14938f1` | CANONICAL |
| E-FEA05P-PORTS | AC2 | `apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs` + `HostController.cs` + `NullHostController.cs` | `24600bbee` | `82c78323f571fe9a882f042ab3826b1c2b41d9fb55dddc010ffbe039e2e89cc1` / `faa9d540a780b986ee9bf8a825ed0cbf29a1a09510191156531e2a1189d33d0d` / `41c1059e625c277d169b93811a89aa0153f442aeb4c71dea8e7015710d884ab9` | CANONICAL |
| E-FEA05P-TESTS | AC2/AC4 | `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/DraftCommandRegistryTests.cs` + `NewManga.App.Tests/DraftPortDefaultTests.cs` | `24600bbee` | `4df7999b0bb23321b9a808a01d1eb965a35f4eb5c5a689334da0b444c23f8486` / `338e002dd9d5e2bec45948d28e5499075a79219ed261a0d594625aa9b3401c0d` | CANONICAL |
| E-FEA05P-SLN | AC6 | `verification/FEA-05-PORT-1/sln-test.log` | `24600bbee` | `f303d1cd231d5d92745252d9b8eed3f92c186509edcc3fc41575cba2c3a4397f` | CANONICAL |

## Resource Manifest

无 worktree（main 直接实现）；资源处置在收口时登记。

## 备注（收口时 DSH 处理）

- 冻结矩阵（`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`）：**不随本卡更新**——矩阵只记录冻结状态、不承载 pin 值；C-07 重冻后仍为 `FROZEN`，内容无需变（P2-3 接受）。`FEA-05_DRAFT_WIRE_CONTRACT.md` 与 §8.2 状态：本卡 AC1 后由 DSH 一并把 `PENDING` → `FROZEN` 并在变更记录中注明（不在本卡写域外扩展）。
- STATUS/PLAN/LEDGER 指针：本卡完成后由 DSH 同步（`FEA-05-PORT-1` done）。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- 2026-11-02：范围复核 r1（P0×2/P1×1）→ r2（P0=0/P1×2）→ r3（P1×1）→ **r4 approved（P0/P1=0，P2×3 接受遗留）**；置 
eady，DSH 实现（Codex 通道故障）。
- 2026-11-02 / DSH：FEA-05-PORT-1 完成（24600bbee）——范围 r1–r4（r4 approved）、实现 impl-r1–r3（r3 approved，P0/P1=0，P2×11 接受）；UNFREEZE 两冻结物（Region 契约 v1.6、C-07 pin 3fdb44e4…）经独立复核通过；全量 sln **949/0/57**；erify_pins 15/15；置 done。
