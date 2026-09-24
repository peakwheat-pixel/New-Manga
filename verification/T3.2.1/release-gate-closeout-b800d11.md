# T3.2.1 Full Release Gate Closeout Decision

Date: 2026-09-24 (Asia/Shanghai)
Decision owner: Codex
Decision: **OPEN — NOT RELEASE READY; NO PRODUCT INTEGRATION AUTHORIZED**

> Latest closeout checkpoint and O-12-2 disposition are appended at the end of
> this record. The opening section remains the historical assessment snapshot.

This is a Codex closeout assessment, not a new implementation Task. The main
recovery point at assessment start was `G:/CODEX/New Manga`, `master` at
`b800d117eadc182784097f7694b416b5cdd58e11`. The product Gate baseline remains
`c2fcb1ce575099f6e74f69c711f423040a545951`; its decision was **PASS TO START**,
which authorized implementation and did not pass the release Gate.

The author recovery point is
`G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-10`, branch
`agent/antigravity/T3.2.1-repair-10`, actual Handoff/tip
`d7edea5f00507a8d9601e6a95294695353cbf7f6`. The independent REPAIR-10 Reviewer
branch is `agent/deepseek/T3.2.1-review-be5200e`. Codex made the O-1 correction
on a separate candidate branch described below. No product or repair branch was
merged into `master`.

## Independent Review record

Review decisions apply only to their fixed slice and head. The two approved
reviews below do not add up to a T3.2.1 full-Gate approval.

| Slice | Fixed objects | Independent Review | Decision and coverage |
|---|---|---|---|
| REPAIR-7 | Delivery `ad62481`; later REPAIR-8 handoff `37d5488` | `6cf9185` was `changes_requested`; REPAIR-8 report says it supersedes the F-001/F-002 dispositions | History only; REPAIR-8 resolves those documentation findings. |
| REPAIR-8 | Base `e24ea5b91cef735ff7c40ca8407a3e69c6a1deb7`; delivery `3cdfdee126e8aab6b7930e49460a753abc69dad0`; Handoff/tip `37d5488ebf8e33f897e802b4147cbd5fb1ad8e04` | `2585efd69009cd7620c6b020e67df90c7d49b0f1`, `agent/deepseek/T3.2.1-review-repair-7` | `approved`, documentation slice only. F-003 wording was deferred and remains open. Report: `git show 2585efd:verification/T3.2.1/repair-8/review-3cdfdee.md`. |
| REPAIR-9 | Delivery `d2bf6a8621c0c89c077e181e3e7bec9ac7cf098f`; Handoff/tip `eeb095ea94cdf0d477bcb09ab7c761883b06f833` | `85f8c59d0a012c1edc4e466187b5b42515297d74`, `agent/deepseek/T3.2.1-review-d2bf6a8` | `changes_requested`. F-1 was P1; F-2/F-3/F-4 and O-3 were also recorded. Report: `git show 85f8c59:verification/T3.2.1/repair-9-review/review-d2bf6a8.md`. |
| REPAIR-10 | Base `eeb095ea94cdf0d477bcb09ab7c761883b06f833`; delivery `be5200efe91a365356e5baac93ea6a71f5fa1520`; Handoff/tip `d7edea5f00507a8d9601e6a95294695353cbf7f6` | `ddc21a2f3cf5521675e95d6e2a8f8f50b1c065fb`, `agent/deepseek/T3.2.1-review-be5200e` | `approved` for packaging-test path independence and its evidence only: 12 passed, 0 skipped, exit 0 with `PYTHONPATH` unset. It did not rerun PyInstaller or Sandbox and did not assess AC3/5/6/7/8/9 or R-014–R-016. Report: `git show ddc21a2:verification/T3.2.1/repair-10/review-be5200e.md`. |

The review commits are in the shared Git object database; the `git show`
commands above retrieve the original reports without copying or editing
Reviewer-owned files.

## O-1 and evidence disposition

REPAIR-10 Review O-1 reproduced a trailing space on line 6 of
`verification/T3.2.1/repair-9/sandbox-run.log`; the original REPAIR-9 range
`37d5488..d2bf6a8` failed `git diff --check` with exit 2. Codex removed that one
space on isolated branch `codex/T3.2.1-release-gate-closeout`, worktree
`G:/CODEX/New Manga.worktrees/T3.2.1-codex-release-gate-closeout`:

- Base: `d7edea5f00507a8d9601e6a95294695353cbf7f6`.
- Codex correction: `188d72a9d144b8cab16f77757abc46318ac8e5e6`.
- Only changed path: `verification/T3.2.1/repair-9/sandbox-run.log`.
- Original blob: `f7cb13c543184a6767500bff35b4256a457fca38`; corrected blob:
  `df14a64d8e566e05c89b96e4272d48dc033726b2`.
- Fresh cumulative check: `git diff --check c2fcb1c 188d72a` exit 0; the same
  range from `37d5488` also exits 0. The exact commands and outputs are in
  [release-gate-closeout-verification.log](release-gate-closeout-verification.log).

This closes the trailing-space fact in the Codex candidate tree; it does not
rewrite the old REPAIR-9 Review or make that delivery approved. REPAIR-9's F-2
build-head/worktree binding, F-4 Sandbox stderr description and O-3 author-vs-
cumulative-scope wording remain open. REPAIR-10 closes the F-3(b) packaging-test
path dependency only. REPAIR-10 also replaced the same-named
`verification/T3.2.1/repair-9/diff-check.log`; the previous blob remains
retrievable with `git show eeb095e:verification/T3.2.1/repair-9/diff-check.log`.
The two versions cover different ranges and must not be conflated. The request's
purported full tip `d7edea59a72173f4b5952f4bc90a07e155bc2eb5` does not exist; the
verified tip is `d7edea5f00507a8d9601e6a95294695353cbf7f6`.

For REPAIR-9 F-1, Codex has fixed the line-level cause and independently rerun
the cumulative check on the corrected candidate. The old Handoff's claim about
the earlier `d2bf6a8` check remains historical and was not rewritten. The F-1
remediation is ready for confirmation in the final independent full-scope
Review; it is not a substitute for that Review.

## Gate status

| Gate | Codex disposition | Evidence still required |
|---|---|---|
| AC1 / AC2 | `PARTIAL` | Existing builds and manifests exist, but the REPAIR-9 logs identify `dce928f` as the build HEAD rather than fixed delivery `d2bf6a8`. Rebuild from the final fixed and reviewed candidate, bind both build logs to that tree, record dependencies, manifests, differences and hashes. |
| AC3 | **`NOT_RUN` — release blocker** | A baseline artifact failed QtCore import in Sandbox. REPAIR-9's fixed package passed `--smoke-test` in Sandbox, but the required real-window, interactive release workflow has not run. Do not mark AC3 `PASS`. |
| AC4 | `PARTIAL` | The REPAIR-9 review independently confirmed Qt/ICU symbol closure evidence and a Sandbox smoke without DLL import failure. The delivery is still `changes_requested`; the full production window/QML workflow and final-head review remain outstanding. Its Sandbox stderr also included 12 QML `TypeError` entries (F-4), not only style warnings. |
| AC5 | `NOT_RUN` | On a fixed package without optional model/OCR dependencies, start Core/UI and verify the missing Provider state is diagnostic and non-crashing. |
| AC6 / AC7 | `PARTIAL / NOT_RUN` | Complete the package UI path with disposable fixtures, restart and verify persisted state; capture source hashes, Managed Copy, Lock, current/pinned Revision, human-confirmed content, SQLite rows and Secret/log checks. Existing service-level probes do not substitute for this GUI run. |
| AC8 | `PARTIAL / NOT_RUN` | Verify default and Unicode `--data-root`, read-only program location, normal-user operation, `tasklist` after exit and SQLite lock release in the clean environment. |
| AC9 | `PARTIAL / NOT_RUN` | Measure at least five actual GUI cold starts on recorded recommended hardware, with raw values and P50/P95 method. Existing five-run `--smoke-test` P95=1.09s is offscreen and is not the bookshelf-ready measurement. Windows 10 best-effort remains separately `NOT_RUN` unless actually tested. |
| AC10 | `PARTIAL / NOT_RUN` for full Gate | Obtain a final DeepSeek Harness non-author Review of the fixed complete delivery/evidence, then Codex records isolated integration verification and a decision. No full-scope approval or integration evidence exists. |
| R-014–R-016 | `OPEN` | R-014: independent Build 2 log and raw process list; R-015: correct the `dict[str, any]` annotation in `verify_path_safety.py` and run it under separately authorized scope; R-016: reconcile the 275/160 test totals with exact commands, environment and collected/pass/skip/fail counts. |
| F-003 | `OPEN / deferred P2` | Four REPAIR-6 phrases still need the authoritative revision/blob wording (`297c3dd` + `fdddfc19…`) when those files are next authorized for editing. |

## Available environment and executable closeout sequence

Windows Sandbox can run the planned isolated Windows-userland checks without a
separate physical test PC; whether its evidence satisfies the D07 clean-machine
boundary will be judged from the full run, not assumed in advance. Sandbox is
installed at
`C:\Windows\System32\WindowsSandbox.exe`. The already recorded guest is
Windows 11 Enterprise x64 build `26100`, account `WDAGUtilityAccount`, with no
`python`, `py` or `git` command. The host is Windows 11 Pro x64 build `26200`.
Sandbox is ephemeral and provides a clean Windows userland, but shares the
physical host. The host is Windows 11 Pro 25H2 build `26200.9457`, AMD Ryzen 9
7950X3D (16 cores / 32 logical processors), 31.6 GiB RAM. Record the active
display resolution in the Sandbox run for AC9. Do
not treat a Sandbox run as evidence for Windows 10. Required items are the
final fixed onedir artifact and SHA-256 manifest, a disposable manga/image
fixture, isolated Sandbox data roots, a read-only mapped artifact folder, and a
writable host evidence folder for transcripts/screenshots/video and exported
database evidence. No user library or credentials are needed.

1. **Freeze and review the remaining repair evidence.** Close REPAIR-9 F-2/F-4/O-3
   with corrected provenance and accurate stderr/scope language; retain Codex's
   O-1 fix; keep F-003 and R-014–R-016 explicitly open until evidence exists.
   Any source/test-script correction needs its own frozen scope and base. Freeze
   one final source commit and Handoff before building.
2. **Rebuild and bind artifacts.** On the fixed head, run the packaging tests
   with `PYTHONPATH` unset, produce independent Build 1 and Build 2 logs, exact
   environment/dependency snapshots, manifests, hash comparison and Qt/QML
   asset checks. Logs must name the actual source HEAD and working-tree state.
3. **Run the clean Windows workflow on an unmodified package.** Start a fresh
   Windows Sandbox session; verify guest OS/account and absence of Python, `py`,
   `git` and developer PATH entries; verify package hash against the manifest.
   Launch `NewManga.exe` normally (no `--smoke-test`, DLL substitution or
   modified package). Show the real main window and the four routes, then run:
   default bookshelf → create Book → create Chapter → import the disposable
   image → Workbench → Mock/Local Pipeline → Reader → export → close → relaunch
   and verify recovery. Capture screenshots/recording, original stdout/stderr,
   exit codes, database before/after, source hashes and the observed QML errors.
   If the real UI still has null-view-model TypeErrors or any required step
   fails, record the failing AC and do not call AC3 passed.
4. **Complete AC5, AC7 and AC8 on the same fixed artifact.** Confirm Core/UI
   startup without optional model dependencies and the missing-provider message;
   check source/hash and persistence invariants; test default and Unicode data
   roots, read-only program files and explicit `--data-root`; capture `tasklist`
   and prove SQLite locks release after exit. Keep all data under disposable
   Sandbox roots.
5. **Run AC9 and close evidence.** Record host CPU/RAM/display, at least five
   real GUI cold-start samples through bookshelf interactivity, raw timings and
   P50/P95 calculation; separately mark Windows 10 `NOT_RUN` if no such guest is
   available. Resolve R-014–R-016 only with their required raw evidence.
6. **Final independent Review and Codex integration check.** DeepSeek Harness
   reviews the fixed full delivery, all Gate evidence and remaining findings as
   a non-author Reviewer. If approved and all Gate criteria are satisfied,
   Codex runs the integration checks on an isolated candidate and writes the
   integration evidence. Until both Review and full Gate closure are recorded,
   no REPAIR-7/9/10 or related branch may be merged into `master`.

## Recommended next Task (not registered or released here)

- **Task**: `T3.2.1-REPAIR-11` — close REPAIR-9 evidence/documentation findings and deferred F-003 wording.
- **Owner / Reviewer**: Antigravity / DeepSeek Harness (independent; Owner ≠ Reviewer).
- **Recovery point and proposed base**: new Antigravity worktree from Codex candidate
  `188d72a9d144b8cab16f77757abc46318ac8e5e6`; proposed branch
  `agent/antigravity/T3.2.1-repair-11`, proposed worktree
  `G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-11`. Neither is created or
  released here; Codex must register the actual recovery point before work starts.
- **Proposed scope**: new `verification/T3.2.1/repair-11/**` evidence, one new Handoff, and the
  minimum authorized wording updates to `doc/tasks/T3.2.1-REPAIR-6.md`,
  `doc/handoffs/T3.2.1-REPAIR-6-f6dc383.md`, and the REPAIR-9 Handoff to resolve F-2/F-4/O-3
  and F-003. Rebuild from a fixed head only if needed to bind build inputs. No product code,
  test assertions, dependency or Schema changes. R-014–R-016 stay OPEN in this slice.
- **Gate**: fix/check against the registered base, preserve all original Review reports, then
  run `git diff --check <base> <delivery>` and protected-path zero-diff checks, preserve all
  original Review reports, then request a fresh independent Review. This proposed task does not
  close AC3 or authorize a merge.

## Directly forwardable next instruction

```markdown
Codex has recorded the T3.2.1 full Release Gate as OPEN. Continue from
master `b800d117eadc182784097f7694b416b5cdd58e11` and candidate
`codex/T3.2.1-release-gate-closeout` at `188d72a9d144b8cab16f77757abc46318ac8e5e6`.
The candidate contains only Codex's O-1 whitespace correction; it is not a
product integration or a release approval.

Next, register the proposed `T3.2.1-REPAIR-11` from the recommended recovery
point above. Its Owner is Antigravity and its independent Reviewer is DeepSeek
Harness. Close REPAIR-9 F-2/F-4/O-3 and F-003 wording, preserving R-014–R-016 as
OPEN until their separately required evidence exists. Freeze the resulting full
source/Handoff head; rebuild and bind Build 1/Build 2 and packaging evidence to
that exact tree. Use the available Windows Sandbox (Windows 11 Enterprise x64
build 26100) for AC3/AC5/AC6/AC7/AC8 and GUI AC9 checks with an unmodified,
hash-verified package and disposable manga fixtures. AC3 remains NOT_RUN until
the real interactive workflow completes; never mark it PASS based on
`--smoke-test`. Capture the evidence listed in
`verification/T3.2.1/release-gate-closeout-b800d11.md`.

Then obtain a fresh DeepSeek Harness full-scope independent Review and have
Codex complete isolated integration verification and evidence. Do not merge
REPAIR-7/9/10 or any related branch into master before the full Release Gate is
closed. Do not change product code, test assertions, dependencies or Schema
without a separately registered and frozen authorization.
```

## Current Codex full-Gate closeout checkpoint (2026-09-24)

**Owner:** Codex. **Decision:** `OPEN — NOT RELEASE READY; NO PRODUCT
INTEGRATION AUTHORIZED`. This checkpoint records the current repair/review
chain and the explicit O-12-2 disposition. The initial assessment above stays
historical; this addendum supersedes its proposed REPAIR-11 next-task instruction.

### Fixed repair and Review chain

| Slice | Fixed objects | Review disposition | Scope of decision |
|---|---|---|---|
| REPAIR-7 | Delivery `ad62481`; later Handoff `37d5488` | Review `6cf9185` was `changes_requested`; REPAIR-8 superseded its F-001/F-002 documentation dispositions | Historical slice only. |
| REPAIR-8 | Base `e24ea5b91cef735ff7c40ca8407a3e69c6a1deb7`; Delivery `3cdfdee126e8aab6b7930e49460a753abc69dad0`; Handoff/tip `37d5488ebf8e33f897e802b4147cbd5fb1ad8e04` | Review `2585efd69009cd7620c6b020e67df90c7d49b0f1` `approved` | Documentation slice only. |
| REPAIR-9 | Delivery `d2bf6a8621c0c89c077e181e3e7bec9ac7cf098f`; Handoff/tip `eeb095ea94cdf0d477bcb09ab7c761883b06f833` | Review `85f8c59d0a012c1edc4e466187b5b42515297d74` `changes_requested` | Full packaging findings remain open; later repair slices do not constitute full approval. |
| REPAIR-10 | Base `eeb095ea94cdf0d477bcb09ab7c761883b06f833`; Delivery `be5200efe91a365356e5baac93ea6a71f5fa1520`; Handoff/tip `d7edea5f00507a8d9601e6a95294695353cbf7f6` | Review `ddc21a2f3cf5521675e95d6e2a8f8f50b1c065fb` `approved` | `tests/packaging` path independence only. |
| REPAIR-11 | Base `188d72a9d144b8cab16f77757abc46318ac8e5e6`; Delivery `962239521afbfec72025ab01941f89e08116ffc4`; Handoff/tip `941dbc89e139a2e24e6b1d17c900e363995decfc` | Review `4f2f8a07e5b8119834cdc4cfd0fd0aa5c62ac4cc` `changes_requested` | Historical Review remains unchanged; evidence findings were followed up by REPAIR-12. |
| REPAIR-12 | Base `962239521afbfec72025ab01941f89e08116ffc4`; Delivery `a2f6695bb289518db656f4d266910dccaa171207`; Handoff/tip `8738c41d7215920935e6fa067d3740e69280cdc6` | Review `a6564862649b00fd91fa4e4ea8a2f64205eb71b7` `approved` | Evidence correction slice only; this is not the final full-scope T3.2.1 Review. |

The REPAIR-12 report is in Reviewer branch `agent/deepseek/T3.2.1-review-a2f6695`,
path `verification/T3.2.1/repair-12/review-a2f6695.md`. Its approval does not
change any historical Review decision or authorize a product merge.

### O-12-2 disposition — legacy REPAIR-11 Handoff

O-12-2 identifies an obsolete, incorrect Sandbox executable hash claim in
`doc/handoffs/T3.2.1-REPAIR-11-9622395.md:31` at the preserved legacy ref
`agent/antigravity/T3.2.1-repair-11` / commit
`941dbc89e139a2e24e6b1d17c900e363995decfc`. The Handoff is historical and stays
read-only; this closeout does not rewrite it. Its claim is superseded by the
correct SHA-256 `4b6f4734415c2add670c2889b22ea107e28345ca24f4a1c86840d866b775e3e6`
recorded at `verification/T3.2.1/repair-11/build-evidence-binding.log:76` in
REPAIR-12 Delivery `a2f6695`, cross-checked against the REPAIR-9 manifest and
Sandbox run log.

**Integration disposition:** do not merge the legacy REPAIR-11 branch or import
its Handoff into the Codex candidate or `master`. The old Handoff is absent from
both current trees. If a later approved integration requires carrying that
historical document, first add a separately reviewed Codex supersession note or
corrected copy that points readers to the REPAIR-12 evidence; do not present the
old value as authoritative. The current `master` search also finds the search
needle in two REPAIR-12 Task verification instructions; these are test
instructions, not hash claims. The fixed REPAIR-12 Delivery tree and isolated
Codex candidate have no matching occurrences.

O-12-1 is also recorded for traceability: the REPAIR-12 Handoff cites the
corrected evidence as line 75, while the SHA statement is actually at line 76.
This closeout uses line 76 and preserves the reviewed Handoff unchanged.

### Gate disposition at the 2026-09-24 checkpoint (carried forward without validity judgment)

| Item | Current status |
|---|---|
| AC3 interactive main workflow | `NOT_RUN` — release blocker; do not mark `PASS`. |
| AC5 | `NOT_RUN` |
| AC6 / AC7 | `PARTIAL / NOT_RUN` |
| AC8 / AC9 | `NOT_RUN` |
| R-014–R-016 | `OPEN` |

No validity judgment or new acceptance testing was performed for these items
in that checkpoint. The full Release Gate remained open and not release ready.
No REPAIR-7/9/10/11/12 branch is merged; no merge is permitted until the full
Gate is closed and a final independent full-scope Review is approved.

### Closeout verification references

`release-gate-closeout-verification.log` records fixed-ref checks for the
candidate, current master source checkpoint, REPAIR-12 Delivery, and preserved
legacy branch. The cumulative whitespace check for `c2fcb1c..188d72a` exits 0;
the exact review/owner objects and path-only search outcomes are recorded
there. The current Codex candidate remains isolated at
`188d72a9d144b8cab16f77757abc46318ac8e5e6`; it has not been merged into `master`.

## Manual AC3 attempt — 2026-09-25 (supersedes the carried-forward NOT_RUN status)

The user manually tested fixed Build 3 in a fresh Windows Sandbox. The executable
SHA-256 was `95f9ba68086087c9999804fd0cd2bd4e5f772de350c74a22f2eaf3e329772c10`;
the GUI launched with no arguments and process exit code 0. The run did not
complete AC3: the image-import path was blocked by the QML error
`BookshelfView.qml:23: TypeError: Cannot read property 'currentChapterId' of
undefined` (31 occurrences in raw stderr). The source points the parent
`BookshelfView` at `detailArea.chapters`, although `chapters` is an internal ID
of `BookDetailPanel` and is not exposed across that component boundary. The
captured Workbench consequently has no pages.

The user also observed that button text and backgrounds are difficult to
distinguish. This is recorded as a visual finding; no contrast ratio was
measured. The Reader screenshot explicitly says no chapter is selected and its
Export control is disabled by `enabled: active`. Thus the click produced no
export action under the captured state, but the export dialog/output behavior
was not validly exercised and is not classified as an export implementation
failure.

The fixed build/source binding, six original screenshots with SHA-256 values,
process record and raw stderr are recorded in
[`manual-observations.md`](ac3-interactive-20260925/manual-observations.md).
The active status changes from `AC3=NOT_RUN` to **`AC3=BLOCKED`**: a real
interactive attempt has begun but cannot proceed until a separately authorized
QML repair is implemented, independently reviewed and retested in a fixed
package. AC3 remains a release blocker; it is not `PASS`. AC5 remains
`NOT_RUN`; AC6/AC7 remain `PARTIAL / NOT_RUN`; AC8/AC9 remain `NOT_RUN`; and
R-014–R-016 remain `OPEN`. Do not merge a related branch before the full Gate
and final independent Review close.
