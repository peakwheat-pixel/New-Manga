---
task: FEA-06-RESIDUAL-4A
task_id: FEA-06-RESIDUAL-4A
reviewer: independent sub-agent (r2, read-only, not involved in r1 or implementation)
reviewer_kind: subagent
base_commit: 39de89e1ecc5ec10465c34794fe87ed0f0171fc4
reviewed_head: 756ab29e2
verdict: approved
date: 2026-11-14
p0: 0
p1: 0
p2: 2
p3: 5
---

# FEA-06-RESIDUAL-4A r2：修复面窄复核（P1 关闭 + pin 基线 + 四门禁）

## 0. 结论

**`approved`。P0 = 0，P1 = 0，P2 = 2，P3 = 5。**

r1 的两条 P1 均已真实关闭，且没有以「修复」为名触碰 inventory 字节：

- **P1-1 已关闭**：`FEA-CONTRACT-FROZEN-C07.md` §5 的 v1.9 行不再声称 `check.ps1` 为红，改为「台账重生成后 PASS；重生成前曾因 TASK_LEDGER 计数过期报错」，与同文件 §2 条件 4 及本轮实测 PASS 一致。
- **P1-2 已关闭**：载体 §3 已删除「`expected_revision` 可选」，改为明确「**不接受** `expected_revision`」，并与 dispatcher `:868-871`、Core handler `:3561-3582` 的实际字段面一致。

**基线未被破坏**：pin 三口径（工作树、HEAD blob LF 归一、冻结记录 §1 置顶）均 = `91e51ab74da201b99b6704e49fca96e93657d869dcc1e9523661dbb299c6d750`；`756ab29e2` 未触 `doc/plan/FEA-C07_API_INVENTORY.md`；四门禁本轮复跑全部 EXIT=0。

**剩余问题均不阻断 C-07 v1.9 重冻**：P2-1（4A 卡「规格 v1.1」未显式版本化，S1:75 / S3:108 仍保留 r1 指出的旧陈述）、P2-2（`TARGET_NOT_FOUND` 在 P2-2/P2-3 处置中的层级与「未知 page」语义仍有歧义）。两者都只涉及 4A 卡文本，不触 inventory/pin，建议在释放 4B 前修正。

## 1. 审查对象与环境

| 项 | 值 |
|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` |
| 被审 head | `756ab29e2f2a0039f89f696de18c09fd92368814`（父 `39de89e1ecc5ec10465c34794fe87ed0f0171fc4`） |
| 提交 | `dsh-lead <dsh@local>`，2026-11-14T09:19:36+08:00，`fea06: dispose RESIDUAL-4A r1 findings (P1 fixed, inventory bytes untouched, pin stays v1.9)` |
| diff 基线 | `39de89e1e`（r1 处置前） |
| 环境 | Windows NT 10.0.26300；PowerShell 7.6.8；Python 3.14.6；git 2.52.0.windows.1 |
| 审查时工作树 | 本会话首条命令 `git status --porcelain=v1` 为空；门禁复跑时仍为空。**09:23:40 出现未跟踪** `doc/tasks/FEA-06-RESIDUAL-4B.md`（DSH 并行起草，**不在** `756ab29e2`）；本报告不把它计入被审字节，仅在 §2.4 作为 P2-6/P2-5 可执行性的下游旁证。审查结束后 DSH 以 `5ee2db0af` 将该 4B 卡与 4A「S7 扩面 errata」落盘（详见 §5），该提交不在本 r2 的 `reviewed_head` 内 |
| 只读纪律 | 未 commit / push / checkout；未改 `doc/plan/**`、卡面、`verification/**`、`src/**`、`apps/**`、`tests/**`；本报告是唯一新增的仓库文件 |
| 独立性 | 由 parent `session-90dc2552-798c-4921-abff-823ae8e6ca5e` 派发的独立上下文子 agent；未参与 4A 的写作、实现或 r1 复核；不采信卡面自述 |

说明：本轮只核**修复面 + 未被破坏的基线**，不重做 r1 的成员表逐行解析（r1 已做，且 inventory 字节在本提交前后逐字节相同）；但 pin、旧 pin、diff 范围、两处 P1 原文、四门禁均重新实测。

## 2. 逐项核验

| # | 要求 | 判定 |
|---|---|---|
| 1 | pin 三口径未变 + 提交未触 inventory | **PASS** |
| 2 | P1-1 已真实关闭 | **PASS** |
| 3 | P1-2 已真实关闭 | **PASS** |
| 4 | P2 处置逐条覆盖且可执行 + README AC5/旧 pin 命令 | **PASS（覆盖/可执行）/ PARTIAL（规格正文固化）** |
| 5 | 四门禁复跑 | **PASS** |
| 6 | 未引入新问题 | **PARTIAL（越界 PASS；记录层残留 P2/P3，非 P1）** |

### 2.1 pin 三口径 — **PASS**

| 口径 | 命令 | 结果 |
|---|---|---|
| 工作树 SHA-256 | `(Get-FileHash -Algorithm SHA256 doc/plan/FEA-C07_API_INVENTORY.md).Hash.ToLower()` | `91e51ab74da201b99b6704e49fca96e93657d869dcc1e9523661dbb299c6d750` |
| HEAD blob（LF 归一） | `git cat-file blob HEAD:doc/plan/FEA-C07_API_INVENTORY.md \| python -c "…sha256…"` | RAW = `91e51ab7…`；LF_NORM = `91e51ab7…`；`CR:0 LF:160 BYTES:13040` |
| 冻结记录 §1 置顶 pin | `doc/plan/FEA-CONTRACT-FROZEN-C07.md:15` | `91e51ab74da201b99b6704e49fca96e93657d869dcc1e9523661dbb299c6d750` |
| 修复前 blob（父提交） | `git cat-file blob 39de89e1e:…` | `91e51ab7…`，13040 B（与 HEAD 相同） |
| 旧 pin 复现（v1.8 父提交） | `git cat-file blob 4cb24ed20:…` | `8ccaba05…`；`CR:0 LF:144 BYTES:10260`（与 §1「前一 pin（v1.8）」一致） |

**提交未触 inventory**：

```
$ git show --stat --oneline 756ab29e2
756ab29e2 fea06: dispose RESIDUAL-4A r1 findings (P1 fixed, inventory bytes untouched, pin stays v1.9)
 doc/plan/FEA-CONTRACT-FROZEN-C07.md                |   4 +-
 .../CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md        |   2 +-
 doc/reviews/FEA-06-RESIDUAL-4A-r1.md               | 206 +++++++++++++++++++++
 doc/tasks/FEA-06-RESIDUAL-4A.md                    |  32 ++++
 verification/FEA-06-RESIDUAL-4A/README.md          |   4 +-
 5 files changed, 243 insertions(+), 5 deletions(-)
```

`git show --name-only 756ab29e2 | Select-String "FEA-C07_API_INVENTORY.md"` 为空；`git diff --name-only 39de89e1e 756ab29e2 -- doc/plan/FEA-C07_API_INVENTORY.md` 为空。**PASS**。

### 2.2 P1-1（冻结记录 §5 假门禁陈述）— **PASS**

原文与修复后（`doc/plan/FEA-CONTRACT-FROZEN-C07.md:100`）：

- 旧：「`check.ps1` 因新增卡使 TASK_LEDGER 计数过期而红（待 DSH 重生成台账）」
- 新：「`check.ps1` 在台账重生成后 PASS，重生成前曾因 TASK_LEDGER 计数过期报错」

与同文件 §2 条件 4（`:45`）「经 DSH 2026-11-14 授权执行一次 `python tools/governance/task_ledger.py --write` 后，`check.ps1`（默认 + `-TaskPath`）**PASS (3 warnings)**」一致；本轮 §2.5 实测同为 PASS / EXIT=0。旧句不再作为「当前门禁」陈述，假陈述已消除。**PASS**。

补充：§1B（`:32`）仍写「v1.9：独立字节级复核 `pending`」，§2 条件 1（`:42`）写 `✅（v1.9 ⏳ pending）`，载体 §6 仍为 `pending`——**没有**提前写成 approved，符合「复核前不得重冻」的纪律。

### 2.3 P1-2（载体误写 `expected_revision`）— **PASS**

修复后 `doc/reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md:46`：

> `HostCommandDispatcher.cs:868-871`（`page_id` 必填、`region_ids` 可选；**不接受 `expected_revision`**——该字段属 `restore_region_revision`（`core_service.py:3605+`），不得混入本命令签名，否则偏离本预授权）

独立源码核对：

```
apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
 868:             case "list_page_region_texts":
 869:                 writer.WriteString("page_id", RequireString(name, payload, "page_id"));
 870:                 WriteOptionalStringArray(writer, name, payload, "region_ids");
 871:                 break;
```

```
src/bootstrap/core_service.py
3561:         page_id = payload.get("page_id")
3566:         requested = payload.get("region_ids")
3612:         expected_revision = payload.get("expected_revision")   # handle_restore_region_revision, 3607+
```

Core handler 只读取 `page_id` / `region_ids`；`TARGET_NOT_FOUND` 仅用于 `region_ids` 过滤中「不是本页 live region」的 id（`:3592-3596`）。`expected_revision` 出现在另一个命令 `handle_restore_region_revision`（`:3607` 起，`:3612` 读取）。修复后的「不接受」陈述与源码一致。**PASS**（`3605+` 的行号略宽，见 P3-4）。

### 2.4 P2 处置 — **PASS（覆盖/可执行）/ PARTIAL（规格正文固化）**

`doc/tasks/FEA-06-RESIDUAL-4A.md` 的「r1 独立复核处置」节（`:193-223`）逐条覆盖 P2-1…P2-7：

| r1 项 | 处置位置 | 判定 | 说明 |
|---|---|---|---|
| P2-1 | `:207` | **PASS** | 冻结记录 §2 条件 1 已改为 `✅（v1.9 ⏳ pending）`；证据格写明 r1 `changes_requested` 与「复核前不得重冻」。仍以 ✅ 开头，见 P3-5 |
| P2-2 | `:208` | **PARTIAL** | 给出 `HOST_NOT_READY` → `REGION_TEXT_PROJECTION_UNAVAILABLE` → `TARGET_NOT_FOUND` 的固定优先级；但 `TARGET_NOT_FOUND（page 不存在）` 的层级/语义有歧义，见 P2-2 |
| P2-3 | `:209` | **PARTIAL** | 处置文本正确指出「`regions: []` 不能单独表示该页无区域」；但规格正文 `S3:108` 仍写「空集合只表示该页真实没有区域」，见 P2-1 |
| P2-4 | `:210` | **PARTIAL** | 处置文本正确要求 L2 取实时 `DraftText`；但规格正文 `S1:75` / `S2:89` 仍写 `Draft.Patch["text"]` / `patch.text`，见 P2-1 |
| P2-5 | `:211` | **PASS（核心句在）** | 已写死「`REGION_TEXT_PROJECTION_UNAVAILABLE` … **不得**加入 `DraftErrorMap`（19 键闭集 …）」；未提 `HOST_NOT_READY`，见 P3-1 |
| P2-6 | `:212` | **PASS** | 已写「4B 卡 `allowed_paths` 必须包含 `WorkbenchViewModel.cs` / `WorkbenchPageView.cs`（及新增控件文件）」；审查期间出现的未跟踪 4B 草稿实测已列入这两个路径（后随 `5ee2db0af` 落盘；不在被审 head，仅作旁证） |
| P2-7 | `:213` | **PASS** | README `:26` 已由 `git show HEAD:` 改为 `git show 4cb24ed20:`；本轮实测该命令 SHA-256 = `8ccaba05…` |

`verification/FEA-06-RESIDUAL-4A/README.md`：

- **AC5 行已更正（PASS）**：`:17` 为 `CHANGES_REQUESTED (r1)`，写明 P0=0 / P1=2 / P2=7 / P3=5、字节层全过、P1 为记录层事实错误、已修 P1-1/P1-2、待 r2。
- **旧 pin 复现命令已更正（PASS）**：`:26` 为 `git show 4cb24ed20:…`，并注明「不可用 `HEAD`——提交后 HEAD 指向新 pin」；实测得 `8ccaba05…`。
- **残留（P3-2）**：README `:62` 仍写「独立字节级复核 NOT_RUN」，与本文件 `:17` 的 `CHANGES_REQUESTED (r1)` 矛盾。

**为什么只判 PARTIAL 而不判 FAIL**：P2 处置的**覆盖与可执行性**成立（每条都有具体动作/判据，P2-5、P2-6 的关键约束都在；下游 4B 草稿已按这些约束编码）。P2-3/P2-4 的问题在于**规格正文未被改写**，处置只存在于追加节；这不会改变 C-07 字节或 pin，但会让只读规格正文的 4B 实现者看到与处置相反的旧句。按 r1 的严重度框架（P2「应修复，不单独阻断本轮重冻」），这属于应在释放 4B 前修正的 P2，不构成 P1。

### 2.5 四门禁复跑 — **PASS（本轮实测）**

四门禁均在 `756ab29e2`、工作树干净时执行；原始输出如下。

**① 默认 check**

```
$ pwsh -NoProfile -File tools/governance/check.ps1
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\MAINT-1-RELEASE-MONITOR.md
WARN: 存在 8 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3177 bytes / 32 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6954 bytes / 64 lines
Governance check: PASS (3 warnings)
EXIT=0
```

**② `-TaskPath` check**

```
$ pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-06-RESIDUAL-4A.md
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\FEA-06-RESIDUAL-4A.md
WARN: 存在 8 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3177 bytes / 32 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6954 bytes / 64 lines
Governance check: PASS (3 warnings)
EXIT=0
```

**③ verify_pins**

```
$ pwsh -NoProfile -File tools/governance/verify_pins.ps1
OK C01b 3c9f5af7d74f
OK C02 bb365ca891a7
OK C03 b77e7968a00b
OK C04b 4b304c0c315f
OK C05 f6e6f3cb1fe1
OK C06 75f8e2b4eb80
OK C07 91e51ab74da2
OK C08 453f993c1a16
OK C09 dc51226b336c
OK C10 ec8fd862f95f
OK C11 44f4273f7ad1
OK C12 f49835860143
OK C13 8faf1e805eac
OK C14 05056cbf65f9
OK C15 f9e376a0ed4c
OK C16 67286eeca8cb
OK C17 cdeee4872e29
OK FEA01 0370c18932b1
PIN AUDIT: PASS (all 18)
EXIT=0
```

**④ inventory `--check`**

```
$ python tools/generate_api_inventory.py --check
| 接口 | 方法数 | 属性/事件/字段数 |
|---|---|---|
| IReaderProgressSink | 1 | 0 |
| IHostController | 79 | 4 |
| IRunController | 6 | 0 |
| **合计** | **86** | — |
...
stderr: OK: rendered counts match FEA-C07 doc
EXIT=0
```

说明：`--check` 的 stdout 是 105 行渲染清单，这里只截计数块；完整渲染与 r1 及 `verification/.../logs/api-inventory.log` 一致。脚本 `tools/generate_api_inventory.py:162-178` 在 `--check` 路径只读 `DOC.read_text`，不写文件；执行前后 `git status` 未出现 inventory 改动。四门禁全部 EXIT=0。**PASS**。

### 2.6 未引入新问题 — **PARTIAL**

**范围（PASS）**：

```
$ git diff --name-status 39de89e1e 756ab29e2
M	doc/plan/FEA-CONTRACT-FROZEN-C07.md
M	doc/reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md
A	doc/reviews/FEA-06-RESIDUAL-4A-r1.md
M	doc/tasks/FEA-06-RESIDUAL-4A.md
M	verification/FEA-06-RESIDUAL-4A/README.md
```

5 个文件全部 ⊆ `allowed_paths`（`doc/reviews/FEA-06-RESIDUAL-4A-*.md` 覆盖 r1 报告；`verification/FEA-06-RESIDUAL-4A/**` 覆盖 README）；`git diff --name-only 39de89e1e 756ab29e2 -- src apps tests` 为空；无 DDL/schema、无 inventory 字节改动。

**记录层（PARTIAL）**：

- 未发现「pending → approved」：载体 §6（`:72`）与冻结记录 §1B（`:32`）仍为 `pending`；冻结记录 §2 条件 1 仍写 v1.9 `pending`。
- 未发现「未执行 → PASS」：四门禁确实是本轮实测 PASS；P2-7 的 README 命令确实已改并可复现。
- **但**发现与 r1 P1-1 同类的记录残留：P2 处置表声称「规格 v1.1 更正/约束/写死」，而 4A 卡只有「对照内容规格 v1」正文，`S1:75`、`S2:89`、`S3:108` 仍是 r1 指出的旧陈述，见 P2-1；AC5 卡面/README 仍写「未派发 / NOT_RUN」，见 P3-2。这些是 P2/P3，不是 P1（不涉及 C-07 字节，且下游 4B 草稿已按处置表编码）。

## 3. 问题清单

### P2（应修复，不阻断 C-07 v1.9 重冻）

**P2-1｜「规格 v1.1」未显式版本化，规格正文仍保留 r1 指出的旧陈述**

- **位置**：`doc/tasks/FEA-06-RESIDUAL-4A.md:208-211`（P2-2/P2-3/P2-4/P2-5 的「规格 v1.1 …」），以及 `:66`（仍是「对照内容规格 v1」）、`:75`、`:89`、`:108`、`:68`。
- **事实**：
  - 卡面没有「对照内容规格 v1.1」节；`Select-String "规格 v1.1"` 只命中处置表本身，没有 v1.1 正文。
  - `S3:108` 仍写「空集合只表示该页真实没有区域」，与 P2-3 处置「`regions: []` **不能**单独表示…」相反。
  - `S1:75` 仍把 L2 定义为 `Draft.Patch["text"]`（读取口径同 `ReadDraftText`），`S2:89` 仍写「草稿 `patch.text`」，与 P2-4 处置「必须取实时 `DraftText`，不得取持久化 `Draft.Patch`」相反。
  - `:68` 仍写「任何与本节冲突的实现视为超范围」；若 4B 按处置表实现，字面上会与 v1 正文冲突。
- **影响**：4A 是 4B 的规格来源；只读 v1 正文的实现者会得到错误行为。审查期间出现的未跟踪 4B 草稿（`doc/tasks/FEA-06-RESIDUAL-4B.md`，不在 `756ab29e2`）已把处置表称为「v1.1 硬约束」并按其编码，说明下游能消解，但 4A 卡自身仍不自洽。
- **建议**：在 4A 卡补一个显式的「对照内容规格 v1.1（r1 处置增量）」节，写明「本节覆盖 v1 的 S1/S3/S5/S7 对应条目」，或直接改 `S1:75`、`S2:89`、`S3:108`；同时把 title/AC1 的「规格 v1」改为「v1 + v1.1 增量」。只动 4A 卡，不触 inventory/pin。
- **级别理由**：属于规格文本/版本化缺口，处置内容本身已可执行；按 r1 框架 P2 不单独阻断重冻，但在释放 4B 前应修。

**P2-2｜`TARGET_NOT_FOUND` 的层级与「未知 page」语义仍有歧义**

- **位置**：`doc/tasks/FEA-06-RESIDUAL-4A.md:208`（P2-2 处置「③ `TARGET_NOT_FOUND`（page 不存在）」）与 `:209`（P2-3 处置「结合 `page_size`/`page_id` 与 `TARGET_NOT_FOUND` 区分」）。
- **事实**：
  - Core `handle_list_page_region_texts` 对未知 page 返回 `regions: []` 且 `page_size: null`（`core_service.py:3556-3558`）；`TARGET_NOT_FOUND` 只在 `region_ids` 过滤中出现「不是本页 live region」时抛出（`:3592-3596`）。
  - `TARGET_NOT_FOUND` 同时是 `DraftErrorMap` 的 19 个 wire 码之一（`WorkbenchViewModel.cs:813`）。把「page 不存在」直接写成 `TARGET_NOT_FOUND`，会被读成 wire 语义，和「面板本地原因码」混层。
  - r1 P2-3 的最小修复是「空集合 = Core 返回 `regions: []`（未知 page 亦为空且 `page_size=null`）；**不得把空集合升级为 typed 错误**」。当前处置表没有明确「未知 page 是空态还是失败态」，只写「结合 `page_size`/`page_id` 与 `TARGET_NOT_FOUND` 区分」，仍可被 4B 读成「升级为 typed 错误」。未跟踪 4B 草稿 `:98` 正是把 `Regions.Count == 0 && PageSize is null` 映射为 `TARGET_NOT_FOUND`——这是下游对歧义的一种解读，不应由 4A 留白。
- **影响**：4B 可能把「未知 page」显示为 `TARGET_NOT_FOUND` 失败态而不是空态/另行判别，也可能把面板本地码与 wire 码混用；不会改变 C-07 字节，但会在 4B Review 变成新的记录/行为争议。
- **建议**：在 v1.1 增量中写死两条：① 面板本地 `TARGET_NOT_FOUND` 与 wire `TARGET_NOT_FOUND` 同名不同层；② 明确「未知 page（`[]` + `page_size=null`）」按空态还是按本地失败态处理，并与 r1 P2-3 的「不得升级为 typed 错误」对齐（若选择失败态，需说明这是 4A 对 r1 建议的显式修订，而不是静默改写）。
- **级别理由**：语义歧义会影响 4B 可判别性；不触 inventory/pin，P2。

### P3（登记/建议，不阻断）

- **P3-1｜P2-5 处置未提 `HOST_NOT_READY`**：`:211` 只写 `REGION_TEXT_PROJECTION_UNAVAILABLE`，r1 P2-5 的最小修复点名 `REGION_TEXT_PROJECTION_UNAVAILABLE` / `HOST_NOT_READY` 两个码都不得加入 `DraftErrorMap`。未跟踪 4B 草稿 `:99` 已把三者都写入 AC5；建议 4A 的 P2-5 句补上 `HOST_NOT_READY`（或明确「其余面板本地码同理」）。
- **P3-2｜AC5 卡面/README 记录落后一拍**：`doc/tasks/FEA-06-RESIDUAL-4A.md:63` 仍为 `<<PENDING: 未派发>>`，`:190` 仍写「**未做**：独立字节级复核（AC5 `pending`…）」，`:248` 仍写「AC5 独立复核 `pending`」；`verification/FEA-06-RESIDUAL-4A/README.md:62` 仍写「独立字节级复核 NOT_RUN」。这些与同一提交新增的 r1 处置节（`:193-201`）及 README `:17` 矛盾。按 AI-1 r2 的 N-02 先例（同类「待派发」簿记落后判 P3），此处登记 P3；建议改为「r1 `changes_requested` → 处置 → r2」。
- **P3-3｜P1-2 处置把载体位置写成 §2**：`doc/tasks/FEA-06-RESIDUAL-4A.md:201` 写「载体 §2 曾把…」，实际修改在载体 **§3 计划节** `:46`（r1 报告也写 §3）。仅定位误差。
- **P3-4｜载体 `core_service.py:3605+` 行号略宽**：`CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md:46` 写 `:3605+`；`handle_restore_region_revision` 实际从 `:3607` 开始，`expected_revision` 在 `:3612`。建议写 `:3607-3612`。不构成事实错误（3605 是前一 handler 的 return，仍在「3605 之后」的范围），仅精度。
- **P3-5｜P2-1 状态仍以 ✅ 开头**：冻结记录 §2 条件 1 现为 `✅（v1.9 ⏳ pending）`。比 r1 时的裸 ✅ 好，但状态列首字符仍是 ✅，快速扫读仍可能读成 gate 已过；建议改为 `⏳（v1.9 pending；v1.0–v1.8 ✅）`，重冻后再翻 ✅。

## 4. 明确回答：是否满足重新独立复核后重冻 C-07 v1.9 的条件？

**满足。** 按 C-07 冻结语义逐条：

1. **独立复核**：r1 `changes_requested` 的 P1-1/P1-2 已真实关闭；本轮 r2 独立复核 `approved`，P0=0 / P1=0。r1 的字节层结论未被推翻。
2. **字节 = pin**：工作树、HEAD blob（LF 归一）、冻结记录 §1 置顶三口径均 = `91e51ab7…`；`756ab29e2` 未触 inventory；旧 pin `8ccaba05…` 可由 `4cb24ed20` 复现。
3. **记录自洽**：冻结记录 §1/§1B/§2/§3/§5 与载体 §1/§3/§4/§6 在 C-07 面上自洽；§1B/§6 仍为 `pending`，没有提前写 approved。
4. **门禁**：四门禁本轮全部 EXIT=0；C07 pin 在 `verify_pins` 中为新值，其余 17 pins 未变。

**但**：P2-1/P2-2 是 4A 卡「规格正文/版本化」与 `TARGET_NOT_FOUND` 语义的残留，**不触 inventory/pin，不影响 C-07 v1.9 重冻**；建议 DSH 在回填载体 §6 / 冻结记录 §1B、§2、§5（r2 approved）并重冻之前或之后、释放 4B 之前修正。若 DSH 要求「零 P2 再重冻」，这两项都只改 4A 卡文本，成本很低，改完可做一次 r3 窄复核（仍不必改 inventory）。

**结论口径**：本轮 `approved` 针对 **C-07 v1.9 的修复面与重冻条件**；不表示 4A 卡规格正文已无 P2，也不表示 4B 已可释放。

## 5. 方法与限制

- **只读**：未 commit / push / checkout；未修改被审文件；唯一新增文件是本报告。所有命令在 `G:\CODEX\New Manga` 执行。
- **未重做**：r1 的成员表逐行解析与 `dotnet build/test`（4A 无产品代码；4B 才涉及 UI/端口）。成员表基线依赖 r1 的 `ALL_MATCH: True` 与 inventory 字节未变（已用 blob SHA-256 证明）。
- **门禁时点**：四门禁在 `756ab29e2`、`git status` 为空时执行。09:23:40 后出现未跟踪 `doc/tasks/FEA-06-RESIDUAL-4B.md`（DSH 并行起草，不在被审提交），会改变 `doc/TASK_LEDGER.md` 的 task files 计数预期；因此**未在它出现后重跑门禁**，以免把并行工作误记为被审提交的 PASS/FAIL。该文件仅作为 P2-6/P2-5 下游可执行性的旁证，未计入被审字节。
- **审查后 HEAD 变动**：本报告写入后，DSH 将 `doc/tasks/FEA-06-RESIDUAL-4B.md` 与 4A「S7 扩面 errata / 4B 实施口径」（E-1–E-3）作为 `5ee2db0af` 落盘，HEAD 由 `756ab29e2` 前移。该提交不在本 r2 的 `reviewed_head` 内：E-1 补齐 4B 生产链 allowed_paths、E-2 明确 `TARGET_NOT_FOUND` 本地判定口径，部分回应本报告 P2-2/P2-6；但 4A 规格正文 `S1:75` / `S3:108` 与「v1.1」显式化（P2-1）在该提交中未改。若 DSH 需要 r2 覆盖 `5ee2db0af`，应对该 delta 另做窄复核；本报告 `approved` 只对 `756ab29e2` 有效。
- **审查后工作树变动（未提交）**：本报告写入后，工作树出现 4A 卡的未提交 v1.1 正文修订（新增「规格版本：v1.1」行；`S1` 的 L2 改为 VM 实时 `DraftText`；`S2` 文本行同步；`S3` 空集合语义与 `TARGET_NOT_FOUND` 本地判定；`S5` 失败表同步），直接回应本报告 P2-1/P2-2 的主要文本面（P2-2 的「未知 page 是否算 typed 失败态」仍需与 r1 P2-3 的「不得升级为 typed 错误」对齐）；同时载体 §6 与冻结记录 §1B/§2/§5 出现未提交的 r2 回填与「已重冻」标记。这些修订**均不在** `reviewed_head`，且其中「已通过 r2 独立复核 approved」引用的本报告尚未入库；若 DSH 将其落盘，建议对 4A → 新 head 的 delta 做一次 r3 窄复核（不触 inventory，pin 仍 `91e51ab7…`），再宣布 r2 覆盖新 head。
- **未采信**：卡面自述、r1 报告的结论、提交 message；pin、两处 P1 原文、dispatcher/Core 源码、四门禁均本轮实测。
- **BLOCKED**：无。
