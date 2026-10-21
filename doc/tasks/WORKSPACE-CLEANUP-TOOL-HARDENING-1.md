---
id: WORKSPACE-CLEANUP-TOOL-HARDENING-1
title: 工作区清理工具的保护判断与失败关闭修复（r208/r209 事故根因）
kind: fix
governance_version: 2
status: in_progress
approval: released_by_user_2026-10-21
blocked_by: null
suggested_owner: dsh
owner: workspace-hardening
reviewer: Codex
depends_on: [WORKSPACE-CONSOLIDATION-1]
base_commit: b8a1e519703f13af73b320dded117004b4bb189a
branch: dsh/WORKSPACE-CLEANUP-TOOL-HARDENING-1
worktree: G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1
allowed_paths:
  - tools/governance/clean_workspace.py
  - tools/governance/remove_worktrees.py
  - tools/governance/archive_branches.py
  - tools/governance/delete_branches.py
  - tools/governance/consolidate.py
  - verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1
  - doc/tasks/WORKSPACE-CLEANUP-TOOL-HARDENING-1.md
---

# WORKSPACE-CLEANUP-TOOL-HARDENING-1：清理工具保护判断与失败关闭修复

## 来源与目标

来源：`WORKSPACE-CONSOLIDATION-1` 的 r208 / r209 / r210 复审与事故台账
（`verification/WORKSPACE-CONSOLIDATION-1/codex-review-r208.md`、`incident-ledger-r208.json`、
`rework-r209-response.md`、`codex-review-r210.md`）。

已证事实：

- `clean_workspace.py` 的 pin 提取只认反引号包裹的表格单元格，裸路径未被当作保护；
- 保护判断按精确名称而非路径身份 + 父子覆盖，导致 P06 保留根内的 `old-runtime/worktree` 被删；
- 删除前没有 ignored / untracked 逐文件清册，`git status` 空被当作可删依据；
- 命令失败（如 `git stash list` 非零退出、权限拒绝）未被拒绝；
- 最终造成 18 个受保护 source（15 个删除根）受损：11 个原位置缺失、6 个仅部分重建、P06 子树缺失。

**目标**：在不执行任何清理的前提下，修复这五个脚本的保护判断与 fail-closed 行为，并用本次事故的
18 个 source / 15 个删除根做回放测试，证明工具会拒绝删除它们。**本 Task 不授权、不执行任何实际删除。**

## Acceptance Criteria

- [ ] **AC1 路径身份与父子覆盖**：保护集合按规范化绝对路径 + 父子关系判定；任何 `PRESERVE_*` 根的后代路径
  （含更深层子树）在删除候选中必须被拒绝；共享根/泛化声明的处理规则写入工具注释与测试。
- [ ] **AC2 失败关闭**：路径解析失败、裸路径/相对路径、非标准表格列数、未知 disposition、`git stash list`
  非零退出、权限拒绝、符号链接/越界路径 → 一律拒绝删除并输出原因；不得静默计 0 或继续。
- [ ] **AC3 删除前清册**：对候选目录生成 ignored / untracked 逐文件大小与 SHA-256 清册，并检查来源/用途；
  没有清册时不得 apply。不得把 ignored 内容直接认定为缓存。
- [ ] **AC4 无破坏夹具与失败注入**：至少覆盖 nested root、裸路径、相对路径、非标准表格、`PRESERVE_UNKNOWN`、
  父目录保护、非 `/worktrees/` 命名、stash 非零退出、权限拒绝、重复/别名路径；每个夹具断言"拒绝删除"。
- [ ] **AC5 dry-run/apply 解耦**：默认 dry-run；apply 必须显式开关 + 释放窗口记录；dry-run 报告可复算，
  apply 与 dry-run 的候选集合差异必须为空。
- [ ] **AC6 事故回放**：用 `incident-ledger-r208.json` 的 18 个 source / 15 个删除根作为输入，工具必须
  全部拒绝删除（0 删除），并给出逐项拒绝原因。
- [ ] **AC7 回归与文档**：运行现有工具测试 + 新增测试；在 Handoff 记录命令、环境、退出码；
  不修改 `WORKSPACE_GOVERNANCE.md` 或协作协议（如需修改，另由 Codex 冻结范围）。

## 允许修改范围

- 仅 frontmatter `allowed_paths` 列出的五个脚本、本 Task 文件与 `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/`。
- 不允许修改其他 Task、STATUS/Plan、历史 Review 或原清册。

## 禁止范围

- 禁止对真实工作区执行 apply/删除/移动/分支清理/GC/prune/push。
- 禁止用 `--force`、禁止跳过保护判断的"修复"。
- 禁止把 Review 或本 Task 当作对历史越界删除的追认。
- 范围扩大须先由 Codex 明确冻结。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1–AC6 | 新增单元/夹具测试 + 事故回放 | 隔离副本；不接触真实工作区 | NOT_RUN | 待交付时填写 |

## 依赖、风险与阻塞

- 依赖：`WORKSPACE-CONSOLIDATION-1` 的 closed_with_limitations 收口（事故输入）。
- 硬阻塞：Codex 必须先冻结本 Task 范围与 `allowed_paths`，再释放实现。
- 风险：修复错误可能让未来清理更危险；必须 fail-closed 并保留 dry-run 报告。

## 交付与运行记录

- Handoff：WIP checkpoint（主机重启前保存）；完整 Handoff、AC 勾选与 Canonical Evidence 待恢复后补齐。
- 已实现：五个脚本的 fail-closed 加固 + `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/`（66 测试，全过）+ `run_evidence.py` 证据生成器。
- 已生成证据：`verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/`（tests.log、environment.json、ac-coverage.json、incident-replay-*.json、declaration-audit.json、real-workspace-snapshot.json、manifest.sha256）。
- Review：尚无。
- 实际测试：见 WIP 证据；最终测试表待恢复后回填。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| 待填写 |  |  |  |  |  |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| NOT_APPLICABLE | - | NOT_APPLICABLE | - | - | 本 Task 为工具修复，不产生或删除工作区资源；测试使用隔离副本 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：0（本 Task 禁止实际删除）。
- 未关闭项及保留原因：待填写。
- 当前指针清理：待填写。
