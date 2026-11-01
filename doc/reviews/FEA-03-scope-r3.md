---
document_id: FEA-03-scope-r3
kind: independent_scope_review
reviewer: fea03-scope-reviewer
reviewer_kind: subagent
reviewer_source: "同一独立席位续任（DSH Agent Teams durable teammate `fea03-scope-reviewer`，fresh 独立上下文，由 Team Lead `lead` 派发；未参与 FEA-03 起草、v1–v4 范围冻结或 CONTRACT-UNFREEZE-C13 载体起草）；子任务标识 = teammate target 名 + 本报告 frontmatter"
reviewer_independent: true
reviewed_by_implementer: false
author: dsh
base_commit: f91a7683b
reviewed_head: f91a7683b
reviewed_head_full: f91a7683bcd8d47032097280b6ad3f2e6af5b83c
repository: G:/CODEX/New Manga
scope: "FEA-03 范围冻结 v4 + CONTRACT-UNFREEZE-C13-2026-11-01（C-13 v5→v6）独立复核；只看契约修订与范围冻结，不构成实现验收"
decision: changes_requested
verdict: changes_requested
p0_count: 0
p1_count: 4
p2_count: 12
unfreeze_decision: approved
checkps1: "Governance check: PASS (2 warnings)，EXIT=0"
verifypins: "PIN AUDIT: PASS (all 15)；C13 = 8faf1e805eac"
captured_at: 2026-11-01T23:45:00+08:00
captured_by: fea03-scope-reviewer
---

# Review：FEA-03 范围冻结 v4 + CONTRACT-UNFREEZE-C13（base/reviewed_head = `f91a7683b`）

**总体结论：`changes_requested`（P0 × 0 / P1 × 4 / P2 × 12）。不写 `approved`。**

**A 部分（UNFREEZE）单独结论：`approved`。** C-13 v5→v6 的字节改动仅限声明范围（状态行 + SC-D11 末尾追加修订段），pin `8faf1e805eac…` 与文件实际 sha256 一致，载体合规；保留的 P2-02 是**冻结记录留痕**整改（§1B/§2/§9），不否定修订本身。

**B 部分（范围冻结卡 v4）**：r2 的 P0×1/P1×5 大体处置到位（P0-01 已由 UNFREEZE + Q-11 + AC11/V19 闭环；P1-02/03/04/05 已闭环），但仍引入 4 条 P1：AC11/V19 的“旧→新”期望与 R-APPLY-2/R-APPLY-3 冲突；R-APPLY-3 无法按现文实现（无 base/摘要列、无按 id 取行 API、normalized geometry 需 page extent、且去重须在 batch 事务内）；receipt 单 revisionId/contentDigest 与多 Region apply 不兼容；AC16 在 V1–V24 中没有 V 行。

本报告只审范围冻结与契约修订，不评价实现、不构成实现验收或 Gate 关闭。

判定口径沿用 r1/r2：**P0** = 与冻结契约/授权直接冲突或按现文无法在不越权前提下实现；**P1** = `ready` 前必须补齐的覆盖、自洽性或接口缺口；**P2** = 一致性、精度与证据卫生改进（其中标注“ready 前补齐”的仍须在 r3 处置提交完成）。

---

## 0. 复核对象、方法与环境

**被审 head `f91a7683b`**（parent `dfa70c002`，即 v2 提交；同一 main 线性提交，工作区 clean）。v4 提交共 8 个文档变更：

1. `doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md`（v5→v6，**+3/−1 行，仅 2 个 hunk**）
2. `doc/plan/FEA-CONTRACT-FROZEN-C13.md`（版本/pin/changelog）
3. `doc/reviews/CONTRACT-UNFREEZE-C13-2026-11-01.md`（新增载体，63 行）
4. `doc/tasks/FEA-03.md`（v4 卡，+107/−101 行）
5. `doc/reviews/FEA-03-scope-r2.md`（r2 报告入库，238 行，与本席位上一轮产出一致）
6. `doc/checkpoints/GOAL-PROGRESS-2026-11-01.md`（新增 §3B 裁决/FOLLOW-UP 登记）
7. `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（FEA-03 → v4/r3、C-13 v6）
另：`doc/TASK_LEDGER.md` 未变（FEA-03 仍 `proposed`）

**对照材料（只读）**：C-13 v6 全文；`doc/contracts/V11R_REGION_WRITE_CONTRACT.md:146-150`、`:233`（C073）；C-13 冻结记录 §1/§1A/§1B/§2/§4/§8/§9；`src/application/editing/{ports.py,service.py,region_canvas.py}`；`src/infrastructure/sqlite/{schema.py,regions.py}`；`src/domain/regions/entities.py`；`apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/`；r1/r2 报告。

**环境与只读证据**

- `git rev-parse HEAD` = `f91a7683bcd8d…`；`git status --porcelain` 为空（clean）；复核期间未改任何被审文件。
- `verify_pins.ps1` → `PIN AUDIT: PASS (all 15)`，C13 `OK 8faf1e805eac`；`check.ps1` → `PASS (2 warnings)`。
- `Get-FileHash doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md` = `8FAF1E805EAC500AB20037D8628B8594F8720E455387A85639897F1127AFD45C`，与冻结记录 §1 的 pin 逐字节一致。
- 本机 Python（win32）实测 `msvcrt.locking` 独占锁：同进程第二个 handle 取同一字节锁 → `OSError errno 13`（Permission denied）。这证明 R-JOURNAL-4 的 `.lock` 与 V23 “双实例 fail-closed” 可用同进程两 handle 在测试中模拟。

**未执行**：未运行 `pytest`/`dotnet test`（无实现可测）；未做运行时崩溃/并发/锁实测（无实现）；未逐字节复核 C-04b/C-08/C-05 正文（本卡不改）。范围冻结阶段以 static review 为准。

---

## 1. A 部分：CONTRACT-UNFREEZE-C13 单独复核

### 1.1 字节范围核验

`git diff dfa70c002..f91a7683b -- doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md` 只有 2 个 hunk：

1. **状态行**：`FROZEN v5` → `FROZEN v6 / … / SC-D11 适用范围经 CONTRACT-UNFREEZE-C13-2026-11-01 修订`（`:3`）。
2. **SC-D11 末尾追加修订段**（位于原文“**验证**”行之后、`## 6A` 之前）：

> 本条「统一去重键」的约束范围**限定为新 token 路径**。旧保存路径保持既有 append-only / 非幂等语义（由 V11R C073 承载），本契约**不要求旧路径去重**，也不因本契约引入而改变旧路径行为；新旧路径的统一去重由独立 follow-up Task 在 C073 与本契约协调后实施（本修订不改 SC-D01…SC-D10、SC-D12）。

结论：**改动确实只限于状态行 + SC-D11 追加段，无其它字节/语义变化**；契约文件共 222 行（+2 行）。载体 §2/§3 对改动范围的声明与 diff 一致；旧 pin 在载体 §3 保留（`d2cb8de4…`），新 pin 与冻结记录一致。

### 1.2 追加式修订是否足以消除 r2-P0-01（原条文与修订段并存的歧义）

- 原 SC-D11 的三条明文（“新旧路径不得双写”“无论走新 token 还是旧路径都以去重键判幂等”“token 只防重放，不单独决定去重”）**原文保留**；追加段用“本条「统一去重键」的约束范围限定为新 token 路径”“本契约不要求旧路径去重”明确覆盖了前两条的适用范围，并把跨路径统一去重显式延后为独立 follow-up。
- 该追加段与 V11R C073（旧路径 append-only、非幂等）一致，消除了“同一代码路径被两份冻结契约要求相反行为”的硬冲突；`verify_pins` 的 C13 期望值来自冻结记录，pin 复验通过。
- **残余字面歧义（低，建议 P2-04 以 Errata 处理，不改字节）**：原句“不得双写产生两个 revision”与追加段的“旧路径不要求去重”并存时，新→旧 = 2 revisions 只能从追加段推出；原文“**验证**”行只覆盖“先旧后新”一种顺序（该顺序下无论 stale 拒绝还是 DB 去重命中，都仍是 1 revision）。建议在 C-13 冻结记录 §9 Errata（非契约正文）补一句“修订段与原文冲突时以修订段为准；新→旧 = 2 revisions 属 C073 预期”，避免后续实现复核逐字对照时再判歧义。

**A 部分结论：`approved`。** 修订内容、范围、字节边界与 pin 均符合 C-13 冻结记录 §1 与 §1A 纪律；追加式修订足以消除 r2-P0-01 的契约冲突。唯一未闭合项是冻结记录留痕（见 §5 P2-02），属整改事项，不影响修订有效性。

### 1.3 冻结记录留痕（§1A/§1B 纪律）核验

- §1 版本/pin 已更新为 v6/`8faf1e80…`（`:14-16`），changelog 新增 v6 行（`:104`），引用载体 ✓。
- §1A 纪律 ②“冻结后任何字节改动必须重算 pin 或走 UNFREEZE”：本次走 UNFREEZE + 重算 pin，**符合**；纪律 ③“双口径 sha256”为建议项，本次只记录 worktree sha256，未记录 LF blob sha —— 建议在 §1B 补齐（P2-02）。
- 纪律 ④“冻结提交本身不得含条款编辑——最后处置必须在冻结之前的独立提交完成并经复核”：本次条款编辑、冻结记录更新、载体与 v4 卡在**同一提交** `f91a7683b`，独立复核（本 r3）在提交之后。这与 v5 当时的补救模式（先冻结、后补 FEA-CONTRACT-BYTES-r1 复核并在 §1B 记录“已补复核”）同构，可接受；但必须在本 r3 处置提交中按同样方式把 v6 的复核链补进 §1B/§2，否则记录仍以 v5 的 r4 证据“声称”v6 已复核。
- **§1B 未更新**（`:20-28`）：仍写“最后一次独立复核 r4 approved（FEA-C13-r4）”“复核后到冻结的改动 = v5 的 K-1…K-4…”，未记 v6 的 UNFREEZE 修订与 r3 复核 → 证据链未覆盖 v6 字节。
- **§2 未更新**（`:30-37`）：条件 1“独立复核通过”仍以 r1→r4 approved 为证据，未列 v6 的复核（r3）；作为 v6 冻结记录，条件表的证据指向 v5 复核 → 不完整。
- **§9 Errata 仍称“C-13 草案 pin `d2cb8de4…` 未变”（`:113`）**：该句在 v6 之后已不成立，应由新 Errata 条目（原文保留）说明“v6 经 UNFREEZE 更新 pin 为 `8faf1e80…`，原句为 v5 时快照”。
- **载体 §4/§5 的时序描述与实际提交次序不一致**：载体写“复核通过后，冻结记录更新为 v6 + 新 pin（本记录 §5 落表）”（`:48`/`:51`），但冻结记录/新 pin 已随同一提交落盘；应在载体或 §1B 补一句“记录已预置，r3 通过后确认生效”，消除时序自相矛盾。

→ 归入 **R3-P2-02**（ready 前补齐）。

### 1.4 未声明的字节/语义变化与跨文档波及

- C-13 文件本身：仅 2 个 hunk，无其它改动 ✓。
- 其它 pin：`verify_pins` 15/15 PASS，除 C13 外均未变 ✓。
- **跨冻结文档波及（新发现）**：`doc/plan/FEA-01_CONTRACT_DRAFT.md:85` 的 §2A pin 矩阵仍列 C-13 为 `d2cb8de4dd79`。FEA-01 本身是 **FROZEN v2 且被 pin**（`0370c189…`，`verify_pins` 的 FEA01 项），因此该行现在与 C-13 冻结记录不一致，且不能在本卡写域内直接改（改 FEA-01 字节需 FEA-01 UNFREEZE）。建议在 FEA-01 **冻结记录**（非 pin 文件）加 Errata 说明“§2A 的 pin 前缀为 2026-11-01 冻结时快照，C-13 已于 v6 更新，当前 pin 以各冻结记录/verify_pins 为准”，或在 C-13 冻结记录 §9 记同一事实。→ **R3-P2-03**

---

## 2. r2 findings 逐项 disposition 核验（18 条）

状态口径：**closed** / **partial** / **open**。

| r2 ID | r2 问题（摘要） | v4/UNFREEZE 处置（证据） | 核验结论 | r3 关联 |
|---|---|---|---|---|
| P0-01 | SC-D11 与 C073 冲突、旧路径去重键不可判定 | v6 追加修订段 + Q-11（卡 `:68`）+ AC11/V19 按 v6 重写（`:139`/`:177`）+ R-LEGACY-1/2/3（`:102-104`） | **closed**（契约治理闭环；UNFREEZE approved）；AC11/V19 的“旧→新”期望仍有内部矛盾 | R3-P1-01 |
| P1-01 | receipt 多序列/崩溃窗口/清理 | Q-7 多序列（`:64`、`:84-86`）、R-RECEIPT-3 清理（`:86`）、R-APPLY-3 DB 兜底（`:94`）、AC15/V20/V21（`:143`/`:178-179`） | **partial**：多序列与清理已闭环；receipt 单 revisionId/contentDigest 与多 Region apply 冲突，R-APPLY-3 不可按现文实现 | R3-P1-02 / R3-P1-03 |
| P1-02 | journal 宿主的只读/单写者/原子性 | R-JOURNAL-1…5（`:79-83`）；R-JOURNAL-4 改为 OS 可写性 + `.lock`，不依赖 Host 通道；AC17/V22/V23（`:145`/`:180-181`） | **closed**（规则可落地；`.lock` 锁行为已实测可行）；“标记不可持久化”的表示与 V22 注入方式仍缺一句 | R3-P2-11 |
| P1-03 | AC12 无 V / CORE 执行面模糊 | V24（`:182`）；L-2 行明确“`assemble_production_core` 对象图，非 `CoreServiceServer` 命令面”（`:152`）；AC12（`:140`） | **closed**（V24 覆盖 AC12；L-2 N/A 前提已写明）；V24 无 .NET 测试命令 | R3-P2-11 |
| P1-04 | R-APPLY-2 与 receipt 冲突 | R-APPLY-2 重放优先（`:93`）、R-APPLY-3（`:94`） | **closed**（规则层矛盾消除）；但 AC11/V19 的“旧→新 stale 拒绝”与新的优先序冲突 | R3-P1-01 |
| P1-05 | manual 位漏检 | Q-9（`:66`）改为 三锁 + `text_json.translation_locked` + `text_json.manual_edited`；R-DIGEST-1（`:99`）、AC10/V17（`:138`/`:175`） | **closed**（`set_locks` 解锁场景现在会改变 digest）；digest 输入是 SC-D12 公式的超集，需一句口径说明 | R3-P2-04 |
| P2-01 | PLAN 行未同步 | PLAN `:15` 已改 v4/r3 + Q-1…Q-11（STATUS `:7` 同步） | **closed** | — |
| P2-02 | core_service 写权 / FOLLOW-UP / approval | 写域已删 `core_service.py`（卡 `:23-43`）；GOAL §3B 登记 Q-6…Q-11 与 FOLLOW-UP-FEA03-1/2/3（`:48-61`）；`approval` 改为 `Q1_Q3_Q6_Q11` | **partial**：approval 未含 Q-7…Q-10，`review_appointment` 未列 r3 | R3-P2-12 |
| P2-03 | 执行面/L-2 | L-2 行已明确对象图；`:153` 旧表述已删 | **closed** | — |
| P2-04 | `tests/core` 基线写权 | 仍授予 `test_region_write_commands.py`/`test_region_batch_locking.py` 写权（`:41-42`） | **open**（与“不降低既有断言”张力仍在） | R3-P2-12 |
| P2-05 | Q-10 措辞 | Q-10 明确“草稿缓冲阶段，不产生新 revision”（`:67`）；AC3/V7 一致 | **closed** | — |
| P2-06 | 崩溃注入机制 | AC5 写明“单元级异常注入 + 集成级真实进程 kill 各一”（`:133`） | **closed** | — |
| P2-07 | fsync 目录 Windows 降级 / `rg` 命令（合并项） | R-JOURNAL-2 已写平台降级（`:80`）✓；R-LEGACY-3 仍未给 flags（`:104`） | **partial**（fsync 闭环；rg 未闭环） | R3-P2-09 |
| P2-08 | AC13 基线范围（tests/infrastructure + tests/domain） | AC13 仍含 `tests/infrastructure`（`:141`）；且命令包含当前不存在的 `tests/domain` | **open** | R3-P2-08 |
| P2-09 | R-APPLY-1 保护/digest 检查位置 | R-APPLY-1 已写“事务内、扩展 seam”（`:92`） | **closed**（位置已写明；与 C-13 冻结记录 §4 铁律 2 的张力见 R3-P2-05） | R3-P2-05 |
| P2-10 | C-13 `:94` 导出/删除 preflight deferral | 卡内无该登记（grep 仅 receipt 行命中“删除”） | **open** | R3-P2-10 |
| P2-11 | AC2 flush 断言层级 | AC2/V3 仍只写“5 个 flush 触发点”，未说明 Core seam 与 UI 触发的分层 | **open** | R3-P2-12 |
| P2-12 | C-13 §4.4 错误码口径 | L-2 行声明新码仅 Core 内部、`allowedRunErrorCodes` 当前不存在（`:152`） | **closed**（未点名 §4.4，留实现复核提示即可） | — |

**计数**：closed 11、partial 3、open 4（共 18）。

---

## 3. B 部分：v4 卡片逐项核查

### 3.1 P0-01 / Q-11 / AC11 / V19

- Q-11（`:68`）+ 来源 4（`:53`）+ AC11（`:139`）+ V19（`:177`）+ 离场 closeout（`:212`）已按 C-13 v6 改写；AC11 写出“旧→新 = 1”“新→旧 = 2”两种顺序的期望，V19 也写出期望值 → r2 要求的“期望值缺失”已补。
- **但“旧→新 = 新路径 stale 拒绝”与 R-APPLY-2/R-APPLY-3 冲突**：R-APPLY-2（`:93`）规定“先查 receipt/DB 去重，命中 → 返回既有 revisionId（不写、不判 stale）”，R-APPLY-3（`:94`）对每个目标 Region 查 `(region_id, base_revision_id, 内容摘要)` 相同且内容一致的行。旧路径先写出的 revision 正是 base 的子 revision、内容一致 → 新路径按 R-APPLY-2 应先命中 DB 去重并返回该 revision，而不是 stale 拒绝。只有在“内容不同”或“去重未命中（例如去重被限定为本 token 之后提交的 revision）”时才走 stale。AC11/V19 现文没有这一限定，因此与 R-APPLY-2/R-APPLY-3 自相矛盾；这也影响 C-13 v6 的“验证：同一内容先后走旧路径、新路径 → 只产生一个 revision”在实现复核时的判读（两种路径都满足 1 revision，但返回语义不同）。→ **R3-P1-01**
- “旧路径行为不变”已不再与 v6 冲突（v6 明确不要求旧路径去重）✓。

### 3.2 R-APPLY-2/R-APPLY-3（P1-04 处置）

- R-APPLY-2 的“重放命中优先于 stale”消除了 r2-P1-04 的直接矛盾 ✓；R-APPLY-3 作为 receipt 崩溃窗口的兜底方向正确。
- **但 R-APPLY-3 按现文无法实现**：
  1. `region_revisions` 表**没有 `base_revision_id` 列、也没有内容摘要列**（`schema.py:251-270`：region_revision_id/region_id/revision_no/snapshot_json/origin/review_state/is_pinned/source_run_id/source_step_run_id/restored_from_revision_id/created_at）。
  2. `RegionRepository` 协议只有 `get_region`/`list_revisions`/`get_revision(region_id, revision_no)`，**没有按 revision_id 取行**的 API（`ports.py:17-34`）；`RegionRevision` 实体也没有 base 字段（`entities.py` 的 RegionRevision dataclass）。
  3. 内容摘要的 canonical 定义（R-LEGACY-2 `:103`）是 `{text_json, geometry(normalized), style_json}`；已提交 revision 的 snapshot 里 `geometry` 是**页像素**几何（`Region.snapshot_state()` 的 `geometry.as_jsonable()`，`entities.py`），要归一化必须知道 page_w/page_h。`pages` 表**没有宽高列**（`schema.py:54-63`），页尺寸来自加载页图/目录；`region_canvas.page_geometry_to_normalized`（`:115`）显式要求 `page_w/page_h`，非正尺寸抛 `PAGE_SIZE_UNAVAILABLE`。卡内没有写这些依赖、页尺寸来源与不可用时的 fail-closed 语义。
  4. R-APPLY-3 要求“apply 事务内”查重，而 `commit_region_batch` 的事务在 SQLite 适配器内部（`regions.py:313` `BEGIN IMMEDIATE`）；应用层无法在其事务内用 repository 查询。要满足该要求，必须扩展 batch seam 的输入（每 Region 的 base/expected digest/候选内容摘要）与输出（每 Region 命中 revisionId），或把去重逻辑放进 adapter；卡内只对保护/digest 检查写了“扩展 seam”（R-APPLY-1），没有为 R-APPLY-3 定义同样的扩展与返回结构。
  5. 旧写点与本次提交的去重归属不明确：旧路径写出的 revision 与新路径 revision 同为 `origin=user`，表内没有“令牌/路径”标记；若不定义归属规则（如 receipt、`created_at >= token.issuedAt` 等），R-APPLY-3 会命中旧路径或其它同内容写入——这与 R3-P1-01 是同一问题的两面。→ **R3-P1-02**

### 3.3 P1-05 manual 位（Q-9）

- Q-9（`:66`）与 R-DIGEST-1（`:99`）现为 `三锁（region 列）+ text_json.translation_locked + text_json.manual_edited`；AC10/V17 断言“改任一位或锁 → digest 变化 → `LOCK_CHANGED`”。
- 对照源码：`save_manual_translation` 置 `RegionText.manual_edited = True` 与 `RegionText.translation_locked = True`（`entities.py:172-178`），但**不镜像** region 列；随后 `set_locks(translation_locked=False)` 调 `unlock_translation` 并把 region 列置 False（`service.py:1334-1341`；`RegionText.unlock_translation` 只清 text 位，`entities.py:187-189`）。因此 r2 指出的“解锁后 digest 不变”场景现在会因 `text_json.translation_locked` 变化而被发现 ✓；重新加锁（save 路径置 text 位）也会被覆盖 ✓。**r2-P1-05 已闭环。**
- 附带口径问题：C-13 SC-D12 公式写的是 `三锁 ‖ manualFlagIn(text_json)`，并说“只覆盖 manual 位”；v4 的 digest 输入是**超集**（额外纳入 `text_json.translation_locked` 与 `manual_edited` 两个 text 位）。方向上这是补齐保护位、不会引入普通保存的假阳性（`manual_edited`/text 锁只在保护动作或人工保存时变），但严格按公式字面属于“扩展定义”。建议在卡内 Q-9 或 C-13 冻结记录 Errata 明确“`manualFlagIn(text_json)` 的实现取 `translation_locked` 与 `manual_edited` 的派生，二者均属保护位”，避免实现复核按字面判偏离。→ **R3-P2-04**

### 3.4 P1-01 receipt 多序列/崩溃窗口/清理

- 已闭环部分：Q-7 改为 `<DraftId>.<DraftSequence>.json` 多序列（`:64`）；R-RECEIPT-2 规定 receipt 命中返回同 revisionId、缺失由 R-APPLY-3 兜底、同 token 不同 contentDigest → `EDIT_TOKEN_REUSED`（`:85`）；R-RECEIPT-3 规定随 Draft 生命周期/7 天清理且不删 journal（`:86`）；AC15/V20/V21 覆盖（`:143`/`:178-179`）。
- **未闭环 1（receipt 形状 vs 多 Region apply）**：R-APPLY-1 要求“一次 apply 全部 Region 在同一事务内”，AC7/V14 明确 3 Region 一次 apply 会产生 3 个 revision；但 R-RECEIPT-1 每条 receipt 只有一个 `revisionId` 和一个 `contentDigest`。对 3 Region apply，receipt 无法表达“Region→revisionId”映射；AC4/AC15 的“同 revisionId”（单数）在跨 Region apply 下无定义；若部分 Region 命中、部分未命中的重放（例如某 Region 被并发写入）行为也未定义。→ **R3-P1-03**
- **未闭环 2（R-APPLY-3 兜底不可实现）**：见 §3.2。
- 未闭环 3（P2 级）：receipt 7 天清理后，`EDIT_TOKEN_REUSED`（同 token 不同内容）不再可判（无 receipt 时 DB 去重只能识别同内容命中）；卡未定义幂等窗口与清理后行为。→ **R3-P2-07**

### 3.5 P1-02 journal 只读通道/单写者（R-JOURNAL-4 + AC17/V22/V23）

- R-JOURNAL-4（`:82`）已改为“不依赖 Host 只读通道”：①OS 层 data-root 不可写 → `DRAFT_JOURNAL_UNWRITABLE`，内存草稿继续可编辑并标记不可持久化；②`<data-root>/drafts/.lock` 独占文件锁，第二实例 fail-closed；③Host 只读下 UI 提示 deferral 到 FEA-04。AC17/V22/V23 覆盖（`:145`/`:180-181`）。
- 可实现性核验：本机 win32 实测 `msvcrt.locking(LK_NBLCK)` 同进程第二个 handle 取同一字节锁 → `OSError errno 13`，因此“第二实例 fail-closed”和 V23 可用同进程两 handle 模拟，无需真实进程；OS 释放锁后第二个 handle 可取得锁（V23 的“释放后可启动”可测）。**规则可实现、可测试** ✓。
- 残余（P2）：①“标记不可持久化”的表示（draft 状态字段？错误面返回 FEA-04？）未定义；②V22 的“data-root 不可写”注入方式未定义（Windows ACL / 把 `<data-root>/drafts` 做成文件 / monkeypatch 均可行，测试须选一个并写进 V22）；③`.lock` 文件本身的路径/清理（遗留空文件是否允许）未写。

### 3.6 P1-03 AC12 无 V / CORE 执行面

- V24（`:182`）“BRIDGE 草稿缓冲：11 字段投影；单串行队列；flush 触发；不接线”已覆盖 AC12 ✓。
- L-2 行（`:152`）已明确“新错误码仅 Core 内部结构化返回（`assemble_production_core` 对象图，非 `CoreServiceServer` 命令面）；BRIDGE 不接线；不改 `allowedRunErrorCodes`（该白名单当前代码不存在）”，旧 `:153` 的“CORE 全部从真实 Core 服务执行”模糊表述已删除 ✓。**r2-P1-03 已闭环。**
- 残余（P2）：V24/AC12 没有给出 .NET 测试命令（AC13 只有 pytest 基线）；BRIDGE 的 11 字段/队列/不接线断言应由 `NewManga.ApplicationCore.Tests` 执行，卡内应写明命令或明确由实现 Handoff 指定。→ **R3-P2-11**

### 3.7 剩余 P2 清单核验

| 项 | 状态（v4） | 证据 | 结论 |
|---|---|---|---|
| PLAN 行同步 v4 | ✅ | `REBASELINE_PLAN.md:15`（v4/r3 + Q-1…Q-11） | 已闭环 |
| GOAL 登记 Q-6…Q-11 | ✅ | `GOAL-PROGRESS:48-61` §3B（含 FOLLOW-UP-FEA03-1/2/3） | 已闭环 |
| `core_service.py` 写权移除 | ✅ | 卡 `allowed_paths:23-43` 仅 `core_assembly.py` | 已闭环 |
| `rg` 排除定义 | ❌ | R-LEGACY-3 `:104` 只有“排除定义与 tests 后 0 命中”，无 flags/命令 | R3-P2-09 |
| `tests/infrastructure` 收窄 | ❌ | AC13 `:141` 仍整目录；且命令含当前不存在的 `tests/domain` | R3-P2-08 |
| `commit_region_batch` 检查位置 | ✅/⚠ | R-APPLY-1 `:92` 写“事务内、扩展 seam” | 已写明；但与 C-13 冻结记录 §4 铁律 2“不改 `ports.py` 契约”的张力需一句 reconcile → R3-P2-05 |
| `fsync 目录` Windows 降级 | ✅ | R-JOURNAL-2 `:80` 平台降级 + 已知限制 | 已闭环 |
| C-13 `:94` 导出/删除 preflight deferral | ❌ | 卡内无“导出/删除 preflight”登记（grep 仅 receipt 行命中“删除”） | R3-P2-10 |
| 版本/元数据 | ⚠ | 标题 v4，但来源 5（`:54`）仍写“本版 v3”；`approval`（`:7`）= `Q1_Q3_Q6_Q11` 缺 Q-7…Q-10；`review_appointment`（`:21`）未列 r3；来源 2（`:51`）仍写 C-13 v5/pin `d2cb8de4…` | R3-P2-01 / R3-P2-12 |
| `tests/core` 基线写权 | ⚠ | `:41-42` 仍授予写权；`:188` 只写“不降低既有断言” | R3-P2-12 |
| AC2 flush 断言层级 | ⚠ | AC2/V3 未说明是 Core seam 五类原因还是真实 UI 触发 | R3-P2-12 |

### 3.8 新问题小结

1. AC11/V19“旧→新 = stale 拒绝”与 R-APPLY-2/R-APPLY-3 的去重优先直接冲突（R3-P1-01）。
2. R-APPLY-3 的 `(region_id, base_revision_id, 内容摘要)` 在现有 schema/协议下不可查询、不可归属、normalized geometry 缺页尺寸依赖、且必须在 batch 事务内实现而未定义扩展（R3-P1-02）。
3. receipt 单 revisionId/contentDigest 与多 Region apply 不兼容，AC4/AC15 的“同 revisionId”与部分命中语义未定义（R3-P1-03）。
4. AC16 在 V1–V24 中无 V 行（v2 的 V21 覆盖已被 v4 重编号替换），V 矩阵回归（R3-P1-04）。
5. 卡内 来源 2 仍引 C-13 v5/pin；冻结记录 §1B/§2/§9 未按 v6 更新；FEA-01 冻结文档的 §2A pin 矩阵仍列 v5 pin（R3-P2-01/02/03）。
6. Q-9 的 digest 输入是 SC-D12 公式超集，需要口径说明（R3-P2-04）。
7. R-APPLY-1“扩展 seam”与 C-13 冻结记录 §4 铁律 2“不改 `ports.py` 契约”的张力（R3-P2-05）。
8. 重放/过期的 precedence、receipt 7 天清理后的 `EDIT_TOKEN_REUSED`、AC13 基线（不存在 `tests/domain` + 过宽 `tests/infrastructure`）、`rg` 命令、C-13 `:94` deferral、V24 命令、V22/V23 注入方式、元数据与写权残留（R3-P2-06…12）。

---

## 4. Findings（r3）

| 编号 | 级别 | 位置 | 问题 | 建议 | 状态 |
|---|---|---|---|---|---|
| R3-P1-01 | P1 | 卡 `:139`（AC11）、`:177`（V19）、`:93-94`（R-APPLY-2/3）、`:103`（R-LEGACY-2） | AC11/V19 写“旧→新 = 旧 1 个 + 新路径 stale 拒绝（共 1）”；但 R-APPLY-2 规定重放/DB 去重优先于 stale，R-APPLY-3 对“base 子 revision + 内容一致”的旧路径 revision 会命中并返回其 revisionId。除非 R-APPLY-3 显式限定“只匹配本 token 提交的 revision”（归属规则未定义），否则旧→新不会 stale 拒绝，AC11/V19 与规则自相矛盾 | 明确去重归属规则（例如 receipt/令牌关联，或限定只匹配本 token 在事务内写入的 revision）；把 AC11/V19 的“旧→新”写成两子场景：内容一致 → DB 去重命中返回旧 revision（1 revision）；内容不一致 → stale 拒绝；并在 V19 中断言返回语义（revisionId vs STALE_BASE_REVISION） | open |
| R3-P1-02 | P1 | 卡 `:94`（R-APPLY-3）、`:103`（R-LEGACY-2）、`:92`（R-APPLY-1）；`schema.py:251-270`、`ports.py:17-34`、`region_canvas.py:115`、`schema.py:54-63`、`regions.py:313` | R-APPLY-3 不可按现文实现：①`region_revisions` 无 `base_revision_id`/内容摘要列；②`RegionRepository` 无按 revision_id 取行 API，`RegionRevision` 无 base 字段；③canonical digest 的 normalized geometry 需 page_w/h，`pages` 表无尺寸列，页尺寸来自页图/目录，卡未写来源与 `PAGE_SIZE_UNAVAILABLE` fail-closed；④去重必须在 `commit_region_batch` 的 `BEGIN IMMEDIATE` 内，但应用层无法访问该事务，卡未定义 seam 扩展的输入（per-region base/digest）与输出（per-region 命中 revisionId） | 在卡内写明算法：base id → base.revision_no（list_revisions 查找）→ 子 revision = base.revision_no+1 → 用页尺寸把 snapshot geometry 归一化后重算 canonical digest 比对；页尺寸来源（apply 上下文的 page extent 或页图目录）与不可用时的 fail-closed 行为；明确扩展 `commit_region_batch`（可选参数 + 每 Region revisionId 返回）或把去重放进 SQLite adapter；并定义旧/新路径 revision 的归属判据 | open |
| R3-P1-03 | P1 | 卡 `:84-86`（R-RECEIPT-1/2/3）、`:92`（R-APPLY-1）、`:135`（AC7）、`:143`（AC15）、`:178-179`（V20/V21） | 多 Region apply（AC7/V14：3 Region 同事务）会产生 3 个 revision，但 receipt 每 `(DraftId, DraftSequence)` 只有一个 `revisionId` 与一个 `contentDigest`；AC4/AC15 的“同 revisionId”（单数）与“各序列可命中”在多 Region 下无定义；重放时部分 Region 命中、部分未命中的行为未定义 | receipt 改为 `{tokenId, DraftId, DraftSequence, regions:[{regionId, revisionId, contentDigest}], committedAt}`（或每 Region 一条 receipt）；apply 响应定义为 Region→revisionId 映射；明确重放的全部命中/部分命中/内容不一致判定，并同步 AC4/AC15/V20/V21 措辞 | open |
| R3-P1-04 | P1 | 卡 `:144`（AC16）、`:157-182`（V 矩阵） | AC16（`edit-open` 登记 active、Session 结束无残留 journal、孤儿 discarded、receipt 保留至 Draft 清理）在 V1–V24 中没有任何 V 行；v2 曾由 V21 覆盖，v4 重编号后丢失。AC13/AC14 为过程项也未在表中标注 | 加 V25 覆盖 AC16 四场景（登记/清理/孤儿/receipt 保留），或在该行注明 AC16 由哪条 V 承载；AC13/AC14 标注 process/无 V | open |
| R3-P2-01 | P2 | 卡 `:51`（来源 2） | 来源仍写“C-13 冻结 v5（pin `d2cb8de4…`）”，与 Q-11/AC11/closeout 的 v6（pin `8faf1e80…`）不一致 | 改为 C-13 冻结 v6 + pin `8faf1e80…`，并链接 UNFREEZE 载体 | open |
| R3-P2-02 | P2 | `doc/plan/FEA-CONTRACT-FROZEN-C13.md:20-28`（§1B）、`:30-37`（§2）、`:113`（§9 Errata）；载体 `:48`/`:51` | v6 复核链未留痕：§1B 仍写“最后一次复核 r4 approved / v5 改动”，未记 v6 UNFREEZE 与 r3；§2 条件 1 证据仍为 r1→r4；§9 仍称“pin d2cb8de4… 未变”；载体 §4/§5 声称“复核通过后更新记录”，但记录已随同一提交更新 | 在本 r3 处置提交中：§1B 增加 v6 行（差异 = 状态行 + SC-D11 追加段；已由 r3 复核）；§2 条件 1 证据补 r3；§9 加 Errata 条目说明 v6 pin 已更新（原文保留）；载体补“记录已预置、r3 通过后确认生效”的时序说明；建议按 §1A③ 补 LF blob sha256 双口径 | open（ready 前补齐） |
| R3-P2-03 | P2 | `doc/plan/FEA-01_CONTRACT_DRAFT.md:85`（FEA-01 FROZEN v2，pin `0370c189…`） | FEA-01 冻结文档 §2A pin 矩阵仍列 C-13 `d2cb8de4dd79`（v5）；v6 后与 C-13 冻结记录不一致，而 FEA-01 已被 pin，不能在本卡写域内改 | 在 FEA-01 冻结记录（非 pin 文件）加 Errata：§2A 为 2026-11-01 冻结时快照，C-13 已 v6 更新，当前 pin 以各冻结记录/`verify_pins` 为准；或在 C-13 §9 记同一事实 | open |
| R3-P2-04 | P2 | 卡 `:66`（Q-9）、`:99`（R-DIGEST-1）；C-13 SC-D12 公式；冻结记录 `:53`（铁律 2） | digest 输入是三锁 + `text_json.translation_locked` + `text_json.manual_edited`，而 SC-D12 公式写 `三锁 ‖ manualFlagIn(text_json)` 且“只覆盖 manual 位”；方向正确（补齐 r2 漏检、仍只含保护位），但严格按公式字面是超集，需明确解释，避免实现复核判偏离 | 在 Q-9 或 C-13 冻结记录 Errata 写清“`manualFlagIn(text_json)` 的实现取 `translation_locked` 与 `manual_edited` 的派生（二者均属保护位；无假阳性）”；实现复核按此口径检查 | open |
| R3-P2-05 | P2 | 卡 `:92`（R-APPLY-1）、`:99`（R-DIGEST-1）；C-13 冻结记录 `:53`（铁律 2“不改 ports.py 契约”） | R-APPLY-1 要求“保护/digest 检查在事务内（扩展 seam）”，但 C-13 冻结记录铁律 2 明写“实现需把 manual 位纳入快照比对范围（这是实现 Task 的 AC，不是改 `ports.py` 的契约）”。扩展 `commit_region_batch` 签名/`RegionLockSnapshot` 是否算“改契约”未界定 | 明确扩展形态（向后兼容的可选关键字参数或新 committer 方法，不改既有调用语义），并在 C-13 冻结记录 Errata 记录该解释；或改用适配器内部比较（不改协议），二选一并写入卡内 | open |
| R3-P2-06 | P2 | 卡 `:89`（R-TOKEN-1）、`:93`（R-APPLY-2）、`:131`（AC4）、`:167`（V9） | 重放/过期 precedence 未写全：SC-D04 要求过期 token 拒绝并返回 `EDIT_TOKEN_EXPIRED`；R-APPLY-2“先查 receipt/DB 去重”若严格先于 token 校验，则“过期 token 的重放”会返回 revisionId 而非过期错误，与 SC-D04 及 V9 冲突 | 写明前置顺序：token 存在/归属/未过期 → receipt/DB 重放命中（返回既有 revisionId）→ stale → 写；并补 V9/V20 交叉场景（过期 + receipt 命中） | open |
| R3-P2-07 | P2 | 卡 `:86`（R-RECEIPT-3）、`:85`（R-RECEIPT-2）、`:143`（AC15） | receipt 在 Draft `discarded` 或 7 天未活动时删除；删除后 `EDIT_TOKEN_REUSED`（同 token 不同内容）不再可判（无 receipt 时 DB 去重只识别同内容命中），AC15 的该断言隐含时间窗口但卡未定义 | 定义幂等窗口（例如 receipt 保留至 Draft 清理，不设 7 天；或明确 7 天后只保证同内容幂等），并写明清理后不同内容重放的行为 | open |
| R3-P2-08 | P2 | 卡 `:141`（AC13） | AC13 基线命令包含 `tests/domain`（当前 repo 不存在该目录，pytest 会报路径错误）和整个 `tests/infrastructure`（含 plugin 打包/沙箱等与本卡无关项）；未写基线“实现前”如何取得、skip/失败如何裁定 | 明确 `tests/domain` 随新测试创建（或从基线命令移除）、`tests/infrastructure` 收窄到相关文件；基线逐文件 outcome + skip 原因 + 无关失败裁定写入 Handoff | open |
| R3-P2-09 | P2 | 卡 `:104`（R-LEGACY-3） | 过渡期判据“`rg "save_manual_translation\(" src apps` 排除定义与 tests 后 0 命中”未给可执行命令/flags；字面执行会命中 `def save_manual_translation(` | 给出完整命令（例如 `rg -t py "save_manual_translation\(" src apps` 并排除定义行/`-g '!**/service.py'`），并说明 tests 排除方式 | open |
| R3-P2-10 | P2 | 卡 `:52`、`:143`（AC16）、`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:94` | C-13 `:94` 的后果承接（导出/删除 preflight 前 flush 或显式提示“有未保存草稿”；导出侧由导出 Task AC 承载、删除侧需 C-04b UNFREEZE）仍未在卡内登记，活跃草稿产生后这是必须显式 deferral 的边界 | 在“来源与授权”或“交付项映射”加一行：本卡不实现导出/删除 preflight，分别由导出实现 Task 的 AC 与 C-04b UNFREEZE 承载（引用 C-13 `:94`） | open |
| R3-P2-11 | P2 | 卡 `:145`（AC17）、`:182`（V24）、`:180-181`（V22/V23） | ①V24/AC12 无 .NET 测试命令（AC13 仅 pytest）；②V22 “data-root 不可写”注入方式未定义；③V23 双实例可用同进程两 handle 模拟（本机实测可行），但卡未写；④R-JOURNAL-4 的“标记不可持久化”如何表示（draft 状态/错误面）未定义 | 写明 BRIDGE 测试命令（`dotnet test apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/NewManga.ApplicationCore.Tests.csproj`）；V22 选一种注入方式；V23 写同进程双 handle；定义“不可持久化”标记与对 FEA-04 的暴露方式 | open |
| R3-P2-12 | P2 | 卡 `:7`（approval）、`:21`（review_appointment）、`:41-42`（tests/core 写权）、`:54`（“本版 v3”）、`:130`（AC2） | 元数据/写权残留：①标题 v4 但来源 5 写“本版 v3”；②`approval` = `Q1_Q3_Q6_Q11` 未含 Q-7…Q-10；③`review_appointment` 未列 r3（AC14 已要求 r3 approved）；④`tests/core` 两个基线文件仍授予写权，与 `:188`“不降低既有断言”张力；⑤AC2/V3 未写 flush 断言层级（Core seam 五类原因 vs 真实 UI 触发） | 统一 v4 版本措辞；`approval` 补全 `Q1…Q11`；`review_appointment` 增 r3；`tests/core` 两文件从写权移除或写明“仅在 DSH 批准且不削弱断言时可改”；AC2 注明 Core seam 断言 + UI 接线归 FEA-04/06 | open |

---

## 5. 验证记录（实际执行）

| 场景 | 命令/步骤 | 环境/commit | 结果 | 证据/备注 |
|---|---|---|---|---|
| HEAD 与工作区 | `git rev-parse HEAD`；`git status --porcelain` | `f91a7683b`，main | PASS（clean） | `f91a7683bcd8d47032097280b6ad3f2e6af5b83c` |
| v4 提交范围 | `git show --stat f91a7683b`；`git diff --stat dfa70c002..f91a7683b` | `f91a7683b` | 8 文件（契约/冻结记录/载体/卡/r2 报告/GOAL/STATUS/PLAN） | 无源码、无 schema、无其它契约字节改动 |
| C-13 v6 diff | `git diff dfa70c002..f91a7683b -- doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md` | `f91a7683b` | 仅 2 hunk：状态行 + SC-D11 追加段 | 与载体 §3“改动范围”一致 |
| C-13 pin | `Get-FileHash` + `verify_pins.ps1` | `f91a7683b` | 8faf1e80… == 冻结记录 pin；C13 OK | `PIN AUDIT: PASS (all 15)` |
| 治理检查器 | `check.ps1` | `f91a7683b` | PASS（2 warnings） | 11 非终态 Task；STATUS 3160 bytes/31 lines 80% |
| 契约状态行/pin/Changelog | 读冻结记录 §1/§8 | `f91a7683b` | v6 + 新 pin + v6 changelog ✓ | §1B/§2/§9 仍 v5 → R3-P2-02 |
| 旧 pin 残留扫描 | 全 `doc/**` 搜索 `d2cb8de4`/`C-13 冻结 v5` | `f91a7683b` | 卡 `:51`、FEA-01 `:85` 为现行文档残留（其余为历史记录/载体引用） | R3-P2-01/03 |
| AC16 V 覆盖 | 读 V1–V24 与 AC1–AC17 | `f91a7683b` | AC1–AC15/AC17 有 V；AC16 无 V | R3-P1-04 |
| R-APPLY-3 可查询性 | 读 `schema.py:251-270`、`entities.py` RegionRevision、`ports.py:17-34` | `f91a7683b` | 无 base/摘要列；无按 revision_id 取行 API | R3-P1-02 |
| normalized geometry 依赖 | 读 `pages` DDL（`schema.py:54-63`）、`region_canvas.py:115` | `f91a7683b` | pages 无宽高；归一化需 page_w/h | R3-P1-02 |
| batch 事务边界 | 读 `ports.py:83-137`、`regions.py:288/313` | `f91a7683b` | 事务在 adapter 内；应用层无法在事务内查重 | R3-P1-02 |
| manual 位解锁场景 | 读 `service.py:119`（effective locks）、`:1232-1258`（save）、`:1287-1349`（set_locks）、`entities.py:138-139/187-189` | `f91a7683b` | 解锁改变 `text_json.translation_locked` → digest 变化 ✓ | r2-P1-05 closed |
| `.lock` 行为（V23 可行性） | 本机 `python -c`：`msvcrt.locking(LK_NBLCK)` 同进程两 handle | win32 | 第一 handle OK，第二 handle `OSError errno 13`；释放后可取 | V23 可同进程模拟 |
| 运行 pytest / dotnet test | — | — | **NOT_RUN** | 无实现可测；范围冻结阶段 |
| 崩溃/并发/journal 实跑 | — | — | **NOT_RUN** | 无实现 |
| C-04b/C-08/C-05 正文逐字节 | — | — | **NOT_RUN** | 非本卡写域 |

---

## 6. 边界声明、结论与复审

**边界声明**

- 本 Review 只审范围冻结 v4 与 CONTRACT-UNFREEZE-C13 的 C-13 v5→v6 修订，不评价实现、不构成实现验收、不构成 Task 释放或 Gate 关闭。
- 未修改任何被审文件；未 commit、未 push；只新增本报告。未访问用户数据。
- `check.ps1`/`verify_pins.ps1` 的 PASS 是机械结果，不替代契约语义与范围判定；本轮再次演示 PASS 下仍存在的文档/版本不一致。

**关键结论**

- **A 部分（UNFREEZE）：`approved`。** 字节改动仅限状态行 + SC-D11 追加段，pin 与字节一致（`8faf1e80…`），载体合规，追加式修订足以消除 r2-P0-01 的契约冲突；记录留痕未完成（§1B/§2/§9、载体时序）归入 P2-02，须在 r3 处置提交补齐，不影响修订有效性。
- **B 部分（v4 范围冻结）：`changes_requested`（P0 × 0 / P1 × 4 / P2 × 12）。不写 `approved`。**
  - P1-01：AC11/V19 的“旧→新 = stale 拒绝”与 R-APPLY-2/R-APPLY-3 的去重优先冲突，且去重归属规则未定义。
  - P1-02：R-APPLY-3 按现文不可实现（无 base/摘要列、无按 id 取行 API、normalized geometry 缺页尺寸、事务内执行未定义 seam 扩展）。
  - P1-03：receipt 单 revisionId/contentDigest 与多 Region apply 不兼容，AC4/AC15 的“同 revisionId”与部分命中语义未定义。
  - P1-04：AC16 无 V 行（V1–V24 覆盖回归）。
  - P2 共 12 条：来源仍引 v5 pin；冻结记录 v6 留痕未完成；FEA-01 冻结矩阵旧 pin；Q-9 digest 超集口径；`ports.py` 扩展与冻结铁律 2 张力；重放/过期 precedence；receipt 7 天清理窗口；AC13 基线（不存在 `tests/domain` + 过宽 `tests/infrastructure`）；`rg` 命令；C-13 `:94` deferral；V24 命令与 V22/V23 注入方式；元数据/写权/AC2 层级残留。

**建议最小闭环顺序**

1. **A 部分整改（P2-02/03）**：r3 处置提交补 C-13 冻结记录 §1B/§2/§9（v6 复核链、LF blob sha、pin 变更 Errata），载体补时序说明，FEA-01 冻结记录加 §2A 快照 Errata。
2. **P1-01**：定义 R-APPLY-3 的“本 token/本路径”归属判据；把 AC11/V19 的旧→新拆成“同内容 = DB 去重命中返回旧 revision”与“不同内容 = stale 拒绝”两子场景，并写清返回语义。
3. **P1-02**：把 R-APPLY-3 的算法与 seam 扩展写进卡（base→revision_no、子 revision、页尺寸来源与 `PAGE_SIZE_UNAVAILABLE` fail-closed、可选参数与 per-Region revisionId 返回）；或改为 receipt 持久化 per-Region digest 的替代方案。
4. **P1-03**：receipt 改为 per-Region 映射（或每 Region 一条），定义 apply 响应与重放全命中/部分命中语义，同步 AC4/AC15/V20/V21。
5. **P1-04**：补 V25 覆盖 AC16；AC13/AC14 标注 process。
6. **P2**：按 §4 表逐项处理；元数据/写权/来源 pin 等机械项可在同一处置提交完成。
7. 修订后以新 head 提交，派 r4（可基于 diff 复审）；只有 P0/P1 清零且 UNFREEZE 记录闭环后才写 `approved`。

**复审口径**：r4 需逐条 disposition 本报告 4 条 P1 与 12 条 P2（fixed/deferred with owner/not applicable + 理由），重新确认 `verify_pins`（C13 = `8faf1e80…`）与 `check.ps1`，并确认 C-13 冻结记录 §1B/§2 的 v6 复核链已闭合；实现复核（`doc/reviews/FEA-03-r1.md`）仍不在本报告范围。

---

*Reviewer：`fea03-scope-reviewer`（DSH Agent Teams durable teammate，fresh 独立上下文，由 Team Lead `lead` 派发；未参与 FEA-03 的起草、v1–v4 范围冻结或 UNFREEZE 载体起草）。日期：2026-11-01。*
