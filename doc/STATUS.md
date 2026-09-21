# Current Development Status

Planning source of truth: [Project Rebaseline Plan](REBASELINE_PLAN.md)
Effective activation base: `master` @ `f8a4f4ab9a1e66808bfa82fd1a59c014fa7ec8a2` on 2026-09-21 (T1.3.1 closure anchor was merge `38d6eaaefe9d344d8534996f469f2ba868922845`; rebaseline activation base was `b05cd886c9a228d79a75adefbb0415b3e8d3898f`)

| Field | Current value |
|---|---|
| Current Milestone | **M1 — Alpha Core Loop Closure** |
| Active Task | **T1.1.2 — Region Canvas & Creator** |
| Active state | **ACTIVE / released for execution** by Owner decision on 2026-09-21. Owner=**Qoder**; non-author Reviewer=**antigravity**; Integrator=Codex. Base `f8a4f4ab9a1e66808bfa82fd1a59c014fa7ec8a2`; branch `agent/qoder/T1.1.2-region-canvas`; implementation not yet started. Allowed paths (inherited from legacy TASK-013, to be re-frozen by Codex against current HEAD before work starts): `src/ui/qml/workbench/**`, `src/ui/viewmodels/workbench/**`, `src/ui/models/tasks/**`, `tests/workbench/**`, `doc/tasks/TASK-013.md`, `doc/handoffs/TASK-013-*.md`, `verification/TASK-013/**`. |
| Other rebaseline tasks | **PLANNED** |
| Concurrent preparation tracks | Authorized by the same Owner decision, **preparation only — no product code**: T1.1.1 detector-provider technical evaluation (DSH) and T1.2.1 Settings contract pre-study (ZCode). Neither may modify `src/**` or `tests/**`; deliverables are documents only, path to be set by Codex. These tracks do not make T1.1.1 or T1.2.1 ACTIVE. |
| Current blockers | T1.1.1: implementation choice required (evaluation in preparation; `src/infrastructure/providers/registry.py` has **no detection slot** and there are **zero** production `DetectionProvider` implementations, so adding one is a shared-interface change that Codex must scope-freeze first). T2.1.1: TASK-059 ND-6 and remaining implementation decisions must be resolved. Governance: **antigravity** has no role in `AGENTS.md` or in the plan's agent-allocation section; it is used this cycle as Review/evidence-check only per Owner ruling 2026-09-21, and `AGENTS.md` is a forbidden path, so the role table still needs a Codex/Owner ruling. |
| Last verified product test status | Merge `38d6eaa`: 982 collected = 976 passed / 6 skipped / EXIT=0 on 2026-09-21; six skips are the existing `openssl unavailable` network cases. Command: `python -m pytest tests -q -p no:cacheprovider -rs` in `TASK-012-py312`, `PYTHONPATH=src`, `PYTHONDONTWRITEBYTECODE=1`, `QT_QPA_PLATFORM` unset. Evidence: [integration-master-38d6eaa.log](../verification/TASK-057/integration-master-38d6eaa.log). |
| Last closed Task | **T1.3.1 / TASK-057** — Round 4 independent Review **approved** (reviewed head `c79cd36`, review commit `ad17dbf`, [Review](reviews/T1.3.1-TASK-057-c79cd36.md)); integrated as `38d6eaa` (`--no-ff`) by Qoder acting as the user-designated integration executor for this cycle. Merged `src`/`tests` are byte-identical to the reviewed head; post-integration regression passed. E1.3 Branch Integration & Baseline Cleanup is now fully closed (T1.3.2 `784e306` + T1.3.1 `38d6eaa`). |
| Open leftovers from T1.3.1 | **R-012** (P2, deferred): restore 前置 live ledger 读的 `sqlite3.Error` 未 typed，仅在「live DB 无 `backup_records`」这一当前不可达配置下触发；必须在把 backup service 接线到生产 bootstrap 的切片里一并 typed 化。**R-013** (P2, **fixed** at closure): `doc/REBASELINE_PLAN.md` 的 T1.3.1 Verification 曾引用不存在的 `tests/maintenance/test_sqlite_backup.py`，已更正为实际套件。详见 [Review §Findings](reviews/T1.3.1-TASK-057-c79cd36.md) 与 [TASK-057](tasks/TASK-057.md)。 |
| Next eligible Task | **T1.1.2** is active; no successor is authorized. T1.1.1 and T1.2.1 stay **PLANNED** (preparation tracks only, per the row above). |
| Pre-existing changes to preserve | `experiments/TASK-017/README.md` modified; 19 untracked files under `.qoder-credits/`. These are not part of rebaseline. |
| Worktree inventory | 94 linked worktrees: 3 MUST_PRESERVE, 9 NEEDS_REVIEW, 76 SAFE_TO_REMOVE, 6 UNKNOWN. No deletion authorized. See [inventory](WORKTREE_SAFETY_INVENTORY.md). |
| Legacy Tasks | TASK-001–065 remain in place as historical evidence; current mapping is in the Rebaseline Plan. |
| Repository policy | Codex remains sole master integrator; Owner ≠ Reviewer; no push is authorized. |

## Stop gate

Execute only T1.1.2. The T1.1.1 / T1.2.1 preparation tracks may run concurrently but must not write product code. Do not start any other task or clean worktrees without human activation. Nothing has been pushed.
