# Worktree Safety Inventory

Snapshot time: 2026-09-20 (Asia/Shanghai)  
Repository: `G:/CODEX/New Manga`  
Master baseline: `d05b3dbbbf4806df07d2b310683923d5df01f2a5`

No worktree was removed or pruned. Classification is conservative:

- `MUST_PRESERVE`: active workspace or contains tracked/untracked changes.
- `NEEDS_REVIEW`: clean but has commits not reachable from current `master`.
- `SAFE_TO_REMOVE`: clean, task-related, and its HEAD is reachable from `master`; this is only eligibility, not an instruction to delete.
- `UNKNOWN`: clean detached Codex worktree whose related task/ownership is not established.

Summary: 94 linked worktrees — 3 `MUST_PRESERVE`, 9 `NEEDS_REVIEW`, 76 `SAFE_TO_REMOVE`, 6 `UNKNOWN`.

| Path | Branch | HEAD | Git status | Commits not in master | Related work | Disposition |
|---|---|---:|---|---:|---|---|
| `G:/CODEX/New Manga` | `master` | `d05b3db` | 1 tracked, 19 untracked | 0 | `ACTIVE-REBASELINE` | **MUST_PRESERVE** |
| `C:/Users/49745/.codex/worktrees/0e0e/New Manga` | `(detached)` | `98b38b7` | clean | 0 | `UNKNOWN` | **UNKNOWN** |
| `C:/Users/49745/.codex/worktrees/2a13/New Manga` | `(detached)` | `130e04c` | clean | 0 | `UNKNOWN` | **UNKNOWN** |
| `C:/Users/49745/.codex/worktrees/3a4d/New Manga` | `(detached)` | `130e04c` | clean | 0 | `UNKNOWN` | **UNKNOWN** |
| `C:/Users/49745/.codex/worktrees/88b4/New Manga` | `(detached)` | `98b38b7` | clean | 0 | `UNKNOWN` | **UNKNOWN** |
| `C:/Users/49745/.codex/worktrees/97d5/New Manga` | `(detached)` | `132e776` | clean | 0 | `UNKNOWN` | **UNKNOWN** |
| `C:/Users/49745/.codex/worktrees/e8e0/New Manga` | `(detached)` | `132e776` | clean | 0 | `UNKNOWN` | **UNKNOWN** |
| `G:/CODEX/New Manga.worktrees/POSTHOC-WINDOW-2026-09-19-qoder` | `agent/qoder/POSTHOC-WINDOW-2026-09-19` | `86b1518` | clean | 0 | `POSTHOC-WINDOW-2026-09-19-qoder` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-001-deepseek-review` | `agent/deepseek/TASK-001-review` | `6c0a996` | clean | 0 | `TASK-001` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-002-deepseek-review` | `agent/deepseek/TASK-002-review` | `e866ea1` | clean | 0 | `TASK-002` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-003-deepseek` | `agent/deepseek/TASK-003-verification-spec` | `4a76cac` | clean | 0 | `TASK-003` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-004-deepseek-rereview` | `agent/deepseek/TASK-004-rereview-181a356` | `5f4db0f` | clean | 0 | `TASK-004` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-004-deepseek-review` | `agent/deepseek/TASK-004-review` | `020c285` | clean | 1 | `TASK-004` | **NEEDS_REVIEW** |
| `G:/CODEX/New Manga.worktrees/TASK-004-zcode` | `agent/zcode/TASK-004-windows-packaging` | `a370b1e` | clean | 0 | `TASK-004` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-005-codex` | `agent/codex/TASK-005-minimal-bootstrap` | `28ffadc` | clean | 0 | `TASK-005` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-005-deepseek-review` | `agent/deepseek/TASK-005-review` | `118038f` | clean | 0 | `TASK-005` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-005-zcode-audit` | `agent/zcode/TASK-005-audit-metadata` | `9fa6835` | clean | 0 | `TASK-005` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-006-deepseek-review` | `agent/deepseek/TASK-006-review` | `baeef13` | clean | 0 | `TASK-006` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-006-zcode` | `agent/zcode/TASK-006-persistence-artifact` | `af6deef` | clean | 0 | `TASK-006` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-007-deepseek-review` | `agent/deepseek/TASK-007-review` | `25df1ca` | clean | 0 | `TASK-007` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-007-zcode` | `agent/zcode/TASK-007-library-import` | `76328bf` | clean | 0 | `TASK-007` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-008-deepseek-review` | `agent/deepseek/TASK-008-review` | `f9e5977` | clean | 0 | `TASK-008` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-008-zcode` | `agent/zcode/TASK-008-region-editing` | `f7becb4` | clean | 0 | `TASK-008` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-009-deepseek-review` | `agent/deepseek/TASK-009-review` | `d2fe13c` | clean | 0 | `TASK-009` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-009-zcode` | `agent/zcode/TASK-009-provider-network-credentials` | `50b6930` | clean | 0 | `TASK-009` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-010-deepseek-review` | `agent/deepseek/TASK-010-review` | `008b101` | clean | 0 | `TASK-010` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-010-zcode` | `agent/zcode/TASK-010-translation-context` | `05effee` | clean | 0 | `TASK-010` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-011-deepseek-review` | `agent/deepseek/TASK-011-review` | `36f874a` | clean | 0 | `TASK-011` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-012-deepseek-review` | `agent/deepseek/TASK-012-review` | `084db60` | clean | 0 | `TASK-012` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-012-zcode` | `agent/zcode/TASK-012-navigation-library-ui` | `e6fe52a` | clean | 0 | `TASK-012` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-013-deepseek-review` | `agent/deepseek/TASK-013-review` | `8f7c454` | clean | 0 | `TASK-013` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-013-zcode` | `agent/zcode/TASK-013-workbench-task-progress` | `7e50523` | clean | 0 | `TASK-013` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-014-deepseek-review` | `agent/deepseek/TASK-014-review` | `5276a18` | clean | 0 | `TASK-014` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-014-rendering-style` | `agent/zcode/TASK-014-rendering-style` | `a49fc76` | clean | 0 | `TASK-014` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-015-deepseek-posthoc` | `agent/deepseek/TASK-015-posthoc` | `9b77685` | clean | 1 | `TASK-015` | **NEEDS_REVIEW** |
| `G:/CODEX/New Manga.worktrees/TASK-015-zcode` | `agent/zcode/TASK-015-reader-export` | `a915d56` | clean | 0 | `TASK-015` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-016-deepseek` | `agent/deepseek/TASK-016-ocr-detection-experiment` | `8153274` | clean | 0 | `TASK-016` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-016-review-fixed` | `(detached)` | `dfd11b9` | clean | 0 | `TASK-016` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-017-deepseek-posthoc` | `agent/deepseek/TASK-017-posthoc` | `fb0bc40` | clean | 1 | `TASK-017` | **NEEDS_REVIEW** |
| `G:/CODEX/New Manga.worktrees/TASK-017-deepseek-tail` | `agent/deepseek/TASK-017-tail-review` | `e50ba29` | clean | 0 | `TASK-017` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-017-zcode` | `agent/zcode/TASK-017-translation-protocol-experiment` | `387bb1e` | clean | 0 | `TASK-017` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-018-deepseek` | `agent/deepseek/TASK-018-mask-inpainting-experiment` | `c8c2a8e` | clean | 0 | `TASK-018` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-019-deepseek` | `agent/deepseek/TASK-019-provider-integration` | `3929d9e` | clean | 0 | `TASK-019` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-020-zcode` | `agent/zcode/TASK-020-webtoon-chunked-reading` | `40f20e7` | clean | 0 | `TASK-020` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-021-zcode` | `agent/zcode/TASK-021-backup-trash-cleanup-diagnostics` | `79ec0d2` | clean | 0 | `TASK-021` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-023-zcode` | `agent/zcode/TASK-023-pdf-mobi-import` | `c87f21c` | clean | 0 | `TASK-023` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-024-deepseek-posthoc` | `agent/deepseek/TASK-024-posthoc` | `9454cec` | clean | 1 | `TASK-024` | **NEEDS_REVIEW** |
| `G:/CODEX/New Manga.worktrees/TASK-024-zcode` | `agent/zcode/TASK-024-extension-boundaries-design` | `86072c3` | 1 tracked | 0 | `TASK-024` | **MUST_PRESERVE** |
| `G:/CODEX/New Manga.worktrees/TASK-028-deepseek-review` | `agent/deepseek/TASK-028-review` | `09108d1` | clean | 0 | `TASK-028` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-029-deepseek-review` | `agent/deepseek/TASK-029-review` | `9b69f35` | clean | 0 | `TASK-029` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-029-zcode` | `agent/zcode/TASK-029-unified-sqlite-persistence` | `4fcb150` | clean | 0 | `TASK-029` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-030-deepseek-review` | `agent/deepseek/TASK-030-review` | `dba2637` | clean | 0 | `TASK-030` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-030-zcode` | `agent/zcode/TASK-030-main-bootstrap-assembly` | `a64c93a` | clean | 0 | `TASK-030` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-031-deepseek-review` | `agent/deepseek/TASK-031-review` | `0509003` | clean | 0 | `TASK-031` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-032-deepseek` | `agent/deepseek/TASK-032-sfx-policy-gate-region-type` | `ff887db` | clean | 0 | `TASK-032` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-033-deepseek` | `agent/deepseek/TASK-033-full-chain-handlers` | `d322ce2` | clean | 0 | `TASK-033` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-033-zcode` | `agent/zcode/TASK-033-full-chain-handlers` | `401d6d7` | clean | 0 | `TASK-033` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-034-deepseek` | `agent/deepseek/TASK-034-test-layer-hardening` | `132e776` | clean | 0 | `TASK-034` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-035-deepseek` | `agent/deepseek/TASK-035-render-sfx-gate-region-type` | `092957e` | clean | 0 | `TASK-035` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-036-deepseek` | `agent/deepseek/TASK-036-settings-validation-and-export-order` | `5606221` | clean | 0 | `TASK-036` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-037-zcode` | `agent/zcode/TASK-037-flaky-diagnostic-fix` | `7c35277` | clean | 0 | `TASK-037` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-038-zcode` | `agent/zcode/TASK-038-production-assembly` | `fcf791f` | clean | 0 | `TASK-038` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-039-zcode` | `agent/zcode/TASK-039-clean-availability` | `355c123` | clean | 0 | `TASK-039` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-040-zcode` | `agent/zcode/TASK-040-clean-probe-injection` | `9b9c2da` | clean | 0 | `TASK-040` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-041-zcode` | `agent/zcode/TASK-041-mobi-import` | `4d925f3` | clean | 0 | `TASK-041` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-042-zcode` | `agent/zcode/TASK-042-streaming-decode` | `98b38b7` | clean | 0 | `TASK-042` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-043-deepseek` | `agent/deepseek/TASK-043-import-fixes` | `d765f22` | clean | 0 | `TASK-043` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-044-deepseek` | `agent/deepseek/TASK-044-purge-integrity` | `9c7d0fa` | clean | 0 | `TASK-044` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-045-deepseek` | `agent/deepseek/TASK-045-webtoon-display-fixes` | `7261ec7` | clean | 0 | `TASK-045` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-045-posthoc-zcode` | `agent/zcode/TASK-045-posthoc` | `8b47b2e` | clean | 1 | `TASK-045` | **NEEDS_REVIEW** |
| `G:/CODEX/New Manga.worktrees/TASK-046-zcode` | `agent/zcode/TASK-046-decode-rewind-cost` | `60cebc0` | 1 tracked, 2 untracked | 0 | `TASK-046` | **MUST_PRESERVE** |
| `G:/CODEX/New Manga.worktrees/TASK-047-qoder` | `agent/qoder/TASK-047-ui-ux-gui-design` | `980ae7d` | clean | 9 | `TASK-047` | **NEEDS_REVIEW** |
| `G:/CODEX/New Manga.worktrees/TASK-048-zcode` | `agent/zcode/TASK-048-thread-sqlite` | `8dc13eb` | clean | 0 | `TASK-048` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-049-zcode` | `agent/zcode/TASK-049-region-input` | `7aca966` | clean | 0 | `TASK-049` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-050-zcode` | `agent/zcode/TASK-050-settings-bindings` | `e49349b` | clean | 0 | `TASK-050` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-051-zcode` | `agent/zcode/TASK-051-workbench-viewer-modes` | `7299b81` | clean | 0 | `TASK-051` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-052-zcode` | `agent/zcode/TASK-052-command-error-surface` | `78aa598` | clean | 0 | `TASK-052` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-053-zcode` | `agent/zcode/TASK-053-run-files-leak` | `54fbdfc` | clean | 0 | `TASK-053` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-054-zcode` | `agent/zcode/TASK-054-cancel-pending-rename` | `51bc5a5` | clean | 0 | `TASK-054` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-055-zcode` | `agent/zcode/TASK-055-diagnostics` | `763a23c` | clean | 0 | `TASK-055` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-056-zcode` | `agent/zcode/TASK-056-cache-version-cleanup` | `823b2d3` | clean | 0 | `TASK-056` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-057-qoder-review` | `agent/qoder/TASK-057-review` | `257ee5b` | clean | 8 | `TASK-057` | **NEEDS_REVIEW** |
| `G:/CODEX/New Manga.worktrees/TASK-057-zcode` | `agent/zcode/TASK-057-backup-restore` | `29546f7` | clean | 6 | `TASK-057` | **NEEDS_REVIEW** |
| `G:/CODEX/New Manga.worktrees/TASK-058-qoder-review` | `agent/qoder/TASK-058-review` | `d0cac07` | clean | 0 | `TASK-058` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-058-zcode` | `agent/zcode/TASK-058-graceful-shutdown-drain` | `9c8cd52` | clean | 0 | `TASK-058` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-059-codex-review` | `agent/codex/TASK-059-review` | `06064f8` | clean | 0 | `TASK-059` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-059-qoder` | `agent/qoder/TASK-059-ui-redesign` | `6cb0afb` | clean | 0 | `TASK-059` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-059-zcode` | `agent/zcode/TASK-059-ui-redesign` | `58272ab` | clean | 0 | `TASK-059` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-060-qoder-review` | `agent/qoder/TASK-060-review` | `36b886c` | clean | 0 | `TASK-060` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-060-zcode` | `agent/zcode/TASK-060-sqlite-ownership` | `f7745e6` | clean | 0 | `TASK-060` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-061-qoder-review` | `agent/qoder/TASK-061-review` | `be99544` | clean | 4 | `TASK-061` | **NEEDS_REVIEW** |
| `G:/CODEX/New Manga.worktrees/TASK-061-zcode` | `agent/zcode/TASK-061-connection-eviction` | `ffdc47d` | clean | 0 | `TASK-061` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-062-codex` | `agent/codex/TASK-062-posthoc-residuals` | `9188fc3` | clean | 0 | `TASK-062` | **SAFE_TO_REMOVE** |
| `G:/CODEX/New Manga.worktrees/TASK-062-qoder-review` | `agent/qoder/TASK-062-review` | `0fe774d` | clean | 0 | `TASK-062` | **SAFE_TO_REMOVE** |

## Dirty worktree details

### `G:/CODEX/New Manga`

- ` M experiments/TASK-017/README.md`
- `?? .qoder-credits/[@代码审查](skill___fullstac__3a3ee254.canvas.tsx`
- `?? .qoder-credits/[@代码审查](skill___fullstac__617e8c11.canvas.tsx`
- `?? .qoder-credits/[@代码审查](skill___fullstac__6d0bdc2f.canvas.tsx`
- `?? .qoder-credits/[@代码审查](skill___fullstac__6d692ab1.canvas.tsx`
- `?? .qoder-credits/[@代码审查](skill___fullstac__92364678.canvas.tsx`
- `?? .qoder-credits/[@代码审查](skill___fullstac__f77fdd01.canvas.tsx`
- `?? .qoder-credits/[@代码审查](skill___fullstac__fce86d6b.canvas.tsx`
- `?? .qoder-credits/report.json`
- `?? .qoder-credits/接下来的任务不要保存在项目目录，另存在项目之外，__0f61192d.canvas.tsx`
- `?? .qoder-credits/接下来的任务不要保存在项目目录，另存在项目之外，__1a7ff85c.canvas.tsx`
- `?? .qoder-credits/接下来的任务不要保存在项目目录，另存在项目之外，__91b88c8d.canvas.tsx`
- `?? .qoder-credits/接下来的任务不要保存在项目目录，另存在项目之外，__a97ca706.canvas.tsx`
- `?? .qoder-credits/接下来的任务不要保存在项目目录，另存在项目之外，__c6f27d5d.canvas.tsx`
- `?? .qoder-credits/接下来的任务不要保存在项目目录，另存在项目之外，__e02c94b5.canvas.tsx`
- `?? .qoder-credits/这个是什么，有什么用，怎么用。请详细说明。不改动__17858942.canvas.tsx`
- `?? .qoder-credits/这个是什么，有什么用，怎么用。请详细说明。不改动__279dc059.canvas.tsx`
- `?? .qoder-credits/这个是什么，有什么用，怎么用。请详细说明。不改动__2e6401a8.canvas.tsx`
- `?? .qoder-credits/这个是什么，有什么用，怎么用。请详细说明。不改动__a3e3bbc8.canvas.tsx`
- `?? .qoder-credits/这个是什么，有什么用，怎么用。请详细说明。不改动__eab0bb7c.canvas.tsx`

### `G:/CODEX/New Manga.worktrees/TASK-024-zcode`

- ` M verification/TASK-024/author-verification.md`

### `G:/CODEX/New Manga.worktrees/TASK-046-zcode`

- ` M doc/reviews/TASK-046-7bf476b.md`
- `?? verification/TASK-046/review-7bf476b/post-integration-full-suite-2b40085.log`
- `?? verification/TASK-046/review-7bf476b/run_suite_at.ps1`

## Disposition rule

No removal is authorized by this inventory alone. Before any later removal, refresh status, confirm ownership, and re-check reachability against the then-current master. Never substitute `git worktree prune` for that review.

