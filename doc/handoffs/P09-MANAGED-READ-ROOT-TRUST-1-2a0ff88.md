---
task_id: P09-MANAGED-READ-ROOT-TRUST-1
author: DeepSeek Harness
recipient: Codex
base_commit: b8a1e519703f13af73b320dded117004b4bb189a
delivery_head: 2a0ff8819dceff0849a2ea783ba202769e18078b
status: in_review  # 交付时快照；当前状态以 Task 文件与 STATUS 为准
supersedes_head: 56aee75ae8fa88913655f27c019345224414096d
---

# Handoff（返修轮）：P09-MANAGED-READ-ROOT-TRUST-1

> 本文件是 **Codex Review `changes_requested`（R-001/R-002/R-003，建议 R-004/R-005）后的返修交付**。
> 上一轮 Handoff `doc/handoffs/P09-MANAGED-READ-ROOT-TRUST-1-56aee75.md` 与实现 head
> `56aee75ae` 降为 **HISTORICAL**；本轮实现 head 为 `2a0ff8819`。
> 设计答案（第一交付物）不变：`verification/P09-MANAGED-READ-ROOT-TRUST-1/DESIGN-expected-identity.md`。
> **本 Handoff 不创建 Review、不声明 AC 已由独立方确认。**

## Review 逐条修复

| Finding | 修复内容 | 证据 |
|---|---|---|
| **R-001（P2）目录准入回归** | `ManagedRootTrust._open_verified()` 在**已打开目标句柄**上拒绝 `FILE_ATTRIBUTE_DIRECTORY`（`TypedResourceChannelError(E_OUT_OF_SCOPE)`）；`image_state`/`_uri_within`/`_page_image` 等调用方不再依赖自己的 `is_file()` | 新测试 `test_directory_substitution_is_refused_by_the_opened_handle`：同名目录替换后 `image_state=="invalid"`、`image_url==""`、`_uri_within==""`、`_checked_managed_path`/`_read_verified_managed`/`_reader_sha256` 均拒绝、`page_frame` 抛 `ProviderInputError`。base FAILED → current PASSED |
| **R-002（P2）AC3 覆盖/断言不足** | ① site3 新增导出 hash（`_verified_managed_sha256`）与**惰性 provider**（`_read_verified_managed`，经真实 `ExportService.export()` 消费；拒绝时目标文件不落盘、正常时仍可导出）重定向拒绝测试；② `ac3-discrimination.py` 改用 `-v` 解析真实 `PASSED/FAILED` 集合、**以 pytest 退出码为门槛**（base 必须非 0、current 必须为 0）、每条列出的测试必须出现在实际集合中（`current_passed` 实际参与断言） | `test_site3_export_hash_refuses_repointed_ancestor`、`test_site3_lazy_export_provider_refuses_repointed_ancestor`、`logs/ac3-discrimination.txt`（base exit=1 / current exit=0，14/14 观测） |
| **R-003（P2）AC2 日志纪律** | `run-suites.ps1` 每份日志写入执行头（generated、shell、os、python 版本与解释器绝对路径、cwd、完整 command）与日志内 `EXIT=<code>`；8 个套件全部重跑 | `logs/suite-*.log`（8 份带头+EXIT）、`logs/summary.txt` |
| **R-004（P3）scratch 位置** | `ac1-r5b-repro.py` / `ac3-discrimination.py` 的 base 源码快照、driver 与 pytest 临时目录改到 `G:/CODEX/New Manga.workspace/temp/P09-MANAGED-READ-ROOT-TRUST-1/`，运行后清理子目录；不再使用系统 `%TEMP%` | 两个脚本输出均含 `scratch_root:` 行 |
| **R-005（P3）重复收敛** | `core_assembly`：两处 `_trust()` 懒捕获收敛为模块级 `_root_trust_for(owner)`；`core_service`：可读性错误收敛为 `_managed_input_unavailable(detail)`，`_reader_sha256` 统一走 `_managed_root_trust()` | diff + 全量套件 |

## 交付结果

- **实现 head**：`2a0ff8819dceff0849a2ea783ba202769e18078b`（3 个源文件 + 14 个测试）
- **设计答案（不变）**：装配时对配置根的一个真实句柄快照 `(volume_serial, file_index)` +
  句柄规范路径 + `os.path.abspath` 词法根；每次读取词法冻结 → 验根身份 → 已打开目标句柄验
  **对象类型（非目录）**与规范路径 → 同句柄读取。第 8 处 `resolve_namespace_identity` 用局部同构版本。
- **链接策略（不变）**：根之上/本身 reparse 允许（身份匹配时）；根之下任何 reparse 拒绝；
  未采用「任一祖先 reparse 即拒绝」。
- **未改动**：删除路径、IPC 契约、Schema、ACL、依赖清单、前端；未执行真实删除/移动/GC；
  未 push/merge。

## AC 对照

| AC | 状态 | 依据 |
|---|---|---|
| AC1 | **MET** | `ac1-r5b-repro.py` exit 0：base=VULNERABLE、current=SAFE（返修后重跑，`logs/ac1-after-fix.txt`） |
| AC2 | **MET** | 8 套件逐套件回归全部 exit 0（core 564 / storage 87 / m2_resource_channel 106 / security **43** / library 63 / reading_export 141 / export 13 / m2_acceptance 37）；每份日志含执行头 + `EXIT`；合法祖先链接在 base/current 均通过 |
| AC3 | **MET** | `ac3-discrimination.py` exit 0：8/8 site 测试 base=FAILED、current=PASSED；R-001/R-002 补充测试 base=FAILED、current=PASSED；AC2 对照两边 PASSED；pytest 退出码为门槛 |
| AC4 | **MET** | `logs/ac4-change-files.txt`：仅 3 个源文件 + 1 个测试文件 + 本 Task 文档/证据；无依赖/契约/Schema/ACL 变更 |
| AC5 | **MET** | `ac5-run-delete-probes.py` exit 0；前序 9 探针 9/9 与基线一致（返修后重跑） |

## 验证证据

| AC/场景 | 实际命令 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 | `C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac1-r5b-repro.py` | Windows / Python 3.14.6 / `2a0ff8819` + base 快照 | **exit 0**；base VULNERABLE、current SAFE | `logs/ac1-after-fix.txt`、`logs/ac1-before-fix.txt`（历史） |
| AC3 | `C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac3-discrimination.py` | 同上 | **exit 0**；base exit=1、current exit=0；14 tests observed | `logs/ac3-discrimination.txt`、`SITE-MATRIX.md` |
| AC2/AC4 | `pwsh -NoProfile -File verification/P09-MANAGED-READ-ROOT-TRUST-1/run-suites.ps1` | 同上 | **exit 0**；8 份日志含执行头+`EXIT` | `logs/suite-*.log`、`logs/summary.txt`、`logs/baseline/`（历史基线） |
| AC5 | `C:/Python314/python.exe verification/P09-MANAGED-READ-ROOT-TRUST-1/ac5-run-delete-probes.py` | 同上 | **exit 0**；9/9 一致 | `logs/ac5-delete-probes.txt`、`.json` |
| 新测试 | `python -m pytest tests/security/test_p09_managed_read_root_trust.py -q` | 同上 | **14 passed**（`tests/security` 全体 43） | `logs/suite-security.log` |
| AC4 文件面 | `git diff --name-only b8a1e51..2a0ff8819` | 同上 | 仅 4 个实现/测试文件 + 本 Task 文档/证据 | `logs/ac4-change-files.txt` |

**未运行**：Rust（`cargo test`）、React/前端、packaging 测试。原因：变更面只在 Python Core
读取路径，未改 IPC/契约/Schema/前端；不属于本 Task 的 AC1–AC5 范围。不得把未运行写成 PASS。

## 接收方式

- worktree：`G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1`
- branch：`dsh/P09-MANAGED-READ-ROOT-TRUST-1`；base：`b8a1e519703f13af73b320dded117004b4bb189a`；
  **实现 head：`2a0ff8819dceff0849a2ea783ba202769e18078b`**；分支 tip 以交付文档提交为准。
- 复现顺序：`ac1-r5b-repro.py` → `ac3-discrimination.py` → `run-suites.ps1` → `ac5-run-delete-probes.py`
  （全部自包含；ac1/ac3 在 `New Manga.workspace/temp/P09-MANAGED-READ-ROOT-TRUST-1/` 建快照并清理，
  ac5 在 `verification/.../_scratch/` 建夹具并清理）。
- 需要接收者重点检查：
  1. R-001 的目录拒绝是否只在**已打开句柄**上判定（而非回到 `is_file()`）；
  2. R-002 的 `ac3-discrimination.py` 是否以 pytest 退出码与真实结果集合为门槛；
  3. R-003 的 8 份日志是否都含执行头与 `EXIT`；
  4. 删除路径是否仍零改动（`git diff b8a1e51..2a0ff8819 -- src/infrastructure/filesystem src/infrastructure/sqlite src/infrastructure/resource_channel/render_preview.py src/infrastructure/imaging` 为空）。

## 下一任务建议（必填）

- **无需下一步操作**（没有已释放且可安全承接的新 Task）。本 Task 的下一步是 Codex 对本返修的
  独立 Review；若仍 `changes_requested`，Owner 按流程回到 `in_progress` 并以新 head 重新 `in_review`。
- 候选（**未释放、不得自行启动**）：把读取路径改为
  `NtCreateFile(RootDirectory=已验证根句柄)` 相对句柄链，以消除「同名目录整体 rename+replace
  且新对象为普通文件」的残余窗口（与删除域 `win_unlink.unlink_by_handle` 同类基建）。

## 风险与遗留

1. **残余风险（设计文档第六节）**：QML `file://` 与 Reader 预览发布器的交接窗口；硬链接；
   同名目录整体 rename+replace（新对象为普通文件，需配置根父目录写权限）；装配后 root
   被搬走 → 全部读取 fail-closed。**文件→目录替换已由 R-001 关闭。**
2. **链接策略取舍**：祖先链接允许（身份匹配时）、根下链接拒绝；「任一祖先 reparse 即拒绝」未采用。
3. `logs/baseline/` 是改动前的历史快照（当时尚无日志头规范），仅用于数量对照；当前证据以
   带执行头+`EXIT` 的 `logs/suite-*.log` 为准。
4. 未运行套件：Rust/前端/packaging（理由见上）。
5. 未执行任何真实删除/移动/GC/prune/清理；未 push/merge；未修改主仓库或其他 Task。
