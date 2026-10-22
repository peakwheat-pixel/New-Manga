---
task_id: SETTINGS-OPEN-C-1-DESIGN
kind: design
status: done
owner: dsh
reviewer: user（D1–D11 产品裁决）；独立 Review 待裁决后由 Codex 指派
created: 2026-10-23
base_commit: 49b0da564789a10186f51eb12cf605de5ba285f7
allowed_paths:
  - doc/design/**
  - doc/tasks/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# SETTINGS-OPEN-C-1-DESIGN — 批次 C 契约设计（回收站 / 备份恢复 / Plugin-Hooks）

## 目标

在**不写产品代码**的前提下，把批次 C 三节的契约、操作面、wire、安全边界与默认值冻结为设计文档，并给出需要用户裁决的决策清单（D1–D11）。用户裁决后，再分别释放 `SETTINGS-OPEN-C-1-RECYCLE` / `SETTINGS-OPEN-C-2-BACKUP` / `SETTINGS-OPEN-C-3-PLUGIN` 实现 Task。

## 范围（设计阶段）

交付 [SETTINGS_SECTION_C_SCHEMAS.md](../design/SETTINGS_SECTION_C_SCHEMAS.md)：

1. **回收站 `recycle_bin`（C-1）**：查看 + 清空**复用既有 wire**（`library_list_recycle_bin_books` / `library_delete_books_permanently`）；≤20/批、确认语义、整库保护原样提示；`auto_cleanup_days` 保留策略**不开放**（无调度消费点）。
2. **备份/恢复 `backup`（C-2）**：冻结 `.nmbak` 包格式 v1（manifest.json + library.db + sidecar + managed/ + revision_refs）、校验规则、恢复语义（覆盖 + 强制 pre_restore + running Run 拒绝）、新 wire（`backup_create/list/restore/delete`，可选 `backup_export`）与 Tauri 文件选择；`auto_backup` 等键不开放。
3. **Plugin/Hooks `plugins`（C-3）**：冻结安装来源（仅本地目录，U-3）、manifest v1、权限默认全关、fail-closed、崩溃隔离、审计、禁用默认值；无实现前 UI 只读"需要安装系统"。

## 硬纪律

- 三节的 `settings_get` / `settings_update_section` 写路径**均不开放**（P15 白名单不变）——没有消费点的设置键不写控件（`fill_color` 教训）。
- 设计阶段**禁止**改 `src/**`、`apps/**`、`tests/**`、冻结契约文本；禁止开放设置页控件。
- 危险操作（永久删除/恢复）必须 Core 侧强确认，UI 不得省略。

## AC

- [x] **AC1 回收站**：查看/清空复用既有 wire；≤20 分批、确认字段全等、整库保护；保留策略留空并写明"无调度消费点"。
- [x] **AC2 备份/恢复**：包格式 v1（含 manifest 字段表/校验规则/排除项）、恢复覆盖 + pre_restore + `BACKUP_RESTORE_BUSY`、4/5 条新 wire、Tauri dialog 文件选择、备份根固定。
- [x] **AC3 Plugin**：安装来源/目录、manifest v1 字段与拒绝规则、权限默认关闭 + C-3 仅无权限插件、崩溃隔离、审计、无实现前只读 UI 文案。
- [x] **AC4 决策清单**：D1–D11 每项含问题/选项/推荐/影响，明确"待用户裁决"。
- [x] **AC5 纪律与治理**：无产品代码改动；`check.ps1` PASS；设计文档与 Task 可追溯。

## 禁止范围

- 不实现回收站/备份/Plugin 任何产品功能。
- 不修改 P15 / M2-C1 冻结契约（实现 Task 时按 B-2 先例补增量注记）。
- 不新增 Schema/migration/依赖。

## 测试要求（设计阶段）

| 场景 | 命令 | 结果 |
|---|---|---|
| 治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | PASS（见交付记录） |
| 设计文档自洽 | 人工核对：wire 命令名/错误码/路径与既有实现一致 | PASS |

## 交付与运行记录

- 2026-10-23：dsh 盘点既有实现（`library_list_recycle_bin_books`、`library_delete_books_permanently` 的确认/分批/整库保护；`application/maintenance/backup.py` 协议与 `infrastructure/sqlite/backup.py` 实现；`extensions.md` §1.3 U-3 范围）后产出设计文档；待用户裁决 D1–D11。
- 未执行：任何实现/测试/UI 改动。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-C1-SETTINGS-SECTION-C-SCHEMAS|AC1-AC5|doc/design/SETTINGS_SECTION_C_SCHEMAS.md|6d6c08541cc9d92398bcb05fc5682ef4759fc4fd|1c141bd076c4ec58aaec495e2f6e3edb11e7567bd67a5bd14d4131ff2b8ed984|CANONICAL|
|EV-C1-SETTINGS-OPEN-C-1-DESIGN|AC1-AC5|doc/tasks/SETTINGS-OPEN-C-1-DESIGN.md|6d6c08541cc9d92398bcb05fc5682ef4759fc4fd|83351289eb93fee26c5a5ede5721137a278c0d3c206fe3000f6779aabe8f2e30|CANONICAL|

## Closeout Record

- Closeout：2026-10-23 关闭（用户确认 D1–D11 全部接受推荐值）；已释放 `SETTINGS-OPEN-C-1-RECYCLE`，C-2/C-3 按分期顺序另行释放。
- canonical_evidence_status：pending；resource_closeout_status：pending。
- 删除/迁移/归档：0。
- 当前指针清理：STATUS/REBASELINE/LEDGER 已登记本 Task。
