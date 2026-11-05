# Handoff — FEA-12-CORE 分片 A（Python Core）

- Task: `doc/tasks/FEA-12-CORE.md`（status: in_review，分片 A；Lead 集成）
- Owner: `fea12-core-py`（DSH Agent Teams teammate）
- 交付日期：2026-11-05（Asia/Shanghai）
- 释放 base：`e47fd47e4`（释放 commit `c8d9adc8d`）；门禁实跑工作树基于 Lead 收口 commit `564bc0760`
- 范围：`doc/reviews/ADJ-2026-11-05-FEA-12-SCOPE.md` D1–D8；wire：M2-C1 rev 2.13（FEA-12-PREREQ-1 done）
- 分片 B：`.NET Host 桥 + R-002` 由 `fea12-core-host` 交付（`verification/FEA-12-CORE/core-host-*`），本分片不改 .NET

## 1. Commit 列表（仅本卡 allowed_paths）

> 实际 SHA 见本文件所在 commit 及 `git log --oneline -- doc/tasks/FEA-12-CORE.md`；两个 commit：
>
> 1. `feat(fea-12-core): Python Core A/C 删除流程（软删/恢复/ListTrash + preview/digest/单事务/X1/PD-08）` — 源码 + 测试
> 2. `docs(fea-12-core): 分片 A 实施记录/AC 证据/门禁日志/任务卡/Handoff` — 证据 + 卡 + Handoff
>
> 只 add 了：`src/application/library/service.py`、`src/application/maintenance/ports.py`、
> `src/domain/books/entities.py`、`src/infrastructure/sqlite/library.py`、`src/bootstrap/core_service.py`、
> `tests/core/test_core_delete_commands.py`、`tests/core/test_core_delete_preview_commands.py`（新）、
> `tests/core/test_core_trash_commands.py`（新）、`tests/core/test_core_service.py`、
> `tests/storage/test_purge_integrity.py`、`tests/fea12/test_core_delete_protection.py`（新）、
> `doc/tasks/FEA-12-CORE.md`、`doc/handoffs/FEA-12-CORE-core-py.md`、`verification/FEA-12-CORE/**`（本分片文件）。
> 未 commit：`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/reviews/**`（Lead-owned）、
> 分片 B 的 .NET/证据、DSIM-1 文件；未 push。

## 2. 交付摘要

### A 流程（AC1–AC3）
- `Book.restore()`：只清 `deleted_at`；repo 单语句 `move_book_to_trash` / `restore_book_from_trash` /
  `list_trash_entries`；Core `MoveToTrash` / `RestoreFromTrash` / `ListTrash`（minor 13、closed shape、
  `idempotency_key`、opaque cursor、逐项原子、`skipped`/`conflicts` 不整批失败）。
- `ListRecycleBinBooks` 冻结投影零改动（空数组≠失败、`page_count` None 通道）。

### C 流程（AC4–AC9）
- `PreviewPermanentDeleteBooks`（minor 11）：PD-01 全披露字段；零写；canonical digest（C-04b §2.1）+
  集合级有序拼接 sha256；`currentRevisionId` 过 lineage guard 取首个可见 region。
- delete 命令 `inventory_digest`/`inventory_digests` 必填 + 两级校验（缺失/格式→`INVALID_REQUEST`；
  不匹配→`BOOK_DELETE_STALE_PREVIEW` 零副作用）。
- `execute_permanent_delete_db`：显式 `BEGIN IMMEDIATE` 单事务；失败整体回滚、不开始文件清理；
  D1 X1 同事务删 `source_binding_publications`→`source_revision_lineage`→`page_bindings`（plans/operations 保留）；
  非终态 source operation 写边界复检 `BOOK_BUSY`。
- PD-08：共享文件保留、目标行删除、跨项目 `source_artifact_revision_id` 悬挂指针置 NULL；
  仅不可安全拆分/关系图不一致 → `BOOK_DELETE_CONFLICT`。
- PD-07：`cleanup_pending` manifest + 显式重试（含批量逐项），不后台自动重试。
- `PurgeTrash`：首版不实现，typed `UNKNOWN_COMMAND`（validation/false）零副作用；capability
  `library.trash.write/1` 仅代表 Move/Restore 可用。

### 统一 ProtectionPolicy（AC10）
- `ProtectionPolicy.evaluate(scope, facts)` 唯一判定（`application/maintenance/ports.py`，不 import infrastructure）；
  软删不阻断、自动清理保护人工成果、彻底删除披露不阻断（仅 active op/unsafe shared 阻断）。

### 命令面（AC11 Python 侧）
- `core.ping` 在 library repository+storage 装配时公告 `library.delete.preview/1`、
  `library.trash.read/1`、`library.trash.write/1`（最小手搭 Core 不公告，`tests/fea09` 不变）。
- preview minor 11 / trash minor 13 / delete minor 10；错误 envelope 与既有 delete 族同形。

## 3. AC 状态（分片 A）

| AC | 状态 | 依据 |
|---|---|---|
| AC1–AC10、AC12 | **MET** | `verification/FEA-12-CORE/core-py-implementation-record.md` §4 逐条证据 + `logs/core-py-ac*.log` |
| AC11 | **PARTIAL（Python 侧 MET）** | Core capability/dispatch/closed shape/typed unsupported 已实跑；.NET registry/dispatcher/client 与 R-002 二选一归 `task-7`，Lead 集成时合并定稿 |

## 4. 门禁实跑（命令/EXIT/数字）

| 门禁 | 命令 | EXIT | 结果 |
|---|---|---|---|
| 相关组 | `C:/Python314/python.exe -m pytest tests/core tests/storage tests/maintenance tests/fea12 -q -p no:warnings` | 0 | **1096 passed** |
| 全量 pytest | `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no` | 0 | **3144 passed / 10 skipped**（基线 3093/10；+51 本卡） |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 0 | **18/18 PASS** |
| 治理 check | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE.md` | 0 | **PASS（4 warnings，均既有/分片 B 证据登记待 Lead 合并）**；最终一次复跑见 §6 |
| golden 向量探针 | `C:/Python314/python.exe verification/FEA-12-CORE/scripts/core_py_inventory_digest.py` | 0 | `all_match: true` |
| 隔离扫描探针 | `C:/Python314/python.exe verification/FEA-12-CORE/scripts/core_py_isolation_scan.py` | 0 | `pass: true` |
| 全量 .NET | 分片 B 已跑：`logs/core-host-dotnet-full-1.log` / `-2.log` | — | 本分片零 .NET 改动；Lead 集成复跑 |

门禁全文：`verification/FEA-12-CORE/logs/gates-core-py.log`。

## 5. 预期行为变更（Review 不判回归）

1. **digest 必填**（§5.11.1a）：既有 delete 测试改为先 Preview 再回传 digest；旧 Host 不传 →
   `INVALID_REQUEST` fail-closed，不降级软删。
2. **PD-08**：共享引用可安全拆分不阻断（原 `test_core_delete_commands.py:323,378` 期望按 ADJ D3 更新）；
   共享文件/binding 保留、跨项目 provenance 置 NULL；仅不可拆分才 `BOOK_DELETE_CONFLICT`。
3. **page 级 purge** 补 C-17 v7/v8 子图（`test_purge_integrity` fixture 补行，D1 X1 同语义）。
4. **capability 新增 3 名**（生产装配断言更新；最小手搭 Core 不公告）。

## 6. 集成注意事项 / 残余风险

1. **分片 B 衔接**：Core 已按冻结 wire 提供 preview(11)/trash(13)/delete(10+digest) 与 3 capability；
   Host 侧需按 task-7 完成 capability probe（缺失→`CORE_CAPABILITY_MISSING`）与 R-002 处置。
   旧 Host 对 delete 不传 digest 会被新 Core `INVALID_REQUEST` 拒绝（预期 fail-closed）；
   新 Host 对旧 Core 的负向对照以 PREREQ-1 证据为准。
2. **`activeRunIds` 不含 active export**（wire 无字段）：export 仍是 `BOOK_BUSY` 阻断项，但不在
   preview 披露列表——wire 冻结缺口，未擅自扩字段。
3. **`deletedBytes` 以实际文件 stat 计**：预览→确认间文件变化会触发 STALE（PD-04 预期）；大书预览有 stat 成本。
4. **page 级 purge 的跨页 lineage 外键**：out-of-target lineage 引用被 purge revision 时 FK 整事务回滚
   （fail-closed；应用层当前不可产生）；book 级 C 流程对该类关系按 PD-08 预检 CONFLICT。若 Review
   发现 schema 禁止置 NULL 的其他情况，按 Lead 要求 stop + 上报（本分片未发现）。
5. **catalog preview 派生文件不计入 deletedFiles/Bytes**（可重建缓存，按 manifest 清理清单处理）。
6. 真实 Windows 回收站（D 流程）NOT_RUN：首版按范围冻结零实现、零 OS API（静态+运行时哨兵证据）。

## 7. 最终 check 复跑（避免日志自指）

- Canonical Evidence 表定稿后复跑：
  `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE.md` → **PASS**
  （warnings 同上；登记于本节与 `logs/core-py-check.log` 的定稿前一次同参复跑）。
- 若集成时 READY DAG/STATUS 再次变化，以 Lead 集成复跑为准（本分片不再改 Lead-owned 文档）。

## 8. Review 就绪声明

分片 A 已按冻结范围与 wire 完成 Python Core 实现、AC1–AC10/AC12 证据齐备、AC11 Python 侧证据齐备；
源码/测试/证据/任务卡/门禁日志已入本卡 allowed_paths 并提交（不 push）。**Review 就绪**：
请 Lead 指派上下文独立 Reviewer（实现者不得自审；Review 报告需记录 Reviewer 身份/会话）。
