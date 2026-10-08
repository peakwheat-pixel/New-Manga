# P08 第二轮正式独立 Review 报告

**Task**：P08「完整产品范围与验收冻结准备」（`doc/tasks/P08.md`）
**Reviewer**：DeepSeek Harness（非作者；作者/Integrator=Codex）
**base_commit**：`ab2f813c0ce311a6712002cafd852b9e7a258380`
**reviewed_head**：`31c263892605fdc984982b9ba1875fa6eb609cb6`
**Review worktree**：`G:/CODEX/New Manga.worktrees/P08-dsh-review-31c2638`（detached）
**decision**：**changes_requested**（0×未闭合 P0、0×未闭合 P1；1×P2 残留 + 1×新增 P2 + 4×新增 P3；首轮 4 P1 / 6 P2 / 5 P3 的逐项 closure 见 §5–§6）
**本次未修改、未 stage、未 commit、未切换 HEAD、未创建任何文件**；只读审查，报告仅在 stdout 交付（与 R2 Handoff 第 40 行约定一致）。

---

## 1. 范围与依据

**已阅读并逐条比对**：`AGENTS.md`；`doc/REBASELINE_PLAN.md`（全文，重点 `:3/:7/:28/:39-52`）；`doc/STATUS.md`（`:3/:7/:20`）；`doc/09_COLLABORATION.md`（全文）；`doc/tasks/P08.md`（受审 head 版本，94 行）；`verification/P08/SCOPE_DRAFT.md`；`verification/P08/AC_COVERAGE.md`（212 行）；`verification/P08/review-dsh-490f9bd.md`（首轮报告全文）；`doc/handoffs/P08-490f9bd9.md`；`verification/P08/verify_scope.py`；`verification/PROJECT-ROADMAP-20261008/verify_plan.py`；`verification/P08/RESUME.md`、`DSH-REVIEW-PROMPT.md`、`preliminary-review.md`；`doc/templates/REVIEW.md`；`doc/00_INDEX.md`、`doc/12_ROADMAP.md`；以及被引用的权威源文件 `doc/04_USER_FLOW.md`、`doc/07_NON_FUNCTIONAL_REQUIREMENTS.md`、`doc/08_ACCEPTANCE_CRITERIA.md`、`doc/13_ACCEPTANCE_TRACEABILITY.md`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md` 的相关条目；并复核真实仓库路径集合。

**归属声明（必须保留）**：本会话的 DSH `pwsh` 工具**全部不可用**（每次调用在进入会话前失败：`Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\P08-dsh-review-31c2638)`；向 `danger-full-access` 提权被拒：`requires approval, but no approval channel is available`）。因此：

- `git diff ab2f813c…31c2638`、`git status`、`git rev-parse`、两条 `python -B -X utf8 …`、任何 `git diff --check` **均为 DSH 的 `NOT_RUN`**，本报告**不含任何由 DSH 亲自执行得到的 PASS/FAIL/EXIT**。
- 下文引用的 `EXIT=0` 一律标注为**调用方（Codex）producer 证据**。
- 因无法运行 `git`，本轮"修改是否仅限 allowlist""diff 是否等于被审提交内容"只能记 `NOT_VERIFIED`，我改以**文件内容层 + `.git` 管理文件层**取证（§2、§8）。

---

## 2. 工作区 / Git 核验（DSH 自身可执行的部分，已执行）

| 核验项 | 方式（DSH 实际读取） | 结果 |
|---|---|---|
| HEAD == reviewed_head | 读 `G:/CODEX/New Manga/.git/worktrees/P08-dsh-review-31c2638/HEAD` = `31c263892605fdc984982b9ba1875fa6eb609cb6` | **严格相等**，detached（无 `ref:` 前缀）✅ |
| reflog 未被推进 | 读同目录 `logs/HEAD`：`0000…0000 31c263892… peakwheat-pixel <peak.wheat@gmail.com> 1791467610 +0800`（仅 1 行） | 自创建起唯一 HEAD，无 checkout/rebase/commit ✅ |
| common dir 共享 | 读 `commondir` = `../..` | 指向 `G:/CODEX/New Manga/.git` ✅ |
| 反向绑定 | 读 `gitdir` = `G:/CODEX/New Manga.worktrees/P08-dsh-review-31c2638/.git` | 回指本 worktree ✅ |
| `git status clean`、`base..head` 全量 diff、`merge-base --is-ancestor`、`branch --contains` | DSH 无法运行 `git` | **NOT_RUN** |
| 主仓 main tip / 证据 commit 定位 | 读 `G:/CODEX/New Manga/.git/refs/heads/main` = `cefbc1377567e62bd7982b84ea9beebfe60a86b9`；读 `.git/logs/HEAD` 尾部：`80f1dacd…→31c263892…（docs(P08): address DSH review findings）→cefbc137…（docs(P08): prepare exact-head DSH review）` | 受审 head 是 main tip 的**父提交**，证据 commit 在其之后 ✅（这是本报告关键结构性事实） |

**重要结构性发现（非缺陷，属协议约定）**：受审 head 全树中**不存在字符串 `31c26389`**（对 worktree 根做内容检索，0 命中；同一检索对 `490f9bd9…` 命中 29 处）。这与 `doc/09_COLLABORATION.md:90`（"Handoff 在交付 head 之后以文档提交追加，引用之前的实现 head；避免要求文件包含自己的 commit hash"）一致：**交付 head 是本提交，绑定 head 的证据/治理文本位于其后一提交**。我已按调用方指令去主仓读取该证据（§4），并把这一边界如实记录，而不是把它当作 P1。

---

## 3. Architecture 结论

**结论：未发现需要修改架构分层、冻结契约或产品边界的问题**（executed＝文件层核对）。

- 产品边界未扩大：四页一级导航不变（`doc/08:241-255` 的 AC-NAV-001/002），D1–D7 的确认结论在 `SCOPE_DRAFT.md:15-23` 原样保留，D5 的 P0/P1 与 `doc/08:171-173`（P0=100% PASS / P1=100% PASS）逐字保留；`AC_COVERAGE.md:7-199` 中无任何 P0/P1 行被标 `DEFERRED`。
- 新架构方向、Legacy 边界与 AD-001 一致：`AD-001:9`（"still describe the legacy production baseline until a separately released Architecture Documentation Rebaseline Task"）、`:13`、`:36`（"a PyInstaller/QML PASS cannot be copied into a Tauri packaging PASS"）与 `SCOPE_DRAFT.md:49`、`AC_COVERAGE.md:175-177/:202` 的新表述一致；`doc/08:188`（`PySide6 Version`）与 `doc/08:2926`（`UI 自动化 / ViewModel`）被明确标为"Legacy 语义，目标等价核定前 NOT_RUN"，未被当作新架构证据。
- 未释放边界未被越过：`REBASELINE_PLAN.md:28/:39` 为 `changes_requested`，`:32-52` 其余 20 项 `proposed / 未释放`；`SCOPE_DRAFT.md:69-71` 明示 P09–P20 "尚无正式 Task / 未认领"；Architecture Documentation Rebaseline Task 被登记为**未编号、未登记、未释放**的前置 Gate（`SCOPE_DRAFT.md:49/:71`、`REBASELINE_PLAN.md:7`），未虚构用户裁决。
- Qoder 未出现在任何当前 Owner/Reviewer/设计位（`SCOPE_DRAFT.md:9`、`AC_COVERAGE.md:3`、`09_COLLABORATION.md:5`）；`AD-001:45` 的旧 Qoder 表述按"历史证据保留、不恢复资格"处理（`doc/tasks/P08.md:73`），不在本 Task 允许路径内，处理正确。

---

## 4. Verification 结论

**结论：本冻结交付在"可归属证据"这一维度上已补齐（producer 侧），但 DSH 无法自证，且新增的验证断言存在 1 处会在下一合法状态立即失效的缺陷（N-02）→ Verification 轴本轮不可批准。**

### 4.1 DSH 实际执行的命令

| 场景 | 命令 | 环境 | 结果 | EXIT |
|---|---|---|---|---|
| 覆盖/链接/只读边界/full P08 whitespace | `python -B -X utf8 verification/P08/verify_scope.py` | DSH `pwsh -Command`；未进入任何解释器（`SetNamedSecurityInfoW Win32 5`） | **NOT_RUN** | 无（未产生 stdout/stderr） |
| 路线图/历史快照 | `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` | 同上 | **NOT_RUN** | 无 |
| 完整范围 whitespace | `git diff --check ab2f813c… 31c263892… -- doc verification/P08 verification/PROJECT-ROADMAP-20261008` | 同上 | **NOT_RUN** | 无 |
| 工作区/提交身份 | `git status`、`git rev-parse HEAD`、`git diff --stat/--name-only`、`git show main:…` | 同上 | **NOT_RUN**（改以 §2 的 `.git` 文件层读取与主仓文件读取替代） | 无 |

### 4.2 归属为 Codex 的 producer 证据（已读取，非 DSH 执行）

读取位置：`G:/CODEX/New Manga/verification/P08/validation.log:157-196`（主仓工作树文件；main tip=`cefbc137`，其 message 为 `docs(P08): prepare exact-head DSH review`）与 `G:/CODEX/New Manga/doc/handoffs/P08-31c26389-dsh-r2.md`（`:6` delivery_head=`31c2638…`、`:22-24` 证据表、`:28` 明示"由后续证据 checkpoint 提交并精确标注 reviewed_head"）。

- 该证据**完全满足 P1-1 的字段要求**：`reviewed_head=31c263892605…`、`review_base=ab2f813c…`、`repo`、`branch=detached`、`review_worktree=P08-dsh-review-31c2638`、`worktree_status=clean`、`common_dir`、`shell=PowerShell 7.6.6`、`python=C:\Python314\python.exe (Python 3.14.6)`、三条命令原文、各自 `EXIT=0`（`:169-190`）；另有 `git diff --stat`（`:191-192`：19 files, +1096/−41）与 `git diff --name-only … -- src apps tests packaging` 空（`:193-194`）。
- **我的独立旁证（推断，非 git 实测）**：把 P08 允许范围内的文件清单逐项点数，恰好 19 个（`doc/tasks/P08.md`、`REBASELINE_PLAN.md`、`STATUS.md`、`00_INDEX.md`、`12_ROADMAP.md`、`tasks/README.md`、`doc/handoffs/P08-490f9bd9.md`、`verification/P08/` 8 个文件、`verification/PROJECT-ROADMAP-20261008/` 4 个文件），与 `:192` 的 19 files 数目吻合，且 **`AGENTS.md` 与 `doc/09_COLLABORATION.md` 不在其中**——与"该交付未改协作协议与入口文档"的自陈一致。
- `doc/tasks/P08.md`（主仓版本，`:63/:85-89/:95`）已把第二轮 head、三条命令、`EXIT=0` 与证据指向写入 Task 测试表；受审 head 内的旧版本（`:82-84`）仍写 `HEAD=80f1dacd…＋工作树差量 / 修订交付固定后须在精确head重跑`，`RESUME.md:20` 亦自陈"不是新固定head的正式Review证据"——这正是"绑定文本必然落在 head 之后"的协议后果（§2），我按此判定 P1-1 已闭合，但把该边界记入 §8。

---

## 5. 首轮 Finding 逐项 closure 状态

| 首轮 ID | 级别 | 本轮判定 | 关键证据（受审 head 文件:行） |
|---|---|---|---|
| **P1-1** 验证日志未绑定 head / 缺环境头 | P1 | **closed**（含边界） | 主仓 `validation.log:157-190` 绑定 `reviewed_head=31c2638` 且含 shell/Python 绝对路径+版本/repo/branch/worktree/EXIT；`doc/handoffs/P08-31c26389-dsh-r2.md:22-28` 交付表指向该日志；`doc/09_COLLABORATION.md:177①` 要求全部满足。DSH 自身仍 `NOT_RUN`（§4.1） |
| **P1-2** AC 真值/路由冲突未对账 | P1 | **closed** | `AC_COVERAGE.md:3` 四段对账齐全：①逐条列出 12 条 Legacy `PASS`（我独立 grep `doc/13` 得 `\| PASS \|` **恰 12 行**，与所列 ID 完全一致）；②未编号 `ACG` 归属（`doc/13:217-226` 的 §51/56/57/59/60/62/63/64/67 逐条对应）；③§74/75 advisory 依 `doc/13:242`，§79 依 `doc/08:3233`「79. 下一阶段建议」；④`AC-DOC-001..003` 依 `doc/08:2821`「正式开发前必须通过文档一致性检查」列为 P09 前 Gate（`AC_COVERAGE.md:189-191`、`SCOPE_DRAFT.md:71`）。§74/75/79 行已标 `ADVISORY ONLY`（`:207/:208/:212`），无伪装 PASS |
| **P1-3** 6 条 AC-WIN 无实现工作包 | P1 | **closed**（附 N/A 级备注） | `AC_COVERAGE.md:10-15`：实现切片改为「ZCode UI切片：P12/P14/P15/P17 按窗口所属页面分配」，P20 降为「只测安装包/平台矩阵」；`AC-WIN-002` 注明与 `AC-CLOSE-001/002` 共享实现且"另保留应用级证据"，关闭语义边界保留。对应 D08 条目 `doc/08:286-366` 确为 6 条 `[P1]` |
| **P1-4** Legacy 基线口径冲突未处置 | P1 | **closed** | `SCOPE_DRAFT.md:49` 增补 legacy 处置段：D5 数值/P0/P1 不变；`AC-PKG-001/003`、`doc/08:188` §6 PySide6、§69 ViewModel/QML 不得直接作 Tauri/React PASS；等价表述须由"单独授权、正式释放的 Architecture Documentation Rebaseline Task"产出，完成前只记 `NOT_RUN`；`AC_COVERAGE.md:175-177`、`:202` 行内同步；Plan/Task 均记该 Task 未编号未释放（`REBASELINE_PLAN.md:7`）。无虚构用户决策 |
| **P2-1** STATUS 同日矛盾 | P2 | **closed** | `STATUS.md:3/:7/:20` 与 `REBASELINE_PLAN.md:3/:28`、`00_INDEX.md:3`、`12_ROADMAP.md:3`、`doc/tasks/P08.md:5` 全部一致为"D1–D7 已确认、P08 `changes_requested`、其余 20 项 proposed/未释放"，原"等待D1–D7"措辞已消失 |
| **P2-2** 依赖/职责/路径错配 | P2 | **closed** | `SCOPE_DRAFT.md:75/:78/:80/:81/:83/:84/:86` 逐项修正；我用真实仓库逐条核对：`src/bootstrap/core_assembly.py` ✅、`apps/desktop/frontend/src/library/`✅+`App.tsx`✅、`reader/`与`export/`确不存在✅（已标注）、根级 `experiments/`✅与`verification/`✅（已声明不存在 `verification/experiments/`）；P15 依赖补 `P10＋ZCode设置设计Task`且"恢复必须 P13 停写排空"，与 `REBASELINE_PLAN.md:46` 一致；P12/P14/P17 设计门具名；`AC-PKG-*/AC-OPTIONAL-*` 打包职责改指 P20（`AC_COVERAGE.md:175-179`） |
| **P2-3** 新格式缺权威通道 / TEXT 缺安装包验证 | P2 | **closed** | `SCOPE_DRAFT.md:58` 增加"暂由本表与 P16/P17 契约作为验收来源，须经单独授权的 Architecture Documentation Rebaseline Task 转录至 D08 或 doc/13"；`:56` TEXT 行已含"生产安装包实际导出与可重开"，与 CBZ/PDF/MOBI 三行对齐 |
| **P2-4** 易误读措辞/等价关系/性能口径 | P2 | **closed** | `SCOPE_DRAFT.md:49` 全部改为"要求…（当前 NOT_RUN）"；`:40` 与 `AC_COVERAGE.md:142` 声明"不把'单图'等同于 PNG，PNG 是用户选定首发格式"；`:66` 引文我逐条核对成立：`doc/08:1484`（暂停 UI ≤200 ms）、`doc/08:2154`（一级页切换 P95≤300 ms）、`doc/08:2441`+`doc/07:280/:286`（4 Hz / 每 250 ms），并明示"这些是不同指标" |
| **P2-5** D04 来源引用不准确 | P2 | **未完全闭合**（见 **N-01**） | 6 处修订我逐条验证**均成立**：四页→`doc/04:27`（§1.1）✅；约束/术语→`§20–22`（`doc/04:721/:759/:786`）且 TM 管理改指 D08 AC-TM-001..004 ✅；诊断→`doc/08:2401` AC-LOG-003 ✅；备份→`doc/04:1499` 仅分区名 ✅；`current`→`doc/04` 全文 0 命中 ✅（grep `current` 无匹配）；缩略图→`doc/04:332/:1216` 并注 D1 延期 ✅。**但同一行新增的 "D04§37仅写单图/ZIP" 与源文不符** → 见 N-01 |
| **P2-6** 验证器覆盖不足 | P2 | **部分闭合**（见 **N-02/N-03/N-04**） | `verify_scope.py:56-62` 已把 `doc/01–08`、`doc/13`、`AD-001` 纳入零差量集合 ✅；`:64-67` 已把整个 `verification/P08` 纳入 `git diff --check` ✅；`:31-54` 新增动态状态断言 ✅（但集合不完整，N-02）；治理 whitespace 范围与 PASS 文案不一致（N-03）；保护集未含 `AGENTS.md`/`doc/09`（N-04） |

**首轮 P1 汇总：4/4 closed；首轮 P2：5/6 closed，1 项（P2-5）残留 1 处不准确来源声明。**

---

## 6. 首轮 P3 观察逐项处置

| 首轮 P3 | 处置判定 | 证据 |
|---|---|---|
| 1. GATE-78 行顺序/表头计数 | **closed** | `AC_COVERAGE.md:201-212` 严格 68→79 顺序（GATE-78 在 `:211`、GATE-79 在 `:212`）；表头不再出现旧"§68–77/79"措辞，改为"编号AC和发布/总Gate逐项列出"（`:1-3`） |
| 2. P20 执行 vs Reviewer/Codex 集成混淆 | **closed** | 列名改为「建议实现切片（未认领）」+「验收责任」；GATE-73 明确"P20 逐格提交证据；DSH 独立 Review；Codex 做集成判定"（`:206`），GATE-76 同（`:209`） |
| 3. 旧 prompt/Handoff 无固定复审字段 | **closed（在后续证据 commit 内，不在受审 head 内）** | 受审 head 的 `DSH-REVIEW-PROMPT.md:5` 仍是 R1 的 `490f9bd`（作为历史正确保留）；R2 的 `verification/P08/DSH-REVIEW-PROMPT-R2.md:8` 与 `doc/handoffs/P08-31c26389-dsh-r2.md:6/:39` 固定在 `31c2638…`（我已在主仓读到这两个文件）；受审 head 内 0 处 `31c26389`（§2） |
| 4. 保留 Qoder 历史但不恢复资格 | **closed** | `doc/tasks/P08.md:73` 明示"不在 P08 允许路径内，按历史证据保留；AGENTS 与协作协议当前 Qoder 退出裁决优先，后续治理任务另行登记，不恢复其项目角色"；`09_COLLABORATION.md:5`、`AGENTS.md:22` 为现行裁决 |
| 5. AD-001/doc/13 历史 Qoder 署名 | **closed（保留既有处置）** | `AD-001:45` 未被改动（`verify_scope.py:61` 断言其零差量），与 P08 不做越权治理一致 |

---

## 7. 新增 Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 |
|---|---|---|---|---|---|
| **N-01** | **P2** | `verification/P08/SCOPE_DRAFT.md:40` | 「当前缺口/来源」列写 **"D04§37仅写单图/ZIP"**，与源文冲突；该列是未来 P16/P17 契约与 Reviewer 判定"需求出处"的唯一指针（首轮 P2-5 的同类问题）。影响：把已存在的 D04 导出流程来源窄化为 2 种格式，与同一行的"已确认范围"列（D1/D2 选定 PNG/ZIP/CBZ/PDF/文本）自相矛盾，弱化 To-Be 与来源的对应关系 | 受审 head 的 `doc/04_USER_FLOW.md:1446`（§37 导出流程）、`:1464-1471` 的"格式："代码块逐行列出 **单图 / ZIP / CBZ / PDF / 文本** 五项 | 改为依源文表述，例如"D04§37 列 单图/ZIP/CBZ/PDF/文本；D08 AC-EXPORT-001（`doc/08:2054-2064`）同列五项；'单图'到 PNG 的映射由用户 D1/D2 选定并由 P16 契约冻结" |
| **N-02** | **P2** | `verification/P08/verify_scope.py:31`（`^status: (changes_requested\|in_review\|done)$`）、`:34`、`:53`；`verification/PROJECT-ROADMAP-20261008/verify_plan.py:41`、`:47-48`、`:52-55` | 为回应 P2-6 而新增的"动态 P08 状态断言"只接受 3 个状态：协议状态机的 `approved`（以及 `ready`/`in_progress`）不在集合内，`verify_plan.py:52-54` 的 `p08_label` 映射亦无 `blocked`。**影响：本次 Review 若被接受，P08 的下一合法状态 `approved` 会使两脚本直接失败**（`assert state` → AssertionError；`verify_plan.py:52` 字典取值 → KeyError），即交付自身的 Gate 工具在下一步不可复跑，须在该步临时改工具 | `doc/09_COLLABORATION.md:66` 状态机：`proposed → ready → in_progress → in_review → approved → done`（另有 `blocked`/`changes_requested`）；对照 `verify_scope.py:31`、`verify_plan.py:41/:47/:52-55` | 让允许集与 `09_COLLABORATION.md:66` 一致（至少补 `approved`，并统一 `verify_plan.py` 的行状态集与 `p08_label`），或改为"状态 ∈ 协议状态机"的断言 |
| **N-03** | P3 | `verification/P08/verify_scope.py:64-68` 与 `:69` 的 PASS 文案 | 脚本内 whitespace 检查只覆盖 `verification/P08`、`doc/tasks/P08.md`、Plan、STATUS、`00_INDEX`、`12_ROADMAP` 六个路径，但文案与主仓日志（`validation.log:174`）称 "full P08 subtree/task governance diff is whitespace-clean"。本交付还改了 `doc/tasks/README.md`、`doc/handoffs/P08-490f9bd9.md` 与 `verification/PROJECT-ROADMAP-20261008/**`（§4.2 的 19 文件旁证），其中 Handoff 未被任何 whitespace 断言或日志命令覆盖 | `verify_scope.py:64-67` 路径清单 vs 主仓 `validation.log:189` 的显式命令清单（含 README 与 roadmap 目录，仍不含 `doc/handoffs`） | 把 `doc/tasks/README.md`、本 Task 自有 Handoff、`verification/PROJECT-ROADMAP-20261008` 纳入脚本内的 `git diff --check`，或把 PASS 文案收窄为实际集合 |
| **N-04** | P3 | `verification/P08/verify_scope.py:56-62` | 只读保护路径集合未含 `AGENTS.md` 与 `doc/09_COLLABORATION.md`，而二者都在本 Task 允许修改范围之外（`doc/tasks/P08.md:75-81`）。影响：若发生越界改动，机器检查无法发现 | 允许范围 `doc/tasks/P08.md:75-77`；保护清单 `verify_scope.py:56-62` | 将 `AGENTS.md`、`doc/09_COLLABORATION.md` 加入零差量集合（或另立治理文件零差量断言） |
| **N-05** | P3 | `verification/P08/AC_COVERAGE.md:3` | 对账句把"未编号 ACG 主题"枚举为 `（§51/56/57/59/60/62/63/64/67）`，读起来像穷举，但 `doc/13` 还有 `ACG-EXT-DETECT`/`ACG-EXT-CONTRACT`/`ACG-EXT-NFR` 三个同样不进入本表的主题 | `doc/13_ACCEPTANCE_TRACEABILITY.md:258-260` | 句尾补"以及 §78 区域的 `ACG-EXT-DETECT/CONTRACT/NFR` 等未编号主题亦继续由 `doc/13` 追踪" |
| **N-06** | P3 | `verification/P08/SCOPE_DRAFT.md:78`、`:80`、`:81`、`:83` | 修订把**已存在**的目录也一并标为"拟议路径"：`apps/desktop/frontend/src/library/`、`App.tsx`、`src/application/editing/`、`apps/desktop/frontend/src/workbench/`（真实存在）；同时 `:81` 写 `src/application/settings/（若Task确认存在）` 而该目录实际存在 8 个文件。影响：As-Is/To-Be 口径被轻微低估，行内标注不一致（`:75` 列同层路径未标"拟议"） | 真实树：`apps/desktop/frontend/src/{library,workbench,settings}/…` 存在、`reader/`与`export/`不存在；`src/application/settings/{bindings,errors,models,network,pipeline_defaults,privacy,resolution,snapshots}.py` 存在 | 区分"现存路径（复用）"与"拟议新增路径"，并把 settings 的存疑括号改为事实陈述 |

**结论性说明**：N-01 使首轮 P2-5 只能判为"部分闭合"；N-02 说明 P2-6 要求的三项判别力中，"动态 P08 状态断言"在下一合法状态即失效。二者均为 P2，且都在本 Task 允许修改路径内、修复成本很低。

---

## 8. 未运行检查与 NOT_VERIFIED 边界

| 项 | 状态 | 说明 |
|---|---|---|
| DSH 侧全部 shell/python/git 检查 | **NOT_RUN（DSH）** | `pwsh` 在 ACL 授予阶段失败（`SetNamedSecurityInfoW Win32 5`），提权无审批通道；与主仓 `doc/handoffs/P08-31c26389-dsh-r2.md:26` 记录的 DSH 侧 `NOT_RUN` 一致 |
| 工作树内容 == 被审提交内容 | **NOT_VERIFIED（DSH）** | 无 `git status`；仅由 §2 的 HEAD/reflog 文件层证据 + 调用方自陈支撑 |
| `git diff ab2f813c…31c2638` 全量差异、allowlist 合规、24 个受保护路径零差量 | **NOT_VERIFIED（DSH）** | 只能记 `NOT_VERIFIED`；producer 侧 `verify_scope.py:63` + `validation.log:174/:193-194` 记为 `EXIT=0`（归 Codex） |
| `git show main:verification/P08/validation.log` | **NOT_RUN** | 改以 `read` 直接读主仓工作树文件 `G:/CODEX/New Manga/verification/P08/validation.log`（`:157-196`）；**因此"该文件内容 == main 提交 blob"未验证**（若主仓该文件另有未提交改动，则我所引用的 R2 证据可能与提交内容不同） |
| 193 条 AC 的逐 ID 顺序一致性 | **部分独立验证** | 我用内容检索独立点数：`doc/08` 的 `^## AC-` 恰 **193** 行，`AC_COVERAGE.md` 的编号行区间恰 **206** 行（193+AC-SMOKE+12 Gate），并抽查各段边界顺序与 D08 一致；"逐 ID 完全相等"由 `verify_scope.py:15` 的 `actual == expected` 断言（Codex 实跑 `EXIT=0`）保证，DSH 未复跑 |
| 产品 pytest/cargo/vitest/GUI/build/model | **NOT_RUN** | P08 为文档 Task，交付自陈 `NOT_RUN`；不属于本交付范围 |
| 质量真值/阈值/样本、Win10/干净 Windows、安装包实测 | **NOT_VERIFIED（正确保留）** | `SCOPE_DRAFT.md:65` 明确缺失数值须在 P18 资格方案独立审定后冻结，未编造 |
| 受审 head 内的 `reviewed_head` 自引用 | **不适用（协议要求）** | 受审 head 全树 0 处 `31c26389`（§2），绑定文本在 `cefbc137`；`09_COLLABORATION.md:90` 明令避免文件包含自身 commit hash，故不构成缺陷，但意味着**任何"冻结交付"都无法自我引用 head**，复审需按调用方指令读 main 上的证据 |

---

## 9. 结论与复审要求

**decision = `changes_requested`**

- **0×P0；0×未闭合 P1**（首轮 4 项 P1 全部关闭，见 §5）。
- **首轮 6 项 P2：5 项关闭，P2-5 部分闭合**（残留 N-01）。
- **新增 2×P2 + 4×P3**（N-01…N-06）。
- 未批准理由（不含 P0/P1）：(a) 修订在 P2-5 同类问题上留下 1 处与源文冲突的来源声明（N-01），使"修订完整、可追溯"尚不成立；(b) 本轮为回应 P2-6 新增的状态断言与治理 whitespace 检查**判别力不足且在下一合法状态即失效**（N-02/N-03/N-04）。二者都在 P08 允许路径内，修复量很小；按本 Task AC（`doc/tasks/P08.md:40-41`「按下表修订全部 P1/P2 并由新的固定 head 复审」「新固定 head 的 DSH 非作者复审 finding 全部闭合」）应先闭环再定 head。

**最小修订清单（不扩范围、不改 D08/doc/13/AD-001、不释放 P09–P20）**：
1. 修正 `SCOPE_DRAFT.md:40` 的 D04 §37 来源表述（N-01），并顺带复核 `:31-42` 中其余来源指针是否与 `doc/04` 原文一一对应。
2. 让 `verify_scope.py:31/:34`、`verify_plan.py:41/:47-48/:52-55` 的允许状态与 `09_COLLABORATION.md:66` 状态机一致（至少补 `approved`，统一 `blocked`）（N-02）。
3. 把 `doc/tasks/README.md`、本 Task 自有 Handoff、`verification/PROJECT-ROADMAP-20261008/**` 纳入脚本内 whitespace 检查或收窄 PASS 文案；把 `AGENTS.md`、`doc/09_COLLABORATION.md` 加入零差量保护集（N-03/N-04）。
4. 补齐 `AC_COVERAGE.md:3` 的 ACG 枚举与 `SCOPE_DRAFT.md:78-83` 的"现存 vs 拟议"标注（N-05/N-06）。
5. 修订提交后固定新的 `reviewed_head`，并把本轮全部 findings 的 disposition 追加进 Task 表；**新的 evidence/binding 文本仍应按 `09_COLLABORATION.md:90` 落在新 head 之后的文档提交**，并明确写出被绑定的 head（本报告的 §2/§8 已说明这一结构性边界，不需要也不可能把 head 哈希写进 head 自身）。

**对本次 reviewer 结论的适用范围**：本报告只对 `31c263892605fdc984982b9ba1875fa6eb609cb6` 有效（`09_COLLABORATION.md:155`：分支随后变化不延用旧批准）。P08 仍未 done，P09–P20 仍未释放；本报告不代表 Codex 已完成集成，也不代表任何产品验收结果。

---

### 非作者/只读声明

DSH 本会话未修改、未 stage、未 checkout、未 commit、未删除或清理任何文件，未改动任何 Git 状态、未推进 Review worktree HEAD；除本报告外未写入任何仓库文件。所有 DSH 未能执行的检查均记 `NOT_RUN`，Codex 的 `EXIT=0` 一律按 producer 证据引用，未写成 DSH 亲自运行。\n