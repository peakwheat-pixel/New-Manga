---
task_id: FEA-11-MATCH-1
reviewer: DSH 独立上下文子 agent（fresh subagent，session 2658835c-a883-472a-89a5-e0e2f5c01c3e；未参与本卡 r1/r2 实现、夹具修复、证据生成或 r1 Review）
reviewer_kind: subagent
session: 2658835c-a883-472a-89a5-e0e2f5c01c3e（parent session-8db9dae5-49df-4d09-ac62-696f0805a95c）
author: fea12-dsim-impl（DSH Agent Teams 成员；Lead `lead`）
base_commit: 2d9a4a219
implementation_head: e8b0b2db8
reviewed_head: 869b6d5d5
scope: r2 窄面复审（R1-01/R1-02/R1-03 核销 + P3 同批 + 门禁/范围/closeout）
decision: approved
findings: P0=0 P1=0 P2=0 P3=3（均为文档/簿记口径，非实现或证据缺陷）
---

# Review r2（窄面）：FEA-11-MATCH-1

## 0. 范围与执行口径

- **被审 head**：`869b6d5d5`（docs/证据；作者时间 01:58:19、提交时间 01:58:42）；实现+测试 `e8b0b2db8`（01:48:32）；r1 交付 `c12023ab6`；base `2d9a4a219`。
- **只读**：未 commit/stash/push/checkout，未修改任何受跟踪文件；复跑、变异树、探针与日志全部写在仓外 `G:\CODEX\New Manga.workspace\FEA-11\review-match-1-r2\`。审查主体期间 `HEAD=869b6d5d5`；结束前因 SCAN-1 提交前进（见下），`reviewed_head` 仍固定为 `869b6d5d5`。
- **并发事实（必须记录）**：审查开始时工作树含他卡 `apps/**` 8 个 `M` + 4 个 `??`（SCAN-1 WIP，不属本复核对象）；审查期间（02:14:50–02:16:39）SCAN-1 把该批 WIP 提交为 `73d01fd2b`/`a684c511d`/`8e8aa5aaa`/`6e5e210a5`，`HEAD` 由 `869b6d5d5` 前进到 `6e5e210a5`，工作树恢复 clean。**`869b6d5d5..HEAD` 对 MATCH-1 范围（`matcher.py`/`scanner.py`/`test_source_match.py`/`verification/FEA-11-MATCH-1/**`/卡/Handoff）零 diff**，故本报告全部结论对 `reviewed_head=869b6d5d5` 有效；但**门禁的零 diff 必须在 `2d9a4a219..869b6d5d5` 上引用**——在移动的 `HEAD=6e5e210a5` 上重跑 `git diff 2d9a4a219..HEAD -- apps` 会因 SCAN-1 的已提交 `apps/**` 而**非空**（那是 SCAN-1 的变更，不是 MATCH-1 的）。
- **一个必须如实记录的副作用**：全量 pytest（本 Review 第 3 节）在 02:07:18 重写了既有测试副作用文件 `verification/FEA-09/logs/wire-redacted.ndjson`（R8 既有 debt，写入方为 `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/WireLogSourceRedactionTests.cs:33`/fea09 测试路径），使审查开始时的 `M`（`93AA3670…`，非 FEA-09 canonical pin）恢复为 **FEA-09 EV-059 登记的 canonical 字节 `548de629…`（5004B）**；该文件随后未被任何新提交纳入，当前与 `HEAD` 一致（`git status` clean）。DSH 如需保留他卡那份 drift，属本 Review 无法还原的既有测试产物（其 canonical pin 本就是 `548de629…`，当前即登记态）。
- **并发事实**：`c12023ab6..869b6d5d5` 区间还含两个**他卡**提交（`b621a3310` SCAN-1 ready、`e0c370870` HOST-AUTH-1 SOURCE_PIN 登记），不计入本卡；本卡 r2 自身只有 `e8b0b2db8`（2 文件）与 `869b6d5d5`（12 文件）。
- **依据**：卡 `doc/tasks/FEA-11-MATCH-1.md`、Handoff `doc/handoffs/FEA-11-MATCH-1-handoff.md`、`verification/FEA-11-MATCH-1/**`、r1 报告（仓外 `review-match-1/FEA-11-MATCH-1-r1.md`）、`src/application/sources/{matcher,scanner,model,planner}.py`、`src/infrastructure/sqlite/{source_sync,schema}.py`、`tests/fea11/{test_source_match,test_source_sync}.py`、`tests/fea11/conftest.py`、`tools/governance/{check,verify_pins}.ps1`。

## 1. 结论

**approved。P0 = 0，P1 = 0，P2 = 0，P3 = 3（新增，均为文档/簿记，不阻断 closeout）。**

r1 三条 P2 全部**实质修复且可判别**：

1. **R1-01**：唯一像素 pass 新增 `elif len(candidates) == 1 and not comparable` → `ambiguous/incomparable`（双侧非空、写 `paired_*_ids`），转换正确；新增改名 × orientation/params/decoder_version 三维判别测试；**删除该分支即变红**（本 Review 独立变异）。我另做了**端到端探针**：真实迁移 + 真实 HMAC grant + 真实严格读 + 改名/重编码容器 + 旧 params 代际不可比 → scan 输出 `ambiguous/incomparable`（totals 仅 1 条 ambiguous），显式 `bind` 决策被 plan/confirm/apply 接受，apply `core-committed`，`p1` **PageId 保留**（binding_version 2，`previous_binding_id=pb-p1`）。「保留 bind/PageId」不再只是读码推断。
2. **R1-02**：字节分支守卫测试改为**可达形态**（旧行 v7 无 profile，前置 duplicate pass 不吸收；新侧一字节同一 + 一同像素成员）。**r1 M6 变异（去掉字节分支重复守卫）现使该用例变红**（`unchanged/unique_pixel` vs 期望 `ambiguous/duplicate_group`），判别性成立。
3. **R1-03**：7 份日志 `recorded_at` 与 mtime 同秒级一致（Δ=+0.88…+4.83s），全部**晚于代码提交 01:48:32、早于 docs 提交 01:58:42**；全文时间线自洽（全量 237s 必须在 01:48:32 之后启动才能在 01:53:01 写完）；10 条 Canonical Evidence sha256 逐项复算 **10/10 MATCH**，`check.ps1` 机械校验 PASS、`verify_pins` 18/18。

P3 三条（§6）：R2-01「40 表」口径不实（运行期 `sqlite_master` 为 **36**；40 是迁移 SQL 中 `CREATE TABLE` 语句数，含 4 个 v5 重建临时表）；R2-02 卡面「测试要求」表仍写 `fea11 107 passed`（应 108，同卡正文与证据均为 108）；R2-03 卡面引用的 `doc/reviews/FEA-11-MATCH-1-r1.md` **不存在**、`reviewer: null`（r1 报告未落盘，属 DSH closeout 动作）。

## 2. r1 findings 核销

| r1 ID | 级别 | 处置核验 | 判定 |
|---|---|---|---|
| **R1-01** 改名+profile 不可比时输出 missing+added | P2 | `matcher.py:338-360` 新分支：条件 `len(candidates)==1 and not comparable`（等价于 `len(comparable)==0`）→ `ambiguous/incomparable` 并占用双侧 id；判别测试 `test_renamed_incomparable_counterpart_is_ambiguous_not_missing_added`（`test_source_match.py:414`）覆盖 old `001.png` vs new `002.png` × {orientation=6, params frame=1, decoder_version=2}，断言 classification/evidence、`totals=={ambiguous:1}`、且无 `unique_pixel`/`direct`。**变异 MR2-01（整段删除）→ 该用例 FAIL（`('missing','none')`）**。端到端 bind 探针见 §4.1。 | **已修复（RESOLVED）** |
| **R1-02** 字节分支重复守卫测试不判别 | P2 | 用例改为 `old`（`pixel_digest=None, width=4, height=3`）+ `new1`（字节同一、pixel=P）+ `new2`（pixel=P）→ 前置 duplicate/unique pass 都不吸收 `old`，字节分支实际执行。**变异 MR2-02（r1 M6 同款）→ 该用例 FAIL（`unchanged/unique_pixel`）**，且新增 `totals` 断言（ambiguous 1 + added 1）。 | **已修复（RESOLVED）** |
| **R1-03** 日志 `recorded_at` 不可为真 | P2 | 7 份日志头部改为 `datetime.now()` 机器时间（`probe_recorded_at.py` 逐项对照）；mtime 与 `recorded_at` Δ 见 §3.3；基线日志头明确注明「body 于释放日 ~00:24 捕获、头部为重生成时刻」。数字与我的独立复跑一致。 | **已修复（RESOLVED，附字段语义说明）** |
| R1-04 `_old_evidence_complete` 死代码+错误 docstring | P3 | 已删除；`src/`+`tests/` grep **0 引用**（仅 Handoff 处置表提及该名称）。 | **已处置** |
| R1-05 快照仅 17/40 表 | P3 | `_snapshot` 改为 `sqlite_master` 枚举（`test_source_match.py:241`）；本 Review 探针：**36/36 覆盖**，`missing=[]`，含 `reading_progress/rendition_cache/pipeline_run_targets/step_result_candidates/step_runs/media_artifacts`。**但「40 表」数字不实 → R2-01**。 | **已处置（数字待更正）** |
| R1-06 gates.log 最终复跑在登记前（4 warnings） | P3 | gates.log 现记录 **PASS (3 warnings)** 且与卡面一致；我的独立 `check.ps1 -TaskPath` 输出与日志逐行一致（3 warnings）。登记行在跑该次 check 时已存在（否则会有第 4 个「evidence_dir 未登记」warning）。**遗留一处不可避免的自指**：gates.log 是 EV-M10 自身，嵌入的 check 输出必然早于最终 sha 的定格（否则 pin 不匹配），故「最终复跑」只能理解为「EV-M10 行登记后」，不能自证「最终 pin 之后」；建议在 Closeout Record 用 DSH 自己的 closeout 复跑补一条最终 PASS（不必重写 gates.log）。 | **已处置（附自指说明）** |
| R1-07 lost-scan 断言过松 | P3 | `test_source_match.py:938-985`：断言 `code == "SOURCE_PLAN_STALE"`、`details["cause"] == "expired"`、全表快照相等、`source_operations`/`source_binding_publications` 行数零增。实现侧 `errors.py:61-64` 确为 `stale(cause)` 形状。 | **已处置** |
| R1-08 changed 缺显式像素不同守卫 | P3 | `matcher.py:392-398` 增加 `old.pixel_digest == new.pixel_digest → ambiguous/duplicate_group`。当前**结构性不可达**：任何能进入 locator pass 的 old 行必为「无双侧 ≥2 的 triad」，若 new 侧存在同像素行，unique-pixel pass 早已配对（可比→unique_pixel，不可比→R1-01 分支）；若 old 侧 ≥2，duplicate pass 早已吸收。守卫为面向未来重排的防御，正确。 | **已处置** |
| R1-09 `encrypted` 被写成端到端已证 | P3 | EV §4/Handoff AC-M1 已收窄为「仅 `_reason_for_import_error` 映射层单测，zip 加密成员扫描级端到端未构造」。 | **已处置** |
| R1-10 空条件 `pyproject.toml` | P3 | 证据命令/表格已移除；`pyproject.toml` 实测不存在（`Test-Path` False），证据改为 `requirements.txt`+`schema.py`+`migrator.py`。 | **已处置** |
| R1-11 binding 状态表述不一 | P3 | 卡 AC-M3/AC-M5、Handoff、EV 统一为「旧 binding 保持原状态（本装置为 `healthy`）」。`AC-MATRIX.md:7` 仍用 `duplicate_group+needs_confirmation`，但该词指 ambiguous 分类语义（C-17 口径），非 binding 状态，不算遗漏。 | **已处置** |
| R1-12 非图片成员 `content_digest=None` → apply NOT NULL | P3（卡外） | 未修；卡「残余 limitation/卡外后续」（`:192`）与 EV §5 已如实登记为卡外后续。 | **已登记（保持 open，卡外）** |

## 3. 独立复跑（本 Review 实跑）

### 3.1 门禁

| 场景 | 命令 | 结果 | 日志（仓外） |
|---|---|---|---|
| 隔离测试 | `C:/Python314/python.exe -m pytest tests/fea11 -q -p no:cacheprovider` | **108 passed**, 8 warnings, 2.97s, EXIT 0 | `pytest-fea11.log` |
| 本卡测试 | 同上 `tests/fea11/test_source_match.py` | **20 passed**, EXIT 0 | `pytest-match.log` |
| 全量 | `… -m pytest tests -q -p no:warnings --tb=no` | **3203 passed, 10 skipped**, 264.83s, EXIT 0 | `full-pytest.log` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)** | `verify-pins.log` |
| 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-MATCH-1.md` | **PASS (3 warnings)** | `check-task.log` |
| 治理（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)** | `check-default.log` |
| 零漂移 | `git diff --name-only 2d9a4a219..869b6d5d5 -- doc/plan doc/contracts apps`；`-- src/infrastructure/sqlite/schema.py src/infrastructure/sqlite/migrator.py requirements.txt requirements-dev.txt` | **空 / 空**（**必须在 reviewed_head 上引用**；`HEAD` 已被 SCAN-1 推进，见 §0） | 终端 |
| 变更域 | `git diff --name-only 2d9a4a219..869b6d5d5 -- src tests`（`HEAD` 前进后复核结果不变） | 2 src + 4 tests（`matcher/scanner`；`test_source_match`、W1 `test_source_scan`、W1b `test_source_sync`/`test_source_relink`）；`conftest.py` 零 diff | 终端 |
| `.NET` | NOT_RUN | 合法：已提交范围 `apps/**` 零 diff、本卡无 C# 变更；未写 PASS | — |
| 推送/工作树 | `git rev-list --count origin/main..HEAD`=941；`HEAD..origin/main`=0；HEAD 非 origin/main 祖先 | **未 push**；审查结束工作树 clean（SCAN-1 已提交其 WIP） | `status-before.txt`/`status-after.txt` |

### 3.2 证据 pin / 时间线

- Canonical Evidence 9×CANONICAL + EV-M10 SOURCE_PIN 逐项复算 **10/10 MATCH**（含 `gates.log`=`09cae20f…`、`EV.md`=`5033409a…`）。
- `recorded_at` vs mtime vs commit（`probe_recorded_at.py`）：

| 日志 | recorded_at | mtime | Δ | 晚于代码提交 | 早于 docs 提交 |
|---|---|---|---|---|---|
| pytest-fea11 / pytest-match / pytest-full / verify-pins / pytest-baseline | 01:53:01 | 01:53:01.881–.882 | +0.88s | ✓ | ✓ |
| static-diff | 01:56:16 | 01:56:16.939 | +0.94s | ✓ | ✓ |
| gates | 01:58:00 | 01:58:04.827 | +4.83s | ✓ | ✓ |

- 时间线自洽：代码提交 01:48:32 → 全量 237s（约 01:49:04 起、01:53:01 止）→ 01:53:01 批量写日志头 → 01:54:28 AC-MATRIX → 01:55:15 Handoff → 01:56:16/17 static-diff、changed-files → 01:56:30 EV.md → 01:58:00/04 gates.log → 01:58:19/31/42 卡/docs 提交。**R1-03 的不可能时间戳已消失。**

### 3.3 日志正文与本次实跑的一致性

`fea11 108`、`match 20`、`full 3203/10`、`pins 18/18`、两份零 diff 空、`check PASS (3 warnings)` 与我的独立输出逐项一致；`pytest-full.log` 正文 `3203 passed, 10 skipped in 237.42s`、`pytest-baseline.log` `3183 … 237.96s`，skip 数与基线同为 10（无新增 skip）。基线未在旧 head `71e4b42b4` 重跑（不改工作树/不新建 worktree），以 delta 交叉验证：3203−3183=20 = 本卡新增用例数（19→20，见 §4.4）。

## 4. 变异 / 反证（仓外副本 `review-match-1-r2/mut`，仓库零改动）

| # | 变异（精确单点替换） | 预期 | 实测 | 结论 |
|---|---|---|---|---|
| **MR2-01** | 整段删除 `matcher.py:338-360` 的 R1-01 降级分支 | 新用例红 | `test_renamed_incomparable_counterpart_is_ambiguous_not_missing_added` **FAILED**（`('missing','none') != ('ambiguous','incomparable')`，dimension=orientation） | **RED ✓** |
| **MR2-02** | 字节分支去掉重复守卫（r1 M6 同款：`pixel_duplicate` 判定改为恒定 `unchanged/unique_pixel`） | R1-02 用例红 | `test_byte_identity_does_not_bypass_a_duplicate_pixel_group` **FAILED**（`('unchanged','unique_pixel')`） | **RED ✓** |

副本基线（未变异）先以 `test_source_match.py` 20 passed 自检，再施加变异，避免环境噪声。

### 4.1 R1-01 端到端（`probe_bind_e2e.py`，真实栈）

构造：生产迁移 v8 + 真实 zip + 真实 HMAC grant + 真实 `read_verified_bytes`；旧行由 seed 写入**真实完整 profile**（等价 W1b 的 complete-profile 夹具，非真实导入），再把 `decoder_params_json` 换成 `frame=1`（模拟旧 decoder params 代际）；新容器 = 改名成员 `002.png` + **同栅格重编码字节**（pixel digest 相同、content_digest 不同）。

- scan：`diff = [('ambiguous','incomparable', page 'p1', old 'e1', new 'se-…')]`，`totals = {ambiguous:1}`（无 missing/added）。
- 显式 `bind`（`target_page_id='p1'`）→ plan/preview/confirm 接受（`planner.py:199-210` 要求 ambiguous 必须 bind/defer）→ apply `core-committed`。
- 结果：`p1` 仍在 `pages`；binding v2 `healthy`，`previous_binding_id=pb-p1`，`accepted_source_version=新版本`；publication `relation='changed'`（`service.py:906-922` 对非 direct/unique_pixel 一律返回 `changed`，即不继承坐标，方向安全）。

> 说明：该用例必须「同像素、不同字节」。若改名成员字节也相同，`content_digest` 唯一相等会先被字节分支按 AC-M4「唯一字节等价」判为 `unchanged/unique_pixel`（合法，非缺口）；R1-01 场景对应「重打包/重编码改名 + Pillow/params/decoder 变更」。
>
> 条件安全性：新分支未重复检查 `old/new_pixel_counts`，但**由 pass 顺序保证**——凡进入唯一像素 pass 且未配对的 old 行，`_is_duplicate_member` 为假，即两侧该 `pixel_digest` 计数只能为 1（new 侧 ≥2 或 old 侧 ≥2 都会先在 duplicate pass 被吸收）。因此 `len(candidates)==1 and not comparable` 即「唯一同像素 counterpart 不可比」，无重复组误判风险。

### 4.2 R1-05 快照覆盖（`probe_snapshot.py` / `probe_table_count.py`）

- 运行期 v8 `sqlite_master` 用户表 **36**；`_snapshot` 36 个 key，`missing=[]`，`extra=[]`，`_SNAPSHOT_TABLES` 已不存在。
- 迁移 SQL 中 `CREATE TABLE` 语句 **40** 条（含 4 个 `*_v5` 重建临时表，最终库中不存在）——**这正是「40 表」的来源，但不是运行期表数 → R2-01**。

### 4.3 R1-08 不可达性

结构性论证：locator pass 只处理未被更早 pass 配对的 old 行。若 old 与某个未配对 new 行 `pixel_digest` 相同且唯一，则 unique-pixel pass 已配对（可比）或已由 R1-01 分支配对（不可比）；若任一侧该像素计数 ≥2，old 行必为 duplicate member，早被 duplicate pass 吸收。故 `changed/direct` 分支不可能遇到同像素对；守卫为防御性正确实现。

### 4.4 测试集完整性

`c12023ab6` → `869b6d5d5` 的 `test_source_match.py`：`def test_*` **19 → 20**，**无删除**，仅新增 `test_renamed_incomparable_counterpart_is_ambiguous_not_missing_added`；删除行仅为（a）旧 17 表快照元组、（b）字节用例旧 fixture 与旧 docstring、（c）lost-scan 的「任意 typed」弱断言（被更强的 code+cause+计数断言替换）。未放松任何断言。

## 5. 范围与纪律

- **r2 两提交**：`e8b0b2db8` = `src/application/sources/matcher.py` + `tests/fea11/test_source_match.py`（均在 allowed_paths）；`869b6d5d5` = 卡 + Handoff + `verification/FEA-11-MATCH-1/**`（12 文件，均 allowed_paths）。
- **无越界**：`conftest.py`、`test_source_scan.py` 之外的其它测试、`scanner.py`（本轮）、`model.py`、`service.py`、`ports.py`、`core_assembly.py`、`referenced/**`、`schema.py`、迁移、依赖清单、`apps/**`、`doc/plan`、`doc/contracts` 全零 diff。W1/W1b 文件未在 r2 再动（r2 只动 `test_source_match.py`）。
- **未 push**；`a85874186`/`b621a3310`/`e0c370870` 等指针/他卡提交不计入本卡。
- **他卡 WIP 未计入**：审查开始时 `apps/**` 未提交内容属 SCAN-1，未出现在任何 r2 提交与证据命令的已提交范围里；审查后期 SCAN-1 自行提交（`73d01fd2b` 等），本 Review 未参与、未评价其内容。MATCH-1 的 `apps/**` 零 diff 只在 `2d9a4a219..869b6d5d5` 成立。
- **证据口径**：`changed-files.txt` 的「committed vs base」是**整段** `2d9a4a219..HEAD` diff，故含他卡 docs 行（STATUS/PLAN/LEDGER/AC4-GAPS-1/HOST-AUTH-1/SCAN-1/FEA-11.md）；标题已写「committed vs base」，属可读但易误读，建议 closeout 时标注「含他卡指针提交」。非缺陷。

## 6. Findings（本轮新增，全部 P3，不阻断）

| ID | 级别 | 位置 | 事实与影响 | 最小返修点 |
|---|---|---|---|---|
| **R2-01** | P3 | `tests/fea11/test_source_match.py:238-240`；Handoff §0 R1-05 行 | 「schema currently has 40 of them」/「当前 40 表」**不实**：运行期 `sqlite_master` 用户表为 **36**；40 是迁移 SQL `CREATE TABLE` 语句数（含 4 个 `*_v5` 重建临时表，最终库不存在）。功能结论不受影响（快照确为全表 36/36）。 | 注释与 Handoff 改为「运行期 `sqlite_master` 用户表（当前 36；迁移 SQL 中 `CREATE TABLE` 共 40 条，含 4 个 v5 重建临时表）」，或直接去掉数字。改注释只影响该文件字节，`fea11 108` 需以注释-only 说明（3s 可复跑）。 |
| **R2-02** | P3 | `doc/tasks/FEA-11-MATCH-1.md:156`（测试要求表 AC-M6 行） | 仍写「**fea11 107 passed**」，与同卡 §状态段/AC-M6 正文（108）、`AC-MATRIX.md:9`、`EV-M3`（108）矛盾；属 r1 数字残留。 | 改为 108（或改为「见 `logs/pytest-fea11.log`」避免硬编码）。 |
| **R2-03** | P3（closeout 动作） | 卡 `:47`/`:198`、Handoff `:16`；`doc/reviews/` | 卡/Handoff 引用的 `doc/reviews/FEA-11-MATCH-1-r1.md` **不存在**（`Test-Path` False，`doc/reviews` 无 MATCH-1 文件），且卡 `reviewer: null`。r1 §9.6 要求的落盘未执行，读者无法从仓库取到 r1 结论。 | DSH closeout 时把 r1 报告与本 r2 报告落盘为 `doc/reviews/FEA-11-MATCH-1-r1.md`、`…-r2.md`，回填 `reviewer`（或 `review` 字段）指向两份报告与 session 来源。 |

> 观察（非 finding）：`gates.log` 的自指（R1-06）与 `changed-files.txt` 的整段 diff 口径各有一句话说明需求，建议 closeout 记录注明，无需改实现。

## 7. 未审到 / 残余风险

1. **基线数字**未在 `71e4b42b4` 重跑（只读约束下不新建 worktree），以 3203−3183=20 与 19→20 交叉验证；基线 body 为释放日实跑（日志头已注明）。
2. **未跑 .NET**（`apps/**` 零 diff，NOT_RUN 合法）；Host/IPC 侧未涉及。
3. **真实用户库/真实卷/跨卷/移动盘、PDF、folder-source 专项**未验证；R1-12 的 NULL digest apply 风险仍未实测（卡外）。
4. 新分支的安全性依赖「profile 由字节派生」的一致性前提（生产成立、单测夹具可不一致）；若未来允许手工 profile，需重新论证 §4.1 的计数不变量。

## 8. Closeout 建议（DSH 动作，不在本 Review 执行）

1. **AC-M1…AC-M6**：按 §2 与 §3 可定稿 **全部 MET**（AC-M4 的 R1-01 边界已由实现+判别测试+端到端 bind 探针闭环）。`.NET` NOT_RUN 口径保留。
2. **AC11-3 回填（FEA-11 卡）**：建议写
   **「AC11-3 = MET（由 `FEA-11-MATCH-1` 承接 r7 L-4 / R-012 闭环；两条路径、7 维可比性+一对一唯一、重复组 needs_confirmation、旧证据缺失/不可比降级且不伪造、真实 FEA-09 v7 旧库 fixture + 独立 match 测试。残留 limitation：L-M1（PDF 插页不产 pixel profile）、L-M4（旧证据按冻结参数重算未实现）；另注：AC11-3 字面『目录重复内容不合并 occurrence』与 zip 同机制但未设 folder-source 专项断言）」**。
   若验收口径不允许 AC 带 limitation 记 MET，则保持 **PARTIAL** 并点名 L-M1/L-M4——**不得无条件写 MET**。回填时不得改历史证据字节。
3. **delivery_head**：建议取 **`869b6d5d5`（含卡/Handoff/证据）**，并在卡/Handoff/EV 明确记录**实现 head `e8b0b2db8`**；理由：与 r1 §9.2 建议及 `FEA-11-AC4-GAPS-1` 先例（delivery_head 指向含证据提交）一致，审计从 delivery_head 出发即含取证。若坚持现口径（`e8b0b2db8`），**必须**在 Closeout Record 写明「交付提交 `869b6d5d5`（r2 docs/证据）」并保持三处一致——当前三处一致指向实现 head 且注明「r2 docs 紧随其后」，属可接受但不利于「按 head 取证据」。
4. **`integration_commit`**：由 DSH 在 closeout 填最终集成/文档提交（若 R2-01/R2-02 与 review 落盘合并提交，取该提交）；提交后重跑 `check.ps1`/`verify_pins.ps1` 并把**最终 PASS** 记入 Closeout Record（解决 R1-06 自指，无需重写 gates.log）。**零 diff 必须按本卡交付范围引用**（`2d9a4a219..869b6d5d5` 或 closeout 时重新采集的范围）；`HEAD` 已被 SCAN-1 推进，在移动 HEAD 上跑 `git diff 2d9a4a219..HEAD -- apps` 会因 SCAN-1 已提交文件而非空，不得误判 MATCH-1 越界。
5. **状态字段**：`canonical_evidence_status` → `complete`（done 的机械要求），`resource_closeout_status` → `complete`（无删除/迁移；仓外隔离根与 `review-match-1-r2/` 按 PRESERVE/清理策略处理，`closeout_counts` 如实填 0）。
6. **R2-01/R2-02** 可选在同一 closeout 文档提交内修正（R2-01 只改注释文本，若改则顺手复跑 `tests/fea11` 3s 留证）；**R2-03 必做**。
7. **L-M1…L-M7 / R1-12**：卡面、Handoff、EV 三处如实且一致；R1-12 保持「卡外后续」，不得并入本卡 closeout 当作已修。

---

**decision: approved。** P0=0/P1=0/P2=0/P3=3（R2-01「40 表」应为 36、R2-02 卡面残留 `fea11 107`、R2-03 r1/r2 Review 未落盘且 `reviewer: null`）。r1 三条 P2 全部实质修复：R1-01 改名不可比 → `ambiguous/incomparable` 且端到端 `bind` 保留 PageId（p1、binding v2、apply `core-committed`）；R1-02 字节守卫用例在 M6 变异下**变红**；R1-03 时间戳与 mtime/提交序列自洽、10 条 pin 10/10 MATCH。门禁独立复现（tree=`869b6d5d5`）：fea11 **108**、本卡 **20**、全量 **3203/10**、pins **18/18**、`check.ps1`（默认与 `-TaskPath`）**PASS (3 warnings)**、契约/plan/schema/迁移/依赖/apps 在 `2d9a4a219..869b6d5d5` 内**零 diff**、`.NET` 如实 **NOT_RUN**、未 push、无 conftest/越界改动。建议 closeout：AC11-3 回填 **MET（带 L-M1/L-M4 limitation）**、delivery_head 取 **`869b6d5d5`** 并记录实现 head **`e8b0b2db8`**、落盘 r1/r2 Review。

MATCH-1-R2-REVIEW: APPROVE（P0=0 P1=0 P2=0 P3=3；R1-01/02/03 已实质闭合，附 P3 文档/簿记处置建议）
