---
task_id: FEA-12-DSIM-1
reviewer: DSH 独立上下文 fresh subagent（session `fc7ffec8-b24b-418a-82f7-dcc99cb2a7dc`；父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c`）
reviewer_kind: subagent
base_commit: 37f84bb895c9ef9b64e3865f3a92b245f2e28a7c
reviewed_head: 4a63c781a
decision: approved
---

# Review：FEA-12-DSIM-1（D 流程模拟切片）

**审查者身份与来源**：DSH 派发的独立上下文 fresh subagent（session `fc7ffec8-b24b-418a-82f7-dcc99cb2a7dc`；父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c`）。未参与本卡实现、Handoff 或证据生成。审查为**只读**：未 commit / push / stash / reset / checkout 他人改动；仅向仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-dsim\` 写日志与本报告；未触碰真实回收站、真实用户数据、外部卷。

**被审对象**：`doc/tasks/FEA-12-DSIM-1.md`（status `in_review`；AC1–AC5 `<<MET>>`；EV-01…EV-18）；实现 commits `94a12e93f`（协议/模拟件/测试）、`3d0d325f7`（目录指纹 junction 拒绝 + normcase）、docs commit `4a63c781a`；base `37f84bb89`；reviewed_head `4a63c781a`。

**并发写入声明（非本 Reviewer 所为）**：审查开始及全部复跑期间，仓库 HEAD 为 `4a63c781a`、`git status` clean。约 16:05–16:07 的最终检查时，其他 Agent 在共享工作树推进了 HEAD 至 `f11bff37e`（`docs(fea-11-lineage-1): r3 Review 落盘…`，仅 `doc/TASK_LEDGER.md`、`doc/reviews/FEA-11-LINEAGE-1-r3.md`、`doc/tasks/FEA-11-LINEAGE-1.md` 3 files），并留下未跟踪的 `doc/reviews/FEA-12-PREREQ-1-r2.md`；两者均为**其他任务**的并发写入，不是本 Reviewer 所为，未改 FEA-12-DSIM-1 的 `src/**`/`tests/fea12/**`/`verification/FEA-12-DSIM-1/**`。本 Review 的结论只对 `reviewed_head=4a63c781a` 有效；HEAD 推进后本文件按模板自动属于该 head 的历史 Review。

---

## 1. 结论

**decision: approved。P0=0，P1=0，P2=2，P3=7。**

实现方向与冻结范围一致：application 端口 + 生产 typed 不可用默认实现 + `SimulatedRecycleBin` 测试替身 + 隔离/静态/哨兵测试；无真实 Windows 回收站 API、无 Host/UI 接线、无既有生产路径改造、无 schema/依赖、无冻结契约 diff。关键门禁可独立复核：`pytest tests/fea12` 13 passed、静态扫描 766 files/0 API、哨兵 PASS、pins 18/18、`check.ps1` PASS（3 warnings）。

**但有 2 个 P2 需在 DONE 前处置**：

1. **R-001（隔离加固缺口）**：`SimulatedRecycleBin` 只校验“条目路径”的 junction/symlink，**未校验自身 `_bin_dir`、manifest 路径、journal 路径**；我实测预置 `<root>/simulated-recyclebin` junction 可让 `os.replace` 与 manifest 写**落到隔离根之外**，预置 `recyclebin-journal.jsonl` 硬链接可使 journal 追加写到根外文件。生产默认实现不可用、`SimulatedRecycleBin` 仅测试替身，且需要调用者 scratch root 内预先存在 reparse/hardlink，因此定级 P2（纵深防御/AC 表述精度），不是 P1；但 AC2 的“全部写入都在隔离根内”在字面上不成立，必须修或在 DONE 前把 AC2/ISOLATION-EVIDENCE 的表述收窄并登记残余风险。
2. **R-002（closeout 门禁）**：`check.ps1` 的 3 个 warning 之一是 `verification/FEA-12-DSIM-1/logs/{gates.log,check-final.log}` 未登记过程文件；Handoff 已自认，DONE 前应移入 workspace agent-output 或补列 SOURCE_PIN，并同步 Resource Manifest。

其余 P3 为证据精度/覆盖建议（ENVIRONMENT 断链、ISOLATION 行数陈旧、range 口径、.NET 首跑归因、覆盖缺口、AppData 表述、日志头），不阻断集成。

| ID | 级别 | 摘要 | 状态 |
|---|---|---|---|
| R-001 | **P2** | bin-dir/manifest/journal 可被预置 junction/hardlink 绕过隔离根 | open（DONE 前处置） |
| R-002 | **P2** | evidence_dir 过程文件未登记（check warning 3） | open（closeout） |
| R-003 | P3 | ENVIRONMENT 引用不存在的 Handoff 文件名，且漏列 fix commit | open |
| R-004 | P3 | ISOLATION-EVIDENCE 写 840 lines，实际 876 | open |
| R-005 | P3 | `base..head` range 含 7 个其他任务 commit + Lead 指针 commit；应给 per-commit scope 证明 | open |
| R-006 | P3 | .NET 首跑 flaky 归因与 `dotnet-full-1.log` 实际 diff 不符 | open |
| R-007 | P3 | 测试未覆盖 fs-root 拒绝、真实 junction、rollback/manifest 失败等 | open（建议） |
| R-008 | P3 | “AppData 零操作”与 sentinel 使用 OS temp（`AppData\Local\Temp`）字面冲突 | open（建议改写） |
| R-009 | P3 | 原始日志缺 EXIT/shell/venv 头（Q-009 证据纪律） | open（建议） |

---

## 2. 范围与边界

### 2.1 commit 层级

`git log --oneline --reverse 37f84bb89..4a63c781a` 共 **11 个 commit**，其中本卡自有 **4 个**：

| commit | 内容 | 文件 |
|---|---|---|
| `94a12e93f` | feat：协议 + 模拟件 + 测试 | 5 files / +1625：`src/application/maintenance/{__init__.py,recycle_gateway.py}`、`src/infrastructure/filesystem/simulated_recycle_bin.py`、`tests/fea12/{conftest.py,test_recycle_gateway_sim.py}` |
| `3d0d325f7` | fix：`os.walk(followlinks=False)` + reparse 拒绝 + normcase | 1 file / +54/−18：`simulated_recycle_bin.py` |
| `144683876` | Lead/生命周期：DSIM-1 转 in_review | `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/TASK_LEDGER.md`（**不在本卡 allowed_paths**；ADJ-2026-11-05 §D6 明确“Lead 保留 STATUS/PLAN/TASK_LEDGER/集成/commit”） |
| `4a63c781a` | docs/evidence | 18 files：Task 卡、Handoff、`verification/FEA-12-DSIM-1/**`（全部在 allowed_paths） |

**逐 commit 结论**：`94a12e93f` 与 `3d0d325f7` 只触 allowed_paths 内文件；`4a63c781a` 全部在 allowed_paths；`144683876` 为 Lead-owned 指针 commit。**未发现本卡实现 commit 改既有生产路径、接 Host/UI、改契约/schema/依赖、或越权写其他任务文件。**

### 2.2 range 口径（严格检查失败，但不是本卡越界）

`git diff --name-status 37f84bb89..4a63c781a` = **65 entries / 11 commits**，按顶层目录：`apps` 2、`doc` 10、`src` 10、`tests` 6、`verification` 37。该范围**不是**本卡单独 delta，还含：

- `FEA-12-PREREQ-1` r1/r2：`doc/reviews/FEA-12-PREREQ-1-r1.md`、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`、2 个 `CommandWiringB*Tests.cs`、`verification/FEA-12-PREREQ-1/**`；
- `FEA-11-LINEAGE-1` r3：`src/application/{rendering,sources,tasks}/**`、`src/bootstrap/core_assembly.py`、`src/infrastructure/{providers,sqlite}/**`、`tests/fea11/**`；
- 本文档/证据指针 commit。

因此“`base..head` 全部在 allowed_paths 内”这一**range 级**断言不成立；但 **DSIM-1 自有 commit 的 per-commit 断言成立**（见 2.1）。这与 PREREQ-1 r1 Review 的同类观察一致（该 Review §“范围与冻结核对”已指出 range 含其他任务 commit）。建议在 Task/Handoff 中补一行 per-commit scope 证明，避免后续审计把 range 误读为本卡 delta（R-005）。

### 2.3 冻结面 / 生产路径 / 依赖

- `git diff 37f84bb89..4a63c781a -- doc/plan`：**零 diff**（18 pinned 契约全在其中）。
- `git diff ... -- doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md`：**零 diff**。
- `doc/contracts/` 仅 `M2-C1_TYPED_IPC_CONTRACT.md` 变化，来自 **`26775dfef`（PREREQ-1 r2）**，不是 DSIM-1 commit。
- `verification/FEA-09`：base..head **零 diff**；工作树 clean，未见被测试重写的 tracked 证据。
- `apps/**`：DSIM-1 commit **零 diff**；range 内 2 个 `.cs` 测试文件来自 PREREQ-1 r2。
- 无 `pyproject.toml`/requirements/依赖变化；无 schema/migration；无新 worktree（`git worktree list` 无 DSIM-1）；未 push（`origin/main..HEAD` 有 18 个未推送 commit，含本卡与其他任务；`main` 无 upstream）。

---

## 3. D 流程边界（关键）

### 3.1 协议与生产默认实现

- `OriginalFileRecycleGateway`：`src/application/maintenance/recycle_gateway.py:250-266`，`move_to_recyclebin(entries, *, journal)`；`journal` keyword-only 且无默认值（C-01b SC-34 seam）。`RecycleItemOutcome`/`RecycleOutcome` 为逐项 typed 结果，`moved`/`failed`/`not_started` 与封闭 reason 词表在构造期校验（`recycle_gateway.py:124-152`、`:69-85`）。
- 生产默认 `UnavailableOriginalFileRecycleGateway`（`:269-292`）：对每个 entry 返回 `not_started + gateway_unavailable`、`operation_id=""`；**不调用 journal、不碰文件系统、不碰 DB、不降级永久删除**。测试 `test_production_default_is_typed_unavailable_with_zero_side_effects` 用 `_RecordingJournal` 和全树快照证明零副作用（`tests/fea12/test_recycle_gateway_sim.py:257-295`）。
- application 模块只 import stdlib，不 import `infrastructure`/`bootstrap`/`ports`；AST 断言在 `test_d_failure_cannot_degrade_to_permanent_delete__static_ast`（`:500-566`）。
- **未接 Host/UI**：`grep` 全 `src/**` 与 `apps/**` 仅 `maintenance/__init__.py` 与两个新模块自身出现名字；`test_no_production_file_references_the_d_flow_port`（`:298-324`）用精确集合断言，无生产引用。

### 3.2 无真实 Windows 回收站 API / 无 C 流程回退

- 静态扫描（独立复跑）：`src` 256 + `apps` 510 = **766 files / 0 API hits**；token 覆盖 `shfileoperation`、`shfileopstruct`、`ifileoperation`、`ifileoperationprogresssink`、`shell32`、`microsoft.visualbasic`、`windows.storage`、`send2trash`、`winshell`、`win32com`、`shell.application`、`fof_allowundo`（`verification/FEA-12-DSIM-1/tools/static-scan.ps1:44-49`；日志 `logs/static-scan.log:7`）。
- 两个 D 模块 AST：无 `unlink`/`rmtree`/`rmdir`/`remove`/`remove_managed`/`purge_*`/`permanently_delete`/`Popen`/`system`，无 `sqlite3`/`subprocess`/`ctypes`/`winreg`/`pythoncom`/`win32`/`send2trash`/`winshell` 导入；application 模块零 mutating call（`tests/fea12/test_recycle_gateway_sim.py:500-566`）。静态扫描另以 `rmtree(`/`unlink(`/`os.remove(`/`os.unlink(`/`os.rmdir(`/`sqlite`/`subprocess`/`ctypes`/`winreg`/`os.system(` 复核两个模块（`static-scan.log:14-19`）。
- 失败语义：注入 `in_use` 时，失败项原文件仍在原位、字节相同、不进 manifest；成功项才移动；全树快照差集只有成功项离开原位（`test_recycle_gateway_sim.py:446-497`）。`_rollback` 只在源路径可恢复时把 `stored` `os.replace` 回原位；源路径已被重建或 `stored` 不存在时抛 `RecycleSafetyError`，拒绝把未知位置谎报为“原文件仍在”（`simulated_recycle_bin.py:460-473`、`:93-102`）。我另用仓外探针实测 `_verify_moved=False` 时：`failed/verify_failed`、原文件恢复、manifest 为空（`logs/rollback-probe.log`）。
- **未声称 D 完成**：Task 卡 `:89`、Handoff `:95`、`AC-MATRIX.md:17-22`、`ISOLATION-EVIDENCE.md:4/93-98` 均明确“真实 Windows 回收站 NOT_RUN、需另行授权”；未发现把模拟写成真实 D 完成的表述。

---

## 4. 隔离与安全（逐条）

### 4.1 根校验

`_assert_isolated_root`（`simulated_recycle_bin.py:135-156`）：
- 拒绝文件系统根（`resolved.parent == resolved`）；我以只读方式实测 `SimulatedRecycleBin(Path('G:\\'))` 抛 `UnsafeIsolatedRootError: filesystem root is not an isolated scratch root`；
- 拒绝不存在、非目录；
- 拒绝任一路径段以 `recycle.bin` 结尾（含 `$Recycle.Bin`）；
- **不拒绝**根本身是 junction/symlink，也不拒绝根位于真实用户目录；由于条目 containment 使用“未解析 baseline + 解析后复查”，根为 reparse 时条目会 fail-closed（全部 `outside_isolated_root`），但构造阶段不报错。属残余风险/P3（见 §8）。

测试 `test_simulated_bin_refuses_non_isolated_roots`（`:428-438`）覆盖“不存在/`$Recycle.Bin`/非目录”，**未覆盖文件系统根**（代码路径未测；R-007）。

### 4.2 条目路径包含 / `..` / reparse walk

`_confine`（`:407-442`）：
1. 必须是绝对路径；
2. `raw.replace("\\","/").split("/")` 后拒绝空段、`.`、`..`（`segments[1:]`）；
3. 以 `os.path.abspath(root)`（**不解析**）为 baseline 做 `relative_to`；
4. 从 `self._root` 起对未解析路径逐段 `lstat`，任一段 `_is_reparse_point` → `outside_isolated_root`；
5. `absolute.resolve()` 后再做一次 `relative_to(baseline)` 包含复查。

`_is_reparse_point` 用 `st_file_attributes & FILE_ATTRIBUTE_REPARSE_POINT`（Windows）或 `S_ISLNK`（POSIX），对目录条目 junction/symlink 有效；`_fingerprint` 的 `os.walk(followlinks=False)` 对选中文件夹内每一级目录/文件做 reparse 拒绝（`:170-213`）。我实测“选中文件夹内含 junction”返回 `failed/unsupported_entry`，原文件夹与其中普通文件保持原位（`logs/rollback-probe.log`）。路径比较用 `os.path.normcase(os.path.abspath(...))`（`:228-243`）；Python 3.14 的 `Path.relative_to` 在 Windows 上大小写不敏感（我实测 `g:\...` 与 `G:\...` 返回 `.`），修复有效。

### 4.3 移动 / 复核 / 回滚 / manifest

- 逐项 `os.replace(source, stored)`，`stored` 在 `_bin_dir` 内（`:386-390`），同根同卷；单文件/目录均逐项原子。
- 移动前 `_fingerprint` 记录 `(kind, size, sha256)`；移动后 `_verify_moved` 检查源路径已不存在 + 目标指纹一致（`:444-458`）；失败回滚（`:391-393`、`:460-473`）。
- manifest（`simulated-recyclebin/recyclebin-manifest.json`）记录 `request_id`/`original_path`/`stored_path`/`kind`/`size_bytes`/`sha256`/`moved_at`；写入用临时文件 + `os.replace` + fsync（`:475-497`）。journal 为 append-only JSONL，attempt 在移动前、receipt 在验证后，逐行 fsync（`:504-541`）。测试验证 manifest 自描述、journal attempt/receipt 顺序与 operation_id 一致（`test_recycle_gateway_sim.py:384-409`）。
- 无 `unlink`/`rmtree`；D 失败不转永久删除。注意：若 `_append_manifest_entry`/`record_receipt` 在移动成功后抛错，代码不会回滚（异常上抛，journal 只有 attempt、无 receipt）；这不是 `failed` 路径，属崩溃恢复/真实桥的残余风险（§8），不是 C 回退。

### 4.4 R-001：隔离根写入目标可被预置 junction/hardlink 绕过（P2）

**代码缺口**：
- `SimulatedRecycleBin.__init__` 只对 `isolated_root` 调 `_assert_isolated_root`（`:264`），**未对 `_bin_dir`**（`root/simulated-recyclebin`，`:265`）做 reparse 检查；
- `_recycle_one` 的 `stored = self._bin_dir / f"{uuid...}-{source.name}"` 与 `os.replace`（`:386-390`）会跟随 `_bin_dir` 的 junction；
- `_write_manifest`（`:488-497`）在 `_bin_dir` 内建 temp 并 `os.replace` 到 manifest，同样跟随 junction；
- `JsonLinesRecycleJournal.__init__`（`:512-514`）只校验 root，`_append`（`:536-541`）直接 `open(path, "a")`；若 `recyclebin-journal.jsonl` 是预置硬链接/符号链接，追加会落到根外文件；
- `_confine` 只保护“被选中条目”的路径，不保护 gateway 自身写目标。

**实测（仓外 temp，非仓库）**：
- `<root>/simulated-recyclebin` 建成指向 `outside-bin` 的 junction；移动 `root/victim.png` → outcome `moved=1`，`outside-bin/8bfe6f9f-victim.png` 与 `outside-bin/recyclebin-manifest.json` 出现，根外路径被写入；
- `<root>/recyclebin-journal.jsonl` 建成指向 `outside-journal.txt` 的硬链接；`record_attempt` 后 outside 文件内容被追加；
- 证据：`G:\CODEX\New Manga.workspace\FEA-12\review-dsim\logs\isolation-bypass-probe.log`；探针脚本 `...\probe\probe.py`。

**影响**：AC2 / `ISOLATION-EVIDENCE.md:26-27` 的“全部写入都在隔离根内”不是结构上无条件成立；恶意/误置 reparse/hardlink 可让测试替身写根外（甚至覆盖 junction 目标中同名 `recyclebin-manifest.json`）。但：生产默认是 typed unavailable，`SimulatedRecycleBin` 仅测试替身、不被 Host/UI 引用；利用需要调用者 scratch root 内预先存在 junction/hardlink。故定级 **P2（纵深防御/AC 表述精度）**，不是 P1；若 DSH 把 AC2 当全称命题，则应把 AC2 降为 PARTIAL 并先修。

**最小返修**（不要求本 Reviewer 改代码）：
- 构造期/写入前校验 `_bin_dir`、manifest、journal 均非 reparse/link，且 `os.path.realpath` 位于 `os.path.realpath(root)` 下；对 journal 额外拒绝 `st_nlink > 1`（硬链接）；拒绝 root 本身 reparse。
- 增加判别性测试：`tmp_path` 内用 junction（Windows `mklink /J`）和硬链接各一条，期望 `failed`/构造拒绝且根外零变化；或至少在 Handoff/AC 中把“结构保证”收窄为“假定调用者提供的 root 及其内部无预置 reparse/hardlink”。
- 若选择不修，DONE 前必须把 AC2/ISOLATION-EVIDENCE 的表述改为限定条件，并登记残余风险，不能继续写“全部写入都在隔离根内”。

---

## 5. 测试判别力

`tests/fea12/test_recycle_gateway_sim.py` 共 **13 tests**（我 `--collect-only` 收集为 13；独立复跑 13 passed），全部 `tmp_path` 隔离；**无 skip/xfail、无 fake repo、无 `__new__`、无 monkeypatch/放宽断言**。覆盖：

| 场景 | test | 判别点 |
|---|---|---|
| 协议/封闭词表 | `:225` | runtime_checkable isinstance；keyword-only `journal`；未知 status/reason 构造期 `ValueError` |
| 生产默认零副作用 | `:257` | 全树快照、`_RecordingJournal` attempts/receipts 为空、无 bin/journal、safe projection 无路径 |
| 无 Host/UI 引用 | `:298` | 精确集合匹配，仅 port/`__init__`/simulated 三个文件出现名字 |
| 成功模拟/可审计 | `:332` | 文件+目录进 manifest、字节/SHA-256/kind、stored 在 bin 下、journal attempt→receipt |
| 空选择 | `:412` | 空 typed outcome + attempt/receipt 仍记录 |
| 根拒绝 | `:428` | 不存在/`$Recycle.Bin`/非目录 |
| 失败注入 | `:446` | 原文件字节/集合不变、`failed/in_use`、失败项不进 manifest、receipt typed reason |
| D 不降级 C（AST） | `:500` | 两模块无破坏性调用/DB/进程导入；application 零 mutating call、无 infrastructure import |
| 缺失选择 | `:569` | `failed/path_not_found`、无 bin |
| 根外/遍历/相对 | `:590` | 三条 `failed`、outside 树不变、sentinel 字节不变、无 bin |
| 运行时哨兵 | `:619` | 成功+失败后 `tmp_path` 除 isolated root 外全树快照相同；失败项字节仍 `TWO` |
| 静态 API 扫描 | `:661` | 766+ files、0 hit；合成 token 非空证明 |
| 测试路径字面量 | `:682` | 无 `%APPDATA%`/`%LOCALAPPDATA%`/`%USERPROFILE%`/`$env:APPDATA`/`$Recycle.Bin`/盘符；每个检测器对合成样本非空 |

**覆盖不足（P3/R-007）**：
- 文件系统根拒绝（代码 `:138-141`）未在 pytest 覆盖（我以只读构造实测拒绝）；
- 真实 junction/symlink 条目（Handoff 风险 4 已自认；我实测文件夹内 junction → `unsupported_entry`，但未入库）；
- `verify_failed` 回滚、`already_in_bin`、manifest 损坏/写入失败、journal 目录/symlink（我实测 rollback/already_in_bin 正常，见 `logs/rollback-probe.log`）；
- R-001 的 bin-dir/journal 绕过没有测试（也未被现有测试发现）。

**判别力评价**：13 tests 对“正常 tmp_path + 注入失败 + 生产默认”的语义是真实的，不是空转；静态/路径扫描有合成样本非空证明；失败注入与全树快照能区分“保留”与“删除”。但对“结构性隔离”的测试只覆盖条目路径，不覆盖 gateway 自身写入目标，因此 R-001 能漏过。

---

## 6. AC1–AC5 判定

| AC | 判定 | 依据与说明 |
|---|---|---|
| **AC1 协议与生产默认** | **MET** | `recycle_gateway.py:250-292`；`test_protocol...`/`test_production_default...`/`test_no_production_file...`；typed unavailable、零副作用、无 Host/UI。 |
| **AC2 模拟实现** | **MET（限定）**；若按全称读则为 **PARTIAL** | 正常 tmp_path 下：成功移动、manifest/journal 可审计、零 Windows API；根/条目校验、`os.replace`、复核、回滚均成立，测试覆盖。**但 R-001**：预置 junction/hardlink 可使 bin/manifest/journal 写到根外，故 `ISOLATION-EVIDENCE.md:26-27` 的“全部写入都在隔离根内”需加条件或修复。 |
| **AC3 失败语义** | **MET** | 注入失败原文件字节/集合不变、typed `failed`、失败项不进 manifest；AST 证明无删除/DB/进程回退；我的 rollback 探针进一步验证 `verify_failed` 恢复原文件。 |
| **AC4 隔离与禁令** | **MET** | 静态 766/0 API；`tests/fea12` 2 files/0 真实路径字面量；运行时哨兵 PASS（成功/失败/生产默认三次运行，隔离根外 `outside changes: []`）；`test_paths_outside...`/`test_runtime_sentinel...`。注：sentinel 使用 OS temp（`AppData\Local\Temp`，§R-008 表述），未触真实用户数据/回收站。 |
| **AC5 交付件与门禁** | **MET** | `pytest tests/fea12` 13 passed；全量 pytest 交付日志 3093/10（基线 3073/10，+20 = 13 + LINEAGE-1 r3 7）；全量 .NET 稳定树 1403/0/79（首跑/二次各 1 failed 已分列）；pins 18/18；`check.ps1` PASS 3 warnings；EV-05…EV-18 sha256 14/14 匹配。**证据精度问题**：R-002/R-003/R-004/R-006/R-009。 |

---

## 7. 独立复跑

所有复跑在 `G:\CODEX\New Manga`（复跑期间 HEAD `4a63c781a`，工作树 clean）执行；日志写仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-dsim\logs\`。每次复跑前后 `git status --porcelain` 均为空；最终检查时其他 Agent 并发推进 HEAD 至 `f11bff37e` 并留下 `?? doc/reviews/FEA-12-PREREQ-1-r2.md`（非本 Reviewer 所为，见上方“并发写入声明”）。本 Reviewer 未 commit/push/stash/reset/checkout。

| 场景 | 命令 | 结果 | 证据 |
|---|---|---|---|
| fea12 pytest | `C:/Python314/python.exe -m pytest tests/fea12 -q -p no:warnings -p no:cacheprovider --tb=no` | **13 passed in 3.32s，EXIT 0** | `logs/pytest-fea12-review.log` |
| 静态扫描 | `pwsh -NoProfile -File verification/FEA-12-DSIM-1/tools/static-scan.ps1` | **PASS，EXIT 0**：src 256 + apps 510 = 766 files / 0 API；tests 2 files / 0 literals；2 modules / 876 lines / 0 fallback | `logs/static-scan-review.log` |
| 哨兵探针 | `C:/Python314/python.exe verification/FEA-12-DSIM-1/tools/sentinel-probe.py` | **PASS，EXIT 0**：run1 moved=1，run2 failed/in_use 原文件保留，run3 not_started；`outside changes: []` | `logs/sentinel-probe-review.log` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (all 18)，EXIT 0** | `logs/verify-pins-review.log` |
| 治理 check | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-DSIM-1.md` | **PASS (3 warnings)，EXIT 0**；第 3 条为 `logs/gates.log`/`logs/check-final.log` 未登记 | `logs/check-review.log` |
| 隔离绕过探针（我新增） | `C:/Python314/python.exe ...\probe\probe.py` | **2 findings**：bin-dir junction 使移动+manifest 落到根外；journal 硬链接使根外文件被追加 | `logs/isolation-bypass-probe.log` |
| 回滚/条目探针（我新增） | `C:/Python314/python.exe ...\probe-rollback.py` | **PROBE2 PASS**：`verify_failed` 恢复原文件、文件夹内 junction → `unsupported_entry`、bin 目录 → `already_in_bin` | `logs/rollback-probe.log` |
| 全量 pytest / .NET | **未重跑**，引用交付日志 | 全量 pytest `logs/pytest-full.log` 3093/10；.NET 首跑/二次各 1 failed / 670 passed / 7 skipped（App.Tests），稳定树 `logs/dotnet-full-3.log` 1403/0/79 | 见 §6 / Task 卡 |

**未重跑理由**：全量 .NET 会重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson` 并可能与共享工作树的其他任务并发写入冲突；全量 pytest 约 4.6 分钟，且当前 head 相对交付 head 只有 docs/evidence commit（`4a63c781a` 在 `3d0d325f7` 之后仅 docs/evidence）。已用 fea12 定向复跑、静态/哨兵/pins/check 独立复跑与 EV hash 核对交叉验证；全量数字引用交付日志并保留首跑/复跑分列。**未把 NOT_RUN/模拟写成真实 D 完成。**

**AppData/真实数据声明**：本次复跑未读写真实用户数据、真实回收站或外部卷；`sentinel-probe.py` 按交付脚本在 `tempfile.TemporaryDirectory()`（`C:\Users\...\AppData\Local\Temp\fea12-dsim-sentinel-*`，脚本退出自清理）运行，属 OS temp scratch；该路径字面上位于 AppData 下，见 R-008 的表述建议。

---

## 8. 范围 / 资源 / 卫生

- **allowed_paths**：`doc/tasks/FEA-12-DSIM-1.md`、`doc/handoffs/FEA-12-DSIM-1-*.md`、`src/application/maintenance/recycle_gateway.py`、`src/application/maintenance/__init__.py`、`src/infrastructure/filesystem/simulated_recycle_bin.py`、`tests/fea12/**`、`verification/FEA-12-DSIM-1/**`。DSIM-1 实现 commit 全部命中；`4a63c781a` 的 18 个文件也全部命中。`144683876` 的 3 个指针文件不在本卡 allowed_paths，但属 ADJ §D6 的 Lead-owned 生命周期写域（R-005）。
- **工作树/资源**：未新建 DSIM-1 worktree；`git worktree list` 仅显示既有其他任务 worktree；审查期间本卡文件无 modified/untracked（最终检查时的 `?? doc/reviews/FEA-12-PREREQ-1-r2.md` 属其他 Agent 的并发写入，非本卡、非本 Reviewer）；未创建本卡 workspace temp；Resource Manifest 的 temp/agent-output 为 NOT_APPLICABLE。我的 review workspace 在仓外，仅有日志与探针脚本；探针用的 junction/hardlink 已 `rmdir` 解除并删除数据，未留重解析点。
- **evidence_dir 警告**：`verification/FEA-12-DSIM-1/` 共 16 个文件；EV-01…EV-18 覆盖 14 个（+4 个代码文件），**只有 `logs/gates.log`、`logs/check-final.log` 未登记**，正是 check warning 3（`logs/check-final.log:5`）。Handoff 风险 7 已列。DONE 前二选一：移入 `G:\CODEX\New Manga.workspace\...\agent-output` 并更新引用，或把二者列为 SOURCE_PIN（EV-19/EV-20）并同步 Resource Manifest（R-002）。
- **Canonical Evidence**：EV-05…EV-18 sha256 逐一 `Get-FileHash` **14/14 MATCH**；EV-01…EV-04 在 `3d0d325f7` 存在且与 HEAD blob 一致（`73934f76…`、`410c9d2a…`、`5a3ba80a…`、`f9de367d…`）。EV 表的 `commit` 列对日志为 `-`（可用 docs commit 补全，非阻塞）。
- **provenance**：全量 pytest 3093/10 与 .NET 1403/0/79 的日志无 commit/shell 头，但 `gates.log:19-75` 记录了 command/EXIT/head（pytest 工作树 = `3d0d325f7` + 并发 LINEAGE-1 r3；.NET 环境 `.NET SDK 10.0.401`）且 `ENVIRONMENT.md` 记录工具链；数字可复核，但原始日志缺 Q-009 的 EXIT/shell/venv 头（R-009）。
- **未 push**：`origin/main..HEAD` 有 18 个未推送 commit（含其他任务）；`main` 无 upstream；本卡未 push。该事实与本卡“不 push”声明一致。

---

## 9. 残余风险

1. **R-001 的隔离绕过**：预置 junction/hardlink 可让测试替身写根外；生产不可达（默认 unavailable/测试替身），但 AC2 表述需限定或修复。
2. **真实 D 流程 NOT_RUN**：无真实 Windows 回收站 API、无真实占用/网络盘/路径替换验证；真实 OS 桥需新授权。模拟切片不能证明真实 OS 行为。
3. **崩溃恢复未实现**：journal/receipt 只是 seam；移动成功但 manifest/receipt 写失败时无回滚/恢复；真实桥需实现“先核对 OS 事实再重发”。
4. **无 OS 级 junction/symlink 测试**：代码路径存在（我实测条目 junction 被拒），但测试套件未锁定；真实桥需覆盖。
5. **测试覆盖缺口**：fs-root 拒绝、rollback、already_in_bin、manifest 损坏/写失败、journal 硬链接未入库（部分我已用仓外探针验证，但交付测试没有锁定）。
6. **单写者假设**：manifest 读改写与 JSONL journal 无锁，测试替身并发不安全；真实桥需明确单写者/锁。
7. **AppData 表述**：sentinel/pytest 使用 OS temp（`AppData\Local\Temp`），与“AppData 零操作”字面冲突；未触用户数据/真实回收站，建议改写。
8. **证据精度**：`ENVIRONMENT.md` 断链、`ISOLATION-EVIDENCE.md` 行数陈旧、.NET 首跑归因与日志不符、原始日志头缺失；不影响代码结论，但影响审计可复核性。

---

## 10. 最小返修点（不代改代码）

| ID | 最小动作 |
|---|---|
| **R-001** | `SimulatedRecycleBin.__init__`/写入前：校验 `_bin_dir`、manifest、journal 非 reparse/link 且 `realpath` 在 `realpath(root)` 下；journal 拒绝 `st_nlink > 1`；拒绝 root reparse。加 junction/hardlink 判别测试；或收窄 AC2/ISOLATION 措辞并登记残余风险。 |
| **R-002** | DONE 前把 `logs/gates.log`、`logs/check-final.log` 移入 workspace agent-output（更新 Task/Handoff 引用）或补列 SOURCE_PIN（EV-19/20），同步 Resource Manifest。 |
| **R-003** | `ENVIRONMENT.md:7` 的 `FEA-12-DSIM-1-94a12e93f.md` 改为 `FEA-12-DSIM-1-3d0d325f7.md`；`:6` 补列 fix commit `3d0d325f7`。 |
| **R-004** | `ISOLATION-EVIDENCE.md:65` 的 `840 lines` 改为 `876 lines`（与 `static-scan.log:19`、Handoff:41 一致）。 |
| **R-005** | Task/Handoff 增加 per-commit scope 证明：`94a12e93f` 5 files、`3d0d325f7` 1 file、`4a63c781a` 18 files 全在 allowed_paths；`144683876` 为 Lead-owned 指针；range 含 7 个其他任务 commit。 |
| **R-006** | 修正 `Handoff:45`/`gates.log:51-54`/`AC-MATRIX:27` 的首跑归因：`dotnet-full-1.log:180-181` 显示的是 FEA-12-PREREQ-1 路径差异；可写“并发 PREREQ-1 r2 verification 写入（实测见日志）”，保留 flaky 分类。 |
| **R-007** | 建议补：fs-root 拒绝、真实 junction（`mklink /J`）、rollback/verify_failed、already_in_bin、manifest 写失败；至少补 fs-root + R-001 两类。 |
| **R-008** | 把“未使用 AppData”改为“仅 OS temp 自清理 scratch（pytest tmp_path 同族），未读写用户 AppData 业务数据/真实回收站”；或 sentinel 改用 `G:\CODEX\New Manga.workspace\temp\FEA-12-DSIM-1\`。 |
| **R-009** | 原始日志补 shell/venv/EXIT 头（或让 gates.log 明确覆盖每个 raw log 的 command/EXIT/head），满足 Q-009 证据纪律。 |

---

## 11. done vs changes 意见

**approved（可交 DSH 集成）**，理由：无 P0/P1；实现落在冻结范围；生产默认 typed 不可用且零副作用；无真实 Windows API；失败不降级 C；13 tests + 静态/哨兵/pins/check 可独立复核；真实 D 明确 NOT_RUN。**但 DONE 前必须处置 R-001、R-002**；R-003…R-009 建议在 closeout 一并修正。若 DSH 对 AC2 采用“任何情况下全部写入都在隔离根内”的全称解释，则 R-001 应升级为 P1、AC2 降为 PARTIAL，直到修复（修复量很小：bin-dir/journal 的 reparse/硬链接校验 + 一条判别测试）。

---

## 12. 自审声明

本人为 DSH 派发的独立上下文 fresh subagent（session `fc7ffec8-b24b-418a-82f7-dcc99cb2a7dc`；父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c`），**未参与** FEA-12-DSIM-1 的实现、Handoff 或证据生成；审查只读，未 commit/push/stash/reset/checkout 他人改动；所有写入均在仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-dsim\`；未触碰真实回收站、真实用户数据或外部卷；探针使用仓外 temp 并已清理（junction/hardlink 已解除，无残留）。审查末段 HEAD 推进至 `f11bff37e` 及 `?? doc/reviews/FEA-12-PREREQ-1-r2.md` 为其他 Agent 的并发写入，非本人所为；本人未修改该文件。本报告按审查指令未写入仓库 `doc/reviews/`；DSH 若需入库，可复制为 `doc/reviews/FEA-12-DSIM-1-*.md`（allowed_paths 已含该模式），并由 DSH 决定是否把本报告与 R-001 的处置进入 final evidence。

**最终决定：approved**（P0=0，P1=0，P2=2：R-001 隔离写目标加固、R-002 evidence_dir closeout；P3=7：证据精度/覆盖/表述）。实现主体与门禁通过；R-001 需在 DONE 前修复或把 AC2 收窄为“调用者提供的干净 root”并登记残余风险；R-002 需在 closeout 处置。真实 Windows 回收站行为仍为 **NOT_RUN**，需用户另行专门授权。
