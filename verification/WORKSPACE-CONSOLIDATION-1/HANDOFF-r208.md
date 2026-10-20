---
task_id: WORKSPACE-CONSOLIDATION-1
handoff_id: HANDOFF-R208
author: dsh
recipient: Codex
reviewer: Codex
base_commit: 3947d63447457fe3ef8d3587942e632724ab3d72
delivery_head: 198a9e440cf1626dec9c4bc31affbaf773d23706
status: rework_submitted_for_review
date: 2026-10-20
---

# Handoff：WORKSPACE-CONSOLIDATION-1（R208 返修）

## 0. 交付边界

- 本 Handoff 是 **返修提交说明**，不是 Review、不表示 Task 完成、不授予集成/删除/关闭权限。
- Task 保持 `in_review`；Reviewer 仍为 Codex；Owner 未自审、未自行批准、未关闭。
- 本轮未新增删除、移动、分支清理、历史改写、force、push、GC/prune；未重跑一次性 X6；未写回任何被删原路径。
- 本文件位于 `verification/WORKSPACE-CONSOLIDATION-1/`。**`doc/handoffs/` 不在本 Task 冻结 allowed_paths**，
  因此 Handoff 暂放 evidence_dir，未自行扩权；是否迁移到 `doc/handoffs/` 请 Integrator/Codex 裁定。
- 固定 head：返修由三个提交组成——内容提交 A（`198a9e44…`，全部返修文件与证据）、
  修正提交 C（Task AC7 kept 口径与 HANDOFF frontmatter pin 更正）、pointer-only 提交 D（仅更新 Task `delivery_head`）。
  **复审用固定 head = D**（D 的 SHA 见交付消息；D 中 Task 的 `delivery_head` = C，本文件 frontmatter 记录实现提交 A）。

## 1. 交付结果（按用户返修指令逐项）

| 用户要求 | 完成情况 | 证据 |
|---|---|---|
| 二、保全 P03 两个独有提交 | **已完成**：持久 archive tag + 增量 bundle + verify + 隔离恢复演练；无 -f、无覆盖 | `p03-preservation-r208.md` / `.json` |
| 三、重做事故影响台账（18 资源 / 15 删除根） | **已完成**：逐项 8 字段 + availability；P09 四条与 P06 子树纳入；六 worktree 只称部分重建 | `incident-ledger-r208.md` / `.json` |
| 四、修正当前记录 | **已完成（追加式）**：Plan、STATUS、Task、WORKTREE_SAFETY_INVENTORY Stage 8；AC1/AC2/AC6/AC9 与 AC3/AC7 重评；登记 r208 并解释第 4 条 warning | 四个文件 + `records-correction-r208.md` |
| 五、禁止项 | **全部遵守**：无新增删除/移动/清理/改写/force/push/GC/prune；未把 ignored 判为缓存；未凭治理 PASS/HEAD 相同/bundle verify 宣称完整 | `findings-disposition-r208.md` §5 |
| 六、交付 | 本 Handoff + findings disposition + 事故台账 + P03 证据 + 记录更正 + 治理原始输出；区分 executed/NOT_RUN/UNVERIFIED | 本目录各文件 |

## 2. AC 与 Task 状态（Review 裁定后的当前口径，不自行批准）

| AC | 当前记录 | 说明 |
|---|---|---|
| AC1 | `PARTIAL` | 表与总数可复算；缺未跟踪逐文件大小/引用表、缺 267 条已删分支原 tip；测试表 NOT_RUN 不能支撑 MET |
| AC2 | `PARTIAL` | Stage 7 已追加更正；原 126/“不忽略 ignored”/“永久丢失”等表述废弃 |
| AC3 | `PARTIAL / 保护目标 FAIL` | 18 个具体 source（15 删除根）受影响；57/57 只是名称子集 |
| AC4 | `MET（分支 payload）` | 76/76 manifest bundle verify；返修后 77/77；**增量 bundle 依赖前置**，非独立完整备份 |
| AC5 | `MET（抽验）` | 19 项祖先核验；56 个强删全部归档；其余 merged 项缺原 tip 映射 |
| AC6 | `PARTIAL` | 132 闭环成立；ignored 清册、原始 status/stash 输出、独有/终态/引用门槛不完整 |
| AC7 | `PARTIAL / 安全目标 FAIL` | 49.48 GiB 是删除前逻辑字节合计；物理净释放未证实；workspace/worktrees 实际移除 7 处 |
| AC8 | `MET` | 保留治理主线，不改名；19 条未合并分支均有归档 |
| AC9 | `PARTIAL` | 治理 PASS exit 0；fsck exit 0 但有 613 条 dangling；保护/恢复验收不成立 |

## 3. 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| R208-01 P03 对象与无 ref | `git cat-file -t` ×2；`rev-list 0a25ceb --not --all`；`for-each-ref --contains` | Git 2.52 / HEAD 3947d6344 | executed：对象存在；无 ref；恰 2 提交 | `p03-preservation-r208.md` §2 |
| R208-01 tag/bundle | `git tag archive/P03-review-prep-112495c7`；`git bundle create mainline..tag`；`git bundle verify`；`bundle list-heads` | 同上 | executed：exit 0；verify exit 0；4,391 B；SHA-256 4c2aef44…ddbee | `p03-preservation-r208.json` |
| R208-01 自包含性 | 空 bare 仓库 verify（无前置） | 系统临时目录 | executed：exit 1，缺前置 e33199902 | 同上 |
| R208-01 恢复演练 | 空 bare + `GIT_ALTERNATE_OBJECT_DIRECTORIES` + `fetch <bundle>`；`rev-list`/`diff --name-status` | 同上 | executed：fetch exit 0；2/2 提交；变更 2 文件 | 同上 §5 |
| 18 资源 / 15 根 | 只读扫描 + 原 Task/Manifest/Receipts 逐项核对 | HEAD 3947d6344 | executed：18 source、15 root；availability 6/1/3/8/0 | `incident-ledger-r208.md` / `.json` |
| 132 / 93 / 19 | `git worktree list --porcelain`；`show-ref --heads`；逐分支 `merge-base --is-ancestor` | 同上 | executed：132 / 93 / 19；19/19 tag+bundle+verify exit 0 | `measurements-r208.json` |
| 1223 / 320 | 按 `archive-manifest.json` 76 条循环 `rev-list mainline..tag` 求和/并集 | 同上 | executed：1,223 / 320（口径 A）；当前 77 tags = 1,225 / 322 | `records-correction-r208.md` §1 |
| 49.48 GiB 口径 | 两份 receipt `removed[].bytes` 求和 | 同上 | executed：53,129,852,873 B = 49.481031 GiB；物理净释放 UNVERIFIED | `measurements-r208.json` |
| 7 处 workspace/worktrees 移除 | 过滤 `worktree-removal.json` removed[] | 同上 | executed：7 处 / 13,225,660,979 B；4 处回建 | `records-correction-r208.md` §3.5 |
| task-envs 边界 | 递归 lstat 不跟 reparse | 同上 | executed：3,880,296,828 B；检测环境仅 138,129,041 B | 同上 §3.6 |
| X6 capture 副本 | `Get-FileHash` stdout.md / stderr.md | 同上 | executed：32,426 B / 0109aed4…a3602；0 B / e3b0c442…b855，与 pin 一致 | `incident-ledger-r208.md` SRC-13 |
| X6 selftest 可重建字节 | 内存构造 3 个固定内容文件并哈希；不落盘、不重跑 | Python 3.14.6 -B | executed：3 个 SHA 与两轮 pin 相符 | 同上 SRC-11/12 |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/WORKSPACE-CONSOLIDATION-1.md` | PowerShell 7.6.6 | executed：见 §4；exit 0 | 本文件 §4 |
| tools 修复 | — | — | **NOT_RUN**：无 tools/** 授权；建议范围见 `findings-disposition-r208.md` §R208-04 | — |
| 全盘/卷影/备份搜索 | — | — | **NOT_RUN**：无授权/工具边界 | — |
| 恢复写回原位置 | — | — | **NOT_RUN**：先映射后裁定，且不得覆盖现存文件 | — |
| 76/77 bundle 全量恢复演练 | — | — | **NOT_RUN**：只对 P03 新增 bundle 做隔离恢复演练 | — |

## 4. 治理检查原始输出

本段记录两个时点；均为只读命令，原样输出。

**Run A（返修文件已写入、Task 证据尚未登记时，2026-10-20）：**

```text
Shell: PowerShell
Governance scope: 13 current documents; no historical directory scan.
Task: doc\tasks\WORKSPACE-CONSOLIDATION-1.md
WARN: 存在 38 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3190 bytes / 25 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6251 bytes / 55 lines
WARN: evidence_dir 含未登记过程文件（归入 workspace 或列为 SOURCE_PIN）：G:\CODEX\New Manga\verification\WORKSPACE-CONSOLIDATION-1\codex-review-r208.md, G:\CODEX\New Manga\verification\WORKSPACE-CONSOLIDATION-1\findings-disposition-r208.md, G:\CODEX\New Manga\verification\WORKSPACE-CONSOLIDATION-1\HANDOFF-r208.md, G:\CODEX\New Manga\verification\WORKSPACE-CONSOLIDATION-1\incident-ledger-r208.json, G:\CODEX\New Manga\verification\WORKSPACE-CONSOLIDATION-1\incident-ledger-r208.md, G:\CODEX\New Manga\verification\WORKSPACE-CONSOLIDATION-1\measurements-r208.json, G:\CODEX\New Manga\verification\WORKSPACE-CONSOLIDATION-1\p03-preservation-r208.json, G:\CODEX\New Manga\verification\WORKSPACE-CONSOLIDATION-1\p03-preservation-r208.md
Governance check: PASS (4 warnings)
EXIT: 0
```

（该 warning 的未登记清单按检查器 `Select-Object -First 8` 截断；第 9 个未登记文件为
`records-correction-r208.md`。）

**Run B（Task 证据登记后、提交前）：**

```text
Shell: PowerShell
Governance scope: 13 current documents; no historical directory scan.
Task: doc\tasks\WORKSPACE-CONSOLIDATION-1.md
WARN: 存在 38 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3190 bytes / 25 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6251 bytes / 55 lines
Governance check: PASS (3 warnings)
EXIT: 0
```

解释：Run A 的第四条 warning 就是 `codex-review-r208.md` 等返修文件尚未登记到 Canonical Evidence。
Review 报告属于新增未跟踪文件，按原作者边界未 `git add`，只登记路径与 SHA-256。登记后该 warning 消失，
仅余三条既存 warning（38 个非终态 Task、STATUS 80%、Plan 80%）。最终以 Run B 为准。

## 5. 接收方式 / 复审入口

- 仓库：`G:/CODEX/New Manga`；分支：`antigravity/P09-AC3-DELETE-HARDEN-1`；主 checkout（未新建 worktree）。
- 复审固定 head：修正提交 C 的 pointer-only 后继 D（见交付消息）；`git show --stat` 应显示 A 含全部返修文件，
  C 只改 Task AC7 一行与 HANDOFF 两处，D 只改 Task `delivery_head` 一个字段。
- 关键文件：`verification/WORKSPACE-CONSOLIDATION-1/{codex-review-r208.md, p03-preservation-r208.md/.json,
  incident-ledger-r208.md/.json, records-correction-r208.md, measurements-r208.json,
  findings-disposition-r208.md, HANDOFF-r208.md}`。
- 复审建议顺序：① `git bundle verify` P03 bundle + 检查 tag；② 按 incident-ledger 抽查 18/15 计数与当前存在性；
  ③ 复算 132/93/19/1223/320/49.48 GiB/7 处；④ 核对 Plan/STATUS/Task/Inventory 更正是否与证据一致；
  ⑤ 确认没有新增删除/移动/GC 痕迹（HEAD 之外只应有本轮新增文件与四个文档的追加式修改）。
- 本轮**没有** push；没有集成；没有关闭 Task。
- 证据目录新增了本地 `.gitattributes`（`* text eol=lf`）：本目录文件以 SHA-256 登记在 Task Canonical Evidence，
  若在 `core.autocrlf=true` 的检出于新 clone 被转成 CRLF，pin 会失效（参见仓库根 `.gitattributes` 的 GOV-EOL-PIN-1 段）。
  该文件只固定本目录证据的换行，不改检查器、不改 Schema。

## 6. 下一任务建议（必填）

**无需下一步操作。** 原因：本 Task 的 P1 残余与不可恢复风险必须由 Codex 独立复审、由用户明确裁决；
在用户/Codex 给出裁决前，不得释放后续清理、恢复写回或 tools 修复 Task。

- Task ID / 标题：待 Codex 复审结论后由用户决定（候选：tools 保护修复、P09/P06 恢复能力调查；均未创建）。
- 推荐 Agent / Reviewer：若创建，实现 Agent 需非本次执行者；Reviewer=Codex。
- 推荐原因与前置依赖：前置是本次复审结论 + 用户对不可恢复残余的风险裁决。
- Recovery point：`G:/CODEX/New Manga`，branch `antigravity/P09-AC3-DELETE-HARDEN-1`，固定 head B；未创建新 worktree。
- 允许修改路径：未冻结；需在释放时由 Codex 明确。
- 禁止范围与新增授权条件：禁止删除/移动/GC/prune/push；禁止在未冻结前修改 `tools/**`。
- 交付物：待 Task 释放时定义。
- 验证命令、环境与完成 Gate：由后续 Task 定义；本轮证据可作为输入。
- 可直接转发给 Agent 的指令：暂无可安全转发的指令（等待复审与用户裁决）。

## 7. 风险与遗留

1. **不可恢复残余**：7 个 temp 路径与 4 个 P09 review-scratch 原位置缺失；仅 X6 capture 有同哈希副本、
   两轮 selftest 固定字节可精确重建；其余恢复能力未证实，不得称“永久不可恢复”。
2. **ignored 内容缺口**：六处重建 worktree 与其他被删目录无删除前逐文件清册；不得认定为缓存，也不得反证删除前为空。
3. **P06 `old-runtime/worktree`**：受保护子树缺失，父根仍在；旧 runtime 产物是否可重建未证实。
4. **增量 bundle**：76 个原 bundle 与 P03 新 bundle 均依赖前置对象历史；不是可在空仓库独立恢复的完整备份。
5. **统计口径**：49.48 GiB 是删除前逻辑字节合计，不是物理净释放；1,223 是分支计数合计、去重 320。
6. **记录更正方式**：Plan/STATUS/Task/Inventory 只做追加式更正，历史 pin、旧 Review、原清册未改写；
   如需改写历史记录，必须另获授权。
7. **回退方法**：本轮没有删除/移动；如需回退，仅移除新增的 P03 tag/bundle 与新增证据文件，
   但 P03 tag/bundle 在获准前**不得**移除（GC 风险）。任何回退需 Codex 明确指令。
