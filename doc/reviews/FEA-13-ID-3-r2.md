---
task_id: FEA-13-ID-3
reviewer: DSH 独立上下文子 agent（parent `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`）
reviewer_kind: subagent
author: dsh
base_commit: 54453abb3
reviewed_head: 67bccb08d
implementation_head: 3d8b5507e
previous_review: doc/reviews/FEA-13-ID-3-r1.md
decision: approved
---

# Review r2：FEA-13-ID-3（r1 findings 处置复核）

## 范围与依据

- 只读复审；本次唯一写入文件为本报告。未改生产源码/测试/契约，未 commit/push。
- 被审 head `67bccb08d`（r2 返修），父链 `54453abb3` → `3d8b5507e` → `9867e48ed` → `67bccb08d`。
- 对照：`doc/reviews/FEA-13-ID-3-r1.md`（changes_requested；P0=0/P1=0/P2=1/P3=4）、Task 卡 `doc/tasks/FEA-13-ID-3.md` §Review 处置、`verification/FEA-13-ID-3/`。
- 变更面：`git diff 9867e48ed..67bccb08d --stat` = 10 文件，代码 3 文件（`core_assembly.py`、`identity.py`、`nmbak.py`）+ 测试 1 文件 + 卡/README/2 日志/E2 ledger/r1 报告。全部落在 `allowed_paths`（`doc/reviews/FEA-13-ID-3-*.md`、`verification/**`、3 个 src、`tests/storage/test_nmbak_identity.py`、卡）内；唯一例外 `doc/TASK_LEDGER.md` 属 Integrator 记账，沿用 r1 对 `9867e48ed` 的口径不计 finding（其 563/0/12 与 `check.ps1` 的「12 个非终态」及 `doc/tasks/*.md` 计数 564-README=563 一致）。
- 未审到：全量 `dotnet test`、`tests/storage` 全量、真实用户库/多进程并发（与 r1 同口径）。

### 视角状态

- **Architecture**：`executed`（迁移钩子接线、身份读取时机、门禁归一化、事务契约）。
- **Verification**：`executed`（实跑 4 项门禁 + 4 个 EV hash + 新增用例判别力的反证）。
- **Spec**：`executed`（R-001…R-005 逐条 + AC3 重判）。
- **Standards**：`N/A`（无仓库级编码标准冲突）。

## r1 findings 逐条判定

| ID | 原级别 | r2 判定 | 核对证据 |
|---|---|---|---|
| R-001 | P2 | **FIXED** | `core_assembly.py:175-182` 现传 `database_id_reader=lambda: read_database_id(self._conn)`（模块级 import 在 `:136`，r1 前即存在，lambda 在调用时解析模块全局，**无 NameError**）。新增用例 `test_pre_migration_package_carries_the_existing_identity`（`tests/storage/test_nmbak_identity.py:168-186`）非空断言：直接构造真实 `_NmbakMigrationBackup`，`_had_history` 为真（`_open` 已 `apply_pending`），断言包内 `manifest["database_id"] == identity`。**判别力反证**：用 r1 前形态（不传 reader）在真实库上复现，manifest 为 `None`（本 Review 实跑 `PRE_FIX_WOULD_FAIL_ASSERT=True`），故该用例在旧代码上必红。注释已改为「首次启动 unknown、后续升级携带既有身份」。附加 `data_root=self._backup_root.parent` 与构造器默认值（`nmbak.py:181`）等值，属冗余但无行为变化 |
| R-002 | P3 | **FIXED** | `nmbak.py:358-367` 两侧 `str(...).strip()` 归一化后再比较；空白/纯空白退化为 falsy → 与 unknown 同义（不误判 mismatch）。manifest 无签名的纵深防御风险已登记于 `verification/FEA-13-ID-3/README.md` 残余清单（「纵深防御」条） |
| R-003 | P3 | **PARTIAL** | 注释已改（`:1201-1206` 现描述惰性读取与时机）；但 `:1207` 新增的**函数内** `from infrastructure.sqlite.identity import read_database_id  # noqa: F401 (used by the hook below)` 是死代码——模块级 `:136` 已导入同一名字，钩子解析的是模块全局而非该局部名，注释「used by the hook below」失真，且 `# noqa: F401` 掩盖了未使用。既有日志句「this session performed no write」对旧库回填仍失真，仅在卡内登记后续（README 残余清单未列），按原 r1 建议可接受为 defer |
| R-004 | P3 | **FIXED** | `identity.py:48-56` docstring 显式声明「**no active caller transaction**」，说明 `with conn:` 会在迁移事务内提前提交，并说明损坏值降级 `None`（unknown）的语义与门禁关系。r1 的可选建议（损坏值留诊断日志）未实现，但语义已文档化，不阻断 |
| R-005 | P3 | **PARTIAL** | ①已补：`test_v1_package_without_identity_is_unknown_and_still_restores`（`:189-216`）把真实 v2 包重写为 v1 形态（`format="nm-backup"`、`format_version=1`、删除 `version`/`database_id`），当前库**确有身份**却仍放行 restore —— 断言有效（非空）。③C# 解析测试未补，卡内以「不在 allowed_paths」登记残余，经核对 `allowed_paths` 确实只含 `CoreServiceClient.cs`/`HostRuntime.cs`、无 C# 测试路径，理由成立。②（list 对 v1 返回 null）、④（并发幂等）、⑤（V11R wire 行）未动，按 r1「可留后续」 |

**统计：FIXED 3（R-001/R-002/R-004）· PARTIAL 2（R-003/R-005）· OPEN 0。无新增 P0/P1。**

## 新增 findings（均为 P3，不阻断）

| ID | 级别 | 文件/行 | 说明 | 建议 |
|---|---|---|---|---|
| N-001 | P3 | `doc/tasks/FEA-13-ID-3.md:98-99` | §Review 处置表的 R-001 行被**裸换行**截断：`迁移包恒 ` + LF + `ull、绕过门禁…`，即「null」丢字成「 ull」，且该行仅 2 列、`**已修**` 单元格掉到独立行，表格结构损坏。R-001 恰是 r1 唯一阻塞项，其处置记录不可被机器/人稳定解析 | closeout 前修复为单行完整表格行（同时核对「data_root」表述的冗余性质） |
| N-002 | P3 | `src/bootstrap/core_assembly.py:1207` | 死 import + 失真注释（见 R-003），属可读性缺陷；若后续 lint 收紧会触发 F401 | 删除该局部 import 与 `# noqa`，注释保留「惰性读取」语义即可 |
| N-003 | P3 | `src/bootstrap/core_assembly.py:1204-1206` | 注释措辞仍不精确：全新库（无 `schema_migrations`）时钩子是 **no-op**（`_had_history=False` 直接返回 `""`），不会产出「unknown 包」；真正写 null 的场景是**旧库首次升级**（有历史、无身份）。当前措辞「on a brand-new library it is still unknown at that moment」以偏概全 | 改为「旧库首次升级时仍 unknown，回填后每次升级携带身份」 |

## Acceptance Criteria 重判

| AC | r1 | r2 | 依据 |
|---|---|---|---|
| AC1 原子写入/幂等 | MET | **MET** | 未改动；4 文件定向 pytest 43 passed（EXIT 0） |
| AC2 旧库回填 | MET | **MET** | 未改动 |
| AC3 manifest 携带 | PARTIAL | **MET** | 迁移钩子已接线：库有身份时 `pre_migration` 包携带真实身份（新用例 + 反证）；无身份（旧库首次升级）写 `null`；v1 包读作 unknown。AC3 字面「与库一致」现对两类包均成立 |
| AC4 跨库 restore 拒绝 | MET | **MET** | 门禁归一化后行为不变；变异日志仍为 1 failed/7 passed，失败点 `test_nmbak_identity.py:147` 与当前文件行号一致，证据未过期 |
| AC5 list 投影 | MET | **MET** | 未改动；`dotnet build` 0 警告 0 错误 |
| AC6 门禁 | MET | **MET** | 本 Review 实跑 4 项全 EXIT 0；EV 4/4 字节一致；返修 diff ⊆ allowed_paths（除 TASK_LEDGER 记账，见上） |
| E4「wire 解析测试」 | — | **未执行**（证据计划列了该项，但 allowed_paths 无 C# 测试路径） | 已在卡内登记；建议后续片补 |

## 验证（本 Review 实跑，环境 Windows / Python 3.14 / `67bccb08d`）

| 场景 | 命令 | 结果 |
|---|---|---|
| 定向 pytest（卡要求 4 文件） | `python -m pytest tests/storage/test_nmbak_identity.py tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_format.py tests/storage/test_nmbak_coverage.py -q` | **PASS**，`43 passed in 4.80s`，**EXIT 0** |
| C# 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Debug --nologo` | **PASS**，`0 个警告 / 0 个错误`，**EXIT 0** |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-13-ID-3.md` | **PASS**（3 warnings：12 非终态 / STATUS 80% / PLAN 80%），**EXIT 0** |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS**，`PIN AUDIT: PASS (all 18)`，**EXIT 0** |
| EV 字节一致性 | 4 个 `Get-FileHash -Algorithm SHA256` 对照卡 | **PASS，4/4 MATCH**（README `0c8169ad…`、suite `9c42206c…`、mutation `edf86bd1…`、build `a1f492e5…`） |
| 证据自洽 | 读 `logs/pytest-backup-suite.log`、`logs/mutation-db-gate.log` | PASS：suite `EXIT=0` + `82 passed`（含 identity 8 例）；变异 `EXIT=1` + 1 failed/7 passed，失败行号与当前测试一致 |
| R-001 用例判别力 | 内联 Python 复现 r1 前形态（不传 reader） | PASS：manifest `database_id=None` ≠ identity，证明新用例会红 |
| `git status --short` | — | 写本报告前**干净** |
| 全量 `dotnet test` / `tests/storage` 全量 | — | **NOT_RUN**（与 r1 同口径的环境限制，卡与 README 已声明） |

## 结论

- **verdict: `approved`**。r1 唯一阻塞项 R-001 已实质修复且有判别力证据；R-002/R-004 完整修复；R-003/R-005 按登记口径为 PARTIAL 且均已登记残余；**无新增 P0/P1**，AC1–AC6 全部 MET。
- 建议在 closeout 前顺手清掉 3 个 P3：N-001（卡表裸换行/丢字）、N-002（死 import + 失真注释）、N-003（注释把「全新库」与「旧库首次升级」混写）。三者不改变任何运行时行为。
- 本次审查独立于实现与返修（r2 返修由实现方完成，本报告作者未参与）。
