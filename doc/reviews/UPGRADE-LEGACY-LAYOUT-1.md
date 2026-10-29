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
