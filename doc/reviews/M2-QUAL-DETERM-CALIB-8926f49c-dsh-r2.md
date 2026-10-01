dsh: reasoning:
让我开始这个 review 任务。首先读取 r1 报告、返修 diff、以及 worktree 的相关文件。

让我先做初步侦察。
dsh: reasoning:
The file sandbox failed to grant write. Hmm, "SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)". This is a sandbox setup failure, not a denial of my operation. Let me retry maybe. It says workspace-write policy. Possibly transient. Let me try again.

Actually maybe I should try with sandbox_permissions escalation? But the guidance says a blocked file operation is reported as `[sandbox: file access denied under <mode> mode]`. This is a different error — setup failure. Let me retry once.
dsh: reasoning:
The sandbox cannot set ACLs on the workspace. Possibly because the workspace dir is G:\CODEX\New Manga and I'm the workspace root owner... Let me try reading a file with the read tool — maybe that works via a different path.

Actually the failure occurs at sandbox setup for pwsh. The read/glob/grep tools might have a different backend. Let me try.
dsh: reasoning:
Interesting — dsh-review-r1.md appears to be a transcript of the r1 review including reasoning. Let me read the rest, specifically the final verdict section (R1-R14 findings). Also read dsh-review-r2.md (which exists — that's my current output target? Actually r2 file already exists! Maybe from a previous attempt of this round). Let me check.

Wait — glob shows dsh-review-r1.md and dsh-review-r2.md. So r2 exists already. Hmm, the task says round 2 review. The r2 file might be a partial/previous run. Let me read the tail of r1 first (the findings), then r2.

Note pwsh is broken (sandbox provisioning failure: SetNamedSecurityInfoW failed). The r1 reviewer noted the same and proceeded with read/glob/grep only. I should do the same. Let me check if pwsh works now... it failed twice. Let me try once more later maybe with sandbox_permissions. Actually the error is not a policy denial marker; it's a setup failure. Retrying may not help. Perhaps I could try a different workdir (the workspace is "G:\CODEX\New Manga" — grantWrite failed there, maybe because the current session's workspace already... hmm). Let's try workdir=G:/CODEX temporarily? That would be outside workspace. Let me just try one retry with a workdir inside a temp area.

Actually, let me try `pwsh` with workdir set to a Temp path to see if the sandbox grants write elsewhere. The error came from granting write on the workspace root. If the file policy requires granting write on workspace root and it fails, no pwsh will work. Let me test once with a different workdir.

Let me batch: read r1 tail, read r2, and try pwsh retry.
dsh: reasoning:
pwsh is unavailable. So I must do this review statically with read/glob/grep only. That matches r1's approach.

Let me continue reading r1's tail to get the final findings (R1-R14 conditions).

Also there's dsh-review-r2.md — the current task asks me to produce round 2. Maybe r2 file exists from a prior partial attempt. Let me read it.

Let me read r1 offset 693 onwards, and r2.
dsh: reasoning:
The r2 file is just my current session's partial transcript (being written live). OK, so dsh-review-r2.md is the current session transcript being recorded. Fine.

Important: pwsh is unavailable in this environment — the same sandbox provisioning failure. So I must do this statically with read/glob/grep.

Now I have the r1 findings R1-R14 fully. Let me now read the review-fix.diff and verify the claims.

Let me plan the verification:

R1 (P2): bbox per-reading_order assertion fail-closed + calibration.md §1.1 assumption registration.
R2 (P2): case_gate_verdict coverage precondition (non-empty pairs → n≥1 else NO_DATA) + thresholds §5 "全空跑由 §7 translate 评分 Gate 兜底" relation sentence + limitation.
R3 (P2): thresholds §5 0-pair → NO_DATA exemption + "ko webtoon 家族未被本次校准覆盖".
R4 (P2): "0.05 绝对值余量" unified + §6.3 length cliff 4-char counterexample.
R5 (P3): median boundary limited to sample length distribution.
R6 (P3): is_nonempty extracted common + 判空基准 unified.
R7 (P3): translate_details coverage assertion + dropped 落盘 (measured 0).
R8 (P3): 词面口径误报方向登记 (probe not added + reason).
R9 (P3): 双轨判别规则 (provider 绑定判轨 + runner --determinism-track 显式记录、不一致 fail-closed).
R10 (P3): quality-report :189/:199 relation note.
R11 (P3): Task AC3 actual revision surface + §1 empty check registration.
R12 (P4): handoff denominator 7/11 non-empty first.
R13 (P4): calibration.json relative path.
R14 (P4): fork_commit annotation.

Plus: rerun consistency claim; self-check claims.

Let me read the review-fix.diff. It may be large. Let me check size first via glob/read. Let me grep for diff headers.

Let me read the fix diff.
dsh: reasoning:
7 files: handoff, task, script, calibration.json, calibration.md, quality-report.md, quality-thresholds.md. Note: **quality-report.md** is now modified — that was NOT in the allowed surface per r1's D-section reading ("Task allows verification/M2-TA3-B/** thresholds/plan 修订"). Wait, actually the Task allowed surface: r1 said "verification/M2-TA3-B/** 的 thresholds/plan 修订". Now quality-report.md is modified under R10 (which r1 itself recommended as an option: "报告 :189/:199 加一行关系注"). So it's a recommended fix. Need to check the Task's allowed surface wording to see whether quality-report.md is allowed. Let me read the task file's 允许修改路径.

Note: phase2-plan.md is NOT in this fix diff (no changes needed).

Total: "7 文件 +223/−46" per the prompt. Let me verify the counts by reading the whole diff. 223 added, 46 removed.

Note the allowed-surface question: 7 files include quality-report.md which might be outside the frozen allowed surface. That's a key 回潮 check item ("7 文件全允许面").

Let me read the whole fix diff now (557+ lines). Let me read it in chunks.
dsh: reasoning:
Continue reading the diff.
dsh: reasoning:
Continue reading the rest of the diff (450-570).
dsh: reasoning:
Now I have the full fix diff. Note: the diff shows quality-thresholds.md only ONE hunk (@@ -165,11 +165,11 @@ shared context includes both the §5 rows and the F5 note — showing as a single hunk because they're within the context window). So the change is: §5 remote row (line 168) modified, mock row (169) unchanged (context line 563), and the F5 note (line 172) modified. Good — no other thresholds changed. §7 row 10 wasn't touched in this diff (that was touched in the previous commit e3b7c48d). OK.

Now let me verify claims against the actual worktree files. Key items:

1. Does the worktree tip = 8926f49c? And is the fix commit 8926f49c? Let me verify via .git refs / reflog (read-only file reads, as r1 did).

2. Verify the script's actual content (R1/R2/R6/R7 implementations) with line numbers.

3. Verify calibration.json new values: coverage fields, relative path, method/limitations text, and that distributions/pairs/verdicts are unchanged.

4. Verify the claim "返修前后 calibration.json 18 对/分布/探针/逐对/verdicts 逐值零差异" — I can compare the fix diff's calibration.json hunks: the diff only shows structural changes (summaries_dir, method alignment_key, empty_pair_rule additions, coverage fields, reasoning, limitations). Indeed no pairs/distribution values changed in the diff → strong evidence of zero numeric difference. Let me confirm: the json hunks are @@ -2,7, @@ -10,7, @@ -19,6, @@ -30,6 (K11 coverage), @@ -239,6 (BJ02 coverage), @@ -499,14 (reasoning). So yes, no distribution/pair value changes. 

Wait — one important thing: gate_verdict_normalized for each case. The fix changed build_pairs to use case_gate_verdict(pairs) instead of gate_verdict(median, min). Since K11 and BJ02 have non-empty pairs, the verdict is unchanged (PASS). The diff doesn't show changes to gate_verdict_normalized lines → consistent.

But there's a subtle issue: `case_gate_verdict` uses `round(statistics.median(values), 4)` where values = similarity_normalized of ALL pairs (including empty_both). Previously it used `distribution([...])["median"]`. Is distribution's median the same as round(statistics.median(...),4)? Let me check the distribution function. r1 read it at file line 187. Need to verify it rounds to 4. If distribution rounds to 4 and uses statistics.median on rounded values... Let's check: distribution(values) probably computes `[round(v,4) for v in values]` then median. In the old code, `distribution([p["similarity_normalized"] for p in pairs])["median"]`. similarity_normalized values are already rounded (probably at creation). Need to check whether closing gate uses rounded or raw. Potential subtle difference: if similarity_normalized is rounded at pair creation (round(...,4)), then statistics.median(values) equals distribution median. Let me check the script.

Also: does the change from `gate_verdict(median, min)` to `case_gate_verdict(pairs)` preserve NO_DATA for empty distributions? gate_verdict(None, None) → NO_DATA presumably. case_gate_verdict returns NO_DATA if no nonempty pairs. Fine.

5. R2 coverage precondition: threshold §5 wording — "非空对 n≥1 方可判定，否则 NO_DATA——全空跑...由 §7 translate 评分 Gate 兜底...region_count=0 的 case 贡献 0 对 → 同 NO_DATA 口径豁免...不阻断整体 Gate". The review question: "NO_DATA 豁免不阻断整体 Gate 的口径是否清晰". Need to assess clarity. Concern: the §5 text says PASS/EARLIER "全部对齐对 ... 满足 median ≥0.95 且 min ≥0.70 方为 PASS" — and now with NO_DATA exemption. Is it clear what the overall Gate verdict is when one case is NO_DATA? The text says "不阻断整体 Gate 但单独登记" for region_count=0. But what about a NO_DATA due to all-empty (provider down)? The text says "全空跑...可平凡 PASS，由 §7 translate 评分 Gate 兜底，本 Gate 不对翻译覆盖度负责". Hmm — that phrasing conflicts subtly with the coverage precondition: the precondition says NO_DATA (not PASS) for all-empty; but the relation sentence says "全空跑在相似度口径下可平凡 PASS，由 §7 兜底". So does all-empty → NO_DATA or PASS? The script returns NO_DATA. The §5 text says both "否则 NO_DATA" and separately "全空跑…可平凡 PASS…由 §7 兜底". This is a genuine potential ambiguity: the reader may read "全空跑 → 平凡 PASS（不阻断）+ §7 兜底" which contradicts "非空对 n≥1 方可判定，否则 NO_DATA".

Hmm, but careful: "全空跑在相似度口径下可平凡 PASS" describes the *pre-fix* gate behavior (the blind spot) — the fix then adds the precondition to turn it into NO_DATA. Reading the full sentence: "覆盖前置（CALIB r1 R2/R3）：非空对 n≥1 方可判定，否则 NO_DATA——全空跑（两次 run 译文全空）在相似度口径下可平凡 PASS，由 §7 translate 评分 Gate 兜底，本 Gate 不对翻译覆盖度负责". The em-dash clause is a rationale. It's arguably readable, but there is a real semantic tension: is all-empty "NO_DATA" or is it "PASS by trivial similarity, compensated by §7"? Also whether NO_DATA blocks integration isn't stated for the all-empty case (only the region_count=0 case says "不阻断整体 Gate"). This is a legitimate P3-level clarity finding for round 2 — the owner claims "全空跑由 §7 translate 评分 Gate 兜底" relation sentence + limitation. The requirement in the task: "R2/R3 的 thresholds §5 新文案语义（NO_DATA 豁免不阻断整体 Gate 的口径是否清晰）".

Let me think harder: What does "不阻断整体 Gate" mean? The overall Gate (the F5 determinism gate over the fixed 3 cases). For K01 (region_count=0), NO_DATA → exempt, doesn't block. For an all-empty run, the case would also be NO_DATA... but is that "不阻断"? If a case is all-empty in both runs, then that case is NO_DATA. Under "不阻断整体 Gate" it would not block either — meaning "provider down" would NOT block the F5 determinism gate! That's exactly the blind spot R2 wanted closed. But the §5 wording says coverage is handled by the §7 translate gate. Is that a fair closure? The r1 recommendation was: "在 Gate 定义中加覆盖前置（如「非空源 region 中译文非空比例」或「非空对 n≥1」），或在局限中明写「全空跑可 PASS，由 §7 第 8 行 translate 评分 Gate 兜底」". The owner did BOTH: added a precondition producing NO_DATA AND the relation sentence. Reasonable.

But the ambiguity: NO_DATA for all-empty — does it block? The §5 says for region_count=0 "同 NO_DATA 口径豁免（与 §6 R11 零 region 豁免同口径），不阻断整体 Gate 但单独登记". Since the "NO_DATA 口径" is defined as 豁免/不阻断, and all-empty also → NO_DATA, a reader infers all-empty also doesn't block overall gate. So a provider-down run wouldn't block the determinism gate — but would block the §7 translate gate. The relation sentence states exactly that. So it is *arguably* clear, but requires the reader to connect "否则 NO_DATA" with "同 NO_DATA 口径豁免". I'd call it "清晰度基本达标但有一处措辞张力" — P3, non-blocking, worth noting for a future wording pass. Hmm.

Actually wait. There's a deeper issue worth checking: is NO_DATA semantically right for the all-empty case *as a determinism gate*? If both runs consistently return empty, the determinism gate has no signal — NO_DATA is honest. And coverage is a separate gate. That's a defensible design. OK.

However, there's a real potential inconsistency I should verify: the §5 text says "region_count=0 的 case 贡献 0 对 → 同 NO_DATA 口径豁免（与 §6 R11 零 region 豁免同口径）". Does §6 R11 actually exist in quality-thresholds.md §6? Let me check §6 for an "R11 零 region 豁免" entry. This is a cross-reference that must resolve. Need to grep.

Also: does the calibration.md/text claim "K11=ko P&C、BJ02=ja BJ"? K11 is Korean (당근아? = Korean). And thresholds §5 originally said fixed 3 cases cover "ja BJ 印刷漫 / ko webtoon / ko P&C 三家族" — so K01 = ko webtoon, K11 = ko P&C, BJ02 = ja BJ. The fix says "本次校准的 K01 即此情形，ko webtoon 家族因此未被本次校准覆盖". Correct.

6. R4: "0.05 绝对值余量" unified — check thresholds §5 (line 562) now says "留 **0.05 绝对值余量**=0.70（CALIB r1 R4：非「一个字符」，4 字锚串 1 编辑差=0.25）" ✓, calibration.md §4.1 ✓, script reasoning ✓, and §6.3 length cliff with 4-char counterexample ✓. Also need to check the calibration.md §4.1 "min ≥ 0.7" vs thresholds "0.70" — minor.

7. R5: median boundary限定样本长度分布 ✓ (in script, md §4.2, §6.7, json limitation)

8. R6: is_nonempty extracted ✓; but verify it's used in both places ✓ (line 203 and 334 in diff). Also `pair_status` now uses normalize. Note: is_nonempty uses normalize(text_first) or normalize(text_second) — equivalent to status != empty_both/empty_one_side? Let's check: is_nonempty returns bool(nf or ns). For empty_both: nf="" ns="" → False ✓. For empty_one_side: nf="" ns nonzero → True! **Wait**: `bool(normalize(first) or normalize(second))` → if first is empty but second is non-empty, returns True. But the docstring says "excludes empty_both AND empty_one_side". That's a BUG in the new is_nonempty! Let me re-read:

```python
def is_nonempty(pair: dict) -> bool:
    """r1 R6: the single non-empty-pair predicate shared by the case-level
    and aggregate subsets (excludes empty_both AND empty_one_side; a side
    is empty iff normalized to "")."""
    return bool(normalize(pair["text_first"]) or normalize(pair["text_second"]))
```

`normalize(text_first) or normalize(text_second)`: if text_first normalizes to "" and text_second is non-empty, the expression is truthy → returns True → pair counted as non-empty. But the docstring claims it excludes empty_one_side. So the predicate does NOT exclude empty_one_side — it only excludes the case where BOTH are empty.

And what was the old aggregate definition? `p["status"] not in ("empty_both", "empty_one_side")` → excluded both. So the new is_nonempty CHANGES the aggregate semantics for empty_one_side pairs: previously excluded, now included. And the case-level old definition was `p["status"] not in ("empty_both",)` → included empty_one_side. So the "unification" chose the case-level semantics (include one-side-empty) but the docstring claims exclusion of both.

Which is correct? r1 R6 said: "抽一个 is_nonempty(pair) 供两处共用" and "建议都用 normalize 后的空串". r1's R6 complaint was that the two definitions differed: per-case included empty_one_side, aggregate excluded it. The unification picks "OR" semantics = non-empty if either side non-empty = excludes only empty_both. That means the aggregate "非空对" subset would now INCLUDE empty_one_side pairs (when they occur). Is that intended? For the *aggregate nonempty* subset (used to report raw_nonempty / normalized_nonempty distributions), including a one-side-empty pair (similarity 0.0) would drag the distribution down. Semantically, "非空对" for reporting distributions... r1's suggestion implied unifying, without specifying which. The adopted definition (either side non-empty) is arguably the natural reading of "非空对" (a pair where at least one side has text). But the docstring's parenthetical contradicts the implementation — a real defect: the code's docstring states "excludes empty_both AND empty_one_side" while the implementation excludes only empty_both. That's an internal inconsistency introduced by the fix commit, AND it changes the aggregate denominator semantics vs r1's original (which excluded both).

Crucially: does this change any numbers? No — because the current data has no empty_one_side pairs, so the numbers are identical (the handoff says zero numeric change, consistent). But it's a latent semantic divergence plus a false docstring. Is it a regression relative to r1's R6 ask? r1 said "两处定义不同 → 抽公共"—the fix achieved a common predicate but the common predicate matches the case-level (permissive) definition, not the aggregate (strict) one, and the docstring documents the strict one. So R6 is "partial" — the extraction happened, but (a) the docstring is wrong, and (b) the aggregate semantics silently changed (documented as "excludes empty_both AND empty_one_side" in the docstring but implemented permissively).

Wait — actually let me double check: maybe is_nonempty is intended as "at least one side non-empty" and the docstring just mis-states. Either way, one of code/doc is wrong. This is a legitimate new finding for round 2 (P3, maybe P2 given it's a Gate-definition artifact? It doesn't affect current numbers; the aggregate nonempty subset is a *reporting* subset, not the Gate itself — the Gate uses all pairs via case_gate_verdict). Let me confirm what the aggregate nonempty is used for: `nonempty_pairs = [p for p in all_pairs if is_nonempty(p)]` then distributions raw_nonempty/normalized_nonempty reported. Not a Gate leg (Gate uses per-case case_gate_verdict over all pairs). So impact = reporting subset semantics + wrong docstring. P3.

Hmm, but also important: does the change alter module behavior for future data in a way that's fail-open? Including empty_one_side (sim 0.0) into the nonempty subset would *lower* the reported median/min (fail-closed direction). Not dangerous.

Let me also double-check `pair_status`'s raw comparison: `return "identical" if first == second else "variant"`. With normalize-based emptiness. Fine.

Another potential issue with pair_status: normalize() strips all whitespace; two texts differing only in whitespace → both non-empty, status="variant" (since raw differ) but similarity_normalized = 1.0. That's the existing disclosure (ro=5/10). Fine.

9. R7: coverage assertion + dropped field. Note: the new assert is `if set(t1) != ros1 or set(t2) != ros2` → SystemExit. But wait: this assertion means EVERY region must have a translate_detail. Is that always true in general? For K11, translate_details has 13 entries = 13 regions ✓. BJ02 5/5 ✓. But hold on: K11 `details.translated=11` while 13 regions — but translate_details has 13 entries (including empty translated_text for ro=9/13). Right, per r1 verification translate_details count = 13.

Hmm, but is the new assertion too strict for future data? E.g., SFX regions might legitimately have no translate_detail entry in some runs (if the pipeline skips writing details for SFX)? Then the script would hard-FAIL (SystemExit) rather than exclude. That's fail-closed but could cause false FATAL. Given the current design "must cover all regions", that's a deliberate fail-closed choice. It's a design decision worth noting: the assert treats "region without translate_detail" as a summary inconsistency. Given K11 includes SFX with an explicit empty detail, the convention seems to be that every region gets a detail entry. Acceptable. Worth a NOT_VERIFIED/observation. Also note: `set(t1) != ros1` — t1 keys are read from translate_details; a *duplicate* translate_detail with the same reading_order would collapse (dict overwrite) and could still satisfy the assertion while dropping one... Actually if two details map to the same reading_order (dup region_id), out[ro] overwritten → set size smaller → assertion catches (set(t1) != ros1) unless there's also a missing region... fine, it's caught. Good.

Also: the `n_dropped_regions` field is computed after the assertion, so it's always 0 — the field is vacuous (assertion already guarantees 0). That's fine as bookkeeping (handoff says 实测 0). But note: `n_dropped_regions` can never be non-zero, so it carries no information. Minor P4. Actually it does demonstrate the completeness basis in the artifact. Fine.

10. R9: the double-track discriminator: "按本次 run 的 translate provider 绑定判定轨道——remote 采样 provider（provider id 含 remote 采样服务标识，如 deepseek/*）走相似度轨，mock/确定性 provider 走哈希轨；qualification runner 以 --determinism-track remote|mock 参数显式记录所选轨道，声明与 provider 绑定不一致时 fail-closed 报错。" Is this executable? It references a runner parameter `--determinism-track` that doesn't exist yet in any runner (TA3-A runner `run_smoke.py`?). So it's a forward-looking contract statement. The r1 ask was "补一句判别规则（如「按 provider 绑定是否 remote 采样」或新增 --determinism-track 参数）". The owner did both: provider binding rule + a declared future runner flag + fail-closed on mismatch. Executability: the rule is now determinate (provider binding is observable), and the flag is specified. But "provider id 含 remote 采样服务标识，如 deepseek/*" is a bit loose (what counts as remote sampling?). And no runner currently implements --determinism-track → NOT_VERIFIED/implementation pending. This is acceptable for a threshold-definition doc: it defines the discriminator and the enforcement. I'd mark R9 closed with a note that the flag's implementation is future work (must be registered somewhere). Is it registered as pending? Not explicitly. Let me grep for determinism-track across the repo to see if it's referenced elsewhere (e.g., phase2-plan), and whether some "待实现" registration exists.

11. R10: quality-report.md :189/:199 relation notes added ✓ — but is quality-report.md within the allowed surface? Need to check the Task's 允许修改面 section. Note the evidence must be checked. Let me read the task file fully.

12. R11: Task AC3 updated ✓ (line 62 of diff), fork_commit added ✓.

13. R12: handoff AC1 row updated to 7/11 非空对 ✓.

14. R13: calibration.json summaries_dir relative ✓; script uses `SUMMARIES_DIR.relative_to(REPO_ROOT) if SUMMARIES_DIR.is_relative_to(REPO_ROOT)`. Need REPO_ROOT defined. `is_relative_to` requires Python 3.9+. Fine. But note: `Path.relative_to` on Windows path — SUMMARIES_DIR is REPO_ROOT / "verification/M2-TA3-B/phase2/summaries" → relative_to works. If the default path is derived from REPO_ROOT, it always is_relative_to → always relative. Good. But subtle: the script's default SUMMARIES_DIR = REPO_ROOT / ... so the fallback (absolute) would only trigger with an explicit --summaries-dir outside. Fine.

Wait: does REPO_ROOT exist as a variable in the script? r1 said REPO_ROOT = parents[2]. Let me verify in the actual file. Also, does the script use REPO_ROOT for the default SUMMARIES_DIR? Need to read the script.

15. The claim "连续两次重跑 sha256 字节级一致" — NOT_VERIFIED (no shell).

16. The claim "qual-*.json 零改动、porcelain 干净、diff --check EXIT=0" — NOT_VERIFIED (no shell), but the fix diff contains no qual-*.json ✓. I can also check that the worktree files' mtimes... no, not meaningful.

Wait — actually can I verify porcelain indirectly? No shell. Hmm. But maybe I can read the reflog/HEAD to verify tip=8926f49c and that the branch is at the fix commit. Let me read the worktree's gitdir files: .git file → gitdir path; then logs/HEAD. r1 did this. Let me do it.

Also I should verify the fix commit 8926f49c is actually the tip and that e3b7c48d → 8926f49c. Note the prompt says "返修 commit=8926f49c（2400b57a→8926f49c）". Interesting: the fix commit's parent is 2400b57a (the handoff commit). Let me verify via reflog.

Let me now do a batch of reads:
- worktree .git file
- main repo .git/worktrees/M2-QUAL-DETERM-CALIB-zcode/logs/HEAD
- task file (doc/tasks/M2-QUAL-DETERM-CALIB.md) full
- the script file relevant regions

Let me start. Note that paths with spaces — read tool should handle.

Actually, one consideration: reading the .git file. Let me glob for it.

Let me batch several reads.
dsh: reasoning:
Task file: 允许面 = `experiments/M2-QUAL-DETERM-CALIB/**`、`verification/M2-TA3-B/**`（thresholds/plan 修订+本 Task 产物）、Task/Handoff。So quality-report.md IS under verification/M2-TA3-B/** → allowed. ✓ Note the parenthetical "（thresholds/plan 修订+本 Task 产物）" narrows the intent, but the path glob allows it. r1 raised it as R10 recommending an annotation. The owner implemented it in that file and explicitly noted "该文件在本 Task 允许面 verification/M2-TA3-B/** 内". Acceptable — I should note that the narrow parenthetical means it's a "允许面内但超出括号列举" case; but since the fix was explicitly requested by r1 R10 and the path is allowed, it's fine. I'll flag as a minor observation (P4) at most, or just note it as acceptable.

Now, worktree gitdir. Let me read the reflog to verify tip = 8926f49c and commit chain.
dsh: reasoning:
Confirmed: tip = 8926f49c25e76cf0fdd89a2a030cdc9024b316ee, parent = 2400b57a (matches prompt "2400b57a→8926f49c"). Task handoff said "e3b7c48d 的父提交即 8996ca55" ✓ (reflog line 3 shows 8996ca55 → e3b7c48d). So fork_commit: 8996ca55 annotation is factually correct ✓.

Also the branch is on the worktree, HEAD → refs/heads/agent/zcode/M2-QUAL-DETERM-CALIB. Let me verify the ref = 8926f49c.

Now let me check main's HEAD (should still be at 8996ca55, i.e., no integration yet).

And read the script's key sections + verify line numbers.

Let me batch:
- read refs/heads/agent/zcode/M2-QUAL-DETERM-CALIB (in the common .git dir)
- read main .git/HEAD and refs/heads/main
- read the script file (whole, ~800 lines now)

Let me read the script in chunks. Actually let me first read the head region (1-140) and the key functions.

Since I need accurate line numbers, let me read the whole file in 2 reads (it's ~800 lines).

Actually, more efficient: grep for key definitions to get line numbers, then read targeted ranges.

Let me batch grep + reads.
dsh: reasoning:
Branch ref = 8926f49c ✓. main HEAD → refs/heads/main; r1 said main = 8996ca55. Let me verify main ref later (probably unchanged).

Now read the script sections:
- 60-100 (constants, disclaimer)
- 95-200 (normalize, levenshtein, similarity, translations_by_reading_order, pair_status, is_nonempty)
- 200-330 (percentile, distribution, perturb, synthetic_probes, gate_verdict, case_gate_verdict)
- 320-420 (build_pairs)
- 690-800 (main)

Let me batch reads.
dsh: reasoning:
main ref = 1d477b35... — not 8996ca55 anymore! So main has advanced beyond the release commit. Interesting. r1 said main was at 8996ca55 at r1 time. Now main = 1d477b35. That means other commits landed on main (integration of other tasks in the 4-task batch, or the release-followups). This means the worktree branch's fork point (8996ca55) is now behind main. Not a defect of this deliverable, but relevant to the integration step (rebase/merge needed) and to the "branch base" claim: fork_commit: 8996ca55 remains factually correct (the branch really was created from 8996ca55). Good — R14's annotation is accurate.

Hmm, but does this affect anything? The integrator will need to merge into main at 1d477b35. Fine — note in next steps.

Let me check main's reflog tail to see what landed after 8996ca55 (useful for integration context: whether thresholds/quality-report have been changed by others since → potential conflict). Let me grep main's logs/HEAD for the recent entries.

Actually, more relevant: are there changes on main since 8996ca55 that touch the same files (quality-thresholds.md, quality-report.md, calibration.*)? If yes, the fix diff base might be stale → merge conflicts. Let me check main reflog entries after 8996ca55.

Let me grep the main reflog for lines after 8996ca55. I'll read the tail of G:/CODEX/New Manga/.git/logs/HEAD.

Also important: is `is_nonempty` correct? Confirmed the bug: `normalize(text_first) or normalize(text_second)` — for empty_one_side, one is empty, the other non-empty → truthy → True, so pair is counted non-empty. Docstring says excludes empty_one_side. So docstring contradicts implementation. Let me double check what the impact is for the aggregate `nonempty_pairs` (main). In main, nonempty_pairs is used for distributions raw_nonempty/normalized_nonempty. Previously (r1 version) it excluded empty_one_side too. So the semantic changed for hypothetical data. Both call sites now share the predicate. The r1 ask was satisfied in spirit (one predicate) but the predicate's semantics match the per-case old definition, and the docstring claims the aggregate old definition. So it's a documented-vs-implemented mismatch, plus a silent semantic change to the aggregate reported subset (only visible with empty_one_side data).

Wait, is the per-case `nonempty` (line ~375) used for n_pairs_nonempty and raw_nonempty/normalized_nonempty distributions too? Yes. With the old code per-case included empty_one_side; new code also includes it → per-case unchanged. Aggregate changed from exclude to include. So the fix did NOT unify to the stricter definition; it unified to the looser one, changing aggregate behavior. Since empty_one_side never occurs, zero numeric impact today.

Hmm — but which semantics is "right" for a *non-empty* subset? "非空对" naturally = a pair where at least one side is non-empty? Or where both are non-empty? Ambiguous. For the purposes of reporting a distribution of similarities over "non-empty" pairs, including a pair with similarity 0.0 (one side empty) seems wrong-ish but it IS "non-empty" in the sense that there's text. Eh. The important thing is the docstring is inconsistent with the code, and the aggregate definition silently changed. I'll report as R6-partial/P3 with precise file:line (191-195) and note the two call sites (case ~375, aggregate ~715?) Let me get exact current line numbers for the call sites.

Also check: does the fix's calibration.md/JSON document the non-empty definition? The json has `empty_pair_rule.emptiness_basis`. And `n_pairs_nonempty`. No statement of which subset rule. Fine.

Let me now read build_pairs and main to get exact line numbers and verify.
dsh: reasoning:
Interesting! main = 1d477b35a369b43b4940c04b9a8da4de02677c40, NOT 8996ca55 as r1 recorded. So main has advanced since r1 (the orchestrator has been integrating other tasks). That's fine — not a finding per se, but worth noting: main advanced beyond 8996ca55, confirming nothing from this branch is integrated (need to check whether 1d477b35 is a descendant of 8996ca55, can't verify ancestry without object decoding... but I can check the main reflog to see the transitions).

Let me check the main reflog tail for what happened after 8996ca55.

Also important: the is_nonempty docstring bug confirmed at line 191-195: docstring says "excludes empty_both AND empty_one_side" but implementation is `bool(nf or ns)` which INCLUDES empty_one_side. Confirmed defect (P3).

Let me now read the rest of the script: 305-440, and 690-844.

Also check pair creation: does pair dict include "similarity_normalized" rounded? Let's read build_pairs 322-420.
dsh: reasoning:
Now I have the script. Key observations:

1. `case_gate_verdict` uses `values = [p["similarity_normalized"] for p in pairs]` (all pairs) and `round(statistics.median(values), 4)`. The old code used `distribution([...])["median"]` = `round(statistics.median(values), 4)`. Identical. ✓ No numeric change.

BUT: is `case_gate_verdict` NO_DATA when there are 0 pairs? `any(...)` over empty → False → NO_DATA ✓. And for K11/BJ02, non-empty pairs exist → gate_verdict(median, min) ✓ unchanged.

2. `is_nonempty` docstring bug confirmed (line 191-195). Implementation = OR (excludes only empty_both).

Additionally, I realize there's a *second* consequence: the aggregate `nonempty_pairs` in main (line 708) now uses OR semantics → includes empty_one_side. But more importantly — check the aggregate distribution values in calibration.json: agg raw_nonempty n=16, normalized_nonempty n=16. Since no empty_one_side exists, unchanged ✓. The handoff claim "统计量逐值一致" holds for current data ✓.

Hmm wait, but there's another subtlety: r1's R6 said the two definitions differ, and the *fix* unified to OR semantics. Which is "correct"? The docstring (written in the fix) says it excludes both — the author *intended* AND semantics (exclude both) but implemented OR. Wait let me think again about which one the author intended:

`is_nonempty` docstring: "the single non-empty-pair predicate shared by the case-level and aggregate subsets (excludes empty_both AND empty_one_side; a side is empty iff normalized to "")".

If intended to exclude both, the implementation should be `bool(nf and ns)` (both non-empty = non-empty pair). The implementation `bool(nf or ns)` means "at least one side non-empty" which includes empty_one_side. So code ≠ docstring. Definitively a defect.

Which semantics then apply in the artifact? The code's OR. Is OR defensible as "非空对"? "非空对" naturally = "对中至少一方非空"... hmm, actually for the purpose of "excluding empty pairs from the non-empty subset", "非空对" would more naturally mean "not an empty pair" = not both-empty = OR. So OR matches the label "非空对" (a pair that isn't empty), while the docstring describes exclusion of one-side-empty (AND). r1's R6 complaint was about the divergence between per-case (OR-ish, status != empty_both) and aggregate (AND-ish). The fix picked OR and mis-documented it as AND.

So: the code resolves r1's divergence; the docstring is wrong. Impact today: zero (no empty_one_side in data). Future: aggregate nonempty subset includes one-side-empty pairs → the reported "非空" distribution includes 0.0-similarity pairs, dragging it down (conservative). Not fail-open. But the comment/docstring is self-contradictory → P3 finding (documentation defect introduced by the fix + semantic divergence from r1's stated aggregate definition not disclosed).

Also note: the fix's claim "重跑零数字变化（当前空对恰为 ''）" is honest but the docstring bug is new.

3. R1 bbox assertion: `if a["bbox"] != b["bbox"]`. bbox from `r.get("bbox")` — if the summary's regions lack a "bbox" key, both would be None and None == None → passes silently. Hmm! That's a hole: if bbox is absent in both runs, the cross-check is vacuous (None == None). Is bbox present in the summaries? r1 verified bbox exists in K11/BJ02 regions. So fine today. But the assertion doesn't prove bbox presence → a vacuous pass if the field is missing. Worth a P3/P4 note: should assert bbox is not None (or key present). Actually let's check: do regions in qual-*.json have "bbox"? r1 read them and saw bbox values. Let me confirm quickly with grep on the summaries. Also the calibration.json pairs do not record bbox; no matter.

That's a genuine residual: `bboxes.get(rid)` returns None if absent → cross-check silently passes. Recommend `if a["bbox"] is None or a["bbox"] != b["bbox"]`. I'll report as P3 (fail-open edge in the new guard).

Hmm, is it plausible that a summary's regions lack bbox? The regions[] entries in K11 show "bbox" (r1 saw x,y,w,h). Let me verify the key name — grep for '"bbox"' in qual-K11.json to see the structure. Actually r1 said "region_id 591425e1 ... bbox 45,6,123,48". Let me verify the actual JSON key: maybe it's "bbox": {"x":...} or "bbox": [x,y,w,h]. Either way, dict/list equality works. Let me confirm the key exists in regions[] (not just ocr_details[]). r1 said "rerun regions[] ro=13 (b2dad79f) bbox 805,564" — it seemed to read from regions. Let me verify with grep.

4. Check `distribution` called with `values` — case_gate_verdict no longer uses distribution; fine.

5. `main` global declaration at line 697 before argparse (line 699) ✓ — SyntaxError fixed.

6. `n_dropped_regions` always 0 given the assertion ✓ (vacuous but harmless).

7. R7 coverage assertion semantics: strict — every region needs a translate_detail. For K01 (0 regions), ros1 = set() and t1 = {} → equal → passes → pairs=[] → case_gate_verdict → NO_DATA ✓, and the artifact-level `gate_verdict_normalized` = NO_DATA. But note: K01 is NOT in CALIBRATION_CASES (only K11, BJ02). So K01 isn't even run by the calibration script. The thresholds §5 defines the Gate over the fixed 3-case set; the calibration script only covers 2. That's consistent with the disclosure "ko webtoon 家族未被本次校准覆盖" ✓.

8. One more: the thresholds §5 says "非空对 n≥1 方可判定，否则 NO_DATA". The script implements case_gate_verdict using `any(is_nonempty(p) for p in pairs)` — with OR semantics, an all-empty run → NO_DATA ✓ (all pairs both-empty → is_nonempty False) — correct for the stated precondition. Good: for the coverage precondition, OR semantics is the *right* choice (a pair with one side non-empty counts as coverage). So the OR semantics is arguably intended and the docstring is just wrong. Fine.

Now let me verify:
- qual-*.json unchanged: check the fix diff (no qual files) ✓. Also verify the regions[] have bbox keys.
- calibration.json content: relative path, coverage fields, no numeric changes.
- quality-thresholds.md §6 R11 reference exists.
- quality-thresholds.md §7 row 10 (from earlier commit) - check current content.
- phase2-plan not modified in this fix ✓ (only 7 files listed; phase2-plan absent → untouched by fix).

Let me now grep for the things I need:
- "R11" in quality-thresholds.md (§6 zero-region exemption)
- §7 row 10 content
- "determinism-track" across repo
- "bbox" in qual-K11.json regions

And read calibration.json relevant parts (head, coverage, gate verdicts, limitations) — to confirm the committed artifact matches the diff and has no other changes.

Also check: does calibration.json still contain "summaries_dir": "verification\\M2-TA3-B\\phase2\\summaries" — the diff shows the relative path with backslashes. Since it's a Windows path str() → backslashes ✓. R13 says "相对仓库根路径" — committed as `verification\M2-TA3-B\phase2\summaries`. Slightly platform-specific (backslash separators) but repo is Windows. Fine.

Let me also verify that the git diff hunk for quality-thresholds.md in the fix touches ONLY §5 row + note (no other thresholds numbers) — from the diff, hunk @@ -165,11 +165,11 @@ includes: line 561 replaced by 562 (remote row), line 563 context (mock row — unchanged), line 564 context (render row), line 566 replaced by 567 (note). So changed lines: 561→562 and 566→567; unchanged: 563, 564, 565. And no other hunk → §7 row 10 untouched in this commit (it was changed in e3b7c48d). ✓ Thresholds values elsewhere untouched ✓.

Now, "回潮检查：7 文件全允许面" — the 7 files:
1. doc/handoffs/... → Task/Handoff ✓
2. doc/tasks/M2-QUAL-DETERM-CALIB.md → Task ✓
3. experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py → ✓
4. verification/M2-QUAL-DETERM-CALIB/calibration.json → ✓ ("本 Task 产物")
5. verification/M2-QUAL-DETERM-CALIB/calibration.md → ✓
6. verification/M2-TA3-B/quality-report.md → path allowed (verification/M2-TA3-B/**), but the parenthetical says "（thresholds/plan 修订+本 Task 产物）" — quality-report.md is neither thresholds nor plan; it's a delivered TA3-B2 evidence doc. Strictly, the parenthetical narrows the intent. However r1 R10 explicitly recommended annotating it, and the Task's literal path glob permits verification/M2-TA3-B/**. So: 允许面内（字面），但超出括号列举意图 — note as P4/observation with recommendation that the integrator confirm the narrow-scope reading, since TA3-B2 产物 JSON 禁改 only covers qual-*.json. Actually the 禁改 list includes "TA3-B2 已交付 run 产物 JSON（qual-*.json 等，只读）" — quality-report.md is not a run artifact JSON. So editing it is within the letter of 允许面. And R10 was r1's own recommendation. I'd call this PASS with a note.

7. verification/M2-TA3-B/quality-thresholds.md → ✓

No src/tests/contracts/STATUS/qual-*.json ✓.

Now let me verify calibration.json actual file. Let me read its head and the coverage sections and the gate verdicts + check for other changes. Also check the file's line count.

Let me batch greps and reads.
dsh: reasoning:
calibration.json: file now 527 lines (was 512 + ~15 added). No "NO_DATA" occurrences (no case returns NO_DATA in this calibration) ✓ consistent with the claim that verdicts unchanged (K11/BJ02 = PASS).

Wait — the grep pattern included "NO_DATA" and found none. So the committed JSON has no NO_DATA. Fine.

Now let me verify the numeric distributions are unchanged. The fix diff showed no changes to stats blocks, which strongly implies unchanged. Good.

Now let me check:
1. quality-thresholds.md §5 (lines ~165-175) and §6 R11 and §7 row 10 — read the file.
2. Grep for "determinism-track" across the repo.
3. Verify qual-K11.json regions have "bbox" key.
4. Check main reflog for what advanced past 8996ca55 (to confirm no integration of this branch).

Let me batch.
dsh: reasoning:
Good. §6 R11 exemption exists at quality-thresholds.md:185 → the cross-reference "与 §6 R11 零 region 豁免同口径" resolves ✓.

`--determinism-track` appears ONLY in the thresholds note and the handoff (and not in any runner). So it's a forward-declared flag not yet implemented — grep found it only in thresholds:172 and handoff:92. Let me verify: the grep results for "determinism-track" — in the huge output I see only quality-thresholds.md:172 and doc/handoffs/...:92 mention `--determinism-track`. No runner implements it. So the discriminator is defined on paper but the flag is unimplemented → the "可执行性" is partial: the rule is determinate (provider binding), and the flag is a future requirement. Since the Task's scope is "口径修订" not runner implementation, that's acceptable — but the r1 R9 ask was "补一句判别规则...否则该双轨在实现时仍需二次裁决". The owner's rule leaves "provider id 含 remote 采样服务标识" somewhat open-ended but references deepseek/* as the example. Is that enough to avoid a second decision? Mostly. I'd mark R9 closed with a P3 note: the mapping criterion is heuristic ("provider id 含 remote 采样服务标识") and no runner currently implements `--determinism-track`, so the first qualification run still needs to decide the concrete predicate; suggest registering the flag as runner work item (e.g., in phase2-plan §2.1 or the runner TODO) or wording the rule as a hard predicate (e.g., "provider 绑定为 remote HTTP endpoint"). Hmm — but careful, I shouldn't invent new demands beyond proportionality. r1's ask was "补一句判别规则". They did. I'll grade R9 closed with a minor observation (P4/P3).

Now let me verify:
1. bbox key presence in qual-K11.json regions[].
2. Are there any other changes in the fix commit beyond the 7 files? Can't run git. But the diff provided is the "返修 diff" — the prompt says "7 文件 +223/−46". I can count added/removed lines from the diff to verify +223/−46. Let me count: I can't run a command... but grep can count. Let me use grep patterns to count '^+' and '^-' lines. The grep tool returns matches with line numbers; if >250 matches it saves to a file. Hmm, "Found up to 250 matches; larger results report where the complete list was saved."

Alternative: read the whole diff and count mentally — 570 lines, tedious. Maybe I can use grep with a pattern that matches only added lines, and see the count reported. The tool reports "Found N matches" — let me try `^\+` and `^\-`. If the count exceeds 250, it'll be capped but report where saved. Actually the grep tool says "Returns up to 250 matches; a larger result reports where the complete match list was saved." So the count might be inaccurate. Hmm.

Let me try anyway: pattern `^\+[^+]` for added lines and `^-[^-]` for removed lines. +223 and −46. Added lines likely >250? 223 < 250, so it should report exactly. Removed 46 < 250 ✓.

Let me also verify the worktree files match the diff (post-image). The key check: does the diff's post-image correspond to the worktree files at 8926f49c? I've verified script lines, calibration.json lines, thresholds lines, task lines — all match the diff's post-image ✓. Good.

3. Check whether the worktree has uncommitted changes — can't run git status. However, I could check file mtimes vs commit time... not reliable. NOT_VERIFIED.

Hmm, actually there might be an indirect way: the worktree's index file... too complex. I'll leave NOT_VERIFIED.

4. Verify the calibration.md content matches the diff (I read calibration.md:14 via grep ✓). Let me read the whole calibration.md to verify §1.1/§6.3/§6.6/§6.7/§6.8 line numbers for citations. Wait — the handoff says "calibration.md §1.1 登记该假设与校验" for R1. But the calibration.md I saw has "## 1. 方法（Gate 定义）" with numbered items 1..5 — there's no §1.1! The handoff R1 row says "calibration.md §1.1 登记该假设与校验". Hmm, and the R2 row says "calibration.md §1.4 + §6.6 局限登记". So the handoff references "§1.1" and "§1.4" — does calibration.md have subsections §1.1, §1.4? Let me check. The diff's calibration.md hunk @@ -8,10 +8,10 @@ shows items 1-5 of §1 (no §1.1 heading). So "§1.1" likely means "§1 第 1 条" (item 1 of §1) and "§1.4" = item 4. That's an imprecise citation style but understandable. Hmm — r1's own report used "§1 item4" style. The handoff's "§1.1/§1.4" numbering might be a minor citation convention issue (md uses numbered list, not subsections). P4 at most. Let me check whether calibration.md's §1 has sub-numbering... Let me read calibration.md fully (about 102 lines now).

5. Also verify calibration.md §6 items: the diff shows items 6,7,8 added → 8 limitations total. And "§6.3" referenced in handoff R4 = item 3 ✓.

6. Verify the claim "连续两次重跑 sha256 字节级一致" — NOT_VERIFIED. But note: is there any nondeterminism in the script? `random.Random(SYNTHETIC_SEED)` ✓, dict/set iteration: `sorted(t1)` — t1 is dict[int,...] sorted ✓. `set(t1) != set(t2)` — sets of ints used only for comparison ✓. `set(t1) != ros1` comparison ✓. `first["language"]`, `source_sha256` ✓. JSON keys are insertion-ordered (dict literal) ✓ deterministic. `json.dumps` with ensure_ascii=False, indent=2 ✓. The only environment-dependent value was summaries_dir (now relative if under REPO_ROOT) ✓. So the two-run byte-identity claim is plausible. But wait: is `SUMMARIES_DIR.is_relative_to(REPO_ROOT)` deterministic given the default? Yes.

Hmm, one more: does `Path.relative_to` produce backslashes on Windows? str(PurePath) uses the platform separator → backslashes ✓ consistent with the committed `verification\M2-TA3-B\phase2\summaries`. But re-running in another OS would produce forward slashes → an artifact churn. Repo is Windows-only. Fine.

7. Also verify: does calibration.json contain `"n_dropped_regions": 0` for both cases ✓ (lines 39, 253).

8. Check whether `qual-*.json` were modified: the fix diff doesn't include them ✓. Additional evidence: I can check whether the summaries' region objects have "bbox" keys (to validate the bbox check isn't vacuous).

Let me now do these reads/greps:
- grep '"bbox"' in qual-K11.json (count)
- read calibration.md fully
- count added/removed lines in fix diff

Let me batch.
dsh: reasoning:
bbox exists in regions[] (13 in regions at lines 142-286, and 13 in rerun at 415-559 presumably — actually 26 total = 13 + 13). So the bbox check is non-vacuous today ✓. But the code's `bboxes.get(rid)` returning None if missing → silent pass. Since bbox is present, fine; residual robustness note (P4/P3).

Careful: are those 26 bbox occurrences all inside `regions[]`? Lines 142-286 (13 occurrences, spacing 12 lines each) are probably regions[0..12]. And 415-559 another 13. Are there also `ocr_details` with bbox? If ocr_details also has bbox, the count would be >26. 26 = 13+13 suggests only regions[] (13 per file) have bbox; ocr_details has a different structure. Hmm, r1 read "ocr_details ro=13 bbox x=805 y=564" — maybe ocr_details entries have "x","y","w","h" not "bbox". Either way, regions[] have bbox ✓ (the exact key used by the script is regions[].bbox — let me verify it's inside a regions entry. Line 142 is in the file; line 130ish would be a region start. Let me spot check lines 130-160 of qual-K11.json.

Actually, I should verify that the bbox values used by the script (regions[].bbox) are the same objects compared across runs, and that they match between runs for K11 (the handoff claims 13/13). r1 verified bbox equality for K11 13/13 by comparing. Now with the fix, the script asserts it. I can independently verify by comparing regions[] bbox values in qual-K11.json vs qual-K11.rerun.json — that's a good independent check of the claim "K11 13/13、BJ02 5/5 实测一致" AND that the new assertion won't trip on a re-run.

This matters: if bbox differed for any reading_order, the new fail-closed would raise SystemExit and the committed calibration.json (which exists with results) would be inconsistent — the artifact proves it passed. But an independent check is cheap and valuable: read both regions[] sections and compare.

Let me read qual-K11.json lines 130-300 (regions) and qual-K11.rerun.json corresponding range, and check that the bbox sequences are identical. That's ~170 lines each; doable but heavy. Alternative: grep for a compact representation — I could grep with a pattern capturing region_id + reading_order + bbox lines... grep returns matching lines only, not context. Hmm.

Better: the region entries have "bbox": { "x": .., "y": .., "width"? ... }. Let me read a range to see structure, then decide.

Actually, the calibration.json committed artifact exists and equals the script output (verified for many fields); the script asserts bbox equality; hence bbox equality holds for the data used. That's a sound inference IF the artifact was truly generated by this script (which I can't fully verify without running). But combined with r1's independent verification of 13/13 bbox equality, the claim is well supported. I'll do a spot check of a few reading_orders to be safe — maybe compare the first region and the sfx region (ro=13) between runs.

Let me read qual-K11.json lines 130-200 and qual-K11.rerun.json lines 130-200 (using offset). Note both files may have different layouts.

Actually more efficient: grep for '"reading_order"' and '"x"' lines? Getting complex. Let me just read ranges.

Also, I want to check the region entries' structure to confirm the reading_order values 1..13 and bbox.

Let me do:
1. read qual-K11.json offset 130 limit 90
2. read qual-K11.rerun.json offset 130 limit 90

But wait: are the rerun file's regions at the same line range? r1 said rerun regions around lines 136-300. Likely similar layout. Let me try.

Also I need to count added/removed lines in the fix diff (+223/−46). Let me use grep counts.

Let me batch these.
dsh: reasoning:
Excellent — first 6 regions' bbox identical across runs, region_ids different ✓. Also note `sfx_policy: "skip"`. I'll trust r1's full 13/13 verification.

Note: rerun file has 708 lines vs 709 for run1 — fine.

Now let me verify the +223/−46 claim by counting diff lines. Let me try grep counts.

Also verify: the handoff says the rerun-file line counts; not needed.

Let me count:
- added lines: pattern `^\+[^+]` (excludes +++).
- removed lines: pattern `^-[^-]`.

Also I want to check for any trailing whitespace or whitespace errors: `git diff --check` claim → NOT_VERIFIED, but I can grep for added lines ending with whitespace: pattern `^\+.*[ \t]$`. Let me do that too. Careful: the diff itself contains lines with trailing spaces legitimately? A trailing-whitespace check is exactly what diff --check flags. Let me grep `^\+.* $` (space before EOL) and `^\+.*\t$`.

Let me batch these greps.
dsh: reasoning:
The added-line grep found 212 matches + the removed found 46. The prompt claims +223/−46. The added count is 212, not 223. Hmm — grep may have truncated at some limit? It said "Found 212 matches" for added and 46 for removed. Note earlier the grep tool says "Returns up to 250 matches" — 212 < 250, so not truncated. But my pattern `^\+[^+]` excludes lines that are exactly "+" (empty added lines, i.e. "+"). Let me count those: lines in the diff that are just "+" — I saw several (e.g., diff line 18 "+" alone? Actually line 18 in the first read: "+" at line 18? Let me check: in the first read, line 18 was "+" (empty). Yes: "18: +" — hmm, the read output showed line 18 as `+`. So empty added lines exist. My pattern excluded them.

Also `^-{1}[^-]` excludes lines that are exactly "-" (empty removed lines). The removed count 46 matches the claimed 46 exactly, so probably no empty removed lines. For added: 212 + number of bare "+" lines = 223 → 11 bare "+" lines. Plausible: the handoff section adds blank lines (lines 20, 22, 39, 41 in the diff?). Let me count bare "+" lines with pattern `^\+$`.

Let me verify: pattern `^\+$` should give ~11.

Also verify trailing whitespace in added lines: pattern `^\+.*[ \t]$` (added lines ending with whitespace). But note: the file content lines like `+  ` — rare. Let me grep.

Let me run these two greps.

Also I should double check the "7 文件" claim: 7 diff --git headers ✓.

Now let me think about remaining verification items and findings:

A. R1 — bbox assertion implemented ✓ fail-closed ✓, calibration.md §1 item 1 registers the assumption ✓. Residual: `bboxes.get(rid)` → None==None vacuous pass if bbox key missing in both runs. P3/P4 residual. Also note the assertion compares bbox dicts (x/y/width/height) ✓.

Important extra check: is the bbox assertion actually reachable/effective? Yes, in the loop over sorted(t1) — both a and b exist since sets are equal ✓.

B. R2 — `case_gate_verdict` implemented ✓ (NO_DATA if no non-empty pair). thresholds §5 wording added ✓. calibration.md §1.4 + §6.6 ✓. json method.empty_pair_rule.coverage_precondition ✓ + limitation ✓. Residual: the wording tension ("否则 NO_DATA" vs "全空跑可平凡 PASS，由 §7 兜底"); also NO_DATA's effect on the overall Gate is stated only for region_count=0 ("不阻断整体 Gate"), so for all-empty NO_DATA the effect isn't explicitly stated. Is that a real gap? The sentence "region_count=0 的 case 贡献 0 对 → 同 NO_DATA 口径豁免（与 §6 R11 零 region 豁免同口径），不阻断整体 Gate 但单独登记" — "同 NO_DATA 口径豁免" implies the NO_DATA caliber = 豁免 (exempt). So an all-empty case → NO_DATA → exempt → doesn't block the overall gate, with coverage handled by §7. Read carefully, the text does define it. I'd grade R2 closed, with a P3 note about the em-dash clause possibly reading as "全空跑 = PASS" and the recommendation to make explicit "NO_DATA 不阻断整体 Gate，但必须在报告单独登记" for the all-empty case too (currently that phrasing attaches only to region_count=0). This is a wording refinement, not a blocker.

Actually, hold on. There's a more substantive question the user asks: "NO_DATA 豁免不阻断整体 Gate 的口径是否清晰". I should give a clear answer: mostly clear but with one ambiguity: (i) "可平凡 PASS" vs "NO_DATA" contradiction; (ii) whether NO_DATA blocks the overall gate is stated only via the region_count=0 sentence. I'll present it as a P3 clarity finding.

C. R3 — thresholds §5 region_count=0 → NO_DATA exemption ✓ + ko webtoon 未覆盖 ✓. Cross-ref §6 R11 resolves (quality-thresholds.md:185) ✓. Closed.

D. R4 — 0.05 absolute margin unified in thresholds:168, calibration.md:68, script:571/reasoning:742-744, plus §6.3 four-char counterexample ✓, json limitation 3 ✓. Also need to check thresholds no longer contains "一个字符" anywhere → grep for "一个字符" to confirm zero occurrences. Let me check that too.

E. R5 — median boundary conditioned ✓ in script §4.2, md:69, §6.7, json limitation ✓.

F. R6 — is_nonempty extracted and used in both places ✓; pair_status unified to normalize ✓. BUT docstring says "excludes empty_both AND empty_one_side" while implementation is OR (includes empty_one_side) → new internal contradiction; also changes the aggregate subset semantics vs the pre-fix definition (which excluded empty_one_side). So R6 = partial (functionality done, semantic intent vs implementation mismatch). Severity: P3 — no numeric impact today; but if an empty_one_side pair ever appears, the aggregate "非空" distributions would include a 0.0 pair while the docstring claims exclusion — and note that per the fix's own intent the *case-level* subset is what build_pairs uses. Which one does the artifact report as n_pairs_nonempty? calibration.json n_pairs_nonempty=11 for K11 (13 - 2 empty_both) — under OR semantics, still 11 (no empty_one_side). ✓ unchanged.

Hmm, is it possible the author intended OR and the docstring is just loose? Either way it's a defect to report.

Wait, actually — I should double check the semantics that r1 R6 requested. r1 R6 said: "抽一个 is_nonempty(pair) 供两处共用；similarity 与 pair_status 统一判空基准（建议都用 normalize 后的空串）". r1 didn't specify whether empty_one_side should be included. So the owner chose a definition and documented it as excluding both while implementing inclusion. R6 core ask = done. I'll mark closed-with-residual (P3 new finding N1).

G. R7 — coverage assertion ✓, explicit missing-region_id SystemExit ✓, coverage fields ✓, dropped=0 ✓. Residual: `n_dropped_regions` is structurally always 0 (unreachable non-zero) — vacuous but harmless; and the strict "every region must have translate_detail" is a new hard requirement that could produce a false FATAL for legitimate summaries that omit detail entries for some region types (e.g. SFX). Need to assess: is there evidence that translate_details always covers regions? K11: 13/13 including SFX (ro=13 has an empty detail) ✓, BJ02 5/5 ✓, K01 0/0 ✓. So the convention holds in all three cases. I'll note it as an observation (P4): the strictness is justified by observed convention but should be registered as an assumption ("每个 region 必有一条 translate_detail") — actually the fail-closed direction is safe; if a future run legitimately omits, it fails loudly and the owner decides. Fine. Mark R7 closed.

H. R8 — limitation registered ✓, probe not added with reason ✓. Closed.

I. R9 — discriminator rule added ✓ (provider binding + --determinism-track + fail-closed). Residual: the flag is not implemented anywhere (grep shows only the thresholds note and handoff) → the "可执行性" is at definition level; the concrete predicate "provider id 含 remote 采样服务标识" is still heuristic. Also the rule lives in a supplemental note (尾注) rather than §5 row / phase2-plan — a runner reading phase2-plan §2.1 wouldn't see it. Hmm, that's a reasonable P3: the discriminator should be referenced from phase2-plan §2.1 (the runner-facing doc) or registered as runner work. But phase2-plan modification was in the allowed surface... The fix didn't touch phase2-plan. Note: r1 R9 asked to add the rule "在 §5 或 phase2-plan §2.1". They did §5 (note). So the ask is satisfied. I'll mark closed with a P4 observation about implementation pending.

J. R10 — quality-report.md :189/:199 relation notes ✓. Check the actual line numbers in the file: the diff hunk headers are @@ -186,7 +186,7 @@ and @@ -196,4 +196,4 @@. r1 cited :189 and :199. The changed lines: in hunk 1, the changed line is the "新裁决点（建议）" row — its line number? The hunk starts at 186 with 7 lines of context. The diff context lines are 186,187,188, then the changed line (189) ✓, then 190,191,192. So :189 ✓. Hunk 2 starts at 196 with 4 lines: 196,197,198 context, 199 changed? Wait: the hunk shows:
```
@@ -196,4 +196,4 @@ export 哈希独立复算（§5 口径，runner 之外）：**13 个 OK export
 2. **Task 建议 A（新）**：webtoon 长条漫检测支持...
 3. **Task 建议 B（新）**：导入大图支持...
 4. （登记）SFX→translate 策略的产品入口...
-5. （口径）F4 的 detect 冒烟口径修订 + F5 ...
+5. （口径）...（关系注...）
```
So changed line = 199 ✓ (196,197,198 context + 199). Matches r1's citation. ✓ Closed.

K. R11 — Task AC3 updated with actual revision surface + §1 empty registration ✓ (task:28) ✓. Note: the task AC3 text now mentions "quality-report.md :189/:199 的历史... 已于 r1 返修按 R10 加关系注解除" ✓.

L. R12 — handoff:41 updated to "7/11 非空对" ✓. Let me verify the actual handoff file line = 41. The diff hunk @@ -38,7 +38,7 @@ with context 38,39,40 then changed line 41 ✓.

M. R13 — relative path ✓ in script + json. Residual: uses platform separator (backslash) — if the repo is ever cloned on Linux the path string would be forward-slash (still correct, just different); not a defect. Also `is_relative_to` requires Python ≥3.9 (project uses 3.12) ✓. Closed.

N. R14 — fork_commit: 8996ca55 ✓ confirmed by reflog (e3b7c48d parent = 8996ca55) ✓. Closed.

Q. The handoff's claim "手稿 R1 落点 calibration.md §1.1" — calibration.md has no §1.1 subsection (it's item 1 of §1). Minor citation inaccuracy: P4.

Also handoff R2 row says "calibration.md §1.4 + §6.6" → §1 item 4 is where the coverage precondition text is (line 14) — so "§1.4" means §1 item 4. Slightly loose but decipherable. And R3 row says "calibration.md §1.4/§6.6" ✓ same.

Hmm, the handoff writes "§1.1"/"§1.4" — since calibration.md §1 is a numbered list (1..5), writing "§1.1" is wrong-ish; "§1 第 1 条" would be right. But it's a minor documentation nit. Actually careful: many repo docs use "§1 第 4 条" style? Not important. P4.

Now — one more important verification: the "返修前后 calibration.json 18 对/分布/探针/逐对/verdicts 逐值零差异" claim. The fix diff's calibration.json hunks show ONLY these changes:
- line 5 (summaries_dir)
- line 13 (alignment_key)
- lines 22-23 (emptiness_basis, coverage_precondition)
- lines 35-39 (K11 coverage fields)
- lines ~249-253 (BJ02 coverage fields)
- lines 476 (reasoning)
- lines 482, 485-488 (limitations)
No changes to any pair values, distributions, probes, or gate verdicts ✓. So the zero-difference claim is verified at the diff level (the diff IS the change set; if the artifact had changed numbers they'd appear). ✓ Strong verification.

Wait — is there a possibility that the diff provided is incomplete (path-filtered or trimmed)? The prompt says the fix diff is the 返修 diff (2400b57a→8926f49c). I can cross-check the diff's file set against the branch's two commits... can't run git. But I verified the post-image of every file matches the worktree (script, task, calibration.json, calibration.md, quality-report.md, thresholds, handoff partially). If the diff were truncated/synthetic, matching all 7 post-images would be a big coincidence. Also the diff hunks' pre-images match r1's verified state (e.g., thresholds pre-image has the old text, handoff pre-image has 7/13). Good.

One check I should do: does the post-image of the handoff file match the diff? Let me read the handoff file lines 30-50 and the new r1 section (lines 74-103). Let me also verify the handoff file's total lines.

Also I should verify the fix diff's added/removed counts (+223/−46) to validate the prompt's stated size and the handoff's own claims. 212 + bare "+" lines. Let me grep `^\+$`.

Let me also grep "一个字符" across the repo to confirm R4's unification (no residual "一个字符级余量"). Note: the new text contains "非「一个字符」" — which mentions the phrase in a negation. So a grep for "留一个字符级" should find nothing. Let me grep "一个字符级".

Also: check that "0.05 余量" and "绝对值余量" appear consistently. Done via diff.

Also verify no other thresholds numeric changes: the fix diff showed only the §5 remote row and the F5 note. The mock row and others unchanged ✓. Let me be thorough: does the post-image thresholds file still contain "留 0.05 余量"? The old text had "留 0.05 余量=0.70" in the 依据 cell (line 561) — the new text has "留 **0.05 绝对值余量**=0.70". ✓ replaced.

Let me now also double check one thing about R2: does `case_gate_verdict`'s coverage precondition use `is_nonempty` (OR semantics)? Yes — `any(is_nonempty(p))`. For the coverage precondition, OR is correct: a case with any translated region passes the precondition. But note the subtle interplay: with OR semantics, an empty_one_side pair counts as "non-empty pair" → the all-empty case (all empty_both) still → NO_DATA ✓. Good.

Now, one more potential issue: `case_gate_verdict(pairs)` computes the median/min over ALL pairs (including empty_both=1.0) — same as before ✓.

Let me also consider whether the R2 fix creates an inconsistency between the脚本 and thresholds: thresholds says "非空对 n≥1 方可判定，否则 NO_DATA" ✓ matches the script. And "region_count=0 的 case 贡献 0 对 → 同 NO_DATA 口径豁免" ✓ the script returns NO_DATA for 0 pairs ✓.

Now, the "全空跑由 §7 translate 评分 Gate 兜底" — is §7 row 8 (translate 对白 median ≥3.5 且 ≥80%) able to catch an all-empty translation run? An all-empty translation would score 0 → median <3.5 → FAIL ✓. And row 7 (SFX n≥15) — if n<15 only registered. So the fallback is real for dialogue ✓. Though "该译的没译" — yes, the translate scoring gate evaluates translations, and empty ones would score poorly. Reasonable. Note a nuance: §7 row 8 requires a manual scoring worksheet (人工评分), so the fallback is not automatic — but it is a Gate. Fine.

Now let me check the handoff file for the new section and also verify its claims about "programmatic comparison零差异" — that's an owner claim; I verified structurally via the diff. Also "连续两次重跑 sha256 字节级一致" — the handoff says? The prompt says the owner claims it. The handoff (diff lines 40-44) says "重跑 → ... 逐值一致" and "两次运行输出一致" in the AC1 row. The prompt's claim "连续两次重跑 sha256 字节级一致" may be in the handoff's new section — the diff shows only 3 bullets. Hmm, the prompt's claim list is the owner's summary given by the user. I'll mark it NOT_VERIFIED (no shell) but note the script is deterministic by construction (seeded RNG, sorted iteration, no time/uuid) → high confidence.

Wait, is there truly no timestamp in the output? The payload has no generated_at field ✓ (I read the payload keys: task, measure, calibration_source, method, cases, aggregate, threshold_evaluation, limitations, directional_disclaimer). calibration.md header has a hardcoded date "2026-10-01" (from the script's docstring? let me check render_markdown's header line). If the date is hardcoded, deterministic ✓. Let me check line ~439-470 for the header. The md line 1-7 includes "日期 2026-10-01" — need to see if it's hardcoded or from datetime.now(). If from datetime.now(), two runs on different days would differ → the "byte-identical" claim would be date-dependent. Let me check the render_markdown header.

Let me read script lines 439-530 to inspect the md rendering header and §1/§4 text (also to verify line numbers for citations).

Let me batch: read script 443-500; grep '^\+$' count; grep "一个字符级" repo-wide; read handoff 74-105.

Actually the handoff file: I can read lines 60-105 to see the new section (the diff showed it up to line 44 of the diff = handoff line ~103).

Let me batch 3 calls.
dsh: reasoning:
- Added lines: 212 + 11 bare "+" = 223 ✓ matches the prompt's +223. Removed 46 ✓. Total diff "+223/−46" verified.

- "一个字符级" now appears only in the handoff's R4 row (quoting the old wording being fixed) → the old wording is gone from thresholds/calibration.md/script ✓ R4 unification verified. Note also the script/md now say "非「一个字符」" which my grep didn't match (it searched "一个字符级|留一个字符") — correct.

- The md header date "2026-10-01" is hardcoded in render_markdown (line 448) ✓ → deterministic.

Now let me verify the handoff file content at tip (post-image) — read lines 30-50 and 74-105. Also check the handoff's total line count and that the "§1.1"/"§1.4" citations and other claims match.

Also: I noticed the handoff R2 row claims the relation sentence is written into thresholds §5 as 「全空跑可 PASS 相似度 Gate，由 §7 translate 评分 Gate 兜底」— the actual thresholds text says "全空跑（两次 run 译文全空）在相似度口径下可平凡 PASS，由 §7 translate 评分 Gate 兜底". ✓ closely matches.

Let me read the handoff.

Also, one more verification for R1: the handoff claims "K11 13/13、BJ02 5/5 实测一致". I verified K11 ro 1-6 identical; r1 verified 13/13. For BJ02 let me spot check 5 regions bbox across runs — cheap and strengthens R1's closure. Let me read qual-BJ02.json and qual-BJ02.rerun.json regions.

Let me batch: read handoff 74-105; read handoff 30-50; grep bbox with context in BJ02 files... simpler: read the regions sections. Let me find the regions section line numbers via grep "regions" in both? Let me grep '"bbox"' in qual-BJ02.json to get line numbers, then read the range.

Let me do that.
dsh: reasoning:
Note: qual-BJ02.json appears to be a compact file where regions are on lines 141-193 with bbox at 145,157,169,181,193. And there's another structure at 239-290 that also has region_id + reading_order + bbox — maybe that's the "ocr_details" section (which also carries reading_order and bbox). Interesting: BJ02's regions and ocr_details both have region_id/reading_order/bbox. Note the script uses `summary["regions"]` and `summary["translate_details"]` ✓ (line 152/156). Good.

Now let me verify BJ02 bbox equality across runs for the 5 regions. Let me read qual-BJ02.json lines 136-200 and qual-BJ02.rerun.json lines 136-200.

Hmm — wait. This is important! For BJ02, both `regions[]` and some other list (ocr_details?) have bbox. If the script's regions[] entries have bbox ✓ (lines 141-193 in the regions list). Fine.

Let me verify BJ02 rerun bbox matches. Read both.

Also: I realize I should double-check one thing for R7: the assertion `set(t1) == ros1`. For BJ02, regions[] has 5 entries with reading_order 1..5 ✓ and translate_details 5 entries ✓.

But hold on — a critical question: does K01.rerun.json (region_count=0) have regions[] = [] → ros = set() and translate_details = [] → t = {} → set(t1) == ros1 = set() ✓ no FATAL → pairs=[] → NO_DATA ✓. Consistent with the codebase claim. And K01 isn't in CALIBRATION_CASES anyway.

Let me read BJ02 regions in both files.
dsh: reasoning:
BJ02 bbox: 5/5 identical across runs, region_ids all different ✓. So the claim "K11 13/13、BJ02 5/5 实测一致" is verified (I verified K11 ro1-6 + r1 verified 13/13; BJ02 5/5).

Now, remaining checks:
1. Whether quality-report.md post-image matches the diff — I saw the grep result earlier (line 189 and 199 in the repo now have the relation notes? The grep output earlier showed the quality-report.md lines... actually the earlier grep for "R11" showed line 15 and 21 only. Let me directly read quality-report.md lines 185-200 to confirm the relation notes are in place at :189 and :199.

2. Verify the worktree has no uncommitted modifications — can't (no shell). NOT_VERIFIED.

3. Check whether the fix commit touched anything else (e.g., phase2-plan) — the provided diff has 7 files; phase2-plan absent. The prompt says "7 文件 +223/−46" ✓ consistent with the diff I read. ✓

4. Also verify: main advanced to 1d477b35 — no impact on this review, but might be worth noting that the integration base moved (the integrator should merge/rebase). Let me check main's reflog tail to see what advanced. Cheap: grep the main logs/HEAD for 1d477b35 and 8996ca55 to see transitions. Let me read the last ~10 lines of main reflog. I don't know length; earlier r1 said line 727 was 8e0de8d0→8996ca55. So the file has ~730+ lines. Let me read with offset 720 limit 30.

Actually is this necessary? It's relevant for "推荐下一步" (integration). If main moved, the integrator should rebase/verify. Let me check quickly.

5. One more consideration for the "回潮检查": the user asked "thresholds 其他阈值数值零改动". Verified via the fix diff (only §5 remote row + note). But I should also confirm that this commit didn't revert the earlier e3b7c48d changes — no, the post-image matches e3b7c48d's changes plus the new ones ✓.

6. R2's thresholds §7 relationship: R2's relation sentence says "由 §7 translate 评分 Gate 兜底". §7 row 8 is translate 对白 中位数 ≥3.5 且 ≥80%. Does the thresholds text specify "§7" generically? It says "由 §7 translate 评分 Gate 兜底" — §7 is the 阈值提案总表; rows 7 (SFX) and 8 (对白) are the translate scoring gates. The reference is a bit loose (row-level would be better: §7 行 7/8), and r1's R2 recommendation said "由 §7 第 8 行 translate 评分 Gate 兜底". The owner wrote "§7 translate 评分 Gate" (without row number). Minor imprecision: P4. Also, row 7 (SFX) only fires at n≥15, so SFX coverage isn't fully covered by the fallback — but the disclosure says "翻译覆盖度由 §7 translate 评分 Gate 兜底" which for SFX is conditional. Hmm, is that a substantive gap? The all-empty blind spot concerns translations; the §7 fallback catches dialogue (row 8) but SFX only if n≥15 evaluated. It's a nuance; the limitation says coverage is enforced by §7. I could note it as P4 (precise row reference + note that SFX row is n≥15-conditional).

Let me now check the quality-report.md lines 185-200, and main reflog tail.

Then I'll consider whether there are any other new issues:

Potential new issues to weigh:
N1 (P3): is_nonempty docstring/implementation mismatch (OR vs "excludes both") + aggregate subset semantics changed vs pre-fix definition, undisclosed. — definitely report.

N2 (P3): bbox cross-check vacuous if `bbox` key absent (None == None). Recommend `a["bbox"] is None or ...` guard. — report as P3/P4. Severity: today non-vacuous (verified). It's a residual fail-open in the new guard. I'd call it P3 (low) — actually since it's a guard whose purpose is fail-closed detection, a silent-pass hole matters; but bbox is present in both summaries and the schema appears to always include it. P4? Let me weigh: The r1 R1 finding was about a missing guard → the fix added one that can be vacuous in a specific data-degradation scenario. If regions[] lacked bbox, the whole geometric check silently does nothing → the R1 hole reopens invisibly. I'd call it P3 (residual, non-blocking, cheap fix).

N3 (P3): thresholds §5 NO_DATA/PASS wording tension (all-empty described as both "否则 NO_DATA" and "可平凡 PASS ... 兜底"), and the "不阻断整体 Gate" statement attaches only to the region_count=0 case. — report as clarity item.

N4 (P4): handoff citations "§1.1"/"§1.4" don't exist as headings (calibration.md §1 items); thresholds fallback reference "§7" without row 7/8.

N5 (P4): `n_dropped_regions` structurally always 0 (unreachable non-zero due to the preceding FATAL) — bookkeeping field can't ever show a drop; consider either removing or documenting it as an invariant. Non-blocking.

N6 (P4): quality-report.md edit is inside the literal allowed path glob but outside the parenthetical narrowing ("thresholds/plan 修订+本 Task 产物"); r1 R10 requested it, so acceptable — recommend the integrator record the scope extension. Actually I'd frame it as: 允许面判定=通过（字面），但括号意图未覆盖，需集成方确认。P4.

N7 (P4): `--determinism-track` not implemented in any runner (grep: only thresholds note + handoff). The rule's predicate "provider id 含 remote 采样服务标识" is qualitative. Register as runner work item.

N8: docs claim "与返修前 JSON 程序化对比零差异" — verified structurally via diff (no numeric hunks) ✓. Good, this is a positive.

N9: The R2 precondition applies to the case-level verdict but the aggregate/overall Gate verdict: is there an aggregate Gate verdict in the artifact? `threshold_evaluation.observed = {K11: PASS, BJ02: PASS}` — there's no single "overall" verdict field. The overall Gate is the union of per-case verdicts. With NO_DATA semantics, the reader must know NO_DATA doesn't block. This is exactly the clarity issue (N3). Note the artifact has no explicit overall verdict — pre-existing design. Fine.

Also potential: does `case_gate_verdict` docstring/behavior for the K01 zero-pair case match thresholds? Yes.

One more: is there a risk that `is_nonempty` being OR-based breaks the coverage precondition semantics in an undesired way? For an "all-empty" run, no pair has any non-empty side → NO_DATA ✓ correct. For a run where exactly one region has a translation → precondition satisfied → gate evaluates → median over all pairs mostly 1.0 → PASS. Hmm! Interesting: the coverage precondition is only n≥1 non-empty pair; a rerun where 12/13 regions are empty in both runs and 1 region has a translation would PASS (median 1.0). So the coverage precondition is minimal — it closes only the *completely* empty case. The thresholds text says "非空对 n≥1 方可判定" — matching the implementation ✓. Is that adequate for the R2 ask? r1 recommended either a coverage-ratio precondition or the relation sentence. The owner did the minimal n≥1 + the relation sentence + limitation. The limitation text says "an all-empty rerun (provider down) ... requires >=1 non-empty pair else NO_DATA; translation COVERAGE is enforced by the §7 translate scoring gate, not here". So partial coverage gaps are explicitly delegated to §7 ✓ disclosed. Acceptable. I'll note in the review that the precondition is deliberately minimal (only the fully-empty case) with partial-coverage delegated to §7 — and that this is disclosed. Good, no finding, or a P4 note.

Now let me check quality-report.md lines around 185-200 and main reflog.

Also: I should double check the claim "qual-*.json 零改动" — the fix diff has no qual files ✓. And also verify there are no *other* modified files in the worktree relative to the commit... can't. But the prompt says the fix diff is 7 files. Also I can check whether the worktree contains any obviously-new untracked file related to the fix... can't glob for untracked. Hmm, glob would list files regardless of git status. The prompt's claim "porcelain 干净" is NOT_VERIFIED.

Let me do the last two checks.
dsh: reasoning:
main = 1d477b35 = after merging M2-DETECT-WEBTOON-DIAG and closing it. The CALIB branch is not merged ✓ (integration pending). Note the reflog: "STATUS active line -> batch progress (DIAG done; ALLOC/CALIB r2 pending; SFX-ENTRY r1 pending)". So STATUS tracks CALIB as "r2 pending" — good, the plan/STATUS registration gap from r1 R? (E5) may have been resolved by the orchestrator. Let me check: r1's E5 said REBASELINE_PLAN has no CALIB row and STATUS has no mention. Now the close commit says STATUS active line → batch progress (…CALIB r2 pending) and PLAN +4 batch nodes. So the orchestrator added PLAN/STATUS rows. Let me verify with a grep for "CALIB" in doc/STATUS.md and doc/REBASELINE_PLAN.md in the worktree.

Wait — the worktree is at 8926f49c which is based on 8996ca55, so its STATUS/REBASELINE_PLAN are pre-1d477b35 (they don't include those updates). Hmm: the worktree's doc/STATUS.md is at the fork point (8996ca55). The main branch's STATUS at 1d477b35 includes the batch progress. So checking the worktree's STATUS isn't the right check for the current main state. I can read the main repo's doc/STATUS.md directly (G:/CODEX/New Manga/doc/STATUS.md) — the main worktree checkout at 1d477b35. Let me grep it for CALIB.

This matters for the "集成方闭合清单"/推荐下一步: if STATUS/PLAN registration is already resolved, that item is closed. Let me check.

Also worth noting: main advanced past the fork → integration will need a merge (no conflicts expected: the CALIB branch touches thresholds §5 + quality-report + its own dirs; the DIAG merge may have touched thresholds/plan? The DIAG close commit says "PLAN mermaid +4 batch nodes ... + inventory row" and "STATUS active line" — it touched doc/STATUS.md and doc/REBASELINE_PLAN.md, not verification/M2-TA3-B/**. So merge should be clean. But note: does the CALIB branch's Task file update conflict with main's? No.

Let me grep main's doc/STATUS.md and doc/REBASELINE_PLAN.md for CALIB.
dsh: reasoning:
Confirmed: the orchestrator has registered CALIB in main's STATUS.md:14 ("M2-QUAL-DETERM-CALIB（同 @8926f49c 复跑逐值一致，r2 复核中）") and REBASELINE_PLAN.md:173 (mermaid node "M2-QUAL-DETERM-CALIB F5 确定性校准 · O:ZCode（r2 复核中）"). So r1's E5 integration-side item (缺乏 PLAN/STATUS 登记) is now closed on main. 

Interesting: the STATUS line says "M2-QUAL-DETERM-CALIB（同 @`8926f49c` 复跑逐值一致，r2 复核中）" — "复跑逐值一致" is recorded by the orchestrator (they apparently re-ran the script themselves? or they're quoting the owner's claim). Hmm, "同 @8926f49c 复跑逐值一致" — this appears to be the orchestrator's own verification. That's external to my review but supports the re-run claim. I can cite it as corroboration but it's still not my own run → NOT_VERIFIED as a first-hand item, with note that the integrator recorded a re-run.

Now let me also check whether the earlier r1 mentions in STATUS ("此前：...") mention CALIB r1 approved_with_conditions. Not necessary.

One more check for completeness: REBASELINE_PLAN line 173 node says "r2 复核中" — consistent.

Now, are there any other things to verify?

Let me reconsider the "回潮检查" more carefully:
1. 7 files, all within allowed surface ✓ (quality-report.md with the parenthetical caveat).
2. qual-*.json zero appearance ✓ (not in the fix diff).
3. thresholds other numeric values unchanged ✓.

I should also verify that the fix commit didn't touch phase2-plan (it didn't) — that's fine since phase2-plan was already updated in the previous commit and R9's rule went to thresholds.

One more possible check: did the fix accidentally touch `doc/STATUS.md`? Not in the diff ✓.

Now let me think about whether to raise any P1/P2 findings. The owner claims all R1-R14 closed. My assessment:

- R1: closed (with residual P3: bbox None vacuous pass).
- R2: closed (with residual P3: wording tension re NO_DATA vs PASS / non-blocking scope).
- R3: closed.
- R4: closed (verified unification).
- R5: closed.
- R6: closed-with-defect (P3 N1: is_nonempty docstring contradicts implementation; aggregate subset semantics changed from the pre-fix strict definition without disclosure).
- R7: closed (with P4: n_dropped_regions structurally always 0; strict-coverage assumption).
- R8: closed.
- R9: closed (with P4: flag unimplemented; predicate qualitative; the rule lives in a 尾注 not referenced from phase2-plan §2.1/runner).
- R10: closed (allowed-surface note).
- R11: closed.
- R12: closed.
- R13: closed.
- R14: closed (reflog verified).

No P0/P1/P2? Let me weigh N1 (is_nonempty). Is it P2? It's an internal contradiction in a delivered Gate-definition artifact + a silent semantic change to the aggregate non-empty denominator (which is reported in calibration.json/md tables). Impact today: zero. Future: if an empty_one_side pair appears, the aggregate "非空" row would include a 0.0 similarity pair — the reported "非空" distribution wouldn't match the documented definition, and a reader/reporter could misread. Also — and this is more interesting — does the case-level n_pairs_nonempty (used in the md table as "非空对") match the case-level definition used by the Gate precondition? Yes, both use is_nonempty. So the Gate precondition and the reported "非空对" column agree ✓ — which is arguably the *right* unification (r1's ask). The only defect is the docstring text + the undisclosed change of the aggregate definition. I'd rate P3.

Hmm wait, actually, let me reconsider: which definition did the pre-fix *case-level* use? `nonempty = [p for p in pairs if p["status"] not in ("empty_both",)]` → includes empty_one_side. The pre-fix aggregate excluded both. So the fix aligned the aggregate to the case-level (permissive). The reported aggregate rows in the md ("合并 ... 非空" n=16) would, under an empty_one_side scenario, include a 0.0 → median drops. Which is arguably the safer/conservative direction and consistent with the per-case column. So the substance is fine; only the docstring is wrong. P3 (doc defect). Good — but I must flag it clearly since it's a NEW defect introduced in this fix commit and it directly concerns R6's closure ("判空基准统一" claim).

Hmm, one more angle on N1: the handoff R6 row claims "抽 is_nonempty(pair) 供 case 级（build_pairs）与 aggregate（main）非空子集共用；pair_status 判空基准与 similarity 统一为 normalize 后空串". Both true. It doesn't claim the exclusion semantics. So the handoff doesn't overclaim; the code's docstring does. OK.

Another check on N1: is there any chance `is_nonempty` is actually intended AND the `or` is deliberate for a different reason? If the intent were "exclude empty_one_side", the implementation would be wrong in a fail-open-ish direction for the aggregate. But since the case-level pre-fix definition included them, and the docstring says excludes... The safest framing: "docstring 与实现不一致（实现为 OR=仅排除双方空，docstring 声称排除双方空与单方空）；无论哪个是意图，二者必须对齐，并明确 aggregate 非空口径相对返修前的变化。" ✓.

Now, is there any *fail-open* residual I should elevate? Let me think about the R2 closure robustness: `case_gate_verdict` requires ≥1 non-empty pair. OK.

What about R1's bbox guard interplay with `translations_by_reading_order`: bbox comes from regions[] via region_id; since rid is validated to exist in `order` (regions), bboxes also has it ✓. So `bboxes.get(rid)` is not None *unless the region entry lacks a bbox key*. In the observed schema every region has bbox. So N2 is a hypothetical schema-degradation hole. P4? I'll put it as P3-low but mark as "可选加固". Hmm. The user asked me to focus on "R1 bbox 断言实现". I should report it: implemented correctly in structure, fail-closed with SystemExit ✓, but has a vacuous-pass edge if `bbox` is missing/None on both sides. Since `r.get("bbox")` deliberately tolerates absence, the guard can silently no-op. Recommend `if a["bbox"] is None or a["bbox"] != b["bbox"]`. I'll rate P3 (residual, additive).

Also — should I verify that the bbox dicts are *equal* including key order? Python dict equality is order-insensitive ✓. And JSON objects → dicts ✓. Good.

Another possible issue: the bbox cross-check asserts *exact* geometric identity. If a detector upgrade changed integer rounding by 1px in future runs, the calibration script would FATAL rather than warn. That's the intended fail-closed design for calibration (not for the Gate runner). Note: this assertion lives in the calibration script, not in the future Gate runner. The thresholds §5 says "两 run 逐 reading_order bbox 交叉校验，不一致 fail-closed——CALIB r1 R1" — presenting it as part of the Gate definition. But the actual Gate runner (qualification runner) doesn't implement it (it's a documented requirement). Hmm: the thresholds row now promises a bbox cross-check as part of the Gate. The `--determinism-track` flag likewise. So both are forward requirements on the runner — that's fine as a spec, but the integrator/runner owner must implement them. Worth noting in the recommendation: the qualification runner (M2-TA3-B runner) must be updated to implement (a) the bbox cross-check, (b) the coverage precondition → NO_DATA, (c) `--determinism-track`. Currently the runner (experiments/M2-TA3-B/run_qualification.py / verify_exports.py) has no such logic — let me check quickly whether run_qualification.py already implements a determinism gate. r1 didn't discuss. Let me grep run_qualification.py for determinism/hash gate to see if the authoritative thresholds §5 change requires code changes there. This is a genuinely valuable integration finding: the thresholds now define a Gate that the existing runner does not implement (it still does export hash comparison?). Let me check.

Let me grep experiments/M2-TA3-B/run_qualification.py for "sha256"/"deterministic"/"hash".
dsh: reasoning:
Confirmed: the qualification runner (experiments/M2-TA3-B/run_qualification.py) still implements ONLY the sha256 bitwise rerun comparison (`--rerun-check`, rerun report with sha256_first/second, and at line 851 fails if not all match). It does NOT implement the new double-track / similarity Gate / coverage precondition / bbox cross-check / `--determinism-track`. phase2-plan §2.1 and §4 step 5 now describe the new declared口径 (the plan says "改为 ... 相似度 Gate"), but the runner code hasn't been updated (and can't be — experiments/M2-TA3-B/** is in the allowed surface "thresholds/plan 修订", but the runner code is arguably out of this Task's scope since the Task is about口径 revision + calibration).

Is this a finding? The thresholds §5 now says "remote 翻译链 ... 满足 median ≥0.95 且 min ≥0.70 方为 PASS" and the runner at line 851 does `if not all(item["match"] for item in report["rerun"]): ...` → it would FAIL a remote-translation rerun on export sha mismatch (exactly the old口径), i.e. the runner as-implemented contradicts the newly修订 authoritative口径. Back in TA3-B2, the runner's rerun behavior produced the K11 MISMATCH → the old Gate would FAIL. With the new口径, that same K11 export mismatch should NOT FAIL the determinism gate (the similarity gate PASSes). So there's an implementation-vs-口径 divergence: the runner must be updated before the new口径 is operative. This is a genuinely relevant integration item (and r1's R9 asked for the discriminator precisely because "该双轨在实现时仍需二次裁决").

Severity: This is not a defect of the owner's delivery (the Task scope = 口径修订 + 校准, and the runner update is a separate work item). But it MUST be registered as a follow-up, otherwise anyone running `--rerun-check` today would apply the superseded口径 and get a FAIL contradicting the new thresholds. Also the runner line 851's fail-closed on hash mismatch is still the operative behavior. So I should raise this as an integration item (P3, "口径—实现落差"): explicitly register the runner implementation work (bbox cross-check, coverage precondition, --determinism-track, similarity Gate, dual-track selection) as a follow-up Task/step, e.g., in phase2-plan §4 or a proposed Task row (the PLAN has "CALIB ... proposed" nodes; the orchestrator can add a follow-up).

Hmm, is this within the review's scope? The review asks about R9's "可执行性" (executability) of the dual-track rule. The answer: the rule is now determinate on paper, but the runner that must execute it still implements only the old single-track hash口径, and no work item registers that gap. That's exactly the kind of finding a reviewer should surface. I'll include it as a P3 (not blocking the口径 landing, but blocking the口径 becoming operative; needs a registered follow-up).

Let me verify runner line ~845-855 to quote precisely. Let me read run_qualification.py lines 786-860.

Also I should double check whether the runner's fail-closed is conditional on track. Let me read.

Let me also check whether phase2-plan §4 step 5 or §2.1 mentions that the runner code needs updating (i.e., is the gap registered?). phase2-plan §4 step 5 says "3 case 确定性复跑 | 复跑哈希对照 + 译文相似度 Gate 计算（F5 双轨口径...）" — it describes the step as computing both. So the plan acknowledges the runner must compute the similarity gate (a step, not implemented yet). Actually, is the runner step executed by a human following the plan with the calibration script? Partially. So the gap is registered at the plan level ("步骤 5 ... 复跑哈希对照 + 译文相似度 Gate 计算") ✓ — the plan does say the step includes the similarity Gate. So the follow-up is at least visible in the plan. But the runner code's actual behavior (fail on hash mismatch for remote) is not aligned. I'll frame the finding precisely: the plan text now requires the similarity Gate, but `run_qualification.py:851` still fail-closes on export sha mismatch — so unless the runner is updated, executing the documented step 5 yields a contradiction. Register as follow-up.

Let me read the runner's relevant lines to be accurate.

Also let me check verify_exports.py? Not needed.

Let me read run_qualification.py 786-860.
dsh: reasoning:
Confirmed: run_qualification.py:851 fail-closes on export sha mismatch for ALL rerun cases (no track discrimination). So the runner currently enforces the superseded byte-equality口径 for the remote chain. With the new thresholds §5 dual-track口径, running `--rerun-check BJ02,K01,K11` would still FAIL on K11 (MISMATCH) — contradicting the new authoritative口径. Also note: line 813 `match = bool(sha_first) and sha_first == sha_second` — K01 (region_count=0) would have export?? K01 has no export presumably → match=False → failure count. Hmm, that's the pre-existing behavior (the top-level Gate counts it as a failure). Not our concern.

This is a legitimate integration finding (P3): the authoritative口径 now declares a Gate that the operative runner does not implement; the runner must be updated (or the Task must register the follow-up explicitly). Where would it be registered? phase2-plan §4 step 5 says "复跑哈希对照 + 译文相似度 Gate 计算" — the plan's step text does include the similarity Gate computation, so it's partially registered. But `run_qualification.py` behavior isn't flagged as needing change. I'll report it as a P3 integration item with a concrete recommendation (follow-up work item for the runner: track selection, similarity gate, coverage precondition/NO_DATA, bbox cross-check; and register it in PLAN as a proposed node or in phase2-plan §2.1 explicitly).

Now let me also double check the claim in thresholds §5 that "全空跑...由 §7 translate 评分 Gate 兜底" — is §7 row 8 the dialogue scoring gate — yes (line 203). And row 7 (SFX) requires n≥15. Fine, P4-level precision note.

Now let me assemble the review. Before that, let me consider a few more possible checks:

1. Verify no "qual-*.json" in the fix diff ✓ (7 files listed).
2. Verify thresholds numeric values unchanged ✓.
3. Verify that the fix didn't modify phase2-plan (absent) ✓.
4. Verify the fix's calibration.json numeric identity claim ✓ (diff has no numeric hunks).

5. One more: the owner claims "连续两次重跑 sha256 字节级一致". Can I find supporting evidence? The orchestrator's STATUS line says "同 @8926f49c 复跑逐值一致" (the orchestrator re-ran and compared). That's second-hand corroboration. I'll cite it as corroboration but keep NOT_VERIFIED for first-hand.

Hmm, "复跑逐值一致" from the orchestrator might refer to comparing values, not byte-identity. Fine.

6. Also should I verify the calibration.md/json for the "0.05 绝对值余量" vs "min ≥ 0.7" consistency: md says "min ≥ 0.7" in §4 header while thresholds says 0.70, PROPOSED_GATE min_min=0.70. Cosmetic (P4).

7. The md §2 table row for K11 raw says "raw(全部) 相同对 6 浮动对 7" — and calibration.json raw_all_pairs n_identical=6, n_variant=7 ✓.

8. Any new issue in the handoff's r1 record: "R1 ... calibration.md §1.1 登记该假设" → calibration.md has no §1.1 subsection (P4 citation nit). Also "R2 ... calibration.md §1.4 + §6.6". I'll note as P4.

9. Also the handoff table's "落点" for R10 says the file is within the allowed surface ✓.

10. One more possible item: the handoff's claim "JSON 预期结构差异仅三类（均为返修要求）：summaries_dir 相对化（R13）、case 级 coverage 字段（R7）、method/limitations 文本增强（R1/R2/R4/R5/R8）" — verified against the diff: the changes are exactly: summaries_dir (R13), alignment_key text (R1/R7), empty_pair_rule additions (R6/R2), coverage fields (R7), reasoning (R4/R5/R2), limitations (R4/R5/R8 + R2/R3). The handoff's list omits the empty_pair_rule additions (R6) and the reasoning field. "三类" is a slight undercount (they'd count method text as one class → alignment_key + empty_pair_rule additions are within "method 文本增强" ✓, and reasoning is within...? Reasoning is under threshold_evaluation, not method. The list says "method/limitations 文本增强" — reasoning isn't in either. Minor imprecision: the reasoning string (R4/R5/R2) is also a text enhancement but sits under threshold_evaluation; the third class should be "method/limitations/reasoning 文本增强". P4 nit. Worth mentioning? It's a trivial doc precision issue about the claim "仅三类". I'll fold it into a minor note. Actually this matters a bit for the "零差异" claim: the claim says the diff is limited to three classes, and I verified no numeric churn. I'll mention the omission as P4.

Now, what's my final verdict? All 4 P2 conditions closed with residual P3s (none blocking). The r1 conditions R1-R4 are substantively closed. R5-R14 closed. New residuals: N1 (is_nonempty doc/internal semantics), N2 (bbox None vacuous pass), N3 (NO_DATA wording), plus P4s and the runner-implementation gap (P3).

Verdict: **approved**（可集成）— with the residuals registered as non-blocking follow-ups? Or approved_with_conditions? The user asks: "终局 verdict：approved（可集成）/ changes_requested". So I must choose one of two. Given:
- No P0/P1/P2 remaining.
- All r1 conditions closed.
- Residuals are P3/P4 (documentation precision, minor code hardening, runner follow-up).

The instruction offers "approved（可集成）" vs "changes_requested". I should choose **approved** with explicit non-blocking residuals (N1-N5) recommended to be handled by the integrator or a follow-up. But wait — N1 is a code/docstring defect in the delivered artifact; is it blocking? It's a wrong docstring + an undisclosed semantic change to a reported subset. It doesn't affect any number or the Gate's operative semantics (the Gate precondition uses the same predicate as the reported 非空 column). Since the task's deliverable is a calibration artifact + threshold口径, and the docstring is internal to the script while the *artifact* documents "emptiness_basis" correctly ("a side is empty iff its §0-normalized form is ''") — hmm, does the JSON's `emptiness_basis` claim exclusion of empty_one_side? It says "a side is empty iff its §0-normalized form is ''" — that's the basis, consistent with the code. It doesn't state whether non-empty pairs exclude one-side-empty. So the artifact doesn't misstate it; only the script's docstring does. That's a P3 internal-doc defect, non-blocking for integration.

Hmm, but I want to be careful about a possibly bigger issue: does the OR semantics change any *reported* number in the artifact? No (no empty_one_side pairs). Does it change the thresholds-documented Gate? The thresholds say "非空对 n≥1 方可判定，否则 NO_DATA" — with OR semantics, "非空对" = a pair where at least one side is non-empty. Under an empty_one_side pair, the pair counts as non-empty → precondition satisfied. That's the sensible reading ✓. So the implementation matches the thresholds text; only the script docstring conflicts. Good: N1 = P3 doc defect.

N2 (bbox None) — P3 hardening, non-blocking.
N3 (NO_DATA wording) — P3 clarity.
N4/N5/N6 — P4.
Runner gap — P3 integration follow-up (needs registration, not this delivery's fault).

So verdict = **approved（可集成）**, with residuals to be closed by the integrator (documentation wording) or registered as follow-ups (runner implementation). Since the user asked me to choose approved/changes_requested, and the r1 conditions are all closed with no new P0-P2, approved is proportionate and consistent with repo precedent (r2 usually approves when r1 conditions are closed). I'll note that N1-N3 are P3 and recommend the integrator fold them into the integration commit or a follow-up, explicitly stating they do not block integration.

Hmm, but let me double-check one thing before approving: is there any chance the R1 bbox assertion *breaks* the rerun claim? No — bbox verified identical.

And is there a chance the R7 coverage assertion is too strict for BJ02/K11? Verified 13/13, 5/5 ✓.

One more: does `translations_by_reading_order` handle `bbox` when regions have "bbox" but the key is nested differently? Verified ✓.

Also the R7 assertion uses `set(t1) != ros1` where ros1 is built from `first["regions"]` — note `ros1` includes regions of ANY type including SFX; K11 ro=13 SFX has a translate_detail ✓.

Also: what if `regions` key is missing entirely (region_count=0 case, K01)? The code does `{r["reading_order"] for r in first["regions"]}` — if "regions" key absent → KeyError. For K01, r1 verified `regions: []` exists ✓ (empty list). So fine.

Let me do a final check on K01's summary structure to make sure `regions: []` exists (so the new strict code wouldn't crash on a 0-region case). r1 said "K01 两 run 均 region_count=0、regions=[]、translate_details=[]（我直读 .rerun.json:52）". I'll trust that, but a quick grep on qual-K01.json for '"regions"' would confirm. Let me do it — cheap and it validates R3's premise.

Also let me confirm K01 is not in CALIBRATION_CASES ✓ (line 77: ["K11", "BJ02"]).

Let me grep K01 for 'regions' and 'translate_details'.

Also, one more: verify the worktree file count/quality-report.md line total 199 ✓ matches the diff post-image (hunk @@ -196,4 +196,4 @@ with the file ending at 199) ✓.

Let me run the K01 check and then write the review. I also want to double check the thresholds §5 statement "region_count=0 的 case 贡献 0 对 → 同 NO_DATA 口径豁免（与 §6 R11 零 region 豁免同口径）" — §6 R11 exemption is about 产物存在性 (四件齐豁免), which is a different Gate (§6 全链). Saying "同 NO_DATA 口径豁免" conflates two different豁免 concepts (one is a §6 product-existence exemption, the other is a §5 determinism NO_DATA). Hmm, the thresholds says "与 §6 R11 零 region 豁免同口径" — meaning "the same caliber as the R11 zero-region exemption" (i.e., aligned with the §1/§6 R11 exemption for zero-region cases). It's a reasonable cross-reference (both say: zero-region cases are protocol outcomes, exempt, not FAIL). Acceptable. But note the §6 R11 exemption is about "OCR/translate 明细存在"; the §5 use is about the determinism Gate verdict. The phrasing "同口径" is loose but understandable. P4 nit, probably not worth reporting. I'll skip or mention briefly.

Let me do the K01 grep and then compose.
dsh: reasoning:
K01.rerun.json: regions: [] (line 73) and translate_details: [] (line 76) ✓ → the new strict coverage code handles 0-region cases fine (set() == set()) → NO_DATA.

The trailing-whitespace grep found 28 matches — but these are context lines (lines starting with a space) in the diff, where the trailing whitespace is part of the *unified diff* itself? No wait — the pattern `[ \t]+$` matches lines ending with whitespace, including context lines that are just " " (a single space prefix for an empty context line). Those are lines like " " (space + empty content) which is a normal empty context line in a diff, not trailing whitespace in the file. My pattern also matched bare context lines " " (line 58, 64, etc.). It matched 28 lines, all of which appear to be just context lines with a single space (the diff's empty context lines). But careful: line 570 shows "  " (2 spaces?) — that's the end of the file maybe. Let me check whether any *added* line ends with whitespace: use pattern `^\+.*[ \t]$`. Let me run that to be precise. This matters for validating the "diff --check EXIT=0" claim (which I can't run, but I can approximate for added lines).

Note `git diff --check` flags trailing whitespace on added lines and space-before-tab etc. So let me grep `^\+.* $` and `^\+.*\t$`.

Let me run it.
dsh: reasoning:
No added line has trailing whitespace ✓ → consistent with `git diff --check` EXIT=0 (for the trailing-whitespace class at least). Space-before-tab (`+ \t` patterns) would also be flagged; the grep `^\+.*[ \t]$` covers trailing whitespace; space-before-tab is different (a space immediately followed by a tab in the indentation). Let me not over-engineer; I can note partial verification: no trailing whitespace in added lines → the diff --check claim is plausible but not fully verified (space-before-tab not checked). Actually let me quickly check `^\+[ ]+\t` too — cheap. Hmm, I'll skip; instead I'll state "added 行零行尾空白（trailing-whitespace 类）→ diff --check 主要判据通过；完整的 EXIT=0 仍属运行期项".

Now let me also double check one potential issue I haven't: the fix diff's `calibration.json` line 476 reasoning and limitations are inside `threshold_evaluation` and top-level `limitations` ✓ verified in the script (lines 741-760, 803-812) and the JSON.

Let me also confirm the md table's aggregate rows unchanged (18/16) ✓ from the earlier read (line 25-26).

OK. One more consideration about R2's "NO_DATA 豁免不阻断整体 Gate" clarity: let me re-read the thresholds sentence once more:

"**覆盖前置（CALIB r1 R2/R3）**：非空对 n≥1 方可判定，否则 **NO_DATA**——全空跑（两次 run 译文全空）在相似度口径下可平凡 PASS，由 §7 translate 评分 Gate 兜底，本 Gate 不对翻译覆盖度负责；region_count=0 的 case 贡献 0 对 → 同 NO_DATA 口径豁免（与 §6 R11 零 region 豁免同口径），不阻断整体 Gate 但单独登记（本次校准的 K01 即此情形，ko webtoon 家族因此未被本次校准覆盖）。"

Reading: precondition → NO_DATA; the em-dash clause explains WHY (all-empty would trivially PASS) and who compensates (§7); then the region_count=0 case → "同 NO_DATA 口径豁免 ... 不阻断整体 Gate 但单独登记". So "NO_DATA 口径" is characterized as 豁免/不阻断. A careful reader concludes: NO_DATA (either cause) does not block; coverage is §7's job. That's coherent. The remaining risk: the phrase "在相似度口径下可平凡 PASS" could be misread as "the gate PASSes the all-empty case" rather than "before the precondition it would have". I'll report as a P3 wording refinement (add "（未加前置时）" or "故" to make causality explicit), non-blocking.

I think I have enough. But let me consider whether to also flag: the thresholds §5 doesn't say what the *aggregate/overall* verdict is when one of the fixed 3 cases is NO_DATA (e.g., "整体 Gate = 其余 case 的 verdict 合取"). The phrase "不阻断整体 Gate" implies it. It's adequately stated. OK.

One more: should I flag that `case_gate_verdict`'s NO_DATA is a NEW verdict value not previously in the thresholds vocabulary (PASS/FAIL)? The thresholds now defines NO_DATA explicitly ✓ (from R3). Fine.

Let me also double check the R9 rule's fail-closed direction: "声明与 provider 绑定不一致时 fail-closed 报错" ✓ (rule-level; runner not implemented).

Also: the R9 rule says "provider id 含 remote 采样服务标识，如 deepseek/*" — hmm, what is the actual remote provider id in this project? phase2-plan §2.1 line 29 says: "`translate`：按用户选择绑 `openai-compatible-translation` 或 `sakura-local`". The DeepSeek endpoint is bound via the `openai-compatible-translation` provider (with base_url to DeepSeek)! So the "remote sampling provider id" for the actual T-4 run is `openai-compatible-translation`, NOT `deepseek/*`. The thresholds rule's example "provider id 含 remote 采样服务标识，如 `deepseek/*`" doesn't match the project's actual provider id. That's a concrete executability defect in the R9 discriminator: following the example literally, `openai-compatible-translation` (the actual remote DeepSeek binding used in the calibration source runs) would not match "deepseek/*" and could be classified as... ambiguous. The rule says "按 provider 绑定是否 remote 采样" (semantic) with an example that doesn't correspond to the project's real id. This is a genuine P3 finding: the discriminator example is inconsistent with phase2-plan §2.1's provider binding vocabulary (`openai-compatible-translation` bound to the DeepSeek endpoint; `sakura-local` = local). Recommend: state the rule in terms of the project's actual provider ids (e.g., `openai-compatible-translation`/remote base_url → 相似度轨; `sakura-local`/mock → 哈希轨), or in terms of "provider 的 endpoint 是否为本机回环/内置 mock".

That's a valuable, concrete finding. Let me verify the provider ids in the codebase: grep for PROVIDER_OPENAI_TRANSLATION value and sakura-local.

Let me check: phase2-plan line 126 `provider_id=PROVIDER_OPENAI_TRANSLATION`. And translation_openai.py defines SAKURA_DEFAULT_BASE_URL. Let me grep for the provider id constants.

Let me do that to be accurate.
dsh: reasoning:
Confirmed: the actual remote provider id used for the calibration source runs is `openai-compatible-translation` (with base_url=https://api.deepseek.com/v1, model=deepseek-chat). The thresholds R9 rule's example "provider id 含 remote 采样服务标识，如 `deepseek/*`" does not match the project's provider id vocabulary. So a runner implementing the literal rule would need to decide whether `openai-compatible-translation` counts as remote — it obviously is remote (DeepSeek endpoint), but the rule's stated criterion ("provider id 含 remote 采样服务标识") is not satisfied by that id. This is a concrete executability defect (P3): recommend re-expressing the rule in the project's actual vocabulary, e.g. "translate 绑定的 provider_id ∈ {openai-compatible-translation}（远端 base_url）→ 相似度轨；sakura-local / 内置 mock → 哈希轨"，or "以 provider 的 endpoint 是否为本机回环/内置 mock 判定".

Good — that's finding N-focus for R9. R9 = partial/closed-with-residual → I'd say "closed（口径已补），但判别示例与本项目实际 provider 词汇不一致 → P3 残留"。

Now I'm fairly complete. Let me consider a couple more possible checks:

1. Does the fix's thresholds note also need the coverage precondition to appear in §7 row 10? §7 row 10 says "确定性复跑双轨（F5 修订...）：remote 翻译链 = reading_order 对齐译文相似度 Gate（normalized 口径 median ≥ 0.95 且 min ≥ 0.70）；mock/deterministic 链 = export 哈希逐位一致". It does NOT mention the NO_DATA coverage precondition. Is that an inconsistency? §7 is the summary table; §5 is the detail. The row points to §5 注. Acceptable, but a reader of the summary table alone wouldn't know about NO_DATA. Since §7 row 10 says "详见 §5 注" ✓. Fine, no finding. Hmm, but this is the "权威口径" table (用户裁决清单). Minor: P4 at most. I'll skip.

2. Is the R2 coverage precondition reflected in the *calibration script's artifact* for K01? K01 isn't in CALIBRATION_CASES, so no. Fine.

3. Should I flag that `CALIBRATION_CASES` excludes K01, while the Gate's fixed case set includes K01 — meaning the calibration never exercises the NO_DATA path (0 pairs)? That's exactly what R3's disclosure covers ("region_count=0 的 case 贡献 0 对、按 NO_DATA 豁免" — and the artifact/limitation says K01 is NO_DATA-exempt). But note: the claim "the gate requires >=1 non-empty pair else NO_DATA" is asserted in thresholds/limitations but NOT actually exercised by the calibration script's output (no NO_DATA case in the JSON). The handoff claims "重跑实测 dropped=0" but no test of the NO_DATA branch. Is there any test/demonstration of the NO_DATA path? Not in the artifact (grep for NO_DATA in calibration.json found none). So the new precondition is unverified-by-execution (no case exercises it). Worth a NOT_VERIFIED/finding: the coverage-precondition branch (NO_DATA) has no executed instance in the delivered artifact; K01 is excluded from CALIBRATION_CASES, so the branch is only statically present. Recommendation: either add K01 to the calibration cases (it would produce NO_DATA and exercise the branch — though the script only reports, and K01's 0-pair handling would then appear in the artifact as evidence), or a one-line unit-style demo. Hmm, adding K01 to CALIBRATION_CASES would change the output artifact structure (adding a case). But it would empirically demonstrate the NO_DATA path and also the "0 对 case 豁免" caliber. Since the owner claims R3's exemption is "landed in the wording", and the code path exists, it's fine semantically, but the *evidence* for the NO_DATA precondition is only static. I'd raise this as a P3 (evidence gap): the R2/R3 code branches (NO_DATA) are never exercised by the delivered calibration output; a cheap demonstration would be running the calibration with K01 included (or a tiny inline self-check) and registering the resulting NO_DATA. That's a fair, actionable review point. I'll include it.

Let me double check: is K01 excluded because it has no translate pairs (would produce an empty pairs list, and `case_gate_verdict` → NO_DATA, and the md table would show None values...). Note that if K01 were included, render_markdown's table would show `n_pairs=0`, min/median = None → it prints "None" and the report's "关键读数" uses cases[0]/cases[1] indexing (hardcoded) — CALIBRATION_CASES order is [K11, BJ02]; if K01 were appended as third, cases[2] unused. The md render at §2 loops over cases → would render K01 row with None values. Also `agg` distributions include 0 pairs from K01 — no numeric change since distributions are over pairs. Actually including K01 would change `n_pairs` aggregate? No: sum of pairs = 18 still (K01 contributes 0). So including K01 would be harmless and would exercise the NO_DATA branch. That strengthens my recommendation: adding K01 to CALIBRATION_CASES is a cheap, safe way to (a) exercise the NO_DATA path, (b) demonstrate the R3 exemption for the fixed-3-case set that thresholds §5 names. Good suggestion.

Hmm, careful: `render_markdown` uses `cases[0]`/`cases[1]` for K11/BJ02 in the 关键读数 — adding K01 as third keeps that working ✓. And the §2 table row for K01 would show None/None for min/median — cosmetic. And the md "关键读数" might need the NO_DATA mention. Fine — it's a suggestion.

4. One more: should I verify there's no leftover reference to "7/13" anywhere else that would reintroduce the mixed denominator? Let me grep for "7/13" across the worktree. r1 R12 was about the handoff. Let me check whether thresholds/calibration.md still contain "7/13" anywhere in a leading position. calibration.md:28 says "K11 raw 浮动 7/11 非空对（复现 quality-report F5 已登记的 7/11 观察；normalized 降为 5/11...）" ✓ no 7/13. Let me grep to be sure.

Let me run a final grep for "7/13" and "NO_DATA" in the worktree deliverables.
dsh: reasoning:
Confirmed:
- No residual "7/13" in a leading/authoritative position (only in handoff:41 as the explicitly-marked "内部附报" clarification and historical docs like quality-report:144 / TA3-B2 handoff / old reviews, which are historical records) ✓ R12 closed.
- "NO_DATA" appears in thresholds:168, calibration.md:14/95, calibration.json:23/514/522 ✓ — but NOT as an actual verdict value in the artifact (no case returns NO_DATA) → my P3 evidence-gap finding stands (the branch is statically present but not exercised).
- calibration.json is now 527 lines (the earlier read said 527; the grep shows line 522 = limitation). ✓

Now I have everything I need. Let me also double check one small thing: the R7 claim "dropped 落盘（实测 0）" ✓ (n_dropped_regions: 0 at lines 39, 253).

Let me think about whether to run one more check: whether the worktree has any modified-but-uncommitted file. I can try an indirect check: compare file sizes/mtimes? Not meaningful. Alternatively, check if `.git/worktrees/.../index` mtime... no. I'll leave porcelain as NOT_VERIFIED.

Hmm, wait. Maybe I can partially verify "porcelain 干净" differently: the fix diff's post-images match the worktree files exactly for all 7 files — I verified 6 of 7 in detail (handoff, task, script, calibration.json, calibration.md, quality-report, thresholds — actually all 7). If there were uncommitted modifications, the worktree files would likely differ from the committed post-image... but I compared against the diff, not the commit object. Since the diff is stated to be 2400b57a→8926f49c and the worktree HEAD is 8926f49c, and the worktree files match the diff's post-image, then the worktree files match the commit's content → no modifications to those 7 files. But uncommitted changes could exist in OTHER files (e.g., a leftover untracked file). Since the review scope is these 7 files, this is a reasonable partial verification. I'll state it exactly that way: "7 文件 post-image 与 diff 逐块一致 → 这 7 文件无未提交改动（间接）；完整的 porcelain 洁净仍属运行期项".

Let me now also double check that the thresholds §7 row 10 (modified in e3b7c48d) is present and consistent in the current file ✓ (line 205 read earlier) — it mentions the dual-track and points to §5 注 ✓, though it lacks the NO_DATA/coverage precondition (P4 minor).

Now let me also assess: does the fix diff contain any change to the "0.05 余量" in thresholds 依据 cell? Yes transformed to "0.05 绝对值余量" ✓ R4 unification verified in all four places:
1. thresholds:168 依据 cell ✓
2. calibration.md:68 ✓
3. script render_markdown reasoning (line ~571-572) ✓
4. script JSON reasoning (line 742-744) ✓
And §6.3 / limitation 3 with the 4-char counterexample ✓ both in md:92 and script limitation ✓ and json limitation ✓.
And the old wording "留一个字符级测量余量" is gone except in the handoff's R4 row quoting it ✓.

Great.

Now the final structure of my answer:

## Verdict
approved（可集成）—— with 0×P0/P1/P2 new; R1-R14 all closed (R6/R9 closed with P3 residuals); residuals N1-N5 P3/P4 recommended for integrator/follow-up, non-blocking.

Wait — should I be more careful? The user's binary choice: approved（可集成）/ changes_requested. I'll choose approved and be explicit that the residuals are non-blocking and where to fold them.

## R1-R14 逐条复核表
Table with 条目 | r1 级别 | Owner 声称 | 复核结论 | 证据（文件:行）

I need to give file:line for each. Let me collect precise citations:

- R1: 脚本 calibrate_determinism.py:144-174（bbox 采集 :154/:172）、:349-358（逐 reading_order bbox 断言 + SystemExit）、:280-284? Actually alignment key-set check is :331-335; coverage check :336-345. calibration.md:11（§1 第 1 条登记假设与校验）。handoff:84. Verified bbox equality: qual-K11.json:136-286 vs qual-K11.rerun.json:136-286 (ro1-6 spot check identical; r1 verified 13/13); qual-BJ02.json:139-197 vs rerun (5/5 identical). Residual N2: `bboxes.get(rid)` at :154/:172 → None==None vacuous.
- R2: 脚本 :303-319（case_gate_verdict → NO_DATA at :314-315）、:416（case verdict 用 case_gate_verdict）、:708（aggregate is_nonempty）、json:23/514/522、thresholds:168、calibration.md:14/95. Residual N3 (wording) + N-evidence gap (NO_DATA branch not exercised by artifact; K01 not in CALIBRATION_CASES at :77).
- R3: thresholds:168（region_count=0 → NO_DATA 豁免 + ko webtoon 未覆盖）、§6 R11 at thresholds:185（交叉引用可解析）、calibration.md:95、json:522. Closed.
- R4: thresholds:168、calibration.md:68/92、脚本:571-572（render_markdown）、:742-744（reasoning）、json:482/512? (json limitation at :482...). Let me be careful with json line numbers: limitation 3 is at json line 482 per the diff mapping (diff line 482). And the reasoning at json:514 (grep confirmed line 514). Fine: json:482（limited 3）, json:514（reasoning）.
- R5: 脚本:579-584? Let me compute: the diff hunk @@ -493,8 +581,11 @@ → the new median line is around 581-584. In the actual file, the §4.2 text... I read lines 443-507, and the §4 reasoning starts later (~571). I didn't read 560-600 of the actual file. The diff says the changes are at file lines ~581-584 (new). To be safe, I can cite from the diff hunk headers: script §4.2 at :581-584 (per @@ -493,8 +581,11 @@), and md:69/96, json:517? Hmm, json §4.2 → json limitation for R5 at diff line 487 → json:487; and the reasoning at json:514. Also md:69 (§4.2), md:96 (§6.7).
  Let me double check the script's §4.2 line numbers by reading lines 560-600. It's worth doing for citation accuracy since I cite it. Let me read script 560-600.

Also for R7 citations: script :158-165 (missing region_id FATAL), :329-345 (coverage assertion), :389-396 (coverage fields), json:35-39/251-253? (diff shows K11 at diff 451-455 → json 35-39 ✓, BJ02 at diff 463-467 → json ~249-253; grep showed n_dropped at json:39 and :253 ✓).

- R6: script :177-188 (pair_status normalize), :191-195 (is_nonempty), :376, :708. Residual N1.
- R8: script :649-661? The diff hunk @@ -569,6 +662,26 @@ adds limitations 6-8 at file lines ~662-682. So §6.6/6.7/6.8 at script ~663/669/676; md:95/96/97; json:522/523? Hmm, json limitations: the diff lines 486,487,488 → json lines 486,487,488. Let me confirm: the json limitation list lines — grep showed json:522 for the coverage limitation. So the json limitations are at 520-524ish. Hmm! The diff line numbers for the json hunk (@@ -499,14 +511,17 @@) map diff line 486 → json line? The hunk starts at json line 511 (new). Diff line 471 is the hunk header; diff lines 472-474 are context (gate_verdict FAIL, closing braces, },). Let me map: hunk header at diff 471 = new json line 511. Diff line 472 = json 511, 473 = 512, 474 = 513, 475 = removed reasoning (old 514), 476 = new reasoning (json 514 ✓ matches grep). Then 477 = json 515 ("},")? Actually the hunk continues: 477 "  }," → 515? Hmm, whatever: grep gave exact json lines: coverage_precondition :23, n_dropped_regions :39/:253, reasoning :514, coverage limitation :522. So limitations 3-8 are at json ~517-522. Let me just use the grep-verified line for the ones I cite: json:514 (reasoning), json:522 (R2/R3 limitation). For R4/R5/R8 limitations I'll cite the md/script instead (md:92/96/97, script limitation block) — or cite json limitation by content. To be safe I'll read json lines 515-527 to get exact line numbers for limitations.

Let me do two final reads: script 560-600 and json 512-527.

Also R9: thresholds:172（尾注判别规则）、phase2-plan:33? No, phase2-plan wasn't changed in the fix. R9 落点 = thresholds:172. Residual N-runner (run_qualification.py:851 & :811-825 still hash-only) + N-provider-vocabulary (actual remote id = `openai-compatible-translation`, src/infrastructure/providers/translation_openai.py:34-35; quality-report:6).
- R10: quality-report.md:189/:199 ✓ verified in worktree.
- R11: task:28 ✓, plus AC3 wording; fork_commit task:13.
- R12: handoff:41 ✓.
- R13: script :766-776（relative_to）、json:5 ✓.
- R14: task:13 ✓ + reflog evidence.

Let me do those two reads for line accuracy, then write.

Also for the "返修前后零数字差异" claim, cite: fix diff calibration.json hunks = 6 处结构/文本 only; no pairs/stats/probes/verdicts hunks; json:34/:248 n_pairs_nonempty=11/5, :241/:367 gate_verdict_normalized PASS ✓。

Let me read those two ranges.
dsh: reasoning:
Now I have exact citations:
- script:571-579 (§4.1 min, "0.05 绝对值余量" at :574-575)
- script:580-589 (§4.2 median with length-distribution qualifier at :584-588)
- script:662-682 (§6.6/6.7/6.8 additions — let me confirm: the diff hunk @@ -569,6 +662,26 @@ → new lines 662-687. The three appended limitations: R2/R3 at ~662-665 (block starting at 662), R5 at ~669, R8 at ~676. From the md read (md:95/96/97) and json:522/523/524. For the script I'll cite the block as :662-682 (approximate). Let me be safe: I'll cite "script:662-687（§6 第 6-8 条）" — hmm, accuracy matters. I could read script 655-700 to confirm. Let me not over-read; I can cite the md/json lines which I verified exactly, and for the script cite the hunk range. Actually the review table should cite precise lines where I claim something. For R8 I'll cite calibration.md:97 and json:524, plus script limitation block (I'll state "§6 limits 6-8 in render_markdown（文件 :662 起，按 diff hunk @@ -569,6 +662,26 @@）"). That's honest.

Hmm, let me just read script 655-700 quickly to be precise. It's one more read; worth it for citation accuracy.

Actually, I can bound it: the diff hunk `@@ -569,6 +662,26 @@` means the new block occupies lines 662-687 (26 lines: 6 context + 20 added? The hunk has 26 new lines: 5 context lines + 21 added). The added limitations are:
```
+    lines.append(
+        "6. **覆盖前置...（3 lines of text）"
+    )
+    lines.append(
+        "7. ...
+    )
+    lines.append(
+        "8. ...
+    )
```
Let me count from the diff (lines 304-323): 304 "+    lines.append(", 305-309 "+text" (5 lines), 310 "+    )", 311 "+    lines.append(", 312-315 (4 lines), 316 "+    )", 317 "+    lines.append(", 318-322 (5 lines), 323 "+    )" = 21 added lines. Plus 5 context lines (the existing limitation 5 continuation + closing) = 26 ✓. The hunk starts at new line 662: context lines 662-666? Let's map: the hunk's first lines are context:
```
         "5. **归一化口径依赖**：normalized 口径吸收换行/空格差异（K11 浮动 7→5）；"
         "若产品语义认为换行位置也是译文的一部分，应引用 raw 口径附报。"
     )
+    lines.append(
...
```
So context = 3 lines (662, 663, 664)? Then added 21 lines = 665-685, then trailing context 2 lines = 686-687. Hmm, the hunk header says +662,26 → lines 662..687 = 26 lines. Context 5 + added 21 = 26 ✓. So there might be 2 more context lines at the end. Given added lines start after 3 context lines (662-664), the added block = 665-685, and context 686-687 (the remaining 2: `lines.append("")` and `lines.append(f"> **声明**...")`). So limitations 6/7/8 are at script lines 665-685: item 6 starts at 665 (lines.append() then the string at 666?). Precisely: 665 "+    lines.append(", 666-670 the 5 text lines (666,667,668,669,670), 671 "+    )", 672 "+    lines.append(", 673-676 (4 lines), 677 "+    )", 678 "+    lines.append(", 679-683 (5 lines), 684 "+    )". So: limitation 6 text at 666-670, limitation 7 at 673-676, limitation 8 at 679-683. Close enough; I'll cite "script:665-684（局限 6-8）" to be safe. Good — I'll use a range.

Now, let me also double check the R2 script citation: case_gate_verdict at :303-319; build_pairs coverage fields :389-396; the aggregation at :708. ✓

One more consideration: for R2's residual I want to cite thresholds:168 and calibration.md:14 for the wording tension.

Also for the "NO_DATA 未被实际执行" evidence: CALIBRATION_CASES = ["K11","BJ02"] at script:77; json has no NO_DATA (grep) — 527-line json with no NO_DATA line ✓ (grep on the directory found NO_DATA only in calibration.md/json:23/514/522 text, not as a verdict). ✓

Alright. Also, I should double-check the R6 residual more concretely: could `is_nonempty`'s OR semantics differ from the docstring in a way that matters for n_pairs_nonempty? Only with empty_one_side. Confirmed no such pair in data (18 pairs). ✓

Now let me think about my overall verdict and how to phrase the residuals. Also "回潮与新问题" section:
- 回潮: 7 files all within allowed surface (quality-report.md noted), qual-*.json zero, thresholds other thresholds unchanged, +223/−46 verified, no src/tests/contracts/STATUS, phase2-plan untouched by this commit (already updated in e3b7c48d).
- 新问题: N1-N6 + runner gap.

And "NOT_VERIFIED": script re-run byte-identity (no shell); porcelain clean; diff --check EXIT=0 (partially: no trailing whitespace in added lines); git show --stat 8926f49c; the "程序化对比零差异" program itself; the half-finished draft fixes; also `--determinism-track` implementation.

And "推荐下一步": integrator merges/applies the 3 P3 doc-level fixes (or registers them) + opens a follow-up for the runner; then Codex integrates and STATUS/PLAN already registered (main has CALIB in STATUS:14 and PLAN:173 as "r2 复核中" → after this r2 approval, integrator updates to approved/integrated).

Per AGENTS.md, I must end with a recommended next step that includes a forwardable instruction with the right agent. The repo convention: after review, the integrator (Codex/编排会话) integrates. I'll give: 交集成方（编排会话代行 Codex）执行集成 + 同步 STATUS/PLAN；并给出 R1 修复项的可转发指令。Also mention the reviewer file should be stored at doc/reviews/M2-QUAL-DETERM-CALIB-8926f49c-dsh-r2.md.

Let me also decide: should the N1 (is_nonempty docstring/semantics) be a condition? The user asked binary approved/changes_requested. I'll approve but list N1 as the top "集成前建议顺手闭合" item (one-line docstring fix or change to `and`). Actually careful: if the integrator "fixes" the docstring to match the implementation, that's a doc change in the worktree → would require a new commit from the Owner, not the integrator. The instruction: the integrator should NOT author code fixes in the owner's面? Repo practice: 集成方 can make integration fixes (as seen in other tasks: "集成方闭合清单"). I'll recommend: either (a) record N1 as a known residual and let the Owner fix in a follow-up commit, or (b) the integrator folds it into the integration commit (repo has precedent for integrator-authored cleanup, e.g., M2-SFX-PROD-1's "集成修正 0c4afdb1"). I'll present both and let the integrator decide, with a preference for a tiny Owner fix if the worktree is still open, otherwise integrator fold-in with disclosure.

Hmm, one thing to double check: is the worktree still at 8926f49c and can the Owner commit again? Yes, branch is checked out at 8926f49c, clean (claimed). The integrator will merge. Fine.

Let me now write the final report. It should be thorough but organized. Output sections exactly as requested:
## Verdict
## R1-R14 逐条复核表
## 回潮与新问题
## NOT_VERIFIED
## 推荐下一步

I'll write in Chinese, dense, with file:line citations. Let me make the table compact.

Let me draft the R1-R14 table:

| # | r1 级别 | Owner 声称 | 复核结论 | 证据（worktree@8926f49c） |

R1 P2 closed → closed（+P3 残留 N2）
R2 P2 closed → closed（+P3 残留 N3）
R3 P2 closed → closed
R4 P2 closed → closed
R5 P3 closed → closed
R6 P3 closed → closed（+P3 新缺陷 N1）
R7 P3 closed → closed（+P4 N5）
R8 P3 closed → closed
R9 P3 closed → partial-closed（口径已补，判别示例与项目 provider 词汇不符 + runner 未实现 → N4/N6）→ I'll mark "closed（附 P3/N4 + 集成项 N6）"
R10 P3 closed → closed（允许面按字面通过，P4 N7）
R11 P3 closed → closed
R12 P4 closed → closed
R13 P4 closed → closed
R14 P4 closed → closed

Plus the two owner claims: 复跑一致性 and 自检.

I need to also explicitly answer the 5 focus questions in 复核要求 1:
- R1 bbox 断言实现: 正确 fail-closed；残 N2 空值旁路。
- R2/R3 thresholds §5 语义: 基本清晰，一处张力（N3）。
- R4 0.05 绝对值余量统一: 已统一（4 处）。
- R7 fail-closed 断言完整性: 完整（覆盖断言 + 缺 region_id FATAL）；n_dropped_regions 恒 0（N5）。
- R9 双轨判别规则可执行性: 定义层可执行但示例 provider id 不符 + runner 未实现（N4/N6）。

I'll fold these into a short "重点结论" paragraph after the table or within the table rows. Better: add a short "重点项结论" block under the table.

Length: aim for a comprehensive but readable report. Let's write it.

One more check I should do for completeness on "回潮": are there any files in the fix commit outside the 7 that I might have missed because the diff is path-filtered? The prompt gives the diff as authoritative for the fix. I'll note this as NOT_VERIFIED (diff 生成口径), same as r1.

Also the exact numbers: +223/−46 verified (212+11 added; 46 removed). ✓

Let me write the final answer now.

For NOT_VERIFIED I'll list:
1. 脚本两次重跑字节级 sha256 一致（沙箱无 shell；STATUS:14 集成方记「复跑逐值一致」=旁证）。静态可判定的部分：无时间戳/无随机源（seed 固定 :263、md 头部日期硬编码 :448）、迭代全 sorted（:347/:420）→ 结构上确定。
2. porcelain 干净 / git diff --check EXIT=0 / git show --stat 8926f49c（我以「7 文件 post-image 与 diff 逐块一致 + 新增行零行尾空白」间接佐证）。
3. fix diff 生成口径（是否 path-filter）→ 无法排除夹带；集成方以 git diff --stat 2400b57a..8926f49c 复核。
4. NO_DATA 分支未被实际执行（K01 不在 CALIBRATION_CASES）。
5. `--determinism-track` 及 runner 侧实现（grep 全仓仅 thresholds:172 与 handoff:92 出现）。
6. 半成品草稿 4 处修正（草稿未入库）。

推荐下一步 (per AGENTS.md must give a forwardable instruction + next agent):
- 集成方（编排会话代行 Codex）：merge agent/zcode/M2-QUAL-DETERM-CALIB (8926f49c) → main；同步 STATUS.md:14 / REBASELINE_PLAN.md:173 由「r2 复核中」→ approved/集成；把本 r2 报告原字节入库 doc/reviews/M2-QUAL-DETERM-CALIB-8926f49c-dsh-r2.md。
- Owner（ZCode）或集成方顺手闭合 N1（一行 docstring）与 N3（一处措辞），若走 Owner 则新提交并更新 handoff；否则集成 commit 内记明。
- 新开 follow-up（登记不释放）：qualification runner 落实现行口径（track 选择/相似度 Gate/覆盖前置 NO_DATA/bbox 交叉校验），因为 run_qualification.py:851 仍是哈希逐位 fail-closed，与 thresholds:168/172 冲突。

I'll phrase the recommended next step as a single forwardable instruction as required.

Let me write it all out now. I'll be careful to be precise and honest about severity.

Actually, one consideration on severity of the runner gap (N6): is it possible that the *intended* reading is that the runner update belongs to a future qualification run and the plan already says so (§4 step 5)? phase2-plan:182 says step 5 = "复跑哈希对照 + 译文相似度 Gate 计算". So the plan does prescribe computing the similarity gate at step 5 (manual/scripted by the operator). So the runner code's hash-only behavior + fail-closed is a divergence from the plan, but the plan's step 5 is arguably executed by the operator using the calibration script. Still, `run_qualification.py --rerun-check` would exit non-zero on K11 — a concrete conflict. I'll rate it P3 integration item, non-blocking, needs registration. Fair.

Also note: the fix commit did NOT touch phase2-plan — fine, since phase2-plan already carried the dual-track text from e3b7c48d. But the R9 discriminator rule was added to thresholds only; phase2-plan §2.1 (runner-facing) doesn't carry the discriminator rule. Minor (P4): recommend the follow-up add it to phase2-plan §2.1 when the runner is updated. I'll fold into N6.

Writing now.
复核完成。以下是 r2 定点复核报告。

---

## Verdict

**`approved`（可集成）** — 0×P0、0×P1、0×P2；r1 的 4×P2（R1–R4）与 10×P3/P4（R5–R14）**全部实质闭合**；本轮新增仅 3×P3 + 4×P4 残留（文档措辞/加固/后续登记类），**均不阻断集成**。

判定要点（与 r1 同一静态口径：沙箱 `pwsh` 不可用，全程 read/glob/grep + git 元数据文件直读）：

1. **R1–R14 逐条可落地**：每条声称都能在 worktree 找到对应改动，且改动与声称一致（详见下表）。R6/R7/R9 各有一处**新增残留**（N1/N5/N4），性质为脚本文档自相矛盾、恒零字段、判别示例词汇不符，不影响任何数值与 Gate 判定语义。
2. **零数值漂移已被 diff 结构证明**：`calibration.json` 的 6 个 hunk 全部是 `summaries_dir` / `alignment_key` / `empty_pair_rule` 增补 / coverage 字段 / `reasoning` / `limitations` 文本，**无任何 pairs / stats / probes / gate_verdict 行被触碰**（`review-fix.diff:416-491`）；`pairs` 逐值、`n_pairs_nonempty` 11/5（`:34`/`:248`）、`gate_verdict_normalized` PASS/PASS（`:241`/`:367`）与返修前一致。
3. **范围纪律成立**：7 文件全在 Task 允许面（`doc/tasks/M2-QUAL-DETERM-CALIB.md:33-34`）；`qual-*.json` 零出现；thresholds 仅 §5 remote 行 + §5 尾注两行改动，其余阈值数值（0.10/0.15/0.20/0.25、3.5/80%、n≥15、pipeline_failures=0）零改动；`+223/−46` 与 diff 逐行计数吻合（212 非空 `+` 行 + 11 个纯 `+` 空行；`−` 46）。
4. **拓扑与上游一致**：worktree reflog 证实 `8996ca55 → e3b7c48d → 2400b57a → 8926f49c`，`fork_commit: 8996ca55` 注记与 e3b7c48d 父提交一致；分支 ref = 8926f49c，HEAD 未分离；main 已前进至 `1d477b35`（本分支未集成），且 main 侧 STATUS/PLAN 已登记本 Task（r1 E5 的登记缺口已由编排方闭合）。

---

## R1-R14 逐条复核表

| # | r1 级别 | Owner 声称 | 复核结论 | 证据（worktree @8926f49c） |
|---|---|---|---|---|
| **R1** | P2 | bbox 逐字段断言 + `§1.1` 假设登记 | **closed**（+残留 N2） | 采集 `bbox`：`calibrate_determinism.py:154`、`:172`；断言+同通道 FATAL：`:349-358`（`if a["bbox"] != b["bbox"]: raise SystemExit(...)`）；登记：`calibration.md:11`、`calibration.json:13`。**独立复核 bbox 恒等**：K11 ro1–6 逐字段相同（`qual-K11.json:136-208` vs `qual-K11.rerun.json:136-208`，region_id 全不同），BJ02 **5/5** 相同（`qual-BJ02.json:139-197` vs `qual-BJ02.rerun.json:139-197`）→ 断言非空转、当前数据不会误触发 |
| **R2** | P2 | `case_gate_verdict` 覆盖前置（≥1 非空对否则 NO_DATA）+ thresholds 关系句 + 局限 | **closed**（+残留 N3） | 代码：`:303-319`（`:314-315` 返回 NO_DATA）、接线 `:416`；thresholds：`:168`「非空对 n≥1 方可判定，否则 **NO_DATA**……由 §7 translate 评分 Gate 兜底」；局限：`calibration.md:14`/`:95`、`calibration.json:23`/`:514`/`:522`。数值无回退（K11/BJ02 均有非空对 → verdict 仍 PASS，`:241`/`:367`） |
| **R3** | P2 | 0 对 → NO_DATA 豁免 + ko webtoon 未覆盖 | **closed** | thresholds`:168`「region_count=0 的 case 贡献 0 对 → 同 NO_DATA 口径豁免……不阻断整体 Gate 但单独登记……**ko webtoon 家族因此未被本次校准覆盖**」；交叉引用可解析：`§6 R11 零 region 豁免` 确在 `quality-thresholds.md:185`；K01 事实核对：`qual-K01.rerun.json:52`（`region_count:0`）、`:73`（`regions: []`）、`:76`（`translate_details: []`）→ 新增强断言在 0-region 上不误报（空集相等） |
| **R4** | P2 | 「0.05 绝对值余量」统一 + §6.3 长度悬崖 4 字反例 | **closed** | 四处统一：thresholds`:168`、`calibration.md:68`、脚本 `:571-579`（`:574-575`「**0.05 为绝对值余量**……不是「一个字符」」）、`calibration.json:482`?→实为 `:519` + reasoning `:514`；全仓 grep `一个字符级` 仅剩 handoff 引述旧措辞（`handoff:87`）。4 字反例：`calibration.md:92`、脚本局限 3、`calibration.json:519` |
| **R5** | P3 | median 边界限定样本长度分布 + §6.7 局限 | **closed** | 脚本 `:580-589`（`:584-588`「在本校准样本的译文长度分布下——浮动串长 4–16 字」+ 不外推长译文）；`calibration.md:69`/`:96`；`calibration.json:514`/`:523` |
| **R6** | P3 | 抽公共 `is_nonempty` + 判空基准统一 | **closed**（+新缺陷 N1） | `pair_status` 改 normalize 判空：`:177-188`；`is_nonempty`：`:191-195`；两处引用：`:376`、`:708`（旧的分叉定义已消失）；无数字变化（`:181-182` 注释已披露）。**N1**：`:192-194` docstring 写「excludes empty_both AND empty_one_side」，实现是 `bool(nf or ns)`＝**只排除双方空** |
| **R7** | P3 | 覆盖断言 + dropped 落盘 + 缺 region_id FATAL | **closed**（+残留 N5） | 覆盖断言+落盘 dropped 列表：`:340-345`；缺 region_id 同通道：`:158-165`（不再裸 KeyError）；产物字段：`:389-396` → `calibration.json:35-39`（K11 13/13/13/13/0）、`:249-253`（BJ02 5/5/5/5/0）。断言不可达时 `n_dropped_regions` 恒 0（N5） |
| **R8** | P3 | 词面口径误报方向登记（探针不加+理由） | **closed** | `calibration.md:97`、脚本局限 8（`:665-684` 区段）、`calibration.json:524`；理由「词面框架内无法构造确定性语义等价代理」+ 后续语义度量方向均有落字 |
| **R9** | P3 | 双轨判别规则 + `--determinism-track` + 不一致 fail-closed | **closed（口径层）/ 执行层待落地**（N4/N6） | `quality-thresholds.md:172` 尾注含「按 provider 绑定判轨…`--determinism-track remote\|mock`…不一致 fail-closed」✓。**N4**：示例「provider id 含 remote 采样服务标识，如 `deepseek/*`」与本项目实际词汇不符——校准来源 run 的远端 provider 是 `openai-compatible-translation`（`translation_openai.py:34`，绑定 `https://api.deepseek.com/v1`，`quality-report.md:6`），并不含 `deepseek/*` 形态；**N6**：全仓 grep 该参数只出现在 thresholds 与 handoff，`run_qualification.py` 仍只做哈希逐位 |
| **R10** | P3 | quality-report :189/:199 关系注 | **closed**（+P4 N7） | 两处关系注已落地并与 r1 行号一致：`quality-report.md:189`、`:199`；`:199` 亦注明「F4 部分仍待其自身 Task」 |
| **R11** | P3 | Task AC3 改实际修订面 + §1 空核对登记 | **closed** | `doc/tasks/M2-QUAL-DETERM-CALIB.md:28`（改写为 §5 双轨条目+尾注 / §7 总表第 10 行 / phase2-plan §1/§2.1/§4，并明写「§1 经核对为**空修订面**」） |
| **R12** | P4 | handoff 分母 7/11 非空先行 | **closed** | `handoff:41`「raw 口径 K11 浮动 **7/11 非空对**（……7/13 仅为内部附报，不复引已修正的混用分母）」；全仓无其他权威位以 7/13 起头（`calibration.md:28` 亦为 7/11 先行） |
| **R13** | P4 | calibration.json 相对路径 | **closed** | 脚本 `:766-776`（`relative_to(REPO_ROOT)` + 回退）→ `calibration.json:5` = `verification\M2-TA3-B\phase2\summaries`；`REPO_ROOT` 定义在 `:71-72`，默认路径必然落在仓库内 |
| **R14** | P4 | `fork_commit: 8996ca55` 注记 | **closed** | `doc/tasks/M2-QUAL-DETERM-CALIB.md:13`；reflog 直读证实 `.git/worktrees/.../logs/HEAD:3`＝`8996ca55 → e3b7c48d`（父提交即 fork 点） |
| 复跑一致性 | 声称 | 18 对/分布/探针/逐对/verdicts 逐值零差异 | **成立（静态强证据）** | fix diff 中 `calibration.json` 的 6 个 hunk 无任何数值行；`pairs`/`stats`/`synthetic_probes` 上下文行原样保留（`review-fix.diff:420-491`）。字节级重跑本身见 NOT_VERIFIED |
| 自检 | 声称 | qual-*.json 零改动 / porcelain 干净 / diff --check EXIT=0 | **部分成立** | `qual-*.json` 不在 diff（7 文件枚举）；新增行**零行尾空白**（`^\+.*[ \t]$` 无命中）→ diff --check 主判据通过；porcelain 见 NOT_VERIFIED |

**重点项直接回答**

- **R1 bbox 断言实现**：实现正确且与既有 FATAL 同通道，非空转（K11/BJ02 实测恒等）；唯一缺口是 `bboxes.get(rid)`（`:154`）在两 run 都缺 `bbox` 键时给出 `None == None` 的**静默通过**（N2）。
- **R2/R3 thresholds §5 语义是否清晰**：**基本清晰，一处张力**——同句既说「非空对 n≥1 否则 **NO_DATA**」，又说「全空跑……在相似度口径下**可平凡 PASS**，由 §7 兜底」；「不阻断整体 Gate」只挂在 region_count=0 分句上（N3）。串读可正确理解为「未加前置时才会平凡 PASS；NO_DATA 口径＝豁免不阻断、覆盖度归 §7」，无实质歧义，但建议加「（未加前置时）」或「故」消歧。
- **R4「0.05 绝对值余量」是否与 thresholds 统一**：**是**，thresholds/calibration.md/脚本 md/脚本 JSON reasoning 四处同口径，旧「一个字符级余量」表述全清。
- **R7 fail-closed 断言完整性**：**完整**（两 run 键集合 + translate_details 覆盖 regions[] + 缺 region_id 三条全走 SystemExit，dropped 列表入 FATAL 消息）；`n_dropped_regions` 因前置断言**结构上恒为 0**，属背书字段而非检测字段（N5）。
- **R9 双轨判别规则可执行性**：**定义层可执行（规则确定 + 参数名 + fail-closed 方向明确），执行层未落地**——判别示例的 provider id 形态与本项目实际绑定不符（N4），且 `run_qualification.py:851` 仍对三 case 无差别做 export sha 逐位 fail-closed，与 thresholds:168/172 的现行口径**直接冲突**（N6）。

---

## 回潮与新问题

**回潮检查（全部通过）**

| 项 | 结论 | 证据 |
|---|---|---|
| 7 文件全允许面 | **通过（1 处需集成方确认）** | handoff/Task/`experiments/M2-QUAL-DETERM-CALIB/**`/`verification/M2-QUAL-DETERM-CALIB/**`/`verification/M2-TA3-B/{quality-thresholds,quality-report}.md` 均在 `task:33` 允许面。`quality-report.md` 落在 `verification/M2-TA3-B/**` 字面允许面内，但**超出括号列举**「thresholds/plan 修订+本 Task 产物」的意图；因其正是 r1 R10 的建议动作且非 `qual-*.json` 禁改物，判**可接受**（N7，建议集成 commit 记明范围依据） |
| `qual-*.json` 零出现 | **通过** | 7 文件枚举（`review-fix.diff:1/45/66/416/492/534/553`），无 `phase2/summaries/**` |
| thresholds 其他阈值零改动 | **通过** | 单一 hunk `@@ -165,11 +165,11 @@`：`quality-thresholds.md:168`（remote 行重写）、`:172`（尾注重写）；`:169` mock 行、`:170` 渲染行、`:195-206` §7 全表（含被 e3b7c48d 改过的行 10 = `:205`）均为上下文未动 |
| 无 `src/**`/`tests/**`/`doc/contracts/**`/`STATUS.md` | **通过** | 同上 7 文件枚举 |
| `phase2-plan.md` 本轮未再改 | **通过（合理）** | 不在 fix diff；其双轨文本已在 e3b7c48d 落地（`phase2-plan.md:17`/`:33`/`:182`） |
| 规模自洽 | **通过** | `+223/−46`：212 个非空 `+` 行 + 11 个纯 `+` 空行；`−` 46 行 |

**新问题（本轮引入/暴露，均为非阻断）**

- **N1｜P3｜`is_nonempty` docstring 与实现相反，且 aggregate 非空口径相对返修前被静默放宽**
  `experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py:191-195` vs `:708`（及 `:376`）。docstring 称「excludes empty_both AND empty_one_side」，实现 `bool(normalize(a) or normalize(b))` 只排除**双方空**；返修前 aggregate 用 `status not in ("empty_both","empty_one_side")`（严格），case 级用 `not in ("empty_both",)`（宽松），本轮统一到**宽松**分支。当前数据无 `empty_one_side` → 零影响（`n_pairs_nonempty` 11/5、`:34`/`:248` 不变）；但一旦出现单方空对，`calibration.json`/`md` 的「非空」分布会含 0.0 对，而 docstring 仍声称排除——reader 无法从代码确认口径。建议：把 docstring 改为「excludes empty_both（a pair counts as non-empty if either side is non-empty）」，或在 handoff/JSON 明写「aggregate 非空口径本轮由严格改为宽松（R6 统一的方向）」。
- **N2｜P3｜bbox 交叉校验存在 `None == None` 静默旁路**
  `calibrate_determinism.py:154`（`r.get("bbox")`）→ `:353`（`a["bbox"] != b["bbox"]`）。若某 run 的 `regions[]` 整体缺 `bbox` 键，两 run 均为 `None` → 断言通过，R1 想堵的置换风险重新隐没。当前 schema 每 region 都带 `bbox`（`qual-K11.json:142` 等 26 处、`qual-BJ02.json:145` 等），故非空转。建议 `if a["bbox"] is None or a["bbox"] != b["bbox"]:`（一行加固）。
- **N3｜P3｜thresholds §5 覆盖前置措辞张力 + NO_DATA 分支无执行证据**
  ① 措辞：`quality-thresholds.md:168`（同 `calibration.md:14`、`calibration.json:23`）「否则 NO_DATA——全空跑……可平凡 PASS……」；建议加「（未加前置时）」明确因果，并把「不阻断整体 Gate 但单独登记」同样挂到全空跑情形（现仅挂 region_count=0 分句）。
  ② 证据：`CALIBRATION_CASES = ["K11","BJ02"]`（`:77`）→ 交付产物中**没有任何 case 触发 NO_DATA**（全库 grep：NO_DATA 只出现在文本字段，`calibration.json:23`/`:514`/`:522`，无 verdict 值）。R2/R3 的新分支目前只有静态存在性。**低成本补证**：把 K01 追加进 `CALIBRATION_CASES`（`n_pairs` 仍为 18，K01 贡献 0 对）即可在产物里留下 `gate_verdict_normalized = NO_DATA` 的实证，同时覆盖 thresholds §5 命名的固定 3 case。
- **N4｜P3｜R9 判别示例的 provider id 与本项目实际绑定不符**
  `quality-thresholds.md:172` 以「`deepseek/*`」为例，但项目远端翻译 provider 是 `openai-compatible-translation`（`src/infrastructure/providers/translation_openai.py:34`；`PROVIDER_SAKURA = "sakura-local"` 在 `:35`），DeepSeek 仅体现为 `base_url`/`model`（`quality-report.md:6`），phase2-plan 的绑定表亦用同一 id（`phase2-plan.md:29`）。按字面示例判轨会把真实远端 run 判成「不匹配任何 remote 标识」。建议改写为项目词汇或改用「endpoint 是否本机回环/内置 mock」判据。
- **N5｜P4｜`n_dropped_regions` 结构恒 0**
  `calibrate_determinism.py:396` 位于 `:340-345` 断言之后，只可能是 0（`calibration.json:39`/`:253`）。作为「完整性背书」可留，但不应被当作检测项读；建议注释里点明「invariant, cannot be non-zero by construction」。
- **N6｜P3｜现行口径与在役 runner 冲突（集成待办，需登记）**
  `quality-thresholds.md:168`/`:172` 与 `phase2-plan.md:33`/`:182` 已宣称「remote 链＝相似度 Gate」，但 `experiments/M2-TA3-B/run_qualification.py:811-825`（仅算 `sha256_first/second`）与 `:851`（任一不匹配即 `failures += 1`）仍是原单轨逐位口径 → 今天跑 `--rerun-check BJ02,K01,K11` 会因 K11 哈希不一致让 Gate FAIL，与修订后口径矛盾。需在 PLAN/后续 Task 登记 runner 侧实现（track 选择 + 相似度 Gate + 覆盖前置 NO_DATA + bbox 交叉校验），并建议把判别规则同时写进 runner 面向的 `phase2-plan.md §2.1`。
- **N7｜P4｜`quality-report.md` 编辑的范围依据未书面登记**（见回潮表）。
- **N8｜P4｜handoff 落点引用为「§1.1/§1.4」**（`handoff:84`/`:85`/`:86`）：`calibration.md` §1 是编号列表（1–5），无 §1.1/§1.4 子标题，实指 §1 第 1/4 条；另 `handoff:102` 把差异归为「三类」，遗漏 `threshold_evaluation.reasoning` 文本增强（同属 R4/R5/R2 要求，非数值）。均属引用精度。

---

## NOT_VERIFIED

沙箱 `pwsh` 本轮仍不可用（`SetNamedSecurityInfoW failed: Win32 5: grantWrite(G:\CODEX\New Manga)`，与 r1 同因），以下为运行期项：

1. **脚本两次重跑 sha256 字节级一致**（Owner 声称）：未执行。静态可判定部分支持该声称——无时间戳字段、md 头部日期硬编码（`calibrate_determinism.py:448`）、唯一随机源为固定 seed（`:263`）、迭代全 `sorted`（`:347`、`:420`）、路径已相对化（`:766-776`）。旁证：main 侧 `doc/STATUS.md:14` 记「M2-QUAL-DETERM-CALIB（同 @8926f49c 复跑逐值一致，r2 复核中）」（编排方复跑记录，非本人一手）。
2. **`git status --porcelain` 干净 / `git diff --check` EXIT=0 / `git show --stat 8926f49c`**：未执行。间接佐证：7 文件 post-image 与 diff 逐块一致（脚本/JSON/MD/thresholds/report/Task/handoff 均逐行核对），新增行零行尾空白。
3. **fix diff 生成口径**（是否 path-filter / 是否 `2400b57a..8926f49c`）：未文档化；无法完全排除未展示文件。建议集成方 `git diff --stat 2400b57a..8926f49c`（应恰为 7 文件 +223/−46）与 `git diff --name-only 8996ca55..2400b57a`（确认未夹带禁改面）。
4. **NO_DATA 分支的一手执行证据**：无（见 N3②）。
5. **`--determinism-track` 及 runner 侧新口径实现**：全仓无实现（仅文档声明）。
6. **半成品草稿的 4 处修正**：草稿未入库，无法比对（`handoff:42` 等自述口径仅可读、不可核）。

---

## 推荐下一步

**交集成方（编排会话代行 Codex）执行集成：`git merge agent/zcode/M2-QUAL-DETERM-CALIB`（tip `8926f49c`，parents `2400b57a`；预期与 main `1d477b35` 无冲突，main 侧仅动了 `doc/STATUS.md`/`doc/REBASELINE_PLAN.md`），并把本报告原字节入库 `doc/reviews/M2-QUAL-DETERM-CALIB-8926f49c-dsh-r2.md`，同时把 `doc/STATUS.md:14` 与 `doc/REBASELINE_PLAN.md:173` 的「r2 复核中」更新为 `approved`/集成结论。**

可直接转发的执行指令：

> **集成方（Codex/编排会话）**：① 合并 `agent/zcode/M2-QUAL-DETERM-CALIB`（tip `8926f49c`）入 main，跑 post-merge 全量套件并记录结果；② 入库 `doc/reviews/M2-QUAL-DETERM-CALIB-8926f49c-dsh-r2.md`（DSH 非作者 r2，verdict=approved）；③ 用 `git diff --stat 2400b57a..8926f49c` 复核返修面恰为 7 文件/+223/−46 且 `qual-*.json` 零改动，并在集成 commit message 记明 `verification/M2-TA3-B/quality-report.md` 的修改依据（r1 R10 建议 + 字面允许面）；④ 同步 `STATUS:14`/`PLAN:173` 状态。
> **残留（非阻断，择一闭合）**：N1（`calibrate_determinism.py:192-194` docstring 改为「excludes empty_both；either side non-empty」或调实现为 `and`）、N3①（`quality-thresholds.md:168` 加「未加前置时」消歧）、N2（`:353` 增 `a["bbox"] is None or` 加固）——若 worktree 仍开放，交回 Owner（ZCode）一笔小修并更新 handoff；否则由集成 commit 一并修正并在 message 注明。
> **新开 follow-up（登记不释放）**：qualification runner 落实现行双轨口径（`run_qualification.py:851` 现仍对 remote 链做 export 哈希 fail-closed，与 `quality-thresholds.md:168/172` 冲突），含 track 选择/相似度 Gate/覆盖前置 NO_DATA/bbox 交叉校验，并把 N4 的判轨判据改用项目实际 provider id；顺带把 K01 追加进 `CALIBRATION_CASES` 以留下 NO_DATA 执行证据（N3②）。
