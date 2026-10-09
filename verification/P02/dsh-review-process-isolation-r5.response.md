# P02 Process Isolation r5 — DSH 非作者独立设计 Review（正式）

---

## 1. 审查范围、精确基点与工作区状态

| 项 | 值 | 复核方式 |
|---|---|---|
| Base / r4 approved design candidate | `fb0a7668d948ae68f15fd59aaffd6aedf6663c99`（parent=`92361e35…`，tree=`61abeb08…`） | `git rev-parse`、r4 response:10 |
| Candidate / r5 delivery | `1c7efb172b8e9d766e38f84cf3728a90bb5953d0` | `git rev-parse HEAD` |
| Candidate tree | `f50f9716a87ffe7a6272370a92b0eeb862e75079` | `git rev-parse HEAD^{tree}` |
| Candidate parent | `fb0a7668d948ae68f15fd59aaffd6aedf6663c99`（=base；`base..candidate`=**1** commit） | `git rev-parse HEAD^@`、`git rev-list --count` |
| commit 元数据 | author/committer=`peakwheat-pixel <peak.wheat@gmail.com>`，`2026-10-09T23:21:30+08:00`，subject=`docs(P02): close r4 process isolation review findings` | `git log -1 --format` |
| 本审查 checkout | `C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r5`，**detached HEAD**=candidate | `git status` |
| Git 目录 | common=`G:/CODEX/New Manga/.git`；worktree git-dir=`…/.git/worktrees/P02-process-isolation-review-dsh-r5` | `git rev-parse --git-dir/--git-common-dir` |
| 洁净性 | 审查开始与结束 `git status --porcelain=v1 --untracked-files=all` 均 **0 项**；无 staged/untracked、无 stash | 两次 `git status`、`git stash list` |
| Diff 规模 | **16 路径，+270/−4**；`M doc/tasks/P02.md`，其余 15 条全在 `verification/P02/**` | `git diff --name-status/--numstat` |
| dispatch 记录 | 候选树内**尚无** `dsh-review-process-isolation-r5.dispatch.md`（只有 r5.prompt.md；按 prompt 约定 dispatch 在本次 Review 后记录最终 SHA/tree）。本报告因此自行记录 H/T/P | `git diff --name-only`、目录列示 |

说明：候选树内 `verification/P02/dsh-review-process-isolation-r5.prompt.md` 与本次收到的 dispatch prompt 逐段一致（18 行）。

---

## 2. 决定

**Decision：`APPROVED_WITH_CONDITIONS`（仅 Design / Scheme Review）。**
**计数：P0 = 0；P1 = 0；P2 = 0；P3 = 2**（N-04、N-05，均为**本轮新引入**的文档问题）。

- **批准对象**：r4 findings **N-01、N-02、N-03 的实质修订**（build addendum r3 config 指代、Build plan Review 状态、scope 文件级许可扩写、Task boundary 章节指针），以及 r3/r4/r5 三层 scope 的路径连续性。
- **条件（2 项，纯文档，不改 XML/hash）**：N-04、N-05 必须在下一处纯文档 commit（即入库 r5 dispatch/delivery checkpoint 的那次提交）内闭合。条件未闭合或未由治理方显式裁定为非条件前：**Smoke admission 保持 `NOT_ADMITTED`**（`doc/tasks/P02.md:60` 要求"所有 Review 条件闭合"才尝试 Smoke）。
- **本决定最多允许**：在本固定 candidate 下执行 `proposal:78` 步骤 1 的**本机非提权、只读** preflight（P3 按 r3/r4 口径不阻断该 preflight）。
- **本决定不授权**：Windows Feature 查询以外的任何 Feature 变更/启用、提权、`wsb start/connect/exec`、Sandbox 启动/连接、Smoke 执行或 Smoke PASS、Smoke admission、Build Gate PASS、任何 build、产品 runner/Vitest/GUI/WebView、任何 AC PASS。
- **与 r4 口径的差异说明**：r4 对 P3-only 给 `APPROVED`。本轮唯一的交付目标就是文档精度，却新引入 1 处"许可文本窄于交付差量"（N-02 同类复发）与 1 处冻结授权段内的转义残留，故我保留 P3 严重度、但把它登记为**条件**而非纯观察。

Gate 语义分层（互不推导、不写 PASS）：**Design Review=本报告 `APPROVED_WITH_CONDITIONS`（仅设计）**；**Smoke admission=`NOT_ADMITTED`**；**Smoke=`NOT_AUTHORIZED / NOT_RUN`**；**Build Gate=`BLOCKED`**；**build=`NOT_AUTHORIZED / NOT_RUN`**；**产品验收=`BLOCKED`**；**Windows Sandbox Feature=`UNKNOWN`**；**Hard Build Barrier=保持有效**。

---

## 3. N-01 ～ N-03 disposition

### N-01｜P3（r4 旧状态/旧 config 指代）→ **CLOSED**
- **addendum**：`codex-scratch-build-input-host-inventory-r2-build-addendum.md:13` 已改为"…均需 ReadOnly=true，**当前冻结的 r3 Smoke config 不含这两个 Git roots**"，与同文件 `:47`"already exist in the **r3** Smoke config"、`:3`、`:42`（仅 Git 两个根为 Build-only）一致。全库 grep `r2 [Ss]moke config` 仅 1 命中，且为 r4 报告对旧文本的历史引用（`dsh-review-process-isolation-r4.response.md:132`），非残留事实陈述。
- **plan**：`codex-scratch-build-plan.md:81` 已删除"当前 proposal=`PROPOSED / REVIEW_PENDING`"，改为"proposal design review：r3=`APPROVED_WITH_CONDITIONS` (P0/P1/P2/P3=0/0/2/4)，r4=`APPROVED` (0/0/0/3，仅设计)；N-01..N-03 三项非阻断 P3 待文档修订"，并保留 `Smoke admission=NOT_ADMITTED`、`Smoke=NOT_AUTHORIZED / NOT_RUN`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、`P02 AC1–AC6=BLOCKED`、`Hard Build Barrier 有效`。
- **数值独立核对**：r3 response "P0 = 0；P1 = 0；P2 = 2；P3 = 4"、r4 response §3 "P0 = 0；P1 = 0；P2 = 0；P3 = 3"，与 plan:81 登记的 `0/0/2/4`、`0/0/0/3` 相符 ✓。
- **残留**：`plan:60`、`gate:39/50`、`start-r1:19` 仍含 `PROPOSED / REVIEW_PENDING`，但均位于明确标注日期的历史分层，与 r4 报告 §3 非阻断观察一致，不构成新 finding。
- **措辞瑕疵（观察 O-3）**：`plan:81` 与本轮已交付的修订不一致处在于"待文档修订"（修订已在本 commit 完成），宜为"待 r5 Review 关闭"。

### N-02｜P3（scope 文件级许可窄于实际改动）→ **CLOSED（实质）**
- **r3-start 文件级许可**：`codex-scratch-build-process-isolation-scope-delta-r1.md:52` 现为"`codex-checkpoint-p02-process-isolation-r3-start.md`（只追加/校正 r3 hash 时间点 erratum **及 R3-01 MSVC/SDK input 分类措辞一致性修正**）"，与 r4 N-02 指出的实际改动（r3-start:23 Build-only 分类措辞）范围相符 ✓。
- **r5 extension 授权边界**：`scope-delta:59–69` 明确限于 (1) `doc/tasks/P02.md` boundary 段的 scope 标题引用、(2) addendum 的 r3 config 行、(3) build plan 的 proposal review state 行、(4) scope delta 本 extension、(5) `verification/P02/**` 的 r5 start/delivery/review checkpoint、validation record 与 `dsh-review-process-isolation-r4.*`、`dsh-review-process-isolation-r5.*` 正式附件（点名含 `codex-checkpoint-p02-process-isolation-r4-review.md`）；并禁止 r3 WSB XML/canonical hash、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、P02 Owner allowlist、产品实现/测试、Schema/IPC/依赖、root/其他作者 dirty 文件 ✓。
- **新缺口**：该 extension 对 scope-delta 的许可写作"**只追加**本 r5 extension"，但交付同时**就地替换**了 `:52`（`--numstat` = `13 1`）→ **N-04**。

### N-03｜P3（章节指针名与真实标题不一致）→ **CLOSED**
- `doc/tasks/P02.md:60` 现为"…scope basis 见 [`process-isolation scope delta`](…) **§ r3/r4 scope extension**"；实际标题 `scope-delta:40` = `## r3/r4 scope extension（2026-10-09；冻结于 r3 candidate 92361e35…）`，章节名逐字一致（括号内为日期/candidate 注记）✓。
- 观察 O-2：该指针未包含承载本轮冻结与许可的 `## r5 P3 documentation closure` section。

---

## 4. 新 findings

### N-04｜P3｜r5 冻结许可（append-only）窄于实际交付（N-02 同类复发）
- **证据**：`scope-delta:66`"`codex-scratch-build-process-isolation-scope-delta-r1.md`：**只追加本 r5 extension**"；而 `git diff --numstat base..HEAD` 对同文件 = `13 1`，被删除的正是 `:52` 的旧许可行（r3/r4 extension 内的就地替换）。`codex-checkpoint-p02-process-isolation-r5-start.md:7` 自述为"(4) scope delta 本身的 N-02 许可修订"，说明作者意图，但**冻结文本未覆盖该就地编辑**。
- **影响**：与 N-02 同类（许可文本与交付差量不完全对应，削弱 scope 可核验性）。文件本身在许可清单内，无路径越界、无运行态/Gate/产品影响。被改内容恰是 r4 N-02 给出的首选修复方式，故问题在 r5 许可措辞而非改动本身。
- **可验证修复**（择一）：把 `:66` 改为"只允许追加本 r5 extension **及就地扩写 `:52` 的 r3-start 许可行（不改其他文字）**"；或在 r5 delivery checkpoint 内显式登记该 1 行替换（r4 N-02 的第二选项）。

### N-05｜P3｜r5 extension 末行残留字面转义 `` `n `` 且文件缺尾换行
- **证据**：`scope-delta` LF-canonical（git blob）**8037 bytes**，工作区 8105 bytes（CRLF）；文件**最后 2 字节 = `0x60 0x6E`（`` `n ``）**，紧接"…最多进入本机非提权只读 preflight。"之后；文件**不以换行结束**（`git diff` 显示 `\ No newline at end of file`）。base 版本无此字节，属本轮引入。
- **影响**：纯文本/排版瑕疵，不改变任何授权或 Gate 语义；但位于冻结授权 section 内，属本轮新引入的文档缺陷。
- **可验证修复**：删除末尾 2 字节 `` `n `` 并补文件尾换行；不改其他文字。

---

## 5. 非阻断观察（不计入 finding）

- **O-1 状态分层**：`scope-delta:44` 仍以"当前状态：`FROZEN_FOR_R4_REVIEW`"表述，而同文件 `:61` 已冻结 `FROZEN_FOR_R5_REVIEW`，r5 extension 未声明取代关系。属 r4 报告已明确不作为 finding 的"日期分层"同类，但建议下次文档触碰时加一句 supersession。
- **O-2 指针完整性**：`P02.md:60` 仅指向 `§ r3/r4 scope extension`，未指向 r5 section；与 N-03 规定修复一致，非缺陷。
- **O-3 待办措辞**：`plan:81`"待文档修订"、`codex-process-isolation-r5-validation.md:9`"N-01..N-03 待修"与同 commit 已交付修订略有张力，宜为"待 r5 Review 关闭"。
- **O-4 自身记录缺失**：候选树无 r5 delivery checkpoint，也无本 candidate 的 SHA/tree 记录（`r5-validation:3` 声明由 delivery checkpoint 补录）。这与"第 N 轮 checkpoint 落在第 N+1 轮 commit"的既有模式一致（r4 delivery/review checkpoint 正是本 commit 才入库），且 dispatch 约定由 r5 dispatch 文件记录最终 SHA/tree。
- **O-5 自检 PASS 的性质**：`r5-validation:8–12` 的 `PASS` 为作者在独立 Review 前的自检断言，不得视为本 Reviewer 的结论或任何运行态 PASS；其 `:13` 路线 validator 是以 r4 base 为 live HEAD 执行，本报告已在 candidate HEAD 重跑（见 §8）。
- **O-6 AC 计数口径**：`plan:81` 仍写 `AC1–AC6`（base 既有措辞，R3-06 已登记延期至 P02 closeout，本轮未扩大）；新 r5 文件用 `AC1–AC7`。无任何文件隐去 AC7、无任何文件声称 AC 通过，`doc/tasks/P02.md:39–45` 全部仍为 `[ ]`。

---

## 6. base..candidate 差异路径与 scope 核验

| # | 路径 | 变更 | 许可归属 |
|---|---|---|---|
| 1 | `doc/tasks/P02.md` | +1/−1 | 仅 `### Codex-only scratch-build output boundary`（L58–73）内 L60；r5 ext:63 |
| 2 | `verification/P02/codex-scratch-build-input-host-inventory-r2-build-addendum.md` | +1/−1（L13） | r5 ext:64 |
| 3 | `verification/P02/codex-scratch-build-plan.md` | +1/−1（L81） | r5 ext:65 |
| 4 | `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md` | +13/−1 | r5 ext:66（**N-04**：就地替换 L52 超出"只追加"） |
| 5 | `codex-checkpoint-p02-process-isolation-r5-start.md` | +10 | r5 ext:67 |
| 6 | `codex-process-isolation-r5-validation.md` | +24 | r5 ext:67 |
| 7-8 | `codex-checkpoint-p02-process-isolation-r4-delivery.md`、`…-r4-review.md` | +12/+12 | r3/r4 ext:53（"r4 delivery/review checkpoint"） |
| 9-15 | `dsh-review-process-isolation-r4.{dispatch,exit.txt,mount.txt,prompt,response,session.txt,stderr.txt}` | +11/+1/+2/+29/+132/+3/+0 | r3/r4 ext:55（"r4.* 正式审查附件"） |
| 16 | `dsh-review-process-isolation-r5.prompt.md` | +18 | r5 ext:67（"r5.* 正式审查附件"） |

- **路径集合核验**：`git diff --name-only` 的 16 条中，落在 `doc/tasks/P02.md` 或 `verification/P02/**` 之外的 = **0**；命中 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`apps/`、`src/`、`packaging/`、`requirements*`、`tests/`、Schema/IPC 的 = **0**。
- **Owner allowlist/产品范围**：`doc/tasks/P02.md` 的"允许修改范围"段（L47–56）与 Codex 集成专属治理段（L56）未改；boundary L60 自身声明"不属于 Owner allowlist，不改变 Owner 可改路径、产品 AC、行为基线、共享契约或 Task 状态，也不重冻结 P02"。**未扩大 Owner allowlist** ✓。
- **`STATUS` / `REBASELINE_PLAN`**：未出现在 diff；`doc/STATUS.md:3` 仍为 P02 唯一 Active Task（in_progress / ACTIVE）、Build Gate=`BLOCKED`、AC1–AC6 BLOCKED、Hard Build Barrier 有效（只读复核）。
- **root 保护现场独立复核（只读）**：`G:/CODEX/New Manga` = `main@549a6544f0be1eec66c09ece393fd1a409f10bf3`，203 status entries，staged=0；按 manifest **逐项复算 203/203** path/status/size/SHA-256 全匹配（mismatch=0、err=0）；canonical entries = **36985 bytes / `3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`** ✓。candidate 16 路径 ∩ root dirty = **0**。
- **r4 证据链复核**：checkout 外 raw JSONL `…/p02-process-isolation-plan/dsh-review-logs/dsh-review-process-isolation-r4.stdout.jsonl` = **316609 bytes / `fdc16332785c9f6228ffb64fd4e0ac6051b675a60c4c79f7c2ac8225b0198cd8` / `thinking`×37**，与 r4 dispatch:9、r4-review checkpoint:7 记录一致；r4 `exit.txt`=`0`、`stderr.txt`=0 bytes、`session.txt`=`session-e4de7c63-6bab-4f42-839d-17754dc8d495` ✓。

---

## 7. r3 WSB XML bytes/hash（不变）

| 项 | base `fb0a7668` | candidate `1c7efb17` |
|---|---|---|
| Git blob | `0f795f872f38e3f757f275d642c75bd4ca4f020f`（2609 bytes） | `0f795f872f38e3f757f275d642c75bd4ca4f020f`（2609 bytes） |
| canonical LF bytes / SHA-256 | 2609 / `9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d` | 同左（**逐字节相同**，工作区 2631 bytes 仅为 CRLF 检出转换，无 BOM、无裸 CR） |

与 `scope-delta:56`、`r5-validation:15`、r4 response §4 一致 ✓。

---

## 8. 精确 Gate 状态（不推导、不写 PASS）

| Gate | 状态 | 依据 |
|---|---|---|
| Windows Sandbox Feature（`Containers-DisposableClientVM`） | **UNKNOWN** | 无候选内查询证据；本机查询需提权（`proposal:78,93`）；本轮未查询、未提权 |
| Smoke admission | **NOT_ADMITTED** | `doc/tasks/P02.md:60`（设计 Review 通过 + 条件闭合 + Codex 单独记录 admission + 完整 preflight）；`scope-delta:61`、r5-start:9、r5-validation:20 |
| Isolation Smoke | **NOT_AUTHORIZED / NOT_RUN** | 未执行 `wsb start/connect/exec`；plan:81、r5-validation:20 |
| Build Gate | **BLOCKED** | plan:4/81、r5-start:9、r5-validation:20、`scope-delta:56` |
| build | **NOT_AUTHORIZED / NOT_RUN** | 同上；无任何 build 命令与证据 |
| P02 AC1–AC7 | **全部 `BLOCKED / NOT_RUN`**（`doc/tasks/P02.md:39–45` 全 `[ ]`） | 无任何验收证据；`plan:81` 的 `AC1–AC6` 为已登记延期口径，AC7 未被隐去也未被声称通过 |
| P02 Hard Build Barrier | **保持有效（active）** | plan:81、r5-start:9、r5-validation:20、`scope-delta:56` |
| Design/Scheme Review（本报告） | **APPROVED_WITH_CONDITIONS（仅设计）** | 本文 §2–§4 |

---

## 9. 已执行 / 未执行检查

**已执行（全部只读；未写文件、未改 Git/index、未动 root 或其他 worktree、未提权）**
`git rev-parse HEAD/HEAD^{tree}/HEAD^@/HEAD^`、`git log -1 --format=%H %T %P %aI %cI %an %ae %cn %ce %s`、`git rev-list --count`、`git status --porcelain=v1 --untracked-files=all`（审查前后均 0 项）、`git stash list`、`git worktree list`、`git rev-parse --git-dir/--git-common-dir`、`git diff --name-status/--name-only/--numstat/--stat/--check`（EXIT=0）、`git cat-file blob/-s`、`git show`；`python -X utf8` 内存内复算 r3 XML 行尾归一化 SHA-256、scope-delta 末字节与字面 `` `n ``、root manifest canonical entries hash（203 项 / 36985 bytes / `3a54fa97…`）与 **203/203 逐项 size+SHA-256 复算**、candidate 路径与 root dirty 交集；`git -C "G:/CODEX/New Manga" rev-parse/status`（只读）；`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` 在 **candidate HEAD** 执行 = **EXIT=0**（196 unique nodes、105 集成记录、21 planned nodes DAG、路线状态与链接、governance whitespace 全过；输出 `Product tests/build/GUI: NOT_RUN (planning-only)`），其打印的 `live HEAD=1c7efb17…` 即本 candidate；只读 stat+hash r4 raw JSONL。

**未执行 / 不可复算（限制）**
- 未查询或修改任何 Windows Feature，未提权，未运行 `wsb`，未启动/连接 Sandbox，未执行 Smoke，未 build，未运行 runner/Vitest/GUI/WebView——运行态一律 `UNKNOWN / NOT_RUN / BLOCKED`。`verify_plan.py` 是纯打印式文档/路线 validator（无写文件分支），不属产品测试或 build。
- host `git.exe/cl.exe/link.exe/rc.exe/mt.exe` 的版本/大小/SHA-256 未复核（未读 `C:\Program Files`）；addendum:10–11、:21–24 的这些值为 `NOT_VERIFIED`。
- r3-start 的 `14:34 UTC` 快照值（4280 / `1acbe671…`）不可由 Git 复算（未进入历史）。
- `r5-validation:8–12` 的作者自检 `PASS` 未被采信为本 Reviewer 的独立结论（其对 N-01/N-02/N-03 的对应断言由本报告 §3 独立重做）。
- 本机 PowerShell 处于 ConstrainedLanguage（.NET 静态调用失败、`$env:TEMP` 写入被沙箱拒绝），全部复算改用 git plumbing + python 完成；未申请提权。
- DSH token usage、Desktop session 可见性仅采信版本化证据，未重放。

---

## 10. 下一项安全 Gate 与推荐下一步

1. **下一处纯文档 commit（最高优先、无风险）**：闭合 **N-04**（把 `scope-delta:66` 的许可改为覆盖 `:52` 的就地扩写，或在 r5 delivery checkpoint 内登记该 1 行替换）与 **N-05**（删除末行 `` `n ``、补文件尾换行）；同一提交入库 r5 dispatch/delivery checkpoint，记录最终 candidate SHA/tree。**不得**改 r3 WSB XML/canonical hash、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、Owner allowlist、产品实现/测试、Schema/IPC/依赖。
2. **随后**：按 `proposal:78` 步骤 1 执行本机非提权只读 preflight（root HEAD/branch/common-dir、`wsb` identity/version、`wsb list` 无 running session、固定 clone 路径 `G:\CODEX\P02-scratch-build-source` 不存在、架构/BIOS 虚拟化/RAM/可用内存/磁盘/CPU、全部 HostFolder 与 pinned inputs）。非提权下 Feature 查询失败按设计记 `BLOCKED`，属正确结果。
3. **Smoke admission 必须由 Codex 单独记录**；在此之前 `Smoke=NOT_AUTHORIZED / NOT_RUN`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`、Hard Build Barrier 保持有效。

**推荐下一步（可直接转发 Codex）**
> 在 `codex/P02-process-isolation` 既有 scope 内做一次纯文档收尾并固定新 commit：(1) `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md:66` 的许可改为"只允许追加本 r5 extension 及就地扩写 `:52` 的 r3-start 许可行（不改其他文字）"，或在 r5 delivery checkpoint 中显式登记该 1 行替换；(2) 删除该文件末行残留的字面 `` `n `` 两字节并补文件尾换行；(3) 同提交入库 r5 dispatch/delivery checkpoint（记录 candidate SHA=`1c7efb172b8e9d766e38f84cf3728a90bb5953d0` 或其后继、tree、parent、Review 结论）。不改 r3 XML 与任何 canonical hash、不改 `STATUS`/`REBASELINE_PLAN`/Owner allowlist/产品与契约。此后仅执行本机非提权只读 preflight；`Smoke=NOT_AUTHORIZED/NOT_RUN`、`Smoke admission=NOT_ADMITTED`、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED/NOT_RUN`、AC1–AC7=`BLOCKED`、Hard Build Barrier 有效。

---

**Reviewer 声明**：本次 Review 全程只读；未修改本 checkout、Git/index、root 或其他 worktree；未提权、未查询/更改/启用任何 Windows Feature、未启动/连接 Sandbox、未运行 `wsb`/Smoke/Build/产品 runner/Vitest/GUI/WebView；所有未运行的检查均标为 `UNKNOWN` / `NOT_RUN` / `BLOCKED` / `NOT_VERIFIED`，未写为 PASS。
