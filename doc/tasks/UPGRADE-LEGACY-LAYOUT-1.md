---
id: UPGRADE-LEGACY-LAYOUT-1
title: 修复真实升级缺口——Core 启动时迁移旧布局 data/library.db → 根 library.db
kind: fix
governance_version: 3
status: done
approval: user_authorized_2026-10-29_fix_upgrade_gap
suggested_owner: dsh
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [UPGRADE-REHEARSAL-1]
base_commit: af6d9e94d
branch: task/UPGRADE-LEGACY-LAYOUT-1
worktree: G:/CODEX/New Manga.workspace/worktrees/UPGRADE-LEGACY-LAYOUT-1
integration_commit: 098c60381
delivery_head: ce3cf5bac1dacc1d1c72395a9bb8b745ddcc92cc
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/UPGRADE-LEGACY-LAYOUT-1
allowed_paths:
  - doc/tasks/UPGRADE-LEGACY-LAYOUT-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/handoffs/UPGRADE-LEGACY-LAYOUT-1-handoff.md
  - src/infrastructure/sqlite/upgrade_legacy_layout.py
  - src/bootstrap/core_service.py
  - tests/infrastructure/test_upgrade_legacy_layout.py
  - verification/UPGRADE-LEGACY-LAYOUT-1/**
  - G:/CODEX/New Manga.workspace/task-envs/UPGRADE-LEGACY-LAYOUT-1/**
  - G:/CODEX/New Manga.workspace/worktrees/UPGRADE-LEGACY-LAYOUT-1/**
---

# UPGRADE-LEGACY-LAYOUT-1：修复真实升级缺口（in_review / round 3）

## 来源

`UPGRADE-REHEARSAL-1` 用真实升级前备份演练发现：`core_service.py:666` 固定读取根 `library.db`，
不识别旧布局 `data/library.db` → 旧用户升级后书架不可见。用户 2026-10-29 指示「立即修复升级缺口」。

## 实现（round 3，已集成 main `098c60381`，代码提交 `ce3cf5bac`）

1. `src/infrastructure/sqlite/upgrade_legacy_layout.py`：`migrate_legacy_layout(data_root)` 启动迁移。
   - 检测 `<root>/data/library.db`（及 `data/managed/`、`data/backups/`）→ 迁移到根布局；侧车 `-wal/-shm/-journal` 随库复制。
   - **原子迁移**：DB + 侧车 + 目录全部 staging 并 `PRAGMA integrity_check` 验证；全部成功后统一 promote。
     **promote 顺序 = 目录 → 侧车 → 主 DB**：sidecar 失败不会留下无 WAL 的根 DB；已 promote 的目录在重试时跳过（自愈）。
   - **fail-closed**：任何失败（含 I/O 占用/权限）包装 `LegacyLayoutError`，`main()` 打印错误后 `return 2` 退出——
     不继续 assemble，避免创建空根库导致旧数据永久不再迁移。
   - **当前库存在时跳过 legacy DB staging**，只补迁缺失的 `managed/backups`（损坏/被占用的旧 DB 不阻断补迁）。
   - 只复制不删除（旧 `data/` 保留可回滚）；写 `<root>/logs/upgrade-legacy.log`。
2. `src/bootstrap/core_service.py` `main()`：`data_root` 计算后、任何 DB 使用前调用；失败退出码 2。
3. `tests/infrastructure/test_upgrade_legacy_layout.py`：**12 用例**（正常/当前库优先+补迁/幂等/无旧/WAL+journal/损坏库/
   I/O 包装/目录部分失败/仅目录/日志/sidecar promote 失败后重试成功/当前库+损坏旧库补迁）。

## 验证（round 3）

- 单测：**12 passed**（`unit-tests.log`，带 COMMAND/CWD/PYTHON/AT 头与 EXIT）。
- 全量回归：**2612 passed / 10 skipped / 0 failed**（206s，`pytest-full.log`，带命令头）。
- **main() fail-closed probe**：损坏 legacy DB → 两条警告 + `MAIN_RETURN 2`，根目录不创建 `library.db`（`main-failure-probe.log`）。
- **真实数据首次迁移**（2026-10-26 first-run 备份全新副本）：`migrated=true`、copied=`managed/, backups/, library.db`、
  源 SHA 未变、新库 SHA 一致（`96fc4120…`）、books=1、schema v6、integrity ok（`real-data-first-migration.json`）；
  第二次运行幂等（`real-data-second-run.json`）。

## Acceptance Criteria

- [x] **AC1 迁移实现**：独立模块 + `main()` 启动时调用；原子 staging/promote（目录→侧车→DB）；只复制不删除；写日志。<<MET>>
- [x] **AC2 幂等与守卫**：当前库绝不覆盖；无旧布局 no-op；重复运行幂等；部分迁移可续迁；`integrity_check` 验证。<<MET>>
- [x] **AC3 测试**：12 用例（含 sidecar promote 失败重试、当前库+损坏旧库补迁）；单测 12 passed；全量 2612 passed。<<MET>>
- [x] **AC4 真实数据验证**：真实备份全新副本首次迁移 → SHA 一致、books=1、integrity ok；第二次幂等。<<MET>>
- [x] **AC5 门禁**：`check.ps1` PASS；契约不变；Handoff `doc/handoffs/UPGRADE-LEGACY-LAYOUT-1-handoff.md`（已列入 allowed_paths）。<<MET>>

## 禁止范围（已遵守）

未改命令面契约/DB schema；未删除旧数据；未改历史 done 卡字节；未 push main。

## 交付与运行记录

- worktree：`G:/CODEX/New Manga.workspace/worktrees/UPGRADE-LEGACY-LAYOUT-1`，HEAD `ce3cf5bac`。
- 集成：main `154f97a5c`（round 1）→ `27de6fce3`（round 2）→ **`098c60381`（round 3 merge）**。
- 证据：`verification/UPGRADE-LEGACY-LAYOUT-1/`（round 3 日志/JSON + round 1/2 旧证据保留为历史）。

## Review

- 实施与自查：DSH（Lead）。
- 独立审查 round 1（`region-workbench-owner`，`154f97a5c`）：**FAIL**（4×P1 + 6×P2）。
- 独立复审 round 2（`region-workbench-owner`，`27de6fce3`）：**FAIL**（2×P1 + 6×P2；R-01/R-02/R-03 已闭环；R-04 未真正原子 + main 继续启动创建空库；R-05 corrupt legacy DB 阻断补迁；R-06/R-07 证据头/Handoff/旧证据登记）。
- **round 3 修复**：R-04 sidecar 先于 DB promote + 失败 `return 2`（probe 证明根不建空库）；R-05 当前库时跳过 DB staging；
  R-06 +2 用例（12）；R-07 日志头补齐、Handoff 更新并纳入 allowed_paths、旧 `real-data-verify.json` 登记为 SOURCE_PIN。
- 复审：**待 region-workbench-owner 再审 `098c60381`**。
- 独立复审 round 3（region-workbench-owner，reviewed_head `ce3cf5bac`）：**PASS**（P0=0，P1=0；R-01/R-02/R-03/R-04/R-05/R-06/R-07 均闭环：12 passed、main fail-closed `MAIN_RETURN 2` 且不建根库、sidecar 失败重试成功、current+corrupt legacy 补迁成功、证据 7/7 pin、check PASS 3 warnings；剩余 4×P2：目录 promote 严格原子性表述/测试回归缺口/Handoff head pending/fail-closed 在 current DB 场景的启动策略，建议 done 收口时顺手修正）。详见 [`doc/reviews/UPGRADE-LEGACY-LAYOUT-1.md`](../reviews/UPGRADE-LEGACY-LAYOUT-1.md) 的 Round 3 Review。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| unit-tests | AC3 | verification/UPGRADE-LEGACY-LAYOUT-1/unit-tests.log | ce3cf5bac | 8e7c0eae4b519109d695656f5ed328c36d7c9441f9e1e260c286a87dbee2f1f9 | CANONICAL |
| real-data-first-migration | AC4 | verification/UPGRADE-LEGACY-LAYOUT-1/real-data-first-migration.json | ce3cf5bac | 0c84400e2d70230eb0cbd080c29b0fe2a71bb25a0b9ca30d66400889c2dc8f6b | CANONICAL |
| real-data-second-run | AC4 | verification/UPGRADE-LEGACY-LAYOUT-1/real-data-second-run.json | ce3cf5bac | 7c5cf78c7fc69ed8f23f9b3f85ca8aab33e4eb96d5f736e4fee3f12777f16376 | CANONICAL |
| pytest-full-summary | AC3 | verification/UPGRADE-LEGACY-LAYOUT-1/pytest-full-summary.txt | ce3cf5bac | 79b05d72d605f5ad8c7383a2fb0f8a7532aaaf6a26d7af167828b203fdfcd0d4 | CANONICAL |
| pytest-full-log | AC3 | verification/UPGRADE-LEGACY-LAYOUT-1/pytest-full.log | ce3cf5bac | b65dbbaee1f7c531691414c2bb893a778538382f7304b4f84cc04934e2b8c84e | CANONICAL |
| main-failure-probe | AC2 | verification/UPGRADE-LEGACY-LAYOUT-1/main-failure-probe.log | ce3cf5bac | 57c4a8d3c4d5a75a7d32cff824501e6432feade5290c17d1f793506c55877395 | CANONICAL |
| legacy-real-data-verify-r1 | 历史 | verification/UPGRADE-LEGACY-LAYOUT-1/real-data-verify.json | - | a676771122a6f9966785582fe615b5064d4adae0ae651d8561c0ad9a13ba7459 | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/UPGRADE-LEGACY-LAYOUT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/UPGRADE-LEGACY-LAYOUT-1 | 提交 ce3cf5bac | 修复实现（round 3） |
| task-env | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-LEGACY-LAYOUT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/UPGRADE-LEGACY-LAYOUT-1 | real-data-fresh-v3 / pytest-full-v3.log / probe-root | 真实数据验证与 probe 工作区 |

## Closeout Record

- Closed：2026-10-29 as **done**（用户「立即修复升级缺口」；round 1/2 FAIL → round 3 PASS；集成 merge `098c60381`，代码 `ce3cf5bac`）。
- 复审 PASS 后 P2 处理：Handoff frontmatter `head` 已更新为 `ce3cf5bac`；fail-closed 策略补充说明
  （迁移失败即退出是为保护旧数据不被空库永久遮挡；仅当**当前库缺失、旧数据存在**时触发；若仅补迁目录失败且当前库可用，仍退出——已知 P2，后续可按需改为降级启动）；目录 promote 严格原子性表述保留在 Handoff 风险节。
- 资源：worktree/task-env 保留（PRESERVE_REFERENCED）；round 1/2 旧证据保留为 SOURCE_PIN。
- 后续（follow-up，不阻塞）：①目录 promote 的严格原子性注记与测试回归（P2）；②`NEWMANGA_DATA_ROOT` 隔离的端到端集成测试（P2）；③GUI 端到端升级验证（B 卡遗留）。
