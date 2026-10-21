---
id: WORKSPACE-DECLARATION-REMEDIATION-1
title: 真实仓库声明完整性错误的分诊与解析精度修复（163 → 残余，review r2 加固）
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
delivery_head: 2c38980c98385be79e4d67e801a954d698955c80
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

来源：`WORKSPACE-CLEANUP-TOOL-HARDENING-1` 交付后，真实仓库 `--audit-declarations` 为
**1858 declarations / 1264 roots / 163 errors / 54 warnings**，工具 fail-closed 拒绝清理。

第一版（`dca07bd3d`）把 errors 降到 15，但 Codex Review r2 判定 `changes_requested`：4 个 P1
fail-closed 缺口（F-01 叙述启发式跳过 path-like、F-02 instrumentation 文件名可绕过 fatal、F-03
泛化 destination 降级、F-04 不完整 schema 跳过）+ 4 个 P2。返修后**安全优先、不追求 ≤10**。

实际结果（2026-10-21，review r2 返修后）：**163 errors → 76 errors（+236 warnings）**。
76 条全部逐条列于 `RESIDUAL.md`（含原始 `message`）。多数新增 error 是 Review 要求恢复的
fail-closed 语义：F-01 使 8 条 path-like prose 恢复 fatal，F-03 使 6 条泛化 destination 恢复 fatal，
F-04 使 44 个不完整 identity 表恢复 fatal，F-05 拒绝 3 个含 NUL/UTF-16 的损坏文件与任意短/高控制字符二进制。**不宣称 0，
不为凑 ≤10 削弱安全**。

## Acceptance Criteria

- [x] **AC1 分诊清单**：`REMEDIATION.md`（before/after 数字与横向对比）+ `TRIAGE.md`（163 行逐条：
  code/file/tracked/owner/locator/category/decision）+ `audit-before.json` + `audit-after.json`；
  无遗漏、无静默。 <<MET>>
- [x] **AC2 JSON 声明识别（review F-02）**：BOM 容错；不可解析 JSON 只有精确 `path + sha256` 命中
  `non-declaration-json-exceptions.json`（67 条已审阅日志）才降为 `JSON_NON_DECLARATION` warning；
  文件名启发式已删除，真声明改名为 `*.stdout.json` 或截断在 token 前一律 fatal；sha 不匹配则不豁免。
  JSON_PARSE **69 → 2**（2 条含 token 的历史 JSON 仍 fatal）。新增 4 个正反例夹具。 <<MET>>
- [x] **AC3 非路径 source（review F-01）**：只有明确占位符/纯 prose（无路径语法）跳过；一旦
  `is_path_like()` 为真必须解析，不可解析则 fatal（含空格/CJK 的真实路径被保护，嵌入路径的说明
  文字 fatal）。DECL_BARE_NAME **57 → 0**；DECL_RELATIVE_UNRESOLVED **0 → 6**、DECL_UNKNOWN_DISPOSITION
  **0 → 2** 是 F-01 恢复 fail-closed 的预期结果。新增 7 个夹具（含空格/CJK 真实路径、已存在顶层单组件路径保护正例）。 <<MET>>
- [x] **AC4 历史编码（review F-05）**：严格 GB18030 fallback 仅接受含 CJK 的文本；NUL、控制字符比例
  过高或非 CJK 的二进制 payload 一律 `FILE_UNREADABLE`。3 个 P02/P04 GBK 文件 → `FILE_ENCODING_LEGACY`
  warning；3 个含 NUL/UTF-16 的损坏文件 → `FILE_UNREADABLE` error（新增，fail-closed）。新增 4 个夹具。 <<MET>>
- [x] **AC5 表格识别（review F-03/F-04）**：Resource Manifest/Canonical Evidence 只有在不声明任何
  identity 列时才是叙述表（warning）；声明了 identity 列但缺必要列 → `TABLE_SCHEMA_INCOMPLETE`
  fatal；path-like 泛化 destination → `DECL_DESTINATION_GENERALIZED` fatal；真正 malformed 行 →
  `TABLE_ROW_ARITY` fatal。新增 5 个夹具。 <<MET>>
- [x] **AC6 残余清单**：`RESIDUAL.md` 逐条 76 条（file/code/message/tracked/owner/why-not-precision/
  ruling），并解释为何 76 不是 0、为何不追求 ≤10。 <<MET>>
- [x] **AC7 回归与证据**：既有 80 tests 全过；新增 20 tests 全过；双 incident replay 15/15 REJECT、
  0 删除、18/18 source；`run_evidence.py` exit 0；真实审计 exit 2 且 76 errors 如实记录；未执行任何
  真实删除/GC/prune/push；Canonical Evidence 行 pin evidence commit。 <<MET>>

## 允许修改范围

- `tools/governance/clean_workspace.py`（共享解析核心）。
- `verification/WORKSPACE-DECLARATION-REMEDIATION-1/`（报告、夹具、日志、manifest、精确豁免清单）。
- 本 Task 文件与 `doc/handoffs/`。
- **未修改**任何历史 Task/证据/untracked 文件、Plan/STATUS/check.ps1/task_ledger.py/主仓库。

## 禁止范围

- 未削弱 F-01（junction realpath）、F-02（JSON fail-closed）、F-03（destination 完整性）、F-04（`--out`
  防自删）等语义；Review r2 后反而恢复了 F-01/F-03/F-04 的 fatal 语义。
- 未删除/移动/归档任何真实文件；未 push/GC/prune/历史重写；未修改 `doc/` 下除本 Task 外文件。

## 测试要求

| 场景/AC | 命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| 新增 AC2–AC5/F-01…F-05 夹具 | `C:/Python314/python.exe -B -m unittest test_declaration_remediation -v`（cwd `verification/WORKSPACE-DECLARATION-REMEDIATION-1/tests`） | Windows 11 / Python 3.14.6；`%TEMP%` 隔离仓库 | **executed**：`Ran 20 tests` / `OK`，exit `0` | `tests.log`、`evidence/new-tests.log` |
| 既有 80 tests | `C:/Python314/python.exe -B run_suite.py`（cwd `verification/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tests`，只读） | 同上 | **executed**：`Ran 80 tests` / `OK`，exit `0` | `evidence/existing-tests.log` |
| incident replay（clean_workspace） | `python -B tools/governance/clean_workspace.py --replay-incident verification/WORKSPACE-CONSOLIDATION-1/incident-ledger-r208.json --out <taskdir>` | 只读 ledger | **executed**：15/15 REJECT、0 删除、0 violation、18/18 source，exit `0` | `incident-replay-clean-workspace.json` |
| incident replay（remove_worktrees） | 同上换 `remove_worktrees.py` | 同上 | **executed**：15/15/0/0/18，exit `0` | `incident-replay-remove-worktrees.json` |
| 真实审计 after | `python -B tools/governance/clean_workspace.py --repo G:/CODEX/New Manga --workspace-root G:/CODEX/New Manga.workspace --audit-declarations --out <dir>` | 只读、同一仓库快照 | **executed**：1858 declarations / 1264 roots / **76 errors** / 236 warnings，exit `2`（fail-closed） | `audit-after.json`、`evidence/audit-after.log` |
| 保护未削弱 | `python -B protection_delta.py` | 比较旧/新解析器声明集合 | **executed**：旧 1858/1264 → 新 1858/1264；无真实保护丢失 | `evidence/protection-delta.json` |
| 复算 | `python -B verification/WORKSPACE-DECLARATION-REMEDIATION-1/run_evidence.py` | 同上 | **executed**：`evidence-ok`，exit `0` | `evidence/environment.json`、`evidence/manifest.sha256` |

## 依赖、风险与阻塞

- 依赖：`WORKSPACE-CLEANUP-TOOL-HARDENING-1` 的 F-01…F-07 安全语义（80 tests 全过）。
- 风险：76 条残余中 6 泛化声明、4 env、1 歧义相对路径、2 JSON_PARSE、1 malformed 行、1 path-like
  destination prose 需 Codex/用户裁定；其余 61 条是 review r2 恢复 fail-closed 后的真实历史缺口
  （44 个不完整 identity 表、8 条 path-like prose、6 个泛化 destination、3 个损坏文件；r3 另加存在顶层条目探测与短二进制拒绝）。详见
  `RESIDUAL.md`。未修改任何历史文件；所有跳过项都有 warning 且不登记保护。

## 交付与运行记录

- 分诊/修复：`REMEDIATION.md`、`TRIAGE.md`（163 行逐条）、`RESIDUAL.md`（76 条 + message + 原因）、
  `non-declaration-json-exceptions.json`（67 条 path+sha256+reason）。
- 证据：`audit-before.json`（163 errors / exit 2）、`audit-after.json`（76 errors / exit 2）、
  `tests.log`、`evidence/`（logs、environment、manifest、triage-summary、protection-delta）。
- 提交：evidence commit `2c38980c9`（代码/测试/报告/日志/manifest 冻结）→ Task-only 记录 commit；Canonical
  Evidence 行 pin evidence commit；`delivery_head` 指向它。
- 治理检查：worktree 内 `check.ps1` 结果与 exit 见 `evidence/governance-check.log`；既有 7 类
  base 问题（TASK_LEDGER 过期、archive stale、REBASELINE_PLAN 预算、READY DAG）由 Lead/Codex
  在主仓集成时处理；最终治理检查由 Codex 执行。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EV-CODE | AC2–AC5 | `tools/governance/clean_workspace.py` | `2c38980c98385be79e4d67e801a954d698955c80` | `6747ba69bbbb1dc8c34d7c88cb7f527ea5b3ea08777058da4f70708ac6ea79d6` | `CANONICAL` |
| EV-TESTS-NEW | AC2–AC5/F-01…F-05 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/tests/test_declaration_remediation.py` | `2c38980c98385be79e4d67e801a954d698955c80` | `70698e4f94af68b2fa3950f750993bed878e11fed471ad082b06dda8c15723e0` | `CANONICAL` |
| EV-JSON-EXCEPTIONS | AC2/F-02 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/non-declaration-json-exceptions.json` | `2c38980c98385be79e4d67e801a954d698955c80` | `c2f185fb489e4b89be28cdfb139eb649c7022a718d0d27877be4ca0d8fa4adc4` | `CANONICAL` |
| EV-AUDIT-BEFORE | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/audit-before.json` | `2c38980c98385be79e4d67e801a954d698955c80` | `a6aa479199f804fa0b49d5dac4761680ee072068f964b4a8cf1811d619b43273` | `CANONICAL` |
| EV-AUDIT-AFTER | AC2–AC6 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/audit-after.json` | `2c38980c98385be79e4d67e801a954d698955c80` | `d8cd63e57870a1e396dc25bc5c181adf817d999d1e2c8c1c7882e24b7eae3c14` | `CANONICAL` |
| EV-SNAPSHOTS | AC1/AC7 same snapshot | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/audit-snapshots.json` | `2c38980c98385be79e4d67e801a954d698955c80` | `c0883a1ba2e6d6d390eda834ec47a37a43074b75b4316c84c593e0cdc6099a7a` | `CANONICAL` |
| EV-REMEDIATION | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/REMEDIATION.md` | `2c38980c98385be79e4d67e801a954d698955c80` | `6dc2239860528b6f37634d9f6e0defd1757a4be5ba1160a6bde29733229e916f` | `CANONICAL` |
| EV-RESIDUAL | AC6 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/RESIDUAL.md` | `2c38980c98385be79e4d67e801a954d698955c80` | `986118f24ccb0d626dc00822852fae7173876364a3f673d9194e49ae885241ef` | `CANONICAL` |
| EV-TRIAGE | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/TRIAGE.md` | `2c38980c98385be79e4d67e801a954d698955c80` | `72318d84e9f3ed4a097e2dbe20671d522e94d6423ab70df2e1ba3a7392322f82` | `CANONICAL` |
| EV-TESTS-LOG | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/tests.log` | `2c38980c98385be79e4d67e801a954d698955c80` | `7f853c75e5882e56ac0c88d1fba04304ff51b2fd6555b5c0da89f6cce1f9c7c0` | `CANONICAL` |
| EV-NEW-TESTS-LOG | AC2–AC5 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/new-tests.log` | `2c38980c98385be79e4d67e801a954d698955c80` | `7f853c75e5882e56ac0c88d1fba04304ff51b2fd6555b5c0da89f6cce1f9c7c0` | `SOURCE_PIN` |
| EV-EXISTING-LOG | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/existing-tests.log` | `2c38980c98385be79e4d67e801a954d698955c80` | `b3c98cdc1160a4f22a05a6281b1cfee1f03a8b2dd882fd8fb3096ee8034a0625` | `SOURCE_PIN` |
| EV-REPLAY-CLEAN | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/incident-replay-clean-workspace.json` | `2c38980c98385be79e4d67e801a954d698955c80` | `9b0881c2cb788b68dd56262b4e25134468775f6f8252cb2d5f5ce83cf647af01` | `CANONICAL` |
| EV-REPLAY-WT | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/incident-replay-remove-worktrees.json` | `2c38980c98385be79e4d67e801a954d698955c80` | `b1fe0864f49bf4d56ff4d3b82c7d9e89c0f01ef46f289293826ab1e8fdba083b` | `CANONICAL` |
| EV-REPLAY-LOG-CLEAN | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/incident-replay-clean_workspace.log` | `2c38980c98385be79e4d67e801a954d698955c80` | `1b6e7ecbe02e31521f27faf405f9338c3160848c4bbe425ebf73fd29f38c2069` | `SOURCE_PIN` |
| EV-REPLAY-LOG-WT | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/incident-replay-remove_worktrees.log` | `2c38980c98385be79e4d67e801a954d698955c80` | `b260568f8b7e0165788c106695182637d26adfffafc70ec810d5befc72acb335` | `SOURCE_PIN` |
| EV-ENV | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/environment.json` | `2c38980c98385be79e4d67e801a954d698955c80` | `2ccce55110c1ec9a65c9b47910a9c01901d19dc93f8be050f49be28d3a6adc7c` | `CANONICAL` |
| EV-TRIAGE-SUMMARY | AC1/AC6 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/triage-summary.json` | `2c38980c98385be79e4d67e801a954d698955c80` | `26a31cccb411409267b5d12712daa8ee56cf10e903842155fa5ef09c5acab067` | `SOURCE_PIN` |
| EV-DELTA | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/protection-delta.json` | `2c38980c98385be79e4d67e801a954d698955c80` | `af68b5cc3092fdd1a6e5d01799a12b3367f66e9a5791c2879e028626b7e7ac5e` | `CANONICAL` |
| EV-DELTA-LOG | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/protection-delta.log` | `2c38980c98385be79e4d67e801a954d698955c80` | `23454b9f5fe2d782b618be69bb74887a9bc125cf8f6a66b8985453d242c01f8d` | `SOURCE_PIN` |
| EV-DELTA-SCRIPT | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/protection_delta.py` | `2c38980c98385be79e4d67e801a954d698955c80` | `b2011dfdc8b2b5569bcd45b7ae7cb045b640035ac89a81894b7589abd6a7521b` | `SOURCE_PIN` |
| EV-RUNNER | Gate（可复算） | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/run_evidence.py` | `2c38980c98385be79e4d67e801a954d698955c80` | `7809e40b2b8b6ca169fa8df52995e3519b8f06a05c7c4e8c33bf5e5da4b94d55` | `SOURCE_PIN` |
| EV-BUILD-REPORTS | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/build_reports.py` | `2c38980c98385be79e4d67e801a954d698955c80` | `e467f4985b80e1157064912ecb6bdaffc62577b656740f2fe31949f8b981db70` | `SOURCE_PIN` |
| EV-BUILD-LOG | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/build-reports.log` | `2c38980c98385be79e4d67e801a954d698955c80` | `26d3045912e33ea4d97b7d16bcf193cfb6d125976aae71985f41559c00cd106c` | `SOURCE_PIN` |
| EV-AUDIT-BEFORE-LOG | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/audit-before.log` | `2c38980c98385be79e4d67e801a954d698955c80` | `e87bb95973f4f7aec82b18aa71d721a395c767bb6636129229e03762abdc34ce` | `SOURCE_PIN` |
| EV-AUDIT-AFTER-LOG | AC2–AC6 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/audit-after.log` | `2c38980c98385be79e4d67e801a954d698955c80` | `e02002d4503dd4525a40e682c4bcb026385d39f04f2c7609e16267bd2cb99261` | `SOURCE_PIN` |
| EV-AUDIT-BEFORE-EXITCODE | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/audit-before.exitcode` | `2c38980c98385be79e4d67e801a954d698955c80` | `53c234e5e8472b6ac51c1ae1cab3fe06fad053beb8ebfd8977b010655bfdd3c3` | `SOURCE_PIN` |
| EV-AUDIT-AFTER-EXITCODE | AC2–AC6 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/audit-after.exitcode` | `2c38980c98385be79e4d67e801a954d698955c80` | `53c234e5e8472b6ac51c1ae1cab3fe06fad053beb8ebfd8977b010655bfdd3c3` | `SOURCE_PIN` |
| EV-CHECK | Gate（治理检查日志） | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/governance-check.log` | `2c38980c98385be79e4d67e801a954d698955c80` | `5e6d76c86489b06a235e2db29ed2a1d3185f782b2c07a1c9389d971c88bb503f` | `SOURCE_PIN` |
| EV-MANIFEST | Gate（证据清单） | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/manifest.sha256` | `2c38980c98385be79e4d67e801a954d698955c80` | `1e3d09f39b8871106a97d609bcdb0012edf73b4a61a32b2cf66dd12ffc047e1f` | `SOURCE_PIN` |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| NOT_APPLICABLE | - | NOT_APPLICABLE | - | - | 本 Task 为只读解析器修复；不产生、不迁移、不删除任何资源。测试夹具均在 `%TEMP%` 隔离仓库；真实仓库审计只读、exit 2、0 删除。 |

## Closeout Record

- Closeout date / Codex：待 Codex 独立 Review 与主仓集成后填写（本 Task 状态 `in_review`）。
- canonical_evidence_status：`complete`（证据行 pin evidence commit；`governance-check.log` 另记）。
- resource_closeout_status：`complete`（无资源需处置；未执行任何真实删除）。
- 删除、迁移、归档数量/字节数：0。
- 未关闭项：76 条残余声明错误（`RESIDUAL.md`）；详见风险段。
- 当前指针清理：未修改 Plan/STATUS/其他 Task/历史 Review；最终治理检查由 Codex 在主仓执行。
