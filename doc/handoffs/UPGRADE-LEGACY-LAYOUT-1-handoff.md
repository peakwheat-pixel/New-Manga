---
task: UPGRADE-LEGACY-LAYOUT-1
title: 修复升级缺口（旧布局 data/ → 根布局）Handoff
status: done
date: 2026-10-29
head: ce3cf5bac1dacc1d1c72395a9bb8b745ddcc92cc
---

# Handoff：UPGRADE-LEGACY-LAYOUT-1

## 任务

修复 `UPGRADE-REHEARSAL-1` 发现的升级缺口：旧布局 `<root>/data/library.db` 不被新壳读取（Core 只读根 `library.db`），旧用户升级后书架不可见。

## 实现（round 3）

1. `src/infrastructure/sqlite/upgrade_legacy_layout.py`：Core 启动时 `migrate_legacy_layout(data_root)`
   - 检测 `<root>/data/library.db`（及 `data/managed/`、`data/backups/`）→ 迁移到根布局；
   - 侧车 `-wal/-shm/-journal` 随库复制；
   - **原子迁移**：DB+侧车+目录全部 staging 并 `PRAGMA integrity_check` 验证后统一 promote；
     promote 顺序 = 目录 → 侧车 → 主 DB（sidecar 失败不会留下无 WAL 的根 DB；已 promote 的目录在重试时跳过，自愈）；
   - 只复制不删除（旧 `data/` 保留可回滚）；当前库绝不覆盖；
   - **当前库已存在时跳过 legacy DB staging**，只补迁缺失的 `managed/backups`（损坏/被占用的旧 DB 不阻断补迁）；
   - 所有 I/O 失败包装为 `LegacyLayoutError`；写 `<root>/logs/upgrade-legacy.log`。
2. `src/bootstrap/core_service.py` `main()`：`data_root` 计算后、任何 DB 使用前调用；
   **迁移失败时打印错误并 `return 2` 退出**（不继续 assemble，避免创建空根库导致旧数据永久不再迁移）。
3. `tests/infrastructure/test_upgrade_legacy_layout.py`：**12 用例**（正常/当前库优先/补迁/幂等/无旧/WAL+journal/损坏库/
   I/O 包装/部分失败/仅目录/日志/sidecar promote 失败后重试成功/当前库+损坏旧库补迁）。

## 验证（round 3）

- 单测：12 passed（`verification/UPGRADE-LEGACY-LAYOUT-1/unit-tests.log`，带命令头）。
- `main()` 失败退出 probe：损坏 legacy DB → 打印两条警告、`MAIN_RETURN 2`、根目录不创建 `library.db`（`main-failure-probe.log`）。
- 真实数据（2026-10-26 first-run 备份全新副本）：首次迁移 `migrated=true`、copied=`managed/, backups/, library.db`、
  源 SHA 不变、新库 SHA 一致（`96fc4120…`）、books=1、schema v6、integrity ok（`real-data-first-migration.json`）。
- 全量回归：`pytest-full.log`（带命令头）。

## 两轮独立 Review 处理

- round 1（reviewed_head `154f97a5c`）：FAIL（4×P1 + 6×P2）。
- round 2（reviewed_head `27de6fce3`）：FAIL（2×P1 + 6×P2；R-01/R-02/R-03 已闭环；R-04 未真正原子 + main 继续启动创建空库；R-05 边界；R-06/R-07 证据头/Handoff）。
- round 3 修复：R-04（sidecar 先于 DB + 失败退出）、R-05（当前库时跳过 DB staging）、R-06（+2 用例）、R-07（Handoff 本文件、日志头、旧证据登记 SOURCE_PIN）。
- 复审：待 region-workbench-owner。

## 边界与风险

- 迁移失败（损坏库/占用/权限）→ Core 退出码 2，Host 显示启动失败；用户数据不被改写，修复后可重试。
- 旧 `library.db-journal` 随库复制（SQLite 打开时回滚）。
- 当前库存在但 managed/backups 缺失 → 每次启动补迁一次（幂等）。

## 下一步

- 复审 PASS → 转 `done`。
## fail-closed 说明（review P2）

- main() 在迁移失败时 eturn 2：目的是避免 ssemble_production_core 创建空根库、让旧 data/library.db 永久不再被迁移。
- 触发条件：仅当**当前根 library.db 缺失且旧数据存在**（需要迁移）时；损坏/占用/权限错误都会走到这里。
- 已知 P2：若当前库已存在、仅补迁 managed/backups 目录失败，也会退出（严格保护）；后续可按需改为"警告后继续"。