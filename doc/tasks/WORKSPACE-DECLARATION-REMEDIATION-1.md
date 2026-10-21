---
id: WORKSPACE-DECLARATION-REMEDIATION-1
title: 真实仓库声明完整性错误的分诊与解析精度修复（163 → 仅保留已裁定残余）
kind: governance-hardening
governance_version: 2
status: in_review
approval: user_authorized_20261021_declaration_followup
suggested_owner: DeepSeek Harness
owner: workspace-hardening
reviewer: Codex
depends_on: [WORKSPACE-CLEANUP-TOOL-HARDENING-1]
base_commit: 83b111ac104d47b30cf0842f553f97656cd0d8d1
branch: dsh/WORKSPACE-DECLARATION-REMEDIATION-1
worktree: G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1
integration_commit: null
delivery_head: dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1
canonical_evidence_status: complete
resource_closeout_status: complete
start_commit: f0f19596f
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
导致工具对真实仓库 fail-closed 拒绝清理。

目标：完成 163 条错误逐条分诊；修复解析器误报/精度问题；**不削弱** F-01…F-07 安全语义；剩余真实缺口
进入显式 `RESIDUAL.md`（含 file/code/tracked/owner/原因/裁定建议），不静默忽略、不宣称 0。

**实际结果（2026-10-21）：163 errors → 15 errors（+239 warnings）**。15 条残余全部逐条列于
`RESIDUAL.md`；其中 10 条（6 泛化声明 + 4 env）为 Task 明确要求保留待裁定的策略性缺口，5 条为真实
非策略残余（2 个含 token 的不可解析 JSON、1 个歧义相对路径、1 个真正 malformed 资源表、1 个 path-like
destination prose）。**未达到 ≤10 目标**：达到 10 必须削弱 fail-closed 或改写冻结历史，二者都被 Task 禁止，
详见 RESIDUAL.md「Why 15 rather than <=10」。未修改任何历史 Task/证据/untracked 文件。

## Acceptance Criteria

- [x] **AC1 分诊清单**：`REMEDIATION.md` + `audit-before.json` + `TRIAGE.md`（逐条 163 行：code/file/
  tracked/owner/locator/category/decision）+ `audit-after.json`；每类根因与处理决定齐全，无遗漏。 <<MET>>
- [x] **AC2 JSON 声明文件识别**：BOM 容错加载；不可解析 JSON 仅在（含声明 token | 文件名像声明清单 |
  tracked 且非 instrumentation）时 fatal，否则 `JSON_NON_DECLARATION` warning。新增 4 个正反例夹具
  （untracked instrumentation → warning；token → fatal；manifest 名 → fatal；tracked artifact → fatal）。
  真实审计 JSON_PARSE **69 → 2**，两条均为含 `disposition` token 的 `run-baseline-*.json`（RESIDUAL 说明）。 <<MET>>
- [x] **AC3 非路径 source 值**：`NOT_APPLICABLE`/`none yet`/中文说明/占位符 → `DECL_SOURCE_NOT_A_PATH`
  warning 并跳过（不登记保护）；bare 标识符仍 `DECL_BARE_NAME` fatal；真实 path-like `PRESERVE_*` 失败仍
  fatal。新增 4 个夹具（NOT_APPLICABLE、none yet+中文、bare 仍 fatal、真实路径仍保护）。
  DECL_BARE_NAME **57 → 0**，DECL_UNKNOWN_DISPOSITION **9 → 0**，DECL_RELATIVE_UNRESOLVED **6 → 0**。 <<MET>>
- [x] **AC4 历史编码兼容**：`read_text` 非法 UTF-8 → GB18030 严格解码 + `FILE_ENCODING_LEGACY` warning；
  两种编码都失败仍 `FILE_UNREADABLE`。新增 GBK 正例（保护仍生效）与坏字节反例。FILE_UNREADABLE **3 → 0**，
  warning 3 条（P02 ×2、P04 ×1）。 <<MET>>
- [x] **AC5 叙述表格识别**：Resource Manifest / Canonical Evidence 仅接受精确英文 schema
  （`resource_type`/`source_path` + `disposition`；`evidence_id`+`path`）；叙述/中文表格跳过并
  `TABLE_NOT_RESOURCE_MANIFEST` / `TABLE_NOT_CANONICAL_EVIDENCE` warning；真正 malformed 资源表仍
  `TABLE_ROW_ARITY` fatal。新增 4 个夹具（中文叙述表、英文叙述表、malformed、叙述 evidence 表）。 <<MET>>
- [x] **AC6 残余清单**：`RESIDUAL.md` 逐条列出 15 条残余（file/code/message/tracked/owner/为何不能由解析精度
  修复/建议裁定），并明确说明 **15 不是 0**、为何未达 ≤10。 <<MET>>
- [x] **AC7 回归与证据**：既有 80 tests 全过（只读副本运行，exit 0）；新增 14 tests 全过；两个 incident replay
  15/15 REJECT、0 删除、18/18 source；`run_evidence.py` exit 0；真实仓库 `--audit-declarations` exit 2 且
  15 errors 如实记录；未执行任何真实删除/GC/prune/push；Canonical Evidence 行 pin evidence commit。 <<MET>>

## 允许修改范围

- `tools/governance/clean_workspace.py`（共享解析核心；未改其它工具行为）。
- `verification/WORKSPACE-DECLARATION-REMEDIATION-1/`（报告、夹具、测试、日志、manifest）。
- 本 Task 文件与 `doc/handoffs/`。
- **未修改**任何历史 Task/证据/untracked 文件、Plan/STATUS/check.ps1/task_ledger.py/主仓库。

## 禁止范围

- 未削弱 F-01（junction realpath）、F-02（untracked 声明/不可解析 JSON fail-closed）、F-03（path-like
  destination）、F-04（`--out` 防自删）等语义；tracked 非 instrumentation 不可解析 JSON 仍 fatal。
- 未删除/移动/归档任何真实文件；未 push/GC/prune/历史重写；未修改 `doc/` 下除本 Task 外文件。

## 测试要求

| 场景/AC | 命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| 新增 AC2–AC5 夹具 | `C:/Python314/python.exe -B -m unittest test_declaration_remediation -v`（cwd `verification/WORKSPACE-DECLARATION-REMEDIATION-1/tests`） | Windows 11 / Python 3.14.6；`%TEMP%` 隔离仓库；`PYTHONPYCACHEPREFIX` 指向 workspace temp | **executed**：`Ran 14 tests` / `OK`，exit `0` | `tests.log`、`evidence/new-tests.log` |
| 既有 80 tests | `C:/Python314/python.exe -B run_suite.py`（cwd `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests`，只读） | 同上 | **executed**：`Ran 80 tests` / `OK`，exit `0` | `evidence/existing-tests.log` |
| incident replay（clean_workspace） | `python -B tools/governance/clean_workspace.py --replay-incident verification/WORKSPACE-CONSOLIDATION-1/incident-ledger-r208.json --out <taskdir>` | 只读 ledger | **executed**：15 candidates / 15 rejected / 0 deleted / 0 violations / 18 sources，exit `0` | `incident-replay-clean-workspace.json` |
| incident replay（remove_worktrees） | 同上换 `remove_worktrees.py` | 同上 | **executed**：15/15/0/0/18，exit `0` | `incident-replay-remove-worktrees.json` |
| 真实审计 after | `python -B tools/governance/clean_workspace.py --repo G:/CODEX/New Manga --workspace-root G:/CODEX/New Manga.workspace --audit-declarations --out <dir>` | 只读，同一仓库快照 | **executed**：1855 declarations / 1262 roots / **15 errors** / 239 warnings，exit `2`（fail-closed） | `audit-after.json`、`evidence/audit-after.log` |
| 保护未削弱 | `python -B protection_delta.py` | 比较旧/新解析器在真实仓库上的声明集合 | **executed**：旧 1858/1264 → 新 1855/1262；3 条被移除声明均为旧解析器误登记为保护的 prose 串，检查后不指向任何现有路径；无真实保护丢失 | `evidence/protection-delta.json` |
| 复算 | `python -B verification/WORKSPACE-DECLARATION-REMEDIATION-1/run_evidence.py` | 同上 | **executed**：`evidence-ok`，exit `0` | `evidence/environment.json`、`evidence/manifest.sha256` |

## 依赖、风险与阻塞

- 依赖：`WORKSPACE-CLEANUP-TOOL-HARDENING-1` 的 F-01…F-07 安全语义（回归 80 tests 全过）。
- 风险：15 条残余中有 10 条需 Codex/用户裁定（泛化 workspace root 声明、`%TEMP%`/`%APPDATA%` env 路径）；
  另有 2 条含 token 的历史 JSON 日志、1 个 malformed 资源表、1 个歧义相对路径、1 个 path-like destination
  prose。详见 `RESIDUAL.md`。解析精度修复未改任何历史文件；`DECL_SOURCE_NOT_A_PATH` 等新 warning 是
  保守跳过（不登记保护、不授权删除）。

## 交付与运行记录

- 分诊/修复：`REMEDIATION.md`（含 before/after 数字与横向对比）、`TRIAGE.md`（163 行逐条）、
  `RESIDUAL.md`（15 条残余 + ≤10 未达原因）。
- 证据：`audit-before.json`（修复前，163 errors / exit 2）、`audit-after.json`（修复后，15 errors / exit 2）、
  `tests.log`、`evidence/`（logs、environment、manifest、triage-summary、protection-delta）。
- 提交：evidence commit `dca07bd3d`（代码/测试/报告/日志/manifest 冻结）→ Task-only 记录 commit（本文件；Canonical Evidence 行 pin `dca07bd3d`，`delivery_head` 指向它）。
  Canonical Evidence 行 pin evidence commit；`delivery_head` 指向最终代码 commit。
- 治理检查：worktree 内运行 `check.ps1 -TaskPath doc/tasks/WORKSPACE-DECLARATION-REMEDIATION-1.md` → exit `1`，`FAIL (7 errors, 3 warnings)`：2 条 TASK_LEDGER 过期、3 条既有 `archive/history` stale 引用、`REBASELINE_PLAN` 预算超限、以及 READY DAG 仍只允许 `ready`（本 Task 已 `in_review`，由 Lead/Codex 在主仓同步）；未修改 Plan/STATUS/check.ps1/task_ledger.py。原始输出+exit 见 `evidence/governance-check.log`，最终治理检查由 Codex 在主仓集成后执行。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EV-CODE | AC2–AC5 | `tools/governance/clean_workspace.py` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `4c803ab869fb0acd2f1a9b53785d6dc55ee5b33314d86aaa6158720c8df41454` | `CANONICAL` |
| EV-TESTS-NEW | AC2–AC5 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/tests/test_declaration_remediation.py` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `0734435dec717a227b11a8f714501bb02084f80242adcd355100ebae5d5e0888` | `CANONICAL` |
| EV-AUDIT-BEFORE | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/audit-before.json` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `6038a36fe51e93a95bcf8cba7c094dd544bc187b403cd82908f0b85685e998ae` | `CANONICAL` |
| EV-AUDIT-AFTER | AC2–AC6 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/audit-after.json` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `5a5826e3a0772b65eca15ff2e5f6b18f7bc1ac8c371d989c144bf2dfe0dea2a9` | `CANONICAL` |
| EV-REMEDIATION | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/REMEDIATION.md` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `40654902054c883398c53ca4f5ee89ee1694eab038d912827b2888f28176ae4d` | `CANONICAL` |
| EV-RESIDUAL | AC6 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/RESIDUAL.md` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `8339320fa95e10764f07efe8a0fa1da97fb3747d0c3b1895b4d8a3cfac800630` | `CANONICAL` |
| EV-TRIAGE | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/TRIAGE.md` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `36d7e864a5e41441ab10f98f2d5a3f2d6d50121649a98cf291edd2fb0ad70d71` | `CANONICAL` |
| EV-TESTS-LOG | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/tests.log` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `310933dd1cc706cee0f1b730df2acad21caa773299c7cb7c42fb961fb5376a20` | `CANONICAL` |
| EV-NEW-TESTS-LOG | AC2–AC5 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/new-tests.log` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `310933dd1cc706cee0f1b730df2acad21caa773299c7cb7c42fb961fb5376a20` | `SOURCE_PIN` |
| EV-EXISTING-LOG | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/existing-tests.log` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `cbbf4bed5b999882aeaaee9dd2dcb9bc3c9d6fd8aba330727a24c9b247cfcd02` | `SOURCE_PIN` |
| EV-REPLAY-CLEAN | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/incident-replay-clean-workspace.json` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `8a735f46e182e31a6b3f925ad1db8a04eb4a972ce3e8d377342f21148dabb7e3` | `CANONICAL` |
| EV-REPLAY-WT | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/incident-replay-remove-worktrees.json` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `8a49ae3a4895492c54cf06603a23efa8da481e99c8eae7234b0f1366fa1a082f` | `CANONICAL` |
| EV-REPLAY-LOG-CLEAN | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/incident-replay-clean_workspace.log` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `1fcb5b91144080bc7b8988ac8e31608196c47cf996e6bb0db3ee0dce9078545d` | `SOURCE_PIN` |
| EV-REPLAY-LOG-WT | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/incident-replay-remove_worktrees.log` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `7b8ffc8e7d738c2d7d0bd6fc7b69a42056c04e4ea1d40451e0f6e241aca872d6` | `SOURCE_PIN` |
| EV-ENV | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/environment.json` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `36df5bfbe945d45872ca686efb0cd828d35325814ba5691d3226dab9d94cfc61` | `CANONICAL` |
| EV-TRIAGE-SUMMARY | AC1/AC6 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/triage-summary.json` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `fb16f725be1fd3e10cb02a395f251b173801385d543fccbbe5b77a59be7acb8c` | `SOURCE_PIN` |
| EV-DELTA | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/protection-delta.json` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `f3dd2abeb755ede5131ba74abca8b015dc2f1800b1ba551eed72bd0618d7c570` | `CANONICAL` |
| EV-DELTA-LOG | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/protection-delta.log` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `3447fc6e214fdc8d1cf483fbb10e67a93641f006d9be359f10355f3a905405bf` | `SOURCE_PIN` |
| EV-DELTA-SCRIPT | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/protection_delta.py` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `b2011dfdc8b2b5569bcd45b7ae7cb045b640035ac89a81894b7589abd6a7521b` | `SOURCE_PIN` |
| EV-RUNNER | Gate（可复算） | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/run_evidence.py` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `a097b954cc3ce82eb8eaee470dd14be6c7d9663bd77b16e70dd280c572c22d01` | `SOURCE_PIN` |
| EV-BUILD-REPORTS | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/build_reports.py` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `b0f8d8b3e9aab67896812d38ddfa91aa00d4acd3521e95bc9c58e030db7f6818` | `SOURCE_PIN` |
| EV-BUILD-LOG | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/build-reports.log` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `fa668d032048f4ba661f23f38823794dc10cfdde2a6836306abe467874d8fd6d` | `SOURCE_PIN` |
| EV-AUDIT-BEFORE-LOG | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/audit-before.log` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `64a16097c3c853680e5e561ec397bd202e860df5a76db5483a89e4915ffd19e7` | `SOURCE_PIN` |
| EV-AUDIT-AFTER-LOG | AC2–AC6 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/audit-after.log` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `763605821b785ed3b46264735f2846a3973115b472e964e89e372d1715ffe506` | `SOURCE_PIN` |
| EV-AUDIT-BEFORE-EXITCODE | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/audit-before.exitcode` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `53c234e5e8472b6ac51c1ae1cab3fe06fad053beb8ebfd8977b010655bfdd3c3` | `SOURCE_PIN` |
| EV-AUDIT-AFTER-EXITCODE | AC2–AC6 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/audit-after.exitcode` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `53c234e5e8472b6ac51c1ae1cab3fe06fad053beb8ebfd8977b010655bfdd3c3` | `SOURCE_PIN` |
| EV-CHECK | Gate（治理检查日志） | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/governance-check.log` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `a67c3f9d2993bb5c432063eaf041314150da6f840de707676cc8bff3a2e69001` | `SOURCE_PIN` |

| EV-MANIFEST | Gate（证据清单） | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/manifest.sha256` | `dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1` | `7d21d22e9d0f81eecf7a3b4a354cb13bee1232a724d91b5cec92e13bd4c18c8a` | `SOURCE_PIN` |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| NOT_APPLICABLE | - | NOT_APPLICABLE | - | - | 本 Task 为只读解析器修复；不产生、不迁移、不删除任何资源。测试夹具均在 `%TEMP%` 隔离仓库；真实仓库审计只读、exit 2、0 删除。 |

## Closeout Record

- Closeout date / Codex：待 Codex 独立 Review 与主仓集成后填写（本 Task 状态 `in_review`）。
- canonical_evidence_status：`complete`（23 条证据行 pin evidence commit；`governance-check.log` 另记）。
- resource_closeout_status：`complete`（无资源需处置；未执行任何真实删除）。
- 删除、迁移、归档数量/字节数：0。
- 未关闭项：15 条残余声明错误（`RESIDUAL.md`）；10 条需 Codex/用户裁定，5 条为真实解析/历史缺口。
- 当前指针清理：未修改 Plan/STATUS/其他 Task/历史 Review；最终治理检查由 Codex 在主仓执行。
