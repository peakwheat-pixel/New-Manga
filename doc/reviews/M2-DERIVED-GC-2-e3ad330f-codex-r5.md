---
task_id: M2-DERIVED-GC-2
reviewer: Codex（非作者）
reviewed_head: e3ad330f
evidence_tip: 4c9053e2
base_commit: 230c076f
decision: changes_requested
findings: 1
---

## 复核判定

- **F-01 — NOT FIXED（P1）**：WAL 判别与缺主键用例已补，但 `_EXPECTED_LAYOUT` 只核对列名和主键序号（[catalog_store.py](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:259>)）。它仍未核验列类型及 `CHECK` 等约束。具体反例：空的 `preview_namespace` 保留相同列和 `singleton` 主键，但没有 `CHECK(singleton = 1)`，并已有 `singleton=2` 行。绑定查询只找 `singleton=1`，所以看不到该行（[第 150 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:150>)）；布局检查通过，资源计数也为零，初始化便可能保留这条未知历史并写入新绑定。新测试只覆盖缺主键表（[test_catalog_authority.py](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_catalog_authority.py:516>)）。建议校验必要的列约束，并拒绝 namespace 表中的任何既有行；补充同列同主键但缺 CHECK、带 `singleton=2` 行的零写入用例。

- **F-08 — FIXED（构建链与全量回归已绑定当前代码）**：第四轮日志记录 sidecar 构建输出的 HEAD 为 `e3ad330f` 且成功（[fourth-round-build-and-run.log 第 592–593 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/fourth-round-build-and-run.log:592>)），NSIS 构建成功并记录安装包 SHA（[第 595–602 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/fourth-round-build-and-run.log:595>)）；runner 核对同一路径、同一 SHA（[第 613 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/fourth-round-build-and-run.log:613>)）。全量 pytest 日志绑定 `e3ad330f`，结果 `1934 passed, 1 skipped, EXIT=0`（[pytest-full.log](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/pytest-full.log:4>)）。runner 唯一 FAIL 是已登记的 CS-L1 协议快照漂移，仍按 F-07 保留 FAIL 记录。

  有一处计数不一致：用户所述定向 `167 passed` 未在归档中找到；第四轮日志记的是 `119 passed`（[第 604–607 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/fourth-round-build-and-run.log:604>)）。这不改变已归档的全量回归结果，但 `167` 这一具体说法未获证实。F-02 本轮无差量，维持上轮 FIXED。

## 范围核查

**`230c076f..e3ad330f` 范围通过**：仅三项变更——允许的 `catalog_store.py`、允许的 `test_catalog_authority.py`、允许的 Review 文档；无 `apps` 或 packaging 脚本差量。

需更正证据范围表述：`230c076f..4c9053e2` **不是**零 `src/apps` 差量，其中包含本轮 `catalog_store.py` 变更；零差量区间是 `e3ad330f..4c9053e2`。后一区间的其余变更位于允许的 Handoff/verification 路径。

## 最终 verdict

**`changes_requested`**：F-01 仍可能把带未知 namespace 历史的非规范 catalog 绑定为自有库。建议补齐约束校验及对应反例后再复审。

只读核查执行了命令级 `git -c safe.directory=... -C ... rev-parse/diff/show/grep`；`git diff --check` 的 `src tests` 范围通过。未运行测试或打包命令，也未写入文件。