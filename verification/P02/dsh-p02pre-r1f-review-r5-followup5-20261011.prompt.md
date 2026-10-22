# DeepSeek Harness read-only Review request: P02PRE-R1F Review Round 5 follow-up #5

请作为非作者 Reviewer，只复核以下固定的 11 个输入文件。Task=P02PRE-R1F；Repo=G:/CODEX/New Manga；branch/HEAD=cddff58469b56e181019a8ddfeade80684bc7eb9。Owner/Author/Integrator/Adjudicator=Codex /root。上一轮 DSH follow-up #4 为 CHANGES_REQUESTED (0/0/0/1)，Codex 已 adjudicate 并修复唯一 F1/P3 文档矛盾；当前候选增加 self-check4 与 follow-up #5 的 future artifacts 至 protected inventory，现为 90/90 unique。请独立审查新的精确候选。

## 固定输入 pins

1. doc/tasks/P02PRE-R1F.md — 21603 bytes / SHA-256 BEFFCA43C76C3AB1D645389BB8075E7D4A3BBBF530B487EC27306AA1C4E4329E
2. verification/P02/p02pre-r1f-manifest-20261011.md — 24689 bytes / SHA-256 9CAEE9C9ADC5011416F843A7C5704EEBBA813BFCDE12A3415E3B2F731644FADD
3. verification/P02/p02pre-r1f-capture.ps1 — 67071 bytes / SHA-256 4C01B8F9F0A6225B25398733B16D7286C40BBF22C4958E82BDD7A7710BADB25D
4. verification/P02/p02pre-r1f-r5-followupfix4-selfcheck-20261011.json — 2154 bytes / SHA-256 64812B7F86BDFF025AB5BC632878C96AD1B80F8B1C5010C32A6EA843D0717E0A
5. verification/P02/p02pre-r1f-r5-followup4-review-adjudication-20261011.md — 4000 bytes / SHA-256 1CFE92BE7C6FF488447CD26EC81168E015EF2B1B620DFF74745C07C65554CAE4
6. verification/P02/dsh-p02pre-r1f-review-r5-followup4-20261011.stdout.md — 13169 bytes / SHA-256 55133FC56E27C95B301301682C4532C5ABA535852166E33183FA9CF82FE17B2F
7. verification/P02/dsh-p02pre-r1f-review-r5-followup4-20261011.prompt.md — 3946 bytes / SHA-256 93C041CC824E5D63C02849A8B4BA6B9697CFF46F50C4ED1EA7A9A520D931F69D
8. verification/P02/dsh-p02pre-r1f-review-r5-followup4-20261011.stderr.log — 118238 bytes / SHA-256 A1640BC9CE8D5DE0A755D1AAAC90C3886DE79D3C7BCEFCCAC15D225FA771164B
9. verification/P02/dsh-p02pre-r1f-review-r5-followup4-20261011.exit — 3 bytes / SHA-256 13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354
10. verification/P02/p02pre-r1f-r5-followupfix3-selfcheck-20261011.json — 2927 bytes / SHA-256 18BD55A9119ADD7253CAD00D87843EEF4A6B047900BB1D47964437E23E465B97
11. verification/P02/p02pre-r1f-r5-followup3-review-adjudication-20261011.md — 4500 bytes / SHA-256 98F2AF2B56EBC857EC2311AEDD8D27F1F651E90C91FA043EF59ED03AE7302AE0

## Review focus

- 逐字核验两个 protected-key arrays 的 path membership：当前合计应为 90 keys / 90 unique / 0 duplicates；确认新增 6 项为 follow-up-fix4 self-check，以及 follow-up #5 prompt/stdout/stderr/exit/Codex adjudication；确认所有 11 个本轮输入都在 script 中，尤其不要把相似文件名或行号当作路径相同。
- 独立检查 follow-up #4 F1/P3 是否准确修复：旧 self-check3 的 childStderrBytes=404 与其 SHA-256 是否被如实保留；当前 self-check4 是否精确绑定 67071-byte script，Windows PowerShell 5.1.26100.9549 parse errors=0、selfCheck=PASS、assert output=0、child exit=0、stderr=0，且 capture/getter/registry/ACL write=false。
- 检查 Task、manifest、script、self-check 与 #4 adjudication 之间是否存在 pin、计数、release order 或风险状态矛盾；核对只有 follow-up #5=APPROVED 并由 Codex adjudicate 后才允许 R8 parse-only，之后另做 pre-run adjudication 才能运行一次 capture。
- 明确保留 private_registry_absence=UNPROVABLE、Technical Gate=NOT_SATISFIED、Owner Risk Acceptance=APPROVED、Gate Disposition=WAIVED_BY_OWNER、Build Authorization=AUTHORIZED_WITH_EXCEPTION、Build Gate=BLOCKED、Hard Build Barrier=EFFECTIVE、Build/Cargo=NOT_RUN、AC1–AC7=BLOCKED / NOT_RUN。不得把 owner waiver/self-check/review 说成 Gate PASS。
- 输出 Decision、P0/P1/P2/P3 counts、逐项 finding（精确路径/位置、影响、最小修复）及 scope limitations。仅当无开放问题时返回 APPROVED (0/0/0/0)。

## 严格边界

只读以上 11 个 pin 文件；不访问任何未 pin 路径或 .tmp.driveupload；不运行 shell/grep/rg/PowerShell/测试/getter/hash/R8/capture/Build-Cargo/AC1–AC7；不写文件、不改 Gate。若不能在该读取范围内完成 review，返回 BLOCKED / REVIEW_SCOPE_LIMITATION，不要扩大范围。Review 不授权 R8/capture，也不代表 Gate PASS。
