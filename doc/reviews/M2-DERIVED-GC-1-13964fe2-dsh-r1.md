VERDICT: approve_with_conditions

结论摘要：**未发现 P0/P1/P2 行为缺陷**。AC1-AC3 的证据链与 raw 日志逐条对得上（详见下「已核对无问题」）；`collect_orphans` 的两类回收对象在**新 issue / 解析语义**上确实等价，代码只经 `entries()/remove()`，零 schema、零契约、零 React/Rust 改动。给出的条件全部是**证据完整性 / 文档精确性**（3 条 P3），不需要改实现逻辑。

> 审查限制（如实声明）：本会话 shell 被沙箱拒绝（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`，且无审批通道，无法 escalate），因此**无法执行 `git diff`，也未重跑任何测试**（符合 Task 要求）。diff 级事实以下列只读证据交叉核验：worktree reflog（`G:/CODEX/New Manga/.git/worktrees/DERIVED-GC-1/logs/HEAD`）、`verification/M2-DERIVED-GC-1/raw/*` 与 `verification/M2-PAGE-NAV-PROJECTION-1/raw/*` 基线日志、全仓符号 grep。

---

## 一、逐条发现

### PR-01（P3）「行为等价」在 preview 死行上并非严格恒等：issue 的 typed code 会变
- 位置：`src/infrastructure/resource_channel/render_preview.py:116-120`（docstring 声称 `preview issues fail typed`）、`src/infrastructure/resource_channel/host_bridge.py:87-93`、`apps/desktop/src-tauri/src/resource_protocol.rs:100-109`
- 事实链：死行（文件缺失、行仍在）时 `issue` → `catalog.lookup` 命中 → `capture_facts` 打开失败 → `E_OPEN_FAILED`→`E_NOT_FOUND` ⇒ `REF_NOT_FOUND`（asset 协议 `status_for` 映射 **404**）。GC 删行后同一请求 → `lookup` 未命中 ⇒ `RESOURCE_NOT_CATALOGED`（`status_for` 落入 `_ => 400`，**400**）。page-original 键则由 `core_service.py:1024-1033` 自愈重发布（真等价，测试 3 钉住）。
- 影响：两条路径都**不服务任何字节**、都是 typed 硬失败，前端 `WorkbenchPage.tsx:767-776` 只是把 code 字符串显示出来 ⇒ 实际影响≈0。但这与冻结文档「死行本就不可解析——行为等价」的字面表述不完全一致。
- 建议处置：不改代码；在 docstring / Handoff / 收口文档把该条改成「等价到同一失败类（不服务字节）；typed code 由 `REF_NOT_FOUND` 变为 `RESOURCE_NOT_CATALOGED`，asset status 404→400」。

### PR-02（P3）`scope_class` 过滤无测试钉住（反向推演不会红），而它是加载性的
- 位置：`src/infrastructure/resource_channel/render_preview.py:130-131`（`if entry.scope_class == "derived-read-only"`）
- 反向推演：删掉该过滤条件，`tests/core/test_derived_gc.py` 6 用例**全绿**（无任何 managed 行用例）。
- 真风险场景：同一个 `M2RC2_CATALOG_DB` 里同时存在 `managed-read-only` 行（写入端 `src/bootstrap/acceptance_bridge.py:420-424`，`RESOURCE_ID_TEMPLATE="m2ac1-page-{index}"`，`rel_path` 相对 **managed 根**）。若过滤丢失，行循环会用 **derived 根**去拼这些 `rel_path`（`render_preview.py:149`）→ 文件不存在 → `catalog.remove` 误删 managed 行 → managed 页 issue 全线 `RESOURCE_NOT_CATALOGED`。
- 建议处置：加一条用例——`catalog.upsert("m2ac1-page-0", "managed-read-only", "books/b1/chapters/c1/translated/x.png")`（文件不存在）后 `collect_orphans()`，断言 `dead_rows_removed == 0` 且该行仍在。

### PR-03（P3）目录级逃逸检查（文件删除路径唯一的门）无测试覆盖
- 位置：`src/infrastructure/resource_channel/render_preview.py:139-141`
- 反向推演：删掉 `if not resolved_dir.is_relative_to(root): raise`，6 用例**全绿**——测试 4（`test_escaping_catalog_row_fails_closed`）只覆盖**行级**检查（`:150-151`）。
- 定性：实现本身与冻结文本「与 publish 同款」一致（`publish` 也是目录级：`:45-46`、`:84-85`），且目录级对 `iterdir()` 的条目是**充分**的（条目是已解析目录的直接子项；符号链接条目被 `unlink` 时只删链接本身）。因此这是**证据缺口**而非实现缺陷；但 Handoff:17 写成「每个候选路径 resolve().is_relative_to(root)」属高估（见 PR-05）。
- 建议处置：加一条用例（`previews/` 做成指向 root 外的 junction/symlink，断言 `OSError` 且 root 外文件未被删），或在 Handoff 如实收窄为「文件循环=目录级检查、行循环=候选级检查，目录级未单独用例覆盖」。

### PR-04（P3）RC4-12 的**主增长机制**未被本刀触及，「最小闭合」措辞有误读风险
- 位置：`src/infrastructure/resource_channel/render_preview.py:145`（`stem in catalogued` 即保留）；`apps/desktop/src-tauri/src/main.rs:411-425`（轮换只 `revoke_resource`，只置内存 `revoked`，见 `src/application/resource_channel/service.py:245-279`）
- 事实：正常轮换后，旧 preview **行在、文件在** ⇒ GC 恒不回收。RC4-12 原文（`doc/reviews/M2-RC4-DOMAIN-COMMANDS-1e6b58b9-dsh-r2.md:54`）正是「轮换/撤消失败后旧文件与旧 catalog 行不回收，长期增长」。本刀只清 orphan（无行）与死行（无文件），轮换增长路径**零改善**（Task 已用「明确不做」诚实声明，但标题/来源「RC4-12 登记的预览 GC 缺口最小闭合」容易被收口时误记为 closed）。
- 建议处置：收口时把 RC4-12 登记为 **partial mitigation**（orphan/死行子集已闭；轮换路径保持 open，后续候选需要 page 关联或 grant 联动），避免下一轮 review 误判缺口已关闭。

### PR-05（P4）Handoff 逃逸检查描述与实现不符（文档精度）
- 位置：`doc/handoffs/M2-DERIVED-GC-1-zcode-13964fe2.md:17` vs `render_preview.py:139-141` / `:149-151`
- 建议处置：改为「目录级 + 行级候选检查」，与代码一致（PR-03 一并修）。

### PR-06（P4）单点失败中止整刀：状态一致但清理能力被一条坏项阻塞
- 位置：`render_preview.py:146`（`unlink` 抛 `PermissionError`，Windows 上文件被 host reader 持有时会发生）、`:150-151`（一条畸形行即 `raise`）
- 事实：任一异常都会中止整个 sweep（`core_service.py:1712` 吞掉后 continue），本次启动只完成「已经做掉的那部分」。**状态一致性我已逐序核对为安全**：文件循环删除的对象必然无行；行循环只删文件已缺失的行；二者交错也不产生「有行但文件被 GC 删掉」的 torn state。只是剩余清理要等下次启动。
- 建议处置：可接受（fail-closed + 幂等重试）；若想更稳，可在两个循环内 per-item `try/except` 记录后继续，或把该取舍写进 docstring。

### PR-07（P4）删除面是「两目录内一切未知文件」：临时残留与误配置爆炸半径
- 位置：`render_preview.py:135-147`
- 事实：`publish/publish_original` 用 `tempfile.NamedTemporaryFile(dir=...)`（无扩展名，stem=`tmpXXXX`），崩溃残留会被清掉（**这是好事**）；但同一逻辑意味着任何未来写入者放进这两个目录、又没登记 catalog 的文件都会被静默删除。另外若 operator 把 `M2RC1_DERIVED_ROOT` 指到 managed 根（D03 布局同样有 `previews/`，见 `src/ports/repositories/storage.py:3-7`），managed 预览会被当 orphan 删除（生产/打包装配下二者是 `user_root/derived` 与 `user_root/managed`，`main.rs:664-683` 不同路径，故不是现有路径缺陷）。
- 建议处置：在 docstring 明确「root 必须是 derived 只读根、且这些目录由本 publisher 独占」的前置条件（或限定文件名模式，但会漏清，不推荐）。

### PR-08（P4）小 nit 汇总
- `render_preview.py:146-147`：`unlink(missing_ok=True)` 后无条件 `removed_files += 1`，外部先删时会虚增统计（无安全影响）。
- `render_preview.py:143-144`：`is_file()` 会跳过悬空符号链接与子目录 ⇒ 保守泄漏（不会误删，符合「保守子集」取向）。
- `render_preview.py:129-130`：启动即 `mkdir` derived root 并全量 `entries()` 载入内存；catalog 正是长期增长对象，故 sweep 为 O(N)/启动一次。可接受，记录即可。
- `core_service.py:1712`：`except Exception` 会连 `TypeError/KeyError`（如 stats 形状变化）一起吞掉，但均留 `[core.derived_gc] skipped: ...` stderr 痕，符合 AC2 fail-soft 边界；未吞 `BaseException`（Ctrl-C 不被吞）✓。

---

## 二、已核对、未发现问题的关键点（含未发现问题的区域）

1. **AC1 证据链**：`raw/focused-pytest-1.log:3,4,21,67` → HEAD=`13964fe2`、命令与基线**逐字相同**（`tests/core tests/editing tests/rendering tests/m2_resource_channel -q`）、428 passed、EXIT=0；基线 `M2-PAGE-NAV-PROJECTION-1/raw/focused-pytest-1.log:4,21` = 422 ⇒ 差值恰为 `test_derived_gc.py` 的 6 个用例。
2. **AC2 证据链**：`raw/cargo-test-1.log:77-80` 出现 4 行 `[core.derived_gc] orphan_files_removed=0 dead_rows_removed=0`——即 **Rust 侧真实 spawn 的 `-m bootstrap.core_service`**（`library_bridge.rs:184-186,207-232`）在生产装配路径上确实跑了一次 GC，且实验室根下 0 误删。这是比单测更强的装配证据。单测侧 `test_startup_gc_is_fail_soft_and_logs_a_summary` 双形态（skipped / 统计）钉住 `core_service.py:1699-1713`。
3. **AC3 证据链**：`raw/full-pytest-1.log:3,4,399,400` = 1882 passed/1 skipped/EXIT=0 vs 基线 1876+1sk（+6 等量递增，命令同为 `pytest -q`）；`cargo 55 passed; 0 failed; 1 ignored`、`vitest 136 passed (12 files)`、`npm run build` EXIT=0，与 PAGE-NAV 基线逐项相同 ⇒ 零 React/Rust 改动的不变量成立。
4. **commit 链核验**：reflog = `d4cd96a7`（base，与 Task:14 一致）→ `f1e40631`（release 冻结）→ `13964fe2`（feat 交付，当前 HEAD）→ `ea757205`（docs/handoff+raw 日志），branch `refs/heads/zcode/derived-gc-1`，与 Task/Handoff 自述完全一致。
5. **「orphan 不可被 issue」端到端核对通过**：`host_bridge.py:87-93` 强制 `catalog.lookup`，行缺失即 `RESOURCE_NOT_CATALOGED`；`_CORE_OWNED_ISSUE_PARAMS`（`:43,82-86`）拒绝 host 传 `rel_path/scope_class`；`service.issue` 只接受 Core 自己查出的 `rel_path`（`service.py:81-106`）。除此之外**没有任何**「按 rel_path 直通发引用」的面（Rust `main.rs:444-455` 只传 resource_id+revision）。唯一残留前提：*已签发*的 in-memory grant 在**另一个进程**中仍可读该文件——但行只能被「文件已缺失」的 GC 或外部改库删除，且本进程启动时 grant 表必为空（`service.py:10-14`）⇒ 生产路径等价成立（建议把该前提写进 docstring，见 PR-07）。
6. **死行删后自愈等价**：`core_service.py:1024-1033`（`lookup` 未命中 → `publish_original` → `upsert` 同键）+ 测试 3（`test_dead_deterministic_row_self_heals_to_same_key_after_gc`）双向钉住；`ORIGINAL_REVISION="original"` 常量两分支共用（`render_preview.py:17`）。
7. **活文件+活行零触碰**：只有「stem 不在 catalog」才 unlink（`:145-146`），只有「文件缺失」才 remove（`:152-154`）；测试 1/2 断言活文件与活行存活 ✓。
8. **逃逸与越权面**：`previews/pages` 目录级 `resolve().is_relative_to(root)`（`:139-141`）在**任何删除之前** fail-closed；行级候选检查 `:149-151`；`unlink` 仅删目录项（符号链接不追目标、硬链接不影响源）⇒ managed/用户源文件不可能被触及（PR-07 的误配置前提除外）。
9. **零契约/零 schema**：`collect_orphans` 只用既有 `entries()`（`catalog_store.py:109-115`）与 `remove()`（`:83-89`，基线 `tests/m2_resource_channel/test_catalog_authority.py:59-61` 已存在）；无新错误码（`dto.py:72-89` 未动）；`PROTOCOL_MINOR=6`（`core_service.py:159`）未 bump；`M2-C1` 最新 revision 仍是 1.8（M2-PAGE-NAV-PROJECTION-1 冻结）⇒ 「零修订」属实。
10. **反向推演**：删 `item.stem not in catalogued` → 测试 1/2 红 ✓；删行级 `is_relative_to` → 测试 4 红 ✓；fail-soft 改 raise → 测试 6 红 ✓。**不会红的两处已单列为 PR-02/PR-03**。
11. **确定性与遍历**：`sorted(resolved_dir.iterdir())`（`:142`）确定性排序；`entries()` 自带 `ORDER BY resource_id` ⇒ raise/中断点可复现。
12. **改造面收敛**：全仓 grep `collect_orphans|_run_startup_gc|derived_gc` 仅命中 `render_preview.py`、`core_service.py`、`tests/core/test_derived_gc.py` 与文档；Rust/TS/QML 无新符号引用（`src/ui` 命中 0）⇒ React/Rust/Legacy src/ui 未接触（弱证据，diff 受限见上文声明）。
13. **未发现问题区域**：`publish`/`publish_original`/`artifact_exists`/`lookup` 语义未被改动；`catsslog` 并发模型（单锁、单写者）与 GC 的启动时序无竞态（GC 在任何 publish 之前，单写者进程内）。

---

## 三、条件（Conditions，进入 `done` 前闭合；均为证据/措辞，不改实现逻辑）

- **C-1**（对应 PR-02）：新增「`managed-read-only` 死行必须保留」用例（跨 scope 原子性钉住）。
- **C-2**（对应 PR-03、PR-05）：补目录级逃逸用例；若不做，则在 Handoff/收口文档把「逃逸防御」证据范围如实收窄到行级候选，并修正「每个候选路径」表述。
- **C-3**（对应 PR-01、PR-04）：收口文档精确化「行为等价」为「同一失败类（typed code/asset status 可能不同）」，并把 RC4-12 记为 **partial mitigation**（轮换路径仍未回收）。

---

## 四、推荐下一步

1. **Task**：M2-DERIVED-GC-1 r1 返修（闭合 C-1..C-3）——仅测试 + 文档，无共享接口/Schema 改动授权需求。
2. **Agent**：Owner = ZCode（原实现者，返修 own 代码）；Reviewer 保持 DeepSeek Harness（本 r1）；集成 = Codex。
3. **Recovery point**：`G:/CODEX/New Manga.worktrees/DERIVED-GC-1`，branch `zcode/derived-gc-1`，base `d4cd96a7`，head `13964fe2`（返修产生新 commit，需重跑 focused/full pytest 并更新 raw 日志 HEAD 行）。
4. **Verification**：`python -m pytest tests/core tests/editing tests/rendering tests/m2_resource_channel -q`（期望 428+新增）与全量 `pytest -q`（1882+新增，0 failed）；cargo/vitest/build 因零 React/Rust 改动可只声明不变量（如实现未动可免跑，按 AC3 口径记录）。
5. **Forwardable instruction**：「在 worktree `G:/CODEX/New Manga.worktrees/DERIVED-GC-1`（branch `zcode/derived-gc-1`，base `d4cd96a7`，head `13964fe2`）按 DSH r1 Review 的条件 C-1..C-3 返修 M2-DERIVED-GC-1：①在 `tests/core/test_derived_gc.py` 增加一条 `managed-read-only` 死行保留用例；②补目录级逃逸用例或在 Handoff 收窄逃逸证据表述；③在 docstring/Handoff/收口文档精确化 preview 死行的 typed code 差异并声明 RC4-12 为 partial mitigation。不改 `collect_orphans` 行为逻辑、不改契约/Schema、不触 React/Rust/src-ui。提交后重跑 focused + 全量 pytest 并把 raw 日志写入 `verification/M2-DERIVED-GC-1/raw/`，更新 Handoff 后交回 DSH r2。」

若 Codex 认为 C-1..C-3 可转为「登记 deferred（非阻塞）」，则本 r1 可等价结论为 **approve**（0×P0/P1/P2），后续按 r2 复核措辞与用例即可。
