# P09-MANAGED-READ-ROOT-TRUST-1 — AC 结果与运行记录

- base_commit：`b8a1e519703f13af73b320dded117004b4bb189a`
- 实现提交 / 证据提交：见 `doc/handoffs/P09-MANAGED-READ-ROOT-TRUST-1-<short-head>.md`
  与 Task 文件 Canonical Evidence（证据文件不记录自身 commit）。
- 环境：Windows（NTFS，junction 可用），`C:/Python314/python.exe` = Python 3.14.6，
  pytest 9.1.1，PySide6 6.11.2。所有命令均在
  `G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1` 内执行。
- 本文件只记录**实际运行**的命令与退出码；未运行项不写 PASS。

## AC1 — R5b 复现（祖先 junction → outside bytes）被拒绝

探针：`ac1-r5b-repro.py`。它用 `git archive b8a1e5197 src` 把 **base 源码**解到系统临时目录，
在**同一 driver** 上先跑 base、再跑当前 worktree：

1. 以 `live -> real`（junction）作为数据目录祖先装配生产 Core；
2. 合法读取一次（探针判别力对照）；
3. 移除 junction 并把祖先重定向到外部镜像树（`payload/data/managed/...` 内容为 `OUTSIDE`）；
4. 调用 R5b 的复现点 `_checked_managed_path()`，若接受则读出字节。

| 运行 | 命令 | exit | 结果 |
|---|---|---|---|
| 修复前（当前代码尚未修复） | `python verification/P09-MANAGED-READ-ROOT-TRUST-1/ac1-r5b-repro.py` | **1** | base=VULNERABLE、current=VULNERABLE（`accepted=True`，读到 `OUTSIDE`）→ `logs/ac1-before-fix.txt` |
| 修复后 | 同上 | **0** | base=VULNERABLE、current=SAFE（`accepted=False`、`error=P16WireError`、outside bytes 未读出）→ `logs/ac1-after-fix.txt` |

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

### 套件回归（逐套件单独进程；合并运行会因 `from conftest import ...` 冲突，见 `logs/baseline/`）

命令（每个 suite 单独执行，日志 `logs/suite-<suite>.log`，汇总 `logs/summary.txt`，
runner：`run-suites.ps1`）：

```
pwsh -NoProfile -File verification/P09-MANAGED-READ-ROOT-TRUST-1/run-suites.ps1
```

| suite | base（改动前） | current（修复后） | exit |
|---|---|---|---|
| `tests/core` | 564 passed, 1 warning | 564 passed, 1 warning | 0 |
| `tests/storage` | 87 passed | 87 passed | 0 |
| `tests/m2_resource_channel` | 106 passed | 106 passed | 0 |
| `tests/security` | 29 passed | **40 passed**（+11 本 Task 新测试） | 0 |
| `tests/library` | 63 passed | 63 passed | 0 |
| `tests/reading_export` | 141 passed | 141 passed | 0 |
| `tests/export` | 13 passed | 13 passed | 0 |
| `tests/m2_acceptance` | 37 passed | 37 passed | 0 |

- 汇总 exit code = **0**（runner 在任一 suite 非 0 时返回 1）。
- `tests/core` 的 1 条 warning 与 QML `TypeError` 输出在 base 日志中同样存在（`logs/baseline/baseline-core.log`），
  不是本 Task 引入。
- 逐处"换 root 前合法读取"断言：见 `SITE-MATRIX.md` 第 5 列与测试文件各 site 测试的首段。

**结论：AC2 MET**（合法读取与合法祖先链接均不回归；内部链接拒绝是有意策略并在设计文档记录）。

## AC3 — 8 处逐个有测试（不接受「模式相同所以一起算」）

测试文件：`tests/security/test_p09_managed_read_root_trust.py`（11 个测试）。

判别力脚本：`ac3-discrimination.py` —— 把**同一测试文件**复制到临时树、conftest 指向
`git archive b8a1e5197 src` 的 base 源码运行，然后与当前 worktree 运行结果逐条对比。

```
python verification/P09-MANAGED-READ-ROOT-TRUST-1/ac3-discrimination.py
```

exit **0**；结果（`logs/ac3-discrimination.txt`）：

| row | test | base | current |
|---|---|---|---|
| site1 | `test_site1_read_original_page_reader_refuses_repointed_ancestor` | FAIL | PASS |
| site2 | `test_site2_resolve_page_resource_refuses_repointed_ancestor` | FAIL | PASS |
| site3 | `test_site3_checked_managed_path_refuses_repointed_ancestor` | FAIL | PASS |
| site4 | `test_site4_protected_export_target_uses_frozen_managed_baseline` | FAIL | PASS |
| site5 | `test_site5_image_state_refuses_repointed_ancestor` | FAIL | PASS |
| site6 | `test_site6_uri_within_refuses_repointed_ancestor` | FAIL | PASS |
| site7 | `test_site7_page_image_source_decodes_verified_handle_bytes` | FAIL | PASS |
| site8 | `test_site8_resolve_namespace_identity_refuses_swap_between_walk_and_open` | FAIL | PASS |
| AC2 | `test_ancestor_junction_is_allowed_for_legal_reads` | PASS | PASS |

base 运行合计 10 failed（8 处 site + 内部链接策略 + 原始语缺失的 primitive 测试）、current 0 failed。
第 8 处测试用 R6 的注入时序：`_lstat_reparse_walk` 通过后、打开之前把祖先换成 junction
（`injection never fired` 会显式断言，不会静默跳过）。

逐处映射与行号漂移说明见 `SITE-MATRIX.md`。

**结论：AC3 MET。**

## AC4 — 不引入新依赖或契约变更

命令（实现提交后重跑）：`git diff --name-only b8a1e519703f13af73b320dded117004b4bb189a..HEAD`

变更文件（除本 Task 文档/证据外）：

```
src/bootstrap/core_assembly.py
src/bootstrap/core_service.py
src/infrastructure/resource_channel/handle_resolver.py
tests/security/test_p09_managed_read_root_trust.py
```

- 无依赖清单变更：`pyproject.toml` / `requirements*.txt` / `package.json` / `pnpm-lock.yaml` /
  `Cargo.toml` / `Cargo.lock` 均不在 diff 中（仓库中不存在的清单文件也不应被新建——本 Task 未新建）。
- 无契约/Schema/ACL 变更：`doc/contracts/**`、`src/**/schema*`、`src/infrastructure/sqlite/schema.py`、
  `src/infrastructure/**/acl*` 均不在 diff 中。
- 不新增第三方 import：读取原语只用 `ctypes`/`os`/`pathlib`（`handle_resolver` 既有导入面）；
  新增的 `tempfile` 是标准库且 `core_service` 之前未用于依赖引入。
- 不新增/修改 IPC 命令、wire 错误码、JSON 结构：错误面沿用既有 `TypedResourceChannelError` 家族，
  各处映射回**原有**异常类型/文案（见 SITE-MATRIX）。

**结论：AC4 MET。**

## AC5 — P09-AC3-DELETE-HARDEN-1 的 9 个探针不回归

- 副本：`ac5-delete-probes/`（生成脚本 `ac5-prepare-probes.py`；与原件 diff：
  `ac5-delete-probes/PATH-ADAPTATION.diff`，**只有路径常量不同**，探针逻辑未改）。
- 运行：`python verification/P09-MANAGED-READ-ROOT-TRUST-1/ac5-run-delete-probes.py`
  → exit **0**；结果 `logs/ac5-delete-probes.txt`、`logs/ac5-delete-probes.json`。

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

## 未运行 / 边界

- 本 Task 不运行 Rust（`cargo test`）、React/前端与 packaging 测试：变更面只在 Python Core 读取路径，
  且未改 IPC/契约/Schema；这些套件不在本 Task 的验收方向内（AC1–AC5 全部落在 Python 侧）。
- 未执行任何真实删除/移动/GC/prune/清理；删除路径代码零改动（AC5 零回归）。
- 残余风险（交接窗口、硬链接、同名替换、root 搬走后 fail-closed）见设计文档第六节与 SITE-MATRIX 末节。
