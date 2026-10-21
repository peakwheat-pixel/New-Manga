---
id: WORKSPACE-DECLARATION-REMEDIATION-1
title: 真实仓库声明完整性错误的分诊与解析精度修复（163 → 残余，review r2 加固）
kind: governance-hardening
governance_version: 2
status: done
approval: user_authorized_20261021_declaration_followup
suggested_owner: DeepSeek Harness
owner: workspace-hardening
reviewer: Codex
depends_on: [WORKSPACE-CLEANUP-TOOL-HARDENING-1]
base_commit: 83b111ac104d47b30cf0842f553f97656cd0d8d1
branch: dsh/WORKSPACE-DECLARATION-REMEDIATION-1
worktree: G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1
integration_commit: bb7887442475cebc80e037e8d34d219e0eb9bf19
delivery_head: cacd1c021a34c363f5b36d1b2b72f19f07acc081
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
F-04 使 44 个不完整 identity 表恢复 fatal，F-05 拒绝 3 个含 NUL/UTF-16 的损坏文件与任意短/高控制字符二进制；F-01 的 generalized junction 必须 fatal（source 与 evidence 两个入口）。**不宣称 0，
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
  **0 → 2** 是 F-01 恢复 fail-closed 的预期结果。新增 16 个夹具（含空格/CJK 真实路径、已存在顶层单组件路径、generalized junction 正反例、TRIAGE 多 code 归因）。 <<MET>>
- [x] **AC4 历史编码（review F-05）**：严格 GB18030 fallback 仅接受含 CJK 的文本；NUL、控制字符比例
  过高或非 CJK 的二进制 payload 一律 `FILE_UNREADABLE`。3 个 P02/P04 GBK 文件 → `FILE_ENCODING_LEGACY`
  warning；3 个含 NUL/UTF-16 的损坏文件 → `FILE_UNREADABLE` error（新增，fail-closed）。新增 4 个夹具。 <<MET>>
- [x] **AC5 表格识别（review F-03/F-04）**：Resource Manifest/Canonical Evidence 只有在不声明任何
  identity 列时才是叙述表（warning）；声明了 identity 列但缺必要列 → `TABLE_SCHEMA_INCOMPLETE`
  fatal；path-like 泛化 destination → `DECL_DESTINATION_GENERALIZED` fatal；重复 identity 列 →
  `TABLE_DUPLICATE_IDENTITY_COLUMN` fatal（不再静默取第一列）；真正 malformed 行 →
  `TABLE_ROW_ARITY` fatal。新增 8 个夹具（含 Resource Manifest/Canonical Evidence 重复列正反例）。 <<MET>>
- [x] **AC6 残余清单**：`RESIDUAL.md` 逐条 76 条（file/code/message/tracked/owner/why-not-precision/
  ruling），并解释为何 76 不是 0、为何不追求 ≤10。 <<MET>>
- [x] **AC7 回归与证据**：既有 80 tests 全过；新增 29 tests 全过；双 incident replay 15/15 REJECT、
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
| 新增 AC2–AC5/F-01…F-05 夹具 | `C:/Python314/python.exe -B -m unittest test_declaration_remediation -v`（cwd `verification/WORKSPACE-DECLARATION-REMEDIATION-1/tests`） | Windows 11 / Python 3.14.6；`%TEMP%` 隔离仓库 | **executed**：`Ran 29 tests` / `OK`，exit `0` | `tests.log`、`evidence/new-tests.log` |
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
  （44 个不完整 identity 表、8 条 path-like prose、6 个泛化 destination、3 个损坏文件；r3/r4 另加存在顶层条目探测、generalized junction 探测、短二进制拒绝、扫描输入内容快照、TRIAGE 角色+code 归因、README 自日志、重复 identity 列拒绝）。详见
  `RESIDUAL.md`。未修改任何历史文件；所有跳过项都有 warning 且不登记保护。

## 交付与运行记录

- 分诊/修复：`REMEDIATION.md`、`TRIAGE.md`（163 行逐条）、`RESIDUAL.md`（76 条 + message + 原因）、
  `non-declaration-json-exceptions.json`（67 条 path+sha256+reason）。
- 证据：`audit-before.json`（163 errors / exit 2）、`audit-after.json`（76 errors / exit 2）、
  `tests.log`、`evidence/`（logs、environment、manifest、triage-summary、protection-delta）。
- 提交：evidence commit `cacd1c021`（代码/测试/报告/日志/manifest 冻结）→ Task-only 记录 commit；Canonical
  Evidence 行 pin evidence commit；`delivery_head` 指向它。
- 治理检查：worktree 内 `check.ps1` 结果与 exit 见 `evidence/governance-check.log`；既有 7 类
  base 问题（TASK_LEDGER 过期、archive stale、REBASELINE_PLAN 预算、READY DAG）由 Lead/Codex
  在主仓集成时处理；最终治理检查由 Codex 执行。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EV-CODE | AC2–AC5 | `tools/governance/clean_workspace.py` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `544aea1ebd5202bd7c70b65a7e7c4a08e6a66d2c48eebec68f13a9c195066188` | `CANONICAL` |
| EV-TESTS-NEW | AC2–AC5/F-01…F-05 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/tests/test_declaration_remediation.py` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `a12a38c89d259021a5324542c8a550cc9336a6ef52096f681b7e3b3eb9ba70fa` | `CANONICAL` |
| EV-JSON-EXCEPTIONS | AC2/F-02 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/non-declaration-json-exceptions.json` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `c2f185fb489e4b89be28cdfb139eb649c7022a718d0d27877be4ca0d8fa4adc4` | `CANONICAL` |
| EV-AUDIT-BEFORE | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/audit-before.json` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `782420e81f545078354fd092c21f757f3f767fb8bc872dbd9d4d6bde599c354f` | `CANONICAL` |
| EV-AUDIT-AFTER | AC2–AC6 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/audit-after.json` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `134bb1fee298a297d063d5b3890f8b9c19ce1ed1090a5a9cf2bba1cfc30bcc03` | `CANONICAL` |
| EV-SNAPSHOTS | AC1/AC7 same snapshot | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/audit-snapshots.json` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `601c542ce0b0f08cb467774b3876004ded01cd345a8c03e580898ff85dd5a0b3` | `CANONICAL` |
| EV-REMEDIATION | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/REMEDIATION.md` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `e0943a28df52a5276fbbc6451ab30823deda876007bac4556756816097e2fc41` | `CANONICAL` |
| EV-RESIDUAL | AC6 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/RESIDUAL.md` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `986118f24ccb0d626dc00822852fae7173876364a3f673d9194e49ae885241ef` | `CANONICAL` |
| EV-TRIAGE | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/TRIAGE.md` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `be04e10274d8066ae51df73143ed07d9c6080dad0d2988c46a0457308387aa7f` | `CANONICAL` |
| EV-TESTS-LOG | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/tests.log` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `108b346f80c12c8c2de20da0f3e89fbd33cc8ed18fb45f72b26b5fc1d1365af7` | `CANONICAL` |
| EV-NEW-TESTS-LOG | AC2–AC5 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/new-tests.log` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `108b346f80c12c8c2de20da0f3e89fbd33cc8ed18fb45f72b26b5fc1d1365af7` | `SOURCE_PIN` |
| EV-EXISTING-LOG | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/existing-tests.log` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `848c28687dd31dda672495376c269a1c2478a9b13e3ba5257523de9217f0498f` | `SOURCE_PIN` |
| EV-REPLAY-CLEAN | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/incident-replay-clean-workspace.json` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `c7143fdb7394a12d811a62cb93a7f5ed4f71601cc9c3fb7b72b898531f8445e5` | `CANONICAL` |
| EV-REPLAY-WT | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/incident-replay-remove-worktrees.json` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `8817eeb5a0e857a8fc65aada005250125e9699093b3b4736a8978bbcee44c234` | `CANONICAL` |
| EV-REPLAY-LOG-CLEAN | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/incident-replay-clean_workspace.log` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `1b6e7ecbe02e31521f27faf405f9338c3160848c4bbe425ebf73fd29f38c2069` | `SOURCE_PIN` |
| EV-REPLAY-LOG-WT | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/incident-replay-remove_worktrees.log` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `b260568f8b7e0165788c106695182637d26adfffafc70ec810d5befc72acb335` | `SOURCE_PIN` |
| EV-ENV | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/environment.json` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `c2f2bd87e7f020993fcb3f5cb22aa750dd5b749c3425c982ab773417df2e79f1` | `CANONICAL` |
| EV-TRIAGE-SUMMARY | AC1/AC6 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/triage-summary.json` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `e88785f7c8c61e74603e0c438f5152017fafa5f85dccbb8c9ad3f310d24d0387` | `SOURCE_PIN` |
| EV-DELTA | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/protection-delta.json` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `7891db6c58dd45daac40e5a9aa86865f8d0e12c371856ac300d9b74ee1656f8a` | `CANONICAL` |
| EV-DELTA-LOG | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/protection-delta.log` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `23454b9f5fe2d782b618be69bb74887a9bc125cf8f6a66b8985453d242c01f8d` | `SOURCE_PIN` |
| EV-DELTA-SCRIPT | AC7 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/protection_delta.py` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `bf03a964c6c470a0ea95d7409d8814c5cf7f7b7292ee7dcd91d5b5310079bd1e` | `SOURCE_PIN` |
| EV-RUNNER | Gate（可复算） | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/run_evidence.py` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `9b64fa3d7ce3d1f1acc549c73d0373b9bef06e9c78c8ea37c406a9a83ec9debc` | `SOURCE_PIN` |
| EV-RUNNER-LOG | Gate（自日志） | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/run-evidence.log` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `219f18c4b1630863d406492d0847bc8da69317cc1daa52d2c0adf48741a1acef` | `SOURCE_PIN` |
| EV-RUNNER-EXIT | Gate（自 exit） | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/run-evidence.exitcode` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | `SOURCE_PIN` |
| EV-BUILD-REPORTS | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/build_reports.py` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `0c0074057178a6a90c8acf80491cc79e816a2fca5690d2c8fef66b53151b4327` | `SOURCE_PIN` |
| EV-BUILD-LOG | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/build-reports.log` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `26d3045912e33ea4d97b7d16bcf193cfb6d125976aae71985f41559c00cd106c` | `SOURCE_PIN` |
| EV-AUDIT-BEFORE-LOG | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/audit-before.log` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `e87bb95973f4f7aec82b18aa71d721a395c767bb6636129229e03762abdc34ce` | `SOURCE_PIN` |
| EV-AUDIT-AFTER-LOG | AC2–AC6 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/audit-after.log` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `e02002d4503dd4525a40e682c4bcb026385d39f04f2c7609e16267bd2cb99261` | `SOURCE_PIN` |
| EV-AUDIT-BEFORE-EXITCODE | AC1 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/audit-before.exitcode` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `53c234e5e8472b6ac51c1ae1cab3fe06fad053beb8ebfd8977b010655bfdd3c3` | `SOURCE_PIN` |
| EV-AUDIT-AFTER-EXITCODE | AC2–AC6 | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/audit-after.exitcode` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `53c234e5e8472b6ac51c1ae1cab3fe06fad053beb8ebfd8977b010655bfdd3c3` | `SOURCE_PIN` |
| EV-CHECK | Gate（治理检查日志） | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/governance-check.log` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `5e6d76c86489b06a235e2db29ed2a1d3185f782b2c07a1c9389d971c88bb503f` | `SOURCE_PIN` |
| EV-MANIFEST | Gate（证据清单） | `verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/manifest.sha256` | `cacd1c021a34c363f5b36d1b2b72f19f07acc081` | `b09b40585333f9d6080cf3df55024175fac9a7c8b8ec500cd7d38fd9e7e1485b` | `SOURCE_PIN` |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| linked worktree | G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1 | PRESERVE_REFERENCED | - | - | 本 Task 交付分支所在 linked worktree；集成/Review 前不得删除。 |
| temp bytecode cache | G:/CODEX/New Manga.workspace/temp/WORKSPACE-DECL-REMEDIATION/pycache | NOT_APPLICABLE | - | - | runner 指定的 `PYTHONPYCACHEPREFIX`；当前存在但为空，未删除，留待 owner/Codex 清理核销。 |
| NOT_APPLICABLE | - | NOT_APPLICABLE | - | - | 本 Task 为只读解析器修复；不产生、不迁移、不删除任何资源；测试夹具均在 `%TEMP%` 隔离仓库；真实仓库审计只读、exit 2、0 删除。 |

## Closeout Record

- Closeout date / Codex：待 Codex 独立 Review 与主仓集成后填写（本 Task 状态 `in_review`）。
- canonical_evidence_status：`complete`（32 条证据行 pin evidence commit；`governance-check.log` 另记）。
- resource_closeout_status：`pending`（Resource Manifest 已登记 linked worktree 与 temp/pycache；未删除，留待 Codex 核销）。
- 删除、迁移、归档数量/字节数：0。
- 未关闭项：76 条残余声明错误（`RESIDUAL.md`）；详见风险段。
- 当前指针清理：未修改 Plan/STATUS/其他 Task/历史 Review；最终治理检查由 Codex 在主仓执行。

## Closeout Record（Lead 2026-10-21）

- Codex Review 链：r1–r6 `changes_requested`（共 5 轮返修），**r7 `approved`**（0 阻塞 finding）；原始报告归档于 `doc/reviews/WORKSPACE-DECLARATION-REMEDIATION-1-*-codex-r*.md`。
- 集成：合并 `bb7887442`（delivery `cacd1c021`；evidence `cacd1c021` 冻结，32 条 Canonical Evidence pin、30 条 manifest 可复算）。
- 结果：真实仓库 `--audit-declarations` 从 163 errors 降到 **76 errors / 236 warnings**；76 条全部保留 fail-closed，逐条在 `RESIDUAL.md`；未放宽解析语义、未改历史文件/旧证据、未执行真实删除。
- 资源核销：linked worktree 保留（PRESERVE_REFERENCED）；`temp/WORKSPACE-DECL-REMEDIATION/pycache` 为空且未删除；`resource_closeout_status: complete`。
- 回归：29 新测试 + 80 既有测试 exit 0；双 incident replay 15/15 REJECT、0 删除、18/18 source；`run_evidence.py` exit 0；集成后主仓治理检查 PASS。
- 后续：76 条残余按 `RESIDUAL.md` 分类另立 Task/裁定（历史表结构 44、泛化/环境 10、JSON/不可读/歧义等 22），本 Task 不授权真实清理。
