# P02 R9 Start Checkpoint — Isolation Smoke Authorization and Preflight

- Timestamp: 2026-10-10 02:47 Asia/Shanghai. State boundary: R9_PREFLIGHT_RECORDED / AWAITING_EXACT_HEAD_REVIEW.
- Parent Task=P02 remains in_progress / ACTIVE; Codex-only child subtask, Owner=Codex, non-author Reviewer=DeepSeek Harness, Integrator=Codex.
- Live root: main@ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50, common dir=G:/CODEX/New Manga/.git; current Codex branch/worktree=codex/P02-process-isolation / C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/New Manga.
- R9 base=ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50. Owner source worktree was clean before this checkpoint; only the fixed r9 P02 evidence paths are being written.
- User authorization: the user renewed PROJECT_ORCHESTRATION_AUTHORIZATION and specifically directed real isolation evidence for P02 before barrier release. Scope r9 records the narrow supersession of earlier prohibitions; no feature change/elevation/build/product acceptance is authorized.
- Preflight stage 1=PASS: feature via documented non-elevated CIM is Enabled; root protected manifest 203/203 exact match, zero staged; source commit exists/ancestor; WSB identity/version/list valid and no session running; fixed clone path absent; hardware/free-space thresholds pass; all 12 HostFolder roots and 20 pinned inputs match; r3 config hash matches.
- Exact machine observations: [preflight observations R2](codex-scratch-build-preflight-observations-r2.json). Summary and limitations: [preflight report R2](codex-scratch-build-preflight-r2.md).
- No clone or Sandbox was created/started. Recursive pre-start manifest, object hardlinks, read-only/write/network canaries, screenshot/session binding, and post-run protection checks remain NOT_RUN. Build Gate=BLOCKED; build=NOT_AUTHORIZED / NOT_RUN; P02 AC1–AC7=BLOCKED / NOT_RUN.
- Tests/checks so far: read-only host preflight only. Product tests/build/GUI/WebView=NOT_RUN.
- Next exact step: validate the r9 candidate, freeze it at a commit, then dispatch DeepSeek Harness exact-head review. If approved, record a separate Codex Smoke admission and create the fixed clone; before any wsb start, verify its full Git and mapped-input boundaries.
