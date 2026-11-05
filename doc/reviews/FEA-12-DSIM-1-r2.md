---
task_id: FEA-12-DSIM-1
reviewer: DSH 独立上下文 fresh subagent（session a39295f9-012b-401d-b35e-864c4c481d00；父会话 session-8db9dae5-49df-4d09-ac62-696f0805a95c）
reviewer_kind: subagent
base_commit: 37f84bb895c9ef9b64e3865f3a92b245f2e28a7c
reviewed_head: beee351bb
decision: approved
---

# Review（r2）：FEA-12-DSIM-1（D 流程模拟切片）

**审查者身份与来源**：DSH 派发的独立上下文 fresh subagent（session `a39295f9-012b-401d-b35e-864c4c481d00`；父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c`）。**未参与**本卡实现、返修、Handoff 或证据生成；未参与 r1 审查（r1 session `fc7ffec8-b24b-418a-82f7-dcc99cb2a7dc`）。审查为**只读**：未 commit / push / stash / reset / checkout 他人改动；未修改仓库文件；仅向仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-dsim-r2\` 写日志、探针脚本与本报告；未触碰真实回收站、真实用户数据、AppData 业务数据或外部卷。

**被审对象**：`doc/tasks/FEA-12-DSIM-1.md`（status `in_review`；AC1–AC5 `<<MET>>`，AC2 已收窄）；r2 commits `d5925957b`（R-001 隔离写目标加固 + 8 项新测试）与 `beee351bb`（Task/Handoff/证据，18 files）；r1 被审 head `4a63c781a`、r1 Review `doc/reviews/FEA-12-DSIM-1-r1.md`（approved，P0/P1=0，P2=2，P3=7）；r2 reviewed_head `beee351bbcc6aa18eabe800bc7f5501385af9f3a`。

**并发写入声明（非本 Reviewer 所为）**：审查开始时 HEAD = `beee351bb`。审查期间其他 Agent 在共享工作树提交了 FEA-12-CORE shard B `9ebb812b0` 与 `fc7125586`（HEAD 现为 `fc7125586`），并留有 FEA-12-CORE shard A 未提交改动；`git diff beee351bb..HEAD -- <DSIM-1 文件>` 为空，**被审内容未被并发 commit 修改**。另：FEA-12-CORE 的未跟踪测试 `tests/fea12/test_core_delete_protection.py` 于 16:38:41 出现（在我 16:34 的定向复跑之后），故当前 `pytest tests/fea12` 会收集 32 项；定向文件复跑仍为 21 passed（见 §6）。本 Reviewer 对所有 `src/…/simulated_recycle_bin.py`、`tests/fea12/test_recycle_gateway_sim.py`、`verification/FEA-12-DSIM-1/**`、Task/Handoff 的 `git status` 为空；未 commit/push。并发改动、HEAD 推进与未跟踪测试均非本 Reviewer 所为，也不属于 r2 commit。

---

## 1. 结论

**decision: approved。P0=0，P1=0，P2=0，P3=3（均为证据/文档精度，不阻断集成）。**

- **R-001（P2）真实修复，已核销**：新增 `_assert_write_target` / `_assert_plain_component_walk`，在构造期与每次读写前校验 bin/manifest/journal；我独立复现预置/重植 junction、journal/manifest 硬链接、root 跨 junction、fs-root，均按预期拒绝且**根外零变化**；并做了一个判别性探针：把新校验在内存中禁用后，**r1 的 bin-junction 绕过精确复现**（根外出现移动文件与 manifest，状态 `moved`），证明 R-001 相关新测试不是空转（另 2 项 R-007 覆盖测试有各自行为断言）。21 passed，无 skip。
- **R-002（P2）真实消除，已核销**：`gates.log`/`check-final.log` 已从 evidence_dir 删除、迁至仓外 agent-output 并在 `agent-output-manifest.json`（EV-19）登记；我复跑 `check.ps1 -TaskPath` 为 **PASS（3 warnings，无 evidence_dir 告警）**；Resource Manifest 已改为 `PRESERVE_REFERENCED`。
- **R-003…R-009 均已逐项处置**，未发现“未处置写成已修”：R-007 的剩余缺口（manifest 写失败/损坏、journal 目录/符号链接）在 Handoff/AC-MATRIX 明确登记为残余风险，属诚实保留。
- **AC1–AC5 全部 MET**（AC2 为“限定”MET；AC5 的 .NET 数字引用 r1 稳定树，r2 尝试的 flaky 已如实分列）。实现仍在冻结范围内：无真实 Windows 回收站 API、无 Host/UI 接线、生产默认 typed 不可用、无依赖/schema/契约变更、无 push；真实 D 流程 **NOT_RUN** 声明保留。
- 仅有 3 项 P3 证据/文档精度问题（“零写入”措辞、Handoff 门禁数字与 full-pytest 命令串、3093/3073 基线标签），不改变代码安全性与 AC 判定；建议 closeout 前顺手修正，不要求返修代码。

| ID | 级别 | 摘要 | 状态 |
|---|---|---|---|
| R-001 | P2（r1） | bin/manifest/journal 可被预置 junction/hardlink 绕过隔离根 | **closed（已修，独立验证）** |
| R-002 | P2（r1） | evidence_dir 过程文件未登记（check warning） | **closed（已迁移/登记，check 无告警）** |
| P3-1 | P3（r2 新） | AC2/ISOLATION/AC-MATRIX “零写入”措辞过宽：重植拒绝前可能已写一条根内 journal attempt | open（文档精度） |
| P3-2 | P3（r2 新） | Handoff 门禁数字/命令串陈旧（“2 warnings/15 Task” vs 实际 3/13；full pytest `--tb=no` vs 日志头 `--tb=short`） | open（文档一致性） |
| P3-3 | P3（r2 新） | Task AC5 “基线（r1 交付 head）3093/10”与 EV-07 `baseline-pytest.log`（3073/10 @ 37f84bb89）标签需区分 | open（可追溯性） |

---

## 2. R-001 核销（隔离写目标加固）

### 2.1 代码核对（`src/infrastructure/filesystem/simulated_recycle_bin.py`）

| 要求 | 实现位置 | 核对结果 |
|---|---|---|
| 构造期校验自身 bin/manifest/journal | `SimulatedRecycleBin.__init__:359-374` → `_assert_write_targets:390-406`；`JsonLinesRecycleJournal.__init__:646-651` | ✅ gateway 校验三者；journal 校验自身 |
| 每次读写前复检 | `read_manifest:408-427`；`_recycle_one:505-515`（move 前 + mkdir 后）；`_write_manifest:621`；journal `read_records:666-675`、`_append:677-685` | ✅ 读、move、manifest 写、journal append/read 均复检 |
| abspath 包含 | `_assert_write_target:214-221`（`relative_to(root_absolute)`） | ✅ |
| 逐段 reparse 拒绝 | `_assert_write_target:222-232`（`lstat` + `_is_reparse_point`）；`_assert_plain_component_walk:177-195`（root 从 anchor 逐段） | ✅ |
| `realpath(target) ⊆ realpath(root)` | `_assert_write_target:233-238`（`os.path.realpath` + `_is_within`） | ✅ |
| 既有 manifest/journal 为普通文件且 `st_nlink<=1` | `_assert_write_target:239-258` | ✅ 硬链接拒绝；非普通文件拒绝 |
| typed 安全错误、根外零写入 | `RecycleSafetyError`（`recycle_gateway.py:93` 定义）；bin/manifest 校验在 move/mkdir/manifest 写之前抛出，journal 自身校验在 append 前抛出 | ✅ 根外零写入（见 2.2）；“零写入”措辞见 P3-1 |
| root 跨 junction / fs-root 拒绝 | `_assert_isolated_root:148-174`：fs-root 先拒绝，随后 `_assert_plain_component_walk:169-173` | ✅ 两者均拒绝 |

### 2.2 独立探针（仓外，非仓库；脚本与日志均留档）

探针 `G:\CODEX\New Manga.workspace\FEA-12\review-dsim-r2\probe-r001.py`，在仓外 scratch 内用**真实 NTFS junction**（`cmd /c mklink /J`）与**真实硬链接**（`os.link`）复现 r1 的攻击面：

| 场景 | 结果 |
|---|---|
| A 预置 `<root>/simulated-recyclebin` junction | 构造即 `RecycleSafetyError: … crosses a junction/symlink`；根外 sentinel 树 1→1 不变 |
| B 预置 journal 硬链接 | `JsonLinesRecycleJournal` 与 `SimulatedRecycleBin` 构造均 `RecycleSafetyError: … hard-linked`；根外文件字节不变 |
| C 预置 **manifest 硬链接**（测试套件未覆盖，额外核） | 构造即 `RecycleSafetyError: simulated bin manifest is hard-linked…` |
| D 构造后**重植 bin junction** + 非空选择 | move 时拒绝；根外新增 `[]`；原文件 `PAGE BYTES` 仍在原位；**根内 journal 已有 1 行 attempt**（P3-1 的事实依据） |
| E 构造后**重植 journal 硬链接** | append/read 均拒绝；根外 journal 仍为 `OUTSIDE`；原文件仍在 |
| F root 经由 junction 到达 | `UnsafeIsolatedRootError: … must not cross a junction/symlink` |
| G 文件系统根 | `UnsafeIsolatedRootError: filesystem root is not an isolated scratch root` |
| H **判别性反证**：内存中禁用 `_assert_write_targets` 后重复 r1 预置 bin junction | **绕过精确复现**：根外新增 `5416ba4c-page.png`、`recyclebin-manifest.json`，outcome `status=moved`。说明新测试的 `pytest.raises(RecycleSafetyError)` 断言确实依赖 r2 校验，去掉校验即失败 |

日志：`...\review-dsim-r2\logs\probe-r001.log`（EXIT 0，“unexpected bypasses: 0”；H 行为预期绕过）。探针 scratch 已清理，无 junction/hardlink 残留。

### 2.3 测试核对

- `tests/fea12/test_recycle_gateway_sim.py` 新增 8 项（`:771-924`）：`test_filesystem_root_is_refused`、`test_root_reached_through_a_junction_is_refused`、`test_preplanted_bin_dir_junction_is_refused_without_outside_writes`、`test_preplanted_journal_hardlink_is_refused_without_outside_writes`、`test_replanted_bin_dir_junction_is_refused_at_write_time`、`test_replanted_journal_hardlink_is_refused_at_write_time`、`test_verify_failed_rolls_back_to_the_original`、`test_entry_inside_the_simulated_bin_is_already_in_bin`。
- 真实 OS 对象：`_make_directory_junction:741-751` 使用 `cmd /c mklink /J`；`_make_hardlink:762-768` 使用 `os.link`；fixture 全在 `tmp_path`，`finally` 解除。
- 独立复跑 **21 passed**（无 skipped），证明 junction/hardlink 场景真实执行而非跳过。
- 判别性成立：A/D 若去掉校验会走成 `moved`（H 实证），B/C/E 的构造/追加会成功而不抛错；故这些断言不是同义反复。
- r2 diff 对测试文件为 **+198/−0**，未删除或放宽既有断言；代码文件 4 行删除仅为局部变量重构与 docstring。

### 2.4 R-001 结论

**closed**。r1 的 bin/manifest/journal 重定向缺口已在构造期与读写前被结构化拒绝，根外零写入，root 跨 junction/fs-root 拒绝，且测试具备判别力。残余是已声明的 TOCTOU 窗口（§8），不是 R-001 未修。

---

## 3. R-002 核销（evidence_dir 告警）

- `verification/FEA-12-DSIM-1/logs/gates.log`、`check-final.log` 已从 HEAD 删除（`git show --name-status beee351bb` 的 `D` 行；`git ls-tree beee351bb verification/FEA-12-DSIM-1` 不含两者）；仓外 `G:\CODEX\New Manga.workspace\agent-output\fea12-dsim-impl\FEA-12-DSIM-1\` 存在 `gates.log`、`check-final.log`、`check-final-r1.log`。
- `agent-output-manifest.json` 的 3 个文件 bytes/sha256 与仓外实际文件 **3/3 MATCH**；`source_root` 与 Resource Manifest 的 `PRESERVE_REFERENCED` 一致。
- 我独立复跑 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-DSIM-1.md`：**PASS (3 warnings)，EXIT 0**；warnings 为 13 个非终态 Task、STATUS 80%、PLAN 80%，**无 evidence_dir 告警**。`check.ps1:719-734` 的未登记文件检查确实生效；当前 evidence_dir 16 个文件全部在 EV 表中登记（EV-05…EV-18 + EV-19/EV-20；EV-01…EV-04 为代码路径）。r1 的 `check-final-r1.log` 仍保留在仓外，未被覆盖。
- Resource Manifest 已从 `NOT_APPLICABLE` 改为 `PRESERVE_REFERENCED`（Task:118-123），并写明逐文件 bytes/sha256 与“判别力证据仍以仓内为准”。

**closed**。

---

## 4. R-003…R-009 核销

| ID | r1 级 | r2 处置 | 独立核对 | 判定 |
|---|---|---|---|---|
| R-003 ENVIRONMENT 断链 + 漏 fix commit | P3 | 引用改为 `FEA-12-DSIM-1-d5925957b.md`；补列 `3d0d325f7`、`d5925957b` | `ENVIRONMENT.md:6-21`；Handoff 文件存在；三 commit 属实 | ✅ closed |
| R-004 ISOLATION 行数 840 陈旧 | P3 | 改为 r2 实测 **1020 lines** | 我复跑 static-scan：`2 modules / total lines = 1020`；`gates.log`/`static-scan.log` 一致 | ✅ closed |
| R-005 range 口径 | P3 | ENVIRONMENT 增 per-commit scope 表 | `94a12e93f` 5 files、`3d0d325f7` 1、`d5925957b` 2、`beee351bb` 18；全部命中 allowed_paths；range 另含 6 个其他任务/Lead commit（§7） | ✅ closed |
| R-006 .NET 首跑归因与日志不符 | P3 | 改为实测 diff（`FEA-12-PREREQ-1/tools/…` → `…/logs/…`） | `dotnet-full-1.log` 原文确为 `Expected …FEA-12-PREREQ-1/tools/rev213-diff-aud…` vs `Actual …/logs/rev213-diff-audi…`；Handoff/G3/AC-MATRIX 同步 | ✅ closed |
| R-007 覆盖缺口 | P3 | 新增 fs-root、真实 junction、rollback、already_in_bin；**明确保留** manifest 写失败/损坏、journal 目录/符号链接未入库 | 8 项新测试中 6 项 R-001 + 2 项 R-007；Handoff:108 / AC-MATRIX:34/43 如实登记剩余缺口 | ✅ 处置（部分，诚实保留） |
| R-008 AppData 措辞冲突 | P3 | ISOLATION §4 / ENVIRONMENT 改为“OS temp scratch ≠ 用户 AppData 业务数据”；不再使用“AppData 零操作”字面 | `ISOLATION-EVIDENCE.md:109`、`ENVIRONMENT.md:43`；我检索确认该字面只出现在“不再使用”的说明中 | ✅ closed |
| R-009 raw log provenance 头 | P3 | 10 个 raw log 均加 `# command/shell/python/head/captured/EXIT/summary` 头 | 10/10 存在头；EXIT/summary 与正文一致（见 §5、§6）；仅 full-pytest 命令串有 P3-2 小差异 | ✅ 基本 closed（附 P3-2） |

未发现把未处置项写成“已修”：R-007 的剩余场景在 Handoff:108、AC-MATRIX:34/43、ISOLATION §6 均明示未入库；R-001 的 TOCTOU 也在 Task:58、ISOLATION:46、AC-MATRIX:41 明示未消除。AC 标记与证据一致（AC2 为“MET（限定）”，AC5 引用 r1 稳定树并把 r2 flaky 单列）。

---

## 5. AC1–AC5 判定

| AC | 判定 | 依据与说明 |
|---|---|---|
| **AC1 协议与生产默认** | **MET** | `recycle_gateway.py:238-292`：`OriginalFileRecycleGateway.move_to_recyclebin(entries, *, journal)`；`UnavailableOriginalFileRecycleGateway` 逐项 `not_started/gateway_unavailable`、`operation_id=""`、不碰 journal/FS/DB；`test_production_default…` 在 21 passed 内；全 `src`/`apps` 仅 3 个文件出现端口名（两模块 + `maintenance/__init__.py`），无 Host/UI 引用。 |
| **AC2 模拟实现（限定）** | **MET（限定）** | 正常 `tmp_path` + 干净 root 下移动/manifest/journal 可审计；R-001 加固经 §2 独立验证；AC2/ISOLATION/AC-MATRIX 已明确“不再声称任何情况下全部写入都在隔离根内”，登记 TOCTOU/单写者。**限定成立**；措辞“零写入”有过宽处（P3-1）。 |
| **AC3 失败语义** | **MET** | `test_failure_injection…`、`test_missing_selection…`、`test_verify_failed_rolls_back…`、AST 测试均在 21 passed 内；注入失败原文件字节/集合不变、typed `failed`、失败项不进 manifest；`verify_failed` 回滚恢复；两模块零 unlink/rmtree/DB/进程；application 零变更型调用。 |
| **AC4 隔离与禁令** | **MET** | 我复跑 static-scan：`src 256 + apps 510 = 766 files / 0 API hits`；`tests/fea12` 2 files（并发前）/0 真实路径字面量；2 模块 1020 lines / 0 删除/DB/进程；运行时哨兵 `PASS … outside changes: []`；测试无 `%APPDATA%`/真实盘符/真实 `$Recycle.Bin` 字面量。 |
| **AC5 交付件与门禁** | **MET（引用 + 已归因）** | fea12 21 passed（独立复跑）；全量 pytest 交付日志 `3101 passed / 10 skipped`（原文 + 头，EV-06 哈希匹配）；.NET r2 尝试 `1 failed/670 passed/7 skipped`（`dotnet-r2-1.log`，EV-20）且 **r2 无 .NET 改动**，引用 r1 稳定树 `0 failed/1403 passed/79 skipped`（`dotnet-full-3.log`，EV-08）；pins 18/18（独立复跑）；check PASS 3 warnings、无 evidence_dir（独立复跑）。 |

---

## 6. 独立复跑（只读；日志写仓外）

所有复跑在 `G:\CODEX\New Manga`（开始时 HEAD `beee351bb`；期间其他 Agent 推进至 `fc7125586`，DSIM 文件 delta 为空）执行。日志目录：`G:\CODEX\New Manga.workspace\FEA-12\review-dsim-r2\logs\`。

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| fea12 pytest（reviewed head 时） | `C:/Python314/python.exe -m pytest tests/fea12 -q -p no:warnings -p no:cacheprovider --tb=no` | **21 passed，EXIT 0**（16:34，当时 `tests/fea12` 仅 2 个 py 文件） | `pytest-fea12-review.log` |
| fea12 定向复跑（并发文件出现后） | 同上，仅 `tests/fea12/test_recycle_gateway_sim.py` | **21 passed，EXIT 0**（当前 HEAD，DSIM 内容不变） | `pytest-dsim-file-after-concurrency.log` |
| 静态扫描 | `pwsh -NoProfile -File verification/FEA-12-DSIM-1/tools/static-scan.ps1` | **PASS，EXIT 0**：766 files / 0 API；2 test files / 0 literals；2 modules **1020** lines / 0 fallback | `static-scan-review.log` |
| 静态扫描（并发后复核） | 同上 | **PASS**：766 files / 0 API；3 test files（含 CORE 新文件）/ 0 literals；2 modules 1020 / 0 fallback | `static-scan-review-after-concurrency.log` |
| 哨兵 | `C:/Python314/python.exe verification/FEA-12-DSIM-1/tools/sentinel-probe.py` | **PASS，EXIT 0**：run1 moved=1、run2 failed/in_use 原文件保留、run3 not_started；`outside changes: []` | `sentinel-probe-review.log` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (all 18)，EXIT 0** | `verify-pins-review.log` |
| 治理 check | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-DSIM-1.md` | **PASS (3 warnings)，EXIT 0**；无 evidence_dir 告警 | `check-review.log`；并发后复跑 `check-review-after-concurrency.log` 同为 3 warnings |
| R-001 判别探针（我新增） | `C:/Python314/python.exe ...\probe-r001.py` | **A–G 全拒绝、根外零变化；H 禁用校验后绕过复现**；unexpected bypasses: 0 | `probe-r001.log` |
| 全量 pytest / .NET | **未重跑**，引用交付日志 | 全量 pytest `3101 passed/10 skipped`（EV-06）；.NET r2 尝试 `1/670/7`（EV-20），r1 稳定树 `0/1403/79`（EV-08） | 交付日志哈希 16/16 匹配 |

**未重跑全量 pytest/.NET 的理由**：①当前共享工作树含 FEA-12-CORE 未提交改动与未跟踪测试（非本卡、非本 Reviewer），全量 pytest 会测到混合树，无法给出比交付日志更干净的数字；②全量 .NET 会重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`（`WireLogSourceRedactionTests.cs:33`），且 `FluentResidual2VisualEvidenceTests` 的 `git status --verification` 断言（`:52/:106`）在并发写入窗口内必然 flaky，交付的 r2 尝试日志已如实记录 EXIT 1 并归因；③r2 commit 对 `.cs` 零改动，引用 r1 稳定树在方法上成立；④交付日志与 EV 哈希匹配、总量已逐项复核。**未运行 .NET，因此无需（也未执行）`git checkout -- verification/FEA-09`；当前 worktree 的 FEA-09 改动为其他 Agent 所有，本 Reviewer 未触碰。**

**并发/AppData 声明**：复跑期间 `tests/fea12` 新增了 FEA-12-CORE 的未跟踪测试（16:38:41，11 tests），故现在直接运行 `pytest tests/fea12` 会收集 32 项；这是并发污染，不是 r2 交付内容。哨兵脚本按交付实现使用 `tempfile.TemporaryDirectory()`（物理位于 `C:\Users\<user>\AppData\Local\Temp`，自清理），与 pytest `tmp_path` 同族；未读写用户 AppData 业务数据、未触碰真实回收站/外部卷。

---

## 7. 范围、冻结与边界核对

- **per-commit scope**：`94a12e93f`（5 files：两新增模块 + additive `__init__` + conftest + test）、`3d0d325f7`（1 file）、`d5925957b`（2 files）、`beee351bb`（18 files：Task、Handoff、`verification/FEA-12-DSIM-1/**`）。逐一命中 `allowed_paths`；未发现 r2 自有 commit 改 allowed_paths 之外的文件。
- **range 口径**：`4a63c781a..beee351bb` 共 **8 个 commit**（f11bff37e、41ff156a4、451e175a9、e47fd47e4、c8d9adc8d、ab95c906e、d5925957b、beee351bb）。除 DSIM 的两个 commit 外，其余为 FEA-11-LINEAGE-1、FEA-12-PREREQ-1、FEA-12-CORE 与 Lead 指针 commit；因此**range 级“仅 allowed_paths”不成立**（与 r1 R-005 一致，ENVIRONMENT 已说明），但 **DSIM 自有 commit 的 per-commit 断言成立**。
- **冻结/生产路径**：`git diff 4a63c781a..beee351bb -- doc/plan doc/contracts apps pyproject.toml requirements.txt verification/FEA-09` **零 diff**；无 schema/migration、无新依赖（r2 仅 stdlib `stat` 等既有 import）；无 Host/UI 接线（端口名只在 3 个文件出现）。
- **回收站 API 禁令**：static-scan 766/0；另以更宽 token（SHFileOperation/IFileOperation/Shell32/Microsoft.VisualBasic/Windows.Storage/send2trash/winshell/win32com/Shell.Application/FOF_ALLOWUNDO/FileSystem.DeleteFile/SHNotify/Recycle.Bin）复核 `src`+`apps`，只命中产品领域词（如 `ListRecycleBinBooks`/`RecycleBinPage`）与 DSIM 自身标识符（`SimulatedRecycleBin`/`RecycleBinEntry`/`recycle.bin` 目录名拒绝逻辑），无真实 OS 回收站调用。
- **生产默认**：`UnavailableOriginalFileRecycleGateway` typed 不可用、零操作；`SimulatedRecycleBin` 仅测试替身，不被 Host/UI 引用。
- **真实 D**：Task:89、Handoff 风险 1、AC-MATRIX:21、ISOLATION §6 均保留 **NOT_RUN**；未发现“D 已完成”的表述。
- **未 push**：`git branch -r --contains beee351bb` 为空；`git merge-base --is-ancestor beee351bb origin/main` 为假；`main` 无 upstream。r2 commit 只在本地。
- **Canonical Evidence**：我用 `Get-FileHash` 复核 EV-05…EV-20 **16/16 MATCH**（含 EV-19 manifest、EV-20 r2 dotnet 日志）；交付 `pytest-fea12.log`/`pytest-full.log`/`dotnet-full-3.log`/`dotnet-r2-1.log` 的正文总量与头一致（21；3101/10；1403/0/79；1/670/7）。
- **并发边界**：本 Reviewer 对 DSIM 文件 `git status` 为空；`HEAD` 推进、`tests/fea12/test_core_delete_protection.py`、FEA-09 日志改动均属其他 Agent，未被我修改或提交。

---

## 8. 残余风险（不阻断，需在真实桥/closeout 前知悉）

1. **TOCTOU（已声明）**：`_assert_write_target` 与写入是两次系统调用；构造后重植 bin/journal、或替换 root 自身，仍可能在检查与写入之间发生。单写者测试替身假设；真实 OS 桥必须绑定句柄并保持单写者纪律。
2. **崩溃恢复未实现**：移动成功但 manifest/receipt 写失败时无回滚；journal 可能只有 attempt、无 receipt。属 SC-34 真实桥任务。
3. **覆盖缺口（已登记）**：manifest 写失败/损坏、journal 目录/符号链接未入库；选中文件夹内 junction 已由代码拒绝但无 OS 级测试。
4. **“零写入”措辞**：重植拒绝发生在 journal attempt 之后时，隔离根内会留下 1 条 attempt（P3-1）；根外仍零写入，安全性质不受影响。
5. **root 校验保守**：root 路径任一段为 junction 即拒绝；在用户 temp 被重定向的机器上会 fail-closed（可能是测试环境问题），符合隔离优先。
6. **.NET 外部 flaky**：`FluentResidual2VisualEvidenceTests` 与 `WireLogSourceRedactionTests` 的 git-status 窗口由既有测试互相触发；r2 无 .NET 改动，建议集成复跑时保留首跑+复跑证据。
7. **模拟 ≠ 真实 D**：真实 Windows 回收站行为 **NOT_RUN**，需用户另行授权；本卡不能作为 D 完成依据。
8. **证据精度**：P3-1/P3-2/P3-3 为文档/标签层面，不影响代码与门禁结论。

---

## 9. P3 明细与最小返修点（不代改代码）

| ID | 位置 | 事实 | 最小动作 |
|---|---|---|---|
| **P3-1** | `doc/tasks/FEA-12-DSIM-1.md:58`；`verification/FEA-12-DSIM-1/ISOLATION-EVIDENCE.md:43`；`AC-MATRIX.md:13` | “零写入（不移动、不建目录、不写 journal/manifest）”在“构造后重植 bin junction”场景不成立：`move_to_recyclebin` 先 `journal.record_attempt`（根内 1 行），再在 `_recycle_one` 复检时抛 `RecycleSafetyError`（我的探针 D）。**根外仍零写入**，安全性质成立 | 改成“零根外写入；被拒目标不写；若拒绝发生在 attempt 之后，隔离根内可能保留一条 attempt journal”。若想字面成立，可在 `move_to_recyclebin` 开头先调用 `_assert_write_targets()`（可选代码改动；不影响现有测试） |
| **P3-2** | `doc/handoffs/FEA-12-DSIM-1-d5925957b.md:80`、`:111`、`:48-49` | `:80` 写“应 2 warnings”；`:111` 写“2 warnings（15 非终态 Task、PLAN 80%）”；实际 `check.ps1` 为 **3 warnings / 13 非终态 Task / STATUS 80% / PLAN 80%**（我的复跑、`check-final.log`、`gates.log:71-75`、Task:76 一致）。另 `:48-49` full pytest 命令写 `--tb=no`，而 raw log 头与 `gates.log:24` 为 `--tb=short` | 更新 Handoff 两处为 3/13/STATUS/PLAN；full pytest 命令串与 raw log 头对齐（保留 `--tb=short` 或注明实际命令） |
| **P3-3** | `doc/tasks/FEA-12-DSIM-1.md:76`（AC5 行）；EV-07 `baseline-pytest.log` | AC5 写“基线（r1 交付 head）3093/10”，但 EV-07 原文是 `head 37f84bb89` 的 **3073/10**；3093 的出处是 r1 Handoff:44 / r1 Review:192（本轮未重跑），`gates.log:26-29` 已注明引用。非错误，但审计易误读 | 把 3073/10 标为“base 37f84bb89（EV-07）”、3093/10 标为“r1 交付 head，引用 r1 Handoff/Review，未重跑”；或在 Task AC5 行引用 `gates.log` 的说明 |

其他小注（不计 finding）：Task:90 把“8 项新判别测试”放在 R-001 句内，实际为 R-001 6 项 + R-007 2 项；`AC-MATRIX.md:28` 已按 6 项拆分，Handoff:31 的 8 项列表也覆盖两类，属表述粒度问题。

---

## 10. done vs changes 意见

**approved（可交 DSH 集成/closeout），不建议 changes_requested。** 理由：r1 的两个 P2 均真实修复并可独立复现；无 P0/P1/P2 残留；AC1–AC5 证据可复核；范围、冻结、禁令、未 push、NOT_RUN 均守住；21 passed、766/0、1020 lines、哨兵 PASS、pins 18/18、check PASS 无 evidence_dir 告警均由我独立复跑确认。P3-1/P3-2/P3-3 是证据/文档精度，建议 closeout 前顺手修正（不要求返修代码）；若 Lead 对 AC2 采用“任何可疑状态都必须零写入（含 journal attempt）”的字面解释，则应先做 P3-1 的可选代码小改或在 AC2 明确限定，但这不改变本次代码安全结论。

**集成建议**：保留 r1 Review、r2 Handoff、`agent-output-manifest.json` 与 `verification/FEA-12-DSIM-1/logs/**` 的原字节；closeout 时把 `canonical_evidence_status`/`resource_closeout_status` 从 `pending` 收口，并在 STATUS/PLAN/Ledger 记录 r2 approved；不要把 `tests/fea12/test_core_delete_protection.py`（FEA-12-CORE 未跟踪）误算入 DSIM-1。

---

## 11. 自审声明

本人为 DSH 派发的**独立上下文 fresh subagent**（session `a39295f9-012b-401d-b35e-864c4c481d00`；父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c`），**未参与** FEA-12-DSIM-1 的任何实现、返修、Handoff 或证据生成，也未参与 r1 审查；审查对象仅 `reviewed_head=beee351bb`（及其中 `d5925957b`）。审查只读：未 commit/push/stash/reset/checkout 他人改动；未修改仓库文件（`git status` 对 DSIM 文件为空；`tests/fea12/__pycache__` 时间戳早于本次审查，未被本次运行改写）；所有写入在仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-dsim-r2\`；未触碰真实回收站、真实用户数据、AppData 业务数据或外部卷；探针 scratch 已清理、无 junction/hardlink 残留。审查期间 HEAD 推进至 `fc7125586`、FEA-12-CORE 未提交改动与 `tests/fea12/test_core_delete_protection.py` 出现，均为其他 Agent 的并发写入，非本人所为；`git diff beee351bb..HEAD -- <DSIM 文件>` 为空，本报告结论只对 `beee351bb` 有效。

**最终决定：approved**（P0=0，P1=0，P2=0，P3=3：零写入措辞、Handoff 门禁数字/命令串、3093/3073 基线标签；均为非阻断证据精度项）。真实 Windows 回收站行为仍为 **NOT_RUN**，需用户另行专门授权。
