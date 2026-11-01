---
task_id: FEA-05-PORT-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: 7bbc09dbb
reviewed_head: 974b65196
decision: changes_requested
counts: { P0: 0, P1: 2, P2: 10 }
---

# FEA-05-PORT-1 实现复核 r2（独立上下文；本席位只审范围，未参与实现）

| 字段 | 值 |
|---|---|
| base_commit | `7bbc09dbbd6b5548a15088c4931d50689c1f58df`（impl-r1 被审 head） |
| reviewed_head | `974b65196341c27805ad072a0ca23c00ed02ac22`（`fix(fea-05-port-1): 处置实现复核 r1…`；`git status --porcelain` 为空） |
| 实现者 | DSH（Codex 通道故障；范围 r4 approved）——本席位**未参与实现**，仅审过范围 r1–r4 与实现 r1（符合 2026-10-31 上下文独立裁决） |
| reviewer | `fea05-wire-scope-reviewer`（DSH 派发 fresh 子 agent；只读被审 head，未 commit/push） |
| 日期 | 2026-11-02 |
| 审查范围 | impl-r1 的 P1×5 处置、UNFREEZE 复核（`FROZEN-C07:17`）、新问题、P2 逐项、三绿与全量回归 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 2 / P2 = 10（共 12）** |

> **一句话结论**：**changes_requested**。P1-01/P1-02/P1-03 三项**已实质修复**（`ReadDraft` 按真实 `to_json` 映射 11 个 PascalCase 字段、`Draft` DTO 补齐、`PrepareCandidateAsync` 改读 `origin`；`DraftPatchRequest(IReadOnlyDictionary<string, object?>)` 透传、不再把 `text` 写成字符串；Region/Drafts 子集断言已补），构建 0 warning/0 error、全量 sln **934/0/57** 复现通过、`verify_pins` 15/15、`--check` EXIT 0。**但**：①**P1-04 仍未完成**——App.Tests 无任何 draft 行为用例（仅 Fake 默认实现），交付说明自承「未完成（时间约束）…记 P2」，**实现者无权把冻结 AC2 单方面降级**，本复核不接受；②**P1-05 仅部分关闭**——`FROZEN-C07` 历史 pin 已恢复 ✓，但 **§1B 仍是旧文「r2 approved / 无需补复核」**（DSH 声称已改为「v1.1 复核中」，实际未改）、**UNFREEZE 记录与新 pin 不一致**（记录仍写 `5c48083f…`，当前最终字节是 `3fdb44e4…`）、changelog 2026-11-02 行也仍写 `5c48083f…`。故 UNFREEZE 的重新独立复核本轮仍**不能判通过**。

---

## 0. 方法与只读声明

- 只读核查被审 head；未修改被审文件、未 commit/push；**本报告是本轮唯一新增文件**。
- 独立复跑（本轮实测）：

| 命令/检查 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain` | `974b65196…` / 空（clean） |
| `dotnet build apps/desktop-avalonia/NewManga.sln` | **0 warning / 0 error，EXIT 0** |
| `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings …/NewManga.runsettings` | **51/235/85/31/119/413 passed；28/0/0/0/22/7 skipped；0 failed；合计 934/0/57，EXIT 0** ✓ |
| `pwsh tools/governance/verify_pins.ps1` | **PASS（all 15）**；C-07 实际 SHA-256 = `3fdb44e4…` 与 `FROZEN-C07:15` 一致 ✓ |
| `python tools/generate_api_inventory.py --check` | **EXIT 0** |
| `pwsh tools/governance/check.ps1` | **PASS（3 warnings）**：10 非终态；STATUS 3162/35（80%）；PLAN 3769/52（80%） |
| 证据日志核对 | `sln-test.log`/`coreclient-test.log`/`build.log` 与实测一致 ✓ |

---

## 1. P1 逐项 disposition（impl-r1 → 本轮）

| r1 ID | 判定 | 证据 / 缺口 |
|---|---|---|
| **P1-01** 读路径键名/字段 | **CLOSED** | `Draft` DTO（`DraftCommands.cs:15-26`）已含 11 字段（`DraftId`/`SessionId`/`PageId`/`RegionId`/`BaseRevisionId`/`PageBindingVersion`/`DraftSequence`/`Patch`/`UndoCursor`/`SavedAt`/`Status`）；`ReadDraft`（`HostController.cs:2380-2401`）按真实 `Draft.to_json()`（`entities.py:107-121`）PascalCase 读取，`patch` 取 object 克隆、`undoCursor` 数字、`savedAt`/`status` 字符串；`PrepareCandidateAsync` 已改读 `origin`（`HostController.cs:2297`，对应 `entities.py:177`）✓ |
| **P1-02** patch 外形 | **CLOSED** | `DraftPatchRequest(IReadOnlyDictionary<string, object?> Patch)`（`DraftCommands.cs:33`）；`DraftPatchJson` 直接返回 `patch.Patch`（`HostController.cs:2411`），不再构造 `text: "字符串"`/`region_type`；patch 由 Core 拥有、端口透传 ✓（符合 `drafts.py:174-178`/`:334-340` 的对象要求） |
| **P1-03** AC4 子集断言 | **CLOSED** | `RegionWriteCommandTests.cs:110-119` 已补 `RegionWrite ∪ RegionRead ⊆ additive` 与 `DraftsCommandNames ⊆ additive` 两条 `Assert.True`；17（`:109`）与计数（`:120-122`）保留 ✓；全量测试绿 |
| **P1-04** AC2 App.Tests 行为覆盖 | **仍 OPEN（不接受降级）** | 仍只有 `FakeHostController.cs:1496-1522` 默认实现；`git grep` 显示 App.Tests 无任何用例调用 7 个端口方法；dispatcher 6 个 draft case/XOR 亦无 CoreClient 测试。交付说明 `:54` 自承「**未完成**（时间约束）…记为 P2 接受遗留，由 FEA-06 联调时补」。**AC2 是范围 r4 冻结的验收标准**（卡 `:68`「`App.Tests` 覆盖（fake/failure 路径）」），实现者不能单方面降级；若 DSH 认为该 AC 应改，须**另走范围变更（重新 scope review 修改卡）**，不能在实现复核里记为 P2 |
| **P1-05** FROZEN-C07 记录 | **PARTIAL（未完全关闭）** | ✅ 已恢复：`FROZEN-C07:54` §1A「修正后 pin」= `17c8f701…`；`:76` 2026-11-01 变更行恢复旧 pin；`:15` §1 现写当前字节 pin `3fdb44e4…`（与实测 SHA-256 一致）；C-07 `:24` 变更类别已改「54 个中 36 基线 + 18 FEA 新增」✓。❌ 未改：`:19-27` **§1B 仍是「最后一次独立复核 r2 approved / 复核后到冻结的改动 仅状态行 / 无需补复核」**（与本次「重新独立复核」要求矛盾；DSH 声称已改「v1.1 复核中」——与文件不符）；`CONTRACT-UNFREEZE-2026-11-02.md:28` 新 pin 仍写 `5c48083f…`（当前最终 pin `3fdb44e4…`）；`FROZEN-C07:77` 2026-11-02 变更行也仍写 `5c48083f…` |

---

## 2. UNFREEZE 复核结论（`FROZEN-C07:15-17`）

**本轮仍不能判通过**（→ changes_requested）。

- **字节层面已可**：Region 契约 v1.6（`:1`/`:3`/`:62-63`/`:346`/`:457`/`:491`）与 C-07 库存（54/61/18、成员表 +7）已落盘；C-07 最终 pin `3fdb44e4…` 与实际 SHA-256 一致，`verify_pins` 15/15 ✓；v1.0 历史 pin `17c8f701…` 已在 §1A/2026-11-01 行保留 ✓。
- **记录层面不可判通过**：§1B 未更新（还写着「r2 approved / 无需补复核」）；UNFREEZE 载体 §2 的「新 pin」与最终 pin 不一致（`5c48083f…` vs `3fdb44e4…`，系变更类别再编辑导致 pin 再次变化，但记录未同步）；changelog 2026-11-02 行同样停留在 `5c48083f…`。这三处使「冻结字节=复核字节」的证据链不闭合，且 §1B 的结论与本次要求相反。

---

## 3. AC 逐项

| AC | 判定 | 说明 |
|---|---|---|
| **AC1 两冻结物** | **未通过（记录待闭合）** | 契约 v1.6 ✓、UNFREEZE 记录存在但 pin 陈旧（P1-05）、C-07 54/61/18 ✓、pin 与字节一致 ✓、`verify_pins` ✓；独立复核=本报告，结论 changes_requested → ④ 未过 |
| **AC2 端口面** | **未通过** | 7 方法与可空签名、映射修复（静态核对）✓；**App.Tests 行为覆盖缺失**（P1-04） |
| **AC3 registry** | **通过** | 17/6/CoreBindings/`Drafts` 域/XOR/6 cases；parity 与 contract 测试全绿（934/0/57 实测） |
| **AC4 契约测试** | **通过** | Region/Drafts 子集断言已补（`:110-119`）；`CommandContractV11RTests` 绿 |
| **AC5 端口清单** | **通过** | `--check` EXIT 0（复跑） |
| **AC6 回归** | **通过** | 本轮复跑 build 0 warn/0 err + sln test **934/0/57 EXIT 0**（6 项目逐一核对） |
| **AC7 证据** | **部分** | 日志/说明与实测一致 ✓；卡 AC 未标、Canonical Evidence 占位、status 仍 `ready`、Closeout 含 stray CR（P2-5） |

---

## 4. Findings

### P1（2 条，阻塞）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| **P1-04（沿用）** | `FakeHostController.cs:1496-1522`；`tests/NewManga.App.Tests/**`（无引用）；`delivery-notes.md:54`；卡 `:68` | **AC2 未完成**：App.Tests 无 draft 行为用例；dispatcher 6 case/XOR 无 CoreClient 测试。交付说明以「时间约束」单方降为 P2——**不接受**。缺少测试也使 P1-01/P1-02 的修复只经静态核对、无回归护栏 | 补：①App.Tests 至少 fake 成功路径（子类 FakeHostController 返回 Draft/DraftLease）+ failure 路径（异常/未就绪→null）+ Null 默认；②CoreClient.Tests 覆盖 6 条 payload 与 `drafts_status` XOR（两给/都不给/各一）。如确需延后，须由 DSH 走**范围变更**（新 scope review 改 AC2），不能在实现复核中降级 |
| **P1-05（部分）** | `FEA-CONTRACT-FROZEN-C07.md:19-27`（§1B）、`:77`（changelog）；`CONTRACT-UNFREEZE-2026-11-02.md:28` | **冻结记录未闭合**：§1B 仍「r2 approved / 无需补复核」；UNFREEZE 记录与 changelog 的「新 pin」仍是 `5c48083f…`，与当前最终 pin `3fdb44e4…` 不一致（变更类别编辑导致二次变字节，记录未同步） | §1B 改为「v1.1：pin `3fdb44e4…`，复核报告 `FEA-05-PORT-1-impl-r2`（结论通过后由 DSH 重冻）」；UNFREEZE §2 与 changelog 更新为最终 pin（可注明中间值 `5c48083f…`→`3fdb44e4…`）；§1A 的「最终字节」标注为 v1.0 口径 |

### P2（10 条，与 impl-r1 相同或延续；不阻断）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| P2-1 | `HostCommandRegistry.cs:322-323`、`:363`、`:117`/`:328` | 重复 `/// <summary>`、`AddDomain(...Drafts…)` 缩进 4 空格、`DraftsNames`/`DraftsCommandNames` 双份清单 | 合并/修正 |
| P2-2 | `V11R_REGION_WRITE_CONTRACT.md:61`、`:491` | `:61` 仍「11 条命令的 CoreMinor 均为 3」（应 17 或改家族措辞）；v1.6 变更行插在 v1.1 与 v1.2–v1.5 之间 | 修正措辞/行序 |
| P2-3 | `FEA-05_DRAFT_WIRE_CONTRACT.md:37-39`；`tests/core/test_draft_commands.py:19-24`/`:41` | FEA-05 契约 §2（Draft snake_case 说明、`Origin`）与真实 `to_json`（PascalCase、`origin`）及协议测试 fake 三者不一致；端口现按真实值实现，契约文本仍错 → DSH 冻结 FEA-05 契约前须统一 | DSH 裁决口径并同步契约/测试 |
| P2-4 | `FEA-C07_API_INVENTORY.md:4` | 生成时 HEAD 仍 `a740f855f`（ready 提交），非实现/冻结提交 | 冻结提交时改为实际 head |
| P2-5 | 卡 `:67-73`、`:100-106`、`:108-115` | AC 全 `[ ]`/`<<TODO>>`、Canonical Evidence 占位、status 仍 `ready`、Closeout 行 stray CR（`置 eady`） | 收口/转 `in_review` 前刷新 |
| P2-6 | `doc/STATUS.md:7`、`:10` | `:7` 重复「`FEA-04b` in_review；上一 `FEA-04b` in_review」；`:10` 仍「`FEA-05-PORT-1` 待建卡」 | 去重/更新 |
| P2-7 | `delivery-notes.md:55`、`:57` | 处置表称「§1B 更新为「v1.1 复核中」」——**与文件不符**（§1B 未改）；回归行掉字「erify_pins」 | 按实际修正；清理控制/转义字符 |
| P2-8 | `IHostController.cs:420-421`；`NullHostController.cs:539-564` | 接口注释「never a silent success for a write」与 Null/Fake 的 `ApplyCandidates→空字典`、`Discard→CompletedTask` no-op 成功相矛盾；`GetDraftAsync` null 同时表示未就绪/无 draft | 明确 null/空/no-op 语义并补注释/测试 |
| P2-9 | `FEA-05_DRAFT_WIRE_CONTRACT.md:3`；`V11R_COMMAND_CONTRACT_V1.md` §8.2 | 6 命令已注册，但 FEA-05 契约与 §8.2 仍 `PENDING`（卡备注称 DSH 收口升级） | FEA-06 消费前由 DSH 升级并记录 |
| P2-10 | 卡 `:72`；`sln-test.log` | 基线 931/0/60 vs 本轮 934/0/57（+3 passed/−3 skipped），本卡未新增测试，差异来源未说明 | DSH 说明 skip 集合变化，或固定基线快照 |

---

## 5. 处置建议

1. **必须先决**：P1-04 要么补测试（推荐，最小：App.Tests fake 成功+failure+Null 默认；CoreClient 6 payload+XOR），要么由 DSH **走范围变更**（重新 scope review 修改 AC2）——两者之一完成前本轮不能 approved。
2. **P1-05 收尾**：更新 §1B、UNFREEZE 记录 §2 与 changelog 的最终 pin（`3fdb44e4…`），并注明中间值来源；§1A 的「最终字节」标注 v1.0 口径。完成后 UNFREEZE 复核即可判通过（字节已正确、pin 与字节一致、历史已保留）。
3. P2：P2-7（交付说明失真）和 P2-3（契约口径）建议本轮一并处理；其余可在收口批处理。
4. 修复后派 **impl-r3**；P0/P1=0 后 DSH 重冻 C-07、升级 FEA-05 契约/§8.2，转 `in_review` 并补 AC7 证据表。

## 6. 边界声明

本报告只审实现与冻结范围/契约的一致性，**不构成集成验收**；真实 sidecar/端到端（FEA-06 消费）与 App.Tests 行为测试**仍未验证**（现状缺失，见 P1-04）。本席位未参与 FEA-05-PORT-1 的实现或返修（实现者为 DSH），符合 2026-10-31「上下文独立」裁决；未修改被审文件、未 commit/push；行号基于 `974b65196` 实测。
