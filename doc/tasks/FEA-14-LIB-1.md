---
id: FEA-14-LIB-1
title: FEA-14 切片 LIB-1：书/章元数据编辑与顺序（复用 PREQ 预冻结 wire P5–P8）
kind: implementation
governance_version: 3
status: in_review
approval: **DSH 2026-11-10 冻结**（`ADJ-2026-11-10-FEA14-S5-SCOPE` §2.1/§2.2；PREQ-1 wire 预冻结 LIB P5–P8；侦察 `recon.md` §2.2）
suggested_owner: dsh
owner: dsh
reviewer: null
depends_on:
  - FEA-14-S5-PREQ-1
base_commit: 8e39bb72c
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-14-LIB-1
allowed_paths:
  - doc/tasks/FEA-14-LIB-1.md
  - doc/reviews/FEA-14-LIB-1-*.md
  - doc/handoffs/FEA-14-LIB-1-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/plan/FEA-C07_API_INVENTORY.md
  - doc/plan/FEA-CONTRACT-FROZEN-C07.md
  - verification/FEA-14-LIB-1/**
  - src/application/library/service.py
  - src/application/library/ports.py
  - src/infrastructure/sqlite/library.py
  - src/bootstrap/core_assembly.py
  - src/bootstrap/core_service.py
  - apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs
  - tests/storage/test_library_metadata.py
  - tests/core/test_library_wire.py
out_of_scope:
  - 不引入 Volume 实体（PREQ 未纳入；另行裁决）
  - 不改冻结契约字节（C-07 统计节按实现落地更新，pin 重算须记录）
  - 不做批量重排 UI（只做数据面 + 既有命令）
  - 不修改 FEA-15 正式验收声明
---

# FEA-14-LIB-1：书/章元数据编辑与顺序

## 背景

FEA-14 S5 LIB 切片（FEA-00 §12.2/§15.6）需要书/章元数据编辑与章顺序：`UpdateBookMetadataAsync`/`ReorderChaptersAsync`/`UpdateChapterMetadataAsync`/`CreateChapterWithMetadataAsync`（PREQ §3/§8 P5–P8，minor 3）。现有库已能创建书/章，但缺元数据 patch/重排/chapter kind。

## Scope 冻结（2026-11-10，DSH）

1. Core：`LibraryMetadataService`（书 patch：title/author/series_title/description/notes/tags；章 patch：kind/custom_rank/number/title/subtitle/notes；重排：ordered_ids 全量校验；创建带元数据章）。
2. 数据面：`books` 加 `author/series_title/description/notes` 列（additive migration v12）；`chapters.custom_rank` 列；`book_tags` 既有表复用。
3. Host：P5–P8 四条命令（additive；旧签名不变），按 C-07 冻结记录流程更新 inventory 并重算 pin。
4. 证据：pytest 定向/全量、App.Tests、check/pins/API inventory。

## Acceptance Criteria

- [x] **AC1 书元数据**：patch 部分字段（其余保留）；title 非空校验；tags 替换语义；无书 → typed 错误。 <<MET>>
- [x] **AC2 章元数据**：kind（paged/webtoon）/custom_rank/number/title/subtitle/notes 更新；非法 kind 拒绝；无章 → typed。 <<MET>>
- [x] **AC3 章重排**：`ordered_ids` 必须覆盖全书章（缺/多/重复 → typed）；sort_order 连续重写；重排后读取顺序一致。 <<MET>>
- [x] **AC4 创建带元数据章**：title/kind/number/import_order 落库；返回 chapter_id/title/kind/number；父书不存在 → typed。 <<MET>>
- [x] **AC5 迁移/契约/门禁**：v12 additive（旧行字段级无损）；P5–P8 按 PREQ §8 形状；`generate_api_inventory.py --check` EXIT 0；`verify_pins` 18/18（C-07 pin 更新记录）。 <<MET>>
- [x] **AC6 证据**：定向 pytest/App.Tests 通过；`verification/FEA-14-LIB-1/` 日志含 EXIT；NOT_RUN（LIB-2 UI/Volume 实体）如实登记。 <<MET>>

## 证据计划（L2）

`verification/FEA-14-LIB-1/`：`logs/`（pytest 定向/全量、App.Tests、门禁、API inventory、pins、v12 回归）、迁移前后字段表、NOT_RUN、复现命令。

## 风险与回退

| 风险 | 处置 |
|---|---|
| 元数据覆盖用户手改 | patch 只改提供字段；测试断言未提供字段保留 |
| 重排丢章 | 全量覆盖校验（缺/多/重复 → typed，不改库） |
| 迁移风险 | v12 additive + pre_migration 备份 + 失败即停 |
| 旧行无损 | 迁移前后字段级对比测试 |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| temp | `G:\CODEX\New Manga.workspace\FEA-14-LIB-1\`（隔离数据根） | NOT_APPLICABLE | — | — | 仓外，不提交 |
| user-data | `%APPDATA%\com.newmanga.desktop` | NOT_APPLICABLE | — | — | 只读；测试用隔离根 |
| build | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 复用现有环境 |
| worktree | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 主树实现 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-LB-001 | LIB-1 | `verification/FEA-14-LIB-1/logs/dotnet-app-tests.log` | `-` | `4987dccef65de79af3491054ee4990d6008ba723c77dc4d3adba554eb5f33da5` | CANONICAL |
| EV-LB-002 | LIB-1 | `verification/FEA-14-LIB-1/logs/pins-api.log` | `-` | `6546b28c059bc7abb357decb6976061db20b344a4b45e17dba218a05d7822c6b` | CANONICAL |
| EV-LB-003 | LIB-1 | `verification/FEA-14-LIB-1/logs/pytest-lib.log` | `-` | `ce38561c691b5c16c8fdb233738783c531ee810c99826a190bb197191a166ed0` | CANONICAL |
| EV-LB-004 | LIB-1 | `verification/FEA-14-LIB-1/logs/regression-v12.log` | `-` | `2723cbd1f3c7f45cd5b5510619e480f7dfdd879ad57077dc18d8372b1db0e1fd` | CANONICAL |
| EV-LB-005 | LIB-1 | `verification/FEA-14-LIB-1/README.md` | `-` | `c4580ee64982b33c1d0ff668db4fdc49a0c7bacbd09753c2386183268ed2bc4a` | CANONICAL |

## Closeout Record

- 未开始（2026-11-10 scope 冻结，`ready`）。
