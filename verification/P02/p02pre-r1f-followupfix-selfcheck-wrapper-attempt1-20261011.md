# R5 follow-up-fix isolated self-check wrapper attempt 1

Timestamp=`2026-10-11 09:18:13 UTC`. Parent orchestration engine=PowerShell `7.6.6`; intended child=`C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` (`5.1`).

The wrapper attempted to pass the full Base64-encoded source as part of the child `-EncodedCommand` argument. `Process.Start()` failed before creating the child process:

```text
An error occurred trying to start process 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' with working directory 'G:\CODEX\New Manga'. FileName or extension is too long.
```

Classification=`HARNESS_FAILURE / CHILD_NOT_STARTED`, not a parser/self-check result and not a capture-script failure. The candidate source was read and hashed by the parent; the Windows PowerShell 5.1 child did not start, so no parsing or assertions ran. No capture script, host getter, registry/ACL operation, or repository state write ran. The unique self-check result target `p02pre-r1f-r5-followupfix-selfcheck-20261011.json` was not created. Retry will stream source bytes through redirected stdin after starting the child, then retain the attempt-2 result at the unique target.
