# P02 Smoke Admission — Current Stage-1 Preflight R2

- Captured: `2026-10-10T04:11:59.5066498+08:00`; completed: `2026-10-10T04:12:58.602+08:00`; result: `PRESTART_STAGE_1_PASS` (`16/16` frozen thresholds true).
- Reviewed delivery: `c85a041c514f3c0dd1c355a2d09f064dbc64e749` / tree `b67e3e02186a8009c46da0dba819003b04acfec1`; independent R6 exact-head Review=`APPROVED`.
- Shell: `C:\Program Files\PowerShell\7\pwsh.exe` PowerShell `7.6.6`, PID `20492`, `Environment.UserInteractive=True`, elevated=`False`.
- Feature InstallState=`1`. WSB AppX=`MicrosoftWindows.WindowsSandbox_0.8.107.0_x64__cw5n1h2txyewy` version=`0.8.107.0`; `wsb.exe` version=`0.8.107.0`, bytes=`156160`, SHA-256=`247e092b5c5bd37820f225a7dd3ddf10ae37a67e2751a19c24b802c84769c441`; version/list exits=`0/0`. `wsb list --raw` returned JSON with `WindowsSandboxEnvironments=[]` (0 environments).
- Hardware: architecture CIM `9`, firmware virtualization `True`, physical cores `16`, total RAM `31.647 GiB`, available RAM `16765 MiB`, C:/G: free `328.904/1299.429 GiB`.
- HostFolder roots `12/12` match; input pins `20/20` hashes, `14/14` registered sizes, `6` unregistered sizes.
- Root manifest `203/203` entries; missing/extra/status/content mismatches=`0/0/0/0`; candidate/root overlap `[]`. Frozen root manifest HEAD=`549a6544f0be1eec66c09ece393fd1a409f10bf3`, live root=`main@ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50`.
- Reviewed XML canonical LF `2609 bytes` / `9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d`, mappings `11` (10 RO + 1 RW), LogonCommand count `0`.
- Aggregation correction: `wsb list --raw` returns JSON; “empty” is determined by `WindowsSandboxEnvironments=[]`, not by zero stdout bytes. Raw capture and host measurements are unchanged.
- Fixed clone exists=`False`. This remains pre-admission evidence only: Smoke admission=`NOT_ADMITTED` pending separate Codex checkpoint; complete preflight=`BLOCKED / INCOMPLETE`; Build Gate=`BLOCKED`; build=`NOT_AUTHORIZED / NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`; Hard Build Barrier=`EFFECTIVE`.
- No clone, Sandbox, Smoke, Build, runner, Vitest, GUI, WebView, or product test was started.
- Machine-readable evidence: [observations R2](codex-smoke-admission-preflight-r2.json).
