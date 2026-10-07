---
task_id: M2-DERIVED-GC-2
reviewer: Codex（非作者）
reviewed_code_head: a4f80bf0f23a65e0add38ada27a04aea3e689e02
evidence_tip: b7e7e818f6b2876c5d2ec760ff5fc7929a481ecf
decision: changes_requested
findings: 1
---

## 复核结论

1. **注释 + `CHECK(singleton IN (1, 3))`：已拒绝，来自全文比较。** 空白归一化后，注释仍在 SQL 文本中，因此不等于规范 DDL；测试断言了 canonical-schema 拒绝消息和零写入。[catalog_store.py:382](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:382>) [test_catalog_authority.py:880](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_catalog_authority.py:880>)

2. **“归一化全文相等 ⇒ 语义等价”不成立，F-01 仍未闭合（P1）。** 删除全部空白会抹掉 SQL token 边界。规范列定义 `derived_root TEXT NOT NULL` 可改写为合法的多词类型名 `derived_root TEXTN OTNULL`；两者去空白后相同，但后者没有 `NOT NULL` 约束。当前布局检查只比列名和主键位，[catalog_store.py:323](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:323>)；全文比较因此可能接受这张非规范表。[catalog_store.py:383](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:383>)  
   建议保留词间边界进行比较，例如折叠连续空白而非删除空白，并增加此 DDL 反例。匹配目标没有字符串字面量，不能避免这种 token 合并问题。

3. **探针删除后守卫链：尚未完全闭合。** 它已拒绝本轮指定的注释组合反例，但上述去空白构造可绕过规范 schema 检查；删除探针后没有后备判别。应修正比较规则并补测后再判定闭合。

4. **证据绑定：通过，附日志标题不一致。** pytest 日志首行仍写旧 `e11562be`，但下一行记录的完整 `HEAD` 是 `a4f80bf0...`，结果为 1939 passed、1 skipped、EXIT=0。[pytest-full.log:1](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/pytest-full.log:1>) [pytest-full.log:4](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/pytest-full.log:4>) packaged 日志绑定同一 HEAD，安装包 SHA 与 runner 产物一致；定向回归 161 passed。runner 的唯一 CS-L1 FAIL 仍被记录，整体 GATE 为 FAIL。[eighth-round-build-and-run.log:46](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/eighth-round-build-and-run.log:46>) [eighth-round-build-and-run.log:686](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/eighth-round-build-and-run.log:686>) [eighth-round-build-and-run.log:748](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/eighth-round-build-and-run.log:748>)

5. **范围：通过。** `e11562be..a4f80bf0` 与 `a4f80bf0..b7e7e818` 的提交差量均在 allowed_paths；后一段 `src/apps` 无差量。

本轮只读执行了 `git rev-parse`、`git diff`、`git show` 核查；未运行测试、打包或写入文件。建议下一步修正空白归一化规则并补充 `TEXTN OTNULL` 反例，然后再提交复核。