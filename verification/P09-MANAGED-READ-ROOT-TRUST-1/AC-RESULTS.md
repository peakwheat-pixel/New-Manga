# P09-MANAGED-READ-ROOT-TRUST-1 — AC 结果与运行记录

- base_commit：`b8a1e519703f13af73b320dded117004b4bb189a`
- 实现提交 / 证据提交：见 `doc/handoffs/P09-MANAGED-READ-ROOT-TRUST-1-<short-head>.md`
  与 Task 文件 Canonical Evidence（证据文件不记录自身 commit）。
- 环境：Windows（NTFS，junction 可用），`C:/Python314/python.exe` = Python 3.14.6，
  pytest 9.1.1，PySide6 6.11.2，pwsh 7.6.6。所有命令均在
  `G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1` 内执行。
- 本文件只记录**实际运行**的命令与退出码；未运行项不写 PASS。
- **Review 返修轮**：Codex Review（`changes_requested`，R-001/R-002/R-003 + 建议 R-004/R-005）的
  逐条修复与本轮结果见文末「Review 返修对照」。本轮日志全部为返修后重新生成。

## AC1 — R5b 复现（祖先 junction → outside bytes）被拒绝

探针：`ac1-r5b-repro.py`。它用 `git archive b8a1e5197 src` 把 **base 源码**解到
`G:/CODEX/New Manga.workspace/temp/P09-MANAGED-READ-ROOT-TRUST-1/`（R-004：不用系统 `%TEMP%`），
在**同一 driver** 上先跑 base、再跑当前 worktree：

1. 以 `live -> real`（junction）作为数据目录祖先装配生产 Core；
2. 合法读取一次（探针判别力对照）；
3. 移除 junction 并把祖先重定向到外部镜像树（`payload/data/managed/...` 内容为 `OUTSIDE`）；
4. 调用 R5b 的复现点 `_checked_managed_path()`，若接受则读出字节。

| 运行 | 命令 | exit | 结果 |
|---|---|---|---|
| 修复前（历史，第二轮保留） | `python verification/P09-MANAGED-READ-ROOT-TRUST-1/ac1-r5b-repro.py` | **1** | base=VULNERABLE、current=VULNERABLE（`accepted=True`，读到 `OUTSIDE`）→ `logs/ac1-before-fix.txt` |
| 返修后 | 同上 | **0** | base=VULNERABLE、current=SAFE（`accepted=False`、`error=P16WireError`、outside bytes 未读出）→ `logs/ac1-after-fix.txt` |

**结论：AC1 MET。** base 上复现成立、修复后拒绝；探针的 `injection_fired` 与
`outside_bytes_served` 分开报告，注入未触发不会被读作 SAFE。

## AC2 — 合法读取不回归（含链接合法使用）

### 链接策略（显式取舍，见 `DESIGN-expected-identity.md` 第四节）

- **配置根之上/本身是 reparse**：允许，当且仅当对象身份仍等于启动快照。测试 harness 全程
  以 `live -> real` junction 作为数据根祖先 —— 8 处测试的**第一段断言都是换 root 前合法读取成功**，
  即合法链接用法在 base 与 current 都成立。
- **配置根之下任何 reparse 段**：拒绝（内部链接会被规范路径判据识别；
  `test_internal_link_below_the_root_is_refused`：base FAIL → current PASS）。
- **「任一祖先 reparse 即拒绝」未采用**：会破坏上述两类合法部署。

### 套件回归（逐套件单独进程；合并运行会因 `from conftest import ...` 冲突）

命令：`pwsh -NoProfile -File verification/P09-MANAGED-READ-ROOT-TRUST-1/run-suites.ps1`

**R-003：每份 `logs/suite-<suite>.log` 均含执行头（generated / shell / os / python + 解释器路径 /
cwd / command）与日志内 `EXIT=<code>`。** 汇总见 `logs/summary.txt`。

| suite | base（改动前，历史基线） | current（返修后，合规日志） | EXIT |
|---|---|---|---|
| `tests/core` | 564 passed, 1 warning | 564 passed, 1 warning | 0 |
| `tests/storage` | 87 passed | 87 passed | 0 |
| `tests/m2_resource_channel` | 106 passed | 106 passed | 0 |
| `tests/security` | 29 passed | **43 passed**（29 旧 + 14 本 Task） | 0 |
| `tests/library` | 63 passed | 63 passed | 0 |
| `tests/reading_export` | 141 passed | 141 passed | 0 |
| `tests/export` | 13 passed | 13 passed | 0 |
| `tests/m2_acceptance` | 37 passed | 37 passed | 0 |

- 汇总 exit code = **0**（runner 在任一 suite 非 0 时返回 1）。
- `tests/core` 的 1 条 warning 与 QML `TypeError` 输出在 base 基线日志中同样存在，不是本 Task 引入。
- `logs/baseline/` 是**改动前**的历史快照日志（当时日志规范尚未要求执行头/EXIT），仅作数量对照；
  当前证据以带头的 `logs/suite-*.log` 为准。
- 逐处"换 root 前合法读取"断言：见 `SITE-MATRIX.md` 与测试文件各 site 测试的首段。

**结论：AC2 MET**（合法读取与合法祖先链接均不回归；内部链接拒绝是有意策略并在设计文档记录）。

## AC3 — 8 处逐个有测试（不接受「模式相同所以一起算」）

测试文件：`tests/security/test_p09_managed_read_root_trust.py`（**14 个测试**）。

判别力脚本：`ac3-discrimination.py` —— 把**同一测试文件**复制到临时树（位于
`G:/CODEX/New Manga.workspace/temp/P09-MANAGED-READ-ROOT-TRUST-1/`，R-004），conftest 指向
`git archive b8a1e5197 src` 的 base 源码运行，然后与当前 worktree 运行结果逐条对比。

**R-002 门槛**：pytest 以 `-v` 运行并解析真实 `PASSED/FAILED` 行；**base 退出码必须非 0、
current 必须为 0**；每条列出的测试必须出现在实际结果集合中（缺失即 FAIL）。不再使用
「未出现在失败集合即 PASS」，脚本内的 `current_passed` 已实际参与断言。

```
python verification/P09-MANAGED-READ-ROOT-TRUST-1/ac3-discrimination.py
```

exit **0**；结果（`logs/ac3-discrimination.txt`）：

| row | test | base | current |
|---|---|---|---|
| site1 | `test_site1_read_original_page_reader_refuses_repointed_ancestor` | FAILED | PASSED |
| site2 | `test_site2_resolve_page_resource_refuses_repointed_ancestor` | FAILED | PASSED |
| site3 | `test_site3_checked_managed_path_refuses_repointed_ancestor` | FAILED | PASSED |
| site4 | `test_site4_protected_export_target_uses_frozen_managed_baseline` | FAILED | PASSED |
| site5 | `test_site5_image_state_refuses_repointed_ancestor` | FAILED | PASSED |
| site6 | `test_site6_uri_within_refuses_repointed_ancestor` | FAILED | PASSED |
| site7 | `test_site7_page_image_source_decodes_verified_handle_bytes` | FAILED | PASSED |
| site8 | `test_site8_resolve_namespace_identity_refuses_swap_between_walk_and_open` | FAILED | PASSED |
| AC2 | `test_ancestor_junction_is_allowed_for_legal_reads` | PASSED | PASSED |
| R-001 | `test_directory_substitution_is_refused_by_the_opened_handle` | FAILED | PASSED |
| R-002 | `test_site3_export_hash_refuses_repointed_ancestor` | FAILED | PASSED |
| R-002 | `test_site3_lazy_export_provider_refuses_repointed_ancestor` | FAILED | PASSED |

base 退出码 = 1、current 退出码 = 0；base 观测到 14 个测试、current 观测到 14 个测试。
第 8 处测试用 R6 的注入时序：`_lstat_reparse_walk` 通过后、打开之前把祖先换成 junction
（`injection never fired` 会显式断言，不会静默跳过）。

逐处映射、行号漂移与 R-001/R-002 补充见 `SITE-MATRIX.md`。

**结论：AC3 MET。**

## AC4 — 不引入新依赖或契约变更

命令：`git diff --name-only b8a1e519703f13af73b320dded117004b4bb189a..HEAD`（记录于
`logs/ac4-change-files.txt`）。

变更文件（除本 Task 文档/证据外）仅：

```
src/bootstrap/core_assembly.py
src/bootstrap/core_service.py
src/infrastructure/resource_channel/handle_resolver.py
tests/security/test_p09_managed_read_root_trust.py
```

- 无依赖清单变更：`pyproject.toml` / `requirements*.txt` / `package.json` / `pnpm-lock.yaml` /
  `Cargo.toml` / `Cargo.lock` 均不在 diff 中；本 Task 未新建任何清单文件。
- 无契约/Schema/ACL 变更：`doc/contracts/**`、`src/infrastructure/sqlite/schema.py`、
  ACL 相关路径均不在 diff 中。
- 不新增第三方 import：读取原语只用 `ctypes`/`os`/`pathlib`（`handle_resolver` 既有导入面）；
  `tempfile` 为标准库。
- 不新增/修改 IPC 命令、wire 错误码、JSON 结构：错误面沿用既有 `TypedResourceChannelError` 家族，
  各处映射回**原有**异常类型/文案（见 SITE-MATRIX）。

**结论：AC4 MET。**

## AC5 — P09-AC3-DELETE-HARDEN-1 的 9 个探针不回归

- 副本：`ac5-delete-probes/`（生成脚本 `ac5-prepare-probes.py`；与原件 diff：
  `ac5-delete-probes/PATH-ADAPTATION.diff`，**只有路径常量不同**，探针逻辑未改）。
- 运行：`python verification/P09-MANAGED-READ-ROOT-TRUST-1/ac5-run-delete-probes.py`
  → exit **0**；结果 `logs/ac5-delete-probes.txt`、`logs/ac5-delete-probes.json`（返修后重跑）。

| probe | injection_fired | outside_survived | verdict | 基线 | 一致 |
|---|---|---|---|---|---|
| `n002-race-probe.py` | False | True | INCONCLUSIVE | INCONCLUSIVE | ✅ |
| `n002-race-probe2.py` | True | True | SAFE | SAFE | ✅ |
| `n004-ancestor-probe.py` | True | True | SAFE | SAFE | ✅ |
| `n004-production-order-probe.py` | True（脚本 assert，干净退出） | True | SAFE | SAFE | ✅ |
| `r5-p1-managed-remove-probe.py` | True（脚本 assert） | True | SAFE | SAFE | ✅ |
| `r5-p1-cleanup-book-files-probe.py` | True（脚本 assert） | True | SAFE | SAFE | ✅ |
| `r5b-p1-remove-managed-race-probe.py` | True | True | SAFE | SAFE | ✅ |
| `r5b-p1-collect-orphans-race-probe.py` | True | True | SAFE | SAFE | ✅ |
| `r6-p1a-publish-cleanup-race-probe.py` | True | True | SAFE | SAFE | ✅ |

基线来源：`verification/P09-AC3-DELETE-HARDEN-1/HANDOFF.md` 的探针表与 R5b/R6 结果。
`n002-race-probe.py` 的 hook 不在当前实现路径上，故按基线保持 INCONCLUSIVE（不读作 SAFE）。

**结论：AC5 MET。**

## Review 返修对照（Codex `changes_requested`）

| Finding | 修复 | 证据 |
|---|---|---|
| **R-001（P2）目录准入回归** | `ManagedRootTrust._open_verified()` 在**已打开目标句柄**上拒绝 `FILE_ATTRIBUTE_DIRECTORY`（`E_OUT_OF_SCOPE`），不再依赖调用方 `is_file()`；`image_state`/`_uri_within` 随之为 `invalid`/`""` | `test_directory_substitution_is_refused_by_the_opened_handle`（base FAILED → current PASSED，见 AC3 表）；`tests/security` 43 passed |
| **R-002（P2）AC3 覆盖/断言不足** | 新增导出 hash 与惰性 provider 的重定向拒绝测试（惰性 provider 经真实 `ExportService` 消费、拒绝时目标文件不落盘）；`ac3-discrimination.py` 改为 `-v` 解析真实结果集合 + 以 pytest exit code 为门槛 + 每条列出测试必须出现在实际集合中（`current_passed` 参与断言） | `test_site3_export_hash_refuses_repointed_ancestor`、`test_site3_lazy_export_provider_refuses_repointed_ancestor`；`logs/ac3-discrimination.txt`（base exit 1 / current exit 0） |
| **R-003（P2）AC2 日志证据纪律** | `run-suites.ps1` 为每份日志写执行头（timestamp/shell/os/python/解释器路径/cwd/command）与日志内 `EXIT=<code>`；8 个 suite 全部重新运行 | `logs/suite-*.log`（8 份带头+EXIT）、`logs/summary.txt` |
| **R-004（P3）scratch 位置** | ac1/ac3 的 base 快照与 driver 临时目录改到 `G:/CODEX/New Manga.workspace/temp/P09-MANAGED-READ-ROOT-TRUST-1/`，不再使用系统 `%TEMP%`；运行后清理子目录 | `ac1-r5b-repro.py`、`ac3-discrimination.py` 输出中的 `scratch_root:` 行 |
| **R-005（P3）重复收敛** | `core_assembly` 两处 `_trust()` 收敛为 `_root_trust_for(owner)`；`core_service` 的可用性错误收敛为 `_managed_input_unavailable(detail)`，`_reader_sha256` 也统一走 `_managed_root_trust()` | 全量套件通过；diff 审查 |

## 未运行 / 边界

- 本 Task 不运行 Rust（`cargo test`）、React/前端与 packaging 测试：变更面只在 Python Core 读取路径，
  且未改 IPC/契约/Schema；这些套件不在本 Task 的验收方向内（AC1–AC5 全部落在 Python 侧）。
- 未执行任何真实删除/移动/GC/prune/清理；删除路径代码零改动（AC5 零回归）。
- 残余风险（交接窗口、硬链接、同名目录整体 rename+replace、root 搬走后 fail-closed）见设计文档
  第六节与 SITE-MATRIX 末节。
