dsh: reasoning:
Let me start by exploring the repository and the diff.

I need to do a static review. Let me read the diff, Task, Handoff, and relevant source files.

Let me plan: read the diff file first, then relevant sources.

The worktree is at G:/CODEX/New Manga.worktrees/M2-SFX-TRANSLATE-ENTRY-zcode. Session workspace is G:\CODEX\New Manga. File sandbox is workspace-write, so reading outside workspace... reading may be allowed. Let's try.

Let me start with the diff.
dsh: reasoning:
The pwsh failed for a sandbox reason (grantWrite failed). Let me try read tool instead.

Let me read the diff with the read tool. It might be big. And the Task file.
dsh: reasoning:
Now let me inspect the actual worktree files to verify the claims: core_assembly.py, gate.py, step.py, service.py (tasks), editing/service.py, models.py (domain/tasks/models.py), domain/regions/entities.py (SfxPolicy), schema, pipeline_defaults.py, handlers.py, mock_local.py.

Also check the contracts TASK-002 §4.

Note the repo at workspace is G:\CODEX\New Manga (maybe master). The worktree is at G:/CODEX/New Manga.worktrees/M2-SFX-TRANSLATE-ENTRY-zcode. Let me check whether I can read outside session workspace. The file sandbox is workspace-write for "G:\CODEX\New Manga". Reading outside might be denied. Let's test with read on the worktree file.

Actually the diff contains the full changes. But I need to verify base code (e.g., _load_pipeline_defaults, create_region signature, SfxPolicy enum, gate semantics, save_settings_section). Those are unchanged files; I can read them from the main repo (master at 8996ca55? base=8996ca55 per prompt; Task says base_commit 8e0de8d0 — discrepancy! The prompt says base=8996ca55, implement=a377a25a, tip=453f6d73. Task file says base_commit: 8e0de8d0. Hmm, that's a discrepancy worth noting: handoff says base_commit 8e0de8d0, prompt says base=8996ca55. Possibly 8996ca55 is the integration base (master tip) and 8e0de8d0 the branch base. Need to check.

Let me try reading the worktree files.
dsh: reasoning:
Good, worktree is readable. Now let me check:
1. `_load_pipeline_defaults` implementation — settings read.
2. `save_settings_section` semantics.
3. consumes points: step.py:176, tasks/service.py:418.
4. editing/service.py create_region signature.
5. domain Region SfxPolicy default.
6. Whether assemble reads settings before/inside try; the sfx_policy_cfg read is placed inside `try:` after opening DB. Check that the read happens in both mock and non-mock branches — yes it's before the `if mock_local_providers:`.

Also important: is `_load_pipeline_defaults(conn)["settings"]` a dict? Let's check.

Also check whether reading settings requires pipeline_defaults service to exist/row; if no row exists, does _load_pipeline_defaults return default with "settings" key? Check.

Also check `editing.create_region` signature: keyword `sfx_policy`. And whether create_region validates region_type sfx + policy. Also check what default it uses.

Let me read those.
dsh: reasoning:
Now read _load_pipeline_defaults in worktree (line 448-...) and the assembly segment 820-1080 to check placement and the closure.

Note line 839: `provider_bindings=_load_pipeline_defaults(conn)["provider_bindings"]` — there's a separate read for the service. Wait, where is that? Let me read lines 820-900 and 1000-1130.

Also note duplicate reads of pipeline defaults — performance/consistency, but fine.

Important: check whether `_load_pipeline_defaults` returns "settings" possibly as a JSON string or dict.
dsh: reasoning:
Now check the closure 1000-1070, plus create_region in editing/service.py, region entity SfxPolicy default, and the detect handler's region_creator call signature.

Also need to check whether there is a second region creator path (e.g. in acceptance bridge or detection_sfx) that also creates regions without policy — not necessary.

Key claim about "仅 SFX 候选" — verified in diff.

Another key: is `region_type is RegionType.SFX` identity comparison safe? RegionType is an enum, so `is` works for enum members. Fine.

Now the "zero behavior change" claim for non-SFX: previously region_type already SFX with default policy SKIP. Now SFX candidates get SfxPolicy.SKIP when unconfigured → same. But wait: is `editing.create_region(..., sfx_policy=SfxPolicy.SKIP)` identical to not passing? create_region's default is presumably SfxPolicy.SKIP. Let me verify. If the default were None or something else, passing SKIP explicitly could be different. Check editing/service.py.

Also, the closure now passes sfx_policy always (even SKIP) which may override create_region behavior for non-SFX regions — check whether create_region raises if sfx_policy != SKIP for non-SFX region, or whether passing SKIP for speech is fine.

Let's read editing/service.py around create_region.
dsh: reasoning:
Good. create_region default SfxPolicy.SKIP; passing SKIP explicitly is identical.

Now check the closure in the worktree lines 1000-1070, and whether region_creator type/port signature changed (ports shouldn't change).

Also check consumers: step.py:176 and tasks/service.py:418.

Then check TASK-002 contract §4/§7.2 for sfx_policy semantics.

Also check the mock_local MOCK_SFX_TRANSLATION_TEXT to confirm the end-to-end proof (region_type == "sfx" gate).

Also check that `mock_local`'s translation provider returns MOCK_SFX_TRANSLATION_TEXT only for region_type "sfx" — verifying the test claim.

Let me batch reads.
dsh: reasoning:
Now check `_sfx_gate_suppresses` definition and `_SFX_GATED_STEPS` in tasks/service.py. Let me grep.

Also check the contract TASK-002 §4 and §7.2 concerning sfx_policy and region_type.

Also check the mock_local translation provider.

Also check whether there are other region creation paths in production detect (e.g., detection_sfx provider registering regions?) - claim says only closure.

Also: check whether `Mapping` import from collections.abc and `Any` from typing are fine (they are used). Note `isinstance(section, Mapping)` with collections.abc.Mapping works (ABC with __subclasshook__). Fine.

Potential issue: settings values come from JSON; a JSON list would fail isinstance(Mapping) → ValueError. A JSON string for "sfx" section → ValueError. Good.

Potential gap: `settings["sfx"]` as a mapping but with extra keys — fine.

Potential coverage gap in fail-fast: non-string same as bool? `{"policy": True}` → bool is not str → ValueError. Covered by "not a string". List/dict also covered.

But: what about a section that is a Mapping but the policy value is e.g. `{"policy": "translate "}`? covered.

What about settings itself being not a Mapping? `_sfx_policy_from_settings(settings)` calls settings.get — if a corrupted JSON gives dict always (from _mapping). The function is annotated Mapping; passing None would AttributeError. Since _load_pipeline_defaults always returns dict, fine. Minor.

Now consider: the read happens after `_load_pipeline_defaults` at line 839 (provider runtime) — no issue.

Another potential concern: the assembly reads `_load_pipeline_defaults(conn)["settings"]` at line 879-881, which is inside the outer `try:` that presumably does `conn.close()` on failure? Let me check: the assembly is `conn, opened = open_database(...)` then `try: ... except: conn.close(); raise`. If the ValueError propagates, the connection closed. Let's check the top-level try/except structure — is there a `finally` that closes conn? Look at lines 776-800 and the end of function. Actually the diff shows `sfx_policy_cfg = ...` inside the try block. Let's check exception handling around to ensure fail-fast doesn't leak the sqlite connection (resource leak on assembly failure). That's a legit finding if there's no except closing. Let's read around 780-800 and the function's except clause (search "except" near end).

Also check whether the ValueError from fail-fast leaves a partially initialized state — probably fine as the function raises.

Let me also check pipeline_defaults row: `save_settings_section` writes to storage via `_save` bridge. In tests they use `core.pipeline_defaults`. Fine.

Another thing: does anything else consume `settings["sfx"]`? e.g., pipeline snapshot settings. Probably no.

Now, importantly: the "Ocr script" same-channel claim: is `settings["ocr"]["script"]` actually read anywhere? Let me grep for "script" in core_assembly or settings consumers to verify the precedent (that ocr.script rides that channel and is read). If ocr.script is written but never read, the claim "same channel" is about write path only. Let me grep.

Let me batch: grep `_sfx_gate_suppresses|_SFX_GATED_STEPS` in tasks/service.py; grep `"script"` / `script` in src for settings consumption; read mock_local translation part; read contract TASK-002 relevant sections.
dsh: reasoning:
Interesting: `settings["ocr"]["script"]` — let me check how the ocr.script key is consumed. Grep for "script" in src to see if there's a reader. The handoff claims "settings 通道先例：save_settings_section("ocr", {"script": ...}) → pipeline_defaults 行 settings_json → 装配侧 _load_pipeline_defaults(conn) 可读". "可读" = readable, not necessarily read. So claim is that the channel exists. Fine.

But wait: is there a reader for "ocr.script" specifically at assembly to project onto runtime settings? `_load_pipeline_settings(conn)` returns the whole settings dict; then build_provider_runtime(settings=...). So any settings key is passed to provider runtime. So the "same channel" is accurate.

Now, an important consideration: does passing settings to build_provider_runtime validate unknown sections/keys? If a provider runtime validates settings strictly, adding "sfx" section could break? No — new section only appears when user writes it. But could the settings section "sfx" be misinterpreted by build_provider_runtime as a provider profile section? Let's check build_provider_runtime to see if it consumes settings sections by name. If it treats settings top-level keys as provider ids, then "sfx" section might be interpreted as provider config and cause an error. Let me check.

Also check ui/viewmodel.py settings — which sections it supports (section names). If there's a closed list of sections, "sfx" might be rejected in UI (not in scope, but relevant to AC1 "product entry" claim). Let's look at viewmodel.py around 400-530 to see if sections are whitelisted.

Let me also check TASK-002 contract for sfx_policy semantics.
dsh: reasoning:
Let me read TASK-002 §7.2 and §4 to check the contract claim: "sfx_policy 三值语义已在 SFX-SEM-1 契约化". §7.2 SFX safety rule. Let me read the contract around §7.2.
dsh: reasoning:
Contract §7.2 defines the three-value policy semantics (skip/manual/translate) as region-level policy behavior. It doesn't define where the policy value comes from (no settings key spec). §4 1.1 revision defines region_type carrying. So the "TASK-002 needs no revision" argument is plausible: the new settings key is a configuration entry, not contract semantics. But one could argue: contract §7.2 defines policy semantics but not the configuration channel; adding a persisted settings key is a new persistent storage key that may need contract registration (TASK-002 is the minimum data/execution contract; settings keys live in TASK-050?). The Handoff acknowledges this and defers to integrator. That's an acceptable judgment — I can flag it as a P3/P4 observation: the settings key becomes part of the persisted data/execution surface read by assembly; but TASK-002 covers execution semantics, and TASK-050 covers the pipeline_defaults channel. Check TASK-050 contract doc for whether settings sections are enumerated (closed set). If TASK-050 enumerates known sections, adding "sfx" might need registration. Let me check doc/contracts for TASK-050 and any settings section enumeration / IPC contract listing settings sections.

Also check the UI viewmodel settings sections whitelist, and check the React/IPC contract (M2-C1 Typed IPC) for settings keys — if the IPC contract enumerates allowed settings sections, then writing "sfx" via IPC would be rejected → the "product entry" is not reachable by user yet (already admitted in Handoff as not done: UI entry not made). That's a known limitation, listed as risk 2. Fine but worth verifying whether the claim "核心通道 save_settings_section 已可用" holds end-to-end for a user path. Let me check the IPC surface: grep for "settings" in src/ipc or apps.

Let me check contracts dir listing and grep for "ocr" and "script" in doc/contracts to see if any contract enumerates settings sections.
dsh: reasoning:
No contract mentions settings sections. So the Handoff argument is consistent: no contract enumerates settings keys; the sfx policy key is a new config entry. But TASK-002 §4 / region schema has sfx_policy column with three values; the new bit is where it comes from. I'd say the judgment "TASK-002 不需修订" is defensible, with a P3 note that the persisted settings key `sfx.policy` now becomes a de-facto assembly contract not registered anywhere (only Handoff), and the IPC/settings UI contract (M2-C1) will need it when the entry is exposed — the Handoff already says so.

Now check M2-C1 IPC contract for settings section exposure — does it have a whitelist for settings sections? If yes, and "sfx" isn't in it, the user-facing entry is blocked (Handoff risk 2 covers it partially: "用户配置当前经 IPC/开发者路径" — hmm, it says "用户配置当前经 IPC/开发者路径", implying IPC path exists). Let me verify: grep M2-C1 for settings.
dsh: reasoning:
The IPC contract has `SaveSettings` with `{section, values}` — generic section, so "sfx" can pass through. Good; AC1's channel is genuinely reachable via the existing generic IPC exchange (though no UI in React yet). So the Handoff risk 2 statement "用户配置当前经 IPC/开发者路径" is roughly accurate: IPC exchange is generic (AS-IS) — but is the IPC bridge implemented? Let's check whether SaveSettings handler exists in src (ipc). Quick grep.

Also verify handlers.py detect region_creator call passes provider_label (5th positional) and that the closure signature matches. The diff didn't change the closure signature. Let me check handlers.py:287.

Also check tests/core/test_sfx_assembly.py & test_core_detect.py exist (referenced as precedents) to see the R9 seam helper duplicated.

Also confirm no other call sites to create_region in src that create SFX regions (detection_sfx?). Grep create_region in src.
dsh: reasoning:
Note: no typed IPC SaveSettings handler in src (the M2-C1 contract says AS-IS in-process VM only). So the user-facing entry today is the in-process Settings VM (`ui/viewmodels/settings/viewmodel.py:435` save_section generic). The UI is Legacy PySide/QML, which per AGENTS.md is historical-only, product architecture = React/Tauri. So "product entry" for the user is not yet reachable through the new architecture — acknowledged in Handoff risk 2 (suggest Qoder later). Relevant to AC1? AC1 says "sfx_policy 从 provider/pipeline 设置读取（复用既有 settings/profile 通道…）" — reading is done; the write channel is generic existing. So AC1 satisfied at the core level; the actual user-visible entry is deferred and disclosed. I'll note as P3 finding: AC1 "可配置入口" is only a library-level write path (save_settings_section) — no production user path exists today (Legacy VM is retired; React settings page/Tauri IPC SaveSettings not implemented). That's disclosed as Handoff risk 2 but the Task's stated purpose was "SFX→translate 产品入口" / "解除评测 n=0 的前置阻断" — for evaluation purposes, a script/dev path suffices. So it's acceptable but should be explicit. Since Task AC1 doesn't require UI, not a violation. P3 info.

Now let's check the acceptance_bridge.py:311 create_region call — does it also need policy? Acceptance bridge seeds regions; with sfx_policy default SKIP. Not in scope.

Now the important verification aspects:

A. Default zero change:
- `_sfx_policy_from_settings({})` → SKIP.
- closure passes SKIP for non-SFX and `sfx_policy_cfg` (SKIP when unconfigured) for SFX → identical to before (create_region default SKIP, and old call passed no sfx_policy).
- Does anything else create SFX regions with policy? Only this closure. Good.
- Configuration leakage: region_type determined by provider_label prefix `SFX_LABEL_PREFIX`; non-SFX gets hardcoded SKIP → no leakage. Good.
- Risk: a *user-created* region of type SFX (via editing/UI) still defaults SKIP; the setting doesn't apply to user-created SFX regions. Is that a behavior gap? The Task scope is detect-created regions ("生产链 SFX region"). But semantics: setting "sfx policy" applies only to machine-created SFX regions at creation; a region created before the setting change keeps its old policy (re-assemble doesn't migrate existing rows). This means existing SFX regions from previous runs remain SKIP forever unless re-detected. That's an important semantic note for the "product entry" — turning on translate does NOT retroactively translate already-created SFX regions; the region must be re-created (or the policy updated per region). Registration: with translate configured, previously detected pages would not change. That's a real limitation worth flagging P2/P3: the config entry only affects newly created regions; no migration/retro-apply and no per-region policy edit path surfaced in this Task. Is there an edit path for sfx_policy elsewhere (apply_sfx_policy exists in entity)? Let me check if any application service exposes sfx_policy editing (apply_sfx_policy users). Grep apply_sfx_policy.

B. fail-fast matrix:
- covered cases: section absent, section None, section not Mapping, key absent, key None, non-str, unknown word, blank, case/whitespace normalization.
- Coverage gaps to note:
  1. whitespace-only *section value* covered by normalized check.
  2. non-string keys not relevant.
  3. `settings` not a Mapping (None) → AttributeError not ValueError; but unreachable via `_load_pipeline_defaults` (always dict). Note only.
  4. A JSON `settings` value could contain nested `{"sfx": {"policy": "translate", ...}}`; fine.
  5. bool `True` is not str → ValueError. Good.
  6. What about a policy value like `"SKIP\n"`? strip handles. `"trans\u200blate"`? not covered — trivially fine.
- Placement: mock branch outside — confirmed line 879-881 (inside outer try, after env gates, before `if mock_local_providers:`). ✓
- ValueError message prefix: two of three messages start with "invalid settings sfx.policy:" and the third "unsupported settings sfx.policy ...". All contain "sfx.policy" ✓. Regex match in tests uses "sfx.policy" — note `.` in regex matches any char, minor.
- Note: the ValueError is raised at assembly but *where* relative to DB opening: assembly raises after `open_database`, which may run migrations on the DB before failing. So "fail-fast" still performed migrations. Minor, P4 (same as env gates which run after migrations too, so precedent-consistent).

C. Test quality:
- Qt-free 19 tests: matrix 9 + illegal 6 + 4 assembly tests = 19 ✓ (9+6+4=19). ✓
- end-to-end 2 ✓.
- Do the e2e tests truly exercise plan gate + step gate? The translate test asserts `decisions[(region_id,'translate')][0].value == 'run'` from finished.tasks units → that's plan-level decision (tasks/service _decide_step → SKIP_POLICY) proving plan gate. And the persisted MOCK_SFX_TRANSLATION_TEXT proves step-level gate (execute_translate_step decides per entry) admitted. Hmm — actually does it prove step gate consumed? If the plan gate allowed the run, and step gate skipped, the region would have no translation. Since translation landed, the step gate did not skip → step gate consumption is proven transitively. Yes, both consumed. Also the mocked provider returns SFX text only for region_type=='sfx' — proving the type passthrough.
- manual test asserts `all(step.step_type != "translate" for step in retranslate.step_runs)` and decision skip_policy/sfx_skip from units → plan-level registration. ✓ And OCR ran → manual keeps OCR ✓.
- Does the manual test prove the step-level gate? No: the plan gate already blocks translate, so the step gate isn't exercised for manual. But `decide_sfx_translation` for manual is already covered by existing SFX-SEM-1 tests (claim: gate.py unchanged). Acceptable; note as minor coverage observation (P4) — the e2e manual case proves plan-level suppression only, not that execution would also skip if planned. Existing tests presumably cover gate unit semantics; let me verify tests for gate manual exist (grep tests for decide_sfx_translation).

- The `_detect_deps` helper relies on closure introspection of `core.pipeline._executor._handlers["detect"]` and monkeypatches `deps.detector` — a test-only seam. It's marked as the DSH r1 R9 precedent. Note that this is white-box and brittle (private attrs `_executor`, `_handlers`), P4 info. Actually it also *mutates* the deps object of a real assembly; fine for test.
- The e2e test relies on `assemble_acceptance_core` and mock bindings (`m2ac1-mock-ocr`, `m2ac1-mock-translate`) — are these provider ids correct/existing? Let me verify they exist in mock_local / acceptance fixture. grep "m2ac1-mock".
- `_scenario` returns `_build` which tests ignore (`_build` unused in body — assigned but unused). Trivial.
- `page_id` param unused? used.
- In `_scenario`, `core.conn.close()` then rebuild — fine.
- Test asserts `regions["speech"]["sfx_policy"] == "skip"` — real leakage check ✓.
- Note: e2e asserts `steps["detect"].status is StepRunStatus.COMPLETED` — first_run includes detect.
- `_run_region_command` blocked → resume_blocked; sensible.

Potential issue: the e2e test monkeypatches the detector *after* assembly, replacing the mock detector for the already-built handler deps. Does the detect handler's deps hold a reference to the detector captured at assembly (yes) — assignment works since deps is a mutable object. OK.

Verify mock provider ids exist. grep.

D. Scope discipline:
- diff touches: doc/handoffs (new), doc/tasks (frontmatter + 交付记录), src/bootstrap/core_assembly.py, 2 new test files. All allowed面 (allowed: src minimal面, tests/**, Task/Handoff). Worktree branch tip 453f6d73 = handoff commit; the review diff includes handoff+task+code+2 tests. Prompt says diff = review-input.diff from base 8996ca55 to tip 453f6d73. Need to check: does the worktree contain any uncommitted changes? Can't run git (shell blocked). Hmm — pwsh failed with sandbox error "grantWrite failed". So no shell. Static review only; mark NOT_VERIFIED for git status/porcelain and test runs.

Wait — can I try pwsh again? It failed at sandbox setup ("SetNamedSecurityInfoW failed (Win32 5): grantWrite"). Probably will fail consistently. The user said "沙箱无 shell 时不执行命令" — treat as no shell. So NOT_VERIFIED for runtime items. I can still try glob/grep/read.

- models.py zero change: verify domain/tasks/models.py sfx_policy default and that worktree file equals master's. I can compare the worktree file vs master file by reading both (diff hunks only cover core_assembly + docs + tests, so by definition of the diff, models.py unchanged). The diff is authoritative if it's the actual diff from base to tip. But the prompt says diff file is provided; I should verify its completeness claims by checking file contents in the worktree for the claimed untouched files? A cheaper check: confirm worktree core_assembly has the changes (done ✓) and that other claimed-untouched files carry no `_SFX_SETTINGS_SECTION`/sfx settings read (grep ✓ only core_assembly). For git-level proof, NOT_VERIFIED.

E. Contract judgment: as analyzed, defensible. §7.2 defines three-value semantics (already contract'd); §4 1.1 defines region_type transport. The new thing is the settings source, which no contract enumerates (TASK-050 is a Task not a contract; check if TASK-050 exists as task doc and whether it enumerates settings sections... it's the pipeline defaults channel; the sfx section is a new section name within it. If the IPC contract exposes SaveSettings generic {section, values}, no revision needed. I'll conclude: no contract revision strictly required; but recommend registering `sfx.policy` in the settings-key registry (if one exists: doc or code listing known settings sections). Let me check whether there's a documented list of settings sections (e.g., in ui/viewmodels/settings/viewmodel.py or docs) — if a canonical list exists, the new key should be added there (but that file is Legacy UI, out of allowed面?). Let's check viewmodel around 400-530 for a section whitelist.

Let me also check TASK-050 task doc for settings section enumeration, and whether any docs list settings keys (doc/ references). grep doc for "ocr.script" or `"script"`.

Let me batch:
1. grep src for "m2ac1-mock"
2. read ui/viewmodels/settings/viewmodel.py 400-530
3. grep doc for ocr.*script / settings section list
4. grep tests for decide_sfx_translation (existing coverage of manual)
5. grep src for apply_sfx_policy usage.
dsh: reasoning:
Good — the `ocr.script` precedent is real: M2-TA3-B2 handoff F6 says production settings `ocr.script=korean` written via `save_settings_section`. And TASK-050 docs confirm the settings channel read at assembly (settings_snapshot). Note: `ocr.script` is consumed by provider runtime via `_load_pipeline_settings`. Our new key is read directly by `_load_pipeline_defaults`. Both from the same row; so "同通道" is accurate.

However — one subtle asymmetry: `_load_pipeline_defaults(conn)["settings"]` vs `_load_pipeline_settings(conn)`. Are they equivalent? Let me check `_load_pipeline_settings` (lines 491-...) to make sure they decode the same row/column. If `_load_pipeline_settings` has different tolerance/semantics, using the other reader is fine but worth noting for symmetry. Let me read it.

Also check the ui settings viewmodel: does the Legacy settings UI have a whitelist of sections? Line 435 is a generic `save_section`. Let's read 400-530 quickly to assess whether a user could write "sfx" through the existing UI (affects AC1 "product entry" claim). Actually, Legacy UI is retired per AGENTS.md, so less important. But the Handoff claims "用户配置当前经 IPC/开发者路径". Let me confirm whether the Legacy VM validates section names — if it does whitelist, then "用户路径" claim would be weaker. Let me read.

Also verify `_SFX_POLICY_VALUES` ordering and that SfxPolicy values are exactly skip/translate/manual ✓ (from entities: SKIP skip, TRANSLATE translate, MANUAL manual).

Another check: `tuple(policy.value for policy in SfxPolicy)` — fine.

Also `from typing import Any` — style: the file may already use `Any`? Diff adds the import. Fine. Note `Mapping` from collections.abc — used in isinstance; fine (runtime-checkable ABC).

Now think about whether `_sfx_policy_from_settings` normalization to lower could mask a config error: "Translate" accepted; fine.

Now the semantics question raised earlier: existing SFX regions created before configuration keep SKIP. Does any code path apply the configured policy to existing regions on re-assemble? No. So enabling translate requires new detect or per-region policy edit. Is there an app service exposing sfx_policy update? grep apply_sfx_policy usage: only definition in entities (no callers besides?). The grep on tests found none; let me grep src for apply_sfx_policy.

This matters for AC1's stated purpose ("解除 SFX 翻译评测 n=0 的前置阻断"): to evaluate SFX translation on existing pages, the user must re-run detect (which requires deleting existing regions? detect handler reuses existing live regions! Look at handlers.py lines ~255-269: if `live` regions exist, it reuses them and returns without creating new ones). So for a page already detected (the TA3-B2 corpus), enabling translate and re-running detect will NOT re-create regions — the existing SKIP regions are reused → translate path remains unreachable for existing pages. Hmm! That's a substantive finding: the setting only takes effect at region *creation*; for already-detected pages (which is exactly the TA3-B2 corpus with 9 SFX regions), the only way to apply the configured policy is to delete/re-create regions or edit policy per region — and this Task provides no per-region policy update path (no IPC/UI). Let me check whether "live" reuse indeed happens: read handlers.py 240-270 fully. And whether there's some other path that re-applies policy (e.g., detect handler updates existing region policy? reuse returns regione ids without policy update).

That could be a P2 finding (functional gap for the stated purpose) or at least a P3 documentation/scope note. The Handoff discloses re-assemble semantics ("settings 改后下一次 assemble 生效") but does NOT disclose that already-created regions keep their old policy and that detect reuses existing regions. Their risk 3 says "translate 路径生产可达但需用户显式配置" — but for pages already detected, it's not reachable without re-creating regions. Their e2e test uses a fresh temp DB, which masks this.

Let me verify the reuse path and whether any delete-regions path exists (delete_region soft-deletes; then detect would create again since live excludes deleted? `_live_regions` presumably filters deleted). So user could delete regions then re-detect. But is there a UI path? In new architecture, workbench region delete maybe exists. Anyway, the finding: enabling the policy on an existing library requires region re-creation (detect reuses live regions), no retro-apply; must be disclosed.

Let me read handlers.py 230-270 and check `_live_regions`/reuse condition. Also check detect step's "skip if regions exist" planning (the detect step may be skipped entirely when regions exist). In tasks service, detect step decision may SKIP_VALID if stage completed. In the e2e test they ran TRANSLATE_ALL on a fresh page.

Let me read handlers.py 225-270.
dsh: reasoning:
Confirmed: detect reuses live regions, so the policy is applied only at creation. `_load_pipeline_settings` and `_load_pipeline_defaults` decode the same column with equal tolerance (dict or {}). Symmetric ✓. Minor duplication (two independent reads of the same row; if a settings write happened between line 839 and 879 — impossible within one assembly, single-writer). P4 note.

Now, is the "existing SFX region retro-apply" gap a genuine P2 finding? The Task AC1 says "sfx_policy 从 provider/pipeline 设置读取…默认仍 SKIP，可配置为 translate/manual" and AC2 "detect 装配把策略传到 region 创建/翻译门消费点". AC explicitly says "region 创建" — so applying at creation only matches AC. The background says the goal is to unblock evaluation n=0 — for new detections, achievable. For the TA3-B2 corpus (already detected), re-detect reuses regions → still SKIP. To run SFX translation eval on that corpus, one would need to re-create regions (e.g., delete regions or use fresh import). Actually wait — in the TA3-B2 experiments, they possibly used the acceptance harness which *seeds* regions up front (acceptance_bridge.py:311 create_region). In the acceptance/eval harness path, regions are seeded by `assemble_acceptance_core`'s seeding code, NOT via the detect closure! Look: acceptance_bridge.py line 311 `state.core.editing.create_region(...)` — the acceptance loop seeds Regions up front (core_assembly comment line 845-847: "The acceptance loop seeds Regions up front, so its pipeline plans the region-level chain and never executes detect"). So the TA3-B2 evaluation harness creates regions itself with default SKIP — and this Task's change in `_create_detected_region` does NOT affect that seeding path!

That is potentially a significant finding: if the SFX translation evaluation (TA3-B2, n=0) is run through `assemble_acceptance_core`/acceptance seeding, then the policy configured in settings will NOT reach those seeded regions (they call `editing.create_region` directly, default SKIP). Then the stated purpose "解除 SFX 翻译评测 n=0 的前置阻断" would be unmet for the harness that produced n=0.

Let me examine acceptance_bridge.py around 280-360 to see how regions are seeded and whether it reads settings/policy.

This is important. Let me read it.
dsh: reasoning:
Confirmed: the acceptance harness (`method_seed_fixture`) creates regions directly with default SKIP. If TA3-B2's SFX evaluation used this harness path (or a similar seeding path), then configuring `sfx.policy=translate` would NOT affect seeded regions — the SFX eval would remain n=0 unless the harness is changed (which is outside this Task's allowed面? acceptance_bridge.py is in src/, allowed面 is "src/（detect/translate 装配+settings 读取的最小面）" — arguably acceptance_bridge seeding is another minimal面 but the Task's AC2 says detect 装配 → region 创建, so seeding path is out of AC).

Now, how did TA3-B2 produce "9 SFX regions all SKIP"? Let me check the M2-TA3-B2 handoff/task to determine whether regions came from the detect path or a seeding path. That determines whether this Task actually unblocks the stated goal. Let's look at the TA3-B2 handoff and verification evidence.

Let me grep doc/handoffs/M2-TA3-B2-3c8801b7.md and doc/tasks/M2-TA3-B2.md for how SFX regions were created.
dsh: reasoning:
Key: TA3-B2's SFX regions came from the real production chain? §4: "SFX 翻译语义本 run 未被真实触发（生产 SfxPolicy 默认 SKIP 且无产品改置入口）". The run used the real production pipeline (experiments/M2-TA3-B/run_qualification.py) — probably with real detection (ogkalu + chiqui7 SFX parallel) → regions created via the detect step's region_creator → this Task's fix directly applies. So the change does unblock the TA3-B runner (which detects regions through the production chain). Let me verify briefly that the runner uses the production assembly (core_assembly) and detect path, not acceptance seeding. The handoff mentions "真实 docTR detect"→"真实 manga ogkalu detect（+chiqui7 SFX 并行）" so yes, real detect path → region_creator. Good — so my earlier concern about acceptance harness seeding is a separate path, not the eval path. Still worth a note (P4/P3): the acceptance bridge's fixture seeding path bypasses the policy, so m2_acceptance SFX coverage can't exercise it; but the e2e test covers production detect closure. Actually the e2e test uses assemble_acceptance_core but drives the detect chain via the real closure (monkeypatched detector) — it bypasses the seeded regions intentionally (fresh page, no seeding). Good.

Wait: does `assemble_acceptance_core` run `method_seed_fixture`? The e2e test calls `assemble_acceptance_core(tmp_path/"data", ...)` which just builds core + acceptance bridge; no seeding unless method_seed_fixture called. ✓.

Now let me double-check the claim "既有测试零修改" and "530 passed" — NOT_VERIFIED (no shell). Also verify the new test files exist in the worktree with same content as diff (to make sure the diff matches the worktree tip). Let me read the worktree test files' sizes/hashes? I can read them and compare quickly with diff content — spot check.

More critical static checks remaining:
1. Does the worktree core_assembly have exactly the diff changes and nothing else? Compare with master file: I could compute a diff-ish comparison by reading the master file's same region. The diff is provided as authoritative; but to catch e.g. an uncommitted extra change... can't verify without git. NOT_VERIFIED for "worktree == diff".

Actually, hold on: prompt says base=8996ca55 but Task/handoff say base_commit=8e0de8d0. The diff might be computed from 8996ca55 (integration base). If base differs, the diff could include unrelated changes from other work merged between 8e0de8d0 and 8996ca55. The diff we got shows only 4 files — so either base is the same effectively for these files, or the review-input.diff was generated with `git diff 8996ca55...453f6d73`. If 8996ca55 is master tip and 8e0de8d0 the branch fork point, a diff from 8996ca55 would show 453f6d73 minus 8996ca55 which could include backwards changes. The diff shows only the 4 expected files, which suggests 8996ca55 == 8e0de8d0 in terms of tree or that master hasn't moved. Hmm, actually the prompt says "base=8996ca55、implement=a377a25a、tip=453f6d73". The Task file (delivered at tip) says base_commit 8e0de8d0. Discrepancy worth flagging as a P4/P3: base metadata inconsistency — which is a recurring issue in this project (see TA3-B2 R14: "base 元数据一致性（521d0bdd vs 69137837）静态不可判定" → integrator decides). So I should flag: Task/handoff declare base_commit=8e0de8d0 while review input declares base=8996ca55; static review cannot determine which is the fork point; integrator to verify with git (and check no unrelated changes are included, though the diff shows only 4 files).

Let me check whether commit 8996ca55 exists in doc references (grep for 8996ca55 in repo). And 8e0de8d0. That may reveal master tip.

2. Check STATUS.md to see current active task / claim that M2-SFX-TRANSLATE-ENTRY is active and its base. Note禁改面 includes doc/STATUS.md.

3. Check whether `_sfx_policy_from_settings` handles a JSON settings section that is a list → ValueError ✓.

4. Check the sfx_policy schema CHECK constraint and whether writing 'translate' is allowed (schema.py:230). Verify in the repo.

5. Check the ports signature of region_creator type (ports/detection) — unchanged; verify that no type stub for region_creator mentions sfx_policy (no need).

6. Check the `SfxPolicy` import ordering/lint (imports alphabetical?). Not critical.

7. Check test file test_sfx_policy_settings.py's assembly fixture passes `font_catalog=object()` etc. — with `# type: ignore`; the actual signature likely has these as keyword-only. Fine.

8. One more: the e2e test asserts `regions["speech"]["text"]["machine_translation"] == MOCK_TRANSLATION_TEXT` — the backfilled speech region is region #1 (manga-1, reading_order 1) matching `_backfill_detected_regions` first-region semantics. ✓ Consistent with the disclosed adjacent finding.

9. Potential issue: in `_scenario`, `assemble_acceptance_core(tmp_path / "data", tmp_path / "managed")` is called twice; first core's conn closed, then rebuild. But the `_build` function ignores args? `def _build(): return assemble_acceptance_core(...)`. OK.

10. Check `assemble_acceptance_core` signature to ensure the e2e test's call matches (2 positional args) — read bootstrap/acceptance_bridge.py near assemble_acceptance_core.

Let me now check the schema CHECK, ports signature, acceptance_bridge assemble function, and STATUS + commit hashes.
dsh: reasoning:
STATUS confirms: main 三套件 509+1skipped; M2-SFX-TRANSLATE-ENTRY Owner 交付 @453f6d73, "21 新增测试、基线 530+1sk". Also confirms master tip after merges.

Now about the base: prompt says base=8996ca55. Let me grep STATUS or docs for 8996ca55 to identify. Not found in STATUS. Could be master tip at review time. The Task says base_commit 8e0de8d0. Hmm, the handoff says base `8e0de8d0` while "复现命令" etc. The review-input.diff header would have been created by the review-input generation with base 8996ca55. If diff = `git diff 8996ca55 453f6d73`, and the branch's fork point is 8e0de8d0, then the diff would include revert-like changes for any commits in 8996ca55 not in branch... but branch contains 8e0de8d0 which is presumably an ancestor of 8996ca55 (master). So `git diff 8996ca55 453f6d73` shows changes going from master tip to branch tip: files that master advanced (e.g., core_assembly.py changed by M2-IMPORT-ALLOC-LIMIT at f9c15e45?) would appear as diffs. The provided diff shows only 4 files, which means master (8996ca55) and branch content agree on all other files. But wait: it shows the new handoff file and Task modification and code+2 tests — exactly the branch's own changes. If master advanced core_assembly.py after 8e0de8d0, the diff would show those too (as reversals). It doesn't. So either master didn't touch core_assembly between 8e0de8d0 and 8996ca55, or base 8996ca55 is actually the merge-base-ish.

Hmm, but hold on: maybe the diff is `git diff 8e0de8d0 453f6d73` and the "base=8996ca55" in the prompt is wrong/mislabeled. I can check whether 8996ca55 appears anywhere. Let me grep whole doc for 8996ca5.

Actually, more decisive: check if master's core_assembly.py at G:\CODEX\New Manga differs from 8e0de8d0's version. Master here = the main repo working tree; might include merges up to f9c15e45 etc. If master's core_assembly has changes relative to the branch base that predate the branch, then diff-from-master would show them. Let me compare master core_assembly vs worktree core_assembly outside the changed hunks: e.g., check whether master has `_load_pipeline_defaults` same, and check the M2-IMPORT-ALLOC-LIMIT change (unlikely in core_assembly).

Simplest: grep master core_assembly for "sfx_policy_cfg" (should be absent) and check a couple of areas near line 879 in master vs worktree. If master differs elsewhere (e.g., allocation limit), the provided diff would have shown it... unless the diff was generated against 8e0de8d0 and simply mislabeled in the prompt.

I can do a rough comparison: read master core_assembly around 860-890 and compare with worktree. Let me also grep master for "_load_pipeline_defaults" line numbers to see whether master == branch base in structure.

Actually, a cheap decisive test: master's line count vs worktree's. Worktree has 1203 lines. If master has a different count in a way consistent with the +49 lines (+~45 for the function/comments + ~13 for closure and comment... let's see: diff net +49). If master == base, master should have 1203 - 49 = 1154 lines. Let me check master's line count by reading far offset (read tool tells total lines).

Let me read master core_assembly at offset 1150 to see total.
dsh: reasoning:
Master core_assembly has 1123 lines; worktree has 1203 → +80 lines total?? Wait, but the diff says +49 net for core_assembly.py. Hmm. Let me compute: worktree 1203, master 1123 → difference 80. But the diff only adds ~49 net (5+ ~49? let's count diff hunks: hunk1 import changes (+2 -1 = +1... actually -1 +2? "from collections.abc import Callable" → "Callable, Mapping" = +0 net lines; then +from typing import Any = +1; then imports RegionType block 7 lines replacing 1 = +6; then the new function block +49? and the closure +11). Total: let me count from diff:

1. `-from collections.abc import Callable` `+from collections.abc import Callable, Mapping` — net 0.
2. `+from typing import Any` — +1.
3. `-from domain... import BBox, RegionGeometry, RegionOrigin, RegionType` → `+from domain...import (BBox, RegionGeometry, RegionOrigin, RegionType, SfxPolicy,)` in 7 lines — net +6.
4. New function block: lines +166..+213 in diff = 48 lines added (the comment 4 lines, blank, constants 3, function ~30, blank lines). Say +48.
5. Assembly read: +13 lines.
6. Closure: `+region_type = _detected_region_type(provider_label)` +1, region_type=..., +10 lines for sfx_policy, and reordering. Net ~+11.
Total ≈ 1+6+48+13+11 = 79. So +79/80. The handoff's "+49 净行" claim is wrong! Let me count carefully with the diff line numbers.

Hunk 3 hunk header: `@@ -678,6 +685,55 @@` → old 6 lines, new 55 lines → +49 lines in that hunk. That hunk covers lines 162-214 in the diff file: the `_detected_region_type` context (3 lines context) + new function block. Hmm, the hunk header says +49 net for that hunk. But hunk 1 (+2/-1?) and hunk 2 (+1) and hunk 4 (+11)...

Hunk 1: `@@ -25,7 +25,7 @@` → same count (7→7): the `-from collections.abc import Callable` / `+from collections.abc import Callable, Mapping` inside a 7-line window = net 0.
Hunk 2: `@@ -34,6 +34,7 @@` → 6→7 = +1.
Hunk 3: `@@ -49,7 +50,13 @@` → 7→13 = +6.
Hunk 4: `@@ -678,6 +685,55 @@` → 6→55 = +49.
Hunk 5: `@@ -810,6 +866,19 @@` → 6→19 = +13.
Hunk 6: `@@ -959,10 +1028,21 @@` → 10→21 = +11.
Total net = 0+1+6+49+13+11 = +80. So the handoff's "+49 净行" is a misreading of the hunk header (+49 for hunk 4 only). Actual = +80 lines. That's a factual error in the Handoff/Task claim ("+49 净行") — minor but it's an evidence accuracy finding (P3). Let me double check master line count = 1123 and worktree 1203: +80 ✓ consistent. 

So Finding: handoff claims +49 净行 in core_assembly.py but actual net is +80 (diff hunk sums; master 1123 → worktree 1203 lines). Wait, but caution: master file (G:\CODEX\New Manga) is not necessarily identical to branch base 8e0de8d0. If master == base for this file (no matches for sfx_policy → base version), then 1123 vs 1203 confirms +80. Both the diff hunk arithmetic and the line counts agree on +80. Good, solid.

Hmm, but is master's version == base 8e0de8d0's version? The diff says base version of that hunk region equals what I read in master? Let me check master around the corresponding lines (the closure region ~ line 959 in base per hunk header `-959,10`). The diff header says old file line 959-968 for the closure hunk, and master has 1123 lines total. Worktree hunk new line 1028. Difference 1028-959 = 69 lines of inserted content before that point (1+6+49+13 = 69) ✓ consistent. And master's total 1123 + 80 = 1203 ✓. So master's file == base file for this file (at least in aggregate). Good — so master == base 8e0de8d0 for core_assembly.py basically. Then what's 8996ca55? Possibly master tip; the master working tree might be at 8996ca55. Either way, the diff content matches base 8e0de8d0 for these files, so the base label mismatch is likely just naming (review input base = master tip == merge base for these files). I'll flag it as low-severity metadata inconsistency to be resolved by integrator with git (P4), since I can't run git.

Hmm wait, actually if master == 8996ca55 and master's core_assembly == base's core_assembly, the diff generated from 8996ca55 would be identical for this file. So the discrepancy is benign metadata (branch fork point 8e0de8d0 vs review base 8996ca55). Since Task frontmatter base_commit=8e0de8d0 is the branch's declared base, and review-input uses 8996ca55 — the integrator should reconcile. In TA3-B2 there was a similar R14. I'll note as P4.

Now let me double check the "+49 净行" claim appears in both handoff and Task. Handoff line 44: "src/bootstrap/core_assembly.py（+`_sfx_policy_from_settings` 纯函数+装配读取+闭包传参，+49 净行）". Task line 119/121 mentions? Task 交付记录 AC3 doesn't mention +49; the handoff does. Also the prompt's "Owner 声称" says "+49 净行". OK → finding R?

Let me now verify the test file contents in the worktree match the diff (spot check for tampering) — count lines. New test files: test_sfx_policy_settings.py 242 lines (diff says +242), test_sfx_policy_end_to_end.py 309 lines. Let me check worktree sizes.

Also verify the number of tests: settings 9+6+4 = 19 ✓; e2e 2 ✓ = 21 ✓.

Let me also check for a subtle problem in the e2e test: `_run_region_command` for OCR_REGION on the SFX region: OCR requires a provider binding "ocr" which is saved. Fine.

Potential issue: `pytest.importorskip("PySide6")` at module import, but the handoff claims "2 Qt offscreen". If PySide6 is missing, both skipped — and then the "530+1skipped" count: 530 passed + 1 skipped. Hmm! If the e2e test module is skipped due to missing PySide6 (or any skip), the claimed total 530+1 skipped would mean the 2 e2e tests RAN (not skipped) under the T1.1.1-impl-py312 venv which has PySide6. So 21 new passed + 509 baseline = 530 ✓ and the 1 skipped is the pre-existing baseline skip. That's consistent: 530 = 509 + 21. But careful: the skipped count baseline "509+1skipped"; new total "530 passed + 1 skipped" — 509+21 = 530 ✓, skipped unchanged ✓. Consistent. Good. But note: the settings tests (19) are Qt-free, e2e (2) require PySide6; in the claimed run both executed. NOT_VERIFIED.

Also: does the diff's claim "既有测试零修改" hold? The diff shows no test modifications ✓ (statically verifiable from the diff).

Now let's check the tests dir in the worktree for the two new files and confirm no other new test files (that would break "only 2 new test files" claim) — diff is authoritative, but let me glob tests/core for sfx_policy files.

Also I should verify one thing in the new test: `test_default_assembly_creator_keeps_skip` asserts `sfx.sfx_policy is SfxPolicy.SKIP`. `_create_via_assembly` uses `core.editing.get_region(region_id)`; create_region returns region with SfxPolicy enum ✓.

Another check: `_seed_page` inserts books/chapters/pages with columns; must match schema (source_order etc.). If the INSERT column list mismatches the schema, the tests would fail — the Owner claims they pass. NOT_VERIFIED statically? I could verify the schema columns. Let me check the pages table schema quickly to see whether these columns exist with those exact names (a wrong column would make the test fail, contradicting claimed green — a good static cross-check).

Let me read schema.py pages table.
dsh: reasoning:
Columns exist (pages has chapter_id, source_filename, sort_order, width, height, created_at, updated_at presumably). Let me check lines 35-60 for the pages table definition to confirm columns `source_filename`, `width`, `height`, `created_at`, `updated_at`.

Actually the INSERT includes `source_filename` and `width`/`height`. Let me read schema 30-60.
dsh: reasoning:
pages columns source_filename/width/height are added by later ALTER migrations (lines 180-200 presumably). Fine — the INSERT lists all of them; un-migrated DB wouldn't have them, but open_database runs all migrations. ✓

Note the books table needs title/created_at/updated_at — check lines 30-38 (books). Likely fine.

Now let me check the test file in worktree matches diff (e.g., total lines 242 and 309). Let me read the worktree test files' last lines / total to confirm the diff = worktree content. I'll read offset 230 of settings test and offset 300 of e2e test.

Also, I want to verify one important semantic claim: "非 SFX 恒 SKIP" — but note `create_region` for non-SFX now receives `sfx_policy=SfxPolicy.SKIP` explicitly. Same as default. ✓

Another: is there any other place where an SFX region can be created by the production chain? `_create_detected_region` is the only one. ✓ (acceptance seeding is harness-only.)

Now, one more consideration for A (zero behavior change): the new assembly-time read calls `_load_pipeline_defaults(conn)` an extra time (line 879). `_load_pipeline_defaults` catches sqlite3.Error → returns empty. If the DB read fails, policy silently SKIP — consistent with tolerance. No behavior change. But: fail-fast philosophy vs tolerant read — if settings_json is corrupt JSON, `_mapping` returns {} → policy SKIP silently (no fail-fast). Is that a gap against "非法值装配期 ValueError"? A corrupt JSON settings blob is a malformed setting but the reader's documented tolerance is to treat it as empty. This is a real boundary: "存在但非法（... section 形状坏）⇒ ValueError" — but if the whole settings_json is not valid JSON, you cannot detect an illegal sfx.policy; treated as absent → SKIP. The Handoff's claim "非法值 fail-fast" covers only post-decode values; the pre-existing tolerant decode ("unconfigured (or corrupt) install decodes to all-empty") takes precedence. This is defensible (documented tolerance, no way to distinguish corrupt from configured-elsewhere), but worth a P3 finding: corrupt `settings_json` (or non-dict JSON) silently yields SKIP, i.e., the fail-fast matrix has a hole at the persistence-decoding layer; the docstring says "never a silent fallback" which is slightly overstated. Good finding — P3.

Similarly `{"sfx": {"policy": "translate"}}` where section is a dict works. But if settings_json is `{"sfx": "translate"}` → ValueError ✓.

Another potential hole: `{"sfx": {"policy": "translate "}}` ✓ normalized.

Another: `settings["sfx"]["policy"]` written via save_settings_section with e.g. int 7 → stored in JSON → read back as 7 → ValueError ✓.

Now let's consider "B fail-fast 覆盖完备性" — the matrix tests: bogus, "on", "", "   ", 7, "translate" (section shape). Missing from tests: `{"sfx": None}` (returns SKIP, matches matrix entry for section absent? Actually separate: `settings["sfx"] = None` → SKIP; tested in matrix as `{"sfx": {"policy": None}}`, but not section=None). Also missing: `{"sfx": []}` (non-Mapping non-None → ValueError) and bool/float/list policy values. Coverage is representative; I can list these as suggested additional cases (P4). Also `{"sfx": {"policy": "TRANSLATE"}}` tested ("  TRANSLATE "). Also, no test for extra keys preserved.

Also missing: an assertion that the normalization path uses `SfxPolicy(normalized)` — fine.

Now the "E2E 真实贯通 plan 门 + step 门" question: 
- plan 门 evidence: `_unit_decisions(retranslate)` reads `finished.tasks[*].units[*].decision/reason` — these come from the planner (`_decide_step` → `_sfx_gate_suppresses` → `decide_sfx_translation`). For translate: decision "run" → proves plan gate admitted. For manual: skip_policy/sfx_skip → proves plan gate suppressed.
- step 门 evidence: for translate, persisted MOCK_SFX_TRANSLATION_TEXT proves the execute-time gate (`execute_translate_step`) did not skip AND region_type passed through. For manual, step gate not exercised (plan gate already blocks). Also, is `sfx_skip`/`SKIP_POLICY` from the step-level path covered anywhere in the new tests? Not in e2e (manual test's decision is plan-level since units are created by planner). The knowledge/test_sfx_gate.py covers the pure function. So step-level consumption for manual isn't directly e2e-proven, but the handler path translates the plan decisions... Actually does the step-level gate produce a skipped record when called? Not critical.

Hmm, but there's a subtlety: does `finished.tasks[*].units[*].decision` reflect plan decisions or execution updates? For translate, `.value == "run"` suggests PlanDecision.RUN. Fine.

Now, is the claim "plan 门与 step 门两处消费点" e2e-proven? The translate test proves both consumed (plan allows run; step produces output). Good.

C. Also should check: does the e2e test actually prove `_sfx_gate_suppresses` for the configured translate region via the plan gate — yes decision run. But could it be "run" regardless of policy (e.g., if the gate were broken)? The manual case shows skip_policy for manual, so the gate has discriminating power ✓. And speech is not gated ✓ (assertions on speech translation).

Now think about whether the *speech* region being policy=skip and gated: `_SFX_GATED_STEPS` includes translate etc., but `_sfx_gate_suppresses` returns False for non-sfx (gate returns TRANSLATE) ✓.

D. Range discipline: diff files = doc/handoffs (new), doc/tasks (modified), src/bootstrap/core_assembly.py, 2 new tests. All within allowed面. Zero touches to ports/contracts/models/etc. — verified from diff content. But note the diff's completeness depends on base correctness (metadata issue). Also `models.py` claim: Task background says `domain/tasks/models.py:186` default; handoff says `models.py` defaults unchanged. Let me verify quickly there's a sfx_policy default in domain/tasks/models.py:186 (to see if the handoff's "models.py 默认值不动" is the right file — the region default is in domain/regions/entities.py:230). The Task background cites `domain/tasks/models.py:186` as the default. Let me check what's at that line — if it's not a sfx_policy default, that's a (pre-existing, not this Task's) doc inaccuracy. Let me grep domain/tasks/models.py for sfx_policy.

Also E: contract. Already analyzed.

Let me also double check there's no existing test asserting the *exact* number of calls/args of region creator that could break — no.

One more potential issue: `assembled` fixture in settings test builds assembly with `mock_local_providers=True` and monkeypatch `tmp_path`; both tests calling `assembled()` twice on same tmp_path — SQLite reuse fine.

Another potential: the fixture is named `assembled` and returns `_build` (a function), used as `assembled(mock_local_providers=True)` — the parameter shadows the fixture name... the test does `def test_default_assembly_creator_keeps_skip(assembled):` then `core = assembled(mock_local_providers=True)` ✓.

Now let me verify worktree test files match the diff (anti-tamper). Read the tail of each.
dsh: reasoning:
Worktree test files match diff line counts ✓.

Now check the region snapshot plumbing: `_sfx_gate_suppresses(region: RegionSnapshot)` — how does RegionSnapshot get sfx_policy? From the region row/revision. Since create_region persists sfx_policy, the snapshot carries it ✓. Let me verify RegionSnapshot has sfx_policy field sourced from DB.

grep RegionSnapshot sfx_policy.

Also check that `_backfill_detected_regions` (service.py:922) binds first region — already disclosed.

One more: is there a "region policy" propagation issue: the region snapshot used by the planner may come from the *current revision* (snapshot JSON), which includes sfx_policy (entities snapshot includes it: line 284 in entities dump). ✓

Let me verify RegionSnapshot.sfx_policy exists and the read path.

Also: potential issue with `_sfx_gate_suppresses` for region_type "sfx" and policy "translate" → gate returns translate → not suppressed → plan RUN ✓.

Let me grep for RegionSnapshot definition.
dsh: reasoning:
All plumbing verified: DB column → repo → RegionSnapshot → plan gate; builder → step gate.

Now, one thing to check: `_effective_sfx_policy` falls back to skip on blank. If policy value in DB were blank → skip. Fine.

Now, another thought on zero-behavior-change: `_load_pipeline_defaults(conn)["settings"]` is called at line 879, i.e. an extra SQL read at assembly for *every* install, including production. Cost negligible. But it also means: if the DB has corrupt settings_json, silently SKIP ✓ (as discussed). Also, does this extra read happen before `conn` is used for anything requiring write? No.

Another: does the assembly read happen before the pipeline_defaults service creation (line 1088/1114)? Yes; irrelevant.

Now, one more check on A: the claim "闭包仅对 SFX 候选传 create_region(sfx_policy=...)，非 SFX 恒 SKIP". Note it passes `sfx_policy=SKIP` explicitly for non-SFX rather than omitting. Equivalent. ✓

Now, consider whether `region_type is RegionType.SFX` — `_detected_region_type` returns `RegionType.SFX` enum member, so identity holds ✓.

Potential missed consumption point: is there any *other* place where machine-created regions get a policy, e.g. `RegionStepWriter` or detect handler creating regions for reused regions with an updated policy? Not relevant.

Another consideration for the review item 1: "配置泄漏到非 SFX 的可能性" — also consider the *planner/step* gate: a speech region with policy=translate? Gate returns TRANSLATE for non-sfx regardless of policy ✓ (gate.py:34-35). So even if a policy leaked to a speech region, the gate is permissive for non-sfx — no suppression risk, but rendering service: `rendering/service.py:540-556` `_manual_sfx_allowed(region_type, sfx_policy, allow_manual=...)` → returns allow_manual and policy is MANUAL — could a leaked MANUAL policy on a speech region change render behavior? Let's check line 372 context: `region.region_type.value, region.sfx_policy.value, allow_manual=allow_sfx`. If leak happened, a speech region with manual policy could be treated as manual SFX → potentially relaxed allow_manual. But since the closure hardcodes SKIP for non-SFX, no leak from this path. Other paths (user edit) not in scope. Good, and worth stating in the review that the leak guard matters because consumers like rendering aren't all type-keyed (rendering checks region_type too via `_render_action`?). Let me quickly read rendering/service.py 360-380 and 530-560 to describe the guard's importance accurately.

Let me read that.
dsh: reasoning:
Rendering also type-keyed via the shared rule ✓ — leakage to non-SFX would be tolerated by all consumers since the shared rule returns translate for non-sfx. So the leak guard is defense-in-depth, and consumers are type-safe anyway. Good insight to report.

Now, are there other consumers where a leaked MANUAL policy on a non-sfx region would change behavior? None found (all use the shared rule).

Now, remaining checks:
1. Handoff claim "gate.py:32 翻译门三值就绪" ✓ verified.
2. "消费点 step.py:176" ✓; "service.py:418 经 _sfx_gate_suppresses" ✓.
3. "editing/service.py:247 sfx_policy 参数已存在" — handoff says 247 (the def line is 247; parameter at 254) ✓ close enough.
4. "handlers.py:287" ✓.
5. "pipeline_defaults.py:105" ✓.
6. "core_assembly.py:441 _load_pipeline_defaults" — actual def at 448 in base/worktree; handoff says 441. Hmm: diff hunk header earlier showed `@@ -25,7 +25,7 @@` etc. Handoff line 24 says "装配侧 `_load_pipeline_defaults(conn)`（`bootstrap/core_assembly.py:441`）". In the worktree (post-change) it's at 448; in base (master) let me check: master's version. Earlier I read worktree line 448. Base line = 448 - (insertions before line 448): the imports added 7 lines (1 + 6) before it and... the new function is AFTER _load_pipeline_defaults (line 697), so base line = 448 - 7 = 441 ✓. So the handoff cites base-file line numbers consistently (441 for _load_pipeline_defaults, editing/service.py:247, gate.py:32, step.py:176, service.py:418). And core_assembly closure/assembly lines cited "detect handler handlers.py:287" ✓ base. OK good.

7. Task AC4 — contracts 判定.

Now let me double check the "+49 净行" and other numeric claims. Actual net +80 lines. Handoff claims "+49 净行" — error. Also the handoff's "本 handoff commit" and the Task frontmatter delivery_head note.

Another numeric check: "test_sfx_policy_settings.py 19 条 Qt-free" — 9+6+4 = 19 ✓. "test_sfx_policy_end_to_end.py 2 条" ✓. "新增 21 条" ✓.

"三套件 530+1skipped = 509+1+21" — 509+21=530 ✓ consistent arithmetic.

"m2_acceptance 35 条" — plausible; NOT_VERIFIED.

Now: does the new assembly read change behavior for the *acceptance bridge* fixture path? No.

Another angle: does `_sfx_policy_from_settings` get called for every assembly, including tests that write weird settings? E.g., existing tests that save settings section "sfx"? None (new key). But: are there existing tests that write arbitrary settings into pipeline_defaults settings_json (e.g., `{"sfx": ...}`)? Unlikely. The claim "既有测试零修改且全绿" implies no collision. Fine.

Potential regression risk for production: any existing install with a settings key "sfx" of unexpected shape (e.g., written by a future/existing UI)? Only "providers" and "ocr" sections are written by the Legacy VM. So low risk. But note: if a user/profile previously stored `{"sfx": "on"}` (env-style) — impossible. OK.

Now let's consider whether the fail-fast placement is inside the same `try` that closes conn on exception. Let me check the outer try/except structure to report accurately (resource handling). Grep for "except" and "conn.close()" near the end of assemble_core_services.
dsh: reasoning:
Line 1201-1202: `except Exception: conn.close(); raise` — so the ValueError from fail-fast closes the connection ✓. Good, no resource leak.

Let me confirm lines 1190-1203 to be precise about what's in the try (does the try wrap from line 779? yes presumably).

Also I want to check whether the assembly's ValueError happens *after* migrations run and possibly after the DB was created — "fail-fast" creates/migrates DB then fails; acceptable (env gates same position). Note: an invalid setting makes the app fail to start entirely (assembly) — that's the intended fail-fast per AC2. Also: the test `test_settings_policy_illegal_fails_the_assembly` writes bogus then re-assembles → ValueError. Note the write path itself (`save_settings_section`) accepts "bogus" (no validation) — i.e., the invalid value is persisted first and only rejected at next assembly. So a user writing an invalid value via IPC gets a successful save, then the app fails to start on next assembly. Is that ideal? AC says "非法值 fail-fast（沿用 SFX conf 阈值 env 校验先例）" — assembly-time fail-fast is what's asked. But it creates a "brick" until the row is fixed externally (no UI to fix). Worth noting P3: validation is only at read time; the writer (`save_settings_section`, and any IPC SaveSettings) accepts arbitrary values, so an invalid value persists and blocks startup — the user cannot fix it through the app (unless the settings UI can load... the app may still open the settings? No: assembly fails → app can't start at all → no UI to clear the key). Compare with env-gate precedent: env is fixed out-of-band too. But for a *persisted* key, bricking the app with no in-app recovery is a more serious failure mode. That's a good substantive finding: recommend validating at write time too (or documenting the recovery path), though the Task's AC explicitly says assembly fail-fast. Severity: P2? The Task explicitly required assembly-period fail-fast and forbade touching other files? Allowed面 includes src minimal面 (settings channel) — validating in `save_settings_section` would be a broader面 change (application/settings), out of the declared minimal面. Since AC2 mandated assembly fail-fast, I'd rate P3 (design risk + recovery gap), with a recommendation to register a recovery path / write-time validation as follow-up. Hmm, but is it really unrecoverable? The user could delete/edit the row via developer path; the app is bricked until then. In production, that's a real support burden. Let me check whether the app catches assembly exceptions gracefully (e.g., app shows error UI). Let me grep where assemble_core_services is called in the app entry (apps/ or src/ui) to see if failure is caught and the app still starts in a degraded mode. If it's caught and shows an error, still bricked for settings edits.

Let me check callers of assemble_core_services.
dsh: reasoning:
Let me look at src/bootstrap/app.py:164 to see if assembly failure is handled (app startup error). Quick read around 150-185.

Also check tests using assemble with temp DB — any of them writes settings sections that could collide? Not needed.

Let me read app.py 150-180.
dsh: reasoning:
So the ValueError propagates to the app startup and the app fails to launch. Confirmed "brick" failure mode. I'll report as P3 with concrete consequence + recovery path suggestion (write-time validation or documented row fix), noting AC2 explicitly requested assembly fail-fast so it's a design consequence rather than a spec violation.

Now let me think about whether there's any P0/P1/P2 finding at all.

Candidate P2s:
(a) Effective scope gap: policy applies only at region creation; existing SFX regions (the TA3-B2 corpus = 8 BJ06 + 1 K11 regions, already persisted) keep SKIP forever unless regions are re-created; detect reuses live regions (handlers.py:258-269), so re-running the pipeline does NOT apply the new policy to already-detected pages. The declared goal ("解除 SFX 翻译评测 n=0 的前置阻断") is only met for newly created regions / fresh runs. No retro-apply and no per-region policy update entry (apply_sfx_policy has no caller). Impact: the SFX evaluation would need to re-detect after deleting regions or re-run from a fresh data root. This is a genuine semantic limitation that the Handoff didn't state (it says "translate 路径生产可达但需用户显式配置" and "settings 改后下一次 assemble 生效" which is misleading: assemble re-reads, but existing regions don't change). Also the e2e test uses a fresh DB and never exercises the "already detected page" case, so the claim "配置后 SFX region 进入翻译" holds only for new regions.

Is it P2 (needs fix or explicit disclosure) or P3? Given the Task's stated purpose is to unblock evaluation, and the eval can be re-run with a fresh data root or by deleting regions (a data-manipulation step not yet documented), I'd call it P2 — "must be disclosed in Handoff/Task (and ideally verified by a test or an integration note)". Because the reviewer must judge whether the AC is met: AC1/AC2 are met literally. The gap is in the operational claim. Severity P2 as "changes_requested-level disclosure requirement"? Hmm. The output format wants findings with P0-P4. I'd mark R1 = P2 (semantics: config only affects newly created regions; re-assemble does not retro-apply; detect reuses live regions; no per-region policy update path) with recommendation: either document the required re-creation/re-detect procedure in the Task/Handoff, or add a regression test pinning the "existing region keeps old policy" behavior so it's an explicit decision. Note that the existing behavior *is* intentional per AC ("region 创建"). Strictly, AC2 says "detect 装配把策略传到 region 创建/翻译门消费点" — so this is within spec. I'll rate it P2 for the operational disclosure but state clearly it's not an AC violation. Actually maybe P3 is more defensible since it's not a defect but a scope/disclosure gap... The consequence is significant for the stated goal (n=0 unblocking) though. Let me call it P2 with an explicit "not an AC violation; disclosure/decision needed" and note the cheap mitigation (Handoff wording + one test).

Hmm, but a P2 typically means "must fix before integration". Given the user asked for precision-first and honest registration, a wording fix in the Handoff/Task (which is within allowed面) is a legitimate integration condition. I'll mark P2 and phrase the fix as disclosure + optional pinning test.

(b) The handoff's "+49 净行" is wrong (+80). P3 (evidence accuracy).

(c) Corrupt settings_json silently → SKIP, contradicting "never a silent fallback". P3.

(d) Assembly fail-fast with persisted key = app bricked until the row is fixed out-of-band; writer accepts any value (no paired validation). P3.

(e) Base metadata inconsistency 8996ca55 vs 8e0de8d0. P4 (integrator to reconcile).

(f) Test coverage: manual e2e proves plan-level suppression only; step-level `decide_sfx_translation` manual path covered by tests/knowledge/test_sfx_gate.py:37 ✓ (existing) — so no gap. I'd note it's acceptable. Maybe P4 observation: the e2e manual case cannot distinguish plan-gate vs step-gate suppression (no assertion on execute path); but since plan blocks, fine.

(g) settings test matrix missing cases: `{"sfx": None}`, `{"sfx": []}`, bool policy, list policy. P4.

(h) `_sfx_policy_from_settings` assumes `settings` is a Mapping (AttributeError on None) — unreachable today; P4 note.

(i) Duplicated settings read (line 839 `_load_pipeline_settings`, line 879 `_load_pipeline_defaults`) — two decoders for one row; both tolerant and equivalent; P4 (could reuse `_load_pipeline_settings(conn)` which returns just the settings dict). Actually using `_load_pipeline_settings(conn)` would have been simpler (1 line, no dict indexing) and is the exact decoder `build_provider_runtime` uses at line 838 — better symmetry ("same channel" claim). This is a legit simplification finding (P4/P3). The handoff claims "与 ocr.script 同通道" — ocr.script is consumed through `_load_pipeline_settings`; the new key uses `_load_pipeline_defaults(...)["settings"]`. Same row, equivalent decode; but for consistency using `_load_pipeline_settings` would be more literally "同通道". I'll list as P4 consistency/simplification.

Also: is `Mapping` from collections.abc used elsewhere in the file? Fine.

(j) `_SFX_POLICY_VALUES` module-level tuple computed from enum, and error message ordering "skip|translate|manual" ✓.

(k) One more: `_sfx_policy_from_settings` returns `SfxPolicy(normalized)` — for value 'skip' returns SKIP ✓.

(l) Consider `SECTION` naming: key is "sfx"+"policy". Is there a risk of collision with an existing settings section "sfx" written by provider runtime/profile system? Let me check whether provider runtime treats top-level settings sections as provider profiles: build_provider_runtime(settings=...). Let me check how it consumes `settings` — if it iterates over keys as step→binding, a new top-level "sfx" key might be interpreted as a step config. Let me read runtime.py around 639 to verify it doesn't choke on unknown sections (the existing "ocr" and "providers" sections already ride there, so unknown/handled sections are fine — but "sfx" is a *new* section name that might accidentally match a step or profile name). Let me check quickly.
dsh: reasoning:
`_provider_settings(settings, provider_id)` reads settings by provider id key. Adding a top-level "sfx" key: does any provider id equal "sfx"? Provider ids are like PROVIDER_SAKURA, PROVIDER_MANGA_OCR, etc. Let me check `_provider_settings` and whether any provider id is "sfx" (e.g., "chiqui7" SFX provider id). Let me grep for provider ids containing "sfx".

If a provider id were "sfx", the new settings section would be interpreted as that provider's profile config (name/type keys) — could cause unexpected behavior (e.g., registering a provider profile named type/…). Let's check.
dsh: reasoning:
No provider with id "sfx". Let me check detection_sfx provider_id to be safe: grep "provider_id" in detection_sfx.py.

Actually, `_provider_settings(settings, provider_id)` reads `settings[provider_id]`; provider ids are like "vision-detection"/"chiqui7-sfx"? Let me check detection_sfx provider_id value.
dsh: reasoning:
Provider profiles are nested under `settings["providers"]["profiles"]`, so a top-level `settings["sfx"]` key is inert to the provider runtime. ✓ No collision. Good — I can state that positively in the review (verified no collision with the provider-profile namespace).

Now, let me double check the `RoutePolicy.from_settings(settings, ...)` and `_retry_policy(settings)` — do they read arbitrary top-level keys? `_retry_policy(settings)` might read settings["retry"] etc. Let me quickly check `_retry_policy` and RoutePolicy.from_settings key names to ensure "sfx" is not used. grep for `settings.get(` in runtime.py to list top-level keys consumed.
dsh: reasoning:
Top-level keys consumed by the runtime: "providers", "network". "sfx" is inert ✓. Also `settings["ocr"]["script"]` — who consumes it? Perhaps the OCR provider reads `settings["ocr"]["script"]`? Let me check quickly: grep for `"ocr"` in runtime/providers. Not strictly needed, but the "same channel as ocr.script" claim implies something consumes it. From TA3-B2 F6: "ko case 必须写生产 settings `ocr.script=korean`（生产默认 japanese，paddleocr-korean slot 会 typed 拒绝）" — so the OCR provider reads it. Let me verify to be thorough — grep `\["ocr"\]` in src.

Let me do that plus check `_GLOBAL_NETWORK_SECTION` value (just to be sure it's not "sfx").
dsh: reasoning:
No consumer of `settings["ocr"]["script"]` in src today? Let me check the OCR provider for script settings: grep "script" in src/infrastructure/providers.
dsh: reasoning:
handlers.py:329: `script=str(settings.get("script", SCRIPT_JAPANESE))` — this reads the *step-level* settings (run's frozen step settings snapshot), presumably seeded from `settings["ocr"]`? Let me check how the OCR handler gets `settings` — probably `run.settings_snapshot` or the per-step settings keyed by step type. Let me read handlers.py around 310-340 to see the context of that `settings`.

This matters for the claim "settings["ocr"]["script"] 同通道" — the mechanism: pipeline_defaults `settings_json` → `PipelineDefaults(settings=...)` → run's settings_snapshot → handler reads per-step section? Let's check tasks/service.py to see how settings_snapshot is built from pipeline_defaults settings (maybe keyed by step type: settings["ocr"] for the ocr step). If so, then a top-level "sfx" section might similarly be projected to the "sfx" *step*... but "sfx" is not a step type. Hmm, if run settings_snapshot is built as the whole settings mapping, then handler `settings.get("script")` would need settings["ocr"] to be merged... Let me look.
dsh: reasoning:
`self._section(run.settings_snapshot, "ocr")` → run.settings_snapshot["ocr"]["script"]. And run.settings_snapshot is frozen from the pipeline defaults settings (SnapshotProvider.freeze at assembly, line 1114 `load=lambda: PipelineDefaults(**_load_pipeline_defaults(conn))`). So `settings["ocr"]["script"]` is a top-level section in the SAME settings mapping, consumed via a section accessor. So the new `settings["sfx"]["policy"]` is indeed "the same channel" (same row, same top-level-section convention), except consumed at assembly rather than in a step handler. ✓ Claim verified.

Note also `_section(run.settings_snapshot, "ocr")` — interesting: the run settings snapshot freezes the *whole* settings mapping, so a run created after configuring sfx would carry `{"sfx": {"policy": ...}}` in its snapshot; harmless.

Note: run.settings_snapshot is frozen at run creation (from the persisted row at that time). Since policy is read at assembly from the DB row (not from the run snapshot), a run created before the config change but executed after re-assembly... irrelevant.

Potential subtle issue: assembly reads the policy from the DB at assembly time; the region creation uses `sfx_policy_cfg` captured in the closure. If settings change while the app runs (another process writes), no effect until restart ✓ documented.

Now let me consider `_section` in handlers: is there a validation whitelist of sections? Probably not.

I think I have enough. Let me also verify the diff's claim of "porcelain 干净" → NOT_VERIFIED (no shell).

One more reviewer duty: check the Task's allowed面 says "src/（detect/translate 装配+settings 读取的最小面…）" — the change is in core_assembly.py ✓ within src.

Also check the Task frontmatter `status: in_review` — diff shows ready→in_review ✓. Note: Task's "交付记录" section added ✓, and AC4 documented ✓.

Now, one more static check on the new code: `_sfx_policy_from_settings` is placed at module level between `_detected_region_type` and `default_data_root` ✓, and the constants `_SFX_SETTINGS_SECTION`, `_SFX_POLICY_KEY`, `_SFX_POLICY_VALUES` are module-level. `_SFX_POLICY_VALUES` order = enum definition order (skip, translate, manual) ✓.

Style/lint: `from typing import Any` — the file now imports Any; does the file otherwise use `typing` things (e.g., `object`)? Fine. `Mapping` from collections.abc for isinstance: correct runtime-checkable ABC ✓.

Any mypy concern: `settings.get(...)` on Mapping[str, Any] returns Any ✓.

`isinstance(section, Mapping)` — for a dict ✓.

Type annotation of `_sfx_policy_from_settings(settings: Mapping[str, Any]) -> SfxPolicy` ✓; call site passes `_load_pipeline_defaults(conn)["settings"]` typed `dict` (untyped function returns dict) ✓.

Now consider the error message uses `type(section).__name__` — fine.

One more possible issue: the fail-fast message for an illegal *value* uses `raw!r` which could include newlines → log injection? Trivial, P4 at most. Not worth listing. Actually a settings value from IPC could contain arbitrary text; the exception message echoes it into stderr. Minor. Skip.

Let me also double check: does `_load_pipeline_defaults` get called with `conn` before the schema check/migrations? Line 879 is after line 778 `open_database` (which migrates) ✓.

Another item for NOT_VERIFIED: pytest counts, red→green evidence (the red state wasn't archived; the Handoff admits "红态未入库，红→绿由 commit body 叙述"). That's an evidence weakness: AC3 says "先红后绿" but the red evidence is only narrative (no archived log). Compare with project precedent (M2-IMPORT-ALLOC-LIMIT archived 红态). I should flag as P3: 红态未归档，仅 commit body 叙述；AC3 允许? Task AC3 says "先红后绿——默认 SKIP 零变化…". The precedent M2-IMPORT-ALLOC-LIMIT archived "红态归档". So flag as P3 (evidence completeness) — reviewer cannot verify red; integrator could re-derive red by checking out base and running the new tests (they'd fail since selectors missing) — that's a cheap verification for the integrator. Good NOT_VERIFIED item.

Let me check the commit body claim: I can't read git log (no shell). The handoff says commit body carries red→green narrative. Task AC3 [x] describes red state. Since not archived → NOT_VERIFIED, with suggested integrator command: `git show a377a25a` commit body + run new tests at base to confirm red.

Now, the "+49 净行" error: also check the Task's own "交付记录" doesn't repeat it — line 119 says "新增 21 条全 PASS"; no +49. So the error is in the Handoff line 44 and possibly prompt's restatement. I'll report it as a Handoff-line-44 accuracy finding.

Wait, let me re-read handoff line 44 text: "`src/bootstrap/core_assembly.py`（+`_sfx_policy_from_settings` 纯函数+装配读取+闭包传参，+49 净行）". Yes. Actual +80 (or 79-80). Let me be precise: diff hunk sums = +80. Let me recount hunk 3 to be sure the new function block is 49 added lines:
diff lines 162-214 correspond to hunk `@@ -678,6 +685,55 @@`: old 6 → new 55 = +49. Inside: context lines 162-164 (`)` and blank... let me see: 
- line 162 `     )` context
- 163 ` ` context (blank)
- 164 (blank context)
Wait the hunk shows:
```
@@ -678,6 +685,55 @@ def _detected_region_type(provider_label: str) -> RegionType:
     )
 
 
+#: M2-SFX...
...
+
+
 def default_data_root() -> Path:
     root = os.environ.get("NEWMANGA_DATA_ROOT")
     if root:
```
Old: 6 lines = `    )`, blank, blank, `def default_data_root...`, `    root = ...`, `    if root:` = 6 ✓
New: 55 lines = same 6 + 49 added ✓. The added = 3 comment lines + 3 constants + blank + function (30 lines) + 2 blanks = ~41... let me count the added lines in the diff (lines starting with + between 166 and 214): 166-172 (7 lines: comment block), 173 blank?? Let me count from the diff text: 

+166 `+#: M2-SFX-TRANSLATE-ENTRY: the persisted...`
+167 `+#: assembly-level...`
+168 `+#: row and ...`
+169 `+#: ``ocr.script`` key rides...`
+170 `+_SFX_SETTINGS_SECTION = "sfx"`
+171 `+_SFX_POLICY_KEY = "policy"`
+172 `+_SFX_POLICY_VALUES = tuple(...)`
+173 `+` (blank)
+174 `+` (blank)
+175-188: def + docstring (14 lines: def, docstring 13)
...
+212 `+    return SfxPolicy(normalized)`
+213 `+` blank
+214 `+` blank
So added ≈ 49 ✓ (166→214 = 49 lines all "+"). Yes, +49 in that hunk.

Total = 0 + 1 + 6 + 49 + 13 + 11 = 80. And file length delta 1123 → 1203 = 80 ✓. So the handoff's "+49 净行" is the hunk-4 number, not the file's net. Confirmed error. P3 (or P4?). It's an evidence-accuracy error in the Handoff; the project treats such numbers as auditable. I'd say P3.

Hmm, wait. Is master (G:\CODEX\New Manga) == base 8e0de8d0? Let me verify by checking that master's file at base line 678 area is what the diff expects. The hunk header says base line 678 has `def _detected_region_type(provider_label: str) -> RegionType:` with context. In master, `_detected_region_type` is at line 670 (I read it: line 670 def, ends 685). The hunk header `@@ -678,6 +685,55 @@` means base lines 678-683 and new lines 685-739. Base 678 ≈ `    )` (line 676-679 in master: 670 def, 671-680 docstring, 681-685 return statement). In master, line 681 `return (`, 682-684 `RegionType.SFX if...`, 685 `)`. So base 678 is inside the docstring, not `    )`. Hmm! Master line 685 = `    )`. The hunk's first context line is `    )` → base line 678 should be `    )`. But in master, `    )` is line 685. That's a 7-line offset — exactly the 7 lines added by hunk 2 (imports) and hunk 1... no wait, base vs master: if master == base, and the diff's old-line numbers are base line numbers, then base line 678 = `    )`. But master line 685 = `    )`. So master ≠ base: master is 7 lines longer before this point? But master has 1123 lines and base has... base total = 1203 - 80 = 1123. Same total but different line offsets? That can't be if the diff is complete.

Hmm, let me recompute. The diff hunk header `@@ -678,6 +685,55 @@` — the hunk starts at old line 678, new line 685. The new offset 685 - 678 = 7 = lines added before this hunk (1 + 6 = 7) ✓ consistent. So old line 678 (base) = new line 685 (worktree) = `    )`.

I read the worktree file: line 685 = `    )`? Let me check my earlier read of worktree offsets 640-779: line 685 was `    )`. Yes! In the worktree read, line 685 shows `    )` (I see "685:     )" — the read output showed line 685 as `    )`). ✓

And master line 685 also = `    )` (from the earlier master read: 681 `return (`, ..., 685 `    )`). Wait, in my master read of `_detected_region_type` (from the worktree read actually — no, that was the worktree read at offset 640). Let me recheck: the first read was the WORKTREE file (G:/CODEX/New Manga.worktrees/.../core_assembly.py), lines 640-779, showing 670 def, 685 `)`. The master read — I only grepped master (no matches for sfx_policy) and read master offset 1145 (out of range, 1123 lines). I never read master's `_detected_region_type` region.

So: worktree line 685 = `    )` ✓ matches new-side numbering (685). Master's total = 1123 = base total (1203-80). Master's `_detected_region_type` presumably at 670-685? If base line 678 = `    )`, then base's def is at ~663 and master's at ~663 too (master == base). But in the worktree, def is at 670 and `)` at 685, i.e., new numbering. So base's def would be at 663. Does master have it at 663? I inferred 670 from the worktree read, not master. Let me verify master's line for `def _detected_region_type` — grep with line number.

This is a sanity check on whether master == base (to make the total-lines comparison valid).
dsh: reasoning:
Master: `def _detected_region_type` at 663 (base) → new 670 ✓ (+7). `def default_data_root` at 681 (base) → the diff hunk 4 new side: the new file's `def default_data_root` = 681 + 7 (earlier inserts) + 49 (hunk 4) = 737 ✓ matches worktree line 737. 

So master == base for this file ✓, and the net delta is +80 lines, not +49. Master total 1123 + 80 = 1203 ✓✓. Solid finding.

Now, is master's 1123 the same as 8e0de8d0? Given the diff's old-side line numbers match master exactly at three points (663→ diff old 678 hunk start is 15 lines later... let me verify: diff old line 678 = `    )`; master base: def at 663, docstring 664-673, `return (` 674, `RegionType.SFX` 675-677, `)` 678 ✓ — yes! master line 678 = `    )`. Consistent: master == base 8e0de8d0 for this file. 

So base 8e0de8d0 and master agree here; the review-input's "base=8996ca55" is a different commit label (probably master tip at review time) whose core_assembly content equals base's (since the diff shows no other changes). Fine → P4 metadata note.

Now let me think about whether there's any P0/P1. I don't see a correctness defect in the shipped code:
- default SKIP zero change ✓ (verified by code path).
- fail-fast works ✓ (verified logic).
- leak guard ✓.
- ranges ✓.

So verdict: approved_with_conditions (or "approved" with P2/P3 findings?). The task asked for Verdict section. Given findings include a P2 (operational semantics/disclosure) and P3s, an appropriate verdict is "changes_requested"? Hmm. Let's judge: Is the P2 a real defect requiring a code change? AC1/AC2 are satisfied literally. The gap is documentation/decision-level. In this project's precedent, verdicts used: approved / approved_with_conditions / changes_requested. Since the finding requires the Owner to amend Handoff/Task wording (and possibly add a pinning test), and everything else is fine, I'd say "approved_with_conditions" with conditions R1 (disclose retro-apply semantics + decide/pin) and R2 (+49 → +80 correction) — both doc-level, low-risk. If the reviewer thinks the semantics gap is important enough to require a decision by the integrator/user, "approved_with_conditions" is the right call.

Hmm, but let me reconsider the severity of R1. Which is it: does the goal "解除 SFX 翻译评测 n=0 的前置阻断" actually work for the evaluation path? The TA3-B2 runner uses production assembly + real detect. If the user re-runs the qualification with `sfx.policy=translate`, will SFX regions get policy=translate? The runner creates a *fresh* data root per case (probably), so detect creates regions → policy applied ✓. So for re-running evaluation, it works. The gap only affects pre-existing libraries/regions. Also TA3-B2's runner: is the data root fresh per run? Likely yes (case dirs). Then the stated goal is met. So R1's severity drops to P3-ish. But the semantics is still worth surfacing: for an existing library already detected, config has no effect; the user must delete/re-detect regions (or start fresh). And the Handoff's phrasing "settings 改后下一次 assemble 生效" could mislead a user into expecting existing pages to change. I'll keep it as P2? Given the review's value is in surfacing this for the integrator's/user's decision, and per the prompt item 1 focus ("是否真的零行为变化"), I'll list it as R1 P2 with the note "非 AC 违约；需在 Handoff/Task 明确 + 由集成方裁决是否为后续 Task（region 级策略更新入口）". Hmm, to be careful and defensible in a precision-first project: a P2 finding should block integration until addressed. The address = 2 sentences in the Handoff + optionally a pinning test. That's reasonable as an integration condition. OK: R1 = P2.

Actually let me reconsider one more time whether the retro-apply gap is even true: is there any place that updates the policy of existing regions when settings change? Grep showed `apply_sfx_policy` in entities with no callers in src (the grep for `apply_sfx_policy` in src returned only entities.py:247). So no application service exposes it — confirmed: no per-region policy update path exists anywhere (no IPC, no UI, no service). That strengthens R1: today, an SFX region created with SKIP can never be switched to translate through the product; only re-creation (delete region + re-detect, or fresh import) applies the configured policy. Also for a *pre-existing* SFX region that is region-locked? irrelevant.

Hmm, and also: does `delete_region` + re-detect work? detect handler reuses "live" (non-deleted) regions; after soft-deleting all regions the page has none live → detect re-creates with the configured policy ✓. So the recovery path is: delete the page's regions, then run TRANSLATE_ALL/detect again. Is there a UI path for deleting a region? Legacy workbench VM had region ops; new React architecture maybe. Worth suggesting the Handoff document this procedure explicitly. Good, that's actionable.

Let me quickly verify `_live_regions` includes deleted filter — yes handlers.py:258-262 filters `not region.deleted` ✓.

Now also double check: after re-creating regions, the OCR/translation stages for the page: since regions changed, the run resumes... fine, out of scope.

One more possible finding regarding "默认 SKIP 零变化": the new extra `_load_pipeline_defaults(conn)` call at assembly happens *before* the mock branch; in a *fresh* DB where the pipeline_defaults row doesn't exist yet, returns {} → SKIP ✓. In an existing DB with a row written by a *newer* schema? fine.

What about the interaction with `open_database`'s "refuses to run against a database written by a newer schema" (AC-DB-005)? Not affected.

Another possible issue: assembly failure due to an illegal persisted value could be triggered by a *settings write* the user can't undo — already covered as R4 (brick). I'll merge the brick concern into R4 (P3) with the write-time validation suggestion and note that AC2 mandated assembly fail-fast (so a fix = add write-side validation in a follow-up Task; or document recovery).

Hmm, but wait: would write-time validation be "better"? The project precedent for env gates is fail-fast at assembly. For a persisted key, the UI write path (`save_settings_section`) is generic and used by other sections; adding sfx-specific validation there would couple application/settings to a specific key semantics — arguably worse. A cleaner fix: the IPC/UI layer (future) validates. So R4 is best phrased as: "fail-fast 位置合理但对持久化键存在不可在应用内恢复的启动阻断；建议在 Handoff/契约登记恢复路径（删除/修正 pipeline_defaults.settings_json 的 sfx.policy），并在未来 UI 写入面做前置校验。" P3.

Now, let me also double check the fail-fast "mock 分支外" claim: the read is before `if mock_local_providers:` ✓ but note it's inside the outer `try` after `open_database` and inside the same block as env gates ✓.

One more coverage item for B: is the assembly fail-fast test proving that the error happens *before* the mock detector registration etc.? It asserts ValueError raised — sufficient.

Also: is there a test proving that the ValueError message for the *non-string* case and the *section-shape* case mention "sfx.policy"? The parametrized illegal test uses `pytest.raises(ValueError, match="sfx.policy")` for all 6 cases ✓ including section shape ("translate"). Note: the section-shape message is "invalid settings sfx.policy: settings['sfx'] must be a mapping..." ✓ contains it.

Alright. Also, the `match="sfx.policy"` regex: '.' matches any char, so it wouldn't catch a typo like "sfxXpolicy" — nitpick P4? I'd skip or mention in a single line. Maybe mention as a P4 test-hygiene nit (use re.escape or `match=r"sfx\.policy"`). It's a legit tiny review note. I'll include it in the test-quality section as a P4.

Now, let me think about whether "既有测试零修改" and "530" are verifiable statically: the diff shows no test file modifications ✓ (only additions). The count 509 baseline is from STATUS ("main 三套件 509+1skipped 0 failed" ✓ consistent with STATUS line 14). Good — so 530+1 = 509+21 ✓ internally consistent.

Wait, one nuance: STATUS says "main 三套件 509+1skipped 0 failed". The handoff says the baseline 509 + 21 new = 530. ✓.

Now, are there tests that could break due to the extra assembly-time DB read? E.g., tests that mock `sqlite3.Connection` or `_load_pipeline_defaults`? Let me grep tests for `_load_pipeline_defaults` / monkeypatching it. If some test monkeypatches assembly internals with a fake conn lacking `execute`, the new call could break them. Let me check.
dsh: reasoning:
No test writes a conflicting "sfx" section, and no test monkeypatches the reader. Existing tests use real DBs. The extra read is harmless to them ✓ (supports "no existing test changes needed").

Let me also check `tests/core/test_sfx_assembly.py` (the precedent referenced) to see how it drives the closure and whether the new explicit `sfx_policy=` kwarg could break an existing test that asserts call args or a region default. E.g., a test asserting `create_region` called without sfx_policy (mock/spy)? Let me grep tests for "sfx_policy" in tests.
dsh: reasoning:
Relevant existing tests:
- tests/core/test_sfx_assembly.py:219 asserts sfx.sfx_policy.value == "skip" via the real assembly (default) — should still pass ✓ (default SKIP).
- tests/providers/test_detect_handler.py:349 asserts regions[1].sfx_policy.value == "skip" — detect handler path ✓ unchanged.
- tests/rendering/test_rerender.py:572 asserts a region created via... probably a direct create_region; fine.

Let me check tests/core/test_sfx_assembly.py around 200-230 to see how it creates regions (maybe via the closure) — if it does, the new explicit kwarg doesn't change SKIP ✓.

I'm fairly confident. Let me spot-check test_sfx_assembly.py:190-225 to see if it's the real assembly closure and whether an unconfigured settings row yields SKIP (already implied).

I think I have enough evidence. Let me also verify the "R9 seam" helper duplication claim: test_core_detect.py has the same `_detect_deps` closure unwrapping (the Handoff says tests/core/test_core_detect.py established it). Already seen in the diff docstring. Not important.

Now let me count the findings and structure the output.

Findings list:
- R1 (P2): 配置只对"此后新建"的 region 生效；既有 region 不回溯。Evidence: core_assembly.py:1032-1048 (policy passed only at create_region), handlers.py:258-269 (detect reuses live regions, so re-running detect does NOT re-create → 已检出页面的 SFX region 永远保持 SKIP), no application path updates an existing region's policy (entities.py:247 `apply_sfx_policy` 无调用者; IPC/UI 无入口). Impact: 手稿库/TA3-B2 已落库的 8+1 SFX region 不会因配置 translate 而改变；Handoff §方案落点 "settings 改后下一次 assemble 生效" 会被误读为对既有 region 生效。Fix: Handoff/Task 明确"仅新建 region 生效；既有 region 需删除后重新 detect（detect 复用 live region，见 handlers.py:258）或使用全新 data root"；可选补 1 条 pinning test（预置 SKIP region + 配置 translate + 再跑 detect → 仍 SKIP，作为已决策语义的证据）。Not an AC violation.
- R2 (P3): Handoff:44（及 prompt 转述）"+49 净行"与实测不符：diff 六个 hunk 合计 +80（grep 实测 master/base `_detected_region_type`=663→worktree 670、`default_data_root` 681→737、文件 1123→1203 行）。+49 只是第 4 个 hunk 的数字。修正行数。
- R3 (P3): fail-fast 矩阵在持久化解码层有洞：`_load_pipeline_defaults._mapping`（core_assembly.py:474-481）对坏 JSON / 非 dict 值静默返回 {} ⇒ 非法 sfx.policy 被当成"未配置"→ SKIP，与 docstring "never a silent fallback" 表述相抵。建议把 docstring 限定为"解码成功之后的非法值 fail-fast"，或登记"settings_json 损坏 → 容忍为未配置"的既有语义（TASK-050 先例）。不影响 AC。
- R4 (P3): 装配期 fail-fast + 写入端零校验 ⇒ 一个非法持久化值会让应用整体启动失败（app.py:164 无捕获，异常直出），且产品内无清除入口（settings 页在 Legacy VM；新架构 UI/IPC 未接），只能外部改 DB。建议 Handoff 登记恢复路径（修/删 pipeline_defaults.settings_json 的 sfx.policy），未来 UI 写入面做前置校验。位置与 AC2 要求一致，非违规。
- R5 (P4): `settings["sfx"]["policy"]` 读取用 `_load_pipeline_defaults(conn)["settings"]`，而同一行的 `ocr.script` 读取用的是 `_load_pipeline_settings(conn)`（core_assembly.py:838）；两者解码等价但字面"同通道"应对齐（用 `_load_pipeline_settings` 一行更简）。P4 一致性/简化。
- R6 (P4): 测试矩阵可补的边界：`{"sfx": None}`、`{"sfx": []}`、`{"sfx": {"policy": True}}`（bool 非 str 分支未直接覆盖）；`pytest.raises(..., match="sfx.policy")` 中 `.` 未转义（应为 `sfx\.policy`）。
- R7 (P4): 红态证据未归档（Handoff §验证证据"红态未入库，红→绿由 commit body 叙述"）；AC3 要求"先红后绿"，建议集成方以 `git show a377a25a` + 在 base 上跑两个新测试复现红态（新测试在 base 上必然 collection error / 2 failed）。

Also the base metadata mismatch — include as R8 (P4): Task/handoff base_commit=8e0de8d0 vs review-input base=8996ca55；静态可证 core_assembly.py 的旧侧行号与 master(=base) 一致且 diff 只含 4 个文件，故实质等价；仍请集成方以 git 事实回填（对照 TA3-B2 R14 先例）。

Ordering by severity: R1 P2 first, then P3s, P4s.

Now the 逐项核对表 A-E:

A 默认零变化:
- 无配置路径：`_load_pipeline_defaults` 空行/无行 → settings={} → `_sfx_policy_from_settings` → SKIP（worktree core_assembly.py:711-713）✓
- 传递：闭包对 SFX 传 SKIP、非 SFX 硬编码 SKIP（1041-1045）；create_region 默认 `sfx_policy=SfxPolicy.SKIP`（editing/service.py:254）⇒ 显式传 SKIP 与旧"不传"逐位等价 ✓
- 泄漏：region_type 由 `_detected_region_type`（provider_label `sfx-` 前缀）唯一决定，非 SFX 分支硬编码 SKIP ⇒ 配置无法泄漏 ✓；且所有下游消费点都按类型走同一个 `decide_sfx_translation`（gate.py:33-38、service.py:179、rendering/service.py:553），即使泄漏也不会改变非 SFX 行为（防御纵深）✓
- 额外读取无副作用：多一次 `_load_pipeline_defaults`（879-881）是只读、容错、返回 {} 时行为不变 ✓；settings["sfx"] 与 provider runtime 的命名空间无冲突（profiles 嵌在 settings["providers"]["profiles"]，runtime 只读 providers/network，runtime.py:128/155/226/258）✓
- 结论：零行为变化成立（未运行测试 → NOT_VERIFIED 部分）。

B 配置通道与 fail-fast:
- 通道：save_settings_section("sfx", {...}) → pipeline_defaults.settings_json → 装配期 `_load_pipeline_defaults(conn)["settings"]`；与 ocr.script（handlers.py:322-329 经 run.settings_snapshot["ocr"]、由 pipeline_defaults 冻结 tasks/service.py:262）同一行同一 section 约定 ✓（对称性 → 见 R5 的读取器不一致）
- 位置：env 门之后、mock 分支之外（879-883）✓；异常经 1201-1202 关连接后上抛 ✓
- 值域/规范化：SfxPolicy 三值；strip+lower；缺 section/缺键/None → SKIP；未知词/空白/非字符串/section 非 Mapping → ValueError 且消息含 sfx.policy ✓（三处消息：715-719、724-727、730-733）
- 洞：解码层（R3）；写入端无校验（R4）
- 覆盖矩阵：见 R6。

C 测试质量:
- 19 Qt-free（9 选择 + 6 非法 + 4 装配）；2 Qt e2e（309 行）✓ 总 21，算术与 STATUS 基线 509 自洽（509+21=530）✓
- e2e translate：plan 门（units decision=run via service.py:418-423 + `_sfx_gate_suppresses`）与 step 门（译文落库，mock 仅对 region_type=="sfx" 返回 MOCK_SFX_TRANSLATION_TEXT，mock_local.py:125-126）双证明；speech 邻居正常译文=非 SFX 无扰 ✓
- e2e manual：OCR COMPLETED + plan 决策 skip_policy/sfx_skip + 无 translate step + 译文恒空；step 级 manual 语义由既有 tests/knowledge/test_sfx_gate.py:37 覆盖（本 Task 未改 gate）→ 可接受
- 装配闭包测试用真实 assembly + 闭包解包（tests/core/test_core_detect.py 先例），非平行 fixture ✓
- 弱项：红态未归档（R7）；`_detect_deps` 依赖私有 `_executor/_handlers`（脆但沿用先例，P4 不提也行——我归入 R6/P4 提一句？还是单独? I'll mention inside C as an accepted-risk note without a finding number... Actually the instruction says findings R1..; I can mention accepted risks in the table cells. Fine.)
- 既有测试零修改：diff 无任何既有测试文件改动 ✓（静态）；会受影响的既有断言（test_sfx_assembly.py:219、test_detect_handler.py:349、rendering/test_rerender.py:572）都断言默认 skip → 与新行为一致 ✓

D 范围纪律:
- diff 4 个文件：doc/handoffs（新）+ doc/tasks（frontmatter/交付记录）+ src/bootstrap/core_assembly.py + 2 新测试 ✓ 全在允许面
- 禁改面零：ports/contracts/packaging/apps/STATUS 未出现 ✓；models/gate/handlers/editing service/detection_sfx/ports/contracts 零触碰 ✓（我逐文件 grep 了 sfx 相关改动：master 侧无 sfx_policy reads，新代码只在 core_assembly）
- 唯一未核实：worktree 是否有未提交改动 / porcelain / diff --check（无 shell → NOT_VERIFIED）
- 行数声明错误（R2）。

E 契约判定:
- TASK-002 §7.2（217-225）已把 skip/manual/translate 三值自动行为契约化；§4 1.1（132 行）已契约化 region_type 携带与 sfx 语义；本次新增只是"装配层从一个既有 settings 行读取" ⇒ 不改契约语义 ✓ 判定成立
- 支撑：无任何契约枚举 settings 键/节（grep contracts 无 pipeline_defaults/save_settings_section）；M2-C1 IPC 的 SaveSettings 是泛化 `{section, values}`（M2-C1:121），无需为该键修订
- 但：`sfx.policy` 成为装配期事实契约（非法值阻断启动），目前只登记在 Handoff/Task；建议集成方在设置键注册面（未来 React 设置页/IPC 契约）登记键名与值域（Handoff 风险 2 已部分覆盖）→ 归入 R4/R1 的收口条件之一，或作为 P4 观察。

Let me add that as a P4 finding or fold into E verdict. I'll fold into the E cell + mention in 集成方闭合清单.

NOT_VERIFIED (integration-side):
1. 三套件 530 passed + 1 skipped 0 failed（命令与解释器见 handoff 接收方式）——未复跑
2. 新测试 21 条在 a377a25a 全绿 + 在 base 8e0de8d0 红态（collection error + 2 failed）
3. `git diff --check` EXIT=0 / `git status --porcelain` 干净 / worktree HEAD == 453f6d73 / review-input.diff 与 `git diff <base> 453f6d73` 逐字节一致（并确认 base 8e0de8d0 vs 8996ca55）
4. 禁改面专项 diff（ports/contracts/apps/packaging/detection_sfx/STATUS）零改动（静态只能证 core_assembly 与新增测试文件）
5. m2_acceptance 35 条与三套件是否含 QML TypeError 噪音（handoff 声称）
6. 端到端测试未覆盖的真实模型链 / `NEWMANGA_SFX_DETECTION=off` 与 policy 组合（handoff 已自述）
7. app 启动遇非法值的实际行为（app.py 无捕获 → 启动失败；静态判定）

集成方闭合清单:
1. 复跑三条命令（worktree 根，T1.1.1-impl-py312）确认 530+1sk；在 base 上跑两个新测试确认红态
2. 以 git 事实核对 base（8e0de8d0 / 8996ca55）并回填 Task frontmatter；确认 diff 只含 4 个文件、禁改面零
3. 要求 Owner 修 R2（+49→+80）与 R1（Handoff/Task 明确"仅新建 region 生效 + 既有 region 需删后重 detect/全新 data root"），或在集成 commit 中直接补登记
4. 决定 R4 的恢复路径登记（外部修 pipeline_defaults.settings_json）与后续"region 级策略更新入口/设置页"是否单独释放（Handoff 风险 2 已提）
5. 静态 R3/R5/R6/R7 可作为后续小改或接受并登记

推荐下一步（一句）: 集成方按闭合清单复跑三套件与红态后，要求 Owner 补 R1/R2 两处登记（不改代码）即可合并。

Wait — is it fair to require R1/R2 修 before merge? R2 is a doc number fix; R1 is a disclosure. Both doc-level in Handoff/Task (allowed面). Verdict: approved_with_conditions.

Let me double check one claim I plan to make: "app.py:164 无捕获" — assemble_services doesn't catch; but the caller of assemble_services might catch. Let me check the caller in app.py main/entry. Quick grep for assemble_services( usage / try around it.

Let me verify to avoid an inaccurate claim.
dsh: reasoning:
app.py:499-503 has a try/except around assemble_services in main() — let me read 495-525 to see whether the exception is reported gracefully (so "bricked" is accurate: app exits with error). Let me read.
dsh: reasoning:
Confirmed: main() catches, prints "bootstrap failed: <error>" to stderr, returns 1 → the app cannot start until the persisted value is fixed externally. That's my R4 evidence (app.py:499-509).

Now I have everything. One more consideration: should I check `_section` helper for validation whitelist (handlers.py `_section`)? Let me quickly confirm it doesn't validate unknown sections (relevant to the "same channel" symmetry claim, since the policy read is not via `_section`). Not needed.

Also confirm the region-type mapping prefix constant SFX_LABEL_PREFIX = "sfx-" (detection_sfx.py:142) ✓ — so the composite provider labels SFX candidates "sfx-N". And note `_detected_region_type` uses `.startswith("sfx-")`, so a label like "sfx-1" → SFX ✓. Fine.

One more thought on R1: is it possible that a *region policy* already persisted for existing regions would be updated by some "apply_sfx_policy" path in the future? Not now.

Also, is there possibly a path where the composite detect provider assigns labels to *existing* reused regions? No — reuse skips creation.

Also: the planner's backfill creates page tasks; not relevant.

Let me also double check the claim in R1 that detect reuses live regions — but wait: does the detect *step* even run for a page whose regions exist? Planning: detect step has `stages.get("detect")` validity. If a page already had detect completed, the step is SKIP_VALID. So even more so. And if re-run with forced mode? detect handler reuse → returns existing region ids. ✓

Alright, also for completeness: my claim "既有 SFX region 需 delete 后重新 detect" — after soft-deleting regions, does the detect step become re-plannable? The stage state "detect completed" might make it SKIP_VALID, which would prevent re-detect! Hmm. Planning uses `stages.get(step_type).is_valid` — the stage state comes from target snapshots (region snapshots etc.). For a page-level detect step, the stage state would be derived from the page's artifacts? Not sure. If detect is skipped as valid, then re-creating regions requires a new page or forced re-run. This weakens my proposed recovery path. Let me not over-specify: I'll say "既有 region 的迁移路径需明确（重新检出/删除 region 后重跑 detect 或全新 data root），当前产品内无 region 级策略更新入口" and put the exact procedure decision on the Owner/integrator. That's safer and still actionable.

Actually, I could quickly check how detect stage validity is determined for page tasks to avoid an incorrect suggestion... It's a detail; I'll phrase it as "需集成方/Owner确认可行步骤" to remain accurate. Good.

One more thing to check for the review's item 3: "manual 语义（保留 OCR+SKIP_POLICY+sfx_skip 登记）" — verified in test ✓ and matches contract §7.2 manual row ✓.

Now let me write the review. Format required:
## Verdict
## 逐项核对表（A…B…C…D…E）
## Findings（R1…，P0-P4，文件:行）
## NOT_VERIFIED（集成方运行时项）
## 集成方闭合清单
## 推荐下一步（一句）

Language: Chinese, technical identifiers in English. Should be thorough but not bloated. Note the user asked to output the full text directly.

Precision on line numbers: cite worktree (post-change) lines for new code and repo lines for unchanged code; note base line numbers where relevant.

Key line refs:
- worktree core_assembly.py:697-734 (_sfx_policy_from_settings), 688-694 constants, 879-881 read, 1031-1048 closure, 1201-1202 close-on-error.
- master/base core_assembly.py: 663 (_detected_region_type), 681 (default_data_root), 1123 lines total; worktree 1203.
- gate.py:32-42; step.py:176; tasks/service.py:143,163,179,418-423; editing/service.py:247-266; handlers.py:258-269, 287-296, 322-329; rendering/service.py:553-556; entities.py:48-53,230; schema.py:230-231; pipeline_defaults.py:105-120; runtime.py:128/155/226/258; app.py:499-509; mock_local.py:43,125-126; acceptance_bridge.py:310-319.
- tests: test_sfx_policy_settings.py:31-97? (matrix at diff lines), illegal 741-755; e2e file.

Also mention the count verification: 9+6+4=19, +2 = 21; 509+21=530 consistent with doc/STATUS.md:14.

For R2, give the arithmetic: hunks net +80 (0+1+6+49+13+11); file 1123→1203 (verified via read tool line counts); base `def default_data_root` 681 → new 737. Handoff:44 says +49.

Let me write it now. Keep it organized and reasonably concise but complete. Also include accepted-risk / positive verifications in the table cells.

For the verdict: `approved_with_conditions`（有条件通过）with the conditions being R1 (disclosure/decision) and R2 (number correction) — both doc-level; no code defect found.

I should also state explicitly: 未发现 P0/P1；默认零变化与 fail-fast 主张静态成立。

Length: moderate-long. Let's write.
## Verdict

**approved_with_conditions（有条件通过；未发现 P0/P1）**

- 代码面静态核对无正确性缺陷：默认 SKIP 零行为变化成立，fail-fast 位置与值域覆盖成立，闭包对非 SFX 恒 SKIP 的泄漏防护成立，改动面完全落在允许面。
- 条件均为**文档/登记级**（允许面内）：R1（配置只对"此后新建"的 region 生效这一语义未登记，且 Handoff 措辞会误导）与 R2（"+49 净行"与实测 +80 不符）。
- 全部运行时断言（三套件 530+1sk、红态、porcelain）本环境无 shell，列入 NOT_VERIFIED 交集成方。

## 逐项核对表

### A 默认 SKIP 零变化

| 项 | 静态结论 | 证据 |
|---|---|---|
| 无配置路径 | 成立 | 无 `pipeline_defaults` 行/空 `settings_json` → `_load_pipeline_defaults` 返回 `settings={}`（core_assembly.py:448-488）→ `section is None` → `SfxPolicy.SKIP`（core_assembly.py:711-713） |
| 传递链等价 | 成立 | 闭包对 SFX 传 `sfx_policy_cfg`、非 SFX 硬编码 `SfxPolicy.SKIP`（core_assembly.py:1041-1045）；`create_region` 默认即 `sfx_policy=SfxPolicy.SKIP`（application/editing/service.py:254），显式传 SKIP 与旧"不传"逐位等价 |
| 类型判定唯一 | 成立 | 类型仅由 `_detected_region_type(provider_label)`（`sfx-` 前缀，core_assembly.py:670-685 + detection_sfx.py:142）决定；非 SFX 分支无配置入口 |
| 泄漏影响面 | 成立（双保险） | 全部下游消费点共用同一规则：gate.py:32-42、tasks/service.py:179（`_sfx_gate_suppresses`）、translation/context/step.py:176、rendering/service.py:553-556 —— 非 SFX 恒 `TRANSLATE`，即便泄漏也不改变非 SFX 行为 |
| 命名空间冲突 | 无 | provider 档案嵌在 `settings["providers"]["profiles"]`，runtime 只读顶层 `providers`/`network`（runtime.py:128,155,226,258）；顶层 `sfx` 键对 runtime 惰性无害（`ocr` 节先例同形） |
| 新增只读开销 | 无副作用 | 装配多一次 `_load_pipeline_defaults(conn)`（core_assembly.py:879-881）：只读、容错、异常→`{}`，失败即 SKIP；异常路径经 core_assembly.py:1201-1202 关连接后上抛，无泄漏 |
| 既有断言兼容 | 成立 | 受影响的既有断言均断言默认 skip 且与新行为一致：tests/core/test_sfx_assembly.py:219、tests/providers/test_detect_handler.py:349、tests/rendering/test_rerender.py:572；无测试写 `settings["sfx"]` 节（tests 内 `save_settings_section` 仅用 `ocr`，test_pipeline_defaults_service.py:69,107,109） |

### B 配置通道与 fail-fast

| 项 | 静态结论 | 证据 |
|---|---|---|
| 写入通道对称性 | 成立 | `save_settings_section("sfx", {...})` → `pipeline_defaults.settings_json`（pipeline_defaults.py:105-120）；`ocr.script` 走同一行同一 section 约定（handlers.py:322-329 经 `run.settings_snapshot["ocr"]`，由 tasks/service.py:262 冻结自同一 `PipelineDefaults`） |
| 读取时点 | 成立 | env 门（858-868）之后、`if mock_local_providers:`（883）之外，mock 形态同样 fail-fast ✓ |
| 值域/规范化 | 成立 | `SfxPolicy` 三值 skip/translate/manual（entities.py:48-53）；strip+lower；缺 section/缺键/None → SKIP；非法 → `ValueError`，三处消息均含可检索串 `sfx.policy`（core_assembly.py:715-719、724-727、730-733） |
| 矩阵覆盖 | 基本完备（补充项见 R6） | tests/core/test_sfx_policy_settings.py：选择矩阵 9 + 非法 6 + 装配 4 = 19 |
| 洞 | 2 处（非 AC 违规） | 解码层静默容忍（R3）；写入端零校验导致启动阻断不可应用内自愈（R4） |

### C 测试质量

| 项 | 静态结论 | 证据 |
|---|---|---|
| 数量与算术自洽 | 成立 | 19 + 2 = 21；509（doc/STATUS.md:14 main 基线）+ 21 = 530，skipped 不变 ✓ |
| translate 全链真实贯通 | 成立 | plan 门：`units[*].decision.value == "run"`（tasks/service.py:418-423 经 `_sfx_gate_suppresses`→gate.py）；step 门：译文落库且 mock 仅对 `region_type == "sfx"` 返回 `MOCK_SFX_TRANSLATION_TEXT`（mock_local.py:43,125-126）⇒ 门放行 + 类型贯通双证明 |
| manual 语义 | 成立 | OCR `COMPLETED`（manual 保留）+ plan 登记 `skip_policy`/`sfx_skip` + 无 translate step + 译文恒空 + speech 邻居正常译文；step 级 manual 语义由既有 tests/knowledge/test_sfx_gate.py:37 覆盖（gate.py 未改，可接受） |
| 接缝真实性 | 成立 | 设置测试用真实 `assemble_core_services` + 装配自身闭包（不复刻 fixture）；e2e 用 `assemble_acceptance_core` 同款装配 + 真实 detect 闭包（脚本化 detector 仅替换 `deps.detector`，沿用 tests/core/test_core_detect.py 先例） |
| 红态证据 | 弱（R7） | Handoff 自述"红态未入库，红→绿由 commit body 叙述"；AC3 要求"先红后绿"却无归档日志（对照 M2-IMPORT-ALLOC-LIMIT 的"红态归档"先例） |
| 既有测试零修改 | 成立（静态） | diff 无任何既有测试文件改动 |

### D 范围纪律

| 项 | 静态结论 | 证据 |
|---|---|---|
| diff 文件面 | 合规 | 仅 4 个：`doc/handoffs/M2-SFX-TRANSLATE-ENTRY-a377a25a.md`（新）、`doc/tasks/M2-SFX-TRANSLATE-ENTRY.md`（frontmatter+交付记录）、`src/bootstrap/core_assembly.py`、2 个新测试文件 |
| 禁改面 | 零触碰 | `src/ports/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`detection_sfx.py`、`doc/STATUS.md` 均未出现在 diff；models.py/gate.py/handlers.py/editing service 未改（逐文件 grep 复核，`sfx_policy` 读取仅新增于 core_assembly.py） |
| 声明准确性 | 1 处错误（R2） | Handoff:44 "+49 净行"实为第 4 个 hunk 的数字，文件净增 +80（1123→1203） |
| git 级事实 | NOT_VERIFIED | porcelain/`diff --check`/worktree HEAD 无 shell 不可验 |

### E 契约判定

| 项 | 静态结论 | 证据 |
|---|---|---|
| TASK-002 不需修订 | **成立** | §7.2 已把 skip/manual/translate 三值的自动行为完整契约化（TASK-002:217-225）；§4 的 1.1 修订已契约化 `region_type` 携带义务与 sfx 翻译语义（TASK-002:132,350）。本 Task 未改 schema/协议/枚举，只新增"装配层从既有 settings 行读取" |
| 无键面契约被破 | 成立 | `doc/contracts/**` 全库 grep 无 `pipeline_defaults`/`save_settings_section`/设置节枚举；M2-C1 的 `SaveSettings` 为泛化 `{section, values}`（M2-C1_TYPED_IPC_CONTRACT.md:121），无需为该键修订 |
| 残留 | 1 项登记建议 | `sfx.policy` 已成为装配期事实契约（非法值阻断启动），目前只存在于 Handoff/Task；建议在设置键注册面（未来 React 设置页/IPC 契约）登记键名+值域+恢复路径（Handoff 风险 2 已部分覆盖） |

## Findings

**R1（P2，语义/登记；非 AC 违约）配置只对"此后新建"的 region 生效，既有 region 永不回溯**
- 证据链：策略仅在 `create_region` 调用点注入（core_assembly.py:1032-1048）→ detect handler 对已有 live region 直接复用、不再创建（infrastructure/providers/handlers.py:258-269）⇒ 已检出页面（含 TA3-B2 的 8×BJ06 + 1×K11 SFX region）重跑 detect 拿不到新策略；产品内无 region 级策略更新入口（`Region.apply_sfx_policy`，domain/regions/entities.py:247，全 src 无调用者；IPC/UI 无该字段写面）。
- 影响：Handoff §方案落点"settings 改后下一次 assemble 生效"会被读成"既有 region 也生效"，而实际只有新建 region 生效；对已有手稿库，SFX→translate 仍不可达，n=0 阻断只在新库/新检出上解除。
- 要求（允许面内即可闭合）：在 Handoff/Task 明确写"仅新建 region 携带配置策略；既有 region 需先清除后重新检出或使用全新 data root（具体可行步骤由 Owner 用 git/代码证据确认，注意 detect 步骤的 stage 有效性）"，并建议补 1 条 pinning test（预置 SKIP region + `policy=translate` 重跑 detect → 断言仍 SKIP），把该语义钉成显式决策。

**R2（P3，证据准确性）Handoff "+49 净行"错误，实为 +80**
- `doc/handoffs/M2-SFX-TRANSLATE-ENTRY-a377a25a.md:44`。六个 hunk 净增 0+1+6+49+13+11 = **+80**；实证：base/master `def _detected_region_type`=663 → worktree 670、`def default_data_root`=681 → 737、文件 1123 → **1203** 行（+49 只是 `@@ -678,6 +685,55 @@` 单个 hunk）。
- 要求：改正为 +80（或"core_assembly.py:688-734 + 879-881 + 1031-1048，净 +80"）。

**R3（P3，fail-fast 边界）持久化解码层是静默洞，与 "never a silent fallback" 表述相抵**
- `_load_pipeline_defaults._mapping`（core_assembly.py:474-481）对坏 JSON/非 dict 一律返回 `{}` ⇒ 此时非法 `sfx.policy` 被当作"未配置"→ SKIP，不 fail-fast。
- 处理：或把 docstring/Handoff 限定为"解码成功后的非法值 fail-fast（坏 `settings_json` 沿用 TASK-050 容忍为未配置语义）"，或补一条测试固化该边界。不影响 AC。

**R4（P3，运维面）装配期 fail-fast + 写入端零校验 = 不可应用内自愈的启动阻断**
- `save_settings_section` 不校验值（pipeline_defaults.py:105-120），非法值先成功落库；下次装配抛 `ValueError`（core_assembly.py:879-881）→ `app.py:499-509` 捕获后打印 `bootstrap failed:` 并 `return 1`，应用无法启动，因此也没有 UI 能清除该键。
- 处理：Handoff 登记恢复路径（修正/删除 `pipeline_defaults.settings_json` 的 `sfx.policy`），并在未来设置键契约/UI 写入面加前置校验；位置本身符合 AC2。

**R5（P4，一致性/简化）同一行两种读取器**
- 新代码用 `_load_pipeline_defaults(conn)["settings"]`（core_assembly.py:879-881），而同一行的 `ocr.script` 与 provider runtime 用的是 `_load_pipeline_settings(conn)`（core_assembly.py:838）。两者解码等价（448-505）但字面"同通道"应对齐；改用 `_load_pipeline_settings(conn)` 可少一层索引与一次语义分裂风险。

**R6（P4，测试边界）矩阵可补的取值与正则卫生**
- 未直接覆盖：`{"sfx": None}`（section 为 None 分支）、`{"sfx": []}`（非 Mapping 非 None）、`{"sfx": {"policy": True}}`（bool 非 str 分支）；`pytest.raises(..., match="sfx.policy")` 的 `.` 未转义，建议 `match=r"sfx\.policy"`（tests/core/test_sfx_policy_settings.py:241 等）。

**R7（P4，证据完整性）红态未归档**
- Handoff §验证证据自述红态只存在于 commit body。集成方可用廉价命令复现：在 base 上跑两个新测试文件（预期 collection error + 2 failed），归档到 verification。

**R8（P4，元数据）base 标签不一致**
- Task/handoff 声明 `base_commit=8e0de8d0`，review 输入声明 `base=8996ca55`。静态可证 core_assembly.py 旧侧行号与 master(=base) 完全对齐（663/678/681 三处），且 diff 只含 4 个文件，故实质等价；仍请集成方以 git 事实回填（对照 M2-TA3-B2 R14 先例）。

## NOT_VERIFIED（集成方运行时项）

1. 三套件结果 `530 passed + 1 skipped 0 failed`（`PYTHONPATH=src "…/T1.1.1-impl-py312/Scripts/python.exe" -m pytest tests/providers tests/core tests/m2_acceptance -q`）与 m2_acceptance 35 条不受扰。
2. 新增 21 条在 `a377a25a` 全绿；在 base 上红态（collection error + 2 failed）。
3. `git diff --check` EXIT=0、`git status --porcelain` 干净、worktree HEAD == `453f6d73`、`review-input.diff` 与 `git diff <base> 453f6d73` 逐字节一致。
4. 禁改面专项 diff（`src/ports/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`detection_sfx.py`、`doc/STATUS.md`）零改动；`models.py`/`gate.py` 零改动（静态仅能证 diff 内容）。
5. `e2e` 用例真机行为（offscreen Qt、SQLite 往返、`resume_blocked` 分支是否触发）。
6. Handoff 自述未跑项：真实模型链（chiqui7/ogkalu）、`NEWMANGA_SFX_DETECTION=off` × policy 组合、React/IPC 设置页入口。
7. 非法持久化值下的应用启动表现（静态判定为 `bootstrap failed` + exit 1，见 R4）。

## 集成方闭合清单

1. 复跑三套件命令确认 `530+1sk`；在 base 上跑两个新测试确认红态并归档（闭合 R7）。
2. 以 git 事实核对 base（`8e0de8d0` vs `8996ca55`）、diff 文件数=4、禁改面零、worktree HEAD=`453f6d73`（闭合 R8 + NOT_VERIFIED 3/4）。
3. 要求 Owner 在允许面内补两处登记：R1（既有 region 不回溯的语义 + 迁移步骤 + 可选 pinning test）、R2（+80 行数）；不改代码即可合并。
4. 裁决 R4 的恢复路径登记，并把"设置键注册（键名/值域/非法值恢复）+ region 级策略更新入口/设置页"作为后续 Task 归属（Handoff 风险 2 已提，建议明确 Owner）。
5. R3/R5/R6 可作后续小改接受并登记，或本轮一并处理（均不阻塞集成）。

## 推荐下一步（一句）

集成方先按闭合清单复跑三套件与 base 红态并核对 git 事实，随后要求 Owner 只在 Handoff/Task 内补 R1 语义登记与 R2 行数更正（无代码改动），即可合并 `a377a25a`。
