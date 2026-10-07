# M2-DERIVED-GC-1 Handoff（Owner→Reviewer/Integrator）

- Owner: Codex Executor（ZCode 代行，持续自治授权）
- Reviewer: DeepSeek Harness（非作者）
- Integrator: Codex
- Task: [M2-DERIVED-GC-1](../tasks/M2-DERIVED-GC-1.md)（release `f1e40631`，base `d4cd96a7`）
- Branch/worktree: `zcode/derived-gc-1` @ `G:/CODEX/New Manga.worktrees/DERIVED-GC-1`
- Delivery head: `13964fe2`（单交付 commit：Core 实现+装配+测试同 commit）

## 交付内容（一句话）

derived 只读根启动时 orphan/死行清理第一刀（RC4-12 登记的预览 GC 缺口最小闭合）：`RenderPreviewPublisher.collect_orphans()` 只回收两类**行为等价于已不存在**的对象——previews//pages/ 下无 catalog 行的 orphan 文件（本就无法被 issue）与 `derived-read-only` 中文件已丢失的死行（本就无法解析，rev 1.7 自愈可重建确定性键）；零 wire 语义变化、零 schema 变化、零 React/Rust 改动。

## 逐层交付（全部 @`13964fe2`）

### Core
- `src/infrastructure/resource_channel/render_preview.py`：`collect_orphans() -> {"orphan_files_removed": N, "dead_rows_removed": M}`——①previews//pages/ 两目录扫描，文件 stem 不在 `derived-read-only` catalog 行中 → 删文件；②catalog 行 rel_path 文件缺失 → `catalog.remove`（既有方法）；每个候选路径 `resolve().is_relative_to(root)` 逃逸检查（与 publish 同款；catalog 的 `upsert` 写入端本就拒绝 traversal，逃逸行只能来自 db 外部篡改——防御针对该场景 fail-closed）；活文件+活行零触碰；只经 `entries()`/`remove()` 交互，零 schema 变更。
- `src/bootstrap/core_service.py`：`_run_startup_gc(previews)` 独立函数（可测）——main() 装配路径 `RenderPreviewPublisher` 构建后、`serve_forever()` 前调用一次；成功打 `[core.derived_gc] orphan_files_removed=N dead_rows_removed=M`、异常打 `[core.derived_gc] skipped: ...` 后继续（fail-soft，GC 永不阻断服务启动）。
- 测试 `tests/core/test_derived_gc.py`（**6 用例**）：两目录 orphan 删除+活文件保留、死行删除+活行保留、**死确定性行 GC 后 resolve 自愈重建同键**（与 rev 1.7 契约互操作）、逃逸行 fail-closed（直接 sqlite 插入绕过 upsert 写入端校验，模拟 db 篡改）、空目录 clean noop、`_run_startup_gc` fail-soft+统计 stderr 双形态。

## 验收对照

| AC | 状态 | 证据 |
|---|---|---|
| AC1 Core 单测 | DONE | focused 四目录 **428 passed**（PAGE-NAV 基线 422 + 本 Task 6 新用例）；raw 日志 `verification/M2-DERIVED-GC-1/raw/focused-pytest-1.log`（HEAD=`13964fe2`，EXIT=0） |
| AC2 装配 | DONE | `_run_startup_gc` fail-soft+统计双形态用例；main() 装配路径调用一次（stderr `[core.derived_gc]`） |
| AC3 回归 | DONE | 全量 pytest **1882 passed+1 skipped+0 failed**（base 1876+1sk +6 新用例，等量递增）；cargo **55+1ign**、vitest **136**、build EXIT=0 基线不变（本 Task 零 React/Rust 改动的不变量确认）；raw 日志 `verification/M2-DERIVED-GC-1/raw/{full-pytest,cargo-test,vitest-run,frontend-build}-1.log`（HEAD=`13964fe2`） |
| AC4 非作者 Review | PENDING | DSH r1（本文档即派发依据） |

## 设计裁定（Reviewer 请特别核验）

1. **「行为等价」论证是本 Task 的安全性根基**：orphan 文件（无 catalog 行）不可被 issue（issue 必经 catalog lookup）；死行（文件缺失）不可被解析——preview 键 issue 走 typed 失败、page-original 键走自愈重发布（upsert 覆盖同键，测试 3 钉住）。删除二者不改变任何可观察行为。
2. **保守子集边界**：只回收 orphan/死行；「有行且有文件的旧 preview」按引用回收需要 page 关联（catalog 无 page 列）或 grant 表联动——**明确不做**，登记为后续候选。revoke/TTL/grant 语义零变化。
3. **写入端已 fail-closed 的分层**：catalog `upsert` 拒绝 traversal rel_path（dto.py 校验），GC 的逃逸检查是针对「db 被外部篡改」的读端防御（测试用 sqlite 直插构造）——两层独立，不互为替代。
4. **fail-soft 而非 fail-closed**：GC 是缓存卫生不是正确性前提，异常不阻断启动（与 region 读取 fail-soft 同哲学）；stderr 统计留观测痕。

## Reviewer 关注点提示

- 实现集中在 `render_preview.py` 的 `collect_orphans`（约 55 行）与 `core_service.py` 的 `_run_startup_gc`（约 15 行）。
- 反向推演点：删掉 `item.stem not in catalogued` 条件（误删活文件）→ 测试 1/2 红；删掉 `is_relative_to` 检查 → 测试 4 红；把 fail-soft 改成 raise → 测试 6 红。
- stem/resource_id 对应关系：previews/ 文件名 `preview-<uuid>.png`、pages/ 文件名 `page-original-{page_id}{suffix}`——`Path.stem` 恰为 resource_id（扩展名被剥离）。
