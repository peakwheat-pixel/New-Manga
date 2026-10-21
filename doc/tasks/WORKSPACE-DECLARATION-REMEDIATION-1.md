---
id: WORKSPACE-DECLARATION-REMEDIATION-1
title: 真实仓库声明完整性错误的分诊与解析精度修复（163 → 仅保留已裁定残余）
kind: governance-hardening
governance_version: 2
status: ready
approval: user_authorized_20261021_declaration_followup
suggested_owner: DeepSeek Harness
owner: workspace-hardening
reviewer: Codex
depends_on: [WORKSPACE-CLEANUP-TOOL-HARDENING-1]
base_commit: 83b111ac104d47b30cf0842f553f97656cd0d8d1
branch: dsh/WORKSPACE-DECLARATION-REMEDIATION-1
worktree: G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/WORKSPACE-DECLARATION-REMEDIATION-1
allowed_paths:
  - tools/governance/clean_workspace.py
  - tools/governance/remove_worktrees.py
  - verification/WORKSPACE-DECLARATION-REMEDIATION-1
  - doc/tasks/WORKSPACE-DECLARATION-REMEDIATION-1.md
  - doc/handoffs
created: 2026-10-21
---

# WORKSPACE-DECLARATION-REMEDIATION-1：声明完整性错误分诊与解析精度修复

## 来源与目标

来源：`WORKSPACE-CLEANUP-TOOL-HARDENING-1` 交付后，用真实仓库运行
`clean_workspace.py --audit-declarations` 得到 **1858 declarations / 1264 roots / 163 errors / 54 warnings**，
导致工具对真实仓库 fail-closed 拒绝清理。错误分布（2026-10-21 实测，报告
`G:/CODEX/New Manga.workspace/temp/WORKSPACE-DECL-REMEDIATION/audit/declaration-audit.json`）：

| code | 数量 | 主要来源 |
|---|---:|---|
| JSON_PARSE | 69 | 67 个文件不含 `source_path`/`disposition` 等声明 token（stdout/runner/meta 日志被当成声明 JSON） |
| DECL_BARE_NAME | 57 | 历史任务/证据中的 `NOT_APPLICABLE`、`none yet`、中文说明文字等非路径值 |
| DECL_UNKNOWN_DISPOSITION | 9 | Codex governance 证据文档中的叙述性表格被当成 Resource Manifest |
| DECL_DESTINATION_UNRESOLVED | 7 | `WORKSPACE-CONSOLIDATION-1` 对 workspace root/managed area 的泛化声明 |
| DECL_RELATIVE_UNRESOLVED | 6 | 历史 Task 中的「见 G:/CODEX/New Manga」等说明文字 |
| DECL_GENERALIZED | 6 | 同上，workspace root/managed area 泛化声明 |
| DECL_ENV | 4 | 历史 Task P19 的 `%TEMP%` 记录 |
| FILE_UNREADABLE | 3 | P02/P04 历史 GBK 编码 markdown |
| TABLE_ROW_ARITY | 1 | `GOV-DEBT-CLEANUP-2.md` 资源表 7 列/表头 6 列 |
| DECL_RELATIVE_AMBIGUOUS | 1 | P19 `worktrees/P19-AC3-1` |

这些错误中大量是**解析器精度问题**（非声明 JSON 被当成声明文件、说明文字被当成路径、叙述表格被当成资源表），
不应通过改写 107 个历史文件/证据来“修复”（会破坏历史证据字节与 pin），而应在工具侧收紧“什么才算声明”的规则；
真正的策略性缺口（泛化 workspace root 声明、env、歧义路径）保留为**显式残余清单**，由 Codex/用户裁定，不得静默跳过。

目标：
1. 对 163 条错误完成逐文件/逐类分诊，区分「解析器误报」「可安全修复的解析精度问题」「需要裁定的真实声明缺口」「untracked 历史内容（不可修改）」；
2. 修复解析器误报与精度问题，使真实仓库审计的 error 只剩显式残余清单（目标 ≤ 10，且每条有 file/原因/裁定建议）；
3. **不得削弱** `WORKSPACE-CLEANUP-TOOL-HARDENING-1` 的 F-01…F-07 安全语义：真正的声明文件（含 `source_path`/`resource_type`/`disposition` 结构）仍必须 fail-closed。

## Acceptance Criteria

- [ ] **AC1 分诊清单**：提交 `REMEDIATION.md` + `audit-before.json`，列出 163 条错误按 code/file/tracked-untracked/文件归属（Task 状态或 evidence）分类、每类根因、是否解析器误报、处理决定；不得遗漏或按数量糊弄。<<PARTIAL: 待实施>>
- [ ] **AC2 JSON 声明文件识别**：非声明 JSON（stdout/runner/meta/log；解析失败且内容不含声明 token，且文件名不符合声明清单模式）只记 `JSON_NON_DECLARATION` warning，不再 `JSON_PARSE` fatal；含声明 token 或声明清单命名的不可解析 JSON 仍 fatal。新增夹具覆盖两类；真实审计 JSON_PARSE 错误降到 ≤2 且逐一说明。<<PARTIAL: 待实施>>
- [ ] **AC3 非路径 source 值**：source 值不是 path-like（`NOT_APPLICABLE`、`none yet`、说明文字、占位符）时记 `DECL_SOURCE_NOT_A_PATH` warning 并跳过，不登记保护；只有 path-like 但不可解析的值才是错误。夹具覆盖 `NOT_APPLICABLE`/prose/`none yet`/中文说明；真正的 `PRESERVE_*` 具体路径若不可解析必须仍 fatal。<<PARTIAL: 待实施>>
- [ ] **AC4 历史编码兼容**：`read_text` 对非法 UTF-8 尝试 GB18030 严格解码并记 `FILE_ENCODING_LEGACY` warning；无法解码仍 `FILE_UNREADABLE`。3 个 P02/P04 文件不再报错。<<PARTIAL: 待实施>>
- [ ] **AC5 叙述表格识别**：只有表头含 `resource_type` 或 `source_path`（英文精确列名）且 disposition 列精确为 `disposition` 的表格才按 Resource Manifest 解析；叙述性/中文表格跳过并记 warning。夹具覆盖 Codex governance 文档样式；真正 malformed 资源表仍报 `TABLE_ROW_ARITY`。<<PARTIAL: 待实施>>
- [ ] **AC6 残余清单**：真实审计剩余错误逐条列入 `RESIDUAL.md`，含 file、code、message、tracked/untracked、owner/归属、为何不能由解析精度修复、建议裁定（例如泛化 workspace root 声明需 Codex 裁定、env/歧义需用户裁定、untracked 历史内容属原作者）。不得静默忽略，不得把残余说成 0。<<PARTIAL: 待实施>>
- [ ] **AC7 回归与证据**：既有 80 tests 全部通过；新增测试覆盖 AC2–AC5 正反例；两个 incident replay 仍 15/15 REJECT、0 删除、18/18 source 覆盖；`run_evidence.py` exit 0；真实仓库 `--audit-declarations` 的 exit code 与 error 数如实记录；未执行任何真实删除/GC/prune/push；治理检查在集成后 PASS。<<PARTIAL: 待实施>>

## 允许修改范围

- `tools/governance/clean_workspace.py`（共享解析核心；若 `remove_worktrees.py` 复用相同逻辑可改）
- `verification/WORKSPACE-DECLARATION-REMEDIATION-1/`（报告、夹具、测试、日志、manifest）
- 本 Task 文件与 `doc/handoffs/`
- **不修改**任何历史 Task/证据/untracked 文件；不得用「改历史文档」凑 0 错误。

## 禁止范围

- 不得削弱 F-01（junction realpath 保护）、F-02（untracked 声明扫描/不可解析 JSON fail-closed）、F-03（path-like destination 完整性）、F-04（`--out` 防自删）等既有安全语义；
- 不得把真实声明文件的解析失败降级为 warning；
- 不得删除/移动/归档任何真实文件；不得 push/GC/prune/历史重写；
- 不得修改 `doc/` 下除本 Task 外的任何文件（Plan/STATUS 由 Lead 同步）。

## 验收证据

- `verification/WORKSPACE-DECLARATION-REMEDIATION-1/REMEDIATION.md`：分诊与修复说明。
- `audit-before.json` / `audit-after.json`：真实仓库审计前后（同一命令、同一仓库快照）。
- `RESIDUAL.md`：残余错误与裁定建议。
- `tests/` + `tests.log`：新/旧测试，含执行头与 EXIT。
- `incident-replay-*.json`：两个路径工具回放仍 15/15、0 删除。
- `evidence/`：manifest、environment、命令日志；Canonical Evidence 行 pin 到 evidence commit（先冻结证据，再提交 Task 记录）。

## Closeout Record

- 待实施；由 Lead 在 Codex Review + 集成后填写。
