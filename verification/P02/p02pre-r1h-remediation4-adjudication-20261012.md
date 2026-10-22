# P02PRE-R1H round-four Review adjudication

日期：2026-10-12（Asia/Shanghai）

## 裁决结果

- Owner=`/root/p02_r1h_codex_owner`；非作者 Reviewer=`/root/p02_r1h_remediation_review`；Integrator/Adjudicator=`/root`。
- round-four Review report=`verification/P02/codex-subagent-p02pre-r1h-static-review-remediation4-20261012.md`，8769 bytes / SHA-256 `0BE345FDA968A0F9194CA99ECD35D110F3F5F81C76116AFF65E7BAF574069C0F`；verdict=`APPROVED_STATIC_CONTENT`，P0/P1/P2/P3=`0/0/0/0`。
- root 复算 Review 前后全部 source/candidate pins=`11/11 MATCH`。Review pins=`verification/P02/codex-p02pre-r1h-remediation4-review-input-pins-20261012.json`，3952 bytes / SHA-256 `9F97C92F6BAC558DE35A470FFB6055EBE6D4C2A80A4733654CAA46F5AD074726`。
- 独立报告中的 key-overload 分析与冻结代码一致。采纳 R1H-007=`FIXED_STATIC`：显式 `[object]$index` 选择 OrderedDictionary 的 object-key getter，左侧 `$prefix[[int]$index]` 仍按 prefix 数组位置读取；稀疏 key 不再被混作值位置。本裁决只接受静态修复，不宣称真实 PowerShell AST、自检或 fixtures 已运行。
- R1H-006=`FIXED_STATIC_COVERAGE`；R1H-005=`FIXED_STATIC`；R1H-001=`FIXED_BY_FAIL_STOP_STATIC`，冻结 Git status/index 值仍缺失且为 `UNPROVABLE`；R1H-002/003=`FIXED_STATIC`；R1H-004=`FIXED_STATIC_CONTENT`。
- Task AC3 满足：非作者静态 Review 无 P0/P1/P2；root 冻结输入 pins pre/post 相同。AC3=`PASS_WITH_EVIDENCE`，证据为上述报告、pins 和 root 复算。AC2=`NOT_RUN`；AC4 后续 integration/parser/selfcheck/preflight=`NOT_RUN`；AC5 final pre-run=`NOT_RUN`；AC6 capture/post-run Review=`NOT_RUN`；AC1=`NOT_VERIFIED / UNPROVABLE`（不能因此跳过安全 fail-stop）；AC7=`NOT_VERIFIED`。Candidate 尚未集成。

## Delivery integration 授权边界

- Review 的 candidate base=`946938bd0696dfddd01f87d61fe6723c63ecdc86`，parent=`0ecada4182d624d4f352a253e09db3bdecbee5d1`，delivery HEAD=`7e7d0bce8dd86a2302d2a9eb278702d9c70354ff`，tree=`c9afca4e9bfd8d1b6a6c3ad5a8a33e0e12c3d87b`。Codex root delivery verification=`verification/P02/p02pre-r1h-round4-delivery-verification-20261012.md`。
- 按 Task AC4，仅在目标路径确认 absent 时，root 可用 `CreateNew` 精确集成 Review 通过的三个文件：`p02pre-r1h-capture.ps1`、`p02pre-r1h-selfcheck.ps1`、`p02pre-r1h-handoff-20261012.md`；逐文件 byte/hash 与 reviewed delivery 一致。任何目标已存在或不匹配均不得覆盖；先停并记录 collision。集成后再次验证来源 commit、目标 hash 与 controlled status。
- 集成成功后才运行 Task 明确允许的 PowerShell 7.6.6 parser、isolated self-check 和 no-profile child preflight；它们是真实运行证据，需单独记录退出码、进程/版本、输出与前后 pins。self-check 包含的 mutation fixtures 在合法正例顺利通过后必须真实运行并记录实际结果。任一检查失败时定位根因、最小修复并重新冻结 Review；不放行 final pre-run/capture。
- 本裁决不授权跳过 AC5 的精确 final pre-run；也不自动授权一次性 R1H capture，须依 Task 按实际证据另行评估。更不解除 Build Barrier。

## Gate 不变

- `private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；原文 `technical condition unmet; user explicitly accepted residual risk`。
- Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7 中所有非 AC3 项仍未通过/未运行，按 Task 分项状态记录。
- Windows Sandbox 不查询、安装、启用或启动。R1G 已消耗 one-shot 不重跑。
