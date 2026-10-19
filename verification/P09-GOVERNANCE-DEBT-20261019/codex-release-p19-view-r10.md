# P19 兼容视图后继 Task 释放裁定（r10）

日期：2026-10-19
事实基线：主 checkout `G:\CODEX\New Manga`，当前 HEAD `cf4529297f4e38fcde0bbc51784ec301ddbdeb35`；Manifest 检查器集成提交 `3fe78a67c`。本文件是释放准备与顺序说明，不替代 Codex 对 Task、Plan、STATUS 的正式落盘和 Gate。

## 3.1 范围裁定

### 仅改 P19 Task 的 Resource Manifest 节

允许改动严格限于 `doc/tasks/P19-UI-FIX-1.md` 的 `## Resource Manifest` 节正文：把当前 Markdown 链接改成检查器识别的、反引号包裹的仓库相对 JSON 路径。不得改 frontmatter、AC、Canonical Evidence、测试记录、其他章节或 Task 状态。`allowed_paths` 对该文件的授权不代表可编辑整个文件；Acceptance Criteria 明确把写入范围收窄到这一节。

不改 `verification/P19-UI-FIX-1/resource-manifest.json`，也不改任何历史证据文件、证据 pin、工作区资源或其他 Task。源 JSON 当前已由已集成检查器/schema 支持，不是本次兼容视图缺陷的来源。

### 三个既存 FAIL 不纳入范围

两项 `Evidence SHA-256 不匹配` 与一项 `DONE evidence_dir 含未登记文件` 均不属于本 Task。它们分别涉及两个历史日志的内容与 P19 DONE evidence 目录清单；修正散文引用不会也不应通过重钉 pin、改写日志或扩充历史清单来处理它们。须在本 Task 的验证证据中记录 P19 检查由 4 项错误减为且仅减为这 3 项，并明确 P19 Task 检查仍为 FAIL。

建议本 Task 完成后状态为 `done`，而非 `closed_with_limitations`：本 Task 唯一已释放 AC 是兼容引用修正，且该 AC 完整通过；P19 留下的三个历史错误是明确排除在范围外的既存问题，并不构成本 Task 未完成的 AC。`done` 只表示本窄范围 Task 已完成，不得写成 P19 检查 PASS、P19 所有历史债务已清偿或 P19 可重新释放。若验证发现额外错误、指定错误未消失，或本 Task AC 未全通过，则不能 `done`；先回到 Codex 裁定范围，不能自行扩围。

## 3.2 可整体落盘的 Task

建议 ID 为 `P19-UI-MANIFEST-VIEW-1`。此任务只依赖 `GOV-RESOURCE-MANIFEST-JSON-1`：它提供本 Task 所需的已集成引用解析能力。P19-UI-FIX-1 是被修订的历史 Task/输入对象，不是待重新执行的前置 Task；不要把 P19 加为 `depends_on`。

`base_commit` 采用完整当前 HEAD `cf4529297f4e38fcde0bbc51784ec301ddbdeb35`。`3fe78a67c` 是集成提交，但用户提供的事实明确主 checkout 已在后续 HEAD `cf4529297`；选当前 HEAD 才能把基线绑定到实际包含集成检查器的当前主线状态，而不假设中间后续状态。释放前 Codex 仍须核实该对象存在并包含 checker；若主线 HEAD 已变化，重新冻结完整 hash、branch/worktree 与允许路径后再释放。

以下 Task 的 `ready` 仅在 Codex 已将其登记入 Plan DAG 和 READY 声明、在 STATUS 加入 READY/待派指针、核实依赖/基线/Owner/Reviewer/路径并通过权威检查后生效。Owner 与 Reviewer 不同。

````markdown
---
id: P19-UI-MANIFEST-VIEW-1
title: P19-UI-FIX-1 Resource Manifest 兼容视图修正
kind: documentation
governance_version: 2
status: ready
approval: coordinator_release_20261019_after_GOV-RESOURCE-MANIFEST-JSON-1_closeout
suggested_owner: DeepSeek Harness
owner: dsh
reviewer: antigravity
depends_on: [GOV-RESOURCE-MANIFEST-JSON-1]
base_commit: cf4529297f4e38fcde0bbc51784ec301ddbdeb35
branch: dsh/P19-UI-MANIFEST-VIEW-1
worktree: G:/CODEX/New Manga.workspace/worktrees/P19-UI-MANIFEST-VIEW-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P19-UI-MANIFEST-VIEW-1
allowed_paths:
  - doc/tasks/P19-UI-FIX-1.md
  - verification/P19-UI-MANIFEST-VIEW-1/
  - doc/handoffs/P19-UI-MANIFEST-VIEW-1-*.md
  - doc/reviews/P19-UI-MANIFEST-VIEW-1-*.md
---

# P19-UI-MANIFEST-VIEW-1：P19 Resource Manifest 兼容视图修正

## 来源与目标

已集成 `GOV-RESOURCE-MANIFEST-JSON-1`（集成提交 `3fe78a67c`）的检查器开始解析 `P19-UI-FIX-1.md` 的 Resource Manifest 节。当前节使用 Markdown 链接，检查器按反引号 JSON 路径规则提取出的却是裸文件名 `resource-manifest.json`，从而报 `Resource Manifest 引用必须位于 verification/**`。目标是在不改 P19 其他内容和源 JSON 的情况下，把引用改成唯一的仓库相对路径 `verification/P19-UI-FIX-1/resource-manifest.json`。

## Acceptance Criteria

- [ ] **AC1 唯一正文改动**：只替换 `doc/tasks/P19-UI-FIX-1.md` 中 `## Resource Manifest` 节的正文引用；不改 frontmatter 或其他章节。新正文准确采用本 Task「精确替换文本」所列内容，保留工作区资源保留、删除计数及 6 个日志仅在证据目录内改名的原说明。
- [ ] **AC2 检查器识别仓库相对路径**：运行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P19-UI-FIX-1.md`。证据须显示 `Resource Manifest 引用必须位于 verification/**` 已消失，且被解析目标为 `verification/P19-UI-FIX-1/resource-manifest.json`。本次预期该命令仍因 AC3 列出的三个已知历史问题以非零码失败；不得记作 PASS。
- [ ] **AC3 错误集合限定且如实报告**：保存命令完整 stdout/stderr 与 exit code。结果恰为两项已知 `Evidence SHA-256 不匹配`（`frontend-npm-test-final.log`、`frontend-npm-build-final.log`）及一项已知 `DONE evidence_dir 含未登记文件`（原有 8 个 `04-settings-*/app-err-*` 文件）；没有新的错误。记录基线 4 项到变更后 3 项的对照，结论为 P19 检查仍 FAIL。
- [ ] **AC4 源 JSON 和历史证据不变**：记录 `verification/P19-UI-FIX-1/resource-manifest.json` 变更前后 SHA-256 相同；确认两个触发 SHA 错误的日志、8 个未登记文件、P19 的 Canonical Evidence/pins 均未被本 Task 改写或重钉。
- [ ] **AC5 改动面与资源安全**：记录交付 diff 仅含 P19 Task 的 `## Resource Manifest` 正文和本 Task 明确允许的 Handoff/Review/evidence 产物；不改源 JSON，不改历史证据文件，不重钉 pin，不删、不移或归档资源。任何意外文件变化均停止并交 Codex 裁定。
- [ ] **AC6 交付与复核**：在 `verification/P19-UI-MANIFEST-VIEW-1/` 留存变更前后文本/diff、上述可复核检查记录及退出码；提交 Handoff；由非作者 Antigravity 独立 Review 固定的 `delivery_head`，明确审查本 Task 的单节范围与预期残余 FAIL。Review 和 Codex 集成/集成后检查通过后才允许 Codex closeout 为 `done`。

## 精确替换文本

把 P19 Task 当前 `## Resource Manifest` 下的散文正文整体替换为以下一段（保留该节标题）：

> 外部清单：`verification/P19-UI-FIX-1/resource-manifest.json`。worktree、构建产物、隔离数据和源数据均保留；删除 0 项。6 个旧成功运行日志仅在证据目录内改名以防覆盖。

路径必须保持反引号包裹、无空格、完整仓库相对路径；不要使用 Markdown 链接，也不要在本节另加会匹配为 JSON 引用的旁支表达。保留原有资源处置说明有助于保持事实语境且不会扩大写入范围，只留引用不建议。

## 允许修改范围

- `doc/tasks/P19-UI-FIX-1.md`：仅 `## Resource Manifest` 节正文。
- `verification/P19-UI-MANIFEST-VIEW-1/`：本 Task 的判别力证据，必须纳入 `allowed_paths`。
- `doc/handoffs/P19-UI-MANIFEST-VIEW-1-*.md`、`doc/reviews/P19-UI-MANIFEST-VIEW-1-*.md`：本 Task 自己的交接和独立审查记录。允许这些 Task 专属路径；不授权改写其他 Task 的 Handoff/Review。
- Branch/worktree 为释放时规划值；Codex 按协作协议创建/确认工作区。路径若实际不可用，先由 Codex修订 Task 与权威登记，不得另选未登记目录。
- Plan、STATUS、Task README/导航及生命周期字段由 Codex按协作协议更新，不是 Owner 的实现写权限。

## 禁止范围

- 不改 `verification/P19-UI-FIX-1/resource-manifest.json`。
- 不改 P19 的 frontmatter、其他章节、Canonical Evidence、pins 或任何历史证据文件；不得修补证据哈希或登记/搬动 8 个历史未登记文件。
- 不重钉、删除、移动、归档资源；不改 `tools/**`、`src/**`、`tests/**`、Schema、依赖、Plan/STATUS 或其他 Task。
- 不得把 P19 Task 检查的预期 FAIL 写成 PASS，不得隐去三个已知残余错误或宣称 P19 Task 完全无错误。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC2/AC3 P19 指定 Task 检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P19-UI-FIX-1.md`；保存完整 stdout/stderr/exit code，并与修改前 4 错误基线比较 | Windows PowerShell 7；已集成 checker；检查器只读 | NOT_RUN；预期修复 1 项，余 3 项仍 FAIL | `verification/P19-UI-MANIFEST-VIEW-1/p19-task-check-after.log` 等 |
| AC4 JSON 源完整性 | 对源 JSON 及指定历史证据逐项记录 SHA-256/状态，修改后复核 | 仓库主线只读来源 | NOT_RUN | `verification/P19-UI-MANIFEST-VIEW-1/source-preservation.md` |
| AC5 单节改动面 | 查看精确 diff 与工作区状态，核对无越界路径/资源操作 | 固定 base 与交付 head | NOT_RUN | `verification/P19-UI-MANIFEST-VIEW-1/scope-diff.md` |

## 依赖、风险与阻塞

- 硬依赖：`GOV-RESOURCE-MANIFEST-JSON-1`，已集成并 closeout；checker 所需行为基线为当前主线 `cf4529297f4e38fcde0bbc51784ec301ddbdeb35`。
- P19 Task 的三项历史 FAIL 是已知范围外结果。若检查器结果与 AC3 预期不符，暂停并交 Codex adjudicate；不在本 Task 内修债。
- 修改 P19 DONE Task 的一个正文节不会将其重新打开；本 Task 的关闭状态与 P19 历史检查结果分开报告。

## 交付与运行记录

- Owner：DeepSeek Harness；Reviewer：Antigravity；Codex 负责释放核验、独立集成及 closeout。
- Handoff：`doc/handoffs/P19-UI-MANIFEST-VIEW-1-<short-head>.md`。
- Review：`doc/reviews/P19-UI-MANIFEST-VIEW-1-<short-head>-antigravity-r1.md`。
- Handoff 与 Review 固定完整 `base_commit`、`delivery_head`、`reviewed_head`、实际命令、环境、退出码与预期残余 FAIL。实际结果为 3 项既存 FAIL 时写明检查命令非零退出，不能称为 PASS。

## Canonical Evidence

进入 `in_review` 前，为 AC1–AC5 各登记可复核证据及含文件的 commit/SHA-256；AC6 以 Handoff、独立 Review 与固定 commit 证明。

| evidence_id | AC/Gate | path | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| P19VIEW-DIFF | AC1/AC5 | `verification/P19-UI-MANIFEST-VIEW-1/scope-diff.md` | 待交付 | 待计算 | CANONICAL |
| P19VIEW-CHECK | AC2/AC3 | `verification/P19-UI-MANIFEST-VIEW-1/p19-task-check-after.log` | 待交付 | 待计算 | CANONICAL |
| P19VIEW-SOURCE | AC4 | `verification/P19-UI-MANIFEST-VIEW-1/source-preservation.md` | 待交付 | 待计算 | CANONICAL |
| P19VIEW-HANDOFF | AC6 | 实际 Handoff 路径 | 待交付 | 待计算 | CANONICAL |
| P19VIEW-REVIEW | AC6 | 实际 Review 路径 | Review commit | 待计算 | CANONICAL |

## Resource Manifest

本 Task 的 worktree、日志和派生产物在 closeout 时逐项记录引用/进程检查；不确定项保留，不因本 Task 而删除或移动任何 P19 历史资源。按协作协议 §4.2 在 closeout 前完成准确清点，不将“未删除”描述成“资源不存在”。

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- `canonical_evidence_status`: `pending`。
- `resource_closeout_status`: `pending`。
- 删除、迁移、归档数量/字节数：待核实；按本 Task 禁止范围均应为 0。
- 未关闭项及保留原因：P19 源 Task 检查仍预期有三项历史 FAIL；不属于本 Task AC。
- 当前指针清理：由 Codex 在终态时更新 Plan / STATUS / Task 导航并运行 Task 检查。
````

## 3.3 Plan 登记与 READY

在 `GOV-RESOURCE-MANIFEST-JSON-1` 行之后新增一行：

```markdown
|P19-UI-MANIFEST-VIEW-1|GOV-RESOURCE-MANIFEST-JSON-1|ready（P19-UI-FIX-1 Resource Manifest 兼容视图；集成后仅消除引用格式错误）|
```

依赖只写 `GOV-RESOURCE-MANIFEST-JSON-1`，不写 `P19-UI-FIX-1`。前者是 checker 功能依赖；后者是要校正的历史对象，不是尚待完成的上游 Task。

更新 Plan 原 READY 行为：

```markdown
READY 节点：ARCH-DOC-REBASELINE、P20、P19-UI-MANIFEST-VIEW-1。in_review：HARDEN-2。done：**34 项**。
```

协作协议 §4 明确 Plan 是 DAG/READY 权威、STATUS 是唯一 Active Task/运行状态权威，并允许多个 READY 节点；当前已有 ARCH-DOC-REBASELINE 与 P20 两个 READY 项。因此新增 READY 声明不与“P20 是 STATUS 唯一 Active Task”冲突。Codex 还须在 STATUS 登记该 READY/待派 Task，但保留 `P20` 为唯一「当前 Task」；不要把本 Task 设为 Active，也不要移除其他 READY 声明。只有 Plan、STATUS、Task frontmatter 三者一致且治理检查 PASS 后才可派发。

## 3.4 P19 正文精确改法

保持标题 `## Resource Manifest` 不变，将该节原来这一段：

```markdown
见 [`resource-manifest.json`](../../verification/P19-UI-FIX-1/resource-manifest.json)。worktree、构建产物、隔离数据和源数据均保留；删除 0 项。6 个旧成功运行日志仅在证据目录内改名以防覆盖。
```

替换成：

```markdown
外部清单：`verification/P19-UI-FIX-1/resource-manifest.json`。worktree、构建产物、隔离数据和源数据均保留；删除 0 项。6 个旧成功运行日志仅在证据目录内改名以防覆盖。
```

必须保留原有保留、删除数与日志改名说明；仅留下路径虽能提供解析线索，却会丢失同一节原先记录的处置事实。路径用反引号包裹，无 Markdown 链接，且是 `verification/**` 下的仓库相对路径；源 JSON 字节与内容保持原样。

## DSH 按以下顺序落盘

1. **Codex 释放前核验**：只读确认 `GOV-RESOURCE-MANIFEST-JSON-1` 为 done、集成提交 `3fe78a67c` 可达，当前基线仍为完整 `cf4529297f4e38fcde0bbc51784ec301ddbdeb35` 且含 checker。核对 P19 当前检查基线四项错误及 JSON 文件现状；确认新 Task 文件 ID 不存在。若主线或错误基线不同，先更新本释放文档与 Task AC/基线，不自行假定。
2. **Codex 登记释放**：将上文 Task 整体写入 `doc/tasks/P19-UI-MANIFEST-VIEW-1.md`；在 Plan 新增唯一 DAG 行并替换 READY 声明；在 STATUS 登记 READY/待派指针，同时保持 P20 为唯一 Active Task。填实已核验的 owner/reviewer、完整 base、branch、worktree 和 allowed_paths。执行 `pwsh -NoProfile -File tools/governance/check.ps1` 与 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P19-UI-MANIFEST-VIEW-1.md`；权威检查失败时不派发。
3. **DSH 认领与 Reality Check**：在指定 linked worktree/branch 核对 base、head、工作区 dirty/untracked 内容及 STATUS/Plan 当前指针；不覆盖任何他人内容。确认认领后由 Codex 将 Task 置 `in_progress`。Owner 只在 Task 的 `allowed_paths` 内工作。
4. **DSH 修改和留证**：先保存 P19 原节文本及源 JSON hash；只编辑 P19 Task 的 Resource Manifest 正文为 3.4 指定文本。运行 AC2 命令，完整保存 stdout、stderr、退出码和输出对照；复核预期为引用格式错误消失、仅留 AC3 的三项历史 FAIL。检查源 JSON 和历史证据未变，不修改任何 pin/证据目录清单、不删移资源。证据写入 `verification/P19-UI-MANIFEST-VIEW-1/`。
5. **DSH 交付**：逐项完成 AC1–AC5 并将证据 pin 写入 Task；生成规定路径 Handoff，固定 delivery head，状态转 `in_review`。明确 P19 检查仍 FAIL（预期 3 项），不要写全绿。
6. **Antigravity 独立 Review**：以精确 base/delivery head 审查单节范围、路径解析、错误集合对照、源 JSON/历史证据保护和 Handoff。Reviewer 不得是作者。finding 要求修改时由 Owner 修订并以新 head 重审。
7. **Codex 集成与 closeout**：Review 批准后由 Codex 集成，重跑新 Task 指定检查和必要的 P19 检查；逐项核实差异及 Resource Manifest、pins、evidence_dir、集成提交与资源留存。集成后 P19 检查仍有三项历史 FAIL 需在 closeout 明记；本 Task 所有 AC 和资源 closeout 完成后，Codex 才能设置 `done` 并更新 Plan/STATUS/导航指针。

## 本文件写入前后工作区状态

写入前与写入后状态必须由同一轮 PowerShell 采样比较：记录 `git status --porcelain` 的行数与 UTF-8 行文本 SHA-256，并核对除本文件新增路径外的条目完全相同。预期唯一新增项为 `?? verification/P09-GOVERNANCE-DEBT-20261019/codex-release-p19-view-r10.md`；已有的其他 dirty/untracked 项全部保留。不得以整个工作区非 clean 阻止本次只写授权文件，但必须在实际状态对照中明确数量与指纹。

实际采样结果（同一 PowerShell 会话）：

| 时点 | 行数 | SHA-256（状态行文本 UTF-8，行间 LF） |
|---|---:|---|
| 写入前 | 1235 | `1EC39ACEE7E3CD9EBD8390DC0B1A6417262476C3D53166FCCD53DFC9C31044FD` |
| 写入后 | 1236 | `4F395C73149E1A82921505D71DDE1A099CA3025B01AABECA3F45F10B4A9D903F` |

唯一新增项：`?? verification/P09-GOVERNANCE-DEBT-20261019/codex-release-p19-view-r10.md`。剔除该目标行后前后状态集合差异为 0；其他既有 dirty/untracked 项全部保留。
