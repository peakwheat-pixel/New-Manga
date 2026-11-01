---
task_id: task-1
document_id: FEA-D06-CLOSEOUT-r1
kind: independent_review
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-1"
reviewer_independent: true
reviewed_by_implementer: false
author: dsh-lead（DSH 主会话，Lead / Architect / Integrator）
base_commit: 6358cfd05
reviewed_head: 12c63b925
reviewed_head_full: 12c63b92597c4b4ac367b6c204d5cd1a608fe315
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 12c63b92597c4b4ac367b6c204d5cd1a608fe315）；工作区 clean（git status --porcelain 空）"
repository: G:/CODEX/New Manga
source_branch: main
scope: "FEA-D06-GAP 收口材料（Canonical Evidence / Resource Manifest / Closeout Record）+ 同 commit 新增的 doc/checkpoints/AUTONOMOUS-2026-11-01.md"
decision: changes_requested
verdict: changes_requested
p0_count: 0
p1_count: 3
p2_count: 5
checkps1: "PASS（3 warnings），EXIT=0；默认调用与 -TaskPath doc/tasks/FEA-D06-GAP.md 两种调用均实跑，输出一致"
verifypins: "PASS (all 13)，EXIT=0；C-08 pin = 453f993c1a16eab9db783f5b3a24710ac6e24b9a290a2b05bcba45f463fa8517，与文件实算一致"
reviewed_sha256:
  doc/tasks/FEA-D06-GAP.md: 09a620b41dac7ef99d96d9a84a95a623fc042424a9db5f7dfb2e0c3013a9cb9f
  doc/checkpoints/AUTONOMOUS-2026-11-01.md: f1244df9b2771093c2ad9929ecd0e78bf0e9ea9e9b849e26a69afe09ef420cd0
independence_note: >-
  本复核与被审收口材料的产出方为不同上下文（DSH 主会话 vs 独立 teammate），不构成自审。
  但须披露：3 条 Canonical Evidence 对应的 3 份报告（FEA-C08-r12 / FEA-D04D07-COVERAGE-r3 /
  GATE-DELETE-CONTRACT-CLOSURE-r3）均由本人（c01b-reviewer）在更早轮次产出，即本人是"被引用证据"的作者。
  本报告只裁定「收口材料是否忠实、完整地引用这些既有证据」，不重新为它们出具批准，也不因作者身份放宽标准。
captured_at: 2026-11-01T12:17:31+08:00
captured_by: c01b-reviewer
---

# Review：FEA-D06-GAP 收口（R1）

## 范围与依据

本 Review 只对 YAML 中固定的 `base_commit: 6358cfd05` 与 `reviewed_head: 12c63b925` 有效。复核全程 HEAD 未前进、工作区 clean；若 head 改变，本文件自动降为历史记录。

**被审 diff（全量，`git diff --stat 6358cfd05 12c63b925`）**：

```text
 doc/checkpoints/AUTONOMOUS-2026-11-01.md | 27 +++++++++++++++++++++++
 doc/tasks/FEA-D06-GAP.md                 | 38 ++++++++++++++++++-------------
 2 files changed, 50 insertions(+), 15 deletions(-)
```

被审内容：①`doc/tasks/FEA-D06-GAP.md` 状态 `in_progress → in_review`、`delivery_head`/`canonical_evidence_status` 回填、Canonical Evidence 3 行、Resource Manifest 单行表、Closeout Record；②新增 `doc/checkpoints/AUTONOMOUS-2026-11-01.md`。

**依据（按优先级）**：

- `AGENTS.md`：当前授权（STATUS 为唯一 Active Task 与运行状态权威）、每次开始工作、工作区规则。
- [09 协作协议](../09_COLLABORATION.md)：§4（Task 文件约定 / 状态机）、§4.1（Canonical evidence：**每个已释放 AC/Gate 指向一个当前证据项**）、§4.2（Task closeout 与派生资源、allowed_paths 越界处置、`done` 前门禁）、§4.3（AC 状态标记）、§5.1（下一任务建议 ≠ 任务释放）、§5.2（Rolling checkpoint 必须 Task-local，**不另建全局 `CHECKPOINT.md`**）、§6（独立性口径）。
- [WORKSPACE_GOVERNANCE](../WORKSPACE_GOVERNANCE.md) §Workspace 路径（`temp/<TASK-ID>/` 等按 Task 分目录）。
- [00_INDEX](../00_INDEX.md)（"当前恢复点 = STATUS 指定的 rolling checkpoint"）。
- `doc/templates/REVIEW.md`、`tools/governance/check.ps1`（只读阅读其判定逻辑，用于区分"机器 PASS"与"语义合规"）。

**未审到的部分（如实声明，不作 PASS）**：

1. AC1–AC4 与 M2-C1 `:203`/`:137`/`:902`/`:1060`、P11 §3.3 的**条款级逐字语义对照**——本轮未重跑（与 Task 自述一致）；我仅做了"条款是否存在"的抽查。
2. AC5/AC8/AC9 的**底层结论语义**——我只核验了证据文件的路径/commit/sha256/verdict/frontmatter，未重做覆盖分析与 Gate 判定。
3. 冻结契约的**语义正确性**——只核"字节未动 + pin 一致"，未重审条款内容。
4. 运行日志未另建 `verification/` 目录（不在 Review 座位写权限内），命令与 EXIT 逐条记录于本报告。

## Standards（记录在案的标准；硬性项）

| 标准 | 条款 | 本次判定 |
|---|---|---|
| Canonical evidence 必须覆盖每个已释放 AC | 09 §4.1 | **违反**：AC1/AC3/AC4 无证据项指向（R-001） |
| Resource Manifest 必须逐项给 disposition 与引用检查结果，并在 manifest 内闭环 | 09 §4.2 | **违反**：本次 Task 实际存在仓外临时脚本，未登记为任何 disposition（R-002） |
| 不得越过 frozen `allowed_paths` 写入；越界须暂停并在 Task 提出范围变更 | 09 §4.2 记协作纪律（§4 内第 4/6 条） | **违反**：新增 `doc/checkpoints/` 不在 allowed_paths（R-003） |
| Rolling checkpoint 必须 Task-local，不另建全局 checkpoint | 09 §5.2 | **违反**：新增跨 6 项排队的全局 checkpoint 载体（R-003） |
| 证据 pin 必须对该 commit 的 blob 可复现 | 09 §4.1 | 符合（R-000 核验，见验证表 V-4） |
| AC 行必须 `- [x]` + 行末 `<<MET>>` | 09 §4.3 | 符合（9/9） |
| `done` 前才回填 integration_commit / resource_closeout_status | 09 §4.2、check.ps1 `:743`–`:747` | 符合（`in_review` 阶段保留 null/pending 合法） |

（可选视角：本轮未使用 Spec baseline，理由是本次 diff 纯文档且 AC 的语义验证已明示 NOT_RUN；不使用 baseline smell 判定。）

## Architecture

**总体**：本 commit 不含代码、不含契约字节改动（`git diff 63508cfd05 12c63b925 -- doc/plan/` 为空；`verify_pins.ps1` 13/13），因此不存在分层/依赖/持久化风险面。架构问题集中在**治理面**：证据链完整性、资源闭环、写权限边界与权威指针一致性。

1. **证据链结构正确但覆盖不全。** 3 条 Canonical Evidence 的 `path`/`commit`/`sha256`/`class` 全部真实可复现（我在 commit blob 上重算，非仅 worktree）。但 `E-C08-R12` 的 `AC/Gate` 列只写 `AC2,AC5–AC7`，而 AC1、AC3、AC4 三条 AC 同样标 `<<MET>>` 却没有任何**证据项指向**——违反 §4.1 的"每个已释放 AC/Gate 指向一个当前证据项"。frontmatter `canonical_evidence_status: complete`（`:18`）因此是**未完全成立的完整性声明**。
2. **资源闭环与实况不符（最实质问题）。** Task 正文称"仓外 tmp 脚本用后即弃"（`:93`），单行表宣告 `NOT_APPLICABLE` 且"无待清理资源"（`:97`）；而 `G:\CODEX\New Manga.workspace\tmp\` 实际仍有 **32 个本次工作产生的脚本/产物**，其中至少 20 个直接服务于本 Task 的 AC1–AC9（`add_c08_d06.py` 是**生成被冻结契约字节**的脚本，另有 `update_c08_record.py`、`fix_c08_r9.py`、`fix_c08_r9b.py`、`fix_c08_rec.py`、`sync_c08_records.py`、`fix_r11.py`、`fix_s7.py`、`fix_ac8.py`、`fix_ac9.py`、`fix_matrix.py`、`fix_matrix2.py`、`fix_matrix_final.py`、`fix_tasks_d06_d07.py`、`extend_c09.py`、`reorder_c09.py`、`fix_c09_r3.py`、`fix_c09_k.py`、`c08pin.txt`、`c09_sha.txt`、`fix_1a_residual*.py`）。这不是"格式是否合法"的问题，而是**closeout 的事实基础不真**。
3. **写集合越界 + 新权威面。** 新增 `doc/checkpoints/AUTONOMOUS-2026-11-01.md` 不在 Task `allowed_paths`（`:21`–`:30`）内；`check.ps1` **完全不校验 `allowed_paths`**（`Select-String allowed_paths` 零命中），因此 PASS 不能作为范围合规的证据。该文件同时：①与 §5.2"不另建全局 checkpoint、优先放 `verification/<Task-ID>/`"冲突；②未被 `doc/STATUS.md` 指向，而 `00_INDEX:15` 把"当前恢复点"定义为"STATUS 指定的 rolling checkpoint" → 形成**未登记的第二个恢复点/状态面**；③`doc/checkpoints/` 是本次提交**新建**的目录（`git log --diff-filter=A -- doc/checkpoints/` 仅命中本 commit）。
4. **权威指针三方不一致（未由本 commit 引入，但本 commit 未闭合）。** reviewed_head 上：`doc/tasks/FEA-D06-GAP.md:6 = in_review`，而 `doc/STATUS.md` 仍写 `` `in_progress` ``、`doc/TASK_LEDGER.md:42 = in_progress`、`doc/REBASELINE_PLAN.md:48 = in_progress`。`check.ps1` 只在 STATUS 指向**终态** Task 时报错（`:633`），无法发现阶段不符。三份文件**都在 allowed_paths 内**，且 §4.2（`:97`）把指针更新列为 `done` 前动作——所以"本轮延后"可辩护，但 Closeout 未声明这一延后，读者会看到互相矛盾的两个状态。
5. **无代码/契约双权威复写**：本 commit 未复制任何契约正文，均为指针性引用，符合"唯一事实在权威源"。

## Verification（逐项，含真实输出）

运行环境：Windows，`pwsh -NoProfile`，workdir `G:\CODEX\New Manga`；HEAD = `12c63b92597c4b4ac367b6c204d5cd1a608fe315`，工作区 clean。

| # | 场景 / AC | 实际执行 | 结果 | 证据 |
|---|---|---|---|---|
| V-1 | `check.ps1`（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（3 warnings），EXIT=0** | 输出：`Governance scope: 15 current documents` / `Task: doc\tasks\FEA-D06-GAP.md` / 3 条 WARN（11 非终态 Task、STATUS 3159 B 80%、PLAN 6687 B 80%）/ `Governance check: PASS (3 warnings)` |
| V-2 | `check.ps1 -TaskPath` | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-D06-GAP.md` | **PASS（3 warnings），EXIT=0**（与 V-1 逐字相同——默认调用已把 STATUS 指针解析为该 Task） | 同上 |
| V-3 | `verify_pins.ps1` | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (all 13)，EXIT=0** | 13 行 OK：C01b 3c9f5af7d74f / C02 bb365ca891a7 / C03 b77e7968a00b / C04b 694ce5bc8c8b / C05 b34db8876879 / C06 b798dd8a9b38 / C07 17c8f7016a36 / C08 453f993c1a16 / C09 dc51226b336c / C11 44f4273f7ad1 / C12 f49835860143 / C13 d2cb8de4dd79 / C14 05056cbf65f9；`PIN AUDIT: PASS (all 13)` |
| V-4 | 证据 3 行的 commit blob 复算 | `git cat-file -e <commit>:<path>` + `git cat-file blob` 落 `$env:TEMP` 后 `Get-FileHash` | **PASS（3/3 一致）** | E-C08-R12 @`44667d836`→`4d2053ab…740ed`(len 6890)；E-D04D07-R3 @`2ed4ed91a`→`7baba549…7fac`(len 7081)；E-GATE-R3 @`0119a8014`→`f894839f…b313`(len 6713)。三者 worktree sha256 与该 commit blob **相同**，且 `git cat-file -e` 均 exit 0 |
| V-5 | 证据 commit 可达性 | `git merge-base --is-ancestor <c> 12c63b925` | **PASS** | 44667d836 / 2ed4ed91a / 0119a8014 均为 reviewed_head 祖先（exit 0） |
| V-6 | AC 标记完整性 | 正则统计 reviewed_head 与 delivery_head 两份 blob | **PASS** | `- [x]` = 9，`<<MET>>` = 9，`- [ ]` = 0（两个 head 均为 9/9/0） |
| V-7 | AC1 控制 pending 条款 | 抽查 pinned C-08 字节（sha256 `453f993c…`） | **存在性 PASS / 语义对照 NOT_RUN** | `doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md:68` `### SC-R06 控制 pending 状态`；`:70`/`:78` 含「安全边界」；**但无 canonical evidence 指向（R-001）** |
| V-8 | AC2 真实完成口径条款 | 同上 | **存在性 PASS / 语义对照 NOT_RUN** | `:80` `### SC-R07`；`:82`/`:101` 含「事件不是状态真值」；`:100` 含 `RunAccepted` 不证明完成 |
| V-9 | AC3 retry 快照来源条款 | 同上 | **存在性 PASS / 语义对照 NOT_RUN** | `:106` `### SC-R08`；`:110`/`:115` 含「快照来源」；`:113`/`:131` 含 `RetryFailedTargets`。**无 canonical evidence 指向（R-001）** |
| V-10 | AC4 断线 receipt 条款 | 同上 | **存在性 PASS / 语义对照 NOT_RUN** | `:125` `### SC-R09`；`:137`/`:139` 含 `request_id` 不作去重键的描述。**无 canonical evidence 指向（R-001）** |
| V-11 | AC5 UNFREEZE 载体 | `Test-Path` + 读 r12 结论 | **PASS** | `doc/reviews/CONTRACT-UNFREEZE-C08-2026-11-01.md` 存在；r12 结论「4 项全部到位」覆盖该载体 |
| V-12 | AC6 独立复核 approved（P0/P1=0） | 读 `doc/reviews/FEA-C08-r12.md` frontmatter | **PASS** | `verdict: approved`、`p0_count: 0`、`p1_count: 0`、`p2_count: 2`（K-1/K-2 非阻断）；`:22` 亦已把「最后一次独立复核」指向 r12 → r12 的 K-2 已闭合 |
| V-13 | AC7 重新冻结 pin | `verify_pins.ps1` + 直接复算 C-08 字节 | **PASS** | `Get-FileHash doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md` = `453f993c1a16eab9db783f5b3a24710ac6e24b9a290a2b05bcba45f463fa8517`，与 `verify_pins` 的 `OK C08 453f993c1a16` 一致 |
| V-14 | AC8 D04–D07 完整覆盖 | 读 `doc/reviews/FEA-D04D07-COVERAGE-r3.md` frontmatter | **PASS（仅核 verdict，覆盖语义未重做）** | `verdict: approved`、`p0_count: 0`、`p1_count: 0`、`p2_count: 2` |
| V-15 | AC9 `G-DELETE-CONTRACT` 判定 | 读 `doc/reviews/GATE-DELETE-CONTRACT-CLOSURE-r3.md` frontmatter + 裁定文件存在 | **PASS（仅核 verdict）** | `verdict: approved`、`p0_count: 0`、`p1_count: 0`、`p2_count: 1`；`doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md` 存在 |
| V-16 | `delivery_head: 0119a8014` 是否为"AC1–AC9 交付落盘提交" | `git show 0119a8014:doc/tasks/FEA-D06-GAP.md` 统计 | **PASS** | 该 commit 的 blob 已是 9×`[x]` + 9×`<<MET>>` + 0 未勾；`git show -s` subject = `chore(governance): 收尾——D06 task AC1-AC9 全 MET…` |
| V-17 | 冻结契约字节未被动 | `git diff 6358cfd05 12c63b925 -- doc/plan/` + 13 个受 pin 文件 blob 对比 | **PASS** | `doc/plan/` diff **为空**；13 个受 pin 文件（12 份 `FEA-C*_DRAFT.md` + `FEA-C07_API_INVENTORY.md`）base blob == head blob，逐项 `same=True` |
| V-18 | 未触碰其它 Task / 代码 | `git show --name-status 12c63b925` | **PASS** | 仅 `A doc/checkpoints/AUTONOMOUS-2026-11-01.md`、`M doc/tasks/FEA-D06-GAP.md`；本 commit 未改任何代码、M2-C1、其它 12 份契约、`doc/STATUS.md`、`tools/**` |
| V-19 | `allocation`：写集合是否在 allowed_paths 内 | 逐文件比对 `:21`–`:30` | **FAIL** | `doc/checkpoints/AUTONOMOUS-2026-11-01.md` 不在 allowed_paths（R-003） |
| V-20 | Resource Manifest 与实况一致性 | 扫 `New Manga.workspace` + `git worktree list` + `Test-Path verification/FEA-D06-GAP` | **FAIL** | `verification/FEA-D06-GAP` 不存在（与正文一致，✓）；无 FEA-D06-GAP worktree（✓）；但 `New Manga.workspace\tmp\` 有 **32** 个 2026-11-01 10:51–11:42 的脚本/产物，至少 20 个直接属于本 Task（R-002） |
| V-21 | `integration_commit: null` 是否诚实 | 读 `:16`、`:102` 与 check.ps1 `:743`–`:747` | **PASS** | `:102` 明写"`integration_commit` 与 `resource_closeout_status: complete` 在复核通过后的收口提交回填"；`in_review` 阶段空值是合法且被正确说明的 |
| V-22 | checkpoint 内容真实性 | 复算其两项可核事实 | **PASS（2/2）** | 「起始 HEAD `6358cfd05`」属实；「未 push 提交 246」= `git rev-list --count origin/main..6358cfd05` = **246** ✓（reviewed_head 为 247 且非 origin/main 祖先，未 push ✓）。注：origin/main 为本地引用、未 fetch，该数字仅对本地引用成立 |
| V-23 | 本地/远端状态（复核期间） | `git status --porcelain`、`git rev-parse HEAD` | **PASS** | 全程空 / 未变；本 Review 只写了本文件 |

**机器检查不代表语义合规**：V-1/V-2/V-3 全 PASS，但 R-001/R-002/R-003 三项均**不会被这三条命令发现**（`check.ps1` 不校验 AC↔evidence 覆盖、不校验 `allowed_paths`、不校验 STATUS↔Task 阶段一致）。本轮 PASS 不得被引用为这三项的合规证据。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | **P1** | `doc/tasks/FEA-D06-GAP.md:18`、`:87` | AC1/AC3/AC4 标 `<<MET>>` 但 Canonical Evidence 无任何行指向它们；同时 frontmatter 声明 `canonical_evidence_status: complete` → 完整性声明不成立，违反 09 §4.1「每个已释放 AC/Gate 指向一个当前证据项」 | `:87` 的 `AC/Gate` 列仅 `AC2,AC5–AC7`；全文无第二行 evidence；V-7/V-9/V-10 已证实三条 AC 有实际条款但无证据指针 | 把 `:87` 的 `AC/Gate` 改为 `AC1–AC7`（并在 Closeout 追加一句"AC1/AC3/AC4 的条款级语义由 r9→r10/r11→r12 链承载，本收口未重跑，见测试表注"）；若认为 AC5 需单独的载体证据，可再加一行指向 `doc/reviews/CONTRACT-UNFREEZE-C08-2026-11-01.md` | open |
| R-002 | **P1** | `doc/tasks/FEA-D06-GAP.md:93`、`:97` | 正文称"仓外 tmp 脚本**用后即弃**"、表行宣告 `NOT_APPLICABLE` 且"**无待清理资源**"；实况是 32 个本次脚本仍在 `New Manga.workspace\tmp\`（含生成被冻结契约字节的 `add_c08_d06.py`）→ closeout 的事实基础不真，违反 09 §4.2「逐项给出 disposition + 源/目标 + hash/manifest + 引用检查结果」；亦不符 WORKSPACE_GOVERNANCE 的 `temp/<TASK-ID>/` 分目录要求 | `Get-ChildItem 'G:\CODEX\New Manga.workspace\tmp' -File` → **32** 项，mtime 2026-11-01 10:51–11:42；其中 `add_c08_d06.py`(sha256 `746de56b…`)、`fix_ac8.py`(11:31)、`fix_ac9.py`(11:39)、`fix_matrix_final.py`(11:42)、`c08pin.txt`、`c09_sha.txt` 直接对应 AC1–AC9；`git worktree list` 无 FEA-D06-GAP；`Test-Path verification/FEA-D06-GAP` = False | 二选一：(a) 把这些脚本按 `temp/FEA-D06-GAP/` 归位并在 manifest 逐项（或分组+清单 manifest）记 `DELETE_SAFE`/`PRESERVE_UNKNOWN` + sha256 + 引用检查结果，删/留都要有记录；(b) 若确属跨 Task 共享残留，则 manifest 改为 `PRESERVE_UNKNOWN` 并点名 `New Manga.workspace\tmp\` 的清单文件，**不得**写"无待清理资源" | open |
| R-003 | **P1** | `doc/checkpoints/AUTONOMOUS-2026-11-01.md:1`（新增文件）；`doc/tasks/FEA-D06-GAP.md:21`–`:30` | ①写集合越界：该文件不在 frozen `allowed_paths`（09 §4.2 纪律：越界须暂停并在 Task 提出范围变更）；②形态违规：§5.2 要求 Task-local checkpoint、优先 `verification/<Task-ID>/`、"不另建全局 `CHECKPOINT.md`"，本文件是跨 6 项排队的全局载体；③新权威面：`00_INDEX:15` 定义"当前恢复点 = STATUS 指定的 rolling checkpoint"，而本文件**未被 STATUS 指向**，`doc/checkpoints/` 目录也是本 commit 新建（`git log --diff-filter=A` 仅命中本 commit）；④`check.ps1` 不校验 `allowed_paths`、也不扫描 `doc/checkpoints/` → 治理盲区 | `git show --name-status 12c63b925` → `A doc/checkpoints/AUTONOMOUS-2026-11-01.md`；`Select-String tools/governance/check.ps1 -Pattern allowed_paths` → **0 命中**；`git show 12c63b925:doc/STATUS.md` → 无任何 checkpoint 指针；`00_INDEX.md:15` 原文见上 | 三选一：(a) **推荐**：移入 `verification/FEA-D06-GAP/`（§5.2 首选位置，且已在 allowed_paths 内），并让 STATUS 指向它；(b) 删除该文件，把恢复所需信息并入本 Task 的 Closeout/Handoff；(c) 若坚持全局 checkpoint：必须由 DSH 在 `allowed_paths` 增列 `doc/checkpoints/**`（= 范围变更）+ 在 `00_INDEX` 与 `STATUS` 登记为当前恢复点，并说明与 §5.2 的关系 | open |
| R-004 | **P2** | `doc/STATUS.md`（未改）、`doc/TASK_LEDGER.md:42`、`doc/REBASELINE_PLAN.md:48` | 三处仍写 `FEA-D06-GAP … in_progress`，与 `doc/tasks/FEA-D06-GAP.md:6 = in_review` 矛盾；AGENTS.md 规定"STATUS 为唯一 Active Task 与运行状态权威"→ 读者会看到两个阶段。三份文件都在 allowed_paths 内，可同 commit 同步；§4.2 把指针更新列为 `done` 前动作，故"延后"本身可辩护，但 Closeout **未声明**这一延后 | `git show 12c63b925:doc/STATUS.md` → `` `in_progress`（**AC1–AC9 全 MET**，待收口动作…）``；`TASK_LEDGER.md:42` 与 `REBASELINE_PLAN.md:48` 同上；`check.ps1:633` 仅拦"STATUS 指向终态 Task" | 在 Closeout 追加一句"STATUS/PLAN/LEDGER 的阶段指针按 §4.2 在 `done` 收口提交一并更新（当前仍为 `in_progress`，属有意延后）"；或本轮就把三处改为 `in_review` | open |
| R-005 | **P2** | `doc/tasks/FEA-D06-GAP.md:20` | `evidence_dir: verification/FEA-D06-GAP` 指向**不存在**的目录（正文 `:93` 也承认"未创建"）；字段与实况不一致，且 `check.ps1:719`–`:737` 的 evidence_dir 漏登扫描因此被静默跳过（无 warning = 无信息） | `Test-Path verification/FEA-D06-GAP` → `False` | 置为 `null`（并保留正文说明），或真的创建该目录并存放本 Task 的判别力产物；两者择一，避免"声明了却不存在的证据目录" | open |
| R-006 | **P2** | `doc/tasks/FEA-D06-GAP.md:77` | AC5/AC6/AC7 合并为一行 `PASS`；三条 AC 语义不同（载体登记 / 独立复核 / 重冻），合并行使 §4.2「逐项 AC 证据」的逐项追溯变弱；且该行证据写"r12 approved"对 AC5 属间接（载体本身是另一文件） | `:77` 原文 `| AC5–AC7 | … | PASS | r12 approved；pin 453f993c… |` | 拆成三行分别给证据：AC5→UNFREEZE 载体路径；AC6→r12 frontmatter（p0=0/p1=0）；AC7→pin 值与 `verify_pins` EXIT=0 | open |
| R-007 | **P2** | `doc/tasks/FEA-D06-GAP.md:93`、`:95`–`:97` | 与用户口头要求「纯文本不建表（参考 FEA-GOV-11）」的偏离**未被显式登记**：正文只写"机械校验所需的最小登记"，未记录"用户要求纯文本 / `check.ps1` 对 `done` 强制 6 列或 JSON / 故由 DSH 判定加单行表"这一冲突与裁决依据 → 后续审计会把它读成静默偏离（**判定：格式本身不构成伪造，见下"对 Lead 提问的裁定" Q3**） | `:93` 原文只说"机械校验所需"；`check.ps1:782`（`resourceRows.Count -eq 0` → `DONE 必须逐项填写 Resource Manifest`）、`:786`（6 列）、`:793`（结果不得为空）为硬约束 | 在 Resource Manifest 段或 Closeout 补一句偏离登记：「用户口径=纯文本；`check.ps1` 对 `done` 要求 6 列表或 `verification/**` JSON 引用；经 DSH 判定采用单行 `NOT_APPLICABLE` 表，内容为真实无资源；如需纯文本须另立 governance Task 修改检查器」 | open |
| R-008 | **P2** | `doc/checkpoints/AUTONOMOUS-2026-11-01.md:15`–`:19` | 队列第 1–5 行全为"待填"，含尚未释放的 `FEA-C14-DRAFT` 收口、L-3 Errata、C-10 起草、PLAN 预算卫生；文件头 `:5` 写"每项完成即 commit"，容易被读成"已授权批次"，与 09 §5.1「下一任务建议不等于任务释放」相冲突的风险 | `:14`–`:19` 全为 `—`/`待填`；`REBASELINE_PLAN` 当前 DAG 未含 C-14/L-3/C-10 的释放记录 | 与 R-003 一并处理；若保留该文件，在头部显式加一行"本队列为计划记录，不是任务释放；释放仍须 STATUS 登记 + DAG 列表 + 范围冻结" | open |

**P0：无。** 本 commit 未改代码/契约字节、未动用户数据、未 push。

### 对 Lead 提问的裁定

**Q1（证据 3 行是否真在 commit 里、sha256 是否对得上）**：**PASS**。见 V-4/V-5——`git cat-file -e` 三条均 exit 0；对 `git cat-file blob` 落到 `$env:TEMP` 的字节重算，三份 sha256 与表内值**逐字相同**，且与 worktree 相同。这不是只在工作区对得上。

**Q2（AC1–AC9 全 `[x]` + `<<MET>>`；AC1–AC4 保留 `NOT_RUN` 是否诚实）**：**诚实，予以肯定**。9/9 勾选、9/9 `<<MET>>`、0 未勾（V-6）；AC1–AC4 未重跑就写 `NOT_RUN` 并加注"本收口没有重跑这些文档对照"，符合"未验证不得写成 PASS"红线；我另行抽查了 pinned C-08 的 SC-R06…SC-R09 确实存在（V-7…V-10），说明 `<<MET>>` 不是空指向。**但**：`<<MET>>` 的依据必须落在 Canonical Evidence 上（`check.ps1:840` 的报错文案即"依据应进 Canonical Evidence"），AC1/AC3/AC4 缺证据项 → R-001。

**Q3（单行 `NOT_APPLICABLE` 6 列表是否属"为过检查而伪造"）**：**不构成伪造，但内容不真（R-002/R-007 分开处理）**。
- 制度层：`check.ps1` 对 `done` 的 Resource Manifest 只接受"非空 6 列表"或"`verification/**` 单个 JSON 引用"（`:750`–`:783`、`:786`、`:793`）；JSON 路线同样要求 `resources` 非空（`:86`）与 `process_check` 非空（`:101`），所以"纯文本无表"在**现行检查器下不可满足**——这是检查器约束，不是作者可选偏好。你加单行表是**当前规则下唯一可行的合规写法**，且正文声明"不表示存在资源"、`source_path`/`destination`/`integrity` 均为 `-`（未虚构任何路径或 hash）。因此**格式与动机不构成伪造**。
- 但内容层：`NOT_APPLICABLE`+「无待清理资源」与实况不符（32 个 `tmp` 脚本仍在）→ 真正的缺陷是**资源事实**，不是表格式。修 R-002 后，这张表就是真实且合法的。
- 若你仍要满足用户"纯文本"口径，可行路径有三：①（推荐）保留单行表 + 在正文登记偏离（R-007 文案）；② 另立 governance Task 修改 `check.ps1`，允许"纯文本 `NOT_APPLICABLE` + 明确的检查结果句"通过——但 `tools/**` 不在本 Task allowed_paths，必须单独释放；③ 用 `verification/FEA-D06-GAP/resource-manifest.json`——注意这并不能省掉那一行（`resources` 不得为空、`NOT_APPLICABLE` 仍需 `process_check`），只是把同一行搬进 JSON，复杂度更高，不建议。

**Q4（`integration_commit: null` 是否说明清楚）**：**是，PASS**（V-21）。`:102` 明确"复核通过后的收口提交回填"，与 §4.2（`:76` 集成窗口、`:97` `done` 前门禁）及 `check.ps1:743`–`:747` 一致。唯一遗漏是指针延后未声明（R-004）。

**Q5（三命令实跑）**：**全 PASS，EXIT 均为 0**（V-1/V-2/V-3 逐字记录）。提醒：这三条命令**不能**证明 R-001/R-002/R-003/STATUS 一致性。

**Q6（13 份 draft 未改动）**：**PASS，但你的表述需更正**——`doc/plan/FEA-C*_DRAFT.md` 实际只有 **12** 份；第 13 个受 pin 文件是 `doc/plan/FEA-C07_API_INVENTORY.md`（无 `_DRAFT` 后缀）。合并算："13 个受 pin 的契约文件 base blob == head blob，全部 same=True"，且 `git diff 6358cfd05 12c63b925 -- doc/plan/` 为空（V-17）。另：本 commit 的实际文件清单为 2 项，**多出的那项是 `doc/checkpoints/AUTONOMOUS-2026-11-01.md`**（即 R-003）。

## Architecture / Verification 分面结论

- **Architecture：不通过（因治理面问题）**。证据链结构、pin 语义、AC 标记机制正确；但存在三处需修复的治理缺陷：证据覆盖不全（R-001）、资源 closeout 事实不真（R-002）、写集合越界并引入未登记恢复点（R-003）。
- **Verification：机器检查全 PASS，语义合规 3 项 FAIL**。`check.ps1`（默认与 `-TaskPath`）PASS/EXIT 0、`verify_pins.ps1` 13/13 PASS/EXIT 0、证据 sha256 3/3 复算一致、AC 标记 9/9、`doc/plan/` 零改动——这些可以引用；V-19/V-20 及 AC1/AC3/AC4 映射为 FAIL，不得以机器 PASS 覆盖。

## 结论与复审

**decision：`changes_requested`**（P0 × 0 / P1 × 3 / P2 × 5；P1 未闭合，不得 `approved`）。

**1 号复核未通过的原因不是"内容造假"，而是"收口材料的三处不完整/不真**：AC↔证据覆盖缺 3 条；资源清单与仓外实况矛盾；新增 checkpoint 越出 frozen 写集合且未登记为恢复点。三者均为**可在 1 个收口提交内修完**的事项（改 1 行 evidence 的 AC 列、把 tmp 脚本归位/登记、把 checkpoint 移入 `verification/FEA-D06-GAP/` 或删除）。

**复审要求**：

1. 修 R-001/R-002/R-003（P1）后，以**新 head** 再次进入 `in_review`；本报告对 `12c63b925` 的结论不延用到新 head（09 §6：分支随后变化不延用旧批准）。
2. R-004…R-008（P2）建议同批处理，尤其是 R-004（STATUS/PLAN/LEDGER 与 Task 阶段一致的声明）与 R-007（偏离登记）。
3. 复审时请一并确认：`git show --stat <新 head>` 的文件清单与 `allowed_paths` 逐项对应；`New Manga.workspace\tmp\` 的处置结果可复核（清单 + sha256）。
4. 本报告不构成 `approved`，也不构成任何实现/推送授权；复核本身未修改被审文件、未执行任何 git 写操作、未动冻结字节（`verify_pins.ps1` 13/13）。

—— 报告结束（`decision: changes_requested`；P0×0 / P1×3 / P2×5；机器检查全 PASS 但语义合规 3 项 FAIL）。
