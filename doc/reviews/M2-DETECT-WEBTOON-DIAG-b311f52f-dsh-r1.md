dsh: reasoning:
Let me start by exploring the review inputs. I need to read the diff, task doc, handoff, diagnosis.md, probe-results.json.

The working directory is G:\CODEX\New Manga. The worktree is G:/CODEX/New Manga.worktrees/M2-DETECT-WEBTOON-DIAG-zcode, and diff at G:/CODEX/New Manga.task-envs/M2-DETECT-WEBTOON-DIAG/review-input.diff.

Note file policy: workspace-write with session workspace G:\CODEX\New Manga. But reading files outside might be... read is usually allowed. Let me try.

Let me start with reading the task doc and the diff.

Let me first list files.
dsh: reasoning:
The pwsh tool failed with sandbox error. And glob returned no files - maybe the worktree path doesn't exist or is not accessible. Let me try reading the diff directly with read tool.

Actually the sandbox error is about granting write to workspace. The file policy is workspace-write; the workspace is G:\CODEX\New Manga. The command failed. Let me retry with just workspace default? Hmm, the error "SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)" — this is an ACL grant failure. Possibly the sandbox tries to grant write to workspace and fails. Maybe I should try running pwsh without workdir... same. Let's try again—maybe transient. Or use read/glob tools instead which may use a different backend.

glob returned "No files found" — that could mean path with space... Let me test glob on the main workspace.
dsh: reasoning:
Good. The diff is 2408 lines. Let me read the whole diff in chunks, plus the worktree files. But the worktree path: glob found nothing under the worktree path. Let me check whether the worktree exists at all. pwsh failed due to sandbox ACL issue. Let me try read on a worktree file.

Actually maybe the worktree doesn't exist (the task-env review-input.diff exists). The instructions said "沙箱无 shell 时不执行命令" — implying shell may not be available. So I should rely on read/glob/grep tools.

Let me try glob with different path form (backslashes).
dsh: reasoning:
The worktree exists. Let me now read the rest of the diff, and the key files: diagnosis.md, probe-results.json, task doc, handoff.

Also I should read the production source `src/infrastructure/providers/detection_manga.py` to verify the owner's claims about `_detect_text_boxes`, MANGA_TEXT_CLASSES, threshold, etc.

Let me continue reading the diff and in parallel read task doc.
dsh: reasoning:
Now let me read the rest of the diff (probe-results.json content, mostly). It spans lines 783-2408 (1626 lines of JSON). I need to inspect key parts: per-tile data, K02/K04 pages, BJ02, and the deduped boxes sample.

Also read the production source detection_manga.py.

Let me read the diff from 899 onward in chunks and also the production source.
dsh: reasoning:
Now I have the production source verified. Key checks:

1. `_detect_text_boxes` passes `rgb` directly to processor with no size override — confirmed (line 342).
2. `MANGA_TEXT_CLASSES = (1,2)` — confirmed.
3. `MANGA_CONF_THRESHOLD = 0.5` — confirmed.
4. Note: production detect does `cluster_words_into_blocks` after getting text boxes. The probe's `provider_detect` calls `provider.detect` → region_count = number of blocks (clusters), not raw text boxes. So BJ02: 10 raw text boxes ≥0.5 → cluster into 5 blocks. That matches "region_count 5（bubble 丢弃 5）" — wait, diagnosis says "BJ02（对照）2946×4167 6.5× provider region 5（bubble 丢弃 5）raw score_max 0.9721". Hmm, "bubble 丢弃 5" — that would mean 10 detections ≥0.5, of which 5 bubble + 5 text → then clustered into 5 blocks? Actually need to check probe-results BJ02 data. The handoff says "BJ02 对照 10 检出". Let me check the raw JSON for BJ02: provider_detect region_count=5, confidences (5 values 0.937-0.972), and raw_observability official_post_process_ge_0_5 = 10. So 10 raw ≥0.5 → 5 bubble dropped, 5 text → cluster_words_into_blocks merges 5 text boxes into 5 blocks (or fewer). Need to verify counts to check the claim's precision. The diagnosis table says "provider region 5（bubble 丢弃 5）" which is a bit ambiguous but consistent.

Important: The probe's tile_experiment does NOT apply `cluster_words_into_blocks`. It applies greedy NMS to text-class boxes and counts 193 as "检出". Meanwhile the full-page provider path counts *blocks* after clustering. So the comparison "0 → 193" compares provider region_count (blocks, after merge) = 0 against tile-level *text boxes* after NMS = 193. That's an apples-to-oranges granularity claim — actually the diagnosis does discuss 193 vs docTR 15 as granularity, and says ogkalu detects include bubble text blocks and free text (class 1/2). But there's an inconsistency: the production pipeline merges text boxes into blocks via `cluster_words_into_blocks`; the tile experiment does not perform this merge, so the 193 number is not comparable to the "0 region" number. This is a real methodological finding worth noting: the tile experiment omits the production merge step, so the claimed recovery is at word/text-box level, not at the region level production actually returns. If merge were applied, the count would be lower but still >0 presumably. That's not fatal to the root cause (the raw page also had 0 text boxes at threshold, so 0 regions follows), but it weakens the "0→193 recovery under byte-identical production sequence" claim in the Handoff/AC2 wording: "每块走与生产逐字节相同的推理序列" — tile inference sequence is identical, but the post-inference chain (merge) is not. Actually the claim is scoped to "推理序列" which is technically accurate. But the 193 number is presented as "去重检出" vs provider's "region". The task AC2 says "块级是否恢复候选" — candidates. In production terms candidates = blocks after merge. So the experiment measures a different quantity than "候选". This is worth a P2/P3 finding.

Also note: `official_post_process_ge_0_5` for K01 = 0 while manual count_ge 0.5 = 0. Fine.

Another check: diagnosis claims "BJ02 仅用 10 个 query 即饱和" — need to check class_wise for BJ02.

Another key: for K01 class_wise: class 2 has count_ge_0_1 = 7, max 0.2045. Classes 0 and 1 max 0.0. Interesting — zero for bubble class. Hmm, class_wise "0" max = 0.0 and "1" max = 0.0 while class "2" max = 0.2045. That means for all 300 queries, the argmax class was never 0 or 1 — i.e., class 2 dominates all queries. That's suspicious but plausible for a collapsed distribution.

Wait — there's a subtlety in the class_wise computation: it groups by argmax label, so class 0 and 1 max = 0.0 means no query had 0 or 1 as argmax. OK.

Now the "垂直压缩 ~97×" arithmetic: 62133/640 = 97.08. Yes. But note the claim "垂直压缩 ~97×" — correct as a ratio of height to target height. However the diagnosis frames "垂直 ~97×" as the compression. Fine.

But there's a nuance: the model input is 640×640, and the page 690×62133 → the horizontal is compressed 690/640 = 1.078×. So anisotropy. Accurate.

Now key methodological question 1: is 1024²/overlap 128 justified? The script docstring says 128 px = 12.5% overlap, inside the task's 10–20% band, multiple of RT-DETR stride 32. But 128/1024 = 12.5%, and the task doc... let me check: the task's AC2 says "用 K01 裁切成 1024×1024 块实测" — the task itself specifies 1024×1024. Overlap band 10-20%: where does that come from? The task doc doesn't mention overlap band. The script comment says "128 px overlap (12.5%, inside the task's 10-20% band...)" — that band is not in the task doc (the task says only "1024×1024 块"). Hmm, maybe from another doc (an earlier proposal?). Let me grep for "10" and "20%" in task/docs/handoffs. Actually the task doc I read has full content: 允许修改面, 纪律, AC. No mention of 10–20% overlap. So "任务书 10–20% 带内" is an unsupported claim (misattribution). That's a documentation accuracy finding (P3). Let me verify by grep for "重叠" or "10–20" or "10-20" in docs.

Also "RT-DETR stride 32" justification: 128 is a multiple of 32, and 1024 too. Reasonable.

Question about 70 tiles: height 62133, tile 1024, step 896. Number of tiles = ceil? Let's compute: y goes 0, 896, ..., while y < height. The last tile starts at y where y < 62133. The number of tiles = floor((62133 - 1024)/896) + 1 + ... Let's compute: tiles start at 0, 896*k. Need 896k < 62133 → k < 69.35 → k=0..69 → 70 tiles. Yes 70 tiles. Last tile origin 896*69 = 61824, crop_h = min(61824+1024, 62133) - 61824 = 309. Matches "含尾块 crop_h=309". Let me verify in JSON later.

70/70 tiles having ≥1 detection: min per-tile count is 1 (tile 13 has 1). So "1–18 per tile". Is this plausible as genuine? The claim of false positives from "small image everywhere has boxes" — the tiles are 1024×1024, that's a normal-ish size, not tiny. And confidences are high (0.9+ mostly). Which contradicts "重缩放后小图处处有框假阳性" concern. Actually the concern in the review brief: "70/70 块全有检出是否可能是重缩放后小图「处处有框」的假阳性". The tile is 1024², downscaled to 640², similar to BJ02's 2946×4167 → 640×640 (compression 4.6–6.5×). For BJ02 the model produced only 10 detections ≥0.5 out of 300 queries — so no "处处有框". But no per-block BJ02 control was run. Hmm — a good control would be: run the tiling on BJ02 (a normal page) and compare, or run the same full-page path on 1024² crops of K01 vs. a padded/gray-only tile: pad-only tiles would test whether the pad (constant 114 gray) region yields false positives. The probe did measure `n_dropped_center_in_pad = 0` for all tiles → there were no detections whose center fell in the right pad band (x>690). But wait — that's only the *center in pad* filter; detections *entirely within* the right pad band would also be dropped by center filter. Zero dropped means the model produced no boxes in the gray pad region at all. That's actually decent evidence against "pad creates false positives". But it doesn't address false positives within the content.

A stronger control: "空白/纯灰块" tile. Not run. Worth noting as directional limitation, which the doc acknowledges partially ("无 ground truth").

Min conf 0.5009 — touching the threshold. The distribution: many boxes at 0.90+, a tail near 0.50. The min is the minimum of the *deduped* set which is the same as min over mapped since NMS keeps. Note tile 19 has 18 detections with confs from 0.8399 down to 0.5009 — nearly all near threshold. That suggests tile 19 (origin 17024, covering 17024–18048) is a region where the model emits many low-confidence boxes clustered near 0.5–0.6, possibly a text-dense panel or possibly a false-positive burst. This deserves flagging: the "conf distribution 健康" claim for the deduped set overall (mean 0.85) is skewed by the many high-confidence ones; a per-tile analysis shows at least one tile with 18 boxes mostly at 0.50–0.60, which is exactly the shape of a threshold-boundary burst. The doc does say "未见重复爆炸", but doesn't analyze tile 19. Worth a P2/P3 finding: no per-tile distribution analysis / no check whether the 18-box tile is duplicate-heavy (which NMS should have removed). Actually important: NMS IoU 0.5 removed only 226→193 (−33). If tile 19's 18 boxes are the same text detected multiply... no, within a tile there'd be no duplication unless model emits overlapping queries. RT-DETR without NMS (set prediction) generally doesn't need NMS. 18 boxes in one 1024px tile with 12.5% overlap — plausible for a text-dense panel.

Hmm, but here's a deeper issue: does the dedup actually work across overlap bands? Overlap band is 128px at the bottom of each tile and top of the next. A bubble straddling the boundary might be detected partially in both tiles. With IoU 0.5 requirement, a box detected fully in tile A and a truncated box in tile B would have IoU maybe < 0.5 → both kept → duplicate/partial boxes. The doc admits cross-block truncation risk and says "在本实验中未观察到病态输出（无超长/退化框进入 sample）" — but the sample is only 40 boxes sorted by y, and there's no explicit duplicate-rate measurement per overlap band. The 226→193 (−33) dedup count presumably reflects overlap duplicates. But we can't distinguish "true duplicate suppression" from "both copies kept". A proper check: count boxes near band boundaries. Not done. This is a legit P2 finding: de-dup effectiveness not independently verified (no per-band analysis, no ground truth), and the "NMS IoU 0.5 实测有效" claim in §3-A rests on the −14.6% reduction which is not evidence of correctness (could be removing real boxes vs duplicates; or failing to remove duplicates).

Actually let me reconsider: NMS with IoU 0.5 on boxes that don't overlap removes nothing. The 33 removed must be overlapping pairs, likely same-object double detections across tiles. But NMS can also merge two distinct nearby text boxes with IoU>0.5? Unlikely for text boxes. Fine. Still, claim "实测有效" is weak but not wrong; the doc labels it directional.

Another methodological issue: In the tile experiment, the boxes are in tile-local coords, mapped back by adding origin_y. But the tile was **padded** to 1024 width: crop is 690 wide (full page width) padded to 1024. Since tile is exactly 1024 tall (except last), the resize to 640×640 shrinks by 1.6×. Then post_process with target_sizes = tile shape (1024×1024) → coords back in tile space. Good.

For the last tile (crop_h=309), the crop is 690×309 padded to 1024×1024 — the actual content occupies only 309 of 1024 rows → after resize to 640×640, the content is squeezed vertically by 1024/309 = 3.3× (since processor resizes 1024→640 uniformly, and content is only 30% of the height). So the last tile's content is anisotropically... no, actually it's uniformly scaled 1024/640 = 1.6×, but the content only occupies 309/1024 = 30% of the frame → after resize, content is 193px tall in a 640px frame. That's a 690/1024 wider... wait: crop is 690 wide × 309 tall, padded to 1024×1024 (right and bottom pad). Then resized to 640×640: content becomes 690/1.6 = 431 wide × 309/1.6 = 193 tall. So the content is preserved proportionally! No anisotropy — padding keeps aspect ratio. Good, that's actually the point of padding. So the last tile content is at 1.6× downscale, same as others. Fine. Actually this means padding to square is what preserves aspect ratio, which is a valid design. Good.

Hmm, but wait: the page width is 690, padded to 1024 → content occupies 67% of width. So effective downscale of content is 1.6×; content is rendered at 431×640 for full tiles (690/1.6=431). Wait no: for a full tile, crop is 690×1024, padded to 1024×1024 → content occupies 690/1024 of width → after resize to 640×640, content is 431 wide. So the content has ~1.6× downscale in both axes (690→431, 1024→640). Yes uniform, correct aspect ratio. Good.

Wait, but there's an issue: the padding to 1024 wide means the aspect ratio of the padded square is 1:1 but content 690:1024 = 0.674. After resize to 640×640 (square), content becomes 431×640 → aspect preserved. Yes.

So the tile approach preserves aspect ratio and content scale. Good methodology. The 1.6× compression vs BJ02's 6.5× — hmm, BJ02 2946×4167 → 640×640 = 4.6× (width 2946/640=4.6) and 6.5× (4167/640=6.5). So it's anisotropic for BJ02 too (no padding) and yet it works. Interesting: the diagnosis used BJ02's "6.5×" as "正常检出分布" and argued that 1280 size still compresses 49× ≫ 6.5×. But BJ02 is anisotropic with 4.6 vs 6.5 — so the model tolerates anisotropy at ~5× but not 97×. The threshold between 6.5× and 97× is unbounded in the evidence — there's no experiment at, e.g., 10×, 20×. So the "C is excluded because 1280 still compresses 49×" argument is directionally reasonable but the claim "远超 BJ02 正常检出的 6.5× 分布" is a weak comparison (single control with 6.5×; no dose-response curve). Worth flagging as a limitation of the C exclusion: it's plausible but not measured. The doc does say "没有任何证据表明更大 size 能恢复" — honest. But the diagnosis.md wording "远超 BJ02 正常检出的 6.5× 分布" implies a threshold that isn't established. I'd flag as P3.

Now, the deeper question the reviewer brief raises: does BJ02 vs webtoon comparison exclude the "webtoon domain style" confounder? BJ02 is a Japanese manga (Black Jack) page — different domain (JA vs KO), different style, and different layout. The comparison shows the *pipeline* works on a normal-aspect page, but cannot separate "webtoon content unseen by model" from "resolution collapse". The key disambiguation is the tile experiment on K01: same content, same weights, same threshold, only resolution changed → 0→193. That's a genuinely strong controlled intervention (within-page, within-content). So the root-cause chain closes via the tile experiment, NOT via BJ02/docTR. The owner's argument does rely on the tile experiment to close — and the diagnosis.md §2.3 explicitly says "0 → 193 的恢复是根因的直接反证". So the logic is complete, though diagnosis §2.2's framing could imply BJ02/docTR does more work than it does. Actually §2.4's exclusion of "输入 decode/通道错误" uses BJ02 + sha256; that's a different hypothesis (pipeline bug) and BJ02 is valid for that. Good.

But wait — is there an alternative explanation for 0→193 that the tile experiment does NOT exclude? Consider: the tile experiment uses the *same model* but now each tile is a 1024² padded square. Another possible confounder: the model might be responding to the *gray padding border* rather than content? No — boxes are mapped and center-filtered to content, and 0 dropped in pad. Hmm, but the center filter only drops boxes whose center x > 690. A box spanning pad and content with center in content would be kept with x1 clipped? No, x1 isn't clipped in the probe (mapped box keeps x1 possibly > 690). Median box width 144.1, so boxes are small; unlikely to span. Also the pad is on the right (width) and bottom (last tile). The pad value 114 gray is a constant region; the model could produce "text_free" boxes on it, but 0 center-in-pad dropped → none. OK.

Another alternative: maybe the model does respond to webtoon content but the *full-page* path has an additional failure (e.g., the processor's handling of a 62133px tall image producing garbage) — but that's the same root cause (resolution). Fine.

Still, one alternative not excluded: the 0 at full page could ALSO be partly due to the extreme aspect ratio breaking the processor or creating an out-of-distribution input in a way that even a bigger size wouldn't fix — but that is the same conclusion. Fine.

So root cause chain: I'd rate A solid, with a caveat that the tile experiment's "193" is at text-box level (no production merge), so the quantitative recovery claim isn't apples-to-apples with the 0 region count, though the qualitative conclusion (signal recovered) holds since full-page raw ≥0.5 count is 0 too.

Actually, that's the key: full-page raw_observability counts_ge 0.5 = 0, and official post-process = 0, both before merge. So the comparison "raw text boxes ≥0.5: 0 (page) → 193 (tiles, post-NMS)" is apples-to-apples at the text-box level. The doc's headline says "0 → 193 去重检出". The doc's table says provider region 0. Slight mixing. I'll flag as a precision/documentation issue (P3) rather than a correctness issue, and note that stating "0→193 candidates" in the task doc delivery record is inaccurate since production candidates are post-merge blocks; the AC2 wording "块级是否恢复候选" is loosely satisfied.

Hmm, wait. Let me reconsider: is it really true that the production full page gave 0 text boxes? provider_detect region_count=0 and the merge of zero boxes yields zero blocks. And official post_process ≥0.5 = 0 → no text boxes at all. Yes.

Now let me look for the second part of the JSON — BJ02 raw observability, K02/K04. And the deduped_boxes_sample. Let me continue reading the diff (1299-2408).

Also: the review needs to verify "范围纪律": diff files = handoff, task, experiments script, diagnosis.md, probe-results.json → 5 files. Handoff says "git show 2d6b7bf6 --stat 仅 4 个文件" — the 4 files being experiments/verification/task doc? Let's count: commit 2d6b7bf6 (implementation) contains: experiments/diagnose_webtoon_detect.py, verification/diagnosis.md, verification/probe-results.json, doc/tasks/...md = 4 files. Then b311f52f (docs) adds the handoff. The Owner claim says "5 文件全允许面". The diff shows 5 files total: handoff (new), task (modified), experiment script (new), diagnosis.md (new), probe-results.json (new). All within allowed paths. Good. But note: the diff includes both commits presumably (base 8996ca55 → tip b311f52f). Let me verify the diff has only these 5 files by grepping "diff --git" in the diff file.

Also check: `doc/STATUS.md` not modified — confirmed by diff file list.

Also the handoff header says base_commit: 8e0de8d0 and delivery_head: 2d6b7bf6, but the task's base_commit is 8e0de8d0 while the review brief says base=8996ca55. Fine: 8996ca55 is the 4-Task batch release commit on top of 8e0de8d0? Actually the handoff says "base 8e0de8d0，其上的 8996ca55 为四 Task 批量释放 commit". So the diff base for review is 8996ca55.

One inconsistency: task doc front-matter `base_commit: 8e0de8d0`. Handoff says "复审范围 git diff 8996ca55..2d6b7bf6（实现）+ 本文档 commit". Since the diff file we got is review-input.diff, let me check what it contains — it starts with the handoff as a new file, so it's 8996ca55..b311f52f. Good.

Now — a critical scope question: does the commit 2d6b7bf6 actually include the probe-results.json? Yes.

Big question 4: is probe-results.json too large for the repo? It's 1626 lines. Let me estimate bytes. 1626 lines × ~30 chars ≈ 50KB. Fine. Let's check actual file size via... pwsh is unavailable (sandbox error). Let me try read with limit to check total lines: read showed "(Showing lines 500-... of 2408" for the diff. For the JSON file, I can read it directly. Let me get its line count by reading with a huge limit... the read tool returns total lines. Let me do that later.

Hmm, also: "无 __pycache__ 入库" — can't verify without git; but the diff file list is authoritative for what's in the commit.

Let me check the whole diff for all "diff --git" lines and also for any binary file markers ("Binary files").

Let me also check whether probe-results.json includes full per-tile confidences (yes) — 70 tiles. That's reasonable evidence, not excessive. The deduped_boxes_sample only 40 boxes (out of 193) — the doc says "40 个去重样例框". Since the full 193 boxes aren't stored, an independent reviewer can't recompute NMS or verify 193 from the JSON. Actually you can't recompute the dedup: the JSON stores per-tile confidences (mapped) summing to 226 and per-tile counts, but not the box coordinates of all 226 → the 226→193 dedup is not reproducible from the JSON. That's a legitimate finding: reproducibility gap. Coordinates of all mapped boxes would be needed to verify NMS. The sample of 40 sorted by y gives some. This matters for "判定-证据-结论链是否可独立复核" (review item 5). I'd flag P3: probe-results.json stores only 40 of 193 deduped boxes and no pre-NMS coordinates → NMS result not independently recomputable; recommend storing all boxes or a per-band duplicate analysis. But is it a blocker? For a diagnosis task, high-volume raw data... The claim "226→193" can't be checked. Reviewer should note it. It's directional evidence.

Hmm, also there's a subtle bug candidate in the probe: `deduped_conf.min` = 0.5009 — that's a raw conf, fine.

Another potential issue: `greedy_nms` uses `_iou(candidate, keeper) <= iou_threshold` — standard.

Another: in tile_experiment, `page_box = (x0, y0 + y, x1, y1b + y, score)` — variable name shadowing `y1` (the tile end) with `y1b`. The loop variable `y1 = min(y + TILE_SIZE, height)` is assigned before, then reused as `for x0, y0, x1, y1b, score in tile_boxes` — they named the box's y1 as `y1b` to avoid shadowing. OK, no bug.

But: does the mapped box need x/y order check? `results["boxes"]` from post_process are (x0,y0,x1,y1). Fine.

Another: the drop rule uses center_x > width (690). Since boxes are in page coords with x from tile-local (tile width 1024), boxes in the pad have x0 ≥ 690. A box with center < 690 but extending into pad is kept. Minor.

Another: The last tile crop_h=309 with content only in top 309 rows; boxes detected there get y0 + y where y = 61824. Fine.

Now let me also check for the "RT-DETR stride 32" claim — is the RT-DETR-v2 backbone stride really 32? Typically ResNet backbone with stride 32 for the final stage. Fine, unverified but plausible. Minor.

Now let me check the "10-20% band" claim in the task doc. Need to grep. Also check experiments/M2-TA3-B/case-selection.json to verify the six ko cases and layout types (K05/K08/K19). Also check whether BJ02 exists in that manifest.

Let me continue reading the diff and do greps in parallel.

Actually, the diff is the authoritative artifact but the working tree files are easier to read fully. Let me read the actual files in the worktree: verification/M2-DETECT-WEBTOON-DIAG/probe-results.json and diagnosis.md. But careful: the worktree file might differ from the diff (working tree clean claimed). I'll cross-check a couple of values.

Let me read the diff remainder in two big chunks (1299-1700, 1700-2408) — actually the JSON part is mostly tile data. Let me instead grep the diff for specific keys to extract: BJ02 page block, K02, K04, deduped_boxes_sample. Better: read the JSON file directly from worktree, which is the same content.

Plan:
- read probe-results.json lines around BJ02 and K02/K04 and the sample.
- grep the diff for "diff --git" lines.
- grep for "10–20" or "10%" in task/handoff.
- read experiments/M2-TA3-B/case-selection.json (read-only) to confirm six cases + BJ02.
- check TA3-A smoke-K01.json for the 15 candidates claim.

Let me batch these.
dsh: reasoning:
Confirmed: 5 files in diff, no binary. Case selection covers the 6 ko webtoon cases (K01, K02, K04, K05, K07, K08, K09, K10). The task says six cases K01/K02/K04/K05/K08/K19. Wait — K19 is `paged_webcomic` layout, NOT `webtoon_long_strip`! The task background says "生产 ogkalu 对 webtoon 长条漫 0 候选（K01/K02/K04/K05/K08/K19 六 case）". But per the manifest, K19 = `layout_type: paged_webcomic` (Pepper&Carrot ep20 page 1), and K11 also paged_webcomic. So the "ko 6 case" list mixes layout types. Hmm, but the infographic says the F1 is about ko cases; the six ko cases in TA3-B2 F1 may be "ko 侧 0 候选" not necessarily all webtoon_long_strip. Let me check TA3-B2 evidence to see the F1 case list. This matters because:
- The root cause (whole-page downscale) explains webtoon_long_strip pages (K01/K02/K04/K05/K08). K19 is paged_webcomic (Pepper&Carrot ep20 P01) — probably a normal-ish aspect page? If K19 also returns 0 candidates, that would NOT be explained by the long-strip downscale mechanism, and would weaken the "single root cause" claim / and the tiling fix wouldn't necessarily address K19.

This is a potentially significant finding! Let me check TA3-B2 F1 evidence. Let me find the TA3-B2 verification files.

Also K11 is paged_webcomic with 0? The excluded. Let's look for TA3-B2 docs: verification/M2-TA3-B2/**.

Let me grep for "F1" and "0 候选" in verification and doc.

Also note the task doc's AC2 requires the ko 6 case list to be re-run in the fix task, including K19 — if K19's failure has a different cause (e.g., its aspect ratio or content), the tiling fix might not close it. Worth a finding (P2): the diagnosis never inspected the six-case geometry; only 3 webtoon_long_strip pages were probed (K01/K02/K04). K05/K08/K19 were not probed at all, yet the task claims the root cause covers the six-case F1. K19 is a different layout type and its 0-candidate cause is unverified.

Hmm, but the background given in the review brief says: "生产 ogkalu（RT-DETR-v2）对 webtoon 长条漫 0 候选（K01/K02/K04/K05/K08/K19 六 case）". Maybe the F1 evidence lists those six as failing. Let me verify from TA3-B2 evidence. Let me search.

Let me look at the TA3-B2 verification directory.
dsh: reasoning:
Very important finding from `verification/M2-TA3-B/quality-report.md:52`:

"| K19 | ko | 0 | 0 | 同 K01 | SKIPPED | — | 1.0 | F1（页面实测 1200×1660，...）。该页所有语言 SVG 文本层为 0 元素=**无字页**，检出无候选是**正确行为**，但生产 step 状态为 failed/INVALID_INPUT——口径问题见 F4）"

And F1 description at line 140: "K19(1200×1660 无字页；...) 同状态（检出无候选对无字页是正确行为，但生产 step 状态=failed 而非空成功，见 F4）"

So K19's 0 candidates is CORRECT behavior (blank page, no text), not the resolution-collapse bug. It's grouped in F1 as a caliber/state issue (F4), not a detection failure.

So the review brief's premise and the Task's "ko 6 case（K01/K02/K04/K05/K08/K19）" includes K19 which is a text-free page whose 0 candidates is correct. This means:
- The fix Task's acceptance criterion "ko 6 case 候选数 >0" (handoff §下一任务建议: "ko F1 六 case 候选数 >0 且全链可用") is **unachievable/incorrect for K19** — a text-free page must return 0 candidates; requiring >0 would force false positives or an impossible gate.
- The diagnosis.md §3 推荐排序 line 115 says "验收 = ko 6 case（K01/K02/K04/K05/K08/K19）重跑 qualification 关闭 F1" — implies K19 should also be fixed by tiling, which is wrong: K19's case is an F4 state-caliber issue.

Wait, but I should be careful: the task doc background also lists K19 六 case. Was the source (TA3-B2 F1) grouping? The F1 line includes K19 with the note. And 1.1a groups "K01/K02/K04/K05/K08/K19 F1". So upstream TA3-B2 grouped K19 into F1 (with the caveat). So the owner inherited the grouping. But the owner's diagnosis states confidence high for "整页重缩放致目标消失" for the six-case F1, while K19 (1200×1660, aspect 1.38, compression ~1.9×) is a text-free page, not a long strip. The diagnosis doesn't mention this at all — it never probed K19 nor accounted for the fact that the ko-6 list includes a 无字页 whose 0 candidates is correct.

This is a genuine P2 (maybe P1?) finding for the fix-Task acceptance criteria: "六 case 候选数 >0" is an invalid gate for K19. Should be P2 — it doesn't invalidate the diagnosis of the 5 webtoon long strips, but it does propagate an incorrect acceptance criterion into the next Task and mis-states the scope of the root cause ("六 case" all explained by downscale).

Let me confirm the exact wording of the F1 acceptance in handoff: "验证命令、环境与完成 Gate：主 venv + PYTHONPATH=src；单测全绿 + 三套件回归 0 failed + ko F1 六 case 候选数 >0 且全链可用". Yes, "候选数 >0" for six cases including K19. That's an error. Also "交付物：... + ko 6 case（K01/K02/K04/K05/K08/K19）重跑 qualification 证据".

Also check K05/K08 dimensions — not probed. Fine.

Now, also worth checking: is K11 (paged_webcomic, 0 candidates?) — no, K11 is fine.

Let me now read the quality-report F1/F4 sections for precision, and also check the TA3-A smoke-K01.json claim (15 regions) — need to confirm. Let me read the relevant part of smoke-K01.json and quality-report lines ~40-70 and ~130-160.

Also I need to check probe-results.json remaining content: BJ02 raw observability (does it show count_ge 0.5 = 10?), K02/K04, deduped sample. Let me read the JSON file in worktree directly (it's ~1626 lines). Let me grep for key values instead.

Let me plan the remaining reads:
1. quality-report.md lines 40-70 and 130-160 (F1/F4).
2. TA3-A smoke-K01.json relevant fields.
3. probe-results.json: BJ02 + K02 + K04 sections and the deduped sample and tail.
4. Check whether BJ02 path in JSON is the TA2B worktree path (fine).
5. Check STATUS.md for the task registration (scope/authorization). Maybe not needed.

Let me batch.
dsh: reasoning:
Confirmed BJ02: region_count=5, counts_ge 0.5=10, official=10. So 10 raw ≥0.5 → 5 blocks (merge) → and "bubble 丢弃 5"? Let's see: class_wise for BJ02 to check how many text vs bubble. Let me read the BJ02 block lines 1535-1660 and K02/K04 blocks, plus the deduped sample (1088-1371).

Let me also verify the tile count and last tile. And check the per-tile min counts: is any tile 0? n_dropped all 0. Need n_boxes_raw values; grep didn't capture. Let's read the tile section summary lines 1020-1120 and the sample.

Let me read probe-results.json 1020-1120 and 1372-1660.
dsh: reasoning:
BJ02: 10 raw ≥0.5 = 5 bubble (class 0) + 5 text_bubble (class 1) → text boxes = 5 → merged into 5 blocks (region_count=5). So "bubble 丢弃 5" is accurate; and "10 检出" accurate. And the diagnosis claims "BJ02 仅用 10 个 query 即饱和" — accurate.

Interesting: BJ02 counts_ge "0.3": 10, and 0.1: 14 → a sharp gap. Webtoon pages: 0.1: 7/4/14, 0.3: 0. So the webtoon pages' score distribution decays smoothly below 0.3 with no >0.3 — consistent with collapse. BJ02 has a bimodal shape (10 strong, gap, then 4 weak). Good.

Now the JSON's class_wise for K01: class 0 max 0.0, class 1 max 0.0, class 2 max 0.2045. Hmm — so at full page, the argmax class for ALL 300 queries is class 2 (text_free). No bubble class predictions at all. That's fine.

Now let me look at the deduped_boxes_sample: first boxes at y=156.7, 714.7, 1105.4, 1627.7, 1896.4, 2266.3, 2569.6, ... The tile 0 covers y 0–1024, tile 1 covers 896–1920. The box at y=1105.4 (tile 1) and 1627.7 (tile 1), 1896.4 (tile 1). Hmm, tile 1 origin 896 covers 896–1920, so boxes at 1105, 1627, 1896 are from tile 1 — matches tile 1's 3 confidences [0.943, 0.9365, 0.6356]. Box y=1105.4 conf 0.9365, y=1627.7 conf 0.943, y=1896.4 conf 0.9485? No wait 0.9485 is tile 2. Hmm, the box at y=1896.4 has conf 0.9485 which is tile 2's top confidence (tile 2 origin 1792, covering 1792–2816). And box y=2266.3 conf 0.8974 also tile 2's third. And box at y=2569.6 conf 0.9472 (tile 2's second). So tile 1's box at 1896.4 with conf 0.6356 must have been deduped away or... Actually the sample is sorted by y and shows the first 40 deduped. Let's see: tile 1 boxes: confs [0.943, 0.9365, 0.6356]. The sample shows y=1105.4 (0.9365) and y=1627.7 (0.943) → two of tile 1's three; the 0.6356 one presumably had center... hmm it should appear in the sample if not deduped. Unless it was deduped against a tile-2 box with IoU>0.5 (i.e., the same bubble detected in both tiles!). That would be exactly the overlap duplicate case. Interesting but speculative.

Anyway, NMS dedup: 226→193. But we cannot verify since only 40 boxes stored.

Let me now check the remaining key issue: the "10–20% band" attribution. The task doc doesn't mention it; the script docstring says "inside the task's 10-20% band". Let me grep the whole repo for "10–20" to see whether any doc (e.g., a Codex proposal or review) establishes that band.

Also check STATUS.md for this task's registration/authorization and to see if there's a recorded reviewer.

Also I should check the handoff for the claim "base_commit: 8e0de8d0" vs brief's base=8996ca55 — fine.

Let me grep for "10-20" / "10–20" across the repo (md files).
dsh: reasoning:
Key context confirmed: STATUS says the Active Task is "无 Active Task——TA3-B 家族全链收官，等用户三项裁决" and M2-TA3-B2 done. The M2-DETECT-WEBTOON-DIAG task is authorized by user_ruling_2026-10-01_all_four. The STATUS.md wasn't updated (禁改面). OK.

Also important: STATUS says F1 = "ogkalu 对 webtoon 长条漫 0 候选 ×6=Gate 最大单因". And quality-report line 52 says K19 is a text-free page where 0 candidates is correct behavior. Both co-exist in the record.

Now, the grep for "10–20" found only the diagnosis.md and script docstring — so "任务书 10–20% 带内" is not supported by the task doc (doc/tasks/M2-DETECT-WEBTOON-DIAG.md). Let me double check the task doc — maybe there's more content in another section? The task doc is only 50 lines and I read it fully. It says "用 K01 裁切成 1024×1024 块" — no overlap band. So the "10–20% band" attribution is an unverifiable provenance claim (P3/P4). Minor.

Let me also verify the K02/K04 raw observability details (score_max 0.1666 / 0.2835, counts). And check the diagnosis claims about K02 "600×18401 28.8×" (18401/640 = 28.75 ✓), K04 (28156/640 = 43.99 ✓), K01 97.08 ✓, BJ02 6.5× (4167/640=6.51 ✓).

Let me read lines 1372-1535 for K02/K04 to double-check counts_ge (0.3) = 0 and class_wise.

Also I want to verify the claim in diagnosis §2.2 point 2: "K01 在 ≥0.01 有 143 个 query" ✓ (counts_ge 0.01 = 143).

And "300 个 query 全部有非零分数（counts_ge[0.0]=300）" — hmm, count_at(0.0) counts scores >= 0.0, which is always 300 unless negative. So "全部有非零分数" is WRONG: `counts_ge["0.0"]=300` only proves all scores ≥ 0, not that they're non-zero. Since sigmoid output is always ≥0 and ≤1, counts_ge 0.0 is trivially 300 for any input. The diagnosis uses this as evidence that "输出管线正常" — that's a weak/incorrect inference: sigmoid output is always in (0,1), so counts_ge 0.0 = 300 is trivially true regardless. Actually it also lists 0.01: 143 for K01 (nontrivial). But the sentence "300 个 query 全部有非零分数（counts_ge["0.0"]=300）" is a logical error — with sigmoid it's tautological. For BJ02 0.01 = 240. So the diagnostic value of counts_ge["0.0"] is zero. This is a legitimate P3 finding: the "输出管线正常" argument partly relies on a tautological statistic; the non-tautological version is counts_ge 0.01 (143/300 for K01) and the fact that logits are finite. Also there's no explicit recording that the raw logits are finite (no NaN check) — a NaN in logits would make sigmoid NaN, and `max()` with NaN → nan; then score_max would be nan. score_max is a number, so no NaN in K01. OK, so the conclusion holds but the stated evidence is partly tautological. Worth noting as P3/P4.

Hmm, let me be careful: is `counts_ge["0.0"]` = 300 trivially true? scores are sigmoid outputs ≥ 0 → yes always 300. The doc's inference "模型'看到了什么'但远不构成检出" is fine from 143@0.01.

Now let me also consider the "official post_process cross-check" claim: "official_post_process_ge_0_5 与手工 ≥0.5 计数在四页全部相等（webtoon 页 0=0，BJ02 10=10）". Both are 0 for the webtoon pages — so that's a trivially-equal comparison (0=0) for 3 of 4 pages; only BJ02 has a nontrivial 10=10. The doc says it "在四页全部相等" which is literally true but 3/4 are trivial. Minor. Actually for the cross-check purpose (does my manual reduction agree with the official post-process), agreement at 0 is weak; but the manual reduction is over ALL 300 queries which is exactly the point. Hmm, with threshold 0.5 and max score 0.204, agreement is trivial. But the real cross-check would be at a threshold where counts are nonzero, e.g. 0.1 → official post_process at 0.1 should give 7 for K01. The probe only cross-checked at 0.5. So the cross-check is weak for the 3 webtoon pages. Worth P3 note (measurement self-consistency claim over-stated: 3/4 comparisons are 0=0).

Now the diagnosis claim "K01 塌陷分数分布在 143 个 query 上，与容量无关" — fine.

Next: the tile experiment omits `cluster_words_into_blocks` — I established that. Let me double check the probe's run_tile_inference: it applies only class filter (1,2) and threshold. So yes no merge. The 193 is text-box count. And the doc §2.3 table says "去重后 conf max 0.9666..." and §1 says "0 检出恢复到 193 个去重检出". Handoff says "0 → 193 去重检出". Task doc says "块级 0→193 去重检出". The phrase "检出" is at text-box level while the page-level "0" was region (post-merge block) count — but also raw text boxes 0. So actually both are 0 at both levels, and 193 is at text-box level while region level would be fewer. Since the reviewer needs to flag that the returned "candidates" (production) would be ~blocks, not 193. The AC2 wording "块级是否恢复候选" — the experiment shows candidate *signal* recovered. I'll flag as P3 documentation precision: state that 193 = post-NMS text-class boxes before the production `cluster_words_into_blocks` merge, so the production candidate count would be lower; the diagnosis never applies the production merge in the tile path, meaning the "recovery" is not measured in production output units. Recommend the fix Task's qualification measure region counts.

Also: does the production path apply NMS? No. RT-DETR is set-based. In the fix (方案 A), the doc suggests page-level NMS. But the frozen production merge `cluster_words_into_blocks` already clusters words into blocks with MERGE_* constants; adding NMS before it is a new stage. The doc's 方案 A says "页级 NMS → 输出绝对像素 text_boxes". Introducing NMS in the provider is a new behavior not present in the current frozen sequence; the diagnosis acknowledges risk. Fine. But note the doc claims "契约零变更" — the output contract is unchanged, but the detection semantics (NMS + tiling) is a behavior change that could alter results on non-webtoon pages if tiling triggers wrongly. The doc does say triggering conditions must be configurable and based on aspect/size. OK.

Now, performance: "CPU 19.8s/70 块" vs "生产 273ms/页先例" — handoff says "性能从 273ms/页变为秒级/页（70 块实测 19.8s CPU）". But actually tile inference is 19793ms for 70 tiles ≈ 283ms/tile, and full page K01 was 574ms (provider_detect elapsed_ms=574, raw infer 297ms). So per-page cost goes 0.57s → 19.8s (34×). The doc says "生产 273ms/页先例" — where's 273ms from? BJ02 provider elapsed 333ms, infer 277ms. Hmm "273ms/页" is not in this JSON. It's presumably from C4 qualification perf logs. It's cited as "先例". Not independently verified here → NOT_VERIFIED. And "秒级/页" is actually ~20s/page, which is more than "秒级" in the ordinary sense but technically seconds. The handoff says "CPU 秒级/页" and diagnosis says "CPU ≈19.8s/70 块/页". For 62133px page: 70 tiles. For a shorter webtoon (K02 18401px → ~20 tiles) it'd be ~6s. Fine. But the handoff "验证命令...performance 基线登记（CPU 秒级/页预期）" is vague — 20s/page is a 34× regression that deserves explicit product-level expectation management, and the doc does mention "超长页需预期管理". OK. I'd note in findings that "秒级" understates 19.8s for the worst case; recommend the fix Task carry an explicit latency budget (e.g., ≤ X s/page) rather than "秒级".

Also concurrency: since page height 62133 and tiles are independent, batching could speed up (RT-DETR accepts batches). Not needed.

Another point: memory. Each tile is 1024²×3 = 3MB padded; full page rgb 690×62133×3 = 128MB (fits). Fine.

Now let me check the remaining JSON sections (K02, K04) quickly and the tile confidences' full set to assess distribution health and the min. Also I want to check the first tile's data (tile 0 origin 0) and count tiles=70 and whether all 70 have n_boxes_raw ≥1 (the doc claims 70/70). The confidences lists: I can compute from the grep? No. Let me verify by reading the tile array — it spans lines ~150-1087, that's 937 lines for 70 tiles. That's a lot but I can spot-check. Actually I can verify "70/70 have ≥1" by checking whether any "n_boxes_raw": 0 appears in the file.

Let me grep for '"n_boxes_raw": 0' in probe-results.json.

Also check total_raw_detections=226 = sum of n_boxes_raw. Can't easily sum. But I can check whether the sum of tile confidences counts equals 226 by counting lines? Too heavy. Alternative: verify a few tiles.

Actually, I can verify the sum via a script... no shell. Hmm, pwsh failed with a sandbox ACL error, not a policy denial. Maybe retry pwsh once — the error was "SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)". This is a sandbox setup failure, likely because the workspace ACL can't be modified. The user instruction says "沙箱无 shell 时不执行命令" — explicitly tells me not to run commands. So I should treat shell as unavailable and mark shell-verifiable items NOT_VERIFIED.

Let me do the key greps.
dsh: reasoning:
No "n_boxes_raw": 0 and no "n_boxes_mapped": 0 → so all 70 tiles have ≥1 raw detection. Confirms "70/70 块全部有 ≥1 检出". Good, that claim is verifiable.

Now, the 70/70 claim in the doc says "单块检出 1–18 个" — but tile 13 has 1, tile 19 has 18. Verified.

Now I have enough on the JSON. Let me also check TA3-A smoke-K01.json to verify the "docTR 15 candidates, same page sha256" claim — this is a key cross-referenced evidence.

Also check the handoff file itself in worktree vs the diff (identical presumably).

Also verify that no `src/**` was changed in the diff — confirmed by the 5-file list.

Let me also verify the diff has no trailing whitespace issues claim (git diff --check EXIT=0) — can't run; the diff content itself: let me check for trailing whitespace in added lines. Hard via grep but I can try grep for lines ending with space in the diff. Ripgrep pattern ` +$` in the diff. That's a NOT_VERIFIED-ish item but I can partially check.

Let me do:
1. read TA3-A smoke-K01.json (find region_count 15 and source_sha256).
2. grep the diff for trailing whitespace in added lines: pattern `^\+.*[ \t]$`.

Also check the diagnosis claim "TA3-A verification/M2-TA3-A/summaries/smoke-K01.json, detector=doctr-fast_base-pinned, region_count=15, source_sha256=600ca755…".

Let me find the file.
dsh: reasoning:
The TA3-A smoke-K01.json path referenced by diagnosis.md §2.2 says `verification/M2-TA3-A/summaries/smoke-K01.json` — I used the wrong path (missing `summaries/`). Let me retry.

Also no trailing whitespace added lines → supports diff --check clean claim.

Let me retry the TA3-A file.
dsh: reasoning:
Confirmed: smoke-K01.json region_count=15, detector=doctr-fast_base-pinned, source_sha256=600ca755… matches K01. Good — the cross-reference is accurate (though the diagnosis cites path `verification/M2-TA3-A/summaries/smoke-K01.json` — correct).

Note: docTR region boxes are large (618×619, 654×740 etc.) — these look like *block*-level regions (much larger than text lines), not text-line level. Hmm. The diagnosis claims "docTR fast_base 输出文本行级候选（15）vs ogkalu 块级 193". But TA3-A's docTR region_count=15 with box sizes 618×619, 654×740, 376×437... For a 690-wide webtoon page, a 618×619 box is a big region — that's a bloc/paragraph-level region. So the claim "docTR 行级 vs ogkalu 块级" may be reversed or at least inaccurate. Actually in TA3-A, docTR runs detect then the same `cluster_words_into_blocks` merge is applied (docTR adapter uses the frozen merge). So region_count=15 is the merged block count for docTR. And the ogkalu tile experiment's 193 is pre-merge text boxes. So the doc's comparison "193 vs docTR 15：粒度不同" mixes pre-merge text boxes (193) against post-merge blocks (15). That's a real apples-to-oranges error in the diagnosis §2.3 judgment. Let me verify: does TA3-A smoke-K01's region output come from the merged blocks? The sizes 618×619 suggest merged blocks (or the docTR detect returns paragraph-level boxes natively). Let me look at the smoke-K01.json region entries to see if there's a "provider_label"/word count.

Actually, for the purposes of this review, the key finding is: diagnosis §2.3's "docTR 文本行级（15）vs ogkalu 气泡/文本块级（块级 193）" is not supported by the cited evidence — the cited 15 regions are ~600×600px blocks on the same page, and ogkalu's 193 is pre-merge text boxes. Comparing 193 pre-merge against 15 post-merge is exactly the granularity mismatch the doc warns about, but attributes wrongly. It's a P3 (documentation/precision) finding, since the doc does conclude "产品取舍留给修复 Task" — direction is fine, wording is not.

Hmm, but wait. Let me check whether doctr's 15 is post-merge. Let me read smoke-K01.json around lines 20-60 to see structure.

Let me read that.
dsh: reasoning:
TA3-A region_count=15, region_runs=15, detect="production-doctr". These are the production detection regions (post-adapter, i.e., after the same `cluster_words_into_blocks` merge). The region boxes at lines 120-285 are the region candidates with width/height ~600×600. So yes: docTR's 15 = production regions (post-merge blocks), ogkalu's 193 = pre-merge text-class boxes after NMS. This is a granularity mismatch in the diagnosis's comparison table.

Hmm — is that right though? `cluster_words_into_blocks` merges word boxes into blocks. For docTR, the "words" are line-level boxes and blocks are merged groups. For the K01 page, 15 blocks each ~600×600px — plausible: webtoon panels contain speech bubbles; docTR may produce line boxes that merge into 15 blocks. Actually 618×619 for a 690-wide page = nearly full width and 619 tall — that seems more like a "panel" than a text block. Hmm, but whatever, they're production regions.

So the diagnosis statement "docTR fast_base 输出文本行级候选（15）" is inaccurate: TA3-A's 15 is the production *region* count after the same merge pipeline (the smoke summary's `detect.region_count`), not raw text lines. I should flag this as a P3 with evidence (smoke-K01.json:43, and the region box sizes 618×619/654×740 at :125-126/:147-148).

Actually hold on. Let me be careful about the claim "docTR 行级". The docTR adapter (`detection_doctr.py`) detects word-level boxes with docTR's detection model, then clusters into blocks. docTR's detector output is word/line-level. The 15 is post-cluster. So both the "line level" and the count 15 refer to different stages. The doc conflates: "docTR 文本行级（15）" — 15 is not line-level count. If ogkalu tiling were run through the production merge, its block count would be comparable. So the honest comparison needs ogkalu-post-merge vs docTR-post-merge. The diagnosis explicitly defers the product tradeoff to the fix Task but states the granularity difference as established fact based on a mismatched comparison. P3.

Now, let me consider one more angle on the root cause: is there an alternative explanation that the full-page 0 is caused by the *aspect ratio* rather than *scale*? The tile experiment changes scale (1.6× vs 97×) but keeps aspect (square padded tile). A control that would separate "aspect ratio" from "scale" is missing, but for the fix design it doesn't matter much (both A and any fix address the long strip). Also the C rejection (bigger size) is relevant: a 1280 target still gives 49×. Fine.

Another consideration: the probe's tile experiment uses `processor(images=tile_rgb)` where tile_rgb is a 1024×1024 uint8 array. The image processor with size 640×640 rescales. Same as production. Good.

Now, is the probe's use of `provider._engine_or_raise()` (private method) an issue? It's an experiment, acceptable. It also constructs the provider with the same args. Good. Minor: it uses a private API, which could drift; documented as AC1 "生产 provider 逐字节同构造". Fine.

Another check: `production_detect` passes `DetectionRequest(page_id=..., image_bytes=..., width, height)` — check the DetectionRequest signature requires those fields and maybe more. The provider validates `len(image_bytes) in (expected*3, expected*4)`. The probe passes rgb24 (HxWx3 uint8 → tobytes), so expected*3 → OK. Good.

But hmm: `provider_detect` for K01 elapsed 574ms lower than tile total 19793/70=283ms. Consistent.

Now potential issue: the probe never runs the full-page path *after* tiling to compare, fine.

Next: "原生 pad 值 114" — arbitrary constant, no citation. Minor (P4).

Also: "TILE_SIZE 1024" chosen because... doc says "1024×1024 块" per task AC2 (task doc specifies 1024×1024 — yes: "用 K01 裁切成 1024×1024 块实测"), so tile size is task-mandated. The overlap 128 is at the experimenter's choice with the claimed 10–20% band not in the task. So the documented provenance for 128 is partly unsupported. Also, actually the task says "1024×1024 块" but the page width is 690 — so tiles are 1024 tall with width padded to 1024. Fine.

One more: the experiment's NMS is described as "页级 NMS" in 方案 A. The probe's greedy NMS is O(n²) — fine for 226 boxes.

Now let me double check the "y 覆盖全页 156.7–62008.9" — claim: y_range [156.7, 62008.9] and page height 62133. The last tile is 61824-62133 containing content 309 tall. Detection at 62008.9 → near the bottom. Good. But note: the y_range is the *box top* (b[1]) of boxes — coverage claim is about detection presence across the page, not full coverage of every band. Fine but the doc's "y 覆盖全页" means detections exist near top and bottom. OK.

Now the min conf 0.5009 issue. Let me examine: which tile contains the 0.5009? Tile 19 (origin 17024) has 18 confidences including 0.5009, and tile 17 has 0.5013. So low-confidence boxes cluster in tiles 17 and 19 (y ≈ 15232 and 17024). Also tile 69 (last, 309px tall) has 0.5356. These are near-threshold. In the deduped set min = 0.5009.

Interesting: since the tile experiment's threshold is the production 0.5 applied *per tile*, low-contrast content that in full page would be <0.5 gets boosted. Fine.

Question raised in the brief: "块级 conf min 0.5009 贴阈——分布是否健康". The deduped mean 0.8503 and max 0.9666 with min 0.5009 — the mean is healthy but the presence of exactly-at-threshold boxes means the count 193 is threshold-sensitive: a small threshold change could swing the count substantially. The doc doesn't provide a sensitivity check (e.g., counts at 0.3/0.1 within tiles) or a per-tile confidence histogram. Worth a P3 finding: report the distribution more fully (e.g., how many of the 193 are <0.6) so the fix Task knows the count is threshold-sensitive; the tile 19 burst of 18 boxes at 0.50–0.84 is consistent with a text-dense panel but not verified.

Let me count how many of the 193 deduped are below 0.6 — can I? The per-tile confidences sum to 226, and I have partial data. Too heavy to enumerate all 70 tiles. I could note from visible data: tiles 17 (0.5013, 0.5231), 19 (11 boxes ≤0.59), 13 (0.5662), 15 (0.5526), 69 (0.5356) — at least ~14 boxes below 0.6 in a subset. That's enough to say "a nontrivial fraction sits near threshold".

Hmm, I realize I should double check the claim "70/70 块有检出" is presented as evidence of健康, which the brief suspects could be "处处有框" false positives. Counter-evidence: BJ02 on a normal page produced only 10 boxes ≥0.5 out of 300 queries across the whole page → the model is not promiscuous. But the tiles are 1024² input while BJ02's whole page (2946×4167) went to 640². If the model becomes promiscuous at low compression, BJ02 at 640² isn't the right control. A better control would be tiling BJ02 too (its tiles would be 1024² at ~3× less compression than full-page). Not done. Also, the pad-only region produced 0 detections which is a partial control. So: 70/70 with high confidences is unlikely to be pure hallucination, but no per-block false-positive control was run — the doc acknowledges no GT. I'll note it as a residual uncertainty (already partially disclosed) and recommend the fix Task's qualification include precision measurement (the doc does defer precision to the fix Task). So maybe not a finding, or a P3 with the concrete suggestion of a "blank/pad-only tile" negative control which is cheap.

Actually, the pad-only control IS effectively there: 0 dropped in pad. But no tile that is *entirely* pad was tested; for full tiles the pad band is 334px wide (690-1024) and the model produced zero boxes whose center was in it, meaning it produced zero boxes in a 334×1024 gray region per tile. That's 70 × ~0.33MPixel of blank area with zero false positives. Decent negative control actually. I should credit that. But it doesn't cover "text-like texture" false positives.

Now let me also consider the docs' claim in §2.4 "provider 后处理过滤丢框 | 官方 post_process 在阈值处本就为 0，无可过滤之物" — valid.

"RT-DETR query 容量不足（300 query）| BJ02 仅用 10 个 query 即饱和；K01 塌陷分数分布在 143 个 query 上" — the K01 argument: 143 queries ≥0.01 means the model distributed mass over many queries rather than being capped. Reasonable.

Now let me consider the "conf 阈值过高" exclusion: "webtoon 三页 raw max 0.167–0.284，降到 0.3 仍为 0 检出；且低分是重缩放伪影而非真目标". The second clause "低分是重缩放伪影而非真目标" is an interpretation, supported by the tile experiment (same content yields >0.9 boxes). Fine.

Now let me assess scope discipline in more depth:
- 5 files, all in allowed paths: experiments/M2-DETECT-WEBTOON-DIAG/**, verification/M2-DETECT-WEBTOON-DIAG/**, doc/tasks/M2-DETECT-WEBTOON-DIAG.md, doc/handoffs/M2-DETECT-WEBTOON-DIAG-*.md. ✓
- No src/tests/requirements/packaging/apps/contracts, no experiments/M2-TA3-A|B modified (only read), no doc/STATUS.md. ✓ Verified by the diff file list (5 diff --git entries). No binary. ✓
- probe-results.json size: 1626 lines. Let me estimate the byte size. I could read the file's... no shell. Rough: average line ~30 chars → ~50KB. The largest content is tile confidences and 40 sample boxes. Acceptable for a verification artifact. Full 226 boxes would be ~226×5 numbers ≈ maybe 10KB more. So the "not storing all boxes" isn't about size — it's a reproducibility gap. Good framing: storing all 226 pre-NMS boxes (or the deduped 193) would cost only a few KB, so the omission is not justified by size. That strengthens the P3 into an actionable fix.

Let me quantify: 193 boxes × 5 floats × ~8 chars ≈ 8KB. So yes, cheap. Good finding.

- Is probe-results.json "大体积数据入库"? ~50-60KB, fine.

Now the documentation quality item:
- diagnosis.md chain: 判定 → 证据 → 排除 → 修法 → 局限 → 索引. Independent verifiable? Mostly: it cites JSON keys and code lines. I verified: preprocessor config values, model_input_shape, logits shape, score values, counts, BJ02 numbers, tile numbers, docTR 15, sha256 pins match source. Good.
- Inaccuracies found: (a) "任务书 10–20% 带内" provenance; (b) "docTR 文本行级（15）" granularity mismatch; (c) "counts_ge 0.0=300 证明 query 全部有非零分数" tautology; (d) "手工与官方后处理交叉一致（四页全部相等）" — 3/4 trivial; (e) "0→193 检出" vs production candidate semantics (pre-merge); (f) "垂直压缩 ~97×" fine; (g) K19 included in the "ko 6 case" closure without noting it is a text-free page whose 0 candidates is *correct* behavior (per M2-TA3-B quality-report.md:52 and F1 note) — this is the most consequential one for the next Task's Gate.
- Limitations disclosed: n=3 pages, 1 tile page, CPU-only, no GT. Adequate, but missing: no BJ02 per-tile control, no threshold sensitivity, no repeat runs, and NMS effect not decomposed (dedup correctness unverified), and K19 not probed.

Now let me double-check (g): is the claim "K01/K02/K04/K05/K08/K19 六 case" attributed to the task doc, which itself inherited from TA3-B2 F1. The review brief also lists those six. So flagging it is appropriate as a finding on the deliverable's forward-looking Gate (handoff §交付物/§验证命令) and diagnosis §推荐排序. Severity: the handoff's "完成 Gate = ko F1 六 case 候选数 >0 且全链可用" would force an impossible/incorrect acceptance on K19 (which must legitimately return 0 and instead needs the F4 state-caliber fix). If the fix Task is released with that Gate, the Gate is unfalsifiable/failing by construction. That's a P1 for the *next task's definition* — but is it a finding against *this* deliverable? The deliverable is the diagnosis + recommendations. It states the Gate. I'd say P2 (correctness of the endorsed closure criterion), possibly P1. Given review severity norms in this repo (P0-P4, P1 = must fix before approval), I think this deserves P1: an incorrect closure criterion that would propagate to the next Task's Gate, and a misstatement of the root-cause scope ("六 case" all attributed to long-strip downscale while one of the six is a text-free page and two others (K05/K08) were never probed). Hmm, but the owner could argue the task brief itself said the six cases. Still, the owner is responsible for not propagating an incorrect Gate, and quality-report.md:52 is available evidence in-repo that K19's 0 is correct behavior. Also the owner claims the diagnosis covers "六 case" — the diagnosis never even reads K19's geometry (1200×1660) which is available in qual-K19.json. So P1 seems justified: "范围/验收口径错误".

Let me be careful: is it certain that K19 fails for a different reason? quality-report.md:52 says "该页所有语言 SVG 文本层为 0 元素=无字页，检出无候选是正确行为，但生产 step 状态为 failed/INVALID_INPUT——口径问题见 F4". So yes, K19 = 无字页. Its 0 candidates is correct. The F1 grouping (line 62) lumps it in, but with the caveat in line 52 and line 140. So a reviewer flagging "K19 必须 ≥1 候选" is right.

Note also: is K19 possibly a mislabeled case? K19 = kr_Pepper-and-Carrot E20P01, "unlabeled_or_absent". Yes, no text.

So Finding R-K19: P1.

Now, let me also consider whether the "六 case" claim undermines the root-cause conclusion. Not for K01/K02/K04/K05/K08 (five webtoon long strips) — though K05/K08 were never probed (only K01/K02/K04). The doc's limitation says "tile 实验仅 K01；K02/K04 仅整页探针" and "三页整页分数塌陷形态一致，外推可信". But it doesn't say K05/K08 were unprobed; the task's AC1 only asked for K01 + K02/K04 抽样. So it's within AC. Still, the diagnosis's implied coverage of the six-case F1 is broader than the evidence. Should be stated. I'll fold into the same finding or a separate P2: "F1 六 case 中 K05/K08 未做任何探针（无整页可观测值），但 §1/AC2 的判定以'三 webtoon 页'证据覆盖 F1 全量；建议在 diagnosis.md §4 明确 K05/K08 未采样的边界". Actually the diagnosis §1 says the ruling is based on 3 pages. And AC2 was satisfied. Hmm, but Handoff AC2 says "六 case" nowhere... The task doc background lists six. I'll make it a P3 documentation boundary note, combined with the K19 P1.

Wait — for K05/K08: do they actually fail with 0 candidates? quality-report table lines 46/48: K05 0 regions F1, K08 0 regions F1. And their sizes: not listed. K05/K08 are hf_cleaned_webtoon → long strips. Fine.

Let me now also check: is there any statement in the deliverable claiming K05/K08 were probed? Handoff line 44 says "明确未运行：K02/K04 的块级实验...". And the probe cases are K01/K02/K04/BJ02. The handoff doesn't claim K05/K08 were probed. The diagnosis §4 limitation says "K02/K04 仅整页探针". It doesn't mention K05/K08 at all in the limitation (they're part of the F1 six). So P3: list K05/K08 as never sampled.

Now performance claim: "生产 273ms/页先例" — verify? Probably from C4. Not in evidence reviewed. Mark NOT_VERIFIED (the number source). Also "CPU 秒级/页" vs measured 19.8s for the tallest page.

Also, the review brief asks: "方案 A 的「NMS IoU 0.5 实测有效」在哪些数据上测的" → Answer: only the K01 70-tile experiment, measuring 226→193; no per-band duplicate analysis, no ground truth, no comparison of kept/dropped boxes' correctness; the 193 count is not independently recomputable from the stored JSON (only 40 sample boxes + per-tile confidences). So "实测有效" is under-supported; it's "在单页单次实验中使计数下降 14.6%，但既未验证被删的是重复框、也未验证留下的无重复". Good finding (P2).

Also "CPU 秒级/页的性能估计依据" → 19793ms measured for K01 (70 tiles) → 283ms/tile; extrapolation is linear in tile count = ceil((H-1024)/896)+1. For K02 (18401) → 20 tiles → ~5.7s; K04 (28156) → 31 tiles → ~8.8s. The doc gives "秒级/页" and notes linear growth. Reasonable but the handoff Gate "performance 基线登记（CPU 秒级/页预期）" lacks a number/budget. P3.

Now let me consider the "拒绝" of 方案 C. The doc says "没有任何证据表明更大 size 能恢复". That's honest. But there's a subtlety: the doc also claims "远超 BJ02 正常检出的 6.5× 分布" implying a threshold. I'll note as P4/P3 — the exclusion of C is reasonable but presented with a comparison that isn't a dose-response; C is "not evidenced" rather than "excluded". The task doc delivery record says C "证据不支持，排除" — fine as "excluded for lack of evidence". Actually diagnosis §3-C says "判定：证据不支持，排除" — acceptable. The table row in the task doc says "C processor size 覆盖（排除：62133→1280 仍压 49×）" — that's a quantitative argument, OK. And "62查找"... The brief's claim "C=processor size 覆盖（排除：62133→1280 仍压 49×）" matches. Fine — mild P4 at most. Actually I'd keep it as a P3 note that the "6.5× 正常分布" is a single-point comparison without a dose-response, so the C exclusion should be worded as "无支持证据"（which the diagnosis body does）rather than the task doc's "排除". I'll fold into documentation.

Let me also verify one more numeric claim: "垂直压缩比 K04 44.0×" → 28156/640 = 43.99 ✓. "K02 28.8×" → 18401/640=28.75 ✓. "BJ02 6.5×" → 4167/640=6.51 ✓. Good.

Another verification: "三页整页分数塌陷形态一致" — K01 max 0.2045, K02 0.1666, K04 0.2835; counts_ge 0.3 = 0 for all; counts_ge 0.1 = 7/4/14. ✓

Also "K01 在 ≥0.01 有 143 个 query——模型看到了什么但远不构成检出". ✓ (K02 290, K04 298 — interesting: K02/K04 have nearly all 300 queries ≥0.01, yet max 0.167/0.284. That's a very flat distribution. The doc says "这是重缩放伪影的典型形态，而非输入 decode 崩溃（否则应为全零/异常）". Hmm — for K02, 290/300 queries ≥0.01 with max 0.167 is a flat, near-uniform distribution. Is that consistent with "model sees the content but scores collapse"? It could equally indicate the model is responding to a uniformly-degraded texture. Either way it's not decode failure. Fine.

Now let me also double check that the probe results were not re-run this round (timestamp 2026-10-01T11:43:32Z, and this round's commit is 2d6b7bf6). The claim "本轮未重跑探针、只补分析/文档" — I cannot verify git history without shell (NOT_VERIFIED). But: the implementation commit 2d6b7bf6 adds BOTH the script and the JSON. If the script and JSON are in the same commit, that's consistent with "the probe artifact was produced by the previous (circuit-broken) round and committed now". Whether the JSON was regenerated is not statically verifiable from the diff alone. Note as NOT_VERIFIED (integration side: check JSON mtime vs script mtime, or whether the working tree JSON hash matches the committed blob).

Hmm, actually there's one static signal: the JSON's `generated_at_utc` = 2026-10-01T11:43:32Z, and the task/handoff were written 2026-10-01. Fine.

Another potential static signal: the probe script's `probe_schema_version: 1` matches the writer. And the JSON structure matches the script exactly (keys: task, probe_schema_version, generated_at_utc, environment, weights, preprocessor_config, conf_threshold_production, case_selection_manifest, pages). ✓ Consistent — so the JSON was produced by (a version of) this script. Good check to credit.

One more: the script writes `case_selection_manifest` path from the worktree — matches JSON line 839 (`G:\CODEX\New Manga.worktrees\M2-DETECT-WEBTOON-DIAG-zcode\experiments\M2-TA3-B\case-selection.json`). ✓ So the JSON was produced from this worktree. But wait — the worktree existed before the branch commits? Sure, the worktree path is fixed. Also, the JSON's K01 source_path points to `G:\CODEX\New Manga\test_assets\...` (main checkout), consistent with `asset_location: main_checkout_suite` in the manifest. ✓

Now — an important consistency check for the "熔断前一轮产出" claim: the JSON's `weights.dir` = `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/...`. Fine.

Another check: probe `PROBE_CASES = ("K01","K02","K04","BJ02")` and the JSON has exactly those 4. ✓ Order in JSON: K01, K02, K04, BJ02 ✓.

Now the environment claim: "torch 2.14.0+cpu". Torch 2.14 doesn't exist in reality (as of my knowledge), but this is a fictional/self-consistent project; the JSON records it. Not a finding.

Let me now check whether there is any missing AC coverage: AC1 says record "送入 processor 的图像尺寸、processor 重缩放目标尺寸（preprocessor_config.json 的 size/shortest_edge）、模型 raw 输出（logits 形状/最大置信度/top-k 分数分布，含 conf<0.5 的低分检出数）、letterbox/resize 参数". The probe records: size_wh, model_input_shape, preprocessor_config (size/do_pad/pad_size/resample), score_max, top10, counts_ge {0.5,0.3,0.1,0.01,0.0}, official_post_process, class_wise. Missing: "shortest_edge" — the doc says "无 shortest_edge 字段（该 config 走显式 size 路径），探针已按原样记录". The probe's `keep` tuple doesn't include "shortest_edge", so if it existed it wouldn't be recorded — but the diagnosis asserts it's absent. Minor gap: the claim "无 shortest_edge" can't be verified from the JSON (the key was filtered out). It's verifiable only from the weights dir config file (not in repo, weights are gitignored). So this is a small evidence gap: assert absence of shortest_edge without recording it. Since `load_preprocessor_config` filters to a fixed key list, absence in the JSON doesn't prove absence in the file. P4 finding. Actually the diagnosis says "无 shortest_edge 字段（该 config 走显式 size 路径），探针已按原样记录" — "探针已按原样记录" is false for that specific key. Nice catch; P4.

Also AC1 says "top-k 分数分布" — recorded top10. ✓ "含 conf<0.5 的低分检出数" ✓.

AC3: three options compared with 改动面/风险/成本 ✓ (方案 A table, B, C).

AC4: zero src ✓.

Now, one more scope item: the task's 允许修改面 includes `doc/tasks/M2-DETECT-WEBTOON-DIAG.md` ✓ and handoff ✓.

Now let me formulate findings with file:line references.

Line references (current worktree files):
1. `doc/handoffs/M2-DETECT-WEBTOON-DIAG-2d6b7bf6.md:54` and `:61` — "ko 6 case（K01/K02/K04/K05/K08/K19）重跑 qualification" + "ko F1 六 case 候选数 >0 且全链可用" → K19 是无字页（`verification/M2-TA3-B/quality-report.md:52`、`:140`），0 候选是正确行为，其失败属 F4 口径问题；"候选数 >0" 对 K19 不可满足/错误。Also `doc/tasks/M2-DETECT-WEBTOON-DIAG.md:50` and `verification/M2-DETECT-WEBTOON-DIAG/diagnosis.md:115` repeat the six-case closure.

Let me get exact line numbers for the handoff. From the diff, handoff lines: line 54 = 交付物 (in the file, the diff added lines start at 1 for the handoff). The handoff file content: line 54 "- **交付物**：..." wait, the read of the worktree handoff would give exact numbers. The grep earlier showed `doc\handoffs\M2-DETECT-WEBTOON-DIAG-2d6b7bf6.md:54` = "- **交付物**：实现 + 单测（含跨块截断框、重叠带重复、极端长页）+ ko 6 case（...）+ Handoff." and `:61` = "验证命令、环境与完成 Gate". ✓ Good, grep gave line numbers.

2. `verification/M2-DETECT-WEBTOON-DIAG/diagnosis.md:71` and `:93` — "NMS IoU 0.5 实测有效（226→193）" — 未验证被删框是否为重复框；JSON 未存全量框，不可独立复算。Also probe-results.json only stores 40 of 193 deduped boxes (`probe-results.json:1088`) and no pre-NMS coordinates → 226→193 不可复算。P2.

3. `experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py:343-367` (`run_tile_inference`) — tile path skips `cluster_words_into_blocks`; production `detect` output = post-merge blocks (`src/infrastructure/providers/detection_manga.py:148-152`). Hence "0→193 检出/候选" is not in production output units; the doc's "候选" wording (`doc/tasks/M2-DETECT-WEBTOON-DIAG.md:45`, `diagnosis.md:58`(§1)) mixes levels. P2 (documentation precision + metric mismatch).

Wait, diagnosis.md §1 is at line... In the diff, diagnosis.md content lines: the file starts at diff line 644 as `# M2-...`. Let me map: diff line 644 = file line 1. So file line = diff line - 643. §1 judgment block starts diff 657 → file 14; "0 检出恢复到 193 个去重检出" diff 658 → file 15. §2.3 judgment bullets diff 710-714 → file 67-71. Let me verify with the grep result: grep found diagnosis.md line 71 = "NMS 去重比 226→193（-14.6%）..." and line 54 = the design sentence ("设计：K01 裁成 1024×1024 块、垂直重叠 128px（12.5%，落在任务书 10–20% 带内...）"). diff line 697 = §2.3 设计 → 697-643 = 54 ✓. And line 93 = 方案 A 风险 row ✓ (diff 736 → 93). Great, mapping confirmed: file_line = diff_line - 643.

So:
- §1 judgment: diagnosis.md:15.
- §2.2 table: diagnosis.md:37-42 (diff 680-685).
- §2.2 自洽性 point 2: diagnosis.md:47 (diff 690).
- §2.2 point 3: diagnosis.md:48 (diff 691).
- §2.3 design: diagnosis.md:54.
- §2.3 result table: diagnosis.md:57-64ish.
- §2.3 judgments: 69-71.
- §2.4: 73-81.
- §3 A: 86-93 (need exact).
- §3 B: 96-104.
- §3 C: 106-110.
- recommendation: 113-117.
- §4 limitations: 119-124.

Let me read the worktree diagnosis.md to get exact line numbers (it's 133 lines).

4. `diagnosis.md:54` — "落在任务书 10–20% 带内" — 任务书（`doc/tasks/M2-DETECT-WEBTOON-DIAG.md:26`）只规定 1024×1024，无重叠带宽；P4 provenance inaccuracy.

5. `diagnosis.md:69` (diff 712?) — "docTR fast_base 输出文本行级候选" vs `verification/M2-TA3-A/summaries/smoke-K01.json:43` region_count=15 = production 合并后的 region（TA3-A smoke 的 detect.region_count；box 尺寸 618×619/654×740 见 :125-126/:147-148）→ 粒度对比口径不一致。P3.

6. `diagnosis.md:47` — counts_ge["0.0"]=300 作为"query 全部有非零分数"的证据是恒真（sigmoid ≥ 0）；非平凡证据是 counts_ge["0.01"]=143。P4.

7. `diagnosis.md:48` — "四页交叉一致（webtoon 页 0=0，BJ02 10=10）"：3/4 为 0=0 平凡相等，建议只在非零阈值（如 0.1）做交叉核对。P4.

8. Probe 未记录 shortest_edge（`diagnose_webtoon_detect.py:468-481` keep 列表），但 `diagnosis.md:26`(?) 断言"无 shortest_edge 字段，探针已按原样记录"。Let me locate: diff 673 = "即任何输入都被无保比例地压到 640×640。无 shortest_edge 字段..." → file line 30. Let me verify: diff 673 - 643 = 30. Yes diagnosis.md:30. But wait, line 27-29 is the table, line 30 is the sentence. I'll verify by reading.

9. Performance: "生产 273ms/页先例" (`diagnosis.md:93`) — not in the reviewed evidence (JSON shows K01 provider 574ms / infer 297ms; BJ02 333ms). Source not cited → NOT_VERIFIED + P4 (cite the C4 artifact).

10. Per-block negative control / 70/70: suggest "纯 pad/空白块"对照 + BJ02 同切法对照。P3 (directional limitation partially disclosed). Reference `diagnosis.md:64`(70/70) and §4.

Hmm, the brief asks specifically: "70/70 块全有检出是否可能是重缩放后小图「处处有框」的假阳性（BJ02 对照的 per-block 行为是否验证过？...）". Answer: BJ02 per-block control not run; but pad-band zero-FP + BJ02 full-page 10/300 boxes are partial counter-evidence. Also each tile is 1024² (not small), and content is downscaled 1.6×. The 70/70 claim is verifiable in JSON (no tile with 0). I'll present it as a P3 recommendation.

11. Threshold sensitivity: min conf 0.5009 at `probe-results.json:932`; tile 19 has 11 of 18 boxes in [0.5009,0.59] (`probe-results.json:1196-1214`) → count 193 is threshold-sensitive and a per-tile histogram/sensitivity run isn't provided. P3. Actually is that "11 of 18 below 0.6"? Tile 19 confs: 0.8399, 0.7247, 0.7139, 0.6892, 0.6783, 0.6574, 0.6408, 0.5903, 0.5807, 0.5804, 0.5732, 0.5485, 0.5458, 0.5442, 0.5337, 0.5199, 0.5186, 0.5009 → below 0.6: 0.5903, 0.5807, 0.5804, 0.5732, 0.5485, 0.5458, 0.5442, 0.5337, 0.5199, 0.5186, 0.5009 = 11 of 18. ✓ Good, I can cite that.

Note: these confidences are `mapped` (post-class-filter, pre-NMS). The deduped ones may differ. Careful phrasing: tile 19 mapped 18 boxes, 11 below 0.6.

12. `probe-results.json` 未存全量框 → 复算缺口（与 #2 合并）。Also mention size ~50KB so size isn't a constraint. Let me get actual file size... I can't. I'll phrase "约 1,626 行" instead of bytes.

Actually, I could estimate: 193 boxes * 5 numbers in the pretty-printed style used for the 40-box sample = each box takes 7 lines in the sample (e.g., "[\n 184.6,\n ... \n]"). The 40-box sample spans lines 1088-1371 = 284 lines → ~7 lines/box. 193 boxes would be ~1,350 lines ≈ doubling the file. Hmm, that's substantial but still ~100KB. I'll say "全量 193 框按现有紧凑一格一框的写法约 +1,300 行/≈60KB" — maybe too speculative. Better: "按去重样例的缩进格式，193 框全量约需 +1.3k 行；若改用每框一行的数组则可控制在 ~200 行内" — that gives the actionable fix. Good.

Hmm, let me get the actual byte size using... the read tool returns content but not size. glob doesn't give size either. I'll avoid byte claims.

Now, an important question: should the verdict be approved_with_conditions or changes_requested? The P1 (K19 Gate) is a documentation/criteria fix, not needing new experiments. Given the repo's review conventions (P1 usually → changes_requested unless minor), but the fix is a one-line doc correction that the integrator could also handle... The review brief expects a verdict. The core diagnosis (root cause, evidence, exclusion chain) is sound and independently verified on the key numbers. The issues are: one consequential Gate/criteria error (P1), one metric-level conflation (P2), one reproducibility gap (P2), plus P3/P4 documentation precision items. Since a P1 exists affecting a downstream Task's release Gate, I'll go with **changes_requested** — but with an explicit note that the changes are documentation/criteria-only (no re-run of the probe needed) and that the core ruling is accepted. Hmm. Let me weigh: "approved_with_conditions" would be appropriate if conditions were minor and the artifact could be merged as-is. Here the handoff/task text must be edited before it's used to release the fix Task (otherwise Codex releases a broken Gate). Since the deliverable includes that Gate text, changes are requested. I'll say changes_requested with a clear scope: 3 doc edits (P1 + 2×P2), no code/probe changes.

Actually, let me reconsider the P1 severity. Is "候选数 >0" for K19 really going to be enforced? The handoff §"下一任务建议" is a proposal to Codex; Codex will draft the Task. The risk is real but the owner's text explicitly flags it as "候选 Task（待 Codex 释放）". A reviewer flagging it as P1 is defensible; but P1 convention might be "blocks approval of the claim". The claim "ko 6 case 全由整页重缩放致 0 候选" is factually wrong for K19 and would mislead. I'll call it P1 and explain. Fine.

Also, should I raise that 5 of the 6 F1 cases were not all probed? K05/K08 unprobed: it's within AC (AC1 asked K01 + K02/K04 抽样), and the doc's limitations say K02/K04 only full-page. I'll make it a P3 (add K05/K08 to the limitation; the "六 case" scope statement in the task record implies coverage that doesn't exist).

Hmm, wait. Let me re-read the task AC2: "若整页重缩放成立，用 K01 裁切成 1024×1024 块实测 ogkalu 检出能力". So AC2 explicitly only requires K01 for the tile experiment, and AC1 requires K01 (及 K02/K04 抽样) for the probe. So the deliverable meets its AC. The issue is only the forward-looking six-case claim and diagnosis's scope language. Good — so the AC coverage is complete. I should say that in the table.

Let me now check the diagnosis.md line numbers precisely by reading the worktree file.

Also I should double check `diagnosis.md` §2.4 line for "BJ02 仅用 10 个 query 即饱和" and "K01 塌陷分数分布在 143 个 query 上".

Let me read diagnosis.md fully (133 lines).
dsh: reasoning:
Now I have exact line numbers. Let me also double-check the handoff file's exact lines around the key claims (I have grep line numbers 54, 61-62). Let me read the handoff to get precise line numbers for the Gate and to verify the diff content matches the worktree (it should).

Actually I read the handoff via the diff already (lines 1-85 of the diff = handoff content lines 1-78ish). The file has 78 lines? The diff header said `@@ -0,0 +1,78 @@` but the content I saw went to line 84 of the diff → let me not worry. The grep gave: line 54 = 交付物, line 61 = 验证命令..., line 62 = 可直接转发指令, line 68 = 风险... Let me verify by reading the worktree handoff file lines 45-70.

Also I should double check whether the worktree files match the diff (working tree clean claim). Let me spot check: diagnosis.md in worktree line 15 says "0 检出恢复到 193 个去重检出" — diff line 658 same ✓. Line 54 same ✓. So consistent.

One more check: the handoff's front-matter `delivery_head: 2d6b7bf6` and the diff contains the handoff as a new file → the handoff was added in b311f52f (docs commit), consistent.

Now let me read the handoff worktree lines 44-70 for exact citations.
dsh: reasoning:
Now I have precise line numbers. Let me also verify the STATUS/authorization aspect: the task front-matter `approval: user_ruling_2026-10-01_all_four` and STATUS says "等用户三项裁决" — the task claims approval "全部进行". I can't verify the user ruling from the repo; the task doc records it. NOT_VERIFIED (authorization provenance) — but low priority; the orchestrator's brief states the task was released. Fine.

One more possible scope issue: the task doc modified `status: ready → in_review` and appended 交付记录; the 允许修改面 includes the task doc. ✓

Now, let me also check whether the probe script has any issue with `--output` writing into the repo (it writes to verification/... by default) — fine.

Potential code-quality findings on the probe script (AC1 evidence quality):
- `raw_observability` doesn't record whether logits contain NaN/inf explicitly (though score_max would be nan). Minor.
- `counts_ge["0.0"]` trivial (already noted).
- The full-page path runs BOTH `provider.detect` and `raw_observability` (duplicate inference) — that's why elapsed differs (574 vs 297). Fine, documented.
- `greedy_nms` doesn't handle the case where two boxes of different classes overlap — NMS is class-agnostic. Since production merge is also class-agnostic (both text classes merged), fine. Actually text_bubble (1) and text_free (2) boxes for the same text could overlap and be deduped — which is arguably correct.
- No `torch.manual_seed` needed (deterministic eval).
- The tile experiment's timing includes NMS and mapping (as documented).
- The script's class-wise stats use the argmax label per query, which means a query whose bubble score is 0.6 and text score 0.65 counts only as text. For the "class_wise" counts this undercounts bubble. For BJ02 that yields bubble=5/text=5, and the official post_process gave 10 boxes; the provider counted bubble_class_dropped=5. So class_wise matches the official. ✓ Actually does the official post_process use argmax too? RT-DETR post_process typically takes max over classes. So consistent.

Now, a deeper check on the claim "整页重缩放致目标消失" vs the tile experiment: the tile experiment's compression is 1.6×. So the causal variable is resolution. The doc claims "压缩 1.6×，与模型训练分布相称" — plausible.

But here's a subtlety worth raising: the fix Task will use tiles of 1024²; the model's preprocessor resizes them to 640² — 1.6×. Yet the full-page path also resizes to 640². The difference is that in the tile case, the model receives ~1/70 of the page content at 640². So the effective *content* resolution is what matters. The doc's framing "仅改输入空间分辨率" is right.

Alternative fix D not considered: pass the page in multiple crops *without* padding (width 690 → resize to 640 keeping full tile height?) — irrelevant.

Another alternative not considered: since the width is 690 and the model wants 640, a per-band approach with size override (e.g., size={"height": 640, "width": 640} but crop bands of 690×~618) would give ~1.08× horizontal and 1× vertical. That's basically方案 A but with band height = 618. Not a distinct option. Fine.

Should the diagnosis have considered that the tile experiment also implicitly changes the *aspect ratio* to square (padded) while the full page is 1:90? Yes — the "唯一变量是输入的空间分辨率" claim is not exactly right: the tile experiment changes BOTH the amount of content per inference (1.6× downscale vs 97×) AND the aspect ratio of the input (square vs 1:90). So strictly, the experiment doesn't isolate "resolution" from "aspect ratio". However, padding preserves content aspect ratio within the tile, so the model sees content at 1.6× with correct proportions; while the full page sees content at 1.078× horizontal and 97× vertical — i.e., the aspect distortion is a *consequence* of the same anisotropic resize. So "resolution" and "anisotropy" are both changed by the intervention. Since the proposed fix (tiling + padding) addresses both, that's fine for the fix, but the claim "唯一变量是输入的空间分辨率" is imprecise — anisotropy is co-varied. It matters only for choosing among C-like fixes (a size override to e.g. 640×1280 would still distort). Since C is rejected anyway, the practical impact is nil. I'll note as P3 with a wording correction: "唯一被改变的变量是送入单次推理的像素预算（含由此消除的各向异性）" — precise.

Good finding for review item 2 ("根因排除链... 逻辑完整性").

Let me also double check whether the padding gray 114 could bias the model since image_mean normalization... `do_normalize: false` in the preprocessor config! The config says `do_normalize: false` while image_mean/std exist. So the model receives un-normalized [0,1] rescaled values. Interesting but not our concern. Note: the tile pad value 114/255 = 0.447. Fine.

Hmm wait, `do_normalize: false` is unusual for RT-DETR (normally true). The diagnosis doesn't mention it. Not needed.

Now let me think about whether the pad-value 114 choice interacts: the pad is a constant gray; if the model was trained with letterbox padding, 114 is standard. Fine, it's labeled "common detection padding value" without citation. P4 at most; I'll fold into the "参数依据" note.

Now let's think about whether there's any P0. I don't think so: no src changes, evidence chain sound, numbers check out.

Let me also consider one thing in review item 4: "probe-results.json 是否含大体积数据（块坐标全量入库是否合理）". Answer: JSON contains per-tile confidences (226 mapped boxes' scores) but NOT their coordinates; only 40 sample boxes. So it's actually *less* than full-fidelity. Size is small (1,626 lines). The "块坐标全量入库" premise in the brief is incorrect — worth stating explicitly. And the converse issue (missing coordinates) is the finding.

Also: does the JSON store absolute paths of user assets (noncommercial_research_source_restricted)? It stores local absolute paths (`G:\CODEX\New Manga\test_assets\...`). That's consistent with existing evidence files (e.g., TA3-B case-selection stores absolute paths). No secret. Fine.

Let me also confirm "无 __pycache__ 入库" — the diff has 5 files, none is __pycache__ ✓. And no binary ✓ (grep found no "Binary files").

Now let me think about which findings to list and severity:

R1 [P1] 六 case 关闭口径把 K19 当成重缩放缺口 → 错误 Gate「候选数 >0」。Files: doc/handoffs/...:54, :55; diagnosis.md:115; doc/tasks/...:50. Evidence: verification/M2-TA3-B/quality-report.md:52,:62,:140. Recommendation: 把 K19 从 tiling Gate 中剥离，改为 F4 口径项（无字页应空成功、step 不得 failed）；tiling Gate 只覆盖 5 张 webtoon 长条漫。

R2 [P2] 193 与 0 不在同一计量层级（pre-merge 文本类框 vs provider region/块），tile 实验跳过 `cluster_words_into_blocks`（probe:343-367 vs src:148-152）；诊断/任务书把 193 称作"检出/候选"。Files: diagnose_webtoon_detect.py:343-367, detection_manga.py:148-152, diagnosis.md:15/:69, doc/tasks:45.

R3 [P2] "NMS IoU 0.5 实测有效" 无去重正确性证据、且 226→193 不可独立复算（JSON 只存 40/193 框、无 pre-NMS 坐标）。Files: diagnosis.md:71,:93; probe-results.json:1088; diagnose_webtoon_detect.py:440-463.

R4 [P3] docTR 15 的粒度表述错：15 = TA3-A 生产 region（合并后），非行级；与 193（pre-merge）不可比。Files: diagnosis.md:70,:104; handoff:63; evidence smoke-K01.json:43,:125-126.

R5 [P3] "任务书 10–20% 带内" 无出处（任务书只规定 1024×1024）；128px/12.5% 与 pad=114 缺依据引用。Files: diagnosis.md:54; doc/tasks:26. (P4 maybe; but provenance claims should be accurate → P3? I'd say P4 for the pad value, P3 for the misattribution.) Let me merge: R5 [P3] 参数依据的两处出处不准（10–20% 带、pad 114）。

R6 [P3] "唯一变量是输入的空间分辨率" 不精确：tile 实验同时改变了内容像素预算与输入宽高比（各向异性），两者共变；对 A 无害，但对排除 C 的论证有影响（C 的 size 覆盖仍带各向异性）。Files: diagnosis.md:69,:111.

R7 [P3] 70/70 全检出缺少 per-block 负对照（纯 pad/空白块、BJ02 同切法），且 193 的阈值敏感度未给（min 0.5009 贴阈；tile 19 的 18 框中 11 框 <0.6）。Files: diagnosis.md:63,:65; probe-results.json:932, 1196-1214.

R8 [P4] `counts_ge["0.0"]=300` 恒真，不能支撑"query 全部有非零分数"；后处理交叉核对 3/4 页为 0=0 平凡相等。Files: diagnosis.md:46,:47.

R9 [P4] `shortest_edge` 未进 keep 列表，JSON 无法证明其不存在，与 "探针已按原样记录" 不符。Files: diagnose_webtoon_detect.py:468-481; diagnosis.md:30.

R10 [P4] 性能baseline引用 "273ms/页先例" 无出处（本 JSON 内 K01 574ms/BJ02 333ms），handoff Gate "CPU 秒级/页预期" 无数字预算，而最坏实测 19.8s（34×）。Files: diagnosis.md:61,:93; handoff:55.

R11 [P3] 局限性未登记 K05/K08 未采样、BJ02 无 per-tile 对照、单次运行无方差。Files: diagnosis.md:121. Maybe merge with R7. I'll keep R11 as its own (scope boundary of the six-case F1). Actually R1 covers K19; R11 covers K05/K08 unprobed + "六 case" implication. Let me merge R11 into R1? R1 is about K19's Gate. R11 is about the diagnosis's coverage claim. Different fixes (one to the Gate, one to the limitations list). I'll keep both but make R11 P3.

That's 11 findings — reasonable. Maybe trim to keep signal high. Let me keep ~10.

Also for item 4 (范围纪律), everything checks out — state it clearly in the table, no findings.

NOT_VERIFIED (integration-side):
- 5 文件范围/无二进制/无 __pycache__：已由 review-input.diff 静态确认（5 个 diff --git、无 Binary）→ actually verified statically. So NOT: "git status --porcelain 干净"、"git diff --check EXIT=0"（静态检查新增行无行尾空白，但 EXIT=0 未运行）; "git show 2d6b7bf6 --stat 仅 4 文件"（at commit boundary; the diff shows 5 files over 8996ca55..tip）; "本轮未重跑探针"（需 mtime/git 证据）; 探针复跑可复现性（需 venv+权重+CPU ~1–2 分钟）; 193 的复算（需原始坐标，JSON 未存 → 更准确说不可复算，是 finding）; 生产 273ms/页先例来源; 三套件回归/单测（本 Task 无测试改动，无需）; K19 1200×1660 无字页的判读（我按 quality-report 复核，静态成立，但未跑 qual-K19 之外的东西）; 权重 sha256 与 pin 一致（JSON 自述 all_pins_match=true，我核对的是 detection_manga.py 里的 pin 值 vs JSON 中记录的 sha256 —— 这个我其实静态核对过了！Let me verify: JSON model.safetensors sha256 = 037930a8...; source MANGA_MODEL_SHA256 = 037930a861e67870eb345be01b28cc70d7e2b7956528e48ee0ebdb0c093df80d ✓. config.json b6d70793... vs MANGA_CONFIG_SHA256 b6d707933e12e9593a7025604be1c95add70a6db371fdd1532e8854e2256e072 ✓. preprocessor 7e9e2245... vs MANGA_PREPROCESSOR_SHA256 7e9e2245806aa3ef068a5321f5eebee3116fa4cec560173231954ffaca930eca ✓. So the pins match the source; whether the actual files on disk have those hashes requires running the probe → NOT_VERIFIED. Good, that's a nice distinction to record.

Let me double check those strings by eye:
JSON: "037930a861e67870eb345be01b28cc70d7e2b7956528e48ee0ebdb0c093df80d" vs source "037930a861e67870eb345be01b28cc70d7e2b7956528e48ee0ebdb0c093df80d" ✓
JSON: "b6d707933e12e9593a7025604be1c95add70a6db371fdd1532e8854e2256e072" vs "b6d707933e12e9593a7025604be1c95add70a6db371fdd1532e8854e2256e072" ✓
JSON: "7e9e2245806aa3ef068a5321f5eebee3116fa4cec560173231954ffaca930eca" vs "7e9e2245806aa3ef068a5321f5eebee3116fa4cec560173231954ffaca930eca" ✓ 

Also the K01 source_sha256 in JSON "600ca7551a186d05e8f6876e66c89e2c44a0ec99c0cc0e53694a67c7622be47b" vs case-selection.json:294 "600ca7551a186d05e8f6876e66c89e2c44a0ec99c0cc0e53694a67c7622be47b" ✓. K02: JSON "b1123355e8c451f99100b153679f126676f616c9715ea6e1cbdbfaeeb3134f50" vs manifest:314 same ✓. K04: "8bfad8af8e4f7ca594f8223d1b0fffbc916a8617a64baa1c381f078f0e4c1873" ✓. BJ02: "c1ce06205b8e64c1a199f1adbab3bdaa9aff46d67abc8283bd4ef28ea6dd5417" ✓.

Great — these static cross-checks I *did* verify. I should list them as verified, with the caveat that the actual file hashes are runtime.

Also the manifest's K01 layout_type = webtoon_long_strip ✓ matches JSON. BJ02 paged_manga ✓.

Integration closure checklist:
1. 更正 K19 口径（把 F1 tiling Gate 限为 5 张长条漫；K19 归 F4 无字页空成功口径）。
2. 释放修复 Task 时把验收改为 region/候选层级（跑生产 `provider.detect` 计数），并给出性能数字预算。
3. 让 Owner（或 Codex 集成时）补：全量框落盘（或至少 pre-NMS 坐标）使 226→193 可复算；docTR 15 的层级表述；10–20% 带出处；shortest_edge 记录。
4. STATUS 登记（Codex）。
5. Review 记录归档 doc/reviews/M2-DETECT-WEBTOON-DIAG-<head>-dsh-r1.md。

Recommended next step (one sentence): 以「文档/口径更正」而非重跑实验闭合 R1–R3，然后由 Codex 释放修复 Task（Gate 限 5 张 webtoon 长条漫 + 生产 region 层级计数 + 明确性能预算）。

Verdict: changes_requested.

Hmm, let me reconsider. The instruction says "非作者独立 Reviewer... round 1". The repository convention: P1 → changes_requested. I'll go changes_requested but emphasize the changes are doc-only and the core ruling is accepted.

Wait, one more consideration about R1 severity. Let me re-read handoff:55: "ko F1 六 case 候选数 >0 且全链可用". If Codex naively adopts this, K19 (no text) can never have >0 candidates unless the detector hallucinates. So the Gate would fail forever or force a bad fix. That's a genuine P1 in the *deliverable's proposal*. Yes.

Also let me double check that K19 is indeed among "F1 ko 6 case" and that the tiling fix wouldn't help. K19 is 1200×1660 paged_webcomic, aspect 1.38 — no downscale issue at all, and it's text-free. So even the root cause doesn't apply. Confirmed: `verification/M2-TA3-B/quality-report.md:52`.

Hmm, but is the brief's premise maybe that K19 也 fails but for the caliber reason, and the owner grouped it because TA3-B2 F1's count of 6 includes it. Whatever — my finding stands: the deliverable must distinguish.

Let me also quickly double-check one thing: the task doc line 21 background says "生产 detect（manga ogkalu RT-DETR-v2）对 webtoon 长条漫返回 0 候选（K01/K02/K04/K05/K08/K19 六 case）" — includes K19 as "webtoon 长条漫", which is wrong on two counts (it's paged_webcomic and text-free). But that line is the pre-existing task background (not added by this delivery — the diff only changed status line and appended 交付记录). So the *background* line is inherited, not the owner's error. But the owner's appended line 50 and handoff repeat the six-case closure. And diagnosis.md:115 too. OK, keep P1 but scope it to the new text.

Also check: handoff:48 "关闭 TA3-B2 F1（ko 6 case 0 候选）" — same issue.

Now let me write the final review. Format requested: 
## Verdict
## 逐项核对表（A 根因证据链 / B 块级方法学 / C 修法建议 / D 范围纪律 / E 文档质量）
## Findings（R1…，P0-P4，文件:行）
## NOT_VERIFIED（集成方运行时项）
## 集成方闭合清单
## 推荐下一步（一句）

The table should cover the five areas. I'll also answer the reviewer's specific questions within the table/findings.

Let me make sure the verdict language is Chinese, per global instructions. Yes — output in 简体中文, keeping code/paths in English.

Let me now write out the numbers I verified:
- source pins match JSON-recorded sha256 (3 files) — static ✓
- 4 pages' sha256 vs manifest ✓
- K01 690×62133 → 640×640 = 97.1× ✓ (62133/640=97.08)
- K02 600×18401 → 28.8× ✓
- K04 690×28156 → 44.0× ✓
- BJ02 2946×4167 → 6.5× ✓
- max scores 0.2045/0.1666/0.2835/0.9721 ✓
- counts_ge 0.5 = 0/0/0/10; ≥0.3 = 0/0/0/10; ≥0.1 = 7/4/14/14 ✓
- official_post_process = 0/0/0/10 == manual ✓ (but 3 trivial)
- logits [1,300,3], model_input [1,3,640,640] for all four ✓
- preprocessor_config do_pad=false, pad_size=null, size 640×640, do_normalize=false ✓
- tiles 70, last crop_h 309, origins step 896 ✓ (0, 896, ..., 61824)
- total_raw 226 = total_mapped 226, deduped 193 ✓ (JSON fields; sum not independently recomputed — 不能复算，标注)
- 70/70 tiles ≥1 (no n_boxes_raw 0) ✓
- per-tile max 18 (tile 19), min 1 (tile 13) ✓
- elapsed 19793ms → 282.8ms/tile ✓
- deduped conf max 0.9666/mean 0.8503/min 0.5009 ✓
- sample geometry 40 boxes stored ✓
- docTR 15 = smoke-K01.json:43 (production region count) ✓ sha256 match ✓
- K19 = 1200×1660 无字页 (quality-report:52) ✓
- diff = 5 files, all allowed paths, no binary, no trailing whitespace added ✓

One caveat: 226 = sum of per-tile n_boxes_raw — I verified no zero tile and that field exists per tile, but I did not sum 70 values. State it as "未逐块求和复算（无可执行环境）" → NOT_VERIFIED. Good honesty.

Also "193 去重" — not recomputable → finding + NOT_VERIFIED.

Let me write it now. Keep it organized and reasonably concise but complete. I'll write findings with 证据/影响/建议.

For the "逐项核对表", I'll use a markdown table with columns 审查项 | 结论 | 依据.

Let me draft.

Also mention: 未发现 P0；核心判定（整页重缩放）经我的静态复核接受，且我的判断是：验证该判定的决定性证据是 **K01 页内干预（同一页、同权重、同阈值、仅改单次推理的像素预算）**，不是 BJ02/docTR 跨页对照——008 diagnosis.md §2.3 的论证链依赖块级实验闭环，这一点逻辑上是成立的；§2.2 的 BJ02/docTR 只用于排除探针/管线伪影（不同假设），不构成"webtoon 域风格差异"混淆变量的排除。也就是说：BJ02（日漫 paged_manga、JA）与 webtoon（韩漫长条、KO）跨域跨版面，确实无法单独排除"域风格"解释；但 K01 的页内干预把域/内容/权重全部固定，因此混淆变量在 §2.3 被消掉。这是我对审查项 2 的结论。

Wait — careful. Does the page-internal intervention fully exclude "domain style"? Yes: the same page content, same model, only input geometry changed, and signal appears. So the residual "domain" hypothesis cannot explain a 0→193 flip. Good. But one could argue the model responds to *something* in tiles that it doesn't in the full page even if it can't recognize Korean text (e.g., it detects generic text-like textures when at proper scale). That's still "resolution is the switch" — the root-cause claim (input geometry) holds; the "193 are true text" claim is separate and disclaimed. Good.

Also answer: "同页 docTR 15 候选是关键证据吗——docTR 与 ogkalu 是不同模型，同页对比能否直接归因分辨率？" Answer: no, it can't; it only shows the page has detectable text and that the 0 is backend-specific (which TA3-B2 r1 R1 already established). The owner's chain does rely on the tile experiment to close, which is correct methodology. But §2.2 line 50 lists the docTR comparison under "证据链" without that caveat, and §2.3 line 70/§3-B line 104 mis-states its granularity. So the logic is complete but the presentation should tag the docTR comparison as background (it does say "背景证据，非本任务产出" at line 50 — good, it's tagged). So the owner did tag it. I should credit that. Then R4 is purely about the granularity wording.

OK. Also for review item 1: "1024²/重叠 128px 的切法是否有依据（模型输入尺寸对齐？）" — 1024 是任务书指定；128 = 12.5% = stride 32 的 4 倍；与模型输入 640 无关（640/1.6=400... ) hmm, is 1024 aligned to the model input 640? 1024/640 = 1.6 — not an integer. So the tile size is NOT aligned to the model input size; it's aligned to stride 32 (1024 = 32×32). Worth noting: a 640-aligned tile (e.g., 640 or 1280) would give 1.0×/2.0× scale and avoid resampling. The chosen 1024 forces a 1.6× resample of every tile. Not wrong (compression 1.6× is mild and near the training distribution), but the doc's phrase "与模型训练分布相称" is an assertion without evidence, and the alternative of using the processor's native 640 band (band height 640 → 1.0×, no resample) wasn't evaluated. That's a decent P3 design note for the fix Task: consider 640-tall bands (zero resample) vs 1024 (1.6× resample) in the qualification, since the fix Task will carry the tiling parameters. Actually careful: bands of 640 tall at 690 wide → padded to 1024 wide? No — pad to square 690×690 → resize 690→640 means 1.08×. Hmm, if you pad the 690-wide band to a square of side max(690,640)=690, then the processor resizes 690×690 → 640×640 = 1.078×, essentially no resample. That would be the "native scale" option. With 1024×1024 padded tiles the content gets 1.6× downscale. So there IS a design alternative closer to native. Worth a P4/P3 suggestion. I'll fold it into R5 (参数依据) as a recommendation: 修复 Task 应在 qualification 中比较 1024²（1.6× 重采样）与 640/690 原生尺度块（≈1.0×），因为后者零重采样且块数更多（成本更高）。Hmm, actually blocks of 690×690 → 3× more tiles → 3× cost. Trade-off. Good note.

Wait, is that right? Tile 1024 tall covers 896 px of new content per step. A 690-tall tile with 128 overlap covers 562 px per step → 1.6× more tiles. Yes.

Enough. Let me write.

One more: item D scope — also check "无二进制" ✓ and "porcelain 干净" not verifiable statically → NOT_VERIFIED.

I'll now compose the final answer. It should be thorough but readable. Let me structure the findings table with columns: ID | 级别 | 位置 | 问题 | 建议.

Let me write the final output.
# Review：M2-DETECT-WEBTOON-DIAG（round 1，非作者独立审查）

审查对象：`8996ca55..b311f52f`（`review-input.diff`，5 文件）+ worktree `M2-DETECT-WEBTOON-DIAG-zcode` 实际文件。本机沙箱无法执行命令（`pwsh` 被沙箱拒绝），全部结论为静态审查；运行时项列入 NOT_VERIFIED。

## Verdict

**changes_requested**

核心判定成立、可接受：**整页无 letterbox 各向异性重缩放致目标消失**，且其决定性证据（K01 页内干预：同页/同权重/同阈值，仅改单次推理的像素预算 → 0→193）方法学正确、数字与上游证据（TA3-A smoke、TA3-B manifest、`detection_manga.py` pin）逐项对得上。范围纪律、零 `src` 改动、无二进制全部通过。

判 `changes_requested` 的原因**只有 1 条 P1 与 2 条 P2，且全部是文档/验收口径级更正，不需要重跑探针**：交付物把一个「无字页」（K19）写进了 tiling 修复的完成 Gate（`候选数 >0`），并把 pre-merge 文本框数 193 与生产 region 数当作同一计量层级，同时「NMS 实测有效」的原始框未落盘、不可独立复算。

## 逐项核对表

| 项 | 结论 | 依据（我已独立核对的事实） |
|---|---|---|
| **A 根因证据链** | **接受（P1/P3 措辞问题见 Findings）** | ①`_detect_text_boxes` 确无 size 覆盖直传 processor（`src/infrastructure/providers/detection_manga.py:342-348`）；②JSON 记录的 `size=640×640/do_pad=false/pad_size=null` 与 `model_input_shape=[1,3,640,640]`（四页含 62133px 高页）确为物理事实；③四条 score 数字（0.2045/0.1666/0.2835/0.9721）与 `counts_ge`、`logits_shape=[1,300,3]`、`official_post_process_ge_0_5` 全部与 JSON 一致；④压缩比算术自洽（62133/640=97.08、18401/640=28.75、28156/640=43.99、4167/640=6.51）；⑤权重三文件 sha256 与源码 pin **逐字符一致**，四页 sha256 与 `case-selection.json` 逐字符一致；⑥`smoke-K01.json:43` 确为 `region_count:15`、`source_sha256` 同页。**混淆变量判定**：BJ02/docTR 是跨域跨版面（JA paged_manga vs KO webtoon），**不能**单独排除「webtoon 域风格差异」；但 K01 页内干预把域/内容/权重全部固定，混淆变量在 §2.3 被消掉 ⇒ 论证链依赖块级实验闭环，逻辑完整（作者也把 docTR 标注为「背景证据」，标注正确） |
| **B 块级方法学** | **基本成立，2 处需更正** | ①1024² 来自任务书 AC2 明文，128px=12.5%=stride 32×4，几何自洽；70 块/步长 896/尾块 `crop_h=309` 与 JSON 完全一致；②「226→193」**不可独立复算**（JSON 只存 40/193 去重框，无 pre-NMS 坐标）；③tile 路径**跳过** `cluster_words_into_blocks`，而生产 region 是合并后的块 ⇒ 193 与「0 region」不同层级；④「70/70 块有检出」**可验证为真**（全文无 `"n_boxes_raw": 0`），单块 1（tile 13）–18（tile 19）；右 pad 带 70 块 × 334×1024px 零检出（`n_dropped_center_in_pad` 全 0）是有效的弱负对照，但**无纯空白块/BJ02 同切法对照**，且 min conf 0.5009 贴阈未做敏感度分析 |
| **C 修法建议** | **A 主线结论接受；证据强度被高估** | ①A 的「契约零变更」论证成立（`DetectionRequest/Response` 与 MERGE_* 输入=绝对像素 text_boxes 确实不变）；②「NMS IoU 0.5 实测有效」只在**单页单次**的 226→193 上测得，未验证被删的是重复框、留下的无重复；③193 vs docTR 15 的**粒度对比口径错误**（15 是 TA3-A 生产 region 数，不是行级数）；④性能估计依据=19793ms/70 块=283ms/块（线性外推成立），但最坏页 19.8s 相对 `273ms/页` 是 ~34× 退化，「秒级/页」与 Gate 均无数字预算；⑤C 的排除方向正确，但「远超 BJ02 的 6.5× 分布」是**单点比较、无剂量-响应曲线**，「排除」应保持为正文的「无支持证据」 |
| **D 范围纪律** | **PASS** | `review-input.diff` 仅 5 个 `diff --git`：`doc/handoffs/M2-DETECT-WEBTOON-DIAG-2d6b7bf6.md`(new)/`doc/tasks/M2-DETECT-WEBTOON-DIAG.md`(M)/`experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py`(new)/`verification/M2-DETECT-WEBTOON-DIAG/diagnosis.md`(new)/`probe-results.json`(new)——全部在允许面；无 `src/**`、`tests/**`、`requirements.txt`、`packaging/**`、`apps/**`、`doc/contracts/**`、`experiments/M2-TA3-A|B/**`、`doc/STATUS.md`；无 `Binary files`/`GIT binary patch`、无 `__pycache__`；新增行**无行尾空白**。`probe-results.json` 1,626 行、无像素/权重，**未全量存块坐标**（见 R3） |
| **E 文档质量** | **良好，5 处精度问题** | 表结构「判定→证据→排除→修法→局限→索引」可独立复核；JSON 结构（`probe_schema_version`/`environment`/`weights`/`preprocessor_config`/`pages`）与脚本写出字段**逐键一致**，说明 JSON 确由该脚本产出；局限（n=3、n=1 页、CPU、无 GT）如实。精度问题：`counts_ge["0.0"]=300` 恒真（R8）、四页交叉核对 3/4 为 0=0 平凡（R8）、`shortest_edge` 未入 keep 列表却称「已按原样记录」（R9）、「任务书 10–20% 带内」无出处（R5）、K05/K08 未采样未登记（R11） |

## Findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **R1** | **P1** | `doc/handoffs/M2-DETECT-WEBTOON-DIAG-2d6b7bf6.md:48,54,55`；`verification/M2-DETECT-WEBTOON-DIAG/diagnosis.md:115`；`doc/tasks/M2-DETECT-WEBTOON-DIAG.md:50` | **完成 Gate 把 K19 当成重缩放缺口**。Handoff 写「ko F1 六 case 候选数 >0 且全链可用」「交付物=…K19 重跑 qualification」。但 K19=`kr_Pepper-and-Carrot E20P01`、`layout_type=paged_webcomic`、实测 1200×1660（无长条漫压缩问题），且 `verification/M2-TA3-B/quality-report.md:52` 明载「该页所有语言 SVG 文本层为 0 元素=**无字页**，检出无候选是**正确行为**，但生产 step 状态为 failed/INVALID_INPUT——口径问题见 **F4**」（同页 `:62`/`:140` 亦同）。按现行 Gate，K19 永远不可能满足「候选数 >0」，除非检测器产生幻觉框 ⇒ 下一 Task 的 Gate 不可满足，且把 F4 口径缺陷误归为 F1 检测缺陷。 | 把 tiling 验收面**限定为 5 张 `webtoon_long_strip`**（K01/K02/K04/K05/K08），Gate 改为「生产 `provider.detect` region 数 >0 且全链可用」；K19 单列 F4 项（无字页应空成功、step 不得 `failed`）。三处文字同修（handoff/task/diagnosis）。 |
| **R2** | **P2** | `experiments/.../diagnose_webtoon_detect.py:343-367`（`run_tile_inference`/`tile_experiment`）vs `src/infrastructure/providers/detection_manga.py:148-152`；`diagnosis.md:15,69,92`；`doc/tasks/...:45` | **计量层级混淆**。tile 路径只做「阈值 0.5 + 文本类过滤 (1,2) + 跨块 NMS」，**未走** `cluster_words_into_blocks`；生产的 region/候选是**合并后的块**。故「0 → 193 检出/候选」是 pre-merge 文本框数 vs 生产 post-merge region 数，两者不可直接相减；AC2 的「块级是否恢复候选」字面上未被按候选计量。 | 文字改为「0 个 ≥0.5 文本框 → 193 个跨块去重文本框（**合并前**）」；修复 Task 的 qualification 用生产 `provider.detect` 的 region 数计量，并给出去重/合并后的块数（预期显著小于 193）。 |
| **R3** | **P2** | `diagnosis.md:71,93`；`diagnose_webtoon_detect.py:440-463`（只写 `deduped_boxes_sample[:40]`）；`probe-results.json:1088` | **「NMS IoU 0.5 实测有效」不可复核**。226→193 只在单页单次测得；JSON 未存全量框坐标（仅有 70 块 confidences 与 40 个去重样例框），无法验证「被删的 33 个是重复框」还是「该删的没删 / 误删真框」；也没有按重叠带（每块底部 128px）的重复率分析。文件体积不是理由（193 框若按 `[x0,y0,x1,y1,s]` 每框一行仅 ~200 行）。 | 落盘全量（或至少 pre-NMS）坐标并加一段「重叠带 vs 非重叠带检出密度/重复对」统计；或把结论降级为「去重使计数下降 14.6%，正确性未验证」。 |
| **R4** | **P3** | `diagnosis.md:70,104`；`doc/handoffs/...:63` | **docTR 15 的粒度表述错误**：15 是 TA3-A smoke 的**生产 region 数**（合并后），`smoke-K01.json:43`；其 region 框为 618×619/654×740 级（`:125-126`/`:147-148`），非「文本行级」。用它对比 pre-merge 的 193 正是本文自己警告的粒度错配。 | 改为「docTR 15 = 生产合并后 region；ogkalu 193 = 合并前文本框；两者先后层级不同，真正的产品取舍需在修复 Task 用同一层级（生产 region）对比」。 |
| **R5** | **P3** | `diagnosis.md:54`；`doc/tasks/...:26` | **参数依据出处不实**：「落在**任务书** 10–20% 带内」在任务书中不存在（AC2 只规定「1024×1024 块」，无重叠带宽）；`pad 常量灰 114` 自称「the common detection padding value」无引用。另：1024 与模型输入 640 **不对齐**（1.6× 重采样），而任务书也允许选更接近原生尺度的块。 | 删去「任务书 10–20% 带内」或改成「实验自选，理由=stride 32 整数倍」；修复 Task 的 qualification 建议加一组 690×690 原生尺度块（≈1.0× 重采样、块数 ~1.6×）作对照。 |
| **R6** | **P3** | `diagnosis.md:69,111` | **「唯一变量是输入的空间分辨率」不精确**：tile 干预同时改变了「单次推理的像素预算」与「输入宽高比（方形 vs 1:90，即消除了各向异性）」，二者共变。对方案 A 无害，但用它去论证 C（size 覆盖仍带各向异性）时需要区分。 | 改为「唯一被改变的是送入单次推理的像素预算（并由此消除各向异性拉伸）；本实验不区分二者的相对贡献」。 |
| **R7** | **P3** | `diagnosis.md:63,65`；`probe-results.json:932,1196-1214` | **70/70 与阈值敏感度**：复制前提正确（我核过 JSON 无 0 检出块），右 pad 带零检出也是有效弱负对照；但缺 ①纯 pad/空白块或 BJ02 同切法的 per-block 负对照，②阈值敏感度（min 0.5009 贴阈；tile 19 的 18 框中 **11 框 <0.6**：0.5903…0.5009）。193 这个数对阈值高度敏感，修复 Task 需要知道。 | 在局限中写明「无 per-block 负对照、无阈值敏感度」；修复 Task 的 qualification 带 ≥2 个阈值点的候选数曲线。 |
| **R8** | **P4** | `diagnosis.md:46,47` | ①`counts_ge["0.0"]=300` 对 sigmoid 输出**恒真**，不能支撑「300 个 query 全部有非零分数」；非平凡证据是 `counts_ge["0.01"]=143`（已在同句）。②「四页全部相等」中 3/4 是 0=0 平凡相等，交叉核对只在 BJ02 有检验力（0.5 阈值），建议在 0.1 阈值也交叉核对一次。 | 删去 §2.2 第 2 点的 tautological 依据；第 3 点注明「3/4 为平凡相等」。 |
| **R9** | **P4** | `diagnose_webtoon_detect.py:468-481`（`keep` 白名单）；`diagnosis.md:30` | `shortest_edge` **不在** keep 列表内 ⇒ 它即使存在也不会进 JSON；故「无 shortest_edge 字段…探针已按原样记录」的后半句不成立（断言本身很可能是对的）。 | `keep` 增补 `shortest_edge`/`resample` 等键，或把句子改为「该字段未被记录，依据是 RTDetrImageProcessor 走显式 `size` 路径」。 |
| **R10** | **P4** | `diagnosis.md:61,93`；`doc/handoffs/...:55,62` | 性能证据链有缺口：「**273ms/页先例**」在本任务证据内无出处（JSON 实测 K01 `provider_detect` 574ms / raw infer 297ms、BJ02 333ms）；Gate 写「CPU 秒级/页预期」而最坏实测 19.8s（≈34× 退化），无数字预算。 | 引用 273ms 的原始 artifact；Gate 改为可判定的延迟预算（如「K01 ≤ 25s / K02 ≤ 10s，CPU」）。 |
| **R11** | **P3** | `diagnosis.md:121`（局限性）；`doc/tasks/...:21` | 局限未登记 **K05/K08 完全未采样**（探针只跑 K01/K02/K04/BJ02），而交付文字反复以「六 case」表述 F1 覆盖面 ⇒ 读者会以为六 case 都有适配器级可观测值。 | 局限性加一句「F1 六 case 中 K05/K08 无任何探针；外推基于 3 页同形态塌陷」。 |

补充（不计 finding）：`diagnose_webtoon_detect.py` 使用 `provider._engine_or_raise()` 私有方法——实验脚本可接受，但应在修复 Task 复用同一路径时留意 API 漂移。未发现 P0。

## NOT_VERIFIED（集成方运行时项）

1. **探针复跑**（`python experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py`，主 venv + 权重快照 + CPU 1–2 分钟）：用于确认 `generated_at_utc=2026-10-01T11:43:32Z` 的 JSON 可由当前脚本重现，尤其 `226/193` 与逐块 confidences。
2. **磁盘权重真实 sha256**：我**已静态核实** JSON 内记录的三文件 sha256 与 `detection_manga.py:85-93` 的生产 pin **逐字符一致**、四页 sha256 与 `case-selection.json` 一致；但「磁盘上那三/四个文件确实是这些哈希」需运行侧确认（`all_pins_match=true` 为 Owner 自述）。
3. **`226 = Σ n_boxes_raw` 与 `193 = NMS 输出`**：无可执行环境逐块求和复算，且坐标未落盘 ⇒ 该等式**不可由交付物复算**（已记为 R3）。
4. `git status --porcelain` 干净、`git diff --check 8996ca55..2d6b7bf6` EXIT=0、`git show 2d6b7bf6 --stat` 仅 4 文件：我静态确认「新增行零行尾空白」「diff 共 5 文件全部在允许面」，但 EXIT 码与 porcelain 需集成方跑。
5. **「本轮未重跑探针」**：需 `git log --stat`/blob 时间戳证据；静态只能确认 JSON 结构与脚本写出字段一致。
6. `行尾/文件数`之外：`probe-results.json` 实际字节数（我按 1,626 行 + 无二进制判断为小体积，未取字节数）。
7. 生产 `273ms/页` 先例的原始 artifact（源不在本 diff 内）。

## 集成方闭合清单

1. **R1（P1，必须先改）**：tiling 验收面改为 5 张 `webtoon_long_strip`；K19 归 F4「无字页空成功」口径。同修 `handoff:48,54,55`、`diagnosis.md:115`、`doc/tasks/...:50`。
2. **R2/R3（P2）**：把 193 标注为 pre-merge 文本框；修复 Task 的完成 Gate 用生产 `provider.detect` 的 region 数计量；让 Owner 补全量框坐标或把「NMS 实测有效」降级表述。
3. 建议一并闭合 R4/R5/R8/R9/R10/R11（纯文字更正，无需重跑）。
4. Codex 集成时在 `doc/STATUS.md` 登记（本 Task 禁改面）：诊断结论、R1 口径更正、修复 Task 释放范围（含 `src/infrastructure/providers/detection_manga.py` 与检测参数配置通道）。
5. 归档 Review：`doc/reviews/M2-DETECT-WEBTOON-DIAG-<head>-dsh-r1.md`（本轮）。
6. 释放前确认：修复 Task 的触发条件、块尺寸/重叠、NMS 阈值均**配置化**（与 handoff:53 一致），且新增测试覆盖跨块截断框与重叠带重复。

## 推荐下一步（一句）

以「仅文档/验收口径更正」闭合 R1–R3（**不必重跑探针**，核心判定与证据我已独立接受），随后由 Codex 释放修复 Task，其 Gate 限 5 张 webtoon 长条漫、以生产 region 层级计数并带明确 CPU 延迟预算，K19 单列 F4 口径项。
