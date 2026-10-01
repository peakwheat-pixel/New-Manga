dsh: reasoning:
Let me start by exploring the repository and the relevant files.

The task:静态 Review of M2-QUAL-DETERM-CALIB. I need to read the diff, task doc, handoff, calibration artifacts, thresholds doc, phase2-plan, and verify claims.

Let me start reading.

Let me plan: read files in parallel.

Note the working directory is G:\CODEX\New Manga but the worktree is G:/CODEX/New Manga.worktrees/M2-QUAL-DETERM-CALIB-zcode. Let me explore.

Let me first check the review-input.diff and the task file.

I'll do multiple tool calls in one block.

Should I create a goal? The user asks for a static review, round 1. This is a single-turn deliverable arguably but long. Continuous review rounds... Probably not needed. It's a review deliverable; I'll just do it. Actually the instruction says create_goal for long-running objectives. This is a bounded single review. I'll skip the goal.

Let me start.
dsh: reasoning:
The pwsh failed due to sandbox. Let me note: "Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)". Hmm, that's a sandbox provisioning error. The workspace is G:\CODEX\New Manga and file policy workspace-write. The pwsh command failed to even set up. Let me retry — maybe transient. Actually the error says grantWrite failed. Perhaps the pwsh tool can't run. The user said "沙箱无 shell 时不执行命令" — if sandbox has no shell, don't run commands. So I should rely on read/glob/grep tools only.

Let me continue reading the diff, then read the actual files in the worktree.

Let me read the rest of the diff.
dsh: reasoning:
Now I have the full diff. Let me now read the actual files in the worktree to verify:
1. `verification/M2-TA3-B/quality-thresholds.md` §0 normalization, §5, §7
2. `verification/M2-TA3-B/phase2/summaries/qual-K11.json` etc. — check region counts, translate_details — to verify 13 pairs, 5 pairs, and the emptiness claims and text.
3. `experiments/M2-TA3-B/measure_cer.py` — verify normalization replication.
4. `doc/tasks/M2-QUAL-DETERM-CALIB.md` in the worktree (tip includes more? diff shows only base..e3b7c48d changes; tip=2400b57a handoff. Actually the diff given is base..tip? Let me check: the diff includes handoff file M2-QUAL-DETERM-CALIB-e3b7c48d.md and task status delivered. It says implement=e3b7c48d, tip=2400b57a (handoff). Hmm. The handoff says delivery_head e3b7c48d. The diff includes handoff + task as new/changed. Possibly the diff is base..tip = 2400b57a which includes e3b7c48d plus a handoff commit. Need to check the worktree git log — but no shell. Hmm, I can read .git files? Reading .git/HEAD and refs is possible via read tool.

Let me check the worktree structure.

Also check the quality-report.md §5 for F5 record (7/11 observation).

Also check whether qual-*.json files are unchanged (can't run git, but the diff doesn't include them — that's evidence).

Also check `verification/M2-TA3-B/phase2/summaries/` for K01 (region_count=0 claim) and other cases.

Let me glob the worktree.

Key verification tasks:
1. K11 summary: regions count, translate_details count, reading_orders, region_type, translated_text values — verify the 13 pairs and the empty claims (`\n\n` source, ro=9; ro=13 sfx empty).
2. BJ02: 5 regions.
3. K01: region_count 0.
4. normalization function in measure_cer.py — does it match §0 in quality-thresholds.md?
5. thresholds diff — only the listed lines changed (already seen the diff; verify no other changes: the diff for quality-thresholds.md shows 3 hunks: §5, §5 note, §7 row 10. Good.)
6. phase2-plan 3 hunks.
7. Check the "7/11" claim: K11 raw nonempty variant = 7/11. Verified from JSON.
8. Median arithmetic: 18 pairs. If ≤8 float with magnitude [0.75,0.875], median of sorted 18 values: positions 9 and 10 (1-indexed) → statistics.median averages 9th and 10th. If 8 floats, sorted ascending: floats occupy positions 1..8, identical occupy 9..18 → median = (v9+v10)/2 = 1.0. Correct. If 9 floats: positions 1..9 floats, 10..18 = 1.0 → median = (v9+1.0)/2 where v9 ≤ 0.875 → ≤0.9375 <0.95. Correct. But wait — the claim "浮动 ≥9 对时 median ≤0.9375 恒 FAIL" assumes float values ≤0.875. But float values could be >0.875? Actually the max float measured is 0.875, and the reasoning assumes the float amplitude band [0.75,0.875]. If a float were 0.9375 (like single_char on 16-char text), then 9 floats could give median (0.9375+1)/2=0.96875 ≥0.95 → PASS. So the boundary argument is conditional on the amplitude band. Hmm, the probe single_char_ge4 max was 0.9375 (a 16-char string 1-char edit = 15/16 = 0.9375). Wait, 1 - 1/16 = 0.9375. And n=15 for single_char_ge4. So the claim "median ≤(0.875+1)/2=0.9375" holds only if all 9+ floats are ≤0.875. If 9 floats at 0.9375 → median = 0.96875 PASS. So the math is not universally valid: it depends on the float magnitude distribution. The document does say "以实测浮动幅度 [0.75, 0.875] 计" (using measured amplitude). So it's disclosed as conditional. But is it a real weakness? It's a bounding scenario. The claim "约半数 region 浮动即触发 median gate" is conditional. Actually more precisely: median gate fails when the 9th smallest value < 0.90 (since median = (v9+v10)/2 ≥ 0.95 requires v9+v10 ≥ 1.9; with v10=1.0 need v9≥0.9). So the correct condition: at least 9 pairs with similarity < 0.90. With observed max float 0.875 < 0.90, so ≥9 floats at observed magnitude → FAIL. But there's an edge: if exactly 9 floats all = 0.9 → median = 0.95 → PASS (>= inclusive). Fine.

So the math: 9 floats each in [0.75,0.875] → median = (0.875+1)/2 at most = 0.9375. Correct as an upper bound given the band. I should note the conditionality: it assumes float magnitudes stay within the measured band; longer strings with 1-char edits give higher similarity (e.g., 0.9375 for 16 chars), so 9 floats could exceed 0.95 median. Actually let's compute: for median to be ≥0.95 with 9 floats, need v9 ≥ 0.9. Single-char edit on 10+ char string gives ≥0.9. K11 ro=11 is 8 chars normalized ("哦我的泰阳阳！！" → let me count: 哦我的泰阳！！ = 7 chars, and 哦我的泰阳阳！！ = 8? raw 0.9, normalized 0.875 = 1-1/8. So the normalized strings are 8 chars. A 1-char edit on a 10-char string = 0.9. On 20-char = 0.95 → would PASS min gate 0.7 but median leg: if 9 such pairs float at 0.95, median = (0.95+1)/2 = 0.975 → PASS. So the median leg does not catch "all pairs float by 1 char" for long translations. That's a genuine limitation of the median gate design: it catches systematic change only in proportion to magnitude. The doc's §4.2 statement "浮动 ≥9 对（≥50%）时 median ≤0.9375 <0.95（恒 FAIL）" — the word 恒 FAIL is too strong without the band condition, though the sentence starts with "以实测浮动幅度 [0.75, 0.875] 计", which scopes it. So it's conditionally correct. I'd flag as a P3 finding: the "恒 FAIL" phrasing should be explicitly conditioned on the float amplitude band (it is in the same sentence, so mildly fine), and the median gate's insensitivity to low-magnitude systematic drift should be registered as a limitation. Actually the observed limitation list has 5 items; this one (median leg blind to low-magnitude systematic drift, since 1-char edits on long text give high similarity) is arguably covered partly by item 3 (very-short granularity) but not the flip side. Hmm. Let me think about whether the synthetic probe single_char_ge4 covers it: single_char_ge4 median=0.857 with 15 pairs; max 0.9375. So it shows all-float FAILs, but wait — with 15 pairs all floating, median = 0.857 → FAIL. But if translations were all long (e.g., 30 chars), single-char float → 0.967 similarity → median ~0.967 ≥ 0.95 → PASS. So a real systematic issue: "all regions changed by one character each" on long texts passes the median gate. Is that acceptable? Arguably yes — one char per region is benign. But it shows the median leg's threshold semantics depend on text length. Worth a P3 minor.

Now let me also verify the "min ≥ 0.70" margin claim: "0.75 − 0.05 = 0.70 留一个字符级测量余量". Hmm: 0.75 is the worst measured. A "one character-level margin" — for a 4-char text, one extra edit = 0.5, not 0.70. So the margin of 0.05 is only a half-edit margin for 4-char strings. Actually the claim "provider 版本/提示词微调可能带来 ±1 编辑差" — ±1 edit on a 4-char string means similarity drops to 0.5, which would still FAIL at 0.70. So the 0.05 margin does NOT absorb one more edit for short strings; it absorbs only a fraction. For longer texts, 1 char = e.g. 1/8 = 0.125 drop → 0.75-0.125=0.625 < 0.7 FAIL. Hmm wait, the worst measured is on 4-string (0.75), so 1 more edit → 0.5. For a 20-char string, 0.75 would be 5 edits; one more = 6/20 → 0.7, exactly at boundary. So the "0.05 margin = 一个字符级测量余量" wording is inconsistent: 0.05 is not one character for the anchor string (which is 4 chars, where one char = 0.25). This is a real argumentation defect: the margin rationale is stated per character but the numeric margin 0.05 corresponds to 1 char only for 20-char strings. I should flag this (P2/P3): the margin justification is quantitatively loose — for the anchor 4-char string, one additional edit costs 0.25 (similarity → 0.5), far exceeding the 0.05 margin. So 0.70 does not provide a "one character" buffer for the worst-case pair; it provides a buffer of 0.05 (a fraction of a character). This is a substantive methodology criticism for阈值论证.

Alternatively, is 0.70 too loose? It allows a pair to have arbitrarily large absolute edit distance as long as similarity ≥0.7 (e.g., 30% of chars replaced on a long string). Combined with median ≥0.95 this constrains aggregate, but the min leg permits ~30% char-level drift on a single region. The synthetic drift_40 min=0.5 FAILs, so the intended catch is ≥40% on any single pair. But a single region with 30% chars replaced is undetected by the min leg and diluted in the median. That's arguably acceptable given Gate purpose (catch wholesale drift), but worth noting as boundary.

Also: is 0.70 too tight for 3-char translations (documented limitation 3)? Yes, documented.

Another check: the empty-pair rule: both empty=1.0. Rationale: "two runs agree that the region has no translation — behaviour matches". Reasonable, but consider: a region whose source text is non-empty but both runs return empty translation (OCR empty source vs. skip). K11 ro=9 source "\n\n" (whitespace only) — so its source is effectively empty. The doc says "K11 ro=9 OCR 空文本、ro=13 SFX SKIP". Note that both empty=1.0 counts as identical and inflates the "identical" count and pulls median up. In K11, 2 of 13 pairs are empty_both. They're excluded from the non-empty subset (11) but included in "all pairs" (13) used for the gate. That's a disclosure question: if both-empty pairs count as 1.0, and some cases might have many empty regions, the median could be inflated by un-translated regions. Actually more critical: single-side empty = 0.0 is fail-closed (good). But what about "both empty" where the region has non-empty source? Could mask a systematic translation failure — e.g., if the provider is down and returns empty for all regions in both runs, the gate would PASS with median 1.0! That's a serious blind spot: a provider that consistently fails to translate (empty output) yields similarity 1.0 for all pairs → PASS despite zero translation output. This is a real P2/P3 finding: the gate has no coupling to translation coverage (non-empty ratio); both-empty=1.0 means an all-empty run passes. Need a coverage precondition (e.g., non-empty source → non-empty translation ratio) to close this hole. The doc registers the rule as "行为一致" but doesn't register the failure mode "systematic empty output passes". That's a gap in limitation registration and in the gate definition. I think this is the strongest methodological finding. Severity: P2 (gate correctness gap, but no natural sample; and other gates (translate scoring) exist elsewhere... though those are separate thresholds; the determinism gate alone would pass). Let me verify: is there another gate requiring translations to be non-empty? quality-thresholds §7 row 8 translate 对白 median≥3.5 — that's a different gate. But the determinism gate could pass vacuously. Worth P2.

Also check data extraction: `translations_by_reading_order` builds `out[ro] = {...}` — if two translate_details share the same reading_order (shouldn't), silently overwritten. Also `order[detail["region_id"]]` raises KeyError if a translate_detail's region_id is not in regions → uncaught KeyError (not fail-closed with a clear message). Also if a region has no translate_details entry (e.g., a region skipped in translate), then t1 lacks that ro; if both runs skip the same region, both lack → set equality holds and the pair is silently dropped from the calibration, with no registration of the dropped count. This is a data-completeness gap: regions present in `regions[]` but absent from `translate_details[]` are silently excluded from n_pairs. Does that happen for K11 (13 regions vs 13 details)? Need to check the summary. The doc claims n_pairs=13 = region count. If regions[] has 13 and details 13, fine. But the alignment check only compares t1 vs t2 sets, not vs the region set. So a silently-missing region in both runs is invisible. That's a fail-open direction hole (drop pairs → fewer pairs → median easier). Combined with the empty rule this is the "fail-open" criticism. Worth a finding (P2/P3): alignment completeness vs regions[] is not asserted; only cross-run set equality. Recommend asserting set(t1) == set(t2) == set(reading_order of all regions) and registering dropped-region counts.

Hmm, but careful: is that a real risk? translate_details might legitimately omit regions (e.g., region_type not translated). Need to check the summaries. Let me read qual-K11.json.

Also verify the "reading_order 集合不一致 → fail-closed" implementation: `set(t1) != set(t2)` → SystemExit. Yes implemented. Note: it compares sets of reading_order keys derived from translate_details, not from regions[]. And it's SystemExit with FATAL message, exit code non-zero — fine.

Another check: `pair_status` uses `.strip()` to determine emptiness, while similarity uses raw strings. So a pair where first="\n" and second="  " → status empty_both → similarity(" \n"?) Actually similarity("\n","  ") → both non-empty strings (truthy) → levenshtein=... a="\n" b="  " max_len=2, dist=2 → 0.0. But status = empty_both. So there's an inconsistency: status says empty_both (both empty) but similarity may be < 1.0. In K11 ro=9, text_first="" and text_second="" exactly, so similarity=1.0. Also note the nonempty subset in case-level uses `status not in ("empty_both",)` while the aggregate nonempty uses `status not in ("empty_both","empty_one_side")` — inconsistent definitions between per-case and aggregate! Let's check: in build_pairs: `nonempty = [p for p in pairs if p["status"] not in ("empty_both",)]` — so empty_one_side pairs would be INCLUDED in per-case nonempty. In main: `nonempty_pairs = [p for p in all_pairs if p["status"] not in ("empty_both", "empty_one_side")]` — excluded. Also `raw_nonempty`/`normalized_nonempty` distributions. Since no empty_one_side occurs, the numbers coincide today, but the two definitions diverge if a one-side-empty pair appears. That's a latent inconsistency worth flagging (P3, low impact but a real defect in a "registered gate definition" artifact). Also note n_pairs_nonempty in case = 11 for K11 (13 - 2 empty_both) and aggregate n_pairs_nonempty = 16 (18-2). Consistent numerically.

Also the `distribution` n_identical counts v==1.0 and n_variant counts v<1.0; sum = n. Fine.

percentile: linear interpolation, no issue. P10 for BJ02 = 0.85: sorted [0.75,1,1,1,1], k=(5-1)*0.1=0.4 → f=0, c=1 → 0.75 + (1-0.75)*0.4 = 0.85. Correct.

median for K11 raw_all = 0.9474: sorted values: 0.75,0.75,0.75,0.8571,0.8571,0.9474,0.9? wait let me sort: values = [0.75,0.75,1,1,0.8571,0.8571,1,0.75,1,0.9474,0.9,1,1]. Sorted: 0.75,0.75,0.75,0.8571,0.8571,0.9,0.9474,1,1,1,1,1,1 → n=13, median = 7th = 0.9474. ✓. raw_nonempty (11): remove two 1.0s (ro=9,13) → sorted: 0.75,0.75,0.75,0.8571,0.8571,0.9,0.9474,1,1,1,1 → median = 6th = 0.9 ✓.

normalized K11 all: values [0.75,0.75,1,1,1(ro5),0.8571,1,0.75,1,1(ro10),0.875,1,1] → sorted: 0.75,0.75,0.75,0.8571,0.875,1,1,1,1,1,1,1,1 → n=13, median=7th=1.0 ✓. n_variant=5 ✓ (0.75,0.75,0.75,0.8571,0.875). min 0.75, max 0.875, median of variant subset = 0.75 ✓.

Aggregate raw_variant_only n=8 median 0.8035: values [0.75,0.75,0.75,0.8571,0.8571,0.9,0.9474,0.75] sorted: 0.75,0.75,0.75,0.75,0.8571,0.8571,0.9,0.9474 → n=8 → median = (4th+5th)/2 = (0.75+0.8571)/2 = 0.80355 ✓.

Aggregate raw_nonempty median 0.9737: n=16 sorted: [0.75×4, 0.8571×2, 0.9, 0.9474, 1.0×8] = 4+2+1+1+8=16 → median = (8th+9th)/2 = (0.9474+1.0)/2 = 0.9737 ✓.

Good, arithmetic checks out. And with 8 variants out of 18, raw median = 1.0 (all-pairs) — fine.

Now the normalized aggregate: 6 variants in 18 → median 1.0 ✓.

Now verify "浮动 ≤8 对 → median 恒=1.0". With 18 pairs and 8 floats, sorted position 9 and 10 are 1.0 → median 1.0 ✓ (assuming floats always <1.0). Actually careful: §4.2 says "浮动 ≤8 对（<50%）时 median 恒=1.0（PASS）" — correct: with 8 floats, positions 1-8 are floats (<1.0), positions 9-18 are 1.0 → median=(1+1)/2=1.0 ✓. With 9 floats → position 9 is a float. Median=(v9+1.0)/2. v9 ≤ max float. If measured band max 0.875 → ≤0.9375 ✓. So conditional on band. Note also the band depends on all floats ≤0.875; the probe max was 0.9375. So "恒 FAIL" requires the assumption. It's disclosed as "以实测浮动幅度 [0.75, 0.875] 计" but the word "恒" combined with a synthetic probe showing 0.9375 exists makes it a bit fragile. P3.

Also "≈约半数浮动即红线" for K11 (13 pairs): ≤6 floats → median 1.0; 7 floats → median=(v7+1)/2, with v7 ≤0.875 → ≤0.9375 FAIL. So the boundary is not exactly "half" for other n. Fine.

Now the normalized vs raw argument. Gate uses normalized. Concern: normalization strips ALL whitespace, including newlines. Stripping all whitespace means "AB" vs "A B" identical; also CJK text with newlines is collapsed. Is that legitimate for translation stability? The doc argues it matches project CER normalization §0. Need to verify quality-thresholds §0 actually says strip all whitespace, …≡..., casefold. Let me read the file §0.

Potential issue: normalization also removes spaces between Latin words, so "hello world" vs "helloworld" → identical. And casefold. For similarity that's a mild leniency. The doc registers limitation 5. Reasonable.

Now check whether measure_cer.py's normalization matches. Let's read it.

Also check `experiments/M2-TA3-B/measure_cer.py` exists. The script says "replicated from experiments/M2-TA3-B/measure_cer.py". If that file's normalization differs (e.g., doesn't strip all whitespace, or doesn't casefold), the claim "identical to measure_cer.py" is false. Must verify.

Let me look at the worktree now.

Also verify scope: no src/tests. Diff shows 6 files: handoff, task, script, calibration.json, calibration.md, phase2-plan.md, quality-thresholds.md — that's 7 files. Handoff says "6 files, +1338/−7". Let me count diff files: 
1. doc/handoffs/M2-QUAL-DETERM-CALIB-e3b7c48d.md (new)
2. doc/tasks/M2-QUAL-DETERM-CALIB.md
3. experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py (new)
4. verification/M2-QUAL-DETERM-CALIB/calibration.json (new)
5. verification/M2-QUAL-DETERM-CALIB/calibration.md (new)
6. verification/M2-TA3-B/phase2-plan.md
7. verification/M2-TA3-B/quality-thresholds.md

That's 7 files, not 6. Handoff says "交付物（commit e3b7c48d，6 files，+1338/−7）". Hmm — maybe the commit e3b7c48d contains 6 files and the handoff file is the 7th in a later commit (tip=2400b57a). Indeed: implement=e3b7c48d, tip=2400b57a (handoff). So the diff base..tip includes 7 files; the e3b7c48d commit has 6 files (the handoff doc being added in the follow-up commit 2400b57a). Wait but the task file modification (status delivered) — was that in e3b7c48d? Probably. So 6 = script, calibration.json, calibration.md, thresholds, phase2-plan, task. That adds up to exactly 6. ✓. So the handoff was committed separately (2400b57a). Good, consistent.

But the Review is against tip=2400b57a presumably; the diff is base..tip. Also does the handoff doc at tip get committed? Yes as new file.

Now check the worktree for the file list and whether there's any uncommitted content. Can't run git. But can read .git? For a worktree, .git is a file pointing to gitdir. We could check `git status` is impossible without shell. So NOT_VERIFIED for porcelain cleanliness. Actually maybe I can read the diff only. The user says NOT_VERIFIED for runtime items.

Hmm — but can I verify "porcelain 干净"? Without shell, no. Leave as NOT_VERIFIED.

Let me now check whether e3b7c48d exists as claimed and that the diff equals base..tip. I can read .git files: G:\CODEX\New Manga.worktrees\M2-QUAL-DETERM-CALIB-zcode\.git is a file containing "gitdir: ...". Let me read it, and read refs. Or maybe simpler: read `G:\CODEX\New Manga\.git\worktrees\...`. Let's check what's readable.

Let me first list the worktree root and the relevant directories via glob.

Let me batch several calls:
- read calibration.md at tip (to confirm it matches diff; and check file exists)
- read quality-thresholds.md §0 and §5/§7
- read measure_cer.py
- glob summaries
- read qual-K11.json

Let me do glob first to find paths.

Actually let's batch: glob for "verification/M2-TA3-B/phase2/summaries/*.json" in the worktree; read quality-thresholds.md; read measure_cer.py; read calibration.md.

I'll use the worktree path as `path` for glob.

Let me also read the task doc for ACs.

Batch 1.
dsh: reasoning:
Important: glob for `verification/M2-TA3-B/phase2/summaries/*.json` in the worktree → "No files found". That's alarming. The calibration data source is `verification/M2-TA3-B/phase2/summaries/qual-K11.json`. If those files don't exist in the worktree, then... Maybe glob path handling. Let me check the directory exists.

Note measure_cer.py's docstring mentions cer-summary.json denominator "ko K11 13 regions" — so K11 has 13 regions in the summary.

Let me glob more broadly.

Also note: REPO_ROOT for calibrate_determinism.py = parents[2] of `experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py` → parents[0]=M2-QUAL-DETERM-CALIB, [1]=experiments, [2]=repo root. Correct.

And calibration.json's calibration_source.summaries_dir records the absolute worktree path — a machine-specific absolute path baked into a committed artifact. Minor finding (portability/reproducibility; also leaks local path). Also `calibration.json` is a generated artifact containing absolute path — if regenerated at the main repo path, diff churn. P4/P3.

Let me now find the summaries dir. Maybe the glob tool's path needs to exist; let's glob "verification/M2-TA3-B/phase2/**" to see.
dsh: reasoning:
Good — `**/qual-*.json` works but the anchored `verification/M2-TA3-B/**` pattern didn't (weird glob semantics — maybe because pattern with `/**` and the path arg? Whatever).

Note: K11.rerun.json exists, BJ02.rerun.json, K01.rerun.json. Good — the three rerun cases (BJ02,K01,K11).

Now let's read qual-K11.json and qual-K11.rerun.json, and BJ02 pair, and K01 (region_count=0 claim). These are large possibly. Let me read them.

Also need quality-report.md §5 for F5 observation "7/11".

And thresholds §5/§7 lines around 160-214.

Let me batch reads.
dsh: reasoning:
Verified K11: regions 13, translate_details 13, reading_order 1..13, region_type from regions[]: 13 = sfx, others speech. Note the calibration script's `region_type` uses detail.get("region_type") first, which exists in translate_details (e.g., "sfx" for ro=13). ✓ matches.

Note the regions[].region_type for ro=13 is "sfx" and translate_details has "sfx". ✓.

Also note K11 details status: details.translated = 11 while 13 regions. So 2 regions had no translation (ro=9 OCR empty source "\n\n", ro=13 SFX skip). Both translate_details present with empty translated_text. Good — no silent drop for K11. translate_details count = 13 = regions count. ✓ So set(t1) == all reading orders.

Now BJ02 and K01. Let me read BJ02 + BJ02.rerun + K01.

Also the quality-report.md §5 for the F5 record (7/11 or 7/13?). The task background says "K11 Run2 译文浮动 7/11". The handoff says "raw 口径 K11 浮动 7/13（非空 7/11）". Let me check quality-report §5.

Let me batch: read qual-BJ02.json, qual-BJ02.rerun.json, qual-K01.json, and quality-report.md (search for F5 / 7/11).

Given file sizes, use grep for quality-report.

Let me do reads and greps.
dsh: reasoning:
BJ02: 5 regions, 5 details, first-run texts match calibration.json ✓ (ro=1 别说得那么冠冕堂皇, ro=4 所谓强大).

Interesting: BJ02 ro=2 source "必ずオペはしろ．．．" (fullwidth dots) → translation "一定要做手术……". In the calibration.json, BJ02 ro=2 text_first = "一定要做手术……" — yes present. Note quality-thresholds §0 says 统一省略号与长音符（…≡...）— normalization converts "…" to "..." and also \u22ef. In BJ02 translation "一定要做手术……" → "一定要做手术......" both runs identical anyway.

Wait — calibration.json shows BJ02 ro=2 text as "一定要做手术……" — good.

K01: region_count=0 on first run. Need to check K01.rerun.json too (the claim "K01 has region_count=0 on both sides"). Let me check quickly.

Also need to check K11.rerun.json to verify the second-run texts (e.g., ro=1 "小萝卜？", ro=6 "小萝卜？！！！", ro=11 "哦 我的\n泰阳阳！！"). The calibration.json claims text_second values. Must verify, especially ro=5 normalized equivalence and ro=10.

Also verify the "7/11" observation in quality-report §5.

Let me read qual-K11.rerun.json and grep quality-report.md.

Also check the note: K11 ro=11 first "哦 我的\n泰阳!!" vs second "哦 我的\n泰阳阳!!" — raw sim 0.9? Let's compute: normalize both: "哦我的泰阳！！" = 7 chars? 哦,我,的,泰,阳,！,！ = 7. second: "哦我的泰阳阳！！" = 8 chars. Wait but the JSON says text_first = "哦 我的\n泰阳！！" → normalize → "哦我的泰阳！！" = 7 chars (哦 我 的 泰 阳 ！ ！). second → "哦我的泰阳阳！！" = 8 chars. levenshtein = 1 (insert 阳). 1 - 1/8 = 0.875 ✓ matches similarity_normalized 0.875. raw: "哦 我的\n泰阳！！" length 9? 哦,space,我,的,\n,泰,阳,！,！ = 9. second "哦 我的\n泰阳阳！！" = 10. lev=1 → 1-1/10 = 0.9 ✓.

ro=6: "胡萝卜？！！！" → 7 chars; "小萝卜？！！！" → 7; lev=1 → 1-1/7 = 0.8571 ✓.

ro=1: 胡萝卜？ = 4 chars → 0.75 ✓.

Now let me verify the second-run file.

Also might check qual-BJ02.rerun.json.

Let's batch: read qual-K11.rerun.json (709 lines?) and grep quality-report for "7/11" and F5.
dsh: reasoning:
Verified the K11 rerun texts match calibration.json's text_second values exactly, including ro=5 "本以为\n没必要\n做到这种地步", ro=10 "咔咯咔咯咔咯\n咔咯沙沙 沙沙\n沙沙沙沙", ro=11 "哦 我的\n泰阳阳！！".

Also the quality-report F5 says "Run2 译文浮动（7/11 非空口径，DSH r1 修正原 7/13 混用分母）". So the "7/11" observation is raw-string based. The handoff claimed "raw 口径 K11 浮动 7/13（非空 7/11）" — slightly muddled phrasing but the calibration.md says "K11 raw 浮动 7/11 非空对（复现 quality-report F5 已登记的 7/11 观察）" ✓. But note the handoff verification table row says "raw 口径 K11 浮动 7/13（非空 7/11）" — in the AC4/handoff table: "AC1 K11 观察复现 | raw 口径 K11 浮动 7/13（非空 7/11）". Hmm, this is contradictory with the F5 record which explicitly corrected the denominator to 7/11 ("DSH r1 修正原 7/13 混用分母"). The calibration.md correctly uses 7/11. The handoff's "7/13（非空 7/11）" reintroduces the mixed-denominator phrasing that quality-report explicitly corrected. Actually "7/13" if you mean "7 variant out of all 13 pairs" is factually true as raw_all_pairs.n_variant=7 — and the parenthetical "(非空 7/11)" clarifies. But given quality-report explicitly says the 7/13 was a "混用分母" error, restating 7/13 first in the handoff (even with a parenthetical) risks re-propagating the corrected error. Minor doc finding (P4).

Also let me confirm the K11 rerun region/reading_order mapping: the rerun translate_details order — the first detail in rerun (region_id 591425e1...) has translated "小萝卜？" and source 당근아? Which reading_order? The rerun's regions[] should map that region_id to reading_order 1. The calibration script maps via the rerun's own regions. Since the script output shows ro=1 text_second 小萝卜？, and the rerun translate_details order matches, plausible. But I should verify the rerun regions[] has region_id 591425e1 → reading_order 1. Important because the whole alignment validity rests on region_id→reading_order within each run. Let me check lines 136-300 of the rerun file.

A potential subtlety: does the rerun summary contain a *different* reading_order assignment? If rerun's reading_order for the region is also 1, alignment works. Let me verify a few: rerun regions[] mapping.

Let me read the rerun file from line 130 to 300.

Also, I want to verify the claim "region_id 每 run 重新生成，同 bbox 两轮 uuid 不同" — the rerun region_id for reading_order 1 is 591425e1... vs first run eada0f25... Different ✓, while bbox should be the same. Let me confirm bbox x=45,y=6,w=123,h=48 for rerun ro=1.

Let me read that range.
dsh: reasoning:
Confirmed: K01 both runs region_count=0 → excluded from calibration (script comment says "K01 has region_count=0 on both sides"). ✓ But note: the script's comment says "The only two M2-TA3-B2 cases that have a run+rerun summary pair with non-trivial region translations (K01 has region_count=0 on both sides)". However — the rerun set is only BJ02, K01, K11 (3 cases, R15). So the calibration uses 2 of the 3, and the ko-webtoon family (K01) contributes nothing. That means the "3 case covers three families" design of R15 is not actually covered by the calibration: only ja BJ + ko P&C. This is a divergence worth noting: the Gate is defined over "固定 3 case (BJ02/K01/K11)" in thresholds, but K01 gives NO pairs (region_count=0, a known defect F1/attribution data:no-regions-detected). So when the Gate is executed in a future run, K01 must be handled: the script currently would... if run on K01 with both sides region_count=0 → t1 = {} and t2 = {} → set equal → pairs = [] → distribution over empty list → min/median None → gate_verdict NO_DATA. Then in main, `distribution([])` → min None; gate_verdict returns "NO_DATA". But the aggregate would include 0 pairs. And notably `render_markdown` would then do `agg['normalized_all_pairs']['min']` = None → prints None; and `cases[0]` indexing `k11 = cases[0]; bj02 = cases[1]` — hardcoded positions! If CALIBRATION_CASES changes order or a case yields different results, the report key readings would break/mislabel. Minor robustness issue (P4).

More importantly: the Gate as written in thresholds §5 says "固定 3 case ... 全部对齐对 ... median ≥0.95 且 min ≥0.70 方为 PASS". With K01 producing zero pairs, the thresholds text doesn't state how zero-pairs cases are treated (NO_DATA vs PASS vs exempt). The calibration script returns NO_DATA for such a case, and would SystemExit only if the two runs' reading_order sets differ (both empty → equal → no exit). So a case with zero regions in both runs yields NO_DATA and the calibration does not define whether the Gate PASSes. That's an integration gap: the authoritative wording (thresholds §5) should state the region_count=0 exemption (R11) applies. Actually R11 exemption exists in §6 for product existence. Hmm, thresholds §5's new entry doesn't mention the K01 no-region exemption. The script's fail-closed only covers mismatched sets — a genuine asymmetry: if run A has 13 regions and run B has 0 (e.g., detect regression in the rerun), then t1 ≠ t2 → SystemExit → fail-closed ✓. Good.

But the case where BOTH are 0 → NO_DATA, undefined in thresholds. I'd flag P3: thresholds §5 should state zero-pair case handling (NO_DATA/豁免), since the fixed 3-case set includes K01 which is currently 0/0.

Now, let me verify the empty-source region ro=9: source "\n\n" and both translations empty → empty_both → 1.0. Note: this region has an empty OCR source, so it isn't a "translation behaviour agreement" but an upstream empty. The gate counts it as perfect similarity. That's the blind-spot I identified. K11's non-empty count 11 vs 13: 2 such pairs are excluded from "非空" subset but INCLUDED in the Gate's all-pairs (the gate uses `distribution([p["similarity_normalized"] for p in pairs])` = all pairs including empty_both). The report says "（同 case 两次 run 全部对齐对，含空对规则）" ✓ disclosed.

So the blind spot: all-empty run → all pairs 1.0 → median=1.0 min=1.0 → PASS. Real risk: if the translation provider fails wholesale (returns "" for everything) in both runs, the determinism Gate PASSes. Combined with other gates (translate scoring median ≥3.5 for dialogue) there is a separate gate that would catch empty translations — but that's a different阶段 gate on a different artifact (manual scoring worksheet), and the determinism gate is the one being defined here. I'll flag as P2: gate definition lacks a coverage precondition (non-empty translation ratio / min non-empty pairs) — recommend adding to the authoritative wording (e.g., require non-empty-source regions to have non-empty translations, or register explicitly that all-empty passes and is caught by the §3/§7 translate scoring gate). Since AC4 asks for limitations登记, this specific failure mode isn't in the 5 limitations. Good finding.

Let me double check whether the limitation list mentions it... The 5 limitations: n=2; no natural FAIL; short-translation granularity; Run1 unmeasured; normalization dependence. No all-empty blind spot. ✓ finding.

Next: the alignment completeness issue. `translations_by_reading_order` only iterates translate_details. For K11, 13 details = 13 regions ✓. For BJ02, 5 = 5 ✓. So today no drop. But a future case where a region has no translate_detail entry (e.g. run2 per_region failed and no detail written) would silently reduce n_pairs rather than fail-closed. The requirement "region 数不同怎么办——对齐失败 fail-closed" is only enforced on the intersection-of-details key sets, not on the region sets. Also, if translate_details has an entry whose region_id isn't in regions[], `order[detail["region_id"]]` raises KeyError → crash (fail-closed but ugly traceback, not the registered SystemExit). Acceptable but worth a P4.

Additionally: duplicates — if two details map to the same reading_order (e.g. duplicate region_id), dict silently overwrites → undercount. Minor.

Now the bigger methodological question: is reading_order a valid alignment key across runs? The script relies on each run's own `regions[].reading_order` + region_id join. The concern: reading_order is regenerated per run and might not be stable (e.g., ordering depends on detection order/bbox sort). Evidence check: K11 first vs rerun bboxes — the bbox for reading_order 1 in first run (45,6,123,48) equals rerun's reading_order 1 bbox (45,6,123,48), and all 13 look identical in sequence. Actually, note that reading_order here is NOT sorted by y: ro=13 has y=564 while ro=12 has y=1458. So reading_order is not a simple spatial sort; there is an explicit ordering (page reading order). But the crucial check: is reading_order stable across runs? We can verify by comparing bbox sequences of run1 vs rerun for K11. From what I've read, ro 1..11 match exactly (x,y,w,h). I read rerun 1-11; first run 1-13. Let me verify rerun 12-13 too (lines 265-300 shown partially: ro=11 bbox 174,1252,135... then 12,13). The earlier read showed rerun ocr_details ro=13 bbox x=805 y=564 w=173 h=197 — identical to first run's ro=13 ✓. And rerun's regions[] ro=13 (b2dad79f) bbox 805,564? The rerun ocr_details line 556-565 shows region_id b2dad79f with reading_order 13 and bbox 805,564,173,197 ✓. So bbox↔reading_order mapping is identical across runs → alignment valid. Good: I can state that I verified bbox-level identity for K11 (13/13) as a proxy, but the script itself doesn't verify bbox/geometry consistency. Recommendation (P3): add a geometric sanity assertion (bbox equality or IoU) when aligning by reading_order, since reading_order stability is an assumption; bbox is the only cross-run geometric identity available. That would make the alignment fail-closed on a reading-order drift (e.g., detect order change would silently misalign pairs and produce false floats). This is a genuinely valuable finding: if run B's reading_order assignment shifts by one (e.g., detector returns regions in a different order), the alignment silently pairs different text and yields massive false floats — no protection. The current guard (set equality of reading_orders) cannot catch permutation of the same key set. Strong P2 finding.

Hmm, is that too speculative? The Gate's whole validity rests on the alignment key. A pure key-set equality check cannot detect a permutation. The project has bbox available in both runs and cross-run bbox equality is empirically confirmed for K11. So recommending fail-closed on geometric mismatch (or at minimum registering the assumption in limitations) is a fair, well-founded finding. Severity P2 (methodology: unverified alignment assumption, silent failure mode → could produce spurious FAIL or spurious PASS).

Let me also verify the BJ02 rerun to confirm the 所谓强啊 pair (ro=4).

Also need to check `region_type`: calibration.json K11 ro=13 says "sfx" — from translate_details region_type ✓.

Now, "18 对齐对（K11 ko 13 + BJ02 ja 5）" — verified 18 ✓.

Next verification: does the script actually regenerate calibration.json deterministically and match the committed one? Can't run Python (no shell). NOT_VERIFIED for re-run. But I can statically verify the JSON structure matches what render_markdown would produce... paritally. I can verify the printed "关键读数" vs JSON numbers: e.g., the report says "实测浮动幅度全部落在 [0.75, 0.875]" — agg_v min 0.75 max 0.875 ✓ (normalized_variant_only). And "K11 n=5、min=0.75、median=0.75" ✓ JSON.

Wait — one inconsistency: In render_markdown, line: `f"——实测浮动幅度全部落在 [{agg_v['min']}, {agg_v['max']}]，是 min 阈值（{PROPOSED_GATE['min_min']}）的锚。"` uses agg_v (aggregate normalized variant only) → [0.75, 0.875] ✓.

Another: §4.1 says "实测最坏浮动对 = {agg['normalized_all_pairs']['min']}" = 0.75 ✓ and "（4 字译文单字替换，K11 ro=1/2/8 与 BJ02 ro=4）" — ro=1 胡萝卜？(4 chars) ✓, ro=2 小萝卜！(4) ✓, ro=8 胡萝卜！(4) ✓, BJ02 ro=4 所谓强大 (4) ✓. Good. But note K11 ro=11 is 0.875 on 8 chars, and ro=6 0.8571 on 7 chars. Consistent.

Hmm wait: ro=6 "胡萝卜？！！！" is 7 chars → 1-1/7=0.857 ✓.

Now the interesting bit: the claim in §4.1 "（provider 版本/提示词微调可能带来 ±1 编辑差）" — as analyzed, 0.05 margin ≠ 1 edit for 4-char strings. Let me be precise: for the worst measured pair (4 chars, 1 edit → 0.75), one more edit → 2/4 = 0.5 < 0.70 → FAIL. So the 0.05 margin does NOT absorb ±1 edit at the anchor magnitude. The stated rationale is quantitatively wrong. This is a solid P2 (阈值论证) finding. Also note min≥0.70 with 0.75 anchor means the tolerance is 0.05 absolute = 1/20; for a 4-char string, a 0.05 tolerance is 0.2 characters. So effectively the min leg has almost zero margin above the observed worst float: any worsening beyond a fraction of a character on that 4-char pair → FAIL. That means the Gate is brittle in the direction of false FAIL on short translations — which the doc partially acknowledges (limitation 3, 3-char). Actually limitation 3 is about 3-char; the same phenomenon applies at 4-char (margin 0.05). I'd recommend either lowering min (e.g., 0.60, i.e., allow 2 edits on a 4-char string) or explicitly restating the margin semantics ("0.05 absolute, not one character") in both calibration.md and thresholds. Good actionable finding.

Conversely, is 0.70 too loose? For long texts, 0.70 allows up to 30% char replacement in a single region undetected by the min leg. Given median ≥0.95 covers the aggregate, a single region could drift 30% and pass. The synthetic drift_40 min=0.5 FAILs, so the min leg's effective detection threshold is ~30%+ drift on the worst pair. Disclose as boundary. P3.

Now the median leg's blindness to low-magnitude systematic drift (all long-text regions drifting by 1 char → similarity 0.95+ → median ≥0.95 PASS). That's arguably intended (1 char = benign). But the report §4.2 claims the median leg catches "全部 region 系统性浮动" — the synthetic probe single_char_ge4 shows FAIL only because its texts are short (median 0.857, max 0.9375). For a case with longer texts, the same "all regions float by 1 char" scenario would PASS. So the claim "「全部对 1 编辑浮动」（系统性轻微变化）→ median leg FAIL" is over-general: it holds for the probe's string-length distribution, not universally. That's a P3 finding on threshold argumentation precision (report §4.3 演示结论 wording and probe_conclusion).

Let me compute the single_char_ge4 probe: n=15, min 0.75, median 0.857, max 0.9375. The 15 texts are non-empty first-run translations of K11+BJ02: lengths normalized: 4,4,4,4,7,3? wait let me list normalized first-run texts of the 16 non-empty pairs minus... The probe uses nonempty_pairs (16) but n=15 because single_char_ge4 skips texts with len<4 (picker returns 0 → skip). Which text has len<4? BJ02? normalized texts: K11: 胡萝卜？(4), 小萝卜！(4), 胡萝卜？(4), 胡萝卜？！(5), 本以为没必要做到这种地步(11), 胡萝卜？！！！(7), 咦？床底下也有你？(8), 胡萝卜！(4), 咔咯咔咯咔咯咔咯沙沙沙沙沙沙沙沙(13? let's see 咔咯咔咯咔咯=6, 咔咯沙沙沙沙=6, 沙沙沙沙=4 → 16), 哦我的泰阳！！(7), 咕噜噜(3), BJ02: 别说得那么冠冕堂皇(9), 一定要做手术......(9? 一定要做手术+6 dots=11-12), 所谓正确，就是软弱(10), 所谓强大(4), 就是说不行(5). 

The 3-char one is 咕噜噜 → skipped by the >=4 filter → n=15 ✓. Note it's the very pair the limitation 3 talks about (3-char). Good, consistent: n=15 of 16 non-empty.

So median of 15 values = 8th. Values: for len 4 → 0.75; len 5 → 0.8; len 7 → 0.857; len 9 → 0.889; len 11 → 0.909; len 16 → 0.9375; len 8 → 0.875; len 13? etc. Sorted ascending: 0.75 (×4: 胡萝卜？, 小萝卜！, 胡萝卜？, 胡萝卜！, 所谓强大 = 5 pairs of len 4!). Let me count len-4 texts: K11 ro1 胡萝卜？, ro2 小萝卜！, ro3 胡萝卜？, ro4 胡萝卜？！(5 chars), ro8 胡萝卜！, BJ02 ro4 所谓强大. So len4: ro1, ro2, ro3, ro8, BJ02ro4 = 5 values at 0.75. len5: K11 ro4 胡萝卜？！(5) → 0.8; BJ02 ro5 就是说不行(5) → 0.8. len7: K11 ro6 胡萝卜？！！！(7) → 0.857; K11 ro11 哦我的泰阳！！(7) → 0.857. len8: K11 ro7 咦？床底下也有你？(8) → 0.875. len9: BJ02 ro1 别说得那么冠冕堂皇 (9) → 0.889; BJ02 ro3 所谓正确，就是软弱 (10) → 0.9; 一定要做手术......(need count: 一定要做手术 = 6 chars + "......" 6 = 12) → 0.9167. Let's not be exact.

Sorted ascending first values: 0.75×5, 0.8×2, 0.857×2, 0.875, then larger. n=15 → median = 8th value = ? positions: 1-5: 0.75; 6-7: 0.8; 8-9: 0.857 → 8th = 0.857 ✓ matches JSON median 0.8571. min 0.75 ✓ max 0.9375 (the 16-char one) ✓.

Good — internal consistency confirmed.

Now, drift_40: n=16 (all non-empty pairs including 3-char), min 0.5, median 0.5635, max 0.6667. Note the max 0.6667 means even the longest text got 40% replaced → 0.6 expected; 0.6667 for some. Fine.

But note something important about the probes: `perturb` uses `rng.sample(range(len(text)), min(n_chars, len(text)))` then `chars[p] = rng.choice(SUB_POOL)`. The substituted char could be the SAME as the original (pool may contain it) — e.g., for drift_40 the realized edit distance can be less than n_chars. This makes the probes slightly optimistic but doesn't affect claimed magnitude much. Also the pool consists of traditional-Chinese chars (嗎克啊乐欧课咯) while texts are simplified — fine, meant as opaque substitutions. Also since the same rng is shared across probes sequentially, the probes are deterministic given order (seed fixed) ✓. But note: probes consume rng in a fixed order → reproducible ✓. However, the raw texts are perturbed after normalization (base = normalize(text)) → perturbation on normalized text; then similarity(base, normalize(perturbed)) — normalize applied again. Fine.

One subtle bug: `perturb(base, n_chars, rng)` where base is normalized; substituting with pool chars, then `normalize()` of that — normalize strips whitespace and casefolds; pool chars are CJK so unaffected. Fine. But if the original text had whitespace (e.g., "哦 我的..."), base has it stripped, so the perturbation is applied to a text of shorter length than the raw. That means drift percentages are computed on normalized lengths — consistent with the normalized metric. Fine, and picker(text) uses `len(normalize(t))` ✓ consistent.

Another subtlety: the "single_char_ge4" probe skips texts with normalized len < 4 — so n=15. But the probe's `min_gate_verdict` PASS uses min=0.75 ≥ 0.70 ✓, and `gate_verdict` FAIL because median 0.857 < 0.95 ✓.

Now: `gate_verdict` is applied to probes and observed, and uses `PROPOSED_GATE`. ✓.

Now let's check the JSON's `threshold_evaluation.gate.min_min = 0.7` (not 0.70) — cosmetic.

Another check: calibration.json `case_id` "calibration_source.summaries_dir" contains the absolute worktree path. Already noted (P4 portability + committed machine path; also it will change when re-run in the main repo → artifact churn; and it reveals a local path, though other artifacts already contain absolute paths like scratch_root, so nothing new).

Now check the claim "实测仅此情形" (only both-empty occurs). Verified: all pairs statuses are identical/variant/empty_both. Let me confirm there's no empty_one_side in the JSON — from the dump: K11 statuses: variant, variant, identical, identical, variant, variant, identical, variant, empty_both, variant, variant, identical, empty_both. ✓ no empty_one_side. BJ02: identical×4 + variant. ✓.

Hmm, but the claim "双方空=1.0（实测仅此情形）" and the second run of K11 ro=9: source "\n\n" → translated_text "" both. Note that the ro=9 region has ocr_text "\n\n" — its OCR is effectively empty (whitespace only). So the "empty translation" is a consequence of empty source. The gate rule treats it as 1.0.

Now let's also check whether the pair's source_text in calibration.json is from the FIRST run (a["source_text"]). For K11 ro=9 source "\n\n" ✓.

Now scope check: does the diff touch anything outside allowed surface? Files: doc/handoffs/**, doc/tasks/M2-QUAL-DETERM-CALIB.md, experiments/M2-QUAL-DETERM-CALIB/**, verification/M2-QUAL-DETERM-CALIB/**, verification/M2-TA3-B/{phase2-plan.md,quality-thresholds.md}. All within allowed surface ("Task/Handoff", "verification/M2-TA3-B/** 的 thresholds/plan 修订"). ✓ No src/tests/contracts/STATUS. qual-*.json not in diff ✓ (I verified the diff file list: 7 files, none is a summary JSON). ✓

But wait: what about experiments/M2-TA3-B/**? The script says it replicated normalize from measure_cer.py without importing; the diff doesn't modify measure_cer.py ✓.

Now, was the quality-report.md updated to record the F5 解除? The Task's AC3 says thresholds §5/§7/§1. The task file AC3 mentions "§5/§7/§1 的 superseded-pending 条目". The implementer only changed §5 and §7, not §1. Is there a superseded-pending in §1? Let me grep for superseded-pending / F5 in quality-thresholds.md to see if any remain. The handoff claims `grep -n "superseded-pending"` → only the F5 note's 解除 mention. Let me verify with grep, including the whole repo for other superseded-pending references related to determinism (e.g., phase2-plan, quality-report, REBASELINE_PLAN, STATUS, other tasks). If quality-report.md still says "重定义前 thresholds §5/§7 的对应条目按 superseded-pending 引用" — that's a historical record (report is a past run's record, shouldn't be rewritten). But other live docs (STATUS.md, REBASELINE_PLAN.md, M2-TA3-B.md task) might still reference the pending state. Those are outside the modifiable surface (doc/STATUS.md is 禁改). Let me grep the repo for "superseded-pending" to enumerate residual references — that informs the integration closure checklist.

Let me grep.

Also check doc/reviews/ directory for existing review files and naming convention.

Let me also confirm the diff is exactly base..tip by checking if there are other files at tip not in the diff... can't without git. I'll rely on the diff + NOT_VERIFIED.

Let me run the greps.
dsh: reasoning:
Findings:
1. Task AC3 says "§5/§7/§1 的 superseded-pending 条目替换" — but the deliverable only touched §5 and §7. Is there a superseded-pending in §1? The grep shows no §1 superseded-pending. So AC3's "§1" mention is probably an error in the Task text itself (the R9 original only added notes at §5 line + §5 note + §7 line 10 — confirmed by dsh r2 review R9: lines 168/171/204). So nothing missing; the Task's "§1" is a typo in the Task doc left uncorrected. The Task doc is within the allowed modification surface and the implementer didn't fix it. Minor documentation finding (P4): AC3 mentions §1 but no such item existed, and neither the owner nor the handoff noted the discrepancy. Actually handoff says "thresholds §5/§7" only — silently dropping §1. Should be registered as "AC3 §1 项核对为空（R9 原注只在 §5/§7/§5 尾注）" to close the AC honestly. Worth P4/P3.

2. quality-report.md still has two "superseded-pending" references (lines 189, 199) — those are historical F5 裁决点 records, and quality-report.md is arguably part of TA3-B2 delivered evidence. Is it in the allowed modification surface? Task allows `verification/M2-TA3-B/**`（thresholds/plan 修订+本 Task 产物）. So quality-report.md could be updated but "修订面" is narrowed to thresholds/plan. The handoff claims `grep -n superseded-pending verification/M2-TA3-B/quality-thresholds.md` → only the解除 mention. Fine for thresholds. But the residual references in quality-report.md mean a reader consulting the report still sees "重定义前 thresholds §5/§7 的对应条目按 superseded-pending 引用" which is now stale (the state has been resolved). This is a doc-consistency issue for the integration closure list. Since quality-report is a delivered evidence doc whose §5 is a historical record of the裁决点, a one-line "(已由 M2-QUAL-DETERM-CALIB 落地，2026-10-01)" annotation would be warranted — but modifying delivered evidence docs has its own discipline. I'll put it as a P4 with recommendation: either annotate or explicitly register that quality-report §8/§9 references are historical and intentionally not updated. Currently neither is done — the owner didn't mention the residual references anywhere, and the handoff's grep claim is scoped to thresholds only, which could give a false impression of "no残留". Good finding.

3. Task AC1 says "区分「浮动对」（7/11）与「相同对」" — the task's own AC anchors to 7/11 raw; deliverable provides both. OK.

Now let me check doc/reviews conventions: existing r1/r2 files. Fine.

Now check whether calibration.md/JSON in the worktree match the diff exactly (they should). Also let me check the tail of calibration.json (already seen in diff).

Let me also check the tail of calibration.md (diff showed 96 lines). Verified.

Now, one more check: the phase2-plan §4 step 5 edit says "复跑哈希对照 + 译文相似度 Gate 计算". Fine.

Now check the diff --check whitespace claim: can't run. NOT_VERIFIED.

Now let me examine whether `doc/reviews/` has prior DSH review file naming: M2-TA3-B2-<sha>-dsh-r1.md. The handoff recommends `doc/reviews/M2-QUAL-DETERM-CALIB-e3b7c48d-dsh-r1.md`. Consistent.

Now let me double-check one potential real bug in the script: `main()` — `global SUMMARIES_DIR, OUT_DIR` then argparse defaults are computed from the module-level globals BEFORE... wait: `parser.add_argument("--summaries-dir", default=str(SUMMARIES_DIR))` — after the global declaration, SUMMARIES_DIR still holds the module-level value (global declaration doesn't reset). So default is the repo path ✓. The handoff says the half-finished draft had a SyntaxError because `global` was declared after argparse referenced the global. Actually `global X` after a reference to X in the same function is a SyntaxError ("name 'X' is used prior to global declaration"). The fix moves `global` to the top ✓. Good.

Another: `SUMMARIES_DIR = Path(args.summaries_dir)` — assigning to the global ✓.

Then `build_pairs` uses the global SUMMARIES_DIR ✓.

Now: determinism claim "两次运行输出一致". The only randomness is random.Random(20261001) ✓ seeded. `json.dumps` deterministic ✓. Paths absolute: `str(SUMMARIES_DIR)` in JSON → if run with default it's the worktree path; if run from the main repo it'd be the main repo path → NOT byte-identical across environments. The claim "确定性" is within the same environment ✓, but the committed artifact embeds an environment-specific absolute path, so "两次运行输出一致" only holds in the same checkout. Since the handoff says a Reviewer should re-run to compare, re-running in this worktree reproduces byte-identically; re-running in the main repo would change 1 line. Worth a P4 note.

Now, the sorted() of pairs uses `sorted(t1)` (reading_order ints) ✓.

`flatten_pairs` order: K11 pairs then BJ02 ✓.

One more possible issue: `distribution` n_identical counts v == 1.0 — with rounding to 4 decimals, a similarity of 0.99995 would round to 1.0 and be counted identical. Only relevant for very long strings (len > 20000). Negligible.

Also `similarity` for empty pairs: both empty → 1.0; one empty → 0.0 ✓ as documented.

But `pair_status` uses `.strip()` while `similarity` uses raw strings. Consider first="\n" second="\n": status → empty_both; similarity("\n","\n") = 1.0 ✓ consistent. Consider first="\n" second=" \n": status empty_both but similarity = 0.0 (both truthy). Then this pair would be status empty_both but similarity 0.0 → counted as a variant in normalized_all_pairs (0.0)! And excluded from nonempty subset by status. That's the inconsistency: status-based subsetting can conflict with similarity-based classification. In the current data it doesn't occur (the empty pairs are exactly ""). But a future run with whitespace-only differences would produce a pair counted as floating with 0.0 similarity, dragging min to 0.0 → FAIL — actually fail-closed, fine, but the mixed semantics is a latent defect. Also the reverse: status empty_one_side but similarity... they'd be 0.0 consistently. I'll fold this into a P3 finding about status/类似度 定义不一致 (case-level vs aggregate nonempty subset definitions + strip vs raw).

Let me formulate that finding precisely:
- R-x (P3): `build_pairs()` 的 `nonempty` 用 `status not in ("empty_both",)`（保留 empty_one_side），而 `main()` 的 aggregate `nonempty_pairs` 用 `status not in ("empty_both","empty_one_side")`（排除）。两处「非空对」定义不同 → 同一 artifact 内 n_pairs_nonempty 分母不一致的隐患（当前数据因无 empty_one_side 而未显形）。同时 `pair_status` 用 `.strip()` 判空、`similarity` 用原串判空，二者在「仅空白差异」时结论可冲突（status=empty_both 但 similarity<1.0）。

Which also means: the K11 per-case n_pairs_nonempty=11 vs aggregate 16 — both consistent because no empty_one_side. OK.

Now, the biggest remaining question for the review verdict: are the findings blocking? The Gate definition has real gaps: (a) alignment permutation not guarded (no bbox cross-check); (b) all-empty blind spot; (c) margin math inconsistency (0.05 ≠ one character); (d) zero-pair (K01) handling undefined in the authoritative wording; (e) no coverage precondition. These are P2-ish. None invalidates the numbers (numbers verified correct), but several affect the authoritative wording (thresholds §5 双轨 entry) which is now the project's binding口径. I'd give verdict: PASS_WITH_CONDITIONS / 有条件通过 — round 1 findings must be fixed (or explicitly registered as limitations) before integration. Given the review format asks for a Verdict, I'll write "有条件通过（CONDITIONAL PASS）——数值与范围纪律通过；Gate 定义的 3 项 P2 缺口须在集成前以「局限登记或定义补全」方式闭合".

Hmm, let me weigh severity more carefully to be fair and not overreach:

(1) Alignment permutation risk (P2): The Gate's core assumption. Evidence: for K11 I verified bbox↔reading_order identical across runs, so the assumption held in this dataset. But the rewritten authoritative口径 says "按 reading_order 对齐" without any geometric cross-check; a future run where detect returns a different order would silently mispair. Also note reading_order is derived from the same detect output, so if detection changes, region sets may differ → but if the same 13 regions are ordered differently, sets are equal → silent. Real, cheap mitigation: compare bbox per reading_order across runs (fail-closed if mismatch) or register it as an explicit assumption. I'd say P2 (needs registration at minimum) — the report §1 states the alignment key but doesn't register "reading_order 跨 run 稳定性" as an assumption/limitation. Actually limitation 4 is about Run1 layer. So yes, a missing limitation. P2.

(2) all-empty PASS blind spot (P2): A run where translation returns empty everywhere passes both legs with 1.0. Evidence: the rule is registered as "双方空=1.0" with rationale "两次 run 行为一致". The gate is a *stability* metric, so arguably "consistently empty" is stable — but as a *determinism Gate for the pipeline*, a provider-down run would pass. Since a separate gate (§3 translate scoring: dialogue median ≥3.5, SFX non-fail ≥70%) exists, the risk is partly covered by another gate. But the determinism gate should at least require non-empty-pair count > 0 or coverage. P2 with the mitigation: add a coverage precondition or register the blind spot in limitations ("all-empty run passes; covered by §7 row 7/8 translate scoring Gate"). Good.

(3) min margin math (P2? P3?): The thresholds entry says "min 阈值锚在实测最坏浮动 0.75 下留 0.05 余量=0.70" — this text says "留 0.05 余量", not "一个字符" — so the authoritative wording (thresholds:168) is actually OK! It's the calibration.md §4.1 that says "取 0.75 − 0.05 = 0.70 留一个字符级测量余量（provider 版本/提示词微调可能带来 ±1 编辑差）". So the "one character" framing is only in calibration.md/JSON reasoning. Check JSON reasoning: "min gate = measured floating-pair band [0.75, 0.875] shifted down one character-level margin -> 0.70". Same claim in English. So the defect is in the calibration artifact's reasoning (which is cited by thresholds as the rationale). P3 (documentation/argument precision, doesn't change the number). But I should note it matters for interpretation: 0.05 on a 4-char anchor is 0.2 char, so the gate tolerates essentially zero additional degradation on the worst pair; worth stating honestly. P3.

(4) K01 zero-pair undefined (P2/P3): thresholds §5 names fixed 3 cases including K01, which produces 0 pairs in both runs. The Gate's PASS/FAIL/NO_DATA for a zero-pair case is undefined in the authoritative text; the script returns NO_DATA but thresholds says "全部对齐对 ... 满足 median≥0.95 且 min≥0.70 方为 PASS" — with zero pairs in a vacuous sense min/median undefined → NO_DATA, and combined with the R11 exemption in §6 it's probably intended as exempt. Must be stated. Also note: the R15 rationale "覆盖三家族" is now factually not achieved by the calibration (ko webtoon family absent) — thresholds §5's依据 cell says "校准=K11/BJ02 重跑对实测分布" which is honest, but the "固定 3 case 覆盖三家族" line remains and could mislead into believing 3-family coverage exists. P3.

(5) median boundary math conditionality (P3): "浮动 ≥9 对时 median ≤(0.875+1)/2=0.9375 恒 FAIL" — valid only if float magnitudes ≤0.875; the synthetic probe already produced 0.9375 floats (n=15, max 0.9375). So the "恒" is band-conditional; and for long-translation cases, an all-pairs-float-by-one-char scenario could PASS the median leg. Register as limitation or qualify. P3.

(6) Data-extraction completeness: no assertion that translate_details covers all regions[] (silent drop), and KeyError if a detail references an unknown region_id. P3.

(7) Scope/discipline: verified zero src/tests/contracts, qual-*.json untouched (not in diff), thresholds diff only touches the three superseded-pending-related places, phase2-plan three places. ✓ But need to double check the thresholds diff didn't change other threshold numbers: the hunks are exactly §5 row 168 (replaced row), new row 169 (added), the §5 note line, and §7 row 10. Numbers 0.10/0.15/0.20/0.25/3.5/80%/70% untouched ✓ (diff shows only those 3 hunks). ✓ 

Wait — the diff shows for quality-thresholds.md 3 hunks: @@ -165,10 +165,11 @@ (removes the old确定性复跑 row, adds two rows), @@ -201,7 +202,7 @@ (row 10). Hmm the second hunk shown is @@ -201,7 +202,7 @@ which includes line 202-205 region; and the note hunk @@ -165,10 +165,11 @@... Let me re-read: hunk 1 at -165,10 +165,11 covers the row replacement (lines 165-175ish) and includes the note line replacement (line 172). Hunk 2 at -201,7 +202,7 covers §7 rows 7-11 (the diff context shows rows 7,8,9,10,11 with row 10 changed). So only two hunks for thresholds. ✓ 

Also the diff for phase2-plan has 3 hunks ✓ (§1 row, §2.1 row, §4 step 5).

(8) tasks doc AC3 "§1" mismatch (P4).

(9) calibration.json embeds absolute worktree path (P4).

(10) handoff re-introduces "7/13（非空 7/11）" phrasing that quality-report explicitly corrected as 混用分母 (P4).

(11) The Gate applies only to remote chains; "remote" detection is by what? The Gate bifurcation criterion ("remote/随机采样翻译链" vs "mock/deterministic provider 链") isn't operationalized anywhere — how does a runner decide which track to apply? thresholds §5 says the runner should... The new口径 doesn't define the discriminator (e.g., provider id / a flag). For the future qualification run, the runner must know. Worth P3: add the operational discriminator (e.g., "--determinism-track remote|mock" or provider-based rule) or register as open.

That's a decent finding for integration.

(12) Also: the new Gate's PASS semantics with the empty-pair rule inflate the median: 2/13 K11 pairs are empty_both=1.0. If a case had most regions empty, median would trivially be 1.0. Tie to (2).

Now let me also double check the "18 对" and "浮动 6/18" claim vs the JSON: normalized_all_pairs n_variant=6, n=18 ✓. And "浮动幅度 [0.75,0.875]" ✓.

Also verify the claim in handoff "K11 浮动对 n=5、min=median=0.75（raw 口径 7/13 精确复现 quality-report F5 记录）" — "精确复现" is fine for raw_all=7/13 and nonempty 7/11.

One more: handoff claims "对半成品脚本的修正 4 处" — I can't verify the pre-existing draft (untracked, not in diff). NOT_VERIFIED.

Also "零 src/tests/contracts、TA3-B2 产物（qual-*.json）零改动、porcelain 干净、diff --check EXIT=0" — diff confirms no src/tests; porcelain/diff --check NOT_VERIFIED (no shell).

Now, one more important check: does the diff include any change to `doc/STATUS.md`? No ✓. Handoff correctly notes STATUS must be updated by the integrator ✓.

Now also verify that `verification/M2-QUAL-DETERM-CALIB/` didn't previously exist with other files (new files only ✓).

Let me now double-check the calibration.md §6 has exactly five limitations ✓ and JSON limitations has 5 strings ✓.

Let me check the ROOT repo (G:\CODEX\New Manga) — is the branch merged? Not my concern. But maybe check whether `doc/reviews/` exists and what the latest review file naming is, to give a correct next step. Also check REBASELINE_PLAN for the CALIB task's status (whether the plan says something about the F5 threshold / Gate definition that now conflicts). That could be a cross-doc consistency finding: if REBASELINE_PLAN defines the determinism Gate as byte-equality, the plan is the "唯一规划事实源" and would need sync (but it may be in 禁改面). Let me grep REBASELINE_PLAN.md and STATUS.md for 确定性/F5.

That's valuable for the integration closure list.
dsh: reasoning:
Important: the second grep result is huge. Key info: REBASELINE_PLAN line 115 mentions M2-TA3-B2 done with "F5 重定义" as 裁决移交. Does REBASELINE_PLAN list M2-QUAL-DETERM-CALIB as a task? The grep for "M2-QUAL-DETERM-CALIB" found matches only in the new files (script, handoff, task, thresholds, phase2-plan, calibration). So REBASELINE_PLAN does NOT mention M2-QUAL-DETERM-CALIB at all. And STATUS.md doesn't either (grep found no M2-QUAL-DETERM-CALIB in doc/STATUS.md). Let me verify explicitly: the grep pattern "M2-QUAL-DETERM-CALIB" over the whole worktree returned 44 matches; scanning the list: files are experiments/..., doc/handoffs/M2-QUAL..., doc/tasks/M2-QUAL..., verification/M2-TA3-B/quality-thresholds.md, phase2-plan.md, verification/M2-QUAL-DETERM-CALIB/*. No doc/REBASELINE_PLAN.md, no doc/STATUS.md, no doc/00_INDEX.md. 

That's significant: AGENTS.md says "当前 Milestone、Task 树、依赖和 Legacy Mapping 只以 REBASELINE_PLAN 为准；当前唯一 Active Task 与运行状态只以 STATUS 为准". A Task not registered in REBASELINE_PLAN/STATUS can't be "released"... but the Task file exists with approval: user_ruling_2026-10-01_all_four and the user directly asked for this review, and the task file itself says integrator = 编排会话代行 Codex（用户全权授权+自治授权）. So the release came from user ruling rather than plan registration. Still, the integration closure list should include: REBASELINE_PLAN has no entry for M2-QUAL-DETERM-CALIB (as a task row) and STATUS has no Active Task line for it — the integrator must decide whether to add a plan row (plan is 唯一规划事实源) or record the ruling. That's a legit finding for the closure list, not necessarily a defect of the owner (both files are outside the owner's allowed surface). Good: I'll list as P3/integration item. Note the handoff does say "STATUS 在本 Task 禁改面，须由集成方/Codex 更新" ✓ — acknowledged for STATUS but not for REBASELINE_PLAN. Let me double check REBASELINE_PLAN around the task list for TA3-B family — maybe there's a row for it under a different name. The grep for M2-QUAL-DETERM-CALIB found nothing there, so no row. I should verify by reading the plan's relevant section to see whether the F5 裁决 is registered as a task ID. Let me grep REBASELINE_PLAN for "CALIB" and "F5".

Also I noticed: doc/reviews glob returned "No files found" — but the grep clearly found doc/reviews/*.md files! So the glob pattern with "/" anchored... hmm, glob returned nothing for "doc/reviews/*.md" and for "verification/M2-TA3-B/**" but worked for "**/qual-*.json" and "**/*.md"? Actually the second pattern I used was "doc/reviews/*.md" → nothing. Strange. Maybe the glob tool's path resolution has issues with the space in the directory name ("New Manga.worktrees") — but "**/qual-*.json" worked with the same path. Odd. Possibly the glob implementation only supports "**" patterns rooted... Whatever; the grep tool works fine. I'll rely on grep/read.

Let me grep REBASELINE_PLAN.md for CALIB / F5 rows, and check STATUS for the current active task statement.

Also, I should check doc/reviews for the naming and whether the review file for this task exists already (it shouldn't).

Let me do targeted greps.
dsh: reasoning:
Confirmed: REBASELINE_PLAN has no task row for M2-QUAL-DETERM-CALIB; STATUS.md has no mention. That's an integration-side item (both are outside the owner's modifiable surface). I'll list it in the 闭合清单.

Now, a few remaining verifications:

1. Whether the committed calibration.md/calibration.json in the worktree are byte-identical to the diff (they should be). I read calibration.json partially via diff and calibration.md via diff. Let me spot check the actual files exist with the expected content — read calibration.md fully (96 lines) to confirm and to cite line numbers for findings. I need file:line references. Let me read the actual calibration.md with line numbers, and the script with line numbers (the diff gave me content but line numbers in the file = diff line numbers minus offset 114). Let me read the script file directly for accurate line numbers for citations.

Key citation line numbers needed:
- calibrate_determinism.py: normalize (~215), similarity (~240), translations_by_reading_order (~258), pair_status (~274), build_pairs (~387), alignment check (~394), nonempty per-case (~419), main aggregate nonempty (~709), synthetic probes, PROPOSED_GATE.

From the diff, file line = diff line - 114 for the script (since diff line 115 = file line 1). So:
- `normalize` def at diff 215 → file 101
- `levenshtein` diff 224 → file 110
- `similarity` diff 240 → file 126
- `translations_by_reading_order` diff 258 → file 144
- `pair_status` diff 274 → file 160
- `distribution` diff 301 → file 187
- `perturb` diff 319 → file 205
- `synthetic_probes` diff 330 → file 216
- `gate_verdict` diff 374 → file 260
- `build_pairs` diff 387 → file 273
- alignment fail-closed diff 394-398 → file 280-284
- nonempty per case diff 419 → file 305
- `main` diff 697 → file 583
- PROPOSED_GATE diff 195 → file 81
- aggregate nonempty diff 709 → file 595
- render_markdown diff 475 → file 361; §4.1 min reasoning at diff 599 → file 485; §4.2 median at diff 606 → file 492; §4.3 probes at diff 613 → file 499.
- threshold_evaluation reasoning diff 744 → file 630.
- calibration_source summaries_dir diff 761 → file 647.

Better to read the actual script file with line numbers to be safe. Let me read specific ranges: 70-130, 140-200, 260-320, 480-500, 580-600, 625-650.

Actually let me just read the whole script? 713 lines — that's fine but heavy. I'll read in two chunks with limits to get exact line numbers for the parts I cite.

Let me read script lines 70-130 and 270-320 and 480-500 and 580-600.

Actually, precision matters for findings. Let me read lines 95-135 (normalize/levenshtein/similarity), 140-170 (alignment/status), 270-315 (build_pairs), 480-500 (§4 reasoning), 590-600 (main nonempty), 626-640 (reasoning string).

I'll do 3 reads.
dsh: reasoning:
Now I have precise line numbers.

Additional finding: line 487: "取 0.75 − 0.05 = **0.70** 留一个字符级测量余量（provider 版本/提示词微调可能带来 ±1 编辑差）" — the "一个字符级测量余量" claim. As analyzed, 0.05 ≠ 1 character for the 4-char anchor (1 char = 0.25). So the rationale is quantitatively wrong and, worse, it implies the gate absorbs ±1 edit which it does NOT for short strings: 2 edits on a 4-char string = 0.5 → FAIL. This is a P2-ish finding because the "余量" claim is used to justify 0.70 in the authoritative thresholds §5 依据 cell too ("min 阈值锚在实测最坏浮动 0.75 下留 0.05 余量=0.70" — this one doesn't say "一个字符", so it's honest). So the number 0.70 is justifiable as "0.05 absolute margin", but the *interpretation* in calibration.md overstates its robustness. I'll flag P3 with the note that thresholds wording is fine but should be read together with calibration.md's stronger claim.

Hmm, but one could argue 0.70 leaves a margin that fails even benign floats on shorter strings (limitation 3). Combined: the min leg is brittle for short texts (both directions of the "margin" discussion). I'll present it as one finding: min leg 的余量与短串粒度不匹配（0.05 绝对值 ≠ 1 编辑差；4 字串再退一步即 0.5→FAIL），应在局限登记中把「0.05 余量」的语义写清，并考虑对 <6 字串给出例外或降档。

Also line 496-497: the median boundary "恒 FAIL" conditional on the [0.75,0.875] band. Note the synthetic probe itself shows 0.9375 max, so the band [0.75,0.875] is a measured-sample band, not a theoretical band. P3.

Another observation from line 485-486: "实测最坏浮动对 = 0.75（4 字译文单字替换，K11 ro=1/2/8 与 BJ02 ro=4）" — correct.

Now, one more important check on the emptiness rule: does the module docstring/§1 "4" describe both-empty as "两次 run 行为一致：都无译文"? Yes.

The gate uses all pairs including empty_both. Also `n_pairs_nonempty` excludes them for the non-empty subset reporting. So the Gate median includes 2/13 = 1.0 freebies in K11, 0 in BJ02. If a case has many empty regions (e.g., all SFX skipped), the gate's median is dominated by 1.0 → PASS. That's the coverage blind spot. I'll write it as a P2 finding: 空对规则与覆盖度耦合缺失 → 全空跑 PASS。

Mitigation suggestion: add to the Gate an explicit coverage precondition (e.g., "非空源 region 中译文非空比例 ≥ X" or "非空对数 ≥ 1", or at least register the blind spot and cite §7 row 8 translate scoring as the compensating gate).

Now let me double check the claim in thresholds/calibration that BJ02 Run1 render was bitwise identical: quality-report confirms BJ02 both export sha256 = 5c74a4f0... ✓ (from summary export sha256 "5c74a4f01e053ee2" both). I read qual-BJ02.json export sha256 = 5c74a4f01e053ee2c6427adf2fe6659687257660c98fc1997d9f56fb15e75528. The rerun should have the same. Let me verify quickly with grep on the rerun file for sha256. Also verify K11 rerun export sha differs (86ff9aa7...). Good extra evidence.

Let me grep for "sha256" in both rerun files.

Also, I might check doc/reviews listing via grep-based glob... not needed.

One more item: the handoff claims "6 files，+1338/−7". The diff I was given — does it show the stat? No, it's a plain diff, no stat. I can count added lines roughly: script 713 + calibration.json 512 + calibration.md 96 + handoff 76 = 1397 added for new files; minus? Hmm the claim +1338/−7 refers to commit e3b7c48d which excludes the handoff (76 lines) and includes task (+9/-1?) ... 713+512+96 = 1321 added for the three new files in e3b7c48d, plus task +9/−1, thresholds +3/−1... wait thresholds: -2 +3? Let's compute: hunk1 removes 1 row line and the note line (2 lines removed) and adds 2 rows + 1 note = hmm.

Let me compute the totals for commit e3b7c48d = script(713 add) + calibration.json(512) + calibration.md(96) + task(+9/-1) + phase2-plan(+3/-3) + thresholds(+4/-3?) ≈ 713+512+96+9+3+4 = 1337 added; removed: 1+3+3 = 7. That gives +1337/−7 vs the claimed +1338/−7 — off by one. Hmm. Let me count more carefully from the diff:

doc/tasks: @@ -2,7 +2,7 @@ hunk: line 92 changed (-1/+1) and lines 96-108 added (+9). So +10/-1? The hunk shows the status line replaced (1 removal, 1 addition) plus 9 added lines (blank + "## 交付记录" + 7 bullets + ...). Let me count the added lines in that hunk: 
```
+
+## 交付记录（2026-10-01，ZCode）
+
+- 本 Task 由 ZCode 续接...
+- AC1：...
+- AC2：...
+- AC3：...
+- AC4：...
+- 交接：...
```
That's 10 added lines (blank, heading, blank, 5 bullets... wait bullets: 本 Task, AC1, AC2, AC3, AC4, 交接 = 6 bullets). So added = 1(blank)+1(heading)+1(blank)+6(bullets) = 9? Let me recount from the diff text lines 100-108:
100: + (blank)
101: +## 交付记录（2026-10-01，ZCode）
102: + (blank)
103: +- 本 Task ...
104: +- AC1：...
105: +- AC2：...
106: +- AC3：...
107: +- AC4：...
108: +- 交接：...
That's 9 added lines. Plus the status line change +1/−1 → task total +10/−1.

thresholds: hunk 1: removed 1 (old 确定性复跑 row line 1487) → and the note line replaced (line 1492 removed, 1493 added). Wait hunk1 spans lines 1483-1494: context lines, then
- (old 确定性复跑 row)
+ (new remote row)
+ (new mock row)
context: 渲染产物 row
context blank
context > **本节 superseded...
- > **本节 superseded-pending 注...
+ > **本节 F5 修订注...
So hunk1: +2 (rows) +1 (note) = +3; −1 (row) −1 (note) = −2.
hunk2 (§7 row 10): +1/−1.
thresholds total: +4/−3.
phase2-plan: 3 hunks each +1/−1 = +3/−3.
So e3b7c48d total: script 713 + json 512 + md 96 + task 10 + plan 3 + thresholds 4 = 1338 added; removed 1+3+3 = 7. → +1338/−7 ✓ 

So the handoff's "6 files，+1338/−7" is exactly right for e3b7c48d (6 files: script, json, md, task, plan, thresholds) ✓. Verified.

And the review-input.diff (base..tip) = 7 files including the handoff (76 added) → +1414/−7. Good, consistent — so the diff provided is base..tip=2400b57a which includes the handoff commit. Good, that also means the handoff file exists at tip ✓.

Now let me quickly verify BJ02 rerun export sha and K01 rerun (already read K01 rerun: no export). Let me grep sha256 in BJ02.rerun and K11.rerun to confirm the "upper-bound reference" claim.

I also want to verify the review-input.diff is complete/consistent with the worktree tip. I can partially check: does the diff include everything? Not verifiable without git. NOT_VERIFIED.

Let me grep the rerun summaries for export sha256.
dsh: reasoning:
Confirmed:
- BJ02 rerun export sha256 = 5c74a4f0... identical to first run ✓ (upper-bound reference claim verified).
- K11 rerun export = 86ff9aa7... ≠ 2c5dee05... ✓ MISMATCH as recorded.
- K01 rerun region_count = 0 ✓ (both runs 0).
- BJ02 rerun region_count = 5 ✓.
- K11 rerun region_count = 13 ✓.

Line 305 vs 595-597: the per-case nonempty excludes only empty_both; the aggregate excludes empty_both AND empty_one_side. Confirmed inconsistent definitions. P3.

Now I have everything I need. Let me also double check the calibration.md actual file content line numbers for citation (§ numbers).

calibration.md (96 lines):
- §0? The report has "## 1. 方法" at line ~11 (diff line 1360 → md line 9?). Let me map: diff line 1352 = md line 1. So md line = diff line - 1351.
  - "## 1. 方法（Gate 定义）" at diff 1360 → md 9
  - §1 item 4 empty rule at diff 1365 → md 14
  - "## 2. 实测分布" diff 1368 → md 17
  - 关键读数 diff 1379 → md 28
  - "## 3. 逐对清单" diff 1381 → md 30
  - "## 4. Gate 阈值建议（AC2）" diff 1413 → md 62
  - min reasoning diff 1419 → md 68
  - median reasoning diff 1420 → md 69
  - probe text diff 1421 → md 70
  - table diff 1423-1427 → md 72-76
  - 判别力闭环 diff 1429 → md 78
  - "## 5. 语义边界" diff 1433 → md 82
  - "## 6. 局限登记（AC4）" diff 1439 → md 88
  - limitations 1-5 diff 1441-1445 → md 90-94
  - 声明 diff 1447 → md 96

thresholds file line numbers: 168, 169, 172, 205 ✓ (from the read with line numbers).

phase2-plan lines 17, 33, 182 ✓.

task file: line 5 (status), 27 (AC3 §1 mention), 41-46 (交付记录).

handoff lines: 13 (status frontmatter), 26 (+1338/−7), 37 (AC1), 47 (K11 7/13), 54 (关键数字), 60 (Reviewer 检查建议).

Let me verify the handoff line numbers by reading the actual handoff file (the diff gives content; line numbers = diff line - 6). For citation accuracy:
- diff 26 → handoff line 20 (续接说明)
- diff 37 → line 31 (AC1 row)... 
Hmm, handoff file starts at diff line 7 → handoff line 1. So handoff line = diff line - 6.
- "### AC 对照" diff 33 → line 27
- AC1 row diff 37 → line 31
- 验证证据 table diff 42 → line 36
- "AC1 K11 观察复现 | raw 口径 K11 浮动 7/13（非空 7/11）" diff 47 → line 41
- 关键数字 diff 54 → line 48
- 接收方式 diff 56 → line 50
- 复现 diff 59 → line 53
- Reviewer 检查建议 diff 60 → line 54
- 风险与遗留 diff 75 → line 69

Rather than guess, let me read the handoff file directly to get exact lines for the "7/13" claim. Quick read.

Actually, the diff line numbers are reliable: I'll cite the handoff with file lines computed as diff-6 but better verify. Let me read lines 30-50 of the handoff.

Let me also check doc/00_INDEX.md — does it index verification dirs? Given REBASELINE_PLAN doesn't have the task, 00_INDEX may need an entry. Out of scope but relevant for closure. I'll mention generically.

One read to confirm handoff line numbering, then write the review.
dsh: reasoning:
Confirmed line 41: "raw 口径 K11 浮动 7/13（非空 7/11）".

Now I have everything. Let me also consider: should I check the `.git` to confirm tip = 2400b57a and that the diff corresponds to base..tip? I can read the worktree's HEAD ref file. Let's try: `G:\CODEX\New Manga.worktrees\M2-QUAL-DETERM-CALIB-zcode\.git` is a file. Then read the gitdir/HEAD. This would let me verify tip = 2400b57a (strengthening verification of "diff = base..tip"). Worth one attempt.

Let me read the .git file.
dsh: reasoning:
Now read HEAD and the branch ref. HEAD in a worktree gitdir points to the branch ref, but the ref itself lives in the common dir (G:/CODEX/New Manga/.git/refs/heads/agent/zcode/M2-QUAL-DETERM-CALIB) or packed-refs. Let me read HEAD and the ref file.

Note: file policy is workspace-write with workspace = "G:\CODEX\New Manga"; reading G:/CODEX/New Manga/.git/... should be allowed (read).

Let me read both.
dsh: reasoning:
Tip = 2400b57ae65b... ✓ matches "tip=2400b57a". And HEAD is on the branch (not detached) ✓ ("勿切分支/勿 reset" — currently on branch, clean state claimed).

Can I verify the commit graph (base 8e0de8d0 → e3b7c48d → 2400b57a)? The commit objects are zlib-compressed; can't decode with read. I could check that 2400b57a's reflog worktree file... Actually the worktree gitdir has `logs/HEAD` with reflog entries showing commit transitions! Let me read G:/CODEX/New Manga/.git/worktrees/M2-QUAL-DETERM-CALIB-zcode/logs/HEAD. That would show the branch's commits (checkout/create/commit events) — potentially listing e3b7c48d and 2400b57a. Great idea for verifying "implement=e3b7c48d then handoff=2400b57a" and also whether the worktree is clean (no way) but at least the last commits.

Let me read it.
dsh: reasoning:
Excellent — reflog confirms:
- The worktree branch was created at 8996ca55 (not 8e0de8d0!). Hmm! The reflog line 1 shows the initial branch creation at 8996ca55feea... not 8e0de8d0. The Task frontmatter says base_commit: 8e0de8d0. The review input says base=8e0de8d0. The reflog's first entry is the worktree branch creation point (8996ca55), then reset to HEAD (8996ca55), then commit → e3b7c48d, then → 2400b57a.

So the branch was based on 8996ca55, not 8e0de8d0! Unless 8996ca55 is... hmm. But the review-input.diff is provided separately (base 8e0de8d0 → tip) and applied cleanly to the files I read? The diff showed thresholds index 117542e0..c325e30a and task index 86ba2ecc..459c6d6d. If the branch base were 8996ca55 and 8e0de8d0 were an ancestor, the diff base..tip could still be computed from the main repo. The reflog only records the branch creation at 8996ca55 — that's the commit the branch was created from (probably main's HEAD at creation time). If 8e0de8d0 != 8996ca55, that's a discrepancy worth flagging: the delivery's branch base is 8996ca55 while Task/frontmatter/handoff claim base_commit=8e0de8d0.

But careful: worktree reflog's first entry is "0000000 → 8996ca55" which is the worktree checkout creation (git worktree add creates the branch at some commit). So the branch started at 8996ca55. Then commit → e3b7c48d. So parent-of-e3b7c48d is presumably 8996ca55.

Is 8996ca55 possibly the same as "8e0de8d0"? No, different hashes.

Hmm, but maybe the predecessor (circuit-broken agent) created the worktree at 8e0de8d0, committed something... no — there's no commit between. Actually the reflog shows only two commits. Unless the predecessor's worktree was different.

Wait: maybe 8996ca55 is a commit *after* 8e0de8d0 on the main branch (i.e., the branch was created from a later main HEAD than the declared base). Or 8e0de8d0 is the declared "base" per the task freeze and 8996ca55 is what the worktree actually started from. Since I can't read commit objects, I can't verify ancestry.

Can I check other evidence? The base commit hash 8e0de8d0 appears in the Task frontmatter and handoff. Let me check the main repo's refs/heads/master (or main) — maybe master is at 8996ca55 now. Reading `G:/CODEX/New Manga/.git/refs/heads/master` (or check HEAD for the main worktree). If master = 8996ca55, then the branch was created from master at a point after the declared base 8e0de8d0 — meaning the diff base..tip would include any main-branch changes between 8e0de8d0 and 8996ca55... but the review-input.diff only contains the 7 task files, so no unrelated changes rode along (the diff was computed against 8e0de8d0 and shows only these files, which means nothing else changed between 8e0de8d0 and 8996ca55? no—if 8996ca55 = master head merged other commits, the diff 8e0de8d0..tip would show those other files too). Since the review-input.diff shows only 7 files, either 8e0de8d0 == 8996ca55 in content, or the diff was computed base..tip where base is an ancestor with no other differences. 

Hmm, actually maybe 8e0de8d0 isn't an ancestor at all and the diff is misleading. But the diff includes files whose "index 117542e0..c325e30a" blob hashes correspond to the pre-change state; the pre-image of quality-thresholds.md in the diff includes §5 with superseded-pending, which exists in the worktree's base. Fine.

Let me check the main repo HEAD/master to see the relationship. Read G:/CODEX/New Manga/.git/HEAD and refs/heads/master (or main).

This matters: if the deliverable's true base differs from the declared base, the review's diff-based scope verification may be against the wrong base (e.g., unrelated commits from another task could be included if the base were earlier). The diff shows only 7 files, which is reassuring, but I should report the discrepancy: "worktree 分支创建点=8996ca55（reflog），与声明的 base_commit=8e0de8d0 不一致；需集成方确认 8e0de8d0 与 8996ca55 的关系（是否 8996ca55 为 8e0de8d0 的后继/同内容）". This is a P3 finding (evidence/traceability).

Let me check master.
dsh: reasoning:
glob on the .git dir returns nothing (maybe glob ignores dot dirs? It said it includes hidden/ignored files... but maybe the path arg handling). Let me use read on G:/CODEX/New Manga/.git/refs/heads/main.

Actually the main worktree's HEAD → refs/heads/main. Let me read that ref.

Also I could read the main repo's logs/HEAD to see the recent commits on main (its reflog will show checkout/reset events and maybe merges), which might reveal whether 8e0de8d0 and 8996ca55 are both on main. That's a lot of digging; but one read of the main reflog tail could clarify. The main logs/HEAD could be long; I'll read it with an offset near the end... I don't know the length. Let me first read the main ref.
dsh: reasoning:
main = 8996ca55. So the worktree was created from main HEAD = 8996ca55. The declared base_commit = 8e0de8d0.

Now, is 8e0de8d0 an ancestor of 8996ca55? Presumably: base 8e0de8d0 was probably the commit where the task was frozen/released, and main advanced to 8996ca55 (e.g., by the integration of another task, or the CALIB release commit) before the worktree was created. Since the review-input.diff 8e0de8d0..2400b57a contains only the 7 task files, either:
(a) 8e0de8d0 → 8996ca55 contains no changes to tracked files other than what's in the diff (unlikely if main advanced), or
(b) the diff was computed by the task-env tooling in a way that filters to the task's files, or
(c) 8e0de8d0 is a descendant... no.

Actually maybe 8e0de8d0 IS an ancestor and the intermediate commits touched files that are also new/untracked or the same content. Hmm. Alternatively 8e0de8d0 could be an ancestor that is 8996ca55's parent chain with only doc changes... but any change would appear in the diff.

Wait — maybe the diff provided is base..implement (e3b7c48d) and not base..tip? No, it includes the handoff file which was added in 2400b57a.

Hmm, but there's another possibility: the review-input.diff was generated with a path filter (only the task's allowed/expected paths) — that would explain the absence of other main-branch changes. Or main was at 8e0de8d0 when the task was released and 8996ca55 = the commit that *released* the task (adding doc/tasks/M2-QUAL-DETERM-CALIB.md, which is a pre-existing file in the diff's pre-image: "index 86ba2ecc..459c6d6d" — so the task file existed at the base 8e0de8d0 too).

Hmm, if 8996ca55 added the task file, the pre-image at 8e0de8d0 wouldn't have it. So no.

I can check the main reflog to see the recent history of main and whether 8e0de8d0 appears. Let me read G:/CODEX/New Manga/.git/logs/HEAD (the main worktree's reflog). It may be large; let me read the last ~40 lines. I'll read with offset. First, how long? Try reading with a large offset... simpler: read the whole file with limit 2000 and see. It might be a few hundred lines. Let's grep it for 8e0de8d0 and 8996ca55 instead (grep tool on that file path).

That's the cleanest: grep for "8e0de8d0" in G:/CODEX/New Manga/.git/logs/HEAD.
dsh: reasoning:
This fully resolves the base question:
- main line 726: commit 8e0de8d0 = "close(M2-TA3-B2)" — the base.
- main line 727: 8e0de8d0 → 8996ca55 = "release(4-task batch)" — the batch release commit that added the task files (including doc/tasks/M2-QUAL-DETERM-CALIB.md) and updated REBASELINE_PLAN/STATUS.

So the worktree was created from 8996ca55 (the release commit), while the declared base_commit=8e0de8d0 (the pre-release close commit). The review-input.diff base..tip = 8e0de8d0..2400b57a includes the release-commit changes too? The release commit 8996ca55 certainly modified REBASELINE_PLAN.md and STATUS.md (adding the 4-task batch rows) — those would appear in the diff 8e0de8d0..2400b57a. But the provided review-input.diff contains only 7 files (no REBASELINE_PLAN, no STATUS). Therefore review-input.diff is NOT a plain `git diff 8e0de8d0..2400b57a` — it must have been filtered to the task's paths, or computed against 8996ca55 despite being labeled base=8e0de8d0.

Hmm. Let me double-check: maybe the release commit only added doc/tasks/*.md (4 new files) and did not touch REBASELINE_PLAN/STATUS (the commit message says "PLAN mermaid TA3B2 -> done + inventory row" was in the previous commit 8e0de8d0 for TA3-B2 close; the release commit message doesn't mention PLAN/STATUS updates). Actually the release commit message lists 4 task releases; it likely added 4 task files and possibly PLAN rows. Its message doesn't explicitly say STATUS updated. Hmm.

If the release commit only added new task files, then diff 8e0de8d0..2400b57a would include: doc/tasks/M2-DETECT-WEBTOON-DIAG.md, doc/tasks/M2-IMPORT-ALLOC-LIMIT.md, doc/tasks/M2-SFX-TRANSLATE-ENTRY.md (new), plus doc/tasks/M2-QUAL-DETERM-CALIB.md (new at release, but the diff shows it as *modified* with index 86ba2ecc..459c6d6d — meaning the pre-image exists in the diff's base. If M2-QUAL-DETERM-CALIB.md was created by the release commit 8996ca55, then diffing 8e0de8d0..tip would show it as a NEW file, not a modification with an index pair. The diff shows "diff --git a/doc/tasks/M2-QUAL-DETERM-CALIB.md b/doc/tasks/M2-QUAL-DETERM-CALIB.md / index 86ba2ecc..459c6d6d 100644 / --- a/... +++ b/..." with a hunk at @@ -2,7 +2,7 @@ — a modification, not a new file.

Therefore the diff's base DOES contain doc/tasks/M2-QUAL-DETERM-CALIB.md. So the diff base is a commit where the task file already existed with 32 lines. If 8996ca55 (release) created it, then the diff base can't be 8e0de8d0... unless the task file pre-existed at 8e0de8d0 and the release commit modified it (status ready / frontmatter). That's plausible! The 4-task release commit might have edited pre-existing task files (staged earlier as drafts) — the task file at 8e0de8d0 had 35 lines (per the diff: hunk at line 35 with "## 纪律" and the file grew to 46 lines). Wait, the diff says @@ -35,3 +35,12 @@ meaning the pre-image had at least 37 lines? No: hunk header "-35,3" = 3 lines starting at line 35 in the old file; and the file's old version must have had ≥37 lines... Actually 35+3-1 = 37 lines old. Hmm, but the hunk context is:
```
 ## 纪律
 
 - 阈值建议必须附实测分布...
+
+## 交付记录...
```
So the old file had at least those 3 lines and ended there → old file length could be exactly 37 lines. New = 37 + 9 = 46 ✓ matches the current file's 46 lines. So the pre-image task file had 37 lines. Fine.

So the diff base contains a 37-line M2-QUAL-DETERM-CALIB.md. Which commit introduced it? Possibly the same release commit (8996ca55) or an earlier commit. If 8996ca55 created it, the diff base would have to be 8996ca55 (then it wouldn't appear as a modification at all) — contradiction. So the task file existed before the diff base, i.e., before 8e0de8d0? Then the diff base might genuinely be 8e0de8d0 and the task file pre-existed (maybe the task file was created earlier as a draft/ready task in the backlog).

Hmm, but the reflog on main says the release commit is "8e0de8d0 → 8996ca55" and its message says "M2-QUAL-DETERM-CALIB (F5: ...)". If the task file already existed at 8e0de8d0 with status ready, the release commit may have just bumped its frontmatter/approval. Plausible: M2-QUAL-DETERM-CALIB.md exists in the base with `status: ready`, `approval: user_ruling_2026-10-01_all_four`... but wait, the diff only changed `status: ready → delivered`, not the approval field. The approval field already said `user_ruling_2026-10-01_all_four` at base. So the task file (37 lines) existed at 8e0de8d0 with approval already set. Hmm, that's odd for a release commit to then "release" it. But maybe the release commit added the *other three* task files (DIAG/ALLOC/SFX) and this one already existed.

Either way — is there a scope risk? If the diff base (8e0de8d0) is not the branch's actual fork point (8996ca55), then the diff 8e0de8d0..tip could omit or mislabel changes. But importantly: the diff shows only 7 files, all within the allowed surface. If the release commit 8996ca55 modified REBASELINE_PLAN/STATUS (outside the owner's allowed surface), that commit is NOT authored by this owner — it's the orchestrator's release commit — so it shouldn't be attributed to this delivery anyway.

So the practical conclusion: the branch base is 8996ca55 (release commit), the declared base_commit in the Task is 8e0de8d0, and the provided review-input.diff is computed from 8e0de8d0 which *includes* the release commit's changes — yet it shows only the 7 task files, which implies the release commit's diff for this task's path set is exactly those files, i.e., possibly the release commit also modified doc/tasks/M2-QUAL-DETERM-CALIB.md (e.g., status ready + approval), and the owner's commit further modified it. That would mean the Task file's pre-image in the diff (status: ready) is post-release.

Hmm, wait. Actually here's a cleaner hypothesis: the diff base 8e0de8d0 might be wrong in my assumption that the diff is 8e0de8d0..2400b57a. The task statement says "base=8e0de8d0、implement=e3b7c48d、tip=2400b57a（handoff）" and "diff：...review-input.diff". Maybe the diff was generated by the task-env tooling as `git diff 8e0de8d0...2400b57a` with `--` path filters. Or perhaps the tooling computed merge-base(8e0de8d0, branch) which is 8996ca55... then diff 8996ca55..2400b57a → only the task files (task md modified, since at 8996ca55 the task was `ready`). That fits PERFECTLY: at 8996ca55 (release), the task file was created/modified to status ready + approval; the diff 8996ca55..tip shows the task file modified ready→delivered, plus the 6 other files. And the "base=8e0de8d0" label is just the pre-release commit recorded in the Task frontmatter.

Either way, I can verify the content of the task file at the release commit? I can't read blobs. But I have a decisive check: if the diff were 8e0de8d0..tip and the release commit touched REBASELINE_PLAN.md/STATUS.md, those would appear. They don't. Two possibilities: (a) diff is from 8996ca55 (merge-base), or (b) the release commit didn't touch those files. Given the release commit message ("release(4-task batch)") and AGENTS discipline ("当前唯一 Active Task...只以 STATUS 为准"), it almost certainly updated STATUS/PLAN — so (a) is most likely: the tooling diffed from the branch fork point (or filtered paths).

Conclusion for the review: the branch fork point per reflog is 8996ca55 (release commit), not the declared base_commit 8e0de8d0; this is a traceability nit (frontmatter base_commit semantics = "task freeze base" vs actual branch base). Retrospectively, the Task frontmatter's `base_commit: 8e0de8d0` refers to the task-freeze base; the branch was cut from the release commit 8996ca55. Worth a P4 note with a recommendation to record the actual fork point for future audits (or use `git diff <fork>..tip`). Also NOT_VERIFIED: the exact diff invocation used for review-input.diff.

Hmm, but actually there's a subtlety: the release commit 8996ca55 came AFTER 8e0de8d0, and the diff provided (7 files) matches either "8e0de8d0..tip filtered" or "8996ca55..tip". Both are consistent with the 7 files if the release commit only added the other 3 task files and modified this one. Wait, if the release commit added the other three task files, then diff 8e0de8d0..tip would include those 3 new task files! It doesn't. Therefore the diff is NOT 8e0de8d0..tip; it must be 8996ca55..tip (or path-filtered). Unless the release commit didn't add new files but only modified existing ones (the 4 tasks might have all pre-existed as ready/paused docs). Given the commit message says "release(4-task batch)", and their task files might have been authored earlier (e.g., 3 task files created when TA3-B2 closed, with status: proposed/paused), the release commit could have just bumped statuses to ready. In that case diff 8e0de8d0..tip would show 4 modified task files, but the provided diff shows only 1 task file modified. So still contradiction → the diff base is 8996ca55 (the fork point), or the diff was path-filtered to this task's files.

Either way, the correct claim is: the provided diff is consistent with `<fork=8996ca55>..2400b57a` (7 files), and NOT with a plain `8e0de8d0..tip` unless the release commit modified exactly doc/tasks/M2-QUAL-DETERM-CALIB.md among the four (impossible, since the other three tasks were also released... they'd have status changes too, appearing in the diff).

Hmm, careful — maybe the other three task files were created in the release commit as NEW files; then diff 8e0de8d0..tip would list them as new. Not present. And if they were created before 8e0de8d0 with status ready... then the release commit wouldn't need to modify them. Ah, that's possible! If the 4 task docs were all authored earlier (e.g., in the TA3-B2 close commit 8e0de8d0, "PLAN mermaid TA3B2 -> done + inventory row" — maybe the close commit also added the 4 task files as drafts with `approval:` placeholders), then the release commit 8996ca55 may have modified only their frontmatter statuses... but then the diff would show 4 modified task files. Only 1 appears.

Unless the release commit modified all four but the review-input.diff was path-filtered to this task. That's the most likely explanation given task-env tooling ("review-input.diff" for a single task is probably scoped to that task's paths).

So: I cannot determine whether the release-commit-era changes to other files ride along; but the diff I reviewed shows only this task's files, and all changes in it are within the allowed surface. I'll note in NOT_VERIFIED that the diff generation method (path filter vs fork-point diff) is not documented in the handoff, so "diff 中不得出现 qual-*.json" is verified only for the provided diff, and the integrator should run `git diff --stat 8996ca55..2400b57a` (fork→tip) to confirm the delivery contains exactly 6+1 files.

Hmm, actually — I realize the more valuable framing: the declared base_commit (8e0de8d0) ≠ actual branch fork (8996ca55). Since 8996ca55 is main's current HEAD, and 8e0de8d0 is its parent, the practical impact is nil (only the release commit is between them, which touches task docs). But it's a traceability finding: "base_commit 应改为实际 fork 点（或标注为 task-freeze base）"。P4.

Now let me also double check that main is still at 8996ca55 (yes) — meaning nothing from this branch is integrated yet ✓ (integration pending).

Also: the worktree HEAD is on the branch ✓ (not detached), and the reflog shows only 2 commits; nothing after 2400b57a. So the worktree's last activity = the handoff commit. No evidence of post-delivery edits in the reflog (reflog doesn't track working-tree edits though). So "porcelain 干净" remains NOT_VERIFIED (needs `git status`).

I think I have enough. One more consideration: the review asks specifically "reading_order 对齐的有效性（两次 run region 数不同怎么办——对齐失败 fail-closed 的实现）". My finding: the implementation compares translate_details-derived reading_order key sets, not region sets; region-count差异 manifests as a key-set差异 and triggers SystemExit ✓ (fail-closed implemented correctly for that case). But: (a) it does not detect a permutation (same key set, different mapping) — no geometric cross-check despite bbox being available and empirically identical; (b) it does not detect regions missing from translate_details in BOTH runs (silent pair loss); (c) zero-pairs-both-sides → NO_DATA, undefined in thresholds (K01 is the live example).

Good. And the answer to "空对口径的合理性": rule is reasonable but has the all-empty blind spot and the status/similarity semantic split.

"Levenshtein 归一（1−dist/max_len）实现正确性": verified — the implementation is a standard two-row DP; `min(prev[j]+1, curr[j-1]+1, prev[j-1]+(ca!=cb))` correct; early returns correct; and it's byte-identical to measure_cer.py's `levenshtein` (lines 60-75) and `normalize` (lines 51-57) — I compared them: identical character-for-character (measure_cer.py uses multi-line formatting for the min() call; semantics identical). ✓ Note measure_cer.py's normalize does NOT include "ー not folded to -" logic — consistent with both (§0 says ー is not folded; neither does folding). ✓ So the claim "复刻自 measure_cer.py" is accurate (modulo formatting).

Also §0 says "统一省略号与长音符（…≡...、ー 不与 - 互转）" — the implementation handles "…" and "\u22ef" (midline horizontal ellipsis) but not the CJK ellipsis "⋯" (U+22EF is ⋯ actually! U+22EF = MIDLINE HORIZONTAL ELLIPSIS "⋯"). The comment in the code writes "\u22ef" — correct escape. But what about "‥" (U+2025) or "。。。"/"．．．" (fullwidth dots, seen in BJ02 source "しろ．．．")? Normalization does NOT fold fullwidth "．" into "."; §0 doesn't require it either. But note the BJ02 source has "．．．" and its translation "……" — normalization converts the translation's "…" → "..." but leaves fullwidth "．" alone. Since both runs had identical text there, no impact. It's a §0-faithful implementation; a pedantic observation: the "…≡..." unification is one-directional (both `…` and `⋯` → `...`), which matches §0's "…≡..." plus the project's actual script. No finding. Actually §0 says "…≡..." which the script interprets as both directions; fine.

Hmm — one more: the `normalize` function strips ALL whitespace including spaces between Latin words: "所谓 强大" → "所谓强大". Registered as limitation 5 only for line breaks/spaces. Fine.

Now: threshold论证 "0.70 会不会太松/太紧":
- Too tight for short strings (documented limitation 3, 3-char; but also 4-char with only 0.05 margin).
- Too loose for long strings (a single 30%-replaced region passes the min leg; e.g., a 20-char region with 6 chars changed = 0.70 exactly → PASS with `>=`). This is not registered as a limitation. It's the flip side of "min leg 抓结构性漂移": the probe drift_40 min=0.5 shows 40% caught, but 30% on a long region is invisible. P3: 建议在 §6 增补「min 腿的判别力随译文长度下降」的登记。

Now "合成对照（40% 替换→0.5）能否代表真实漂移模式" — my assessment: the probes are character-substitution noise on the *observed* translations, i.e., they model "uniform random char corruption", whereas real provider drift is typically: re-phrasing (different words, similar meaning → similarity can be low but semantically fine), truncation, or language switching. The probes therefore over-approximate lexical drift but under-represent structured drift (e.g., entire region re-translated with different wording = similarity ~0.1-0.3 → would FAIL loudly, fine) and don't model "one region translated into a different language/longer text" (insertion-only → similarity drops). Overall: the chain substitution is a reasonable stress proxy for the *metric*, but NOT a representative model of provider drift modes; the report does say "漂移代理（非 FAIL 实证）" — mostly honest. But one specific gap: because drift probes are derived from each pair's own previously-identical text, the probe measures pure metric response, not a plausible drift distribution. I'll register as P3 with recommendation to add a "paraphrase/同义改写" probe (the most likely real drift: same meaning, different words) — note that a paraphrase would produce LOW similarity → FAIL, which is a *design* issue for a "translation stability" gate (semantic equivalence ≠ lexical identity). This is actually an interesting substantive point: the Gate as defined (character-level similarity) penalizes legitimate non-determinism in *wording* while claiming to measure "translation stability". For remote LLM translation, two runs may produce semantically equivalent but lexically different translations, e.g., "别说得那么冠冕堂皇" vs "别说得那么漂亮" (similarity 0.75 → passes) or fully different phrasing (similarity ~0.2 → FAIL). So the Gate conflates lexical identity with semantic stability. Since the adopted口径 is exactly that (user-ruled: "reading_order 对齐译文相似度"), this is inherent to the ruling, not an owner error; but the limitation registration should say the metric is lexical, not semantic — the current limitations mention 归一化口径依赖 but not "词面 vs 语义" (paraphrase false-FAIL). §1.5 says "同输入同模型重跑下译文的词汇级一致性" — actually it DOES say 词汇级一致性! Good, the report discloses "词汇级". But it's not in the five limitations (nor is the false-FAIL risk of legitimate paraphrase). I'll fold into a P3 finding: add a limitation "语义等价但词面不同的合法重译会被判 FAIL（词面口径的固有误报方向）".

That's a strong, honest review point. Note the observed data has one such near-case: ro=11 "泰阳！！" → "泰阳阳！！" = 1 edit (0.875) passing; but "胡萝卜？"→"小萝卜？" is a *synonym* substitution (同义词), also 1 edit. So real paraphrase at scale would FAIL — the gate would produce false FAILs for legitimate semantic equivalence. Registered? limitation list mentions 极短译文粒度 but not this. I'd rate P2 because it's a fundamental validity issue of the Gate being adopted as the authoritative口径: it treats benign lexical variation as instability, but the threshold was calibrated only on the 1-edit regime; any 2+ edit benign paraphrase on a short region FAILs. Given the calib data (K11 ro=1/2/8: 胡萝卜↔小萝卜 — already a synonym swap at 1 edit), the next benign variation (e.g., 胡萝卜→红萝卜, still 1 edit) is fine, but 胡萝卜→萝卜 (2 edits on 4 chars = 0.5) FAILs. So the min gate 0.70 on 4-char strings effectively means "at most 1 character may differ" — for 4-char CJK translations, any 2-char lexical change (very plausible benign variation) → FAIL. This is the crux: **min ≥0.70 is effectively a near-exact-match requirement on short regions**, which is a false-FAIL machine for remote sampling. The doc's limitation 3 only covers ≤3-char strings; but 4-char strings have the same cliff (2 edits = 0.5). Recommend: (a) register the length-dependent min-leg cliff explicitly with the 4-char counterexample (2 edits → 0.5, FAIL) rather than only ≤3字; (b) or use an edit-distance-based rule (e.g., "≤1 edit on short strings") / per-length threshold; (c) at minimum, note that the min leg's practical semantics on 4-char regions = exact match modulo one character.

That's my P1/P2-level methodological finding. Is it P1? It doesn't invalidate the numeric calibration (which is honest), and the Gate passes the observed data. But it does mean the adopted thresholds encode an approximate requirement that the calibration data cannot support (n=2, only 1-edit floats observed). The doc partially registers it (limitation 3) with the correct fail-closed direction. So P2 is fair: "局限登记的粒度边界写得比实测更窄（只写 3 字），且未量化 4 字串的 min 腿悬崖；建议扩写并给出改判方案". I'll make it R2 (P2).

Let me now also reconsider the all-empty (. P2) and permutation alignment (P2) and zero-pair K01 (P2). Three P2s plus one more P2 (min-leg 4-char cliff). That's 4 P2. Plus P3s: median band conditionality, nonempty definition inconsistency, probe representativeness (段落改写/词面口径), 0.05≠1char margin wording, zero-pair NO_DATA undefined, thresholds no operational discriminator for remote vs mock track, handoff 7/13 wording, task AC3 §1 mismatch, calibration.json absolute path, quality-report residual superseded-pending references, branch fork vs declared base. P4: cosmetic.

Grouping to avoid an unwieldy list, I'll present ~12 findings: R1-R4 (P2), R5-R11 (P3), R12-R14 (P4).

Let me assign the verdict. The numbers are verified correct, scope discipline holds, docs are honest. But the Gate is now the authoritative口径 and has identifiable definitional gaps (alignment permutation, all-empty pass, zero-pair handling, min-leg cliff). Given the review's purpose (round 1), verdict = **changes_requested（有条件）**: require the owner/integrator to fix the 2 blocking-ish items (R1 alignment permutation guard or explicit limitation; R2 min-leg cliff limitation expansion) — hmm, "changes_requested" vs "approved_with_conditions". The findings are mostly "add limitation registration / clarify wording", which falls under AC4's obligation ("局限登记"). Since AC4 is an explicit AC and the limitations are incomplete in ways that matter for the Gate's authority, I'd say `changes_requested` with a small返修面 (all documentation-level, no code changes required except optionally a bbox guard). Alternatively `approved_with_conditions` if I judge the gaps as acceptable-with-registration by the integrator.

The prior review culture in this repo: r1 often `changes_requested` with one P1; r2 `approved`. Here nothing rises to P1 (no false claim of fact; all numbers verified). I'll go with **`changes_requested`（P2 级，返修面=文档/局限登记 + 建议脚本加 1 处 fail-closed 断言）** — hmm. Is that too harsh given everything checks out? The user asked for a rigorous static review with 重点审查项 including these very questions. The most defensible position: the交付 numbers are correct and the口径 revision is faithfully landed; the Gate definition has 3 unregistered failure modes that AC4 ("局限登记") arguably should cover. Round 1 requesting these be closed is proportionate. I'll declare: Verdict = **changes_requested（无 P0/P1；4×P2 全部为 Gate 定义/局限登记缺口，返修面小：文档扩写 + 1 处可选 fail-closed 断言）**, and explicitly state 数值/范围/纪律 全部通过, so integration can proceed immediately after the P2s are closed (or relocated to a follow-up with user's awareness).

Actually, let me reconsider R1 (alignment permutation). Is a bbox guard really needed? The Gate's alignment key is per-run reading_order derived from the run's own regions; if the detector returns the same set of regions in a different order, pairs misalign → similarity collapses → FAIL (fail-closed direction!) — a false FAIL, not a false PASS. So the risk direction is fail-closed (spurious FAIL), which is the safe direction, though it wastes a Gate FAIL. Hmm, but could a permutation produce a false PASS? Misalignment of *empty* regions or near-identical translations (e.g., K11 has four nearly identical 胡萝卜 texts!) — indeed K11 ro=1/2/3/4/6/8 are all near-identical ("胡萝卜？", "小萝卜！", …). If a permutation occurred among those, similarity could remain high (they're 1-2 edits apart) → a misaligned pair scored ~0.75 could look like a benign float → FAIL/float ambiguity, but NOT a false PASS overall since median would still be dominated by real identical pairs... Actually misalignment among near-identical regions yields similarity ~0.75 for those pairs and could inflate the float count (fail direction). So the main risk is over-flagging (fail-closed) plus ambiguous root cause. Still worth a guard, and grading P2 seems slightly high; P2 is defensible because a silently-wrong alignment makes the Gate's result uninterpretable (can't distinguish "detect order changed" from "translation drifted"), and the fix is cheap (bbox identity check; bbox is present in both summaries). I'll keep P2 but state the risk direction honestly (false-FAIL/不可解释, not false-PASS).

Hmm — wait. There IS a false-PASS scenario: if the misalignment swaps a floating pair with an identical pair. E.g., run A: ro=1 "胡萝卜？", ro=3 "胡萝卜？" (identical in run B). If reading_order permutes, pairs (1,3) and (3,1) may accidentally align texts that are equal → similarity 1.0. In K11, ro=1 and ro=3 have the same first-run text "胡萝卜？" — if ro=1's second-run text "小萝卜？" paired with ro=3's second-run "胡萝卜？" — that's what happens now (real). A permutation could make a drifting pair look identical. So yes, false PASS is possible for near-duplicate regions. Good, P2 justified.

Now R2 (all-empty PASS): false-PASS scenario, P2 ✓.

R3 (K01 zero-pair): the authoritative thresholds name a 3-case set where one case yields zero pairs; without a rule, the future Gate run's behavior is undefined (script → NO_DATA, an undefined verdict in the thresholds vocabulary which only has PASS/FAIL). P2 (integration-blocking for the future runner, though not for this delivery). Maybe P3 since it doesn't affect this delivery's validity... but thresholds is exactly what's being delivered, and it will be executed by a future runner against a 3-case set that includes a 0-pair case. I'll call it P2 with the note that it may be closed by one sentence in the thresholds.

R4 (min-leg 4-char cliff / margin semantics): P2 documentation+definition.

Then P3s.

Hmm, I should be careful not to overload with P2s; but each is defensible. Let me finalize:
- R1 P2: 对齐仅校验 reading_order 键集合，无法检出同键集不同序/同 bbox 置换；无几何交叉校验 → 可能产生误 FAIL 或对近似重复 region 的误 PASS；建议加 bbox 逐 ro 一致断言（fail-closed）或至少登记该假设。
- R2 P2: 「双方空=1.0」+ Gate 取全部对 → 全空/大面积空跑可 PASS（覆盖度盲点）；建议加覆盖前置条件或在局限登记中写明并由 §7 第 8 行 translate 评分 Gate 兜底。
- R3 P2: thresholds §5 固定 3 case 含 K01（两 run 均 region_count=0）→ 0 对场景的 Gate 判定（NO_DATA/豁免）未定义；建议补一句 R11 一致的豁免/NO_DATA 口径。
- R4 P2: min leg 的 0.05 余量口径与实际粒度不匹配（4 字串 2 编辑=0.5 即 FAIL；"留一个字符级测量余量"表述不成立）→ 局限登记只覆盖 ≤3 字，未量化 4 字悬崖；建议改写余量语义并扩写局限/考虑按长度分档。
- R5 P3: median 边界「浮动 ≥9 对恒 FAIL」以 [0.75,0.875] 为条件；合成探针自身出现 0.9375，长译文的低幅系统性浮动可 PASS median leg（"全部对 1 编辑浮动 → median leg FAIL" 非普适）。
- R6 P3: 非空对定义在 build_pairs(:305) 与 main(:595-597) 不一致（empty_one_side 一处保留一处排除）；且 pair_status 用 strip、similarity 用原串，仅空白差异时 status 与 similarity 语义冲突。
- R7 P3: 数据完整性未断言 translate_details 覆盖 regions[]（两 run 同时缺同一 region 时静默丢对，n_pairs 变小、median 更易 PASS）；未知 region_id 会 KeyError 崩溃（非注册的 SystemExit）。
- R8 P3: 判别力对照均为「字符随机替换」代理，未覆盖最可能的真实漂移形态（同义改写/整段重译）；词面口径对语义等价的合法重译会产生误 FAIL，未登记该固有误报方向。
- R9 P3: 「remote/随机采样链 vs mock/deterministic 链」双轨缺运行期判别规则（runner 如何选轨未定义）。
- R10 P3: quality-report.md:189/199 仍留 superseded-pending 表述（历史裁决点），handoff 的 grep 声明只覆盖 thresholds，易被读作"全仓无残留"；建议集成方加一句关系注或明确不改的理由。
- R11 P3: Task AC3 写「§5/§7/§1」，实际 R9 原注只在 §5/§5 尾注/§7；§1 项核对为空未登记（AC 闭合不完整）。
- R12 P4: handoff:41 用「7/13（非空 7/11）」，与 quality-report 明确修正的「7/13=混用分母」措辞回潮。
- R13 P4: calibration.json:5 写入 worktree 绝对路径（环境相关、跨 checkout 复跑会 churn）；建议改为相对路径。
- R14 P4: Task frontmatter base_commit=8e0de8d0 与分支实际 fork 点 8996ca55 不一致（reflog 证据）；建议注明 fork 点或改用实际 fork。

Also the "自检项" NOT_VERIFIED: porcelain 干净、diff --check EXIT=0、脚本重跑逐字节一致、git show --stat e3b7c48d、半成品草稿的 4 处修正（草稿不在版本库）.

Also add as NOT_VERIFIED: review-input.diff 的生成口径（未文档化）。

Also: I verified that the *content* of calibration.json/md matches the diff; but I did not run the script → the artifact-vs-code consistency is verified by hand-recomputation of the distributions/medians (which I did partially: K11 raw/normalized, aggregate medians). I should state that I independently recomputed the key distributions from the summary JSONs and they match — that's strong evidence (I verified: 13/5 pairs, texts match, raw 7/11, normalized 5/13 with the ro=5/10 absorption, all four medians, aggregate 18/16, variant-only medians).

Let me double check aggregate raw_variant_only median 0.8035 — computed ✓. And aggregate normalized_nonempty median 1.0 ✓ (10 identical of 16 → median = (8th+9th)/2 where sorted: 6 variants (0.75×4, 0.8571, 0.875) + 10 ones → positions 1-6 floats, 7-16 ones → median = (1+1)/2 = 1.0 ✓).

One more check on the BJ02 p10 = 0.85 ✓ computed.

Also the "P10" of aggregate normalized_nonempty = 0.75 ✓ (position: k=(16-1)*0.1=1.5 → f=1,c=2 → v1 + (v2-v1)*0.5 = 0.75 ✓).

Good — all numbers independently reproduced.

Now the 逐项核对表 with A/B/C/D/E sections, and the required output format. Also 集成方闭合清单 and 推荐下一步 (one sentence).

For findings I must give 文件:行. Let me assemble accurate references:
- experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py:144-157 (translations_by_reading_order), :280-284 (fail-closed), :305 vs :595-597 (nonempty), :126-136 (similarity), :160-165 (pair_status), :132-135 (empty rule), :101-107 (normalize), :110-123 (levenshtein), :59-67? (docstring), :484-498 (reasoning §4.1/4.2), :500-506 (probes), :216-247 (synthetic_probes) — let me get exact lines for synthetic_probes: from the diff, def synthetic_probes at diff 330 → file 216. perturb at diff 319 → file 205. probe list at diff 349-353 → file 235-239. OK.
- PROPOSED_GATE at diff 195 → file 81.
- calibration.md:90-94 (limitations 1-5), :68-69 (min/median reasoning), :14 (empty rule), :78 (判别力闭环), :62 (§4 建议 Gate).
Let me map calibration.md lines precisely: md line = diff line − 1351.
  - §4 heading diff 1413 → md 62
  - min reasoning diff 1419 → md 68
  - median reasoning diff 1420 → md 69
  - probe text diff 1421 → md 70
  - table rows diff 1425-1427 → md 74-76
  - 闭环 diff 1429 → md 78
  - §6 heading diff 1439 → md 88
  - limitations diff 1441-1445 → md 90-94
  - §1 item4 empty rule diff 1365 → md 14
  - §3 note diff 1411 → md 60
  - 关键读数 diff 1379 → md 28
Let me verify md 68-69 by reading the actual file lines 62-80 and 88-96 to be safe about line numbers.

- quality-thresholds.md:168 (remote row), :172 (note), :205 (§7 row 10).
- phase2-plan.md:17, :33, :182.
- doc/tasks/M2-QUAL-DETERM-CALIB.md:5, :27, :39-46.
- doc/handoffs/...md:41, :48, :44, :45.
- verification/M2-QUAL-DETERM-CALIB/calibration.json:5 (summaries_dir), :1253? (min_min 0.7). Let me get the exact line for gate in JSON: diff 1250-1254 → json line = diff − 833. gate min_min diff 1253 → json 420? Hmm: json file starts at diff 834 → json line = diff − 833. gate block diff 1250-1254 → json 417-421. Let me confirm by reading json lines 415-425. And summaries_dir diff 838 → json 5 ✓ (matches grep which said line 5).

Let me do two verification reads: calibration.md lines 60-96, and calibration.json lines 414-424. This ensures my citations are right.
dsh: reasoning:
All citations verified. Now let me write the review report. The user asked for output in a specific format, directly in the reply ("直接输出全文"). So I output the full review text as my answer (not writing a file — the instruction says 输出格式（直接输出全文）).

Should I also write the file doc/reviews/...? The user says "直接输出全文" — output the full text. They didn't ask me to write the file. The handoff suggests the report goes to doc/reviews/M2-QUAL-DETERM-CALIB-e3b7c48d-dsh-r1.md. But my instruction: "输出格式（直接输出全文）" — I'll just output. Writing a file isn't requested; and file-policy is workspace-write (workspace = main repo, not the worktree) — writing to the worktree might be denied. I'll only output the text.

Now compose. Requirements:
## Verdict
## 逐项核对表（A 校准方法学 / B 阈值论证 / C 数据提取 / D 范围纪律与修订面 / E 文档）
## Findings（R1…，P0-P4，文件:行）
## NOT_VERIFIED（集成方运行时项）
## 集成方闭合清单
## 推荐下一步（一句）

Language: Chinese. Keep it dense and precise.

Verdict: I'll say `changes_requested`（0×P0/0×P1；4×P2 全部为 Gate 定义/局限登记缺口，返修面小），plus note that numbers/scope/doc all verified.

Hmm, let me reconsider once more whether to use "approved_with_conditions" instead. The repo's r1 precedent (M2-TA3-B2 r1) was changes_requested for P1; M2-DOCTR-QUAL-C4 r1 was approved_with_conditions with P1+P2s. Here 0 P1, 4 P2 (all definitional/documentation). Following C4 precedent (approved_with_conditions with 1 P1 + 2 P2 + 6 P3), 0 P1 + 4 P2 → `approved_with_conditions` is arguably the calibration-consistent choice. The conditions are: close/register R1–R4 (P2) before or during integration.

I think `approved_with_conditions` is more proportionate and consistent with repo precedent, with explicit conditions C1–C4 (closed by 文档扩写/一句口径补充，可由集成方与 Owner 协作落字). Let me go with that, and be explicit that none of the P2s invalidates the numbers, but three of them touch the newly authoritative thresholds wording, so they must be closed before the Gate is executed by a future runner.

Let me write it.

Structure of 逐项核对表: rows per numbered focus item with 结论 (通过/有条件通过) and evidence.

Focus items:
1. 校准方法学
2. 阈值论证
3. 数据提取正确性
4. 范围纪律
5. 文档

I'll map each to A–E sections as requested with sub-items.

For "A 校准方法学": reading_order 有效性、region 数不同→fail-closed 实现、空对口径、Levenshtein 归一实现正确性、normalized vs raw 关系与 Gate 采用 normalized 的论证。

Include the verified evidence: K11 run1 vs rerun bbox 13/13 一致（我逐条比对 reading_order 1–13 的 bbox：45/6/123/48 等全部相同，region_id 全部不同）→ 说明当前数据集上对齐可靠；脚本无几何断言 → R1.

For "B 阈值论证": median 边界数学（≤8→1.0 成立；≥9→≤0.9375 以幅度带为条件）; min 余量（数值可锚定，但"一个字符级余量"表述不成立，4 字串 2 编辑=0.5）; 合成对照代表性; 无自然 FAIL 样本的披露程度（已披露 limitation 2，方向正确，但词面口径固有误报方向未登记）。

For "C 数据提取": 18 对构成与源 summary 一致（K11 13 regions/13 translate_details; BJ02 5/5; K01 0/0 且两 run 均 0）；逐对文本与 rerun 文件逐条一致；raw 7/11 与 quality-report F5 记录一致；ro=5/10 被 §0 归一化吸收的披露合理（calibration.md:28/§6.5、脚本 :306-309）；分布数字我独立重算一致（列出重算结果）；但完整性断言缺失（R7）与两处非空定义不一致（R6）。

For "D 范围纪律": 7 文件全在允许面；qual-*.json 不在 diff；thresholds 仅 2 hunk（§5 行替换+注、§7 第 10 行），0.10/0.15/0.20/0.25/3.5/80%/70% 全未动；phase2-plan 3 hunk；无 src/tests/contracts/STATUS/TA3-A；e3b7c48d 的 6 文件 +1338/−7 与 handoff 声明一致（我按 diff 逐 hunk 计数）。

For "E 文档": 5 条局限、handoff 复现命令、修订来源标注（4 处均含「M2-QUAL-DETERM-CALIB + 用户裁决 2026-10-01」）、局限 5 条中缺 3 项（R1/R2/R4）→ 条件；quality-report 残留（R10）；Task AC3 §1（R11）；handoff 7/13（R12）。

Now the findings list with severity and file:line. Then NOT_VERIFIED, 闭合清单, 推荐下一步.

Let me write out the report carefully but not overly long. It'll be long anyway; that's appropriate for this task.

For NOT_VERIFIED:
- 脚本重跑一致性（`python experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py` 两次 diff=0）——沙箱无 shell，未执行；已用人工重算关键分布代替（结果一致）。
- `git status --porcelain` 干净、`git diff --check` EXIT=0、`git show --stat e3b7c48d`。
- 半成品草稿的 4 处修正（草稿未入库，无法比对 SyntaxError 前后）。
- review-input.diff 生成口径（是否 path-filter / 是否 8996ca55..2400b57a）；分支 fork=8996ca55 vs 声明 base=8e0de8d0（reflog 已证 fork 点，但未验证 8e0de8d0 是否与 8996ca55 内容等价于本任务面）。
- calibration.json 与脚本的真实产物一致性（仅静态/人工重算，未执行）。

闭合清单:
1. 落地 R1–R4（P2）：thresholds §5 增补 ①对齐几何交叉校验（或登记为假设）②空跑/覆盖度前置 ③0 对 case（K01）判定 ④min 腿长度悬崖；至少 calibration.md §6 加 3 条局限 + thresholds 一句。
2. R5–R9（P3）择要落字（median 边界条件、非空定义统一、完整性断言、双轨判别规则）。
3. 集成方核对回退面与 fork：`git diff --stat 8996ca55..2400b57a`（应 7 文件）与 `git diff 8e0de8d0..8996ca55 --stat` 确认 release 提交未夹带本任务禁改面。
4. STATUS/PLAN：REBASELINE_PLAN 无 M2-QUAL-DETERM-CALIB 行、STATUS 无该 Task（禁改面）——集成方须补 Task 行/Active Task 记录，否则本 Task 处于「无登记即交付」状态。
5. quality-report.md:189/199 残留 superseded-pending 的关系注（或记录不改理由）。
6. Task AC3 的「§1」更正为实际修订面（§5/§5 尾注/§7 第 10 行）。
7. 回退：revert 2400b57a+e3b7c48d 即回 base（thresholds/plan 一并回退）；无数据副作用。
8. 数据和 artifact：calibration.json 的 summaries_dir 绝对路径建议改相对路径后重生成（会导致一次 artifact churn，可并入本次返修）。

推荐下一步（一句）：交回 Owner（ZCode）做 P2 文档级返修（thresholds §5 与 calibration.md §6 补 4 条口径/局限），随后 Codex 集成并同步 STATUS/PLAN 登记。

Now write the final answer.
## Verdict

**`approved_with_conditions`（0×P0、0×P1；4×P2 + 7×P3 + 3×P4）**

判定依据：本轮的**事实面与数字面全部独立复算通过**——18 对构成、逐对文本、raw 7/11 与 normalized 5/13、四个 median/min/P10、聚合 16/18 分母，我用源 summary JSON 手工重算与 `calibration.json` 逐值一致；范围纪律（零 `src/tests/contracts`、`qual-*.json` 零出现、thresholds 只动 superseded-pending 相关 2 处 hunk、phase2-plan 3 处）逐行核对成立；`e3b7c48d` 的「6 files / +1338 / −7」我按 diff 逐 hunk 计数亦精确吻合。

未给 `approved` 的唯一原因：**本次交付把「相似度 Gate」写成了权威执行口径，而该 Gate 定义仍有 4 处未被登记/未定义的缺口（R1–R4）**，其中 3 处可能在将来 runner 执行时产生不可解释结果或误 PASS。这些缺口**不在数字里**（数字诚实且可复现），而在 Gate 定义与局限登记的完备性上（AC4 的直接范围）。返修面为文档扩写 + 1 处可选 fail-closed 断言，不改任何已注册数值；条件闭合后可立即集成。

---

## 逐项核对表

### A 校准方法学

| # | 核对项 | 结论 | 证据（我独立核对） |
|---|---|---|---|
| A1 | reading_order 对齐的有效性 | **通过（附条件 R1）** | 对齐实现正确：先建本 run 的 `region_id→reading_order`（`calibrate_determinism.py:144-157`），再以 reading_order 为键配对；我用两次 K11 summary 逐条比对 **13/13 个 region 的 bbox 与 reading_order 完全一致、region_id 全部不同**（如 ro=1：run1 `eada0f25…`/rerun `591425e1…`，bbox 均 45,6,123,48），r1 R1「region_id 每 run 重生成」的方法学事实成立，本次数据上对齐可靠。**缺口**：脚本只校验键集合相等（`:280-284`），无任何几何交叉校验，无法检出「同键集不同序/置换」——见 R1 |
| A2 | 两次 run region 数不同 → fail-closed | **通过** | `set(t1) != set(t2)` → `raise SystemExit("FATAL: … alignment impossible")`，非零退出、无静默降级（`:280-284`）。K01 两 run 均 `region_count=0` → 两侧空集相等 → 不触发（不误报），但引出 R3 的 0 对场景未定义 |
| A3 | 空对口径合理性 | **方向合理，登记不完备（R2）** | 双方空=1.0、单方空=0.0（`:126-136`、`calibration.md:14`），规则是「先登记后使用」而非临时约定，单方空取 0.0 为 fail-closed 方向 ✓。实测确仅出现 `empty_both`（K11 ro=9 源 `"\n\n"`、ro=13 SFX SKIP；我核对了全部 18 对的 status，无 `empty_one_side`）✓。**缺口**：Gate 取「全部对」（含 2/13 空对=1.0 白送分），全空/大面积空跑可 PASS——见 R2 |
| A4 | Levenshtein 与归一化实现正确性 | **通过** | 两行 DP 递推 `min(prev[j]+1, curr[j-1]+1, prev[j-1]+(ca!=cb))` 与边界短路均正确（`:110-123`）；`similarity = 1 − dist/max_len` 正确（`:126-136`）。与 `experiments/M2-TA3-B/measure_cer.py:51-75` 逐字符比对 **语义完全一致**（仅 `min()` 调用换行格式不同），未跨目录 import 的理由（M2-TA3-B 在禁改面）成立。归一化：去全部空白 + `…`/`\u22ef`→`...` + casefold，与 thresholds §0（`quality-thresholds.md:13`）一致 |
| A5 | normalized vs raw 两口径关系与采用 normalized 的论证 | **通过** | 双口径并存且可复现 F5 观察；「Gate 口径=normalized，raw 附报」的理由（换行/空格级渲染差异不计入翻译不稳定、与项目 CER 同口径）成立且有先例；K11 ro=5/ro=10 raw 浮动但 normalized=1.0 的吸收**在 `calibration.md:28` 与脚本注释 `:306-309` 明示披露**，浮动对子集按「各口径 similarity<1.0」定义而不用 `status=="variant"` 的修正正确（我用 JSON 复核：raw 浮动 7、normalized 浮动 5）。残余口径依赖已登记为局限 5（`calibration.md:94`） |

### B 阈值论证

| # | 核对项 | 结论 | 证据 |
|---|---|---|---|
| B1 | median ≥0.95 的边界数学 | **算术成立，条件是幅度带（R5）** | 18 对下浮动 ≤8 时中位两位（第 9/10 位）恒为 1.0 → median=1.0 ✓；浮动 ≥9 时 median=(v₉+1)/2，v₉≤0.875 → ≤0.9375<0.95 ✓ **但该上界以「浮动幅度 ≤0.875」为前提**；`calibration.md:69` 已写「以实测浮动幅度 [0.75,0.875] 计」，措辞基本自洽，唯「恒 FAIL」的性质需随长度变化——见 R5 |
| B2 | min ≥0.70 的余量论证 | **数值可锚定，「一个字符级余量」不成立（R4）** | 锚点 0.75（4 字串单字替换）正确；0.75−0.05=0.70 ✓。但 `calibration.md:68`/脚本 `:487` 称「留一个字符级测量余量（±1 编辑差）」——**4 字串的 1 个编辑差 = 0.25，不是 0.05**；4 字串再退一步即 2/4=0.5 → FAIL。故 0.70 对短串实质是「至多 1 字之差」的近精确匹配，不是「吸收 ±1 编辑」 |
| B3 | 0.70 太松/太紧 | **两端各有未登记边界** | 太紧侧：局限 3 只写「3 字」，未量化 4 字串同样的悬崖（R4）。太松侧：长译文 30% 字符替换（如 20 字串改 6 字 = 0.70）在 `>=` 语义下 PASS min leg，且被 median 稀释——`drift_40`（min 0.5）只证明了 40% 能抓，30% 抓不到，未登记（并入 R8） |
| B4 | 合成对照能否代表真实漂移 | **作为「度量响应演示」成立，作为「漂移模型」不足（R8）** | 三探针均为「随机字符替换」，能证明 min/median 两腿的响应方向；但真实 remote 漂移的主形态是**同义改写/整段重译**，且本 Gate 是**词面口径**（`calibration.md:84` 表述正确），语义等价的合法重译会被判低相似度→FAIL。该固有误报方向未登记为局限 |
| B5 | 「无自然 FAIL 样本」局限的披露与缓解 | **披露诚实、缓解部分成立（并入 R8）** | `calibration.md:91`（局限 2）与 `:70`（「非 FAIL 实证、仅演示阈值判别力」）措辞准确，未把合成对照冒充实证 ✓；缓解手段（三探针覆盖 min/median 两腿）合理，但缺口是「无真实漂移形态样本」（B4/R8）与「探针自身出现 0.9375 浮动仍被称恒 FAIL」（R5） |

### C 数据提取正确性

| # | 核对项 | 结论 | 证据 |
|---|---|---|---|
| C1 | 18 对构成与源 summary 一致 | **通过** | `qual-K11.json`：`regions` 13 条、`translate_details` 13 条、`detect.region_count=13`，与 `n_pairs=13` 一致；`qual-BJ02.json`：5/5/5，与 `n_pairs=5` 一致；K01 两 run 均 `region_count=0`、`regions=[]`、`translate_details=[]`（我直读 `.rerun.json:52`），脚本注释称「K01 两侧 region_count=0」准确 |
| C2 | 逐对文本与源文件一致 | **通过（逐条）** | 我用 `calibration.json` 的 `text_first`/`text_second` 与 `qual-K11.json:568-685`、`qual-K11.rerun.json:568-684`、`qual-BJ02.json:299-344` 逐条比对：18/18 完全一致（含 ro=5 换行位移、ro=10 空格差异、ro=11「泰阳！！/泰阳阳！！」、BJ02 ro=4「所谓强大/所谓强啊」） |
| C3 | 复现 F5 的 7/11 观察 | **通过** | `quality-report.md:144`「Run2 译文浮动（7/11 非空口径，DSH r1 修正原 7/13 混用分母）」；`calibration.json` K11 `raw_nonempty.n_variant=7/n=11` ✓（`n_pairs_nonempty=11`=13−2 空对） |
| C4 | 统计量独立重算 | **通过（全部吻合）** | 我手算：K11 raw_all median=0.9474、raw_nonempty median=0.9、normalized_all median=1.0/n_variant=5、variant_only median=0.75；BJ02 p10=0.85；聚合 raw_variant_only median=(0.75+0.8571)/2=0.8035、raw_nonempty median=(0.9474+1)/2=0.9737、normalized_nonempty median=1.0 —— 与 `calibration.json` 逐值一致，`percentile()` 线性插值实现无误 |
| C5 | ro=5/ro=10 归一化吸收的披露 | **通过（充分）** | `calibration.md:28` 报告正文、脚本 `:306-309` 代码注释、局限 5（`:94`）三处披露，并在阈值依据（`quality-thresholds.md:168`）以「K11 normalized 浮动 5/13」明示 |
| C6 | 提取完整性保障 | **不足（R7）** | 只断言两次 run 的键集合互等，未断言 `translate_details` 覆盖本 run `regions[]`；两 run 同时缺同一 region 时**静默丢对**（n_pairs 变小、median 更易 PASS，fail-open 方向）；detail 的 `region_id` 不在 `regions[]` 时抛未捕获 `KeyError` 而非注册的 SystemExit（`:146,150`） |

### D 范围纪律与修订面

| # | 核对项 | 结论 | 证据 |
|---|---|---|---|
| D1 | 零 `src/**`、`tests/**`、`doc/contracts/**` | **通过** | review-input.diff 共 7 文件：handoff、Task、`experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py`、`verification/M2-QUAL-DETERM-CALIB/{calibration.json,calibration.md}`、`quality-thresholds.md`、`phase2-plan.md`；无 src/tests/contracts/`experiments/M2-TA3-A/**`/`doc/STATUS.md` |
| D2 | `qual-*.json` 零改动 | **通过** | diff 中不出现任何 `phase2/summaries/**`；我另核对了 K11/BJ02 两次 run 的 export sha256（BJ02 双 run 均 `5c74a4f0…`、size 8759037=上界参照成立；K11 `2c5dee05…` vs `86ff9aa7…`=MISMATCH 如记录），源产物内容与 Task 描述一致、无被改写迹象 |
| D3 | thresholds 只动 superseded-pending 相关条目 | **通过（逐行）** | `quality-thresholds.md` 仅 2 个 hunk：`:168` 行替换为双轨两行 + `:172` 注替换；`:205`（§7 第 10 行）。其余阈值数值 **0.10/0.15/0.20/0.25（OCR）、≥70%/n≥15（SFX）、中位数 3.5/≥80%（对白）、pipeline_failures=0** 全部零改动 ✓；§1 无 superseded-pending（R9 原注确在 §5 行/§5 尾注/§7 行），handoff 关于「仅剩修订注内解除表述」的 grep 声明在该文件内成立 ✓ |
| D4 | phase2-plan 三处同步 | **通过** | `:17`（§1 交付物）、`:33`（§2.1 确定性复跑）、`:182`（§4 步骤 5），各 +1/−1，三处均引用 thresholds §5 注与 calibration.md |
| D5 | delivery 文件清单与 stat 自洽 | **通过** | 按 diff 逐 hunk 计数：`e3b7c48d`=6 文件（脚本 713 + json 512 + md 96 + Task 10 + plan 3 + thresholds 4 = +1338；−1−3−3 = −7）与 handoff「6 files，+1338/−7」精确一致；handoff 文件本身属 tip 提交 `2400b57a`（worktree HEAD 已由 ref 确认为 `2400b57ae65b…`）✓ |
| D6 | base/fork 标注 | **轻微不一致（R14）** | Task frontmatter `base_commit: 8e0de8d0`，但 worktree reflog 显示分支创建点=**8996ca55**（主仓 reflog：`8e0de8d0`=close(M2-TA3-B2)，`8e0de8d0→8996ca55`=release(4-task batch)），且 `main` 现仍在 8996ca55 |

### E 文档

| # | 核对项 | 结论 | 证据 |
|---|---|---|---|
| E1 | 局限五条登记 | **通过但需扩写（R1/R2/R4）** | `calibration.md:90-94` + `calibration.json.limitations`（5 条）齐备：n=2、无自然 FAIL、极短译文粒度、Run1 层未测、归一化口径依赖；缺「对齐置换」「空跑覆盖度」「短串 min 悬崖/词面误报」 |
| E2 | handoff 复现命令 | **通过** | `handoff:53` `python experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py`（可选 `--summaries-dir/--out-dir`），与脚本 `:583-591` 参数一致；`handoff:54` 给出三条 Reviewer 检查建议，可执行 |
| E3 | 修订来源标注 | **通过（4 处全覆盖）** | `quality-thresholds.md:168/172/205`、`phase2-plan.md:17/33`、`calibration.md:7`、`handoff`/Task 交付记录均标「M2-QUAL-DETERM-CALIB + 用户裁决 2026-10-01（全部进行）」 |
| E4 | 与既有文档的一致性 | **有残留（R10/R11/R12）** | `quality-report.md:189/199` 仍写 superseded-pending（历史裁决点，未加关系注）；Task `:27` AC3 含「§1」（实际无此项，未登记空核对）；`handoff:41` 回潮「7/13（非空 7/11）」表述 |
| E5 | 规划/状态登记 | **集成侧待办（不在 Owner 允许面）** | `doc/REBASELINE_PLAN.md` 全文无 M2-QUAL-DETERM-CALIB 行（仅 `:115` TA3-B2 行提到「F5 裁决移交」）；`doc/STATUS.md` 无该 Task 任何字样——handoff 只声明 STATUS 需集成方更新，未提 PLAN |

---

## Findings

**R1｜P2｜对齐校验只覆盖键集合，无法检出 reading_order 置换（可能误 FAIL 或对近似重复 region 误 PASS）**
`experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py:280-284`（`set(t1) != set(t2)`）、`:144-157`；`calibration.md:9-15`
两次 run 的 reading_order 键集合相等即可通过，但**有序置换（同一 detect 输出集合、排序不同）会让 region 错配**：K11 存在 6 个近乎重复的短台词（`胡萝卜？`/`小萝卜！`/`胡萝卜！`/`胡萝卜？！`…），错配可把「真浮动对」与「相同对」互换成看似良性的 0.75 浮动（误 FAIL）甚至 1.0（误 PASS）。该假设在本次数据中成立（我核对 13/13 bbox 逐条相同），但脚本未把「reading_order 跨 run 稳定」写成断言或局限；`bbox` 在两个 summary 中均可得，交叉校验成本极低。
**建议**：对齐时逐 reading_order 断言 bbox 一致（不一致即 fail-closed，与现有 FATAL 同一风格）；或至少在 `calibration.md §1`/§6 登记该假设与失效方向。

**R2｜P2｜「双方空=1.0」+ Gate 取全部对 = 全空/大面积空跑的覆盖度盲点**
`calibrate_determinism.py:132-135`、`:322-324`（Gate 用 `pairs` 全量）；`calibration.md:14`、`:64`
两 run 都返回空译文 → 相似度 1.0 → 计入 Gate。若 translate provider 整体失效（两 run 全空）或某 case 绝大多数 region 为空（SFX SKIP、OCR 空），median 被 1.0 支配 → **Gate 可 PASS 而实际零翻译产出**。这是 fail-open 方向的判别力空洞，且未列入五条局限。
**建议**：在 Gate 定义中加覆盖前置（如「非空源 region 中译文非空比例」或「非空对 n≥1」），或在局限中明写「全空跑可 PASS，由 §7 第 8 行 translate 评分 Gate 兜底」，并把二者关系写进 `quality-thresholds.md:168`。

**R3｜P2｜权威口径命名的固定 3 case 中 K01 为 0 对，0 对场景的 Gate 判定未定义**
`quality-thresholds.md:168`（「固定 3 case（BJ02/K01/K11）…全部对齐对…满足 median ≥ 0.95 且 min ≥ 0.70 方为 PASS」）；`qual-K01.json:51-58`、`qual-K01.rerun.json:50-58`
K01 两 run 均 `region_count=0`（`data:no-regions-detected`），K01 实际贡献 0 对；脚本对空分布返回 `NO_DATA`（`:258-265`），但 thresholds 只定义了 PASS/FAIL，未说明 0 对 case 是豁免（R11 同构）还是 NO_DATA、以及 NO_DATA 是否阻断整体 Gate。同时 §5 依据栏仍保留「固定 3 case 覆盖三家族」的表述，而校准实际只覆盖 ja BJ + ko P&C 两家族（K01 家族缺席）。
**建议**：在 §5 双轨条目补一句 0 对/`region_count=0` 的判定与豁免口径，并注明本次校准未覆盖 ko webtoon 家族。

**R4｜P2｜min 腿的余量语义与短串粒度不匹配，「一个字符级余量」不成立**
`calibration.md:68`、`calibrate_determinism.py:484-491`、`calibration.md:92`（局限 3）
0.75−0.05=0.70 的算术没错，但把 0.05 说成「一个字符级测量余量（±1 编辑差）」在锚点串（4 字）上错误：4 字串 1 编辑差 = 0.25，2 编辑差 = 0.5 → FAIL。即 min ≥0.70 对 4 字译文实质是「至多 1 字之差」，任何 2 字的良性词面变化都会 FAIL（K11 的 `胡萝卜↔小萝卜` 已是同义替换，仅因恰好 1 字才通过）。局限 3 只覆盖 ≤3 字，未量化 4 字悬崖，也未给改判方向。
**建议**：把余量表述改为「0.05 绝对值余量」（thresholds `:168` 的写法已正确，`calibration.md` 应与之统一）；局限 3 扩写为「长度相关悬崖」并给 4 字反例（2 编辑→0.5）；可选按译文长度分档或对 <6 字串单列规则。

---

**R5｜P3｜median 边界「≥9 对浮动恒 FAIL」以浮动幅度带为条件，探针自身已突破该带**
`calibration.md:69`、`:74`（`single_char_ge4` max=0.9375）、`:78`
median=(v₉+v₁₀)/2 的 FAIL 条件是 v₉<0.90；「≤0.9375」只在浮动幅度 ≤0.875 时成立。对长译文（1 编辑差即 ≥0.9），「全部 region 各漂 1 字」可 median ≥0.95 而 PASS。`:78` 的闭环句「『全部对 1 编辑浮动』→ median leg FAIL」因此是**探针长度分布下的结论，非普适**。
**建议**：把该句限定为「在本校准样本的译文长度分布下」，并在局限中登记「median 腿对低幅系统性漂移的分辨力随译文长度下降」。

**R6｜P3｜「非空对」两处定义不一致；`pair_status` 用 strip 而 `similarity` 用原串**
`calibrate_determinism.py:305`（排除 `empty_both`）vs `:595-597`（排除 `empty_both`+`empty_one_side`）；`:160-165` vs `:126-136`
同一 artifact 内 per-case 与 aggregate 的「非空」分母定义不同（当前数据无 `empty_one_side`，故数字巧合一致，将来必然分叉）。另：仅空白差异时（如 `"\n"` vs `" \n"`）`status=empty_both` 但 `similarity=0.0`，status 分类与相似度口径互相矛盾。
**建议**：抽一个 `is_nonempty(pair)` 供两处共用；`similarity` 与 `pair_status` 统一判空基准（建议都用 normalize 后的空串）。

**R7｜P3｜提取完整性未断言，存在静默丢对（fail-open）与未捕获 KeyError**
`calibrate_determinism.py:146`、`:150`、`:280-284`
只比对 t1/t2 键集合，未比对 `regions[]` 全集；两 run 同时缺同一 region 的 `translate_details` 时该对静默消失（n_pairs 变小、median 更易 PASS）。`region_id` 不在 `regions[]` 时 `order[...]` 抛裸 `KeyError`（非注册的 FATAL 退出）。本数据 13/13、5/5 覆盖完整，故不影响当前数字。
**建议**：加 `set(t1) == set(t2) == {r["reading_order"] for r in regions}` 断言并落盘 `dropped_regions`；`order.get(...)` 缺失时走同一 SystemExit 通道。

**R8｜P3｜判别力对照只覆盖「随机字符替换」，缺真实漂移形态；词面口径的固有误报方向未登记**
`calibrate_determinism.py:205-247`（`perturb` 单字符池随机替换）、`calibration.md:70-78`、`:84`、`:91`
三探针均模拟「均匀随机字替换」，未覆盖最可能的 remote 漂移形态（同义改写、整段重译、插入/截断）。Gate 是**词面**度量（§1.5 已明示「词汇级一致性」），因此「语义等价、词面不同」的合法重译会被判低相似度 → min/median 双腿 FAIL。这是该口径的固有误报方向，未进五条局限。
**建议**：局限中增补一条；探针可加「同义改写代理」（如对固定比例 region 注入语义等价的替换词），以显示该口径在真实漂移谱上的位置。

**R9｜P3｜双轨口径缺运行期判别规则**
`quality-thresholds.md:168-169`、`phase2-plan.md:33`
「remote/随机采样翻译链 → 相似度 Gate；mock/deterministic 链 → export 哈希逐位」没有可执行的判别依据（provider id？配置标志？run 参数？）——未来 runner 无法从文档确定走哪轨。
**建议**：在 §5 或 phase2-plan §2.1 补一句判别规则（如「按 provider 绑定是否 remote 采样」或新增 `--determinism-track` 参数），否则该双轨在实现时仍需二次裁决。

**R10｜P3｜`quality-report.md` 残留两处 superseded-pending，handoff 的 grep 声明只覆盖 thresholds**
`verification/M2-TA3-B/quality-report.md:189`、`:199`；`handoff:44`
handoff 用「`grep -n superseded-pending verification/M2-TA3-B/quality-thresholds.md` → 仅剩解除表述」作为 AC3 证据，范围正确，但读者容易读作「全仓无残留」；报告 `:189/:199` 仍写「重定义前 thresholds §5/§7 按 superseded-pending 引用」，该状态已解除。
**建议**：报告 `:189/:199` 加一行关系注（「已由 M2-QUAL-DETERM-CALIB 于 2026-10-01 落地」），或在 handoff 中明写「报告内为历史裁决点、有意不改」。

**R11｜P3｜Task AC3 的「§1」核对为空，未登记**
`doc/tasks/M2-QUAL-DETERM-CALIB.md:27`（「§5/§7/§1 的 superseded-pending 条目」）vs 实际修订 `quality-thresholds.md:168/172/205`；`handoff:33` 只写 §5/§7
R9 原注确不在 §1（旁证：`doc/reviews/M2-TA3-B2-7922a3fc-dsh-r2.md:23` 只点 `:168/:171/:204`）。AC 面被悄悄缩窄而未登记，属 AC 闭合不完整（Task/Handoff 均在 Owner 允许面）。
**建议**：Task `:27` 改为实际修订面并注明「§1 核对为空（R9 原注不在 §1）」。

---

**R12｜P4｜handoff 回潮已被 quality-report 修正的分母措辞**
`handoff:41`「raw 口径 K11 浮动 7/13（非空 7/11）」
`quality-report.md:144` 明确「DSH r1 修正原 7/13 混用分母」。虽然「7/13=全部对口径、7/11=非空口径」字面为真，但在已被定案更正的位置重新以 7/13 起头，易再次传播旧分母。`calibration.md:28` 与 `:44` 的写法（先 7/11 非空、再 normalized 5/11）是正确的，建议 handoff 对齐。

**R13｜P4｜`calibration.json` 写入 worktree 绝对路径，跨 checkout 复跑即 churn**
`verification/M2-QUAL-DETERM-CALIB/calibration.json:5`（`summaries_dir: G:\CODEX\New Manga.worktrees\M2-QUAL-DETERM-CALIB-zcode\…`）
与脚本「确定性、两次运行输出一致」的声明在同一 checkout 内成立，但在主仓路径重跑会改写该行（产物非环境无关）。集成方若在主仓复跑校准，会产生一次无意义 diff。
**建议**：`calibration_source.summaries_dir` 改存相对仓库根的路径（其他 TA3-B2 产物已有绝对路径先例，故仅 P4）。

**R14｜P4｜声明的 base_commit 与分支实际 fork 点不一致**
`doc/tasks/M2-QUAL-DETERM-CALIB.md:12`（`base_commit: 8e0de8d0`）；worktree 分支 reflog 首条 = `8996ca55`
主仓 reflog 证实：`8e0de8d0`=close(M2-TA3-B2)，`8e0de8d0 → 8996ca55`=release(4-task batch)，main 现仍在 `8996ca55`。因此本分支实际 fork 点是 release 提交，`base_commit` 是「Task 冻结基线」而非分支基线；review-input.diff 若按 fork 点计算则与此标注不一致（见 NOT_VERIFIED）。
**建议**：frontmatter 注明 `fork_commit: 8996ca55`（或统一 base 语义），后续 Task 同此。

---

## NOT_VERIFIED（集成方运行时项）

沙箱内 `pwsh` 无法建立（`SetNamedSecurityInfoW failed: grantWrite(G:\CODEX\New Manga)`），本轮为纯静态 Review，以下留集成方：

1. **校准脚本真实重跑一致性**：`python experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py` 两次运行 diff=0（handoff 证据表 `:40` 的 PASS 依据）。我以源 JSON **人工重算占全部关键统计量并逐值吻合**（见 C4），但未执行脚本，故「脚本产物 ↔ 提交的 calibration.json/.md 字节一致」仍属运行期项。
2. **工作区洁净与格式检查**：`git status --porcelain` 为空、`git diff --check` EXIT=0、`git show --stat e3b7c48d`（handoff `:45` 的 PASS 依据）。
3. **diff 生成口径**：review-input.diff 是 `8e0de8d0..2400b57a` 全量、还是按 fork 点/路径过滤（我据此无法排除「release 提交夹带其他三 Task 文档」被过滤掉）；建议集成方跑 `git diff --stat 8996ca55..2400b57a`（应为 7 文件）与 `git diff --stat 8e0de8d0..8996ca55`（确认 release 提交未触及本 Task 禁改面）。
4. **半成品草稿的 4 处修正**：草稿不在版本库（handoff `:14`/`:21-25` 自述），无法比对「SyntaxError 前后 / 浮动对子集定义 / 探针判定语义 / median 推导」的改动事实。
5. **`--summaries-dir/--out-dir` 分支路径**：脚本自定义目录分支的正确性（默认路径已静态核对）未运行验证。
6. **双轨 Gate 在真实 runner 上的落地**：未运行（handoff `:46` 已如实标 NOT_RUN，AC 无此要求）。

---

## 集成方闭合清单

1. **闭合 R1–R4（P2，条件项）**：①对齐加 bbox 交叉断言或把「reading_order 跨 run 稳定」写进 `calibration.md §6` 与 thresholds §5 注意；②空跑/覆盖度前置条件（或明写由 §7 第 8 行评分 Gate 兜底）；③§5 补 `region_count=0`/0 对 case 的判定与豁免口径，并去掉/限定「固定 3 case 覆盖三家族」的隐含完整性；④局限 3 扩写为长度相关悬崖（4 字 2 编辑=0.5），余量表述统一为「0.05 绝对值」。
2. **择要落字 R5–R9（P3）**：median 边界加长度前提；统一「非空对」定义；补提取完整性断言 + `dropped_regions`；局限增补词面口径误报方向；§5/phase2-plan 补双轨判别规则。
3. **R10–R14（P4）** 可一并落字（报告关系注、Task AC3 §1、handoff 7/13、`calibration.json` 相对路径、fork_commit 标注）。
4. **规划/状态登记（不在 Owner 允许面）**：`doc/STATUS.md` 无本 Task 记录、`doc/REBASELINE_PLAN.md` 无本 Task 行——集成方须补 Active Task/任务行，否则本交付处于「已交付但未登记」状态（与 AGENTS.md「当前唯一 Active Task 只以 STATUS 为准」不符）。
5. **范围与回退复核**：`git diff --stat 8996ca55..2400b57a` 应为 7 文件、禁改面零出现；回退=`revert 2400b57a` + `revert e3b7c48d` 即回 base（thresholds/plan 修订一并回退，无数据迁移、无外部副作用）。
6. **产物完整性**：确认 `verification/M2-QUAL-DETERM-CALIB/` 仅两文件、`experiments/M2-QUAL-DETERM-CALIB/` 仅脚本；若按 R13 改相对路径，需重生成 `calibration.json`（会 churn 1 行，建议并入本次返修）。
7. **不释放范围声明**：本 Task 不解释也不修复 K11 Run1 层 export 哈希根因（thresholds `:169` 已界定范围），集成后如需追责渲染/导出层确定性，应另立 Task。

---

## 推荐下一步

交回 Owner（ZCode）做 P2 文档级返修：在 `quality-thresholds.md:168` 与 `calibration.md §6` 补入 R1–R4 四项口径/局限（对齐置换校验或登记、空跑覆盖度、K01 0 对判定、短串 min 悬崖并把余量表述改为 0.05 绝对值），完成后由 Codex 集成并同步 `STATUS`/`REBASELINE_PLAN` 的任务登记。
