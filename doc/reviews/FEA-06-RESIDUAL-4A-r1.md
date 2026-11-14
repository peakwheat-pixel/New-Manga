---
task: FEA-06-RESIDUAL-4A
task_id: FEA-06-RESIDUAL-4A
reviewer: independent sub-agent（独立上下文，未参与实现）
reviewer_kind: subagent
date: 2026-11-14
reviewed_head: 7c1ac472f
base_commit: 4cb24ed20556f85bbbe8c4a0ff9d34b6dbfcf65a
verdict: changes_requested
p0: 0
p1: 2
p2: 7
p3: 5
---

# FEA-06-RESIDUAL-4A r1：C-07 additive UNFREEZE v1.9 独立字节级复核

## 0. 结论

**`changes_requested`。P0 = 0，P1 = 2，P2 = 7，P3 = 5。**

**通过的部分（全部为本轮实测，不采信卡面自述）**：pin `91e51ab7…` 双口径可复现；正式成员表与源码逐行一致（`ALL_MATCH: True`，`IHostController` 79 方法 + 4 非方法成员，三接口合计 86）；`--check` EXIT 0；越界为零（提交 10 个文件全部 ⊆ `allowed_paths`，`src/**`/`apps/**`/`tests/**` 零改动）；`verify_pins.ps1` 18/18 PASS 且 C07 为新 pin、其余 17 pins 零改动；v1.2–v1.8 历史 pin 行与变更行保持原字节。

**阻断项全部在记录层（非 inventory 字节）**：

- **P1-1**：冻结记录 §5 的 v1.9 行仍写「`check.ps1` … 红（待 DSH 重生成台账）」，与本文件 §2 条件 4、载体 §4.6、卡面、证据 README 及本轮实测 PASS 直接矛盾；
- **P1-2**：载体 §3 把 `expected_revision` 写成 `list_page_region_texts` 的「可选」分发字段，但 dispatcher 与 Core handler 均不接受该字段；若 4B 据此给端口加参数，会偏离已预授权的签名，需二次 UNFREEZE。

两处修复都不触碰 `doc/plan/FEA-C07_API_INVENTORY.md` 字节，pin 仍应为 `91e51ab7…`。

## 1. 审查对象与环境

| 项 | 值 |
|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` |
| 被审 head | `7c1ac472f`（`fea06: RESIDUAL-4A C-07 additive UNFREEZE v1.9 …`），父提交 `4cb24ed20` |
| 审查时现状 | 工作树干净；审查期间 DSH 在 `7c1ac472f` 之上追加了 `776cfeb78`（custom_rank 测试）与 `39de89e1e`（RO-1 errata，仅改裁决文档）。**4A 的 5 个契约/证据路径在 `7c1ac472f..HEAD` 零差异**（`git diff --stat` 为空），故本轮字节证据在现 HEAD 仍成立 |
| 环境 | Windows NT 10.0.26300；PowerShell 7.6.8；Python 3.14.6 |
| 只读纪律 | 未 commit / push；未改 `doc/plan/**`、卡面、`verification/**`、`src/**`、`apps/**`、`tests/**`；唯一新增文件是本报告；独立解析脚本放在仓外 `G:\CODEX\New Manga.workspace\task-temp\FEA-06-RESIDUAL-4A-review\` |
| 独立性 | 本会话未参与 4A 的写作、实现或返修；结论只依据本轮命令输出与源码/字节原文 |

## 2. 逐项核验

### 2.1 pin 双口径 — **PASS**

| 口径 | 命令 | 结果 |
|---|---|---|
| 工作树 SHA-256 | `(Get-FileHash -Algorithm SHA256 doc/plan/FEA-C07_API_INVENTORY.md).Hash` | `91e51ab74da201b99b6704e49fca96e93657d869dcc1e9523661dbb299c6d750` |
| 提交 blob 字节 SHA-256（`7c1ac472f` 与现 HEAD） | `git cat-file blob <head>:doc/plan/FEA-C07_API_INVENTORY.md \| python -c "…sha256…"` | `91e51ab74da201b99b6704e49fca96e93657d869dcc1e9523661dbb299c6d750` |
| 冻结记录 §1 新 pin | `doc/plan/FEA-CONTRACT-FROZEN-C07.md:15` | `91e51ab74da201b99b6704e49fca96e93657d869dcc1e9523661dbb299c6d750` |
| 旧 pin 复现（父提交） | `git cat-file blob 4cb24ed20:doc/plan/FEA-C07_API_INVENTORY.md \| …sha256…` | `8ccaba05cbc21eec04a366f8bfa2be2dea4515ba90e6d5aab95b11a7c47f0509` |
| 「前一 pin（v1.8，保留原值）」 | `FEA-CONTRACT-FROZEN-C07.md:16` | `8ccaba05…`（原值保留，未被追溯改写） |

**口径说明（重要）**：冻结记录定义的是「文件字节 SHA-256」，而 `git hash-object` 默认输出 **SHA-1 blob id**，二者天生不可能相等。本项按语义核验：`git hash-object` = `d488d1111743aadf0f43704cab6aaa4312bbf39f`，与提交 diff 的 index 行 `index 23d407cea..d488d1111` 一致；同一 blob 的 **SHA-256** 三处一致等于 pin。另 `git cat-file -s` = 13040 B（新）/ 10260 B（旧），与 README 的 13,040 B 相符。若把验收条件按字面读成「`git hash-object` 必须等于 SHA-256 pin」，该条件本身不可满足；按 pin 语义，本项 PASS。

### 2.2 成员表逐行 = 源码 — **PASS**

- **独立解析器**（未 import `tools/generate_api_inventory.py`，自行解析源码 interface 块）读取 `IHostController.cs`（`IHostController` 在 `:116`、`IReaderProgressSink` 在 `:104`）与 `RunContracts.cs`（`IRunController` 在 `:365`），得到 `IHostController` **79 方法 + 4 非方法成员**（`Snapshot`/`StartRequests`/`ExportDirectorySuggestion`/`Changed`）、三接口 **86**；与 `doc/plan/FEA-C07_API_INVENTORY.md` 正式成员表（`:32-118`、`:120-128`）逐行比对输出：

```
IReaderProgressSink: src=1 doc=1  MATCH
IHostController: src_methods=79 doc_methods=79; src_nonmethod=4 doc_nonmethod=4  MATCH
IRunController: src=6 doc=6  MATCH
ALL_MATCH: True
TL_TOTAL_METHODS: 86
EXIT=0
```

- `python tools/generate_api_inventory.py --check` → **EXIT 0**，stderr `OK: rendered counts match FEA-C07 doc`，stdout 统计 `1 / 79 / 6 = 86`。
- 文档统计行 `:20`（`IHostController | 79`）与 `:22`（合计 `86`）与实测一致。
- 说明：`IReaderProgressSink` 实际位于 `IHostController.cs:104`（任务简述把它归入 `RunContracts.cs` 不准确）；生成脚本同时解析两文件，结论不受影响。

### 2.3 记录链自洽 — **PARTIAL**

已核实为真：

- 载体 §6（`CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md:72`）为 **`pending`**，未预写 approved；
- 冻结记录 §1B（`:32`）如实写「v1.9：独立字节级复核 `pending`」；
- 冻结记录 §5（`:100`）有 v1.9 变更行；
- §2 条件 3（`:44`）计数 `1/79/6 = 86`，并写明 4B 落地后 `1/80/6 = 87`；
- v1.2–v1.8 的 §5 变更行与 §1 pin 链（v1.2–v1.7）与 `4cb24ed20` **逐字节相同**；v1.8 原值按 UNFREEZE 先例从「sha256（最终字节）」移入新增「前一 pin（v1.8）」行，未被改写；
- `doc/TASK_LEDGER.md` 可由工具复现：`python tools/governance/task_ledger.py --diff` 输出 `task files 600 / terminal 591 / non-terminal 8 / outside the plan 3`，与台账 `:9-16`、`:29-34`、`:44-47` 一致（工具在 `task_ledger.py:81-83` 明确排除 `README.md`）。

不一致项（详见 §3）：**P1-1**（§5 的 `check.ps1` 陈述与 §2 条件 4 及实测矛盾）、**P2-1**（§2 条件 1 标 ✅ 而 v1.9 复核 pending）、**P3-1**（§1B「复核后到冻结的改动」缺 v1.8 行，既有断档）。

### 2.4 越界 — **PASS**

`git diff --name-status 4cb24ed20 7c1ac472f` 恰为 10 个文件，全部 ⊆ 卡面 `allowed_paths`（`:21-28`，含 `doc/TASK_LEDGER.md` 的 R-1 一次性机械重生成例外 `:153`）：

```
M doc/TASK_LEDGER.md
M doc/plan/FEA-C07_API_INVENTORY.md
M doc/plan/FEA-CONTRACT-FROZEN-C07.md
A doc/reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md
A doc/tasks/FEA-06-RESIDUAL-4A.md
A verification/FEA-06-RESIDUAL-4A/README.md
A verification/FEA-06-RESIDUAL-4A/logs/api-inventory.log
A verification/FEA-06-RESIDUAL-4A/logs/gates-2026-11-14.log
A verification/FEA-06-RESIDUAL-4A/logs/member-table-eq-stdout.log
A verification/FEA-06-RESIDUAL-4A/logs/pin-before-after.log
```

- `git diff --name-only 4cb24ed20 7c1ac472f -- src apps tests` → **空**（零改动）。
- `git diff --numstat` 中 inventory = `18 2`，与载体 §1「+18/−2」指纹一致；统计行/正式成员表/S5 计划节不在任一 diff hunk 内（hunk 仅 `@@ -1,7 +1,7 @@` 与 `@@ -137,8 +137,24 @@`）。
- `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → `PIN AUDIT: PASS (all 18)`、`OK C07 91e51ab74da2`、EXIT 0；其余 17 个契约文件不在本提交 diff 中，pin 零改动。

### 2.5 规格可验收性 — **PARTIAL**

- AC1–AC6（卡面 `:59-64`）中，AC2/AC3/AC4/AC6 均可由命令/文件结构机械判定，且本轮已复核其证据；AC1（规格冻结）与 AC5（独立复核）本身是评审门，不属「机械验收」，但卡面已明确写明门槛。
- **负向不变量明确**：S5 `:133` 用整段写死「投影不可用时不得显示任何对照内容、不得用本地/缓存/L1 推测值填充」，并要求 4B 同时新增「投影不可用 → 零文本行」断言；R-3（`:179`）再次登记。**PASS**。
- **新增 typed code**：`REGION_TEXT_PROJECTION_UNAVAILABLE` 在 `src/apps/tests` 中 **0 处出现**（仅卡面 `:128` 与 `MAINT-1` 记录提及）；`DraftErrorMap`（`WorkbenchViewModel.cs:806-835`）是 19 键闭集，等于 `FEA-05_DRAFT_WIRE_CONTRACT.md:41-63` 的 17 个 wire 码 + `INTERNAL`/`UNKNOWN`（`:65`），且 `FEA-06-impl-r1` 曾认证「19 键逐码一致」。因此**该新码本身与既有闭集不冲突**（它是 UI 面板本地原因，不属 wire 码表）；但规格没有写死「不得把它加进 `DraftErrorMap`」，存在 4B 破坏该闭集的风险 → **P2-5**。
- 其余规格精度问题：失败态判别链（P2-2）、空集合语义（P2-3）、L2「当前工作副本」口径（P2-4）、S7 允许面的边界（P2-6）。

### 2.6 CRLF / pin 可复现性 — **PARTIAL（既有债，不判 FAIL）**

- `git config core.autocrlf` = **true**；`git check-attr text eol -- doc/plan/FEA-C07_API_INVENTORY.md` = `unspecified`/`unspecified`；`.gitattributes` 中无 `doc/plan/**` 或该文件的 `eol=lf` 规则（现有规则只覆盖 `doc/tasks/*.md`、`doc/handoffs/*`、部分 `verification/**`）。
- 当前工作树与 blob 均为纯 LF：`CR=0 LF=160`，大小 13040 B（两者一致），故 **pin 在本工作树/LF 克隆可复现**。
- 但在 `core.autocrlf=true` 的 fresh clone 上，checkout 会把该文本文件转成 CRLF，SHA-256 变化 → `verify_pins.ps1` 的 C07 会失败。该债对 v1.8 及更早 pin 同样成立，**非本轮引入**，载体 §4.4（`:60`）与证据 README（`:69`）已如实披露。按本轮规则不判 FAIL；建议登记或修复（P3-5）。

## 3. 问题清单

### P1（必须在重冻前修复）

**P1-1｜冻结记录 §5 的 v1.9 行断言 `check.ps1` 为红，与同文件 §2 及实测矛盾**

- **位置**：`doc/plan/FEA-CONTRACT-FROZEN-C07.md:100`（§5 v1.9 行末）。
- **事实**：该行写「`check.ps1` 因新增卡使 TASK_LEDGER 计数过期而红（待 DSH 重生成台账）」。
- **证据**：同文件 §2 条件 4（`:45`）写「经 DSH 2026-11-14 授权执行一次 `python tools/governance/task_ledger.py --write` 后，`check.ps1`（默认 + `-TaskPath`）**PASS (3 warnings)**，台账随同一 commit 提交」；committed 台账已由 599/7 变为 600/8；本轮实测默认与 `-TaskPath` 均 `PASS (3 warnings)` / EXIT=0；`verification/FEA-06-RESIDUAL-4A/logs/gates-2026-11-14.log:13-28` 同样是 PASS；commit message 亦写「门禁四件套 EXIT=0」。该句是提交前旧状态的残留，作为「当前门禁」陈述为假。
- **最小修复**：把该句改为「台账经 DSH 授权重生成后 `check.ps1` **PASS (3 warnings)**；重生成前曾因台账过期报错」。不改 inventory 字节/pin。

**P1-2｜载体把 `expected_revision` 写成 `list_page_region_texts` 的可选字段（事实错误）**

- **位置**：`doc/reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md:46`（§3「接入既有面」括号内）。
- **事实**：原文「`HostCommandDispatcher.cs:868-871`（`page_id` 必填、`region_ids` 可选、`expected_revision` 可选）」；实际上该命令只写 `page_id` 与 `region_ids`。
- **证据**：`HostCommandDispatcher.cs:868-871` 的 case 块仅 `WriteString("page_id", …)` + `WriteOptionalStringArray(…, "region_ids")` + `break`；Core `handle_list_page_region_texts`（`core_service.py:3533-3605`）只读取 `page_id`/`region_ids`，其 docstring（`:3544`）亦写 `{"page_id", "region_ids"?}`；`expected_revision` 出现在别的命令（如 `restore_region_revision` 的 `:3612`、dispatcher `:862` 的 `pin_revision`）。`RegionPageTextProjection.Parse` 也不含该字段。
- **风险**：4B 若按载体实现 `expectedRevision` 参数，会使端口签名偏离 inventory 计划节（`:146`）与卡面 S3（`:102-105`）的预授权签名，触发第二次 UNFREEZE。
- **最小修复**：删除「、`expected_revision` 可选」，或改写为「该命令不接受 `expected_revision`（与写命令不同）」。

### P2（应修复，不单独阻断本轮重冻）

**P2-1｜§2 条件 1 标 ✅，而 v1.9 独立复核仍 pending**

- 位置：`FEA-CONTRACT-FROZEN-C07.md:42`。
- 事实/证据：同一行文末与 §1B（`:32`）、载体 §6（`:72`）、卡面 AC5（`:63`）、证据 README（`:17`）均写 pending；重冻前「独立复核通过」对 v1.9 尚未成立，✅ 会被读成 gate 已过。
- 最小修复：状态改「⏳（v1.9 `pending`；v1.0–v1.8 ✅）」或拆为两行；重冻时再翻 ✅。

**P2-2｜失败态 typed 原因的判别链未定义**

- 位置：卡面 `:108`（`null` 语义）与 S5 表 `:126-131`。
- 事实：端口唯一失败返回是 `null`，但表要求区分 `REGION_TEXT_PROJECTION_UNAVAILABLE` / `HOST_NOT_READY` / `TARGET_NOT_FOUND`；规格未写判定来源与优先级（例如先看 `Snapshot` 就绪/`LastError`，再落到面板本地码）。
- 证据：现有读方法失败会 `SetLastError("HOST_NOT_READY")`（`HostController.cs:308` 等），但卡面没有把该通道写进规格。
- 最小修复：在 S3/S5 写死优先级（建议：Host 未就绪 → `HOST_NOT_READY`；否则 `null` → `REGION_TEXT_PROJECTION_UNAVAILABLE`；`regionIds` 过滤缺目标 → `TARGET_NOT_FOUND`），或让端口返回 typed 结果。

**P2-3｜「空集合只表示该页真实没有区域」与 Core 行为不符**

- 位置：卡面 `:108`。
- 事实/证据：Core handler docstring 明确写「A page with no regions **-- unknown page_id included --** reads as `regions: []` … an unknown page additionally reads `page_size: null`」（`core_service.py:3556-3558`）。按现规格，4B 可能把「未知 page」当成「无可比对内容」而不是失败态。
- 最小修复：改为「空集合 = Core 返回 `regions: []`（未知 page 亦为空且 `page_size=null`）；不得把空集合升级为 typed 错误，也不得以 `null`/伪造值冒充」。

**P2-4｜L2「当前工作副本」取持久化草稿，与 VM 的实时编辑文本可能不一致**

- 位置：卡面 `:75`（L2 定义）、`:89-90`（文本/来源）。
- 事实：规格把 L2 文本定义为 `Draft.Patch["text"]`（读取口径同 `ReadDraftText`），而 VM 的实时编辑值是 `DraftText`（`WorkbenchViewModel.cs:31-32/70-77`），可能与 `_persistedDraftText` 不同（`HasUnsavedDraft`，`:94-95`）；冲突态输入仍可能可编辑（`WorkbenchPageView.cs:705` 的 `IsEnabled = !IsReadOnly && CurrentDraft is not null`）。
- 影响：面板可能把「已保存草稿」当作「当前工作副本」展示，用户刚输入但未保存的文本不会出现在对照里。
- 最小修复：明确 L2 文本 = `WorkbenchViewModel.DraftText`（实时）或明确标注「本地已保存草稿」，并补一条对应断言。

**P2-5｜新 typed code 与 `DraftErrorMap` 19 键闭集的边界未写死**

- 位置：卡面 `:126-133`；映射在 `WorkbenchViewModel.cs:806-835`。
- 事实：`DraftErrorMap` 为 19 键闭集 = `FEA-05_DRAFT_WIRE_CONTRACT.md:41-63` 的 17 码 + `INTERNAL`/`UNKNOWN`（`:65`），`FEA-06-impl-r1` 曾以「19 键逐码一致」认证。规格要求新码在面板显示 bespoke 文案，但未禁止把它加进 `DraftErrorMap`；若 4B 加入，会破坏该闭集与 FEA-05 §3 的对应关系，并出现在 `WorkbenchPageView.cs:721` 的错误码列表里。
- 最小修复：在 S5/S7 加一句「`REGION_TEXT_PROJECTION_UNAVAILABLE` / `HOST_NOT_READY` 是面板本地 typed 原因，不得加入 `DraftErrorMap`，也不得改 FEA-05 §3 码表」。

**P2-6｜S7 允许面未包含实现面板所必需的 VM/View 编辑**

- 位置：卡面 `:142-146`（S7）。
- 事实：S7「只允许新增：1 个 `IHostController` 方法 + 3 处实现 + 1 个对照面板控件 + 1 组测试」；但面板需要 `WorkbenchViewModel` 的对照状态/命令（端口调用、L1/L2 数据、失败态）与 `WorkbenchPageView` 的冲突横幅旁按钮/容器（`:656-660` 附近），字面遵守会与实现所需冲突，迫使 4B 回卡改规格。
- 最小修复：在 allowed 列表补「`WorkbenchViewModel` 对照状态/命令（只增，不改既有公共 API 语义）与 `WorkbenchPageView` 对照容器/按钮（不改 `FluentUi.Banner` 签名、非冲突态零变化）」。

**P2-7｜证据 README 的旧 pin 复现命令在提交后指向新 pin**

- 位置：`verification/FEA-06-RESIDUAL-4A/README.md:26`；同类表述见 `logs/pin-before-after.log:2`。
- 事实：写「`git show HEAD:doc/plan/FEA-C07_API_INVENTORY.md` → … SHA-256 = `8ccaba05…`」；提交后 HEAD 已含新字节，实测该命令 SHA-256 = `91e51ab7…`（新 pin）。证据是在提交前生成的，但 README 作为提交后的可复现说明已失效。
- 最小修复：改为 `git show 4cb24ed20:doc/plan/FEA-C07_API_INVENTORY.md`，并在日志头记录生成时 HEAD。

### P3（登记/建议）

- **P3-1**：`FEA-CONTRACT-FROZEN-C07.md:33`（§1B「复核后到冻结的改动」）缺 v1.8 行（既有），本次追加 v1.9 后呈 v1.7 → v1.9 断档；建议在下次触及时补「v1.8：AI-1 统计 79/86 + P21–P25 成员表并入」。
- **P3-2**：载体 `:21` 指纹拆分称 RO-1 节「12 行」，实际该节 15 行（`FEA-C07_API_INVENTORY.md:140-154`，9 非空 + 6 空行）；总数 `+18/−2` 正确，拆分口径不精确。
- **P3-3**：卡面 `:121` 称「测试已按 `Content` 含『查看对照』断言」，但既有 `:668-669` 是 `DoesNotContain`（卡面 `:133` 已正确纠正）；建议改为「既有反向断言」。
- **P3-4**：证据 README `:7` 称「全部日志头行记录生成时 HEAD 与 `git status --short`」，实际 `pin-before-after.log` 与 `member-table-eq-stdout.log` 均无 HEAD/status；建议改为「部分日志」或补齐。
- **P3-5**：`.gitattributes` 无 `doc/plan/FEA-C07_API_INVENTORY.md text eol=lf`，`core.autocrlf=true` 下 fresh clone 会破坏该 pin（既有债，v1.8 及更早同样成立；载体/README 已披露）。建议登记为 GOV-EOL-PIN 扩展或单独修复；不在本卡 `allowed_paths` 内，故不判 FAIL。

## 4. 明确回答：本次 UNFREEZE 是否满足「重新独立复核后重冻」的条件？

**当前（`7c1ac472f`）不满足。** 字节层、统计层、成员表层、越界面与门禁全部通过，但冻结记录/载体内仍有 **2 个 P1 事实错误**（P1-1、P1-2）；在 C-07「复核字节 = 冻结字节、记录必须自洽」的纪律下，不能带着这两个错误重冻。

**修复后即可满足，且成本很低**：P1-1、P1-2（建议连同 P2-1、P2-7）都只改 `doc/plan/FEA-CONTRACT-FROZEN-C07.md` / 载体 / 证据 README，**不触碰 inventory 字节**，所以 pin `91e51ab7…`、成员表 79/86、`--check`/`verify_pins` 结论全部保持有效；r2 只需做窄复核（重算三口径、重读两处改动、复跑四门禁）即可判 `approved`，随后由 DSH 回填载体 §6 与冻结记录 §1B（并把 §2 条件 1 按 P2-1 处理）后重冻。

若 DSH 对 P1-1/P1-2 的严重度有不同口径，可降级为 P2 并在重冻提交中一并修正；但**以当前字节直接重冻会使冻结记录永久保留一处假门禁陈述和一处假 wire 字段陈述**，本复核不建议这样做。

## 5. 复核方法与限制

- **独立解析**：成员表比对使用自写解析器（仓外 `verify_members.py`），未调用/未 import 仓库的 `tools/generate_api_inventory.py`，只把结果与脚本 stdout、「`--check`」和源码三方对照。
- **未复跑**：`dotnet build/test`（4A 无产品代码，非本卡判别面）；UI/行为实现属 4B，本轮不评。
- **未修改**：载体 §6 与冻结记录 §1B 均未回填（按只读纪律），复核定性与回填由 DSH 执行；本报告是本轮唯一新增文件。
- **HEAD 变动**：审查期间 HEAD 由 `7c1ac472f` 前移至 `39de89e1e`；已确认 `7c1ac472f..HEAD` 对 4A 的 5 个契约/证据路径零差异，故上表字节证据仍对当前树成立。
