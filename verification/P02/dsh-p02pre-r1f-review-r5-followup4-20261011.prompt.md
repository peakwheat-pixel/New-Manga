# DeepSeek Harness 只读 Review 请求：P02PRE-R1F Review Round 5 follow-up #4

请作为非作者 Reviewer，只复核下列固定的 11 个输入文件。Task=`P02PRE-R1F`；Repo=`G:/CODEX/New Manga`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。Owner/Author/Integrator/Adjudicator=`Codex /root`。上一轮 DSH follow-up #3 报告 `APPROVED`，但 Codex 集成发现其“8 个输入均在 protected list”断言有一项错配；当前候选新增 12 个固定路径并重跑了 exact-script PS 5.1 self-check。请独立核对新候选是否闭合。

## 固定输入 pins

1. `doc/tasks/P02PRE-R1F.md` — `21390 bytes / SHA-256 3C83EA4172B06FE500EDB8335DD6517390C7D4B9B70462B3A02AAA6FD8B86CAD`
2. `verification/P02/p02pre-r1f-manifest-20261011.md` — `23135 bytes / SHA-256 9D0086457D06DFDCFE071E963BC7D1F2818ABDB6A985C2D13D2B9B92260910B4`
3. `verification/P02/p02pre-r1f-capture.ps1` — `66560 bytes / SHA-256 F55F195E0A746B8D6B1EA19A7FA212495FDFA4F4FEAB6CF281BECE65173AC8E8`
4. `verification/P02/p02pre-r1f-r5-followupfix3-selfcheck-20261011.json` — `2927 bytes / SHA-256 18BD55A9119ADD7253CAD00D87843EEF4A6B047900BB1D47964437E23E465B97`
5. `verification/P02/p02pre-r1f-r5-followup3-review-adjudication-20261011.md` — `4500 bytes / SHA-256 98F2AF2B56EBC857EC2311AEDD8D27F1F651E90C91FA043EF59ED03AE7302AE0`
6. `verification/P02/dsh-p02pre-r1f-review-r5-followup3-20261011.stdout.md` — `14724 bytes / SHA-256 B69904CA3FCBE8BC246E88B70D914E7CEDB5C7E5B5908C48FE5BB472B7E5F87E`
7. `verification/P02/dsh-p02pre-r1f-review-r5-followup3-20261011.prompt.md` — `3438 bytes / SHA-256 0CD792CCEAE5EB895C06E96B40FB92D080197446C0943824F7385B8E62EED4EE`
8. `verification/P02/p02pre-r1f-r5-followupfix-selfcheck-20261011.json` — `2307 bytes / SHA-256 FE2277D0410B6E9CAB84D2CF1551FBCF4886B57A8DE9E4EAE2B305FDC44F237C`
9. `verification/P02/p02pre-r1f-r5-followup2-review-adjudication-20261011.md` — `4950 bytes / SHA-256 EBBF269659F9C7F058FCA968C7A619EB51900FAFD9476AA801F99570B478575B`
10. `verification/P02/p02pre-r1f-followupfix-selfcheck-wrapper-attempt1-20261011.md` — `1179 bytes / SHA-256 CABB770B21701E96A083D1FB22E55122ECD89CCA5EE86114A5393697027D9703`
11. `verification/P02/dsh-p02pre-r1f-review-r5-followup3-20261011.stderr.log` — `119856 bytes / SHA-256 C5F45CBD520AA9628968724654FC1076EBE769AF68602BE05AD59E7324DC7CFC`

## Review focus

- 逐字核对 script 的两个 protected-key arrays。特别确认本轮 Codex adjudication `p02pre-r1f-r5-followup3-review-adjudication-20261011.md`、follow-up #2 adjudication、follow-up #3 prompt/stdout/stderr/exit、自检3，以及预定 follow-up #4 prompt/stdout/stderr/exit/adjudication 是否都在冻结脚本中；确认新加 12 个路径与旧 72 条无重复，合计 `84/84 unique`。切勿依据旧报告的行号或相似文件名推断路径相同。
- 检查 manifest 关于已列 Review artifact 的措辞、structured skip counts、旧 self-check pin #8、当前 PS 5.1 self-check 的 source/transport/exit 证据与 Task release 顺序是否与 script 一致。
- 核对 release 顺序：follow-up #4 `APPROVED` + Codex pin/path adjudication → Windows PowerShell 5.1 parser R8 parse-only → Codex pre-run adjudication（核验 84 个路径存在性和 hash）→ 单次 capture。确认所有 owner waiver / Build / AC 状态没有被误记为 PASS。
- 只报告可从这 11 个 pins 直接复现的问题，给 P0/P1/P2/P3、精确文件/位置、影响和最小修复。无开放问题时给 `APPROVED` 与 `0/0/0/0`。

## 边界

只读以上 11 个 pin 文件，不访问其他路径或 `.tmp.driveupload`，不运行 shell/grep/rg/PowerShell 命令、测试、getter、hash、R8、capture、Build/Cargo 或 AC1–AC7，不写文件，不改 Gate。若无法在该读取边界内完成 path membership 核验，报告 `BLOCKED / REVIEW_SCOPE_LIMITATION`，不要自行扩大读取范围。Review 不授权 R8/capture，也不代表 Gate PASS。
