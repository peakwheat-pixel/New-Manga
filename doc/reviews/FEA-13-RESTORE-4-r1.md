---
task_id: FEA-13-RESTORE-4
reviewer: 独立上下文子 agent（由 parent session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5 派发；未参与实现/返修）
reviewer_kind: subagent
author: dsh
base_commit: 0dc4ff85f
reviewed_head: 2e2d8b301（被审实现提交 f9ebce677）
decision: changes_requested
---

# Review：FEA-13-RESTORE-4（FEA-13 片 4 / merge restore）

## 范围与依据

- 被审：`git diff 0dc4ff85f..f9ebce677`（15 文件，+1197/-6）；范围文件 `restore_plan.py`（新）、`nmbak.py`、`core_service.py`、2 个测试文件、卡/Handoff/证据/ADJ 文档。
- 依据：`doc/tasks/FEA-13-RESTORE-4.md`、`doc/reviews/ADJ-2026-11-09-FEA13-RESTORE-MODEL.md`、`FEA-13-scope-r1.md` §7 片 4、C-13/C-01b SC-13/SC-17。
- 只读审查：仅临时变异 `restore_plan.py` / `core_service.py` 各一次（已 `git checkout --` 还原并复绿，工作区 clean）；未改契约/pins/测试。
- 未审：真实进程 kill 崩溃注入、Host/UI 端到端（本轮无 C# diff）、跨机恢复。

## Architecture（分层/契约/安全/持久化）

- 分层：`nmbak.py` 未 import application 层（infrastructure 新代码仅 `_conn` 属性 + 4 个路径方法）；`core_service.py:3204` 的 application 导入在函数内，方向正确。`NmbakBackupService.connection` 把 live 连接暴露给 bootstrap（组装根）可接受，但 application 层直接拿到 infrastructure 的 conn，耦合偏紧（判断项，不单列 finding）。
- 契约/范围：无 C-13/C-04b/C-09 字节、18 pins、M2-C1、UI、片 5 改动（diff 文件集核实）。但 `doc/reviews/ADJ-2026-11-09-FEA13-RESTORE-MODEL.md` 出现在 diff 中而**不在** `allowed_paths`（见 P3-2）。
- 安全：默认 `defer` 确实只写 `add`，不整库覆盖；`keep` 不删 live；DB 写入在 `BEGIN IMMEDIATE…COMMIT` 内。主要安全缺口见 P1-1（库身份/run 活跃检查缺失）与 P1-2（L-5 对真实并发写者无效）。
- 持久化：staging 复制+digest 自比对、marker `staging→committed` 可用，但 marker 缺 plan digest/应用项，COMMIT 与 marker 之间无原子性、无启动期读者；undo 保全未 fsync（P2-3/P2-6）。

## Verification（实际执行）

| 场景 | 命令 | 结果 | 证据/EXIT |
|---|---|---|---|
| 定向 pytest（4 文件） | `python -m pytest tests/storage/test_nmbak_merge_restore.py tests/core/test_core_restore_plan.py tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_identity.py -q` | **38 passed** | EXIT 0（本会话） |
| dotnet build | `dotnet build apps/desktop-avalonia/NewManga.sln -c Debug --nologo` | 0 warning / 0 error | EXIT 0 |
| 治理检查 | `check.ps1 -TaskPath doc/tasks/FEA-13-RESTORE-4.md`；`check.ps1` | PASS（3 warnings） | EXIT 0 / EXIT 0 |
| pins | `verify_pins.ps1` | PIN AUDIT: PASS (all 18) | EXIT 0 |
| EV sha256 | 卡中 5 条逐条 `Get-FileHash` | **5/5 一致** | 见下 |
| 变异①（defer 也应用冲突） | 变异后 `pytest tests/storage/test_nmbak_merge_restore.py tests/core/test_core_restore_plan.py -q` | **4 failed / 5 passed**；还原后 9 passed | EXIT 1 → EXIT 0 |
| 变异②（L-5 判决反转） | 变异后 `pytest tests/core/test_core_restore_plan.py -q` | **1 failed / 4 passed**；还原后 5 passed | EXIT 1 → EXIT 0 |

EV 核对（全部一致）：README `6fe5d254…`、pytest 日志 `62c5f602…`、build 日志 `09134b51…`、mutation-defer `db5da2a4…`、mutation-no-lock `7e249a0e…`。

### 重点逐条核实

| 检查项 | 结论 |
|---|---|
| 只读预览（`plan_rows` 仅 ATTACH + SELECT，`finally` DETACH） | 成立；测试快照覆盖 books/pages 行、managed 全部文件 sha、包 sha，但**未比 mtime、未覆盖全 7 表**（P3-1） |
| defer 语义（不写 conflict/keep、不整库覆盖） | 默认（`entries` 为空）成立；但 `mode` 不参与判定，`defer` + `entries` 会覆盖冲突（P2-1） |
| UseBackup 保全（先保全后覆盖、失败不覆盖） | 行级成立且已测；**无 fsync**、managed 无副本（P2-6 / P2-2） |
| 事务边界（BEGIN IMMEDIATE/COMMIT/ROLLBACK；`_replace_row` 参数序） | 事务结构正确，未与 `with conn` 混用；`_replace_row` 在**同 schema** 下顺序正确，跨 schema 有隐患（P2-5）；`mode` 校验在 COMMIT 之后（P2-1） |
| staging/marker | DB 复制+sha 自比对、`staging→committed` 可用；marker 缺 plan digest/应用项、COMMIT→marker 窗口状态含糊、无重启读者（P2-3） |
| L-5 | 设置/释放在 `try/finally`（overwrite 路径亦持锁），但请求循环串行 + 调度线程绕过 dispatch（P1-2）；读命令被一并阻断（P3-3） |
| 分层 | 通过（见上） |
| out_of_scope | 契约/pins/M2-C1/UI/片 5 零 diff；ADJ 文档越界（P3-2） |

## AC 判定

| AC | 判定 | 说明 |
|---|---|---|
| AC1 只读预览 | **MET** | 代码层面零写（ATTACH+SELECT+DETACH）；快照测试通过，但 mtime 未断言、仅 2/7 表（P3-1） |
| AC2 默认 defer | **PARTIAL** | 冲突/keep 保留成立、无整库覆盖；但**两个测试文件都没有 add 用例**，`_insert_row` 零覆盖，"add 项被应用"未验证；`defer`+`entries` 可覆盖冲突（P2-1） |
| AC3 UseBackup 保全 | **PARTIAL** | 行级"先保全后覆盖/缺 undo 区不覆盖"成立并已测；managed 项一律 deferred、无副本，与卡"rows JSON / managed 副本"不符（P2-2） |
| AC4 过期拒绝 | **FAIL** | 非法 mode → `INVALID_REQUEST` 成立；但 `RESTORE_PLAN_STALE` 在全仓**无任何抛出点**（仅 `core_service.py:454` 映射），预览→换包/库身份变化检测完全缺代码，不只是"端到端未做"（P2-4） |
| AC5 L-5 + staging/marker | **PARTIAL** | marker `staging/committed`、apply 崩溃后 marker=staging 且 live 不变、锁释放均成立；L-5 对真实并发写者无效（P1-2），marker 载荷/状态机不完备（P2-3） |
| AC6 门禁 | **PARTIAL** | pytest/build/check/pins/EV 全 PASS；但 "diff ⊆ allowed_paths" 不成立（ADJ 文档越界，P3-2），wire/C# 项未实现（P3-5） |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R4-001 | **P1** | `src/infrastructure/sqlite/nmbak.py:426-456`；对照 `:356-374`；`src/bootstrap/core_service.py:3209` | merge 路径只调 `_verify_package`，**不做 `BACKUP_DATABASE_MISMATCH` 检查、不做 `_is_run_active()` 检查**（overwrite 路径两者都做）。默认 `defer` 会把**另一个库**的 add 行静默并入 live；run 进行中也可并写 | 代码对照可证；无测试覆盖（测试包均同源库） | `extract_for_plan`/`_merge_restore` 复用身份与 run 活跃检查，映射 `BACKUP_DATABASE_MISMATCH` / `BACKUP_RESTORE_BUSY`，补两条 RED 用例 | open |
| R4-002 | **P1** | `src/bootstrap/core_service.py:7794`；`:7861-7873`；`:1310-1322` | L-5 门在 `dispatch_request`，但 `serve_forever` 串行读 stdin：restore 处理期间不可能再派发其他请求，门实为不可达；而真实并发写者（run scheduler 线程 `run_pending_once`）**不经 dispatch**、也不在 merge 路径的 `_is_run_active` 保护内 → ADJ §2.4.5 点名的"Run 提交"未被 fail-closed | `tests/core/test_core_restore_plan.py:149-163` 是直接置位 `_restore_maintenance_active`，未走真实窗口 | 在 `_merge_restore` 内先拒绝活跃 run（或对 pipeline 加维护标志检查）；L-5 应覆盖进程内写者而非只覆盖串行 wire；测试用真实并发窗口 | open |
| R4-003 | P2 | `src/application/maintenance/restore_plan.py:232-242`、`:267-268` | `mode` 在 `apply_restore` 中**完全不参与判定**，只有 `use_backup_keys` 决定是否覆盖冲突 → `mode="defer"` 且带 `entries` 时仍覆盖冲突（有保全）；`mode` 校验在 COMMIT 之后，非法 mode 会**先落盘再抛** `ValueError`（非 typed 错误） | 变异①证明覆盖路径可达；`_merge_restore` 直接透传 entries | `selected` 增加 `mode == "use_backup"` 前置；mode 校验移至函数入口并抛 `NmbakBackupError("INVALID_REQUEST")`；补 defer+entries 拒绝用例 | open |
| R4-004 | P2 | `src/bootstrap/core_service.py:3239`；`src/application/maintenance/restore_plan.py:150`、`:253-260` | `managed_root=None` 使 wire 计划**永不包含 managed 项**；`apply_restore` 的 managed 分支恒 deferred（死代码）；`extract_for_plan` 产出的 `managed_entries` 无人使用 → 裁决 L-C 层对客户端不可见、不可应用 | 读代码可证；存储测试自行传 `managed_root` 才覆盖 managed | 本片要么显式声明 managed 层 deferred 并降 AC3 口径，要么把 managed 项纳入 plan/apply（staging 复制+保全） | open |
| R4-005 | P2 | `src/bootstrap/core_service.py:3224-3271` | marker 缺 ADJ §2.4.4 要求的 **plan digest 与应用项清单**；`committed` 在 COMMIT 之后写，两者之间崩溃会留下 `state="staging"` 但数据已提交的**歧义状态**；全仓无 marker 读者/启动清理，"重启可判定并清理"未实现 | `test_marker_stays_staging_when_the_apply_crashes` 只覆盖 apply 抛错（回滚）分支 | marker 增加 plan digest/applied keys 与 `applying` 态；实现启动期判定清理或明确登记为后续并在卡中降级 AC5 | open |
| R4-006 | P2 | `src/bootstrap/core_service.py:454` | `RESTORE_PLAN_STALE` 仅登记映射，`src/**` 无抛出点（grep 单点命中）；预览→换包/库身份变化检测零代码，AC4 的核心行为缺失而非仅缺端到端 | `Select-String RESTORE_PLAN_STALE src/**` 仅 1 行 | 实现生成号/包 sha/库身份比对并在 stale 时逐项 typed 拒绝；否则删除登记并在卡中把 AC4 标 FAIL/后续 | open |
| R4-007 | P2 | `src/application/maintenance/restore_plan.py:187-204` | `_replace_row` 的 SET 值用 **live 表列序**去掉 key 位置，却喂的是 `SELECT * FROM restore_src`（备份列序）。同 schema 正确；跨 schema（表重建式迁移/旧包）会错位或绑定数不符 → UseBackup 静默写错值（或误判全 conflict） | 仅 books 同 schema 用例通过，无 schema 漂移用例 | 改为显式列名 `SELECT <cols>…`，并先比对两侧 `table_info`，不一致则该项 fail-closed | open |
| R4-008 | P2 | `src/application/maintenance/restore_plan.py:159-173`、`:241-242` | "受保护可恢复副本"未落盘持久化：`write_text` 返回即覆盖，undo JSON 不在 DB 事务内也无 fsync；断电/崩溃后覆盖已 COMMIT 而 undo 可能丢失 | 无崩溃注入用例 | undo 文件 fsync（文件+目录），或把保全行写入同事务的 undo 表；补持久性用例 | open |
| R4-009 | P3 | `tests/storage/test_nmbak_merge_restore.py:118-141` | AC1 的"mtime 全不变"未断言，快照仅 books/pages 两表；包 mtime、DB 文件字节未比 | 测试快照可读 | 补 mtime 与 7 表/DB 文件字节快照 | open |
| R4-010 | P3 | `doc/reviews/ADJ-2026-11-09-FEA13-RESTORE-MODEL.md`（diff 内） | 该文件不在卡 `allowed_paths`（仅 `doc/reviews/FEA-13-RESTORE-4-*.md`），AC6 "diff ⊆ allowed_paths" 不成立 | `git diff --name-only 0dc4ff85f..f9ebce677` | 补 allowed_paths 或在卡/Closeout 说明该 ADJ 由裁决流程引入 | open |
| R4-011 | P3 | `src/bootstrap/core_service.py:410-412` | 豁免集只留 3 个备份命令 → **读命令（`books.list` 等）也被阻断**，与 ADJ"其他**写**命令 fail-closed"不一致（测试还断言了该行为）；`backup.delete` 豁免可在 restore 中删包 | `:7794` + 测试断言 | 改为命令分级（读放行/写拒绝），`backup.delete` 在 restore 窗口内拒绝或在删除时校验在途 restore | open |
| R4-012 | P3 | `src/bootstrap/core_service.py:3213-3235`；`src/infrastructure/sqlite/nmbak.py:437-456` | staging 只复制 DB（未复制 managed，"文件数/字节"未校验），且 staged DB **不是实际应用源**；进程崩溃后 `.restore-staging-*`/`.nmbak-plan-*` 无启动清理 | 代码可证 | 明确 staging 语义（仅提交凭据）或补齐 managed staging；启动清理残留目录 | open |
| R4-013 | P3 | `apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs:936-958` | 卡"wire/C#：`backup.restore` 增 `mode`/`entries`；C# 暴露 `PlanRestoreAsync`/`RestoreAsync(mode)`"未实现（C# 仍只写 `confirm_restore`），V11R 行级登记亦未做 | C# 无 `mode`/`entries`/`PlanRestoreAsync` 字样 | 补齐 C# 面并登记 V11R 行修订，或把该条移出本片范围 | open |

## 结论与复审

- **decision: changes_requested**。默认 `defer` 的核心安全属性（不整库覆盖、保留 live、行级 typed 失败隔离）成立，门禁与证据可复现；但 **2 个 P1**（merge 路径缺库身份/run 活跃检查；L-5 对真实写者无效）与 **AC4 实质缺失（FAIL）** 落在"最高风险片"的关键路径上，按模板批准门槛不可批准。
- 返修优先级：R4-001/R4-002（数据安全）→ R4-003/R4-006（语义与 AC4）→ R4-005/R4-007/R4-008（持久化）→ R4-004（managed 层口径）→ P3。
- 复审：新 head + 对应 findings disposition；本轮变异与门禁数字只对 `f9ebce677`/`2e2d8b301` 有效。
