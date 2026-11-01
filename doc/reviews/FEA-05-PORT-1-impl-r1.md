---
task_id: FEA-05-PORT-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: 9ff2f7eac
reviewed_head: 7bbc09dbb
decision: changes_requested
counts: { P0: 0, P1: 5, P2: 10 }
---

# FEA-05-PORT-1 实现复核 r1（独立上下文；本席位只审范围，未参与实现）

| 字段 | 值 |
|---|---|
| base_commit | `9ff2f7eacef5513ca22db4eb7e6dcfca38e4022b`（范围 v4 被审 head） |
| reviewed_head | `7bbc09dbbd6b5548a15088c4931d50689c1f58df`（`feat(fea-05-port-1): …`；`git status --porcelain` 为空） |
| 实现者 | DSH（范围 r4 approved 后实现；Codex 通道故障，按目标故障转移规则）——本席位**未参与实现**，仅审过范围 r1–r4（符合 2026-10-31 上下文独立裁决） |
| reviewer | `fea05-wire-scope-reviewer`（DSH 派发 fresh 子 agent；只读被审 head，未 commit/push） |
| 日期 | 2026-11-02 |
| 审查范围 | AC1–AC7、UNFREEZE 复核（`FROZEN-C07:17`）、端口/registry/测试/契约一致性、治理三绿 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 5 / P2 = 10（共 15）** |

> **一句话结论**：**changes_requested**。结构与流程大体到位（契约 v1.6 五站点、UNFREEZE 记录、C-07 47→54/54→61、pin 重算且 `verify_pins` 15/15、registry 17/6/域/XOR、三绿、全量 sln **934/0/57** 实测通过）。但端口**读写路径的数据映射与真实 Core 输出不符**：`ReadDraft` 按 camelCase 读而真实 `Draft.to_json()` 是 `DraftId/...` 大写键（`entities.py:107-121`），`Draft` DTO 又缺 5 个持久字段 → `Open/Patch/Get/List` 返回的 Draft 除 `status` 外全空；`PrepareCandidateAsync` 读 `Origin` 而真实键是 `origin`；`DraftPatchRequest(string? Text, string? RegionType)` 无法表达合法 patch（`text` 必须是对象，字符串会被服务端 `DRAFT_PATCH_INVALID` 拒绝）。此外 AC4 要求的 Region/Drafts 子集断言被删除未补、AC2 要求的 App.Tests 行为覆盖缺失（交付说明自承「仅编译级」），且 `FEA-CONTRACT-FROZEN-C07.md` 的历史 pin 行被**追溯改写**、§1B 未更新——故 UNFREEZE 的「重新独立复核」本轮**不通过**。

---

## 0. 方法与只读声明

- 只读核查被审 head；未修改被审文件、未 commit/push；**本报告是本轮唯一新增文件**。
- 独立复跑（本轮实测）：

| 命令/检查 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain` | `7bbc09dbb…` / 空（clean） |
| `dotnet build apps/desktop-avalonia/NewManga.sln` | **0 warning / 0 error，EXIT 0** |
| `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings …/NewManga.runsettings` | **6 个项目：51/235/85/31/119/413 passed；28/0/0/0/22/7 skipped；0 failed；合计 934 passed / 0 failed / 57 skipped，EXIT 0** ✓ 与交付声称一致 |
| `pwsh tools/governance/verify_pins.ps1` | **PASS（all 15）**；另独立核对 C-07 实际 SHA-256 = `5c48083f…` 与记录 pin 一致 ✓ |
| `python tools/generate_api_inventory.py --check` | **EXIT 0** |
| `pwsh tools/governance/check.ps1` | **PASS（3 warnings）**：10 非终态；STATUS 3162/35（80%）；PLAN 3769/52（80%） |
| 证据日志核对 | `sln-test.log` 与实测 6 项目合计一致；`coreclient-test.log`=119/22、`build.log`=EXIT 0 ✓ |

---

## 1. UNFREEZE 复核结论（`FROZEN-C07:15-17` 要求）

**结论：本轮「重新独立复核」不通过**（→ `changes_requested`）。

- 冻结物 A（Region 契约 v1.5→v1.6）：内容基本达成——`:1`/`:3`（标题/状态）、`:62-63`（§1.1 并集 17 + `DraftsCommandNames`）、`:346`（§4 并集 17）、`:457`（§8 验证表）、`:491`（变更记录 v1.6）均已更新；`CONTRACT-UNFREEZE-2026-11-02.md` 记录两冻结物、理由、影响、旧/新 pin ✓。**但** `:61` 仍写「11 条命令的 CoreMinor 均为 3」（未随 17 更新）；变更记录 v1.6 行插在 v1.1 与 v1.2–v1.5 之间（版本序错）——见 P2-2。
- 冻结物 B（C-07 库存）：`FEA-C07_API_INVENTORY.md` 47→54、合计 54→61、成员表 +7、日期/HEAD 刷新 ✓；pin 重算 `5c48083f…` 与文件 SHA-256 一致，`verify_pins` 15/15 ✓。**但** `:24` 变更类别仍「47 个中…11 个为 FEA 期间新增」（未改 54/18）——见 P2-4。
- **不通过的核心原因**：`FEA-CONTRACT-FROZEN-C07.md` 的历史 pin 行被**追溯改写**（详见 P1-05），§1B「冻结字节 vs 复核字节」未更新；且本复核提出 P1 修复项，字节在修复后还会变化——当前 pin 不能作为「已复核通过」的冻结依据。**处理**：修完 P1 后由 DSH 更新 §1B/重冻记录并再次独立复核（或复用本轮修复后的 r2），再签 pin。

---

## 2. AC 逐项

| AC | 判定 | 证据与缺口 |
|---|---|---|
| **AC1 契约 UNFREEZE（两冻结物）** | **未通过（部分达成）** | ①v1.6 五站点 ✓（`:61` 残留、变更序 P2-2）；②UNFREEZE 记录 ✓；③C-07 54/61、成员表 +7 ✓ 但 `:24` 变更类别未改（P2-4）；④独立复核=本报告 **不通过**（P1-05）；⑤`verify_pins` 15/15 ✓、pin 与字节一致 ✓ |
| **AC2 端口面** | **未通过** | 7 方法与可空签名已按卡落地（`IHostController.cs:422-461`）；`HostController` 实现经 `HostRuntime.Commands` dispatcher（`:2215`）；Null/Fake 不抛默认（`NullHostController.cs:539-564`、`FakeHostController.cs:1495-1522`）。**但**读写映射错误（P1-01/P1-02），且 App.Tests 无行为覆盖（P1-04） |
| **AC3 CoreClient registry** | **通过（附 P2）** | `DraftsCommandNames` 6 ✓、`V11RAdditiveCommandNames`=17（并集）✓、`CoreBindings` 6（同名/minor 3）✓、`DraftsNames`+`AddDomain` ✓、`HostCommandDomain.Drafts` ✓、dispatcher 6 显式 case + `drafts_status` XOR ✓（`HostCommandDispatcher.cs:501-545`）；parity/contract 测试全绿（实测）✓。缺专门 dispatcher 测试（P2 同 P1-04 建议） |
| **AC4 契约测试** | **未通过** | `RegionWriteCommandTests`：`:109`（17）与计数断言在 ✓；**但** Region 子集/Drafts 子集断言被删除未补（P1-03）；`CommandContractV11RTests` 全绿 ✓ |
| **AC5 端口清单** | **通过** | `generate_api_inventory.py --check` EXIT 0（本轮复跑） |
| **AC6 回归** | **通过** | 本轮复跑：build 0 warn/0 err；sln test **934/0/57，EXIT 0**；与证据日志一致。（基线 931/0/60 的 +3/−3 口径见 P2-10） |
| **AC7 证据** | **部分** | `verification/FEA-05-PORT-1/` 4 文件（build/sln-test/coreclient-test/delivery-notes）与实测一致 ✓；但卡 AC 全 `<<TODO>>`、Canonical Evidence 占位、status 仍 `ready`、Closeout 行含 stray CR（P2-5） |

---

## 3. Findings

### P1（5 条，阻塞）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| **P1-01** | `HostController.cs:2380-2386`（`ReadDraft`）、`:2293-2297`（`PrepareCandidateAsync`）；`DraftCommands.cs:11-17`；`src/domain/drafts/entities.py:107-121`/`:172-177`；`core_service.py:3016/3027/3051-3052` | **读路径 DTO 键名与真实 `to_json()` 不符，返回空壳。** 真实 `Draft.to_json()` 键为 `DraftId`/`SessionId`/`PageId`/`RegionId`/`BaseRevisionId`/`PageBindingVersion`/`DraftSequence`/`patch`/`undoCursor`/`savedAt`/`status`，而 `ReadDraft` 读 `draftId`/`sessionId`/`pageId`/`regionId`/`draftSequence`（仅 `status` 命中）→ Open/Patch/Get/List 的 Draft 全空；`Draft` DTO 另缺 `BaseRevisionId`/`PageBindingVersion`/`patch`/`undoCursor`/`savedAt`（11 个持久字段只剩 6 个，且无 `patch`，UI 拿不到草稿内容）；`PrepareCandidateAsync` 读 `"Origin"` 而真实键是 `origin`（`entities.py:177`）。根因：实现照抄了协议测试的 **fake** `to_json()`（`tests/core/test_draft_commands.py:23-24` `{"draftId": …}`、`:41` `"Origin"`），而真实 handler 直接返回 `to_json()`（`core_service.py:3016`）。错误被吞（`TryGetProperty` 失败即空串），无异常、编译/现有测试均过 | 按真实键名映射（`DraftId` 等 + `origin`）；补齐 DTO 字段（`patch` 用 `JsonElement`/字典）；建议 case-insensitive 兜底 + 新增行为测试锁住键名 |
| **P1-02** | `DraftCommands.cs:19`（`DraftPatchRequest(string? Text, string? RegionType)`）；`HostController.cs:2396-2410`（`DraftPatchJson`）；`src/domain/drafts/entities.py:77-101`；`src/application/editing/drafts.py:174-178`/`:334-340`；`tests/core/test_draft_commands.py:103` | **写路径 patch 外形无法表达合法 patch。** `DraftPatchJson` 写 `payload["text"] = patch.Text`（**字符串**），但服务端要求 `patch["text"]` 是 **Mapping**（`drafts.py:174-178`、`:334-340`；实际形状见协议测试 `{"text": {"zh": "x"}}`）→ 必然 `DRAFT_PATCH_INVALID`；`region_type` 不是 draft patch 域（prepare 只读 `style/text/geometry`，patch_draft 会把未知键并入草稿）→ 无意义；`geometry`/`style` 完全无法表达 | 把 patch 建模为对象（`JsonElement` 直传或 `{Text, Geometry, Style}` 字典），对齐 `_TEXT_KEYS`/`_STYLE_KEYS` 与 `_apply_candidate_patch`；补行为测试 |
| **P1-03** | `RegionWriteCommandTests.cs:101-118`（对比 base `9ff2f7eac:107-117`）；卡 `:70`（AC4）、`:61`（P4） | **AC4 未完成：Region/Drafts 子集断言被删未补。** 本次只删除了旧 `:110-114` 的「additive == RegionWrite ∪ RegionRead」断言，未按卡改为「RegionWrite ∪ RegionRead ⊆ additive」，也未补「`DraftsCommandNames ⊆ additive`」；当前仅 `:109` 等值（17）+ 计数。交付说明 `:22` 却声称「Region 子集 + Drafts 子集」 | 补两条 `Assert.True(additive.IsSupersetOf(...))`（或直接断言三家族并集相等），并修正交付说明 |
| **P1-04** | `FakeHostController.cs:1495-1522`（仅默认实现）；`tests/NewManga.App.Tests/**` 无引用；`verification/FEA-05-PORT-1/delivery-notes.md:44`；卡 `:68`（AC2） | **AC2 未完成：App.Tests 无行为覆盖。** 仅给 Fake 加了 7 个默认 stub（编译级），App.Tests 无任何用例调用 7 个端口方法（`git grep` 仅命中 Fake 自身）；dispatcher 6 个 draft case/XOR 也无 CoreClient 测试。交付说明自承「App.Tests 仅编译级…P2 记录」——实现者无权把 AC 单方面降为 P2 | 补 App.Tests：7 方法成功/失败/null-host/未就绪路径；补 CoreClient：6 个 payload case + `drafts_status` XOR（两都给/都不给/各一） |
| **P1-05** | `doc/plan/FEA-CONTRACT-FROZEN-C07.md:15`（§1 pin）、`:54`（§1A 修正后 pin）、`:77`（2026-11-01 变更行）、`:19-27`（§1B）；`FEA-C07_API_INVENTORY.md:24`；`CONTRACT-UNFREEZE-2026-11-02.md:33-34` | **冻结记录被追溯改写 + 复核页未更新。** 新 pin 直接覆盖了 §1 的 2026-11-01 冻结字节 pin（`17c8f701…`→`5c48083f…`），并把 **2026-11-01 的历史变更行**也改成新 pin——违反该记录自身纪律「pin 是证据，不能静默替换；原值可独立复现」；§1B 仍写「最后一次独立复核 r2 approved / 复核后到冻结的改动 仅状态行 / 无需补复核」，与新字节及「需重新独立复核」矛盾；changelog `:80` 声称「变更类别 11→18」但 C-07 `:24` 仍是 11 | 恢复 2026-11-01 的历史 pin 行原值；新增「2026-11-02 重冻 v1.1」节记录新 pin、UNFREEZE 载体与**通过后的**复核报告；更新 §1B（复核字节=复核时提交）；修正 C-07 `:24` 为「54 个中 36 基线 + 18 FEA 新增」；重冻须在本轮 P1 修复后的复核通过之后 |

### P2（10 条，接受/建议，不阻断但建议本轮顺手）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| P2-1 | `HostCommandRegistry.cs:322-323`、`:363`、`:117`/`:328` | 代码卫生：连续两个 `/// <summary>`（XML 文档不良）；`AddDomain(..., Drafts, …)` 缩进 4 空格（方法体内其余 8 空格）；`DraftsNames` 与 `DraftsCommandNames` 两份同值清单（漂移风险，parity 测试可兜底） | 合并为单一集合；修正缩进/重复注释 |
| P2-2 | `V11R_REGION_WRITE_CONTRACT.md:61`、`:491` | 契约内部残留：`:61` 仍「11 条命令的 CoreMinor 均为 3」（应 17 或改「各家族追加命令」）；v1.6 变更行插在 v1.1 与 v1.2–v1.5 之间（版本序未按 v1.5 后追加） | 修正措辞；把 v1.6 行移到 v1.5 之后 |
| P2-3 | `FEA-05_DRAFT_WIRE_CONTRACT.md:37-39`；`tests/core/test_draft_commands.py:19-24`/`:41` | **三处口径不一致**：契约 §2 说 Draft 键是 snake_case、RegionCandidate 是 `Origin`；协议测试用 fake 固定 camelCase/`Origin`；真实 `to_json()` 是 PascalCase/`origin`。这是 FEA-05-WIRE-1 遗留债务，若不在 DSH 把该契约转 `FROZEN` 前修正，端口与后续 UI 将无稳定依据 | DSH 在冻结 FEA-05 契约前统一口径（建议 handler 归一为契约声明的 camelCase，或改契约/测试对齐 `to_json`），并同步修 §2 描述 |
| P2-4 | `FEA-C07_API_INVENTORY.md:24`、`:4` | 变更类别「47 个中…11 个 FEA 新增」未改 54/18；生成 HEAD 用 `a740f855f`（ready 提交）而非实现提交 | 改「54 个中 36 基线 + 18 FEA 新增」；HEAD 用实现/冻结提交 |
| P2-5 | 卡 `:67-73`、`:100-106`、`:108-115` | 卡未刷新：AC 全 `[ ]`/`<<TODO>>`、Canonical Evidence 占位、status 仍 `ready`（未 `in_review`）、Closeout 行含 stray CR（`置 eady`） | 收口/转 `in_review` 前统一刷新（AC7 证据表补 4 个文件） |
| P2-6 | `doc/STATUS.md:7`、`:10` | `:7` 仍重复「`FEA-04b` in_review；上一 `FEA-04b` in_review」；`:10` 仍「`FEA-05-PORT-1` 待建卡」（已实现） | 去重并改「实现完成待复核」 |
| P2-7 | `verification/FEA-05-PORT-1/delivery-notes.md:12`、`:22`、`:14-22` | 交付说明失真：`:12` 称「变更类别 11→18」、`:22` 称「Region 子集 + Drafts 子集」（均未落地）；文件路径出现掉字（`pps/desktop-avalonia/…`，缺首字母 `a`） | 按实际改动修正说明；清理控制/转义字符 |
| P2-8 | `IHostController.cs:420-421`、`NullHostController.cs:539-564`、`HostController.cs:2338-2348` | 语义细节：接口注释称「never a silent success for a write」，而 Null/Fake 的 `ApplyCandidatesAsync` 返回空字典、`DiscardDraftAsync` 直接完成（no-op 成功）；`GetDraftAsync` 用 null 同时表示「host 未就绪」与「无 draft」，可能掩盖 typed error | 明确 null/空/no-op 的语义边界（注释+测试）；考虑「未就绪」抛/返回独立状态 |
| P2-9 | `VERIFICATION/**` 无；`FEA-05_DRAFT_WIRE_CONTRACT.md:3`、`V11R_COMMAND_CONTRACT_V1.md` §8.2 | 6 条命令已注册进 CoreClient，但 FEA-05 契约与总契约 §8.2 仍 `PENDING`（卡备注称 DSH 在 AC1 后升级）；需确保在 FEA-06 消费前完成升级，否则「已注册但契约未冻」 | DSH 收口时升级 FEA-05 契约状态与 §8.2；在 Closeout 记录 |
| P2-10 | 卡 `:72`（AC6）、`verification/…/sln-test.log` | 基线口径差异未解释：本次 **934 passed / 57 skipped**，基线 **931/0/60**（+3 passed/−3 skipped），而本卡未新增任何测试；需确认是否 runsettings/跳过集合变化，否则「不退化」无法精确对照（0 failed 已满足） | DSH 说明 ±3 的来源；必要时固定基线快照 |

---

## 4. 处置建议

1. **P1 修复顺序**：P1-01/P1-02（端口映射/patch 外形，直接在 `HostController.cs`/`DraftCommands.cs` 内按真实 `to_json` 重写）→ P1-04（补 App.Tests/CoreClient 行为测试，锁住键名与 XOR）→ P1-03（补 Region/Drafts 子集断言）→ P1-05（恢复 FROZEN-C07 历史、补 §1B/重冻记录、改 C-07 变更类别）。
2. **P2-3 的契约口径需 DSH 裁决**（handler 归一 vs 端口按 PascalCase），否则 P1-01 修法可能与 FEA-05 契约冲突；建议在同一修复批内统一。
3. 修完后派 **impl-r2** 复核；P0/P1=0 且 UNFREEZE 复核通过后，由 DSH 重冻 C-07、升级 FEA-05 契约/§8.2，再转 `in_review` → AC7 收口。
4. 全量 sln 934/0/57 与三绿（`verify_pins` 15/15、`--check` EXIT 0、`check.ps1` PASS）本轮已独立复现，可在修复后仅复跑受影响项目 + 三绿，不必每次全量。

## 5. 边界声明

本报告只审实现与冻结范围/契约的一致性，**不构成集成验收**；真实 sidecar/端到端（FEA-06 消费）与 App.Tests 行为测试**未验证**（现状缺失，见 P1-04）。本席位未参与 FEA-05-PORT-1 的实现或返修（实现者为 DSH），符合 2026-10-31「上下文独立」裁决；未修改被审文件、未 commit/push；行号基于 `7bbc09dbb` 实测。
