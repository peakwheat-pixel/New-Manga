dsh: reasoning:
Let me start by reading the r1 report and the diff.

Let me plan: read r1 report, review-fix.diff, then the worktree files, git log, etc.

Let me start with reading key files.
dsh: reasoning:
The r1 report seems to be a leaked transcript of the previous review session. Let me read the rest of it, and also try pwsh again — the sandbox might behave differently this session. The pwsh failure "SetNamedSecurityInfoW failed (Win32 5): grantWrite" persists. Let me try a read-only command or with a different workdir. Actually maybe I should try with sandbox_permissions escalation? The instruction says approval policy ask; without answerer it fails closed. Let me just try once with danger-full-access for git commands, since git topology verification is central to this round (commit 400046ef, R9 trace).

Actually wait — my file policy is workspace-write and the failure is about granting write on G:\CODEX\New Manga (which is the workspace). Hmm, "Win32 5" = access denied. Maybe try workdir inside the workspace and see. The previous attempt had no workdir. Let me try with workdir set.

Let me first read the rest of r1 report.
dsh: reasoning:
The pwsh sandbox is failing. Let me try with sandbox_permissions escalation once (danger-full-access) to get git access — this is a static review but commit topology verification matters a lot this round (R9 trace, R7 content presence). The approval policy is "ask"; may fail closed. Let's try once.

Actually, first let me check whether there's a read-only alternative: maybe the git data can be read via the `read` tool (git internals as text files). r1 did exactly that: read reflog files. I can do the same. Let me try reading:
- G:/CODEX/New Manga/.git/worktrees/M2-IMPORT-ALLOC-LIMIT-zcode/... hmm, reflog for HEAD of worktree.

Let me first try one escalation attempt for git since it'd be very valuable, then fall back to static .git reading.

Note: I should be careful — sandbox_permissions with justification in the user's language.

Let me try both: the pwsh escalation, and in parallel read the diff file.

Actually, parallel calls in the same block: yes, I can call pwsh (escalated) and read the diff simultaneously. But if the escalated one requires approval and fails closed, fine.

Let me first check the diff size and read it in chunks. Let me try glob to see files, then read the diff.

Plan:
1. Read review-fix.diff (probably ~334 lines since +284/-50 → maybe 400 lines).
2. Read r1 report lines 623+ for the rest (findings, conditions) — useful for checking R1-R10 conditions.
3. Static git inspection via read tool of .git reflog.

Let me go.
dsh: reasoning:
No shell. So: static review only, and I must use read/glob/grep on .git text files for git facts.

Let me read the diff.
dsh: reasoning:
Interesting: dsh-review-r2.md already exists (probably the same leaked-transcript pattern — the current session's transcript being written there, or... hmm). Actually the r1 report file contained a leaked transcript of MY r1 session. Similarly dsh-review-r2.md may be my current session's transcript (being written as I go). Let me check if dsh-review-r2.md has content — it might contain a partial transcript. I should not treat it as an input. Let me peek at its size/first lines to determine.

Also I need:
1. The rest of dsh-review-r1.md (lines 623+) — the findings/conditions R1-R10 as originally named. Wait — R1-R10 in the user's prompt map to the r1 report's conditions. The r1 report I read up to line 622 appears to end mid-thought ("Findings list:") — the file may be truncated at the point where the session was cut off! Let me read from 623 to the end. Hmm, the read returned lines 1-298 then I read 299-622 and output capped. Let me read 620-end.

Actually the important thing: the R1-R10 numbering in this round's dispatch. The handoff §8 lists R1-R10 with severities: R1 P2, R2 P2, R3 P3, R4 P3, R5 P3, R6 P3, R7 P3, R8 P4, R9 P4, R10 P4. The r1 report itself may have been truncated before writing final findings (file ended at "Findings list:" line 622). Let me check the file length.

2. Read the actual worktree files:
- src/infrastructure/importing.py (R6 comment, R7 tighten position, _MobiDocumentHandle.render_page)
- tests/library/test_production_adapters.py (R1 new test, R8 assertions, fixture)
- tests/library/helpers.py (make_thin_png)
- experiments/M2-IMPORT-ALLOC-LIMIT/verify_k07.py (R2 fd2 capture)
- verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json
- verification/M2-IMPORT-ALLOC-LIMIT/pre-fix-tests-against-base-src.txt
- doc/handoffs/...a5c8adf1.md
- doc/tasks/M2-IMPORT-ALLOC-LIMIT.md

3. Git facts: read .git reflog for the worktree (to confirm 400046ef exists, its parent 02f306ea, and the R9 trace: checkout of baseline blob then restore — that wouldn't show in reflog as a commit; but the commit 400046ef's content matters). Also check `.git/logs/HEAD` of worktree and refs.

Also, importantly: the R9 trace claim "git checkout 8996ca55 -- src/infrastructure/importing.py" then "git checkout HEAD -- src/..." — the user's execution note says "R9 恢复步骤曾抹掉 R6/R7 修改（git checkout HEAD --），发现后重新应用复跑". Wait: at the time R9 was run, HEAD was 400046ef? No — R9 was performed during the return-fix work *before* committing 400046ef. Hmm, the archive file says HEAD=02f306ea + 返修工作区改动. The sequence: checkout 8996ca55 -- importing.py (overwrites worktree file with baseline), run tests, then `git checkout HEAD -- src/infrastructure/importing.py` — but HEAD at that moment was 02f306ea, which contains the a5c8adf1 version (the file as of the docs commit, i.e., WITHOUT R6/R7 changes since those were uncommitted worktree edits!). So `git checkout HEAD --` restored the file to the 02f306ea version, wiping the uncommitted R6 comment rework and R7 MOBI tightening. Then owner re-applied them. That explains the execution note. So the trace is plausible and the claim is that re-application happened. The check: does 400046ef contain R6 comment + R7 tightening? The diff review-fix.diff shows both in the final state (the diff is presumably 02f306ea→400046ef, computed after re-application). But review-fix.diff is the *provided* diff artifact; I need to confirm the worktree file content actually contains them (worktree files are the real fact). So reading src/infrastructure/importing.py in the worktree is key.

Wait, careful: the diff artifact may have been generated from the re-applied worktree *before* commit, or from the commit. Since the R9 mishap happened and was re-applied, the final commit 400046ef should contain them. I'll verify worktree file content == expected, and verify the commit exists via git files (reflog).

Let me now do reads in parallel:
- importing.py (the relevant regions: header comment ~lines 30-60, and _MobiDocumentHandle.render_page ~380-430)
- test_production_adapters.py (full, ~200 lines)
- helpers.py make_thin_png region
- verify_k07.py full
- pre-fix txt
- handoff md
- task md

That's a lot; batch them.

Let me start with importing.py + test_production_adapters.py + helpers.py + git reflog reads.

For git: the worktree's gitdir. From r1: G:/CODEX/New Manga/.git/worktrees/M2-IMPORT-ALLOC-LIMIT-zcode/HEAD and logs. Let me glob for .git/worktrees/*/HEAD? glob may have failed before for hidden dirs. r1 said glob returned nothing but read worked. Let me just read:
- G:/CODEX/New Manga/.git/worktrees/M2-IMPORT-ALLOC-LIMIT-zcode/logs/HEAD
- G:/CODEX/New Manga/.git/worktrees/M2-IMPORT-ALLOC-LIMIT-zcode/HEAD
- G:/CODEX/New Manga/.git/refs/heads/agent/zcode/M2-IMPORT-ALLOC-LIMIT (or packed-refs)

Let me batch.
dsh: reasoning:
Git facts confirmed:
- 400046ef is a real commit with parent 02f306ea, message "review-fix(M2-IMPORT-ALLOC-LIMIT): DSH r1 approved_with_conditions rework R1-R10". Branch tip = 400046ef.
- Worktree file content contains R6 comment (lines 46-54) and R7 tightening (line 418) — so the R9 mishap was indeed re-applied and committed. Good, but I should verify these are in the *commit*, not just worktree. Since branch tip = 400046ef and the file matches... but worktree could be dirty relative to 400046ef. Hmm. The final verification is whether commit 400046ef contains R6/R7. I can't run git show. But: I could check whether the worktree is dirty by comparing file mtime/hash... no shell. Alternative: read the git object? The commit object is zlib-compressed; can't decompress without shell (read tool reads text; zlib binary). Unless the repo is packed and I can't.

Hmm — can I find another artifact that shows 400046ef's content? The provided review-fix.diff is the artifact for 400046ef → it's presumably `git diff 02f306ea 400046ef` and includes both R6 and R7 hunks. That's the claim. Combined with branch tip = 400046ef (ref file) and worktree file content matching, the evidence is strong: if the worktree were dirty with uncommitted re-applications, the tip ref would still be 400046ef but the diff artifact author (owner) generated it... Circular.

Can I detect dirtiness statically? Option: `.git/worktrees/<name>/index` binary — comparing is not feasible by read.

Hmm, but there's a trick: `pwsh` unavailable. What about the git "commit-graph"? no.

Alternative: check for a `.git/worktrees/.../COMMIT_EDITMSG`? Not helpful.

Actually — maybe I can decompress zlib with pure reasoning? No.

Well: there's another approach. The loose object for 400046ef might be packed. But even if loose, I can't decompress.

I'll rely on: (a) reflog shows the commit created with that message; (b) the diff artifact generated against 02f306ea shows R6/R7 hunks; (c) worktree file matches. Dirtiness relative to HEAD is a residual NOT_VERIFIED, but I can also note that the diff artifact was produced after re-application, and there's no way for the owner to produce the diff without git working. The risk of "uncommitted re-application" (owner generated diff from dirty worktree, then didn't commit) would mean the diff artifact shows changes not in the commit — but the reflog shows 400046ef created *after* the R9 mishap (timestamp 1790864206) which is later than 02f306ea (1790862312). The R9 archive describes work at HEAD=02f306ea, i.e. before 400046ef existed. So the order is consistent: R9 ran while worktree dirty on 02f306ea, mishap wiped changes, re-applied, then committed 400046ef. Good, an internally consistent timeline.

Let me double-check timestamps:
- 1790854625 worktree checkout at 8996ca55
- 1790862023 reset moving to HEAD (hmm, at 1790862023 = the abandoned agent's reset? or the owner's?)
- 1790862214 a5c8adf1 implement
- 1790862312 02f306ea docs
- 1790864206 400046ef review-fix
Gap between docs (1790862312) and review-fix (1790864206) = 1894 s ≈ 31.6 min. That's the r1 review + rework window. Plausible.

Note: no stash reflog entries; the R9 archive explains they used checkout-blob instead of stash. Good — that resolves r1's uncertainty about the "stash" claim: the return-fix archive honestly documents the method change (git checkout 8996ca55 -- file). And the mishap (`git checkout HEAD --` wiping R6/R7) is exactly the hazard of that method — and it's disclosed in the dispatch's execution notes and the archive says "HEAD 恢复". Wait — does the archive disclose the mishap? The archive at line 493 shows `git checkout HEAD -- src/infrastructure/importing.py` — with HEAD=02f306ea, this restores the a5c8adf1 version, wiping uncommitted R6/R7 edits. The archive does NOT disclose that mishap, but the dispatch execution note does ("R9 恢复步骤曾抹掉 R6/R7 修改（git checkout HEAD --），发现后重新应用复跑"). Hmm. Is that a finding? The archive as an evidence artifact documents the command sequence faithfully (it's what was run). The fact that the sequence had a side effect on the worktree and was recovered — the final commit contains R6/R7, so the outcome is fine. But strictly, if R9's archive describes the *final* run (re-run after re-applying), then the sequence as recorded is: checkout baseline → run → checkout HEAD → (then the mishap would wipe and they'd re-apply). Since the archive says the R9 run was re-done after re-applying, the sequence is accurate for the final run. Fine. But there's a subtle ordering issue: after re-applying R6/R7 and re-running the red-state sequence, the red-state test run for R1's new test (`allocation_limit_decides_accept_or_reject`) — hold on. The red run was executed with the *baseline* importing.py but with the new tests including R1's mechanism-lock test AND R8's tightened assertion. The archive says 4 failed, 1 passed, 8 deselected — with `-k "long_strip or allocation_limit or fail_closed or truncates_very_long"`. Note `-k allocation_limit` selects: test_qt_image_decoder_raises_allocation_limit_above_qt_default, test_qt_image_decoder_allocation_limit_decides_accept_or_reject. And `long_strip` → imports_webtoon_long_strip. `fail_closed` → 1 passed. `truncates_very_long` → truncated test. Total selected 5 → 4 failed + 1 passed ✓ consistent. 8 deselected: file total = 13? Previously 12 tests + 1 new = 13. 13 - 5 = 8 ✓ consistent. 

Wait: earlier the handoff said 12 tests in the file at a5c8adf1 (4 new). Then R1 adds 1 → 13. Five suites: 522 = 521 + 1 ✓ (they said 四套件口径 522). Then 550 = 522 + 28 ✓ (import_formats 28). Consistent arithmetic. Good.

Now, the important new-content checks:

R1: test_qt_image_decoder_allocation_limit_decides_accept_or_reject:
```python
import infrastructure.importing as importing
data = make_thin_png(690, 4000)
decoded = QtImageDecoder().decode(data)
assert (decoded.width, decoded.height) == (690, 4000)
monkeypatch.setattr(importing, "_ALLOCATION_LIMIT_MIB", 1)
with pytest.raises(ImageDecodeError):
    QtImageDecoder().decode(data)
```
Key question: does `decode()` read the module global at call time? Need to see decode() implementation: `QImageReader.setAllocationLimit(_ALLOCATION_LIMIT_MIB)` — reads the module global at call time ✓ (Python resolves the global in the module's namespace at each call). So monkeypatching `importing._ALLOCATION_LIMIT_MIB = 1` works ✓.

Concern 1: the assertion is `pytest.raises(ImageDecodeError)` without checking the failure reason. With limit=1 MiB, 690×4000×4 = 11,040,000 B = 10.53 MiB > 1 MiB → Qt rejects at allocateImage → read() returns null → ImageDecodeError ✓. Since the payload is *complete and valid*, the only reason for failure is the allocation limit. So this is a genuine mechanism lock ✓✓ — addresses r1 R1 exactly as recommended (Option 2 suggested in r1).

But: is the acceptance leg (`decode` at production limit) dependent on the limit? At 2047 it passes; the *combination* (same bytes, pass at 2047 / fail at 1) isolates the limit ✓. Actually stronger: the lower-limit leg failing plus the pass at 2047 is a strict mechanism lock.

Concern 2 (new finding?): the test asserts `pytest.raises(ImageDecodeError)` but the decoder's typed error is raised only when... let's check: after read() returns null, decode raises ImageDecodeError with detail. Also `buffer` etc. Fine.

Concern 3: Does `monkeypatch.setattr(importing, "_ALLOCATION_LIMIT_MIB", 1)` interact with the autouse fixture `_restore_qt_allocation_limit`? The fixture restores the Qt global after the test (captured `before`). During the test, decode sets Qt limit to 1 → rejected; the Qt global is left at 1. Fixture teardown restores `before` ✓. Order: autouse fixture setup captures before (real), teardown runs after monkeypatch undo. Fine.

But here's a subtle real issue: within this test, the first decode sets the Qt global to 2047 (production limit). Then monkeypatch sets module constant to 1 → second decode sets global to 1 → rejected. Test ends; fixture restores to `before`. What is `before`? Depends on what earlier tests left. If a previous test in the module (e.g., the long_strip test) ran decode, global = 2047 at its teardown → fixture restored to `before` captured at that test = whatever it was. Since the fixture is autouse per-test and restores after each test, `before` for the new test = the value at its setup. For the very first test in the module, `before` = Qt default 256 (or a leaked value from another module). After the fixture teardown, global = 256 → so a *subsequent test in another module* relying on the leaked 2047... no test relies on leakage. OK: this is the pre-existing design from a5c8adf1, fine.

Hmm — wait, actually there's a potential issue with the *ordering* of the new test relative to the long_strip test. Not important.

Concern 4: R1's new test executes `QtImageDecoder().decode(data)` where data = make_thin_png(690, 4000) — a full 10.5 MiB decode, twice (once accepted, once rejected *before* allocation). Cheap. But is it marked slow? R9 said "用例①加 @pytest.mark.slow（真实 289.5 MiB 解码）" — the slow mark was added to `test_qt_image_decoder_imports_webtoon_long_strip_beyond_qt_default_cap` (line 391 in diff shows the mark added above that test) ✓ matches R9's description ("用例①"). Good.

Now the R8 assertion: `len(detail) == importing._ERROR_DETAIL_MAX_CHARS + 3`. The test's fake LongErrorReader returns a 5000-char string; `_reader_error_detail` truncates to 300 + "..." = 303 ✓. But wait: does the fake errorString return exactly 5000 "x"? Let me read the test file to check. If errorString is "x"*5000, then detail == "x"*300 + "..." → endswith("...") ✓ and len == 303 ✓. Good. Note the assertion imports the constant from the module — self-referential (if the constant were changed to 5000, the test would still pass while the *behavior* scaling... no: `_ERROR_DETAIL_MAX_CHARS` is used both by the code and the assertion, so changing the constant to 5000 would make the assertion expect 5003 and the code produce 5003 → still passes. That's a tautology risk: the test doesn't pin the value 300. Is that a finding? r1 R8 asked to tighten `<=400` to exact bound; using the module constant is reasonable (the *bound* is what matters, not the literal 300). But a regression that sets the constant to 100000 would pass the test while defeating the "bounded detail" goal. Hmm — but the intent of the constant is a single source of truth; arguably acceptable. r1's original suggestion was "assert exact bound". A hardcoded 303 would pin the value. I'd note this as a P4 nit (residual self-reference tautology) — worth mentioning but not blocking. Actually let me think: is it really a tautology? The property "detail is truncated to the configured bound + marker" is exactly what's asserted. The *choice* of bound is a separate concern (argued in the comment/rationale). So the assertion is meaningful for the truncation behavior. Only if someone changed the constant would the test silently follow — but that's by design (single source of truth). I'll mark it as P4 observation, not a condition.

R2: verify_k07.py fd2 capture. Let me scrutinize `_capture_native_stderr`:

```python
@contextmanager
def _capture_native_stderr(sink: list[str]):
    with tempfile.TemporaryFile(mode="w+b") as tmp:
        saved = os.dup(2)
        try:
            sys.stderr.flush()
            os.dup2(tmp.fileno(), 2)
            yield
        finally:
            sys.stderr.flush()
            os.dup2(saved, 2)
            os.close(saved)
        tmp.seek(0)
        sink.append(tmp.read().decode("utf-8", errors="replace").strip())
```

Issues:
1. Is the fd2 redirect reliable? Qt's categorized logging writes to stderr via `fprintf(stderr, ...)` / `write(2, ...)` — redirecting fd 2 with dup2 does capture it at OS level ✓. This is the standard approach. Caveat: on Windows, Qt's default message handler uses `fprintf(stderr)` → the C runtime's stderr FILE* still points to fd 2; since we replaced fd 2 at the OS level (dup2), writes go to the temp file ✓. The `sys.stderr.flush()` before/after handles Python-level buffering. Good.
   Caveat: on Windows, `stderr` in the CRT may be unbuffered → fine.
   Caveat: if Qt logging was configured to a different output (e.g. qt.conf or QT_LOGGING_TO_CONSOLE=0), the message might not be emitted; but the JSON contains the message, so it was captured in practice.
   Potential issue: `sys.stderr` might have been replaced/buffered such that the flush isn't enough — but the capture is at fd level and Python's sys.stderr writes also go to fd 2, which would end up in the same buffer. Minor: this means any Python-level stderr noise during the with-block also lands in `native_stderr` — but the with-block only wraps `reader.read()`, so noise is minimal. Note: if Python's sys.stderr is line-buffered/block buffered and it flushes after the restore... they flush before dup2 restore ✓. Good.

2. **The `tmp.seek(0)`/`sink.append(...)` placement is OUTSIDE the `try/finally` but INSIDE the `with tempfile.TemporaryFile(...)`** — correct: after the finally restores fd2, then seek+read. ✓ Order fine (fd2 no longer points to tmp when reading, which is fine since we read via tmp's own file object).

3. `os.dup(2)` then `os.close(saved)` in finally ✓ no fd leak.

4. But: the `finally` block restores fd2 — if the `yield` raises, the finally still restores and then the read/append is skipped (exception propagates) — acceptable.

5. A subtle Windows issue: `os.dup2` on Windows with file objects works for fds ✓ (Python supports dup2 on Windows).

6. Another subtlety: if nothing is written to fd2, `sink[0]` = "" — the code then does `case_control["native_stderr"] = native_stderr[0]`. If the capture produced empty (e.g. Qt not logging), the JSON would have "" and the verdict would still PASS (since verdict only checks rejected + positive arm). So a regression where the stderr capture breaks would NOT fail the verdict — the evidence could silently degrade to "". Hmm! That's a real (if minor) finding: the script's assertion doesn't require the native_stderr to be non-empty. r1 R2's condition was "evidence must carry the discriminating log"; the code archives it but doesn't *assert* it. Given the JSON shows the message for all three cases, the artifact is fine now. But the guard is weak: `verdict: PASS` would still hold if the message became empty. P4 (or P3?) — recommend asserting the expected substring in the verdict computation. Since r1's R2 was about the artifact carrying the evidence and the artifact does, the item is closed; the weak guard is a new P4 finding. Actually, hmm, I should consider: is it worth raising? It's a genuine robustness gap in the evidence script: the very thing r1 demanded is captured but not asserted, so a future regression silently yields empty stderr + PASS. I'll list as P4 with a concrete one-line remedy (`and "exceeds the current allocation limit" in native_stderr`).

7. Another potential issue: the positive arm at 2047 allocates the *decoded* image (345.6 MiB for K07) — in the control loop, `image_ok` stays alive until reassigned in the next iteration (it's a local; also `image` from the 256 arm). Memory: for K07, at most ~345 MiB alive; then K09's decode allocates another 264 MiB while K07's `image_ok` may still be referenced... Actually in the next iteration, `image = reader.read()` (null) and then `image_ok` is reassigned → old QImage freed. Peak = K07's 345 MiB + K09's 264 MiB temporarily = ~610 MiB. Fine. Also note the positive arm happens AFTER the production pass, so the production decode's images are freed. OK.

Wait, one more: the positive arm runs with `QImageReader.setAllocationLimit(_ALLOCATION_LIMIT_MIB)` where `_ALLOCATION_LIMIT_MIB` is imported from the production module — the script imports it (visible in the diff line 214: `"allocation_limit_mib": _ALLOCATION_LIMIT_MIB`). Need to confirm the import line exists (in the unchanged part of the script). Let me read the script head.

8. `declared_mib`: `reader.size()` returns header-declared size *before* read ✓. For K07 declared 345.6 ✓ matches JSON.

9. Also `image` variable in the rejected path is null; positive arm uses separate buffer/reader ✓ (since the first reader is exhausted/error state — good that they create a new buffer+reader).

10. env section: python/platform/pyside6/qt/allocation_limit_mib ✓ present in JSON. Note `"platform": "Windows-11-10.0.26300-SP0"` — plausible.

R3: control arm ✓ as described. `at_2047_same_reader_same_bytes` with decoded true + width/height ✓. Verdict includes it ✓. Good: this addresses r1's "two variables differ" concern by adding a raw-read pass at 2047 in the same code path ✓.

R4: mime removal: handoff §4 now says "宽高/managed ref 登记" ✓; task AC3 line says "宽高/managed ref 全登记（r1 R4：domain Page 无 mime 字段，不登记 mime）" ✓; script docstring updated ✓ (diff line 126-129). Need to check src/domain/pages/entities.py has no mime field to confirm the justification, and check no residual "mime" claim elsewhere in task/handoff. Let me grep.

Careful: the script docstring change says "(r1 R4: domain Page carries no mime field, so none is claimed here.)" ✓.

R5: topology corrected in handoff header (line 9) and task frontmatter base_commit with comment (line 98). Note: YAML frontmatter with `# comment` after value — is that valid YAML? `base_commit: 8e0de8d0 # Task 授权基线；...` — YAML comments start with ` #` and the value would parse as "8e0de8d0" ✓ valid YAML inline comment. But if any tooling parses the frontmatter strictly... it's standard YAML, fine. However, mixing Chinese text in the comment is fine.
Hmm, but one concern: does the task doc's frontmatter get machine-parsed by the project (e.g., a status tool expecting a clean hash)? Inline comments are legal YAML; a naive regex parser `^base_commit:\s*(\S+)` would still capture the hash ✓. OK.

Also the handoff header says "Task 授权基线 `8e0de8d0`；分支实际 fork 自 release `8996ca55`" ✓ accurate, and topology line `8996ca55(fork=release) → a5c8adf1 → 02f306ea → 本返修 commit` ✓ accurate. Good, R5 closed.

R6: importing.py comment updated: domain anchor with 921 MiB, 5.9x, 2.2x, "unmeasured extrapolation ... no measured source" ✓; NOT 0 reworded as bounded fail-closed ✓; MiB units unified ✓. Verify arithmetic: 690×350,000×4 = 966,000,000 B ÷ 1,048,576 = 921.2 MiB ✓ (comment says ~921 MiB ✓). 2047/921.2 = 2.222 ✓ ~2.2x ✓. 2047/345.6 = 5.92 ✓ ~5.9x ✓. Handoff §2 updated ✓ (diff line 25).

R7: `_MobiDocumentHandle.render_page` sets `QImageReader.setAllocationLimit(256)` before `QImage.loadFromData(raw)` ✓ position correct (line 418, before line 420's loadFromData). Uses 256 = Qt built-in default — hardcoded literal 256 rather than a named constant. Minor P4: magic number duplicating Qt's default; could reference a named constant or `QImageReader().allocationLimit()`... no, that would read the current global. A comment explains it ✓. Acceptable.

Does the tightening break existing MOBI tests? The claim: import_formats 28 例全绿. Static check: MOBI test images presumably small; 256 MiB bound is the previous effective bound anyway (since MOBI render happened under default 256 before this task, and under a cracked 2047 after a5c8adf1). Wait — important: before a5c8adf1, MOBI render ran at Qt default 256 (unless the global was raised by a prior import decode in the same process — which was impossible pre-fix since nothing raised it). After a5c8adf1, MOBI render could inherit 2047. R7 restores 256 → same as pre-task behavior → no test breakage expected ✓. Logically sound.

But: does a subsequent webtoon decode still work after MOBI tightened the global to 256? Yes — QtImageDecoder re-asserts 2047 before every read ✓. And is there a *within-render* issue: `render_page` sets 256 and then `image.save(buffer, "PNG")` — `image.save` writes, no allocation limit relevance ✓ (save doesn't use the reader limit).

Potential real issue: `_MobiDocumentHandle.render_page` sets the global to 256 *permanently* (doesn't restore). So after any MOBI page render, the process global is 256; webtoon decode re-asserts 2047 ✓. Also `QImage.loadFromData` for other paths (PDF?) — `_PdfiumDocumentHandle` uses pdfium (no Qt read) then `image.save`. Other Qt readers? Let me grep QImageReader/QImage.loadFromData/fromData across src to see the complete set of decode sites and confirm no other path inherits a stale 2047 or stale 256 concern. r1 did some of this. Let me grep.

Also potential concern: the MOBI tightening uses the *product* Qt default 256 but there may be legit large MOBI pages? Pre-task behavior was 256, so no regression ✓.

R8: closed as discussed; assertion uses constant (self-referential nit).

R9: archive file pre-fix-tests-against-base-src.txt — verify the provenance lines: 
- `git checkout 8996ca55 -- src/infrastructure/importing.py`
- `-c "import infrastructure.importing as m; print(m.__file__)"` → path ✓ (module resolution)
- `git diff 8996ca55 -- src/...` → exit=0, empty output → worktree == baseline blob ✓ (此即溯源: git 语义零 diff)
- `git show 8996ca55:src/... | grep -c setAllocationLimit` → 0 ✓
- red run: 4 failed, 1 passed, 8 deselected in 1.18s
- recovery: `git checkout HEAD -- src/...` + `git status --porcelain`

Note the archive's provenance: "基线 blob 写回溯源" ✓ present. r1's R9 asked for "红态归档 + 溯源行" — present ✓. However, one issue: the archive is a hand-authored text file (a transcript of commands and outputs), not raw tool output. Can't be independently validated (no machine-generated log). It's plausible and internally consistent (1.18s for the red run vs 12 passed 1.57s green — the red run is *faster*, which makes sense: 4 tests fail fast; the long_strip test at baseline rejects quickly at 256 without allocating 289 MiB ✓; the 1.18s includes creating 690×110000 thin PNG (~304 MB of zeros compression) — hmm, that should take ~1-2s by r1's estimate. 1.18s total. Plausible-ish. Note: baseline rejection happens *after* the PNG factory builds the full thin PNG (compression of ~304MB zeros). If compression alone took >1s, the total 1.18s is tight but possible. Not a finding.

Wait — actually there's something more important in the red run: the red run used `-k "long_strip or allocation_limit or fail_closed or truncates_very_long"` — 5 tests selected, and the *new R1 test* failed at baseline as expected. But careful: at baseline (importing.py from 8996ca55), does `import infrastructure.importing as importing` + `monkeypatch.setattr(importing, "_ALLOCATION_LIMIT_MIB", 1)` work? At baseline, `_ALLOCATION_LIMIT_MIB` doesn't exist → `monkeypatch.setattr` raises AttributeError (monkeypatch.setattr requires the attribute to exist unless raising=False). But the failure occurs *earlier*: the first `QtImageDecoder().decode(data)` at baseline limit 256 rejects 10.5 MiB? No wait — 690×4000 = 10.5 MiB < 256 MiB → baseline decode *succeeds*! So the first assertion `(decoded.width, decoded.height) == (690, 4000)` passes at baseline, then `monkeypatch.setattr(importing, "_ALLOCATION_LIMIT_MIB", 1)` → AttributeError since baseline has no such constant → the test fails with AttributeError (an error, counted as failed) ✓. The archive says the failure reason is "基线 decode 不断言 limit，进程全局 256 拒绝 690x4000（~10.5 MiB），「@2047 必过」腿失败 -> 红". That's WRONG: 10.5 MiB is *below* 256, so baseline decode succeeds; the red failure is due to the missing module constant (AttributeError from monkeypatch.setattr), not due to a 256 rejection. Hmm! Wait, let me re-read the archive lines 483-484:

"  - allocation_limit_decides_accept_or_reject（r1 R1 机制锁定）：基线 decode 不断言 limit，进程全局 256 拒绝 690x4000（~10.5 MiB），「@2047 必过」腿失败 -> 红。"

Two suspicious claims: (a) "进程全局 256 拒绝 690x4000（~10.5 MiB）" — FALSE, 10.5 MiB < 256 MiB so 256 does not reject it; (b) "「@2047 必过」腿失败" — the test has no "@2047 必过" leg; the leg naming is borrowed from the R3 control arm. Actually the test's legs are: production-limit accept (passes at baseline too, since baseline's effective limit is 256 and 10.5 < 256), then 1 MiB reject leg — at baseline the monkeypatch fails with AttributeError before reaching the decode.

Hold on — is the baseline global really 256? In the red run, the module fixture `_restore_qt_allocation_limit` captures `before` and restores. The process global at the start = 256 (Qt default; the red run is a fresh pytest process). The baseline code never calls the setter. But — careful — the red-state test file also includes other tests that run *before* `allocation_limit_decides_accept_or_reject` and may set the global: e.g. `test_qt_image_decoder_imports_webtoon_long_strip_beyond_qt_default_cap` explicitly calls `QImageReader.setAllocationLimit(256)` at its start (per r1's reading, line ~89) — that's baseline-friendly. And other green tests? The autouse fixture restores. So at the R1 test's start, global = 256, and baseline decode of 10.5 MiB *succeeds* ✓ (so no failure there). Then the monkeypatch raises AttributeError → test fails ✓ red for the right *kind* of reason (the fix's constant/behavior doesn't exist), but the archive's stated reason is factually incorrect.

Hmm, wait. Let me reconsider whether monkeypatch.setattr on a non-existent attribute raises. Yes: `monkeypatch.setattr(obj, name, value)` raises AttributeError("... object has no attribute ...") if the attribute doesn't exist and `raising=True` (default). So the test fails with AttributeError. Either way it's a failure, so "4 failed" stands. But the documented failure reason is wrong in two ways. Is that a meaningful finding? The red-state archive is evidence; an inaccurate failure-reason explanation misrepresents *why* the test is red. For R1's mechanism-lock claim, the important thing is the *green* behavior and the isolation of the limit; the red leg being red due to a missing constant (rather than a substantive assertion) is a weaker red signal — although it *is* genuine: the test cannot even run against baseline.

Hmm, but actually let me double check: maybe the test at baseline fails differently. `QtImageDecoder().decode(data)` at baseline: baseline `decode()` — does it raise for 10.5 MiB? No. So decoded succeeds. Then monkeypatch AttributeError. So the test is red.

Wait, is there a chance the baseline decode *does* fail because make_thin_png's output... no, it's a valid full PNG.

So the archive's "关键失败摘录" for the R1 test is inaccurate: it claims a 256-rejection of a 10.5 MiB payload (impossible) and a "@2047 必过" leg that doesn't exist. That's a real (P3) evidence-accuracy finding. The severity: P3 — the archive's overall conclusion (the new test is red on baseline) is correct, but the stated mechanism is wrong, which matters because the archive is the artifact that reviewers/integrators rely on. Also it signals the archive was written from memory rather than from actual pytest output (the raw output would show "AttributeError: <module 'infrastructure.importing'> does not have the attribute '_ALLOCATION_LIMIT_MIB'" or the assertion failure). Actually hmm — I should be careful: could the red failure be the *first* assert? Let me think once more about the baseline global at that moment. Tests in the file order: (1) ... pre-existing tests (managed copy, etc.), (2) `imports_webtoon_long_strip_beyond_qt_default_cap` (marked slow), (3) `raises_allocation_limit_above_qt_default`, (4) the new mechanism test, (5) fail_closed, (6) truncates. The `-k` selection runs 5 of them; order preserved. During the long_strip test at baseline: it sets 256 explicitly, decode does nothing (baseline), 289.5 > 256 → ImageDecodeError → test fails ✓; fixture restores global to `before` = 256. Then `raises_allocation_limit_above_qt_default`: baseline decode doesn't call the setter → calls empty → assert fails ✓ red. Fixture restores. Then the new mechanism test: global 256 → 10.5 MiB decodes fine → first assert passes → monkeypatch AttributeError → red.

So yes: my analysis holds. The archive's failure excerpt for the R1 test is wrong. Let me also check whether `make_thin_png(690, 4000)` is really ~10.5 MiB: 690×4000×4 = 11,040,000 B = 10.53 MiB ✓ (and the test comment says ~10.5 MiB ✓).

Hmm, but hold on — the fixture. Is `_restore_qt_allocation_limit` autouse for the module? Let me read the test file to confirm the fixture and the exact test body (I've only seen the diff hunks). Also check whether the new test's `monkeypatch.setattr` would be affected by an import inside decode... no.

Also — one more important check: does the *new* test pass in the green state *for the right reason*? At production limit 2047, decode of 10.5 MiB succeeds ✓. At 1 MiB, decode rejected ✓. Any chance the 1 MiB leg fails for a different reason (e.g. an exception from `_reader_error_detail`)? The decoder raises ImageDecodeError with detail "Unable to read image data" ✓. So `pytest.raises(ImageDecodeError)` matches ✓ mechanism lock genuine.

But is the *rejection* at limit=1 attributable to the limit? The payload is complete and valid, and the same bytes decoded fine moments before with only the module constant changed (and consequently the Qt global). The only difference is the limit ✓. Solid. R1 closed.

However — a subtlety: does `decode()` set the limit *before* creating the QImageReader? Yes (assert earlier). ✓.

Another subtlety for R1's isolation: `monkeypatch.setattr(importing, "_ALLOCATION_LIMIT_MIB", 1)` — but does `decode()` reference `_ALLOCATION_LIMIT_MIB` as a module global (not a default arg or a captured local)? Need to read decode() body to be sure (e.g., if it were `limit: int = _ALLOCATION_LIMIT_MIB` as a default parameter, monkeypatching the module attr wouldn't affect it). Let me read lines ~80-140 of importing.py.

R10: handoff §5 repro command now includes --out ✓ (diff line 51).

Now, additional checks I should do:
1. Read tests/library/test_production_adapters.py fully (to verify the new test body, fixture, imports, ImageDecodeError import, make_thin_png import, pytest.mark.slow registration in pytest.ini).
2. Read importing.py decode() region (lines 80-140) to verify the setter call and global lookup.
3. Read verify_k07.py head (imports of _ALLOCATION_LIMIT_MIB, argparse, --out handling).
4. grep for "mime" residuals in task/handoff/script.
5. Check pytest.ini for the slow marker registration & markers config (the diff added @pytest.mark.slow — is "slow" registered? r1 said an existing marker exists in pytest.ini).
6. Check src/domain/pages/entities.py for Page fields (R4 justification).
7. Check the full commit file list: the diff has 7 files? Let me count "diff --git" in review-fix.diff: handoff md, task md, verify_k07.py, importing.py, test_production_adapters.py, pre-fix txt, verify-k07.json = 7 ✓ (+284/−50 presumably).
8. Backflow/回潮 check: files touched are all in allowed surface (src/infrastructure/importing.py, tests/library/*, experiments/M2-IMPORT-ALLOC-LIMIT/*, verification/M2-IMPORT-ALLOC-LIMIT/*, doc/tasks/*, doc/handoffs/*) ✓ per the task's allowed list. I should verify the allowed/forbidden path list from the task doc itself.
9. Check whether the pre-existing green test `test_qt_image_decoder_fail_closed_above_limit_with_reader_error_text` still passes with R7's MOBI change and the 2047 limit — it asserts rejection of an exactly-2048 MiB declared image at 2047 ✓ unchanged.
10. Check whether R7's 256 literal could break `test_production_adapters.py`'s other tests? No MOBI render there.
11. Check import_formats tests to confirm 28 tests & MOBI path (can't run; static check that the MOBI tests exist and use small images).
12. Confirm the handoff §6 registers R7 ✓ (diff line 59).
13. Check "handoff 返修记录节" exists ✓ §8 (diff lines 67-88).
14. Also confirm the claim "五套件 550 passed+1skipped 0 failed" arithmetic: 522 + 28 = 550 ✓. And 四套件 522 = 521 + 1 (new R1 test) ✓. But wait: R9 says the file now has 13 tests; the earlier count: a5c8adf1 file had 12 (8 old + 4 new). Now 13 (8 old + 5 new). Suites: providers+core+m2_acceptance = 509; + test_production_adapters = 509+13 = 522 ✓. Then + import_formats 28 = 550 ✓. Consistent. 

Hmm, one wrinkle: is the skip counted in 550? "550 passed, 1 skipped" ✓.

Also: does the new R1 test add a *second* decode-heavy test causing the suite time to grow? It's ~10.5 MiB decode ×2, negligible ✓.

15. Another potential issue with the R1 test: `import infrastructure.importing as importing` inside the test — module import is cheap since already imported ✓. But if the test runs *before* any other module import in an isolated run (`-k`), fine.

16. Check: does `QtImageDecoder` get imported at module top of the test file from `infrastructure.importing`? Yes per r1 (lines 13-16) ✓.

17. R2's fd2 capture: check whether the script's `print()` output (Python-level, goes to sys.stderr only for errors) interferes — the `with` block only wraps read() ✓.

18. Windows note: `tempfile.TemporaryFile(mode="w+b")` on Windows returns a file that is deleted on close ✓; `os.dup2(tmp.fileno(), 2)` works with CRT fds ✓. One concern: on Windows, a C-runtime fd vs OS handle mismatch — `tmp.fileno()` is a CRT fd, and `os.dup2` handles both CRT fds and OS handles... In CPython on Windows, `os.dup2(fd, fd2)` accepts CRT fds; but Qt's native library writes to fd 2 via its own CRT (MSVC runtime). Hmm! This is a real Windows subtlety: Python (built with the UCRT) and Qt (also UCRT for PySide6 6.11) share the same CRT if both use the UCRT DLL — PySide6 wheels are built with MSVC/UCRT, and CPython 3.12 uses UCRT as well. `_dup2` in UCRT updates the process-wide fd table (which is in ucrtbase), so redirecting fd 2 affects writes from Qt's `fprintf(stderr, ...)` if Qt resolves stderr through the same UCRT fd table. Since both use ucrtbase and the fd table is per-process in the CRT, the redirect works. And the JSON proves it worked (message captured) ✓. So implementation is reliable in practice (empirically proven by the artifact). Good — I can note the empirical confirmation.

Hmm, but a caveat: if Qt logs via `OutputDebugString` or `write(2)` (not CRT), also captured ✓.

19. Now — is there a *new* problem with R3's positive arm memory? K07's positive arm allocates 345 MiB, K09 264, K10 265 — sequential, each released. Plus the production pass already decoded them → total runtime higher. Fine. But note: the positive arm's `image_ok` holds the full QImage until the next loop iteration's `image_ok = ...`, and `control` dict only stores width/height ✓ no retention. Fine.

20. The verdict now requires the positive arm ✓.

21. JSON: `"declared_mib"` present for the rejected arm; for the non-rejected case it's absent (only native_stderr) — minor asymmetry, unreachable in practice ✓ (verdict requires rejected for PASS).

22. Check `native_stderr` value equals the claim in handoff/task: "qt.gui.imageio: QImageIOHandler: Rejecting image as it exceeds the current allocation limit of 256 megabytes" — the handoff §4 quotes it *without* the "qt.gui.imageio: " prefix but says "stderr 分类日志" (categorized log) — the prefix is the category ✓ close enough; the R2 table row in handoff §8 quotes exactly "qt.gui.imageio: QImageIOHandler: Rejecting ..." with prefix? Let me check diff line 74: "实测 `qt.gui.imageio: QImageIOHandler: Rejecting image as it exceeds the current allocation limit of 256 megabytes`" ✓ exact match with JSON ✓. Task AC4 row quotes without prefix (line 112: `QImageIOHandler: Rejecting image as it exceeds the current allocation limit of 256 megabytes` 原文已按 case 归档进 JSON) — the "原文" (verbatim) label while omitting the category prefix is a minor imprecision; the JSON carries the full line. P4 nit at most. Hmm, "原文" = verbatim; the quoted substring IS a substring of the original. Acceptable. I'll mention as a nit only if space permits.

23. Does the JSON still need `qt_version`? env has qt 6.11.2 ✓ R2 closed.

24. Check that the JSON's managed_original_ref changed hashes (uuid-based) — fine, since each run regenerates refs: `7410a3a0...` → `f0bf3a2c...`. This is expected because the uuid is random per run; the evidence shows a re-run happened (consistent with the schema v2 re-run claim ✓ good corroboration that the JSON was regenerated rather than hand-edited).

Now let me also verify the claim "import_formats 28 例全绿" — static: count tests in tests/import_formats. I can grep for "def test_" counts. Let me do that.

Also verify R7's effect on tests/import_formats MOBI tests: `_MobiDocumentHandle.render_page` now sets 256 before loadFromData — MOBI fixture images are tiny ✓ no breakage.

Another check: does any *other* place in src call `QImageReader.setAllocationLimit` or rely on the global? grep.

And: does `importing.py` `QtImageDecoder.decode` still call the setter before reading (R7's claim "QtImageDecoder 每 decode 前重断言 2047")? Verify by reading lines 80-140.

Also the R6/R7 "re-applied" claim — verified via worktree content. But is the worktree dirty vs 400046ef? If the owner re-applied and committed, clean. If they re-applied *after* committing, the worktree would be dirty and the commit would lack R6/R7 — but then review-fix.diff (which the owner provided as the commit diff, presumably `git diff 02f306ea 400046ef`) would lack them. Since the diff HAS them and the diff is the review object `02f306ea→400046ef`, the commit contains them. Unless the owner generated the diff from the dirty worktree (`git diff 02f306ea`), which would show the same content even if uncommitted. Hmm. Is there any static way to distinguish? 

Idea: read `.git/worktrees/.../index` — binary, but the index contains entry mtimes and blob SHAs. Not comparable without hashing the worktree file.

Another idea: the diff header line for importing.py says `index 320ca3f9..85771fe2 100644`. The target blob SHA 85771fe2 is what the *diff* claims the post-image blob is. If I could compute the git blob SHA of the worktree file, I could compare to 85771fe2 — but that requires hashing (sha1 of "blob <len>\0" + content) — no shell. Hmm. Could the `read` + a manual sha1 be done by me mentally? No.

Alternative: check whether there's a *second* artifact referencing the commit: e.g., the task doc's delivery_head? The task frontmatter still says delivery_head: a5c8adf1 (not updated to 400046ef) — hmm, is that expected? The return-fix commit 400046ef is the review-fix; delivery_head remains the implement head. Debatable; not a finding (the handoff header says "本返修 commit" placeholder — i.e., they didn't fill in the actual hash 400046ef in the handoff header! Diff line 13: "→ `02f306ea`(docs/handoff) → 本返修 commit" — they wrote "本返修 commit" instead of the hash `400046ef`. Since the handoff is *inside* the return-fix commit, writing its own hash is impossible (self-reference) — standard practice: you can't reference the commit that contains the doc. But they could have amended... no. It's acceptable (r1's own R5 change). Note: no P-level.

Hmm, but should the *task doc* `delivery_head` be updated to 400046ef for the integrator? The task doc is inside 400046ef too. The reviewer/integrator knows the branch tip from the dispatch. Minor: I can note in the recommendation that integration should record 400046ef as the reviewed tip. Not a finding against the owner.

OK. Now, about detecting worktree dirtiness: maybe I can find `.git/worktrees/.../index` and compare its mtime with the commit time? The `read` tool doesn't expose mtime. The glob tool returns paths "in modification-time order" — useful! If I glob the worktree src files and compare ordering... crude. Hmm, actually the glob tool returns up to 100 paths in modification-time order. I could glob `src/infrastructure/*.py` and see whether importing.py is the most recently modified among them — that would indicate edits after other files, but not whether after the commit. Not conclusive.

Better idea: `pwsh` is unavailable, but is there another tool that can execute? No. What about `web_fetch` on a file:// URL? No, it's HTTP(S).

Hmm, what about reading the *packed* or loose git object for the commit with the `read` tool? The loose object for 400046ef, if loose, is at .git/objects/40/0046ef... zlib-compressed — the read tool would give garbage (binary decoded as UTF-8 → replacement chars). Can't decompress. Unless... packs. No.

So: worktree-vs-HEAD cleanliness → NOT_VERIFIED (as r1 already noted). But I have strong circumstantial evidence: the diff artifact `index 320ca3f9..85771fe2` for importing.py; the reflog commit exists with the right message; and the worktree content matches the diff's post-image *textually*. The only unverified link is whether the provided diff was computed from the commit or from the dirty tree. I can state the residual risk: if the diff was computed from a dirty worktree and the re-application was not staged/committed, the commit 400046ef could lack R6/R7 — but the reflog message and timestamp (after re-application) plus the fact that a *branch ref* points at 400046ef... Hmm, actually here's a stronger argument: the review-fix.diff's own header for the new file `pre-fix-tests-against-base-src.txt` has `index 00000000..46eb2e42` — a full-file add with a blob SHA. For the diff to contain a blob SHA for a *new* file, git had to hash the worktree file — git diff would still produce it from a dirty tree (intent-to-add? no — for an untracked file, `git diff` does NOT show it at all unless `git add -N` or the file is staged). !!! That's a key observation: `git diff 02f306ea 400046ef` shows the new file because it's *in the commit*. If the owner had generated the diff from a dirty worktree against 02f306ea, the new file `pre-fix-tests-against-base-src.txt` would NOT appear (untracked files are invisible to `git diff` without -N/staging). Unless they used `git diff --no-index`, no. So for the diff to include the new file, the file must be committed (in 400046ef) and the diff computed as a commit-to-commit (or worktree-with-staged-index... `git diff 02f306ea` compares to the *working tree* including staged changes? `git diff <commit>` compares commit to working tree, and for untracked files they're excluded; but if the file was `git add`ed (staged), then `git diff <commit>` DOES include staged content? Hmm: `git diff <commit>` = diff between commit and working tree, and the working tree for tracked/index-known paths... A newly staged file (in the index, not in the commit) — is it shown by `git diff <commit>`? Yes: `git diff HEAD` shows staged+unstaged changes for files in the index, including newly added (staged) files. So if they staged the new file but didn't commit, the diff would still show it. Hmm, so the argument isn't airtight — but combined with the reflog entry showing a commit was created with the message "review-fix ... R1-R10" at the time after the rework, and the branch ref pointing at it, the probability that the commit is incomplete is low. And they explicitly said "重新应用复跑" and the dispatch is from the owner stating the commit content. I'll mark the residual as NOT_VERIFIED with a one-line integrator check (`git diff --stat 400046ef` + `git status --porcelain` empty). That's honest.

Hmm, wait. Actually there IS one more static signal available: the *worktree's* `logs/HEAD` last entry is the commit creation. If the owner had then modified files without committing, the reflog wouldn't show it (no reset/checkout), so no signal. Right.

But here's a thought: the review-fix.diff's `index 320ca3f9..85771fe2` for importing.py — the pre-image 320ca3f9 should equal the blob in commit 02f306ea for that file, and the post-image 85771fe2 should equal the blob in 400046ef. If the provided diff were produced by `git diff 02f306ea` (worktree), the post-image line would still show 85771fe2 (git hashes the worktree content). So no distinction. Fine, NOT_VERIFIED stands.

Let me now do the remaining reads/greps in a batch:
- tests/library/test_production_adapters.py lines 1-200 (full-ish)
- importing.py lines 80-160 (decode)
- verify_k07.py lines 1-80 and 80-... (or fully, ~280 lines)
- grep "mime" in doc/tasks/M2-IMPORT-ALLOC-LIMIT.md, doc/handoffs/M2-IMPORT-ALLOC-LIMIT-a5c8adf1.md, experiments/M2-IMPORT-ALLOC-LIMIT/verify_k07.py
- grep "slow" in pytest.ini
- count tests in tests/import_formats
- grep "setAllocationLimit|loadFromData|fromData|QImageReader" in src/
- read src/domain/pages/entities.py (Page fields)
- read verification JSON + pre-fix txt in worktree (to confirm the committed/actual content matches the diff) — the JSON diff is authoritative but let me verify the worktree file exists with native_stderr.

Let me batch these efficiently. I'll do a few greps + reads.

Also need: the task doc's allowed/forbidden path list (for 回潮检查). Let me read doc/tasks/M2-IMPORT-ALLOC-LIMIT.md fully.

Let me batch now.
dsh: reasoning:
Important discovery in the test file: the `_restore_qt_allocation_limit` fixture is defined at line 70-77, i.e., AFTER the first three tests (lines 23-59) but BEFORE the M2 tests. Wait — autouse fixtures apply to all tests in the module regardless of definition position! Autouse fixture is registered at module import, and applies to every test in the module. So the first three tests also get it. Fine (r1 noted this).

Hmm, but wait: `@pytest.fixture(autouse=True)` defined at line 70 applies to tests defined *before* it in the file too (pytest collects fixtures module-wide). Yes ✓.

Now the R1 test analysis: at baseline (8996ca55), `_ALLOCATION_LIMIT_MIB` doesn't exist. So:
- line 125: `QtImageDecoder().decode(data)` — baseline decode has no setter, uses the process global. What's the global at that point in the red run? The autouse fixture captures `before` at the start of *this* test and doesn't set anything. The previous test (`raises_allocation_limit_above_qt_default`) monkeypatched the class setter → restored after. And the autouse fixture for that test restored the global to its `before`. Which is...? Let's trace from the red run start (fresh process, global = 256):
  - Many deselected tests don't run.
  - Selected order: (a) test_qt_image_decoder_imports_webtoon_long_strip_beyond_qt_default_cap, (b) raises_allocation_limit_above_qt_default, (c) allocation_limit_decides_accept_or_reject, (d) fail_closed_above_limit_with_reader_error_text, (e) truncates_very_long_reader_errors. Wait — the selection `-k "long_strip or allocation_limit or fail_closed or truncates_very_long"`: does "allocation_limit" match `test_qt_image_decoder_imports_webtoon_long_strip_beyond_qt_default_cap`? No (name has no "allocation_limit"; it has "long_strip" ✓ matched). And `test_qt_image_decoder_raises_allocation_limit_above_qt_default` ✓, `test_qt_image_decoder_allocation_limit_decides_accept_or_reject` ✓. So 3 + fail_closed (1) + truncates (1) = 5 ✓ matches "5 selected".

  Trace: (a) at baseline: sets global 256 explicitly; decode → 289.5 MiB > 256 → ImageDecodeError → test fails (FAILED) ✓; teardown: fixture restores to before=256.
  (b) baseline: monkeypatch class setter; decode → calls empty → assert fails ✓ FAILED; teardown: monkeypatch undo, fixture restores global to 256.
  (c) baseline: global 256; decode of 10.5 MiB succeeds → assert (690,4000) ✓ passes; then `monkeypatch.setattr(importing, "_ALLOCATION_LIMIT_MIB", 1)` → AttributeError (module has no attribute) → FAILED (error).
  (d) fail_closed: global 256, declared 2048 MiB > 256 → rejected → ImageDecodeError with detail "Unable to read image data" → passes ✓ PASSED.
  (e) truncates: baseline no truncation → detail 5000 chars; `detail.startswith("x"*100)` ✓ passes; `detail.endswith("...")` FAILS → FAILED ✓.

  So 4 failed, 1 passed ✓ matches the archive's counts. And the *only* passed is fail_closed ✓.

  BUT the archive's explanation for (c) is wrong: it says "进程全局 256 拒绝 690x4000（~10.5 MiB），「@2047 必过」腿失败". Two errors: (i) 10.5 MiB < 256 MiB, so no rejection; (ii) the actual failure is AttributeError from monkeypatch.setattr on a missing attribute. So the archive's failure attribution is fabricated/incorrect. The *count* and the conclusion (red) hold, but the mechanism stated is wrong. This is a genuine P3 finding on the R9 evidence artifact (it's the artifact whose accuracy is the whole point of R9, and r1's R9 condition was exactly "red-state provenance/archive").

  Also note: this means the red leg for the mechanism test isn't a substantive assertion failure — it's an error from monkeypatching a missing attribute. Is that acceptable as "red"? It does prove the baseline lacks the fix, but the *test* is not asserting anything at baseline. Debatable; I'd call it a P4 nuance (the red signal is "cannot run against baseline" rather than "assertion fails"). Actually: hmm, `monkeypatch.setattr` AttributeError counts as a test error (failed) — so it's red. Fine. But the more accurate statement is that at baseline the test errors on the missing constant. I'll fold this into the R9 finding.

Hmm, wait. Let me double check: maybe `_ALLOCATION_LIMIT_MIB` DOES exist in the baseline (8996ca55) version of importing.py! The baseline already had a partial fix? The archive says `git show 8996ca55:src/infrastructure/importing.py | grep -c "setAllocationLimit"` → `0`. But `_ALLOCATION_LIMIT_MIB` could conceivably exist without any setter usage? No — the constant was introduced by a5c8adf1 together with the setter. The archive's grep for setAllocationLimit = 0 confirms the baseline has no setter; does it have the constant? Extremely unlikely (a constant named `_ALLOCATION_LIMIT_MIB` only makes sense for the setter call). Hmm, but r1's analysis of the task doc says: "续接前 owner（熔断 agent）在 8996ca55 上已写 importing.py 修复+测试方向" — i.e., the 熔断 agent had already written the fix in the *uncommitted worktree*, but the *committed* 8996ca55 baseline doesn't have it. The red run restored the committed baseline blob → no constant ✓.

So my analysis holds: (c) fails with AttributeError. Unless... the import `import infrastructure.importing as importing` at baseline — fine.

Let me double check `monkeypatch.setattr` semantics: `monkeypatch.setattr(target, name, value, raising=True)` — "raising: if True (the default) raise AttributeError if the attribute doesn't exist". ✓ So AttributeError.

Good. Now, this is a real finding worth reporting precisely: the archive's stated failure reason for the R1 test is factually impossible (a 10.5 MiB payload cannot be rejected by a 256 MiB limit) and misnames the leg; the actual baseline failure is AttributeError at line 128. Severity: P3 (evidence accuracy), with the mitigation that the counts and the overall conclusion are correct. And, notably: the R1 test's red leg is *not* a substantive assertion failure, so the "red" evidence for R1 is weaker than the archive implies. Hmm, does that undermine R1's closure? No: R1's requirement was a mechanism-locking *green* test; the green-state isolation (pass at 2047 / reject at 1 on identical bytes) is genuine and I verified it statically. The red leg is a bonus.

Now let me reconsider whether the green isolation is airtight. Test line 125-126: decode at production limit → success. Then monkeypatch to 1 → decode → ImageDecodeError. The only change is the module constant → which `decode()` reads at line 94 at call time ✓. Confirmed: `QImageReader.setAllocationLimit(_ALLOCATION_LIMIT_MIB)` inside decode reads the module global at call time (line 94, same module) ✓. So monkeypatch works ✓. R1 closed — genuinely mechanism-locking. 

One caveat: could the 1 MiB leg fail for a reason *other* than the limit? Consider: qimageiohandler's allocateImage rejects when totalBytes > limit*1MiB. 11,040,000 > 1,048,576 ✓ → returns null → read() null → ImageDecodeError ✓. The bytes are valid (same bytes passed at 2047). So the only variable is the limit ✓ airtight.

Another caveat: is 690×4000×4 computed by Qt as the "allocation size"? PNG is RGBA8 → 4 bytes/px ✓ = 11,040,000 B = 10.53 MiB > 1 MiB ✓.

So R1: closed, well done.

R8 check: line 179-180 ✓ as analyzed. Note the assertion `len(detail) == importing._ERROR_DETAIL_MAX_CHARS + 3` uses the module constant (self-referential). Also line 147 still has `len(detail) <= 400` in the fail-closed test (not the truncation test) — that's fine (that test's detail is short).

Now, the crucial remaining check: is the R8 assertion actually satisfied in the green state? `detail = "x"*5000` → `_reader_error_detail` → `text[:300] + "..."` = 303 chars; `_ERROR_DETAIL_MAX_CHARS + 3` = 303 ✓; endswith("...") ✓. Good.

Hmm, one more: the test patches `PySide6.QtGui.QImageReader` (module attribute) with LongErrorReader. But `decode()` does `from PySide6.QtGui import QImageReader` *inside* the function → picks up the patched attribute ✓ (patch happens before decode). ✓.

Now R7's MOBI: check the *position* — line 418 `QImageReader.setAllocationLimit(256)` then line 419-420 `image = QImage(); image.loadFromData(raw)` ✓ before decode. Correct.

But hold on — a functional subtlety for R7: `_MobiDocumentHandle.render_page` sets the global to 256 and never restores. Consider the import pipeline: images import (sets 2047) → MOBI document render (sets 256) → then another *image* import (sets 2047 again ✓). Fine. But what about the *same* MOBI handle rendering multiple pages? Each page sets 256 first ✓. Fine.

Is there any other Qt decode path that might now run at 256 while expecting 2047? The webtoon path is `QtImageDecoder` which re-asserts ✓. Any other decode? Let me grep for `loadFromData|fromData|QImageReader|QImage(` in src/ to enumerate.

Also the R7 hardcoded 256: Qt's default constant. If Qt's default ever changes, the literal diverges. P4 nit. Could be `QImageReader.allocationLimit()`... no (that reads the mutated global). Acceptable; the comment says "Qt 内建 256 MiB".

Hmm, actually there's a subtle issue worth checking: does `_MobiDocumentHandle.render_page` get called in a *different thread*? The comment in importing.py says "Import runs on the application thread today". If MOBI rendering ran on a worker thread while image import ran on the app thread concurrently, the global could be raced (2047 set by the webtoon decode between MOBI's set-256 and its loadFromData). Pre-existing concurrency caveat, not new. Fine — and it's the same class of issue as before. I'll note under NOT_VERIFIED/new issues: the R7 mitigation is "best effort" under concurrency (if a future worker-thread import overlaps a MOBI render, the tighter bound can be transiently widened). Low risk today (single-threaded import). Worth a P4.

Next: verify the remaining files:
1. verify_k07.py in the worktree — confirm the fd2 capture and the `_ALLOCATION_LIMIT_MIB` import and the `--out` writing.
2. verify-k07.json in worktree (confirm native_stderr present, schema v2).
3. pre-fix-tests-against-base-src.txt in worktree (confirm content matches diff).
4. handoff md (full) — check §6/§8 and forbidden-surface claims.
5. task md (full) — allowed/forbidden paths for 回潮检查.
6. grep "mime" residuals.
7. tests/import_formats count = 28.
8. pytest.ini markers (slow registered) — else `--strict-markers` would error. Let me check pytest.ini.

Let me batch these.
dsh: reasoning:
Interesting: there are other `QImage.fromData` sites:
- src/application/export/pdf_qt.py:24
- src/infrastructure/rendering/pixel_source_style.py:55
- src/infrastructure/rendering/qt_compositor.py:41,60,61

These decode PNG bytes via QImage.fromData → QImageReader internally → subject to the process-global allocation limit. After the fix, the global could be 2047 (after any image import decode) → these paths inherit 2047 instead of 256. And after a MOBI render, it's 256. So the process-global value is non-deterministic depending on execution history — that's a pre-existing design consequence of the a5c8adf1 change (raising the global), and R7 only addressed the MOBI path. r1's R7 condition was specifically about MOBI; the owner closed it. But now I notice additional decode sites that r1 didn't enumerate (r1 mentioned `_PdfiumDocumentHandle` using QImage.loadFromData; it didn't enumerate pdf_qt.py / rendering/*). These are legacy-rendering/export paths (PySide6/QML legacy architecture per AGENTS.md), so their risk relevance is limited (the product's new architecture is Tauri/React; PySide6 code is historical evidence). Still, for completeness I should note: the process-global widening also affects `pixel_source_style` / `qt_compositor` / `pdf_qt` decode paths, which the R7 mitigation did not cover. Is this in scope? The task's allowed surface is `src/infrastructure/importing.py` only (src/ 其他面禁改?). The task says forbidden: "src/ports/**、importing.py 外 infrastructure、src/bootstrap/**、doc/contracts/**、packaging/**、apps/**、TA3-A/B experiments、doc/STATUS.md". Note "importing.py 外 infrastructure" is forbidden → so the owner could NOT touch pixel_source_style.py or qt_compositor.py (both under infrastructure/). And pdf_qt.py is under application/ — presumably outside allowed surface too.

So the correct treatment isn't to fix them but to *document* the widened envelope. Is that registered? handoff §6 registers only the MOBI tightening. So the residual: the process-global 2047 also applies to those three/four other `QImage.fromData` sites when they run after an image import. Since R7's condition was about MOBI, and the owner's fix covers the untrusted-input path (MOBI embedded images are untrusted; the rendering/export paths decode *already-managed* PNG produced by the app itself — trusted/derived data, bounded by the app's own output), the risk is lower. Actually pixel_source_style decodes "original_png" (a managed original = user-imported file, i.e. untrusted-ish!). Hmm: `pixel_source_style.py:55: image = QImage.fromData(original_png)` — this decodes the *managed original* (which is imported user content). If a user imported a malformed PNG declaring ~2 GiB, that import would now... wait, the import itself now allows up to 2047 MiB, and the decoded image is validated. Then rendering decodes the same bytes again → at 2047 → could allocate ~2 GB again. Pre-fix, both were capped at 256. So the widening affects the rendering workbench path too. But: is that path even live in the current product? Per AGENTS.md, PySide6/QML code is legacy/historical evidence, no longer released for implementation. The M2 milestone tasks are on the new architecture... but this task itself modified importing.py (PySide6-based `QtImageDecoder`) — so the legacy Python Core surface is still what's being fixed (M2-IMPORT-ALLOC-LIMIT is about the import channel). Hmm, the repo still runs these paths.

So a fair review note: the R7 hardening covered the MOBI document path; the same global-bleed argument applies to other `QImage.fromData` call sites (pdf_qt.py, pixel_source_style.py, qt_compositor.py) that were not enumerated in the rationale — but they are outside this task's allowed surface (禁改面: importing.py 之外的 infrastructure/application). So the right action is documentation/registration, not code. I'll report as P3 (回潮/论证面完整性) with the recommendation to register it in handoff §6 (a doc-only change, allowed) — or at least note that the risk is lower for app-derived data.

Hmm, careful about "回潮" (scope creep) — this isn't owner-introduced scope; it's an incompleteness of the previous rationale that r1 already partially raised and the owner addressed only for MOBI (the one site r1 named). As the r1 reviewer, I should acknowledge: I named only the MOBI site; the owner closed exactly what I asked. Now I'm discovering additional sites. Fair to report as a new P3 finding with honest attribution ("r1 未枚举完备，owner 只闭合了 r1 点名的点；本轮新发现").

Wait, but is it really a *finding* worth blocking? The verdict options are approved / changes_requested. The new findings so far:
- N1 (P3): R9 archive's stated failure mechanism for the R1 test is factually wrong (10.5 MiB cannot be rejected by 256 MiB; actual failure = AttributeError on missing `_ALLOCATION_LIMIT_MIB`).
- N2 (P3): process-global 2047 bleed to other `QImage.fromData` sites (rendering/export) not enumerated/registered; R7 covered only MOBI.
- N3 (P4): `native_stderr` capture not asserted in the verdict (empty capture still yields PASS).
- N4 (P4): R8 assertion self-referential via module constant (doesn't pin 300).
- N5 (P4): R7's 256 magic literal duplicating Qt's default.
- N6 (P4): R7 mitigation is best-effort under a hypothetical concurrent MOBI render vs webtoon decode (single-threaded today).
- N7 (P4?): handoff/task "原文" quote omits the `qt.gui.imageio:` category prefix present in JSON (nit).
- N8: Task frontmatter `base_commit: 8e0de8d0 # comment` — inline comment; if any project tooling regex-parses `^base_commit:\s*(\S+)` it still works ✓. Not a finding.
- N9: `delivery_head: a5c8adf1` not updated to 400046ef (can't self-reference; acceptable). Not a finding, but integrator note.

None of these are P0/P1/P2 blocking. R1-R10 all closed (with R9's archive having an inaccurate excerpt — does that make R9 "partial"? The deliverable asked for the red-state archive with provenance; it exists and the provenance lines are there and the counts are corroborated by my independent analysis (4 failed/1 passed is exactly what my static trace predicts). Only the "关键失败摘录" prose for one test is wrong. I'd call R9 "closed with P3 correction" — i.e., closed, with a documentation correction recommended. Per the output format I need closed/partial. I'll mark R9 "closed（附 P3 更正）" and explain. Hmm, the requested table wants closed/partial per item. I'll use "closed" + a note, or "closed*" with footnote. Let me use "closed（含 P3 更正）".

Hmm, but the dispatch says "重点：... R9 红态归档的溯源行" — the provenance lines are present and I can validate them logically:
- `git checkout 8996ca55 -- src/...` writes the baseline blob to the worktree ✓ valid method.
- `git diff 8996ca55 -- src/...` empty = worktree == baseline ✓ that's a real git-semantic equality proof (r1 asked for 溯源行; this is exactly it) ✓.
- `git show 8996ca55:... | grep -c setAllocationLimit` → 0 ✓.
- module resolution path print ✓ proves pytest imports the worktree file, not an installed copy. Good (PYTHONPATH=src).
These are good provenance lines. The "关键失败摘录" is the weak part.

Wait — one more thing to check on R9: the provenance claim "raw sha256 因 autocrlf 行尾规范化不可直接比对，以 git diff 为准" — is that right? `git diff` compares worktree→blob with autocrlf normalization applied (i.e., it compares normalized content) — so `git diff` empty means the *normalized* content equals the baseline blob; combined with the module path print, the loaded module content equals the baseline. Hmm, subtle: `git diff <commit> -- path` compares the index/worktree to the commit *after* applying clean filters (autocrlf), so "empty diff" = "the file as git would store it == baseline blob" — that's exactly the needed equality ✓. The archive's note is accurate and shows good rigor.

Now let me verify remaining items:
1. verify_k07.py rest (lines 120-287) — to confirm env/decoded_mib/control/--out implementation in the worktree (the diff shows it, but confirm the final file, plus the `_ALLOCATION_LIMIT_MIB` import line).
2. verification JSON in worktree — confirm native_stderr.
3. handoff md full (check §6 registered items, §8 table) — verify the worktree file has the返修记录 section.
4. task md full (allowed/forbidden list + AC table).
5. tests/import_formats count (28 例) — grep "def test_" count.
6. pytest.ini markers (slow registered).
7. src/domain/pages/entities.py Page fields (no mime) — R4 justification.
8. Check helpers.py make_thin_png (unchanged this round; the diff doesn't touch helpers.py — note: the diff has 7 files and does NOT include tests/library/helpers.py, correct since R1's test uses the existing make_thin_png(690,4000) signature — wait, does `make_thin_png` support a `rows` kwarg defaulting to full rows? Test line 123 `make_thin_png(690, 4000)` and line 140 `make_thin_png(8192, 65536, rows=1)`. The pre-existing helper (from a5c8adf1) has the `rows` param ✓. Need to confirm `make_thin_png(690, 4000)` produces a *complete* valid PNG with all 4000 rows → yes by default rows=height. Let me read the helper to confirm the default is the full height (critical for R1's "完整合法" claim).
9. Check that `make_png()` (used in raises_allocation_limit test) is small ✓.
10. Confirm the review-fix.diff file count = 7 and no forbidden paths (grep "diff --git" lines).

Let me batch: read helpers.py make_thin_png region, verify_k07.py 120-287, worktree JSON, handoff md, task md, and greps for import_formats count / pytest.ini.

That's a lot of tool calls; let me split into two batches.
dsh: reasoning:
helpers.make_thin_png default rows=height ✓ → R1's `make_thin_png(690, 4000)` is a complete valid PNG ✓.

verify_k07.py: imports `_ALLOCATION_LIMIT_MIB` at line 126 ✓; env at 135-141 ✓; decoded_mib ✓.

JSON confirmed in worktree ✓ matches diff ✓.

Now: the JSON no longer has a trailing newline? The diff said "\ No newline at end of file"? Actually I didn't see that marker in the diff at the end (line 592: ` "verdict": "PASS"` and "End of file - total 592 lines"). The diff for the JSON's last hunk didn't show a "\ No newline" marker in what I read (the read ended at line 592 with `"verdict": "PASS"`). The read tool reported the worktree JSON as 100 lines — no info about trailing newline. Minor, ignore.

Now read pytest.ini via the read tool (pwsh unavailable). Let me glob for pytest config, then read. Also read the handoff and task docs, and count import_formats tests, and Page entity.

Let me batch:
- read pytest.ini (guess path; if not exists, error) — better: glob "pytest.ini" and "pyproject.toml" in worktree root.
- read handoff md
- read task md
- grep import_formats test count
- read src/domain/pages/entities.py

Let me first glob for config files + read the docs.

Actually let me glob '*.ini' and '*.toml' and '*.cfg' at worktree root. The glob tool takes a path. Let me do glob pattern "*.ini" path worktree, plus "pytest.ini" reading directly.

I'll do: read G:/CODEX/New Manga.worktrees/M2-IMPORT-ALLOC-LIMIT-zcode/pytest.ini ; read handoff; read task; grep "def test_" in tests/import_formats.
dsh: reasoning:
The grep found 26 test defs but there may be parametrization (28 例). 12 in test_mobi_import.py + 14 in test_document_import.py = 26 defs; with 2 parametrized cases → 28 tests. Plausible ✓. Good enough for static; the "28 例" claim can't be exactly verified without running, note as NOT_VERIFIED (minor).

pytest.ini registers the `slow` marker ✓ (line 4). Note: `markers = slow: long-running tests (sparse 256 MiB streaming)` — the description mentions 256 MiB streaming; now also used for the 289.5 MiB decode test. Minor doc nit (P4-). Also note there's no `--strict-markers` issue ✓.

Also — important: pytest.ini has no `-m` filter by default; the slow test still runs by default (not deselected unless `-m "not slow"`). So the mark is informational only ✓ fine.

Handoff §8 exists ✓ with R1-R10 table + verification section. Good, "handoff 返修记录节" present ✓.

Handoff §5 STILL says "全量四套件（期望 521 passed, 1 skipped）" at line 63-64 — STALE! After the return fix, the four-suite expectation is 522 (521 + R1's new test). The R10 change added `--out` to the K07 command, but the pytest command's expected count wasn't updated to 522, and the "五套件 550" run isn't in §5's repro block (it's in §8). This is a documentation inconsistency: §5 says 521 while §8 says 522/550. It's the same kind of "evidence overclaim/stale" issue r1 raised. Severity: P3? It's a doc inconsistency in the repro command block — a reviewer/integrator running §5 would see 522 passed vs the documented 521 (a mismatch that could cause confusion but is trivially explained). Given the task's own R10 was about making §5's commands correct/reproducible, leaving the count stale is a partial regression of that same caliber. Wait, was the 521 in §5 correct at the time of a5c8adf1? Yes (517 baseline + 4 = 521). After the return fix added a 5th test, §5 wasn't updated. So the R10 "复现命令可复现工件" was only about --out; but the expected-count line is now wrong. I'd rate P3 (documentation/evidence accuracy, minor) or P4. Since the number directly contradicts §8 (522) and a rerun would "fail" the documented expectation, I'll call it P3- (low P3) — I'll list as P3 with easy fix.

Hmm, also note: the handoff §3 table (line 40-42) still describes the *pre-return-fix* red/green numbers (3 failed, 4/4 passed, 517→521) which is correct history for a5c8adf1 but is now superseded. §3 wasn't updated with the new red state (4 failed/1 passed, 5 tests) — but the R9 row in §8 covers it, and §8's "返修后验证" gives the new numbers. Acceptable (history vs. current). But the same staleness in §5 is a *command expectation*, more consequential. I'll note both in one finding: §5 期望值 521 过期（应为 522/550），§3 表仍是 a5c8adf1 口径（§8 已覆盖，可接受）.

Now, another check: handoff §7 "Review 指引" still mentions "基线 stash 复现命令可重放" — the method is no longer stash-based (§8/R9 uses blob checkout). Minor stale text. P4.

Now the "回潮检查" (scope): allowed surface = src/infrastructure/importing.py, tests/(import 相关), experiments/M2-IMPORT-ALLOC-LIMIT/**, verification/M2-IMPORT-ALLOC-LIMIT/**, Task/Handoff. The diff touches exactly those 7 files ✓:
1. doc/handoffs/M2-IMPORT-ALLOC-LIMIT-a5c8adf1.md ✓ Handoff
2. doc/tasks/M2-IMPORT-ALLOC-LIMIT.md ✓ Task
3. experiments/M2-IMPORT-ALLOC-LIMIT/verify_k07.py ✓
4. src/infrastructure/importing.py ✓
5. tests/library/test_production_adapters.py ✓
6. verification/M2-IMPORT-ALLOC-LIMIT/pre-fix-tests-against-base-src.txt ✓ new
7. verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json ✓
No forbidden paths ✓. Also R7 touches only importing.py (the only allowed src file) ✓ — good, since fixing other QImage.fromData sites would have violated the禁改面.

"7+ 文件" — the dispatch says 7 文件 +284/−50 ✓ matches my count of diff --git headers (7). Let me verify the +/- counts statically? I can count from the diff: not worth it exactly, but roughly: +284/−50 plausible. I could count lines starting with '+' and '-' in the diff file via grep... grep counts matches, not a sum of two patterns easily. I can grep "^\+\+\+ " etc. Eh. Let me just do a rough check: the diff is 592 lines total including headers. Not worth it. I'll note the count as consistent with the file list (can't sum precisely without shell — actually I could grep for lines starting with "+" using pattern "^\+[^+]" and count... the grep tool caps at 250 matches. Skip; declare NOT_VERIFIED for the exact +/− counts (trivial).

Now, remaining checks I should do:
(a) src/domain/pages/entities.py — confirm Page has no mime field (R4 justification).
(b) Does any doc still overclaim mime? grep showed the diff only; let me grep the worktree files for "mime" in handoff/task/script — I already read all three fully: handoff §4 line 49 "宽高/managed ref 登记" ✓ no mime; task AC3 line 47 ✓ no mime (mentions "不登记 mime" in the R4 annotation — that's a meta-reference, fine); script docstring line 17-18 ✓. Also grep in the diff showed line 76 (R4 row) and 129 (docstring) — all meta-references ✓. R4 closed. But note: task AC3 line 47 still says "尺寸/宽高登记" — AC3 in the AC list (line 28) says "尺寸/宽高登记" ✓ fine.
(c) Check Page entity quickly.
(d) Check tests/library/helpers.py make_thin_png full body to be sure `make_thin_png(690,4000)` yields a *complete* PNG (data_rows = height when rows is None ✓ from line 184). Also confirm IEND written ✓. Good enough — but let me read lines 152-215 to confirm the IDAT completes with Z_FINISH and IEND, because R1's mechanism lock depends on the payload being *complete* (if make_thin_png omitted the final bytes, the payload would be invalid and the 1-miB rejection wouldn't be attributable to the limit!). Actually: even if the PNG were truncated, the 1 MiB rejection test would still pass (truncated → fail) → the lock would be broken (same tautology as before). So I MUST verify make_thin_png produces a complete valid PNG for rows=None. Critical check. Let me read it.

If `make_thin_png(690, 4000)` is complete: then the accept leg (line 125-126) succeeding at 2047 with correct dimensions proves the payload is complete and valid ✓, which in turn makes the 1 MiB rejection attributable to the limit ✓. Actually — that's a nice self-proof: the test itself first asserts the *same bytes* decode successfully (complete valid image), so the subsequent rejection can only be the limit. So even without reading the helper, the test's logic is airtight *provided* the accept leg really decodes (which it asserts with dimensions). ✓ So R1 is closed regardless. Still, reading the helper is cheap; r1 already validated it in round 1 and it's unchanged. Skip? I'll do a quick read to be thorough about "完整合法" claim.

(e) Verify that the R1 test's 1 MiB leg isn't affected by the *previous* test leaving the global at 1 MiB: the second decode sets it to 1 (module constant) — fine; teardown restores. ✓

(f) The dispatch asks about "R7 的 MOBI 收紧位置正确性（render_page 解码前）与对既有 MOBI 测试的影响". Position ✓ verified (line 418 before 420). Impact on existing MOBI tests: the tests in tests/import_formats/test_mobi_import.py exercise `_MobiDocumentHandle.render_page`? Let me check one: test_picture_mobi_imports_one_managed_page_per_image — it likely uses a real small picture MOBI fixture → render_page → now sets 256 first → images are tiny → decodes fine ✓. Also `test_undecodable_page_image_fails_that_page` — uses a fixture with a bad image → still fails ✓. Also does any MOBI test assert the global allocation limit value afterwards? Unlikely. Let me grep test_mobi_import.py for allocationLimit to be sure → none (from the earlier repo-wide grep for setAllocationLimit|loadFromData|QImageReader|fromData in src only; let me grep the whole tests dir for allocation to see which test files touch it).

Actually r1 grep'd "allocation" in tests and found the marker + test file. Let me grep tests/ for "allocationLimit" to enumerate all test touchpoints — to check that R7's new setter doesn't break an assertion elsewhere (e.g. tests asserting the limit stays 2047 after a MOBI render, or the reverse).

(g) Also confirm that `_MobiDocumentHandle.render_page`'s new import of QImageReader doesn't create a circular/lazy-import problem: `from PySide6.QtGui import QImage, QImageReader` inside the method ✓ fine.

(h) Check whether the MOBI render path's tightening could *break* the DocumentRaster tests at 256: e.g., a picture MOBI with a large embedded image > 256 MiB would now fail — but that was the pre-a5c8adf1 behavior ✓.

Let me run these final checks:
- read helpers.py 152-215
- grep tests for "allocationLimit"
- read src/domain/pages/entities.py (or grep for "mime" in it)
- grep diff for "^diff --git" to confirm 7

Then write the review.

Also I should double check the R1 test in relation to the *fixture restore* — `monkeypatch.setattr(importing, "_ALLOCATION_LIMIT_MIB", 1)` is undone by monkeypatch teardown ✓, and the Qt global restored by the fixture ✓ (the fixture's `before` was captured at test setup = 2047 or 256 depending on prior state; either way the module constant is intact so subsequent decodes set 2047 ✓). Good.

One more potential issue with R1's test: it leaves the Qt global at 1 MiB *during* the test only; the fixture restores. But if the fixture teardown ran *before* monkeypatch teardown... it doesn't (analyzed in r1) ✓.

Hmm — actually wait. There's a subtle problem: the autouse fixture is *module-scoped*? No, function-scoped (default) ✓. Fine.

Another consideration: the new R1 test name contains "allocation_limit" — it's included in the R9 red-state `-k` selection ✓.

Now let me also consider: does the R1 test depend on the fixture at all? It mutates the Qt global via decode → yes the fixture matters for isolation ✓ present.

Let me also double check the claim "四套件 522 = 原 521 + R1 新用例". 521 was the a5c8adf1 delivery count with 4 new tests. Adding 1 → 522 ✓. And 550 = 522 + 28 ✓. And 509+13+28 = 550 ✓. Consistent ✓.

One more: the handoff §8's verification line says "五套件 ... → 550 passed, 1 skipped, 0 failed". The task doc (§ line 46, AC2) still says "四套件 517→521" (old) — the task evidence table wasn't updated with the return-fix numbers, but §8 + handoff cover it. The task's AC2 row describes the *original* delivery; R9 changed the red numbers (3 failed/4 new → now 4 failed/5 new with the archive). Should the task AC2 row be updated? It's stale relative to the return fix: AC2 says "红态 3 failed / 4 新增" and "绿态 4/4 passed ... 517→521" while the current state is 5 new tests and 522/550. This is a documentation staleness finding (P3/P4): the Task delivery evidence table reflects a5c8adf1 only, with no pointer to §8's updated numbers. Since the Task doc is the integrator-facing summary, and the dispatch explicitly mentions "五套件 550 passed" as the verification claim, the mismatch could mislead. I'll fold this with the handoff §5 stale-count finding into one P3 documentation finding: "返修后数字未同步到 handoff §5 / Task AC2 表（521 vs 522/550；3 failed/4 新增 vs 4 failed/5 新增）——只落在 §8". Actually, hmm: is it wrong to leave the task AC2 row as the a5c8adf1 historical record? The task frontmatter still says delivery_head: a5c8adf1, so the AC table describes that head; the return fix is an addendum documented in §8 (and handoff §8). Defensible. But §5 in the handoff is a *command with an expectation* and it's now wrong → that's the sharper one. I'll report §5 as P3 and the AC2 table staleness as P4 (acceptable as history, but recommend a one-line addendum).

Let me now finish the remaining verification calls.
dsh: reasoning:
Confirmed:
- make_thin_png default rows=height → complete payload (IHDR+IDAT with flush+IEND) ✓ → R1's "完整合法" claim holds ✓. Note: `b"\x00" + b"\x00"*(width*4)` = correct filter byte + RGBA row ✓. IDAT complete with compressor.flush() ✓. So `make_thin_png(690,4000)` is a valid PNG that decodes ✓ — R1's mechanism lock is airtight.
- Page entity: width, height, managed_original_ref, no mime ✓ → R4's justification is factually correct ✓.
- Only test_production_adapters.py touches allocationLimit in tests ✓ → R7's new setter in render_page can't break other test assertions about the global.
- 7 diff files, all in the allowed surface ✓.

Now let me do a final sanity check on the R7 effect on MOBI tests: which MOBI test exercises render_page with the production `_MobiDocumentHandle`? test_picture_mobi_imports_one_managed_page_per_image etc. They use small fixtures. The R7 change sets 256 → same as Qt default → no behavioral change for small images ✓. And `pytest tests/import_formats` (28 tests) reported green (owner claim; NOT_VERIFIED by me, can't run).

Hmm, one more thing to verify: does `_MobiDocumentHandle.render_page` get exercised by tests through a *monkeypatched* QImageReader? No.

Now let me check the one remaining item: whether `tests/library/helpers.py` is unchanged in this round (the diff's 7 files don't include it ✓) — correct, `make_thin_png` already had the `rows` param from a5c8adf1 ✓.

Also: the dispatch asks about "回潮检查：7+ 文件全允许面；无超范围改动". The diff's 7 files ✓. But is the *worktree* otherwise clean (untracked/modified files beyond the commit)? Can't verify without git → NOT_VERIFIED. However I can partially check for stray artifacts in the allowed verification dir: glob verification/M2-IMPORT-ALLOC-LIMIT/** and experiments/M2-IMPORT-ALLOC-LIMIT/** to see if there are extra untracked files. Hmm, glob gives files but not tracked status. Let me list the worktree's verification + experiments dirs to at least enumerate (any extra .log/.json would suggest untracked leftovers). Also list doc/handoffs to ensure only one handoff file changed. Quick glob.

Also: the R9 archive mentions `git status --porcelain # importing.py 不再出现`. Fine.

Let me also check whether there are *other* verification artifacts under verification/M2-IMPORT-ALLOC-LIMIT/ (e.g., an old json). Quick glob.

One more: I should double-check the claim in handoff §8 R7 "import_formats 28 用例全绿" and "五套件 550". Can't run → NOT_VERIFIED. But I can statically count: 26 defs with 2 parametrized = 28? Let me check parametrize usage in those two files to make the count credible. Let me grep "parametrize" in tests/import_formats. If e.g. `@pytest.mark.parametrize("fill", [...])` with 3 values appears once → 26 - 1 + 3 = 28 ✓ plausible. Let me check.

Then write the report.

Let me batch: glob verification dir, glob experiments dir, grep parametrize in tests/import_formats.

Actually also worth checking: `tests/library/test_production_adapters.py` total test count = 13 (to validate the 522 arithmetic). Let me grep "^def test_" in that file: from my read, lines 23,30,35,81,97,116,133,150,183,197,... let me count from the file (251 lines total, I read 200). Let me grep.

Let me batch 4 calls.
dsh: reasoning:
13 tests ✓ matches the arithmetic (8 pre-existing + 5 M2 tests; wait: 13 total, of which M2 tests = lines 81,97,116,133,150 = 5; pre-existing = 8 ✓). Baseline (a5c8adf1) had 12 → 8+4 ✓. 509+13 = 522 ✓; +28 (26 defs + parametrize expansion of 1 test × ? ) Let me check the parametrize at test_document_import.py:277 → `test_imported_pdf_page_keeps_the_source_colour(workspace, fill)` with `fill` parametrized — 26 defs; if that parametrize has 3 values → 26-1+3 = 28 ✓. Let me verify the number of param values quickly (lines 277-282). Minor; the 28 claim's credibility: 26 defs + 2 extra params = 28 ✓ if 3 params. Let me read those lines to be precise. Also the verification/experiments dirs contain only the expected artifacts ✓ no stray files (untracked cleanliness still NOT_VERIFIED but no leftovers in the allowed dirs).

Let me do a final read of test_document_import.py:270-285 and then write the report.

Actually, also worth verifying: are there any *other* directories/files in the worktree that the diff doesn't cover but which contain the review-relevant state? Not needed.

One more important item for the new-issues section: r1's finding about the fail-closed test (P2, tautology). R1's condition list: R1 was the mechanism-lock; the fail-closed tautology was part of R1's finding? The r1 report (leaked transcript) discussed the fail-closed test's tautology as a P2 finding and proposed Option 2 (the mechanism-lock test). The owner's R1 row says the fail-closed test "保留为 typed fail-closed 保护，其机制证明职责移交本用例" — that's exactly the right resolution: the new test locks the mechanism; the old test remains as a protective regression. So the residual: the fail-closed test still passes for the wrong reason (truncated IDAT) — but now that's *documented* in the test comment (lines 137-139) and its mechanism role is delegated. So the r1 concern is closed by design change ✓. Good.

Also, let me reconsider the severity/verdict decision once more:

Findings this round:
1. R9 archive's failure-reason excerpt for the R1 test is factually wrong (P3) — evidence-accuracy defect in the artifact added specifically to close R9. Fix: correct the two lines (10.5 MiB < 256 so baseline decodes fine; actual red = AttributeError on missing `_ALLOCATION_LIMIT_MIB` at line 128). Also then the "红态" for the mechanism test is an AttributeError, not an assertion failure — worth stating honestly.
2. handoff §5 期望值 "521 passed" stale (should be 522 for 四套件 / 550 for 五套件) (P3).
3. Process-global 2047 bleed beyond MOBI: other QImage.fromData sites (src/application/export/pdf_qt.py:24, src/infrastructure/rendering/pixel_source_style.py:55, src/infrastructure/rendering/qt_compositor.py:41,60,61) inherit 2047 and are outside the allowed surface → recommend registering in handoff §6 as a known, bounded-by-禁改面 residual (P3).
4. native_stderr capture not asserted in verdict (empty capture → PASS) (P4).
5. R7's 256 magic literal + best-effort under concurrency (P4).
6. R8 assertion self-referential via module constant (P4).
7. handoff §7 stale "基线 stash" method reference; pytest.ini slow marker description stale; task AC2 row not updated with return-fix numbers (P4, bundled).

None P0-P2. Verdict: approved (可集成). Should I say approved with the P3s as integrator follow-ups? The dispatch asks approved / changes_requested. All conditions R1-R10 are closed; the residuals are documentation-accuracy items that don't affect code correctness or evidence sufficiency (the JSON artifact carries what R2 demanded). I'll give approved, with 3 P3 documentation corrections recommended (not gating), and note that if the project requires zero-inaccurate evidence artifacts, item 1 could justify changes_requested — but I should pick one. The honest call: the code and evidence are sound; the archive's prose error is an artifact-accuracy defect but the artifact's *substantive* claims (counts, provenance, red/green split) are correct and independently corroborated by my static trace. So: approved. I'll list item 1 as the top recommendation for the integrator to fix in a follow-up doc commit (or fix it myself? I'm a reviewer; not my file... I could offer. The instructions say final answer must give a recommended next step. I'll recommend the integrator apply the 4 documentation corrections in one small commit, then integrate).

Hmm, one consideration: should the P3 stale count in §5 be considered a "conditional" that blocks? The r1 round's conditions were R1-R10; all closed. New findings are documentation-only. Approving is right, with explicit follow-ups. I'll be clear that approved ≠ zero-issues.

Now let me also double check one technical claim I want to make about R2's fd2 capture reliability — I should state the caveats honestly:
- `os.dup2(tmp.fileno(), 2)` at the OS/CRT fd level captures writes from the native Qt layer on Windows provided Python and Qt share the same CRT fd table (both UCRT with CPython 3.12 + PySide6 6.11) — empirically confirmed by the archived line in all three cases ✓.
- Caveats: (i) any Python-level stderr writes inside the with-block also land in the buffer (only `reader.read()` is wrapped → negligible); (ii) if Qt's logging rules suppress the category message, `sink[0]` would be "" and the verdict would still PASS (item 4); (iii) the redirect is not thread-safe — if another thread writes to fd 2 after the restore... actually writes during the window from another thread would land in the temp file; in this single-threaded script, fine.
- Also: `sys.stderr.flush()` only flushes Python's buffer; the CRT's own stderr FILE* buffer used by Qt isn't flushed — if Qt buffered the message in its CRT buffer, it would be flushed later (after the fd is restored) and land on the real stderr instead of the temp file. Hmm! That's a genuine subtlety: Qt uses `fprintf(stderr, ...)` (or qWinLogMessage). If the CRT's stderr is unbuffered (default for stderr when attached to a console: unbuffered? In MSVC, stderr is unbuffered by default — `_IONBF`), writes go straight to the fd → captured ✓. But if the process's stderr is *not* a console (redirected), MSVC's stderr is still unbuffered by default (stderr is always unbuffered unless setvbuf is called). So capture is reliable ✓, and empirically proven. I'll mention the buffering theory as the residual caveat with the empirical confirmation.

Now, one more possible check: does the JSON's three identical native_stderr lines show that the capture is per-case (not accumulated/global)? Each has exactly one line ✓ per-case capture works ✓. Good; also proves no duplicate cross-contamination (capture starts fresh bool per iteration ✓ `native_stderr: list[str] = []` inside the loop ✓).

Hmm, one bug-ish detail: `_capture_native_stderr` appends to the passed list; the code passes `native_stderr` (fresh per case) ✓. Then `case_control["native_stderr"] = native_stderr[0]` — if the list were empty (exception path) it'd IndexError; but the append always happens on normal exit ✓ (unless the read raises). Fine.

Wait — one more: in the *else* branch (unexpectedly decoded at 256), `native_stderr[0]` is also used — the append always happened ✓.

Now let me also verify the R2 claim "OS 级 fd2 捕获 ... 实测" wording in handoff §8 R2: yes ✓.

And the handoff §4 sentence: "该日志原文已按 case 以 OS 级 fd2 捕获归档进 JSON ... JSON 另含 env 段（python/platform/pyside6/qt）与 per-case decoded MiB / 对照臂 header-declared MiB" ✓ all verified present in JSON ✓. Good — the R2 overclaim from r1 is genuinely fixed (not just re-worded) ✓.

Let me do the last read (parametrize count) and then compose the final report. Actually, the parametrize detail is minor; but the "28 例" claim is part of the owner's verification claim. Let me read lines 270-285 of test_document_import.py quickly.

Also I realize I should double check whether the R1 new test is included in the "四套件 522" — yes.

Let me also think about whether there's any issue with the new test *ordering vs. the slow marker*: `-m "not slow"` would deselect only the long_strip test; the mechanism test isn't slow ✓ (fast).

One more potential issue I should flag or dismiss: the R1 test decodes 10.5 MiB twice — but the *second* decode at limit=1 is rejected *before* allocation, so memory is fine ✓.

OK. Let me read the parametrize block and then write.
dsh: reasoning:
parametrize with 3 values → 26 defs - 1 + 3 = 28 ✓ the "import_formats 28 例" claim is arithmetically consistent ✓.

verify_k07.py: everything confirmed. Note the `--out` writes with `ensure_ascii=False, indent=2` ✓ and the file has no trailing newline (write_text of json.dumps... json.dumps doesn't append "\n") — the diff didn't show "\ No newline at end of file" for the JSON... hmm, actually the old JSON at a5c8adf1 was also written by the same code → also no trailing newline. The diff would show `\ No newline at end of file` markers if the file lacks a final newline. In the diff I read, at line 591-592 the hunk ends with ` "verdict": "PASS"` and no "\ No newline" marker visible. Let me check: my read of the diff ended at line 592 = `   "verdict": "PASS"`. There was no marker line. Hmm, for a file without a trailing newline, git diff shows a `\ No newline at end of file` line after the last content line. Its absence suggests the file DOES end with a newline. But json.dumps + write_text doesn't add one... unless the pre-existing JSON file at a5c8adf1 was created by the same script → also no trailing newline → the diff would show the marker. Since the read tool didn't show it and reported the file as 592 lines total... Possibly the marker exists but my read output truncated it? The read said "(End of file - total 592 lines)" and the last line content was `   "verdict": "PASS"`. If there were a marker, it'd be line 593. Hmm, "total 592 lines" — so no marker. Then the JSON ends with a newline. Maybe an editor added it. Not important. Skip.

Wait, actually one detail in the diff I should double check — in the diff hunk at the end, after line 591 `   "verdict": "PASS"` there might be a `\ No newline at end of file` that the read tool trimmed as an empty/garbled line. Irrelevant to the verdict.

Now, let me reconsider one potential *substantive* issue with the R2 fd2 capture that I should verify more carefully: the `native_stderr` in the JSON contains ONLY the Qt line — no Python-level noise. Good.

But here's a thought: the control loop sets the limit to 256 and reads; then the positive arm at 2047 — does the positive arm's *successful* decode also emit a Qt categorized log ("qt.imageio: ...")? No, and the positive arm is outside the capture context anyway. Fine.

Another important check: in the positive arm, does `reader_ok.read()` at 2047 for K07 allocate 345 MiB? Yes. That's the point ✓ and it's the "same reader read of the same bytes" ✓.

Now — one more consideration regarding R3's claim "限值唯一变量": within the control pass, the 256 arm and the 2047 arm use *different* QImageReader/QBuffer instances but identical construction; the only changed variable is the limit ✓ correct.

OK, I have everything. Let me also consider the r1 report's remaining tail (lines 623+) to make sure I've matched the R1-R10 numbering exactly with r1's own conditions. The handoff §8 table lists R1-R10; the user's dispatch lists them too. The r1 report file appears to end mid-writing (line 622 "Findings list:"). Let me read the tail to see if the findings were written (maybe the file continues beyond 622 with the final report). The read at offset 299 limit 400 returned up to 622 and said output capped; total file lines unknown. Let me read from 620 to end to check, in case r1's conditions differ from the dispatch's summary (e.g., numbering). It matters for accuracy of my per-item table. Let me read it.

Actually the dispatch itself enumerates R1-R10 (the owner's §8 table matches: R1 mechanism lock, R2 evidence, R3 control arm, R4 mime, R5 topology, R6 MiB, R7 MOBI, R8 truncation assertion, R9 red archive, R10 --out). And the leaked transcript's analysis matches those (R1=fail-closed tautology/mechanism lock; R2=stderr not in JSON; R3=control two-variable; R4=mime overclaim; R5=topology; R6=MiB unit; R7=MOBI global bleed; R8=≤400 loose; R9=red-state not archived; R10=--out missing). ✓ consistent. But note r1's analysis said R1 was P2 "test does not lock the mechanism" ✓ matches.

Let me quickly read the tail of dsh-review-r1.md to see the final verdict/findings list (lines 620-700) — useful to confirm severities and whether r1's conditions match. Let me do that. If the file ends at 622, fine.

Then write the final answer.

Actually, the file is called dsh-review-r1.md and contains the transcript; the actual final report might be there after line 622. Let me read from 620 with limit 200.
dsh: reasoning:
The r1 report file contains the full r1 review (transcript + final report). R1-R10 numbering matches. Good — my per-item table aligns with the dispatch.

Interesting extra fact from r1's later analysis: there's a TASK-043 precedent for the red-state archive file name `verification/TASK-043/pre-fix-tests-against-base-src.txt` — and the owner used exactly that name/format for this task ✓ (R9 closed with the repo's established format). That strengthens my assessment that R9's artifact format matches convention; only the failure-reason prose for one test is wrong.

Hmm, let me check the TASK-043 precedent file to see whether the convention includes raw pytest output — if the precedent also includes a curated "关键失败摘录", then the accuracy of that prose matters even more. Let me read verification/TASK-043/pre-fix-tests-against-base-src.txt in the worktree (or main repo) and compare formats. This could strengthen or weaken my R9 finding. Quick read.

Also, r1 mentioned tests/core/test_core_assembly.py:241 imports QtImageDecoder — it's in the four-suite run set ✓.

Let me read the TASK-043 precedent file. Path: G:/CODEX/New Manga/verification/TASK-043/pre-fix-tests-against-base-src.txt (main repo) or worktree. Let me glob to find it.

Then I'll write the final report. I have enough facts.

Actually, one more thing worth verifying for my new P3 finding #2 (global bleed to other QImage.fromData sites): are those sites reachable in the same process after an image import? 
- src/application/export/pdf_qt.py:24 — PDF export path (application layer) — reachable in the same process ✓.
- src/infrastructure/rendering/pixel_source_style.py:55 and qt_compositor.py:41,60,61 — rendering/compositing → reachable when rendering a page after importing ✓ (same process, later in time). So yes, the widened 2047 applies there. Note these are legacy PySide6 paths, and the decoded bytes there are app-managed originals (same trust class as the import). I'll frame it as: the widened envelope is process-wide and covers these sites too; R7 covered only the MOBI (untrusted) path; the others decode app-derived/managed originals, so risk is lower, but the rationale/registration should enumerate them (documentation-only, since they're in the禁改面). P3.

Let me quickly confirm those files' context (are they legacy/active?) — not critical; the grep gave line numbers. And `src/application/export/pdf_qt.py` — in application/ layer (禁改面 as "其他 infrastructure 文件"... actually pdf_qt.py is in application/, not listed explicitly in the allowed/forbidden list; the allowed list only includes importing.py + tests + experiments + verification + docs, so application/ files are outside the allowed surface → 禁改 by implication). Fine.

Let me read the TASK-043 precedent then write.
dsh: reasoning:
The TASK-043 precedent archive contains **raw pytest output** (full failure tracebacks + summary), plus tree provenance lines. That's the repo convention: raw output, not a hand-curated summary. The M2-IMPORT-ALLOC-LIMIT R9 archive contains only a curated summary with the `-q -rs -rf` last-4-lines and a *authored* "关键失败摘录" — and that authored excerpt is wrong for one test. This strengthens my finding:

1. The archive deviates from the repo precedent (raw failure output archived, which would have made the failure reasons unambiguous).
2. The authored excerpt is factually wrong for the R1 test.

So R9 → I'd say "closed（but evidence-quality deviation, P3）". Given the repo precedent explicitly includes raw tracebacks, and the archive's excerpt misstates the failure mechanism, my recommendation: append the raw pytest failure lines (or correct the excerpt). This is a documentation/evidence-quality fix, not code.

Hmm, does this rise to changes_requested? Let me weigh. The core review question set: R1-R10 closed? R9's deliverable (archived red-state evidence with provenance) *is* present with the key provenance lines and correct counts; one excerpt line is wrong. Given the whole point of R9 was evidence quality (it was itself a P4 for missing archive), shipping an archive with an incorrect failure reason in it is exactly the class of defect r1 was closing (evidence accuracy). However: it doesn't affect the code, doesn't affect the substantive conclusion (red on baseline: confirmed true), and the counts are corroborated by my independent static trace. Two options:
- approved + recommend a doc fixup (my inclination),
- approved_with_conditions/changes_requested for the excerpt fix.

The dispatch asks for approved / changes_requested (binary). Note the previous round was approved_with_conditions, and the owner has now closed all 10. If I now issue changes_requested for a prose line in an evidence file + a stale count, that's defensible but arguably harsh... Yet the project's standard (per r1's own R2 finding, "证据声明超出工件" was treated as a P2 condition) is strict about evidence artifacts. The R9 excerpt is an *inaccurate claim about a test result* — the same species as R2 (which was P2 and a condition). Hmm. But magnitude: R2 was a claim that evidence existed when it didn't (AC4/F2 caliber upgrade depended on it). R9's excerpt is an explanation of an already-correct count, in a supporting archive, with the raw command recorded. The substantive evidence (4 failed/1 passed, provenance) is intact and correct.

I'll go with **approved（可集成）** and list the R9 excerpt as P3 "集成前建议修正" — but hmm, if I say approved, the integrator may ignore. I can make the recommendation explicit and low-cost: "集成 commit 时顺带修正（1 行）". The instruction says verdict must be approved/changes_requested. I'll choose approved, with 3 non-gating P3 documentation corrections and explicit wording that I recommend applying them in the integration commit (doc-only, no re-review of code needed). That's honest and proportionate: no code defect, no evidence *absence*, no unverifiable claim blocking integration.

Hmm, let me reconsider once more the severity of the R9 excerpt error. Is my analysis definitely right that the R1 test at baseline fails with AttributeError rather than a 256-rejection? Let me re-verify `make_thin_png(690, 4000)` decoded size: 690*4000*4 = 11,040,000 bytes = 10.53 MiB. Qt limit 256 MiB → no rejection ✓. And the test's first decode at baseline: `QtImageDecoder().decode(data)` — baseline decode has no setter, so the process global applies. If the global were still 256 → decode succeeds → assert passes → then monkeypatch AttributeError. But wait: what if the global at that moment were... hmm, could the global be *lower* than 10.5 MiB? No (only 256 or values set by earlier tests: the long_strip test sets 256; the fixture restores). Could the global be 0? No.

So the baseline failure is definitely not a 256-based rejection. Unless... hmm, one alternative: at baseline, `import infrastructure.importing as importing` then `monkeypatch.setattr(importing, "_ALLOCATION_LIMIT_MIB", 1)` — if `monkeypatch.setattr` with raising=True raises AttributeError, pytest reports the test as failed (error) ✓. The archive's "关键失败摘录" says the failure is a 256-rejection + "「@2047 必过」腿失败". Both wrong. Yes, confirmed.

Hmm, although — wait. Let me reconsider: maybe the baseline (8996ca55) *does* have `_ALLOCATION_LIMIT_MIB`! What if the 熔断 agent's work was partially committed at 8996ca55? The archive's `git show 8996ca55:... | grep -c "setAllocationLimit"` = 0 → no *setter* usage, but the constant could exist unused? Improbable... but what if the constant existed in the baseline (e.g., the 熔断 agent had committed an early version with just the constant)? Then monkeypatch would succeed, and the decode at limit=1 would... baseline decode doesn't call the setter, so the global stays 256 → the decode of 10.5 MiB succeeds → `pytest.raises(ImageDecodeError)` fails with "DID NOT RAISE" → still red, but again NOT for the reason stated ("256 拒绝 690x4000" would still be false). So either way the archive's excerpt is wrong. Good — my finding is robust to that uncertainty. I'll phrase it accordingly: regardless of whether the constant existed in the baseline, the stated reason ("256 上限拒绝 690×4000≈10.5MiB") is impossible.

Let me also check r1's mention: "decode() calls the setter before constructing the reader" and the task doc line 22 says "src/infrastructure/importing.py:45-59 是唯一 QImageReader 使用点，无 allocation limit 设置点" — at the *Task-authoring* baseline (8e0de8d0) there was no setting point. And 8996ca55 is a doc-only release commit. So the baseline has no constant ✓. Then monkeypatch AttributeError. Fine.

Now also: the archive line 44-45 says for the truncation test "基线 5000 字符 detail 不截断，endswith("...") 失败" ✓ correct. Line 42-43 correct ✓. Line 46-47 correct ✓. Only the R1 line is wrong.

One more consideration: the archive says "5 个新用例 -q -rs -rf" in handoff §8 R9 — but the -k expression selects 5 tests (4 new M2 tests + the R1 new one = 5 new) ✓ correct.

Alright. Now, another item I should double check for completeness: the dispatch says "R9 恢复步骤曾抹掉 R6/R7 修改（git checkout HEAD --），发现后重新应用复跑". I verified R6/R7 are present in the worktree and in the provided diff. The residual is whether they're in the commit (NOT_VERIFIED for the commit object itself, though the evidence strongly suggests yes). I'll be explicit about the evidence chain and the one residual check for the integrator (`git diff 400046ef -- src/infrastructure/importing.py` should be empty / `git status --porcelain` empty).

Let me also verify the diff's line-count claim +284/−50 approximately by grepping... skip; declare NOT_VERIFIED (trivial).

One last check I want: does the help of the R2 env section include `allocation_limit_mib` twice (top-level env + per-case "allocation_limit_mib": 2047 in the pre-existing part at lines 9,26,43 of JSON)? Yes, per-case entries already had `allocation_limit_mib` from schema v1 (unchanged) — fine, redundant but harmless.

Also the JSON has no `timestamp` — minor; skip.

Now let me also double check one thing about R7 that could be a *real* issue: the R7 tightening means that when `_MobiDocumentHandle.render_page` runs, it sets the global to 256. Then `image.save(buffer, "PNG")` — no reader involvement. But what if the *same process* later decodes a webtoon image via a path that does NOT go through QtImageDecoder (e.g., `QImage.fromData` in qt_compositor) — it'd get 256 (after a MOBI render) or 2047 (after an image import) — non-deterministic. This is the same N2 finding's flip side: the global is now history-dependent, so other decode sites get either 256 or 2047 depending on the last import/render. I'll state this crisply in N2 (the envelope for non-covered sites is now non-deterministic: 256 or 2047). That's a good, precise way to put it. And the mitigation options are outside the allowed surface → register in handoff §6 / a follow-up Task.

Hmm, is that a *new* problem introduced by R7? Before R7 (a5c8adf1), those sites were 256 or 2047 too (2047 after an image import). R7 makes MOBI render *lower* it, so after a MOBI render the other sites get 256 (the pre-task behavior). So R7 doesn't worsen it; the non-determinism pre-exists from a5c8adf1's global raise. So N2 = "the a5c8adf1 global raise affects all in-process decode sites; R7 covers only MOBI (the one r1 named); the rest remain unregistered". Right.

Now let me write the final report. Structure:

## Verdict
approved（可集成）— 0×P0/P1/P2 新发现；R1-R10 全部 closed；3×P3 文档级校正（不阻塞）+ 4×P4。附条件式建议：集成 commit 顺带修正（无需重审代码）。

## R1-R10 逐条复核表
Table with columns: # | r1 级别 | 处置判定 | 证据落点（文件:行） | 复核要点

R1 closed — tests/library/test_production_adapters.py:116-130; mechanism lock verified: make_thin_png(690,4000) full payload (helpers.py:152-201, data_rows=height, IEND present), accept at production limit with dims assert, then monkeypatch `importing._ALLOCATION_LIMIT_MIB=1` → same bytes rejected; decode() reads the module global at call time (importing.py:94) → isolation airtight. Note: monkeypatch.setattr requires the attr to exist (green state ✓).
R2 closed — verify_k07.py:91-111 (_capture_native_stderr), 133-141 (env), 180-185 (decoded_mib), 218-228 (declared_mib); JSON:57-63 env, :69/:80/:91 native_stderr, :20/:37/:54 decoded_mib, schema_version 2 ✓. fd2 dup2 reliability: OS-level dup2 on the shared UCRT fd table; Python-side flush before redirect and before restore; empirically confirmed by per-case single-line captures. Caveat: not asserted in verdict (P4).
R3 closed — verify_k07.py:237-259 positive arm; verdict includes it (:268-274); JSON :70-74, :81-85, :92-96 decoded true with dims.
R4 closed — Page entity has only width/height/managed_original_ref (src/domain/pages/entities.py:26-28, no mime); wording removed in handoff:49, task:47 with R4 note, script:17-18; diff residual mentions are meta-only.
R5 closed — handoff:3,:5; task:12 (inline YAML comment, still parses).
R6 closed — importing.py:46-54 (921 MiB, 5.9×/2.2×, "no measured source"), handoff:29; arithmetic verified: 966e6/1048576=921.2 MiB, 2047/921.2=2.22, 2047/345.57=5.92.
R7 closed — importing.py:410-418 (setAllocationLimit(256) before loadFromData at :420); only tests/library/test_production_adapters.py touches allocationLimit in tests → no assertion conflicts; MOBI fixture images are small → behavior identical to pre-task default; import_formats 28 (26 defs + 3-way parametrize = 28 ✓).
R8 closed — test:179-180 (endswith + == MAX+3) ✓; P4: self-referential constant.
R9 closed（含 P3 更正）— pre-fix-tests...txt:13-24 provenance (checkout blob + `git diff 8996ca55` empty + grep=0 + module path print) ✓; :32-37 raw summary 4 failed/1 passed/8 deselected — my independent static trace reproduces exactly this split ✓; BUT :40-41 excerpt wrong (10.5 MiB < 256 → not a 256 rejection; actual baseline failure = AttributeError on missing `_ALLOCATION_LIMIT_MIB` at test:128). Also deviates from repo precedent (verification/TASK-043/pre-fix-tests-against-base-src.txt archives raw tracebacks).
R10 closed — handoff:67 --out ✓; but handoff:63-64 expectation still 521 (stale, P3).

## 回潮与新问题
- 7 files all in allowed surface, no forbidden path; only src file = importing.py ✓ (R7 fix correctly stayed inside the allowed file).
- Worktree content vs commit: verified R6/R7 present in worktree; reflog chain 8996ca55→a5c8adf1→02f306ea→400046ef at .git/worktrees/.../logs/HEAD:1-6 with the review-fix message; branch ref = 400046ef. R9 mishap trace consistent with the archive's HEAD=02f306ea basis; re-application landed (worktree + diff both carry R6/R7).
- New findings N1-N7 with severities.
- handoff §8 returns-fix section present ✓ (§8 table + 返修后验证).

## NOT_VERIFIED
1. 实跑数字（550/522/517、import_formats 28）— 无 shell。
2. worktree 相对 400046ef 是否干净（porcelain）— 无 shell；间接证据充分。
3. commit 400046ef 内容是否与 review-fix.diff 完全一致（diff 可能由脏工作区生成）— 需 `git status`/`git diff 400046ef`。
4. `git diff --check`、+284/−50 精确。
5. K07 资产 sha256 与 TA3-B2 记录一致性（无 sha256sum）。
6. R7 对 MOBI 的运行时影响（Qt 全局在所有 QImage.fromData 站点生效的运行时确认）。
7. fd2 捕获在目标机的可重复性（本次仅有已归档工件，未复跑）。

## 推荐下一步
One sentence: 集成方在 worktree 跑 `git status --porcelain` + 五套件确认 550 passed 后，用同一 commit 顺带修正 3 处 P3 文档（R9 摘录、handoff §5 期望值 521→522/550、§6 登记非 MOBI 解码面），即可把 400046ef 合入并把 Task 置 done；无需重审代码。

Let me make sure I give file:line for everything, and mention the R1/R2 focus items the dispatch asked. Also the dispatch asked to check "R1 用例是否真正锁定机制（limit=1 必拒+默认必过的同输入对照）" — answered ✓.

I should also mention explicitly: r1's P2 fail-closed tautology: resolved by design (mechanism proof delegated to the new test; the old test remains as a documented protective regression) — I should state that the fail-closed test still cannot distinguish truncation from limit rejection (unchanged), but its role is now explicitly documented (test comment :137-139 + handoff §8 R1). So no new condition.

Length: keep it organized and dense but not bloated. Chinese output.

One more precision: for R2's fd2 reliability, mention the concrete mechanics: `os.dup2(tmp.fileno(), 2)` + `sys.stderr.flush()` before/after; Qt's categorized logging goes to the CRT/OS fd 2 in the same UCRT fd table as CPython 3.12 → captured; the archived per-case lines prove it empirically. Residual: writes from other threads during the window would also be captured (none here); no assertion that the capture is non-empty (P4).

Also note the JSON's identical 3 lines and that the capture list is fresh per case (verify_k07.py:212) → no cross-case contamination ✓.

Also mention: verdict PASS requires rejected + positive arm decoded, but not native_stderr non-empty (N3).

Let me write it. I'll use a table for R1-R10. Also include the file:line references. For the diff file, cite `review-fix.diff:NN`.

Also for handoff line numbers, I read the worktree file (103 lines) so I can cite handoff:NN accurately ✓. For the task doc (50 lines) ✓. For verify_k07.py (287 lines) ✓. For tests (251 lines, I read to 200 but grep gave line numbers) ✓. For importing.py (453) ✓. For the archive txt (51) ✓. For the JSON (100) ✓.

Write now.
静态复核完成（该沙箱无 shell：`SetNamedSecurityInfoW failed (Win32 5)`，升级通道无审批者，故 git/pytest 实跑均以 `.git` 文本与源码静态取证替代）。以下为 r2 定点复核结论。

## Verdict

**approved（可集成）** — 0×P0/P1/P2 新发现；r1 的 R1–R10 **全部 closed**（R9 附一处 P3 证据文字更正）。代码与证据工件经静态独立复核成立：`importing.py:94/418`、`tests/library/test_production_adapters.py:116-130`、`verify_k07.py:91-111/237-259`、`verify-k07.json`（schema v2）、`pre-fix-tests-against-base-src.txt` 均与 owner 声称一致，且 commit 拓扑 400046ef 经 reflog 证实。新发现仅 3×P3 + 4×P4，全部为文档/证据文字级，不触碰实现与证据充分性。

## R1-R10 逐条复核表

| # | r1 级别 | 判定 | 落点（文件:行） | 复核要点 |
|---|---|---|---|---|
| R1 | P2 | **closed** | `tests/library/test_production_adapters.py:116-130`；`helpers.py:152-201`；`importing.py:94` | 机制锁定**真成立**：`make_thin_png(690,4000)` 默认 `rows=None→height`（helpers:184）且含 IDAT `flush()`+IEND（:193-201）＝**完整合法**载入（10.53 MiB）；先在同一输入上以生产 limit 断言成功（:125-126 且校验宽高），再 `monkeypatch.setattr(importing,"_ALLOCATION_LIMIT_MIB",1)` 同字节必拒（:128-130）。`decode()` 在**调用时**读取模块全局（`importing.py:94` 直接引用 `_ALLOCATION_LIMIT_MIB`），故 monkeypatch 生效，对照臂唯一变量＝limit，非截断/非其他失败模式 → r1「不锁定机制」条件实质闭合。原 fail-closed 用例（:133-147，rows=1 截断）保留为保护性回归、其机制职责已显式移交（:137-139 注释 + handoff:88），不再要求它区分限值拒绝与截断失败 |
| R2 | P2 | **closed** | `verify_k07.py:91-111`（fd2 捕获）、`:133-141`（env）、`:180-185`（decoded_mib）、`:218-228`（declared_mib）；`verify-k07.json:57-63,69,70-74,80,91` | 工件**真的**含证据，非文字降级：三例 `native_stderr` 原文＝`qt.gui.imageio: QImageIOHandler: Rejecting image as it exceeds the current allocation limit of 256 megabytes`，与 handoff:89 引用逐字一致；env（python 3.12.3/Windows-11/PySide6 6.11.2/Qt 6.11.2/limit 2047）、per-case `decoded_mib`(345.6/264.5/265.0)、`declared_mib`、`schema_version:2` 齐备。fd2 捕获实现可靠：`os.dup(2)`→`os.dup2(tmp.fileno(),2)`、切前/切后 `sys.stderr.flush()`、`finally` 恢复并 `close(saved)`（无 fd 泄漏），读取放在恢复之后；Qt 分类日志走 UCRT/OS fd 2，与 CPython 3.12 同 fd 表 → 被捕获；`native_stderr` 列表按 case 新建（:212），三例各仅一行，证明无跨例串扰与累积。JSON 中 managed ref 哈希与 schema 同步变更＝**重跑证据**（非手改） |
| R3 | P3 | **closed** | `verify_k07.py:237-259`；verdict `:268-274`；JSON`:70-74,81-85,92-96` | 对照臂内 256 拒 / 2047 过，且**同 reader 读法、同字节**（新 QBuffer+QImageReader，仅改 limit），三例 `decoded:true` 且宽高与主通道一致 → r1「两个变量」缺陷消除；`passed` 判定已纳入该臂（缺该键即 FAIL） |
| R4 | P3 | **closed** | `src/domain/pages/entities.py:26-28`；handoff:49；task:47；`verify_k07.py:15-18` | 核实 domain `Page` 字段仅 `width/height/managed_original_ref`（无 mime）→ 删除表述有据；三处主张均已改为「宽高/managed ref」；diff 内残留的 mime 词仅出现在 R4 处置说明与 docstring 的**否定式**元引用，非主张 |
| R5 | P3 | **closed** | handoff:3,5；`doc/tasks/...:12` | 头部改为「Task 授权基线 8e0de8d0；分支实际 fork 自 release 8996ca55」，拓扑 `8996ca55→a5c8adf1→02f306ea→返修` 与 `.git/worktrees/.../logs/HEAD:1-6` 完全一致；frontmatter 用 YAML 行内注释（`base_commit: 8e0de8d0 # …`）仍可被常规解析取到哈希 |
| R6 | P3 | **closed** | `importing.py:46-54`；handoff:29 | 921 MiB / 5.9× / 2.2× 算术复核通过（966e6 B÷1048576＝921.2；2047/921.2＝2.22；2047/345.57＝5.92）；~350k px 已标注「无实测出处的假设上尾」；「非 0」论证重心改为「有界 fail-closed 锚在域实测 345.6 MiB」，与 r1 要求一致 |
| R7 | P3 | **closed** | `importing.py:410-418`（收紧）→ `:420`（`loadFromData`） | 位置正确：`QImageReader.setAllocationLimit(256)` 在 `image.loadFromData(raw)` **之前**，且 `from PySide6.QtGui import QImage, QImageReader` 同步（:401）；既有 MOBI 面零影响可静态论证——256 恰为 a5c8adf1 之前 MOBI 通道的有效上界（任务前 Qt 内建默认），收紧只是恢复原 fail-closed 语义；测试侧仅 `tests/library/test_production_adapters.py` 触碰 `allocationLimit`（grep 6 处全在该文件），无断言冲突；`import_formats` 计 28 例自洽（26 个 `def test_` + `test_document_import.py:277-279` 三值 parametrize ＝ 28），但实跑绿态属 NOT_VERIFIED |
| R8 | P4 | **closed** | `test_production_adapters.py:179-180` | `endswith("...")` + `len(detail) == _ERROR_DETAIL_MAX_CHARS + 3` 替代 `<=400`；对 `"x"*5000` 的 fake（:170）语义正确。残留 P4：断言与实现共用同一常量，改大常量测试仍绿（不 pin 300） |
| R9 | P4 | **closed（含 P3 更正）** | `verification/.../pre-fix-tests-against-base-src.txt:13-24`（溯源）、`:27-37`（红态）、`:50-51`（恢复）；`test_production_adapters.py:80` | 溯源行**合格**：`git checkout 8996ca55 -- <file>` 写回基线 blob → `git diff 8996ca55 -- <file>` 空（git 语义零 diff，附 autocrlf 说明）→ `git show 8996ca55:<file> \| grep -c setAllocationLimit` ＝ 0 → `-c "import infrastructure.importing as m; print(m.__file__)"` 打印 worktree 解析路径（证明 pytest 未用到别处副本）。红态 **4 failed / 1 passed / 8 deselected** 经我独立静态推演**完全吻合**（长条 289.5>256 拒、setter calls 空、R8 收紧断言失败、fail-closed 256 下同样拒 2048→基线绿；文件 13 用例－选中 5＝8 deselected）；`@pytest.mark.slow` 已加在真实 289.5 MiB 解码用例（:80），marker 已在 `pytest.ini:4` 注册。**唯一缺陷见 N1（:40-41 失败归因错）** |
| R10 | P4 | **closed** | handoff:66-67 | `--out verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json` 已补；`verify_k07.py:277-280` 确实 `mkdir+write_text` 落盘（`ensure_ascii=False, indent=2`）。**残留见 N2：§5 的断言数字未同步** |

补充：commit 内容完整性（dispatch 第 3 点）——`.git/worktrees/M2-IMPORT-ALLOC-LIMIT-zcode/logs/HEAD:6` 证实 `02f306ea → 400046ef`「review-fix … R1-R10」、`.git/refs/heads/agent/zcode/M2-IMPORT-ALLOC-LIMIT`＝`400046ef…`；worktree 实文件中 R6 注释（`importing.py:46-54`）与 R7 收紧（`:410-418`）**均在**，且 `review-fix.diff:331-382`（R6/R7）与 `:438-494`（R9 新增文件）表明 diff 含全部 7 文件——R9 误擦（`git checkout HEAD --` 抹掉未提交的 R6/R7）已被**重新应用并落盘**，轨迹自洽（返修 commit 时间 1790864206 晚于 R9 归档所述 HEAD=02f306ea 的 1790862312）。

## 回潮与新问题

**回潮检查：通过。** `review-fix.diff` 恰 7 个 `diff --git` 头（:1,89,115,331,383,438,495），全部落在任务书允许面（`doc/tasks`+`doc/handoffs`、`experiments/M2-IMPORT-ALLOC-LIMIT/**`、`verification/M2-IMPORT-ALLOC-LIMIT/**`、`src/infrastructure/importing.py`、`tests/library/*`）；禁改面（`src/ports/**`、其他 infrastructure、`src/bootstrap/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`）零出现。值得肯定：R7 的加固被正确限制在**唯一允许的 src 文件**内完成，未越界去改 `pixel_source_style.py`/`qt_compositor.py` 等禁改面。handoff **返修记录节存在且可用**（`handoff.md:82-103`，R1-R10 表 + 返修后验证三行）。

**新发现（均不阻塞）**

- **N1（P3，证据文字错误）** `pre-fix-tests-against-base-src.txt:40-41` 对 R1 用例的红态归因不成立：(a) 690×4000×4＝10.53 MiB **远低于** 256 MiB，基线全局 256 根本不会拒绝它；(b) 该用例没有「@2047 必过」腿（那是 R3 对照臂的命名）。真实红因是 `monkeypatch.setattr(importing,"_ALLOCATION_LIMIT_MIB",1)` 在基线（无该常量）上抛 `AttributeError`（`test_production_adapters.py:128`）；即便退一步假设基线已存在该常量，失败也会是 `DID NOT RAISE`，仍非 256 拒绝。**计数与结论（基线红）不受影响**，但摘录属"作者转述"且错。另：本仓既有先例 `verification/TASK-043/pre-fix-tests-against-base-src.txt` 归档的是**原始 pytest 输出（含 traceback）**，建议照抄该格式或直接修正这两行。
- **N2（P3，数字过期）** `handoff.md:63-64` 复现命令仍写"期望 521 passed, 1 skipped"，返修新增 R1 用例后应为 **522**（四套件）/ **550**（五套件，见 `:101`）。§5 与 §8 自相矛盾，照 §5 复跑会"对不上期望值"。同类轻量项：`:80` Review 指引仍提"stash 复现"（R9 已改 blob 写回法，见归档 :10-11）；`doc/tasks/...:46` AC2 行仍是 a5c8adf1 口径（3 failed/4 新增、517→521），未提返修后 4 failed/5 新增、522/550——可作历史记录，但建议加一行指回 handoff §8。
- **N3（P3，上界影响面登记不全）** a5c8adf1 抬高的是**进程全局**，R7 只收紧了 r1 当时点名的 MOBI 路径。同进程另有解码点同样继承该全局：`src/application/export/pdf_qt.py:24`、`src/infrastructure/rendering/pixel_source_style.py:55`、`src/infrastructure/rendering/qt_compositor.py:41,60,61`（均 `QImage.fromData`）。且经 MOBI 渲染后全局会被压回 256、经图片导入后为 2047 → 这些站点的实际上界**随执行历史在 256/2047 间浮动**。这些文件全在禁改面，正确处置是**登记**（建议在 `handoff.md:70-76` §6 增一行，或留作后续 Task），而非本 Task 改码。
- **N4（P4）** `verify_k07.py:268-274` 的 `passed` 只校验 `rejected` 与正向臂，**不校验 `native_stderr` 非空**——R2 所依赖的那行日志若因 Qt 日志规则变化而消失，脚本仍会输出 `verdict: PASS`（静默退化）。建议加一条 `and "exceeds the current allocation limit" in v["native_stderr"]`。
- **N5（P4）** `importing.py:418` 用字面量 `256` 复刻 Qt 内建默认（注释已解释），但无命名常量；另该收紧在"未来并发导入"下是 best-effort（`importing.py:59-62` 自陈单线程）。两者均为登记级。
- **N6（P4）** `test_production_adapters.py:180` 断言自引用 `_ERROR_DETAIL_MAX_CHARS`（见 R8 行）。
- **N7（P4，nit）** task:48 引用 stderr 原文时省略了 JSON 中实际存在的 `qt.gui.imageio: ` 分类前缀，并称"原文"；handoff:89 已带前缀，建议统一。

## NOT_VERIFIED

1. **全部实跑数字**：五套件 550/四套件 522、基线 517、`import_formats` 28 例、红态 4 failed/1 passed 的**真实控制台输出**（本沙箱无 shell；红态数字与我的静态推演吻合，但并非实跑复现）。
2. **worktree 相对 400046ef 是否干净**（`git status --porcelain`）；以及 `review-fix.diff` 是否由 commit 而非脏工作区生成（`git diff 400046ef` 应为空）。间接证据充分（reflog 提交时间晚于 R9、diff 含新增文件与 R6/R7），但 commit 对象内容无 shell 不可直接展开。
3. `git diff --check` 与 `+284/−50` 精确计数。
4. K07 资产 `sha256 95435126…`（JSON:8）与 TA3-B2 记录/资产实际哈希的一致性（无 `sha256sum`）；仅宽高 690×131289 与 TA3-B2 记载一致。
5. R7 的运行时效果：Qt 全局是否确如注释所述同样约束所有 `QImage.fromData` 站点（N3 的前提），需一次运行时确认。
6. `verify_k07.py` 在目标机复跑（含 fd2 捕获在控制台/重定向两种宿主下的可重复性）。
7. `tests/import_formats` 全绿（R7 MOBI 面回归）——owner 声称，未复跑。

## 推荐下一步

集成方（Codex 代行）在 worktree 执行 `git status --porcelain`（期望空）并复跑 `PYTHONPATH=src <venv> -m pytest tests/library/test_production_adapters.py tests/providers tests/core tests/m2_acceptance tests/import_formats -q`（期望 550 passed, 1 skipped）确认后，即可把 **400046ef** 合入并把 M2-IMPORT-ALLOC-LIMIT 置 done；同时建议由 Owner 用一个纯文档 commit 顺带闭合三处 P3：修正 `pre-fix-tests-against-base-src.txt:40-41` 的失败归因并补原始 pytest 失败输出、把 `handoff.md:63-64` 期望值改为 522/550、在 §6 登记非 MOBI 解码面的全局上界浮动（N1/N2/N3），均无需重审代码。
