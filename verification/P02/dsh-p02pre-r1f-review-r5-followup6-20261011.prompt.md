# DeepSeek Harness read-only Review request: P02PRE-R1F Review Round 5 follow-up #6

请作为非作者 Reviewer，只复核以下固定的 11 个输入文件。Task=P02PRE-R1F；Repo=G:/CODEX/New Manga；branch/HEAD=cddff58469b56e181019a8ddfeade80684bc7eb9。Owner/Author/Integrator/Adjudicator=Codex /root。上一轮 DSH follow-up #5 为 CHANGES_REQUESTED (0/0/0/1)，Codex 已 adjudicate：把 childEngine 与 PSEdition 字段含义写清，纠正 #5 report 中的 pin-numbering false positive，并新增 self-check5 与 follow-up #6 artifacts。当前冻结 candidate=96/96 unique，请独立复核。

## 固定输入 pins

1. doc/tasks/P02PRE-R1F.md — 22425 bytes / SHA-256 1359D5134C3FD26DC6C4BFBFFF9BA63312FCFB3364C7DF53FB34BFD00A93D50D
2. verification/P02/p02pre-r1f-manifest-20261011.md — 26464 bytes / SHA-256 9432A99D9AC54755D57E6E4DB902E916C7E6CE5BAF9C5DA8C24A9FF67C179A89
3. verification/P02/p02pre-r1f-capture.ps1 — 67582 bytes / SHA-256 5A3FE118A8758CCDF0BEDBE170D31B34DA6C338101096EAA825DE80DF70E8316
4. verification/P02/p02pre-r1f-r5-followupfix5-selfcheck-20261011.json — 2221 bytes / SHA-256 2FC047C13787D50C75FA5BCDF156BE5063040C0752484D927CB366BD8783C287
5. verification/P02/p02pre-r1f-r5-followup5-review-adjudication-20261011.md — 4672 bytes / SHA-256 03A5CE9D66B5235EE7F56E27239BCF18E317AD945702C9FCDE2420627465226A
6. verification/P02/dsh-p02pre-r1f-review-r5-followup5-20261011.stdout.md — 17711 bytes / SHA-256 5535945FD9A0667057C13FF998AC8FBB791DB5A3A1BC40ECF58534EA714F63A1
7. verification/P02/dsh-p02pre-r1f-review-r5-followup5-20261011.prompt.md — 4252 bytes / SHA-256 B7AA5523DDFDB005D2994F99AABAB99ED5670FE66E66515EF9A06CE12A20682C
8. verification/P02/dsh-p02pre-r1f-review-r5-followup5-20261011.stderr.log — 28012 bytes / SHA-256 E47A5CA117A2B2125AE4E61C7B29CB428586AC57BCF408615B7FE1AC96033D4B
9. verification/P02/dsh-p02pre-r1f-review-r5-followup5-20261011.exit — 3 bytes / SHA-256 13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354
10. verification/P02/p02pre-r1f-r5-followupfix4-selfcheck-20261011.json — 2154 bytes / SHA-256 64812B7F86BDFF025AB5BC632878C96AD1B80F8B1C5010C32A6EA843D0717E0A
11. verification/P02/p02pre-r1f-r5-followup4-review-adjudication-20261011.md — 4000 bytes / SHA-256 1CFE92BE7C6FF488447CD26EC81168E015EF2B1B620DFF74745C07C65554CAE4

## Review focus

- 逐字核验两个 protected-key arrays，当前应为 83 + 13 = 96 keys / 96 unique / 0 duplicates。确认新增 6 项精确为 self-check5 与 follow-up #6 prompt/stdout/stderr/exit/Codex adjudication；核对本轮 11 个 pins 全部在 script 中。切勿按 pin 编号错配或把相似文件名当成相同路径。
- 审查 #5 F1 文档修正：fix4 artifact 顶层 childEngine=Windows PowerShell 是 parent-side executable label；child JSON 的 engine field 对应 PSEdition=Desktop；fix5 应同时明确 engine=Windows PowerShell、edition=Desktop、版本=5.1.26100.9549。确认旧 artifacts 未被改写且 manifest/Task 与 self-check5 一致。
- 复核 self-check5 精确绑定 script bytes/SHA、Windows PowerShell 5.1.26100.9549、PARSE_OK、7 个 pure functions、PASS、assert output=0、child exit=0、stderr=0、capture/getter/registry/ACL write=false。
- 检查 #5 Review 对 path membership 的 Codex correction 是否有依据：实际 pin #8=#4 stderr（script line738）、#9=#4 exit（line739）、#11=#3 adjudication（line734）；确认 manifest 中关于 #4 Review outputs 的范围措辞与实际 inventory 一致。
- 检查 Task、manifest、script、自检、adjudication 间的精确数值、review status 与 release order。只有 follow-up #6=APPROVED 且 Codex pin/path-membership adjudication 后，才能做 R8 parse-only；随后另做 pre-run adjudication才可能释放单次 capture。
- 明确保留 private_registry_absence=UNPROVABLE、Technical Gate=NOT_SATISFIED、Owner Risk Acceptance=APPROVED、Gate Disposition=WAIVED_BY_OWNER、Build Authorization=AUTHORIZED_WITH_EXCEPTION、Build Gate=BLOCKED、Hard Build Barrier=EFFECTIVE、Build/Cargo=NOT_RUN、AC1–AC7=BLOCKED / NOT_RUN。不得把 waiver、self-check 或 Review 写成 Gate PASS。
- 输出 Decision、P0/P1/P2/P3 counts、逐项 finding（精确文件/位置、影响、最小修复）和 scope limitations；无开放问题时给 APPROVED (0/0/0/0)。

## 严格边界

只读以上 11 个 pin 文件；不访问任何未 pin 路径或 .tmp.driveupload；不运行 shell/grep/rg/PowerShell/测试/getter/hash/R8/capture/Build-Cargo/AC1–AC7；不写文件、不改 Gate。若无法在该读取边界内完成复核，返回 BLOCKED / REVIEW_SCOPE_LIMITATION，不要扩大范围。Review 不授权 R8/capture，也不代表 Gate PASS。
