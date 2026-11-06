---
task: FEA-11-RUN-GRANT-1-PREREQ-1
title: FEA-11-RUN-GRANT-1-PREREQ-1 独立 byte-level 契约复核 r1（C-06 v1.2 + C-16 v1.3 UNFREEZE）
reviewer: fresh subagent（独立上下文；未参与起草；只读）
session: b4cd858d-709e-4ad0-886b-bc6a7b359bf7（$DSH_SESSION_ID 实测；以 Lead 记录为准）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-06
repo: G:\CODEX\New Manga
branch: main
reviewed_head: b17d7282193afa6583c6c7a7bfc6456d04313af5
verdict: changes_requested
---

# C-06 v1.2 + C-16 v1.3 UNFREEZE · 独立 byte-level 复核 r1

> **结论先行：`changes_requested`。P0=0 / P1=1 / P2=5 / P3=8。**
>
> - **两份契约字节本身未发现 P0/P1**：C-06/C-16 的 sha256、`verify_pins` 18/18、其余 16 项 pin、`CORE_PROTOCOL_MINOR`/schema/依赖/Run wire/M2-C1/C-07/C-08/C-15/C-17/ADJ-001 零 diff 均已实测通过（见 §A–§D）。
> - **唯一 P1 在卡面（`doc/tasks/FEA-11-RUN-GRANT-1-PREREQ-1.md` 已在 HEAD 提交，本轮不可自我修正）**：D-4/I-3 写「能力缺失 → `CORE_CAPABILITY_MISSING`，不铸 grant、不 dispatch」，而**同一卡 §兼容与影响**、**C-16 §0 落盘字节**、**载体 §3** 都写「不铸/不绑、按现状 dispatch（既有 managed Run 零变化）」。两种口径对「旧 Core 上 Run 是否被拒、以何码失败」给出不同答案，AC-P1「C-06/C-16 只含本卡 I-2/I-3 登记的增量」因此不成立。
> - **返修面极小**：只改卡面（及必需的载体/证据），**不触碰 C-06/C-16 字节**，故无需重算 2/18 pin；改后做窄面复审（卡 diff + 两份契约 sha 不变 + pins 18/18）即可。
> - **另须在提交前处理 P2-3**：两份冻结记录已把「独立复核 approved（P0=0/P1=0）」与 C-16 §2 条件 5「✅」写成既成事实，而载体 §6 仍是 `pending`。本报告既判 P1，这些断言在提交前必须先按实际结论回填/改写（否则即为不实证据）。

---

## 0. 复核对象、方法与实测环境

- reviewed_head：`b17d7282193afa6583c6c7a7bfc6456d04313af5`（`git rev-parse HEAD` 实测），branch `main`。
- 工作树待提交面（`git status --porcelain -uall`，共 11 项）：5 个 `M`（C-06、C-16、两份冻结记录、矩阵）+ 1 个新载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md` + `verification/FEA-11-RUN-GRANT-1-PREREQ-1/` 下 5 个文件（`pre-post.sha256`、`changed-lines.diff`、`other-16-pins.txt`、`logs/pins.log`、`logs/check.log`）；无 `carrier.md`（见 P3-4）。
- 只读事实以**工作树最终字节**为准；载体/卡面自述仅作索引，不直接采信。对载体引用的代码位置（`_bindings` 生产者、Run 命令面、host-control 闭集、typed 失败点）逐处回源核对。
- 唯一写入：本报告。未 `git add`/`commit`/`push`，未删/移任何文件，未改任何被审字节。为比对 HEAD 原始字节，仅在系统 `%TEMP%` 写了 2 个只读副本（`git show` 的重定向输出），未落仓库。

### 0.1 本轮实测命令与结果（摘要）

| 命令 | 实测结果 |
|---|---|
| `git diff --name-only HEAD` | 恰好 5 个文件：C-06/C-16/`FEA-CONTRACT-FROZEN-C06`/`...-C16`/`FEA-CONTRACT_FREEZE_MATRIX.md` |
| `git diff --name-only HEAD -- doc/contracts doc/plan src apps tools` | 同上 5 个 `doc/plan` 文件；`doc/contracts`/`src`/`apps`/`tools` **0 文件** |
| `Get-FileHash -Algorithm SHA256 doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md` | `1e5e6927376d0eacb82ed479e84c891e02512c920a5b8cf6e29d78e063ad350f` |
| `Get-FileHash -Algorithm SHA256 doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `274b031cdebf26ab228d747a399c13a343f4a38ed4b143660a140e27d255cb19` |
| `git hash-object`（两份契约） | C06 `3524b6be6910c63c6ac73c71969d750b04e91ddc`；C16 `7d277439e5d0150551669f7ebc520886837aed5f` |
| HEAD 原始字节 sha256（`git show HEAD:` 字节重定向后 `Get-FileHash`） | C06 `8faa8cd139f2e9c599dcd34063a5ac1a85941ecac287fcd693eb43d2109b2003`；C16 `0b9511a55ea15fafdc2de7d33fb204e5c7e2cf2efed69977ee6dd092f22e5905` |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，C06 `1e5e6927376d`、C16 `274b031cdebf`，其余 16 项与 `logs/pins.log` 逐行一致 |
| `pwsh -NoProfile -File tools/governance/check.ps1` / `-TaskPath ...` | 两次均 `Governance check: PASS (3 warnings)`，输出与 `logs/check.log` 逐行一致 |
| `changed-lines.diff` vs `git diff HEAD -- C06 C16` | 归一化后**完全相同**（11 674 字符） |
| 其余 16 项抽查（C01b/C07/C14/C15/C17 实算） | `3c9f5af7d74f…`/`3fdb44e49afe…`/`05056cbf65f9…`/`d8c0a3bcfc21…`/`aefa0fa5b17e…`，均等于各自冻结记录 pin 与 `other-16-pins.txt` |

---

## A. diff 最小性 —— **FAIL（P1）**

**文件面 PASS**：`git diff --name-only HEAD` 与 `git diff --name-only HEAD -- doc/contracts doc/plan src apps tools` 都只返回 5 个 `doc/plan` 文件；`git status -uall` 无其他改动，未越界。

**逐行对应：载体 §2 全部落地，但 C-16 §0 与卡 I-3 语义不符（P1）**：

| 载体登记 | 落盘 | 判定 |
|---|---|---|
| §2.A.1 状态行 + 日期行（C-06） | `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md:3-4` | 描述性等价（措辞略异） |
| §2.A.2 §2.2 新增行 | `FEA-C06_SOURCE_AUTH_DRAFT.md:43` | 落地（含 scope 展开器/healthy/facts/零 DB 写/选择规则/typed 失败） |
| §2.A.3 §2.3 新增行 | `FEA-C06_SOURCE_AUTH_DRAFT.md:56` | 落地 |
| §2.A.4 §6 变更记录 | `FEA-C06_SOURCE_AUTH_DRAFT.md:96` | 落地（注意卡 I-2 误写 §5，见 P3-1） |
| §2.B.1 状态行 + 日期行（C-16） | `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:3-4` | 描述性等价 |
| §2.B.2 §0 wire 行 → 1.2 + 能力 `source.read.run/1` | `FEA-C16_SOURCE_READ_WIRE_DRAFT.md:17,22` | 落地；wire 行与能力行均与载体一致 |
| §2.B.3 新增 §2.4 | `FEA-C16_SOURCE_READ_WIRE_DRAFT.md:73-90` | 落地 |
| §2.B.4 §10 条件 ⑤ + 变更记录 | `FEA-C16_SOURCE_READ_WIRE_DRAFT.md:224,231` | 落地 |

**未登记的语义差异（P1）**：卡 I-3 第 2 条（`doc/tasks/FEA-11-RUN-GRANT-1-PREREQ-1.md:81`）登记「缺失 → `CORE_CAPABILITY_MISSING`；按操作检查」，D-4（同卡 `:59`）登记「Host 缺失 → `CORE_CAPABILITY_MISSING`，不铸 grant、不 dispatch」；而落盘 `FEA-C16_SOURCE_READ_WIRE_DRAFT.md:22` 是「缺失 → **不铸造、不绑定**，按现状 dispatch（旧 Core 行为不变；referenced Run 仍 typed 失败）」。这不是描述性差异，而是**行为差异**（是否拒绝 Run、以何码失败）。
其余 diff 块（冻结记录 3 块、矩阵 3 块）均属载体 §2.C / 卡 I-4 登记范围；矩阵第 16 行标签实测为 `wire v1.3`（不是 v1.1），无版本错位。

MATRIX 之外无其他未登记改动。

---

## B. 不变量零改动 —— **PASS**

diff 块边界（`changed-lines.diff` 原文 hunk 头）：C-06 仅 `@@ -1,7 +1,7 @@`、`@@ -40,6 +40,7 @@`、`@@ -52,6 +53,7 @@`、`@@ -91,3 +93,4 @@`；C-16 仅 `@@ -1,7 +1,7 @@`、`@@ -14,11 +14,12 @@`、`@@ -69,6 +70,25 @@`、`@@ -201,10 +221,11 @@`。逐项：

| 不变量 | 证据 | 结论 |
|---|---|---|
| source-read grant 四维 scope 形状 | C-06:39 grant 字段行未动；C-16:51-60 四维 scope 示例未动（无对应 hunk） | 零改动 |
| `≤300s` TTL | C-06:40 未动；C-16 §2.4:75、:88 明写「不延长」 | 零改动 |
| 撤销/失联语义 | C-06:42、C-16:23/:204 未动；§2.4 明写「不改变」 | 零改动 |
| C-16 §6 错误闭集（新增码？） | C-16:171-192 未动；§2.4 引用的 `SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_EXPIRED`/`SOURCE_GRANT_REVOKED` 均在 §6 表；`HOST_ONLY_REQUIRED`/`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH` 为 M2-C1 §5.7 既有码（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:541,552-554`），`INVALID_REQUEST` 亦为既有码 | **无新增码** |
| C-16 §7 脱敏规则 | C-16:196-205 未动；§2.4 仅引用「脱敏沿用 §7」 | 零改动 |
| §3.1 fresh-grant/密码通道 | C-16:102-128 未动（无 hunk） | 零改动 |
| `RegisterSourceReadGrant` 字节/语义 | C-16:37-71 主体未动（新增只在 72 行处插入） | 零改动 |
| `RevokeSourceReadGrant` 字节/语义 | C-06:55、C-16:23、C-16:204 未动 | 零改动 |

结论：新增内容是**追加式**的（新行/新节/新能力/冻结条件 ⑤），既有条款字节未被改写。

---

## C. 未越界 —— **PASS**

- `git diff --name-only HEAD -- doc/contracts doc/plan src apps tools` 只列 5 个 `doc/plan` 文件；`doc/contracts`、`src`、`apps`、`tools` **0 文件**。
- `CORE_PROTOCOL_MINOR=3` 所在 `src/` 零 diff；`schema.py` 零 diff；依赖文件（`pyproject`/`package.json`/lock 等）零 diff（`git status -uall` 仅上述 11 项）。
- M2-C1（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`）、C-07/C-08（`doc/plan`）、C-15/C-17（`doc/plan`）、ADJ-001（`doc/contracts`）均零 diff；C-15/C-17 另以 sha256 抽查（见 §D）。
- Run 命令请求/响应字节：`core_service.py:5862-5923` 零 diff（`src` 零改动）；`docs/plan` 中无其它 Run wire 文件改动。
- 载体对现状的引用经回源核对成立：host-control 闭集无授权建立命令（`src/bootstrap/core_service.py:355-364`）、Run 命令面不带 grant（`:5867-5923`）、`_bindings` 写入口仅 import（`src/application/importing/referenced/runtime.py:567-569`）与 sync apply（`src/application/sources/service.py:287,295-323`）、typed 失败点（`src/bootstrap/core_assembly.py:1773-1775`、`src/infrastructure/sqlite/pipeline.py:897-899`）。

---

## D. pin 可复算 —— **PASS**

- C-06 工作树 sha256 = `1e5e6927376d0eacb82ed479e84c891e02512c920a5b8cf6e29d78e063ad350f` = `FEA-CONTRACT-FROZEN-C06.md:16,18` 的 pin；C-16 工作树 sha256 = `274b031cdebf26ab228d747a399c13a343f4a38ed4b143660a140e27d255cb19` = `FEA-CONTRACT-FROZEN-C16.md:16,18` 的 pin。
- `git hash-object` 两值（`3524b6be…`/`7d277439…`）分别等于两份冻结记录 `:17` 的 blob id。
- `verify_pins.ps1` 实测 **18/18 PASS**；C06 打印 `1e5e6927376d`、C16 打印 `274b031cdebf`，其余 16 项与 `logs/pins.log` 逐行一致。
- 其余 16 项：`other-16-pins.txt` 全部 `prev=actual`、`changed=0`；抽查 5 项实算值（C01b `3c9f5af7d74f28…`、C07 `3fdb44e49afe9f…`、C14 `05056cbf65f9…`、C15 `d8c0a3bcfc21…`、C17 `aefa0fa5b17e…`）与各自冻结记录 pin 一致；16 个文件相对 HEAD 均零 diff（`git diff --name-only HEAD -- doc/plan` 不含它们）。
- `pre-post.sha256` 的 pre 值（`8faa8cd1…`/`0b9511a5…`）实测等于 HEAD 原始字节 sha256，也等于两份冻结记录保留的 v1.1 pin。

---

## E. 冻结记录/矩阵一致性 —— **PASS（含 P2-3 / P3-5）**

- 版本面自洽：C-06 `FROZEN v1.2`（`FEA-C06:3`、`FROZEN-C06:15`、矩阵第 6 行 `:24`、载体 `:22-25`）；C-16 `FROZEN v1.3`（`FEA-C16:3`、`FROZEN-C16:15`、矩阵第 16 行 `:37`、载体 `:29-32`）。
- 历史 pin 保留：C-06 v1.0 `b798dd8a…`（`FROZEN-C06:33`）、v1.1 `8faa8cd1…`（`:37`）；C-16 v1.0 `6e7f8d3d…`（`FROZEN-C16:72,84`）、v1.1 `0b9511a5…`（`:35`）。
- §1A/§1B 口径：C-16 §1A（`:22-25`）未改；C-16 §1B 新增历史/复核行（`:35-36`）；C-06 无 §1A（沿用旧结构），§1B（`:22-38`）新增 v1.2 复核/复核字节/冻结字节与历史行。
- 「复核后改状态行」字节差异：**不存在**。冻结记录声明复核字节 = 冻结字节 = 工作树（`FROZEN-C06:35-36`、`FROZEN-C16:36`），实测 sha 相等（§D）——本报告复核的正是含 `FROZEN v1.2/v1.3` 状态行的最终字节。
- 冻结条件/变更记录：C-16 §10 追加条件 ⑤ 与 v1.3 变更行（`FEA-C16:224,231`）；C-06 以新增 §6 承载 v1.2 重冻（`FROZEN-C06:70-80`），与 C-16 的 §6/§7 分节先例一致。
- **P2-3**：两份冻结记录与 C-16 §2 条件 5 已把「独立复核 approved / P0=0、P1=0」写成既成事实（`FROZEN-C06:77`、`FROZEN-C16:46,82`），而载体 §6 仍是 `pending`（载体 `:59-62`）。本报告判 P1 ⇒ 提交前必须按实际结论回填/改写。
- **P3-5**：两份冻结记录头部「冻结时间」未随版本更新（`FROZEN-C06:4` 仍 `2026-11-01`；`FROZEN-C16:4` 仍 `2026-11-03（v1.0）/2026-11-04（v1.1）`）；C-06 §1B 的 v1.1 pin 在 `:32` 与 `:37` 重复出现（无害冗余）。

---

## F. 命令规格自洽性 —— **FAIL（P2，非阻断）**

**通过项**：

- 请求/响应形状与 Run 自身字段域一致：`command`/`scope` 与 `StartRun`/`PrepareRun` 的 payload 同域（`src/bootstrap/core_service.py:5871,5908`），scope 解析器即 Run 用的 `_parse_run_scope`（`:5724-5753`，closed-shape、未知/越域 → `INVALID_REQUEST`）；`grant_ids` 1..64/去重/非空。
- 校验顺序（host-only → shape → grant live/expiry/revoked → scope 展开）单调、无跳步；`refused` 原子性（非空即零映射写入、`bound_pages=0`）与 C-16 `:88` 一致；写入映射 `grant_id → {source_id, version_id, entry_ids}` 与 `bind_imported_entry` 同构（`src/infrastructure/resource_channel/source_read_refs.py:411-440`）；读时选择规则与 `find_bound_for_source` 一致（`:442-474`，max by `(generation, grant_id)`）。
- per-page 匹配使用 `entry_key`/`locator`/`ordinal`（`FEA-C16:87`），与既有 `claim_secret_for_binding` 的三选一先例一致（`source_read_refs.py:345-347`），并以 `source_entries`/`source_locations` 逐项核对（C-15 `:115-141` 确有 `locator`/`ordinal`；`page_bindings` 确有 `source_id`/`entry_id`/`accepted_source_version`/`status`，C-15 `:146-167`），无路径回退。
- 零 DB 写/不建 plan-apply-journal/不发布资源/不延长 TTL/幂等；错误码复用、`details` 仅计数/ID；脱敏沿用 §7；不改 Run wire/`PROTOCOL_MINOR`/schema/依赖（`FEA-C16:88-90`）。
- 「旧 Core 能力缺失 → 不铸不绑、按现状 dispatch」在**契约与载体**中明确（`FEA-C16:22,90`；载体 `:42`）。

**不一致项**：

- **P2-1**：C-06 §2.3 新行写「任一目标页不可授权 → **整体 typed 失败**且零绑定写入」（`FEA-C06:56`），而 C-16 §2.4 与卡 I-3 的失败形态是**正常响应** `{bound_pages:0, refused:[{page_id, code}]}`（`FEA-C16:85,88`；卡 `:87`）。「typed 失败」若指错误 envelope，则两契约对同一情形的 wire 形态不一致。
- **P2-2**：C-06 §2.2 写「按签名 grant 的 `source_id/version/entry(...)` 与 **facts** 校验当前 healthy binding」（`FEA-C06:43`），载体 §2.A.2 亦写「四维 scope/facts」（载体 `:23`）；但 C-16 §2.4 的 per-page 匹配只列 scope 三维 + healthy + publication gate，**未包含 facts/identity 校验**（`FEA-C16:87`）。实现口径不明（是否打开源文件核对 volume serial/file id）。
- **P2-5**：§2.4 的 publication gate 仅以「非 open（C-17 §3.3）」引用（`FEA-C16:87`），未写明「无 publication 行」的两种情形（legacy v7 binding 沿旧规则放行 / 新同步 binding 缺行视为损坏 fail-closed）。Core 现有两个 gate 谓词本就不一致：`core_assembly.read_gate` 对无行返回 `open`（`src/bootstrap/core_assembly.py:1244-1261`），`core_service._assert_source_sync_gate` 在前驱有 gate 时抛 `SOURCE_ACCESS_DENIED`（`src/bootstrap/core_service.py:5072-5103`，即 L-R11）。新命令须冻结复用哪一个谓词。
- **P3-2**：§2.4 被插在 §2 `RegisterSourceReadGrant` 标题之下（C-16 `:37` 与 `:73`），而 §2 没有 2.1–2.3，新命令在结构上成了 register 的子节。
- **P3-3**：「错误码：复用 §6 闭集，不新增」（`FEA-C16:89`）措辞不精确：校验顺序里三个 envelope 码来自 M2-C1 §5.7，不在 C-16 §6 表内；但**确无新增码**（B 仍 PASS）。
- **P3-7**：`command` 取值域未限定到「带 scope 的 Run 起始命令」（StartRun/PrepareRun/AcceptRun）；`ControlRun`/`ResumeBlockedRun`/`RetryFailedTargets` 的 payload 只有 `run_id`/`action` 等、无 `scope` 字段（`core_service.py:5862-5931`），「与对应 Run 命令同一取值域」对这三条命令不成立。
- **P3-8**：C-06 §2.3 版本句仍写「本组命令 v1.1」（`FEA-C06:58`）、§5 条件 4 仍写「v1.1 minor 增量」（`FEA-C06:87`），与 C-16 §0 的 `source-access-wire/1.2`（`FEA-C16:17`）及新行「v1.2 新增」（`:56`）口径不一致；矩阵第 6 行却写「wire v1.2 additive DSH 批准 ✅」（矩阵 `:24`）。

---

## G. 证据真实性 —— **PASS（含 P3-4）**

- `pre-post.sha256`：pre 值 = HEAD 原始字节 sha256（`8faa8cd1…`/`0b9511a5…`），post 值 = 工作树 sha256，四项与 §D 实测完全一致。
- `changed-lines.diff`：与 `git diff HEAD -- C06 C16` 归一化后**逐字节相同**（11 674 字符），非手写摘要。
- `logs/pins.log`：重跑 `verify_pins.ps1` 输出与日志 19 行逐行一致（含 `PIN AUDIT: PASS (all 18)`）。
- `logs/check.log`：重跑 `check.ps1`（默认与 `-TaskPath`）输出逐行一致（`PASS (3 warnings)`，3 条 warning 与日志同文）。
- `other-16-pins.txt`：16 项 `prev=actual`；抽查 5 项实算与冻结记录 pin 相符（§D），非伪造。
- **P3-4**：卡 I-5 列明证据含 `carrier.md`（卡 `:103`），目录中**不存在**；其余 5 项齐全。载体本身在 `doc/reviews/`，本报告承担复核结论，故不构成信息缺口，但与卡面登记不符。

---

## H. 不夸大 / limitation 保留 —— **FAIL（P2）**

**不夸大 PASS**：载体开篇即写「生产 referenced 页 Run 仍不可端到端（L-R1）」（载体 `:10`），§4 回退与风险、§3 兼容均写「referenced Run 仍 typed 失败」（载体 `:42,49-50`）；卡面「本卡只交付契约字节与冻结证据：不构成实现授权，不构成『referenced Run 产品可用』」（卡 `:44`）、L-P3 `:136`。未发现把「契约就绪」写成「实现/产品可用」。

**limitation 保留不完整（P2-4）**：
- 卡 L-P2 保留了 L-G1/L-G2/L-G9（卡 `:135`）；载体 §4 只保留 L-G1/L-G9（载体 `:49`），**漏 L-G2**（加密 referenced Run）。
- 载体与卡**均未登记 L-R11 / L-G10**（两读面 publication gate 不一致，scope review `:377` 判「另立 follow-up」）。而新 §2.4 直接引用 publication gate（`FEA-C16:87`），与该不一致相邻；RUN-GRANT-1 落地时必须保留该 follow-up 口径（见 P2-5）。

---

## Findings

| ID | 严重度 | 事实（path:line） | 最小修复 |
|---|---|---|---|
| R1-P1-1 | **P1** | 卡 D-4（`doc/tasks/FEA-11-RUN-GRANT-1-PREREQ-1.md:59`）、I-3（`:81`）写「缺失 → `CORE_CAPABILITY_MISSING`，不 dispatch」；同卡 §兼容与影响（`:128`）、C-16 §0 落盘（`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:22`）、载体 §3（`:42`）写「不铸/不绑、按现状 dispatch、既有 managed Run 零变化」 | 改卡面（不改契约字节）：D-4/I-3 改为「Host 探测缺失 → 不铸/不绑定，Run 按现状 dispatch；不得以缺能力拒绝 Run，不得用未知命令探测，错误码按现状由 Core typed 失败」。改后窄面复审：卡 diff + 两份契约 sha 不变 + pins 18/18 |
| R1-P2-1 | P2 | C-06 §2.3 新行「整体 typed 失败」（`FEA-C06:56`）vs C-16 §2.4/卡 I-3 的 `{bound_pages:0, refused[]}` 响应（`FEA-C16:85,88`；卡 `:87`） | C-06 该行改为「整体拒绝（refused[] 逐页报告、`bound_pages=0`）」，下轮 UNFREEZE 或本卡登记补正 |
| R1-P2-2 | P2 | C-06 §2.2「与 facts 校验」（`FEA-C06:43`）、载体「四维 scope/facts」（`:23`）vs C-16 §2.4 无 facts/identity 校验（`FEA-C16:87`） | 二选一并在两处统一：或在 §2.4 补「facts 与 `source_locations` 逐项核对、无路径回退」，或从 C-06/载体删去「facts」 |
| R1-P2-3 | P2 | 冻结记录预填复核结论：`FROZEN-C06:77`、`FROZEN-C16:46,82` 写 approved/P0=0/P1=0，而载体 §6 仍 pending（载体 `:59-62`）；本报告判 P1 | 提交前按实际结论回填（若返修后复审 approved 再写 approved；否则改为 pending/实际结论），并让 C-16 §2 条件 5 的 ✅ 与之一致 |
| R1-P2-4 | P2 | 载体 §4 漏 L-G2（载体 `:49` vs 卡 `:135`）；载体与卡均未登记 L-R11/L-G10（scope review `:377`） | 载体 §4 补 L-G2；载体/后续 RUN-GRANT-1 卡登记 L-R11/L-G10 为 follow-up（不阻塞本卡） |
| R1-P2-5 | P2 | C-16 §2.4 publication gate 未写明「无 publication 行」口径（`FEA-C16:87`）；两 gate 谓词本就不一致（`core_assembly.py:1244-1261` vs `core_service.py:5072-5103`，L-R11） | §2.4 增一句「legacy 无行沿 C-17 §3.3 旧规则；新同步缺行 fail-closed」，或由实现卡冻结「复用 Run 面 `read_gate`」并在卡面登记 |
| R1-P3-1 | P3 | 卡 I-2 写「§5 变更记录」（卡 `:76`），C-06 变更记录实为 §6（`FEA-C06:90-96`） | 改卡为 §6（或删除节号） |
| R1-P3-2 | P3 | §2.4 嵌在 §2 `RegisterSourceReadGrant` 之下（`FEA-C16:37,73`），§2 无 2.1–2.3 | 下轮重排为独立命令节（本次不改字节） |
| R1-P3-3 | P3 | 「复用 §6 闭集」（`FEA-C16:89`）不含 `HOST_ONLY_REQUIRED`/`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`（M2-C1 §5.7 `:541,552-554`）；无新增码 | 措辞改为「复用 §6 + M2-C1 §5.7 envelope 既有码，不新增」 |
| R1-P3-4 | P3 | 证据缺卡 I-5 列明的 `carrier.md`（卡 `:103`）；其余 5 项齐全真实 | 补 `carrier.md` 摘要或从卡 I-5/AC-P5 移除该条 |
| R1-P3-5 | P3 | 冻结记录头部冻结时间未随版本更新（`FROZEN-C06:4`、`FROZEN-C16:4`）；C-06 §1B v1.1 pin 重复（`:32`/`:37`） | 下轮记录维护时补 v1.2/v1.3 时间并去重 |
| R1-P3-6 | P3 | 两契约状态行删去上一版复核标注（C-06 原「r7 approved」、C-16 原「r15 + 已提交字节复核 approved」），改为「复核见载体」（`FEA-C06:3`、`FEA-C16:3`）；历史仍保留于 `FROZEN-C06:30`、`FROZEN-C16:69` | 无需改字节；下次状态行更新时保留上版复核指针 |
| R1-P3-7 | P3 | §2.4 `command` 取值域未限定到带 scope 的 Run 起始命令；`ControlRun`/`ResumeBlockedRun`/`RetryFailedTargets` 无 `scope`（`core_service.py:5862-5931`） | §2.4 或实现卡明确允许的 command/scope 来源（Run 快照） |
| R1-P3-8 | P3 | C-06 §2.3 版本句与 §5 条件 4 仍写 v1.1（`FEA-C06:58,87`），与 C-16 `source-access-wire/1.2`（`FEA-C16:17`）及矩阵「wire v1.2」（矩阵 `:24`）不一致 | 下轮 UNFREEZE 补一句 v1.2 版本说明；本次不改已冻结条款字节 |

---

## 最终判定

- **verdict：`changes_requested`**（P0=0、P1=1、P2=5、P3=8）。
- **是否需要返修：是**，但返修面**不涉及两份契约字节**：只改卡面 D-4/I-3（P1）、按实际结论回填冻结记录/载体 §6（P2-3），并酌情处理 P2-1/P2-2/P2-4/P2-5 与 P3（可登记为下轮/后续卡）。
- **不构成**：本报告不批准提交，也不构成实现授权或产品可用性结论。
- **复审口径（建议）**：卡面与载体改动后做窄面复审——①`git diff` 仅含卡/载体/矩阵（若改）；②两份契约 sha256 仍为 `1e5e6927…`/`274b031c…`（未改则无需重算 2/18 pin）；③`verify_pins` 18/18、`check.ps1` PASS；④P1 关闭证据（卡 D-4/I-3 与 C-16 §0 同文）。若返修选择改契约字节，则必须重算 pin、更新冻结记录并重新完整复核。

## 真实性声明

本报告是本次复核中**唯一**写入的文件。复核者未参与 C-06 v1.2 / C-16 v1.3 的起草或任何前轮复核；未修改被审字节、证据、卡、冻结记录或矩阵；未执行 `git add`/`commit`/`push`；未删除或移动任何文件。所有 pin/sha256/门禁结论均由本轮命令在 `reviewed_head=b17d7282193afa6583c6c7a7bfc6456d04313af5` 的工作树字节上实测得出，未采信载体的自述结论。
