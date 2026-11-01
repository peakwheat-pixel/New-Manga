---
task_id: FEA-05-PORT-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: 974b65196
reviewed_head: 24600bbee
decision: approved
counts: { P0: 0, P1: 0, P2: 11 }
---

# FEA-05-PORT-1 实现复核 r3（独立上下文；本席位只审范围，未参与实现）

| 字段 | 值 |
|---|---|
| base_commit | `974b65196341c27805ad072a0ca23c00ed02ac22`（impl-r2 被审 head） |
| reviewed_head | `24600bbee9fa8c45b95c804d9130ee935c6f43fd`（`fix(fea-05-port-1): 处置实现复核 r2…`；`git status --porcelain` 为空） |
| 实现者 | DSH（Codex 通道故障；范围 r4 approved）——本席位**未参与实现**，仅审过范围与实现 r1/r2（符合 2026-10-31 上下文独立裁决） |
| reviewer | `fea05-wire-scope-reviewer`（DSH 派发 fresh 子 agent；只读被审 head，未 commit/push） |
| 日期 | 2026-11-02 |
| 审查范围 | impl-r2 的 P1×2 处置、新测试真实性与覆盖、UNFREEZE 复核（`FROZEN-C07:17`）、新问题、P2 逐项、三绿与全量回归 |
| 结论 | **approved** |
| 计数 | **P0 = 0 / P1 = 0 / P2 = 11（11 条均为接受遗留/建议，不阻断）** |

> **一句话结论**：**approved**。P1-04 已实质关闭：新增 `DraftPortDefaultTests`（3 个 Theory × Null/Fake 两 host = 6 用例，覆盖 7 方法的安全降级）与 `DraftCommandRegistryTests`（4 Fact + 5 Theory 用例 = 9 用例，覆盖注册/域/通道/minor/并集 17/分区/6 条 payload fail-closed/XOR），**断言均非空转**且本轮全绿；P1-05 已闭合：§1B 改为「v1.0 r2 approved；v1.1 r2 changes_requested，待 r3；v1.1 尚未重冻」，UNFREEZE 记录 §2 新 pin 改为最终 `3fdb44e4…`（注明中间值 `5c48083f…` 废弃），v1.0 历史 pin `17c8f701…` 保留于 §1A，pin 与实测 SHA-256 一致、`verify_pins` 15/15。本轮独立复跑：build 0 warn/0 err；全量 sln **949/0/57，EXIT 0**（6 项目 51/235/85/31/128/419）——与声称一致。**UNFREEZE 重新独立复核本轮判通过**，剩余 11 条 P2 均为收口级建议。

---

## 0. 方法与只读声明

- 只读核查被审 head；未修改被审文件、未 commit/push；**本报告是本轮唯一新增文件**。
- 独立复跑（本轮实测）：

| 命令/检查 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain` | `24600bbee…` / 空（clean） |
| `dotnet build apps/desktop-avalonia/NewManga.sln` | **0 warning / 0 error，EXIT 0** |
| `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings …/NewManga.runsettings` | **51/235/85/31/128/419 passed；28/0/0/0/22/7 skipped；0 failed；合计 949/0/57，EXIT 0** ✓ |
| `pwsh tools/governance/verify_pins.ps1` | **PASS（all 15）**；C-07 实际 SHA-256 = `3fdb44e4…` 与 `FROZEN-C07:15` 一致 ✓ |
| `python tools/generate_api_inventory.py --check` | **EXIT 0** |
| `pwsh tools/governance/check.ps1` | **PASS（3 warnings）**：10 非终态；STATUS 3162/35（80%）；PLAN 3769/52（80%） |
| 证据日志核对 | `sln-test.log`（949/0/57）、`coreclient-test.log`（128/22）、`app-tests.log`、`build.log` 与实测一致 ✓ |

---

## 1. P1 逐项 disposition

| r2 ID | 判定 | 证据 |
|---|---|---|
| **P1-01** 读路径映射 | **CLOSED（沿用 r2）** | `ReadDraft`（`HostController.cs:2380-2401`）按真实 `Draft.to_json()`（`entities.py:107-121`）读 11 个 PascalCase 字段；`Draft` DTO 11 字段（`DraftCommands.cs:15-26`）；`PrepareCandidateAsync` 读 `origin`（`:2297`）✓ |
| **P1-02** patch 外形 | **CLOSED（沿用 r2）** | `DraftPatchRequest(IReadOnlyDictionary<string, object?> Patch)`（`:33`）、`DraftPatchJson` 透传（`:2411`）✓ |
| **P1-03** 子集断言 | **CLOSED（沿用 r2）** | `RegionWriteCommandTests.cs:110-119` 两条子集断言 ✓，全绿 |
| **P1-04** AC2 行为覆盖 | **CLOSED** | 新增 `DraftPortDefaultTests.cs`（6 用例，Null+Fake 两 host × 7 方法降级）与 `DraftCommandRegistryTests.cs`（9 用例：注册/域/通道/CoreCommand/minor、并集 17、分区一次、5 条 payload fail-closed、XOR 3 情形）；实跑 CoreClient 119→128、App 413→419（+15）全绿，断言非空转（详见 §3） |
| **P1-05** 记录一致性 | **CLOSED** | `FROZEN-C07:23-25` §1B 已如实记录「v1.1 尚未重冻 / 待 r3 / 当前 pin 仅本地校验」；`CONTRACT-UNFREEZE-2026-11-02.md:28` 新 pin 改为最终 `3fdb44e4…` 并注明中间值 `5c48083f…` 废弃；§1A `:54` 与 2026-11-01 行 `:76` 保留 v1.0 pin `17c8f701…`（未追溯改写）；C-07 `:24` 变更类别 54/36/18 ✓。残留见 P2-7（changelog 行仍写 `5c48083f…`） |

---

## 2. UNFREEZE 复核结论（`FROZEN-C07:15-17`）

**本轮判通过（approved）**——满足「重新独立复核通过后由 DSH 重冻」的前半条件：

- **字节**：Region 契约 v1.6 五站点（`:1`/`:3`/`:62-63`/`:346`/`:457`/`:491`）与 C-07 库存（54/61/18、成员表 +7）落盘；C-07 最终 pin `3fdb44e4…` = 实测 SHA-256，`verify_pins` 15/15 ✓。
- **记录**：UNFREEZE 载体两冻结物（Region 契约无 pin；C-07 有）最终 pin 一致；v1.0 历史 pin 保留、中间值注明废弃；§1B 如实披露「v1.1 尚未重冻」，不存在「复核字节未覆盖」的掩盖。
- **结论**：独立复核通过；**下一步由 DSH 执行重冻**（更新 §1B 为 r3 approved + 重冻日期，按 `CONTRACT-UNFREEZE:34` 纪律）。UNFREEZE 记录 §1 的 Region 契约「复核」行可在重冻时追加引用本报告。

---

## 3. 新测试真实性/覆盖评估（Lead 特别要求）

**非空转**：两组测试均直接调用生产 API 并断言具体值/具体异常，改坏实现会红。

- `DraftPortDefaultTests`（`NewManga.App.Tests/DraftPortDefaultTests.cs`，6 用例）：`Hosts()` 提供 `NullHostController.Instance` 与 `FakeHostController(ReadySnapshot)` 两 host；断言 `Open→null`、`Patch/Prepare→null`、`Get→null`、`List/Apply→empty`、`Discard` 完成不抛——若任一默认实现改成抛异常或返回非空，测试必红 ✓。**局限**：两 host 均为「不可用」实现，未覆盖 fake 成功路径与真实 `HostController` 映射/异常传播（见 P2-11）。
- `DraftCommandRegistryTests`（`NewManga.CoreClient.Tests/Commands/DraftCommandRegistryTests.cs`，9 用例）：
  - 注册事实：6 条名集合、`Drafts` 域、`CoreService` 通道、`CoreCommand`=同名、`CoreMinor=3`（错一项即红）；
  - `V11RAdditiveCommandNames` 恰 17 且等于三家族并集；
  - `ForDomain(Drafts)` 与 `DraftsCommandNames` 完全相等、全域分区总数 = `All.Count`；
  - 5 条 payload 缺必需字段 → `HostCommandInvalidArgumentsException` 且 `Code == INVALID_ARGUMENTS`（fail-closed）；
  - `drafts_status`：`{}` 与两键都给 → 抛；单给 `draftId`/`sessionId` → 通过（XOR）。
  - 局限：`drafts_open` 用例把 `pageBindingVersion` 等以字符串构造（缺字段先抛，未测类型校验）；XOR 测试未覆盖「键存在但 null」的边界——P2-11 一并建议。

---

## 4. AC 逐项

| AC | 判定 | 说明 |
|---|---|---|
| **AC1 两冻结物** | **通过** | 契约 v1.6 五站点 ✓、UNFREEZE 记录 ✓（最终 pin 一致）、C-07 54/61/18 ✓、pin 与字节一致 ✓、`verify_pins` 15/15 ✓；独立复核=本报告 approved → ④ MET；重冻由 DSH 执行 |
| **AC2 端口面** | **通过** | 7 方法/可空签名/实现/Null 默认 + App.Tests 行为覆盖（fake/failure 降级路径）✓；既有方法不回归（全量 949/0/57） |
| **AC3 registry** | **通过** | 17/6/CoreBindings/`Drafts` 域/XOR/6 cases；新增 `DraftCommandRegistryTests` 直接覆盖 ✓ |
| **AC4 契约测试** | **通过** | Region/Drafts 子集断言 ✓；`CommandContractV11RTests` 全绿 ✓ |
| **AC5 端口清单** | **通过** | `--check` EXIT 0（复跑） |
| **AC6 回归** | **通过** | 本轮复跑 build 0 warn/0 err；sln **949/0/57 EXIT 0**（6 项目逐一核对） |
| **AC7 证据** | **部分** | 日志（build/sln-test/coreclient-test/app-tests）与实测一致 ✓；卡 AC 未标、Canonical Evidence 占位、status 仍 `ready`、Closeout 含 stray CR（P2-5） |

---

## 5. Findings（11 条 P2，均不阻断）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| P2-1 | `HostCommandRegistry.cs:322-323`、`:363`、`:117`/`:328` | 重复 `/// <summary>`；`AddDomain(...Drafts…)` 缩进 4 空格；`DraftsNames`/`DraftsCommandNames` 双份同值清单 | 合并/修正 |
| P2-2 | `V11R_REGION_WRITE_CONTRACT.md:61`、`:491` | `:61` 仍「11 条命令的 CoreMinor 均为 3」（应 17 或改家族措辞）；v1.6 变更行插在 v1.1 与 v1.2–v1.5 之间 | 修正措辞/行序 |
| P2-3 | `FEA-05_DRAFT_WIRE_CONTRACT.md:37-39`；`tests/core/test_draft_commands.py:19-24`/`:41` | FEA-05 契约 §2（Draft snake_case 说明、`Origin`）与真实 `to_json`（PascalCase、`origin`）及协议测试 fake 仍不一致；端口已按真实值实现，契约文本待 DSH 冻结前统一 | DSH 裁决口径并同步 |
| P2-4 | `FEA-C07_API_INVENTORY.md:4` | 生成时 HEAD 仍 `a740f855f`（ready 提交），非实现/冻结提交 | 重冻时改为实际 head |
| P2-5 | 卡 `:67-73`、`:100-106`、`:108-115` | AC 全 `[ ]`/`<<TODO>>`、Canonical Evidence 占位、status 仍 `ready`、Closeout 行 stray CR（`置 eady`） | 转 `in_review`/收口前刷新 |
| P2-6 | `doc/STATUS.md:7`、`:10` | `:7` 重复「`FEA-04b` in_review；上一 `FEA-04b` in_review」；`:10` 仍「`FEA-05-PORT-1` 待建卡」 | 去重/更新 |
| P2-7 | `FEA-CONTRACT-FROZEN-C07.md:77`；`delivery-notes.md:57`/`:68` | changelog 2026-11-02 行仍写「pin 重算为 `5c48083f…`」，未注明最终 `3fdb44e4…`（与 §1/UNFREEZE 不一致）；交付说明 P1-05 处置行称 changelog 已一致（实际未改）；回归行掉字（`erify_pins`/`pi inventory`） | changelog 补最终 pin 或「中间→最终」；修交付说明与掉字 |
| P2-8 | `IHostController.cs:420-421`；`NullHostController.cs:539-564` | 接口注释称「never a silent success for a write」，而 Null/Fake 的 `ApplyCandidates→空字典`、`Discard→CompletedTask` 属 no-op 成功；`GetDraftAsync` null 同时表示未就绪/无 draft | 明确语义并补注释/测试 |
| P2-9 | `FEA-05_DRAFT_WIRE_CONTRACT.md:3`；`V11R_COMMAND_CONTRACT_V1.md` §8.2 | 6 命令已注册，但 FEA-05 契约与 §8.2 仍 `PENDING`（卡备注称 DSH 收口升级） | FEA-06 消费前升级并记录 |
| P2-10 | 卡 `:72`；`sln-test.log` | 基线 931/0/60 vs 本轮 949/0/57（+18 passed/−3 skipped；其中 15 为本卡新增测试，另 3 为历史 skip 变化）未说明 | DSH 说明 skip 变化或固定基线快照 |
| P2-11（新） | `DraftPortDefaultTests.cs`；`HostController.cs:2218-2401`（映射/异常传播） | 新测试未覆盖：① fake **成功**路径（返回 Draft/DraftLease 并断言）；② 真实 `HostController` 的 `ReadDraft/ReadEditToken` 映射（P1-01 修复无回归护栏）；③ dispatcher typed error → 端口异常传播；④ XOR「键存在但 null」边界；`drafts_open` 缺字段用例用字符串造数未测类型 | 建议 FEA-06 联调补集成测试，或对 `HostController` 增加 internal 可见性单测；`DraftCommandRegistryTests` 增 null 值与类型边界 |

---

## 6. 处置建议

1. **范围/实现结论：approved**（P0/P1=0）。P1-01…P1-05 全部关闭；新增 15 个测试真实、全绿且断言具体。
2. **DSH 收口步骤**：①按 UNFREEZE 纪律**重冻 C-07**（§1B 更新为 r3 approved+日期，pin 保持 `3fdb44e4…` 与字节一致）；②升级 FEA-05 契约 `PENDING→FROZEN` 与总契约 §8.2 状态（并顺手修正 P2-3 的 §2 口径）；③刷新卡 AC/证据表、status→`in_review`→`done`、修 Closeout stray CR；④修 P2-7（changelog 最终 pin/交付说明）与 P2-10（基线口径）。
3. P2 其余（1/2/4/5/6/8/9/11）可在收口批处理或转 FEA-06 前置；P2-11 建议写入 FEA-06 测试计划。

## 7. 边界声明

本报告只审实现与冻结范围/契约的一致性，**不构成集成验收**；真实 sidecar 端到端与 FEA-06 UI 消费**未验证**。本席位未参与 FEA-05-PORT-1 的实现或返修（实现者为 DSH），符合 2026-10-31「上下文独立」裁决；未修改被审文件、未 commit/push；行号基于 `24600bbee` 实测。
