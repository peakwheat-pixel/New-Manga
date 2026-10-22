# Independent Review — P02PRE-R1F exact frozen inputs

Reviewer role: DeepSeek Harness, non-author. Author/Owner/Integrator/Adjudicator: Codex `/root`.
Repository: `G:/CODEX/New Manga`, branch `main`, base/reviewed HEAD `cddff58469b56e181019a8ddfeade80684bc7eb9`.

## Exact reviewed inputs

- Task `doc/tasks/P02PRE-R1F.md` — 8,939 bytes; SHA-256 `B6624F8CFFF9D40A91B3ED01FA5618951B9CBB93B8E1617D217F8D355FA3DA41`.
- Frozen manifest `verification/P02/p02pre-r1f-manifest-20261011.md` — 8,882 bytes; SHA-256 `11CB16047CEB54419EAE7D17505DC36566E6EF119979E0C15645DAD19C5C758E`.
- Capture script `verification/P02/p02pre-r1f-capture.ps1` — 49,977 bytes; SHA-256 `0A421B5FB6D7BA9AECDB5475459E1D2E385508A5664996C43DA0F2000BFCC9BC`.
- Windows PowerShell 5.1 parse evidence `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r3-20261011.json` — 1,766 bytes; SHA-256 `EC7E24D63AE28F2A2EA135DFC5A35A851C214C67BF8C95A64105410913A6257F`; records `PARSE_OK`, exit 0, child/parent input SHA match, and `captureScriptInvoked=false`.
- Prior R1 adjudication and evidence Review are context only: `verification/P02/p02pre-r1-adjudication-20261011.md`, `verification/P02/dsh-p02pre-r1-evidence-review-20261011.md`. The prior R1 output remains immutable; do not read, decode, or reproduce its Git-status Base64 or path inventory.
- Inherited scope sources, only as needed to verify the declared delta: `verification/P02/p02pre-r1-manifest-20261011.md` and `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md`.

Codex independently checked the four pins with .NET SHA-256, `Get-FileHash`, and `certutil`; do not claim your own hash verification unless actually possible. Review the exact files from the shared workspace and report if any bytes are inaccessible.

## Assignment and boundaries

Review only this R1F delivery for architecture/security and verification completeness. Do not edit files, run commands, execute/parse the capture script, query host/OS/token/path/ACL/environment/registry/WER, create a profile, write a canary, build/Cargo, or run AC1–AC7. Do not infer test results from source review. Do not repeat broad runner/source-contract side-effect research; R0 is closed and the user explicitly accepted that residual risk. Do not use Qoder.

Check whether Task + manifest + script remain aligned and stay inside the exact read-only R1F scope. In particular:

1. R1 F-01…F-04 remediation: tracked symlink leaf skip is permitted only when Git mode is `120000` and the live leaf is a reparse point; record metadata only and never read/hash/follow target. Parent reparse, untracked/unknown reparse, mode mismatch, container/submodule (`160000`), unsupported Git mode, or path escape must fail-stop. Confirm counts distinguish candidate paths from terminal NUL split artifacts and that partial results preserve first blocker/omitted counts.
2. Parser and command records: PS 5.1 compatibility; the parser JSON is parse-only; self-checks assert no-follow classifier, NUL/index parser behavior, and one named command object. Check whether any PowerShell pipeline/output can reintroduce arrays/placeholders.
3. Execution boundary: only the frozen Windows PowerShell runner plus listed `whoami /all` and fixed Git commands; verify actual arguments are fixed and no shell/package manager/compiler/network/COM/helper is launched by the script.
4. Write boundary: the only script-side write should be one exclusive `FileMode.CreateNew` JSON at the exact R1F evidence path. Check for any file/registry/ACL/profile/canary mutation, retry, cleanup, transcript, or alternate output. Registry opens must be read-only; ACL operations query-only.
5. Evidence quality: exact identity/Git checks; status/raw bytes; protected hashes and ACL endpoint comparisons; WER/TEMP/cache getters; fail-stop on query/identity/path/hash errors; size-limited partial evidence must not erase original stop reason. Look for false `PASS_WITH_EVIDENCE`, false `FAILED`, or missing `UNPROVABLE` / `REQUIRES_ACTIVE_TEST` labels.
6. Confirm R1F does not claim to prove `private_registry_absence`, profile store/API effects, effective WER policy, transient access/write closure, hardlink/ADS invariants, dynamic child closure, or any Build/AC result. The standing values remain `private_registry_absence=UNPROVABLE`, Technical Gate=`NOT_SATISFIED`, Owner Risk Acceptance=`APPROVED`, Gate Disposition=`WAIVED_BY_OWNER`, Build Authorization=`AUTHORIZED_WITH_EXCEPTION`, and Build Gate=`BLOCKED` until later evidence/adjudication.

Return an independent review in Chinese, following `doc/templates/REVIEW.md` where applicable. Include reviewed IDs/HEAD and exact input pins, a decision (`APPROVED` or `CHANGES_REQUESTED`), P0/P1/P2/P3 counts, Architecture and Verification conclusions, and findings with stable IDs, severity, precise file/line, impact, and required correction. Separate any limitation caused by inaccessible files. Review is not capture release, Gate PASS, Build authorization, or AC result.