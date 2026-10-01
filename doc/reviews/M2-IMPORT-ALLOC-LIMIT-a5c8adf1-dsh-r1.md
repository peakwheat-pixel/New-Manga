dsh: reasoning:
Let me start by exploring the workspace and the review inputs.

The task: static review of M2-IMPORT-ALLOC-LIMIT. Need to read the diff, task doc, handoff, verification JSON, and the actual code in the worktree.

Let me start.
dsh: reasoning:
Sandbox issue. The workspace is G:\CODEX\New Manga but paths outside? Let's try again maybe read-only operations. The error is about grantWrite failing. Perhaps use read/glob/grep tools instead.

Let me try glob/read tools.
dsh: reasoning:
pwsh fails due to sandbox write grant across drive? "SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)". Probably the sandbox tries to grant write on workspace but fails due to permissions? Actually the error suggests ACL modification failed. Approval policy ask. Let's try pwsh with sandbox_permissions escalation? The instruction says sandbox_permissions for a one-shot retry of the exact operation the sandbox just denied. This is a command denial (grantWrite failed). Hmm, the failure is in the harness itself, not the command. Let me retry once with danger-full-access? But that's a heavy escalation. Let's first try a simple pwsh command again to see if it's transient.

Actually the task says: "沙箱无 shell 时不执行命令，NOT_VERIFIED 留给集成方" — i.e., if the sandbox has no shell, don't execute commands; leave NOT_VERIFIED to the integrator. So this is anticipated: I should do a static review with read/grep/glob tools only.

Let me still try once with escalation? The instruction says retry the exact operation with sandbox_permissions if denied. The sandbox denied because it couldn't grant write. Given the user's explicit instruction that no shell → no commands, I'll do static review. But maybe a read-only retry would work... The policy is workspace-write, and it fails. Let me try one escalation attempt with danger-full-access to get git commands? Approval policy is ask; without answerer it fails closed. Hmm. Let's try once — if it fails, proceed statically. Actually the guidance: "a blocked file operation is reported as [sandbox: file access denied under <mode> mode], a policy denial: do not retry another way." Here it's a different error (SetNamedSecurityInfoW). Let me try one retry with sandbox_permissions=danger-full-access and justification.

Actually, wait — maybe try `run_in_background`? No. Let me just try the escalation once with a cheap command (git status/log in the worktree). It's worth it for verification of commit hashes, diff --check, etc.

Let me do that and in parallel read the diff file.
dsh: reasoning:
No shell available. So all git/shell verification → NOT_VERIFIED. Good, that's anticipated.

Now let me read the actual source files in the worktree: src/infrastructure/importing.py, tests/library/helpers.py, tests/library/test_production_adapters.py, doc/tasks/M2-IMPORT-ALLOC-LIMIT.md, doc/handoffs/..., verification JSON, and the verify_k07.py script. Also check ta3-b2 docs for F2 caliber, and the review template (doc/templates/REVIEW.md), plus the collaboration doc maybe. Also prior review r1 R4 reference.

Let me also read dsh-task-r1.txt and dsh-review-r1.md in the task env (previous round?).

Let me read files in parallel.
dsh: reasoning:
Interesting — dsh-review-r1.md appears to be a leaked transcript of this very session (probably a previous run artifact of the same dispatch). I should not treat it as prior review content; it's this run's own transcript replay. Actually it seems the harness logs my reasoning into that file. I'll ignore it (it's the same round-1 dispatch, not a prior review).

Wait — note line 5 of the task says base=8996ca55, while the handoff says base 8e0de8d0. Interesting discrepancy: the task doc says base_commit: 8e0de8d0 and handoff says base `8e0de8d0`. But the dispatch says base=8996ca55 (the half-finished worktree from a circuit-broken agent). So there are two baselines: task base commit 8e0de8d0 (git base) and the abandoned worktree state at 8996ca55. Hmm, actually "base=8996ca55" might be the base of the review diff (the commit the diff is computed against). And task doc says base_commit: 8e0de8d0. That's a discrepancy worth checking: is a5c8adf1's parent 8e0de8d0 or 8996ca55? The red test used stash on top of 8996ca55 baseline. Let me check git log via reading .git files? I can't run git. But I can read the worktree's .git file — the worktree's .git is a file pointing to the common dir. And the git log can be read from .git logs/HEAD (reflog) in the common dir. Let me check.

Let me look at the repo's .git directory: G:/CODEX/New Manga/.git/worktrees/M2-IMPORT-ALLOC-LIMIT-zcode/... and G:/CODEX/New Manga/.git/logs/HEAD.

That's a nice static way to verify commit topology and porcelain-ish state (can't check index). Let me try.

Also I need to read:
- tests/library/helpers.py (full)
- tests/library/test_production_adapters.py (full)
- doc/tasks/M2-IMPORT-ALLOC-LIMIT.md (full)
- doc/handoffs/M2-IMPORT-ALLOC-LIMIT-a5c8adf1.md (full)
- verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json
- experiments/M2-IMPORT-ALLOC-LIMIT/verify_k07.py
- doc/templates/REVIEW.md for the review format (though output format given).
- TA3-B2 quality report re F2 to check caliber upgrade claim.
- doc/09_COLLABORATION.md for allowed paths / review rules? Maybe check task file for allowed/forbidden paths.

Let me batch reads.
dsh: reasoning:
Now let me analyze deeply.

Key observations:

1. `src/infrastructure/importing.py`:
   - `setAllocationLimit(_ALLOCATION_LIMIT_MIB)` before read. Fine.
   - Comment claims decay "Qt checks the bound before allocating" — accurate for QImageReader/QImageIOHandler. Actually in Qt, QImageReader::read checks `QImageIOHandler` and there's a check in `QImageReader::read()`: `if (d->handler && ...)`. The allocation limit check is done in `QImageReader::read` via `qt_imageAllocationLimit` — actually the check is in `QImageReader::read()`: 
     ```
     if (d->handler) { ... }
     ```
     Real implementation: In `qimagereader.cpp`, `QImageReader::read()`:
     ```
     QImage image;
     ...
     if (d->handler && d->handler->canRead()) { ... }
     ```
     And `QImageIOHandler` calls `qt_allocateImage`? Let me recall. Qt 6.5 added `QImageReader::allocationLimit()` and `setAllocationLimit()`; default 256 MB; the check: "The allocation limit is checked before the image is allocated." Implementation in qimageiohandler.cpp? Actually in `QImageReader::read()`:
     ```
     #if QT_CONFIG(imagedecoder) ... 
     ```
     The relevant code: `qimageiohandler.cpp` has
     ```
     static bool checkImageAllocation(...)
     ```
     Hmm, in qimage.cpp there's `QImage::QImage` overloads that fail if size exceeds limit? Actually the check happens through `QImageIOHandler::read()` calling `QImage::setDevicePixelRatio`... Let me recall the actual source of `qimageiohandler.cpp`:
     ```cpp
     bool QImageIOHandler::allocateImage(QSize size, QImage::Format format) ...
     ```
     Hmm, I recall Qt 6.5 introduced `QImageIOHandler::allocateImage()` which checks:
     ```cpp
     bool QImageIOHandler::allocateImage(QSize size, QImage::Format format) {
         if (size.isEmpty()) { ... return false; }
         if (!qt_imageiohandler_checksize(size, format)) return false; // allocation limit
         image = QImage(size, format);
         ...
     }
     ```
     And there's `QImageReader::allocationLimit` documentation: "The allocation limit is a safety mechanism to prevent the application from allocating too much memory... Images that exceed this limit will fail to decode. ... The default value is 256 MB. ... Setting the limit to 0 disables it." And a note: "The limit is an estimate of the amount of memory an image will require, and is checked before allocation."

     Actually more precisely: Qt docs say "Since Qt 6.5, QImageReader has an allocation limit, default 256 MB. ... The limit is checked after reading the image header, before allocating the image." That matches the claim "Qt checks the bound before allocating". So the comment is accurate. However — an important nuance: the limit check applies to images that "exceed" the allocation limit; it's based on the estimated memory required (size × depth/8), and the "Unsupported" nuance: the check happens in the handler via `QImageIOHandler::allocateImage` for handlers that opted in (PNG handler uses it). Indeed the PNG handler in Qt 6.5+ uses `allocateImage()` so the limit applies. But not all handlers use it? Hmm. Actually the check exists in QImageReader::read too? Let's think about correctness of this static review: the key risk is whether the claim "Qt checks before allocating" is verifiable and whether the test truly locks the mechanism.

   Important potential issue: **`_reader_error_detail` test with `LongErrorReader` monkeypatching `PySide6.QtGui.QImageReader`** — but `decode()` imports `from PySide6.QtGui import QImageReader` inside the function, so monkeypatching the module attribute works.

   BUT: `test_qt_image_decoder_uses_safe_mime_fallback` also monkeypatches with `UnknownFormatReader` that now has a static `setAllocationLimit`. Note that `decode` calls `QImageReader.setAllocationLimit(...)` where QImageReader is the class (fake), so a static method on the fake is needed — they added it. Good catch by owner.

   However there's a subtle issue: in `test_qt_image_decoder_truncates_very_long_reader_errors`, the fake `LongErrorReader.setAllocationLimit` is a staticmethod, fine.

2. **`test_qt_image_decoder_imports_webtoon_long_strip_beyond_qt_default_cap`** — potential correctness concern: it sets `QImageReader.setAllocationLimit(256)` then calls decode which re-asserts 2047. The `make_thin_png(690, 110_000)` with full rows (data_rows = 110000) compresses a 690×4+1=2761 bytes row × 110000 rows = ~303.7 MB of raw zeros → zlib compress(9) with back-references produces tiny output. But the *factory* memory: batch = row * rows_per_batch. rows_per_batch = max(1, 8388608 // 2761) = 3038 rows → batch = 3038*2761 ≈ 8.39 MB. OK bounded ~8 MiB. Fine. Compress time for 300MB of zeros at level 9: zlib on highly repetitive data is fast-ish but level 9 on 300 MB... maybe ~1-2 s. Acceptable.

   Then decoded = QtImageDecoder().decode(data) — actual Qt decode of a 690×110000 RGBA image = 304 MB allocation. The allocation limit check: 690*110000*4 = 303,600,000 bytes = 289.5 MiB < 2047 → allowed. Decode succeeds. Note: does PNG handler allocate 690×110000*4 = 303.6MB? Yes, and the test allocates it. That's heavy but fine.

   Wait — but does the decode actually succeed given the image is a real full PNG? Yes, all rows present.

   Important: this test with `QImageReader.setAllocationLimit(256)` first is somewhat redundant given the decoder re-asserts. Actually the point is to prove that the pre-existing 256 value gets overridden. Fine.

3. **fail-closed test with `make_thin_png(8192, 65536, rows=1)`**: 8192*65536*4 = 2,147,483,648 bytes = 2048 MiB exactly. The check is `>` limit? Qt's check: `if (totalSize > limit)` → reject. limit=2047 MiB → 2048 > 2047 → reject. Good, boundary is exactly at the edge: if Qt's comparison were `>=` it'd also reject. Either way rejected. Good — but the test does NOT assert the reason is the allocation limit; it only asserts that an ImageDecodeError is raised with non-empty bounded detail. Concern (審查項3): the test comment claims "Qt checks against declared IHDR size before allocating, so a single IDAT scanline exercises the real rejection". But the assertion cannot distinguish:
   - rejection by allocation limit (desired mechanism), vs.
   - rejection because the IDAT stream is truncated/incomplete (rows=1 of 65536) → decode error "Unable to read image data" anyway.
   
   Both produce ImageDecodeError! So the test is NOT locking the mechanism — exactly the concern raised. The test would pass even if `setAllocationLimit` were 4096 (i.e., if the fix were broken/open) because the truncated IDAT would still fail. That's a real finding: the fail-closed test is a tautology — it asserts failure for a payload that fails regardless. To actually lock the mechanism you'd need something like: assert with limit=2047 → reject AND with a bigger-but-not-huge declared size... hmm, but constructing a decode that would succeed if allowed would need the real full data (2GB). Alternative: use a smaller declared size that exceeds 2047 (e.g. 65536×8192) and check detail/errorString — but errorString is the same "Unable to read image data". A better mechanism lock: read the stderr message, or check timing, or use a size that exceeds the limit and whose rows are complete? Not feasible within 2GB.

   Alternatively, the mechanism could be locked by asserting that a *complete* valid PNG just under 2047 MiB decodes fine (but that allocates ~2GB in test — no). Or assert that the same truncated payload with a limit of e.g. 4096 still fails (showing the failure is truncation not limit) — that would show the test does not isolate the mechanism. So finding: the test's claim of "exercising the real rejection" is unverified by assertion; it only asserts typed fail-closed on oversize declaration. Severity: P2 (test does not lock the mechanism it claims; would pass with a broken limit). Since the red-state result says this test was green on baseline (256 also rejects), the test provides no red signal for the fix — acknowledged by owner as "保护性回归测试基线绿符合预期". But the conclusion "the fix must NOT swallow it" is only partially demonstrated.

   Hmm, but is there a way the test *does* isolate? No. The comment even acknowledges that with rows < height the payload is truncated by design. So the failure may be due to truncation. I should flag as P2 finding with a concrete suggestion: add an assertion that distinguishes (e.g., run the same payload with the limit restored to a value above the allocation size, and assert it still fails — proving failure is truncation, which then means the test cannot claim to lock the limit mechanism; or better: verify via a *valid but smaller* image with the limit temporarily set below its size, i.e. setAllocationLimit(1) then decode make_png(4,3) → reject with typed error, proving limit enforcement is active, plus decode succeeds at 2047 — that pair locks "limit is the deciding factor"). Actually that's a nice alternative: a positive control: `QImageReader.setAllocationLimit(1)` then decode a real small png → must raise ImageDecodeError; and decode a 289.5MiB webtoon strip at 256 → must succeed. Hmm the second is already the red/green test. The pair (reject at 1, accept at 2047 for the same input) *does* isolate the limit mechanism. For the >2047 case they'd need a >2047 declaration, which the truncated test gives — combined with a check that the same file at limit=... hmm.

   Practical suggestion: in the fail-closed test, additionally assert that the payload fails with a limit raised above 2048 (e.g. monkeypatch the module constant to 4096 and confirm it still fails with the same error) — that shows the failure is truncation-driven, exposing the test's non-isolation; the honest fix then is to add a separate mechanism test: `setAllocationLimit(1)` + a valid small PNG → typed ImageDecodeError (proves the limit is enforced by Qt at all and that the decoder does raise typed failure), or capture stderr. I'll suggest that shape but frame it as "test does not distinguish", leaving the fix approach to owner.

   Actually careful: is it really true that a truncated IDAT fails? PNG handler in Qt: it decodes rows until data ends; when the IDAT stream is exhausted early, `read()` returns a null image (failure). Yes — QImageReader::read returns null and errorString = "Unable to read image data". So indeed the test passes for the wrong reason. But note: Qt's PNG handler in 6.x reads the whole image via `read()` and if incomplete, returns false. So yes.

   There's also a risk in the opposite direction: maybe the truncated IDAT alone causes rejection before the allocation-limit check? No, the limit check happens at `allocateImage` after header parse. Either way.

   Additionally: another consequence — the test says "never a process kill", demonstrating fail-closed. Fine.

4. **`detail` length assertion `<= 400`** while the truncation constant is 300 + "..." = 303. The bound 400 is loose but fine. However the truncation test asserts `detail.startswith("x"*100)` and `len(detail) <= 400` — but doesn't assert `len(detail) == 303` or that it ends with "...". So a regression that truncates to e.g. 500 chars would fail (501 > 400), ok. But a regression removing truncation entirely → 5000 > 400 fails. A regression truncating to 350 would pass despite violating _ERROR_DETAIL_MAX_CHARS=300. Minor P3: assert exact bound.

5. **The `_reader_error_detail` fallback**: "bytes are not a decodable image" — Old behavior preserved semantically. Fine. But note that the old code was `reader.errorString() or "bytes are not a decodable image"` — if errorString was whitespace-only, old code kept whitespace; new strips. Improvement.

   Potential issue: `_reader_error_detail(reader)` calls `reader.errorString()` — the fake readers have it. OK.

6. **Concurrency/threading claim**: "Import runs on the application thread today; worst case under concurrency is two idempotent writes of the same value." Is that actually sound? `QImageReader::setAllocationLimit` is a static that sets a global (`Q_GLOBAL_STATIC`/atomic?). In Qt 6.5 source:
   ```cpp
   static int qt_allocationLimit = 256;
   int QImageReader::allocationLimit() { return qt_allocationLimit; }
   void QImageReader::setAllocationLimit(int mbLimit) { qt_allocationLimit = mbLimit; }
   ```
   Hmm, in Qt 6.x it's implemented via `QImageReader::setAllocationLimit` using a static atomic? Let me recall qimagereader.cpp:
   ```cpp
   /*!
       \since 6.5
       ...
   */
   int QImageReader::allocationLimit() { return qt_imageReaderAllocationLimit(); }
   void QImageReader::setAllocationLimit(int mbLimit) { ... }
   ```
   Actually I believe it's:
   ```cpp
   static QBasicAtomicInt qt_allocation_limit = Q_BASIC_ATOMIC_INITIALIZER(256);
   ```
   In Qt 6.5+, `QImageReader::allocationLimit()`/`setAllocationLimit()` are backed by an atomic (QBasicAtomicInteger) — I recall the implementation in `qimagereader.cpp`:
   ```cpp
   namespace {
   QBasicAtomicInt allocationLimit = Q_BASIC_ATOMIC_INITIALIZER(256);
   }
   ```
   Hmm. I'm fairly confident it's atomic because `QImage::fromData` etc. can be called from threads. Qt docs mention: "setAllocationLimit() ... This function is thread-safe." Not sure. I should not assert strongly. I'll note that the claim "idempotent/same value under concurrency" is *behaviorally* fine regardless of atomicity (setting the same int value concurrently is benign even if non-atomic in the strict sense — a torn write isn't possible for a naturally aligned int on supported platforms, but the C++ standard makes it UB). Since both writers write the same value, the practical risk is nil. So the argument is acceptable; but the comment should ideally not rely on "same value" alone if another code path could set a different value (e.g., future code or tests). And indeed the *test fixture* sets 256 → then decode re-asserts 2047; that's the very cross-mutation scenario, single-threaded. Fine.

   Is there a more reasonable instance-level approach ignored? QImageReader is per-instance, but the allocation limit is NOT a per-instance property (Qt only provides static). So the "instance-level alternative" doesn't exist for QImageReader in Qt 6.5. However, an alternative implementation could be: call `setAllocationLimit` once at composition/bootstrap (but that's a forbidden path `src/bootstrap/**` and wouldn't self-heal), or set it in `QtImageDecoder.__init__` plus per-decode re-assert. Or the decoder could check `QImageReader.allocationLimit()` and only set if lower — a read-modify-write that's worse (TOCTOU). So the per-decode assert is defensible. But one real design concern: the global setter affects *all* QImageReader users in the process, including `QImage.fromData`? Does `QImage::fromData` respect the allocation limit? `QImage::fromData` creates a QImageReader internally → yes, it does affect `_PdfiumDocumentHandle`/`_MobiDocumentHandle` which use `QImage.loadFromData`. Actually `QImage::loadFromData` uses QImageReader internally → the allocation limit applies. So the side effect broadens the cap for PDF/MOBI raster decode too. Is that a problem? It raises the cap from 256 to 2047 process-wide, which weakens the built-in safety for all decode paths in the process (including PDF page render → PNG decode, MOBI pages). The comment says the static setter is process-global and justifies per-decode idempotence, but it doesn't explicitly acknowledge/analyze that it *lowers the process-wide protection* for every other QImage/QImageReader decode path (e.g. `_MobiDocumentHandle.render_page` uses `image.loadFromData(raw)` on untrusted MOBI-embedded images; `_PdfiumDocumentHandle` writes PNG via image.save, no read). That's a genuine finding: the side effect scope isn't fully enumerated. Severity P3 (documentation/analysis incompleteness) — could be P2 given a security-ish angle (memory-amplification cap weakened for untrusted MOBI page images: a 2GB declared MOBI image would now be attempted → possible OOM). Actually that's a plausible DoS vector: MOBI embedded page images are untrusted input; previously capped at 256MiB, now up to 2047MiB. The mitigation: still fail-closed at 2047. Worth flagging as a scope/side-effect note the owner should register, since AC1 requires "内存上界必须有论证" for the limit chosen — the argument covers domain webtoon pages but the global setter's effect on *other* untrusted decode paths (MOBI) is not analyzed. Good finding, moderate.

   Wait, does `_MobiDocumentHandle.render_page` run in the same process and after some webtoon decode? Yes, same process. The global limit persists at 2047 for the process lifetime after any image import decode. So MOBI embedded images up to 2047MiB decode would be attempted. Prior: 256. So the effective cap for MOBI rises 8×. This is a real, if modest, risk-amplification that the rationale didn't cover. P3 (or P2). I'd call it P2-ish? The task discipline says "内存上界必须有论证（不能简单 setAllocationLimit(0)）" — they gave an argument for the value relative to the webtoon domain; the global bleed to other readers is unaddressed. I'll rate P3 (documentation/analysis gap, no functional defect) but recommend registering it in the comment/handoff. Hmm, given this is a memory-safety-relevant global, maybe P2. Let me weigh: the reviewer shouldn't inflate. The practical exposure: MOBI import of a crafted embedded PNG with declared ~2GB — Qt rejects above 2047 so max attempted allocation ~2GB → OOM risk on memory-constrained machine vs previously 256MB. This is a genuine regression in the fail-closed envelope for a *different* input class. I'll mark P2 with a concrete minimal remedy: either scope the cap (not possible instance-wise), or apply the raised limit only around the webtoon/page decode... but it's static, can't scope per-read safely. Alternative remedy: keep 2047 but register the widened envelope for `_MobiDocumentHandle` (documented risk) — or make `_MobiDocumentHandle` explicitly re-assert 256 before its own loadFromData (defense in depth, cheap). That's a concrete, minimal suggestion. Nice — that's a substantive review contribution.

   Hmm wait, but is the MOBI path really reading untrusted data with `QImage.loadFromData`? Yes: `raw = path.read_bytes()` from extracted MOBI. And `_MobiDocumentHandle.render_page` can be reached in the same process. Also `PdfiumDocumentRaster` renders bitmap then `image.save` (no read). And what about `QtImageDecoder.decode` itself — fine.

   Also note that `_MobiDocumentHandle` is in the same file (allowed path), so a remedy is within the allowed surface. Good.

7. **Red-state methodology**: "git stash src 后对 8996ca55 基线跑新测试". The method: stash only src (keeping new tests), run the new tests against baseline src → 3 failed / 4 new. That's a valid red test for the fix, provided the stash actually reverted importing.py. But careful: the new tests depend on `make_thin_png` in helpers.py which is a *test* file (kept). Yes.

   Concerns:
   - The red claims in the handoff are not reproducible from the diff alone; the "verify" section is prose. Static review can't re-run → NOT_VERIFIED. Fine.
   - The claim "3 failed" and "第 4 个 fail-closed 保护测试基线即绿" is self-consistent with the test designs: on baseline (no setter), test 1 fails at 256 (289.5MiB > 256) ✓; test 2 fails (calls empty) ✓; test 3 fail-closed: baseline has no setter call, so Qt default 256 → 2048 > 256 → rejected → passes ✓; test 4 truncation: baseline detail = errorString() (5000 chars) not truncated → `len(detail) <= 400` fails ✓. So 3 failed / 4 new. Consistent. 
   - But: is test 3 on baseline really passing? On baseline, `decode()` does `detail = reader.errorString() or "..."` → for the truncated PNG at 256 limit, errorString = "Unable to read image data" → ImageDecodeError raised → test passes. Yes.
   - One subtlety: the red state's test 1 sets `QImageReader.setAllocationLimit(256)` explicitly before decoding; on baseline, decode does not re-assert, so 256 stands → 289.5MiB rejected → fails ✓. Good, the test is designed to be red on baseline.
   - Also the autouse fixture restores the process global; in the red state, test 1 sets 256 and fixture restores before-value... Actually fixture records `before` at test start; test 1 sets 256 inside; after, restored to `before` (which is 256 if nothing changed, or 2047 if a previous test's decode leaked — note the fixture restores, so with the fix the global returns to whatever it was before the test, typically 256 default). Fine.
   
   - However: there's an ordering hazard — the autouse fixture's `before` is read at setup, and tests like `test_qt_image_decoder_reports_dimensions_and_mime_type` (which runs before the fixture is defined? no, fixture is module-level autouse → applies to ALL tests in the module, including the 3 pre-existing ones) — good, so global leakage across modules is contained. But the fixture is module-scoped autouse → applies to all tests in this module only. Cross-module leakage: if another test module runs decode and leaks 2047... with the fix, decode always leaves 2047 in the global. Consider the run order: `test_production_adapters.py` decode tests run → global becomes 2047 (or restored to `before` by fixture after each test). The fixture restores after each test in this module. But `test_qt_image_decoder_raises_allocation_limit_above_qt_default` monkeypatches setAllocationLimit itself, so no global change. And the doc-table/other modules (m2_acceptance) using QtImageDecoder? If any other test module calls `QtImageDecoder().decode`, the global becomes 2047 and stays. Does any other test assert on the 256 default? Unlikely. But there's a subtle real-world concern: the global persists after the first decode → *any* subsequent Qt decode in the same process gets 2047. That's the production design (intended). Fine.

8. **verify_k07.py**:
   - Control pass: sets `QImageReader.setAllocationLimit(256)` claiming "the unfixed Qt default (F2)". The *unfixed Qt default* is indeed 256 MiB, and baseline decode didn't set it. But note: the control is run *after* the production pass, and they explicitly set 256 to reproduce. That's a faithful reproduction of the pre-fix code path only if the process's global was 256 at that point and baseline never asserted. Since baseline `decode()` never calls the setter, the effective limit is Qt's default 256 — unless some other code changed it. So the control is a valid attribution: same reader code with default 256 → rejected; production channel with 2047 → accepted. This does support "the fix made it pass". 
   - BUT: attribution caveat — the control uses raw `QImageReader.read()` on the bytes, while the production path routes through `ImportImagesUseCase` → `QtImageDecoder` → QBuffer/QImageReader. The difference between the two runs is (a) the limit and (b) the surrounding plumbing (ManagedCopy, sink). Could the production pass have succeeded for another reason (e.g. the decoder never actually decodes bytes... no, it does). Or could the control have failed for another reason (e.g. `QBuffer` lifetime/format detection)? Both use QBuffer. The control doesn't call `reader.format()`. Should be the same. Also, the claim of the stderr message "Rejecting image as it exceeds the current allocation limit of 256 megabytes" — that's a Qt categorized log (`qt.imageio` category). The JSON does NOT include the stderr message! The handoff says "已归档进 JSON 附带复现命令" but the JSON's `control_qt_default_256` entries only have `rejected` and `detail` ("Unable to read image data"). The stderr line is NOT in the JSON. So the claim "stderr 归档" (archived) is not supported by the evidence file: no stderr text and no reproduction command field in the JSON. Let me double check the JSON: fields: schema_version, task, cases{}, control_qt_default_256{Case:{rejected, detail}}, verdict. Indeed no `stderr`, no `repro_command`, no `qt_version`, no `timestamp`, no `env`/python version. Findings:
     - P2/P3: handoff §4 claims "（已归档进 JSON 附带复现命令）" but verify-k07.json contains neither the Qt categorized log text nor a repro command. Evidence claim exceeds the artifact. This matters for the "F2 一级证据" caliber: the discriminating evidence that the rejection was due to the allocation limit is precisely that stderr line (errorString is generic "Unable to read image data" for many failures). Without it in the artifact, the control's attribution rests on assertion only. Still, the control rejection is at least consistent. I'd call this P2: the artifact doesn't carry the message that uniquely identifies the limit rejection, while the docs claim it does.
     - Also missing `qt_version`/`PySide6 version` and `allergen`: schema_version=1. Also no `decoded_size_mib` field. Field completeness question in the review prompt: "宽高/managed ref/errorString" — width/height/managed ref present; errorString present; but expected `decoded ≈345.6MiB` not recorded; case-selection cross-ref not recorded. Also K07's `imported[0].filename` = "base.png" and the doc says sizes fine.
     - Also verify-k07.py `MemorySink.max_source_order` returns `len(self.pages)` — fine.
     - Also the script's `ImportSource(filename=path.name, ...)` → filename "base.png" for all three cases, fine.
     - Script writes JSON via `args.out.parent.mkdir` — path relative to CWD; repro command passes `--out verification/...`. The handoff repro command omits `--out`! Handoff §5 says `PYTHONPATH=src "$PY" experiments/M2-IMPORT-ALLOC-LIMIT/verify_k07.py` with no `--out`, so the JSON wouldn't be regenerated. The script docstring shows `--out verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json`. Minor P3: repro command in handoff doesn't reproduce the artifact.
   - `verify_k07.py` measured "≈345.6 MiB" claim: 690×131289×4 = 362,357,640 B = 345.57 MiB ✓. K09: 690×100480×4 = 277,324,800 = 264.48 MiB ✓. K10: 690×100674×4 = 277,860,240 = 264.99 MiB ✓. Good, numbers check out. Note K09/K10 at ~264.5/265 MiB are just above the 256 MiB default (264.5 > 256) ✓ consistent with F2 rejections.
   - Domain bound extrapolation: "690 x ~350k px x 4B ≈ 965MiB" — 690×350,000×4 = 966,000,000 B = 921.3 MiB. Hmm: 966e6/1048576 = 921.2 MiB. The claim says 965 MiB — that's using MB (10^6) not MiB: 966 MB ≈ 966e6 bytes = 921.3 MiB. So "965MiB" is a unit mix-up (it's ~966 MB = ~921 MiB). Where does 350k px come from? Unstated. Also then "2.1× margin": 2047/921 = 2.22; 2047/965 = 2.12. So with the corrected MiB 921 → margin 2.22×, still fine. The unit slip weakens the argument's rigor slightly (P4/P3 nit) — the conclusion holds. Also "外推最坏 690×~350k" is an unsourced extrapolation; the domain's largest real page is K07 = 131,289 px. Where's 350k from? Unsupported. Worth a finding: the "domain upper bound" is an unproven extrapolation (2.67× the tallest measured page); a 2047/345.6 = 5.9× margin over the *measured* max is the defensible number. Not fatal.
   - "2047 在 Qt int 参数内": 2047 fits int trivially ✓. But why 2047 rather than 2048? Seems chosen to sit just below 2048 MiB (2 GiB) which is a common allocator/arch boundary; the comment doesn't explain *why 2047* specifically (e.g. avoiding an exact 2 GiB boundary or 32-bit size overflow). Minor: the specific value lacks justification for the "-1". Also note that `setAllocationLimit(0)` disables — confirmed by Qt docs. The comment says "in Qt semantics 0 completely disables the check" ✓ correct.
   
   Hmm, actually one more: does Qt's allocation limit apply to the *declared* size or to actual allocation? The claim "checks before allocating" is used to justify rows=1 test. Qt's implementation: `QImageIOHandler::allocateImage()` is called by handlers *before* allocating and checks the limit. For the PNG handler, `QImageReader::read` — the handler reads header then allocates via allocateImage → check. So the check does happen before allocation, based on the header. ✓ The mechanism claim is right in general. But per finding above the *test* doesn't prove it.

   - The control's use of `QImageReader.setAllocationLimit(256)`: is 256 exactly Qt's default? Qt docs: "The default is 256 MB." ✓.

   - One more thing on the control: they restore `setAllocationLimit(_ALLOCATION_LIMIT_MIB)` after; good.

9. **Range discipline (7 files)**: diff touches: doc/handoffs/...(new), doc/tasks/M2-IMPORT-ALLOC-LIMIT.md (status/delivery_head + evidence), experiments/M2-IMPORT-ALLOC-LIMIT/verify_k07.py (new), src/infrastructure/importing.py, tests/library/helpers.py, tests/library/test_production_adapters.py, verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json (new). That's 7 files. All within allowed surface: src/infrastructure/importing.py ✓ allowed; tests/ import related ✓; experiments/M2-IMPORT-ALLOC-LIMIT/** ✓; verification/** ✓; Task/Handoff ✓. No forbidden files. ✓

   But static review cannot verify the top-level diff covers everything (e.g. whether the worktree also modified other files not in the diff). review-input.diff is presumably `git diff base..tip`. I'll note NOT_VERIFIED: "7 文件之外是否还有改动（porcelain/diff --stat 无法在本沙箱复核）".

   Also: the dispatch says base=8996ca55 while Task/handoff say base_commit=8e0de8d0. Two different bases — the handoff says "commit 拓扑：8e0de8d0(base) → a5c8adf1(implement) → 本 handoff commit", and the task says base=8996ca55 was the circuit-broken agent's workspace (uncommitted). So a5c8adf1's parent should be 8e0de8d0, and 8996ca55 is... wait, the dispatch says "base=8996ca55, implement=a5c8adf1, tip=02f306ea (docs)". So the review diff is computed from 8996ca55 → 02f306ea. If a5c8adf1's parent is 8e0de8d0, then 8996ca55 must be an ancestor of 8e0de8d0? Hmm. "续接自熔断半成品" at 8996ca55 as uncommitted changes — then uncommitted changes have no commit hash. So 8996ca55 is probably the commit the previous (circuit-broken) agent's worktree HEAD pointed at, i.e. the base commit for this task's work. But the Task says base_commit: 8e0de8d0. Possibly 8996ca55 is a *later* commit on the mainline (or the previous agent's HEAD) and 8e0de8d0 is the task's declared base — 8e0de8d0 might be an ancestor of 8996ca55, and a5c8adf1's parent = 8996ca55. In that case the handoff's claim "base 8e0de8d0" is loose but the task field says base_commit 8e0de8d0 (unchanged in the diff). The discrepancy is worth a P3 finding: the review diff base (8996ca55) ≠ declared `base_commit: 8e0de8d0`; the handoff says base 8e0de8d0 and topology `8e0de8d0 → a5c8adf1`. If a5c8adf1's real parent is 8996ca55, the handoff topology is wrong/misleading (the implement commit also inherits whatever 8996ca55 contained beyond 8e0de8d0). This matters for scope review: the diff base 8996ca55 may already include unrelated changes from the circuit-broken agent... but the review diff only shows 7 files, so if 8996ca55→02f306ea contains only these 7 files, fine. But the *red-state* baseline claim "stash src 对 8996ca55 基线跑新测试" is against 8996ca55, i.e. the review diff base — consistent with the dispatch. And AC "基线不回退：main 509+1skipped" vs handoff "基线 8996ca55: 517 passed, 1 skipped" vs task discipline "main 509+1skipped". Hmm: handoff says baseline four-suite = 517 passed 1 skipped, delivery = 521 passed 1 skipped. Task discipline says main 509+1skipped 0 failed. 517 vs 509 — different scope counts (four suites vs whole suite). The handoff's four suites = production_adapters + providers + core + m2_acceptance = 517 baseline. Task says main 509+1 skipped. These are different denominators; the +4 is consistent (517→521). But "基线不回退：main 509+1skipped 0 failed" — is 517 the "main" number? Unclear. Potential P4 documentation mismatch: no whole-suite (`pytest tests`) run reported; the task's discipline explicitly cites main 509+1skipped. Handoff only reports four suites. So the full-suite no-regression claim is NOT verified by the reported evidence scope. Worth a finding (P3): the handoff's "四套件" ≠ 全量 tests; the task纪律 baseline "main 509+1skipped" is not re-measured. Recommend running `pytest tests -q` (or the canonical full-suite command) before integration. Let me check whether other tests exist beyond those four dirs — probably yes (tests/library has many files; is tests/library included? production_adapters.py is IN tests/library, but the four-suite command passes only that file, not the whole tests/library dir!). So coverage is: 1 file + 3 dirs. tests/library has many more files (helpers.py, other test files) not run. That's a notable gap: the changed helper `tests/library/helpers.py` (added make_thin_png) could affect other tests? It's additive only, no modification to existing helpers, so low risk. But the claim "无回归" is scoped to 4 selections. Good finding P3.

   Let me verify what's in tests/library to gauge.

10. **The `_restore_qt_allocation_limit` autouse fixture applies to all tests in the module** — including the pre-existing `test_managed_copy_adapter...`. Importing PySide6.QtGui at fixture setup: fine.

11. **Test `test_qt_image_decoder_imports_webtoon_long_strip_beyond_qt_default_cap` memory**: decodes a 289.5 MiB QImage → 303.6 MB RAM in test; plus make_thin_png's ~8 MiB. Acceptable? The handoff says file-level 12 tests in 1.57s. Hmm: creating the PNG (compressing 300 MB of raw zeros at level 9) + Qt decoding 690×110000... in 1.57s total for 12 tests? Compressing 303 MB at zlib level 9 takes ~0.5-1.5s alone; decoding a 289 MB PNG ~0.3-0.5s. Total 1.57s seems optimistic but plausible on a fast machine (zlib on all-zeros compresses at ~200-400 MB/s at level 9? Level 9 is slow; ~50-100 MB/s for zeros... maybe 3-6s). Hmm, "12 passed 文件级 1.57s" (after fix) vs "修正前 9.76s". This is a soft plausibility concern, not something static review can settle (can't run). I'll put it in NOT_VERIFIED as a runtime/perf check but mention the suspicion? I'd rather not raise an unverifiable perf doubt as a finding; maybe as a P4 note that the reported 1.57s for the module (including a 289.5MiB decode) is suspicious and should be re-confirmed at integration, because if the test silently skipped the real decode (e.g. rows=1 semantics or the assertion never exercising the decode) the green evidence is weaker. Hmm — but the test asserts width/height == (690,110000), which requires a successful decode of... actually does it? `DecodedImage(width,height)` comes from `image.width()/height()` of the decoded QImage. So a real decode must have happened. Unless Qt can return an image with correct dims without full allocation — no, QImage allocation happens. So 12 tests must allocate ≥289.5MiB once. 1.57s is fast but possible with fast zlib + fast CPU. I'll note it as a low-severity verification item (P4/NOT_VERIFIED).

Actually wait. Let me reconsider: `make_thin_png(690, 110_000)` full rows: batch = row*3038 where row is 2761 bytes → the loop computes `compressor.compress(batch)` 37 times over ~304 MB. zlib level 9 on highly repetitive data: it uses the hash chain; with all-zero input the matches are long, so throughput can be high (longest-match). Could be ~150-300 MB/s → ~1-2s. Plus PNG decode of 304MB: ~0.3s. So ~2-3s. Reported 1.57s total for 12 tests including 4 new ones... tight but not impossible. Also note the *red* run was 9.76s "修正前" — that's the previously slow fail-closed test (2GB intermediate). Fine, plausible. I'll mention only as NOT_VERIFIED.

12. **`make_thin_png` correctness**: 
    - IHDR = `struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)` → 4+4+1+1+1+1+1 = 13 bytes ✓.
    - CRC via zlib.crc32 ✓.
    - Row = filter byte 0 + width*4 zeros for RGBA8 ✓.
    - Rows per batch = max(1, 8MiB // len(row)) ✓ (for width 8192: len(row)=1+32768=32769; 8388608//32769=255 → batch ≈ 8.36 MB ✓).
    - `b"".join(idat_parts)` — note: for a *full* thin PNG (rows=height) the compressed stream of 304 MB zeros is tiny (~300KB), so join is fine. For rows=1, tiny. But consider a hypothetical huge width/height where compressed output is large — not used.
    - Potential issue: compression ratio for uniform zeros means IDAT is small; but Qt's PNG handler decompresses lazily row by row. Fine.
    - Another subtle issue: `rows_per_batch = max(1, (8*1024*1024)//len(row))` → "~8 MiB" claim ✓ but `row` itself is allocated as `width*4` up front (8192*4 = 32KB fine; but if someone calls make_thin_png(65000, 10) row = 260KB, fine).
    - One real gap: the docstring claim "No full-size allocation happens in the factory" is TRUE after the fix, but the *test* using rows=1 is a truncated payload (documented). Fine.
    - No interlace, bit depth 8 ✓. Uses single IDAT chunk; PNG allows up to 2^31-1 ✓.
    - Memory peak: batch (~8.4MB) + compressed parts. ✓ So the fix to the circuit-broken factory is correct. Good — I can confirm owner claim 2's second half via static reading.

13. **`_reader_error_detail` truncation semantics**: `text[:_ERROR_DETAIL_MAX_CHARS] + "..."` → max 303 chars. Test asserts ≤400. Fine. But "截 300 字符" claim: the truncation yields 303 chars. Minor.

14. Handoff §0: "回填 owner 先读 diff 核实方向再实跑" — process claim.

15. **Provenance of the half-finished work**: the owner adopted the `importing.py` fix "零修改" from the circuit-broken agent's uncommitted work. Static review can't attribute authorship. Note: the review is of the delivery; fine. But one risk: the "采纳零修改" means the argument comment is the previous agent's; no issue.

16. **taskdoc `delivery_head: a5c8adf1`** added to frontmatter but the handoff also exists; tip=02f306ea docs commit. Fine.

17. Is `QImageReader.setAllocationLimit` available in Qt 6.5+? PySide6 6.11.2 ✓. But the app's minimum PySide6 version? If the product targets an older PySide6 (<6.5), `setAllocationLimit` doesn't exist → AttributeError. Let me check the project's dependency pin (pyproject / requirements). The task says "Qt 6.5+ API 具备". Let me grep for PySide6 version pin in pyproject.toml.

That's an important finding candidate: if pyproject allows PySide6 <6.5, the unconditional call breaks. Let me check.

18. Also check: is `importing.py` truly the only QImageReader use site? grep for QImageReader in src.

19. Check `ImageDecodeError` type — typed error; the application port. Also check whether ImportImagesUseCase maps it to `failed` with detail. Let's read service.py to confirm the detail flows into report.failed and thus verify-k07's entry. Also whether `ImageDecodeError` is caught. Let me grep.

Let me now do a batch of greps/reads:
- pyproject.toml for PySide6 pin
- grep QImageReader in src
- grep allocationLimit across repo (to see other setters / expectations)
- tests/library listing (glob) to judge full-suite scope
- doc/TA3-B2 quality report for F2 caliber wording
- application/importing/images/service.py (decode path + error handling)

Let me batch.
dsh: reasoning:
Important: `tests/library/test_import_images.py` exists and likely uses `helpers.QtImageDecoder` fake (line 117 in helpers) or the production one. Also `tests/library/conftest.py` exists — maybe it adds sys.path. Note the four-suite command runs `tests/library/test_production_adapters.py` only, not the whole `tests/library` dir. So `test_import_images.py`, `test_book_crud.py`, etc. were not in the "517→521" claim. That supports my P3 finding about regression scope.

Wait, the handoff says "四套件 517→521+1skipped". tests/providers, tests/core, tests/m2_acceptance plus test_production_adapters.py. So tests/library's other 6 test files are excluded. Hmm. Let me check the repo's canonical test command — maybe in doc/09_COLLABORATION.md or a Makefile/pytest.ini. Let me find pytest config and the "main 509+1skipped" claim source. Let's look at conftest.py in tests/library to understand the Qt fake usage, and check whether tests/library/test_import_images.py uses the production QtImageDecoder (which would be affected by the change... no, it's a fake on line 117 `class QtImageDecoder` in helpers — wait, helpers defines a fake QtImageDecoder using QImage.fromData. Hmm, that's interesting: helpers has QtImageDecoder as a *fake* that bypasses importing.py. Interesting but unrelated.

Hmm wait, actually is there a naming collision? tests/library/helpers.py line 117 defines `class QtImageDecoder` with `decode` using `QImage.fromData`. And test_production_adapters.py imports `QtImageDecoder` from `infrastructure.importing` (line 13-16) — so no collision there. Fine.

Now: the important question — does `tests/library/test_import_images.py` import the production QtImageDecoder? Let's check quickly. Also check pytest.ini/pyproject location (maybe pyproject.toml doesn't exist; find config).

Also I should check the F2 caliber upgrade implications: the TA3-B2 quality-report.md still says F2 is 推断口径 with "原始 Qt 日志未归档" — the owner did NOT update quality-report.md (it's TA3-B2's artifact; the task AC4 says "F2 的「推断」口径可升级为一级证据（复跑 K09 原始错误归档，若顺带）"). The owner claims the upgrade in handoff/task but did not modify verification/M2-TA3-B/quality-report.md (not in allowed surface? Allowed surface lists verification/M2-IMPORT-ALLOC-LIMIT/** only, and TA3-B2 experiments are forbidden). So the caliber upgrade is registered in the new task docs only, leaving the TA3-B2 report's F2 row still saying "推断" — a doc consistency gap: the original claim site isn't updated, and the "一级证据" claim is now in a different artifact. Is it forbidden to touch quality-report.md? 禁改面: TA3-A/B experiments (handoff §6 says "TA3-A/B experiments" untouched). quality-report.md is verification/M2-TA3-B/ — handoff says "TA3-A/B experiments" not touched; verification/M2-TA3-B/ is arguably part of TA3-B2 artifacts and not in the allowed list. So the owner correctly left it; but the upgrade claim needs a pointer/cross-reference. Worth a P3/P4 finding: the caliber upgrade is asserted in the new task/handoff, but TA3-B2 quality-report F2 row still labels it 推断 — either an integrator note should be added there (new artifact) or the handoff should explicitly note the original site is untouched (it does say F2 caliber upgraded; ambiguous). Also, importantly, the handoff claims "已归档进 JSON 附带复现命令" — but the JSON has no stderr and no repro command. That's the stronger finding (evidence overclaim).

Also — the "原始 Qt 日志未归档" gap that motivated the upgrade: the owner says the stderr categorized log was archived. But it's NOT in the JSON. Let me double check by reading the actual JSON file in the worktree (the diff is authoritative but let me confirm identical).

Also I should verify the Qt version claim "PySide6 6.11.2" — hmm, PySide6 6.11 doesn't exist yet? As of 2025, PySide6 versions: 6.5–6.9... 6.11.2 hmm. Qt 6.11 is plausible for 2026 (the doc dates say 2026-10-01). So fine.

Let me check the environment venv to see the installed PySide6 version statically (site-packages dir names) — that would be a nice static verification of the Qt version and that setAllocationLimit exists in the installed PySide6. I can read the venv's PySide6 package files: G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Lib/site-packages/PySide6/QtGui.pyi — grep for setAllocationLimit. And check the version in `PySide6/__init__.py` or `PySide6/_config.py`. Let's do that — good static evidence.

Also I can statically check whether `QImageReader.allocationLimit` default is 256 by inspecting the .pyi docs? Not needed; but I could grep the PySide6 QtGui.pyi docstring for allocationLimit which may include the doc text. Let's try.

Also check pyproject/requirements for PySide6 pin. Let me find files: glob for pyproject.toml, requirements*.txt, setup.cfg at worktree root.

Let me batch these.
dsh: reasoning:
PySide6 QtGui.pyi has `allocationLimit()` at line 3246 — let me see the surrounding lines to find setAllocationLimit and the version. Let me read that region.

Also read requirements.txt for PySide6 pin, pytest.ini.
dsh: reasoning:
PySide6 pinned ==6.11.2 → the API availability claim holds (and Qt version is pinned, so no <6.5 risk). Good — that closes one potential finding: dependency pin guarantees `setAllocationLimit` exists. Let me confirm `setAllocationLimit` is in the .pyi (grep only found allocationLimit at 3246; setAllocationLimit not found?!). The grep for "allocationLimit" should match "setAllocationLimit" as substring. Only 1 match → `setAllocationLimit` may NOT be in QtGui.pyi! Hmm. That's interesting. Wait, grep found only line 3246 `def allocationLimit() -> int: ...`. If `setAllocationLimit` existed in the .pyi, the pattern "allocationLimit" would match it too. So the stub lacks setAllocationLimit?

Hmm, maybe the static method is declared differently, e.g. `def setAllocationLimit(mbLimit: int, /) -> None: ...` — that contains "AllocationLimit" with capital A, so my regex `allocationLimit` (lowercase a) would not match `setAllocationLimit`! Right — "setAllocationLimit" contains "AllocationLimit" (capital A after "set"). My pattern was lowercase "allocationLimit", which matches only `allocationLimit()`. Case sensitivity. So I need to grep case-insensitively for "allocationlimit".

Let me redo with pattern "(?i)allocationlimit".

Also check the PySide6 version file and whether QtGui.pyi has setAllocationLimit declared. And maybe check the binary Qt GUI library for the symbol? Not necessary.

Let me also check the docstring of setAllocationLimit in the .pyi? .pyi files don't carry docstrings.

Better: check the actual PySide6 docs in the wheel? There may be no docs. But Qt's binary (Qt6Gui.dll) will have the symbol; can't inspect without tools. Could check `PySide6/QtGui.pyd`? No.

Alternatively, there might be Qt C++ headers in the wheel? No.

Another static route: the tests reference `QImageReader.setAllocationLimit` and the owner claims green runs. Static review: I'll accept API existence (Qt 6.5+ documented; pinned 6.11.2) — but I can grep the PySide6 stubs case-insensitively to confirm the binding is exposed.

Let me also look for a `.pyi` chunk file: PySide6 puts large classes' method stubs into `QtGui.pyi` normally. Let's grep case-insensitive.

Also let me check the venv's PySide6 version string file to confirm 6.11.2 statically.

Also useful: check whether `QImageReader.allocationLimit` is documented anywhere else in repo (M2-D1 logs etc.). Not needed.

Next, other checks:
1. tests/library/test_import_images.py — does it use production decoder? Check quickly (grep for QtImageDecoder import).
2. Check `application/importing/images/service.py` to confirm decode failure detail flows to `failed` entries with `detail` field (verify_k07 uses `f.detail`). Need to confirm field names exist (report.failed[].detail, report.imported[].page/.filename). If fields mismatch, verify_k07.py would crash → evidence invalid. Let me read service.py and ports.py.
3. Check `ManagedFileStorage` constructor + `ensure_layout` and `ManagedCopyStoreAdapter` usage in verify_k07.py (storage.ensure_layout() exists? new_revision_relative_path etc.). If verify_k07.py had API mismatches, it would fail to run — but owner claims PASS. Static check adds value.
4. Check `ImportSource(filename=..., data_provider=...)` signature and `import_files(chapter_id, sources)`.
5. Check `ImageDecodeError` is a subclass of Exception with message = detail (str(excinfo.value) == detail). Read ports.py.

Let me batch these reads.
dsh: reasoning:
Good: `setAllocationLimit(mbLimit: int, /)` exists in the pinned PySide6 6.11.2 stubs (static, per line 3245 context — the @staticmethod at 3245 applies to allocationLimit; line 3280's setAllocationLimit — need to confirm it's static too. Let me read 3275-3285 to check for @staticmethod decoration.)

Also verify_k07.py field usage matches ports: FailedImport(filename, reason, detail) ✓; ImportedPage(filename, page) ✓; Page has width/height/source_size_bytes/managed_original_ref ✓ (need to confirm Page fields; service.py constructs with those names, so they exist).

Also `ImportSource.data_provider` ✓ and `import_files(chapter_id, [sources])` ✓. MemorySink implements the three port methods ✓.

Now check `ManagedFileStorage` API: `ManagedFileStorage(Path)`, `.ensure_layout()`, `.write_temp`, `.verify_temp`, `.new_revision_relative_path(book, chapter, kind, uuid_hex, suffix)`, `.publish`, `.discard_temp`. verify_k07.py uses `storage.ensure_layout()` and passes storage tuple to ManagedCopyStoreAdapter(storage, lambda). Let me verify these methods exist in src/infrastructure/filesystem/managed_storage.py (allowed read). This matters for whether verify_k07.py could have run (evidence validity). Also D03 layout: `books/<book>/chapters/<chapter>/original/<hash>.png` ✓ matches managed ref in JSON.

Let me read managed_storage.py signatures (grep def).

Also let me check the .pyi around 3276-3282 for staticmethod.

Also check whether `tests/library/test_import_images.py` uses the fake decoder from helpers (so not affected) — quick grep.

Also, the whole test suite count: let me find the canonical full-suite command in docs (e.g., doc/09_COLLABORATION.md or README) to judge whether the four-suite selection matches project convention. Grep for "517 passed" or "509 passed" or canonical pytest command in doc/. Let me grep for "m2_acceptance" and "pytest -q" in docs to see convention.

Let me batch: 
1. read managed_storage.py grep def
2. read QtGui.pyi 3274-3284
3. grep test_import_images.py for QtImageDecoder
4. grep docs for canonical test command ("pytest tests" with options).
dsh: reasoning:
Confirmed: the "四套件" excludes tests/library's other 6 test files (including test_import_images.py which exercises the import use case with the *fake* helpers.QtImageDecoder). The task discipline says "基线不回退：main 509+1skipped 0 failed" — where does 509 come from? Let me grep for "509" in doc to find the source of the baseline number. If the canonical full-suite run is `pytest tests -q` → maybe 509+1 skipped... but here 517 for four selections is larger than 509, which is odd: a subset (4 selections) having MORE tests than the full suite (509)? That suggests 509 comes from an older measurement (different time). Let me search "509" in doc.

Actually the task file's 纪律 line likely came from the Task author copying a baseline from Rebaseline Plan/STATUS. Anyway, the point stands: the four-suite selection ≠ full suite; the handoff's "无回归" claim is scoped. I should quantify: tests/library other files (~7 files) + tests/reading_export + others not run. Let me count test files overall to make the finding concrete. glob "tests/**/*.py" and count. Let me get the list count.

Also grep "509" in doc to see provenance.

Let me also check `doc/09_COLLABORATION.md` §review requirements to see if a full-suite requirement exists (e.g., "集成前必须全量 pytest"). And check the Review template for required sections. Let me grep for "pytest" in doc/09_COLLABORATION.md.

Let me batch:
1. glob tests/**/*.py (count)
2. grep "509" in doc/
3. grep "pytest" in doc/09_COLLABORATION.md
4. read QtGui.pyi? done.

Also I want to check the QA/test convention: maybe there's a `tests/run_all.ps1` or a documented canonical command. Grep for "pytest tests" in the repo root docs.

Let me do it.
dsh: reasoning:
Key: doc/STATUS.md says "main 三套件 **509+1skipped 0 failed**" — so the canonical baseline is a **三套件** (three suites), not four. The task纪律 says "基线不回退：main 509+1skipped 0 failed" (三套件 = 509). But the owner ran **四套件** = 517 baseline → 521. So the owner's selection differs from the documented canonical "三套件" (probably tests/providers + tests/core + tests/m2_acceptance = 509) by adding tests/library/test_production_adapters.py (8 tests → 509+8=517 ✓!).

Let me verify: 517 - 509 = 8. test_production_adapters.py has 12 tests in module-level per handoff ("12 passed 文件级")... Hmm, handoff says "绿态 4/4 passed（12 passed 文件级 1.57s）" — meaning the file has 12 tests total. 509 + 12 = 521 = delivery total; 517 = 509 + 8? That doesn't match: baseline 3-suite = 509, plus file baseline (12-4=8) = 517 ✓✓. Yes! Baseline of test_production_adapters = 8 existing tests (12 - 4 new) → 509+8=517; delivery 509+12=521 ✓.

So the numbers are fully consistent, and the canonical "main 三套件 509+1skipped" is intact: the four-suite run = 三套件 + the modified file. So the "基线不回退" discipline is satisfied *in the sense that* the three canonical suites plus the touched file pass. But the four-suite run still doesn't include the other tests/library files. Hmm — the canonical main baseline is 三套件 (providers, core, m2_acceptance) = 509. So excluding other tests/library files is the project's convention (testpaths=tests but they run 三套件). Actually wait, "main 三套件 509+1skipped 0 failed" is what STATUS says — so the project's canonical gate is three suites. The owner added the touched file. Good, that's exemplary. So my earlier P3 finding about scope weakens considerably: the convention itself is 三套件. I should reframe: the owner's four-suite selection = canonical 三套件 + the changed test file, which is *better* than the convention, and numbers reconcile exactly (509+8=517 → 509+12=521). I can even state the reconciliation as a positive verification of internal consistency. But the remaining gap: tests/library other files + tests/reading_export etc. aren't in the canonical gate either — not this task's fault. I'll downgrade to P4/NOT_VERIFIED mention: the 521 doesn't cover other tests/library files (e.g. test_import_images.py) that touch the import path; those should be in the integration-time run. Hmm, actually test_import_images.py uses the helpers fake decoder, so importing.py isn't exercised. Only production_adapters.py exercises QtImageDecoder. Good. But still the integration step could run `pytest tests -q` — I'll recommend that as the integrator closure item.

Wait, but does the *whole* suite even pass? baseline discipline only ever mentions 三套件. So not a finding against the owner. I'll present it as a verified consistency + a suggestion.

Now, the base commit discrepancy: dispatch says base=8996ca55, and handoff says base `8e0de8d0` with commit topology `8e0de8d0 → a5c8adf1`. The task frontmatter says base_commit: 8e0de8d0. And the review diff base is 8996ca55. So which is the parent of a5c8adf1? If the diff base is 8996ca55 and the implement is a5c8adf1, then the diff includes everything from 8996ca55 to 02f306ea. Hmm, but the half-finished work was *uncommitted* in the workspace at 8996ca55. "回填 owner 先读 diff 核实方向再实跑" — so a5c8adf1 might have been created on top of 8996ca55 (the previous worktree HEAD). Then the handoff's stated base "8e0de8d0" and topology "8e0de8d0(base) → a5c8adf1" would be inaccurate unless 8996ca55 == 8e0de8d0... but they're different hashes.

Hmm, possibility: 8996ca55 is the commit *on the branch* that the half-finished agent's worktree was at (e.g., a checkpoint/claim commit), and 8e0de8d0 is the task's declared base_commit. If a5c8adf1's parent is 8996ca55, the handoff topology "8e0de8d0(base) → a5c8adf1(implement)" is misleading/imprecise: it skips 8996ca55. Also then the红态 "stash src 对 8996ca55 基线" is consistent with 8996ca55 being the actual parent.

But the number reconciliation (509 + 8 = 517) suggests the baseline was fine.

Since I can't run git, I can try to read the git logs statically! The worktree's `.git` file points to the gitdir; `.git/logs/HEAD` contains reflog with commit messages. Also I could read `.git/refs/heads/...`. Non-shell static reading of git internals is legitimate. Let me try: read G:/CODEX/New Manga/.git/worktrees/M2-IMPORT-ALLOC-LIMIT-zcode/HEAD and commondir, then the branch ref file, then logs/HEAD.

Careful: reading `.git` internals is read-only. Let's do it — it gives verifiable commit hashes.

Let me glob the worktree git dir.
dsh: reasoning:
The glob for .git/worktrees found no files — maybe glob excludes hidden/ignored? The tool says it includes hidden and ignored files. But it returned nothing. Perhaps the glob path needs the pattern to match; let's try pattern "*" or specific files: read G:/CODEX/New Manga/.git/worktrees/M2-IMPORT-ALLOC-LIMIT-zcode/HEAD directly.

Hmm, but the sandbox is workspace-write scoped to "G:\CODEX\New Manga" — reading .git should be allowed (read is allowed anywhere? file policy workspace-write means writes restricted; reads were fine for .worktrees paths).

Let me try reading HEAD and logs/HEAD.
dsh: reasoning:
Excellent — this settles the topology:
- Worktree created at 8996ca55 (initial checkout) — the first reflog entry is "0000... → 8996ca55" with no message (worktree checkout).
- 8996ca55 → a5c8adf1 (implement commit), so a5c8adf1's **parent is 8996ca55**, NOT 8e0de8d0.
- a5c8adf1 → 02f306ea (docs commit) = tip.

So the handoff's claim "commit 拓扑：8e0de8d0(base) → a5c8adf1(implement)" is **factually wrong**: the implement commit sits on 8996ca55. The task frontmatter also declares base_commit: 8e0de8d0. Is 8996ca55 == 8e0de8d0? No, different hashes. So either the task's declared base_commit is wrong, or the handoff's topology is wrong. The dispatch itself says base=8996ca55. So the discrepancy is real and should be flagged (P3, documentation/traceability).

Is this a substantive issue? It matters for scope: the diff base 8996ca55 is what review-input.diff was computed from (7 files). If a5c8adf1's parent is 8996ca55, then the implement commit contains only those changes (assuming the diff base is 8996ca55). But the declared base_commit in the Task frontmatter (8e0de8d0) is the *authorized* base — meaning the owner was supposed to start from 8e0de8d0, but the worktree was at 8996ca55 (which includes whatever commits between 8e0de8d0..8996ca55, e.g. master advance or another task's integration). Is 8996ca55 an ancestor/descendant of 8e0de8d0? I can check: read the main repo's reflog/log for those commits, or check `.git/logs/refs/heads/master`. Actually the review-input.diff's base is what matters and it shows only 7 files, so the extra commits between don't add changes in this diff — but they might be *other* work (merged). Since the Task says base_commit 8e0de8d0 and worktree at 8996ca55, if 8996ca55 is a descendant of 8e0de8d0 on master (e.g., the release commit 69137837 → ... ), then the owner started from a later point than declared, which the project actually allows ("分支按窗口规则 git merge master 快进" in other tasks). Not necessarily a violation, but the handoff should state it accurately.

Actually, wait. Let me reconsider: maybe the worktree was created *at* 8996ca55 which IS the task's branch base (declared as 8e0de8d0 in the task file, possibly wrong metadata written by Codex). Let me check the master log to see the relationship: read G:/CODEX/New Manga/.git/logs/refs/heads/master (or HEAD) and grep for 8996ca55 and 8e0de8d0. Reflog lines record old→new, so I can find entries.

Let me grep those hashes in .git/logs.

Also — the handoff §3 claims red state was run "对 8996ca55 基线" which is consistent with the actual parent ✓ (so the red-state baseline is the real parent, good).

But the handoff ALSO says in §0 that the half-finished work was "留在 8996ca55 工作区的半成品（未提交）". And the reflog shows the worktree was created at 8996ca55 with two "reset: moving to HEAD" entries — consistent with an abandoned agent that perhaps did `git stash`/`reset`. OK.

Now, are the red-state runs trustworthy? The stash claim: `git stash src` — hmm, "git stash" of src only then run tests. Since the diff base is 8996ca55 and the tests are new (untracked or committed?), stash wouldn't include untracked files by default. But owner said "git stash src 后对 8996ca55 基线跑新测试" — plausible: they committed both src+tests in a5c8adf1? No — the red run happened before committing; the half-finished work was uncommitted: modified importing.py + tests/helpers.py + tests/test_production_adapters.py. To get "baseline src + new tests" they'd stash the src file only: `git stash push src/infrastructure/importing.py` → reverts src, keeps test changes. That works. Fine, and it's the natural method. Cannot verify runtime.

Now let me check the commit contents statically to verify "7 files" and "禁改面零触碰" independently: the diff base is 8996ca55 and a5c8adf1. I can't run git show. But I can inspect the git *tree* objects? That's heavy (zlib). Alternative: `review-input.diff` is presumably the full `git diff 8996ca55 02f306ea` — I can count the files in it: 7 (handoff, task, verify_k07.py, importing.py, helpers.py, test_production_adapters.py, verify-k07.json). I'll take the diff as the review object scope and note that verifying the diff completeness (no other modified/untracked files in the worktree) requires git → NOT_VERIFIED (porcelain clean claim).

Hmm, but I could check for stray untracked files by comparing the worktree against... no. Skip.

Now let me check master log to resolve 8e0de8d0 vs 8996ca55 relationship. Let me grep in .git/logs for both hashes.

Also, the reflog shows author "peakwheat-pixel" (user's account) for the commits — normal for the machine.

Let me also confirm the reflog of the branch ref (logs/refs/heads/agent/zcode/M2-IMPORT-ALLOC-LIMIT) to see branch creation base — that shows where the branch was created (from which commit), which is the strongest evidence of base. Let me read it.
dsh: reasoning:
Now the topology is fully resolved:
- master: ... → 8e0de8d0 (close M2-TA3-B2) → 8996ca55 (release 4-task batch: activates the four tasks).
- Task branch created from 8996ca55 ("branch: Created from HEAD").
- So the actual authorized base for the branch is 8996ca55 (the release commit that activated the task), while the Task frontmatter says `base_commit: 8e0de8d0`.
- The handoff §0 says "base `8e0de8d0`" and topology "8e0de8d0(base) → a5c8adf1(implement)" — this is **wrong**: parent of a5c8adf1 is 8996ca55. Note that the task file's base_commit field was presumably written by Codex when creating the Task (8e0de8d0 = the state before the release commit). So the Task metadata itself was already "8e0de8d0" before delivery, and the diff base given by dispatch (8996ca55) is correct. So the owner's handoff topology claim is inaccurate/自己加的.

However: note the release commit 8996ca55 came *after* 8e0de8d0 and only added doc/Task files presumably (release batch: Task skeletons + STATUS/PLAN). If 8996ca55 touched doc/tasks/M2-IMPORT-ALLOC-LIMIT.md etc., then the review diff base 8996ca55 is fine. The important thing: the review diff (8996ca55→02f306ea) shows the task doc as an *existing* file being modified (index cb4d10a0..070b959e) ✓ consistent with the Task being created at 8996ca55.

So the finding: Task frontmatter `base_commit: 8e0de8d0` and handoff §0 "base 8e0de8d0 / 拓扑 8e0de8d0 → a5c8adf1" are inaccurate; the actual branch base and diff base is 8996ca55 (release commit). Not fatal for the code, but it's a traceability defect (P3): the declared base ≠ actual parent, and the review evidence header should state the true parent. Also the red-state claim "对 8996ca55 基线" is the *correct* one, contradicting the handoff's own §0/base line. Internal inconsistency in the same document. Good finding.

Also: the release commit 8996ca55 was the branch creation point; the half-finished work was uncommitted in that worktree → consistent.

Now, let me also verify the commit message claim in the reflog: a5c8adf1 = "raise Qt decode allocation limit to 2047 MiB with typed reader-error detail; fix F2 webtoon import rejection" ✓.

Now, is the half-finished work in the same worktree (8996ca55) authored by "熔断 agent"? The reflog shows no stash entries (stash isn't in HEAD reflog anyway; stash has its own log). Let me check .git/logs/refs/stash — if stash was used for the red run, there'd be entries. Let's check. That would corroborate the red-state method. Let me read G:/CODEX/New Manga/.git/logs/refs/stash if exists. Actually the worktree shares .git; stash log at .git/logs/refs/stash.

Also I can check whether a stash still exists (dangling) — not needed.

Let me now also verify the F2 caliber claim by reading the TA3-B2 quality-report F2 row (already seen via grep: line 141 says 推断口径 and "原始 Qt 日志未归档"). The owner did not update it (not in the allowed surface). The Task AC4 says "F2 的「推断」口径可升级为一级证据（复跑 K09 原始错误归档，若顺带）" — AC4 satisfied if the new artifact archives the raw Qt log. The new JSON does NOT contain the stderr log line, and does not contain the command. The handoff claims it's archived. That's the key evidence-quality finding (P2): the artifact lacks the discriminating evidence; the "一级证据" claim is not verifiable from the artifact. The verification JSON only has errorString='Unable to read image data' for the control, which is *not* limit-specific.

Hmm, let me double check the actual JSON file in the worktree (maybe the diff truncated something, or the file has more content than the diff hunk — the diff says new file with @@ -0,0 +1,69 @@ — 69 lines, and the content we saw matches 69 lines with no trailing newline). Let me read the actual file to be sure (also to note the missing trailing newline → `git diff --check` wouldn't complain about that but "\ No newline at end of file" is in the diff).

Also I want to check if there's an archived stderr log elsewhere in the worktree (e.g. verification/M2-IMPORT-ALLOC-LIMIT/*.log). Let me glob that dir.

Let me also check the experiments dir for the verify script — is there anything else (e.g. a log file)? glob experiments/M2-IMPORT-ALLOC-LIMIT/**.

Let me batch.
dsh: reasoning:
No stash log → the "git stash" red-state method left no trace in stash reflog. Hmm, if they used `git stash push src/...` and later `git stash pop`, the stash reflog (.git/logs/refs/stash) would have entries. It doesn't exist at all → either no stash was ever created in this repo, or the stash ref log was removed... Actually `git stash pop` on the last stash deletes the ref and (I believe) git removes the reflog file for stash? When the stash list becomes empty, git deletes `refs/stash` and its reflog file. Yes — `git stash pop` of the final stash drops the ref; the reflog file is removed too (git prunes logs for deleted refs). So absence is consistent with a fully-popped stash. Weak evidence either way; can't verify. Let me check `.git/logs/refs/` for other stale stash logs... no.

Another possible stash trace: dangling objects from the stash commit would remain in .git/objects but unreferenced (and maybe in `git fsck` only). Can't scan. Actually — could I find the stash commit? `.git/ORIG_HEAD`? Let me check .git/ORIG_HEAD, .git/MERGE_HEAD, and `.git/worktrees/.../ORIG_HEAD`. Not conclusive.

I could check whether loose objects exist under .git/objects/?? that correspond to stash commits — glob .git/objects/*/*... infinite. Let's check if the repo is packed (objects/pack). Skip — this is beyond static review value. I'll record the red-state method as reasonable but NOT_VERIFIED (cannot replay), and note that no stash reflog remains (consistent with a popped stash; no corroborating artifact).

Hmm, one improvement: the red-state evidence has no archived log file (no `.log` under verification/M2-IMPORT-ALLOC-LIMIT). So the 3-failed claim is not archived — only asserted in handoff. Given the project's review conventions (evidence archived), worth a P3 finding: red-state output not archived as an artifact (no pytest log), only prose in the handoff. Compare: other tasks archive logs under verification/. Reasonable finding.

Now let me double-check a few technical points for the argumentation chain:

(a) Is 0 really "disable" in Qt? Qt docs for `QImageReader::setAllocationLimit(int mbLimit)`: "Sets the allocation limit to mbLimit megabytes. This limit is applied to images read with QImageReader... The limit is applied to the image size... Set to 0 to disable the limit." Actually the docs: "A value of 0 means no limit." I'm fairly confident. Also `allocationLimit()` default 256. ✓

(b) Qt int parameter: `int mbLimit` — 2047 fits ✓.

(c) Does the limit apply to *decoded* size (width*height*depth)? Qt's implementation: `QImageIOHandler::allocateImage()` checks `QImageReader::allocationLimit()` against `size.width()*size.height()*depth/8` (approximately, with overflow guard). Qt docs: "The limit is specified in megabytes and applies to the total size of the image data (width × height × depth/8)." So 690×110000×4 = 303.6e6 B = 289.5 MiB > 256 MiB ✓ rejected pre-fix.

(d) Interesting subtlety: the size check uses integer arithmetic; for 8192×65536×4 = 2^31 exactly = 2147483648. Qt's implementation may guard overflow with `qMulOverflow` and reject as "too big" for 32-bit size (QImage max is 2^31-1 bytes? Actually QImage can't exceed ~2GB total on 32-bit size). On 64-bit Windows, QImage uses qsizetype (64-bit) internally but the allocation limit is int MB. `QImageReader::allocationLimit` check: in qimageiohandler.cpp:
```cpp
static bool qt_imageio_shouldCheckAllocationLimit() ...
bool QImageIOHandler::allocateImage(QSize size, QImage::Format format)
{
    if (size.isEmpty()) {...}
    const qsizetype totalBytes = ...;
    if (totalBytes > allocationLimit*1024*1024) return false
}
```
Hmm, also there's a check: `if (!size.isValid()) return false;` — QSize validity on 64-bit is fine for 8192×65536? QSize uses int (32-bit) coordinates; 65536 and 8192 fit in int ✓. So the limit check rejects at 2048 > 2047 MiB ✓ (if the comparison is `>`; if `>=` also rejects). Good.

But hold on: for the fail-closed test, is the *declared* total 2048 MiB computed as 8192*65536*4 = 2147483648 bytes, and 2047 MiB = 2146435072 bytes → 2147483648 > 2146435072 ✓ rejected. Fine.

Now what if the PNG handler's allocation-limit rejection happens only when the *handler* supports it? In Qt 6.5+, `QImageReader::read()` also has a fallback check? The Qt docs note: "This limit is applied to QImageReader, but not to QImage::loadFromData / QImage::fromData"? Hmm — I recall: "QImageReader::allocationLimit ... The limit also applies to QImage::loadFromData() and QImage::fromData()"? Let me think. There's a doc sentence in Qt: "Note: The limit is applied to all QImageReader instances, including those used indirectly by QImage::loadFromData()." I'm not certain. Actually I recall the opposite nuance: `QImage::loadFromData` uses QImageReader internally with default auto-detect, so it inherits the global limit. For safety in my review, I'll phrase the MOBI finding conditionally: "if the global limit also governs `_MobiDocumentHandle.render_page`'s `QImage.loadFromData` (QImage 内部使用 QImageReader)", which is almost certainly true. Let me try to find hard evidence in the wheel: maybe PySide6 ships Qt docs? No. Could check QtGui.pyi for QImage.fromData docstrings — .pyi has no docstrings.

Maybe there is a Qt documentation file in the repo (doc/research) mentioning allocationLimit. Or check the Qt source in the venv? No source.

I can hedge appropriately: "若 `QImage::loadFromData`（内部 QImageReader）也受该全局上限约束（Qt 6.5+ 的分配上限是 QImageReader 静态全局）" — the static global is inherently process-wide for QImageReader users. For QImage::loadFromData the question is whether it goes through QImageReader with the limit. In Qt 6.5+, `QImage::loadFromData` → `QImageReader reader(device)` … yes it does. I'm reasonably confident. I'll mark as P3 with a conditional and recommend the cheap defense (re-assert a tighter bound in `_MobiDocumentHandle.render_page` or document the widened envelope).

Hmm, wait. Is there a real risk that this global change breaks another *existing test* expectation? e.g. tests/import_formats/test_mobi_import.py — if a test asserts rejection of a large declared MOBI image... unlikely.

Now (e): one more important check on the "test 1 sets 256 then decode re-asserts 2047" design: the test name says "beyond_qt_default_cap" and asserts success. With the fix, decode sets 2047 → success ✓. Good, this is a genuine red→green test.

But hold on: is `QImageReader.setAllocationLimit(256)` at line 89 *itself* a problem — it mutates the process global; the autouse fixture restores `before` (captured at test setup) → after this test the global returns to whatever it was (likely 256 or 2047). If another test module assumed default 256 later in the same session, it's restored ✓. Good discipline. But if the fixture's captured `before` is 2047 (leaked from a prior test in the same module that ran decode without the fixture... all tests in this module have the fixture), fine. Cross-module: tests/import_formats/test_mobi_import.py might run after and get 252... no, restored. OK.

Actually one real subtlety: the fixture restores `before`, which for the *first* test in the module may be the leaked 2047 from another module that used the production decoder earlier in the session — that's fine (idempotent).

(f) `monkeypatch.setattr(QImageReader, "setAllocationLimit", lambda mb: calls.append(mb))` in test 2: monkeypatch on the *real* PySide6 class attribute. PySide6 static methods are settable? In PySide6, setting an attribute on a class object defined in C++/shiboken — `setattr` on a Shiboken type... Shiboken types generally allow attribute assignment (they have a dict). `monkeypatch.setattr` on a Shiboken class should work (tests already do `monkeypatch.setattr("PySide6.QtGui.QImageReader", UnknownFormatReader)` which sets the module attribute, not the class). Hmm — test 2 sets the attribute on the *class object* `QImageReader`. If Shiboken types are immutable (like some builtins), setattr raises TypeError → test would error, not pass. The owner reports green 4/4, so presumably it works. But note the risk: patching a C++ static method on the class with a Python function — when called via `QImageReader.setAllocationLimit(2047)`, Python looks up the class dict → the lambda is a plain function, so it becomes a bound method? No — for a class attribute lookup `QImageReader.setAllocationLimit`, a plain function accessed on the *class* (not instance) returns the plain function in Python 3 (functions are descriptors, but `Class.func` returns the plain function, no binding). So `QImageReader.setAllocationLimit(2047)` calls lambda(2047) → calls.append(2047) ✓. Good.

But wait — does the monkeypatch of the *class* attribute take effect given `decode()` does `from PySide6.QtGui import QImageReader` inside the function? It imports the same class object → yes, class-level patch visible ✓. Good.

And test 4 patches the module attribute `PySide6.QtGui.QImageReader` → the in-function `from ... import` picks up the fake ✓. But careful: the fake `LongErrorReader` is a class; `decode` calls `QImageReader.setAllocationLimit(...)` → staticmethod ✓; `QImageReader(buffer)` → `__init__(self, device)` ✓; `reader.format()` ✓; `reader.read()` ✓; `errorString()` ✓. Good.

Note test 4's fake class name shadows; fine.

(g) The autouse fixture also runs for `test_qt_image_decoder_raises_allocation_limit_above_qt_default` which monkeypatches the setter; the fixture's teardown calls the *restored* real setter (monkeypatch undo happens... ordering!). Fixture teardown vs monkeypatch teardown order: monkeypatch is a function-scoped fixture; teardown order is reverse of setup. `_restore_qt_allocation_limit` is autouse; monkeypatch is requested by the test. Setup order: autouse fixtures are instantiated... hmm. For a test requesting both `monkeypatch` and the autouse fixture, the ordering depends on scope/dependencies: autouse fixtures are set up before the test's explicitly requested fixtures? Actually pytest orders: higher-scoped first; within same scope, autouse fixtures are instantiated before non-autouse ones that the test requests. So setup: `_restore_qt_allocation_limit` (captures before, yields), then `monkeypatch`. Teardown: reverse → monkeypatch undo first (restores real setter), then the autouse fixture's post-yield code calls the real setter ✓. So no error. 

But hmm, in test 2, the fixture captured `before = QImageReader.allocationLimit()` (real) and restores real setter with `before` ✓.

What if the order were reversed (fixture teardown runs while setter is still monkeypatched)? Then `QImageReader.setAllocationLimit(before)` would call the lambda → appends, no restore, and monkeypatch undo would then restore the real setter but the global value stays 256 (test 1 leaked? no, test 1 set 256 then decode set 2047 → global 2047; fixture restores to `before`). Edge case only. Actually if `before` capture happens while the class setter is patched (impossible—fixture setup precedes patch), fine.

So test design is sound.

(h) `_reader_error_detail` truncation: `text[:300] + "..."`. Test asserts `detail.startswith("x"*100)` and `len(detail) <= 400` — doesn't assert exactly 303. P4 nit.

(i) The fail-closed test asserts `detail.strip()` non-empty and `len(detail) <= 400` — with errorString "Unable to read image data" (25 chars) ✓. It does NOT assert the detail equals a limit-specific message (Qt doesn't provide one) — acknowledged in docs. But the test comment claims "typed failure with the reader's own error text, never a process kill" — it can't prove "never a process kill" from a single run, but pragmatically ok.

(j) 2047 vs 2048: The test's declared 2048 MiB error is right at the boundary, so the test's rejection *does* depend on 2047 vs 2048 (if the constant were raised to ≥2048 MiB, the limit check would pass and the decode would proceed → then it would fail on truncated IDAT anyway → still ImageDecodeError!). So indeed the test cannot catch a limit raised to 4096. Confirms the tautology finding. Good — and I can state precisely: the same assertion passes for limit=4096 (truncated IDAT fails) → no red signal for AC1's "fail-closed above limit" property. Also note: if the constant were raised to e.g. 100_000 MiB, the test still passes. So test 3 provides zero protection against the "unbounded OOM" risk that the rationale explicitly guards against. That's a meaningful P2.

Concrete remedy suggestion: 
- Option 1 (cheapest): assert the mechanism in the test by checking that the same payload is accepted when the limit is raised above 2048 MiB... not possible (truncated). 
- Option 2: use a *complete* PNG whose declared size exceeds a *temporarily lowered* module bound: e.g. monkeypatch `importing._ALLOCATION_LIMIT_MIB` to 1, then `decode(make_thin_png(690, 4000))` (a complete, valid small-ish PNG with full rows; 690*4000*4 = 11 MB > 1 MiB) → asserts rejection *and* that the same bytes decode fine at 2047 → strictly isolates the limit as the deciding factor. Note: monkeypatching the module constant requires decode to read it at call time (it does: `QImageReader.setAllocationLimit(_ALLOCATION_LIMIT_MIB)` reads the module global at call time; monkeypatch.setattr(importing, "_ALLOCATION_LIMIT_MIB", 1) works ✓).
  This gives a genuine mechanism lock with tiny memory (11 MB). Excellent suggestion.
- Option 3: for the >2047 path, additionally capture Qt's categorized log via `qInstallMessageHandler`/`QLoggingCategory` to assert "exceeds the current allocation limit" appears — but the handler would need registering and the message is from the internal category; doable with PySide6 `qInstallMessageHandler`. Alternatively assert the same payload also fails at 2047 *and* the message via stderr capture isn't available in-process.

I'll recommend Option 2 as the primary mechanism lock (with the exact shape).

(k) `len(data) < 1_000_000` assertion in test 1: For a full-rows thin PNG, compressed size ≈ 300KB for 304MB of zeros at level 9 (zeros compress ~1000:1) ✓ under 1MB. Fine.

(l) Now, another potential functional concern: the decode path now calls the setter *before* creating the reader, which also means for all other formats. No issue.

(m) Does `QtImageDecoder.decode` set the limit before `buffer.open`? Yes, line 92 before QBuffer creation. Fine.

(n) Potential concern about the *degraded* path: `ImageDecodeError(_reader_error_detail(reader))` — Qt's errorString for the allocation-limit rejection is "Unable to read image data", which is generic and does NOT tell the user "image too large for decode limit". AC1 asks for "typed 错误改善" with reader-level原文 — delivered. But for the *product* the user-facing diagnostic for oversize images remains opaque ("Unable to read image data"), meaning a >2047MiB page still fails with a non-actionable message. Since AC1 only asked for reader原文, this satisfies AC1 literally. But it's worth flagging as a product-level P3 observation: the limit rejection is indistinguishable from corruption in the typed detail (Qt doesn't expose it), so UI can't tell "too big" from "corrupt". Recommend registering this as a known limitation (or pre-checking declared dimensions from the header). The handoff does NOT register this as a known limitation — actually handoff §6 registers other items; let me check whether it mentions the errorString opacity... §4 mentions "Qt 的 limit 拒绝原因不进 errorString". It's mentioned in §4, so partially registered. I'll mention as P4/registration nuance.

(o) The `_ERROR_DETAIL_MAX_CHARS = 300` — rationale "r1 R4 ... bounded" ✓. But note: the detail truncation applies to ImageDecodeError detail which the use case passes to FailedImport.detail. Bounded at 303 ✓.

(p) Now check whether `verify_k07.py` really reproduced the TA3-B2 F2 failures at the *import channel* level for the control — the control uses raw QImageReader, not ImportImagesUseCase. So the control does not reproduce "import rejection" but "decode rejection"; the production pass uses the full channel. The attribution "fix made import pass" is supported: the only difference in the decode step is the limit. Actually there IS one more difference: the production run uses `QtImageDecoder` with a QBuffer of the *bytes*; the control does the same. ✓ Good. But the control uses its own QBuffer + QImageReader(buffer) without calling format() first. Format detection differences? `QImageReader(buffer)` auto-detects content by default (autoDetectImageFormat default true) ✓ same as decoder.

Wait — one subtle but *important* attribution gap: the production pass *sets 2047* via the decoder; the control *sets 256*. Both are the same code otherwise. So the causal variable is the limit ✓. This is a valid controlled comparison. I'll credit it. The weakness is only that the rejection reason isn't independently recorded (stderr claim not in artifact) — so the control could theoretically be rejected for another reason (e.g. the raw read without prior format() call... no, that's fine; or memory pressure). Actually a stronger control design would be: same raw reader at BOTH 256 (reject) and 2047 (accept) — i.e., the control should also include a 2047 raw-read pass that succeeds. The current control only shows rejection at 256; the acceptance at 2047 is shown only through the fuller production path. Adding a raw read at 2047 would isolate the limit within one code path. That's a constructive P3 suggestion (evidence design). Because as it stands: production-path-accept(2047) vs raw-path-reject(256) differ in two variables (limit AND plumbing). Minor but real. Good finding for D section.

(q) verify-k07.json field completeness: no `qt_version`/`pyside6_version`, no `python_version`, no `decoded_size_mib` per case, no `mime_type` (AC3/AC1 claim "宽高/mime/managed ref 全登记" — the JSON records width/height/source_size_bytes/managed_original_ref but NOT mime_type! The task AC3 evidence row claims "宽高/mime/managed ref 全登记" — the script never writes mime_type into the JSON (entry has filename/width/height/source_size_bytes/managed_original_ref). The Page entity — does it have a mime type? Looking at service.py: Page(..., width, height, managed_original_ref...) — no mime_type field! DecodedImage has mime_type but the Page doesn't carry it. So the task's claim "宽高/mime/managed ref 全登记" is inaccurate: mime is not recorded anywhere in the evidence (nor is it a Page field). That's a concrete overclaim → P3 finding (evidence field overclaim). Nice catch.

Also the task AC3 row says "K09 690×100480、K10 690×100674 均 imported 零 failed，宽高/mime/managed ref 全登记" → mime missing. Also the Task background said AC3 = "尺寸/宽高登记" — width/height recorded ✓. So the mime claim is an extra overclaim in the evidence table.

(r) Also `verify-k07.py` writes `results` without `qt_version` etc. — for a "一级证据" artifact, environment metadata (PySide6 6.11.2, Python version) is missing; the handoff mentions the venv in §3 but not in the JSON. P4 recommendation.

(s) `results["cases"][case]["path"]` is an absolute machine path ✓ fine for internal evidence.

(t) The script's control loop mutates the global and restores; if `QImageReader.setAllocationLimit(256)` is called *before* the production loop? No, order is fine. But note: the control sets 256 and then the *raw* read. However, one issue: the control is run in the same process *after* the production loop; the production loop's last decode left 2047; then control sets 256 ✓.

(u) `hashlib.sha256(path.read_bytes())` reads the 57MB file *again* after the import — memory spike ~57MB, fine.

(v) Potential issue: `MemorySink.max_source_order` returns `len(self.pages)`, and `add_page` appends → fine for one file per case.

(w) Now, `ImportSource(filename=path.name, data_provider=path.read_bytes)` — `data_provider` reading bytes each call; the use case calls `source.read()` once ✓.

(x) D07 §37 read-only claim ✓ (only reads).

Now let me double check one more claimed item: "importing.py 之外 src 零触碰" — the diff only modifies importing.py in src ✓. And "7 文件全允许面" ✓ (verified from diff file list). I'll verify the count: let me count "diff --git" lines in review-input.diff via grep.

Let me also verify no forbidden path appears in the diff (grep for "src/ports", "src/bootstrap", "doc/contracts", "packaging/", "apps/", "doc/STATUS.md" as diff headers).

Let me run those greps on the diff file.

Also: check `doc/tasks/M2-IMPORT-ALLOC-LIMIT.md` frontmatter base_commit stays 8e0de8d0 (yes, unmodified) — and handoff's claim. Confirmed.

One more: the review prompt says tip=02f306ea (docs). The task doc says delivery_head: a5c8adf1 — consistent (implement head vs docs tip) ✓ and the handoff is named M2-IMPORT-ALLOC-LIMIT-a5c8adf1.md while the handoff commit is 02f306ea — mildly confusing but the handoff file name references the delivery head. Fine.

Let me grep the diff for forbidden paths and count files.
dsh: reasoning:
7 files confirmed. The forbidden-path check: the file list above shows none of the forbidden paths. Good — the diff's 7 files are all in the allowed surface.

Now I have enough for a thorough review. Let me also quickly consider whether an alternative design was ignored that's clearly better (review item 1):

Alternatives:
1. `setAllocationLimit` once at bootstrap/assembly (process startup) — could be seen as cleaner, but bootstrap is a forbidden path for this task, and per-decode re-assert is self-healing. Also note the *existing* code deliberately imports PySide6 lazily inside the method (no Qt dependency at module import) — a bootstrap-level call would force Qt import at startup, contradicting the layering note in TASK-031's review ("PySide6 在 decode() 函数内导入，使模块本身不携带 Qt 依赖"). So per-decode is architecturally consistent. Credit the owner: this alternative is arguably *worse* for this repo.
2. Instance-level: QImageReader has no instance-level allocation limit in Qt 6.5+ (only the static). So "实例级方案" doesn't exist; the closest is a narrower re-assert around the specific decode... which is what they do. Could note the `setAllocationLimit` is static — verified from the stub (`@staticmethod`), so the process-global side effect is unavoidable given the constraint. Good: this is a *verifiable* static fact I can cite (PySide6 6.11.2 QtGui.pyi:3279-3280) — strengthens the review.
3. Derive N from settings — task allows; not done, justified (avoid expanding the settings contract). ✓ acceptable. But: is 2047 hard-coded a problem for the *32-bit* packaging? The product targets Windows x64 (Tauri/Python). Fine.
4. Read `allocationLimit()` and take max(current, needed)? No — that would be unbounded (accept whatever code set). Their unconditional assert is stricter/better.

One more thought on the "965 MiB" extrapolation: also the comment says "690 x ~350k px x 4 B is ~965 MiB" — a page of 690×350,000 px. Where does 350k come from? Not stated (K07 is 131,289). Weak but harmless. Also, if a future page were 690×780,000 px (~2 GiB), it'd be rejected — the handoff §6 registers "若未来出现域内更大页…重新评估入口" ✓ good.

Another point: is the limit a *per-decode* bound? Qt's allocation limit applies to a single image decode ✓ — but the import path decodes then *also* keeps the QImage alive only during decode; the DecodedImage only keeps w/h. Actually, note: the decoded QImage (345 MiB) is alive only within decode() → freed after. But `data` bytes are held (57MB). OK. Also ManagedCopy writes bytes. No retention of the big QImage ✓ (no memory leak introduced by the fix). Good.

Now consider: does raising the limit to 2047 MiB risk *actual* OOM in normal import? A malicious/corrupt PNG declaring 2000 MiB → Qt will attempt to allocate ~2GB and *succeed* if the machine has RAM+swap → potential OOM/thrash at import time. This is the inherent trade-off of any value >256. The rationale acknowledges "corrupt/declared-huge header could OOM" only for the 0 case, implying that 2047 is safe — but the same argument applies at 2047 (a corrupt header declaring 2000 MiB now gets attempted instead of rejected). The comment's "非 0" argument doesn't fully address that a hard bound at 2047 is still a 2 GiB attempt. Worth noting as a P3 argumentation gap: "0 disables the check → OOM" is not a distinguishing argument for 2047 vs, say, 512; the real question is where to set the bound and whether the memory budget (2GB per decode, concurrent imports?) is acceptable. Also note the import loop is sequential (one file at a time) → at most one 2GB QImage at a time plus the file bytes. That should be stated in the rationale (it's implicit in "单次 decode"). The comment does say "keeps any single decode well below realistic 64-bit desktop memory budgets" ✓ but doesn't address *sequential* multiple decodes (fine) or *concurrent* imports (not concurrent today). Reasonable. I'll fold this into a single P3: the 2047 rationale is directionally sound but has two soft spots — (i) the "0 会 OOM" argument is a non-zero argument, not a 2047 argument; the actual justification is the domain bound × margin (2.1×), which relies on an unsourced 350k-px extrapolation and a MB/MiB unit slip (921 MiB, not 965 MiB); (ii) the process-global bleed to other decode paths (MOBI) is unanalyzed.

Let me double-check the unit arithmetic to be precise:
690 × 350,000 × 4 = 966,000,000 bytes.
966,000,000 / 1,048,576 = 921.23 MiB. So "约 965 MiB" should be "约 921 MiB（或 966 MB）". ✓ unit slip.
2047 / 921.23 = 2.222 → margin 2.2× (comment says 2.1×; using the wrong 965 figure gives 2.12). So slight.
Also 2047 MiB = 2146.4 MB.

And K07: 690×131,289×4 = 362,357,640 B = 345.57 MiB ✓ (comment says ~345.6 MiB ✓).
2047/345.57 = 5.92× margin over the *measured* max.

Now, the "2.1× 余量" is over a hypothetical 350k-px page, not over the measured domain max (5.9×). The comment frames 2.1× as "margin over the domain bound" where the domain bound is the extrapolation — acceptable but should be labeled as such. Fine.

One more check on the claim "Qt 6.5+" in the comment: setAllocationLimit was added in Qt 6.5 ✓ (docs say "since 6.5"). The pinned PySide6 6.11.2 satisfies it, and requirements.txt pins `PySide6_Essentials==6.11.2` — note the requirement is PySide6_Essentials; does QtGui live in Essentials? Yes, QtGui is part of PySide6-Essentials ✓ (QtGui is in Essentials, not Addons) ✓. Good — worth noting the pin makes the API guaranteed.

Hmm, one caveat: does `PySide6_Essentials` include QtGui? PySide6-Essentials includes QtCore, QtGui, QtWidgets, QtNetwork, QtQml, QtQuick, etc. ✓.

Now consider test 1's memory: `make_thin_png(690, 110_000)` full rows → decode allocates 289.5 MiB QImage. On a machine with the default 256MiB cap... it *passes* now. And in the same test suite, m2_acceptance tests may run in parallel? No, sequential.

Potential test-suite hazard: `pytest -n auto`? Not used (no xdist mention).

Also: the module-level `pytest.importorskip("PySide6")` at line 10 → skip if PySide6 missing. The fixture imports PySide6 inside the fixture body — autouse fixture applies to all tests in the module; but `pytest.importorskip` already ensures PySide6 present ✓. However `_restore_qt_allocation_limit` is module-level autouse and runs **before** the importorskip? No — importorskip runs at collection (module import), so the whole module is skipped before fixtures ✓.

Now, what about `pytest.ini` marker "slow: long-running tests (sparse 256 MiB streaming)" — there's an existing marker for a 256MiB test. Let me check if some existing test uses `make_png` sparse/256MiB streaming and whether the new autouse fixture interferes... The new tests aren't marked slow; test 1 allocates ~290MiB and takes ~1s. Reasonable but could be marked `slow` given the repo has that marker. P4 suggestion: mark test 1 `@pytest.mark.slow` to keep the fast suite fast (the repo already has that marker for a 256MiB streaming test). Nice concrete suggestion. Let me check what uses the slow marker to make the suggestion accurate.

Let me grep for "mark.slow" in tests.

Also check: is there an existing test that asserts Qt's default allocation limit value (which would now be affected)? grep for "256" in tests/library. Let me do a final batch of greps:
- grep "mark.slow" in tests
- grep "allocation" in tests (done)
- grep "make_thin_png" usages (only the new test)
Then write the review.

Also: should I check the Task template review format? The prompt gives the output format explicitly — follow that.

Let me run the last greps.
dsh: reasoning:
I have all I need. Note one more thing: `verify_k07.py` imports the *private* `_ALLOCATION_LIMIT_MIB` from production code — acceptable for an experiment, minor.

Also: is `helpers.py` (tests/library) in the allowed surface? "tests/（import 相关）" ✓.

One more consideration regarding "porcelain 干净" claim: cannot verify (no shell) → NOT_VERIFIED. But I could partially check: are there uncommitted modifications? Can't without git. Note also the presence of `.git` worktree reflog shows the last reflog entry is the docs commit → no commit after 02f306ea ✓ (tip consistent with dispatch tip=02f306ea ✓). That's a nice static confirmation: the worktree's branch ref points to 02f306ea (the last reflog entry new-hash) and the branch ref file... let me verify the branch ref content = 02f306ea. The branch ref lives in the common dir `.git/refs/heads/agent/zcode/M2-IMPORT-ALLOC-LIMIT` (or packed-refs). Let me read it — quick and strengthens verification that tip=02f306ea matches.

Let me also check `.git/refs/heads/agent/zcode/M2-IMPORT-ALLOC-LIMIT`.

Actually the reflog is enough evidence, but a ref read is cheap. Let me do it, plus check if `git status` dirty-ness could be inferred... could I stat file mtimes? Files modified after the commit time (1790862214 = ?) — let me convert: 1790862214 epoch → 2026-10-01? 1790862214 / 31556952 ≈ 56.75 years after 1970 → ~2026.7 → Oct 2026 ✓. If worktree files have mtime newer than the last commit (1790862312 = tip commit time), that suggests edits after commit. But reading the *index* to compare hashes requires parsing .git/index (binary, doable but ugly). Let me try a targeted approach: read the branch ref, and check mtime of importing.py vs tip commit timestamp? mtimes aren't a reliable dirty indicator (checkout sets mtime at checkout/commit time). Actually if a file was modified after the last commit, its mtime > tip commit time (modulo clock). I can't get mtimes without shell... `read` doesn't give mtime. The glob tool returned modification-time ordering earlier but not timestamps.

So: porcelain clean → NOT_VERIFIED. Fine, acknowledged.

Let me read the branch ref to confirm tip.
dsh: reasoning:
Confirmed: branch tip = 02f306ea ✓ matches dispatch. Parent chain 8996ca55 → a5c8adf1 → 02f306ea ✓ (from reflog).

Now let me write the review. Structure per required format:

## Verdict
## 逐项核对表（A 修复方案论证 / B 红绿证据 / C 测试质量 / D 真图验证 / E 范围纪律）
## Findings（R1…，P0-P4，文件:行）
## NOT_VERIFIED（集成方运行时项）
## 集成方闭合清单
## 推荐下一步（一句）

Verdict: approved_with_conditions? Since findings are P2/P3 (no P0/P1, no functional defect), I'd give `approved_with_conditions` (条件通过): conditions = R1 (fail-closed 测试机制锁定 or 登记为已知的不锁定), R2 (stderr/复现命令归档修正 or 撤销 overclaim), R3 (base/topology 更正). Let me settle severities:

Findings list:
- R1 (P2): fail-closed test does not lock the mechanism; tautological under truncation; provides no protection for the "unbounded OOM" property. File: tests/library/test_production_adapters.py:115-129 (+ helpers.py:163-168). Remedy: mechanism-lock variant using monkeypatch of `_ALLOCATION_LIMIT_MIB` to 1 with a complete small PNG (accept at 2047 / reject at 1), or keep rows=1 but add the "same bytes fail with limit raised above 2048" / register as known non-lock.
- R2 (P2): AC4 evidence overclaim — handoff §4 + task line 48 claim stderr categorized log "已归档进 JSON 附带复现命令", but verify-k07.json contains neither the Qt log line nor a repro command (and no env/qt version). Without that message, the control rejection isn't distinguishable from other decode failures (errorString is generic). Remedy: either append the captured stderr line(s) + command + PySide6/Qt version to the JSON, or downgrade the wording to "对照组显示 256 下拒绝；limit 归因由尺寸边界+同代码路径推出（Qt limit 原因不进 errorString，stderr 未归档）".
- R3 (P2 or P3): control design varies two factors (limit AND channel); a raw read at 2047 that succeeds is missing. Combine with R2? They're related but distinct: R2 = evidence artifact content; R3 = control design. I'll make R3 P3.
- R4 (P3): AC3 evidence table claims "宽高/mime/managed ref 全登记" but mime_type is recorded nowhere (Page has no mime field; script writes no mime). Fix: correct the wording or add mime. File: doc/tasks/M2-IMPORT-ALLOC-LIMIT.md:47; experiments/.../verify_k07.py:112-120.
- R5 (P3): base/topology mismatch: Task frontmatter base_commit=8e0de8d0 & handoff §0 "base 8e0de8d0 / 拓扑 8e0de8d0→a5c8adf1"; actual branch creation point & parent of a5c8adf1 = 8996ca55 (release 4-task batch commit; verified via .git reflog/logs). Fix: correct the handoff header (and Task base_commit or a note) so the review object's base is traceable. File: doc/handoffs/...a5c8adf1.md:9; doc/tasks/...:12.
- R6 (P3): 2047 rationale soft spots: (a) "非 0 防 OOM" doesn't discriminate 2047 (a corrupt header at 2000 MiB is now *attempted*, i.e. the same OOM class the non-zero argument invokes, just at a higher bound) — the real argument is domain bound × margin; (b) unit slip 690×350k×4B = 921 MiB (not ~965 MiB) → margin 2.2×; (c) the "~350k px" domain extrapolation is unsourced (measured max 131,289 px; 5.9× margin over measured max is the defensible number). File: src/infrastructure/importing.py:41-61. (P3, argumentation quality, no code change strictly needed but comment/handoff §2 should be corrected.)
- R7 (P3): process-global bleed not registered: raising the process-wide cap also raises the effective bound for every other QImageReader/QImage decode in-process — notably `_MobiDocumentHandle.render_page` (untrusted MOBI-embedded images via `QImage.loadFromData`, same file, line 408-413), where the pre-fix effective bound was 256 MiB and becomes 2047 MiB (8×). Fix: either re-assert a tighter bound in the MOBI page read (cheap, same file, allowed surface) or register the widened envelope in the comment/handoff §6. File: src/infrastructure/importing.py:92, 402-413.
- R8 (P4): truncation test asserts only ≤400 while the constant is 300 (+3); assert exact bound / endswith("..."). File: tests/library/test_production_adapters.py:157-159, src/...:65-75.
- R9 (P4): red-state evidence not archived as an artifact (no pytest log under verification/); only prose in handoff §3. Convention in this repo is archived logs. Also test 1 allocates ~290 MiB decoded + compresses ~304 MB raw; consider `@pytest.mark.slow` (repo already has that marker) or documenting runtime budget. Files: doc/handoffs/...:44-48; tests/...:80-93.
- R10 (P4): verify_k07.py evidence lacks env metadata (PySide6/Qt version, python, platform) and per-case decoded-size MiB; handoff §5 repro command omits `--out`, so following it does not regenerate the JSON artifact. Files: experiments/.../verify_k07.py:110-125; doc/handoffs/...:62-73; verification/.../verify-k07.json:1-3.

Hmm, that's 10 findings; maybe consolidate to keep it tight: R2+R3 could merge; R9+R10 could merge partially. I'll keep them as separate but concise, ordered P2 first. Let me target ~8 findings: 
R1 P2 (test mechanism), R2 P2 (AC4 evidence overclaim), R3 P3 (control two-variable), R4 P3 (mime overclaim), R5 P3 (base/topology), R6 P3 (2047 rationale soft spots), R7 P3 (global bleed/MOBI), R8 P4 (exact truncation bound), R9 P4 (red log not archived + slow marker), R10 P4 (env metadata + --out in repro). 10 is fine — the review prompt asks for thorough coverage of 6 items.

Also positives to record in the tables (verified statically):
- 7 files, all in allowed surface; no forbidden path in diff (verified via diff headers).
- `setAllocationLimit` is `@staticmethod` in pinned PySide6 6.11.2 (QtGui.pyi:3279-3280) + requirements.txt pins PySide6_Essentials==6.11.2 → API availability guaranteed; instance-level alternative doesn't exist (Qt exposes only the static) → the process-global design is forced, and per-decode re-assert is defensible; the lazy in-method Qt import keeps module layering (consistent with TASK-031 review note).
- `_reader_error_detail` bounds the detail; fake readers updated (both UnknownFormatReader:42-44 and LongErrorReader:139-142) — the AttributeError defect from the predecessor is genuinely fixed (verified: decode() calls the setter before constructing the reader, and both fakes now define it).
- make_thin_png streaming is correct: CRC/IHDR well-formed, batch ≤ ~8 MiB, `rows` clamp `min(rows, height)`, memory independent of height (verified by reading code); the predecessor's ~2GB intermediate is genuinely removed.
- Red-state logic self-consistent: on baseline (no setter), test1 fails at 256 (289.5>256), test2 fails (calls empty), test4 fails (5000>400), test3 passes (256 rejects 2048) ⇒ exactly 3 failed/4 new. ✓ arithmetic consistent.
- Test-count reconciliation: canonical main = 三套件 509+1 skipped (STATUS.md); +8 pre-existing tests in the touched file = 517; +4 new = 521 ✓ — so the numbers are internally consistent and include the canonical suites + the touched file.
- K07 real-file numbers: 690×131289×4 = 345.57 MiB ✓ (>256 → consistent with F2), K09 264.48 ✓, K10 264.99 ✓; managed refs follow D03 layout books/<book>/chapters/<chapter>/original/<hex>.png ✓; production-channel path verified against ports/service signatures statically (FailedImport(filename, reason, detail), ImportedPage(filename, page), ImportSource(filename, data_provider), MemorySink implements the 3 port methods, ManagedFileStorage has ensure_layout/write_temp/verify_temp/new_revision_relative_path/publish/discard_temp) ⇒ the script would exercise the real channel as claimed.
- Attribution: production pass at 2047 vs control at 256 on the same bytes → the limit is the causal variable (with the R3 caveat).

Verdict: `approved_with_conditions`（条件通过）— 0×P0/P1；R1/R2 为条件（P2），其余为建议/文档级；集成方须在合并前闭合 R1/R2（或由 Owner 登记为已知限制）。

Hmm, should R1 be a *condition*? The test-quality concern doesn't block correctness of the fix (the fix itself is verified by the real-file test and the red/green webtoon test). The "fail-closed" property is functionally true (Qt rejects >2047 in reality). The test just doesn't prove it. So it's a test-quality condition — I'd make it a condition (conditional approval) since it's P2 and cheap to fix. Yes: conditions = R1 (either add mechanism lock or register as known non-lock) + R2 (fix overclaim or archive stderr).

NOT_VERIFIED (integrator runtime items):
1. pytest 红/绿与四套件实跑（517→521+1 skipped, 0 failed）——本沙箱无 shell，无法复跑；且红态无归档日志。
2. 红态 stash 复现方法（stash 只含 src）与是否真的在 8996ca55 树 + 新测试 上跑；.git 内无 stash reflog 残留（与 pop 后清理一致，但不构成证据）。
3. `git status --porcelain` 干净、`git diff --check` EXIT=0 与"7 文件之外无改动"（含 untracked）——需集成方在 worktree 实跑；本次仅能从 review-input.diff 的 7 个 diff --git 头确认范围内文件。
4. verify_k07.py 实跑（真图 K07/K09/K10 只读 + %TEMP% 管理树）与 stderr 分类日志原文（`QImageIOHandler: Rejecting image as it exceeds the current allocation limit of 256 megabytes`）——JSON 未含该文本，需 Owner/集成方补档或实跑取回。
5. 2047 下的真实解码内存峰值/耗时（单次 ~345.6 MiB QImage + 57 MB 源字节；测试 1 单次 ~289.5 MiB）与 1.57s 文件级耗时；建议集成方在目标机复测一次峰值与墙钟。
6. Qt 全局上限对所有 QImageReader/QImage 解码生效的运行时确认（尤其 `_MobiDocumentHandle.render_page` 的 `QImage.loadFromData` 是否同受约束；见 R7）。
7. 60ff... 无。另：`QImageReader.setAllocationLimit` 在锁定版本 PySide6 6.11.2 的存在已由 stub 静态确认，但"运行时可调用"仍需一次实跑（绿态已声称）。
8. K07 资产 sha256 `95435126…` 与 TA3-B2 记录/资产实际哈希的一致性（无 shell 无法 sha256sum）；仅尺寸 690×131289 与 TA3-B2 case-selection 记载一致（该一致性我未在本次直接读到 case-selection 文件——我没读它！）。Hmm — I claimed cross-check with TA3-B2 case-selection; I haven't read experiments/M2-TA3-B/case-selection.json. The TA3-B2 quality-report.md line 47 lists K07/K09/K10 with dims 690×131289/690×100480/690×100674 ✓ (I saw that in the grep output). So the dims cross-check against quality-report.md is verified; the case-selection.json itself I didn't read. I'll phrase it against quality-report.md (verified) and leave sha256 to the integrator.

Also "main 509+1skipped 0 failed" — the STATUS.md line confirms the canonical baseline is 三套件 509+1 ✓ (verified from doc/STATUS.md).

集成方闭合清单:
1. worktree 实跑：`PYTHONPATH=src <venv-python> -m pytest tests/library/test_production_adapters.py tests/providers tests/core tests/m2_acceptance -q` → 期望 521 passed, 1 skipped, 0 failed；并补跑 `-q tests` 或至少 `tests/library tests/import_formats` 关注 MOBI/import 相邻面（R7）。
2. `git -C <worktree> status --porcelain`（期望空）与 `git diff --check 8996ca55 02f306ea` EXIT=0；核实 a5c8adf1 的 parent 确为 8996ca55 并据此修正 handoff/Task 的 base 记录（R5）。
3. 真图复跑：`PYTHONPATH=src <venv-python> experiments/M2-IMPORT-ALLOC-LIMIT/verify_k07.py --out verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json`（注意加 --out），捕获 stderr 中 `Rejecting image as it exceeds the current allocation limit of 256 megabytes` 原文并归档 → 闭合 R2；确认 verdict PASS。
4. 红态复现（可选但建议）：`git stash push src/infrastructure/importing.py`（只 stash src）→ 跑 4 新测试 → 期望 3 failed → `git stash pop`；把原始 pytest 输出归档到 verification/M2-IMPORT-ALLOC-LIMIT/。
5. R1：加入"机制锁定"测试（monkeypatch `importing._ALLOCATION_LIMIT_MIB=1` + 完整小 PNG → 拒；2047 → 通过），或先在 Task/handoff 登记"fail-closed 测试不锁定机制"为已知限制。
6. R4/R6/R10 文档级修正（mime 表述、965→921 MiB、--out、env 元数据）。
7. 集成决策：2047 与 settings 可配置化的边界（本 Task 不做），以及 K07 域外更大页的复评入口已登记（handoff §6）→ 认可。

推荐下一步（一句）：Codex（集成方）在 worktree 实跑四套件+真图脚本并补档 stderr 原文，Owner 顺带闭合 R1（机制锁定测试）后即可合入。

Let me double check the claim "8 pre-existing tests in test_production_adapters.py": 12 total - 4 new = 8 ✓ and 509+8 = 517 ✓.

Also verify the red-state expectation for test 1 more carefully: baseline `decode` (no setter) + test sets 256 → `QImageReader.read()` on a valid 690×110000 PNG → Qt rejects because 289.5 MiB > 256 → read returns null → ImageDecodeError raised → test 1 fails (error, not assertion) ✓ counted as "failed".

Now let me also double check "F1 五例 <256MiB" – not needed.

One more: the review prompt item 2 asks whether stash-red methodology "是否有效". Answer: methodologically valid (it isolates the src delta while keeping the new tests — the correct way to show the tests are red on the pre-fix code), with caveats: (a) no archived output; (b) the "baseline" is 8996ca55 which already contains the *predecessor's* uncommitted... no, stash of src gives 8996ca55's committed src, which has no allocation limit at all ✓ so it's a true pre-fix baseline. Also note the three red tests only cover: limit-override, setter-called, truncation. The fail-closed property isn't red-covered (R1).

Also, one nuance about item 2's "3 failed/7 中的构成": The dispatch text says "3 failed/7 中的构成" (probably meaning "3 failed of 7"?). Handoff says 3 failed / 4 新增 tests. Actually "红态 3 failed/4 新增" means 3 failed of the 4 new. The dispatch's "3 failed/7" might refer to something else; I'll just state: 4 new tests, 3 red on baseline, 1 baseline-green by design; and the composition maps exactly to the three defects (256-cap rejection, no setter call, no truncation) ✓ self-consistent. Also note the red-state count is "test-level" and there is no claim about other tests turning red ✓ (the new src change can't break other tests? The setter call changes global state at import decode; other tests in the four suites that decode images via QImage/QImageReader could be affected only by a *higher* cap → no behavioral change below 256 ✓ so no regression risk).

Hmm, one more possible regression vector worth mentioning as a P4: `QtImageDecoder.decode` now performs a *global mutation* on every call; any test that asserts Qt's allocationLimit default (none found — grep shows no such test outside the new ones) is safe ✓. I verified via grep: only new tests reference allocationLimit. Good — I can state that positively.

Let me also double check there's no other test file using `importing.QtImageDecoder`: grep showed only test_production_adapters.py imports it (plus verify_k07.py). Let me verify quickly? The earlier grep for "QImageReader|allocationLimit" covered src/tests/experiments. For "QtImageDecoder" I saw conftest uses helpers.QtImageDecoder (fake). Could there be another test importing production QtImageDecoder? Let me grep "from infrastructure.importing import" to be safe — it affects the regression-scope claim (which tests exercise the change). Quick grep.

Also check whether `tests/import_formats/test_mobi_import.py` has an oversize-image expectation that interacts with R7. Let me grep for "loadFromData|256|allocation" in tests/import_formats — probably nothing. One grep for "infrastructure.importing" across tests.
dsh: reasoning:
Very useful: `tests/core/test_core_assembly.py:241` imports `QtImageDecoder` from infrastructure.importing (likely an assembly smoke test) and `tests/import_formats/test_mobi_import.py:42` imports from infrastructure.importing (MobiDocumentRaster etc.). And TASK-043 established a repo convention: red-state evidence archived as `verification/TASK-043/pre-fix-tests-against-base-src.txt` with node ids and tree provenance (`infrastructure.importing = ...temp\task043-prefix\src\...`). That's the project's precedent for red-state evidence — supporting my R9 finding (this task's red-state evidence is not archived as an artifact, while TASK-043 archived exactly such a file with tree provenance). This is a strong, evidence-based finding: precedent exists in-repo.

Also TASK-043's README describes "base c5aa664 的 src + 本次新测试, -q -rs -rf：8 failed / 8 passed" with per-node ids and tree provenance. Excellent concrete recommendation: mirror that format (archive `pre-fix-tests-against-base-src.txt` + assert the importing module path resolves to the base tree).

Let me confirm test_core_assembly.py:241 context — does it construct QtImageDecoder and decode? If it decodes a real image, the global limit is set — harmless. Let me look at that snippet briefly to see if it's affected (e.g., asserts something about limits). Quick read of lines 230-255. And tests/import_formats/test_mobi_import.py line 42 imports what? Let me check lines 30-60. These two confirm the regression-relevant adjacent tests are inside the four-suite selection? tests/core ✓ is included (test_core_assembly.py is in tests/core!) and tests/import_formats ✗ is NOT included in the four suites. test_mobi_import.py imports from infrastructure.importing — so the MOBI path (R7) has tests outside the run set. That strengthens: recommend integrator run tests/import_formats too.

Let me read those two snippets quickly.
dsh: reasoning:
Confirms: tests/import_formats/test_mobi_import.py exercises MobiDocumentRaster (the R7-adjacent path) and is NOT in the four-suite run set → recommend integrator run it.

Now I'm ready to write. Let me be careful about facts and keep it well-structured in Chinese, with the required headings exactly.

A few more numeric checks I want to state:
- 690×110000×4 = 303,600,000 B = 289.54 MiB ✓ (>256).
- 8192×65536×4 = 2,147,483,648 B = 2048 MiB ✓ (2^31).
- 2047 MiB = 2,146,435,072 B; 2048 MiB - 2047 MiB = 1 MiB = 1,048,576 B.
- K07 345.57 MiB, K09 264.48 MiB, K10 264.99 MiB ✓ all >256.
- 690×350,000×4 = 966,000,000 B = 921.2 MiB (comment says ~965 MiB → MB/MiB 混用).
- 2047/921.2 = 2.22×; 2047/345.57 = 5.92×.

Test-count reconciliation: STATUS.md "main 三套件 509+1skipped 0 failed" (verified in doc/STATUS.md line 14) + touched file's 8 pre-existing tests = 517 ✓ + 4 new = 521 ✓.

One more consideration for A: "有没有更合理的实例级方案被忽略" — answer: Qt 只提供静态 API（PySide6 6.11.2 QtGui.pyi:3279-3280 的 `@staticmethod setAllocationLimit`），因此不存在实例级方案；可选替代是把 setter 放到 assembly/bootstrap（更早、一次），但 ①bootstrap 属本 Task 禁改面；②importing.py 刻意把 PySide6 延迟到方法内导入（TASK-031 审查记录），启动期调用会破坏该分层；③每次 decode 幂等重断言对"他处改写全局"有自愈性。结论：现行方案在本仓库约束下是最小且自洽的。唯一真正的替代是「按页面形态/设置项配置」，Task 已允许但被显式推迟并留痕（handoff §2 settings 通道不做）→ 记为可接受的范围决策。

Also for A: 截断 300 chars — the truncation is on errorString, not on the domain; fine.

For E: the diff is 7 files: list them; forbidden surfaces zero; only src file = importing.py ✓; tests within allowed; experiments/verification new dirs allowed ✓. Note `doc/handoffs/...`+`doc/tasks/...` allowed. Note nothing touched in `doc/STATUS.md` ✓ (STATUS still says "无 Active Task"? Actually the Task is in_review but STATUS was not updated — is that a problem? Task's allowed surface excludes doc/STATUS.md (禁改面) ✓, so the integrator will handle STATUS. Good — mention in the closure list: integrator updates STATUS (its own surface).

For the 红态 section B: mention the TASK-043 precedent with the concrete archived file `verification/TASK-043/pre-fix-tests-against-base-src.txt` (tree provenance line: `infrastructure.importing = C:\...\task043-prefix\src\infrastructure\importing.py`), recommending mirroring it. Good, evidence-based.

Also worth noting for B: tests TASK-043 README shows the pattern "-q -rs -rf" with node ids; the red run here should similarly record node ids + the resolved `infrastructure.importing` path to prove the base tree was used (this addresses "stash src 的红态方法是否有效" precisely: without path provenance, a reader can't tell whether the baseline was the base src or the fixed src).

For D: fields — width/height ✓, managed ref ✓ (D03 layout), errorString ✓ (control), but missing: env/qt version, mime (claimed), decoded MiB, stderr log line, repro command. And control design (two variables).

Also for D: `imported[0].source_size_bytes` = on-disk size ✓ matches top-level; sha256 per case ✓ present (good, integrity of the asset input is archived). Actually sha256 IS present ✓ — credit that.

Also — "managed_original_ref" for K07 is `.../original/7410a3a0d7f148b3829563abbc0348b3.png` — a uuid4 hex, not the sha256 prefix. Fine (ManagedFileStorage uses uuid4 hex). Note: the adapter passes uuid4().hex ✓ consistent.

One question: verify_k07.py's expected D03 layout check: `books/verify-k07/chapters/chapter-k07/original/...` ✓ matches book_id_for_chapter lambda `verify-{case.lower()}` → "verify-k07" ✓ and chapter_id "chapter-k07" ✓.

Now, the JSON's K07 `height: 131289` matches the TA3-B2 quality-report K07 dims ✓ (cross-check verified against quality-report.md:47 which I read via grep).

For NOT_VERIFIED I'll list ~7 runtime items.

Verdict: `approved_with_conditions`（条件通过，0×P0/P1；2×P2 条件）。Hmm — is R1 P2 or should it be P3? The concern is a test that doesn't test what it claims. The project's review tradition in this repo (M2-QUAL etc.) uses P2 for "evidence/test does not support the claim". I'll keep P2 and make it a condition that can be closed either by adding the mechanism test OR by registering the limitation (a documentation fix) — that's a cheap closure path.

R2 (evidence overclaim) P2 — condition: archive stderr or downgrade wording.

Everything else P3/P4 → non-blocking suggestions.

Let me write the final answer. It should be comprehensive but readable. Use tables for the 逐项核对表, findings with 文件:行.

Format headings exactly as requested:
## Verdict
## 逐项核对表（A 修复方案论证 / B 红绿证据 / C 测试质量 / D 真图验证 / E 范围纪律）
## Findings（R1…，P0-P4，文件:行）
## NOT_VERIFIED（集成方运行时项）
## 集成方闭合清单
## 推荐下一步（一句）

I'll write it in 简体中文. Include the static verification facts with file:line citations.

Let me draft the tables concisely with 结论 (成立/部分成立/待实跑) per item.

A items:
A1 值 2047 / 非 0 / 边界 | 部分成立（论证方向正确，两处软点） | 注释 importing.py:41-61；R6
A2 分配前检查非预分配 | 成立（Qt 语义与代码用法一致；且验证脚本本身依赖该语义） | importing.py:55-56；R1 指出测试未锁定
A3 static 全局 setter 副作用（进程级/并发幂等） | 成立但覆盖不全 | PySide6 6.11.2 QtGui.pyi:3279-3280（@staticmethod，无实例级 API）；R7
A4 实例级/更优替代是否被忽略 | 无更优替代；bootstrap 方案受禁改面与延迟导入分层约束 | tests/core/test_core_assembly.py:261+ 有「Core 层不得模块级 PySide6」约束 → in-method import 是既有纪律 | 成立
A5 settings 可配置化不做 | 可接受（Task AC1 允许自选并留痕；handoff §2 留痕；唯一未登记的是"域外更大页"复评入口已登记 §6） | 成立
A6 fail-closed 语义 | 代码层成立（>limit 仍 ImageDecodeError，detail 非空） | 测试层未锁定 → R1
A7 typed 错误改善 r1 R4 | 成立（errorString strip + fallback + 300 截断；detail 流入 FailedImport.detail → service.py:86-87） | 成立（P4 nit R8）

B items:
B1 红态方法有效性 | 方法方向正确（只回退 src 保留新测试是标准做法），但缺树溯源归档 → P4/R9（TASK-043 有先例）
B2 3 failed/4 新增构成 | 自洽（1:289.5>256；2:calls 空；4:5000 不截断；3:基线 256 亦拒 2048 → 基线绿） | 成立
B3 绿态 4/4 | 待实跑（NOT_VERIFIED）
B4 517→521+1skip 0 failed | 数字自洽（STATUS 三套件 509+1 + 该文件既有 8 → 517，+4 → 521）；但四套件不含 tests/import_formats（MOBI 相邻面，R7）→ 集成补跑
B5 PySide6 6.11.2 环境 | requirements.txt:1 固定 ==6.11.2；stub 有 API ✓

C items:
C1 rows=1 机制锁定 | 不成立（同断言在 limit≥2048 也通过；截断 IDAT 单独就足以失败）→ R1 P2
C2 make_thin_png 流式正确性 | 成立（逐行核对：IHDR 13B/CRC/过滤器字节/zlib 流式/批次 ≤8.4MiB/rows clamp）
C3 截断断言 | 部分（≤400 而非 ==303；未断言尾部 "..."）→ R8
C4 全局值恢复 fixture | 成立（autouse，前后捕获恢复；teardown 顺序与 monkeypatch 兼容）
C5 fake 补齐 | 成立（UnknownFormatReader:42-44 / LongErrorReader:139-142，均在 decode 前置断言路径上必要）
C6 测试代价 | 待实跑（test 1 单次分配 ~289.5MiB QImage、压缩 ~304MB 原始行；建议 slow 标记）→ R9

D items:
D1 字段完整性 | 部分（宽高/sha256/managed ref/limit ✓；mime 缺失却被声称；无 env/qt 版本、无 decoded MiB）→ R4/R10
D2 生产通道真实性 | 成立（静态对齐 ports/service/ManagedFileStorage 签名：FailedImport(filename,reason,detail)、ImportedPage(filename,page)、ImportSource(filename,data_provider)、MemorySink 三方法、storage.ensure_layout/write_temp/verify_temp/new_revision_relative_path/publish/discard_temp）
D3 对照组归因 | 方向成立、强度不足（同一字节在 256 拒/2047 通过 → 限值是因果变量，但两臂还差一个通道变量；且 errorString 不区分原因、stderr 未归档）→ R2/R3
D4 K07 尺寸与 TA3-B2 一致性 | 成立（quality-report.md:47 K07 690×131289 / K09 690×100480 / K10 690×100674 与 JSON 逐位一致；三例解码 345.6/264.5/265.0 MiB 均 >256 → F2 自洽）
D5 只读源文件 | 成立（脚本仅 path.read_bytes/stat）→ D07 §37

E items:
E1 7 文件全允许面 | 成立（diff --git 头 7 个，逐一核对允许清单）
E2 importing.py 之外 src 零触碰 | 成立（唯一 src 文件）
E3 tests 改动在允许面 | 成立（tests/library/{helpers,test_production_adapters}.py，均为 import 相关）
E4 禁改面零 | 成立（diff 内无 src/ports、src/bootstrap、doc/contracts、packaging、apps、doc/STATUS.md；TA3-B experiments 未动）
E5 porcelain 干净 / diff --check EXIT=0 | NOT_VERIFIED（无 shell）
E6 版本库记录 | branch ref=02f306ea ✓、reflog 证明 8996ca55→a5c8adf1→02f306ea（与 dispatch 一致），但与 Task/handoff 声称的 base 8e0de8d0 矛盾 → R5

Now findings text. Let me write them with 文件:行 and 建议.

Then NOT_VERIFIED list.

Then 集成方闭合清单 (numbered, with commands).

Then 推荐下一步 (one sentence).

Note: I must mention the sandbox: no shell → static only. Good to state in Verdict.

Let me write the final answer now. Keep it organized and reasonably concise per line.
## Verdict

**approved_with_conditions（条件通过）** — 0×P0 / 0×P1；2×P2 条件（R1 测试未锁定机制、R2 AC4 证据超述），其余 P3/P4 为文档与证据设计级。修复本体（`setAllocationLimit(2047)` + typed detail）方向、放置点、范围纪律与真图通道**静态层面成立**；限制在于本沙箱无 shell（`pwsh` 因 `grantWrite(G:\CODEX\New Manga)` 失败、升级无审批通道），一切 pytest / verify_k07.py / git 实跑归入 NOT_VERIFIED。

可静态确认的关键事实（非作者复核，均给出行号）：
- 分支 ref `02f306ea`（`.git/refs/heads/agent/zcode/M2-IMPORT-ALLOC-LIMIT`）与 dispatch 一致；`.git/worktrees/.../logs/HEAD` 证明真实父子链 **`8996ca55`（release 4-task batch）→ `a5c8adf1` → `02f306ea`**，`8996ca55` 的父才是 `8e0de8d0`（`.git/logs/HEAD:726-727`）。
- `QImageReader.setAllocationLimit` 在锁定版本内**存在且为 static**（`PySide6/QtGui.pyi:3279-3280`），`requirements.txt:1` 固定 `PySide6_Essentials==6.11.2` → Qt 6.5+ API 可用性有静态保证，且 Qt **不提供实例级** allocation limit（静态全局是唯一 API）。
- 数值链自洽：K07 690×131289×4 = 345.57 MiB、K09 264.48、K10 264.99（均 >256，与 `verification/M2-TA3-B/quality-report.md:47` 的 K07/K09/K10 尺寸逐位一致）；新红态测试 690×110000×4 = 289.54 MiB；超限测试 8192×65536×4 = 2^31 B = 2048 MiB > 2047 MiB。
- 计数链自洽：`doc/STATUS.md` 记录 main 三套件 **509+1skipped**；被改文件既有 8 例 → 517，+4 新增 → **521**（与 handoff §3 完全对得上）。

---

## 逐项核对表（A 修复方案论证 / B 红绿证据 / C 测试质量 / D 真图验证 / E 范围纪律）

### A 修复方案论证

| # | 核对项 | 结论 | 依据 |
|---|---|---|---|
| A1 | 2047 论证链（非 0 / 域上界 / int 内 / 分配前检查） | **部分成立**（方向对，2 处软点） | `src/infrastructure/importing.py:41-61`；见 R6：①"非 0 防 OOM"只能排除 0，不能区分 2047（同一 OOM 类只是上移到 2 GiB 尝试）；②`690×350k×4B` 实为 **921 MiB（不是 ~965 MiB）**，MB/MiB 混用，且 350k px 外推无出处；可辩护数字是对实测最大页 345.57 MiB 的 **5.9×** 余量 |
| A2 | "Qt 分配前检查、非预分配" | **成立（机制描述）** | Qt 语义 + 证据脚本自身就依赖该语义（`verify_k07.py:171-183`）；但测试未锁定它 → R1 |
| A3 | static 全局 setter 副作用（进程级/并发幂等 re-assert） | **成立但覆盖不全** | Qt 只有 static（`QtGui.pyi:3279-3280`）；同值并发写实际无害，讨论可接受。**未论证**的是"全局上限对所有解码路径生效"的越界影响 → R7 |
| A4 | 是否有更合理的实例级方案被忽略 | **无更优替代** | 实例级 API 不存在；改到 `src/bootstrap/**` 属本 Task 禁改面（`doc/tasks/...:34`），且 `importing.py` 刻意在方法内延迟导入 PySide6（`tests/core/test_core_assembly.py:261+` 有"Core 层不得模块级 PySide6"纪律）→ 每次 decode 断言是最小自洽解 |
| A5 | 不做 settings 可配置化 | **可接受** | AC1 允许"方案自选并留痕"，handoff §2 已留痕；未来更大页复评入口登记在 handoff §6 |
| A6 | fail-closed 语义（>limit 仍 typed 失败） | **代码成立 / 测试未锁定** | `importing.py:102-103` 必抛 `ImageDecodeError`，detail 必非空；测试侧见 R1 |
| A7 | r1 R4 typed 错误改善 | **成立** | `importing.py:63-75`（strip + 空回退 + 300 截断）→ `service.py:86-87` 落 `FailedImport.detail`；断言松紧见 R8 |

### B 红绿证据

| # | 核对项 | 结论 | 依据 |
|---|---|---|---|
| B1 | "stash src 对 8996ca55 跑新测试"方法有效性 | **方法正确、证据不足** | 只回退 src 保留新测试是标准红态做法，且 `8996ca55` 确为真实基线（`.git` reflog）；但无归档日志、无树溯源（无法证明跑的是基线 src 而非已修复 src）→ R9（仓库已有先例 `verification/TASK-043/pre-fix-tests-against-base-src.txt`，含 `infrastructure.importing = ...\task043-prefix\src\...` 溯源行） |
| B2 | 3 failed / 4 新增的构成自洽性 | **自洽** | 基线无 setter：①690×110000（289.5>256）拒 → 红；②`calls` 空 → 红；④5000 字符不截断（>400）→ 红；③2048>256 亦拒 → 基线绿（owner 已如实标注"保护性测试基线绿"）。3+1=4 无需调整 |
| B3 | 绿态 4/4 | **待实跑** | NOT_VERIFIED-1 |
| B4 | 517→521+1skipped 0 failed | **数字自洽、范围需补** | 509（STATUS 三套件）+8+4=521 完全对账；但四套件不含 `tests/import_formats`（MOBI/PDF 面，见 R7）→ 集成方补跑 |
| B5 | 环境（PySide6 6.11.2） | **成立** | `requirements.txt:1`；stub 具备 API |

### C 测试质量

| # | 核对项 | 结论 | 依据 |
|---|---|---|---|
| C1 | 2048 MiB IHDR + 单行 IDAT 是否真正锁定"分配前拒绝" | **不成立（P2，R1）** | `rows=1` 使 IDAT 截断，**截断本身单独就足以让 `read()` 返回 null**；把 `_ALLOCATION_LIMIT_MIB` 改成 4096 / 100000，该断言仍然通过 → 对 AC1 的"不得无限放行"零保护力。owner 的"实测 0.01s/stderr 分类日志证实"是**运行观察**，未固化为断言 |
| C2 | `make_thin_png` 流式改造正确性 | **成立** | 逐行核对 `tests/library/helpers.py:152-201`：IHDR 13 B、`>IIBBBBB`、CRC32、filter byte 0、`zlib.compressobj(9)` 流式、批次 ≤ ~8.4 MiB（`max(1, 8MiB//len(row))`）、`min(rows, height)` 钳制；峰值确实与 height 无关，前任的 `row*height` 一次性 ~2 GB 中间对象已被真正移除 |
| C3 | detail 截断断言 | **部分成立（P4，R8）** | `test_production_adapters.py:127-129,157-159` 只断言 `<=400`，而常量语义是 300+3；未断言 `endswith("...")`，350 字符级回归漏检 |
| C4 | 全局值恢复 fixture | **成立** | `:70-77` 逐测试前后捕获恢复；pytest 夹具拆除顺序（monkeypatch 先还原、再恢复全局）与 `:102-104` 的类级 patch 兼容 |
| C5 | fake 补 `setAllocationLimit` | **成立且必要** | `:42-44`、`:139-142`；`decode()` 在构造 reader 前就调用 setter（`importing.py:92`），缺它必 AttributeError——owner"修正 2 处"的第一处判断准确 |
| C6 | 测试代价 | **待实跑** | 用例①单次真实解码分配 ~289.5 MiB QImage 且需压缩 ~304 MB 原始行；`pytest.ini:4` 已有 `slow` 标记惯例（`tests/m2_resource_channel/...:106`），建议标注（R9） |

### D 真图验证

| # | 核对项 | 结论 | 依据 |
|---|---|---|---|
| D1 | 字段完整性 | **部分成立（R4/R10）** | 宽高 ✓、`sha256` ✓、`allocation_limit_mib` ✓、`managed_original_ref` ✓、control `errorString` ✓；**mime 无任何记录**（`Page` 本身无 mime 字段，脚本也未写）；无 Qt/PySide6 版本、无 python/平台、无 decoded MiB、无 control 的 stderr 原文、无复现命令 |
| D2 | 生产通道真实性 | **成立（静态签名对齐）** | `FailedImport(filename,reason,detail)`/`ImportedPage(filename,page)`/`ImportSource(filename,data_provider)`（`application/importing/images/ports.py:66-98`）、`MemorySink` 实现三分法、`ManagedFileStorage.ensure_layout/write_temp/verify_temp/new_revision_relative_path/publish/discard_temp`（`src/infrastructure/filesystem/managed_storage.py:70-125`）全部存在；managed ref 形状 `books/<book>/chapters/<chapter>/original/<hex>.png` 与 D03 一致 |
| D3 | 对照组能否归因"修复使其通过" | **方向成立、强度不足（R2/R3）** | 同一字节：生产通道 2047 → 通过；原始 reader 256 → 拒绝 → 限值是因果变量。但两臂同时变了"限值"与"通道"；且 `errorString='Unable to read image data'` 对任何解码失败都成立，**唯一能区分原因的分类日志并未进 JSON**（handoff §4 却称"已归档进 JSON 附带复现命令"）→ 与 `verification/M2-TA3-B/quality-report.md:141` 当时"原始 Qt 日志未归档"的同一缺口未真正闭合 |
| D4 | K07 尺寸与 TA3-B2 一致性 | **成立** | JSON 与 `quality-report.md:47` 的 K07 690×131289 / K09 690×100480 / K10 690×100674 逐位一致；三例解码 345.6/264.5/265.0 MiB 均 >256 → F2 自洽 |
| D5 | 源文件只读（D07 §37） | **成立** | 脚本仅 `path.read_bytes()/stat()`；managed 树写 `%TEMP%` 一次性目录（`verify_k07.py:100-118`） |

### E 范围纪律

| # | 核对项 | 结论 | 依据 |
|---|---|---|---|
| E1 | 7 文件全允许面 | **成立** | `review-input.diff` 7 个 `diff --git`：handoff / task / `experiments/M2-IMPORT-ALLOC-LIMIT/verify_k07.py` / `src/infrastructure/importing.py` / `tests/library/helpers.py` / `tests/library/test_production_adapters.py` / `verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json` —— 与 `doc/tasks/...:33` 允许清单逐一匹配 |
| E2 | importing.py 之外 src 零触碰 | **成立** | diff 内 src 只有 1 个文件 |
| E3 | tests 改动在允许面 | **成立** | 两者均为 import 相关 |
| E4 | 禁改面零 | **成立** | diff 内无 `src/ports/**`、`src/bootstrap/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`；TA3-A/B experiments 未动（正确：F2 原口径站点 `quality-report.md` 属他人交付面，未擅自改写） |
| E5 | porcelain 干净 / `diff --check` EXIT=0 | **NOT_VERIFIED** | 无 shell |
| E6 | 版本库溯源 | **部分成立（R5）** | branch tip=`02f306ea` 与 dispatch 一致 ✓；但 Task `base_commit: 8e0de8d0`（`:12`）与 handoff §0 "base `8e0de8d0`、拓扑 `8e0de8d0(base) → a5c8adf1`" **均与实际父子链（8996ca55 → a5c8adf1）不符**，且与 handoff §3"对 8996ca55 基线"自相矛盾 |

---

## Findings（R1…，P0-P4，文件:行）

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **R1** | **P2** | `tests/library/test_production_adapters.py:115-129`（+`tests/library/helpers.py:163-168`） | fail-closed 测试**没有锁定它声称的机制**：`rows=1` 的 IDAT 被设计性截断，截断自身即可让 `read()` 返回 null 并抛 `ImageDecodeError`；把 `_ALLOCATION_LIMIT_MIB` 改成 4096/100000，该用例与 detail 断言全部照旧通过 → AC1 的"不得无限放行（OOM）"性质零回归保护。注释里"exercises the real rejection"属未断言的主张（本沙箱无法看到 owner 的 stderr 观察） | 加一条**机制锁定**用例：`monkeypatch.setattr(importing, "_ALLOCATION_LIMIT_MIB", 1)` + 完整合法小图（如 `make_thin_png(690, 4000)`，11 MB）→ 必拒；同一字节在 2047 下 → 必过。这组"同输入、仅限值不同"才把"限值是决定因素"固化为断言。若不想加，至少在 Task/handoff 明确登记"该用例不锁定机制" |
| **R2** | **P2** | `doc/handoffs/M2-IMPORT-ALLOC-LIMIT-a5c8adf1.md:59`、`doc/tasks/M2-IMPORT-ALLOC-LIMIT.md:48` vs `verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json:54-67` | **证据超述**：文档称 stderr 分类日志 `Rejecting image as it exceeds the current allocation limit of 256 megabytes`"已归档进 JSON 附带复现命令"，但 JSON 只有 `rejected/detail`，既无该原文也无复现命令（也无 env/qt 版本）。AC4"F2 升级为一级证据"目前只由 `errorString='Unable to read image data'`（对所有解码失败同形）支撑，**与 TA3-B2 r1 要求"不得引用未归档原文"的同一缺口** | 二选一：①把该分类日志原文（逐例）+ 复现命令 + PySide6/Qt 版本追加进 JSON；②把措辞降级为"对照组在 256 下拒绝，配合尺寸边界与同一 reader 代码路径归因；Qt 不将 limit 原因写入 errorString，stderr 未归档" |
| R3 | P3 | `experiments/M2-IMPORT-ALLOC-LIMIT/verify_k07.py:148-175` | 对照组只跑"原始 reader @256 → 拒"，通过是通过**另一条通道**（生产 use case @2047）观察的；两臂同时变了限值与通道。同一 reader 在 2047 下的正向臂缺失 | 在 control 段加一条"原始 reader @2047 → 必须成功"（同一 reader 代码、同一字节），使"限值"成为唯一变量；成本低（就是已解码过的那 3 例） |
| R4 | P3 | `doc/tasks/M2-IMPORT-ALLOC-LIMIT.md:47`、`experiments/.../verify_k07.py:110-120` | AC3 声称"宽高/**mime**/managed ref 全登记"，但 mime 既不进 JSON 也不是 `Page` 字段（`application/importing/images/service.py:99-110` 无 mime），证据里查无此项 | 改为"宽高/managed ref/源大小/sha256 全登记"，或在脚本里显式记录 `QtImageDecoder.decode(...).mime_type` |
| R5 | P3 | `doc/handoffs/...a5c8adf1.md:9`、`doc/tasks/M2-IMPORT-ALLOC-LIMIT.md:12` | 基线记录错误/自相矛盾：Task `base_commit: 8e0de8d0`、handoff §0 "base 8e0de8d0 / 拓扑 8e0de8d0(base) → a5c8adf1"，实际 `a5c8adf1` 的父是 `8996ca55`（release 4-task batch），分支亦由 `8996ca55` 创建（`.git/worktrees/.../logs/HEAD:1-4`、`.git/logs/HEAD:727`），而 handoff §3 自己又写"对 8996ca55 基线" | 修正 handoff 头为 `8996ca55 → a5c8adf1 → 02f306ea`；Task frontmatter 的 `base_commit` 要么改为 `8996ca55`，要么加注"Task 授权基线 8e0de8d0；分支实际起点=release commit 8996ca55（仅新增 Task/STATUS 文档）" |
| R6 | P3 | `src/infrastructure/importing.py:41-61`（handoff §2） | 论证链 2 处软点：①"0 会 OOM"论证只排除 0，不构成 2047 的理由（2047 仍是 2 GiB 级单次尝试，真正的理由只有"域上界×余量"）；②`690×350k×4B ≈ 965 MiB` 单位混用（= 966 MB = **921 MiB**，余量 2.2× 而非 2.1×），且 350k px 外推无出处（实测最大 131,289 px） | 注释中改为："域实测最大 345.6 MiB（K07）/ 按现有页宽外推上界 ≈921 MiB / 2047 MiB 留 ≥2.2× / 单文件串行解码，不预分配"。数字口径统一 MiB |
| R7 | P3 | `src/infrastructure/importing.py:92` 与同文件 `402-413` | **全局溢出未登记**：进程级静态上限一旦被 import 路径设为 2047，同进程其它 `QImageReader/QImage` 解码也随之上移——尤其 `_MobiDocumentHandle.render_page` 的 `image.loadFromData(raw)`（MOBI 内嵌图像=不可信输入），其有效上界从 256 MiB 变 2047 MiB（8×），正是 fail-closed 纪律关心的那类风险面 | 最小面二选一（都在允许面内）：①在 MOBI 页解码前显式 `QImageReader.setAllocationLimit(256)` 重新收紧；②在 `importing.py:57-60` + handoff §6 明确登记"该全局上界同时放宽 PDF/MOBI 解码路径，风险已登记"。集成方还应补跑 `tests/import_formats`（`test_mobi_import.py:42` 直接使用该适配器，不在本次四套件内） |
| R8 | P4 | `tests/library/test_production_adapters.py:157-159`、`src/infrastructure/importing.py:65-75` | 截断断言过松（`<=400` vs 实际 303；未断言尾部 `...`） | 断言 `len(detail) == _ERROR_DETAIL_MAX_CHARS + 3` 或 `endswith("...")` |
| R9 | P4 | `doc/handoffs/...a5c8adf1.md:44-48`、`tests/...:80-93` | 红态只有文字，无归档日志与树溯源；仓库既有先例（`verification/TASK-043/pre-fix-tests-against-base-src.txt` 含逐条 node id + `infrastructure.importing = ...\src\...` 溯源）。用例①需 ~289.5 MiB 解码 + 压缩 ~304 MB 原始行，未标 `slow`（`pytest.ini:4` 已有该 marker） | 归档 `verification/M2-IMPORT-ALLOC-LIMIT/pre-fix-tests-against-base-src.txt`（`-q -rs -rf` + node id + 解析出的 `infrastructure.importing` 路径）；用例①加 `@pytest.mark.slow` |
| R10 | P4 | `experiments/.../verify_k07.py:110-125`、`verification/.../verify-k07.json:1-3`、`doc/handoffs/...:62-73` | 证据缺 env 元数据（PySide6/Qt、python、平台、per-case decoded MiB）；handoff §5 复现命令**漏 `--out`**，照抄不会重建 JSON 产物 | JSON 增加 `env` 段与 `decoded_size_mib`；复现命令补 `--out verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json` |

---

## NOT_VERIFIED（集成方运行时项）

1. **红/绿与四套件实跑**：`pytest tests/library/test_production_adapters.py tests/providers tests/core tests/m2_acceptance -q` 期望 521 passed / 1 skipped / 0 failed；以及 4 个新用例绿态 4/4（owner 声称 1.57s 文件级）。本沙箱 `pwsh` 不可用，无法复跑。
2. **红态可重放性**：stash 仅含 `src` 的红态是否确在 `8996ca55` 树上执行（`.git` 内无 stash reflog 残留，与 pop 后清理一致，但不构成证据）；3 failed 的逐条 node id 未归档。
3. **工作区洁净与范围完备性**：`git status --porcelain` 为空、`git diff --check 8996ca55 02f306ea` EXIT=0、"7 文件之外无改动（含 untracked）"。本次仅能证明 review-input.diff 的 7 个 diff 头落在允许面。
4. **真图脚本实跑**：`verify_k07.py`（真图只读 + `%TEMP%` managed 树）与 stderr 分类日志原文（`QImageIOHandler: Rejecting image as it exceeds the current allocation limit of 256 megabytes`）；JSON 未含该文本，需 Owner/集成方补档或实跑取回。
5. **内存/耗时实测**：2047 下单次 ~345.6 MiB QImage + 57 MB 源字节的峰值与墙钟（用例①单次 ~289.5 MiB），目标机复测一次。
6. **全局上限的真实作用域**：`QImage::loadFromData`（`_MobiDocumentHandle.render_page`）是否确实继承该静态上限（R7 的运行时确认）；以及 `tests/import_formats`（MOBI/PDF 面）在 2047 下无回归。
7. **API 运行时可调用性**：`setAllocationLimit` 在锁定 PySide6 6.11.2 的存在已由 stub 静态确认（`QtGui.pyi:3279-3280`），但"实际可调用且生效"仍需一次实跑（owner 绿态已声称）。
8. **资产完整性**：K07/K09/K10 的 `sha256`（JSON 已记录）与 `test_assets` 实物哈希的一致性、以及 case-selection 原文件的逐位交叉核对（本次只核到 `quality-report.md:47` 的尺寸一致）。

---

## 集成方闭合清单

1. **实跑四套件 + 补跑相邻面**（闭合 B3/B4/R7）：`PYTHONPATH=src "<venv>/Scripts/python.exe" -m pytest tests/library/test_production_adapters.py tests/providers tests/core tests/m2_acceptance tests/import_formats -q` → 期望 521+1 skipped 之上再补 `tests/import_formats` 全绿、0 failed。
2. **范围与空白**（闭合 E5/R5）：worktree 实跑 `git status --porcelain`（期望空）、`git diff --check 8996ca55 02f306ea`（EXIT=0）、`git rev-parse a5c8adf1^`（期望 `8996ca55`）并据此修正 Task/handoff 的 base 记录。
3. **真图复跑与补档**（闭合 D3/R2/R10）：`PYTHONPATH=src "<venv>/Scripts/python.exe" experiments/M2-IMPORT-ALLOC-LIMIT/verify_k07.py --out verification/M2-IMPORT-ALLOC-LIMIT/verify-k07.json`（**务必带 `--out`**），捕获 stderr 分类日志原文 + env 版本入 JSON，确认 `verdict: PASS`；建议顺带加"原始 reader @2047 → 成功"对照臂（R3）。
4. **红态归档**（闭合 B1/R9）：`git stash push src/infrastructure/importing.py` → 跑 4 新用例（期望 3 failed / 1 passed）→ `git stash pop`；输出以 `-q -rs -rf` 归档到 `verification/M2-IMPORT-ALLOC-LIMIT/`，含解析出的 `infrastructure.importing` 绝对路径。
5. **R1 条件闭合**（二选一）：加入"同输入、仅限值不同"的机制锁定用例；或在 Task/handoff 明确登记该用例不锁定机制（不可两者都不做）。
6. **文档级收口**：R4（mime 表述）、R6（921 MiB / 外推口径/非 0 论证重心）、R10（`--out` 与 env 元数据）。
7. **集成决策记录**：①2047 为硬编码常量、settings 通道显式推迟（handoff §2）——认可；②进程全局上界对 MOBI/PDF 解码路径的放宽需登记或收紧（R7）；③TA3-B2 `quality-report.md` 的 F2 行仍写"推断口径/原始 Qt 日志未归档"，本 Task 未改该文件（属他人交付面，处置正确）——合入时应在集成记录里指明"F2 口径升级证据在 `verification/M2-IMPORT-ALLOC-LIMIT/`，原站点待 Codex 决定是否回填"。
8. **STATUS 更新**：`doc/STATUS.md` 属本 Task 禁改面，由 Codex/编排在集成时更新（Task 当前 `status: in_review`）。

---

## 推荐下一步（一句）

由 Codex（集成方）在 worktree 实跑四套件（含 `tests/import_formats`）与 `verify_k07.py --out`、补齐 stderr 原文与红态归档日志，Owner 同时闭合 R1（补机制锁定用例或登记不锁定）+ R2 措辞/证据修正，即可 `approved` 合入。
