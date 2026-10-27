---
id: S4-CMD-BATCH-1
title: S4-A/B/C 命令接线（region 写 4 + reader 2）
kind: implementation
governance_version: 3
status: in_review
approval: user_authorized_2026-10-27_followups_a2_extra
suggested_owner: saber-ui-spec
owner: route-research
reviewer: dsh
depends_on: []
base_commit: 171529b5d
branch: task/S4-CMD-BATCH-1
worktree: G:/CODEX/New Manga.workspace/worktrees/S4-CMD-BATCH-1
integration_commit: null
delivery_head: 90535f048e388a513c19ba48ec6e4d304a0712a7
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/S4-CMD-BATCH-1
allowed_paths:
  - doc/tasks/S4-CMD-BATCH-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/S4-CMD-BATCH-1/**
  - G:/CODEX/New Manga.workspace/task-envs/S4-CMD-BATCH-1/**
  - G:/CODEX/New Manga.workspace/worktrees/S4-CMD-BATCH-1/**
---

# S4-CMD-BATCH-1：S4-A/B/C 命令接线（region 写 + reader 命令）

## 背景

S2 遗留 42 条 NS 中，S4-A/B/C 登记 10 条：region 写 4、reader 2、Run/Export 4（Run/Export 由 `RUN-EXPORT-E2E-1` 承接）。本任务做 **region 写 4 + reader 2 = 6 条**接线。

交付分支基于任务基线 `171529b5d`，已 rebase 到 main `9f58b4c1d`（RUN-EXPORT-E2E-1 24→33、NS-WIRE-B1 33→46 先落地）并手动合并；合并后 registry **46 → 51 IMPLEMENTED / 15 NOT_SUPPORTED**，S4Wiring 28 wired / 0 NS。Handoff：`doc/handoffs/S4-CMD-BATCH-1-handoff.md`。

## Acceptance Criteria

- [x] **AC1 清单**：列出 S4-A/B/C 中 region 写与 reader 命令共 6 条（region 写 4 + reader 2），逐条标注旧壳 handler/参数/返回/错误类型、Core 路由/payload/result/wire error、before→after。证据：`verification/S4-CMD-BATCH-1/command-list.json`。<<MET>>
- [x] **AC2 接线**：C# Host registry/dispatcher/domain service 实现 5 条新绑定 + `library_get_reader_projection` 真实 chapter 复验；每条对冻结 sidecar 真实执行并有断言，region 写使用 BOOK-FIXTURE 派生的真实 region/revision/page/clean-artifact（`scripts/seed_s4_region_fixture.py`）且只在 durable 副本上写。证据：`commands/s4-region-reader-results.json`（7/7 all_ok）、`commands/core-command-probe.json`（raw wire 6 目标路由 ok:true）。<<MET>>
- [x] **AC3 parity**：`extract-command-surface.py --check` PASS、Rust 快照 sha 未变（`4c6a4da0…`）；C# registry `24/42 → 33/33 → 46/20 → 51 IMPLEMENTED / 15 NOT_SUPPORTED`，每命令原因/通道齐全；同步 NS-WIRE-B1 测试的硬编码计数 46/20→51/15。证据：`parity-update.json`、`parity-check.log`、`evidence/commands/parity-contract.json`。<<MET>>
- [x] **AC4 回归**：`scripts/test.ps1` **PASS 162/162，0 skipped**（coreclient 45 / host 42 / app 75）；vitest **60/567**；pytest **3F/2746P/9S**（失败集合与任务书基线 3F/2739P/9S 完全一致；main 新增 7 个 device 测试导致通过数 2739→2746，无新增失败）。证据：`evidence/test/summary.json`、`vitest.log`、`pytest.log`。<<MET>>
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；13 条 64-hex sha256 evidence pin；Handoff + 本卡 Record Decision（region 写权限/只读门）。<<MET>>

## Record Decision — region 写权限 / 只读门

**决定**：本批 6 条命令只在 `NewManga.CoreClient` registry / dispatcher / domain service 层接线，**不新增** `HostRuntime` 公开写方法，不改变“parity 前只读”门。

1. 既有只读门：`HostRuntime.CreateBookAsync` / `SaveReadingProgressAsync` 在 `Policy.WritesAllowed == false` 时抛 typed `ReadOnlyHostException`，请求不达 Core（`apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs:70-79,155-167`）。
2. S5 若把 region 写 4 条经 `HostRuntime` 暴露给 UI，必须复用同一 `Policy.WritesAllowed` 门与 typed 拒绝；App 不得直接持 `HostCommandDispatcher` 绕过；dispatcher 自身不做策略判断（Core 是语义权威，与既有命令一致）。
3. 真实写操作前必须持当前 revision（`list_regions` → `expected_revision`）；并发写由 Core 乐观锁返回 `INPUT_REVISION_CHANGED`；Host 不得猜测/伪造 revision 或 id。
4. 本批未扩大写权限：没有新增可被 UI 直接调用的公开写方法，也没有修改只读策略判定。

## 实际测试记录

| 套件 | 命令 | 结果 |
|---|---|---|
| 全量 .NET | `apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <private>` | **PASS 162/162，0 skipped**（coreclient 45 / host 42 / app 75） |
| 前端 | `apps/desktop/frontend`：`npx vitest run` | **60 files / 567 tests passed** |
| Python | `python -m pytest -q` | **3 failed / 2746 passed / 9 skipped**（失败集合与基线一致：detection real x2 因 `transformers` 缺 `RTDetrV2ForObjectDetection`；workbench pause optimistic x1） |
| 命令面 | `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` | **PASS**（66 命令，零漂移） |

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/S4-CMD-BATCH-1/**`、workspace。

## 禁止范围

不改 Python Core 语义（发现缺陷先回报）、不改 Host 契约语义/旧壳、不 push、不 gc/prune；与 `RUN-EXPORT-E2E-1` / `NS-WIRE-B1` 并行时 registry 冲突以先落地者为准、后落地者 rebase。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E1 | AC1 | verification/S4-CMD-BATCH-1/command-list.json | - | 9d56cf6d117e7f2868ab729ea775c978ad16a9c7a6e5fea8c29b40458bc35df3 | CANONICAL |
| E2 | AC3 | verification/S4-CMD-BATCH-1/parity-check.log | - | 820f6d456abeab98d52599b5fffdfa051b58369b8a108e8860b1fde4f6db82fe | CANONICAL |
| E3 | AC3 | verification/S4-CMD-BATCH-1/parity-update.json | - | b21038d57e3aeaefd3b7403e88d06acc85cac3e5860eddbe306dd562c6712769 | CANONICAL |
| E4 | AC1/AC2 | verification/S4-CMD-BATCH-1/commands/core-command-probe.json | - | 4a40c346e3a1bc768ed82018826f927dc0222d531d3bbda51ae939a46e4b3cea | CANONICAL |
| E5 | AC2 | verification/S4-CMD-BATCH-1/evidence/commands/s4-region-reader-results.json | - | f20a05c68533dfd3caaa5acfdd492cb2fe42ddfe8d64f2e757ed72209b561cbf | CANONICAL |
| E6 | AC2/AC4 | verification/S4-CMD-BATCH-1/evidence/commands/integration-results.json | - | 13cba3d26ddcc28765ceef4410acaa6f21249f54852aa9204850dd1c49fdd09c | CANONICAL |
| E7 | AC3 | verification/S4-CMD-BATCH-1/evidence/commands/parity-contract.json | - | d12b669af8e304a5368d648e1c56cafa4b490afd90cfe43290602b27612481d6 | CANONICAL |
| E8 | AC2 | verification/S4-CMD-BATCH-1/evidence/commands/not-supported-typed-errors.json | - | eb7ca7e1e7af8d13bc2e1151834ddbced4b0a313f6ac00d59d1e703c851f1559 | CANONICAL |
| E9 | AC2 | verification/S4-CMD-BATCH-1/evidence/commands/s4-wiring.json | - | e93851d237d046baf98d9afe38ab74e0ab2199cdf34b1485f8c4abe9c596f329 | CANONICAL |
| E10 | AC4 | verification/S4-CMD-BATCH-1/evidence/test/summary.json | - | 74ba77aa945e516182b1856e61138df7d8ab068d3a817b2b8e1b3c1911316d56 | CANONICAL |
| E11 | AC4 | verification/S4-CMD-BATCH-1/vitest.log | - | 941be5c040e7234c369ab0f4b83885501b9488a9cb55ad23e264831b1b7cb586 | CANONICAL |
| E12 | AC4 | verification/S4-CMD-BATCH-1/pytest.log | - | 40ab23c5d0125d148d3ca72501b6b31a1231f1c0b535c4d8c5ac6e496c0e13ac | CANONICAL |
| E13 | AC1–AC5 | verification/S4-CMD-BATCH-1/REPORT.md | - | ca98e4f43bcfa1eba9421faa3a7f98f6ef00081baf32df99c629104ec5e89998 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/S4-CMD-BATCH-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/S4-CMD-BATCH-1 | 见 `region-fixture/fixture.json`（`library_db_sha256` 覆盖 db+wal） | 交付时保留：region fixture（durable 数据根）、evidence-rerun（test.ps1 私有证据）、test-ps1-run*.log；AC11 sidecar 副本不含在内。关闭时复核引用。 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy | PRESERVE_REFERENCED | 原路径 | AC11 未标注副本（仓外） | 只读复用；不得随仓库传播，关闭时复核。 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`complete`（13 条 sha256 pin）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
