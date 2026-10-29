---
task_id: UPGRADE-LEGACY-LAYOUT-1
reviewer: region-workbench-owner
author: dsh-lead
base_commit: af6d9e94d
reviewed_head: 154f97a5c6a636b7ce319677b109e076b5ad33d3
decision: changes_requested
---

# Review：UPGRADE-LEGACY-LAYOUT-1

**Reviewer 独立性**：本 Review 由 region-workbench-owner 执行，未参与该修复实现；实施与自查由 dsh-lead（DSH）完成。只读审查，未修改产品代码、测试或证据。

**执行口径**：覆盖 Architecture（启动时序、数据安全、幂等、隔离、Windows I/O、回滚、契约）与 Verification（单测实跑、证据核对、故障注入）。按用户要求只运行 `tests/infrastructure/test_upgrade_legacy_layout.py` 子集，不运行全量 pytest；全量结果只核对其证据文件本身。

## 范围与依据

- 审查对象：`git show 154f97a5c`（main 已集成），base `af6d9e94d`。
- 关键文件：
  - `src/infrastructure/sqlite/upgrade_legacy_layout.py`（新增，170 行）
  - `src/bootstrap/core_service.py:4588-4628`（`main()` 调用）
  - `tests/infrastructure/test_upgrade_legacy_layout.py`（7 用例）
  - `verification/UPGRADE-LEGACY-LAYOUT-1/{unit-tests.log,real-data-verify.json,pytest-full-summary.txt,pytest-full.log}`
- 依据：Task 卡 AC1–AC5、`doc/tasks/UPGRADE-LEGACY-LAYOUT-1.md`；Review 模板 `doc/templates/REVIEW.md`。

## Architecture 结论

- **调用时机（PASS）**：`core_service.py:4588-4601` 在 `_ensure_preview_namespace`（`:4621`）和 `assemble_production_core`（`:4628`）之前调用迁移，中间没有打开 `library.db`；`assemble_production_core` 才开始使用 `data_root / "library.db"`。
- **正常路径数据安全（PASS）**：只复制不删除；根 `library.db` 已存在时直接跳过（`:141-147`）；损坏库在 staging 上 `PRAGMA integrity_check` 失败（`:73-85`），不 promote，staging 在 `finally` 清理（`:169-170`）；旧 `data/` 始终保留，正常回滚成立。
- **正常幂等（PASS）**：第一次迁移后根库存在，第二次返回 skipped（`:143-147`）；单测覆盖。
- **NEWMANGA_DATA_ROOT 隔离（代码层 PASS，无测试）**：`main()` 用 `NEWMANGA_DATA_ROOT` 计算 `data_root` 后传给迁移（`:4589-4596`），迁移不触碰默认数据根；但未在测试或集成层验证。
- **Windows I/O 边界（FAIL，P1）**：`_copy_file`（`:68-70`）、`os.replace`（`:99`）、`copytree`（`:116-117`）的 `OSError/PermissionError` 未被转换成 `LegacyLayoutError`；`main()` 只捕获 `LegacyLayoutError`（`:4595-4601`），因此文件被占用/权限不足时启动会抛出未捕获异常，而不是打印警告并继续。
- **失败原子性（FAIL，P1）**：数据库在 `:99` 先 promote，`managed/backups` 在 `:155-158` 后复制。目录复制失败时根 `library.db` 已落地，随后启动抛错；下一次启动因根库存在直接跳过迁移（`:141-147`），`managed/backups` 可能永久缺失。模块 docstring `:24-25` 的“失败后 data root 保持原样”不成立。
- **契约（PASS）**：`git show 154f97a5c --stat` 仅含 core_service 导入/调用、新模块、测试和证据；未改命令面、DB schema、共享契约。

## Verification

| 场景 | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| 单测（7 用例） | `python -m pytest tests/infrastructure/test_upgrade_legacy_layout.py -q`（repo root） | **PASS：7 passed in 0.23s**（Python 3.14.6） | 本次 review 实跑 |
| 证据日志核对 | 读取 `verification/UPGRADE-LEGACY-LAYOUT-1/unit-tests.log` | **FAIL**：文件内容为 `no tests ran ... ERROR: file or directory not found: tests/infrastructure/test_upgrade_legacy_layout.py`，不是卡 `:55` 声称的 7 passed；pin `99853b…` 与该错误文件一致 | `unit-tests.log`（4 行） |
| 复制失败注入 | 在临时根上 monkeypatch `shutil.copy2` 抛 `PermissionError` | **FAIL（P1）**：异常直接逃出 `migrate_legacy_layout`，`main()` 不捕获 | probe（task-env 临时脚本） |
| 部分失败注入 | monkeypatch `_promote_directory` 抛 `PermissionError` | **FAIL（P1）**：异常后根 `library.db` 已存在；第二次调用返回 `current library.db already present`，`managed/` 未被复制 | probe（task-env 临时脚本） |
| 路径含空格 | 临时根 `root with space/data/library.db` 调迁移 | PASS：`migrated=True`（SQLite URI 正常） | probe |
| 真实数据证据 | `real-data-verify.json` + task-env log | **PARTIAL/FAIL**：JSON 记录的是第二次运行（`migrated:false`，`skipped_reason=current library.db already present`），不是 AC4 所称的首次迁移；task-env `real-data-root/logs/upgrade-legacy.log` 有成功迁移行，但未进入 evidence/pin | `real-data-verify.json`、task-env log |
| 全量回归证据 | `pytest-full-summary.txt` / `pytest-full.log` | 证据显示 `2607 passed, 10 skipped, 2 warnings`、末尾 `EXIT=0`；但日志无命令/venv 头（不满足 Q-009 证据纪律）；按用户要求**未独立重跑全量** | 证据文件 |
| 治理门禁 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/UPGRADE-LEGACY-LAYOUT-1.md` | PASS（3 warnings：非终态/STATUS/PLAN 预算） | 本次实跑 |
| Handoff | `Test-Path doc/handoffs/UPGRADE-LEGACY-LAYOUT-1-handoff.md` | **FAIL**：文件不存在，但卡 AC5 `:67` 声称有 Handoff | 文件系统 |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-01 | P1 | `verification/UPGRADE-LEGACY-LAYOUT-1/unit-tests.log`；卡 `:55/:65` | AC3 的“7 passed”证据不成立：日志实际是 “no tests ran / file or directory not found”。当前代码实跑 7 passed，但 pinned 证据无法支持 AC3。 | 读取日志；pin `99853b…` 匹配错误内容；`python -m pytest ...` 实跑 7 passed | 从 repo root（或标准 venv）重新运行单测并覆盖 `unit-tests.log`，带 shell/venv 头与 `EXIT=0`；更新 pin/卡证据。无需改产品代码。 | open |
| R-02 | P1 | `verification/UPGRADE-LEGACY-LAYOUT-1/real-data-verify.json`；卡 `:56-58/:66` | AC4 的 pinned 证据只记录第二次运行（`migrated:false`），未记录首次迁移；task-env log 有成功行但未入库/pin，无法由证据独立复现“迁移后 SHA 一致”。 | JSON `result.migrated=false`；task-env `real-data-root/logs/upgrade-legacy.log` | 在**全新副本**上重跑首次迁移并保存输出（含 `migrated:true`、copied、SHA、books、integrity），或把 task-env log 纳入 evidence 并 pin；无需改产品代码。 | open |
| R-03 | P1 | `src/infrastructure/sqlite/upgrade_legacy_layout.py:68-70, 99, 116-117`；`src/bootstrap/core_service.py:4595-4601` | Windows 文件占用/权限失败（`PermissionError/OSError`）不会转换成 `LegacyLayoutError`，`main()` 只捕获后者，启动直接失败；不符合“失败不阻塞启动、可接受行为”的边界要求。 | 故障注入：`copy2` 抛 `PermissionError` 后异常逃出；`main()` 仅 `except LegacyLayoutError` | 将迁移内所有 I/O 失败包装为 `LegacyLayoutError`（保留原异常链），或在 `main()` 捕获 `OSError` 并打印警告后继续；补对应测试。 | open |
| R-04 | P1 | `src/infrastructure/sqlite/upgrade_legacy_layout.py:99-108, 155-158`；docstring `:24-25` | promote DB 后复制 `managed/backups`，目录复制失败会留下“根库已存在 + 目录缺失”的部分状态；下次启动的当前库守卫永久跳过迁移，用户旧页面不可见（旧 `data/` 仍在，可手动回滚但无提示）。docstring 的“失败后 data root 保持原样”与事实不符。 | 故障注入 `_promote_directory` 抛错：根库存在；第二次调用 skipped | 先完整 staging 数据库+managed+backups 并验证，再统一 promote；或检测到当前库由迁移创建但目录缺失时允许续迁/修复；补部分失败测试。 | open |
| R-05 | P2 | `src/infrastructure/sqlite/upgrade_legacy_layout.py:114` | 当前 `managed/` 或 `backups/` 已存在时整个目录被跳过；若新版本曾先启动一次留下空目录，旧布局的 managed 页面不会复制，升级后仍不可见。 | 代码路径；当前布局优先策略 | 评估合并/非空目录处理，或至少记录日志并在文档说明；补测试。 | open |
| R-06 | P2 | `tests/infrastructure/test_upgrade_legacy_layout.py` | 7 用例覆盖正常/当前优先/no-op/幂等/WAL/损坏/日志，但未覆盖：`main()` 调用顺序与 LegacyLayoutError 继续启动、`NEWMANGA_DATA_ROOT` 隔离、OSError/文件占用、部分失败、已存在 managed 目录、`-journal` 残留。 | 逐条核对测试文件 | 补关键边界测试，尤其 R-03/R-04/R-05。 | open |
| R-07 | P2 | `verification/UPGRADE-LEGACY-LAYOUT-1/pytest-full.log`、`pytest-full-summary.txt` | 全量日志无命令/shell/venv 头；仅有 summary 和末尾 `EXIT=0`，不满足 Q-009 证据纪律；单测日志同样缺少头且内容错误。 | 读取日志首尾 | 重新生成带完整头的全量日志并更新 pin。 | open |
| R-08 | P2 | 卡 `:67` AC5；`doc/handoffs/` | AC5 声称有 Handoff，但 `doc/handoffs/UPGRADE-LEGACY-LAYOUT-1-handoff.md` 不存在。 | `Test-Path` = False | 补 Handoff（模板五节）并纳入交付记录。 | open |
| R-09 | P2 | `src/infrastructure/sqlite/upgrade_legacy_layout.py:41` | 仅处理 `-wal/-shm`，不处理旧崩溃遗留的 `library.db-journal`；若有 rollback journal，可能 integrity 失败或遗漏已提交事务（旧数据保留，但升级可能不生效）。 | 代码路径 | 评估 journal 处理或明确 fail-closed 并记录；补测试。 | open |
| R-10 | P2 | `src/infrastructure/sqlite/upgrade_legacy_layout.py:141-147` | 若用户已先启动过新版本（根库被创建为空库），迁移永久跳过旧布局，书架仍为空；当前任务未覆盖该“已打开一次”的升级路径（当前库绝不覆盖是正确安全策略，但产品缺口仍在）。 | 代码路径；单测 `test_current_layout_wins` | 在文档/后续任务中登记该限制，评估空根库识别或提示用户；不要静默覆盖。 | open |

## 未覆盖 / 限制

- 未运行全量 pytest（按用户要求仅跑子集）；全量数字仅按证据文件核对，未独立复现。
- 未做真实 Windows 文件占用/ACL 实测；使用故障注入证明异常路径（足以证明未捕获类型，不代表真实句柄语义）。
- 未审查产品其他启动路径（如 Host 进程）是否也调用迁移；本卡只要求 Core 启动。

## 结论与复审

**FAIL / CHANGES_REQUESTED @ `154f97a5c`**：P0 = 0；P1 = 4（R-01 AC3 证据不成立、R-02 AC4 证据只覆盖第二次运行、R-03 Windows I/O 失败逃逸导致启动崩溃、R-04 非原子 promote 留下不可自愈的部分迁移状态）；P2 = 6。R-01/R-02 只需重跑并重打证据；R-03/R-04 需要代码加固（最小修复：I/O 失败包装为 `LegacyLayoutError` 并在 `main` 安全处理；先 staging 全部内容再 promote/或支持续迁）及对应测试。R-03/R-04 修复后需重新执行单测、真实数据首次迁移证据和（按 DSH 决定）全量回归，再送复审。

作者不可自审；本结论仅对 `154f97a5c` 有效，head 变化后需重新审查。

## Round 2 Review

**reviewed_head**: `27de6fce3e6ad8a2d2da434fc67d3ac1da9d1f13`；**decision: changes_requested（FAIL）**。

**复核方式**：只读检查 `27de6fce3` 的代码/测试/证据；repo root 实跑 10 个单测；按 round 1 方法做 I/O、promote 失败、sidecar 失败、current-db/corrupt-legacy 故障注入；核对 5 个证据 SHA-256 与 `check.ps1`；`git show 27de6fce3 --stat` 核对 allowed_paths。全量 pytest 未独立重跑（用户要求）。

### R-01..R-07 逐项状态

| 项 | round 1 问题 | 状态 | 证据/复核结论 |
|---|---|---|---|
| R-01 | unit-tests.log 是 “no tests ran” | **PASS（已修复）** | `unit-tests.log` 现有 COMMAND/CWD/PYTHON/AT + `10 passed` + `EXIT=0`；pin 匹配；本次 repo root 实跑 10 passed（0.30s）。 |
| R-02 | real-data 证据只记录第二次运行 | **PASS（已修复）** | `real-data-first-migration.json`：`migrated=true`、`copied=[managed/,backups/,library.db]`、源 SHA 前后不变、新库 SHA 一致（`96fc4120…`）、books=1、schema=6、integrity=ok、data 保留；`real-data-second-run.json`：`migrated=false`（幂等）。 |
| R-03 | I/O 异常逃逸会崩溃启动 | **PASS（已修复）** | 故障注入 `shutil.copy2→PermissionError`：现在转为 `LegacyLayoutError`，根无 DB、无 managed、staging 清理；`shutil.Error`（`copytree` 聚合异常）实测是 `OSError` 子类并被包装；`main()` 捕获后继续。 |
| R-04 | 非原子 promote / 部分状态不可自愈 | **FAIL（仍有 P1）** | 见 R2-01、R2-02：sidecar 在 DB 之后 promote，失败会留下“根 DB 已存在、WAL 缺失”；目录先 promote 后 DB 失败会留下部分根目录；更关键是失败后 `main()` 继续，`assemble_production_core` 会创建**空根 `library.db`**，下一次启动的 current 守卫会永久跳过旧库迁移。 |
| R-05 | 当前库存在时跳过（旧 managed 不补） | **PARTIAL（P2）** | 正常 current DB + 缺失 managed/backups 会补迁（单测/代码成立）；但 current DB 存在时仍先 stage+verify legacy DB，若 legacy DB 损坏/被占用则整次迁移抛错，缺失目录得不到补迁（探针 D）。 |
| R-06 | 边界测试缺失 | **PARTIAL（P2）** | 10 用例实跑通过，但缺少：sidecar promote 失败、目录 promote 失败、失败后 main 创建空库、current DB + corrupt legacy、`NEWMANGA_DATA_ROOT` 主入口、已有 managed 目录。 |
| R-07 | 证据头缺失 / Handoff 缺失 | **PARTIAL（P2）** | unit 日志已带头；但 `pytest-full.log:1` 仅为 `----`，无 COMMAND/CWD/PYTHON/AT（卡宣称“带命令头”不成立）；Handoff 已存在但 frontmatter `head: 311ddfe0d (review) / rework commit pending` 过期，且引用不存在的 `pytest-full-v2.log`；旧 `real-data-verify.json` 仍留在 evidence_dir 但未登记，`check.ps1` 因此新增 warning；Handoff 也不在卡 `allowed_paths`。 |

### Round 2 Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R2-01 | P1 | `src/infrastructure/sqlite/upgrade_legacy_layout.py:101-112, 204-215` | DB 文件（含 `-wal/-shm/-journal`）按 `staged_db_files` 顺序逐个 `os.replace`，base DB 先于 sidecar。以 `-wal` 为例，base 成功、sidecar 失败时根 DB 已落地且无 WAL；异常被包装后 main 继续，下一次启动 `current_exists=True` 只补目录、不补缺失 sidecar，可能丢失 WAL 中未 checkpoint 的事务。 | 故障注入 `_promote_file` 对 `library.db-wal` 抛 PermissionError：`root_db=True, root_wal=False`；第二次 `migrate` 返回 skipped 且 WAL 仍缺失。 | sidecar 先 promote、DB 最后；或在 `current_exists=True` 时检测并补缺失 sidecar；加 sidecar promote 失败测试。 | open |
| R2-02 | P1 | `src/bootstrap/core_service.py:4595-4601, 4628`；`core_service.py:707`；`core_assembly.py:942`；`connection.py:344-346` | `main()` 捕获 `LegacyLayoutError` 后继续执行 `assemble_production_core`；OpenDatabase 在根库缺失时会创建**空库**（probe：`SchemaState.EMPTY`）。随后 `current_exists=True`，旧 `data/library.db` 永久不再迁移；用户看到空书架（旧数据仍在 `data/`，但无提示/自动恢复）。目录先 promote 后失败的场景即可触发。 | 故障注入 `_promote_directory` 对 `backups` 失败：root managed 已存在、root DB 不存在；模拟 `open_database` 后创建空 root DB；retry 仅返回 `copied=['backups/']`，root DB 仍无 books 表。 | 迁移失败且当前根库不存在时，不应继续 assemble 创建空库（可返回错误/记录 pending 标记）；或在下一次启动识别“空新库+pending 迁移”并允许旧库迁入/提示用户。 | open |
| R2-03 | P2 | `src/infrastructure/sqlite/upgrade_legacy_layout.py:208-215`；docstring `:26-31` | 多个目录按字典顺序 promote；第一个目录成功后第二个失败会把已成功目录留在 root，docstring/卡“失败不落地/根保持原样”不成立（retry 可续，但原子声明过强）。 | 故障注入 `_promote_directory` 对 `backups` 失败：root `managed=True`、`backups=False`、root_db=False。 | 目录整体 staging/promote 策略要么接受“部分目录可续”并如实描述，要么用临时根目录整体切换；补 promote 失败测试。 | open |
| R2-04 | P2 | `src/infrastructure/sqlite/upgrade_legacy_layout.py:174-183` | `current_db.exists()` 时仍无条件 `_stage_database` 复制+校验 legacy DB；若 legacy DB 损坏/被占用，直接抛 `LegacyLayoutError`，R-05 的 missing managed/backups 补迁不执行。 | 探针 D：current DB 正常、legacy `data/library.db` 为 “not sqlite”、data/managed 存在 → `LegacyLayoutError`，root managed 未生成。 | 仅在 `not current_exists` 时 stage DB；current 存在时只 stage 目录；补测试。 | open |
| R2-05 | P2 | `tests/infrastructure/test_upgrade_legacy_layout.py` | 10 用例未覆盖 R2-01/R2-02/R2-03/R2-04 及 `NEWMANGA_DATA_ROOT` 主入口；卡 AC3 的“隔离 root 传参/部分失败”覆盖不完整。 | 逐条核对测试文件；故障注入均为手工探针，无对应回归测试。 | 新增上述边界测试；优先覆盖 sidecar promote 失败、失败后空 root DB、corrupt legacy + current DB。 | open |
| R2-06 | P2 | `verification/UPGRADE-LEGACY-LAYOUT-1/pytest-full.log:1`；`unit-tests.log`；Handoff frontmatter | 全量日志缺 command/shell/venv 头（首行 `----`），与卡“带命令头”不符；Handoff `head` 仍是 `311ddfe0d (review) / rework commit pending`（实际 27de6fce3），并引用不存在的 `pytest-full-v2.log`。 | 读取日志/Handoff | 重生成全量日志头并更新 pin；Handoff 更新 head/status/文件名；补 Handoff 到 allowed_paths。 | open |
| R2-07 | P2 | 卡 `allowed_paths`；`verification/UPGRADE-LEGACY-LAYOUT-1/real-data-verify.json` | `27de6fce3` 新增 `doc/handoffs/UPGRADE-LEGACY-LAYOUT-1-handoff.md`，但卡 allowed_paths 未包含该路径（超出实现范围）；旧 `real-data-verify.json` 留在 evidence_dir 未登记，`check.ps1` 报 warning（4 warnings，DONE 时会报错）。 | `git show --name-status 27de6fce3`；`check.ps1` 输出 | 在卡 allowed_paths 补 handoff；登记/移走旧证据，避免 DONE evidence_dir 未登记文件。 | open |
| R2-08 | P2 | `src/infrastructure/sqlite/upgrade_legacy_layout.py:141-147`；`connection.py` | 用户已先启动新版本创建空根库时，旧布局仍被跳过；本 task 未处理该“已打开一次”的升级路径（当前库不覆盖是安全策略，但产品缺口仍在）。 | 代码路径；R2-02 也揭示同类空库问题 | 在后续任务/文档中登记限制，评估空库识别或提示用户；不要静默覆盖。 | open |

### Round 2 验证

| 场景 | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| 单测 10 用例 | `python -m pytest tests/infrastructure/test_upgrade_legacy_layout.py -q`（repo root） | PASS：10 passed in 0.30s | 本次实跑；`unit-tests.log` 亦一致 |
| I/O 包装 | `copy2→PermissionError` 故障注入 | PASS：`LegacyLayoutError`，根不变、staging 清理 | 本次探针 |
| sidecar promote 失败 | `_promote_file` 对 `-wal` 抛 PermissionError | FAIL：root db 存在、wal 缺失；retry skipped，无修复 | 本次探针 |
| 目录 promote 部分失败 | `_promote_directory` 对 `backups` 抛 PermissionError | FAIL：root managed 已留下（非原子）；随后 main 继续会创建空 root DB | 本次探针 |
| current DB + corrupt legacy | current DB 正常、legacy db “not sqlite”、legacy managed 存在 | FAIL：`LegacyLayoutError`，managed 未补迁 | 本次探针 |
| 真实数据证据 | first/second JSON | PASS：首次 migrated=true、SHA/books/integrity 一致；第二次幂等 | `real-data-first-migration.json`、`real-data-second-run.json` |
| 证据 pin | 5 个 sha256 | PASS：5/5 与 pin 一致 | 本次实算 |
| 门禁 | `check.ps1 -TaskPath` | PASS（4 warnings；新增未登记 `real-data-verify.json` warning） | 本次实跑 |
| 契约 | `git show 27de6fce3 --stat` | 仅允许的源码/测试/证据 + handoff；未改命令面/schema | commit diff |

### Round 2 结论

**FAIL / CHANGES_REQUESTED @ `27de6fce3`**：P0=0；P1=2（R2-01 sidecar 非原子、R2-02 失败后空根库导致旧库永久不迁移）；P2=6。R-01/R-02/R-03 已闭环；R-04 仍未真正闭环，R-05/R-06/R-07 为部分闭环。最小修复：
1. sidecar 先 promote、DB 最后，或在 current DB 存在时补缺失 sidecar；
2. 迁移失败且当前根库不存在时不要静默创建空根库（返回错误/写 pending 标记/下一次启动识别并允许旧库迁入），并补对应测试；
3. `current_exists` 时跳过 legacy DB staging/verify，仅补目录（避免 corrupt legacy 阻塞补迁）；
4. 补全 sidecar/目录 promote 失败、失败→空库、`NEWMANGA_DATA_ROOT` 等测试；
5. 重生成带 command 头的全量日志、修正 Handoff 元数据/文件名、补 handoff 到 allowed_paths、登记/移走旧 `real-data-verify.json`。

修复后需重新执行 10 用例、真实数据首次/二次证据和全量回归，再送第三轮复审。
