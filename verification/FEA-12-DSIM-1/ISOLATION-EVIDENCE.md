# FEA-12-DSIM-1 — 隔离、静态扫描与运行时哨兵证据（r2，含 R-001 加固）

> 本卡是 **D 流程模拟切片**：只交付 application 端口 + 模拟实现 + 隔离/哨兵测试。
> **真实 Windows 回收站桥未实现、未验证（`NOT_RUN`）**；本文件所有 PASS 都不构成"真实 OS 回收站行为已验证"。

## 1. 边界（实现 / 不实现）

| 项 | 本卡 | 证据 |
|---|---|---|
| `OriginalFileRecycleGateway` application 协议 + 逐项 typed 结果（`moved`/`failed`/`not_started` + 封闭 reason 词表） | **已实现** | `src/application/maintenance/recycle_gateway.py`；`tests/fea12/test_recycle_gateway_sim.py::test_protocol_is_structural_and_the_typed_vocabulary_is_closed` |
| 生产默认 `UnavailableOriginalFileRecycleGateway`：typed 不可用、零文件/journal/DB 操作 | **已实现** | 同上 `::test_production_default_is_typed_unavailable_with_zero_side_effects`；`tools/sentinel-probe.py` run 3 |
| `SimulatedRecycleBin`：只在隔离根内 `os.replace`、可审计 manifest、JSONL journal | **已实现** | `src/infrastructure/filesystem/simulated_recycle_bin.py`；`::test_simulated_move_is_auditable_and_keeps_original_path_semantics` |
| **R-001（r2）**：gateway 自身写目标（bin 目录 / manifest / journal）的 realpath containment + junction/symlink/硬链接拒绝，构造期 + 每次读写前复检 | **已实现** | 本文件 §2.2；`::test_preplanted_bin_dir_junction_is_refused_without_outside_writes` 等 6 项 R-001 判别测试 |
| 失败注入：原文件字节/集合不变、逐项 typed、不转永久删除 | **已实现** | `::test_failure_injection_keeps_original_bytes_and_never_deletes`；`::test_d_failure_cannot_degrade_to_permanent_delete__static_ast` |
| 真实 Windows 回收站 API（SHFileOperation/IFileOperation/Shell32/Microsoft.VisualBasic.FileIO/Windows.Storage…） | **零实现、零调用（禁令）** | `logs/static-scan.log`（766 files，0 hits） |
| Host/UI 生产接线 | **不做** | `::test_no_production_file_references_the_d_flow_port` |
| 真实 OS 行为验证 | **`NOT_RUN`** | 本文件 §6；Handoff 风险与遗留 |

## 2. 隔离设计（结构约束，非约定）

### 2.1 根与条目路径

`SimulatedRecycleBin` / `JsonLinesRecycleJournal` 在构造期即校验隔离根：

1. 根必须**已存在**且是目录（不隐式创建任意根）；
2. 根不能是文件系统根（`<drive>:\` 的 `parent == self`）；
3. 根路径任一段落不得以 `recycle.bin` 结尾（**拒绝真实 Windows 回收站目录**）；
4. **R-001（r2）**：根路径不得跨 junction/symlink（从文件系统 anchor 逐段 `lstat` reparse 拒绝）；
5. 每个条目路径必须：绝对路径 → 拒绝空/`.`/`..` 段 → 以**未解析**根基线做包含检查（根之上有 junction 时候选会被解析到基线之外 → 拒绝）→ 对未解析路径逐段 `lstat` 拒绝 junction/symlink → 解析后再验一次包含；
6. 目标文件/文件夹与模拟 bin 目录都在**同一个隔离根**内（同卷），移动用 `os.replace`（逐项原子）；移动后按 kind/size/SHA-256 复核，复核失败则回滚并报 `failed`；无法回滚时抛 `RecycleSafetyError`（`failed` 永远等价于"原文件仍在"）；
7. manifest（`simulated-recyclebin/recyclebin-manifest.json`）与 journal（`recyclebin-journal.jsonl`）都写在隔离根内；
8. 本卡两个模块**零删除调用**（无 `unlink`/`rmtree`/`rmdir`/`remove`）、零 DB 访问（无 `sqlite`）、零进程/原生调用（无 `subprocess`/`ctypes`）——见 §3.3 与 pytest AST 断言。

隔离根外路径的拒绝是 typed 结果 `failed + outside_isolated_root`，**零文件系统效果**（`::test_paths_outside_the_isolated_root_are_refused`）。

### 2.2 R-001 加固：gateway **自身**写目标不可被重定向（r2）

Review r1 实测：`SimulatedRecycleBin` 只校验"条目路径"，未校验自身的 bin 目录 / manifest / journal；预置 `<root>/simulated-recyclebin` junction 可让 move/manifest 落到根外，预置 `recyclebin-journal.jsonl` 硬链接可让 journal 追加写到根外。r2 修复（`_assert_write_target` / `_assert_plain_component_walk`）：

- **构造期**：`SimulatedRecycleBin.__init__` 与 `JsonLinesRecycleJournal.__init__` 即校验三者（bin 目录 / manifest / journal）；
- **每次读写前复检**：`_recycle_one`（move 前 + 建 bin 目录后）、`_write_manifest`、manifest 读取、journal 的 `_append`/`read_records` 都重新校验；
- 校验内容：abspath 包含 → 未解析逐段 reparse 拒绝 → `os.path.realpath` 后再次包含（`realpath(target)` 必须在 `realpath(root)` 下）→ 既有 manifest/journal 必须是普通文件且 `st_nlink <= 1`（拒绝硬链接）；
- 任何可疑状态 → typed `RecycleSafetyError`，且**零写入**（不移动、不建目录、不写 journal/manifest）；
- 判别测试（真实 NTFS junction `mklink /J` + 真实硬链接 `os.link`，全部在 `tmp_path` 内）：预置 bin junction、预置 journal 硬链接、构造后重植 bin junction、构造后重植 journal 硬链接、root 跨 junction——均抛 typed 错误且根外 sentinel 零变化。

**残余风险（已登记，不消除）**：校验与写入是两次独立文件系统调用，存在 **TOCTOU** 重植窗口；本切片是单写者测试替身，真实 OS 桥必须绑定句柄并保持 journal/SSD 单写者纪律。**因此 AC2 的表述已收窄为"在调用者提供的干净隔离根内，且对自身写入目标做 reparse/硬链接拒绝；并发重植窗口未消除"**，不再声称"任何情况下全部写入都在隔离根内"。

## 3. 静态扫描（实跑，0 命中）

命令与完整输出：`logs/static-scan.log`（脚本 `tools/static-scan.ps1`，只读）。

```
pwsh -NoProfile -File verification/FEA-12-DSIM-1/tools/static-scan.ps1
EXIT: 0
```

### 3.1 `src/**` + `apps/**` 零 Windows 回收站 API

- 扫描范围：`.py`/`.cs`/`.csproj`/`.props`/`.targets`/`.xaml`/`.ps1`；排除 `bin/obj/target/dist/build/__pycache__/.git/.vs/node_modules/testresults/.pytest_cache/.venv/site-packages`（构建产物与第三方 vendored 依赖不是本仓源码）。
- 结果：`src` 256 files / 0 hits；`apps` 510 files / 0 hits；**合计 766 files / 0 hits**。
- 词表：`shfileoperation`、`shfileopstruct`、`ifileoperation`、`ifileoperationprogresssink`、`shell32`、`microsoft.visualbasic`、`windows.storage`、`send2trash`、`winshell`、`win32com`、`shell.application`、`fof_allowundo`。

等价 grep（供 Reviewer 独立复跑）：

```powershell
Get-ChildItem src,apps -Recurse -File -Include *.py,*.cs,*.csproj,*.props,*.targets,*.xaml,*.ps1 |
  Where-Object { $_.FullName -notmatch '\\(bin|obj|target|dist|build|node_modules|site-packages)\\' } |
  Select-String -Pattern 'SHFileOperation|IFileOperation|Shell32|Microsoft\.VisualBasic|Windows\.Storage|send2trash|winshell|win32com|Shell\.Application|FOF_ALLOWUNDO' -List
# 期望：0 行；EXIT 0
```

### 3.2 `tests/fea12/**` 零真实路径字面量

- 约束：测试不得出现 `%APPDATA%`/`%LOCALAPPDATA%`/`%USERPROFILE%`、`$env:APPDATA`、`$Recycle.Bin`、盘符绝对路径（正则 `[A-Za-z]:[\\/]`）。检测器本身用片段拼接构造模式，并对合成样本做非空证明（避免"检测器空转"）。
- 结果：2 files / **0 hits**。
- 对应 pytest：`::test_test_sources_reference_no_real_path_literals`。

### 3.3 D 流程两模块零删除/DB/进程回退

- 扫描 `recycle_gateway.py`（application）与 `simulated_recycle_bin.py`（infrastructure 模拟件），模式：`rmtree(`、`unlink(`、`os.remove(`、`os.unlink(`、`os.rmdir(`、`remove_managed(`、`purge_pages(`、`permanently_delete(`、`sqlite`、`subprocess`、`ctypes`、`winreg`、`os.system(`。
- 结果（r2 实测）：2 modules / **1020 lines** / **0 hits**（r1 为 876 lines，R-001 新增校验代码；见 `logs/static-scan.log`）。
- 对应 pytest AST 断言：`::test_d_failure_cannot_degrade_to_permanent_delete__static_ast`（另断言 application 模块零变更型调用、不 import `infrastructure`）。

## 4. 运行时哨兵（隔离根外零变化）

命令与完整输出：`logs/sentinel-probe.log`（脚本 `tools/sentinel-probe.py`，使用 `tempfile.TemporaryDirectory()` 自清理 scratch）。

```
C:/Python314/python.exe verification/FEA-12-DSIM-1/tools/sentinel-probe.py
EXIT: 0
PASS: runtime sentinel outside the isolated root unchanged
```

三次运行与结果（原样摘录，JSON 为 `RecycleOutcome.to_dict()` 安全投影）：

| 运行 | 输入 | 结果 | 原文件 |
|---|---|---|---|
| 1 成功模拟 | 隔离根内真实文件 `page-01.png` | `moved=1`，`status=moved` | 移入隔离根内 `simulated-recyclebin/` |
| 2 失败注入 | 隔离根内真实文件 `locked.png`，注入 `in_use` | `failed=1`，`status=failed, reason=in_use` | **留在原位且字节不变**（`LOCKED ORIGINAL`） |
| 3 生产默认 | 隔离根内真实文件 `default.png` | `not_started=1`，`reason=gateway_unavailable`，`operation_id=""` | **留在原位**（零操作） |

哨兵证明：

- 隔离根外 sentinel 树（`outside-sentinel/user-sources/chapter-01.png`、`outside-sentinel/notes.txt`）运行前后 SHA-256 **完全相同**；
- `outside changes: []`（隔离根外路径集合与逐文件 size+SHA-256 零差异）；
- 隔离根内确实发生了变化（成功移动 + bin 目录 + manifest + journal），证明探针不是空转；
- pytest 内等价断言：`::test_runtime_sentinel_outside_isolated_root_never_changes`（在 `tmp_path` 上对成功 + 失败两次运行做全树快照对比）。

**AppData 表述（Review r1 R-008 修正）**：pytest `tmp_path` 与探针的 `tempfile.TemporaryDirectory()` 在运行时**物理上位于 OS temp**（本机为 `C:\Users\<user>\AppData\Local\Temp\...`），这是 ADJ-2026-11-05 §D7 明确允许的隔离根族。本卡**未读取/使用 `%APPDATA%` 等环境变量、未读写用户 AppData 业务数据、未操作真实回收站**；此处不再使用"AppData 零操作"的字面表述。

## 5. r2 新增判别测试（R-001 / R-007）

`tests/fea12` 现共 **21 tests**（r1 13 + r2 8）：

| 场景 | test | 判别点 |
|---|---|---|
| fs root 拒绝 | `test_filesystem_root_is_refused` | 构造 `Path(tmp_path.anchor)` → `UnsafeIsolatedRootError`（代码分支被覆盖） |
| 根跨 junction | `test_root_reached_through_a_junction_is_refused` | 真实 `mklink /J` 根 → `UnsafeIsolatedRootError`（junction/symlink） |
| 预置 bin junction | `test_preplanted_bin_dir_junction_is_refused_without_outside_writes` | 构造即 `RecycleSafetyError`，根外 sentinel 树零变化 |
| 预置 journal 硬链接 | `test_preplanted_journal_hardlink_is_refused_without_outside_writes` | gateway 与 journal 构造均 `RecycleSafetyError`：硬链接；根外文件字节不变 |
| 构造后重植 bin junction | `test_replanted_bin_dir_junction_is_refused_at_write_time` | move 前复检 → `RecycleSafetyError`，原文件不动、根外零写 |
| 构造后重植 journal 硬链接 | `test_replanted_journal_hardlink_is_refused_at_write_time` | append/read 复检 → `RecycleSafetyError`，根外文件不变 |
| `verify_failed` 回滚 | `test_verify_failed_rolls_back_to_the_original` | 注入错误指纹 → `failed/verify_failed`、原文件字节恢复、manifest 为空 |
| bin 内条目 | `test_entry_inside_the_simulated_bin_is_already_in_bin` | `failed/already_in_bin`，bin 内文件不动 |

（其余 13 项覆盖见 r1 证据与 Task 卡。）

## 6. 未验证 / NOT_RUN（不得表述为已具备）

1. **真实 Windows 回收站行为**：未调用任何 OS API，未做真实移入/恢复/占用/网络盘/路径被替换验证 —— `NOT_RUN`，需用户另行专门授权。
2. **并发/TOCTOU**：写目标校验与写入之间存在重植窗口（R-001 已收窄表述并登记；模拟件单写者）。
3. **崩溃恢复**：journal/receipt（SC-34）形状已建立，但"崩溃后先核对 OS 事实再决定重发"的恢复逻辑未实现（属真实 Host 桥任务）。
4. **生产接线**：无 Host/UI 接线、无 C-07 冻结面改动、无 DB/schema/依赖变化。
5. 本文件所有"PASS"仅指**模拟切片在隔离根内的行为**与**静态禁令**，不构成 D 流程完成声明。
