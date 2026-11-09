---
task_id: FEA-13-COV-2
reviewer: DSH 派发的独立上下文子 agent（review session `2e5eec27-39e1-4b70-84b1-199bca898b24`；父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`；未参与本 Task 实现/返修）
reviewer_kind: subagent
author: DSH（Lead / Integrator；实现 `00f14179a`、文档/指针 `1ec37271f`/`92e8f88b8`）
base_commit: 892cb99df
reviewed_head: 92e8f88b8
decision: changes_requested
---

# Review（r1）：FEA-13-COV-2 覆盖清单二期

## 0. 审查者身份、范围与方法

- **审查者来源**：DSH 派发的独立上下文子 agent（`subagent`，review session `2e5eec27-39e1-4b70-84b1-199bca898b24`），未参与本 Task 的设计、实现或返修；只读被审 head，唯一仓库写入为本报告。符合 2026-10-31 用户裁决的「上下文独立」口径。
- **被审对象**：base `892cb99df`；实现 `00f14179a`；文档/指针 `1ec37271f`、`92e8f88b8`（被审 head）。分支 `main`；审查开始与代码复核结束时 `git status --porcelain` 为空（本报告写入前）。
- **diff 范围**：实现提交 `892cb99df..00f14179a` 共 **8 个文件、+621 行**：`src/infrastructure/sqlite/nmbak.py`、`src/bootstrap/core_assembly.py`、`tests/storage/test_nmbak_coverage.py`（新增）、`doc/tasks/FEA-13-COV-2.md`、`verification/FEA-13-COV-2/**`（README + 3 logs）。`892cb99df..92e8f88b8` 另含 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` 与 Handoff（生命周期文档）。
- **方法**：①逐文件 diff 核对实现与卡/裁决口径；②复跑卡指定 6 文件 pytest；③独立变异（禁用 extras sha 校验；以及补充的「restore 写回 extras」真变异）并还原；④三项治理门禁；⑤4 个 EV sha256 复核；⑥边界与 `out_of_scope` 零 diff 检查；⑦`%TEMP%` 内只读探针：空目录类别、运行中 journal 的 `.lock`、缺省/显式 `data_root`、v8→v9 升级路径（探针脚本不落仓库，用后删除）。
- **未审/未运行**：`tests/storage` 全量、全量 .NET（本片零 C#）、真实 Windows ACL「不可读目录」、真实用户 profile 的升级（探针是合成 v8 库）、Host 侧 wire 消费 `deferred_categories`、真实大体积 drafts/plugins。

## 1. 结论速览

- **verdict：`changes_requested`**。P0 = 0，**P1 = 1**，P2 = 3，P3 = 4。
- **阻断项 R-001（P1）**：`_skipped_categories` 把「目录存在但 0 文件」当作错误，导致**任何空 `drafts/`（生产启动后正常存在的目录）或空 `plugins/` 会让 `create()` 抛 `BACKUP_CREATE_FAILED`**。独立探针证明：正常干净关机后的 `drafts/` 只有空 `receipts/`；下一次有 pending migration 的启动会在 `_NmbakMigrationBackup`（pre-migration 备份）处失败，**升级被阻断**，且该异常不是 `MigrationError`、`assemble_core_services` 不会包装，直接失败。该行为与任务卡 `:48`「空目录记 0 文件」直接冲突。
- **AC 结论**：AC1 **PARTIAL**、AC2 **MET**、AC3 **PARTIAL**、AC4 **MET**、AC5 **MET**、AC6 **MET**（详见 §3）。
- 其余 P2：运行中 journal 的 `.lock/pid` 被打进包；AC3 测试未覆盖真正触发 `_skipped_categories` 的空/不可读路径；BK2-1 R-003 移交给本片的 SC-B01 源授权元数据未落实也未裁决。

## 2. 重点核实（口径与独立探针）

### 2.1 extras 四类入包与 0 文件语义

- 非空场景正确：探针（显式与缺省 `data_root` 各一次）与 `test_covered_categories_are_packaged_with_digest_and_size` 一致，包内为 `extras/{settings, drafts, plugins, trash-manifest}/...`，manifest 每项含 `sha256`+`size_bytes`，`included_categories` 排序正确；`extras_total_bytes` 与包内字节一致。
- **空目录场景错误**（R-001）：探针输出
  - `[A empty drafts (explicit data_root)] BACKUP_CREATE_FAILED: required backup categories missing: drafts`
  - `[A empty drafts (default parent inference)] BACKUP_CREATE_FAILED: required backup categories missing: drafts`
  - `[C empty plugins] BACKUP_CREATE_FAILED: required backup categories missing: plugins`
  - `[D absent drafts/plugins] OK ... included_categories: ['settings','trash-manifest']; skipped_categories: []`
- 真实启动链证明空 `drafts/` 不是异常状态：`core_assembly.py:1606` 每次启动构造 `DraftJournal(Path(db_path).parent / "drafts")`；`draft_journal.py:79-82` 创建 `drafts/` 与 `drafts/receipts/`，`close()`（`:154-175`）只删 `.lock`，不删根目录。干净关机后 `drafts/` 仍在、且没有文件。
- **升级路径实测**：合成 v8 库 → 执行一次 `DraftJournal` 创建并 `close()`（模拟干净关机）→ 用与 `_NmbakMigrationBackup` 相同接线（`backup_root = db_path.parent/"backups"`，不传 `data_root`）的 provider 跑 v8→v9：实测 `UPGRADE: NmbakBackupError BACKUP_CREATE_FAILED | required backup categories missing: drafts`，`schema after attempt: 8`，`packages: []`。`migrator.py:165-172` 不捕获 provider 异常；`core_assembly.py:1182-1193` 只捕获 `MigrationError`，故该异常会直接终止装配。

### 2.2 运行中 journal 的 `.lock/pid` 被入包

- 探针在 `DraftJournal` 打开期间执行 `create()`：`[B running journal] drafts members: ['extras/drafts/.lock/pid']`，`included_categories` 仍含 `drafts`。也就是说，正常运行时 `drafts` 类别**只是靠内部锁文件**才非空；这不仅把瞬态进程状态放进包，还会在未来片 4 写回 extras 时把过期 `.lock` 恢复到活 journal，存在 `DRAFT_JOURNAL_LOCKED` 风险（R-002）。

### 2.3 排除项与 `verified`

- `catalog/`、`derived/` 在 data_root 内但不在 extras 收集范围；包内无 `extras/catalog/**`、`extras/derived/**`；`excluded_categories` 四项均带 reason；测试断言与代码一致。外部原文件/OS vault 按定义不可达（静态记录）。
- `verified=true` 只在 read-back `_verify_package` 通过后写入（`nmbak.py:301-311`），extras 的 sha/size/未知成员在 `_verify_package` 内校验（`:839-879`）；但「正常空目录」状态无法产出包，故正常语义不完整（AC3 PARTIAL）。

### 2.4 restore 延迟写回

- 代码只写回 `managed/`（`_restore_managed`），extras 仅解到临时目录并在 finally 删除；report 无条件带 `deferred_categories`（`:377-379`）。
- 测试 `test_restore_defers_extras_and_leaves_them_byte_identical` 通过：4 类 JSON 字节不变，`deferred_categories` 为 4 类。
- **独立真变异**（非证据日志中的弱变异）：在 `restore` 中临时加入「把 extras 写回 data_root」后，AC4 用例 **1 failed / 3 passed（EXIT=1）**；`git checkout` 还原后 **4 passed（EXIT=0）**，文件 sha256 与变异前一致。说明 AC4 断言确有判别力；证据日志里的「deferred_categories 清空」只是报告断言，不是卡 AC5② 的字面变异（R-005）。

### 2.5 extras sha256 校验与同长篡改

- `_verify_package` 对每个 extras 成员同时校验 sha256 与 size；同长篡改只能由 sha 抓住（测试 `:194-210` 正是同长改字节）。
- **独立变异**：把 `if hashlib.sha256(extra_bytes)...` 改为 `if False and ...` 后，`tests/storage/test_nmbak_coverage.py` 实测 **1 failed / 3 passed（EXIT=1）**，失败点正是 `test_tampered_extras_member_is_corrupt`；`git checkout -- src/infrastructure/sqlite/nmbak.py` 后 **4 passed（EXIT=0）**，sha256 回到 `A14EB62D0DEA082BABE75654EB529A8E1D2CFDA863554B09CFBA008B8B0B69DE`，工作树干净。

### 2.6 `data_root` 缺省推断与显式传入

- `nmbak.py:178-180` 缺省 `backup_root.parent`；`core_assembly.py:1813` 的 `data_root = Path(db_path).parent`，主装配 `:1921-1930` 显式传 `data_root`；迁移钩子 `:1174-1179` 用 `Path(db_path).parent / "backups"`，缺省推断得到同一根。探针 E 证明显式/缺省两次创建的 extras 成员集合完全相同（`[E] same extras member set: True`）。**一致，无 finding**。但迁移钩子未显式传 `data_root`，可读性上建议后续顺手对齐（非阻断）。

### 2.7 边界、EV 与 out_of_scope

- `git diff --name-only 892cb99df..00f14179a` = 8 文件，**8/8 ⊆ allowed_paths**。
- `doc/contracts`、`doc/plan`、`tools`、`apps`、`src/bootstrap/core_service.py`、`src/application/maintenance` 在 `892cb99df..92e8f88b8` **零 diff**；未实现 merge restore/写回/DatabaseId/调度，未改契约字节或 pins。
- head 范围比实现提交多出 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、Handoff；按 BK2-1 R-011 的既有先例属 DSH 生命周期写入，不单独计为越界（其计数漂移另见 R-006）。
- 4 个 EV sha256 与当前字节 **4/4 MATCH**（大小写不敏感比较）：
  - README `a807a751…542cc87`；pytest log `47579996…3972896`；mutation-extras-sha `d0e681e6…9926830`；mutation-deferred `ee09dc10…ad4d5c`。
- `git log`：`892cb99df` → `00f14179a` → `1ec37271f` → `92e8f88b8`（无额外实现提交夹带）。

## 3. AC 逐项判定

| AC | 判定 | 证据与说明 |
|---|---|---|
| **AC1 类别入包** | **PARTIAL** | 非空四类入包、每项 sha256+size、`included_categories` 与成员一致（测试 + 探针 B/E 通过）。但卡 `:48` 的「空目录记 0 文件」未实现：空 `drafts`/`plugins` 直接失败（R-001 探针 A/C），且 0 文件类别无法进入 `included_categories`。 |
| **AC2 排除项记录** | **MET** | 包内无 `catalog/**`、`derived/**`；`excluded_categories` 四项均带 reason（`nmbak.py:84-95`；测试 `:127-133`）。外部原文件/OS vault 按定义不在收集范围。 |
| **AC3 verified 语义** | **PARTIAL** | 收集抛错 → `BACKUP_CREATE_FAILED` 且无包（测试 `:136-147`；实现 `:251-258`、通用 `OSError` 包装 `:321-322`）；read-back 通过才 `verified=true`。但「正常空目录」被误判为失败，正常状态下无法产出 verified 包；且测试 monkeypatch 绕过了 `_skipped_categories` 路径（R-003）。 |
| **AC4 restore 延迟写回** | **MET** | 测试 `:150-191` 通过；独立「写回 extras」真变异使该用例 RED（EXIT=1），还原后绿（EXIT=0）；report `deferred_categories` 四类（`:377-379`）。 |
| **AC5 变异判别** | **MET** | 卡允许「择一或全部」；① 禁用 extras sha 校验后 tampered 用例 RED（独立复现：1 failed/3 passed，EXIT=1），还原后 4 passed（EXIT=0）。证据中的②是 `deferred_categories` 清空而非卡面「restore 写回 extras」，属证据口径问题（R-005），不改变本 AC 判定。 |
| **AC6 门禁** | **MET** | 6 文件 pytest 70 passed（EXIT=0）；`check.ps1` 默认与 `-TaskPath` 均 PASS（EXIT=0）；pins 18/18（EXIT=0）；diff 8/8 允许；EV 4/4。 |

## 4. Findings

| ID | 级别 | 文件:行 | 问题 | 依据/复现 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| **R-001** | **P1** | `src/infrastructure/sqlite/nmbak.py:251-258`、`:662-672`；`src/infrastructure/filesystem/draft_journal.py:79-82`、`close()` `:154-175`；`src/bootstrap/core_assembly.py:1183,1606,1174-1179` | `_skipped_categories` 把「目录存在但收集到 0 个文件」归为 `skipped`，`create()` 抛 `BACKUP_CREATE_FAILED`。生产每次启动都会创建 `<data_root>/drafts`（含空 `receipts/`），干净关机后仍为空目录；下一次 pending migration 的 pre-migration 备份因此失败，升级启动被阻断。空 `plugins/` 同理。与任务卡 `doc/tasks/FEA-13-COV-2.md:48`「空目录记 0 文件」及 `:54`「收集失败」的语义直接冲突；Handoff `doc/handoffs/FEA-13-COV-2-00f14179a.md:18` 写成「为空/失败」反而固化了错误口径。 | 独立探针：空 drafts → `BACKUP_CREATE_FAILED: required backup categories missing: drafts`；合成 v8 库 + 干净关机 drafts + 同生产接线 provider 跑 v8→v9 → 同一错误，`schema after attempt: 8`、`packages: []`（`migrator.py:165-172` 不捕获、`core_assembly.py:1182-1193` 只捕获 `MigrationError`）。 | ① 删除「空目录=错误」判定：`skipped_categories` 只应由真实收集错误产生（或移除该字段）；② 存在的类别即使 0 文件也计入 `included_categories`（可加 `extras_count` 辅助）；③ 收集时排除 `drafts/.lock/**`（见 R-002）；④ 补测试：空 `drafts`/`plugins`、真实 `DraftJournal` 开/关后的根、v8→v9 pre-migration 备份、空 settings；⑤ 修复前不得 approve。 | open |
| **R-002** | **P2** | `src/infrastructure/sqlite/nmbak.py:628-638`；`src/infrastructure/filesystem/draft_journal.py:103-134` | 运行中 `DraftJournal` 的 `.lock/pid` 被 `drafts/**` 递归收入包（`extras/drafts/.lock/pid`），manifest 将 `drafts` 记为已入包。包内出现瞬态锁/进程状态；未来片 4 若按 extras 写回，可能恢复过期锁，导致 journal `DRAFT_JOURNAL_LOCKED`/fail-closed。 | 探针 B：`drafts members: ['extras/drafts/.lock/pid']`，`included_categories` 含 `drafts`；实测 create 成功并打包。 | 收集时排除 drafts 根下的 `.lock/`（及 `.tmp`/临时文件）；明确 `receipts/**` 是否属于应入包数据并加断言；在片的 README/卡内记录排除规则。 | open |
| **R-003** | **P2** | `tests/storage/test_nmbak_coverage.py:136-147`、`:62-70` | AC3 的失败分支测试用 `monkeypatch.setattr(service, "_collect_extras", boom)` 直接抛 `OSError`，只覆盖了通用 `OSError`→`BACKUP_CREATE_FAILED` 映射，**完全绕过新增的 `_skipped_categories` 判定**；fixture 的 drafts/plugins 始终有文件，因此 R-001 不会被测试发现。也缺少：空目录、真实不可读根、未知 extras 成员、`skipped_categories` 字段、settings 缺文件的负例。 | 测试代码与独立探针；当前 4 例全绿，但空 drafts 用例若加入会立即 RED。 | 至少补：空 `drafts`/`plugins` 成功入包（0 文件）、空 settings、DraftJournal 干净关机后的根、`_skipped_categories` 仅在读取失败时触发；未知 extras 成员 → `BACKUP_CORRUPT`；`skipped_categories` 成功包为 `[]` 的断言。 | open |
| **R-004** | **P2** | `doc/tasks/FEA-13-COV-2.md:29-34`（out_of_scope 未提）；`doc/tasks/FEA-13-BK2-1.md:95`；`doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md:26,38`；`doc/reviews/FEA-13-BK2-1-r1.md:57` | BK2-1 r1 R-003 的处置把「SC-B01 源引用与授权元数据入包」明确移交「片 2（FEA-13-COV-2）/独立裁决」，但本卡 AC、out_of_scope 与实现均未涉及，也未见独立裁决；FEA-13 收尾时该 C-09 强制增量可能静默丢失。 | 上列文件逐条对照；本 head 的 diff 无相关实现/登记。 | DSH 在 closeout 前明确裁决：单列 Task、或在 C-09 冻结记录登记未实现/延后，并同步 BK2-1 处置与 STATUS/PLAN；不得以「不属本片 AC」静默关闭。 | open |
| **R-005** | **P3** | `doc/handoffs/FEA-13-COV-2-00f14179a.md:18`；`verification/FEA-13-COV-2/README.md:19-20,28-30`；`verification/FEA-13-COV-2/logs/mutation-deferred.log:1` | 文档口径与卡冲突/证据标签不精确：Handoff 写「类别根存在但收集为空/失败 → `BACKUP_CREATE_FAILED`」，卡 `:48` 明确空目录记 0 文件；README 把 AC5② 写成「`deferred_categories` 清空」，而卡 `:63` 的②是「restore 写回 extras」，日志命令也只写「deferred_categories emptied」；变异日志未记录被改代码的 diff，复现依赖文字描述。 | 逐行对照卡 `:59-64`、Handoff、README、两份 mutation log；本次独立真变异已证明 AC4 断言可判别。 | 统一为「空目录=合法 0 文件、仅收集错误才失败」；要么把 AC5② 作为补充变异如实标注（非卡面②），要么补真正的「写回 extras」变异日志（含改动 diff/命令/EXIT）；两处口径在同一处写清。 | open |
| **R-006** | **P3** | `doc/TASK_LEDGER.md:14-16` | ledger 声明 `task files tracked by git = 561`、`untracked (drafts) = 1`、`non-terminal tracked = 11`，但 head 上 `FEA-13-COV-2.md` 已被 `00f14179a` 跟踪，`python tools/governance/task_ledger.py` 实测为 **562 tracked / 0 untracked / 12 non-terminal tracked**。`check.ps1` 只比 `task files=562` 与 `non-terminal=12` 两项，所以门禁未发现该漂移。 | 实跑 `python tools/governance/task_ledger.py`（EXIT=0）与 `git ls-files doc/tasks/FEA-13-COV-2.md`；行号见左。 | DSH 生命周期写权重跑 `python tools/governance/task_ledger.py --write`（或在卡/Handoff 说明是生成时口径），避免 closeout 引用错误计数。 | open |
| **R-007** | **P3** | `src/infrastructure/sqlite/nmbak.py:280-289`、`:841-879` | manifest 的 `included_categories`/`skipped_categories`/`excluded_categories` 在 `_verify_package` 中完全未交叉校验：篡改 manifest 可让类别声明与 `extras` 实际成员不一致而仍通过验证；`skipped_categories` 在成功包中恒为 `[]`（任何非空都在创建前 abort），事实上是死字段；另外，未来新增 extras 类别（同 `version:2`）会被本版本判为 `BACKUP_CORRUPT` 而非 `BACKUP_FORMAT_UNSUPPORTED`，前向兼容性未定义。 | 代码逐行；现有测试只断言创建侧，未覆盖篡改类别字段。 | 在 `_verify_package` 中断言 `extras` 的类别集合与 `included_categories` 一致、`skipped_categories` 为空；明确 extras 类别的版本/前向兼容策略（未知类别 → `BACKUP_FORMAT_UNSUPPORTED` 或 manifest feature 字段），并在 README 登记。 | open |
| **R-008** | **P3** | `src/infrastructure/sqlite/nmbak.py:628-638`、`:641-660` | extras 收集对 `rglob` 结果只判断 `is_file()`，会跟随文件符号链接把 data_root 之外的内容读入包；若以符号链接作为 `drafts`/`plugins` 根，也可能把外部目录纳入。`_resolve_within` 只用于 managed 路径，未用于 extras，和「外部原文件不入包」的边界不完全一致。 | 代码路径；Windows 默认允许文件 symlink（需权限），未被测试覆盖。 | 对 extras 使用与 managed 相同的「词法 + resolve 后仍在根内」校验；至少排除 `path.is_symlink()`，并在卡/README 记录该边界。 | open |

**计数：P0 = 0；P1 = 1（R-001）；P2 = 3（R-002/R-003/R-004）；P3 = 4（R-005/R-006/R-007/R-008）。**

## 5. 门禁与复跑（本环境实际执行）

| # | 场景 | 命令/步骤 | 结果 | EXIT |
|---|---|---|---|---|
| G1 | 卡指定 pytest（6 文件） | `python -m pytest tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_format.py tests/storage/test_nmbak_coverage.py tests/storage/test_backup_restore.py tests/core/test_core_backup_wire.py tests/infrastructure/test_nmbak_startup_backup.py -q` | **70 passed**（9.16s；证据日志 70 passed/9.34s 同口径） | **0** |
| G2 | 治理默认 | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)**：12 个非终态 Task；STATUS/PLAN 80% 预算 | **0** |
| G3 | 治理按卡 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-13-COV-2.md` | **PASS (3 warnings)** | **0** |
| G4 | 证据 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**（C09 `dc51226b336c`） | **0** |
| G5 | EV sha256 ×4 | `Get-FileHash -Algorithm SHA256` 对卡 EV 表 | **4/4 MATCH** | **0** |
| G6 | 变异① extras sha 禁用 | 临时改 `if hashlib.sha256(extra_bytes)...` → `if False and ...`；`pytest tests/storage/test_nmbak_coverage.py -q` | **1 failed / 3 passed**（同长篡改用例 RED）；`git checkout --` 后 **4 passed** | **1 / 0** |
| G7 | 变异② restore 写回 extras（补充） | 临时在 `restore` 写回 extras；`pytest tests/storage/test_nmbak_coverage.py -q` | **1 failed / 3 passed**（AC4 字节断言 RED）；还原后 **4 passed** | **1 / 0** |
| G8 | 边界 | `git diff --name-only 892cb99df..00f14179a` | **8/8 ⊆ allowed_paths**；out_of_scope 相关路径零 diff | **0** |
| G9 | 工作树 | `git status --porcelain`（代码复核结束、报告写入前） | 空；`nmbak.py` sha256 变异前后一致 `A14EB6…69DE` | **0** |

## 6. 剩余风险

1. **包体/内存**：`drafts/**`、`plugins/**` 进入每次 manual/automatic/pre_restore 包；`_verify_package` 用 `archive.read(member)` 整文件读入内存（`:860`）。本片只保证覆盖，大小/保留策略归片 5（卡 `:87`），但大目录会放大 restore 校验内存与时间，需在片 5 前持续登记。
2. **片 4 写回语义**：本片只 defer；若片 4 直接按 extras 写回，`.lock/pid`（R-002）与 0 文件类别的表示（R-001）会立刻暴露，需在片 4 设计前先修/定稿。
3. **wire 投影**：`core_service.handle_backup_restore` 直接返回 service report，`deferred_categories` 会以新增键进入响应；`tests/core/test_core_backup_wire.py` 未断言该键，Host 侧消费未知。卡声明「不改 wire」，实际是 additive payload 变化，需片 4/5 与 Host 对齐。
4. **SC-B01 源授权元数据**：R-004 尚未落实/裁决，是 FEA-13 收尾的跨片风险。
5. **旧包**：v1/v2 无 `extras` 按空处理，现有 70 用例含旧包场景；仍缺 base-writer golden（BK2-1 R-001 残余，COV-2 未承接）。
6. **平台边界**：真实 Windows ACL/权限拒绝、符号链接、只读根未实测；R-008 仅为代码级风险。
7. **治理**：ledger tracked/untracked 计数漂移（R-006）；`check.ps1` 不校验这两项，不能作为 ledger 正确性的证据。

## 7. 未验证项

- `tests/storage` 全量、全量 .NET、Host/Avalonia 侧 `deferred_categories` 的解析与展示。
- 真实用户 profile 的 v8→v9（或未来版本）升级；本报告只在合成库上证明链路会失败（R-001）。
- 真实不可读目录/ACL 下 `Path.rglob` 是抛错还是静默返回；`_skipped_categories` 的「不可读」语义未实测。
- 大体积 drafts/plugins 的包体、耗时、内存与 restore 行为。
- 符号链接/外部卷边界（R-008）。

## 8. 结论与复审

- **decision：`changes_requested`。** 本 head 的 extras 入包、排除记录、restore defer、sha/size 校验与治理门禁大体落地（AC2/AC4/AC5/AC6 MET），但 R-001 是**由本 diff 引入的 P1 回归**：正常干净关机后的空 `drafts/` 会让 pre-migration 备份失败并阻断升级，且与任务卡 `:48` 明确冲突。按 `doc/templates/REVIEW.md:18` 的批准门槛（P0/P1 未解决不可批准），当前不可交 DSH 集成。
- **复审前至少完成**：R-001 修复 + 空目录/升级路径测试；R-002 排除 `.lock`；R-003 补判别测试；R-004 由 DSH 裁决归属；R-005 统一口径。R-006/R-007/R-008 可随返修或后续片处置，但需在 Handoff/README 登记。
- 本报告只对 `reviewed_head 92e8f88b8` 有效；若代码/证据/卡变化，须以新 head 重新派发独立上下文复审。
- 本审查未 commit、未 push、未改生产源码/测试/契约；唯一仓库写入为本文件；探针脚本仅位于 `%TEMP%`，未进入仓库。
