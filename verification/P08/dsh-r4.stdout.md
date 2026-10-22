# P08 DSH 正式 Review（R4）

---
task_id: P08
reviewer: DeepSeek Harness（非作者；作者/Integrator=Codex）
author: Codex
base_commit: ab2f813c0ce311a6712002cafd852b9e7a258380
reviewed_head: 16fb07a973b36b0b129945bc3a85f9ae51234982
decision: approved
---

## 1. 范围与依据

**受审交付**：`ab2f813c0ce311a6712002cafd852b9e7a258380..16fb07a973b36b0b129945bc3a85f9ae51234982`（完整 P08 文档交付）。

**审查 worktree**：`G:/CODEX/New Manga.worktrees/P08-dsh-review-16fb07a9-r4`；`.git` 文件 = `gitdir: G:/CODEX/New Manga/.git/worktrees/P08-dsh-review-16fb07a9-r4`；`commondir` = `../..` → `G:/CODEX/New Manga/.git`；`HEAD` 文件 = `16fb07a973b36b0b129945bc3a85f9ae51234982`（裸 SHA，即 detached）；该 worktree `logs/HEAD` 仅 1 行且为该 head，自创建起未被推进。

**先读文件**：`AGENTS.md`、`doc/09_COLLABORATION.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P08.md`、`verification/P08/{RESUME.md,AC_COVERAGE.md,SCOPE_DRAFT.md,verify_scope.py,validation.log,DSH-REVIEW-PROMPT.md}`、R1/R2/R3 正式报告（`review-dsh-490f9bd.md`、`review-dsh-31c2638.md`、`review-dsh-1ad05d99-r3.md`）、`doc/handoffs/P08-*.md`；随后核实 `doc/04_USER_FLOW.md`、`doc/08_ACCEPTANCE_CRITERIA.md`、`doc/13_ACCEPTANCE_TRACEABILITY.md`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/tasks/README.md`、`verification/PROJECT-ROADMAP-20261008/{verify_plan.py,ROADMAP.md,RESUME.md,REPORT.md}`、`doc/templates/REVIEW.md`。

**差量定位方法（因 DSH shell 不可用，改用 Git 文件层 + 跨轮同树内容比对）**：读主仓 `G:/CODEX/New Manga/.git/logs/HEAD` 得提交链（`:944`–`:946`）：`e56ac2c`(prepare third DSH review) → `1d6cfa27`(mark third DSH review in progress) → **`16fb07a9`「docs(P08): record R3 review and fixes」** → `1ec14aa2`(prepare R4 review handoff)。据此：本 head 即 **R3 结果记录 + N-07/N-08 修订提交**；R4 的 Prompt/Handoff/固定 head 验证条目位于其**直接子提交** `1ec14aa2`，与 `doc/09_COLLABORATION.md:90`（"Handoff 在交付 head 之后以文档提交追加；避免要求文件包含自己的 commit hash"）及 R3 先例（`review-dsh-1ad05d99-r3.md:20`）**一致，不构成缺陷**。

**未使用聊天记录作为产品事实。D1–D7 未重开、未重新解释为 Reviewer 裁决**（受审文件与 R3/R4 Prompt 均明确禁止重开：`DSH-REVIEW-PROMPT-R3.md:7`、`review-dsh-1ad05d99-r3.md:23`）。

**只读声明**：本会话未修改、创建或删除任何项目文件，未 stage/commit/checkout，未改动 Git 状态或 worktree HEAD。唯一命令尝试为 `git rev-parse HEAD`、`git status --porcelain=v1 --branch`（含一次复现），均在沙箱 ACL 授予阶段失败，**未提权**（无审批通道）。

## 2. Architecture 面结论

产品实现面为 `N/A`（文档冻结型 Task，无产品代码变更）。在记录范围内**未发现架构分层、冻结契约、共享 Schema、依赖或数据保护边界问题**（`executed` = 文件层核对；DSH 未能运行 git/python）：

- **四页边界未扩**：`AC_COVERAGE.md:7-9` 维持"一级页面只有四个"为 P0，`SCOPE_DRAFT.md:31` 明示"不扩一级页面"；AD-001 的四页/React+Tauri+Python Core 目标架构未被 P08 改写。
- **Legacy → 目标架构口径正确且未被绕过**：`SCOPE_DRAFT.md:49` 声明 D07/D08 仍是 Legacy 生产基线，`AC-PKG-001/003`、`§6 PySide6`、`§69 ViewModel` 属 stack-specific，须由**单独授权、正式释放**的 Architecture Documentation Rebaseline Task 产出目标等价表述；在此之前只记 `NOT_RUN`、不复用 PySide6/QML 证据（`AC_COVERAGE.md:175-179`、`:189-191`、`:202`）。该 Task 未登记、未释放，P09/P18/P20 对应 Gate 在 Plan 中保持阻断（`REBASELINE_PLAN.md:40/:49/:51`、`SCOPE_DRAFT.md:71`）——**P08 未越权创建或释放它**。
- **数据保护语义无回退**：源文件 hash 零变化、人工修改/Lock/current/pinned 保护在 `SCOPE_DRAFT.md:62` 列为不可降级门槛，`AC_COVERAGE.md` 对应 `AC-IMPORT-002`、`AC-TRANS-002/004`、`AC-LOCK-001..005`、`AC-REV-001..004`、`AC-CLEAN-001/002`、`AC-CACHE-001/002` 全部 `INCLUDED` 且 `NOT_RUN`；全库备份（DB＋Managed Copy、失败回滚、DB-only 不可替代）见 `SCOPE_DRAFT.md:20/:42` 与 `AC-BACKUP-001..004`。
- **受保护路径零差量**：`verify_scope.py:65-73` 的保护集包含 `src/apps/tests/packaging`、`doc/contracts`、`doc/reviews`、`AGENTS.md`、`doc/09`、`doc/01–08`、`doc/13`、`AD-001`、`task-inventory.csv`；其 EXIT=0 **归 Codex**（DSH `NOT_RUN`）。我以文件层交叉印证：R3 报告所引 `doc/08:2054-2064`、`doc/13:242`、`doc/04:1446-1472` 原文与本 head 逐字一致，未见冻结源文档漂移迹象。

## 3. Verification 面结论

### 3.1 环境与元数据核验（DSH 实际执行）

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| HEAD == reviewed_head | 读 `.git/worktrees/P08-dsh-review-16fb07a9-r4/HEAD` | DSH read；无 shell | **PASS**（严格相等，detached） | `HEAD:1` = `16fb07a9…` |
| worktree 自创建起未推进 | 读该 worktree `logs/HEAD` | 同上 | **PASS** | 仅 1 行：`0000…0000 → 16fb07a9… peakwheat-pixel 1791471617 +0800`；无 checkout/commit/rebase |
| worktree 反向绑定 | 读 `.git` 文件 | 同上 | **PASS** | `gitdir: G:/CODEX/New Manga/.git/worktrees/P08-dsh-review-16fb07a9-r4` |
| common-dir | 读 `commondir` | 同上 | **PASS** | `../..` → `G:/CODEX/New Manga/.git` |
| 交付 head 身份/链位 | 读主仓 `.git/logs/HEAD:945-946` | 同上 | **PASS** | `1d6cfa27 → 16fb07a9「record R3 review and fixes」→ 1ec14aa2「prepare R4 review handoff」` |
| `git rev-parse` / `git status` / `git diff --check` / 两个 python | `git rev-parse HEAD`；`git status --porcelain=v1 --branch`；R4 Prompt 所列命令 | DSH pwsh | **NOT_RUN（DSH）** | `SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\P08-dsh-review-16fb07a9-r4)`；换 `workdir` 与重试均复现；未提权 |
| 工作树 == 被审提交树（clean） | 无 `git status` | — | **NOT_VERIFIED（DSH）** | 旁证：HEAD/reflog 文件层 + 树内已含 R4 修订；**Codex** 断言见子提交 `validation.log:340`（`git diff --exit-code HEAD -- .` EXIT=0） |
| 差量 allowlist 合规、受保护路径零差量 | — | — | **NOT_VERIFIED（DSH）** | 仅能引用 producer 断言：`validation.log:339`（EXIT=0、空）、`doc/handoffs/P08-16fb07a9-dsh-r4.md:25` |

### 3.2 内容级核验（DSH read/grep 实际执行）

| 场景 | 步骤 | 结果 | 证据 |
|---|---|---|---|
| AC 逐项对应 D08 | grep `^## AC-[A-Z0-9-]+ \[P[0-2]\]`（doc/08） vs grep `^\| AC-[A-Z0-9-]+ \|`（AC_COVERAGE） | **PASS**：两侧均 **193** 条，ID 与顺序逐项一致（NAV→WIN→…→DOC→EXT-*）；另 `D08-AC-SMOKE` 1 行 + `D08-GATE-68..79` 12 行 | doc/08:215–3223；`AC_COVERAGE.md:7-199`、`:200`、`:201-212` |
| D08 AC-EXPORT-001 原文 | read `doc/08:2052-2064`；grep `PNG` 全文 | **PASS**：`## AC-EXPORT-001 [P0] 格式` 恰列 **单图/ZIP/CBZ/PDF/文本** 五项（`:2059-2063`）；**全文 0 次 "PNG"** | `doc/08:2052-2064`；grep `PNG` → No matches |
| N-07 修订实际文本 | read `AC_COVERAGE.md:142` | **PASS**：决策列现为"D08 AC-EXPORT-001列单图/ZIP/CBZ/PDF/文本五项；D1/D2将"单图"选为PNG，首发映射由P16契约冻结；**D08未限定PNG**"；建议切片列把 PNG 映射归因 D1/D2 + P16 | `AC_COVERAGE.md:142` |
| "只写/仅写"式来源收缩残留 | grep `单图\|PNG\|只写` 于 `verification/P08/**` | **PASS**：唯一"只写"命中为 `AC_COVERAGE.md:81` 的 `AC-RFULL-002 [P0] 只写目标 Region`（语义无关）；其余命中均为正确的五项/PNG 归因表述 | grep 结果 24 匹配 |
| N-08 动态 Handoff 范围 | read `verify_scope.py:74-84`；glob `doc/handoffs/P08-*` | **PASS**：`handoffs = sorted(...glob("P08-*.md"))` + `assert handoffs`，`*handoffs` 传入 `git diff --check`；PASS 文案打印 `({len(handoffs)} Handoffs)`；head 内 3 件 = R1 `P08-490f9bd9.md`、R2 `P08-31c26389-dsh-r2.md`、R3 `P08-1ad05d99-dsh-r3.md` | `verify_scope.py:74-84`；glob 3 件 |
| 新增 Handoff 的动态行为 | 读主仓 `validation.log:346` | **PASS（旁证）**：R4 Handoff 落地后为"4 P08 Handoffs dynamically in whitespace scope"，证明 glob 对新增 Handoff 生效 | 主仓（子提交）`validation.log:346` |
| 12 条 Legacy PASS 口径 | grep `f9e5977`（9 命中）+ read `doc/13:45-48/50/64-65/75-76/197-199` + `AC_COVERAGE.md:3` | **PASS**：9 条绑历史 Review `f9e5977` + AC-DOC-001..003 绑 TASK-001/002 审计证据；`doc/13:150` AC-EXPORT-001 = `NOT_RUN/无应用测试`；`AC_COVERAGE.md:3` 明示这 12 条历史 PASS 不被本表覆盖、AC-DOC 历史 PASS 不自动关闭新架构 Gate | 同上 |
| §74/75/79 advisory | read `doc/13:242`；`AC_COVERAGE.md:3/:207/:208/:212` | **PASS**：§74/75 由 doc/13 明确"建议性、不作为独立验收项"；§79 标题即"下一阶段建议"；本表 GATE-74/75/79 标 `ADVISORY ONLY`、无独立 PASS | 同上 |
| N-02 协议状态集（复核无退化） | read `09_COLLABORATION.md:66-76`；`verify_scope.py:9-10,34-37`；`verify_plan.py:11-24,62,78` | **PASS**：协议 9 态；两脚本 `TASK_STATES` 同为 9 态，`assert set(STATUS_LABELS)==TASK_STATES`，`p08_label = STATUS_LABELS[state]`（`approved` 已可承载） | 同上 |
| 产品 pytest/cargo/vitest/GUI/build/model | 未运行 | **NOT_RUN（正确保留）** | `doc/tasks/P08.md:113`、`RESUME.md:21`、`validation.log:342` 等 |

**Verification 面结论**：本 head 的**内容级**事实（AC 覆盖完整性、N-07/N-08 修订文本、12 条 Legacy 口径、§74/75/79 advisory、协议状态集、D1–D7 七项）已由 DSH 文件层独立取证，未发现与源文冲突；**命令级**证据（两 validator、`git diff --check`、受保护路径差量、clean 判定）全部为 Codex 归属，DSH 侧 `NOT_RUN`，本报告**不将其写成 DSH PASS**。

## 4. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| **N-07** | P2 | `verification/P08/AC_COVERAGE.md:142` | R3：状态列称"D08原文只写单图/ZIP"，把 P0 AC 来源窄化为 2 项 | 现文已列五项并归因 D1/D2+P16，且明写"D08未限定PNG"；`doc/08:2054-2064` 五项、全文 0 次 PNG；`SCOPE_DRAFT.md:40` 同口径 | — | **closed**（本轮独立确认，非依作者自述） |
| **N-08** | P3 | `verification/P08/verify_scope.py:74-84` | R3：Handoff whitespace 范围硬编码两项，head 之后新增 Handoff 不受检 | 现为 glob `doc/handoffs/P08-*.md` + `*handoffs` 入 `git diff --check`，PASS 文案例印计数；head 内 R1/R2/R3 三件全覆盖；主仓新增第 4 件被自动纳入 | 无阻断；边界见 R4-02 备注（glob 非递归、需 `P08-` 前缀、untracked 不入 diff） | **closed**（非阻断边界保留） |
| R1 P1-1 | P1 | `validation.log` / `P08.md` 测试表 | 证据未绑定固定 head、缺 shell/解释器头 | 现 `validation.log` 按轮次绑定 `31c26389`→`1ad05d99`（R2/R3 条目含环境与 EXIT）；R3 `:78` 判 closed，本轮 `:109-111` per-round 行保留、子提交追加 R4 行 | — | **closed，无回退** |
| R1 P1-2 | P1 | `AC_COVERAGE.md:3` | AC 真值/责任路由与 doc/13 冲突、未对账 | `AC_COVERAGE.md:3` 四段对账齐全（To-Be NOT_RUN、未编号 ACG 归 doc/13、§74/75/79 advisory、AC-DOC §66 Gate） | — | **closed，无回退** |
| R1 P1-3 | P1 | `AC_COVERAGE.md:10-15` | 6 条 AC-WIN 无实现落点（原写 P20 packaging） | 现 6 行实现切片均指 ZCode `P12/P14/P15/P17` 按窗口归属页，P20 仅平台/安装包验证 | — | **closed，无回退** |
| R1 P1-4 | P1 | `SCOPE_DRAFT.md:49`、`AC_COVERAGE.md:175-179/:202` | Legacy baseline 与 D08 新架构验收冲突未处置 | 现声明 D5 门槛/P0/P1 级不变，stack-specific 须经 Architecture Documentation Rebaseline Task 等价映射，之前只记 `NOT_RUN` | — | **closed，无回退** |
| R1 P2-1..P2-4、P3-1..P3-5 | P2/P3 | STATUS/Plan/Index/Roadmap/AC_COVERAGE/SCOPE_DRAFT | 见 R1 报告 `:145-195` | R2 `:82-85/:97-101` 逐项 closed；本轮抽验 STATUS/Plan/Index/Roadmap 的 P08 状态一致（`changes_requested`、20 未释放） | 遗留一处措辞见 **R4-01** | **closed（一处残句另记 R4-01）** |
| R1 P2-5 → N-01 | P2 | `SCOPE_DRAFT.md:40` | 来源列"仅写单图/ZIP"与源文冲突 | 现文"D04 §37与D08 AC-EXPORT-001列出的单图、ZIP、CBZ、PDF、文本全部覆盖；用户D1/D2将单图映射为PNG" | — | **closed（R3 经 N-01），无回退** |
| R1 P2-6 → N-02/03/04 | P2 | `verify_scope.py` | 零差量/whitespace 覆盖不足、协议状态集过窄 | N-02 见 §3.2；N-03 现覆盖 `doc/tasks/README.md`、`*handoffs`、派生路线目录；N-04 现含 `AGENTS.md`、`doc/09_COLLABORATION.md`（`:66-67`） | — | **closed，无回退** |
| N-05 / N-06 | P3 | `AC_COVERAGE.md:3`、`SCOPE_DRAFT.md:78/81` | 未编号 ACG 枚举不全；现存目录误标"拟议" | 现 `:3` 含 `ACG-EXT-DETECT/CONTRACT/NFR`；`:78/:81` 区分"现存可复用"与"拟议新增" | — | **closed，无回退** |
| **R4-01** | **P3** | `doc/STATUS.md:10` | 同一可变段内自相矛盾：`:10` 称"当前21个规划节点…状态为 `proposed / 未释放`"，而 `:3`/`:20` 称 `changes_requested 1、proposed / 未释放20`。STATUS 是运行状态事实源（`00_INDEX.md:81` 口径），恢复中的 Agent 可能误判 21 项全未释放；R1 P2-1 曾以 `:10` 为矛盾一侧（`review-dsh-490f9bd.md:147`），R2 只改 `:20` 未清 `:10`。**非阻断**（权威计数 `:3`/`:20` 正确，无产品/数据影响） | `doc/STATUS.md:3/:10/:20`；`REBASELINE_PLAN.md:28/:39`；`verify_scope.py:85-89` 证明 `:10` 位于可变段（冻结标记 `## 2026-10-08 完成：` 在 `:22`）；主仓 `STATUS.md:10` 仍为原文 | 限定 `:10` 为"仅统一编号；P08 已登记正式 Task，其状态以本节开头为准"，或改为"20 项 proposed / 未释放 + P08=changes_requested" | open（P3，建议集成状态同步时清） |
| **R4-02** | **P3** | `verification/P08/verify_scope.py:65-84` | 范围守卫是**否定式**（受保护集零差量 + 枚举集 whitespace），**没有正向断言"差量 ⊆ P08 允许路径"**。`doc/10`、`doc/11`、`doc/templates/**`、非 P08 的 `doc/handoffs/*`、其他 `verification/*` 目录既不在保护集也不在 whitespace 集，若被改动不会有任何断言触发；差量完整性只能依赖 Codex 的 `git diff --name-only` 断言（`validation.log:339`、`handoff:25`），DSH 无法复跑。**非阻断，且未发现任何越权改动证据** | `verify_scope.py:65-73`（否定式）vs `:74-84`（枚举 whitespace）；`doc/tasks/P08.md:97-103`（允许/禁止范围）；DSH `NOT_RUN` 边界见 §3.1 | 增补正向 allowlist 断言（`git diff --name-only BASE` 结果 ⊆ 允许集），或在脚本/文档中显式登记该边界 | open（P3，建议下一轮或集成时收口） |
| **R4-03** | **P3** | `doc/handoffs/P08-490f9bd9.md:37` | R1 Handoff 的"允许修改路径"写 `doc/reviews/P08-490f9bd9-dsh-r1.md` 及 `verification/P08/review-dsh-r1.md`——**两路径均不存在**；R1 报告实际归档于 `verification/P08/review-dsh-490f9bd.md`。且 `doc/reviews` 属受保护零差量集（`verify_scope.py:65`），照该指针写入反会触犯 P08 守卫。影响：轮次证据指针失真（可追溯性）。**非阻断**（报告本体存在且被 Task/STATUS 正确引用） | glob `doc/reviews/P08*` → 无；`verification/P08/review-dsh-r1.md` → 无；`RESUME.md:9`、`validation.log:95` 指向真实路径 | 更正该指针为真实归档路径，或标注"已被 `verification/P08/review-dsh-490f9bd.md` 取代" | open（P3，历史残项，可随手修） |

### 4.5 复核后判定为**非缺陷**的项（已排除，说明理由免误判）

1. **被审 head 内 P08.md/RESUME.md/validation.log 处于"上一轮记录态"、head 本身未被任何受审文件记录**（如 `P08.md:17` 仍 `reviewed_head: 1ad05d99`、`RESUME.md:7/:27` 称修订"尚未提交"、`:19` 命令 3 绑定 `31c26389`）：这是**协议已解释的 fix 提交形态**——`09_COLLABORATION.md:90` 要求 Handoff 于交付 head 之后追加，R3 先例 `review-dsh-1ad05d99-r3.md:20/:34` 已判定同形态不构成缺陷。子提交 `1ec14aa2` 已补齐 R4 Prompt/Handoff、`P08.md:17` 的 `reviewed_head: 16fb07a9`、`validation.log:333-350` 固定 head 验证条目与 `RESUME.md` 全量更新（主仓可读）。
2. **任务状态在被审 head 为 `changes_requested`、子提交翻为 `in_review`**：符合 `09_COLLABORATION.md:73`（"修订后回到 in_review"）的过渡次序，与 R3 轮同构。
3. **`P08.md:109/:111` 的 validator 行绑定 `31c26389`（R2 head）**：该表按轮次逐条入库（R4 行由 `:113` 补充），每行绑定其当轮 head，非混用。
4. **`AC_COVERAGE.md:207/:208/:212` 的 advisory 行结果列写 `NOT_RUN`**：`verify_scope.py:23` 要求全表行以 `| NOT_RUN |` 结尾；决策列已明写"不是独立 Gate 或单独 PASS"，属保守占位而非造 PASS。
5. **`STATUS.md:234/:388` 的 "Current Active Task = 无 Active"**：位于 `## 2026-10-08 完成：`（`:22`）之后的**冻结历史段**（`verify_scope.py:85-89` 断言其逐字不变），且限定语为"产品 Task"，不属本交付缺陷。
6. **`verify_plan.py` 的 `assert ... ⊆ TASK_STATES` 与 `verify_scope.py:63` 的 20 项未释放计数**：grep 独立复算 `REBASELINE_PLAN.md` 中 `| Pnn | proposed / 未释放 |` = **20** 行（P01–P07、P09–P21），`| P08 | changes_requested |` 在第 39 行，断言成立。

## 5. NOT_RUN / NOT_VERIFIED 边界

| 项 | 状态 | 原因 |
|---|---|---|
| DSH `pwsh` 全部 shell/git/python 检查（含 `git rev-parse`、`git status`、`git diff --check`、`verify_scope.py`、`verify_plan.py`） | **NOT_RUN（DSH）** | `SetNamedSecurityInfoW failed (Win32 5): grantWrite(<worktree>)`，重试与换 workdir 均复现；**未提权** |
| 工作树内容 == `16fb07a9` 提交树；`git status` clean | **NOT_VERIFIED（DSH）** | 无 `git status`；以 `.git` HEAD/reflog/commondir 文件层 + 树内含 R4 修订为旁证；Codex 断言见子提交 `validation.log:340` |
| `ab2f813..16fb07a9` 全量差集、allowlist 合规、受保护路径零差量 | **NOT_VERIFIED（DSH）** | 仅引用 producer 断言（`validation.log:338-339`、`handoff:24-25`）；其 EXIT=0 **归 Codex** |
| 两 validator 实跑结果 | **NOT_RUN（DSH）**，producer EXIT=0 | 本报告的 closed 判定基于**源码逐行审读 + 源文/真实树独立取证**，不依赖其 EXIT |
| 所有 R2/R3/R4 报告与 Handoff 的 blob 等同性、报告 SHA256 复算 | **NOT_VERIFIED（DSH）** | 无 `git show`/`Get-FileHash`；仅逐字读取工作树文件 |
| 产品 pytest/cargo/vitest/GUI/build/model、真实推理、GUI | **NOT_RUN（正确保留）** | 本 Task 无产品变更；交付各处亦明确记为 NOT_RUN |
| 质量真值/阈值/样本、Win10/干净 Windows、安装包实测 | **未声称 PASS（正确）** | `SCOPE_DRAFT.md:65` 明示数值须在 P18 资格方案独立审定后冻结 |

## 6. 结论与复审

**decision = `approved`**（仅对 `reviewed_head=16fb07a973b36b0b129945bc3a85f9ae51234982`、base `ab2f813c0ce311a6712002cafd852b9e7a258380` 有效；head 变动后不得延用）。

理由：
- **0×未闭合 P0；0×未闭合 P1**。R3 的 N-07（P2）与 N-08（P3）本轮**逐项独立确认 closed**（以受审 head 文件原文 + 源文 `doc/08`/`doc/13`/SCOPE_DRAFT 交叉复核，未依作者自述）；R1 的 4×P1、6×P2、5×P3 及 R2 的 N-01..N-06（含 N-02/N-03/N-04 涉及的两脚本）**均无退化**。
- 交付的实质内容（193 条 AC 与 D08 逐项同序对应、D1–D7 未扩写、D5 门槛未降、12 条 Legacy PASS 口径正确、§74/75/79 advisory、全库备份与源/人工/Lock/current/pinned 保护、Architecture Documentation Rebaseline 前置 Gate 保持阻断）在记录范围内全部成立，**未发现新的 P0/P1/P2**。
- 本轮新增 3 项均为 **P3 非阻断**（STATUS 一处残句、守卫的否定式设计边界、R1 Handoff 历史指针），不触及产品范围、AC 来源、数据保护或发布门槛，故不构成本模板"P0/P1 未解决或关键验证缺失"的禁批条件。
- **剩余风险（须由 Codex 集成 Gate 承接）**：① 命令级证据（两 validator、diff-check、clean、受保护路径零差量）为 Codex 归属、DSH `NOT_RUN` → 集成时应在固定 head 复跑并留 EXIT/环境头；② 工作树==提交树未由 DSH 验证；③ R4-02 的"无正向 allowlist"意味着差量完整性依赖 Codex 断言；④ `R4-01/02/03` 建议在集成状态同步中随手收口。
- 本批准**不等于 P08 完成**：不改变 P08=`changes_requested`、不代表集成结论、不释放 P09–P20、不改变 Architecture Documentation Rebaseline Task 未登记/未释放的现状；所有产品结果仍为 `NOT_RUN`，未把任何 `NOT_RUN`/`NOT_VERIFIED` 改写为 PASS。

**复审规则**：若后续产生新固定 head，本报告 findings disposition 须在新报告中逐项延续（含 R4-01..R4-03），不抹旧记录。

## 7. 下一任务建议（可直接转发）

- **Task**：P08 / R4 通过后的 Codex 集成 Gate（不新建产品 Task，不释放 P09–P20）。
- **Agent / Reviewer**：Codex 为 Integrator；如需对集成后新 head 复审，Reviewer=DeepSeek Harness（非作者），不得由 Codex 自审。
- **Recovery point**：仓库=`G:/CODEX/New Manga`；branch/worktree=`main` / `G:/CODEX/New Manga`；base=`ab2f813c0ce311a6712002cafd852b9e7a258380`；本 Review 针对的 delivery head=`16fb07a973b36b0b129945bc3a85f9ae51234982`；R4 Prompt/Handoff 已在子提交 `1ec14aa2`（`verification/P08/DSH-REVIEW-PROMPT-R4.md`、`doc/handoffs/P08-16fb07a9-dsh-r4.md`）。
- **Scope**：只读+集成记录面；允许更新 `doc/tasks/P08.md`、`verification/P08/**`、本 Task 自有 Handoff 与授权的 `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/tasks/README.md`、派生 `REPORT/ROADMAP/RESUME/verify_plan.py` 的 P08 状态。禁止：产品源码/测试/打包、共享契约/Schema/依赖、`doc/04`/`doc/08`/`AD-001`/`doc/13` 源文件；不释放 P09–P20；不恢复 Qoder 资格；不替用户作产品取舍。
- **Deliverables**：① 归档本 R4 报告原文（含 SHA256）并挂载 DSH native session/exit；② 收口 R4-01（`STATUS.md:10`）、R4-03（R1 Handoff 指针），评估 R4-02（正向 allowlist）；③ 在固定 head 复跑 `python -B -X utf8 verification/P08/verify_scope.py`、`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`、`git diff --check base <head>` 与受保护路径 `git diff --name-only`，逐次入库环境/EXIT；④ 更新 Task/Plan/Status/Index/Roadmap/Handoff/RESUME。
- **Verification / Gate**：命令级证据须绑定**固定 head** 且带 shell/解释器头与 EXIT；`NOT_RUN`/`NOT_VERIFIED` 不得写成 PASS；P0/P1 未闭合、D1–D7 或数据保护回退、关键证据缺失时不得置 `done`。
- **可直接转发指令**：请在 `G:/CODEX/New Manga`（main，P08 允许路径内）接收 DSH R4 `approved` 报告并归档原文与 SHA256，确认 DSH native session/CLI exit；按最小范围收口 `doc/STATUS.md:10` 与 `doc/handoffs/P08-490f9bd9.md:37`，评估 `verification/P08/verify_scope.py` 正向 allowlist 断言；随后在固定 head 复跑 `python -B -X utf8 verification/P08/verify_scope.py`、`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`、`git diff --check ab2f813c0ce311a6712002cafd852b9e7a258380 <head>` 及受保护路径差量检查并记录环境/EXIT，同步 P08 Task/Plan/Status/导航；满足全部完成 Gate 后方可置 `done`——在此之前保持 P08 未完成、P09–P20 未释放，不修改 D04/D08/AD-001/doc/13 与产品源码/测试，`NOT_RUN` 不得改写为 PASS。

**非作者/只读声明**：本会话未修改、创建、删除任何项目文件，未 stage/commit/checkout，未改动 Git 状态或 worktree HEAD；报告仅在最终答复中交付，供 Codex 核验与归档。
