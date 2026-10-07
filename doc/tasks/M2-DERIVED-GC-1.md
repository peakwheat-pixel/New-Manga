---
id: M2-DERIVED-GC-1
title: derived 只读根 orphan/死行清理第一刀（RC4-12 登记的预览 GC 缺口最小闭合）
kind: feature
status: in_review
delivery_commit: 4edec70a (rework; initial delivery 13964fe2)
handoff: ../handoffs/M2-DERIVED-GC-1-zcode-13964fe2.md
approval: user_2026-10-07_autonomous_mode_continuation（STATUS Planned next 候选②，授权自动选下一最高优先任务）
suggested_owner: Codex Executor
owner: Codex Executor（ZCode 代行）
reviewer: DeepSeek Harness（非作者）
integrator: Codex
depends_on: [M2-RC4-DOMAIN-COMMANDS, M2-PAGE-RESOURCE-RESOLVE-1]
base_commit: d4cd96a7
branch: zcode/derived-gc-1
worktree: G:/CODEX/New Manga.worktrees/DERIVED-GC-1
integration_commit: null
---

# M2-DERIVED-GC-1

## 来源与目标

RC-4 DSH r1 RC4-12（P4，两轮 review 均登记延后）：`render_preview.py` 每次 rerender 以随机 `preview-<uuid4>` 键发布新 PNG 并 `catalog.upsert`；revoke 只标记内存引用表（`service.py:245-280` 只置 `entry.revoked`），**不删 catalog 行、不删 derived 文件**——轮换/失败残留使 previews/ 目录与 resource_catalog 表单调增长。本 Task 交付**启动时 orphan/死行清理第一刀**：零 wire 语义变化的纯内部缓存回收。

## 冻结范围

### GC 语义（保守子集，不触 grant 表/引用层）
- `RenderPreviewPublisher.collect_orphans() -> dict[str, int]`（返回 `{"orphan_files_removed": N, "dead_rows_removed": M}` 统计）：
  1. **orphan 文件**：derived root 的 `previews/` 与 `pages/` 目录内、文件 stem 不在 catalog 行中的文件 → 删除（无 catalog 行即无法被 issue，行为等价于已不可达）。
  2. **死行**：catalog 中 `scope_class='derived-read-only'` 且 `rel_path` 指向文件不存在的行 → `catalog.remove`（与 rev 1.7 自愈语义兼容：resolve 侧 lookup 未命中/文件缺失均走重发布重建，upsert 覆盖同键）。
- 文件删除前 `resolve()` 逃逸检查（`is_relative_to(root)`，与 publish 同款）；只操作 derived root 内 `previews/`、`pages/` 两目录；**绝不触碰 managed 源文件/用户源文件**；catalog 交互仅 `entries()`/`remove()`（既有方法，零 schema 变更）。

### 装配（src/bootstrap/core_service.py）
- `main()` 装配路径（:1689 附近）：`RenderPreviewPublisher` 构建后、`serve_forever()` 前调用一次 `collect_orphans()`，统计打 stderr（`[core.derived_gc] ...`）。
- 失败 fail-soft：GC 异常不阻断服务启动（stderr 记录后继续）。

### 明确不做
- **不回收「有行且有文件」的旧 preview**（活文件按引用/LRU 回收需要 page 关联或 grant 表联动——登记为后续候选，本刀冻结不做）。
- revoke/TTL/grant 语义零变化；契约 M2-C1 零修订（orphan 本就不可 issue、死行本就不可解析——行为等价）。
- React/Rust 零接触（纯 Core 内部）。
- Legacy src/ui 零接触。

## 验收 Gate

1. AC1 Core：`collect_orphans` 单测（orphan 文件删除/死行删除/活文件+活行保留/逃逸防御/统计数正确/删死行后 resolve 自愈重建同键）；focused pytest 全绿。
2. AC2 装配：启动路径调用一次+stderr 统计+GC 异常 fail-soft 不阻断启动（测试钉住）。
3. AC3 回归：全量 pytest 等量递增（1876 基线+新增）；cargo/vitest 基线不变（本 Task 零 React/Rust 改动——cargo/vitest 各跑一轮确认不变量）。
4. 非作者 Review（DSH）通过。

## 完成定义

AC 全过 + Review 通过 + 集成 merge main + STATUS/PLAN 收口。
