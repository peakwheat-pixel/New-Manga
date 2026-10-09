# P02 Process Isolation r6 — DSH 非作者独立设计 Review（正式）

---

## 1. 审查范围、精确基点与工作区状态

| 项 | 值 | 复核方式 |
|---|---|---|
| Base / r5 reviewed candidate | `1c7efb172b8e9d766e38f84cf3728a90bb5953d0` | `git rev-parse` |
| Base 元数据 | tree=`f50f9716a87ffe7a6272370a92b0eeb862e75079`，parent=`fb0a7668…`，subject=`docs(P02): close r4 process isolation review findings`，**16 路径 / +270−4** | base commit 自身 `--numstat`（16 条，+270/−4，与 r5 response §6 表逐行一致） |
| Candidate / r6 delivery | `30da5fafb23ec578132d91b88c66bd1e6a6f9d2c` | `git rev-parse HEAD`（分支 `codex/P02-process-isolation` 亦指向该 SHA） |
| Candidate tree | `2ae3e03be54eea385e2c0eda6369dc03e7048324` | `git rev-parse HEAD^{tree}` |
| Candidate parent | `1c7efb172b8e9d766e38f84cf3728a90bb5953d0`（=base；单 parent、无 merge） | `git cat-file -p HEAD`、`git rev-parse HEAD^@`、`git rev-list --count base..HEAD`=**1** |
| commit 元数据 | author/committer=`peakwheat-pixel <peak.wheat@gmail.com>`，`2026-10-09T23:34:20+08:00`（=15:34 UTC），subject=`docs(P02): close r5 process isolation review conditions` | `git log -1 --format`（与 r6-start/validation 的 15:34 UTC 自述一致） |
| 本审查 checkout | `C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r6`，**detached HEAD**=candidate | `git status`、`git worktree list` |
| Git 目录 | common=`G:/CODEX/New Manga/.git`；worktree git-dir=`…/.git/worktrees/P02-process-isolation-review-dsh-r6` | `git rev-parse --git-common-dir` |
| 洁净性 | 审查开始与结束 `git status --porcelain=v1 -uall` 均 **0 项**；stash=0；未新增 `__pycache__`（validator 以 `-B` 运行） | 两次 `git status`、`git stash list`、目录检查 |
| Author checkout | `C:\Users\49745\.codex\worktrees\p02-process-isolation-plan\New Manga` @ `30da5faf`（=candidate），**tracked 改动=0**，2 条 untracked（`codex-checkpoint-p02-process-isolation-r6-delivery.md`、`dsh-review-process-isolation-r6.stderr.txt`，均属提交后审计件） | 只读 `git -C … status` |
| Diff 规模 | 相对 base=**12 路径，+261/−2**，全部落在 `verification/P02/**` | `git diff --name-status/--numstat/--check` |
| r6 in-tree 记录 | 候选树内 `dsh-review-process-isolation-r6.*` **仅有** `r6.prompt.md`；全 `verification/P02` grep `30da5faf` = **0 命中**（candidate SHA 尚未入库，待 r6 dispatch 记录） | `git ls-tree`、grep |

---

## 2. 决定

**Decision：`APPROVED_WITH_CONDITIONS`（仅 Design / Scheme Review）。**
**计数：P0 = 0；P1 = 0；P2 = 0；P3 = 1**（唯一新增为 **N-06**，纯文档许可措辞；r5 的 N-04、N-05 均已实质闭合）。

- **批准对象**：r5 两项条件 N-04（许可文本窄于交付，同类复发）与 N-05（冻结段内转义残留 + 缺文件尾换行）的实质修订，以及 r5 formal evidence 的完整入库与自洽。
- **条件（1 项，纯文档，不改 XML/hash、不改任何 Gate 语义）**：`scope-delta` § r6 对「被修改的那一行」的许可措辞（**原文指向 r3/r4 extension 的 :52，而本轮实际改的是 r5 extension 的 :66**）应在下一处纯文档 commit 内改为逐行明确，或在 r6 delivery checkpoint 显式登记；亦可由治理方显式裁定为非条件。条件未闭合前：**Smoke admission 保持 `NOT_ADMITTED`**（`doc/tasks/P02.md:60` 要求“所有 Review 条件闭合”）。
- **本决定最多允许**：在本固定 candidate 下执行 `proposal:78` 步骤 1 的**本机非提权、只读** preflight。
- **本决定不授权**：任何 Windows Feature 查询/变更/启用、提权、`wsb start/connect/exec`、Sandbox 启动/连接、Smoke 执行或 Smoke PASS、Smoke admission、Build Gate PASS、任何 build、产品 runner/Vitest/GUI/WebView、任何 AC PASS。
- **与 r5 口径的关系**：r5 因“本轮唯一交付目标即文档精度，却再次出现许可文本窄于交付”而把 P3 登记为条件；r6 仍是同一局面（第三次同类），故我保持 P3 严重度、并同样登记为条件，同时明确 N-04/N-05 的设计实质已通过。

---

## 3. N-04 / N-05 disposition

### N-04｜P3（r5 extension 许可 append-only 窄于实际就地替换 :52）→ **CLOSED（实质）**
- **现文本**：`codex-scratch-build-process-isolation-scope-delta-r1.md:66` = “允许追加本 r5 extension，**并只就地扩写 r3/r4 extension 中 r3-start 的许可行（原 :52；不改其他文字）**，用于修复 N-02 文件级许可描述过窄及闭合 N-04。”
- **判定**：r5 extension 的 scope permission **已明确覆盖** r3-start 原 :52 许可行的一行就地扩写，且以“不改其他文字”限定范围 → 满足 r5 给出的首选修复路径（r5 response:64 第 1 选项）。
- **范围自证**：base..candidate 对 scope delta 的差量 = 精确 1 行替换（:66）+ 末行 EOF 修复 + 追加 § r6（`--numstat`=`12 2`，`1+1`（:66）+`1+1`（末行）+空行+9 行 § r6 = 12/2，算术闭合）；`:52` 在 r6 中**未被触碰**（它已在 base `1c7efb17` 的 r5 commit 内完成扩写）。

### N-05｜P3（r5 extension 末尾字面 `` `n ``、缺文件尾换行）→ **CLOSED（逐字节验证）**
- candidate blob `454b525d51c328aa0a12644501254e9b2b54d8f7`：**10026 bytes、CR=0、LF=79、末 4 字节=`e3 80 82 0a`（“。”+LF）**，`endswith(0x60 0x6E)`=**False**，即**以单个 LF 结束、无末尾空行**（base 为 8037 bytes，与 r5 N-05 证据一致）。
- 全文差量中 `\ No newline at end of file` 标记共 3 处：**1 处在 `−` 侧（被删的旧行）**，另 2 处是 `r5.response.md`、`r6.prompt.md` 正文里对该短语的引用；**`+` 侧无任何 no-newline 标记** → git blob 已无 `No newline at end of file`。
- 工作区文件 10105 bytes = 10026 + 79（`core.autocrlf` 检出转换），与 r5 记录的 blob/工作区双口径一致。
- 文中其余 2 处 `` `n `` 均为 § r6 对“被删除的两个字符”的文档化引用（`:75`、`:78`），非残留。

---

## 4. 新 findings

### N-06｜P3｜r6 extension 的路径许可未指名本轮实际被修改的那一行（N-02→N-04→N-06 同类第三次）
- **证据**：
  - `scope-delta:75`（冻结的 r6 许可）：“仅允许按上文 r5 extension 的授权，**扩写 r3/r4 extension 中 r3-start 的一行文件许可**；删除本文件 r5 extension 末尾误留的两个字符 `` `n `` 并补 LF 文件尾；追加本 r6 extension。**不得改其他既有文字**。”
  - 但 `base..candidate` 实际改动的是 **r5 extension 内的 :66**（diff 唯一内容 hunk 起始 `@@ -63,7 +63,17 @@`，`−` 行即旧 :66）；而 **:52 位于 r3/r4 extension，在 base 1c7efb17 已改完，本轮为 no-op**（`:52` 在 base/candidate 逐字节相同）。
  - r6 证据自身也按“效果”而非“行号”表述：`scope-delta:78`（R6验收）写“N-04 许可精确覆盖上述 **:52** 一行就地扩写”，`codex-process-isolation-r6-validation.md:8` 断言“scope delta 的 r6 extension **再精确列明此改动**”——该断言在冻结文本层面并不成立。
- **影响**：纯治理可核验性问题，无路径越界、无 XML/hash、无运行态/Gate/产品影响。精确修复范围**确有入库记录**：`codex-checkpoint-p02-process-isolation-r6-start.md:8` 明确“仅修改 r5 extension 中 N-04 所指的 **:66** 许可语句”，故材料意图可判定，仅冻结文本与交付差量的字面映射不足（与 r4 N-02、r5 N-04 同类）。
- **可验证修复（择一）**：把 `:75` 首句改为“修订 r5 extension 内授权 r3-start 一行就地扩写的许可语句（r5 extension 原 :66；不改其他既有文字），使 :52 的一行就地扩写获得明确授权”，或在 r6 delivery checkpoint 显式登记该 1 行修订。

---

## 5. 非阻断观察（不计入 finding）

- **O-1 单位措辞**：`codex-process-isolation-r6-validation.md:13` “base 与 working file 均 2609 bytes”把 LF-canonical blob（2609，base/HEAD 逐字节相同）与 CRLF 检出文件（2631）混写；实质结论为真（我独立复算 blob 相同、canonical SHA-256 一致），仅措辞不精确。
- **O-2 冻结层叠加**：`scope-delta:44` 仍写 `FROZEN_FOR_R4_REVIEW`，`:61` 写 `FROZEN_FOR_R5_REVIEW`，`:73` 写 `FROZEN_FOR_R6_REVIEW`，三层无 supersession 声明（r5 O-1 复发，属既有日期分层惯例）。
- **O-3 plan 陈旧**：`codex-scratch-build-plan.md:81` 仍为“N-01..N-03 三项非阻断 P3 **待文档修订**”及 `AC1–AC6`；r5 已 CLOSED N-01..N-03、r6 已修 N-04/N-05，但 § r6 明确**禁止**修改 Build plan（`:77`），故属已登记的延期文档项（含 R3-06 的 AC 计数口径延期），非本轮违规。
- **O-4 自记录缺口**：候选树无 r6 delivery/review checkpoint，也无 r6 dispatch/response/exit/session/mount/stderr（author worktree 已有 r6-delivery 草稿与 r6.stderr.txt 两条 untracked）；candidate SHA 尚未入库。与“第 N 轮 checkpoint 落在第 N+1 轮 commit”的既有模式一致（r5 同样如此），但 r6 dispatch 必须记录 H/T/P。
- **O-5 指针完整度**：`doc/tasks/P02.md:60` 仅指向 `§ r3/r4 scope extension`，未指向 § r5/§ r6——这正是 N-03 规定的写法，非缺陷（r5 O-2 复发）。
- **O-6 自检性质**：`codex-process-isolation-r6-validation.md:8–14` 的 `PASS` 是作者在独立 Review 前的自检断言，不得视为本 Reviewer 结论；我已独立重做其中可复算项（见 §7、§9），未能复算项保持 `NOT_VERIFIED`。

---

## 6. base..candidate 差异路径与 scope 核验

| # | 路径 | numstat | 许可归属 |
|---|---|---|---|
| 1 | `codex-checkpoint-p02-process-isolation-r5-delivery.md` | +11 | r5 ext:67 / r6 ext:76 |
| 2 | `codex-checkpoint-p02-process-isolation-r5-review.md` | +11 | r5 ext:67 / r6 ext:76 |
| 3 | `codex-checkpoint-p02-process-isolation-r6-start.md` | +13 | r6 ext:76 |
| 4 | `codex-process-isolation-r6-validation.md` | +22 | r6 ext:76 |
| 5 | `codex-scratch-build-process-isolation-scope-delta-r1.md` | **+12/−2** | r6 ext:75（:66 许可、EOF、§ r6；**N-06** 指向字面映射不足） |
| 6–11 | `dsh-review-process-isolation-r5.{dispatch,exit.txt,mount.txt,response.md,session.txt,stderr.txt}` | +11/+1/+2/+158/+3/+0 | r5 ext:67 / r6 ext:76 |
| 12 | `dsh-review-process-isolation-r6.prompt.md` | +17 | r6 ext:76 / r6-start:9 |

- **路径集合**：12 条中落在 `verification/P02/**` 之外的 = **0**；命中 `doc/tasks/P02.md`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`apps/`、`src/`、`tests/`、`requirements*`、`packaging/`、Schema/IPC 的 = **0**。
- **Owner allowlist / 产品范围**：`doc/tasks/P02.md` 本轮未被触碰（L47–56 允许修改范围与 L56 治理段、L58–73 Codex-only boundary 均不变）→ **未扩大 Owner allowlist、未改 Task boundary、未改 AC（L39–45 仍全 `[ ]`）、未重冻结 P02**。
- **`STATUS`/`REBASELINE_PLAN`/Build plan/host inventory**：均不在 diff 内。
- **root 保护现场（只读独立复核）**：`G:/CODEX/New Manga`=`main@549a6544f0be1eec66c09ece393fd1a409f10bf3`；`git status`=**203 项**、staged=**0**；按 manifest **逐项复算 path/status/size/SHA-256 = 203/203 匹配**，mismatch=0、missing=0、extra=0；canonical entries=**36985 bytes / `3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`**（与 recipe 逐字节一致）。candidate 12 路径 ∩ root dirty = **0**。

---

## 7. R5 formal evidence 自洽性（prompt 第 3 项）与 N-01..N-03 独立确认

**证据链自洽（全部只读复算）**
- `dsh-review-process-isolation-r5.response.md`（158 行，入库）=Decision `APPROVED_WITH_CONDITIONS`（仅设计）、`0/0/0/2`，与 `codex-checkpoint-p02-process-isolation-r5-review.md:6`、`r5.dispatch.md:11` **三方一致**。
- `r5.dispatch.md`：base=`fb0a7668…`、candidate=`1c7efb17…`、tree=`f50f9716…`、parent=base —— 与 git 复核一致；session=`session-e94ff6f7-0701-4dc2-955d-018c373ebe79`，该串**确实出现**在 raw JSONL 文本内；`r5.exit.txt`=`0\n`（2 bytes）、`r5.stderr.txt`=**0 bytes**（blob `e69de29…`）、`r5.mount.txt`=`mount_session.py exit=0` + 目标 `P02-process-isolation-review-dsh-r5`，与 `r5.session.txt`（`cwd=…review-dsh-r5`、`review_checkout_head=1c7efb17…`）互洽。
- 库外 raw JSONL `…/p02-process-isolation-plan/dsh-review-logs/dsh-review-process-isolation-r5.stdout.jsonl` = **269485 bytes / `f9b4a9ad2f270fe1774e3892b12b627bed708f79b344ef9bf2c94b4c775b19f9`**，与 dispatch:9、r5-review:7 记录**逐字节一致**；末个 usage event = `inputTokens=3455 / outputTokens=6631 / cacheReadTokens=113664 / totalTokens=123750`，与 dispatch:10 **完全一致**（未跨 event 相加）。
- r4 证据链（r5 §6 引用）：raw JSONL = **316609 bytes / `fdc16332…`**、`thinking` 出现 **37** 次、`exit=0`、`session-e4de7c63-…`、stderr=0 —— 与 r4 dispatch:6/8/9 一致。
- 格式小注（不影响自洽）：`r5.dispatch.md:4` 写版本行 `dsh 0.2.0-rc.2 --profile headless --json -`，`:7` 命令写 `dsh --profile headless --json -`（省略版本前缀），与 r4 dispatch 同格式。

**N-01..N-03 disposition 独立确认（均 CLOSED）**
- **N-01**：addendum 现有行“以上 HostFolder 均需 ReadOnly=true，**当前冻结的 r3 Smoke config 不含这两个 Git roots**” ✓；`plan:81` 已登记 `r3=APPROVED_WITH_CONDITIONS (0/0/2/4)`、`r4=APPROVED (0/0/0/3，仅设计)`、N-01..N-03 待闭合，并保留 Smoke admission/Smoke/Build Gate/build/AC/Hard Build Barrier 原状态 ✓（数值与 r3/r4 response 一致）。
- **N-02**：`scope-delta:52` 的 r3-start 文件级许可含“只追加/校正 r3 hash 时间点 erratum **及 R3-01 MSVC/SDK input 分类措辞一致性修正**” ✓；r5 extension 授权边界（`:59–69`）限于点名的 5 类路径/附件 ✓。随后暴露的缺口即 N-04（本轮已实质闭合）。
- **N-03**：`doc/tasks/P02.md:60` 引用的 `§ r3/r4 scope extension` 与真实标题 `scope-delta:40`（`## r3/r4 scope extension（…）`）**逐字一致** ✓。

---

## 8. r3 WSB XML bytes/hash 与不受影响面

| 项 | base `1c7efb17` | candidate `30da5faf` |
|---|---|---|
| `codex-p02-wsb-smoke-config-r3.xml` Git blob | `0f795f872f38e3f757f275d642c75bd4ca4f020f`（2609 bytes） | **同一 blob**（2609 bytes） |
| canonical UTF-8/LF bytes / SHA-256 | 2609 / `9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d` | **逐字节相同**（我独立复算：CR=0、LF=22、sha256=同值） |

`r2` config（`4d030b6b…`，2397 bytes）同样未被触碰；产品代码/测试、Schema/IPC、依赖、`STATUS`、`REBASELINE_PLAN`、Owner allowlist 均无差量。

---

## 9. 精确 Gate 状态（互不推导、不写 PASS）

| Gate | 状态 | 依据 |
|---|---|---|
| Design/Scheme Review（本报告） | **APPROVED_WITH_CONDITIONS（仅设计）** | 本文 §2–§4 |
| Windows Sandbox Feature（`Containers-DisposableClientVM`） | **UNKNOWN** | 未查询、未提权；本机查询需提权（`proposal:78,93`） |
| Smoke admission | **NOT_ADMITTED** | `doc/tasks/P02.md:60`（需 Design Review 通过 + 全部条件闭合 + Codex 单独记录 + 完整 preflight）；N-06 条件未闭合 |
| Isolation Smoke | **NOT_AUTHORIZED / NOT_RUN** | 未运行 `wsb start/connect/exec`，未启动/连接 Sandbox |
| Build Gate | **BLOCKED** | plan:4/81、r6-start:12、r6-validation:18、`scope-delta:79` |
| build | **NOT_AUTHORIZED / NOT_RUN** | 无任何 build 命令与证据 |
| P02 AC1–AC7 | **全部 `BLOCKED / NOT_RUN`** | `doc/tasks/P02.md:39–45` 全为 `[ ]`；无验收证据 |
| 产品验收 | **BLOCKED** | 同上 |
| P02 Owner allowlist | **未扩大（不变）** | 本轮 diff 不含 `doc/tasks/P02.md` |
| P02 Hard Build Barrier | **保持有效（active）** | plan:81、r6-start:12、r6-validation:18、`scope-delta:79` |

---

## 10. 已执行 / 未执行检查

**已执行（全部只读；未写文件、未改 Git/index、未动 root 或其他 worktree、未提权）**
`git rev-parse HEAD/HEAD^{tree}/HEAD^@/HEAD^`、`git cat-file -p/-s/blob`、`git log -1 --format=%H %T %P %aI %cI %s`、`git rev-list --count`、`git status --porcelain=v1 -uall`（审查前后均 0 项）、`git stash list`、`git worktree list`、`git diff --name-status/--numstat/--stat/--check`（EXIT=0）、`git ls-tree`；库外 JSONL 的 `Get-Item.Length`+`Get-FileHash -SHA256` 与内容/usage/thinking 解析；python（byte-exact 管道，已用 git blob SHA-1 交叉自证）复算 scope deltablob 10026/0CR/79LF/末字节、XML canonical 2609/CR=0/LF=22/SHA-256、manifest canonical 36985/`3a54fa97…`；PowerShell 逐项复算 root manifest **203/203 path+status+size+SHA-256**、额外项=0、staged=0；candidate 12 路径 ∩ root dirty=0；**`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` 在 candidate HEAD 执行 = EXIT=0**（打印 `live HEAD=30da5faf…`，7 项 PASS，`Product tests/build/GUI: NOT_RUN (planning-only)`；该脚本为纯打印式文档/路线 validator，仅第 43 行只读 `.open`，无写文件/子进程分支，`-B` 避免 bytecode 写入）。

**未执行 / 不可复算（限制，一律不写为 PASS）**
- 未查询或修改任何 Windows Feature、未提权、未运行 `wsb`、未启动/连接 Sandbox、未执行 Smoke、未 build、未运行产品 runner/Vitest/GUI/WebView → 运行态与本项相关 Gate 一律 `UNKNOWN / NOT_RUN / BLOCKED`。
- host `git.exe/cl.exe/link.exe/rc.exe/mt.exe` 版本/大小/SHA-256 未复核（未读 `C:\Program Files`）→ addendum 中相应值 `NOT_VERIFIED`。
- `codex-checkpoint-p02-process-isolation-r3-start.md` 的 `14:34 UTC` 快照值（4280 / `1acbe671…`）不可由 Git 复算（未进入历史）。
- r5/r6 validation 的自检 `PASS` 行未被采信为本 Reviewer 结论（可复算项已独立重做，其余保持作者断言）。
- author worktree 历史上的“7/8 条未提交证据记录”（r5-review:5、r6-start:6）不可独立复算；其“提交前 clean”不可回溯验证，但当前 tracked 改动=0、HEAD=candidate。
- DSH token usage、Desktop session 可见性仅采信版本化证据，未重放。

---

## 11. 限制

1. 本报告只覆盖 **Design/Scheme Review**，任何运行态、Smoke、Build 与产品验收结论均不在其中，且不得由本报告的 APPROVED_WITH_CONDITIONS 推导。
2. 唯一条件 N-06 属许可措辞精度，不改变 r6 candidate 的设计实质；但它使 docs 冻结文本与交付差量的字面映射继续存在第三次同类缺口。
3. 未运行项（Feature、Sandbox、Smoke、Build、产品测试）在本报告中一律保持 `UNKNOWN / NOT_RUN / BLOCKED / NOT_VERIFIED`。

---

## 12. 下一项安全 Gate 与推荐下一步

1. **下一处纯文档 commit（最高优先、无风险）**：闭合 **N-06**（把 `scope-delta:75` 首句改为指名 r5 extension 原 `:66` 的许可修订，或在 r6 delivery checkpoint 内显式登记该 1 行修订）；同提交入库 r6 delivery/review checkpoint 与 r6 dispatch/response/session/mount/exit/stderr，并记录 candidate SHA=`30da5fafb23ec578132d91b88c66bd1e6a6f9d2c` / tree / parent。**不得**改 r3 WSB XML、canonical hash、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、Owner allowlist、产品实现/测试、Schema/IPC/依赖。
2. **随后**：按 `proposal:78` 步骤 1 执行本机**非提权只读** preflight（root HEAD/branch/common-dir、`wsb` identity/version、`wsb list` 无 running session、`G:\CODEX\P02-scratch-build-source` 不存在、架构/BIOS 虚拟化/RAM/可用内存/磁盘/CPU、全部 HostFolder 与 pinned inputs）。非提权下 Feature 查询失败按设计记 `BLOCKED`，属正确结果。
3. **Smoke admission 必须由 Codex 单独记录**；在此之前 `Smoke=NOT_AUTHORIZED / NOT_RUN`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`、Hard Build Barrier 保持有效。

**推荐下一步（可直接转发 Codex）**
> 在 `codex/P02-process-isolation` 既有 scope 内做一次纯文档收尾并固定新 commit：(1) 将 `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md:75` 的首句改为“修订 r5 extension 内授权 r3-start 一行就地扩写的许可语句（r5 extension 原 :66；不改其他既有文字），使 :52 的一行就地扩写获得明确授权”，或在 `codex-checkpoint-p02-process-isolation-r6-delivery.md` 中显式登记该 1 行修订（N-06）；(2) 同提交入库 r6 delivery/review checkpoint 与 `dsh-review-process-isolation-r6.{dispatch,response,session,mount,exit.txt,stderr.txt}`，dispatch 记录 candidate SHA=`30da5fafb23ec578132d91b88c66bd1e6a6f9d2c`、tree=`2ae3e03be54eea385e2c0eda6369dc03e7048324`、parent=`1c7efb172b8e9d766e38f84cf3728a90bb5953d0`；(3) 不改 r3 WSB XML/canonical hash、`STATUS`/`REBASELINE_PLAN`/Owner allowlist/产品与契约。此后仅执行本机非提权只读 preflight；`Feature=UNKNOWN`、`Smoke admission=NOT_ADMITTED`、`Smoke=NOT_AUTHORIZED/NOT_RUN`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED/NOT_RUN`、AC1–AC7=`BLOCKED`、Hard Build Barrier 有效。

---

**Reviewer 声明**：本次 Review 全程只读；未修改本 checkout、Git/index、root 或其他 worktree，未新建文件（含未写 response 文件），未提权、未查询/更改/启用任何 Windows Feature、未启动/连接 Sandbox、未运行 `wsb`/Smoke/Build/产品 runner/Vitest/GUI/WebView；所有未运行的检查均标为 `UNKNOWN` / `NOT_RUN` / `BLOCKED` / `NOT_VERIFIED`，未写为 PASS。
