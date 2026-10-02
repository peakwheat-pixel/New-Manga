dsh: reasoning:
Let me start by exploring the repository and the review inputs. I need to read the diff, task, handoff, report, and evidence files.

Let me plan: this is a static review. I should read:
- G:/CODEX/New Manga.task-envs/M2-SFX-E2E-MATERIAL/review-input.diff
- doc/tasks/M2-SFX-E2E-MATERIAL.md (in worktree)
- doc/handoffs/M2-SFX-E2E-MATERIAL-40a8ceec.md
- verification/M2-SFX-E2E-MATERIAL/sfx-e2e-report.md
- evidence files: qual-BJ06.json, material-inventory.json, cases.json, diagnose_sfx_detect.json

Sandbox is workspace-write but workspace is "G:\CODEX\New Manga" — the worktree is outside (G:/CODEX/New Manga.worktrees/...). Reading outside workspace may be denied? Let's try. Reading is typically allowed under workspace-write? Actually file policy workspace-write allows writes in workspace; reads may be broader. Let's try.

Let me start with the diff, which is at G:/CODEX/New Manga.task-envs/... also outside workspace.

Let me try reading.
dsh: reasoning:
The shell sandbox can't set up. The prompt said "沙箱无 shell 时不执行命令" — if no shell in sandbox, don't execute commands. So use file tools instead: read/glob/grep.

Let me try glob on the worktree.
dsh: reasoning:
Good, file tools work. Shell doesn't (sandbox setup fails). So static review only.

Let me read the diff first. It's probably large (5618 lines added). Let me read it.
dsh: reasoning:
Now let me read the rest of the diff, and key evidence files. Let me continue diff reading in chunks. 5749 lines. Let me read the file list first via grep on "diff --git".
dsh: reasoning:
Interesting. Now some scrutiny on the diagnosis:

1. The report §3.2 claims BJ13's "页面唯一 sfx 类框落在 T 恤印花（conf 0.82，误报=生产 run 的 sfx region）". But wait: BJ13's production run detected 1 sfx region. Yet the diagnosis shows a text box at [2122.1, 282.9, 2480.0, 1278.2] conf 0.7436 which contains the first reference SFX ピ一一ーン！ at [2210,240,2560,1000] — coverage of ref by text box: intersection = x: max(2210,2122.1)=2210 to min(2560,2480)=2480 → width 270; y: max(240,282.9)=282.9 to min(1000,1278.2)=1000 → height 717.1. Ref area = 350*760=266000. Intersection = 270*717.1=193,617 → cov 0.728. That's less than panel's 0.83. OK so panel wins via coverage metric. Fine.

But there's a subtlety: the "coverage" metric is intersection/ref area, single-sided, so a giant panel box covering everything wins. Actually the panel box [375.1,370.3,2612.3,3802.0] is the full page. The verdict "class confusion: picked up as panel" is somewhat misleading: the giant full-page panel box covers everything, so essentially the detector produced a whole-page panel box and the coverage metric trivially assigns the SFX to it. That's an important interpretive weakness: the "panel class covers SFX" conclusion may be an artifact of a page-spanning panel detection plus a single-sided coverage metric that ignores box size. The report says "竖排白底黑框毛笔字与 panel 边框形态相似" — but the evidence shows a page-level panel box (375,370)-(2612,3802) i.e., nearly whole page, and second ref covered cov 1.00 by the same box. Hmm, but note there's also a text box at [493.9,2682.8,761.3,3640.2] conf 0.8437 which covers the second ref [420,2560,760,3400]: intersection x: 493.9..760 width 266.1; y: 2682.8..3400 = 717.2 → 190,858/ (340*840=285,600) = 0.668. Panel box cov 1.00. So panel wins again. This is largely a page-level panel dominating. So the "class confusion (panel 支配)" claim is not really evidenced as confusion between SFX glyph shapes and panel borders; it's that a page-scale panel box trivially covers all refs and the single-sided coverage picks it. This is a genuine review finding — P2/P3: the diagnosis metric is size-biased (IoU would be fairer), and the verdict "class confusion" is not supported; it may be "no SFX-specific detection; ref falls inside a page-level panel box". Also the claim in the report that this "与 DETECT-EVAL §4 检出+分类两层" converges.

Wait, let me check: for BJ14, panel boxes: [1866.6,1632.5,2946,3040], [351,3087,2929,4167], [374.5,1633.5,1864.2,3041.2], [372,0.9,1489,1586.4], [1974.6,0,2946,1586.2], [1501.7,0,1968.5,1582.6]. The refs: [1230,300,1520,950] → covered by panel [372,0.9,1489.1,1586.4] cov: x 1230..1489.1=259.1, y 300..950=650 → 168,415/ (290*650=188,500) = 0.894 ✓ matches. That panel box is a page-ish region (372,0.9)-(1489,1586) — that's a quarter-page. So BJ14's three refs are each inside relatively large panel regions, which are plausible panels in a 4-panel layout. So a SFX drawn inside a panel would be covered by the panel box. That's not necessarily "confusion"; it's genuinely the panel box being large enough to cover the SFX, and there's no separate sfx detection. The "class confusion" wording inflates the evidence: to demonstrate class confusion (misclassifying SFX glyphs as panel), you'd need boxes that tightly bound the SFX. Here for BJ14 ref2 and ref3 the coverage is 1.00 by [374.5,1633.5,1864.2,3041.2] and [1866.6,1632.5,2946,3040] — these are the top two panel regions of the lower half. Hmm, ref3 (1900,2260)-(2200,2900) is inside panel [1866.6,1632.5,2946,3040]: cov 1.00. So again trivially covered.

So the finding: diagnosis lacks a "box tightness" criterion (e.g., IoU or box area ratio), so "panel 类高置信覆盖" is not evidence of classification confusion at the SFX location; the coverage metric is one-sided and a page/quarter-page panel box trivially covers. Also they didn't report whether the detector produced any local box near the SFX at all (i.e., recall gap vs confusion), which was one of their own stated diagnostic categories ("no box at all → blind spot"). Their verdict logic checks `best_cov > 0` only, so almost any page will report "class confusion" — the "detector blind spot" category can essentially never trigger, making the three-way classification non-discriminating. That's a solid P2 finding with file:line references: experiments/M2-SFX-E2E-MATERIAL/diagnose_sfx_detect.py lines ~255-275 (coverage function 196-203; verdict branch 264-275).

Also, another important detail: the diagnosis says BJ13's sfx box (conf 0.8222) at [1561.5,2608.5,1775.4,2906.9] is the T-shirt print. The production run's sfx region(s): report says BJ13 has 4 regions (3 speech + 1 sfx). Need to verify from qual-BJ13.json that this sfx region matches the diagnosed box location, and the OCR text was '．．．'. Also verify that the diagnosis box matches production region box. Let's check qual-BJ13.json.

Also need to check that the diagnosed text boxes at BJ13 [493.9,2682.8,761.3,3640.2] correspond to the second ピ一一ーン！ (which is the "huge vertical phone ring" SFX) — and note that in production the sfx_policy translate gate: the text boxes don't route to sfx. Fine.

But wait — important: report §3.2 BJ13 row says "页面唯一 sfx 类框落在 T 恤印花（conf 0.82，误报=生产 run 的 sfx region）". In the production run, only regions above conf 0.5 AND cls=sfx are kept... plus what other filtering does production do (min size, etc.)? Also the production pipeline may apply additional filters (e.g., aspect ratio, or region dedup, or OCR non-empty requirement). The report §3.1 says BJ13 has 4 regions (3 speech + 1 sfx). The diagnosis found 1 sfx box conf 0.82 → matches count. Good.

Now the T-shirt print claim: is the box [1561.5,2608.5,1775.4,2906.9] really a T-shirt print? That's a bare assertion from a single annotator's eyeball on a preview. It's directional. Note it isn't verifiable statically. Also note the OCR of that region was '．．．' — hmm, if a T-shirt print yields OCR '．．．', the region likely contains mostly blank/white; that's consistent with a false positive on a blank-ish area. Fine — but the alternative reading: could that box actually be one of the two ピ一一ーン！ SFX? The refs are at (2210,240)-(2560,1000) and (420,2560)-(760,3400). The sfx box (1561.5,2608.5)-(1775.4,2906.9) doesn't overlap either ref. So it's a third location → consistent with "not the目检 SFX". Whether it's a T-shirt print is unverifiable; the "误报" characterization depends on the目检 inventory being complete (single annotator, 40dpi→100dpi). Reasonable but must be flagged as directional. Also the report claims "T 恤印花" in two places; material-inventory may or may not mention T-shirt. Let's read material-inventory.json.

Let me now read the remaining diff parts and the key evidence JSONs. Files to read:
- diff lines 400-871 (register_new_cases, render_vol_pages, run_new_asset_e2e)
- diff 871-1096 (cases.json diff)
- diff 1096-1124 (run.log)
- qual-BJ06.json (huge, 1128-2743)
- qual-report.json
- material-inventory.json (2797-2901)
- new-assets-run.log
- new-asset-report.json
- qual-BJ13/14/15
- sfx-detect-diagnosis.json (done)
- report (done)

Let me read them. I'll do parallel reads.
dsh: reasoning:
Notes so far:

1. material-inventory.json `assets[].file` uses "日漫_JA/01_black_jack_official/vol03/pages/vol03_p0048.png" while cases.json new entries have `"local_path": "日漫_JA/01_black_jack_official/vol03/pages"` and... let me check if cases.json entries have a `file` key — the register script's entry dict has "page_file": spec["file"] where spec["file"] = "pages/vol03_p0048.png". Hmm! That's inconsistent with existing BJ cases presumably. Need to check existing BJ06 case structure in cases.json — what key does it use for the page file? Let's grep cases.json in the worktree for BJ06 entry. Since the diff only shows added lines for BJ13-15, I need the existing file (unchanged) to compare field schema. The worktree has test_assets/comic_golden_suite/manifests/cases.json. Let me read around BJ06's entry.

Also check: register script wrote "page_file": "pages/vol03_p0048.png" but material-inventory says "日漫_JA/01_black_jack_official/vol03/pages/vol03_p0048.png". If existing cases use e.g. "page_file": "日漫_JA/.../pages/vol03_pXXXX.png" then the new entries deviate. Need to verify. Also BJ06 might use "file" or "page_path". Let me grep.

2. register_new_cases.py `pipeline_status_of` has a bug-ish: `"ocr": "PASS" if (run2_ok and n_translated > 0) or run2_ok else "FAIL"` — that's just run2_ok, redundant. Not a big deal but it's dead logic / misleading. Also it writes "reading_order": PASS based on run1. Fine.

3. The `"sfx": "PASS" if any(...sfx_policy == "translate")`. For BJ13, is region_type "sfx" with sfx_policy translate present? The report says BJ13 sfx region 1/1 passes. Need to verify in qual-BJ13.json.

4. Another potential issue: register script re-serializes the entire cases.json with json.dumps and writes it back. If the original file has any formatting differences (e.g. non-2-space indent, escaped unicode, key order) it would show up as diff lines. Diff shows +214/-0, i.e., only additions... Actually the diff shows only one hunk at line 6150 with 214 added and 0 removed, so byte-identical prefix except the insertion point. Good — that supports "append only". But wait: with 3 entries each ~70 lines = ~210 lines + separators. 214 ✓.

5. License snapshot: captured at 2026-10-02T08:07Z, inventory generated_at 08:20Z. Snapshot bytes 32843, sha256 2bb1dc9f1a06... The report says 32,843 bytes ✓ consistent. Snapshot is git-external so I can't verify the sha256 — but wait, I might be able to read it! It's at G:/CODEX/New Manga.task-envs/M2-SFX-E2E-MATERIAL/license-evidence/... Reading is allowed by file tools presumably (glob worked outside workspace). I can read the HTML snapshot and check whether the claimed terms appear (二次利用フリー, attribution, 1 month report, Kindle 禁令, JASRAC pages). I cannot compute sha256 without shell. Hmm — shell is unavailable. I could... no. Can't compute sha256. But I CAN verify field completeness of terms by reading the HTML. That's valuable.

Let me find the license-evidence dir.

6. Also material-inventory "JASRAC-managed music pages: vol2 p35/54/150/151/153, vol7 p192" — report says the same. Verify against snapshot text.

Let me now read the rest of the diff (900-1100 cases.json additions, then run.log, qual files). And also read the HTML snapshot. And the existing cases.json BJ06/BJ01 entries for schema comparison.

Let me be efficient: parallel reads.
dsh: reasoning:
Good. Now read the license snapshot HTML, and the qual-BJ06.json translate_details + regions. And existing cases.json BJ06 entry.

Key checks:
- BJ06 regions: 17 with region_type sfx for 8, sfx_policy translate, and translate_details entries for those 8 with non-empty translated_text and final_source=machine.
- Report §1.3 table lists 8 OCR texts: いいじゃ, いいん, ！！！, ．．．, ．．．, ハチン, わ．．．, ３． — wait that's 8 including ハチン. Order in table: ハチン, いいじゃ, いいん, わ．．．, ！！！, ．．．, ．．．, ３．. Need to match the actual OCR outputs and translations from qual-BJ06.json.

Let me grep qual-BJ06.json for "translated_text" and region_type.

Actually the qual-BJ06.json in the diff has 1613 lines; let me read the translate_details section. Let me grep in the worktree file.
dsh: reasoning:
Now check the BJ06 SFX translations against the report table:

Actual from JSON (translate_details, sfx order):
1. いいじゃ → 好啊 ✓
2. いいん → 嗯嗯 ✓
3. ！！！ → ！！！ ✓
4. ．．． → …… ✓
5. ハチン → 啪 ✓
6. ．．． → …… ✓
7. わ．．． → 哇…… ✓
8. ３． → 3. ✓

Report table matches all 8 (semantically same set). ✓ Report ordering differs but content matches. Also the "≤6 字符" claim: 好啊=2, 嗯嗯=2, ！！！=3, ……=2, 啪=1, ……=2, 哇……=3, 3.=2 → all ≤6 ✓.

Note: report §1.2 says first-run BJ06 sfx OCR were いいじゃ/いいん/！！！/．．．×2/ハチン/わ．．．/３． ✓ matches.

Now check speech 9: report §1.4 claims 8/9 逐位一致 with first run, 1/9 legit re-translation (ちょっとおじいさん！？). Hmm — the current run's translation for ちょっとおじいさん！？ is "喂，老爷爷！？". The report says first-run was 「等一下，老爷爷！？」. That's a claim about the first-run artifact — which they say is untouched and presumably readable in the repo (first run of BJ06 under SKIP). Let me find the first-run qual-BJ06.json elsewhere in the repo (maybe verification/M2-TA3-B2/...). Since the diff says existing products untouched, I can check the first-run artifact to verify the 8/9 claim. That's a key verification: is the claim "8/9 逐位一致" checkable? Let's search for qual-BJ06.json in the main worktree.

Also: the report says the 9th speech region OCR "あいじゃ" → "爱酱"?? Wait: region with ocr_text "あいじゃ" got translation "爱酱" — that's a mistranslation (あいじゃ is meaningless; likely OCR error for「いいじゃ」... hmm actually "あいじゃ" → "爱酱" is a hallucination-ish translation). Not part of SFX AC claims but it's in the speech set. The report says speech 9/9 正常翻译 ("speech 对照 9/9 正常"). "爱酱" for "あいじゃ" is questionable but it's the OCR source's fault; and speech quality isn't the AC. Also note "しかし、" → "但是，" fine.

Hmm, but is there a possible finding: report §0/§1 claims speech "9/9 正常翻译不受扰" while one of them is "あいじゃ"→"爱酱" which is a garbled OCR (probably ハチン-adjacent page content). Not a defect of this task. Could mention as P4/observation: the speech set includes an OCR-garbled region, so "9/9 正常" is loosely stated but defined as "落库成功". Minor.

Now verify the 8 sfx regions: compare the region-level list. Let me read the regions section (lines 920-1130) to check region_type/sfx_policy and also check whether regions have bbox/OCR. Also check "defect" claims: "17/17 region 零 defect". Let's look for "defect" fields.

Also want to check the K11/首跑 comparison feasibility. Let me find the first-run BJ06 summary.

Let me also read cases.json BJ06 entry (lines 4804-4877) for schema comparison (to check page_file key etc.), and lines 4455-4530 for BJ01.

Parallel calls.
dsh: reasoning:
Good. Schema matches BJ06 exactly (page_file: "pages/vol03_p0056.png"). So the new entries are schema-consistent ✓. material-inventory uses a different (fuller) path form — that's just a different doc, fine, though minor inconsistency between inventory "file" and cases.json "page_file".

Now, an important check: the "sfx" pipeline_status for BJ14/BJ15 = NOT_RUN. The register script derives from regions with region_type sfx AND sfx_policy==translate. For BJ14/15, if 0 sfx regions → NOT_RUN ✓ consistent with the report.

Wait, but there's a subtlety in the register script's sfx rule: it requires `sfx_policy == "translate"`, which is a *policy* field, not a run outcome. If a page had an sfx region with policy translate but translation failed, it would still be PASS. Minor. Also if the harness default policy were skip, sfx would be NOT_RUN even though detection ran. It's marked PASS only if gate actually released. Report §3.1 says BJ13 sfx=PASS "存在走通 translate gate 的 sfx region". OK, reasonable but criterion is policy-presence not outcome. P4 note.

Also, "speaker_attribution": "NOT_RUN" — but is that consistent with BJ06's existing case (also NOT_RUN)? Yes, BJ06 has NOT_RUN. Fine.

Another check: `"difficulty": "unassessed"` and `"ground_truth_available": "none"` consistent.

Now let me verify the 8 sfx region list (lines 1030-1130) and the final part of qual-BJ06 (defects?). And check "17/17 region 零 defect" evidence: maybe "defect" appears in regions? Let me grep "defect" in qual-BJ06.json.

Also check run2 region_runs detail, export status, wall_s, cost metering fields (translate_metering?), and the "34 requests" claim.

Let's grep for "requests", "est", "meter", "wall_s", "defect", "translated" counts.
dsh: reasoning:
Now: pitfall — the "17/17 region 零 defect" claim. Let me check what the actual qual harness checks. The run.log said "[BJ06] details: OK {'ocr': 17, 'translated': 17}". "零 defect" might come from a "defects" field in the summary; grep for "defect" returned no matches (the grep pattern included defect and returned nothing for it). Indeed no "defect" string found. So the claim "17/17 region 零 defect" isn't backed by a machine-readable field in the summary — probably an interpretation of "all per-region statuses completed". That's a minor traceability gap: the report asserts "零 defect" without a defect list/count field. P3/P4.

Now check the final part of qual-BJ06: export, translation_metering, wall_s. Also the beginning part: source sha256, image dims. Let me read lines 1584-1613.

Also check whether the qual-BJ06 "detect" stage includes per-region confidences... and whether "17/17 region" includes the ones with 0.82 conf etc.

Then verify the first-run comparison claims. Search the repo for the first-run BJ06 summary. Let me glob for **/qual-BJ06.json across the main worktree G:/CODEX/New Manga and worktrees.

Also check the DETECT-EVAL report §4.4 清单 to validate the 衔接 claim. Let me read verification/M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md §3.3 and §4.4.

Let's do parallel: read tail of qual-BJ06, glob for qual-BJ06* in main repo, grep DETECT-EVAL for §4.4 items.
dsh: reasoning:
Let me read the DETECT-EVAL report §3.3, §4.4 and Known limitations 4 to evaluate the衔接 claim (panel vs text class confusion). Also read the first-run qual-BJ06.json (M2-TA3-B/phase2) to verify speech 8/9 identical + 1 legit retranslation, and the first-run sfx OCR/skip policy.

Let me read those.
dsh: reasoning:
Excellent. The first-run artifact (M2-TA3-B/phase2/summaries/qual-BJ06.json) verifies:

- First run: 17 regions (9 speech + 8 sfx), sfx_policy=skip for all sfx, translated 9 (speech only), sfx translated_text="" final_source="none". ✓ matches "首跑全 skip".
- Speech first-run translations match the current run's 9 except ちょっとおじいさん！？ = "等一下，老爷爷！？" (first run) vs "喂，老爷爷！？" (current) → 8/9 逐位一致 ✓, 1/9 changed ✓. Claim verified.

Wait, careful: the claim is "8/9 逐位一致". Let me list first run: 但是，/ 爱酱 / 他反复出现...！！/ 喂喂 / 呼吸很奇怪…… / 等一下，老爷爷！？ / 这不是醉驾吗！？ / 然后， / ！！！ — current: 但是，/ 爱酱 / 他反复出现...！！/ 喂喂 / 呼吸很奇怪…… / 喂，老爷爷！？ / 这不是醉驾吗！？ / 然后， / ！！！ ✓ exactly 8 identical + 1 changed. Verified. 

Now the K11 similarity: "与 KO-RERUN 相似度 Gate 观察的合法重译形态同型" — plausible; but is the "legal re-translation" determination supported? 「等一下，老爷爷！？」→「喂，老爷爷！？」 semantic equivalence: yes, both are address+wait; acceptable. Fine, directional.

Now note ordering issue: the first-run region order vs current: same region_ids? Let's check quickly whether region_ids match (claim "与首跑同 region 数、同类型分布——检测确定性跨 run 复现"). Report §0 says "chiqui7 检出 17 region（8 sfx + 9 speech，与首跑逐 region 一致）". Hmm, "逐 region 一致" — does that mean identical region ids/bboxes? Let me check the first run's region ids vs current run's. From the grep of the first-run: region list at lines 146-339. Let me read lines 140-345 of first run to compare region ids/bboxes with the current run.

That's a good verification: if region ids/bboxes differ, the "逐 region 一致" claim (report §0) would overstate. Let's check.

Also the "K11 裁决项 7 正面关闭" claim and "首跑 BJ06 sfx region OCR 全非空" — verified: first run OCR text for the 8 sfx regions = いいじゃ/いいん/！！！/．．．/ハチン/．．．/わ．．．/３． all non-empty ✓.

Now let's also check the KO-RERUN §3.2 claim (8 个有文本 sfx region) and §7.7 to verify the statements. Let's grep the KO-RERUN report.

Then the new-assets runs: need to verify BJ13/14/15 summaries: region counts, sfx_policy, translated texts, metering, and notably BJ13's sfx region ocr '．．．'→'……'. And the report's claim "BJ13 bfs region 1/1 = T 恤印花误报".

Also check new-asset-report.json numbers vs report §3.1 table (8/12/14 requests; token sums).

Let me read those files. And also verify token arithmetic: 20,246 + 4,756 + 7,309 + 8,424 = 40,735 ✓ (compute: 20246+4756=25002; +7309=32311; +8424=40735 ✓).

Requests: 34+8+12+14 = 68 ✓.

Now check new-asset-report.json for the actual metering values and whether the report's per-case numbers (4,756 etc.) come from the summaries.

Let me read new-asset-report.json, and grep qual-BJ13/14/15 for translated_text / sfx_policy / metering.
dsh: reasoning:
Region ids differ between runs (expected: new page_id / new region UUIDs) but bboxes seem identical: run1 first region bbox 2251,152,242,575 = same as current run's first region bbox. So "逐 region 一致" is true in terms of bbox/type/order, not region_id. The report §0 says "与首跑逐 region 一致" — accurate if interpreted as bbox/type; but strictly the region_ids differ. In §1.1 the report says "与首跑同 region 数、同类型分布——检测确定性跨 run 复现". Slight nuance: region ids regenerate, bboxes identical. That's fine — I could note the wording precision (P4). Let me verify the full bbox lists match for the 8 sfx regions: current run sfx bboxes: (2145,3084,161,309), (2495,2907,157,409), (1534,3517,223,395), (926,2818,170,294), (388,3402,340,534), (1830,2969,162,297), (408,468,217,492), (2494,1895,87,103). First run's sfx bboxes at lines 254-339 — I saw structure but not values. Let me check quickly by reading first-run lines 250-345.

Also note the wall_s in new-asset-report: BJ13 217.92 vs report 217.9 ✓; BJ14 309.38 ✓; BJ15 358.16 (report 358.2 ✓).

Note: new-assets-run report generated_at_utc = 00:18:50 — but BJ06 finished at 00:18:36 and BJ15 wall 358s, so the new-assets run must have... wait, generated 00:18:50, finished_at 00:33:35. Total wall of 3 cases ≈ 217.9+309.4+358.2 = 885.5s ≈ 14.8 min = from 00:18:50 to 00:33:35 ✓ (885s = 14.75 min) ✓ consistent.

But hmm: BJ06 run started at 00:07:01 and finished 00:18:36 — and the diagnosis tool generated_at 00:35:46, material-inventory 08:20:00. Hmm, material-inventory generated_at_utc 08:20:00Z while snapshot captured 08:07Z — but BJ06 run log timestamps showed 08:07:10 local (the run.log says 2026-10-02 08:07:10 for manga_ocr — that's local time, while qual-BJ06 started_at_utc 00:07:01Z). So local time = UTC+8. So diagnosis at 00:35:46Z = 08:35:46 local. material-inventory generated_at 08:20:00Z — but wait, that would be 16:20 local if local=UTC+8. Hmm. material-inventory's generated_at_utc "2026-10-02T08:20:00Z" — if the author used local time and mislabeled as UTC, that's a 8-hour skew. Similarly the license snapshot "snapshot_captured_at": "2026-10-02T08:07Z" while the run.log's local 08:07:10 corresponds to 00:07Z. Hmm! So the license snapshot captured_at 08:07Z conflicts... Actually the snapshot capture may have occurred at local 08:07 while the BJ06 run started at local 08:07 too? No — run.log local timestamps: "2026-10-02 08:07:10.398" for manga_ocr loading, and qual-BJ06 started_at_utc 00:07:01Z, finished 00:18:36Z. So local = UTC+8, and 08:07 local = 00:07 UTC. So if the snapshot was captured at local 08:07, then its UTC would be 00:07Z, not 08:07Z. But the material-inventory says snapshot_captured_at 08:07Z and generated_at 08:20Z. And the bj06 run started at 00:07:01Z. Two things happening at "08:07" — one labeled local (run.log) and one labeled Z. Suspicious: the snapshot capture time is likely local time mislabeled as UTC (a real inconsistency), OR the workflow order was: snapshot at 00:07Z... hmm.

Actually wait. Look at the timeline: BJ06 run 00:07:01Z → 00:18:36Z. new-assets run 00:18:50Z → 00:33:35Z. diagnosis 00:35:46Z. So all these are "Z" and would be 08:07-08:35 local in UTC+8. Meanwhile license snapshot claims captured 08:07Z and inventory generated 08:20Z — which are... hmm, if those were local times they'd be 00:07Z and 00:20Z. 00:07Z is exactly when the BJ06 run started. Interesting coincidence but plausible if the author ran things sequentially and the snapshot was actually captured earlier (e.g., on 2026-10-02 at local 08:07 — no wait, BJ06 run started at local 08:07 too).

Hmm, hold on. Maybe the machine's local timezone is UTC+8 and the run.log "08:07:10" is local while qual-BJ06's started_at_utc "00:07:01Z" is UTC. Both refer to 08:07 local. So the license snapshot's "2026-10-02T08:07Z" — if that's a Z-labeled value it's inconsistent with the BJ06 run. But actually the license capture presumably happened *before* the runs (license-first discipline), so it can't be at 00:07Z... unless it happened concurrently. Hmm, material-inventory says captured_at 08:07Z, generated 08:20Z — before the diagnosis (00:35:46Z)? That would put inventory generation at 08:20Z which is 16:20 local, *after* everything. And the report's own §2.3 says render manifest. Also the report generated date 2026-10-02.

So the most likely reading: material-inventory.json's timestamps (08:07Z / 08:20Z) are actually local-time values mislabeled with "Z", i.e., a timestamp-labeling inconsistency, while the qual summaries use true UTC. Not a functional defect (directional evidence), but worth a P3/P4 finding on timestamp discipline, since the review asks about field completeness. Hmm, but is it? Actually maybe the license snapshot was captured at 08:07Z (16:07 local) — and the runs at 00:07Z (08:07 local) happened before... that would violate "license-first" ordering (license evidence must precede material use). Wait no: 00:07Z < 08:07Z, so runs happened first, snapshot 8h later. Either way there's an ordering inconsistency between the two readings:
- Reading A (snapshot time is true UTC 08:07Z): license snapshot (08:07Z) postdates the AC3 runs (00:18-00:33Z) → contradicts "许可一手快照先行" (license-first) discipline claimed in the handoff/report.
- Reading B (snapshot time is local mislabeled as Z = 00:07Z): then snapshot is roughly simultaneous with BJ06 run start; still "先行" claim unverifiable, but at least not 8h after.

Either way this is a legitimate finding: the timestamps in material-inventory.json vs the run summaries are mutually inconsistent (8h skew suggesting local/UTC label confusion), which weakens the "许可快照先行" ordering evidence. P3.

Hmm, but careful. Let me double check by examining whether any file mtimes are available... I can't run shell. But glob results gave modification-time ordering. Let me use read on the spill file? Not helpful. Maybe I can check file mtimes via glob on specific dirs — the glob tool returns paths in modification-time order! That's a hint. The earlier glob of task-envs returned: license-evidence first, then thumbs-vol03/... in page order. Hmm, glob ordering is "modification-time order" — license-evidence/densho810-free-snapshot appeared first in the list, meaning... the list said "Returns up to 100 paths in modification-time order" — typically most recent first? If most-recent-first, then the snapshot is the most recently modified file in task-envs. Hmm, that includes all thumbnails written before. So snapshot most recent → snapshot modified after thumbnails. But the drawing order isn't conclusive about exact time.

Actually I can inspect... no shell. Hmm.

Let me check whether the task-envs tree has other files: render-final-manifest.json, pixels, detect-diag-previews. The glob was truncated at 100 paths (281 total). Let me grep the spill file for interesting paths (manifest, license, detect-diag, pixels).

Also, importantly, I should check whether the snapshot HTML actually contains the claimed terms. Let me read it (32KB HTML — might be long; grep is better).

Checks on snapshot:
- "二次利用フリー"
- attribution text 「ブラックジャックによろしく 佐藤秀峰」
- info@densho810.com, 1 month
- Kindle
- JASRAC with page numbers: 2巻 p35/54/150/151/153, 7巻 p192

Let me grep the snapshot.

Also, the snapshot itself is git-external, so it is NOT part of the diff — it's referenced. That means the license evidence is not independently verifiable from Git; a reviewer can only inspect the external file. I can inspect it since I have read access. But its sha256 can't be recomputed without shell. I'll mark sha256 as NOT_VERIFIED (integration/runtime), but I can verify content presence.

Let me grep the snapshot for those terms.
dsh: reasoning:
Key observation from the glob ordering (modification-time order, and it seems the list is roughly *ascending* by mtime given license-evidence first, thumbs, then grids, then render-final-manifest, pixels, previews, detect-diag-previews last). Hmm, but wait: thumbs-vol03 files came before grid_page_p0001-0035.png which is in the same dir. Then render-manifest.json (line 230) then .jpg grids (231-237) then... line 256 render-final-manifest.json. So order is: license-evidence html (line 1!), then thumbs pages, then grids... 

Hmm — license-evidence first suggests it has the OLDEST mtime? Or the newest? The glob doc says "Returns up to 100 paths in modification-time order" — ambiguous. If license-evidence snapshot were created first (license-first discipline), the order would be ascending. But then the sequence: license-evidence/html (first), then thumbs (earlier pages then grids), then render-manifest.json, then grid .jpg... that ordering is odd for ascending (grid .png before render-manifest.json before grid .jpg suggests two separate render passes: first pass without --grid, then a pass with --grid? Actually the .jpg grids were probably from an earlier jQuery/different tool...).

Hmm, this ordering is muddled. Let's not over-infer from glob ordering. Note: the file listing shows `thumbs-vol03/grid_page_p00XX-YYYY.png` and `.jpg` both — so the contact sheets were generated twice (once .png from render_vol_pages.py --grid, once .jpg maybe a re-encode). And `thumbs-vol03/render-manifest.json`, `render-final-manifest.json` at root.

Wait — the material-inventory says `render_manifest_git_external: ".../render-final-manifest.json"` ✓ exists. And visual_scan says thumbs in thumbs-vol03 ✓, contact sheets 7 ✓ (grid_page_p0001-0035 ... p0211-0221 = 7 sheets covering 221 pages ✓).

The `detect-diag-previews` 3 files ✓ exist.

pixels/ocr/crops/BJ06/*.png 17 crops ✓ (matches 17 regions) and pixels/export/BJ06-translated.png ✓.

Hmm interesting: the diagnosis preview BJ13 claims the T-shirt print sfx box; I could actually LOOK at the preview image! I have read_image. That would let me verify the "T 恤印花误报" claim and whether refs are SFX. That's a strong verification step — the images are external but readable. Let me look at BJ13-detect-diag.jpg.

Also the license snapshot: need to verify the attribution string 「ブラックジャックによろしく　佐藤秀峰」 appears with two points (title + author) — line 265 shows exactly that ✓. English "Give My Regards to Black Jack SHUHO SATO" ✓. 1ヶ月以内 report to info@densho810.com ✓ (line 275, 333, 413). Kindle prohibition line 317/375 ✓. 1円以上 有償 line 318/417 ✓. JASRAC line 323/382 — but does the snapshot list the specific page numbers (vol2 p35/54/150/151/153, vol7 p192)? The inventory claims "JASRAC-managed music pages: vol2 p35/54/150/151/153, vol7 p192". Line 323 mentions JASRAC管理楽曲 but I didn't see page numbers in the grep because my pattern didn't include them. Let me grep for "p35" / "35" / "54" / "150" / "192" in the snapshot.

Also verify the "vol03 is JASRAC-free" claim: need snapshot to list which pages/volumes have JASRAC-managed music. Let me grep for "192" and "35".

Let me do that plus read the BJ13 preview image.
dsh: reasoning:
Excellent! The BJ13 preview is very informative:

- The two blue rectangles = reference SFX (ピ一一ーン！ in vertical ovals? Actually the blue boxes are the approx reference boxes at top-right and left-middle). Wait, the blue boxes... In the image, the top-right blue box encloses the vertical text "ピーーーン！"? Actually the top-right shows a vertical oval-ish bubble with "ピーーー...ン" (looks like "ピーーーーーン" with the oval outline). And the left-middle blue box encloses another vertical text "ピーーーーン".

Hmm wait, looking closer: the top-right shows a vertical oval containing hand-drawn katakana which reads something like "ピーーーーーーーー" — a phone ring. And the left one similar. The blue ref boxes look OK.

- The red box (sfx class) is on the guy's T-shirt logo "SURF..." (a T-shirt print!) — confirming the "T 恤印花误报" claim! Yes! The red box is right at the T-shirt chest print reading "SURF" style letters. That's excellent verification: the T-shirt print claim is CORROBORATED by the preview image. Note: at the source resolution the red box xyxy [1561.5,2608.5,1775.4,2906.9] ... in the 1/3-scale preview that'd be ~(520,869)-(592,969) — in the displayed 982x1389 image (which is ~1/3 of 2946x4167 = 982x1389 ✓). So the red box at (520,869)-(592,969) in the preview = T-shirt print area. ✓ Yes, matches the "SURF" logo on the T-shirt (in the image it's at roughly x 520-590, y 870-970). ✓ Confirmed.

- The green boxes = panel class boxes; the outer green box is the page-level panel box (375,370)-(2612,3802) in source = (125,123)-(870,1267) in preview — matches the big green rectangle framing the artwork. ✓ Confirms my analysis: the panel box that "covers" both refs is a near-page-level box. This strongly supports my P2 finding: the "panel 类 0.92-0.97 高置信覆盖" is largely a page-scale panel box trivially covering; the DETECT-EVAL R12 note itself warns that coverage is single-sided and "大框可平凡覆盖；chiqui7_any_class 列常被 panel 类页面级大框支配 coverage=1.0，该列不用于任何结论". The new diagnosis reintroduces exactly the metric that the earlier report disqualified. That's a strong, well-grounded finding (P2): the diagnosis tool uses the same one-sided coverage and the report's "panel 类高置信覆盖" claim relies on a column/caliber its own reference report explicitly rules out for conclusions.

Also note: the orange box = text class box around the chapter title (第19話 徳ちゃんと先生) at top-left [384.9,413.7,1638,813.3] → preview (128,138)-(546,271) ✓ matches. And the blue ref box at top-right overlaps the actual SFX. The text box at [2122.1,282.9,2480,1278.2] (conf 0.74) is the actual SFX location — orange? Wait, in the image, the top-right area: there's a green box overlapping and blue box around the SFX oval. Is there an orange box there? Looking at the description: colors: red=sfx, orange=text, lime=others (bubble/panel). Hmm, the code says color = "red" if sfx else ("orange" if text else "lime"). So panel and bubble are both lime. The big green→lime box around the whole artwork = panel. The text boxes = orange: chapter title box (orange outline around 第19話 title ✓ visible) and... the third text box [493.9,2682.8,761.3,3640.2] → preview (165,894)-(254,1213) = around the left SFX? Hmm no wait. That box is at x 165-254, y 894-1213 in preview — which is the left-side vertical SFX area (the left blue ref box is at (140,853)-(253,1133)). So yes the orange text box overlaps the left SFX. And the fourth text box [2122.1,282.9,2480,1278.2] → preview (707,94)-(827,426) = top-right SFX area, overlapping the top-right blue ref box. Interesting: so there IS an orange (text) box on each of the two目检 SFX locations, in addition to the page-level panel box. The report's table says "均 panel 类 conf 0.943 (cov 0.83/1.00)" — it reports only the *best-coverage* box, which is the page-level panel. It does not disclose that a text-class box (conf 0.74/0.84) also covers each SFX location at cov 0.67-0.73. So the report's claim "6 个被 panel 类 0.92-0.97 高置信覆盖" is a best-coverage cherry-pick that hides the co-located text boxes — the very "class confusion" they'd want to describe is *also* text-class. And more importantly, the actual cause of no sfx region might be either. This is a P2/P3 finding on the diagnostic's non-disclosure: report §3.2 table shows only the top-coverage box, omitting the text-class candidates at the same locations; the "panel 支配" attribution is an artifact of the single-sided coverage + best-box selection.

Hmm, wait. Let me be careful about which boxes are which in the preview. The image shows at top-right: a green/lime box (large, spanning the top-right quadrant from ~(700,60) to (860,530)?) Hmm hard to tell exactly. Let me look again at the described image: top-right there is a large box outline that goes around the SFX oval and extends right — appears to be a rectangle with a green-ish/olive outline (that's the page-level panel box border at x=870? no, the page-level panel box right edge = 2612/3 = 870 which is indeed near the right side). The visible vertical line at the far right (~x=870) is the panel box's right edge, and the top edge at y≈123. So the big rectangle = the page-level panel box ✓.

There's also an orange box around the chapter title ✓ (text box 1).

So on BJ13, the detector produced: 1 page-level panel box, 3 text boxes (chapter title, top-right SFX?, left SFX?), 1 sfx box (T-shirt). Wait, text boxes: [384.9,413.7,1638,813.3] = chapter title (covers "第19話 徳ちゃんと先生" ✓). [493.9,2682.8,761.3,3640.2] = left-middle (the left SFX location!) and [2122.1,282.9,2480,1278.2] = top-right (the top-right SFX location!). Hmm, but [493.9,2682.8,761.3,3640.2] — x 493-761 → preview x 165-254, y 894-1213. The left blue ref = [420,2560,760,3400] → preview (140,853)-(253,1133). So yes overlapping. So the detector DID find both目检 SFX locations as *text* class boxes (conf 0.84 and 0.74)! That means the claim "sfx 类 0 命中" is true, and there's no blind spot — but the class assigned is **text**, not "panel". The report says the SFX were "covered by panel class" and concludes "与 ko 域 text 混淆形态不同：本样本是 panel 类（竖排白底黑框毛笔字与 panel 边框形态相似）". But the evidence shows the SFX locations were covered by BOTH a page-level panel box AND co-located text-class boxes! So the claim "与 ko 域 text 混淆形态不同" is contradicted by the diagnosis data itself: text-class boxes DO sit on the SFX locations (conf 0.74/0.84), exactly like the ko-domain text confusion form (DETECT-EVAL §3.3: "chiqui7 的类内混淆（sfx 类漏、text/bubble/panel 类捡走）：...→text conf=0.94").

This is a solid, high-value P2 finding: the report's central interpretation in §3.2 (panel-class confusion, morphologically different from the ko-domain text confusion) is not supported by the diagnosis JSON, because the same locations have text-class boxes with conf 0.74–0.84 that the report's best-coverage table hides. Let me verify the coverage numbers:
- top-right ref [2210,240,2560,1000] vs text box [2122.1,282.9,2480.0,1278.2]: ix = min(2560,2480)-max(2210,2122.1) = 2480-2210 = 270; iy = min(1000,1278.2)-max(240,282.9)=1000-282.9=717.1; area ref=350*760=266000 → cov=0.7275 (0.73).
- left ref [420,2560,760,3400] vs text box [493.9,2682.8,761.3,3640.2]: ix=760-493.9=266.1; iy=3400-2682.8=717.2; area=340*840=285600 → cov=0.668 (0.67).

Yes. So co-located text boxes at cov 0.67/0.73, panel at 0.83/1.00. Since the report states "6 个被 panel 类 0.92-0.97 高置信覆盖" and "与 ko 域 text 混淆形态不同...本样本是 panel 类", the omission is material to the interpretive conclusion. Also the T-shirt false positive is confirmed by the preview (red box = SURF print) — that part is corroborated.

For BJ14: boxes list includes text boxes at [505.6,3344.4,867.1,3883.7], [2334.2,3138.8,2605.8,3686], [471.1,2441.2,741.3,2980.1], [1519.6,1735.5,1723.4,2052.2], [2008.8,2528.1,2160,2986.4], [2603.4,1676.1,2676.4,1943.3]. Refs: [1230,300,1520,950] (top area) — no text box overlaps (text boxes are lower/right). [400,1900,700,2560] vs text [471.1,2441.2,741.3,2980.1]: iy = min(2560,2980.1)-max(1900,2441.2)=2560-2441.2=118.8; ix=min(700,741.3)-max(400,471.1)=700-471.1=228.9 → 228.9*118.8=27,193 / (300*660=198000) = 0.137. Small. [1900,2260,2200,2900] vs text [2008.8,2528.1,2160,2986.4]: ix=2160-2008.8=151.2; iy=2900-2528.1=371.9 → 56231/(300*640=192000)=0.293. Small. So for BJ14 the top-coverage box is genuinely a panel box (cov 0.89-1.00) and text coverage is low. Fine — so BJ14's "panel" attribution is less misleading, but still the boxes are quarter-page panels, not tight SFX-shaped boxes.

For BJ15: refs [1600,200,1900,800] and [900,1650,1150,2200]; text boxes: [1341.6,3515.9,1567.6,3908.9], [504,2799.7,733.1,3248.6], [1926.5,3516.8,2124.2,3841.1], [2389.4,1635.6,2492.4,1894.9], [1647.9,2684.9,1715.5,2950.2], [2446.1,2692.4,2517.6,2958.1], [1041.3,2722.4,1105.5,2984.2], [819.4,943.1,911.4,1291], [1430.8,226.2,1534.4,564.6]. Ref1 [1600,200,1900,800] vs text [1430.8,226.2,1534.4,564.6]: ix = 1534.4-1600 <0 → 0. So no text overlap → panel only. Ref1 also vs text box... no. Ref2 [900,1650,1150,2200] vs text [819.4,943.1,911.4,1291]: iy = min(2200,1291)-max(1650,943.1)=1291-1650 <0 → 0. So BJ15 panel-only ✓.

So the text-class co-location issue is BJ13-specific (2 of 7 instances). Still worth flagging as P2/P3: the report's generalization "本样本是 panel 类（与 ko text 混淆形态不同）" over-generalizes from a best-coverage box selection, and BJ13's own data contains text-class boxes on both目检 SFX.

Hmm, careful: is the "text" box in BJ13 really covering the SFX, or is it covering something else nearby (e.g., the oval speech bubble containing the SFX)? Looking at the top-right: the SFX ピーーーン！ is drawn inside an oval shape (looks like a large oval = likely the "phone ring" represented in an oval outline, and the blue ref box covers it). The orange text box at [2122.1,282.9,2480,1278.2] — hmm, in preview (707,94)-(827,426). The top-right vertical text oval spans roughly x 700-830, y 90-430 in preview. So the text box tightly bounds the oval itself. So yes: the detector DID detect the SFX oval but classified it text (or it's an oval-bubble form → text/bubble). Actually it's classified "text". So it's fair to say the location was detected as text-class, not that it's a blind spot.

Hold on. Also possible: the top-right oval contains the phone SFX drawn in an oval balloon-like shape → detector sees text (which is what SFX lettering is) — that's exactly the class confusion the eval reported for ko (SFX → text). Therefore the report's claim "与 ko 域 text 混淆形态不同" is factually contradicted for BJ13, and the report's own diagnostic data files include the text boxes needed to see this. Good finding.

But wait — I should double check the preview: is there an orange box at the top-right? The image shows at top-right: a large box with olive/green line that extends beyond the oval, plus a blue box tightly around the oval. I see in the image "the top-right blue box" and a bigger green box overlapping. Is there an orange box? Let me look at the rendered image once more mentally: In the top-right, I see a blue rectangle (ref) around the vertical oval text, and a greenish rectangle extending to the right edge and down. The text box (2122,282)-(2480,1278) at preview scale (707,94)-(827,426): the blue ref box in preview is (2210/3,240/3)-(2560/3,1000/3) = (737,80)-(853,333). So the orange box (707,94)-(827,426) is slightly left and taller than the blue ref box — they overlap heavily. In the image, indeed there appear to be two nested rectangles around the top-right SFX: a blue one and an olive/lime one. Hmm, the olive one might be the panel box edge... no, panel box is (125,123)-(870,1267) — one big rectangle.

In the image at top-right I can discern: an outer rectangle spanning from about x=707 to 853 and y=60 to 470ish — with a distinctly different color (looks olive/dark yellow). And the blue rectangle inside/overlapping. I'm fairly confident the orange box is there (the tool draws text boxes in orange). The image rendering shows the top-right with a lime/olive outline around the oval and text label. Hmm. Since the coordinates are objective (they're from the JSON), my geometric computation stands: the text box at [2122.1,282.9,2480.0,1278.2] has 0.73 coverage of ref1. Whether it's visible as orange or lime doesn't change the JSON facts. Note that the report's own table for BJ13 says "页面唯一 sfx 类框落在 T 恤印花" while omitting these text boxes. Good.

Hmm, but one more consideration in fairness: the report says "7 个目检实例：sfx 类 0 命中；6 个被 panel 类 0.92-0.97 高置信覆盖". For BJ13 they wrote "均 panel 类 conf 0.943（cov 0.83/1.00）" — they reported best coverage. Since the box that best covers is the page-level panel, saying "panel 覆盖" isn't false per se, but "与 ko 域 text 混淆形态不同" is the overreach, since for BJ13 the co-located text boxes are the same-domain text-confusion form. I'll file it as P2 (interpretive claim not supported by the cited evidence) with file:line refs:
- verification/M2-SFX-E2E-MATERIAL/sfx-e2e-report.md:125 (§3.2 bullet "形态学与 DETECT-EVAL 的 ko 域观察不同")
- sfx-detect-diagnosis.json:58-65 (BJ13 text boxes) + the verdicts at 74-99
- diagnose_sfx_detect.py:255-275 (best-coverage-only verdict)

Also — the report §3.2 for BJ13 says cov 0.83/1.00 for the two refs; that matches. Fine.

Now, let me also verify the claim about "6 个被 panel 类 0.92-0.97 高置信覆盖" — BJ14 3 panel conf .9668/.9687/.9721 ✓ within 0.92-0.97; BJ15 .9552/.9188 ✓; BJ13 .9431 ✓. So 7 instances, 6 of them best-covered by panel... wait: BJ13's 2 refs + BJ14's 3 + BJ15's 2 = 7. All 7 have panel best-cov. The report says 6 of 7 covered by panel with conf 0.92-0.97 (0.9431, 0.9668, 0.9687, 0.9721, 0.9552, 0.9188 = 6 in [0.92,0.97]... wait 0.9721 is in range; so all 7 are within 0.9188-0.9721, i.e. 0.92-0.97 ✓ all 7). Report says "6 个被 panel 类 0.92-0.97 高置信覆盖" — that's inconsistent with its own table which shows all 7 as panel-class (BJ13 2 + BJ14 3 + BJ15 2). Hmm! Owner's claim in the task prompt says "6 个被 panel 类 0.92-0.97 高置信覆盖（与 ko 域 text 混淆形态不同）". And report §0 (§3.2 table) says: BJ13 "均 panel 类 conf 0.943" (2), BJ14 "均 panel 类 conf 0.967-0.972" (3), BJ15 "均 panel 类 conf 0.919-0.955" (2) → 7. But §0 conclusions table and §3.2 prose say "6 个被 panel 类覆盖". So there's an internal numeric inconsistency: 7 vs 6. Unless one instance is excluded... which one? Possibly BJ13 instance 1 is at cov 0.83 vs... no. Or maybe they mean 6 of the 7 because one is... Let me check: report line 15 (§0): "7 个目检 SFX 实例：sfx 类 0 命中；6 个被 panel 类 0.92-0.97 高置信覆盖；BJ13 唯一 sfx region 为 T 恤印花误报". And line 121-123 table: BJ13 2 refs both panel; BJ14 3 refs panel; BJ15 2 refs panel = 7. So "6 个" contradicts the table's 7. Possibly the author intended "6 个被 panel 类 ... 覆盖" counting only those with cov 1.00? cov values: BJ13 0.83 & 1.00; BJ14 0.89,1.00,1.00; BJ15 1.00,1.00 → cov=1.00 for 5, plus... no. Or maybe they counted the 6 non-BJ13 ones? Hmm BJ14(3)+BJ15(2)=5, +BJ13 1 = 6? If one counted only the cov=1.00 ones: 5. Hmm.

Actually maybe they counted instances where panel was the *sole* class at the location (excluding BJ13's 2 text co-located) → BJ14 3 + BJ15 2 = 5. Not 6.

Or excluding the BJ13 ref with cov 0.83 → 6 instances with cov≥0.89? Eh.

Most likely a counting slip (7 vs 6). This is a legitimate P3 finding: the "6/7" count in §0/§3.2 prose is inconsistent with §3.2's own table (7/7 panel-class). I'll note it as a numeric inconsistency with file:line refs: report line 15 vs lines 119-123; and the diagnosis JSON verdicts (7 verdicts, all "class confusion ... cls=panel").

Let me count verdicts in diagnosis JSON: BJ13 2 (lines 85, 97), BJ14 3 (307, 319, 331), BJ15 2 (591, 603) = 7, all "class confusion ... cls=panel" ✓. So "6" is wrong; should be 7. Good, objective finding (P3).

Also the claim "BJ13 sfx region 1/1 落库『．．．』→『……』" — need to verify from qual-BJ13.json. Let me read the translate_details of qual-BJ13 and check the sfx policy/region. Let me also verify BJ14/BJ15 region counts and absence of sfx regions and the metering numbers (8/12/14 requests, tokens 4370+386, 6654+655, 7724+700).

Wait, report §3.1 table says BJ13 "8 / 4,370+386" = 4,756 ✓; BJ14 12 / 6,654+655 = 7,309 ✓; BJ15 14 / 7,724+700 = 8,424 ✓. Let me verify from the summaries.

Let me grep qual-BJ13.json and others for translate_details and metering.
dsh: reasoning:
Verified BJ13: 4 regions (3 speech + 1 sfx), sfx ocr '．．．' → '……', final_source machine, export sha 70b95ded… ✓, metering 8 / 4370+386 ✓, wall 217.92 ✓ (report 217.9).

BJ14: 6 speech regions, requests 12, 6654+655 ✓.

Note: BJ13's speech regions include "Ｗｉｆｉｘ" — the WiFi print on the wall... interesting, and "第１９話徳ちゃんと先生" title. Fine.

Wait — BJ13's 3 speech regions: "いやー、" (from... hmm the page had no dialogue balloons per feature_notes "no dialogue balloons"!). The page is the lead page with the man sitting; the OCR "いやー、" and "Ｗｉｆｉｘ" come from... the "WiFi" print on the wall/desk and maybe some small text. And feature_notes says "no dialogue balloons" — but 3 speech regions were detected. Minor internal inconsistency: cases.json BJ13 feature_notes claims "no dialogue balloons" while the run detected 3 speech regions (likely from signage/prints). Hmm, actually looking at the preview image: the desk has a paper/document and a wall poster with text (the "Ｗｉｆｉｘ" print), plus the phone/computer. So "no dialogue balloons" is accurate (no speech bubbles from characters) but there is non-balloon lettering. The feature_notes says "no dialogue balloons" — OK, that's technically defensible; the detector's "speech" regions came from printed signage (WiFi) and possibly the poster. Note: the tag "complex_background" etc.

Hmm, but interestingly, that means BJ13's "speech" region set includes a WiFi sign print and title — and its "sfx" region is the T-shirt print. So this page is a somewhat noisy test asset. The report acknowledges the T-shirt false positive.

Now BJ15 grep. Let me check BJ15: 7 speech regions, requests 14, 7724+700. And check whether there are zero sfx regions ✓ (report says 7+0).

Let me also check the run logs (bj06-run/run.log and new-assets-run.log) to verify the log claims. And check the `qual-report.json`.

And I should verify the range discipline claims: 18 files全允许面, manifests 只增. The diff file list: 18 files:
1. doc/handoffs/M2-SFX-E2E-MATERIAL-40a8ceec.md (new)
2. doc/tasks/M2-SFX-E2E-MATERIAL.md (modified: status + 2 text edits)
3. experiments/M2-SFX-E2E-MATERIAL/diagnose_sfx_detect.py (new)
4. experiments/.../register_new_cases.py (new)
5. experiments/.../render_vol_pages.py (new)
6. experiments/.../run_new_asset_e2e.py (new)
7. test_assets/comic_golden_suite/manifests/cases.json (append)
8. verification/.../bj06-run/run.log
9. verification/.../bj06-run/summaries/qual-BJ06.json
10. verification/.../bj06-run/summaries/qual-report.json
11. verification/.../material-inventory.json
12. verification/.../new-assets-run.log
13. verification/.../new-assets-run/summaries/new-asset-report.json
14. qual-BJ13.json
15. qual-BJ14.json
16. qual-BJ15.json
17. sfx-detect-diagnosis.json
18. sfx-e2e-report.md

= 18 ✓ matches "18 files". Good. No src/tests/contracts/packaging/apps/STATUS touched ✓ (verify by file list: none). Also note the task file edit includes a fix of "dialogue-readability-worksheet" → "dialogue-readiness-worksheet" (line 74) — a doc correction. Is that within allowed paths? The Task allowed modifying the task file (status frontmatter) presumably. The diff shows -2/+... Let me check the exact task-file changes: line 65 status ready→delivered_in_review, line 26 of handoff... and line 74 worksheet name fix, plus appended 交付记录 section. The claim "−2 为 Task 文件回填的 frontmatter/正文替换" — the diff for the task file shows 3 hunks: status change (1 del/1 add), the worksheet name fix (1 del/1 add), and the appended records (+9 lines, 0 del). Total: -2 lines ✓ consistent with "+5618/−2".

Wait, the review input says diff is 18 files +5618/−2. The handoff says 17 files +5569/-2 for the implement commit, then handoff commit adds the handoff file (49 lines) → 18 files, +5618 ✓ (5569+49=5618 ✓). Nice consistency check.

Now, range discipline: is experiments/ an allowed path? The Task frontmatter presumably lists allowed paths. Let me read the task file to check 允许修改路径 and AC definitions. This is important for the range discipline review: e.g., does the Task allow modifying `test_assets/comic_golden_suite/manifests/cases.json` and writing into `test_assets/comic_golden_suite/日漫_JA/...` (gitignored pixels)? Let me read the task file fully.

Also read the task's AC list to verify AC1-AC4 claims against what the task required.

Let me read doc/tasks/M2-SFX-E2E-MATERIAL.md in the worktree.
dsh: reasoning:
BJ15: 7 speech, 14 requests, 7724+700 ✓.

Task file: 允许修改面 includes verification/M2-SFX-E2E-MATERIAL/**, experiments/M2-SFX-E2E-MATERIAL/**, test_assets/comic_golden_suite/** (and manifests/**), Task/Handoff ✓. The 18 files all fall in these allowed surfaces ✓ (doc/handoffs, doc/tasks, experiments/M2-SFX-E2E-MATERIAL, test_assets/comic_golden_suite/manifests/cases.json, verification/M2-SFX-E2E-MATERIAL/**). ✓

Note the AC4 in the task says "成本预算：BJ06 全链 ≈34 region×2 请求≈70 请求 + 新素材端到端单页——合计 est token 预算 10 万内". Actual: 68 requests, 40,735 tokens. Hmm, "≈34 region×2 请求≈70 请求" is odd — 34 region×2 = 68 requests... the task text seems to have garbled the arithmetic (region count is 17, ×2 = 34 requests for BJ06 ✓ which is what happened; the "≈34 region×2 请求≈70" would mean 68). Anyway, actual BJ06 = 34 requests, total 68 including new assets. The budget is on est token (100k) → 40.7% ✓. Fine.

Interesting: the budget item said "BJ06 全链 ≈34 region×2 请求" = 68 requests for BJ06 alone? Then total would exceed 70. Meh — the task text is internally loose. Actual 68 total requests. Not a finding per se, but I could note the request-level budget line in the Task (line 28) is ambiguous and the report's "68 请求" happens to coincide with the task's "≈70 请求" number; not worth much. Actually it's worth a P4 note: the Task's cost budget is expressed in est tokens (10万) while its request estimate (≈70) is a by-product; the report correctly compares to the token budget. Fine, skip or minor.

Now, one important remaining check for AC1: "SFX gate 放行 8/8（sfx_policy 字段实测 skip→translate）" — verified: current run sfx regions have sfx_policy=translate, and first-run had skip ✓. Mechanism evidence: the field is set by the reassemble stage with policy translate; the run.log has "[BJ06] sfx_policy_reassemble: OK {'policy': 'translate'}" ✓. However — does "sfx_policy" field presence prove the *gate* released translation? The actual proof of gate release is that translated_text is non-empty for the 8 sfx regions while in the first run (skip) they were empty. ✓ Strong.

"final_source=machine" = translation produced by machine (not manual). The report/handoff glosses it correctly (翻译产出非人工). Is there a contract doc defining final_source values? Maybe worth verifying terminology: final_source could be "machine"/"manual"/"none". In first run final_source="none" for skipped regions ✓, so machine = machine-translated. The handoff statement "final_source=machine（翻译产出非人工）" is consistent with the observed data. ✓

Now let me double-check "17/17 region 零 defect". What is "defect"? Need to see qual-report.json and run.log. [BJ06] details: OK {'ocr': 17, 'translated': 17}. Hmm "translated: 17" in run.log vs the first run's 'translated': 9. So in the current run all 17 regions got translated. But wait — the speech 9 + sfx 8 = 17 ✓ all translated. So "17/17" refers to translated count. Where does "零 defect" come from? Possibly a run1 "defects" concept in the harness. Let me check run_qualification.py to see if there's a defect notion (maybe in KO-RERUN report there's "defect" terminology for region-level defects). Let's grep for "defect" in the repo experiments/M2-TA3-B and the summaries.

This matters for the finding about unverifiable "零 defect". Let me grep.

Also check qual-report.json contents.

Also: I should verify the claim "与首跑同 region 数、同类型分布" and _bbox_ identity — I partially verified. Let me read first-run lines 250-340 for the 8 sfx bboxes to compare.

Let me do these in parallel: grep "defect" across repo (main worktree, include *.py,*.md,*.json — maybe restrict to experiments/M2-TA3-B and verification/M2-TA3-B3-KO-FULLRUN), read first-run sfx bboxes, read qual-report.json.
dsh: reasoning:
Verified: first-run sfx bboxes identical to current run's sfx bboxes (paired by reading_order) ✓ — detection deterministic across runs (bbox-level), region_ids differ (regenerated UUIDs). The report says "与首跑逐 region 一致" and "与首跑同 region 数、同类型分布——检测确定性跨 run 复现" — supports bbox/type-level identity. Minor wording precision: region_id values are new, so "逐 region 一致" is true only for order/type/bbox. P4.

"零 defect": the harness attributes failures as `defect:` entries in `summary["attribution"]`. qual-BJ06.json "attribution": [] ✓ — so "零 defect" = no `defect:` attribution entries. That IS supported by evidence: attribution = [] in the summary and "attribution": [] in qual-report.json. Great — so the claim "17/17 region 零 defect" is verifiable via attribution=[]. Actually it's "0 defect" not "17/17 region 零 defect" — a slightly loose phrasing, but supported. So no finding here; I'll note it as verified (attribution=[] is the machine-readable basis). Good — better to be accurate: I'll record it as verified with the note that the machine-readable carrier is `attribution: []`.

Now, remaining checks:

1. K11 相关 claims: "K11 裁决项 7 正面关闭" — verify the KO-RERUN §7.7 item 7 wording. Let me grep KO-RERUN report for "7.7" and "K11".
2. The claim "任务书背景写 9 个 SFX region = 笔误级偏差，KO-RERUN §3.2 口径为 8" — verify KO-RERUN §3.2 mentions 8 sfx regions for BJ06.
3. Range discipline: manifests 只增 — verified via diff (only additions, and insertion at line 6150 within the cases array). Need to confirm no existing case modified: the diff hunk header @@ -6150,6 +6150,220 @@ with context lines 6150-6155 then additions. The last context line is `}` of the previous case and `]`/`}` closing. ✓ +214/-0 ✓.
4. Pixel zero-in-git: the diff has no PNG files ✓ (all 18 files are .md/.json/.py/.log). And .gitignore rule exists — I can verify the .gitignore content in the worktree: test_assets/comic_golden_suite/日漫_JA/.gitignore. Let me read it, and check whether the new pages dir would indeed be ignored by `/01_black_jack_official/`. Also verify that the BJ pages directory is not tracked in git (can't check git, but the diff shows no pixels).
5. Key leak scan: check the diff/logs for any API key patterns. Let me grep the verification dir for "sk-" or "api_key" values. The qual-report says credential: env. Let me grep the whole diff for "sk-" / "key".
6. scrub_secrets usage — in the harness, not in this diff. The run.log contains no key ✓.
7. Cost claim: 68 requests/40,735 ✓ verified arithmetic.
8. Check the "221 页目检" claim: thumbs contain p0001..p0221? glob showed 281 paths; the 100 shown ended at p0099. Let me grep the spill file for the last page number and count of thumbs pages. Also verify 7 contact sheets ✓ seen (p0001-0035, 0036-0070, 0071-0105, 0106-0140, 0141-0175, 0176-0210, 0211-0221 = 7 sheets, 221 pages ✓).
9. Verify the 9 candidate pages in material-inventory (48,53,60,96,101,158,159,160,161) = 9 ✓. And check that thumbs/inspect contains evidence of the 9 candidates' re-inspection at 100dpi — glob showed only "thumbs-vol03/inspect/p0159-sfx-zoom.jpg". Hmm! material-inventory says "9 candidate pages re-rendered at 100dpi" and report §2.1 says "100dpi 复查件+zoom 裁片" in thumbs-vol03/. But glob results (281 files) only showed one file in thumbs-vol03/inspect: p0159-sfx-zoom.jpg. Let me grep the full spill list for "inspect" and "100" to see all files under thumbs-vol03/inspect.

That could be a finding: the 100dpi re-inspection evidence for the other 8 candidates appears absent (only 1 zoom file). But the glob list was truncated to 100 of 281 and the spill file has the full list; my grep on the spill file for "inspect" wasn't included (I grepped for manifest|license|previews|pixels|grid|100dpi|zoom — "zoom" matched p0159-sfx-zoom.jpg only). Let me grep the spill file for "inspect" and "p00" to enumerate.

Let me also check the render-final-manifest.json and thumbs-vol03/render-manifest.json for the 9 candidates (100dpi) and 221 pages.

Let me run those greps/reads.
dsh: reasoning:
Good: 9 inspect pages present (p0048, p0053, p0060, p0096, p0101, p0158, p0159, p0160, p0161) in both .png and .jpg ✓ matching the 9 candidates in material-inventory ✓. Plus p0159-sfx-zoom.jpg ✓. So the visual scan evidence is complete for 9 candidates. Good — that closes the "9 candidates re-inspected" claim.

Now find the KO-RERUN report. Let me glob for KO-FULLRUN / KO-RERUN docs. The task mentions "KO-RERUN §7.7" and "KO-RERUN 报告 §3.2". Let's find the file.
dsh: reasoning:
Found ko-rerun-report.md. Let me check §3.2 (the "8 个有文本 sfx region" reference at line 108 — actually line 108 is in some section) and §7.7 item 7.

Let me grep for section headers and read the relevant parts.
dsh: reasoning:
Verified:
- KO-RERUN §3.2 line 108 says "ja BJ06 类素材（8 个有文本 sfx region）" ✓ → the "8" caliber claim checks out.
- §7 裁决项 7 (line 173): "K11 sfx.policy=translate 端到端素材路线（ja BJ06 或新素材，非 ko 范围）" ✓ → the "K11 裁决项 7 正面关闭" claim is about this item. The current task delivers ja BJ06 e2e + new material pooling. Reasonable closing, though strictly item 7 says "素材路线" — the task delivered that (ja BJ06 route + new material). Note: the KO-RERUN §3.2 also emphasizes that in K11 the gate release was *inferred*, not proven by a translate step ("放行为推断——该 region OCR 为空...无 translate step 实证"). Now BJ06 proves a real translate step for sfx regions (translated_text non-empty, final_source=machine) ✓. Strong positive closure.

- Also KO-RERUN's "合法重译" finding under similarity gate: yes, they observe "语义等价合法重译" for K11 (min=0.4615) — the report's §1.4 analogy to that form checks out ✓.

Also note KO-RERUN itself explicitly corrected the wording "放行为推断" (r1 R9). Interesting for the review: the current report's §1.1 claims "gate 放行 8/8（sfx_policy 字段 skip→translate 实测）". In BJ06, unlike K11, there IS a real translate step for sfx regions (translated_text non-empty) — so "放行" is now proven by the translate output, stronger than KO-RERUN's inference. But strictly, the mechanism evidence offered is the field value + non-empty translations; the sfx_policy field alone is config. The report's §1.1 table says "gate: sfx region sfx_policy 字段实测 translate ×8（首跑全 skip）" and "落库: 8/8 非空". Together this is adequate proof of gate release for a translate-policy run. However, one nuance: does the pipeline record an explicit gate decision (e.g. gate_decision field, or SKIP reason) anywhere? The first run's sfx regions had final_source "none" and translated_text "" (skip → SKIP reason). Let me check whether the summaries contain sfx_skip_reason in the first run for skipped regions; if so, in the current run there would be no skip reason. Not critical.

One more mechanism check: is `sfx_policy` per-region set at *import/reassemble* time (i.e., the same in both runs for all regions, so the change is caused by the run config)? Both runs used the same base settings except policy. Yes: first run all sfx regions skip; the current run all sfx regions translate ✓. Good.

Now let me check a subtle thing on the "sfx_policy 字段实测 skip→translate 落库+门放行" — that's verified.

Remaining: 
(a) key leak scanning: grep the diff for secret-ish patterns.
(b) The `run.log` in bj06-run — note it contains "[BJ06] details: OK {'ocr': 17, 'translated': 17}" ✓ consistent.
(c) Check new-assets-run.log.
(d) Check the .gitignore rule for pixels.
(e) Check possible flaw in register_new_cases.py's pipeline_status_of: "ocr": PASS if run2_ok... redundant; and "text_detection"/"region" PASS if summary["regions"]; "sfx" PASS based on policy only. Also — potential issue: if register script were re-run after cases exist → it fails closed ✓. Also, `data = json.loads(raw)` then re-dump; if the existing file had non-ASCII escapes or different key order... json.dumps preserves insertion order of loaded dicts ✓. But one risk: if the original used ensure_ascii=True escapes for Japanese, rewriting with ensure_ascii=False would produce a huge diff. The diff showed only +214, so the original must already be ensure_ascii=False. ✓ (Confirmed by diff: only additions, and the new entries contain raw Japanese, and context lines include raw "日漫_JA" — indeed line 878 context shows "02_open_ground_truth_peppercarrot" ASCII... hmm, but the new entries include 「ブラックジャックによろしく　佐藤秀峰」 unescaped ✓ and BJ06 existing entry has 日漫_JA unescaped ✓ (line 4824). Good, so format is consistent.)

Wait — one thing to verify: the diff shows the insertion at the end of the "cases" array; the new entries are appended after the last existing case ✓ (line 1093-1095 context `}` `]` `}`). ✓

(f) Check the BJ13/14/15 file/`sha256` consistency between cases.json, material-inventory.json and the render-final-manifest.json (external). I can check render-final-manifest.json for the 3 pages' sha256 to verify they match cases.json. That's a strong cross-check of "逐页 sha256 入 material-inventory.json" claim. Let me read render-final-manifest.json.

(g) Verify the claim "像素入本 worktree gitignored 套件目录" — check .gitignore.

Let me do these three reads/greps.
dsh: reasoning:
Big finding candidate: render-final-manifest.json generated_at_utc "2026-10-02T00:11:29Z" — but wait, the BJ06 run was 00:07:01Z–00:18:36Z, and the new-assets run 00:18:50Z–00:33:35Z. The render manifest at 00:11:29Z falls INSIDE the BJ06 run window. Hmm, that's plausible if rendering happened concurrently... but more importantly, the new-assets run at 00:18:58 local log line ("2026-10-02 08:18:58.891" local) — and log says BJ13 started after BJ06 finished. OK.

Crucially: new-assets-run.log lines 8/29/47 show local timestamps 08:18:58, 08:22:29, 08:27:39 → local = UTC+8 → 00:18:58Z, 00:22:29Z, 00:27:39Z ✓ consistent with new-asset-report generated 00:18:50Z start.

And run.log (bj06) local 08:07:10 → 00:07:10Z ✓.

So local time = UTC+8 confirmed. Now:
- render-final-manifest.json generated_at_utc 00:11:29Z = local 08:11:29 → that's during the BJ06 run (00:07–00:18Z). Plausible (parallel work) but note: the render of the 3 final pages happened at 00:11:29Z, i.e., AFTER the license snapshot capture claimed at 08:07Z (=00:07Z if local) — fine, license first ✓ under reading B. Under reading A (snapshot truly 08:07Z), the snapshot postdates everything. Since local time is UTC+8 as just verified, and the author's other files use true UTC ("Z") for run summaries... hmm, the run summaries' UTC comes from the harness (datetime.now(timezone.utc)), while the manually-authored material-inventory timestamps ("2026-10-02T08:20:00Z", "snapshot_captured_at": "2026-10-02T08:07Z") were typed by the author. Given the machine's local time is UTC+8, and the render manifest (00:11:29Z, from the script using datetime.now(timezone.utc)) shows the render happened at local 08:11:29 — the author's hand-written "08:07Z" for the license snapshot and "08:20:00Z" for inventory are almost certainly LOCAL times mislabeled with "Z". Indeed: the license snapshot at local 08:07 would be 00:07Z — the same minute the BJ06 run started. Hmm, that's a suspicious coincidence but plausible (the author captured the license snapshot first, then started BJ06).

Wait, but can I tell whether the snapshot was captured before or after? The snapshot file was the first entry in the mtime-ordered glob... Ordering ambiguity. Let's test the glob ordering hypothesis using known timestamps within task-envs: render-final-manifest.json (00:11:29Z) vs detect-diag-previews (00:35:46Z) vs pixels/export/BJ06-translated.png (export at 00:18:36Z per summary). In the spill list order: license-evidence(line1) < thumbs pages < grids.. < render-manifest.json(230) < grid jpgs(231-237) < inspect pngs/jpgs(238-255) < render-final-manifest.json(256) < pixels/ocr/crops/BJ06/*(257-273) < pixels/export/BJ06-translated.png(274) < inspect/p0159-sfx-zoom.jpg(275) < detect-diag-previews/BJ13..15(276-278).

So order: render-final-manifest (00:11:29Z) then BJ06 export png (00:18:36Z) then p0159-sfx-zoom.jpg then detect-diag-previews (00:35:46Z). That's ASCENDING mtime! Great: the glob returns ascending modification time. Then license-evidence snapshot is the OLDEST file in the task-envs tree — which supports "许可快照先行" (captured before thumbnails/render) ✓✓. And p0159-sfx-zoom.jpg (line 275) is after the BJ06 export but before detect-diag — consistent with post-run zoom confirmation? Hmm, the zoom was part of AC2 visual scan which should precede the runs... but it was modified after? Maybe it was re-saved. Minor.

Under ascending-mtime ordering: snapshot oldest → license first ✓. Then thumbs (40dpi, oldest after license) → grid sheets → inspect (9 candidates at 100dpi) → render-final-manifest → ... consistent with the described workflow order: license snapshot → 40dpi thumbs → contact sheets → 100dpi inspect → 150dpi final render (00:11:29Z).

Hmm wait, but the order shows thumbs pages first, then grid .png, then render-manifest.json (230, in thumbs-vol03), then grid .jpg, then inspect... This suggests: (1) 40dpi render of all pages (thumbs pages), (2) grid .png sheets, (3) render-manifest.json written at end of that run, (4) grid .jpg conversions, (5) inspect 100dpi pages. All pre-BJ06-render. OK: so license-first holds under the ascending-order reading.

So my earlier timestamp-skew concern: material-inventory.json "generated_at_utc": "2026-10-02T08:20:00Z" and "snapshot_captured_at": "2026-10-02T08:07Z". If those are local (UTC+8) labels, actual = 00:20:00Z / 00:07Z. But the inventory must have been written after all evidence (it's a summary)... 00:20Z would be during the new-assets run, and the report was written after 00:35Z. Hmm, if the author typed 08:20 as local = 16:20... no, local at that time was 08:20 (UTC+8). Ugh: the author worked at local 08:07-08:5x on 2026-10-02 while UTC was 00:07-00:5x. So material-inventory's "08:20:00Z" is plainly a local-time value with a wrong Z suffix. Same for "snapshot_captured_at 08:07Z" (local 08:07). And the material-inventory says generated 08:20 (local) which is *before* the diagnosis (local 08:35) and before the report — plausible.

So finding: timestamp fields in material-inventory.json (and the license snapshot's captured_at) are written in local time but suffixed "Z", inconsistent with the UTC timestamps in the run summaries (8-hour skew). Consequence: the "license snapshot 先行" ordering cannot be confirmed *from those fields* (it reads as if the snapshot postdates the runs by 8h). Evidence for local-time reading: new-assets-run.log local 08:18:58 vs summary UTC 00:18:5x; render-final-manifest 00:11:29Z vs its own log? Well the render manifest is generated by the script with true UTC. And the thumbs render-manifest? Let me check thumbs-vol03/render-manifest.json's generated_at — if the script generated it with UTC, it should be ~00:0x. Let me read it to cross-check. Also I can verify the license snapshot's actual mtime ordering only via glob inference (weak). I'll report the timestamp inconsistency as P3 (documentation discipline, not evidence falsification) and note that the *chain* suggests snapshot-first but the labeled times contradict it.

Hmm, actually, let me reconsider: maybe the author's claim "snapshot_captured_at 08:07Z" is intentional and the snapshot really was captured at 08:07Z (16:07 local), i.e. AFTER the runs — but that would break the license-first discipline claim (material used at 00:11-00:33Z before license verification at 08:07Z). The report §2.2 says "快照：densho810.com/free/ 2026-10-02 抓取". The handoff says "许可一手快照先行". The mtime ordering (ascending) suggests the snapshot file is the oldest in the whole tree — supporting actual-先行. But "oldest in tree" also includes thumbs which were created just after. So the snapshot is older than thumbs → license before material download/render ✓. So the effective ordering holds by mtime; only the printed timestamp is skewed. Good: I'll present it as a label inconsistency with mtime evidence supporting 先行, and mark the exact ordering as low-severity.

Hmm, one more caveat on the glob ordering: the doc says "Returns up to 100 paths in modification-time order" — it returned 100 of 281 and said the full list is stored. The full list is the spill file (281 lines?). Let me check the spill file length. The ordering is presumably consistent. Fine, I'll describe it as "mtime 顺序（升序）" with the caveat.

Now: .gitignore check — my glob for test_assets/comic_golden_suite/日漫_JA/.gitignore found nothing. Glob searches files matching the pattern; a dotfile should match if it exists. Hmm, "No files found" means the file doesn't exist at that path? But material-inventory claims "files ignored by test_assets/comic_golden_suite/日漫_JA/.gitignore rule /01_black_jack_official/". Maybe glob excludes hidden/ignored files? The tool says "including hidden and ignored files". Let me search more broadly: glob pattern "**/.gitignore" in the worktree, and also grep the main repo for "01_black_jack_official" in .gitignore files.

Let me check.
dsh: reasoning:
Confirmed: thumbs render-manifest generated at 00:08:09Z (true UTC, by the script), i.e., after the license snapshot step (per author's intent) and *during* the BJ06 run (00:07:01-00:18:36Z). Hmm — the 40dpi thumbnails of 221 pages took from 00:07 to 00:08:09? That's fast (117 seconds for 221 pages at 786x1112) — plausible.

Wait, this raises a subtle point: the BJ06 run started 00:07:01Z and the thumb rendering finished 00:08:09Z — concurrent. Fine.

So the mtime-ascending reading holds and the license snapshot is older than thumbs (which are 00:07-00:08Z). So the snapshot's real capture time is ≤ 00:08Z; its label says 08:07Z. Two candidate reconstructions: (a) label is local-mislabeled → real 00:07Z (=just before thumbs) ✓ consistent with mtime ordering and the workflow; (b) label is true UTC → 08:07Z, which contradicts mtime ordering (snapshot older than thumbs created at 00:08Z). Since mtime ordering shows the snapshot older than files created at 00:08Z UTC, (a) must hold: the snapshot label is local time mislabeled as UTC. 

So the finding is now solid: material-inventory.json's `snapshot_captured_at: "2026-10-02T08:07Z"` and `generated_at_utc: "2026-10-02T08:20:00Z"` are local-time (UTC+8) values carrying a "Z"/UTC label; every other artifact in the tree uses true UTC. Actual UTC ≈ 00:07Z and ≈ 00:20Z... hmm, but generated_at 08:20 local = 00:20Z, which is when the new-assets run was in progress (BJ14 started ~00:22Z). But material-inventory describes the final render manifest (00:11:29Z) — so it must have been written after 00:11Z ✓ consistent with ~00:20Z. ✓ Good, reading (a) is fully consistent.

Interestingly, the report says §2.2 snapshot captured 2026-10-02 and material-inventory's own date; the discrepancy is only in the Z suffix. P3 finding (documentation/timestamp hygiene) — affects the ability to audit "license-first" ordering from the document itself; I verified ordering via mtime instead.

Now the .gitignore: exists at test_assets/comic_golden_suite/日漫_JA/.gitignore (earlier glob with the exact pattern failed maybe due to path separator/normalization). Let me read it to verify the rule "/01_black_jack_official/". And check that the new pixels are inside the ignored dir. Also verify whether these pixels are actually untracked — the diff has no PNGs, so they're not in the commit ✓ (in the diff). But "gitignored" matters because otherwise they'd be untracked-but-uncommitted files; the claim is check-ignore verified. Static evidence: .gitignore rule ✓ + no PNG in diff ✓.

Let me read the .gitignore and also grep the diff for any key-like strings (leak scan) and check for "sk-" patterns.

Also, I want to double check the BJ06 "gate 放行" mechanism by looking at the source gate implementation? The task says zero src changes; the gate is pre-existing (DETECT-EVAL §4.1 verified decide_sfx_translation). No need.

One more: "speech 9/9 对照" is verified. "SFX 家族全链闭环" claim: DETECT→PROD→SEM→ENTRY→PRIMARY. The report says "SFX 家族 DETECT→PROD→SEM→ENTRY→PRIMARY 的 ENTRY 之后各段在 ja 域无遗留缺口". Hmm, but "PRIMARY 门全域" — the gate release evidence for sfx regions here is real ✓. Note the SFX-SEM-1 specialization: is there evidence that the SEM-1 prompt specialization was actually applied to those 8 sfx regions (vs the normal dialogue prompt)? The report claims "SEM-1 prompt 特化" as part of the chain. Is that machine-verifiable from the artifacts? The translate_details have final_source=machine but nothing indicating the SEM-1 prompt was used. There might be a "prompt_kind"/"provider" field. Let me check the translate_details structure in qual-BJ06.json (lines 1428-1582) for fields like "provider_id", "prompt_profile", "instruction_id". Let me read one sfx entry fully (lines 1505-1535) and one speech entry.

That's a good check: does the artifact evidence SEM-1 特化 (i.e. that sfx regions used the SFX prompt rather than the speech prompt)? If not present in the artifact, the "SEM-1 prompt 特化" claim rests on the harness's implementation, i.e., unverifiable statically from the evidence → NOT_VERIFIED or a P3 finding about missing mechanism evidence. Let me look.

Also check the "SFX-TRANSLATE-ENTRY" control: run.log "sfx_policy_reassemble: OK {'policy': 'translate'}" ✓.

Let me read translate_details entries in qual-BJ06.json (the sfx ones) fully.
dsh: reasoning:
.gitignore rule "/01_black_jack_official/" ✓ confirmed at line 26. So the new pages under 日漫_JA/01_black_jack_official/vol03/pages are ignored ✓, consistent with "像素不入 git".

Note: translate_details for the sfx entries contain only region_id/region_type/sfx_policy/source_text/translated_text/final_translation/final_source. There's NO field evidencing SFX-SEM-1 prompt specialization (no prompt/profile/instruction id). Let me check the speech entries similarly (lines 1432-1510: region_id, region_type, sfx_policy, source_text?, translated_text, final_translation, final_source). Let me look at one speech entry: line 1432-1437 showed region_type/sfx_policy/translated_text/final_translation/final_source but I didn't see source_text — grep showed "source_text"? My earlier grep pattern didn't include source_text. Let me check a speech entry to see if source_text exists. Not critical.

Key point: the artifacts do NOT record which prompt/specialization was used per region. So the claim "SEM-1 prompt 特化" is not independently verifiable from the delivered evidence; it rests on the harness code path (which is pre-existing, unchanged, and was reviewed in earlier tasks). I'll file it as a P3 finding / partial NOT_VERIFIED: evidence for the SEM-1 specialization step in the chain is not in the summary JSON (no prompt/profile identifier), so the "全链闭环" claim's SEM segment is inferred from the harness implementation rather than from the artifacts. The report's §1.3 table compares outputs "对照 SFX-SEM-1 的 ≤6 字符/禁直译规范" = output-side compliance check, which is fine, but the mechanism (that the SFX-specific prompt was used) is not recorded. Let me verify whether the qualification harness records such a field anywhere, e.g. grep experiments/M2-TA3-B/run_qualification.py for "SEM" or "sfx_prompt" or "prompt".

Let me also verify that the pipeline actually routes sfx regions to a specialized prompt in the production code — grep src for sfx prompt specialization (src/.../translation/...). If the mechanism exists in src (read-only), the claim is plausible; but the evidence artifact doesn't pin it. Let me do a quick grep.

Also check the diff leak scan: grep the diff for suspicious strings.

Let me batch: 
1. grep src for "SFX_SEM" / sfx prompt specialization.
2. grep the diff file for "sk-" / "API_KEY" / "Bearer".
3. grep run_qualification.py for "prompt".
dsh: reasoning:
Leak scan: no `sk-...` keys, no Bearer tokens. Only path references to `deepseek.key` (a file path, not content) ✓ consistent with "key env 注入+scrub_secrets、leak 扫描 CLEAN" — statically I can confirm no key material in the diff. Good.

Two notable findings from these greps:

1. **Path inconsistency in the new-assets run summaries**: pixel_path/crops_dir for BJ13/14/15 = `G:\CODEX\New Manga.task-envs\M2-TA3-B\M2-SFX-E2E-MATERIAL\pixels-new-assets\...` whereas the report §1.1 / run_new_asset_e2e.py default is `PIXEL_ROOT_DEFAULT.parent / "M2-SFX-E2E-MATERIAL" / "pixels-new-assets"` → PIXEL_ROOT_DEFAULT.parent = task-envs/M2-TA3-B, so the actual path is task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/pixels-new-assets. But the report §6 证据物 table says "像素产物 Git 外 task-envs/M2-SFX-E2E-MATERIAL/pixels*/" — i.e., the report claims pixel products are under task-envs/M2-SFX-E2E-MATERIAL/, but the new-asset pixel root is actually under task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/. And the handoff says "独立 out-dir/pixel-root". Let me verify which path exists: the glob of task-envs/M2-SFX-E2E-MATERIAL showed `pixels\export\BJ06-translated.png` (BJ06) but I didn't see pixels-new-assets under it. The glob returned 281 paths, 100 shown; the spill list I grepped for "pixels" showed only lines 257-274 (pixels\...\BJ06). So under task-envs/M2-SFX-E2E-MATERIAL there's no pixels-new-assets → the new-asset pixels are at task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/pixels-new-assets/.

So:
- Report §6 line 166: "像素产物 | Git 外 `task-envs/M2-SFX-E2E-MATERIAL/pixels*/`（crops+exports）" — this lists the BJ06 pixel root; the new-assets pixel root is under a different parent (task-envs/M2-TA3-B/...). Minor documentation inaccuracy, and also a small hygiene issue: the default pixel root nests a task-named dir under the *harness* task-env dir (a bit odd, since M2-TA3-B is a different task's env tree — meaning this task wrote outside its own task-env dir!). Hmm! Interesting: the handoff claims "像素入本 worktree gitignored 套件目录、源 PDF（TA2B worktree）只读引用——本 worktree 以外零写入". But writing pixels into `task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/pixels-new-assets` IS a write outside this worktree (into another task's env tree, M2-TA3-B). And the BJ06 run wrote to task-envs/M2-SFX-E2E-MATERIAL/pixels ✓ (own task env). So the claim "本 worktree 以外零写入" is contradicted by the new-assets pixel root path under task-envs/M2-TA3-B/ (another Task's directory). Is task-envs/M2-TA3-B this task's own env? The task-envs naming is per-task; M2-SFX-E2E-MATERIAL's own env dir is task-envs/M2-SFX-E2E-MATERIAL. The venv is at task-envs/M2-TA3-B-ocr (shared env, established in earlier tasks). But writing the pixel root into task-envs/M2-TA3-B/ is a cross-task write into the harness task's env directory.

Hmm, is that within the Task's "允许修改面"? The allowed surfaces are repo paths (verification/, experiments/, test_assets/...) and the pixel discipline says pixels go to git-external tree. Writing to another task's git-external env tree isn't a repo-file violation but it does contradict two claims: (i) "本 worktree 以外零写入" (handoff §AC2 item 4, task file line 48) — technically false if the pixel root is under task-envs/M2-TA3-B/; and (ii) report §6's pixel path listing. Severity: P3 (discipline/documentation honesty) — the substance (pixels outside git ✓) holds, but the "zero writes outside this worktree" claim isn't accurate; the pixel root is a subdirectory of a *different* task's env tree. Wait — is it possible that the author intended PIXEL_ROOT_DEFAULT.parent to be task-envs/... let me verify PIXEL_ROOT_DEFAULT in run_qualification.py to be sure that M2-TA3-B is the parent. Let me grep.

Actually, the summary JSON itself says the path: `G:\CODEX\New Manga.task-envs\M2-TA3-B\M2-SFX-E2E-MATERIAL\pixels-new-assets\export\BJ13-translated.png`. That's definitive. So the pixel root used is task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/pixels-new-assets.

Hmm, but was that decided in the script default: `PIXEL_ROOT_DEFAULT.parent / "M2-SFX-E2E-MATERIAL" / "pixels-new-assets"`. If PIXEL_ROOT_DEFAULT = task-envs/M2-TA3-B/pixels, parent = task-envs/M2-TA3-B. So yes, default nests under M2-TA3-B. Let me confirm PIXEL_ROOT_DEFAULT. If instead PIXEL_ROOT_DEFAULT = task-envs/M2-TA3-B/M2-TA3-B/pixels... let me just check.

Also there's a consumer-visible consequence: BJ13/14/15 export PNGs live in a directory inside the M2-TA3-B task env tree, and the report's §6 inventory points at the wrong parent (task-envs/M2-SFX-E2E-MATERIAL/pixels*/). For a future reader, the pixel products of AC3 are at a path the report doesn't give. This is a legitimate P3 finding (evidence-path traceability).

Let me confirm PIXEL_ROOT_DEFAULT and also verify that task-envs/M2-SFX-E2E-MATERIAL has no pixels-new-assets dir (from glob: the listing at line 257 was pixels\..., and after line 274 came inspect/zoom and detect-diag-previews; so within M2-SFX-E2E-MATERIAL there's no pixels-new-assets ✓ — but the glob might have been sorted by mtime, so a pixels-new-assets dir under M2-SFX-E2E-MATERIAL would still appear. It didn't. Let me also do a targeted glob to be sure.

2. Also worth checking: the BJ06 summary's `source_path` points to the TA2B worktree page file and `source_sha256` b06c9d7d… — matches cases.json BJ06 page_sha256 ✓ (verified earlier: b06c9d7ddb0f… ✓).

Now let me finalize a few remaining checks:
- PIXEL_ROOT_DEFAULT confirmation.
- glob for pixels-new-assets under both trees.
- Check run_qualification.py's `--sfx-policy` handling? Not necessary.
- Check the handoff's "18 files 全允许面" and "manifests 只增不改" claims: verified.
- Verify the claim "cases.json 97→100": existing count 97? The diff context @@ -6150,6 +6150,220 @@ and the file now has 6369 lines with 100 cases. I can count case_id occurrences: BJ01-BJ15 is 15; total 100 per claim. Let me count `"case_id":` occurrences in cases.json via grep (grep returns up to 250 matches; there are 100 — fine). Let me do that to verify 100 and that BJ13-15 are the only new ones (order). Actually the claim is 97→100 which I can verify: count = 100 ✓ if grep returns 100 matches. And the diff adds exactly 3 case blocks ✓.

Let me batch these final checks.
dsh: reasoning:
100 case_ids ✓ (97 existing + 3 new). The new ones are appended at the very end after K25 ✓ (line 6155, 6226, 6297) — consistent with the diff insertion point (after line 6150 = end of K25 entry). ✓ "只增" verified.

Also PIXEL_ROOT_DEFAULT at line 96 — let me confirm its value to nail the new-assets pixel-root finding. Let me read lines 90-110 of run_qualification.py.

Also glob for pixels-new-assets under M2-SFX-E2E-MATERIAL returned nothing ✓ — need to confirm it's under M2-TA3-B. Let me glob G:/CODEX/New Manga.task-envs/M2-TA3-B/**/pixels-new-assets/** — that might be many files. Let me just glob for "**/pixels-new-assets/*" in M2-TA3-B.

Also: interesting — case_id "BJ13/BJ14/BJ15" appended after K25, whereas the BJ family is contiguous BJ01-BJ12 earlier. The report says "case_id 沿 BJ 家族顺延" — the ids are sequential within BJ (13/14/15) ✓ but positioned at the file end. Not an issue (append-only requires end placement).

Let me read the PIXEL_ROOT_DEFAULT and glob the M2-TA3-B tree.
dsh: reasoning:
Confirmed: PIXEL_ROOT_DEFAULT = task-envs/M2-TA3-B/phase2-pixels; parent = task-envs/M2-TA3-B → run_new_asset_e2e.py default pixel root = task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/pixels-new-assets ✓ as observed. Crops present for 4/6/7 regions ✓ (17 crops for 17 new regions ✓).

So finding: 
(a) The new-assets pixel unknowns: pixel root is a nested subdir inside the **M2-TA3-B** task env tree, not under this task's own env dir (`task-envs/M2-SFX-E2E-MATERIAL/`). This contradicts the handoff/task claim "本 worktree 以外零写入" (true only in the "本 worktree" sense... wait, it writes outside this worktree, so "本 worktree 以外零写入" is literally FALSE). Hmm, careful: the claim in the task file line 48 says "源 PDF 只读引用（本 worktree 以外零写入）". But writing pixels into task-envs/M2-TA3-B/... is a write outside this worktree. Also the BJ06 run wrote to task-envs/M2-SFX-E2E-MATERIAL/pixels (also outside the worktree!) — but that's the task's own env dir, which is the sanctioned git-external pixel tree. So the claim "本 worktree 以外零写入" can't be literally true; it should read "零写入其他 Task 的 worktree/产物". Given pixel discipline explicitly sanctions git-external pixel roots, the intent is "no writes to other agents' worktrees/artifacts". But the AC3 pixel root lands inside another Task's env tree (M2-TA3-B), which is a deviation from the "own task-env" pattern used for AC1. I'll report this as P3 with precise file:line refs and note the substance (pixels outside git, no cross-task *artifact* modification) still holds — the M2-TA3-B tree gets a new nested subdirectory but no existing file is modified... I can't prove no modification without git; the diff shows zero repo changes. Mark as P3 discipline/precision + recommend correcting the claim + report §6 path.

(b) Report §6 line 166 lists pixel products as `task-envs/M2-SFX-E2E-MATERIAL/pixels*/` — the AC3 pixels aren't there. P4/P3 documentation accuracy.

Now let me also double check the "T 恤印花" claim vs the material-inventory: it's not in material-inventory (only in report). Fine.

One more thing to check: the report claims "chiqui7 检出 17 region（8 sfx + 9 speech，与首跑逐 region 一致）" — verified (order/type/bbox identical; region_ids differ). Also the report's §0 table says "chiqui7 检出 17 region（8 sfx + 9 speech，与首跑同分布）" in §1.1 — fine.

Another check: "speech 16 region 翻译正常" for AC3 = 3+6+7 = 16 ✓.

Also the claim "BJ13 sfx region 1/1 落库『．．．』→『……』" ✓ verified.

Now, additional review points to consider:

- AC1's SFX region count discrepancy (9 vs 8): the Task text (background) says 9 SFX regions; measured 8. The report registers it as "笔误级偏差" citing KO-RERUN §3.2 ("8 个有文本 sfx region"). Hmm — careful: KO-RERUN §3.2 says "ja BJ06 类素材（8 个有文本 sfx region）" — that's "8 regions with text", which does NOT establish that BJ06 has exactly 8 sfx regions total. The claim that the task's "9" is a typo is inferred: the current run shows 17 total = 8 sfx + 9 speech; the task's "9 个 SFX region" probably confused 9 (speech count) with sfx. So the "9" in the task might well have been derived from the same 17-region detection where 9 was the *speech* count, or from the K11 precedent... Either way, the honest handling (report both, use measured 8) is fine. But note: where did "9 SFX region" come from? Possibly from `dialogue-readiness-worksheet` SFX skeleton. Let me check that worksheet to see if it mentions 9 sfx regions for BJ06 — that would clarify whether the "9" was a documented caliber rather than a typo. If the worksheet says something like "BJ06: 9 sfx regions", the discrepancy is a discrepancy between two project documents, and calling it a "笔误" may be unjustified. Let me check the worksheet.

Let me grep the repo for "dialogue-readiness-worksheet" and "9 个" sfx.

Also the task-file edit changed "dialogue-readability-worksheet" → "dialogue-readiness-worksheet" — I should verify the actual filename to see which is correct (if the correct name is "dialogue-readability-worksheet", then the edit introduced an error!). That's a nice concrete check: glob for *worksheet* files.
dsh: reasoning:
Very important finding! Let me parse:

- `verification/M2-TA3-B/quality-report.md:120`: "本 run SFX region 共 9 个（8 BJ06 + 1 K11；r1 R6 修正原「全部在 BJ06」表述——K11:65069961 亦为 sfx region...)". So the documented caliber: BJ06 has **8** sfx regions, K11 has 1 → total 9. So the Task's "已有 9 个 SFX region" is likely a conflation of the "9 SFX region total (8 BJ06 + 1 K11)" figure from the TA3-B quality report. That supports the report's treatment (measured 8 for BJ06, discrepancy registered). Actually the report says "任务书背景「9 个 SFX region」实测 8，与 KO-RERUN §3.2「ja BJ06 类素材（8 个有文本 sfx region）」一致——以实测 8 为准，任务书表述登记为笔误级偏差". The true origin is quality-report.md:120's "9 个（8 BJ06 + 1 K11）" — so the task text merged the total. The report's explanation is close enough but slightly off in attribution (it cites KO-RERUN §3.2 rather than quality-report §3.1 line 120; but KO-RERUN §3.2 does say 8). It's a "笔误级偏差" registration and doesn't affect acceptance. I'd note as a P4 observation: the deviation registration cites KO-RERUN §3.2 but the actual source of "9" is the TA3-B quality-report "9 个（8 BJ06 + 1 K11）" phrasing — worth registering precisely so future readers don't re-open it.

- Another important check: `dialogue-readability-worksheet.csv/json` exists — the task's original text referenced "dialogue-readability-worksheet" which EXISTS. The Task file edit changed it to "dialogue-readiness-worksheet" (which does NOT exist). Hmm! Let me verify: the glob found `dialogue-readability-worksheet.csv/json` and no `dialogue-readiness-worksheet`. So the author's edit renamed the reference from an existing artifact name to a non-existent one! Wait, let me be careful: maybe there's a "dialogue-readiness-worksheet" elsewhere (e.g. in another task's verification dir). The glob searched **/*worksheet* across the whole main repo G:/CODEX/New Manga and returned 8 files, none named dialogue-readiness. But maybe it's in a worktree (not the main repo) — the glob was limited to G:/CODEX/New Manga (the main repo root, not worktrees). Another worktree could have it. Hmm, but the reference is to a project artifact; the main repo should have it if it's a delivered artifact... Let me search the worktrees too (glob on G:/CODEX root would be huge). Let me grep the whole main repo for "dialogue-readiness" and "dialogue-readability" to see which name the project uses.

This is a great concrete finding candidate: the diff changed a correct reference to an incorrect one (or vice versa). Let me check thoroughly. Also the review-input mentions: "任务书背景写 9 个 SFX=笔误级偏差" and the diff line 74 is a rename of the worksheet. Let me grep for both spellings in the repo.
dsh: reasoning:
Confirmed:
- The project-wide artifact name is `dialogue-readability-worksheet` (exists: verification/M2-TA3-B/phase2/translate/dialogue-readability-worksheet.csv/json).
- There is NO `dialogue-readiness-worksheet` anywhere.
- The Task file (in the worktree) now says `dialogue-readiness-worksheet` (line 21) because the diff changed it (line 74 of diff: `-`dialogue-readability-worksheet` `+`dialogue-readiness-worksheet``).

Wait — let me double check the diff direction. Diff lines 73-74:
```
-KO-RERUN §7.7：K11 唯一 SFX region OCR 空=素材缺口。推荐路线=**ja BJ06 先行**（已有 9 个 SFX region，`dialogue-readability-worksheet` SFX 骨架引用过，零新素材）+ 新素材扩展。...
+KO-RERUN §7.7：... `dialogue-readiness-worksheet` SFX 骨架引用过 ...
```
Yes: the pre-image had `dialogue-readability-worksheet` (the CORRECT name) and the post-image has `dialogue-readiness-worksheet` (a name that exists nowhere). So the Owner's "correction" is a **regression**: it broke a valid artifact reference in a background paragraph of a frozen Task document.

This is a solid finding — P2 (a factual regression in a Task doc reference; the change was not required by the ACs and it is wrong). It's low impact functionally but it's an incorrect edit to a Task doc, which is exactly what a reviewer should catch. Also it's within the "Task/Handoff" allowed surface, but the edit itself is unjustified/wrong.

Also worth noting: this is the only "正文替换" in the -2 lines. The handoff claimed "-2 为 Task 文件回填的 frontmatter/正文替换" — but one of those two replaced lines introduced a wrong reference.

Additionally, the diff also changed the same line's content type... only the worksheet name.

Also check: does the `dialogue-readability-worksheet` contain the SFX skeleton with 9 (or 8) items? The worksheet has "SFX 骨架" for BJ06. Line 106 of quality-report said "9 个（全部在 BJ06）" originally, corrected. The worksheet sfx-semantic-worksheet.csv is separate. Let me check the worksheet for BJ06 SFX rows count to see whether it documents 8 or 9 sfx regions — that would inform the "9 vs 8" registration. Actually `sfx-semantic-worksheet.csv` is the SFX worksheet (skeleton). Let me read it — it may have 8 or 9 rows. If it has 8 BJ06 rows + 1 K11 → 9, that exactly explains the "9" in the Task background. Let me check quickly.

Let me read verification/M2-TA3-B/phase2/translate/sfx-semantic-worksheet.csv (probably small).

Then I have enough for the review. Let me also double check the report's §1.2 statement "首跑 BJ06 的 8 个 sfx region OCR 全部非空（いいじゃ/いいん/！！！/．．．×2/ハチン/わ．．．/３．）" ✓ verified against the first-run summary OCR details (same order).

One more: report §1.1 "gate | sfx region `sfx_policy` 字段实测 `translate` ×8（首跑全 `skip`）" ✓ verified.

Report §1.4 "9/9 speech 翻译落库；与首跑（SKIP 门下）对照：8/9 逐位一致，1/9 为合法重译变体（ちょっとおじいさん！？「等一下，老爷爷！？」→「喂，老爷爷！？」...)" ✓ verified exactly.

Report §0 "34 请求 ≈20.2k est token" ✓ verified (18,604+1,642=20,246).

Report §4 table numbers ✓ verified.

Now, the cost budget: "预算 10 万的 40.7%" ✓ arithmetic (40,735/100,000 = 40.735%) ✓.

Remaining review items:
- AC4's "key 零明文（env 注入 + scrub_secrets，产物已抽查无泄漏形态）" — statically verified: no key strings in the diff; scrub_secrets exists in the harness (line 109). ✓ The actual runtime scrub can't be re-verified → NOT_VERIFIED for integration (running the harness and confirming no key in outputs).
- "porcelain clean" / "diff --check EXIT=0" — cannot verify without shell → NOT_VERIFIED.
- git check-ignore — the .gitignore rule verified statically; the actual `git check-ignore` result NOT_VERIFIED.
- sha256 recomputation (snapshot 2bb1dc9f…, PDF 31c37c85…, page sha256s, export sha256s) — page sha256s cross-check consistent across material-inventory / cases.json / render-final-manifest / run_new_asset_e2e.py NEW_ASSET_CASES / the summaries' source sha256_match=True. That internal cross-consistency is strong but the actual digest recomputation needs shell → the values are consistent but not recomputed. However, I do have one independent recomputation route: the read_image tool reported the sha256 of the *normalized copy* of the preview JPEG — not comparable. So mark recomputation as NOT_VERIFIED (integration), while noting five-way internal consistency.

Hmm wait, actually: can I verify a sha256 indirectly? The read_image tool returned "sha256:e20096b6..." for a normalized/re-encoded copy, not the file. Not usable.

- The claimed pixel sizes: material-inventory lists BJ13 size 7,518,623 ✓ matches render-final-manifest ✓. And run logs: BJ13 export size 8,613,251 (that's the exported PNG, not the source). ✓ consistent names.

Now: another check on the license snapshot claim: the report says the snapshot is 32,843 bytes with sha256 2bb1dc9f…. I can't recompute; but I can note the snapshot content includes download links for volumes 1-13 ✓ and the terms ✓. Also verify the snapshot is genuinely the /free/ page: title "ブラックジャックによろしく フリーダウンロード｜..." ✓ and it contains the terms ✓. Also check it's not truncated (e.g., missing the 規約 section) — the grep found terms from all sections ✓ (lines 250-420 of ~500 line file). Let me check the file's total line count and whether the license terms section is complete (規約 items 1-5 + 免責). Also, the material-inventory claims "二次利用フリー（商用/非商用、无需事先许可）" ✓ line 287 states 商用・非商用の区別なく、事前の承諾を得ることなく無償で複製 ✓.

One more possible issue: the snapshot's "attribution mandatory: 「ブラックジャックによろしく 佐藤秀峰」" — the actual page text at line 265: "「ブラックジャックによろしく　佐藤秀峰」の2点を明記してください" ✓ and the cases.json attribution uses full-width space "ブラックジャックによろしく　佐藤秀峰" ✓ consistent.

Also the obligations: "public-use report e-mail within 1 month — USER to-do" ✓ registered in material-inventory obligations ✓ and report §2.2/§5.6 ✓. Also the JASRAC page positions: material-inventory says "vol2 p35/54/150/151/153, vol7 p192" — the snapshot ALSO lists 11巻/77頁 (Volume 11 / Page 77) which the inventory OMITS! Snapshot line 325: "・11巻／77頁／『ジョーンジェットの犬』（作品コード066-3777-9）作詞／浅井健一" and EN line 384 area also. Let me confirm: line 383-384 EN shows Volume 2 / Pages 35, 54, 150, 153 (note: the EN version omits 151!), Volume 7 / Page 192, and presumably Volume 11 / Page 77 on the next line (line 385) which my grep didn't show because the pattern matched only certain things... Actually my grep pattern included "150|151|153|192|54" but not "77". Line 384 matched "192". There should be a line after 384 with "Volume 11 / Page 77". The grep for line 325 (Japanese) shows 11巻/77頁 ✓ included in the Japanese list. So the snapshot lists THREE volumes with JASRAC-managed music pages: vol2, vol7, and **vol11/p77**.

The material-inventory's terms_verified_in_snapshot says: "JASRAC-managed music pages: vol2 p35/54/150/151/153, vol7 p192 — this selection uses vol03 only (JASRAC-free volume)". It omits the vol11 p77 entry! And the report §2.2 repeats: "JASRAC 管理乐曲页位（2 巻 p35/54/150/151/153、7 巻 p192）" — also omits 11巻 p77.

Is the omission material? The conclusion drawn ("本次选取仅 vol03（JASRAC-free 卷）") is still valid since only vol03 was used and vol11 isn't relevant. But the claim "条款逐条复证" (each clause re-verified) is weakened: the JASRAC page list was transcribed incompletely (missing the vol11/p77 entry). This is a legitimate P3 finding: incomplete transcription of a license clause in material-inventory.json:21 and report §2.2 → the "逐条复证" claim is not fully accurate. Since the selection uses vol03 only, no license risk results; but the record is incomplete and the same list may be reused later (e.g., if a later task pools vol11 p77, the registered list would miss it).

Also note the EN/JP discrepancy: JP says 2巻/35,54,150,151,153 (5 pages) while EN line 383 says "Volume 2 / Pages 35, 54, 150, 153" (4 pages, omitting 151). The inventory lists the JP 5 pages ✓ (correctly using JP). Fine — I could note that the EN version is incomplete but the inventory used JP. Not a finding against the owner.

Let me verify the full JASRAC block by reading lines 320-330 and 380-390 of the snapshot to be precise. Also check the file line count.

Let me also read the sfx-semantic-worksheet.csv to check the 9 vs 8 SFX region count for BJ06.
dsh: reasoning:
Excellent! This resolves the "9 vs 8" question definitively:

`sfx-semantic-worksheet.csv` has 9 rows: 8 BJ06 rows + 1 K11 row. So the Task background's "已有 9 个 SFX region" came from this worksheet's 9 rows (which includes K11's 1). The report calls it a "笔误级偏差" and cites KO-RERUN §3.2; the precise origin is the 9-row SFX worksheet (8 BJ06 + 1 K11) — exactly the same conflation that DSH r1 review flagged in M2-TA3-B2 (doc/reviews/M2-TA3-B2-81e5ad81-dsh-r1.md:62). So the Task text repeated the already-corrected "9 全部在 BJ06" misstatement. The Owner's handling (measured 8, registered) is correct, but the attribution of the deviation ("笔误") is imprecise; better: "任务书背景沿用了 M2-TA3-B2 已更正的 9（8 BJ06 + 1 K11）合计口径". This is a P4 documentation-precision note.

Also verifies the OCR source texts of the first run's 8 sfx regions ✓ (matching my earlier finding).

Also very useful: the worksheet confirms the region_ids of the first run (2e99d206… etc. as seen in the first-run summary lines 250-346 ✓). And the new run's region_ids are different (regenerated) ✓ — so "与首跑逐 region 一致" is bbox-level ✓ (as I noted).

Now, is there any risk that the report's claim "与首跑同 region 数、同类型分布——检测确定性跨 run 复现" is problematic? No — bboxes identical.

Now let me also double check the sfx-detect-diagnosis.json's sfx box for BJ13 (conf 0.8222 at 1561.5,2608.5 - 1775.4,2906.9) vs the production run's BJ13 sfx region bbox. Let me read qual-BJ13.json region bbox (line 331-343). From the grep earlier: line 331-334 region_id b3e3273b..., region_type sfx. Let me read lines 295-345 to get bboxes. Cross-check the production sfx region bbox equals the diagnosis's T-shirt box (approximately). This confirms "BJ13 唯一 sfx region=T 恤印花" — the diagnosis box (from the same detector at conf≥0.25, all classes) at conf 0.8222 should match the production region bbox. Let me verify.

Also — an important consideration: the production run keeps cls=sfx at conf≥0.5. The diagnosed T-shirt box conf 0.8222 ≥ 0.5 ✓ so it would survive → consistent with the 1 sfx region.

Let me read qual-BJ13.json lines 290-345.
dsh: reasoning:
Confirmed: BJ13 production sfx region bbox = (1561,2608,214,299) = exactly the diagnosis's sfx box (1561.5,2608.5 → 1775.4,2906.9) ✓. So "BJ13 唯一 sfx region = T 恤印花误报" is internally consistent, and the preview image confirms the red box sits on the T-shirt chest print (SURF logo) ✓. Great.

Also: BJ13's speech regions: region 1 bbox (2124,258,370,1013) = the top-right SFX oval location!! Wait: the top-right ref SFX is at (2210,240)-(2560,1000). The speech region 1 bbox = (2124,258)-(2494,1271). That's aligned with the top-right SFX oval! And its OCR text is "いやー、" — so the top-right oval, which the annotator claims contains ピ一一ーン！(phone ring), was OCR'd as "いやー、" by manga-ocr and classified as **speech** (not sfx!).

Hold on! That's very interesting. Looking at the preview image again: the top-right vertical oval — does it read ピーーーーーン (phone ring) or いやー? Actually, looking at the image, the top-right vertical text in the oval looks like "ピーーーーーーー" ... hmm. The OCR read "いやー、". The annotator claims ピ一一ーン！(phone ring). Hmm. In the image, the top-right oval's characters: the first char looks like "ピ" (with handakuten) followed by a long vertical line... hard to say. The left oval (region 3, speech, bbox 472,2668,308,1002 → matches the left ref SFX box 420,2560-760,3400) has OCR "Ｗｉｆｉｘ"?? Wait no. Let me map:

- speech region 1: bbox (2124,258,370,1013) → the top-right oval → OCR "いやー、" 
- speech region 2: bbox (374,382,1312,469) → the chapter title 第19話 徳ちゃんと先生 → OCR "第１９話徳ちゃんと先生" ✓
- speech region 3: bbox (472,2668,308,1002) → the left oval → OCR "Ｗｉｆｉｘ" ← ??? 

Hmm! wait. The translate_details order: region ffed29e8 (order 1) → OCR "いやー、"; region 5ed8dfc4 (order 2) → OCR "第１９話徳ちゃんと先生"; region de83b0c4 (order 3) → OCR "Ｗｉｆｉｘ"; region b3e3273b (order 4, sfx) → OCR "．．．".

Mapping by bbox: order 3 bbox (472,2668)-(780,3670) = the LEFT oval (the left blue ref box = 420,2560-760,3400). And its OCR is "Ｗｉｆｉｘ"? That can't be right — the left oval is where the annotator says ピ一一ーン！(the second phone ring). Hmm, but wait: in the preview image, the left-middle vertical text region... Let me look at the image again: the left side has a blue box around a vertical text that appears to read... The image shows on the left, in a large oval, characters that look like "ピーーーーーーン" I thought. But the T-shirt print says "SURF..." Hmm, "Ｗｉｆｉｘ" — where's that? In the image, there's a wall-mounted print/poster with text on the right side (near the desk, at around x 630-680, y 270-340 in preview = source ~1890-2040, 810-1020). Hmm, that's inside the sfx region? No...

Anyway, the mapping by bbox says the left vertical oval (472,2668)-(780,3670) was OCR'd as "Ｗｉｆｉｘ". Hmm, that's likely a mis-OCR? Actually hold on. Looking at the preview image, on the left side there IS a vertical oval with text. I described it as "ピーーーーン". The OCR says "Ｗｉｆｉｘ". Hmm, both? The OCR result "Ｗｉｆｉｘ" is weird for a big brush oval.

Wait, maybe the left oval actually contains a large "Ｗ" like shape... Let me look at the image once more: In the left oval, the visible strokes look like a big "ピ" + "ー" + "ー" + "ー" + "ー" + "ン"? Or could be a stylized "Ｗｉｆｉ"? Hmm. I recall the image: left oval contains vertical text that appeared to have a loop-ish first character and long vertical strokes with a final "ン"-like shape. OCR (manga-ocr, poor on SFX) produced "Ｗｉｆｉｘ". Hmm, that suggests the oval might be a WiFi-signal drawing with "WiFi" text! Actually — the page has a WiFi print on the wall? And the phone-ring SFX?

Hmm hold on. Let's reconsider: In the preview image, at the top right there's an oval with vertical text; the top-right *blue box* (ref) is drawn there. There's also a wall calendar/poster on the right wall with small text. The "Ｗｉｆｉｘ" print — I see in the image, on the right wall near the desk, a framed/printed poster with characters (around x 620-680, y 270-360 preview) which is where a "WiFi" sign might be... but the region mapping says the OCR "Ｗｉｆｉｘ" belongs to bbox (472,2668,308,1002) = left oval. That bbox has no overlap with the wall poster.

Unless the translate_details region order doesn't correspond to reading_order... Let me verify by reading the full ocr_details and translate_details with region_ids. From the grep: line 376-421: "region_id": "ffed29e8..." ocr_text "いやー、"; "5ed8dfc4..." ocr_text "第１９話徳ちゃんと先生"; "de83b0c4..." ocr_text "Ｗｉｆｉｘ"; "b3e3273b..." ocr_text "．．．". And the regions list maps: ffed29e8 → order 1 (top-right oval), 5ed8dfc4 → order 2 (title), de83b0c4 → order 3 (left oval), b3e3273b → order 4 (T-shirt).

So OCR of the top-right oval = "いやー、" and of the left oval = "Ｗｉｆｉｘ". Hmm, both look like garbage for a phone-ring SFX. Interesting. This raises a question about the annotator's目检: are the two large oval texts really ピ一一ーン！(phone ring)? Looking at the preview image, the top-right oval: I can see characters that look like "ピ" then a long stroke... Actually the image at the top-right: I see what appears to be "ピーーーーーーーー" vertically? Hmm, or is it "いやー"? 

Hmm, let me look at the image more carefully. I only got one view. The top-right oval text: first character at top looks like a katakana "ヒ" with a small circle → "ピ"; then several long vertical strokes (ー); then a final "ン". That's ピーーーーン = phone ring ✓ consistent with the annotator. The OCR "いやー、" is garbage then? Hmm, manga-ocr reading a vertical brush SFX as "いやー、" — plausible garbage.

And the left oval text: In the image, the left oval contains something that looks like it starts with a shape... The OCR says "Ｗｉｆｉｘ" which is bizarre. Maybe the left oval actually reads "ピーーーーーーーーン" too but manga-ocr hallucinated "WiFi" from context (the page has a WiFi-related scene?). Hmm, hold on — maybe there's a "WiFi" mark in the middle of the left oval? Some manga draw "WiFi" icon.

Hmm, wait. Maybe I mis-assigned: is the left blue ref box (420,2560,760,3400) actually on the desk area (the WiFi print)? No: preview coords (140,853)-(253,1133) = left side, middle-lower = the left oval ✓.

OK whatever the OCR is, the key observation is: the two目检 SFX locations were detected and classified as **speech** with OCR text, not "sfx". This is direct evidence that:
(1) The claim "sfx 类 0 命中" ✓ true.
(2) The claim "6 个被 panel 类覆盖" undercounts / mischaracterizes: for BJ13, the two SFX locations became **production speech regions** (region_type=speech, sfx_policy=skip) with OCR text — i.e., the classifier assigned **speech**, and these are real product-visible regions: they got TRANSLATED as dialogue! In the production BJ13 run, regions 1 and 3 (the two big phone-ring SFX) were treated as speech and translated: "いやー、"→"哎呀——" and "Ｗｉｆｉｘ"→"Ｗｉｆｉｘ". So under production semantics, huge SFX got translated as dialogue (garbage), and the T-shirt print became the SFX region.

Wow — this is a substantive finding about the domain-gap conclusion. The report §3.2 says the risk is only "漏检即无 region" and "误报面（T 恤印花被判 sfx）". But the actual evidence in this very run shows a **third, worse form of damage**: two目检 SFX instances were mis-classified as *speech* and thus went through the normal dialogue translation path, producing garbage translations ("Ｗｉｆｉｘ" passed through, "いやー、"→"哎呀——") that will be typeset into the manga page (inpainting/render/export). That's not just "no region / no translation" — it's wrong-content regions. The report's §3.2 "对产品语义的影响面" analysis misses this form, even though its own artifacts show it. This is a P1/P2-level finding for the review: the impact analysis is incomplete/inaccurate; the observed mis-classification route is speech (not panel-only), and the product consequence is a mistranslated dialogue region rendered into the page.

Hmm, but hold on. Is my claim about the top-right region being a目检 SFX location accurate? The top-right speech region bbox = (2124,258) 370x1013 → (2124,258)-(2494,1271). The ref SFX box = (2210,240)-(2560,1000). Overlap substantial ✓. And the diagnosis JSON has a text box at (2122.1,282.9)-(2480,1278.2) conf 0.7436 — that's approximately the same box as the production speech region (2124,258)-(2494,1271)! So the production region = the "text"-class box from the diagnosis (label "text" is mapped to region_type=speech in production? Probably text→speech). Yes: ogkalu detector classes are text/bubble/panel → mapped to speech regions. So in production, the top-right SFX was picked up as a "text" box → region_type=speech.

So the diagnosis's own data (text-class boxes) + the production summaries show that the two目检 SFX on BJ13 became **speech regions with OCR text and translations**. The report's §3.2 table for BJ13 says "均 panel 类 conf 0.943（cov 0.83/1.00）" — reporting only the best-covering box (the page-level panel) and hiding the text/speech-class boxes that are the *actual production regions*. That's a significant evidence-selection problem: the report's conclusion "本样本是 panel 类（与 ko 域 text 混淆形态不同）" is contradicted by the production artifacts it ships.

This is my strongest finding (P1 or P2). Let me determine severity. The task's AC3 was "新素材端到端测试…与 BJ06 结果合并为 SFX 端到端能力结论". The delivered capability conclusion says "检测段是真实瓶颈；漏检即无 region；policy=translate 不产生错误 SFX 翻译". The omitted fact — SFX被当 speech 翻译并渲染 — materially changes the risk assessment for the product (SfxPolicy=SKIP default does NOT protect against this; the damage happens on the normal speech path regardless of SFX policy). The report explicitly claims "SfxPolicy=SKIP 默认下该盲区无用户可见影响（sfx 候选缺失仅意味着不触发 SFX 特化翻译）" — that's **factually wrong** per its own evidence: BJ13's phone-ring SFX were translated as dialogue and rendered into the exported page (export OK, translated regions rendered) — under the default SKIP policy this still happens because the regions are typed speech. So the impact statement is wrong. That's P1-worthy? It's a claim error in a verification report's risk analysis, not a code defect. The task's deliverable is evidence; an incorrect impact conclusion in the main report is significant. I'd rate P2 (evidence/analysis defect requiring correction), or P1 if it would mislead the user's ruling on domain expansion. Given "P0-P4" scale, I'll call it P1 for the "SfxPolicy=SKIP 下无用户可见影响" claim being contradicted by the delivered artifacts (it's a false safety claim in an evidence report that the user will lean on for a ruling), and pair it with the diagnosis-metric finding as P2.

Hmm, let me double check the SKIP claim more carefully: report line 126: "对产品语义的影响面：SfxPolicy=SKIP 默认下该盲区无用户可见影响（sfx 候选缺失仅意味着不触发 SFX 特化翻译）；policy=translate 下也不产生错误 SFX 翻译（漏检即无 region）。误报面（T 恤印花被判 sfx）在 policy=translate 下会把印花当 SFX 翻译……"

The "盲区" here is defined as sfx-class recall gap. But the actual detection outcome for the two目检 SFX on BJ13 (and by analogy BJ14/15) is that they are detected as text/speech regions and translated as dialogue. So the "盲区" is not a "no region" recall gap; it's a mis-routing. The report's claim "sfx 候选缺失仅意味着不触发 SFX 特化翻译" is technically true of the sfx class, but the user-visible consequence is that SFX text gets translated by the dialogue path (garbage output for いやー、/Ｗｉｆｉｘ) and typeset into the page — which IS user-visible and independent of SfxPolicy. So yes, the impact analysis is materially incomplete.

But careful: did BJ14/BJ15's目检 SFX also become speech regions? BJ14 has 6 text boxes in the diagnosis and 6 production speech regions; the refs were covered by panel boxes (cov 0.89-1.00), and text coverage low (0.14/0.29/0). Hmm — so for BJ14, the目检 SFX (オギャァ) may NOT have been translated as dialogue (their locations had no text-class box!). Let me check BJ14's speech region bboxes vs the ref boxes to see whether any production speech region covers the SFX. The diagnosis for BJ14 listed 6 text boxes: (505.6,3344.4,867.1,3883.7), (2334.2,3138.8,2605.8,3686), (471.1,2441.2,741.3,2980.1), (1519.6,1735.5,1723.4,2052.2), (2008.8,2528.1,2160,2986.4), (2603.4,1676.1,2676.4,1943.3). Refs: (1230,300,1520,950) — none overlap (best 0? no text box near top-left). (400,1900,700,2560) vs (471.1,2441.2,741.3,2980.1) → partial cov 0.14. (1900,2260,2200,2900) vs (2008.8,2528.1,2160,2986.4) → cov 0.29. So for BJ14, 2 of 3 SFX locations partially overlap text boxes → possibly translated as dialogue. Hmm, the diagnosis's own "best box" verdicts ignore that.

I should verify BJ14's production regions' bboxes to see whether they match the diagnosis's text boxes (i.e., production speech regions on the SFX). qual-BJ14.json regions are at lines 393-453 (6 speech). Let me read them, and compare with the diagnosis text boxes. If the production speech regions coincide with the text boxes near the SFX, then "SFX translated as dialogue" happened on BJ14 too.

Let me read qual-BJ14.json lines 390-460.

Also I realize I should double check my claim about BJ13's top-right oval being a SFX (ピ一一ーン！) vs the annotator's目检 — the annotator's own inventory says two ピ一一ーン！. The top-right oval and the left oval are those two. The T-shirt box is separate. So yes.

Let me read BJ14 regions.
dsh: reasoning:
BJ14 production speech regions:
1. (2553,1650,178,337) = matches diagnosis text box (2603.4,1676.1,2676.4,1943.3)? Hmm, diagnosis text box x 2603-2676 w=73, y 1676-1943 h=267. Production region 1 is (2553,1650)-(2731,1987) w=178 h=337. Close but not identical — production applies different letterbox/scale? Or the production detection uses different NMS/preprocessing? Hmm, the diagnosis used the same code path supposedly. The boxes differ somewhat: e.g. diagnosis bubble (2517.1,1599.9,2772,2042.4) vs production region1 (2553,1650,178,337) = (2553,1650)-(2731,1987). Hmm! Actually production region 1 looks more like the diagnosis's *bubble* box (2517,1600)-(2772,2042) shrunk... or like a text box.

Hmm wait. Production regions come from ogkalu (text/bubble) detector + chiqui7 sfx. The diagnosis only replays the chiqui7 sfx detector (detection_sfx.py)! So the production speech regions come from a *different* model (ogkalu), not from chiqui7. The diagnosis's "text/panel/bubble" boxes are chiqui7's classes. So the mapping "diagnosis text box == production speech region" is NOT valid — they're different models!

Let me recheck BJ13: diagnosis chiqui7 text box (2122.1,282.9)-(2480,1278.2) and production speech region 1 (2124,258)-(2494,1271). These are nearly identical! Hmm, that's suspicious. But wait — maybe the production pipeline *also* uses chiqui7's non-sfx classes for regions? Let me check src/infrastructure/providers/detection_sfx.py to see what the production combination does: does it merge chiqui7 boxes of all classes, or only sfx, with ogkalu? The report says "chiqui7 sfx 类" only adds sfx regions. Hmm, but the near-identical BJ13 box suggests the production region came from... either ogkalu (coincidence?) or chiqui7 text.

Actually for BJ14, production region 2 = (1441,1686,349,503) = (1441,1686)-(1790,2189); diagnosis chiqui7 text box (1519.6,1735.5,1723.4,2052.2) — similar-ish but not identical (production is bigger). Production region 4 = (1933,2498)-(2260,3005) vs diagnosis text (2008.8,2528.1)-(2160,2986.4) — production bigger. So production regions ≈ chiqui7 text boxes expanded. Hmm, that suggests ogkalu boxes are slightly different but cover similar areas (both are "text" detectors, i.e., text-line boxes).

So I can't reliably equate. But the key question remains: in the production run, was any of the目检 SFX covered by a production speech region (thus translated as dialogue)? For BJ13: yes, clearly — production speech regions 1 and 3 exactly cover the two目检 SFX locations (2124,258,370,1013) vs ref (2210,240,2560,1000) and (472,2668,308,1002) vs ref (420,2560,760,3400). Those are the目检 SFX locations, and their OCR texts (いやー、/Ｗｉｆｉｘ) and translations (哎呀——/Ｗｉｆｉｘ) are in the delivered summary ✓. So for BJ13 the finding is solid regardless of which model produced them.

Also for BJ13, the diagnosis JSON's chiqui7 text boxes at those same locations corroborate the confusion (chiqui7 also says text there).

For BJ14: production speech regions 1..6 with OCR texts: あの．．．(1519,1735 area→region2), 癌の末期じゃ (region?), etc. The refs: (1230,300,1520,950) top-left — production region 2 is at (1441,1686)... no. Let me match OCR to bboxes: from the greps, translate_details order 1-6: 那个……/癌症晚期了/5年前做过手术…/这位患者……难道说/我之前住进了市内的大医院/明明不那样做就好了…
ocr_details order: あの．．．/癌の末期じゃ/５年前に手術したんだが再発してね．．．/この患者さん．．．もしかして/市内の大病院に入院してたんだがな/よせばいいのに１ヵ月前に退院してきちまった.

The refs (オギャァ) are at (1230,300,1520,950), (400,1900,700,2560), (1900,2260,2200,2900). Production speech regions: (2553,1650), (1441,1686), (414,2392), (1933,2498), (2271,3106), (460,3286). Does any overlap a ref?
- ref2 (400,1900,700,2560) vs region3 (414,2392)-(808,3003): overlap y 2392-2560 (168), x 414-700 (286) → area 48,048 / ref area (300*660=198,000) = 0.24. Partial. Hmm, so region 3 (OCR あの．．．?? no—order 3 = 5年前に手術…) partially overlaps ref2 (オギャァ at 400,1900-700,2560). Hmm, partial overlap only.
- ref3 (1900,2260,2200,2900) vs region4 (1933,2498)-(2260,3005): overlap 267x402 = 107,334 / 192,000 = 0.56. So region 4 substantially overlaps ref3 (オギャァ #3). Interesting.
- ref1 (1230,300,1520,950) vs region2 (1441,1686,349,503) → no (y far).

So on BJ14 there IS partial overlap between 2 of the 3目检 SFX and production speech regions. But the diagnosis's chiqui7 boxes for those refs were panel-dominant (cov 0.89/1.00 by quarter-page panels), and the text coverage was 0.14/0.29. The production regions (ogkalu-based) may come from the ogkalu detector, which the diagnosis didn't evaluate at all! The diagnosis only replays chiqui7 (detection_sfx). So the diagnosis cannot characterize the *production* region routing, which is dominated by ogkalu. That's an important limitation: the conclusion "检测缺口在 chiqui7 sfx 类" is fine, but the report's table implies "chiqui7 实际判定 = panel 类" for the目检 SFX — i.e., it presents chiqui7's class assignment as the production outcome, while production regions for those locations may come from ogkalu. For BJ13, the production speech region bbox (2124,258,370,1013) is ~chiqui7's text box (2122,283,358,995)... hmm, those are nearly identical (2124,258,370,1013) vs (2122.1,282.9,358,995). Differences of ~1-25 px. That is much closer than a coincidence would suggest. Hmm! Does production use chiqui7 for text too? Let me check detection_sfx.py quickly to understand: maybe the production "chiqui7 SFX" provider merges chiqui7 boxes with ogkalu boxes and the region for the SFX oval came from... Actually maybe the ogkalu detector also detects text there and produces a similar box (both models are trained on similar data). The near-identical values could be coincidence-ish (2% differences).

Hmm, but wait: the diagnosis's text box [2122.1, 282.9, 2480.0, 1278.2] and production region [2124,258,370,1013]→(2124,258)-(2494,1271): the differences are: x0 +1.9, y0 -24.9, x1 +14, y1 -7.2. Pretty close but not exact. Given the same preprocessing, if it were the same box, it'd be exact. So they're different model outputs that happen to agree closely. Fine — for BJ13 the two目检 SFX locations were ALSO detected by ogkalu as text (since production region_type=speech with OCR text) ✓. So the finding stands by the production artifacts themselves: BJ13's two巨大 SFX became speech regions (translated), regardless of model.

So my P1/P2 finding is robust: report §3.2's impact analysis ("SKIP 下无用户可见影响" / "漏检即无 region") is contradicted by the delivered BJ13 run: the two目检 SFX were detected as speech regions, translated via the dialogue path ("いやー、"→"哎呀——", "Ｗｉｆｉｘ"→"Ｗｉｆｉｘ"), and rendered/exported (export OK). Also the diagnosis table attributes them to "panel 类" while the same evidence file shows text-class boxes there, and the production artifacts show speech regions there.

Hmm, careful about "translated as dialogue and rendered": does the export render the translations? Export is the translated page image (BJ13-translated.png) ✓ status OK. So yes, the mistranslations are typeset into the exported page.

Now, I want to double-check whether the two BJ13 speech regions really correspond to the two目检 SFX and not to some other text. Region 1 bbox (2124,258)-(2494,1271) is at the top-right = the top-right oval ✓. Region 3 bbox (472,2668)-(780,3670) = left oval ✓. And OCR texts "いやー、" and "Ｗｉｆｉｘ". Hmm, "Ｗｉｆｉｘ" for the left oval... Let me look at the preview image once more to see what the left oval contains. Actually, looking at the image I received: the left-middle vertical oval — I can see it contains large characters. Given the OCR "Ｗｉｆｉｘ" and the annotator's claim ピ一一ーン！... Hmm, there's a real possibility the annotator mis-identified the left oval: maybe it's actually a "WiFi" mark? But the annotator labeled it ピ一一ーン！(phone ring). Hmm.

Let me look at the image again in more detail by requesting a zoom? I can't crop without shell. But maybe I can read the other preview images (BJ14/BJ15) and also there might be a zoom crop of p0048? The thumbs-vol03/inspect has only p0159-sfx-zoom.jpg. Hmm.

Actually — let me re-read the BJ13 preview image carefully. From the rendered image I saw:
- Top-right: a vertical oval containing characters. I described "+ーーーー" ... The visible glyphs at top-right: I recall seeing "ピ" like shape with a long series of vertical strokes and a "ン"? Or was it "いやー、"? The manga-ocr reading "いやー、" suggests the oval might contain hiragana いやー which would be *dialogue*, not SFX! Hmm. But the annotator (who zoomed at 100dpi) says ピ一一ーン！(phone ring). 

Hmm, this matters: if the oval actually contains "ピーーーーン" (phone ring), OCR "いやー、" is garbage → the annotator is right and the region is a目检 SFX mistranslated. If the oval contains "いやー" (someone saying "no..."), the annotator's目检 is wrong. Looking at the picture: the top-right oval — the first char looks like it has a handakuten circle (ピ) rather than い. And the long vertical strokes = ー. So ピーーーーーーン. I'm fairly confident: in the image, the top-right oval's content has a small circle at the top-right of the first glyph (characteristic of ピ or プ/ペ/ポ) — consistent with ピ一一ーン！.

Hmm, and for the left oval: characters appeared to be... I recall a shape like "ピ" too plus ー and a final "ン" at the bottom? The OCR "Ｗｉｆｉｘ" is weird. Hmm, "Ｗｉｆｉｘ" — maybe the left oval contains a large "Ｗ" + "ｉ" + "ｆ" + "ｉ" + "ｘ"?? That would be a stylized "WiFi" (phone ringing via WiFi?) Hmm. Or manga-ocr confusing ピーーーーン with Ｗｉｆｉｘ? Unlikely but manga-ocr does hallucinate.

Ah wait — maybe the left "oval" is actually a WiFi icon/speech? Let me look at the image once more. Actually, from the image: on the left side, the blue box surrounds a vertical oval with characters that look like "ピーーーーーーーーーーーーーーーーー" spanning the full height... 

I could ask read_image again on the BJ13 preview and look hard. But images are described to me in one pass; I can request the preview again — the tool returns the same image. Maybe I can request a specific region? No cropping available. Hmm, maybe I can read the OCR crop of that region! The BJ06/13 crops exist in the external tree: pixels-new-assets/ocr/crops/BJ13/*.png — those are the exact region crops for the 4 BJ13 regions. Reading the crop for region de83b0c4 (the left oval) and ffed29e8 (top-right) would let me see the source glyphs clearly at native crop resolution! Let me read those two crop images. That's a decisive check on whether the目检 inventory (ピ一一ーン！) is correct and whether the reviewer's interpretation is right.

Let me do that: read_image on
- G:/CODEX/New Manga.task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/pixels-new-assets/ocr/crops/BJ13/ffed29e8e881400586249e72f10a29f8.png (top-right oval)
- .../de83b0c423294d8cadf7944dc6dff2b3.png (left oval)
- .../b3e3273b76c443359dca2d67bb856e85.png (T-shirt print)

These are the actual production region crops. Great idea.

Let me do those three reads.
dsh: reasoning:
Now I can see the crops clearly. Both crops contain large handwritten vertical katakana that reads: "ピ" + "ー" (long) + "ー"? Let me interpret: The top crop shows a large "ヒ" with a handakuten (ピ) at top? Actually the rendering shows: a big curved shape "ヒ" with... hmm, the image shows what looks like "に"/"は"? Let me read the glyph: it looks like a large "は" with a circle → "ぱ"? Hmm.

The first crop (370x1013) shows: at top a large glyph that looks like "ヒ" with a small circle at its upper right → "ピ"; then a long horizontal-ish stroke... Actually the shapes: I see a big "ㄣ"-like curve, then two short strokes with a tiny circle (like "゛" or "ぱ"?), then a long vertical stroke with a dot at the end (like "！"?). Hmm.

Second crop similar: "ヒ"-like with circle, then "゛" strokes, then a long vertical bar and a dot.

Honestly, these look like ハチン? No... The OCR for crop1 (top-right oval) was "いやー、" and for crop2 (left oval) "Ｗｉｆｉｘ". Looking at the crops, I'd read them as "ピーーーーーン！" attempts? Hmm, the crops appear to show what could be a stylized "パ" + "ー" + "ン" + "！"?

Honestly, manga-ocr's readings ("いやー、", "Ｗｉｆｉｘ") are garbage on these hand-drawn SFX. And the annotator's目检 reading "ピ一一ーン！" (phone ring) is plausible for a large oval-enclosed vertical手写 katakana with a final "ン"+"！". Actually looking at the crop: the bottom has a dot and a slanted stroke — like "！" (exclamation) or "ン". And the middle has "ー" strokes. The top has "ピ" (ヒ with handakuten circle ✓ I can see the small circle next to the second stroke of ヒ). So "ピーーーン！" is a reasonable reading ✓. Both crops are the same text (phone ring SFX), matching the annotator's inventory ピ一一ーン！×2 ✓.

So: the annotator's目检 (SFX = ピ一一ーン！×2) is corroborated for both locations ✓, and manga-ocr read them as "いやー、" and "Ｗｉｆｉｘ" (garbage) ✓ which production treated as speech and translated ("哎呀——" and "Ｗｉｆｉｘ") — i.e., the mis-routed SFX produced garbage translations on the dialogue path and got rendered into the exported page.

Hmm, this also reveals a related point: the annotator's目检 inventory calls the style "huge handwritten vertical, balloon-edged" — the ovals are actually ellipse-shaped outlines around the SFX (typical phone-ring representation) ✓.

So my P1 finding is now very well substantiated:
- BJ13: 2 of the目检 SFX (ピ一一ーン！×2) were detected as **speech** regions (region_type=speech, bbox exactly at the SFX locations), OCR'd ("いやー、"/"Ｗｉｆｉｘ"), translated via the normal dialogue path ("哎呀——"/"Ｗｉｆｉｘ"), and rendered/exported OK.
- The report's §3.2 impact statement ("SfxPolicy=SKIP 默认下该盲区无用户可见影响…policy=translate 下也不产生错误 SFX 翻译（漏检即无 region）") is contradicted: the damage occurs on the speech path and is independent of SfxPolicy; a garbage translation of a huge SFX gets typeset into the page.
- The diagnosis table attributes the two instances to "panel 类" (best coverage) while its own JSON lists text-class boxes there, and the production evidence shows speech regions; the "与 ko 域 text 混淆形态不同（本样本是 panel 类）" claim is unsupported.
- Severity: I'd say P1 for the incorrect impact/safety claim (affects the user's ruling on whether the gap is harmless), and P2 for the diagnosis-metric/attribution problem. Actually, both stem from the same root; I'll present as two findings: R1 (P1): impact analysis contradicted by delivered artifacts (SKIP-path damage), R2 (P2): diagnosis verdict methodology (single-sided coverage + best-box only, hides co-located text boxes; "no box at all" branch effectively unreachable; panel attribution is an artifact of page-level panel boxes; the DETECT-EVAL R12 note explicitly disqualified this metric), R3 (P3): "6 vs 7" count inconsistency, R4 (P3): JASRAC clause transcription incomplete (11巻/77頁 missing), R5 (P3): timestamp label skew in material-inventory (local time labeled Z), R6 (P3): "本 worktree 以外零写入" contradicted by pixel root inside task-envs/M2-TA3-B + report §6 pixel path wrong, R7 (P2/P3): Task doc reference regression dialogue-readability → dialogue-readiness (non-existent artifact), R8 (P4): "9 vs 8" deviation registration attribution imprecise (origin = sfx-semantic-worksheet 9 rows = 8 BJ06 + 1 K11), R9 (P4): "逐 region 一致" wording (region_ids regenerate; bbox/type identical), R10 (P4): register_new_cases.py's redundant ocr status expression + sfx status derived from policy field rather than outcome; R11 (P4): report §6 tool list says "工具 ×3 ... /register_new_cases.py/diagnose_sfx_detect.py（×4）" — inconsistent ×3/×4 phrasing; minor. Also report §3.1 "speech 16 region 翻译方向正确" while BJ13's speech set includes a WiFi print and the "いやー、" garbage — worth folding into R1.

Let me double-check R11: report line 164: "| 工具 ×3 | `experiments/M2-SFX-E2E-MATERIAL/render_vol_pages.py` / `run_new_asset_e2e.py` / `register_new_cases.py` / `diagnose_sfx_detect.py`（×4） |" — the label says ×3 but lists 4 files and says (×4). Trivial P4 cosmetic.

Also: does the handoff mention "工具 ×4" ✓ (task file line 46 says 工具 ×4 ✓). Fine.

Another check for E (scope discipline): "manifests 只增不改" ✓; "cases.json 无既有条目改动" ✓; "像素零入库" ✓; 18 files all within 允许修改面 ✓;禁改面 zero diff ✓ (no src/tests/contracts/packaging/apps/STATUS files in the diff ✓). Also "首跑/KO-RERUN 产物零触碰" — the diff doesn't touch verification/M2-TA3-B/** or M2-TA3-B3/** ✓. Let me be sure: the file list has nothing under verification/M2-TA3-B ✓.

One more scope item: the report §1.1 says the run used "harness=KO-RERUN 判轨控件就绪版，零改动复用" — the harness run_qualification.py is in experiments/M2-TA3-B/ and is unmodified in the diff ✓ (consistent with "零改动复用"). BUT: the harness writes settings via `core.pipeline_defaults.save_settings_section("sfx", {"policy": sfx_policy})` (line 490-492) — this mutates a persisted settings store somewhere (maybe in the user profile or a temp dir), not in the repo. That's presumably why the KO-RERUN had "生产 settings 键生效". Potentially it leaves a changed global setting (sfx policy=translate) behind after the run! The K11 run in KO-RERUN already did this; does the harness restore the settings afterwards? If not, a subsequent run without --sfx-policy would inherit translate (production default SKIP assumption broken). Let me check run_qualification.py around line 480-520 to see whether it restores. Hmm, this is the pre-existing harness (not in this diff), and the KO-RERUN task already used it with the same behavior; the current report says "首跑全 skip" for BJ06 — the first run was done with... hmm, the first run (M2-TA3-B phase2) had sfx skip = production default. If the harness's setting persisted after the K11 translate run (done later in KO-RERUN), then a subsequent run would default to translate. Not our task's concern, but let me look quickly — if the settings mutation persists, then it's a cross-task environment side effect worth noting as an integration/NOT_VERIFIED item (the current run set policy=translate globally; did the task leave the store dirty?).

Let me read run_qualification.py lines 480-530.

Also, one more: the "sfx_policy_reassemble" stage suggests the harness re-assembles the pipeline with the policy. Let me read that section to see whether the setting is scoped to the run (e.g., saved then restored, or stored in a temp profile via env var like NEWMANGA_DATA_DIR). Let me look.
dsh: reasoning:
The sfx.policy is persisted into the case's own db (`db_path` under case_root / "managed"?) — need to know whether db_path is per-case in the scratch/managed area (git-external temp) or the shared production data dir. Line 495: `assemble_core_services(db_path, case_root / "managed", ...)`. Let me check where db_path/case_root come from — if per-case under the scratch root (`C:\Users\...\Temp\m2-ta3b2-BJ06-...` per the summary's scratch_root), then no global state pollution. The BJ06 summary has "scratch_root": "C:\\Users\\49745\\AppData\\Local\\Temp\\m2-ta3b2-BJ06-c5zd4pgr" ✓ so it's a per-run temp scratch → the settings write is scoped to that scratch db ✓ no production-state side effect. But for run_new_asset_e2e.py, which calls run_case directly... it gets its own scratch per case presumably. Let me verify quickly that case_root is under scratch (grep for scratch_root/case_root in run_qualification.py). If per-case scratch, no cross-task contamination ✓. Good to check because "policy 强制" writing into a shared db would be an environment side effect (relevant to "本 worktree 以外零写入" and to the "首跑零改动" claim — the writes are in temp scratch, fine).

Let me grep.
dsh: reasoning:
Confirmed: per-run `tempfile.mkdtemp` scratch, so the settings write and DB are scratch-scoped ✓ — no production-state or cross-task contamination from the sfx policy. Good: the "首跑产物零改动" and "本 worktree 以外零写入(除像素)" substance holds except for the pixel-root placement under M2-TA3-B.

Hmm, so for R6: the pixels write into `task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/pixels-new-assets` — that IS a write into another task's env tree. Is that a violation? The task's允许修改面 is about repo paths; the pixel discipline says git-external tree. The AC1 pixels went to task-envs/M2-SFX-E2E-MATERIAL/pixels (own task env). AC3's went under M2-TA3-B's env tree due to the script's default deriving from PIXEL_ROOT_DEFAULT.parent. So it's an inconsistency + contradicts the "本 worktree 以外零写入" phrasing (which is literally false anyway since pixels are outside the worktree). I'll frame it as: the claim should be "no writes to other Task worktrees/artifacts"; the AC3 pixel root lands inside another Task's env tree (M2-TA3-B), and report §6's pixel path inventory (`task-envs/M2-SFX-E2E-MATERIAL/pixels*/`) doesn't cover it → evidence-path traceability P3.

Now let me also confirm the "scripts ×4 in experiments/M2-SFX-E2E-MATERIAL" all exist in the worktree (diff shows 4 new .py files ✓).

Let me also confirm there are no other files in experiments/M2-SFX-E2E-MATERIAL (e.g., leftover) — glob.

Also for completeness in section E: "diff --check EXIT=0" (whitespace errors) — can't run; but I can eyeball: the diff has no trailing whitespace complaints visible. NOT_VERIFIED.

Also "porcelain clean" — NOT_VERIFIED (no shell).

One more verification useful for AC1: the report claims the BJ06 run used an independent out-dir/pixel-root with zero modification of the first-run artifacts. Evidence: summary paths point to verification/M2-SFX-E2E-MATERIAL/bj06-run/summaries and pixels in task-envs/M2-SFX-E2E-MATERIAL/pixels ✓ (not M2-TA3-B/phase2). First-run artifact exists untouched in main repo (not in this worktree's diff) ✓. Good.

Hmm, one more potential issue: pixel root for BJ06 = `task-envs/M2-SFX-E2E-MATERIAL/pixels` — but the report §1.1 says "独立 pixel-root（`task-envs/M2-SFX-E2E-MATERIAL/pixels`，与并行 KO-FULLRUN 零文件交集）" ✓ consistent, and default PIXEL_ROOT_DEFAULT would be task-envs/M2-TA3-B/phase2-pixels; the author overrode it to their own task env ✓. So AC1 correctly used own env, AC3 didn't (used the default). Consistent with my finding.

Now let me check the KO-FULLRUN parallelism claim: the report says the BJ06 run was parallel with KO-FULLRUN with zero file intersection. KO-FULLRUN task = M2-TA3-B3-KO-FULLRUN. Does it exist? Earlier glob of verification/M2-TA3-B3* found nothing. Let me check whether the parallel task's artifacts exist in the repo (main worktree). The task file says depends_on includes M2-TA3-B3-KO-FULLRUN. If that worktree/task doesn't exist yet (no artifacts), then the "与并行 KO-FULLRUN 零文件交集" claim is about a task that may not exist → minor. Let me check for M2-TA3-B3 in the repo and worktrees.

Let me grep doc/tasks for M2-TA3-B3 and glob for its verification dir.
dsh: reasoning:
M2-TA3-B3-KO-FULLRUN.md exists as a task (claimed/released) but no verification artifacts yet → the "并行无文件交集" claim is plausible/a priori (different case, different out-dir) but not verifiable statically beyond path independence ✓. Fine — it's a low-value item; I'll fold into NOT_VERIFIED lightly or omit. I'll mention in the 逐项 table under E that path independence is verified (BJ06 uses its own out-dir/pixel-root and ko artifacts aren't in this diff).

Also, 4 tool scripts ✓ exist.

Now let me also double check one AC1 evidence item I haven't: "run1+run2 completed" ✓ (summary stages + run2 status completed, 17/17 per-region completed ✓). And "export OK sha256 c1d503f4…" ✓ matches report §1.1 (c1d503f49a341ade…) ✓ and qual-report ✓.

Wall 695.8s = 357.62+336.92 = 694.54 + overhead ≈ 695.83 ✓ consistent.

Now let me assess the report's §1.3 quality table once more for any overstatement: "≤6 字符符合率 8/8" ✓ (max 3 chars). "无音节直译实例" — ハチン→啪 ✓, いいじゃ→好啊 (not transliteration イイジャ→伊伊佳) ✓. OK.

The report's "文化对等结论不外推" ✓ honest.

One more AC4 item: "key 零明文（env 注入 + scrub_secrets）" — the report says "产物已抽查无泄漏形态" ✓ I verified no key strings in the diff. Note the run.log contains the HF unauthenticated warning (no token) ✓.

Cost: 68 requests, 40,735 tokens ✓. But note the task's AC4 budget says "合计 est token 预算 10 万内" ✓ 40.7% ✓. Also the task mentions "≈34 region×2 请求≈70 请求" — actual 34 requests for BJ06 (17 regions × 2) and 68 total. So the request count is consistent with the intended model ✓.

Now, is the report's claim "34 请求（=17 region×2 的 KO-RERUN 请求数模型）" ✓ verified in the summary: requests 34, n_target_region_calls 34 ✓.

Now, the "预算 10 万" self-consistency: 40.7% ✓.

Let me also double check the BJ06 gate claim "sfx region sfx_policy 字段实测 translate ×8（首跑全 skip）" — verified ✓ both runs.

I think I have enough. Let me also peek at whether the report's §3.2 "6 个被 panel 类..." claim vs the diagnosis verdicts (7 panel) — I'll cite: report §0 table line 15 ("6 个被 panel 类 0.92-0.97 高置信覆盖") vs report §3.2 table lines 119-123 (all 7 rows panel 类) vs sfx-detect-diagnosis.json (7/7 verdicts say cls=panel). Also the task file line 49 and handoff repeat "6 个". So the count propagates. Good finding (R3, P3).

Let me now also confirm the exact line numbers for citations. I need file:line for findings:

1. R1 (P1) — Impact analysis contradicted:
   - report line 126: "对产品语义的影响面：SfxPolicy=SKIP 默认下该盲区无用户可见影响（sfx 候选缺失仅意味着不触发 SFX 特化翻译）；policy=translate 下也不产生错误 SFX 翻译（漏检即无 region）。"
   - Contradicting evidence: qual-BJ13.json regions (lines 294-341): region ffed29e8 region_type=speech bbox (2124,258,370,1013) = 目检 SFX #1; region de83b0c4 speech bbox (472,2668,308,1002) = 目检 SFX #2; ocr_details lines 376-421 (いやー、/Ｗｉｆｉｘ); translate_details lines 426-450 (哎呀——/Ｗｉｆｉｘ); export OK line 463-467.
   - Also report line 15 (§0) claims "BJ13 唯一 sfx region 为 T 恤印花误报" — true, but omits that both目检 SFX became speech regions.
   - Crop evidence: pixels-new-assets/ocr/crops/BJ13/{ffed29e8…,de83b0c4…}.png show the two ピ一一ーン！ SFX as the speech-region crops ✓ (I verified visually).

2. R2 (P2) — Diagnosis verdict methodology:
   - diagnose_sfx_detect.py:196-203 (coverage single-sided) and 255-275 (best-box only; "no box at all" unreachable when a page-level panel exists).
   - sfx-detect-diagnosis.py? no: sfx-detect-diagnosis.json BJ13 box list (lines 16-66) shows the text boxes at the two SFX locations (lines 28-46, 57-66) and a page-level panel box (lines 18-26) — but the report table (line 121) only cites panel.
   - report line 125 "形态学与 DETECT-EVAL 的 ko 域观察不同：ko webtoon SFX 混淆去向是 text 类；本样本是 panel 类".
   - M2-SFX-DETECT-EVAL sfx-detect-eval-report.md:145 (Known limitations 6: "coverage 单侧口径（R12）… `chiqui7_any_class` 列被 panel 类页面级大框支配、不用于结论") — the new diagnosis reuses exactly that disqualified metric.
   - Also the diagnosis circle: the chiqui7 text boxes are at the two SFX locations (BJ13) with conf 0.74/0.84 → text-confusion form is present, contradicting "本样本是 panel 类".

3. R3 (P3) — 6 vs 7 count: report line 15 & line 117 ("6 个被 panel 类 0.92-0.97 高置信覆盖") vs report lines 119-123 table (7 rows) vs sfx-detect-diagnosis.json verdicts (7 of 7 "cls=panel": lines 85, 97, 307, 319, 331, 591, 603). Also repeated in task line 49 and handoff line 27.

4. R4 (P3) — JASRAC clause transcription incomplete: material-inventory.json:21 lists vol2+vol7 but omits 11巻/77頁 (snapshot lines 325, 384-ish); report line 83 same. Impact low (vol03 only) but "条款逐条复证" overstated.

5. R5 (P3) — timestamp label skew: material-inventory.json:4 (generated_at_utc 08:20:00Z) and :15 (snapshot_captured_at 08:07Z) vs run logs' local 08:07-08:35 / summaries' UTC 00:07-00:35 (qual-BJ06.json:1148 started 00:07:01Z; new-assets-run.log:8 local 08:18:58). Local = UTC+8 → labels wrong; the "许可先行" ordering can't be audited from the doc (I verified via mtime ordering instead: the snapshot file is the oldest entry in the task-env tree).

Hmm, careful — I should present the mtime inference as an inference (glob returns mtime order). Let me phrase: "按文件 mtime 顺序（glob 升序）快照早于 thumbs/render，实物先行成立；但文档时间戳写成 Z 造成 8 小时偏差，审计者从文档本身无法复现'先行'。"

6. R6 (P3) — pixel root & "零写入" claim:
   - run_new_asset_e2e.py:761-763 default pixel root = PIXEL_ROOT_DEFAULT.parent/"M2-SFX-E2E-MATERIAL"/"pixels-new-assets" = task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/pixels-new-assets (PIXEL_ROOT_DEFAULT=.../M2-TA3-B/phase2-pixels, run_qualification.py:96-98);
   - evidence: qual-BJ13.json:495-497 pixel_path / crops_dir (I saw lines 3490/3502 in diff = summary fields). Let me get exact line numbers in qual-BJ13.json for pixel_path: from the diff, line 3490 corresponds to the diff line, not the file line. Let me grep the file for pixel_path to get exact lines. I'll cite report §6 line 166 as the wrong inventory, and handoff/task line 48 claim "本 worktree 以外零写入". Let me get the exact line numbers in qual-BJ13.json.

7. R7 (P2) — Task doc reference regression: doc/tasks/M2-SFX-E2E-MATERIAL.md:21 now says `dialogue-readiness-worksheet` (nonexistent); the real artifact is `dialogue-readability-worksheet` (verification/M2-TA3-B/phase2/translate/dialogue-readability-worksheet.csv/.json). Diff line 74. This is an unauthorized-quality edit that introduced a wrong reference. P2 severity (wrong doc fact in a Task file; low functional impact). I'd say P3... The instruction says severity P0-P4. A wrong reference in a frozen task doc is a real defect but trivial impact → P3. Hmm, but it's the only actual factual error introduced by the diff into a shared doc. I'll assign P2? Let me define my scale in the report: P0 blocker, P1 must-fix before integration (evidence/claim integrity), P2 should-fix (misleading evidence/claims), P3 minor (doc/traceability), P4 nit. I'll put R7 at P3 since it's a doc-only reference error, and R1 at P1, R2 at P2.

8. R8 (P4) — "9 vs 8" origin: the 9 comes from sfx-semantic-worksheet.csv (9 rows = 8 BJ06 + 1 K11; line 2-9) and quality-report.md:120; the report attributes it to a "笔误" and cites KO-RERUN §3.2. Registration is fine; attribution imprecise (and this exact conflation was already flagged in doc/reviews/M2-TA3-B2-81e5ad81-dsh-r1.md:62). P4.

9. R9 (P4) — "逐 region 一致" wording: region_ids differ (first run sfx ids 2e99d206…/… vs new run 3ca24465…); bbox/type/order identical. report line 13/31. P4.

10. R10 (P4/P3) — register_new_cases.py:410-419 pipeline_status derivation: `"ocr": "PASS" if (run2_ok and n_translated > 0) or run2_ok else "FAIL"` reduces to run2_ok (dead condition); `"sfx": PASS` keyed on the policy field rather than the outcome (a sfx region that failed translation would still be PASS) — and BJ13's sfx PASS is thus a *policy-present* status, not an outcome status; also `"inpainting"`/`"typesetting"` PASS derived from run2 completion alone. These statuses are then written into cases.json as if they were measured per-stage results. P3 (evidence precision). Note the report §3.1 explains BJ13 sfx=PASS as "存在走通 translate gate 的 sfx region" ✓ honest-ish.

11. R11 (P4) — report line 164 "工具 ×3 …（×4）" mismatch.

12. Maybe R12 (P4) — report §1.2's phrase and the "17/17 region 零 defect" carrier: verified via attribution=[] (qual-BJ06.json:1593) — I'll list it as verified rather than a finding. Also report §1.1 "17/17 region 零 defect" is not a field; recommend citing attribution=[].

Let me get exact line numbers for a few citations: qual-BJ13.json pixel_path/crops_dir; report line numbers already known (from my reads: report lines 15, 117, 119-123, 125, 126, 164, 166, 83; task line 21/25/26/46-51; material-inventory lines 4, 15, 21, 52).

Let me grep qual-BJ13.json for pixel_path/crops_dir line numbers, and also the export section lines.
dsh: reasoning:
Confirmed R7: diff line 73 → 74 changes `dialogue-readability-worksheet` (correct) to `dialogue-readiness-worksheet` (nonexistent). P3.

Also BJ13's speech region translations: "いやー、"→"哎呀——" (line 429-431) and "Ｗｉｆｉｘ"→"Ｗｉｆｉｘ" (447-449) ✓ confirms R1 (the SFX got dialogue-path translations and were rendered).

Now I have plenty. Let me also spot-check the report's §1.5 cost for BJ06: 34 requests = 17 regions × 2 ✓.

One more: is there any issue with the AC3 "speech 16 region 翻译方向正确" claim? BJ13's speech regions include the two mis-detected SFX (いやー、/Ｗｉｆｉｘ) — so "speech 16 region 翻译方向正确" is wrong for those two (the source isn't speech; the translations are garbage). Report line 112 says "新素材上 speech 链完全正常（16 region 翻译方向正确，含标题/对白/癌症病情陈述等长句）". The BJ13 speech set includes 2 mis-routed SFX → the "16 region 方向正确" claim overstates. This is part of R1; I'll fold it in, or make it a separate P2. I'll fold into R1 as a second instance.

Let me now also double check that region counts cited in the report §3.1 table are right: BJ13 4 (3+1) ✓; BJ14 6 (6+0) ✓; BJ15 7 (7+0) ✓.

And "speech 16 region" = 3+6+7 = 16 ✓ (but 2 of the 3 BJ13 "speech" are actually SFX).

Now let me think about whether R1 might be unfair. Could those two BJ13 regions be legitimately speech? Region1 OCR "いやー、" — could the oval contain "いやー、"? I looked at the crop; it looked like ピ/ー/ン strokes. Hmm, my visual reading isn't definitive, but the annotator's 100dpi zoom inspection says ピ一一ーン！ and the region bbox exactly matches the目检 SFX location with the ellipse outline typical of a telephone ring drawn in an oval. Also the same text is at the other location (crop 2, same glyphs). Two identical large oval-enclosed texts on a lead page, one at top-right and one at mid-left — a phone-ring SFX repeated twice is highly plausible (the scene: old man in a clinic, a phone... the desk has a phone). Also manga-ocr's "Ｗｉｆｉｘ" for the second instance is clearly a hallucination (a "WiFi" print would not be drawn as a giant vertical oval). So R1 is well-grounded. And even if the glyphs were dialogue, then the annotator's目检 inventory (the very basis of the AC2 pooling and the diagnosis reference boxes) would be wrong — which itself is a finding (the diagnosis uses hand-estimated ref boxes as ground truth; if the annotator's reading is wrong, the "panel confusion" verdicts rest on wrong refs). Either way, there's an inconsistency worth surfacing: the目检 inventory, the diagnosis reference boxes, and the production routing disagree, and the report doesn't address the conflict. I'll phrase R1 to cover both directions: "either the目检 inventory is right → SFX got dialogue-path translation and rendering (impact analysis wrong); or the production routing is right → the AC2/诊断 reference boxes are wrong → the diagnosis verdicts are built on misidentified refs. Either branch invalidates part of the report and requires resolution with the source image at zoom." That's a robust and fair way to put it. But my crop inspection tilts to branch 1; state that.

Good. Now, additional consideration for the verdict: is the task's core deliverable acceptable despite R1/R2? AC1 (BJ06) is solid ✓ — the strongest part. AC2 material pooling is solid with license ✓ (minor transcription issue R4). AC3 chain PASS ✓ with an honest gap registration, but the *interpretation* of the gap has a material defect (R1) and the diagnosis tooling has an evidence-caliber defect (R2). Range discipline is clean ✓ (R5-R7 minor). So verdict: PASS with required corrections (conditional / "需修订后集成") — I'd say verdict = "有条件通过（P1/P2 修订后再集成）" since the corrections are to the report's claims (not to code), and the underlying facts remain valid. The integration gate should require the report §3.2 impact analysis + the 6/7 count + the panel/text attribution to be corrected and re-registered (or downgraded to directional with the contradiction disclosed).

Important: the report is a git artifact in verification/**; fixing it requires a new commit → so integration (merge) should be blocked until fixed, or the integrator can accept with a documented correction note. I'll recommend: 集成前由 Owner 提交修订 commit（报告 §0/§3.2 影响面与计数、diagnosis 结论口径、material-inventory JASRAC/时间戳、task doc 引用回退）。That's a fair closure list.

Now the NOT_VERIFIED items (integration runtime):
1. sha256 recomputation of all pins (license snapshot 2bb1dc9f…, PDF 31c37c85…, page sha256 ×3, export sha256 ×4) — internal 5-way consistency verified, digest recomputation needs shell.
2. `git status --porcelain` clean; `git diff --check` EXIT=0; `git check-ignore` result for the 3 new PNGs.
3. The 3 new page PNGs' existence/size/DPI in the worktree (material-inventory claims 2946×4167, 7.5/6.5/8.8MB) — the pixels exist in the worktree (glob? I haven't checked the worktree's test_assets.../vol03/pages dir. Let me check quickly: glob the worktree pages dir to confirm vol03_p0048/0060/0159 exist). Also gitignored status.
4. Live license snapshot fetch & page-content equality to the pinned snapshot (I verified terms inside the file, not fetch equality).
5. Cost metering is an estimate (not endpoint usage) — cannot be independently confirmed beyond the proxy records; also "remote 轨 similarity Gate" was NOT run for BJ06 (no rerun pairs: run.log "rerun_pairs=0"), so the determinism-track evidence here is declaration/binding only, not a similarity measurement. Hmm! That's worth checking: the run used --determinism-track remote but no rerun-check, so "判轨：declared=remote=inferred（DeepSeek binding），fail-closed 校验通过" is just the declaration validation ✓ as stated. The report doesn't claim a similarity gate for BJ06 — it says "跨 run 逐位一致性不适用" (Known limitation 4) ✓. But note the handoff says "run1+run2" — those are page-selection and region-chain, NOT a determinism rerun ✓ the report is clear. Fine.

Actually hmm, one thing: the report §1.1 says "判轨：declared=remote=inferred（DeepSeek binding），fail-closed 校验通过" — this is verified from qual-BJ06.json determinism_track ✓.

6. whether the `sfx_policy` settings write leaves the scratch DB only (verified by code reading: mkdtemp) but the actual temp dirs' residual state = not verifiable.
7. User-side: densho810 report e-mail obligation (user to-do) — not a technical item but should be in the integration closure list.

Let me quickly verify the 3 new page files exist in the worktree pages dir (and the existing BJ pages for context), which also supports "像素入 gitignored 套件目录".

Then I'll write the review.

Also worth verifying: the pages dir contains BJ06's page vol03_p0056.png? That's from the TA2B worktree (source_path points to M2-TA2B-OPEN-ASSETS-zcode). Not needed.

Let me glob the worktree pages dir.
dsh: reasoning:
The 3 new page PNGs exist in the worktree's gitignored suite dir ✓ with matching source_sha256 (52 hex chars! "3af0054184bacabf73baa140382ab087e8d668babc04cd74ac57d5a36c45a040" — let me count: 3af0054184bacabf (16) 73baa140382ab087 (32) e8d668babc04cd74 (48) ac57d5a36c45a040 (64) ✓ 64 hex = valid sha256 ✓). Good, and there's a "source_sha256_recomputed" field ✓ meaning the harness re-hashed the file after the run ✓ — that's an in-run recomputation, so the page sha256 pins are recomputed within the run (source_sha256_recomputed == source_sha256 ✓ verified for BJ15; presumably the same for others). This is stronger than "declared": the harness verifies sha256_match ✓ (run.log "[BJ15] source: OK {'sha256_match': True}") ✓.

But note the pixel file is simply *present* — I can't confirm it's untracked/ignored without git. The .gitignore rule + no PNG in the diff ≈ strong. Mark "tracked status" as NOT_VERIFIED (integration: git check-ignore).

Now let me write the review. Format required:

## Verdict
## 逐项核对表（A BJ06 端到端 / B 素材许可 / C 入池纪律 / D 检测缺口判读 / E 范围纪律）
## Findings（R1…，P0-P4，文件:行）
## NOT_VERIFIED（集成方运行时项）
## 集成方闭合清单
## 推荐下一步（一句）

Language: Chinese. Include file:line citations. Be precise and evidence-based.

Let me assemble the verified facts carefully.

A. BJ06 端到端 — verified items:
- A1: 17 regions = 8 sfx + 9 speech; sfx_policy: first run skip (all 8), current run translate (all 8). Evidence: qual-BJ06.json:921-1125 (regions), M2-TA3-B/phase2/summaries/qual-BJ06.json:142-346 (first run), quality-report/sfx-semantic-worksheet.
- A2: 8/8 sfx translate_details non-empty, final_source=machine (qual-BJ06.json:1511-1582); first run sfx translated_text "" + final_source "none" (first run :734-802).
- A3: 8 OCR texts match worksheet/first run and report §1.2 ✓.
- A4: report §1.3 table (report:45-54) matches the 8 pairs exactly; ≤6 chars holds (1-3 chars).
- A5: speech 8/9 identical + 1/9 changed (ちょっとおじいさん！？) — verified against the first-run artifact (等一下，老爷爷！？ vs 喂，老爷爷！？) ✓ exactly as claimed; the "合法重译" judgment is a single-annotator directional call (echoes KO-RERUN §4's legal-retranslation form ✓ cite ko-rerun-report.md:132).
- A6: pipeline_completed=true; run1 357.62s + run2 336.92s; 17/17 per-region completed; export OK c1d503f4…; wall 695.83 ✓ (report:29 matches).
- A7: "零 defect" = attribution [] ✓ (qual-BJ06.json:1593; harness defect标记 run_qualification.py:601-613,687,798).
- A8: detection determinism: bbox/type/order identical across runs; region_ids regenerated → report's "逐 region 一致" precise only at bbox level (R9).
- A9: 34 requests / 20,246 est token ✓ (qual-BJ06.json:1601-1608).
- A10 NOT verified: the "SEM-1 prompt 特化" step itself has no per-region artifact (no prompt/profile id in translate_details) — the mechanism exists in src (protocol.py:36,53; handlers.py:401; step.py:52; mock_local.py:40,111) but SFX-specific prompt use is inferred from the harness path, not recorded. → I'll put this in NOT_VERIFIED or as a P4 finding. I'll list as NOT_VERIFIED (mechanism-level) with a note.
- A11: the 9-vs-8 deviation: measured 8 ✓; origin of "9" = sfx-semantic-worksheet.csv:2-10 (9 rows, 8 BJ06 + 1 K11) + quality-report.md:120 — the report's "笔误" attribution is imprecise (R8).

B. 素材许可:
- B1: snapshot file exists (32,843 bytes claimed; I can't verify size/bytes but the report says 32,843 and the inventory 32843 — consistent), contains 二次利用フリー (line 95-96), attribution 「ブラックジャックによろしく　佐藤秀峰」+EN (265), 1ヶ月 report info@densho810.com (275/333/413), Kindle 禁止 (317/375), 1円以上有償 (318/417), JASRAC 页位 (324-325) ✓ all present.
- B2: JASRAC list incomplete in the registration: snapshot also lists 11巻/77頁 (325) — missing in material-inventory:21 and report:83 (R4).
- B3: vol03 JASRAC-free claim ✓ consistent with snapshot (only vol2/7/11 listed).
- B4: attribution format matches snapshot exactly ✓ and is used verbatim in cases.json:941 etc. ✓.
- B5: framework consistency with TA2B (material-inventory framework_precedent references doc/tasks/M2-TA2B.md) — I verified the reference and report obligation registration; the TA2B draft file path claimed (verification/M2-TA2B/densho810-report-draft.txt) — I haven't verified it exists! Let me check quickly. If it doesn't exist, the "TA2B 草稿覆盖" claim fails. Let me glob for it.
- B6: unverifiable: sha256 of the snapshot (NOT_VERIFIED), live-page equality (NOT_VERIFIED).

C. 入池纪律:
- C1: 18 files ✓ enumerated; all within 允许修改面 (task:30-32) ✓.
- C2: cases.json 100 case_ids (97+3); new entries at the tail; +214/-0 ✓; schema identical to BJ06 (page_file:"pages/vol03_pXXXX.png" ✓ material-inventory uses the longer form — cosmetic).
- C3: sha256 consistency across 5 artifacts: cases.json:945/1016/1088, material-inventory:60/74/88, render-final-manifest:13/21/29, run_new_asset_e2e.py:721/733/745, summaries' source_sha256 + source_sha256_recomputed + sha256_match=True ✓ all identical.
- C4: 9 candidates目检 evidence files exist (thumbs-vol03/inspect/page_p00{48,53,60,96,101,158,159,160,161}.{png,jpg}) ✓ + 7 contact sheets covering 221 pages ✓ + p0159 zoom ✓.
- C5: pixels gitignored by 日漫_JA/.gitignore:26 ✓; the 3 PNGs exist in the worktree ✓; no PNG in the diff ✓.
- C6: register_new_cases.py append-only with fail-closed clash check (435-438) ✓; the pipeline_status derivation issues (R10).

D. 检测缺口判读:
- D1: 7 verdicts all "cls=panel" in the diagnosis JSON ✓ (85,97,307,319,331,591,603); report table matches the numbers ✓ (0.9431/0.9668/0.9687/0.9721/0.9552/0.9188, cov 0.83/1.00/0.89/1.00/1.00/1.00/1.00 ✓ matches table 121-123).
- D2: T-shirt false positive ✓ verified by preview (red box on the T-shirt chest print) + production region bbox (1561,2608,214,299) == diagnosis sfx box (1561.5,2608.5–1775.4,2906.9) ✓ + OCR '．．．' → '……' ✓.
- D3: "sfx 类 0 命中" ✓ (BJ14 0, BJ15 0; BJ13 1 box=T-shirt; report:117-123 ✓).
- D4: But: (i) the two目检 SFX on BJ13 are production **speech** regions with OCR+translations (R1); (ii) the diagnosis's own JSON has text-class boxes at those two locations with conf 0.74/0.84 (R2), so "本样本是 panel 类，与 ko text 混淆不同" is unsupported; (iii) the metric is the single-sided coverage that DETECT-EVAL §5.6/R12 explicitly disqualified ("panel 类页面级大框支配…不用于结论") and the BJ13 best box IS the page-level panel box (375,370)-(2612,3802) (R2); (iv) the "6" count (R3).
- D5: 衔接 DETECT-EVAL §4.4: verified the report cites the right clause (7 pre-integration conditions incl. class-confusion handling item 5, threshold freeze item 7) ✓ and correctly states domain expansion is out of scope ✓; but its own finding adds a routing damage form not covered by §4.4's checklist framing (which assumes the sfx class does/n't fire) → recommend feeding to §4.4/USER ruling (R1 recommendation).

E. 范围纪律:
- E1: no src/tests/doc/contracts/packaging/apps/STATUS in the diff ✓; 18 files ✓; +5618/-2 ✓ (5569+49).
- E2: first-run/KO-RERUN artifacts untouched ✓ (diff touches nothing under verification/M2-TA3-B/**).
- E3: manifests append-only ✓.
- E4: key leak scan: no key material in the diff ✓ (paths only); scrub_secrets exists in the harness (run_qualification.py:109) and records are scrubbed at dump (131) ✓.
- E5: cost 68/40,735/40.7% ✓ arithmetic.
- E6: "本 worktree 以外零写入" inaccurate (R6); "porcelain clean/diff --check" NOT_VERIFIED.
- E7: BJ06 out-dir/pixel-root independent from KO-FULLRUN ✓ (pixel root task-envs/M2-SFX-E2E-MATERIAL/pixels, out-dir verification/M2-SFX-E2E-MATERIAL/bj06-run/summaries) — the parallel task has no artifacts in the repo yet (only the task file), so "零文件交集" is verified only at path level.

Let me check the TA2B draft file existence quickly (B5) — one glob.

Then write. Also I should double check whether `verification/M2-TA2B/densho810-report-draft.txt` exists (the report §2.2 and material-inventory:23 both claim it).
dsh: reasoning:
TA2B draft exists ✓ (verification/M2-TA2B/densho810-report-draft.txt) so the "TA2B 草稿覆盖" claim is grounded ✓ (though whether the draft actually covers the new pages is a user-side judgment).

Interesting: task-envs/M2-SFX-E2E-MATERIAL has render-final-manifest.json and thumbs render-manifest, plus license-evidence HTML and detect-diag-previews + pixels ✓.

Note: the material-inventory:51 label "render_manifest_git_external": ".../render-final-manifest.json" ✓.

I have everything I need. Let me now write the review.

Let me define severity scale explicitly in the verdict/Findings header:
- P0 阻断；P1 集成前必须修正（结论/证据完整性）；P2 应修正（证据口径/误导性表述）；P3 轻微（文档/可追溯性）；P4 提示。

Findings list (final):
R1 P1 — BJ13 两个目检 SFX 被生产链路当 speech 翻译并渲染；报告 §3.2 影响面结论被自家产物反证。
  证据: report:126; qual-BJ13.json:294-341 (bbox 定位), :385/:409 (OCR), :429-431/:447-449 (译文), :463-469 (export OK); 裁片 pixels-new-assets/ocr/crops/BJ13/ffed29e8….png、de83b0c4….png（本人目检=两个椭圆内竖排大字，与 material-inventory:64-66 的 ピ一一ーン！×2 位置一致）; report:15/112 的 "speech 16 region 翻译方向正确"。
  要求: 二择一裁定（目检对→影响面重写；生产路由对→AC2/诊断参照框错），并把 "SfxPolicy=SKIP 下无用户可见影响" 撤回或限定。

R2 P2 — 诊断判读口径：单侧 coverage + 只取最优框，隐藏同位置 text 类框；panel 归因实为整页 panel 大框平凡覆盖；"no box at all" 分支实际不可达。
  证据: diagnose_sfx_detect.py:196-203, 255-275; sfx-detect-diagnosis.json:18-26（BJ13 整页 panel 框）+ :28-46/:57-66（同位置 text 框 conf 0.84/0.74）; report:125; 反证引用 M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md:145（R12：单侧 coverage / panel 页面级大框支配 / 不用于结论）。
  要求: 改 IoU/双向覆盖或直接报告所有与参照框相交的框（类+conf+cov），据此重写 "panel 类混淆、与 ko text 形态不同" 的表述。

R3 P3 — "6 个被 panel 类覆盖" 与自身表格/诊断 JSON 的 7/7 矛盾（三个文件重复）。
  证据: report:15, report:117-123, sfx-detect-diagnosis.json:85/97/307/319/331/591/603, doc/tasks/M2-SFX-E2E-MATERIAL.md:49, handoff:27.

R4 P3 — 许可条款 JASRAC 页位转录不全（漏 11巻/77頁），"逐条复证" 表述过强。
  证据: material-inventory.json:21; report:83; 快照 densho810-free-snapshot-2026-10-02.html:324-325（含 11巻/77頁）; 结论（仅用 vol03）不受影响。

R5 P3 — 时间戳 Z 标签错位（本地时间 UTC+8 当 UTC），导致 "许可先行" 顺序无法从文档复核。
  证据: material-inventory.json:4 (08:20:00Z), :15 (08:07Z) vs qual-BJ06.json:1148 (00:07:01Z) / new-assets-run.log:8 (本地 08:18:58) / thumbs render-manifest:3 (00:08:09Z); 按 mtime 升序快照文件最早，"先行" 实物成立。

R6 P3 — "本 worktree 以外零写入" 不准确 + 报告 §6 像素路径清单漏 AC3 根目录。
  证据: run_new_asset_e2e.py:761-763 默认派生自 run_qualification.py:96-98 → task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/pixels-new-assets（qual-BJ13.json:466,478 实测路径）; report:166; doc/tasks/M2-SFX-E2E-MATERIAL.md:48。

R7 P3 — Task 文档回填把存在的产物名改成不存在的名字（唯一实质正文改动）。
  证据: review-input.diff:73-74; doc/tasks/M2-SFX-E2E-MATERIAL.md:21（现为 dialogue-readiness-worksheet，全仓库不存在）; 实际产物 verification/M2-TA3-B/phase2/translate/dialogue-readability-worksheet.csv/.json。

R8 P4 — "9→8 笔误级偏差" 的归因不精确（来源是 sfx-semantic-worksheet 9 行=8 BJ06+1 K11 的合计口径，且该合并口径在 M2-TA3-B2 review 已被指出）。
  证据: verification/M2-TA3-B/phase2/translate/sfx-semantic-worksheet.csv:2-10; verification/M2-TA3-B/quality-report.md:120; doc/reviews/M2-TA3-B2-81e5ad81-dsh-r1.md:62; report:35。

R9 P4 — "与首跑逐 region 一致" 仅在 bbox/类型/序号层成立（region_id 全部重生成）。
  证据: qual-BJ06.json:923/935… vs 首跑 M2-TA3-B/phase2/summaries/qual-BJ06.json:144/156…; report:13,31。

R10 P3 — cases.json pipeline_status 的推导语义弱于字段外观：ocr 条件冗余（等价 run2_ok）、sfx 只看 policy 字段不看译文结果、inpainting/typesetting 直接由 run2 完成推出。
  证据: register_new_cases.py:410-425; cases.json:927-938（BJ13 sfx=PASS）; report:113（解释为 "存在走通 translate gate 的 sfx region"，与脚本口径不完全一致）。

R11 P4 — 报告 §6 工具行 "×3" 与列出/标注的 4 个脚本不一致。
  证据: report:164。

Verified-no-finding items (to show in tables): the rest.

Hmm, one more possible finding: the report §0 (§3.1) says BJ13 "4（3+1 sfx）" and "sfx『．．．』→『……』" ✓ verified. Fine.

Also: is the "T 恤印花" characterization in the report supported? ✓ by preview. Good — I'll mark verified.

One more thought about R1's severity: P1 means integration-blocking. Is it fair to block integration on a report-claim issue? The Task deliverable *is* the report/results; AC3's conclusion feeds the user's ruling on DETECT domain expansion. The wrong claim ("SKIP 下无用户可见影响") could lead the user to under-prioritize. I'd say P1 for the claim, with the recommendation that the merge can proceed after the report amendment (or the integrator accepts with a recorded correction). I'll phrase the verdict as "有条件通过：AC1/AC2 证据成立可集成；AC3 的结论面须先按 R1/R2 修订（或由集成方在合并说明中记录更正）".

Also should I flag that the diagnosis's "production_threshold": 0.5 matches production? ✓ (detection_sfx uses conf 0.5). I verified report says production keeps cls=sfx conf>=0.5 ✓ consistent with the diagnosis note. I didn't verify the src constant... Actually let me not claim; I'll mark as "与 DETECT-EVAL 的记录一致" or just note it as consistent with the report's claim. Hmm, I did read detection_sfx.py indirectly. I could quickly check the 0.5 threshold in src to be thorough — it's relevant to "高置信 0.92-0.97" framing and to whether the T-shirt box (0.8222) is "高置信". Not essential. Skip.

Also the diagnosis note says production keeps only cls=sfx at conf>=0.5 with NMS iou 0.7 ✓ matches the code I saw (NMS_IOU=0.7 constant in the diagnosis, imported _nms). Fine.

Now let me write out the final answer. It must be complete and in Chinese, with the required sections. Keep it organized and reasonably concise but thorough. I'll include a note at the top that the sandbox had no shell so all runtime items are NOT_VERIFIED.

For the 逐项核对表, I'll produce 5 sub-tables (A-E) with 项/结论/证据 file:line. Keep rows tight.

Let me write it.
# M2-SFX-E2E-MATERIAL 静态 Review（round 1，非作者 DSH）

- 对象：branch `agent/zcode/M2-SFX-E2E-MATERIAL`、implement `40a8ceec`、tip `04966987`（docs）；diff = `G:/CODEX/New Manga.task-envs/M2-SFX-E2E-MATERIAL/review-input.diff`（18 files，+5618/−2）
- 审查方式：**纯静态**。本会话沙箱无法起 shell（`SetNamedSecurityInfoW failed (Win32 5: grantWrite)`），因此一切需要执行命令的项（sha256 复算、`git status`/`git diff --check`/`git check-ignore`、现状抓取）一律置 `NOT_VERIFIED`，交集成方；我改用文件层可读证据（worktree 产物、Git 外 task-envs 快照/裁片/预览图、首跑对照产物）做交叉核对，包含对 3 张诊断预览与 BJ13 区域裁片的**目视复核**。
- 严重度定义：P0 阻断；P1 集成前必须修正（结论/证据完整性）；P2 应修正（证据口径或误导性表述）；P3 轻微（文档/可追溯性）；P4 提示。

## Verdict

**有条件通过（CONDITIONAL PASS / deltas-required）**。AC1（BJ06 端到端）与 AC2（素材许可+入池）的核心事实经独立复算成立，范围纪律干净，是本 Task 最扎实的部分：17 region（8 sfx + 9 speech）与首跑 bbox 逐条一致、`sfx_policy` 首跑全 `skip` → 本跑全 `translate`、8/8 sfx 译文非空且 `final_source=machine`、speech 8/9 逐位一致 + 1/9 合法重译（与首跑逐字核对完全相符）、成本 68 请求 / 40,735 est token = 40.7% 自洽、cases.json 100 条只增（+214/−0）、像素零入库。

但 AC3 的**结论面有一处被自家产物反证的实质性错误**（R1，P1），且检测诊断的**判读口径**使用了 DETECT-EVAL 自身已明文废止的单侧 coverage 度量、并只披露最优覆盖框（R2，P2），另有计数矛盾（R3）、许可条款转录不全（R4）、时间戳标签错位（R5）、"零写入"表述不实（R6）、Task 文档回填引入不存在引用（R7）。这些都集中在"解释与登记"层，不推翻 BJ06 实测与素材许可事实；修订（新 commit）后即可集成。

## 逐项核对表

### A. BJ06 端到端（AC1）

| 项 | 结论 | 证据 |
|---|---|---|
| 17 region = 8 sfx + 9 speech | ✅ 成立 | `bj06-run/summaries/qual-BJ06.json:921-1125`（9 speech + 8 sfx，reading_order 1-17） |
| gate 机制证据（skip→translate） | ✅ 成立，且强于 K11（KO-RERUN §3.2 当时只是"放行推断"） | 本跑 sfx `sfx_policy=translate`（`qual-BJ06.json:1034/1046/…/1118`）×8；首跑 `sfx_policy=skip`（`M2-TA3-B/phase2/summaries/qual-BJ06.json:255/267/…/339`）×8；`run.log:4` `sfx_policy_reassemble OK {'policy':'translate'}` |
| 译文落库 8/8 非空 | ✅ 成立 | `qual-BJ06.json:1511-1582`（好啊/嗯嗯/！！！/……/啪/……/哇……/3.，均 `final_translation` 非空、`final_source=machine`）；首跑同 8 条为 `""`+`final_source=none`（首跑 `:734-802`）。`final_source=machine` = 机器产出非人工，用词与首跑 `none` 对照自洽 |
| 报告 §1.3 表与 JSON 逐条一致 | ✅ 8/8 逐条一致（仅行序不同）；≤6 字符 8/8 成立（1–3 字）；`ハチン→啪` 非音译 | `sfx-e2e-report.md:45-54` vs `qual-BJ06.json:1511-1582` |
| 任务书 9 个 SFX vs 实测 8 | ✅ 以实测 8 为准，登记正确；**归因不精确**（见 R8） | `sfx-semantic-worksheet.csv:2-10`（9 行 = 8 BJ06 + 1 K11）；`M2-TA3-B/quality-report.md:120` |
| speech 对照 8/9 逐位 + 1/9 合法重译 | ✅ 逐字复算成立（`ちょっとおじいさん！？`「等一下，老爷爷！？」→「喂，老爷爷！？」，其余 8 条完全相同）；"合法重译"与 KO-RERUN §4 的同型形态呼应成立 | 本跑 `qual-BJ06.json:1432-1509` vs 首跑 `:653-730`；`ko-rerun-report.md:132` |
| pipeline_completed / run1+run2 / 零 defect / export | ✅ 成立；"零 defect" 的可机读载体是 `attribution: []`（harness 用 `defect:` 前缀登记） | `qual-BJ06.json:1584-1592`（export OK `c1d503f4…`）、`:1611-1612`（wall 695.83、completed）、`:1593` `attribution: []`；`run_qualification.py:601-613,687,798` |
| 与首跑"逐 region 一致" | ⚠️ 仅 bbox/类型/序号层成立（region_id 全部重生成）（R9） | 本跑 `:923,935…` vs 首跑 `:144,156…`；sfx 8 条 bbox 逐条相同（2145/3084/161/309 等） |
| 成本 34 请求 / 20,246 est token | ✅ 成立（18,604+1,642） | `qual-BJ06.json:1601-1608` |

### B. 素材许可（AC2）

| 项 | 结论 | 证据 |
|---|---|---|
| 一手快照在案 | ✅ 文件存在且非空壳（498 行）；条款关键词逐条命中 | `task-envs/M2-SFX-E2E-MATERIAL/license-evidence/densho810-free-snapshot-2026-10-02.html`（95-96 二次利用フリー/商用非商用免事先许可、265 署名「ブラックジャックによろしく　佐藤秀峰」+EN、275/333/413 公开后 1 ヶ月内 info@densho810.com 报告、317/375 Kindle 禁止、318/417 电子书店 ≥1 円有偿） |
| 署名义务与 cases 登记格式一致 | ✅ 逐字一致，全角空格保留 | 快照 `:265` vs `cases.json:941/1012/1084` 与 `material-inventory.json:67/81/95` |
| vol03 选用（JASRAC-free） | ✅ 结论成立，但**页位转录不全**（漏 11 巻/77 頁）（R4） | 快照 `:324-325`；`material-inventory.json:21`；`sfx-e2e-report.md:83` |
| 报告义务=用户待办 + TA2B 先例 | ✅ 成立（草稿文件确实存在） | `material-inventory.json:23,100`；`verification/M2-TA2B/densho810-report-draft.txt` |
| 快照 sha256 `2bb1dc9f…` / 32,843 bytes | ⚠️ 文档内部自洽（报告与 inventory 同值），**未复算** | `material-inventory.json:13-14`；`sfx-e2e-report.md:82` → NOT_VERIFIED |
| 快照与站点现状一致 | ⚠️ 只核了快照内部条款，未做二次抓取比对 | NOT_VERIFIED |

### C. 入池纪律

| 项 | 结论 | 证据 |
|---|---|---|
| cases.json 97→100 只增 | ✅ 100 条 `case_id`；新增 BJ13/14/15 位于数组末尾；diff 仅 1 个 hunk `@@ -6150,6 +6150,220 @@`，+214/−0，无既有条目改动 | `cases.json:6155/6226/6297`；`review-input.diff:871-1095` |
| 新 case 结构与既有 case 同构 | ✅ 字段集、`page_file:"pages/vol03_pXXXX.png"`、`local_path`、`attribution/attribution_note` 与 BJ06 完全同构（`material-inventory.json` 用更长路径形式，仅文档层差异） | `cases.json:880-950` vs `:4804-4875` |
| sha256 五处一致 | ✅ cases.json / material-inventory / render-final-manifest / `run_new_asset_e2e.py` NEW_ASSET_CASES / run 产物 `source_sha256(+recomputed)` 全同（86eeb6c2…/61dfeb2f…/3af00541…）；run 内还做了 `sha256_match:True` 复算 | `cases.json:945/1016/1088`；`material-inventory.json:60/74/88`；`render-final-manifest.json:13/21/29`；`run_new_asset_e2e.py:721/733/745`；`qual-BJ15.json:16,735` |
| 目检链路实物存在 | ✅ 221 页缩略图（p0001–p0221）+ 7 张 contact sheet（0035/0070/0105/0140/0175/0210/0221 分段）+ 9 候选 100dpi 复查件（p0048/53/60/96/101/158/159/160/161 的 png+jpg）+ p0159 zoom | `task-envs/M2-SFX-E2E-MATERIAL/thumbs-vol03/**`（含 `inspect/`） |
| 像素零入库 + gitignore 规则 | ✅ 规则在位（`/01_black_jack_official/`），diff 无任何 PNG，3 个新页 PNG 只存在于 worktree 套件目录 | `test_assets/comic_golden_suite/日漫_JA/.gitignore:26`；worktree `日漫_JA/01_black_jack_official/vol03/pages/vol03_p00{48,60,159}.png` |
| append-only 程序化 + fail-closed | ✅ case_id 冲突即 `return 2`，不改 suite 级 header，保持 CRLF/2 空格/尾换行 | `register_new_cases.py:429-503` |
| pipeline_status 诚实性 | ⚠️ 表面如实（BJ14/15 sfx=NOT_RUN），但推导语义弱于字段外观（见 R10） | `register_new_cases.py:410-425`；`cases.json:927-938` |

### D. 检测域缺口判读

| 项 | 结论 | 证据 |
|---|---|---|
| 7 目检实例 sfx 类 0 命中 | ✅ 成立（BJ14/BJ15 全带 0.25 亦无 sfx；BJ13 仅 1 个 sfx 框） | `sfx-detect-diagnosis.json:290-295(0)/574-579(0)/68-73(1)` |
| "T 恤印花误报"定性 | ✅ **本人目视复核确认**：预览红框正落在人物 T 恤胸口印花（SURF 字样）上，且诊断 sfx 框 (1561.5,2608.5)-(1775.4,2906.9) 与生产 BJ13 唯一 sfx region bbox (1561,2608,214,299) 完全对应，OCR『．．．』→译文『……』 | `detect-diag-previews/BJ13-detect-diag.jpg`；`sfx-detect-diagnosis.json:47-56`；`qual-BJ13.json:331-341,421,456-458` |
| panel 类 0.92-0.97 覆盖的读数 | ✅ 数字与表一致（0.9431/0.9668/0.9687/0.9721/0.9552/0.9188；cov 0.83/1.00/0.89/1.00/1.00/1.00/1.00） | `sfx-detect-diagnosis.json:85/97/307/319/331/591/603`；`sfx-e2e-report.md:119-123` |
| "panel 类混淆、与 ko 域 text 形态不同" | ❌ **不成立**（R2）：BJ13 两个参照框在诊断 JSON 里同时有同位置 **text 类框**（conf 0.84 [493.9,2682.8,761.3,3640.2]、conf 0.74 [2122.1,282.9,2480,1278.2]，对参照框 cov 0.67/0.73），且 "panel 最优" 来自整页 panel 大框 (375.1,370.3)-(2612.3,3802.0) 的平凡覆盖 | `sfx-detect-diagnosis.json:18-26,28-46,57-66`；`sfx-e2e-report.md:125`；反证= DETECT-EVAL `sfx-detect-eval-report.md:145`（R12 明文：单侧 coverage 大框平凡覆盖、panel 页面级大框支配、"不用于结论"） |
| 生产路由的实际情况 | ❌ 报告"漏检即无 region / SKIP 下无用户可见影响"被自家产物反证（R1） | `qual-BJ13.json:294-317`（两个目检 SFX 位置=**speech** region）+ `:385,409`（OCR いやー、/Ｗｉｆｉｘ）+ `:429-431,447-449`（对话链译文 哎呀——/Ｗｉｆｉｘ）+ `:463-469`（export OK）；裁片 `task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/pixels-new-assets/ocr/crops/BJ13/ffed29e8….png`、`de83b0c4….png`（目视：两处椭圆内竖排大字，与 `material-inventory.json:64-66` 的 ピ一一ーン！×2 位置一致） |
| "6 个"计数 | ❌ 与自身表格/JSON 的 7/7 矛盾（R3） | `sfx-e2e-report.md:15,117` vs `:119-123`；`sfx-detect-diagnosis.json` 7 条 verdict 全 `cls=panel` |
| 与 DETECT-EVAL §4.4 衔接 | ✅ 指向正确（域扩展/类内混淆/阈值冻结属既有 7 项集成前条件，本 Task 零生产改动），结论"检测段是真实瓶颈"方向成立；但应按 R1 补一种 §4.4 未覆盖的损害形态（误路由到 speech 后的对话链翻译与渲染） | `sfx-detect-eval-report.md:128-136`；`sfx-e2e-report.md:127,132` |

### E. 范围纪律 / 成本

| 项 | 结论 | 证据 |
|---|---|---|
| 18 files 全在允许面 | ✅ 全部落于 `verification/M2-SFX-E2E-MATERIAL/**`、`experiments/M2-SFX-E2E-MATERIAL/**`(×4)、`test_assets/comic_golden_suite/manifests/cases.json`、Task/Handoff | `review-input.diff` 文件头清单（18 个）；`doc/tasks/M2-SFX-E2E-MATERIAL.md:30-32` |
| 禁改面零 diff | ✅ diff 中无 `src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`，也无 `verification/M2-TA3-B/**`（首跑/KO-RERUN 产物） | 同上 |
| manifests 只增不改 | ✅ 唯一 hunk 为尾部追加，+214/−0 | `review-input.diff:875-1095` |
| +5618/−2 自洽 | ✅ 5569（implement，17 files）+49（handoff）=5618；−2 = Task frontmatter 状态行 + 正文引用行 | Handoff 交付清单；`review-input.diff:64-65,73-74` |
| key 零明文 | ✅ diff 内无 `sk-*`/Bearer/密钥值，只有路径与 env 名；harness 侧 `scrub_secrets` 在 dump 前统一应用 | `review-input.diff` 全量检索；`run_qualification.py:109,131` |
| 成本 68 请求 / 40,735 / 40.7% | ✅ 算术成立（20246+4756+7309+8424；34+8+12+14），各 case 与 summary 逐项一致 | `sfx-e2e-report.md:137-143`；`qual-BJ0x.json` metering 段 |
| "本 worktree 以外零写入" | ❌ 不准确（R6） | `run_new_asset_e2e.py:761-763` 默认派生；`qual-BJ13.json:466,478` 实测路径 |
| porcelain clean / diff --check / check-ignore | ⚠️ 无 shell，未验 | NOT_VERIFIED |

## Findings

**R1（P1）｜AC3 影响面结论被自家产物反证：BJ13 两个目检 SFX 是被当 speech 翻译并渲染的，不是"无 region"**
- 位置：`verification/M2-SFX-E2E-MATERIAL/sfx-e2e-report.md:126`（"SfxPolicy=SKIP 默认下该盲区无用户可见影响……policy=translate 下也不产生错误 SFX 翻译（漏检即无 region）"），并被 `sfx-e2e-report.md:15,112`、`doc/tasks/M2-SFX-E2E-MATERIAL.md:49`、Handoff 第 4 条复述。
- 反证（全部来自交付物本身）：`qual-BJ13.json:294-317` 的 region #1 bbox (2124,258,370,1013) 与 region #3 bbox (472,2668,308,1002) 正是两处目检 ピ一一ーン！（参照框 (2210,240,2560,1000)/(420,2560,760,3400)），其 `region_type=speech`、`sfx_policy=skip`；`:385,:409` OCR 为 `いやー、`/`Ｗｉｆｉｘ`；`:429-431,:447-449` 走正常对话链产出 `哎呀——`/`Ｗｉｆｉｘ`；`:463-469` export OK → 错误译文已进入渲染页。我另用裁片 `task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/pixels-new-assets/ocr/crops/BJ13/ffed29e8….png`、`de83b0c4….png` 目视确认两处就是椭圆内竖排大字（与 `material-inventory.json:64-66` 一致）。
- 影响：用户将据此裁决"检测域扩展是否值得优先"，而该段给出的是"默认 SKIP 下无用户可见影响"的错误安全感——损害发生在 speech 路径上，与 `SfxPolicy` 无关，且会把乱码译文排版进成品页。
- 要求（二择一，须在报告内显式裁定）：①若目检正确（我目视倾向此项）→ 重写影响面：新增"SFX 误路由为 speech → 对话链乱译 → 进渲染"的损害形态，撤回 SKIP 免责句，并把 `sfx-e2e-report.md:112` 的"speech 16 region 翻译方向正确"限定为 14/16；②若生产路由正确 → 则 AC2 目检清单与 `diagnose_sfx_detect.py:146-160` 的参照框本身不可靠，诊断全部 verdict 作废。

**R2（P2）｜诊断判读口径：单侧 coverage + 只取最优框，导致"panel 类混淆"实为整页 panel 大框平凡覆盖，并隐去同位置 text 类框**
- 位置：`experiments/M2-SFX-E2E-MATERIAL/diagnose_sfx_detect.py:196-203`（`coverage = intersection/ref 面积`，单侧）、`:255-275`（只取 `best_cov` 一条并据此分类；`best_cov<=0` 才判"blind spot"，只要存在页面级 panel 框该分支实际不可达）；结论表述见 `sfx-e2e-report.md:125`。
- 反证：`sfx-detect-diagnosis.json:18-26` 的 panel 框几乎覆盖整页 (375.1,370.3)-(2612.3,3802.0)，对两个参照框 cov=0.83/1.00；同一文件 `:28-46,:57-66` 显示两个 SFX 位置另有 **text 类框** conf 0.84/0.74（cov 约 0.67/0.73，我按坐标复算）。DETECT-EVAL 已就同型度量明文设限："coverage=intersection/SFX 面积是**单侧口径**……大框可平凡『覆盖』（`chiqui7_any_class` 列常被 panel 类页面级大框支配 coverage=1.0，**该列不用于任何结论**）"（`verification/M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md:145`，R12）；本次诊断恰好复用了被废止的度量，并把结果升级为形态学结论。
- 要求：诊断输出改为"列出所有与参照框相交的框（类+conf+cov，或补 IoU/双向覆盖）"，据此重写 §3.2 的 "panel 类支配 / 与 ko 域 text 混淆形态不同"，或降级为"存在整页 panel 框 + 同位置 text 框，两者均可解释 sfx 类 0 命中，归属未定"。

**R3（P3）｜"6 个被 panel 类 0.92-0.97 覆盖"与自身表格及诊断 JSON 的 7/7 矛盾，且已复制进 Task 与 Handoff**
- 位置：`sfx-e2e-report.md:15` 与 `:117`（"6 个"）vs `:119-123` 表格（BJ13 2 + BJ14 3 + BJ15 2 = 7 行，全 panel）；`sfx-detect-diagnosis.json:85,97,307,319,331,591,603` 共 7 条 verdict；重复处 `doc/tasks/M2-SFX-E2E-MATERIAL.md:49`、`doc/handoffs/M2-SFX-E2E-MATERIAL-40a8ceec.md:27`。
- 要求：统一为 7（或在报告中说明被排除的那 1 个实例及其理由）。

**R4（P3）｜许可条款"逐条复证"不完整：JASRAC 页位漏 11 巻/77 頁**
- 位置：`material-inventory.json:21`、`sfx-e2e-report.md:83` 只列 vol2 p35/54/150/151/153 与 vol7 p192。
- 快照原文同时含第三条：`densho810-free-snapshot-2026-10-02.html:325`「・11巻／77頁／『ジョーンジェットの犬』（作品コード066-3777-9）」（英文区 `:384` 之后同样列出，且英文区的 Volume 2 少 151 页——登记采用了日文版，正确）。
- 影响：本次仅用 vol03，结论（vol03=JASRAC-free）不受影响；但该列表是后续复用依据，缺项会在未来入池 vol11 时误导。
- 要求：补齐第三条，并把"逐条复证"限定为"已复证项 + 该三条页位清单"。

**R5（P3）｜`material-inventory.json` 时间戳把本地时间当 UTC（Z 后缀），使"许可快照先行"无法从文档复核**
- 位置：`material-inventory.json:4`（`generated_at_utc: 08:20:00Z`）、`:15`（`snapshot_captured_at: 08:07Z`）。
- 对照：真实 UTC = 本地−8h（`run.log:1` 本地 08:07:10 ↔ `qual-BJ06.json:1148` `00:07:01Z`；`new-assets-run.log:8` 本地 08:18:58 ↔ summary `00:18:5xZ`），即 08:20/08:07 是本地时刻；同目录脚本产物用的是真 UTC（`thumbs-vol03/render-manifest.json:3` = 00:08:09Z、`render-final-manifest.json:3` = 00:11:29Z）。
- 补充（对 Owner 有利的事实）：按文件 mtime 升序，`license-evidence/densho810-free-snapshot-2026-10-02.html` 是 task-envs 树中最早的文件，早于 thumbs/render → 实物顺序上"许可先行"成立；但按文档字面读，快照反而晚于全部 run，结论相反。
- 要求：改为 UTC 真值（约 00:07Z/00:20Z）或显式标 `+08:00`。

**R6（P3）｜"本 worktree 以外零写入"不实 + 报告 §6 像素路径清单漏 AC3 根目录**
- 位置：`doc/tasks/M2-SFX-E2E-MATERIAL.md:48`、Handoff 第 4 条（"本 worktree 以外零写入"）；`sfx-e2e-report.md:166`（"`task-envs/M2-SFX-E2E-MATERIAL/pixels*/`"）。
- 事实：AC3 的 pixel-root 由 `run_new_asset_e2e.py:761-763` 从 `PIXEL_ROOT_DEFAULT.parent`（`run_qualification.py:96-98` = `task-envs/M2-TA3-B/phase2-pixels`）派生，实际落到**另一个 Task 的 env 树**：`task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/pixels-new-assets/`（`qual-BJ13.json:466,478`；该目录下 17 张裁片 + 3 张 export 已实物核对）。AC1 则正确地用了自己的 env（`task-envs/M2-SFX-E2E-MATERIAL/pixels`）。
- 影响：实质（像素不入 Git、未改他 Task 产物、run 的 sqlite/settings 写在 `tempfile.mkdtemp` 私有 scratch，见 `run_qualification.py:447-449,490-504`）无风险；但声明与报告清单都需修正，否则后续审计者按报告路径找不到 AC3 像素。
- 要求：把表述改为"零写入其他 Task 的 worktree/既有产物（像素写入 Git 外 task-env 树）"，并在 §6 补 AC3 像素根路径。

**R7（P3）｜Task 文档回填把存在的产物名改成不存在的名字（本 diff 唯一的实质正文替换）**
- 位置：`review-input.diff:73-74`（`dialogue-readability-worksheet` → `dialogue-readiness-worksheet`），落于 `doc/tasks/M2-SFX-E2E-MATERIAL.md:21`。
- 事实：全仓库检索无 `dialogue-readiness-*`；真实产物为 `verification/M2-TA3-B/phase2/translate/dialogue-readability-worksheet.csv/.json`（由 `experiments/M2-TA3-B/build_worksheets.py:220-221` 生成，`verification/M2-TA3-B/quality-report.md:126` 引用）。即改前正确、改后指向不存在的文件。
- 要求：回退该词（可随修订 commit 一起）。

**R8（P4）｜"9→8 笔误级偏差"的归因不精确**
- 位置：`sfx-e2e-report.md:35`（归因为"笔误"并引 KO-RERUN §3.2）。
- 实际来源：`verification/M2-TA3-B/phase2/translate/sfx-semantic-worksheet.csv:2-10` 共 9 行 = **8 BJ06 + 1 K11**，`verification/M2-TA3-B/quality-report.md:120` 写"9 个（8 BJ06 + 1 K11）"；同一合并口径此前已被 non-author review 点出（`doc/reviews/M2-TA3-B2-81e5ad81-dsh-r1.md:62`）。建议登记为"沿用 M2-TA3-B2 已更正的 9 = 8 BJ06 + 1 K11 合计口径"，而不是"笔误"，以免后人重复开单。

**R9（P4）｜"与首跑逐 region 一致"只在 bbox/类型/序号层成立**
- 位置：`sfx-e2e-report.md:13,31`。
- 事实：8 个 sfx 的 bbox 与 reading_order 逐条相同，但 `region_id` 全部重生成（本跑 `3ca24465…` 等 vs 首跑 `2e99d206…` 等）。建议改为"bbox/类型/序号逐条一致"。

**R10（P3）｜`cases.json` 的 `pipeline_status` 推导语义弱于字段外观**
- 位置：`register_new_cases.py:410-425`：`"ocr"` 条件 `(run2_ok and n_translated>0) or run2_ok` 等价于 `run2_ok`（冗余死分支）；`"sfx"` 只看 region 上 `sfx_policy=="translate"` 而**不看该 region 是否有译文**（译文失败的 sfx region 仍会写成 PASS）；`"inpainting"/"typesetting"` 直接由 run2 completed 推出。
- 影响：`cases.json:927-938` 的 BJ13 `sfx=PASS` 实为"策略已放行"而非"该段结果达标"；`sfx-e2e-report.md:113` 的说明（"存在走通 translate gate 的 sfx region"）比脚本口径更诚实，两者应对齐。
- 要求：在报告/脚本注里显式声明 status 的推导规则（policy-presence vs outcome），或按结果重导。

**R11（P4）｜报告 §6 工具行 "×3" 与所列 4 个脚本不一致**
- 位置：`sfx-e2e-report.md:164`（`工具 ×3 | render_vol_pages.py / run_new_asset_e2e.py / register_new_cases.py / diagnose_sfx_detect.py（×4）`）。

## NOT_VERIFIED（集成方运行时项）

1. **全部 sha256 复算**：许可快照 `2bb1dc9f…`（32,843 bytes）、源 PDF `31c37c85…`、3 张新页 PNG、4 个 export、task-env 内渲染/诊断清单文件。静态侧只证明了**五处引用互相一致**（cases.json / material-inventory / render-final-manifest / `run_new_asset_e2e.py` / run 产物 `source_sha256_recomputed`）+ run 内 `sha256_match=True`。
2. **git 面**：`git status --porcelain` 是否干净、`git diff --check` EXIT=0、3 张新 PNG 与 17 张裁片是否真被 `git check-ignore` 命中、分支 tip 是否即 `40a8ceec`（diff/patch-id 与 worktree 逐字对照）。
3. **许可快照的时效性**：未做 `densho810.com/free/` 二次抓取与快照逐字节比对（仅验证了快照内部条款存在）。
4. **许可条款清单完整性以外的页位核对**：vol03 是否确实不在 JASRAC 三条页位清单内（按卷判断成立，未按卷内页逐页核）。
5. **SEM-1 prompt 特化是否真的作用于这 8 个 sfx region**：`translate_details` 无 prompt/profile 标识，机制仅可从只读 src 推断（`src/ports/translation/protocol.py:36,53`、`src/infrastructure/providers/handlers.py:401`、`src/application/translation/context/step.py:52`、`src/infrastructure/providers/mock_local.py:40,111`）；报告 §1.3 只做了输出侧规范对照。若集成 Gate 需要"SEM 段已实证"，须补一条可按 region 检索的 prompt/instruction id。
6. **成本计量性质**：`--meter-translation` 为 experiments 层 proxy（estimate_tokens，`qual-BJ06.json:1601-1608` 自述"非 endpoint 计量"），无法独立复核真实用量；预算比例 40.7% 只在该口径下成立。
7. **BJ14/BJ15 的目检 SFX 是否也走了对话链**：诊断 JSON 中 2 个参照框与 text 类框仅有 0.14/0.29 的部分相交、另有 1 个 0 相交，静态不足以定性；需按 R1 的方法（裁片+region bbox 对位）逐页确认。
8. `doc/tasks/M2-TA3-B3-KO-FULLRUN` 目前只有 Task 文件、无产物，"与并行 KO-FULLRUN 零文件交集"仅在路径层成立。

## 集成方闭合清单

1. **R1（P1）**：裁定分支①/②，修订 `sfx-e2e-report.md`（§0 结论速览、§3.2 影响面、§3.1 "16 region 方向正确"）与 Task/Handoff 复述句；若采分支①，建议补一句给 DETECT-EVAL §4.4 的输入："sfx 类漏检的损害不止'无 region'，还包括误路由为 speech 后经对话链乱译并渲染"。**此项未闭合前不并入 master。**
2. **R2/R3（P2/P3）**：`diagnose_sfx_detect.py` 增列所有相交框（类/conf/cov，建议补 IoU）并重出 `sfx-detect-diagnosis.json`；据此重写 §3.2 的 panel/text 归因；全库统一"7/7"。
3. **R4/R5（P3）**：补齐 JASRAC 三条页位；修正 `material-inventory.json` 的 UTC 时间戳（或标 `+08:00`），并保留"快照实物早于 thumbs/render"的 mtime 依据。
4. **R6/R7/R11（P3/P4）**：修正"零写入"表述与 §6 像素路径（补 `task-envs/M2-TA3-B/M2-SFX-E2E-MATERIAL/pixels-new-assets/`）；回退 `dialogue-readiness-worksheet` → `dialogue-readability-worksheet`；统一 §6 工具计数。
5. **R8/R9/R10（P3/P4）**：登记 9=8 BJ06+1 K11 的准确来源；"逐 region 一致"改"bbox/类型/序号一致"；在报告内写明 `pipeline_status` 的推导规则。
6. **运行时复核**：按 NOT_VERIFIED 1–3 复算哈希、跑 `git status --porcelain` / `git diff --check` / `git check-ignore`；确认禁改面与既有产物零 diff 后再合并。
7. **用户待办移交**：densho810 公开利用后 1 个月内邮件报告（`info@densho810.com`，新增 3 页同源，沿用 `verification/M2-TA2B/densho810-report-draft.txt`）；以及 DETECT 域扩展是否立项的裁决（DETECT-EVAL §4.4 七项）。

## 推荐下一步（一句）

先由 ZCode 就 R1/R2 出一个只改报告与诊断输出的修订 commit（含 R3–R7 的登记修正），再由集成方按 NOT_VERIFIED 清单复算哈希与 git 面后合入 `40a8ceec`+修订。
