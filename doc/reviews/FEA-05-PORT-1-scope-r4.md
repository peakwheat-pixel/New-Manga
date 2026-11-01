---
task_id: FEA-05-PORT-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: e77e1baf5
reviewed_head: 9ff2f7eac
decision: approved
counts: { P0: 0, P1: 0, P2: 3 }
---

# FEA-05-PORT-1 范围复核 r4（独立上下文，未参与本卡）

| 字段 | 值 |
|---|---|
| base_commit | `e77e1baf5de0513dc359946e7e681a7372847357`（范围 v3 被审 head） |
| reviewed_head | `9ff2f7eacef5513ca22db4eb7e6dcfca38e4022b`（`docs(fea-05-port-1): 范围 v4…`；`git status --porcelain` 为空） |
| 被审对象 | `doc/tasks/FEA-05-PORT-1.md`（115 行，status=proposed）；同提交收编 r3 报告 |
| reviewer | `fea05-wire-scope-reviewer`（Draft 线 FEA-05-WIRE-1 范围 r1–r7 与实现 impl-r1–r3 同一席位；**本卡未参与者**） |
| reviewer 来源 | DSH Team Lead 派发，**fresh 独立上下文**（DSH 子 agent）；只读被审 head，未 commit/push |
| 日期 | 2026-11-02 |
| 审查范围 | r3 的 P1×1 是否关闭、P2 逐条 disposition、AC1–AC7 可验收性、写域、新问题 |
| 结论 | **approved** |
| 计数 | **P0 = 0 / P1 = 0 / P2 = 3（3 条接受遗留，不阻断）** |

> **一句话结论**：**approved**。r3 唯一 P1 已真实关闭：`Open/Patch/Prepare` 返回类型改为 `Task<DraftLease?>`/`Task<Draft?>`/`Task<RegionCandidate?>`，与 `Nullable=enable` + `TreatWarningsAsErrors=true`（`Directory.Build.props:7/10`）及 Null 的 null 默认自洽；literal `\n` 归零、`## 备注`/`## Closeout Record` 结构恢复；AC1 ③ 数字（47→54、54→61）、AC1 ② pin 措辞、AC6 回归口径（测试要求 `:96`）均到位。写域两冻结物（Region 契约 v1.6 + C-07 pin/UNFREEZE 载体）齐全，AC1–AC7 全部可验收。仍有 3 条 P2 接受遗留（其中 2 条是 DSH 声称已修、但卡文本实际未落地的项——`All`/`CoreBindings` 细节与 DTO 字段清单；1 条是冻结矩阵「接受不更新」的理由不准确），均不影响范围冻结。

---

## 0. 方法与只读声明

- 只读核查被审 head；未修改被审文件、未 commit/push；**本报告是本轮唯一新增文件**。
- 已执行（只读）：

| 命令/检查 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain` | `9ff2f7eac…` / 空（clean） |
| `git diff --stat e77e1baf5..9ff2f7eac` | 2 files：卡（+15/−5 改写）、r3 报告（+118） |
| 卡原始字节自检 | literal `\n` = **0**、literal `\r` = **0**、stray CR = false、115 行 ✓ |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（3 warnings）**：10 非终态 Task；STATUS 3154/34（80%）；PLAN 3751/51（80%） |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS（all 15）** |
| `python tools/generate_api_inventory.py --check` | **EXIT 0**；渲染 `IHostController 47` / 合计 `54`（与 AC1 ③ 基线一致） |

---

## 1. r3 逐项 disposition

| r3 ID | 级别 | 状态 | 证据 |
|---|---|---|---|
| **r3-P1-01** nullability 矛盾 | P1 | **CLOSED** | `:59` 签名已改 `Task<DraftLease?> OpenDraftAsync(…)`、`Task<Draft?> PatchDraftAsync(…)`、`Task<RegionCandidate?> PrepareCandidateAsync(…)`；Null 默认（Open→`Task.FromResult<DraftLease?>(null)`、Patch/Prepare→null）与可空签名自洽，编译不再触发 CS8619；AC2（`:68`）已注明「Open/Patch/Prepare 三个返回可空」✓ |
| r3-P2-1 备注 literal `\n` | P2 | **CLOSED** | 全文 literal `\n` 计数 5 → **0**（自检）；`## 备注（收口时 DSH 处理）`（`:108`）、`## Closeout Record`（`:113`）恢复为真实标题，`## 前置`/`## 任务拆解` 亦正常 ✓ |
| r3-P2-2 AC6 措辞 | P2 | **CLOSED（附说明）** | AC6 正文（`:72`）仍写「不退化（基线 931/0/60）」，但测试要求行（`:96`）已明确「既有用例不退化（基线 931/0/60），新增 App.Tests/CoreClient 用例数单独记录」——语义已可消歧，不再二义 ✓ |
| r3-P2-3 冻结矩阵 | P2 | **CLOSED（理由有误，见 P2-3）** | 备注（`:110`）已登记「不随本卡更新（接受）」；但理由「矩阵按 pin 文件存在性生成；矩阵无独立文件」与实际不符（实际存在独立人工维护的 `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`）→ 记为 P2-3 |
| r3-P2-4 `All`/`CoreBindings` | P2 | **PARTIAL（未实际落地）** | P3（`:60`）仍只写「`DraftsCommandNames`（6 新集合）+ `V11RAdditiveCommandNames` 11→17 + `All`/域枚举/`CoreBindings`/`AddDomain` 同步」；`All` 语义（既有 `HostCommandRegistry.All` 字典 vs 新聚合属性）与 6 条 `CoreBindings` 映射（`drafts_*`→`drafts_*`、minor 3）仍未写明 → P2-1 |
| r3-P2-5 DTO 字段 | P2 | **OPEN（未实际落地）** | P2（`:59`）仍只列 DTO **名称**（`Draft`/`DraftLease`/`DraftPatchRequest`/`EditToken`/`RegionCandidate`），**无字段清单**；`DiscardDraftAsync` 丢弃 `{discarded}` 的理由亦未写。DSH 所称「DTO 字段已列」与卡文本不符 → P2-2 |
| r3-P2-6 AC1 ② pin 措辞 | P2 | **CLOSED** | AC1 ②（`:67`）已改「两份冻结物的理由/影响；Region 契约**无 pin**，仅 C-07 重算 pin」✓ |

---

## 2. 关键核查

### 2.1 P1 关闭验证（nullability）

- 卡 `:59`：`Task<DraftLease?> OpenDraftAsync`、`Task<Draft?> PatchDraftAsync`、`Task<RegionCandidate?> PrepareCandidateAsync`。
- Null 默认：`Open→Task.FromResult<DraftLease?>(null)`、`Patch/Prepare→null` ✓ 与可空签名一致；`GetDraftAsync`→`Task<Draft?>`、`ListDraftsAsync`→`Task<IReadOnlyList<Draft>>`（`Array.Empty<Draft>()`）、`ApplyCandidatesAsync`→`Task<IReadOnlyDictionary<string,string>>`（空字典）、`DiscardDraftAsync`→`Task.CompletedTask` ✓ 均自洽。
- 项目设置 `Nullable=enable`/`TreatWarningsAsErrors=true`（`Directory.Build.props:7/10`）与既有可空约定（`IHostController.cs:147/161/186/191`）一致；AC2 `:68` 已同步「三个返回可空」✓。**P1 关闭。**

### 2.2 写域与两冻结物

- `doc/contracts/V11R_REGION_WRITE_CONTRACT.md` ✓（`:23`）、`doc/plan/FEA-C07_API_INVENTORY.md` ✓（`:24`）、`doc/plan/FEA-CONTRACT-FROZEN-C07.md` ✓（`:25`）、`doc/reviews/CONTRACT-UNFREEZE-*.md` ✓（`:26`）、端口三实现 ✓（`:28-30`）、`NewManga.CoreClient/**` ✓（`:31`，含 `DraftCommands.cs`）、两个测试工程 ✓（`:32-33`）、`verification/FEA-05-PORT-1/**` ✓、指针 ✓、`doc/reviews/FEA-05-PORT-1-*.md` ✓。
- `FEA-05_DRAFT_WIRE_CONTRACT.md`/§8.2 由 DSH 收口（备注 `:110`）✓；冻结矩阵接受不更新（理由见 P2-3）。**无阻塞缺口。**

### 2.3 AC 可验收性

| AC | 判定 | 说明 |
|---|---|---|
| AC1 契约 UNFREEZE（两冻结物） | **可验收** ✓ | ①v1.6 五站点；②UNFREEZE 记录 + 两冻结物 + Region 无 pin 明确；③C-07 47→54/54→61、成员表 +7、变更类别 11→18、生成日期/HEAD；④独立复核；⑤`verify_pins` 15/15——均在卡/写域内 |
| AC2 端口面 | **可验收** ✓ | 7 方法（Open/Patch/Prepare 可空）已与 Null 默认自洽；App.Tests 覆盖在写域 |
| AC3 registry | **可验收** ✓ | 6 wire 命令 / `V11RAdditiveCommandNames`=17 / XOR / parity 派生断言 |
| AC4 契约测试 | **可验收** ✓ | `:109`（17）+`:110-114`（Region 子集）+`DraftsCommandNames ⊆ additive`；`CommandContractV11RTests` 不受影响 |
| AC5 端口清单 | **可验收** ✓ | 人工更新 C-07 + `--check` EXIT 0（文件在写域） |
| AC6 回归 | **可验收** ✓ | 命令可跑；`:96` 已明确「既有不退化、新增单独记录」 |
| AC7 证据 | **可验收** ✓ | `verification/FEA-05-PORT-1/**` 在写域 |

---

## 3. Findings（3 条 P2，均接受遗留）

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| P2-1 | P2 | 卡 `:60`（P3）；`HostCommandRegistry.cs:135+`/`:305-313`/`:340-380` | `All` 语义未澄清（既有 `HostCommandRegistry.All` 字典 vs 新聚合属性）；6 条 `CoreBindings`（`drafts_*`→`drafts_*`、minor 3）与 `AddDomain` 的落地要点仍未写 | P3 补一句「`All`=既有 registry 字典，自动含新 descriptor；`CoreBindings` 6 条 `drafts_*`→同名、minor 3」 |
| P2-2 | P2 | 卡 `:59`（P2）；`core_service.py:3015-3018`；`FEA-05_DRAFT_WIRE_CONTRACT.md:26-31` | DTO **字段清单**未列：`DraftLease`（draft/canEdit/token）、`Draft`（draftId/sessionId/pageId/regionId/draftSequence/status/patches…）、`DraftPatchRequest`、`EditToken`（六字段）、`RegionCandidate`（candidateId/regionId/baseRevisionId/origin）；`DiscardDraftAsync` 丢弃 `{discarded}` 理由未写 | 按 wire §2/to_json 列出字段或注明「以 `to_json` 为准」；C083 可 `Task<bool>` 或注明丢弃理由 |
| P2-3 | P2 | 卡 `:110`（备注）；`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md:1-6` | 「接受不更新」的理由不准确：矩阵实际是**独立人工维护**文件（`:1` 标题、`:3` 状态、`:5` 作者 DSH），并非「按 pin 文件存在性生成 / 无独立文件」 | 理由改为「矩阵只记录冻结状态、不承载 pin 值；重冻后 C-07 仍为 `FROZEN`，其内容无需变，故不更新」 |

---

## 4. 结论与建议

1. **范围冻结结论：approved**（P0 = 0 / P1 = 0）。端口面（7 方法/可空签名/Null 默认）、registry（6 wire 命令/17 additive/XOR）、契约 UNFREEZE（Region v1.6 + C-07 pin 重算 + 两冻结物 UNFREEZE 载体 + 独立复核）、测试更新（并集断言 + 子集）与写域均已自洽，AC1–AC7 可机械验收。
2. **转 `in_review` / 派实现前建议**：把 P2-1/P2-2 两条「声称已修但卡文本未落地」的项补上（避免实现者在 `All`/`CoreBindings`/DTO 字段上自行发挥）；P2-3 仅需更正理由措辞。三条均不改变范围冻结结论，可在实现期或下一次文档 pass 修。
3. **实现期提醒（非 finding）**：AC1 的独立复核应在 C-07 pin 重算**之前**完成（`FROZEN-C07:15-17`：冻结字节需覆盖复核字节），pin 记录由 DSH 在冻结点写入；本卡直接 main 实现、由 DSH 提交（禁止范围 `:77`）。

## 5. 边界声明

本报告只审范围冻结（Task 卡文本及其引用的契约/代码/测试/治理事实），**不构成实现验收**，也不构成 UNFREEZE 或契约修订批准。本席位未参与 FEA-05-PORT-1 的起草/实现/返修；未修改被审文件、未 commit/push；行号基于 `9ff2f7eac` 实测。
