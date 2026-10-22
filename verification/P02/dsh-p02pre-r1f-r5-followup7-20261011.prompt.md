# P02PRE-R1F-R7：Task/manifest evidence-path scope delta 独立 Review

你是非作者 Reviewer（DeepSeek Harness）。请只读审查这次治理范围变更，不修改任何文件，不运行 shell/命令、测试、getter、capture、Build/Cargo 或 AC，也不要查询/安装/启用/启动 Windows Sandbox。

固定上下文：
- Repo G:\CODEX\New Manga；branch main；base HEAD cddff58469b56e181019a8ddfeade80684bc7eb9；tree c25d051a4b9a0bd9773b50170e100f575ea19f2b。
- 已审查 Task doc/tasks/P02PRE-R1F.md，22412 bytes / SHA-256 4F5B27A7E2946EB9258B9EBB213511947D918D8B4DC64500B60F823EE8FFDB70。
- 已审查 manifest verification/P02/p02pre-r1f-manifest-20261011.md，28521 bytes / SHA-256 02CD20C1D4F56D23673E377A68AB352ED6C71A7C3E12349538C191044EBB4D45。
- capture script 未变：verification/P02/p02pre-r1f-capture.ps1，67582 bytes / SHA-256 5A3FE118A8758CCDF0BEDBE170D31B34DA6C338101096EAA825DE80DF70E8316。
- R8 parser=verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json，2595 bytes / SHA-256 2C3BA665FF16D5CD8F9749CEE4BB2BCDCB4102661ACAFDF67A889FEA8F66A696；result=PARSE_OK，Windows PowerShell 5.1.26100.9549，captureScriptInvoked=false。
- 前一轮 follow-up #6 Review 与 Codex adjudication 只释放 R8：REVIEW_ACCEPTED_FOR_R8_ONLY；不得把它升级为 capture release 或 Gate PASS。

这次改动仅为命名 capture 后的独立 Review prompt/stdout/stderr/exit 与 Codex adjudication 文件，并为这组 Task/manifest scope delta 安排 R1F-R7 Review。Task 已允许的 exact paths：
- Pre-run scope Review：verification/P02/dsh-p02pre-r1f-r5-followup7-20261011.{prompt.md,stdout.md,stderr.log,exit}；Codex adjudication=verification/P02/p02pre-r1f-r5-followup7-review-adjudication-20261011.md。
- Post-run Review（capture 后才创建）：verification/P02/dsh-p02pre-r1f-postrun-review-20261011.{prompt.md,stdout.md,stderr.log,exit}；Codex adjudication=verification/P02/p02pre-r1f-postrun-adjudication-20261011.md。
- Capture wrapper 的 stdout/stderr/exit 分别为 verification/P02/p02pre-r1f-capture-20261011.stdout.log、.stderr.log、.exit；唯一 capture JSON 仍是 verification/P02/p02pre-r1f-evidence-20261011.json，由脚本用 FileMode.CreateNew 创建。

请检查完整 Task/manifest 和脚本相关部分，重点给出：
1. 新增 Review/adjudication 路径是否均在 Task 允许写入范围内，路径是否彼此分离且没有覆盖旧证据。
2. Pre-run R1F-R7 Review 文件是在 capture 之前创建；manifest 是否正确要求这些 untracked review files 被 main repository general inventory 发现并 hash。它们不改变 capture child 的可写范围。
3. Post-run Review 文件在 capture 之后创建；是否清楚标注它们不是 capture child 的输出，也不应出现在 R1F T0 inventory。
4. scope delta 是否改变 script、精确 executor/argv、用户/SID、输入/output/canary/TEMP/cache/WER/registry/ACL 路径、子进程边界、禁止写、Owner risk waiver、private_registry_absence 分类或 Build/Gate 状态。Script SHA 与 R8 source pin 应仍完全一致；96-key protectedHashes 数组应仍保持 83+13=96 unique。
5. 任何 P0/P1/P2/P3 findings，及可能阻止一次只读 R1F capture 的具体原因。

Review 结论必须是 APPROVED 或 CHANGES_REQUESTED，列出 P0/P1/P2/P3 数量，findings逐项写明路径/行、触发条件、影响和最小修复；并说明未覆盖风险。不要执行任何动作，也不要把 Review 结论称为技术 Gate PASS、capture result 或 Build authorization。