---
task_id: FEA-DOC-RECONCILE-1
reviewer: 独立上下文 fresh subagent（DSH 派发；子 agent 会话 `a4bd44b7-1f4d-4a37-8ceb-c382e0988aad`；父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`）
reviewer_kind: subagent
review_independence: 未参与该 Task 的实现、返修、证据生成或 Handoff 撰写；只读被审 head 与指定基线，未修改任何被审文件
author: dsh-lead（DSH）
base_commit: 9b0683822
reviewed_head: b6ada81e8
r1_review: doc/reviews/FEA-DOC-RECONCILE-1-r1.md（reviewed_head 4d64bfdcb；changes_requested；P0=0/P1=1/P2=4/P3=8）
decision: approved
counts: P0=0 / P1=0 / P2=0 / P3=2（REC-09/REC-11 残余 PARTIAL）；另记 r1 范围外 P1×1（r3 已处置）
---

# Review：FEA-DOC-RECONCILE-1（FEA 线文档对账）r2

## 0. 审查者身份与来源

- 审查者：**独立上下文 fresh subagent**（`reviewer_kind: subagent`），子 agent 会话 `a4bd44b7-1f4d-4a37-8ceb-c382e0988aad`，派发方（父）会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`。
- **未参与**该 Task 的实现、返修、证据生成或 Handoff 撰写；仅只读仓库与 Git 对象。本报告是审查者唯一写入的文件。
- 仓库：`G:\CODEX\New Manga`，分支 `main`；Python 3.14、PowerShell 7.6.8。
- 被审 head：**`b6ada81e8`**（`fix(fea-doc-reconcile-1): 处置 Review r1（REC-01…REC-13）并重生成台账`）。r1 被审 head `4d64bfdcb`；首次交付 `d91dbe444`；基线 `9b0683822`。
- 审查方式：`git show` / `git diff` 读取被审 head 的对象字节 + 只读复跑治理门禁；未跑 pytest / .NET 全量（本轮 0 源码改动，不适用）。

## 1. 审查环境与仓库状态（含 head 前进声明）

- 复审开始时 `HEAD = b6ada81e8`；`doc/tasks` 无未提交改动，tracked 树干净。工作区另有一份**并行 Review 的未跟踪文件** `doc/reviews/FEA-DOC-RECONCILE-1-review.md`（17:48:03 生成，非被审提交内容，后被 r3 纳入）。
- **审查期间 HEAD 前进到 `c22aea60c`**（`fix(fea-doc-reconcile-1): r3 处置（GOV-11/D07 front matter 收口 + 四表名可追溯）`，17:49:49）。**本报告全部判定按 `git show b6ada81e8:<path>` / `git diff 4d64bfdcb..b6ada81e8` 绑定到 `b6ada81e8` 的对象字节；r3 不在本报告审查范围**（另见 §7 的范围外记录）。
- 本报告未 commit、未 push；未改任何被审文件。

## 2. 结论

**`approved`**（对 r1 的 13 条 findings 与 AC1–AC8 的对账结论）。

- r2 处置后：**FIXED 11 / PARTIAL 2 / OPEN 0**；**无新增 P0/P1**（相对 r1 的 13 条）。
- 13 条中仅 2 条 P3 仍非完全闭合：REC-09（四表名可追溯性仍要求跨文档，r3 已补）、REC-11（预算登记数字 6996 与实测 6994 不符，结构性余量未释放）。
- **7 项对账的事实内核全部成立**；r1 第 7 项（BRIDGE）的「无缺口」过度声明已撤回，改为可核依据（`FEA-07` `ExitCoordinator` + `FEA-07-RESIDUAL-2` AC-R4a-2）。
- **范围外记录（不改变上述 13 条结论）**：`b6ada81e8` 上 `FEA-GOV-11` / `FEA-D07-UNBLOCK` 仍以 `status: done` 携带 `canonical_evidence_status: pending`、`resource_closeout_status: pending`、`integration_commit: null`（GOV-11 且 `reviewer: null`），违反 `doc/09_COLLABORATION.md:77,97`。该 P1 不在 r1 的 13 条内、非 r2 引入，已由 r3 `c22aea60c` 修复并填实 evidence 表；**若最终集成绑定 `b6ada81e8` 而非 r3，该项须先处置**。

## 3. 13 条逐条判定（REC-01…REC-13）

| Finding | r1 级别 | 判定 | 依据（`b6ada81e8` 字节） |
|---|---|---|---|
| REC-01 AC7 要求「PLAN 写明不独立释放**及依据**」 | P1 | **FIXED** | AC7 已改写为「PLAN 记结论（不独立释放），依据…登记于本卡 §对账清单 #7，不留悬空节点」（`doc/tasks/FEA-DOC-RECONCILE-1.md:67`）；#7 明列依据（`:57`）；PLAN 唯一 BRIDGE 文本为「含 FEA-02-BRIDGE 裁决=不独立释放」（`doc/REBASELINE_PLAN.md:11`）。采用 r1 建议的方案②（改写 AC，不塞 PLAN），PLAN 预算亦无需再挤。 |
| REC-02 ledger 分项数字在交付 head 不成立 | P2 | **FIXED** | `doc/TASK_LEDGER.md:14-16` 现为 `559 / 0 / 13`；复审复跑 `python tools/governance/task_ledger.py` 得 `task files 559 (tracked 559, untracked 0)`、`non-terminal 13 (tracked 13)`，逐格一致；`git status --porcelain -- doc/tasks` 为空。 |
| REC-03 AC3「测试表不再 `NOT_RUN`」与事实相反 | P2 | **FIXED** | AC3 改为「测试表 `NOT_RUN` 原样保留（append-only，不据此判 PASS）」（`doc/tasks/FEA-DOC-RECONCILE-1.md:63`），与 `doc/tasks/FEA-GOV-11.md:59-61`（三行仍 `NOT_RUN`）及 Closeout `:78`（「原字节保留」）一致。 |
| REC-04 STATUS 的 L-1 冲突 + AD-003/PREREQS 过期口径未登记 | P2 | **FIXED** | `doc/STATUS.md:11` 现为「四表 DDL 已冻 = L-1 前置已满足（C-15 schema v7 + C-17 v1.1 schema v8；L-2…L-9 保留）」；`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md:128`、`doc/plan/FEA-C11_IMPL_PREREQS.md:24` 未在 r2 diff 中（`git diff --name-only` 不含）；卡 §残余 `R-1`/`R-2` 已登记（`:93-94`）。事实核对：v7 建 `source_entries`/`page_bindings`（`src/infrastructure/sqlite/schema.py:673,704`），v8 建 `source_sync_plans`/`source_operations`（`:757,763,786`），即 L-1 四表；C-15/C-17 冻结记录支持（`doc/plan/FEA-CONTRACT-FROZEN-C15.md:43,50-51`、`-C17.md:3,20`）。 |
| REC-05 BRIDGE「由 FEA-05/06/07 覆盖、无缺口」超出证据 | P2 | **FIXED** | `doc/tasks/FEA-DOC-RECONCILE-1.md:57` 改为「不独立释放；退出协调由 `FEA-07` 已交付的 `ExitCoordinator`（AC2）与 `FEA-07-RESIDUAL-2` AC-R4a-2 覆盖；残余风险另卡」；所引两行存在且语义匹配：`doc/tasks/FEA-07.md:298`（AC2 含「退出协调归进程级 ExitCoordinator」、`<<MET>>`）、`doc/tasks/FEA-07-RESIDUAL-2.md:50`（AC-R4a-2 生命周期逐项不变断言）；实现类存在（`apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Lifecycle/ExitCoordinator.cs:11`）且有测试；`doc/tasks/FEA-04.md:46` 只支持「本卡不依赖」的限定被如实保留。 |
| REC-06 D07 Closeout 未披露 D07 行 7「⚠ 部分」/L-5 | P3 | **FIXED** | `doc/tasks/FEA-D07-UNBLOCK.md:90` 新增口径补充：D07 行 7 为「⚠ 部分」，由 L-5 明文认定关闭，且「不表示 D07 逐项无保留，也不表示四表 DDL 已因此冻结」；所引 `doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md:30`（D07 行 7 ⚠ 部分）、`:39-40`（L-5 认定）语义匹配。 |
| REC-07 PLAN「完成」行丢失 `Owner c04b-impl` | P3 | **FIXED** | `doc/REBASELINE_PLAN.md:52` 现为「C-04b v1.2 `26aa0ca4a`（Owner c04b-impl）、R-1 0 pin」，Owner 署名恢复；Handoff r2 记录同步（`doc/handoffs/FEA-DOC-RECONCILE-1-d91dbe444.md` r2 表）。原基线行见 `git show 9b0683822:doc/REBASELINE_PLAN.md`（含 `Owner c04b-impl`）。 |
| REC-08 GOV-11 AC3 主证据指向 `FEA-01-FREEZE-1` 不精确 | P3 | **FIXED** | `doc/tasks/FEA-GOV-11.md:79` 追加证据更正：主证据为 `FEA-02-CORE`（独立 Review + 集成 `135479270`，按 `ADJ-2026-11-01:77` U-12），`FEA-01-FREEZE-1` 仅为冻结链末环/前置；核对 `doc/tasks/FEA-02-CORE.md:6,16`（`done` / `135479270`）与 `:10`（独立 reviewer）。 |
| REC-09 版本记法混用；四表名可追溯性不足 | P3 | **PARTIAL** | 版本记法已修：`doc/STATUS.md:11` 写「C-15 schema v7 + C-17 v1.1 schema v8」，不再把 C-15 写成「v7」、不再把 v8 挂在 FEA-11-PREREQ-1 名下；`PLAN:12` 的「C-17 v1.0」登记为 `R-3`（`doc/tasks/FEA-DOC-RECONCILE-1.md:95`）。**但四表名在 `b6ada81e8` 仍未落地**：卡 `:51` 只引「`tests/fea11/test_v8_migration.py`（v8 建 4 表）」，未列 L-1 四表；STATUS 未列；仓库内并列四表名的 `GATE-DELETE-…:41`、`FEA-C11_IMPL_PREREQS.md:24` 仍写「未冻结」（后者即 R-2）。→ 版本已修、表名可追溯性未修（r3 已在卡 §#1 补四表名）。 |
| REC-10 IMMERSIVE 补充未限定「本卡 legacy 壳」 | P3 | **FIXED** | `doc/tasks/FEA-07-IMMERSIVE-F11-1.md:133` 已限定「物理 2K/4K **仅指本卡 legacy 壳路径**；v2 壳 2K 已由 `FEA-07-V2-F11-1` 于 AOC 2560×1440 主屏物理复验（`EV-V2F-05`）」；核对 `doc/tasks/FEA-07-V2-F11-1.md:58,65,72`（2560×1440、`EV-V2F-05`；4K 仍受环境限制，未被本句误称已验证）。 |
| REC-11 PLAN 预算余量近零（6985/7000，63/64） | P3 | **PARTIAL** | 预算风险已登记为 `R-4`（`doc/tasks/FEA-DOC-RECONCILE-1.md:96`），且 Handoff r2 表与 `gates-2.log:45-46` 记 `6994/7000 B、63/64 行`（与本回复审实测一致）。**但**：①卡 `R-4` 写「6996/7000」「约 4 bytes」，与实测 6994（余 6 B）差 2 B；②「完成：」长段（`doc/REBASELINE_PLAN.md:52`）未迁出，结构余量未释放，只把处置推到「释放下一 Task 前」。→ 登记到位、数字不准、余量未释放。 |
| REC-12 Handoff 不在 allowed_paths | P3 | **FIXED** | `doc/tasks/FEA-DOC-RECONCILE-1.md:31` 已增 `doc/handoffs/FEA-DOC-RECONCILE-1-*.md`；被写文件 `FEA-DOC-RECONCILE-1-d91dbe444.md` 匹配该模式。 |
| REC-13 gates.log 无 EXIT 码、无 shell 头 | P3 | **FIXED** | 新增 `verification/FEA-DOC-RECONCILE-1/gates-2.log`：`:1-3` 有时间、`shell: 7.6.8 / Core`、`BASE`/`PRE_COMMIT_HEAD`；`:12,21,43` 三段命令逐条 `EXIT=0`；`:45-46` 预算实测；卡 Canonical Evidence `:109-110` 将 `gates-2.log` 标 CANONICAL、`gates.log` 标 HISTORICAL（commit `d91dbe444`），旧字节未改。 |

**计数：FIXED 11 / PARTIAL 2（REC-09、REC-11）/ OPEN 0。**

## 4. r1 报告字节核对（按任务要求，但前提不成立）

- **任务给定的比对基线不存在**：`git cat-file -e 4d64bfdcb:doc/reviews/FEA-DOC-RECONCILE-1-r1.md` → `fatal: path ... exists on disk, but not in '4d64bfdcb'`（exit 128）。r1 报告是在 `4d64bfdcb` **之后**由 r1 审查者写出的，在 r1 审查时是 untracked（r1 报告 §验证自述「写报告后仅 `?? doc/reviews/FEA-DOC-RECONCILE-1-r1.md`」），故不可能存在于 `4d64bfdcb`。**「应与 `git show 4d64bfdcb:…` 一致」这一核对不可执行**。
- 可核的事实：`git diff --numstat 4d64bfdcb..b6ada81e8 -- doc/reviews/FEA-DOC-RECONCILE-1-r1.md` = **81 / 0**（纯新增）；`b6ada81e8` 的 blob 与本机 worktree 字节一致（`git diff --quiet b6ada81e8 -- …` exit 0）；文件 81 行、sha256 `a978cce8…`，头部 `reviewed_head: 4d64bfdcb` / `decision: changes_requested`，正文 13 条与 P0=0/P1=1/P2=4/P3=8 自洽；`c22aea60c`（r3）`--name-status` 未包含该文件（未再改写）。
- **结论**：未发现改写迹象，但「提交前字节未被编辑」只能以「纳入时即如此」举证，**无法从 Git 证明**（r1 时为 untracked，本机无第二份提交前基线；`session_event_search` 取回原始写入事件超时，未作为证据）。此条属 review setup 的可追溯性缺口，不判为实现的缺陷。

## 5. 门禁、预算与 Canonical Evidence（实际复跑）

| # | 检查 | 命令/方法 | 结果 | EXIT |
|---|---|---|---|---|
| 1 | 治理门禁 | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)`；warnings = 13 个非终态 Task、STATUS 3026 B/28 行（80%）、PLAN 6994 B/63 行（80%） | 0 |
| 2 | 单卡门禁 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-DOC-RECONCILE-1.md` | 同上，`PASS (3 warnings)` | 0 |
| 3 | 契约 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)` | 0 |
| 4 | 台账复算 | `python tools/governance/task_ledger.py`（只读） | `task files 559 (tracked 559, untracked 0)`；`terminal 545`；`non-terminal 13 (tracked 13)` | 0 |
| 5 | 预算实测 | `Get-Item` + 逐行计数 | STATUS **3026 B / 28 行**（上限 3200/45）；PLAN **6994 B / 63 行**（上限 7000/64）——均在预算内，PLAN 仅余 6 B / 1 行 | — |
| 6 | 改动边界 | `git diff --name-only 4d64bfdcb..b6ada81e8 -- src apps tests tools doc/plan doc/contracts` | 空；r2 全部 10 个变更文件都在 `doc/**`、`verification/**`（`M×8`、`A×2`） | — |
| 7 | 7 条 CANONICAL | `Get-FileHash -Algorithm SHA256`（`b6ada81e8` worktree） | 7/7 与卡 `:103-109` 一致；HISTORICAL `gates.log` 亦与 `:110` 一致 | — |

Canonical Evidence 逐条（`b6ada81e8` worktree 字节）：`STATUS 0f282ae5…`、`PLAN c61845d6…`、`GOV11 26147255…`、`D07 58fcf1a8…`、`IMMERSIVE 4ea62822…`、`RG2 83d15cbd…`、`gates-2.log d6626c58…`；HISTORICAL `gates.log c5fcd1f7…`——**全部一致**（EOL 注意事项见 §8）。

治理门禁复跑输出与交付的 `gates-2.log:3-46` 逐项一致（警告文案、预算数字、18 个 pin 行、三段 EXIT=0），可相互印证。

## 6. 「对账结论是否成立」

- **7 项对账的事实内核均成立**：①四表 DDL 已由 C-15 v7 + C-17 v1.1（schema v8）冻结，L-1 前置满足；②`FEA-C11-PREREQ-1` DAG 行 `done`（集成 `b7018e19b`）；③GOV-11 的 4 项裁决输入与 4 份冻结记录齐备；④`G-DELETE-CONTRACT` 已于 2026-11-01 关闭（D07 行 7 的 L-5 口径已披露）；⑤IMMERSIVE 的 v2 壳 limitation 由 `FEA-07-V2-F11-1` 收口且补了 legacy 壳限定；⑥RUN-GRANT-2 的 title 为历史描述且 `status: done`；⑦BRIDGE 不独立释放的**结论与依据**现在都可核（`FEA-07` `ExitCoordinator` AC2 + `FEA-07-RESIDUAL-2` AC-R4a-2），「无缺口」的过度声明已撤回。
- **不再存在「对账结论不成立」的问题**；r1 指出的 P1（AC7/BRIDGE）已闭合。剩余的 REC-09（表名可追溯性）与 REC-11（预算数字/余量）属表述与记账残余，不推翻任何对账事实。

## 7. 范围外发现与处置（不计入 13 条）

- **P1-EXT-01（生命周期前置，`b6ada81e8` 上成立）**：`doc/tasks/FEA-GOV-11.md:6,10,16-19` 与 `doc/tasks/FEA-D07-UNBLOCK.md:6,16-19` 为 `status: done` 但 `canonical_evidence_status: pending`、`resource_closeout_status: pending`、`integration_commit: null`、`delivery_head: null`，GOV-11 另 `reviewer: null`；违反 `doc/09_COLLABORATION.md:77`（done 须集成/验证/closeout 全通过）与 `:97`（done 前两项须 `complete`）。该问题在 `d91dbe444` 即存在，非 r2 引入、不在 r1 的 13 条内；**r3 `c22aea60c` 已将其置 `b6ada81e8`/`complete` 并填实两卡的 Canonical Evidence 表**（该修复未经本报告验证，属 r3 范围）。若集成 head 仍是 `b6ada81e8`，此项须先行处置。
- **并行 Review 披露**：审查期间工作区出现另一份未跟踪的独立 Review `doc/reviews/FEA-DOC-RECONCILE-1-review.md`（reviewed_head `4d64bfdcb`，其判 P1=2/P2=4/P3=3），并被 r3 纳入。本审查者读过该文件做交叉核对，但本报告每条判定均以仓库字节独立复核；该文件的结论不构成本报告的依据或指令。

## 8. 剩余风险

- **r1 报告字节保留只能「以纳入时为准」**（§4）：无法从 Git 证明提交前未被编辑。
- **EOL 与 pin 可复现性**：`doc/tasks/FEA-11-RUN-GRANT-2.md` 的 worktree 为 CRLF（`git ls-files --eol` = `i/lf w/crlf attr/text eol=lf`），卡 pin `83d15cbd…` 是 CRLF 字节；干净 checkout 得到 LF（blob `8a5e7a56…`），pin 会失配。新增的 `gates-2.log` 无 `text eol=lf` 属性（worktree CRLF、blob `47250b24…`），其 pin `d6626c58…` 依赖 `core.autocrlf=true`。前者为 r1 既有、后者为 r2 新增的**pin 纪律残余**（不改变本轮「当前字节一致」的结论；建议下次在本卡 allowed_paths 内补 `eol=lf` 并统一重算）。`gates.log` 属 HISTORICAL，按任务口径不计。
- **PLAN 预算**：6994/7000 B、63/64 行，仅余 6 B / 1 行；`R-4` 只登记未释放，「完成：」长段仍在。任何后续 DAG 修改都须先迁移。
- **REC-09 的表名可追溯性**在 `b6ada81e8` 仍需跨 C-15/C-17/测试文件；r3 已在卡 §#1 补名（未验证）。
- **r3 未审**：`c22aea60c` 的 front matter/evidence 填实与四表名补充不在本报告范围；如以 r3 集成，建议由 r3 复审报告绑定该 head。
- **未穷举全仓过期表述**：本轮只核 13 条与 7 项对账；`doc/AD-003:128`、`doc/plan/FEA-C11_IMPL_PREREQS.md:24` 等已登记为 `R-1`/`R-2`，未在本卡修改（符合 allowed_paths）。
- **未运行**：pytest / .NET 全量（0 源码改动，不适用）；未重算 18 pins 之外的任何 pin；未做全仓 stale-wording 扫描。

## 9. 验证（实际执行）

| 场景 | 命令/步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| HEAD 与工作树 | `git rev-parse HEAD`；`git status --porcelain`；`git log -5` | `main` | 复审起点 `b6ada81e8`；tracked 树干净，`doc/tasks` 无改动；审查中出现并行 Review 未跟踪文件（后被 r3 纳入） | 本报告 §1 |
| 被审 diff | `git diff --stat/--name-status 4d64bfdcb..b6ada81e8` | 同上 | 10 文件（M×8/A×2），全部 `doc/**` + `verification/**`；`src/apps/tests/tools/doc/plan/doc/contracts` 零改动 | 命令输出 |
| 13 条逐项 | `git show b6ada81e8:<path>` + `git grep`/`Select-String` 定位行 | 同上 | 见 §3 | 各条依据行 |
| 治理门禁 | `check.ps1`；`check.ps1 -TaskPath …` | 同上 | PASS（3 warnings），EXIT=0；与 `gates-2.log:3-21` 一致 | 复跑输出 |
| 契约 pin | `verify_pins.ps1` | 同上 | PASS 18/18，EXIT=0 | 复跑输出 |
| 台账 | `task_ledger.py`（只读） | Python 3.14 | 559/559/0；non-terminal 13/13；EXIT=0 | 复跑输出；`TASK_LEDGER.md:14-16` |
| 预算 | 字节/行计数 | 同上 | STATUS 3026/28；PLAN 6994/63 | 实测；`gates-2.log:45-46` |
| Canonical sha256 | 逐项 `Get-FileHash`（b6 工作树） | 同上 | 7/7 CANONICAL + 1 HISTORICAL 一致 | 逐项比对 |
| r1 报告基线 | `git cat-file -e 4d64bfdcb:doc/reviews/…r1.md`；`git diff --numstat` | 同上 | 基线路径不存在（exit 128）；r1 报告为 +81/−0 纯新增 | §4 |
| HEAD 前进 | `git reflog`/`git log` | 同上 | 复审期间新增 `c22aea60c`（r3），本报告不覆盖 | §1/§7 |
| 未运行 | pytest / dotnet 全量 | — | NOT_RUN（0 源码改动，不适用） | — |

## 10. 审查边界

- 本报告只对 **`b6ada81e8`** 的字节负责；`c22aea60c`（r3）是在本报告形成期间产生的新 head，未审。
- 本 `approved` 是对 **r1 的 13 条处置与对账结论** 的接受，不是对 `b6ada81e8` 上一切事项的背书（§7 的 P1-EXT-01 仍以 r3 为修复载体）。
- 本报告不构成集成批准、不关闭 Task；findings 处置与最终集成 head 由 DSH 决定。审查者未参与实现、未修改任何被审文件、未 commit、未 push。
