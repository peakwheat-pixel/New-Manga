---
task: FEA-06-RESIDUAL-4A
task_id: FEA-06-RESIDUAL-4A
reviewer: independent sub-agent (r4, read-only, not involved in r1/r2/r3/implementation)
reviewer_kind: subagent
base_commit: eae0eb67a04843f25c8794a18c6729111bece264
reviewed_head: f3ca74a10
verdict: changes_requested
date: 2026-11-14
p0: 0
p1: 0
p2: 1
p3: 4
---

# FEA-06-RESIDUAL-4A r4：r3 六条 P2 处置的窄复核

## 0. 结论

**`changes_requested`。P0 = 0，P1 = 0，P2 = 1，P3 = 4。**

被审范围 `eae0eb67a..f3ca74a10`（唯一提交 `f3ca74a10`，父 `eae0eb67a`，共 5 个文件、+324/−18）。

**r3 的 6 条 P2 全部真实关闭（6/6）**：F-1 的实质事实错误已更正（真实路径存在且 4B 卡两处已正确）、F-2 已删除「v1.1 已通过 r2」并改为与载体 §6 一致的覆盖边界、F-3 的 README 三处反向 `pending` 已清除、F-4 的台账 4B 已为 `in_progress` 且与生成器指标逐项一致、F-5 的 4B Closeout 已改「未关闭（in_progress）」、F-9 的 DSH 裁决已同时落到 4A AC1 与 4B `approval`。**基线未破**：inventory pin 仍 `91e51ab7…`、`src/apps/tests` 零 diff、`verify_pins` 18/18。

**本次 `changes_requested` 只源于 1 条新产生的记录层 P2（P2-1）**：卡面 AC1 已置 `MET`（由 r2+r3 替代 scope review），但证据索引 `verification/FEA-06-RESIDUAL-4A/README.md:13` 仍写 AC1 `PARTIAL`、判据仍是「独立 scope review 通过」——同一形式要件在记录面仍有两种互斥状态。这是**反向陈旧**（已结案写成未结案），不是「把未做说成已做」；不触 pin、不改 inventory 字节、不要求撤回 4B 释放，但下游（4B r1 Review / 集成核对）若读 README 会重新打开 F-9。

**门禁**：`check.ps1`（默认 + 4A + 4B）与 `verify_pins.ps1` 全部 **EXIT=0**；`generate_api_inventory.py --check` 在**当前工作树**为 **EXIT=1**，根因是并行 4B 第二刀在 `IHostController.cs` 新增 `ListPageRegionTextsAsync`（未提交、不属本次提交），以 `f3ca74a10` 提交 blob 复算为 **1 / 79 / 4 = 86、三接口行逐行命中 → PASS**（详见 §3.7）。

## 1. 被审范围、方法与工作树声明

| 项 | 值 |
|---|---|
| 被审区间 | `eae0eb67a..f3ca74a10`（`eae0eb67a` = 4B-1 wire 方法提交；`f3ca74a10` = 唯一被审提交） |
| 被审文件 | `doc/tasks/FEA-06-RESIDUAL-4A.md`、`doc/tasks/FEA-06-RESIDUAL-4B.md`、`doc/TASK_LEDGER.md`、`verification/FEA-06-RESIDUAL-4A/README.md`、`doc/reviews/FEA-06-RESIDUAL-4A-r3.md`（新增） |
| 审查性质 | 只读；未参与该处置、r1/r2/r3 或 4B 实现；未 checkout、未 commit、未 push；只新建本报告 |
| 方法 | 不采信自述：用 `git show <head>:<path>` 读提交态字节、`Get-FileHash` 实测 pin、`git grep` 全文核对、`task_ledger.py` stdout 与台账逐项比对、`generate_api_inventory.py` 以提交 blob 复算 |

**工作树状态声明**：审查开始时 `git status --porcelain` 为**空**；审查中段出现 5 个 `apps/**` 未提交改动（`HostController.cs` / `IHostController.cs` / `NullHostController.cs` / `HostRuntime.cs` / `FakeHostController.cs`，即 4B 第二刀）。按任务约束，这些 dirty **不计入判定**，其内容未被读取或评估；**唯一例外**是确认 `IHostController.cs` 新增了 `ListPageRegionTextsAsync`（`:277`，+16 行），用于解释 inventory 门禁的工作树 EXIT=1，不作为对 4B 工作的审查。

## 2. 逐项结论

| # | 复核项 | 结论 | 关键证据 |
|---|---|---|---|
| 1 | F-1 路径已更正、真实路径存在、旧路径不再出现 | **PASS（P2 关闭）／字面条件 FAIL（P3-1）** | `4A:234` = `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`；真实文件 134,124 B / 2,875 行 / `class HostRuntime` 在 `:20`；旧路径 `Test-Path`=False、`git log --all`=0；但 `4A:234` 的更正注记内仍含旧字符串 1 次 |
| 2 | F-2 版本行删除「已通过 r2 approved」，与载体 §6 一致 | **PASS** | `4A:70` 改为「r2 覆盖 C-07 v1.9 的 inventory 字节与记录链；v1.1/errata 属 r2 后处置，由 r3 窄复核覆盖」，与载体 `:83` 覆盖范围声明同界 |
| 3 | F-3 README 无残留 `pending`／`NOT_RUN` 矛盾 | **PASS** | README 全文 **0 处 `pending`**；`NOT_RUN` 仅 4 行且均为真实未做项（80/87、产品代码、FEA-06 AC3）；AC3/AC4/AC5 行均为 `MET`，无互斥 |
| 4 | F-4／F-5 状态一致 | **PASS** | 台账 `:41` 记 `FEA-06-RESIDUAL-4B` 为 `in_progress`（in plan = mentioned）；4B `:174`「未关闭（当前 `in_progress`…）」；4B 全文无「未释放」；台账指标与 `task_ledger.py` stdout 逐项相等 |
| 5 | F-9 裁决已落盘（AC1 + 4B approval） | **PASS**（两处均有）；附 P2-1 同步缺口 | `4A:59` `<<MET: … scope review 形式要件按 r3 F-9 裁决，由 r2+r3 两轮独立字节级复核替代>>`；`4B:8` `approval` 显式记录同一裁决并写明 DSH 承担责任；`doc/reviews/` 无其他 scope review 报告 |
| 6 | 基线未破坏（pin／diff 范围／18 pins） | **PASS** | SHA-256 = `91E51AB74DA201B99B6704E49FCA96E93657D869DCC1E9523661DBB299C6D750`；区间 5 文件全为 `doc/**` + `verification/**`，`src/apps/tests` diff = 0；`PIN AUDIT: PASS (all 18)` |
| 7 | 门禁复跑 | **PASS（提交态）**；工作树 inventory 为 EXIT=1（已归因） | `check.ps1` ×3 = `PASS (3 warnings)` / EXIT=0；`verify_pins` = 18 OK / EXIT=0；inventory 工作树 `FAIL: IHostController: rendered 80 not in doc` / EXIT=1，提交 blob 复算 79/86 全行命中 |
| 8 | 是否有新假陈述 | **PASS（未发现「未做→已做／待复核→已通过」）**；但存在 P2-1 的反向陈旧 | AC1 的 MET 依据（r2+r3 覆盖、规格三处更正）均可证；4B approval 的前置均可证；r3 引用只列 `P0=0/P1=0`、未写其 `changes_requested`/P2=6，属选择性（P3-3） |

## 3. 逐项证据

### 3.1 F-1（`4A:234`）

| 子项 | 实测 | 判定 |
|---|---|---|
| 允许面已写正确路径 | `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs` | PASS |
| 真实路径存在 | `Get-Item`：`G:\CODEX\New Manga\apps\desktop-avalonia\src\NewManga.Host\HostRuntime.cs`，134,124 B；`(Get-Content).Count` = 2,875；`Select-String 'class HostRuntime'` = `:20 public sealed class HostRuntime : IAsyncDisposable` | PASS |
| 旧路径不存在 | `Test-Path apps/desktop-avalonia/src/NewManga.App/Services/HostRuntime.cs` = `False`；`git log --all --oneline -- <旧路径>` 计数 = 0（从未存在，非搬迁） | PASS |
| 「全文不再出现旧路径」 | `4A:234` 注记仍写：「本节初稿误写为 `App/Services/HostRuntime.cs`，该路径从未存在」——**1 次** | **FAIL（字面）** |
| 4B 的承接面 | `4B:30` = `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`；`4B:107` = `src/NewManga.Host/HostRuntime.cs`（两处均正确，故 F-1 的下游阻断已消除） | PASS |

说明：该残留是**自指更正注记**（说明「错在哪、从未存在」），不是把旧路径当作有效路径；r3 的 F-1 实质（路径不可照抄）已关闭。仅按父任务「全文零出现」的字面条件判 FAIL，登记为 P3-1。

### 3.2 F-2（`4A:70` 与载体 §6）

`4A:70` 现行：

> **复核边界（r3 F-2 更正）：r2 的 `approved` 覆盖的是 C-07 v1.9 的 inventory 字节与记录链；v1.1 定稿与 S7 errata 属 r2 后处置，由 r3 窄复核覆盖（`doc/reviews/FEA-06-RESIDUAL-4A-r3.md`，P0=0/P1=0）。不得表述为「v1.1 已通过 r2」。**

与载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md:83` 的覆盖范围声明逐点一致：r2 的 `reviewed_head = 756ab29e2`、覆盖 C-07 v1.9 的 inventory 字节与记录链；v1.1 定稿与 S7 errata 属 r2 后处置，不改变 inventory 字节/pin/方法名/返回类型/统计，由 r3 窄复核覆盖。`v1.1` 确实晚于 r2（r2 的 P2-1 明写「v1.1 未显式版本化」），故该边界陈述为真。

遗留（继承 P3，非本次 6 条 P2）：载体同一段仍用未来时「待 4B 释放前由一次 r3 窄复核覆盖」（r3 F-7）；4A 新文本未重复该时序，故不构成两文件互斥。

### 3.3 F-3（README）

- `Select-String -Pattern 'pending'` → **0 命中**；`'NOT_RUN|NOT_DONE|NOT_FLIPPED'` → 仅 `:60` 标题与 `:62-65` 四条，内容分别是「复核已完成」「80/87 NOT_DONE（属 4B）」「产品代码 NOT_RUN」「FEA-06 AC3 NOT_FLIPPED」，均与当前事实一致，且与 AC3/AC4/AC5 的 `MET` 行**不矛盾**。
- `:15` AC3 = `MET`（§1B 已记 r1→处置→r2 approved 并已重冻）；`:16` AC4 = `MET`（§6 已回填 approved）；`:17` AC5 = `MET`（r2 `approved`，被审 head `756ab29e2`）。与冻结记录 §1B `:32`、载体 §6 `:72-83` 实测一致。
- 仍存的 README 陈旧：`:39`「`PLAN` 6954 B、8 个非终态 Task」实测为 6,980 B / 9（`check.ps1` 亦报 9）——r3 F-10 的 P3，未在本次范围。`:13` AC1 行是 P2-1（见 §4）。

### 3.4 F-4／F-5

**F-4（台账）**：

| 指标 | `doc/TASK_LEDGER.md` | `task_ledger.py --diff` stdout | 一致 |
|---|---|---|---|
| task files | 601 | 601 | ✅ |
| terminal / non-terminal | 591 / 9 | 591 / 9 | ✅ |
| named in plan / outside plan | 7 / 2 | 7 / 2 | ✅ |
| tracked / untracked | 601 / 0 | 601 / 0 | ✅ |
| non-terminal tracked | 9 | 9 | ✅ |
| by status | proposed 3、in_progress 2、in_review 2、(none) 1、approved 1、ready 1 | 同 | ✅ |

台账 `:41` = `` | `FEA-06-RESIDUAL-4B` | `in_progress` | mentioned | ``；4B 卡 `:6` = `status: in_progress`；`doc/REBASELINE_PLAN.md:59` 表外节点含 `FEA-06-RESIDUAL-4B(in_progress)`。**提示**：`task_ledger.py --diff` 并不读取台账文件做 diff（源码 `:164-167` 只在 stdout 追加 outside-plan 列表），故上表的相等性是「生成器指标 vs 台账文件逐项手比」，见 P3-4。

**F-5（4B Closeout）**：`:174` = 「Closeout date / DSH：未关闭（当前 `in_progress`，2026-11-14 由 DSH 释放；前置 4A r2 `approved` + C-07 v1.9 重冻）。」全文检索「未释放」= **0 命中**；`:175/:176` 的 `canonical_evidence_status: pending` / `resource_closeout_status: pending` 是未关闭任务的正常记账，不是状态互斥。

### 3.5 F-9（裁决落盘）

| 落盘点 | 现行文本 | 判定 |
|---|---|---|
| `doc/tasks/FEA-06-RESIDUAL-4A.md:59` | `[x]` AC1 + `<<MET: 规格 v1.1 已定稿（S1/S2/S3/S5 已同步 P2-2/P2-3/P2-4）；scope review 形式要件按 r3 F-9 裁决，由 r2+r3 两轮独立字节级复核替代>>` | PASS |
| `doc/tasks/FEA-06-RESIDUAL-4B.md:8` | `approval` 段：「**scope review 形式要件裁决（r3 F-9）**：本卡不另做独立 scope review，改由 4A 的 r2 + r3 两轮独立字节级复核替代——两者均由未参与实现者执行，且已核规格可验收性、allowed_paths 边界与预授权一致性；DSH 承担该替代的裁决责任。」 | PASS |
| 其他载体 | `git grep` 未发现第三份裁决记录（`doc/reviews/` 无独立 scope review 报告）；r3 的建议 ② 被 DSH 采纳并以卡面文字落盘 | PASS |

未同步面（P2-1）：证据 README `:13` 仍 `PARTIAL` + 「独立 scope review 通过为准」；4A front matter `:7-8`（`disposition: scope 未冻结`、`approval: 待 DSH scope review`）与 `:193` 下一步①也仍把 scope review 写成待办。后两者本身是 r3 F-8/F-6 的 P3，本次 AC1 结案后语义更陈旧；若 DSH 的 `approval` 指「任务释放审批」而非「AC1 的形式要件」，则应保留并注明区分。

### 3.6 基线未破坏

```
Get-FileHash -Algorithm SHA256 doc/plan/FEA-C07_API_INVENTORY.md
Algorithm : SHA256
Hash      : 91E51AB74DA201B99B6704E49FCA96E93657D869DCC1E9523661DBB299C6D750
路径      : G:\CODEX\New Manga\doc\plan\FEA-C07_API_INVENTORY.md
```

- `git diff --name-only eae0eb67a f3ca74a10`：`doc/TASK_LEDGER.md`、`doc/reviews/FEA-06-RESIDUAL-4A-r3.md`（新增）、`doc/tasks/FEA-06-RESIDUAL-4A.md`、`doc/tasks/FEA-06-RESIDUAL-4B.md`、`verification/FEA-06-RESIDUAL-4A/README.md`——**5/5 为文档或证据**；`src`/`apps`/`tests` 命中数 = **0**；inventory 与冻结记录不在 diff 中。
- `HEAD = f3ca74a10`，父 = `eae0eb67a`；提交后无追加提交。
- `verify_pins.ps1` → 18 行 OK（含 `C07 91e51ab74da2`），`PIN AUDIT: PASS (all 18)`，**EXIT=0**。

### 3.7 门禁复跑（原始输出与 EXIT）

工作目录 `G:\CODEX\New Manga`，HEAD `f3ca74a10`；审查开始时工作树干净。

**① `pwsh -NoProfile -File tools/governance/check.ps1`**

```
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\MAINT-1-RELEASE-MONITOR.md
WARN: 存在 9 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3177 bytes / 32 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6980 bytes / 64 lines
Governance check: PASS (3 warnings)
EXIT=0
```

**② `check.ps1 -TaskPath doc/tasks/FEA-06-RESIDUAL-4A.md`**

```
Task: doc\tasks\FEA-06-RESIDUAL-4A.md
（同上 3 条 WARN）
Governance check: PASS (3 warnings)
EXIT=0
```

**③ `check.ps1 -TaskPath doc/tasks/FEA-06-RESIDUAL-4B.md`**

```
Task: doc\tasks\FEA-06-RESIDUAL-4B.md
（同上 3 条 WARN）
Governance check: PASS (3 warnings)
EXIT=0
```

**④ `pwsh -NoProfile -File tools/governance/verify_pins.ps1`**

```
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

**⑤ `python tools/generate_api_inventory.py --check`（工作树，EXIT=1）**

```
| 接口 | 方法数 | 属性/事件/字段数 |
|---|---|---|
| IReaderProgressSink | 1 | 0 |
| IHostController | 80 | 4 |
| IRunController | 6 | 0 |
| **合计** | **87** | — |

（其后为完整成员表渲染，关键差异为 #35 `ListPageRegionTextsAsync` 被计入，合计 87）

FAIL: IHostController: rendered 80 not in doc
EXIT=1
```

**归因（不判本次提交 FAIL）**：`git diff --stat` 显示 `IHostController.cs` 有 **+16 行未提交**改动（并行 4B 第二刀），`git show f3ca74a10:...IHostController.cs` 中 `ListPageRegionTextsAsync` **0 命中**。以 `f3ca74a10` 的提交 blob 复算同一解析器：

```
IReaderProgressSink: methods=1 others=0 doc_has_row=True
IHostController: methods=79 others=4 doc_has_row=True
IRunController: methods=6 others=0 doc_has_row=True
total_methods=86
CHECK_AT_f3ca74a10=PASS
EXIT=0
```

（`FEA-C07_API_INVENTORY.md:22` 合计行为 `| **合计** | **86**（另有 4 个非方法成员…） |`；脚本 `--check` 只比对三接口计数行，三行均命中。）即：**提交态 inventory 门禁 PASS；工作树 EXIT=1 完全由并行未提交改动引起**。

### 3.8 新假陈述检查

对 `f3ca74a10` 新增/改写文本逐条核对：

| 新陈述 | 实测 | 判定 |
|---|---|---|
| `4A:70` 「r2 覆盖 C-07 v1.9 inventory 字节与记录链；v1.1/errata 由 r3 覆盖」 | 与载体 `:83`、r3 §3.2 一致；r2 `reviewed_head=756ab29e2` | 真 |
| `4A:59` 「规格 v1.1 已定稿（S1/S2/S3/S5 已同步 P2-2/P2-3/P2-4）」 | r3 §3.2 五处逐项 PASS | 真 |
| `4A:59` 「scope review 形式要件由 r2+r3 替代」 | r2/r3 均为独立上下文；r3 的建议 ② 被 DSH 采纳；两处落盘 | 真（归属表述见 P3-3） |
| `4A:234` 「真实文件在 NewManga.Host/，2875 行，class 于 :20」 | 实测 2,875 行、`:20`、134,124 B | 真 |
| `4B:8` 「前置：4A r2 approved、C-07 v1.9 重冻、规格 v1.1 定稿」 | 全部可证 | 真 |
| `README:15/:16/:17` MET 行 | §1B/§6/pin 实测一致 | 真 |
| `README:62` 「r3 覆盖 v1.1/S7 errata delta（P0=0/P1=0）」 | P0/P1 数值真；但未写 r3 结论 `changes_requested`/P2=6 | 选择性（P3-3） |
| `README` 无 `pending` | grep 0 命中 | 真 |
| 台账 4B `in_progress` / `untracked 0` | 与生成器 stdout、git 实况一致 | 真 |

**结论：未发现「把未做说成已做」或「把待复核说成已通过」的新增陈述。** 发现的记录问题均为反向陈旧（P2-1）或选择性引用（P3-3）。

## 4. 问题清单

> 级别口径沿用 r1/r2/r3：P0 = 破坏冻结字节/安全；P1 = 记录层假陈述且阻断重冻或实施；P2 = 应修、不单独阻断但会在下游被引用；P3 = 登记/不修。**P2-1 不触 pin、不改 inventory 字节、不要求撤回 4B 释放。**

### P2（1 项）

**P2-1｜AC1 结案未同步证据 README，记录面仍称 AC1 `PARTIAL` 且判据为独立 scope review**

- **位置**：`verification/FEA-06-RESIDUAL-4A/README.md:13` 对照 `doc/tasks/FEA-06-RESIDUAL-4A.md:59`。
- **实测**：README = 「**PARTIAL**：规格 v1 已写入卡面…；「冻结」以独立 scope review 通过为准」；卡面 = `[x]` + `<<MET: … 由 r2+r3 两轮独立字节级复核替代>>`。
- **性质**：同一形式要件在同一 Task 的两份记录里互斥；属 r3 F-3（README 反向残留）的同类，只是方向相反（MET 被写成 PARTIAL）。本次提交更新了 README 的 AC3/AC4/AC5 行，却没有同步 AC1 行。
- **下游影响**：4B 的 r1 Review 或后续集成若按 README 核对 4A 前置，会读成「规格未冻结、需补 scope review」，与 4B `approval` 的裁决冲突，可能重开 F-9。
- **修法（1 行级）**：README `:13` 改为 `MET`，写明「按 DSH 2026-11-14 对 r3 F-9 的裁决，scope review 形式要件由 r2 + r3 两轮独立字节级复核替代」。建议同时把 `4A:7-8` 与 `:193 下一步①` 的 scope review 措辞同步（若 `approval` 被定义为「任务释放审批」，则保留并注明区分）。
- **缓解事实**：卡面 AC1 与 4B `approval` 已正确落盘，故 4B 实施不被阻断。

### P3（4 项，登记）

**P3-1｜F-1 的旧路径字面残留 1 处**

- `4A:234` 的更正注记仍含 `App/Services/HostRuntime.cs`（自指「本节初稿误写为…」）。父任务字面条件「全文不再出现」未满足，但属防回归注记、不是有效路径声明；F-1 的实质已关闭。
- 可选修法：保留注记（建议，因它记录了错误来源）或将其改为「本节初稿路径错误（见 r3 F-1）」而不复写错误字符串。

**P3-2｜r3 已登记的 3 条 P3 未修（继承，不属本次 6 条 P2）**

- 载体 `:83` 仍写「待 4B 释放前由一次 r3 窄复核覆盖」（r3 F-7；实际 r3 在 4B 释放后完成）。
- `README:39` 仍写「`PLAN` 6954 B、8 个非终态 Task」；实测 6,980 B / 9（r3 F-10）。
- `4A:61/62/63` 仍为 `<<PARTIAL … pending>>` / `<<PENDING: 未派发>>`，与 README 的 AC3/AC4/AC5 `MET` 及冻结点记录相反（r3 F-6，判 P3 登记不修）。
- 建议：随 P2-1 一次修完，避免下一轮复核再遇到同源陈旧。

**P3-3｜对 r3 的引用不完整、裁决主体表述不够精确**

- `README:62` 与 `4A:59` 引用 r3 时只列 `P0=0/P1=0`，未写 r3 实际结论 `changes_requested`（P2=6，`doc/reviews/FEA-06-RESIDUAL-4A-r3.md`）；数值不假，但容易被读成「r3 通过」。
- `4A:59`「按 r3 F-9 裁决」把裁决主体写在复核者名下；`4B:8` 明确是 DSH 裁决并承担替代责任。建议统一为「按 DSH 对 r3 F-9 的裁决」，并补一句「r3 的 6 条 P2 已由 `f3ca74a10` 处置」。

**P3-4｜README 复现节对 `task_ledger.py --diff` 的描述与实现不符（预存）**

- `README:78` 写「`python tools/governance/task_ledger.py --diff` # 只读核对台账是否与 `doc/tasks/*.md` 一致」。
- 实测 `tools/governance/task_ledger.py:164-167`：`--diff` 只在 stdout 末尾追加 outside-plan 列表，**不读取 `doc/TASK_LEDGER.md` 做比对**，也不返回差异码。故本次 F-4 的核对改为「生成器指标 vs 台账文件逐项比对」（§3.4）。
- 建议：README 改为 `task_ledger.py --write` 后 `git diff --exit-code doc/TASK_LEDGER.md`，或如实描述 `--diff` 的语义。

## 5. r3 的 6 条 P2 是否全部真实关闭（逐条）

| r3 条目 | 是否真实关闭 | 本次实测依据 |
|---|---|---|
| **F-1** E-1 的 `HostRuntime.cs` 路径不存在 | **是（实质）**；字面残留见 P3-1 | 正确路径在 `4A:234`；真实文件存在且行数/类行号与注记一致；旧路径 `Test-Path`=False、`git log --all`=0；4B 两处正确路径未变 |
| **F-2** 规格 v1.1 被写成「已通过 r2 approved」 | **是** | `4A:70` 已改为 r2 覆盖 v1.9 字节/记录链、v1.1/errata 由 r3 覆盖；与载体 `:83` 同界；明确写「不得表述为 v1.1 已通过 r2」 |
| **F-3** README 三处 `pending` 反向残留 | **是** | README 全文 `pending` = 0；AC3/AC4/AC5 行为 `MET`，与载体/冻结记录一致；`:62` 已改为「复核已完成」 |
| **F-4** 台账把 4B 记为 `proposed` | **是** | 台账 `:41` 记 `in_progress` + mentioned；6 项指标与 `task_ledger.py` stdout 逐项相等（601/591/9/7/2/601/0/9）；4B 卡 `:6` = `in_progress` |
| **F-5** 4B Closeout 仍称「未释放」 | **是** | 4B `:174` = 「未关闭（当前 `in_progress`…）」；全文无「未释放」；与 `:6/:7/:8` 不再互斥 |
| **F-9** AC1 的 scope review 形式要件缺位 | **是**（裁决已在 AC1 + 4B approval 落盘）；同步缺口见 P2-1 | `4A:59` AC1 MET + 替代依据；`4B:8` 同裁决 + DSH 责任；无其他 scope review 报告，符合「替代」而非「已补做」的表述 |

**汇总：6/6 真实关闭，0 条未关闭。** 本次唯一的 P2 是**关闭动作带出的新同步缺口**（P2-1），不是任一条 P2 未处置。

## 6. 复核边界

- 本报告只对 `eae0eb67a..f3ca74a10` 的**文档/证据字节与记录链**作判断；并行 4B 第二刀的 `apps/**` 未提交改动（`HostController.cs`、`IHostController.cs`、`NullHostController.cs`、`HostRuntime.cs`、`FakeHostController.cs`）**不在**本报告范围，未被评估；仅在 §3.7 用其存在解释 inventory 门禁的工作树 EXIT=1。
- 本报告不构成对 `ListPageRegionTextsAsync` 实现的验收，不构成 80/87 已达成的声明（提交态仍是 **79/86**），不构成 `FEA-06` AC3 的状态变更（仍为 **PARTIAL**），不构成远端 push 授权。
- 本 r4 只新建 `doc/reviews/FEA-06-RESIDUAL-4A-r4.md`；未修改被审文件、未 commit/checkout/push。
- 审查者未参与该卡的写作、实现、r1、r2 或 r3 复核。
