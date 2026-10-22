# P02PRE-R1F Round 4 独立 Review：修正继承 manifest hash pin

你是非作者 Reviewer=`DeepSeek Harness`。请在共享仓库 `G:/CODEX/New Manga`、当前 branch=`main`、HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9` 上只读审查冻结候选。Owner/Author/Integrator/Adjudicator=`Codex /root`。本轮只审文档 pin 修正与 capture script protected-hash 清单增量，确认先前 R3 闭合内容未回归。

## 精确输入 bytes

- Task=`doc/tasks/P02PRE-R1F.md`，`12812 bytes / SHA-256 51BD45ECAF08F67F0824CA989B20F1DD0211BE966846E07683DF58D2B25AD2AB`
- Manifest=`verification/P02/p02pre-r1f-manifest-20261011.md`，`13263 bytes / SHA-256 15FD7795833A3D62D7AD0B322D4DA7B8E7AFF41C4FC88C67AA17947C307F21F0`
- Capture script=`verification/P02/p02pre-r1f-capture.ps1`，`56051 bytes / SHA-256 1CBED581B0A774DA78C619F80272B98C4CB1D7B3DB633A2722FEA5673C507737`
- R1 source manifest=`verification/P02/p02pre-r1-manifest-20261011.md`，`12615 bytes / SHA-256 A5510774B47C17EB29C5BF5D73FE7B755C72E2726FC5280E7EF11A91A23C67A7`
- R1 source cross-checks: `doc/tasks/P02PRE-R1.md:89`, `verification/P02/p02pre-r1-adjudication-20261011.md:27`, and `verification/P02/p02pre-r1-evidence-20261011.json:2627` record that same 64-digit SHA. Codex independently ran .NET SHA-256, `Get-FileHash`, and `certutil`; all returned the same value.
- Prior R3 Review report=`verification/P02/dsh-p02pre-r1f-review-r3-20261011.stdout.md` (R3 approved the older Task/manifest/script bytes; the report's assertion that the inherited pin was 64 digits was incorrect because the R1F literal omitted the final `7`).
- Prior R6 parser artifact=`verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r6-20261011.json` binds the older script SHA `4FB853E696D2BDF86BA48D5C7C45E006D90356C66EB450D6856AD55B89F37D54`; it is historical for this review and does not parse the current script.

## Review questions

1. Confirm the corrected R1 manifest pin in the exact Task and manifest is 64 hexadecimal digits and matches all cited R1 sources; ensure no R1 input or result was modified.
2. Review the Task/manifest scope and exact script diff. The script delta should only add these exact artifacts to its protected-hash inventory: Round 4 prompt/stdout/stderr/exit and `p02pre-r1f-parser-windows-powershell-5.1-r7-20261011.json`. Confirm this introduces no execution, getter, or write behavior.
3. Recheck the previously reviewed safety/acceptance boundaries relevant to the capture: one `FileMode.CreateNew` evidence output, fixed Windows PowerShell 5.1 executor and listed Git/whoami children, no profile/API/registry/ACL/canary/build/Cargo/AC action, no reading user manga/database/Lock/Revision/model/credential/WER dump contents, and all non-PASS risk states remain unchanged.
4. Confirm R3 findings remain closed, and identify any new blocker or required correction. If no P0–P2 issue remains, return `APPROVED` with counts `0/0/0/0` and state that this releases only the subsequent R7 parse-only step; it does not release capture or any Gate.

## Strict limits

- Read-only review only. Do not run commands, parser, host getter, capture, registry/profile/ACL operation, build/Cargo, AC1–AC7, canary, or Windows Sandbox action. Do not modify source files or governance files.
- Keep all historic Review evidence unchanged. Return a concise finding table and an overall decision with P0/P1/P2/P3 counts. Explain any conclusion that could not be independently verified.
- Write raw final Review text to `verification/P02/dsh-p02pre-r1f-review-r4-20261011.stdout.md`; diagnostics to `.stderr.log`; numeric process exit to `.exit`. Do not write elsewhere.

## Current risk/Gate state

Keep `private_registry_absence=UNPROVABLE`, Technical Gate=`NOT_SATISFIED`, Owner Risk Acceptance=`APPROVED`, Gate Disposition=`WAIVED_BY_OWNER`, Build Authorization=`AUTHORIZED_WITH_EXCEPTION`, and exact text `technical condition unmet; user explicitly accepted residual risk`. Build Gate remains `BLOCKED`; Hard Build Barrier remains `EFFECTIVE`; Build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`. Windows Sandbox remains untouched.
