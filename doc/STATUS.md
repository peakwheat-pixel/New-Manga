# Current Development Status

Planning source of truth: [Project Rebaseline Plan](REBASELINE_PLAN.md)

Audit checkpoint: 2026-09-21 (Asia/Shanghai)

| Field | Current value |
|---|---|
| Code baseline HEAD | `ce21ff9ea5738970bbda9a86079b673918c76048` |
| Branch | `master` |
| Current milestone | **M1 — Alpha Core Loop Closure** |
| Stage | **Stage B — Controlled Execution** |
| Active product task | **T1.1.2 — Region Canvas & Creator**; Release Gate passed; `READY_FOR_QODER` |
| Product task owner/reviewer | Owner: Qoder; non-author reviewer: pending assignment; Coordinator/integrator: Codex. |
| Execution branch/worktree | `task/t1.1.2-region-canvas-qoder` / `G:\CODEX\New Manga.worktrees\T1.1.2-qoder` |
| Execution base/head | `b985d9cf92a894f035550fe409179b3cb5adcbd8`; delivery head: not yet created |
| Verified test status | Isolated Python 3.14 venv using `requirements-dev.txt`: `982 collected = 976 passed + 6 skipped`, exit 0. All six skips are OpenSSL-unavailable TLS cases. |
| Smoke status | `python -m bootstrap.app --smoke-test --data-root <temp>` exit 0; SQLite and managed directory created. |
| Compile status | `python -m compileall -q src tests` exit 0. |
| Current blockers | Production detector is `None`; Settings page is a placeholder with no Settings VM; Graphite F is not applied to production QML; reading/export history remain JSON-backed; product packaging and clean-machine gate are absent. |
| Dirty main-worktree files | Preserve: `experiments/TASK-017/README.md` (tracked modification); `.qoder-credits/` (19 untracked files); `.codewiki/`, `wiki/`, `.repowikiignore`, `doc/AI_COORDINATION.md` (untracked parallel/generated material). |
| Worktrees | Existing inventory is a 2026-09-20 conservative snapshot. Old `TASK-013-qoder` is clean but based on pre-Stage-A history and contains prior Qoder work; preserved, not selected. New T1.1.2 worktree is clean at `b985d9c`. No deletion or prune is authorized. |
| Last product integration | `38d6eaa` TASK-057 backup/restore integration; subsequent `49f35e8..ce21ff9` changes are planning/design documentation only. |
| Evidence | [Rebaseline verification](../verification/REBASELINE-2026-09-21.md) |

## Verified completed capability

SQLite v2 core persistence, managed copy, image/PDF/picture-MOBI import,
Webtoon tiled reading, scheduler/executor, rendering/export, connection
ownership, diagnostics wiring, four top-level routes, backup/restore service
tests and restore admission/latch tests are present and covered by the fresh
isolated suite. This is implementation evidence, not a claim of real-provider
quality or release readiness.

## Open gaps

1. T1.1.2: draw and persist a manual rectangle/polygon region from Workbench.
2. T1.1.1: choose and wire one real text detector; MangaOCR is recognition,
   not detection.
3. T1.2.1: expose provider, credential, endpoint and proxy settings safely.
4. T2.1.1: apply the selected Graphite Atelier token layer to production QML.
5. T3.1.1: migrate reading progress and export history from JSON to SQLite.
6. T3.2.1: build and verify a product Windows onedir package on a clean machine.

## Stage B execution gate

Only T1.1.2 is released. Do not start T1.1.1 or any later roadmap unit. Qoder
must stay within the released packet and must not modify bootstrap, shared
contracts, schema, settings, providers, theme, packaging, or the top-level
shell. Codex alone performs final `region_creator` bootstrap wiring and
integration. Preserve all dirty files and worktrees.

## Recovery instruction

```powershell
Set-Location 'G:\CODEX\New Manga'
git status --short --branch
git rev-parse HEAD
Get-Content doc\STATUS.md
Get-Content doc\REBASELINE_PLAN.md
git log -8 --oneline --decorate
```

If the worktree is dirty, preserve the listed files and identify their owner
before any edit. Resume from the latest committed checkpoint, not chat memory.

Worker recovery check:

```powershell
Set-Location 'G:\CODEX\New Manga.worktrees\T1.1.2-qoder'
git status --short --branch
git rev-parse HEAD
```
