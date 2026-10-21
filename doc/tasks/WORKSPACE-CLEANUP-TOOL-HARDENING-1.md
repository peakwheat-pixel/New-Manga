---
id: WORKSPACE-CLEANUP-TOOL-HARDENING-1
title: 工作区清理工具的保护判断与失败关闭修复（r208/r209 事故根因）
kind: fix
governance_version: 2
status: done
approval: released_by_user_2026-10-21
blocked_by: null
suggested_owner: dsh
owner: workspace-hardening
reviewer: Codex
depends_on: [WORKSPACE-CONSOLIDATION-1]
base_commit: b8a1e519703f13af73b320dded117004b4bb189a
branch: dsh/WORKSPACE-CLEANUP-TOOL-HARDENING-1
worktree: G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1
integration_commit: 368c0780974ada5879d165526c60d41ee0fc8dc2
delivery_head: b0ad9f8d15e42f0751c137a9a41527f5dd3b4fda
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
证据目录：`verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/`（可用 `run_evidence.py` 复算）。

本次为 **Resubmission 3**：已按 Codex Review r1（F-01…F-07）与 r2（F-02 malformed JSON、F-05 证据字节冻结）
修复。提交顺序：evidence commit `30946decf`（冻结代码/测试/证据/最终日志/manifest）→ Task-only 记录 commit
（本文件，引用该 evidence commit）。

## Acceptance Criteria

- [x] **AC1 路径身份与父子覆盖**：保护集合按规范化绝对路径 + 父子关系判定；任何 `PRESERVE_*` 根的后代路径
  （含更深层子树）以及保护根的祖先候选在删除候选中必须被拒绝；共享根/泛化声明的处理规则写入工具注释与测试。
  **补充（F-01）**：声明经 junction/symlink 时，除词法路径外还按真实目标路径保护（双向）；真实目标候选同样 REJECT。 <<MET>>
- [x] **AC2 失败关闭**：路径解析失败、裸路径/相对路径、非标准表格列数、未知 disposition、`git stash list`
  非零退出、权限拒绝、符号链接/越界路径 → 一律拒绝删除并输出原因；不得静默计 0 或继续。
  **补充（F-02/F-03/F-06）**：声明扫描覆盖 tracked 与非忽略 untracked 的 `doc/tasks`/`verification`
  `.md`/`.json`；untracked 声明解析失败 → 整态拒绝；**任何 JSON 声明文件解析失败一律记为完整性错误
  （`JSON_PARSE`，不再以是否含字面 `PRESERVE` 区分，避免 MIGRATE/ARCHIVE 漏保护）**；path-like 但无法解析的
  destination 记完整性错误；重复 inventory identity 显式拒绝（`INVENTORY_DUPLICATE_IDENTITY`）。 <<MET>>
- [x] **AC3 删除前清册**：对候选目录生成 ignored / untracked 逐文件大小与 SHA-256 清册，并检查来源/用途；
  没有清册时不得 apply。不得把 ignored 内容直接认定为缓存。 <<MET>>
- [x] **AC4 无破坏夹具与失败注入**：至少覆盖 nested root、裸路径、相对路径、非标准表格、`PRESERVE_UNKNOWN`、
  父目录保护、非 `/worktrees/` 命名、stash 非零退出、权限拒绝、重复/别名路径（另加符号链接/越界）；每个夹具断言"拒绝删除"。
  **补充（F-06）**：stash/权限拒绝走真实 CLI 入口（`main(argv)`）；重复 inventory identity 明确拒绝；
  **补充（F-02 r2）**：MIGRATE / ARCHIVE 声明藏在语法错误 JSON 中 → exit 2、0 删除。 <<MET>>
- [x] **AC5 dry-run/apply 解耦**：默认 dry-run；apply 必须显式开关 + 释放窗口记录；dry-run 报告可复算，
  apply 与 dry-run 的候选集合差异必须为空。**补充（F-04）**：apply 前拒绝 `--out` 等于/位于任一候选
  （含经 alias 指向）。 <<MET>>
- [x] **AC6 事故回放**：用 `incident-ledger-r208.json` 的 18 个 source / 15 个删除根作为输入，两个路径删除工具
  必须全部拒绝删除（0 删除），并给出逐项拒绝原因。 <<MET>>
- [x] **AC7 回归与文档**：运行现有工具测试 + 新增测试；在 Handoff 记录命令、环境、退出码；
  不修改 `WORKSPACE_GOVERNANCE.md` 或协作协议。 <<MET>>

> 结果摘要（真实执行，原始输出见证据）：80/80 新测试 OK；事故回放 15/15 REJECT / 0 删除 / 18/18 source 覆盖；
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
| AC1–AC6 新增测试 | `C:/Python314/python.exe -B verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/run_suite.py` | Windows 11 / Python 3.14.6 / Git 2.52.0；全部夹具在 `%TEMP%` 隔离仓库，不接触真实工作区 | **executed**：`Ran 80 tests` / `OK`，exit `0`（0 skip） | `evidence/tests.log` |
| AC6 事故回放 | `python -B tools/governance/clean_workspace.py --replay-incident verification/WORKSPACE-CONSOLIDATION-1/incident-ledger-r208.json --out verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence`；`remove_worktrees.py` 同参 | 同上；只读输入 ledger，不删除任何路径 | **executed**：两工具均 `candidates=15, rejected=15, deleted=0, violations=0`，exit `0` | `evidence/incident-replay-clean-workspace.json`、`evidence/incident-replay-remove-worktrees.json` |
| AC1/AC2/AC6 补充：真实仓库声明审计 | `python -B tools/governance/clean_workspace.py --audit-declarations --incident-ledger <ledger> --out <evidence>` | 同上；只读扫描 tracked + 非忽略 untracked 的 `doc/tasks/**`+`verification/**` | **executed**：枚举 7392 tracked + 1504 untracked 路径；实际解析 2271 `.md` + 1147 `.json`；1858 declarations / 1264 roots；18/18 incident source 覆盖；163 条完整性错误（含 69 条 `JSON_PARSE`）→ **fail-closed exit 2**（未删任何文件） | `evidence/declaration-audit.json`、`.log` |
| AC7 既有测试（1） | `C:/Python314/python.exe -B tools/governance/tests/test_ac_gate.py` | 同上 | **executed**：`12/12 cases behaved as specified`，exit `0` | `evidence/existing-test_ac_gate.py.log` |
| AC7 既有测试（2） | `C:/Python314/python.exe -B tools/governance/tests/run-resource-manifest-cases.py` | 同上 | **executed（既存失败）**：`0/32 cases behaved as expected`，exit `1`；失败为 check.ps1 `TASK_LEDGER 已过期` 等无关规则，范围外，未修改其 expectation | `evidence/existing-run-resource-manifest-cases.py.log` |
| Gate 真实工作区未触碰 | `run_evidence.py` 内前后快照 | 只读 | **executed**：HEAD / `git status`（排除本 Task 路径）/ ledger 路径存在性前后一致 | `evidence/real-workspace-snapshot.json` |
| 复算 | `C:/Python314/python.exe -B verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/run_evidence.py` | 同上 | **executed**：`evidence-ok`，exit `0` | `evidence/environment.json` |

## 依赖、风险与阻塞

- 依赖：`WORKSPACE-CONSOLIDATION-1` 的 closed_with_limitations 收口（事故输入）。
- 风险：真实仓库仍有 163 条历史声明完整性错误（含 69 条不可解析 JSON、7 条 path-like destination）→
  工具会整态拒绝清理（fail-closed 的预期副作用）；声明扫描刻意覆盖 1504 个非忽略 untracked 声明路径；
  共享 guard core 寄居 `clean_workspace.py`（allowed_paths 只允许这 5 个文件，无法新增共享模块）；
  apply 仅在 `%TEMP%` 夹具验证；进程占用检查未实现。详见 Handoff §7。

## 交付与运行记录

- **Resubmission 3（Review r2：F-02 malformed JSON、F-05 evidence 字节冻结）**：
  - F-02：删除 `"PRESERVE" in raw` 启发式；扫描范围内 JSON 解析失败一律 `JSON_PARSE` 完整性错误（整态拒绝），
    新增 MIGRATE / ARCHIVE / 无 marker 三个 malformed JSON 夹具（均 exit 2、候选存在）。
  - F-05：evidence commit `30946decf` **同时冻结**最终 `governance-check.log`（显式 LF 归一）与最终
    `manifest.sha256`（11 项，含 log）；manifest 每项 SHA-256 等于该 commit 的 Git blob 字节（已逐项校验）。
    本 Task-only 记录 commit 只引用该 evidence commit；27 条 Canonical Evidence 行的 commit pin 全部指向
    `30946decf`，SHA-256 与该 commit 的 Git blob 字节一致（无 SHA-only 行、无自引用）。
  - Handoff 表述修正：7392+1504 为**枚举路径数**，2271 `.md` + 1147 `.json` 才是**实际解析文件数**。
- **R3-F02-DOC（文档性变更，no behaviour change）**：`clean_workspace.py` 的
  `scan_repo_declarations` docstring 原先仍写“含 `PRESERVE` marker 的 malformed JSON 才 fatal、无 marker 记
  warning”，与实现及 Handoff 相反；已改为“任何 JSON 解析失败 = `JSON_PARSE` 完整性错误、整态拒绝、无 marker
  豁免”，并明确禁止重新引入该启发式。只改 docstring（6 insertions / 3 deletions，均在 docstring 内），
  80/80 测试仍通过，行为未变。最终代码 commit `b0ad9f8d`；Canonical Evidence 仍 pin evidence commit
  `30946decf`（证据字节未重新冻结）。
- Handoff：`verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/HANDOFF.md`（逐项 AC、命令/环境/退出码、残余风险）。
- Review：r1 `changes_requested`（`21715c5c0`）→ r2 `changes_requested`（`beeac02af`）；本轮修复后请求再 Review。
  本 Task 不自审。
- 实际测试：新测试 80/80 exit 0；事故回放两工具 15/15 REJECT exit 0；既有 `test_ac_gate.py` exit 0；
  既有 `run-resource-manifest-cases.py` exit 1（既存失败，如实记录）；真实工作区快照前后一致。
- 治理检查：worktree 内 `check.ps1 -TaskPath ...` exit `1`，`FAIL (5 errors, 4 warnings)`；原始输出与 exit
  见 `evidence/governance-check.log` 与 Handoff §6。5 个 error 为 worktree 缺少主仓未跟踪 drafts/archive 内容
  导致的 TASK_LEDGER 计数与既有 stale `archive/history` 引用，与本 Task 改动无关；未修改 Plan/STATUS/
  check.ps1/task_ledger.py，最终治理检查由 Codex 在主仓执行。
- 日志与 pin 的时序说明（避免自引用）：`governance-check.log` 生成时 Task 行仍 pin 上一 evidence commit
  `dbd6cbf5f`（该 commit 是祖先且各字节可由工作区命中，check 通过）；随后 evidence commit `30946decf` 冻结该
  日志与 manifest，本记录 commit 将全部行 pin 更新为 `30946decf`。检查结果（5 errors / 4 warnings）不受 pin
  数值影响；最终治理检查由 Codex 在主仓执行。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EV-AC1-CORE | AC1 | `tools/governance/clean_workspace.py` | `30946decf` | `9cfd68ed4744871f8ef5dd8e7c749218093cbce73e1dcd74e425b890c3851b72` | `CANONICAL` |
| EV-AC1-JUNCTION | AC1（F-01） | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_tools_fixtures.py` | `30946decf` | `9456979854f716c16320e295387059f1ad87fafdd52f6c50835dd8d2d6489b4b` | `SOURCE_PIN` |
| EV-AC2-WT | AC2 | `tools/governance/remove_worktrees.py` | `30946decf` | `5db35bbe08dc3dd7e8c9f23413872ab8195521ea15f7cd0e1666b7c8d469afec` | `CANONICAL` |
| EV-AC2-TESTS | AC2 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/tests.log` | `30946decf` | `6b46adeb7d8904ca3c2445fbe07e1e26184f0cd1e6de287fa4884bbf05d8713e` | `CANONICAL` |
| EV-AC3 | AC3 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/tests.log` | `30946decf` | `6b46adeb7d8904ca3c2445fbe07e1e26184f0cd1e6de287fa4884bbf05d8713e` | `CANONICAL` |
| EV-AC4 | AC4 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/ac-coverage.json` | `30946decf` | `986b9333b1c2ba125b91c691314b2ae3b3c416615de3cec5515bf46172c3530d` | `CANONICAL` |
| EV-AC5 | AC5 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/tests.log` | `30946decf` | `6b46adeb7d8904ca3c2445fbe07e1e26184f0cd1e6de287fa4884bbf05d8713e` | `CANONICAL` |
| EV-AC6 | AC6 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/incident-replay-clean-workspace.json` | `30946decf` | `8c5c72b3ae685bee1906f77f6987e220faae6214275a88e493c5236276c03cbb` | `CANONICAL` |
| EV-AC6-WT | AC6 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/incident-replay-remove-worktrees.json` | `30946decf` | `b11f8c21a9c2ba86eed4b44908796b992586371a9177d52f97a2c3e647fe7efa` | `CANONICAL` |
| EV-AC7 | AC7 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/environment.json` | `30946decf` | `69efe1ef4eb71c0f2c46ecea7bd7cf209df249b74b3003028013f0b130b527a8` | `CANONICAL` |
| EV-AC7-EXISTING | AC7 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/existing-test_ac_gate.py.log` | `30946decf` | `639947e13a6b7046210d85a817fc418eda18f49144f5b5fdd5f631745adc49ee` | `SOURCE_PIN` |
| EV-AC7-EXISTING2 | AC7 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/existing-run-resource-manifest-cases.py.log` | `30946decf` | `7ec53b200d745f7f8267634034df4dc88a13d9e13594919ce69d9443e8ddeb38` | `SOURCE_PIN` |
| EV-AC7-ARCHIVE | AC7 | `tools/governance/archive_branches.py` | `30946decf` | `42c35587493f8ee0993800c7a9265decc6a60b2e1f34b0a86b9702e497ed46b5` | `CANONICAL` |
| EV-AC7-DELETE | AC7 | `tools/governance/delete_branches.py` | `30946decf` | `2146c2349fbb03ac9b9e32be4c207f586aa0457a75cb8be1c3b5a87b767fdaa8` | `CANONICAL` |
| EV-AC7-CONSOLIDATE | AC7 | `tools/governance/consolidate.py` | `30946decf` | `734f1b6acb02fadc853fabaab5b3c3000e7d12f8166505a4c98ac582895c78a0` | `CANONICAL` |
| EV-AUDIT | AC1/AC2/AC6 补充 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/declaration-audit.json` | `30946decf` | `6fd800ff0a855c7483fb46cbc9bf6c41b0771213f165ba51ec02f942e499a68e` | `CANONICAL` |
| EV-AUDIT-LOG | AC1/AC2/AC6 补充 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/declaration-audit.log` | `30946decf` | `69401767843ba0d2443dab2f22906742363e331a013fb338a2ebde07d9a72b12` | `SOURCE_PIN` |
| EV-SNAPSHOT | Gate | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/real-workspace-snapshot.json` | `30946decf` | `b65cd04d70ea1fdfafddfb3277a205da2c7935cd3bf2d978ce308e8e7ca4d9d0` | `CANONICAL` |
| EV-RUNNER | Gate（可复算） | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/run_evidence.py` | `30946decf` | `6a0a1145c8ae1c0fb1e708f901f24966cf22ff541918a9acf070d1a9cb8b8f10` | `SOURCE_PIN` |
| EV-TEST-GUARD | AC1–AC3 测试源码 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_guard_core.py` | `30946decf` | `7461f1ec8480adf37e7f3cb495f104efc573f153d3a99be0c18840ba0680fcbd` | `SOURCE_PIN` |
| EV-TEST-FIXTURES | AC2–AC5 测试源码 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_tools_fixtures.py` | `30946decf` | `9456979854f716c16320e295387059f1ad87fafdd52f6c50835dd8d2d6489b4b` | `SOURCE_PIN` |
| EV-TEST-REPLAY | AC6 测试源码 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_incident_replay.py` | `30946decf` | `bf4a59f81e05d2c5b727ceee1c189b54cd178a05b9a81e7236b8b5aebc8415b3` | `SOURCE_PIN` |
| EV-TEST-OTHER | AC7 测试源码 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/test_other_tools.py` | `30946decf` | `f6c2a81cecb6d07171f640004dddfdd83ad15de8c11b207756fed26963d901e9` | `SOURCE_PIN` |
| EV-TEST-SUPPORT | 测试夹具 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/fixture_support.py` | `30946decf` | `c591bdd3727cd2426e8f30baa5f54e7ea3c975fbd3c1664fe6e99b9ac139752a` | `SOURCE_PIN` |
| EV-TEST-RUNNER | 测试运行器 | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests/run_suite.py` | `30946decf` | `0cb2b75dad75f2316ded3322a3f98b2f4ef1877b5fe287188de75232beff297b` | `SOURCE_PIN` |
| EV-CHECK | 治理检查日志（过程证据） | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/governance-check.log` | `30946decf` | `4b7ddc851e477b2264fd21ec575c6f8cf6ec0f70ec4ddeb00bd8b96f0266cb21` | `SOURCE_PIN` |
| EV-MANIFEST | 证据清单（过程证据） | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/evidence/manifest.sha256` | `30946decf` | `5dbf2a6dd5ae613f6e401dbfccea97460fc190675bbee622a1a07a6248f2d848` | `SOURCE_PIN` |
| EV-28 | 交付 Handoff | `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/HANDOFF.md` | `1dc8a8944` | `6ddcadb8c922736ac65c4352c22ec7a247999c2ee51100949c00d859febde048` | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| NOT_APPLICABLE | - | NOT_APPLICABLE | - | - | 本 Task 为工具修复，不产生、不迁移、不删除任何工作区资源；测试与 apply 验证均在 `%TEMP%` 隔离夹具，真实工作区前后快照一致（`evidence/real-workspace-snapshot.json`） |

## Closeout Record

- Closeout date / Codex：2026-10-21；Codex R1→R2→R3→**R4 `approved`**（0 阻塞 finding）；主仓集成 commit `368c0780974ada5879d165526c60d41ee0fc8dc2`；Task 状态 `done`。
- canonical_evidence_status：`complete`（27 条证据行，commit pin 全部为 evidence commit `30946decf`，
  SHA-256 与该 commit 的 Git blob 字节逐项一致；`governance-check.log`、`manifest.sha256` 亦在同一 evidence commit 内）。
- resource_closeout_status：`complete`（无 worktree/task-env/artifact/exchange 等资源需处置；未执行任何真实删除）。
- 删除、迁移、归档数量/字节数：0（本 Task 禁止实际删除；测试仅删除 `%TEMP%` 夹具）。
- 未关闭项及保留原因：真实仓库 163 条历史声明完整性错误（含 69 条不可解析 JSON、7 条 path-like destination）
  → 工具 fail-closed 拒绝清理，需另立 Task 或 Codex/用户裁定；既有 `run-resource-manifest-cases.py` 0/32 为
  check.ps1/task_ledger 仓库状态问题，范围外如实保留。
- 当前指针清理：未修改 Plan/STATUS/其他 Task/历史 Review；worktree 缺少主仓未跟踪 drafts/archive 内容，
  治理检查留有既有 TASK_LEDGER 计数与 stale 引用差异，最终治理检查由 Codex 在主仓执行。

## 释放记录（2026-10-21，用户授权）

- 用户裁决：释放（"1释放"）。Owner：`dsh-workspace-hardening`（DSH teammate）；Reviewer：Codex。
- 范围冻结：沿用本 Task `allowed_paths`（5 个工具脚本 + 本 Task + evidence 目录），不扩大；Codex 在交付时独立复核。
- Base：`b8a1e519703f13af73b320dded117004b4bb189a`；worktree：`G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1`；分支：`dsh/WORKSPACE-CLEANUP-TOOL-HARDENING-1`。
- 硬边界不变：不授权、不执行任何真实删除/移动/分支清理/GC/prune/push；默认 dry-run。

## 集成记录（2026-10-21，Lead）

- 分支 `dsh/WORKSPACE-CLEANUP-TOOL-HARDENING-1` 已合并入治理主线：merge commit `368c0780974ada5879d165526c60d41ee0fc8dc2`（evidence commit `30946decf`、最终代码 commit `b0ad9f8d1`、delivery_head 见 frontmatter）。
- Codex Review 链：R1 changes_requested（F-01..F-07）→ R2 changes_requested（F-02/F-05 残余）→ R3 changes_requested（仅 docstring 矛盾 R3-F02-DOC）→ **R4 approved**（0 阻塞 finding，可进入集成）。
- 集成验证：证据 27/27 行、manifest 11/11 在主线复算通过；Task/Plan/STATUS/台账已同步；默认治理检查 PASS。
- 状态保持 `in_review`：按 Codex R4“集成验证完成前不应标记 done”与项目生命周期，最终 `done` 收口与签名/发布裁定一并处理；本 Task 无未完成实现项。
