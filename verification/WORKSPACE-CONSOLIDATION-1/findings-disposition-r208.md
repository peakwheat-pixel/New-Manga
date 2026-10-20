---
disposition_id: R208-FINDINGS-DISPOSITION
task_id: WORKSPACE-CONSOLIDATION-1
author: dsh
reviewer_of_record: Codex
date: 2026-10-20
review_basis: verification/WORKSPACE-CONSOLIDATION-1/codex-review-r208.md
reviewed_head: 3947d63447457fe3ef8d3587942e632724ab3d72
rework_base_head: 3947d63447457fe3ef8d3587942e632724ab3d72
task_status_at_delivery: in_review
approval: none (Owner 不自行批准、不关闭 Task)
---

# R208 findings 逐项处置（dsh / WORKSPACE-CONSOLIDATION-1 返修）

## 0. 边界与口径

- 本文件是 **Owner 对 Reviewer findings 的逐项 disposition**，不是 Review、不是批准、不是关闭。
- Reviewer 仍为 Codex；Task 保持 `in_review`，最终是否接受由 Codex 与用户裁决。
- 所有状态只用三类：**executed**（本轮实际执行、有原始输出/可复算）、**NOT_RUN**（未执行，原因明确）、**UNVERIFIED**（没有可核实证据）。没有证据的项目一律不写 MET。
- 本轮没有新增删除、移动、分支清理、历史改写、force、push、GC/prune；没有重跑一次性 X6，也没有把任何内容写回被删除的原路径。
- 数字口径见 `records-correction-r208.md` 与 `measurements-r208.json`；事故逐项映射见 `incident-ledger-r208.md` / `.json`；P03 保全见 `p03-preservation-r208.md` / `.json`。

## 1. 总表

| ID | 级别 | 处置状态 | 一句话结论 | 证据 |
|---|---|---|---|---|
| R208-01 | P1 | **FIXED（保全完成，待 Review）** | P03 两个独有提交已建持久 archive tag 与增量 bundle，verify exit 0，隔离恢复演练恢复 2/2 提交 | `p03-preservation-r208.md` / `.json` |
| R208-02 | P1 | **MAPPED / 事件 open** | P09 四个 review-scratch 与 P06 `old-runtime/worktree` 已纳入 18 资源台账；未恢复、未写回；恢复能力未证实 | `incident-ledger-r208.md` SRC-02..06 |
| R208-03 | P1 | **CORRECTED** | 六个 worktree 只记为“原路径与 HEAD 部分重建”；不再使用“原样复原/永久丢失”混合口径 | `incident-ledger-r208.md` SRC-01/14–18 |
| R208-04 | P1 | **NOT_FIXED / 需冻结 tools 范围** | `clean_workspace.py` 的根因未改；按用户指令不自行扩权，提交具体建议范围给 Codex 裁定 | 本文件 §3.4 |
| R208-05 | P1 | **CORRECTED（追加式）** | Plan/STATUS/Task/Inventory 当前摘要与 AC 已追加更正，历史 pin/旧 Review/原清册未改写 | `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、Task、Inventory Stage 8 |
| R208-06 | P2 | **ACKNOWLEDGED** | 五个治理脚本当时不在冻结 allowed_paths；本轮不改 tools、不追溯授权，登记为范围偏离 | 本文件 §3.6 |
| R208-07 | P2 | **PARTIAL（可补部分已补，缺口明示）** | 补出 93 条当前 refs→完整 SHA、19 条未合并分支 tag/bundle/verify；248 条已删分支无原 tip，不能补造 | `measurements-r208.json`、`records-correction-r208.md` 附录 C |
| R208-08 | P2 | **CORRECTED** | 1223/320、77/1225/322、49.48 GiB 逻辑字节、7 处 workspace/worktrees 移除、task-envs 边界均已更正 | `records-correction-r208.md` §1–3 |
| 补充 | — | **OPEN / user decision** | 不可恢复残余、ignored 内容缺口、恢复写回范围均需用户/Codex 裁定 | 本文件 §4 |

## 2. 逐项处置

### R208-01（P1）P03 detached worktree 两个独有提交未归档

**Review 事实**：删除路径 `G:/CODEX/New Manga.worktrees/P03-review-prep-112495c7`，原 detached HEAD
`0a25ceb4577158d9dff184776ff4599e74e25c57`，含两个主线没有的提交，删除后无 ref、无已验证 bundle。

**本轮 executed**：

1. 复核对象仍存在：两个 SHA 的 `cat-file -t` = `commit`；`rev-list 0a25ceb... --not --all` 恰为两个提交；
   `for-each-ref --contains` 两 SHA 均为空；原 worktree 路径不存在。
2. 新建持久轻量 tag：`refs/tags/archive/P03-review-prep-112495c7` → `0a25ceb45...`（无同名冲突，未用 `-f`）。
3. 新建**增量** bundle：
   `G:/CODEX/New Manga.workspace/archive/bundles/P03-review-prep-112495c7.bundle`，
   4,391 B，SHA-256 `4c2aef444ab3974401dfe038c7cf26f289cb8dd370bfe6062dfb5d2d70fddbee`；
   `git bundle verify` exit **0**；前置依赖 `e3319990216699357c8b5a37c494010505535bb6`（在主线内）。
4. 自包含性：**否**。空 bare 仓库无前置时 verify exit 1（`Repository lacks these prerequisite commits`），
   已在证据中如实记录，不称“独立完整备份”。
5. 隔离恢复演练：空 bare + alternates 提供前置后 fetch exit 0，两个 commit 可读；
   `rev-list` 集合与 `mainline..tag` 逐 SHA 相等（2/2）；变更文件与 Review 记录一致：
   `doc/handoffs/P03-PACKAGED-SFX-ENTRY-140a6686-r3.md`、`verification/P03-PACKAGED-SFX-ENTRY/RESUME.md`。
6. 既有 76 个 bundle 未覆盖/未修改：目录 76→77 个文件，22,106,711→22,111,102 B，差值 4,391 B；
   既有文件 mtime 仍为创建时点。

**残余 / NOT_RUN**：原 worktree 目录、detached 检出形态、ignored 内容、目录元数据未恢复（无删除前逐文件清册）；
未做 GC/prune（按禁止项），未 push。恢复依赖前置对象历史，非自包含。

### R208-02（P1）P09 四个 review-scratch 与 P06 保留根子树受损

**本轮 executed**：纳入 `incident-ledger-r208.md` 的 SRC-02 与 SRC-03..06，逐项记录：

- 原 disposition：P09 四条均为 `PRESERVE_UNKNOWN`（源裁定 `verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/codex-resource-ruling.md` RX-01..RX-04，Task `P09-PREVIEW-LIFECYCLE-RECLAIM-1.md:165`）；
  P06 为 `PRESERVE_REFERENCED`（`doc/tasks/P06.md:127`、`verification/P06/resource-manifest.json` `$.resources[1].subdirectories[0]`）。
- 删除收据：P09 四条在 `workspace-cleanup.json`，合计 **14,699,110,702 B**；
  P06 子树在 `worktree-removal.json`，**2,186,496,184 B**，原 head `ad75fadc2944983b4322f353176ba70cf0b0b7ae`。
- 当前：P09 四路径不存在，父目录 `review-scratch` 为空；P06 父根仍在，`old-runtime` 存在但 `old-runtime/worktree` 不存在。
- 恢复来源：**NONE_PROVEN**（已记录搜索范围，包括父目录、workspace/archive 顶层、agent-output/coordinator；未做全盘/卷影/回收站/外部备份搜索）。
- 字节核验：P09 有原 pin（文件数/bytes/content SHA-256），当前无法复核；P06 原记录只有 subdirectory 名称与删除字节，无逐文件 pin。

**残余 / NOT_RUN**：未恢复、未写回原位置（写回需要先冻结范围与来源，且不得覆盖现存文件）；恢复能力未证实，
**不得称“永久不可恢复”**，也不得称“都是缓存”。

### R208-03（P1）六个 worktree 的“复原”表述与 disposition 错误

**本轮 executed**：`incident-ledger-r208.md` 逐项修正：

- 六个路径当前均存在且 HEAD 匹配 `inventory.worktrees[].head` 九位前缀，但 `symbolic-ref -q HEAD` 均失败 → **detached**；
  `status --porcelain -uall` 空、`ls-files --others --ignored --exclude-standard --directory` 空，但这只说明当前无可见内容，
  **不能反证删除前无 ignored 内容**。
- 原 disposition 纠正：仅 `GOV-PIN-LINEAGE-1/worktree` 是 `PRESERVE_REFERENCED`；
  `FEAT-CREATE-1/2/4`、`P19-UI-FIX-2`、`P02-real-webview-harness-antigravity` 是 **PRESERVE_UNKNOWN**（Review Q1 已指出）。
- 六处原记录字节合计 12,911,515,002 B；当前六处合计 1,812,799,148 B（约 14.04%），bytes 差额未逐项归因（NOT_RUN）。
- 表述固定为：“**原路径与 HEAD 的部分重建（PARTIALLY_RECONSTRUCTED）**；原分支检出、ignored 内容、目录元数据未恢复”。

**残余**：六处 ignored 内容/目录元数据无删除前清册；是否含用户数据未证实；不把重建说成原样复原。

### R208-04（P1）`clean_workspace.py` 等工具的保护判断缺陷

**本轮 NOT_FIXED（按授权边界）**：Task 的 `allowed_paths` 不含 `tools/**`；用户返修指令明确要求先提交具体范围给 Codex 裁定，
不得自行扩权。本轮**未修改任何工具、未运行任何清理/apply 路径**。

**提交 Codex 裁定的建议范围（未执行）**：

- 冻结文件：`tools/governance/clean_workspace.py`、`tools/governance/remove_worktrees.py`、
  以及（若需要同批）`tools/governance/delete_branches.py`、`archive_branches.py`、`consolidate.py`。
- 要求：路径身份 + 父子覆盖（保护根的任何后代都不得删）；解析/命令失败必须拒绝而不是计 0；
  `git stash list` 非零退出必须拒绝；删除前 ignored 逐文件清册/用途/来源；无破坏夹具（nested root、bare path、
  相对路径、非标准表格、PRESERVE_UNKNOWN、父目录保护、非 `/worktrees/` 命名）与失败注入测试。
- 本轮不创建工具修复 Task，也不把 Review 当作写授权。

### R208-05（P1）Plan/STATUS/Task/Inventory 当前摘要与 AC 过时

**本轮 executed（追加式更正，不改历史 pin）**：

- `doc/REBASELINE_PLAN.md`：WORKSPACE-CONSOLIDATION-1 行改为 `in_review / changes_requested（r208）`，
  写 132 worktree、76/77 bundle、49.48 GiB 逻辑字节、18 资源、AC 不能判 MET，指向更正底稿。
- `doc/STATUS.md`：当前 Task 行改为返修中与 r208 事实，删除“57/57 保护项在位”“释放约 49.5 GB”“9 AC 全 MET”等失效摘要。
- `doc/tasks/WORKSPACE-CONSOLIDATION-1.md`：AC1/AC2/AC3/AC6/AC7/AC9 重评（PARTIAL，均不判 MET），
  追加 r208 更正段、事故资源可用性表、Review 记录、Canonical Evidence 新证据登记、Closeout 更新。
- `doc/WORKTREE_SAFETY_INVENTORY.md`：Stage 7 顶部加“已被 Stage 8 更正”指针；追加 Stage 8 更正（132、93、19、1223/320、
  49.48 GiB 逻辑、7 处 workspace/worktrees 移除、task-envs 边界、18 资源、ignored 缺口）。
- 原 Review、原 pin、原清册、历史 commit 未改写；`codex-review-r208.md` 原文未动。

**说明**：AC4/AC5/AC8 保持 Review 认可的状态（分支 payload / 抽验 / 主线裁定），AC4 注明增量 bundle 依赖前置、
P03 另行保全，不据此宣称灾备完整。

### R208-06（P2）五个治理脚本不在冻结 allowed_paths

**本轮 ACKNOWLEDGED**：在 Task 的 r208 更正段与 Handoff 中如实登记：本轮清理新增/使用了
`consolidate.py`、`archive_branches.py`、`remove_worktrees.py`、`delete_branches.py`、`clean_workspace.py`，
当时冻结 allowed_paths 未含 `tools/**`；这是范围偏离，**不把历史授权反写成早已具备**。
本轮未继续修改工具；后续修复需 Codex 先冻结工具范围并独立 Review（见 R208-04 建议）。

### R208-07（P2）盘点缺未跟踪逐文件大小/引用表；分支缺原 tip

**本轮 PARTIAL**：

- **已补**：`measurements-r208.json` 记录 93 条本地分支完整 SHA（74 已并入 + 19 未并入）、19 条未合并分支的
  `archive/*` tag、tag tip == branch tip、bundle 文件与 verify exit 0；当前 77 个 archive ref 的 1,225/322 口径。
- **不能补**：inventory 没有未跟踪逐文件 sizes/references 表，也没有每个已删分支的删除瞬间完整 tip；
  267 个已合并删除项中仅 19 个能从 worktree 快照交叉定位原 head，**其余 248 个无法在删除后补造**。
- 不声称“四表齐全”为已验证事实；该缺口列入剩余风险，由用户/Codex 决定是否接受。

### R208-08（P2）统计口径与 disposition 叙述

**本轮 CORRECTED**（详见 `records-correction-r208.md`）：

| 原表述 | 更正后 |
|---|---|
| 1,223 个独有提交 | **76 个 manifest 分支归档 corpus** 的逐分支计数**合计** 1,223；跨 bundle **去重 320**。当前 77 archive refs = 1,225 合计 / 322 去重（含 P03 两提交），两口径不得混用 |
| 释放约 49.5 GB | 两份删除收据的**删除前递归逻辑字节合计** 53,129,852,873 B = 49.481031 GiB；无卷可用空间前后差值，**物理净释放未证实** |
| ARCHIVE（158 项派生产物） | 实际为 `shutil.rmtree` 删除，**无归档目的地**；原 disposition 标签不准确，已追加说明，不把它称“归档” |
| 213→126 worktree | 当前注册 **132**（213 − 50 − 37 + 6）；126 是回建前时点 |
| workspace/worktrees 未动 | 实际移除 **7 处**（FEAT-CREATE-1/2/4、P02-NEW-TIME-X6-AC1-AC7、P15-C1-review、P19-AC3-1、P19-UI-FIX-2），其中 **4 处回建** |
| 3.6 GB task-envs 是检测环境 | task-envs 总逻辑 3,880,296,828 B（3.613808 GiB）；检测环境 `M2-PROD-DETECT-ENV-1` 仅 138,129,041 B（131.73 MiB） |

## 3. 治理 warning 解释（第四条）

Review 写入后治理检查为 `PASS (4 warnings)`，第四条原文：

```text
WARN: evidence_dir 含未登记过程文件（归入 workspace 或列为 SOURCE_PIN）：G:\CODEX\New Manga\verification\WORKSPACE-CONSOLIDATION-1\codex-review-r208.md
```

原因：`codex-review-r208.md` 是 Review 的新增未跟踪文件，尚未登记到 Task 的 Canonical Evidence；
检查器按未登记文件报告。**不是**产品测试失败，也不是检查器错误。
本轮已在 Task 的 Canonical Evidence 中登记该 Review（`SOURCE_PIN`，SHA-256 pin），并同时登记返修证据；
注意：Review 文件为 Codex 所作且保持未提交状态（未跟踪内容归原作者），本 Task 不 `git add` 它，
只登记路径与 SHA-256。最终治理输出见 Handoff 的“治理检查原始输出”段。

## 4. 仍需用户/Codex 裁决的残余风险（本 Task 不自行接受）

1. **不可恢复残余**：7 个 temp 路径与 4 个 P09 review-scratch 原位置缺失；其中仅有 X6 capture 副本与两轮 selftest
   固定字节有恢复证据，其余恢复能力未证实。是否接受该风险、是否授权全盘/卷影/备份搜索，由用户裁决。
2. **ignored 内容**：六个重建 worktree 与其他被删目录的 ignored 内容无删除前逐文件清册；不得把它们直接认定为缓存。
3. **P06 `old-runtime/worktree`**：受保护子树的旧 runtime 产物是否可重建，尚无证据；需要 P06 Owner 与用户裁定。
4. **恢复写回原位置**：本轮只做映射，未写回；任何写回必须先冻结范围、来源与不覆盖现存文件的条件。
5. **tools 修复**：见 R208-04 建议范围，需 Codex 先冻结再实施。
6. **shared-root 泛化声明**：`SEC-FIX-PATH-ECHO-1.md:113` 对整个 workspace 根的 `PRESERVE_REFERENCED` 声明，
   机械祖先匹配会覆盖 168+1 个删除根；需要 Integrator 整合裁定，不能悄悄忽略，也不能当作 169 份独立工件丢失。

## 5. 本轮执行/未执行清单（便于独立复核）

| 项 | 状态 |
|---|---|
| P03 对象存在性、tag、bundle、verify、恢复演练 | **executed**（exit 0；证据见 p03-preservation） |
| 18 资源 × 字段台账、15 删除根映射 | **executed**（incident-ledger） |
| 132/93/19、1223/320、1225/322、49.48 GiB、7 处移除、task-envs、57/57 边界 | **executed**（measurements + records-correction） |
| AC1/AC2/AC6/AC9 重评（含 AC3/AC7） | **executed**（本文件 §2 R208-05 与 records-correction §4） |
| Plan/STATUS/Task/Inventory 更正 | **executed**（见各文件 r208 更正段） |
| 治理检查 | **executed**（PASS，exit 0；原始输出见 Handoff） |
| tools/** 修复 | **NOT_RUN**（无授权；建议范围已提交） |
| 全盘/卷影/回收站/备份搜索 | **NOT_RUN**（无授权、无工具边界） |
| 恢复写回原位置 | **NOT_RUN**（先映射后裁定） |
| bundle 恢复演练（76/77 全部） | **NOT_RUN**（只对 P03 新增 bundle 做了隔离恢复演练） |
| 重跑 X6 / 重建原 selftest 文件实例 | **NOT_RUN**（禁止；只做内存字节重建） |
| 删除/移动/分支清理/历史改写/force/push/GC/prune | **NOT_RUN**（全部禁止） |
