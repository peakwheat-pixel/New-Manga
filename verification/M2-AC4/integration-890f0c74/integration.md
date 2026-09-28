# M2-AC4 集成记录（integration record）

- **Integrator**：Codex（代行，ZCode 子 agent 会话，用户授权 2026-09-28）；Owner=ZCode（另一子 agent），Owner≠Integrator。
- **本记录与相关裁决**：Lead（代行 Codex 主会话）已裁决六项（见 §4），集成方落字；均标注「代理裁决，用户可撤销」。
- **Merge**：`fc99182147bccc89d9bd9124dd17d15b1d428e21`（`git merge --no-ff agent/zcode/M2-AC4-reader-lineage-library-pagecount`，父 `252705bf` + `890f0c74`，无冲突，'ort' 策略）。
- **Owner tip / ledger**：`890f0c74`；claim `5f9f54ab` → 实现 `130dd7db` → evidence/handoff `890f0c74`；base=`a5529181`。
- **集成修正 commit**：见 §7（merge 之上单 commit，message 前缀 `integration(M2-AC4):`）。
- **环境**：`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / pytest 9.1.1）；shell Git Bash（win32）。

## 1. DSH r1 Review 结论

- 报告：`doc/reviews/M2-AC4-890f0c74-dsh-r1.md`（原字节拷贝自 `/tmp/m2ac4-review/dsh-r1-result.md`）。
- **SHA256**：`48b34dbb75cfc5a15085f11688644668d6b8e914d6a6b3bda2b782703471e6fa`（拷贝前后一致，已双向核对）。
- **结论：approved_with_conditions，0×P0**。P1×3（集成前必须关闭，本次全部关闭，见 §4）；P2×5（集成方裁决，处置见 §4/§5/§6）；P3×7（观察/deferred，处置见 §6）。

## 2. 集成方代跑证据（Owner worktree tip=890f0c74，主 repo merge 后再验）

DSH r1 §2 not_verified 8 项中需代跑者，全部代跑完毕；日志带头（shell / python 版本 / `git rev-parse HEAD` / ISO 时间戳），尾记 EXIT 码，存 `verification/M2-AC4/integration-890f0c74/raw/`。

| # | 命令（worktree `G:/CODEX/New Manga.worktrees/M2-AC4-zcode`） | 期望 | 实测 | EXIT | 日志 |
|---|---|---|---|---|---|
| 1 | `git diff --name-status a5529181..890f0c74` | 恰 4 类允许路径（doc/STATUS.md、release-a5529181.md 属 release commit 252705bf） | 16 项：净变更（`252705bf..890f0c74`）恰为 tests/m2_acceptance 新套件 + verification/M2-AC4/** + doc/tasks/M2-AC4.md + doc/handoffs/M2-AC4-owner-delivery.md | 0 | — |
| 2 | `git status --porcelain src/ apps/ doc/contracts/` | 空 | 空 | 0 | — |
| 3 | `git diff --stat a5529181..890f0c74 -- tests/m2_acceptance/test_acceptance_loop.py test_data_integrity.py test_provider_fail_closed.py` | 空 | 空 | 0 | — |
| 4 | `git diff --check a5529181..890f0c74` | EXIT=0 | 无输出 | 0 | — |
| 5 | `git log --oneline a5529181..HEAD` + `git merge-base --is-ancestor 5f9f54ab HEAD` | 恰 3 commit / EXIT=0 | 5f9f54ab→130dd7db→890f0c74 / EXIT=0 | 0 | — |
| 6 | `git ls-files tests/m2_acceptance/__pycache__` | 空 | 空 | 0 | — |
| 7 | `$py -m pytest tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py -v` | 9 passed, 2 xfailed | **9 passed, 2 xfailed** (0.94s) | 0 | `raw/integration-pytest-new-suite.log` |
| 8 | `$py -m pytest … -v --runxfail` | 恰 2 红，EXIT=1 | **恰 2 failed, 9 passed**：失败点 `test_reader_export_lineage_library_pagecount.py:584`（F-1）与 `:782`（F-2），见 §3 | 1 | `raw/integration-pytest-new-suite-runxfail.log` |
| 9 | `$py -m pytest tests/m2_acceptance -q` | 32 passed, 2 xfailed | **32 passed, 2 xfailed** (9.10s) | 0 | `raw/integration-pytest-regression.log` |
| 10 | MU1 变异（`service.py:219` ABORT 条件 → 恒 False；`grep -c` 唯一性=1 守卫） | 主判别红 | **3 failed, 6 passed, 2 xfailed**（红点同 Owner 记录）；已 `git checkout --` 还原，`git status --porcelain src/` 空 | 1 | `raw/integration-mutation-MU1-run.log` |
| 11 | MU2 变异（`core_service.py:160` → `page_count=999`；`grep -c` 唯一性=1 守卫） | 主判别红 | **2 failed, 7 passed, 2 xfailed**（`test_ac4_books_without_pages…` 保持 xfail，符合预期）；已还原，src/ 空 | 1 | `raw/integration-mutation-MU2-run.log` |
| 12 | `git rev-parse 252705bf^`（P3-1 对齐） | =a5529181 | `a55291819bf9f98b36919a509ee7b00b440beb5d`；`252705bf` 仅改 `doc/STATUS.md`、新增 `doc/tasks/M2-AC4.md`、`verification/M2-AC4/release-a5529181.md` | 0 | — |

MU 复核（步骤 10/11）为可选项，已执行且结果与 Owner `discrimination-mutations.md` 逐项一致——MU 红不再仅依赖 Owner raw 日志+DSH 静态核对，集成方已独立复现。

## 3. F-1/F-2 的 runxfail 失败点与缺陷对齐（「失败原因即缺陷本身」证明）

- **F-1**：`test_ac2_history_records_which_stale_pages_were_included` 失败于 `test_reader_export_lineage_library_pagecount.py:584`——`assert persisted_stale == {stale_page_id}`（`:582-583` 从持久行 `scope_snapshot_json` 取 `included_stale_page_ids` 得空集）。**与 F-1 定义（export history 持久层无 included_stale/missing_page_ids）精确对齐**，非环境性失败（同 run 中其余 9 场景含 SQLite/文件系统密集场景全 PASS）。
- **F-2**：`test_ac4_books_without_pages_are_not_presented_as_zero` 失败于 `:782`——`assert presented_unknown`（`:776-781` 检查 `page_count is None`/负数/`page_count_known is False` 三通道均不存在）。**与 F-2 收窄后定义（unknown/已知度通道缺失）精确对齐**。
- 结论：`--runxfail` 真实 traceback 已落盘（DSH r1 §5 条件 3 / P3-3 的补强证据），两条红均为缺陷断言本身，无环境噪声。

## 4. Lead 六项裁决落字（代理裁决，用户可撤销）

1. **P1-1（AC5 证据纪律）**：采 DSH 关闭方式①——以集成方 tip 复跑生成的带头带 EXIT 日志为准（§2 #7-#9）。`verification-results.md:20`「每个日志文件带头」改为「final-\* 与 git-diff-check 等集成复跑日志带头；Owner 交付的 probe/run1/run2/MU1/MU2 五日志无头无 EXIT，如实保留」。`doc/tasks/M2-AC4.md:53/:85` 与 `doc/handoffs/M2-AC4-owner-delivery.md:31` 的 AC5 证据纪律判定改为「**部分满足（交付日志），集成复跑补足**」。HEAD 指向澄清：Owner `final-*.log` 的 HEAD=claim commit `5f9f54ab`，与其声称的执行状态不符，本记录以集成复跑日志（HEAD=`890f0c74`）为最终证据。
2. **P1-2（AC2 判定拆分）**：AC2 判定改为「**PASS(a、c) / 部分不满足(b 持久留痕，同一 F-1)**」，同步 `Task:50/:85`、`Handoff:28`、`verification-results.md:45`。
3. **P1-3（F-2 定性收窄）**：F-2 定性改为「**unknown/已知度通道缺失：0 与真实计数一致（非数值造假），但无法区分『确认 0 页』与『数据不可用/未统计/导入未完成』**」；**AC4(b) 判 FAIL 保留**——AC4(b) 原文要求如实反映未知/缺失，0 无未知通道即不可区分（需求解释裁定）。同步 `Task:52`、`Handoff:52`、`verification-results.md:53`。
4. **P2-1（AC5 vacuous 子断言）**：AC5 措辞区分「**Core 层可达面（Managed Copy / artifact revision 指纹）承重**」与「**用户源文件在 Core 侧结构性不可达（`data_provider` 返回常量 payload，导入后不存在用户源路径；非 PASS 证据）**」。不改测试（DSH 确认结构性、先例同构）。
5. **P2-2（xfail 跨 Task 耦合）**：接受 xfail 留在默认套件；四条承接见 §5。
6. **F-1/F-2 修复候选**：按 DSH §3/§4 登记两个 **proposed / NOT_RELEASED** Task：`doc/tasks/M2-FIX-EXPORT-LINEAGE.md`（F-1；schema/契约：`scope_snapshot_json` 加键方案 A vs 独立列 migration 方案 B 的取舍留给释放时冻结；含 per-page revision 范围裁定 = P2-3）、`doc/tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md`（F-2；IPC 契约：DTO/Rust Option/TS 类型；**不得把真实 0 改 null，必须保留「已知为 0」表达能力**）。两 Task 验收标准均含「移除对应 xfail 标记转 PASS，XPASS 出现即处理」。

## 5. xfail 四条承接（DSH r1 §5，集成记录义务）

1. **登记**：默认 `tests/m2_acceptance` 从此为 **32 passed + 2 xfailed，非全绿是已知受控状态**（2 xfail = F-1/F-2 的可复跑验收证据，`strict=True`）；**不得据此把新增 xfail 正常化**——后续 Task 仍以「无新增 skip/xfail」为默认纪律。
2. **修复 Task 范围**：F-1/F-2 修复 Task（§4 裁决 6）允许范围已显式包含对应 `@pytest.mark.xfail` 的移除与断言转 PASS，「XPASS 出现即处理」写入其验收标准。
3. **runxfail 补证**：`--runxfail` 真实 traceback 已由集成方代跑落盘（§3），证明失败原因即 F-1/F-2 而非环境（P3-3 关闭）；xfail `reason` 字段内补写预期失败点属测试文件改动，留给修复 Task 随 xfail 移除一并处理。
4. **不移出默认套件**：维持 DSH §5 裁定——移出将使证据脱离 CI 执行，防腐能力下降；固定 2 xfailed 优于显式常态红。

## 6. P3 处置表（DSH r1 §1 P3 逐条）

| 项 | 处置 | 去向 |
|---|---|---|
| P3-1 release hash 对齐（`release-a5529181.md` 以 a5529181 为 base vs Task/Handoff release=252705bf） | **已关闭**：集成方实测 `252705bf^ = a5529181`，release commit 是代码 base `a5529181` 之上的唯一文档 commit（仅动 STATUS/Task 骨架/release 说明）。两者关系为「base vs release 文档 commit」，无矛盾 | §2 #12 |
| P3-2 `verification-results.md:18` 第 5 行「待交付 commit 后执行」+ EXIT=0 易误读 | **已关闭**：集成方已在交付 tip 代跑 `git diff --check a5529181..890f0c74` EXIT=0（§2 #4），C 步文档修正时同步该行措辞与实测 | §2 #4 + C 修正 |
| P3-3 xfail reason 未写预期失败点 + 缺 runxfail traceback | **runxfail 部分已关闭**（§3 集成代跑落盘）；reason 字段补写归修复 Task（随 xfail 移除一并处理） | §5 条 3 |
| P3-4 NOT_RUN 与「不在承诺内」混列 | 观察：PDF/CBZ/single_image 实为「不在 AC1 承诺内」而非未运行；不改 Owner 交付文件，本记录登记即视为披露 | 本行 |
| P3-5 Handoff 无 YAML frontmatter | 观察：模板偏差属实；Handoff 内容完整（task/owner/delivery_head 信息在正文），不回溯补写 | 本行 |
| P3-6 `_PRODUCTION_COUNT_SQL` 手抄副本漂移风险 | **登记**：写入 M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN「同步义务」——修复动 `core_service.py` 谓词时必须同步测试副本 | FIX Task F-2 |
| P3-7 `reading_export.py:176-240` 并发 read-modify-write + DELETE NOT IN 互删风险 | **登记**：写入 M2-FIX-EXPORT-LINEAGE AC5（F-1 修复触碰同一函数，释放时一并评估同期修复或独立缺陷登记） | FIX Task F-1 |

P2 剩余三项处置：
- **P2-3（per-page revision 范围）**：已裁定落入 M2-FIX-EXPORT-LINEAGE——释放时必须显式裁定「页版本」是否含 per-page revision/内容指纹，不得默认只补 included ids（代理裁决，用户可撤销）。
- **P2-4（production 装配 `ReaderPage.translated_stale` 恒 False）**：属实（`core_assembly.py:356-357` 同 revision 赋值）；不削弱本 Task 导出侧 stale 判定验收（`ExportService._stale_scope` 为 production 逻辑，MU1 已证判别力）。**登记为观察项**：Reader 侧 stale 提示生产不可达属产品需求缺口，是否立 Task 留后续 planning 裁定，本集成不擅自扩 Task 树。
- **P2-5（默认套件长期非全绿门禁口径）**：本记录 §5 条 1 即为门禁口径披露；CI 门禁规则如需显式配置（如 `--xfail-strict` 已默认、允许 2 xfailed），留 Codex 主会话在门禁定义处固化。

## 7. 缺陷登记与修复候选

| 缺陷 | 定性（收窄后） | 证据指针 | 修复候选 |
|---|---|---|---|
| **F-1** | export history 持久层无 `included_stale_page_ids`/`included_missing_page_ids`；CONTINUE 放行的 stale 页持久不可追溯（内存 `ExportResult` 正确） | `raw/probe-output.log`（`history row keys`/`scope_snapshot keys` 无字段）；xfail 场景 `test_ac2_history_records_which_stale_pages_were_included`（断言 `:583-586`）；DSH r1 §3 逐行链条（`_record`/`_scope_snapshot`/`ExportRecord`/schema 13 列/SQLite 存取层全链无落点） | `doc/tasks/M2-FIX-EXPORT-LINEAGE.md`（proposed / NOT_RELEASED） |
| **F-2** | unknown/已知度通道缺失：0 与真实计数一致（非数值造假），但无法区分「确认 0 页」与「数据不可用/未统计/导入未完成」；AC4(b) FAIL 保留 | `raw/probe-output.log`（`Probe Empty Book page_count: 0`）；xfail 场景 `test_ac4_books_without_pages_are_not_presented_as_zero`（断言 `:776-786`）；DSH r1 §4 逐行链条（DTO `int` → Rust `u32` → TS `number` 全链无 unknown 表达位） | `doc/tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md`（proposed / NOT_RELEASED） |

两候选 Task 均未冻结 base/branch/worktree，禁止任何会话未经 Rebaseline Plan 释放流程实施。

## 8. 判别力边界披露

- **AC2(a)「零任何记录」语义**：实测「零 completed 记录」实为零*任何*记录——`StaleExportError` 在 `_record` 之前抛出，被拒导出连 failed 记录都不留。本套件将该行为断言为承诺语义；若产品定义认为被拒导出也应留痕，属 D03 §31 语义澄清（accepted-but-unspecified），超出 M2-AC4，未做语义扩张。
- **AC5 vacuous 子断言**：「用户源文件零风险」在 Core 层结构性不可达（导入后 Core 只持有调用方字节，`data_provider` 常量，无用户源路径）；承重的是 Managed Copy 与译文 revision 指纹。裁决 4 已在 Task/Handoff 措辞中区分，虚假承重部分不再作为 PASS 证据引用。
- **xfail 掩盖效应**：strict xfail 不区分失败原因，修复后若因环境原因失败仍显示 xfailed；本记录 §3 的 runxfail traceback 为当前基线补足了「失败原因即缺陷」证明，后续由修复 Task 的 XPASS 纪律接管。

## 9. 范围与集成卫生

- Merge 引入内容 = Owner tip 净变更（§2 #1），无第三方内容混入；`src/**`、`apps/**`、`doc/contracts/**` 在 Owner 分支零命中。
- 主 repo 上不属于本 Task 的未提交改动（`apps/desktop/frontend/package*.json`、`src-tauri/**`、`permissions/**`、`verification/M2-RC2/raw/**` 等）**未被 add/checkout/覆盖**，保持原状归原作者。
- 集成修正 commit 仅含：本记录 + raw 日志 + DSH 报告拷贝 + 两个 FIX Task 登记 + `doc/tasks/M2-AC4.md`、`doc/handoffs/M2-AC4-owner-delivery.md`、`verification/M2-AC4/verification-results.md`、`doc/REBASELINE_PLAN.md` 的裁决落字修正 + 集成 head 复跑日志。
- 未 push、未动 Owner 分支、未删任何分支。
