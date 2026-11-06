---
task: FEA-11-RUN-GRANT-2B-PREREQ-1
title: FEA-11-RUN-GRANT-2B-PREREQ-1 独立 byte-level 契约复核 r1（C-16 v1.4 容器多成员 entry 授权接受面）
reviewer: fresh subagent（独立上下文；未参与本 UNFREEZE 起草；只读被审字节）
session: 46c5cfef-1cfd-4953-9d9b-f781a5bc3515（`$DSH_SESSION_ID` 实测；以 Lead 记录为准）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent（独立 byte-level 契约复核；未参与起草、未参与前轮复核、未参与 RUN-GRANT-1/2 实现）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 1b615211200a174c5ada090e838b2e02e8e6fd44
verdict: changes_requested
---

# C-16 v1.4 UNFREEZE（容器多成员 entry 授权接受面）· 独立 byte-level 复核 r1

> **结论先行：`changes_requested`。P0=0 / P1=2 / P2=4 / P3=9。**
>
> - **C-16 v1.4 字节的安全语义成立**：容器多成员 entry 的写法**没有**放宽授权面——`path` 限定同一容器、`facts` 必须等于容器物理身份（四键同一）、`locator/ordinal` 明文要求 Core 权威且 Host 不得推断、逐项校验且任一项不符**整 grant typed 拒绝**、读取/匹配沿用 `entry_key OR locator OR ordinal` + 容器 facts、**无路径回退**、`find_bound_for_source`/`commit_guard` 不变。B 项 ①–⑦ 逐条 **PASS**（见 §B、§V）。
> - **P1-1（阻断，契约字节错误）**：`FEA-C16_SOURCE_READ_WIRE_DRAFT.md:68` 把「条目数 ≤ `budget.max_entries`」也收进「任一项不满足 → `SOURCE_ACCESS_DENIED`」；而既有实现与 §6 对该超限路径固定返回 **`SOURCE_BUDGET_EXCEEDED`**（`source_read_refs.py:172-173`、`:902-905`；C-16 §6 `:184`；§2 `:70`「超限拒绝不截断」）。实现照 v1.4 字面写会改变既有 `RegisterSourceReadGrant` 错误码语义，违反本批「§6 零改动」自查项。
> - **P1-2（阻断提交面，非提案字节）**：本复核开始时工作树只有 5 项 UNFREEZE 改动；复核期间 `05:24`–`05:29` 陆续出现 **5 个** `apps/desktop-avalonia/**` 文件的修改（3 个 Host 源 + 2 个测试；注释自证为 **FEA-11-RUN-GRANT-2A** 实现，外部并发写入，非本复核所为；行数随并发仍在增长）。因此最终 `git diff --name-only HEAD` **不再**只含 UNFREEZE 面，载体 §5②「src/apps/tools/tests 零 diff」在最终工作树上不成立。UNFREEZE 提交前必须按路径隔离（或先完成/隔离 2A）。（**r1 后**：DSH 已隔离，05:33 工作树只含 UNFREEZE 面，见 §H。）
> - **P2（返修后重冻）**：冻结记录 §8 表尾残留旧 §7 的「其他 16 pins（C-06 与 C-16 为本批重签）」行（结构损坏 + 与 v1.4 事实矛盾）；头部「冻结时间」缺 v1.4；C-16 §10⑥ 与载体 §3「其余 16」计数错误（应为除 C-16 外 17 项不变）；§2 示例 decoder 枚举 `cborpdf` 与 v1.4 `{zip,cbz,pdf}`/实现 `_KINDS` 不一致。
> - **已实测通过**：C-16 sha256 `9fe9d5f0…` = 冻结记录 pin；`git hash-object` `3ef67791…`；`verify_pins` **18/18 PASS**；其余 17 契约零 diff、抽查 6 项 pin 不变；`pre-post.sha256` pre = HEAD v1.3 `7c355ccb…`；`changed-lines.diff` 与 `git diff HEAD -- C-16` 45 行逐行一致；`check.ps1`/`check-taskpath.log` 可复现（PASS，3 warnings）。

---

## 0. 复核对象、方法与实测基线

### 0.1 对象（工作树最终字节）

| # | 对象 | 结论载体 |
|---|---|---|
| 1 | `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`（v1.4） | §A–§D |
| 2 | `doc/plan/FEA-CONTRACT-FROZEN-C16.md`（v1.4 pin 记录） | §D、§E |
| 3 | `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`（C-16 行） | §E |
| 4 | `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16.md`（载体） | §A、§E、§F |
| 5 | `doc/tasks/FEA-11-RUN-GRANT-2B-PREREQ-1.md`（卡，HEAD 已提交） | §F |
| 6 | `verification/FEA-11-RUN-GRANT-2B-PREREQ-1/**` | §D、§G |

背景只读、不作为被审对象：`doc/reviews/FEA-11-RUN-GRANT-2-scope-r1.md`（2B 设计，F11–F16/F25–F31）；`src/infrastructure/resource_channel/source_read_refs.py:986-990,598-610`（现状单 entry 限制）及其相邻的注册/匹配实现（用于核对「既有语义」是否被本批改动）。

### 0.2 工作树与并发事实（重要）

| 时点 | `git status --porcelain -uall` | 说明 |
|---|---|---|
| 复核开始（约 05:19） | 3 个 `M`（C-16 / FROZEN-C16 / MATRIX）+ 2 个 `??`（载体、证据目录，共 6 文件） | 与任务书声明的 UNFREEZE 面一致 |
| 复核末（05:29 定稿快照） | 上述 5 项 **+ 5 个 `M`**：Host 源 `HostRuntime.cs`、`SourceReadCoordinator.cs`、`SourceScanScheduler.cs`；Tests `Fea11RunGrantIpcTests.cs`、`SourceRegistryTests.cs` | 外部并发写入，mtime `05:24:18`–`05:27:52`；diff 注释自证 `FEA-11-RUN-GRANT-2A (card S-2/S-3/S-4)`；行数随写入变化（05:29 `git diff --stat` 为 `+836/−40`，05:30 复核已增至 `+1247/−41`） |

- 这 5 个 `apps/**` 改动**不是**本 UNFREEZE 的字节，也不是本复核写入；它们全部属于 `FEA-11-RUN-GRANT-2A` 的 allowed_paths（`FEA-11-RUN-GRANT-2-scope-r1.md:§3.3`）。并发写入可能仍在继续（本快照截至 `05:29:48`）；本报告的 A 项结论按该快照判定，若 Lead 后续看到更多 `apps/**`/`tests/**` 文件，属同一并发源的扩大，提交隔离结论不变。
- 本报告的 A 项按**最终工作树**判定（任务要求「事实以工作树最终字节为准」），因此判 FAIL；但在 findings 中明确归因与最小修复为「提交隔离」，不要求改 C-16 字节。
- 被审 5 个 UNFREEZE 文件的 mtime 停在 `05:17:37`–`05:18:47`，复核期间未再变化；C-16 sha256 在写报告前重新计算仍为 `9fe9d5f0…`。
- 本复核**不审查**上述 5 个 2A 文件的实现内容（不在本任务书范围；未参与、未运行其测试）。

### 0.3 实测命令与结果（摘要）

| 命令 | 实测结果 |
|---|---|
| `git rev-parse HEAD` | `1b615211200a174c5ada090e838b2e02e8e6fd44`（branch `main`） |
| `git diff --name-only HEAD` | 最终：3 个 `doc/plan` + **5 个 `apps/desktop-avalonia/**`**（见 0.2） |
| `Get-FileHash -SHA256 doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `9fe9d5f0ae6209078e149759f40b29100ee6c0d40be3022fc77bbc1ebf21a0f7` |
| `git hash-object -- doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `3ef677913974ca7718b49458fd83303dab4f253a` |
| HEAD v1.3 原始字节 sha256（`git show HEAD:` 重定向后计算） | `7c355ccb8f826879e34252750c642c8a7b5c138cd5be5b089a7a518bb56519e5`（30 583 bytes） |
| v1.4 工作树字节 | 32 532 bytes、LF=233、CRLF=0（LF 原始字节；`git cat-file blob` 重算 sha256 同值） |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，C16 `9fe9d5f0ae62`；其余 17 项与 `logs/pins.log` 逐行一致 |
| `pwsh -NoProfile -File tools/governance/check.ps1`（默认 / `-TaskPath ...2B-PREREQ-1.md`） | 两次均 `Governance check: PASS (3 warnings)`，输出与 `logs/check.log` / `logs/check-taskpath.log` 逐行一致 |
| `changed-lines.diff` vs `git diff HEAD -- C-16`（归一化 CRLF/LF） | 45 行逐行相同，0 差异 |
| 其余 17 契约 | `git diff --name-only HEAD -- doc/plan` 仅 3 个被审文件（C-06/C-17 等零 diff）；抽查 C06/C17/C15/FEA01/C05/C14 完整 pin 与各自冻结记录一致 |

---

## A. diff 最小性 —— **FAIL（P1-2 + 逐行 PASS）**

### A.1 文件面：FAIL（P1-2）

- 复核开始时 `git diff --name-only HEAD` = `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`、`doc/plan/FEA-CONTRACT-FROZEN-C16.md`、`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`（3 个 tracked）；未跟踪 = 载体 + `verification/FEA-11-RUN-GRANT-2B-PREREQ-1/**`（6 文件）。**与任务书声明的 UNFREEZE 面一致。**
- 复核末（最终字节）多出 **5 个** `apps/desktop-avalonia/**` 文件（0.2：3 个 Host 源文件、2 个测试文件）。因此：
  - `git diff --name-only HEAD` **不再**只含 UNFREEZE 文件 → 本项 FAIL；
  - 载体 §5 核对②「仅 C-16/冻结记录/矩阵变化，C-06/C-17 及 src/apps/tools/tests 零 diff」（`CONTRACT-UNFREEZE-2026-11-07-C16.md:53`）在最终工作树上**不成立**；
  - 5 个 `apps/**` 改动是并发的 2A 实现（不属于本 UNFREEZE 提案），但若 UNFREEZE 提交不按路径隔离，会把 2A 未完成实现（含测试）夹带进 UNFREEZE 提交。
- 卡 `doc/tasks/FEA-11-RUN-GRANT-2B-PREREQ-1.md` 已在 HEAD 提交（`git ls-files --error-unmatch` 命中，工作树无改动），不在本批 diff；属正常。

### A.2 C-16 逐行对应载体 §2：PASS

`git diff HEAD -- C-16` 共 4 个 hunk、10 行变更（5 加/5 减），逐行对应：

| C-16 位置 | 落盘内容 | 载体 §2 条目 |
|---|---|---|
| `:3` | 状态行 → `FROZEN v1.4（2026-11-07 重冻…）` + 载体/冻结记录链接 | §2.A 第 1 点（`:17`） |
| `:4` | 日期行补 `2026-11-07（v1.4 UNFREEZE）` | §2.A 第 1 点 |
| `:17` | §0 wire 行 `source-access-wire/1.2` → `1.3`，并注明「v1.4 仅澄清…不改 wire 字段/命令集」 | §2.A 第 2 点（`:18`） |
| `:68` | 新增「容器源多成员 entry（v1.4 UNFREEZE）」整段 | §2.B（`:20-27`）逐条落地（见下表） |
| `:225` | §10 冻结条件追加 ⑥ | §2.C 第 1 点（`:30`） |
| `:233` | §10 变更记录追加 v1.4 行 | §2.C 第 2 点（`:31`） |

§2.B 逐条映射（`FEA-C16:68`）：

| 载体 §2.B 条目 | C-16:68 明文 | 判定 |
|---|---|---|
| `zip/cbz/pdf`、`entries[]` 1..N（N ≤ `budget.max_entries`） | 「容器源（`rendition.decoder ∈ {zip, cbz, pdf}`）的 `scope.entries[]` 允许 **1..N**（N ≤ `budget.max_entries`）」 | 落地 |
| 每项 `path` = 同一容器绝对路径 | 「每项 `path` 必须为**同一容器**的绝对路径」 | 落地 |
| `locator/ordinal` = 成员身份，Core 权威，Host 不得推断 | 「以 Core 权威扫描结果为准，Host **不得**自行推断或从容器内容猜测」 | 落地（更强的「或从容器内容猜测」） |
| `facts` = 容器物理身份（四键同一） | 「每项 `facts` 必须等于**容器**物理身份（…四键同一）」 | 落地 |
| 逐项校验（locator 安全/ordinal/ path/facts/条目数） | 「Core 注册时逐项校验：locator 安全…、`ordinal ≥ 0` 且唯一、`path` 一致、facts 与容器身份一致、条目数 ≤ `budget.max_entries`」 | 落地（错误码问题见 P1-1） |
| 任一项不满足 → 整 grant typed，不截断不部分接受 | 「任一项不满足 → **整 grant typed 拒绝**（`SOURCE_ACCESS_DENIED`，不截断、不部分接受）」 | 落地（超限码冲突，P1-1） |
| 匹配沿用 OR + 容器 facts、无路径回退、find_bound/commit_guard 不变 | 同句后半 | 落地 |
| folder/image 语义不变 | 「`folder`（逐成员、路径各自独立）与 `image`（单 entry）语义不变」 | 落地 |

**未登记改动：无。** C-16 的 4 个 hunk 全部在载体 §2 A/B/C 登记范围内；§0 wire 版本 `1.2→1.3` 本身已登记（理由精度见 P3-2），`§2` 示例、`§2.4`、`§6`、`§7`、`§3.1` 均零改动。

---

## B. 安全语义审查 —— **PASS（①–⑦ 逐条通过；附 P1-1、P3-4/P3-5、P2-4）**

> 判定方法：把 v1.4 明文逐条映射到 `source_read_refs.py` 的注册（`_parse_scope`/`register`）与匹配（`_scope_covers_entry`/`_location_matches`/`_bindings`）现状，检查「是否存在比 v1.3 更宽的可授权面」。结论：**没有**。

### B① 同一容器绝对路径、禁跨文件/跨根 —— PASS

- v1.4 明文「每项 `path` 必须为**同一容器**的绝对路径」（`FEA-C16:68`），注册校验含「`path` 一致」。
- 既有注册对每项 `path` 强制绝对、拒绝 `.`/`..` 段、拒绝 reparse、`stat` 必须是普通文件（`source_read_refs.py:917-945`）；`container_path/container_facts` 由 scope 构造（`:986-990`）。
- 匹配期只用 `source_entries`（属于该 `source_id/version`）与 `source_locations`（容器行），**从不读路径**（`:603-605`、`:613-631`）。N 项 `path` 不一致会被注册校验拒绝（实现须按 v1.4 补该项校验；现单 entry 实现只在 folder 分支做「同一 root」比较 `:948-984`）。
- 结论：无法借助 N 项跨文件/跨根读取；最坏只能拒绝（fail-closed）。

### B② 每项 facts = 容器物理身份；成员 digest 冒充 —— PASS（附 P3-4）

- v1.4 明文「每项 `facts` 必须等于**容器**物理身份（`volume_serial`/`file_id`/`size`/`sha256` 四键同一）」（`FEA-C16:68`）。
- 匹配期用 `grant.container_facts` 与 `source_locations` 的 `volume_serial/file_id/size_bytes/content_digest` 逐键比对（`source_read_refs.py:603-605`、`:613-631`）；任何一项不符 → `False`（不匹配、不授权）。
- 成员内容 digest 冒充容器 facts：该 facts 会与容器 `source_locations` 不符 → 匹配失败（fail-closed）；反之用容器 facts 冒充成员：匹配仍按容器身份，只影响「哪一成员」的 OR 子句，不改变授权根。
- **残余精度**（P3-4）：注册期「facts 与容器身份一致」的**参考点**未指定（首项 facts？容器 path 当场 digest？`source_locations`？）。匹配期安全不依赖该选择；建议 2B 实现卡锁定「全部项 facts 必须彼此相等，且 `container_facts` 只取容器路径的物理身份」。

### B③ locator/ordinal 来自 Core 权威、Host 不得推断；重复/越界/`.`/`..`/绝对 —— PASS（附 P3-5）

- v1.4 明文：「`locator`/`ordinal` 为容器内成员身份（以 Core 权威扫描结果为准，Host **不得**自行推断或从容器内容猜测）」（`FEA-C16:68`）。
- 拒绝面：
  - locator 的 `.`/`..`/绝对：明文「locator 安全（不得 `.`/`..`/绝对）」；既有 folder 分支已有 `validate_locator`（`:955`、`:979`），container 分支需按 v1.4 补（现单 entry 分支未调用，属 2B 实现项）。
  - ordinal：明文「`ordinal ≥ 0` 且唯一」；既有已拒 bool/负数（`:925-928`），唯一性需补。
  - ordinal **越界**（≥ 实际成员数）：v1.4 未明文拒绝（P3-5）；但匹配用 `ordinal == source_entries.ordinal`，越界值不会命中任何行 → fail-closed（不授权）。不是放宽，只是缺少显式 fail-closed 声明。
- 结论：PASS；建议 2B 实现卡补「ordinal 越界 → 拒绝」并用判别用例锁定。

### B④ 条目数受 `budget.max_entries`、超限 typed 不截断；多 entry 是否绕过 64/预算 —— PASS（附 P1-1）

- 限制明文：`N ≤ budget.max_entries`（`FEA-C16:68`）与 §2 budget 行「`max_entries`=单 grant 条目上限（默认 10000，可配）；超限拒绝不截断」（`:70`）。
- 「不截断、不部分接受」明文（`:68`），与 §2.4「任一目标页不可授权 → 整体 typed、零映射写入」（`:89`）同构。
- **64 上限**：64 是 `AuthorizeSourceReadForRun` 的 `grant_ids` 个数上限（`:83`；实现 `source_read_refs.py:457-464`），不是「成员数」上限；多 entry 不改变 grant 数量，因此不构成对 64 的绕过。**folder 先例**已经允许单 grant 携带 N 成员（`:594-597`、`:633-651`），容器多 entry 与之一致，不是新类别。
- **预算**：`max_bytes` 定义为「单 entry 读取上限」（`:70`），`max_entries` 为条目上限；N 项不改变单 entry 上限，总量随 N 增长是既有 folder 语义的一部分，仍受 `max_entries` 约束。未发现「多 entry 绕过预算」的新路径。
- **P1-1**：超限的**错误码**写错（`SOURCE_ACCESS_DENIED` vs 既有 `SOURCE_BUDGET_EXCEEDED`），见 findings；这不改变「拒绝、不截断」的结论，但会改变既有实现语义。

### B⑤ 匹配 OR + facts、无路径回退、find_bound/commit_guard 不变 —— PASS

- v1.4 明文「读取/匹配沿用既有 `entry_key == entry_id OR locator == source_entries.locator OR ordinal == source_entries.ordinal` + facts 与**容器**身份比对；**无路径回退**；`find_bound_for_source`/`commit_guard` 语义不变」（`FEA-C16:68`）。
- 与实现一致：`_scope_covers_entry` 的三子句 OR + `_location_matches(location, container_facts)`（`source_read_refs.py:600-610`、`:613-631`）；`find_bound_for_source` 只按 `(generation, grant_id)` 选择 live grant（`:564-581`）；`commit_guard` 与读取期均调 `VerifySourceRead`（`:69` 契约）。
- 未发现「允许 facts-only」「允许由路径推出 entry」「允许部分成功」的条款；§2.4 的原子性/零映射写入明文未改（`:89`）。

### B⑥ 与 folder / image 语义不冲突 —— PASS（附 P2-4）

- v1.4 明文「`folder`（逐成员、路径各自独立）与 `image`（单 entry）语义不变」（`:68`）；容器集合 `{zip, cbz, pdf}` 不含 `image`。
- 实现侧 folder 有独立的 `_folder_scope_covers`（`source_read_refs.py:633-651`），与容器分支（`:598-610`）分离；v1.4 只要求容器分支 1..N，不影响 folder。
- **P2-4**：同节 `:54` 示例仍写 `"decoder": "zip|cborpdf|image"`，而 v1.4 新句与实现 `_KINDS`（`zip/cbz/pdf`，`:48`）都是 `pdf`；示例中的 `cborpdf` 不存在。属既有字节遗留，但 v1.4 使其在同节显性矛盾，建议 2B 实现前统一。

### B⑦ 与 §2.4（Run 授权建立）交互 —— PASS

- §2.4 的 per-page 匹配明文已经是「`scope.entries[]` 中**某项**满足 `entry_key == binding.entry_id` 或 `locator == source_entries.locator` 或 `ordinal == source_entries.ordinal`，并核验该 entry 的 facts 与 `source_locations` 一致」（`FEA-C16:88`），本身不限制 entries 为 1 项。
- v1.4 只澄清「容器 entries 可为 N 项」，§2.4 字节未改（diff 无 §2.4 hunk）；2B 实现改共享的 `_scope_covers_entry` 后，§2.4 的 per-page 匹配自动受益，无需新增命令/字段。
- 反向检查：多 entry 不会让 §2.4 绕过 `scope.source_id/version` 相等（`:88`）、不会绕过 facts 核验、不会改变「任一目标页不可授权 → 整体 typed、零写」的原子性（`:89`）；`grant_ids` 仍 1..64（`:83`）。
- 结论：自洽，不产生新绕过。

---

## C. 不变量零改动 —— **PASS（附 P1-1、P2-3；计数按实测）**

逐项核对 `git diff HEAD -- C-16` 与全仓 diff：

| 不变量 | 结论 | 证据 |
|---|---|---|
| wire 字段/命令集 | 零改动 | C-16 diff 无字段/命令 hunk；`:17` 明说「不改 wire 字段/命令集」；`:68` 只约束既有 `entries[]` 形态 |
| TTL ≤ 300s | 零改动 | C-16 无 TTL 行 diff；实现 `:166-167` 未改 |
| 撤销 / 失联 | 零改动 | C-16 §0/§7 无 diff；§7.7（`:205`）未改 |
| §6 错误闭集（无新增码） | 无新增码 | C-16 §6 表（`:172-191`）零 diff；v1.4 只复用 `SOURCE_ACCESS_DENIED`（但超限映射冲突 → P1-1） |
| §7 脱敏 | 零改动 | C-16 §7（`:197-206`）零 diff |
| §3.1 fresh-grant | 零改动 | C-16 §3.1（`:103-129`）零 diff |
| `RegisterSourceReadGrant` / `RevokeSourceReadGrant` 既有字节语义 | 字段/签名/TTL/撤销/失联不变；唯一登记变更是容器 cardinality 1→N | C-16 diff；实现 `_ENVELOPE_FIELDS`（`:49-52`）未改；本批就是为该 1→N 走 UNFREEZE |
| Run wire / `CORE_PROTOCOL_MINOR` | 零改动 | `apps/**/src` 中 Run wire 相关 0 diff（仅 2A 的 version 通道，与本契约无关）；`PROTOCOL_MINOR=3` 未动 |
| schema / 迁移 / 依赖 | 零改动 | 全仓 diff 无 schema/依赖文件 |
| M2-C1 | 零改动 | 未在 diff；C-16 `:16` 未改 |
| C-06 / C-17 及其余契约 | 逐字节不变 | `git diff --name-only HEAD -- doc/plan` 仅 3 个被审文件；`verify_pins` 18/18；抽查 6 项 pin 不变 |

计数说明（P2-3）：18 个冻结对象中，**只有 C-16 重签**，不变的是**除 C-16 外的 17 项**（含 C-06/C-17）。因此：
- C-16 `:225` ④「C-06/C-17 与其余 16 pins 零改动」→ 数字错误（16 应为 17，或改写为「C-06/C-17 与其余 15 份（除 C-16）」）；
- 载体 `:43`「C-06/C-17 与其余 16 份冻结契约逐字节不变」→ 同样错误；
- 与 FROZEN-C16 `:48`「其余 **17** 项不变」、`:98`「其他 17 pins」矛盾。

---

## D. pin 可复算 —— **PASS**

| 核对项 | 期望 | 实测 | 判定 |
|---|---|---|---|
| C-16 工作树 sha256（verify_pins 口径） | `9fe9d5f0ae62…`（FROZEN-C16:16） | `9fe9d5f0ae6209078e149759f40b29100ee6c0d40be3022fc77bbc1ebf21a0f7` | PASS |
| `git hash-object`（blob id） | `3ef67791…`（FROZEN-C16:17；diff index `a5143d5e1..3ef677913`） | `3ef677913974ca7718b49458fd83303dab4f253a` | PASS |
| blob 原始字节 sha256（LF） | `9fe9d5f0…`（FROZEN-C16:18） | `9fe9d5f0…`（32 532 bytes、LF=233、CRLF=0） | PASS |
| `verify_pins.ps1` | 18/18 PASS | `PIN AUDIT: PASS (all 18)`；C16 `9fe9d5f0ae62`，其余 17 项与 `logs/pins.log` 逐行一致 | PASS |
| 其余 17 契约与 HEAD 冻结记录 pin 逐项相同 | 17/17 不变 | `git diff --name-only HEAD -- doc/plan` 仅 C16/FROZEN16/MATRIX；抽查 C06 `99831a20…13d4`、C17 `aefa0fa5…1a59`、C15 `d8c0a3bc…79d6`、FEA01 `0370c189…cfd5`、C05 `f6e6f3cb…4714`、C14 `05056cbf…49e9`，均与各自冻结记录 pin 及 `other-17-pins.txt` 12 前缀一致 | PASS |
| `other-17-pins.txt` 真实性 | 17 项、changed=0 | 17 行 `UNCHANGED prev=… actual=…`，`SUMMARY: 17 contracts, changed=0`；与实测前缀一致（完整 64 位由 verify_pins 覆盖） | PASS（P3-6 前缀强度） |

**复算命令**：`Get-FileHash -Algorithm SHA256`、`git hash-object`、`git cat-file blob` 三口径在 LF 最终字节上一致；`verify_pins.ps1` 读 FROZEN-C16 第一个 `| sha256… |` 行，当前行即 `9fe9d5f0…`。

**注（r1 后）**：以上为 r1 快照（`9fe9d5f0…`）。DSH 处置后当前字节 pin 为 `ad25fb3c…`，`verify_pins` 实测仍 **18/18**、证据已同步；详见 §H。

---

## E. 冻结记录 / 矩阵一致性 —— **FAIL（P2-1/P2-2/P2-3；P3-1/P3-9；pending 正确）**

### E.1 PASS 面

- §1 冻结版本 v1.4、sha256、blob id、历史 pin（v1.3/v1.1/v1.0）自洽；§1A 三口径未改；§1B 新增 v1.4 复核字节 = 冻结字节并注明 r1 pending（`:37`）。
- §2 条件行 6：`⏳`（pending），证据指向载体 §6 + `logs/pins.log`（`:48`）；条件 6 写「其余 **17** 项不变」——正确。
- §8 v1.4 段：载体/触发授权/修订内容/独立复核 pending/冻结字节 sha/历史 pin 齐备；修订内容与 C-16 实际 diff 一致（`:90-97`）。
- 矩阵 C-16 行（`:37`）：`FROZEN v1.4` 2026-11-07、条件「①v1.4 独立 byte-level 复核（载体）②C-06/C-17 零改动 ③18/18 ④PASS」、实现归属 `FEA-11-RUN-GRANT-2`；与冻结记录/载体一致。
- **无「复核前预填 approved」**：载体 §6 `r1：pending`（`:58`）；FROZEN §2 条件 6 `⏳`；§8 独立复核 `pending`。`FROZEN v1.4`/矩阵 `FROZEN v1.4` 的提前落盘与 v1.3 先例一致（§1B `:36` 明示「先冻结最终字节再复核」），不构成本项 FAIL。

### E.2 FAIL 面

- **P2-1（结构 + 不实陈述）**：`FROZEN-C16:99` 在 §8 表格末尾残留旧 §7 的「`| 其他 16 pins | 逐字节不变（C-06 与 C-16 为本批重签；复核断言见载体 §6） |`」。HEAD 中该行是 §7 表最后一行（`git show HEAD:…` L85）；插入 §8 时未把它移回/替换，导致：
  - §8 表同时有 `:98`「其他 17 pins」与 `:99`「其他 16 pins」，数字与事实互相矛盾；
  - `:99`「C-06 与 C-16 为本批重签」对 v1.4 **不成立**（本批仅 C-16 重签，C-06 零改动，pin 实测不变）；
  - §7 表因此缺最后一行（历史记录被截断）。
- **P2-2**：`FROZEN-C16:4`「冻结时间：2026-11-03（v1.0）/ 2026-11-04（v1.1）/ 2026-11-06（v1.3）」未补 `2026-11-07（v1.4）`，与 §1「冻结版本 v1.4（2026-11-07 UNFREEZE 重冻…）」不一致。
- **P2-3**：C-16 `:225` 与载体 `:43` 的「其余 16」计数错误（见 §C 计数说明）。
- **P3-1**：`FROZEN-C16:37`「r1 复核 pending，见 §7」——v1.4 记录在 §8，应为「见 §8」。
- **P3-9**：`FROZEN-C16:94`「C-06/C-17 与其余 17 pins 零改动」——2+17 的语序重复计数，建议「其余 17 项（含 C-06/C-17）零改动」。

---

## F. 载体 / 卡不夸大 —— **PASS（附 P3-3/P3-8；AC-T4 字面满足度）**

- **不写成实现/产品可用**：载体 §3 明确「新 Host × 旧 Core：多成员容器不可用（维持 L-G12②）」「旧 Host × 新 Core：行为不变」（`:40-41`）；§1 明确「契约就绪」目标是最小明文（`:12`）；卡 `status: ready`、AC-T1…T4 全未勾选（`:83-86`）。
- **保留未解决项**：卡「已知 limitation / follow-up」保留 L-P1′（M2-C1 枚举滞后）、L-P2′（2B 仍需 2A 版本通道；长 Run/加密/重启不因本契约解决）、L-P3′（契约就绪不构成实现授权）（`:94-98`）；载体 §4 风险①–③（pin 重签、facts 语义、max_entries/64 限制）保留。
- **max_entries/64 行为**：载体 §4③ 明写「超限 typed，不截断」（`:47`）；卡 T-2/T-4/AC 同样要求（`:46-48`）。**P3-3**：载体把「64 grant 上限」说成限制「单容器可授权成员数」不精确——64 是单次授权命令的 grant 数上限，单容器成员数由 `max_entries` 限制；建议措辞修正（不影响语义）。
- **AC-T4 字面**：载体 §5 括注「载体/卡不夸大（契约就绪 ≠ 实现/产品可用）」（`:53`）满足字面字符串，但建议在 §1/§3 增一句独立的边界声明（P3-8）。

---

## G. 证据真实性 —— **PASS**

| 证据 | 核对 | 判定 |
|---|---|---|
| `pre-post.sha256` | pre = `7c355ccb8f826879e34252750c642c8a7b5c138cd5be5b089a7a518bb56519e5` = HEAD v1.3 实测字节（30 583 bytes）；post = `9fe9d5f0…` = 工作树 v1.4 | PASS |
| `changed-lines.diff` | 与 `git diff HEAD -- C-16` 归一化后 45 行逐行相同（0 差异） | PASS |
| `logs/pins.log` | 18/18 PASS，与 `verify_pins.ps1` 实跑逐行一致 | PASS |
| `logs/check.log` | `Governance check: PASS (3 warnings)`，Task 2A，与实跑逐行一致 | PASS |
| `logs/check-taskpath.log` | Task 2B-PREREQ-1，与实跑逐行一致 | PASS |
| `other-17-pins.txt` | 17 行 UNCHANGED、changed=0；12 前缀与实测一致（完整值由 verify_pins 覆盖，P3-6） | PASS |

**注（r1 后）**：以上为 r1 快照证据。当前 `pre-post.sha256` post、`logs/pins.log` C16 已更新为 `ad25fb3c…`；`changed-lines.diff` 已重生成，与当前 `git diff HEAD -- C-16`（55 行）逐行一致；证据目录新增 `carrier.md` 与 `EV.md`。详见 §H。

**未跑项（NOT_RUN）**：全量 `pytest tests`、全量 `dotnet test NewManga.sln`、`NEWMANGA_FEA11_IPC=1` 真实 IPC、`generate_api_inventory.py --check`、`scope_validation.py`。本复核的契约/证据范围不依赖它们；且全量测试会改写 tracked 证据，超出「只写一个文件」的硬约束。

---

## V. 安全漏洞逐条判定（重点）

| # | 攻击假设 | 判定 | 依据 |
|---|---|---|---|
| V1 | 借 N 项跨文件/跨根读取 | **不可利用** | 同一容器 `path` + `path` 一致校验；匹配只读 `source_entries`/`source_locations`，无路径回退（`FEA-C16:68`；`source_read_refs.py:917-945,603-631`） |
| V2 | 成员内容 digest 冒充容器 facts / 反之 | **不可利用**（fail-closed）；参考点未指定（P3-4） | facts 必须 = 容器身份；匹配用 `container_facts` 对 `source_locations` 四键比对（`source_read_refs.py:613-631`） |
| V3 | locator/ordinal 注入（`.`/`..`/绝对/重复/越界） | **不可利用**；越界未明文但 fail-closed（P3-5） | locator 安全 + ordinal ≥0/唯一（`FEA-C16:68`）；`ordinal` 越界不命中 `source_entries` |
| V4 | 多 entry 绕过 64 grant 上限 / 预算 | **不可绕过** | 64 是 `grant_ids` 个数上限（`FEA-C16:83`；实现 `:457-464`）；成员数受 `max_entries`（`:70`）；folder 已有 N 成员先例 |
| V5 | facts-only / 路径推出 / 部分成功 | **无此条款** | OR + facts + 无路径回退 + 整 grant typed（`FEA-C16:68,89`） |
| V6 | 与 folder/image 语义冲突 | **无** | folder 独立函数（`source_read_refs.py:633-651`）；image 单 entry 不变（`FEA-C16:68`） |
| V7 | §2.4 per-page 匹配被放宽或绕过 | **无** | §2.4 字节未改，per-page 已按「某项」+ facts + `source_id/version` 相等（`FEA-C16:88`）；多 entry 只扩大合法成员面 |

**特别说明（OR 语义的既有性质）**：单 entry 的 `locator`/`ordinal` 可分别命中不同 `source_entries` 行（OR 语义），这是 v1.3 既有性质，v1.4 **未**扩大；若视为缺陷应另开契约议题，不在本批 UNFREEZE 处理。

---

## Findings 表

| ID | 严重度 | 事实（path:line） | 最小修复 | 阻断 |
|---|---|---|---|---|
| P1-1 | **P1** | `FEA-C16:68` 把「条目数 ≤ `budget.max_entries`」纳入「任一项不满足 → `SOURCE_ACCESS_DENIED`」；既有实现 `source_read_refs.py:172-173`、`:902-905` 与 §6 `FEA-C16:184` 对该路径返回 `SOURCE_BUDGET_EXCEEDED`，§2 `:70` 亦写「超限拒绝不截断」 | 把「超 `budget.max_entries`」从 `SOURCE_ACCESS_DENIED` 句拆出，明确「→ 既有 `SOURCE_BUDGET_EXCEEDED`，不截断」；其余结构/身份类保持 `SOURCE_ACCESS_DENIED`。改后重算 C16 pin、重冻、窄面复审 | 是 |
| P1-2 | **P1**（提交面，非提案字节） | 最终 `git diff --name-only HEAD` 含 5 个 `apps/desktop-avalonia/**` 文件（Host 源 3 + Tests 2；行数随并发写入变化，05:29 快照 `+836/−40`），mtime `05:24:18`–`05:27:52`，注释自证 FEA-11-RUN-GRANT-2A；使载体 §5②「src/apps/tools/tests 零 diff」不成立 | UNFREEZE 提交按路径只 stage 5 项（C-16/FROZEN-C16/MATRIX/载体/证据），或先完成/隔离 2A；提交后复核 `git diff --name-only <base>..<commit>` | 是（阻断提交；不改 C-16） |
| P2-1 | P2 | `FROZEN-C16:99` §8 表尾残留旧 §7「其他 16 pins（C-06 与 C-16 为本批重签）」；与 `:98`「其他 17 pins」并列矛盾，且 v1.4 仅 C-16 重签（C-06 pin 实测不变） | 把该行移回 §7 表尾（或删除残留副本），§8 只保留「其他 17 pins」正确行 | 是 |
| P2-2 | P2 | `FROZEN-C16:4` 冻结时间未含 v1.4（只到 v1.3） | 补 `2026-11-07（v1.4）` | 是 |
| P2-3 | P2 | `FEA-C16:225` 与载体 `:43`「C-06/C-17 与其余 16（份/pins）零改动」；实际 18 对象中 C-16 重签、其余 17 项不变（含 C-06/C-17），与 `FROZEN-C16:48,98`「17」矛盾 | 改为「C-06/C-17 与其余 15 份（除 C-16）零改动」或「其余 17 项（含 C-06/C-17）零改动」；C-16 字节改动需重算 pin | 是 |
| P2-4 | P2 | `FEA-C16:54` 示例 `"decoder": "zip\|cborpdf\|image"` 与 v1.4 `:68` `{zip, cbz, pdf}` 及实现 `_KINDS`（`source_read_refs.py:48`）不一致；`cborpdf` 不存在、且缺 `cbz` | 统一为 `zip\|cbz\|pdf\|image`（或注明示例为抽象写法）；属既有示例行，需登记进本批或下次 UNFREEZE | 是（实现歧义） |
| P3-1 | P3 | `FROZEN-C16:37`「见 §7」应为「见 §8」 | 改引用 | 否 |
| P3-2 | P3 | `FEA-C16:17` wire 版本 `1.2→1.3`；v1.3 载体曾明确登记 `1.2`，本次未说明为何把 v1.3 的 wire 面追溯登记为 1.3 | 在载体 §2.A 补一句「v1.3 新增 §2.4 本应登记 wire 1.3，本次补登；v1.4 无 wire 变更」 | 否 |
| P3-3 | P3 | 载体 `:47`「`max_entries`/64 grant 上限仍限制单容器可授权成员数」不精确：64 限制单次授权 grant 数，不是成员数 | 改为「`max_entries` 限制单 grant 成员数；64 限制单次授权 grant 数」 | 否 |
| P3-4 | P3 | `FEA-C16:68` 注册期「facts 与容器身份一致」的容器身份参考点未指定 | 2B 实现卡锁定「各项 facts 彼此相等，`container_facts` 只取容器路径物理身份」；或在契约补一句 | 否 |
| P3-5 | P3 | `FEA-C16:68` ordinal 越界未明文拒绝（匹配 fail-closed） | 2B 实现卡补「越界 → 拒绝」判别用例；或契约补明文 | 否 |
| P3-6 | P3 | `other-17-pins.txt` 仅 12 hex 前缀，非完整 64 位 | 证据升级为完整 sha256（或注明以 verify_pins 全量输出为准） | 否 |
| P3-7 | P3 | 卡 I-4 列「carrier」证据，但 `verification/.../**` 无载体副本；载体在 `doc/reviews/` | 在载体 §7/卡 I-4 注明「载体即 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16.md`，不复制」 | 否 |
| P3-8 | P3 | 载体只在 §5 复核要求括注「契约就绪 ≠ 实现/产品可用」，未在 §1/§3 独立声明 | 在载体 §3 或结论段增一句边界声明（AC-T4 字面） | 否 |
| P3-9 | P3 | `FROZEN-C16:94`「C-06/C-17 与其余 17 pins」重复计数语序 | 改为「其余 17 项（含 C-06/C-17）」 | 否 |

**计数：P0=0 / P1=2 / P2=4 / P3=9。**

---

## H. 复核后记（2026-11-07 05:31，DSH 并发处置后）

> **本节是 r1 定稿后的补记**：§A–§G 的实测快照是 C-16 `9fe9d5f0…`（05:29 定稿）。定稿后 DSH 在同一工作树并发处置 r1 findings，当前最终字节已变为下表右列；r2 应以当前字节 + 当前载体/证据复核。**本节不改变 §A–§G 作为 r1 时点记录的性质，但修正「当前字节」的 pin/证据结论。**

### H.1 当前字节实测（05:31 快照）

| 项 | r1 快照（§A–§G） | 当前（DSH 处置后） |
|---|---|---|
| C-16 sha256（verify_pins 口径） | `9fe9d5f0ae6209078e149759f40b29100ee6c0d40be3022fc77bbc1ebf21a0f7` | `ad25fb3c89bb1749552c3de988369ae93b5e9e7f563ce2530a5d4c65ba2ad8dc` |
| C-16 blob id | `3ef677913974ca7718b49458fd83303dab4f253a` | `b9be0acfa232154510d8453133ef8803b6b8fbbe` |
| C-16 bytes / 末尾 | 32 532 / `... 0a` | 32 577 / `... 7c 0a 0a`（末尾多一空行） |
| FROZEN-C16 pin | `9fe9d5f0…` | `ad25fb3c…`（§1/§1B/§8 已更新；L4 冻结时间已补 v1.4） |
| 载体 | 5 928 bytes（§6 r1 pending） | 6 916 bytes（`7a163cd5…`；§6 已回填 r1 `changes_requested` → 处置 → r2 pending） |
| `pre-post.sha256` post | `9fe9d5f0…` | `ad25fb3c…`（已同步） |
| `logs/pins.log` C16 | `9fe9d5f0ae62` | `ad25fb3c89bb`（已同步） |
| `changed-lines.diff` | 45 行（旧字节） | 55 行，与当前 `git diff HEAD -- C-16` **逐行一致**（实测） |
| `verify_pins.ps1` | 18/18 | **18/18 PASS**（实测；C16 `ad25fb3c89bb`） |
| 证据目录新增 | — | `carrier.md`（载体副本，sha 同工作树载体）、`EV.md`（7 文件 sha/bytes） |
| `git status`（UNFREEZE 面） | 5 项 + 并发 2A 5 文件 | **只含 UNFREEZE 面**（3 个 `M` doc/plan + 载体/r1 报告 + 证据 8 文件）；2A 的 5 个文件已由 DSH 提交为 `aa0a5562b` + `a0bafc89e`，当前 HEAD = `a0bafc89e`（05:34 实测） |

### H.2 r1 findings 处置状态（对当前字节）

| r1 ID | 状态 | 当前证据 |
|---|---|---|
| P1-1 超限错误码 | **已修** | C-16:68 现为「条目数超 `budget.max_entries` → `SOURCE_BUDGET_EXCEEDED`（不截断）；其余任一项不满足 → 整 grant typed 拒绝（`SOURCE_ACCESS_DENIED`，不部分接受）」 |
| P1-2 提交面 | **已隔离** | 2A 的 5 个 `apps/**` 修改已由 DSH 提交为 `aa0a5562b`+`a0bafc89e`；05:34 实测工作树 diff 只含 3 个 UNFREEZE doc/plan |
| P2-1 §8 残留旧行 | **已清**（但见 H.3-1） | FROZEN §8 表尾不再有「其他 16 pins」；§7 表尾的正确行同时缺失 |
| P2-2 头部冻结时间 | **已修** | FROZEN:4 已含 `2026-11-07（v1.4）` |
| P2-3 计数 | **C-16 已修**；载体 §3 已改「17」但语序仍重复 | C-16:225、变更记录、载体:43 均为 17；「C-06/C-17 与其余 17 份」仍是 2+17 语序（见 H.3-3） |
| P2-4 decoder 枚举 | **已修** | C-16:54 现为 `zip|cbz|pdf|image|folder`，与新句 `{zip,cbz,pdf}`、`_KINDS` 一致 |
| P3-1「见 §7」 | **已修** | FROZEN:37 现指向 §8，并记录 r1→r2 |
| P3-2 wire 1.3 解释 | 未处置 | C-16:17 仍为 1.3；载体 §2 A 仍无补登说明 |
| P3-3 64 表述 | 未处置 | 载体:47 仍把 64 与单容器成员数并列 |
| P3-4/P3-5 容器 identity 参考点/ordinal 越界 | 未处置 | 属 2B 实现卡事项 |
| P3-6 前缀证据 | 部分 | `other-17-pins.txt` 仍 12 前缀；`EV.md` 提供了证据文件完整 sha（非契约 pin 全量） |
| P3-7 carrier 证据 | **已解决** | 新增 `verification/.../carrier.md`（与工作树载体同 sha）+ `EV.md` |
| P3-8 AC-T4 明写 | 未处置 | 载体仍在 §5 括注 |
| P3-9 语序 | 部分 | C-16 §10 已 17；FROZEN:94「其余 17 pins」语序未改 |

### H.3 当前字节仍需 r2 关注（新增/残留）

1. **P2（新增，载体未同步）**：载体 §2.B 注册校验段（`CONTRACT-UNFREEZE-2026-11-07-C16.md:25`）仍写「条目数 ≤ `budget.max_entries`；任一项不满足 → 整 grant typed 拒绝（`SOURCE_ACCESS_DENIED`…）」，**未同步** C-16 当前的「超预算 → `SOURCE_BUDGET_EXCEEDED`；其余 → `SOURCE_ACCESS_DENIED`」拆分。载体 §6 处置①虽描述了拆分，但 §2 提案正文未改，形成同文矛盾。
2. **P3（清理副作用）**：FROZEN §7 表尾缺「其他 16 pins」行（HEAD v1.3 的 `L85` 行在清理中一并删除）；§8 的正确「其他 17 pins」保留。建议在 §7 恢复该行。
3. **P3（语序）**：载体:43「C-06/C-17 与其余 17 份」与 FROZEN:94「C-06/C-17 与其余 17 pins」仍是 2+17 语序；建议统一为「其余 17 项（含 C-06/C-17）」。
4. **P3（格式）**：C-16 末尾多一个空行（`... 7c 0a 0a`），应为单换行；若属有意的「LF 规范化」请在载体登记。
5. **P3（证据清单）**：载体 §7 未列新增的 `carrier.md`/`EV.md`；建议补入。
6. **P1-2（提交面，已隔离）**：2A 的 5 个文件已由 DSH 提交为 `aa0a5562b`（feat）+ `a0bafc89e`（test）；**05:34 实测 `git diff --name-only HEAD` 只含 3 个 UNFREEZE doc/plan 文件**（另有载体/r1 报告/证据 untracked），当前 HEAD = `a0bafc89e`。→ 当前 A 项文件面 PASS。UNFREEZE 提交时仍按路径 stage 5 项（base = `a0bafc89e`），并在提交后复核 `git diff --name-only <base>..<commit>`。
7. **矩阵**：C-16 行仍写 `FROZEN v1.4`（矩阵不写 pin）；r2 approved 后无需改 pin，但可在条件①回填「r2 approved」。

### H.4 r2 建议核对清单

- 载体 §2.B 与 C-16:68 **逐字一致**（当前不一致，见 H.3-1）；
- C-16 `ad25fb3c…` 的 sha/blob/pin 三口径、pins 18/18、其余 17 项不变（当前实测已 PASS，需 r2 重跑确认）；
- `changed-lines.diff`（55 行）与当前 `git diff HEAD -- C-16` 一致（当前实测一致）；
- 载体 §6 r2 结论回填、FROZEN §1B/§8 与载体结论一致；
- 提交隔离后的 `git diff --name-only <base>..<commit>` 只含 5 项 UNFREEZE 文件（当前 base 应为 `a0bafc89e`）；
- 上述 H.3 的 P2/P3 是否处置。

---

## 最终 verdict

**`changes_requested`（r1 时点；当前字节的处置与 r2 待办见 §H）。**

- **契约字节层面**：C-16 v1.4 的授权接受面语义**没有安全放宽**（§B/§V 全部 PASS），pin 可复算、18/18、17 项不变、证据真实（§D/§G）。但 `FEA-C16:68` 的超限错误码与既有实现/§6 冲突（P1-1），必须先修；C-16 §10⑥ 的计数错误（P2-3）同文件，建议一并修。任何 C-16 字节修复都会改变 pin，须**重算 pin + 重冻 + 窄面复审**（不得先提交后补审）。
- **冻结记录/载体层面**：§8 残留旧行（P2-1）、头部冻结时间缺 v1.4（P2-2）、计数错误（P2-3）、示例 decoder 枚举（P2-4）须在重冻前修正；这些不改变 C-16 语义，但影响冻结记录自洽性与 2B 实现歧义。
- **提交面**：最终工作树混入并发的 2A 实现（P1-2），UNFREEZE 提交必须按路径隔离；这不影响 C-16 字节，但影响「UNFREEZE 提交只含契约面」的审计结论。
- 通过标准（载体 §5）：approved 可含非阻断 P3；本轮 P1×2 + P2×4 均阻断，故返修后复审。

---

## 真实性声明

- 本报告由**独立上下文 fresh subagent** 撰写：未参与 C-16 v1.4 起草、未参与本 UNFREEZE 的前轮复核、未参与 FEA-11-RUN-GRANT-1/2 的实现或返修；只读被审字节与背景文件。
- **唯一写入**：本文件 `doc/reviews/FEA-11-RUN-GRANT-2B-PREREQ-1-r1.md`。未 `git add`/`commit`/`push`；未删除/移动任何文件；未改 C-16/冻结记录/矩阵/载体/卡/证据/STATUS/PLAN 字节。为比对 HEAD 原始字节，仅在系统 `%TEMP%` 写了一个只读副本（`git show` 重定向），已删除，未落仓库。
- **并发事实**：复核开始时工作树只有 5 项 UNFREEZE 改动；`05:24:18`–`05:27:52` 陆续出现 5 个 `apps/desktop-avalonia/**` 文件的修改（3 个 Host 源文件 + 2 个测试文件，注释自证 FEA-11-RUN-GRANT-2A），**非本复核写入**，我未参与、未审查其实现内容；报告按任务要求以**当时**最终工作树判定 A 项，并明确归因。**05:33–05:34 这些 2A 改动已由 DSH 提交为 `aa0a5562b` + `a0bafc89e`**，当前工作树 diff 只余 3 个 UNFREEZE doc/plan；§A/P1-2 的 FAIL 是 r1 快照（05:29）结论，当前字节状态见 §H。
- **事实基线**：`reviewed_head 1b615211200a174c5ada090e838b2e02e8e6fd44`；§A–§G 的被审字节为 C-16 `9fe9d5f0…`（mtime `05:17:37`–`05:18:47`）。**r1 定稿后（05:30–05:31）DSH 并发处置 r1 findings**，C-16 变为 `ad25fb3c…`、冻结记录 pin/载体/证据同步更新；§H 已记录当前字节实测与 r2 待办。若 Lead 在收到本报告后继续编辑工作树，pin 与 diff 需重新实测，本报告结论只对其记录的两次快照负责。
- **未跑项**：全量 pytest / 全量 .NET / 真实 IPC / API inventory `--check` / `scope_validation.py` 均标 **NOT_RUN**（不在本复核范围或会写 tracked 证据）；已实跑项（verify_pins、check.ps1×2、sha256/hash-object、diff 比对）均在正文给出命令与结果。
- **session**：`46c5cfef-1cfd-4953-9d9b-f781a5bc3515`（`$DSH_SESSION_ID` 实测）；parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`。
- 本报告不构成实现授权、不构成产品可用声明、不替代 DSH 的 findings 处置与集成验证。
