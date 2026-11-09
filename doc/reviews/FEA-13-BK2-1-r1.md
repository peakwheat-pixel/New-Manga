---
task_id: FEA-13-BK2-1
reviewer: DSH 派发的独立上下文子 agent（review session `a4e50095-25c6-4772-957c-ef0da839e3d2`；父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`；未参与实现）
reviewer_kind: subagent
author: DSH（Lead / Integrator；实现提交 `ac1882fc8`）
base_commit: 1aad960b8
reviewed_head: 0cb4b80d5
decision: approved
---

# Review：FEA-13-BK2-1（backup/2 写端 + 版本协商 + backup/1 只读 adapter）

## 0. 审查者身份、范围与方法

- **审查者来源**：DSH 派发的独立上下文子 agent（`subagent`，review session `a4e50095-25c6-4772-957c-ef0da839e3d2`），未参与本 Task 的设计、实现或返修；只读被审 head，唯一写入文件为本报告。符合 2026-10-31 用户裁决的「上下文独立」口径。
- **被审对象**：base `1aad960b8` → 实现 `ac1882fc8` → 文档 in_review `0cb4b80d5`（worktree `main`，审查开始/结束时 `git status` 均干净）。
- **范围**：`git diff 1aad960b8..ac1882fc8` 的 9 个文件、`1aad960b8..0cb4b80d5` 的 5 个文档文件；受影响调用链 = `NmbakBackupService.create/restore/list` → `_read_manifest` → `_negotiate_manifest` → `_verify_package` → `core_service.py` 备份命令面的错误映射。
- **依据**（按优先级）：任务卡 `doc/tasks/FEA-13-BK2-1.md`；C-09 冻结记录 §9 errata **D1**（`doc/plan/FEA-CONTRACT-FROZEN-C09.md:103`）；裁决 `doc/reviews/ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT.md` §1/§2；scope review `doc/reviews/FEA-13-scope-r1.md` §7 片 1；C-09 草案 SC-B07（`doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md:136-143`）；C-09 冻结记录 §5 第 5 条（`FEA-CONTRACT-FROZEN-C09.md:63`）。
- **方法**：①逐文件读 diff 与全文；②复跑任务卡指定 pytest 与三项治理门禁；③**两处变异判别**（v3 分支→`BACKUP_CORRUPT`、写端 `version`→1）并复原；④独立探针（inline python，产物仅落 `%TEMP%`）：用 **base `1aad960b8` 源码的 writer** 生成真实 backup/1 包再交给新读端恢复、无 `page_original_refs` 旧包、`format_version:2`、`version:"2"`、缺 `version`、`list` 与截断包；⑤核对 EV sha256 与 allowed_paths/out_of_scope。
- **未审/未验证**：全量 pytest 与整套 .NET（本片零 C# 改动）；真实 Host↔Core IPC 下新错误码的 UI 呈现（仅抽样阅读 `CoreServiceClient`/`CommandRegistry`，未见备份错误码闭集，未知码有通用 envelope 兜底）；旧打包二进制的实际拒读行为（以 base 源码模拟代替）；C-09 草案全文逐字节。

## 1. Standards（可选视角，executed）

| 项 | 结论 | 依据 |
|---|---|---|
| 证据纪律（EXIT + shell/venv 头、判别力 artefact） | **未完全满足**（P2，R-002） | `doc/templates/REVIEW.md:54`；两份 mutation 日志无 `# command/# shell/# time/# EXIT=` |
| 写域纪律（allowed_paths） | 实现 diff **9/9 全部在 allowed_paths** | `git diff --name-only 1aad960b8..ac1882fc8` |
| 治理指针 | `check.ps1` 默认/`-TaskPath` PASS（3 warnings：12 个非终态 Task、STATUS/PLAN 预算 80%） | 门禁表 |
| 分层与依赖 | `nmbak.py` 只在 infrastructure 层内新增常量/协商；`core_service.py` 仅 +1 行映射；无新依赖、无 schema 变化 | diff |
| Smell（判断项） | dead `except`、恒真断言（前者本 diff 引入，后者 base 已有） | R-004/R-007 |

## 2. Spec（可选视角，executed）

- **AC 忠实实现**：AC1–AC6 全部可观察项均能在代码/测试/探针中定位（见 §3）。
- **scope creep**：`core_service.py` 仅 `_BACKUP_ERROR_RULES` 新增 `BACKUP_FORMAT_UNSUPPORTED: ("validation", False)` 一行（`:449`），**无** handler/其它逻辑改动；`src/infrastructure/sqlite/backup.py`（`SqliteBackupService`）零 diff；无 `DatabaseId` 真值、无覆盖清单二期、无 merge restore、无调度、无数据根迁移。
- **来源要求但缺失**：C-09 SC-B07 ④「包内加密的源授权元数据段」（草案 `:138`）与 SC-B01「源引用与授权元数据入包」（草案 `:26`、`:38`）不在本片，且 6 片拆分中**无片认领** → R-003（P2）。本片 AC 未要求，故不影响 AC 判定，但影响「SC-B07 已落地」的措辞。

## 3. AC 逐项判定

| AC | 判定 | 证据 |
|---|---|---|
| **AC1 写端 v2** | **MET** | 实测 manifest 顶层键含 `format:"nmbak"`、`version:2`、`database_id:null`、`schema_version:9`，**无** `format_version`；`revision_refs[0]` 与 `page_original_refs[0]` 均含 `sha256`+`size_bytes`（reviewer manifest dump；`tests/storage/test_nmbak_backup.py:120-139`、`tests/storage/test_nmbak_format.py:151-154`）。 |
| **AC2 v1 只读 adapter** | **MET**（证据面见 R-001） | reviewer 探针用 base `1aad960b8` 的 writer 生成**真实** backup/1 包（`nm-backup`/`format_version:1`，无 `version`/`database_id`）→ 新读端恢复成功；包 sha256 + `st_mtime_ns` 前后一致；manifest 未被改写为 v2。另验「无 `page_original_refs` 键」旧包恢复成功（scope review §7 片1 AC2 要求）。提交内测试 `test_nmbak_format.py:143-174` 覆盖同路径（由 v2 包 relabel 合成，见 R-001）。 |
| **AC3 v3 拒绝零副作用** | **MET** | `test_nmbak_format.py:177-204`：`BACKUP_FORMAT_UNSUPPORTED`，DB/managed/包字节/备份目录集合（含无 `pre_restore`）不变；代码顺序 `nmbak.py:304-307`（`_verify_package` 先于 `create("pre_restore")`）；Core 映射 `core_service.py:449` + 查表 `:6981-6983`。reviewer 探针另验 `format_version:2` 的 backup/1 包同样 typed 且零副作用。 |
| **AC4 未知 format** | **MET** | `test_nmbak_format.py:207-220`（同码，且显式 `!= "BACKUP_CORRUPT"`）；`nmbak.py:628-631`。 |
| **AC5 变异判别** | **MET** | reviewer 独立变异 ①v2-version 分支→`BACKUP_CORRUPT`：`pytest tests/storage/test_nmbak_format.py -q` → **1 failed / 3 passed，EXIT 1**；②写端 `version=1`：`create()` read-back 抛 `BACKUP_CREATE_FAILED: read-back verification failed: ... backup/2 version 1 is not supported`，`test_create_package_contains_frozen_v1_layout` **1 failed，EXIT 1**。两处均 `git checkout -- src/infrastructure/sqlite/nmbak.py` 复原，`git status` 干净，复跑 25 passed/EXIT 0。提交内日志可辅证但缺 EXIT 头（R-002）。 |
| **AC6 门禁** | **MET** | 定向 pytest 64 passed/EXIT 0；`check.ps1` PASS/EXIT 0（默认与 `-TaskPath`）；`verify_pins` 18/18/EXIT 0；实现 diff 9/9 ⊆ allowed_paths；out_of_scope 零 diff；EV 表 4/4 sha256 与当前字节一致。 |

**结论**：AC1–AC6 全部 **MET**；无 FAIL/PARTIAL。AC2 的「真实/旧变体」证据由 reviewer 探针补齐，提交内 canonical 证据的形态缺口见 R-001。

## 4. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-001 | P2 | `tests/storage/test_nmbak_format.py:69-73,156-157`；`verification/FEA-13-BK2-1/README.md:21` | AC2 的「真实 v1 包」由**本片 v2 writer 产物 relabel**合成（`_to_legacy_v1` 删 `version`/`database_id`、写 `format_version:1`），并非旧 writer 生成的 golden 字节；`verification/` 下无 fixture 与 sha256 快照；亦未覆盖 scope review §7 片1 AC2 明列的「**无 `page_original_refs`** 的旧包」。影响：兼容性承诺的 canonical 证据形态弱于声明（功能本身经 reviewer 探针验证正确）。 | 探针 A/B：base `1aad960b8` writer 生成的真实 v1 包与「删 `page_original_refs` 键」包均恢复成功且包字节不变。 | 补一份由 base writer 生成的 golden fixture + sha256 快照入库，并加「无 `page_original_refs`」用例；或把 reviewer 探针固化为 `verification/FEA-13-BK2-1/` 脚本与日志后重签 EV。 | open |
| R-002 | P2 | `verification/FEA-13-BK2-1/logs/mutation-v3-corrupt.log`（首行即 pytest 输出）；`.../mutation-writer-version.log`；`doc/handoffs/FEA-13-BK2-1-ac1882fc8.md:22`；`verification/.../README.md:20` | Handoff 声称「3 份日志（含命令头/EXIT）」，实际仅 `pytest-backup-suite.log` 有 `# command/# shell/# time/# EXIT=`；两份 mutation 日志无任何头/EXIT，违反证据纪律（`doc/templates/REVIEW.md:54`）。另 README AC1 行引「25/25」而其指向的 suite 日志为 **64 passed**（子集/总数口径混用，未同处解释）。影响：证据不可自证口径；判别力本身经 reviewer 复现成立，不构成关键验证缺失。 | 逐文件首/末行检查；reviewer 复跑两处变异均 EXIT 1、复原后 25 passed/EXIT 0。 | 重采两份日志（带命令头/EXIT）并重签 EV；README 统一数字口径（64 = 5 文件全套，25 = `test_nmbak_backup.py`+`test_nmbak_format.py` 子集）。 | open |
| R-003 | P2 | `doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md:138`（SC-B07 ④）、`:26/:38`（SC-B01 源授权元数据）；`doc/handoffs/FEA-13-BK2-1-ac1882fc8.md:14` | C-09 要求的「包内**加密**的源授权元数据段」与「源引用与授权元数据入包」本片未实现，且 `ADJ-2026-11-09` §2 的 6 片拆分**没有任何片认领**；Handoff 首句「C-09 SC-B07 落地」范围宽于实际交付。影响：FEA-13 收尾时该强制增量可能静默丢失（跨片遗漏），且 closeout 措辞可能被读成 SC-B07 全量完成。 | 任务卡 `:29-35` out_of_scope 未列该项；`doc/reviews/FEA-13-scope-r1.md` §7 片 2–6 无一覆盖。 | DSH 把该项登记到明确片（或单列 Task）并在 Handoff/README/STATUS 中把本片措辞限定为「SC-B07 的写端/协商/adapter 子集」。 | open |
| R-004 | P3 | `src/infrastructure/sqlite/nmbak.py:1`（仍称 "backup package v1"）、`:22`、`:633-639` | 模块与 `_verify_package` docstring 仍只写 `BACKUP_CORRUPT`，而该方法现在经协商可抛 `BACKUP_FORMAT_UNSUPPORTED`；`_verify_package` 中 `int(...)` 已删，`try/except (TypeError, ValueError)` 对 `str()` 成为死代码。影响：文档性错误 + 死代码，易误导后续片。 | 读 `nmbak.py:633-639`；`git diff` 显示删除了 `format_version = int(...)`。 | 下一片（同文件写权）更新 docstring、删除死 `except`；或本片补一条注释级 errata 说明。 | open |
| R-005 | P3 | `src/infrastructure/sqlite/nmbak.py:68-80,614,622` | `_as_int` 接受字符串版本（探针：`version:"2"` 被接受并成功恢复），docstring 称「历史包为 `str`」但仓内**无任何此类历史包证据**（v1/v2 writer 均写 int）；v2 包内混入 `format_version` 也被忽略。影响：读端接受面宽于 D1 冻结字面值（无安全影响，摘要仍全量校验）。 | 探针 E1：`version:"2"` ACCEPTED。 | 要么给出历史包证据并在注释登记，要么把 v2 `version` 严格限定为 int（v1 保留宽松兼容）。 | open |
| R-006 | P3 | `src/infrastructure/sqlite/nmbak.py:612-627` | 已知 `format` 但**缺** `version`/`format_version`（或非标量）被归为 `BACKUP_FORMAT_UNSUPPORTED`；SC-B07 只规定 `version > 2` 为 unsupported（草案 `:139`），缺字段更接近结构损坏（`BACKUP_CORRUPT`）。影响：错误文案可能把「包损坏」误导为「App 太旧」。 | 探针 F1：`nmbak` 无 `version` → `BACKUP_FORMAT_UNSUPPORTED`。 | 区分「字段存在但值不支持」（→ unsupported）与「字段缺失/非标量」（→ corrupt），并补两例负测。 | open |
| R-007 | P3 | `tests/storage/test_nmbak_backup.py:109,131-139` | AC1 断言未覆盖每项 `size_bytes`、也未覆盖 `page_original_refs` 条目形状；同文件 `:131-133` 存在**恒真断言** `... .hexdigest() or True`（base 已有），使 `database_sha256` 检查形同虚设（且语义上把包字节 sha 与 DB sha 比较，本身方向错误）。影响：AC1 证据强度弱于声称（行为已由 reviewer manifest dump 验证）。 | 读测试与 manifest dump；`git show 1aad960b8:...` 证明 `or True` 为 base 已有。 | 后续在 allowed_paths 片内：断言 `refs[0]["size_bytes"]`、`page_original_refs[0]` 形状，删除恒真断言或改为断言 `database_sha256 == sha256(library.db 成员字节)`。 | open |
| R-008 | P3 | `tests/storage/test_nmbak_backup.py:109` | 测试名仍为 `test_create_package_contains_frozen_v1_layout`，断言内容已是 v2。影响：名称与语义不符，影响后续片检索/追溯。 | 读 `:109-139`。 | 重命名为 `..._v2_layout`（该文件在 allowed_paths）。 | open |
| R-009 | P3 | `tests/storage/test_nmbak_format.py:223-226`；`src/bootstrap/core_service.py:6981-6983` | AC3 的 `category=validation、retryable=false` 仅断言私有字典 `_BACKUP_ERROR_RULES`，无 wire envelope 端到端断言；`tests/core/test_core_backup_wire.py` 不在本片 allowed_paths，故属写域限制而非作者疏漏。已读映射消费点确认查表 + `("internal", False)` 兜底生效。 | 读 `core_service.py:6944-6995`。 | 集成阶段在 `test_core_backup_wire.py` 补一条「v3 包 → error.code/category/retryable」端到端用例。 | open |
| R-010 | P3 | `doc/design/SETTINGS_SECTION_C_SCHEMAS.md:108,138`；`doc/design/redesign-v1/00-facts/01_CAPABILITY_INVENTORY.md:376,378`；`src/bootstrap/core_service.py:6959-6962` | 写端改为 `nmbak`/`version:2` 后，旧设计文档仍写「恢复前必须 `manifest.format == "nm-backup"`」「错误码集不含新码」，代码注释的码表枚举也未含新码。影响：陈旧文档与实现不一致（历史设计文档，非冻结契约；本片 out_of_scope 禁止改）。 | grep 命中位置。 | DSH 登记文档对账项（FEA-13 后续片或 docs 专项），不在本片解冻写域。 | open |
| R-011 | P3 | `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`（`ac1882fc8..0cb4b80d5`） | in_review 文档提交改了 3 个不在本 Task `allowed_paths` 的治理指针文件（内容为 in_review 登记与计数重算，属 DSH 生命周期职责，无生产影响）。 | `git diff --name-only ac1882fc8..0cb4b80d5`。 | 在集成记录中显式登记「治理指针由 DSH 在 allowed_paths 之外维护」的口径，避免与写域违规混淆。 | open |
| R-012 | P3 | `doc/plan/FEA-CONTRACT-FROZEN-C09.md:103`（2×`0x08`）、`:106`（1×`0x0B`） | §9 errata 的 D1 行渲染为 `ackup/1`/`ackup/2`、D4 行渲染为 `erified=true`（`b`/`v` 被控制字符吃掉），冻结记录文本出现不可见控制字符。**base `1aad960b8` 已存在，非本 diff 引入**；冻结记录 append-only，且不在本片写域。 | 字节级扫描：line 103 = 0x08,0x08；line 106 = 0x0B。 | DSH 以追加 errata 注记更正（或以 ADJ 干净原文为准登记），并建议加一条「doc 控制字符」检查到治理脚本。 | open |

**计数：P0 = 0，P1 = 0，P2 = 3，P3 = 9。** 无 P0/P1；R-001/R-002 为证据形态问题（判别力已由 reviewer 复现），R-003 为拆分台账缺口，均不阻断集成，但应在 closeout 前处置或正式登记。

## 5. 门禁与复跑（全部在本环境实际执行）

| # | 场景 | 命令/步骤 | 结果 | EXIT | 证据 |
|---|---|---|---|---|---|
| G1 | 定向 pytest（任务卡指定 5 文件） | `python -m pytest tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_format.py tests/storage/test_backup_restore.py tests/core/test_core_backup_wire.py tests/infrastructure/test_nmbak_startup_backup.py -q` | **64 passed** | **0** | 本报告；与 `verification/.../logs/pytest-backup-suite.log` 一致（Python 3.14.6 / pytest 9.1.1） |
| G2 | 变异①：v2-version 分支→`BACKUP_CORRUPT` | `pytest tests/storage/test_nmbak_format.py -q` | **1 failed / 3 passed**（`assert 'BACKUP_CORRUPT' == 'BACKUP_FORMAT_UNSUPPORTED'`） | **1** | reviewer 实测；与 `logs/mutation-v3-corrupt.log` 一致 |
| G3 | 变异①复原 + 复绿 | `git checkout -- src/infrastructure/sqlite/nmbak.py`；`pytest tests/storage/test_nmbak_format.py tests/storage/test_nmbak_backup.py -q` | `git status` 干净；**25 passed** | **0** | reviewer 实测 |
| G4 | 变异②：写端 `version = 1` | `pytest tests/storage/test_nmbak_backup.py::test_create_package_contains_frozen_v1_layout -q` | **1 failed**（`BACKUP_CREATE_FAILED: read-back ... backup/2 version 1 is not supported`） | **1** | reviewer 实测；与 `logs/mutation-writer-version.log` 一致 |
| G5 | 变异②复原 + 复绿 | `git checkout -- ...`；两文件 pytest | `git status` 干净；**25 passed** | **0** | reviewer 实测 |
| G6 | 治理默认检查 | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)**（12 个非终态 Task；STATUS 2903B/29 行、PLAN 6769B/63 行达 80%） | **0** | 本报告 |
| G7 | 治理 `-TaskPath` | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-13-BK2-1.md` | **PASS (3 warnings)** | **0** | 本报告 |
| G8 | 证据 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **18/18 OK**（C09 `dc51226b336c` 未变） | **0** | 本报告 |
| G9 | EV sha256 核对 | `Get-FileHash` ×4 对 EV 表 | **4/4 MATCH**（README/`pytest-backup-suite.log`/`mutation-v3-corrupt.log`/`mutation-writer-version.log`） | **0** | 本报告 |
| G10 | diff ⊆ allowed_paths | `git diff --name-only 1aad960b8..ac1882fc8` 对 allowed_paths 模式 | **9/9 ALLOWED**，0 越界 | **0** | 本报告 |
| G11 | out_of_scope 零 diff | `git diff --name-only 1aad960b8..0cb4b80d5 -- doc/plan doc/contracts doc/reviews/FEA-13-scope-r1.md doc/reviews/ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT.md tests/core/test_core_backup_wire.py apps` | **空**（契约字节/pins/M2-C1/V11R 文档/其它片零 diff；`SqliteBackupService` 零 diff） | **0** | 本报告 |
| G12 | 真实 v1 包探针（审查者补充） | inline python：base `1aad960b8` writer 生成 v1 → 新读端 restore | 恢复成功；包 sha256+mtime 不变；无就地升级；无 `page_original_refs` 旧包亦成功 | **0** | 本报告（产物仅 `%TEMP%`，未入库 → R-001） |
| G13 | 边界探针 | `list` v3 包、截断 zip、`format_version:2`、`version:"2"`、缺 `version` | list 不抛（verified=false）；截断→`BACKUP_CORRUPT`；`fv2`→unsupported 且零副作用；`"2"` 被接受；缺 version→unsupported | **0** | 本报告（R-005/R-006） |

## 6. Architecture / Verification 结论

- **Architecture：PASS。** 协商前置于 `_verify_package`，`_verify_package` 前置于 `pre_restore` 创建（`nmbak.py:304-307`），拒绝路径结构上不可能产生副作用；写端只写 v2；v1 路径纯读；错误码在 wire 面被显式映射为 `validation`/非 `retryable`，未伪装成 `corrupt`；`core_service.py` 只加一行，无 handler/协议/依赖/schema 变化；`SqliteBackupService` 与 Host/UI 零改动。
- **Verification：PASS（带证据形态保留）。** G1–G11 全部由 reviewer 独立复跑/核对；G12–G13 补足 canonical 证据未覆盖的真实旧包与边界行为。两处变异均由 reviewer 亲手复现（EXIT 1）并复原（EXIT 0、工作树干净）。

## 7. 剩余风险与未验证项

1. **旧二进制读 v2 包**：以 base 源码复现为 `BACKUP_CORRUPT`（fail-closed，符合 Handoff 声明）；未用真实旧打包二进制验证，UI 会把「包更新」显示为「包损坏」——发布说明需登记（R-003 的措辞关联）。
2. **未跑全量**：`tests/storage` 全量与整套 .NET 未跑（Handoff 已如实声明）；本片零 C# 改动，但新错误码在 Host/UI 的呈现未端到端验证（R-009）。
3. **`list` 语义**：v3 包在 `backup.list` 中与损坏包同形（`backup_type:"unknown"`、`verified:false`），无「版本过新」区分；本片 AC 未要求，留给后续片/UI 决策。
4. **跨片写权**：`nmbak.py`/`core_service.py` 为多片共用单点，本片已冻结；R-004/R-005/R-006 的修正须在下一片同文件写权内完成，避免并行。
5. **文档对账**：R-010 的陈旧文档与 R-012 的冻结记录控制字符不在本片写域，须由 DSH 登记后续处置。

## 8. 结论与复审

- **decision：approved。** base `1aad960b8` → 实现 `ac1882fc8` → in_review `0cb4b80d5` 的交付可交 DSH 集成：AC1–AC6 全 MET，P0/P1 = 0，关键判别（两处变异、v1 只读、零副作用）已由 reviewer 独立复现。
- **放行条件（非阻断，closeout 前处置或登记）**：R-001（补 golden v1/无 `page_original_refs` 证据或固化探针）、R-002（重采 mutation 日志头/EXIT；统一 25/64 口径）、R-003（SC-B07 ④ 与源授权元数据入包的归属登记 + 措辞收窄）；P3 可在后续片或文档专项收敛。
- **复审**：若 DSH 修改上述 canonical 证据或代码，须以新 head 重新派发独立上下文复审；本报告只对 `reviewed_head 0cb4b80d5` 有效。
- 本审查未 push、未 commit、未改动生产代码/测试/契约；唯一写入文件为本报告。
