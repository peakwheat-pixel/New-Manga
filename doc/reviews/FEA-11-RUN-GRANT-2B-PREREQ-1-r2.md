---
task: FEA-11-RUN-GRANT-2B-PREREQ-1
title: FEA-11-RUN-GRANT-2B-PREREQ-1 r2 窄面复审（C-16 v1.4 UNFREEZE 最终字节）
reviewer: fresh subagent（独立上下文；未参与起草、未参与 r1、未参与实现；只读被审字节）
session: e032ed9a-ed9d-4282-bfc8-1a1fbe51ea29（`$DSH_SESSION_ID` 实测；以 Lead 记录为准）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent（r2 窄面 byte-level 复审；未参与 C-16 v1.4 起草、r1 复核、FEA-11-RUN-GRANT-1/2 实现）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: a0bafc89ec74be08e3d6d721105639df01a140a7（复核开始时 1b6152112；复核期间 2A 提交 aa0a5562b/a0bafc89e 仅触 `apps/**`，UNFREEZE 面字节未变）
verdict: approved
---

# C-16 v1.4 UNFREEZE（容器多成员 entry）· r2 窄面复审（最终字节）

> **结论先行：`approved`。P0=0 / P1=0 / P2=0 / P3=11（r1 遗留 OPEN 6 项 + 本轮新增 5 项；r1 的 P3-1/P3-7 已 CLOSED、P3-8 已 ACCEPTED）。**
>
> - **A（P1-1 关闭）PASS**：`FEA-C16:68` 已把「条目数超 `budget.max_entries`」固定为 **`SOURCE_BUDGET_EXCEEDED`（不截断）**，只有其余结构/身份类项不满足才 `SOURCE_ACCESS_DENIED`/整 grant 拒绝；与 `source_read_refs.py:172-173`、`:902-905` 及 §6 `:184` 一致，**未新增错误码**。
> - **B（P1-2 关闭）PASS**：复核期间 2A 的 5 个 `apps/**` 改动已由 2A 自己的两个提交（`aa0a5562b`、`a0bafc89e`，05:33:27/05:33:32）收走；UNFREEZE 面的 tracked diff 仍**只含 3 个 `doc/plan` 文件**，`git diff --name-only HEAD -- doc/plan` = 3 个被审文件；载体 §6⑥ 已记录提交隔离。**另有一个范围外的并发 tracked 改动**（`verification/FEA-09/logs/wire-redacted.ndjson`，05:41:22 被某测试运行追加 1 行脱敏 wire 日志），必须由显式 pathspec 排除在 UNFREEZE 提交之外（N-5）。提交时的显式 pathspec 动作本身 **NOT_RUN**（UNFREEZE 提交尚未创建）。
> - **C（P2/P3 处置）PASS（修复面全落地）+ 1 项 P3 登记缺口**：decoder 示例、§10⑥/变更记录/载体 §3 计数（17）、冻结记录残留旧行、v1.4 冻结时间、§8 复核状态（pending，未预填 approved）均已修；但 r1 的 P3-2/3/4/5/6/9 未在载体 §6 处置中登记接受（N-1），载体 §2.B 仍保留 P1-1 旧错误码措辞（N-2）。
> - **D（最终字节安全语义）PASS**：容器多成员 entry **无授权放宽**——同一容器 path、facts=容器身份四键同一、locator/ordinal 来自 Core 权威且 Host 不得推断/猜测、逐项校验、任一不符整 grant 拒绝、匹配 OR+facts 且无路径回退、`find_bound_for_source`/`commit_guard` 不变、folder/image 语义不变、与 §2.4 自洽。
> - **E（pin 与证据）PASS**：C-16 sha256 `ad25fb3c89bb…` = 冻结记录 pin；`git hash-object` `b9be0acf…` = 记录 blob；`verify_pins` **18/18 PASS**；其余 17 契约抽查 6 项均与各自冻结记录/`pins.log` 相同；`pre-post.sha256`/`changed-lines.diff`/3 份 log/`carrier.md`/`EV.md` 与当前字节一致。
> - **F（不变量/零漂移）PASS**：wire 字段/命令集、TTL、撤销/失联、§6 闭集、§7 脱敏、§3.1、Register/Revoke 语义、Run wire/`PROTOCOL_MINOR`、schema/依赖、C-06/C-17 及其余契约字节均零改动；载体/卡不夸大（契约就绪 ≠ 实现/产品可用）。
> - 剩余 11 项 P3 全部**非阻断**（§"Findings" 逐条列明，无静默忽略）；按载体 §5/卡 AC-T2 的通过标准（`approved` 可含非阻断 P3、P0/P1=0），本结论不阻断 UNFREEZE 提交与重冻。

---

## 0. 复核对象、方法、实测基线

### 0.1 被审对象（工作树最终字节）

| # | 对象 | 结论载体 |
|---|---|---|
| 1 | `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`（v1.4） | §A、§C、§D、§E |
| 2 | `doc/plan/FEA-CONTRACT-FROZEN-C16.md`（v1.4 冻结记录） | §C、§E |
| 3 | `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`（C-16 行/状态行） | §E、§F |
| 4 | `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16.md`（载体） | §A、§B、§C、§F |
| 5 | `doc/tasks/FEA-11-RUN-GRANT-2B-PREREQ-1.md`（卡，HEAD 已提交） | §C、§F |
| 6 | `verification/FEA-11-RUN-GRANT-2B-PREREQ-1/**` | §E |

背景只读、不作为被审对象：`doc/reviews/FEA-11-RUN-GRANT-2B-PREREQ-1-r1.md`（r1）；`src/infrastructure/resource_channel/source_read_refs.py`（用于核对「既有实现/§6 语义」是否被本批改动、以及 v1.4 明文是否与既有实现冲突）。

### 0.2 并发与 HEAD 变化（重要事实）

| 时点 | 实测 | 说明 |
|---|---|---|
| 本轮开始（05:32） | `HEAD=1b6152112`；`git status` 有 3 个 `doc/plan` M + 5 个 `apps/**` M | 5 个 `apps/**` 为 **FEA-11-RUN-GRANT-2A** 未提交实现（r1 P1-2 的同一并发源），**不在本复审范围** |
| 复核期间（05:33:27/05:33:32） | `aa0a5562b`（feat 2A）、`a0bafc89e`（test 2A） | 两个提交**只含** `apps/desktop-avalonia/**`（`git diff --name-only 1b6152112..a0bafc89e` = 恰 5 个 apps 文件），**未触任何 doc/plan 或契约字节** |
| 复核末（05:39） | `HEAD=a0bafc89e`；`git diff --name-only HEAD` = 3 个 `doc/plan` 文件 | 2A 已按自身提交收走；UNFREEZE 面与 2A 面在工作树上已可分离 |
| 报告写作期间（05:41:22） | 新增范围外 tracked M：`verification/FEA-09/logs/wire-redacted.ndjson`（+1 行，`git diff HEAD --stat` = `1 insertion`） | 某并发测试运行追加的**脱敏** wire 日志行（`timestamp_utc 2026-11-06T21:41:22Z`；全字段 `[REDACTED]`、ASCII-only，无密码/路径泄漏）；**非本复核所为、不在 UNFREEZE 面**；提交时必须排除（N-5） |

- 被审 4 个改动文件（C-16/FROZEN/MATRIX/载体）mtime：C-16 `05:30:32`、FROZEN `05:31:03`、MATRIX `05:18:47`、载体 `05:31:35`；证据文件生成于 `05:31:15`–`05:31:45`（C-16/FROZEN 均先于证据），此后未再变化；本轮两次实测 C-16 sha256 均为 `ad25fb3c…`。
- HEAD 前移**不影响**被审字节：C-16 在 `1b61521` 与 `a0bafc8` 的 HEAD blob 均为 `a5143d5e1…`（v1.3，sha256 `7c355ccb…`），工作树 v1.4 与 HEAD 的差异只有本批 3 个 `doc/plan` 文件。

### 0.3 实测命令与结果

| 命令 | 实测结果 |
|---|---|
| `git rev-parse HEAD` | 开始 `1b615211200a174c5ada090e838b2e02e8e6fd44`；末 `a0bafc89ec74be08e3d6d721105639df01a140a7` |
| `git diff --name-only HEAD` | 05:39 快照：仅 3 个 `doc/plan` 文件；05:42 复核末：3 个 `doc/plan` 文件 **+ 1 个范围外** `verification/FEA-09/logs/wire-redacted.ndjson`（并发测试追加，见 0.2/N-5） |
| `git diff --name-only HEAD -- doc/plan` | 同上 3 个文件（C-06/C-17 及其余契约零 diff） |
| `Get-FileHash -SHA256 doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `ad25fb3c89bb1749552c3de988369ae93b5e9e7f563ce2530a5d4c65ba2ad8dc` |
| `git hash-object -- doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `b9be0acfa232154510d8453133ef8803b6b8fbbe` |
| C-16 v1.4 工作树字节 | **32 577 bytes、LF=234、CR=0**（LF 原始字节；write/hash 两口径同值） |
| HEAD v1.3 blob 原始字节 | `git cat-file blob HEAD:…` → sha256 `7c355ccb8f826879e34252750c642c8a7b5c138cd5be5b089a7a518bb56519e5`、30 583 bytes、LF=231、CR=0 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，C16 `ad25fb3c89bb`；与 `logs/pins.log` **逐行相同**（Compare-Object 0 差异） |
| `pwsh -NoProfile -File tools/governance/check.ps1`（默认） | `Governance check: PASS (3 warnings)`，Task 2A；与 `logs/check.log` 逐行一致 |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-RUN-GRANT-2B-PREREQ-1.md` | 同上 PASS (3 warnings)，Task 2B-PREREQ-1；与 `logs/check-taskpath.log` 逐行一致 |
| `changed-lines.diff` vs `git diff HEAD -- C-16` | 均 55 行，**逐行相同**（Compare-Object 0 差异） |
| 其余 17 契约 pin 抽查 | C06 `99831a20ffd6`、C17 `aefa0fa5b17e`、C05 `f6e6f3cb1fe1`、C15 `d8c0a3bcfc21`、C14 `05056cbf65f9`、FEA01 `0370c18932b1`：record = 文件实际 = `pins.log`，6/6 相同 |

---

## A. P1-1 关闭（预算超限错误码）—— **PASS**

**A.1 明文已拆分（`FEA-C16:68`）**

> 「Core 注册时逐项校验：locator 安全（不得 `.`/`..`/绝对）、`ordinal ≥ 0` 且唯一、`path` 一致、facts 与容器身份一致。**条目数超 `budget.max_entries` → `SOURCE_BUDGET_EXCEEDED`（不截断）；其余任一项不满足 → 整 grant typed 拒绝**（`SOURCE_ACCESS_DENIED`，不部分接受）。」

- 只有「条目数超预算」映射到 `SOURCE_BUDGET_EXCEEDED`，并且明写**不截断**；
- 「其余任一项」（locator 安全 / ordinal / path 一致 / facts 一致）→ **整 grant** `SOURCE_ACCESS_DENIED`，明写**不部分接受**；
- 与 §2 `:70`「`max_entries`=单 grant 条目上限（默认 10000，可配）；超限拒绝不截断」一致，不再是「任一项不满足 → 一律 DENIED」。

**A.2 与既有实现/§6 语义一致，未新增错误码**

| 核对点 | 证据 | 判定 |
|---|---|---|
| 超条目数 → `SOURCE_BUDGET_EXCEEDED`（调度层） | `source_read_refs.py:172-173`：`len(entries) > budget.max_entries` → `SourceImportError("SOURCE_BUDGET_EXCEEDED", …)` | 一致 |
| 超条目数 → `SOURCE_BUDGET_EXCEEDED`（scope 解析层） | `source_read_refs.py:902-905`：`len(entries) > 10000` → `SOURCE_BUDGET_EXCEEDED` | 一致 |
| 其余结构/身份错误 → `SOURCE_ACCESS_DENIED` | 同文件 `:911-912`、`:918-920`、`:921-924`、`:925-928`、`:929-934`、`:942-945`、`:986-989`（`container grant must carry one entry`） | 一致 |
| §6 闭集未新增码 | C-16 §6 表 `:172-191` 零 diff；`SOURCE_BUDGET_EXCEEDED` 原就在 `:184`（validation/false） | 一致 |
| 未改写既有错误码语义 | 本次 C-16 diff 只新增 §2 段与 §0/§10 元数据；无 §6 hunk | 一致 |

> 观察（N-4，P3，非阻断）：`_parse_scope` 另有硬上限 10000（`:902-905`），而契约 §2 `:70` 写 `max_entries`「默认 10000，可配」；若 `budget.max_entries` 配到 >10000，契约允许而实现会拒绝。属**更严/fail-closed**，非授权放宽，且是 v1.4 之前既有行为；建议 2B 实现卡注明或对齐。

**A 判定：PASS。** P1-1 已关闭，且修复本身未引入新错误码、未改变既有契约不变量。

---

## B. P1-2 关闭/可接受（提交隔离）—— **PASS**

**B.1 工作树隔离（实测）**

- 复核开始时（HEAD `1b6152112`）：`git status --porcelain` 含 3 个 `doc/plan` M + 5 个 `apps/**` M（r1 P1-2 所列同一批 2A 文件：3 个 Host 源 + 2 个测试）。
- 复核期间：`aa0a5562b`、`a0bafc89e` 两个 2A 提交把它们收走；`git diff --name-only 1b6152112..a0bafc89e` = **仅 5 个 `apps/desktop-avalonia/**` 文件**，未触 `doc/**`。
- 复核末（HEAD `a0bafc89e`）：
  - `git diff --name-only HEAD` = **3 个 `doc/plan` 文件**（UNFREEZE 面的 tracked 部分）+ 报告写作期间出现的 1 个**范围外**文件 `verification/FEA-09/logs/wire-redacted.ndjson`（并发测试追加，非 UNFREEZE 面）；`src/apps/tools/tests` **零 diff**；
  - `git diff --name-only HEAD -- doc/plan` = 3 个被审文件（C-06/C-17 等零 diff）；
  - 未跟踪项 = 载体、r1、r2（本报告）、`verification/FEA-11-RUN-GRANT-2B-PREREQ-1/**`，以及**范围外**的 `verification/FEA-11-RUN-GRANT-2A/**`（2A 证据）。
- 因此载体 §5②「仅 C-16/冻结记录/矩阵变化，C-06/C-17 及 src/apps/tools/tests 零 diff」在被审 UNFREEZE 面上成立；但工作树当前另有 2 处**范围外并发产物**（2A 的 `verification/FEA-11-RUN-GRANT-2A/**`、被并发追加的 FEA-09 wire 日志），**都必须在 UNFREEZE 提交时排除**。2A 实现面已由 2A 自身提交承载（`aa0a5562b`/`a0bafc89e`）。

**B.2 提交隔离的记录**

- 载体 §6⑥（`CONTRACT-UNFREEZE-2026-11-07-C16.md:59`）：「提交隔离：UNFREEZE 提交只含本 UNFREEZE 面，2A 改动走其自身提交。」
- 本任务书明确：UNFREEZE 提交将由 DSH 用**显式 pathspec** 隔离，不含 2A 文件。载体记录与之一致（措辞未逐字写 "pathspec"，但隔离承诺与范围明确）。

> **NOT_RUN**：UNFREEZE 提交尚未创建，故「提交后 `git diff --name-only <base>..<commit>` 只含 UNFREEZE 面」属 DSH 提交时义务，本轮无法实测；本轮可实测的替代证据（工作树 UNFREEZE 面 tracked diff 只含 3 个文件 + 2A 已独立提交；范围外并发产物另见 0.2/N-5）已足以判定 P1-2 的处置可接受。

**B 判定：PASS（P1-2 CLOSED；提交时证据 NOT_RUN，由 DSH 在提交步骤补足）。** 注意：因工作树存在范围外并发产物（`verification/FEA-11-RUN-GRANT-2A/**`、`verification/FEA-09/logs/wire-redacted.ndjson`），UNFREEZE 提交**不得**用 `git add -A`/`git commit -a`，必须逐路径显式 stage（N-5，P3）。

---

## C. P2/P3 处置 —— **PASS（修复面全落地）；附 1 项 P3 登记缺口**

### C.1 逐项核对

| r1 finding | 修复要求 | 最终字节实测 | 判定 |
|---|---|---|---|
| P2-4 示例 decoder 枚举 | 与 v1.4/实现一致 | `FEA-C16:54` → `"decoder": "zip|cbz|pdf|image|folder"`；与 `:68` 容器集 `{zip, cbz, pdf}` 兼容，且与 `_KINDS`（`source_read_refs.py:48` = `{image, folder, zip, cbz, pdf}`）**完全一致**；`cborpdf` 已消失（仅存于 `changed-lines.diff` 的删除行） | **CLOSED** |
| P2-3 计数（C-16 §10⑥） | 其余 16 → 17 | `FEA-C16:225` ⑥「C-06/C-17 与其余 **17** pins 零改动」 | **CLOSED**（数字已改为 17；语序问题见 P3-9） |
| P2-3 计数（变更记录） | 同上 | `FEA-C16:233` v1.4 行「C-06/C-17 与其余 **17** pins 零改动」 | **CLOSED**（同上） |
| P2-3 计数（载体 §3） | 同上 | 载体 `:43`「C-06/C-17 与其余 **17** 份冻结契约逐字节不变」 | **CLOSED**（同上） |
| P2-1 冻结记录残留旧行 | 移回 §7 或删除残留副本 | 最终 §8 表尾为 `:98`「其他 17 pins 逐字节不变」；旧「其他 16 pins（C-06 与 C-16 为本批重签）」行已删除（`git diff HEAD -- FROZEN` 可见该行被 §8 标题取代） | **CLOSED**（采用 r1 允许的「删除残留副本」；§7 历史表尾行的取舍见 P3-Note） |
| P2-2 冻结记录冻结时间 | 补 v1.4 | `FROZEN:4`「2026-11-03（v1.0）/ 2026-11-04（v1.1）/ 2026-11-06（v1.3）/ **2026-11-07（v1.4）**」 | **CLOSED** |
| §8 复核状态 | 不得预填 approved | `FROZEN:95`「… → **r2 窄面复核 pending**（approved 后于本行追加结论）」；`FROZEN:48` 条件 6 `⏳`；载体 `:60` `r2 pending`；C-16 `:3` 仅写「复核见载体」 | **CLOSED（正确 pending）** |

### C.2 r1 的 9 项 P3 逐条状态（不得静默忽略）

| r1 P3 | 要求 | 实测 | 状态 |
|---|---|---|---|
| P3-1 | `FROZEN:37`「见 §7」→ §8 | `FROZEN:37` 已写「见 §8」 | **CLOSED** |
| P3-2 | 说明 wire `1.2→1.3` 为追溯登记 | `FEA-C16:17` 现写「**source-access-wire/1.3**（v1.3 additive §2.4 + `source.read.run/1`；v1.4 仅澄清…不改 wire 字段/命令集）」——已说明 1.3 覆盖内容，但未说明「v1.3 当时登记为 1.2、本次追溯更正」 | **OPEN**（部分改善） |
| P3-3 | 修正「64 限制单容器成员数」措辞 | 载体 `:47`③ 仍写「`max_entries`/64 grant 上限仍限制单容器可授权成员数」——64 限制的是单次授权命令的 `grant_ids` 数（`FEA-C16:83`），不是成员数 | **OPEN** |
| P3-4 | 指定注册期「facts=容器身份」的参考点 | `FEA-C16:68` 未指定参考点（首项 facts / 容器 path 当场 digest / `source_locations`）；匹配期 fail-closed，不影响授权面 | **OPEN**（建议 2B 实现卡锁定） |
| P3-5 | ordinal 越界显式拒绝 | `FEA-C16:68` 只要求「`ordinal ≥ 0` 且唯一」，未明文「越界 → 拒绝」；匹配按 `source_entries.ordinal`，越界不命中（fail-closed） | **OPEN**（建议 2B 实现卡加判别用例） |
| P3-6 | `other-17-pins.txt` 用完整 64 位 | 仍为 12 hex 前缀（17 行 `UNCHANGED prev=… actual=…`）；完整值由 `verify_pins` 18/18 覆盖 | **OPEN** |
| P3-7 | 载体证据副本 | `verification/FEA-11-RUN-GRANT-2B-PREREQ-1/carrier.md` 已存在，与 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16.md` **逐字节相同**（sha256 `7a163cd5…`、6 916 bytes） | **CLOSED** |
| P3-8 | §1/§3 独立声明「契约就绪 ≠ 实现/产品可用」 | 载体 §5⑤ 字面含该句（AC-T4 字面满足）；§3 `:40` 明写「多成员容器不可用（维持 L-G12②）」；未按建议在 §1/§3 另起独立句 | **ACCEPTED**（非阻断） |
| P3-9 | 「C-06/C-17 与其余 17」2+17 语序 | 现同时出现在 `FEA-C16:225`⑥、`:233`、载体 `:43`、`FROZEN:94`；数字 17 正确，但「2 + 17」读法会得出 19，属冗余计数 | **OPEN**（措辞，非事实错误） |

> **登记缺口（P3，N-1）**：载体 §6「处置」只登记了 6 项（错误码拆分、decoder 示例、计数、冻结记录清理、LF 规范化、提交隔离），**没有**逐条登记 P3-2/3/4/5/6/9 的处置或明确接受。这属「静默」而非事实错误；建议在载体 §6 补一行（「P3-2/3/4/5/6/9 接受为非阻断；P3-4/P3-5 转入 2B 实现卡」）。

**C 判定：PASS（6 项修复全部落地且可验证）；P3 处置登记不完整 → 计入 N-1（P3，非阻断）。**

---

## D. 最终字节安全语义复核 —— **PASS（无授权放宽）**

### D.1 逐项核对（`FEA-C16:68` 明文 vs 不变量）

| # | 检查 | 明文/代码证据 | 判定 |
|---|---|---|---|
| D1 | 同一容器 path、禁跨文件/跨根 | `FEA-C16:68`「每项 `path` 必须为**同一容器**的绝对路径」+「`path` 一致」校验；匹配期只读 `source_entries`/`source_locations`，从不读路径（`source_read_refs.py:600-610`、`:613-631`） | PASS |
| D2 | facts = 容器身份四键同一 | `FEA-C16:68`「每项 `facts` 必须等于**容器**物理身份（`volume_serial`/`file_id`/`size`/`sha256` 四键同一）」；`_location_matches` 四键逐一比对，任一不符 → `False`（`:613-631`）；`_facts` 要求恰好四键（`:993-997`） | PASS |
| D3 | locator/ordinal 来自 Core 权威、Host 不得推断 | `FEA-C16:68`「以 Core 权威扫描结果为准，Host **不得**自行推断或从容器内容猜测」（比载体 §2.B 的「不得自行推断」更严） | PASS |
| D4 | 逐项校验 | `FEA-C16:68`：逐项 locator 安全 / `ordinal ≥ 0` 且唯一 / path 一致 / facts 一致；既有实现已有单 entry 的 path 绝对/`.`/`..`/reparse/普通文件校验（`:917-945`）与 facts 四键解析（`:993-997`） | PASS |
| D5 | 任一不符 → 整 grant 拒绝、不部分接受 | `FEA-C16:68`「其余任一项不满足 → **整 grant typed 拒绝**（`SOURCE_ACCESS_DENIED`，不部分接受）」；与 §2.4 `:89`「任一目标页不可授权 → 整体 typed、零映射写入」同构 | PASS |
| D6 | 匹配 OR + facts、无路径回退 | `FEA-C16:68` 明文与 `_scope_covers_entry` 的 `entry_key == entry_id OR locator == … OR ordinal == …` + `_location_matches(location, container_facts)` 完全对应；无任何路径比较（`:600-631`） | PASS |
| D7 | `find_bound_for_source`/`commit_guard` 不变 | 明文「语义不变」；`src/**` 零 diff（`git status`/`git diff HEAD` 无 src 文件），`find_bound_for_source`（`:712`）与 `commit_guard`（`:281`）字节未动 | PASS |
| D8 | folder/image 语义不冲突 | `FEA-C16:68`「`folder`（逐成员、路径各自独立）与 `image`（单 entry）语义不变」；容器集 `{zip,cbz,pdf}` 不含 image/folder；folder 走独立函数（`:633-651`） | PASS |
| D9 | 与 §2.4 自洽 | §2.4 `:88` 本身按「`entries[]` 中**某项**满足 … 并核验该 entry 的 facts」；§2.4 字节零 diff；多 entry 不改变 `scope.source_id/version` 相等、facts 核验、`grant_ids` 1..64（`:83`）与整体 typed 原子性（`:89`） | PASS |
| D10 | 无「facts-only / 路径推出 entry / 部分成功」新条款 | `FEA-C16:68` 全句逐项检查未见此类条款；§2.4 `:88-89` 未改 | PASS |

### D.2 攻击假设复核（沿用 r1 V1–V7，按最终字节重判）

| # | 攻击假设 | 最终字节判定 | 依据 |
|---|---|---|---|
| V1 | 借 N 项跨文件/跨根读取 | 不可利用 | 同一容器 path + `path` 一致校验；匹配不读路径（`FEA-C16:68`；`:600-631`） |
| V2 | 成员 digest 冒充容器 facts | 不可利用（fail-closed）；参考点仍未指定（P3-4） | facts 必须等于容器身份；匹配用 `container_facts` 对 `source_locations` 四键比对 |
| V3 | locator/ordinal 注入（`.`/`..`/绝对/重复/越界） | 不可利用；越界未明文拒绝但匹配 fail-closed（P3-5） | locator 安全 + ordinal ≥0/唯一；越界不命中 `source_entries` |
| V4 | 多 entry 绕过 64 grant 上限/预算 | 不可绕过 | 64 是 `grant_ids` 个数上限（`:83`），成员数受 `budget.max_entries`（`:70`/`:68`）；folder 已有 N 成员先例 |
| V5 | facts-only / 路径推出 / 部分成功 | 无此条款 | OR + facts + 无路径回退 + 整 grant typed（`:68`、`:89`） |
| V6 | 与 folder/image 冲突 | 无 | folder 独立函数；image 单 entry 不变（`:68`） |
| V7 | §2.4 per-page 匹配被放宽 | 无 | §2.4 字节未改；per-page 仍按「某项」+ facts + `source_id/version` 相等（`:88`） |

> 说明（既有性质，非 v1.4 引入）：单 entry 的 `locator`/`ordinal` 可分别命中不同 `source_entries` 行（OR 语义）是 v1.3 既有性质；v1.4 只把合法成员面从 1 扩到 N，**未**改变 OR 语义，也未让 Host 越出「同一容器/同一 source+version」的授权根。

**D 判定：PASS（容器多成员 entry 无授权放宽；与既有实现、§6、§2.4 自洽）。**

---

## E. pin 与证据 —— **PASS**

### E.1 pin 复算

| 核对项 | 期望 | 实测 | 判定 |
|---|---|---|---|
| C-16 工作树 sha256（verify_pins 口径） | `ad25fb3c89bb…`（`FROZEN:16/18`） | `ad25fb3c89bb1749552c3de988369ae93b5e9e7f563ce2530a5d4c65ba2ad8dc` | PASS |
| `git hash-object`（blob id） | `b9be0acf…`（`FROZEN:17`；diff index `a5143d5e1..b9be0acfa`） | `b9be0acfa232154510d8453133ef8803b6b8fbbe` | PASS |
| blob 原始字节 sha256 | `ad25fb3c…`（LF） | 32 577 bytes、LF=234、CR=0；两口径同值 | PASS |
| `verify_pins.ps1` | 18/18 PASS | `PIN AUDIT: PASS (all 18)`；C16 `ad25fb3c89bb`；与 `logs/pins.log` 逐行相同 | PASS |
| 其余 17 契约 vs HEAD 冻结记录 | 17/17 不变 | 抽查 6 项（C06/C17/C05/C15/C14/FEA01）record = 实际 = `pins.log`；`git diff --name-only HEAD -- doc/plan` 仅 3 个被审文件 | PASS |
| C-16 `1/18` 重签 | 仅 C16 新值 | `pins.log` 仅 C16 为新值，其余 17 项 UNCHANGED；`other-17-pins.txt` 17 行 `UNCHANGED`、`changed=0` | PASS |

### E.2 证据与当前字节一致性

| 证据 | 实测 | 判定 |
|---|---|---|
| `pre-post.sha256` | pre `7c355ccb…` = HEAD v1.3 blob 实测（30 583 bytes、LF=231、CR=0）；post `ad25fb3c…` = 当前 v1.4 | PASS |
| `changed-lines.diff` | 与 `git diff HEAD -- C-16` 均 55 行，逐行相同（0 差异） | PASS |
| `logs/pins.log` | 与 `verify_pins.ps1` 实际运行**逐行相同**（408 bytes） | PASS |
| `logs/check.log` | `PASS (3 warnings)`、Task 2A，与实际默认运行逐行相同（418 bytes） | PASS |
| `logs/check-taskpath.log` | Task 2B-PREREQ-1，与实际 `-TaskPath` 运行逐行相同（427 bytes） | PASS |
| `verification/.../carrier.md` | 与 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16.md` **逐字节相同**（`7a163cd5…`、6 916 bytes） | PASS |
| `EV.md` | 7 个证据文件的 sha256/bytes 与实际逐一相符（carrier `7a163cd5`、changed-lines `349b588b`、pins `6755ba3d`、check `63073b8c`、check-taskpath `04e0aca2`、other-17 `931bcdd4`、pre-post `bea56b40`） | PASS |
| `other-17-pins.txt` | 表头 `@ 1b6152112`、17 行 UNCHANGED、`changed=0`；12 hex 前缀（P3-6） | PASS（前缀强度 P3） |

> 证据新鲜度说明：`other-17-pins.txt` 记录基线为 `1b6152112`；此后 HEAD 前移到 `a0bafc89e`，但 intervening 两个提交只含 `apps/**`（实测 `git diff --name-only 1b6152112..a0bafc89e`），且当前 HEAD 下重跑 `verify_pins` 仍 18/18，故 17 项不变的断言在当前字节上仍成立。
>
> 并发写入不影响本项：05:41:22 被追加的 `verification/FEA-09/logs/wire-redacted.ndjson` **不是 18 个 pin 对象**；追加后重跑 `verify_pins` 仍 `PASS (all 18)`，重跑 `check.ps1`（默认 / `-TaskPath`）仍分别与 `logs/check.log` / `logs/check-taskpath.log` 逐行一致（追加行全字段 `[REDACTED]`，无敏感内容）。

**E 判定：PASS。**

---

## F. 不变量与零漂移 —— **PASS**

| 不变量 | 结论 | 证据 |
|---|---|---|
| wire 字段/命令集 | 零改动 | C-16 diff 无字段/命令 hunk；`:17` 明写「不改 wire 字段/命令集」；`:68` 只扩展既有 `entries[]` 基数 |
| TTL ≤ 300s | 零改动 | 无 TTL 行 diff；实现 `:166-167` 未改 |
| 撤销/失联 | 零改动 | §7.7（`:205`）无 diff；`RevokeSourceReadGrant` 语义未改 |
| §6 错误闭集（无新增码） | 无新增码 | §6 表 `:172-191` 零 diff；v1.4 只复用 `SOURCE_BUDGET_EXCEEDED`/`SOURCE_ACCESS_DENIED`（均原在闭集） |
| §7 脱敏 | 零改动 | §7（`:197-206`）无 diff |
| §3.1 fresh-grant | 零改动 | §3.1（`:103-129`）无 diff |
| Register/Revoke 语义 | 仅容器 entries 基数 1→N；字段/签名/TTL/撤销不变 | C-16 diff；`_ENVELOPE_FIELDS`（`source_read_refs.py:49-52`）未改 |
| Run wire / `PROTOCOL_MINOR` | 零改动 | `src/**` 零 diff；apps 的 2A 改动不涉 Run wire（且不在本批复审面） |
| schema/迁移/依赖 | 零改动 | 全仓 diff 无 schema/依赖文件 |
| C-06/C-17 及其余契约 | 逐字节不变 | `git diff --name-only HEAD -- doc/plan` = 3 个被审文件；`verify_pins` 18/18；抽查 6 项 pin 不变 |
| 范围外并发产物 | 不影响未跟踪/冻结面 | `verification/FEA-11-RUN-GRANT-2A/**`（2A 证据）与 `verification/FEA-09/logs/wire-redacted.ndjson`（+1 行脱敏日志，非 pin 对象）；不得进入 UNFREEZE 提交（N-5） |
| 载体/卡不夸大 | 不夸大 | 载体 §3 `:40`「新 Host × 旧 Core：多成员容器不可用（维持 L-G12②）」；§5⑤ 明写「契约就绪 ≠ 实现/产品可用」；卡 `status: ready`、AC-T1…T4 全未勾选；§6/§8 复核状态 pending |
| 冻结记录未预填 approved | 正确 | `FROZEN:48` ⏳、`:95` r2 pending；载体 `:60` pending |

附加观察（非阻断）：
- 载体 §2.B（`:25`）**未随 P1-1 处置同步**：仍写「逐项校验…条目数 ≤ `budget.max_entries`；任一项不满足 → 整 grant typed 拒绝（`SOURCE_ACCESS_DENIED`，不截断、不部分接受）」，与最终 `FEA-C16:68` 的超预算 `SOURCE_BUDGET_EXCEEDED` 及同载体 §6① 矛盾 → **N-2（P3）**。
- 卡（HEAD 已提交、本批未改）`out_of_scope`、T-1、AC-T1、复核要求仍写「其余 16」（`:32`、`:45`、`:83`、`:91`），与 C-16/载体/冻结记录修正后的 17 不一致 → **N-3（P3）**。

**F 判定：PASS。**

---

## Findings（r1 逐条状态 + 本轮新增）

### r1 findings 状态

| r1 ID | 状态 | 依据 |
|---|---|---|
| P1-1 预算错误码 | **CLOSED** | `FEA-C16:68` 已拆分；§6 `:184` 未改；实现 `:172-173`/`:902-905` 一致（§A） |
| P1-2 提交隔离 | **CLOSED**（提交时证据 NOT_RUN） | 2A 已由 `aa0a5562b`/`a0bafc89e` 独立提交；UNFREEZE 面 tracked diff 仅 3 个文件（另有范围外并发产物，见 N-5）；载体 §6⑥ 记录隔离（§B） |
| P2-1 §8 残留旧行 | **CLOSED** | 旧「其他 16 pins」行已删除，§8 `:98` 为「其他 17 pins」（r1 允许的删除选项；§7 历史表尾行取舍见下 Note） |
| P2-2 冻结时间 | **CLOSED** | `FROZEN:4` 补 `2026-11-07（v1.4）` |
| P2-3 计数 16→17 | **CLOSED** | `FEA-C16:225/233`、载体 `:43` 均为 17；遗留语序见 P3-9 |
| P2-4 decoder 示例枚举 | **CLOSED** | `FEA-C16:54` = `zip|cbz|pdf|image|folder`，与 `_KINDS` 一致 |
| P3-1 | **CLOSED** | `FROZEN:37`「见 §8」 |
| P3-2 | **OPEN** | wire 1.3 已说明覆盖内容，未说明追溯更正 |
| P3-3 | **OPEN** | 载体 `:47`③ 仍把 64 说成成员数上限 |
| P3-4 | **OPEN** | facts 参考点未指定（建议 2B 卡） |
| P3-5 | **OPEN** | ordinal 越界未明文拒绝（fail-closed） |
| P3-6 | **OPEN** | `other-17-pins.txt` 12 hex 前缀 |
| P3-7 | **CLOSED** | verification `carrier.md` 与载体逐字节相同 |
| P3-8 | **ACCEPTED** | AC-T4 字面满足；§3 有产品不可用声明（非阻断） |
| P3-9 | **OPEN** | 「C-06/C-17 与其余 17」冗余语序（数字正确） |

> **Note（P2-1 的取舍）**：r1 的修复选项包含「删除残留副本」。最终字节采用删除，导致 §7（v1.3 历史段）表尾不再有 HEAD 中的「其他 16 pins」行；该断言的事实仍保留在 `FROZEN:47` 条件 5（「其余 16 项不变」）。建议（非阻断）在 §7 恢复该行或加一句指向 §2 条件 5。不构成不实陈述，故记 P3-Note 而非新 P2。

### 新增 findings（全部 P3，非阻断）

| ID | 严重度 | 事实（path:line） | 建议 |
|---|---|---|---|
| N-1 | P3 | 载体 §6（`:59`）处置只列 6 项，未登记 r1 P3-2/3/4/5/6/9 的处置或明确接受 | 在 §6 补一行接受/转 2B 卡；不涉冻结字节 |
| N-2 | P3 | 载体 §2.B（`:25`）仍把「条目数 ≤ `budget.max_entries`」纳入「任一项不满足 → `SOURCE_ACCESS_DENIED`」，与 `FEA-C16:68` 及同载体 §6① 矛盾 | 提交前把该句改为与冻结字节一致（超预算 → `SOURCE_BUDGET_EXCEEDED`）；载体非冻结对象，改后仅需刷新 `verification/.../carrier.md` 与 `EV.md` 哈希，**不改 C-16 pins、无需重冻** |
| N-3 | P3 | 卡（HEAD 已提交、本批未改）`:32`、`:45`、`:83`、`:91` 写「其余 16」，与修正后的 17 不一致 | 下次编辑卡时统一为「其余 17（含 C-06/C-17）」或「C-06/C-17 外 15 份」 |
| N-4 | P3（观察，既有） | `source_read_refs.py:902-905` 硬上限 10000 与契约 §2 `:70`「默认 10000，可配」并存；配置 >10000 时契约允许而实现拒绝（更严，fail-closed） | 2B 实现卡注明硬上限或统一由 `budget.max_entries` 控制 |
| N-5 | P3（提交面，范围外） | 05:41:22 有并发测试运行向 tracked 证据 `verification/FEA-09/logs/wire-redacted.ndjson` 追加 1 行（`git diff HEAD --stat` = 1 insertion；内容全 `[REDACTED]`）；叠加 2A 的未跟踪证据目录，工作树存在 UNFREEZE 面之外的并发产物 | UNFREEZE 提交必须逐路径显式 stage（禁止 `git add -A`/`git commit -a`）；该 FEA-09 行的归属由 2A/其测试所有者处置（保留、提交或回退），不纳入本 UNFREEZE |

**r2 计数：P0=0 / P1=0 / P2=0 / P3=11（r1 遗留 OPEN 6 + 新增 5；另 P3-1/P3-7 CLOSED、P3-8 ACCEPTED）。**

---

## 最终 verdict

**`approved`。**

- **契约最终字节**：C-16 v1.4 的容器多成员 entry 语义**没有授权放宽**（§D 十项 + V1–V7 全部通过）；P1-1 的超预算错误码已按 r1 要求拆分为 `SOURCE_BUDGET_EXCEEDED`，且未新增错误码（§A）。
- **pin/证据**：C-16 sha256 `ad25fb3c…` = 冻结记录 pin；blob `b9be0acf…`；`verify_pins` 18/18；其余 17 项不变（抽查 6）；证据与当前字节一致（§E）。
- **提交面**：2A 已独立提交；UNFREEZE 面的 tracked diff 只剩 3 个 `doc/plan` 文件，但工作树另有范围外并发产物（2A 未跟踪证据、被追加的 FEA-09 wire 日志），因此 UNFREEZE 提交必须按 DSH 声明的显式 pathspec 逐路径执行（N-5），提交后以 `git diff --name-only <base>..<commit>` 复核（§B，NOT_RUN）。
- **不变量**：wire/命令集/TTL/撤销/§6/§7/§3.1/Run wire/`PROTOCOL_MINOR`/schema/依赖/C-06/C-17 零漂移；载体与卡不夸大（§F）。
- **非阻断 P3**：11 项（含 N-1 处置登记、N-2 载体 §2.B 旧错误码措辞、N-3 卡计数、N-4 既有硬上限、N-5 提交面并发产物）。它们不改变冻结字节、pin、安全语义或 AC-T1…T4 的成立，按载体 §5/卡 AC-T2 的通过标准（`approved` 可含非阻断 P3、P0/P1=0）不阻断本 UNFREEZE 提交。
- **后续动作（DSH）**：①在载体 §6 追加 r2 结论/session/reviewed_head；②`FROZEN:48` 条件 6 `⏳`→✅、`FROZEN:95`/`FROZEN:37` 的 r2 pending 改为 approved；③建议顺手按 N-1/N-2 更新载体并刷新 `verification/.../carrier.md`+`EV.md` 哈希（不改 C-16 pins）；④以显式 pathspec 提交 UNFREEZE 面，提交后重跑 `verify_pins`/`check.ps1` 并复核提交 diff。
- 若 C-16 字节或任一 pin 在提交前再次变化，本 `approved` 失效，须重算 pin 并重新窄面复审。

---

## 真实性声明

- 本报告由**独立上下文 fresh subagent** 撰写：未参与 C-16 v1.4 起草、未参与 r1 复核、未参与 FEA-11-RUN-GRANT-1/2 的实现或返修；只读被审字节与背景文件。
- **唯一写入**：本文件 `doc/reviews/FEA-11-RUN-GRANT-2B-PREREQ-1-r2.md`。未 `git add`/`commit`/`push`；未删除/移动任何文件；未修改 C-16/冻结记录/矩阵/载体/卡/证据/STATUS/PLAN 的字节。为计算 HEAD v1.3 blob 的原始字节 sha256，在系统 `%TEMP%` 写了一个临时文件（`git cat-file` 重定向），已删除，未落仓库。
- **并发事实**：复核开始时工作树含 5 个 `apps/desktop-avalonia/**` 的 2A 未提交改动；复核期间它们由 2A 的 `aa0a5562b`、`a0bafc89e` 两个提交（05:33:27/05:33:32，仅 `apps/**`）收走。报告写作期间（05:41:22）另有并发测试运行向 tracked `verification/FEA-09/logs/wire-redacted.ndjson` 追加 1 行脱敏 wire 日志（`[REDACTED]`、ASCII-only），**非本复核写入**；我未参与、未审查 2A 的实现内容，也未运行任何测试。本报告只按任务书范围审查 UNFREEZE 面；上述两项范围外产物均在 §B/§E/§F 与 N-5 中如实登记。
- **事实基线**：被审字节取工作树最终字节（C-16 `ad25fb3c…`、32 577 bytes、LF=234/CR=0）；`reviewed_head a0bafc89e…`（开始 `1b6152112`）。若 Lead 在收到本报告后继续编辑被审文件，pin/diff 需重新实测，本报告结论只对上述快照负责。
- **未跑项（NOT_RUN）**：全量 `pytest tests`、全量 `dotnet test NewManga.sln`、`NEWMANGA_FEA11_IPC=1` 真实 IPC、`generate_api_inventory.py --check`、`scope_validation.py`；UNFREEZE **提交**及其提交后 diff/pins 复核（提交尚未创建）。已实跑项（`verify_pins`、`check.ps1`×2、sha256/`hash-object`/`git cat-file`、diff 逐行比对、证据哈希复算）均在正文给出命令与结果。
- **session**：`e032ed9a-ed9d-4282-bfc8-1a1fbe51ea29`（`$DSH_SESSION_ID` 实测）；parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`。
- 本报告不构成实现授权、不构成产品可用声明，不替代 DSH 的 findings 处置、提交与集成验证。
