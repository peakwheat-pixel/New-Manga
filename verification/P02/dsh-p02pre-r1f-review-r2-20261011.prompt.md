# Independent Review Round 2 — P02PRE-R1F exact frozen inputs

Reviewer: DeepSeek Harness, non-author. Owner/Author/Integrator/Adjudicator: Codex `/root`.
Repository: `G:/CODEX/New Manga`, branch `main`, reviewed HEAD `cddff58469b56e181019a8ddfeade80684bc7eb9` (working tree is dirty; the exact file pins below define the delivery).

## Exact reviewed inputs

- Task `doc/tasks/P02PRE-R1F.md` — 10,192 bytes; SHA-256 `79CD06C91D5091A3320832A9AD3B8606D6EC7E2E3F7912A27C5240F92294C98A`.
- Manifest `verification/P02/p02pre-r1f-manifest-20261011.md` — 10,490 bytes; SHA-256 `23AF217DBE050CCC4D15990DDBE231CD2DCE3A3E0976637B388430D35C2BE218`.
- Capture script `verification/P02/p02pre-r1f-capture.ps1` — 55,065 bytes; SHA-256 `20C9D1C2C8FBE87D9EFFA84C14A29B17363958B9D95D7D47C02960BC5A3CBF9F`.
- Context: Round 1 Review `verification/P02/dsh-p02pre-r1f-review-20261011.stdout.jsonl` (actual content is Markdown) and Codex adjudication `verification/P02/p02pre-r1f-adjudication-20261011.md`.

Codex independently checked the three exact pins with .NET SHA-256, `Get-FileHash`, and `certutil`. Do not claim you independently recalculated them unless you actually can. Report any inaccessible or mismatched file explicitly.

## Assignment

Perform an independent, read-only Round 2 review of the exact Task, manifest, and script above. Determine whether the implementation resolves the five Round 1 findings and whether the frozen contract still matches the implementation and stays within the authorized R1F read-only scope. Review source and the two context records only.

Round 1 findings to adjudicate independently:

1. F1 P1: all repository fail-stop paths need accurate `firstBlockingPath`, `omittedCount`, candidate-count-known semantics, and an operation/error record; unknown candidate counts must not appear as zero omissions.
2. F2 P2: strict UTF-8 failures for both path inventory and `ls-files --stage` need explicit stop states; case-only path collisions must fail-stop under Windows path semantics.
3. F3 P2: the inherited R1 manifest pin was 65 hex characters; the R1F manifest should use the 64-character value recorded by the R1 Task without rewriting the old R1 history.
4. F4 P3: link inventory field name should match the manifest (`mode`).
5. F5 P3: after a tracked symlink leaf is skipped, no further getter/hash/ACL query may run for that path; the code and manifest should state this invariant.

Also check that:

- Tracked symlink skipping still requires Git index mode `120000` and a live leaf `ReparsePoint`; every other reparse/mode mismatch, submodule, unsupported object, or path escape remains fail-stop.
- Parser/count self-checks and single-command-object assertions are coherent with PowerShell 5.1 and do not invoke the capture or host getters during this review.
- The script launches only the frozen PowerShell runner and the listed `whoami /all`/Git children; registry getters remain read-only; the only script write remains the unique exclusive evidence JSON.
- Claims remain bounded: do not infer host runtime outcomes, registry absence, profile API safety, dynamic child/write closure, Build, or AC1–AC7 from source review.

## Boundaries

Do not edit any file. Do not run commands, execute or parse the capture script, query host/OS/token/path/ACL/environment/registry/WER, create/delete a profile, modify ACL/registry, write a canary, build/Cargo, or run AC1–AC7. Do not repeat broad R0 runner/source-contract research; R0 is closed. Do not use Qoder.

## Required response

Respond in Simplified Chinese, following `doc/templates/REVIEW.md` where applicable. Include reviewed Task ID/HEAD and the exact input pins; decision=`APPROVED` or `CHANGES_REQUESTED`; P0/P1/P2/P3 counts; Architecture and Verification conclusions; stable finding IDs with severity, exact file/line, impact, and required correction. Separate any limitation caused by inaccessible files. State that this review is not capture release, Gate PASS, Build authorization, or an AC result.
