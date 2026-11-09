---
task_id: FEA-13-SCHED-5
reviewer: 独立上下文子 agent（由 parent session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5 派发；未参与实现/返修，只读被审 head）
reviewer_kind: subagent
author: dsh
base_commit: cf563a711
reviewed_head: 5e8b7712d（实现提交 4befab5f3）
decision: approved_with_conditions
---

# Review r1：FEA-13-SCHED-5（自动备份调度/保留/失败语义，FEA-13 片 5）

## 范围与依据

- 被审：`git diff cf563a711..4befab5f3`（13 文件，+811/-65）；生产码仅 `src/application/maintenance/backup_schedule.py`（新）与 `src/bootstrap/core_service.py`，余为两个测试、卡、Handoff、EV、4 个治理指针。
- 依据：`doc/reviews/FEA-13-scope-r1.md` §7 片 5（:263-273）、`doc/reviews/ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT.md` D4（:16）、`doc/tasks/FEA-13-SCHED-5.md` AC1–AC6、Handoff、`verification/FEA-13-SCHED-5/`。
- out_of_scope 核对：`doc/contracts/**`、`doc/plan/**`、pins **零 diff**；无新增 DDL（配置/receipt 用既有 `application_metadata`）；无 Host/C# diff（未引入 Host 定时器）；未改 merge restore 语义（片 4 的 `_merge_restore` 无 diff）。
- 未审：真实进程 kill/磁盘满部署态、Host/UI 端到端、大库耗时；`tests/storage` 全量未跑（仅按要求 4 文件）。
- 只读：未改生产码/测试/契约/pins，未 commit/push；除本报告外工作区 clean（变异已按字节还原，sha256 前后一致）。

## 门禁复跑（本会话）

| 命令 | 结果 | EXIT |
|---|---|---|
| `python -m pytest tests/application/test_backup_schedule.py tests/infrastructure/test_nmbak_startup_backup.py tests/storage/test_nmbak_backup.py tests/core/test_core_restore_plan.py -q` | **48 passed**（5.72s） | 0 |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-13-SCHED-5.md` | Governance check: PASS（3 warnings：12 非终态 Task / STATUS 80% / REBASELINE 80%） | 0 |
| `pwsh -NoProfile -File tools/governance/check.ps1`（默认） | PASS（同上 3 warnings） | 0 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | PIN AUDIT: PASS (all 18) | 0 |
| EV 4 条 sha256 `Get-FileHash` | **4/4 与当前字节一致**（README `5eaf0a1b…`、SUITE `fc80dc45…`、MUT1 `4030f756…`、MUT2 `12feeca0…`） | — |

- EV suite 日志为 **10 文件 108 passed**（`# EXIT=0`，2026-11-09T22:18:01+08:00）；本会话按要求复跑 4 文件 48 passed。口径不同但不相交于失败，无冲突。
- 独立变异（本会话，非引用 EV）：删除 `retained.update(protected_ids)` → `test_retention_protects_the_recovery_chain` **1 failed / 5 passed，EXIT 1**；按备份字节还原（`RESTORED_SHA_MATCH=True`）→ **6 passed，EXIT 0**。与 EV-MUT1 一致，判别力成立。

## 逐项核实（Review 关注点）

| 关注点 | 结论 | 核实 |
|---|---|---|
| 调度模型 `due()` | **正确**（除 weekday） | daily=24h、weekly=7×24h、custom_hours=N、disabled=false；纯函数注入 `now/last`；`parse_*` 全部容错不抛（`None`/坏 JSON/错类型/越界 → 默认值）。 |
| **D4 ① 手动包永不删** | **成立** | `select_prunable` 只取 `backup_type=="automatic"`，manual 永不成候选；用例 + 变异可判别。 |
| **D4 ② 最新 verified / last `pre_restore` 在 keep 之外仍保留** | **成立** | `retained = newest keep | protected_ids`（`backup_schedule.py:122-123`）；`protections()` 取最新 verified + `backup.last_restore_pre_restore_id`（`core_service.py:8138-8149`）；overwrite restore 成功后写该 key（`:3197-3202`，`NmbakBackupError` 之外的 `sqlite3.Error` 静默）。注：真实包型下 `pre_restore` 本就不进候选，保护为额外防御；变异用例把 pre_restore 构造成 automatic id，故判别的是 `protected_ids` 机制本身。 |
| **手动不重置计时** | **代码正确，用例判别力不足** | 计时只取 `backup_type=="automatic" and verified`（`:8154-8163`）；但 `test_manual_backup_does_not_reset_the_automatic_schedule` 在旧实现（跨类型取最新 verified）下同样为绿色（手动包年龄≈0 → 不轮转），无法杀旧 bug；README 已自认变异②不可判别。 |
| disabled 只跳过创建、restore 仍可用 | **代码成立，无用例** | `_BACKUP_ENABLED_KEY` 仅在 `_ensure_automatic_backup` 读取；restore 入口不看该开关。`schedule.kind=="disabled"` 走 `due()=False` 分支，不写 receipt（见 P2-1）。 |
| receipt 每次决策写 / 失败语义 | **部分成立** | created/created_first/disabled/failed 均写 `backup.last_receipt`（kind/status/next_due/message/created_at）；`service.create` 抛 `NmbakBackupError` 被捕获不向上抛（失败计数 +1，连续 K=3 → `degraded`）。**not-due 与 books==0 分支直接 return，不写 receipt**；`backup.schedule.kind=disabled` 也静默。 |
| 兼容 `_AUTOMATIC_BACKUP_REFRESH_HOURS` | **成立** | daily 映射为该 knob（`int()`，0 合法 → 任何已存在包视为陈旧）；旧 2 例补丁测试通过。 |
| 旧 API `_prune_automatic_backups(service, entries)` | **签名兼容但已死** | 默认 `keep=None→DEFAULT_KEEP(5)`、`protected_ids=None`；生产已改走 `prune()` 闭包，无任何调用者，2 参旧调用也无测试。`_AUTOMATIC_BACKUP_KEEP` 仍存在但不再是保留真源。 |
| out_of_scope | **契约/pins/其它片零 diff**；治理指针有 diff | `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/PLAN-HISTORY.md` 在实现提交内（DSH 生命周期写域，非卡面 `allowed_paths` 字面集合），与 AC6「diff ⊆ allowed_paths」表述不符（P3-5）。 |

## AC 判定

| AC | 判定 | 要点 |
|---|---|---|
| AC1 调度模型 | **MET**（带 P3） | 四类 `due()`/`parse_*` 容错/注入时钟成立；disabled 不创建且 restore 路径不受影响（代码可证，缺用例 P3-4）；weekly 的 `weekday` 未参与判定（P3-3）。 |
| AC2 错过计划 receipt | **PARTIAL** | 超龄/首次会写 receipt 且带 `next_due`、不静默；但字面 `kind=missed_or_due` 未实现（实际 `created_first/created/disabled/failed`，「missed」只在 `message`），且纯 not-due 启动不写 receipt（P2-1/P2-2）。 |
| AC3 保留 + D4 | **MET** | N 可配置（`backup.keep_count`，默认 5）；手动包永不删；最新 verified 与 last `pre_restore` 在 keep 外仍保留（用例 + 独立变异 RED→GREEN）。保留预算不再覆盖 pre_migration/pre_restore 见 P2-3。 |
| AC4 手动不重置计时 | **MET（代码）/ 用例弱** | 代码只按 automatic 计时；用例无判别力（P3-7）。 |
| AC5 失败语义 | **MET** | `create` 的 OSError/sqlite3/zip 均被 nmbak 包装为 `NmbakBackupError`（`nmbak.py:335-336`）→ 本函数捕获、不阻断启动；K=3 → `degraded` 有用例；Host 无定时器（无 C# diff）。receipt 写入本身未加 sqlite 保护（P3-6）。 |
| AC6 门禁 | **PARTIAL** | 定向 pytest 48 passed、check.ps1（默认 + TaskPath）PASS、pins 18/18、EV 4/4 字节一致；但实现提交含 4 个 `allowed_paths` 外治理文件，与字面断言不符（P3-5）。 |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| S5-001 | P2 | `src/bootstrap/core_service.py:8185-8187`（另 `:8151-8153`、`:8166-8177`） | **receipt 覆盖声明与实现不符**：not-due 分支与 books==0 分支直接 return，不写 `backup.last_receipt`；`backup.schedule.kind="disabled"` 因 `due()=False` 落入 not-due 分支而静默，只有 `backup.auto_enabled=false` 才产生 `disabled` receipt。docstring `:8099-8100` 与 README `:17` 均宣称「每次决策写 / 不静默跳过」，消费者（当前无 Host 读取）会看到陈旧决策记录。 | 代码路径审读；`test_disabled_schedule_creates_nothing_and_writes_a_receipt` 仅覆盖 `auto_enabled`；`select_prunable`/disabled 集成无 receipt 断言。 | 二选一：not-due（含 schedule-disabled）写 `kind=not_due/skipped` 的最小 receipt，或修正 docstring/README 口径为「需要动作的决策写 receipt」。 | open |
| S5-002 | P2 | `doc/tasks/FEA-13-SCHED-5.md:63` vs `core_service.py:8170,8227,8206` | **卡面 AC2 指定 `kind=missed_or_due` 未实现**，实际枚举为 `created_first/created/disabled/failed`，AC2 仍标 `<<MET>>`；无消费者故功能影响小，但 AC 字面契约不成立，后续集成/UI 若按卡面取 kind 会落空。 | 全文搜索 `missed_or_due` 零命中；用例只断言 `kind in {"created","created_first"}`。 | 修订卡面 AC2 为实际枚举（并说明 missed 由 `message` 表达），或实现 `missed_or_due`。 | open |
| S5-003 | P2 | `src/application/maintenance/backup_schedule.py:114-116`（旧行为见 `cf563a711:core_service.py` 的 `_prune_automatic_backups`） | **保留预算不再覆盖 `pre_migration`/`pre_restore`**：旧实现把三类包计入 `_AUTOMATIC_BACKUP_KEEP`，新 `select_prunable` 只筛 `automatic`，导致每次 pending DDL 前的 `pre_migration` 与每次 overwrite restore 前的 `pre_restore` 永不自动删（D4 只要求保护最近一个 `pre_restore`）。反复迁移/恢复场景包体积无界增长。 | diff 审读；`BACKUP_TYPES` 含四类（`nmbak.py:65`），`restore` 每次建 pre_restore（`:375`）；无任何裁剪路径。 | D4 保护之外将旧 `pre_migration/pre_restore` 纳入预算，或在卡/README 明确裁决「永不删」并登记磁盘增长风险。 | open |
| S5-004 | P3 | `src/bootstrap/core_service.py:8016,8252-8268` | `_AUTOMATIC_BACKUP_KEEP` 仍是公开常量但已不是保留真源（prune 用 `DEFAULT_KEEP`）；`_prune_automatic_backups` 生产无调用者（被 `prune()` 闭包取代），2 参旧调用亦无测试；`_package_age_hours`（`:8023`）只剩测试引用。双真源 + 死代码易漂移。 | grep 全仓：`_AUTOMATIC_BACKUP_KEEP`/`_package_age_hours` 仅定义与测试导入；`_prune_automatic_backups` 无调用点。 | 删除死代码，或让 `_ensure_automatic_backup` 复用 `_prune_automatic_backups` 并以 `_AUTOMATIC_BACKUP_KEEP` 为唯一默认值。 | open |
| S5-005 | P3 | `src/application/maintenance/backup_schedule.py:41-56`（`weekday` 见 `:35,69-75`） | weekly 的 `weekday` 被解析/校验但不参与 `due()`，weekly 实为「距上包 168h」；卡面「指定 weekday + 24h 门」未实现（README `:39` 已登记残余，但卡面未降级措辞）。 | `test_weekly_and_custom_intervals` 只断言 7×24h；全仓无 weekday 判定用例。 | 实现 weekday 锚定，或修订卡面表为「7×24h 间隔」。 | open |
| S5-006 | P3 | `tests/infrastructure/test_nmbak_startup_backup.py:279-301` | AC1 称「disabled 时 restore 仍可用」，但无用例；当前仅由「`_BACKUP_ENABLED_KEY` 只在 `_ensure_automatic_backup` 读取」的代码审读保证。 | 搜索 `auto_enabled` 仅该用例；restore 用例未在 disabled 元数据下运行。 | 增 1 例：disabled + 一条 restore 成功（或登记为代码级论证）。 | open |
| S5-007 | P3 | `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/PLAN-HISTORY.md`（提交 `4befab5f3`） | 实现提交含 4 个卡面 `allowed_paths` 之外的治理指针文件，与 AC6「diff ⊆ allowed_paths」字面不符；内容仅为 `in_review` 生命周期指针（无 done 误标、无契约/pins 改动），check.ps1 PASS。 | `git show --stat 4befab5f3`；`git diff --name-only cf563a711..4befab5f3 -- doc/contracts doc/plan` 为空。 | 在卡面把 DSH 生命周期指针登记为写域，或修正 AC6 措辞。 | open |
| S5-008 | P3 | `src/bootstrap/core_service.py:8062-8092`（receipt/失败计数写入） | 新增的 `_write_metadata_json/_write_backup_receipt` 抛出的 `sqlite3.Error` 不在 `_ensure_automatic_backup` 的 `except NmbakBackupError` 内，DB 锁/只读等场景会穿透到 `run`（`main()` 的 try 只有 finally，无 except）→ 启动中断，与「失败不阻断启动」的表述不完全一致；旧代码 `list_backups()` 已有同类暴露，故非本片回归。 | 代码审读：`except NmbakBackupError`（`:8244`）不覆盖 sqlite；`create` 的异常已被 nmbak 包装（`nmbak.py:335`）。 | 给 receipt/计数写入加 `sqlite3.Error` fail-soft（打印后继续），或登记为既有约束。 | open |
| S5-009 | P3 | `tests/infrastructure/test_nmbak_startup_backup.py:259-276` | AC4 用例无判别力：旧实现（跨类型取最新 verified）下「手动包刚建 → 不轮转 → automatic 仍为 1」同样通过；README 已自认变异②不可判别。 | 用例断言 `len(automatic_after)==1`；旧逻辑同结果。 | 注入时钟/直接构造「automatic 明显更旧 + manual 刚建」再断言不发生轮转。 | open |

**计数：P0=0，P1=0，P2=3，P3=6。**

## Architecture 结论

分层正确：纯调度/保留模型放 `application/maintenance`，Core 承担执行与持久化；配置与 receipt 复用 `application_metadata`（无 DDL、无 Host 定时器、无契约改动）。D4 以「只轮转 automatic + 保护集」实现，属保守方向，不删恢复链。主要架构性缺口是保留预算只覆盖 automatic，pre_migration/pre_restore 从此无界（S5-003），需 DSH 裁决是补预算还是明确永不删。

## Verification 结论

按 4 文件口径 **48 passed（EXIT 0）**、check.ps1 两种调用均 PASS（EXIT 0）、pins 18/18 PASS（EXIT 0）、EV 4/4 字节一致、独立 D4 变异 RED→GREEN 并字节还原。未发现关键验证缺失；AC2 字面项（receipt kind）与 AC6 字面项（diff 集合）为文档/AC 一致性问题，非运行时失败。

## 结论与复审

**approved_with_conditions**（0 P0 / 0 P1）。固定 head `5e8b7712d`（实现 `4befab5f3`）的调度/保留/失败语义在运行时层面可交 DSH 集成；进入 done 前须处置以下条件：

1. **S5-001/S5-002（P2）**：收敛 receipt 口径——实现 not-due/schedule-disabled 的 receipt，或修订卡面 AC2 的 kind 枚举 + README「每次决策写」措辞（二者必须一致，AC2 才能按字面判 MET）。
2. **S5-003（P2）**：对 `pre_migration/pre_restore` 的保留作出裁决（补预算或正式登记永不删 + 磁盘增长风险）。
3. **S5-007（P3）**：修正 AC6「diff ⊆ allowed_paths」措辞或登记 DSH 生命周期写域。

S5-004/005/006/008/009 可登记为残余（P3，不阻塞集成）。复审仅对本 head 有效；新 head 须另行提交并追加 disposition。
