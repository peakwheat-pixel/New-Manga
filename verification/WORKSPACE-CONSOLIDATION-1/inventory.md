# 工作区整理盘点（AC1 四表）

生成：`tools/governance/consolidate.py`（只读），2026-10-20。
主 checkout：`G:\CODEX\New Manga`，HEAD `62303a576`，主线 `antigravity/P09-AC3-DELETE-HARDEN-1`。

## 一、总量

| 项 | 数 |
|---|---:|
| 本地分支 | **418** |
| 已并入主线 | 342 |
| **未并入主线** | **76** |
| 已注册 worktree | **213** |
| 受保护 worktree 名 | **57** |
| 受保护且在注册表中 | 57 |
| 非保护且干净无 stash | 87 |

## 二、分支表（未并入主线的 76 条，按独有提交数降序）

| 分支 | 独有提交 | tip 日期 | worktree 检出 |
|---|---:|---|---|
| `agent/zcode/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` | 78 | 2026-10-14 | P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION |
| `agent/zcode/T3.2.1-repair-13` | 64 | 2026-09-25 | T3.2.1-zcode-repair-13 |
| `agent/zcode/P02-NEW-TIME-BASELINE` | 60 | 2026-10-14 | P02-NEW-TIME-BASELINE |
| `agent/antigravity/T3.2.1-repair-12` | 54 | 2026-09-24 | T3.2.1-antigravity-repair-11 |
| `agent/deepseek/T3.2.1-review-a2f6695` | 54 | 2026-09-24 | T3.2.1-deepseek-review-12 |
| `agent/qoder/T3.2.1-repair-13` | 54 | 2026-09-24 | T3.2.1-qoder-repair-13 |
| `agent/antigravity/T3.2.1-repair-11` | 53 | 2026-09-24 | — |
| `agent/deepseek/T3.2.1-review-9622395` | 53 | 2026-09-24 | T3.2.1-deepseek-review-11 |
| `codex/T3.2.1-release-gate-closeout` | 50 | 2026-09-24 | T3.2.1-codex-release-gate-closeout |
| `agent/antigravity/T3.2.1-repair-10` | 49 | 2026-09-24 | T3.2.1-antigravity-repair-10 |
| `agent/deepseek/T3.2.1-review-be5200e` | 49 | 2026-09-24 | T3.2.1-deepseek-review-10 |
| `agent/antigravity/T3.2.1-repair-9` | 46 | 2026-09-24 | T3.2.1-antigravity-repair-9 |
| `agent/deepseek/T3.2.1-review-d2bf6a8` | 46 | 2026-09-24 | T3.2.1-deepseek-review-9 |
| `agent/zcode/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` | 43 | 2026-10-14 | P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION |
| `agent/antigravity/T3.2.1-repair-7` | 41 | 2026-09-23 | T3.2.1-antigravity-repair-7 |
| `agent/deepseek/T3.2.1-review-f6dc383` | 31 | 2026-09-23 | T3.2.1-deepseek-review-f6dc383 |
| `agent/zcode/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | 31 | 2026-10-14 | P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION |
| `agent/antigravity/T3.2.1-repair-6` | 30 | 2026-09-23 | T3.2.1-antigravity-repair-6 |
| `agent/antigravity/T3.2.1-repair-5` | 25 | 2026-09-23 | T3.2.1-antigravity-repair-5 |
| `agent/antigravity/T3.2.1-repair-4` | 19 | 2026-09-23 | T3.2.1-antigravity-repair-4 |
| `agent/codex/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE` | 18 | 2026-10-13 | P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE |
| `codex/integration-p02pre-r1h-p2-1-external-harness-trace` | 18 | 2026-10-13 | — |
| `agent/codex/M2-C1-typed-ipc-contract` | 16 | 2026-09-26 | M2-C1-codex-typed-ipc-contract |
| `agent/antigravity/P02PRE-R1H-H2-COLLECTOR-R3` | 15 | 2026-10-13 | P02PRE-R1H-H2-COLLECTOR-ANTIGRAVITY-R3 |
| `agent/antigravity/T3.2.1-repair-3` | 15 | 2026-09-23 | T3.2.1-antigravity-repair-3 |
| `review/qoder/M2-C1-typed-ipc-r3-4d66523` | 15 | 2026-09-26 | M2-C1-qoder-review-r3-4d66523 |
| `agent/deepseek/T3.2.1-review-d79d7dd` | 14 | 2026-09-23 | T3.2.1-deepseek-review-d79d7dd |
| `review/deepseek/M2-C1-typed-ipc-r3-4d66523` | 14 | 2026-09-26 | M2-C1-deepseek-review-r3-4d66523 |
| `agent/codex/P02PRE-R1H` | 13 | 2026-10-12 | p02pre-r1h-codex |
| `review/deepseek/M2-C1-typed-ipc-r2-7e65f4f` | 12 | 2026-09-26 | M2-C1-deepseek-review-r2-7e65f4f |
| `agent/antigravity/P22-roundtrip-serialization` | 10 | 2026-10-10 | P22-roundtrip-serialization-antigravity |
| `agent/qoder/TASK-047-ui-ux-gui-design` | 9 | 2026-09-19 | TASK-047-qoder |
| `agent/antigravity/T3.2.1-windows-packaging` | 8 | 2026-09-23 | T3.2.1-antigravity-packaging |
| `agent/antigravity/P02PRE-R1H` | 7 | 2026-10-12 | — |
| `agent/zcode/P02PRE-R1H` | 7 | 2026-10-12 | p02pre-r1h-zcode |
| `codex/P02-hook-cache-isolation-plan` | 7 | 2026-10-09 | P02-hook-cache-isolation-plan-codex |
| `agent/antigravity/P02PRE-R1G` | 6 | 2026-10-12 | — |
| `agent/deepseek/T3.2.1-review-cdc0b6f` | 6 | 2026-09-23 | T3.2.1-deepseek-review-cdc0b6f |
| `agent/deepseek/T3.2.1-review-repair-7` | 6 | 2026-09-23 | T3.2.1-deepseek-review-repair-7 |
| `agent/deepseek/T3.2.1-review-repair-14-r2` | 5 | 2026-09-25 | T3.2.1-deepseek-review-repair-14-r2 |
| `agent/qoder/T2.2.1-reader-workbench-qml` | 5 | 2026-09-22 | T2.2.1-qoder |
| `agent/antigravity/T3.2.1-repair-14` | 4 | 2026-09-25 | T3.2.1-antigravity-repair-14 |
| `agent/codex/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW` | 4 | 2026-10-13 | P02PRE-R1H-H1-CURRENT-INPUT-REVIEW |
| `agent/qoder/TASK-061-review` | 4 | 2026-09-19 | TASK-061-qoder-review |
| `agent/zcode/P02PRE-R1H-H2-COLLECTOR` | 4 | 2026-10-13 | P02PRE-R1H-H2-COLLECTOR |
| `review/deepseek/M2-C1-typed-ipc-7d908a5` | 4 | 2026-09-26 | M2-C1-deepseek-review-7d908a5 |
| `agent/codex/P02PRE-R1H-FORENSIC-RECOVERY-INTEGRATION` | 3 | 2026-10-13 | P02PRE-R1H-FORENSIC-RECOVERY-INTEGRATION |
| `agent/codex/P02PRE-R1H-H2-RUN-INTEGRATION` | 3 | 2026-10-13 | P02PRE-R1H-H2-RUN-INTEGRATION |
| `agent/deepseek/T3.2.1-review-repair-14` | 3 | 2026-09-25 | T3.2.1-deepseek-review-repair-14 |
| `codex/FEAT-CREATE-1` | 3 | 2026-10-17 | FEAT-CREATE-1 |
| `master` | 3 | 2026-09-27 | M2-UI1-integration-final-83a |
| `agent/antigravity/P02PRE-R1H-R6-A4` | 2 | 2026-10-12 | p02pre-r1h-r6-attempt4-antigravity |
| `agent/codex/T1.2.1-integration` | 2 | 2026-09-22 | — |
| `agent/codex/TASK-013-production-pipeline-seam` | 2 | 2026-09-16 | — |
| `agent/qoder/T1.1.2-region-canvas` | 2 | 2026-09-21 | TASK-013-qoder |
| `codex/P14` | 2 | 2026-10-16 | P14 |
| `codex/P15-C1-FU2` | 2 | 2026-10-17 | P15-C1-FU2 |
| `dsh/GOV-PIN-LINEAGE-1` | 2 | 2026-10-20 | worktree |
| `agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG` | 1 | 2026-10-08 | PACKAGED-AC1-DLL-DIAG-dsh |
| `agent/deepseek/T1.1.1-detector-evaluation` | 1 | 2026-09-21 | T1.1.1-detector-evaluation |
| `agent/deepseek/T3.2.1-review-740503e` | 1 | 2026-09-23 | T3.2.1-deepseek-review-740503e |
| `agent/deepseek/T3.2.1-review-7d687f5` | 1 | 2026-09-23 | T3.2.1-deepseek-review-7d687f5 |
| `agent/deepseek/T3.2.1-review-92c9307c` | 1 | 2026-09-23 | T3.2.1-deepseek-review-92c9307c |
| `agent/deepseek/T3.2.1-review-f39ddc0` | 1 | 2026-09-23 | T3.2.1-deepseek-review-f39ddc0 |
| `agent/deepseek/TASK-004-review` | 1 | 2026-09-14 | TASK-004-deepseek-review |
| `agent/deepseek/TASK-015-posthoc` | 1 | 2026-09-17 | TASK-015-deepseek-posthoc |
| `agent/deepseek/TASK-017-posthoc` | 1 | 2026-09-17 | TASK-017-deepseek-posthoc |
| `agent/deepseek/TASK-024-posthoc` | 1 | 2026-09-17 | TASK-024-deepseek-posthoc |
| `agent/zcode/M2-I1-core-assembly-seam` | 1 | 2026-09-25 | M2-I1-zcode |
| `agent/zcode/T1.2.1-settings-ui-viewmodel` | 1 | 2026-09-22 | T1.2.1-settings-ui-viewmodel |
| `agent/zcode/T2.2.1-reader-workbench-polish` | 1 | 2026-09-22 | T2.2.1-zcode |
| `agent/zcode/TASK-045-posthoc` | 1 | 2026-09-19 | TASK-045-posthoc-zcode |
| `codex/P02-fallback-scope` | 1 | 2026-10-09 | P02-fallback-scope-codex |
| `codex/project-roadmap-rebaseline` | 1 | 2026-10-15 | PROJECT-ROADMAP-REBASELINE |
| `codex/rebaseline-audit-20260921` | 1 | 2026-09-21 | — |
| `review/deepseek/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r2` | 1 | 2026-10-08 | RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-dsh-r2 |

## 三、worktree 表（受保护者）

| 路径 | 分支 | 保护来源数 |
|---|---|---:|
| `G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE` | `codex/arch-doc-rebaseline` | 1 |
| `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1` | `codex/ENV-BUNDLE-1-sidecar-rebuild` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1` | `codex/ENV-BUNDLE-1-FU1-packaged-acceptance` | 7 |
| `G:/CODEX/New Manga.workspace/worktrees/EVENTS-FWD-1` | `agent/antigravity/EVENTS-FWD-1` | 4 |
| `G:/CODEX/New Manga.workspace/worktrees/EXPORT-IPC-1` | `agent/antigravity/EXPORT-IPC-1` | 4 |
| `G:/CODEX/New Manga.workspace/worktrees/EXPORT-REVEAL-1` | `codex/EXPORT-REVEAL-1` | 5 |
| `G:/CODEX/New Manga.workspace/worktrees/HOST-CORE-1` | `codex/HOST-CORE-1-hostcontrol-handler` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1` | `codex/HOST-ISSUER-1-tauri-ref-issuer` | 4 |
| `G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1-C1` | `codex/HOST-ISSUER-1-C1-grant-registration-contract` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/HOST-TTL-BOUNDARY-1` | `codex/HOST-TTL-BOUNDARY-1-grant-ttl` | 3 |
| `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE` | `agent/zcode/P02-NEW-TIME-BASELINE` | 1 |
| `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | 5 |
| `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` | 3 |
| `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` | 1 |
| `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6` | `agent/zcode/P02-NEW-TIME-X6` | 4 |
| `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-ANTIGRAVITY` | `agent/antigravity/P02-NEW-TIME-X6-AC1-AC7` | 3 |
| `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-INTEGRATION` | `codex/p02-mainline-closeout-20261015` | 4 |
| `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO` | `agent/antigravity/P02-NEW-TIME-X6-BUILD-CARGO` | 6 |
| `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO-DSH-REVIEW` | `(detached)` | 1 |
| `G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-FORENSIC-RECOVERY-INTEGRATION` | `agent/codex/P02PRE-R1H-FORENSIC-RECOVERY-INTEGRATION` | 1 |
| `G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW` | `agent/codex/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW` | 1 |
| `G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR-ANTIGRAVITY-R3` | `agent/antigravity/P02PRE-R1H-H2-COLLECTOR-R3` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR-INTEGRATION` | `(detached)` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-RUN-INTEGRATION` | `agent/codex/P02PRE-R1H-H2-RUN-INTEGRATION` | 1 |
| `G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE` | `agent/codex/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE` | 1 |
| `G:/CODEX/New Manga.workspace/worktrees/P06-GC-DISTRIBUTION-MIGRATION` | `codex/P06-gc-distribution-migration-evidence` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P09-FU1-DECODER-TEST` | `codex/P09-FU1-decoder-test-baseline` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P09-FU2-IMPORT-IPC-RUNTIME` | `codex/P09-FU2-import-ipc-runtime` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P09-IMPORT-CORE` | `codex/P09-import-core` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P10-CREDENTIAL-CONFIG-CONTRACT` | `codex/P10-credential-config-contract` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P11-LONG-TASK-LIFECYCLE-CONTRACT` | `codex/P11-long-task-lifecycle-contract` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P12` | `agent/antigravity/P12-bookshelf-ui` | 3 |
| `G:/CODEX/New Manga.workspace/worktrees/P12-C1-IMPORT-IPC` | `codex/P12-C1-import-ipc-contract` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P13-C1-RUNTIME-IPC` | `codex/P13-C1-runtime-ipc-contract` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P13-RUN-RUNTIME` | `codex/P13-run-runtime-control-recovery` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P14` | `codex/P14` | 4 |
| `G:/CODEX/New Manga.workspace/worktrees/P15` | `zcode/P15` | 5 |
| `G:/CODEX/New Manga.workspace/worktrees/P15-C1` | `antigravity/P15-C1` | 4 |
| `G:/CODEX/New Manga.workspace/worktrees/P15-C1-FU1` | `codex/P15-C1-FU1` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P15-C1-FU2` | `codex/P15-C1-FU2` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1` | `codex/P15-CORE-1` | 1 |
| `G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1A` | `codex/P15-CORE-1A` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1B` | `codex/P15-CORE-1B` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1C` | `codex/P15-CORE-1C` | 1 |
| `G:/CODEX/New Manga.workspace/worktrees/P15-HOST-1` | `codex/P15-HOST-1` | 1 |
| `G:/CODEX/New Manga.workspace/worktrees/P15-HOST-2` | `codex/P15-HOST-2` | 1 |
| `G:/CODEX/New Manga.workspace/worktrees/P16-C1-READER-EXPORT-IPC` | `codex/P16-C1-reader-export-ipc-contract` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P16-READER-EXPORT-CORE` | `codex/P16-reader-export-core` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P17` | `agent/antigravity/P17` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P18-JA-KO-QUALITY` | `codex/P18-ja-ko-quality-qualification` | 2 |
| `G:/CODEX/New Manga.workspace/worktrees/P19-BOOT-1` | `codex/P19-BOOT-1` | 3 |
| `G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-1` | `codex/P19-UI-FIX-1` | 1 |
| `G:/CODEX/New Manga.workspace/worktrees/P22-REBASE-1` | `codex/p22-rebase-1` | 7 |
| `G:/CODEX/New Manga.workspace/worktrees/PROJECT-ROADMAP-RELEASE-REVIEW` | `(detached)` | 1 |
| `G:/CODEX/New Manga.workspace/worktrees/READER-IPC-1` | `codex/READER-IPC-1` | 4 |
| `G:/CODEX/New Manga.workspace/worktrees/RUN-IPC-1` | `agent/dsh/RUN-IPC-1` | 4 |
| `G:/CODEX/New Manga.workspace/worktrees/UI-DESIGN-1` | `agent/zcode/UI-DESIGN-1` | 2 |

## 四、可清理候选（非保护 且 干净 且 无 stash）

| 路径 | 分支 | 脏条目 | stash |
|---|---|---:|---:|
| `C:/Users/49745/.codex/worktrees/P02-hook-cache-review-dsh-r4` | `(detached)` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/P02-preflight-r4-condition-closure-92dc7361-review-dsh` | `review/deepseek/P02-preflight-r4-condition-closure-92dc7361` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/P02-preflight-r5-844aec28-review-dsh` | `review/deepseek/P02-preflight-r5-844aec28` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/P02-preflight-review-dsh-r1` | `(detached)` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r1` | `(detached)` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r2` | `(detached)` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r3` | `(detached)` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r4` | `(detached)` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r5` | `(detached)` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r6` | `(detached)` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r6-followup` | `(detached)` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r7` | `(detached)` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/p02-post-review-preflight-review-r2/New Manga` | `(detached)` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/p02-post-review-preflight-review/New Manga` | `(detached)` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/p02-r2-docs-closeout/New Manga` | `codex/P02-r2-docs-closeout` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/p02pre-r1h-codex` | `agent/codex/P02PRE-R1H` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/p02pre-r1h-r6-attempt4-antigravity` | `agent/antigravity/P02PRE-R1H-R6-A4` | 0 | 0 |
| `C:/Users/49745/.codex/worktrees/p02pre-r1h-zcode` | `agent/zcode/P02PRE-R1H` | 0 | 0 |
| `G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree` | `dsh/GOV-PIN-LINEAGE-1` | 0 | 0 |
| `G:/CODEX/New Manga.workspace/P06-GC-DISTRIBUTION-MIGRATION/old-runtime/worktree` | `(detached)` | 0 | 0 |
| `G:/CODEX/New Manga.workspace/P09-BASELINE-T2` | `(detached)` | 0 | 0 |
| `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-1` | `codex/FEAT-CREATE-1` | 0 | 0 |
| `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-2` | `codex/FEAT-CREATE-2` | 0 | 0 |
| `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-4` | `codex/FEAT-CREATE-4` | 0 | 0 |
| `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7` | `agent/zcode/P02-NEW-TIME-X6-AC1-AC7` | 0 | 0 |
| `G:/CODEX/New Manga.workspace/worktrees/P15-C1-review` | `(detached)` | 0 | 0 |
| `G:/CODEX/New Manga.workspace/worktrees/P19-AC3-1` | `codex/P19-AC3-1` | 0 | 0 |
| `G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-2` | `codex/P19-UI-FIX-2` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/M2-C1-codex-typed-ipc-contract` | `agent/codex/M2-C1-typed-ipc-contract` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/M2-C1-deepseek-review-r2-7e65f4f` | `review/deepseek/M2-C1-typed-ipc-r2-7e65f4f` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/M2-C1-deepseek-review-r3-4d66523` | `review/deepseek/M2-C1-typed-ipc-r3-4d66523` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/M2-C1-qoder-review-r3-4d66523` | `review/qoder/M2-C1-typed-ipc-r3-4d66523` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/M2-I1-zcode` | `agent/zcode/M2-I1-core-assembly-seam` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode` | `agent/zcode/M2-SFX-ANNOTATE-R2` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/M2-SFX-CORRECTION-EXPORTER-zcode` | `agent/zcode/M2-SFX-CORRECTION-EXPORTER` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/M2-SFX-DATA-INFRA-zcode` | `agent/zcode/M2-SFX-DATA-INFRA` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/M2-SFX-SYNTH-BG-AUTO-zcode` | `agent/zcode/M2-SFX-SYNTH-BG-AUTO` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/M2-UI1-integration-final-83a` | `master` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/P02-build-preflight-codex` | `codex/P02-build-preflight` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/P02-fallback-scope-codex` | `codex/P02-fallback-scope` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/P02-harness-scope` | `codex/P02-harness-scope` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/P02-hook-cache-review-dsh` | `(detached)` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/P02-owner-amendment-codex` | `codex/P02-owner-amendment` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/P02-owner-transfer-integration-codex` | `codex/P02-owner-transfer-integration` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/P02-process-isolation-review-dsh-r7` | `(detached)` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity` | `agent/antigravity/P02-real-webview-harness` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/P03-review-prep-112495c7` | `(detached)` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/P04-prod-command-concurrency-antigravity` | `agent/antigravity/P04-prod-command-concurrency` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/P04-scope-freeze` | `codex/P04-scope-freeze` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh` | `agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T1.1.1-detector-evaluation` | `agent/deepseek/T1.1.1-detector-evaluation` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T1.2.1-settings-ui-viewmodel` | `agent/zcode/T1.2.1-settings-ui-viewmodel` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T2.2.1-qoder` | `agent/qoder/T2.2.1-reader-workbench-qml` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-packaging` | `agent/antigravity/T3.2.1-windows-packaging` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-10` | `agent/antigravity/T3.2.1-repair-10` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-11` | `agent/antigravity/T3.2.1-repair-12` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-14` | `agent/antigravity/T3.2.1-repair-14` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-3` | `agent/antigravity/T3.2.1-repair-3` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-4` | `agent/antigravity/T3.2.1-repair-4` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-5` | `agent/antigravity/T3.2.1-repair-5` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-6` | `agent/antigravity/T3.2.1-repair-6` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-7` | `agent/antigravity/T3.2.1-repair-7` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-9` | `agent/antigravity/T3.2.1-repair-9` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-codex-release-gate-closeout` | `codex/T3.2.1-release-gate-closeout` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-10` | `agent/deepseek/T3.2.1-review-be5200e` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-11` | `agent/deepseek/T3.2.1-review-9622395` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-12` | `agent/deepseek/T3.2.1-review-a2f6695` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-740503e` | `agent/deepseek/T3.2.1-review-740503e` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-7d687f5` | `agent/deepseek/T3.2.1-review-7d687f5` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-9` | `agent/deepseek/T3.2.1-review-d2bf6a8` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-92c9307c` | `agent/deepseek/T3.2.1-review-92c9307c` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-cdc0b6f` | `agent/deepseek/T3.2.1-review-cdc0b6f` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-d79d7dd` | `agent/deepseek/T3.2.1-review-d79d7dd` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-f39ddc0` | `agent/deepseek/T3.2.1-review-f39ddc0` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-f6dc383` | `agent/deepseek/T3.2.1-review-f6dc383` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-repair-14` | `agent/deepseek/T3.2.1-review-repair-14` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-repair-14-r2` | `agent/deepseek/T3.2.1-review-repair-14-r2` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-deepseek-review-repair-7` | `agent/deepseek/T3.2.1-review-repair-7` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/T3.2.1-qoder-repair-13` | `agent/qoder/T3.2.1-repair-13` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/TASK-004-deepseek-review` | `agent/deepseek/TASK-004-review` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/TASK-013-qoder` | `agent/qoder/T1.1.2-region-canvas` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/TASK-015-deepseek-posthoc` | `agent/deepseek/TASK-015-posthoc` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/TASK-017-deepseek-posthoc` | `agent/deepseek/TASK-017-posthoc` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/TASK-024-deepseek-posthoc` | `agent/deepseek/TASK-024-posthoc` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/TASK-045-posthoc-zcode` | `agent/zcode/TASK-045-posthoc` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/TASK-047-qoder` | `agent/qoder/TASK-047-ui-ux-gui-design` | 0 | 0 |
| `G:/CODEX/New Manga.worktrees/TASK-061-qoder-review` | `agent/qoder/TASK-061-review` | 0 | 0 |

## 五、带改动因而不得清理的 worktree

| 路径 | 分支 | 脏条目 | stash | protected |
|---|---|---:|---:|---|
| `C:/Users/49745/AppData/Local/Temp/diag002-s2-2jWfPm` | `(detached)` | 2804 | 0 | no |
| `C:/Users/49745/AppData/Local/Temp/diag002-s2v4-FTf6BC` | `(detached)` | 2804 | 0 | no |
| `C:/Users/49745/AppData/Local/Temp/diag002-s2v5-WJGAfi` | `(detached)` | 2804 | 0 | no |
| `G:/CODEX/New Manga` | `antigravity/P09-AC3-DELETE-HARDEN-1` | 1237 | 0 | no |
| `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE` | `agent/zcode/P02-NEW-TIME-BASELINE` | 88 | 0 | yes |
| `G:/CODEX/New Manga.workspace/worktrees/P15-HOST-2` | `codex/P15-HOST-2` | 64 | 0 | yes |
| `G:/CODEX/New Manga.worktrees/P22-roundtrip-serialization-antigravity` | `agent/antigravity/P22-roundtrip-serialization` | 57 | 0 | no |
| `G:/CODEX/New Manga.workspace/worktrees/FEAT-IMPORT-MULTI-1` | `codex/FEAT-IMPORT-MULTI-1` | 50 | 0 | no |
| `G:/CODEX/New Manga.workspace/worktrees/P14-review` | `(detached)` | 40 | 0 | no |
| `G:/CODEX/New Manga.workspace/worktrees/P15-review` | `(detached)` | 40 | 0 | no |
| `G:/CODEX/New Manga/.agents/worktrees/P19-UI-MANIFEST-VIEW-1` | `P19-UI-MANIFEST-VIEW-1` | 34 | 0 | no |
| `G:/CODEX/New Manga/.agents/worktrees/GOV-PLAN-BUDGET-1` | `GOV-PLAN-BUDGET-1` | 33 | 0 | no |
| `G:/CODEX/New Manga/.agents/worktrees/GOV-RESOURCE-MANIFEST-JSON-1` | `GOV-RESOURCE-MANIFEST-JSON-1` | 33 | 0 | no |
| `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-POSTRUN-REVIEW` | `agent/codex/P02-NEW-TIME-X6-POSTRUN-REVIEW` | 28 | 0 | no |
| `G:/CODEX/New Manga.workspace/worktrees/PROJECT-ROADMAP-REBASELINE` | `codex/project-roadmap-rebaseline` | 27 | 0 | no |
| `G:/CODEX/New Manga.workspace/worktrees/RUN-IPC-1` | `agent/dsh/RUN-IPC-1` | 26 | 0 | yes |
| `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-zcode` | `agent/zcode/P02-real-webview-harness` | 26 | 0 | no |
| `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO` | `agent/antigravity/P02-NEW-TIME-X6-BUILD-CARGO` | 25 | 0 | yes |
| `G:/CODEX/New Manga.workspace/worktrees/P22-REBASE-1` | `codex/p22-rebase-1` | 25 | 0 | yes |
| `G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode` | `agent/zcode/M2-DERIVED-GC-2` | 24 | 0 | no |
| `G:/CODEX/New Manga.worktrees/RC4-integration` | `codex/rc4-integration` | 21 | 0 | no |
| `G:/CODEX/New Manga.worktrees/M2-AC5-BUILD-FRESH-CHECKOUT-zcode` | `agent/zcode/M2-AC5-BUILD-FRESH-CHECKOUT` | 14 | 0 | no |
| `G:/CODEX/New Manga.worktrees/M2-FIX-DIGEST-SEEK-2GIB-zcode` | `agent/zcode/M2-FIX-DIGEST-SEEK-2GIB` | 14 | 0 | no |
| `G:/CODEX/New Manga.worktrees/P01-closeout-review-antigravity` | `(detached)` | 12 | 0 | no |
| `G:/CODEX/New Manga.worktrees/P02-hook-cache-isolation-plan-codex` | `codex/P02-hook-cache-isolation-plan` | 10 | 0 | no |
| `G:/CODEX/New Manga.worktrees/P02-stage-a-validation-38672473-exact` | `(detached)` | 9 | 0 | no |
| `G:/CODEX/New Manga.worktrees/P02-stage-a-validation-38959ba99-exact` | `(detached)` | 9 | 0 | no |
| `G:/CODEX/New Manga.worktrees/P02-stage-a-validation-172eee84-full` | `(detached)` | 8 | 0 | no |
| `C:/Users/49745/.codex/worktrees/p02-r2-docs-closeout-review/New Manga` | `(detached)` | 7 | 0 | no |
| `C:/Users/49745/.codex/worktrees/p02-r2-docs-fixes-review` | `(detached)` | 7 | 0 | no |
| `C:/Users/49745/.codex/worktrees/p04-prod-command-concurrency-review` | `(detached)` | 7 | 0 | no |
| `G:/CODEX/New Manga.worktrees/P02-stage-a-validation-cc1bd750-full` | `(detached)` | 7 | 0 | no |
| `C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r2` | `(detached)` | 6 | 0 | no |
| `G:/CODEX/New Manga.worktrees/M2-SETTINGS-IPC-CHANNEL-zcode` | `agent/zcode/M2-SETTINGS-IPC-CHANNEL` | 6 | 0 | no |
| `C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r3` | `(detached)` | 5 | 0 | no |
| `C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r4` | `(detached)` | 5 | 0 | no |
| `G:/CODEX/New Manga.workspace/worktrees/SEC-FIX-PATH-ECHO-1` | `codex/SEC-FIX-PATH-ECHO-1` | 5 | 0 | no |
| `G:/CODEX/New Manga.worktrees/P01-c8-review-dsh` | `(detached)` | 5 | 0 | no |
| `G:/CODEX/New Manga.worktrees/P01-c9-review-antigravity` | `(detached)` | 5 | 0 | no |
| `G:/CODEX/New Manga.worktrees/P02-stage-a-validation-172eee84-probe` | `(detached)` | 5 | 0 | no |
| `G:/CODEX/New Manga.worktrees/P02-stage-a-validation-5fa8a41f` | `(detached)` | 5 | 0 | no |
| `G:/CODEX/New Manga.worktrees/P02-stage-a-validation-9b82e97b` | `(detached)` | 5 | 0 | no |
| `C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r1` | `(detached)` | 4 | 0 | no |
| `G:/CODEX/New Manga.workspace/worktrees/P14` | `codex/P14` | 4 | 0 | yes |
| `G:/CODEX/New Manga.worktrees/M2-C1-deepseek-review-7d908a5` | `review/deepseek/M2-C1-typed-ipc-7d908a5` | 4 | 0 | no |
| `G:/CODEX/New Manga.worktrees/P02-stage-a-validation-cc1bd750-probe` | `(detached)` | 4 | 0 | no |
| `C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r5` | `(detached)` | 3 | 0 | no |
| `C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r5-followup` | `(detached)` | 3 | 0 | no |
| `C:/Users/49745/.codex/worktrees/P02-preflight-r4-083d2b47-review-dsh` | `review/deepseek/P02-preflight-r4-083d2b47` | 3 | 0 | no |
| `C:/Users/49745/.codex/worktrees/p02pre-r1h-r6-exec-a6-antigravity/New Manga` | `agent/antigravity/P02PRE-R1H-R6-EXEC-A6` | 3 | 0 | no |
| `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | 3 | 0 | yes |
| `G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1` | `codex/P15-CORE-1` | 3 | 0 | yes |
| `G:/CODEX/New Manga.worktrees/P02-stage-a-validation-172eee84-failureprobe` | `(detached)` | 3 | 0 | no |
| `G:/CODEX/New Manga.worktrees/P03-packaged-sfx-entry-antigravity` | `agent/antigravity/P03-packaged-sfx-entry` | 3 | 0 | no |
| `G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-dsh-r2` | `review/deepseek/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r2` | 3 | 0 | no |
| `G:/CODEX/New Manga.worktrees/T3.2.1-zcode-repair-13` | `agent/zcode/T3.2.1-repair-13` | 3 | 0 | no |
| `G:/CODEX/New Manga.worktrees/TASK-046-zcode` | `agent/zcode/TASK-046-decode-rewind-cost` | 3 | 0 | no |
| `C:/Users/49745/.codex/worktrees/M2-C1-dsh-review-7de1cd2-r2` | `review/deepseek/M2-C1-zcode-7de1cd2-r2` | 2 | 0 | no |
| `G:/CODEX/New Manga/.agents/worktrees/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1` | `GOV-RESOURCE-MANIFEST-SAME-LOCATION-1` | 2 | 0 | no |
| `G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR` | `agent/zcode/P02PRE-R1H-H2-COLLECTOR` | 2 | 0 | no |
| `G:/CODEX/New Manga.workspace/worktrees/P15` | `zcode/P15` | 2 | 0 | yes |
| `G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-3` | `codex/P19-UI-FIX-3` | 2 | 0 | no |
| `G:/CODEX/New Manga.worktrees/M2-C1-dsh-review-7de1cd2` | `review/deepseek/M2-C1-zcode-7de1cd2` | 2 | 0 | no |
| `G:/CODEX/New Manga.worktrees/M2-C2-zcode` | `agent/zcode/M2-C2-typed-ipc-contract-revision` | 2 | 0 | no |
| `G:/CODEX/New Manga.worktrees/P03-review-prep-85482c5b` | `codex/P03-integration-4c04459` | 2 | 0 | no |
| `G:/CODEX/New Manga.worktrees/PAGE-NAV-1` | `zcode/page-nav-projection-1` | 2 | 0 | no |
| `G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-dsh-r1` | `review/deepseek/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r1` | 2 | 0 | no |
| `C:/Users/49745/.codex/worktrees/m2-i2-review-a4705a9/New Manga` | `(detached)` | 1 | 0 | no |
| `C:/Users/49745/.codex/worktrees/p02-d27-review-repair-review` | `(detached)` | 1 | 0 | no |
| `C:/Users/49745/.codex/worktrees/P02-preflight-r6-c85a041c-review-dsh` | `review/deepseek/P02-preflight-r6-c85a041c` | 1 | 0 | no |
| `G:/CODEX/New Manga.workspace/worktrees/EXPORT-REVEAL-1` | `codex/EXPORT-REVEAL-1` | 1 | 0 | yes |
| `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-3` | `codex/FEAT-CREATE-3` | 1 | 0 | no |
| `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-ANTIGRAVITY` | `agent/antigravity/P02-NEW-TIME-X6-AC1-AC7` | 1 | 0 | yes |
| `G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1C` | `codex/P15-CORE-1C` | 1 | 0 | yes |
| `G:/CODEX/New Manga.workspace/worktrees/READER-IPC-1` | `codex/READER-IPC-1` | 1 | 0 | yes |
| `G:/CODEX/New Manga.workspace/worktrees/RUN-IPC-1-review` | `(detached)` | 1 | 0 | no |
| `G:/CODEX/New Manga.worktrees/M2-C1-qoder-review-7de1cd2` | `review/qoder/M2-C1-zcode-7de1cd2` | 1 | 0 | no |
| `G:/CODEX/New Manga.worktrees/M2-I2-review-0d6acc7` | `(detached)` | 1 | 0 | no |
| `G:/CODEX/New Manga.worktrees/P03-dsh-review-6d84b48` | `review/deepseek/P03-packaged-sfx-entry-6d84b48` | 1 | 0 | no |
| `G:/CODEX/New Manga.worktrees/RC4-domain-commands` | `codex/rc4-domain-commands` | 1 | 0 | no |
| `G:/CODEX/New Manga.worktrees/T2.2.1-zcode` | `agent/zcode/T2.2.1-reader-workbench-polish` | 1 | 0 | no |
| `G:/CODEX/New Manga.worktrees/TASK-024-zcode` | `agent/zcode/TASK-024-extension-boundaries-design` | 1 | 0 | no |

## 六、大体积目录表（AC1 第四表）

删除前实测，按体积降序。`可再生` 一列是判定，不是猜测——依据列写明为什么。

| 路径 | 体积 | 处置 | 依据 |
|---|---:|---|---|
| `\worktrees` | 111.08 GB | **保留** | 含 57 个 `PRESERVE_REFERENCED` 恢复点；P15 manifest 已把 3 个 junction 登记为受保护 |
| `…\worktrees\<task>\node_modules`、`target`、`dist` | 含于上行 | **保留** | 技术可再生，但位于受保护 worktree 内，删它等于改变恢复点的形态 |
| `…\review-scratch` | 13.69 GB | **已清理** | 评审临时区，0 条证据 pin 引用 |
| `…\builds` | 11.83 GB | **已清理** | 构建产物；`P22-REBASE-1/cargo-target` 被 pin，已保留 |
| `G:\CODEX\New Manga.worktrees\<37 个孤儿>` | 0.67 GB | **保留** | `.git` 已丢失，无法判定与任何提交的差异；不确定项保留 |
| `…\task-envs` | 3.61 GB | **保留** | 含 `M2-PROD-DETECT-ENV-1` 的隔离 venv；删它等于撤销该 Task 的成果 |
| `…\temp` | 2.86 GB | **已清理**（保留 1 项） | 临时区；`P22-REBASE-1` 被 pin |
| `…\tasks` | 2.83 GB | **保留** | 来源未逐一核实 |
| `…\test-materials` | 2.81 GB | **保留** | 2 条证据 pin |
| `…\archive` | 1.08 GB | **保留** | 归档区本身；本轮新增 76 个 bundle（21.1 MB） |
| `…\artifacts` | 0.91 GB | **保留** | 0 条 pin，但来源未核实；不确定项保留 |
| `…\tmp` | 0.45 GB | **已清理**（部分因占用失败） | 临时区 |

**释放合计**：worktree 移除 29.3 GB + 派生产物 20.15 GB = **约 49.5 GB**。

**明确未追的体积**：`workspace/worktrees` 111 GB 与 `task-envs` 3.6 GB。这两处的收益最大，但前者是恢复点、后者是某个 Task 的成果载体，**清理它们会让「整理」变成静默的破坏**。
