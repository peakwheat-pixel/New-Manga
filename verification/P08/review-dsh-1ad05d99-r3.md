# P08 DSH 正式 Review（R3）

---
task_id: P08
reviewer: DeepSeek Harness（非作者；作者/Integrator=Codex）
author: Codex
base_commit: ab2f813c0ce311a6712002cafd852b9e7a258380
reviewed_head: 1ad05d99c924678f35a2558f6e15b6c548d92f09
decision: changes_requested
---

## 1. 范围与依据

**受审交付**：`ab2f813c0ce311a6712002cafd852b9e7a258380..1ad05d99c924678f35a2558f6e15b6c548d92f09`（完整 P08 文档交付），固定 head=`1ad05d99c924678f35a2558f6e15b6c548d92f09`。

**先读文件**：`AGENTS.md`、`doc/09_COLLABORATION.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P08.md`、`verification/P08/RESUME.md`；随后核实 `doc/04_USER_FLOW.md`、`doc/08_ACCEPTANCE_CRITERIA.md`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`、`doc/13_ACCEPTANCE_TRACEABILITY.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/tasks/README.md`、`doc/templates/REVIEW.md`、`verification/P08/{SCOPE_DRAFT.md,AC_COVERAGE.md,verify_scope.py,validation.log,review-dsh-31c2638.md}`、`verification/PROJECT-ROADMAP-20261008/{verify_plan.py,ROADMAP.md}`。

**差量定位方法（因 shell 不可用，改用 linked worktree + `.git` 文件层）**：
- 主仓 `G:/CODEX/New Manga/.git/logs/HEAD:929-943` 还原提交链：`ab2f813`(base) → `490f9bd`(R1) → `31c2638`(R2) → `77ba9b3`「record DSH round-two findings」→ **`1ad05d9`「address DSH round-two findings」** → `e56ac2c`「prepare third DSH review」(main tip)。
- 因此本 head = **N-01..N-06 的作者修订提交**；绑定该 head 的 Handoff/Prompt/Task 记录位于其后一提交（`e56ac2c`），这与 `doc/09_COLLABORATION.md:90`（"Handoff 在交付 head 之后以文档提交追加······避免要求文件包含自己的 commit hash"）一致，**不构成缺陷**。
- 我以并存的两个 linked worktree 做内容级差量：本 review worktree=`1ad05d9`、R2 worktree=`P08-dsh-review-31c2638`=`31c2638`（两者 `.git` 层 HEAD 均由文件读取确认）。

**未使用聊天记录作为产品事实；D1–D7 未重开、未重新解释为 Reviewer 裁决。**

## 2. 工作区 / Git 核验（DSH 自身可执行部分）

| 核验项 | 方式（DSH 实际读取） | 结果 |
|---|---|---|
| HEAD == reviewed_head | 读 `.git/worktrees/P08-dsh-review-1ad05d9-r3/HEAD` = `1ad05d99c924678f35a2558f6e15b6c548d92f09` | **严格相等**，detached ✅ |
| 该 worktree 自创建起未被推进 | 读 `logs/HEAD`：仅 1 行 `0000…0000 → 1ad05d99… peakwheat-pixel 1791469806 +0800` | 无 checkout/commit/rebase ✅ |
| worktree 反向绑定 | 读 `.git` 文件 = `gitdir: G:/CODEX/New Manga/.git/worktrees/P08-dsh-review-1ad05d9-r3` | ✅ |
| common-dir | 读 `commondir` = `../..` → `G:/CODEX/New Manga/.git` | ✅ |
| `git status` clean / `rev-parse` / `diff --check` / 两条 python | DSH `pwsh` 在 ACL 授予阶段失败 | **NOT_RUN**（见 §6） |
| 工作树内容 == 被审提交内容 | 无 `git status`；以 HEAD/reflog 文件层 + 主仓/旁证 worktree 内容比对替代 | **NOT_VERIFIED**（DSH）；旁证与 `1ad05d9` 树一致（P08.md/RESUME/validation.log 均处 R2 记录态，SCOPE_DRAFT/AC_COVERAGE/两校验器已含 R3 修订，恰为「fix 提交」形态） |
| 主仓 tip 与证据提交定位 | 读 `.git/logs/HEAD:943` | main tip = `e56ac2c`，是受审 head 的**直接子提交**，承载 R3 Handoff/Prompt 与 Codex 证据 ✅ |

## 3. Architecture 面结论

**在记录范围内未发现架构分层、冻结契约或产品边界问题（`executed`＝文件层核对；DSH 未能运行 git/python）。**

- 产品边界未扩大：四页一级导航不变（`doc08:241-255` AC-NAV-001/002；`AD-001:26` 明列 Library/Bookshelf、Workspace/Workbench、Reader、Settings），`SCOPE_DRAFT.md:15-23` 的 D1–D7 原样保留，**D5 门槛未降低**（`:21` 仍为"P0/P1全部通过、AC-SMOKE完整主流程全部通过"）。
- AD-001 边界一致：`AD-001:9`（目标架构文档重基线前，02/D07/D08 仍描述 legacy 生产基线）、`:35`（源文件安全/Managed Copy/人工修改/Lock/current/pinned + 可恢复任务状态）、`:36`（PyInstaller/QML PASS 不可复制为 Tauri 打包 PASS）与 `SCOPE_DRAFT.md:49`、`AC_COVERAGE.md:189-191` 一致；`AD-001:45` 的历史 Qoder 署名按"历史证据保留、不恢复资格"处理且未改动。
- 未释放边界未越过：`REBASELINE_PLAN.md:39` 为 `| P08 | changes_requested |`，`:32-52` 其余 20 行 `proposed / 未释放`；`SCOPE_DRAFT.md:69-71` 明示 P09–P20 无正式 Task；`doc/tasks/` 下确实不存在 P09–P21 文件。
- **Architecture Documentation Rebaseline 前置 Gate 仍清晰**：`SCOPE_DRAFT.md:49/:71`、`AC_COVERAGE.md:189-191`（AC-DOC-001..003 为 §66 正式开发前 Gate，Legacy PASS 不自动关闭新架构 Gate）、`REBASELINE_PLAN.md:40/:49/:51`（P09/P18/P20 依赖该 Task 映射）三处一致，且明确"未登记、未释放、P08 不创建它"。

## 4. Verification 面结论

**结论：N-01..N-06 六项修订在受审 head 上逐项成立（`closed`）；R1 的 4×P1、R2 的 0×P1 未发现任何回退；但 `AC_COVERAGE.md:142` 残留一处与源文冲突的格式归属声明（N-07，P2）→ 本轴本轮不可批准。**

### 4.1 DSH 亲自执行的检查

| 场景 | 命令 | 环境 | 结果 | EXIT |
|---|---|---|---|---|
| 所有 shell/git/python 检查 | `git -C … rev-parse HEAD`、`status --porcelain=v1`、`rev-parse --git-common-dir`、`log --oneline`、`diff --name-status/--stat/--numstat/--check <base>..<head>`、`python -B -X utf8 verification/P08/verify_scope.py`、`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` | DSH `pwsh`；每次调用在进入解释器前失败：`Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\P08-dsh-review-1ad05d9-r3)`（另一 workdir 复现同一错误；子代理会话复现同一错误） | **NOT_RUN** | 无（未产生 stdout/stderr） |
| 文件层取证（本报告全部事实来源） | `read`/`glob`/`grep` 读 `.git` 管理文件、两 worktree 与主仓文件 | DSH 文件工具 | executed ✅ | — |

依纪律：**未尝试提权**；未把 Codex 结果写成 DSH 执行结果。

### 4.2 归属为 Codex 的 producer 证据（已读取，非 DSH 执行）

主仓 `verification/P08/validation.log:270-282`：`reviewed_head=1ad05d99…`、`review_worktree=…P08-dsh-review-1ad05d9-r3; detached; clean; common_dir=G:/CODEX/New Manga/.git`、`PowerShell 7.6.6`、`Python 3.14.6 (C:\Python314\python.exe)`、`verify_scope.py` EXIT=0、`verify_plan.py` EXIT=0、`git diff --check` EXIT=0、`git diff --name-only -- src apps tests packaging` 空；`doc/handoffs/P08-1ad05d99-dsh-r3.md:22-28` 给出对应交付表并明示"只代表Codex命令"。该证据位于受审 head 之后一提交（符合 `09_COLLABORATION.md:90`），且 DSH 无法验证主仓该文件内容 == 提交 blob（§6）。

## 5. Findings

### 5.1 R3 指定项（N-01…N-06）

| ID | 级别 | 判定 | 独立证据（受审 head；括号内为 R2 侧对照=修订必要性） |
|---|---|---|---|
| **N-01** | P2 | **closed** | `SCOPE_DRAFT.md:40` 现写"D04 §37与D08 AC-EXPORT-001列出的单图、ZIP、CBZ、PDF、文本全部覆盖；用户D1/D2将单图映射为PNG"，同格来源列写"D04 §37与AC-EXPORT-001均列五种输出格式，PNG映射来自用户D1/D2"。源文核实：`doc/04:1446-1472`（§37「导出流程」格式块逐行 **单图/ZIP/CBZ/PDF/文本**）、`doc/08:2054-2064`（AC-EXPORT-001 [P0] 同五项）。**归因正确**：PNG 映射明确归于用户决定 D1/D2。（R2 侧 `31c2638:40` 原文为"D04§37仅写单图/ZIP" ❌） |
| **N-02** | P2 | **closed** | `verify_scope.py:9-10` `TASK_STATES`=9 态，`:34-37` 从协议解析状态块并断言集合相等，`:38-46` 状态/`integration_commit`/`approval`/`reviewed_head` 断言（`:43` 仅 `done` 要求非 null integration，**approved/blocked 不误报**）；`verify_plan.py:11-24` 9 态 `TASK_STATES`+9 条 `STATUS_LABELS` 且 `assert set(STATUS_LABELS)==TASK_STATES`，`:56-63/:71/:78-79` Plan 行、Task 状态、ROADMAP Mermaid 双标签三处一致。协议核实：`doc/09_COLLABORATION.md:66-76` 恰为 `proposed/ready/in_progress/blocked/in_review/changes_requested/approved/done/closed_with_limitations` 9 态。当前实态一致：Plan`:39`、P08.md`:5`、`ROADMAP.md:39/:49`。（R2 侧 `verify_scope.py` 无状态集；`verify_plan.py:47` 仅 `changes_requested\|in_review\|done`、`:52-54` 三键字典 → 下一合法状态 `approved` 必失败 ❌） |
| **N-03** | P3 | **closed（见 N-08 的 head 之后稳健性备注）** | `verify_scope.py:74-81` 的 `git diff --check` 现覆盖 `verification/P08`、`doc/tasks/P08.md`、Plan、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、**`doc/tasks/README.md`**、**P08 自有 Handoff 两件**、**`verification/PROJECT-ROADMAP-20261008`**（受审 head 的 P08 Handoff 经 glob 仅此 2 件，无遗漏）。（R2 侧 `31c2638:64-67` 仅 6 条路径 ❌） |
| **N-04** | P3 | **closed** | `verify_scope.py:65-72` 零差量保护集已含 `AGENTS.md` 与 `doc/09_COLLABORATION.md`（`:66`），并以 `git diff --name-only BASE -- …` 断言为空。（R2 侧 `31c2638:56-62` 无此两项 ❌） |
| **N-05** | P3 | **closed** | `AC_COVERAGE.md:3` 现明列"§78 仍为草案的 AGENT-001/002、FONT-003、SAKURA-002/003、**ACG-EXT-DETECT、ACG-EXT-CONTRACT、ACG-EXT-NFR** 继续由 doc/13 追踪，不在本表重复"。交叉核实：`doc/13:248/:258-260` 三项确实由 doc/13 追踪且 `NOT_RUN`；`doc/08` 全文 `ACG-EXT` **0 命中**，与"未进入 D08 正式编号"自洽。（R2 侧 `31c2638:3` 缺这三项 ❌） |
| **N-06** | P3 | **closed** | `SCOPE_DRAFT.md:78`（P12 现存`library/`+`App.tsx`）、`:80`（P14 现存`editing/`、`src-tauri/src/`、`workbench/`）、`:81`（P15 **"现存可复用：src/application/settings/（已有 bindings.py、errors.py、models.py、network.py、pipeline_defaults.py、privacy.py、resolution.py、snapshots.py）"**）、`:83`（P17 现存 Core `reading/`、`export/`；**拟议新增 `frontend/src/reader/`、`frontend/src/export/`（目前均不存在）**）。真实树核实：`src/application/settings/` 含列出的 8 个模块（另有 `__init__.py`）；`frontend/src/{library,workbench,settings,region,resourceChannel,ac1,testSupport}` 存在，**`reader`/`export` 不存在** ✅。（R2 侧 `31c2638:81` 写"拟议路径：src/application/settings/（若Task确认存在）" ❌） |

### 5.2 新增 Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| **N-07** | **P2** | `verification/P08/AC_COVERAGE.md:142`（AC-EXPORT-001 [P0] 行，状态列） | 该格写 **"INCLUDED：D08原文只写单图/ZIP；PNG是用户选定首发格式…"**。D08 关于导出格式的唯一权威条目 `AC-EXPORT-001` 实列 **五项（单图/ZIP/CBZ/PDF/文本）**，故该句把 P0 AC 的来源范围错误窄化为 2 项；且与**同一交付**的 `SCOPE_DRAFT.md:40`（"D08 AC-EXPORT-001······均列五种输出格式"）**直接互相矛盾**。影响：本文件是 P16/P17 逐 AC 判定"需求出处"的索引，会诱发"CBZ/PDF/文本在 D08 无来源"的误判（与 R2 N-01 同类缺陷，未被 N-01 修订扫掉） | `AC_COVERAGE.md:142`；`doc/08:2058-2064`（格式块：单图/ZIP/CBZ/PDF/文本）；`doc/08` 全文 `ZIP`/`CBZ` 仅命中 `:2060/:2061`（无其他"只列两项"的出处）；`SCOPE_DRAFT.md:40`；R2 侧 `31c2638:142` 逐字相同（说明系遗留而非 R3 新引入） | 改为与 `SCOPE_DRAFT.md:40`/`doc/08:2054-2064` 一致，例如"INCLUDED：D08 AC-EXPORT-001 列单图/ZIP/CBZ/PDF/文本五项；'单图'到 PNG 的映射由用户 D1/D2 选定并由 P16 契约冻结" | open |
| **N-08** | P3 | `verification/P08/verify_scope.py:77-78`（Handoff 清单）与 `:82`（PASS 文案） | P08 自有 Handoff 采用**硬编码两项**列表。受审 head 上该文案属实（两件为当时全部）；但 pack 其后的提交新增 `doc/handoffs/P08-1ad05d99-dsh-r3.md`（我已在主仓读取该文件），而主仓与受审 head 的 `verify_scope.py:74-81` 清单**逐字相同**、未含新 Handoff，因此该 PASS 文案在全仓当前状态下已不再成立 | `verify_scope.py:77-78`；受审 head `doc/handoffs/P08*` glob=2 件；主仓 `doc/handoffs/P08-1ad05d99-dsh-r3.md` 存在（`:6` delivery_head=1ad05d9）；主仓 `verify_scope.py:74-81` 与受审 head 一致 | 把 Handoff 一项改为 `doc/handoffs/P08-*.md` 之类的集合/glob，或每次新增 Handoff 时同步加入清单并让 PASS 文案与实际集合对齐 | open（非阻断；针对 head 之后提交，不影响本 head 的自洽） |

### 5.3 R1/R2 历史 closure 回看（未见回退）

| 历史项 | 本轮判定 | 依据 |
|---|---|---|
| R1 4×P1（P1-1 证据未绑 head／P1-2 AC 真值路由／P1-3 AC-WIN 落点／P1-4 Legacy 口径） | **保持 closed，无回退** | R3 证据链绑 `reviewed_head=1ad05d9`+环境+EXIT（validation.log:270-282）；`AC_COVERAGE.md:3` 的四段对账完整；`AC_COVERAGE.md:10-15` AC-WIN 仍指 P12/P14/P15/P17、P20 仅平台/安装包；`SCOPE_DRAFT.md:49` Legacy 处置段保留 |
| R1 6×P2 | **6/6 实质闭合** | P2-1（STATUS/Plan/INDEX/ROADMAP/README 均 `changes_requested` 一致）；P2-2（路径/依赖已按真实树标注）；P2-3（`SCOPE_DRAFT.md:58` 临时权威+转录条件、`:56` TEXT 含安装包导出）；P2-4（`NOT_RUN` 明示、性能三指标区分、`:66` 引用成立）；P2-5（→N-01，**closed**，但同类残留另记 N-07）；P2-6（→N-02/N-03/N-04，**closed**） |
| R1 5×P3 观察 | **保持 closed** | GATE-78 顺序 `AC_COVERAGE.md:201-212` 为 68→79；P20 执行/Review/集成三分离（`:206/:209`）；R2/R3 prompt+Handoff 均绑定真实 base/delivery head；Qoder 保留历史不恢复资格 |
| R2 N-01..N-06 | **6/6 closed** | 见 §5.1，均以受审 head 文件原文 + 源文/真实树独立复核，未以作者自述为关闭依据 |
| R2 结构性边界（head 内不自引哈希；证据文本在后一提交） | **不构成缺陷，处理正确** | `doc/09_COLLABORATION.md:90`；受审 head 的 `P08.md:17-20`/`RESUME.md:22-24`/`ROADMAP.md:3/:5` 仍为 R2 记录态，与其"fix 提交"身份自洽（与 R2 交付 `31c2638` 形态逐项同构） |

### 5.4 门槛与保护项逐条核对（未发现退化）

| 项 | 结论 | 证据 |
|---|---|---|
| D1–D7 未被扩写 | ✅ | `SCOPE_DRAFT.md:15-23` 与 R2 版本逐行同义；`verify_scope.py:48` 断言 7 行决策 |
| D5 门槛未降低 | ✅ | `SCOPE_DRAFT.md:21/:49`；`AC_COVERAGE.md:206/:209` GATE-73/76 `INCLUDED` 且"当前NOT_RUN" |
| AC 覆盖逐项对应 D08 | ✅（结构） | `verify_scope.py:13-23` 以 `doc/08` 的 193 个 `## AC-` 顺序全等 + AC-SMOKE + 12 Gate = 206 行且全 `NOT_RUN`；DSH 未复跑该断言（producer 证据） |
| 12 条 Legacy PASS 未被误报 | ✅ | `doc/13` 中 `\| PASS \|` **恰 12 行**（`:45-48,50,64,65,75,76,197-199`），ID 与 `AC_COVERAGE.md:3` 列举完全一致；本表各行均 `NOT_RUN` |
| 无 P0/P1 被延期 | ✅ | `AC_COVERAGE.md` 中 `DEFERRED` **恰 6 行**（`:194-199`），级别均为 `[P2]`（PLUGIN-001..003、FONT-001/002、SAKURA-001） |
| §74/75/79 等建议项未变成独立验收 | ✅ | `AC_COVERAGE.md:207/:208/:212` 均 `ADVISORY ONLY：不是独立Gate或单独PASS` |
| 全库备份 | ✅ | `SCOPE_DRAFT.md:20(D4)/:42`、`AC_COVERAGE.md:133-137`（AC-BACKUP-001..004 [P0]，含"Restore 不改源文件"）、`REBASELINE_PLAN.md:46/:50` |
| 源文件/人工修改/Lock/current/pinned 保护 | ✅ | `SCOPE_DRAFT.md:35/:62`（源 hash 零变化、不静默覆盖人工/Lock/pinned、失败无半提交）、`REBASELINE_PLAN.md:44/:50`、`AD-001:35` |
| 新增格式有独立验收且不冒充 D08 | ✅ | `SCOPE_DRAFT.md:51-58`（P08-FMT-MOBI/CBZ/PDF/TEXT 均 `NOT_RUN` + 临时权威与转录条件） |

## 6. 审查边界（NOT_RUN / NOT_VERIFIED）

| 项 | 状态 | 说明 |
|---|---|---|
| DSH 全部 shell/python/git 检查（含 `verify_scope.py`、`verify_plan.py`、`git diff --check`、`status`、`rev-parse`、`diff --name-status/--stat`） | **NOT_RUN（DSH）** | `pwsh` 在 ACL 授予阶段失败 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(<worktree>)`；改用其他 workdir 与子代理会话均复现；未提权（无审批通道），故不尝试 |
| 工作树内容 == 被审提交内容 | **NOT_VERIFIED** | 无 `git status`；以 `.git` HEAD/reflog/commondir 文件层 + 两 worktree 内容形态比对为旁证 |
| `ab2f813..1ad05d9` 全量差集与 allowlist 合规、24 个受保护路径零差量 | **NOT_VERIFIED（DSH）** | 只能引用 producer 断言：`verify_scope.py:65-73` 的保护集（`src/apps/tests/packaging`、`doc/contracts`、`doc/reviews`、`AGENTS.md`、`doc/09`、`doc/01–08`、`doc/13`、`AD-001`、`task-inventory.csv`）我逐条读过、内容合理；其 EXIT=0 归 Codex |
| `verify_scope.py`/`verify_plan.py` 实跑结果 | **NOT_RUN（DSH）**，producer=EXIT=0 | `validation.log:275-276`；本报告的 closed 判定基于**源码逐行审读 + 源文/真实树独立取证**，不依赖其 EXIT |
| 主仓 `validation.log`/R3 Handoff 内容 == 其提交 blob | **NOT_VERIFIED** | 以 `read` 直接读主仓工作树文件，未验证该文件无未提交改动 |
| 产品 pytest/cargo/vitest/GUI/build/model | **NOT_RUN（正确保留）** | 本 Task 无产品变更；交付各处亦明确记为 NOT_RUN |
| 质量真值/阈值/样本、Win10/干净 Windows、安装包实测 | **未声称 PASS（正确）** | `SCOPE_DRAFT.md:65` 明示缺失数值须在 P18 资格方案独立审定后冻结 |

## 7. 结论与复审

**decision = `changes_requested`**

- **0×未闭合 P0；0×未闭合 P1。** R1 的 4×P1 与 R2 的 P1 状态无任何回退。
- **R2 的 N-01..N-06：6/6 `closed`**（逐项以受审 head 文件原文 + 源文/真实树独立复核，未以作者自述关闭）。
- **新增 1×P2（N-07）+ 1×P3（N-08）**：`AC_COVERAGE.md:142` 仍称"D08原文只写单图/ZIP"，与 `doc/08:2058-2064` 及本交付 `SCOPE_DRAFT.md:40` 直接矛盾；N-08 为 head 之后一提交的 whitespace 覆盖稳健性问题（非阻断）。
- 未批准理由（不含 P0/P1）：文档冻结型 Task 的交付物在**同一交付内自相矛盾地描述一项 P0 AC 的来源**，使"范围/验收可追溯"尚未完全成立；修复量极小（单格一句），且完全落在 P08 允许路径内。

**最小修订清单（不扩范围、不改 D04/D08/AD-001/doc/13、不释放 P09–P20）：**
1. 修正 `AC_COVERAGE.md:142` 状态列为 D08 五项格式表述，保留"单图→PNG 由用户 D1/D2 选定并由 P16 冻结"的归因（N-07）。
2. 顺带 grep 全 `verification/P08/**` 是否还有"只写/仅写"式的来源收缩表述（本次已检索，`AC_COVERAGE.md:142` 为唯一命中）。
3. 建议（非阻断）把 `verify_scope.py` 的 Handoff 路径改为集合/glob，或同步加入 R3 Handoff（N-08）。
4. 修订提交后固定新 `reviewed_head`，并在**其后**的文档提交中追加 Handoff/Prompt 与 `validation.log` 条目（`09_COLLABORATION.md:90`），逐项登记 N-07/N-08 的 disposition；届时派发 R4 非作者复审。

**固定 head 结论**：本报告仅对 `1ad05d99c924678f35a2558f6e15b6c548d92f09`（base `ab2f813c0ce311a6712002cafd852b9e7a258380`）有效；head 变动后不得延用。P08 仍未 done、P09–P20 仍未释放；本报告不代表 Codex 集成结论，也不代表任何产品验收结果，且未把任何 `NOT_RUN` 改写为 PASS。

**下一任务建议（可直接转发）**：请在 `G:/CODEX/New Manga`（main/主工作区，P08 允许路径内）只读以外的最小范围内修正 `verification/P08/AC_COVERAGE.md:142`，并评估 `verification/P08/verify_scope.py:77-78` 的 Handoff 覆盖；随后运行 `python -B -X utf8 verification/P08/verify_scope.py`、`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`、`git diff --check` 并记录环境/EXIT，建立新的固定 delivery head 与新 `doc/handoffs/P08-<new-head>-dsh-r4.md`、`verification/P08/DSH-REVIEW-PROMPT-R4.md`，再派发 DeepSeek Harness 非作者 R4 复审；在此之前保持 P08=`changes_requested`、不释放 P09–P20、不恢复 Qoder 资格，且不得修改 D04/D08/AD-001/doc/13 与产品源码/测试。

**非作者/只读声明**：本会话未修改、未创建、未删除任何项目文件，未 stage/commit/checkout，未改动任何 Git 状态或 worktree HEAD；报告仅在最终答复中交付。
