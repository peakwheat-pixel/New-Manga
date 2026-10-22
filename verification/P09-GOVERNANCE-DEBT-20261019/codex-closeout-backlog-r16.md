# GOV-UNTRACKED-BACKLOG-1 Closeout adjudication r16

日期：2026-10-20  
裁定者：Codex（Lead / Architect / Integrator）  
主 checkout：`G:\CODEX\New Manga`  
branch：`antigravity/P09-AC3-DELETE-HARDEN-1`  
当前 HEAD：`94efecc75a3132d6f4b1e76fc66a18c9f2912e8b`

## 结论摘要

- 交付范围的 AC1–AC6 均为 `[x]`，独立 Review 对 `a2f411a68` 给出 `APPROVED`，没有 P0；当前证据文件的 SHA-256 都与任务 pin 相符。
- Review 的 P1 所述跨 worktree 行尾风险属实：`core.autocrlf=true`，本 Task 证据路径的 `text/eol` 属性目前均为 `unspecified`。本 checkout 的索引与工作树文件都是 LF，当前 hash 没有失配。
- **P1 修复不属于本 Task**：AC5 明确禁止改 `.gitattributes`，该禁止也适用于 Codex closeout。Owner 遵守 AC5 是正确的。应新建独立、范围冻结的行尾治理小 Task；修复完成和复核前，本 Task 不宜从 `in_review` 进入 `done`。不应使用 `closed_with_limitations`，因为该状态不适用于 AC 全部达成但仍有一项待修的可修复 P1，也不能把 P1 标成已解决。
- 本文件仅为裁定记录；按本轮授权，未改 Task、Review、Plan、STATUS、`.gitattributes` 或任何既有证据，没有运行 Git 写命令。

## 1. Head 与状态裁定

| 指针 | 裁定值 | 说明 |
|---|---|---|
| `reviewed_head` | `a2f411a6894c7de351173695519fd1b640cbdbc4` | Review frontmatter 固定的被审查交付 head；P1 的后续修复不能覆盖或改写此值。 |
| `delivery_head` | `a2f411a6894c7de351173695519fd1b640cbdbc4` | 已修正 handoff pin 的交付提交，也是 Review 的精确目标。不要改成含 Review 的当前 HEAD。 |
| `integration_source_head` | `a2f411a6894c7de351173695519fd1b640cbdbc4` | 本 Task 直接在主 checkout，没有独立来源分支/worktree；交付来源即该固定提交。 |
| 当前主 checkout HEAD | `94efecc75a3132d6f4b1e76fc66a18c9f2912e8b` | 含 Review 落盘及后续仓库提交，不因此变成 `delivery_head`。 |
| `integration_commit` | **`null` / 不适用** | 无 merge、cherry-pick 或本 Task 专属集成提交；直接在主 checkout 做 closeout 不得把当前 HEAD 冒充 integration commit。之后若为独立 P1 Task 产生新提交，也不能回填为本 Task 的集成提交。 |

终态当前**不可登记**：保持 `in_review`，直到独立 P1 修复 Task 完成并通过独立 Review、集成后校验，或 Codex 按协作协议形成有根据的重审裁定。届时若风险已修复，建议终态为 `done`；若经复核确认跨 worktree pin 风险不影响本 Task 的 Gate 且由单独 Task 明确承接，可再判断是否满足 `done`。`closed_with_limitations` 不是当前建议。

## 2. Canonical Evidence 与 Resource Manifest

### Canonical Evidence

任务表现有 6 行：5 份 `verification/GOV-UNTRACKED-BACKLOG-1/` 文件（AC1、AC1-JSON、AC2、AC3、AC4）及一份 Handoff（AC6）。我逐个计算的 SHA-256 与表内登记值一致；`git ls-files --eol` 显示索引和工作树均为 `lf`。本次没有发现 hash 漂移。

- 本次 closeout Review 是 AC6 审查结论的来源文件，并已由 Task frontmatter 的 Review 指针引用。若后续实际编辑 Task 表完成生命周期收口，建议加一行 Review 证据（路径 `doc/reviews/GOV-UNTRACKED-BACKLOG-1-a2f411a68-antigravity-r1.md`，commit 为包含该文件的实际 commit，SHA-256 为执行 closeout 时计算的值），避免把 Reviewer 报告误当作 Handoff。
- 不因 `.gitattributes` 修复而重算现有证据 SHA-256。`text eol=lf` 改变检出规范化规则，不改变这些现有 LF 内容的字节或预期 pin；只有实际文件内容发生变化时才应重算对应 hash。也无需对这 6 项更换 introducing commit。
- 当前数据：5 份 evidence 的文件 hash 与 pin 相等，handoff hash 为 `bd978b7d2865dde1865260ce147fb4e71a9115a4e54680829701ff5d06eefed6`，与任务表相等。

### Resource Manifest

现有 4 行已分别记录 backlog、`CON`、Task evidence dir、agent output。Review 报告是审查证据，不是派生产物资源；无需添加为 Resource Manifest 行。`.gitattributes` 是版本控制配置，不属于本 Task 已盘点的派生资源，且本 Task 无权修改；无需加入本 Task 的资源表。独立 EOL Task 应在自己的 Resource Manifest 评估规则变更和其验证产物。

## 3. `.gitattributes` 行尾风险与独立修复方案

### 裁定与范围

现有先例证明为 hash-pinned evidence 固定 LF 是项目已采用的治理模式。该修复技术上合理，但 `GOV-UNTRACKED-BACKLOG-1` 的 AC5/禁止范围明文规定“不改 `.gitattributes`”，所以不能以“Codex closeout”名义在本 Task 内实施。应由 Codex 建立独立小 Task，明确授权仅追加下列规则、检查 attributes 与 clean checkout pin 可复现性；再分配实现者和不同 Reviewer。该 Task 不是本报告当前执行的授权。

### 建议追加内容和位置

在 `.gitattributes` 文件末尾追加，作为独立、带注释的规则组（保留现有内容及其分组）：

```gitattributes

# GOV-UNTRACKED-BACKLOG-1: canonical evidence and handoff files are SHA-256 pinned.
# Keep LF on checkout so pins remain reproducible when core.autocrlf=true.
verification/GOV-UNTRACKED-BACKLOG-1/** text eol=lf
doc/handoffs/GOV-UNTRACKED-BACKLOG-1-*.md text eol=lf
```

### 独立 Task 获准后的命令序列

在有该 Task 授权、正确分支/工作区并确认没有覆盖他人改动后，按顺序执行；以下是**建议命令，不是本次已执行命令**：

```powershell
git status --short
git check-attr text eol -- verification/GOV-UNTRACKED-BACKLOG-1/ac1-ac3-composition-and-references.md doc/handoffs/GOV-UNTRACKED-BACKLOG-1-60970cf9d.md
# 追加上述规则后：
git add --renormalize -- verification/GOV-UNTRACKED-BACKLOG-1/ doc/handoffs/GOV-UNTRACKED-BACKLOG-1-60970cf9d.md
git diff --cached --check
git diff --cached -- .gitattributes verification/GOV-UNTRACKED-BACKLOG-1/ doc/handoffs/GOV-UNTRACKED-BACKLOG-1-60970cf9d.md
git ls-files --eol -- verification/GOV-UNTRACKED-BACKLOG-1/ doc/handoffs/GOV-UNTRACKED-BACKLOG-1-60970cf9d.md
Get-FileHash -Algorithm SHA256 -LiteralPath verification/GOV-UNTRACKED-BACKLOG-1/ac1-ac3-composition-and-references.md
Get-FileHash -Algorithm SHA256 -LiteralPath verification/GOV-UNTRACKED-BACKLOG-1/ac1-ac3-inventory.json
Get-FileHash -Algorithm SHA256 -LiteralPath verification/GOV-UNTRACKED-BACKLOG-1/ac2-anomalous-entries.md
Get-FileHash -Algorithm SHA256 -LiteralPath verification/GOV-UNTRACKED-BACKLOG-1/ac3-references.json
Get-FileHash -Algorithm SHA256 -LiteralPath verification/GOV-UNTRACKED-BACKLOG-1/ac4-worktree-mirror-guide.md
Get-FileHash -Algorithm SHA256 -LiteralPath doc/handoffs/GOV-UNTRACKED-BACKLOG-1-60970cf9d.md
```

`git add --renormalize` 会按新 attributes 重新规范化并 stage 指定的**已跟踪**路径，不会自动提交；审阅 staged diff，确认没有意外内容。本仓库目前这些文件 `i/lf w/lf` 且 pin 已匹配，因此预期 renormalize 不会改变六个 blob 或 pin；attributes 文件本身会是新增变更。若实际 hash 或 staged blob 有变化，先查明原因，不要为了通过检查盲目改 pin。验证阶段还应在新建的干净 linked worktree 中确认 `git ls-files --eol` 为 `i/lf w/lf`、6 个 pin 全通过，再跑 Task-scoped governance checker。

## 4. Plan / STATUS

当前 Plan 第 31 行仍把本 Task 记作 `in_progress`；应在**真正完成 closeout 后**替换为以下完整节点行，而不是现在提前标成终态：

```text
|GOV-UNTRACKED-BACKLOG-1|—|done（1591 个未入库文件的分类与边界化；只读盘点，不删不移；AC1–AC6 达成；跨 worktree LF 规则由独立 EOL Task 处理；closeout r16）|
```

本建议仅适用于 P1 独立处理并达到 done gate 后；若独立 Task 尚未释放或 P1 仍未裁定，节点不应从 `in_progress` 直接跳成 `done`。实际任务状态字段当前为 `in_review`，Plan 使用的 `in_progress` 是历史/不一致状态，需在未来 closeout 一并纠正。

`doc/STATUS.md` 目前没有本 Task、`GOV-EVIDENCE-UNIQUE-1` 或 `GOV-DEBT-CLEANUP-2` 的匹配指针；r15 后 STATUS 不复制 DAG 节点状态。因此本 Task 从非 Active 的 `in_review` 收口时，**STATUS 无需改动**。

## 5. 下一任务：GOV-EVIDENCE-UNIQUE-1

- Plan 将它列为 `ready`，依赖 `GOV-DEBT-CLEANUP-2`；后者为 `closed_with_limitations`。依赖条件不自动等同于“全 AC 技术完成”，但 Plan 已明确把 GOV-EVIDENCE-UNIQUE-1 列为 READY，且其范围是 AC7 唯一最终证据判定、只读 61 文件、不改 pin。就任务图释放条件而言，该依赖满足；需在新 Task 中引用 GOV-DEBT-CLEANUP-2 的 closure evidence，并明确哪些未完成 AC 不被继承或改写为 PASS。
- 在本 Task 尚未通过 closeout Gate 时，不应立即派发。先建立并释放上文独立 EOL 修复 Task（或由 Codex 形成等效的书面处置裁定），解决“进行中的主 checkout 改 `.gitattributes`”与“61 个文件只读判定”不能并发执行的写集冲突；之后核对 Plan/STATUS 权威指针、Owner/Reviewer、base、branch/worktree、allowed_paths 和 evidence_dir，并执行 coordinator 流程。按项目的故障转移规则，不分配 Qoder。
- GOV-EVIDENCE-UNIQUE-1 是只读证据审查，可在 EOL Task 完成后由 DeepSeek Harness 作为 Owner、Antigravity 作为独立 Reviewer；若实际范围含通用编码则由 Antigravity 承担实现。本轮未释放、未派发，也未运行 coordinator。

**可转发的后续准备指令（不是释放/派发授权）：**

> Codex：先按本裁定建立一个独立的 EOL 治理小 Task，范围仅覆盖为 `GOV-UNTRACKED-BACKLOG-1` 的 evidence 与 Handoff 固定 LF、renormalize 指定已跟踪文件、核对六个既有 hash，并在干净 linked worktree 运行 Task checker；明确不修改任务 evidence 内容、pins 或其他目录，配置独立 Reviewer。该 Task 完成并集成后，重新核对 GOV-UNTRACKED-BACKLOG-1 的 closeout Gate。随后若依赖 closure evidence 和 READY 条件仍成立，再按实际 Plan/STATUS 登记并释放 GOV-EVIDENCE-UNIQUE-1：DeepSeek Harness Owner、Antigravity Reviewer，范围只读 61 个指定 evidence 文件，不改任何 pin；固定真实 base/head 和 workspace 路径，逐项记录五项 AC、命令、逐文件结论及 NOT_RUN/BLOCKED。不要自行把 `closed_with_limitations` 解释成所有 AC 达成，也不要启动未释放 Task。

## 6. Git 状态对比与本次边界

写入本报告前运行 `git status --porcelain --untracked-files=all`，统计为 **1592 行：1 个已跟踪修改项、1591 个未跟踪文件**。已跟踪修改是 `.qoder-credits/report.json`；未跟踪文件是原有积压。此前所见的折叠视图不是逐文件状态。

本报告写入后应再次运行同一只读命令并比较：唯一新增应是本文件所属的未跟踪路径 `verification/P09-GOVERNANCE-DEBT-20261019/codex-closeout-backlog-r16.md`；`.qoder-credits/report.json` 仍是唯一已跟踪修改，其他 1591 个未跟踪文件不变。该新增报告使逐文件状态预期为 **1593 行：1 个已跟踪修改项、1592 个未跟踪文件**。若观察到除此之外的变化，应保留并报告，不要清理或覆盖。

本次实际写入范围限于本报告。未调用 `coordinator-lease.py`，未调用任何 Git 写命令，未删除/移动仓外文件。由于新增文件本身尚未入库，本报告当前没有可填写的 introducing commit；需在后续合法入库后再引用真实 commit。
