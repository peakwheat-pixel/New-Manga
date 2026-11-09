---
task_id: FEA-13-COV-2
reviewer: 独立子代理（DSH 派发，独立上下文；DSH session `f8d29aa2-8c04-4e87-b4a0-b6d06d710472`；父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`）
reviewer_kind: subagent
author: dsh
base_commit: 892cb99df
reviewed_head: f861057078d3c3c5c7af395e934211bda3713959
decision: approved
---

# Review r2：FEA-13-COV-2（覆盖清单二期）

- 审查轮次：r2（复审 r1 / r1b 的处置提交）
- 被审 head：`f861057078d3c3c5c7af395e934211bda3713959`（`f86105707`），父提交 `92e8f88b8`
- 审查者来源：独立子代理，未参与本 Task 的实现与返修；只读被审 head（工作区只写本报告）
- 范围：`git diff 92e8f88b8..f86105707`（11 文件，+481/−66），对照卡 `doc/tasks/FEA-13-COV-2.md` §Review 处置 R-001…R-008、`doc/reviews/FEA-13-COV-2-r1.md`、`-r1b.md`、`-sc01-decision.md`、Handoff 与 `verification/FEA-13-COV-2/**`
- 方法：逐文件读 diff + 相关源码/测试；按 §Review 处置逐条核实；复跑定向 pytest、6 文件备份面 pytest、`check.ps1`（默认 + `-TaskPath`）、`verify_pins`、`task_ledger.py` 只读复算；在 `%TEMP%` 写**仓外一次性探针**（不入仓）验证空目录 create/restore 与符号链接边界；核对 4 份 EV 的 sha256

## 1. 结论摘要

- **verdict：`approved`**（可交 DSH 集成验证）。**无新增 P0/P1**。
- **FIXED = 5**（R-001/R-002/R-003/R-006/R-007）；**PARTIAL = 3**（R-004/R-005/R-008）；**OPEN = 0**。
- 前序唯一 P1（R-001 空目录阻断 create/restore/pre-migration）**已消除**，并有提交测试 + 独立探针双证。
- 3 项 PARTIAL 均为 P3 级：均不阻断 AC，但其中 2 项涉及证据/文档口径的准确性（N-001、N-002），建议 DSH 在 closeout 时一并登记或顺手修正。

## 2. R-001…R-008 逐条判定

| ID | r1/r1b 级别 | 卡处置主张 | r2 判定 | 依据（被审 head 事实） |
|---|---|---|---|---|
| R-001 | P1 | 删除「空目录=缺失」；`_present_categories` 记录存在的类别根，空根入 `included_categories` + `empty_categories`；仅真实收集错误才 `BACKUP_CREATE_FAILED` | **FIXED** | 代码：`nmbak.py:251-257`（不再有 skipped→raise）、`:673-683`（`_present_categories` 按 `is_dir()` 记录，`trash-manifest` 按 `is_file()`）、`:281-287`（`empty_categories = present − extras`）、OSError 仍由 `:323-326` 包成 `BACKUP_CREATE_FAILED`。测试：`tests/storage/test_nmbak_coverage.py:232-250`（空 drafts/plugins → 成功、`skipped=[]`）。独立探针（`%TEMP%` 仓外）：空 `drafts/receipts/` + 空 `plugins/` → `create` 成功且 `verified=true`，`included=[drafts,plugins,settings,trash-manifest]`、`empty=[drafts,plugins]`、`skipped=[]`；随后 `restore()`（含 `pre_restore` 自备份）成功、JSON 字节不变。**未提交测试缺口**：没有「空 drafts + restore 的 pre_restore 不受阻」专门用例（r1b 建议项），本审查以探针代证，列残余。 |
| R-002 | P2 | 跳过 `.lock/` 与 `*.tmp`，测试断言包内无 | **FIXED** | `nmbak.py:636-642`（`relative.parts` 含 `.lock` 跳过；`*.tmp` 跳过）；测试 `:253-265` 断言包内无 `.lock`/`.tmp` 且 `drafts` 仍在 `included_categories`。行为与探针一致。 |
| R-003 | P2 | 覆盖空目录成功路径 + 类别声明不一致 + 未知类别前向兼容；monkeypatch 失败用例保留 | **FIXED** | 4 例均提交：空目录 `:232-250`、`.lock`/`.tmp` `:253-265`、声明不一致 → `BACKUP_CORRUPT` `:268-279`、未知 extras 类别 → `BACKUP_FORMAT_UNSUPPORTED` `:282-301`；monkeypatch 失败用例 `:136-147` 保留。卡处置范围已覆盖。残余：真实 ACL 不可读根、空 settings 负例、缺失/多余 extras 成员中的部分分支仍无测试（卡已登记 UNKNOWN）。 |
| R-004 | P2 | 已裁决：本片不实现，单列 `FEA-13-SRC-6`（proposed），不改契约；卡 `out_of_scope` 登记 | **PARTIAL** | 裁决实质已完成：`sc01-decision.md:9-13`（不实现、单列 `FEA-13-SRC-6`、不新增 C-09 errata）、卡 `:29-35` `out_of_scope` 已登记。但裁决文件 `:14` 声称「BK2-1 卡内 R-003 处置表的『④ 归片 2』措辞**已收窄**为『独立裁决』」——`doc/tasks/FEA-13-BK2-1.md:95` 现文仍为「④ 与 SC-B01 源授权元数据入包归片 2（`FEA-13-COV-2`）/独立裁决」，**该同步未发生**（本 head diff 未含 BK2-1 卡）。见新增 N-001。 |
| R-005 | P3 | 口径统一为「空目录=合法 0 文件，仅收集错误失败」；补**真实**「restore 写回 extras」变异日志 | **PARTIAL** | 口径统一：Handoff `:18`、README「空目录语义（R-001 修复）」与卡 `:48/:62` 一致，**已修**。但新 AC5② 日志并非「真实写回 extras」：`logs/mutation-writeback.log:54-55` 的失败快照为 `after == b'{"restored":true}'`，真实 extras 写回应等于包内字节（fixture 为 `{"format_version":1,"profiles":[]}`），说明变异是向 settings 路径写**固定标记**，只能证明 AC4 断言能发现「任意写入」，不能证明它判别「extras 原字节写回」；且日志未记录变异 diff，`# time`（`:3`）与 `pytest-backup-suite.log:3` 的 7 位小数完全相同（可解释为批次时间戳，但不可独立复核）。①（sha 变异）仍为决定性判别，AC5 不因此失败。 |
| R-006 | P3 | 重跑 `task_ledger.py --write` | **FIXED** | `python tools/governance/task_ledger.py` 只读复算：`task files 562 (tracked 562, untracked 0)`、`non-terminal 12 (tracked 12)`、by status（done 468 / closed_with_limitations 44 / cancelled 18 / historical 11 / superseded 8 / proposed 5 / in_review 3 / blocked 2 / (none) 1 / approved 1 / ready 1）与 `doc/TASK_LEDGER.md:9-32` 逐项一致，EXIT=0。 |
| R-007 | P3 | `_verify_package` 断言 `included == extras ∪ empty`、`skipped` 为空；未知 extras 类别 → `BACKUP_FORMAT_UNSUPPORTED` | **FIXED** | `nmbak.py:893-916`（双向集合校验 + `skipped_categories` 非空即 `BACKUP_CORRUPT`，且 `declared_included is None` 时跳过以兼容旧包）、`:855-858`（未知类别 → `BACKUP_FORMAT_UNSUPPORTED`）；测试 `:268-279`、`:282-301` 覆盖两条路径。`create` 的 read-back（`:305-314`）复用同一校验，正常包不被误伤（探针 `create_ok=true`）。 |
| R-008 | P3 | `_collect_extras` 跳过 `is_symlink()`；真实 ACL/符号链接回归列残余 | **PARTIAL** | 文件符号链接**已跳过**（`nmbak.py:644`；探针：`drafts/sym.txt` 不收集）。但 Windows **目录 junction/reparse point 未被拦截**：探针 `mklink /J data/plugins/junction → 仓外目录` 后，`_collect_extras` 仍返回 `("plugins", "junction/leak.txt")`（`Path.is_symlink()` 对 junction 为 False，`rglob` 进入），外部内容仍可被打入包，与 `:643` 注释「never follow links out of the category root」及「外部原文件不入包」边界不符。见新增 N-002；卡已如实登记「符号链接回归 UNKNOWN」。 |

## 3. 新增 findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| N-001 | P3（文档/治理准确性） | `doc/reviews/FEA-13-COV-2-sc01-decision.md:14`；`doc/tasks/FEA-13-BK2-1.md:95` | 裁决文件声称 BK2-1 卡措辞「已收窄为『独立裁决』」，但 BK2-1 卡仍写「④ … 归片 2（`FEA-13-COV-2`）/独立裁决」；追踪 R-004 处置时会读到互相矛盾的来源。 | 逐行对照两文件；本 head diff 未包含 BK2-1 卡修改。 | closeout 时把 BK2-1 `:95` 改为「④ 不在 6 片拆分内，独立裁决（见 `FEA-13-COV-2-sc01-decision.md`）」，或修正裁决文件 `:14` 的既成事实表述。 | open |
| N-002 | P3（安全边界） | `src/infrastructure/sqlite/nmbak.py:635-646` | `path.is_symlink()` 不能识别 Windows junction/mount point；`rglob` 会进入 junction 目录，把 data root 之外的普通文件收入 `drafts`/`plugins` extras（包体污染、可把外部内容带进备份）。 | 仓外探针：`junction_islink=false`；`collects_junction_children=[["plugins","junction/leak.txt"]]`；文件 symlink 用例被正确跳过。 | extras 收集改用「路径 resolve 后必须仍在 `data_root/<category>` 内」的词法+realpath 校验（与 managed 侧 `_resolve_within` 一致），或识别 reparse point；补 junction/symlink 负测（可在 `%TEMP%` 构造 junction，无需管理员权限）。 | open |

## 4. AC 判定

| AC | 结论 | 依据 |
|---|---|---|
| AC1 类别入包（含空目录） | **MET** | 探针 + 测试证明四类入包、空根记 0 文件且计入 `included_categories`/`empty_categories`；`extras` 每项含 sha256+size。 |
| AC2 排除项记录 | **MET** | 未改动路径保持原样；测试 `:128-133` 断言 excluded 四项有 reason 且 catalog/derived 不入包。 |
| AC3 verified 语义 | **MET** | 收集/读取错误 → `BACKUP_CREATE_FAILED` 且无包（`nmbak.py:323-333`、测试 `:136-147`）；空目录不失败（探针）；read-back 含 extras sha/size 与类别交叉校验（`:893-916`）。 |
| AC4 restore 延迟写回 | **MET** | 探针：restore 后所有 JSON 字节不变、`deferred_categories=["settings","trash-manifest"]`（= 实际入包类别，空类别正确地不声明写回）；测试 `:174-191` 覆盖四类非空场景。卡 `:56` 口径「实际入包且延迟写回」一致；AC4 括注「与 `included_categories` 对应」在空类别场景下语义偏松，建议后续措辞对齐（观察项，非 finding）。 |
| AC5 变异判别 | **MET**（① 决定性；② 证据弱） | 卡允许「择一或全部」；① 的 tampered-sha 日志仍有效（sha 路径本 r2 未改），② 日志判别力弱见 R-005。 |
| AC6 门禁 | **MET** | 见 §5：pytest 35/74 passed、`check.ps1` 默认与 `-TaskPath` PASS、pins 18/18、diff 11 文件（仅 `doc/TASK_LEDGER.md` 在 `allowed_paths` 之外，属 DSH 生命周期写；按 BK2-1 R-011 先例不计越界）。 |

## 5. 验证与门禁（本审查实际执行）

| # | 命令 / 步骤 | 结果 | EXIT |
|---|---|---|---|
| T1 | `python -m pytest tests/storage/test_nmbak_coverage.py tests/storage/test_nmbak_format.py tests/storage/test_nmbak_backup.py -q` | `35 passed in 5.15s` | **0** |
| T2 | `python -m pytest tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_format.py tests/storage/test_nmbak_coverage.py tests/storage/test_backup_restore.py tests/core/test_core_backup_wire.py tests/infrastructure/test_nmbak_startup_backup.py -q` | `74 passed in 8.96s`（与 EV-COV-SUITE 计数一致） | **0** |
| T3 | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)` | **0** |
| T4 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-13-COV-2.md` | `Governance check: PASS (3 warnings)` | **0** |
| T5 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)` | **0** |
| T6 | `python tools/governance/task_ledger.py`（只读复算） | 562 tracked / 0 untracked / 12 non-terminal；与 `doc/TASK_LEDGER.md:9-32` 一致 | **0** |
| T7 | EV 4 份 `Get-FileHash -Algorithm SHA256` | 4/4 与卡 `:76-79` 一致（见 §6） | **0** |
| T8 | 仓外探针（`%TEMP%`，不入仓）：空 drafts/receipts + 空 plugins → create/restore；`mklink /J` junction + 文件 symlink | `create_ok=true`、`empty=[drafts,plugins]`、`skipped=[]`、restore 成功且 JSON 字节不变；junction 逃逸、文件 symlink 被跳过（见 §3 N-002） | **0** |
| T9 | `git status --short`（本报告写入前） | 干净（无输出） | — |

## 6. EV 校验（当前字节 vs 卡内 pin）

| evidence_id | 卡内 sha256 | 实测 | 结论 |
|---|---|---|---|
| EV-COV-README | `3c6997cb…06b594a` | `3C6997CB…06B594A` | 一致 |
| EV-COV-SUITE | `9749fb42…bd27e51` | `9749FB42…BD27E51` | 一致 |
| EV-COV-MUT-SHA | `d0e681e6…09926830` | `D0E681E6…09926830` | 一致 |
| EV-COV-MUT-WRITEBACK | `96258775…b0516cbd` | `96258775…B0516CBD` | 一致 |

## 7. 残余风险与待办（不阻断）

1. **R-005/N-001 证据与文档口径**：AC5② 日志不是真实 extras 原字节写回，且缺变异 diff；`sc01-decision:14` 对 BK2-1 的「已收窄」不成立。建议 closeout 前后任选其一修正（改日志标注或改 BK2-1 卡/裁决文字）。AC5 由 ① 支撑，不受影响。
2. **R-008/N-002**：junction/reparse point 仍可把外部内容带入 extras；建议片 4（写回语义）落地前修复，或在卡残余中明确 junction 边界。
3. **测试缺口**：空 `drafts` + `restore()`（pre_restore）专门用例、空 settings 负例、真实不可读根、junction 负测（可用 `mklink /J` 稳定构造）；符号链接/ACL 已在卡登记 UNKNOWN。
4. **证据批次**：`mutation-extras-sha.log` 仍为 r1 前批次 `fea-13-cov-2`（20:48），r2 未重采；sha 校验路径本 r2 未改，计数与代码仍可复现，建议片 4 重采时统一批次头。
5. **生命周期**：卡 `reviewer:` 字段仍为「待指派」、`delivery_head` 仍为 `00f14179a`，`Closeout Record` 未填；由 DSH 在 r2 批准后按流程更新（本审查只写本报告，未改卡）。
6. **性能/IO**：`_verify_package` 逐成员全量 `archive.read`、restore `extractall` 解出永不写回的 extras（r1 P3 观察）未变，归片 5。
7. **旧包兼容**：v1/v2 无 `included_categories` 时交叉校验跳过（`nmbak.py:893-894`），保持兼容；建议后续补 base-writer/旧包 golden（BK2-1 残余）。

## 8. 结论

- **Architecture**：extras 收集/校验集中在 `NmbakBackupService`，未改契约字节与 18 pins，分层与写域边界未变；空目录语义与真实错误语义已分离，`verified` 仍由 read-back 决定。
- **Verification**：定向与备份面 pytest、两道 `check.ps1`、`verify_pins`、ledger 复算、4 份 EV、独立探针全部为预期结果；无 EXIT≠0。
- **decision：`approved`**。无 P0/P1、无 OPEN 项；3 项 P3 PARTIAL（R-004/R-005/R-008）与 2 项新增 P3（N-001/N-002）登记为残余，可由 DSH 在集成/closeout 时处置。本报告只写本文件，未改生产源码/测试/契约，未 commit、未 push。
