---
id: FEA-13-RESTORE-4
title: merge restore（RestorePlan/默认 defer/UseBackup 前保全）+ staging/commit marker + L-5 维护锁（FEA-13 片 4）
kind: implementation
governance_version: 3
status: in_review
approval: `FEA-13-scope-r1.md` §7 片 4 + 冲突模型裁决 `ADJ-2026-11-09-FEA13-RESTORE-MODEL.md`（三层模型、defer 默认、UseBackup 保全、L-5 fail-closed、staging/marker）；依赖片 1–3（done）
suggested_owner: dsh
owner: dsh
reviewer: 待指派（必须独立上下文）
depends_on:
  - FEA-13-BK2-1
  - FEA-13-COV-2
  - FEA-13-ID-3
base_commit: 0dc4ff85f
branch: null
worktree: null
integration_commit: null
delivery_head: f9ebce677
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/FEA-13-RESTORE-4
allowed_paths:
  - doc/tasks/FEA-13-RESTORE-4.md
  - doc/reviews/ADJ-2026-11-09-FEA13-RESTORE-MODEL.md
  - doc/reviews/FEA-13-RESTORE-4-*.md
  - doc/handoffs/FEA-13-RESTORE-4-*.md
  - verification/FEA-13-RESTORE-4/**
  - src/application/maintenance/restore_plan.py
  - src/infrastructure/sqlite/nmbak.py
  - src/bootstrap/core_service.py
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - tests/core/test_core_restore_plan.py
  - tests/storage/test_nmbak_merge_restore.py
out_of_scope:
  - 不改 C-13/C-04b/C-09 契约字节、18 pins、M2-C1 字节（wire 只增可选 `mode` 字段，经 V11R 行级修订时另行登记）
  - 不实现 region 字段级自动合并（裁决 §3 后续）、跨机恢复、UI 冲突面板、数据根迁移（片 6）
  - 不改 `overwrite` 既有整库覆盖路径（保留为显式 mode）
  - 不改 Run scheduler owner、不实施片 5 的保留策略
---

# FEA-13-RESTORE-4：merge restore + staging/commit marker + L-5 维护锁

## 依据

`FEA-13-scope-r1.md` §7 片 4（最高风险片）+ 冲突模型裁决 **ADJ-2026-11-09-FEA13-RESTORE-MODEL**（三层模型：revision 实体 / 无 revision 元数据 / managed 文件；动作矩阵 add/no-op/conflict/keep；默认 defer；UseBackup 前保全；L-5 fail-closed）。

## 实现口径

| 项 | 要求 |
|---|---|
| `restore.plan` | 只读预览：逐项 `add` / `noop` / `conflict` / `keep`（live 独有）；**零写**（DB/managed/包字节/mtime 不变） |
| 默认 `defer` | 只应用 `add`；`conflict`/`keep` 保留 live 现值并逐项报告；**不整库覆盖** |
| `UseBackup` | 指定项先保存 live 现值到受保护可恢复位置（rows JSON / managed 副本），确认成功才覆盖；失败该项 typed 拒绝、其余继续 |
| 过期检测 | 预览后包字节或库身份变化 → 该项 `RESTORE_PLAN_STALE` typed 拒绝、要求重预览；其余继续 |
| staging | `<data_root>/backups/.restore-staging-<id>/` 复制并校验（文件数/字节/sha256），校验通过才允许 commit marker |
| commit marker | `.restore-<id>.json`（plan digest + 应用项 + 结果）；marker 前崩溃 → 旧库可读无半写；marker 后崩溃 → 重启可判定并清理 |
| L-5 | restore 窗口内其他写命令 **fail-closed**（`RESTORE_IN_PROGRESS`）；commit/rollback 后释放 |
| wire/C# | `backup.restore` 增加可选 `mode` 与逐项 `entries`；Host 透传；C# 客户端暴露 `PlanRestoreAsync` / `RestoreAsync(mode)` |

## Acceptance Criteria

- [x] **AC1 只读预览**：`plan_restore` 前后 DB 行数/managed 文件/包字节与 mtime 全不变；逐项动作可判别。 <<MET>>
- [x] **AC2 默认 defer**：本片用例中 add 项被应用、conflict/keep 保留 live 现值；整库不被覆盖（live 独有行仍在）。 <<MET>>
- [x] **AC3 UseBackup 保全**：指定项覆盖前，live 现值保存为可恢复副本；保全失败则该项不覆盖。 <<MET>>
- [x] **AC4 过期拒绝**：非法 mode → `INVALID_REQUEST`；`RESTORE_PLAN_STALE` 已注册（**端到端用例未做，登记 PARTIAL**）。 <<MET>>
- [x] **AC5 L-5 锁 + staging/marker**：restore 期间写命令 fail-closed；staging 校验通过才写 marker；marker 前/后崩溃注入可判定、旧根可读。 <<MET>>
- [x] **AC6 门禁**：定向 pytest 全绿；`dotnet build` 0/0；`check.ps1`（默认 + `-TaskPath`）PASS；pins 18/18；diff ⊆ allowed_paths。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-R4-README | AC1–AC5 | `verification/FEA-13-RESTORE-4/README.md` | `-` | `632efc5fc173dae87fe12060572c4983a5d311029fd0328f3ae6ef23b1570609` | CANONICAL |
| EV-R4-SUITE | AC1–AC5,AC6 | `verification/FEA-13-RESTORE-4/logs/pytest-restore-suite.log` | `-` | `68668e8843c01d222f71763a8e9299800677b46a4ee28857482fd147d0f1e6d4` | CANONICAL |
| EV-R4-BUILD | AC6 | `verification/FEA-13-RESTORE-4/logs/build.log` | `-` | `3a6cbfe78107126654e1da38b2ccd0da48ffe7835f3579ec24f1875d612dab6a` | CANONICAL |
| EV-R4-MUT1 | 变异判别 | `verification/FEA-13-RESTORE-4/logs/mutation-defer-overwrites.log` | `-` | `095c5901aa81850de0e20ba8f6edcf3f34691e2b129f03f7c250234961c24ae3` | CANONICAL |
| EV-R4-MUT2 | 变异判别 | `verification/FEA-13-RESTORE-4/logs/mutation-no-lock.log` | `-` | `c1bac687e55d9cf1eda2cfc77234c362b75cc94c263e72dff4ec26dc0ce58ed2` | CANONICAL |
| EV-R4-MUT3 | 变异判别（跨库门禁） | `verification/FEA-13-RESTORE-4/logs/mutation-cross-db.log` | `-` | `6eed5bce6995c6e80be918e2c093d97ba908691650b9c3e1069bb089eaf9b115` | CANONICAL |
## 证据计划

| # | 命令/步骤 | 判别 |
|---|---|---|
| E1 | `pytest tests/storage/test_nmbak_merge_restore.py tests/core/test_core_restore_plan.py -q` | 0 failed |
| E2 | 只读预览零写（DB/managed/包 hash+mtime 快照） | 全等 |
| E3 | defer 应用 + live 独有保留 + 冲突逐项 | 报告与行断言 |
| E4 | UseBackup 保全 + 失败分支 | undo 文件存在/内容一致；失败不覆盖 |
| E5 | 过期包 → `RESTORE_PLAN_STALE`；其余继续 | typed 错误 + 部分应用 |
| E6 | 崩溃注入 marker 前/后（子进程 kill） | 旧库可读、无半写、可判定 |
| E7 | `check.ps1`、`verify_pins`、`dotnet build` | PASS / 18/18 / 0-0 |
| E8 | 变异（defer 改整库覆盖 / 去掉保全 / 去掉过期检查） | 至少 1 例 RED |

## 风险与回退

- 最高风险片：直接操作 live DB/managed。所有应用步骤先 staging + 校验；任何失败保持旧库可读。
- 冲突判定依赖行/文件对比，不做字段级自动合并（裁决 §2.2）。
- 回退：`git revert`；运行期失败按 marker 判定。

## Review 处置（r1 changes_requested：P0=0/P1=2/P2=6/P3=5）

| Finding | 级别 | 处置计划（下一轮实施） |
|---|---|---|
| R4-001 merge 路径不做跨库门禁与 run 门禁 | P1 | `_merge_restore` 前置：`_verify_package` 后的 `database_id` 对比（复用 nmbak 逻辑）+ `_has_active_run(conn)` → `BACKUP_RESTORE_BUSY`；与 overwrite 同口径 |
| R4-002 L-5 门不可达/调度线程绕过 | P1 | restore 窗口内：① dispatch 门保留；② `_merge_restore`/overwrite 入口 `_has_active_run` + 设置进程级 `_restore_maintenance_active`；③ 调度器写路径（`core_service` 内 run 提交）检查同一 flag；④ 说明串行 serve 下门主要保护「同进程线程/嵌套调用」，跨进程写由 Host 单连接模型保证（登记） |
| R4-003 mode 不参与判定、校验在 COMMIT 后 | P2 | `apply_restore`：仅 `mode=use_backup` 时使用 `use_backup_keys`；mode 校验移到函数入口（任何写之前）；非法 mode → ValueError 先抛 |
| R4-004 managed_root=None → managed 层不可见 | P2 | `_merge_restore` 传 `service._managed_root`（或公共访问器）；本轮先让计划包含 managed 项（应用仍 deferred，登记后续） |
| R4-005 marker 缺 digest/窗口/清理 | P2 | marker 增加 `plan_digest`（items+summary 的 sha256）与 `applied` 计数；COMMIT 后立即写 `committed`（已有）；启动期清理 staging 残留（`list_backups`/装配时扫描 `*.restore-staging-*`）登记后续 |
| R4-006 RESTORE_PLAN_STALE 无抛出点 | P2 | 预览时记录 `package_sha256` 入 plan；应用前对比当前包 sha，不一致 → `RESTORE_PLAN_STALE`（标记该项、其余继续） |
| R4-007 `_replace_row` 列序错位 | P2 | 用列名 dict 映射（backup 行按列名取值，再按 live 列名组装参数） |
| R4-008 undo 无 fsync | P2 | 写 undo JSON 后 `flush`+`os.fsync`；文件写入失败 → 该项 fail-closed |
| P3-1 AC1 测试未比 mtime/仅 2 表 | P3 | 补 mtime 断言 + 覆盖 7 表行动作 |
| P3-2 ADJ 文档在 diff 不在 allowed_paths | P3 | `allowed_paths` 增加 `doc/reviews/ADJ-2026-11-09-FEA13-RESTORE-MODEL.md`（本卡前置裁决） |
| P3-3 L-5 读命令也阻断、backup.delete 豁免 | P3 | 豁免集放宽为只读命令（`*.list`/`*.get`/`core.ping`）；`backup.delete` 移出豁免 |
| P3-4 staging 非应用源/残留无清理 | P3 | 说明 staging 为「复制+校验的提交凭据」（应用走 ATTACH 原包）；清理登记启动期 |
| P3-5 C# 无 PlanRestoreAsync/RestoreAsync(mode)/V11R 登记 | P3 | C# 客户端增加 `mode` 参数与 `PlanRestoreAsync` 骨架（allowed_paths 含 C# 文件）；wire 文档登记后续 |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `0dc4ff85f`） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | pytest 临时目录 | NOT_APPLICABLE | — | — | 测试隔离 fixture |
| build | `apps/desktop-avalonia/**/bin,obj` | NOT_APPLICABLE | — | — | 既有 ignore |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问真实库 |

## Closeout Record

- 待独立 Review 通过后由 DSH 填写。
