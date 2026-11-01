---
document_id: FEA-GATE-READINESS
kind: independent_review
task_id: task-30（Gate 关闭前完整覆盖面 + 跨契约一致性）
round: 1
scope: 两个 Gate 关闭前的完整覆盖面 + 跨契约一致性 + Gate 记账 + C-09 就绪
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-30"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: e35f37603
reviewed_head_full: e35f37603faf728d16eaec5b0cb148d1695ffd1c
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == e35f37603）"
reviewed_documents:
  - 12 份 doc/plan/FEA-CONTRACT-FROZEN-*.md 与对应契约草案（C-01b/C-02/C-03/C-04b/C-05/C-06/C-07/C-08/C-11/C-12/C-13/C-14）
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md、doc/plan/FEA-01_CONTRACT_DRAFT.md、doc/plan/FEA-CONTRACT_FREEZE_PACKAGE.md
  - doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md §9、doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md §5
  - doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md
  - doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md §13.2 `:767`–`:770`（D04–D07 必须冻结的内容）
  - doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md §5.5/§7（Run 与控制/断线语义）、doc/reviews/FEA-GOV-7-r2.md（C-09 复核）
baseline: "verify_pins.ps1 PASS (all 12)；check.ps1 PASS (3 warnings)；12/12 记录 pin 与当前 blob 一致；12/12 记录含 §1B"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 4
p2_count: 3
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
verifypins: "PASS (all 12)，EXIT=0，本次实跑；C14 OK"
captured_at: 2026-11-01T10:30:00+08:00
captured_by: c01b-reviewer
---

# 独立复核：两个 Gate 关闭前的完整覆盖面 + 跨契约一致性

**本报告不是** Gate 关闭裁定、不是冻结动作、不释放任何 Task。

## 1. 结论（先说结论）

**verdict：`changes_requested`（P0 × 0 / **P1 × 4** / P2 × 3）。**

**两个 Gate 的契约侧判定：**

| Gate | 契约侧判定 | 依据 |
|---|---|---|
| **`G-CONTRACT`**（D05 Source/grant/资源契约冻结） | **✅ 满足**（附 1 条记账注记） | D05 五项全部有冻结承载：①持久身份与授权分离=C-06；②scope/version/lease=C-06 grant scope + C-01b SC-25/29/31；③重定位/同步=C-14 SC-S01…S08（引用 C-01b SC-26/27/34）；④容器页映射=C-14 SC-S09…S13；⑤缓存边界/资源上限=C-06 `:64` per-request + C-01b SC-02/03/20 + **C-14 SC-S14/15/16**（淘汰/持久化/全局上限）。§0.1 四条「已承载」逐行实核为真。**注记**：AD-003 `:117` 承诺的四张表 DDL 仍未冻结（C-14 L-1），关闭裁定须明示其承载计划。 |
| **`G-DELETE-CONTRACT`**（协议字段/码表/**D04-D07 冻结**） | **❌ 不满足** | D04 ✓、D05 ✓，但 **D06 有 4 项声明范围未写入任何冻结契约**、**D07 有多项未冻结且承载契约 C-09 自身未冻并与 Gate 互相等待（循环）**。详见 §2/§3。 |

**结论**：现在只能裁定 `G-CONTRACT`；`G-DELETE-CONTRACT` **不能关闭**——按现在的事实，它在 D06 与 D07 上都不闭合，且 D07 存在**结构性循环**（见 P1-2）。

---

## 2. 两个 Gate 的逐条判定（带证据）

### 2.1 `G-CONTRACT`（D05）—— **满足**（5/5，附记账注记）

| # | D05「必须冻结」（方案 `:768`） | 冻结承载 | 判定 |
|---|---|---|---|
| 1 | 持久身份与授权分离 | C-06（`identityFacts` + `grant`，`:39`/`:51`） | ✅ |
| 2 | scope / version / lease | C-06 grant `scope`（`:39`/`:52`）+ C-01b SC-25/29/31（lease） | ✅ |
| 3 | 重定位 / 同步 | C-14 SC-S01…S08；引用 C-01b SC-26/27/34（不复写），补 relink/repoint 区分、范围选择、sync plan 字段、可执行判据 | ✅ |
| 4 | 容器页映射 | C-14 SC-S09…S13（locator≠身份、Page 绑定、稳定排序键、健康判定、原文件缺失） | ✅ |
| 5 | 缓存边界 / 资源上限 | 已承载：C-06 `:64` 第 7 条 per-request 预算、C-01b SC-02（可再生产物+cache key）/SC-03（非缓存边界）/SC-20+C-06 `:65`（两通道隔离）；**缺口补齐**：C-14 SC-S14（淘汰：LRU、大文件先清、引用计数跳过、preflight 期间不淘汰）、SC-S15（持久化：可全量丢弃重建、受管根内、崩溃后校验）、SC-S16（全局上限：总字节+并发解码数、配置项但「必须有上限」为契约条款）、SC-S17（通道隔离边界） | ✅ |

**记账注记（不阻断）**：AD-003 `:117` 写「`source_entries`/`page_bindings`/`source_sync_plans`/`source_operations` 的表名、索引、外键、约束与迁移版本**均未定，由 DSH 在 D05 范围冻结**」；C-14 把这些 DDL 留给「后续存储契约」并登记为 **L-1 已知限制**（`FEA-CONTRACT-FROZEN-C14.md:64`）。→ 关闭 `G-CONTRACT` 的裁定时应显式写明「D05 五项不含 DDL；DDL 由后续存储契约承载」，否则 AD-003 `:117` 的承诺无着落。

### 2.2 `G-DELETE-CONTRACT`（D04–D07）—— **不满足**

| 包 | 声明范围（方案/FEA-01） | 冻结承载 | 判定 |
|---|---|---|---|
| **D04** 草稿/保护/结果 | 方案 `:767` 六项：edit token/journal、Draft/Protection 版本、candidate-only prepare、统一事务 live apply、锁定样式白名单、旧非幂等写兼容 | C-13 §3 六项逐条映射（SC-D04/D05、SC-D01/D12、SC-D06/D07、SC-D08、SC-D09/D10、SC-D11） | ✅ 满足 |
| **D05** Source/grant/资源 | 五项 | C-06 + C-14 + C-01b（见 2.1） | ✅ 满足 |
| **D06** Run 快照 | FEA-01 C-08 `:57` 六项：preview 与发送同源；不可变内容 pin；**retry 是否复用 source run 快照**；**控制 pending 状态**；**真实完成口径**；**断线 receipt** | C-08 SC-R01（preview 同源 ✓）、SC-R02（不可变 pin ✓）、SC-R03/R04/R05；**其余三项无条款**；M2-C1 §5.5（冻结）含 `ControlRun` 与状态迁移表，可**部分**承接「控制 pending 状态」；`RetryFailedTargets`（M2-C1 `:206`）部分承接 retry 区分 | **❌ 不满足**（见 P1-1） |
| **D07** 删除/备份/迁移 | FEA-01 C-09 `:58` 七项：软删/恢复/TrashEntry 新命令面；三路径统一 ProtectionPolicy；备份覆盖清单（`settings/*.json`、`catalog.sqlite` 现状缺失项）；`backup/2`；`DatabaseId`；自动备份调度归属；独占写锁与 pin | 冻结覆盖：M2-C1 §5.11 字段/码表（C-04b）、`DatabaseId`（C-01b SC-18）、独占维护锁（SC-17）、备份一致性/清单部分（SC-10a/10b/12/13）、格式 Gate（SC-38）；**其余**只在 **C-09 草案（未冻结）**，且 C-09 草案本身也**没写** `backup/2`、旧包 adapter、自动备份调度归属 | **❌ 不满足**（见 P1-2） |

---

## 3. D04–D07 覆盖表（要求 → 承载 → 判定）

见上表。补充证据位置：

- **D04**：`FEA-C13_DRAFT_PROTECTION_DRAFT.md` §3 六项映射表（`:150` 起六行）；SC-D01…SC-D12 实体条款在 §2/§4/§5。
- **D05**：`FEA-C14_SOURCE_RELOCATION_DRAFT.md` §0 矩阵五 + §0.1 四条 + §1–§3 十七条；`FEA-C06_SOURCE_AUTH_DRAFT.md:39/51/52/64/65`；`FEA-C01b_STORAGE_CONTRACT_DRAFT.md:84/85/86/88/95/98`。
- **D06**：`FEA-C08_RUN_SNAPSHOT_DRAFT.md` SC-R01 `:39`–SC-R05 `:61`；FEA-01 C-08 行 `:57` 为声明范围；M2-C1 §5.5 `:185`–`:226`（冻结，含状态迁移表 `:212`–`:216`）、`:200`（同键重放）、`:206`（RetryFailedTargets）、§7.2 `:1087`–`:1093`（**Proposed，非冻结**）。
- **D07**：`FEA-C01b_STORAGE_CONTRACT_DRAFT.md:66`（SC-17）/`:67`（SC-18）/`:53`–`:57`（SC-10a/10b/12/13）/`:107`（SC-38）；`FEA-C04b_DELETE_PROTOCOL_DRAFT.md`（M2-C1 §5.11 字段与码表）；`FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md` SC-B01…SC-B05（**草案，未冻结**）。

---

## 4. Findings

### P1

**P1-1 — D06 有 4 项声明范围未写入任何冻结契约**
- 位置：`FEA-01_CONTRACT_DRAFT.md:57`（C-08 声明范围）；`FEA-C08_RUN_SNAPSHOT_DRAFT.md`（冻结，22 条 SC-R01…R05 只覆盖 3 项）。
- 事实：
  - **控制 pending 状态**：C-08 无条款（全文 `pending` 仅出现在与 C-05 的接口行 `:69`）；M2-C1 §5.5 有 `ControlRun` + 状态迁移表（`:212`–`:216`）可**部分**承接，但 C-08 未引用/映射它，冻结记录 `FEA-CONTRACT-FROZEN-C08.md:54` 却声称「**D06 现在有承载契约** → `G-DELETE-CONTRACT` 的 D06 覆盖完成」——**该声明不成立**。
  - **真实完成口径**：12 份契约 + M2-C1 检索「完成口径/真实完成」0 命中；仅有 `M2-C1:137`「同步响应表示接受，不表示长任务完成」与 `:902`/`:1060`「事件不是状态真值」两条相邻语义，**无独立条款**。
  - **retry 是否复用 source run 快照**：C-08 SC-R02 只说「更新快照=新 Run（`source_run_id`）」，未回答「retry 是否复用源 Run 的快照」；M2-C1 `:206` 只说新 Run 冻结失败页——**部分**。
  - **断线 receipt**：全部契约 0 命中「receipt」用于 Run 断线（仅 C-01b SC-34 的删除 operation receipt）；M2-C1 §7.2 是 **Proposed（非冻结）**，`:1091`「重连后重读 Core 状态、不自动重放」不是 receipt 语义。
- 影响：`G-DELETE-CONTRACT` 的 D06 条件不满足；C-08 冻结记录 §5 的 D06 覆盖声明需更正。
- 要求：补 C-08 条款（或明确「由 M2-C1 §5.5/§7 冻结面承载」并写出映射，尤其「真实完成口径」「断线 receipt」无任何承载）；然后重开（或补）独立复核。

**P1-2 — D07 多项未冻结 + C-09↔Gate 循环（决定性缺口）**
- 位置：`FEA-01_CONTRACT_DRAFT.md:58`（C-09 声明范围）；`FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md`（草案，`§4` 条件③）；`FEA-CONTRACT_FROZEN-C04b.md:35`（「本单只承载 D07」）。
- 事实：
  - **冻结**只覆盖：M2-C1 §5.11 字段/码表（C-04b）、`DatabaseId`（C-01b SC-18）、独占维护锁（SC-17）、备份一致性/清单部分（SC-10a/10b/12/13）、格式 Gate（SC-38）。
  - **未冻结**：`三路径统一 ProtectionPolicy`（C-09 SC-B04 只列三层边界，无统一策略条款）；`备份覆盖清单（含 settings/*.json、catalog.sqlite 归属）`（C-01b SC-10b 仅注明「未入包」；C-09 SC-B01 定义但未冻）；`backup/2`（全仓仅方案 `:520` 有，**任何契约均无**）；`旧包 legacy adapter`（同上，仅方案 `:520`）；`自动备份调度归属`（无）；`软删/恢复/TrashEntry 新命令面`（M2-C1 rev 2.11 只冻回收站读，软删/恢复命令面未冻）。
  - **循环**：`G-DELETE-CONTRACT` 要求 D04–D07 冻结；D07 的剩余项承载 = C-09；C-09 冻结条件③ = 「`G-DELETE-CONTRACT` 关闭 + `G-CONTRACT` 关闭」→ **Gate 等 C-09，C-09 等 Gate**，按现文本无法闭合（用户此前对 C-14 明示过的同类循环风险在此出现）。
  - 旁证：方案 `:901` 自己写「`catalog/catalog.sqlite` 归属**待 D07 冻结**」——即该项确实未决，不能算已承载。
- 要求：先解环——三种可行方向（择一并在留痕中写明）：① 将 C-09 的 §4 条件③改为「G-CONTRACT 关闭 + G-DELETE-CONTRACT 的 D04/D05/D06 部分关闭」等可满足形式，先冻 C-09；② 把 `backup/2`/`旧包`/`调度归属`/`catalog 归属` 拆成独立小契约先冻；③ 在 Gate 定义中明确「D07 的备份/迁移面由 C-09 承载，Gate 关闭以 C-09 冻结回归为后置条件」并据此修正 ADJ-001 §9 与矩阵。**在解环前，`G-DELETE-CONTRACT` 不能关闭。**

**P1-3 — 冻结契约 C-03/C-06 在冻结后被改（未走 UNFREEZE），且新字节无独立复核；记录有模板残留**
- 位置：提交 `a111b0873`（`git diff a111b0873^ a111b0873 -- doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md`）；记录 `FEA-CONTRACT-FROZEN-C03.md:74`/`:85`、`FEA-CONTRACT-FROZEN-C06.md:25`。
- 事实：
  - C-03 `:49` 冻结后改写命名映射（删「浮层→decorative」，改为「浮层无对应专类，归属待 FEA-04b 判定，不得默认 decorative」）；C-06 `:80` 冻结后改写条件③（「缓存预算自含」→「只含 per-request 解码预算；D05 缓存边界仍由 C-01b/C-09 分担」）。
  - 两份记录 `§1B` 处置写「**已补复核**（FEA-CONTRACT-BYTES-r1…）」——但该报告复核的是**冻结前→冻结**的差异，**不覆盖这次冻结后的新字节**；记录 `§1A` 有「冻结后措辞限定（提交 a111b0873）」一句，但**没有 UNFREEZE 载体**（全仓仅 `doc/handoffs/TASK-057-unfreeze.md` 历史文件，与本次无关），与各记录 §1「冻结语义：条款字节自本记录起不得改动；修订须走 UNFREEZE」冲突。
  - 记录文本有**模板残留**：C-03 `:74`/`:85` 出现字面量 `$($pair.src)` 与 `` `n`n ``（PowerShell 插值未生效），且同一段落在 §1A 中重复两次。
  - 我核了这两处编辑的语义：方向与我在 `FEA-CONTRACT-BYTES-r1` 的 P2 建议一致、属收窄性限定 ✓（内容本身无问题）。
- 影响：冻结字节完整性（项目核心纪律）被破坏；Gate 关闭若基于「12 份冻结契约」，这两份的「冻结」在形式上不成立。
- 要求：① 补写 `doc/reviews/CONTRACT-UNFREEZE-2026-11-01.md`（或等价载体）记录两处编辑 + 由独立复核确认（本报告可作为该次复核的证据）；② 或回退两处编辑后重新冻结；③ 修正记录中的 `$($pair.src)` / `` `n`n `` 残留与重复段落。

**P1-4 — 冻结矩阵/覆盖声明与事实不符（Gate 依据失真）**
- 位置：`FEA-CONTRACT_FREEZE_MATRIX.md:10`（「D04/D05/D06/D07 均有冻结契约 → 两 Gate 的契约侧条件已满足」）、`:25`（C-08 行「approved r2」）与 `:30`（C-08 第二行「FROZEN」**重复行**）、`:21`（C-04b 行仍写「5 项全未满足」）、`:23`（C-06 行仍写「`G-CONTRACT: OPEN`」）、`:3`（表头仍 `DRAFT / 待复核`）、`:30`（C-14 行条件「③02 裁决」疑似残留）。
- 事实：matrix 的「契约侧条件已满足」对 `G-DELETE-CONTRACT` **不成立**（见 P1-1/P1-2）；C-08 出现两行；多行「阻塞项」列与实际 FROZEN 状态矛盾。
- 影响：Gate 记账的直接依据之一自相矛盾；用户按矩阵核账会被误导。
- 要求：修正矩阵（去重、更新阻塞项与状态、更正覆盖声明），并据此写 Gate 裁定。

### P2

1. **P2-1（`G-CONTRACT` 记账更新）**：`ADJ-001:128` 的 `G-DELETE-CONTRACT` 仍 `OPEN` 且**无理由列**（按本判应写明「D06/D07 未覆盖 + C-09 循环」）；`AD-003:128` 的 `G-CONTRACT` 仍写「未冻结前：…」（D05 已冻，应改为「契约侧已满足，待 DSH 裁定」并保留 DDL 注记）。这两处更新是 DSH 的 Gate 裁定动作，不属于本复核可代行。
2. **P2-2（`FEA-01` 陈旧行）**：FEA-01 是 11 份契约的清单，**没有 C-13/C-14 行**（`FEA-01:47`–`:59` 仅 C-01b…C-12）；而这两个契约正是 D04/D05 的新承载 → 清单与冻结现状不同步（建议补两行或注明「C-13/C-14 见冻结矩阵」）。
3. **P2-3（C-14 §4 遗留）**：C-14 冻结版 §4 C-04b 行已改为「需求声明 + 字节修订属 UNFREEZE/独立 Task」✓；但 `FEA-CONTRACT-FROZEN-C14.md:52` 写「Gate 皇关闭」错别字（应为「皇→仍」或「Gate 仍关闭需 DSH 裁定」），建议顺手修。

---

## 5. 矛盾清单（跨 12 份契约）

**结论：未发现会阻断 Gate 的「直接矛盾」。** 逐对实核：

| 对 | 检查点 | 结果 |
|---|---|---|
| C-01b ↔ C-13 | regions/三锁/`page_bindings` 语义 | **无矛盾**：C-13 的 `RegionCandidate`/三锁/`protectionDigest` 与 C-01b 的 SC-26/27/30/33 不重叠；C-13 §7 明确「C-01b 的三锁是保护语义、任何写入路径必须检查」（`:122`） |
| C-01b ↔ C-14 | 缓存（SC-02/03/20）、同步（SC-26/27/34） | **无矛盾**：C-14 §0/§4/§1 SCs 均「引用不复写」；C-14 SC-S14/15/17 只引用 SC-02/03 范围与 SC-20 通道 |
| C-06 ↔ C-14 | `scope.entry` vs `EntryId` | **无矛盾但未闭合**：C-14 §4 已改为「对齐规则须在 C-06 侧或协议实现 Task 确认」✓（`FEA-C14:197`）；登记为 L-3 |
| C-04b ↔ C-14 | preflight pending | **无矛盾**：C-14 SC-S08 已改为「需求声明；字节修订属 C-04b UNFREEZE/M2-C1 §5.11.2 独立 Task」（`FEA-C14:146-148`），并登记 L-2 |
| C-08 ↔ C-13 | `PreparedRun` vs `RegionCandidate` | **无矛盾**：C-13 §4 明确「同名异物，必须区分」（`:100-102`） |
| C-05 ↔ C-13 | `S(p,t)` 与活跃草稿 | **无矛盾**：C-13 `:94`/`:194` 明确「活跃草稿**不进** `S(p,t)`；导出/删除前须 flush 或提示」——这是**显式边界**，不是冲突 |

**但有一处「覆盖矛盾」而非「语义矛盾」**（已列 P1-1）：`FEA-CONTRACT-FROZEN-C08.md:54` 声称 D06 覆盖完成，与 FEA-01 C-08 `:57` 的六项声明范围不符。

---

## 6. C-09 就绪判定

| C-09 条件（`FEA-C09:64-67`） | 状态 | 证据 |
|---|---|---|
| ① 独立复核通过 | **✅** | `FEA-GOV-7-r2.md`（`reviewed_head d29cf3698`，verdict `approved`，P0×0/P1×0/P2×3）复核了 C-09 v2 ✓ |
| ② C-01b 已冻结 | **✅** | `FEA-CONTRACT-FROZEN-C01b.md`，pin `3c9f5af7…` 实核一致 |
| ③ `G-DELETE-CONTRACT` + `G-CONTRACT` 关闭 | **❌** | `G-CONTRACT` 满足但未裁定；`G-DELETE-CONTRACT` **不满足**（D06 缺 4 项、D07 缺项 + 循环） |
| ④ `check.ps1` PASS | **✅** | 本次实跑 PASS（3 warnings）EXIT=0 |
| （另）C-09 自身范围完备性 | **❌ 部分** | 即使解环，C-09 草案对 FEA-01 C-09 `:58` 的 `backup/2`、旧包 adapter、自动备份调度归属、软删/恢复命令面**未写**；需先补条款再冻 |

**判定：C-09 现在不可冻。** 卡点 = 条件③（且存在循环，见 P1-2）+ C-09 自身范围缺口。

---

## 7. 数据安全与治理（本次实跑）

- `check.ps1`：PASS（3 warnings），EXIT=0。
- `verify_pins.ps1`：PASS (all 12)，EXIT=0；12/12 记录 pin 与当前 blob 逐一一致（C-01b `3c9f5af7`、C-02 `bb365ca8`、C-03 `b77e7968`、C-04b `694ce5bc`、C-05 `b34db887`、C-06 `b798dd8a`、C-07 `17c8f701`、C-08 `37586fb2`、C-11 `44f4273f`、C-12 `f4983586`、C-13 `d2cb8de4`、C-14 `05056cbf`）；12/12 记录含 §1B；§1A 抽样准确（C-08/C-13 原 pin 可复现）——**但 C-03/C-06 的 §1A 有模板残留（P1-3）**。
- 未 push（`origin/main..HEAD` = 225）；工作树干净；本轮只读，唯一写入为新建本报告。

---

## 8. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具，`reviewer_kind: subagent`，独立上下文；未参与 12 份契约的起草/冻结、未参与 C-09 起草、未参与 Gate 记账。
- 我出具过 C-01b/C-02/C-03/C-04b/C-05/C-06/C-07/C-08/C-13/C-14 的部分复核报告（如实披露）；本轮按「Gate 条件是否真满足」标准从严核，不因先前批准过任何契约而放宽（P1-1/P1-2/P1-3 均直接影响 Gate 或冻结完整性）。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`。

---

## 9. NOT_RUN

- 未运行程序/pytest；全部为文档、冻结字节、git 历史与脚本输出比对。
- 未核 D01/D02/D03/D08（不在两个 Gate 的契约侧条件内）。
- 未核 C-10（U-03 已裁但未起草，不在本轮范围）。
- 未核 C-07/C-11/C-12 与 D04–D07 的间接接口（它们不属于 Gate 条件，仅确认 pin）。
- 未核各契约的**实现**（代码侧）与 M2-C1 字节修订执行情况——本报告只判「契约冻结面」。
- 未核 C-09 自身条款的语义质量（只判范围缺口与就绪条件）；未核 `doc/tasks/*` 的 AC 与契约映射。

—— 报告结束（`verdict: changes_requested`：`G-CONTRACT` 满足；`G-DELETE-CONTRACT` 不满足，D06 缺 4 项、D07 缺项且与 C-09 循环；另冻结字节完整性 1 项、矩阵/记账失真 1 项）。
