---
task_id: M2-DERIVED-GC-2
reviewer: Codex（非作者）
reviewed_code_head: e11562bed91a36dcbf0ec31094e44822e154488d
evidence_tip: 28a61f7865ad6daa4158c1884bd5062308f30a80
decision: changes_requested
findings: 1
---

## F-01 — P1，仍未闭合

1. **普通 `CHECK(singleton IN (1, 3))` 会被文本层拒绝**，新测试匹配到专属错误消息并检查零写入。[test_catalog_authority.py:842](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_catalog_authority.py:842>)

2. **注释走私加 `CHECK(protocol_version > 0)` 会被探针拒绝。** 文本层命中注释中的字样；探针的 `singleton=2` 行能插入，随后触发专属拒绝。这个用例验证了该构造会被探针拦截。[test_catalog_authority.py:880](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_catalog_authority.py:880>)

3. **两道守卫组合仍可误放行，故不接受“只会误拒”的论证。** 在完整空 catalog 上使用：

   ```sql
   /* check(singleton = 1) */ CHECK (singleton IN (1, 3))
   ```

   空白归一化保留注释，文本守卫因此命中 `check(singleton=1)`；探针插入 `singleton=2` 时，真实 CHECK 拒绝该行，错误消息含 `CHECK`，探针便将其视为语义通过。[catalog_store.py:375](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:375>) [catalog_store.py:417](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:417>) [catalog_store.py:420](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:420>)

   随后 `singleton=1` 绑定成功，而该表仍允许 `singleton=3`。现有测试分开覆盖这两类构造，没有覆盖它们的组合。建议让约束校验识别真实 SQL 结构，或采用规范 schema 校验，并加入此组合反例。

## 证据与范围

pytest 和 packaged 日志均绑定 `e11562be`。pytest 记录 1939 passed、1 skipped、EXIT=0；packaged 构建和 161 项定向回归成功。runner 保留唯一 CS-L1 FAIL，整体 GATE 为 FAIL，按既有债务口径记录。[pytest-full.log:4](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/pytest-full.log:4>) [pytest-full.log:75](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/pytest-full.log:75>) [seventh-round-build-and-run.log:46](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/seventh-round-build-and-run.log:46>) [seventh-round-build-and-run.log:694](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/seventh-round-build-and-run.log:694>) [seventh-round-build-and-run.log:748](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/seventh-round-build-and-run.log:748>)

`adb1498c..e11562be` 与 `e11562be..28a61f78` 的差量均在 allowed_paths；后一区间 `src/apps` 零差量。当前工作树另有 24 个 Tauri 自动生成文件显示行尾差异；忽略行尾后无内容差量，不在上述提交区间内。

本轮只读核查了固定提交的 `git show`、`git diff` 和 `git rev-parse`，未运行测试或打包。建议下一步补上组合反例并修正两层守卫，再提交复核。