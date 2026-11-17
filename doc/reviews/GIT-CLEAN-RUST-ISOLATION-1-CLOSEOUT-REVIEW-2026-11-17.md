---
task_id: GIT-CLEAN-RUST-ISOLATION-1
kind: closeout-review
reviewed_head: d8f917a2b
reviewer: reviewer-rustiso
reviewer_kind: subagent
reviewer_independence: 独立上下文子 agent；本会话只含复核任务，未参与本卡的实现、返修或收口
reviewed_at: 2026-11-17T17:13:48+08:00
subject: 独立判定 Lead 将本卡从 in_review 收口为 closed_with_limitations 是否成立
decision: ACCEPTED_WITH_FINDINGS
p0: 0
p1: 1
p2: 6
---

# GIT-CLEAN-RUST-ISOLATION-1 —— 收口独立复核（2026-11-17）

> `reviewed_head: d8f917a2b`（main）
> `reviewer: reviewer-rustiso`（DSH 派发的独立上下文子 agent；未参与实现/返修/收口）
> 复核时间：2026-11-17T17:13:48+08:00
> 复核方式：只读；唯一写入为本报告文件。
> **本复核不构成产品发布验收。**

## 0. 复核对象与被审事实

| 项 | 值 | 来源 |
|---|---|---|
| 被审 head | `d8f917a2bd8f726714d555b6702e065822b333a1` | `git rev-parse HEAD` |
| 父提交 | `d8a7f1907` | `git log --oneline -3` |
| 被审分支 | `main` | `git rev-parse --abbrev-ref HEAD` |
| 工作区状态 | clean（`git status --porcelain` 空） | 实测 |
| 卡面状态变更 | `in_review` → `closed_with_limitations` | diff `@@ -3,11 +3,11 @@` |
| 收口依据 | `doc/reviews/GIT-CLEAN-RUST-ISOLATION-1-LEGACY-SCOPE-RULING-2026-11-17.md`（Codex 裁定 + DSH 采纳） | 卡面 L200 |
| 收口链提交 | `d8a7f1907`（引入裁定 + 采纳）、`d8f917a2b`（收口标记） | `git log 529febcf9..d8f917a2b` |
| 提交 author | 两提交均为 `DSH <dsh@local>` | `git log --format='%h \| %an <%ae> \| %s'` |

## 1. 七项逐条判定

| # | 必测问题 | 判定 | 关键实测证据 |
|---|---|---|---|
| 1 | AC 未被篡改 | **PASS** | AC1/AC3 行 sha256 与父提交**逐字节相同**；AC1 仍 `<<PARTIAL: …>>`、AC3 仍 `<<BLOCKED: …>>`；AC2/AC4 仍 `<<MET>>` |
| 2 | 裁定是否被如实采纳 | **PASS**（附 P2-2） | L-R1…L-R7 七条逐条落地且语义等价；R2-F01…F05 明确 `WONT_FIX_LEGACY` + 「不等于已修复」，全文无「已修复」误写 |
| 3 | 历史证据字节未动 | **PASS** | `--stat` 仅 4 个 `doc/` 文件；`-- verification/` diff 为空；EV pin 抽样 4/4 匹配 |
| 4 | 资源核销 | **PASS**（附 P2-1） | manifest 存在、sha256 独立重算**完全一致**；2 个实路径 destination 均存在；19/10,858/190,447,692 逐目录精确吻合 |
| 5 | 门禁 | **PASS** | `check.ps1` 输出 `Governance check: PASS (3 warnings)`，`EXITCODE=0` |
| 6 | 产品边界论证是否成立 | **PASS**（论证成立，无过度外推） | `AGENTS.md:54`、`AD-002:24,30`、`09_COLLABORATION.md:79` 三条文本直接支撑；卡面 L-R2 + 边界段已封住误读 |
| 7 | reviewer 独立性 | **PASS**（附 P1-1、P2-3） | `owner: ZCode` / `reviewer: reviewer-rustiso` → 非 ZCode 自审；非 Lead 自审（子 agent 独立上下文） |

---

## 2. 逐项实测记录

### 2.1 问题 1：AC 行未被篡改（PASS）

**方法**：以字节流读取两个版本的 blob（不经 PowerShell 管道解码），按 `0x0A` 切行，对 AC1–AC4 各行字节直接计算 SHA-256。

```powershell
# 关键片段：Process 直取 stdout 字节流
$p.StandardOutput.BaseStream.CopyTo($ms)   # 避免任何编码往返
$h.ComputeHash($lineBytes)                 # 行长与 sha256 均逐行计算
```

| AC | head 行号 | parent 行号 | head 字节 | parent 字节 | head sha256 | parent sha256 | 字节相同 |
|---|---|---:|---:|---:|---|---|---|
| AC1 | 34 | 34 | 191 | 191 | `a49421ad3dc62bda6d300569161c4cf7c3db9ecc9053568e03e253fdb6a94bf0` | 同左 | **是** |
| AC2 | 35 | 35 | 127 | 127 | `8cb18a668ab2eebe660595bd2706a4e87da27399d1b105b8e5cb6d15dba0d35e` | 同左 | **是** |
| AC3 | 36 | 36 | 229 | 229 | `15873374dafbe80365a5a1ca455ddf5c2d2dd70e3940ca297be2d8ed0a262be5` | 同左 | **是** |
| AC4 | 37 | 37 | 167 | 167 | `8064651b5c929c8df6788bc3f51a7b4f02701120aac01300de46980ae3037d94` | 同左 | **是** |

AC1/AC3 行文本（head 版，与 parent 完全一致）：

```
- [ ] **AC1**：registry隔离修订与全使用者清点已交付，编译/生产check通过。 <<PARTIAL: DSH r2确认主要隔离/资源真实性；R006异常清理及R2-F02..05仍待补>>
- [ ] **AC3**：真实多channel公平响应、容量、取消/关停与回收验证。 <<BLOCKED: r2四个Core场景通过，fault20真实write超时及资源回收通过，但peak0未达32，容量接受/拒绝路径未验证>>
```

AC2/AC4 的 `<<MET>>` 语义未被改写：AC2 仍为程序性 `<<MET>>`（无原因后缀），AC4 仍保留 `（DSH blocked，不等于技术通过或集成）` 的自我限定。收口段 L-R3/L-R4 对两者是**收紧**解释，不是放宽。

**附加检查**：两版整 blob 的控制字符扫描（`0x20` 以下排除 LF/CR/TAB，另检 `0x7F`）：

| 版本 | blob 字节数 | 控制字符数 |
|---|---:|---:|
| `d8f917a2b^` | 30,005 | 0 |
| `d8f917a2b` | 33,633 | 0 |

即 `d8a7f1907` 声称修复的「收口段自伤控制字符」在 head 已不存在，且 **AC 行本身从未处于 control-char 区域**。

### 2.2 问题 2：裁定是否被如实采纳（PASS，附 P2-2）

裁定文件 `doc/reviews/GIT-CLEAN-RUST-ISOLATION-1-LEGACY-SCOPE-RULING-2026-11-17.md` 的 Q3（L41–L47）列出 7 条限制，卡面 L208–L214 逐条落地。逐条语义对照：

| 裁定 Q3 | 裁定原文要点 | 卡面 L-R | 卡面表述 | 语义 |
|---|---|---|---|---|
| 1 | AC1 保持 `<<PARTIAL: ...R006异常清理及R2-F02..05仍待补>>`；不得写成已修复 | L-R1 | AC1 保持 `<<PARTIAL: …R006异常清理及R2-F02..05仍待补>>`；不得把遗留项写成已修复 | 等价 |
| 2 | AC3 保持 `<<BLOCKED: ...peak0未达32，容量接受/拒绝路径未验证>>`；不得声称饱和或已验证所有权 | L-R2 | 同表述 + 「不得声称达到饱和或已验证 accepted/refused 所有权」 | 等价 |
| 3 | AC2 `MET` 仅限固定 head `1829a38` 两次默认并发 `153/0/6/12`，不得外推 | L-R3 | 逐字保留 head、四个计数与外推禁令 | 等价 |
| 4 | AC4 `MET` 仅表程序性；结论仍 `blocked` | L-R4 | 「只表示交付绑定与审查流程已执行；审查结论仍为 `blocked`」 | 等价 |
| 5 | R2-F01…F05 原记录仍 `open`；`WONT_FIX_LEGACY` 是分类 | L-R5 | 「仍为 `open`；…是收口分类，不表示 finding 已修复或原始记录已关闭」 | 等价 |
| 6 | fault 回收只记录 peak 前部分；`remaining=0` 是打印值 | L-R6 | 逐字保留「peak 失败后的后续断言未执行」 | 等价 |
| 7 | 不改 `MAX=32`、不改进生产实现/契约/Schema/依赖 | L-R7 | 同，并补 `registry`（原卡 L41/L48 本已述及） | 等价（略更精确，未削弱） |

**R2-F01…F05 处置核验**：卡面 L202 与 L212 两处均写明 `WONT_FIX_LEGACY`「**收口分类，不等于已修复**」，并声明 `verification/…/r2/DISPOSITION.md` 原 `open` 状态与字节保持原样。

- 在 4 个被改文件全文中检索 `已修复|已解决|已通过`，命中 3 处，**全部为否定式**（L202「不等于已修复」、L208「不得把遗留项写成已修复」、L212「不表示 finding 已修复」）。
- 原始证据未改：`verification/GIT-CLEAN-RUST-ISOLATION-1/r2/DISPOSITION.md:16-20` 现读仍为 5 条 `open`（含 `R2-F01 P1 | open，直接阻断`），与裁定 L29–L33 的引用一致。

**P2-2**：裁定文件 L81（DSH 采纳段）写「7 条限制逐条写入卡面 `## Closeout Record` 的 limitation 段」，但卡面实际节标题为 `## 2026-11-17 收口（Codex Legacy 裁定采纳 → closed_with_limitations）`（L198）+ `### 收口限制清单（L-R1…L-R7，来自 Codex 裁定 Q3）`（L206），文档中不存在 `## Closeout Record`。属指向性命名不符，不影响限制内容。

### 2.3 问题 3：历史证据字节未动（PASS）

```
$ git diff d8f917a2b^ d8f917a2b --stat
 doc/REBASELINE_PLAN.md                  |  2 +-
 doc/STATUS.md                           |  2 +-
 doc/TASK_LEDGER.md                      | 12 +++++------
 doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md | 35 +++++++++++++++++++++++++++------
 4 files changed, 36 insertions(+), 15 deletions(-)

$ git diff d8f917a2b^ d8f917a2b -- verification/
<EMPTY>
```

扩到整条收口链 `529febcf9..d8f917a2b`（含 `d8a7f1907`），`-- verification/` 同样为空；该链仅新增 1 份裁定文件与 1 份另一张卡的收口验证报告，未触碰任何既有 verification 文件。

此外：

```
$ git log --oneline -5 -- verification/GIT-CLEAN-RUST-ISOLATION-1/
f632f801b chore(evidence): commit GIT-CLEAN verification evidence and V1 audit artifacts
```

该目录最后一次变更是 `f632f801b`，早于本收口链。

**EV pin 抽样重算**（4/4 匹配）：

| evidence_id | path | 重算 sha256 | 匹配 |
|---|---|---|---|
| EV-001 | `…/review-package-r1/PACKAGE_MANIFEST.json`（仓外） | `b5fe398d…ee4a41` | 是 |
| EV-067 | `verification/GIT-CLEAN-RUST-ISOLATION-1/r2/dsh-review-r2.md` | `a0bba91a…ac3829` | 是 |
| EV-068 | `verification/GIT-CLEAN-RUST-ISOLATION-1/r2/DISPOSITION.md` | `d7624880…41d7ef28` | 是 |
| EV-069 | `verification/GIT-CLEAN-RUST-ISOLATION-1/r2/checkpoint-review.md` | `5278bf0e…749e068` | 是 |

### 2.4 问题 4：资源核销（PASS，附 P2-1）

**manifest 存在性与摘要重算**：

```
manifest: G:\CODEX\New Manga.workspace\task-envs\GIT-CLEAN-RUST-ISOLATION-1\RESOURCE-MANIFEST.json
size     = 4077 B
mtime    = 2026-11-17T17:03:23+08:00
$ (Get-FileHash … -Algorithm SHA256).Hash.ToLower()
52502fd234bd9c711ad200a9d47b541b6096f2fa6f998ee59ca1bf238b79af28
卡面 L204 声明：52502fd234bd9c711ad200a9d47b541b6096f2fa6f998ee59ca1bf238b79af28
=> MATCH = True
```

**三个 `destination_path` 实测**（卡面 L140–L142）：

| 行 | disposition | destination_path | `Test-Path` |
|---|---|---|---|
| L140 | `PRESERVE_REFERENCED` | `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1` | **True** |
| L141 | `PRESERVE_REFERENCED` | `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/review-package-r2` | **True** |
| L142 | `NOT_APPLICABLE` | `—` | 无需存在（枚举语义正确） |

**内容独立重算**（逐目录 `Get-ChildItem -Recurse -File -Force` 求文件数与字节和）：

| 目录 | manifest 文件数 | 实测 | manifest 字节 | 实测 |
|---|---:|---:|---:|---:|
| codex-prerequisites-r1 | 6 | 6 | 25,034 | 25,034 |
| codex-test-environment | 0 | 0 | 0 | 0 |
| codex-test-environment-r2 | 535 | 535 | 2,690,891 | 2,690,891 |
| codex-validation-r1 | 24 | 24 | 205,940 | 205,940 |
| codex-validation-r2 | 25 | 25 | 348,332 | 348,332 |
| dispatch-dsh-probe-r1 | 3 | 3 | 313 | 313 |
| dispatch-dsh-review-r1 | 5 | 5 | 419,859 | 419,859 |
| dispatch-dsh-review-r2 | 6 | 6 | 317,588 | 317,588 |
| dispatch-zcode-r1 | 6 | 6 | 13,695 | 13,695 |
| dispatch-zcode-r2 | 6 | 6 | 6,218 | 6,218 |
| empty-hooks | 0 | 0 | 0 | 0 |
| r2-runner | 2 | 2 | 10,841 | 10,841 |
| review-disposition-r2 | 1 | 1 | 1,774 | 1,774 |
| review-package-r1 | 8 | 8 | 88,277 | 88,277 |
| review-package-r2 | 4 | 4 | 284,373 | 284,373 |
| runner | 2 | 2 | 10,834 | 10,834 |
| source | 5,110 | 5,110 | 92,767,867 | 92,767,867 |
| source-r2 | 5,109 | 5,109 | 92,790,066 | 92,790,066 |
| zcode-delivery-r2 | 6 | 6 | 465,790 | 465,790 |
| **合计（19 项）** | **10,858** | **10,858** | **190,447,692** | **190,447,692** |

**P2-1（口径披露）**：上表的「实测」是在**排除 `.git`** 后吻合的。若用最朴素的 `Get-ChildItem -Recurse -File -Force`（含 VCS 内部目录）直接统计整个 task-env，会得到不同的数字：

| 口径 | 文件数 | 字节数 |
|---|---:|---:|
| manifest / 卡面 L140、L204 | 10,858 | 190,447,692 |
| 实测，**排除** `.git` | 10,858 | 190,447,692 |
| 实测，**包含** `.git` | 12,666 | 195,868,326 |

差额精确等于两个隔离副本的 `.git`：`source/.git` = 899 文件 / 2,655,484 B；`source-r2/.git` = 909 文件 / 2,765,150 B（合计 1,808 文件 / 5,420,634 B）。两份隔离仓库的 `.git` 目录本身即「PRESERVE_REFERENCED」对象的一部分，因此**排除 `.git` 是可辩护的统计口径，不是数据错误**；问题仅在于卡面与裁定文件的「19 目录 / 10,858 文件 / 190,447,692 B」未标注该口径，读者做整目录递归校验时会得到 12,666 / 195,868,326 而误以为不符。

结论：资源核销结论（全部保留、删除/迁移/归档 = 0、manifest 摘要一致）**成立**。

### 2.5 问题 5：门禁（PASS）

采集时刻 **2026-11-17T17:10**；该时刻 `git status --porcelain` 输出为空，工作树与 `d8f917a2b` 逐字节一致，故下述结果即**被审 head 的纯快照结果**。

```
$ pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\GIT-CLEAN-RUST-ISOLATION-1.md
WARN: 存在 6 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3170 bytes / 28 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6757 bytes / 64 lines
Governance check: PASS (3 warnings)
EXITCODE=0
```

3 条 warning 均为全局预算/统计类提示，与本卡收口判定无冲突（「6 个非终态 Task」正是把本卡移出非终态后的余量，与 `TASK_LEDGER` 的 6 一致）。

**并发工作区漂移（如实披露，非本卡缺陷）**：本复核期间工作区出现了**非本复核产生**的未提交修改，作者为并发进行的另一会话：

- `2026-11-17T17:14:39`：`doc/tasks/SIDECAR-REBUILD-1.md`（`status: in_progress` → `closed_with_limitations`）；
- `2026-11-17T17:16:18`：`doc/STATUS.md`（把 `SIDECAR-REBUILD-1` 并入 `closed_with_limitations` 列表并更新四件套数字；本复核已核对该 diff，**未触动 `GIT-CLEAN-RUST-ISOLATION-1` 的条目**，本卡仍在列表中）。

受其影响，同一命令在漂移后重跑（`17:15:11`）返回：

```
WARN: 存在 5 个非终态 Task（见 TASK_LEDGER）…
FAIL: TASK_LEDGER 已过期：声明 6 个非终态 Task，实际 5 个（重跑 tools/governance/task_ledger.py --write）
Governance check: FAIL (1 errors, 3 warnings)
EXITCODE=1
```

该 FAIL 的归因是唯一的：本卡收口提交 `d8f917a2b` 已把 `TASK_LEDGER` 的非终态由 7 校正为 6，而并发会话把 `SIDECAR-REBUILD-1` 改为终态后未同步 `TASK_LEDGER`（`doc/TASK_LEDGER.md` 在本复核期间无任何未提交修改，`git status` 已实测）。**与本卡收口判定无关**；但任何在漂移后的工作树上重跑门禁的人都会看到该 FAIL，需按提示重跑 `tools/governance/task_ledger.py --write` 消除（不属本复核授权范围，仅提示）。

**门禁实际覆盖面**（读 `tools/governance/check.ps1` 确认，避免高估 PASS 的含义）：

- L1436–L1439：`closed_with_limitations` 必须 `canonical_evidence_status: complete` 且 `resource_closeout_status: complete`。本卡两项均为 `complete`。
- L1437–L1504：Resource Manifest 逐行校验 disposition 枚举、destination 存在性、integrity 非空；integrity 为路径时校验 manifest 文件存在。
- L1531–L1569（§4.3）：gv3 卡进入 `in_review/approved/done/closed_with_limitations` 时，每个 AC 行必须有合法 `<<MET|PARTIAL|BLOCKED|NOT_APPLICABLE>>`，且与勾选一致；L1564 仅对 `done` 禁止未达成 AC —— 这正是 `closed_with_limitations` 允许保留 `PARTIAL/BLOCKED` 的机器定义。
- **未覆盖**：manifest 内容摘要与卡面两位一体的比对（卡面 integrity 列放的是路径而非摘要，L1497–L1502 只验路径存在）；`reviewer` 字段（全文无任何 reviewer 校验，见 P2-3）。

因此 `PASS` 支持的结论是「卡面结构、AC 标记一致性、资源路径与两项 closeout 标志合规」，**不**等于「reviewer 独立性、资源摘要、裁定语义已被机器验证」；后三者由本复核人工实测补齐。

### 2.6 问题 6：产品边界论证是否成立（PASS，论证成立）

**论证链与文本依据**

1. AC3 的验证对象是 `apps/desktop/src-tauri/src/` 内的 Rust registry（生产预算 `MAX=32`、accepted/refused 句柄所有权、pool/reader/writer 回收）。卡面 L41 把允许范围限定在该目录的 `cfg(test)` 与压力测试；`Test-Path apps/desktop/src-tauri` = **True**，该目录仍在仓库中并带 `LEGACY_FROZEN.md`。
2. `AGENTS.md:54`（实测原文）：「后续 Task、缺陷诊断和修复只允许落在该架构；**Tauri/React/WebView2 与 PySide6/QML 代码、测试和既有 Task 仅保留为历史证据，不再释放 Legacy 实现、诊断或修复任务**。」
3. `doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md:24`：「C# Host 服务层 … **取代原 Tauri/Rust host**。」；`:30`：「**明确移除**：React/TypeScript、Tauri、Rust host（9 文件/16,926 行）、WebView2…」。
4. `doc/09_COLLABORATION.md:79`：「`closed_with_limitations` 仅用于**用户明确裁决**或**已批准目标架构取代旧 Task**；记录替代依据、closure evidence、未完成 AC/Finding 原始状态及分类，不得改写为 PASS；除新授权外不恢复实施。」

第 2 条直接把「Legacy 的**测试**」与「不再释放 Legacy 修复/诊断任务」并列写入产品边界；第 4 条把「已批准目标架构取代旧 Task」列为 `closed_with_limitations` 的合法启用条件，而 AD-002 是 2026-10-26 用户裁决批准的目标架构。**因此「AC3 属已退役 Tauri/Rust 线，故不在旧实现上补测并允许终态收口」有直接、逐条的文本依据，不属于无据推断。**

**是否过度外推 —— 逐点核查**

| 可能的越界 | 实测是否发生 | 依据 |
|---|---|---|
| 把「不再释放 Legacy 任务」说成「Rust 并发容量已通过/已验证」 | **未发生** | 卡面 L209（L-R2）明令「不得声称达到饱和或已验证 accepted/refused 所有权」；AC3 仍 `<<BLOCKED>>` |
| 把「无生产缺陷证据」说成「已证明无缺陷」 | **未发生** | 裁定 L21 与 `r2/DISPOSITION.md:16` 均限定为「**当前没有**生产缺陷证据」；卡面未升级该表述 |
| 用本卡收口去放宽 Gate/发布结论 | **未发生** | 卡面 L218 边界段：「不改变任何 Gate 结论，不改变父候选 `e34a90d` / 源 `main`，不 push 候选、不置 `done`、不集成」；L-R4 另行禁止以 AC4 声称技术验收 |
| 把「不另立新架构容量卡」当成「新架构无需验证容量」 | **未发生，但需注意其性质** | 裁定 L35 与卡面 L202 均写明触发条件：「若将来新架构复现对应**用户可见**行为，再按 `AGENTS.md` 另立卡」，并明确「不继承 Rust 的 `MAX=32`」 |

**必须记录的性质界定**：该论证的法律效力是「**范围替代 + 有触发条件的风险接受**」，而不是「技术验证通过」。其前提是「新架构尚未复现对应用户可见行为」——即**证据缺失下的默认安全接受**，而非「已证明新架构无此风险」。这一定性在卡面中已被 L-R2、L-R4 与 L218 边界段正确封住，因此**不构成 finding**；但若将来有人引用本卡作为「并发容量风险已被审查/可忽略」的依据，即属误用。建议后续引用一律以 L-R2 为准。

**补充观察（不计 finding）**：`doc/REBASELINE_PLAN.md:57` 记载另一张并发卡 `HOST-CONCURRENCY-FLAKY-1` 亦为 `closed_with_limitations`，说明新架构侧并发风险另有独立处置通道。这与本卡的对象不同（Rust registry 容量 vs Host 并发缺陷），不构成本卡论证的反例，但可佐证「新架构问题走新卡」的机制确实在运转。

### 2.7 问题 7：reviewer 独立性（PASS，附 P1-1、P2-3）

| 检查 | 实测 | 判定 |
|---|---|---|
| 是否 ZCode 自审 | `owner: ZCode`（L9）；`reviewer: reviewer-rustiso（…）`（L10） | 否 ✔ |
| 是否 Lead 自审 | 被审变更 author = `DSH <dsh@local>`；本复核者是 DSH 派发的**独立上下文子 agent**，会话内无任何实现/返修动作 | 否 ✔（符合 `AGENTS.md` 2026-10-31 裁决：作者可派发独立上下文子 agent 审查） |
| 是否有替换后的 reviewer 记录 | frontmatter L10 + 收口段 L203 + 卡尾 L219 三处一致指向 `reviewer-rustiso` | 是 ✔ |
| 历史 reviewer 记录是否保留 | 「Reviewer 二次改派（2026-10-25）」段 L189–L196 完整保留；`dsh-review-r1/r2` 字节未改（EV-067 匹配） | 是 ✔ |

**独立性强度如实披露**：本复核的独立性来自**上下文隔离**（不同会话/实例），而非**组织隔离**——本复核由被审变更的作者（Lead/DSH 主会话）派发。该模式为 `AGENTS.md` 2026-10-31 裁决明确允许，但强度弱于由未参与该变更的外部 Agent（Codex / ZCode）复核。裁定文件 L49 的**建议**是改派 `Codex`；卡面选择走裁定并列允许的「改派独立子 agent」分支，形式上合规，实际独立性弱于建议方案。此项作为独立性说明记录，不单列 finding。

**P1-1**：卡面存在对 `reviewer` 当前值的互相矛盾陈述。

- 位置：`doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md:185`
- 原文：「DSH 接任 Lead / Architect / Integrator（见 `doc/GOVERNANCE_TAKEOVER_2026-10-25.md`）。本 Task 的 Owner/实现作者仍为 ZCode；**当前 Reviewer 改派 ZCode**（同日再次改派，见下节「Reviewer 二次改派」）。」
- 冲突对象：同文件 L10 `reviewer: reviewer-rustiso（DSH 子 agent，独立上下文，未参与实现；2026-11-17 收口复核）`
- 实测命令：`Select-String -Pattern 'reviewer' doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md` → 同时命中 L10（rustiso）与 L185（ZCode）
- 加剧因素：L185 所属小节标题带日期（`## 2026-10-25 DSH 接管后的处置`），但句内使用「**当前** Reviewer」且未加「截至 2026-10-25」之类的时点限定；相邻 L187 同样残留「Task 保持 `in_review`」。相比之下 L179 以「2026-10-25：」显式起句。矛盾方向恰好命中本卡最敏感的「自审」风险点——若读者只读 L183–L196 历史段，会得出「Reviewer = ZCode = Owner」的自审结论，与收口事实相反。
- 严重性定级理由：不影响 head 字节、不影响裁定 7 条落地、可通过文档顺序（L198 之后为最新）消解，故不阻断收口；但它是「本卡是否已消除自审」这一核心治理结论在卡面上的唯一矛盾点，且无机器校验兜底（见 P2-3），故定 **P1**。
- 建议修复（不属本次授权范围，仅记录）:把 L185 改为历史时点表述，例如「2026-10-25 时点 Reviewer 为 ZCode（已被 2026-11-17 收口段取代）」，并给 L187 的 `in_review` 加同样的时点限定。

---

## 3. Findings

### 计数

| 级别 | 数量 | 定义 |
|---|---:|---|
| **P0** | **0** | 阻断项：AC 篡改、证据被改、裁定未采纳、结论不成立 |
| **P1** | **1** | 影响可核验性/合规性，需修复但不阻断收口 |
| **P2** | **6** | 文档/治理瑕疵，不影响收口成立 |

### P0

无。

以下关键断言全部实测通过，故无 P0：AC1/AC3 行字节未变（sha256 相同）、AC2/AC4 `<<MET>>` 未被改义、`verification/**` 零改动、manifest sha256 一致、7 条限制逐条落地、R2-F01…F05 未被写成已修复、门禁 exit 0。

### P1

**P1-1 — 卡面 L185 与 frontmatter L10 对「当前 reviewer」给出互相矛盾的值**

- 文件：行：`doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md:185`（冲突面 `:10`）
- 实测命令：
  ```powershell
  cd 'G:\CODEX\New Manga'
  Select-String -LiteralPath 'doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md' -Pattern '^reviewer:|当前 Reviewer'
  ```
- 实测值 vs 卡面值：L10 `reviewer: reviewer-rustiso（…）` ←→ L185「当前 Reviewer 改派 ZCode」；两者不能同时为真。
- 影响：可能被引用为「本卡由 Owner（ZCode）自审」，与本次独立复核事实冲突；`check.ps1` 不校验 `reviewer` 字段（见 P2-3），无自动兜底。

### P2

**P2-1 — 资源统计口径未披露（排除 `.git`）**

- 文件：行：`doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md:140`、`:204`；同口径亦见于 `doc/reviews/GIT-CLEAN-RUST-ISOLATION-1-LEGACY-SCOPE-RULING-2026-11-17.md:35`
- 实测命令：
  ```powershell
  $root = 'G:\CODEX\New Manga.workspace\task-envs\GIT-CLEAN-RUST-ISOLATION-1'
  # 排除 .git
  Get-ChildItem -LiteralPath $root -Recurse -File -Force |
    Where-Object { $_.FullName -notmatch '\\\.git\\' } |
    Measure-Object -Property Length -Sum
  # 包含 .git
  Get-ChildItem -LiteralPath $root -Recurse -File -Force |
    Measure-Object -Property Length -Sum
  ```
- 实测值 vs 卡面值：卡面 10,858 文件 / 190,447,692 B（排除 `.git` 时**精确吻合**）vs 含 `.git` 时 12,666 文件 / 195,868,326 B（差 1,808 文件 / 5,420,634 B）。
- 影响：核销结论不变，但读者用整目录递归校验会得到不同数字，易误判为「资源被改动」。

**P2-2 — 采纳段指向的 `## Closeout Record` 节名不存在**

- 文件：行：`doc/reviews/GIT-CLEAN-RUST-ISOLATION-1-LEGACY-SCOPE-RULING-2026-11-17.md:81`；卡面实际节 `doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md:198`、`:206`
- 实测命令：`Select-String -LiteralPath 'doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md' -Pattern '^## '`
- 实测值 vs 卡面值：卡面标题为 `## 2026-11-17 收口（…）` + `### 收口限制清单（L-R1…L-R7，来自 Codex 裁定 Q3）`；文档内无 `## Closeout Record`。
- 影响：限制内容不受影响；仅指向性命名不一致，增加后续定位成本。

**P2-3 — 未按裁定 L49 记录 `reviewer_kind` 与子任务/会话 ID，且 `reviewer` 字段混入说明文字；门禁对该字段零校验**

- 文件：行：`doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md:10`、`:203`、`:219`
- 实测命令：
  ```powershell
  Select-String -LiteralPath tools/governance/check.ps1 -Pattern 'reviewer' -CaseSensitive:$false   # 无任何输出
  ```
- 实测值 vs 卡面值：裁定 L49 要求「若改派独立子 agent，则记录 `reviewer_kind=subagent` 及其会话或子任务 ID」；卡面仅记 Agent 名 `reviewer-rustiso` + 中文说明，未写 `reviewer_kind`、未写会话/子任务 ID。
- 缓冲：`AGENTS.md:31-32` 的表述为「记（子 agent 的会话/子任务 ID **或** Agent 名）」，据此记录 Agent 名**已满足 AGENTS.md**；本项是对裁定更细要求的偏离，非 AGENTS.md 违规。
- 影响：`check.ps1` 对 `reviewer` 完全无校验（本项实测确认），导致 reviewer 的正确性与独立性只能人工核验；叠加 P1-1 后风险放大。

**P2-4 — `WONT_FIX_LEGACY` 为本次新造的 finding 处置枚举，未登记进治理协议**

- 文件：行：`doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md:202`、`:212`；定义来源 `doc/reviews/GIT-CLEAN-RUST-ISOLATION-1-LEGACY-SCOPE-RULING-2026-11-17.md:29-33`
- 实测命令：`Select-String -LiteralPath 'doc/09_COLLABORATION.md' -Pattern 'WONT_FIX'` → 无输出（`doc/09_COLLABORATION.md:79` 仅定义 `closed_with_limitations`，`:93` 的资源处置枚举不含此项）
- 实测值 vs 卡面值：卡面按裁定使用该分类并附定义「收口分类，不等于已修复」；协议文档中无此枚举。
- 影响：语义当前清晰且有出处；但作为新增治理词汇未入协议，后续卡片可能各造变体。

**P2-5 — `REBASELINE_PLAN` 移除表外节点条目后未登记终态落点**

- 文件：行：`doc/REBASELINE_PLAN.md:61`（移除）与 `:62-64`（未新增）
- 实测命令：`Select-String -LiteralPath 'doc/REBASELINE_PLAN.md' -Pattern 'GIT-CLEAN-RUST-ISOLATION-1'` → 无输出
- 实测值 vs 卡面值：本卡在 `doc/TASK_LEDGER.md` 已正确计为 terminal（`closed_with_limitations` 66→67、`non-terminal` 7→6、`in_review` 行删除），`check.ps1` PASS；但 Plan 中已无任何提及，历史快照段（`:63`）仅列 `WORKSPACE：CONSOLIDATION-1` 等三张卡。
- 影响：治理计数一致，Plan 侧该卡终态无落点；若后续按 Plan 追终态清单会漏掉本卡。属登记完整性，不属事实错误。

**P2-6 — 裁定原文字节由 DSH 转录保存，本复核无法独立验证「逐字」**

- 文件：行：`doc/reviews/GIT-CLEAN-RUST-ISOLATION-1-LEGACY-SCOPE-RULING-2026-11-17.md:14-15`
- 实测命令：`git log --oneline --all -- 'doc/reviews/GIT-CLEAN-RUST-ISOLATION-1-LEGACY-SCOPE-RULING-2026-11-17.md'` → 仅 `d8a7f1907` 一次引入，此后未被修改
- 实测值 vs 卡面值：文件自述「Codex 当时无法写盘，由 DSH 逐字保存」。仓库侧只能证明「该文件自引入后未再被改动」，不能证明「与 Codex 原始输出逐字一致」——原始 Codex 输出不在仓库内，无对照物。
- 影响：裁定正文的完整性依赖 DSH 的转录纪律；本次复核只能核验「采纳段与卡面一致」「裁定内部自洽」「裁定与所引证据（`r2/DISPOSITION.md:16-22`、`AGENTS.md:54`、`AD-002:24,30`）一致」，不能核验逐字性。该限制已由裁定自身如实披露，故列为 P2 而非 P1。

### 观察（不计 finding）

- 卡面 L204「全部 `PRESERVE_REFERENCED`」：Resource Manifest 三行中 L142 为 `NOT_APPLICABLE`（`—`）。「删除/迁移/归档 = 0」的断言准确；「全部」一词按「有资源的项全部」理解即无误。
- 卡面 L157/L162 记载的遗留探针 `source/.git-probe-tmp.md`（74 B）仍在 `source` 目录且被 manifest 计入。属 `PRESERVE_REFERENCED` 下的历史遗留，与收口无冲突。
- `d8a7f1907` 修复过「收口段自伤的控制字符」。本次对两版 blob 做字节级扫描，`< 0x20`（排除 LF/CR/TAB）与 `0x7F` 均为 0 个，该问题已消除、无复发。

---

## 4. Decision

```
decision: ACCEPTED_WITH_FINDINGS
p0: 0   p1: 1   p2: 6
```

收口在**实质要件**上成立：

1. AC1 仍 `<<PARTIAL>>`、AC3 仍 `<<BLOCKED>>`，两行与父提交**逐字节相同**；AC2/AC4 的 `<<MET>>` 未被改义（问题 1 PASS）。
2. 裁定 Q3 的 7 条限制逐条落地且语义未被削弱；R2-F01…F05 明确为 `WONT_FIX_LEGACY` 且反复声明「不等于已修复」（问题 2 PASS）。
3. `verification/**` 零改动，EV pin 抽样 4/4 匹配（问题 3 PASS）。
4. Resource Manifest 存在、摘要独立重算完全一致、destination 实测存在、19/10,858/190,447,692 逐目录精确吻合（问题 4 PASS）。
5. `check.ps1` exit 0、`PASS (3 warnings)`，且该 PASS 的覆盖面（AC 标记一致性 + closeout 标志 + 资源路径）经源码级确认（问题 5 PASS）。
6. 产品边界论证有 `AGENTS.md:54`、`AD-002:24,30`、`09_COLLABORATION.md:79` 三条直接文本依据，且未发生四类过度外推（问题 6 PASS）。
7. 无 ZCode 自审、无 Lead 自审；reviewer 三处记录一致（问题 7 PASS）。

不构成 REJECTED 的理由：没有任何一条「必须满足才能收口」的要件缺失或可被解释为造假/削弱——AC 字节、证据字节、manifest 摘要、门禁结果、裁定落地均为实测通过。

不构成纯 ACCEPTED 的理由：存在 1 项 P1（reviewer 现值的文档内部矛盾）与 6 项 P2（口径披露、节名指向、reviewer 元数据、新造枚举未入协议、Plan 终态落点、裁定转录可验证性）。

## 5. 该卡能否保持 `closed_with_limitations`

**能保持 `closed_with_limitations`，无需退回 `in_review`。**

依据：

- `doc/09_COLLABORATION.md:79` 给出的两个启用条件之一——「**已批准目标架构取代旧 Task**」——成立：AD-002（2026-10-26 用户裁决）明确移除 Tauri/Rust host，`AGENTS.md:54` 规定其代码与测试仅作历史证据且不再释放 Legacy 实现/诊断/修复任务。收口不属于「无依据的用户裁决替代」，走的是架构取代分支，故无需新的用户裁决。
- 同条其余要求逐项满足：替代依据已记录（裁定文件 + `AGENTS.md`/`AD-002` 引用，卡面 L200–L201）；未完成 AC 与 finding 的原始状态及分类已记录（AC1 `PARTIAL`、AC3 `BLOCKED`、R2-F01…F05 `WONT_FIX_LEGACY`）；**未改写为 PASS**（字节级实测）；声明「除新授权外不恢复实施」（卡面 L194–L196、L218）。
- 机器门禁 `check.ps1` 对该状态的硬性要求（`canonical_evidence_status: complete`、`resource_closeout_status: complete`、AC 标记与勾选一致、允许 `PARTIAL/BLOCKED` 留在终态、资源 destination 存在）全部满足，`exit 0`（`2026-11-17T17:10` 干净快照；工作树漂移后重跑的结果与归因见 §2.5）。
- 资源侧闭环：全部 `PRESERVE_REFERENCED`、删除/迁移/归档 = 0、manifest 摘要一致，符合 `doc/09_COLLABORATION.md:95`「保留不阻止 Task DONE，但必须在 manifest 中闭环」。

**但**：保持该状态不等于本卡可被引用为「并发风险已审查通过」。任何后续引用必须以卡面 L-R2（不得声称达到饱和或已验证 accepted/refused 所有权）与 L-R4（AC4 程序性含义）为准；若出现「本卡已证明 Rust/新架构并发容量安全」的解读，即为误用，应立即纠正。

**建议**（不属本复核授权范围，交 Lead 处置）：P1-1 与 P2-1…P2-6 均为文档级修订，可在下一次涉本卡的治理提交中一并处理，不必为此重开本卡。

---

## 6. 边界与限制声明

**本复核不构成产品发布验收**，不改变任何 Gate 结论，不改变 `doc/STATUS.md` / `doc/REBASELINE_PLAN.md` 的权威指针，不改变父候选 `e34a90d` 与源 `main`，不 push、不集成、不置 `done`。

本复核为**只读**：除本报告文件外未修改、未创建、未删除任何文件；未执行 `git add/commit/push/checkout/reset/clean`；未改动 `verification/**` 与 task-env 内任何字节。

**复核期间工作区并非静止**：`2026-11-17T17:14:39` 的 `doc/tasks/SIDECAR-REBUILD-1.md` 与 `2026-11-17T17:16:18` 的 `doc/STATUS.md` 均为非本复核产生的未提交修改（并发会话所为，归原作者所有，本复核未触碰；`STATUS.md` 的改动已核对不涉本卡条目）。因此本报告的 `check.ps1` 结论绑定于 `2026-11-17T17:10` 的干净快照；在漂移后的工作树上重跑会得到 `FAIL`（详情与归因见 §2.5），该 FAIL 与本次收口无关。

本复核的已知局限：

1. **独立性来源**：本复核者为被审变更作者（Lead/DSH 主会话）派发的独立上下文子 agent；独立性来自上下文隔离，非组织隔离（强度弱于外部 Agent 复核，见 §2.7）。
2. **裁定逐字性不可验证**：裁定正文由 DSH 转录保存，仓库内无原始 Codex 输出可对照（P2-6）。
3. **门禁覆盖面**：`check.ps1` 不校验 `reviewer` 字段、不比对 manifest 内容摘要与卡面声明，相关结论由本复核实测补齐，而非由门禁保证。
4. **未复跑产品测试**：本复核不重跑 Rust 测试或任何构建；AC2 的 `153 passed / 0 failed / 6 ignored / 12 filtered` 未被本复核重新执行，仅核验其记录字节与 `<<MET>>` 语义未被改写。
