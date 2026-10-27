---
id: NS-WIRE-A1
title: NS 命令接线第一批（settings/plugins/backup/cleanup）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_followups_batch_a1
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: 230164c5c
branch: task/NS-WIRE-A1
worktree: G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-A1
integration_commit: 7e1ef00d7
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/NS-WIRE-A1
allowed_paths:
  - doc/tasks/NS-WIRE-A1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/NS-WIRE-A1/**
  - G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-A1/**
  - G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-A1/**
---

# NS-WIRE-A1：设置/插件/备份/清理类 NOT_SUPPORTED 接线（第一批）

## 背景

S2 交付时 66 条生产命令中 16 条已实现、50 条显式 NOT_SUPPORTED；S3/S4 已登记 18 条计划批次（S3-A/B/C 8 条、S4-A/B/C 10 条）。本任务做 **A 组第一批 = S3-A/B/C 类（settings / plugins / backup / cleanup 语义）** 的命令接线。

## Acceptance Criteria

- [x] **AC1 清单**：从 `doc/handoffs/HOST-COMMAND-MIGRATION-1-handoff.md` 与 `verification/HOST-COMMAND-MIGRATION-1/parity/` 列出 S3-A/B/C 对应命令（预期 8 条），逐条标注 Core 路由/参数/返回。→ **MET**：8 条全部列出（旧壳 handler/参数/返回/错误类型 + Core 路由 + minor + probe 实测）：`verification/NS-WIRE-A1/command-list.json`。
- [x] **AC2 实现**：在 C# `HostCommandRegistry`/dispatcher 与 domain service 中接线；每条命令对冻结 sidecar 真实执行，参数/返回/错误码与旧壳 parity 一致。→ **MET**：registry 8 条 Core 绑定（P15 三条 minor=7，其余 minor=3）；dispatcher 复刻旧壳签名做参数边界校验/负载翻译；集成测试 24 implemented 真实执行 + `probe-results.json` 8 路由实测（含 reader projection 在 BOOK-FIXTURE-1 上 8 页成功路径；P15 错 minor/空 chapter 两类负例）。
- [x] **AC3 parity 更新**：`extract-command-surface.py --check` 零漂移；parity 快照中这些命令从 NOT_SUPPORTED → IMPLEMENTED，证据 JSON 落 `verification/NS-WIRE-A1/`。→ **MET**：`--check` PASS（66 命令零漂移，快照 sha `4c6a4da0…` 未变）；registry 16→24 IMPLEMENTED / 50→42 NOT_SUPPORTED（8 条变更）：`parity-update.json` + `evidence/parity-contract.json`。
- [x] **AC4 回归**：`scripts/test.ps1` 全绿（新增命令测试）；旧壳 vitest 60/567；pytest 基线 3F/2739P/9S 无新增失败。→ **MET**：test.ps1 **110/110 passed, 0 skipped**；vitest **60/60 文件、567/567 用例**；pytest **3F/2739P/9S（0 新增）**。
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。→ **MET**：check.ps1 PASS；pin 见下；`doc/handoffs/NS-WIRE-A1-handoff.md`。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/NS-WIRE-A1/**`、workspace。只读参考：旧 Rust host 命令面、S2 Handoff。

## 禁止范围

不改 Python Core 语义、不改 Host 契约（如确需，先回报 DSH）、不改旧壳、不 push、不 gc/prune；不得把未验证命令标 IMPLEMENTED。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | `verification/NS-WIRE-A1/tools/probe-ns-a1.ps1`（8 路由直连）+ `scripts/test.ps1` 集成测试 | 无标签 sidecar 副本 + 隔离 data root（+ BOOK-FIXTURE-1 数据根） | **PASS**：8/8 路由实测；24 implemented 真实执行；P15 错 minor/空 chapter 负例按预期 typed error | `probe-results.json`、`evidence/integration-results.json` |
| AC3 | `extract-command-surface.py --check` + registry 前后对比 | Rust 源只读 | **PASS**：66 命令零漂移、快照 sha 未变；16→24 / 50→42 | `parity-update.json`、`parity-check.log` |
| AC4/AC5 | test.ps1 / vitest / pytest / check.ps1 | 全量 | **PASS**：110/110、60/567、3F/2739P/9S、治理 PASS | `dotnet-all.log`、`vitest.log`、`pytest.log` |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
| N1 | AC1–AC4 | verification/NS-WIRE-A1/command-list.json | 14e855407 | f6c9df117ae6c8b346312c3776cacdc6bff643c7bbca43555907880f771b2d82 | CANONICAL |
| N2 | AC1–AC4 | verification/NS-WIRE-A1/dotnet-all.log | 14e855407 | b0157db389fd9757568ce1a68a95815b1dde3979a131e12940182a7b333365d5 | CANONICAL |
| N3 | AC1–AC4 | verification/NS-WIRE-A1/parity-check.log | 14e855407 | 820f6d456abeab98d52599b5fffdfa051b58369b8a108e8860b1fde4f6db82fe | CANONICAL |
| N4 | AC1–AC4 | verification/NS-WIRE-A1/parity-update.json | 14e855407 | fc1236936140684635ce25c2701c60f8878d57e21fb51f26dd2bbea5cd506c91 | CANONICAL |
| N5 | AC1–AC4 | verification/NS-WIRE-A1/probe-results.json | 14e855407 | d60cbf21ae7814c638d73f217e900a5b7fa92b663c292ff2c0e27af44bea0f67 | CANONICAL |
| N6 | AC1–AC4 | verification/NS-WIRE-A1/pytest.log | 14e855407 | 9f2537decad9141e62a81cb188a7dbf278c084d50e440de21f421ae32ba001ee | CANONICAL |
| N7 | AC1–AC4 | verification/NS-WIRE-A1/REPORT.md | 14e855407 | cab1c7bc302a196fab62d249b3742944eb5d933563e17fb64553957146ff188c | CANONICAL |
| N8 | AC1–AC4 | verification/NS-WIRE-A1/vitest-install.log | 14e855407 | 5ae5647600aa76bd44ec59a927c65d7518548484e8f2c30dd53af06e1e142b06 | CANONICAL |
| N9 | AC1–AC4 | verification/NS-WIRE-A1/vitest.log | 14e855407 | 60f06accf43cbc0bcb320c6af57fa453172c0a60e3a74632bde161458522f56c | CANONICAL |
| N10 | AC1–AC4 | verification/NS-WIRE-A1/evidence/chinese-roundtrip.json | 14e855407 | bbd6ee9d4ccf9ac6d3e1bd5c8d845a69c7845cd76e54e983874778185e95f130 | CANONICAL |
| N11 | AC1–AC4 | verification/NS-WIRE-A1/evidence/domain-services.json | 14e855407 | 2036c66efbfe2a7a92cf13f3b4fb62f405b81f61f1679f78897eaeb7677d3184 | CANONICAL |
| N12 | AC1–AC4 | verification/NS-WIRE-A1/evidence/integration-results.json | 14e855407 | e7fecd4a26dbaacdecc0f7d33ab12108d545dfbd5fb6140b3f140cedcaa61890 | CANONICAL |
| N13 | AC1–AC4 | verification/NS-WIRE-A1/evidence/not-supported-typed-errors.json | 14e855407 | 9e7e7802b7ab89d45ebddbf0c649e9cf5434326d065981eedfe30418982b7246 | CANONICAL |
| N14 | AC1–AC4 | verification/NS-WIRE-A1/evidence/parity-contract.json | 14e855407 | f0fe2042292d787b41b416cd11664d39c854c32ae50ce698727af610f5728ec2 | CANONICAL |
| N15 | AC1–AC4 | verification/NS-WIRE-A1/evidence/wiring.json | 14e855407 | 1c3050a24274705d1857460168ca728959644ad49a9f39cfa4003a4d19529a01 | CANONICAL |
| N16 | AC1–AC4 | verification/NS-WIRE-A1/tools/probe-ns-a1.ps1 | 14e855407 | 0e9fe1238e7b34095810625b900a054bc6c334ca1469d58dc1653a95251a0f01 | CANONICAL |
|---|---|---|---|---|---|
| E-A1-REPORT | AC1–AC5 | `verification/NS-WIRE-A1/REPORT.md` | `14e855407` | `cab1c7bc302a196fab62d249b3742944eb5d933563e17fb64553957146ff188c` | CANONICAL |
| E-A1-LIST | AC1 | `verification/NS-WIRE-A1/command-list.json` | `14e855407` | `f6c9df117ae6c8b346312c3776cacdc6bff643c7bbca43555907880f771b2d82` | CANONICAL |
| E-A1-PROBE | AC1/AC2 | `verification/NS-WIRE-A1/probe-results.json` | `14e855407` | `d60cbf21ae7814c638d73f217e900a5b7fa92b663c292ff2c0e27af44bea0f67` | CANONICAL |
| E-A1-PARITY | AC3 | `verification/NS-WIRE-A1/parity-update.json` | `14e855407` | `fc1236936140684635ce25c2701c60f8878d57e21fb51f26dd2bbea5cd506c91` | CANONICAL |
| E-A1-CHECK | AC3 | `verification/NS-WIRE-A1/parity-check.log` | `14e855407` | `820f6d456abeab98d52599b5fffdfa051b58369b8a108e8860b1fde4f6db82fe` | CANONICAL |
| E-A1-INTEGRATION | AC2/AC4 | `verification/NS-WIRE-A1/evidence/integration-results.json` | `14e855407` | `e7fecd4a26dbaacdecc0f7d33ab12108d545dfbd5fb6140b3f140cedcaa61890` | CANONICAL |
| E-A1-CONTRACT | AC2/AC3 | `verification/NS-WIRE-A1/evidence/parity-contract.json` | `14e855407` | `f0fe2042292d787b41b416cd11664d39c854c32ae50ce698727af610f5728ec2` | CANONICAL |
| E-A1-NOTSUP | AC2 | `verification/NS-WIRE-A1/evidence/not-supported-typed-errors.json` | `14e855407` | `9e7e7802b7ab89d45ebddbf0c649e9cf5434326d065981eedfe30418982b7246` | CANONICAL |
| E-A1-DOMAINS | AC2 | `verification/NS-WIRE-A1/evidence/domain-services.json` | `14e855407` | `2036c66efbfe2a7a92cf13f3b4fb62f405b81f61f1679f78897eaeb7677d3184` | CANONICAL |
| E-A1-DOTNET | AC4 | `verification/NS-WIRE-A1/dotnet-all.log` | `14e855407` | `b0157db389fd9757568ce1a68a95815b1dde3979a131e12940182a7b333365d5` | CANONICAL |
| E-A1-VITEST | AC4 | `verification/NS-WIRE-A1/vitest.log` | `14e855407` | `60f06accf43cbc0bcb320c6af57fa453172c0a60e3a74632bde161458522f56c` | CANONICAL |
| E-A1-PYTEST | AC4 | `verification/NS-WIRE-A1/pytest.log` | `14e855407` | `9f2537decad9141e62a81cb188a7dbf278c084d50e440de21f421ae32ba001ee` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-A1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-A1 | 本轮 probe 临时根已清理；证据副本在 `verification/NS-WIRE-A1/` | 无残留进程；task-env 仅脚本副本 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS

- **8/8 接线 IMPLEMENTED**：settings_update_section、settings_provider_profiles_list、settings_network_profiles_list、settings_resolve_overrides、ackup_create、plugins_set_enabled、cleanup_run、library_get_reader_projection。
- 关键发现（已记录）：P15 settings 面 Core 硬拒 minor≠7（probe 反证 minor3→INVALID_REQUEST）；registry 三条固定 minor=7；dispatcher 按旧壳签名做参数边界校验与负载翻译（INVALID_ARGUMENTS），Core 业务错误码透传。
- parity：xtract-command-surface.py --check PASS（66 命令零漂移，Rust 快照 sha 4c6a4da0… 未变）；**16→24 IMPLEMENTED / 50→42 NOT_SUPPORTED**。
- 证据：command-list.json、probe-results.json（8 路由直连+2 负例；reader projection 在 BOOK-FIXTURE-1 上 8 页成功）、parity-update.json、vidence/。
- 回归（DSH 复跑 scripts/test.ps1）：见执行记录；vitest 60/567、pytest 3F/2739P/9S 基线不变。
- 基线说明：任务卡 base 原写 230164c5c（早于卡片创建，治理 FAIL），实际分支基于释放提交 50ab8fc5；已按实现方记录更正。
- 遗留：S4-A/B/C 10 条仍 NS（后续批次）；reader projection 成功路径依赖 BOOK-FIXTURE 数据根；cleanup 仅空缓存、backup 仅创建。
## 集成验证补记（2026-10-27T04:44Z）

- DSH 在 main 上复跑 pps/desktop-avalonia/scripts/test.ps1 → **TEST PASS (Debug): 110/110 passed, 0 skipped**（此前一次失败为遗留进程锁日志/并行抢占所致，清理后复现全绿）。
- 结论：AC4 由实现方证据 + DSH 复跑双重确认。
