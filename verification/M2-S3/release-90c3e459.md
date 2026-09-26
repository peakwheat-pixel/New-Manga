# M2-S3 release record — 2026-09-26

- Task: `M2-S3` — Tauri Asset Protocol Feasibility Probe; state `ready / TAURI_ASSET_PROTOCOL_PROBE_RELEASED`.
- Authorization: current user request to choose and register the next bounded Task from the listed candidates. The release authorizes this isolated research/probe only; it does not authorize product runtime implementation.
- Decision: resolve M2-S1 S1-B1 before the large-media runtime. Contract 1.1 still marks Tauri asset-protocol form `NOT_RUN`; a real WebView permission/cache/lifecycle probe determines whether this path can safely serve restricted bytes. S1-B6 is deferred until a runtime channel exists.
- Owner / Reviewer / Integrator: DeepSeek Harness / ZCode (non-author) / Codex.
- Dependencies: M2-S1, M2-S2, and M2-C2 are `done` on the current master.
- Fixed base: `90c3e45962733799d43e3aefacf4fea99f662a2c`.
- Branch / worktree: `agent/deepseek/M2-S3-tauri-asset-protocol-probe` / `G:/CODEX/New Manga.worktrees/M2-S3-deepseek`; created from the fixed base and remains clean at that base. The released Task file lives on master; before claiming it, Owner copies only `doc/tasks/M2-S3.md` from master into the branch, then records `ready` → `in_progress` per the collaboration protocol.
- Owner write scope: `experiments/M2-S3/**`, `doc/tasks/M2-S3.md`, `doc/research/M2-S3_TAURI_ASSET_PROTOCOL_PROBE.md`, `doc/handoffs/M2-S3-*.md`, `verification/M2-S3/**`; assigned Reviewer may write `doc/reviews/M2-S3-<reviewed-head>.md`.
- Explicit exclusions: all product code, product tests, root dependencies/locks, existing Contract and security evidence, user materials, and final transport selection.
- Starting state: no probe files or test results exist yet. Every command and AC in the Task is `planned`; S1-B1 remains open until reviewed integration evidence supports a status change.
- Deferred decisions: S1-B6 waits for runtime; M2-C2 F-01..F-04 stay deferred to the next Task that actually touches the Contract.