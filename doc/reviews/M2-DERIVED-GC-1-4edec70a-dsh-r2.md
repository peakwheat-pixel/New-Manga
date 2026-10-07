## VERDICT: approve

> 审查限制（如实声明，与 r1 同）：本会话 shell 仍被沙箱拒绝（`SetNamedSecurityInfoW failed (Win32 5)`），一次 `danger-full-access` escalate 也因"无可用审批通道"失败；`web_search` 返回 HTTP 401（搜索端点未配置）。因此**未执行 `git diff`、未重跑测试**（符合只读审查要求）。diff 级事实改用：worktree reflog（`G:/CODEX/New Manga/.git/worktrees/DERIVED-GC-1/logs/HEAD`，本次已独立读取）、全仓符号 grep、以及 r1 报告锚点与当前源码的**行号对齐不变式**（下详）。

结论摘要：**C-1/C-2/C-3 全部 fixed**，0×P0/P1/P2。两个新用例的判别力经反向推演均成立（不是"恒绿"用例），r2 raw 日志 5 份 HEAD 行全部自述 `4edec70a` 且数字与 Handoff 逐项一致，返修对 `collect_orphans`/`_run_startup_gc` 是**文档级零行为变更**。新增 4 条 P4 文档/可移植性 nit，均不阻塞、建议收口时一并处理。

---

## 一、逐项判定（C-1..C-3）

| 条件 | 判定 | 一句证据 |
|---|---|---|
| **C-1**（原 PR-02）managed-read-only 死行保留用例 | **fixed** | `tests/core/test_derived_gc.py:120-136` 新增 `test_managed_scope_rows_are_never_touched_by_the_sweep`：upsert `m2ac1-page-0`/`managed-read-only`/`books/b1/...` 后断言 `stats == {orphan:0, dead_rows:0}` 且 `lookup(...) is not None`；且 `catalog_store.py:83-89 remove()` 与 `:109-115 entries()` **均无 scope 条件**，删掉 `render_preview.py:138-139` 的过滤必然误删该行 ⇒ 用例必红，判别力成立 |
| **C-2**（原 PR-03/PR-05）目录级逃逸用例 + Handoff 表述收窄 | **fixed** | `tests/core/test_derived_gc.py:139-169` 新增 `test_directory_level_escape_fails_closed`：`_winapi.CreateJunction(str(outside), str(junction))` 把 `previews/` 指到 root 外，`pytest.raises(OSError, "escaped derived root")` + `outside/keep-me.txt` 存活 + `preview-keep` 行未删；`Handoff:29` 已收窄为「**目录级**门（unlink 循环唯一前门）+**行级**候选检查」 |
| **C-3**（原 PR-01/PR-04）docstring 精确化 + Handoff 同步 | **fixed** | `render_preview.py:107` 已标 `PARTIAL mitigation`；`:120-126` 精确化为「page-original 自愈同键；preview issue 由 `REF_NOT_FOUND`(404) → `RESOURCE_NOT_CATALOGED`(400)，both typed hard failures，serve no bytes」；`:128-131` 明写「rotation growth path = registered follow-up, out of scope」；`Handoff:24` 一句话交付同步含 PARTIAL mitigation + typed code 差异 |

---

## 二、新发现（均非阻塞）

**N-01｜P4｜`src/bootstrap/core_service.py:1702-1703`（并 `tests/core/test_derived_gc.py:5-8`）**
C-3 的措辞精确化只落在 `collect_orphans` docstring 一处；`_run_startup_gc` docstring 仍写 "Orphan files (no catalog row) and dead rows (missing file) are **behaviour-equivalent to absent already**"，测试模块 docstring 也仍写 "already unresolvable"。与 PR-01 被点名的同类字面表述残留 ⇒ 建议收口时统一（或明确以 `render_preview.py:114-126` 为唯一权威表述）。无功能影响。

**N-02｜P4｜`tests/core/test_derived_gc.py:156,158`**
`import _winapi` 无平台守卫，与仓库既有 Windows-only 惯例不一致（对照 `tests/core/test_transport_credential_assembly.py:33-34` 的 `sys.platform != "win32"` → `pytest.skip(...)`）；非 Windows 上是 error 而非 skip。判定为可移植性 nit：仓库无 CI（无 `.github/workflows`）、产品边界为 Windows，且 focused/full 的 **skipped 计数与基线相同（1 skipped）⇒ 该用例确实被执行且通过，未被 skip**。附带核验：`finally: os.rmdir(str(junction))` **不会误删目标内容**（Windows `RemoveDirectoryW` 对 directory reparse point 只删 junction 本身；目标是 `tmp_path/outside`，且实测无 error），junction 也不会泄漏到 pytest 的 tmp 清理阶段。

**N-03｜P4｜`doc/tasks/M2-DERIVED-GC-1.md:3`（并 `:40`）**
r1 PR-04 指出的"误记 closed"风险仍挂在 Task 标题上（"RC4-12 登记的预览 GC 缺口**最小闭合**"），`:40` 冻结文本亦保留"行为等价"。两处均属 release 冻结文本（Owner 不宜擅改），且 `Handoff:24/17` 已用 PARTIAL mitigation 定性 ⇒ 建议 Codex 收口时在 REBASELINE_PLAN/STATUS 按 PARTIAL mitigation 记录，不要只读标题。

**N-04｜P4｜`doc/handoffs/M2-DERIVED-GC-1-zcode-13964fe2.md:18`**
PR-06 disposition 声称"fail-closed 取舍登记 **docstring**/Handoff"，但 `collect_orphans` docstring 内并无"单点失败中止整刀"的取舍表述（Handoff 侧已记）。属 PR-05 同类的文档精度小偏差。

---

## 三、核对过、未发现问题的关键点

1. **返修范围收敛**：reflog 独立读出 `ea757205 → 4edec70a`（commit: *fix(derived-gc): DSH r1 rework C-1..C-3 (managed-scope pin, junction escape pin, wording precision)*）→ `728d256d`（docs/raw 日志复跑），branch `refs/heads/zcode/derived-gc-1`，与 Handoff:8-9 完全一致；全仓 grep `collect_orphans|_run_startup_gc|derived_gc|CreateJunction` 仅命中实现/测试/文档，Rust/TS/QML 0 命中。
2. **实现"零行为变更"的最强可用证据**：`core_service.py` 三处锚点行号与 r1 报告**完全相同**（`:1024-1033` 自愈分支、`:1699` 函数定义、`:1712` `except Exception`）⇒ 该文件零行变更；`render_preview.py` 的 `def collect_orphans` 仍在 **:106**（函数前内容未变），而 docstring 之后**全部 9 个语句锚点一致 +8**（scope 过滤 :130-131→:138-139、目录级门 :139-141→:147-149、`sorted(iterdir())` :142→:150、`is_file()` :143-144→:151-152、unlink :145-146→:153-154、行级检查 :149-151→:157-159、remove :152-154→:160-162 等）⇒ 唯一变化是 docstring 增长 8 行，函数体逐行未动；`ORIGINAL_REVISION`(:17)、`publish` 门(:45-46)、`publish_original` 门(:84-85) 行号不变可佐证函数外零改动。
3. **r2 raw 日志一致性**：`focused-pytest-1.log:3/21/67`、`full-pytest-1.log:3/399/400`、`cargo-test-1.log:2/79/81`、`vitest-run-1.log:2/22-23/27`、`frontend-build-1.log:2/14` 全部 `HEAD=4edec70a...`；430 passed / 1884+1sk / 55+1ign / 136(12 files) / EXIT=0 与 Handoff:37-39 逐字一致。
4. **+8 等量递增**：基线 `M2-PAGE-NAV-PROJECTION-1/raw/{focused,full}` = 422 / 1876+1sk（HEAD=`00538a14`）⇒ 430=422+8、1884=1876+8；focused 命令与基线逐字相同。`test_derived_gc.py` 实测 8 个 `test_` 函数（6 交付 + 2 返修），与 Handoff:31/37 自述吻合。
5. **C-2 反向推演（删目录级门的确切后果）**：`previews/` 为指向 `outside` 的 junction 时，缺门会 `iterdir()` 遍历 outside → `keep-me.txt`（stem 不在 catalog）被 `unlink`，且 `preview-keep` 行因文件缺失被 `remove` ⇒ 三重断言同时红，用例不是"恒红/恒绿"的伪判别。
6. **C-1 反向推演（删 scope 过滤的确切后果）**：`entries()` 全量返回、`remove()` 无 scope 条件 ⇒ managed 行会以 derived 根拼相对路径 → 文件不存在 → 行被删，`dead_rows_removed` 0→1 且 `lookup` 变 None，双重钉住。
7. **AC2 装配证据仍在**：`cargo-test-1.log:69-72` 4 行 `[core.derived_gc] orphan_files_removed=0 dead_rows_removed=0`，紧跟 `real_*_sidecar` 用例之后（Rust 侧真实 spawn 的生产装配路径），比单测更强；单测侧 `test_startup_gc_is_fail_soft_and_logs_a_summary` 仍以 skipped/统计双形态钉住 `core_service.py:1705-1713`（`except Exception` 未吞 `BaseException`）。
8. **清理与副产物安全**：`os.rmdir` 只删 reparse point、目标是 tmp 内目录；junction 创建不依赖管理员权限（用例注释正确）；用例失败时 `finally` 仍会清理；`test_escaping_catalog_row_fails_closed` 的 sqlite 直插与表结构（`catalog_store.py:35-41` 三列）相容。
9. **无新契约/schema 面**：`remove()`/`entries()` 为既有方法（`catalog_store.py:83-89`、`:109-115`），`remove` 语义与 `tests/m2_resource_channel/test_catalog_authority.py` 基线一致；本 Task 未新增错误码、未 bump `PROTOCOL_MINOR`（r1 :66 已核，本轮实现行号不变式佐证未动）。
10. **未验证项（如实列出）**：当前工作区是否有未提交改动（无法 `git status`，按"未提交内容归原作者所有"处理）；`728d256d` 与 `4edec70a` 之间的确切 diff 清单（仅凭 reflog commit message + 全量 grep + 文件内容判断为 docs/raw 日志）。

---

## 四、推荐下一步

1. **Task**：M2-DERIVED-GC-1 通过 r2（approve；C-1..C-3 全闭，0×P0/P1/P2），进入 Codex 集成 Gate。
2. **Agent**：Integrator = Codex（Owner 侧无需再返修；N-01..N-04 全为 P4 非阻塞 nit，可随 merge 一并处理）。
3. **可转发指令**：「在 worktree `G:/CODEX/New Manga.worktrees/DERIVED-GC-1`（branch `zcode/derived-gc-1`，base `d4cd96a7`，delivery head `4edec70a`，docs head `728d256d`）执行 M2-DERIVED-GC-1 集成收口：DSH r2 结论 **approve**（C-1/C-2/C-3 全部 fixed，0×P0/P1/P2）。①以 `4edec70a` 为集成提交来源做 Codex 集成验证；②收口 REBASELINE_PLAN/STATUS 时按 Handoff:24 记录 RC4-12 为 **PARTIAL mitigation**（orphan/死行子集闭合，**轮换增长路径保持 open**），勿按 `doc/tasks/M2-DERIVED-GC-1.md:3` 标题的『最小闭合』字面记 closed；③可选顺手闭合 r2 的 P4 nit：统一 `core_service.py:1702-1703` 与 `tests/core/test_derived_gc.py:5-8` 的『等价于不存在』措辞、给 `test_directory_level_escape_fails_closed` 补 `sys.platform != "win32"` skip 守卫（可选，当前 Windows 实测已通过）。不引入新功能范围。」

**无需用户决策的阻塞项**；若 Codex 选择把 N-01..N-04 全部登记 deferred，本 r2 结论不变（approve）。
