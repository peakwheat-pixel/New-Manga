# M2-DERIVED-GC-1 Handoff（Owner→Reviewer/Integrator）

- Owner: Codex Executor（ZCode 代行，持续自治授权）
- Reviewer: DeepSeek Harness（非作者）
- Integrator: Codex
- Task: [M2-DERIVED-GC-1](../tasks/M2-DERIVED-GC-1.md)（release `f1e40631`，base `d4cd96a7`）
- Branch/worktree: `zcode/derived-gc-1` @ `G:/CODEX/New Manga.worktrees/DERIVED-GC-1`
- Delivery head: `13964fe2`（单交付 commit：Core 实现+装配+测试同 commit）
- Rework head: `4edec70a`（DSH r1 `approve_with_conditions` 返修，条件 C-1..C-3 全闭合；r1 报告 `doc/reviews/M2-DERIVED-GC-1-13964fe2-dsh-r1.md`）
- Polish head: `9c9c7e55`（DSH r2 `approve` 后顺手闭 N-01/N-02/N-04；r2 报告 `doc/reviews/M2-DERIVED-GC-1-4edec70a-dsh-r2.md`；**本文件以下数字均以 polish head 为准**）

## DSH r2（@`4edec70a`，报告 `doc/reviews/M2-DERIVED-GC-1-4edec70a-dsh-r2.md`）：VERDICT **approve**

C-1/C-2/C-3 全部 **fixed** 判定（两个新用例判别力经 DSH 反向推演证实非伪判别；实现零行为变更经行号不变式佐证——唯一变化是 docstring 增长 8 行）。新发现 N-01..04 全 P4 非阻塞——r2 无条件放行；Owner 顺手闭合（polish commit）：

| 项 | 级 | 处置 |
|---|---|---|
| N-01 「等价于不存在」措辞在 _run_startup_gc docstring 与测试模块 docstring 残留 | P4 | **fixed**——两处统一为「failure-class equivalent」并指向 collect_orphans docstring 为权威表述 |
| N-02 `import _winapi` 无平台守卫 | P4 | **fixed**——补 `sys.platform != "win32"` → `pytest.skip`（沿 transport_credential_assembly 先例） |
| N-03 Task 标题「最小闭合」误读风险 | P4 | **收口处理**——STATUS/PLAN 收口按 **PARTIAL mitigation** 记录（orphan/死行子集闭合、轮换增长路径保持 open），release 冻结文本不回改 |
| N-04 PR-06 disposition 声称「登记 docstring」与事实不符 | P4 | **fixed**——表述更正为「登记于本表与 Handoff」 |

## DSH r1 逐项 disposition（r1 @`13964fe2`；rework `4edec70a`）

| 项 | 级 | 处置 |
|---|---|---|
| C-1（PR-02）scope_class 过滤无测试钉住——删过滤 managed 行会被误删 | P3 | **fixed**——新增 `test_managed_scope_rows_are_never_touched_by_the_sweep`（managed-read-only 死行保留；删过滤即红） |
| C-2（PR-03/PR-05）目录级逃逸检查无测试覆盖+Handoff 表述高估 | P3 | **fixed**——新增 `test_directory_level_escape_fails_closed`（`_winapi.CreateJunction` 把 previews/ 指到 root 外，断言 OSError 且 root 外文件存活）；Handoff 逃逸表述收窄为「目录级门+行级候选检查」 |
| C-3（PR-01/PR-04）「行为等价」表述与 typed code 事实有偏差+RC4-12 主增长路径未触及 | P3 | **fixed**——docstring 精确化（preview 死行 issue 由 `REF_NOT_FOUND`/404 变 `RESOURCE_NOT_CATALOGED`/400，同为 typed 硬失败不服务字节）；RC4-12 定性 **PARTIAL mitigation**（轮换增长路径保持 open）；Handoff/收口同步 |
| PR-06 单点失败中止整刀 | P4 | **accepted**——DSH 自证状态一致安全+幂等重试；fail-closed 取舍登记于本表与 Handoff（r2 N-04 更正：collect_orphans docstring 不含该取舍表述，以本 disposition 为登记处） |
| PR-07 删除面前置条件 | P4 | **fixed（docstring）**——补「root 必须是 derived 只读根且两目录由本 publisher 独占」 |
| PR-08 统计虚增/悬空链接保守泄漏/O(N) 扫描/except Exception 吞域 | P4 | **accepted 登记**——均无安全影响；DSH 逐项核对含 Ctrl-C 不被吞 ✓ |

## 交付内容（一句话）

derived 只读根启动时 orphan/死行清理第一刀（RC4-12 登记的预览 GC 缺口 **PARTIAL mitigation**——orphan/死行子集闭合，轮换增长路径保持 open）：`RenderPreviewPublisher.collect_orphans()` 只回收两类**失败类等价**的对象——previews//pages/ 下无 catalog 行的 orphan 文件（本就无法被 issue）与 `derived-read-only` 中文件已丢失的死行（page-original 键自愈重建同键；preview 键 issue 的 typed code 由 `REF_NOT_FOUND`/404 变 `RESOURCE_NOT_CATALOGED`/400，同为 typed 硬失败不服务字节）；零 wire 语义变化、零 schema 变化、零 React/Rust 改动。

## 逐层交付（全部 @`13964fe2`）

### Core
- `src/infrastructure/resource_channel/render_preview.py`：`collect_orphans() -> {"orphan_files_removed": N, "dead_rows_removed": M}`——①previews//pages/ 两目录扫描，文件 stem 不在 `derived-read-only` catalog 行中 → 删文件；②catalog 行 rel_path 文件缺失 → `catalog.remove`（既有方法）；**目录级** `resolve().is_relative_to(root)` 门（previews//pages/ 各一，unlink 循环唯一前门）+**行级**候选检查（针对 db 外部篡改；catalog 的 `upsert` 写入端本就拒绝 traversal——防御双层独立）；活文件+活行零触碰；只经 `entries()`/`remove()`，零 schema 变更。前置条件（docstring 冻结）：root 必须是 derived 只读根、两目录由本 publisher 独占。
- `src/bootstrap/core_service.py`：`_run_startup_gc(previews)` 独立函数（可测）——main() 装配路径 `RenderPreviewPublisher` 构建后、`serve_forever()` 前调用一次；成功打 `[core.derived_gc] orphan_files_removed=N dead_rows_removed=M`、异常打 `[core.derived_gc] skipped: ...` 后继续（fail-soft，GC 永不阻断服务启动）。
- 测试 `tests/core/test_derived_gc.py`（rework 后 **8 用例**）：两目录 orphan 删除+活文件保留、死行删除+活行保留、**死确定性行 GC 后 resolve 自愈重建同键**（与 rev 1.7 契约互操作）、逃逸行 fail-closed（直接 sqlite 插入绕过 upsert 写入端校验，模拟 db 篡改）、**managed scope 行绝不被 sweep 触碰**（r1 C-1：删 scope 过滤即红）、**目录级逃逸 fail-closed**（r1 C-2：`_winapi.CreateJunction` 将 previews/ 指向 root 外，断言 OSError 且 root 外文件存活）、空目录 clean noop、`_run_startup_gc` fail-soft+统计 stderr 双形态。

## 验收对照

| AC | 状态 | 证据 |
|---|---|---|
| AC1 Core 单测 | DONE | focused 四目录 **430 passed**（PAGE-NAV 基线 422 + 本 Task 8 新用例：6 交付+2 r1 返修）；raw 日志 `verification/M2-DERIVED-GC-1/raw/focused-pytest-1.log`（HEAD=`9c9c7e55`，EXIT=0） |
| AC2 装配 | DONE | `_run_startup_gc` fail-soft+统计双形态用例；main() 装配路径调用一次（stderr `[core.derived_gc]`；DSH r1 独立证实 raw cargo 日志内 4 次真实 sidecar spawn 均打印 GC 统计=装配证据强于单测） |
| AC3 回归 | DONE | 全量 pytest **1884 passed+1 skipped+0 failed**（base 1876+1sk +8 新用例，等量递增）；cargo **55+1ign**、vitest **136**、build EXIT=0 基线不变（本 Task 零 React/Rust 改动的不变量确认）；raw 日志 `verification/M2-DERIVED-GC-1/raw/{full-pytest,cargo-test,vitest-run,frontend-build}-1.log`（HEAD=`9c9c7e55`） |
| AC4 非作者 Review | DONE | r1 [approve_with_conditions](reviews/M2-DERIVED-GC-1-13964fe2-dsh-r1.md)（0×P0/P1/P2；3×P3 条件+5×P4）→ rework `4edec70a` C-1..C-3 全闭合 → r2 [approve](reviews/M2-DERIVED-GC-1-4edec70a-dsh-r2.md)（N-01..04 P4 顺手闭合） |

## 设计裁定（Reviewer 请特别核验）

1. **「行为等价」论证是本 Task 的安全性根基**：orphan 文件（无 catalog 行）不可被 issue（issue 必经 catalog lookup）；死行（文件缺失）不可被解析——preview 键 issue 走 typed 失败、page-original 键走自愈重发布（upsert 覆盖同键，测试 3 钉住）。删除二者不改变任何可观察行为。
2. **保守子集边界**：只回收 orphan/死行；「有行且有文件的旧 preview」按引用回收需要 page 关联（catalog 无 page 列）或 grant 表联动——**明确不做**，登记为后续候选。revoke/TTL/grant 语义零变化。
3. **写入端已 fail-closed 的分层**：catalog `upsert` 拒绝 traversal rel_path（dto.py 校验），GC 的逃逸检查是针对「db 被外部篡改」的读端防御（测试用 sqlite 直插构造）——两层独立，不互为替代。
4. **fail-soft 而非 fail-closed**：GC 是缓存卫生不是正确性前提，异常不阻断启动（与 region 读取 fail-soft 同哲学）；stderr 统计留观测痕。

## Reviewer 关注点提示

- 实现集中在 `render_preview.py` 的 `collect_orphans`（约 55 行）与 `core_service.py` 的 `_run_startup_gc`（约 15 行）。
- 反向推演点：删掉 `item.stem not in catalogued` 条件（误删活文件）→ 测试 1/2 红；删掉 `is_relative_to` 检查 → 测试 4 红；把 fail-soft 改成 raise → 测试 6 红。
- stem/resource_id 对应关系：previews/ 文件名 `preview-<uuid>.png`、pages/ 文件名 `page-original-{page_id}{suffix}`——`Path.stem` 恰为 resource_id（扩展名被剥离）。
