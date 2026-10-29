---
task: UPGRADE-LEGACY-LAYOUT-1
title: 修复升级缺口（旧布局 data/ → 根布局）Handoff
status: in_review (rework round 1)
date: 2026-10-29
head: 311ddfe0d (review) / rework commit pending
---

# Handoff：UPGRADE-LEGACY-LAYOUT-1

## 任务

修复 `UPGRADE-REHEARSAL-1` 发现的升级缺口：旧布局 `<root>/data/library.db` 不被新壳读取（Core 只读根 `library.db`），旧用户升级后书架不可见。

## 实现（已集成 main `154f97a5c`，返修中）

1. 新增 `src/infrastructure/sqlite/upgrade_legacy_layout.py`：Core 启动时 `migrate_legacy_layout(data_root)`。
   - 检测 `<root>/data/library.db`（及 `data/managed/`、`data/backups/`）→ 复制到根布局；
   - **原子迁移**：先全部 staging（DB + 侧车 + 目录）+ `PRAGMA integrity_check`，成功后才统一 promote（目录先、DB 最后）；
   - 只复制不删除（旧 `data/` 保留可回滚）；当前库存在绝不覆盖；当前 `managed/backups` 缺失时补迁（修复部分迁移）；
   - 所有 I/O 失败包装为 `LegacyLayoutError`，`main()` 捕获后打印警告继续启动；
   - 写 `<root>/logs/upgrade-legacy.log`。
2. `src/bootstrap/core_service.py` `main()`：`data_root` 计算后、任何 DB 使用前调用。
3. `tests/infrastructure/test_upgrade_legacy_layout.py`：10 用例（正常/当前库优先/幂等/无旧/WAL+journal/损坏库/I/O 包装/部分失败/仅目录/日志）。

## 验证（返修后）

- 单测：10 passed（`verification/UPGRADE-LEGACY-LAYOUT-1/unit-tests.log`，带命令头）。
- 真实数据（2026-10-26 first-run 备份，全新副本）：首次迁移 `migrated=true`、copied=`managed/, backups/, library.db`、源 SHA 不变、新库 SHA 一致（`96fc4120…`）、books=1、schema v6、integrity ok（`real-data-first-migration.json`）；第二次运行 `migrated=false`（`real-data-second-run.json`，幂等）。
- 全量回归：见 `pytest-full-v2.log`（带命令头）。

## 独立 Review（round 1）

- Reviewer：`region-workbench-owner`，结论 **FAIL / CHANGES_REQUESTED**（P0=0；P1×4 + P2×6）：
  R-01 证据失效（unit-tests.log 曾为 "no tests ran"）；R-02 real-data 证据只记录第二次运行；
  R-03 Windows I/O 异常崩溃；R-04 非原子 promote 部分状态；R-05 已存在目录跳过；
  R-06 边界测试缺失；R-07 证据头缺失；Handoff 缺失。
- 本次返修逐项处理：R-01/R-02/R-07 重生成带命令头证据；R-03 包装 OSError、main 捕获；
  R-04 原子 staging + promote（目录先 DB 后）；R-05 缺失目录补迁；R-06 新增 3 用例；Handoff 即本文件。
- 复审：待（reviewer 将再次审查 rework 提交）。

## 边界与风险

- Windows 文件占用导致复制失败：现在会以 `LegacyLayoutError` 报告、启动继续（日志可查），用户数据不被改写。
- 旧 `library.db-journal`（崩溃残留）随库复制（SQLite 打开时回滚），不单独处理。
- 当前库存在但由迁移创建且 managed/backups 缺失：本次启动会补迁。

## 下一步

- 复审（region-workbench-owner）→ PASS 后转 `done`；FAIL 则按发现继续修复（用户许可范围内）。
