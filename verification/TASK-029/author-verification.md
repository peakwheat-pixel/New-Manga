# TASK-029 作者验证记录

- 日期：2026-09-15（Asia/Shanghai）
- 作者：ZCode；被测 commit：`a2348e91824e90db74bfba7aa9e805309f499797`
- 环境：Windows 11 专业版 Build 26200 x64；Python 3.12.3（固定项目环境 `G:/CODEX/New Manga.task-envs/TASK-005-py312`，pytest 9.1.1）；测试数据库/Managed Storage/临时文件均在 TASK-029 独立临时根目录（pytest tmp_path），零用户数据接触；未新增依赖

## 实际执行命令与结果（派单指定四条 + 补充）

| # | 命令（工作目录 = TASK-029 worktree 根） | 退出码 | 结果 |
|---|---|---|---|
| 1 | `python -m pytest tests/storage -v` | 0 | **33 passed**（v1/v2 迁移、checksum、备份、TOO_NEW 门控、Artifact safe-commit 全套在 v2 库回归、v1 冻结与越界表边界检查） |
| 2 | `python -m pytest tests/library -v` | 0 | **32 passed**（TASK-007 全部 25 项 + SQLite round-trip/重启/占位 Page/软删/无 UNIQUE(name) 边界 7 项） |
| 3 | `python -m pytest tests/editing -v` | 0 | **25 passed**（TASK-008 全部 17 项 + SQLite 原子 seam/冲突回滚/Pin/恢复/重排/触发器 8 项） |
| 4 | `PYTHONPATH=src python -m pytest tests` | 0 | **95 passed**（core 6 + storage 33 + library 32 + editing 25） |
| 5 | `git diff --check c6db2c0 <head> --` | 0 | PASS |
| 6 | `git status`/`git diff --name-only` 范围核对 | — | 仅 allowed_paths：`src/infrastructure/sqlite/{schema,library,regions}.py`、三处 application ports/service、三目录测试；v1 SQL 字符串零改动（结构断言 `test_v1_schema_is_unchanged`） |

## 迁移与兼容探针（含于测试）

- v1 空库 → 全量应用 → `[1, 2]`；v1-only 库（`default_migrations()[:1]` 构造）→ 追加 v2 → v1 占位 Page 行保留且 `list_pages/get_page/existing_source_hashes/max_source_order` 不伪造其数据。
- 迁移前备份：v0→v1 守卫先于 `backup_records` 表（文件产出、无行）；v1→v2 守击在 v1 状态快照（记录行 `schema_version=1`、受管相对路径 `backups/{id}.db`）。
- `TOO_NEW/query_only`：构造 version=3 → 只读、写入抛错、MigrationRunner 拒绝。
- v2 CHECK：非法枚举/负尺寸/空 hash 写入被数据库拒绝。

## 开发过程中发现并修正的问题（供 Review 参考）

1. **SQLite 不支持 `ALTER TABLE ADD CONSTRAINT`**——regions 的复合 current 外键改为写入 `CREATE TABLE` 定义（SQLite 前向引用合法，与 v1 media_artifacts 同型）。
2. **committer 对象引用稳定性**：InMemory committer 初版以 staged 对象调用 `update_region()`，替换了 repo 内对象引用，导致调用方后续读到孤儿对象（症状：APPLIED 后调用方 current=None）——修正为把 revision-owned 状态同步进 repo 内既有对象，staged 仅作为指针/状态回传视图。
3. **`apply_machine_translation` 守卫顺序**：锁检查一度先于 stale-revision 检查，违反 D06 §90 优先级（revision 过期比锁更根本，契约 V01 场景）——恢复 expected-first 顺序，seam 内仍保留第二道锁防线。
4. **测试毫秒抖动**：`make_png`/时间戳字段的两次独立构造比较跨毫秒不稳定——改按稳定键（page_id）断言。

## NOT_RUN / N/A

| 项 | 状态 | 理由 |
|---|---|---|
| 多连接并发竞争（两个写连接同时 BEGIN IMMEDIATE） | NOT_RUN | busy_timeout=5000 已配置；seam 单事务语义已由单连接守卫回滚证明；真实并发协调属 TASK-011 与集成验证 |
| 生产 bootstrap 装配（连接注入四页 UI） | NOT_RUN（范围外） | bootstrap/QML 不在允许路径；Adapter 已可注入，装配属 UI/入口切片 |
| managed_original_ref 与 D03 managed_original_artifact_id 收敛 | N/A（TASK-028 §3.1 明确保留差异） | 后续文档同步/产品决策 Task |
| R-201（edited_confirmed 合并继承）/R-202（拆分 reading_order 归一化） | N/A | TASK-028 §7 明确不在本 Task 裁决 |
| Migration 失败恢复端到端（损坏库） | NOT_RUN | MigrationRunner 失败回滚有单测；损坏库恢复属 TASK-021 |
| 性能 / 大数据量 | N/A | 无本 Task AC；D07 §11 容量属 Benchmark |
