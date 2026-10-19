---
id: GOV-EVIDENCE-UNIQUE-1
title: GOV-DEBT-CLEANUP-2 AC7 唯一最终证据判定
kind: governance
governance_version: 2
status: proposed
approval: codex_scope_release_required
suggested_owner: dsh
owner: dsh
reviewer: Antigravity
depends_on: [GOV-DEBT-CLEANUP-2]
base_commit: 2636301fe5d6c33535f873aeb776c3e4beb5dd2d
branch: agent/deepseek/GOV-EVIDENCE-UNIQUE-1
worktree: 待 Codex 在 G:\CODEX\New Manga.workspace\worktrees\GOV-EVIDENCE-UNIQUE-1 创建并登记实际路径
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-EVIDENCE-UNIQUE-1
allowed_paths:
  - doc/tasks/GOV-EVIDENCE-UNIQUE-1.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/handoffs/
  - doc/reviews/
  - verification/GOV-EVIDENCE-UNIQUE-1/
---

# GOV-EVIDENCE-UNIQUE-1：GOV-DEBT-CLEANUP-2 AC7 唯一最终证据判定

## 来源与目标

承接 `GOV-DEBT-CLEANUP-2` AC7 未完成部分。只读审查 `verification/GOV-DEBT-CLEANUP-2/ac7-evidence-dir-files.md` 列出的 61 个文件，并按原 AC/来源 Task 判断每项是否为某个已释放 AC 的唯一最终证据。不得因本 Task 而恢复或改写已关闭 Task 的状态、AC、Review、Canonical Evidence 或历史 pin。主证据入口：
- `doc/tasks/GOV-DEBT-CLEANUP-2.md` 与 `doc/reviews/GOV-DEBT-CLEANUP-2-94c8dcdab-antigravity-r2.md`
- `verification/GOV-DEBT-CLEANUP-2/ac7-evidence-dir-files.md`
- `doc/09_COLLABORATION.md` §4.1 / §4.2 / §5

## Acceptance Criteria

- [ ] **AC1 — 61 项逐文件判定**：对源表 61 项逐项记录精确路径、文件 SHA-256、候选类别、对应来源 Task/已释放 AC、当前 Canonical Evidence pin、文件是否能证明 AC、是否存在等效替代证据、是否为唯一最终证据及理由。不得只依据文件名、目录或表面存在性判定。
- [ ] **AC2 — 唯一性与完整性核验**：对每个已释放 AC 建立 `AC → Canonical Evidence` 映射；明确判为唯一、存在其他等效证据、非判别力证据、无法确定或不适用。任何缺失来源、无法访问、hash 不符或 AC 未释放均保留为 `BLOCKED/UNKNOWN`，不可改写成 PASS。
- [ ] **AC3 — 只读保护**：不更改源 Task、Review、既有 Canonical Evidence、pin、61 个文件、`.gitattributes`、`.gitignore` 或生产文件；不移动、删除、归档、重命名、复制或补登记其他 Task 的 evidence。候选补 pin 只写本 Task 的建议表，须由 Codex 在独立获准范围处理。
- [ ] **AC4 — 可复核交付与 Review**：入库逐项结果、来源 commit/hash、方法与未决项；生成 Handoff；由 Antigravity 对固定 delivery head 独立 Review。逐项证据覆盖和 limitation 保持一致。
- [ ] **AC5 — 生命周期和资源 closeout**：完成 Task/Review/Plan/STATUS 生命周期、Canonical Evidence 与 Resource Manifest；更新 integration 字段并按直接/branch 集成事实登记；运行适用治理检查并完整保存命令、环境、stdout、stderr、exit code。任何不通过均如实记录，不放宽 checker。

## 允许修改范围

- `verification/GOV-EVIDENCE-UNIQUE-1/`：只读判定矩阵、复核记录、运行输出。
- 本 Task 自身文件、Handoff、Review 及 Codex 管理的 Plan/STATUS 指针元数据。

## 禁止事项

- 不改 `verification/GOV-DEBT-CLEANUP-2/`、任何来源 Task/Review/evidence、历史 pin、`.gitattributes`、`.gitignore`、`tools/`、`src/`、`tests/` 或其他生产路径。
- 不把建议 pin 写回来源 Task；不执行物理处置；不扫描并裁定与 61 项无关的未入库文件。
- 不把 `closed_with_limitations` 来源 Task 改成 `done`，不重开 AC，也不把 `UNKNOWN/BLOCKED/NOT_RUN` 写成 PASS。

## 测试与验证

本 Task 为只读证据判定，不运行产品测试。planned：对 61 行逐行核对、重算文件 hash、核查来源提交含文件、对照来源 Task 的 AC/pin，并运行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-EVIDENCE-UNIQUE-1.md` 与全局 checker。按命令、PowerShell 版本、结果、stdout/stderr、exit code 记录；不得把未跑项标为通过。

## Canonical Evidence

登记 AC1–AC5 判别力矩阵、Handoff、Review 和 checker 输出；每项记录仓库相对路径、含文件 commit、SHA-256、class。Review 必须绑定精确 `reviewed_head`。

## Resource Manifest

冻结 ready 前登记实际 Task worktree 路径；task-env、dataset、artifact、temp、agent-output、exchange 逐项核实。不适用需有目录核实依据；未知、dirty、被引用或用户数据一律保留。

## Closeout Record

- 状态：`proposed`。尚未释放、无 owner 认领、无交付。
- 释放条件（Codex r14 §5）：登记真实 worktree 路径、base/head、Plan/STATUS 指针后，
  由 Codex 置 `ready` 并派发。
- 本 Task 的产出是只读判定矩阵，不修改任何证据文件、pin 或生产代码。
