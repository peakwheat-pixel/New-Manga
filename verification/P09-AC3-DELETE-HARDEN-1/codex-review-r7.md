<!-- codex session: 01a15233-102d-7811-be9b-d0f5d84a8b4a | reviewed_head: 2ba73a5e3 -->

# P09-AC3-DELETE-HARDEN-1 R7

- **reviewed_head:** `2ba73a5e3df01346543cebc04bb90f4db23077fb`
- **decision:** `changes_requested`
- **findings:** 4 open — 1 unresolved P1 from R6 and 3 new P2 findings

## R6 后各项判断

1. **publish cleanup 修复：PASS。** `_cleanup_quietly` 沿 handle chain 清理；发布清理探针在旧版失败、当前版通过。动态红绿对比直接调用了 `publish_original`；我没有单独动态触发另一条 `publish()` 分支。
2. **P2 draft 纳入 `resolve_namespace_identity`：PARTIAL。** 函数已列入 draft 说明，但正式 Task scope 和 AC3 仍未纳入，见下方 P2。
3. **AC4 未修复：确认。** 独立复现了预览行和文件残留，AC4 判 `FAIL`。
4. **探针判别力：PASS。** 三组旧版/当前版对照都得到预期红绿结果，细节见下表。

## 必需验证

表中 `injection_fired` 表示攻击注入触发；对预置 junction 的探针，它表示攻击 fixture 已建立并通过断言。`outside_survived` 单独报告被保护的外部文件是否仍存在。

| Probe | injection_fired | outside_survived | 结果 |
|---|---:|---:|---|
| `n002-race-probe2.py` | True | True | SAFE |
| `n004-ancestor-probe.py` | True | True | SAFE |
| `n004-production-order-probe.py` | True（junction fixture 已断言） | True | SAFE |
| `r5-p1-managed-remove-probe.py` | True（junction fixture 已断言） | True | SAFE |
| `r5-p1-cleanup-book-files-probe.py` | True（root junction fixture 已断言） | True | SAFE |
| `r5b-p1-remove-managed-race-probe.py` | True | True | SAFE |
| `r5b-p1-collect-orphans-race-probe.py` | True | True | SAFE |
| `r6-p1a-publish-cleanup-race-probe.py` | True | True | SAFE |
| 额外检查：`n002-race-probe.py` | **False** | True | **INCONCLUSIVE**；`Path.is_file` hook 未触发 |

我也在 `%TEMP%` 的旧代码快照上运行了三组对照，没有 checkout 或改动仓库：

| Probe | 旧版结果 | 当前版结果 |
|---|---|---|
| managed remove race（旧快照 `f25d41d50^`） | `injection_fired=True`，`outside_survived=False`，VULNERABLE | `True`，`True`，SAFE |
| collect orphans race（旧快照 `652d88e65^`） | `True`，`False`，VULNERABLE | `True`，`True`，SAFE |
| publish cleanup（旧快照 `897e48042^`） | `True`，`False`，VULNERABLE | `True`，`True`，SAFE |

测试结果：

- `tests/storage`：86 passed。
- `tests/core`：558 passed，另有 1 条 Pillow deprecation warning。
- `verify_all.py`：exit 0。为避免改写仓库里已 pin 的 evidence，我在当前 HEAD 的隔离快照中运行；删除验收查询、源文件保护与孤儿扫描均通过。
- **NOT_VERIFIED：**没有运行完整 `pytest tests`、Cargo、前端或 packaging 测试，因此 AC12、Rust/UI 相关部分不能据此判通过。

## AC4 调查

AC4 的 key mismatch 和残留确实存在。读取 5 次后有 5 条 `preview-*` 行；永久删除后仍有 **5 条预览行和 5 个预览 PNG**（另有生命周期 lock 文件）。确定性清理查找的是 `page-original-p1`，找不到这些 UUID key。

我没有发现当前清理路径可用来可靠区分“仍在用”的行：

- 5 条记录具有相同的 `artifact_id` 和 `artifact_revision_id`，所以 revision match 无法挑出当前行。
- 这 5 条 reader projection 记录均为 `retired=0`；reader projection 路径不会通过 rerender rotation 退休记录。
- ResourceChannel 的 grant 表可能提供每个 key 的临时授权信息，但 `cleanup_book_files` 没有用它，也没有对应的生命周期关联。WebView 当前引用没有传给清理路径。
- 所以“grant 或 WebView 当前引用”目前不能证明哪个 lifecycle row 是唯一 live row。清理期间的在途读取和书本删除后的引用如何失效，仍需在修复方案里定明。已加载成 Blob 的图片是否需要继续保留，现有证据不足以断言。

另一个实现问题是 AC4 方向方案的查询时序：它计划在 `cleanup_book_files` 中从 `media_artifacts` 反查 artifact，但生产路径先执行数据库永久删除、删除 artifact rows，再调用文件清理。按现有顺序实施该查询会缺少映射，修复仍可能漏掉 preview 行。见 [AC4 方向方案](<G:/CODEX/New Manga/verification/P20-CLOSE-BOUND-HARDEN-2/ac4-direction-1-plan.md:73>)、[永久删除调用顺序](<G:/CODEX/New Manga/src/bootstrap/core_service.py:1139>) 和 [数据库删除实现](<G:/CODEX/New Manga/src/infrastructure/sqlite/library.py:1053>)。

## AC1–AC12

| AC | R7 verdict | 依据 |
|---|---|---|
| AC1 | **PARTIAL** | `tests/core` 覆盖 Core route；本轮未跑 Tauri 和前端验证。 |
| AC2 | **PASS** | `tests/core` 通过。 |
| AC3 | **PARTIAL** | Core 测试通过；前端 mixed-batch retry 行为本轮未验证。 |
| AC4 | **FAIL** | 永久删除后实测仍有 5 条预览行和 5 个 PNG。 |
| AC5 | **PASS** | Storage 测试及 junction/竞态探针通过，外部文件存活。 |
| AC6 | **PASS** | Core 测试与隔离快照的 `verify_all.py` 验证通过。 |
| AC7 | **PASS** | 当前 HEAD 隔离快照运行 `verify_all.py`，验收查询通过。 |
| AC8 | **PASS** | Storage/Core 测试通过；清理范围探针通过。 |
| AC9 | **NOT_VERIFIED** | 本轮未运行 Cargo 测试。 |
| AC10 | **NOT_VERIFIED** | 本轮未运行 packaging 测试。 |
| AC11 | **PARTIAL** | P09 AC3 delete 子条件仍为 `BLOCKED`；但 Task `delivery_head` 与当前 reviewed head 不一致。 |
| AC12 | **NOT_VERIFIED** | 本轮只运行了 storage、core 和定向验收；未运行完整回归集。 |

P09 AC3 delete 子条件仍为 **`BLOCKED`**，符合硬约束；未将其判为 PASS。该状态见 [STATUS](<G:/CODEX/New Manga/doc/STATUS.md:12>) 和 [P09 Task](<G:/CODEX/New Manga/doc/tasks/P09.md:59>)。

## Findings

1. **P1 — AC4 预览残留仍未解决。** [render_preview.py](<G:/CODEX/New Manga/src/infrastructure/resource_channel/render_preview.py:69>) 为每次发布生成 `preview-<uuid>`；[library.py](<G:/CODEX/New Manga/src/infrastructure/sqlite/library.py:1124>) 按 `page-original-<page_id>` 清理。复现：5 次读取后永久删除，剩 5 条 preview lifecycle rows 与 5 个 PNG。**这是 R6 延续的未关闭 finding。**

2. **P2 — AC4 方向方案在映射查询前删除数据。** 方案拟在清理阶段从 `media_artifacts` 找 artifact，但生产删除流程已先删这些行，查询会失去映射。复现：按当前永久删除顺序执行，随后不存在可供该查询反查的 `media_artifacts` rows。

3. **P2 — P2 draft 的 resolver 范围没有写进正式 Task scope。** draft 的说明列出 `resolve_namespace_identity`，但正式 scope 和 AC3 清单仍未纳入。见 [draft scope](<G:/CODEX/New Manga/verification/P20-CLOSE-BOUND-HARDEN-2/r5b-p2-read-path-draft.md:76>) 和 [AC3](<G:/CODEX/New Manga/verification/P20-CLOSE-BOUND-HARDEN-2/r5b-p2-read-path-draft.md:83>)。

4. **P2 — Task 交付指针落后于被审查的修复。** Task frontmatter 的 `delivery_head` 仍为 `652d88e6513128023d120c99bfd05a8f8544dc13`，本轮实际 HEAD 是 `2ba73a5e3df01346543cebc04bb90f4db23077fb`；指针没有覆盖后续 R6 修复提交。见 [Task delivery_head](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:17>)。应更新交付指针及对应 Handoff/evidence。

**Standards：** 本轮代码差异没有发现新的代码规范问题。  
**Spec：** AC4 仍失败，且其修复方案和 resolver handoff 范围存在上述缺口。

**Ready for integration (done)? No.** AC4 的 P1 未关闭，另有计划和交付指针问题；本轮不应集成或关闭 Task。

**推荐下一步：** 修订 AC4 方案，使 artifact/resource 映射在数据库删除前可用，并明确永久删除时 grant、在途读取及旧 WebView 引用的失效规则；加入“读多次后永久删除”的残留归零验证，随后更新交付指针并提交 R8 复审。本轮未修改仓库文件。