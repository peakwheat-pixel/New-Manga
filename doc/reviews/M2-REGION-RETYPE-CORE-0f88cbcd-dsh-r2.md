## Verdict
**approved（可集成）**

方法边界（必须先声明）：本 worktree 的命令执行在本会话被沙箱硬拒绝（`pwsh` 立即 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`，后台任务同样失败；`danger-full-access` 升级无审批通道）。因此 `git show 1b765007`、`git diff --name-status`、`git status` 无法独立执行，凡涉及 git 对象的结论均改用**文件内容旁证 + 双向零污染检索**，下文逐条标注。全程只读，未写入任何文件。

## 逐条闭合表

| 条目 | 判定 | 证据（path:line） |
|---|---|---|
| P2-1 AC5 raw 越权覆盖 | **闭合**（git 层为旁证） | `verification/M2-AC5/raw/cleanstart-gate.json:4,72` 现为 `installer 5410e29e…`/`CS-L1 minor:0`；该 sha 被**未被本轮触碰**的伴生文件独立侧证为 M2-AC5 原始产物：`M2-AC5/verification-results.md:30,54,71`、`checkpoint.md:16,20`、`raw/artifact-inventory-final.txt:3`、`raw/ac1-repro-run2-hashes.txt:1`、`raw/README.md:32,47,68`；`r1-library-probe.log:4-6` 实测 minor=0，`cleanstart-probe-stdout.log:7` 时间戳 `0929/111018`。新产物 6 文件在 `verification/M2-REGION-RETYPE-CORE/raw/retype-m2ac5-*`（gate.json minor=3、`r1-library-probe.log:4-6` minor=3、probe-stdout 时间戳 `1004/154015`），命名对齐 `verification/M2-RG1/raw/rg1-m2ac5-*` 先例。双向检索零污染：`M2-AC5/raw` 内无 `1004/1005→` 时间戳、无 `minor=3`、无 `set_region_type/retype/d6003ae7`；新 raw 内无 `0929/`、无 `minor=0`。引用路径已改：`verification.md:76`、handoff `:48`、task `:46`；`handoff:76`「SETTINGS-IPC 时代 minor=2」已按实测改写 |
| P2-2 DB_FAILED 码位 | **闭合** | `service.py:361-377` 显式分支：`INPUT_REVISION_CHANGED`→typed 冲突返回（经 `_guard_status_of`），`DB_FAILED/LOCK_CHANGED`→`RuntimeError`；全局 `_guard_status_of`（`service.py:78-81`）仅 `LOCK_CHANGED` 映射、形态与 r1 基线一致（未改，git 无法证）；单测走 ports 真实 `RegionCommitResult`（`tests/editing/test_region_retype.py:553-623`），红态 `raw/retype-r1-red-state.log:3-13` 实测两条 `DID NOT RAISE`，绿态含于 `raw/retype-r1-pytest-editing-pipeline.log:3`（143 passed） |
| P3-1 docstring minor/家族名 | **闭合** | `core_service.py:10,13,18` 三处 `minor: 3+`；`:16-17` Allowed production commands 补 `M2-REGION-RETYPE-CORE`；`:62` 新增家族段 |
| P3-2 ACL 循环+负例 | **闭合** | `main.rs:794-798` 三面并集循环（9+4+3=16，与 `:789-793` 注释算式一致）；`:897-918` `production_only_commands_stay_off_both_frozen_test_surfaces`（三家族统一负例 + probe/ac1 pin 7/6）；`raw/retype-r1-cargo-test.log:39,47` 两测试 ok |
| P3-3 补跑回归+日志入库 | **闭合** | `raw/retype-r1-pytest-editing-pipeline.log`（143 passed）、`retype-r1-pytest-tri-suite.log:11`（650 passed, 1 skipped）、`retype-r1-pytest-full.log:379-393`（1 failed/1780 passed/1 skipped，失败=`tests/m2_test_assets/test_catalog.py:33 assert 100 == 97`）、`retype-r1-cargo-test.log:72`（49+1ig）。附注：pre-existing 归因缺日志（见新发现 P4-1） |
| P3-4 真实 sidecar 测试 | **闭合** | `main.rs:1487-1522`（`list_regions("no-such-page")`→`{"regions":[]}`；`set_region_type("no-such-region")`→`TARGET_NOT_FOUND`/`not_found`）；`retype-r1-cargo-test.log:68` ok |
| P3-5 前端 pin 顺延 | **闭合（登记）** | `verification.md:109`、`handoff:91` 登记归 Workbench UI Task，本 Task 前端零改动 |
| P4-1 effective_sfx_policy | **闭合** | `service.py:84-93` 模块级 helper；`core_assembly.py:39` 导入、`:1042` 调用（创建与改标两写路径共用同一布尔规则） |
| P4-2 命名决策登记 | **闭合（登记）** | `verification.md:111`、`handoff:93`（stdio snake_case vs 契约逻辑名 vs Tauri 命名风格归 UI Task） |
| P4-3 seam 复检失败分支单测 | **闭合** | `tests/editing/test_region_retype.py:626-643`（fake committer 返回 `INPUT_REVISION_CHANGED`→typed 冲突+零写入） |
| P4-4 测试卫生三处 | **闭合** | ①`tests/core/test_core_service_retype.py:170,177` `len(revisions)==revisions_before+1`；②`test_region_retype.py:348-357` 恒真 `or` 子句拆为 region_type 必变/`sfx_policy` 免断言两分支；③同文件 `:385-404` 改 `origin=RegionOrigin.MACHINE` 并断言 `"machine"` |
| Q1-附条件 b（Task:39） | **闭合** | `doc/tasks/M2-REGION-RETYPE-CORE.md:39` 已写明「`packaging/**` 除**经追认的** CS-L1 协议字面量与 RC2 EXPECTED 计数同步外不改；spec 冻结（Q1 附条件 b，DSH r1 返修措辞修订 2026-10-04）」；旁路对象实测在位（`packaging/m2ac5/run_clean_start_e2e.py:445,497` minor=3；`verification/M2-RC2/run_e2e.py:302-311` 含两命令）。微瑕：RC2 runner 实际在 `verification/**` 而非 `packaging/**`，该句把两对象并入同一修饰语，语义略含糊（不构成未闭合） |

## 新发现

- **P3-1 Task frontmatter 与正文/r2 声称冲突**：`doc/tasks/M2-REGION-RETYPE-CORE.md:5` `status: ready`，而同一文件 `:57` 称「status 保持 in_progress 待 r2 复核与 Codex 集成」；`:12` `base_commit: 69321db7` 与 `handoff:5`、`verification.md:4` 的 `base=1b765007` 冲突。影响集成状态机与基线追溯，建议集成时一并回填（若属 r1 P4-5/6/7 已裁定「登记不修」项，请归并去重）。
- **P3-2 返修链顶未登记**：`handoff:6` 仍 `delivery_head: cfbf3859`（而 `handoff:79` 称链顶已更新为返修 commit），`verification.md:4` 链条顶端亦仍为 `cfbf3859`，`task:55` 同；`verification.md:97` 出现孤立 hash `eaed7858` 却未在任何交付链/frontmatter 中定义。集成者无法从文档确定 r2 交付 commit，建议补一行「r1 返修 commit=<hash>（链顶）」。
- **P4-1 P3-3 pre-existing 归因缺独立日志**：`verification.md:107`/`handoff:89` 的「stash 全部改动后于 HEAD 干净态同败」在 `raw/` 无对应日志（raw 仅 red-state/editing-pipeline/full/tri-suite/cargo 五份）。失败点（`tests/m2_test_assets` 资产计数）与本 Task 改动路径无交集，归因可信，但建议补一条复现日志或由 Integrator 一条命令代验。
- **P4-2 命名先例文件数不完全对应**：RG1 先例为 7 文件（含 `rg1-m2ac5-cleanstart-runner.log`），本轮搬运 6 文件（无 runner 汇总日志）。`verification.md:76` 仅引用 gate JSON，无缺证影响，仅提示「沿 RG1 命名先例」在集合上略有出入。

**推荐下一步**：由 Codex（集成者）执行 M2-REGION-RETYPE-CORE 集成，并在同一提交回填 Task frontmatter（`status`、`base_commit`）与返修链顶 hash；P4-1 可在集成验证时以一条 stash 复跑日志顺手闭合。无需再次返修本 Task 的实现内容。
