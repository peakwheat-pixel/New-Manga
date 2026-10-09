# Checkpoint: P02 current prestart exact-head Review R1

- Timestamp / Agent / Task: 2026-10-10 07:10 +08:00 / Codex / P02.
- TaskStatus / ExecutionState: in_progress / ACTIVE.
- Boundary: REVIEW_CHANGES_REQUESTED / NO_SANDBOX_START.
- Owner / non-author Reviewer / Integrator: Codex / DeepSeek Harness / Codex (parent P02 implementation Owner remains Antigravity).
- Reviewed HEAD / tree / base: e6227e0b0b2c205105c8bc22ee49132d9da779e7 / d05694f1a6eb1867a3d0ee1e8416698e2e3f4ed9 / 4183e7f7cf366c27aa8ad8a0bc7300af48783470.
- DSH session: session-2d9c11f8-2d7f-4519-92ef-fb361c87edc9; CLI 0.2.0-rc.2; exit=0; mount script exit=0. Session mounted to P02-current-prestart-review-dsh-r1 workspace and will appear on the next DSH desktop launch; desktop was not restarted.
- DSH decision=CHANGES_REQUESTED; P0/P1/P2/P3=0/0/1/2; open=3. Review response SHA-256=CB0F37239524522B5446BA4865382D93C6554C6D3B1D58601BFBA667752BCF5B. Evidence: dsh-review-p02-current-prestart-r1.response.md, .exit, and .session.json.

## Findings and disposition

1. P02-PRESTART-R1-01 (P2): HostFolder delivery checkpoint points to a nonexistent/uncommitted old stdout and mismatched SHA/time. Repair the checkpoint to reference the committed r2 stdout SHA, empty stderr, and exit=0. Do not change the actual successful recheck result.
2. P02-PRESTART-R1-02 (P3): Codex route-validator and diff-check logs bind to delivery commit 3fcaee2f, while review package HEAD is e6227e0b. The DSH reviewer independently reran the route validator at e6227e0b (7/7, exit=0) and diff-check at exact HEAD (exit=0). State the binding distinction explicitly and keep exact-head claims scoped to the correct commit.
3. P02-PRESTART-R1-03 (P3): STATUS.md current evidence paragraphs and historical snapshot lacked blank lines. Restore paragraph separation so the 04:11 clone-prestate observation stays visually historical.

DSH also marked threshold derivation and capture-script provenance UNKNOWN because the saved host report records values but not the threshold verdict, and capture scripts were not in the review slice. Codex derived 11 host/WSB criteria from the saved report using the accepted thresholds in the process-isolation proposal; result=PASS is saved in r9f-current-host-threshold-assessment-r1.json. The exact immediate host/UI/config/clone/root checks remain mandatory after the next Review. The captured evidence is not a substitute for those immediate checks.

## Verification and scope

- DSH independently checked the 32-path diff against the expected base; it found no path outside the P02 documentation/evidence allowlist.
- DSH reran verify_plan.py at reviewed HEAD e6227e0b: 7/7 PASS, exit=0. It reran git diff --check at base..HEAD and HEAD^..HEAD: exit=0.
- DSH confirmed the saved HostFolder counts, filesystem/source/EOL pins, hardlinks, output capability, Sky/WSB values, root manifest, one-attempt limit, and no false Smoke/Build/AC PASS claims.
- DSH did not run wsb start, any Sandbox/guest command, Build, GUI, product tests, or HostFolder access/scan/list/hash. It made no tracked changes.
- Smoke admission=ADMITTED (one attempt); wsb start=NOT_RUN; Smoke=NOT_RUN; Build Gate=BLOCKED; build=NOT_AUTHORIZED / NOT_RUN; hook/cache=BLOCKED / NOT_VERIFIED; AC1–AC7=BLOCKED / NOT_RUN; Hard Build Barrier=EFFECTIVE.

## Next exact action

修正 HostFolder checkpoint 的日志指针/Hash/时间；补充 route-validator/diff-check 的 HEAD 绑定说明；为 STATUS.md current 与 history 段落恢复空行。保留 Smoke 与 Build gates。对修订后的固定 delivery commit 运行 route validator、diff-check 和 JSON assertions，随后重新派发 DSH exact-head Review。Review 批准前不启动 Sandbox。