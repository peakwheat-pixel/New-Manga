---
task: FEA-11-WATCH-1
title: FEA-11-WATCH-1 r3 窄面复审（fresh subagent；r2b 测试真实性返修核销 + closeout 收口）
reviewer: fresh subagent（独立上下文；未参与 FEA-11/WATCH-1 任何实现、r1 或 r2 复核）
session: 13663da1-2f1a-4fff-a95f-2965a589ae29
parent_session: session-8db9dae5-49df-4d09-ac62-696f0805a95c
date: 2026-11-06
timezone: Asia/Shanghai
repo: G:\CODEX\New Manga
branch: main
worktree: clean（review 结束时）
base: 919c9aa1e
implementation_chain: e60105cf9（r1 feat）→ 19a2af7f3（r2 fix）→ 00083a977（r2b test）
r2b_docs_commit: 4da7a2105
integration_head_under_review: e1036e561
reviewed_head: e1036e561727421975c4640753fa7a2f3b456316
decision: APPROVE
findings: P0=0 / P1=0 / P2=0 / P3=6（均为文档/证据收尾项，不阻断代码与门禁结论）
---

# FEA-11-WATCH-1 r3 窄面复审

> **结论先行：`APPROVE`（P0=0 / P1=0 / P2=0 / P3=6 观察项）。**
>
> r2 的两条 P2 已在 `00083a977` 真正落地，并由我在**隔离运行**下独立复现：
> ① `RootLost_IsDegraded_AndReArmsOrCountsUncovered` 已是严格断言
> `Assert.Equal(0, status.Active)` + `Assert.True(status.Uncovered >= 1)`（`SourceWatcherTests.cs:607-608`，
> 无恒真残留）；② 末行 Tick 前有 `await fixture.Scheduler.HintIdleAsync();`（同文件 `:613`），
> 该用例隔离重跑 **5/5 全绿**；③ r2b 无任何 `src/` 改动，产品语义与 r2 已独立证实的 P1/P2 修复逐字节未变。
>
> 门禁独立复跑：Host **185/0/55**；全量 .NET 首跑命中**已知** `verification/FEA-09` flaky（1 failed），
> 恢复后 RUN2 **1527/0/86**；check **PASS（3 warnings）**、pins **18/18**、API **PASS**、
> scope diff **0 行**、卡面 EV **19/19** 哈希逐项一致。
>
> 文档更正总体如实：record §7.3/§7.5 已明确改成「**r2b 才落地**」，卡 r2b 段与 Handoff §9 一致；
> 但留下 6 个 P3 收尾项（record §5 的 check.log 哈希与已提交文件不符、卡 r2 历史段/Handoff §8 仍保留
> 「r2 已修」表述、卡面第 200 行字面 `\n`、EV 表 AC/Gate 列被收敛、卡面 `ready` 横幅、Resource Manifest
> 路径与实际不符），建议在 closeout 提交中一并修正（详见 §5）。**不阻断 closeout。**
>
> 本 review 只读：未修改仓库、未 commit、未 push；全部复核产物写在
> `G:\CODEX\New Manga.workspace\FEA-11\review-watch-1-r3\`。

---

## 1. 只读核验基线

| 项 | 事实 | 证据 |
|---|---|---|
| HEAD / reviewed_head | `e1036e561727421975c4640753fa7a2f3b456316`（`docs(fea-11-watch-1): r2b 集成…待 r3 窄面复审`） | `git rev-parse HEAD` |
| 实现链 | `e60105cf9`（feat）→ `19a2af7f3`（r2 fix）→ `00083a977`（r2b test）→ `4da7a2105`（docs 回填）→ `e1036e561`（r2b 集成） | `git log --oneline 919c9aa1e..HEAD` |
| 工作树 | 开始/结束时 `git status --porcelain` 均空；我复跑全量后已 `git checkout -- verification/FEA-09` | 实跑 |
| 未 push | `git branch -r --contains 00083a977/e1036e561` 均为空；`origin/main = b1c1f5a56`（本地领先） | 实跑 |
| r2b 改动面 | `git diff --name-only 1e79cfe50..HEAD` = 测试 1 文件 + 卡/Handoff + verification；`git diff --name-only 00083a977..HEAD -- apps/desktop-avalonia/src` = **空** | 实跑 |
| 产品源码字节 | `SourceWatcher.cs` `52cf4575…`、`SourceScanScheduler.cs` `0e8e3ddb…` 与 `19a2af7f3`（r2 fix 头）逐字节相同 | SHA256 对照 |
| 契约/schema/依赖 | `git diff --name-only 919c9aa1e..HEAD -- doc/plan doc/contracts src/` = **0 行**；`*.csproj/*.props/*.targets/*.sln/*.lock` 无变化 | 实跑 |
| AC11-1 | `doc/tasks/FEA-11.md:103` 仍 `- [ ]`，仍带 `<<PARTIAL…>>`；本卡未回填 | 只读 |
| L10 | 未解决；`919c9aa1e..HEAD` 无 RENDITION/L10 实现或任务新增 | 只读检索 |
| 审查者独立性 | r3 fresh subagent；未参与实现、r1、r2；只读仓库 | 本会话 |

---

## 2. r2 findings 核销（逐项对字节，不采信 Owner 日志）

### 2.1 P2-1 严格断言 —— **已落地，可判别**

`apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceWatcherTests.cs:603-609`（当前 HEAD）：

```csharp
var status = watcher.Status();
Assert.True(status.Degraded);
// r2b P2-1: strict discriminator (the previous `|| Active >= 0` was always true). The lost root
// is disarmed AND counted uncovered; a real re-arm is impossible because the directory is gone.
Assert.Equal(0, status.Active);
Assert.True(status.Uncovered >= 1);
Assert.NotNull(fixture.Scheduler.Snapshot().Watcher);
```

- `apps/desktop-avalonia` 全树检索 `Active\s*>=\s*0` / `Uncovered\s*>=\s*1\s*\|\|`：**仅命中注释行 605**，无恒真断言残留。
- `Assert.Equal(0, status.Active)` 与 `Assert.True(status.Uncovered >= 1)` 均非恒真；r2 独立探针已测得该场景
  `Active=0, Uncovered=2`，与断言一致（r2 报告 §3.3）。
- 判定：**r2 P2-1 已修复**。

### 2.2 P2-2 单飞 gate 时序 —— **已落地**

同文件 `:610-614`：

```csharp
// r2b P2-2: the root-lost all-target hint pass occupies the single-flight gate, so a manual
// TickAsync right after would legitimately merge (false). Drain it first (same as overflow test),
// then the periodic path is verified to still run.
await fixture.Scheduler.HintIdleAsync();
Assert.True(await fixture.Scheduler.TickAsync());
```

- `SourceScanScheduler.HintIdleAsync()`（`:431-437`）返回当前 `_hintTask`；提示 pass 完成后释放 `_tickGate`，
  因此随后 `TickAsync()` 可正常执行——与 `Overflow_RespectsBudget_AndCompletesAcrossTicks`（`:572/579`）同一模式。
- 该用例隔离运行结果：**5/5 全绿**（§3.1），与 `logs/r2b-rootlost-isolated.log` 的 5/5 一致；
  r2 记录的“无该行时隔离 5/5 红”由 r2 探针独立证实（r2 报告 §3.3）。
- r2b 无 `src/` 改动（§1），产品语义未变；r2 已独立证实的 P1（hint pass 起点）与 P2（撤销后拆除）代码字节未变。
- 判定：**r2 P2-2 已修复**。

### 2.3 “r2 误述 → r2b 才落地”的文档更正

| 位置 | 当前表述 | 与字节/事实一致性 | 判定 |
|---|---|---|---|
| 卡 `## r2b 测试真实性返修`（`:149-156`） | 「P2-1 已修…；record §7.3/§7.5 更正 r2 阶段“已修”误述」 | 与代码（`:607-608`、`:613`）一致 | ✅ 如实 |
| record §7.3（`:136`） | 「P3-3 RootLost 恒真断言…**r2b 才落地**（r2 commit message 曾误称已修）」 | 与代码一致；明确更正归因 | ✅ 如实 |
| record §7.5（`:153-160`） | P2-1/P2-2 根因、修复、5/5、无 src 改动 | 与代码/日志一致；但 §7.5 内「check PASS（3 既有 warnings）」与已提交 `check.log` 的 4 warnings 不一致（见 P3-1） | ✅/⚠️ |
| Handoff §9（`:100-105`） | 「r2 的 commit message/record 曾误称已改，record §7.5 已显式更正」 | 如实 | ✅ 如实 |
| Handoff §8（`:93-98`） | 历史段仍写「P3-3 RootLost 严格断言（Active=0 && Uncovered≥1）」 | 历史段未加更正脚注（见 P3-2） | ⚠️ 历史表述 |
| 卡 `## r2 返修`（`:140-146`） | 历史段仍写「`RootLost` 严格断言 `Active==0 && Uncovered>=1`」 | 同上（见 P3-2） | ⚠️ 历史表述 |
| `gates.log` §7（`:39-44`） | r2b 隔离 5/5、185/0/55、1527/0/86、check/pins/API/scope | 与我复跑一致 | ✅ 如实 |
| 卡 EV 表（`:162-180`） | EV-01…EV-19 | 19/19 哈希与工作区逐项一致；但 AC/Gate 列全部收敛为 `AC-W1/2/3/4`（见 P3-4） | ✅/⚠️ |

**结论**：r2b 段、record §7.3/§7.5、Handoff §9 的更正**如实**，不再把“r2b 的代码落地”算到 r2 头上；
仅卡 `## r2 返修` 与 Handoff §8 作为**历史段**保留旧表述（由后置 erratum 覆盖），列 P3-2 建议补脚注。

---

## 3. 独立复跑（全部实跑；日志在仓外 `review-watch-1-r3\`）

环境：`dotnet 10.0.401`；仓库 `main`；Release；先 `dotnet build apps/desktop-avalonia/NewManga.sln -c Release`
（0 warnings / 0 errors）。

### 3.1 RootLost 用例隔离 ×5

命令（每次单用例）：

```text
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj \
  -c Release --no-restore --no-build \
  --filter "FullyQualifiedName~RootLost_IsDegraded_AndReArmsOrCountsUncovered"
```

| 运行 | 结果 |
|---|---|
| run 1 | 已通过 1 / 0 / 0，57 ms，EXIT 0 |
| run 2 | 已通过 1 / 0 / 0，54 ms，EXIT 0 |
| run 3 | 已通过 1 / 0 / 0，54 ms，EXIT 0 |
| run 4 | 已通过 1 / 0 / 0，55 ms，EXIT 0 |
| run 5 | 已通过 1 / 0 / 0，54 ms，EXIT 0 |

日志：`rootlost-isolated-5x-clean.log`（另有含首次构建的 `rootlost-isolated-5x.log`）。
与 `verification/FEA-11-WATCH-1/logs/r2b-rootlost-isolated.log`（EV-15，`3d17ea50…`）的 5/5 结论一致。

### 3.2 门禁

| 门禁 | 期望（卡面/record） | 我的独立结果 | 证据 |
|---|---|---|---|
| Host 单测全量 | 185/0/55（240） | **185 / 0 / 55（240）**，8 s，EXIT 0 | `host-full.log` |
| 全量 .NET RUN1 | 1527/0/86 | **1526 / 1 / 86**，EXIT 1 —— 命中**已知** `FEA-09` flaky：`NewManga.App.Tests.FluentResidual2VisualEvidenceTests.Captures_Residual2_Visual_Inventory_Only_When_Opted_In` 断言 `git status` 期望空、实际 `M verification/FEA-09/logs/wire-redacted.ndjson`（用例自身等待 23 s） | `dotnet-full-run1.log` |
| 全量 .NET RUN2（RUN1 后恢复 `verification/FEA-09`） | 1527/0/86 | **1527 / 0 / 86**，EXIT 0（21+38+253+117+31+185+167+715；skipped 55+24+7=86）；跑后再恢复 FEA-09，工作树 clean | `dotnet-full-run2.log` |
| `check.ps1 -TaskPath doc/tasks/FEA-11-WATCH-1.md` | PASS（3 既有 warnings） | **PASS (3 warnings)**，EXIT 0（非终态 Task 9 / STATUS 80% / PLAN 80%） | `check-taskpath.log`（`2afe8d24…`） |
| `verify_pins.ps1` | 18/18 | **PIN AUDIT: PASS (all 18)**，EXIT 0 | `pins.log` |
| `generate_api_inventory.py --check` | PASS | **OK: rendered counts match FEA-C07 doc**（61 接口），EXIT 0 | `api-inventory.log` |
| scope diff `919c9aa1e..HEAD -- doc/plan doc/contracts src/` | 空 | **0 行** | 实跑 |
| 卡面 EV-01…EV-19 sha256 | 19 行 | **19/19 逐项重算一致** | 实跑（见下） |

补充：
- 全量 RUN1 的 flaky 属 r1/r2 已记录的 `verification/FEA-09` 证据路径竞态（套件运行期间
  `wire-redacted.ndjson` 变为 dirty，用例断言 `git status` 为空而失败），与本卡 Host watcher 代码无关；
  按 r3 要求“首跑 flaky 复跑并记录”执行，恢复 FEA-09 后 RUN2 全绿。
- pytest 未复跑（r3 窄面不要求；本卡零 Python；EV-13/EV-14 为 r2 实跑证据，哈希已核）。
- gated HostRuntime（1/0/0）未复跑（需真实 sidecar，r3 窄面未要求）。

**EV 19 行复算**（卡面 `:162-180`，工作区 clean 即 HEAD 字节）：全部一致，包括
`changed-files.txt bec9d211…`、`host-watch-runtime.json 25baaac0…`、`api-inventory.log b4b9e68e…`、
`check-post-commit.log db8a4a52…`、`check.log ed28ade7…`、`dotnet-full-1/2 c465cf51…/55d15767…`、
`gates.log 4bbb3da7…`、`mutation-m1/2/3 5f4560d2…/8d7336cd…/d045f863…`、`pins.log f198eda4…`、
`pytest-full db330f47…`、`pytest-summary 57d272da…`、`r2b-rootlost-isolated 3d17ea50…`、
`watcher-runtime d6fe979a…`、`watcher-unit b8115d59…`、`record.md b99b2675…`、`scope-validation efb88360…`。

---

## 4. 范围与纪律

| 项 | 结论 |
|---|---|
| r2b `00083a977` 改动面 | 仅 `SourceWatcherTests.cs`（+6/−2 行：2 行断言 + 1 行 HintIdleAsync + 注释）与卡/Handoff/verification；`git diff 1e79cfe50..00083a977` 无 `src/`、无 App/Core、无契约/schema/依赖、无 STATUS/PLAN/LEDGER/reviews |
| `4da7a2105` / `e1036e561` | 仅卡 + Handoff（docs 回填/集成）；未改代码与产品源 |
| 依赖 | 无 `*.csproj/*.props/*.targets/*.sln/*.lock` 变化；仍只有 BCL `System.IO.FileSystemWatcher` |
| 未 push | 远程分支不含 `00083a977`/`e1036e561`；`origin/main=b1c1f5a56` |
| 工作树 | review 开始时 clean；全量 .NET RUN1 后出现 `M verification/FEA-09/logs/wire-redacted.ndjson`，已恢复；结束时 clean |
| AC11-1 | 仍 `- [ ]` + `<<PARTIAL…>>`；卡面/record/Handoff 均声明不回填 |
| L10 | 未解决；无 RENDITION 实现/任务新增 |
| RH-3 | 未修（target 集只增不减），与 limitation 一致 |
| 真实数据/资源 | 仅隔离 temp 根与仓库测试；未触碰用户数据/AppData/外部卷；仓外产物只在 `G:\CODEX\New Manga.workspace\FEA-11\review-watch-1-r3\` |

---

## 5. Findings（P3×6，均不阻断；建议 closeout 一并收尾）

### P3-1（证据打包）`record §5` 的 `check.log` 哈希与**已提交文件**不一致

- 事实：record §5 记 `logs/check.log = 2afe8d249b29…`，但 HEAD 中该文件实际为
  `ed28ade75e02…`（4 warnings：包含“`evidence_dir 含未登记过程文件 …check-post-commit.log`”）。
- 我在 HEAD 重跑 `check.ps1 -TaskPath`（树 clean）得到的日志**恰好是 `2afe8d24…`**（3 warnings）：
  证明实现者确实在最终状态下跑过 check 并把它写进 §5，但**没有把这个最终日志提交**，提交的是更早的
  4-warning 版本；卡面 EV-05 签的也是这个 4-warning 文件（哈希自洽，但内容不是最终状态）。
- 影响：`PASS` 结论不受影响（两版都是 PASS；我复跑 3 warnings）；但“EV-01…EV-19 全部按最终文件 sha 重签”的
  记录表存在 1 行不一致，且 `gates.log §6` 的“3 既有 warnings”只对最终状态成立。
- 建议（closeout 前）：用我复跑得到的 3-warning 内容覆盖 `logs/check.log`（或把 §5 改成 `ed28ade7…`），
  并同步重签 EV-05；若 closeout 会改卡/记录，则 closeout 后重跑 check 再签一次。

### P3-2（历史表述）卡 `## r2 返修`（`:145`）与 Handoff §8（`:97`）仍写“r2 已修严格断言”

- 这两处是**历史段**（r2 交付记录），当前仍声称 r2 落地了 `RootLost` 严格断言；与 r2b 段/§7.3/§7.5/§9 的
  erratum 并存。代码与当前状态无矛盾（r2b 已落地），但严格按“不再声称 r2 已修”口径，历史段需要脚注。
- 建议：在这两处各加一句“（**实际 r2b `00083a977` 才落地，见 r2b 段/§7.5**）”，或在 closeout 说明中明确
  “历史段保留原字节，由 r2b 段覆盖”。不要求改写 commit message（不可改写）。

### P3-3（Markdown）卡面 `:200` 存在字面 `\n`，把 r2b 与 r2 两条 bullet 合并

- 事实：`doc/tasks/FEA-11-WATCH-1.md:200` 行内是 `…scope diff 0。\n- **r2 返修（Review r1 CHANGES 处置）**…`，
  字面 `\n` 使 r2 段被并入 r2b 段，渲染异常（`write` 时可能是转义字符串误用）。
- 建议：改成真正的换行，拆回两条 bullet。

### P3-4（证据映射）卡面 EV 表 AC/Gate 列被统一成 `AC-W1/2/3/4`

- `e1036e561` 把 r2b 时的逐项映射（EV-05 `AC-W5（全量 .NET）`、EV-08 `AC-W2（变异）`、EV-11 `AC-W5（pins）`、
  EV-17 `AC-W3（r2b 隔离 5/5）`、EV-18 `AC-W5（范围）`、EV-19 `提交后门禁` 等）统一改成 `AC-W1/2/3/4`，
  丢失了“每条证据对哪个 AC/Gate 有判别力”的信息（尤其 pins/scope 属 AC-W5，变异分别属 W2/W3/W4）。
- 建议：closeout 恢复逐项 AC/Gate 标注（或增加“Gate”列），不影响哈希。

### P3-5（陈旧横幅）卡面 `:43` 仍写 `状态：ready（…待 Owner 认领实施）`

- 与 frontmatter `status: in_review` 及当前 `r2b → r3` 阶段矛盾；该行自 `4b3692415`（scope 冻结）起未更新。
- 建议：closeout 时改为 `in_review → done` 的最终状态描述（或删除该横幅）。

### P3-6（资源/证据新鲜度）Resource Manifest 路径不存在 + `check-post-commit.log` 为 r2 期日志

- 卡 `## Resource Manifest` 记的 `G:\CODEX\New Manga.workspace\temp\FEA-11-WATCH-1\`（DELETE_SAFE）与
  `…\agent-output\fea11-watch-1\`（PRESERVE_REFERENCED）当前**均不存在**（实际过程产物在
  `G:\CODEX\New Manga.workspace\FEA-11-WATCH-1\` 顶层 Task 目录；`agent-output` 下无 `fea11-watch-1`）。
  closeout 需把不存在的条目改成 `NOT_APPLICABLE`/`DELETE_SAFE（0 字节）`，或指向真实路径。
- EV-04 `logs/check-post-commit.log`（`db8a4a52…`）内容是 r2 期（STATUS 3118 bytes）的 post-commit check，
  未随 r2b 重新生成；建议 closeout 后补一次 post-commit check，或把 EV-04 说明改为“r2 期保留证据”。
- 以上均不影响 `canonical_evidence_status` 的哈希一致性，但影响 closeout 的资源/证据叙述。

---

## 6. AC-W 判定（独立；不代 DSH 关闭）

| AC | 判定 | 依据 |
|---|---|---|
| **AC-W1 生命周期/范围** | **MET** | arm/registry 复核/typed skip/Stop 零 hint 由 r2 独立探针证实且 r2b 未改产品源码；gated 用例（r2 1/0/0）与本次 Host 全量 185/0/55 支持。 |
| **AC-W2 hint 语义/去抖** | **MET** | r2 P1 探针（hint 在 hint pass 内被扫、pending 清空）与变异 A 红；r2b 无 src 变更；去抖/合并/脱敏测试仍在。 |
| **AC-W3 overflow/根删除/上限** | **MET（本轮补实证据）** | `RootLost` 现为严格断言 `Active==0 && Uncovered>=1` 且隔离 5/5 绿；overflow/cap 用例通过。 |
| **AC-W4 与 SCAN-1 协同** | **MET** | r2 探针（单飞 replay≤1、hinted 优先、预算/退避/pause、命令集合 `{ScanSourceSync}`）已独立证实；r2b 无 src 变更。 |
| **AC-W5 资源/隐私/门禁** | **MET** | Host 185/0/55；全量 .NET 1527/0/86（RUN2；RUN1 为已知 FEA-09 flaky 已复跑）；pytest 3212/10（引用/实跑证据未变）；pins 18/18；API PASS；check PASS；scope diff 0；EV 19/19；无新依赖/契约/schema 变更。 |

AC11-1：**仍 PARTIAL**，本卡不回填；L10 不解决；RH-3 不修。

---

## 7. Closeout 建议（APPROVE 后由 DSH 执行）

1. **frontmatter 定稿**：
   - `delivery_head: 00083a977`（Owner 实现+测试交付链头；若沿用 `FEA-11-SCAN-2` 的“delivery_head=Lead 集成提交”口径，
     则填 closeout/集成提交 hash，并在注释保留实现链 `e60105cf9 → 19a2af7f3 → 00083a977`）。
   - `integration_commit`：待 r3 APPROVE 后的 **closeout 提交**生成后填其实际 hash（当前 `e1036e561` 只是
     “待 r3 复审”的 r2b 文档集成，不应作为终态集成提交；若 DSH 决定将其作为集成基线，则需再建关闭提交）。
   - `status: done`（或按 DSH 处置 `closed_with_limitations`）；`canonical_evidence_status: complete`；
     `resource_closeout_status: complete`；`reviewer:` 补记 r3 会话/报告。
2. **先做 §5 的 P3 收尾**：P3-1（check.log/§5 哈希）、P3-2（历史段脚注）、P3-3（字面 `\n`）、
   P3-4（EV 表 AC/Gate）、P3-5（ready 横幅）、P3-6（Resource Manifest / EV-04 新鲜度）；改完重跑
   `check.ps1 -TaskPath`、`verify_pins.ps1`、API inventory，并重签受影响 EV（至少 EV-05/EV-18 与卡面表）。
3. **AC-W 定稿**：AC-W1…W5 全 **MET**（AC-W3 以 r2b 严格断言 + 隔离 5/5 为判别证据）；
   AC11-1 保持 **PARTIAL**，L10 不解决，RH-3 不修。
4. **资源处置**：`temp/FEA-11-WATCH-1` 与 `agent-output/fea11-watch-1` 已不存在 → 记 `DELETE_SAFE（0）`/
   `NOT_APPLICABLE`；若保留顶层 `FEA-11-WATCH-1` 过程目录，按治理规则登记或归档到 workspace archive。
5. **指针**：更新 `STATUS`（当前仍写“r2 窄面复审中/下一步 r2 窄面复审”）、`REBASELINE_PLAN`、`TASK_LEDGER`
   到 `done/closeout`，并清理 READY/当前 Task 指针（由 DSH 执行）。
6. **limitation 保留**：watcher 漏事件/设备差异依赖 SCAN-1 周期兜底（非正确性依赖）；folder 内任意事件=该 source due
   （无增量 diff，受预算/单飞约束）；**hint pass 会重扫 ≤budget−1 个刚扫 target**；跨 tick 延迟由生产 900 s 周期决定；
   HostRuntime seam 无 fake-Core/注入时钟；SCAN-2 RH-3 target 只增不减不修；真实树/证据路径测试理论可能 flaky
   （r3 RUN1 命中 FEA-09 已知 flaky，恢复后 RUN2 全绿）；**AC11-1 仍 PARTIAL**；L10 不解决。
7. **报告归档**：本报告在仓外；如需入库，DSH 可复制为 `doc/reviews/FEA-11-WATCH-1-r3.md`（在 allowed_paths 的
   `doc/reviews/FEA-11-WATCH-1-*.md` 内），并在卡 frontmatter 的 `reviewer` 行补记 r3。

---

## 8. 复核产物位置（仓外）

- 报告：`G:\CODEX\New Manga.workspace\FEA-11\review-watch-1-r3\FEA-11-WATCH-1-r3.md`
- 日志：`rootlost-isolated-5x-clean.log`、`rootlost-isolated-5x.log`、`host-full.log`、
  `dotnet-full-run1.log`、`dotnet-full-run2.log`、`check-taskpath.log`、`pins.log`、`api-inventory.log`
- 未修改仓库、未 commit、未 push；未创建 linked worktree。

WATCH-1-R3-REVIEW: APPROVE
