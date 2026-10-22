# Git Worktree Inventory — 2026-10-12

只读快照；Task 状态仅在 STATUS/REBASELINE_PLAN 明确映射时标注，否则为 UNKNOWN。`commits outside main` = `git rev-list --count main..HEAD`；dirty worktree 保留，clean/reachable 本身不构成删除授权。
统计：366 registered；clean=302；dirty=64；missing=0。12 条 stale admin metadata 不属于 registered worktree，见 cleanup manifest。

| Path | Branch | HEAD | State | Tracked changes | Untracked | Commits outside main | Task mapping | Disposition |
|---|---|---|---|---:|---:|---:|---|---|
| G:/CODEX/New Manga | main | 343895fb5f0329c0c07a7104ec321b698f967607 | DIRTY | 26 | 1234 | 0 | ACTIVE main checkout | ACTIVE / MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/comic-test-assets/New Manga | agent/codex/M2-TA2A-ja-public-assets | f8ef48c4079e03e57a7ed0da1e9b79c05e90979c | DIRTY | 0 | 1 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/diag-reading-export-001/New Manga | agent/deepseek/DIAG-READING-EXPORT-001-reading-export-flaky-diagnosis | 77c661b0e32c8f6f5a9a2e4006a267624f622e2e | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/m2-ac1-integration/New Manga | codex/M2-AC1-integration | b43f5628562ce8a7b633355ecf9b7539bd5656b4 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/M2-C1-dsh-review-7de1cd2-r2 | review/deepseek/M2-C1-zcode-7de1cd2-r2 | b2377288680569dbee4e2299fd7dfae4de067c54 | DIRTY | 0 | 8 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/m2-i2-review-a4705a9/New Manga | (detached) | a4705a9f473d0e8d9087068edc4bec572d90439a | DIRTY | 0 | 5 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/m2-rc2-integration/New Manga | codex/m2-rc2-integration | 72215b8f4c1a2dee5dd86334ddf03b2938c07b9e | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/m2-rc2-integration-review/New Manga | (detached) | 83de13dfe0521125715c2e26da75b96a63103938 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/m2-rc2-zcode/New Manga | agent/zcode/M2-RC2-resource-channel-hardening | dc8e5c95c31ccc0dd96fa2287b44aa962c70153d | DIRTY | 0 | 56 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/no-hf-comic-assets/New Manga | agent/codex/M2-TA2C-no-hf-assets | 2e7843275235a9dfc2d63ab8e80facc28a489f6a | DIRTY | 0 | 4 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r1 | (detached) | e6227e0b0b2c205105c8bc22ee49132d9da779e7 | DIRTY | 0 | 4 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r2 | (detached) | 9bd1999c76ff65994d6e7bca44ba568553fe26ec | DIRTY | 0 | 6 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r3 | (detached) | 322526fcde650ea9dcfde4a14f828afeb8808ead | DIRTY | 0 | 5 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r4 | (detached) | 6ffa2a9c5375d21bb905f4d6adbccb9124ed531b | DIRTY | 0 | 5 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r5 | (detached) | 68bafd3741f376bfab297b8ced911191e96bd424 | DIRTY | 0 | 3 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r5-followup | (detached) | 999e6adfc229698344c0cbf9bfb6d636fe73fb7c | DIRTY | 0 | 3 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/p02-d27-review-repair-review | (detached) | c328691af582ff782c9d41dda60494dec990c6a6 | DIRTY | 1 | 0 | 1 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/P02-hook-cache-review-dsh-r4 | (detached) | ceca2446da88df23a719f40868cc89e1481ccb2c | CLEAN | 0 | 0 | 7 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/p02-post-review-preflight/New Manga | codex/P02-post-review-preflight | 8a0685c9bf5aec7e7cc51f466f3fec7b176c35de | DIRTY | 0 | 9 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/p02-post-review-preflight-review/New Manga | (detached) | d92c405304cb88712cb8777d8ec59618f4806df7 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/p02-post-review-preflight-review-r2/New Manga | (detached) | 8a0685c9bf5aec7e7cc51f466f3fec7b176c35de | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/P02-preflight-r4-083d2b47-review-dsh | review/deepseek/P02-preflight-r4-083d2b47 | 083d2b47f7051c2dedd0d9ae4346ae1affab6c1b | DIRTY | 0 | 3 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/P02-preflight-r4-condition-closure-92dc7361-review-dsh | review/deepseek/P02-preflight-r4-condition-closure-92dc7361 | 92dc7361194f1db8fdf7aff3a15a3d234ae56678 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/P02-preflight-r5-844aec28-review-dsh | review/deepseek/P02-preflight-r5-844aec28 | 844aec282416111310d9a9efcac5bc9e0c6eb451 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/P02-preflight-r6-c85a041c-review-dsh | review/deepseek/P02-preflight-r6-c85a041c | c85a041c514f3c0dd1c355a2d09f064dbc64e749 | DIRTY | 0 | 1 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/P02-preflight-review-dsh-r1 | (detached) | 561f4105171b99910d739698380787f35203d3f2 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/New Manga | codex/P02-process-isolation | 999e6adfc229698344c0cbf9bfb6d636fe73fb7c | DIRTY | 0 | 121 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r1 | (detached) | c542a31b102cdc5c129efd9df155a2760ed777b2 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r2 | (detached) | 3555213a748a7b407400589e1490a387353dec16 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r3 | (detached) | 92361e3578eedb93d7cf6c4c5a4db06652d31fe9 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r4 | (detached) | fb0a7668d948ae68f15fd59aaffd6aedf6663c99 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r5 | (detached) | 1c7efb172b8e9d766e38f84cf3728a90bb5953d0 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r6 | (detached) | 30da5fafb23ec578132d91b88c66bd1e6a6f9d2c | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r6-followup | (detached) | 2394dc98d7dc723402eecaee9f37b54bda41ae0e | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r7 | (detached) | d90dd8f1d44dd022314bb63a305b013dcadb6a44 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/p02-r2-docs-closeout/New Manga | codex/P02-r2-docs-closeout | 67fdf9c5c577ed44271f64aa8668e3bdb8994a94 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/p02-r2-docs-closeout-review/New Manga | (detached) | 4d5a0864495d9482ad162d05588b4921aaece3ac | DIRTY | 0 | 7 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/p02-r2-docs-fixes-review | (detached) | f366124ecb6194ff9ea4ee0d6c684ccb2b781a07 | DIRTY | 0 | 7 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/p02-stage-a-r8-exact/New Manga | (detached) | 89413f45a601966eb40d7af7abea65cbdfc754b3 | DIRTY | 9 | 0 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/p02-stage-a-r8-integration/New Manga | codex/P02-stage-a-r8-integration | 549a6544f0be1eec66c09ece393fd1a409f10bf3 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/p02pre-r1g/New Manga | agent/antigravity/P02PRE-R1H | 256e3ea622cba7a658020ddcf015b18894d88b38 | CLEAN | 0 | 0 | 7 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/p02pre-r1h-attempt6-zcode/New Manga | agent/zcode/P02PRE-R1H-R6-EXEC-A6 | 343895fb5f0329c0c07a7104ec321b698f967607 | DIRTY | 0 | 10 | 0 | Current P02 path (STATUS/PLAN) | REQUIRED_EVIDENCE / MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/p02pre-r1h-codex | agent/codex/P02PRE-R1H | c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d | CLEAN | 0 | 0 | 13 | Current P02 path (STATUS/PLAN) | REQUIRED_EVIDENCE / MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/p02pre-r1h-integration/New Manga | (detached) | cddff58469b56e181019a8ddfeade80684bc7eb9 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/p02pre-r1h-r6-attempt4-antigravity | agent/antigravity/P02PRE-R1H-R6-A4 | c7c7879e8ae90ad23b29d9d8cc6ea97e3eff5427 | CLEAN | 0 | 0 | 2 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/p02pre-r1h-r6-exec-a6-antigravity/New Manga | agent/antigravity/P02PRE-R1H-R6-EXEC-A6 | 343895fb5f0329c0c07a7104ec321b698f967607 | DIRTY | 0 | 3 | 0 | Current P02 path (STATUS/PLAN) | REQUIRED_EVIDENCE / MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/p02pre-r1h-zcode | agent/zcode/P02PRE-R1H | 256e3ea622cba7a658020ddcf015b18894d88b38 | CLEAN | 0 | 0 | 7 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| C:/Users/49745/.codex/worktrees/p04-prod-command-concurrency-review | (detached) | 751abae2277e975eddacc385a423bcd796334f97 | DIRTY | 0 | 7 | 3 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/.codex/worktrees/p2-p2-1-zcode/New Manga | agent/zcode/P02PRE-R1H-P2-1-EVIDENCE-CLOSURE | 343895fb5f0329c0c07a7104ec321b698f967607 | DIRTY | 0 | 4 | 0 | P2-1 closure (STATUS) | BLOCKED / REQUIRED_EVIDENCE / MUST_PRESERVE |
| C:/Users/49745/AppData/Local/Temp/diag002-s2-2jWfPm | (detached) | d268a17082028fb445e2ac3bbb71f265961a2af2 | DIRTY | 937 | 6 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/AppData/Local/Temp/diag002-s2v4-FTf6BC | (detached) | d268a17082028fb445e2ac3bbb71f265961a2af2 | DIRTY | 1582 | 6 | 0 | UNKNOWN | MUST_PRESERVE |
| C:/Users/49745/AppData/Local/Temp/diag002-s2v5-WJGAfi | (detached) | d268a17082028fb445e2ac3bbb71f265961a2af2 | DIRTY | 2434 | 6 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/architecture-decision-registration | codex/architecture-decision-registration | 5a16d8aaa0a9a9362cef6bd2e96d0dbd79e63c62 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/CATEGORY-CLARIFY-1 | zcode/category-clarify-1 | b688c450e07aa033067f7db933d586ec3f2e0666 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/DERIVED-GC-1 | zcode/derived-gc-1 | c2bb8c4654daccd0c641f29e99a2d18760a9402c | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/DERIVED-GC-2-DESIGN | codex/m2-derived-gc-2-design | 4fd91029b7bfae23e7544d34f07d9c8c1f473755 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/DERIVED-GC-2-DESIGN-review-r1 | codex/m2-derived-gc-2-design-review-r1 | 4a930c611c1e7a353f5fe5584932f4cf6d8048c1 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/DERIVED-GC-2-DESIGN-review-r2 | codex/m2-derived-gc-2-design-review-r2 | 3a6846758ebdb18e3ee696e0c1410aa698e43225 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/DERIVED-GC-2-DESIGN-review-r3 | codex/m2-derived-gc-2-design-review-r3 | 8557a3d4162d00dc7a985ede0dabda22809f60fd | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/DERIVED-GC-2-DESIGN-review-r4 | codex/m2-derived-gc-2-design-review-r4 | e4c0967f83a08d9b9e2d84605d17923e81a844b6 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode | agent/zcode/M2-DERIVED-GC-2 | 0fadc330a6daa42de6c78be52feaae26ce6724ea | DIRTY | 24 | 0 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/DIAG-FIX-A-zcode | agent/zcode/DIAG-READING-EXPORT-001-FIX-A-terminal-wait-semantics | 6fe7bd86a5aa66b6161ec658feb27aa3bb1c969f | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/DIAG-FIX-B-zcode | agent/zcode/DIAG-READING-EXPORT-001-FIX-B-reader-heartbeat-lifecycle | f93ea667cd00f4e7647dfcc95f9cc74a08417529 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/DIAG-FIX-C-zcode | agent/zcode/DIAG-READING-EXPORT-001-FIX-C-quit-and-leave-wiring | 0e0e699e6b9c27e5eecab51ae33dd2dbbd000e72 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/DIAG-LOCK-CHANGED-REPRO-002-zcode | agent/zcode/DIAG-M2-LOCK-CHANGED-REPRO-002 | 2c13530ba382262605306efee01c1395e4718bb7 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-dsh | agent/deepseek/DIAG-M2-REGIONLESS-LOCK-CHANGED-001 | 7a03ac5f9677c359c6e13c007d77d46e604e8df0 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/DIAG-READING-EXPORT-001-integration | codex/DIAG-FIX-C-integration | 62a54131f70bfae31cf724079699b1a6894bc42d | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/DOC-FIX-STALE-COMMENTS-zcode | agent/zcode/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS | 8ab9045bd68fff0064ab6b77d824f85369f4b3e1 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/GOV-001-deepseek-review | agent/deepseek/GOV-001-review-5a16d8a | bbf24e73b0d5b40f23f90ce851e47c7cf681ab2a | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/GOV-001-integration | codex/GOV-001-integration | 307a940265fc325076fe77698750392531f8fce1 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-AC1-zcode | agent/zcode/M2-AC1-end-to-end-acceptance | 51f70ed19cd974f0687d92df008c209272655de5 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-AC2-zcode | agent/zcode/M2-AC2-data-integrity | c3ee8dbebc860f67abd668301dc81ab78d917bac | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-AC3-zcode | agent/zcode/M2-AC3-provider-fail-closed | a63d3372ebbd364da9fb5fb53af835559235bb6c | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-AC4-zcode | agent/zcode/M2-AC4-reader-lineage-library-pagecount | 890f0c745809f1978786ae26193dd29fadce1d23 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-AC5-BUILD-FRESH-CHECKOUT-zcode | agent/zcode/M2-AC5-BUILD-FRESH-CHECKOUT | ed8a6ea64efe92957b1306bcfbaeca22ff223b57 | DIRTY | 14 | 0 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/M2-AC5-zcode | agent/zcode/M2-AC5-package-clean-start | 0541b86b8af7a26981861cf6d3e1c2fbb49250f7 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-C1-codex-typed-ipc-contract | agent/codex/M2-C1-typed-ipc-contract | 86013b34da52e106ad55afc035792e9340c5aee8 | CLEAN | 0 | 0 | 16 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-C1-deepseek-review-7d908a5 | review/deepseek/M2-C1-typed-ipc-7d908a5 | e6fc3a59b913f2aef1ab8c7a77ff47df0cd114a1 | DIRTY | 0 | 7 | 4 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/M2-C1-deepseek-review-r2-7e65f4f | review/deepseek/M2-C1-typed-ipc-r2-7e65f4f | 5386744720061d1e411356d2004c5e3ae6ccb6fd | CLEAN | 0 | 0 | 12 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-C1-deepseek-review-r3-4d66523 | review/deepseek/M2-C1-typed-ipc-r3-4d66523 | ac38dede84ff22290c9b9d579c1372c8184a7bd5 | CLEAN | 0 | 0 | 14 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-C1-dsh-r3-review-import | (detached) | b2377288680569dbee4e2299fd7dfae4de067c54 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-C1-dsh-review-7de1cd2 | review/deepseek/M2-C1-zcode-7de1cd2 | b2377288680569dbee4e2299fd7dfae4de067c54 | DIRTY | 0 | 5 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/M2-C1-integration-gate-r3 | codex/M2-C1-integration-gate-r3 | b4c3fc1b15a84d22f8ba46dadb01817fe5ff3631 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-C1-qoder-review-7de1cd2 | review/qoder/M2-C1-zcode-7de1cd2 | 0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5 | DIRTY | 0 | 2 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/M2-C1-qoder-review-r3-4d66523 | review/qoder/M2-C1-typed-ipc-r3-4d66523 | 1950a23619ae489ecc88209593eac75546d61105 | CLEAN | 0 | 0 | 15 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-C1-zcode-registration | agent/codex/M2-C1-zcode-owner-registration | 7478f72fe6f9872cae29f4fa12888b5e1f2380f1 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-C1-zcode-typed-ipc-contract | agent/zcode/M2-C1-typed-ipc-contract | b2377288680569dbee4e2299fd7dfae4de067c54 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-C2-zcode | agent/zcode/M2-C2-typed-ipc-contract-revision | c18f273ad5a7768c6ae1726610da1ac27aa958d3 | DIRTY | 0 | 2 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/M2-D1-codex-review | codex/M2-D1-review-0a27a54 | 41f05713673400dbd4c9592a44fff0bc35579cb8 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-D1-deepseek-audit | agent/deepseek/M2-D1-headless-qt-coupling-audit | 6f2cbb3002b9ab6db048d6464fb83c696fe746ce | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-D1-integration | codex/M2-D1-integration | 409a3c683d80736d4edd22a899e3c94653855ffa | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-D1-registration | codex/M2-D1-audit-registration | bbeb4892746795be4bca92f4e5dda91a77c422a3 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-DETECT-WEBTOON-DIAG-zcode | agent/zcode/M2-DETECT-WEBTOON-DIAG | e1d939fa5f153e4d1a8e68d4c6996384c487ce4e | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-DETECT-WEBTOON-TILING-zcode | agent/zcode/M2-DETECT-WEBTOON-TILING | 0bcaa6197f2cecd6e6621c6b360aa612b9800f3a | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-DETECTION-HYGIENE-zcode | agent/zcode/M2-DETECTION-HYGIENE | 388305f50b5f76d5dad282b3c169b7ad08d34ed6 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-C1-zcode | agent/zcode/M2-DOCTR-QUAL-C1 | 4d75efbccba377bfc54679652f113185a59ae166 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-C4-zcode | agent/zcode/M2-DOCTR-QUAL-C4 | 76fc593f37e8a5b0243796741c5dc580de72428f | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-RUN-zcode | agent/zcode/M2-DOCTR-QUAL-RUN | 4cc7def681da414ed0bc61b1010494a69ee87593 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-FIX-DIGEST-PERF-zcode | agent/zcode/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF | 510202acdfbf085250c7ee09bb7b6421b9d70f03 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-FIX-DIGEST-SEEK-2GIB-zcode | agent/zcode/M2-FIX-DIGEST-SEEK-2GIB | 8a1bc1e856e41aef62a9ad355138a426975c59c0 | DIRTY | 14 | 0 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/M2-FIX-EXPORT-LINEAGE-zcode | agent/zcode/M2-FIX-EXPORT-LINEAGE | d395ef70b311b0d960cddcb0680e9fc423c0b09c | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-FIX-F02-zcode | agent/zcode/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY | 3cef4831fa20a73d3792ef0e24b819186ec88947 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-FIX-LISTBOOKS-zcode | agent/zcode/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN | b6cb1af2299b887461e1e7b2914b7577f8a6871c | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-FIX-STUB-DECODER-zcode | agent/zcode/M2-FIX-STUB-DECODER | 69250a39ac3ff48c13c28cfd34241eb9fb78a494 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-I1-codex-review | codex/M2-I1-review-a89447f | a89447fb91c9aa81f4d847d732ebc91320ad24f2 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-I1-integration-09ad43a | codex/M2-I1-R3-integration-09ad43a | 148981a339d12b45fa9a712b247ed92698349c36 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-I1-R2-codex-review | codex/M2-I1-R2-review-0766952 | ada7cd2aa884164f3e26e504f7fb200022709be8 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-I1-zcode | agent/zcode/M2-I1-core-assembly-seam | 8dab0abbc667e09054616d4f0b0f5a76b1a04d9e | CLEAN | 0 | 0 | 1 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-I2-antigravity | agent/antigravity/M2-I2-qtfree-logic-extraction | 0d6acc7d985a0a96f5a27c2f25b7b2afcd66e716 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-I2-codex-review | codex/M2-I2-review-5d4a465 | 5d4a4650943507ca4053376d6acea36f146c704a | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-I2-integration-0d6acc7 | codex/M2-I2-integration-0d6acc7 | 0275290c3cc64e92dc53157b7d35028447d4d54f | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-I2-review-0d6acc7 | (detached) | 0d6acc7d985a0a96f5a27c2f25b7b2afcd66e716 | DIRTY | 0 | 5 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/M2-IMPORT-ALLOC-LIMIT-zcode | agent/zcode/M2-IMPORT-ALLOC-LIMIT | 499a3da7e6451012caf0c3e0737639c23725a40e | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-IPC1-agy | agent/antigravity/M2-IPC1-production-core-library | 5556fc8e7a184da25af0f082a3d53f0bd84c56dc | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-KO-TILE-CALIB-zcode | agent/zcode/M2-KO-TILE-CALIB | 14f596502dffef0be5331fdac43d08d8915852dc | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-OCR-PADDLE3X-1-zcode | agent/zcode/M2-OCR-PADDLE3X-1 | 53326278b6c48797394a60663c2266b218901bcb | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-P1-agy | agent/antigravity/M2-P1-regionless-region-rebinding | 59acb340318359b6c94278c968edcafb125268c1 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-PROD-DETECT-1-zcode | agent/zcode/M2-PROD-DETECT-1 | 320d795522f89eb50ef2595b64e0010ba7fda87f | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-PROD-DETECT-2-zcode | agent/zcode/M2-PROD-DETECT-2 | 3bef8a15442be7b00960b1e152134feb9dc4f709 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-PROD-DETECT-3-zcode | agent/zcode/M2-PROD-DETECT-3 | 0a47040707ef893b22f7fc51b7ac4d3f86ac07d1 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-PROD-SFX-PROBE-1-zcode | agent/zcode/M2-PROD-SFX-PROBE-1 | 751e26a7ef53fa295b55d10a87443b573d3d3039 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-QUAL-DETERM-CALIB-zcode | agent/zcode/M2-QUAL-DETERM-CALIB | 7a0286ef7beff61d56004519631662a6822c9497 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-R1-deepseek | agent/deepseek/M2-R1-qt-runtime-feasibility | 052f99cb861adfb1602bd34b4cac86d4567d6b97 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-RC1-zcode | agent/zcode/M2-RC1-large-media-resource-channel-runtime | ce3c3771d15c60b743b1e1da936edc445676b305 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-REGION-OVERLAP-ARBITRATION-zcode | agent/zcode/M2-REGION-OVERLAP-ARBITRATION | e43cc5db12287bd21b9bdbb37228339985cd16f8 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-REGION-RETYPE-CONTRACT-zcode | agent/zcode/M2-REGION-RETYPE-CONTRACT | 7f390ca6bc793a9c4e6c1a96bd0a8c06a39b5c5b | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-REGION-RETYPE-CORE-zcode | agent/zcode/M2-REGION-RETYPE-CORE | 0f88cbcdaceb09b914d2465036e5cf4e1e1d7db0 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-REGISTRY-ENV-zcode | agent/zcode/M2-FIX-REGISTRY-ENV | 75c72dfad0637423b028da1637d4c2279e23149b | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-RG1-zcode | agent/zcode/M2-RG1-release-gate | 8e0100ba7fe7b4c7dcd9c43d85f5fc50e8bbce1e | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-S1-scope-registration | codex/M2-S1-review-64c87d1 | 8984b4b38f413325dd0860c5e7bd7751571dc59f | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-S2-antigravity-review-fbdf1bc2 | agent/antigravity/M2-S2-review-fbdf1bc2 | ea11d1092436cceda1135d04944e5c1592297125 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-S2-zcode | agent/zcode/M2-S2-resource-channel-security | fbdf1bc237a2c34db7546e76990f3aad29dfae8d | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-S3-deepseek | agent/deepseek/M2-S3-tauri-asset-protocol-probe | 90c3e45962733799d43e3aefacf4fea99f662a2c | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-S3-zcode | agent/zcode/M2-S3-tauri-asset-protocol-probe | bcef79e775bf4a5b4a4eceb4c3e63ac630aa6de9 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SETTINGS-IPC-CHANNEL-zcode | agent/zcode/M2-SETTINGS-IPC-CHANNEL | 8a28c797b414453df8c3bb14d1cdc4bbf199a93b | DIRTY | 6 | 0 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/M2-SETTINGS-UI-SFX-POLICY-zcode | agent/zcode/M2-SETTINGS-UI-SFX-POLICY | efad4b711a85e1e9a5507744bb4f7dc51daf4d0a | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R1-zcode | agent/zcode/M2-SFX-ANNOTATE-R1 | 7ff8a3ec8642cbb45a0b14b603cd42852728f67a | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode | agent/zcode/M2-SFX-ANNOTATE-R2 | 44cd7cfb63f81fa2786aa1204cd4bf1a0d9e6d12 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R3-zcode | agent/zcode/M2-SFX-ANNOTATE-R3 | 2e58bb8846dd40897b1387f92ddb1cc67da6986f | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-BJ13-RECALL-1-zcode | agent/zcode/M2-SFX-BJ13-RECALL-1 | 04d5f621d56cf877b9aa0d63d6889c736f1d7df7 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-CORRECTION-EXPORTER-zcode | agent/zcode/M2-SFX-CORRECTION-EXPORTER | 669146a19c10ca367dfa1de7027f10326830f7a5 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-DATA-INFRA-zcode | agent/zcode/M2-SFX-DATA-INFRA | 54e04f1ba8767a231e04512b43cf3b7f0550f91f | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-DETECT-DOMAIN-EXT-DIAG-zcode | agent/zcode/M2-SFX-DETECT-DOMAIN-EXT-DIAG | 9cd512d7d75fd290238b8dd17e28871a10a69a01 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-E2E-MATERIAL-zcode | agent/zcode/M2-SFX-E2E-MATERIAL | ca107e1dad4a345ec729526d35fdea2253de7e03 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-EPFAIL-AUDIT-1-zcode | agent/zcode/M2-SFX-EPFAIL-AUDIT-1 | 9ff8fe0112764a6f9f5669362d83ee4694ebe8e9 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-EVAL-zcode | agent/zcode/M2-SFX-DETECT-EVAL | 72586945b2cd355e69f191a9ef115dc432450226 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-FINETUNE-PREFLIGHT-zcode | agent/zcode/M2-SFX-FINETUNE-PREFLIGHT | 824c52f40218c29b9bf7aad1e50169b1e6c72819 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-GATE-T3-zcode | agent/zcode/M2-SFX-GATE-T3 | 4ababbb532dd956f162eadf2b4f1d541b4d47f9e | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-GPU-EP-1-zcode | agent/zcode/M2-SFX-GPU-EP-1 | fbb5b7f4147ff721994598df65d1c9b4d103bebb | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-MISROUTE-UI-IMPL-1-zcode | agent/zcode/M2-SFX-MISROUTE-UI-IMPL-1 | 9f605e0880163af5f9264d1c9202c688fa9fcfb0 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-MISROUTE-UI-MITIGATION-zcode | agent/zcode/M2-SFX-MISROUTE-UI-MITIGATION | 3f589a0bbce3b60096ce55e68f4427da0b1f4850 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-PROD-1-zcode | agent/zcode/M2-SFX-PROD-1 | 81ff304d43b779f8d12f8ab26759d47744e47ba7 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-SEM-1-zcode | agent/zcode/M2-SFX-SEM-1 | da780b7de4643dafb540b522ad697fc8179c3b3a | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-SYNTH-BG-AUTO-zcode | agent/zcode/M2-SFX-SYNTH-BG-AUTO | 5907be5967ea01ce42ee2834e84837771abadc7f | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-T4-SWITCH-zcode | agent/zcode/M2-SFX-T4-SWITCH | bd23eaa8e2ba6d356cdf498dd3235069a3c6a81d | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-T5-TILE-KO-zcode | agent/zcode/M2-SFX-T5-TILE-KO | 306f50408d1eac4d1238e5c785955df5a1002e97 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-TILE-WIDTH-CALIB-1-zcode | agent/zcode/M2-SFX-TILE-WIDTH-CALIB-1 | ea6fbc2cb0ce8567aa21fd950c85e12d27eeb5f2 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V1-zcode | agent/zcode/M2-SFX-TRAIN-V1 | 4e0069044a10386a267074151911c3e56280fbdb | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V2-zcode | agent/zcode/M2-SFX-TRAIN-V2 | 9be2574d4928c55a2aae1e698a6b4da205edd8ca | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-SFX-TRANSLATE-ENTRY-zcode | agent/zcode/M2-SFX-TRANSLATE-ENTRY | e0ba396a51e309e24099dcde7bd4fd17c941d159 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode | agent/zcode/M2-TA2B-OPEN-ASSETS | 98766fdcabad3a8aa2ce733fe341f6c12af2c04f | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-TA2C-TOOLING-GAPS-zcode | agent/zcode/M2-TA2C-TOOLING-GAPS | 1fd2787dc3f69fc7e05112697409f88a61e4e18a | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-TA3-A-E2E-SMOKE-zcode | agent/zcode/M2-TA3-A-E2E-SMOKE | 86bdbded8dfc59bb3f93be8e21f5dc89e70ef12e | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-TA3-B-zcode | agent/zcode/M2-TA3-B | 81cf51255ed6058ea660f20b1090477ef13e7b09 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-TA3-B2-KO-RERUN-zcode | agent/zcode/M2-TA3-B2-KO-RERUN | 581fec6265f849f93435374a8cbaa1304a7f17b2 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-TA3-B2-zcode | agent/zcode/M2-TA3-B2 | 952e8ddbdd33591521956ecdce0357b9b9c31b96 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-TA3-B3-KO-FULLRUN-zcode | agent/zcode/M2-TA3-B3-KO-FULLRUN | bb4b16bc2b01ac051442fcd6c125b2b33d66b230 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-TASKS-BACKFILL-MULTIREGION-zcode | agent/zcode/M2-TASKS-BACKFILL-MULTIREGION | 277016792bc5dfcdcedb902d8ebeb074a28c57ce | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-TASKS-PRIMARY-SFX-GATE-zcode | agent/zcode/M2-TASKS-PRIMARY-SFX-GATE | 0820d3d50c3d5ded5dc51c7ffc7e6311c8514e6f | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-UI1-antigravity-review-23a5ac0 | agent/antigravity/M2-UI1-review-23a5ac0 | 83a795b6717b8f4aed2d84cba3405e09a232ebd5 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-UI1-integration | codex/M2-UI1-integration | e5acaae905f6730e68d080390b9e6d33aae68e48 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-UI1-integration-final-83a | master | 78faeee583600c51740200efd0e05776d6f2cf96 | CLEAN | 0 | 0 | 3 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-UI1-master-integration-20260925 | codex/M2-UI1-master-integration-20260925 | d13b0b11c169b50024370d16b6cb9394de9a46f5 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-UI1-qoder | agent/qoder/M2-UI1-react-parity-visual-contract | 784ce1831adc791882383681a743984c4b847d0b | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-WEIGHTS-SOP-zcode | agent/zcode/M2-MANGA-WEIGHTS-SOP | 4723bfb4991d604062580849cbd3cb71b9595c22 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/M2-WORKBENCH-REACT-1-zcode | agent/zcode/M2-WORKBENCH-REACT-1 | a8bd3ddceeab9170d5fd023823cbb5a6ebc91bb4 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P01-c8-review-dsh | (detached) | 91ab1ef8ddaa1d00b0b34880a103937b4831590d | DIRTY | 0 | 5 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P01-c9-review-antigravity | (detached) | 7645577ab374b581eb7081fd57675c32793249f5 | DIRTY | 0 | 5 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P01-closeout-review-antigravity | (detached) | 51bc01fec2652c0e2bc39bb119f8dd7ca3c294cb | DIRTY | 0 | 12 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P01-integration-codex | codex/P01-integration-20261009 | b7ad98b29196e9859cbfbfe187e6822569f79367 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P01-metadata-audit-codex | agent/codex/P01-metadata-audit | a22a0d935bb1b99be006601a7a2c49cd305b1910 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P02-build-preflight-codex | codex/P02-build-preflight | 4b54f304dc201d129d4ba1c62d0368252e6301b1 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P02-fallback-scope-codex | codex/P02-fallback-scope | 0b95c6a1024f89ae341c637c0d531611175acdc5 | CLEAN | 0 | 0 | 1 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P02-harness-scope | codex/P02-harness-scope | 3c3e4687785e65f668f1146052e78c3da074ba99 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P02-hook-cache-isolation-plan-codex | codex/P02-hook-cache-isolation-plan | ceca2446da88df23a719f40868cc89e1481ccb2c | DIRTY | 3 | 7 | 7 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P02-hook-cache-review-dsh | (detached) | 09d592a09a7c54fe64ed305e15fce5db3591109b | CLEAN | 0 | 0 | 6 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P02-owner-amendment-codex | codex/P02-owner-amendment | 4458b35051dd847ceadad11c332a7e2de3b49512 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P02-owner-transfer-integration-codex | codex/P02-owner-transfer-integration | 3f4d16633a18a9ab7aea5b08b67653cd3f6bf8ff | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P02-process-isolation-review-dsh-r7 | (detached) | d90dd8f1d44dd022314bb63a305b013dcadb6a44 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity | agent/antigravity/P02-real-webview-harness | 89413f45a601966eb40d7af7abea65cbdfc754b3 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P02-real-webview-harness-zcode | agent/zcode/P02-real-webview-harness | e1948466082b3cadbfde1da53b791319e359a10b | DIRTY | 24 | 2633 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P02-stage-a-validation-172eee84-failureprobe | (detached) | 172eee84240e101186b12f1aa09e8a2f9ec92d68 | DIRTY | 3 | 0 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P02-stage-a-validation-172eee84-full | (detached) | 172eee84240e101186b12f1aa09e8a2f9ec92d68 | DIRTY | 8 | 0 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P02-stage-a-validation-172eee84-probe | (detached) | 172eee84240e101186b12f1aa09e8a2f9ec92d68 | DIRTY | 5 | 0 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P02-stage-a-validation-38672473-exact | (detached) | 38672473f93971a4681aef682e5635e64b0bd896 | DIRTY | 9 | 0 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P02-stage-a-validation-38959ba99-exact | (detached) | 38959ba99b84f771aba7010b53b9b47ecdc75488 | DIRTY | 9 | 0 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P02-stage-a-validation-5fa8a41f | (detached) | 5fa8a41f1fbda56dd88fb3a87e1604fd0a14a59e | DIRTY | 5 | 0 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P02-stage-a-validation-9b82e97b | (detached) | 9b82e97b8aadc5b6b8710e03b5128a608697f56e | DIRTY | 5 | 0 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P02-stage-a-validation-cc1bd750-full | (detached) | cc1bd7505f3fc48079db7ea2719040e77a8c58dd | DIRTY | 7 | 0 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P02-stage-a-validation-cc1bd750-probe | (detached) | cc1bd7505f3fc48079db7ea2719040e77a8c58dd | DIRTY | 4 | 0 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P03-codex-traceability-normalization | codex/P03-traceability-log-normalization | 140a6686ef13e45d4c95de2c7929b61bdaef1d1e | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P03-dsh-review-4c04459-r2 | (detached) | 4c04459bc6b8bf9ef6cba596829ac47f37bc02af | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P03-dsh-review-6d84b48 | review/deepseek/P03-packaged-sfx-entry-6d84b48 | 6d84b480d5996d6374192bbbba07807848b8ebde | DIRTY | 0 | 1 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P03-dsh-review-d4c17dd | (detached) | d4c17ddb4ed2b5961102018d7d31a383bdaebab3 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P03-packaged-sfx-entry-antigravity | agent/antigravity/P03-packaged-sfx-entry | 85482c5b001d452953c3ed797ce3c4ed64cae4e3 | DIRTY | 0 | 3 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P03-review-prep-112495c7 | (detached) | 0a25ceb4577158d9dff184776ff4599e74e25c57 | CLEAN | 0 | 0 | 2 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P03-review-prep-85482c5b | codex/P03-integration-4c04459 | 552464238a69ad2cea63cff18abe98f412dbae87 | DIRTY | 0 | 22 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity | agent/antigravity/P04-prod-command-concurrency | faea1a2c9e19f4817fd792290e91324f047529f9 | DIRTY | 1 | 24 | 14 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/P04-scope-freeze | codex/P04-scope-freeze | 4e6a8cfd487a181a8a63236dcd69cc72dd00cb6c | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P05-category-retryable-notes | codex/P05-category-retryable-notes | bc2b690bc4f66d286bb8f16764269f6681c70b0d | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P08-dsh-review-16fb07a9-r4 | (detached) | 16fb07a973b36b0b129945bc3a85f9ae51234982 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P08-dsh-review-1ad05d9-r3 | (detached) | 1ad05d99c924678f35a2558f6e15b6c548d92f09 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P08-dsh-review-31c2638 | (detached) | 31c263892605fdc984982b9ba1875fa6eb609cb6 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P08-dsh-review-490f9bd | (detached) | 490f9bd9637de0812a3ef3d9bbfa754868d5c15f | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P08-dsh-review-af1ddeec-r5 | (detached) | af1ddeec1b998f2ddaf121a85f5fd382561aae1e | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P08-dsh-review-ecb3b520-r6 | (detached) | ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P08-dsh-review-fe222464-r7 | (detached) | fe222464616152e9c95208e06c248565f2fd86a6 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/P22-roundtrip-serialization-antigravity | agent/antigravity/P22-roundtrip-serialization | 4a707db80499f11e93cee163a9a10bf6392b1a92 | DIRTY | 0 | 57 | 24 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh | agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG | c2bde356554c37520bd87d0bc13791a748250133 | CLEAN | 0 | 0 | 1 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity | agent/antigravity/M2-PACKAGED-AC1-ICU-ISOLATION-FIX | f889671c9752da6239ec66ccd14abe0f598c181c | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/PAGE-NAV-1 | zcode/page-nav-projection-1 | 7bec3589eb6a01882e8f681c9b9a5b69e9e88821 | DIRTY | 0 | 2 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/PAGE-RESOLVE-1 | zcode/page-resource-resolve-1 | cae3ac159ff85d39dd54b34a7cc1dd9a37920993 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/POSTHOC-WINDOW-2026-09-19-qoder | agent/qoder/POSTHOC-WINDOW-2026-09-19 | 86b1518f4b52261a7c5bc4f22eec2060cc034118 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/RC4-domain-commands | codex/rc4-domain-commands | 6a7b4c3d691ed89bff8513b9ac409ee5ef5267e8 | DIRTY | 0 | 1 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/RC4-integration | codex/rc4-integration | 0a7e0d5be97b273cc3093a59da11008f20bae89f | DIRTY | 21 | 0 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/RC4-react-consumer | codex/rc4-react-consumer | 7021d34ce5445d57f83098a6876cc6ef9657ddc5 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/RC4-review-preflight | (detached) | bb7f3dcba9685f761bbb9ee5e271b1f91c3e7811 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/REGION-DEBOUNCE-1 | zcode/region-debounce-1 | 80db177d9172f113fca2f1ca4490d4693ce802a0 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/RESOLVE-DEBOUNCE-1 | zcode/resolve-debounce-1 | b4a8d2194e8191da5506247088d20cae6645ac18 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity | agent/antigravity/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD | 8b867e0208246e2e478a2906a2198c60c7d88aa6 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-codex-integration | codex/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-integration | e4242ecd419eb0eea098d2f63b40f709aa5caeea | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-dsh-r1 | review/deepseek/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r1 | 0ea16b832dcf32297d8c73df2ccdcf764c694368 | DIRTY | 0 | 4 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-dsh-r2 | review/deepseek/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r2 | daab1996b99c7036108bc505cc3db29b744fdf9d | DIRTY | 0 | 3 | 1 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex | codex/M2-RUNNER-SNAPSHOT-DEBT | 73588624b70c337ca4fcb36a4d42e91d3b03f5b0 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T1.1.1-detector-evaluation | agent/deepseek/T1.1.1-detector-evaluation | ed607b755e68e478914f7106ac903cef909cb080 | CLEAN | 0 | 0 | 1 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T1.1.1-production-text-detector | agent/zcode/T1.1.1-production-text-detector | 4a631355316e959e9a9704f1ead2eaed39cbf7a3 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T1.1.2-qoder | task/t1.1.2-region-canvas-qoder | 5b917459deeb72de575d0985e1315889444cef4b | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T1.2.1-r5-integration | agent/codex/T1.2.1-r5-integration | e92c414da4112e4b00d34294dd001bcada6e8b7f | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T1.2.1-settings-ui-viewmodel | agent/zcode/T1.2.1-settings-ui-viewmodel | b8a8841449135320337c9bc9736f85b695d8ab2a | CLEAN | 0 | 0 | 1 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml | agent/qoder/T2.1.1-design-f-qml | ddb20441936f14f199e5036564a1667613351928 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T2.1.1-integration | agent/codex/T2.1.1-integration | 3411959dc68477a1305dbdee852cb263d5259ab6 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T2.2.1-qoder | agent/qoder/T2.2.1-reader-workbench-qml | 08465739ae92d7175a77d00053abe598bb150bae | CLEAN | 0 | 0 | 5 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T2.2.1-zcode | agent/zcode/T2.2.1-reader-workbench-polish | df637df1f9d6e8468bc73d6ff585bbf55e8e9a64 | DIRTY | 0 | 1 | 1 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/T3.1.1-antigravity-storage-sqlite | agent/antigravity/T3.1.1-storage-sqlite | 81c319705afd2be2abc168414310164acdce9d90 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.1.1-deepseek-review-899bd3c | agent/deepseek/T3.1.1-review-899bd3c | 4e1eb3ab829eea438437e6289418c20393950dcb | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-packaging | agent/antigravity/T3.2.1-windows-packaging | ffff7c688df07165c6e801c0c9572e9c4910cb9e | CLEAN | 0 | 0 | 8 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-10 | agent/antigravity/T3.2.1-repair-10 | d7edea5f00507a8d9601e6a95294695353cbf7f6 | CLEAN | 0 | 0 | 49 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-11 | agent/antigravity/T3.2.1-repair-12 | 8738c41d7215920935e6fa067d3740e69280cdc6 | CLEAN | 0 | 0 | 54 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-14 | agent/antigravity/T3.2.1-repair-14 | 2f0d26645a5e3597977859f0624d72f561d38ba1 | CLEAN | 0 | 0 | 4 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-3 | agent/antigravity/T3.2.1-repair-3 | d37088a46f0bdae14b7a068f93bbcec38ffe5bad | CLEAN | 0 | 0 | 15 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-4 | agent/antigravity/T3.2.1-repair-4 | 0e0905f8041743175239183d9c4ab7eabb78cb90 | CLEAN | 0 | 0 | 19 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-5 | agent/antigravity/T3.2.1-repair-5 | 297c3dd7d0c977eb22eedefd0ba1ae03d29b64cd | CLEAN | 0 | 0 | 25 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-6 | agent/antigravity/T3.2.1-repair-6 | 14f587c90f6627c0788ec35d5fd72e44ff4806cf | CLEAN | 0 | 0 | 30 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-7 | agent/antigravity/T3.2.1-repair-7 | 37d5488ebf8e33f897e802b4147cbd5fb1ad8e04 | CLEAN | 0 | 0 | 41 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-9 | agent/antigravity/T3.2.1-repair-9 | eeb095ea94cdf0d477bcb09ab7c761883b06f833 | CLEAN | 0 | 0 | 46 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-clean-release-gate-20260925 | codex/T3.2.1-clean-release-gate-20260925 | b18fa0e70ec4356a207fd7d941cdcf0cb2f1c285 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-codex-release-gate-closeout | codex/T3.2.1-release-gate-closeout | 188d72a9d144b8cab16f77757abc46318ac8e5e6 | CLEAN | 0 | 0 | 50 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-codex-repair-14-integration | codex/T3.2.1-repair-14-integration | 6a68fdeb92d8a1c7903166a8076d6260bf8fa79a | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-10 | agent/deepseek/T3.2.1-review-be5200e | ddc21a2f3cf5521675e95d6e2a8f8f50b1c065fb | CLEAN | 0 | 0 | 49 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-11 | agent/deepseek/T3.2.1-review-9622395 | 4f2f8a07e5b8119834cdc4cfd0fd0aa5c62ac4cc | CLEAN | 0 | 0 | 53 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-12 | agent/deepseek/T3.2.1-review-a2f6695 | a6564862649b00fd91fa4e4ea8a2f64205eb71b7 | CLEAN | 0 | 0 | 54 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-740503e | agent/deepseek/T3.2.1-review-740503e | 60d1d5035e32b0709c00f2ab0fdde844e2acee9e | CLEAN | 0 | 0 | 1 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-7d687f5 | agent/deepseek/T3.2.1-review-7d687f5 | 4613338815406be0fdf2240cb1e5715a619f61f7 | CLEAN | 0 | 0 | 1 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-9 | agent/deepseek/T3.2.1-review-d2bf6a8 | 85f8c59d0a012c1edc4e466187b5b42515297d74 | CLEAN | 0 | 0 | 46 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-92c9307c | agent/deepseek/T3.2.1-review-92c9307c | 48bc7f36b67fa73d3b5badbc4f0d079aa11bb29f | CLEAN | 0 | 0 | 1 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-cdc0b6f | agent/deepseek/T3.2.1-review-cdc0b6f | 54bf043379363cacca3da5310eb1ecb371f62407 | CLEAN | 0 | 0 | 6 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-d79d7dd | agent/deepseek/T3.2.1-review-d79d7dd | 54f2627196969309d5c3942caf19ccec6c6ab7b5 | CLEAN | 0 | 0 | 14 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-f39ddc0 | agent/deepseek/T3.2.1-review-f39ddc0 | dc199f607c407adce40d303cb182b28f9a76a1db | CLEAN | 0 | 0 | 1 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-f6dc383 | agent/deepseek/T3.2.1-review-f6dc383 | 82049145f5dae7e36c6e4f8b71b0b959995ed0c7 | CLEAN | 0 | 0 | 31 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-repair-14 | agent/deepseek/T3.2.1-review-repair-14 | 430193968b01022b52edb72b4d6615e3e836e181 | CLEAN | 0 | 0 | 3 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-repair-14-r2 | agent/deepseek/T3.2.1-review-repair-14-r2 | f616175e24229c4fbcffb0145e10764e0c7f93df | CLEAN | 0 | 0 | 5 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-repair-7 | agent/deepseek/T3.2.1-review-repair-7 | 2585efd69009cd7620c6b020e67df90c7d49b0f1 | CLEAN | 0 | 0 | 6 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-integration-20260926 | codex/T3.2.1-integration-20260926 | ad003bb3c7489632772f452855ac7fa173ee698f | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-legacy-closure-20260926 | codex/T3.2.1-legacy-closure-20260926 | 7478f72fe6f9872cae29f4fa12888b5e1f2380f1 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-qoder-repair-13 | agent/qoder/T3.2.1-repair-13 | 8738c41d7215920935e6fa067d3740e69280cdc6 | CLEAN | 0 | 0 | 54 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-qoder-review-78aba7c | agent/qoder/T3.2.1-review-78aba7c | b66788a813b04c0305226331c54327e178093664 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-REPAIR-13-owner-zcode | codex/T3.2.1-REPAIR-13-owner-zcode | b693a5387640668ffd7c1681f8729207475461e8 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/T3.2.1-zcode-repair-13 | agent/zcode/T3.2.1-repair-13 | 13ae23f65e963cf1d5aea19634572627e5e709db | DIRTY | 0 | 3 | 64 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/TASK-001-deepseek-review | agent/deepseek/TASK-001-review | 6c0a9961166eba24d08ae27e3d0b813182b1d916 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-002-deepseek-review | agent/deepseek/TASK-002-review | e866ea1b3b0845b5ef803e0a55f175e9dc911bf0 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-003-deepseek | agent/deepseek/TASK-003-verification-spec | 4a76cac6f33fd9fa5ebf510501ca42ee62d5e7cb | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-004-deepseek-rereview | agent/deepseek/TASK-004-rereview-181a356 | 5f4db0f35defbbb9261e2250d25e2434a93a94b4 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-004-deepseek-review | agent/deepseek/TASK-004-review | 020c2859b601dedf53c0bc1c822f75f55dae5a2a | CLEAN | 0 | 0 | 1 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-004-zcode | agent/zcode/TASK-004-windows-packaging | a370b1ecca03c97a39fddd10761a9e07cd857164 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-005-codex | agent/codex/TASK-005-minimal-bootstrap | 28ffadc3aabee9e008f7fe7b9f55e894c7a3ad79 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-005-deepseek-review | agent/deepseek/TASK-005-review | 118038fbcad63dc6133947d9529b3927df8897c6 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-005-zcode-audit | agent/zcode/TASK-005-audit-metadata | 9fa68353bde1168b81081509d4369d6371f55caa | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-006-deepseek-review | agent/deepseek/TASK-006-review | baeef13b49a184d9c37863ba9c9f605e83c394af | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-006-zcode | agent/zcode/TASK-006-persistence-artifact | af6deefcbb7ca38e455c5a81686f5b2b4b616165 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-007-deepseek-review | agent/deepseek/TASK-007-review | 25df1cab3adc713c62f34ecd0b56d4210511d7b9 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-007-zcode | agent/zcode/TASK-007-library-import | 76328bfc6b2408f3800215624a29b08b46256bb3 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-008-deepseek-review | agent/deepseek/TASK-008-review | f9e59770e7617744178b0f56fc10af558a416298 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-008-zcode | agent/zcode/TASK-008-region-editing | f7becb4d39720277a80f0f07cf8d269a84b9ab89 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-009-deepseek-review | agent/deepseek/TASK-009-review | d2fe13c12a13e340291032f1e18adf976c2b58fa | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-009-zcode | agent/zcode/TASK-009-provider-network-credentials | 50b693016dc0cba5f992084d4bf45d90c34afbd4 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-010-deepseek-review | agent/deepseek/TASK-010-review | 008b1013a9863f4f506764d17d01245cb2403db1 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-010-zcode | agent/zcode/TASK-010-translation-context | 05effee0d597fabd82ce03ea7f9f8ebef89297c2 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-011-deepseek-review | agent/deepseek/TASK-011-review | 36f874a00753c9347ca7aaa60fcd80f94188d0f0 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-012-deepseek-review | agent/deepseek/TASK-012-review | 084db6000f4505f95c6451df8bc5aadefd93f5ff | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-012-zcode | agent/zcode/TASK-012-navigation-library-ui | e6fe52a1edb99716c4be2d61a8ac96824fc06046 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-013-deepseek-review | agent/deepseek/TASK-013-review | 8f7c454321266ba65b3c5152dde19a39d5dfd7ad | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-013-qoder | agent/qoder/T1.1.2-region-canvas | 52de319a4d9cb03ab591736438ac9ca1a3e0f720 | CLEAN | 0 | 0 | 2 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-013-zcode | agent/zcode/TASK-013-workbench-task-progress | 7e5052305ac5a4f8745c8c4c4495f8008187475e | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-014-deepseek-review | agent/deepseek/TASK-014-review | 5276a18c365add9b2b39b9f3d705b09aa6abd163 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-014-rendering-style | agent/zcode/TASK-014-rendering-style | a49fc761a7172f8dd6515bbcfdefa6e5f51563c2 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-015-deepseek-posthoc | agent/deepseek/TASK-015-posthoc | 9b776853787ed22bd18082057cc0c4895a9c0f40 | CLEAN | 0 | 0 | 1 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-015-zcode | agent/zcode/TASK-015-reader-export | a915d5628ce732a7a0fd06bfdc60b6f99684e250 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-016-deepseek | agent/deepseek/TASK-016-ocr-detection-experiment | 81532749586f0a30eb02b780b11fa6eb691dd244 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-016-review-fixed | (detached) | dfd11b9cf3264ef254074043e8f2de5c3f3cdd22 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-017-deepseek-posthoc | agent/deepseek/TASK-017-posthoc | fb0bc400709665e1fcc998d42cd367a696fb5030 | CLEAN | 0 | 0 | 1 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-017-deepseek-tail | agent/deepseek/TASK-017-tail-review | e50ba29d6c9c2282f04132f8a609a393c709f034 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-017-zcode | agent/zcode/TASK-017-translation-protocol-experiment | 387bb1e6a9bad2c881fb4992ee7b362b97070235 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-018-deepseek | agent/deepseek/TASK-018-mask-inpainting-experiment | c8c2a8e88e0166bddc4af86ff6880e29adda139d | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-019-deepseek | agent/deepseek/TASK-019-provider-integration | 3929d9e0c1945f126a681ff046cbad9b93f2b944 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-020-zcode | agent/zcode/TASK-020-webtoon-chunked-reading | 40f20e7aff78991abbda8961275124fad561ef53 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-021-zcode | agent/zcode/TASK-021-backup-trash-cleanup-diagnostics | 79ec0d2b4f0c408a1cfd2d89da79545317b855e6 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-023-zcode | agent/zcode/TASK-023-pdf-mobi-import | c87f21c4e7c116ebe4eebc0b7872dcf72d918a92 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-024-deepseek-posthoc | agent/deepseek/TASK-024-posthoc | 9454cecf7be07ff12dda8734dfc73fb7e9aa3fdd | CLEAN | 0 | 0 | 1 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-024-zcode | agent/zcode/TASK-024-extension-boundaries-design | 86072c30a9587d5eced3daa14c555409d6917e6c | DIRTY | 1 | 0 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/TASK-028-deepseek-review | agent/deepseek/TASK-028-review | 09108d160c42b5f6617e55d8b43a1d807d7c7f79 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-029-deepseek-review | agent/deepseek/TASK-029-review | 9b69f35a34356af48bfd13f23f074d91440f1ebf | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-029-zcode | agent/zcode/TASK-029-unified-sqlite-persistence | 4fcb1503506271f5caa6fbd8d8e87a0b1ee0f803 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-030-deepseek-review | agent/deepseek/TASK-030-review | dba26372dc63d4d23acfd809e7b646106693c230 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-030-zcode | agent/zcode/TASK-030-main-bootstrap-assembly | a64c93ab22d8aa18201f0d7eb3f4a3652dd9b0fd | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-031-deepseek-review | agent/deepseek/TASK-031-review | 0509003e4df0ca84428d61faf32dd16a70168d30 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-032-deepseek | agent/deepseek/TASK-032-sfx-policy-gate-region-type | ff887dbda79fbf2ff365e4f3e6f837094d8fe10f | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-033-deepseek | agent/deepseek/TASK-033-full-chain-handlers | d322ce2eb9967a6d73a79a71e8a5841a23c9e5ca | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-033-zcode | agent/zcode/TASK-033-full-chain-handlers | 401d6d7e56f20ddcb26a5c554c04b665d71ddd1e | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-034-deepseek | agent/deepseek/TASK-034-test-layer-hardening | 132e776da36b3e496745abb308a8cf2e685bcd5e | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-035-deepseek | agent/deepseek/TASK-035-render-sfx-gate-region-type | 092957eabc6b31293fb4fddf274229d5b6f5a6ee | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-036-deepseek | agent/deepseek/TASK-036-settings-validation-and-export-order | 56062216ae16e8a73305f922d4a6fdf5c433a10d | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-037-zcode | agent/zcode/TASK-037-flaky-diagnostic-fix | 7c35277ef25e021f39426630e0badc3cd72d63a2 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-038-zcode | agent/zcode/TASK-038-production-assembly | fcf791f0d12a4156c5b4d26cdb26365b2187d70e | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-039-zcode | agent/zcode/TASK-039-clean-availability | 355c12338c88b88899f3cd33d9d7a010f2de2826 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-040-zcode | agent/zcode/TASK-040-clean-probe-injection | 9b9c2dab43b389f59552762da8182ab17283ce0c | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-041-zcode | agent/zcode/TASK-041-mobi-import | 4d925f339e0a776602c98f354b5164ca122deb21 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-042-zcode | agent/zcode/TASK-042-streaming-decode | 98b38b7ed6519118432cf8520c0f7b8cbd5685cd | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-043-deepseek | agent/deepseek/TASK-043-import-fixes | d765f22c57fc5d204ff24e64c5f2abf725d187ad | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-044-deepseek | agent/deepseek/TASK-044-purge-integrity | 9c7d0fa14ec91785f2d58930c05dbcfae31d2e79 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-045-deepseek | agent/deepseek/TASK-045-webtoon-display-fixes | 7261ec7f4f94e76065c4208a84e040830476a89e | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-045-posthoc-zcode | agent/zcode/TASK-045-posthoc | 8b47b2efd05b86f6bdef2f251f3365c5fb812998 | CLEAN | 0 | 0 | 1 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-046-zcode | agent/zcode/TASK-046-decode-rewind-cost | 60cebc060752d4c68b15288c7602841d0e6f7db4 | DIRTY | 1 | 2 | 0 | UNKNOWN | MUST_PRESERVE |
| G:/CODEX/New Manga.worktrees/TASK-047-qoder | agent/qoder/TASK-047-ui-ux-gui-design | 980ae7df716a0a1b40a060cb3d028cd250e93cbc | CLEAN | 0 | 0 | 9 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-048-zcode | agent/zcode/TASK-048-thread-sqlite | 8dc13ebc32d381a9a5956051b2b9ae9ed61387df | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-049-zcode | agent/zcode/TASK-049-region-input | 7aca966d2962d7de5593ec2e5286f5557a0979fc | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-050-zcode | agent/zcode/TASK-050-settings-bindings | e49349b0c3a22ebea14dc42b94fb5ca2e5311cca | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-051-zcode | agent/zcode/TASK-051-workbench-viewer-modes | 7299b819b336bcdfd9b4dc86a88c8f6ac9af848e | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-052-zcode | agent/zcode/TASK-052-command-error-surface | 78aa5984776bf50863f3c2643d7599402623622d | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-053-zcode | agent/zcode/TASK-053-run-files-leak | 54fbdfc3ba5125dc985333f5cb4b6c0f64b1e3d1 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-054-zcode | agent/zcode/TASK-054-cancel-pending-rename | 51bc5a5f8a50cff1ac8a5af7073602b2f6ca78d7 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-055-zcode | agent/zcode/TASK-055-diagnostics | 763a23cec977488881ddd14483aa2f6b7894e400 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-056-zcode | agent/zcode/TASK-056-cache-version-cleanup | 823b2d361c53fe9f59db62cd80e668435e445c71 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-057-qoder-review | agent/qoder/TASK-057-review | 257ee5bb3fc08b0a4811c016ac5b006f6dfddb30 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-057-zcode | agent/zcode/TASK-057-backup-restore | 29546f792540dbd07cf4fd1a002543d003621b39 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-058-qoder-review | agent/qoder/TASK-058-review | d0cac07f6c6b5cb24b96744681df110c62caa766 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-058-zcode | agent/zcode/TASK-058-graceful-shutdown-drain | 9c8cd5237956dac81ccdd4808298298ff3648a5b | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-059-codex-review | agent/codex/TASK-059-review | 06064f89f2876c72c0f531397b7057f5cb6ef3ac | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-059-qoder | agent/qoder/TASK-059-ui-redesign | 6cb0afb5e53a229c700b0570d19f0f03c9942811 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-059-zcode | agent/zcode/TASK-059-ui-redesign | 58272abfbe4115b265347e014798ebe506e6f6f4 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-060-qoder-review | agent/qoder/TASK-060-review | 36b886ce5a74ced4c20ed18bb642296a4f64af35 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-060-zcode | agent/zcode/TASK-060-sqlite-ownership | f7745e64737fb7a824159c3118756a2f93be921f | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-061-qoder-review | agent/qoder/TASK-061-review | be995446db5a3309adcc81ee0e8779abcc79f65e | CLEAN | 0 | 0 | 4 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-061-zcode | agent/zcode/TASK-061-connection-eviction | ffdc47d2893e5ed92c3669e1554745b57de2578f | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-062-codex | agent/codex/TASK-062-posthoc-residuals | 9188fc35d3b779fff6d96bf54989d8084b5cde1c | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-062-qoder-review | agent/qoder/TASK-062-review | 0fe774d5c0da3fcdd1e51721083022fd711a9ce3 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
| G:/CODEX/New Manga.worktrees/TASK-065-codex | agent/codex/TASK-065-task058-followups | 19afba4bbca4c52e4213e870958a7ba5d181ee00 | CLEAN | 0 | 0 | 0 | UNKNOWN | UNKNOWN_DO_NOT_DELETE |
