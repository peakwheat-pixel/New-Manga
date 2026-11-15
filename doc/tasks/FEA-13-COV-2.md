---
id: FEA-13-COV-2
title: 覆盖清单二期（settings/drafts/plugins/trash-manifest 入包 + verified 语义 + restore 延迟写回）（FEA-13 片 2）
kind: implementation
governance_version: 3
status: done
approval: 裁决 `ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT`（D2 补 drafts/plugins；D3 外观设置不入包）+ `FEA-13-scope-r1.md` §7 片 2；依赖 `FEA-13-BK2-1`（manifest v2 + v1 adapter，done）
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文子代理 r1/r1b/r2（`doc/reviews/FEA-13-COV-2-r1.md`、`-r1b.md`、`-r2.md`；r1/r1b changes_requested → 处置；r2 **approved**，均非实现会话）
depends_on:
  - FEA-13-BK2-1
base_commit: 892cb99df
branch: null
worktree: null
integration_commit: f86105707
delivery_head: 00f14179a
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-13-COV-2
allowed_paths:
  - doc/tasks/FEA-13-COV-2.md
  - doc/reviews/FEA-13-COV-2-*.md
  - doc/handoffs/FEA-13-COV-2-*.md
  - verification/FEA-13-COV-2/**
  - src/infrastructure/sqlite/nmbak.py
  - src/bootstrap/core_assembly.py
  - tests/storage/test_nmbak_coverage.py
out_of_scope:
  - 不改 C-09/C-01b 契约字节、18 pins
  - 不实现 merge restore / 写回（片 4 `FEA-13-RESTORE-4`）：本片 restore 只**报告** `deferred_categories`，不改写 settings/drafts/plugins
  - 不实现 `DatabaseId`（片 3）、调度保留（片 5）、数据根迁移（单列）
  - 外观设置（`%APPDATA%/NewManga`）不入包（ADJ D3）
  - 不改 `SqliteBackupService`、不改 wire
  - **SC-B01 ④「源引用/授权元数据入包」不在本片**：写域在 Host 侧，按 `doc/reviews/FEA-13-COV-2-sc01-decision.md` 单列后续（`FEA-13-SRC-6` proposed），不在本片 AC
---

# FEA-13-COV-2：覆盖清单二期

## 来源与依据

`FEA-13` scope review r1 §7 片 2；ADJ-2026-11-09 **D2**（补 `drafts/**`、`plugins/**`，与 C-01b SC-10b 对齐）与 **D3**（外观设置不入包）。C-09 SC-B01a 归属表是本片规范来源。

## 实现口径

| 类别 | 内容 | 入包规则 |
|---|---|---|
| `settings` | `<data_root>/settings/{provider_profiles,network_profiles,provider_capability_bindings}.json` | 文件存在才入 |
| `drafts` | `<data_root>/drafts/**`（递归） | 目录存在则入（空目录记 0 文件） |
| `plugins` | `<data_root>/plugins/**`（递归） | 目录存在则入 |
| `trash-manifest` | `<managed_root>/trash-manifest.json` | 存在才入 |
| 排除项（逐项记录） | `catalog/catalog.sqlite`（可从 library.db 重建）、`derived/**`（可重建缓存）、外部原文件（data root 之外）、OS 凭据 vault | **不入包**，manifest `excluded_categories` 逐项记录原因 |

- 包内布局：`extras/<category>/<relative_path>`；manifest 新增 `extras`（每项 `category/relative_path/sha256/size_bytes`）、`included_categories`、`skipped_categories`、`excluded_categories`、`extras_total_bytes`。
- `verified=true` 仅当 read-back 校验通过且 extras 全部校验通过；某类别**根存在但收集失败** → `BACKUP_CREATE_FAILED`（不产出包）。
- restore：本片**不写回** extras；report 增加 `deferred_categories`（实际入包且延迟写回的类别）。`_verify_package` 必须校验 extras 成员的 `sha256`+`size_bytes`（tampered extras → `BACKUP_CORRUPT`）。

## Acceptance Criteria

- [x] **AC1 类别入包**：settings 三类（存在才入）、drafts/**、plugins/**、trash-manifest 均入包；**空类别根（如干净关机的 `drafts/`、空 `plugins/`）合法，记 0 文件并计入 `included_categories`/`empty_categories`**；manifest `extras` 每项含 `sha256`+`size_bytes`；类别声明与 `extras`+`empty_categories` 相互校验。 <<MET>>
- [x] **AC2 排除项记录**：`catalog/catalog.sqlite`、`derived/**`、外部原文件、OS 凭据 vault 不在包内；manifest `excluded_categories` 逐项有 `reason`。 <<MET>>
- [x] **AC3 verified 语义**：**收集过程发生读取错误** → `BACKUP_CREATE_FAILED`、无包产出（**空目录不属失败**——这是 R-001 修复点）；正常时 `verified=true` 且 read-back 含 extras 校验与类别声明交叉校验。 <<MET>>
- [x] **AC4 restore 延迟写回**：restore 后 `<data_root>/settings`、`drafts`、`plugins`、`trash-manifest` 字节不变；report 含 `deferred_categories`（与 `included_categories` 对应）。 <<MET>>
- [x] **AC5 变异判别**：①去掉 extras 的 sha 校验 → tampered extras 用例 RED；②restore 写回 extras → AC4 RED；③把 catalog 写进 excluded 之前入包 → AC2 RED（择一或全部）。 <<MET>>
- [x] **AC6 门禁**：定向 pytest 全绿；`check.ps1`（默认 + `-TaskPath`）PASS；pins 18/18；diff ⊆ allowed_paths。 <<MET>>

## Reviewer 登记

- r1：独立子代理 `doc/reviews/FEA-13-COV-2-r1.md`（changes_requested；P0=0/P1=1/P2=3/P3=4）
- r1b：另一独立子代理 `doc/reviews/FEA-13-COV-2-r1b.md`（changes_requested；P0=0/P1=1/P2=3/P3=3，P1 判定与 r1 独立吻合）
- 处置见 §Review 处置；SC-B01 ④ 裁决：`doc/reviews/FEA-13-COV-2-sc01-decision.md`
## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-COV-README | AC1–AC6 | `verification/FEA-13-COV-2/README.md` | `-` | `2bf601fd2576f9f5bde6c5ea2bd9852ae6891f3fb98ec24e11a2f2d887efef60` | CANONICAL |
| EV-COV-SUITE | AC1–AC4,AC6 | `verification/FEA-13-COV-2/logs/pytest-backup-suite.log` | `-` | `d03a08b96fd270028dd6e2a2d673ff1ae31eae53d774df98e0322355398911ca` | CANONICAL |
| EV-COV-MUT-SHA | AC5 | `verification/FEA-13-COV-2/logs/mutation-extras-sha.log` | `-` | `d0e681e6f0d2459b36c25d32443a574d3f4b384d7c0f01885395725509926830` | CANONICAL |
| EV-COV-MUT-WRITEBACK | AC5 | `verification/FEA-13-COV-2/logs/mutation-writeback.log` | `-` | `1c0cc4e9fbe917ff6a3846e469fd5f93bb5f9e3e4ab9934905dfb9bddf94ddde` | CANONICAL |
## 证据计划

| # | 命令/步骤 | 判别 |
|---|---|---|
| E1 | `python -m pytest tests/storage/test_nmbak_coverage.py tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_format.py -q` | 0 failed |
| E2 | 构造 data_root（settings/drafts/plugins/trash-manifest）+ create | 包内 extras 齐全、manifest 记录正确 |
| E3 | 删除/损坏 extras 成员后 restore | `BACKUP_CORRUPT`（sha/size 校验） |
| E4 | restore 后 data_root 字节比较 | 延迟写回、report `deferred_categories` |
| E5 | 变异（去掉 sha 校验 / 写回 extras） | 至少 1 例 RED；复原后绿 |
| E6 | `check.ps1` 默认 + `-TaskPath`；`verify_pins` | PASS / 18/18 |

## 风险与回退

- 包体变大（drafts/plugins 可能很大）→ manifest 记录 `extras_total_bytes`；大小策略归片 5，本片只保证覆盖。
- `data_root` 默认由 `backup_root.parent` 推断（`<data_root>/backups`），迁移钩子同样适用；显式传入优先。
- 回退：`git revert` 单提交；包格式向下兼容（旧包无 extras → v1/v2 adapter 均按空处理）。

## Review 处置（r1 + r1b，独立子代理）

> `doc/reviews/FEA-13-COV-2-r1.md`（P0=0/P1=1/P2=3/P3=4）与 `doc/reviews/FEA-13-COV-2-r1b.md`（P0=0/P1=1/P2=3/P3=3）独立审查、同一 P1 判定。

| Finding | 处置 |
|---|---|
| R-001（P1）空 `drafts`/`plugins` 目录被当错误 → create/restore/pre-migration 阻断 | **已修**：删除「空目录=缺失」判定；`_present_categories` 记录存在的类别根，`included_categories` 含空根、新增 `empty_categories`；仅真实收集错误才 `BACKUP_CREATE_FAILED`。补 4 例测试（空 drafts/plugins、`.lock` 排除、类别声明不一致、未知 extras 类别前向兼容）。 |
| R-002（P2）`.lock/pid`、`.tmp` 被打入包 | **已修**：`_collect_extras` 跳过 `.lock/` 目录与 `*.tmp`；测试断言包内无 `.lock`/`.tmp`。 |
| R-003（P2）AC3 测试绕过 `_skipped_categories` | **已修**：覆盖空目录成功路径 + 类别声明不一致 + 未知类别；monkeypatch 失败用例保留（真实 ACL 不可读无法在 CI 构造，登记 UNKNOWN）。 |
| R-004（P2）SC-B01 源授权元数据入包未落实未裁决 | **已裁决**：`doc/reviews/FEA-13-COV-2-sc01-decision.md`——本片不实现、单列 `FEA-13-SRC-6`（proposed 占位）；卡 `out_of_scope` 同步登记。 |
| R-005（P3）Handoff/README 空目录口径与卡冲突；AC5② 变异非卡面② | **已修**：口径统一为「空目录=合法 0 文件，仅收集错误失败」；补充**真实**「restore 写回 extras」变异日志（`logs/mutation-writeback.log`），AC5② 以该日志为准。 |
| R-006（P3）TASK_LEDGER 计数漂移 | **已修**：重跑 `task_ledger.py --write`。 |
| R-007（P3）类别字段未交叉校验、`skipped_categories` 恒空、未知类别前向兼容未定义 | **已修**：`_verify_package` 断言 `included_categories == extras ∪ empty_categories`、`skipped_categories` 为空；未知 extras 类别 → `BACKUP_FORMAT_UNSUPPORTED`。 |
| R-008（P3）extras 跟随符号链接 | **已修**：`_collect_extras` 跳过 `is_symlink()`；真实 ACL/符号链接回归列入残余（UNKNOWN）。 |
| P3 性能/IO（逐成员全量 read、extractall 解出 extras） | **登记残余**：不改变正确性；优化归后续片（与片 5 一起考虑）。 |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `892cb99df`） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | pytest 临时目录（`tmp_path`） | NOT_APPLICABLE | — | — | 测试隔离 fixture |
| build | NOT_APPLICABLE（纯 Python） | NOT_APPLICABLE | — | — | 无构建产物 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问真实库 |

## Closeout Record

## Closeout Record

- **2026-11-09 / DSH（关账）**：AC1–AC6 全部 MET；C-09 SC-B01a 覆盖清单二期落地（SC-B01 ④ 单列 FEA-13-SRC-6）。
- **Review**：r1 独立子代理 changes_requested（P0=0/P1=1/P2=3/P3=4）→ 处置；r1b 另一独立子代理 changes_requested（P0=0/P1=1/P2=3/P3=3，P1 独立吻合）→ 同批处置；r2 独立子代理 **approved**（FIXED 5 / PARTIAL 3 / OPEN 0；无新增 P0/P1）。
- **P1 修复**：空 drafts/plugins 不再阻断 create/restore/pre-migration（_present_categories + empty_categories；仅真实收集错误失败）。
- **P3 残余处置**：N-001 已同步 BK2-1 措辞（④ 单列裁决）；N-002 已加 junction/reparse point 防护；R-005 已补**真实**「复制包内 extras 字节写回」变异日志；R-004 由 FEA-13-COV-2-sc01-decision.md 裁决；性能/IO 优化（逐成员 read、extractall extras）登记至片 5。
- **门禁**：备份面 6 文件 **74 passed**（EXIT 0）；变异① 1 failed/3 passed、变异②（真实写回）1 failed/7 passed（均 EXIT 1，复原后 8 passed）；check.ps1 默认 + -TaskPath PASS（3 warnings）；verify_pins 18/18；ledger 一致。
- **交付/集成**：实现 `00f14179a`；r2 返修 `f86105707`（`integration_commit`）；本收口提交仅翻转状态与指针。
- **边界**：0 契约字节、0 pin 重算；diff ⊆ allowed_paths（core_assembly.py 仅 data_root 传参一处）。