---
id: P19-UI-MANIFEST-VIEW-1
title: P19-UI-FIX-1 Resource Manifest 兼容视图修正
kind: documentation
governance_version: 2
status: in_progress
approval: coordinator_release_20261019_after_GOV-RESOURCE-MANIFEST-JSON-1_closeout
suggested_owner: DeepSeek Harness
owner: dsh
reviewer: antigravity
depends_on: [GOV-RESOURCE-MANIFEST-JSON-1]
base_commit: cf4529297f4e38fcde0bbc51784ec301ddbdeb35
branch: P19-UI-MANIFEST-VIEW-1
worktree: G:/CODEX/New Manga/.agents/worktrees/P19-UI-MANIFEST-VIEW-1
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
