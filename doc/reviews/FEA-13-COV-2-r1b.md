---
task_id: FEA-13-COV-2
review_round: r1b
reviewer: DSH 派发的独立上下文子 agent（review session 见父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5` 下的 review 子会话；未参与本 Task 实现/返修）
reviewer_kind: subagent
author: DSH（Lead / Integrator；实现 `00f14179a`）
base_commit: 892cb99df
reviewed_head: 92e8f88b8
implementation_commit: 00f14179a
decision: changes_requested
---

# Review（r1b）：FEA-13-COV-2 覆盖清单二期

## 0. 审查者身份与方法（快速审查）

- **审查者来源**：DSH 派发的独立上下文子 agent，未参与本 Task 的设计、实现或返修；只读被审 head，唯一仓库写入为本报告。符合 2026-10-31 用户裁决的「上下文独立」口径。
- **被审对象**：base `892cb99df`；实现 `00f14179a`；被审 head `92e8f88b8`。
- **diff 范围**：`892cb99df..00f14179a` = 8 文件 / +621 行，全部落在任务卡 `allowed_paths` 内（`src/infrastructure/sqlite/nmbak.py`、`src/bootstrap/core_assembly.py`、`tests/storage/test_nmbak_coverage.py`、卡、`verification/FEA-13-COV-2/**`）。`92e8f88b8` 额外的 STATUS/PLAN/LEDGER/Handoff 属生命周期文档提交。
- **方法（限时，不重做变异、不跑全量）**：①`git diff --stat` + 逐文件读 diff/源码（`create`/`restore`/`_collect_extras`/`_copy_extras`/`_skipped_categories`/`_zip_directory`/`_verify_package`/`_extract_package`）；②核对生产侧目录生命周期（`DraftJournal`、`PluginService`、`Json*Store`）；③跑卡指定 2 文件 pytest；④`check.ps1 -TaskPath`；⑤EV 4×`Get-FileHash`；⑥`%TEMP%` 内只读探针（空 `drafts/`）复现 P1，探针不落仓库。
- **未运行**：`tests/storage` 全量、全量 .NET（零 C#）、真实 ACL 不可读目录、真实大体积 drafts/plugins、Host 侧 `deferred_categories` 消费。AC5 两例变异仅按日志核对（按指令不重做）。

## 1. 结论速览

- **verdict：`changes_requested`**。P0 = 0，**P1 = 1**，**P2 = 3**，P3 = 3。
- **阻断项 R-001（P1）**：`_skipped_categories` 把「类别根存在但 0 个成员」判成错误。而 `drafts/` 在 Core 启动时被 `DraftJournal` **无条件创建**（`src/infrastructure/filesystem/draft_journal.py:79`，并建空的 `receipts/`），因此**任何从未写过草稿的库（含全新安装）每次 `create()` 都会 `BACKUP_CREATE_FAILED`**；`restore()` 第一步就是 `create("pre_restore")`（`nmbak.py:347`），所以**restore 同样被阻断**。与卡 `doc/tasks/FEA-13-COV-2.md:48`「目录存在则入（空目录记 0 文件）」直接冲突。
- **AC 结论**：AC1 **PARTIAL**、AC2 **MET**、AC3 **MET**（带注）、AC4 **MET**、AC5 **MET**、AC6 **MET**。
- 与已存在的 r1 报告结论一致（`doc/reviews/FEA-13-COV-2-r1.md`：P1=1，changes_requested）；本报告独立复现并补充两类问题：运行中 `drafts/.lock/pid` 入包、AC3 测试未覆盖真实空/不可读路径。

## 2. Findings

### R-001（P1）空类别根 → 备份与 restore 全阻断

- 位置：`src/infrastructure/sqlite/nmbak.py:252-258`（create 内）、`:662-672`（`_skipped_categories`）、`:612-660`（`_collect_extras`）。
- 事实：
  - `drafts` 目录由 `DraftJournal.__init__` 在 Core 启动时 `mkdir`（并创建 `receipts/`、`.lock/`），即生产常态下**目录必定存在**；无草稿时 `rglob` 收集到 0 个文件 → 判定 skipped → `raise NmbakBackupError("BACKUP_CREATE_FAILED", ...)`。
  - `restore()` 在 `:347` 先 `create("pre_restore", ...)`，同一条路径立即失败 → 用户既不能备份也不能回滚。
  - 独立探针（临时目录，未落仓库）：`drafts/receipts` 为空时 `create("manual", ...)` →
    `RESULT: create FAILED code=BACKUP_CREATE_FAILED detail=required backup categories missing: drafts`。
  - 同类语义也覆盖 `plugins`（`PluginService` 只存路径、不主动建目录，风险低于 `drafts`）与 `settings`（`Json*Store` 仅在保存时 `mkdir`；目录存在但三 JSON 全无时同样失败）。
- 期望：类别根**存在但为空**应视为「0 文件入包」（`included_categories` 记该类别或按卡口径记空），只有**读取失败**（OSError/权限）才 `BACKUP_CREATE_FAILED`。卡 `:48-49`、`:54` 与 Handoff 的「为空/失败」措辞互相矛盾，需一并裁决。

### R-002（P2）运行中 journal 的 `drafts/.lock/pid` 被打进包

- `_collect_extras` 递归收集 `drafts/**` 的**所有文件**，包含 `draft_journal.py:134` 写入的 `.lock/pid`（活动进程 PID）。
- 后果：包内容随进程/运行状态变化（不可复现的成员）；未来片 4 若写回 extras，可能落一个陈旧 PID 锁。应在 `_collect_extras` 排除 journal 运行时内部件（`.lock/**`、临时文件）或明确记录为 known-internal。

### R-003（P2）卡口径与实现/Handoff 冲突（文档事实不一致）

- 卡 `:48-49`：`drafts`/`plugins`「目录存在则入（空目录记 0 文件）」；卡 `:54` 与 Handoff：「根存在但收集失败/为空 → `BACKUP_CREATE_FAILED`」。
- 代码与 Handoff 一致（空即失败），与 `:48-49` 相反。AC3/AC1 的验收语义因此不可判定；应更新卡（或改代码），二选一并留裁决。

### R-004（P2）AC3 测试未覆盖真实触发路径

- `test_uncollectable_category_fails_create_and_leaves_no_package` 用 `monkeypatch` 直接把 `_collect_extras` 换成 `raise OSError`，验证的是 `create()` 的 `except OSError → BACKUP_CREATE_FAILED` 包装（`:321-322`）与 finally 清理，**没有覆盖**：
  - 真实「类别根存在但不可读」的 `rglob`/`copyfile` 失败；
  - `_skipped_categories` 的空类别分支（正是 R-001 的触发点）。
- 因此 green suite 无法拦住 R-001。

## 3. AC 判定

| AC | 结论 | 依据 |
|---|---|---|
| AC1 类别入包 | **PARTIAL** | 四类均入包、每项 `sha256`+`size_bytes`、`included_categories` 与包内成员一致（`test_covered_categories_are_packaged_with_digest_and_size` 通过）；但「目录存在但空」被当作失败，违反卡 `:48` 的 0 文件语义（R-001/R-003） |
| AC2 排除项记录 | **MET** | `EXCLUDED_CATEGORIES` 四项均带 `reason`；catalog/derived 从不收集，测试断言包内无 `extras/catalog/`、`extras/derived/`；外部原文件/OS vault 无收集路径 |
| AC3 verified 语义 | **MET**（带注） | 收集抛出时 `create` 包成 `BACKUP_CREATE_FAILED` 且 finally 删 workdir/tmp，不产出包（`:319-329`）；正常路径 `create` 用 `_verify_package` 做 read-back 才置 `verified=true`（`:301-311`）；注：触发面过宽见 R-001，测试深度不足见 R-004 |
| AC4 restore 延迟写回 | **MET** | `restore` 只 `_restore_database` + `_restore_managed`，extras 不写回；report 含 `deferred_categories`（`:377-379`）；测试在改过 4 类 live 文件后断言 JSON 字节不变且 `deferred_categories` 为四类 |
| AC5 变异判别 | **MET**（按日志，未重做） | `mutation-extras-sha.log`（1 failed/3 passed）、`mutation-deferred.log`（1 failed/3 passed）、复原 4 passed；用例的「同长篡改」只改首字节，仅 sha256 能判别，size 校验无法命中，判别成立 |
| AC6 门禁 | **MET** | 定向 pytest 10 passed EXIT=0；`check.ps1 -TaskPath` PASS（3 warnings）EXIT=0；实现提交 diff ⊆ `allowed_paths`；pins 18/18 由门禁脚本覆盖（本次未单独跑 `verify_pins`） |

`data_root` 一致性：默认 `backup_root.parent`（`:178`），`core_assembly` 显式传 `data_root`（`:1929`），且 `backup_root = data_root/"backups"`（`:1923`）→ 默认推断与显式传入同值，**一致**。

## 4. 门禁与证据复核

| 项 | 命令 | 结果 |
|---|---|---|
| EV 4 | `Get-FileHash -Algorithm SHA256` | **4/4 与卡内表一致**：README `a807a751…2cc87`、pytest-backup-suite `47579996…72896`、mutation-extras-sha `d0e681e6…26830`、mutation-deferred `ee09dc10…d4c8e` |
| G1 | `python -m pytest tests/storage/test_nmbak_coverage.py tests/storage/test_nmbak_format.py -q` | `10 passed in 1.62s`，**EXIT=0** |
| G2 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-13-COV-2.md` | `Governance check: PASS (3 warnings)`，**EXIT=0**；Task 内 6 条 AC 仍标 `<<MET>>`，与 R-001 冲突，需随返修更新 |

### 4.1 审查期间的未提交返修（不属于被审 head）

- 本报告写入前后（约 21:12）工作区出现**未提交**改动：`M src/infrastructure/sqlite/nmbak.py`（+62/−25 左右）与 `M tests/storage/test_nmbak_coverage.py`（+86，新增 4 例）。该补丁移除 `_skipped_categories` 的失败语义、改为 `included_categories` + `empty_categories`（R-001）、跳过 `.lock/**` 与 `*.tmp`（R-002）、未知 extras 类别改为 `BACKUP_FORMAT_UNSUPPORTED`、新增类别声明一致性校验（R-007）。
- **本审查不采信该补丁**：被审对象是提交 `00f14179a`/head `92e8f88b8`；pytest（10 passed）跑于工作区变脏之前，收集数为提交态 4 例（若含新增 4 例应为 14），故门禁证据对应被审 head。返修须提交后再走 r2 独立审查。

## 5. 其余观察（P3）

1. `_verify_package` 对每个 extras 成员 `archive.read(member)` 全量读入内存（`:860`），`create` 的 read-back 又会跑一遍；drafts/plugins 体积无上限（卡已把大小策略推给片 5），大目录会内存/耗时双爆。建议流式 hash。
2. `restore` 用 `archive.extractall` 解出**整个**包（含不会被写回的 extras），大 drafts/plugins 会翻倍占用 temp 空间与 I/O。
3. `BACKUP_CORRUPT` 的「缺失 extras 成员」「未知 extras 成员」两条分支无测试，仅 sha 不匹配有覆盖。
4. `_collect_extras` 无符号链接防护（云盘/嵌套软链目录）；`skipped_categories` 在成功 manifest 中恒为空，属预留字段，可接受。

## 6. 处置建议

- **返修（必须）**：R-001 —— 空类别根按 0 文件入包，仅读取失败才 `BACKUP_CREATE_FAILED`；同步补一条「空 `drafts/`（含 `receipts/`、`.lock/pid`）仍能成功 create，且 `restore()` 的 pre_restore 不受阻」的测试（顺带闭合 R-004）。
- **建议同批处理**：R-002（排除 journal 运行时件）、R-003（卡/Handoff 措辞裁决）。
- 返修后需重跑 6 文件备份面 pytest 与 `check.ps1`，更新 EV 与 AC 表；P3 可留片 4/片 5。
- 本报告只写文档，未改生产源码/测试/契约，未 commit、未 push。
