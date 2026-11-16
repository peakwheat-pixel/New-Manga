---
review_id: GOV-RESIDUAL-AC7-IMPL-REVIEW
task_id: GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1
kind: implementation-review
reviewer: gov-residual-ac7-reviewer
reviewer_kind: subagent
reviewer_source: DSH fresh 独立上下文派发（只读；未参与实现）。委托消息列出的被审 head 为 54b1167ee；实测该 commit 是 amend 前的悬空前像，真实干净工作区 HEAD = 983243488（详见 §1）。
reviewed_head: 983243488
stated_head: 54b1167ee
stated_head_status: dangling-pre-amend（非 main 可达；内部自相矛盾，见 §1）
date: 2026-11-16
timezone: Asia/Shanghai
conclusion: approved
counts: { P0: 0, P1: 0, P2: 5 }
---

# GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1 AC7 实现独立复核（head 983243488）

> 本文件只由独立 Reviewer 撰写。Reviewer 未参与该实现/返修，运行期间未修改仓库任何文件
> （唯一新增文件即本 review；`--audit-declarations` 的 `--out` 指向 workspace 临时目录，
> 独立探针在 `%TEMP%` 建临时 git fixture）。未 commit、未 push、未改产品代码或测试。
>
> **结论先行**：在真实 HEAD `983243488` 上，AC7 的三条命令全部真实运行且 **EXIT=0**；
> 两处不变量改动与 Ruling D 分支经代码审计 + 四组独立负例/正例探针证明**不是绿洗**
> （真实 fail-closed 仍在，只是不再与「全仓错误绝对计数」耦合）。因此给 **approved**，
> 允许进入集成复验。但 **AC7 本身尚未 done**：集成复验（cleanup 卡 AC6）未做、卡片 AC7
> 仍为 `[ ]`；且委托消息给出的 head `54b1167ee` 是悬空 commit，**AC7 关闭记录必须以
> `983243488` 为准，不得引用 `54b1167ee`**（P2-1）。

---

## 0. 结论摘要

| 判定项 | 结论 | 依据 |
|---|---|---|
| AC7 三条命令是否真实运行且 EXIT=0 | **是 / EXIT=0** | §2 命令表（本 Reviewer 亲自执行，记录命令、EXIT、关键输出） |
| 不变量改动是否削弱 fail-closed（绿洗） | **否，但两处替换守卫本身不可触发（P2-2）** | §4 代码审计 + 探针 A/B/C/D |
| Ruling D（带行级身份不再校验整文件 sha）是否合理 | **合理缩小过宽绑定，但存在未覆盖风险** | §4.2、§5、P2-3 |
| 历史证据字节是否被触碰 | **否** | §5（HIE 4 条绑定 sha 实测全匹配；`verification/**` 无 M/D；RRI 文件 blob 三处一致） |
| `residual-runtime-identity.json` RRI-01..07 是否逐字节未变 | **是** | §5.3（blob `ae45f098…` 在 `a6608dd4b`/`70b984ab7`/HEAD 完全相同） |
| AC7 是否已可标 done | **否** | 集成复验未做；卡片 AC7 仍 `[ ]`；head 记录需更正（§8） |
| 本 review 的 `approved` 含义 | **实现侧通过、可进入集成复验** | 不等于 AC7 已完成 |

**与委托叙述不一致、必须纠正的事实（独立核实）：**

1. 委托消息说「被审 head：54b1167ee（git 已提交，工作区干净）」。实测 `54b1167ee` 是
   **悬空 commit**（`git fsck` 报 unreachable；不在任何分支），且**内部自相矛盾**：
   其 `clean_workspace.py` 的 `HISTORICAL_EVIDENCE_DIGEST` 已写成 `c91bbef8…`，但该 commit
   的 HIE 政策文件 canonical digest 实测仍是 `5cc68358…` ⇒ 若真的以 `54b1167ee` 为 head，
   HIE 层会报 `POLICY_DIGEST_MISMATCH`、residual 层早退，测试不可能 13/13 OK。
   reflog：`54b1167ee` 是 2026-11-16 14:16:35 的 commit，2026-11-16 14:16:43 被
   `commit --amend` 成 `983243488`；两者差异**恰好只有** HIE JSON 的那 1 行 message
   （`untracked`→`tracked`）。真实干净工作区 HEAD = `983243488`。
2. 提交信息声称证据日志含「13 tests OK 原文」，但该日志的 `### 测试原始输出（rc=0）`
   一节**为空**，全仓库 `git grep "Ran 13 tests"` 零命中；详见 P2-5。
3. `--audit-declarations` 的 EXIT 仍是 **2**（154 条与 residual 层无关的历史声明债务），
   这**不是** AC7 三条命令的结果，也不属于 AC7 判定范围；AC7 三条命令的 EXIT 全部为 0。

---

## 1. 被审对象与 head 事实

### 1.1 head 核实（独立实测）

| 检查 | 命令 | 实测结果 |
|---|---|---|
| 当前 HEAD | `git rev-parse HEAD` | `9832434889339a1a89cb9a848114d5363de183ff` |
| 工作区 | `git status --porcelain` | 0 行（clean） |
| 分支 | `git branch --show-current` | `main` |
| 委托 head 可达性 | `git fsck --no-reflogs --unreachable` / `git branch -a --contains 54b1167ee` | `54b1167ee` **unreachable**；无分支包含它 |
| reflog | `git reflog show --date=iso` | `54b1167ee`（14:16:35 commit）→ `983243488`（14:16:43 amend） |
| 两 commit 差异 | `git diff --stat 54b1167ee 983243488` | 仅 `tools/governance/historical-evidence-interpretation.json` 1 行 |
| 54b1167ee 自洽性 | 用 python 复算 HIE canonical digest | 常量 `c91bbef8…` ≠ 实际 `5cc68358…`（**不一致**） |
| 983243488 自洽性 | 同上 | 常量 `c91bbef8…` = 实际 `c91bbef8…`（一致） |
| 983243488 父提交 | `git show -s --format=%P` | `70b984ab7`（= R14 收尾 head） |

**结论**：本轮唯一可复核、可满足 AC7 的 head 是 **`983243488`**。委托消息的
`54b1167ee` 是 amend 前 8 秒的中间态，既非 main 可达、又自相矛盾，不能作为 AC7
的固定 head 入档（P2-1）。本 review 的 `reviewed_head` 取 `983243488`。

### 1.2 被审 commit 的改动面（`git show --name-status`）

`983243488`（4 个路径）：

```
M  tools/governance/clean_workspace.py
M  tools/governance/historical-evidence-interpretation.json
M  tools/governance/tests/test_residual_runtime_identity.py
A  verification/GOV-DECLARATION-SCAN-CLEANUP-1/ruling-cd-invariant-rewrite-2026-11-16.log
```

`54b1167ee`（3 个路径）：`M clean_workspace.py`、`M tests/…`、`A verification/…/ruling-cd…log`
——**缺少 HIE JSON 改动**，这正是它 digest 自相矛盾、不能通过自身检查的原因。

### 1.3 复核环境（证据纪律 §4.3.12 要求的头）

| 项 | 实测值 |
|---|---|
| 工作目录 | `G:\CODEX\New Manga` |
| shell | pwsh `7.6.8`（`C:\Program Files\PowerShell\7\pwsh.exe`） |
| Python | `3.14.6`（`C:\Python314\python.exe`） |
| Git | `2.52.0.windows.1` |
| 运行窗口 | 2026-11-16 14:18–14:26 +08:00 |

---

## 2. 命令实测（AC7 三条 + audit）

### 2.1 AC7 三条命令（逐条原始命令 / EXIT / 关键输出）

| # | 原始命令（cwd = `G:\CODEX\New Manga`） | EXIT | 关键输出（原文） |
|---|---|---:|---|
| 1 | `$env:PYTHONPATH="tools/governance"; python -B tools/governance/tests/test_residual_runtime_identity.py` | **0** | 末两行：`Ran 13 tests in 20.862s` / `OK`；stderr 有大量 `ResourceWarning: unclosed file … clean_workspace.py:2292`（**已知 P2、与 EXIT 无关**，沿用 AC7 裁决的观察） |
| 2 | `pwsh -NoProfile -File tools/governance/check.ps1` | **0** | `Governance scope: 15 current documents; no historical directory scan.` / `Task: doc\tasks\MAINT-1-RELEASE-MONITOR.md` / 3 条 WARN（13 个非终态 Task；STATUS.md 3093 bytes/28 lines 达 80%；REBASELINE_PLAN.md 6990 bytes/64 lines 达 80%）/ `Governance check: PASS (3 warnings)` |
| 3 | `git diff --check` | **0** | 无任何输出；运行前后 `git status --porcelain` 均 0 行 |

补充实测（不替代 AC7 指定命令，仅补强）：

| 命令 | EXIT | 结果 |
|---|---:|---|
| `git show --check 983243488` | 0 | 无 whitespace 错误输出（补足 `git diff --check` 在干净树上不检提交内容这一盲区） |
| `git diff --check a6608dd4b..HEAD` | 0 | 本卡工作区间无 whitespace 错误 |

> 边界说明：AC7 指定的 `git diff --check` 在干净工作区上**必然** 0 输出（它只检查工作区
> unstaged 差异）。这是命令字面要求的合法结果，但它本身几乎无判别力；真正的提交级
> whitespace 复核见上表补充项。

### 2.2 `--audit-declarations`（不属于 AC7 三条命令，单列）

原始命令：

```
$env:PYTHONPATH="tools/governance"
python -B tools/governance/clean_workspace.py --audit-declarations --out "G:\CODEX\New Manga.workspace\temp\GOV-RESIDUAL-AC7-REVIEW-2026-11-16"
```

| 项 | 实测值 |
|---|---|
| EXIT | **2**（**原因 = 154 条无关历史声明债务**；见下方区分说明） |
| stdout 末行 | `declaration audit: 6744 declaration(s), 5585 protected root(s), 154 error(s), 732 warning(s)` |
| 报告文件 | `G:\CODEX\New Manga.workspace\temp\GOV-RESIDUAL-AC7-REVIEW-2026-11-16\declaration-audit.json`（242571 B） |
| `counts.errors` | **154** |
| `counts.protected_roots` | **5585** |
| `counts.declarations` / `counts.warnings` | 6744 / 732 |
| `counts.by_disposition.PRESERVE_USER_DATA` | **21** |
| `code == SOURCE_DRIFT` 条数 | **0** |
| `code == POLICY_INVALID` 条数 | **0** |
| `code == ERROR_MISMATCH` 条数 | **0** |
| `DECL_RESIDUAL_RUNTIME_PRESERVED` warning 数 | **7**，locator 恰为 `RRI-01/ALREADY_ABSENT_PATH` … `RRI-07/PRESERVE_ROOTS` |

**必须区分的两件事**（勿混为一谈）：

- **AC7 的三条命令**：上述 §2.1，三条全部 **EXIT=0**。
- **audit 的 EXIT=2**：由 154 条与 residual 层无关的历史声明错误造成
  （`TABLE_SCHEMA_INCOMPLETE` 53、`DECL_RELATIVE_UNRESOLVED` 26、`DECL_ENV` 16、
  `DECL_GLOB` 16、`DECL_DESTINATION_UNRESOLVED` 11、`TABLE_DELIMITER` 10、
  `DECL_UNKNOWN_DISPOSITION` 8、`DECL_TRAVERSAL` 7、`JSON_PARSE` 2，其余各 1）。
  这是 **`GOV-DECLARATION-SCAN-CLEANUP-1` 的 AC3 范围**，不属于 AC7，也不阻塞 AC7。

### 2.3 独立复算保护集合 delta（不依赖任何人的叙述）

用 `clean_workspace` 模块 API 独立跑两遍扫描（屏蔽 residual 层得前像，与测试套件同一注入
技术、但由本 Reviewer 独立执行）：

| 指标 | residual 层屏蔽（前像） | HEAD 实跑 | 差 |
|---|---:|---:|---:|
| 声明错误数 | 161 | 154 | **−7**（恰为 7 条裁定身份） |
| 保护根数 | **5582** | **5585** | **+3** |
| 新增根 | — | `c:/users/49745/appdata/roaming/com.newmanga.m2rc1.desktop/{catalog,data,derived}` 恰 3 个 | 与 APPDATA 三根一致 |
| 丢失根 | — | **0 个**（dropped = `[]`） | 保护集合未缩小 |
| 三根 disposition | — | 每根同时含 `PRESERVE_REFERENCED`（RRI-06）与 `PRESERVE_USER_DATA`（RRI-07） | 与政策一致 |
| `evaluate(appdata/<suffix>)` | 前像三根均 False | 后像三根均 **True** | 按路径核验成立 |
| residual warning | 0 | 7（id = RRI-01…RRI-07） | 层已恢复 |
| 与 residual 无关的错误 | 154 | **154（原样保留，未被吞掉）** | 符合 Ruling C 设计 |

> 注：裁定文/证据日志里的「基线 167」「PRESERVE_USER_DATA 18」是**更早时点**的引用值，
> 本轮未重测那个历史时点；本轮可独立复核的是 HEAD 侧前像 **161 / 5582** 与后像
> **154 / 5585**，以及 21 与「18+3」的差值自洽。

---

## 3. AC7 判据逐条核对

AC7 原文（`doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md:52`）拆为 3 条 + 1 个总则：

| 判据 | 结论 | 依据 |
|---|---|---|
| ① 三条命令真实运行并记录命令与 EXIT | **实现侧满足** | §2.1 由本 Reviewer 亲自运行并记录；但交付侧 committed log 的 raw 证据不足（P2-5），AC7 关闭前须补集成 raw log |
| ② 固定 head 交独立 Reviewer | **满足，但 head 标识须更正** | 实际 head = `983243488`，本 review（独立上下文、未参与实现）已只读复核；委托消息的 `54b1167ee` 为悬空前像，**不得写入 AC7 记录**（P2-1） |
| ③ 集成复验后才 done | **未完成** | cleanup 卡 AC6 仍 `[ ]`；residual 卡 AC7 仍 `[ ]`；本 review 只是前置，不是集成复验 |
| 总则：AC7 是否已满足 | **否（尚未 done）** | ②③ 的收尾动作未做；本 review 给出 approved 仅代表「实现侧可进入集成复验」 |

**判定口径说明**：`approved` 在本文中的含义严格限定为
「三条命令 EXIT=0 + 独立判断不变量改动不是绿洗 + 未发现 P0/P1」，
**不等于** AC7 已满足、也不授权把 AC7 标 done。AC7 的最后两步（集成复验、卡片回填）
必须按 §8 完成。

---

## 4. 不变量改动是否绿洗（独立审计 + 独立探针）

### 4.1 两处 Ruling C 改动的逐行审计

改动前（`70b984ab7` 的 `clean_workspace.py:2178` 附近）：

```python
require(len(removed) == 7 and len(index.errors) == 7, "ERROR_MISMATCH",
        "residual identity batch does not cover exactly the seven errors")
staged.errors = [e for e in staged.errors if e not in removed]
...
require(not staged.errors, "POLICY_INVALID",
        "residual identity interpretation left fatal errors")
```

改动后（HEAD `:2190`、`:2210`）：

```python
require(len(removed) == 7, "ERROR_MISMATCH", …)
staged.errors = [e for e in staged.errors if e not in removed]
...
require(not [e for e in staged.errors if e in removed], "POLICY_INVALID", …)
```

**审计结论（逐项）：**

1. **删掉 `len(index.errors) == 7`：合理，不是放宽失效。**
   真正的判别力在它上方的逐身份校验（HEAD `:2133`）：
   `require(error["file"] == origin and index.errors.count(error) == 1 and error not in removed, "ERROR_MISMATCH", …)`。
   7 个 binding × 每个恰 1 条 error 的 schema 校验（`:2127-2136`）+ binding 集合恰为
   RRI-01..07（`:2074-2077`）⇒ 只要任一裁定身份缺失/重复/文本变化，都会在这里
   fail-closed，而**不是**依赖全仓错误总数。与 residual 层无关的错误继续留在
   `staged.errors` 并由 audit 报出（实测 154 条原样保留、未被吞掉）。
2. **`require(not staged.errors)` → 成员过滤：行为上是设计变更（Ruling C 明文批准），
   但该替换守卫本身不可触发（P2-2）。**
   `staged.errors` 在 `:2192` 已被过滤，`require` 在 `:2210` 才执行，中间只追加
   declarations/warnings（`_register_protective` 已实测不追加 error）⇒ 该表达式恒为真。
   同理，`:2190` 的 `len(removed) == 7` 在「7 个 binding、每个恰 1 条 error、且逐条
   已通过 :2133」之后也恒为真。**两处替换守卫均为 dead guard**：它们不是 fail-open
   （过滤器保证了移除），但也不是真正的防线；真正的防线是 `:2133`。Ruling C 的
   注释/卡片叙述把这两处描述为「保障」，属于表述过强，应更正（P2-2）。
3. **结论：不是绿洗。** 绿洗的定义是「放宽行为、却让检查看起来仍失败即停」。
   这里被删掉的是「全仓错误恰好 7 条」这一**仓库前提**，而 residual 层自身的
   fail-closed 仍然存在（探针 B/C/D 实证）。但「不可触发的替换守卫 + 仍保留的旧注释」
   会让后来者误以为这两处还在起作用，这是必须修的表述/实现瑕疵。

### 4.2 Ruling D（`if not has_line:`）审计

改动：带 `origin_line` + `origin_line_raw_sha256` 的 binding，不再校验整文件
`origin_raw_sha256` / `origin_byte_length`；无行级身份的 binding 照旧校验整文件。

**判断：合理的「相对不变量」，不是绿洗；但有未覆盖风险（P2-3）。**

- 事实核查：`residual-runtime-identity.json` 中带行级身份的只有 **RRI-01/02/03**
  （均绑 `doc/tasks/P19.md` 的 :112/:113/:114）；RRI-04..07 **无行级身份**，整文件校验
  仍然生效（见 §5.2 实测）。
- 事实核查：`doc/tasks/P19.md` 当前 **21306 B**，与 policy 里旧的整文件 sha/18443 B
  已不匹配（该文件在 `0e7bc1fc5` 被合法追加），但三份行级 sha **全部仍匹配**。
  ⇒ 原整文件绑定确属**过宽绑定**：它把「卡上别处永不变」当成本层不变量，已被一次
  合法治理操作击穿。Ruling D 的收窄有实测依据。
- 风险（未覆盖）：该层从此**不再**拦截 `P19.md` 绑定行以外的字节漂移；`git` 历史与
  「禁止改历史卡字节」的治理规则仍在，但不由本层自动 fail-closed。另外 policy 中
  RRI-01/02/03 的 `origin_raw_sha256`/`origin_byte_length` 仍是旧的 18443 字节值，
  现已**不被校验**，属于会误导读者的冗余字段（P2-3）。

### 4.3 独立探针（不依赖被审测试，自己构造并自己断言）

用测试套件的 `FixtureRepo` 拓扑（把三份真实 origin 复制进临时 git repo，policy digest
按 fixture 重算）独立构造 4 个探针：

| 探针 | 构造 | 实测结果 | 判定 |
|---|---|---|---|
| **A（Ruling D 正例）** | 在 fixture `doc/tasks/P19.md` **尾部**追加 `\n`（不改变 :112-114 行） | errors=**0**、residual=**7** | Ruling D 预期行为成立（旧代码此处会报 SOURCE_DRIFT） |
| **B（行漂移负例）** | 改 fixture `P19.md` 的 **:112 绑定行**内容（保留 EOL） | errors=6 且含 **SOURCE_DRIFT**、residual=**0**、原裁定身份未被降级 | fail-closed 成立 |
| **C（身份缺失负例，Ruling C §5① 的对应场景）** | 行字节不动；篡改 fixture policy 中 RRI-01 的 error message（再重算 digest） | errors=8，末项 **ERROR_MISMATCH**、7 条原错误仍在、residual=**0** | **成员不变量真实 fail-closed**；证明真正防线在 `:2133`，不是那两处 dead guard |
| **D（无行级整文件漂移负例）** | 对 **RRI-04** 的 `verification/ENV-BUNDLE-1-FU1/resource-manifest.json` 尾部追加 | errors=8，末项 **SOURCE_DRIFT**、residual=0 | `if not has_line` 分支仍强制整文件 sha |

> 探针 A–D 均在本机 `%TEMP%` 的一次性 git fixture 中完成并清理；未触碰仓库文件。

### 4.4 绿洗判断的最终表述

- **不构成 fail-open / 绿洗**：三处改动都没有让「应失败的场景变绿」；
  探针 B/C/D 与 audit 的 0/0/0（SOURCE_DRIFT/POLICY_INVALID/ERROR_MISMATCH）
  都表明应拦的仍拦。
- **但也不是「更严」**：两处替换守卫不可触发；Ruling D 是「把过宽绑定收窄到行级」，
  属正确性修正而非安全增强。任何「本层因此更安全」的表述都应改成「本层因此不再误报，
  真正的判别力在 :2133 与整文件校验分支」。
- **有 5 个 P2 级瑕疵**（§6），均不阻断 AC7 的「实现侧通过」判定，但应在集成复验
  或后续小卡中处理；其中 P2-4/P2-5 与「Ruling C 的强制负例」「证据纪律」直接相关，
  建议随集成复验一并补齐。

---

## 5. 字节保留核验（历史证据 / RRI 身份）

### 5.1 HIE 4 条 origin 绑定（python 实测，非引用日志）

| 绑定 | origin_file | raw_sha256 匹配 | 实际字节 | 实际 tracked | expected_tracking |
|---|---|:--:|---:|:--:|---|
| `HIE-T01` | `verification/P09-GOVERNANCE-DEBT-20261019/codex-closeout-p19-view-r12.md` | **True** | 23845 | tracked | tracked |
| `HIE-O01` | `verification/P14/owner-initiated-dsh-self-review-r1.md` | **True** | 3288 | tracked | tracked |
| `HIE-O02` | `verification/P14/owner-initiated-dsh-self-review-r2.md` | **True** | 3433 | tracked | tracked |
| `HIE-O03` | `verification/P22/codex-p22-task-r4-malformed-snapshot-7ebd7d40.md` | **True** | 21531 | tracked | tracked |

`reference_guards`（HIE-REF01/02）不是字节绑定（无 `raw_sha256` 字段），不参与本项判定。

### 5.2 HIE 政策文件的改动内容（`a6608dd4b..HEAD` 仅 2 个字段）

```diff
 HIE-O03.expected_tracking: "untracked" -> "tracked"
 FILE_UNREADABLE message:   "untracked markdown …" -> "tracked markdown …"
```

- **没有**修改任何 `raw_sha256` / `byte_length` / `origin_file`；没有触碰任何
  `verification/**` 历史证据字节。
- `clean_workspace.py` 的 `HISTORICAL_EVIDENCE_DIGEST` 在 HEAD 实测为 `c91bbef8…`，
  与 HIE 文件 canonical digest **一致**；该常量重批是政策文本变化的必然连带项。
- `983243488` 的 `--name-status` 见 §1.2：`verification/**` 下**只有 1 个 A**
  （本卡的新证据日志，属 `GOV-DECLARATION-SCAN-CLEANUP-1` 的 allowed_paths），
  **没有**任何 `M`/`D`；`doc/tasks/**` **零改动**。
- `54b1167ee` 的 `--name-status`：同样无 `verification/**` 的 M/D、
  无 `doc/tasks/**` 改动（只有 A 新日志 + 2 个 M 治理文件）；但它缺少 HIE JSON 改动，
  不能作为交付 head（§1.1）。

### 5.3 RRI-01..07 身份逐字节未变

| 检查 | 结果 |
|---|---|
| `git diff --stat a6608dd4b..HEAD -- tools/governance/residual-runtime-identity.json` | **空**（0 行） |
| 工作区 `git diff --stat -- tools/governance/residual-runtime-identity.json` | **空** |
| blob 对比 | `a6608dd4b` / `70b984ab7` / `983243488` 均为 **`ae45f0989786718b6bf1be6c95865872683cf018`**（同一 blob） |
| policy canonical digest | 实测 `5a47481d…51b88`，与 `RESIDUAL_RUNTIME_IDENTITY_DIGEST` 一致；文件 8689 B |
| RRI-04..07 整文件 sha | 均 **匹配**（3784 / 4027 / 4027 / 4027 B） |
| RRI-01..03 | 整文件 sha **不再匹配**（P19.md 现 21306 B，policy 旧值 18443 B 时代），但 **:112/:113/:114 三份行级 sha 全部匹配** —— 这正是 Ruling D 的事实前提，不是本 commit 改坏的 |

---

## 6. Findings（P0/P1/P2）

**P0：0；P1：0**（未发现必须阻断「实现侧通过」的问题：三条命令 EXIT=0、真实 fail-closed
未被削弱、历史证据字节未被触碰）。

**P2：5**

### P2-1 head 标识漂移：委托的 54b1167ee 是悬空且自相矛盾的 pre-amend commit

- **位置/证据**：`git fsck --unreachable`、reflog（14:16:35 → 14:16:43 amend）、
  `git diff --stat 54b1167ee 983243488`（仅 HIE JSON 1 行）、54b1167ee 的
  `HISTORICAL_EVIDENCE_DIGEST=c91bbef8…` 与其 HIE digest `5cc68358…` 不一致。
- **影响**：若把 54b1167ee 写进 AC7 记录，证据不可复现（commit 悬空、会被 gc），
  且该 tree 自身无法通过 HIE 政策校验；后续任何人按此 hash 复核都会得到相反结果。
- **建议**：AC7 注释/Handoff/台账一律引用 **`983243488`**；本 review 的
  `reviewed_head` 即 983243488。不要 commit 54b1167ee 的任何引用。

### P2-2 两处替换守卫不可触发（dead guard），注释与 Ruling C 叙述过强

- **位置**：`clean_workspace.py:2190`（`len(removed) == 7`）与 `:2210`
  （`not [e for e in staged.errors if e in removed]`）；`:2187` 注释还把行号写成
  `:2126`（实际判别在 `:2133`）。
- **证据**：7 个 binding、每个恰 1 条 error，且 `:2133` 逐身份校验通过 ⇒ `:2190`
  恒真；`:2192` 先过滤、`:2210` 后检查且中间无 error 追加 ⇒ 恒真。探针 C 证明真正
  的 fail-closed 在 `:2133`。
- **影响**：不影响实际安全，但会误导后来者以为这两处是防线；也削弱 Ruling C
  「保留守卫」叙述的可信度。
- **建议**：把 `:2190` 改成可触发的断言（或在注释中明确「defense-in-depth,
  当前控制流下不可达」）；`:2210` 删除或改成对「移除数量 == 7」的非空断言；
  修正 `:2187` 的行号引用。

### P2-3 Ruling D 的未覆盖风险与 policy 冗余字段

- **位置**：`clean_workspace.py:2115-2126`；`residual-runtime-identity.json` 的
  RRI-01/02/03（`origin_raw_sha256=243093ab…`、`origin_byte_length=18443`，
  实际 P19.md 21306 B）。
- **风险**：① `P19.md` 非绑定行的字节漂移不再被本层拦截（仅剩 git 与治理规则约束）；
  ② 上述字段已不被校验，成为误导性冗余；③ 测试集中没有「尾追加应通过」（探针 A）
  与「无行级整文件漂移应失败」（探针 D）的用例，行为变更未入库固化；
  ④ RRI-04..07 仍为整文件绑定，若这两份 manifest 未来被合法修改，同类过宽绑定会复发。
- **建议**：新增两条 fixture 用例（A/D）；在 policy 中把不再校验的字段标注为
  `unenforced`（或更新为当前值并在注释说明「行级为权威」）；对 RRI-04..07 是否也可能
  变成可变文件留一句裁定口径。

### P2-4 Ruling C 强制负例①缺失 + 测试名与断言相反

- **位置**：`tools/governance/tests/test_residual_runtime_identity.py`。
- **证据**：Ruling C §5「必须补的负例」① 是「7 条身份中少一条 ⇒ `ERROR_MISMATCH`」；
  测试集中无此用例（`git grep ERROR_MISMATCH` 仅命中一处 **否定**断言）。
  `test_unbound_error_blocks_the_stage` 名字说「block」，新断言却验证「unrelated error
  **不** block 且 7 条照常降级」——名字与行为相反。
- **影响**：代码行为正确（探针 C 已实证），但缺回归保护；cleanup 卡 AC4 的
  「Ruling C 已实施」在测试证据上不完整。
- **建议**：补 ① 的 fixture 负例（可仿探针 C：篡改 policy error message + 重批
  fixture digest，或注入 scanner 规则变化）；把 `test_unbound_error_blocks_the_stage`
  改名为 `test_unrelated_error_does_not_block_the_stage`（或类似）。

### P2-5 交付侧证据日志不满足 §4.3.12，且提交信息有一处不实

- **位置**：`verification/GOV-DECLARATION-SCAN-CLEANUP-1/ruling-cd-invariant-rewrite-2026-11-16.log`；
  `983243488` 的 commit message。
- **证据**：① 日志 `### 测试原始输出（rc=0）` 一节**为空**，无 `Ran 13 tests`/`OK`
  原文，无 shell/解释器头（`git grep "Ran 13 tests"` 全仓零命中）；② commit message
  却写「证据：…log（…13 tests OK 原文）」，与日志实际内容不符；③ 按
  `doc/09_COLLABORATION.md:359`（§4.3.12 证据纪律），只写「N passed」而无
  EXIT+shell/venv 头与逐次入库的日志「按未提供处理」。
- **影响**：交付侧单凭该 log 无法独立复核 AC7 命令 1；本 review 的亲自运行可作为
  Reviewer 侧证据，但不能代替交付侧日志。AC7 关闭前必须由集成复验补 raw log。
- **建议**：集成复验时附完整 raw 输出（含 `PowerShell 7.6.8` / `Python 3.14.6` /
  `git 2.52.0` 头、三条命令、EXIT、以及 audit 的 baseline/after JSON）；更正 commit
  message 或日志中「原文」的说法；不要再用汇总散文代替可复核日志。

---

## 7. 未覆盖风险与边界声明

1. **`P19.md` 非绑定区不再受本层保护**（Ruling D 的直接后果）：本层只 pin :112-114
   三行；其余字节若有漂移，只有 git 历史与「禁止改历史卡字节」的治理规则兜底，
   不产生自动 fail-closed。这是设计取舍，但应登记为已知风险（P2-3）。
2. **audit EXIT=2 在 AC3 完成前恒为 2**：退出码不再携带「residual 层健康」信号；
   自动化若只看 EXIT 会误判。必须按 `counts.errors` 与 code 分布对比（本 review 的
   §2.2 给出本轮快照）；residual 层若回归，会以新增 `SOURCE_DRIFT`/
   `POLICY_INVALID`/`ERROR_MISMATCH` 或 residual warning ≠ 7 的形式出现，而不是
   EXIT 变化。
3. **机器/用户绑定的绝对路径**（`C:/Users/49745/...`）：`require_present` 与测试中的
   `G:/CODEX/New Manga.workspace` 都是本机硬编码；换机/换用户时本 review 的 AC7 结论
   不自动成立。该风险已在 cleanup 卡「附带发现 R-2」登记，本 commit 未引入也未修复。
4. **`check.ps1` 的 scope 不含本卡**：`Governance scope: 15 current documents`，
   运行 Task 是 `MAINT-1-RELEASE-MONITOR.md`；AC7 要求的 check EXIT=0 已满足，
   但 PASS 不能当作本卡文档指针/生命周期的语义证据（此点 AC7 裁决报告已指出）。
5. **`git diff --check` 在干净树上无判别力**：AC7 字面命令 EXIT=0，但只能说明工作区
   unstaged 差异无 whitespace 错误；提交级复核用 `git show --check 983243488` 补做，
   亦为 0。AC7 关闭记录若只写这一条，判别力有限，建议同时记录补充命令。
6. **ResourceWarning 噪声**：命令 1 的 stderr 有大量 `unclosed file`（`clean_workspace.py:2292`），
   属既有技术债（AC7 裁决已记 P2），不影响 `Ran 13 tests / OK / EXIT=0`；但若后续
   用 `-W error` 或 CI 把 stderr 当失败会误红，应知悉。
7. **未重测历史基线**：本轮未重测「167 条 / 5582 / 18」对应的更早 head；§2.3 的基线是
   在 HEAD 上屏蔽 residual 层得到的 **161 / 5582**，用于证明「本层移除 7 条、新增 3 根、
   不吞无关错误」是充分的；但不宣称复现了裁决报告的所有历史数字。
8. **`54b1167ee` 的存在性**：该 commit 目前仅因 reflog 暂存而可读，未来 `git gc` 后
   将不可达；任何文档引用它都会变成不可复核证据（P2-1）。

---

## 8. AC7 关闭前必须完成的事项（交给 DSH/Integrator）

1. **固定 head 更正**：AC7 注释、Handoff、台账一律写 `983243488`；
   明确删除/不引用 `54b1167ee`（P2-1）。
2. **集成复验**（cleanup 卡 AC6）：在集成 head 上重新真实运行 AC7 三条命令，附
   **raw 日志**（shell/解释器头 + 命令 + EXIT + 输出），并附 audit 的 baseline/after
   JSON；注意 `--audit-declarations` 的 EXIT=2 与 AC7 三命令 EXIT=0 要分开记录（§2.2）。
3. **重算并记录数字**：集成 head 上的 `counts.errors` / `counts.protected_roots` /
   `SOURCE_DRIFT` / `POLICY_INVALID` / `ERROR_MISMATCH` / residual warning 7 条 /
   APPDATA 三根；若 AC3 推进导致计数变化，不要把本 review 的 154/5585 硬编码进新证据。
4. **P2 处置**：至少补 Ruling C §5① 负例（P2-4）、补 Ruling D 的 A/D 行为测试（P2-3）、
   更正证据 log 空节与 commit message 的「原文」表述（P2-5）；P2-2 的 dead guard 可
   在注释中标注或在后续小卡清理。
5. **回填 AC7**：把 `[ ] … <!-- blocked: … -->` 整体替换为「三命令实测 + 本 review +
   集成复验」的记录，按 §4.3.1 权威优先级更新 `status`；同步 TASK_LEDGER / STATUS /
   REBASELINE_PLAN 的指针。只有 1–5 全部满足后，AC7 才可标 done。

---

## 9. 复核方法、只读声明与可复现性

- **只读**：除本 review 文件外，未修改仓库任何文件；未 commit / push / reset / stash；
  `--audit-declarations` 仅写 `G:\CODEX\New Manga.workspace\temp\GOV-RESIDUAL-AC7-REVIEW-2026-11-16\`；
  独立探针在 `%TEMP%` 的临时 fixture 中运行并清理。复核开始/结束的
  `git status --porcelain` 均为 0 行（本 review 写入前）。
- **head 事实**：`git rev-parse` / `git fsck` / reflog / blob 对比 / 穷尽 `git grep`，
  见 §1；未信任 commit message 与任何人的叙述。
- **命令**：全部在本机 `G:\CODEX\New Manga` 以 pwsh 7.6.8 + Python 3.14.6 + git 2.52.0 实跑，
  原始命令与 EXIT 见 §2。
- **独立探针**：复制真实 origin 到临时 git repo（与测试套件同一 fixture 拓扑），由本
  Reviewer 自写断言（§4.3），不与被审测试共享断言代码路径。
- **证据文件**：audit JSON 落在上述 workspace 临时目录；review 本身是唯一入库产物。
- **可复现性声明**：§2/§4 的所有命令与探针均可在 `983243488` + 本机环境上复跑；
  若 `P19.md` 或 policy 在未来变化，数字应重测而非沿用本文。

---

**Reviewer**：`gov-residual-ac7-reviewer`（DSH fresh 独立上下文子 agent；未参与实现；
只读被审 head `983243488`）
