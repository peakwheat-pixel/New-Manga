# M2-AC1 Release Record

- **Decision:** 用户明确要求在 M2-RC2 后登记并释放首个 successor；范围只取 M2 Acceptance Backlog 首行。
- **Task / release state:** [M2-AC1](../../doc/tasks/M2-AC1.md), `ready / M2_END_TO_END_ACCEPTANCE_RELEASED`。
- **Owner / Reviewer / Integrator:** ZCode（建议执行角色 `heavy_task_executor`）/ DeepSeek Harness（非作者）/ Codex。
- **Dependency:** M2-RC2=`done`, integration=`88f972fed921c7d7a010bef38a734de2601d9ca5`。
- **Fixed implementation base:** `7db0e7b6ef77b5d403e3d485dc1378d4c786bc7d`.
- **Registration/release commit:** recorded in the final Codex handoff after the governance commit is created.
- **Owner branch:** `agent/zcode/M2-AC1-end-to-end-acceptance`.
- **Owner worktree:** `G:/CODEX/New Manga.worktrees/M2-AC1-zcode` (frozen path; awaiting Codex creation).
- **Scope:** deterministic Mock/Local success path, SQLite result persistence, actual process restart/recovery, Reader page reading and one PNG export verification. The detailed AC, allowed/forbidden paths and commands in the Task are authoritative.
- **Not released:** every other M2 Acceptance Backlog row; real docTR/model success; clean installation/packaging; Legacy QML; Contract/dependency changes; other security, integrity and Release Gate work.

## Release preconditions

At release start, `git rev-parse HEAD` returned `7db0e7b6ef77b5d403e3d485dc1378d4c786bc7d`, branch was `main`, top-level was `G:/CODEX/New Manga`, and Git common directory was `G:/CODEX/New Manga/.git`. `doc/STATUS.md` and `doc/tasks/README.md` both showed no released Active Task. M2-RC2 was `done`. The shared main worktree contained unrelated pre-existing dirty/untracked files; none are included in this release. The M2-AC1 Owner branch/worktree did not exist and is frozen above for creation from the fixed base.

## Released scope and gates

The release authorizes only the listed Task paths and AC. The dedicated `run_e2e.py` must exercise the real Windows Tauri/WebView2 + Python Core flow using a deterministic synthetic provider and an isolated temporary database. It must run two independent samples, shut down and relaunch the desktop/Core processes against the same per-sample data root, restore the saved result without rerunning Pipeline, read at least two pages, export PNG, and compare deterministic output summaries. Missing scenarios, `FAIL`, and `NOT_RUN` fail the Gate; unsupported environment is `BLOCKED`. No real docTR, user source, package readiness, or unlisted backlog result may be reported as PASS.

Release Gate field audit:

| Required field | Frozen evidence |
|---|---|
| Base | `7db0e7b6ef77b5d403e3d485dc1378d4c786bc7d` |
| Branch / worktree | `agent/zcode/M2-AC1-end-to-end-acceptance` / `G:/CODEX/New Manga.worktrees/M2-AC1-zcode` |
| Allowed paths | Present in `doc/tasks/M2-AC1.md` under “允许修改范围” |
| Acceptance criteria | AC1 through AC6 in Task body |
| Verification commands | Python, Rust, React, E2E and scope commands in Task “测试要求” |

## Forwardable Owner instruction

> **致 ZCode（Owner，`heavy_task_executor`）：** 执行已释放的 [M2-AC1](../../doc/tasks/M2-AC1.md)。仓库 `G:/CODEX/New Manga`，固定 base=`7db0e7b6ef77b5d403e3d485dc1378d4c786bc7d`，branch=`agent/zcode/M2-AC1-end-to-end-acceptance`，worktree=`G:/CODEX/New Manga.worktrees/M2-AC1-zcode`（待 Codex 创建）。先从固定 base 建立干净 worktree，再只从本释放记录所属治理提交取入 `doc/tasks/M2-AC1.md` 并提交 `ready`→`in_progress` claim；不要把治理提交合入实现历史。严格按 Task allowed paths 实现并验证确定性 Mock/Local Pipeline → SQLite 保存 → 真正退出/重启并恢复 → Reader 阅读 → PNG 导出闭环。按 Task 表运行专用 E2E 与所有受影响语言测试，记录环境、PID、SQLite 恢复、摘要、Reader/export 断言、EXIT 和原始证据到 `verification/M2-AC1/`，并提交 Handoff。不得实现或声称关闭其他 Acceptance Backlog 行、真实 docTR、打包、Legacy QML 或 Contract 工作。固定交付 head 后交 DeepSeek Harness 非作者 Review；Codex 负责复跑、集成与 `done` 裁决。
