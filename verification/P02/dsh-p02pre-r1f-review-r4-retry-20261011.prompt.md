# P02PRE-R1F Round 4 retry：修正继承 manifest hash pin

你是非作者 Reviewer=`DeepSeek Harness`。请续用本项目指定 DSH session，对下列冻结候选作只读 Review。仓库=`G:/CODEX/New Manga`，branch=`main`，HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。Owner/Author/Integrator/Adjudicator=`Codex /root`。

上一条 Round 4 dispatch 因 DSH 与外层 runner 同时写 `...review-r4-20261011.stdout.md` 而发生 sharing violation，Codex 已中断该运行。该次没有 Review 决定：原 stdout 为 0 bytes；stderr/exit 原样保留为失败派发诊断，外层 CLI exit 未采到。当前候选未改变 Review 范围，也没有放行 capture。

## 本轮精确输入

- Task=`doc/tasks/P02PRE-R1F.md`，`13685 bytes / SHA-256 4F58CEA9C751E20751C3587B0353F3E46527D57050225AD9B33B9FEB6AC31330`
- Manifest=`verification/P02/p02pre-r1f-manifest-20261011.md`，`13682 bytes / SHA-256 91818614AB08DF6C49DF40572C101796DFC40494A2184D7FCCD00BBD5D8A8A42`
- Capture script=`verification/P02/p02pre-r1f-capture.ps1`，`56449 bytes / SHA-256 99B1D9B158C6E9534A9CDE946AE0380C0034D0A407C67D75A8CB902E2E4E1FC7`
- R1 source manifest=`verification/P02/p02pre-r1-manifest-20261011.md`，`12615 bytes / SHA-256 A5510774B47C17EB29C5BF5D73FE7B755C72E2726FC5280E7EF11A91A23C67A7`
- Cross-source pins: `doc/tasks/P02PRE-R1.md:89`, `verification/P02/p02pre-r1-adjudication-20261011.md:27`, and `verification/P02/p02pre-r1-evidence-20261011.json:2627` contain the same R1 manifest hash. Codex independently checked .NET SHA-256, `Get-FileHash`, and `certutil`, all matching.
- R3 Review approved older Task/manifest/script bytes but repeated the shortened 63-digit R1 hash as “64-digit”; do not treat that Review as approval of these corrected bytes.
- R6 parser artifact binds the older script SHA `4FB853E696D2BDF86BA48D5C7C45E006D90356C66EB450D6856AD55B89F37D54`; it is historical and does not parse this candidate.

## Review scope

1. Confirm the corrected R1 pin is exactly 64 hex digits and agrees with the cited R1 sources; no R1 Task/manifest/script/evidence was changed.
2. Review the Task/manifest correction and the exact script diff. Script changes should only add the preserved Round 4 dispatch-failure artifacts, this retry's prompt/stdout/stderr/exit, and the future R7 parser JSON to the protected-hash inventory. Confirm no capture/getter/write behavior was introduced.
3. Confirm prior R1F findings remain closed; the fixed single `CreateNew` output, executor and child-process scope remain exact; no profile/API/registry/ACL/canary/build/Cargo/AC action was added; user-data exclusions remain; Gate/waiver state is unchanged.
4. Return `APPROVED` with P0/P1/P2/P3 counts only if no blocker remains. If approved, state that this releases only the subsequent R7 PS 5.1 parse-only check. Capture and all Gates remain unreleased.

## Strict limits

- Read-only only. Do not run commands, parsers, getters, capture, registry/profile/ACL operation, build/Cargo, AC1–AC7, canary, or Windows Sandbox action. Do not modify any files.
- **Do not write Review artifacts to the shared filesystem.** Return the full concise Review report only in your final response. Codex's outer DSH CLI wrapper will save stdout/stderr/exit into the separately authorized retry artifact paths. This supersedes the prior attempt's conflicting file-write instruction.
- State any evidence you could not independently verify. Do not claim Gate PASS.

## Gate state to preserve

`private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; exact text `technical condition unmet; user explicitly accepted residual risk`. Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; Build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`. Windows Sandbox remains untouched.
