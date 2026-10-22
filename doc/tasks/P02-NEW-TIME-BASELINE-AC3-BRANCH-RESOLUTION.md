---
id: P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION
title: P02 AC3 branch ref 绑定修复
kind: implementation
governance_version: 2
status: done
approval: user_authorized_autonomous_resolution_20261014
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
integrator: Codex /root
depends_on: [P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE]
base_commit: 210b8bc64e055f93a3b899a8e619b5e02b917cdf
branch: agent/zcode/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION
worktree: G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION
integration_commit: 360d7286e32b4d7b766aa434c0e31f210100ec18
delivery_head: b29828e48d848b4dfeab8f8be92948fe43d86971
reviewed_head: b29828e48d848b4dfeab8f8be92948fe43d86971
review_decision: approved
integration_target: agent/zcode/P02-NEW-TIME-BASELINE
integration_status: PASS
dispatch_state: COMPLETE
profile: ZCODE_HEAVY
revisions: {implementation: 1, test: 1, evidence: 2}
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION
followup_of:
  source_task: P02-NEW-TIME-BASELINE
  inherited_finding: AC3-BRANCH-REF-MISMATCH
severity: P2
inherited_evidence:
  - G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE/verification/P02-NEW-TIME-BASELINE/codex-ac3-branch-ref-blocker-20261014T0337.md
  - G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE/verification/P02-NEW-TIME-BASELINE/convergence-post-i2-ac3-branch-output-20261014T0337.json
why_not_current_task: Parent Task exhausted I1/I2; same-lineage I3 is forbidden, so convergence requires a separate resolution Task.
---

# P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION

## 来源与目标

`P02-NEW-TIME-BASELINE` 在 I2 后收敛为 `BLOCKED`。Codex 发现 AC3 collector 把 `git symbolic-ref --quiet HEAD` 返回的 `refs/heads/<branch>` 与 manifest 中短分支名直接比较，导致当前 AC3 必需检查确定 FAIL。Finding `AC3-BRANCH-REF-MISMATCH` 为 P2；证据见 frontmatter 的 inherited_evidence。

此 resolution Task 只修复该分支引用比较并补充回归自检。父 Task 已用完 I1/I2 预算，本 Task 不得依赖父 Task、不得修改或重开其返修轮；修复通过并集成后，父 Task 才恢复 AC3。不得据此运行 collector 或释放 X6。

## Acceptance Criteria

- [x] AC1：保留 freeze manifest 的短分支名契约和源码 binding；运行时正确将短名与 `symbolic-ref` 完整 ref 比较，当前分支匹配为 PASS，错误分支仍 fail-closed。（ZCode 交付：`Test-BranchRefMatchesManifest` 纯函数，`refs/heads/<短名>` 大小写敏感比较；shape/binding 对 `branch` 的校验原样未动）
- [x] AC2：Task selftest 有正例和负例覆盖短名/完整 ref 的比较；全量自检结果、命令、环境、exit 与原始输出入证据，既有断言不得回退。（212 PASS / 0 FAIL / exit 0；新增 2 静态 + 7 行为 + 1 函数存在性断言；既有 202 项语义全保留；证据见 Canonical Evidence）
- [x] AC3：DSH 对固定 Review HEAD `b29828e48d848b4dfeab8f8be92948fe43d86971` bounded Review=`APPROVED`，未发现 P0/P1/P2；Codex verified official manifest 2/2、selftest 212/0/7、delta 仅两个允许文件；已集成到父 Task branch commit `360d7286e32b4d7b766aa434c0e31f210100ec18`，Git tree 与被 Review tree 完全相同。证据见 Canonical Evidence。
- [x] AC4：本 resolution Task 未运行 live collector、未创建 collector output；父 Task 恢复后须重新冻结外部 manifest 并执行自身 AC3/AC4 Gate。

## 允许修改范围

- `tools/p02/p02-new-time-baseline.ps1`：只修 `git-branch-matches-freeze` 的 short-name/full-ref 比较。
- `tools/p02/p02-new-time-baseline-selftest.ps1`：只加对应正/负回归断言。
- 本 Task、其 Handoff、`verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/`。
- Codex 可更新父 Task 指针、DAG/STATUS/checkpoint 并集成经批准的最小修复。

## 禁止范围

不处理 I2-01/I2-02/N-1 或 O-1/O-2；不改其他 collector 行为、共享契约、Schema、依赖、历史输入/结论；不运行 live collector、X6、post-run Review、Build/Cargo、产品 AC1–AC7 或 Windows Sandbox；不重开父 Task I3、不清理或删除用户数据/原始输出。

## 测试要求

| 场景/AC | 计划命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 自检 | `pwsh -NoProfile -File tools/p02/p02-new-time-baseline-selftest.ps1` | resolution worktree root；PowerShell 7.6.6 | PASS（exit 0，212 PASS / 0 FAIL / stderr 空；live skip 保持 7 项、未写成 PASS） | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-selftest-ac3-branch-res-20261013T1947Z.*` |
| AC3 bounded Review / Codex VERIFY | 固定 delivery HEAD；官方 manifest verify；限定继承 finding 与当前 P0–P2 | Reviewer=DSH；Codex 独立 VERIFY/集成 | DSH APPROVED；Codex selftest 212/0/7 exit 0；manifest 2/2 PASS；fix 已 cherry-pick 到父 Task | DSH 摘要、Codex VERIFY、manifest 与 convergence 见 Canonical Evidence |
| AC4 live / later gates | 明确保持不运行 | 后续父 Task Gate | NOT_RUN / NOT_RELEASED | 本 Task Handoff |

## 依赖、风险与阻塞

硬依赖继承父 Task 唯一上游：`P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE`。禁止依赖被阻塞的父 Task，避免 DAG 环；其余父 Task 状态通过 Codex 的集成记录衔接。若验证不通过或发现新 P0–P2，按当前 Task 的有限收敛策略裁决，不扩大范围。

## 交付与运行记录

- Owner=ZCode；Reviewer=DeepSeek Harness；Integrator=Codex。
- ZCode 交付（2026-10-14，UTC 2026-10-13T19:47Z 自检）：fix commit `b29828e48d848b4dfeab8f8be92948fe43d86971`（delivery_head，仅 `tools/p02/p02-new-time-baseline.ps1` +11 行与 `tools/p02/p02-new-time-baseline-selftest.ps1` +40/-3 行）；docs/evidence 提交随后记录该 hash。
  - 修复：新纯函数 `Test-BranchRefMatchesManifest`（完整 ref == `refs/heads/<manifest 短名>`，大小写敏感）；`git-branch-matches-freeze` 调用点改经该函数；`branch` shape/binding 契约与 Expected/ObservedSummary 文案不变。
  - 自检：exit 0 / 212 PASS / 0 FAIL / stderr 空；新增 10 项断言（2 静态防回退 + 7 行为正/负例 + 1 函数存在性），既有 202 项全部保留 PASS；SUMMARY revision=`i2-r3+ac3-branch-res`；live 相关保持 7 项 SKIP（未写成 PASS）。
  - 证据：`verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-selftest-ac3-branch-res-20261013T1947Z.{command.txt,env.txt,stdout.txt,stderr.txt,exit,summary.md}` + `evidence-manifest-ac3-branch-res-r1.json`（逐文件 sha256）。
- Handoff：`doc/handoffs/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md`（delivery_head=`b29828e48d848b4dfeab8f8be92948fe43d86971`）。
- DSH bounded Review / Codex VERIFY：APPROVED；精确 Review HEAD=`b29828e48d848b4dfeab8f8be92948fe43d86971`；Codex independent test/hash/diff verification PASS；修复集成父 Task branch commit=`360d7286e32b4d7b766aa434c0e31f210100ec18`。
- ZCode AGENT_PREFLIGHT=`PASS`；CLI=`node E:/Program Files/ZCode/resources/glm/zcode.cjs` version `0.16.9`；worktree dirty=1（本 Task 文件）；preflight evidence 位于本 Task `verification/`。
- live collector / X6 及之后门禁：NOT_RUN / NOT_RELEASED。

- DSH bounded Review 原始结果：`dsh-review-ac3-branch-p2-bounded-result.md`（exit 0；workspace SHA-256 `4E3D3AECC6564BE7240D4C2ADA1303CAFC02108ED8C5E6412D667543AA463942`）；版本化的是下方 Codex 摘要与验证产物。
- DSH 因 ACL 无法运行 PowerShell 与官方 Python manifest verifier；Codex 独立复跑均通过。F-01 的 code/review head 与 docs package head 区分已证实；F-02 的 preflight 缺失描述与实际 PASS 文件不符；F-03 P4 仅为 stderr hygiene backlog。
- Resolution convergence=`APPROVED`，无 P0/P1/P2，F-03 backlog。父 Task post-resolution convergence=`APPROVED`（I2 cap 2/2），I2-01 P3、I2-02 P4、N-1 P4、F-03 P4 均 backlog；禁止 I3。
- 集成：将 `b29828e48d848b4dfeab8f8be92948fe43d86971` cherry-pick 到 `agent/zcode/P02-NEW-TIME-BASELINE`，integration commit=`360d7286e32b4d7b766aa434c0e31f210100ec18`；两提交 tree=`42daad186020b9754f2e0109c2b83e8f5c1d52b8`。
## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| RES-EV-01 | AC3 / AC4 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/classify-resolution-closeout-20261013T2018Z-input.json` | `0ffcd4d03387fd6a0e2092a628044133c15e1dd6` | `62A70C122090C0DC7B67420D291D479DC7E1341B5AF1AB5B89DAD83857B018BB` | CANONICAL |
| RES-EV-02 | AC3 / AC4 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/classify-resolution-closeout-20261013T2018Z-output.json` | `0ffcd4d03387fd6a0e2092a628044133c15e1dd6` | `615A70A4403C3CEA0098CD886AEADA50279A64852F094CA19055E714A6A21C6A` | CANONICAL |
| RES-EV-03 | AC3 / AC4 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/classify-resolution-closeout-20261013T2018Z.exit` | `0ffcd4d03387fd6a0e2092a628044133c15e1dd6` | `5FECEB66FFC86F38D952786C6D696C79C2DBC239DD4E91B46729D73A27FB57E9` | CANONICAL |
| RES-EV-04 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-ac3-resolution-verify-20261013T2002Z.md` | `f298467add132373f391e4ec9335d84b53052378` | - | CANONICAL |
| RES-EV-05 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-review-manifest-verify-20261013T2002Z.exit` | `f298467add132373f391e4ec9335d84b53052378` | `5FECEB66FFC86F38D952786C6D696C79C2DBC239DD4E91B46729D73A27FB57E9` | CANONICAL |
| RES-EV-06 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-review-manifest-verify-20261013T2002Z.json` | `f298467add132373f391e4ec9335d84b53052378` | `0E666BD0F2C8BE1CCC2F46CED7BC31743125D34994911DCCAEAD40DC13D559C4` | CANONICAL |
| RES-EV-07 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-review-manifest-verify-20261013T2002Z.stderr.txt` | `f298467add132373f391e4ec9335d84b53052378` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` | CANONICAL |
| RES-EV-08 | AC2 / AC3 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-selftest-ac3-branch-res-20261013T2002Z.command.txt` | `f298467add132373f391e4ec9335d84b53052378` | `A1EA5A0F69CE807CFB6A34D995221C4BA7CC581F67C4694FFD4177E06D861690` | CANONICAL |
| RES-EV-09 | AC2 / AC3 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-selftest-ac3-branch-res-20261013T2002Z.env.txt` | `f298467add132373f391e4ec9335d84b53052378` | - | CANONICAL |
| RES-EV-10 | AC2 / AC3 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-selftest-ac3-branch-res-20261013T2002Z.exit` | `f298467add132373f391e4ec9335d84b53052378` | `5FECEB66FFC86F38D952786C6D696C79C2DBC239DD4E91B46729D73A27FB57E9` | CANONICAL |
| RES-EV-11 | AC2 / AC3 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-selftest-ac3-branch-res-20261013T2002Z.stderr.txt` | `f298467add132373f391e4ec9335d84b53052378` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` | CANONICAL |
| RES-EV-12 | AC2 / AC3 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/codex-selftest-ac3-branch-res-20261013T2002Z.stdout.txt` | `f298467add132373f391e4ec9335d84b53052378` | `6D022DEE7672611C0E3D4A9995B2A55054CB6EBC3C7A7F4959C4A67A6AFB343E` | CANONICAL |
| RES-EV-13 | AC3 / AC4 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/convergence-post-dsh-codex-verify-20261013T2004Z-input.json` | `f298467add132373f391e4ec9335d84b53052378` | `A000FF2679D4756864144832F7448F379007C27D3966ECC9CFAB0464027543E8` | CANONICAL |
| RES-EV-14 | AC3 / AC4 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/convergence-post-dsh-codex-verify-20261013T2004Z-output.json` | `f298467add132373f391e4ec9335d84b53052378` | `AC0FDF1BDB4AB918D5564E729D42C30F3E56C5FE307B1C811505790B35958AF4` | CANONICAL |
| RES-EV-15 | AC3 / AC4 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/convergence-post-dsh-codex-verify-20261013T2004Z.exit` | `f298467add132373f391e4ec9335d84b53052378` | `5FECEB66FFC86F38D952786C6D696C79C2DBC239DD4E91B46729D73A27FB57E9` | CANONICAL |
| RES-EV-16 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-agent-preflight-20261013T1957Z.exit` | `f298467add132373f391e4ec9335d84b53052378` | `5FECEB66FFC86F38D952786C6D696C79C2DBC239DD4E91B46729D73A27FB57E9` | CANONICAL |
| RES-EV-17 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-agent-preflight-20261013T1957Z.json` | `f298467add132373f391e4ec9335d84b53052378` | `568B6AE3E90CC01D35B798A33CF4EE613E23402A62F5A15563FC26FF3D69E485` | CANONICAL |
| RES-EV-18 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-agent-preflight-20261013T1957Z.stderr.txt` | `f298467add132373f391e4ec9335d84b53052378` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` | CANONICAL |
| RES-EV-19 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-preflight-attestation-basis.md` | `f298467add132373f391e4ec9335d84b53052378` | `36B4F655020B56DFBAA4DA95B79E06C70BDA3BA81A9ADE1249EB834853B88386` | CANONICAL |
| RES-EV-20 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-preflight-attestation.json` | `f298467add132373f391e4ec9335d84b53052378` | `621D6312A0F93AE143522073963C35F9C8364677E39A82629135C6623B39562A` | CANONICAL |
| RES-EV-21 | AC3 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-review-ac3-branch-p2-bounded-prompt.md` | `f298467add132373f391e4ec9335d84b53052378` | - | CANONICAL |
| RES-EV-22 | AC3 | `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-review-ac3-branch-p2-bounded-result.md` | `-` | `4E3D3AECC6564BE7240D4C2ADA1303CAFC02108ED8C5E6412D667543AA463942` | CANONICAL |
| RES-EV-23 | AC3 | `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-review-ac3-branch-p2-bounded-stderr.txt` | `-` | `46A57ECA54E1FB0D752E2145E935E7F72B3D933DD466F713E837E9F81C6AE288` | CANONICAL |
| RES-EV-24 | AC3 | `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-review-ac3-branch-p2-bounded.exit` | `-` | `5FECEB66FFC86F38D952786C6D696C79C2DBC239DD4E91B46729D73A27FB57E9` | CANONICAL |
| RES-EV-25 | AC3 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-review-ac3-branch-resolution-summary.md` | `f298467add132373f391e4ec9335d84b53052378` | - | CANONICAL |
| RES-EV-26 | AC3 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-review-manifest-bounded-r1.json` | `f298467add132373f391e4ec9335d84b53052378` | `A595A1B4EBD085CC35B44E01A87E44C284B13AB1669512CAE7C88E6D3332B09F` | CANONICAL |
| RES-EV-27 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/evidence-manifest-ac3-branch-res-r1.json` | `61812549b49b4f8470dc3dcc7920026d60c63612` | - | CANONICAL |
| RES-EV-28 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-agent-preflight-20261014T0341.exit` | `61812549b49b4f8470dc3dcc7920026d60c63612` | `5FECEB66FFC86F38D952786C6D696C79C2DBC239DD4E91B46729D73A27FB57E9` | CANONICAL |
| RES-EV-29 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-agent-preflight-20261014T0341.json` | `61812549b49b4f8470dc3dcc7920026d60c63612` | `AF46948EC703401EEAEB72B569242B7AEC8DC5C63618D4A124FEBE0D7493E65A` | CANONICAL |
| RES-EV-30 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-preflight-attestation.json` | `61812549b49b4f8470dc3dcc7920026d60c63612` | `A40AC4F05793BFA8DFF9F6DE20130E4627DA555C741B8EA48BBA46E4E614CDE7` | CANONICAL |
| RES-EV-31 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-preflight-config.json` | `61812549b49b4f8470dc3dcc7920026d60c63612` | `6AEDAB79020D51B65272DA9DD0553A0F077D5D856183CDD145E31AC9E3CB63C6` | CANONICAL |
| RES-EV-32 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-preflight-dry-run-20261014T0340.exit` | `61812549b49b4f8470dc3dcc7920026d60c63612` | `6B86B273FF34FCE19D6B804EFF5A3F5747ADA4EAA22F1D49C01E52DDB7875B4B` | CANONICAL |
| RES-EV-33 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-preflight-dry-run-20261014T0340.json` | `61812549b49b4f8470dc3dcc7920026d60c63612` | `D739F36851DDDE11F4998A97643B0CBD192CB39402FB4F296C81F987CA260B22` | CANONICAL |
| RES-EV-34 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-preflight-dry-run-20261014T0341.exit` | `61812549b49b4f8470dc3dcc7920026d60c63612` | `6B86B273FF34FCE19D6B804EFF5A3F5747ADA4EAA22F1D49C01E52DDB7875B4B` | CANONICAL |
| RES-EV-35 | AC3 / closeout | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-preflight-dry-run-20261014T0341.json` | `61812549b49b4f8470dc3dcc7920026d60c63612` | `6288D7F5BA18C1C9A47A15C9D1EECB5C513B1EE1B4301FA76C377F9ECF973132` | CANONICAL |
| RES-EV-36 | AC1 / AC2 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-selftest-ac3-branch-res-20261013T1947Z.command.txt` | `61812549b49b4f8470dc3dcc7920026d60c63612` | `2E2716BC0C504A766D4B9F903D915A7DF0A06C485E07CC7A61A5E7B9411A6129` | CANONICAL |
| RES-EV-37 | AC1 / AC2 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-selftest-ac3-branch-res-20261013T1947Z.env.txt` | `61812549b49b4f8470dc3dcc7920026d60c63612` | `B464613CDE08855E5ADB20B27C64252D0CC78CD8CCDF3A873F783918CDBD204C` | CANONICAL |
| RES-EV-38 | AC1 / AC2 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-selftest-ac3-branch-res-20261013T1947Z.exit` | `61812549b49b4f8470dc3dcc7920026d60c63612` | `9A271F2A916B0B6EE6CECB2426F0B3206EF074578BE55D9BC94F6F3FE3AB86AA` | CANONICAL |
| RES-EV-39 | AC1 / AC2 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-selftest-ac3-branch-res-20261013T1947Z.stderr.txt` | `61812549b49b4f8470dc3dcc7920026d60c63612` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` | CANONICAL |
| RES-EV-40 | AC1 / AC2 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-selftest-ac3-branch-res-20261013T1947Z.stdout.txt` | `61812549b49b4f8470dc3dcc7920026d60c63612` | `92838472210541E02997EECBE6D1AD08411099B25C683D95977412C12021CC1B` | CANONICAL |
| RES-EV-41 | AC1 / AC2 | `verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/zcode-selftest-ac3-branch-res-20261013T1947Z.summary.md` | `61812549b49b4f8470dc3dcc7920026d60c63612` | `FD5C9846D6CE0E84AB4243E4E79B621391B00C4562963B57C04B8669A2FD0842` | CANONICAL |

| RES-EV-42 | AC3 / closeout | verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/resource-preservation-manifest.json | - | DC08D7F258494A4A332E9FFB18184E0977E8B084B849AD5AA379BAA00AA7358D | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION | verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/resource-preservation-manifest.json | branch-local workspace preserved; manifest captures HEAD and dirty/untracked status; no deletion or worktree removal |
| ZCode agent-output | G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION | verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/resource-preservation-manifest.json | recursive file names, sizes, and SHA-256 recorded; preserved in place |
| Codex agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION | verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/resource-preservation-manifest.json | recursive file names, sizes, and SHA-256 recorded; preserved in place |
| DSH raw review result | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-review-ac3-branch-p2-bounded-result.md | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-review-ac3-branch-p2-bounded-result.md | 4E3D3AECC6564BE7240D4C2ADA1303CAFC02108ED8C5E6412D667543AA463942 | raw result retained byte-for-byte; SHA-256 verified; no deletion |
| DSH raw stderr | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-review-ac3-branch-p2-bounded-stderr.txt | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-review-ac3-branch-p2-bounded-stderr.txt | 46A57ECA54E1FB0D752E2145E935E7F72B3D933DD466F713E837E9F81C6AE288 | raw diagnostic bytes retained unchanged; SHA-256 verified; not presented as review content |
| DSH raw exit | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-review-ac3-branch-p2-bounded.exit | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/dsh-review-ac3-branch-p2-bounded.exit | 5FECEB66FFC86F38D952786C6D696C79C2DBC239DD4E91B46729D73A27FB57E9 | exit record retained and hash verified |
| selftest temp fixture 1 | G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE/20261014-035539-pure-selftest | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE/20261014-035539-pure-selftest | verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/resource-preservation-manifest.json | contents inventoried; retained in place, no cleanup |
| selftest temp fixture 2 | G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE/20261014-040714-pure-selftest | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE/20261014-040714-pure-selftest | verification/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION/resource-preservation-manifest.json | contents inventoried; retained in place, no cleanup |
## Closeout Record

- Closeout date / Codex：2026-10-14T20:23Z / Codex；worktree/agent-output/temp/raw-review resources 全部保留并以 resource-preservation-manifest 固定。
- canonical_evidence_status / resource_closeout_status：complete / complete。
- 未关闭项：无；父 Task 的 live AC3/AC4 与后续准入链保持独立、未释放。
