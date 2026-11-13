# 证据索引

## 2026-11-13 Codex 最终独立 Review（Codex-first 裁决执行）

- `reports/CODEX-FINAL-REVIEW-2026-11-13.md`（原字节 = `evidence/codex-final-review-20261113.result.md`）：Codex 全新上下文对 `reviewed_head=d92859c9ac8a4d3122d6cabfe4d44af980574104` 的最终只读 Review；结论 **REJECT**（属交付文档返修要求，不改变产品 Release Gate BLOCKED）。含 11 候选逐项裁决、AUDIT-11-INC-001 维持 INVESTIGATE、P0–P3 计数、R1–R4、AC 与 Task 生命周期建议。
- `logs/codex-final-review-dispatch-20261113.log`、`evidence/codex-final-review-20261113.meta.json`：CLI `codex-cli 0.162.0`、session `01a1d4ce-6b79-7b43-939d-834e3cdc21a9`、EXIT 0、耗时 1,911.5s、reviewed/expected HEAD 与工作树状态、原始 stderr 路径与 SHA-256。
- `evidence/codex-final-review-20261113.prompt-used.txt`、`.stdout.log`、`.stderr-sanitized.txt`：实际派发 prompt（含 expected_head 与沙箱限制说明）、stdout 原文、stderr 精简元数据；完整 raw stderr 仅保留于 Task workspace。
- 说明：Codex `-s read-only` / `-s workspace-write` 在本机无法 spawn 子进程（Windows error 740），前两次派发在 `b72363aa` 前置检查阶段停止（第二次另因 8 个未跟踪 gate 文件判定工作树不 clean），不构成 Review；第三次以 `-s danger-full-access` 派发并严格只读，Review 前后工作树均 clean。

- `logs/task-card-pin-recompute-20261113-after-review.log`、`evidence/task-card-pin-recompute-20261113-after-review.json`：Codex Review 返修后 Task 卡复算（428 条 pins，含 30 条新 pin 与 9 个重复 evidence_id 重命名）；428/428 PASS，0 fail。

- 返修后 gate batch generated HEAD=`076dfbb63ad7f2b63605bfc16cdd8079e96dd6b2`，四项 EXIT 0（default/TaskPath 各 3 warnings、verify_pins 18/18、API 1/79/6=86）；`logs/audit-post-evidence-076dfbb6-*.log`、`evidence/audit-post-evidence-076dfbb6-*.json`。

## 2026-11-13 P7 DSH 集成核验与 ZCode 额度复核

- `reports/P7-INTEGRATION-CONSISTENCY-CHECK-2026-11-13.md`：DSH 集成核验记录（非 ZCode Review）；371 条 Canonical Evidence 复算、14 条 worktree/BLOB 基准更正、报告计数/AC/R1–R4/Gate 一致性与文档漂移清单。
- `tests/verify_canonical_evidence.py`：Task 卡 Canonical Evidence 只读复算器（`git cat-file` 定位 commit/path 并重算 raw Git BLOB SHA-256）。
- `logs/task-card-pin-recompute-20261113-pre-correction.log`、`evidence/task-card-pin-recompute-20261113-pre-correction.json`：更正前复算（任务卡字节由 `HEAD:doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md` 精确导出、133,609 bytes）；357 pass / 14 fail，generated HEAD=`48ccb75ce1a547cf89e4d38cd577b868e15de5ce`。
- `logs/task-card-pin-recompute-20261113.log`、`evidence/task-card-pin-recompute-20261113.json`：更正后复算（当时 Task 卡 371 条）；371/371 pass、0 fail，generated HEAD=`48ccb75ce1a547cf89e4d38cd577b868e15de5ce`。
- `logs/task-card-pin-recompute-20261113-final.log`、`evidence/task-card-pin-recompute-20261113-final.json`：本轮回填 27 条新 pins 后的最终复算（Task 卡 398 条，同一 BLOB 算法）；398/398 pass、0 fail。
- `evidence/task-card-pin-mismatch-investigation-20261113.json`：14 项不匹配根因调查（记录值 = worktree CRLF 字节；对 commit BLOB 做 LF→CRLF 变换后 14/14 精确匹配）。
- `evidence/task-card-pin-correction-20261113.json`：14 项 pin 的旧值/新值对照，依据 ZCode AUDIT-08 closure review 的 BLOB 基准。
- `logs/zcode-final-review-probe-20261113T1935Z.log`、`evidence/zcode-final-review-probe-20261113T1935Z.json`、`evidence/zcode-final-review-probe-20261113T1935Z.stderr-sanitized.txt`：2026-11-13 19:36 本地 ZCode 最小 plan 探测；provider `1310` / HTTP 429、EXIT 1、stdout 仅 CRLF、无 session/response；原始 stdout/stderr 保留于 Task workspace 并记录 SHA-256。该探测不构成 Review。

## AUDIT-05/06（2026-11-13）

- `reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md`：SFX 与翻译链路阶段结果、候选观察及 NOT_RUN 边界；结论均为 `PARTIAL`，待 ZCode 独立裁决。
- `tests/test_audit05_sfx_regression.py`、`tests/test_audit06_context_observations.py`：审计专用合成回归；未改原有测试或产品代码。
- `logs/audit05-06-targeted-20261113.log`、`evidence/audit05-06-targeted-20261113.json`：generated HEAD=`d96529ebff6cf752ad64a676d05ec622da09e565`，247 passed / 3 deselected，EXIT 0。
- `logs/audit06-context-20261113.log`、`evidence/audit06-context-20261113.json`：generated HEAD=`d96529ebff6cf752ad64a676d05ec622da09e565`，84 passed，EXIT 0。
- 本阶段未运行真实模型、真实 GUI 或付费 API；测试数据置于 workspace Task 环境。三个候选观察见 `AUDIT_ISSUES.md`，严重级别与是否构成正式 finding 待 ZCode 裁决。
- `logs/audit05-06-governance-c0da575-20261113.log`、`evidence/audit05-06-governance-c0da575-20261113.json`：四项门禁 generated HEAD=`c0da575b46e30ecda7a6aefe3bbfe103440ae493`；default/TaskPath check 均 PASS（各 3 warnings）、pins 18/18、API inventory 1/79/6=86；四项 EXIT 0。
- `logs/audit05-06-post-pinbackfill-919b55d-20261113.log`、`evidence/audit05-06-post-pinbackfill-919b55d-20261113.json`：Task pinbackfill HEAD=`919b55d932f3665693b047dfcb075b2bdf1c6d1c` 上 default/TaskPath check 各 PASS（3 warnings）、pins 18/18、API inventory 1/79/6=86；四项 EXIT 0。
- `source/zcode-audit05-06-review-prompt-20261113.txt`：针对固定 reviewed_head=`dfef8d8919fe2d19013e65c84948fb288c2c9928` 的自包含独立只读 Review 输入。
- `logs/zcode-audit05-06-review-dispatch-20261113.log`、`evidence/zcode-audit05-06-review-attempt-20261113.json`：ZCode CLI `0.17.1` plan-mode 调用已发出；服务返回 provider code `1310` / HTTP `429`，额度提示于 `2026-11-17 18:40:33` 重置，EXIT 1、无 session/response。该尝试不计为 Review。
- `evidence/zcode-audit05-06-review-attempt-20261113.stdout.txt`、`evidence/zcode-audit05-06-review-attempt-20261113.stderr-sanitized.txt`：空 stdout 与脱敏错误摘要；含瞬态 `set-cookie` 的原始 stderr 仅保留在 Task workspace，raw SHA 记于 JSON/dispatch log。
- `logs/audit05-06-reviewattempt-gates-46db551-20261113.log`、`evidence/audit05-06-reviewattempt-gates-46db551-20261113.json`：generated HEAD=`46db551b4e4fd38f9f46c0653adef9330afc66ad`，default/TaskPath check 各 PASS（3 warnings）、pins 18/18、API inventory 1/79/6=86；四项 EXIT 0。

- evidence/baseline.json：Git/环境。
- evidence/source-manifest.json：源码/config路径、SHA256、语法结果。
- evidence/static-summary.json：扫描统计和例外。
- logs/：完整执行命令、解释器、EXIT、耗时。
- reports/PUSH_READINESS.md：固定历史范围、未提交归属、推送阻断与后续指令。
- evidence/push-manifest.json：推送候选 SHA、阻断项和证据指纹（不表示上传授权）。
- evidence/push-history-scan.json：全历史新增 blob、压缩 Git 对象与 ZIP 的脱敏扫描。
- evidence/push-material-provenance.json：命中裁定、registry 比对与材料来源缺口。
- evidence/push-worktree-ownership.json：6 个既有 P04 日志的保护指纹。
- logs/push-preparation-checks.json：本轮登记、扫描自检与治理检查结果。
- reports/MATERIAL_CLEARANCE.md：4个合成PNG精确溯源、169个JPEG关联证据与34份数据库只读核查，当前材料阻断裁定。
- evidence/push-material-inspection.json：历史tree路径、图像头、源manifest/hash、逐库结构/计数与限制（不含记录原文）。
- tests/inspect_push_materials.py：复跑材料核查及只读自检；派生SQLite副本只保留在workspace task-env。
- logs/push-material-checks.json：本轮材料核查、自检和治理检查的实际argv/exit。
- reports/MATERIAL_DISPOSITION_OPTIONS.md：完整历史/独立干净快照/暂不推送的具体方案；仅设计，待用户裁决，未释放实施。
- evidence/push-material-disposition.json：用户“不传播”裁决及169个JPEG/压缩外层blob的禁止上传指纹；本地保留。

## 段 B（当前产品基线 `10e4ee013835605800d3830fb960ae8d3aa04167`）

- `reports/00_BASELINE-SEGMENT-B.md`：当前架构的 AUDIT-00 基线结论、有效源码范围和历史缺口。
- `evidence/baseline-segment-b.json`：固定 Git/environment、dirty 状态、目录范围和排除计数。
- `evidence/source-manifest-segment-b.json`：1,301 个源码/构建配置条目的 Git blob SHA-1、SHA-256、字节数与分类。
- `logs/audit-00-segment-b.log`：基线清单生成的命令、shell/interpreter、生成时 HEAD、时点与 EXIT。
- `tests/rebaseline_audit00.py`：段 B 基线生成器；只读取所选代码/配置 blob，不读取排除数据目录的内容。
- `reports/TEST-MAPPING-ADJUDICATION-2026-11-12.md`：ZCode 对段 B 当前/Legacy 测试 suite 的只读映射裁决，以及 .NET suite 建议和原始 AUDIT-01–14 清单缺失限制。
- `logs/test-mapping-adjudication-20261112.log`：ZCode session/turn、命令/EXIT 与原始清单定位搜索结果。
- `reports/TEST-EXECUTION-ADJUDICATION-2026-11-12.md`：ZCode 对 smoke/current-vs-Legacy 面、8 个 `.NET` 测试项目和 no-restore 输出隔离方式的后续裁决。
- `logs/test-execution-adjudication-20261112.log`：ZCode session/turn、`smoke`/solution/assets/ArtifactsPath 只读核验命令与 EXIT；没有执行测试。
- `tests/audit_runner.py`：段 B suite 范围映射；保存历史结果名、记录 HEAD/branch/EXIT；`.NET` 逐项目运行并核对前后 porcelain。
- `reports/PROBES-RESULT-SEGMENT-B.md`：段 B probes 的 2 个待分级问题、1 个未复现越界覆盖预期与 EXIT 1 边界。
- `logs/audit-probes-segment-b-20261112T081030840760Z.log`、`evidence/audit-probes-segment-b-20261112T081030840760Z.json`：段 B probes 生成 HEAD、argv、时点、输出、elapsed 和 EXIT。
- `reports/PROBE-TRIAGE-SEGMENT-B-2026-11-12.md`：ZCode 对两项 probes 的 Medium / High confidence 分级、第三项 defense-verified 定性及证据边界。
- `logs/probe-triage-confirmation-20261112.log`：ZCode 只读确认命令、session/turn/trace、生成 HEAD、时点、回答与 EXIT。
- `logs/pytest-segment-b-20261112T081732598825Z.log`、`evidence/pytest-segment-b-20261112T081732598825Z.json`：Python Core 限定 pytest 的 argv/cwd、生成 HEAD、起始时点、耗时、完整失败输出与 EXIT；结果为 3,519 passed / 16 failed / 10 skipped / 11 warnings。
- `reports/PYTEST-RESULT-SEGMENT-B-2026-11-12.md`：pytest 失败分组、skip/warning 和 suite 证据限制摘要。
- `reports/DOTNET-RESULT-SEGMENT-B-2026-11-12.md`：8 个 Avalonia 测试项目的 TestHost 阻断裁定、TRX 0 计数、工作树守护核验及后续范围。
- `logs/dotnet-result-adjudication-20261112.log`：ZCode 对 .NET suite 的只读 adjudication 原文、session/turn/trace、生成 HEAD 与 EXIT。
- `logs/dotnet-app-20261112T083119769139Z.log`、`evidence/dotnet-app-20261112T083119769139Z.json`；同一 run ID 下另有 appearance、applicationcore、coreclient、designsystem、host、presentationavalonia、themeengine 的配套 log/JSON。8 组均含命令、生成 HEAD、逐项时点/elapsed、EXIT 与 porcelain 守护字节摘要。
- TRX 指针：`G:/CODEX/New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT/dotnet/results-20261112T083119769139Z/`；8 个 TRX 外部 artifact 只读解析后 `total/executed/passed/failed=0`，未复制入仓库，保留在 Task 指定 workspace。
- `reports/SMOKE-RESULT-SEGMENT-B-2026-11-12.md`：smoke `core,wire` 分项结果、7 项前置阻断与级联分析、无证据项及 ZCode adjudication。
- `logs/software-smoke-segment-b-20261112T084557725697Z.log`、`evidence/software-smoke-report-segment-b-20261112T084557725697Z.json`、`evidence/software-smoke-segment-b-20261112T084557725697Z.json`：runner 命令、生成 HEAD、起始时点/elapsed、分层检查结果和 EXIT。
- `logs/smoke-result-adjudication-20261112.log`：ZCode 只读 adjudication 原文、session/turn/trace、生成 HEAD 与 EXIT。
- `reports/GOVERNANCE-RESULT-SEGMENT-B-2026-11-12.md`：默认 governance suite 的命令、生成 HEAD、EXIT、3 warnings 与最终 gate 复跑限制。
- `logs/governance-segment-b-20261112T085303591759Z.log`、`evidence/governance-segment-b-20261112T085303591759Z.json`：governance runner 的 argv/cwd、生成 HEAD、时点、elapsed 与 EXIT。
- `reports/ZCODE-CHECKPOINT-REVIEW-SEGMENT-B-2026-11-12.md`：新独立 ZCode Reviewer 对 reviewed_head `499a6b8e6…` 的 checkpoint 结论、R-1–R-4 findings 与限制。
- `logs/zcode-checkpoint-review-20261112.log`、`logs/zcode-checkpoint-review-findings-20261112.log`：ZCode fresh-context CLI 首轮结论和完整 finding 重述。
- `logs/review-checkpoint-recheck-20261112.log`：实现侧在 reviewed_head Git 对象上逐路径核对 37 个变更、复算 46 个 Canonical/SOURCE_PIN SHA-256 的原始只读结果；EXIT 0，ZCode addendum 已接受为 R-1 closure evidence。
- `reports/ZCODE-CHECKPOINT-REVIEW-ADDENDUM-2026-11-12.md`、`logs/zcode-checkpoint-review-addendum-20261112.log`：ZCode addendum 摘要及原始 CLI 记录；R-1/R-2/R-3 CLOSED、R-4 保持 observation，结论仍限于 `PASS_FOR_CHECKPOINT`。
- `reports/ZCODE-FINAL-CHECKPOINT-REVIEW-2026-11-12.md`、`logs/zcode-final-audit-review-20261112.log`：ZCode 新独立上下文对 reviewed_head `d9478939f…` 的最终 checkpoint review；`PASS_FOR_CHECKPOINT`，F-1/F-2/F-3 的机械证据已补存，待 addendum 复核。
- `logs/review-final-integrity-20261112.log`：固定 `reviewed_head=d9478939f…` 的两段 `git diff --name-status` 路径授权核对及 52 行 BLOB SHA-256 复算；36 个路径条目均 allowed，52/52 pins 匹配，EXIT 0。
- `logs/final-governance-gates-20261112.log`：default/TaskPath check、18 pins、API inventory 的完整输出、生成 HEAD、时点和 EXIT；generated HEAD=`b9b6c5801…`，四项 EXIT 0。
- `logs/postreview-final-verification-20261112.log`：generated HEAD=`ac188dde5…` 的四项治理门禁和 Task 当前 56 行 Canonical/SOURCE_PIN Git blob SHA-256 逐项复算；所有检查 EXIT 0。
- `reports/ZCODE-FINAL-REVIEW-ADDENDUM-2026-11-12.md`、`logs/zcode-final-review-addendum-20261112.log`：ZCode 原 Review session 的只读 addendum；F-1/F-2/F-3 CLOSED，R-4 保持 observation。addendum 提出的 Task pin 与 reviewed_head 到 addendum head 路径范围跟进，见下方完整性日志。
- `logs/postaddendum-integrity-20261112.log`：generated HEAD=`b17fead6d2cbbd2324ffb0a85096eb50448050ff`；对 reviewed_head=`d9478939f2cee81104f18ea757d81cec71c36225` 的 11 个 diff 路径逐项核对，全部属于 allowed_paths；复算当时 Task 的 57 行 pin，57/57 匹配、0 mismatch；EXIT 0。该日志自身及 addendum 报告/原始日志的 Canonical Evidence pin 在后续证据提交后回填。
- `reports/ZCODE-CURRENT-HEAD-CHECKPOINT-REVIEW-2026-11-12.md`、`logs/zcode-current-head-checkpoint-review-20261112.log`：ZCode fresh independent context 对 reviewed_head=`453327ff19ea012026b76d2e10cdcf2c93c58038` 的 checkpoint review，`PASS_FOR_CHECKPOINT`（0 P0 / 0 P1）；N-1/N-2 为 P3、N-3/R-4 为 P4 observation；CLI EXIT 0。报告保留审查当时状态，不追改为后续补记结果。
- `logs/final-post-pinbackfill-gates-20261112.log`：四项治理门禁在 generated HEAD=`453327ff19ea012026b76d2e10cdcf2c93c58038` 的完整输出、命令、UTC 时点及 EXIT；默认/TaskPath check、18 pins、API inventory 均 EXIT 0。
- `reports/ZCODE-LIFECYCLE-ADJUDICATION-2026-11-12.md`、`logs/zcode-lifecycle-adjudication-20261112.log`：ZCode 初次生命周期裁决及原始 CLI 输出；因误将 Codex prompt 选项归为用户原话，已由更正裁决明确撤回，不可作为关闭依据。
- `reports/ZCODE-LIFECYCLE-ADJUDICATION-CORRECTION-2026-11-12.md`、`logs/zcode-lifecycle-adjudication-correction-20261112.log`：ZCode 更正后的终局裁决与原始 CLI 输出；Task 保持 `in_progress`，唯一待用户明确接受 `closed_with_limitations` 的具体语义。保留 AC2/AC3/AC4 PARTIAL、AUDIT-01–14 BLOCKED 和 Release Gate BLOCKED。
- `logs/original-checklist-git-history-search-20261112.log`：generated HEAD=`5cb792e0966817bd642d173ab7db844b2dce092c`；记录 Task 自身可达 Git 历史、`AUDIT-14`/`15项专项` 定向 `-S` 搜索及最早 Task blob。最早版本 `1248f2b8a` 仅含通用 AC1–AC4 和 AUDIT-00–14 范围，没有 AUDIT-01–14 逐项定义；未从当前 Task/audit 子树历史恢复清单。
- `reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md`：当前 Avalonia composition、V1 可计数边界、NOT_WIRED 能力、历史路径/文档债务及独立审查候选；静态阶段 `PARTIAL`。
- `scripts/audit14_static_inventory.py`：AUDIT-14 有界只读采集脚本；不启动 GUI、不构建、不运行测试、不访问用户数据。
- `logs/audit14-static-20261112T192852Z.log`、`evidence/audit14-static-20261112T192852Z.json`：脚本/命令清单、branch、生成 HEAD、UTC、cwd、各条 argv/elapsed/EXIT 与定点搜索输出；所有扫描及产品目录 diff 均 EXIT 0。
- `scripts/capture_audit14_governance.py`：按顺序复核 default check、TaskPath check、18 pins、API inventory 并保留 argv/cwd/UTC/elapsed/EXIT 的采集器。
- `logs/audit14-governance-20261112T193119Z.log`、`evidence/audit14-governance-20261112T193119Z.json`：stage HEAD=`e67fef47461a0de6a600c7fcf67b6a13c9b64635` 首轮 default/TaskPath 因 STATUS/Plan 超预算各 EXIT 1；18 pins、API check EXIT 0。后续精简仅状态摘要后重新检查。
- `logs/audit14-governance-20261112T193219Z.log`、`evidence/audit14-governance-20261112T193219Z.json`：同一 stage HEAD 上修订状态摘要后 default/TaskPath 均 EXIT 0（各 3 warnings），18 pins 18/18 EXIT 0，API 1/79/6=86 EXIT 0；输出含各命令时点/elapsed/argv。
- `source/zcode-audit14-review-prompt-20261113.txt`：ZCode fresh independent context 对 AUDIT-05/06 与 AUDIT-14 七项候选的固定 HEAD 只读 Review 指令；不含人工裁决预设，不授权产品修改。
- `logs/zcode-audit14-review-dispatch-20261113.log`、`evidence/zcode-audit14-review-attempt-20261113.json`：对固定 reviewed_head=`26888045ff475fb2e34b043c55c168f4bd78cd52` 的只读 plan-mode 调用；provider code `1310` / HTTP `429`，EXIT 1、空 stdout、无 session/response；raw stderr hash 保留，正文只在 task-env。
- `evidence/zcode-audit14-review-attempt-20261113.stdout.txt`、`evidence/zcode-audit14-review-attempt-20261113.stderr-sanitized.txt`：失败尝试空 stdout 与脱敏 provider/额度回执；不构成 Review，重置时间见回执。

## 2026-11-13 AUDIT-03

- reports/AUDIT-03-IMPORT-PROJECT-2026-11-13.md：15 项原始检查矩阵、两条导入路径、限制和 FAIL 依据。
- tests/audit_runner.py：新增 audit03-import 定向 suite；按 Core 与 FEA-09 分组，避免多个 conftest.py 的收集冲突，并排除 PySide/QML 历史测试。
- tests/capture_audit03_static.py：捕获 task base 产品路径 diff、当前 allowed path 工作树路径和 whitespace EXIT。
- logs/audit03-core-import-20261112T200824899900Z.log 与 evidence/audit03-core-import-20261112T200824899900Z.json：generated HEAD=8071caccae1a7885fb41b95889cbdc0e80eeb963；87 passed，EXIT 0。
- logs/audit03-referenced-import-20261112T200824899900Z.log 与 evidence/audit03-referenced-import-20261112T200824899900Z.json：同 HEAD；77 passed，EXIT 0。
- logs/audit03-static-20261112T200836Z.log 与 evidence/audit03-static-20261112T200836Z.json：generated HEAD=8071caccae1a7885fb41b95889cbdc0e80eeb963；src/apps/tests 产品 diff EXIT 0；当前 20 条工作树路径均在 allowed_paths；working-tree whitespace EXIT 0。完整 base-to-head 变更集里的 14 条 FEA-11-HOST-AUTH-4 路径是既有提交，不是本 Task 工作树修改。
- logs/audit-probes-segment-b-20261112T195906381034Z.log 与 evidence/audit-probes-segment-b-20261112T195906381034Z.json：generated HEAD=934c81017cadf20e96fd2ee60bfa247086638be6；suite EXIT 1 / 2 passed / 1 failed，含 SEG-B-PROBES-001 junction 越界写复现与独立防线验证；不得把 test PASSED 解释成产品通过。
- 过程记录：audit03-import-project-20261112T195723565045Z 在 HEAD=55630b5c19c20f33332a097eeef917ac5e48cffb 收集阶段 EXIT 2，无产品测试执行；分组后通过。中间 PySide/QML 6 passed 不计入当前架构证据；早期 static capture 对历史差异误报 EXIT 1，最终修正结果见 20261112T200836Z。
- logs/audit03-post-evidence-gates-20261112T201910Z.log 与 evidence/audit03-post-evidence-gates-20261112T201910Z.json：generated HEAD=03b1a7acc5a324dcd1884df82d748569b2c7f91e；default 与 `-TaskPath` check 各 PASS / EXIT 0（各 3 条 warning），verify_pins 18/18 / EXIT 0，API inventory 1/79/6=86 / EXIT 0。工作树在门禁生成时 clean。

## 2026-11-13 AUDIT-04

- reports/AUDIT-04-OCR-DETECTION-2026-11-13.md：OCR/检测真实链路、12 项矩阵、175+40 synthetic pass、质量结论边界与 NOT_RUN 清单。
- tests/audit_runner.py：增加 `audit04-ocr-detection`，providers 与 Core 分组，排除 real-weight provider tests；final runner 在 commit `c20e819009a810ae3828aef7eb8644eb9a3eae80`。
- tests/capture_audit04_static.py：记录产品基线 diff、Task allowed paths、工作树与 whitespace EXIT；source 首次固定于 `5727f5497fdf392295309d031f2632c86e6f1b51`。
- logs/audit04-providers-20261112T203116769705Z.log 与 evidence/audit04-providers-20261112T203116769705Z.json：generated HEAD=`c20e819009a810ae3828aef7eb8644eb9a3eae80`；175 passed、0 skipped、EXIT 0。
- logs/audit04-core-detect-20261112T203116769705Z.log 与 evidence/audit04-core-detect-20261112T203116769705Z.json：同 HEAD；40 passed、0 skipped、EXIT 0。
- logs/audit04-static-20261112T203819Z.log 与 evidence/audit04-static-20261112T203819Z.json：同 HEAD；产品 diff EXIT 0、whitespace EXIT 0；21 条采集时工作树路径均允许，out-of-scope=0；14 条历史 FEA-11 HOST-AUTH-4 路径作继承项披露。
- 过程记录：runner 初次试跑于 `5727f5497fdf392295309d031f2632c86e6f1b51`，providers 167 passed + Core 40 passed；补入 ORT CPU/auto policy tests 后以最终 runner 在 `c20e819009a810ae3828aef7eb8644eb9a3eae80` 重跑为正式结果。初次试跑与早期静态捕获 `20261112T202910Z` / `20261112T203116Z` / `20261112T203329Z` 的日志/JSON均保留。
- logs/audit04-post-evidence-gates-20261112T203946Z.log 与 evidence/audit04-post-evidence-gates-20261112T203946Z.json：generated HEAD=`c10c3ac39e354f08a068825915ece29bd506e969`；default/TaskPath 各 PASS / EXIT 0（各 3 warnings），verify_pins 18/18 / EXIT 0，API inventory 1/79/6=86 / EXIT 0。工作树在门禁生成时 clean。

## 2026-11-13 AUDIT-07

- `reports/AUDIT-07-REPAIR-TYPESET-EXPORT-2026-11-13.md`：阶段矩阵、合成证据、3 个邻接 P16 export 测试失败、两项待 ZCode 裁决候选与真实模型/GUI/字体许可 `NOT_RUN` 边界。
- `tests/audit_runner.py`：新增 `audit07-typeset` suite；源码由 commit `4daa7169752b8f9c85fd8f8a01e5660f98f10481` 固定。
- `logs/audit07-inpaint-pipeline-20261112T205159956924Z.log` 与 `evidence/audit07-inpaint-pipeline-20261112T205159956924Z.json`：generated HEAD=`4daa7169752b8f9c85fd8f8a01e5660f98f10481`；38 passed / 0 skipped，EXIT 0。
- `logs/audit07-rendering-20261112T205159956924Z.log` 与 `evidence/audit07-rendering-20261112T205159956924Z.json`：同 HEAD；73 passed / 0 skipped，EXIT 0。
- `logs/audit07-core-rerender-export-20261112T205159956924Z.log` 与 `evidence/audit07-core-rerender-export-20261112T205159956924Z.json`：同 HEAD；127 passed / 3 failed / 0 skipped，EXIT 1；失败是 P16 reader export hook/options 测试，不是图像像素质量断言。
- `logs/audit07-pillow-source-style-20261112T205159956924Z.log` 与 `evidence/audit07-pillow-source-style-20261112T205159956924Z.json`：同 HEAD；5 passed / 0 skipped，EXIT 0。
- `logs/audit07-font-storage-20261112T205159956924Z.log` 与 `evidence/audit07-font-storage-20261112T205159956924Z.json`：同 HEAD；6 passed / 0 skipped，EXIT 0。
- `logs/audit07-searchable-export-20261112T205159956924Z.log` 与 `evidence/audit07-searchable-export-20261112T205159956924Z.json`：同 HEAD；7 passed / 0 skipped，EXIT 0。
- `logs/audit07-revision-restore-20261112T205631263951Z.log` 与 `evidence/audit07-revision-restore-20261112T205631263951Z.json`：同 HEAD；7 passed / 0 skipped，EXIT 0。
- `logs/audit07-static-scope-20261112T205724Z.log` 与 `evidence/audit07-static-scope-20261112T205724Z.json`：同 HEAD；产品源码/既有测试/依赖/合同差异 EXIT 0，审计越界路径 0，tracked fonts/models 各 0。
- `logs/audit07-governance-4daa716-20261112T211024Z.log` 与 `evidence/audit07-governance-4daa716-20261112T211024Z.json`：generated HEAD=`4daa7169752b8f9c85fd8f8a01e5660f98f10481`；default、TaskPath、verify_pins 18/18、API 1/79/6=86 均 EXIT 0。此为阶段证据提交前门禁；pinbackfill 后仍须复跑。
- `logs/audit07-post-evidence-gates-20261112T211406Z.log` 与 `evidence/audit07-post-evidence-gates-20261112T211406Z.json`：generated HEAD=`46fd59e67b5369637946ecae3af670341a6ad75d`；default/TaskPath 各 EXIT 0（各 3 warnings），verify_pins 18/18 EXIT 0，API inventory 1/79/6=86 EXIT 0。Task pinbackfill 后仍须复跑。
- `logs/audit07-post-pinbackfill-27b1602-20261112T211905Z-default.log`、`logs/audit07-post-pinbackfill-27b1602-20261112T211905Z-taskpath.log`、`logs/audit07-post-pinbackfill-27b1602-20261112T211905Z-pins.log`、`logs/audit07-post-pinbackfill-27b1602-20261112T211905Z-api.log` 与 `evidence/audit07-post-pinbackfill-27b1602-20261112T211905Z.json`：generated HEAD=`27b16028168d1e86987dff7e968f9147b614d34c`；Task pinbackfill 后 default/TaskPath 各 EXIT 0（各 3 warnings）、verify_pins 18/18 EXIT 0、API inventory 1/79/6=86 EXIT 0。

## 2026-11-13 P7 交付与 post-evidence 门禁

- 编号报告：reports/02_ARCHITECTURE_REVIEW.md 至 reports/13_RELEASE_GATE.md、reports/FINAL_AUDIT_REPORT.md；去重台账另保留 AUDIT_ISSUES.md 详细记录。
- AUDIT-09：reports/AUDIT-09-UI-UX-2026-11-13.md；screenshots/audit09-*.jpg；logs/audit09-ui-*.log 与对应 evidence JSON。
- AUDIT-10：reports/AUDIT-10-PERFORMANCE-STABILITY-2026-11-13.md；logs/audit10-performance-20261112T222445371097Z.log；evidence/audit10-performance-metrics-20261112T222445371097Z.json。
- AUDIT-12：reports/AUDIT-12-WINDOWS-DELIVERY-2026-11-13.md；logs/audit12-delivery-inventory-20261112T223042315179Z.log 与同名 JSON。
- AUDIT-13：reports/AUDIT-13-E2E-2026-11-13.md；logs/audit13-core-acceptance-20261112T222650072377Z.log 与同名 JSON。
- P7 gate batch generated HEAD=5a54390f63ed3283ba4a10df359dbc9f3a518a19，commit=592e3f6a9626b45b2962bce4d22f99875ec2e179；default/TaskPath 各 3 warnings EXIT 0，verify_pins 18/18 EXIT 0，API 1/79/6=86 EXIT 0。下一批 generated HEAD=3fc756a1aed8ca366ac0b324ff293cc3e1f9ebb0，commit=c0665ff90408d78097e787bd53af63d96bb32ecf；同样四项均 EXIT 0，细节见各 audit-post-evidence-3fc756a1 文件。此后 generated HEAD=c0665ff90408d78097e787bd53af63d96bb32ecf 的第三批四项门禁也均 EXIT 0，提交=4b91a2d7ff51e2ac6c05eef7c02a4640335fcf92；default/TaskPath 各 3 warnings、pins 18/18、API 1/79/6=86。回填该批 pins 后仍须复跑最终四项门禁。
- Post-pinbackfill generated HEAD=e72bf97816a33e50c8cff5968c198975c3faddbd：default/TaskPath 各 3 warnings、EXIT 0；verify_pins 18/18、EXIT 0；API 1/79/6=86、EXIT 0。日志与 JSON 为 logs/audit-post-evidence-e72bf978-*.log 和 evidence/audit-post-evidence-e72bf978-*.json；下一 pinbackfill 应纳入。
- Final post-pinbackfill generated HEAD=a3a429cc955f12765253a14680e79bab2389dd89：default/TaskPath 各 3 warnings EXIT 0，verify_pins 18/18 EXIT 0，API inventory 1/79/6=86 EXIT 0。原始输出为 logs/audit-post-evidence-a3a429cc-*.log 与 evidence/audit-post-evidence-a3a429cc-*.json，本批按 rolling pin 规则排入下一次 Task-card pinbackfill。
- Current post-pinbackfill generated HEAD=87ee1ea75aefac15a313767c64c149e286d3a8e8：default/TaskPath 各 3 warnings EXIT 0、verify_pins 18/18 EXIT 0、API 1/79/6=86 EXIT 0。logs/audit-post-evidence-87ee1ea7-*.log 与 evidence/audit-post-evidence-87ee1ea7-*.json 已提交并由 AUDIT_RESUME 顶部指向。
- ZCode final Review 派发证据：source/zcode-final-review-prompt-20261113.txt；logs/zcode-final-review-attempts-20261113.log、logs/zcode-final-review-full.stderr.log、logs/zcode-final-review-probe.stderr.log；evidence/zcode-final-review-attempts-20261113.json 及两个空 stdout 文件。固定审查 HEAD=3c40eb5c；两次调用均 provider 1310 / EXIT 1 / 无 session 或 response，故不构成 Review。
- Post-quota checkpoint generated HEAD=77310033f77d5b793fe4ff3734e1ba7cf049c06c，门禁 evidence commit=e61a271fb06f708db67e465be87a396fffc92c47：default/TaskPath 各 3 warnings EXIT 0，verify_pins 18/18 EXIT 0，API 1/79/6=86 EXIT 0。日志与逐项 JSON 为 logs/audit-post-evidence-77310033-*.log、evidence/audit-post-evidence-77310033-*.json。
- Post-pinbackfill generated HEAD=3a1ceccacd5e972413c2d170760ede83ae39a5d1，gate evidence commit=7ecf21c7d724c93c6890703a15394b5854348c69：default/TaskPath 各 3 warnings EXIT 0、verify_pins 18/18 EXIT 0、API 1/79/6=86 EXIT 0。日志与逐项 JSON 为 logs/audit-post-evidence-3a1cecca-*.log、evidence/audit-post-evidence-3a1cecca-*.json；按 rolling pinbackfill 规则待下一次卡面更新纳入。
- Quota recheck generated HEAD=48ccb75ce1a547cf89e4d38cd577b868e15de5ce：ZCode 最小 plan 探测 provider `1310` / HTTP 429、EXIT 1、无 session/response（reset 2026-11-17 18:40:33）；见 `logs/zcode-final-review-probe-20261113T1935Z.log` 与对应 JSON。
- Post-quota recheck gate batch generated HEAD=`52b86d3984f76abdebb4bddf25837b19639ff771`，四项 EXIT 0（default/TaskPath 各 3 warnings、verify_pins 18/18、API 1/79/6=86）；文件为 `logs/audit-post-evidence-52b86d39-*.log` 与 `evidence/audit-post-evidence-52b86d39-*.json`；该批按 rolling pin 规则进入下一次 Task-card pinbackfill。
- 同轮首跑 gate batch generated HEAD=`18357fdcd286ebf8e2c6b1780fcb86d1295d0423` 的 default/TaskPath 因 `doc/STATUS.md` 3,205 bytes 超防膨胀预算而 EXIT 1（pins 18/18、API 86 已 EXIT 0）；失败批次 `logs/audit-post-evidence-18357fdc-*.log`、`evidence/audit-post-evidence-18357fdc-*.json` 原样保留，修复后在同一轮以 52b86d39 重跑。
- Pinbackfill 后 gate batch generated HEAD=`70e92876204932d106f312fcc386177fd2da35f4`，四项 EXIT 0（default/TaskPath 各 3 warnings、verify_pins 18/18、API 1/79/6=86）；`logs/audit-post-evidence-70e92876-*.log`、`evidence/audit-post-evidence-70e92876-*.json`；Task 卡 398 条 pins 复算 398/398 PASS（`logs/task-card-pin-recompute-20261113-final.log`）。
