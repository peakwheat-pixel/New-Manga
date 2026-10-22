# P08 DSH 正式 Review（R5）

---
task_id: P08
reviewer: DeepSeek Harness（非作者；作者/Integrator=Codex）
author: Codex
base_commit: 16fb07a973b36b0b129945bc3a85f9ae51234982
reviewed_head: af1ddeec1b998f2ddaf121a85f5fd382561aae1e
decision: approved
---

## 1. 范围与依据

**受审交付**：`16fb07a973b36b0b129945bc3a85f9ae51234982..af1ddeec1b998f2ddaf121a85f5fd382561aae1e`（R4 三项 P3 修订）。P08 Task 级基线仍为 `ab2f813c0ce311a6712002cafd852b9e7a258380`（`doc/tasks/P08.md:13`）。

**审查 worktree 与环境（DSH 文件层独立核验，全部 PASS）**：

| 事实 | 读取位置 | 结果 |
|---|---|---|
| HEAD == reviewed_head | `G:/CODEX/New Manga/.git/worktrees/P08-dsh-review-af1ddeec-r5/HEAD:1` = `af1ddeec1b998f2ddaf121a85f5fd382561aae1e`（裸 SHA = detached） | PASS |
| worktree 自创建起未推进 | 同目录 `logs/HEAD` 仅 1 行：`0000…0000 → af1ddeec… peakwheat-pixel 1791473109 +0800`，无 checkout/commit/rebase | PASS |
| 反向绑定 | `.git`（文件）= `gitdir: G:/CODEX/New Manga/.git/worktrees/P08-dsh-review-af1ddeec-r5`；admin `gitdir` 回指本 worktree | PASS |
| common-dir | admin `commondir` = `../..` → `G:/CODEX/New Manga/.git`，与 Prompt 期望一致 | PASS |

**固定差量定位（Git 文件层；DSH shell 不可用）**：读主仓 `G:/CODEX/New Manga/.git/logs/HEAD:946-950` 得提交链
`16fb07a9`「record R3 review and fixes」→ `1ec14aa2`「prepare R4 review handoff」→ `893df221`「record active R4 review checkpoint」→ `0c209deb`「archive approved R4 review」→ **`af1ddeec`「address R4 P3 integration findings」** → `bfd70958`「prepare R5 review handoff」。

据此核验 Prompt 的关键范围陈述：**R5 Prompt/Handoff 位于被审 head 的子提交 `bfd70958`，不属于被审 head** ✅。head 内旁证：`grep af1ddeec` 于 `*.{md,py,log}` **0 命中**；`verification/P08/` 下无 R5 Prompt（仅 `DSH-REVIEW-PROMPT.md`/`-R2`/`-R3`/`-R4`）；`doc/handoffs/` 内 P08 Handoff 恰 4 份（R1 `P08-490f9bd9.md`、R2、R3、R4）。故被审 head 内既无 R5 Prompt，也无 R5 会话/报告/EXIT 记录——与 `doc/09_COLLABORATION.md:90`（Handoff 于交付 head 之后追加）及 R2/R3/R4 先例同构。

**先读文件**：`AGENTS.md`、`doc/09_COLLABORATION.md`（§4 状态机、§5.1）、`doc/templates/REVIEW.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P08.md`、`doc/tasks/README.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/handoffs/P08-490f9bd9.md`、`doc/handoffs/P08-16fb07a9-dsh-r4.md`、`verification/P08/{verify_scope.py,AC_COVERAGE.md,SCOPE_DRAFT.md,validation.log,RESUME.md,review-dsh-16fb07a9-r4.md,review-dsh-490f9bd.md}`、`verification/PROJECT-ROADMAP-20261008/{verify_plan.py,ROADMAP.md,RESUME.md,REPORT.md}`、首轮报告引用的源文 `doc/08_ACCEPTANCE_CRITERIA.md`。**未使用聊天记录作为项目事实。D1–D7 未重开、未改写为 Reviewer 裁决。**

**只读声明**：本会话未修改、创建或删除任何项目文件，未 stage/commit/checkout，未改动 Git 状态或 worktree HEAD。**唯一命令尝试全部在沙箱 ACL 授予阶段失败**：`git rev-parse HEAD`、`git status --porcelain=v1 --branch`（默认 workdir 与 `C:\Windows\Temp` 均复现），原始错误为
`Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\P08-dsh-review-af1ddeec-r5)`。**未提权**（无审批通道）。

## 2. Architecture 结论

产品实现面 = `N/A`（纯文档/验证器修订 Task，`src/apps/tests/packaging` 无变更）。在记录范围内**未发现分层、冻结契约、共享 Schema、依赖或数据保护边界问题**（`executed` = 文件层 read/grep；DSH 未能运行 git/python）：

- **四个一级页面未扩**：`AC_COVERAGE.md:8` 维持 `AC-NAV-002 [P0] 一级页面只有四个` 为 `INCLUDED`；`SCOPE_DRAFT.md:31`（四页 must，定义指向 D04 §1.1）、`:17`（D1「保留四个一级页面」）无扩页表述。
- **Legacy → 目标架构口径正确且 Gate 未被绕过**：`SCOPE_DRAFT.md:49` 声明 D07/D08 仍是 Legacy 生产基线，`AC-PKG-001/003`、§6 PySide6、§69 ViewModel 属 stack-specific，须由**单独授权、正式释放**的 Architecture Documentation Rebaseline Task 产出目标等价表述，在此之前只记 `NOT_RUN`；`AC_COVERAGE.md:3`、`:202`（GATE-69 明写"旧技术术语不得直接套用，等价验收映射前 NOT_RUN"）同口径；`REBASELINE_PLAN.md:40`（P09）、`:49`（P18）、`:51`（P20）把该 Gate 写为前置。该 Task 未登记、未释放，P08 未越权创建或释放它。
- **P09–P21 全部未释放**：`REBASELINE_PLAN.md:32-38`（P01–P07）+ `:40-52`（P09–P21）共 **20 行** `proposed / 未释放`；`:39` P08 = `approved` 且行内明示"R4-01..03 三项 P3 待集成处理与新 head 独立复审"、`:28` 明示"其余 20 项 proposed / 未释放"。`doc/tasks/P08.md:40-42` 三项未勾选 AC 含"Codex最终集成检查及Task done"，`integration_commit: null`。**未发现任何"已释放/已实现"措辞。**
- **共享契约/源文件保护**：`verify_scope.py:65-73` 保护集含 `src/apps/tests/packaging`、`doc/contracts`、`doc/reviews`、`AGENTS.md`、`doc/09_COLLABORATION.md`、`doc/01–08`、`doc/13`、`AD-001`、`task-inventory.csv`，断言其差量为空；正向 allowlist 精确到 `doc/tasks/P08.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/tasks/README.md`、派生路线目录**仅 4 个具名文件**、`verification/P08/**`、非嵌套 `doc/handoffs/P08-*.md`——与 `doc/tasks/P08.md:111` 完全一致，且**拒绝**同目录未授权兄弟文件（如 `verification/PROJECT-ROADMAP-20261008/plan-audit.md`）。无放大。
- **数据保护语义无回退**：全库备份（DB＋Managed Copy、失败回滚、DB-only 不可替代）见 `SCOPE_DRAFT.md:20`/`:42`；源文件/Lock/current/pinned/人工修改保护见 `:35`（Pin 保留、`current` 按 AC-REV-*/AC-CLEAN-001 核对）与 `AC_COVERAGE.md` 对应 `INCLUDED` 行。

## 3. Verification 矩阵

### 3.1 DSH 实际执行（read/grep；无 shell）

| 场景 | 步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| HEAD == reviewed_head | read worktree admin `HEAD` | DSH read | **PASS**（严格相等，detached） | `HEAD:1` = `af1ddeec…` |
| worktree 未推进 | read `logs/HEAD` | 同上 | **PASS** | 1 行；创建即该 head，时间戳 `1791473109`（commit 时间 `1791473082` 之后 27s） |
| common-dir | read `commondir`/`gitdir`/`.git` | 同上 | **PASS** | `../..` → `G:/CODEX/New Manga/.git` |
| 被审 head 不含 R5 交付物 | grep `af1ddeec`（`*.{md,py,log}`）；glob `verification/P08/**`、`doc/handoffs/P08-*` | 同上 | **PASS** | 0 命中；无 R5 Prompt；4 份 Handoff |
| 固定差量链位 | read 主仓 `.git/logs/HEAD:946-950` | 同上 | **PASS** | R5 交付物在其子提交 `bfd70958` |
| R4-01 文本 | read `doc/STATUS.md:3/:10/:20/:22` | 同上 | **PASS**（详见 §4） | 见 §4.1 |
| R4-02 谓词与断言 | read `verify_scope.py` 全文 | 同上 | **PASS**（逻辑层；详见 §4.2） | 见 §4.2 |
| R4-03 文本 | read `doc/handoffs/P08-490f9bd9.md:37` | 同上 | **PASS**（详见 §4.3） | 见 §4.3 |
| N-07 源文事实（独立复算） | read `doc/08:2051-2066`；grep `PNG` | 同上 | **PASS**：`AC-EXPORT-001 [P0]` 恰列 **单图/ZIP/CBZ/PDF/文本** 五项；`doc/08` 全文 **0 次 "PNG"** | `doc/08:2054-2064` |
| 差量路径代理核验 | grep `16fb07a9`（`*.{md,py,log}`） | 同上 | **PASS（代理）**：19 个文件命中全部落在 P08 允许路径内（`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/REBASELINE_PLAN.md`、`doc/tasks/P08.md`、`doc/tasks/README.md`、`doc/handoffs/P08-16fb07a9-dsh-r4.md`、`verification/P08/**`、`verification/PROJECT-ROADMAP-20261008/{REPORT,ROADMAP,RESUME}.md`），无越权路径 | grep 结果 |
| 导航一致性 | grep/read `STATUS:3`、`Plan:3/:28/:39`、`00_INDEX:3`、`12_ROADMAP:3/:9`、`README:3/:5`、`P08.md:5/:17/:40-42` | 同上 | **PASS**：P08=`approved`（待 Codex 集成）、20 项未释放、不释放后继实现，全部一致 | 同上 |

### 3.2 命令级（DSH 未执行）

| 场景 | 命令 | 结果 | 说明 |
|---|---|---|---|
| 身份/状态 | `git rev-parse HEAD`、`git status --porcelain=v1 --branch` | **NOT_RUN（DSH）** | `SetNamedSecurityInfoW Win32 5`，换 workdir 亦复现；未提权 |
| 两个 validator | `python -B -X utf8 verification/P08/verify_scope.py`、`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` | **NOT_RUN（DSH）**；producer EXIT=0 | producer 侧记录见主仓（post-delivery）`validation.log:404-405`；**其 EXIT 归 Codex** |
| 固定范围 whitespace | `git diff --check 16fb07a… af1ddeec… -- <P08允许路径>` | **NOT_RUN（DSH）**；producer EXIT=0 | `validation.log:406`、`doc/handoffs/P08-af1ddeec-dsh-r5.md:31` |
| 受保护路径差量 | `git diff --name-only 16fb07a… af1ddeec… -- <受保护路径>` | **NOT_RUN（DSH）**；producer 空 | `validation.log:407`（仅 `src apps tests packaging`）、`handoff:32`（全保护集） |
| 产品 pytest/cargo/vitest/GUI/build/model | 未运行 | **NOT_RUN（正确保留）** | 无产品变更；`handoff:33`、`P08.md:127` 同记 |

## 4. R4-01..03 逐项处置与复现证据

### 4.1 R4-01（P3）→ **closed（DSH 独立确认）**

- **R4 缺陷**：`doc/STATUS.md:10` 在同一可变段内称"21 个规划节点…状态为 proposed / 未释放"，与 `:3`/`:20` 的计数自相矛盾。
- **现文（`doc/STATUS.md:10`）**：`2026-10-08 最新编号裁决：规划任务ID沿用 P01–P21；本句仅说明编号，不表达节点状态或任务释放。当前状态与授权以本文件开头的Active Task及REBASELINE_PLAN顶部为准。原始审计、台账与历史验证日志保留为固定快照。`
- **逐项核验**：① 只说编号、明示"不表达节点状态或任务释放" ✅；② 权威来源明确指向"本文件页首 Active Task"＋`REBASELINE_PLAN` 顶部 ✅（Plan 顶部 `:3` 与 `:28` 正是该权威计数）；③ 同文件计数一致：`:3`「approved 1、proposed / 未释放 20」、`:20`「P08 approved，其余20项 proposed / 未释放」，与 `Plan:3/:28/:39` 一致 ✅；④ `:10` 位于**可变段**（冻结标记 `## 2026-10-08 完成：` 在 `:22`）——即修订未触碰 `verify_scope.py:112` 断言逐字不变的冻结历史段 ✅。
- **复现证据**：`doc/STATUS.md:3/:10/:20/:22`；`REBASELINE_PLAN.md:3/:28/:39`；`verify_scope.py:109-113`。
- **结论**：原矛盾句已被替换，不再声称所有节点 `proposed / 未释放`，权威来源与编号说明分离清晰。**无残留。**

### 4.2 R4-02（P3）→ **closed（含 2 条非阻断观察 R5-01/R5-02）**

- **R4 缺陷**：范围守卫为否定式（受保护集零差量＋枚举集 whitespace），**无正向断言"差量 ⊆ P08 允许路径"**，`doc/10`/`doc/11`/`doc/templates/**`/非 P08 Handoff/其他 `verification/*` 被改不会触发任何断言。
- **现文（`verify_scope.py:74-97`）**：新增 `allowed_files` 精确集、`allowed(path)` 谓词、自检断言，以及对**已提交** `BASE..HEAD` 的正向 allowlist：
  - `:93-94` `changed = git diff --name-only --no-renames BASE HEAD`；`:95-96` `outside_scope = [p for p in changed if not allowed(p)]; assert not outside_scope`。
- **逐项答复 Prompt 的四个问题**：
  1. **是否对固定 BASE..HEAD 已提交差量实施正向 allowlist**：是。`BASE`＝`ab2f813c…`（`:8`，P08 Task 基线），故覆盖范围是 `16fb07a..af1ddeec` 的**超集**；两提交形式的 `git diff A B` 比较的是**树与树**，与本轮 Prompt 指定的 diff 结果一致或更严。`--no-renames` 避免重命名被折叠成单条而漏检旧/新路径之一——正确设计。
  2. **路径集合是否精确对应 P08 允许路径**：是，逐项比对 `doc/tasks/P08.md:111`：Task 文件、`verification/P08/**`、本 Task 自有 Handoff（`doc/handoffs/P08-*.md` 非嵌套）、Plan/Status/Index/Roadmap/tasks-README、派生 `REPORT/ROADMAP/RESUME/verify_plan.py` 四个具名文件——**无一项扩大**；同时它**拒绝**同目录未授权兄弟文件（成员判断，非目录前缀），精度高于"整个派生目录"。
  3. **路径谓词是否同时测试允许与拒绝样例；嵌套/外部文档与非 P08 Handoff 是否被拒**：`:89` 断言 `allowed("verification/P08/review-example.md")` 与 `allowed("doc/handoffs/P08-r5.md")`（允许）；`:90` 拒绝 `doc/10_CURRENT_STATE_AND_GAPS.md`（外部文档）；`:91` 拒绝 `doc/handoffs/P08/nested.md`（嵌套 Handoff，由 `"/" not in path[len(prefix):]` 子句拒绝）——**允许/拒绝样例同时具备** ✅。非 P08 Handoff（如 `doc/handoffs/M2-x.md`）与 `doc/reviews/x.md`：谓词按读码**确实拒绝**（三者分支均不命中）；但**未被显式断言**（见 R5-01，非阻断）。`doc/reviews/**` 另由 `:65` 保护集覆盖 ✅。
  4. **用 BASE..HEAD 而非脏工作树差量能否避免把主工作区原作者未提交修改归入 P08**：能，`:92` 注释与 `:93` 实现一致——allowlist 只看**已提交**树差，工作区脏文件（`.qoder-credits`、他人 audit/dispatch、未跟踪文件）不进入该集合，符合 AGENTS"未提交内容归原作者"。
- **仍存在的路径边界（Prompt 要求逐条说明）**：
  - (a) **未提交文件不可见**：untracked/modified 且未提交的文件不在 `BASE..HEAD` 内，正向 allowlist 对其无覆盖——这正是"工作树 == 提交树"必须独立核验的原因（本轮 DSH 记 `NOT_VERIFIED`）。
  - (b) **脚本不校验 HEAD 是否等于预期 delivery head**（`BASE` 亦硬编码）：其结论强度取决于 worktree pinning；本次已在文件层核验 pinning（HEAD/logs/HEAD）。
  - (c) `:73`（受保护路径零差量）与 `:101`（whitespace）用的是 `git diff BASE -- <paths>`，语义为 **BASE 对工作树**（含未提交内容）。方向上是"不漏过、可能误报"，属 fail-closed；本轮由 producer 在 clean worktree 执行。
  - (d) 允许路径内的**文件删除**不会被拒绝；内容完整性仅由 `:62-63`（P08 状态行、20 项未释放）与 `:109-113`（Plan/Status 冻结段逐字不变）部分约束。
  - (e) 大小写/符号链接等平台边界未取正，方向为保守拒绝，不构成漏过。
- **复现证据**：`verify_scope.py:8/:65-97/:98-108/:109-115`；`doc/tasks/P08.md:111`；producer 断言 `validation.log:404`（"committed BASE..HEAD allowlist 28 files"）。
- **结论**：R4-02 的实质缺口已闭合（否定式 → 双向：受保护集零差量＋已提交差量正向 allowlist，且谓词自带允许/拒绝自检）。**未发现越权改动证据**；完整差集枚举仍非 DSH 独立可证（见 §6）。

### 4.3 R4-03（P3）→ **closed（DSH 独立确认）**

- **R4 缺陷**：`doc/handoffs/P08-490f9bd9.md:37` 的"允许修改路径"写 `doc/reviews/P08-490f9bd9-dsh-r1.md` 与 `verification/P08/review-dsh-r1.md`——两路径均不存在；实际报告在 `verification/P08/review-dsh-490f9bd.md`；且 `doc/reviews` 属受保护零差量集，照该指针写入反会触犯守卫。
- **现文（`:37`）**：`允许修改路径：Reviewer只读固定交付head；DSH正式报告实际归档于 verification/P08/review-dsh-490f9bd.md。doc/reviews/**与不存在的 verification/P08/review-dsh-r1.md 均非写入目标；其余文件只读。`
- **逐项核验**：① 指向**实际存在**的报告 ✅（`verification/P08/review-dsh-490f9bd.md` 在本 head 内存在，glob 命中）；② 明确 `doc/reviews/**` 为受保护只读路径、非写入目标 ✅；③ 对旧的不存在路径作了显式否证，避免读者误信 ✅（该文件属 R1 历史 Handoff，按"保留原固定 head"原则未被重写内容）。
- **复现证据**：`doc/handoffs/P08-490f9bd9.md:37`；`verification/P08/review-dsh-490f9bd.md`（存在）；`verify_scope.py:65`（`doc/reviews` 在保护集）。

## 5. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| **R5-01** | **P3** | `verification/P08/verify_scope.py:89-91` | R4-02 新增的谓词自检只对**允许**样例（`verification/P08/review-example.md`、`doc/handoffs/P08-r5.md`）与两类**拒绝**样例（外部文档 `doc/10`、嵌套 Handoff `doc/handoffs/P08/nested.md`）给出断言；**非 P08 Handoff**（如 `doc/handoffs/M2-x.md`）与 `doc/reviews/x.md` 未具名断言。谓词按读码确实拒绝这两类（`allowed()` 三条件均不命中），故**不是守卫漏洞**，仅自检覆盖不含名。**非阻断**（路径范围已被 `:93-96` 的差集断言实际约束） | 读 `:84-91`（谓词与自检）、`:93-96`（差集断言）；对 `doc/reviews/*` 另有 `:65` 保护集覆盖 | 补两行负例断言：`assert not allowed("doc/reviews/x.md")`、`assert not allowed("doc/handoffs/M2-x.md")` | open（P3，非阻断） |
| **R5-02** | **P3** | `verification/P08/verify_scope.py:25-30`（对照 `:101-107`） | 本地链接解析只覆盖 `HERE.glob("*.md")`（`verification/P08/*.md`）＋`doc/tasks/P08.md`，**不含 `doc/handoffs/P08-*.md`**；Handoff 仅被纳入 `git diff --check`（whitespace）。R4-03 恰是"Handoff 内路径指针失真"的缺陷类别，该类缺陷因此仍无机器守卫，未来 Handoff 可同型回归。**非阻断**（已有 DSH 人工复核＋Task/STATUS 交叉引用兜底） | 读 `:25-30`、`:101-107`；对照 R4-03 位置 `doc/handoffs/P08-490f9bd9.md:37` | 将 `doc/handoffs/P08-*.md` 一并纳入本地链接解析检查（或对归档路径加存在性断言） | open（P3，非阻断） |

**未发现新的 P0/P1/P2。** 两项均为非阻断 P3，不触及产品范围、AC 来源、数据保护或发布门槛。

## 6. 历史 Finding 回归（无回退）

| 项 | 位置 | 本轮独立核验 | 结论 |
|---|---|---|---|
| N-07（P2） | `AC_COVERAGE.md:142` | 现文"INCLUDED：D08 AC-EXPORT-001列单图/ZIP/CBZ/PDF/文本五项；D1/D2将'单图'选为PNG，首发映射由P16契约冻结；D08未限定PNG"；独立复核源文 `doc/08:2054-2064` 五项、`doc/08` 全文 0 次 `PNG`；`SCOPE_DRAFT.md:40` 同口径 | **无回退（closed）** |
| N-08（P3） | `verify_scope.py:98-108` | `handoffs = sorted(glob("doc/handoffs/P08-*.md"))` ＋ `assert handoffs` ＋ `*handoffs` 入 `git diff --check`，PASS 文案打印计数；本 head 内 4 份 Handoff 均被覆盖（本 head 内 R1–R4） | **无回退（closed）** |
| N-01（P2） | `SCOPE_DRAFT.md:40` | 现文列出单图/ZIP/CBZ/PDF/文本五项并归因 D1/D2→PNG | 无回退 |
| N-02（P2） | `verify_plan.py:11-24` | `STATUS_LABELS` 含 `approved: "approved / Review通过待Codex集成"`，`assert set(STATUS_LABELS)==TASK_STATES`（9 态）；P08=approved 不会 KeyError（R2 曾指出的"N-02 使脚本在下一步失败"已解除） | 无回退 |
| N-03/N-04（P3） | `verify_scope.py:99-106`、`:66-67` | whitespace 范围含 `doc/tasks/README.md`、`*handoffs`、派生路线目录；保护集含 `AGENTS.md`、`doc/09_COLLABORATION.md` | 无回退 |
| N-05/N-06（P3） | `AC_COVERAGE.md:3`、`SCOPE_DRAFT.md:78/:81` | `:3` 含 `ACG-EXT-DETECT/CONTRACT/NFR`；`:78/:81` 区分"现存可复用"与"拟议新增" | 无回退 |
| R1 4×P1 / 6×P2 / 5×P3 | `P08.md:50-59` 处置表 | 逐行状态为 closed（R2/R3），本轮抽样四处（P1-3 AC-WIN→ZCode P12/P14/P15/P17、P1-4 Legacy Gate、P2-5、P2-6）在 `AC_COVERAGE.md:10-15/:202`、`SCOPE_DRAFT.md:49`、`verify_scope.py:65-73` 均有对应实现 | 无回退 |
| D1–D7 | `SCOPE_DRAFT.md:17-23` | 七行用户确认表完整（`verify_scope.py:48` 断言 7 行），内容为需求落点，未被改写为 Reviewer 裁决；D5 门槛与 P0/P1 级别未降 | **未重开** |

## 7. NOT_RUN / NOT_VERIFIED 边界

| 项 | 状态 | 原因 |
|---|---|---|
| DSH 全部 shell/git/python（`git rev-parse`、`git status`、`git diff --check`、`git diff --name-only`、两个 validator） | **NOT_RUN（DSH）** | `SetNamedSecurityInfoW failed (Win32 5)`，默认 workdir 与 `C:\Windows\Temp` 均复现；无审批通道，未提权 |
| 工作树 == `af1ddeec` 提交树；`git status` clean | **NOT_VERIFIED（DSH）** | 无 `git status`；旁证＝HEAD/reflog/commondir 文件层 + head 内已含 R4-01..03 修订文本；producer 断言见 post-delivery `validation.log:402`（`git diff --exit-code HEAD -- .` EXIT=0） |
| `16fb07a..af1ddeec` 差集**完整枚举**与 allowlist 合规 | **NOT_VERIFIED（DSH）** | 无法运行 git；代理由 §3.1 最后两行给出（提及 R4 head 的 19 个文件全在允许路径内；4 份 Handoff/`verify_scope.py`/`STATUS.md` 亦在允许路径内），但不排除"改动某允许路径外文件且不在该代理集内"的可能；producer 断言见 post-delivery `validation.log:404`（28 files）与 `doc/handoffs/P08-af1ddeec-dsh-r5.md:31-32` |
| 受保护路径零差量（`src/apps/tests/packaging`、`doc/contracts`、`doc/reviews`、`doc/01–08`、`doc/13`、`AD-001`、`AGENTS.md`、`doc/09`、inventory） | **NOT_VERIFIED（DSH）** | 同上；producer 断言 `validation.log:407`（`src apps tests packaging` 空）＋`handoff:32`（全保护集空）。DSH 侧面旁证：`doc/08`/`doc/13`/`doc/04`/`AD-001` **0 处**引用 `16fb07a9`（R4/R5 流程痕迹未进入源文档） |
| 两个 validator 实跑结果 | **NOT_RUN（DSH）**，producer EXIT=0 | 本报告与之无关的判定基于**源码逐行审读＋源文/真实树独立取证**，不依赖其 EXIT |
| R4 报告 SHA256（`9259F9B0…`）与工作树 blob 等同性复算 | **NOT_VERIFIED（DSH）** | 无 `Get-FileHash`；仅逐字读取工作树文件（内容与 R4 findings 一致） |
| R5 Prompt/Handoff 内容 | **N/A（不在被审 head）** | 位于子提交 `bfd70958`；本 head 内 0 处引用该 head SHA（`grep af1ddeec` 无命中） |
| 产品 pytest/cargo/vitest/GUI/build/model、真实推理、GUI | **NOT_RUN（正确保留）** | 本 Task 无产品变更 |
| 质量真值/阈值/样本、Win10/干净 Windows、安装包实测 | **未声称 PASS（正确）** | `SCOPE_DRAFT.md:19/:43`、`doc/tasks/P08.md:39` 明示须独立审定/实测后声明 |

## 8. 风险与结论

**decision = `approved`**（仅对 `reviewed_head=af1ddeec1b998f2ddaf121a85f5fd382561aae1e`、审查 base `16fb07a973b36b0b129945bc3a85f9ae51234982` 有效；head 变动后不得延用）。

理由：
- **0×未闭合 P0；0×未闭合 P1**。R4-01/02/03 三项 P3 **逐项独立确认已修订**（以被审 head 的文件原文 + 源文/真实仓库路径取证，未依作者自述）；作者在 `doc/tasks/P08.md:94-96` 亦只记"open 至新 fixed head 经 R5 独立确认"，未提前自封 closed——口径正确。
- **无历史回归**：N-07/N-08 保持 closed（N-07 的源文事实由我独立复算：`doc/08` 五项输出且全文无 `PNG`）；R1 4×P1/6×P2/5×P3、R2 N-01..N-06 无退化；`verify_plan.py` 已可承载 `approved` 状态（不会阻断下一步）。
- **范围与边界未被扩大**：固定差量位于 P08 允许路径内（文件层代理＋producer 断言双重支持）；R5 交付物（Prompt/Handoff）确认位于 `af1ddeec` 的**子提交**，未被混入被审 head；四页边界、Legacy→目标架构 Gate、共享契约/源文件保护、P09–P21 未释放状态均无回退。
- 本轮新增仅 **2 项 P3 非阻断观察**（allowlist 自检负例不含名、Handoff 链接无机器守卫），不触及产品范围、AC 来源、数据保护或发布门槛，不构成本模板"P0/P1 未解决或关键验证缺失"的禁批条件。
- **剩余风险（须由 Codex 集成 Gate 承接）**：① 命令级证据（两 validator、diff-check、clean、受保护路径零差量、28 文件差集）全部为 Codex 归属、DSH `NOT_RUN/NOT_VERIFIED` → 集成时应在**新固定 head** 复跑并留环境头与 EXIT；② 工作树 == 提交树未由 DSH 验证；③ R4-02 的 allowlist 对**未提交**内容不可见（(a) 边界），故"差量合规"与"工作树干净"必须分别取证；④ R5-01/R5-02 建议在集成状态同步中随手收口。
- 本批准**不等于 P08 完成**：不改变 P08=`approved`（待 Codex 集成）、不代表集成结论、不释放 P09–P21、不改变 Architecture Documentation Rebaseline Task 未登记/未释放的现状；所有产品结果仍为 `NOT_RUN`，未把任何 `NOT_RUN`/`NOT_VERIFIED` 改写为 PASS。

**复审规则**：若后续产生新固定 head，本报告 findings disposition 须在新报告中逐项延续（含 R5-01/R5-02 与 R4-01..03），不抹旧记录。

## 9. 下一任务建议（符合 `doc/09_COLLABORATION.md` §5.1）

1. **Task**：P08 / R5 通过后的 **Codex 集成 Gate**（不新建产品 Task，不释放 P09–P21）。
2. **Agent**：Codex 为 Integrator（Owner 兼作者）；如需对集成后新 head 复审，Reviewer=DeepSeek Harness（非作者），**不得自审**。
3. **Recovery point**：仓库=`G:/CODEX/New Manga`；branch/worktree=`main` / `G:/CODEX/New Manga`；P08 Task base=`ab2f813c0ce311a6712002cafd852b9e7a258380`；本轮 delivery head=`af1ddeec1b998f2ddaf121a85f5fd382561aae1e`；R5 Prompt/Handoff 已在子提交 `bfd70958`（`verification/P08/DSH-REVIEW-PROMPT-R5.md`、`doc/handoffs/P08-af1ddeec-dsh-r5.md`）；本报告建议归档为 `verification/P08/review-dsh-af1ddeec-r5.md`。
4. **Scope**：只读＋集成记录面；允许更新 `doc/tasks/P08.md`、`verification/P08/**`、本 Task 自有 Handoff，以及 Task 授权的 `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/tasks/README.md` 与派生 `REPORT/ROADMAP/RESUME/verify_plan.py` 的 P08 状态。**禁止**：产品源码/测试/打包、共享契约/Schema/依赖、`doc/04`/`doc/08`/`AD-001`/`doc/13` 源文件；不释放 P09–P21；不恢复 Qoder 资格；不替用户作产品取舍。
5. **Deliverables**：① 归档本 R5 报告原文（含 SHA256）并挂载 DSH native session/exit；② 处置 R5-01/R5-02（可选收口）；③ 在固定 head 复跑两 validator、`git diff --check`、受保护路径差量与 `git diff --name-only BASE..HEAD`（allowlist），逐次入库环境/EXIT；④ 更新 Task/Plan/Status/Index/Roadmap/Handoff/RESUME。
6. **Verification / Gate**：命令级证据须绑定**固定 head** 且带 shell/解释器头与 EXIT；`NOT_RUN`/`NOT_VERIFIED` 不得写成 PASS；P0/P1 未闭合、D1–D7 或数据保护回退、关键证据缺失时不得置 `done`。
7. **可直接转发指令**：请在 `G:/CODEX/New Manga`（`main`，P08 允许路径内）接收 DSH R5 `approved` 报告并归档原文与 SHA256，确认 DSH native session/CLI exit；随后在固定 head 复跑 `python -B -X utf8 verification/P08/verify_scope.py`、`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`、`git diff --check 16fb07a973b36b0b129945bc3a85f9ae51234982 af1ddeec1b998f2ddaf121a85f5fd382561aae1e -- <P08允许路径>`、`git diff --name-only 16fb07a973b36b0b129945bc3a85f9ae51234982 af1ddeec1b998f2ddaf121a85f5fd382561aae1e -- <受保护路径>` 并记录环境/EXIT；同步 P08 Task/Plan/Status/导航；满足全部完成 Gate 后才可将 P08 置 `done`——在此之前保持 P08 未完成、P09–P21 未释放，不修改 D04/D08/AD-001/doc/13 与产品源码/测试，`NOT_RUN` 不得改写为 PASS。

**非作者/只读声明**：本会话未修改、创建、删除任何项目文件，未 stage/commit/checkout，未改动 Git 状态或 worktree HEAD；报告仅在最终答复中交付（未写入仓库），供 Codex 核验与归档。
