---
id: NS-RECLASSIFY-1
title: NOT_SUPPORTED 重探测与重分类（只出证据）
kind: research
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_followups_a2_extra
suggested_owner: baseline-scout
owner: null
reviewer: dsh
depends_on: []
base_commit: 171529b5d
branch: task/NS-RECLASSIFY-1
worktree: G:/CODEX/New Manga.workspace/worktrees/NS-RECLASSIFY-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/NS-RECLASSIFY-1
allowed_paths:
  - doc/tasks/NS-RECLASSIFY-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/NS-RECLASSIFY-1/**
  - G:/CODEX/New Manga.workspace/task-envs/NS-RECLASSIFY-1/**
  - G:/CODEX/New Manga.workspace/worktrees/NS-RECLASSIFY-1/**
---

# NS-RECLASSIFY-1：42 条 NOT_SUPPORTED 重探测与重分类（只出证据，不改代码）

## 背景

`READER-PROGRESS-1` 实现方发现：registry 中 `library_save_reading_progress` 仍标 NOT_SUPPORTED，原因是 S2 时 parity 探针 **payload 错误**（不是真没实现）。类似可能还有别的误分类。本任务把 42 条 NS 全部用**正确 payload** 重探测一遍，给出重分类建议。

## Acceptance Criteria

- [x] **AC1 重探测**：对 `verification/HOST-COMMAND-MIGRATION-1/parity/**` 快照中的 42 条 NOT_SUPPORTED，按旧壳 Rust 签名构造正确 payload，对冻结双 sidecar 逐一探测，记录：可执行/需先实现 Core 路由/需模型/缺契约。
- [x] **AC2 分类建议**：产出 `verification/NS-RECLASSIFY-1/reclassification.json`，每条给 `current_status / proposed_status(IMPLEMENTED|NEEDS_IMPLEMENTATION|NEEDS_MODEL|BLOCKED) / evidence / reason`；注明哪些是 S2 探针错、哪些是真未实现。
- [x] **AC3 不改代码**：本任务**只产出证据与建议**，不修改 registry/parity 快照/冻结证据；应用改动由 DSH 在后续 Task 中做。
- [x] **AC4 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff（含建议应用顺序与风险）。

## 允许修改范围

`verification/NS-RECLASSIFY-1/**`、本卡、STATUS/PLAN/LEDGER、workspace。**只读**：registry、parity 快照、sidecar。

## 禁止范围

不改任何产品源码/冻结证据/协议、不 push、不 gc/prune、不伪造探测结果。命不中签名的命令标 BLOCKED 写原因。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EV-AC1-PROBE | AC1 | verification/NS-RECLASSIFY-1/probe-results.json |  | 51beb8df0b0b44ccc0f6eb421a3cdcc28c8e3ec49eba834a22a6f04e2e5ae7f7 | CANONICAL |
| EV-AC1-SPEC | AC1 | verification/NS-RECLASSIFY-1/probe-spec.json |  | e9058c87b61513536daed1ee4678f471d09fd0ec12243771c77b45cb0dcea3fd | CANONICAL |
| EV-AC2-CLASSIFY | AC2 | verification/NS-RECLASSIFY-1/reclassification.json |  | 1e6a8e34c747d4f98261a3828700d8f30e14d11990d19960d3c19d7f4e7230b1 | CANONICAL |
| EV-RES-MANIFEST | AC4 | verification/NS-RECLASSIFY-1/resource-manifest.json |  | e8e780a3fd353e76d0829996369d4cb40c4ae0ddb223f81c25cd4a6bcd3e9656 | SOURCE_PIN |
| EV-AC2-REPORT | AC2/AC4 | verification/NS-RECLASSIFY-1/REPORT.md |  | 9c44d398ea8f1e879dac7117c9e71406334029980a520f45aff91bb037a86be2 | CANONICAL |
| EV-AC4-PROBETOOL | AC4 | verification/NS-RECLASSIFY-1/tools/probe-core.ps1 |  | 13d8e2d5dfbac721510bf1cd7520ec680f8645ab019f52f4f7afd964661a34a1 | CANONICAL |
| EV-AC4-CLASSIFYTOOL | AC4 | verification/NS-RECLASSIFY-1/tools/classify.py |  | 468d4968c9208c0d58c06d7050fe447d81002ac850339b3594e1e85e9a2502b6 | CANONICAL |

说明：本 Task 只出证据，未提交代码；证据用 64-hex SHA-256 pin（commit 列填 —，避免 pin 到不存在的提交）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/NS-RECLASSIFY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/NS-RECLASSIFY-1 | verification/NS-RECLASSIFY-1/resource-manifest.json | 已核：sidecar 副本 = HOST-CORECLIENT-1 无标签副本（core_service.exe sha256 e0a1eff8…），probe/data = BOOK-FIXTURE-1/isolated-data 私有副本（原件零修改）；仓库内无二进制/权重，只有 JSON/MD 证据 |

## 交付与运行记录

- Handoff：`verification/NS-RECLASSIFY-1/REPORT.md`（§5 建议应用顺序与风险）+ `reclassification.json`。
- 探测对象：冻结 `core_service.exe` `sha256=e0a1eff8…f6f14bc0`（与 S2 同二进制）；协议 2.3 + host-control；
  经验证 minor：P15 settings=7、CreateBook/Chapter=8、**DELETE 面=10**（3–12 扫描实证）。
- 数据根：`BOOK-FIXTURE-1/isolated-data` 的私有副本（重建 catalog 绑定）；原件零修改；未触碰用户 `%APPDATA%`。
- 结果：42 条中 **IMPLEMENTED 35（high 26 / medium 16）**、**NEEDS_IMPLEMENTATION 7**、NEEDS_MODEL 0、BLOCKED 0。
  典型误分类：`library_save_reading_progress`（S2 payload 错 → 本次正确 payload **ok=true**）、
  `resolve_page_resource`（S2 假 id → 本次 **ok=true**）、`list_region_revisions`（S2 用 PascalCase → `UNKNOWN_COMMAND`；
  snake_case 可跑）、`set_region_type`（S2 非法枚举 → 本次合法枚举进入 handler）。
- 未做：16 条 medium 的正向成功路径（payload 契约未完全命中）、import/export grant 全链路（需 Host 侧签发）、
  2 条 host-local shell 动作的可执行探测（Core 无命令）。
- 未修改：registry / 产品源码 / parity 快照 / 冻结证据（AC3）；STATUS/PLAN/LEDGER 未改，交由 DSH 统一更新。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
