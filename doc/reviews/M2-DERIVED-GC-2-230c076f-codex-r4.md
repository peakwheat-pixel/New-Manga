---
task_id: M2-DERIVED-GC-2
reviewer: Codex（非作者）
reviewed_head: 230c076f
base_commit: 70ab9da0
decision: changes_requested
findings: 3
conditions: 2
---

## F-01 / F-02 / F-08

- **F-01 — NOT FIXED（P1；WAL 子项已修）**：WAL 用例现在能区分预检与锁内权威复核：表结构先 checkpoint，immutable 探针确认空表，行留在 WAL，初始化拒绝并检查行保留、未创建绑定表（[test_catalog_authority.py](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_catalog_authority.py:368>)）。外来列名形状也有零写入用例（[第 417 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_catalog_authority.py:417>)）。

  但 `_assert_catalog_claimable` 只比较 `PRAGMA table_info` 返回的列名（[catalog_store.py 第 311–324 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:311>)），没有核验主键、唯一性、NOT NULL、默认值或 CHECK 约束。空表 `resource_catalog(resource_id TEXT, scope_class TEXT, rel_path TEXT)` 若没有 `resource_id` 主键，仍会通过并被 `CREATE TABLE IF NOT EXISTS` 收养；后续 `ON CONFLICT(resource_id)` 写入会因缺少唯一约束而失败（[upsert 第 476–482 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:476>)）。`preview_namespace` 的 singleton 主键与 CHECK 约束也未核验。建议拒绝缺少运行所依赖约束的空表，并增加“列名完全相同但缺主键”的零写入反例。

- **F-02 — FIXED**：新增用例旁路预检，让已打开的真实锁句柄报告 reparse 属性，并断言属性核验执行、出现专属错误、`CloseHandle` 被调用（[test_handle_resolver.py](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_handle_resolver.py:539>)）。对应打开后检查和异常关闭路径在 [handle_resolver.py](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/handle_resolver.py:556>)。这解决了 r3 指出的“无法证明测试命中 post-open 核验”问题。

- **F-08 — NOT_VERIFIED**：新增的 [build-chain.md](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/build-chain.md:3>) 记录的是 `70ab9da0` 的构建；本轮目标代码是 `230c076f`，其中 `catalog_store.py` 有新增逻辑。因此该安装包不能验证当前复核对象。并且仓库中 `build_sidecar: OK` 原文只出现在这份手写汇总里，没有独立构建 stdout 或 sidecar 产物摘要。第三轮日志的安装包 SHA 与该汇总一致，只能证明 runner 使用了该安装包，不能单独证明其内含代码版本（[runner 日志第 36 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/third-round-full-stdout.log:36>)）。

  r4 所称的定向 `118 passed` 未在 verification 归档中找到；全量 pytest 日志记录的是 `HEAD=70ab9da0` 和 `1931 passed, 1 skipped`，不是 `230c076f`。我未运行测试。矩阵还保留 sidecar HEAD `7f652473` 的旧记录（[g1-g7-matrix.md 第 93 行](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/g1-g7-matrix.md:93>)），与新建构链记录不一致。

## 范围纪律

**通过。** `70ab9da0..230c076f` 共 18 个变更路径：生产代码只改了允许的 `catalog_store.py`；两项测试在允许列表中；Handoff、Review 和新增运行材料均在允许的文档路径或 `verification/M2-DERIVED-GC-2/**` 下。没有触及禁止面，也没有改 `apps` 或 packaging 脚本。

只读检查中，`git diff --check` 的 `src tests` 子集通过；全范围检查因归档原始日志空行/行尾空格及复制的 r3 Review 行尾空格而返回非零，不是生产代码或测试差量。

## 最终 verdict

**`changes_requested`**：F-01 的约束检查仍不完整；F-08 没有验证 `230c076f` 的安装态产物及回归结果。F-02 已修复。

建议先补齐已知表的约束校验和同列名缺约束用例，再归档以 `230c076f` 构建的 sidecar/安装包链及对应定向测试结果，之后交非作者复审。

只读核查使用了命令级 `git -c safe.directory=... -C ... rev-parse/diff/show/grep`；未改 Git 配置、未写文件，也未运行 pytest 或打包 runner。