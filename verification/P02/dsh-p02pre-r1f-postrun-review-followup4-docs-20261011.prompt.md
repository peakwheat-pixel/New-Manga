# P02PRE-R1F post-run 文档独立窄复审 follow-up #4

Task ID=`P02PRE-R1F-POSTRUN-DOCS-FOLLOWUP4-20261011`；Reviewer=`DeepSeek Harness`；Author/Integrator/Adjudicator=`Codex /root`；base/reviewed HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。这是新 session 的只读 Review。Follow-up #3 因 dispatch wrapper 输出通道失效超时，没有报告或 verdict；其 session 在诊断时收到一个结果未捕获的 `probe`，状态不明，禁止复用。失败仅分类为 `DISPATCH_TIMEOUT / NOT_A_REVIEW`，详见冻结 failure record。

## Review 目标

仅审查 follow-up #2 的 P3 `R1F-DOC2-01` 修复及其当前状态同步，不重新审查旧 Review 的其他结论，也不释放任何 Gate：

1. R1G manifest 中 `32536 / 3C3F…` 与 `44417 / 7F25…` 是否明确标为 R1G 初始冻结时的历史版本，且没有再称为当前 R1F Task/manifest pins。
2. 当前 R1F Task/manifest 的 pin 是否指向 rolling checkpoint 与后续 R1G dispatch prompt，R1G manifest 的自有当前 pin 是否在 checkpoint/dispatch 处重新绑定。
3. 唯一 Plan DAG、STATUS、文档索引、Task 导航、P02 Task、R1F Task、R1F/R1G manifests 与 rolling checkpoint 是否一致记录：R1F one-shot capture 已在 Windows PowerShell 5.1 因 `Get-FileHash` 解析失败而 fail-stop；#2 finding 已修复；#3 超时且无 Review verdict；#4 使用 fresh DSH session；R1G=`READY`、Owner=`Antigravity`、Reviewer=`DeepSeek Harness`；R1F one-shot 不重跑。
4. 是否保持准确的 gate values：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。
5. PS 7 文字是否准确：R1G 选择 `7.6.6` 且配置 capture 前 command/module preflight；这不是 PS 7 运行期兼容已通过的证据。R1F 的失败不得被描述为 AC 失败或 PS 7 不兼容。

## 冻结 Review 输入

下表 bytes/SHA-256 由 Codex 在派发前实测；本 Review 只做只读内容/交叉引用审查，不要求你执行命令或复算 hash。最后一项 `doc/templates/REVIEW.md` 仅为格式参考。

| 类型 | 文件 | bytes | SHA-256 |
|---|---|---:|---|
| source | `doc/REBASELINE_PLAN.md` | 283060 | `98F9D954DAB0A08575241F9520A88867D2E7168F4E81288D69690FFEDCBC5F7E` |
| source | `doc/STATUS.md` | 289588 | `15ED90088C6E7E42048335FC611B015F814BA27C801BE802F8208FBC6EB1F629` |
| source | `doc/00_INDEX.md` | 58706 | `79C0EF10834925F6568423501A7B25C97D12E2927023284B09E1ED91D6F1395B` |
| policy | `doc/09_COLLABORATION.md` | 19131 | `DAFBD1F65DFCE967F50561926C9CC92F2A7DAAE826C33F375A549573372ECD9D` |
| source | `doc/tasks/README.md` | 37883 | `8729010B5718E208445966AA40309E9A1402D350C5F4F0F930036FD08EEA83F0` |
| source | `doc/tasks/P02.md` | 222394 | `BF1CC4204C9E945ABCBC106BE8B30E683C66F440B2D0002999DBC80FC92A177B` |
| source | `doc/tasks/P02PRE-R1F.md` | 36305 | `B3C947E1C6391C391BBBF0D844A84688463594F478E5CB22BBC20E0F4CDA1AE4` |
| source | `doc/tasks/P02PRE-R1G.md` | 6677 | `F47B1249D57BD630F927E6E964E2243396999008CE584172E13C67D75995321B` |
| format reference | `doc/templates/REVIEW.md` | 3915 | `048DD2C001BC16CE68B46460C2D23AA32BA1119091CA1E2ABA3EE4EE63ED4762` |
| source | `verification/P02/p02pre-r1f-manifest-20261011.md` | 48143 | `D681165661AC1D49C3F31BE7CCF169D9BB6764DE3A115BB903AD177A36C8B058` |
| source | `verification/P02/p02pre-r1g-manifest-20261011.md` | 10599 | `BC103E0B7032561DF20AA2D0F91D226ED690915F476054F25D805C0455693D3E` |
| source | `verification/P02/p02pre-r1f-postrun-adjudication-20261011.md` | 8716 | `ADD2C7538E3B2029E7C4487A072A36561AA387059BC016BAC93F35E01A79C685` |
| prior Review | `verification/P02/dsh-p02pre-r1f-postrun-review-followup2-docs-20261011.stdout.md` | 7526 | `ED560BD1C71C6112B4C65BC1350ECE35BC94E3C7440E4B13A787FCD7F1EB5A92` |
| adjudication | `verification/P02/p02pre-r1f-postrun-review-followup2-docs-adjudication-20261011.md` | 2933 | `17C7C8D82ADD59399F57D03DCD9F4004F78B99B0BBDA31677ECA0226BB500575` |
| dispatch failure | `verification/P02/p02pre-r1f-postrun-docs-followup3-dispatch-failure-20261011.md` | 2806 | `C6D608A939532D8C02B0F3E701F748E1D74BE1F1C0F52C3B0D7A4D2DF924E2F7` |
| recovery snapshot | `verification/P02/codex-checkpoint-p02pre-r1f-postrun-20261011.md` | 12560 | `00F835A28094DCD908FE22EBC512FE5882941B51E3E7EBF10DE40337C82A75E2` |

## 约束与输出

- 只读以上冻结文件；不执行 shell/Git/PowerShell、host getter、profile/registry/ACL API、Build/Cargo/AC，不修改任何文件。
- 不读取 `.tmp.driveupload` 内容或元数据；不触碰 Windows Sandbox。
- 旧 `CHANGES_REQUESTED (0/0/0/1)` 原 verdict 保持不变；本次是修复后的独立窄复审，不重写原报告。
- 若确认修复和状态同步准确，给出 `APPROVED`；否则给 `CHANGES_REQUESTED` 并列出每项 finding 的 ID、级别、精确文件/行、触发/影响、最小修复建议。证据不足则 `NOT_VERIFIED`，不得猜测。
- 请按 `doc/templates/REVIEW.md` 给出简体中文 Markdown 报告，并明确 reviewed HEAD、输入范围、P0/P1/P2/P3 计数、限制。不要把用户 risk acceptance、R1F capture failure 或 PS 7 选择写成 Gate PASS/兼容 PASS。