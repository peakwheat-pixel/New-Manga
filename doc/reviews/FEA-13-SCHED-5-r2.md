---
task_id: FEA-13-SCHED-5
reviewer: 独立上下文子 agent（由 parent session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5 派发；未参与实现/返修，只读被审 head）
reviewer_kind: subagent
author: dsh
base_commit: cf563a711
r1_head: 5e8b7712d
reviewed_head: 74fca0f11
decision: approved
---

# Review r2：FEA-13-SCHED-5（r1 处置复审）

## 范围与依据

- 被审：`git diff 5e8b7712d..74fca0f11`（8 文件，+184/-16）；生产码仅 `src/application/maintenance/backup_schedule.py`（`select_prunable` 三类筛选）与 `src/bootstrap/core_service.py`（not-due / `missed_or_due` receipt）；测试仅 `tests/infrastructure/test_nmbak_startup_backup.py`（+2 例）；其余为卡 §Review 处置、r1 报告、EV README/suite 日志、`doc/TASK_LEDGER.md`。
- 依据：`doc/reviews/FEA-13-SCHED-5-r1.md`、`doc/tasks/FEA-13-SCHED-5.md` §Review 处置、ADJ-2026-11-09 D4、`verification/FEA-13-SCHED-5/`。
- out_of_scope：`doc/contracts/**`、`doc/plan/**`、`tools/governance/**`、`src/host/**` 相对 `cf563a711` **零 diff**；无新增 DDL；无 Host 定时器。
- 只读：未改生产码/测试/契约/pins，未 commit/push；除本报告外工作区 clean。

## 门禁复跑（本会话）

| 命令 | 结果 | EXIT |
|---|---|---|
| `python -m pytest tests/application/test_backup_schedule.py tests/infrastructure/test_nmbak_startup_backup.py -q` | **20 passed**（2.44s） | 0 |
| 同一 10 文件备份面（与 EV-S5-SUITE 同命令） | **110 passed**（11.96s），与 EV 日志一致 | 0 |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-13-SCHED-5.md` | Governance check: **PASS**（3 warnings：12 非终态 Task / STATUS 80% / REBASELINE 80%） | 0 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)** | 0 |
| EV 4 条 sha256（`Get-FileHash`） | **4/4 与当前字节一致**：README `3bfa0a07…`、SUITE `dbad9228…`、MUT1 `4030f756…`、MUT2 `12feeca0…` | — |
| `git status --short` | 除本报告外 clean | — |

## 逐项判定（S5-001…S5-009）

| Finding | r2 判定 | 核实 |
|---|---|---|
| **S5-001** receipt 覆盖声明 | **PARTIAL（残余 P3）** | not-due 分支已写 `kind=not_due`、`status=skipped`、`next_due`、`message`（`core_service.py:8185-8200`）；`auto_enabled=false` 仍写 `disabled`；`backup.schedule.kind="disabled"` 落 not-due 分支写 `not_due`（r1 允许的「not_due/skipped 最小 receipt」口径）。**残余**：`books == 0` 分支（`:8151-8153`）仍直接 return 不写 receipt，而 docstring `:8100`「Every outcome writes」与 README `:16`「每次决策写」仍为全称断言（R2-01）。 |
| **S5-002** AC2 `missed_or_due` | **PARTIAL（残余 P3）** | 已实现：`newest is not None and reason.startswith("missed schedule")` → `kind=missed_or_due`（`:8240-8244`），与 AC2 字面 kind 对齐；新增用例 `test_missed_schedule_receipt_uses_the_ac_kind` 可在修复前代码判红（旧码该场景恒为 `created`），判别有效。**残余**：`missed` 只在年龄 ≥ **2×** 间隔时成立（`:8204-8209`），1×–2× 的「超龄轮转」仍报 `created`，该阈值未在卡/README 记录；用例以 `_AUTOMATIC_BACKUP_REFRESH_HOURS=0.0`（2×0=0）触发，未验证真实超龄边界（R2-03）。 |
| **S5-003** 保留预算三类覆盖 | **FIXED** | `select_prunable` 恢复 `{"automatic","pre_migration","pre_restore"}`（`backup_schedule.py:116-120`），与 `cf563a711:_prune_automatic_backups`（`:8105` 原三类筛选）一致；`manual` 恒排除（`nmbak.py:65` BACKUP_TYPES）；`retained = newest keep ∪ protected_ids`（`:126-127`），D4 保护仍生效；10 文件 110 passed 无回归。**残余**：未新增针对三类的专用用例（R2-05）。 |
| **S5-006** disabled 下 restore 可用 | **FIXED** | 新增 `test_disabled_schedule_keeps_restore_usable`：`auto_enabled=false` → ensure 不建包 → manual create + `restore(confirm_restore=True)` 成功断言 `restored_from`，并验证 receipt 未被 restore 覆盖（仍 `disabled`）。用例有效。 |
| **S5-004** 死代码 / 双真源 | **OPEN（P3，已登记）** | `_AUTOMATIC_BACKUP_KEEP`、`_prune_automatic_backups`、`_package_age_hours` 未删；本片未改。 |
| **S5-005** weekday 未参与判定 | **OPEN（P3，已登记）** | `due()` 仍为 7×24h 间隔；卡面「指定 weekday + 24h 门」未降级措辞。 |
| **S5-007** 治理指针越 allowed_paths | **PARTIAL（P3）** | r2 已在卡 §Review 处置登记为「DSH 生命周期写入惯例」；但 AC6 仍写「diff ⊆ allowed_paths <<MET>>」，而 r2 自身再次修改 `doc/TASK_LEDGER.md`（allowed_paths 外），字面断言仍不成立。 |
| **S5-008** `sqlite3.Error` 穿透 | **OPEN（P3，已登记）** | not-due 分支的 receipt 写入同样未加 fail-soft，风险面略增但不改变既有类别。 |
| **S5-009** AC4 弱用例 | **OPEN（P3，已登记）** | 用例未改，仍无判别力；README 已自认。 |

**计数：FIXED=2（S5-003、S5-006）；PARTIAL=3（S5-001、S5-002、S5-007）；OPEN=4（S5-004/005/008/009，均 P3 登记残余）。**

## 新增/残余 findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| R2-01 | P3 | `core_service.py:8100`、`:8151-8153`、EV README `:16` | `books==0` 分支仍静默，全称断言「Every outcome / 每次决策写」过宽 | 把口径改为「需要动作的决策写 receipt（空库除外）」，或该分支补 `not_due/empty_library` receipt |
| R2-02 | P3 | `core_service.py:8191-8195` | not-due 的 `next_due` 用 `now + interval`，真实下次到期是 `last + interval`；差一个「已过时长」（如 23h/24h 时报 +24h 而非 +1h） | 用 `last + interval` 计算，或注释声明字段为「从现在起的最小等待」 |
| R2-03 | P3 | `core_service.py:8204-8209`；测试 `:408-421` | missed 阈值 2× 未文档化；用例以 0 小时间隔触发，未覆盖真实超龄（如 30h/24h）及 1×–2× 边界 | README/卡面记录阈值，并加一个构造旧 `created_at` 或注入时钟的边界用例 |
| R2-04 | P3 | `verification/FEA-13-SCHED-5/README.md:26-27,32` | EV 内部不一致：AC1 行仍写「108 passed」（日志与复跑为 110）；AC2 行未提 `missed_or_due`/`not_due`；变异行「复原后 13 passed」已过期（该文件现 15 例） | 同步三处数字/枚举；EV-MUT1/MUT2 日志产生于 r2 代码前，建议对新 head 重跑或注明证据时点 |
| R2-05 | P3 | `backup_schedule.py:116-120` | 三类覆盖无专用用例（现有 D4 用例用 automatic id 模拟 `pre_restore`） | 加 1 例：混合 automatic/pre_migration/pre_restore，断言三类同受 keep 预算且 manual 与 D4 保护不被删 |
| R2-06 | P3 | `core_service.py:8240-8244` | 嵌套条件缩进错位（行为正确，可读性差） | 提取 `kind` 变量后格式化 |

**新增 P0/P1：无。** 未发现 manual / `pre_restore` 保护包被新轮转逻辑误删：候选集合不含 `manual`；最新 verified 与 `last_restore_pre_restore_id` 始终并入 `retained`；10 文件 110 passed（含 `test_retention_protects_the_recovery_chain`、merge-restore 全套）。

## AC 判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 调度模型 | **MET** | 四类 `due()`/容错解析/注入时钟不变；disabled 不创建且 restore 有用例（S5-006） |
| AC2 错过计划 receipt | **MET（P3 注）** | `kind=missed_or_due` + `next_due` 已实现并有用例；not-due 也写 receipt；阈值与边界用例见 R2-03 |
| AC3 保留 + D4 | **MET** | 三类预算恢复、manual 永不删、保护集生效；缺专用用例（R2-05） |
| AC4 手动不重置 | **MET（用例弱，S5-009 已登记）** | 代码不变 |
| AC5 失败语义 | **MET** | 未改动；10 文件回归绿 |
| AC6 门禁 | **MET（带 P3）** | 定向 20 passed、10 文件 110 passed、check.ps1 PASS、pins 18/18、EV 4/4；AC6 措辞与治理指针见 S5-007/R2-04 |

## 架构与验证结论

r2 变更方向正确且最小：`select_prunable` 回到旧三类语义（消除 r1 的磁盘无界增长缺口），receipt 补 not-due 与 `missed_or_due`（对齐卡面 AC2 字面枚举），测试补 disabled-restore 与 missed kind。分层与 out_of_scope 未被破坏，未引入 P0/P1 回归。

**结论：approved**（0 P0 / 0 P1 / 0 P2；P3 残余 = S5-004/005/008/009 四条已登记 + R2-01…R2-06 六条新登记）。剩余事项均为文档口径/证据新鲜度/测试强度，可在 done 前顺手修或另立残余；不阻塞 DSH 集成验证。本报告仅对 head `74fca0f11` 有效。
