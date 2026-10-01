dsh: reasoning:
Let me start by reading the review inputs. Let me plan: read the task doc, handoff, diff, red log, and the actual source in the worktree.

Let me start with parallel reads.

Paths:
- G:/CODEX/New Manga.worktrees/M2-TASKS-BACKFILL-MULTIREGION-zcode
- diff: G:/CODEX/New Manga.task-envs/M2-TASKS-BACKFILL-MULTIREGION/review-input.diff

Let me begin.

Also I should consider using the code-review skill? The user gave an explicit output format; it's a static review. The skill "code-review" might be applicable but the user gave explicit instructions. I'll do it directly but maybe consult... The instructions say if task clearly matches a skill's description, call the skill tool before taking task actions. This is a code review of a branch. Hmm. The code-review skill runs parallel subagents with Standards/Spec axes. But the user's requested format is very specific. Loading the skill could add overhead. The guidance says "Load all applicable skills". I'd say code-review is applicable. Let me load it to check, but I should prioritize the user's explicit format.

Actually, let me be pragmatic: load the code-review skill, read its instructions, and adapt. But it may be heavy. Let me first read the artifacts, then decide.

Let me do reads in parallel.
dsh: reasoning:
I need to look at the actual source code in the worktree to verify claims. Let me read the relevant service.py sections.

Also I should check the red log claim: 6 failed = R0, R1, R2, F1, F4, F5. Handoff claims red includes "F1 主红/F4/F5+R0-R2 旧语义断言". Hmm - but handoff said "含 F1 主红/F4/F5 与 R0-R2 旧语义断言" - matches the log. But wait: F2 (single region unchanged), F3 (zero regions) pass in red - consistent. F5 fails in red? F5 asserts terminal_step_units == planned == 3; in the old code, planned would be 2 and terminal 2, so it fails. Yes.

Note that R3 is NOT in the red list - handoff says R3 assertion was changed to 1. In the red log, R3 passes. Hmm, but they said "初次红态曾为 7 failed（R3 当时断言 ocr_steps==2），后按 fan-out 执行顺序...将 R3 断言定为 1". Wait — but if f99a6c55 src + new tests = red, and R3 asserts len(ocr_steps)==1 ... In old code, only primary runs OCR, so len==1 passes. In new code, fan-out runs primary ocr first, then fails at color → secondary cancelled. So len(ocr_steps)==1 in green too. OK consistent. Actually wait: does the old code pass R3 for a different reason? Yes old code only runs primary. Fine.

Now key technical checks:
1. `_plan_region(run, task, region_view, region_snapshot)` signature — verify.
2. `_catalog.current(region_id)` returns view with `region_snapshots()`.
3. `run.planned_step_units` increment.
4. Whether `_plan_region` mutates task.units itself or returns units — the diff does `task.units + tuple(extra_units)`; need to check whether `_plan_region` also appends to task.units (double-append bug!) or appends to run. Let's read.
5. Failure containment F5: `_cancel_remaining` implementation — does it cancel units by task? Need to check that cloned units are cancelled.
6. `_plan_region` when region state changed/deleted: `self._catalog.current(region_id)` — what if region was deleted between detect commit and backfill? Could raise KeyError. In recovery path, `_plan_target` iterates live regions from catalog.current() so no stale ids. In backfill, region_ids come from detect outputs (snapshot) — if the region was deleted concurrently... within the same synchronous call right after detect commit, unlikely but possible in theory (another command?). This is the review point #1 about semantic equivalence. Let me check `_catalog.current` behavior for missing id.
7. Also `_plan_region(run, task, region_view, region_snapshot)` — does it use `task` to compute unit ids via task.task_id? And does it call `_decide_step` with `run`? Need to check that decisions use run's command/context not stale.

Also check whether `_plan_region` uses `region_snapshot` for lock checks and `_sfx_gate_suppresses`.

Also potential issue: duplicate unit ids. If a page already has a region-level unit for that region (e.g., re-plan?), backfill could duplicate. But backfill only happens on a regionless page plan. Hmm, but what about `already_bound` check? The diff shows code after `if not region_ids: return`. Let me read the full function including the early-return guard (maybe it returns if units already have region ids).

Let me read service.py in the worktree.

Also need to check `planned_step_units` for the primary path: does `_mark_terminal` increment terminal_step_units? The test asserts terminal == planned == 3, meaning terminal counts cloned units. Fine.

Let me read the file regions.
dsh: reasoning:
Shell command failed due to sandbox. Try without cd, using workdir param? The error is about grantWrite on G:\CODEX\New Manga — the session workspace is G:\CODEX\New Manga, and the worktree is outside it? "G:/CODEX/New Manga.worktrees/..." — that's a different path than "G:\CODEX\New Manga". Actually the worktree path prefix differs: "New Manga.worktrees" is a directory sibling. So it's outside the workspace root. Hmm, but reading files worked fine.

Let me retry git with workdir param.

Actually the file sandbox is workspace-write over G:\CODEX\New Manga. The worktree at G:\CODEX\New Manga.worktrees\... is outside. Reading works (read tool). Running pwsh with workdir there may fail on sandbox setup. Let me try running git with -C from the workspace.

The git command needs to run in the worktree. Try: `git -C 'G:/CODEX/New Manga.worktrees/...' log`. But sandbox setup itself failed. Let me try a plain command first to see whether pwsh works at all.
dsh: reasoning:
The pwsh sandbox fails for the workspace itself? "SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)". So pwsh is entirely unavailable. The user said "沙箱无 shell 时不执行命令，NOT_VERIFIED 留给集成方". So I'll rely on static reading.

Let's continue reading service.py: _decide_step 419-520 to see SFX gate and region handling; and backfill 900-1000; and the execute/cancel logic 620-800.
dsh: reasoning:
Important observations:

1. `_plan_region(run, task, region_view, region_snapshot)`: signature is (run, task, target: TargetSnapshot, region: RegionSnapshot|None). Here `region_view = self._catalog.current(region_id)` — so `target` = the REGION view (TargetSnapshot). Note in `_plan_target`, for a page it passes target=page view and region=each region snapshot; for region targets it passes target=region view, region=None.

In backfill, they pass target=region_view and region=region_snapshot. Then inside `_plan_region`:
- `steps = _COMMAND_STEPS[run.command_type]`; region is not None so no detect prepend.
- `target_id = region.region_id` ✓
- `current_revisions = region.current_revisions` ✓
- `lock = self._effective_lock(target, region)` where target=region_view → `_effective_lock` with region not None builds LockSnapshot(page_locked=target.lock.page_locked, region_locked=region.lock.region_locked, ...). Here target.lock is the *region's* lock snapshot (since target=region_view), not the page's. Hmm! `page_locked=target.lock.page_locked` — the region view's `.lock.page_locked` field. Does a region view's lock snapshot carry page_locked correctly? Need to check how TargetSnapshot for a region is built. Probably the region's lock snapshot includes page_locked from the page (since Lock is a combined object). In `_plan_target` for page: target=page view, region=region snapshot → page_locked from page lock, region_locked from region's lock. In recovery path for a region target (run_target.target_type REGION), target = region view and region=None → lock = target.lock entirely.

So passing region view + region snapshot: page_locked comes from region view's lock.page_locked. If the region view's lock snapshot's page_locked is populated correctly, fine. Need to check the catalog's region view construction — does `lock` for a region include page_locked? Let's inspect the catalog snapshot code.

Also `_decide_step(run, target=region_view, region=region_snapshot, ...)`:
- `_sfx_gate_suppresses(region)` ✓ uses region snapshot — same as recovery.
- translate lock checks use region.lock.translation_locked ✓
- `_clean_available(target.page_id, ...)` → target.page_id: for a region view, `.page_id` should be the parent page id. Need to check that region TargetSnapshot has page_id set. If it's None, `_clean_probe(page_id)` might misbehave for render step. But render step for REOCR_ALL etc... Let's check which commands include render in steps. For TRANSLATE_ALL steps include render probably. `_clean_available(None, ...)` → probe(None) could be a problem. Hmm, but the probe is optional (None by default in tests? `_clean_probe`) — "its production injection at assembly is wired by TASK-040". So in production it may be wired! Need to check whether `_clean_probe` is wired in bootstrap. If a region TargetSnapshot has page_id properly set, fine. Let's check.

Also note `_plan_region` uses `task.task_id` for unit_id — fine.

2. Note the potential double-planning issue: the primary rebind is only for units with `item.region_id is None`. Then in fan-out, if a region view contains multiple region snapshots (`region_view.region_snapshots()` could return multiple regions for a page view!) — wait, `self._catalog.current(region_id)` — what does current() return for a region id? If it returns a region-scoped TargetSnapshot, region_snapshots() returns... Let's check the catalog implementation. For a Region target, `region_snapshots()` might return the page's regions or just itself. In `_plan_target`, for a region-level run target, it calls `_plan_target(run, task, view)` where view is region view; then `region_views = target.region_snapshots()`; if `target.target_type is PAGE and not target.regions: ()`. For a region target with regions non-empty (?) it would iterate. Hmm — for a region-level command, target is the region view; if region_snapshots() returned the region itself, `_plan_target` would call `_plan_region(run, task, target, region)` with target=region view and region=that region. That's exactly what backfill does. Let me check catalog.

Let me find the catalog code: `src/application/...`? Let's grep for `region_snapshots` definition and `def current`.

Potential bug: double fan-out. In backfill, for each region_id in region_ids[1:], they call `self._catalog.current(region_id)` then iterate `region_view.region_snapshots()`. If region_snapshots() on a region-scoped view returns ALL regions of the page (not just itself), then each additional region would be planned for every region — producing N*(N-1) chains with duplicate unit_ids. That would be a real P0/P1. Need to verify.

Let me grep in src for `def region_snapshots` and `def current`.
dsh: reasoning:
Important: `SqliteTargetCatalog.current(region_id)` returns `self._region_or_error(target_id)` — a REGION-type TargetSnapshot. What does `_region_or_error` set for `regions` tuple and `page_id` and `lock`? Let's read it. And `TargetSnapshot.region_snapshots()` implementation at models.py:261.

If `_region_or_error` builds a TargetSnapshot with target_type=REGION, regions=() (empty), then `region_snapshots()` likely returns `self.regions`. In that case `for region_snapshot in region_view.region_snapshots()` would iterate ZERO items → the fan-out would produce nothing! That would be a P0 (the whole fix does nothing) — but tests pass 17/17, so presumably `_region_or_error` sets regions=(the region itself,). Let's check. Also InMemoryTargetCatalog.current in store.py:159.

Let me read.
dsh: reasoning:
Good: for a REGION-type snapshot, `region_snapshots()` returns exactly one region (itself, or the matching one from `regions`). So the loop always iterates exactly one region — that's a bit roundabout but correct. Note: it returns the matching region from `self.regions` if present (which contains the full region data), else synthesizes from the target fields. So the SFX policy might be LOST if the synthesized fallback is used! Look: the fallback RegionSnapshot does NOT pass `region_type` or `sfx_policy` — so it defaults to region_type="speech", sfx_policy=SfxPolicy.SKIP.value!

That is a critical issue: if `_region_or_error` returns a TargetSnapshot with `regions=()` (empty), then `region_snapshots()` synthesizes a RegionSnapshot without sfx_policy → default "skip" → `_sfx_gate_suppresses` would return True for SFX regions... wait default sfx_policy = SKIP → gate suppresses → SKIP_POLICY. For a genuine SFX region with policy=translate, the fan-out would skip it — which would make the e2e translate test fail... unless `_region_or_error` populates `regions`. The e2e translate test now asserts the SFX region IS translated, and it passes (per Owner's green logs). So presumably `_region_or_error` sets regions=(region_snapshot,) with proper sfx_policy. Let's verify by reading _region_or_error.

Also note the target snapshot's `lock` for a region: `_region_or_error` sets lock. Let's read lines 625-720.
dsh: reasoning:
Good. `_region_or_error` returns `regions=(region,)` with full sfx_policy/region_type. So the `region_snapshots()` loop yields exactly one region with correct data. And lock: page_locked from page row, region fields from region → `_effective_lock(target, region)` with target=region view gives page_locked=region_view.lock.page_locked (true page lock) and region lock fields from region snapshot → identical to what a page-view plan would compute. 

Now, `TargetSnapshot.region_snapshots()` returns `self.regions` matched by region_id — the region object. Then in `_plan_region`, `target_id = region.region_id` ✓, current_revisions from region ✓, stage_states from region ✓.

BUT: note in `_plan_region`, when region is not None, `lock = self._effective_lock(target, region)` → uses target.lock.page_locked. ✓.

One subtle difference vs `_plan_target` page path: In page path, `target` = page view whose `stage_states` are page-level; `_decide_step(run, target, region, ...)` — inside `_decide_step`: `_required_input_available(step_type, stages, previous)` where `stages` = region.stage_states (passed in the call from `_plan_region` — `stage_states` variable = region.stage_states). Also `_clean_available(target.page_id, stages, previous)` uses target.page_id. In backfill, target is the region view whose `page_id` == page id ✓. So equivalent.

Another subtlety: `_plan_region` uses `region_view.region_snapshots()` result vs `region` param — they call `_plan_region(run, task, region_view, region_snapshot)` where region_snapshot came from region_view.region_snapshots() → consistent.

Now, a real difference between recovery path and this backfill: in recovery path, `_plan_target(run, task, view)` with view = page snapshot; it iterates `target.region_snapshots()` = all regions sorted by reading_order... wait for PAGE type returns self.regions which is ordered by reading_order, region_id ✓. In backfill, fan-out set = detect output order (region_ids[1:]).

Now region_ids[0] = primary; the detect handler produces region_ids via reading_order for reuse path. Potential mismatch: does detect's ordering match `regions.list_regions` sorted by reading_order? For new creation path, order = candidate order. Fine.

Potential issue: duplicate unit ids if the page's regions already had units? Backfill only runs when detect ran, which only happens for regionless page plan → no region units existed. But what if the primary rebind loop... `item.unit_id != unit.unit_id and item.region_id is None` — this rebinds ALL regionless units to primary (including possibly steps for other... fine, existing behavior).

Now: could `region_ids` contain ids not in the catalog (deleted between detect commit and backfill)? `_catalog.current(region_id)` raises PipelineError("TARGET_DELETED"/"TARGET_NOT_FOUND") — inside `commit_step_result` after detect commit. Would that propagate? Let's look at commit_step_result's error handling around line 600-700 to see if a raised PipelineError there is handled or crashes the run. Also whether `self._catalog.commit_step` already committed the detect; raising after commit could leave state inconsistent (exception propagates out of commit_step_result → execute_run?). Let's read lines 569-800.

Also, the review point about "region 已被删除/状态已变": recovery path re-reads live regions and never sees deleted ones (page view excludes deleted). Backfill uses detect output ids; if a region was deleted in the window (between detect commit and backfill call — same synchronous call, no interleaving within a single-threaded process... but could another thread/process delete? Possibly via UI). Then PipelineError propagates. Need to assess severity: it's an edge case. Let's see how errors in commit_step_result are handled.

Let me read the execute_run and commit_step_result.
dsh: reasoning:
Continue reading 768-905 for the execute loop, failure handling, cancellation, and interrupted.
dsh: reasoning:
Important: the fan-out happens inside `commit_step_result` for the detect step. In `execute_run`, the index-based loop: after detect commit, `task.units` is replaced with the rebind + appended clones. The loop continues to next index → proceeds through the primary chain (original units after detect), then reaches the cloned units. Good.

Now a critical semantic question for **F5 / failure containment and ordering**: the appended cloned chains are placed AFTER the whole primary chain. Since the primary chain is [detect, ocr, color, term_extract, translate, segment, mask_refine, inpaint, render] presumably, appended clones for region 2 = [ocr, color, ...]. When primary fails at some step, `_cancel_remaining(run, task, unit)` marks all later RUN units of the task terminal (not counting SKIPs? It marks terminal for units with decision RUN after current). Those cloned units get cancelled (marked terminal) — consistent with F5.

Now consider the case where a primary step fails at ocr but the cloned units are appended... fine.

Now potential divergence from recovery semantics: In the recovery path, `_plan_target` produces units per region in region order — for a page with 2 regions: [r1 chain..., r2 chain...]. Same ordering as backfill (primary chain first then clones). Good.

But there's a subtle issue: In recovery path (mode=continue), the task is re-planned; `run.planned_step_units` recomputed as sum. In backfill path, planned_step_units increment. Fine.

Now — the crucial review point 1: semantic equivalence of `_plan_region` reuse:

(a) `_plan_region` receives `target=region_view`. Differences vs page path:
   - `_effective_lock(target, region)` → page_locked from region view's lock (present, from page row) ✓; region lock from region snapshot ✓. Equal.
   - `_clean_available(target.page_id=page id)` ✓.
   - `_provider_available(run, step_type)` ✓ same run.
   - `_decide_step`'s `stages` param = region.stage_states ✓ (page path also uses region.stage_states).
   So decisions are equivalent to what the recovery path would compute for that region. ✓ Good — the Owner's core claim holds statically.

(b) `region_snapshots()` for a REGION target: returns the matching region from `regions` if present else synthesizes WITHOUT region_type/sfx_policy → default skip. In the InMemory catalog, `_region_or_error` presumably sets regions=(region,) too? Let's check store.py's `_region_or_error` (lines ~85-120). If InMemory's `_region_or_error` does NOT populate `regions`, then in tests the synthesized fallback loses sfx_policy → SFX regions would be SKIP_POLICY. And the e2e translate test uses which catalog? It's an end-to-end test with core assembly → sqlite catalog (which populates regions=(region,) ✓). Need to check InMemoryTargetCatalog too, since the pipeline tests use `_build_service(workspace)` — let me check the test helper to see which catalog it uses.

Actually more important: is `region_snapshots()` fallback path reachable in production? Only if `self.regions` doesn't contain a region with matching region_id while target_type is REGION. For SqliteTargetCatalog `_region_or_error` always sets regions=(region,) → not reachable. For InMemory, check.

Let me look at store.py lines 85-125 and the test helper.

(c) The `current()` call raises for deleted region → exception propagation. In `commit_step_result`, `_backfill_detected_regions` is called after `commit_step` applied (detect committed, DB committed regions). If `self._catalog.current(region_id)` raises PipelineError (TARGET_DELETED), the exception propagates out of `commit_step_result` → out of `execute_run`'s call at line 799 (not wrapped in try/except — the try only wraps `self._executor.execute`). So the exception escapes `execute_run` to the caller (application layer / Tauri command). The run would be left RUNNING with detect completed but not marked terminal yet (`_mark_terminal` after backfill call at 658 is skipped!) → run stuck in RUNNING, only recoverable by `recover_running_runs` → INTERRUPTED. That's a new failure mode introduced by fan-out (before, no catalog read happened for region_ids[1:]). But how likely? The region must be deleted between detect's commit and the backfill call — both inside the same synchronous call, no I/O in between except... `self._catalog.commit_step` (which commits DB transaction). Not concurrent normally. Single-threaded UI. So it's a theoretical race, worth a P3/P4 registration. Also could region_ids contain a stale id from detect outputs (e.g., reuse path outputting ids of regions that were deleted before detect ran? unlikely).

Hmm, wait — there's a more realistic case: **detect output ids from the reuse path** — if detect reuses existing regions it returns their ids; those exist. Fine.

But there's another realistic failure: `_region_or_error` requires the page to have `width/height/source_hash/managed_original_ref` etc.; the page already passed `_page_or_error`-ish checks at plan time. For a page-level run, the target page was expanded via `_page_or_error` which requires source_hash and managed_original_ref, but NOT width/height! Look: `_region_or_error` WHERE includes `p.width IS NOT NULL AND p.height IS NOT NULL`. `_page_or_error` doesn't require width/height. So a page that has no width/height (not yet probed) would plan fine as page target, detect runs and creates regions, then backfill calls `current(region_id)` → `_region_or_error` → row is None → PipelineError("TARGET_NOT_FOUND", region_id) → escapes commit_step_result → execute_run raises, leaving run RUNNING. Hmm! Is width/height guaranteed after detect? detect reads the page image; does the detect handler populate width/height? Possibly the detect step writes page dimensions... Let me check. In the InMemory catalog, `_region_or_error` may have similar preconditions.

That would be a P2-ish robustness finding: the fan-out path introduces a new hard dependency on the page having width/height (and the region row being non-deleted) *inside* commit_step_result, outside error handling. Recommendation: wrap in try/except PipelineError → treat as TARGET_DELETED-ish (skip or fail the task gracefully via `_fail_step`/registration), or use a snapshot-derived region view. But do I know whether width/height is set before detect? Let me check the page creation flow: pages get width/height when imported/measured. `_page_or_error` doesn't check. Let me grep for "width" in pipeline.py / ingestion to see when set. Given M2 scope, page dimensions come from managed copy inspection at import. Likely always set for imported pages. Still, `_region_or_error` checks it, so there's a theoretical gap. I'll register as P3 (low likelihood) with the note that exception is unhandled → run stuck RUNNING.

Let me now verify the InMemory catalog's `_region_or_error` and the test builder. Then check the SFX gate function `_sfx_gate_suppresses` (whether it covers manual/skip AND translate policy), and D06 §85.

Then check the e2e test file for the new assertions and the SFX translate flow (whether the translate unit for the SFX region is actually executed in the same run: the e2e test asserts `regions["sfx"]["text"]["machine_translation"] == MOCK_SFX_TRANSLATION_TEXT` right after the TRANSLATE_ALL run).

Also check whether the e2e test's earlier steps still hold: the run is one TRANSLATE_ALL run on a page that already has regions? Wait — the chain shape comment says "a page task planned before any Region existed binds its region steps to the detected regions ... one TRANSLATE_ALL run follows up on every detected region". So in the e2e, the page has no regions before the run; SFX policy came via settings channel reaching region creation. The SFX region plannned/created by detect gets sfx_policy=translate from settings. Then the cloned chain plans translate (policy gate admits translate → `_sfx_gate_suppresses` false) and production handle_translate executes → mock provider returns SFX text. Good.

For manual: OCR runs; then RETRANSLATE_REGION... plans registration (SKIP_POLICY?). The gate is plan-layer; the author claims "manual keeps Detect/OCR for the human" and RETRANSLATE_REGION plans SKIP_POLICY. With fan-out, the cloned chain for manual region: ocr RUN, translate SKIP_POLICY, and propagation to segment/mask_refine/inpaint/render. Let's confirm `_sfx_gate_suppresses` and `_SFX_GATED_STEPS`.

Let me read the SFX gate helper (probably in a policy module or in service.py).
dsh: reasoning:
Now check `_region_or_error` in InMemoryTargetCatalog (lines ~300-358) and the SFX gate in service.py lines 140-175 and gate.py.

Also: does InMemory `current()` for a newly created region (created by detect handler / editing service) find it? `current(target_id)`: if target_id in self._pages → page; else `self._region_or_error(target_id)`. In-memory catalog pages hold regions; detect creates regions via... hmm, in the pipeline tests, `_build_service(workspace)` uses a real sqlite catalog? The test workspace has "regions" and "editing" services. Let me read the test file's `_build_service` to see. The F4 test does `editing.create_region(...)` — so the catalog used by PipelineService must see the new region. If InMemoryTargetCatalog were used, `editing.create_region` wouldn't update it. So probably it uses SqliteTargetCatalog over the same conn. Let's read the test header.

Note: in that case `_region_or_error` = sqlite version which requires width/height not null; the test workspace pages must have those set. Let me check `_build_service`.
dsh: reasoning:
The sqlite catalog is used (SqliteRegionRepository + RegionEditingService + conn). Let me confirm _build_service constructs SqliteTargetCatalog. Let me read 239-300 of the test.

Also check the gate.py decide_sfx_translation to confirm policy semantics.

Then check the e2e sfx test to verify the new translate assertion path — need to confirm the run executes the cloned translate unit and that the mock provider requires region_type == "sfx". Also whether the "speech" region assertion remains.

Let me read those.
dsh: reasoning:
Good. The SFX gate is genuinely consulted inside `_plan_region` → `_decide_step` when region is not None. And `_plan_region` receives region from region_view.region_snapshots() which for the sqlite catalog has correct region_type/sfx_policy. So claim holds.

Now the key question 1b: does the recovery path also produce the same result for SFX regions? Yes — recovery path uses `_plan_target` with page view → same `_plan_region`.

Now: `region.region_type` — in the fallback synthesis path of `TargetSnapshot.region_snapshots()`, region_type defaults to "speech" → gate not applied. But sqlite catalog always populates regions. For InMemoryTargetCatalog's `_region_or_error` — need to check. Not production-critical but affects tests that use InMemory catalog (other test suites). Let me check InMemory's `_region_or_error`.

Also need to check: could `_catalog.current(region_id)` for the *backfill* be the InMemory catalog in some production wiring (bootstrap `_ManagedPageCatalog` at core_assembly.py:156)? There's a `_ManagedPageCatalog` in bootstrap! That might wrap the sqlite catalog. Let's check `current()` there — whether it's a PAGE catalog only (no region support → would raise KeyError/AttributeError for region ids). Let me read core_assembly.py around 156 and check whether PipelineService is wired with `_ManagedPageCatalog` or `SqliteTargetCatalog`.

Let me grep for build_production_pipeline and its catalog wiring.
dsh: reasoning:
Good: `build_production_pipeline` wires `SqliteTargetCatalog(conn)` → production path uses region-aware `current()`. ✓

Now let me examine the e2e SFX test file in full to assess item 4 and the assertion change rationale (test_sfx_policy_end_to_end.py belongs to M2-SFX-TRANSLATE-ENTRY deliverable). Check whether modifying it is reasonable, and whether the translate assertion is truly driven by the fan-out (i.e., would it fail on old code → red). The red log only lists test_regionless_rebinding failures, not the e2e file (the red run only ran the rebinding file). Owner didn't archive a red log for the e2e file. That's a gap: the e2e assertion change (translate region now translated) has no archived red evidence, though the red state log was run only on the rebinding file. Note handoff says "被 e2e manual 红态抓到" (initial implementation caught by e2e manual red) — that's a different thing (the clone-copy implementation). Not necessarily a defect, but worth registering P3: no archived red log for the SFX e2e assertion change (the 19-passed target-file log covers only green).

Also verify: is the e2e translate test's SFX region created by detect with policy=translate from settings? Let me read the file.

Also verify test for manual: after the fan-out, does the manual SFX region's cloned chain skip translate? The manual test asserts something; check it still passes logically (OCR runs? which run?). Let me read the whole e2e file.
dsh: reasoning:
Now the translate test: the TRANSLATE_ALL run on the CHAPTER scope. Chain steps for TRANSLATE_ALL — need _COMMAND_STEPS. For the SFX region (reading_order 2, region_type sfx, policy translate), the cloned chain: steps for TRANSLATE_ALL probably ("ocr","color","term_extract","translate","segment","mask_refine","inpaint","render") etc. The gate admits translate (policy translate → not skipped) → RUN. Then segment/mask_refine/inpaint/render also gated? `_sfx_gate_suppresses` false → they proceed normally (subject to provider availability). Some might be BLOCKED (provider unavailable) — but the run is COMPLETED per test? The test doesn't assert first_run status. It asserts detect completed, speech translated, sfx translated. OK.

But wait — a subtle point for the SFX region: `translate` requires ocr stage or previous ocr RUN. In the cloned chain, previous "ocr" decision is RUN in the same chain (since stages empty for a fresh region → ocr RUN) → OK. And in the primary speech chain the same.

Hmm, but with clone-by-decision-copy (initial implementation), the sfx region's cloned chain would copy primary's translate RUN decision → translation with wrong region_type → mock returns MOCK_TRANSLATION_TEXT... Actually the mock only returns SFX text for region_type sfx. Under decision copy, the translate handler gets the *cloned unit* whose target_id = sfx region_id; the handler reads the region → region_type=sfx → mock returns MOCK_SFX_TRANSLATION_TEXT. Hmm, so why would the manual case fail with clone? Because decision copy would copy primary's translate=RUN → manual SFX gets machine translated. Yes, that's the manual red.

OK. Now the manual test: `test_manual_policy_keeps_the_sfx_region_untranslated` — with fan-out, in the first TRANSLATE_ALL run, the SFX clone chain: translate → SKIP_POLICY. And the assert `text["machine_translation"] == ""` at the end (after RETRANSLATE_REGION, which for a region command skips policy). Fine. But note: with fan-out, the first run's cloned chain for manual SFX includes ocr RUN → so the SFX region gets OCR text in the first run. The manual test then runs OCR_REGION again — fine. But: does the SFX region's OCR in the first run cause the later `RETRANSLATE_REGION` to plan `translate` as... the docstring says manual keeps Detect/OCR. Fine. The test passes per green logs (the manual test still asserts `decision.value == "skip_policy"`).

Wait, actually, one thing to check: in the manual test the docstring/comment at lines 11-33 says "one TRANSLATE_ALL run follows up on every detected region" — consistent.

Now, is there any assertion in the manual test that would have been affected (e.g. `speech` translated)? No change needed. The diff only modified the translate test's assertion + the module docstring. So the diff for test_sfx_policy_end_to_end.py = docstring + one assertion. Reasonable registration (Task says tests/ tasks-related; this file is SFX-ENTRY deliverable). The Task's allowed面 says `tests/`（tasks 相关）. Modifying an SFX e2e test is adjacent — Owner registered it in Task/docstring. Acceptable but worth noting the ownership: modifying another Task's delivered test assertions requires integrator awareness; the change is semantically forced by the new behavior. Fine.

Now the important review items remaining:

A. Does the new e2e translate assertion actually prove the *fan-out* (i.e., would it fail before the fix)? Yes: before the fix, the SFX region had no units at all in that run → machine_translation == "". So the assertion flipped from "" to MOCK_SFX_TRANSLATION_TEXT is a real red→green. But the red evidence for this specific e2e assertion was NOT archived (red log is rebinding-only). Also, is the e2e file in the "3 suites" (tests/core)? Yes.

B. Now deeper risk analysis of the fan-out implementation:

1. **Duplicate regions in region_ids**: if detect output contains duplicates, extra chains duplicate unit_ids. Pre-existing.

2. **`region_ids` may include the `primary` for pages where detect output order isn't reading order** — fine.

3. **The big one: `task.units` append + `planned_step_units` increment vs terminal accounting.** `_mark_terminal` for detect happens AFTER backfill (line 658). Fine.

But consider: cloned units that are non-RUN decisions (SKIP_VALID/SKIP_POLICY/SKIP_LOCK/BLOCKED) are never marked terminal during execute (the loop `continue`s on SKIPs without marking terminal; BLOCKED breaks). So `terminal_step_units` <= `planned_step_units`. Tests assert equality in specific cases. In F5 they assert 3 = 3: detect(terminal) + failed primary ocr(terminal) + cancelled secondary ocr(terminal via `_cancel_remaining` which marks only RUN-decision units after current). ✓.

But in R2 test they assert `terminal == planned == 1 + len(all_regions)` for REOCR_ALL: units = detect + ocr(primary) + ocr(clone) — all RUN. ✓.

Consider a multi-region page where the clone chain has SKIP decisions (e.g., TRANSLATE_ALL with a region whose ocr stage is valid → ocr SKIP_VALID) — then terminal < planned forever? Let's look at how non-RUN units are accounted: In `execute_run`, SKIP units are skipped without `_mark_terminal`. So terminal_step_units would be less than planned_step_units → the run's progress never reaches 100%. Is that pre-existing behavior for the page path (primary chain also can contain SKIPs)? Yes — e.g., for a page with existing regions, plan produces SKIP_VALID units which never become terminal. So this is pre-existing behavior, not introduced. But progress metrics might now be distorted for multi-region pages: `get_task_progress` counts... let me check how `get_task_progress` computes waiting/processing and whether it uses terminal_step_units. Let me read 1029-1105.

Hmm — actually wait. Is it pre-existing that SKIP units are never terminal? Let me check `_planned_task_status` and run status: if all decisions are SKIP → task SKIPPED. In execute_run loop, `task.status` stays PENDING (initial) then at end `elif task.status is PipelineTaskStatus.RUNNING: → COMPLETED`. If a task had only SKIP units (never RUNNING), its status stays PENDING → `_aggregate_run` sees statuses - TERMINAL → RUNNING. Hmm, that's pre-existing unrelated.

Let me check `_plan_target`... Actually this is out of scope. Focus.

4. **Serial order & cancel semantics for the cloned chain and `_cancel_remaining` matching by unit_id**: `_cancel_remaining` iterates task.units and starts marking after the current unit's unit_id. Since cloned unit_ids are unique, fine.

But careful: `_cancel_remaining(run, task, unit)` is called with `unit` = the failed unit. The loop `if current is not None and unit.unit_id == current.unit_id` — compares task unit ids to current.unit_id; the failed unit is in task.units. ✓.

5. **`retry_failed_targets`** → create_run with PAGE_SELECTION → new run, page now has regions → `_plan_target` fans out over live regions. ✓ (recovery semantics).

6. **Pause/resume: `plan_run(mode="continue")` re-plans from live catalog**, replacing task.units entirely — so cloned units are discarded and re-planned. Fine (documented as N7).

7. **The `region_ids` snapshot vs live**: F4 test asserts a region added mid-run isn't followed. But hold on — F4's scenario: the OCR handler (called for the primary chain) creates a third region. The fan-out set was captured at detect commit (2 regions). Then the 3rd region isn't followed. But: the new region was created *after* detect → it has no OCR text; the run completes "COMPLETED" while a region lacks OCR. Is that acceptable? Documented as snapshot semantics. Reasonable. But there's an interesting consequence: for a page where the user adds regions during a run, the run reports COMPLETED with a regionless-of-OCR region — pre-existing? Before the fix, secondary regions also didn't get OCR at all, so no regression.

8. **Lock snapshot semantics for cloned units**: expected_lock = `_effective_lock(region_view, region_snapshot)` computed at backfill time. `_record_step_attempt` re-reads `self._catalog.current(unit.target_id)` for input_refs/lock — not using unit.expected_revisions. Indeed `expected_revisions` from the unit is only used... hmm, `_record_step_attempt` sets input_refs from live current. So plan-time expected values are unused at execution? Let me check — `StepRun.input_refs` from live. So the lock/current_revisions from plan aren't used in commit. Then the decision SKIP_VALID based on stages matters for whether the step runs. Fine.

9. **Bigger semantic question: does `_plan_region` for the fan-out use stage_states that may be stale relative to the just-committed detect?** For the *primary* path, the unit decisions were computed at plan time (before detect created regions) — primary chain decisions are plan-time decisions with region=None: for REOCR_ALL, steps=("detect","ocr") → ocr decision computed with region None, stages = page stage_states, lock = page lock, `_sfx_gate_suppresses` not applied (region None!), `_required_input_available` uses page stages. So the primary chain's decisions ignore SFX policy! That's a real asymmetry: for the primary region, the SFX gate is NOT applied (plan-time, region None). So a multi-region page where region_ids[0] is an SFX region with policy=manual/skip: the primary chain would translate it! Is that pre-existing? Yes — pre-existing behavior (rebind doesn't re-decide). And the new fan-out applies the gate to regions[1:]. So for a page whose *first* detected region is SFX with policy skip/manual, the primary chain still translates it (pre-existing defect, unchanged). Hmm — but the e2e test has speech as reading_order 1 and sfx as reading_order 2, so the SFX is secondary and gated. But wait: the manual e2e test asserts `text["machine_translation"] == ""` for the sfx region. Since sfx is secondary, gate applies → skip. ✓. But if the detector returned sfx first (reading_order 1), the primary chain would have translated it (no gate) → the manual e2e assertion would fail. That's a genuine *remaining* inconsistency: "initial vs recovery semantics" is only half-fixed — the primary's decisions are still plan-time page-level decisions rather than region-level ones. Actually, hmm, is that true? Let's check: for the page path, `_plan_target` → page target, no regions at plan time → region_views=() → `_plan_region(run, task, target, None)` → region None → SFX gate skipped (`region is not None` condition) → translate RUN (if provider available & steps). So yes: for a regionless page plan, the entire primary chain ignores SFX policy. The SFX gate applies only to region-level steps for regions known at plan time.

So: **the fix creates a new inconsistency between primary and secondary regions when the primary region is SFX with manual/skip policy**: primary (rebound in place, plan-time decision) gets translated; secondary (fan-out, gate applied) gets skipped. This is exactly the D06 §85 violation surface the Owner claims to have closed, but only for regions[1:]. Owner's risk register #1 says "policy=manual/skip 的 SFX region 由 plan 层 SKIP_POLICY 保持不翻译" — that claim is true only for non-primary SFX regions. This is a genuine finding! Severity: is it a regression? No — pre-existing for primary. But it's within the exact defect class ("initial vs recovery semantics不一致") and it's arguably *newly reachable*: before fan-out, multi-region pages only ran the primary region; now the fan-out makes the asymmetry observable in the same run — a page whose first detected region is SFX/manual gets machine-translated while its second SFX/manual region is skipped. Hmm, before the fix, the same primary translation happened too (it was the only region processed). So behavior for the primary is unchanged. It's a residual gap / incomplete claim rather than a regression.

Wait, actually let me double-check the primary chain under decision: the primary chain units were planned with region=None. For the *translate* step: `_decide_step` with region None:
- `_sfx_gate_suppresses` not evaluated (region None) → no SKIP_POLICY.
- translate lock: `lock.translation_locked` from page-level lock... `_effective_lock(target, None)` = target.lock = page lock → `translation_locked` False at page level (LockSnapshot page). So translate RUN.
Yes. So an SFX region as the primary region WILL be machine-translated in TRANSLATE_ALL when policy=manual/skip. This violates D06 §85 for the primary. Pre-existing, but the Task's AC/discipline says "既有 backfill 行为（单 region 页）零变化" — which is preserved deliberately. And for a *single-region page* that region is SFX with manual policy: pre-fix behavior = translated. So "zero change" means keeping a D06 §85 violation. Hmm, but is there a test for that (single SFX region page with manual policy)? The e2e uses two regions. Let me check test_sfx_policy_settings.py in tests/core for a single-SFX-region scenario... The M2-SFX-TRANSLATE-ENTRY deliverable presumably tests region-level commands. Also, is there a mitigation: the detect handler's region creator applies the settings policy → SFX region created with policy manual. Then the primary chain planned pre-detect has translate RUN → translated. In a single-region page this is a real D06 §85 violation for automatic runs.

Hmm wait. But maybe the production handle_translate itself checks the gate? Owner explicitly says "production handle_translate 不经 gate". Let me verify quickly — grep handle_translate for gate usage. If it doesn't check, then yes.

This is a significant finding for the review: the SFX gate closure is partial (fan-out regions only), and the Owner's handoff/Task claim "改用 _plan_region 后 gate/lock/stage 决策与恢复路径逐字节一致" is overstated for the primary chain — but the primary chain is explicitly preserved for "zero change". So: register as P2 finding (residual defect, documented partially) — the primary chain's plan-time page-level decisions mean SFX policy is not applied to the first detected region; recommendation: either also re-decide the primary chain from the live region snapshot (with the risk of changing single-region behavior) or register a follow-up Task. Note that the Owner's stated design principle ("initial and recovery semantics must agree") is violated for exactly the primary region — a direct AC1/AC2 contradiction worth flagging.

Hmm, but careful: for a single-region page, re-deciding the primary chain would change behavior (e.g., a page whose only region is SFX-manual would no longer be translated). The Task's discipline says single-region pages zero change. So the Owner consciously chose not to re-decide. Since the Task's AC2 says "最小语义修复", and the primary chain re-decision would change single-region behavior, this is a defensible scope boundary BUT it must be registered as a known residual inconsistency (not claimed as "closed"). Note also it means "SFX-ENTRY 相邻发现" of the same class remains.

Actually — wait. Let me reconsider. Is it possible that the primary chain's decisions ARE region-aware because of something else? For a regionless page plan... `_plan_target(run, task, view)`: `region_views = target.region_snapshots()`; `if target.target_type is PAGE and not target.regions: region_views = ()`. Then `if not region_views: units.extend(self._plan_region(run, task, target, None))`. Yes region=None.

But hold on — for TRANSLATE_ALL on a *chapter* scope where the page already has regions (created by a previous detect), the plan is region-aware. Only the initial regionless plan has region=None for the whole primary chain. That's exactly the backfill scenario. So the residual gap: the primary region's chain keeps page-level (pre-detect) decisions — including no SFX gate, page-level lock, page-level stage_states, and `_required_input_available` against page stages.

Hmm, this reveals an even more important pre-existing issue: the primary chain's `_decide_step` for steps beyond ocr (color/term_extract/translate/segment/...) evaluated `stages` = page.stage_states (not region stages). Since the page has no region stages yet, `stages.get(required)` is NOT_STARTED, and `previous.get(required)` is RUN (for the plan-time chain) → requirements satisfied via previous. OK.

So the primary chain is fine functionally, except the gate/lock nuance.

Now, is there any test in the green suite for "single-region SFX page under manual policy not translated"? If such a test existed, it'd fail. Let me grep tests for `manual` + single region... The e2e test_sfx_policy_settings.py (M2-SFX-ENTRY) — let me check what it covers. It's in tests/core. Since the three suites pass 579, whatever exists passes. Let me check whether there's a single-region SFX manual test that exercises the page-level backfill path. Let me grep.

Let me also verify handle_translate lacks the gate (to confirm the Owner's core claim, since if handle_translate DID check the gate, the whole "clone" argument would be moot and the fan-out would be safe either way).

Let me grep for handle_translate and for the SFX gate usage in providers/handlers.
dsh: reasoning:
Interesting: `application/translation/context/step.py:176` uses decide_sfx_translation — this might be the translate step path? Let's check: `handle_translate` in handlers.py:382 — does it use `translation/context/step.py`? The Owner says "production handle_translate 不经 gate". Let me check handlers.py:382 and step.py:176 to confirm which path is production.

Note `_unit_decisions` in e2e reads plan decisions. The e2e's RED finding was about the `manual` scenario: with decision-copy, translate plans RUN → handle_translate executes → since handle_translate doesn't gate → manual SFX gets translated → assertion `machine_translation == ""` fails. Consistent.

But if step.py:176 (the SFX gate at the step layer) is used in some translation path, the clone approach might still be gated. Let's check.

Also note the `progress` metric: `terminal_step_units / planned_step_units`. For fan-out with SKIP units, terminal < planned → progress < 1.0 even after COMPLETED. Pre-existing for page plans with regions; but the fan-out increases the denominator with cloned units, some of which may be SKIP (e.g. an SFX-manual region's translate/segment/inpaint/render are SKIP_POLICY → never terminal). So a COMPLETED multi-region TRANSLATE_ALL run on a page with an SFX-manual region would report overall_progress < 1.0 forever. Hmm — is that a regression? Before the fix, planned_step_units = 2 for REOCR_ALL and all terminal. Now planned includes cloned SKIP units → progress never reaches 1.0. That's a **user-visible progress regression** (progress bar stuck below 100% for runs with policy-skipped cloned units). Is it real? Let's check: does `_mark_terminal` get called for SKIP units anywhere? In execute_run loop: `if unit.decision is SKIP_VALID or SKIP_LOCK or SKIP_POLICY: continue` → no terminal marking. Also in `plan_run`, `terminal_unit_ids.update(unit.unit_id for unit in units if unit.decision.is_terminal)`. What is `PlanDecision.is_terminal`? Let's check: PlanDecision enum with is_terminal property — maybe SKIP_VALID/SKIP_LOCK/SKIP_POLICY are "terminal"! In plan_run: `run.terminal_step_units = len(terminal_ids)` counts units whose decision is_terminal. If SKIP_* count as terminal, then planned == terminal for skip-only tasks, and progress = 1.0. Let's check the enum definition. That resolves it.

Let me look at PlanDecision in domain/tasks/models.py.
dsh: reasoning:
There IS a step-layer gate: `execute_translate_step` gates SFX. Is it used by the production `handle_translate`? Let's read handlers.py:382 region and see whether handle_translate calls execute_translate_step or builds a request directly.

The Owner's claim "production handle_translate 不经 gate" is crucial. If FALSE (i.e., handle_translate DOES gate), then the manual e2e would pass even with decision-copy... but then the Owner's red-state claim about the manual scenario would be unfounded. However, the Owner says the manual e2e caught it — maybe the manual failure was actually something else. Let me check handlers.py.

Also read PlanDecision.is_terminal (line 122-140).
dsh: reasoning:
Confirmed: production `handle_translate` does NOT call `decide_sfx_translation` — it only passes region_type into the request. So the plan-layer gate is the only automatic-translation defense. Owner's claim ✓ (this is important: it means the "decision copy" alternative would indeed have violated D06 §85 for cloned manual/skip SFX regions). Good.

And `PlanDecision.is_terminal` = not RUN and not BLOCKED → SKIP_* are terminal. So `plan_run` counts them in terminal_step_units. But wait: in the backfill, `run.planned_step_units += len(extra_units)` — but the terminal count for the cloned units that are SKIP_* is NOT incremented! In `plan_run`, terminal_ids included SKIP units. In backfill, only `planned_step_units` grows. So for cloned units with SKIP decision (e.g., an already-valid region whose ocr stage is COMPLETED → SKIP_VALID; or SFX-manual → SKIP_POLICY), `terminal_step_units` will NOT count them → **progress < 1.0 permanently** for such runs (terminal/planned), and `terminal_step_units != planned_step_units`.

That's a real finding! Let's verify carefully:

- `plan_run` (initial): for the regionless plan, units = [detect(BLOCKED? no—RUN?), ocr, ...] computed with region None. For REOCR_ALL with detector wired: steps = (detect, ocr); detect decision: `_decide_step(step_type="detect")` → not in forced; `stages.get("detect")` NOT_STARTED → not valid; previous empty; `_required_input_available("detect")` → requirements has no "detect" → True; provider available? `_provider_available(run,"detect")` → binding for detect maybe None → True → RUN. ocr: forced → RUN. So both RUN. terminal_step_units after plan = len(terminal_ids) = 0 (no terminal decisions). Hmm! At plan time terminal_step_units=0 and planned=2. Then execution marks detect terminal and ocr terminal → 2.

Wait, but for a *page with existing regions* plan (e.g., chapter scope re-run), the units may include SKIP_VALID; plan_run sets terminal_step_units = count of SKIPs (is_terminal). Then execute marks RUN ones. So consistent.

Now for the backfill: cloned units with SKIP_* decisions are appended, `planned_step_units += len(extra_units)`, but the SKIP ones are not added to `terminal_unit_ids`/`terminal_step_units`. In the normal `plan_run` flow they would have been. So the accounting does NOT close exactly when a cloned chain contains SKIP decisions → contradicts the docstring's claim ("``run.planned_step_units`` grows by the appended units so progress and the terminal accounting still close exactly") and the handoff's "planned_step_units 增量与 terminal 闭合".

Is this scenario reachable in the tests? Tests:
- R2/R0/F1: REOCR_ALL with 2 fresh regions; cloned chain = (ocr,) forced RUN → terminal.
- F5: same.
- e2e translate: cloned chain for the SFX region: steps for TRANSLATE_ALL. Let me get `_COMMAND_STEPS` for TRANSLATE_ALL. If the cloned chain includes SKIP decisions (e.g., segment... `_required_input_available` for segment requires ocr valid or previous ocr RUN → ok; provider unavailable → BLOCKED (not terminal)). BLOCKED is not terminal either! Hmm, BLOCKED units: in plan_run, is_terminal false → not counted. At execution, `if unit.decision is BLOCKED: task.status = BLOCKED; break` — the run becomes BLOCKED. Blocks are handled by resume_blocked re-plan.

So the not-counted-terminal issue arises only for SKIP_VALID / SKIP_LOCK / SKIP_POLICY cloned units.

Reachable scenario: multi-region page, TRANSLATE_ALL, one region is SFX with policy=manual or skip → its clone chain: translate → SKIP_POLICY; segment/mask_refine/inpaint/render → propagate SKIP_POLICY (per `_decide_step` propagation rule); color/term_extract → RUN (not gated); ocr → RUN. So planned grows by e.g. 9 but terminal only gets the RUN ones. Even after the run COMPLETED, progress < 1. This is *exactly the e2e manual scenario*! Indeed in the manual e2e, the SFX region's cloned chain has SKIP_POLICY units which are never counted as terminal. Does any test assert terminal == planned there? F5 does for a LOCK_CHANGED case with REOCR_ALL (cloned chain = ocr only RUN → cancelled → counted). The e2e manual test doesn't assert progress. R1/R2 assert equality for REOCR_ALL only (all RUN). So the zero-closure claim fails in the SFX-manual case, untested.

Hmm, but is it a *real* problem? `overall_progress` is user-visible (workbench progress). With a skipped SFX region in a multi-region page run, progress would show e.g. 8/13 ≈ 62% even at COMPLETED. Before the fix, planned = 2 (detect+ocr for REOCR_ALL) or for TRANSLATE_ALL the page chain only. So yes, it's a new user-visible regression in the multi-region SFX case (fan-out adds units whose SKIP terminals aren't counted).

Wait — but also check: does anything else call something that marks terminal for skipped units at the end of execute? `_cancel_pending_tasks` only for cancel; `_cancel_remaining` marks only RUN-decision units. `_aggregate_run` doesn't. So nothing.

Hmm, but hold on: is the *pre-existing* page-with-regions path also affected? In `plan_run`, terminal_ids includes SKIP units → counted. So it's specifically the backfill path that misses them. Confirmed asymmetry: `plan_run` accounts SKIPs, backfill doesn't. This is a genuine P2 finding (progress accounting + contradicts the docstring/handoff claim), and it's untested. Severity: P2 (user-visible progress inaccuracy; no data corruption, no crash). Possibly P1? Let's be measured: P2.

Let me double check by reading `_COMMAND_STEPS` for TRANSLATE_ALL to make sure SKIP_POLICY appears in a cloned chain. Let me read the top of service.py (constants) and check `_COMMAND_STEPS`.

Also I want to check: in the fan-out, `run.terminal_unit_ids` for cloned SKIPs — the docstring says the accounting closes exactly; contradicted.

Let me read service.py lines 60-140.
dsh: reasoning:
Confirmed: TRANSLATE_ALL = 8 steps (ocr,color,term_extract,translate,segment,mask_refine,inpaint,render). Cloned chain for a manual/skip SFX region: ocr RUN, color RUN, term_extract RUN, translate SKIP_POLICY, segment SKIP_POLICY (propagation), mask_refine SKIP_POLICY, inpaint SKIP_POLICY, render SKIP_POLICY → 5 terminal-by-decision units not counted in terminal_step_units.

So in the e2e manual scenario, the first run's `planned_step_units` = primary chain (detect + 8) + clone (8) = 17, and terminal = detect + primary RUN steps + clone RUN steps. Many primary RUN steps would fail/block (providers not configured → BLOCKED). Hmm, in the e2e, only ocr and translate bindings are configured; color/segment/etc. → `_provider_available` returns True if no binding... `binding = run.provider_binding_snapshot.get(step_type)`; if None → True. So color has no binding → available → RUN → the handler would run and fail (no provider registered?) → task_failed? In the e2e translate test, the run must have completed with the machine translation landing. Hmm, if color step fails (PROVIDER_NOT_CONFIGURED as a StepExecutionError), `_fail_step` → task_failed → `_cancel_remaining` → break. Then the SFX region's cloned units would be cancelled → SFX region never translated → test would fail!

But the test apparently passes (green). So maybe provider_binding_snapshot has entries for all steps with available=False? In assembly, bindings come from `pipeline_defaults` settings; the test saved only ocr and translate. Hmm, maybe the assembly writes all bindings with mock providers (assemble_acceptance_core wires Mock/Local providers for everything). The docstring says "Mock/Local providers". So color/segment/etc. have mock providers configured → RUN → succeed. Then the run completes and everything runs. Plausible.

So in the e2e translate scenario, the SFX region's cloned chain: all 8 steps RUN (translate admitted by policy). planned = 9 (primary: detect+8) + 8 = 17; all RUN → all marked terminal? Primary chain: detect, ocr, color, term_extract, translate, segment, mask_refine, inpaint, render → 9 units; the primary region is "speech" (reading_order 1) → all RUN. So terminal = 17 = planned ✓ (assuming no SKIP_VALID).

In the manual scenario: primary chain (speech, region None at plan) → all RUN (8+detect); cloned SFX chain: ocr RUN, color RUN, term_extract RUN, translate/segment/mask_refine/inpaint/render SKIP_POLICY → 5 SKIPs. planned = 17, terminal after run = 9 (primary) + 3 (clone RUN: ocr, color, term_extract) = 12. → progress = 12/17 = 0.706 even though COMPLETED. And `terminal_step_units` never equals planned. The e2e manual test doesn't assert progress → passes. So the bug is real but untested. 

Wait — but careful: are SKIP_POLICY units added to `run.terminal_unit_ids` elsewhere? `plan_run` initial: `terminal_ids.update(unit.unit_id for unit in units if unit.decision.is_terminal)`. At initial plan for the regionless page, primary chain decisions: could any be SKIP_VALID/SKIP_LOCK/SKIP_POLICY? For a fresh page: no. So terminal=0 initially.

Then backfill appends clone units without updating terminal_unit_ids → hence the gap. Confirmed finding.

Severity: This affects `get_task_progress().overall_progress` (workbench progress bar) and `terminal_step_units` shown to UI. For any multi-region page with an SFX region whose policy suppresses steps (the *default* policy is skip! and every region has a `sfx_policy` column default 'skip'), the progress will under-report. Actually note: for a *speech* region, `_sfx_gate_suppresses` returns False (region_type != sfx), so speech clones get no SKIPs. Only SFX regions (region_type == "sfx") with policy skip/manual produce SKIP_POLICY. Also SKIP_VALID could occur for a cloned region whose stage is already completed — but for freshly detect-created regions, stages are fresh. Hmm, but detecting *reuses* existing regions (reuse path) — if the page already had regions with completed OCR stages... the plan would then not be regionless (page.regions non-empty) → no backfill. So the realistic trigger is SFX regions with skip/manual policy — which is the *default* for SFX regions. That's a common production case (BJ02 5 regions etc. with onomatopoeia). So P2, arguably P1 for user-visible progress. I'll call it P2 (no data loss; progress/accounting only) but flag it as the top finding since it directly contradicts a stated invariant + is untested.

Hmm, actually wait. Let me reconsider whether the SKIP-decision cloned units even matter for progress. `overall_progress` = terminal/planned. If the run is COMPLETED, UI might show completed status with a progress bar at 70%. Also `planned_step_units`/`terminal_step_units` may be shown in workbench per-page step counts. Yes, user-visible.

Also, this same class affects `_cancel_pending_tasks` (cancel path) — pre-existing.

Now the second finding candidate: the `current()` raise path (TARGET_DELETED/TARGET_NOT_FOUND) escaping commit_step_result → run stuck RUNNING (detect committed but not marked terminal; not persisted!). Actually note: if `_backfill_detected_regions` raises after `self._catalog.commit_step` returned "applied" (DB already committed to sqlite), the in-memory run object has `step_run.status = COMPLETED` but `_persist` hasn't been called → the store still has the pre-commit state (RUNNING step). Then execute_run propagates the exception to the caller. The run stays RUNNING in the store; `recover_running_runs` would mark it INTERRUPTED. The DB has the detect commit applied. So a crash-consistency gap. Reachability: requires a region in detect output to be missing/deleted at backfill time. Since the whole thing is synchronous and single-threaded, only a concurrent process could do it. Low → P3/P4. But there is the width/height precondition (`_region_or_error` requires p.width/height IS NOT NULL) which `_page_or_error` does not — so if a page can be planned with NULL width/height, then after detect creates regions, the backfill would raise TARGET_NOT_FOUND. Does the production import always set width/height? The e2e/other tests insert width/height. Let me check whether import always measures dimensions — grep the importer for width. If the import path guarantees width/height, this is theoretical. Let me check quickly.

Third finding candidate: the primary chain keeps plan-time page-level decisions → SFX gate not applied to the first detected region. Pre-existing but now inconsistent within the same run; also the handoff claims "改用 _plan_region 后 gate/lock/stage 决策与恢复路径逐字节一致" for the fix surface, which is true only for the appended chains. Also AC1's premise "初始与恢复语义不一致即缺陷本质" implies the initial path should match recovery; after the fix, the primary region still doesn't. So the claimed semantic alignment is partial. Recommendation: register a follow-up Task (re-decide the primary chain from the live region snapshot would change single-region behavior → needs ruling) or at least the risk register should state it. Severity P2 (residual D06 §85 hole for primary SFX region; pre-existing, not a regression).

Hmm, is it truly "not a regression"? Consider a page where the user set the SFX region policy to skip, and detect creates regions where the SFX region is first in reading order. Pre-fix: TRANSLATE_ALL translated the first region (the SFX one) — violation. Post-fix: primary still translated; secondary SFX regions now correctly skip. So the user-visible effect changes only for non-first regions (improvement). Not a regression. But it is an incomplete fix that the Owner's handoff overstates ("policy=manual/skip 的 SFX region 由 SKIP_POLICY 保持不翻译" — needs a "非 primary" qualifier). Register P2 (documentation/precision) as a finding, or P3? Given D06 §85 is a documented must, and the AC1 premise is "initial==recovery", I'd say P2 — the fix leaves the primary region on the old page-level decision procedure, which for the SFX-gate is a policy violation; must at least be registered as a follow-up with a test. I'll present it as P2 with the note that resolving it changes single-region behavior → needs a user/integrator ruling, which the Task's "zero change" discipline forbids.

Fourth: e2e red evidence missing (P3). Red log covers only tests/pipeline/test_regionless_rebinding.py.

Fifth: "语义等价" nuance about the region snapshot vs page-level lock: for the clone chain `_effective_lock(region_view, region_snapshot)`; the region view's lock.page_locked comes from the page row ✓. Equivalent. Also `_plan_region` is called with target=region view — `_required_input_available` uses region stages; same as plan-for-region path ✓. And `_provider_available(run, step)` same.

One more nuance: In the *recovery* path, `_plan_target` for the PAGE target iterates all live regions including the primary, so the primary chain is re-decided with region-level decisions. Thus recovery would SKIP_POLICY the primary SFX region, but the initial run translates it → initial vs recovery still inconsistent for the primary. This strengthens finding #3: it's exactly the class of defect AC1 identified, left in place for region_ids[0].

Now — hmm, wait. Let me double check the primary chain for TRANSLATE_ALL when the page is regionless: does the *plan* include translate for the primary with RUN? The provider binding for translate exists (configured) → RUN. `_sfx_gate_suppresses` not called (region None). So yes.

Let me also double check `_plan_region`'s use for the clone with respect to `steps` including "detect"? region not None → no detect. ✓ Good.

Sixth: unit_id uniqueness / duplicate ids across tasks? `{task_id}:{region_id}:{step_type}` where task_id = "{run_id}:task:{target_order}" — unique per task ✓. And the primary chain keeps `{task_id}:{page_id}:{step_type}` — distinct from clone ids ✓ (page_id != region_id).

Seventh: `region_ids[1:]` — the fan-out set is the detect output; but the detect handler's reuse path returns ids ordered by reading_order; the primary is region_ids[0]. If detect returns ids in an order where region_ids[0] isn't the region with the lowest reading_order... doesn't matter.

Eighth: F5's claim of "atomicity" — the cloned units are cancelled via `_cancel_remaining`, marking them terminal. Cancelled units have no step runs → the UI shows them as cancelled? There's no per-unit status; the terminal count covers them. Consistent with the single-region page semantics (where remaining primary units are cancelled the same way) ✓.

Ninth: what about `max_step_runs` (1000) resource limit? Fan-out multiplies units per page: a 17-region page × 8 steps = 136 units — the limit is on step_runs, so a huge chapter could now exhaust max_step_runs where previously it wouldn't. Behavior on limit: run FAILED with RESOURCE_LIMIT_EXCEEDED and remaining cancelled. Pre-existing limit; the fan-out increases step-run consumption by the region count — that's the intended semantic. Worth a P4 note? It's a real scaling consideration (BJ06 17 regions → 17× steps). Could mention as a risk registration item in the integrator checklist. I'll fold into a P3/P4 note about resource limits / progress with large multi-region pages. Actually the handoff's risk list doesn't mention it. I'll add as P4.

Tenth: F4 test monkeypatches `service._executor._handlers[STEP_OCR]` — white-box but acceptable in this suite (the file already uses `handler_override`). Also F5 same. Fine. But note F5's wrapper signature `_wrapped(step_run, unit, run)`: `ProductionStepExecutor` handlers are called as `handler(step_run, unit, run)`? In execute_run: `self._executor.execute(step_run, unit, run)` — the executor calls the handler with (step_run, unit, run). OK. Actually check `_executor._handlers` structure — F4 does `service._executor._handlers[STEP_OCR]` and assigns a plain function; ProductionStepExecutor probably wraps handlers... In `_build_service`, handlers = ProductionHandlers(...).as_mapping() → passed as `handlers=mapping` to build_production_pipeline → executor constructed with those. Let me check ProductionStepExecutor.execute to confirm handlers are called with 3 positional args and that the executor doesn't require a bound method/`HandlerDependencies`. F4/F5 pass per the Owner's green logs, so fine.

Eleventh: check the docs/handoff claim "292 行净增含测试" — diff stat: service.py +~40, tests +~190 → ~230; whatever. Not important. But maybe verify the claim "改动面=service.py+2 tests" against the diff — yes per review-input.diff. I can't run git, but the diff file is authoritative for the review input. Note: the diff in review-input.diff is the task-env copy; it lists Handoff (new), Task (modified), service.py, 2 test files, and 4 verification logs. Wait — does the diff include only these? The file ends at line 664 with the red log. I saw green-overflow, green-target-files, green-three-suites, red. Yes 4 verification logs. Hmm, the Task doc says "verification 四份红绿日志" ✓.

Also check: does the diff include a "F1-F5" count of 5 new tests? The diff adds F1..F5 ✓ (F1 fans_out, F2 single_region, F3 zero, F4 added-after, F5 primary_failure).

Test count math: baseline 574+2sk → 579+2sk = +5 ✓ consistent with 5 new tests. And rebinding file: 17 tests (11 pre-existing + ... hmm 6 failed + 11 passed = 17 in red; F1-F5 = 5 new + R0-R7?? Let me count the file's tests: R0,R1,R2,R3 + N1..N7? and F1..F5 = 17? Let's check: R0-R3 (4), N1..N7 (7) = 11, plus F1-F5 (5) = 16. Hmm, 17. Maybe there are more (R4/R5). Earlier the section comment said "Regression Suite: R0 - R5". So R0-R5 = 6 tests? Then 6+7(N1-N7) = 13 + 5 = 18. Let me count with grep to be accurate: count `^def test_` in the file. Let me do that.

Also the red state: 6 failed, 11 passed = 17 total. So the file has 17 tests. Let me verify: the diff renamed R2 (not added) and added F1..F5 → net +5 in this file if it had 12 before. 12 + 5 = 17 ✓ if the file had 12 pre-existing tests. R0,R1,R2,R3,R4,R5 + N1..N6 = 12? And N7 exists (test_n7...). Hmm. Let me count precisely with grep to check the claim "6 failed 11 passed" is plausible and that the failing set is exactly the semantics-affected ones. 6 failed = R0, R1, R2, F1, F4, F5. Which pre-existing tests would still pass under old code? R3 (asserts 1 ocr step) ✓ passes old, N1-N7 (recovery semantics, unchanged) ✓. So pre-existing passing = R3 + N1..N7 = 8, plus F2, F3 = 2 → 10. That's 10, not 11. So there must be one more pre-existing test (R4 or R5) that passes in red. 4 (R0-R3) + R4 + R5? If R0-R5 = 6 and N1-N7 = 7 → 13 pre-existing + 5 new = 18 ≠ 17. So maybe R0-R3 only (4) + N1..N8? Unclear. Let me just grep the test function names.

Let me also confirm the number of tests in the file and their names to validate the red log composition claim.

Also — item: "R3 断言按 fan-out 执行顺序修正后为 6" — the red log shows R3 passing, consistent.

Let me grep for def test_ in the file.
dsh: reasoning:
17 tests ✓ (R0,R1,R2,R3,R5,N1-N7 = 11 pre-existing + F1-F5 = 5... wait 11+5=16, but there are 17 listed. Count: R0,R1,R2,R3,R5 =5; N1..N7 =7 → 12; F1..F5=5 → 17 ✓). Red: 6 failed = R0,R1,R2,F1,F4,F5; passed = R3,R5,N1-N7,F2,F3 = 1+1+7+2 = 11 ✓. 

Note: no R4 test (gap in numbering, pre-existing).

Now verify the "579 = 574 + 5" claim: baseline 574 + 5 new = 579 ✓ arithmetic consistent (all other test counts unchanged — the diff only adds tests; R2 renamed not added). ✓

Now let me check a couple of remaining verification points:

(1) The `test_r5_subsequent_run_on_same_page_avoids_duplicate_regions` test — it passes in red and green. In green, the second run on the same page (now with regions) → region-aware plan → units for each region; and no backfill (no detect? Actually detect isn't in the REOCR steps if region is not None → no detect → no backfill). Good.

(2) Does the fan-out risk double-planning when a page's detect step runs in a run where SOME regions already exist? If the page has regions at plan time, `_plan_target` uses them → no detect step at all for REOCR_ALL (steps=(ocr,) since region not None → no detect prepended). Wait: detect is prepended only when `region is None and "ocr" in steps`. If the page has regions, each region gets its own chain starting at ocr, no detect → no backfill. ✓ So the backfill only fires for the regionless case. But hold on: for TRANSLATE_ALL on a page with regions, steps for each region = full 8; no detect. ✓ 

But what about a page with regions where detection is prepended for the *page-level*? Not applicable.

(3) One more: when the backfill rebinds the primary and appends clones, is there a possibility that `region_ids` includes a region id equal to the page id? No.

(4) `run.planned_step_units += len(extra_units)` — persisted via `_persist(run)` at line 659 ✓, and `SqlitePipelineStore.put` re-inserts full run ✓ (claimed). Let me spot-check `put` around line 393-455 to confirm planned_step_units is persisted (the claim). Quick read to validate the "no store change needed" claim.

(5) The handoff claims "`_backfill_detected_regions` 改为实例方法（需 `self._catalog`）" ✓ consistent with diff.

(6) Check the "detect 步骤 commit 成功时同步调用 (service.py:650)" ✓ verified.

(7) `doc/tasks` diff: it removed "## 允许修改面" heading and merged — fine.

(8) Check whether the Task file's `depends_on: [M2-SFX-TRANSLATE-ENTRY]` and base_commit f99a6c55 updated ✓. Also the review request says base=8996ca55 batch family, fork=f99a6c55.

(9) 禁改面 zero diff: I can't run git, but the review-input.diff is the full diff artifact (presumably generated by the integrator). The diff shows only handoff/task/service/tests/verification. I should note that verification is by the diff artifact; the diff lacks file-level checks for untracked/other changes → NOT_VERIFIED for `git status`/full-tree diff (integrator should confirm `git diff f99a6c55..fa866327 --stat` matches).

Wait — the review request says tip=fa866327 (docs) and implement=f541b2f4. The diff presumably covers f99a6c55..fa866327. The red log filename is `red-f99a6c55-src-plus-tests.log`. OK.

(10) Check `SqlitePipelineStore.put` to validate the persistence claim about planned_step_units and pipeline_tasks.units_json. Let me read pipeline.py 380-470.

Also check `_run`/`_task` serialization includes planned_step_units and units (with decisions). Let me verify quickly — the test asserts `executed.planned_step_units` after execute_run returns the in-memory run; but the persistence of appended units matters for restart/UI. Let me read.
dsh: reasoning:
Persistence ✓ — full re-insert including task.units and planned_step_units/terminal_step_units.

Now let me double-check the finding about terminal accounting by finding whether SKIP-decision units are ever marked terminal in the backfill path... Confirmed no.

But wait — maybe for TRANSLATE_ALL on a *regionless* page, the cloned units' SKIPs... hold on, is there also an issue that `run.terminal_unit_ids`/`terminal_step_units` was computed in plan_run for the initial plan, and cloned units' SKIP decisions aren't added? Yes. So the fix should have added:

```
run.terminal_unit_ids.update(u.unit_id for u in extra_units if u.decision.is_terminal)
run.terminal_step_units = len(run.terminal_unit_ids)
```
That's the precise remedy. Good — concrete recommendation.

Let me double check whether `terminal_step_units` is used elsewhere for run gating (e.g., `_aggregate_run` uses task statuses, not terminal counts). Only progress. And `terminal_step_units` is exposed in TaskProgressSnapshot. The e2e manual test's comment in the handoff risk #4 mentions "terminal_unit_ids 以 unit_id 为键的正确性不受影响，R1 断言固化" — they considered accounting closure, but missed the SKIP branch.

Hmm, wait. Let me re-examine: could a cloned unit ever be SKIP_VALID in practice? `_decide_step` line 434: `if step_type not in forced and stages.get(step_type, NOT_STARTED).is_valid: return SKIP_VALID`. For a freshly created region, stage_states for "ocr" etc. would be... The detect commit writes `result.next_stage_states` — the detect handler presumably sets stage "detect" COMPLETED. So no SKIP_VALID for ocr. But for TRANSLATE_ALL, the cloned chain's later steps: stages empty → RUN (or BLOCKED if provider unavailable). And SKIP_POLICY for SFX gated steps. So yes the SKIP_POLICY branch is the live one (documented default policy=skip for SFX!). Very reachable: any multi-region page containing an SFX region with default skip policy running TRANSLATE_ALL → progress < 1.

Hmm, but here's a question: does the SFX region get detect-created with sfx_policy from settings (default skip)? Yes, `core_assembly.py:1041` applies sfx_policy from settings; default SfxPolicy.SKIP (entity default / schema default 'skip'). So the default multi-region scenario: SFX regions skipped at plan layer → progress accounting gap. This is the *default* production case for manga with SFX labels. Strong P2. I'm fairly confident. Let me sanity check that the primary chain (for the speech region 1) doesn't also produce SKIPs. Right.

Actually hold on, I should double check the SHAPE: the fan-out clone for the SFX region — the `_decide_step` propagation rule at line 440: `if prior_decision in {SKIP_POLICY, SKIP_LOCK} and step_type in {segment, mask_refine, inpaint, render}: return prior_decision`. So translate SKIP_POLICY, then segment: prior translate SKIP_POLICY → segment SKIP_POLICY; mask_refine: prior segment SKIP_POLICY → SKIP_POLICY; etc. And color/term_extract: they come BEFORE translate in _FULL_TRANSLATION order ("ocr","color","term_extract","translate",...) — the `previous` dict at the time color is decided = {ocr: RUN}; color is not in the propagation set and prior ocr isn't SKIP → RUN. So 5 SKIPs (translate, segment, mask_refine, inpaint, render). Actually also render: propagation from translate/segment/mask_refine/inpaint SKIP_POLICY → SKIP_POLICY. So 5 SKIP units uncounted per SFX region. Confirmed.

So terminal 12/17 = 0.706 for a 2-region page in the manual policy case; for TRAANSLATE_ALL default-skip SFX with 2 regions: primary chain=9 units all RUN (9 terminal), clone=8 (3 RUN + 5 SKIP) → planned 17, terminal 12.

Hmm wait, one more check: primary chain for TRANSLATE_ALL — 8 steps + detect = 9 units, all RUN? Term_extract requires ocr (previous RUN ✓), color ✓, translate ✓ (region None → no gate, provider bound), segment requires ocr ✓, mask_refine requires segment or previous segment RUN ✓, inpaint ✓, render: `_clean_available(page_id, stages=page stage states, previous)` → previous.get("inpaint") is RUN ✓. So all RUN. ✓ 9 terminal.

So the finding stands: `run.terminal_step_units` under-counts by the number of SKIP-policy cloned units; `overall_progress` never reaches 1.0 for such runs. Also `get_task_progress().skipped_reasons` includes reasons from skipped units (that's fine).

Now, let me look for one more possible issue: F2 test asserts `planned_step_units == terminal_step_units == 2` for a single-region page (no clones) — consistent.

Next: the review item 3 asks to check the red log composition (done ✓ self-consistent: 6 failed/11 passed, and the 6 names match the semantics-affected tests).

One more check for item 3: "R0 in red" — R0 asserts 2 ocr steps; old code gives 1 → fail ✓. R1 asserts 3 units; old = 2 → fail ✓. R2 ✓. F1 ✓. F4: old code → only 2 regions OCRed? F4 creates a 3rd region during OCR and asserts ocr_targets == first two regions' ids. Old code: ocr_targets = {primary} ≠ {r1,r2} → fail ✓. F5 asserts len(ocr_steps)==1 and terminal==planned==3; old: planned=2 → assert fails ✓. Good, the red log is self-consistent with the claimed cause.

Now check NOT_VERIFIED items:
- No shell → cannot verify git state (branch/tip/fork, 禁改面 zero diff, git diff --check), cannot rerun tests, cannot verify the venv/579 numbers, cannot verify the e2e red state.
- Cannot verify that the diff artifact is complete (e.g., untracked files, other modified files not in the diff).

Also check: does the diff include the review-input's scope = f99a6c55..fa866327? I can't verify.

Let me also check whether any *other* test in the repo asserts the old primary-only semantics for backfill that the Owner didn't update (would show as a failure in the 3 suites — they pass 579, so no). But also check other suites not run (tests/workbench, m2_acceptance, editing = 188 passed; the full 11 suites not run). Are there other suites that touch backfill semantics? e.g., tests/ui, tests/acceptance? The handoff says 11 suites total; only 6 run. Let me check which test dirs exist and whether any unrun suite references `_backfill` or multi-region backfill behavior. Let me grep tests for "backfill" to see all affected tests.

That's a good verification: grep across tests for backfill/region_ids to find tests not in the run set.
dsh: reasoning:
tests/providers/test_detect_handler.py executes a pipeline run with detect and checks region_ids; it's in the 3 suites (tests/providers) and passes. Let me check whether any of its tests assert primary-only follow-up after detect (e.g., only one ocr step). Let me check lines 240-400 of that file for assertions that might now be affected but pass anyway. It's part of the 579, so fine.

Let me also check the m2_acceptance tests (run in overflow 188) — they pass.

Now let me look at whether there might be *other* suites (not run) that exercise multi-region backfill. Glob for tests dirs failed (pattern "tests/*" matches files only). Let me list directories under tests via glob "tests/**/*.py"? That's a lot. Let me just glob tests/*/ ... not supported. Use glob pattern "tests/*/*" maybe returns files. Better: grep for "Suite" roots. Let's check with a directory listing via pwsh — unavailable. Use glob "tests/**/test_*.py" and just look at directory names.

Actually simpler: I want to know the 11 suites. Not critical. But one thing matters: whether an unrun suite contains assertions on backfill multi-region semantics that may now break. The grep above shows all references to backfill/region_ids in tests — only regionless_rebinding, sfx e2e, detect_handler, knowledge (unrelated), editing (unrelated), core/test_sfx_policy_settings? (not matched for "backfill"? it appeared? No). So the affected tests are covered. Good: grep shows no other suite asserts backfill semantics → the unrun-suite risk is low.

Hmm, one more: `tests/m2_acceptance` may run full pipeline flows with multi-region pages; the overflow run (188 passed) covers it.

Now let me double check the claim about `_catalog.current` being called for each extra region — could `current()` return a PAGE view if the region id happens to equal a page id? No.

Now the width/height precondition: let me check whether the importer always sets width/height (grep in importing/images). If yes, the TARGET_NOT_FOUND risk is only for concurrent deletion → P4.

Let me grep for "width=" or measure in the importer.
dsh: reasoning:
`library.py:293` shows `list_pages`-ish queries require width IS NOT NULL. And `core_service.py:269` too. `_page_or_error` in pipeline.py doesn't require width/height but the import path always sets width/height (application/importing/images/service.py:107). So width/height is guaranteed for imported pages → the risk window is only concurrent deletion. Good, I'll keep it as P3/P4 (robustness: unhandled PipelineError inside commit_step_result if a detect-reported region vanishes before the backfill read; the run stays non-terminal in the store). Actually I should verify the claim "run stays RUNNING" — since `_persist` wasn't reached, the store has the state from the last `_persist` (after `_record_step_attempt` → step RUNNING, run RUNNING). The DB (catalog) already committed the region creation. So yes: run RUNNING in store + regions created; `recover_running_runs` at next startup → INTERRUPTED → user can continue → re-plan → N7-like recovery. So it partly self-heals. Good nuance; P4/P3.

Now let me reconsider the finding #3 (primary SFX gate) — I want to double check the e2e/manual test does not cover the primary-region case, i.e., a scenario where the SFX region is the first detected region. The detector emits manga-1 (reading_order 1) then sfx-1 (reading_order 2) → sfx secondary. So untested ✓.

Is there any production guard that forces the SFX region not to be primary? No.

So the fix's own stated principle ("initial semantics == recovery semantics") is only satisfied for regions[1:]. For region_ids[0], the initial path still uses pre-detect page-level decisions where the SFX gate cannot see the region. Recovery (plan continue) would re-plan region-aware and gate it. So a page whose first detected region is SFX-manual will be machine-translated on the initial run and skipped after an interruption+continue — the exact inconsistency AC1 calls "缺陷本质". This is a genuine P2 (residual, not regression) and directly relevant to "AC1 语义闭环" claims. Since the Task says single-region pages must not change, the fix for the primary would change single-region behavior — so the correct action is registration/ruling, not silent fix. I'll mark it P2 with a clear recommendation: register a follow-up Task (or extend this one under a new ruling) to re-decide the rebound primary chain from the live region snapshot — including its effect on single-region SFX pages (which is a D06 §85 fix, arguably desirable, but changes the "zero change" AC and the e2e expectations for single-region pages).

Hmm, wait. Actually, let me double check whether that's true for a *single-region SFX* page. Is there a test asserting a single-region SFX manual page is NOT translated on TRANSLATE_ALL? Let me grep tests for such a case — e.g. in tests/core/test_sfx_policy_settings.py. If such a test exists and passes, then my analysis is wrong (the primary chain must be gated somehow). Let me check that file.

Let me grep tests/core for sfx policy tests and read the relevant one.
dsh: reasoning:
Let me look at tests/pipeline/test_pipeline.py:599 `test_sfx_region_policies_suppress_the_automatic_chain` — this is the planner test with a region-level plan (page with regions). It plans with region snapshots → gate applies. Fine.

And `test_planner_agrees_with_the_translate_step_gate`. These are region-aware plans.

Now, is there any test asserting that a page-level regionless plan (backfill scenario) does NOT translate an SFX primary region? test_detect_handler.py:294 mentions "the SfxPolicy default (SKIP) it will be governed by" — let me check that test: it might be the one where an SFX region is the first detected region and the run continues... Let me read tests/providers/test_detect_handler.py around 250-400. This is important: if there's a test asserting no translate for the first region, then my analysis is wrong. But the run there probably only covers detect+ocr (REOCR), so translate isn't in the chain.

Let me read that file section, plus test_full_chain.py (may run TRANSLATE_ALL on a regionless page).
dsh: reasoning:
These tests run TRANSLATE_ALL on a regionless page (detect first). In test_detect_handler (line 240+), the run: detect → ocr fails PROVIDER_NOT_CONFIGURED (no ocr provider) → task_failed → cancel remaining. So it doesn't reach translate. And the second test (line 289) – detect completes and the run... only asserts detect completed. So no test covers TRANSLATE_ALL fully on a regionless page with an SFX primary region.

So my P2 finding #3 stands (untested residual).

Now let me also double check my P2 finding #1 (terminal accounting) against a concrete reachable path within the shipped tests — the e2e manual scenario itself: since the test passes, the accounting gap is invisible. Good; I'll cite the e2e manual scenario as the concrete repro (planned 17 vs terminal 12 for the first run) — but I should be careful with exact numbers because I don't know the primary chain's exact decisions in the acceptance assembly (mock bindings for all steps). I'll phrase it as: any cloned unit whose decision is SKIP_VALID/SKIP_LOCK/SKIP_POLICY is counted in `planned_step_units` but never added to `terminal_unit_ids`/`terminal_step_units`, whereas the initial `plan_run` counts such decisions as terminal (`PlanDecision.is_terminal`), so `terminal_step_units < planned_step_units` and `get_task_progress().overall_progress < 1.0` for completed runs. Concrete trigger: TRANSLATE_ALL on a multi-region page with an SFX region under default `skip` policy → the SFX clone chain gets SKIP_POLICY for translate/segment/mask_refine/inpaint/render (5 of 8) and none are counted. The fix is a 2-line addition.

Let me be precise about where the fix goes: after `task.units = task.units + tuple(extra_units)`:
```
terminal = {u.unit_id for u in extra_units if u.decision.is_terminal}
run.terminal_unit_ids |= terminal
run.terminal_step_units = len(run.terminal_unit_ids)
```

Now, are there any other findings? Let me check a few more things:

(a) The F4 test creates a region during the OCR handler; the fan-out had already been computed. But also: the new region created by `editing.create_region` mid-run — does it break the *primary* chain? No.

(b) `_backfill_detected_regions` is now an instance method but was `@staticmethod` — any external callers? grep showed only service.py:657. ✓ (it's private).

(c) Check `execute_run`'s index loop interaction with `_cancel_remaining`'s iteration over `task.units` — fine.

(d) What about `pause_requested` mid-run then `continue`? `control_run("continue")` for PAUSED just resets to PENDING and re-executes the SAME run/tasks — the cloned units persist (already planned) — fine; for INTERRUPTED → `plan_run(mode="continue")` → full re-plan (replaces task.units, recomputes planned) → fine. But careful: re-planning replaces `run.tasks = tasks` with fresh PipelineTask objects and `run.planned_step_units = sum(...)`, `run.terminal_step_units = len(terminal_ids)` where terminal_ids only counts plan-time terminal decisions — losing the previously-terminal RUN units? Wait, in mode="continue", `run.step_runs` is preserved and terminal_unit_ids is rebuilt from plan decisions only. So previously completed RUN units would be re-planned... but plan decisions would be SKIP_VALID for completed stages (stage COMPLETED → is_valid) → so they become terminal via the SKIP path. OK, pre-existing design.

(e) Now: does the fan-out risk **double OCR** for the primary region? No: the clones start from `region_ids[1:]`.

(f) Duplicate plan if the detect step is retried? `commit_step_result` for detect runs once per attempt; if a detect step fails and is retried via `record_step_attempt`, backfill only fires on successful commit. But could the *same* detect step commit twice (e.g., duplicate commit_step_result call)? `step_run.status` check prevents. ✓

(g) What about two tasks for the same page? Each task has its own task_id → distinct unit ids. But `_catalog.commit_step`/stage states are shared per region — fine.

(h) `region_ids[1:]` uses detect output order; the appended chains are ordered by that list. Recovery orders by reading_order. For the new-creation path, the detect handler creates regions in candidate order and outputs... let me check handlers.py:258-299 to confirm the new path outputs candidate order (the handoff claims so) and the reuse path sorts by reading_order. If the new path outputs candidate order but `reading_order` differs (candidates could have equal order?), a mismatch with recovery ordering only affects step-run order, not correctness. Not a finding. But hmm — one subtle thing: if the detect output order for the new path is candidate order and candidates have reading_order like 1,7 (as in test_detect_handler), then region_ids[0] is the first candidate. Fine.

(i) The `unit_id` double-form debt: registered ✓.

(j) Item 5 scope discipline: tests/ two files. The e2e test change is an assertion update forced by behavior; registered in Task + docstring. Acceptable; I'll note P3-ish observation: it edits another Task's delivered acceptance test without that Task's docs being updated (the Task's own "Chain shape" claim "a multi-region page needs ... per-region follow-up runs" is now stale in M2-SFX-TRANSLATE-ENTRY's handoff, if any). Let me check if the SFX-ENTRY handoff mentions this — probably. Low priority; mention in the checklist that the integrator should note the supersession in the SFX-ENTRY record. Actually the review request says "test_sfx_policy_end_to_end.py 属 SFX-ENTRY 交付物——本 Task 修改它的断言是否合理登记". I'll answer: reasonable and registered in the Task + module docstring + handoff risk #1; recommend that M2-SFX-TRANSLATE-ENTRY's handoff/Task add a supersession note (the old "registered scheduling slice" wording is now false). That's an integrator action.

(k) Check the claim "旧 docstring 自认 later scheduling slice" — the diff shows the old docstring indeed said that ✓. And "旧 R2 断言 secondary untouched" ✓. And "SFX e2e 旧断言译文空+注释自称 registered scheduling slice" ✓. Triple evidence verified.

(l) Verify "恢复路径经 _plan_target 对页面全部现存 region 逐 region fan-out（N7 测试）": `plan_run` mode continue uses `self._catalog.current(run_target.target_id)` (live page view) → `_plan_target` → iterates all regions ✓. N7 test exists (line 673) ✓. Confirmed statically. Note: for mode "initial", `view = run_target.snapshot` (frozen at create_run) — so if regions were created between create_run and plan_run, the frozen snapshot has none → detect step; and the *detect handler* reuses live regions (test_detect_reuses_existing_live_regions) → region_ids = live ids; backfill rebinds/plans clones from live catalog ✓ consistent.

Hmm, interesting: in that reuse scenario (regions created between create_run and plan_run), the initial plan was regionless (frozen snapshot) → detect runs → reuses existing regions → outputs their ids → backfill: primary rebind + clones for the rest using live snapshots. Good; and `_region_or_error` requires those regions to be non-deleted ✓.

(m) One more potential issue: in the reuse scenario the primary region's chain was planned with region=None page-level decisions; the reused region may have COMPLETED ocr stage, yet `forced` steps (REOCR → ocr forced) run anyway ✓ intended.

(n) `planned_step_units` increment vs `_planned_task_status`: task.status was set at plan time (PENDING since RUN exists). After backfill, if all cloned units are SKIP, the primary still has RUN → fine. If the primary chain had no RUN but a clone does? The primary chain always includes the forced/needed steps... Consider TRANSLATE_ALL on a regionless page where the primary (region_ids[0]) is SFX... no, primary isn't gated at plan time → translate RUN. Fine.

(o) Now let me double check whether task.status might need updating after fan-out (e.g., if extra units are added to a task that was planned SKIPPED) — `_planned_task_status` is not recomputed. When could the initial plan produce a task with status SKIPPED? If no unit is RUN. E.g., REOCR_ALL... no, ocr is forced → RUN. RERENDER_ALL on a regionless page: steps=("render",) with region None and no "ocr" in steps → detect not prepended; `_decide_step("render")` → forced {"render"} → `_clean_available(page_id...)`... The chain is page-level; detect never runs → no backfill. So the backfill only fires when detect is in the chain, which requires "ocr" in steps → ocr forced? For REOCR_ALL forced={"ocr"} ✓; for TRANSLATE_ALL forced=∅ but ocr is not forced — could ocr be SKIP_VALID at plan time for a regionless page? stages.get("ocr") on the page stage_states — the page has no region stages; page-level stage "ocr" is never written (ocr writes region stages). So NOT_STARTED → RUN. So the task has RUN units ✓.

So after backfill the task status stays valid ✓.

(p) One more: `run.planned_step_units += len(extra_units)` — but `run.terminal_step_units` is len(terminal_unit_ids)... no recompute needed except my finding.

(q) What about `_cancel_remaining` being called with `task.units` including cloned RUN units when the primary FAILS → they're marked terminal (cancelled) → terminal counts them ✓ (F5). But the *SKIP* cloned units still uncounted → F5 asserts equality only in a REOCR_ALL case (no SKIP clones) → gap untested ✓ consistent with my finding.

Now let me also verify the "F5 semantics equal single-region behavior" claim: `_cancel_remaining` marks all subsequent RUN units terminal → same as single-region. ✓

And item 2's question "页任务状态机是否被破坏": task.status FAILED, run COMPLETED_WITH_FAILURES ✓; retry_failed_targets works on page tasks ✓.

One more consideration for finding #1 severity: could the mismatch cause the run to be reported as not-COMPLETED? `_aggregate_run` uses task statuses, not terminal counts → no. So only progress display. P2 (or P3?). The docstring explicitly claims closure ("progress and the terminal accounting still close exactly") and the handoff says "planned_step_units 增量与 terminal 闭合（R1/F1/F5 断言）" — the claim is false in the SKIP case, and progress is user-visible (workbench progress bar). I'll rate P2 and note it's the single most important gap, with a 2-line fix and a test to add (assert progress closure with an SFX-skip cloned chain).

Hmm, let me double check that `overall_progress` is indeed surfaced in UI. Let me grep for overall_progress in src/ui.
dsh: reasoning:
Confirmed: `projection.py:221` computes overall_progress = terminal/planned and `percent` (line 123) → user-visible progress in workbench. So the accounting gap is user-visible. P2 confirmed.

Let me check projection.py around 100-130 & 200-230 to see whether percent is gated by run status (e.g., if run is COMPLETED, force 100). If `percent` returns 100 when completed, the impact is lower. Let me read.
dsh: reasoning:
Confirmed: no terminal-status override; progress_percent is raw terminal/planned → user-visible in the workbench. P2 confirmed with a concrete UI effect.

Let me also check the workbench UI to see if progress is displayed. `src/ui/viewmodels/workbench/viewmodel.py:261` puts overall_progress into the dict for QML. Enough.

Now, let me quickly double check one more possible defect: `run.terminal_unit_ids` type is a set; `_mark_terminal` adds. In the fix recommendation, note `run.terminal_unit_ids` is a `set[str]` (mutable in a frozen dataclass? PipelineRun probably not frozen). Fine.

Another check: `_backfill_detected_regions` signature changed to include `run` as the first param after self — the docstring and the plan said `(run, task, unit, result)` ✓; call site updated ✓.

Now, what about the `@staticmethod` removal — is `_backfill_detected_regions` referenced in any other module (e.g., tests calling it directly)? grep tests earlier showed only docstring mentions. ✓

Now let me assess item 6 (test environment/口径 registration adequacy). The handoff says baseline 574+2sk was measured in the T3.2.1-packaging-py312 venv with onnxruntime installed by the Owner, and notes the discrepancy vs STATUS's "530+1sk". Then "579 passed, 2 skipped" at f541b2f4 in that same venv. The integrator needs to re-run in the main venv: expected 530+1sk+5 = 535+1sk (if no other differences). Hmm — careful: is the baseline "530+1sk" for main? The Task says "基线不回退：main 530+1skipped 0 failed". But the Owner says the difference is due to f99a6c55 batch new tests (574 vs 530 = 44 new tests). That's a big difference; also the venv difference (packaging venv with onnxruntime installed → 3 previously-failing tests now pass → +3?). The Owner says "与 STATUS 530+1sk 差异=f99a6c55 批次新增测试" and separately "1 skipped vs 2 skipped" difference = transformers not installed (env). Registration adequacy: it's registered but the arithmetic is loose ("574 - 44 = 530"). The 2 skips include "transformers 未装的环境性 skip" — but that's in the same venv as baseline, so it's consistent within the venv. The integrator must confirm: main venv at f99a6c55 → 530+1sk; at f541b2f4 → 535+1sk (or whichever). I'll put this in the closure checklist. The registration is "sufficient but loose" — I'd call it adequate with a P3 note that the zero-regression claim rests on a venv that the Owner modified mid-session (installing onnxruntime), and the +44 delta from the batch is asserted but not itemized. Actually the Owner DID archive the green logs but the baseline 574 log is "会话记录（未入库）" — no archived baseline log! That's a documentation gap: the zero-regression claim depends on an unarchived baseline run in a venv they patched. P3. Hmm, but the three-suite green at delivery head is archived ✓ and the red log is archived. The baseline log is not archived. Note as a P3/P4 finding or as a NOT_VERIFIED item. I'll make it a P3 finding (evidence completeness) + integrator checklist item.

Also: is `579 = 574 + 5` a valid zero-regression check? Only if the 574 baseline is trustworthy. The integrator re-runs the main venv.

Now, one more check on the health of the diff: file `tests/pipeline/test_regionless_rebinding.py` — the diff added a blank line issue? The diff shows:
```
+    assert regions.get_region(secondary.region_id).text.ocr_text == OCR_TEXT
+
 
 def test_r1_...
```
Fine.

Another check: F3 test asserts `executed.tasks[0].error_code == "INVALID_INPUT"` and `COMPLETED_WITH_FAILURES` — fine.

F4 test: monkeypatches `service._executor._handlers[STEP_OCR]`. Is `_handlers` a real attribute of ProductionStepExecutor? F4 passes in green (per logs) so yes. But careful: `_build_service` returns the service; the executor attribute access `service._executor._handlers` — the diff's F4 uses `original_ocr = service._executor._handlers[STEP_OCR]`. Since the Owner's green log says 19 passed (17 + 2), it works. But can I verify `_handlers` exists? Let me grep ProductionStepExecutor. Minor; but if `_handlers` didn't exist, F4/F5 would error → the green log would show failures. The green log shows 17 passed. But the green logs are Owner-produced; I'm reviewing them as evidence, and I verified consistency of the red log numbers. I'll spot-check `_handlers` quickly for completeness since it's cheap.

Also verify `editing.create_region` signature used in F4 matches (page_id, RegionGeometry, reading_order=, origin=) — the workspace editing service is RegionEditingService(regions); create_region signature per test file's region_creator closure uses same → ✓.

Let me grep ProductionStepExecutor for _handlers and execute signature.
dsh: reasoning:
Hmm — `ProductionStepExecutor` has no `self._handlers[STEP_OCR]` for step types? Line 52 uses `self._handlers[provider_id]` inside something (probably a provider registry adapter). Let me read executor.py to see the structure: whether `_handlers` maps step types and how execute dispatches.

If `_handlers` is keyed by provider_id (for the provider registry), then F4/F5's `service._executor._handlers[STEP_OCR] = ...` would... still work if the same dict is keyed by step type? Let me read.
dsh: reasoning:
✓ `_handlers` is keyed by step type first. F4/F5 monkeypatching works; and the extra `except Exception → StepExecutionError("PROVIDER_FAILED")` wrapper means F5's tampering wrapper: it sets `step_run.input_refs["region"] = "tampered..."` then calls the original handler → the original returns a StepResult; then commit_step compares expected revisions → mismatch → LOCK_CHANGED ✓ (F5 asserts LOCK_CHANGED). ✓ consistent.

Now let me also double check F5's expectation that `planned_step_units == terminal_step_units == 3`: units = detect, ocr-primary, ocr-clone (REOCR_ALL, 2 regions) all RUN. Primary ocr fails LOCK_CHANGED → `_mark_terminal(detect)`, `_mark_terminal(ocr unit failed)` → 2; then `_cancel_remaining` marks the clone ocr (RUN, after current) → 3 ✓. planned = 2 + 1 = 3 ✓. Good.

And the run status: COMPLETED_WITH_FAILURES ✓.

Now — hmm, an important subtlety in the red log: F5 FAILED in red. In red, `planned_step_units` = 2, terminal = 2 → assert `== 3` fails ✓.

OK. Now let me consider whether the primary re-decision issue could actually be *worse* than "pre-existing": with fan-out, could a *newly* created region that is the primary be translated where previously... it was also translated (primary was the only one). So no change. ✓ P2 residual.

Now let me think about whether there's an issue with **the region snapshot used for the clone chain and `expected_revisions`**: `_plan_region` sets `unit.expected_revisions = current_revisions` (region "region" revision id at plan time = detect's first revision). But `_record_step_attempt` doesn't use unit.expected_revisions (it reads live). So no stale-lock risk. However, does anything else use `unit.expected_revisions`/`expected_lock`? Let me grep to be sure (if a UI shows them or a store serializes). If unused at execution, then the clone chain's expected values are cosmetic. Let me grep for expected_revisions/expected_lock usage.

This matters for review item B (semantic equivalence): if the plan-time lock/revisions are used somewhere (e.g., workbench display or a "dry-run" preview), the clone's values would be live-snapshot-based rather than frozen-at-plan — consistent with recovery, fine.

Let me grep.
dsh: reasoning:
`unit.expected_revisions/expected_lock` are only serialized (persisted json) and not used at commit. Fine.

Now, summary of findings:

**F/R1 (P2)**: cloned units with `decision.is_terminal` (SKIP_VALID/SKIP_LOCK/SKIP_POLICY) are counted in `planned_step_units` but never added to `terminal_unit_ids`/`terminal_step_units` → progress never reaches 100% for completed runs; contradicts the docstring claim and handoff "闭合". service.py:979-981. Concrete reachable case: TRANSLATE_ALL multi-region page with an SFX region under default `skip` policy (clone chain gets 5 SKIP_POLICY units). Not covered by any F1-F5 test (F5 uses REOCR_ALL where the clone chain is a single forced RUN unit). Remedy: 2 lines; add an assertion.

**R2 (P2)**: the primary (`region_ids[0]`) chain keeps pre-detect, page-level plan decisions — the SFX gate is never consulted for it (`_decide_step` line 418-423 requires `region is not None`). So when the first detected region is an SFX region with policy skip/manual, the initial run machine-translates it (D06 §85 violation), while the same region would be SKIP_POLICY in the recovery path (`plan_run(continue)` re-plans region-aware) — the exact "initial vs recovery inconsistency" AC1 identifies as the defect, left in place for the primary. Not a regression (pre-existing), but the handoff/Task risk wording ("policy=manual/skip 的 SFX region 由 SKIP_POLICY 保持不翻译") and the "两路径语义一致" claim are over-broad; needs a "非 primary" qualifier + follow-up registration/ruling (fixing it changes single-region behavior, which the Task's zero-change discipline forbids → needs integrator/user ruling). service.py:964-971 + 418-423.

**R3 (P3)**: unhandled `PipelineError` from `self._catalog.current(region_id)` inside `commit_step_result` (service.py:974) — if a detect-reported region disappears (or fails `_region_or_error`'s extra preconditions, e.g. `p.width/height IS NOT NULL`, unlike `_page_or_error`) between detect commit and the backfill read, the exception escapes `execute_run` (no handler around it) leaving the in-memory/persisted run non-terminal (`step_run` COMPLETED but detect's `_mark_terminal`/`_persist` skipped), while the DB already has the detect commit. Self-heals only via `recover_running_runs` on next start. Low likelihood (synchronous single-threaded window); remedy: catch PipelineError → `TARGET_DELETED`/skip that region (or `_fail_step`). Register in risk list; the handoff's "region 中途删除 TARGET_DELETED 传播=既有路径行为" only covers the *execution* path, not this new plan-time read.

**R4 (P3)**: red evidence for the `tests/core/test_sfx_policy_end_to_end.py` assertion flip is not archived — `red-f99a6c55-src-plus-tests.log` only covers `tests/pipeline/test_regionless_rebinding.py` (6 failed/11 passed). The e2e assertion change ("" → MOCK_SFX_TRANSLATION_TEXT) is a genuine behavior change that needs its own red log (or the integrator must reproduce it), especially because the e2e file is another Task's deliverable.

**R5 (P3)**: baseline "574+2sk @ f99a6c55" (the zero-regression reference) has no archived log ("会话记录（未入库）") and was measured in a venv the Owner patched mid-session (installed onnxruntime). Zero-regression therefore rests on an unarchived, non-main-venv baseline; the integrator must re-run main venv at f99a6c55 (expect 530+1sk) and at f541b2f4 (expect +5).

**R6 (P4)**: modifying `tests/core/test_sfx_policy_end_to_end.py` (SFX-ENTRY deliverable) is reasonable and registered in the Task/handoff/module docstring, but M2-SFX-TRANSLATE-ENTRY's own records still describe the old "per-region follow-up runs" chain shape → integrator should add a supersession note there.

**R7 (P4)**: fan-out multiplies step-run consumption by the region count (e.g. BJ06 17 regions × 8 steps for TRANSLATE_ALL) against `ResourceLimits.max_step_runs=1000` — the risk register doesn't mention the scaling effect; worth a line in the handoff (17 regions ≈ 136+ units/page; a multi-page chapter selection can approach the cap). Not a blocker.

Let me double check R7's numbers: max_step_runs=1000 per run; a chapter of 20 pages × 17 regions × 8 steps = 2720 > 1000 → the run would hit RESOURCE_LIMIT_EXCEEDED. But before the fix, only the first region ran → 20×8=160. So the fan-out genuinely increases the chance of hitting the limit — though it's the *correct* behavior now. It fails closed with a registered fatal_error. Register as an observation/risk (P4) for the integrator. Note also `_limits` construction is at assembly (probably default 1000). OK.

Also, should I flag the `region_ids[1:]` fan-out set semantics as "snapshot" vs "live" divergence (review item B)? The recovery path reads live regions at plan time; the backfill reads live region snapshots too, but the *set* is detect output (frozen). So on a mid-run region add, initial and recovery differ — by design (F4) and defensible (the run's task graph is fixed at plan/detect time). I'll note in the table under B as acceptable with rationale (F4) but note the inconsistency is deliberate and documented.

One more: does `_plan_region` for the clones respect `forced` steps identically? `_forced_steps(run.command_type)` — same for both paths ✓.

Also verify that the clone's `ocr` step for REOCR_ALL is forced → RUN even if the region's ocr stage is valid... All the more likely SKIP_VALID won't appear for forced steps. Right, so for REOCR_ALL the clone = 1 forced RUN unit (explains why R0/R1/R2/F1/F5 all close).

Now, "NOT_VERIFIED" list (integration-side runtime items):
1. Any test execution (no shell in this sandbox): 579+2sk, 19 passed, 188 passed, red 6/11 → taken from Owner logs; numbers self-consistent per file counts (17 tests in the rebinding file, 11 pre-existing + 5 new; 574+5=579).
2. git facts: branch=agent/zcode/..., base=f99a6c55, fork=f99a6c55, implement=f541b2f4, tip=fa866327, 禁改面 zero diff, `git diff --check`, `git status --porcelain` — cannot run git in this sandbox; reviewed only the provided review-input.diff (which I cannot prove is the complete f99a6c55..fa866327 diff).
3. The e2e translate/manual green outcomes and the claim that the manual scenario caught the decision-copy implementation (no archived log).
4. Main-venv baseline/regression numbers.
5. Whether the diff artifact matches the worktree HEAD (doc/handoff in-worktree matches the diff ✓ I read both: the worktree Task file shows the same content as the diff — yes, I read the worktree Task and it matches; and the handoff I read via the diff only. Let me confirm the handoff file in the worktree matches the diff — I read the diff version and the Task; the worktree Task file matched the diff exactly (lines 2-49 vs diff). Good, so the diff artifact is consistent with the worktree for at least those files.

Actually, one thing I can check statically: the worktree service.py contains the change ✓ (verified lines 923-981), the tests contain F1-F5 ✓, the Task file matches ✓. So the diff artifact matches the worktree for the 3-4 key files. Good — I can state that.

Let me verify the worktree handoff file exists and matches (read first ~20 lines) — cheap and strengthens the verification. Also check the verification log files in the worktree (red log content). Let me read them directly from the worktree to confirm the archived evidence exists on disk (not just in the diff).
dsh: reasoning:
Evidence files exist on disk ✓ (4 logs).

Now the handoff file in the worktree — the diff said new file doc/handoffs/...-f541b2f4.md. Let me verify it exists on disk (glob) — quick. Also I want to check whether the worktree contains any *uncommitted* changes (can't run git). Skip.

Let me do a final check of the handoff file on disk for consistency with the diff (e.g., risk list). Actually the diff content = the file. I'll trust it but do a quick glob to confirm it exists.

Then also confirm: does the repo have a REVIEW template / do I need to write the review to a file? The user asked to "直接输出全文" — output the full text in the response, not write a file. Good.

One more consideration for the review tables: item on "红态证据" — verified self-consistent (6 failed names match the claims; 17 tests total; 11 = R3 + R5 + N1..N7 = 1+1+7 = 9... wait let me recount: passed in red = 17-6 = 11. Tests passing in red: R3, R5, N1, N2, N3, N4, N5, N6, N7, F2, F3 = 11 ✓ (R3, R5 = 2; N1-N7 = 7; F2, F3 = 2 → 11 ✓). And failed = R0, R1, R2, F1, F4, F5 = 6 ✓. 

Let me also double check R5 passes in red: `test_r5_subsequent_run_on_same_page_avoids_duplicate_regions` — second run on the same page with regions → no backfill → unchanged ✓.

And N1-N6 tests: they exercise lock/tamper scenarios on the primary (single or multi region?). E.g., N2 "region_locked_between_detect_and_ocr" — the primary is locked → SKIP_LOCK. With fan-out, would the cloned units also run? In red they pass (old code). In green, do they still pass? The green log says 17/17 ✓. Hmm, interesting: N2 locks the primary region between detect and ocr; with fan-out, the clone for region 2 would run OCR. Does N2 assert something like only the primary is skipped? Let me check N2 and N5/N6 for assertions that might be affected by fan-out — they pass in green per the log, but I want to see whether the fan-out makes N2's assertions accidentally pass/fail. Since green says 17 passed, fine. But for review depth, let me quickly read N2 (line 531-575) to see whether the fan-out interaction is meaningfully covered. Optional. Let me read N2 and N6 quickly since "失败传染/原子性" is a review focus.

Actually N6 "primary_soft_deleted_before_ocr" is interesting: if the primary region is soft-deleted before ocr, then in the fan-out path... the fan-out happened at detect commit (before deletion?). The test presumably deletes the primary region, then ocr for the primary fails TARGET_DELETED → task fails → clone cancelled. Let's read N2/N6 to check the interplay with the new fan-out (this is where the "TARGET_DELETED 传播" note comes from). If N6 deletes the primary *before* detect commits... let me read.
dsh: reasoning:
Interesting! N2, N4, N6 assert `len(ocr_steps) == 1` — and these are in the red AND green passing sets. Why does the fan-out not produce a second OCR step run in N2/N6? Because the primary OCR fails (LOCK_CHANGED / PROVIDER_UNAVAILABLE) → task_failed → `_cancel_remaining` marks the clone unit terminal without running → only 1 ocr step run ✓. And N4: OCR provider missing → primary fails PROVIDER_NOT_CONFIGURED → clone cancelled → 1 step run ✓. Good — this confirms the "failure containment" semantics and that those old assertions remain valid *because of* the serial fail-fast. Good, this is a nice confirmation of F5's claim.

Note N2's wrapper locks `step_run.region_id` — for the primary ocr, step_run.region_id == primary ✓.

So the fan-out's interaction with N2/N4/N6 is exactly the failure-containment path → covered incidentally. 

Now I have enough for a thorough review. Let me also consider: is there a *duplicate-region* risk if `region_ids` contains the same region twice (detect reuse path returning duplicates)? Pre-existing.

One more thing to check for review item B (semantic equivalence when the region state has changed): the recovery path evaluates `_plan_target` on the live *page* view, where regions come from `_page_or_error` (which excludes deleted regions, and reads each region via `_region_from_id` with `deleted_at IS NULL`). The backfill path evaluates each region via `_region_or_error` (raises if deleted). Both read live data; the difference is raise-vs-omit → R3 finding.

Also: in the recovery path the `target` passed to `_plan_region` is the *page* view, so `_decide_step`'s `target.page_id` = page id (same), and `lock.page_locked` from the page row (same as region view's lock.page_locked which came from `p.page_locked`) ✓ equivalent. And `region.region_type/sfx_policy/manual_edited/final_confirmed/current_revisions/stage_states/metadata` — all from `_region_from_id` in both paths ✓ byte-identical. Good: the equivalence claim for decisions is verified statically for the appended chains. I'll state this explicitly as a positive verification (the strongest part of the change).

One nuance: in `_plan_region`, `current_revisions = dict(region.current_revisions)` = `{"region": current_revision_id}` ✓ same in both paths. And `_effective_lock`: page path `LockSnapshot(page_locked=target.lock.page_locked, region_locked=region.lock.region_locked, ...)`; region-view path `LockSnapshot(page_locked=region_view.lock.page_locked (= p.page_locked), region_locked=region.lock.region_locked, ...)` ✓ same. Confirm `_region_or_error`'s lock.translation_locked = region.lock.translation_locked ✓ and inpaint_locked ✓. Equivalent. 

Now let me write the review. Structure per the requested format:

## Verdict
结论：不阻塞（可集成），但有 1 个必修的口径/账目缺陷（P2，建议随本 Task 修掉，2 行）… Let me decide the verdict wording: "有条件通过（conditional pass）" — the implementation's core semantics are correct and statically verified; two P2 issues: (a) terminal accounting gap (progress), (b) primary-region SFX gate residual (needs registration/ruling, cannot be fixed inside this Task's discipline). Given the repo's Gate rules (independent review → integrator), I'd say: Verdict = 通过（Approved with conditions）: P2-1 must be fixed (small) or explicitly registered + follow-up task; P2-2 must be registered as a follow-up (not fixed here); everything else is documentation cleanup. Since I'm a static reviewer with NOT_VERIFIED runtime items, the integrator closes after runtime verification.

I need to be careful and honest: P2-1 (progress accounting) is a real behavior deviation from the docstring's stated invariant and is user-visible. I'd make the verdict "有条件通过 / Conditional approve": require the integrator to either land the 2-line fix + test before merging, or explicitly register it as a follow-up with a ruling; the rest of the delivery is verified.

Let me also double-check one thing in my P2-1 analysis: is `terminal_step_units` used in the UI at all (`percent`), or is the UI progress computed from page counts? `viewmodel.py:261` puts `overall_progress` in the payload; also `progress_percent`. Let me check whether the QML uses progress_percent or a page ratio. Let me grep the QML/TS frontend for progressPercent.

Let me check quickly: grep in apps/ or src/ui for progress_percent / overall_progress.
dsh: reasoning:
Confirmed: `TaskProgressPanel.qml` displays `progress.progress_percent` → the P2-1 finding is directly user-visible (progress percentage stuck below 100% on a COMPLETED run).

Now I'm confident. Let me write the review.

I should also mention where the fix should go and the exact test to add.

Let me draft the tables.

**逐项核对表**

A 勘察与语义
| 声称 | 静态核对结果 | 证据 |
- backfill 触发时机 = commit_step_result 内 detect commit 成功时同步调用 → ✅ service.py:650-657（`outcome.status == "applied"` 分支内，detect 判定 `unit.step_type == "detect"`）；detect 失败（candidates=0 → INVALID_INPUT）不经此路径（N3/F3 断言一致）
- 修复前绑定模型 = 只重绑 region_ids[0] → ✅ 由 diff 的 before 段与 `region_ids[1:]` 无任何 PlanUnit（旧 R2 断言 1 次 OCR / 旧 e2e "" 断言）共同证实
- 三重实证 → ✅ 三处均在工作树中可查（旧 R2 已被改名为 R2 new，但 diff before 段保留；e2e 旧注释/旧断言在 diff；旧 docstring "later scheduling slice" 在 diff）
- 恢复路径逐 region fan-out → ✅ service.py:288-302（mode continue/resume_blocked 用 `self._catalog.current` 而非冻结快照 + `_plan_target` 遍历 `region_snapshots()`）+ N7 存在（:673）
- 语义选项 A/B/C/D → ✅ 对比表在 handoff；B/C 因禁改面排除的推理成立（domain `PlanUnit` / bootstrap+contracts）
- 结论 A 与恢复语义一致 → ⚠️ 对 `region_ids[1:]` 成立；对 `region_ids[0]`（primary）**不成立**（见 R2）

B _plan_region 复用正确性
- 调用形态 `_plan_region(run, task, region_view, region_snapshot)` 与签名 (run, task, target, region) 匹配 → ✅ service.py:338-344
- `_catalog.current(region_id)` 返回 REGION 型 TargetSnapshot，`region_snapshots()` 精确返回该 region（`regions=(region,)`，含 region_type/sfx_policy）→ ✅ sqlite/pipeline.py:664-699 + domain/tasks/models.py:261-279
- 决策等价性（gate/lock/stage/provider/forced）→ ✅ 逐项比对：`_effective_lock(region_view, region)` 的 page_locked 取自 `p.page_locked`（pipeline.py:687-692）与 page 路径 `_effective_lock(page_view, region)` 等价；stage_states/current_revisions/region_type/sfx_policy 均来自 `_region_from_id`；`_clean_available(target.page_id)` = 真实 page id；`_provider_available(run, ...)` 同一个 run；`_forced_steps(run.command_type)` 同一命令。
- SFX gate 真被覆盖 → ✅ service.py:418-423 在 `_plan_region`→`_decide_step` 链上，`region is not None` 才求值；生产 `handle_translate`（providers/handlers.py:382-465）**确实不经** `decide_sfx_translation`（全仓仅 translation/context/step.py:176 与 rendering/service.py 用 gate，且都不在本路径）→ Owner 红态修正的核心声称成立
- region 已删除/状态已变时两路径一致性 → ⚠️ 恢复路径用 `_page_or_error` 过滤 deleted region（不抛）；backfill 用 `_region_or_error`（`deleted_at`→TARGET_DELETED 抛 PipelineError）→ 见 R3
- 快照语义（中途新增 region 不跟进）→ ✅ F4；与恢复路径"live snapshot"的差异是"集合在 detect 时冻结"，属于设计选择（有测试+文档）

C 失败传染与原子性
- primary 失败 → 剩余克隆 unit cancel（`_cancel_remaining` 按 `task.units` 顺序对 RUN unit 标 terminal）→ ✅ service.py:983-993 + 804；克隆链追加在 primary 链之后，故顺序语义与单 region 页一致
- F5 断言 `len(ocr_steps)==1`、`terminal==planned==3` → ✅ 与 REOCR_ALL 克隆链仅 1 个 forced RUN unit 相符
- 意外收获：N2/N4/N6 的 `len(ocr_steps)==1` 断言在 fan-out 下仍然成立，正是靠 fail-fast → 失败传染与既有断言自洽
- 页任务状态机 → ✅ task FAILED / run COMPLETED_WITH_FAILURES / `retry_failed_targets` 按页重试（service.py:905-921）
- 账目闭合 → ❌ SKIP 类决策的克隆 unit 未计入 terminal（R1）

D 测试质量与红绿
- 红日志构成 → ✅ 17 tests = R0,R1,R2,R3,R5 + N1..N7 + F1..F5；红 6 = R0,R1,R2,F1,F4,F5；11 passed = R3,R5,N1-N7,F2,F3 —— 与声称完全自洽（含"R3 由 7 failed 修正为 6"的说明）
- 绿 → ✅ 日志文件 4 份存在（target-files 19、three-suites 579+2sk、overflow 188、red 6/11）；574+5=579 算术闭合；rebinding 17=12+5
- 断言质量 → ✅ 断的是 DB/step_runs/unit.decision 等真实状态；R2 由"负断言"翻转为正向"每 region 都 OCR"，语义翻转有红证据
- e2e 断言翻转的红证据 → ❌ 缺失（red 日志只跑 rebinding 文件）→ R4
- 基线 574 日志 → ❌ 未入库（"会话记录"），且该 venv 被会话中途补装 onnxruntime → R5
- 单 region/0 region/中途新增/失败传染边界 → ✅ F2/F3/F4/F5 + N1-N3
- 未被覆盖：SKIP 类克隆 unit 的账目（R1）、primary 为 SFX 的 gate（R2）、region 计数 >2 的页（F1 只断言 2 region；R2 用 len(all_regions) 泛化到 N ✓）

E 范围纪律
- src 改动仅 service.py → ✅ diff 仅此一个 src 文件；`_backfill_detected_regions` 无外部调用方（grep 仅 service.py:657）
- 禁改面零 → 需 git 验证（本沙箱不能跑 git）→ NOT_VERIFIED；但 diff 中确实没有 domain/schema/ports/providers/bootstrap/contracts/packaging/apps/STATUS
- tests 两文件 → ✅ 合理；`test_sfx_policy_end_to_end.py` 属 SFX-ENTRY 交付物，改动=docstring + 1 条断言，已在 Task/handoff/docstring 三处登记（R6 建议在 SFX-ENTRY 侧加 superseded 说明）
- 持久化零 schema 变更 → ✅ `SqlitePipelineStore.put` 全量重插且含 planned/terminal/units（pipeline.py:393-455）
- 未跑全套件 → 已如实登记（三套件+3 溢出）；grep 全 tests 未见其它 suite 依赖 backfill 语义 → 残余风险低

Findings 列表（R1..R7）。

Now let me assign P-levels and write concise, actionable text with file:line.

R1 P2 — service.py:979-981 (backfill) vs plan_run service.py:305/311 & PlanDecision.is_terminal (domain/tasks/models.py:129-131).
R2 P2 — service.py:964-971 + 418-423; handoff 风险 #1 措辞。
R3 P3 — service.py:974 / 657 / sqlite/pipeline.py:668-677 & 625-639 (`_page_or_error` 无 width/height 前置，`_region_or_error` 有)。
R4 P3 — verification 缺 e2e 红日志。
R5 P3 — handoff 基线日志未入库 + venv 中途补装。
R6 P4 — SFX-ENTRY 交付物交叉修改的记录闭环。
R7 P4 — max_step_runs 规模化。

Also maybe R8 P4: docstring is long (40+ lines) — over-documentation? Not needed. Skip.

Hmm, should R2 be P1? The rule of thumb: P1 = must fix before merge (correctness/data risk); P2 = should fix/register; R2 is pre-existing and out of the frozen scope → P2 with "登记+裁决" (not a merge blocker). R1 is a new behavior deviation introduced by this change (progress wrong for the very scenario this Task enables) → closest to a merge condition. I'll label R1 P2 (not P1) because no data/functional loss, but state it as "建议随本 Task 修（阻断条件）" in the verdict. Actually to be crisp: Verdict = 有条件通过；条件 = R1 修复或显式登记+下一 Task（集成方裁决），其余 P3/P4 只需登记。

Let me now write the final answer in Chinese, full text, using the requested headings. Keep it thorough but not bloated. Include the 集成方闭合清单 (runtime items) and 推荐下一步 (one sentence).

Let me note explicitly the static verification I did on the worktree files (service.py lines, tests, logs) vs. what remains NOT_VERIFIED.

One more consideration for the closure list: integrator must (1) re-run main venv at f99a6c55 and f541b2f4; (2) verify 禁改面 via git diff --stat f99a6c55..fa866327 and git status; (3) reproduce the e2e red (checkout old service.py, run the 2 e2e tests) to archive the missing red evidence; (4) decide R1 (fix or follow-up); (5) register R2 follow-up + amend the handoff risk wording; (6) add supersession note to SFX-ENTRY record; (7) confirm review-input.diff covers the full tip..base range (no untracked/extra files).

For the primary-SFX-region finding (R2), let me give a concrete repro recipe so the integrator can confirm: make the detector emit an sfx candidate with reading_order 1 and a speech candidate order 2 in the e2e scenario with policy=manual → assert the first region's machine_translation... In current code it'd be translated (violation). Actually careful: in the e2e, TRANSLATE_ALL with policy=manual → the primary chain (region None at plan) has translate RUN → the SFX primary region gets machine translation → test assertion `machine_translation == ""` for the sfx region would fail. So a 1-line variation of the existing e2e detector (swap reading_order) reproduces R2. That's a strong, concrete repro. I'll include it.

Wait — is that true? Let me double check the primary chain for the sfx-primary case: `_decide_step(step_type="translate", region=None)`:
- lock page-level, not locked
- `step_type in _SFX_GATED_STEPS` but `region is not None` fails → no policy skip
- translate: `lock.translation_locked` (page-lock snapshot: `_effective_lock(page_view, None)` = target.lock = page LockSnapshot(page_locked=..., others default False)) → False
- `region is not None and (manual_edited or final_confirmed)` → region None → skip
- stages check: page stages "translate" not valid → continue
- previous: for the primary chain, translate's previous includes ocr RUN, color RUN, term_extract RUN → no BLOCKED/SKIP → continue
- `_required_input_available("translate", page_stages, previous)` → required "ocr": page stages ocr not valid, but previous ocr is RUN → True
- provider available (translate binding configured in e2e) → RUN
→ So yes, translate RUN → handle_translate runs → region_type="sfx" → mock returns MOCK_SFX_TRANSLATION_TEXT → lands. So a manual-policy run with an SFX primary region WOULD machine-translate it → D06 §85 violation, and the existing e2e assertion pattern would catch it if the detector emitted sfx first. Excellent concrete repro. I'll state it as: "F2 类零变化守则与 D06 §85 冲突：把 e2e 的 detector 两个 candidate 的 reading_order 对调（sfx 成为 region_ids[0]）即得反例".

Hmm, one caveat: with sfx first, `regions["speech"]` (second) would be the clone with speech → its chain is region-aware → translates normally. And the sfx primary gets translated → violation confirmed. Also note the primary's `unit_id` keeps page-id form. Fine.

I should double check `handle_translate` writes machine_translation for the region regardless of policy → yes (no gate), provider returns text.

Good. Now write the answer.

Length: this is a detailed review; aim for a well-structured but readable output. Use tables.

Also per the workspace instructions: end with a recommended next step (one sentence) — the requested format has "推荐下一步（一句）". And the AGENTS.md says the final reply must give a recommended next step; the requested format covers it. I should also add the "可直接转发给下一个 Agent 的指令" per §5.1? The user's requested output format doesn't include it, and the AGENTS.md says "如存在安全且已授权或可立即释放的下一 Task，必须指定合适 Agent 并提供可直接转发的指令；否则明确写无需下一步操作". The requested format's last section is 推荐下一步（一句）. I'll satisfy both minimally: the 推荐下一步 sentence names the agent and the action; since the immediate next step is integrator-side (Codex/编排会话), and no new Task is being released, I can state "无需新 Task" — but AGENTS.md wants a forwardable instruction if a next Task exists. The integrator action can be given as a forwardable instruction line. I'll keep it to one sentence as requested plus a short forwardable instruction embedded. Actually the user explicitly said "推荐下一步（一句）", so I'll write one sentence that names the agent + action + gate. Good.

Now write it.
# M2-TASKS-BACKFILL-MULTIREGION 静态 Review（round 1，DeepSeek Harness，非作者）

审查方式：无 shell 沙箱（`pwsh` 在本会话直接失败 `SetNamedSecurityInfoW failed`），全部结论来自对 worktree 源码/测试/日志的静态读取 + `review-input.diff` 逐行核对；所有运行时项集中在 NOT_VERIFIED。已核实 worktree 中 `src/application/tasks/service.py`、两个测试文件、Task 回填与 4 份 verification 日志均与 diff 一致（证据确在磁盘上，非仅 diff 文本）。

## Verdict

**有条件通过（Conditional Approve）**——核心语义修复方向正确且静态可证：`_plan_region` 复用对 `region_ids[1:]` 的决策链与恢复路径**逐项等价**（gate/lock/stage/provider/forced 全部同源），SFX gate 确在 plan 层且生产 `handle_translate` 确不经 gate（Owner 红态修正的核心声称成立），失败传染/原子性与旧单 region 语义一致，红态 6 failed/11 passed 构成自洽。

但有一个**本 Task 引入的新缺陷（P2）**：克隆链中被决策层判为终态（`SKIP_VALID/SKIP_LOCK/SKIP_POLICY`）的 unit 只进 `planned_step_units`、不进 `terminal_step_units`，导致 COMPLETED run 的 `progress_percent` 永远 < 100%（`TaskProgressPanel.qml:119/177` 直接显示该值），且与 docstring/handoff 的"账目精确闭合"声称矛盾；触发场景正是本 Task 打开的常见生产场景（多 region 页 + SFX region 默认 `skip`）。建议随本 Task 修（2 行）或由集成方显式登记为下一 Task。

另有一个**本 Task 未闭合的既有缺陷（P2）**：`region_ids[0]`（primary）仍沿用 detect 前的页级 plan 决策，SFX gate 对它不可见 → "初始 vs 恢复语义不一致"在 primary 上原样存在，handoff 风险 #1 的措辞过宽。该点**不应在本 Task 内修**（会改变单 region 页行为，违反"零变化"纪律），需登记 + 集成方/用户裁决。

## 逐项核对表

### A 勘察与语义

| 核对项 | 结论 | 证据（静态） |
|---|---|---|
| backfill 触发时机=detect commit 成功时同步调用 | ✅ | `service.py:647-657`（`outcome.status=="applied"` 分支内，`unit.step_type=="detect"`）；detect 失败（0 候选/缺 provider）不进入该分支，与 F3/N3 断言一致 |
| 修复前只重绑 `region_ids[0]`、`region_ids[1:]` 无 PlanUnit | ✅ | diff before 段（旧 R2「secondary untouched」、旧 e2e 断言 `machine_translation == ""`、旧 docstring `later scheduling slice`）三处齐备 |
| 恢复路径天然逐 region fan-out（N7 先例） | ✅ | `service.py:288-302`：`mode in {continue,resume_blocked}` 用 `self._catalog.current(run_target.target_id)` 取代冻结快照，`_plan_target` 遍历 `target.region_snapshots()` 每 region 调 `_plan_region`；N7 测试存在（`tests/pipeline/test_regionless_rebinding.py:673`） |
| 语义四选项对比与 A 的排除逻辑 | ✅ | handoff §语义选项对比；B（改 `domain.PlanUnit`）与 C（bootstrap/contracts 编排）确在禁改面内，排除理由成立 |
| "初始与恢复语义一致" 的结论 | ⚠️ 部分成立 | 对 `region_ids[1:]` 成立；对 `region_ids[0]` **不成立**（见 R2：primary 链仍是 detect 前的页级决策，`region is None` ⇒ `_decide_step` 不求值 gate） |

### B `_plan_region` 复用正确性

| 核对项 | 结论 | 证据（静态） |
|---|---|---|
| 调用形态与签名匹配 | ✅ | `service.py:338-344` `(self, run, task, target, region)`；调用 `self._plan_region(run, task, region_view, region_snapshot)`（:977） |
| `current(region_id)` 返回 REGION 型快照且携带 region 真实属性 | ✅ | `sqlite/pipeline.py:562-566, 664-699`（`regions=(region,)`，`region` 来自 `_region_from_id`：`region_type/sfx_policy/manual_edited/final_confirmed/current_revisions/stage_states/metadata`）；`domain/tasks/models.py:261-279` 对 REGION 型精确返回该 region（非空 `regions` ⇒ 不走丢 `sfx_policy` 的合成回退分支） |
| 决策等价性（vs 恢复路径 page 视图） | ✅ 逐项等价 | page_locked：`_region_or_error` 取 `p.page_locked`（:687-692）＝page 视图同值；stage_states/current_revisions 同源；`_effective_lock(target, region)` 两支结果一致（:515-525）；`_clean_available(target.page_id)`＝真实 page id；`_provider_available(run, ·)`/`_forced_steps(command)` 同一个 run/命令 |
| SFX gate 真被 `_plan_region` 覆盖 | ✅ | `service.py:418-423` 在 `_plan_region → _decide_step` 链上（`region is not None` 才求值）；生产 `handle_translate`（`infrastructure/providers/handlers.py:382-465`）确**不**调用 `decide_sfx_translation`（全仓 gate 调用方仅 `translation/context/step.py:176` 与 `rendering`，均不在本执行路径）⇒ 结论：红态发现的"克隆 decision 会绕过 gate"成立，改用 `_plan_region` 是必要且正确的选择 |
| gate 传播（translate→segment/mask_refine/inpaint/render） | ✅ | `service.py:437-446` 的 prior-decision 传播；SFX manual/skip 的克隆链因此整体不进入机翻 |
| region 已删除/状态已变时两路径行为一致 | ⚠️ 不一致 | 恢复路径 `_page_or_error` 过滤 deleted region（不抛，:640-646）；backfill `_region_or_error` 对 deleted 抛 `PipelineError("TARGET_DELETED")`（:676-677）⇒ 见 R3 |
| fan-out 集合=detect 输出（中途新增不跟进） | ✅ 设计一致 | F4 固化；与恢复路径"live"的差异是"集合在 detect 时冻结"，有文档+测试，属可接受设计选择 |
| unit_id 形态与唯一性 | ✅ | 克隆 `{task_id}:{region_id}:{step_type}`（:385）与 primary `{task_id}:{page_id}:{step_type}` 天然不冲突；task_id 含 run_id+target_order |

### C 失败传染与原子性

| 核对项 | 结论 | 证据（静态） |
|---|---|---|
| primary 失败 ⇒ 剩余克隆 unit cancel 且不执行 | ✅ | 克隆链追加在 primary 链**之后**（:980），`_cancel_remaining` 按 `task.units` 顺序对当前 unit 之后、`decision is RUN` 的 unit 标 terminal（:983-993），调用点 :804 |
| 与单 region 页语义一致 | ✅ | 同一 `_cancel_remaining` 机制，克隆链只是尾部追加；no-step-run 的 cancel 不产生副作用 |
| 既有失败/边界断言的交叉验证 | ✅ | N2（LOCK_CHANGED）、N4（PROVIDER_NOT_CONFIGURED）、N6（PROVIDER_UNAVAILABLE）在 fan-out 下仍成立（`len(ocr_steps)==1`），正确性正是来自 fail-fast，红绿两态均通过 |
| 任务状态机 | ✅ | task `FAILED` + run `COMPLETED_WITH_FAILURES`（:822-827, :1008-1016）；`retry_failed_targets` 按页重试（:905-921），重规划天然恢复 region 级 fan-out |
| F5 断言（`terminal==planned==3`，1 次 ocr step） | ✅ | REOCR_ALL 克隆链仅 1 个 forced RUN unit（`_forced_steps` :531-532），符合 |
| **账目闭合（SKIP 类克隆 unit）** | ❌ | 见 R1 |

### D 测试质量与红绿

| 核对项 | 结论 | 证据（静态） |
|---|---|---|
| 红日志构成与声称自洽 | ✅ | 文件共 17 个 test：R0,R1,R2,R3,R5 + N1..N7 + F1..F5；红 6 failed = R0,R1,R2,F1,F4,F5；11 passed = R3,R5,N1..N7,F2,F3 —— 与"6 failed/11 passed"和"R3 曾致 7 failed、按 fan-out 顺序修正为 1"完全吻合 |
| 红态成因可归因 | ✅ | R0/R1/R2 是旧"仅 primary"语义断言，F1（多 region 跟进）、F4（快照集合）、F5（planned=3）在旧码下必失败；F2/F3（单 region/0 region）红态即通过，符合"零变化守则"的设计意图 |
| 绿态日志 | ✅（Owner 产出，未复跑） | 4 份日志在 worktree 存在：target-files 19 passed、three-suites 579+2sk、overflow 188、red 6/11；`574 + 5 = 579`、`12 + 5 = 17` 算术闭合 |
| 断言的实质强度 | ✅ | 断的是 DB 行数/`region_revisions`、`step_runs.target_id` 集合、`unit.unit_id` 形态、`unit.decision`、`planned/terminal`，非 mock 内部计数；R2 由负断言翻转为正向"每个 region 都 OCR" |
| e2e 断言翻转的红证据 | ❌ 缺失 | R4 |
| 未覆盖的语义分支 | ❌ | ① SKIP 类克隆 unit 的 terminal 账目（R1）；② primary 为 SFX 时的 gate（R2）；③ 3+ region 页的扇出基数（F1/R2 用 `len(all_regions)` 泛化但 fixture 只 2 region） |
| 基线 574 的可追溯性 | ⚠️ | R5 |

### E 范围纪律

| 核对项 | 结论 | 证据（静态） |
|---|---|---|
| src 改动仅 `service.py` 单文件 | ✅ | diff 仅此一处 src；`_backfill_detected_regions` 无其它调用方（全仓仅 `service.py:657`），`@staticmethod`→实例方法无外部破坏 |
| 禁改面零 diff | ⚠️ 待 git 复核 | diff 中确无 `domain/**`、`sqlite/schema.py`、`ports/**`、`providers/**`、`bootstrap/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`STATUS`；但本沙箱不能跑 `git status/diff` ⇒ NOT_VERIFIED |
| tests 两文件改动的合理性 | ✅ 合理 | `test_regionless_rebinding.py` 是本 Task 主测；`test_sfx_policy_end_to_end.py` 改动仅 docstring + 1 条断言，属行为变更的**必然**后果，已在 Task/handoff/module docstring 三处登记（遗留：R6） |
| 零协议/零 schema 变更、持久化自动落库 | ✅ | `SqlitePipelineStore.put` 全量 DELETE+重插，含 `planned_step_units/terminal_step_units`（`sqlite/pipeline.py:393-431`）与 `pipeline_tasks.units_json`（:443-455） |
| 未跑全套件的风险 | ✅ 风险低 | 全 `tests/` 内引用 backfill/`region_ids` 的测试仅 `test_regionless_rebinding.py`、`test_sfx_policy_end_to_end.py`、`test_detect_handler.py`（知识/编辑类命中为无关同名词）；三套件+3 溢出已覆盖 |

## Findings

**R1（P2，本 Task 引入，建议阻断合并前修或显式登记）** `src/application/tasks/service.py:979-981`
克隆链只做 `run.planned_step_units += len(extra_units)`，未同步 `terminal_unit_ids/terminal_step_units`。`PlanDecision.is_terminal` 把 `SKIP_VALID/SKIP_LOCK/SKIP_POLICY` 视为终态（`domain/tasks/models.py:129-131`），而 `plan_run` 在初始规划时是计入的（`service.py:305, 311`）⇒ 两条路径账目口径不一致。可复现场景（本 Task 打开的常见生产场景）：`TRANSLATE_ALL` + 多 region 页 + 任一 SFX region 使用默认 `skip`（或 `manual`）策略 ⇒ 该 region 的克隆链 8 步中 `translate/segment/mask_refine/inpaint/render` 5 步为 `SKIP_POLICY`，全部只进分母；run `COMPLETED` 后 `get_task_progress().overall_progress < 1.0`（`service.py:1053-1057`、`projection.py:221-225`），工作台 `TaskProgressPanel.qml:119/177` 直接显示该百分比。同时与 `:953` docstring"progress and the terminal accounting still close exactly"及 handoff"planned_step_units 增量与 terminal 闭合"相矛盾。F1-F5 全用 REOCR_ALL（克隆链仅 1 个 forced RUN unit），因此**无任何测试覆盖此分支**。
建议修法（2 行）：`run.terminal_unit_ids.update(u.unit_id for u in extra_units if u.decision.is_terminal)` 后 `run.terminal_step_units = len(run.terminal_unit_ids)`；并补一条断言（多 region + SFX skip 的 TRANSLATE_ALL：`terminal == planned`）。

**R2（P2，既有缺陷未闭合 + 文档过宽，登记/裁决项）** `src/application/tasks/service.py:964-971` 与 `:418-423`
primary 只做 in-place 重绑，其 unit 的 decision 仍是 detect 前 `region=None` 的**页级**决策；`_decide_step` 的 SFX gate 要求 `region is not None`，故 primary **永不**经 `_sfx_gate_suppresses`，而恢复路径（`plan_run(continue)`）会用 live region 重规划并 gate 它。即 AC1 定义的"初始 vs 恢复语义不一致"在 `region_ids[0]` 上原样存在。具体反例：把 `tests/core/test_sfx_policy_end_to_end.py:64-104` detector 两个 candidate 的 `reading_order` 对调（sfx 成为 `region_ids[0]`）并跑 `policy=manual`，当前实现会给该 SFX region 落 `machine_translation`（`handle_translate` 无 gate，`handlers.py:382-465`）⇒ 违反 D06 §85，且与"非 primary SFX region 被 SKIP_POLICY 保持不翻译"自相矛盾。handoff 风险 #1 的"policy=manual/skip 的 SFX region 由 plan 层 SKIP_POLICY 保持不翻译"必须加"非 primary"限定。修它必然改变单 region 页行为（与"零变化"纪律/AC 冲突），**不应在本 Task 内自裁**：登记为独立 Task，或由集成方/用户就"单 region SFX 页是否也重决策"给出裁决。

**R3（P3，健壮性）** `src/application/tasks/service.py:974`（配合 `:657`、`infrastructure/sqlite/pipeline.py:664-677`）
新引入的 `self._catalog.current(region_id)` 位于 `commit_step_result` 内、detect 事务已 commit 之后，且**不在**任何 try/except 中（`execute_run` 只包住 `self._executor.execute`，`:790-797`）。若某 detect 上报的 region 在"commit 成功 → backfill 读取"窗口内被删除，或该 region 不满足 `_region_or_error` 的额外前置（`p.width/height IS NOT NULL`——注意 `_page_or_error` 并不要求，仅因导入路径恒写宽高而未暴露），`PipelineError` 会穿透 `execute_run`：DB 已落 detect 结果，但 `_mark_terminal`/`_persist` 被跳过 ⇒ 存储中 run 停在 `RUNNING`（与 DB 不一致），只能靠启动时 `recover_running_runs` 转 `INTERRUPTED` 自愈。发生概率低（同调用内无并发点），但 handoff 的"region 中途删除=TARGET_DELETED 传播是既有路径行为"只覆盖**执行层**，未覆盖这条新的**规划期读取**。建议：捕获 `PipelineError` 后按 `TARGET_DELETED` 语义跳过该 region（或走 `_fail_step`），并在风险清单补一句。

**R4（P3，证据完整性）** `verification/M2-TASKS-BACKFILL-MULTIREGION/red-f99a6c55-src-plus-tests.log`
红态日志只覆盖 `tests/pipeline/test_regionless_rebinding.py`，而本 Task 同时翻转了另一 Task 交付物 `tests/core/test_sfx_policy_end_to_end.py` 的断言（`"" → MOCK_SFX_TRANSLATION_TEXT`）。该断言翻转是本 Task 最直接的"行为改变"证据，却只有绿态（target-files 19 passed）。请集成方复现并归档 e2e 红态（`git checkout f99a6c55 -- src/application/tasks/service.py` 后跑该文件 2 条测试），否则该断言变更的证据链不闭合。

**R5（P3，测试口径登记不够硬）** handoff §验证证据第 1 行
零回退的参照基线 `574+2sk @ f99a6c55` 标注"会话记录（未入库）"，且该测量所用 venv 在本会话被中途补装 `onnxruntime`（`T3.2.1-packaging-py312`）。即"0 failed"依赖一份未归档、且环境被改动的基线日志；与 STATUS 的 `530+1sk` 差异被归因于"f99a6c55 批次新增测试"（+44）但未逐项列出。口径差异已如实登记（值得肯定），但不足以支撑"零回退"结论，必须由集成方在主 venv 重跑双侧基线。

**R6（P4，跨 Task 记录闭环）** `tests/core/test_sfx_policy_end_to_end.py:11-33` 与 `doc/handoffs/M2-SFX-TRANSLATE-ENTRY-*.md`
本 Task 修改 SFX-ENTRY 交付测试的断言是合理且必要的，登记也到位；但 SFX-ENTRY 侧记录仍写着"multi-region page needs one TRANSLATE_ALL run for detect+creation and per-region follow-up runs"与"the registered scheduling slice"，已被本 Task 推翻。建议集成时在 SFX-ENTRY 的 Task/handoff（或 STATUS 交接口径）加一行 superseded-by 说明，避免后续 Agent 以旧语义为事实源。

**R7（P4，规模化提示）** `src/application/tasks/service.py:782-787`（`ResourceLimits.max_step_runs=1000`）
fan-out 使单页 unit 数≈region 数×步数（TRANSLATE_ALL 17 region ≈ 136+ units），多页 chapter 选择会显著提高触发 `RESOURCE_LIMIT_EXCEEDED` 的概率（fail-closed，非数据损坏）。这是修复后的正确代价，但 handoff 风险清单未提；建议补一行，供后续按需评估限额/批处理策略。

## NOT_VERIFIED（集成方运行时项）

1. **任何测试执行**：沙箱无 shell，`579 passed + 2 skipped`、`19 passed`、`188 passed`、`6 failed/11 passed` 均取自 Owner 日志与 diff，未复跑。可静态确认的只有数字自洽（rebinding 文件 17 个 test = 12 旧 + 5 新；`574+5=579`；红 6 名单与断言翻转一一对应）。
2. **Git 事实**：`branch=agent/zcode/M2-TASKS-BACKFILL-MULTIREGION`、`base/fork=f99a6c55`、`implement=f541b2f4`、`tip=fa866327`、`git diff --check EXIT=0`、`git status --porcelain`、禁改面"零 diff"、以及 `review-input.diff` 是否等于完整的 `f99a6c55..fa866327`（含未跟踪文件）——全部未验证。
3. **e2e 红态**：`test_sfx_policy_end_to_end.py` 在 f99a6c55 src 下必失败（断言翻转）未复现；"初版克隆实现被 e2e manual 红态抓到"亦无归档日志（仅口头声称，机理上成立：`handle_translate` 无 gate）。
4. **主 venv 基线/回归**：`530+1sk` 基线、`f99a6c55` 主 venv 实测、`f541b2f4` 主 venv 实测（预期 +5）未验证。
5. **运行期行为**：R1 的 `progress_percent` 卡在 <100% 的实际观测、R2 的反例（对调 reading_order）实际复现、R3 的异常穿透实测——均为静态推断，需运行时确认。

## 集成方闭合清单

1. `git diff --stat f99a6c55..fa866327` + `git status --porcelain` + `git diff --check`：确认改动面=handoff/Task + `src/application/tasks/service.py` + 2 个测试文件 + 4 份 verification 日志，且与 `review-input.diff` 一致（含未跟踪文件）。
2. 主 venv 双侧复跑：`f99a6c55`（预期 530+1sk）与 `f541b2f4`（预期 +5）；同时归档 `f99a6c55` 基线日志，替换 handoff 中"会话记录（未入库）"。
3. 归档 e2e 红态（old src + new tests，跑 `tests/core/test_sfx_policy_end_to_end.py`），补齐 R4。
4. 裁定 R1：就地修（`terminal_unit_ids/terminal_step_units` 同步 + 新增"多 region + SFX skip ⇒ terminal==planned / progress==1.0"断言）或开独立 P2 Task；修/不修都须同时修正 docstring `service.py:953` 与 handoff 风险 #4 的"账目闭合"表述。
5. 登记 R2 为独立 Task（含"单 region SFX 页是否重决策"的裁决请求）；把 handoff 风险 #1 改为"非 primary 的 manual/skip SFX region"。
6. 在 SFX-ENTRY 记录加 superseded-by 说明（R6）；在风险清单补 R3 与 R7 两条。
7. Review 结论回流 Task（`status` 由 `in_review` 进入集成态）并保留本 Review 作为 `verification/` 证据。

## 推荐下一步（一句）

把本 Review 交给编排会话（代行 Codex）落集成 Gate：先执行闭合清单第 1–3 项运行时复核，再就 R1 就地修或开 P2 Task、并就 R2 的 primary-region 语义提请裁决，全部闭合后方可将本 Task 置 `done`。
