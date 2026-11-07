---
task: FEA-11-L-R11-GATE-UNIFY-PREREQ-1
title: C-16 v1.7 UNFREEZE 独立 byte-level 复核（r1）
reviewer: fresh subagent（独立上下文；未参与 C-16 v1.7 起草、前轮复核或实现；parent session-3ac1953a-094e-4339-889a-284df2b7b34d）
session: 9bc4c117-e171-48b6-8f13-582845d2e12f
reviewed_head: 07a7d746a52fc035c728a4fa4c3d1a1df624ecfa
reviewed_worktree_sha256: 67286eeca8cb2109f35445c6b925b03053c483293b1bdb19e56efdc9965b657d
verdict: approved
p0: 0
p1: 0
p2: 0
p3: 7
date: 2026-11-07
---

# C-16 v1.7 UNFREEZE 独立 byte-level 复核（r1）

## 0. 结论先行

- **结论：`approved`**。P0=0 / P1=0 / P2=0 / P3=7。P3 均为非阻断的记录/口径/提交隔离项；其中 **P3-01 要求提交时隔离包外文档**，P3-03/P3-04 若现在修改会改变 C-16 字节并触发新的 pin/复核，建议接受或在后续 UNFREEZE 处理。
- **被审字节**：`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` 工作树 SHA-256 `67286eeca8cb2109f35445c6b925b03053c483293b1bdb19e56efdc9965b657d`；`git hash-object` `3cd9d2fbf79bd37b3fc35e1895efa1c75d2fc232`。二者与冻结记录 §1/§1B/§11、载体 §7.3、`verify_pins.ps1` 的 C16 值一致。
- **diff 范围**：`git diff --stat -- doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` = **1 file changed, 7 insertions(+), 6 deletions(-)**。仅 §2.4 per-page 授权匹配（`:90`）、§2.4 兼容句（`:93`）、§0 版本面行、头部状态/载体链接/日期、§10 冻结条件 ⑨ + 变更记录 v1.7；无其他条款字节。
- **门禁**：`verify_pins.ps1` **18/18 PASS**（C16 `67286eec…`；其余 17 与 HEAD 实测不变）；`check.ps1` 默认与 `-TaskPath` 均 **PASS（3 warnings）**；`git diff --check` 退出 0。
- **零漂移**：C-17/C-06/C-15/C-07/M2-C1 及其余 12 份契约 blob 与 HEAD 相同；`src/**`、`apps/**`、`tests/**`、`tools/**`、`doc/contracts/**` 零 diff；无新错误码/命令/能力/wire 字段/TTL/schema/依赖。
- **需要 Lead 在提交前处理的一项**：工作树另有两处包外未提交文档（`doc/STATUS.md`、`doc/handoffs/DSH-HANDOFF-2026-11-06.md`），不属于本 UNFREEZE 包；见 P3-01。UNFREEZE 提交必须只 stage 本包文件。

## 1. 基线与只读事实

- 仓库：`G:\CODEX\New Manga`；分支 `main`；HEAD `07a7d746a52fc035c728a4fa4c3d1a1df624ecfa`（已 push；`doc/STATUS.md` 工作树内容也记为该值）。
- 审查者：Lead 派发的独立上下文 fresh subagent，session `9bc4c117-e171-48b6-8f13-582845d2e12f`；未参与 C-16 v1.7 的起草、前轮复核或实现。
- 只读边界：未运行 `git add/commit/push/reset/checkout`；未改 C-16/冻结记录/矩阵/载体/卡/证据任何字节。唯一仓库写入为本报告。
- 初始 `git status --porcelain`（22:35 左右）：5 个 tracked 修改（`doc/STATUS.md`、`doc/handoffs/DSH-HANDOFF-2026-11-06.md`、C-16、FROZEN-C16、矩阵）+ 1 个未跟踪载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-L-R11.md`。
- 复核期间（22:36–22:38）作者并发写入证据目录 `verification/FEA-11-L-R11-GATE-UNIFY-PREREQ-1/`（EV.md、`unfreeze.diff`、`logs/{pins,check,check-taskpath,unfreeze-diffstat}.log`）；**不是本报告作者的写入**，属本包证据。
- PREREQ 卡 `doc/tasks/FEA-11-L-R11-GATE-UNIFY-PREREQ-1.md` 已在 HEAD `07a7d746a` 跟踪、工作树无改动；任务卡不在本次未提交 diff 中（任务描述把它列为未提交包，实际不是）。

## 2. 逐项核对

### 2.1 最终字节与 pin（通过）

| 口径 | 实测值 | 对照 | 结论 |
|---|---|---|---|
| 工作树 SHA-256 | `67286eeca8cb2109f35445c6b925b03053c483293b1bdb19e56efdc9965b657d` | FROZEN §1/§1B/§11、载体 §7.3、`verify_pins` C16 | 一致 |
| `git hash-object` | `3cd9d2fbf79bd37b3fc35e1895efa1c75d2fc232` | FROZEN §1、载体 §7.3 | 一致 |
| blob 内容 SHA-256（LF 原始字节） | `67286eec…`（由原始字节直接复算；与工作树同值） | FROZEN §1 第三行 | 一致 |
| 字节/行尾 | size 41652 B；CR=0；LF=255 | LF 口径 | 一致 |

- `git hash-object`（默认）与 `git hash-object --no-filters` 同为 `3cd9d2fb…`，说明 clean filter 未改变字节，**工作树原始字节 = blob 内容**；因此 FROZEN §1 的「blob 内容 sha256」可由工作树字节复算为 `67286eec…`。
- `git cat-file -e 3cd9d2fb…` 返回 1：该对象尚未进入 ODB（工作树未提交，`hash-object` 未 `-w`）。这是**预提交快照的正常现象**，不是 pin 不一致；提交后 `git cat-file blob 3cd9d2fb…` 应可复算。本报告因此把 `cat-file` 列为「未直接跑」，而非缺陷。
- 矩阵第 16 行/状态行只承载版本与状态，没有 pin 字段；pin 的三处载体是 FROZEN §1/§1B/§11 与载体 §7.3，均已核对。

### 2.2 diff 范围（通过）

`git diff --no-color -- doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` 共 5 个 hunk，逐行核对：

| hunk | 位置 | 内容 | 允许项 |
|---|---|---|---|
| `@@ -1,7 +1,7 @@` | 状态行、日期行 | `FROZEN v1.6`→`v1.7`；载体链接改为 `CONTRACT-UNFREEZE-2026-11-07-C16-L-R11`；日期补 v1.7 | ④ 头部状态/载体链接/日期 |
| `@@ -14,7 +14,7 @@` | §0 版本面行（`:17`） | `source-access wire` 行补 v1.4/v1.5/v1.6/v1.7 注记 | ③ §0 版本面行补注 |
| `@@ -87,10 +87,10 @@` | §2.4 per-page（`:90`） | 「无 publication 行按既有 open 处理」→「旧未参与同步且无 publication 行的 v7 binding 按既有 open；新同步 binding 缺 publication 行属于损坏，fail-closed（C-17 §3.3），不得当作 legacy 放行」 | ① |
| 同上 | §2.4 兼容句（`:93`） | 「两读面既有差异…不属于本命令语义」→「两读面判定由 L-R11 统一为同一谓词（…共用；v1.7 澄清…），本命令沿用该谓词，不引入第三套 gate 判定」 | ② |
| `@@ -241,7 +241,7 @@` | §10 冻结条件（`:244`） | 追加 ⑨ v1.7 | ⑤ |
| `@@ -252,3 +252,4 @@` | §10 变更记录（`:255`） | 追加 v1.7 行 | ⑤ |

- **无其他条款字节改动**；§2.4 的校验顺序（`:89`）、原子性与副作用（`:91`）、错误码（`:92`）等上下文行均未变。
- `git diff --check` 退出 0；`git diff --numstat` = `7 6`；`git diff --stat` = **1 file changed, 7 insertions(+), 6 deletions(-)**，与预期完全一致。
- 行号确认：C-16 `:90` 为 per-page 行、`:93` 为兼容句；C-17 §3.3 标题在 `:171`、正文在 `:173`，即任务所称 `:171-173`。

### 2.3 零漂移（部分通过；包外文档见 P3-01）

- `git diff --name-only` = `doc/STATUS.md`、`doc/handoffs/DSH-HANDOFF-2026-11-06.md`、C-16、FROZEN-C16、矩阵；**不含** `src/**`、`apps/**`、`tests/**`、`tools/**`、`doc/contracts/**` 或其它契约文件。
- `git diff --name-only --cached` 为空（无 staged）。
- 18 份契约 `git hash-object` vs `HEAD:path`：**仅 C-16 不同**（工作树 `3cd9d2fb…` vs HEAD `f8f31f55c…`，预期），其余 **17/17 相同**（附录 B 全表）。
- 指定零改动对象（工作树 blob = HEAD blob）：
  - C-17 `f767e158a43652ea092066081e53fa0810e395fb`
  - C-06 `b537e76dad1e4075eb6ffd213e6c01954a256011`
  - C-15 `b0360cc975d361c3f1431b4c7e644bc1735981ab`
  - C-07 `cd51f8e63b8976cdd8e96fa705a391ad92ea79e9`
  - M2-C1 `6690606c26f67e99e9f61ac87d72ec33c4bd8589`
- 但 `git status --porcelain` 并非只含本包文件：`M doc/STATUS.md`、`M doc/handoffs/DSH-HANDOFF-2026-11-06.md` 两处包外文档（时间 22:13–22:14，早于 C-16 的 22:19 与载体的 22:33）。它们属上一轮 2C closeout/push 的 Lead 文档，不属本 UNFREEZE 包；详见 P3-01。

### 2.4 pin 账（通过）

- `pwsh -NoProfile -File tools/governance/verify_pins.ps1` 实跑：`PIN AUDIT: PASS (all 18)`，`EXIT=0`；逐项 `OK`，C16 `67286eeca8cb`。
- 其余 17 与 HEAD 对比：工作树 blob 全部等于 `HEAD:path`（附录 B），因此「其余 17 实测不变」成立；不是只看脚本输出。
- `verify_pins.ps1` 本身未修改（`git status` 无它）；它从各 `FEA-CONTRACT-FROZEN-*.md` 读取首个 `| sha256 … |` 行，故 C16 新值来自 FROZEN-C16 §1，而不是脚本硬编码。
- `pwsh -NoProfile -File tools/governance/check.ps1`：`Governance check: PASS (3 warnings)`，`EXIT=0`；`-TaskPath doc/tasks/FEA-11-L-R11-GATE-UNIFY-PREREQ-1.md` 同样 PASS（3 warnings）。3 条 warning 为：11 个非终态 Task、STATUS 80% 预算、REBASELINE_PLAN 80% 预算；与预期一致。

### 2.5 语义核对（通过；有一处记录措辞见 P3-02/P3-03/P3-04）

- **与 C-17 §3.3 的关系**：C-17 `:173` 原文为「旧未参与同步且无 publication 行的 v7 binding 沿旧规则；新同步 binding 缺 publication 行属于损坏，fail-closed（由 plan receipt/new previous 链检测），不能当作 legacy 放行」。C-16 `:90` 三个实质要素逐项具备：legacy 无行 open；新同步缺行 fail-closed；不得当作 legacy 放行。**不是 C-17 的逐字复制**：`沿旧规则`→`按既有 open 处理`、`（由 plan receipt/new previous 链检测）`→`（C-17 §3.3）`、`不能`→`不得`。但这正是 scope review §7.2 `:290` 的建议措辞，且 `（C-17 §3.3）` 以引用方式带入检测机制；语义无偏离。
- **安全方向**：`legacy 无行 open` 不回归；只有「新同步链缺 publication 行」这一损坏子形态从 open 收紧为 fail-closed，属于**收紧**，没有把任何原本拒绝的页改为放行。`added` relation（previous NULL）缺行检测不可见属实现卡 L-R11-a limitation（载体 §4 风险 ③；scope review §0.2/§9.3），本契约不承诺覆盖；不影响本 v1.7 的规范句方向。
- **零新增**：diff 未新增错误码、能力、命令、wire 字段、TTL 变化或 `PROTOCOL_MINOR` 变化；`:90` 的「不可授权」仍汇入 `:91` 的既有整体 typed `SOURCE_ACCESS_DENIED` 原子语义。`:93` 仍保留「不引入第三套 gate 判定」。
- **`AuthorizeSourceReadForRun` 原子语义**：`:91`「任一目标页不可授权 → 整体 typed `SOURCE_ACCESS_DENIED` 且零映射写入」字节未改；`src/**` 零 diff；既有整请求原子语义未被改写。
- **`C-16 §10 ⑨` 与冻结记录**：⑨ 是「冻结条件」中的一条（条件式），不是「复核已完成」的状态记录；FROZEN §2 条件 9、§11、矩阵第 16 行、载体 §6 均标 ⏳。二者可共存，但 ⑨ 用完成式「经…复核 approved」在字面上可读作既成事实，见 P3-04。
- **§0 行措辞**：`:17` 的「均不改 wire 字段/命令集/能力/错误码」中的「均」若覆盖整串 v1.4–v1.7，会与 `:23`「v1.5 能力追加 `source.reattest/1`」及变更记录 `:253` 字面冲突；若理解为 v1.7 两个子口径（legacy open / 新同步缺行 fail-closed）则无冲突。属可消除的歧义，见 P3-03；v1.7 本身确未新增能力。
- **代码事实抽查**（任务允许抽查）：`core_assembly.py:1244-1261` 的 `read_gate` 对 `gate is None` 返回 `open`（`:1259-1260`）；`core_service.py:5030` 取 `catalog.source_gate_reader`、`:5057` 调 `gate_reader(page_id)`；`core_assembly.py:1750` 把 `read_gate` 赋给 `source_gate_reader`，与载体 §1 的 `core_service.py:5030,5057` 引用一致；`core_service.py:5303-5334` 的 `_assert_source_sync_gate` 在无行且 `previous` 有 publication 时 `SOURCE_ACCESS_DENIED`（`:5321-5328`），与载体 §1 的一跳描述一致（scope review 另指出两跳不可见，属实现卡范围）。
- C-16 正文只在 `:93` 出现代码符号 `core_assembly.read_gate` / `_assert_source_sync_gate`，二者均可定位；未发现 C-16 正文引用 `pipeline.py`，故无可核对的 `pipeline.py` 行号。载体引用的 `core_service.py:5030,5057` 已实测存在。

### 2.6 冻结纪律（通过）

- FROZEN-C16 §1 记录三口径（工作树 SHA-256 / `git hash-object` / blob 内容 SHA-256），§1A 说明三口径一致；§1B 有 v1.6 与 v1.7 行；§2 条件 9 为 ⏳ 待复核；新增 §11 v1.7 重冻记录；历史 pin（v1.6/v1.5/v1.4/v1.3/v1.1/v1.0）保留。§2 条件 9 与 §11 均标待复核，一致。
- 矩阵状态行已改为 C-16 v1.7，并注记 v1.7 口径；第 16 行 `FROZEN v1.7`、条件 ②「v1.7 独立 byte-level 复核 ⏳ 待派」、条件 ③ C-17/C-06/C-15/C-07/M2-C1 零改动、④ 18/18、⑤ PASS；与 FROZEN 一致。下游写明「L-R11 实现归 FEA-11-L-R11-GATE-UNIFY-1」。
- 载体 §2 A–F 逐项落地：A（`:90`）、B（`:93`）、C（§0 行）、D（状态/日期）、E（§10 条件/变更记录）、F（FROZEN pin/§1B/§2 条件 9/§11、矩阵、`verify_pins` 不改）。未发现「说了但没落地」。
- 载体 §6 如实标「r1 待派独立上下文 fresh subagent 复核」，未伪造 approved；载体 §7.1 明确「复核 approved + DSH 重冻前不得作为已复核字节」。
- 证据目录 EV.md 与日志同批出现；日志与本次实跑逐字相同（pins 18/18、check PASS 3 warnings、diffstat 3 files/29 insertions/13 deletions）。

### 2.7 不夸大（基本通过；见 P3-02/P3-06）

- 未发现「L-R11 已修复」「C-17 §3.3 已实现」「L-R11 已关闭」或「契约就绪 = 实现/产品可用」的声明。载体 §3 末条、§7.4、EV §6、卡 AC-T5 均明确契约就绪 ≠ 实现/产品可用，实现归 `FEA-11-L-R11-GATE-UNIFY-1`。
- 但载体 §3「影响面」用完成式描述「Run 目标层/provider/commit guard 在损坏页从『可进入』变…拒绝」「不会把…放行」，与本卡只改文本、不实现 L-R11 的事实存在口径张力；见 P3-06。
- EV §3 写 C-16 `:90`「与 C-17 §3.3 逐字一致」，字面不成立（见 2.5）；语义一致，见 P3-02。
- `C-16 :93` 的「由 L-R11 统一为同一谓词」是目标/计划语义，不是「已统一」；载体 §3 末条与 §7.4 已作实现分离声明。本报告不把它计为夸大，但建议读者按「L-R11 落地后」理解。

### 2.8 真实性与可复算（通过；见 P3-05/P3-07 与「未跑」）

- 载体/卡引用核对：scope review session `5aa2c0cf-5c75-43f0-91fb-ef3027cc33b5`、verdict `recommended`、方案 C（A+C，scope review `:249`）、1/18 pin（`:288`）均与实际文件一致；RENDITION-1 `:159` 确为 L-R11 登记；C-17 §3.3 `:171-173` 正确；C-17 pin `aefa0fa5…` 与 `verify_pins` 一致；卡 `base_commit: 3945e1f5c` 与 scope review `reviewed_head` 一致（但早于当前 HEAD，见 P3-05）。
- 证据 `unfreeze.diff` 与实时 `git diff --no-color -- C16 FROZEN MATRIX` 在**去除 CRLF 后逐字节相同**（归一化 SHA-256 均为 `8ed9b80ee11ef0c82fe60985f68f48d834dc86e2dea6f45187d825a016226c55`）；原始文件 24468 B vs 实时 24336 B，差异为 132 个 CRLF，见 P3-07。
- 未跑：全量 `pytest tests`、全量 .NET（契约-only，EV §4 标 NOT_RUN；本报告不宣称这些门禁）；`git cat-file`（对象未入 ODB）；未做全量代码审计（仅抽查上述行号/函数）。

## 3. 实跑表

| # | 命令/操作 | 结果 |
|---|---|---|
| 1 | `git rev-parse HEAD` / `--abbrev-ref HEAD` | `07a7d746a52fc035c728a4fa4c3d1a1df624ecfa` / `main` |
| 2 | `Get-FileHash -Algorithm SHA256 doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | `67286eeca8cb2109f35445c6b925b03053c483293b1bdb19e56efdc9965b657d` |
| 3 | `git hash-object -- C-16`；`git hash-object --no-filters -- C-16` | `3cd9d2fbf79bd37b3fc35e1895efa1c75d2fc232`（两者相同） |
| 4 | C-16 原始字节统计 | size 41652；CR=0；LF=255 |
| 5 | `git cat-file -e 3cd9d2fb…` | exit 1（未入 ODB，预提交快照；未直接跑 `cat-file`） |
| 6 | `git diff --stat -- C-16` / `--numstat` / `--check` | `1 file changed, 7 insertions(+), 6 deletions(-)`；`7 6`；exit 0 |
| 7 | `git status --porcelain`（初始/当前） | 初始 5 M + 1 ??；当前 5 M + 载体/证据/本报告未跟踪（见 §6） |
| 8 | `git diff --name-only` / `--cached` | 5 个 doc 文件；cached 空；无 src/apps/tests/tools/doc/contracts |
| 9 | 18 契约 blob vs HEAD | C16 不同（预期）；其余 17 相同（附录 B） |
| 10 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，EXIT=0；C16 `67286eec` |
| 11 | `pwsh -NoProfile -File tools/governance/check.ps1` | `PASS (3 warnings)`，EXIT=0 |
| 12 | 同上 `-TaskPath doc/tasks/FEA-11-L-R11-GATE-UNIFY-PREREQ-1.md` | `PASS (3 warnings)`，EXIT=0 |
| 13 | C-17/C-06/C-15/C-07/M2-C1 blob vs HEAD | 全部相同（附录 B/§2.3） |
| 14 | `unfreeze.diff` vs 实时 3-doc diff | 原始字节不同（CRLF）；归一化后逐字节相同，SHA-256 `8ed9b80e…` |
| 15 | 抽查代码行 | `core_assembly.py:1244-1261`、`:1750`；`core_service.py:5030,5057,5303-5334`（均存在且语义相符） |

## 4. Findings

### P0/P1/P2

- **P0 = 0；P1 = 0；P2 = 0。**

### P3（非阻断）

- **P3-01｜工作树含包外未提交文档（STATUS/handoff + 并发 FEA-12 scope review），UNFREEZE 提交需隔离（P3，提交前动作）**
  - 事实：`git status --porcelain` 有 `M doc/STATUS.md` 与 `M doc/handoffs/DSH-HANDOFF-2026-11-06.md`，时间 22:13–22:14，早于 C-16（22:19）与载体（22:33）；二者不在载体 §2 F、卡 `allowed_paths` 或本包声明内。
  - 另：复核结束时出现 `?? doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md`（22:55，另一 fresh subagent 的 C-04b scope review；非本包、非本报告写入），同属需从 UNFREEZE 提交中排除的并发产物。
  - 影响：不改任何被审契约/代码/门禁；风险是 UNFREEZE 提交若 `git add -A` 会混入上一轮 Lead 文档或并发 scope review。载体 §5 ②「仅 C-16/冻结记录/矩阵/载体/卡/证据变化（`git diff --name-only`）」在字面上未满足。
  - 建议：本 UNFREEZE 提交只 stage C-16/FROZEN/矩阵/载体/证据；STATUS/handoff 由 Lead 单独提交或留存；并发 FEA-12 scope review 亦不应混入本 UNFREEZE 提交。若 DSH 要求 `git status` 严格仅包文件，应先把这些项移出提交面，再重跑本复核的 §3 第 7–8 项。
  - 定性：非阻断于字节/门禁；阻断于「提交零漂移」口径，故在结论中作为提交前条件列出。

- **P3-02｜EV 写「与 C-17 §3.3 逐字一致」，字面不成立（记录准确性）**
  - 事实：EV.md §3 第 42 行写「与 C-17 §3.3 逐字一致」；C-17 `:173` 与 C-16 `:90` 逐字比较有三处差异：`沿旧规则`→`按既有 open 处理`、`（由 plan receipt/new previous 链检测）`→`（C-17 §3.3）`、`不能`→`不得`。
  - 判定：三个实质要素一致，且 C-16 措辞正是 scope review §7.2 `:290` 的建议原文；不构成语义偏离。建议把 EV 的「逐字一致」改为「语义一致（按 scope review §7.2 建议措辞；检测机制经 C-17 §3.3 引用）」。
  - 影响：仅 EV 记录措辞；契约字节无需改动。

- **P3-03｜C-16 §0 `:17`「均不改…能力」范围可歧义（契约文字，非规范条款）**
  - 事实：`:17` 列 v1.5「增 §2.5 reattest」后写「均不改 wire 字段/命令集/能力/错误码」；同文件 `:23` 明确「v1.5 能力追加 `source.reattest/1`」，变更记录 `:253` 也如此。
  - 判定：若「均」指 v1.7 的两个子口径（legacy open / 新同步缺行 fail-closed），无冲突；若指整串 v1.4–v1.7，则与 v1.5 的能力追加字面矛盾。属可消除的歧义，v1.7 本身确未新增能力。
  - 建议：在后续 UNFREEZE 把「均不改」限定为「其中 v1.4/v1.6/v1.7 均不改」或「v1.7 不改」；**若现在改 C-16，会改变 pin 并需重新复核**，本报告不建议为此阻断当前 UNFREEZE。

- **P3-04｜C-16 §10 ⑨ 用完成式「经…复核 approved」，与记录 ⏳ 并存（记录口径）**
  - 事实：C-16 `:244` 条件 ⑨ 写「经独立 byte-level 复核 approved（P0/P1=0）」；FROZEN §2 条件 9、§11、矩阵第 16 行、载体 §6 均标 ⏳/待派。
  - 判定：⑨ 是「冻结条件」条目的条件式表述，不是复核状态表；FROZEN/矩阵/载体均未伪造 approved。但完成式可被读作「已复核通过」。2C-PREREQ r3 曾把「条件列预填 approved」作为处置项（载体 §6 记录），可参照。
  - 建议：FROZEN/矩阵/载体回填时保留 pending→approved 的明确时序；C-16 文字若未来修订，可改为「须经…复核 approved」；当前不改字节。

- **P3-05｜卡/EV/FROZEN §11 的元数据小疵（记录准确性）**
  - 卡 `doc/tasks/FEA-11-L-R11-GATE-UNIFY-PREREQ-1.md:58` 写 FROZEN「版本/pin/§1B/§9 记录」；v1.7 记录实际是 **§11**（§9 是 v1.5）。载体 §2 F 已正确写 §11。
  - 卡 `AC-T1` 写「C-16 v1.7 仅改 `:90` 括注与 `:93` 陈述」；实际允许/发生的 diff 还包括 §0 行、头部状态/日期、§10 条件/变更记录（载体 §5 ① 与任务允许项 ③④⑤）。卡 `:39` 的「只改 §2.4 一处口径」同样过窄。
  - 卡 `base_commit: 3945e1f5c` 与 EV §1 同值，早于当前 HEAD `07a7d746a` 三个提交；若该字段表示本卡实现基线，宜改 `07a7d746a`；若表示 scope review 快照，宜注明。
  - FROZEN §11「approved 后回填（P0/P1/P2 数 + session）」只列 P0/P1/P2，载体 §6 写 P0/P1/P2/P3；建议统一含 P3（本次 P3=7）。
  - 影响：均为记录/卡面文字，不影响 C-16 字节、pin、门禁或语义。

- **P3-06｜载体 §3「影响面」用完成式描述实现效果（不夸大口径）**
  - 事实：载体 §3 写「Run 目标层/provider/commit guard 在损坏页从『可进入』变既有 family 拒绝…」「不会把未确认/损坏 binding 放行」。本卡是契约-only，L-R11 实现未开始；载体 §3 末条、§7.4、EV §6 又明确「不构成任何读面行为改变/实现」。
  - 判定：语义方向正确（收紧），但完成式容易被读成「读面行为已改变」，与任务「不夸大」项存在张力。
  - 建议：在 §3 加「L-R11 实现卡落地后/契约目标语义」限定；不影响当前契约字节。

- **P3-07｜证据 `unfreeze.diff` 为 CRLF 快照，原始字节与实时 diff 不同（证据可复算）**
  - 事实：`verification/FEA-11-L-R11-GATE-UNIFY-PREREQ-1/unfreeze.diff` 24468 B；实时 `git diff --no-color -- C16 FROZEN MATRIX` 24336 B；去 CRLF 后逐字节相同，归一化 SHA-256 均为 `8ed9b80ee11ef0c82fe60985f68f48d834dc86e2dea6f45187d825a016226c55`（133 行）。
  - 判定：内容等价，无契约/语义差异；若项目要求证据快照与实时 diff 逐字节相等，应重捕获为 LF。
  - 建议：重捕获或在 EV 注明「CRLF 归一化后相同」；非阻断。

## 5. 结论与复审建议

- **结论：`approved`（P0=0/P1=0/P2=0/P3=7，均非阻断于被审字节/门禁）。** C-16 v1.7 的最终字节、diff 允许范围、零代码/契约漂移、18/18 pins、check PASS、语义方向、冻结记录/矩阵一致性与「不夸大」总体成立。
- **提交前必须做**：按 P3-01 只 stage 本包文件（C-16、FROZEN-C16、矩阵、载体、证据、本报告；PREREQ 卡已在 HEAD），排除 `doc/STATUS.md` 与 `doc/handoffs/DSH-HANDOFF-2026-11-06.md`。若 DSH 不接受「包外文档」为 P3，则应把它们先移出工作树/单独提交后再重跑本报告 §3 第 7–8 项。
- **approved 后记录回填**（不改变 C-16 字节）：
  1. 载体 §6：r1 `approved`（P0=0/P1=0/P2=0/P3=7），session `9bc4c117-e171-48b6-8f13-582845d2e12f`，reviewed_head `07a7d746a`，worktree `67286eec…`。
  2. FROZEN-C16 §2 条件 9 → ✅（证据：本报告 + 载体 §6）；§1B v1.7 行 →「= v1.7 冻结字节；r1 approved」；§11「独立复核」→ r1 approved（含 P3 数）。
  3. 矩阵第 16 行条件 ② → ✅（r1 approved/P0=0/P1=0/P2=0/P3=7；本报告）；状态行保持 v1.7。
  4. 重跑 `verify_pins.ps1` 与 `check.ps1`（默认 + `-TaskPath`），把日志放入证据目录；确认 C16 仍 `67286eec…`、其余 17 不变。
- **P3 处置建议**：P3-01 提交隔离；P3-02/P3-05/P3-07 为记录/证据文字，可在回填时顺手修正且不动契约字节；P3-03/P3-04 若改 C-16 会改变 pin，需新的 UNFREEZE + 复核；P3-06 只改载体文字，不动 pin；本报告不要求为 P3 阻断当前冻结。
- **复审建议**：记录回填后做一次轻量 re-check（C-16 字节不变 + pins 18/18 + 载体/FROZEN/矩阵三处结论一致）；无需重做完整 byte-level 复核，除非 C-16 字节发生变化。

## 6. 真实性声明

1. **写入范围**：本报告是唯一仓库写入（`doc/reviews/FEA-11-L-R11-GATE-UNIFY-PREREQ-1-r1.md`）；临时文件在仓外 `G:\CODEX\New Manga.workspace\L-R11\unfreeze-review\`（`live-3.diff` 等）。未执行 `git add/commit/push/reset/checkout`；未改 C-16/FROZEN/矩阵/载体/卡/证据任何字节。
2. **独立性**：本报告作者为 Lead 派发的独立上下文 fresh subagent（session `9bc4c117-e171-48b6-8f13-582845d2e12f`；parent `session-3ac1953a-094e-4339-889a-284df2b7b34d`），未参与 C-16 v1.7 起草、前轮复核或实现；只读被审最终字节。
3. **实测与未跑**：实测见 §3；未跑全量 pytest/.NET（契约-only；EV §4 亦标 NOT_RUN）、`git cat-file`（对象未入 ODB）、全量代码审计（仅抽查）。未把未跑项写成通过。
4. **工作树状态**：开始时 5 个 tracked 修改 + 载体未跟踪；复核期间作者并发新增 `verification/FEA-11-L-R11-GATE-UNIFY-PREREQ-1/`（非本报告写入）；本报告写入后新增其自身；复核结束时另见 `?? doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md`（22:55，另一 fresh subagent 的 C-04b scope review，非本包/非本报告写入）。**5 个 tracked 修改文件与开始时相同，未改任何既有字节**；`git status` 的差异来自授权报告与作者/另一审查者的并发产物，不是对包内文件的修改。任务所述「status 与开始相同」因报告必写且并发写入而无法字面成立，特此说明。
5. **口径**：pin/哈希/行号均以本报告日期 `2026-11-07` 的工作树与 HEAD `07a7d746a` 为准；`unfreeze.diff` 的 CRLF 归一化比较见 P3-07；`git cat-file` 口径未直接重放见 2.1。本报告不构成实现、产品可用、push 或 L-R11 关闭声明。

## 附录 A：C-16 diff hunk 与允许项对照

- 状态行/日期行 → ④；§0 `:17` → ③；§2.4 `:90` → ①；§2.4 `:93` → ②；§10 `:244` 条件 ⑨ → ⑤；§10 `:255` 变更记录 → ⑤。共 7 insertions/6 deletions，无其他条款。
- 关键上下文未变：`:89` 校验顺序；`:91` 整体 typed `SOURCE_ACCESS_DENIED`/零映射；`:92` 错误码复用；§2.5/§6/§7 等未在 diff 中出现。

## 附录 B：18 契约 blob vs HEAD（工作树 `git hash-object`）

| ID | 工作树 blob（前 12） | HEAD blob（前 12） | 相同 |
|---|---|---|---|
| C01b | 7127d0643783 | 7127d0643783 | YES |
| C02 | fcea994ae43a | fcea994ae43a | YES |
| C03 | 81738c04976d | 81738c04976d | YES |
| C04b | 201c8369d5c7 | 201c8369d5c7 | YES |
| C05 | 32d039c0e8d1 | 32d039c0e8d1 | YES |
| C06 | b537e76dad1e | b537e76dad1e | YES |
| C07 | cd51f8e63b89 | cd51f8e63b89 | YES |
| C08 | b09291c19de9 | b09291c19de9 | YES |
| C09 | 9870d73a4d9a | 9870d73a4d9a | YES |
| C10 | 5cea9445bb11 | 5cea9445bb11 | YES |
| C11 | 0f1e7b163c58 | 0f1e7b163c58 | YES |
| C12 | a5a17fd9b3c4 | a5a17fd9b3c4 | YES |
| C13 | 5a0cb284cf57 | 5a0cb284cf57 | YES |
| C14 | 111a2ce184a0 | 111a2ce184a0 | YES |
| C15 | b0360cc975d3 | b0360cc975d3 | YES |
| C16 | **3cd9d2fbf79b** | **f8f31f55ca29** | **NO（预期）** |
| C17 | f767e158a436 | f767e158a436 | YES |
| FEA01 | 0f0c2d149201 | 0f0c2d149201 | YES |

> 结论：仅 C-16 变更；其余 17/17 与 HEAD 相同。C-17/C-06/C-15/C-07/M2-C1 的完整 blob 见 §2.3。
