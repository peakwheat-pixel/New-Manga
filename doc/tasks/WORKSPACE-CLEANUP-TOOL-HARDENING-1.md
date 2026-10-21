---
id: WORKSPACE-CLEANUP-TOOL-HARDENING-1
title: 工作区清理工具的保护判断与失败关闭修复（r208/r209 事故根因）
kind: fix
governance_version: 2
status: in_review
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
delivery_head: dbd6cbf5f3afa0d38bb3aa7b869198c4209f4499
canonical_evidence_status: complete
resource_closeout_status: complete
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
`run_evidence.py` 复算）。本次为 **Resubmission 2**：已按 Codex Review（changes_requested，F-01…F-07）修复，
evidence commit `dbd6cbf5f`，Task 记录 commit 紧随其后并引用该 evidence commit。

## Acceptance Criteria

- [x] **AC1 路径身份与父子覆盖**：保护集合按规范化绝对路径 + 父子关系判定；任何 `PRESERVE_*` 根的后代路径
  （含更深层子树）以及保护根的祖先候选在删除候选中必须被拒绝；共享根/泛化声明的处理规则写入工具注释与测试。
  **补充（F-01）**：声明经 junction/symlink 时，除词法路径外还按真实目标路径保护（双向），alias 声明告警记录；
  声明真实目标成为候选时同样 REJECT。 <<MET>>
- [x] **AC2 失败关闭**：路径解析失败、裸路径/相对路径、非标准表格列数、未知 disposition、`git stash list`
  非零退出、权限拒绝、符号链接/越界路径 → 一律拒绝删除并输出原因；不得静默计 0 或继续。
  **补充（F-02/F-03/F-06）**：声明扫描同时覆盖 tracked 与非忽略 untracked 的 `doc/tasks`/`verification`
  `.md`/`.json`；发生 untracked 声明解析错误 → 整态拒绝；path-like 但无法解析的 destination 记完整性错误
  （说明文字/占位符有明确允许规则并记 warning）；重复 inventory identity 显式拒绝（`INVENTORY_DUPLICATE_IDENTITY`）。 <<MET>>
- [x] **AC3 删除前清册**：对候选目录生成 ignored / untracked 逐文件大小与 SHA-256 清册，并检查来源/用途；
  没有清册时不得 apply。不得把 ignored 内容直接认定为缓存。 <<MET>>
- [x] **AC4 无破坏夹具与失败注入**：至少覆盖 nested root、裸路径、相对路径、非标准表格、`PRESERVE_UNKNOWN`、
  父目录保护、非 `/worktrees/` 命名、stash 非零退出、权限拒绝、重复/别名路径（另加符号链接/越界）；每个夹具断言"拒绝删除"。
  **补充（F-06）**：stash 失败与权限拒绝均新增真实 CLI 入口（`main(argv)`）验证；重复 inventory identity 明确拒绝。 <<MET>>
- [x] **AC5 dry-run/apply 解耦**：默认 dry-run；apply 必须显式开关 + 释放窗口记录；dry-run 报告可复算，
  apply 与 dry-run 的候选集合差异必须为空。**补充（F-04）**：apply 前拒绝 `--out` 等于/位于任一候选
  （含经 alias 指向），避免预删除清册被随候选删除。 <<MET>>
- [x] **AC6 事故回放**：用 `incident-ledger-r208.json` 的 18 个 source / 15 个删除根作为输入，两个路径删除工具
  必须全部拒绝删除（0 删除），并给出逐项拒绝原因。 <<MET>>
- [x] **AC7 回归与文档**：运行现有工具测试 + 新增测试；在 Handoff 记录命令、环境、退出码；
  不修改 `WORKSPACE_GOVERNANCE.md` 或协作协议。 <<MET>>

> 结果摘要（真实执行，原始输出见证据）：77/77 新测试 OK；事故回放 15/15 REJECT / 0 删除 / 18/18 source 覆盖；
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
| AC1–AC6 新增测试 | `C:/Python314/python.exe -B verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/run_suite.py` | Windows 11 / Python 3.14.6 / Git 2.52.0；全部夹具在 `%TEMP%` 隔离仓库，不接触真实工作区 | **executed**：`Ran 77 tests` / `OK`，exit `0`（0 skip） | `evidence/tests.log` |
| AC6 事故回放 | `python -B tools/governance/clean_workspace.py --replay-incident verification/WORKSPACE-CONSOLIDATION-1/incident-ledger-r208.json --out verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence`；`remove_worktrees.py` 同参 | 同上；只读输入 ledger，不删除任何路径 | **executed**：两工具均 `candidates=15, rejected=15, deleted=0, violations=0`，exit `0` | `evidence/incident-replay-clean-workspace.json`、`evidence/incident-replay-remove-worktrees.json` |
| AC1/AC6 补充：真实仓库声明审计 | `python -B tools/governance/clean_workspace.py --audit-declarations --incident-ledger <ledger> --out <evidence>` | 同上；只读扫描 tracked + 非忽略 untracked 的 `doc/tasks/**`+`verification/**` | **executed**：1855 declarations / 1263 roots；18/18 incident source 被真实声明覆盖；93 条历史声明错误 → **fail-closed exit 2**（未删任何文件） | `evidence/declaration-audit.json`、`.log` |
| AC7 既有测试（1） | `C:/Python314/python.exe -B tools/governance/tests/test_ac_gate.py` | 同上 | **executed**：`12/12 cases behaved as specified`，exit `0` | `evidence/existing-test_ac_gate.py.log` |
| AC7 既有测试（2） | `C:/Python314/python.exe -B tools/governance/tests/run-resource-manifest-cases.py` | 同上 | **executed（既存失败）**：`0/32 cases behaved as expected`，exit `1`；失败为 check.ps1 `TASK_LEDGER 已过期` 等无关规则，范围外，未修改其 expectation | `evidence/existing-run-resource-manifest-cases.py.log` |
| Gate 真实工作区未触碰 | `run_evidence.py` 内前后快照 | 只读 | **executed**：HEAD / `git status`（排除本 Task 路径）/ ledger 路径存在性前后一致 | `evidence/real-workspace-snapshot.json` |
| 复算 | `C:/Python314/python.exe -B verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/run_evidence.py` | 同上 | **executed**：`evidence-ok`，exit `0` | `evidence/environment.json` |

## 依赖、风险与阻塞

- 依赖：`WORKSPACE-CONSOLIDATION-1` 的 closed_with_limitations 收口（事故输入）。
- 风险：真实仓库仍有 93 条历史声明完整性错误（含 7 条 path-like destination），工具会整态拒绝清理
  （fail-closed 的预期副作用）；声明扫描刻意覆盖 1504 个非忽略 untracked 声明文件，范围更保守；
  共享 guard core 寄居 `clean_workspace.py`（allowed_paths 只允许这 5 个文件，无法新增共享模块）；
  apply 仅在 `%TEMP%` 夹具验证；进程占用检查未实现。详见 Handoff §7。

## 交付与运行记录

- **Resubmission 2（Review changes_requested，F-01…F-07）**：已修复——F-01 声明按真实目标（junction/symlink）
  双重保护 + 真实入口夹具；F-02 声明扫描覆盖非忽略 untracked `.md/.json`（解析错误→整态拒绝）；
  F-03 path-like 但不可解析的 destination → 完整性错误，说明文字/占位符有明确规则并记 warning；
  F-04 apply 前拒绝 `--out` 位于/等于/经 alias 指向任一候选；F-05 evidence commit 冻结后 Task 记录 commit
  引用它，Canonical Evidence 的 commit/sha 逐条对应实际字节，governance 日志确定后重算 manifest；
  F-06 stash/权限拒绝走真实 CLI 入口（`main(argv)`），重复 inventory identity 明确拒绝；
  F-07 纠正 Handoff 中治理检查归因并区分本 Task 的 evidence-dir warning。
- Handoff：`verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/HANDOFF.md`（逐项 AC、命令/环境/退出码、残余风险）。
- Review：`changes_requested`（`21715c5c0`，内容 head `cf7d2d46d`）；本次返修后请求再次独立 Review。本 Task 不自审。
- 实际测试：新测试 77/77 exit 0；事故回放两工具 15/15 REJECT exit 0；既有 `test_ac_gate.py` exit 0；
  既有 `run-resource-manifest-cases.py` exit 1（既存失败，如实记录）；真实工作区快照前后一致。
- 治理检查：在 worktree 内运行 `check.ps1 -TaskPath ...`，exit `1`，`FAIL (5 errors, 4 warnings)`，原始输出与
  exit code 见 `evidence/governance-check.log` 与 Handoff §6；5 个 error 均为 worktree 仓库状态（缺少主仓
  未跟踪 drafts/archive 内容导致 TASK_LEDGER 计数与 3 条既有 stale `archive/history` 引用不一致），
  与本 Task 改动无关；未修改 Plan/STATUS/check.ps1/task_ledger.py，最终治理检查由 Codex 在主仓执行。
- Canonical Evidence 的 commit pin 指向 evidence commit `dbd6cbf5f`（包含对应字节）；`governance-check.log`
  与 `manifest.sha256` 为日志/清单类过程证据，以 SHA-256 pin 登记（其字节由本记录 commit 包含）。
- 未逐行列入 Canonical Evidence 的过程文件：`HANDOFF.md`（由本节与 Handoff 引用；check.ps1 对 in_review
  仅记 warning）。`EV-CHECK`/`EV-MANIFEST` 两行为 SHA-256 pin；其文件内容在记录 commit 内，按“先定稿日志/
  清单、再登记其 SHA-256”执行，日志本身不包含自身哈希，无自引用。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EV-AC1-CORE | AC1 | `tools/governance/clean_workspace.py` | `dbd6cbf5f` | `361e5709a7fb53159d06a319a57c3a2ff863c131dff65a2fbb318fe92f6755c1` | `CANONICAL` |
| EV-AC1-JUNCTION | AC1（F-01） | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_tools_fixtures.py` | `dbd6cbf5f` | `ea6c11f783627decb928f57eebb02ce6274580c60eed7972235590a25b423c66` | `SOURCE_PIN` |
| EV-AC2-WT | AC2 | `tools/governance/remove_worktrees.py` | `dbd6cbf5f` | `5db35bbe08dc3dd7e8c9f23413872ab8195521ea15f7cd0e1666b7c8d469afec` | `CANONICAL` |
| EV-AC2-TESTS | AC2 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/tests.log` | `dbd6cbf5f` | `acce5cfde9a6e179ea056f41169d42a4c7177bcc4a9835002f300edc382fc14d` | `CANONICAL` |
| EV-AC3 | AC3 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/tests.log` | `dbd6cbf5f` | `acce5cfde9a6e179ea056f41169d42a4c7177bcc4a9835002f300edc382fc14d` | `CANONICAL` |
| EV-AC4 | AC4 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/ac-coverage.json` | `dbd6cbf5f` | `80d22db2a402e3cc262f484b66d573c55eccb4e41b83fe4d96a3251b29dd5535` | `CANONICAL` |
| EV-AC5 | AC5 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/tests.log` | `dbd6cbf5f` | `acce5cfde9a6e179ea056f41169d42a4c7177bcc4a9835002f300edc382fc14d` | `CANONICAL` |
| EV-AC6 | AC6 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/incident-replay-clean-workspace.json` | `dbd6cbf5f` | `d1b5edac231a0aa3a9d4b1fc9eb1fd28656b776d926f13c9b8f2a2a23540f0ba` | `CANONICAL` |
| EV-AC6-WT | AC6 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/incident-replay-remove-worktrees.json` | `dbd6cbf5f` | `1e07fbbc1cd9ce9db32c4d7e98b7802ef09e40f3b037dc72da444d9fd4c97b4d` | `CANONICAL` |
| EV-AC7 | AC7 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/environment.json` | `dbd6cbf5f` | `ab3aa565ce095f1fb4032dab104eeb0ba25ed5f635382b89ffd6c95be8145a52` | `CANONICAL` |
| EV-AC7-EXISTING | AC7 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/existing-test_ac_gate.py.log` | `dbd6cbf5f` | `215c67de8f330235b16828e518e47e646460d5fd4e499fcccb79d4d39c7d67f3` | `SOURCE_PIN` |
| EV-AC7-EXISTING2 | AC7 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/existing-run-resource-manifest-cases.py.log` | `dbd6cbf5f` | `7ec53b200d745f7f8267634034df4dc88a13d9e13594919ce69d9443e8ddeb38` | `SOURCE_PIN` |
| EV-AC7-ARCHIVE | AC7 | `tools/governance/archive_branches.py` | `dbd6cbf5f` | `42c35587493f8ee0993800c7a9265decc6a60b2e1f34b0a86b9702e497ed46b5` | `CANONICAL` |
| EV-AC7-DELETE | AC7 | `tools/governance/delete_branches.py` | `dbd6cbf5f` | `2146c2349fbb03ac9b9e32be4c207f586aa0457a75cb8be1c3b5a87b767fdaa8` | `CANONICAL` |
| EV-AC7-CONSOLIDATE | AC7 | `tools/governance/consolidate.py` | `dbd6cbf5f` | `734f1b6acb02fadc853fabaab5b3c3000e7d12f8166505a4c98ac582895c78a0` | `CANONICAL` |
| EV-AUDIT | AC1/AC6 补充 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/declaration-audit.json` | `dbd6cbf5f` | `17b56e68d6801bd0183c842a51475373a4b867c51e00205abf90327b23d78451` | `CANONICAL` |
| EV-AUDIT-LOG | AC1/AC6 补充 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/declaration-audit.log` | `dbd6cbf5f` | `561720500690a9a730f9c9d4541706334225c3d2561f5984d62b643f7216c453` | `SOURCE_PIN` |
| EV-SNAPSHOT | Gate | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/real-workspace-snapshot.json` | `dbd6cbf5f` | `ef373b3fc256984eb3ed67a3c71f80fe3f0283f9c0223cb09972e9b1e87aa4d9` | `CANONICAL` |
| EV-RUNNER | Gate（可复算） | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/run_evidence.py` | `dbd6cbf5f` | `cd864f709689921f8f94d219b028eb25ce825b93eff222ee3ff6353161e2e6fe` | `SOURCE_PIN` |
| EV-TEST-GUARD | AC1–AC3 测试源码 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_guard_core.py` | `dbd6cbf5f` | `7461f1ec8480adf37e7f3cb495f104efc573f153d3a99be0c18840ba0680fcbd` | `SOURCE_PIN` |
| EV-TEST-FIXTURES | AC2–AC5 测试源码 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_tools_fixtures.py` | `dbd6cbf5f` | `ea6c11f783627decb928f57eebb02ce6274580c60eed7972235590a25b423c66` | `SOURCE_PIN` |
| EV-TEST-REPLAY | AC6 测试源码 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_incident_replay.py` | `dbd6cbf5f` | `bf4a59f81e05d2c5b727ceee1c189b54cd178a05b9a81e7236b8b5aebc8415b3` | `SOURCE_PIN` |
| EV-TEST-OTHER | AC7 测试源码 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_other_tools.py` | `dbd6cbf5f` | `f6c2a81cecb6d07171f640004dddfdd83ad15de8c11b207756fed26963d901e9` | `SOURCE_PIN` |
| EV-TEST-SUPPORT | 测试夹具 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/fixture_support.py` | `dbd6cbf5f` | `c591bdd3727cd2426e8f30baa5f54e7ea3c975fbd3c1664fe6e99b9ac139752a` | `SOURCE_PIN` |
| EV-TEST-RUNNER | 测试运行器 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/run_suite.py` | `dbd6cbf5f` | `0cb2b75dad75f2316ded3322a3f98b2f4ef1877b5fe287188de75232beff297b` | `SOURCE_PIN` |
| EV-CHECK | 治理检查日志（过程证据） | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/governance-check.log` | - | `6ee5fb75abe307c6e3395d8f9c2b5284d5f9f423694a55c9373dc78b22a17f74` | `SOURCE_PIN` |
| EV-MANIFEST | 证据清单（过程证据） | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/manifest.sha256` | - | `fd233c8ed09e9cdbb8cc599d6ccd2be7276cf1a44951615c8906a6187a33c0a2` | `SOURCE_PIN` |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| NOT_APPLICABLE | - | NOT_APPLICABLE | - | - | 本 Task 为工具修复，不产生、不迁移、不删除任何工作区资源；测试与 apply 验证均在 `%TEMP%` 隔离夹具，真实工作区前后快照一致（`evidence/real-workspace-snapshot.json`） |

## Closeout Record

- Closeout date / Codex：待 Codex 独立 Review 与主仓集成后填写（本 Task 状态 `in_review`）。
- canonical_evidence_status：`complete`（AC1–AC7 证据行已登记；commit pin 指向 evidence commit `dbd6cbf5f`，
  SHA-256 与工作区/该 commit 字节一致；`governance-check.log`、`manifest.sha256` 以 SHA-256 pin 登记）。
- resource_closeout_status：`complete`（无 worktree/task-env/artifact/exchange 等资源需处置；未执行任何真实删除）。
- 删除、迁移、归档数量/字节数：0（本 Task 禁止实际删除；测试仅删除 `%TEMP%` 夹具）。
- 未关闭项及保留原因：真实仓库 93 条历史声明完整性错误 → 工具 fail-closed 拒绝清理，需另立 Task 或
  Codex/用户裁定；既有 `run-resource-manifest-cases.py` 0/32 为 check.ps1/task_ledger 仓库状态问题，范围外如实保留。
- 当前指针清理：未修改 Plan/STATUS/其他 Task/历史 Review；worktree 缺少主仓未跟踪 drafts/archive 内容，
  治理检查留有既有 TASK_LEDGER 计数与 stale 引用差异，最终治理检查由 Codex 在主仓执行。
