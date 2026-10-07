---
task_id: M2-DERIVED-GC-2
reviewer: Codex（非作者）
reviewed_code_head: da2ddeae616d38d6681865dc1659eec7f5fa966d
evidence_tip: 1a0af963d4e8ce4ac32334e5bbcc3c9bd4f68290
base_commit: e3ad330f4831c868074a4941b14d90711b01c2d1
decision: changes_requested
findings: 1
---

## F-01 — P1，仍未闭合

新增全表计数能拒绝已有 `singleton=2` 行，`CHECK` 字样检查也能拒绝没有任何 CHECK 的空表。但该检查只确认 SQL 文本中出现 `CHECK`，没有验证约束确实是 `CHECK(singleton = 1)`。例如，空的 `preview_namespace` 若只带 `CHECK(protocol_version > 0)`，列名和主键符合 `_EXPECTED_LAYOUT`，行数为零且 SQL 含 `CHECK`，便会通过收养判定；`CREATE TABLE IF NOT EXISTS` 随后保留这张非规范表。[catalog_store.py:345](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:345>) [catalog_store.py:362](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:362>)

两条新测试也没有证明新增守卫命中：fixture 只创建 `preview_namespace`，[foreign rows 测试](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_catalog_authority.py:741>) 和 [without CHECK 测试](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_catalog_authority.py:781>) 都缺少 `resource_catalog`。而 `_assert_catalog_claimable` 会先无条件查询 `resource_catalog`，[catalog_store.py:326](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:326>)，所以测试可能仅因缺表而得到预期的 typed refusal。

**建议处置：**验证 `singleton=1` 约束本身，而非任意 CHECK 字样；测试 fixture 应先创建其余规范空表，再分别构造 singleton=2 和空的错误约束表，并确认拒绝来自对应守卫且无写入。

## 证据与范围

- **证据绑定 PASS。** `pytest-full.log` 记录的 HEAD 与目标代码 hash 一致，结果为 1936 passed、1 skipped、EXIT=0。[pytest-full.log:4](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/pytest-full.log:4>) [pytest-full.log:428](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/pytest-full.log:428>)  
  packaged 日志也记录了相同 HEAD、构建成功、installer SHA 和 121 项定向回归成功。runner 保留了既有 CS-L1 FAIL，整体 GATE 为 FAIL；我按已登记的快照债务看待，没有把它计作 PASS。[fifth-round-build-and-run.log:592](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/fifth-round-build-and-run.log:592>) [fifth-round-build-and-run.log:602](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/fifth-round-build-and-run.log:602>) [fifth-round-build-and-run.log:658](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/fifth-round-build-and-run.log:658>)

- **范围 PASS。** `e3ad330f..1a0af963` 的提交差量落在 Task allowed_paths 内；`da2ddeae..1a0af963` 只有 handoff 与 verification 差量，`src/apps` 无差量。

本轮仅执行了只读 `git rev-parse`、`git diff --name-status`、`git show` 和 `git show` 内容筛选；没有运行测试或打包。**最终 verdict：`changes_requested`**。建议补强 CHECK 语义核验和可区分的完整 catalog 测试后提交复核。