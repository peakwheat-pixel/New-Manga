# Handoff — FEA-12-CORE 分片 A（Python Core）

- Task: `doc/tasks/FEA-12-CORE.md`（status: in_review；分片 A r2；Lead 集成）
- Owner: `fea12-core-py`（DSH Agent Teams teammate）
- 交付日期：2026-11-05（Asia/Shanghai）；r1 交付 → r1 Review changes_requested → **r2 最小返修交付**
- 释放 base：`e47fd47e4`（释放 commit `c8d9adc8d`）；r2 门禁基于 r1 head `85db8354f` + r2 工作树
- 范围：`doc/reviews/ADJ-2026-11-05-FEA-12-SCOPE.md` D1–D8；wire：M2-C1 rev 2.13（FEA-12-PREREQ-1 done）
- 分片 B：`.NET Host 桥/R-002` 由 `fea12-core-host` 交付；Lead 在 r1 处置中定稿 AC11 `<<MET>>`
  （`doc/reviews/FEA-12-CORE-r1.md` R-002 处置）；本分片零 .NET 改动

## 1. Commit 列表（仅本卡 allowed_paths；未 push）

> **r1 交付**：
> 1. **`5fb300fd2`** feat(fea-12-core)：源码（5 文件）+ 测试（6 文件，含 3 新增）。
> 2. **`27dfd7514`** docs(fea-12-core)：任务卡 + Handoff + `verification/FEA-12-CORE/**` r1 证据。
> 3. **`2a8c6cf83`** docs：Canonical Evidence 改 evidence commit pin（行尾无关）+ Handoff 终稿。
> 4. **`85db8354f`** docs：门禁日志补 r1 交付 head/commit 列表。
>
> **r2 返修**：
> 5. **`60dd4d563`** `fix(fea-12-core): r2 最小返修——R-001 派生文件披露 + R-004/007/008/009/010/011/012`
>    — 源码 `src/bootstrap/core_service.py`、`src/infrastructure/sqlite/library.py`；测试
>    `tests/core/test_core_delete_commands.py`、`tests/core/test_core_delete_preview_commands.py`、
>    `tests/core/test_core_trash_commands.py`；`verification/FEA-12-CORE/**` r2 证据/日志/探针/实施记录
>    （Canonical Evidence 的 A 分片行 pin 指向本 commit）。
> 6. **r2 docs 提交**：任务卡（status in_review + r2 处置 + evidence pin 60dd4d563）+ 本 Handoff
>    （SHA 见 `git log --oneline -2`）。
>
> 只 add 了本卡 allowed_paths 内文件。未 commit：`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、
> `doc/TASK_LEDGER.md`、`doc/reviews/**`（Lead-owned）、分片 B .NET/证据、DSIM-1 文件。
> **R-003 表述更正**：`tests/core/test_core_service.py` 不在 r1 交付 commit 的 allowed_paths 内
> （r1 R-003），由 **Lead 于 r1 处置时补登** allowed_paths 窄批；本 Handoff 不再声称"已入 allowed_paths"。

## 2. 交付摘要（r2 更新）

### A 流程（AC1–AC3）
- `Book.restore()`：只清 `deleted_at`；**r2 R-007 接线**——`restore_book_from_trash` 现经 domain
  方法产生值，再以单条 `deleted_at IS NOT NULL` guarded UPDATE 写回两列（逐项原子/并发保护不变）。
- repo `move_book_to_trash` / `list_trash_entries`；Core `MoveToTrash` / `RestoreFromTrash` /
  `ListTrash`（minor 13、closed shape、`idempotency_key`、opaque cursor、逐项原子）。
- `ListRecycleBinBooks` 冻结投影零改动（空数组≠失败、`page_count` None 通道）。

### C 流程（AC4–AC9）
- `PreviewPermanentDeleteBooks`（minor 11）：PD-01 全披露；零写；canonical digest（C-04b §2.1）+
  集合级有序 sha256；`currentRevisionId` 过 lineage guard 取首个可见 region（r2 R-011 测试钉住 `rr1`）。
- **r2 R-001**：`deletedFiles/deletedBytes` 计入 catalog preview/page-original 派生文件（与 managed
  清单按绝对路径去重）；catalog 读失败 → `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`（不静默少报）；
  golden 向量含 derived 记录（19→3 files/46 bytes 场景）。
- delete 命令 digest 必填 + 两级校验；**r2 R-008 限定**：混合 live+retry 批次集合级只做形状校验，
  逐书对存活目标强校验。
- `execute_permanent_delete_db`：显式 `BEGIN IMMEDIATE` 单事务；失败整体回滚；D1 X1 同事务删
  v7/v8 子图（plans/operations 保留）；写边界复检非终态 operation；**r2 R-009**：批量写边界竞态顶层
  `BOOK_BUSY` + items 归因具体 book。
- PD-08：共享文件保留、跨项目 provenance 置 NULL；**r2 R-010** 增加第 5 条预检（目标外 binding
  previous→目标 binding → `BOOK_DELETE_CONFLICT`）。
- PD-07：`cleanup_pending` manifest + 显式重试；**r2 R-012** 批量 partial cleanup → retry →
  逐项状态（deleted/cleanup_pending/not_started）与幂等重放有直接测试。
- `PurgeTrash`：首版不实现，typed `UNKNOWN_COMMAND` 零副作用。

### 统一 ProtectionPolicy（AC10）
- `ProtectionPolicy.evaluate(scope, facts)` 唯一判定（`application/maintenance/ports.py`，不 import
  infrastructure）；软删不阻断、自动清理保护人工成果、彻底删除披露不阻断（仅 active op/unsafe shared 阻断）。

### 命令面（AC11 Python 侧）
- `core.ping` 在 library repository+storage 装配时公告 3 capability；preview minor 11 / trash minor 13 /
  delete minor 10+digest；最小手搭 Core 不公告（`tests/fea09` 不变）。

## 3. AC 状态（分片 A）

| AC | 状态 | 依据 |
|---|---|---|
| AC1–AC3、AC5–AC10、AC12 | **MET** | 实施记录 §4 + `logs/core-py-ac*.log`（r2 重新生成） |
| AC4 | **PARTIAL（r2 证据齐备，待 Lead 复审定稿恢复 MET）** | r2 R-001 修复 + 判别测试 2 条 + golden derived 向量；见 `logs/core-py-ac4-preview.log`、`evidence/core-py-inventory-digest-golden.json` |
| AC11 | **MET（Lead r1 处置定稿；分片 B 证据）** | `doc/reviews/FEA-12-CORE-r1.md` R-002 处置；分片 B `core-host-*` 证据/集成 1405/0/80 |

## 4. 门禁实跑（r2；命令/EXIT/数字见 `logs/gates-core-py.log`）

| 门禁 | 命令 | EXIT | 结果 |
|---|---|---|---|
| 相关组 | `C:/Python314/python.exe -m pytest tests/core tests/storage tests/maintenance tests/fea12 -q -p no:warnings` | 0 | **1104 passed**（r1 1096 + r2 新增 8） |
| 全量 pytest | `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no` | 0 | **3152 passed / 10 skipped**（基线 3093/10；增量 **CORE +51 / DSIM-1 +8**） |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 0 | **18/18 PASS** |
| 治理 check | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE.md` | 0 | **PASS (3 warnings，均既有全仓告警)**；最终复跑见 §7 |
| golden 探针 | `python verification/FEA-12-CORE/scripts/core_py_inventory_digest.py` | 0 | `all_match: true`（含 R-001 derived 披露：3 files/46 bytes） |
| 隔离探针 | `python verification/FEA-12-CORE/scripts/core_py_isolation_scan.py` | 0 | `pass: true`（R-004：is_relative_to 纳入 pass；drive_path_hits=[]） |
| 全量 .NET | 分片 B/Lead 集成：`logs/core-host-dotnet-full-*.log` | — | 集成记录 **1405 passed / 0 failed / 80 skipped**；本分片零 .NET 改动 |

## 5. 预期行为变更（Review 不判回归）

1. **digest 必填**（§5.11.1a）：既有 delete 测试改为先 Preview 再回传 digest；旧 Host 不传 →
   `INVALID_REQUEST` fail-closed，不降级软删。
2. **PD-08**：共享引用可安全拆分不阻断（原 `test_core_delete_commands.py:323,378` 期望按 ADJ D3 更新）；
   共享文件/binding 保留、跨项目 provenance 置 NULL；不可拆分才 `BOOK_DELETE_CONFLICT`。
3. **page 级 purge** 补 C-17 v7/v8 子图（fixture 补行后全绿）。
4. **capability 新增 3 名**（生产装配断言更新；最小手搭 Core 不公告）。
5. **r2/R-001 披露口径**：`deletedFiles/deletedBytes` 含 catalog preview/page-original 派生文件；
   digest 随派生文件集/字节变化（PD-04 预期），golden 向量已更新。
6. **r2/R-008 限定**：混合 live+retry 批次集合级 digest 仅形状校验（PD-07 不重跑预览），存活目标逐书强校验。
7. **r2/R-009**：批量写边界竞态顶层 `BOOK_BUSY`（items 归因具体 book）。
8. **r2/R-012**：批量 cleanup-pending → 显式 retry 的逐项状态/幂等语义有直接测试。

## 6. 集成注意事项 / 残余风险

1. **分片 B 衔接**：新 Host 需按 task-7 先 probe `core.ping` 再调 delete/trash；旧 Host 对新 Core 的
   delete 无 digest → `INVALID_REQUEST`（预期 fail-closed）；新 Host 对旧 Core 负向对照以 PREREQ-1 证据为准。
2. **`activeRunIds` 不含 active export**（wire 无字段）：export 仍是 `BOOK_BUSY` 阻断项，但不在 preview
   披露列表——wire 冻结缺口，未擅自扩字段。
3. **`deletedBytes` 以实际文件 stat 计**（含派生文件；缺失文件计 0）：预览→确认间文件变化会触发
   STALE（PD-04 预期）；大书预览有 stat+catalog lookup 成本。
4. **page 级 purge 跨页 lineage 外键**：应用层当前不可产生；若出现则整事务 FK 回滚（fail-closed）；
   book 级 C 流程按 PD-08/R-010 预检 CONFLICT（含目标外 binding previous 指向）。
5. **catalog preview 派生文件已纳入披露与 digest**（r2 R-001），不再是"登记排除"。
6. 真实 Windows 回收站（D 流程）NOT_RUN：首版按范围冻结零实现、零 OS API（静态+运行时哨兵）。

## 7. 最终 check 复跑（避免日志自指）

- r2 证据表定稿后复跑
  `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE.md` → **PASS (3 warnings)**
  （warnings：非终态 Task 计数、STATUS/PLAN 预算 80%；均既有全仓告警；`logs/core-py-check.log` 为
  定稿前同参 PASS 复跑）。
- `verify_pins.ps1` → **PASS (all 18)**（`logs/core-py-pins.log`）。
- 若 Lead 集成时 READY DAG/STATUS 再次变化，以 Lead 复跑为准（本分片不再改 Lead-owned 文档）。

## 8. r2 复审就绪声明

r1 Review 的 R-001（P2）已按冻结语义修复并补判别测试/golden；R-004/R-005/R-007/R-008/R-009/R-010/
R-011/R-012 均已处置（详见 `verification/FEA-12-CORE/core-py-implementation-record.md` §7 与卡内
「r2 处置结果」）；AC4 证据齐备待 Lead 复审定稿，AC11 已由 Lead 定稿 MET。源码/测试/证据/卡/Handoff
已按 allowed_paths 提交（不 push）。**r2 复审就绪**：请 Lead 指派上下文独立 Reviewer 只审 r2 新 head，
重点复核 R-001 派生披露口径与 golden、R-008 混合 retry 限定、R-009 批量错误码、R-010 第 5 预检、
R-012 批量 retry 直接证据。
