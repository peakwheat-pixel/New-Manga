---
id: FEA-14-AI-1
title: FEA-14 切片 AI-1：提示词模板（复用 PREQ 预冻结 wire P21–P25）
kind: implementation
governance_version: 3
status: in_review
approval: **DSH 2026-11-10 冻结**（`ADJ-2026-11-10-FEA14-S5-SCOPE` §2.1/§2.2；PREQ-1 wire 预冻结 AI P21–P25；DDL v10 计划 §2.4）
suggested_owner: dsh
owner: dsh
reviewer: null
depends_on:
  - FEA-14-S5-PREQ-1
base_commit: 36c4376d1
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-14-AI-1
allowed_paths:
  - doc/tasks/FEA-14-AI-1.md
  - doc/reviews/FEA-14-AI-1-*.md
  - doc/handoffs/FEA-14-AI-1-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/plan/FEA-C07_API_INVENTORY.md
  - doc/plan/FEA-CONTRACT-FROZEN-C07.md
  - doc/reviews/CONTRACT-UNFREEZE-*.md
  - verification/FEA-14-AI-1/**
  - src/domain/ai/**
  - src/application/ai/**
  - src/infrastructure/sqlite/prompt_templates.py
  - src/infrastructure/sqlite/schema.py
  - src/bootstrap/core_assembly.py
  - src/bootstrap/core_service.py
  - apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/PromptTemplatePortTests.cs
  - tests/storage/test_prompt_templates.py
  - tests/core/test_prompt_template_wire.py
  - tests/storage/test_fonts.py
  - tests/storage/test_issue_markers.py
  - tests/storage/test_upgrade_schema_data.py
  - tests/fea09/test_v7_migration.py
  - tests/fea11/test_source_gate_unify.py
out_of_scope:
  - 不触发任何网络/AI 模型调用（PREQ §6：本清单不触发网络/AI 调用）
  - 不做模板 UI/编辑器/预览（AI-2/UI 卡）
  - 不创建译文/任务/规则对模板的引用（引用表本卡只提供读取与删除重指派；写入方留给后续卡）
  - 不改冻结契约字节（C-07 统计/成员表按实现落地更新，pin 重算须记录）
  - 不修改 FEA-15 正式验收声明
---

# FEA-14-AI-1：提示词模板

## 背景（PREQ 预冻结 wire P21–P25）

FEA-14 S5 AI 切片需要「提示词模板」数据面：列出（内置只读 + 自建）、保存自建、删除（须选替代）、复制内置、删除前引用清单（PREQ §6/§8 P21–P25，minor 3）。现有代码无模板实体/表；DDL v10 计划 §2.4 给出目标形状：内置模板不落库（Core 常量，只读、可复制），自建模板落 `prompt_templates`，删除前检查引用并须选替代。

## Scope 冻结（2026-11-10，DSH）

1. Core 数据面：schema **v14** additive 新表 `prompt_templates`（`template_id` PK、`name` 唯一、`body`、`version`（每次保存 +1）、`created_at`、`updated_at`、`deleted_at` 软删）+ `prompt_template_references`（`template_id`、`kind`、`owner_id`、`label`；本卡只读取/重指派，不创建）+ 索引；v1–v13 迁移字节不变。
2. 内置模板：Core 代码常量（只读、不可 P22 覆盖/不可 P23 删除），`List` 合并投影并回 `builtin_count`；P24 复制为自建副本（version=1）。
3. wire：P21 `ListPromptTemplatesAsync {}` → `{templates:[{template_id,name,version,builtin}],builtin_count}`；P22 `SavePromptTemplateAsync {template_id?,name,body}` → `{template_id,version}`；P23 `DeletePromptTemplateAsync {template_id,replacement_id}` → `{deleted:true}`；P24 `CopyBuiltinPromptTemplateAsync {builtin_id,name?}` → `{template_id}`；P25 `GetPromptTemplateReferencesAsync {template_id}` → `{references:[{kind,owner_id,label}]}`。错误一律 typed。
4. Host：`IHostController` +5 方法（additive，旧签名不变）+ DTO（`PromptTemplateInfo`/`PromptTemplateDeleteResult`/`PromptTemplateReference`）+ HostRuntime/CoreServiceClient/HostController/NullHostController/Fake。
5. 契约：按 C-07 冻结记录流程 UNFREEZE 统计（`IHostController` 74→79、合计 81→86）并把 P21–P25 并入正式成员表、S5 计划节清空、重算 pin。
6. 证据：定向 pytest、v14 回归、App.Tests、`check.ps1`/`verify_pins`/API inventory、v1–v13 迁移字节比对。

## 裁决（PREQ 歧义，DSH 2026-11-10）

- **P23 替代语义**：`replacement_id` **必填**且必须存在、不得等于目标模板；若目标仍有引用，在同一事务内把引用重指派到 replacement 后软删目标；无引用同样要求 replacement（PREQ 字面「必须带替代 id」），缺失/无效 → `INVALID_REQUEST`/`TARGET_NOT_FOUND`。
- **内置模板**：只读；P22 指向内置 id → typed 拒绝；P23 删除内置 → typed 拒绝；P24 以 `builtin_id` 复制为自建（`name` 缺省 = 内置名 + " copy"，重名 → typed 拒绝）。
- **版本**：自建模板 `version` 从 1 起，P22 更新已存在模板时 `version+1`（不可回退、不可指定）；`name` 全局唯一（软删后不占用）。
- **引用表**：本卡不创建引用行；P25 对无引用模板返回空数组，P23 的重指派路径用测试 fixture 直接插入引用行验证。

## Acceptance Criteria

- [x] **AC1 数据面/v14**：`prompt_templates`（唯一 name、version、软删）+ `prompt_template_references` additve 建表 + 索引；v1–v13 迁移 NAME/SQL 逐字节不变；旧库升级行级无损；repository 五路径一致。 <<MET>>
- [x] **AC2 P21/P24 列表与复制**：列表 = 内置常量 + 未软删自建（`builtin` 标记、`builtin_count` 正确）；P24 复制内置得到自建副本（version=1、name 缺省/重名规则）。 <<MET>>
- [x] **AC3 P22 保存**：新建（version=1）与更新（version+1）、`name` 唯一（重名 typed `TEMPLATE_NAME_EXISTS`/conflict）、body 非空、内置不可覆盖。 <<MET>>
- [x] **AC4 P23/P25 删除与引用**：P25 列出 `{kind,owner_id,label}`；P23 强制 replacement（缺失/无效/等于自身/内置 → typed），引用重指派后软删（引用行指向 replacement、目标不再可见）。 <<MET>>
- [x] **AC5 契约/门禁**：C-07 UNFREEZE **v1.8**（79/86）成员表逐行 = 脚本 stdout（`ALL_MATCH: True`）、S5 计划节 25/25 全部落地无待实现行、pin `58dbae4c…`；`--check` EXIT 0；`verify_pins` 18/18。 <<MET>>
- [x] **AC6 证据**：定向 pytest/回归/App.Tests 通过；`verification/FEA-14-AI-1/` 日志含 EXIT；NOT_RUN 如实登记。 <<MET>>

## 实现说明（2026-11-10）

- **wire 形状**：P21 `{}` → `{templates:[{template_id,name,version,builtin}],builtin_count}`；P22 `{template_id?,name,body}` → `{template_id,version}`；P23 `{template_id,replacement_id}` → `{deleted:true}`；P24 `{builtin_id,name?}` → `{template_id}`；P25 `{template_id}` → `{references:[{kind,owner_id,label}]}`。
- **typed 错误**：不存在（模板/内置/替代）→ `TARGET_NOT_FOUND/not_found`；名称重复 → `TEMPLATE_NAME_EXISTS/conflict`；字段/内置只读/自替代/空 replacement → `INVALID_REQUEST/validation`；无 `UNKNOWN/internal` 逃逸（service 只抛 `PromptTemplateError`）。
- **数据面**：schema **v14** 仅新增 `prompt_templates` + `prompt_template_references` + 两索引；name 唯一索引仅覆盖未软删行（软删不占用名字）；v1–v13 迁移字节不变。
- **内置模板**：Core 常量（`BUILTIN_PROMPT_TEMPLATES`，本卡 2 条），不落库；P21 合并投影回 `builtin_count`；P22/P23 对内置 id typed 拒绝；P24 复制为自建 version=1（缺省名 `"<builtin> (copy)"`）。
- **删除语义**：P23 强制 replacement（必填、存在、非自身、非内置）；引用行在同一事务 `UPDATE OR REPLACE` 重指派后目标软删；引用表由后续卡（译文/任务/规则）写入，本卡不创建。
- **C-07**：UNFREEZE v1.8（74→79 / 81→86），S5 计划 **25/25 全部落地**；pin `58dbae4c…`。
- **Host**：`IHostController` 5 方法 + DTO（`PromptTemplateInfo`/`PromptTemplateDeleteResult`/`PromptTemplateReference`）六处一致；NullHost 降级返回空/false/null 不抛；P24 客户端仅得 `template_id`（Core 侧分配 name 由 P21 刷新，登记 limitation）。

## 证据计划（L2）

`verification/FEA-14-AI-1/`：`logs/`（pytest 定向/全量、App.Tests、pins/api、v14 回归）、NOT_RUN、复现命令。

## 风险与回退

| 风险 | 处置 |
|---|---|
| 内置模板被覆盖/删除 | service 层按 `builtin` 标记 typed 拒绝；测试固化 |
| 删除模板留下悬空引用 | P23 同一事务重指派后再软删；测试断言引用行指向 replacement |
| 名称唯一冲突 | DB 唯一索引 + service typed 拒绝；软删不占用名字 |
| 迁移风险 | v14 additive + pre_migration 备份 + 失败即停 |
| 旧行无损 | v14 只加新表 + 索引；升级前后行级快照比较 |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| temp | `G:\CODEX\New Manga.workspace\FEA-14-AI-1\`（隔离数据根） | NOT_APPLICABLE | — | — | 仓外，不提交 |
| user-data | `%APPDATA%\com.newmanga.desktop` | NOT_APPLICABLE | — | — | 只读；测试用隔离根 |
| build | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 复用现有环境 |
| worktree | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 主树实现 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-AI-001 | AI-1 | `verification/FEA-14-AI-1/logs/dotnet-app-tests.log` | `-` | `9e0b27e3f6b6cd2c95fdb4a036571bb204d54835db20a99132d2bcbaa32236b7` | CANONICAL |
| EV-AI-002 | AI-1 | `verification/FEA-14-AI-1/logs/pins-api.log` | `-` | `5dc7a4ba377c2cf6f6ca5b622f5be206b9aac0282b5f1248a57aee96aa22b9f2` | CANONICAL |
| EV-AI-003 | AI-1 | `verification/FEA-14-AI-1/logs/pytest-ai.log` | `-` | `656c9f3f64b0e2753a2b6c67b33e21b7f6f27bb26bbd0eb7fe38b7b58b367b5a` | CANONICAL |
| EV-AI-004 | AI-1 | `verification/FEA-14-AI-1/logs/regression-v14.log` | `-` | `bc9cfe64c67504afb7eeed171ec30ca20e8bc2e7daa0cabcccfea8df81307e7c` | CANONICAL |
| EV-AI-005 | AI-1 | `verification/FEA-14-AI-1/README.md` | `-` | `aa51cfd07adf05fc41ddabe5b16dd61d7a4be6dde110d79fa7f8f4aa3945b657` | CANONICAL |

## Closeout Record

- 2026-11-10 scope 冻结（`ready`）→ 实现（schema v14 + `PromptTemplateService` + wire P21–P25 + Host 六处 + C-07 v1.8）→ **r1 独立复核待派发**。未 push。
