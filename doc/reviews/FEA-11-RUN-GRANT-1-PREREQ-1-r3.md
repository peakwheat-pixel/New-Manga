---
task: FEA-11-RUN-GRANT-1-PREREQ-1
title: FEA-11-RUN-GRANT-1-PREREQ-1 最终字节窄面复审（C-06 v1.2 + C-16 v1.3 UNFREEZE r3）
reviewer: fresh subagent（独立上下文；未参与起草/修复/前两轮复核；只读）
session: 3f908eee-d3a0-4698-b06d-a58e0fecacf9（`$DSH_SESSION_ID` 实测）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-06
repo: G:\CODEX\New Manga
branch: main
reviewed_head: b17d7282193afa6583c6c7a7bfc6456d04313af5
verdict: approved
---

# C-06 v1.2 + C-16 v1.3 UNFREEZE · 最终字节窄面复审 r3

> **结论先行：`approved`。P0=0 / P1=0 / P2=1 / P3=5（本轮新增 P2=1、P3=2；另有 r2 遗留 P3-5/P3-6/P3-9 仍 OPEN）。**
>
> - **N-01、N-02 均已关闭**：冻结记录/载体/卡统一为「16 项不变（C-06/C-16 为本批重签）」，断言面不再有「17 pins」；C-06 §5 条件 4 的 v1.2 追加句已回退，`git diff HEAD -- C-06` 的 §5 hunk 消失（C-06 现为 4 hunk：状态/日期行、§2.2、§2.3、§6），C-06:96「仅新增条目」与实际 diff 一致，处置记入载体 §6:63。
> - **字节面全部通过**：C-06 `99831a20…13d4`、C-16 `7c355ccb…19e5` = 两份冻结记录 pin；`verify_pins.ps1` **18/18 PASS**；其余 **16/16** 项实算不变；`pre-post.sha256`/`changed-lines.diff`/`logs/pins.log`/`logs/check.log`/`logs/check-taskpath.log`/`carrier.md` 与当前字节一致；Run wire/`PROTOCOL_MINOR=3`/schema/依赖/M2-C1/不变量零改动。
> - **剩余 1 项 P2 在载体登记面**：载体 §6:64 的「P3 残余处置」使用了 r1 原编号（P3-2/P3-3/P3-8）而非 r2 编号，且「其余 P3 已在 r2 处置记录中逐项说明」与实际不符（r2 P3-5/P3-6/P3-9 未逐项登记，r2 P3-8 未被该句覆盖）⇒ **N3-01（P2，非阻断，须在追加 r3 结论时一并更正）**。
> - **不构成**：本报告不批准实现、不构成 `FEA-11-RUN-GRANT-1` 释放、不构成「referenced Run 产品可用」，也不构成 push 授权。

---

## 0. 复核对象、方法与实测环境

- `reviewed_head`：`b17d7282193afa6583c6c7a7bfc6456d04313af5`（`git rev-parse HEAD` 实测；短 hash `b17d72821`），branch `main`。
- 被审字节＝**工作树最终字节**（HEAD 之后仍有未提交 UNFREEZE 改动）。`git status --porcelain -uall` 实测 **16 项**（不含本报告）：6 个 `M`＝C-06/C-16/两份冻结记录/矩阵/卡；10 个 `??`＝载体、r1、r2、`verification/FEA-11-RUN-GRANT-1-PREREQ-1/**` 7 文件。`git diff --cached` 为空（未暂存）。
- 只读事实以工作树最终字节为准；载体/卡/冻结记录的自述仅作索引，不采信其结论。为读取 HEAD 原始字节，只在系统 `%TEMP%` 写了只读副本（`git cat-file blob HEAD:` 重定向），未落仓库。
- 唯一写入：本报告。未 `git add`/`commit`/`push`，未删除/移动文件，未改任何被审字节、证据、卡、冻结记录或矩阵。
- **NOT_RUN**：pytest、.NET build/test、真实 IPC、API inventory。理由：本卡 `out_of_scope` 禁生产代码，实测 `src/**`、`apps/**`、`tools/**`、`tests/**`、`doc/contracts/**` 相对 HEAD **零 diff**；字节级复审不需要这些门禁。未跑即标 NOT_RUN，不以静态判断代替。

### 0.1 本轮实测命令与结果（摘要）

| 命令 | 实测结果 |
|---|---|
| `git diff --name-only HEAD -- doc/plan/` | 恰好 5 个：C-06、C-16、`FEA-CONTRACT-FROZEN-C06`、`...-C16`、`FEA-CONTRACT_FREEZE_MATRIX.md` |
| `git diff --name-only HEAD -- src apps tools tests doc/contracts` | **空（NONE）** |
| `Get-FileHash -Algorithm SHA256` C-06 / C-16 | `99831A20FFD608257B4F2CF46F63F3836F605B35A4DE787C4AB803E5DD6013D4` / `7C355CCB8F826879E34252750C642C8A7B5C138CD5BE5B089A7A518BB56519E5` |
| `git hash-object` C-06 / C-16 | `9bbd93a01cb74886f2cddb6aeeafe28455baaaf3` / `a5143d5e162f60ffbd902d7dc60792b162c6a378`（= 两份冻结记录 `:17`） |
| HEAD 原始字节 sha256（`git cat-file blob HEAD:` 重定向后实算） | C-06 `8faa8cd1…b2003`、C-16 `0b9511a5…e5905` = `pre-post.sha256` 的 pre 值 = v1.1 历史 pin |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`；C06 `99831a20ffd6`、C16 `7c355ccb8f82`；与 `logs/pins.log` 逐行相同 |
| `check.ps1` / `check.ps1 -TaskPath` | 均 `Governance check: PASS (3 warnings)`，与 `logs/check.log`、`logs/check-taskpath.log` 逐行相同 |
| `changed-lines.diff` vs `git diff HEAD -- C06 C16` | 归一化（CRLF→LF、TrimEnd）后**逐行相同**（两侧归一化后 sha256 均 `965318b0…d74452`；证据原件因 PowerShell 捕获带 CRLF，sha `11351eea…f18`，diff 语义一致） |
| 其余 16 项实算（全部 16 项） | 与 `other-16-pins.txt`/`pins.log` 全部一致（C01b `3c9f5af7d74f`、C07 `3fdb44e49afe`、C15 `d8c0a3bcfc21`、C17 `aefa0fa5b17e`、FEA01 `0370c18932b1` 等） |
| 两份契约 CRLF 计数 | C-06 0 个 CR（11701 B）、C-16 0 个 CR（30583 B），纯 LF ⇒ 工作树 sha256 = blob 内容 sha256 |

---

## A. N-01 关闭（16 项不变口径） —— **PASS**

四处被指出的「17 pins」已全部改为 **16**，并与 C-06/C-16 为本批重签的说明一致：

| 位置 | 当前字节 |
|---|---|
| `doc/plan/FEA-CONTRACT-FROZEN-C06.md:81` | 「其他 16 pins \| 逐字节不变（C-06 与 C-16 为本批重签；复核断言见载体 §6）」 |
| `doc/plan/FEA-CONTRACT-FROZEN-C16.md:85` | 「其他 16 pins \| 逐字节不变（C-06 与 C-16 为本批重签；复核断言见载体 §6）」 |
| `doc/plan/FEA-CONTRACT-FROZEN-C16.md:46` | 「`verify_pins` **18/18**（C16 新值、其余 16 项不变）」 |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md:36` | 「其余 16 pins 断言」；`:45` 另有「其余 16 份冻结契约逐字节不变」 |
| `doc/tasks/FEA-11-RUN-GRANT-1-PREREQ-1.md:57/:114/:116/:123/:145` | D-2/AC-P1/AC-P3/复核要求/门禁均写 **16** 项 / 16/16 |

- **残留断言检查**：本批 6 份被审文档中已无「其他/其余 17 pins」形式的**未变项断言**。仅存的历史文本：
  - 载体 `:63` 的「写『17 pins』」是对 r2 N-01 finding 的**引述**，不是当前断言（正确）；
  - `FROZEN-C16:44` 条件 3「`verify_pins.ps1` **17/17**」是 **v1.1 时点的历史条件行**（证据指向 `verification/FEA-09-PREREQ-1/`），不是本批 16 项未变断言；见 **N3-03**（建议标注时点）。
- 交叉核对：`other-16-pins.txt` 16 项 `prev=actual`、`SUMMARY: 16 contracts, changed=0`；本轮全量实算 16 项一致（见 §E）。**N-01 CLOSED。**

## B. N-02 关闭（C-06 §5 条件 4 回退与变更记录一致性） —— **PASS**

- **§5 hunk 已消失**：`git diff -U0 HEAD -- doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md` 的 hunk 为 `@@ -3,2 +3,2 @@`、`@@ -42,0 +43 @@`、`@@ -54,0 +56 @@`、`@@ -93,0 +96 @@` —— 即状态/日期行、§2.2 行、§2.3 行、§6 变更记录，**共 4 hunk，无 §5**（对照 r2 的 5 hunk）。
- **原文本已恢复**：`FEA-C06_SOURCE_AUTH_DRAFT.md:87` 现为「4. **wire 版本由 DSH 批准**（v1.1 minor 增量）；」，与 HEAD 原字节一致（无 v1.2 追加句）。
- **变更记录与 diff 一致**：`FEA-C06_SOURCE_AUTH_DRAFT.md:96` 写「§2.2 增…；§2.3 增…；仅新增条目，既有 grant 形状/TTL≤300s/撤销/失联/错误闭集零改动」；实际 diff 除头部状态/日期元数据外**只有新增行**，无既有条款改写 ⇒「仅新增条目」字面成立。
- **处置已记入载体 §6**：`doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md:63`「**回退 C-06 §5 条件 4 追加句**（保持『仅新增条目』口径；additive 事实由 C-16 §0 与冻结记录承载），修正 17→16（含载体 §2.C），补 FROZEN-C06 §2 v1.2 核验行；C-06 因此重算 pin（`99831a20…`），C-16 pin 不变（`7c355ccb…`）」。
- **中间态 pin 交叉核对**：`FROZEN-C06:35` 记 r1 复核字节 `1e5e6927…`、r2 `6214ef77…`，分别与 r1 报告 §0.1（`1e5e6927…`）和 r2 报告 §0.1（`6214ef77…`）一致；`FROZEN-C06:36` 的最终字节 `99831a20…` = 本轮实测。**N-02 CLOSED。**

## C. r1/r2 其余 findings —— **P1/P2：PASS（全 CLOSED）；P3 残余：FAIL（N3-01，非阻断）**

### C.1 P1（能力缺失口径）—— **CLOSED**

五处口径统一为「缺失 → 不铸/不绑定、按现状 dispatch」，不再把 `CORE_CAPABILITY_MISSING` 写成 Run 的阻断：卡 D-4（`doc/tasks/FEA-11-RUN-GRANT-1-PREREQ-1.md:59`）、卡 §兼容与影响（`:128`）、卡 I-3（`:81`、`:89`）、C-16 §0 v1.3 能力行（`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:22`）、载体 §3（`CONTRACT-UNFREEZE-2026-11-06-C06-C16.md:42`）。C-16 中 `CORE_CAPABILITY_MISSING` 仅用于既有 `source.read/1`/`source.resolve-secret/1` 门（`:20-21`）与 §7 泛化条款（`:205`），不针对 `source.read.run/1`。

### C.2 P2-1 / P2-2 / P2-5 —— **CLOSED**

- **P2-1 失败形态统一**：C-06 `:56`「任一目标页不可授权 → **整体 typed `SOURCE_ACCESS_DENIED`**、零绑定写入、Host 不得 dispatch（C-16 v1.3 §2.4）」；C-16 `:85`「不使用『成功响应 + refused 列表』形态」、`:88`「整体 typed `SOURCE_ACCESS_DENIED`（`details={"refused_pages": n}`）且零映射写入（不返回部分成功、`bound_pages` 不适用）」。
- **P2-2 facts 核验**：C-16 `:87`「并核验该 entry 的 **facts**（`volume_serial`/`file_id`/`size`/`sha256`）与 `source_locations` 当前物理身份一致（`source_entries`/`source_locations` 逐项核对，**无路径回退**）」；C-06 `:43` 同域。
- **P2-5 gate 谓词**：C-16 `:87`「沿用 Run 目标/commit guard 的**同一** gate 谓词，C-17 §3.3；无 publication 行按既有 open 处理」；`:90`「publication gate 的两读面既有差异（L-R11，`core_assembly.read_gate` vs resolve 面 `_assert_source_sync_gate`）不属于本命令语义，本命令不引入第三套 gate 判定」。回源核对：`read_gate` docstring 自述「the single definition shared by the Run commit guard…」（`src/bootstrap/core_assembly.py:1249`），`_parse_run_scope` 在 `src/bootstrap/core_service.py:5724`；本轮 `src` 零 diff。

### C.3 P2-3（不再预填 approved） / P2-4（limitation 登记） —— **CLOSED**

- **P2-3**：`FROZEN-C06:34`「r3 pending」、`:49` 条件 6 状态 `⏳`；`FROZEN-C16:46` 条件 5 `⏳`、`:82`「**r3 窄面复核 pending**」；载体 `:65`「pending」。全树未见把 v1.2/v1.3 写成 approved 的断言（C-06 `:3`、C-16 `:3` 的 approved 均限定为 v1.1 历史并指向冻结记录）。
- **P2-4**：载体 §4 `:49` 登记 L-G1/L-G9/L-G2/L-R11（L-G10）；卡 L-P2 `:135` 登记 L-G1/L-G2/L-G9/L-G10。

### C.4 r1 P3（8 项）逐条

| r1 ID | 判定 | 依据 |
|---|---|---|
| R1-P3-1 卡 §5→§6 | **CLOSED** | 卡 I-2 `:76`「§6 变更记录追加 v1.2 行」 |
| R1-P3-2 §2.4 嵌套 | **ACCEPTED** | 载体 `:64` 明示「§2.4 置于 §2 下为有意结构，接受」（编号写作 P3-2，见 N3-01） |
| R1-P3-3 错误码措辞 | **ACCEPTED** | 载体 `:64` 明示接受；`HOST_ONLY_REQUIRED`/`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH` 确为 M2-C1 §5.7 既有码（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:541,552-554`），无新增码 |
| R1-P3-4 证据缺 `carrier.md` | **CLOSED** | 证据副本存在（`verification/FEA-11-RUN-GRANT-1-PREREQ-1/carrier.md`，10953 B），与 doc 载体 sha256 **相同**（`B8199412…FFF1`）；副本卫生按 P3-7 接受 |
| R1-P3-5 冻结时间/去重 | **CLOSED（时间）** | `FROZEN-C06:4`、`FROZEN-C16:4` 已补 v1.2/v1.3 时间；去重残余 = r2 P3-9（OPEN） |
| R1-P3-6 状态行历史复核标注 | **CLOSED** | 两契约 `:3` 保留上一版复核标注并指向冻结记录 |
| R1-P3-7 `command` 取值域 | **CLOSED（附措辞残余）** | C-16 `:83` 已限定 `COMMAND_CATALOG` 中可由 scope 展开的 Run 起始命令；措辞不一致残余 = r2 P3-5（OPEN） |
| R1-P3-8 C-06 版本句 | **ACCEPTED** | C-06 `:58` 仍写「本组命令 v1.1」，载体 `:64` 明示接受（编号写作 P3-8，见 N3-01） |

### C.5 r2 P3（9 项）逐条

| r2 ID | 判定 | 依据 |
|---|---|---|
| P3-1 §2.4 结构 | **ACCEPTED** | 载体 `:64` 接受；C-16 `:37`/`:73` 未改 |
| P3-2 错误码措辞 | **ACCEPTED** | 载体 `:64` 接受；C-16 `:89` 未改 |
| P3-3 C-06:58 仍 v1.1 | **ACCEPTED** | 载体 `:64` 接受；C-06 `:58` 未改 |
| P3-4 C-06 条件表无 v1.2 行 | **CLOSED** | 已补 `FROZEN-C06:49` 条件 6（v1.2，`⏳`）；表头口径见 N3-03 |
| P3-5 `command` 措辞 C-16/卡不一致 | **OPEN（未逐项登记）** | C-16 `:83` 写 `COMMAND_CATALOG`，卡 `:83` 只写「可由 scope 展开的 Run 起始命令」；载体未逐项登记 → N3-01 |
| P3-6 folder 源 facts 映射 | **OPEN（未逐项登记）** | C-16 `:87` 仍按 `source_locations` 统一表述；载体未逐项登记 → N3-01（不改变「无路径回退」不变量） |
| P3-7 `carrier.md` 副本 | **ACCEPTED** | 载体 `:64` 明示「副本与原件 sha 相同为证据副本，接受」；当前副本与 doc 载体逐字节相同（含 `r3 pending`） |
| P3-8 卡指针/session 回填 | **OPEN（post-approval）** | 卡 `:10`/`:115` 仍只指 r1；冻结记录 `:78`/`:82` 写「r1/r2 报告」。r3 approved 后须回填 r3 session/reviewed_head → N3-02 |
| P3-9 v1.1 pin 重复 | **OPEN（未逐项登记）** | `FROZEN-C06:32` 与 `:37` 重复 v1.1 pin；载体未逐项登记 → N3-01（无害冗余） |

**C 的小结**：P1 与全部 P2 实质 CLOSED；P3 中 5 项已被载体 §6 明示接受或已修复（P3-1/P3-2/P3-3/P3-4/P3-7），**4 项未逐项登记或仍在后置动作中**（r2 P3-5/P3-6/P3-9、r2 P3-8），另有载体编号错配本身 ⇒ **N3-01/N3-02**。这属于登记面，不触碰契约字节、pin 或证据。

## D. 最终字节最小性 —— **PASS**

- **文件面**：`git diff --name-only HEAD -- doc/plan/` 恰为预期 **5** 文件；另有卡 `doc/tasks/FEA-11-RUN-GRANT-1-PREREQ-1.md`（allowed_paths 内）与未跟踪载体/报告/证据；`doc/contracts`、`src`、`apps`、`tools`、`tests` **0 文件**；无暂存。
- **C-06 diff（4 hunk，无 §5）**：`@@ -3,2 +3,2 @@`（状态行+日期行）、`@@ -42,0 +43 @@`（§2.2 新行）、`@@ -54,0 +56 @@`（§2.3 新行）、`@@ -93,0 +96 @@`（§6 变更记录）。逐条对应载体 §2.A.1–§2.A.4 与卡 I-2 四项，**无未登记段落**。
- **C-16 diff（4 hunk / 6 处改动）**：`-U3` hunk 为 `@@ -1,7 +1,7 @@`、`@@ -14,11 +14,12 @@`、`@@ -69,6 +70,25 @@`、`@@ -201,10 +221,11 @@`；`-U0` 展开为状态/日期、wire 行、能力行、§2.4 新增块、§10 条件⑤、变更记录共 6 处。逐条对应载体 §2.B.1–§2.B.4，**无未登记段落**。
- **不变量零改动（逐项）**：

| 不变量 | 证据 | 结论 |
|---|---|---|
| grant 四维 scope 形状 | C-06 `:39`、C-16 `:51-60` 无 hunk | 零改动 |
| TTL ≤300s | C-06 `:40` 无 hunk；C-16 §2.4 `:75`/`:88` 明写「不改变/不延长」 | 零改动 |
| 撤销语义 | C-06 `:42`、C-16 `:23`/`:204` 无 hunk | 零改动 |
| 失联语义 | 同上 | 零改动 |
| C-16 §6 错误闭集无新增码 | C-16 `:169-194` 无 hunk；§2.4 只引用 `SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_EXPIRED`/`SOURCE_GRANT_REVOKED` 与 M2-C1 §5.7 envelope 既有码 | 无新增码 |
| §7 脱敏 | C-16 `:196-205` 无 hunk；§2.4 `:89`「脱敏沿用 §7」 | 零改动 |
| §3.1 fresh-grant/密码通道 | C-16 `:102-128` 无 hunk | 零改动 |
| `RegisterSourceReadGrant` 语义 | C-16 `:37-71` 主体无 hunk（§2.4 插在 `:72` 之后） | 零改动 |
| `RevokeSourceReadGrant` 语义 | C-06 `:55`、C-16 `:23`/`:204` 无 hunk | 零改动 |
| Run wire 请求/响应 | `src` 零 diff；`doc/contracts` 零 diff | 零改动 |
| `CORE_PROTOCOL_MINOR` | `PROTOCOL_MINOR = 3`（`src/bootstrap/core_service.py:320`），`src` 零 diff | 零改动 |
| schema/迁移/依赖 | `src` 零 diff；依赖文件不在 diff | 零改动 |
| M2-C1 | `doc/contracts` 零 diff | 未改 |

- **备注（非 finding）**：C-06 `:58` 仍写「本组命令 v1.1」，是 r2 P3-3 已接受的 v1.1 版本语境（additive 事实由 C-16 §0 `:17` 的 `source-access-wire/1.2` 承载），不构成本批新增命令的语义冲突。

## E. pin 与证据 —— **PASS**

- **pin 复算**：C-06 工作树 sha256 `99831a20…13d4` = `FROZEN-C06:16`/`:18` 的 pin；C-16 `7c355ccb…19e5` = `FROZEN-C16:16`/`:18` 的 pin。两值 `git hash-object` = `9bbd93a0…`/`a5143d5e…`，分别等于冻结记录 `:17` 的 blob id；两文件 CR=0（纯 LF），故 blob 内容 sha256 = 工作树 sha256。
- **改前值**：HEAD 原始字节实算 = `8faa8cd1…`/`0b9511a5…`，等于 `pre-post.sha256` 的 pre 行，也等于两份冻结记录的 v1.1 历史 pin。
- **`verify_pins.ps1`**：实测 `PIN AUDIT: PASS (all 18)`，C06 `99831a20ffd6`、C16 `7c355ccb8f82`；与 `logs/pins.log` **逐行相同**（本轮复跑比对 True）。
- **其余 16 项**：`other-16-pins.txt` 16 项全部 `prev=actual`、`SUMMARY: 16 contracts, changed=0`；本轮**实算全部 16 项**（非抽查）均相等，与 `pins.log`/冻结记录一致。
- **`changed-lines.diff`**：与 `git diff HEAD -- C06 C16` 归一化后逐行相同（不是手写摘要）；仅含两份契约，4+4 个登记段落。
- **日志**：`logs/pins.log`、`logs/check.log`、`logs/check-taskpath.log` 与复跑逐行相同；`check.log` 与 `check-taskpath.log` 亦逐字节相同（默认 `check.ps1` 实测解析到同一 Task，属预期）；`check` 仍为 PASS（3 warnings，未新增）。
- **`carrier.md`**：与 doc 载体 sha256 相同（`B8199412…FFF1`），当前内容包含 r3 pending；按 r2 P3-7 作为证据副本接受，DSH 追加 r3 结论后须同步副本（见 N3-02）。
- **方法备注**：工作树 blob（`9bbd93a0…`/`a5143d5e…`）尚未入 object DB（未 `git add`，本报告也不得 add），故 `git cat-file` 对它们不可用；本报告用 ① `git hash-object` 复现记录 blob id、② 两文件实测 0 个 CRLF（纯 LF）两条等价事实核验「blob 内容 sha256 = 工作树 sha256」。

## F. 不夸大 —— **PASS**

- 卡 `:44`「本卡只交付契约字节与冻结证据：不构成实现授权，不构成『referenced Run 产品可用』」；L-P3 `:136`「契约就绪不构成实现授权；`FEA-11-RUN-GRANT-1` 释放前不得写码」。
- 载体 §1 `:10`「生产 referenced 页 Run 仍不可端到端（L-R1）」；§3 `:42-44` 保留兼容/影响；§4 `:49` 保留 L-G1/L-G9/L-G2/L-R11 风险；矩阵 C-16 行 `:37`「Run 接线归 FEA-11-RUN-GRANT-1」。
- **未预填 approved**：`FROZEN-C06:34`「r3 pending」、`:49` `⏳`、`:78`「r3 窄面复核 pending」；`FROZEN-C16:46` `⏳`、`:82`「r3 pending」；载体 `:65`「pending」。
- **观察（非 finding）**：两份契约状态行与矩阵标注 `FROZEN v1.2/v1.3`，同时冻结记录把 r3 条件置 `⏳`、`FROZEN-C06:36` 明写「本次先冻结最终字节再复核」——这是「先冻结最终字节、后补独立复核结论」的显式口径，**不是** approved 既成事实断言；r3 批准后按 DSH 流程回填即可。

---

## r1 findings 逐条处置判定

| r1 ID | 严重度 | 判定 | 依据 |
|---|---|---|---|
| R1-P1-1 | P1 | **CLOSED** | 卡 D-4 `:59`、I-3 `:81/:89`、§兼容 `:128`、C-16 §0 `:22`、载体 §3 `:42` 五处同文「不铸/不绑、按现状 dispatch」 |
| R1-P2-1 | P2 | **CLOSED** | C-06 `:56`、C-16 `:85/:88` 统一为整体 typed `SOURCE_ACCESS_DENIED`、零绑定写入、不返回部分成功 |
| R1-P2-2 | P2 | **CLOSED** | C-16 `:87` 已补 facts 四键与 `source_locations` 物理身份核验、逐项核对、无路径回退 |
| R1-P2-3 | P2 | **CLOSED** | 冻结记录/载体全部 pending（`FROZEN-C06:34/:49/:78`、`FROZEN-C16:46/:82`、载体 `:65`） |
| R1-P2-4 | P2 | **CLOSED** | 载体 `:49` 登记 L-G1/L-G9/L-G2/L-R11；卡 L-P2 `:135` |
| R1-P2-5 | P2 | **CLOSED** | C-16 `:87/:90` 复用 Run 目标/commit guard 同一谓词、无 publication 行按 open、不引入第三套；`read_gate` docstring/接线一致（`core_assembly.py:1249`） |
| R1-P3-1 | P3 | **CLOSED** | 卡 I-2 `:76` 改为 §6 |
| R1-P3-2 | P3 | **ACCEPTED** | 载体 `:64` 明示接受（编号错配见 N3-01） |
| R1-P3-3 | P3 | **ACCEPTED** | 载体 `:64` 明示接受；M2-C1 §5.7 既有码（`M2-C1:541,552-554`） |
| R1-P3-4 | P3 | **CLOSED** | `carrier.md` 存在且与 doc 载体同 sha（`B8199412…`） |
| R1-P3-5 | P3 | **CLOSED（时间）/ OPEN（去重）** | 时间已补；去重 = r2 P3-9（OPEN，N3-01） |
| R1-P3-6 | P3 | **CLOSED** | 两契约 `:3` 保留上一版复核标注 |
| R1-P3-7 | P3 | **CLOSED（附措辞残余）** | C-16 `:83` 已限定 `COMMAND_CATALOG` + 同一 scope 展开器；措辞残余 = r2 P3-5（OPEN） |
| R1-P3-8 | P3 | **ACCEPTED** | 载体 `:64` 明示接受（编号错配见 N3-01） |

## r2 findings 逐条处置判定

| r2 ID | 严重度 | 判定 | 依据 |
|---|---|---|---|
| N-01（17 pins） | P2 | **CLOSED** | 四处改 16；断言面零残留；16/16 实算不变（§A/§E） |
| N-02（§5 追加句） | P2 | **CLOSED** | §5 hunk 消失（C-06 4 hunk）；C-06 `:87` 恢复原文本；`:96` 与 diff 一致；载体 `:63` 记录处置 |
| P3-1 | P3 | **ACCEPTED** | 载体 `:64`（有意结构） |
| P3-2 | P3 | **ACCEPTED** | 载体 `:64`（措辞明确） |
| P3-3 | P3 | **ACCEPTED** | 载体 `:64`（历史版本说明） |
| P3-4 | P3 | **CLOSED** | `FROZEN-C06:49` 已补 v1.2 条件行；表头口径见 N3-03 |
| P3-5 | P3 | **OPEN** | C-16 `:83` 与卡 `:83` 措辞仍不一致；未逐项登记 → N3-01 |
| P3-6 | P3 | **OPEN** | C-16 `:87` 的 folder facts 映射未细化；未逐项登记 → N3-01 |
| P3-7 | P3 | **ACCEPTED** | 载体 `:64`；副本与原件 sha 相同 |
| P3-8 | P3 | **OPEN（post-approval）** | 卡 `:10/:115`、冻结记录 `:78/:82` 仍只到 r1/r2 → N3-02 |
| P3-9 | P3 | **OPEN** | `FROZEN-C06:32/:37` v1.1 pin 仍重复；未逐项登记 → N3-01 |

---

## 新 findings

| ID | 严重度 | 事实（path:line） | 最小修复 |
|---|---|---|---|
| **N3-01** | **P2** | 载体 §6「P3 残余处置」（`doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md:64`）用 r1 原编号：`P3-2`（§2.4 置于 §2 下＝r2 的 P3-1）、`P3-3`（复用 §6 闭集＝r2 的 P3-2）、`P3-8`（C-06 §2.3 末尾 v1.1 语境＝r2 的 P3-3）；同句「其余 P3 已在 r2 处置记录中逐项说明」与实际不符——r2 的 P3-5（`command` 措辞，C-16 `:83` vs 卡 `:83`）、P3-6（folder 源 facts 映射，C-16 `:87`）、P3-9（`FROZEN-C06:32/:37` v1.1 pin 重复）均未逐项登记，r2 的 P3-8（卡/冻结记录指针与 session 回填，卡 `:10/:115`、`FROZEN-C06:78`、`FROZEN-C16:82`）被该「P3-8」标签覆盖到另一条目 | 在追加 r3 结论时把 §6 的 P3 段改为**逐项清单**（建议用 `R2-P3-1…R2-P3-9` 前缀），逐项标 CLOSED/ACCEPTED/DEFERRED，并将 P3-5/P3-6/P3-9 明确接受或排入下轮 UNFREEZE 维护、P3-8 列为 approved 后回填项。**仅改载体文本；不改契约字节、无需重算 pin**。非阻断，但须在提交前完成（DSH 本就要在载体 §6 追加 r3 结论） |
| **N3-02** | **P3** | r3 的 session/reviewed_head 尚未回填：卡 `reviewer`（`doc/tasks/FEA-11-RUN-GRANT-1-PREREQ-1.md:10`）与 AC-P2（`:115`）仍只指 `...-r1.md`；`FROZEN-C06:78`/`FROZEN-C16:82` 写「session/reviewed_head 在载体与 r1/r2 报告」；证据 `carrier.md` 也停在「r3 pending」 | approved 后把 r3 session `3f908eee…`/`reviewed_head` 追加到载体 §6、卡 AC-P2/reviewer 指针、两份冻结记录对应行，并同步 `verification/FEA-11-RUN-GRANT-1-PREREQ-1/carrier.md`（保持副本与原件同 sha） |
| **N3-03** | **P3** | 冻结记录表格口径两处历史/批次混排：①`FROZEN-C16:44` 条件 3 仍写「`verify_pins.ps1` **17/17**」（v1.1 时点历史行，未标时点，与同表条件 5 的 18/18 并置易误读）；②`FROZEN-C06:49` 的 v1.2 批次条件编为「6」，但表头 `:42` 写「C-06 §5 条件」，而 C-06 §5 只有 5 条 | 下轮记录维护时给历史行加「（v1.1 时点）」注记，并把 `FROZEN-C06` 第 6 行标注为「v1.2 批次条件」或调整表头；不影响任何 pin 与判读 |

> 计数：**本轮新增 P0=0 / P1=0 / P2=1 / P3=2**（N3-02 为 r2 P3-8 的延续登记）；连同 r2 遗留 P3-5/P3-6/P3-9，本报告开放项合计 **P2=1 / P3=5**。均为非阻断登记/维护项，不涉及契约条款、不变量、pin 或证据真实性。

## 最终判定

- **verdict：`approved`**（P0=0、P1=0、P2=1、P3=5；P2/P3 均非阻断并已登记）。
- **已闭环**：N-01（16 项不变口径统一）、N-02（§5 回退、变更记录一致、处置入载体）；C-06 v1.2 / C-16 v1.3 的语义面、不变量、pin 与证据均通过——18/18、16/16 未变、4+4 登记 hunk、Run wire/`PROTOCOL_MINOR=3`/schema/依赖/M2-C1 零 diff、`pre-post.sha256`/`changed-lines.diff`/日志/`carrier.md` 可复算、无夸大。
- **提交前（commit gate）**：DSH 在载体 §6 追加 r3 `approved` 结论时，必须一并完成 **N3-01**（P3 逐项清单/编号更正）与 **N3-02**（r3 session/reviewed_head 回填、`carrier.md` 同步）；**N3-03** 可在同一次记录维护中完成。上述只改登记文本，**不需要重跑字节复核、不影响 pin（C-06 仍 `99831a20…`、C-16 仍 `7c355ccb…`，pins 仍 18/18）**；建议复跑 `check.ps1`（默认 + `-TaskPath`）做最终确认。
- **范围声明**：本报告只对**工作树最终字节**（`reviewed_head=b17d7282193afa6583c6c7a7bfc6456d04313af5` 之上的 UNFREEZE 改动）负责；不批准实现、不释放 `FEA-11-RUN-GRANT-1`、不构成「referenced Run 产品可用」、不构成 push 授权。

## 真实性声明

本报告是本次复审中**唯一**写入的文件（`doc/reviews/FEA-11-RUN-GRANT-1-PREREQ-1-r3.md`）。复审者为独立上下文的 fresh subagent，未参与 C-06 v1.2 / C-16 v1.3 的起草、r1/r2 复核或本轮处置；未修改被审字节、证据、卡、冻结记录或矩阵；未执行 `git add`/`commit`/`push`；未删除或移动任何文件。所有 sha256、pin、diff、门禁结论均由本轮命令在 `reviewed_head=b17d7282193afa6583c6c7a7bfc6456d04313af5` 的**工作树最终字节**上实测得出，未采信载体/卡/冻结记录的自述结论；未跑项已在 §0 标 `NOT_RUN`。
