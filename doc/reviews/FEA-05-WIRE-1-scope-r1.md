---
task_id: FEA-05-WIRE-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: 4dfc8abc4
reviewed_head: 4dfc8abc4
decision: changes_requested
counts: { P0: 3, P1: 5, P2: 6 }
---

# FEA-05-WIRE-1 范围复核 r1（独立上下文席位）

| 字段 | 值 |
|---|---|
| base_commit | `4dfc8abc4b3d9180ff44eda4c943e97c14a2bfec`（当前 `main` HEAD，`chore(status): 压缩 STATUS 至预算内`） |
| reviewed_head | 同上 `4dfc8abc4`（`git status --porcelain` 为空） |
| 被审草案提交 | `dcf32b98969186c52c83c94436f1013c0b2e6cd9`（建卡）；卡 frontmatter `base_commit: 4ad0b06b3` = 建卡前 head，与提交序一致 |
| 被审对象 | `doc/tasks/FEA-05-WIRE-1.md`（kind=implementation，status=proposed，108 行 / 6115 bytes） |
| reviewer | `fea05-wire-scope-reviewer` |
| reviewer 来源 | DSH Team Lead 派发，**fresh 独立上下文**（DSH 子 agent）；未参与 FEA-05-WIRE-1 的起草、实现或返修；只读被审 head |
| 日期 | 2026-11-02 |
| 审查范围 | **仅范围冻结文本**（AC1–AC7、写域、裁决点 W-1…W-3、契约边界、依赖顺序、可执行性、治理指针）。不含实现审查（尚无实现） |
| 结论 | **changes_requested** |
| 计数 | **P0 = 3 / P1 = 5 / P2 = 6（共 14）** |

> **一句话理由**：范围方向正确（Draft 命令面 wire 确为 FEA-03/04 顺延项，W-1 的「协议层兼容扩展」判断在 M2-C1 §3.2 下可成立），但**被审卡在三条硬约束上不可执行**：①命令面无契约载体，且 `CommandContractV11RTests` 的「注册表 ⊆ 契约清册」断言会直接失败；②`IHostController` 加 6 方法触发 C-07 冻结端口清单的「同 Task 必须更新」规则，而卡内 AC6/禁止范围明令不动 15 份 pin；③AC5 要求的 Python 协议测试没有对应写域（`tests/core/**` 缺失）。三条中的任意一条都会让实现者在「遵守卡」与「满足 AC」之间二选一。

---

## 0. 方法与只读声明

- 只读核查被审 head；**未修改任何被审文件**（卡、STATUS、PLAN、LEDGER、源码、测试、`verification/**` 均未改动），未 commit、未 push。
- **本报告是本轮唯一新增文件**（落在被审卡 `allowed_paths` 的 `doc/reviews/FEA-05-WIRE-1-*.md` 通配内）。
- **未执行**（明确声明）：`dotnet build`/`dotnet test`（sln 全量，FEA-04 口径 991 = 931 passed + 60 skipped）、`python -m pytest`、任何 UI/真机运行、任何源码写入。因此「931/0/60 在当前 head 仍成立」**未验证**，仅引用 FEA-04 已入库证据（见 §5）。
- 已执行（只读）：

| 命令 | 结果 | 证据 |
|---|---|---|
| `git rev-parse HEAD` | `4dfc8abc4b3d9180ff44eda4c943e97c14a2bfec` | 本报告头部 |
| `git status --porcelain` | 空（clean） | 同上 |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（2 warnings）**；`Task: doc\tasks\FEA-05-WIRE-1.md`；warn=10 个非终态 Task、`doc/STATUS.md` 达预算 80% | §6.1 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS（all 15）**；C07 `17c8f7016a36` 一致 | §3.1 |
| `python tools/generate_api_inventory.py --check` | **EXIT=0**（当前渲染 1/47/6=54 与 C-07 文档一致） | §3.2 |

---

## 1. 范围完整性（AC1–AC7 是否足以验收「Draft 命令面 wire」；写域是否覆盖/越界）

### 1.1 交付范围与 AC 覆盖

| 卡内层 | 位置 | 复核 |
|---|---|---|
| Core 白名单 6 命令 | 卡 `:56` | **不足**：未含契约清册登记；命令名与既有服务方法映射未列（§2.4/P1-01） |
| Core handler | 卡 `:57` | 部分：声明「含 token/candidate/receipt」「错误码透传既有结构」，但 draft 错误码在 `core_service.py` 中**0 命中**（新 wire code 面），须冻结映射（P0-01/P1-02） |
| CoreClient | 卡 `:58` | **漏 `HostCommandRegistry`**：`HostCommandDispatcher.InvokeAsync` 先 `HostCommandRegistry.Get(name)`（`HostCommandDispatcher.cs:59`），未注册即 `UNKNOWN_COMMAND`；且 registry 与契约清册有机械 parity 断言（P0-01/P1-05） |
| IHostController 6 方法 | 卡 `:59` | 与 C-07 冻结清单规则冲突（P0-02） |
| Host 转发 | 卡 `:60` | **结论正确但未给证据**：`NewManga.Host/**` 无命令转发表（`git grep 'cleanup_preview\|GetTaskProjection' -- src/NewManga.Host` 0 命中），Host 确无需改动；建议把「已核 = Host 无转发表」写成一行证据，避免 Owner 自行改 Host |
| 测试 | 卡 `:61` | **写域缺失**：Python 协议测试须落 `tests/core/**`（既有 `tests/core/test_core_service.py` 646 行等），不在 `allowed_paths`（P0-03） |

### 1.2 写域（`allowed_paths`，卡 `:22-36`）逐项判定

| 路径 | 判定 | 说明 |
|---|---|---|
| `doc/tasks/FEA-05-WIRE-1.md` | 合理 | 自卡 |
| `src/bootstrap/core_service.py` | 合理且**足够** | 白名单/dispatch/handler/`main()` 注入（`:5804-5814`）全在本文件；`CoreServices.drafts` 已由 FEA-03 装配（`core_assembly.py:760`、`:1310-1316`），**无需动 `core_assembly.py`** |
| `src/application/editing/**` | **过宽 / 与 AC2 冲突** | AC2 明令「不新增编辑语义」，但写域开放整个编辑域（5 文件 1900+ 行）便于顺手改语义；建议收窄为空或仅注明「只读，不改」 |
| `NewManga.CoreClient/**` | 合理 | 缺 registry/domain 明细（P1-05） |
| `App/Services/IHostController.cs`、`HostController.cs`、`NullHostController.cs` | 合理（**但触发 C-07**） | 全仓 3 个实现：`HostController.cs:12`、`NullHostController.cs:10`、`tests/NewManga.App.Tests/FakeHostController.cs:8`（后者在允许的 App.Tests 内，不会编译越界） |
| `tests/NewManga.CoreClient.Tests/**`、`tests/NewManga.App.Tests/**` | 合理但**含冻结契约对照测试** | `Commands/CommandContractV11RTests.cs`、`Commands/CommandParityContractTests.cs` 在此通配内 → 需补「不许弱化既有断言」红线（P1-05） |
| `verification/FEA-05-WIRE-1/**` | 合理 | 含 `evidence_dir`（模板 `TASK.md:38` 要求）✓ |
| `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` | 合理（`TASK_LEDGER` 须重跑生成器） | STATUS 预算已满（P2-02） |
| `doc/reviews/FEA-05-WIRE-1-*.md` | 可接受 | 与 FEA-04b 卡先例一致；FEA-04 采用「Review 不在卡写域」的另一口径，二者都可，建议统一 |

**写域缺口（按严重性）**：①无任何契约载体路径（`doc/contracts/**` 全缺）→ P0-01；②无 `doc/plan/FEA-C07_API_INVENTORY.md` 与 UNFREEZE 载体 → P0-02；③无 `tests/core/**`（Python 协议测试）→ P0-03；④无「允许修改范围」散文节与共享接口变更单列 → P1-03。

**写域过度**：`src/application/editing/**`（P1-03）；`tests/**` 未按「只新增、不改既有断言」设限（P1-05）。

### 1.3 AC1–AC7 可验收性（逐条）

| AC | 判定 | 缺口 |
|---|---|---|
| AC1 白名单+handler/未知命令拒绝（`:65`） | **不可验收** | 「6 条命令在**白名单**登记」表述不准确：`core_service.py` 无独立白名单，是 `_dispatch_request` 分支（`:5440-5455` 为未知命令兜底）；且未要求契约清册行（P0-01）、未要求 `drafts` 未注入时 fail-closed `CORE_UNAVAILABLE`（`_require_cleanup` 先例 `:1918-1928`） |
| AC2 语义不变（`:66`） | 不可机械验证 | 无 payload/result 映射表，无法判断「只调用既有服务」；缺映射即无法判「不新增规则」（P1-02） |
| AC3 CoreClient 映射（`:67`） | **不完整** | 漏 `HostCommandRegistry`/`HostDomainService`/`V11RAdditiveCommandNames`/parity 测试同步；漏 `HostCommandDomain` 域归属（现 6 域闭集 `HostCommandModel.cs:5-13`）（P1-05） |
| AC4 IHostController 面（`:68`） | **不可满足** | 与 C-07 冻结清单「同 Task 更新」+ pin 规则冲突（P0-02） |
| AC5 测试（`:69`） | **不可满足** | Python 测试无写域（P0-03）；CoreClient 侧 parity 断言会因未登记契约而失败（P0-01）；命令形式非冻结形式（P2-01） |
| AC6 契约字节（`:70`） | **自相矛盾** | 「不改 15 份 pin」与 C-07 必改冲突；后半句「若属新契约需 DSH 裁决并登记」是**条件句**，不构成可验收项，且未写载体/路径（P0-01/P0-02） |
| AC7 证据（`:71`） | 可验收 | 与模板 `TASK.md:61-66` 一致 |

---

## 2. 裁决点（W-1/W-2/W-3）与未登记裁决点

### 2.1 W-1「命令面 = M2-IPC1 兼容扩展而非新契约」（卡 `:83`）

- **结论方向可成立，但不完整，且引用依据反了。**
- **可成立的部分**：M2-C1 §3.2 允许同 major 的 additive command widening（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:129-132` 逐次「只新增命令」先例）；`PROTOCOL_MINOR` 当前 3，`dispatch_request` 按族投影 minor（`core_service.py:5468-5476`），故 Draft 族落在默认面**确实可以零 bump**——同族先例见 `_REGION_WRITE_COMMANDS` 注释（`core_service.py:451-457`「same per-command family minor (3)… zero protocol bump」）与 `doc/contracts/V11R_REGION_WRITE_CONTRACT.md:39-59`（明写 minor 策略为「明确决定，非默认」）。
- **引用依据错误（P1-04）**：卡引 `core_service.py:269-287` 作为「commands added 兼容扩展」先例，但该段注释的每一行恰恰是**因为新增命令而 minor bump**（`0→1`、`1→2`、`2→3`、`3→4`、`4→5`、`5→6`）。按该「先例」实现会去改 `PROTOCOL_MINOR`，而 V11R 契约 §1.1 第 3 条明写「bump 会改变所有客户端声明的 envelope 版本，属于未授权共享契约变更」。
- **不完整的部分（P0-01 的裁决面）**：M2-C1 的历次命令新增均伴随**文档 rev + §5 command catalog 行 + 错误码映射**（如 `M2-C1:3` 明写 rev 2.11「修订范围：§3.2、§5 command catalog、§5.12、§11、§12」）；V11R 侧另有 `doc/contracts/V11R_COMMAND_CONTRACT_V1.md` 命令清册（C001–C066 + C067–C077 PENDING）且其 `:241-242` 规定「C067–C077 在……由 DSH 签发前，任何一方不得当稳定契约消费」。而本卡选定的 draft 错误码（`EDIT_TOKEN_*`/`DRAFT_*`/`STYLE_KEY_NOT_ALLOWED`/`LOCK_CHANGED` 等）在 `core_service.py` 全文件 **0 命中**，即**新 wire 错误码字面值**——正是 FEA-03 `:153` L-2 与 FEA-04 `:99` L-2 要求「先完成 M2-C1」的情形。

### 2.2 W-2「不接 Current UI」（卡 `:84`）

- **合理**：与 FEA-04 Q-16（`doc/tasks/FEA-04.md:48`「本卡不实现 wire…wire 接线由 FEA-05/FEA-07 承担」）与 Q-19 一致；把 UI 改造留给后续卡可避免同卡混改。
- **两点须修**：①承接指针 `FEA-06`（Fluent）**不在当前 DAG**——`doc/REBASELINE_PLAN.md` 只有 `FEA-05-WIRE-1` 一行（`:18`），全仓 grep `FEA-06` 仅见于 `doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md:645,927`；Q-16 原文写的是 **FEA-05/FEA-07**（`:48`）。应改为「后续卡（待 DSH 释放）」或 `FEA-07` 并给 doc 指针（P2-04）。②「不接 UI」与「本卡加 6 个 `IHostController` 方法」存在张力：若本卡不接 UI，这些端口在生产上暂时无消费者，却要为此承担 C-07 pin 变更成本 → 建议直接剔除端口面（见 §7 处置建议 b）。

### 2.3 W-3「错误语义」（卡 `:85`）

- **方向合理但不完整**：既有信封为 `{code, category, message, retryable, details?}`（`make_error_envelope`，`core_service.py:808-825`），卡只写「code/message/details」，漏 `category`/`retryable`；更关键的是 `DraftError` 的 `cause_code`/`details` 如何投影未定（`drafts.py:775-782` `_journal_error`），且**每个 draft 码的 category/retryable 必须逐条冻结**（M2-C1 §5.1 错误码族先例）——并入 P1-02。

### 2.4 未登记的裁决点（应登记而卡内无）

| # | 未登记点 | 影响 |
|---|---|---|
| U-1 | 6 命令与既有服务方法的**逐一映射**（`drafts.close`/`drafts.status` 二义，见 P1-01） | 可实现两种相反语义，其一丢用户编辑 |
| U-2 | EditToken 传输/TTL/续发、SessionId 归属（`open_draft` 需 `session_id`+`page_binding_version`，`drafts.py:97-105`；token 由 `issue_edit_token(ttl_seconds)` 单次签发 `:148`、`:286`） | 长会话 token 过期后无命令恢复 → 应用无法提交 |
| U-3 | 是否出 `drafts.flush(trigger)`（C-13 SC-D02 强制 flush 点：切页/切工作面/退出/关窗/Run 提交，`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:47-54`；服务侧 `force_flush/flush_pending`，`drafts.py:576-589`） | R-DRAFT-2 强制 flush 点在 wire 上不可达 |
| U-4 | Core 退出（`core.shutdown`）时活动 Draft 的 flush/清理语义 | 退出路径可能丢未落盘 patch |
| U-5 | 命令命名与域归属：core 路由 `drafts.open` vs Host 命令名（现网为 snake_case，如 `cleanup_preview`）、是否新增 `HostCommandDomain.Drafts` 或塞进既有 Region 域（`HostCommandModel.cs:5-13` 6 域闭集 + `DomainServices.cs:40-97` 每域一个服务类） | registry 形状变化会牵动 parity/domain 计数断言 |
| U-6 | `drafts` 未注入时 fail-closed `CORE_UNAVAILABLE`（对照 `_require_cleanup` `core_service.py:1918-1928`） | 测试/旧装配构造 `CoreServiceServer` 时行为未定 |

---

## 3. 契约边界（15 份 pin / C-02/C-03/C-04b/C-08 / C-07 / C-13 / M2-C1 / 命令清册）

### 3.1 冻结 pin 与字节

- `verify_pins.ps1` 受检 15 份 = 12 份 `doc/plan/FEA-C*_DRAFT.md` + `FEA-C07_API_INVENTORY.md` + `FEA-01_CONTRACT_DRAFT.md`（`tools/governance/verify_pins.ps1:6-13`）。本卡 `allowed_paths` **不包含**其中任何文件，故「不动 C-02/C-03/C-04b/C-08 字节」在写域上成立。
- **但**：①卡 `:75` 只列 C-02/C-03/C-04b/C-08，与 AC6 `:70` 的「15 份 pin」口径不一致（P2-06）；②**C-07 就是 15 份之一**，而本卡按设计必须改它 → 见 §3.2（P0-02）；③卡未声明「不改直接上游 C-13 字节」——C-13 只管草稿/保护语义、不含 IPC 面（全文 grep `wire|IPC|命令` 仅 `:102` 一处同名异物），故 C-13 无需动，但应显式写清，避免 Owner 误以为要改（并入 P1-02）。

### 3.2 C-07 端口清单：冻结规则与卡内禁令直接冲突（P0-02）

- C-07 冻结规则：`doc/plan/FEA-C07_API_INVENTORY.md:11-13`「**新增/删除端口方法时，同一 Task 内必须同步更新本清单**」；`:24`「36 个基线签名不得变，11 个为新增（additive）；**冻结后同样只允许追加**」。冻结记录 `doc/plan/FEA-CONTRACT-FROZEN-C07.md:15-17` 规定「条款字节自本记录起不得改动；修订须走 UNFREEZE 载体 + 重新独立复核 + 重新冻结」，`:42` 再次写「新增/删除端口方法须在同一 Task 内重跑脚本并更新清单，diff 即审查信号」。
- 机械后果：当前 `IHostController` 47 成员（`:17-22` 统计表；本轮 `generate_api_inventory.py --check` = **EXIT 0**），卡 `:59/:68` 要加 6 → 53 成员。`tools/generate_api_inventory.py:159-179` 在 `--check` 模式下把**从源码渲染的计数**与 C-07 文档行逐条比对，任一不符即 `EXIT 1`。因此「加 6 方法且不动 C-07 字节」在机械上不成立。
- 结论：AC6 `:70`「不改 15 份冻结 pin」+ 禁止范围 `:75` 与 AC4 `:68` **互斥**；且 `doc/plan/FEA-C07_API_INVENTORY.md`、`doc/plan/FEA-CONTRACT-FROZEN-C07.md`、UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）全不在写域。

### 3.3 命令清册与 M2-C1：无契约载体（P0-01）

- 机械门禁：`apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandContractV11RTests.cs:68-86`——`HostCommandRegistry.All.Keys` 中**每一条命令都必须在 `doc/contracts/V11R_COMMAND_CONTRACT_V1.md` 的 baseline 行或 PENDING 行中声明**，否则 `Assert.True(undeclared.Length == 0)` 失败并打印缺登记命令名。该测试属于 `dotnet test NewManga.sln`（AC5 的验收命令）→ **AC1/AC3 一落地，AC5 必红**。
- 既有 additive 先例不是「免登记」，而是「登记在契约 + 不动冻结快照」：`HostCommandRegistry.cs:12-23`「Both are additive to the frozen 66-command snapshot (the snapshot file is NOT edited)…ride the SAME per-command Core minor (3)…zero protocol bump, see `doc/contracts/V11R_REGION_WRITE_CONTRACT.md`」；parity 测试同时要求注册表新增集合**恰好等于** `V11RAdditiveCommandNames`（`CommandParityContractTests.cs:88-91`，集合定义 `HostCommandRegistry.cs:310`）。
- 上游明文前置：FEA-03 `:153` L-2「若从 `CoreServiceServer` 命令面暴露新码/新增命令 → `blocked`+M2-C1」；FEA-04 `:99` L-2「**需透传 Draft 命令 → `blocked`（FEA-05/07 + 先完成 M2-C1）**」。被审卡 §来源与授权链（`:43-46`）只引 Q-8/Q-16，**未引这两条 L-2，也未提 M2-C1**。
- 命令清册当前状态：`doc/contracts/V11R_COMMAND_CONTRACT_V1.md:1-3` 状态 `ISSUED`（非 FROZEN）、基线 66 条 + `:220-242` C067–C077 `PENDING`（且明写「DSH 签发前不得当稳定契约使用」）——Draft 面（C078+）无任何登记位。

---

## 4. 依赖与顺序

| 项 | 判定 | 证据 |
|---|---|---|
| `depends_on: FEA-03 / FEA-04` | **成立** | 两者均 `done`：PLAN `:15`（FEA-03 集成 `76d947923`）、`:16`（FEA-04 集成 `f4d8a32ec`）；卡 frontmatter `:11-13`；实现面确由两者交付（`application/editing/**` 服务、CoreClient/IHostController 现状） |
| 与 FEA-04b（`in_review`）冲突 | **无写域冲突** | FEA-04b 只写 `doc/design/fluent-v1/**` + `verification/FEA-04b/**`（卡 `:21-28`），与本卡零交集 |
| 是否须等 FEA-04b AC5 用户确认 | **不必等待，可并行**；但须在卡内写明 | FEA-04b AC5 是「用户确认 + 独立 Review + DSH 冻结」（`doc/tasks/FEA-04b.md:65`、`:111-112`），对象是 Fluent 四页设计基线；Draft wire 与视觉基线无数据/协议耦合。建议卡内加一句「与 FEA-04b AC5 无依赖，可并行」，避免后续误判 Ready 顺序（P2-04） |
| 顺序风险 | DSH 前置应先于 `ready` | P0-01/P0-02 的载体（契约 rev、C-07 UNFREEZE）只能由 DSH 签发；若在 `ready` 后补，Codex 会先撞红测试再等治理 |

---

## 5. 可执行性（工作量/测试面/隐藏风险）

### 5.1 工作量估算（单卡）

- Python：`core_service.py` 新增 1 个族集合 + 1 个首部 docstring 段（该文件每族都在模块 docstring 登记，见 `:106-128`）+ 6 handler + envelope/错误投影表 + `main()` 注入 1 行（`:5804-5814`）+ `__init__` 形参（`:1032-1052`）≈ 150–250 行。
- C#：6 typed 模型 + Dispatcher 6 分支（`HostCommandDispatcher.cs:185-300` 附近）+ Registry 6 描述符 +（可能）`HostCommandDomain` 新成员/`HostDomainService` 子类（`HostCommandModel.cs:5-13`、`DomainServices.cs:40-97`）+ `CoreServiceClient` 6 方法 + `IHostController` 6 方法 × 3 实现（`HostController.cs` 2214 行、`NullHostController.cs` 539 行、`FakeHostController.cs`）≈ 300–500 行。
- 测试：Python 协议 6–12 例、CoreClient 序列化/分发/错误映射 6–12 例、App fake 行为 6 例，另需改 `CommandParityContractTests` 的 additive 集合断言 + `CommandContractV11RTests` 契约行。
- 治理：1 份契约载体 + C-07 UNFREEZE/refreeze + `generate_api_inventory.py` 重跑 + STATUS/PLAN/LEDGER 三指针 + 证据表。
- **判断：单卡可完成，但失败面横跨 Core/协议/治理三层**，且三处 P0 中两处卡在 DSH 手上。建议拆分或明确 kill-criteria（P2-05）。

### 5.2 隐藏风险（卡内未覆盖）

1. **JSON-lines 信封**：请求/响应 minor 由服务端按族投影（`core_service.py:5468-5476`），若实现者照卡 W-1 的「bump 先例」误改 `PROTOCOL_MINOR`，会同时改变**所有既有族**的响应 minor，属契约破坏（P1-04）。
2. **错误码面大部分为新增**：`drafts.py` 抛出 17 个码，其中仅 `LOCK_CHANGED`、`TARGET_NOT_FOUND` 在 `core_service.py` 已有 wire 投影（复用）；`EDIT_TOKEN_{EXPIRED,INVALID,REUSED}`、`DRAFT_{APPLY_FAILED,CANDIDATE_INVALID,CANDIDATE_NOT_FOUND,FLUSH_TRIGGER_INVALID,INVALID,JOURNAL_UNWRITABLE,NOT_FOUND,OWNER_CHANGED,PATCH_INVALID,READ_ONLY}`、`STALE_BASE_REVISION`、`PAGE_SIZE_UNAVAILABLE` 共 15 个在 `core_service.py` **0 命中**（本轮 `git grep -c` 实测）。这些码的 `category`/`retryable` 映射若由实现者即兴决定，将形成**未冻结 wire 语义**（P1-02）。
3. **并发**：`DraftProtectionService` 用自锁 + 后台防抖定时线程（`_schedule_flush`/`_debounced_flush`，`drafts.py:711-728`），而 Core 的 stdio 循环以 `_write_lock`/`_projection_lock` 串行化命令（`core_service.py:1061-1062`）。wire handler 直接调用服务时，flush 线程与 apply 的交互需测试覆盖（卡内无此测试项）。
4. **回执/幂等**：`apply_candidates` 有 receipt 重放语义（`drafts.py:389-407`），wire 必须原样透传 `revisionIds` 与 `EDIT_TOKEN_REUSED`，不得再包一层「成功」；卡内 AC 未提回执重放测试。
5. **退出路径**：`core.shutdown` 分支（`core_service.py:5428-5438`）当前不通知 drafts；`CoreServices.close()` 只关 journal（`core_assembly.py:792-807`）。活动草稿的退出 flush 在 wire 上无落点（U-4）。
6. **下游耦合**：C-13 `:94` 规定「导出/删除 preflight 前必须 flush 或显式提示有未保存草稿」，该项由后续导出/删除 Task 承接；本卡若不出 flush/状态查询命令，会让下游任务再次受阻（应作为已知限制登记）。

### 5.3 测试基线口径

- AC5 引「基线 931/0/60」有据：`doc/handoffs/FEA-04-68c72ba57.md:184`、`verification/FEA-04/build-test-raw.log`（FEA-04 r2 P1-02 关闭后入库）、`doc/reviews/FEA-04-r3.md:21` 独立复跑。**本席位未复跑该命令**（见 §0），只确认引用链存在且一致。
- 但 AC5 文本 `:69` 写 `dotnet test apps/desktop-avalonia/NewManga.sln`（缺 `--no-build --settings .../NewManga.runsettings`），与 FEA-04 r2 P1-02 要求的冻结命令不同形式（P2-01）。

---

## 6. 治理（check.ps1 / verify_pins / STATUS-PLAN-LEDGER 指针）

### 6.1 只读检查结果

| 检查 | 结果 |
|---|---|
| `check.ps1` | **PASS（2 warnings）**。Governance scope=15 当前文档；`Task: doc\tasks\FEA-05-WIRE-1.md`（STATUS 指针可解析，`:7`）；warn1=10 个非终态 Task；warn2=`doc/STATUS.md` 达预算 80%（实测 **3124 bytes / 45 lines**，预算 `Bytes=3200/Lines=45`，见 `check.ps1:614-621` —— 行数**已到上限**，字节剩 76） |
| `verify_pins` | **PASS（all 15）**，C07 `17c8f7016a36` 与冻结记录一致 |
| `generate_api_inventory.py --check` | **EXIT 0**（1/47/6=54 与 C-07 一致） |
| AC 标记 | 7 条 AC 均以 `<<TODO>>` 结尾；`check.ps1:814-830` 的 v3 AC 门只在 `in_review/approved/done/closed_with_limitations` 生效，故 `proposed` 下合规；转 `in_review` 前必须替换为 `<<MET>>`/`<<PARTIAL: …>>` 等（提醒 Owner） |

### 6.2 三指针一致性

| 指针 | 内容 | 判定 |
|---|---|---|
| `doc/REBASELINE_PLAN.md:18` | `FEA-05-WIRE-1 \| FEA-03、FEA-04 \| **proposed**` | ✓ 与卡一致 |
| `doc/STATUS.md:7` | 当前 Task = FEA-05-WIRE-1 `proposed`；上一 FEA-04b `in_review`（r5 approved，AC5 待确认）；FEA-04 done `f4d8a32ec`/931/0/60 | ✓（与 PLAN `:16-18`、FEA-04b 卡 `:111-112` 一致） |
| `doc/TASK_LEDGER.md:46` | `FEA-05-WIRE-1 \| proposed \| own row` | ✓ |
| 小瑕疵 | STATUS `:11` 同时把该卡列为「下一候选」；STATUS `:19` 的 LEDGER 计数（483=471+11+1）已陈旧（当前 `TASK_LEDGER.md:9-13` = 491 files / 480 terminal / 10 non-terminal） | P2-03 |

---

## 7. Findings

| ID | 级别 | 位置 | 问题（触发与影响） | 建议 |
|---|---|---|---|---|
| **P0-01** | P0 | 卡 `:56`、`:58`、`:65`、`:67`、`:70`（AC1/AC3/AC6）↔ `CommandContractV11RTests.cs:68-86`；`HostCommandRegistry.cs:12-23`、`:310`；`CommandParityContractTests.cs:88-91`；`V11R_COMMAND_CONTRACT_V1.md:220-242`；`FEA-03.md:153` L-2；`FEA-04.md:99` L-2 | **命令面无契约载体 → AC5 必红。** 注册表新增命令后，`RegistrySurface_IsFullyDeclared` 断言「每条注册命令必须在 `V11R_COMMAND_CONTRACT_V1.md`（baseline/PENDING 行）声明」，红；parity 测试另要求新增集合恰等于 `V11RAdditiveCommandNames`。而 Draft 错误码在 `core_service.py` 大面积 0 命中（17 个中 15 个为**新 wire code**，仅 `LOCK_CHANGED`/`TARGET_NOT_FOUND` 复用，见 §5.2-2），M2-C1 历次「命令 added」均走 doc rev + §5 catalog + 错误码映射；FEA-03/FEA-04 的 L-2 明文要求「先完成 M2-C1」。卡内 W-1 只论协议层兼容、未登记载体与登记动作，`allowed_paths` 亦无 `doc/contracts/**` | DSH 二选一：**(a)** 先签发命令面契约载体——新建 `doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md`（逐命令 payload/result/错误码+category/retryable，参照 `V11R_REGION_WRITE_CONTRACT.md` 结构）并在 `M2-C1` §5 catalog/§3.2 记 rev、在 `V11R_COMMAND_CONTRACT_V1.md` §8 增 C078+ 行；把上述文件加入写域，或声明为 DSH 单点提交；**(b)** 若判定无需新契约，须在卡内**逐条**写明依据（M2-C1 §3.2 + 既有 additive 先例）并说明为何 L-2「先完成 M2-C1」不适用，且仍需让命令清册可声明（否则 AC5 不可达） |
| **P0-02** | P0 | 卡 `:59`、`:68`（AC4）、`:70`（AC6）、`:75`；`FEA-C07_API_INVENTORY.md:11-13`、`:24`；`FEA-CONTRACT-FROZEN-C07.md:15-17`、`:42`；`generate_api_inventory.py:159-179`；`verify_pins.ps1:10` | **C-07 冻结规则与卡内禁令互斥。** `IHostController` 由 47→53，`generate_api_inventory.py --check` 必 `EXIT 1`；C-07 冻结记录要求「新增端口方法须在同一 Task 内重跑脚本并更新清单」，而更新冻结字节须走 UNFREEZE + 重复核 + 重冻结（pin 必变）。卡内 AC6「不改 15 份 pin」+ 禁止范围把 Owner 逼进死局；写域也缺 C-07 文档与 UNFREEZE 载体 | **(a) 推荐：收窄本卡**——本卡只做 Core 命令面 + CoreClient（Dispatcher/Registry/typed 模型），**不加 `IHostController` 方法**（W-2 已声明不接 UI，端口暂无人消费），把端口面 + C-07 UNFREEZE 留给真正接 UI 的后续卡；或 **(b)** 保留端口面但由 DSH 在 `ready` 前完成 C-07 UNFREEZE/refreeze（`doc/reviews/CONTRACT-UNFREEZE-2026-11-0X.md` + 更新冻结记录 pin + 重跑生成器），并把 `doc/plan/FEA-C07_API_INVENTORY.md` 与冻结记录加入写域（或声明 DSH 单点） |
| **P0-03** | P0 | 卡 `:61`（测试）、`:69`（AC5）、`:91`（测试要求表）、`:22-36`（`allowed_paths`） | **Python 协议测试无写域。** 既有 Core 命令测试全部在 `tests/core/**`（`tests/core/test_core_service.py` 646 行、`test_core_service_retype.py`、`test_core_service_settings.py`），不在 `allowed_paths`；AC5 与测试要求表却要求 `python -m pytest tests/ -q` 覆盖新增协议行为。实现者只能在写域外落测试（越权）或伪装证据 | 写域增 `tests/core/test_core_service_drafts.py`（**仅新增文件，不开放整个 `tests/core/`**，避免与其他线冲突）；若需改既有测试 fixture，则逐个列名并说明理由 |
| **P1-01** | P1 | 卡 `:56`、`:66`（AC2）；`drafts.py:97-149`、`:165-184`、`:215-233`、`:234-257`、`:286-302`、`:304-368`、`:374-377`、`:552-589`；`FEA-C13_DRAFT_PROTECTION_DRAFT.md:47-54` | **6 命令映射二义 + 关键命令缺失（含数据丢失风险）。** `drafts.close` 可映射 `discard_draft`（丢弃并删 journal/receipt）也可映射 `end_session`（先强制 flush 再清会话）——语义相反；`drafts.status` 可映射 `get_draft` 或 `list_drafts`；`drafts.prepare` 的 `origin`（枚举）/`draft_id`/`base_revision_id`、`drafts.apply` 的 `EditToken` 与 `candidate_ids`、`open_draft` 必需的 `session_id`/`page_binding_version` 均未在卡内定。另缺 `flush(trigger)`（C-13 SC-D02/R-DRAFT-2 强制 flush 点）、`resolve_text_conflict`（CONFLICTED 后无解除通道）、token 续发 | 给出「卡内命令 → 服务方法 → 请求字段 → 结果字段」四列表，并**把 close 拆成 `drafts.discard`（丢弃）与 `drafts.end_session`（flush+关会话）两条**；补 `drafts.flush(trigger)`（trigger 取值对齐 `_FLUSH_TRIGGERS`）；显式登记 `resolve_text_conflict`/token 续发为 deferral 及承接指针 |
| **P1-02** | P1 | 卡 `:57`、`:66`（AC2）、`:85`（W-3）；`make_error_envelope`（`core_service.py:808-825`）、`drafts.py:775-782`；`M2-C1:40-43` | **无 payload/result/错误码冻结，AC2 不可机械验证。** W-3 只写「复用 code/message/details」漏 `category`/`retryable`；DraftError 的 `cause_code`/`details` 投影未定；`EDIT_TOKEN_*`/`DRAFT_*` 等属新 wire 码，需逐条冻结 category/retryable（M2-C1 §5.1 先例）；命令命名（`drafts.open`）与 Host 命令名/域归属未登记（`HostCommandModel.cs:5-13` 6 域闭集） | 把「逐命令 payload/result/错误码（含 category/retryable）」作为独立交付物（可并入 P0-01 的契约载体），并补一张 wire 码→投影映射表进 AC1；登记命令命名/域归属裁决（U-5） |
| **P1-03** | P1 | 卡 `:22-36`、`:52-61`、`:73-77`；`doc/templates/TASK.md:34-42`、`:50-52` | **模板节缺失 + 写域结构失衡。** 缺「允许修改范围」节（模板要求「共享接口、Schema、依赖变更单列」——本卡恰改共享端口与 Core 命令面/错误码）与「依赖、风险与阻塞」节（要求区分硬依赖/可并行、记录未定契约及解除标准）；同时 `src/application/editing/**` 全开放与 AC2「不改语义」矛盾 | 补两节；把共享接口/契约/错误码变更单列为「共享面变更」小节并标注治理前置（P0-01/P0-02）；把 `src/application/editing/**` 从写域移除或注明「只读」 |
| **P1-04** | P1 | 卡 `:83`（W-1 依据列）；`core_service.py:266-292`、`:451-457`、`:5468-5476`；`V11R_REGION_WRITE_CONTRACT.md:39-59` | **W-1 引用依据与结论相反。** 卡引 `core_service.py:269-287` 为「commands added 兼容扩展」先例，但该段每行都是「新增命令 → minor bump」；正确依据应为 `_REGION_WRITE_COMMANDS` 注释（`:451-457`）+ V11R 契约 §1.1「零 bump 是明确决定」+ `dispatch_request` 的族级 minor 投影。按错误先例实现会去改 `PROTOCOL_MINOR`，违反 V11R §1.1 第 3 条（未授权共享契约变更），并改变**所有**族的响应 minor | 改写 W-1 依据列（引 `:451-457` 与 V11R §1.1），并在 AC1 明确「`PROTOCOL_MINOR` 保持 3，drafts 族按默认面响应 minor=3，零 bump」 |
| **P1-05** | P1 | 卡 `:58`（AC3）、`:30-31`（测试写域）；`HostCommandModel.cs:5-13`；`HostCommandRegistry.cs:12-23`、`:267-320`；`CommandParityContractTests.cs:88-91`；`CommandContractV11RTests.cs:68-86`；`DomainServices.cs:40-97` | **CoreClient 交付面漏项 + 缺「不许弱化断言」红线。** 卡只写「HostCommandModel/HostCommandDispatcher（或等价）」，未提 registry 描述符、`V11RAdditiveCommandNames`/新增 additive 集合、domain 归属与 `HostDomainService`、以及两处 parity 测试的同步；同时测试写域包含**冻结契约对照测试**，实现者可改断言绕过契约登记（FEA-04 r1 F-09 已有同类裁定） | AC3 补 registry/domain/parity 交付项与「新增集合断言如何扩展」；在禁止范围加「不得弱化/删除既有契约对照断言（只允许新增）」，并把测试写域收窄到新增测试文件（或明确列出允许修改的两处断言及理由） |
| **P2-01** | P2 | 卡 `:69`（AC5）、`:93`（测试要求表） | AC5 正文命令缺 `--no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings`（表格行有），与 FEA-04 r2 P1-02「命令须为冻结形式」的教训不一致 | AC5 正文改为冻结命令全串，或引用测试要求表行号 |
| **P2-02** | P2 | 卡 `:33`（`doc/STATUS.md` 写域）；`check.ps1:614-621`；实测 STATUS 3124 bytes / 45 lines | STATUS **行数已达上限 45/45**、字节 97.6%，任何新增行都会使 `check.ps1` 报「超过防膨胀预算」；本卡的 STATUS 更新（当前 Task 收口/下一候选）必然新增内容 | 卡内加一行前置：「STATUS 需在同一提交内压缩至 ≤45 行/≤3200 bytes，保留 DAG 指针与 Gate 行」；或由 DSH 先压缩再释放 |
| **P2-03** | P2 | `doc/STATUS.md:19` ↔ `doc/TASK_LEDGER.md:9-13`、`:46` | STATUS 的「检查器债务」行仍写 `LEDGER 483 = 471 终态 + 11 非终态 + 1 无 status`，当前 LEDGER 为 491 files / 480 terminal / 10 non-terminal；该行为当前声明（非历史），`check.ps1` 不校验该口径故未报错 | 本卡更新 STATUS 时顺手刷新该行，或由 DSH 单独更正（不属本卡阻断项） |
| **P2-04** | P2 | 卡 `:84`（W-2）、`:43-46`（来源链）；`FEA-04.md:48`、`:114`；`REBASELINE_PLAN.md:17-18`；`FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md:645` | W-2 承接指针写「FEA-06（Fluent）」，但当前 DAG 无 FEA-06（Q-16 原文为 FEA-05/**FEA-07**）；且卡内未写「与 FEA-04b AC5 无依赖、可并行」，易被误读为需等待设计基线 | 承接指针改为「后续卡（待 DSH 释放）/ FEA-07，见 `doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md:645`」；在「依赖、风险与阻塞」节写明与 FEA-04b 无依赖、可并行（FEA-04b 写域 `doc/design/fluent-v1/**`） |
| **P2-05** | P2 | 卡 `:52-61`、`:104` | 工作量/失败面未评估：Core 协议 + C# 客户端 + 端口(3 实现) + 3 套测试 + 契约/清单治理同卡；`Resource Manifest` 直接写「无 worktree（实现提交由 DSH 集成）」，与 FEA-03/04 使用独立 worktree 的先例不同，未说明理由 | 若按 P0-02(a) 收窄，问题自然缓解；否则写明 kill-criteria（如「契约载体未签发则 `blocked`」）与是否使用独立 worktree |
| **P2-06** | P2 | 卡 `:70`（AC6）↔ `:75`（禁止范围）；C-13 边界 | AC6 写「15 份 pin」，禁止范围只列 C-02/C-03/C-04b/C-08，口径不一；且未声明「不改直接上游 C-13 字节」（C-13 不含 IPC 面，实际无需改，应显式写清以免误改） | 统一为「不改 15 份受 pin 文件字节（唯一例外：C-07 按 §P0-02 处置）」；补「C-13 字节不动；C-13 语义（SC-D02/D04/D06）作为 wire 语义依据」 |

---

## 8. 处置建议（最小成本路线，供 DSH 选择）

1. **先裁决 P0-01 的载体问题**（二选一：签发 Draft wire 契约载体 / 说明 L-2 不适用并让清册可声明）。这是 AC1/AC3/AC5 的前置，且只有 DSH 能做。
2. **裁决 P0-02**：推荐收窄——本卡剔除 `IHostController` 6 方法与 `App.Tests` 写域，只交付「Core 命令面 + CoreClient（含 registry）」，C-07 端口面与 UNFREEZE 留给后续接 UI 的卡。若保留端口面，则由 DSH 先做 C-07 UNFREEZE/refreeze 并把相关路径加入写域。
3. **补写域**：`tests/core/test_core_service_drafts.py`（仅新增文件）；`src/application/editing/**` 改为只读。
4. **补冻结内容**：逐命令 payload/result/错误码（含 category/retryable）表；6 命令→服务方法映射（拆 `close`、补 `flush`）；token/session 语义。
5. **改 W-1 依据**、补模板两节（允许修改范围 / 依赖、风险与阻塞）、补「不许弱化既有断言」红线、修正 W-2 指针、冻结 AC5 命令形式、登记 STATUS 预算约束。
6. 完成后派 **范围复核 r2**；P0/P1=0 后再置 `ready`。

## 9. 边界声明

本报告**只审范围冻结**（Task 卡文本及其引用的上游卡、契约、代码/测试事实、治理指针），**不构成实现验收**，也不构成任何设计、契约或架构批准。结论中的「通过/不通过」仅指：该范围文本是否可执行、可机械验证、与上游 L 前置及治理指针一致。实现期的一切 AC 仍需独立实现复核与 DSH 集成验证。

本席位（`fea05-wire-scope-reviewer`）**未参与** FEA-05-WIRE-1 的起草、实现或返修，**未执行** `dotnet build`/`dotnet test`/`pytest`/UI 真机运行，**未修改**任何被审文件、卡、STATUS、PLAN、LEDGER、契约或源码，**未** commit/push。报告内所有代码行号基于 `4dfc8abc4` 实测，行号存在性不证明调用链完整；标注「未验证」的项不得当作已核实事实引用。
