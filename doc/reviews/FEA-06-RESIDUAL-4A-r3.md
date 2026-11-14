---
task: FEA-06-RESIDUAL-4A
task_id: FEA-06-RESIDUAL-4A
reviewer: independent sub-agent (r3, read-only, not involved in r1/r2/implementation)
reviewer_kind: subagent
base_commit: 756ab29e2f2a0039f89f696de18c09fd92368814
reviewed_head: 652580152
verdict: changes_requested
date: 2026-11-14
p0: 0
p1: 0
p2: 6
p3: 4
---

# FEA-06-RESIDUAL-4A r3：v1.1 规格定稿 + S7 扩面 errata 窄复核

## 0. 结论

**`changes_requested`。P0 = 0，P1 = 0，P2 = 6，P3 = 4。**

被审范围 `756ab29e2..652580152`（含 `5ee2db0af`、`6f9fc9f18`，及释放提交 `652580152`）。

**实质面全部通过**：规格 v1.1 的三处更正**真实落入正文**（不是只写在「r1 处置」节）；E-1 的「4 跳生产链」经源码核对**真实存在且行号精确**；E-2 的「不需要第二次 UNFREEZE」经 wire 字段面核对**成立**；inventory 字节与 pin **零变化**；四门禁**全部 EXIT=0**；被审区间**零产品代码 diff**。

**记录层仍有 6 处必须修的陈述问题**，其中 1 处是路径事实错误（E-1）、1 处是把「r2 后处置」写成「r2 已覆盖」、1 处是把 `pending` 写成已回填的反向残留（README 三处）、2 处是把「已释放」写成「未释放」（台账 + 4B Closeout）、1 处是 AC1 的 scope review 形式要件缺位却已按「冻结的规格」被消费。这些**都不触 `doc/plan/FEA-C07_API_INVENTORY.md` 字节、不改 pin、不影响 C-07 v1.9 重冻结论**，也**不要求撤回 4B 释放**；修法全是文档级一行修改。

**对 4B 的直接含义见 §6**：规格 v1.1 与 S7 errata **可以作为 4B 的实施依据**（内容上已核验有效），但上述 P2 须在 4B 的 r1 Review 引用本卡之前更正；E-1 的 `HostRuntime.cs` 路径**不可按字面照抄**。

## 1. 被审范围与审查方法

| 项 | 值 |
|---|---|
| 被审区间 | `756ab29e2..652580152` |
| 区间内提交 | `5ee2db0af`（4B 卡 + S7 errata）、`6f9fc9f18`（v1.9 重冻 + 规格 v1.1 + 载体 §6 回填）、`652580152`（释放 4B `in_progress`） |
| 被审文件 | `doc/tasks/FEA-06-RESIDUAL-4A.md`、`doc/reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md`、`doc/plan/FEA-CONTRACT-FROZEN-C07.md`、`verification/FEA-06-RESIDUAL-4A/README.md`、`doc/reviews/FEA-06-RESIDUAL-4A-r1.md`、`-r2.md`、`doc/TASK_LEDGER.md`、`doc/tasks/FEA-06-RESIDUAL-4B.md`、`doc/REBASELINE_PLAN.md` |
| 审查性质 | 只读；不参与写作/实现/r1/r2；未 checkout、未 commit、未 push |
| 方法 | 不采信卡面自述：pin 用 `Get-FileHash` 实测；4 跳链用源码逐行核对；门禁四件套现场复跑；陈述一致性用跨文件交叉比对 |

**工作树状态声明**：本会话首条命令 `git status --porcelain` 为空（干净）。审查末段工作树出现 ` M apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs`（4B 第一刀，见 4B 卡 E-3；**未提交、属他人并行工作**）。按本次任务约束，该 dirty **不计入判定**，其内容未被本报告读取或评估。

## 2. 逐项结论

| # | 复核项 | 结论 | 关键证据 |
|---|---|---|---|
| 1 | inventory 字节与 pin 未变 | **PASS** | pin = `91e51ab74d…6d750`；`git log 756ab29e2..HEAD --` 该文件为空；`verify_pins` 18/18 |
| 2 | 规格 v1.1 修订真实落入正文 | **PASS** | S1 L2 / S2 文本 / S3 null / S3 regionIds / S5 TARGET_NOT_FOUND 五处均已改写；版本行在 `:70` |
| 3 | S7 errata 合理性（E-1 链、E-2 免二次 UNFREEZE） | **PARTIAL** | 链真实、E-2 成立；**E-1 的 `HostRuntime.cs` 路径错误**（F-1） |
| 4 | 记录链自洽 | **PASS** | 载体 §6 `approved` + r1/r2 两行；冻结记录 §1/§1B/§2 条件 1/§5 同步；**v1.8 行已补**；覆盖范围声明保留 |
| 5 | 是否引入新的假陈述 | **FAIL** | F-2 / F-3 / F-4 / F-5 / F-9 共 5 处（详见 §4） |
| 6 | 4B 释放合规性 | **PASS** | PLAN `:59` 含 `FEA-06-RESIDUAL-4B(in_progress)`；PLAN 6980 B / 64 行；`check.ps1 -TaskPath` PASS |
| 7 | 门禁复跑 | **PASS** | 四项 EXIT=0（原始输出见 §5） |

## 3. 逐项证据

### 3.1 inventory 字节与 pin 未变 —— PASS

```
Algorithm : SHA256
Hash      : 91E51AB74DA201B99B6704E49FCA96E93657D869DCC1E9523661DBB299C6D750
Path      : G:\CODEX\New Manga\doc\plan\FEA-C07_API_INVENTORY.md
（文件 13040 B）
```

- `Get-FileHash -Algorithm SHA256 doc\plan\FEA-C07_API_INVENTORY.md` → `91e51ab7…d750`，与预期值**逐字符相同**（大写输出，小写等价）。
- `git log --oneline 756ab29e2..HEAD -- doc/plan/FEA-C07_API_INVENTORY.md` → **`<EMPTY>`**（整段区间未触该文件）。
- `pwsh -NoProfile -File tools\governance\verify_pins.ps1` → 18 行 `OK`，`PIN AUDIT: PASS (all 18)`，**EXIT=0**；C07 行 `91e51ab74da2`。

### 3.2 规格 v1.1 修订真实落入正文 —— PASS

复核者不采信「r1 独立复核处置」节的声称，直接比对 `756ab29e2..HEAD` 的正文 diff 与 P2-2/P2-3/P2-4 的要求：

| 位置 | v1.0（`756ab29e2`） | v1.1（`652580152`） | 对应处置 | 判定 |
|---|---|---|---|---|
| 版本行 `:70` | 无 | `**规格版本：v1.1（2026-11-14 定稿）**`，并列出 P2-3/P2-4/P2-2 三处更正 | — | **PASS** |
| S1 表 L2 行 `:77` | `Draft.Patch["text"]`（读取口径同 `ReadDraftText`） | `WorkbenchViewModel` 的**实时可编辑 `DraftText`**，并写死「**不得**取持久化 `Draft.Patch["text"]`」 | P2-4 | **PASS** |
| S2 表「文本」行 `:91` | 草稿 `patch.text` | **VM 实时 `DraftText`**（非持久化 `patch.text`；v1.1 修订） | P2-4 | **PASS** |
| S3 `null` 条 `:110` | 「空集合只表示该页真实没有区域」 | 「**空集合不能单独表示「该页无区域」**——Core 对未知 page 也返回 `regions: []`（`page_size` 为 `null`），必须结合 `page_size`/`page_id` 与 `TARGET_NOT_FOUND` 区分」 | P2-3 | **PASS** |
| S3 `regionIds` 条 `:111` | 「非空、去重、全部必须属于该页；Core 侧…返回 `TARGET_NOT_FOUND`」 | 参数**保留**但 4B 调用**一律不传**；`TARGET_NOT_FOUND` 由**本地成员判定**（`IsUiFacingFailure` 会吞 `CoreOperationException`） | P2-2 / E-2 | **PASS** |
| S5 表 `TARGET_NOT_FOUND` 行 `:132` | 「该 region 不在 L1 结果中」 | 「该 **page** 不在当前投影中（**本地判定**，非 Core 错误码）」 | P2-2 / E-2 | **PASS** |

结论：r2 的 P2-1（「规格 v1.1 未显式版本化、正文仍保留旧陈述」）与 P2-2 的**主要文本面已在正文层面关闭**，不是只存在于 append-only 处置节。**逐项 PASS**。

### 3.3 S7 扩面 errata —— PARTIAL（E-1 路径错误）

#### E-1「4 跳链」真实性 —— 链**真实**，行号**精确**，路径**错误**

| 跳 | errata 声明 | 实测 | 判定 |
|---|---|---|---|
| ① `IHostController` | `IHostController.cs` | 存在 | PASS |
| ② `HostController` | `HostController.cs:17` | `:17` = `public sealed class HostController : IHostController, ISourceImportController, IPreparedRunController, ITrashController` | **PASS（行号精确）** |
| ③ `HostRuntime` | `HostRuntime.cs:826-840` 门控样板 | `apps\desktop-avalonia\src\NewManga.Host\HostRuntime.cs:826-840` = `ListRegionsAsync`，含 `_readerIoGate.WaitAsync` / `CoreService ?? throw NotReady()` / `core.ListRegionsAsync` | **PASS（行号精确）** |
| ④ `CoreServiceClient` | `CoreServiceClient.cs:1104` 样板 | `:1104` = `public async Task<RegionPageProjection> ListRegionsAsync(` | **PASS（行号精确）** |
| 路径 | `apps/desktop-avalonia/src/NewManga.App/Services/HostRuntime.cs` | **该路径不存在**；实际在 `apps\desktop-avalonia\src\NewManga.Host\HostRuntime.cs`（2875 行，`class HostRuntime` 在 `:20`） | **FAIL（见 F-1）** |

补充实测：
- `Get-ChildItem -Recurse -Filter HostRuntime*.cs` → 仅 `NewManga.Host\HostRuntime.cs`（134124 B）与 `NewManga.Host.Tests\HostRuntimeIntegrationTests.cs`。
- `git log --all -- apps/desktop-avalonia/src/NewManga.App/Services/HostRuntime.cs` → **空**（该路径从未存在，不是「搬迁」）。
- `NewManga.App.csproj` 含 `..\NewManga.Host\NewManga.Host.csproj` 的 `ProjectReference`，故 App→Host 分层成立，**4 跳链本身无可疑**。
- errata「`CoreServiceClient` 中 `region_texts` **0 命中**」→ 实测 `Select-String -Pattern 'region_texts|RegionTexts'` 于该文件 = **`<0 HITS>`**，属**实**。`ListPageRegionTextsAsync` / `RegionPageTextProjection` 在全 `src/**` 的命中只有 `RegionTextProjection.cs`（解析器，4 处），端口确实未落地。

#### E-2「不需要第二次 UNFREEZE」—— 成立

| 声明 | 实测 | 判定 |
|---|---|---|
| 端口不传 `regionIds`，整页一次 | 与 S1-a「一页一次」一致，S3 `:111` 已写死 | PASS |
| `TARGET_NOT_FOUND` 由本地成员判定 | S3 `:111` + S5 `:132` 一致，未引入 wire 码 | PASS |
| 方法名 / 返回类型不变 | inventory 计划节只锁 `ListPageRegionTextsAsync` + `Task<RegionPageTextProjection?>`（`FEA-C07_API_INVENTORY.md:146`）；errata 未改这两项 | PASS |
| 统计不变（仍 1 方法 / 79 / 86） | `--check` 实测 `1 / 79 / 6 = 86`；端口调用时是否传可选参数**不改变接口方法计数** | PASS |
| 依据成立性 | `HostCommandDispatcher.cs:868-871` = `page_id`（必填）+ 可选 `region_ids`，**无 `expected_revision`**；`:864-867` 注释明写「Core additionally proves each id is a live region of that page (TARGET_NOT_FOUND otherwise)」→ 传 `regionIds` 确实可能引出 `TARGET_NOT_FOUND`；`HostController.cs:2932` = `private static bool IsUiFacingFailure(Exception ex) => ex is`（吞异常样板），errata 引用**准确** | PASS |

**结论**：E-2 的「零额外 UNFREEZE」判断**可成立**（不改签名、不改返回类型、不改统计、不动 wire 命令面）。E-1 的**结论**（扩面 2 个生产文件）**可成立**，但**文字中的路径须更正**。

### 3.4 记录链自洽 —— PASS

| 检查点 | 实测 | 判定 |
|---|---|---|
| 载体 §6 由 `pending` 改为 `approved` | `:72` `**状态：`approved` —— 本 UNFREEZE 已生效并重冻（2026-11-14）。**` | PASS |
| 含 r1/r2 两行（身份/被审 head/结论/P 计数） | `:76` r1 = `451313d2…`/`7c1ac472f`/`changes_requested`/`0/2/7/5`；`:77` r2 = `8389f5bc…`/`756ab29e2`/`approved`/`0/0/2/5`，两行均带门禁列 | PASS |
| 冻结记录 §1 pin 行 | 与 `91e51ab7…` 一致，含「r2 `approved`…**已重冻**」 | PASS |
| §1B r2 行 | `v1.9：r1 changes_requested → 处置 → r2 approved（被审 head `756ab29e2`），已重冻` | PASS |
| **§1B 补上 v1.8 行（r1 P3-1）** | `:33`「复核后到冻结的改动」旧值为 `…v1.7…；v1.9…`（**缺 v1.8**），新值插入「**v1.8：AI-1 统计 79/86 + P21–P25 成员表并入（S5 节 25/25 全落地）**」 | **PASS（真实补上）** |
| §2 条件 1 | 由 `✅（v1.9 ⏳ pending）` → `✅` + 证据列写明 r1→r2→已重冻 | PASS |
| §5 v1.9 行 | 由「**独立字节级复核 r1 changes_requested**」→「r1→处置→r2 approved，已重冻」；署名 `residual-4a（DSH 派出）；重冻 DSH` | PASS |
| 覆盖范围声明保留 | 载体 `:83` blockquote 完整保留，明确 r2 `reviewed_head` = `756ab29e2`、「规格 v1.1 与 S7 errata 属 r2 后处置」 | **PASS（未被删）** |

### 3.5 4B 释放合规性 —— PASS

| 检查点 | 实测 | 判定 |
|---|---|---|
| 卡面 `status: in_progress` | `doc/tasks/FEA-06-RESIDUAL-4B.md:6` | — |
| 是否出现在 PLAN 当前 DAG | `doc/REBASELINE_PLAN.md:59`「表外节点…非终态 **FEA-06-RESIDUAL-4B(in_progress)**」 | **PASS**（位置是「当前活动程序」的表外节点声明，非 DAG 表行；`check.ps1 -TaskPath` 三次均接受） |
| PLAN 预算 | **6980 B / 64 行** → 字节 ≤7000 ✅、行数 ≤64 ✅（门禁自报已达 80% 预算：`6980 bytes / 64 lines`） | **PASS** |
| `check.ps1 -TaskPath 4B` | `PASS (3 warnings)` / **EXIT=0** | PASS |
| 释放前置（R-7：4A r2 approved + v1.9 重冻） | 均满足 | PASS |

### 3.6 门禁四件套 —— PASS（原始输出见 §5）

## 4. 问题清单

> 级别口径沿用 r1/r2：P0 = 破坏冻结字节/安全；P1 = 记录层假陈述且阻断重冻或实施；P2 = 应修、不单独阻断重冻但会在下游被引用；P3 = 登记/不修。**本轮 P2 属「必须在 4B 的 r1 Review 引用本卡前修」的口径，不是「必须撤回 4B 释放」的口径。**

### P2（6 项）

**F-1｜E-1 的 `HostRuntime.cs` 路径不存在（事实错误）**
- **位置**：`doc/tasks/FEA-06-RESIDUAL-4A.md:234`（`### E-1`）——「S7 允许面扩充为包含 `apps/desktop-avalonia/src/NewManga.App/Services/HostRuntime.cs` 与 `apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs`」。
- **实测**：该路径不存在；真实文件 `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`（2875 行，`public sealed class HostRuntime` 在 `:20`）；`git log --all --` 该 App 路径为空（从未有过），排除搬迁解释。
- **为何是 P2 而非 P3**：E-1 的**唯一内容**就是「往 4B 的 `allowed_paths` 里加哪两个路径」。路径错 = 裁决结论不可照抄。若后续卡/复核按 E-1 字面核对 4B 的 `allowed_paths`，会把**正确**的 `NewManga.Host/HostRuntime.cs` 判成越界，或把不存在的路径当成漏改。
- **缓解事实**：4B 卡**没有**照抄——`allowed_paths:30` = `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`，`§允许修改范围:107` = `src/NewManga.Host/HostRuntime.cs`，**两处均正确**。故**不阻断 4B 实施**。
- **修法**：E-1 内两处 `NewManga.App/Services/HostRuntime.cs` → `NewManga.Host/HostRuntime.cs`（一行）。

**F-2｜规格 v1.1 被写成「已通过 r2 独立复核 `approved`」，越界覆盖**
- **位置**：`doc/tasks/FEA-06-RESIDUAL-4A.md:70`——「**规格版本：v1.1（2026-11-14 定稿）**…**已通过 r2 独立复核 `approved`（P0=0/P1=0）**」。
- **矛盾证据**：① r2 报告 front matter `reviewed_head: 756ab29e2`；② r2 报告 `P2-1` 明文「『规格 v1.1』**未显式版本化**」——即 r2 复核时 v1.1 **尚不存在**；③ 载体 §6 覆盖范围声明（`:83`）明文把 v1.1 定为「**r2 后处置**」「待…r3 窄复核覆盖」。
- **性质**：正是任务项 5 点名的「把『r2 后处置』说成『r2 已覆盖』」。该句紧跟在 v1.1 描述之后，读者会读成「v1.1 字节已被 r2 批准」。
- **修法**：改为「规格 **v1.0** 已通过 r2 复核；**v1.1 正文修订**属 r2 后处置，由 r3 窄复核覆盖（见 `FEA-06-RESIDUAL-4A-r3.md`）」。

**F-3｜证据 README 三处仍写 `pending`，与回填后的状态相反**
- **位置**：`verification/FEA-06-RESIDUAL-4A/README.md`
  - `:15`（AC3 行）「§1B 记为「**独立复核 pending**」」——实际 §1B 已记 r2 `approved`。
  - `:16`（AC4 行）「§6 复核记录为 `pending`」——实际 §6 已 `approved`。
  - `:62`（未做/NOT_RUN）「**独立字节级复核 NOT_RUN**：AC5 `pending`，须 DSH 另派…」——与本文件 `:17`（AC5 = **MET**）**同一文件内直接矛盾**。
- **性质**：任务项 5 点名的「`approved` 被写成未复核」。范围 `756ab29e2..HEAD` 的 README diff **只改了 `:17` 的 AC5 行**，`:15`/`:16`/`:62` 为未同步的上下文行。
- **附带**：`:39`「`PLAN` 6954 B、8 个非终态 Task」已过时（现 6980 B / 9），属同源陈旧（P3 级，合并处理即可）。
- **修法**：三处改为已回填事实；`:39` 数字更新或标注「当时实测」。

**F-4｜`TASK_LEDGER` 把已释放的 4B 记为 `proposed`**
- **位置**：`doc/TASK_LEDGER.md:46` = `` | `FEA-06-RESIDUAL-4B` | `proposed` | no | ``。
- **矛盾证据**：`doc/tasks/FEA-06-RESIDUAL-4B.md:6` = `status: in_progress`；`652580152` 的 diff 显示 `status: proposed` → `in_progress`（同时改 `disposition`/`approval`），但该提交**只改 2 个文件**（PLAN + 4B 卡），**未重跑** `python tools/governance/task_ledger.py --write`。台账的 per-task 状态行直接取卡面，故为机械性失配。
- **为何门禁没抓到**：`proposed` 与 `in_progress` **同为非终态**，`task files 601` / `non-terminal 9` 计数不变；`check.ps1` 只对齐计数（`:272-283`），不逐行比对 per-task 状态 ⇒ 三名门禁全绿仍掩盖了该漂移。
- **性质**：任务项 5 的「已释放被写成未释放」。「`doc/TASK_LEDGER.md`」在 4B 的 `allowed_paths` 内且卡面 `:111` 已预告「迟早必然失配」，属应立刻机械重生成的一项。
- **修法**：取得 DSH 授权后 `python tools/governance/task_ledger.py --write` 一次（**不得手写**）。

**F-5｜4B 卡 Closeout 仍称「未释放」**
- **位置**：`doc/tasks/FEA-06-RESIDUAL-4B.md:174`——「Closeout date / DSH：待关闭时填写（当前 `proposed`，**未释放**）」。
- **矛盾证据**：同文件 `:6` `status: in_progress`、`:8` `approval: DSH 2026-11-14 释放（前置已满足…）`、`:7` disposition「2026-11-14，DSH 释放」。
- **性质**：同卡内 front matter 与正文互斥；`652580152` 只翻了 front matter 三行，未同步 Closeout。属「假陈述」清单项。
- **修法**：改为「当前 `in_progress`，2026-11-14 由 DSH 释放；关闭时填写」。

**F-9｜AC1 的 scope review 形式要件缺位，但规格已被按「冻结」消费**
- **位置**：`doc/tasks/FEA-06-RESIDUAL-4A.md:59`（AC1 仍 `[ ]` + `<<PARTIAL: 规格 v1 已落卡面；冻结待独立 scope review>>`）；对照 `doc/tasks/FEA-06-RESIDUAL-4B.md:7` disposition「消费 `FEA-06-RESIDUAL-4A` **冻结的规格 v1.1**」。
- **实测**：`doc/reviews/` 下与 4A 相关的报告只有 r1、r2（字节级）与本 r3；**没有任何独立 scope review 报告**。4A 卡自己的 `:193`「下一步①」仍把「DSH 独立 scope review 本卡规格与预授权（`proposed` → `ready` 前必须有）」列为待办。
- **性质**：AC1 自定的冻结判据是「独立 scope review 通过」，该判据未发生；4B 却已称该规格为「冻结」。这不是字节问题，但属「省略的形式要件被当成已完成」。
- **修法（DSH 二选一）**：① 补一份独立 scope review 并回填 AC1；或 ② 显式裁决「以 r2 + r3 字节级复核替代 AC1 的 scope review」，把 AC1 结案并写明替代依据。**建议 ②**（4B 已释放，重开 scope review 成本高于收益）。

### P3（4 项，登记）

**F-6｜4A 卡 AC 行残留过期标记**
- `:63` AC5：复选框 `[x]` + 标题 `<<MET>>`，但行尾仍是 `` `<<PENDING: 未派发>>` ``（`756ab29e2→HEAD` 的 diff 未删该标记）→ 同一行内互斥。
- `:61` AC3：`<<PARTIAL: … §1B 复核列仍为 pending>>`；`:62` AC4：`<<PARTIAL: 载体已落盘；§6 复核记录待独立复核回填>>` → 两者均已被 `6f9fc9f18` 回填，标记未随之更新。
- 另 `:64` AC6 的 `<<PARTIAL: … 剩余闭合动作＝AC5 独立复核后由 DSH 复跑确认>>` 因 AC5 已关闭而过期。

**F-7｜载体覆盖范围声明的时序承诺被违反**
- 载体 `:83` 写「（v1.1 与 S7 errata）…**待 4B 释放前**由一次 r3 窄复核覆盖」；但 `652580152` 已在 r3 之前把 4B 置为 `in_progress`。
- 判定：**承诺未兑现**，不是假陈述（该句没有声称已覆盖），且本 r3 已事后补上覆盖。建议把该句改为过去时并指向 `FEA-06-RESIDUAL-4A-r3.md`，注明「r3 在 4B 释放后完成」。

**F-8｜4A 卡「下一步」未同步已完成项**
- `:193` 仍写「① scope review → ② 另派复核回填 → ③ 重冻 → ④ 释放 4B」为待办，而 ②③④ 已由 `6f9fc9f18`/`652580152` 完成；同卡 `:192`「未做（交付时）」却已更新为「已于 2026-11-14 完成」→ 同一小节内部前后不一致。

**F-10｜README 门禁描述的数字过时**
- `README:39`「`PLAN` 6954 B、8 个非终态 Task」；实测 6980 B / 9。属历史实测值，与 F-3 一并处理即可。

### 复核实测的「无问题」项（明确记录，避免过度报告）

- `doc/REBASELINE_PLAN.md` 已把 `BLOCKED：无；REVIEW：无` 合并为 `BLOCKED/REVIEW：无` 并塞入 4B，**未超行数/字节预算**。
- 区间内 `src/**`、`apps/**`、`tests/**` diff = **`<NONE>`**（零产品代码改动，符合 4A 的 `out_of_scope`）。
- 4B 卡的 `allowed_paths` 不含任何 `src/**`（Core），`out_of_scope` 明确「零 Core 改动」。
- 载体 §7「不构成什么」仍保留「不构成实现授权 / 不构成 80-87 已达成（当前仍是 79/86）」等边界，未被重冻动作吹掉。

## 5. 门禁复跑（真实输出与 EXIT）

工作目录 `G:\CODEX\New Manga`，HEAD `652580152`，审查开始时 `git status --porcelain` 为空。

### ① `pwsh -NoProfile -File tools/governance/check.ps1`

```
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\MAINT-1-RELEASE-MONITOR.md
WARN: 存在 9 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3177 bytes / 32 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6980 bytes / 64 lines
Governance check: PASS (3 warnings)
EXIT=0
```

### ② `check.ps1 -TaskPath doc/tasks/FEA-06-RESIDUAL-4A.md`

```
Task: doc\tasks\FEA-06-RESIDUAL-4A.md
WARN: 存在 9 个非终态 Task（…）；WARN: STATUS 3177 bytes / 32 lines；WARN: PLAN 6980 bytes / 64 lines
Governance check: PASS (3 warnings)
EXIT=0
```

### ③ `check.ps1 -TaskPath doc/tasks/FEA-06-RESIDUAL-4B.md`

```
Task: doc\tasks\FEA-06-RESIDUAL-4B.md
WARN: 存在 9 个非终态 Task（…）；WARN: STATUS 3177 bytes / 32 lines；WARN: PLAN 6980 bytes / 64 lines
Governance check: PASS (3 warnings)
EXIT=0
```

### ④ `pwsh -NoProfile -File tools/governance/verify_pins.ps1`

```
OK C01b 3c9f5af7d74f … OK C17 cdeee4872e29 … OK FEA01 0370c18932b1
PIN AUDIT: PASS (all 18)
EXIT=0
```

### ⑤ `python tools/generate_api_inventory.py --check`

```
| IReaderProgressSink | 1 | 0 |   | IHostController | 79 | 4 |   | IRunController | 6 | 0 |   | **合计** | **86** | — |
OK: rendered counts match FEA-C07 doc
EXIT=0
```

### ⑥ 附加只读测量

```
(Get-Item doc\REBASELINE_PLAN.md).Length   → 6980
(Get-Content doc\REBASELINE_PLAN.md).Count → 64
git diff --name-only 756ab29e2..HEAD -- src apps tests → <NONE>
git show 5ee2db0af:doc/tasks/FEA-06-RESIDUAL-4B.md | status → proposed
Select-String doc\tasks\FEA-06-RESIDUAL-4B.md -Pattern '^status:' → in_progress
```

## 6. 明确回答：4A 的规格 v1.1 与 S7 errata 是否可作为 4B 的实施依据

**可以，且内容上已核验有效。** 但附 3 条前置更正 + 1 项形式要件裁决。

### 6.1 为什么「可以」（逐项判据）

1. **规格 v1.1 正文已实**（§3.2）：S1 L2 / S2 文本 / S3 `null` / S3 `regionIds` / S5 `TARGET_NOT_FOUND` 五处均与 P2-2/P2-3/P2-4 一致，版本行在 `:70`。4B 可直接据以派生测试，无需回 4A 改规格。
2. **E-2 的口径闭合**（§3.3）：不传 `regionIds` ⇒ 方法名、返回类型 `Task<RegionPageTextProjection?>`、统计（1 方法 / 79 / 86）与 wire 命令面**全部不变** ⇒ **确实不需要第二次 UNFREEZE**；`HostCommandDispatcher.cs:868-871` 与 `HostController.cs:2932` 的引用准确。
3. **E-1 的扩面结论必要且正确**（§3.3）：4 跳链真实（`:17` → `HostRuntime:826-840` → `CoreServiceClient:1104`），`CoreServiceClient` 中 `region_texts` 0 命中属实，故 4B **必须**改 `HostRuntime.cs` 与 `CoreServiceClient.cs`；4B 卡已把两者写入 `allowed_paths`（`:30`/`:31`）。
4. **契约基线干净**（§3.1）：inventory 字节未变、pin 仍 `91e51ab7…`、18/18、零产品代码 diff、四门禁全绿。4B 可在不重开 UNFREEZE 的前提下实施。
5. **实施顺序可执行**（errata E-3）：先 `CoreServiceClient` wire + 解析测试 → 再 Host 三处实现 + UI → 最后统计翻转 80/87 + pin v1.10，与 4B 卡 AC1/AC2 的写法一致；且当前工作树已出现 `CoreServiceClient.cs` 未提交改动，与该顺序吻合。

### 6.2 作为实施依据前必须做的 3 条更正

| # | 动作 | 理由 |
|---|---|---|
| 1 | 更正 E-1 的 `HostRuntime.cs` 路径 → `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs` | 现文本指向不存在的文件；4B 的 r1 Review 若按 E-1 字面核对 `allowed_paths` 会误判越界或漏改（F-1） |
| 2 | 更正 4A `:70` 的「v1.1 已通过 r2 approved」表述 | 现文本把 r2 后处置写成 r2 已覆盖，是本项目已两次（r1 P1-1、r2 P2-1）栽过的同一类记录层错误（F-2） |
| 3 | 同步 README `:15`/`:16`/`:62` 与 4B Closeout `:174`；`task_ledger.py --write` 一次 | 消除「approved 写成 pending」「in_progress 写成 proposed/未释放」的 5 处反向陈述（F-3/F-4/F-5） |

以上 3 条**全部为文档级**，不动 `doc/plan/FEA-C07_API_INVENTORY.md`、不动 pin、不动产品代码；修完**无需**再重冻 C-07，也**无需**撤回 4B 的 `in_progress`。

### 6.3 1 项形式要件需 DSH 裁决

AC1 自定的「规格冻结以**独立 scope review** 通过为准」**尚未发生**（`doc/reviews/` 无此类报告），而 4B 已按「冻结的规格 v1.1」消费（F-9）。建议 DSH 显式裁决「以 r2 + r3 的独立字节级复核替代 scope review」并把 AC1 结案，或在 4B 关闭前补一份 scope review 记录。**在裁决落地前，4B 卡 `disposition` 中「冻结的规格」一词属未兑现的自述。**

### 6.4 不阻断但需在 4B 内继承的约束

- 4B 不得因 E-2 的「本地判定」而把 wire `TARGET_NOT_FOUND` 语义重写为面板码；面板码仍属 UI 本地原因码闭集（P2-5：不得进 `DraftErrorMap` 19 键）。
- 4B 的 AC4 已把「`[]` + `page_size: null`」定为 `TARGET_NOT_FOUND` 失败态，而 r1 的 P2-3 曾要求「不得把空集合升级为 typed 错误」。这是 **4A 对 r1 建议的事实修订**，且 r2 的 P2-2 要求这种情形「须说明是显式修订，而不是静默改写」。当前 S3 只写「必须结合 `page_size`/`page_id` 与 `TARGET_NOT_FOUND` 区分」，判定规则实际落在 4B 卡的「**调用口径（本卡定）**」 → **建议 DSH 在 4A 补一句显式裁定**（不阻断实施，登记为 P3 观察项，不计入上表 P3 计数以免与 F-6…F-10 混淆）。

## 7. 复核边界声明

- 本报告只对 `756ab29e2..652580152` 的**文档字节与记录链**作出判断；4B 实施中的 `CoreServiceClient.cs` 未提交改动**不在**本报告范围，未被读取或评估。
- 本报告不构成对 `ListPageRegionTextsAsync` 实现的验收，不构成 80/87 已达成的声明（**当前仍是 79/86**），不构成 `FEA-06` AC3 的状态变更（仍为 **PARTIAL**），不构成远端 push 授权。
- 本 r3 只新建 `doc/reviews/FEA-06-RESIDUAL-4A-r3.md`；未修改被审文件、未 commit/checkout/push。
- 审查者未参与该卡的写作、实现、r1 或 r2 复核。
