---
task_id: GIT-CLEAN-PUBLICATION-1
reviewer: DeepSeek Harness
author: Codex
base_commit: 349e61faff5f93067af5d4ce2d9e394e0d665b8c
reviewed_head: e34a90d001cce1fa966aec7d2b032bb5ad1cf148
decision: blocked
---

# Review：GIT-CLEAN-PUBLICATION-1

2026-10-24 / DeepSeek Harness（独立 Reviewer，非作者）。本 Review 只对上述 `reviewed_head` 有效。`base_commit` 是源仓基线；`reviewed_head` 属于独立 artifact 仓库的 root commit，两者不在同一对象库，不能按 base..head 增量理解，也不能直接合并到 `main`。

## 范围与依据

- 需求/AC：`doc/tasks/GIT-CLEAN-PUBLICATION-1.md` 的 AC1–AC5、允许/禁止范围与四项版本细化（r1→r4）；交付说明 `verification/GIT-CLEAN-PUBLICATION-1/RESULT.md`、`HANDOFF.md`、`checkpoint.md`；当前指针 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（GIT-CLEAN-PUBLICATION-1 `in_review`，无其他 READY 节点）。
- 审查对象（固定）：
  - 源仓 `G:/CODEX/New Manga`，branch `main`，HEAD = `349e61faff5f93067af5d4ce2d9e394e0d665b8c`；
  - 候选 `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/source-export-r4`，branch `codex/clean-source-snapshot`，root commit `e34a90d001cce1fa966aec7d2b032bb5ad1cf148`，tree `5c42f485455dcf93c8b0551c7012456b165d046f`；
  - 冻结证据 `.../GIT-CLEAN-PUBLICATION-1/review-package/` 与仓内 `verification/GIT-CLEAN-PUBLICATION-1/`；早期候选 `source-export`、`-r2`、`-r3` 仅作树等价比对。
- 未覆盖：安装包/签名、真实模型、真实 GUI 交互、完整产品审计（Task 明确 NOT_RUN）；Legacy PySide6/QML 行为（仅保留参考，不诊断/运行）；源仓其他未提交内容与远端状态。
- 只读约束：本 Review 未修改候选、生产代码、素材、registry、历史/refs、未提交内容或远端；唯一写入为本文件。Core 3 项未重跑（已达同条件 2 次上限），Rust 并行未重跑；未修改系统 Python ACL。
- 视角状态：Architecture `executed`、Verification `executed`；Standards / Spec 未单独执行（`doc/templates/REVIEW.md` 2026-09-18 已取消双轴强制）。为降低遗漏，证据收集派出 3 名只读子核查（Git 隔离 / 来源清单 / 测试证据），其命令与原始输出已汇入本文件并经 Reviewer 交叉复核；判定与批准结论由 Reviewer 独立作出。

## Architecture

**结论：作为“可检查的本地源码快照”，候选在架构边界、来源可追溯与材料隔离三方面成立；但不得据此宣称产品发布、安装包或并发安全。**

1. **导出是固定源 commit 的忠实子集。** 724 个源文件逐项绑定 `source_commit/source_blob/source_sha256/候选 sha256`：722 项与源 blob 逐字节相同，2 项为已记录的字面量变换；6 个生成夹具可由未改动的 generator（`experiments/TASK-016/generate_samples.py`，sha256 `40cf72af…`）独立重建，重跑 `rc=0` 且 6/6 与候选逐字节相同。733 tracked = 724 源文件 + 6 生成夹具 + 3 个授权新增文件（`README.md`、`.gitignore`、`SOURCE_MANIFEST.json`），无未授权额外文件。
2. **分层、契约与依赖未被改动。** 导出仅含 `src/`、`tests/`、`apps/desktop/frontend/`、`apps/desktop/src-tauri/`、`packaging/m2ac5/`、`tools/smoke/` 与白名单根文件；`requirements*.txt`、`pytest.ini`、`package-lock.json`、`Cargo.lock`、`tauri.conf.json` 均为源原样（manifest `transform=null`）。未修改共享接口、Schema、锁文件或生产实现；React/WebView 经 Tauri IPC 访问 Python Core 的既有边界不因快照而变化。
3. **历史与远端隔离成立。** 候选 `.git` 无 `alternates`/`http-alternates`、无 pack、无 replace/grafts/shallow；866 个 loose 对象全部 reachable（730 blob + 135 tree + 1 commit，无 unreachable/dangling）；仅 1 个无父 root commit、1 个 loose ref（`packed-refs` 不存在）、无 remote。源仓全部 4131 个 commit 对象在候选对象库 present=0；源 HEAD/main 未变、index 为空、6 个 P04 日志与任务前 pin 字节级一致。候选与源仓无共享对象库，不是 linked worktree。
4. **私有材料与安全边界。** 169 行 disposition 定义 338 个禁止对象（169 JPEG + 169 压缩外层 blob）；候选对象库 absent=338 / present=0。内容级复核 730 个 blob：payload sha256 匹配 0、JPEG 魔数 0、base64 JPEG 0。导出内无 jpg/jpeg/zip/db/模型/日志；无 symlink/子模块/LFS；二进制恰 6 项（`icon.ico` + 5 个合成 PNG），`icon.ico` 来源 `991097d770435377d68615ad0fd12503e16bb842` 在源仓可查、为 32×32 DIB 非私有素材；P04/P22 sidecar 仅 stdlib、纯测试用途；6 条凭据规则命中均裁定 `TEST_PLACEHOLDER` 并记录值 sha256。
5. **Legacy 保留符合边界。** `src/ui` 的 QML/PySide6 代码按 Task 白名单保留为参考，不运行、不诊断，与 AD-001/STATUS 一致；源文本中的历史 doc/verification 引用不被冒充为快照内证据。
6. **架构层面的限制。** 候选工作树不是纯净目录：ignored 的 `node_modules`（84 MB）、`dist`（462 KB）与 Rust 测试运行时生成的 `verification/P04/diagnostic_p22_692_1792842383784.jsonl` 存在。以 Git 对象/分支交付不受影响；以目录复制或压缩包交付会携带依赖、构建产物与本地环境路径（R-007）。

## Verification

| AC / 检查 | 实际结果 | 判定 |
|---|---|---|
| AC1 文件来源 | 724/724 来源可解、blob/sha256 一致；6/6 生成物可复现；733 = 724+6+3；transform 恰 2 处（`packaging/m2ac5/README.md`、`tests/core/test_core_detect.py` 各 1 行 `49745`→`USER`），733 文件内 `49745` 残留 0；白名单独立重建应选 724、排除 12,916，与 `selection.json` 行级一致 | **MET（可确认）** |
| AC2 禁止材料 | 338/338 禁止对象在候选对象库 missing；169/169 embedded 为 JPEG 魔数且 sha256=payload_sha256；169 个外层为 zlib 流；无 tracked 图片/模型/数据库/日志 | **MET（可确认）** |
| AC3 独立历史与原仓保护 | 单 root、无 parent、无 remote、1 ref、fsck 0、工作树 clean；源 main/index 不变；6 个 P04 日志与 `push-worktree-ownership.json` pin 6/6 一致 | **MET（可确认）** |
| AC4-a 前端 | r3 实测 `Test Files 45 passed (45)` / `Tests 435 passed (435)`；r3/r4 的 `apps/desktop/frontend` tree 同为 `662ad099f9a71f0040ca375ecb637c7839e25e3d`（131 项逐条相同）；r4 `npm ci --offline` 与 `npm run build` 均 exit 0 | **PASS** |
| AC4-b Rust | r4 串行 `running 154 tests` → `153 passed; 0 failed; 1 ignored; 12 filtered out`（1 ignored=`perf_chunk_request_digest_cost`；12 filtered=`packaged_sidecar_tests::`），exit 0；env 与 argv 记录一致。**但 r4 从未以默认并发运行**：r2 并行 `150 passed; 3 failed`（ac1 registry panic@9278、ac4 registry panic@9162、same_channel 缺 P04 fixture），并行日志含 50 条 `UNREAPED_WORKER_REGISTRY at capacity (32)`；r2 串行 `152/1 failed`、r3 串行 `152/1 failed`（208.71s，缺 P22 时回退 P04 挂起，`stopped-test-fixture-r3.json` 记录只终止 Task 自有子进程）；仅 r4 串行单次通过 | **BLOCKED** |
| AC4-c Core | r2 `3 failed, 771 passed`；首轮 `core-tests-isolated-deps.log` 同结果 → 同条件 2 次，符合上限。失败为同一参数化测试 3 组（`tests/core/test_p16_reader_export.py:762×2、:780`）；无 skip/xfail。静态定位为 AppContainer 沙箱 `_grant`→`icacls` 无法为 `C:\Python314\python.exe` 授 ACL→`PLUGIN_HOOK_UNAVAILABLE`→before_export hook 跳过→format options 未应用 / `hook_invoked=0`。运行期硬证据：r2 basetemp 三个 `test_export_hook_effective_opt*/data/library.db` 的 `plugin_events` 各含 `{"code":"PLUGIN_HOOK_UNAVAILABLE","detail":"cannot grant sandbox access to python.exe"}`（opt2 另有 after_export）。该证据未进冻结包，且 `_grant` 丢弃 icacls 错误码，“环境能力不足”是高置信静态推断而非证据事实 | **BLOCKED** |
| AC4-d packaged / 安装包 / 模型 / GUI | 12 项 `packaged_sidecar_tests` 被过滤；安装包、真实模型、真实 GUI、完整产品审计均未运行 | **NOT_RUN** |
| AC5 交付/交接/冻结证据 | 固定 SHA、Handoff、冻结证据已形成；独立 Review 由本文件完成（非虚构批准）。但整体 Task 仍受 AC4 阻断，不能置 done | **PARTIAL** |
| 治理检查 | 独立运行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GIT-CLEAN-PUBLICATION-1.md` → `Governance check: PASS (4 warnings)`、exit 0，与冻结 `governance-check.json` 一致；STATUS/REBASELINE_PLAN/TASK_LEDGER 指针一致 | **PASS（带告警）** |

**证据纪律核查**：19 个 `.log` 均无 EXIT/shell/venv 头（exit 只存于 checks JSON）；冻结 `review-package` 缺被引用的 `checks-r3.json`、`npm-ci-r4.log`、`frontend-build-r4.log`、`core-tests-isolated-deps.log`；`checks-r4.json` 的 rust 条目缺 `filtered_tests_reason`；`evidence_dir` 有 8 个未登记过程文件（governance 自报）。核心数字本身与日志逐项吻合，未发现虚报、skip 掩盖或把 filtered/ignored 当 PASS。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | P1 | `verification/GIT-CLEAN-PUBLICATION-1/rust-tests-r2.log`、`rust-tests-r2-serial.log`、`rust-tests-r3-serial.log`；候选 `apps/desktop/src-tauri/src/library_bridge.rs:1606-1608,9162,9278` | 并发隔离风险未裁决：r2 并行 3 失败（含 2 个 `UNREAPED_WORKER_REGISTRY` 断言与 50 条 capacity(32) 告警），r2/r3 串行也各 1 failed，仅 r4 串行单次通过。串行通过只能证明单线程路径，不能排除产品并发缺陷；AC4 不能宣称并发安全，亦不能作为 push/release 依据 | `rust-tests-r2.log` 尾部 `150 passed; 3 failed`；`rust-tests-r2-serial.log`、`rust-tests-r3-serial.log` 尾部 `152 passed; 1 failed`；`rust-tests-r4-serial.log` 尾部 `153 passed; 0 failed; 1 ignored; 12 filtered out`；checks-r2/r2-serial/r3/r4 的 exit 分别为 101/101/101/0 | 另释诊断 Task：复跑默认并发并静态分析 `static Mutex<Vec<UnreapedWorker>>` 的测试间共享污染与 capacity=32 语义；结论出来前保留 AC4 BLOCKED | open |
| R-002 | P1 | `verification/GIT-CLEAN-PUBLICATION-1/RESULT.md:23`、`validation.json:59`；`core-tests-r2.log` | Core 3 项失败的归因没有进入冻结证据：19 个日志中 `PLUGIN_HOOK_UNAVAILABLE`/`cannot grant sandbox access` 0 命中，仅 RESULT/validation 散文声称；原始记录只存在于 pytest basetemp 的 SQLite 中（临时/可清理产物），且 `_grant` 未保留 icacls 错误码。冻结包内无法自证“环境能力边界而非产品缺陷” | 三个 `pytest-temp-r2-869998…/test_export_hook_effective_opt*/data/library.db` 的 `plugin_events` 均含同一 `plugin_error before_export`；`verification/P04/…` 无对应 audit 文件 | 把 plugin_events 摘要与 pytest basetemp 路径/provenance 登记为 SOURCE_PIN（如 V1 零重跑方案），或冻结该 DB 快照；在 `_grant` 保留 returncode/stderr 后再下结论 | open |
| R-003 | P2 | `review-package/selection.json` | 338 禁止对象的 id 列表不在冻结包内：`selection.json` 仅有 `base/selected/excluded/findings/blockers/icon_provenance`，`validation/snapshot` 只断言数量；真实来源是源仓 untracked `audit/V1-FULL-AUDIT/evidence/push-material-disposition.json`，仅凭 review-package 无法复算 338 | `Select-String selection.json 'outer_object'` 0 命中；disposition `objects[169]` 的 `outer_object`+`embedded_git_object` 去重后 338 | 把 disposition 的 (outer_object, embedded_git_object, payload_sha256) 摘要纳入 review-package 或 Task 证据表 | open |
| R-004 | P2 | `review-package/checks-r4.json`、`checks-r3.json`、`npm-ci-r4.log`、`frontend-build-r4.log`、`core-tests-isolated-deps.log` | 冻结包不完整：`checks-r4.json` 引用的 4 个文件不在 review-package；前端唯一机器 exit 记录 `checks-r3.json` 未冻结；`checks-r4.json` 缺 `filtered_tests_reason`。独立复核依赖仓内目录而非冻结包 | `review-package` 仅 11 个文件；`checks-r4.json` 的 `log` 路径指向 `verification/…/npm-ci-r4.log` 等 | 补齐冻结副本或在 Task 证据表追加 SOURCE_PIN；校验脚本应拒绝引用缺失的 log | open |
| R-005 | P2 | `verification/GIT-CLEAN-PUBLICATION-1/*.log`（19 个） | 证据纪律缺口：全部日志无 EXIT 与 shell/venv 头，exit code 仅存于 checks JSON；模板 Q-009 要求日志带 EXIT/shell 头且逐次入库 | `Get-ChildItem *.log | Select-String '^EXIT|Exit code|^exit='` 命中 0 | 运行器统一追加头（argv、cwd、env 白名单、EXIT）并逐次入库 | open |
| R-006 | P2 | `RESULT.md:24`、`checkpoint.md:11`、`snapshot.json:11` | 边界披露不完整：只写“r4 串行通过 / 串行通过不裁决并行隔离”，未显式列出 r2、r3 两次串行也各 1 failed；`snapshot.json` 的 `RUST_SERIAL_PASS` 与 `FRONTEND_PASS_RUST_SERIAL_PASS_CORE_3_FAILURES` 易被误读为串行一次性通过 | `rust-checks-r2-serial.json`、`rust-checks-r3.json` 均 exit 101；对应日志尾部 `152 passed; 1 failed` | 在 RESULT/checkpoint 明确三次串行结果与 r4 修复路径（P22 fixture），避免“串行通过”歧义 | open |
| R-007 | P2 | 候选工作树 `apps/desktop/frontend/node_modules`、`dist`、`verification/P04/diagnostic_p22_692_*.jsonl` | 工作树非纯净目录：node_modules 84 MB、dist 462 KB、测试生成 jsonl（含 `C:\Python314` 本地路径）。Git 对象交付无影响，目录/zip 交付会携带依赖、构建产物与本地路径 | `git status --porcelain --ignored` 列出三类；`verification/P04/diagnostic_p22_692_1792842383784.jsonl` 2,553 B | 明确“仅通过 Git 对象/分支交付”；若需目录交付则先清理 ignored 内容并复验 | open |
| R-008 | P2 | `verification/GIT-CLEAN-PUBLICATION-1/`（checkpoint.md、checks-r3/r4、core-checks*、core-tests* 等 8 个） | `evidence_dir` 含未登记过程文件（governance warning）；Canonical Evidence 表以仓外 review-package 路径登记，仓内同名副本未登记，权威指针存在双份 | 独立运行 governance check 输出 4 warnings，其中第 4 条列 8 个文件；冻结 `governance-check.json` 同 | 把过程文件归入 workspace，或明确列为 SOURCE_PIN；避免同一证据双份不同口径 | open |
| R-009 | P3 | `RESULT.md:21`、`HANDOFF.md:21` | 措辞：“3 项失败”实为 1 个参数化测试 × 3 组参数；不影响数字真实性 | `core-tests-r2.log:13,21,29` 同一测试名 + 3 组参数 id | 改为“1 个参数化用例的 3 组参数失败” | open |
| R-010 | P3 | 候选 `SOURCE_MANIFEST.json` 的 `generated_files[5]` | 第 6 项 `experiments/TASK-016/samples/manifest.json` 缺 `generator` 字段（另 5 项有），与 Task 描述“生成项含 generator”不完全一致；追溯性未丢失 | `generated_files` key census：5 项含 generator、1 项仅 path/sha256/kind | 补 `generator` 字段，或在 RESULT 说明该 manifest 由生成器创建 | open |
| R-011 | P3 | Task/HANDOFF 描述 vs 候选 `.git` | 表述偏差：实际 `packed-refs` 不存在，只有 1 个 loose ref（隔离性更强，不影响结论） | `Test-Path .git/packed-refs` = False；`show-ref` 仅 1 行 | 更正描述为“1 个 loose ref、无 packed-refs” | open |
| R-012 | P3 | `validation.json:7`（`private_profile_path_hits: []`） | 口径需明确：真名目录 `49745` 残留 0，但源 blob 原样导出仍含假名占位 `C:/Users/Alice`、`C:\Users\sec-fix-path-echo-1`、`C:\Users\settings-secret-agent`、`USERPROFILE` 等；仅在“真实用户目录”口径下 `[]` 成立 | 候选 5 个文本文件中命中 `C:\Users`；均为源 blob 内容 | 在 RESULT 注明 `private_profile_path_hits` 的判定口径（仅真实用户名），避免读者误解为“无任何 C:\Users 路径” | open |
| R-013 | P3 | 候选 `SOURCE_MANIFEST.json`、根 `.gitignore` | 源 commit 在相同路径也跟踪 5 PNG + `samples/manifest.json`（旧渲染批次，内容不同），manifest 只记录重新生成后的 hash，未记录旧 blob；根 `.gitattributes` 未导出，换行策略依赖本地 `core.autocrlf=false` | 源 `git ls-tree HEAD:experiments/TASK-016/samples` 与候选生成物 hash 不同；候选无 `.gitattributes` | 在 README/RESULT 加一句旧版本说明；明确换行策略 | open |

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| Canonical Evidence 9 项 SHA | `Get-FileHash -Algorithm SHA256` 逐项比对 Task 表 | Win11 / pwsh 7；源 `349e61faf`、候选 `e34a90d0` | PASS 9/9 MATCH（`SOURCE_MANIFEST` `be511fdb…`；`validation` `40d812e7…`；`selection` `406a8945…`；`prepare_snapshot` `a9d7b71a…`；`checks-r4` `65733bec…`；`rust-tests-r4-serial` `ab66e07c…`；`core-checks-r2` `5b6db716…`；`core-tests-r2.log` `0215d7e9…`；`frontend-tests-r3.log` `56f025c2…`） | 本文件第 1 节；仓内 verification 与 review-package 副本 8/8 同名文件亦 MATCH |
| 候选 Git 隔离 | `git rev-list --count/--parents/--max-parents=0`、`show-ref`、`remote -v`、`fsck`、`cat-file -e`、`count-objects -v`、检查 alternates/packed-refs/shallow/grafts/replace | 候选 `e34a90d0` | PASS：1 root 无 parent、1 loose ref、无 remote/alternates/pack、866 loose objects 全 reachable、fsck 0、status clean、tracked 733；源 base `349e61faf` 与源全部 4131 commit 均不存在于候选对象库 | 本文件；子核查 task-1 报告 |
| 338 禁止对象 | 从源仓 `push-material-disposition.json` 取 `outer_object`+`embedded_git_object`（338 unique），对候选 `git cat-file --batch-check`；对 730 blob 做 payload sha256/JPEG 魔数/base64 扫描 | 源 `349e61faf`；候选 `e34a90d0` | PASS：absent 338 / present 0；内容级匹配 0/0/0；169 embedded 均 JPEG 魔数且 sha256=payload_sha256 | 子核查 task-1 报告 |
| SOURCE_MANIFEST 724 逐项 | 源 `git ls-tree -r -z 349e61faf` + `git cat-file --batch` 逐 blob；比对 source_blob/source_sha256/候选 sha256/全文 | 源 `349e61faf`；候选 `e34a90d0` | PASS：724/724 一致、0 mismatch；722 逐字节相同、2 为变换项；6/6 生成物可复现（独立重跑 rc=0 逐字节相同） | 子核查 task-2 报告；Reviewer 复核 manifest 固定 hash 与 733 构成 |
| 2 处变换与 `49745` 残留 | 行级 diff 源 blob vs 候选；全仓 733 文件（含二进制）搜 `49745` | 候选 `e34a90d0` | PASS：恰 2 文件各 1 行 `49745`→`USER`；残留 0 | 子核查 task-2 报告；Reviewer 独立 grep 0 命中 |
| 前端 435 与树等价 | 读 `frontend-tests-r3.log` 尾部；`git rev-parse HEAD:apps/desktop/frontend`（r3 vs r4）；`git ls-tree -r` 逐条 | r3 `87accae4`；r4 `e34a90d0` | PASS：45 文件/435 passed；tree `662ad099…` 相同、131 项逐条一致；r4 build exit 0 | 日志与 checks-r3/r4；Reviewer 独立 rev-parse |
| Rust 串行/并行 | 读 `rust-tests-r2.log`、`-r2-serial.log`、`-r3-serial.log`、`-r4-serial.log` 与对应 checks JSON | r2/r3/r4 | r4 串行 PASS（153/0/1/12，exit 0）；r2 并行 FAIL（150/3）、r2 串行 FAIL（152/1）、r3 串行 FAIL（152/1）→ 并发未裁决，AC4 BLOCKED | 日志尾部原文；Reviewer 独立读日志与 checks |
| Core 771/3 与根因 | 读 `core-tests-r2.log`、`core-tests-isolated-deps.log`；静态读 `test_p16_reader_export.py`、`src/infrastructure/plugins/{sandbox,service}.py`；只读 SQLite 查 basetemp `library.db` 的 `plugin_events` | r2 `b1e6935…`；src/tests tree=r4 | 数字 PASS：771 passed / 3 failed，无 skip/xfail；根因支持：3 个 DB 均记录 `PLUGIN_HOOK_UNAVAILABLE / cannot grant sandbox access to python.exe`；归因证据未冻结 → AC4 BLOCKED | 本文件；子核查 task-3 报告与 Reviewer 独立 SQLite 查询 |
| 源码树等价绑定 | `git rev-parse HEAD:<dir>` 比对 r2/r3/r4 的 `src`、`tests/core`、`apps/desktop/frontend`、`apps/desktop/src-tauri` | r2/r3/r4 | PASS：`src` `1571a2ca…`、`tests/core` `da2f41fb…`、frontend `662ad099…`、src-tauri `c45ffb3f…` 三版一致 | Reviewer 独立 rev-parse |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GIT-CLEAN-PUBLICATION-1.md` | 主仓 `349e61faf`（工作区 dirty 不变） | PASS（4 warnings），exit 0；与冻结 `governance-check.json` 一致 | 命令输出；`review-package/governance-check.json` |
| 安装包/签名/模型/GUI/完整审计 | 未运行 | — | NOT_RUN | Task 与 RESULT/HANDOFF 均声明不在此范围 |
| 产品实现正确性/UI/持久化行为 | 未运行（快照非功能变更，无代码改动可审） | — | N/A | 候选仅复制源 commit 内容 |

## 结论与复审

**decision: blocked。** 理由：

1. **材料与来源层面可以确认（AC1–AC3 MET）。** 724 个源文件逐项可追溯到固定源 commit；338 个禁止对象及其内容在候选对象库全部不存在；候选为独立单一根历史、无 remote、未继承源历史；源 main/index 与 6 个 P04 日志未被改动。未发现私有素材或凭据随 Git 对象外泄的事实，也未发现来源伪造或特许越界。
2. **完整验证 Gate 未通过（AC4 BLOCKED）。** 前端 435 与 r4 构建通过且树等价成立；Rust 仅 r4 单次串行通过，默认并发从未通过且并行失败涉及全局 `UNREAPED_WORKER_REGISTRY`；Core 3 项失败虽已静态定位为 AppContainer 无法为本机 Python 授 ACL，但原始证据未进冻结包；12 项 packaged 与安装包、模型、GUI、完整审计均未运行。以上均不足以宣称“产品可发布/可集成”。
3. **AC5 PARTIAL。** 固定 SHA、Handoff、冻结证据已形成，独立 Review 由本文件完成（不虚构批准）；但整体 Task 仍受 AC4 阻断，**不能置 `done`**。
4. **不构成授权的结论：** 本 Review 不批准 push、不批准默认分支/远端变更、不批准产品 release 或安装包验收，也不解除“不传播”裁决。

**可保留的结论：** 该候选可作为**本地、可检查、材料已排除的源码快照**继续保留与移交检查；它与源 main 无共同对象库，不得当作普通主线增量合并。

**复审条件（满足后可追加新 head 的复审）：**

- R-001：另释诊断 Task 复跑 Rust 默认并发，给出 `UNREAPED_WORKER_REGISTRY`（`library_bridge.rs:1606-1608`、`MAX=32`）的测试隔离/产品并发裁定；
- R-002：把 Core 3 项失败的 `plugin_error` 原始记录（basetemp `library.db` 摘要与路径/provenance）登记为 SOURCE_PIN，或在 `_grant` 保留 icacls returncode/stderr 后重跑；
- R-004/R-005/R-006：补齐冻结包缺失文件、日志 EXIT/shell 头与串行结果披露；
- 冻结 sidecar 后运行 12 项 packaged；如仍需宣称发布，另按发布 Gate 验收；
- R-003/R-007/R-008 等证据与交付方式问题按建议修正；
- 任何新 head 必须重新 Review；本文件在 head 变化后自动成为历史记录。

**剩余风险：** 并发测试隔离风险可能对应真实产品稳定性问题（未裁决）；Core 环境限制在其他主机上未必复现，当前机器的 `C:\Python314` 权限状态未固化；候选工作树 ignored 产物的非 Git 交付方式存在携带本地路径风险。
