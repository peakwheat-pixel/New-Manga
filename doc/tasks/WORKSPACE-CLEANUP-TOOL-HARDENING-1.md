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

交付：`verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/HANDOFF.md`；
判别力证据：`verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/`（可用
`run_evidence.py` 复算）。

## Acceptance Criteria

- [x] **AC1 路径身份与父子覆盖**：保护集合按规范化绝对路径 + 父子关系判定；任何 `PRESERVE_*` 根的后代路径
  （含更深层子树）以及保护根的祖先候选在删除候选中必须被拒绝；共享根/泛化声明的处理规则写入工具注释与测试。
  <<MET>>
- [x] **AC2 失败关闭**：路径解析失败、裸路径/相对路径、非标准表格列数、未知 disposition、`git stash list`
  非零退出、权限拒绝、符号链接/越界路径 → 一律拒绝删除并输出原因；不得静默计 0 或继续。
  <<MET>>
- [x] **AC3 删除前清册**：对候选目录生成 ignored / untracked 逐文件大小与 SHA-256 清册，并检查来源/用途；
  没有清册时不得 apply。不得把 ignored 内容直接认定为缓存。 <<MET>>
- [x] **AC4 无破坏夹具与失败注入**：至少覆盖 nested root、裸路径、相对路径、非标准表格、`PRESERVE_UNKNOWN`、
  父目录保护、非 `/worktrees/` 命名、stash 非零退出、权限拒绝、重复/别名路径（另加符号链接/越界）；每个夹具断言"拒绝删除"。
  <<MET>>
- [x] **AC5 dry-run/apply 解耦**：默认 dry-run；apply 必须显式开关 + 释放窗口记录；dry-run 报告可复算，
  apply 与 dry-run 的候选集合差异必须为空。 <<MET>>
- [x] **AC6 事故回放**：用 `incident-ledger-r208.json` 的 18 个 source / 15 个删除根作为输入，两个路径删除工具
  必须全部拒绝删除（0 删除），并给出逐项拒绝原因。 <<MET>>
- [x] **AC7 回归与文档**：运行现有工具测试 + 新增测试；在 Handoff 记录命令、环境、退出码；
  不修改 `WORKSPACE_GOVERNANCE.md` 或协作协议。 <<MET>>

> 结果摘要（真实执行，原始输出见证据）：66/66 新测试 OK；事故回放 15/15 REJECT / 0 删除 / 18/18 source 覆盖；
> 既有 `test_ac_gate.py` 12/12 PASS；既有 `run-resource-manifest-cases.py` 0/32 为**既存失败**（check.ps1 的
> TASK_LEDGER 预算规则，范围外，且不调用这五个脚本），如实记录未掩盖。

## 允许修改范围

- 仅 frontmatter `allowed_paths` 列出的五个脚本、本 Task 文件与 `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/`。
- 不允许修改其他 Task、STATUS/Plan、历史 Review 或原清册；Handoff 因此放在 `evidence_dir`（`doc/handoffs/`
  不在 allowed_paths）。

## 禁止范围

- 禁止对真实工作区执行 apply/删除/移动/分支清理/GC/prune/push。
- 禁止用 `--force`、禁止跳过保护判断的"修复"。
- 禁止把 Review 或本 Task 当作对历史越界删除的追认。
- 范围扩大须先由 Codex 明确冻结。

## 测试要求

| 场景/AC | 命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1–AC6 新增测试 | `C:/Python314/python.exe -B verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/run_suite.py` | Windows 11 / Python 3.14.6 / Git 2.52.0；全部夹具在 `%TEMP%` 隔离仓库，不接触真实工作区 | **executed**：`Ran 66 tests` / `OK`，exit `0`（0 skip） | `evidence/tests.log` |
| AC6 事故回放 | `python -B tools/governance/clean_workspace.py --replay-incident verification/WORKSPACE-CONSOLIDATION-1/incident-ledger-r208.json --out verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence`；`remove_worktrees.py` 同参 | 同上；只读输入 ledger，不删除任何路径 | **executed**：两工具均 `candidates=15, rejected=15, deleted=0, violations=0`，exit `0` | `evidence/incident-replay-clean-workspace.json`、`evidence/incident-replay-remove-worktrees.json` |
| AC1/AC6 补充：真实仓库声明审计 | `python -B tools/governance/clean_workspace.py --audit-declarations --incident-ledger <ledger> --out <evidence>` | 同上；只读扫描 tracked `doc/tasks/**`+`verification/**` | **executed**：1501 declarations / 1023 roots；18/18 incident source 被真实声明覆盖；46 条历史声明错误 → **fail-closed exit 2**（未删任何文件） | `evidence/declaration-audit.json`、`.log` |
| AC7 既有测试（1） | `C:/Python314/python.exe -B tools/governance/tests/test_ac_gate.py` | 同上 | **executed**：`12/12 cases behaved as specified`，exit `0` | `evidence/existing-test_ac_gate.py.log` |
| AC7 既有测试（2） | `C:/Python314/python.exe -B tools/governance/tests/run-resource-manifest-cases.py` | 同上 | **executed（既存失败）**：`0/32 cases behaved as expected`，exit `1`；失败为 check.ps1 `TASK_LEDGER 已过期` 等无关规则，范围外，未修改其 expectation | `evidence/existing-run-resource-manifest-cases.py.log` |
| Gate 真实工作区未触碰 | `run_evidence.py` 内前后快照 | 只读 | **executed**：HEAD / `git status`（排除本 Task 路径）/ ledger 路径存在性前后一致 | `evidence/real-workspace-snapshot.json` |
| 复算 | `C:/Python314/python.exe -B verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/run_evidence.py` | 同上 | **executed**：`evidence-ok`，exit `0` | `evidence/environment.json` |

## 依赖、风险与阻塞

- 依赖：`WORKSPACE-CONSOLIDATION-1` 的 closed_with_limitations 收口（事故输入）。
- 风险：真实仓库仍有 46 条历史声明完整性错误，工具会整态拒绝清理（fail-closed 的预期副作用）；共享 guard core
  寄居 `clean_workspace.py`（allowed_paths 只允许这 5 个文件，无法新增共享模块）；apply 仅在 `%TEMP%` 夹具验证；
  declared 的进程占用检查未实现（本 Task 未扩大范围）。详见 Handoff §7。

## 交付与运行记录

- Handoff：`verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/HANDOFF.md`（含逐项 AC、命令/环境/退出码、残余风险）。
- Review：尚无（请求 Codex 独立 Review；本 Task 不自审）。
- 实际测试：新测试 66/66 exit 0；事故回放两工具 15/15 REJECT exit 0；既有 `test_ac_gate.py` exit 0；
  既有 `run-resource-manifest-cases.py` exit 1（既存失败，如实记录）；真实工作区快照前后一致。
- 治理检查：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/WORKSPACE-CLEANUP-TOOL-HARDENING-1.md`
  在 worktree 内运行，exit `1`，`Governance check: FAIL (5 errors, 4 warnings)`，原始输出与 exit code 见
  `evidence/governance-check.log` 与 Handoff §6。5 个 error 均为 worktree base `b8a1e5197` 早于主仓 Task 释放提交
  `b63f22aba` 的既有差异：TASK_LEDGER 过期 2 条 + `doc/00_INDEX.md`/`doc/AD-001…` 的 3 条 `archive/history/...`
  失效引用；均不在本 Task allowed_paths，**未修改 Plan/STATUS/check.ps1/task_ledger.py**，最终治理检查由 Codex
  在主仓集成后执行。
- 未逐行列入 Canonical Evidence 的过程文件：`HANDOFF.md`、`evidence/declaration-audit.log`、
  `evidence/governance-check.log`、`evidence/manifest.sha256`（均由本节与 Handoff 引用；check.ps1 对 in_review
  仅记 warning）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EV-AC1-CORE | AC1 | `tools/governance/clean_workspace.py` | `cf7d2d46d` | `7fad2d0153a54a2ee14d2fa7d4ff24f95eb858125a0cd1dbf333ca92d7010d18` | `CANONICAL` |
| EV-AC2-WT | AC2 | `tools/governance/remove_worktrees.py` | `cf7d2d46d` | `0b8d656d133d7aafe9fac4682bc37ff6e0b7aa5b6e0d39c9e2d1fa4af69f0bc2` | `CANONICAL` |
| EV-AC2-TESTS | AC2 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/tests.log` | `cf7d2d46d` | `9cc6efc933c034f689ba46936c5cddc92e82bcb12df1c247bcfbdd4516adf146` | `CANONICAL` |
| EV-AC3 | AC3 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/tests.log` | `cf7d2d46d` | `9cc6efc933c034f689ba46936c5cddc92e82bcb12df1c247bcfbdd4516adf146` | `CANONICAL` |
| EV-AC4 | AC4 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/ac-coverage.json` | `cf7d2d46d` | `506f5b85f9b55a22f9706eb20fbf838b444abd2c263247ff3b95f8a60b4c7c50` | `CANONICAL` |
| EV-AC5 | AC5 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/tests.log` | `cf7d2d46d` | `9cc6efc933c034f689ba46936c5cddc92e82bcb12df1c247bcfbdd4516adf146` | `CANONICAL` |
| EV-AC6 | AC6 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/incident-replay-clean-workspace.json` | `cf7d2d46d` | `519a41b527a02ab43550a235b83aafb01486ad32d1ab9268951c0f0e41d971fe` | `CANONICAL` |
| EV-AC6-WT | AC6 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/incident-replay-remove-worktrees.json` | `cf7d2d46d` | `5313961705b54685ebf8141427ee5c6cbd1e888bc7afbfa144f11ced81d74f4e` | `CANONICAL` |
| EV-AC7 | AC7 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/environment.json` | `cf7d2d46d` | `9219374eb2d4ece2c80c27a2a07f2e01e3b4b9401e14de2071049753f5961122` | `CANONICAL` |
| EV-AC7-EXISTING | AC7 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/existing-test_ac_gate.py.log` | `cf7d2d46d` | `bdf462cc6a5ed98a7c5c368b3227dafd5969b82e2f66dbb05f182e9882fbf4a9` | `SOURCE_PIN` |
| EV-AC7-EXISTING2 | AC7 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/existing-run-resource-manifest-cases.py.log` | `cf7d2d46d` | `7ec53b200d745f7f8267634034df4dc88a13d9e13594919ce69d9443e8ddeb38` | `SOURCE_PIN` |
| EV-AC7-ARCHIVE | AC7 | `tools/governance/archive_branches.py` | `cf7d2d46d` | `42c35587493f8ee0993800c7a9265decc6a60b2e1f34b0a86b9702e497ed46b5` | `CANONICAL` |
| EV-AC7-DELETE | AC7 | `tools/governance/delete_branches.py` | `cf7d2d46d` | `2146c2349fbb03ac9b9e32be4c207f586aa0457a75cb8be1c3b5a87b767fdaa8` | `CANONICAL` |
| EV-AC7-CONSOLIDATE | AC7 | `tools/governance/consolidate.py` | `cf7d2d46d` | `734f1b6acb02fadc853fabaab5b3c3000e7d12f8166505a4c98ac582895c78a0` | `CANONICAL` |
| EV-AUDIT | AC1/AC6 补充 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/declaration-audit.json` | `cf7d2d46d` | `528641aacc613601c0d12e97ff0bf9e6d41e8e7f5dc7cb4a47f0bc23b5c26cac` | `CANONICAL` |
| EV-SNAPSHOT | Gate | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/real-workspace-snapshot.json` | `cf7d2d46d` | `87faaad5665a3558487c50b462d0fe2c9a14d2fc82e6141eb4ece19f5d17f670` | `CANONICAL` |
| EV-RUNNER | Gate（可复算） | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/run_evidence.py` | `cf7d2d46d` | `71f177c75a4c3e94d8f8e422ef3eebe16f5b55afc46351f417a79bd61d97ffc0` | `SOURCE_PIN` |
| EV-TEST-GUARD | AC1–AC3 测试源码 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_guard_core.py` | `cf7d2d46d` | `d13e89186d83f9e904dbdef3762046a03b031a7604f89909fafb4377809f4708` | `SOURCE_PIN` |
| EV-TEST-FIXTURES | AC2–AC5 测试源码 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_tools_fixtures.py` | `cf7d2d46d` | `9639ad71ea0f9a1855bd1fa30cbe7098a661b3ef81ed82e644e51005d70bf9fb` | `SOURCE_PIN` |
| EV-TEST-REPLAY | AC6 测试源码 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_incident_replay.py` | `cf7d2d46d` | `bf4a59f81e05d2c5b727ceee1c189b54cd178a05b9a81e7236b8b5aebc8415b3` | `SOURCE_PIN` |
| EV-TEST-OTHER | AC7 测试源码 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_other_tools.py` | `cf7d2d46d` | `f6c2a81cecb6d07171f640004dddfdd83ad15de8c11b207756fed26963d901e9` | `SOURCE_PIN` |
| EV-TEST-SUPPORT | 测试夹具 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/fixture_support.py` | `cf7d2d46d` | `c591bdd3727cd2426e8f30baa5f54e7ea3c975fbd3c1664fe6e99b9ac139752a` | `SOURCE_PIN` |
| EV-TEST-RUNNER | 测试运行器 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/run_suite.py` | `cf7d2d46d` | `0cb2b75dad75f2316ded3322a3f98b2f4ef1877b5fe287188de75232beff297b` | `SOURCE_PIN` |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| NOT_APPLICABLE | - | NOT_APPLICABLE | - | - | 本 Task 为工具修复，不产生、不迁移、不删除任何工作区资源；测试与 apply 验证均在 `%TEMP%` 隔离夹具，真实工作区前后快照一致（`evidence/real-workspace-snapshot.json`） |

## Closeout Record

- Closeout date / Codex：待 Codex 独立 Review 与主仓集成后填写（本 Task 状态 `in_review`）。
- canonical_evidence_status：`complete`（AC1–AC7 证据行已登记，commit `cf7d2d46d` + 工作区 SHA-256 pin）。
- resource_closeout_status：`complete`（无 worktree/task-env/artifact/exchange 等资源需处置；未执行任何真实删除）。
- 删除、迁移、归档数量/字节数：0（本 Task 禁止实际删除；测试仅删除 `%TEMP%` 夹具）。
- 未关闭项及保留原因：真实仓库仍有 46 条历史声明完整性错误 → 工具 fail-closed 拒绝清理，需另立 Task 或 Codex/用户裁定；
  既有 `run-resource-manifest-cases.py` 0/32 为 check.ps1/task_ledger 仓库状态问题，范围外如实保留。
- 当前指针清理：未修改 Plan/STATUS/其他 Task/历史 Review；worktree base 早于主仓 Task 释放提交 `b63f22aba`，
  最终治理检查由 Codex 在主仓执行。
