# P08 DSH 正式 Review 报告（R6）

---
task_id: P08
reviewer: DeepSeek Harness（非作者；作者/Integrator=Codex）
author: Codex
base_commit: af1ddeec1b998f2ddaf121a85f5fd382561aae1e
reviewed_head: ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369
task_base: ab2f813c0ce311a6712002cafd852b9e7a258380
decision: approved
---

## 1. 范围与依据

**受审交付**：固定 worktree `G:/CODEX/New Manga.worktrees/P08-dsh-review-ecb3b520-r6`（detached）内的 `af1ddeec1b998f2ddaf121a85f5fd382561aae1e..ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369`。P08 Task 级基线仍为 `ab2f813c0ce311a6712002cafd852b9e7a258380`（`doc/tasks/P08.md:13`）。

**提交边界（文件层，主仓 `.git/logs/HEAD:949-953`）**：

| 顺序 | commit | subject |
|---|---|---|
| base | `af1ddeec` | docs(P08): address R4 P3 integration findings |
| 区间 | `bfd70958` | docs(P08): prepare R5 review handoff |
| **head** | **`ecb3b520`** | **docs(P08): address R5 verifier findings** |
| post-delivery | `547894f5` | docs(P08): record R6 review checkpoint |
| post-delivery | `e9795470` | docs(P08): anchor R6 dispatch checkpoint（`refs/heads/main`，`.git/refs/heads/main:1`） |

即被审区间含 **2 个提交**（R5 的 post-delivery Prompt/Handoff 准备 + R5 findings 修订）。本轮 R6 Prompt 与 R6 Handoff 位于 `547894f5`/`e9795470`，**不在被审 head**（head worktree 内 `doc/handoffs/` 仅 5 份 P08 Handoff、`verification/P08/` 无 R6 Prompt，见 §3）。

**只读声明**：本会话未创建、修改、删除或暂存任何项目文件，未 checkout/commit，未改动 Git 状态或 worktree HEAD。**DSH 全部 shell/git/python 命令在沙箱 ACL 授予阶段失败**（见 §6），未提权（无审批通道）。本报告仅在最终答复中交付，未写入仓库。

**先读文件**：`AGENTS.md` 语境、`doc/09_COLLABORATION.md:72/:90/:92`、`doc/tasks/P08.md`、`doc/REBASELINE_PLAN.md`（head 与 base 对照）、`doc/STATUS.md`、`doc/00_INDEX.md:3`、`doc/12_ROADMAP.md:3`、`doc/tasks/README.md:3/:5`、`verification/P08/{verify_scope.py, AC_COVERAGE.md, SCOPE_DRAFT.md, RESUME.md, validation.log, review-dsh-af1ddeec-r5.md, DSH-REVIEW-PROMPT-R5.md}`、`doc/handoffs/P08-{490f9bd9,31c26389-dsh-r2,1ad05d99-dsh-r3,16fb07a9-dsh-r4,af1ddeec-dsh-r5}.md`、`verification/PROJECT-ROADMAP-20261008/verify_plan.py:1-24`、`doc/08_ACCEPTANCE_CRITERIA.md` 相关结构（经 AC_COVERAGE 侧核对）。**未使用聊天记录作为项目事实；D1–D7 未重开、未改写为 Reviewer 裁决。**

## 2. Architecture 结论

产品实现面 = **N/A**（纯文档/验证器 Task）。在 DSH 可用证据范围内未发现分层、冻结契约、共享 Schema、依赖或数据保护边界问题：

- **四页边界未扩**：`AC_COVERAGE.md:8` 维持 `AC-NAV-002 [P0] 一级页面只有四个` = `INCLUDED`；`SCOPE_DRAFT.md:17` 仍写「保留四个一级页面」。
- **Legacy → 目标架构 Gate 未被绕过**：`AC_COVERAGE.md:202`（GATE-69 明写「旧技术术语不得直接套用，等价验收映射前 NOT_RUN」）、`SCOPE_DRAFT.md:49/:71`、`REBASELINE_PLAN.md:40`（P09）、`:49`（P18）、`:51`（P20）均把 Architecture Documentation Rebaseline Task 写为前置；该 Task **未登记、未释放**，head 内无越权创建。
- **P09–P21 未释放**：head `REBASELINE_PLAN.md:32-38`（P01–P07）＋`:40-52`（P09–P21）共 **20 行** `proposed / 未释放`；`:28` 明示「其余 20 项 proposed / 未释放」；`:39` P08 = `in_progress`。`doc/tasks/P08.md:113`、`STATUS.md:20` 同口径。
- **共享契约/源文件保护未回退**：head `verify_scope.py:65-74` 保护集含 `src/apps/tests/packaging`、`doc/contracts`、`doc/reviews`、`AGENTS.md`、`doc/09`、`doc/01–08`、`doc/13`、`AD-001`、`task-inventory.csv`，断言差量为空；head `:104-109` whitespace 范围含 README、全部 P08 Handoff、派生路线目录。
- **数据保护语义无回退**：`SCOPE_DRAFT.md:20/:21/:35`（全库 DB＋Managed Copy、失败回滚、DB-only 不可替代、源文件/Lock/current/pinned 保护）与 `AC_COVERAGE.md` 对应 `INCLUDED` 行保持。

## 3. Verification 矩阵

### 3.1 DSH 实际执行（仅文件层 read/glob/grep；全部为只读）

| # | 场景 | 实际步骤 | 结果 | 证据 |
|---|---|---|---|---|
| 1 | HEAD == reviewed_head | read worktree `.git`（文件）→ `gitdir: G:/CODEX/New Manga/.git/worktrees/P08-dsh-review-ecb3b520-r6`；read 该 admin 目录 `HEAD` | **PASS**：`HEAD:1` = `ecb3b520…`（裸 SHA＝detached） | 绝对路径 read |
| 2 | worktree 未推进 | read admin `logs/HEAD` | **PASS**：仅 1 行 `0000…0000 → ecb3b520… 1791474521 +0800`，无 checkout/commit/rebase | 同目录 `logs/HEAD:1` |
| 3 | common-dir | read admin `commondir`=`../..`、admin `gitdir` 回指本 worktree `.git` | **PASS**：→ `G:/CODEX/New Manga/.git` | `commondir:1`、`gitdir:1` |
| 4 | 被审 head 不含 R6 材料 | glob `verification/P08/*`、`doc/handoffs/P08-*` | **PASS**：无 R6 Prompt；P08 Handoff 恰 **5** 份（R1/R2/R3/R4/R5），无 R6 Handoff | glob 结果 |
| 5 | base/head 文件集对照 | glob 同一目录集于 base worktree（`P08-dsh-review-af1ddeec-r5`） | 新增 3 个文件：`DSH-REVIEW-PROMPT-R5.md`、`review-dsh-af1ddeec-r5.md`、`doc/handoffs/P08-af1ddeec-dsh-r5.md`；`doc/contracts/` 两树同为 7 文件（无增删） | 两侧 glob |
| 6 | **R5-01 复算** | 全文 read head/base `verify_scope.py`（118 vs 115 行）逐行对齐 | **PASS**：见 §4.1 | head `:90-94`、base `:89-91` |
| 7 | **R5-02 复算** | read head `:24-32`；grep `\]\([^)]+\)` 于 head `verification/P08/*.md`、`doc/tasks/P08.md`、`doc/handoffs/P08-*` | **PASS**：见 §4.2 | head `:25-26` |
| 8 | 链接目标存在性 | 逐个把 25 个目标路径解析为绝对路径核对（read/glob） | **PASS**：全部为文件 | 见 §4.2 |
| 9 | 链接样式覆盖 | grep `^\s*\[[^\]]+\]:\s*\S`（引用式定义）于 head `verification/P08/*.md`、`doc/tasks/P08.md`、`doc/handoffs/*.md` | 0 命中（当前无该样式，故未检查样式无实际漏项） | grep 结果 |
| 10 | N-07 无回退 | read head/base `AC_COVERAGE.md:142` 对照 | **PASS**：现文列「单图/ZIP/CBZ/PDF/文本五项」＋D08 未限定 PNG，两树一致 | `AC_COVERAGE.md:142` |
| 11 | N-08 无回退 | read head `:101-103`、`:104-109` | **PASS**：`glob("P08-*.md")`＋`assert handoffs`＋`*handoffs` 入 `git diff --check` | head `:101-109` |
| 12 | R4-01 无回退 | read head `STATUS.md:3/:10/:20-22` | **PASS**：`:10` 现文「本句仅说明编号，不表达节点状态或任务释放」，冻结标记在 `:22` | `STATUS.md` |
| 13 | R4-02 无回退 | read head `:85-100` | **PASS**：正向 allowlist 与谓词原样保留，仅新增负例 | head `:95-100` |
| 14 | R4-03 无回退 | read head `doc/handoffs/P08-490f9bd9.md:37` | **PASS**：指向 `verification/P08/review-dsh-490f9bd.md` 并注明 `doc/reviews/**` 非写入目标 | 该行原文 |
| 15 | N-01/N-06 无回退 | read head `SCOPE_DRAFT.md:40/:71/:73/:75/:83/:84` | **PASS**：五种输出＋PNG 归因；「现存可复用」与「拟议新增」仍区分 | 同上 |
| 16 | N-02 无回退 | read head `verify_plan.py:1-24` | **PASS**：9 个 `STATUS_LABELS` 且 `assert set(...)==TASK_STATES` | 同文件 |
| 17 | N-05 无回退 | read head `AC_COVERAGE.md:3` | **PASS**：明写 `ACG-EXT-DETECT/CONTRACT/NFR` 由 doc/13 追踪 | 同文件 |
| 18 | AC 矩阵结构独立复算 | read head `AC_COVERAGE.md:1-8/:196-212` | **PASS（结构）**：`:7-199` = 193 条编号 AC；`:200` = `D08-AC-SMOKE`；`:201-212` = `D08-GATE-68..79`（12）→ 206 行，与脚本 `len(expected)+1+12` 一致；抽验行均以 `| NOT_RUN |` 结尾 | 同文件行区间 |
| 19 | D1–D7 未重开 | read head `SCOPE_DRAFT.md:17-23` | **PASS**：7 行用户确认表完整，D5 门槛未降 | 同文件 |
| 20 | 文档状态一致性 | grep `P08.*in_progress` 于 head `doc/`；read head `P08.md:1-21`、`Plan:3/:28/:39`、`00_INDEX:3`、`12_ROADMAP:3`、`README:3/:5` | **PASS**：head 内 P08=`in_progress`、20 项未释放，四处导航一致 | 见 §5 |
| 21 | R5 材料内部一致 | read head `review-dsh-af1ddeec-r5.md`（169 行）、`P08-af1ddeec-dsh-r5.md`（68 行）、`DSH-REVIEW-PROMPT-R5.md`（42 行） | 与 R5 结论、base/head、SHA256、session 一致；R5 Prompt/Handoff 按 §90 属 post-delivery 材料但在被审区间内（授权路径） | 三文件原文 |
| 22 | 提交链 | read 主仓 `.git/logs/HEAD:920-953`、`.git/refs/heads/main` | 见 §1 表 | 同文件 |

### 3.2 DSH 未执行（NOT_RUN）

| 场景 | 原因 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain=v1 --branch` / `git diff --check` / `git diff --name-only` / `git diff --exit-code` / `git show BASE:…` | 6 次 `pwsh` 调用（默认 workdir ×2、`workdir=C:\Windows\Temp`、`workspace-write` 重试、后台 job `pwsh-8`、`danger-full-access` 提权）**全部**在沙箱 ACL 授予阶段失败：`Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\P08-dsh-review-ecb3b520-r6)`；提权被拒（`requires approval, but no approval channel is available`）。未再提权。 |
| `python -B -X utf8 verification/P08/verify_scope.py`、`…/verify_plan.py` | 无 python/shell；**producer（Codex）记录 EXIT=0**，归 Codex，不冒称 DSH。 |
| 产品 pytest/cargo/vitest/GUI/build/model | 本 Task 无产品变更，**正确保留 NOT_RUN**。 |

### 3.3 DSH 未验证（NOT_VERIFIED）

| 项 | 说明 |
|---|---|
| worktree 工作树 == `ecb3b520` 提交树 / clean | 无 `git status`；仅 HEAD/`logs/HEAD`/`commondir` 文件层旁证 + head 内已含 R5-01/R5-02 修订文本。Codex 断言见主工作区 `validation.log:426`（`git diff --exit-code HEAD -- .` EXIT=0），**归 Codex**。 |
| `af1ddeec..ecb3b520` 差集**完整枚举** | 无法运行 git。可达代理：区间 2 个提交且 subject 与声明一致；base/head 目录集对照新增 3 个文件（全在授权路径）；`doc/contracts/` 文件集一致；Codex 记录 BASE..HEAD allowlist 28→31（主工作区 `validation.log:404`→`:428`），与我观察到的 +3 新增文件数一致。**不排除**「改动某授权路径外已存在文件而不改变文件数」的可能。 |
| 受保护路径零差量（`src/apps/tests/packaging`、`doc/contracts`、`doc/reviews`、`doc/01–08`、`doc/13`、`AD-001`、`AGENTS.md`、`doc/09`、inventory） | 无 git；仅 `doc/contracts/` 文件集两树一致 + Codex 断言（head `validation.log:431` EXIT=0 空；主工作区 `:421`）。内容级等同未由 DSH 证明。 |
| R5 报告 SHA256（`2EA2ADA0…`）与工作树文件等同性复算 | 无 `Get-FileHash`；仅逐字 read。 |
| R6 Prompt 文件与 CLI 收到文本的 hash 等同 | 已逐行读取主工作区 `DSH-REVIEW-PROMPT-R6.md`（28 行）并与本人收到的 Prompt 文本比对一致；未做 SHA256。 |
| 206 行 AC 结果列的逐行 `NOT_RUN` | 抽验 30 行均符合；未逐行核验。 |

## 4. R5-01 / R5-02 逐项独立复算（不沿用作者自述）

### 4.1 R5-01（P3）→ **DSH 独立确认 closed**

**复核点 1：是否明确断言拒绝非 P08 Handoff 与 `doc/reviews/**`**

- head `verify_scope.py:90`：`assert allowed("verification/P08/review-example.md") and allowed("doc/handoffs/P08-r5.md")`（允许样例）
- head `:91` 拒绝 `doc/10_CURRENT_STATE_AND_GAPS.md`；`:92` 拒绝 `doc/handoffs/P08/nested.md`（原有）
- head `:93` **新增** `assert not allowed("doc/handoffs/M2-x.md")` ✅
- head `:94` **新增** `assert not allowed("doc/reviews/x.md")` ✅

**复核点 2：谓词语义独立推演**（head `:85-88`＋`:74-83`）：`allowed_files` 精确集（`doc/tasks/P08.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/tasks/README.md`、派生目录 4 个具名文件）＋前缀 `verification/P08/`＋非嵌套 `doc/handoffs/P08-*.md`。逐例：`doc/handoffs/M2-x.md` 三支均不命中 → False ✅；`doc/reviews/x.md` 三支均不命中 → False ✅；`doc/handoffs/P08/nested.md` 因前缀是 `doc/handoffs/P08-`（连字符）而实际由**前缀条件**拒绝，而非 R5 报告 `:91` 所述「由 `/` not in … 子句拒绝」——结论相同，仅该句归因不精确（见 §5 R6-O3）。负例断言位于任何 `subprocess` 调用之前，故即使 git 不可用也会先执行。

**复核点 3：既有正向 allowlist 仍约束固定已提交差量、排除他人未提交 dirty**

- head `:95-100`：`changed = git diff --name-only --no-renames BASE HEAD`；`outside_scope = [p for p in changed if not allowed(p)]`；`assert not outside_scope` ✅
- `BASE` = `ab2f813c…`（`:8`，P08 Task 基线）→ 覆盖范围是 `af1ddeec..ecb3b520` 被审区间的**超集**（更严）✅
- `git diff A B` 比较提交树与提交树，**结构上排除**主工作区未提交 dirty（原作者内容不进入集合）✅；`--no-renames` 避免重命名折叠漏检 ✅
- `:65-74` 保护路径检查仍为 `git diff BASE -- <paths>`（BASE vs 工作树，含未提交，方向 fail-closed 偏保守）✅

**结论**：R5-01 已按要求的最小范围修订，且未削弱原正向约束。**closed（DSH 独立确认）**。

### 4.2 R5-02（P3）→ **DSH 独立确认 closed**

**复核点 1：循环是否包含 `doc/handoffs/P08-*.md`**

- head `:25`：`handoffs = list((ROOT / "doc/handoffs").glob("P08-*.md"))`
- head `:26`：`for doc in list(HERE.glob("*.md")) + [ROOT / "doc/tasks/P08.md"] + handoffs:` ✅
（base `:25` 无 `handoffs`、`:26` 无 `+ handoffs`；这是本交付在文件头部的唯一新增行。）

**复核点 2：其余链接范围是否正确**：保留 `verification/P08/*.md`（14 个 md）＋`doc/tasks/P08.md`；未扩大、未缩小既有范围 ✅。`target.strip("<>").split("#",1)[0]` 与 `"://" not in target` 仍跳过外链并剥离锚点 ✅。

**复核点 3：固定 head 中所有 P08 Handoff 链接可解析**

| 文件 | 链接 | 目标 | 解析 |
|---|---|---|---|
| `doc/handoffs/P08-490f9bd9.md:14` | 见[范围材料](…) | `verification/P08/SCOPE_DRAFT.md` | 存在 ✅ |
| `doc/handoffs/P08-16fb07a9-dsh-r4.md:28` | [DSH R3报告](…) | `verification/P08/review-dsh-1ad05d99-r3.md` | 存在 ✅ |
| R2/R3/R5 Handoff | grep `\]\(` 0 命中 | — | 无链接 ✅ |

**复核点 4：全循环目标独立枚举**（head 工作树）：`verification/P08/*.md` 7 个链接目标、`doc/tasks/P08.md` 19 个、Handoff 2 个，合计 **25 个目标全部为存在的文件**（含 `../PROJECT-ROADMAP-20261008/core-audit.md`、`desktop-audit.md`、`AC_COVERAGE.md`、`DSH-REVIEW-PROMPT.md`、`P08-490f9bd9.md`、`doc/08`、`doc/13`、`REBASELINE_PLAN.md`、`REPORT.md`、`RESUME.md`、`preliminary-review.md`、`review-dsh-{490f9bd,31c2638,1ad05d99-r3,16fb07a9-r4,af1ddeec-r5}.md`、`validation.log`、`handoffs/P08-{490f9bd9,31c26389-dsh-r2,1ad05d99-dsh-r3}.md`、`DSH-REVIEW-PROMPT-R3.md`）。R6 Handoff 为 delivery 后追加，**不在** head/区间内，无需被本轮解析（与 Prompt 一致）。

**结论**：R5-02 修订有效、非破坏性（head 在该循环下不会报错，我逐目标核对成立）。**closed（DSH 独立确认）**。

## 5. 文档状态与提交边界（两时间点不混为矛盾）

**被审 head `ecb3b520` 内（交付时前置状态，来源＝固定 worktree）**

- `doc/tasks/P08.md:5` `status: in_progress`；`:6 previous_status: approved`；`:13 base_commit=ab2f813c…`；`:17 reviewed_head=af1ddeec…`；`:19 review_session=session-14106c72…`；`:113`「R5-01/R5-02 … 保持 open 直至新 head 经 R6 非作者复核」。
- `doc/REBASELINE_PLAN.md:3`「in_progress 1，proposed / 未释放 20」；`:39 | P08 | in_progress |`。
- `doc/STATUS.md:3`「P08=`in_progress`」；`doc/00_INDEX.md:3`、`doc/12_ROADMAP.md:3`、`doc/tasks/README.md:3/:5` 同口径。
- `verification/P08/RESUME.md:3` TaskStatus=`in_progress`、`:7` 记 checkpoint 提交 `bfd70958` 并注明「以实时 Git status 为准」。

**delivery 之后的主工作区状态（来源＝主工作区绝对路径；提交边界＝`547894f5`+`e9795470`）**

- `G:/CODEX/New Manga/doc/tasks/P08.md:5` `status: in_review`；`:6 previous_status: in_progress`；`:17 reviewed_head=ecb3b520…`；`:18 review_worktree=G:/CODEX/New Manga.worktrees/P08-dsh-review-ecb3b520-r6`；`:19 review_session: pending`；`:20 review_report=verification/P08/review-dsh-ecb3b520-r6.md`。
- `G:/CODEX/New Manga/doc/STATUS.md:3`「R5-01/R5-02修订head=`ecb3b520`，R6独立Review准备完成、待派发。P08=`in_review`」；`G:/CODEX/New Manga/doc/REBASELINE_PLAN.md:3/:28/:39` 同。
- `G:/CODEX/New Manga/verification/P08/validation.log:424-447` 记录 Codex 在精确 R6 worktree 与主工作区的运行（EXIT=0、31 个 BASE..HEAD allowlist 文件、受保护路径空）、`:442` 记录 post-delivery 审计修正项；`:435-447` 记录 R6 Prompt/Handoff 检查点提交 `547894f5`。
- `G:/CODEX/New Manga/verification/P08/` 已有 `dsh-r6.stdout.md`/`dsh-r6.stderr.log`（本轮原始输出，untracked），但**尚无** `review-dsh-ecb3b520-r6.md`（待归档）。

**结论**：head 的 `in_progress` 是交付时状态快照；`in_review`／`reviewed_head=ecb3b520`／`review_session=pending` 属 `547894f5`/`e9795470` post-delivery 同步。**两者不是矛盾**，且 R6 Prompt/Handoff 确不在被审 head 内。P09–P21 仍未释放；架构文档重基线 Gate 仍未绕过。

## 6. Findings

| ID | 级别 | 文件/位置 | 触发与影响 | 证据 | 处置 |
|---|---|---|---|---|---|
| **R6-01** | **P3（非阻断）** | `doc/REBASELINE_PLAN.md:10`（被审 head） | 该句称「当前21个规划节点沿用 `P01–P21`，**状态为 `proposed / 未释放`**」，与同文件 `:3`（in_progress 1）、`:28`（P08 in_progress）、`:39`（`| P08 | in_progress |`）自相矛盾——与 R4-01（`doc/STATUS.md:10`）同类，但 Plan 孪生句未按同一口径修订。可致读者误判 P08 未释放。**非本交付引入**：head 与 base 该行逐字相同；位于冻结标记 `## 2026-10-08 完成：`（Plan 首次出现于 `:60`）之前的可变段。 | head `:3/:10/:28/:39`；base `:10`（相同）；主工作区 `:10` 已改为「当前P08=`in_review`，其余20项=`proposed / 未释放`」，且 `validation.log:442` 记载「outdated 21-proposed wording」已修正 | **open（P3，非阻断）**；修正已在 post-delivery `547894f5` 落地，集成 Gate 记录该证据即可，无需因此单独重开新 head |
| **R6-O1** | P4（信息） | `verification/P08/RESUME.md:7` | 记「恢复核验前的提交HEAD=bfd70958…R5结果与导航同步尚未提交」，而同一提交 `ecb3b520` 已包含该同步；文件自身声明「以实时 Git status 为准」，恢复期易短暂误读。 | head `RESUME.md:3/:7`（与 head 状态实际一致） | 观测项；建议下次状态同步顺手更正，不影响本轮结论 |
| **R6-O2** | P4（信息） | `verification/P08/verify_scope.py:25-32` | 链接检查刻意限定 P08 自有文档（`verification/P08/*.md`、`doc/tasks/P08.md`、P08 Handoff），不覆盖 Plan/STATUS/00_INDEX/12_ROADMAP/tasks-README 的链接；且仅解析行内 `](…)`，不解析引用式定义或 HTML 链接。**当前无实际漏项**：引用式定义 grep 0 命中，被审文件 25 个目标全部存在。 | §3.1 #7/#8/#9 | 观测项（范围边界已如实声明，不构成本交付缺陷） |
| **R6-O3** | P4（信息） | `verification/P08/review-dsh-af1ddeec-r5.md:91` | R5 归档报告称 `doc/handoffs/P08/nested.md`「由 `/` not in … 子句拒绝」；按谓词实读，该例由前缀 `doc/handoffs/P08-`（连字符）条件拒绝。结论不变，仅归因不精确。 | head `verify_scope.py:85-88` | 观测项（历史报告保留原样，不要求改写） |

**未发现新的 P0/P1/P2；R5-01/R5-02 无残留；R4-01/02/03、N-01..N-08 及 R1/R2 历史 Finding 无回退。**

## 7. 历史 Finding 回归

| 项 | 位置 | 本轮独立核验 | 结论 |
|---|---|---|---|
| R4-01 P3 | `STATUS.md:10` | 现文只述编号并指向页首/Plan；冻结段在 `:22` | 无回退（closed 保持） |
| R4-02 P3 | `verify_scope.py:74-100` | 正向 allowlist 与谓词保留，仅新增 2 条负例 | 无回退（closed 保持） |
| R4-03 P3 | `doc/handoffs/P08-490f9bd9.md:37` | 指向真实报告并注明 `doc/reviews/**` 只读 | 无回退（closed 保持） |
| N-07 P2 | `AC_COVERAGE.md:142` | 现文与 base 逐字一致，列五项且注明 D08 未限定 PNG | 无回退 |
| N-08 P3 | `verify_scope.py:101-109` | `glob`＋`assert handoffs`＋入 `diff --check`，5 份 Handoff 覆盖 | 无回退 |
| N-01/N-02/N-03/N-04/N-05/N-06 | `SCOPE_DRAFT.md:40/:71/:83`、`verify_plan.py:11-24`、`verify_scope.py:66-67/:104-109`、`AC_COVERAGE.md:3` | 抽样逐项命中（§3.1 #15-17） | 无回退 |
| R1 4×P1/6×P2/5×P3、R2 记录 | `doc/tasks/P08.md:50-59/:69-74` | 处置表保持 closed 且与文件实现一致 | 无回退 |
| D1–D7 | `SCOPE_DRAFT.md:17-23` | 7 行用户确认表完整，未被改写为 Reviewer 裁决，D5 门槛未降 | **未重开** |

## 8. 风险与结论

**decision = `approved`**（仅对 `base=af1ddeec1b998f2ddaf121a85f5fd382561aae1e`、`reviewed_head=ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369` 有效；head 变动后不得延用）。

理由：
1. **0×未闭合 P0/P1/P2**。R5-01、R5-02 两项 P3 已被 DSH **独立确认 closed**（§4，基于被审 head 文件原文＋谓词推演＋25 个链接目标存在性核对，未依作者自述）。
2. **范围未扩大**：被审区间仅 2 个提交（R5 Prompt/Handoff 准备 + R5 verifier findings 修订）；base/head 目录集对照仅新增 3 个文件（R5 Prompt、R5 Handoff、R5 报告），全部落在 P08 授权路径（`verification/P08/**`、`doc/handoffs/P08-*.md`）；`doc/contracts/` 两树文件集一致。DSH **未能**运行 git，故"完整差集枚举 + 受保护路径零差量"仍为 `NOT_VERIFIED`（Codex 证据：head `validation.log:428` 31 文件 allowlist、`:431` 受保护路径空）。
3. **无历史回退**：R4-01/02/03、N-07/N-08、N-01..N-06、R1/R2 处置均无退化；D1–D7 未重开。
4. **边界未被绕过**：四页边界、Legacy→目标架构 Rebaseline Gate、共享契约/源文件保护、P09–P21 未释放均保持；交付 head 内状态为 `in_progress`，post-delivery 同步为 `in_review`（`547894f5`/`e9795470`），两者时间点不同、非矛盾。
5. 本轮新增仅 **1 项非阻断 P3（R6-01）＋3 项观测**，不触及产品范围、AC 来源、数据保护或发布门槛，不构成禁批条件；R6-01 的修正已在 post-delivery `547894f5` 落地。

**剩余风险（须由 Codex 集成 Gate 承接）**：
① 命令级证据（两 validator、`git diff --check`、clean、受保护路径零差量、31 文件差集）全部为 Codex 归属，DSH 为 `NOT_RUN/NOT_VERIFIED` → 集成时应在固定 head 复跑并留环境头与 EXIT；
② 工作树 == 提交树未由 DSH 验证；
③ 正向 allowlist 对**未提交**内容不可见，故「差量合规」与「工作树干净」必须分别取证；
④ 集成提交需明确记录 R6-01（Plan:10 措辞）修正来源（`547894f5`）与 R5-01/R5-02 关闭状态。

**本批准不等于 P08 完成**：不改变 P08 的 post-delivery `in_review`，不代表集成结论，不释放 P09–P21，不改变 Architecture Documentation Rebaseline Task 未登记/未释放的现状；所有产品结果仍为 `NOT_RUN`，未把任何 `NOT_RUN`/`NOT_VERIFIED` 改写为 PASS。

## 9. 下一任务建议（符合 `doc/09_COLLABORATION.md` §5.1）

1. **Task**：P08 的 **Codex 集成 Gate**（不新建产品 Task，不释放 P09–P21）。
2. **Agent**：Codex＝Integrator（Owner 兼作者）；如因集成产生**新固定 head**，Reviewer 必须为 DeepSeek Harness（非作者），**不得自审**。
3. **Recovery point**：仓库=`G:/CODEX/New Manga`；branch/worktree=`main` / `G:/CODEX/New Manga`；P08 Task base=`ab2f813c0ce311a6712002cafd852b9e7a258380`；本轮 reviewed_head=`ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369`；R6 worktree=`G:/CODEX/New Manga.worktrees/P08-dsh-review-ecb3b520-r6`；R6 Prompt=`verification/P08/DSH-REVIEW-PROMPT-R6.md`、R6 Handoff=`doc/handoffs/P08-ecb3b520-dsh-r6.md`（均 post-delivery，位于 `547894f5`/`e9795470`）。
4. **允许/禁止范围**：Reviewer 只读；Codex 仅在 P08 授权的 `doc/tasks/P08.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/tasks/README.md`、`verification/P08/**`、本 Task 自有 Handoff、派生 `REPORT/ROADMAP/RESUME/verify_plan.py` 的 P08 状态范围内收尾；**禁止**产品源码/测试/打包、共享契约/Schema/依赖、`doc/04`/`doc/08`/`AD-001`/`doc/13` 源文件与用户数据；不释放 P09–P21；不恢复 Qoder。
5. **Deliverables**：① 归档本 R6 报告原文（含 SHA256）并挂载真实 session/CLI exit；② 记录 R5-01/R5-02 closed 与 R6-01（Plan:10）修正证据；③ 在固定 head 复跑 `python -B -X utf8 verification/P08/verify_scope.py`、`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`、`git diff --check af1ddeec… ecb3b520… -- <P08授权路径>`、`git diff --name-only af1ddeec… ecb3b520… -- <受保护路径>`，逐次入库环境/EXIT；④ 更新 Task/Plan/Status/Index/Roadmap/Handoff/RESUME。
6. **Verification/Gate**：命令级证据须绑定固定 head 且带 shell/解释器头与 EXIT；`NOT_RUN`/`NOT_VERIFIED` 不得写成 PASS；P0/P1 未闭合、D1–D7 或数据保护回退、关键证据缺失时不得置 `done`。
7. **可直接转发指令**：请在 `G:/CODEX/New Manga`（`main`）接收 DSH R6 `approved` 报告并归档原文与 SHA256（建议归档为 `verification/P08/review-dsh-ecb3b520-r6.md`），确认 DSH native session 与 CLI exit；在固定 head `ecb3b520` 复跑上述两个 validator 与两条 git 差量检查并记录环境/EXIT；核对 R6-01 所指 `doc/REBASELINE_PLAN.md:10` 措辞修正已在 `547894f5` 落地并留证；完成 P08 全部 AC、非作者 Review、集成检查与集成后验证后，才可将 P08 置 `done` 并同步状态——在此之前保持 P08 未完成、P09–P21 未释放，不修改 `doc/04`/`doc/08`/`AD-001`/`doc/13` 与产品源码/测试，`NOT_RUN`/`NOT_VERIFIED` 不得改写为 PASS。

**非作者/只读声明**：本会话未修改、创建、删除任何项目文件，未 stage/commit/checkout，未改动 Git 状态或 worktree HEAD；唯一命令通道（pwsh）因 `SetNamedSecurityInfoW` Win32 5 在沙箱 ACL 授予阶段失败共 6 次（含换 workdir、后台执行与一次提权尝试），未获提权，故一切命令级证据均记为 `NOT_RUN`/`NOT_VERIFIED` 并明确区分 Codex 来源。
