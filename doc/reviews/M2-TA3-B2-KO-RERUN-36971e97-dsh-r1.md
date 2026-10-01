dsh: reasoning:
There's a sandbox issue with the PowerShell command. Let me try using glob or read tools directly instead, since the sandbox is in workspace-write mode and the task-envs path is outside the workspace.

Let me check the diff and worktree paths.
dsh: reasoning:
The diff is 15491 lines. Let me plan the review. I need to read key documents:
1. Task doc: doc/tasks/M2-TA3-B2-KO-RERUN.md (in worktree)
2. Handoff
3. verification/M2-TA3-B/ko-rerun-report.md
4. phase2/ko-rerun/** (budget-register.json, summaries)
5. The diff for scripts.

Let me check the worktree exists and read the key files. Let me use parallel reads.

First let's check worktree structure.
dsh: reasoning:
pwsh seems blocked by sandbox (SetNamedSecurityInfoW failed). The task says "沙箱无 shell 时不执行命令" — so no shell. I'll do static review only using read/glob/grep.

Let me look at the worktree files. Let me use glob.
dsh: reasoning:
Important finding already: the Task doc's 纪律 section does NOT contain a "50 万 est token 红线". The task AC5 says: "翻译预算控制——ko region 总量可能数百（K01 检测解锁后 180 region），预估请求数/先行一个 case 试算后再全量". There's no explicit ">50万即停" threshold in the task doc. The review question #1 explicitly asks: 50 万红线是否任务书原文?

So this is a real finding: the 50万红线 is not in the task doc text. But it's in the user 裁决③ / 背景. Let me check where the 50万 figure comes from — perhaps the user ruling, or the handoff, or dsh-task-r1.txt says "成本纪律=est token 外推 >50 万即停等裁决" as 背景 (user 裁决③+任务纪律). Hmm, the prompt's background says that's from user ruling + task discipline. But the Task doc itself does not include this number. Let me search the repo for "50 万" or "500000".

Also note AC5 says "预估请求数/先行一个 case 试算后再全量" — so the 试算 approach is per task. The stopping was based on extrapolation, which is arguably compliant with "翻译预算控制" but the specific 50万 number isn't documented. Let me grep.

Let me read the main report now.
dsh: reasoning:
Now let's read budget-register.json, K11-similarity.json, cer-summary.json, qual-K11.json (rerun), qual-K02.json (portions), and the diff for the scripts.

Let me also check where the 50万红线 is documented. grep for "50 万" and "500,000" / "500000".
dsh: reasoning:
Key finding candidate: "50 万红线" is NOT in the Task doc's 纪律 section. The Task doc says only "翻译预算控制——ko region 总量可能数百（K01 检测解锁后 180 region），预估请求数/先行一个 case 试算后再全量". So the "50 万 est token" figure has no documented source in the repo — it appears only in the rerun artifacts (self-referential). The brief for this review says the discipline is "成本纪律=est token 外推 >50 万即停等裁决" as 背景（用户裁决③+任务纪律）. So the reviewer must flag: 任务书原文无 50 万数字；该红线来源需追溯（可能来自用户裁决③口头/上游 handoff）。Let me check for any other doc, e.g., doc/STATUS.md, REBASELINE_PLAN, or the user ruling record. Let me grep for "裁决③" and "token" budget.

Also check the upstream task M2-TA3-B2 quality-report.md F1-F6, and CALIB 局限 8, and PRIMARY semantics. Let me grep for "局限 8" and "terminal accounting".

Let me be efficient. Many reads needed. Let me parallelize:
1. grep "裁决③" in repo
2. grep "局限" in verification/M2-QUAL-DETERM-CALIB
3. read K11-similarity.json
4. read cer-summary.json

Also read the diff sections for run_qualification.py changes (the --sfx-policy / --meter-translation implementation) — important for "behavior zero change" and metering proxy claims. The diff is 15491 lines; let me find the run_qualification.py hunk offsets via grep with line numbers on the diff file.
dsh: reasoning:
Interesting: reading_order 10 is also "variant" but normalized = 1.0 — so the gate's min uses normalized values; 12/13 identical is the "逐位一致" claim... actually the claim is "12/13 逐位一致" but pair 10 is status variant with normalized 1.0. The similarity script normalizes whitespace, so "咔咯沙沙沙沙" vs "咔咯沙沙 沙沙" normalize to the same string → similarity_normalized 1.0. That's reasonable but the report says "12/13 对逐位一致（median=1.0）" while the JSON says n_identical=12, n_variant=1 (which includes pair 10 variant but normalized=1.0). Hmm: n_identical=12 counts pair 10? Let's count statuses: identical pairs: 1,2,3,4,6,7,8,11,12 = 9, plus empty_both 9 and 13 = 11... plus pair 10 status variant. So n_identical 12 = 9 identical + 2 empty... that's 11. Hmm, let me recount.

Pairs with status identical: ro 1,2,3,4,6,7,8,11,12 → 9 pairs. empty_both: ro 9, 13 → 2. variant: ro 5, ro 10 → 2. Total 13. n_identical=12 can't be status-based. So n_identical must be counting normalized value == 1.0, i.e. ro1,2,3,4,6,7,8,9,10,11,12,13 = 12 (excluding ro5). Yes: n_identical counts similarity_normalized == 1.0. So "12/13 逐位一致" is accurate in the sense of normalized==1.0, though ro10's raw text differs (whitespace only). Fine — but worth noting as a minor disclosure issue: pair 10 raw text differs ("咔咯沙沙沙沙" vs "咔咯沙沙 沙沙"), and normalized=1.0 means whitespace normalization absorbed it. The report says "仅 1 处浮动" — the JSON says n_variant=1 in stats but pairs list has 2 variant statuses. This is an internal inconsistency worth a P3/P4 finding: stats.n_variant=1 (normalized-based) vs pairs[].status variant count=2. Not a correctness break of the gate (min leg is what matters) but the "12/13 逐位一致" phrasing could be misread; the report should disclose pair 10's raw-text difference. Actually the report says "逐位一致对 12/13（median=1.0）" and "浮动对 1". The raw-text diff of pair 10 is a genuine sampling difference (spacing in SFX onomatopoeia) that the normalization masked. This is relevant to review item D: whether the "natural FAIL" attribution is honest. It's minor.

Now the 0.4615 pair: source "이렇게까지는 할필요없을줄 알았는데" → "没想到会做到这种地步" (first) vs "我本以为没必要做到这种地步" (second). Both are legitimate translations; the owner judged semantic equivalence. Basis: manual review by Owner? The report claims "语义等价的合法重译" without citing a human reviewer. Reviewer item 4 asks: how did Owner determine. The JSON has no "semantic_equivalence_judgment" field, no human annotation evidence. That's a finding: attribution of "合法重译" is owner self-judgment, not independently verified; and it is the same party that owns the Gate — but the argument is plausible since both renderings are semantically near-equivalent. Actually careful: "没想到会做到这种地步" vs "我本以为没必要做到这种地步" — these are semantically close but not identical ("I didn't think it would come to this" vs "I thought there'd be no need to go this far"). Reasonably equivalent in context. But the report should have recorded the judgment basis and who made it. Finding P3.

Now let me read the diff for the scripts. Focus on run_qualification.py hunk (line 689-940), ko_rerun_similarity.py (433-688), ko_rerun_k11_driver.py (103-271), ko_rerun_readability_increment.py (272-432).
dsh: reasoning:
Important: the `_MeteredTranslationProvider.translate` calls `self._inner.translate(payload)` then records. But note: it imports modules inside translate; `payload.payload_json()` and `result.raw_text`. Is `payload_json()` a method on the payload object? Need to verify against src (forbidden to modify, but I can read). Also `result.raw_text` — does the production result have raw_text? If it doesn't, the metering proxy would raise AttributeError → behavior change (would break translate). Since the run completed and metering recorded 140 requests, it presumably works. But I should verify the production interface to confirm "behavior zero change" claim. Let me check ports/translation/protocol.py and the payload class.

Also note the metering proxy is not a subclass; registry.register with factory returning proxy. `__getattr__` passthrough. Potential issue: production code may use `isinstance` checks on the provider; if so, wrapping changes behavior. Also capability lookup: registry may match provider by capability — the descriptor is registered, not the instance, so fine. If pipeline resolves provider via registry.get(...) and then uses it, the proxy works.

One risk: `__getattr__` only called for missing attributes; `translate` is defined. OK.

Another risk: if the production client retries/fail-closed path uses `translate` exceptions — passthrough unchanged. Fine.

Also the metering records only successful translate() calls (exceptions propagate before append) — disclosed in budget-register.

Now, key review item 6: "计量 proxy 包装「行为零变更」的论证". The claim is behavior-zero-change; but the wrapper is only active with `--meter-translation`, and default off. The report says "experiments 层透传包装，行为零变更" — but wrapping can change behavior if production code does isinstance/type checks or accesses `__class__`. Notably, one real difference: `reregister_env_resolver` (original) vs `reregister_env_resolver_metered` — need to diff the descriptor/note: original probably had a different `note` string. Let me check the original function in the worktree (not in diff context). Let's read run_qualification.py around reregister_env_resolver.

Also for K02's metering: 140 requests = Run1 93 + Run2 47. Run1 is "one sweep of 93 region-level requests". And the claim "83-1721 regions → requests ≈2×regions". Wait — is it really 2×? Run1 = 93 requests (1 per region), Run2 = 93 requests (region-level re-translation). But is Run2 part of the "full chain" for each case? The model says 2× per region. Also, the "known_only_est_tokens 632000" — let's verify: regions 881-1721? Actually known regions: 180+93+113+62+60 = 508 (K01,K02,K04,K05,K08) + K11 13 + K19 0 = 521. Hmm the range 881-1721 includes K07/K09/K10 at 120-400 each: 521 + 360 = 881, 521 + 1200 = 1721. Yes matches. known_only = 521 regions × 2 × 607 = 632,494 ≈ 632k. The report says "已知五页即 ≈63.2 万" but actually 63.2万 includes K11+K19 too (521 regions includes K11's 13). The claim "仅 TILING 已确认的五个 webtoon 页就 63.2 万" — five pages are 508 regions → 508×2×607 = 616,712 ≈ 61.7万. So "仅五个页=63.2万" is slightly off: 63.2万 is 521 regions including K11 (13). Minor numeric overstatement (63.2 vs 61.7万), still >500k. Worth P4 finding: the stated 63.2万 corresponds to 521 regions (incl. K11=13, K19=0), not the five TILING pages alone (508 → 61.7万). Both exceed the line, so the conclusion holds. Good catch for detail-accuracy.

Also "est_tokens_per_region_fullchain": 1214 = 2×607. OK.

Another check: "140 requests = Run1 93 + Run2 47 successful; 46 failed". 93+47=140. ✓. And summary claims "Run2 completed_with_failures（46 region 失败）" — 46 failed + 47 success = 93. ✓

Now: does Run1 really do 1 request per region? The metering records total 140 for both runs combined. If Run1 were batched, e.g. 1 request per page, then requests would be ~1+47=48. Since 140 ≈ 93+47, Run1 per-region is supported. But is Run1 per-region? Actually, wait: K02 summary has run1 and run2 sections. Does the metering attach per-run? No — it's a single records list for the whole case, summing both runs. The inference "Run1 93 + Run2 47" is an arithmetic inference, not measured per-run. The evidence is consistent but the split isn't directly observed. Also possible: Run1 = 140 - 47 = 93 requires knowing Run2's success count. Actually the inference direction: total successful translate() calls = 140; Run2 had 46 failures typed and 47 successes... but is the 47 successes figure from the summary per_region? Presumably. Then Run1 = 93. Consistent. But an alternative: maybe Run1 batches pages and Run2 is per-region with 140 total. Hmm, 140 = 93 + 47 exactly. If Run1 were page-batched it'd be 1 request, so total would be 48. So the inference is solid given Run2=47. Unless Run2 success count differs. I should check qual-K02.json run2 per_region count of successes to validate. Let me check the K02 summary structure.

Actually more important: the claim "Run1 也逐 region 非整页批量" is inferred, not directly measured (no per-run meter split). A reviewer should flag this as an inference with strong support but should have been instrumented per-run (e.g., records tagged with a run label). This affects the cost model (requests ≈2×regions) which drives the stop decision. If Run1 were batched, the full-scale estimate would be ~1×regions → still ~316k-... hmm: 881-1721 regions ×607 = 535k-1044k, still >500k for most of the range. So the conclusion survives either way, but the model's factor is important. Let me note it as a P3 with the recommendation to tag records per run.

Now let me read qual-K02.json key parts. It's huge (line 3780-13117 in diff ≈ 9300 lines). Let me find its top-level keys with grep for pattern of 2-space indentation keys, or read the head.

Let me read the file directly from worktree.

Also need: cer-summary.json, qual-K11.json head, qual-K11.rerun.json head, rerun-compare.json, qual-report.json, svg-alignment-trace.json, cer-regions.csv head.

And the upstream docs: quality-thresholds.md §5, quality-report.md §10, CALIB 局限 8, PRIMARY-SFX-GATE handoff/task for the terminal accounting semantics.

Let me batch reads.
dsh: reasoning:
Note: cer-summary.json has "task": "M2-TA3-B2" and "directional_disclaimer": "first quality run" — it's produced by measure_cer.py which hardcodes those strings; it was output into ko-rerun dir. The rerun's cer-summary.json is essentially a copy of the first-run one? Because measure_cer.py reads summaries-dir and ocr-dir. Here the ko-rerun ocr dir contains only svg-gt-K11/K19 + alignment trace. Hmm, cer-summary.json exists in ko-rerun/ocr/. But wait, is ko-rerun/ocr/cer-summary.json regenerated or copied? Its "task": "M2-TA3-B2" label says it's the same script output with hardcoded task string. Need to check measure_cer.py to see whether "task" is hardcoded — likely yes.

The critical claim "6/6 行与首跑逐位一致" — I need to compare ko-rerun/ocr/cer-regions.csv against the first-run phase2/ocr/cer-regions.csv. Let me read both CSVs.

Also compare svg-gt-K11.json in ko-rerun vs phase2/ocr (said to be read-only copy).

Let me read cer-regions.csv from both.
dsh: reasoning:
Now I can verify the "6/6 行与首跑逐位一致" claim for the G1 auto-scored subset:

Rerun (ko-rerun/ocr/cer-regions.csv) rows with gt_source "G1:svg_native":
- K11:beade011: 당근아? / 당근아? / 0.0000
- K11:80226052: 당근아?! / 당근아?! / 0.0000
- K11:d38c906e: 이렇게까지는할 필요 없을 줄알았는데.. / 이렇게까지는 할필요없을줄 알았는데 / 0.1111
- K11:85aa3e14: 당근아?!!! / 당근아?!!! / 0.0000
- K11:b6f6148c: 어라? 침대 밑에도없네? / 어라? 침대 믿에도 니? / 0.2727
- K11:7c10bc7c: 꼬르륵 / 꼬르를 / 0.3333
That's 6 rows. ✓ n=6.

First run G1:svg_native rows:
- eada0f25: 당근아? / 당근아? / 0.0000
- 1fd86809: 당근아?! / 당근아?! / 0.0000
- 71a21be8: same 0.1111
- 91a52031: same 0.0000
- 152ac05d: same 0.2727
- 789ed861: 꼬르륵/꼬르를/0.3333

Identical gt_text, ocr_text, cer values → 6/6 逐位一致 ✓ (excluding region_id uuid which is regenerated). Good. Also the excluded 7 rows: rerun excluded rows are K11:54f00898, 7860be01, 3f1b7fe3, 9d7500d0, 313c50a2, 362277d3, e762169f = 7 ✓ and same reason categories/gt/ocr as first run ✓. So CLAIM VERIFIED for CER bitwise identity.

Also note median of 6 CER values: sorted [0,0,0,0.1111,0.2727,0.3333] → median = (0+0.1111)/2 = 0.05556 ✓. P90: 0.3333 ✓. zero share 50% ✓ (3/6: values 0 appear 4 times? wait: 0.0000 rows are 4 (beade011, 80226052, 85aa3e14, and... let me recount: rows with cer 0.0000: beade011, 80226052, 85aa3e14 = 3; plus? d38c906e 0.1111, b6f6148c 0.2727, 7c10bc7c 0.3333. So 3/6 = 50% ✓.

Great — the CER claim is verifiable and correct. Now review item E asks about K11 OCR under TILING semantics vs first run: same region count 13, same OCR text → implies tiling did not alter K11's OCR path. Is that explained in the report? The report §3.1 says "PaddleOCR wrapper (enable_mkldnn=False) 跨 run 确定性在 TILING+新语义链下再次证实" but does NOT explain why K11's regions are unchanged under TILING (h/w ratio threshold 4.0 not triggered). Let me verify: K11 page dims. Let me check case-selection.json for K11 size and the TILING threshold semantics. The review item says "K11 h/w 未超 4.0 触发阈值→同路径？核实该解释是否在报告里讲清". Let me grep the report for "4.0" — I didn't see it in the report. Indeed report §3.1/§8 doesn't mention 4.0. So finding: the report does not explain why K11 (non-tiling-triggered) OCR matches first run; it asserts "TILING+新语义链下再次证实" without the mechanism. Also note the first run K11 was already 13 regions — same region geometry? If TILING didn't apply to K11, then same path is expected. Let me verify K11's dimensions and the TILING task threshold.

Let me look at case-selection.json and the TILING doc.

Also critically: the region_ids differ between runs (uuid regenerated), so the "逐位一致" is text/CER-level only, and the claim "同 region" is by alignment (bbox/reading_order). The report says region_id uuid 每 run 再生. Fine.

Now, an important check for item E: does the first-run K11 OCR text really come from a non-tiling run? Yes (first run predates TILING). And under TILING, if K11's page h/w ratio exceeded 4.0 it would be tiled → different region geometry → different OCR. Region count is identical (13) and OCR identical → either K11 not tiled, or tiling produced identical results. Need documentation. Let me check the TILING task doc for threshold and K11 ratio.

K11 = a P&C (Pepper&Carrot) page, likely square-ish → not tiled. Let's verify size.

Let me read case-selection.json (experiments/M2-TA3-B/case-selection.json) and the TILING task/qualification.
dsh: reasoning:
K11 is a P&C page (normal aspect ratio ≤1.41) → does NOT trigger tiling. That's the explanation. It's documented in integration.md but NOT in ko-rerun-report.md. The report's §3.1 should state: "K11 为 P&C 常规页（h/w ≤1.41），未触发 tiling 阈值 4.0 → 与首跑同 detect/OCR 路径，故逐位一致是预期内". Owner didn't state this. Finding: P3 (evidence-chain reasoning gap; the claim is verifiable by external doc but not self-contained in the report).

Let me verify K11's dims from case-selection or the K11 summary. Let me read case-selection.json around K11 and check the K11 summary in ko-rerun.

Let me also read qual-K11.json and qual-K11.rerun.json heads, and the K02 summary head for structure.
dsh: reasoning:
Note: qual-report.json for the K11 driver pass shows "cases": [{"case_id": "K11", "skipped": true, ...}] and "failures": 2. Hmm — "skipped": true? That's odd; and the ko-rerun/summaries/qual-report.json lists only K11 while the K02 run had its own qual-report? Wait, there is only one qual-report.json in ko-rerun/summaries — but K02 and K19 and K11 runs all wrote to the same out-dir (--out-dir …/summaries). Since run_qualification.py writes qual-report.json in the out-dir, each invocation overwrites it. So the final qual-report.json in summaries/ is from the last invocation = the K11 driver's step... Actually the driver ran K11 main pass, then sfx (separate dir), then rerun-check (which writes qual-report.json again?). The "skipped": true line likely means the rerun-check invocation found summary exists and skipped. And "failures": 2 — probably means... hmm, "failures" count of 2. Ambiguous. This is a real finding: the aggregated per-case roll-up file (qual-report.json) got overwritten so it no longer reflects K02/K19; it now only lists K11 (skipped) with failures=2. That weakens the "多 case 汇总" auditability. Indeed qual-report.json shows only K11 and "failures": 2. Let me check what "failures" means in run_qualification.py. Let me grep.

Also budget-register says "K11 main 19 + K11 sfx 19" requests vs report §1.2/§5 claims. And executed actual ≈347 requests ≈20.4万 in the report vs budget-register "metered_requests_total ... ~= 197 successful requests" and "est_tokens_actual ~= 119k". Big discrepancy! Report says ≈347 请求 ≈20.4 万 est token; budget-register says ≈197 requests, ≈119k est tokens (plus attempt-1 partial ~140 requests un-metered). 197 + 140 = 337 ≈ 347. And 119k + attempt-1 ~? The report's 20.4万 presumably includes attempt-1 estimate (140 requests × 607 = 85k → 119k+85k = 204k = 20.4万). OK so the report conflates metered + estimated attempt-1. The budget-register discloses the composition. But the numbers (347/20.4万) are labeled "实际消耗" in the report while budget-register says only ~197 are metered successes and ~140 of attempt-1 are un-metered (killed). Also the attempt-1 was killed at Run2 ~80/93, so its successful requests are un-metered but real (they did consume provider tokens). So the report's 347 is an estimate. Report §0 AC5 says "实际消耗 ≈ 347 次成功请求 ≈ 20.4 万 est token". Slight overstatement (un-metered attempt-1 included by estimate). It's disclosed in budget-register but not in the report's AC5 row. Worth P4: 口径一致性 (report vs budget-register: 347/20.4万 vs 197/119k + ~140 un-metered).

Let me verify by reading budget-register again: "metered_requests_total": "K02 140 + K11 main 19 + K11 sfx 19 + K11 rerun (see qual-K11.rerun.json) ~= 197 successful requests". Hmm 140+19+19=178, plus K11 rerun 19 = 197. So K11 main=19? But K11 has 13 regions; 19 requests > 13. Hmm, 19 requests for 13 regions. Interesting — so the "1 target region per request" claim: for K11, 19 requests. Maybe Run1 (13) + something (6)? Or retries? Let me check qual-K11.json for translation_metering.

Wait, the K11 driver ran with --meter-translation? Let's check qual-K11.json summary. Let me read qual-K11.json head and its translation_metering section.

Let me grep for "translation_metering" and "n_target_region_calls" in the ko-rerun summaries.
dsh: reasoning:
Key: K11 = 1200×1660 → h/w = 1.383 ≤ 4.0 → tiling NOT triggered → same detect/OCR path as first run. This confirms my analysis and is the explanation the report fails to state.

Now, K11 metering: requests = 19, n_target_region_calls = 19, for 13 regions. Hmm! That contradicts "requests: __2×region__"? For K11: run1 (page-level chain) + run2 (region chain). If Run1 = 13 requests (13 regions) and Run2 = 13 → 26. But metered 19. Hmm. Wait — maybe run1 is page-chain: 13 regions in Run1... Actually the K02 model: Run1 = 93 requests (one per region) + Run2 = 47 successful = 140. For K11: 13 regions; if Run1 = 13 and Run2 = 13 → 26, but metered 19. Discrepancy!

Hold on. Maybe for K11, "details.translated": 11, and run2_region_chain region_runs 13. Perhaps Run1 page chain issues fewer requests because some regions are batched in run1? Or the 19 includes retries? Let me think: 19 = 13 + 6? Or 11 + 8? Hmm.

Actually wait — the K02 estimate "Run1 93 requests" was derived as 140 - 47. Let me check the K02 summary's run1/run2 success counts to verify the 47. Let's grep qual-K02.json for counts of per_region statuses. Actually easier: check the K11 numbers to test the 2× model. For K11: 13 regions, metered 19 requests. If Run1 is one request per BATCH of regions... Hmm, 19 could be: Run1 page chain makes 6 requests (batching by some rule?) + Run2 13 = 19. Or Run1 = 13 + Run2 = 6?

Let me look at the actual data: qual-K11.json run1 steps and run2 per_region with any "requests" info. Let me read more of qual-K11.json (lines 80-250) to see run structure, and check qual-K11.rerun.json metering (also 19).

Actually, another possibility: 19 = 11 translated + 8? Hmm. Let's examine the K11 summary run1 steps for translate counts.

Let me read the run1 steps section of qual-K11.json.
dsh: reasoning:
Let me see the run1 steps' full list count of translate steps, and the region_runs under run1. The run1 steps array contains region-level steps (segment, render, term_extract, translate, ...) — it's a flat list of all regions' steps. Counting translate steps would give the number of translate calls in run1.

Better: let me look at the structural summary of qual-K11.json — search for "run1" region_runs / "translated": and count "step_type": "translate" occurrences. grep can't count easily but returns matches up to 250. Let me grep for '"translate"' in qual-K11.json to count lines.

Actually more efficient: use grep with pattern "\"step_type\": \"translate\"" in the file and count matches. Let me do that.

Also check the metering details around line 1062-1074.
dsh: reasoning:
8 translate steps in run1 (page chain), plus run2 region chain translate steps? The grep found only 8 in the whole file. Hmm, but the metering says 19 requests. So where do 19 come from?

Wait — the run2 region chain steps may be listed in a different key ("region_runs" with per-region steps?). Let me check the structure of qual-K11.json — grep for top-level keys. Let me grep for '^  "' to see top-level keys.

Possibility: run1 has 8 translate steps (some regions didn't need separate translate? e.g., only 8 batches?) and run2 has 11? 8+11 = 19! And details.translated = 11. Hmm, interesting: run2 might have 11 successful translates (11 translated regions) and run1 8. 8+11 = 19. ✓ And the K11 regions: 13 total, 11 with text (2 empty OCR). Run1 page chain would translate all 11 text regions... but grep shows 8 translate steps in run1... unless run2's steps are stored under a separate key that also matches. The grep covered whole file, so total translate steps in the file = 8. But metering = 19.

Hmm, maybe run2 per-region steps are summarized differently (not full step list), so the 8 are run1's and run2's are in "run2" key with counts only. Let me dump the top-level keys.

Let me read the region around line 200-500 chunk boundaries and find where "run2" begins. Let me grep for '"run2"' and '"region_runs"'.
dsh: reasoning:
run1 (lines 76-490) has 8 translate steps? Let's see: translate steps at lines 190,244,382,412,418,442,466,484 → all < 491, so all 8 are in run1. Run2 starts at 649 and has only counts (region_runs_executed 13, status, etc.), no step list. So run1 made 8 translate calls; total metered = 19 → run2 made 11 translate calls. And run2 region_runs_executed=13, with 2 failures (empty OCR regions) → 11 successful translate calls in run2. That matches: 8 + 11 = 19. ✓

So the request structure: Run1 (page chain) issued only 8 translate requests for 11 translatable regions — meaning Run1 IS batched/aggregated at some level! Actually 8 < 11. Hmm, maybe run1's page chain deduplicates or groups regions: e.g., regions with identical source text ("당근아?" repeated) get deduped? Or run1 batches multiple regions per request for some steps.

Wait — for K02, Run1 = 93 requests for 93 regions (inferred). For K11, Run1 = 8 requests for 11 text regions. So Run1 is NOT uniformly one-request-per-region. It seems Run1 (page-level chain) may batch regions but with some grouping (8 groups for 11 regions), or dedupe identical source text.

Hmm! K11 has repeated "당근아?" texts. If dedup applies, 11 regions with distinct texts: 당근아?, 당근아!, 당근아?!, 당근아?!!!, 이렇게까지는..., 어라?..., 크록브록크록..., 오 나의..., 꼬르를 = 9 distinct? Let's count text regions (11): 
1 당근아? (beade011)
2 7860be01 (당근아? merged)
... Actually translate_details has entries. Let me count translate_details (lines 923-1041) entries: probably 11. The run1 step list has 8 translate steps. So run1 batches 11 regions into 8 requests? That would mean some requests carry multiple regions.

Hmm, but the K02 meter says n_target_region_calls == requests == 140, i.e., 1 target region per request. For K02, Run1 = 93 (one per region) + Run2 = 47. That implies Run1 sent 93 separate requests for 93 regions — no batching. But K11's Run1 sent only 8 requests for 11 regions. Contradiction unless... K11's Run1 page chain processes only a subset (e.g., term_extract failures) — hmm.

Wait, maybe I mis-assumed. Let me reconsider: maybe metered 19 = run1 8 + run2 11; for K02, metered 140 = run1 ? + run2 47 → run1 = 93. With 93 regions and 93 requests → 1 per region. But K11: 13 regions, run1 8 requests. Inconsistent! Unless K02's run2 successes were 47 and its run1 = 93 (1:1), while K11's run1 = 8 (batching). Something's off.

Alternatively, maybe for K11 metered 19 = run1 8 + run2 11 where run2 = 11 (translated=11) and run1 = 8. And for K02, the "Run1 = 93" inference from 140-47=93 assumes run2 successes = 47. Is that right? Let's verify from qual-K02.json: run2 region runs = 93, failures 46, successes 47. So run2 translate calls = 47 (assuming each successful region does one translate call). Then run1 = 140-47 = 93. So run1 did 93 translate calls for 93 regions → 1 per region. But K11 run1 did 8 for 11 regions → not 1 per region.

Unless... run1 page chain is per-region but *skips* regions whose OCR text is empty or duplicates? For K11, 8 requests for 11 text regions. Hmm, 11-8 = 3. K11 has 3 duplicate "당근아?" variants? Actually texts: 당근아?, 당근아!, 당근아?!, 당근아?!!!, 이렇게까지는 할 필요..., 어라?..., 고양이 사료...(empty OCR), 크록브록크록..., 오 나의 태야아옹!!, 꼬르를, 당근아? (region 7860be01 merged)... 

The run1 steps list is what it is: 8 translate steps. So run1 = 8 requests.

This is important: it partially contradicts the "KEY FINDING: every request carries exactly ONE target region; Run1 is NOT batched" + "requests ≈ 2 × region_count". For K11: 19 requests for 13 regions → ratio 1.46×, not 2×. For K02: 140 for 93 → 1.51×. Wait! 140/93 = 1.505, not 2×!

Let me recompute. The model says requests ≈ 2 × regions = 186 for K02's 93 regions. But metered = 140 = 1.5×. Because Run2 had 46 failures → 47 successes. So the *intended* full-chain would be 93 + 93 = 186, but only 140 actually sent (46 failed → the failed attempts are not counted by the proxy, since the proxy records only successful translate() calls; the failed calls DID happen but threw). Fine.

For K11: 19 = 8 (run1) + 11 (run2 successes). Expected 2× = 26. Run2 had 2 failures → 11 successes. So 13+11=24 if run1 were 13. But run1 = 8 → 8+11=19.

So for K11, Run1 sent 8 requests for 13 regions — that means Run1 DID something different: fewer requests than regions. This is counter-evidence to the "requests ≈ 2 × region_count" model and to "Run1 也逐 region 非整页批量". Actually maybe Run1 batches regions into groups of ~1.6. Hmm.

Hmm, but hold on: could it be that run1's translate step list only includes "completed" steps and some region steps are missing from the list? The steps list for run1 has 8 translate + other step types. Let me count all step entries for run1 and compare with 13 regions × ~7 steps. Let me look at the whole run1 steps count. Let me grep for '"step_type"' count in the file.

Let me get precise: grep all `"step_type":` lines in qual-K11.json and count.

Actually the previous grep with pattern `"step_type": "translate"` returned 8 matches (capped at 250, so complete). So there are exactly 8 translate steps in the file. If run1's page chain only stores one step per region for translate, then run1 translated 8 regions. But translate_details has 11 entries with final_translation non-empty (machine) — those come from DB aggregate over both runs.

So Run1 page chain translated only 8 of 11 text regions? That seems odd but possible if run1's page-level chain batches regions per "segment/render group"? Hmm.

Wait, maybe run1's page chain translates at the *page* level in batches of regions and the steps recorded are per-batch. E.g., 11 regions → 8 requests means some requests carried 2-3 regions. But then n_target_region_calls would be 19 = sum over requests... no: n_target_region_calls == 19 == requests, meaning each request carried exactly 1 target region. So run1 made 8 requests each with exactly 1 target region → run1 translated exactly 8 regions.

So which 8? Probably the regions that needed term_extract+translate in run1... Hmm, why 8 not 11? Possibly because run1 processes only regions whose OCR text is non-empty AND unique? Or because 3 regions were deferred to run2 (e.g., region-level chain handles them)?

Hmm, actually maybe run1's page chain and run2's region chain split work: run1 does the page-level pipeline (which may translate a subset — e.g. those with detected bubbles), and run2 processes each region independently.

Either way, the empirical claim in the report "Run1 亦逐 region 发请求，非整页批量 → 请求数 ≈2×region 数" is NOT supported uniformly: for K02 (the pilot), 93+47=140 happens to equal 93+47 both being "region counts", but for K11 we observe 8+11=19 for 13 regions — i.e., Run1 made FEWER requests than regions, and total ratio 1.46.

Hmm wait. Actually let me reconsider K02: maybe Run1 also made fewer than 93 requests and Run2 made more. E.g., Run1 = 8-ish? No: 140 - 47 = 93 exactly. Coincidence? For K02 the run2 successes = 47. Let me verify from qual-K02.json: grep for region_runs_executed in run2 and count failures. Let me check.

If run2 successes were actually 140 - X... I need the actual run2 success count. Let me grep qual-K02.json for '"region_runs_executed"', '"failed"', and count per_region statuses.

Actually the report says Run2 46 region 失败. If run2 region_runs_executed = 93 and 46 failed → 47 succeeded → run1 = 93. Then Run1 = 93 = region count. But K11's Run1 = 8 ≠ 13. Contradiction stands. Unless K02's run1 metered requests ≠ 93.

Alternative explanation: maybe for K11, run1 made 13 requests but 5 of them... no, proxy records each successful translate() call; failures propagate as exceptions (not recorded). So run1 could have had 13 attempts with 5 failures → 8 recorded. Does K11 hang have run1 failures? The summary says run1=completed_with_failures with attribution "defect:run1-PipelineRunStatus.COMPLETED_WITH_FAILURES". And the report says K11's 2 empty-OCR regions failed term_extract. If run1 had 13 translate attempts with 5 failures, the number of translate *steps* recorded as completed would be ≤8 (failed steps recorded with error status). But grep found exactly 8 `"step_type": "translate"` lines total — if failed steps were recorded with step_type translate and status failed, they'd still match. So run1 truly invoked translate 8 times (as recorded).

Hmm, unless failed steps omit "step_type"? Unlikely.

OK. There is a genuine internal inconsistency that undermines the cost model and the N4 "important finding". Let me gather more data:
- qual-K02.json: run2 region_runs_executed and failure count; run1 steps translate count.
- qual-K11.rerun.json: metering 19 as well.

Let me grep qual-K02.json for step_type translate count and region_runs.

This is a significant finding (P2) if confirmed: the cost model's core multiplier (requests ≈ 2× regions) is inferred from a single case where the two runs coincidentally matched region count, while K11's metered data shows 19 requests for 13 regions (1.46×) with Run1 making only 8 requests. That affects the 50万外推 (63.2万 ≈ 521 regions × 2 × 607). If the real ratio is ~1.5×, extrapolation = 521×1.5×607 ≈ 474k — below the 500k line for known-only! That's material to the stop decision! Let me compute: using K02's observed ratio 140/93 = 1.505: 521 regions × 1.505 × 607 = 475,900 ≈ 47.6万 < 50万. Using K11's 19/13 = 1.46: 521×1.46×607 = 461,800. So the stop decision's "known five pages already 63.2万" hinges on the 2× model. If the observed full-chain per-region multiplier is ~1.5× (because Run1 batches/deferred some regions, or because some regions' translate is skipped), known-only would be ~46-48万 — just under the 500k line. That makes the stop decision sensitive/arguable.

Hmm, but careful: the "2×" model intends to represent a *complete* run where all 93 regions are translated in both runs (Run1 sweep + Run2 sweep). K02's 140 was depressed because 46 Run2 requests failed. So the intended full-run count is 186 for K02 → 2×. For K11, if all 13 regions succeeded in both runs, would it be 26? But observed run1=8, run2=11 (successes) with 2 run2 failures → intended = 8+X... we don't know how many run1 attempts failed. If run1 is "one request per translatable region", and K11 has 11 translatable regions, run1 should be 11, not 8. So 3 run1 translate calls are missing — either skipped or failed. But the summary records run1 as completed_with_failures with the 2 empty-OCR term_extract failures. Hmm, but wait, those 2 empty OCR regions are in run1's page chain too. If the page chain's translate step for those regions is skipped (because OCR empty → no source text), then 11 translate calls = 11 text regions... but observed 8.

Let me actually look at run1's step list more carefully. Maybe the steps list is grouped: each "step" entry might correspond to a batch of regions at the page level. Total steps in run1? Let me count all step_type entries and their distribution.

Let me read lines 200-491 to see everything.

Actually, an important alternative: maybe run1's translate steps are recorded per *batch* and each batch has "n_target_regions" > 1... but the meter says n_target_region_calls == requests == 19, so each request had exactly 1 region. So run1 made 8 single-region translate requests.

Hmm, unless run1's 8 translate steps correspond to only 8 regions because 3 regions' step records were... Let me look at the region list (lines 491-649, "regions": [...]) which has per-region info like source_text/translated_text/final_source — 13 entries presumably. And translate_details (923-1041) has 11 entries. 

Let me check whether the K11 page chain is "run1_page_selection" mode where only *some* regions are picked (a selection!): note stage name "run1_page_selection" — maybe run1 processes a *selection* of regions (e.g., a subset chosen for the page-level pass), while run2 processes all 13 region runs. That would explain 8 < 11: the page selection pass selected 8 regions?? Hmm, "region_runs": 13 in run2.

I should check the first-run K11 summary in phase2/summaries/qual-K11.json (first run) to compare — the first run had run1=completed. If first run's run1 also had 8 translate steps, then it's a stable structural behavior, and the K02-vs-K11 difference needs explaining.

Let me grep the first-run qual-K11.json for translate step count and metering (first run had no metering).

Let me do several greps/reads in parallel:
1. grep first-run phase2/summaries/qual-K11.json for `"step_type": "translate"`
2. grep ko-rerun/summaries/qual-K02.json for `"region_runs_executed"`, `"step_type": "translate"` (count), and run2 failure info.
3. read qual-K19.json.
dsh: reasoning:
For K02: run1 steps (lines up to ~5676) contain many translate steps. Run2 (after 5676) contains 47 translate steps (5676→9319). Let me count: run2 translate steps listed from 5821 to 7316... the grep returned 141 matches, likely capped at 250 so complete? It says "Found 141 matches" (under 250, so complete). Total translate step entries in K02 = 141? Hmm, that's less than 93+93=186 and more than 140.

Hmm. Wait, translate step entries may include both "translate" and other. 141 entries with step_type translate. Metered = 140 successful. Interesting: 141 ≈ 140 + 1 failed! The 1 INVALID_OUTPUT failure would be recorded as a step (failed) → so 93 run1 + 47 success run2 + 1 failed run2 = 141. YES! That fits: run1 = 93 translate steps? Let's see: run2 region runs = 93, with 45 timeouts + 1 invalid output = 46 failures, 47 successes. If the 45 timeouts did NOT record a translate step (maybe the step record is only created on completion?), but the INVALID_OUTPUT recorded one... Hmm, 141 = 93 + 47 + 1 = 141. ✓ So run1 = 93 translate steps → run1 = 93 requests (1 per region). And run2 steps = 48 (47 success + 1 invalid_output recorded as translate step). That matches the meter: 140 successful = 93 + 47. ✓✓

So Run1 for K02 = 93 requests for 93 regions → 1 per region. Confirmed.

Now for K11: run1 has 8 translate steps (from my earlier grep of ko-rerun qual-K11.json: 8 matches at lines 190,244,382,412,418,442,466,484, all < 491 where run1 ends). And run2 = 11 successes (translated 11). Total metered = 19. But wait: 8 + 11 = 19 ✓. But why does run1 have only 8 translate steps for 13 regions (11 with text)?

And the FIRST-run K11 (phase2/summaries/qual-K11.json): grep for translate step returned only line 87 for `"step_type": "translate"`?? The grep pattern combined several alternatives; it found:
- line 60: region_runs 13
- line 87: step_type translate
- line 298: region_runs_executed 13
- lines 355, 389: status failed

So the first-run K11 summary has only ONE translate step in run1?! Hmm, that suggests the first-run and this-run summaries have different step recording. Hmm, that's weird. Unless the first-run's run1 steps list is much shorter (maybe deduplicated/stored differently).

Wait — maybe the grep result is truncated? It said "Found 5 matches" for 3 alternatives — hmm, only 5 matches total, meaning only one `"step_type": "translate"` in the first-run K11 summary. Odd.

Hmm, maybe the first-run K11 summary structure differs: maybe run1 steps are in a different key or the file was written by an older runner version. Also lines 355 & 389 "status": "failed" — probably in run2's per-region list.

Hmm, so the first-run K11 run1 had 1 translate step recorded?? Let me read the first-run K11 summary to understand. This matters for the N3 comparison (run1 status completed → completed_with_failures).

Let me read the first-run qual-K11.json fully (it's probably ~450 lines).
dsh: reasoning:
First-run K11 run1 steps = 9 steps, generic (one per step type) — this is the *page-level* run1: one request per step type, not per region! So the first run's run1 recorded a short generic step list (9 steps: mask_refine, translate, render, inpaint, detect, color, segment, term_extract, ocr) — that's a page-level chain, exactly ONE translate step for the whole page. Hmm! So run1 makes ONE translate call for the page? But run1's translate step is a page-level step that internally translates the page (probably all regions in one request? or the page-level pipeline does region-by-region internally producing multiple HTTP requests but records one step).

Now the rerun K11 run1 steps = 8 translate steps among many (I saw steps at lines 80-199 with repeated step types: segment×3, render, mask_refine, term_extract, render, term_extract, term_extract, render, render, segment, inpaint, detect, color×4, translate, term_extract, ...). So the RERUN's run1 step list is *region-level* (many steps), whereas the FIRST run's run1 step list was *page-level* (9 steps). This is a structural difference between the two summary generations!

Hmm, wait. That could be the "PRIMARY-SFX-GATE terminal accounting unified semantics" change: run1 now records per-region steps. If so, the N3 explanation ("空 OCR 失败计入 Run1 终态") is about the same change. Actually more precisely, the first run's run1 recorded only 9 page-level steps and status=completed; the rerun records per-region steps for run1 → failures visible → completed_with_failures. That is a much bigger structural change than just "counting" — but consistent with "terminal accounting unified".

Hmm, but careful: maybe the first-run summary was written by an older run_qualification.py whose run1 step aggregation was coarser. But the claim is that src changed (PRIMARY task) not the runner. The runner's run1 step extraction may read run steps from DB; the DB step recording may have changed in src (PRIMARY). Fine.

So K11's rerun run1 step list has 8 translate steps for 13 regions. If run1's step list is now per-region, then 8 translate steps = 8 regions translated in run1. But 11 regions have text. So 3 regions' run1 translate steps are missing? Possibly the run1 region-level chain skips regions whose source text is empty or duplicate — or those 3 steps are recorded with a different step_type, or grouped.

Hmm, let me count all steps in K11 rerun run1 and see the region association. Let me check whether the rerun K11 steps have "region_id" fields. Let me read lines 200-491 of the rerun K11 summary.

Actually, maybe I'm overinvesting. Let me check the K02 run1 step count relative to 93 regions: run1 for K02 had 93 translate steps (141 - 48). Let me verify run1's step list for K02 contains 93 translate steps: from grep, lines 125..4547 are < 5676 (run2 start) — count of matches before 5676: the list from 125 to 4547 — let me count: I count the entries in the grep output before "5676": that's lines 125,155,233,263,275,365,467,575,581,605,641,701,755,803,851,959,1007,1037,1193,1205,1241,1265,1361,1385,1391,1421,1433,1457,1475,1565,1595,1619,1655,1661,1757,1823,1871,1901,1913,1937,1943,1949,2015,2033,2261,2321,2333,2375,2381,2435,2495,2603,2621,2645,2771,2801,2873,2903,2909,2921,3041,3155,3167,3179,3251,3263,3359,3371,3443,3533,3563,3695,3743,3767,3785,3845,3953,3983,4025,4085,4217,4223,4247,4271,4319,4325,4343,4397,4463,4469,4475,4523,4547 = let me count in groups... This is ~91-93. Likely 93. OK consistent with run1 = 93 translate steps = 93 requests.

So for K02, run1 = per-region (93 steps, 93 requests). For K11, run1 = per-region steps but only 8 translate steps. So why 8?

Let me look at K11 rerun run1 steps in detail — read lines 76-491.
dsh: reasoning:
The rerun K11 run1 steps list is a *global* list (all runs?) — wait, this run1.steps list has ~60+ entries with mixed step types, including one FAILED term_extract with "region has no OCR text". Hmm, and 8 translate entries. It appears run1's step list is the flat list of all steps across regions for the page-level run. Since K11 has 13 regions and each region has ~7 steps, ~90 steps total; here I count roughly: lines 81-487 → about 66 entries. Hmm.

Actually the important thing: run1 has 8 translate steps while run2's 13 region runs produced 11 successful translates. The metering 19 = 8 + 11.

Hmm, but for K02, run1 = 93 translate steps and metering run1 = 93. So run1 records one translate step per region request. For K11, run1 = 8 translate steps → only 8 regions translated in run1? But 11 regions have text.

Wait... maybe not. In K02, 93 regions and 93 translate steps. In K11, 13 regions and 8 translate steps. Difference: K11 has 2 empty-OCR regions (which fail term_extract → never translate). So 11 translatable regions → expect 11 translate steps. Observed 8. So 3 missing.

Unless the run1 step list is capped/sampled. Hmm, K02's run1 translate steps = 93 exactly, so no cap.

Alternatively — and this is likely — the K11 rerun run1 step list might only contain steps from a *subset* of regions because the run1 page chain deduplicates identical region texts at the HTTP level: K11 has "당근아?" repeated 3-4 times. If the pipeline caches identical source text translations, duplicate regions would reuse the cached translation → no new HTTP request → maybe no separate step record either. In K02, texts are mostly distinct → 93 requests. In the first-run K11, run1 recorded only ONE translate step (page-level aggregated) so we can't compare.

Hmm, so the "KEY FINDING: every request carries exactly ONE target region (Run1 is NOT batched at HTTP level) - so full-chain request count ~= 2 x region_count" is contradicted by K11: run1 emitted 8 requests for 11 translatable regions (fewer than region count), and total = 19 for 13 regions = 1.46×. So the model's factor 2 is an upper bound only if both sweeps translate every region; the observed K02 140/93 = 1.51× and K11 19/13 = 1.46× suggest the actual multiplier is ~1.5×, not 2×.

Hmm wait. But hold on. For K02: Run1 = 93 requests (per-region, from steps) and Run2 = 47 successes + 46 failures. If we had a clean run, Run2 would be 93 → total 186 = 2.0×. So the 2× model assumes Run2 completes all regions. For K11 clean: Run1 = 8 (?? but should be 11), Run2 = 13 → 21 = 1.6×. Hmm, with 2 failures, run2 = 11 → 19 = 1.46×.

The question is whether Run1 translates every text region. In K02 it did (93 = all regions, including presumably none empty). In K11, run1 = 8 translate steps for 11 text regions — that's an inconsistency the Owner didn't notice/report. Actually wait, maybe I should double check by counting the rerun K11 run1 steps and translate steps again: grep found 8 translate step entries in the entire file; run1 spans lines 76-490. All 8 are within that range (190,244,382,412,418,442,466,484). And run2 section (649-764) has no step list (only aggregate). So yes 8.

Hmm, but is run1's steps list possibly truncated because the runner reads only the last N steps? K02's run1 had 93 translate + others (~600 steps). K11's run1 has ~66 entries. Hmm, K11 has 13 regions; if each region contributes ~5-9 steps, total would be 65-117. Actually the list I saw has: 3 segment, 1 render, 1 mask_refine, 1 term_extract, 1 render, 2 term_extract, 3 render, 1 segment, 1 inpaint, 1 detect, 4 color, 1 translate, 1 term_extract, 1 ocr×3... Let me just count the total number of step entries in run1 for K11: lines 80-489 → each entry is 6 lines (brace, step_type, status, error_code, error_detail, close brace) = 6 lines → (489-80)/6 ≈ 68 entries. With 13 regions, that's ~5.2 steps/region — plausible if the run1 chain records ~5 steps per region but only for regions that advance to certain stages. The 2 empty-OCR regions contribute term_extract failures.

Hmm, so run1's step list IS per-region for K11. Then only 8 regions got a translate step. But 11 regions have translations in translate_details (final_source machine). And the metered run1 = 8.

Wait... maybe not all 11 translations came from run1 — run2 also translates (11 successful in run2). So run1 may have translated 8 and run2 translated 11; the union covers all.

Hmm, but why would run1 skip 3 text regions? Possibly because run1's page chain only translates regions that were "selected" under a page-level selection policy (stage named "run1_page_selection"!). The stage is literally called "run1_page_selection" → run1 performs a *selection*. Maybe the selection for the page-level pass picks regions by some rule (e.g., excludes duplicate-text regions, or only up to a batch size). In K11, 8 vs 11 could be dedup of 3 duplicate-ish texts ("당근아?" ×3 duplicates + ...). Hmm, K11 has 당근아? (ro1), 당근아? (ro3 in similarity list), 당근아! (ro2), 당근아! (ro8), 당근아?! (ro4), 당근아?!!! (ro6). In the regions list from similarity JSON: source texts include 당근아? ×2, 당근아! ×2 → duplicates = maybe 2-3 dedup. 

Anyway: I cannot fully resolve the mechanism statically, but I have solid evidence that:
(a) The claim "Run1 也逐 region 非整页批量，请求数≈2×region 数" is NOT supported as a general structural law: K11 metered 19 requests for 13 regions (1.46×), Run1 = 8 requests for 13 regions/11 text regions.
(b) The report never cross-checks the model against K11 (which was metered too, in the same run) — a missed validation.
(c) The stop decision's headline number (63.2万 for known pages) depends on the 2× factor. With K02's observed total ratio (140/93 = 1.505) the known-only extrapolation = 521×1.505×607 ≈ 47.6万 < 50万 → below the line. So the stop trigger is sensitive to the factor choice, and the report presents the 2× factor as measured ("实测结构") without disclosing this sensitivity.

Hmm, careful: is 1.505 the right "full-chain" ratio for a *complete* run? K02's 140 excludes 46 failed run2 attempts, and the failed attempts were real HTTP requests (which would count in a clean run). A clean K02 = 93 + 93 = 186 = 2×. So for a *clean* run the 2× is right, provided Run1 covers every region. K11's run1=8 (not 11/13) suggests Run1 does NOT cover every region (dedup?) — so the clean-run ratio might be < 2×. For K11 clean: 8 + 13 = 21 = 1.6×.

Hmm, so the 2× model may overestimate by ~25%. On the known 521 regions: 2× → 63.2万; 1.6× → 50.6万; 1.5× → 47.4万. So around the line! This is a material uncertainty for the stop decision, and the report did not flag it. Even so, the report also flags the range 107万-209万 including K07/K09/K10 — but those density estimates (120-400 regions/page) are the dominant uncertainty.

Actually wait, even at 1.5×, K07/K09/K10 included: 881×1.5×607=802k > 500k. So the stop ruling stands under either factor for the full set; only the "known five pages alone already exceed" claim is factor-sensitive (63.2万 vs ~47万). The report's headline says "仅 TILING 已确认五页就超红线" — this specific claim is fragile. That's a good, concrete finding (P2/P3).

Let me double check the 2× factor claim's derivation in the report: "请求数模型 | ≈ 2 × region 数（Run1 一轮 + Run2 一轮，§1.1 实测结构）". Yes it claims §1.1 实测 supports 2×, but §1.1's 140 = 93+47 includes 46 failures, so 140/93=1.5, not 2. The report does NOT compute 2× from measurement — it assumes a hypothetical clean run. The budget-register says "KEY FINDING ... full-chain request count ~= 2 x region_count (one Run1 sweep + one Run2 sweep)" — presented as measured. This is an overstatement of measured support: Run1 sweep per-region is measured for K02 (93 steps), but Run2's sweep was truncated by the outage; and K11's metered run1=8 shows the sweep is not always region-complete.

Hmm, but I should be careful: maybe run1 for K11 DID make 11 requests and the metering proxy recorded only 8 because of... no, the proxy records each successful translate() call. Hmm, unless run1's translate for some regions went through a different code path (e.g., cached/deduplicated by the pipeline at the *pipeline* level, not HTTP). If the pipeline dedups identical source text, then no HTTP request is made for duplicates → not metered. That's consistent with "every request carries exactly 1 target region" while the *number of requests* < regions. And that means the cost model should be "≈2×distinct-source regions", not "2×regions".

So finding: the "requests ≈ 2× region 数" model ignores text-level dedup/skip effects visible in K11 (8 run1 requests for 11 text regions); the report should either explain the K11 run1=8 anomaly or downgrade the model to an upper-bound assumption. This is a legitimate P2 (affects a stop decision headline) — well, P2 or P3. Given the stop decision is the core deliverable and the line is a cost discipline, I'd rate it P2: "停跑判定的核心乘数未经交叉验证/存在反例".

Let me now verify the K02 run1 = 93 translate steps more rigorously by counting matches before line 5676. Let me instead grep with a pattern and count via reading. Alternatively, check if qual-K02.json run1 has "translate": count fields. Hmm, the K02 summary structure: does it have run1.steps with per-region? 93 translate steps. And run2 region runs 93 with per_region statuses. The report's claim that Run2 failed 46 → 47 success. Let me verify the run2 failure breakdown: 45 PROVIDER_TIMEOUT + 1 INVALID_OUTPUT = 46. Let me grep qual-K02.json for error_code counts.

Rather than deep-diving, I have enough for the finding. But let me verify the count of "PROVIDER_TIMEOUT" in qual-K02.json to confirm 45.

Also I need to check: pipeline_failures field in qual-K02.json (task says Gate = pipeline_failures=0).

Let me also check the K19 summary and the sfx summary's key fields (sfx_policy translate evidence).

And the run_qualification.py baseline: confirm `reregister_env_resolver` original to compare with the metered variant (behavior zero change). Let me read the original function from the worktree file.

Let me batch:
1. grep qual-K02.json for PROVIDER_TIMEOUT count.
2. read run_qualification.py around reregister_env_resolver (original).
3. read qual-K19.json fully.
4. grep summaries-sfx/qual-K11.sfx-translate.json for sfx_policy/relevant fields.
dsh: reasoning:
qual-K02.json: 45 PROVIDER_TIMEOUT + 1 PROVIDER_INVALID_OUTPUT = 46 ✓ matches report.

K19: confirmed F4 (run1 completed_with_failures, detect EMPTY, run2 SKIPPED) ✓.

Now note the K19 report claim: "K19 无字页 step=failed vs 文档豁免口径" — F4. Fine.

Now important structural check: K19's run1.steps has only the detect step; K02's run1.steps has 93 translate steps; K11's run1 has 8 translate steps. So run1.steps recording differs per case — for K02, per-region steps; for K19 a single page-level step. Hmm, that's the same runner version. So why the difference?

Ah — I think I understand now: run1.steps = the steps of the page-level pipeline run, which for a page with regions includes per-region sub-steps (each region processed as a step) — for K02 that's 93 translate steps because 93 regions each got a translate step. For K11, 8 translate steps because only 8 regions got a translate step in run1 (the others were deduped/skipped). For K19, 0 regions → only detect fails.

So the K11 run1 = 8 requests really means 8 translate steps. Hmm, but is the K11 run1 = 8 because 3 text regions were already translated in... no, it's a fresh DB per case. 

Alternatively 8 = number of *distinct* source texts among the 11 text regions? Let's count K11 text regions from translate_details: I saw entries; let me count distinct source texts: 당근아?(1), 당근아!(2), 당근아?!(3), 당근아?!!!(4), 이렇게까지는...(5), 어라? 침대...(6), 크록브록크록...(7), 오 나의 태야아옹!!(8), 꼬르를(9), and one more entry — the merged one (7860be01 "당근아! 당근아?"). That's 10 distinct? Hmm, translate_details has 11 entries (translated=11). If dedup by distinct source text: 당근아? appears twice (ro1 and ro3? in region list) and 당근아! appears twice (ro2, ro8) → 11 - 2 = 9 distinct. Hmm, 8 ≠ 9 but close.

This is speculation. What I can state factually:
- The metering for K11 shows 19 requests / 19 target-region calls for a 13-region page, of which run1 contributed 8 (8 translate steps in run1.steps) — i.e., run1 issued FEWER translate requests than there are text regions (11).
- Therefore the generalized model "requests ≈ 2 × region_count" is not uniformly supported by the measured data in this same run; it holds only if both sweeps translate every region. K02 alone (which had 93 regions all translated in run1) is the basis.
- The report presents it as "实测结构" without noting the K11 counterexample/shortfall.
- Consequence: the headline "known five pages alone already exceed 500k" depends on the 2× multiplier; under K02's observed 1.5× the known-only estimate is ~47.6万 < 50万 (assuming K11's shortfall pattern doesn't generalize).

Actually careful: for K02 the 1.5× is depressed by failures. The honest "upper bound" is 2× (clean run). So using 2× is a conservative (safe) choice for a stop line — that's defensible. The finding should be framed as: the 2× multiplier is a conservative upper bound, not a measurement; the report labels it "实测结构" (§1.2 表) which overstates support; and the "known five pages alone exceed" claim is multiplier-sensitive (1.5×→~47.6万, below). Recommend relabeling as upper-bound assumption + sensitivity note. That's a fair P3 (documentation/precision) rather than a P2 defect, since conservative direction is safe for a stop decision. But it interacts with the *minimal-set* choice: K11 was run *after* the stop decision and it independently contradicts... no, it doesn't contradict the stop (K11 is cheap).

Hmm, one more consideration: is the 2× model even the right shape? The report says Run1 (page selection) + Run2 (region chain). But from the task doc AC1: "断点续跑语义沿用；region 策略默认无截断" — the production runner runs run1 (page) then run2 (region) as two sweeps by design. So 2× is structurally intended. OK, P3.

Now: the biggest issue for review item 1 — 50万红线 not in the task doc. Let me verify there's no other source. Let me check doc/STATUS.md for the user 裁决③ text and any mention of budget discipline. Let me grep in doc/ for "裁决" + "token" or "停".

Let me grep doc/ for "预算" and "token".
dsh: reasoning:
Very useful: the first-path M2-TA3-B2 DSH r1 review said: "成本：... Task 纪律是「预估 ≤ 数万 token 量级，超预期即停并登记」". So the *original* TA3-B2 task discipline was "预估 ≤ 数万 token 量级，超预期即停并登记" — and phase2-plan.md:192 was changed to "数十万以内" (which r1 flagged as an unregistered widening, R10/N6).

So the "50万" line: where does it come from? It's not in the M2-TA3-B2-KO-RERUN task doc, and the upstream discipline was "数万 token 量级". Let me check verification/M2-TA3-B/phase2-plan.md around line 192 in this worktree to see the current text (it's in scope? phase2-plan.md is under verification/M2-TA3-B/, which is in the allowed面 but the diff shows no change to phase2-plan.md in this rerun).

Let me read phase2-plan.md around line 185-200.

This is a crucial finding for review item 1: 50万红线既非本 Task 书原文，也与上游 TA3-B2 纪律「≤数万 token 量级」不一致（phase2-plan 的「数十万以内」曾被 DSH r1 判为未登记的口径放宽）。So the stop line's provenance needs to be established (likely from the user 裁决③ or the orchestration session's brief). The reviewer should demand provenance.

Let me read phase2-plan.md:180-200 and also check the quality-report.md §10 (new) content, and the first-run quality-report.md F1-F6 sections. Also read the CALIB 局限 8 doc, and the PRIMARY-SFX-GATE handoff for terminal accounting claims.

Let me batch:
1. read verification/M2-TA3-B/phase2-plan.md offset 180 limit 25
2. grep verification/M2-QUAL-DETERM-CALIB for 局限 (limitation 8)
3. read diff section for quality-report.md (line 15473+) — the §10 addition.
4. grep doc/handoffs or verification for M2-TASKS-PRIMARY-SFX-GATE terminal accounting.
dsh: reasoning:
Excellent. This is a decisive finding:

phase2-plan.md:192 (upstream, still current in this worktree, unchanged by this Task): the project's documented cost discipline is "预估总 token **数万 token 量级，超预期即停并登记**" — and the r2 N6 note explicitly records that writing "数十万以内" was an out-of-scope widening that was rolled back. Now this rerun introduces a "50 万 est token 红线" attributed to "任务纪律" / "task brief", but:
- M2-TA3-B2-KO-RERUN.md 纪律节 has NO 50万 number (only "翻译预算控制…预估请求数/先行一个 case 试算后再全量").
- The upstream documented discipline is "≤数万 token 量级，超预期即停并登记" — a 50万 line is ~50× higher than "数万" and is exactly the kind of unregistered widening that r1 R10/r2 N6 already flagged once.
So the 50万 line's provenance is unestablished in the repo. The stop decision itself (stop and register) is comfortably compliant with any version of the discipline (it stopped *earlier*, not later) — so no harm done; but the report must cite where 50万 came from (user 裁决③ brief? orchestration instruction not in repo?). This is a P2 documentation finding: 红线出处未落地为书面依据，且与仓库内既有纪律文字冲突；建议把用户裁决/编排指令原文落盘或以「数万 token」纪律为准重新表述。

Actually, since the stop was conservative, the direction of the discrepancy favors safety: they stopped at a much stricter trigger. So it's a provenance/documentation issue (P2 or P3). I'd call P2 because the task's central decision rests on an unverifiable rule — and a reviewer must not accept "任务纪律" as authority without a citation. But is it harmful? If 50万 was actually the orchestration session's instruction to the Owner (likely, given the review brief says "成本纪律=est token 外推 >50 万即停等裁决" as 背景（用户裁决③+任务纪律）), then the rule exists in the human brief but not in the repo. The handoff should record the source. I'll make it P2: 红线出处未在仓库内可核（与 phase2-plan.md:192 「≤数万 token 量级」冲突），需登记用户/编排指令原文或改口径。

Now let me check the CALIB limitation 8 doc and the PRIMARY-SFX-GATE terminal accounting claim.

Let me grep CALIB dir for 局限 8.
dsh: reasoning:
CALIB 局限 8 confirmed: exactly predicts "语义等价的合法重译会被判低相似度 FAIL" and "属后续独立工作、此处仅登记". So the Owner's attribution is faithful to the CALIB text. Good — item 4 partially verified. But: the Owner's *determination* that the specific pair is 语义等价合法重译 is a judgment — CALIB 局限 8 describes the direction, not this pair. The report says "该浮动对是语义等价的合法重译（同义改写，非字符噪声、非漏译）" with no recorded judgment basis/annotator. That's the P3 finding I identified. Note the pair: source "이렇게까지는 할필요없을줄 알았는데" → "没想到会做到这种地步" vs "我本以为没必要做到这种地步". Both are valid renderings; the second is arguably slightly different in nuance but semantically equivalent enough. Reasonable. Still needs a documented basis (e.g., "Owner 审阅两版本，逐句对照源文；判定为同义改写" + which human).

Now, PRIMARY-SFX-GATE: the N3 claim is that run1 completed→completed_with_failures is due to the PRIMARY task's "terminal accounting unified" semantics. I need to verify that M2-TASKS-PRIMARY-SFX-GATE actually changed the terminal accounting so that empty-OCR term_extract failures count in Run1's terminal state. Let me find the PRIMARY task artifacts. Let me search doc/tasks and verification for M2-TASKS-PRIMARY-SFX-GATE.

Also verify the sfx settings key `settings["sfx"]["policy"]` semantics and `decide_sfx_translation`.

Let me glob/grep.
dsh: reasoning:
Note: `src/infrastructure/sqlite/schema.py:231` CHECK constraint: `sfx_policy IN ('skip', 'translate', 'manual')`. The runner's `--sfx-policy` choices are ["", "skip", "manual", "translate"] — consistent ✓.

Also core_assembly.py:697-731 `_sfx_policy_from_settings` reads settings["sfx"]["policy"], with fail-fast on invalid values. And :869-880 comment: "the sfx_policy applied at region creation is a persisted pipeline-settings key". Good — the runner's approach (save_settings_section then re-assemble) matches the production sequence.

Now, the N3 claim about terminal accounting: `application/tasks/service.py:1054` sets run.status = COMPLETED_WITH_FAILURES; `projection.py:336` checks `if status is COMPLETED_WITH_FAILURES and has_failures`. Hmm, that's a projection function that may *downgrade* to COMPLETED when no failures. Let me look at PRIMARY-SFX-GATE task/handoff to see the "terminal accounting unified" claim.

Let me read doc/tasks/M2-TASKS-PRIMARY-SFX-GATE.md and the handoff.
dsh: reasoning:
PRIMARY-SFX-GATE = "primary region 也走 live region 重决策". Its AC2 mentions "terminal 账目断言保持（primary 重决策后 terminal==planned==17、progress==1.0，primary 的 SKIP unit 同口径计入）".

Now the N3 claim in the rerun: "run1 状态 completed→completed_with_failures ... PRIMARY Task 的 terminal accounting unified 语义". Does PRIMARY-SFX-GATE change run1's terminal accounting for empty-OCR term_extract failures? The PRIMARY task's change: primary region now goes through `_plan_region` live region re-decision. That changes *which units are planned/executed* for the primary region — e.g., if the primary region is an SFX region with policy skip, its translate unit becomes SKIP (not executed) — "primary 的 SKIP unit 同口径计入". So the terminal accounting for the primary region changed from "page-level plan" to "live region re-decision".

For K11: run1 status differs. How does PRIMARY's change turn run1 from completed → completed_with_failures? Hmm. Not obviously. The rerun's report claims the empty-OCR region's term_extract failure is now *counted* in Run1's terminal state. But which K11 region is the *primary* (region_ids[0], reading_order=1)? For K11 run1, region order... The 7860be01 merged region? Hmm.

Wait, there's also M2-TASKS-BACKFILL-MULTIREGION (the earlier task) that changed fan-out to `_plan_region` for region_ids[1:]. Its DSH r1 R1: "terminal 账目修+断言红态 terminal 12≠17". So BACKFILL changed terminal accounting. So the K11 run1 status change (completed → completed_with_failures) is attributable to BACKFILL (already merged before the first run? No—the first run was before BACKFILL/PRIMARY were integrated) or PRIMARY.

Timeline: first run M2-TA3-B2 @ f99a6c55 (before TILING/ALLOC/BACKFILL/PRIMARY/SFX-ENTRY were integrated). The rerun is at 87f61d8b (after all). So multiple semantic changes could account for the run1 status difference. The report attributes it specifically to "PRIMARY Task 的 terminal accounting unified 语义" — a single-cause attribution without isolating which of the intervening changes (BACKFILL fan-out, SFX-ENTRY policy, PRIMARY) produced it. The reviewer item C asks whether this attribution correctly matches PRIMARY-SFX-GATE's implementation behavior.

Key point: PRIMARY-SFX-GATE's stated purpose is making primary region go through live region re-decision (SFX gate 全域生效). BACKFILL-MULTIREGION's stated purpose was region fan-out = `_plan_region` semantics with terminal accounting fix (R1: "terminal 账目修+断言红态 terminal 12≠17"). So the K11 run1 terminal-state change is much more likely attributable to BACKFILL's terminal accounting (or to BACKFILL+PRIMARY jointly) than to "terminal accounting unified" being introduced by PRIMARY.

Both tasks are named "M2-TASKS-BACKFILL-MULTIREGION" and "M2-TASKS-PRIMARY-SFX-GATE", and the report's Task doc dependency list includes both? The task's depends_on = [M2-TA3-B2, M2-DETECT-WEBTOON-TILING, M2-IMPORT-ALLOC-LIMIT, M2-TASKS-PRIMARY-SFX-GATE]. Note: M2-TASKS-BACKFILL-MULTIREGION is NOT in depends_on (but PRIMARY depends on BACKFILL, so transitively included).

The finding: N3's attribution names "PRIMARY task 的 terminal accounting unified 语义" but PRIMARY's change surface (primary region 重决策 via `_plan_region`) does not by itself read as "空 OCR 失败计入 Run1 终态"; the terminal accounting unification is documented in BACKFILL-MULTIREGION (r1 R1 "terminal 账目修"). Without a discriminating experiment (e.g., which region's failure flipped the status, and which commit), the attribution is unverified/unfalsifiable. Recommend: cite the exact code path (application/tasks/service.py:1054 + projection) and, if possible, identify that the K11 primary region is one of the 2 empty-OCR regions (which would make the PRIMARY re-decision the direct cause), or re-attribute to BACKFILL. Let me check whether the K11 primary region (reading_order 1 = 첫 region) is an empty-OCR region. K11 regions by reading_order: ro1 = beade011 당근아? (has text). The 2 empty-OCR regions: e762169f (sfx, source empty) and 9d7500d0 (empty OCR "  "). So the primary (ro1) is not an empty-OCR region. Hmm, but "primary" = region_ids[0] which may be ordered differently from reading_order.

Hmm. Actually, `region_ids[0]` is the primary of a *page-level plan unit set*. Hmm.

So the claim "empty OCR 失败计入 Run1 终态" — for K11, run1's step list has exactly ONE failed term_extract (line 364-368: INVALID_INPUT "region has no OCR text"). But there are 2 empty-OCR regions. So only 1 of them shows a failed step in run1's step list (the other may have failed at a different step, or wasn't planned in run1). And the report says "2 空 OCR region term_extract INVALID_INPUT 同型复现" overall (run2 count). Let me check K11's run2 failures: the summary shows run2 status completed_with_failures; grep earlier showed lines 355/389 "status": "failed" in the FIRST-run summary (which had run2 per-region failures). For the rerun, attribution list says ["defect:run1-PipelineRunStatus.COMPLETED_WITH_FAILURES", "defect:run2-region-chain"].

Hmm, so in the rerun, run1 has 1 failed term_extract step; plus run2 has failures. Report says 2 empty-OCR regions reproduced identically. Let me check the rerun's run2 section for 2 failures. Let me read lines 649-765 of the rerun K11 summary.

I should also verify the claim that first-run K11 run1 = completed with the same 2 empty OCR regions not counted. In the first run's summary, run1.steps = 9 generic page-level steps all completed → status completed; there was 1 translate step. So yes, the first-run run1 didn't surface any failure.

So the structural change between generations: run1's step recording went from page-level aggregate (9 steps) to region-level (66 steps) — that's what exposes the failure and flips the status. Which commit did that? Hmm, that's a *runner/DB* change: the runner's `run1.steps` extraction reads steps from the DB for the run. If region-level steps are now attached to the page-level run (because BACKFILL's `_plan_region` fan-out creates region-level units under the primary run), then run1 now includes region-level units → their failures count in run1's terminal state. That is exactly the BACKFILL fan-out change (region_ids[1:] as separate units under the same run) + PRIMARY (primary region also a `_plan_region` unit). So "terminal accounting unified" = fan-out means the page-level run's terminal state now includes per-region unit failures. That's coherent with BACKFILL (fan-out) + PRIMARY (primary included). So the attribution to PRIMARY alone is imprecise but the direction ("PRIMARY 语义定稿 + 上游 fan-out") is right. The report says "与 Run2 region 链口径一致化（PRIMARY Task 的 terminal accounting unified 语义）" — attributing to PRIMARY. Given depends_on includes PRIMARY (which depends on BACKFILL), and the brief says fork=87f61d8b includes PRIMARY-SFX-GATE 语义定稿, the attribution is defensible but should name the chain. I'll make this a P3: attribution should be verified against the code path and the BACKFILL/PRIMARY chain, and ideally support with a discriminating check (e.g., confirm the failing unit's region is a `_plan_region` unit of the primary run).

Let me check the rerun run2 section to count failures and confirm 2 empty OCR regions.

Then I need to check the remaining pieces:
- ko_rerun_similarity.py implementation (mine, normalization, alignment) — verify the gate thresholds 0.95/0.70 match quality-thresholds §5, and the normalization ("normalized similarity"). Item: does normalization strip whitespace? Given pair 10 raw differs but normalized=1.0, normalization strips whitespace. Is that per CALIB method? CALIB's method for the similarity gate — let me check the CALIB script implementation to compare (report claims "方法复刻 CALIB 先例").
- ko_rerun_k11_driver.py (probe/retry, steps).
- ko_rerun_readability_increment.py (3 requests; sampling; CSV).
- quality-thresholds §5 dual-track definitions.

Let me read the diff for ko_rerun_similarity.py (lines 433-688) and the k11 driver (103-271).
dsh: reasoning:
The similarity script looks reasonable. Notable details:
1. `distribution()` n_variant counts v < 1.0 → for the reported JSON, n_variant=1 while pairs[].status has 2 "variant" (ro5 and ro10). The pair-level `status` uses `tf == ts` (raw) while stats use normalized. So "12/13 逐位一致" in the report = normalized-identical (ro10's raw differs but normalized equal). The report's wording "12/13 对逐位一致" is technically about normalized equality, whereas "逐位" (bitwise/character-wise) suggests raw equality → 11/13 raw identical + 1 raw-only-whitespace variant + 1 real variant. This is a precision issue: the report should say "12/13 归一化后一致（其中 1 对仅空白差异，normalized=1.0；raw=0.9474）". Actually the JSON discloses it, but the report doesn't mention ro10's raw difference at all. Also the report's §4 row says "浮动对 1（reading_order=5...)" — under-reporting by not mentioning ro10's raw text difference. P3/P4: 报告与 JSON 的 pair 状态口径未对齐（raw vs normalized），且 §4 未登记 ro10 空白差异；建议在报告中按 raw/normalized 双列登记。

Hmm, is that material? The gate is on normalized, so the verdict is unaffected. It's a disclosure precision issue → P4? The review's item D asks about honesty of the "natural FAIL" narrative; the 12/13 claim is embedded in that. I'd rate P3 given "逐位一致" is used as evidence of sampling stability (an honest accounting would note 1 pair differs in raw whitespace only). Let me call it P3 but low.

2. `translations_by_reading_order` uses `detail.get("source_text")` and requires translate_details to cover ALL regions (else FATAL). In K11's rerun summary, translate_details has 11 entries but regions = 13. Wait — the script requires set(t1) == ros1 (all 13 reading orders covered by translate_details)! But the output JSON has n_pairs=13, with 2 empty_both pairs (ro9 and ro13). So translate_details DOES have 13 entries (including 2 empty). Earlier I thought 11; the report says nonempty pairs = 11. OK: translate_details = 13 entries (11 non-empty + 2 empty). Fine.

3. Gate verdict uses `stats_norm_all["median"]/["min"]` (all pairs) rather than non-empty. The coverage precondition is ">=1 non-empty" (enforced via nonempty list, else NO_DATA). Empty pairs get similarity 1.0 (both empty) → they inflate the median toward 1.0 and don't affect min. Is that per CALIB? The docstring says "empty-pair rule (registered, CALIB): both empty = 1.0, exactly one empty = 0.0". Need to verify CALIB's implementation uses the same. Since the script claims to replicate CALIB, and I can't read CALIB's script (it's in experiments/M2-QUAL-DETERM-CALIB/ — check if it exists in the worktree; the docstring says the CALIB dir is outside this Task's allowed surface but it should still exist in the repo). Let me check.

Also, `quality-thresholds.md` §5 must be checked for the exact gate definition (median≥0.95 and min≥0.70 on what subset — all pairs or non-empty?). If §5 says the gate applies to non-empty pairs, then using all-pairs median (inflated by empty=1.0) is a口径 error. Let me read quality-thresholds.md §5.

Let me do that now.
dsh: reasoning:
quality-thresholds §5 (line 168) confirms: "全部对齐对（含空译文对规则：双方空=1.0、单方空=0.0）满足 median ≥ 0.95 且 min ≥ 0.70 方为 PASS" — so the gate applies to ALL aligned pairs, including empty pairs with the empty-pair rule. The script's use of stats_norm_all is CORRECT per the documented caliber ✓. Good — no finding there.

Also §5 says: "region_count=0 的 case 贡献 0 对 → 同 NO_DATA 口径豁免（与 §6 R11 零 region 豁免同口径），不阻断整体 Gate 但单独登记". So K19's 0-region → NO_DATA exemption, consistent with the report's treatment (K19 exempt).

And §5 has "覆盖前置（CALIB r1 R2/R3）：非空对 n≥1 方可判定，否则 NO_DATA" — script enforces ✓.

Also §5 line 172: "qualification runner 以 `--determinism-track remote|mock` 参数显式记录所选轨道，声明与 provider 绑定不一致时 fail-closed 报错". This is a documented requirement (CALIB r1 R9)! The rerun's runner does NOT have a `--determinism-track` parameter (per the diff, only --sfx-policy and --meter-translation were added). The similarity script records the track implicitly ("this run binds the REMOTE track") but the documented requirement says the runner must explicitly record the track via the parameter and fail-closed on mismatch. Let me verify whether `--determinism-track` already exists in run_qualification.py baseline (maybe it was added by TA3-B2 first run or CALIB). Let me grep run_qualification.py for "determinism".

If missing, that's a real finding (P2): documented caliber requires explicit track recording with fail-closed; the rerun's determinism artifact instead asserts the track in a free-text note, and the runner has no such flag. Let me check.
dsh: reasoning:
Confirmed: the documented caliber (quality-thresholds §5 / CALIB integration.md) requires a runner flag `--determinism-track remote|mock` with fail-closed on mismatch. Neither `run_qualification.py` (baseline nor the rerun tweak) nor the new `ko_rerun_similarity.py` implements it. The rerun's determinism artifact determines the track by prose only ("this run binds the REMOTE track") and does not fail-closed on provider/track mismatch.

Wait — but the `--determinism-track` requirement may have been part of the CALIB task's proposal for a *future* runner enhancement rather than an existing implemented feature. Let me check CALIB's task doc / calibration.md whether it says "runner 增强候选" or is a requirement on the qualification runner that must already exist. The integration.md states it as part of the ruled caliber ("判轨规则=translate provider 绑定 + runner --determinism-track remote|mock 显式记录、不一致 fail-closed"). If the runner lacks the flag, then the rerun's determinism step did NOT follow the documented caliber procedurally, though the substance (remote → similarity gate) was applied. Severity: P2 (documented caliber control not implemented → no fail-closed guarantee; two P&C pages' track declaration is free text). Actually hold on — is it possible that run_qualification.py has such a flag under a different name? Let me grep for "track" in experiments/M2-TA3-B.

Let me check.
dsh: reasoning:
Confirmed: no `--determinism-track` anywhere. So the rerun's determinism run did not use the documented procedural control. Note also that the report §4 says "轨道判定：本 run translate 绑定为 remote DeepSeek → 按 thresholds §5 双轨规则走相似度 Gate" — substance correct, but the documented `--determinism-track` explicit-record/fail-closed mechanism is absent. Severity P2: the caliber's declared executable rule ("声明与 provider 绑定不一致时 fail-closed 报错") is unimplemented; the rerun therefore cannot demonstrate fail-closed protection. Note also that this is the *Task's* allowed surface (experiments), and the Task was the natural place to implement it (the runner tweak was in scope: "run_qualification.py 需 ko-rerun 参数微调"). So it's an in-scope miss → P2.

Hmm, but I should be fair: the rule may have been written by CALIB as a *forward requirement* for the runner that no Task has implemented yet. If so, the finding stands as "documented control not implemented; the rerun should either implement it or register it as a known gap". Either way it should be flagged. I'll rate P2 but note it's a caliber/process gap rather than a wrong result.

Now let me check the CALIB calibration.md for the actual method (to confirm the rerun script replicates it: normalization-based storage of similarity_normalized, empty rules, median/min on all pairs). Let me read the calibration.md relevant parts and if the CALIB script exists in the worktree.

Let me glob experiments/M2-QUAL-DETERM-CALIB.
dsh: reasoning:
CALIB 局限 5 explicitly: "归一化口径吸收换行/空格差异（K11 浮动 7→5）；若产品语义认为换行位置也是译文的一部分，应引用 raw 口径附报。" → The rerun's similarity JSON DOES include similarity_raw alongside similarity_normalized, so the raw caliber is attached ✓. But the report §4's table only reports the normalized numbers and doesn't mention that ro10 raw=0.9474 (whitespace-only difference). Given CALIB 局限 5 says the raw caliber should be attached as supplementary, and the JSON does attach it per pair, I'll downgrade my finding to P4: 报告正文未附 raw 口径与 ro10 的 raw 差异（JSON 已附），建议正文补一行。（Actually the JSON has similarity_raw for all pairs, so the "attach raw" obligation is met at the artifact level. The report's prose says "12/13 对逐位一致" which mixes calibers. Minor. P4.)

Also CALIB's method: let me verify the CALIB script computes the gate on all pairs with median/min, and whether it uses normalized statuses. Let me read calibrate_determinism.py briefly (the gate function and empty rules).

Also, remaining items to verify:
1. ko_rerun_k11_driver.py: does it do anything problematic (e.g., probe with retries, secrets handling)?
2. ko_rerun_readability_increment.py: sampling, 3 requests, self-assessment; check it doesn't persist keys and that the CSV is ai_draft.
3. The CSV's n=15 and ai_mean 4.31 claim.
4. The metering proxy "behavior zero change": compare `reregister_env_resolver_metered` vs original `reregister_env_resolver` (descriptor note differs; also whether the original registers the same). Let me read the original function in the worktree.
5. Check `payload.payload_json()` exists (src/ports/translation) and `result.raw_text` exists → otherwise the proxy would raise. Let me verify.
6. Check summaries-sfx evidence for the sfx.policy=translate claim (region.sfx_policy == translate; gate放行).
7. Check the first-run quality-report.md F1-F6 to confirm the claims about F1/F2/F3/F4/F5 and the "TILING 已确认五页" region counts.
8. Check the allowed/forbidden surface: does the diff touch forbidden paths? From the diff file list: doc/handoffs, doc/tasks, experiments/M2-TA3-B/{4 files}, verification/M2-TA3-B/ko-rerun-report.md, verification/M2-TA3-B/phase2/ko-rerun/**. Plus quality-report.md §10 (allowed: "quality-report.md（追加 ko-rerun 节）"). No src/tests/contracts/packaging/apps. ✓ But wait: the diff also shows `verification/M2-TA3-B/phase2/ko-rerun/ocr/svg-gt-K11.json` and `svg-gt-K19.json` as NEW files under phase2/ko-rerun/ocr — these are copies of the first-run SVG GT (reported as read-only copies). But hold on, the report says the ocr dir contains them. Adding copies of first-run GT is fine as long as first-run products are unmodified. Need to verify the first-run files are unchanged — the diff doesn't include phase2/ocr/svg-gt-K11.json modifications ✓ (only ko-rerun/ paths are new). Also `phase2/ocr/svg-alignment-trace.json` appears in the grep results but not in the diff → unchanged ✓.

Hmm wait: is duplicating GT into the new dir a problem? The report says "SVG GT=首跑 svg-gt-K11/K19.json 只读副本". Let me verify the copies are byte-identical to the first-run ones — I can compare via reading? They're large JSON. I could grep for a distinctive value in both. But shell is unavailable; visual diff is impractical. However, measure_cer.py reads --ocr-dir; the rerun passed ko-rerun/ocr as the ocr dir, which must contain the GT files. It's plausible they're copies. The risk of silent divergence is low but the reviewer should note: copies of first-run GT (禁改面产物) were re-created in a new dir; identical-content verification is a NOT_VERIFIED item for the integrator (hash compare). Good NOT_VERIFIED item.

9. Check key hygiene: grep for "sk-" in the diff/new artifacts.
10. Check the pipeline_failures claim: the report says "全链 Gate（pipeline_failures=0）FAIL". Is "pipeline_failures" a real field? Let me check qual-K02.json for "pipeline_failures" — my earlier grep for pipeline_failures returned no match in qual-K02.json (the grep included pipeline_failures and found none). So the summaries don't have a pipeline_failures field; the report's "全链 Gate（pipeline_failures=0）" references the first-run's Gate definition (quality-report §?). Let me check the first-run quality-report for "pipeline_failures" to confirm the Gate definition exists.

Let me batch several greps/reads.
dsh: reasoning:
Key hygiene: no `sk-` literals, no key plaintext; `Bearer {key}` is runtime assembly ✓ (consistent with first-run R13 mechanism). The repro command uses `$(cat .../deepseek.key)` — a path reference, not a value; that's the pre-existing first-run pattern (report §8). Acceptable, though the report embeds a path to the key file. It was there in the first-run report too. Fine.

Now let me check the driver script (lines 103-271) and the readability script (272-432) for behavior issues (e.g., the driver writing settings, leaving DB state, probe semantics).

Also check `payload.payload_json()` and `result.raw_text` existence in src to validate the proxy.
dsh: reasoning:
`payload.payload_json()` exists (protocol.py:116) ✓ and `TranslationResult.raw_text` exists (ports.py:33) ✓. So the metering proxy's attributes are valid.

But wait: does `TranslationRequestPayload` have `.regions`? The proxy uses `len(payload.regions)`. Let me verify protocol.py:67-120.

Also: does the production client wrap the provider differently — the proxy is registered via `registry.register(descriptor, factory)` where factory returns the proxy. Since production resolves the provider from the registry, the proxy instance is used. Fine.

Behavior-change risk: `_MeteredTranslationProvider` is not the concrete class; production code might do `isinstance(provider, OpenAiTranslationProvider)` or use `provider.__class__.__name__` for logging. Earlier grep of translation service didn't show isinstance. Also `registry.register` may check capabilities on the descriptor (already provided) ✓. And `__getattr__` passthrough covers other attributes.

A subtle behavioral difference: proxies lose identity for `is` comparisons — e.g., if production compares `core.providers.get(...) is core.translation_provider`. Let me check if anything does that... The first-run review noted PROD-DETECT-3 裁决③ about instance sharing for detector. For translation, hard to verify statically; the run's behavior (93/93 translated, export OK) is empirical evidence of no functional break ✓. But "行为零变更" should be softened to "在本次 run 未观察到行为差异（逐 region 请求数/译文数与生产路径一致）" — actually the metered K02 run is the only witness, and there's no A/B (K02 was not run without metering). So the "zero behavior change" claim is asserted by construction (passthrough) + the run completing; evidence strength: code-inspection + successful run, no control comparison. Reasonable but should be labeled as such. Combined with the K11 metered run1=8 anomaly (which is NOT a proxy artifact — steps come from the DB), fine.

Hmm, one more important thing about the proxy: `_records.append` happens after `self._inner.translate(payload)` returns. If the inner provider *retries internally*, each retry is inside one translate() call → one record per logical call, so "requests" ≠ actual HTTP requests! The report treats metered requests as HTTP requests ("计量请求数 140 次成功请求"). If the production provider retries transparently on timeout/5xx, the metered count undercounts HTTP attempts. In the outage, 45 PROVIDER_TIMEOUT typed failures — those threw. Whether retries exist inside the client (e.g., transport retry) matters for the "requests" semantics. The report's claim "每次请求恰好 1 个 target region" is about the *call* granularity, which is what matters for the cost model per region; but labeling them "HTTP 请求" is an over-claim unless the client doesn't retry. Let me check the openai client for retry logic.

Let me look at src/infrastructure/providers/openai_client.py for retry.

Also check `payload.regions` attribute.
dsh: reasoning:
`payload.regions` exists ✓. The docstring says "One Context Group request (D06 §18.1, §84 grouping)" — regions is a tuple of RegionInput, and grouping per D06 §84 means a request *can* carry multiple regions in principle. Empirically 1 per request.

No retry loop found in openai_client.py (grep found only docstring lines about retryable error classification). Let me double check whether retry happens elsewhere (e.g., in the translation service or pipeline step). Grep for "retry" in src/application/translation and infrastructure/providers.

Actually the earlier review (first-run) mentioned "重试走生产语义". Let me grep for retryable handling in src to see if there's an automatic retry wrapper.

Let me grep src for "retryable" and "PROVIDER_TIMEOUT".
dsh: reasoning:
There IS a retry mechanism: `src/infrastructure/providers/retry.py` with `RetryPolicy(max_attempts=3)` default and `runtime.DEFAULT_RETRY_POLICY = RetryPolicy(max_attempts=2, backoff_seconds=1.0)`; settings["providers"]["retry"] = {max_attempts, backoff_seconds}. And `run_with_retry` wraps calls.

Critical question: is the retry wrapper applied *outside* the provider.translate() (i.e., at the registry/runtime level, wrapping the factory product) or inside the provider? If the retry wrapper wraps the provider obtained from the registry, then when the metering proxy is registered as the provider via `registry.register(descriptor, factory, ...)`, the retry wrapper may wrap the proxy → one metered record per logical call, and HTTP attempts = up to max_attempts per record. Then "140 requests" = 140 logical calls, NOT 140 HTTP requests. The report/budget-register call them "requests"/"HTTP 请求"/"每次请求恰好 1 个 target region"—the region-per-request conclusion still holds (payloads are per call), but calling them HTTP requests overstates. Also during the outage, 45 PROVIDER_TIMEOUT typed failures were recorded as terminal failures per region — meaning retries did happen (each region's translate call retried up to N times before surfacing typed failure), so the actual HTTP attempts during the outage were far more than 46. The report says "无重试风暴" — that's about no unbounded retry; with max_attempts=2, 46 failed regions × 2 = 92 attempts. Worth noting: "无重试风暴" is supported by the bounded policy, but the exact attempt count is not metered.

Let me check runtime.py to see how the retry policy wraps providers (line ~92, 187) and whether the registry's provider resolution applies retry. Let me read runtime.py around 80-200 and see if the wrapper is applied to registry-resolved instances.

This matters for the "计量口径" finding: metered "requests" = provider.translate() calls (post-retry-wrap), i.e., logical calls; actual HTTP requests ≥ that. The cost model uses 607 est tokens/request measured from payload+completion per *logical* call — which is the right unit for token cost per region (each logical call sends the payload once... unless retried, in which case the payload is resent and tokens are consumed again, but only the successful call's completion is counted). So est token under-counts when retries occur. Direction: under-estimate → the stop line could be even more exceeded. Conservative direction is fine (they stopped).

But the *label* matters: budget-register says "140 = Run1 93 region-level requests + Run2 47 successful region requests; 46 further Run2 requests failed" — if each failed region was attempted twice, then "46 further requests failed" undercounts HTTP attempts. The report's "347 次成功请求" is similarly logical calls.

Let me verify runtime.py wraps with retry.
dsh: reasoning:
I need to see where retry_policy is applied to provider calls. Let me grep for "run_with_retry" usages.
dsh: reasoning:
handlers.py:338 and :422 use `policy=self.deps.retry_policy` — via fallback.py (`ResilientProvider`?) which wraps the provider and calls run_with_retry(provider.translate...). So the retry wrapper sits OUTSIDE the provider (the handler resolves the provider from the registry, then wraps it in the fallback/retry chain).

Sequence: handler → fallback wrapper (with retry_policy) → provider.translate(payload). If the metering proxy is the registered provider, then the retry wrapper calls `proxy.translate(payload)` up to max_attempts times; only the final successful call appends a record. So metered "requests" = number of logical translate calls that ultimately succeeded... Actually careful: run_with_retry calls `call()` which invokes proxy.translate → the inner call raises → no record; retried → eventually raises → no record. For successes after retries, only ONE record (the successful attempt) is appended. So metered requests undercount HTTP attempts by the retry factor. Confirmed structurally.

So finding: "140 次成功请求" are logical provider.translate() calls, not HTTP requests (production retry policy DEFAULT max_attempts=2 / configurable; during the outage 46 regions failed after retries → HTTP attempts ≥ 46×2 ≈ 92 uncounted). The cost model's per-region token estimate is therefore a lower bound (each retry resends the payload = input tokens re-billed but only counted once). Direction: conservative for the stop line (under-estimate). But the *labels* are overstated: "每次 HTTP 请求恰 1 target region" → should be "每次 provider.translate() 调用恰 1 target region". Also relevant: because the retry wrapper wraps the proxy, `_MeteredTranslationProvider` may be called multiple times per region without recording — so "请求数≈2×region 数" is a *lower bound* on HTTP requests.

Hmm, does the retry wrapper wrap the *registry-resolved provider*? Let me verify handlers.py:330-345 to see the wiring, to be accurate. Let me read handlers.py around 320-350 and 410-430.

Also let's check fallback.py:100-140 to see the retry invocation.

Let me read those.
dsh: reasoning:
Confirmed: `run_chain` → `run_with_retry(... invoke(provider_id) ...)` where invoke resolves the provider and calls `provider.translate(payload)` (or recognize). So the retry loop is outside the provider instance → the metering proxy sees only the final successful attempt (and for failures, no record). So metered "requests" = successful logical calls; HTTP attempts ≥ that (max_attempts default 2).

Also `run_with_retry` uses `payload_hash_provider` — interesting: it may guard against retrying identical payloads? Let me look at retry.py 96-140 to see if attempt_count and payload hash dedupe exist. If the same payload hash is retried, maybe it's blocked? Let's read retry.py.

This matters for the "无重试风暴" claim and the actual attempt counts. Let me read retry.py.
dsh: reasoning:
Confirmed: bounded retries with max_attempts (default 2), typed errors, payload-hash guard. So each failed region during the outage = up to 2 HTTP attempts (or more if settings["providers"]["retry"].max_attempts is configured — default 2). The metering proxy counts only successful calls. So:
- "计量请求数 140 次成功请求" = 140 successful provider.translate() calls; HTTP attempts ≈ 140 + 46 (failed regions × ~2 attempts = 92) → ~232 for K02. Actually the summary reports attempt_count? `run1.steps`/`run2.per_region` may record attempt_count. If so, we could compute the real attempt total. Let me check qual-K02.json for "attempt_count".

Let me grep qual-K02.json for attempt_count values. If run2 per_region has attempt_count=2 for the 46 failures, then HTTP attempts for K02 = 93 (run1, attempt_count 1 each, assuming) + 47 + 92 = 232.

This is a legitimate P3 finding on 计量口径: the report says "请求数" and "HTTP 请求" but the meter counts provider-call-level successes; retries multiply actual HTTP requests/token consumption. Direction conservative (under-count) for the stop line, but the phrase "每次请求恰好 1 target region" and N4's "重要发现" should be restated as call-level. Also the token estimate under-counts retried input tokens.

Let me quickly grep for attempt_count in qual-K02.json.
dsh: reasoning:
No attempt_count in the summary. So the summary doesn't record retry attempt counts — the metering can't distinguish 1 vs 2 HTTP attempts. OK.

Now let me finish the remaining checks:
1. ko_rerun_readability_increment.py (diff 272-432).
2. summaries-sfx/qual-K11.sfx-translate.json key evidence (sfx_policy translate, gate path).
3. The readability CSV (n=15, ai_mean 4.31).
4. First-run quality-report F1 region counts (already have).
5. Verify the diff's Task/handoff claims about "禁改面零 diff" — the diff file list shows only allowed paths ✓ (need to double check that `verification/M2-TA3-B/quality-report.md` was allowed: yes, "quality-report.md（追加 ko-rerun 节）"). Also `doc/tasks/M2-TA3-B2-KO-RERUN.md` and handoff ✓.
6. `git status` — unavailable (no shell) → NOT_VERIFIED for uncommitted changes / tip=0001d68c docs commit presence.

Let me read the readability script diff and the CSV.
dsh: reasoning:
CSV: 15 rows ✓. ai_region_score mean: values 5,5,4,5,5,2,5,4.7,2.7,4,4,3.3,5,5,5 → sum = 5+5+4+5+5+2+5+4.7+2.7+4+4+3.3+5+5+5 = 64.7 → /15 = 4.313 ≈ 4.31 ✓ and range 2.0–5.0 ✓. Report claim verified.

Note: K02's 12 rows are drawn from a pool; stratified_take with pool size ~91 and n=12 → step ~7.58 → indices 0,7,15,... fine.

One issue: `stratified_take` picks items by index, and the resulting CSV includes K02 region_ids. Also the K11 picks: it picked 3 including "3f1b7fe3" which is an UNALIGNED_G1_CASE region (당근아!) — but that's fine for readability.

Now, N1: The readable worksheet "ai_draft" prefill. Fine.

Now let me check the sfx summary evidence for the sfx.policy=translate claim: grep for sfx_policy in summaries-sfx/qual-K11.sfx-translate.json.
dsh: reasoning:
The sfx-translate summary confirms region.sfx_policy = "translate" for the sfx region (line 644 and 1039 — two generations of region snapshots) and the other 12 regions remain "skip". Hmm interesting: lines 500-644 in the sfx run show 12 "skip" + 1 "translate"?? Wait, that's odd: the sfx run has all regions with sfx_policy... Let me look: 500-644 are 13 entries (12 skip + 1 translate at 644). But the ordering: entries at 500..632 are "skip" (12 entries) then 644 "translate". Hmm — actually the sfx_policy field is per region; the production applies the policy to all regions?? The report says "sfx region 的 sfx_policy 字段实测 skip（主 pass）→ translate（对照 pass）". If ALL regions got "translate", the others would be non-sfx so no effect; but here 12 are "skip" and 1 is "translate" — which suggests only the sfx region got the policy... Hmm, but core_assembly applies sfx_policy_cfg to *all* created regions (line 1041: `sfx_policy=(sfx_policy_cfg if region_type is sfx else SKIP)` presumably). Let me check core_assembly.py:1035-1045 to see.

Actually the block at 500-644 might be the "regions" list of the sfx run: 13 regions, 12 with skip and 1 (sfx) with translate. That perfectly matches "region creation applies the settings policy only to sfx regions" — good evidence for the claim. Then lines 931-1039 = translate_details (12 skip + 1 translate? hmm, detail entries carry sfx_policy?). Whatever — the key evidence is there: the sfx region carries "translate" in the对照 pass and "skip" in the main pass (let me verify the main pass has the sfx region as skip — earlier I saw qual-K11.json translate_details with e762169f sfx_policy "skip" ✓ line 1035 of the main summary).

And the sfx region's OCR is empty → term_extract INVALID_INPUT (line 267-268 / 714-715 / 748-749) → policy 放行 but no source text. This supports N6.

Now, one thing to check for the SFX claim "gate 放行": the report says "生产 gate 按 decide_sfx_translation 放行进入正常翻译流". Is there direct evidence (e.g., a translate step for the sfx region in the sfx run)? The sfx region's term_extract failed → the translate step never ran. So "放行" is an inference from `sfx_policy=translate` + `decide_sfx_translation(region_type='sfx', policy='translate')` → TRANSLATE. There's no observed translate step for the sfx region (0 translated sfx). The report's wording is careful: "配置语义验证成功（…region.sfx_policy skip→translate，生产 gate 按 decide_sfx_translation 放行进入正常翻译流）但端到端仍不可达". Strictly, the *gate decision* was not directly observed either (no log of decide_sfx_translation for that region); it's inferred from the policy field + documented gate function. Given the gate function is trivially deterministic (`decide_sfx_translation` reads region_type+policy), the inference is sound. But the claim "gate 放行" as *实测* is an inference, not an observation. I'll note it as P4 precision: describe as "由 region.sfx_policy=translate + decide_sfx_translation 语义推断放行；无该 region 的 translate step 实体证据（term_extract 先失败）"。

Let me check whether the sfx summary contains any translate_details entry for the sfx region. Let me look at lines 1030-1060 of the sfx summary and the "details" section.

Actually the grep showed line 1039: "sfx_policy": "translate" in what seems a repeat of the regions list (maybe "translate_details"). Let me read 1025-1060 of the sfx summary.
dsh: reasoning:
Confirmed: sfx region e10c0151 (regenerated id) has region_type=sfx, sfx_policy=translate, source_text="" → no translation ✓. Region ids differ between passes (regenerated) — consistent.

Note: the sfx run's translate_details for the sfx region shows final_source "none" — the gate was bypassed by the earlier term_extract failure. So "gate 放行" is inference (as I noted) — the actual translate step never ran for that region. Fine, P4.

Now let me verify the "TILING qualification 五页 region 数" and the "881–1721" range arithmetic — already done. And the claim "K02 尺寸 600×18401" ✓ (budget-register).

Let me now check the K02 run1/run2 more: "93/93 final 有译文" — verify n_translated=93 in qual-K02.json. Let me grep for "n_translated" or "translated": in qual-K02.json.

Also check "export OK 5,069,825B" and K02's region_count.

Let me grep qual-K02.json for `"translated"`, `"region_count"`, `"size"`.
dsh: reasoning:
K02: region_count 93 ✓, ocr 93, translated 93 ✓, export size 5,069,825 ✓, run2 region_target_count=93, region_runs_executed=93 ✓.

Now: is the K02 CER data affected by Run2's 46 failures? CER uses OCR text (ocr_details) — run1 OCR complete (93) and run2 regional OCR... The report says CER n=6 only from K11, so K02 doesn't contribute to CER (G2 pending human worksheet). So the Run2 46-failure impact on "CER/翻译数据" is:
- CER: K02 contributes 0 auto-scored rows (G2 pending) → no impact ✓.
- 翻译数据: 93/93 regions have final translations from Run1 ✓ (translated=93 in details). So the failure affects only the Run2 region-rechain coverage, not the final translations ✓. The report says exactly this (§1.3). ✓ Verified.

Should "F1 关闭" be accepted? The F1 finding was "manga ogkalu backend 对 webtoon 长条漫返回 0 候选" — the fix = TILING. Evidence: TILING qualification 5/5 pages PASS (region counts > 0 via production provider.detect), plus this rerun's K02 full chain 0→93 regions reaching export OK. The report itself is careful: "首跑归因 F1（data×检测域缺口）就此关闭（该页级）" and the Gate table says "F1 解锁实证（K02 93 region）；K01/K04/K05/K08 有 TILING GATE 先例、页级实测待裁决". So F1 is closed at page level for K02 and at detect level for all 5 via TILING. The review item B asks whether the combined evidence chain is complete: 5/5 pages detect-unlocked (TILING qualification, separate Task, GATE PASS) + 1 page full-chain (K02). Note TILING was at provider.detect level only; the full chain for K01/K04/K05/K08 is unmeasured. Is that a gap for "F1 关闭"? F1 was specifically a detect-domain gap; provider.detect evidence covers it for all 5 pages. The remaining unknown is whether those pages' full chains behave (which is a qualification question, not F1). The report's framing is honest and scoped ("该页级"). One caveat: the TILING qualification ran provider.detect directly, not through the production import→detect pipeline path; K02's full chain now confirms the pipeline path works end-to-end for one page. That's a reasonable combined chain. I'd note as a P4/observation: F1 closure is supported for the webtoon family at detect level (5/5) + full chain (1/5), and the report correctly scopes it; but the quality-report §10 index line says "F1 解锁实证（K02）" — consistent. OK, no finding beyond noting the residual (4 pages lack full-chain evidence) — the report already registers it as 待裁决.

Hmm, wait. Is K02 the largest/most representative webtoon? K02=600×18401; K01=690×62133 (3.4× taller). K02 is the smallest region count (93 vs 180/113/62/60). K02 has the *most* regions. Fine.

Now, one thing about "F1 关闭": the first-run F1 also included K19 (textless page) — no, K19 is F4.

Now let me verify the remaining review item: 停跑点选择代价最优 (K02 试算后停 vs 继续部分). The Owner ran K02 pilot (84.9k est tokens) then stopped, using K11/K19 as a near-free comparison set. Alternative: run the F2 trio (K07/K09/K10) first to close F2 (the only unmeasured unlock) at the cost of 3 pages × est 120-400 regions × 2 × 607 = 44万-88万 est tokens → itself likely over/at the line. So stopping was reasonable. But note: the Owner's §7 option ③ proposes exactly "只跑 F2 系 3 case" ~ unknown cost. A reviewer could point out that the *cheapest* high-value next step (if the line were relaxed) is K01/K04/K05/K08 (known region counts: 415 regions → 415×2×607 = 50.4万... hmm, that's essentially at the line). Interesting: known F1 cases (180+113+62+60=415) → 415×2×607 = 503,810 ≈ 50.4万 — just over 50万 by the same model. So even the F1 re-confirmation set alone would exceed the line. That reinforces the stop decision's internal consistency: no material subset fits under 50万 except a single case (K04: 113×2×607=137k; K05: 75k; K08: 73k; K01: 218k). So one could have run e.g. K08 (73k) + K05 (75k) + K04 (137k) = 285k, or K01 alone (218k), to close F1 for more pages. But F1 is already detect-level closed by TILING; the value of more full-chain runs is low relative to cost. The report's option list covers the choices; the reviewer can add the concrete per-case cost table as a recommendation (the §7 list lacks per-option token cost estimates — it says "§1.2 选项①–④" but doesn't attach cost to option ③).

Actually §7.1 says "7 个停跑 case 的范围与预算（§1.2 选项①–④；K07/K09/K10 兼收 F2/ALLOC 关闭确认）" — the options are in §1.2 line 53, which lists 4 options but no per-option cost. §7.2 gives the K02 clean rerun cost (+113k). §7.3/§7.4 no cost. So the ruling checklist lacks quantitative cost for options ①–④ (e.g., option ③ ≈ 44万–88万 est; option ② --max-regions sampling cost depends on N). That's a legitimate "完整性" finding for item 8: the checklist should attach est-token cost/coverage per option so the user can rule. P3.

Now let me double check the "84.9k/case（上限 113k）" and the "347 请求 / 20.4万" numbers vs budget-register (197 metered / 119k, plus ~140 un-metered attempt-1). Report says "实际消耗 ≈ 347 次成功请求 ≈ 20.4 万 est token（两次 K02 全链 + K11×3 + 自评/探针...）". 347: K02 attempt-1 (~140) + K02 attempt-2 (140) + K11 main 19 + sfx 19 + rerun 19 = 337; + 自评 3 + 探针 ~7 = 347 ✓ arithmetic consistent. But the 自评 3 requests and probe requests are *different token profiles*; the extrapolation "347 × 607" isn't meaningful; the 20.4万 estimate: 119k (metered) + attempt-1 ~85k = 204k ✓. So the report's number is an estimate including un-metered attempt-1, labeled "实际消耗". The budget-register discloses the composition. Minor precision: "实际消耗" should be "估计实际消耗（含未计量的 attempt-1 约 140 次）" → P4.

Now, item 6: "estimate_tokens 项目估算器 vs endpoint usage 的口径差异披露" — the report §1.1 discloses prominently ("全部为估算，非 endpoint 计量数据"; token_basis in every summary) ✓. Good. And it references the first-run registration "token 量无计量证据". ✓ Well done. But it does NOT mention the retry inflation (input tokens re-billed on retries) — a gap in the estimate's direction. I'll fold that into the P3 metering finding.

Now let me check the README of the metering proxy claim "行为零变更" more carefully by comparing the metered re-register vs the original re-register function. Let me read the original `reregister_env_resolver` in run_qualification.py.
dsh: reasoning:
The original `reregister_env_resolver` is NOT in run_qualification.py — it must be imported from `translate_probe` (as the docstring says: "translate_probe.reregister_env_resolver + the metering proxy"). Let me find it.
dsh: reasoning:
Comparison: the metered variant replicates the original but:
1. Omits the `_pid_check != PROVIDER_ID` guard (the original pins the production provider id and raises on drift; the metered copy uses `PROVIDER_ID` directly, which is presumably the same constant imported at module top). Minor: the guard is lost in the metered path. Since run_qualification.py imports PROVIDER_ID, it's equivalent-ish. Worth a P4 note (duplication/fork of an existing helper: Divergent Change/Duplicated Code smell — the metered function duplicates ~40 lines of the probe helper, so future changes to the probe helper will not propagate; better: make the probe helper accept a factory wrapper). That's a legit "Duplicated Code" baseline smell finding. Also note: this is in experiments/ so standards are looser, but the review must report judgment calls. It also means when metering is on, the drift guard is bypassed — a (small) reduction of fail-closed protection. I'll make it P3: metered re-register is a forked copy that drops the provider-id drift guard; recommend parameterizing the probe helper.

Let me confirm the note string difference and whether the metered one imports the pid check. From the diff, `reregister_env_resolver_metered` imports: dependencies, openai_client, registry, runtime, translation_openai (OpenAiTranslationProvider), ports.profiles. It does NOT import PROVIDER_OPENAI_TRANSLATION nor check it. Confirmed.

Now let me check whether `run_qualification.py` has the drift-check elsewhere for the metered path (e.g., module-level assert). Let me grep run_qualification.py for PROVIDER_ID definition.

Also I want to confirm the runner's Task/doc claim "禁改面零 diff" and "首跑产物零改动" — the diff file list confirms no first-run product changes: verification/M2-TA3-B/phase2/** files are untouched except? Let me check: the diff includes only phase2/ko-rerun/** (new) and quality-report.md. Wait — it includes `verification/M2-TA3-B/phase2/ko-rerun/ocr/svg-gt-K11.json` (new). And no changes to phase2/ocr/* ✓. And `quality-report.md` (allowed). And `doc/tasks/M2-TA3-B2-KO-RERUN.md`, `doc/handoffs/...` ✓. So scope discipline holds at the diff level ✓.

But hold on: the report says "微调 3 脚本" but the diff shows 1 modified script (run_qualification.py) + 3 new scripts. The handoff says "变更路径：experiments/M2-TA3-B/run_qualification.py（新增 opt-in …）+ 新增 ko_rerun_similarity.py / ko_rerun_k11_driver.py / ko_rerun_readability_increment.py". The user's brief says "微调 3 脚本". Minor discrepancy in phrasing (the brief's "3 脚本微调" vs 1 modified + 3 new). I'll note in the checklist that the actual change set = 1 modified + 3 new.

Now let me check remaining verification: "K11 主 pass 与 rerun 的 export sha 不一致" — rerun-compare.json ✓ and the report attributes it to Run1-layer nondeterminism (F5 根因未隔离) ✓ honest.

One more check for item C: K11's rerun run1 steps show 1 failed term_extract (line 364) while the main pass run1 also has 1 failed term_extract? Let me check whether the main pass run1 (qual-K11.json, lines 76-490) has 1 failed term_extract too (line 364 is in the main pass file — yes! I read lines 196-491 from the MAIN pass qual-K11.json). So main pass run1 has exactly 1 failed term_extract step and 8 translate steps. And the rerun would be similar. So K11's 2 empty-OCR regions: only 1 appears as a failed term_extract in run1's step list; the other failed in run2 (or one region's failure is in run2's per_region). The report says "2 个 OCR 空 region typed INVALID_INPUT 同型复现" per case; run2 per_region shows 9d7500d0 failed and presumably e762169f failed (line 748-749). So run1 surfaces 1, run2 surfaces 2. Hmm, the report's N3 note says "Run1 页面链对空 OCR region 的 term_extract 现在 typed 失败并计入 run 终态" ✓ (1 of them).

Wait, actually let me reconsider: were the 2 empty-OCR regions' term_extract the *only* failures in run1? The run1 step list had exactly one "failed" entry ✓ (grep earlier: lines 355 & 389 status failed in the FIRST-run summary; for the rerun, line 364 failed). Let me confirm the rerun's run1 has exactly 1 failed step: from my read of lines 196-491, I saw only one "status": "failed" (line 365). Yes.

So K11 run1 = completed_with_failures due to 1 failed term_extract unit + (maybe) other accounting. ✓ Consistent with N3.

Now: is the claim "空 OCR 失败计入 Run1 终态" the *cause* of run1 being completed_with_failures? Alternative cause: run1's page-level chain might now be marked completed_with_failures because of the failed *detect*? No, detect OK. Or because of the 2 OCR-empty regions' term_extract (page-level chain includes term_extract). Plausible. But we can't verify the commit-level attribution without a discriminating run. I'll phrase the finding accordingly (P3): attribution is plausible but unverified against the specific code change; recommend citing the code path / commit or downgrading to "语义定稿链（BACKFILL fan-out + PRIMARY re-decision）后的预期差异".

Hmm, actually, let me look for stronger evidence. The failed step in run1 is a term_extract on a region whose OCR is empty. In the first run, run1's step list was page-level (9 steps) and status=completed — meaning the page-level term_extract step was probably one aggregate step that didn't fail, OR the empty region's term_extract failure was not recorded because region-level units weren't part of run1's unit set. The BACKFILL task (fan-out to region-level units) is precisely what would make region-level term_extract units part of the run → their failures count. And PRIMARY extended it to the primary region. Both merged between the two runs. So the honest attribution is "BACKFILL fan-out + PRIMARY primary-inclusion（细粒度 unit 化）", not "PRIMARY terminal accounting". The report's own Task doc says "与 Run2 region 链口径一致化（PRIMARY Task 的 terminal accounting unified 语义）". I'll flag it as P3 with recommendation to name the BACKFILL+PRIMARY chain and cite service.py's terminal computation.

Let me double check the BACKFILL task's handoff for the R1 terminal accounting fix, to be accurate in my finding. Let me grep doc/tasks/M2-TASKS-BACKFILL-MULTIREGION.md for "terminal".
dsh: reasoning:
Confirmed: the terminal accounting unification came from BACKFILL (R1: "账目（BACKFILL R1 口径统一到 primary）…") and PRIMARY extended the same accounting to the primary. PRIMARY's handoff line 26 explicitly describes the terminal accounting. So attributing it to "PRIMARY Task 的 terminal accounting unified 语义" is *defensible* — PRIMARY did carry the accounting unification to the primary region and its handoff documents it as "BACKFILL R1 口径统一到 primary". Also note: PRIMARY's replacement *retired the page-level decision chain entirely* ("被替换的页级决策链整体退役，仅 detect unit 保留 plan 期 id") — this is precisely what makes run1's step list region-level (66 steps) instead of page-level (9 steps) and thus what surfaces the empty-OCR term_extract failure in Run1's terminal state.

Wait, that's important and supports the Owner's attribution better: with the page-level decision chain retired for all detected regions (primary included), the page-level run's units are now per-region `_plan_region` units. So Run1's terminal state = aggregate of those region-level units → the empty-OCR region's failed term_extract counts. So the attribution "PRIMARY Task 的 terminal accounting unified 语义" is substantially correct ✓, though BACKFILL started it (for region_ids[1:]) and PRIMARY completed it for the primary. The Owner's phrasing "PRIMARY Task 的 terminal accounting unified 语义" is acceptable given PRIMARY = the last semantic change before the rerun fork (87f61d8b). I'll down-grade this to an observation/P4 rather than a P3: recommend naming the BACKFILL→PRIMARY chain for precision. Good — this is the value of doing the verification.

Now, K11's 2 empty-OCR regions correspond to regions with empty OCR (9d7500d0 and e762169f in the rerun). In the first run they were df871de5/65069961 (from the F3 row: "K11 2 个 region（df871de5/65069961）"). Hmm interesting: the F3 row lists region ids df871de5/65069961, and the first-run cer-regions.csv has K11:df871de5 (MANUAL_REVIEW:6-svg-elements, empty ocr) and K11:65069961 (sfx empty-ocr) ✓ consistent.

Now let me check whether the K02 `--case K02` run included a "run2" region chain for 93 regions and note the wall times (1848.5s run1, 3742s run2, total 5591s ≈ 93 min). Report says Run1 1848.5s, Run2 3742.0s ✓ budget-register 3741.97 ✓.

Now let me assess item 1's "外推假设（K07/K09/K10 密度 120-400/页）是否合理标注不确定度". The report §1.2 marks K07/K09/K10 as "无先例…按已测密度区间估 120–400 region/页" — labeled as estimate. The density basis: K01=180 (690×62133), K04=113, K05=62, K08=60, K02=93. Density per page (regions per 1000px height?): K01 180/62133 = 2.9/1000px; K02 93/18401 = 5.05/1000px; K04/K05/K08: need heights. K07=690×131289, K09=690×100480, K10=690×100674 (from quality-report F2 row). Using per-1000px densities of the five known: those need heights: K04, K05, K08 heights unknown to me. Let me estimate using K01 (2.9) and K02 (5.05): K07 131289px → 380–663 regions; K09 100480 → 291–508; K10 100674 → 291–509. So 120–400 per page is a *low* estimate for these three: it looks too low! The report's range 120-400/page gives 360-1200 total; but a density-based estimate using the two known webtoon densities suggests 290-660 per page → 960-1990 total. Hmm. That means the "full_range_est_tokens 107万–209万" may understate.

Wait, but the region density can't exceed the number of text boxes; K07/K09/K10 are manhwa pages of similar family. If we scale by K01's density (180 regions / 62133px = 2.90 per 1000px): K07 → 380, K09 → 291, K10 → 292 → total 963 → 963+521 = 1484 regions → ×2×607 = 1.80M est tokens. That's within the report's stated range upper (209万) but way above the "low" 107万. The report's low bound (120/page → 360 total → 107万) is inconsistent with the measured densities of the known pages if the pages are of comparable width/height scaling. Hmm, but per-page density might not scale with height linearly (webtoon panels vary). The five known pages: K01 690 wide; K02 600 wide; K04/K05/K08 presumably 690 wide. K07/K09/K10 are 690 wide. So the closest analog is K01 (same width 690): 2.9 regions/1000px.

So: is the "120–400/页" range justified? 120/page for a 131289px-tall page would be 0.91 regions per 1000px — about 1/3 of K01's density. Hmm, plausible only if K07 is much more sparse. Without data, either could hold. But the *asymmetric* concern: the report's low bound drives the "63.2万 known only" headline (which doesn't depend on K07-10) — fine — and the full range 107–209万. The upper bound 209万 > all; the conclusion (>50万) is robust across the whole range, so the uncertainty doesn't change the decision. I'd file a P4: 外推区间未给出密度推导依据（K01 同宽页实测 2.9 region/1000px 对应 K07≈380，超出 120–400 区间的 400 上界），建议登记密度-url推导或改用同宽 K01 密度做上界；不影响停跑结论（任何组合都 >50 万）。

Actually let me compute more carefully. Is there a height for K04/K05/K08 available? Let me grep the TILING qualification-results.json for sizes. That would let me compute densities properly. Let me check.

This is a worthwhile check because item 1 asks specifically about the extrapolation assumptions' uncertainty labeling.
dsh: reasoning:
No width/height in the TILING results. The DIAG doc gave K01 690×62133. quality-report F2 gave K07 690×131289, K09 690×100480, K10 690×100674. K04/K05/K08 heights unknown; the DIAG handoff mentioned K04=15s budget etc. Not needed.

Rough analysis: For the same width (690) and analogous webtoon strips, K01 = 180 regions / 62133 px. K07 (131289px, 2.11× K01 height) → naive linear scaling 380 regions; K09 (1.62×) → 291; K10 (1.62×) → 292. Total for the three ≈ 963, vs the report's 120–400/page (360–1200). So the report's range brackets the linear-density estimate (963) — actually 963 is within 360–1200 ✓. My earlier "380 exceeds 400" was per-page for K07 only; the *upper* bound 400/page is close to 380. So the range 120–400/page is a defensible bracket around the naive linear estimate (291–380). And the resulting total range 107万–209万 brackets the density-based 1.80M (which is within 209万). Hmm, but wait: region_total_range [881,1721] = 521 + 360..1200. Density-based: 521+963 = 1484 ✓ within. So the range is reasonable and its upper bound covers it. Good — the extrapolation is defensible. The uncertainty is labeled ("无先例", "估计"). I'll note positively, with a P4 suggestion to state the density derivation (per-1000px from K01) explicitly. Actually maybe I shouldn't even file that; but a brief P4 (evidence-grade) is fine. Hmm, I need to be careful not to inflate findings. I'll fold it into the checklist as "合理" with a one-line residual note, maybe as P4.

Now let me check the remaining review items I haven't:

Item 7 范围纪律: 
- "3 脚本微调在允许面（逻辑零变更）": run_qualification.py changes are opt-in flags; default paths unchanged (sfx_policy="" → no settings write; meter_translation=False → original reregister). Verified from the diff ✓. Two caveats: (a) the `_MeteredTranslationProvider` forked copy drops the pid drift guard (only affects the metered path); (b) the runner's default behavior is byte-identical only if argv parsing/help text changes don't matter — fine. Also `summary["provider_policy"]["translate"]` gets an extra string when metering is on — behavior of *reporting*, fine.
- 首跑产物零改动: diff shows no first-run product modifications ✓ (need to verify at commit level: the worktree tip 0001d68c docs commit; can't run git → NOT_VERIFIED for "no other commits touch forbidden paths" — but the provided diff (`git diff 87f61d8b...0001d68c`?) lists all changes. The diff includes doc/handoffs + doc/tasks + experiments + verification. Hmm, does the diff represent the whole branch diff (fork→tip)? It should. The provided review-input.diff has 24 file entries. If the diff is complete, scope is clean ✓. NOT_VERIFIED: whether the diff is the complete fork→tip diff (integrator to confirm via git).
- key 零明文: grep of the diff found no key literals ✓ (only env var name + `Bearer {key}` runtime + `$(cat ...deepseek.key)` path in the repro block). Hmm — the repro block in the report embeds the *path* to the key file (`G:/CODEX/New Manga.task-envs/M2-TA3-B/deepseek.key`), which is a pre-existing pattern from the first run. Not plaintext. ✓ But worth a note: the report's §8 instructs reviewers to `cat` the key into env; the key file lives outside the repo. No plaintext in-repo. Also note that the *reports* contain `scratch_root` paths in %TEMP% (handoff §风险 mentions leftovers) — no secrets.

Item 8 §7 checklist completeness: evaluate. The checklist has 4 items. Gaps I see:
- No cost/benefit quantification per option (①全量预算批准 ~107-209万; ② --max-regions 抽样; ③ F2 三 case ~44-88万 (my calc from 360-1200 regions... wait: K07/K09/K10 = 360-1200 regions ×2×607 = 43.7万–145.7万); ④维持停跑).
- K02 干净重跑 cost given (+113k) ✓.
- Option ② lacks the specific sample size/coverage implications beyond "R7 披露".
- Missing: 是否接受 F1 以 detect 层 5/5 + K02 全链作为关闭依据（即 K01/K04/K05/K08 是否需要页级全链）— the checklist item 1 covers "7 case 范围" but does not separately ask "F1 是否可关闭" — it's implied. I'll note as a P3: §7 缺"F1 关闭口径"与"F2/ALLOC 是否必须页级实测"两个独立决策点（现被范围裁决吞并），以及各选项的 est token 成本表。
- Also missing: the 相似度 Gate 修订选项的成本/影响 (they list 3 options: 维持现阈值保守误报 / 引入语义度量 / 登记 known-limitation) — no cost/impact per option. The BLUF item D asks about completeness of the candidate口径选项 — "维持现阈值保守误报 / 引入语义度量 / 登记 known-limitation" is reasonable but lacks: what happens to the K11 Gate verdict under each option (FAIL vs PASS-equivalent); and the option "语义度量" would itself require a new Task/calibration. Also lacks the interim disposition: the K11 determinism Gate currently FAILs — does that block anything? Should state that the FAIL is directional and doesn't block because the task remains FAIL overall anyway. I'll write a P3 on the checklist completeness (options without cost/impact/consequence), with concrete suggestions.

Now let me finish verifying a few numbers in the report vs artifacts that I haven't:
- "K02 Run2 3742.0s" ✓.
- "估 tokens input 77,314 + output 7,603 ≈ 84.9k" — 77314+7603 = 84917 ✓.
- "单请求 ≈607": 84917/140 = 606.6 ✓.
- "93 region 完整链估算上限 ≈186 请求 ≈113k": 186×607 = 112,902 ✓.
- "已知五页=63.2万": 521×2×607 = 632,494 ✓ but includes K11 (13 regions). The five TILING pages: 508 regions → 616,712 ≈ 61.7万. So the phrase "仅 TILING 已确认五页就 63.2 万" is slightly off (63.2万 = 五页+K11). Report §1.2 line 49 says "已知五页即 ≈ 63.2 万" and line 51 "仅 TILING 已确认的五个 webtoon 页就超过…50 万". budget-register says "even counting ONLY the five TILING-cleared webtoon pages (632k)". So both places mislabel the 63.2万 as the five pages alone. Correctly it's 61.7万 for the five, 63.2万 including K11's 13 regions. Since the known_regions map in budget-register includes K11: 13 and K19: 0 and the region_total_range 881 = 521+360 uses 521 (incl. K11), the mislabel is a real (if small) numeric-attribution error. Both numbers exceed 500k so the conclusion holds. → P4 finding (precision/attribution), file:budget-register.json:40/45, ko-rerun-report.md:49/51, quality-report.md:208.

Good, that's a concrete verified finding.

Let me also verify "881-1721" = 521 + (360..1200)? 120–400×3 = 360–1200 ✓. And known_only 632000 in the JSON (rounded from 632,494) ✓.

Another verification: report §1.2 table says "已知 region 数 K01=180、K02=93、K04=113、K05=62、K08=60 + K11=13 + K19=0" = 521 ✓.

Now the "成本实际 ≈347 请求 ≈20.4万" vs budget-register 197/119k + un-metered ~140. Let me also check: is attempt-1's request count "~140" documented anywhere with evidence? budget-register says "K02 attempt-1 partial ~140 requests additional, un-metered, killed by the harness timeout". Since attempt-1 was killed during Run2 ~80/93, and Run1 completed (93 requests) + Run2 ~47 = ~140 ✓ plausible. OK.

Now: "N7 ZCode 后台 Bash 任务 ~58 分钟被宿主强杀（exit 137）" — Windows exit 137? On Windows, 137 is not typical; the harness note says killed processes settle as exit 1. The report says exit 137 (128+9 = SIGKILL, a Unix convention). Minor: the log evidence is at `ko-rerun-logs/K02-rerun-attempt*.log` — but those logs live outside the repo (task-envs), so they're not in the diff → NOT_VERIFIED (artifact not in the repo). Indeed LOG_ROOT = G:\CODEX\New Manga.task-envs\M2-TA3-B\ko-rerun-logs — outside the worktree. The report cites `ko-rerun-logs/K02-rerun-attempt*.log` as evidence for N7 and the driver writes `K11-driver-result.json` there too. So N7's evidence and the driver's result file are OUTSIDE the repo → not part of the deliverable; the claim is unverifiable from the repo. That's a P3 finding: evidence for N7 (and the driver result) is not in the archived surface; move/register it (like the API outage window which is at least summarized in budget-register).

Similarly the API-outage evidence: probes logged only to the driver log (outside repo); budget-register records the window. The outage classification rests on the 46 typed errors in qual-K02.json ✓ (in-repo) + probe times (out-of-repo). Acceptable but note.

Now, let me check `ko-rerun-pixels` outside repo: the export PNGs are outside the repo (task-envs), consistent with first-run precedent (pixels out of repo, registered in summary paths). The first-run review noted "像素出库 P3/P4". Fine — precedent.

Now NOT_VERIFIED items (integrator):
1. Git-level: branch tip commit 0001d68c exists; diff completeness (fork→tip); no uncommitted changes in the worktree; no forbidden-path commits beyond review-input.diff.
2. First-run artifacts byte-unchanged (esp. phase2/ocr/svg-gt-K11.json, svg-gt-K19.json, cer-regions.csv, quality-thresholds.md) — hash compare the ko-rerun copies vs the first-run originals.
3. Key zero-plaintext: run the same grep sweep over the full checkout (and confirm no key in worktree scratch/untracked files).
4. Kill switch/none.
5. Re-run the similarity script to confirm K11-similarity.json reproduces (deterministic, offline) — cheap and valuable.
6. Confirm `--determinism-track` requirement status (was it ever implemented/registered as a gap?).
7. Verify that `--meter-translation` off path is byte-identical (could run a tiny harness test or diff the two functions' behavior) — I verified by reading; integrator can confirm no behavioral delta e.g. via a unit-level check.
8. Confirm the ko-rerun copies of SVG GT are identical to the first-run originals (I couldn't diff in sandbox).
9. Test suite impact: no src/test changes → expect no change; integrator to confirm the tree's test suites unaffected (sanity).

Now, let me also confirm whether the `simplify`/duplicate issue on `translations_by_reading_order`: it checks `set(t1) != ros1` → requires translate_details to cover ALL regions. For K19 (0 regions), NO_DATA. Fine.

One more potential finding: `ko_rerun_similarity.py` compares qual-K11.json (main pass) with qual-K11.rerun.json. But per thresholds §5 the calibration is about the *same* case run twice. Main pass vs rerun pass ✓ (two independent runs). ✓

Another: the gate uses the same first/second ordering; fine.

Another potential issue: the report §4 says "13 对对齐校验全过（13 reading_order 集合相等 + 逐对 bbox 逐字段一致 + translate_details 全覆盖）" ✓ script enforces.

Let me now also double-check the claim "K11 同型复现（run1 completed→completed_with_failures=PRIMARY 语义定稿预期差异）" — N3 ✓ verified as plausible with strong doc support (PRIMARY handoff line 16: page-level decision chain retired for all regions).

Now — one thing I should double check: the first-run K11's run1 steps were page-level (9 steps) while the rerun's are region-level (66). The first run was at f99a6c55, which is BEFORE BACKFILL-MULTIREGION (base f99a6c55 is BACKFILL's base!). Indeed BACKFILL's task doc: "基线 f99a6c55=574+2sk". So the first run's src was the f99a6c55 tree ✓ → page-level chain. The rerun at 87f61d8b includes BACKFILL+PRIMARY → region-level chains ✓✓. This strongly confirms the N3 attribution mechanism. Excellent.

Now let me examine one more claim in the handoff: "K02 Run2（93 region 独立链）3742.0s" and "K02 试算全链完成" ✓.

Another claim in handoff table: "AC4 相似度 | driver step3（--rerun-check K11）+ step4" ✓.

Another: handoff "评测：ko G1 CER n=6 median 0.0556 PASS 6/6 行与首跑逐位一致（OCR 层跨 run 确定性再证实）" ✓ verified above. But the report's explanation of *why* K11's OCR matches under TILING (h/w=1.383 < 4.0 → tiling off) is absent (item E). I verified: K11 = 1200×1660 (in the summary stages.source). So I can state the correct explanation and recommend adding it. That's finding P3 (E axis): the "OCR 跨 run 确定性再证实" claim rests on the implicit fact that K11 did not enter the tiling path; the report should state h/w=1.383<4.0 (TILING trigger) → same detect/OCR path as the first run, else the "re-confirmation under TILING" wording is misleading (it wasn't tested under tiling). Note the report's phrase "在 TILING+新语义链下再次证实" could be read as evidence that tiling preserves OCR — which it doesn't show. That's a genuine accuracy issue worth P3.

Hmm, actually is it misleading? "OCR 层跨 run 确定性在 TILING+新语义链下再次证实" — since K11 isn't tiled, "TILING+" adds nothing for K11. Yes, mildly misleading. P3.

Now let me look at whether the report/handoff documents the K11 h/w explanation anywhere. Grep for "4.0" in ko-rerun-report.md gave nothing (earlier grep for 4\.0 in the TILING dir). Let me grep the report for "1660" or "tiling".

Let me do a final few greps: report for "tiling"/"阈值"/"4.0"; and check the handoff for the same.
dsh: reasoning:
Confirmed: no mention of the K11 h/w ratio / non-tiling explanation anywhere in the report or handoff.

Also note the handoff table line 25 says "环境与被测 commit … @ 36971e97" while line 3 says the delivery head is 36971e97 and the worktree tip is 0001d68c (docs). The rerun ran at 36971e97 — the implement commit. So the "被测 commit" is 36971e97 ✓. Fine. But: the artifacts were produced BEFORE the docs commit; the review target tip=0001d68c is docs-only, so artifacts correspond to 36971e97 ✓.

One more check: the handoff says the driver ran the K11 set "在恢复窗口内完成（21:33–21:37Z）" — but qual-K19.json started at 20:21Z and K02 at 17:37 (per budget-register pilot window 17:37-20:10 local +0800... hmm, it says "pilot window 2026-10-01T17:37-20:10 local +0800" but also "generated_at_utc: 2026-10-01T21:00Z". The api_outage_window says "observed_from K02 Run2 region ~47 onward"; probe_1 "2026-10-01T20:40Z+0800" — that's a mixed notation ("Z" and "+0800" both!). E.g., "probe_1": "2026-10-01T20:40Z+0800" is not a valid ISO timestamp; it's ambiguous (20:40Z or 20:40+0800?). Similarly "recovered": "2026-10-01T21:27Z driver probe attempt 1 OK (after ~115 min outage); K11 minimal set ... executed 21:33-21:37Z". And the report §1.3 says "故障窗 ≈ 115 分钟（2026-10-01 ~19:30–21:27 +0800）" — while saying 21:27 +0800 elsewhere. Hmm: if the outage is 19:30–21:27 +0800 = 11:30-13:27Z, that's 117 min ✓ 115 min. But summaries' UTC timestamps: K02 started? K19 started 20:21:11Z. If the outage was 11:30–13:27Z, then K19 at 20:21Z is way after. And K11 main pass finished 21:33:01Z. So the report's "+0800" claim (19:30–21:27 +0800) is inconsistent with the summaries' UTC stamps if the UTC labels are right: K11 ran 21:30-21:33Z, and the outage recovery at "21:27Z" ✓ consistent with the driver log in Z. So the outage was ~19:30Z–21:27Z (≈117 min) and the report's "(2026-10-01 ~19:30–21:27 +0800)" mislabels the timezone. Also budget-register "generated_at_utc": "2026-10-01T21:00Z (pilot window 2026-10-01T17:37-20:10 local +0800)" — if pilot window is 17:37–20:10 +0800 = 09:37–12:10Z, that contradicts generated_at 21:00Z and K19's 20:21Z start. So the local/UTC labels are muddled in both the report and budget-register (the same wall-clock range is variously tagged Z and +0800). Net effect: a ~8h ambiguity in the event timeline; the outage duration (~115 min) is internally consistent either way, but the absolute window is not auditable.

Is this worth a finding? The review item list doesn't ask about the timeline, but "诚实登记 environment" is part of the report. It's a concrete, verifiable precision defect: mixed timezone suffixes ("2026-10-01T20:40Z+0800" is malformed) and a window that cannot be reconciled with the summaries' UTC stamps (K19 20:21Z ran before the "19:30" outage start if read as +0800... hmm). Let me carefully reconstruct:

Facts from in-repo artifacts (UTC):
- qual-K19.json: started 2026-10-01T20:21:11Z, finished 20:21:19Z.
- qual-K11.json: started 21:30:47Z, finished 21:33:01Z.
- qual-K11.sfx: ?
- qual-K11.rerun.json: finished ~21:36 (wall 110.71s).
- rerun-compare.json updated_at 21:36:58Z.
- qual-report.json (K11 driver) finished 21:36:58Z.
- qual-K02.json: need started_at. Let me check: budget-register says run2_elapsed 3741.97s, wall 5591.56s. If K02 wall ended around 20:10 (since K19 started 20:21Z → K02 must have finished before 20:21Z), then K02 started ~18:37Z and the outage (region ~47 of run2) ~19:30Z → outage 19:30Z–21:27Z = 117 min ✓✓.

So the correct reading is UTC: K02 18:37–20:10Z, outage window ~19:30–21:27Z, K19 20:21Z, K11 21:30–21:37Z. The report's "+0800" tag on "~19:30–21:27" is wrong (should be Z/UTC), and budget-register's "local +0800" tag on "17:37-20:10" is also wrong (should be UTC: 17:37–20:10Z). So both artifacts mislabel UTC as local +0800 in a few places, and one timestamp is malformed ("20:40Z+0800"). Duration is unaffected (115-117 min) and the classification (environment) is unaffected. Severity: P4 (evidence-grade precision; forbids an external auditor from reconciling the window). I'll file it as P4 with file:line.

Let me verify qual-K02.json's started_at_utc to confirm.
dsh: reasoning:
Confirmed: K02 18:42:13Z → 20:15:25Z (wall 5591.56s ✓). K19 20:21Z. K11 21:30:47Z→21:33:01Z. K11.rerun 21:35:07Z→21:36:57Z.

So the pilot window is 18:42–20:15 UTC, not "17:37-20:10 local +0800" (which would be 09:37–12:10Z). And the outage ~19:30–21:27Z. Findings:
- budget-register.json:4 `generated_at_utc: 2026-10-01T21:00Z (pilot window 2026-10-01T17:37-20:10 local +0800)` — the pilot window per the summary is 18:42–20:15Z; the "17:37–20:10 +0800" label doesn't match either UTC or +0800 interpretation (17:37+0800 = 09:37Z). Actually 17:37 +0800 → if the author meant local wall clock 17:37 = 09:37Z, contradiction. Possibly the author wrote local times of a *different* attempt? The killed attempt-1! Attempt-1 (killed at 58 min) might have been 17:37–18:35 local... Hmm, if local +0800 and the killing happened... Actually, N7 says the first K02 attempt was killed after ~58 min; attempt-2 = 18:42–20:15Z = 20:42–22:15 +0800 local. Hmm, 17:37 local = 09:37Z — too early. But if the "pilot window 17:37-20:10" were actually Z (i.e., the author's local clock reading of the attempt-1 start and attempt-2 end?) Hmm: attempt-1 could have started 17:37Z and been killed at 18:35Z, then attempt-2 18:42–20:15Z. That fits! 17:37Z start of attempt-1 → killed ~58min later at ~18:35Z; attempt-2 18:42–20:15Z; total recorded window 17:37–20:10Z (≈ attempt-1 start to attempt-2 end). So "17:37-20:10" is UTC, mislabeled as "local +0800". 
- report §1.3 "故障窗 ≈ 115 分钟（2026-10-01 ~19:30–21:27 +0800）" — 19:30–21:27 is UTC (consistent with the summaries), mislabeled +0800.
- budget-register api_outage_window probe_1 "2026-10-01T20:40Z+0800" malformed; probe_2 "2026-10-01T21:05Z+0800" malformed. Also probe_1 at 20:40Z doesn't make sense as an outage probe if the outage ended 21:27Z... it does (probes during outage: 20:40Z, 21:05Z, recover 21:27Z) ✓. But wait: K02 finished at 20:15:25Z and the outage was observed from Run2 region ~47; region ~47 of Run2 — Run2 started around... K02 started 18:42:13Z; run1 1848.5s → run1 ended ~19:13Z; run2 3741.97s → ended ~20:15Z. Run2's failure onset at region ~47 ≈ after 47/93 of 3741s ≈ 19:13+1890s ≈ 19:44Z ✓ consistent with "~19:30Z". Then probes at 20:40Z and 21:05Z (after K02 ended), recovery 21:27Z ✓, K11 at 21:30Z ✓. All internally consistent in UTC. So only the "+0800" labels are wrong (3 places) plus the malformed "Z+0800".

Severity: P4 (documentation/precision; no impact on classification or duration). I'll file it.

Now let me consider whether "45×PROVIDER_TIMEOUT + 1×INVALID_OUTPUT ... 无重试风暴" is right: with max_attempts=2 each failure means 2 HTTP attempts → 92 attempts over ~100 min for 46 regions = ~1 attempt/min — clearly no storm ✓. Claim holds.

Now let me assemble everything. Let me also double check one claim I flagged: the report's §0 AC5 "两次 K02 全链" — attempt-1 + attempt-2 = two K02 full chains? Attempt-1 was killed before completing (during Run2 ~80/93), so it's not a full chain. It says "两次 K02 全链 + K11×3 + 自评/探针" in the report §5? Actually report §0 AC5: "实际消耗 ≈ 347 次成功请求 ≈ 20.4 万 est token（两次 K02 全链 + K11×3 + 自评/探针；估算口径见 §1.1）". Attempt-1 was NOT a full chain (killed at Run2 80/93). So "两次 K02 全链" is inaccurate; budget-register correctly says "K02 attempt-1 partial". Minor P4.

Also "K11×3" = main + sfx + rerun ✓.

Now let me also double-check the "140 请求全部 1 target region/请求（Run1 也逐 region 非整页批量）" — I've established:
- K02: metered 140 total (both runs), all n_target_region_calls == 140 → every metered call carried exactly 1 region ✓ (verified in qual-K02.json translation_metering: requests 140, n_target_region_calls 140).
- K11: 19/19 ✓ (also 1 region per call).
So "每 call 1 region" is verified for both ✓. The split Run1=93/Run2=47 is inferred (93 translate steps in run1 ✓ verified from step list; 47 = region_runs 93 - 46 failures ✓). So actually Run1=93 IS directly evidenced by run1.steps (93 translate steps) — hmm, I counted ~93 from grep but didn't count exactly. Let me count the K02 run1 translate steps precisely by reading the boundaries: run1 spans lines ~76-5674; run2 starts at 5675. The grep listed translate step lines; those before 5676: let me count them precisely from the earlier grep output list.

From the grep output, matches before line 5676:
125,155,233,263,275,365,467,575,581,605,641,
701,755,803,851,959,1007,1037,
1193,1205,1241,1265,1361,1385,1391,1421,1433,1457,1475,
1565,1595,1619,1655,1661,1757,1823,1871,1901,1913,1937,1943,1949,2015,2033,
2261,2321,2333,2375,2381,2435,2495,2603,2621,2645,
2771,2801,2873,2903,2909,2921,3041,3155,3167,3179,3251,3263,3359,3371,3443,3533,3563,3695,3743,3767,3785,3845,3953,3983,4025,4085,4217,4223,4247,4271,4319,4325,4343,4397,4463,4469,4475,4523,4547,

Let me count: 
Group1 (11): 125,155,233,263,275,365,467,575,581,605,641
Group2 (7): 701,755,803,851,959,1007,1037 → 18
Group3 (10): 1193,1205,1241,1265,1361,1385,1391,1421,1433,1457 → 28
+1475 → 29
Group4 (15): 1565,1595,1619,1655,1661,1757,1823,1871,1901,1913,1937,1943,1949,2015,2033 → 44
Group5 (9): 2261,2321,2333,2375,2381,2435,2495,2603,2621 → 53
+2645 → 54
Group6 (13): 2771,2801,2873,2903,2909,2921,3041,3155,3167,3179,3251,3263,3359 → 67
+3371 → 68
Group7 (8): 3443,3533,3563,3695,3743,3767,3785,3845 → 76
Group8 (8): 3953,3983,4025,4085,4217,4223,4247,4271 → 84
Group9 (6): 4319,4325,4343,4397,4463,4469 → 90
Group10 (4): 4475,4523,4547 → 93. 
Wait I need to be careful: I listed 4319,4325,4343,4397,4463,4469,4475,4523,4547 = 9 → 84+9 = 93 ✓.

So run1 has exactly 93 translate steps → 93 translate calls in Run1 ✓✓. That verifies Run1 = one call per region for K02 (93/93), and thus the "Run1 逐 region 非整页批量" claim IS directly supported for K02.

But then K11's run1 = 8 calls for 13 regions is a genuine anomaly that contradicts the generalization "请求数 ≈ 2×region 数" (K11 full-chain would be 8+13=21 = 1.6×, not 26). So my finding stands: the model over-generalizes; the K11 data in the same run contradicts it (Run1 emitted fewer calls than regions). Nobody explained why K11's run1 made only 8 calls. This is worth P2 because the cost model drives the stop decision AND the K11 anomaly is unreported despite being in the same metered dataset.

Hmm, one candidate explanation to include: dedup/caching of identical source text. K11's 11 text regions include duplicates (당근아? ×2, 당근아! ×2 → 9 distinct?) — 8 ≈ close to but not equal. Another: the primary region handling. I shouldn't speculate in the finding; I'll just state the facts and that the cause is unexplained, and note the upper-bound framing.

Wait, actually — maybe I should double check the K11 rerun (qual-K11.rerun.json) translate step count for consistency: also 8? If the rerun also shows 8, it's systematic. Let me grep the rerun summary for translate step count. Also, does the K11 main pass have 8 in run1? Yes (I read it).

Let me check the rerun file count quickly.
dsh: reasoning:
Consistent: all three K11 passes have exactly 8 run1 translate steps → 8 + 11 = 19 metered calls. So K11's Run1 systematically emits 8 calls for 13 regions (11 text). Systematic, reproducible, and *unexplained* in the report. Meanwhile K02's Run1 emits 93 = region count. This is a genuine, reproducible discrepancy in the cost model's core multiplier that the report presents as a measured structural law ("请求数≈2×region 数（Run1 一轮 + Run2 一轮，§1.1 实测结构）").

Hmm, hold on. Let me reconsider: for K02, is the 93 truly Run1 = one call per region, or could it be Run1 = 47 and Run2 = 93? Run2 = 93 calls (region_runs_executed 93) with 46 failures → 47 successful → metered Run2 successes = 47. Total metered = 140 → Run1 = 93. But the step list shows 93 translate steps in run1 AND (5676-9319, run2 section) 48 translate steps (47 completed + 1 failed INVALID_OUTPUT — from grep: 48 entries between 5821 and 7316). Let me recount run2 translate entries: from the grep output after 5676: 5821,5970,5989,6032,6063,6082,6119,6144,6181,6200,6249,6268,6299,6324,6367,6398,6435,6454,6491,6516,6541,6572,6621,6640,6665,6708,6745,6776,6801,6826,6857,6882,6925,6956,6993,7012,7043,7080,7099,7130,7167,7192,7229,7254,7297,7316 = count: let me count in groups of 10: (5821..6200) = 10? list: 5821,5970,5989,6032,6063,6082,6119,6144,6181,6200 = 10; (6249..6572): 6249,6268,6299,6324,6367,6398,6435,6454,6491,6516 = 20; (6541,6572,6621,6640,6665,6708,6745,6776,6801,6826) = 30; (6857,6882,6925,6956,6993,7012,7043,7080,7099,7130) = 40; (7167,7192,7229,7254,7297,7316) = 46. So run2 has 46 translate step entries — which correspond to the 45 TIMEOUTs + 1 INVALID_OUTPUT = 46 *failed* translate steps! But then the 47 *successful* run2 calls did NOT produce translate steps?? Hmm, that contradicts. Unless the successful run2 calls also produce steps but the grep output was capped... The grep reported "Found 141 matches" total. Let me recount total: run1 93 + run2 46 = 139, but the tool said 141 matches. Hmm, my counts are rough (I may have mis-grouped). Let me not over-analyze; the tool said 141 matches total which is under the 250 cap, so it's complete. 141 = run1 X + run2 Y. If run1 = 93 and run2 = 48 → 141 ✓ (48 = 47 successes + 1 invalid output; the 45 timeouts... hmm that gives 93+48=141 but then the 45 timeouts produce no translate step while the 1 invalid output does? Odd but plausible if INVALID_OUTPUT happens *after* a response is received (so a step is created) while TIMEOUT aborts before step creation... Actually no: the failed step would be recorded in both cases.

Alternatively run1 = 93 - 45? Ugh.

Hmm, let me test another decomposition: run1 = 93, run2 = 48: the 45 timeouts might not produce a translate step because the step creation happens... Hmm. Or run1 = 48, run2 = 93: then run1 = 48 calls for 93 regions?? That'd be weird given run1 = page-level chain with 93 regions; but run1's translate steps are located at lines 125-4547 (all before 5676) — I counted 93 of them there. So run1 = 93 (the 93 lines I counted before 5676 = 93 exactly, close enough) and run2 = 48 (lines after 5676), totaling 141 ✓ if my run1 count was 93 and run2 count 48. But my run2 count was 46 by grouping. Let me just accept ±2 uncertainty; the qualitative point stands: run1 ≈ 93 region-level translate steps for K02, verifying per-region calls in Run1 for K02; and for K11 (all three passes) exactly 8 run1 translate steps vs 13 regions.

Hmm, wait. Now I realize I should double check the K11 run1 8 more carefully — could there be translate steps in run1 for K11 beyond line 490? The run1 object spans lines 76-490 ("run1": { ... } ends at line 490 with "}," and then "regions": [ at 491). All 8 translate entries (190,244,382,412,418,442,466,484) are within 76-490 ✓. And grep over the whole file found only 8 → run2 section (649-764) has no translate step list. So run1 = 8 confirmed.

So: K11 run1 = 8 calls; run2 = 11 successful calls (13 regions - 2 failures); metered 19. Confirmed.

Interesting: 8 = 11 text regions - 3. Hmm, K11's 13 regions: 11 speech-ish with text + 2 empty. Of the 11, duplicates: 당근아? (ro1 and ro3?) — from the similarity JSON: ro1 당근아?, ro2 당근아!, ro3 당근아?, ro4 당근아?!, ro7 어라?..., ro6 당근아?!!!, ro8 당근아!, ro10 크록브록크록..., ro11 오 나의..., ro12 꼬르를 — that's 10 + ro5 (이렇게까지는) = 11... wait ro9 is empty. So 11 non-empty? similarity JSON lists 13 pairs, 2 empty (ro9 speech empty, ro13 sfx empty) → 11 non-empty. Duplicates among the 11: 당근아? ×2 (ro1, ro3), 당근아! ×2 (ro2, ro8) → distinct texts = 9. So 8 ≠ 9. Hmm.

OK. So the K11 run1 call count (8) doesn't match either 11 (text regions) or 9 (distinct texts). Whatever the mechanism (maybe a page-level batch that groups some regions... but n_target_regions per call is always 1!), it's unexplained. I'll present it as a factual inconsistency requiring explanation, and note that the 2× multiplier is therefore an upper bound assumption, not a measured law. This is the strongest technical finding of my review. Severity: I'd say P2 (the report's central cost model and its headline "五页即超线" rest on it; the same run's K11 data contradicts it and isn't registered).

Now, let me estimate the impact if the K11 pattern generalizes: 521 regions → run1 calls ≈ 521×(8/13)=321 + run2 521 = 842 calls → ×607 = 511k — just above the line! Interesting. And using K02's run1 ratio (1:1) + run2 1:1 → 2×. And a mixed estimate would put known-only right around 50万. So the stop is still defensible but the margin is thin — worth stating.

Hmm, but careful: K11's Run1 = 8 calls for 11 text regions vs K02's Run1 = 93 calls for 93 regions. Why? Because K02's regions are all distinct texts? Then K02's Run1 dedup wouldn't reduce. K11 has only 2 duplicate pairs, which would give 9, not 8. So dedup alone doesn't explain it. There might be something else: maybe run1's translate step count for K11 is 8 because 3 regions' translate happened *within* another step type... Honestly unexplained.

Actually — wait. Let me reconsider: maybe run1 for K11 processed only 8 regions because the page-level chain's "run1_page_selection" selects a subset of regions for the page-level pass (the stage name IS "run1_page_selection"!). For K02, why 93 then? Hmm, maybe there's a cap/batch: e.g., the page-level pass processes at most ~8 regions per page in one batch? No, K02 had 93.

Whatever. The point stands: unexplained, unreported, and it breaks the "2×" generalization. I'm confident this is a good finding.

Let me now also sanity check the claim in the report §1.1 note: "全部为估算，非 endpoint 计量数据" ✓.

One more thing to check for item 6: does the metering proxy record input tokens for the retried attempts? No (only the successful call). And is `estimate_tokens(TRANSLATION_SYSTEM_PROMPT)` a good proxy for the system prompt? Yes, disclosed.

I think I have enough. Let me also quickly verify the "no changes to forbidden paths" at the *diff* level by listing all files in the diff (24 entries). From my earlier grep of "^diff --git", the files are:
1. doc/handoffs/M2-TA3-B2-KO-RERUN-36971e97.md (new)
2. doc/tasks/M2-TA3-B2-KO-RERUN.md (modified)
3. experiments/M2-TA3-B/ko_rerun_k11_driver.py (new)
4. experiments/M2-TA3-B/ko_rerun_readability_increment.py (new)
5. experiments/M2-TA3-B/ko_rerun_similarity.py (new)
6. experiments/M2-TA3-B/run_qualification.py (modified)
7. verification/M2-TA3-B/ko-rerun-report.md (new)
8. verification/M2-TA3-B/phase2/ko-rerun/budget-register.json (new)
9. .../determinism/K11-similarity.json (new)
10. .../ocr/cer-regions.csv (new)
11. .../ocr/cer-summary.json (new)
12. .../ocr/svg-alignment-trace.json (new)
13. .../ocr/svg-gt-K11.json (new)
14. .../ocr/svg-gt-K19.json (new)
15. .../summaries-sfx/qual-K11.sfx-translate.json (new)
16. .../summaries-sfx/qual-report.sfx-translate.json (new)
17. .../summaries/qual-K02.json (new)
18. .../summaries/qual-K11.json (new)
19. .../summaries/qual-K11.rerun.json (new)
20. .../summaries/qual-K19.json (new)
21. .../summaries/qual-report.json (new)
22. .../summaries/rerun-compare.json (new)
23. .../translate/dialogue-readability-ko-increment.csv (new)
24. verification/M2-TA3-B/quality-report.md (modified, §10 appended)

All within the allowed surface ✓. No src/tests/contracts/packaging/apps/STATUS/thresholds ✓ (quality-thresholds.md untouched ✓ — important since §7.3 hands the Gate caliber ruling to the user, correctly not modifying thresholds).

Note: `verification/M2-TA3-B/phase2/**` is allowed ✓ (ko-rerun under it).

Now, one more finding candidate: the sfx-translate pass wrote `summaries-sfx/qual-report.sfx-translate.json` etc. — fine.

Another: `qual-report.json` in summaries/ is overwritten by the last invocation and now only lists K11 (skipped: true) with "failures": 2, losing the K02/K19 roll-up. The handoff cites `qual-report.json` nowhere as evidence for K02/K19, but a reader looking for the consolidated report will see only K11. Also, "skipped": true for K11 in the final qual-report is confusing (it was the rerun-check invocation that skipped the main pass). And "failures": 2 — what does it mean? Let me check run_qualification.py's definition of "failures" to assess whether 2 is meaningful (probably count of case-level failures). For the K11-only rerun pass, failures=2 is odd (K11 is skipped). Let me grep.

This is a real auditability finding (P3): the consolidated roll-up artifact is clobbered/stale. Let me verify the semantics of "failures" in the runner.
dsh: reasoning:
`report["failures"]` counts case-level/rerun failures in that invocation. For the final invocation (rerun-check only), failures=2 presumably counts K11's pipeline failure + something. Actually the final qual-report.json lists cases=[{K11, skipped:true, pipeline_completed:false...}] and rerun=[{K11 ...}] with failures=2. So failures=2 = the skipped case's pipeline_completed false (counted as failure?) + the rerun mismatch? Line 905/920/939/1028 contexts unknown. Anyway, the semantics is "this invocation's failures", not the accumulated run. The key point: the summaries/qual-report.json is the LAST invocation's report (K11 rerun-check), so it is NOT a consolidated record of K02+K11+K19; the report/handoff never flags this, and a reader could mistake `qual-report.json` (in the ko-rerun summaries dir) for the run-level roll-up (as the first-run one was). This is an auditability/P3 finding (artifact naming/clobbering). Recommend: keep per-invocation reports named by suffix, or add a run-level index.

Hmm, but actually in the first run, qual-report.json was the single consolidated report. Here, since multiple invocations share --out-dir, the file is clobbered. The report §0 doesn't cite qual-report.json. It's a minor but real hazard. P3.

Alright. I also want to double check one of the "Owner claims" — "SFX 主 pass n=1 translated=0（SKIP）" ✓ from cer-summary sfx_translation_stats (n_sfx_regions 1, n_translated 0) ✓.

Now, let me reflect on whether there are any P0/P1 findings. I don't see any: no forbidden-path changes, no key leakage, no fabricated numbers that I could detect (all numbers I spot-checked reproduce), fail-closed behavior honest, Gate FAIL reported honestly, stop decision conservative. So verdict: APPROVE (approve with findings) or "changes_requested" (conditional)? The review conventions in this repo: verdicts like `approved`, `changes_requested`, `approved_subagent`. Given no P0/P1 and findings are documentation/precision/method-disclosure level, the honest verdict is **approved with registered findings (R1–R9)** — but two findings rise to P2 (the 2× cost-model generalization + the missing `--determinism-track` fail-closed control, and the 50万 line provenance). Are P2s blocking? In this repo, P2s sometimes are "有条件通过（0×P0/P1，2×P2 文档/口径级由集成方闭合）" (as in PRIMARY-SFX-GATE). So the precedent supports "有条件通过：0×P0/P1，P2 为文档/口径级，由集成方闭合后集成".

Which P2s do I have?
- R1 (P2): 50万红线出处不可核（与 phase2-plan.md:192 的「≤数万 token 量级」纪律冲突，Task 书无该数字）→ 需登记用户/编排指令原文或改写口径。
- R2 (P2): 成本乘数 "≈2×region" 被表述为实测结构，但同一 run 的 K11（19 calls/13 regions；Run1 仅 8 calls）与之矛盾且未登记 → 影响"仅五页即超线"的表态（用 K02 自身 1.5× 口径则已知页 ≈47.6 万 < 50 万；用 K11 的 1.46× 更低）。停跑结论在含 K07-10 时仍成立，但该表态需改为上界假设+敏感性。
- R3 (P2): thresholds §5/CALIB 要求的 `--determinism-track remote|mock` 显式记录 + 不一致 fail-closed 未实现（runner 无该参数），本次以散文声明轨道替代 → 口径控制缺失。
- R4 (P2 or P3): N7/驱动证据在仓库外（ko-rerun-logs），且 `K11-driver-result.json` 未入库 → 事件登记不可复核。Hmm, this is P3-ish. I'll make it P3.

So 2-3 P2s. Verdict: 有条件通过 (approved_with_findings) — integrator closes documentation/caliber items. I'll write it as "有条件通过（changes_requested 不成立；0×P0/P1、3×P2 文档/口径级，由集成方与 Owner 闭合后集成）". Hmm, but I must pick one clear verdict per the requested format. The repo's review template likely has verdict values. Let me check doc/templates/REVIEW.md quickly to use the right vocabulary.

Let me read the review template.
dsh: reasoning:
Verdict vocabulary: pending / changes_requested / approved / blocked. With no P0/P1, and P2s that are documentation/caliber-level (per repo precedent: "DSH r1 有条件通过（0×P0/P1，2×P2 文档/口径级由集成方闭合）→ 集成"), I'll give **approved（有条件）**: the head can go to integration provided the integrator closes the P2 documentation/caliber items (or explicitly registers them as deferred). Hmm — "批准门槛：P0/P1 未解决或关键验证缺失时不可批准". I have no P0/P1, but I do have NOT_VERIFIED items (runtime/git checks). The prompt says NOT_VERIFIED is left to the integrator. So: **approved（0×P0/P1；3×P2 文档/口径级 + NOT_VERIFIED 交集成方闭合）**.

Now let me finalize the findings list with precise file:line references.

R1 (P2) 50万红线出处不可核
- doc/tasks/M2-TA3-B2-KO-RERUN.md:29,39-43（AC5/纪律节无「50 万」字样；纪律仅"预估请求数/先行一个 case 试算后再全量"）
- verification/M2-TA3-B/phase2-plan.md:192（现行仓库纪律=「预估总 token 数万 token 量级，超预期即停并登记」，且该行明确记载 r2 N6 曾把口径写成「数十万以内」被判越界改写后回退）
- 报告/登记把 50 万称为"任务纪律/task brief"：ko-rerun-report.md:15,51；budget-register.json:45,57；quality-report.md:208
- 影响：停跑本身是保守方向（纪律的任何读法都支持停），但"红线"是本次核心决策依据，仓库内无可核出处，且与现行文字相差约 50×；不落盘出处则后续补跑授权口径不可审计。
- 建议：把用户裁决③/编排指令中该 50 万（或其它数值）原文落盘到 Task/报告（引用哪条裁决），或改用 phase2-plan.md:192 的口径重新表述。

R2 (P2) 「请求数≈2×region 数」被表述为实测结构，同 run 的 K11 反例未登记
- 表述处：ko-rerun-report.md:37,48；budget-register.json:16,38-39；quality-report.md:208
- 反例（本次 run 内、已计量）：K11 三个 pass 的 run1 均恰 8 个 translate step（qual-K11.json:190/244/382/412/418/442/466/484；qual-K11.rerun.json:88-400；qual-K11.sfx-translate.json:104-470），而 K11 有 13 region（11 有文本）；计量 requests=19、n_target_region_calls=19（qual-K11.json:1062-1070）→ 19/13=1.46×，Run1 8<11
- 对照：K02 run1 恰 93 个 translate step（qual-K02.json:125…4547，run2 起于 5676）→ Run1 1:1 region（这一条支持"Run1 非整页批量"）
- 影响：2× 只对"两轮都逐 region 全覆盖"的假设成立。用 K02 自身计量比 140/93=1.505（含 46 失败的门限压低）或 K11 的 1.46，则"仅已确认页即超线"的 63.2 万会降到约 47–48 万（521×1.5×607≈47.6 万）——即"五页即超线"在乘数上不稳健（含 K07-10 时任何组合仍超线，停跑结论不变）；Run1 何时少发请求的机制完全未解释（非 duplicate-text 可解释：K11 去重后仍有 9 个不同文本）。
- 建议：①把 2× 明确写成上界假设（含带 K07-10 的 107–209 万为区间结论）；②补一行敏感性（1.5× 时已知页≈47.6 万）与"K11 Run1 8 次调用"的异常登记/机制结论。

R3 (P2) 双轨判轨的可执行控制（--determinism-track + 不一致 fail-closed）未实现
- 要求出处：quality-thresholds.md:172（"qualification runner 以 --determinism-track remote|mock 参数显式记录所选轨道，声明与 provider 绑定不一致时 fail-closed 报错"）；verification/M2-QUAL-DETERM-CALIB/integration.md:8
- 现状：实验层 4 个脚本全文无 track 参数（experiments/M2-TA3-B/*.py 无 "track" 定义）；判定写在 JSON 散文 note（K11-similarity.json:169）与报告 §4 叙述，无 fail-closed
- 影响：本次结论（remote→相似度轨）实质正确，但口头判轨在 provider 绑定被改（例如误指 mock）时不会报错；CALIB 明确写了该机制是口径的一部分。
- 建议：run_qualification.py/ko_rerun_similarity.py 增 `--determinism-track` 并按 provider 绑定校验；或把该行登记为已知缺口（Task 允许面含 runner 微调，未做需说明）。

R4 (P3) N3 归因应点名 BACKFILL→PRIMARY 链
- 表述：ko-rerun-report.md:79（"PRIMARY Task 的 terminal accounting unified 语义"）；Task:48
- 事实核对：账目统一由 BACKFILL-MULTIREGION R1 先做（doc/tasks/M2-TASKS-BACKFILL-MULTIREGION.md:5,35-37），PRIMARY 把 primary 一并纳入并把页级决策链整体退役（doc/handoffs/M2-TASKS-PRIMARY-SFX-GATE-19bf234a.md:16,26）；首跑在 f99a6c55（BACKFILL 的 base）→ run1 步表为页级 9 步（phase2/summaries/qual-K11.json:75-135），重跑为 region 级 66 步（ko-rerun/summaries/qual-K11.json:76-490）
- 影响：结论方向正确，但"PRIMARY"单点归因掩盖了 BACKFILL 的前置作用，且未给出判别证据（哪条 unit 的失败翻转 run1 终态）。
- 建议：改写为"BACKFILL fan-out + PRIMARY primary 纳入（87f61d8b 语义定稿链）"，并引用 src/application/tasks/service.py:1054 / projection.py:336 的终态计算路径。

R5 (P3) CER「6/6 逐位一致」未说明 K11 未进 tiling 路径（口径自洽性）
- 表述：ko-rerun-report.md:97（"跨 run 确定性在 TILING+新语义链下再次证实"）；handoff:15
- 事实：K11=1200×1660（ko-rerun/summaries/qual-K11.json:26-27,44-45），h/w=1.383 ≤ TILING 触发阈值 4.0（verification/M2-DETECT-WEBTOON-TILING/integration.md:8）→ 与首跑同 detect/OCR 路径，逐位一致属预期，**不是** TILING 下 OCR 稳定性的证据；报告/交接全文无"4.0/未触发"字样。
- 影响：措辞把"同路径复现"读成"TILING 语义下复现"，会误导后续对 tiling 影响 OCR 的判断；6/6 数值本身经我逐行核对为真（见核对表 E）。
- 建议：在 §3.1 加一句"K11 h/w=1.383<4.0，未进入 tiling 路径，故与首跑同路径；tiling 路径的 OCR 稳定性本 run 未覆盖（K02 无 GT）"。

R6 (P3) 计量口径把"provider 调用"写成"HTTP 请求"，且未计 retry 倍数
- 表述：ko-rerun-report.md:37（"140 次成功请求""每次请求恰 1 个 target region"）、:19（"347 次成功请求"）；budget-register.json:16,72-74
- 事实：代理在 provider.translate() 外层记录（run_qualification.py:718-733），而 production retry 在 provider 之外（src/infrastructure/providers/fallback.py:101-130 + retry.py:96-146，policy runtime.py:92 max_attempts=2；已配置项 settings["providers"]["retry"]）——失败尝试不落记录，故 140/19 是"成功逻辑调用数"，HTTP 次数≥该值（故障窗 46 region 计 ≈92 次尝试未计），token 估算亦未计重发 input；K02 summary 无 attempt_count 字段可核。
- 影响：方向保守（低估→红线更早触发），停跑决策不受影响；但"请求数≈2×region"式成本表述与"无重试风暴"的量级证据（实际 ≈92 次尝试/~100 分钟）应说清口径。
- 建议：改称"成功 translate() 调用数"，并注明 retry 倍数（默认 max_attempts=2）与 attempt_count 未落盘为计量盲点。

R7 (P3) §7 裁决清单缺成本/影响量化与两个独立决策点
- 位置：ko-rerun-report.md:163-166
- 缺口：①选项①–④无 est token/覆盖量化（现只有 §7.2 的 K02 +113k）；按同一模型可给出：③K07/K09/K10≈360–1200 region≈44–146 万 est token，②按 N 抽样的披露口径，④0；②F1 是否可仅凭"TILING detect 5/5 + K02 全链 1/5"关闭、K01/K04/K05/K08 是否必须补页级全链——该独立决策点被"7 case 范围"吞并；③§7.3 三选项未写各自对 K11 Gate 判定的后果（维持阈值=继续 FAIL；语义度量=需新 Task/校准；登记 known-limitation=本次按 directional 接受）与成本。

R8 (P3) 事件证据在仓库外 + 汇总产物被覆盖
- N7 证据 `ko-rerun-logs/K02-rerun-attempt*.log` 与驱动结果 `K11-driver-result.json` 写在 `G:\CODEX\New Manga.task-envs\M2-TA3-B\ko-rerun-logs`（ko_rerun_k11_driver.py:154,217,263），不在交付面内 → N7（58 分钟强杀/exit 137）与"API 恢复自动执行"不可从仓库复核。
- summaries/qual-report.json 被最后一次调用覆盖，只剩 K11（skipped=true，failures=2；qual-report.json:20-41），不是 K02+K11+K19 的汇总；报告/handoff 未标注，易被误读为 run 级 roll-up。

R9 (P4) 数值/标签精度
- 「仅 TILING 五页即 63.2 万」（ko-rerun-report.md:49,51；budget-register.json:40,45；quality-report.md:208）：63.2 万=521 region（含 K11 13）算得；五页为 508 region → 61.7 万。两者都超线，但归属表述不实。
- 「实际 ≈347 次成功请求 ≈20.4 万」含未计量的 attempt-1 估算（budget-register.json:72-74 自述 197/119k + attempt-1 ~140 未计量），且把被强杀的 attempt-1 称为"K02 全链"（ko-rerun-report.md:19）——应写"估计（含未计量 attempt-1）"。
- 时间戳：budget-register.json:4（"pilot window 2026-10-01T17:37-20:10 local +0800"）与报告 §1.3（"19:30–21:27 +0800"）把 UTC 标成 +0800；实测 summary 为 18:42:13Z–20:15:25Z（qual-K02.json:14,9329）；probe_1/2 的 "20:40Z+0800"/"21:05Z+0800" 非法时间戳（budget-register.json:66-67）。115 分钟时长与 environment 分类不受影响。
- K11-similarity.json:148-151 的 n_variant=1 是 normalized<1 口径，而 pairs[].status 有 2 个 variant（ro5、ro10；ro10 raw=0.9474、normalized=1.0）——报告"12/13 逐位一致/浮动对 1"（:124-125）按 raw 口径应为 11/13 逐位一致 + 1 对仅空白差；CALIB 局限 5 要求 raw 口径附报（JSON 已逐对附 raw，正文缺注）。
- `--sfx-policy translate`"gate 放行"是推断（sfx region OCR 空、term_extract 先失败、无该 region 的 translate step；sfx 摘要 final_source=none，qual-K11.sfx-translate.json:1036-1044），应写作"按 decide_sfx_translation 语义推断放行"。

R10 (P4) 代码卫生（experiments 面，judgement calls）
- `reregister_env_resolver_metered`（run_qualification.py:226-260）是 translate_probe.reregister_env_resolver（translate_probe.py:137-196）的 40 行 fork，且**丢掉了原函数的 production provider-id 漂移守卫**（translate_probe.py:159-160）；possible Duplicated Code + 计量路径 fail-closed 强度下降。建议让 probe 帮助函数接受 factory 包装参数，或在 metered 版本保留 pid 断言。

Also the "3 脚本微调" phrasing (1 modified + 3 new) — put in checklist, not a finding (maybe mention inside R10 or checklist F).

Let me also double check R9's claim "63.2万 = 521 regions × 2 × 607" = 632,494 ✓ and 508×2×607 = 616,712 ✓.

And R2's sensitivity numbers: 521×1.505×607 = 475,876 ≈ 47.6万 ✓; 521×1.46×607 = 461,700 ✓.

Now the checklist sections A–F. Let me write them compactly with evidence line refs.

A 停跑决策:
- 红线原文: 部分成立/不成立 —— Task 书无该数值（R1）；外推假设不确定度已标注（"无先例"、"估计 120–400/页"）✓ 且区间 881–1721 与同宽 K01 密度线性外推（K07≈380/K09≈291/K10≈292，合 963）相容 ✓；停跑点选择代价最优性：可辩护（F1 已由 TILING detect 5/5 覆盖，剩余高频值项=F2 三页，而 F2 三页本身 44–146 万 > 红线，且任一"部分补跑"最小组合 —— K01 单页 218k、K04 137k —— 只能再覆盖 F1 系，收益低）→ 结论：停跑合理，但依据表述需按 R1/R2 修正。
- 具体：其他可选点（先跑 K07/K09/K10）不满足红线；K02 试算后停 + 保留 K19/K11 近零成本对照 = 代价最优。

B F1 解锁实证:
- TILING qualification 5/5 pages provider.detect region>0（K01 180/K02 93/K04 113/K05 62/K08 60）— 独立 Task GATE PASS，属 detect 层。
- 本 run K02 全链 0→93 region、export OK（qual-K02.json:53-74）、93/93 final 有译文 ✓。
- 组合链完整（detect 层 5/5 + 全链 1/5）且报告如实 scope（"该页级"、"K01/K04/K05/K08 页级实测待裁决"）。→ F1 关闭主张成立（页级+detect 级），残余=4 页全链未测（已登记待裁决）。
- Run2 46 environment 失败影响面：CER 不受影响（K02 G2 未入自动子集，ko G1 仅 K11 6 行）；翻译数据不受影响（details translated=93/93，qual-K02.json:68-69）；仅 run2 region 重翻覆盖 46/93 缺失 → 已如实登记并给出干净重跑选项（+113k）→ 隔离正确 ✓。建议补一句：Run2 缺失使 K02 无法作为"全链 pipeline_failures=0"样本（报告已说）。

C PRIMARY 差异与 K11: 归因方向正确、需点名链（R4）；K11 行为对照一致（2 空 OCR region、export OK、CER 逐位）✓；首跑/重跑 run1 步表结构差异（9 页级 → 66 region 级）是同一语义变更的直接指纹 ✓（这一条我核实到了，是加分项）。

D 相似度 Gate 自然 FAIL:
- 与 thresholds §5 口径一致（对比对象=全部对齐对含空对规则、median≥0.95 且 min≥0.70、非空 n≥1 前置；脚本 ko_rerun_similarity.py:630-638 与 §5:168 一致）✓
- min=0.4615 对（reading_order=5）的两版译文（K11-similarity.json:54-63）语义等价判定依据=Owner 自判（报告 §4:129 断言"语义等价合法重译（同义改写，非字符噪声、非漏译）"，无人工审阅/标注人/独立核对记录）——**判定依据未落盘**（P3-ish; I'll fold into a finding? The item D explicitly asks. I'll add it as R11 (P3) or fold into R9. Better: make it its own finding R... Let me add R11 (P3) 语义等价判定依据未落盘.)
- CALIB 局限 8 印证如实（calibration.md:97 原文即"语义等价的合法重译会被判低相似度 FAIL…保守方向"）✓ 首次自然实测的说法成立（CALIB 注明"无自然 FAIL 样本"、局限 8"未加同义改写代理探针"）✓
- 移交裁决表述完整性：给了 3 个候选（维持/语义度量/登记 known-limitation）但无成本/后果（folded into R7）。

E CER 逐位与计量:
- 6/6 逐位一致：我逐行核对 G1:svg_native 6 行 gt/ocr/cer 全同（ko-rerun/ocr/cer-regions.csv:95,98,99,100,101,106 vs phase2/ocr/cer-regions.csv:58,61,62,63,64,69），median 0.0556/P90 0.3333/zero 50% 复算一致 ✓；排除 7 行同口径 ✓（cer-summary.json:36-113）
- 但"在 TILING 语义下"的措辞需修正（R5）
- 计量：估算 vs endpoint usage 已显式披露 ✓（report:29、summary token_basis、budget-register:20）；行为零变更论证=代码透传+opt-in 默认关（run_qualification.py:863-869、899-909），但 (a) metered fork 丢 pid 守卫（R10），(b) 把调用数当 HTTP 请求数（R6）。

F 范围纪律与裁决清单:
- 允许面/禁改面：diff 24 文件全在允许面（experiments/M2-TA3-B/**、verification/M2-TA3-B/phase2/**、quality-report.md 追加、Task/Handoff）✓；无 src/tests/contracts/packaging/apps/STATUS/thresholds（quality-thresholds.md 未动 ✓ 与 §7.3 移交裁决一致）
- 首跑产物零改动：diff 无 phase2/首跑文件（phase2/ocr/*, phase2/summaries/* 无条目）✓（运行时/克隆副本一致性留给集成方哈希核对 → NOT_VERIFIED）
- key 零明文：diff 全文无 sk-/eyJ/密钥字面值（仅 env 名、`Bearer {key}` 运行期拼装、`$(cat …deepseek.key)` 路径）✓
- 脚本变更面表述：实际=1 改（run_qualification.py）+3 新增（用户 brief 的"3 脚本微调"与 handoff 一致但应写清 1+3）
- §7 完整性：见 R7。

Now NOT_VERIFIED (integrator runtime):
1. `git rev-parse`/`git log 87f61d8b..0001d68c` — tip/commit 拓扑、diff 完整性（review-input.diff 是否=完整 fork→tip diff）、worktree 是否 clean（无未提交残留）。
2. 首跑产物 byte 不变：`git diff 87f61d8b...0001d68c -- verification/M2-TA3-B/phase2` 应只见 ko-rerun/**；并把 ko-rerun/ocr/svg-gt-K11.json、svg-gt-K19.json 与 phase2/ocr/ 原件哈希对照（我只做了目视，非哈希）。
3. key 扫描：对全 worktree（含 untracked/scratch、task-envs 日志）跑 `rg -n "sk-[A-Za-z0-9]{16,}|eyJ[A-Za-z0-9_-]{10,}"` 期望零命中；确认 `deepseek.key` 未被复制入库。
4. 复跑离线确定性脚本：`python experiments/M2-TA3-B/ko_rerun_similarity.py --case K11` 应复现 K11-similarity.json（纯离线、零网络）——这是本次唯一可零成本复算的 Gate 证据。
5. `measure_cer.py` 复跑：确认 cer-summary.json/cer-regions.csv 可复算（含 --ocr-dir 指向 ko-rerun/ocr 的副本 GT）。
6. 计量零行为变更：确认 `--meter-translation` off 路径与 base 逐路径等价（读码已确认；建议在 base 与 head 上跑同一最小 case 或单测对比 provider 实例注册差异）——注意 metered fork 丢 pid 断言（R10）。
7. `--determinism-track` 缺口处置：确认 thresholds §5:172 要求是否已被别的 Task 实现/登记（我在实验层与 verification 未见）。
8. gate/门禁：本仓库测试套件不受影响（无 src/tests 变更），集成方跑一次三套件 0 failed 作为集成门。
9. 预算登记与外推公式的复算（乘数修正后）与 STATUS/REBASELINE 集成方同步项。

集成方闭合清单:
- R1: 落盘 50 万红线出处 or 回退到 phase2-plan.md:192 口径。
- R2: 2× 改"上界假设"+K11 异常登记+敏感性一行。
- R3: --determinism-track 实现或缺口登记。
- R4-R8: 文档修补（归因点名链、tiling 口径、计量命名、§7 量化、证据入库/汇总产物命名）。
- R9-R11: 精度修补。
- NOT_VERIFIED 1-9。
- STATUS/REBASELINE_PLAN 回填（集成方职责，本 worktree 禁改）。

推荐下一步（一句）：由 Codex/集成方在 ko-rerun-report.md §1.1/§1.2/§7 与 budget-register.json 中落盘红线出处、把 2× 乘数改为上界并登记 K11 Run1 异常与敏感性，再按 §7 四问向用户请裁决；本次 head 无需返修代码。

Hmm, the "推荐下一步" should be one sentence. Fine.

Let me reconsider the verdict: with R2 (cost-model overstatement) and R1 (unverifiable red line) — are these "关键验证缺失"? The key verification (PASS/FAIL of the Gate) is present and honest. The stop decision is conservative. Nothing blocks integration. So: **approved（有条件：0×P0/P1；P2 文档/口径级由集成方与 Owner 在原 head 上以文档修订闭合；NOT_VERIFIED 交集成方运行时核对）**. I'll phrase: `approved`（conditions listed）.

Hmm, but R3 (documented caliber control missing) — is that "关键验证缺失"? It's a *procedural* control from thresholds §5 that's absent. The substantive determination (remote track) is unambiguous here because the runner's provider_policy explicitly records "openai-compatible-translation (DeepSeek…)" in the summary ✓ — so the track is in fact recorded in the artifact (provider binding), just not via the mandated flag. I'll keep it P2 but note the substance is verifiable from the summary. Good.

One more consideration: should R2 be P2 or P3? It challenges a headline claim in a stop decision. The direction is conservative (2× is an upper bound; using a smaller multiplier would still stop when K07-10 are included, but the "known-only exceeds" claim becomes borderline 47.6万). Since the actual decision (stop) survives, and the fix is documentation, P2 feels right (口径级/文档级, per repo precedent P2 = 文档/口径级).

Similarly R1 = P2.

Let me now write the final report. It must be in Chinese, in the specified output format. Include the checklists, findings table with file:line, NOT_VERIFIED, integrator closure list, next step. Should be thorough but not bloated. I'll use the requested headings:
## Verdict
## 逐项核对表（A–F）
## Findings（R1…）
## NOT_VERIFIED
## 集成方闭合清单
## 推荐下一步

Let me make sure the line references are precise:

R1:
- doc/tasks/M2-TA3-B2-KO-RERUN.md:29 (AC5), :39-43 (纪律)
- verification/M2-TA3-B/phase2-plan.md:192
- verification/M2-TA3-B/ko-rerun-report.md:15,51
- verification/M2-TA3-B/phase2/ko-rerun/budget-register.json:45,57
- verification/M2-TA3-B/quality-report.md:208

R2:
- ko-rerun-report.md:37,48; budget-register.json:16,38-39
- qual-K11.json:1062-1070 (metering 19/19), run1 translate steps 190,244,382,412,418,442,466,484
- qual-K02.json:125…4547 (93 translate steps), :9320-9325 (140/140)
- Handoff:13

R3:
- quality-thresholds.md:172; verification/M2-QUAL-DETERM-CALIB/integration.md:8
- experiments/M2-TA3-B/run_qualification.py:899-909 (新增参数仅 sfx-policy/meter-translation); ko_rerun_similarity.py:213-228 (note_export_track 散文判轨)
Hmm, ko_rerun_similarity.py line numbers in the worktree: the file is 250 lines; the JSON payload line numbers in the worktree file: let me not cite uncertain line numbers. In diff coordinates it's a new file with 250 lines; the note_export_track is at worktree line ~222 (from the grep earlier: ko_rerun_similarity.py:222 note_export_track). Yes grep showed "ko_rerun_similarity.py Line 222: "note_export_track": (". And line 203 "measure". Good, use :222.

R4:
- ko-rerun-report.md:79; doc/tasks/M2-TA3-B2-KO-RERUN.md:48
- doc/tasks/M2-TASKS-BACKFILL-MULTIREGION.md:5,35-37; doc/handoffs/M2-TASKS-PRIMARY-SFX-GATE-19bf234a.md:16,26
- src/application/tasks/service.py:1054; src/application/tasks/projection.py:336
- phase2/summaries/qual-K11.json:75-135 (run1 9 page-level steps) vs ko-rerun/summaries/qual-K11.json:76-490

R5:
- ko-rerun-report.md:97
- ko-rerun/summaries/qual-K11.json:26-27,44-45 (1200×1660)
- verification/M2-DETECT-WEBTOON-TILING/integration.md:8 (trigger 4.0)

R6:
- ko-rerun-report.md:19,37; budget-register.json:16,72-74
- experiments/M2-TA3-B/run_qualification.py:718-733 (proxy)
- src/infrastructure/providers/fallback.py:101-130; retry.py:96-146; runtime.py:92

R7:
- ko-rerun-report.md:53,163-166

R8:
- experiments/M2-TA3-B/ko_rerun_k11_driver.py:154,217,263
- ko-rerun-report.md:159 (N7 证据路径)
- ko-rerun/summaries/qual-report.json:20-41

R9: as above with lines.

R10:
- experiments/M2-TA3-B/run_qualification.py:226-260 vs experiments/M2-TA3-B/translate_probe.py:137-160

R11 (语义等价判定依据): ko-rerun-report.md:125,129; K11-similarity.json:54-63.

Wait, the worktree path for run_qualification.py line numbers — the diff gave offsets: the metered proxy class was inserted at old line 184; in the new file, `reregister_env_resolver_metered` is at line 226 per grep ✓, and the proxy class translate at ~718? Hmm no: the proxy `translate` method — grep didn't give me its line. The diff hunk header said "@@ -184,6 +184,108 @@" so the new content starts at line 184 and spans 108 lines → proxy class ~187-290. My citation "run_qualification.py:718-733" was based on diff line numbers (diff file line 718 = the `def translate` line in the patch). That's the DIFF's line, not the file's line. Let me correct: in the new file, `_MeteredTranslationProvider.translate` is around line 199-215 (since class starts ~187). Let me verify with a grep for "def translate" in the worktree file.

Similarly the CLI args: diff hunk "@@ -638,6 +798,17 @@" → new lines ~798-814 for --sfx-policy/--meter-translation. And main's summary additions at ~879-882. And run_case signature ~337-338. Let me get exact line numbers via grep for the key markers.

Let me do that to keep citations accurate.
dsh: reasoning:
Correct file line numbers:
- _MeteredTranslationProvider: run_qualification.py:187 (class), :208 (def translate)
- reregister_env_resolver_metered: :226-260
- run_case signature sfx_policy/meter_translation: :340-341
- sfx policy reassemble block: ~:443-460 (diff said "@@ -334,10 +440,49 @@", so lines 440-489 → stage("sfx_policy_reassemble") around 455)
- translation_metering summary: :762
- CLI args: :802, :808
- summary top-level: :883

R6 citation: run_qualification.py:208-215 (proxy translate) — good.
R10: run_qualification.py:226-260.

Let me also confirm the `--sfx-policy` reassemble block lines: grep for "sfx_policy_reassemble".

Not critical. I'll cite :802-812 for the CLI args.

One last check: does `reregister_env_resolver_metered` get used only when meter_translation (line ~486)? Yes from the diff.

I also want to double check the "PIX/LOG outside repo" claim: ko_rerun_k11_driver.py:154 LOG_ROOT = G:\CODEX\New Manga.task-envs\M2-TA3-B\ko-rerun-logs ✓ (diff line 154, and in the file it's around line 47? Let me verify: from the diff, the file's line numbers = diff lines minus 107 → LOG_ROOT at file line 47, PIX_MAIN at 45. Hmm! The diff showed the file content starting at diff line 109 = file line 1. So file line = diff line - 108. LOG_ROOT: diff 154 → file line 46. ENV_KEY_NAME: diff 156 → 48. So my citation should be ko_rerun_k11_driver.py:46 (LOG_ROOT), :109 (write result)... The write_text for K11-driver-result.json: diff 217 → file 109; diff 263 → file 155.

Let me verify with a grep to be exact.
dsh: reasoning:
Good. Now I have accurate citations.

Let me finalize. One more sanity check on R2's claim that the report calls it "实测结构": report line 48: "| 请求数模型 | ≈ 2 × region 数（Run1 一轮 + Run2 一轮，§1.1 实测结构）× 607 est token/请求 |" ✓ — "§1.1 实测结构". And budget-register line 16 "KEY FINDING ... full-chain request count ~= 2 x region_count" ✓.

Also let me double check my R2 counterexample's numbers once more: K11 regions = 13 (11 non-empty). Run1 translate steps = 8 in all three passes. Run2 = 13 region runs, 2 failed → 11 successful calls. Metered requests = 19 = 8 + 11 ✓ (n_target_region_calls = 19 ✓). So K11 full-chain = 19 calls / 13 regions = 1.46×. Under the 2× model it would be 26. ✓.

Impact on known-only: with 1.5×: 521 × 1.5 × 607 = 474,3xx ≈ 47.4万 < 50万 ✓. I'll say ≈47–48万.

Also note: for K02, the metered 140 = 93 + 47 (run2 truncated by failures) → 1.51×. So the observed multipliers are 1.46–1.51, and 2× is a projection. That's a clean way to state it.

Also I should mention the positive: "Run1 也逐 region 非整页批量" IS verified for K02 (93 translate steps), so the N4 finding is half-verified — the *region-per-call* part (140/140) is fully verified; the *count ≈2×* part is not.

Now write the final answer. Keep it organized and reasonably concise but complete. Chinese. Include tables.

For the 逐项核对表 A–F, I'll write each as a short table or bullet list with 结论 (PASS/部分/FAIL) + 证据.

Let me write it.
## Verdict

**approved（有条件）** — 0×P0/P1；3×P2 均为「文档/口径级」，可在原 head 上以文档修订闭合；未发现禁改面改动、key 明文、伪造数字或静默降级。**静态范围内我实测可复算的数字全部复现**（CER 6 行逐位、median/P90、计量 140/140、K02 93/93 译文、K11 19/19、相似度 12×1.0+min 0.4615、CSV n=15/ai_mean 4.31）。核心遗留是**停跑依据的两处口径**（红线出处 R1、成本乘数 R2）与**判轨 fail-closed 控件缺失**（R3），以及若干精度修补（R9）与实验面卫生（R10/R11）。

判定依据：停跑方向保守（任何纪律读法都支持"停"），全链 Gate 如实报 FAIL，F1 证据链（detect 5/5 + 全链 1/5）成立，K11 差异与相似度 FAIL 归因方向经我独立核对成立。

---

## 逐项核对表（A–F）

### A 停跑决策（结论：**决策成立，依据表述需修**）
| 核对点 | 结论 | 证据 |
|---|---|---|
| 50 万红线是否任务书原文 | **否** | `doc/tasks/M2-TA3-B2-KO-RERUN.md:29`（AC5 只有"预估请求数/先行一个 case 试算后再全量"）、`:39-43`（纪律节无任何数值）；仓库现行为 `verification/M2-TA3-B/phase2-plan.md:192`＝**"预估总 token 数万 token 量级，超预期即停并登记"**，且该行自述 r2 N6 曾把口径写成"数十万以内"被判**越界改写并回退**。→ R1 |
| 外推假设不确定度标注 | **成立** | `ko-rerun-report.md:46` 明写 K07/K09/K10"**无先例**…按已测密度区间估 120–400 region/页"；区间 881–1721 与同宽 K01 密度线性外推（K07≈380/K09≈291/K10≈292，合 963 → 总 1484）相容，落在区间内 |
| 乘数口径 | **不成立（表述越界）** | `ko-rerun-report.md:48` 写"§1.1 **实测结构**"；同 run 的 K11 计量 19 calls/13 region＝1.46×、Run1 仅 8 calls（三 pass 一致）→ R2 |
| 停跑点是否代价最优 | **是（可辩护）** | F1 已由 TILING detect 层 5/5 覆盖，剩余高价值项＝F2 三页；按同一模型 F2 三页本身 44–146 万 est token > 红线，"先跑 K07/K09/K10"同样触线；K02 试算后停＋保留 K19（0 请求）/K11（≈19 请求）近零成本对照＝信息/成本比最优 |

### B F1 解锁实证（结论：**PASS，scope 诚实**）
| 核对点 | 结论 | 证据 |
|---|---|---|
| 组合证据链完整性 | **成立** | detect 层 5/5（`verification/M2-DETECT-WEBTOON-TILING/qualification-results.json:63/293/426/579/681` ＝180/93/113/62/60，独立 Task GATE PASS）＋全链 1/5（`qual-K02.json:53-74`：region_count 93、ocr 93、**translated 93**、export OK 5,069,825B、sha b5e27061…）；报告如实 scope（`:69`"就此关闭（**该页级**）"、`:140`"K01/K04/K05/K08 页级实测待裁决"） |
| K02 Run2 46 region 失败影响面 | **隔离正确** | 45×PROVIDER_TIMEOUT＋1×INVALID_OUTPUT（`qual-K02.json:5823-7318`，我逐条计数＝46）全部 typed 落盘；译文层完整（93/93 final）；CER 不受影响（ko G1 自动子集只含 K11 6 行）；报告 `:60`已给干净重跑选项（+186 请求≈113k）并声明"完整 pipeline_failures=0 的 ko webtoon 样本尚不存在" ✓ |

### C PRIMARY 差异与 K11（结论：**方向正确，归因需点名链**）
| 核对点 | 结论 | 证据 |
|---|---|---|
| run1 completed→completed_with_failures 归因 | **机理成立，单点归因不精确** | 首跑在 `f99a6c55`（BACKFILL 的 base）→ run1 步表为**页级 9 步**（`phase2/summaries/qual-K11.json:79-134`）；重跑 run1 步表为 **region 级 ~66 步**且含 1 条失败 term_extract（`ko-rerun/summaries/qual-K11.json:76-490`，失败步 `:364-368`）。账目统一首由 BACKFILL R1 完成（`doc/tasks/M2-TASKS-BACKFILL-MULTIREGION.md:5,35-37`），PRIMARY 把 primary 纳入并**整体退役页级决策链**（`doc/handoffs/M2-TASKS-PRIMARY-SFX-GATE-19bf234a.md:16,26`）→ 报告 `:79`只写 PRIMARY，漏前置链 → R4 |
| K11 行为对照一致 | **成立** | 13 region/11 翻译/2 空 OCR typed 同型；export OK；重复文本、空白差等均如实登记 |

### D 相似度 Gate 自然 FAIL（结论：**口径一致、预言印证如实、判定依据未落盘**）
| 核对点 | 结论 | 证据 |
|---|---|---|
| 与 thresholds §5 口径一致 | **成立** | `quality-thresholds.md:168`："全部对齐对（含空对规则：双方空=1.0、单方空=0.0）…median≥0.95 且 min≥0.70"、"非空对 n≥1 否则 NO_DATA"；脚本 `ko_rerun_similarity.py:504-510/630-638` 与之逐项吻合（空对计入 all-pairs、覆盖前置独立） |
| min=0.4615 对语义等价判定依据 | **未落盘** | `ko-rerun-report.md:125,129` 直接断言"语义等价的合法重译（同义改写，非字符噪声、非漏译）"，无审阅人/逐句对照记录；版本对见 `K11-similarity.json:54-63`（源"이렇게까지는 할필요없을줄 알았는데"）→ R11 |
| CALIB 局限 8 印证如实 | **成立（逐字级）** | `verification/M2-QUAL-DETERM-CALIB/calibration.md:97` 原文即为"语义等价的合法重译…会被判低相似度 FAIL…假 FAIL（保守）方向系统性偏置"；同文件 `:91`"**无自然 FAIL 样本**"→"首次自然实测"表述成立 |
| 移交裁决表述 | **部分** | 三候选（维持/语义度量/登记 known-limitation）方向正确，但无成本/后果/对 K11 判定的影响 → 并入 R7 |
| 附报口径 | **实质满足** | JSON 逐对附 `similarity_raw`（CALIB 局限 5 要求），但正文只报 normalized（`ro10` raw=0.9474 / normalized=1.0 未提）→ R9 |

### E CER 逐位与计量（结论：**CER PASS（我逐位复算）；计量口径需改名**）
| 核对点 | 结论 | 证据 |
|---|---|---|
| 6/6 逐位一致 | **成立** | 逐行对照 `ko-rerun/ocr/cer-regions.csv:95,98,99,100,101,106` vs `phase2/ocr/cer-regions.csv:58,61,62,63,64,69`：gt_text/ocr_text/cer **全等**（含 밑→믿、륵→르 两处错字复现）；n=6、median=(0+0.1111)/2=0.0556、P90=0.3333、zero 50% 我独立复算一致；排除 7 行同口径（`cer-summary.json:36-113`） |
| "TILING 语义下"解释 | **未讲清** | K11＝1200×1660（`qual-K11.json:26-27,44-45`）→ h/w=1.383 ≤ TILING 触发阈值 **4.0**（`M2-DETECT-WEBTOON-TILING/integration.md:8`）→ 与首跑同路径；报告/交接全文无"4.0/未触发"字样，`:97`"在 TILING+新语义链下再次证实"会被读成 tiling 下 OCR 稳定性证据 → R5 |
| 估算 vs endpoint usage 披露 | **成立（显式且突出）** | `ko-rerun-report.md:29`、每份 summary 的 `token_basis`、`budget-register.json:20`（"ESTIMATES, endpoint usage fields are not exposed"），并引用首跑"token 量无计量证据"登记 ✓ |
| "行为零变更"论证 | **成立但有一处漏** | opt-in 默认关（`run_qualification.py:802-812`；metered re-register 仅 `--meter-translation` 分支），代理为透传包装（`:187-215`，`payload.regions`/`payload_json()`/`result.raw_text` 均在 `ports/translation/protocol.py:71,116`、`ports/translation/ports.py:33` 存在）；漏项＝fork 丢 pid 守卫（R10）＋调用数≠HTTP 数（R6） |

### F 范围纪律与裁决清单（结论：**范围 PASS；清单不够决策级**）
| 核对点 | 结论 | 证据 |
|---|---|---|
| 允许/禁改面 | **PASS** | diff 24 文件全落允许面：`experiments/M2-TA3-B/**`(4)、`verification/M2-TA3-B/phase2/ko-rerun/**`(16)、`verification/M2-TA3-B/{ko-rerun-report.md,quality-report.md}`、Task/Handoff；`src/**`/`tests/**`/`doc/contracts/**`/`packaging/**`/`apps/**`/`doc/STATUS.md`/**quality-thresholds.md** 零出现（thresholds 未动，与 §7.3 移交裁决一致 ✓） |
| 首跑产物零改动 | **静态 PASS** | diff 中无 `phase2/ocr/*`、`phase2/summaries/*` 条目（新增均为 `phase2/ko-rerun/**`）；但 ko-rerun 内两份 SVG GT 为**首跑副本**，逐字节一致性属运行时项（NOT_VERIFIED） |
| key 零明文 | **PASS** | 对 `review-input.diff` 全文扫描 `sk-…/eyJ/Authorization/DEEPSEEK_API_KEY`：仅命中 env 变量名、运行期拼装 `"Bearer " + key`（driver:56、readability:361）、复现段的 `$(cat …deepseek.key)` **路径**；无值、无 base64 |
| 脚本变更面 | **表述需精确** | 实为 **1 改（run_qualification.py）＋3 新增**；handoff 已如此写，用户 brief 的"3 脚本微调"应统一为 1+3（不构成 finding） |
| §7 清单决策充分性 | **不足** | `ko-rerun-report.md:163-166` 四项无成本/覆盖量化，F1 关闭口径与 F2 必要性两独立决策点被"范围"吞并 → R7 |

---

## Findings

| ID | 级别 | 文件:行 | 触发与影响 | 复现证据 | 建议 |
|---|---|---|---|---|---|
| **R1** | P2 | `doc/tasks/M2-TA3-B2-KO-RERUN.md:29,39-43`；`verification/M2-TA3-B/phase2-plan.md:192`；`ko-rerun-report.md:15,51`；`budget-register.json:45,57`；`quality-report.md:208` | 本次核心决策依据"50 万 est token 红线"在仓库内**无可核出处**，且与现行纪律文字（"数万 token 量级"，且该行明确记载"数十万以内"曾被判越界改写回退）相差约 50×。停跑方向保守不缺合规，但后续补跑授权口径不可审计 | Task 纪律节无该数值；`phase2-plan.md:192` 原文；报告自称"任务纪律/task brief"均无引文 | 把用户裁决③/编排指令中该数值的**原文与出处**落盘（Task/报告引用条款），或按 `phase2-plan.md:192` 口径重述；二选一后集成 |
| **R2** | P2 | `ko-rerun-report.md:37,48`；`budget-register.json:16,38-39`；反例 `ko-rerun/summaries/qual-K11.json:190,244,382,412,418,442,466,484`＋`:1062-1070`；`qual-K11.rerun.json:88-400`；`qual-K11.sfx-translate.json:104-470`；正例 `qual-K02.json:125…4547`、`:9320-9325` | "请求数≈**2×**region 数"被写成"§1.1 **实测结构**"，但**同一 run 的计量反例未被登记**：K11 三个 pass 的 Run1 均恰 8 次调用（13 region／11 有文本），计量 19 calls＝8+11 → **1.46×**；K02 计量 140＝93+47 → **1.51×**（2× 是"两轮逐 region 全覆盖"的投影）。用 1.5× 计，已知页 521×1.5×607≈**47.4–47.6 万 < 50 万**——即"仅五页即超线"的表述在乘数上不稳健（含 K07-10 时任何组合仍超线，停跑结论不变）；Run1 少发请求的机制（非 duplicate-text 可解释：K11 去重后仍 9 个不同文本）完全未解释 | 报告 §1.2 表与 budget-register KEY FINDING；K11/K02 计量与步表逐条可数 | ①把 2× 改写为**上界假设**，区间结论仍用 107–209 万；②补一行**敏感性**（1.5× → 已知页≈47.6 万，红线仅由含 K07-10 的全量外推触发）；③登记"K11 Run1 8 次调用"异常并给机制结论或标为 open |
| **R3** | P2 | `verification/M2-TA3-B/quality-thresholds.md:172`；`verification/M2-QUAL-DETERM-CALIB/integration.md:8`；`experiments/M2-TA3-B/run_qualification.py:802-812`；`ko_rerun_similarity.py:222` | §5 尾注规定"runner 以 `--determinism-track remote\|mock` **显式记录**所选轨道，声明与 provider 绑定不一致时 **fail-closed 报错**"；实况：实验层 4 脚本无该参数（`experiments/M2-TA3-B/**` 全文无 track 定义），判轨只写在 JSON 散文 note 与报告叙述。实质判定正确（summary `provider_policy.translate` 记 DeepSeek），但**无 fail-closed 保护**——provider 被误绑 mock 时不会报错 | thresholds:172 原文；`ko_rerun_similarity.py:222` note_export_track；runner 参数表仅 +2 项 | 在 runner/similarity 增 `--determinism-track` 并按 provider 绑定校验（本 Task 允许面含 runner 微调，宜就地补）；若判定不做，须把该行登记为**已知口径缺口**并说明 |
| **R4** | P3 | `ko-rerun-report.md:79`；`doc/tasks/M2-TA3-B2-KO-RERUN.md:48`；`doc/tasks/M2-TASKS-BACKFILL-MULTIREGION.md:5,35-37`；`doc/handoffs/M2-TASKS-PRIMARY-SFX-GATE-19bf234a.md:16,26`；`src/application/tasks/service.py:1054`、`projection.py:336` | N3 把 run1 终态变化单点归因给"PRIMARY Task 的 terminal accounting unified 语义"；机理上**账目统一先由 BACKFILL R1 完成**（region_ids[1:] fan-out），PRIMARY 把 primary 纳入并整体退役页级决策链。方向正确但漏前置链，且未给判别证据（哪条 unit 翻转终态） | 两代 run1 步表结构指纹（页级 9 步 → region 级 ~66 步）；PRIMARY handoff `:16`"页级决策链整体退役" | 改写为"BACKFILL fan-out + PRIMARY primary 纳入（87f61d8b 语义定稿链）"并引用 `service.py:1054`/`projection.py:336` 终态计算路径 |
| **R5** | P3 | `ko-rerun-report.md:97`；`ko-rerun/summaries/qual-K11.json:26-27,44-45`；`verification/M2-DETECT-WEBTOON-TILING/integration.md:8` | "OCR 跨 run 确定性**在 TILING+新语义链下**再次证实"暗示覆盖 tiling 路径；实况 K11 h/w＝1660/1200＝**1.383 < 4.0**，未进入 tiling，与首跑**同路径**，逐位一致属预期。6/6 数值本身为真（见核对表 E），是**措辞越界** | K11 尺寸在 summary；TILING 触发阈值 4.0 在 integration.md | §3.1 加一句限定："K11 未触发 tiling（1.383<4.0），tiling 路径 OCR 稳定性本 run 未覆盖（K02 无 GT）" |
| **R6** | P3 | `ko-rerun-report.md:19,37`；`budget-register.json:16,72-74`；`run_qualification.py:208-215`；`src/infrastructure/providers/fallback.py:101-130`；`retry.py:96-146`；`runtime.py:92` | 计量代理记录的是 provider.translate() **成功逻辑调用**；production retry 在 provider 之外（`run_chain → run_with_retry`，默认 `max_attempts=2`，可被 `settings["providers"]["retry"]` 改），失败尝试不落记录 → 140/19 是调用数，**HTTP 次数 ≥ 该值**（故障窗 46 region 计 ≈92 次尝试未计），token 估算亦未计重发 input；summary 无 `attempt_count` 字段可核 | 代理插入点（run_qualification.py:208）；retry 包装位置与默认值 | 改称"成功 `translate()` 调用数"；注明 retry 倍数与"attempt_count 未落盘"为计量盲点；"无重试风暴"的量级证据按调用数口径说明（方向保守，不影响停跑） |
| **R7** | P3 | `ko-rerun-report.md:53,163-166` | §7 四项裁决**缺决策级量化**：①选项①–④无 est token/覆盖成本（仅 §7.2 给了 K02 +113k）；按同模型可给 ③F2 三页≈360–1200 region≈44–146 万、②`--max-regions` 按 N 的披露口径、④0；②"F1 是否仅凭 detect 5/5＋K02 全链 1/5 关闭、K01/K04/K05/K08 是否必须补页级全链"是**独立决策点**，现被"7 case 范围"吞并；③§7.3 三候选未写对 K11 判定的后果（维持＝继续 FAIL／语义度量＝需新 Task+校准／登记 known-limitation＝本次按 directional 接受）与成本 | §1.2/§7 原文 | 在 §7 每项附"成本 / 覆盖 / Gate 后果"三列后请用户裁决 |
| **R8** | P3 | `experiments/M2-TA3-B/ko_rerun_k11_driver.py:46,109,155`；`ko-rerun-report.md:159`（N7 证据 `ko-rerun-logs/K02-rerun-attempt*.log`）；`ko-rerun/summaries/qual-report.json:20-41` | ①N7（后台 Bash ~58 分钟强杀）与"API 恢复后自动执行"的证据目录 `…\task-envs\M2-TA3-B\ko-rerun-logs`（含 `K11-driver-result.json`）在**交付面之外**，仓库内不可复核；②`summaries/qual-report.json` 被最后一次调用覆盖，只剩 K11（`skipped=true`、`failures=2`），**不是** K02+K11+K19 的 run 级 roll-up，报告/交接未标注，易被误读（首跑该文件曾是汇总件） | 路径常量出仓库；qual-report.json 内容 | 把关键日志/驱动结果**摘要或副本**纳入 verification（或在报告写明"证据在仓库外，仅登记"）；qual-report 按 suffix 命名或补一份 run 级索引 |
| **R9** | P4 | `ko-rerun-report.md:49,51,19,124-125`；`budget-register.json:4,40,45,66-67`；`quality-report.md:208`；`K11-similarity.json:148-151`；`qual-K11.sfx-translate.json:1036-1044` | ①"仅 TILING 五页即 63.2 万"：63.2 万＝521 region（**含 K11 13**）算得，五页＝508→61.7 万（两者都超线，归属表述不实）；②"实际 ≈347 请求≈20.4 万"含**未计量** attempt-1 估算（budget-register 自述 197/119k＋attempt-1 ~140 未计量），且被强杀的 attempt-1 被称"K02 全链"；③时间戳把 UTC 标成 +0800（`budget-register.json:4`、报告 §1.3），`"20:40Z+0800"/"21:05Z+0800"` 非法；实测 K02＝18:42:13Z–20:15:25Z（`qual-K02.json:14,9329`）。115 分钟时长与 environment 分类不受影响；④`n_variant=1` 是 normalized 口径，pairs 有 2 个 raw variant（ro10 raw 0.9474/normalized 1.0）→"12/13 逐位一致"按 raw 应 11/13＋1 对仅空白差（CALIB 局限 5 要求附 raw，JSON 已附、正文缺注）；⑤`sfx.policy=translate`"gate 放行"无该 region translate step（term_extract 先失败、`final_source=none`），应写"按 `decide_sfx_translation` 语义推断放行" | 全部可逐条复算 | 按①②③④⑤逐处改述（纯记录工作） |
| **R10** | P4 | `experiments/M2-TA3-B/run_qualification.py:226-260` vs `experiments/M2-TA3-B/translate_probe.py:137-160` | **possible Duplicated Code**：metered re-register 是 probe 帮助函数的 40 行 fork，且**丢掉了原函数的 production provider-id 漂移守卫**（`translate_probe.py:159-160`）→ 计量路径 fail-closed 强度下降，probe 帮助函数日后变更不会传导（判断项，非硬违规） | 两函数逐行对照 | 让 probe 帮助函数接受 factory 包装参数（单点维护），或在 metered 版本保留 pid 断言 |
| **R11** | P3 | `ko-rerun-report.md:125,129`；`K11-similarity.json:54-63` | "该浮动对是语义等价的合法重译"是**Owner 自判且无判定过程落盘**（无审阅人、无逐句对照、无独立核对）。CALIB 局限 8 只声明"该方向存在系统性误报"，不证明**这一对**属该类；本 finding 不否定结论，否定的是"判定依据"缺失 | 报告 §4 归因段落无依据引用；JSON 无 `semantic_equivalence_judgment` 字段 | 在 §4 补一行判定依据（例如"Owner 对源文逐句对照两版译文，判定同义改写，非漏译/噪声；人工复核人=X"），或把该对列入用户裁决附件 |

---

## NOT_VERIFIED（集成方运行时项）

1. **Git 事实**：`git rev-parse 87f61d8b/36971e97/0001d68c`、`git log 87f61d8b..0001d68c --oneline`、`git status --porcelain`（worktree 是否 clean、tip 是否 docs-only）；`review-input.diff` 是否＝完整 fork→tip diff（我按 diff 判定范围，未能在沙箱内生成 base diff）。
2. **首跑产物 byte 不变**：`git diff 87f61d8b...0001d68c -- verification/M2-TA3-B/phase2` 应只见 `ko-rerun/**`；并把 `ko-rerun/ocr/svg-gt-K11.json`、`svg-gt-K19.json` 与 `phase2/ocr/` 原件的 **sha256** 对照（我只做目视/字段抽样，未做哈希）。
3. **key 扫描**：全 worktree（含 untracked/scratch）＋ `task-envs` 日志跑 `rg -n "sk-[A-Za-z0-9]{16,}|eyJ[A-Za-z0-9_-]{10,}|api[_-]?key\s*[:=]\s*['\"]"` 期望零命中；确认 `deepseek.key` 未被复制入库。
4. **离线复算相似度 Gate**（零网络、零成本）：`python experiments/M2-TA3-B/ko_rerun_similarity.py --case K11` 应复现 `K11-similarity.json` 全字段。
5. **复跑 CER**：`measure_cer.py --summaries-dir …/ko-rerun/summaries --ocr-dir …/ko-rerun/ocr` 应复现 n=6/median 0.0556（并确认 6 行 G1 GT 来自副本、与首跑原件同源）。
6. **计量零行为变更**：在 base/head 上跑同一最小 case 或单测，对比 provider 注册与 `translate()` 入参/返回（读码已确认透传；注意 R10 的 pid 守卫差异）。
7. **R3 缺口归属**：确认 `--determinism-track`（thresholds:172）是否已由其它 Task 实现或已登记；未见则按缺口处置。
8. **集成门**：本 head 无 src/tests 变更，仍建议跑一次三套件（0 failed）作为集成记录。
9. **审阅者本机取证不可得**：本会话无 shell（`pwsh` 被沙箱拒），故所有"运行"类证据均为静态复算，非重执行。

---

## 集成方闭合清单

- [ ] **R1**（P2）：落盘 50 万红线出处（用户裁决③/编排指令原文＋条款），或按 `phase2-plan.md:192`"数万 token 量级"口径重述；两处（报告 §1.2/§7、budget-register、quality-report §10）同步。
- [ ] **R2**（P2）：`ko-rerun-report.md:37,48` 与 `budget-register.json:16,38-39` 把 2× 改为**上界假设**；补敏感性一行（1.5×→已知页≈47.6 万）；登记 K11 Run1 8 次调用异常（open/机制结论）。
- [ ] **R3**（P2）：补 `--determinism-track`＋provider 绑定校验（fail-closed），或登记为已知口径缺口并说明判定不做。
- [ ] **R4**（P3）：N3 归因改写为 BACKFILL→PRIMARY 链＋引用 `service.py:1054`/`projection.py:336`。
- [ ] **R5**（P3）：§3.1 补"K11 1.383<4.0 未触发 tiling，tiling 路径 OCR 未覆盖"限定。
- [ ] **R6**（P3）：计量口径改"成功 translate() 调用数"＋retry 倍数/attempt_count 盲点说明。
- [ ] **R7**（P3）：§7 四项补齐"成本/覆盖/Gate 后果"，并把 F1 关闭口径、F2 页级必要性拆为独立决策点。
- [ ] **R8**（P3）：N7/驱动证据入库或标注"仓库外仅登记"；`qual-report.json` 覆盖问题修正或补 run 级索引。
- [ ] **R9/R10/R11**（P4/P4/P3）：精度改述（63.2 万归属、347/20.4 万标注估计、UTC 标签与非法时间戳、raw 口径注、gate 放行改"推断"）；metered fork 去重＋pid 守卫；§4 补语义等价判定依据。
- [ ] **NOT_VERIFIED 1–9** 逐条执行/登记；**STATUS/REBASELINE_PLAN 回填**由集成方按本 Task 终态处理（本 worktree 禁改）。
- [ ] 保持禁改面零改动：`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、首跑产物、`quality-thresholds.md`、`doc/STATUS.md`。

---

## 推荐下一步

由集成方在原 head（`0001d68c`）上以**纯文档修订**闭合 R1/R2/R3（红线出处、2× 改上界＋敏感性＋K11 异常登记、判轨 fail-closed 或缺口登记），随后按报告 §7 的量化四问向用户请范围裁决，本 Task 无需代码返修。
