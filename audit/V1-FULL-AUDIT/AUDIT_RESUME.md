# 恢复入口

2026-10-24；HEAD 349e61faff5f93067af5d4ce2d9e394e0d665b8c；branch main；worktree G:/CODEX/New Manga。

先核对 git status / git rev-parse HEAD 与 evidence/source-manifest.json；保留原6个P04诊断文件。已完成基线/盘点。下一步查看 evidence/*.json 和 logs/*.log 的 EXIT，未有结果的套件通过 `python audit/V1-FULL-AUDIT/tests/audit_runner.py <suite>` 执行；suite=pytest/frontend/rust/smoke/governance/dependencies。所有运行数据 G:/CODEX/New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT。不得直接复跑未知仍运行任务；先检查进程。审计未完成，不宣称PASS。

## 2026-10-24 推送准备 checkpoint

TaskStatus=in_progress；ExecutionState=BLOCKED_MATERIAL_PROVENANCE（仅推送准备阻断，全量审计未关闭）。产品 start/head 仍为上述 `349e61faf`；没有新增提交、暂存、上传、清理或历史改写。

已同步 Status/Plan/Task/TASK_LEDGER；治理检查 PASS（3 warnings），不表示全量审计 PASS。工作区仍有本审计未提交文件、3 份已修改治理文档和6份既有P04日志；具体保护 hash 见 `evidence/push-worktree-ownership.json`，P04均不暂存。完整结果和后续指令见 `reports/PUSH_READINESS.md`；固定推送候选、base和证据hash见 `evidence/push-manifest.json`。

历史离线扫描已覆盖17455个新增blob、2144个zlib对象与3份ZIP；4项凭据命中均为测试占位值。材料许可/数据库隐私仍未证明，173个嵌入图像未取得当前主线标准对象路径映射；不能push。下一精确步骤：按报告追溯嵌入tree/材料来源；不因本次文档同步批量暂存整包审计，尚未冻结的全量审计证据与未分配Reviewer状态均保留。

## 材料复核 checkpoint（当前恢复点）

产品HEAD/branch/worktree不变，Task仍in_progress；推送准备仍BLOCKED_MATERIAL_PROVENANCE。读取 `reports/MATERIAL_CLEARANCE.md` 和 `evidence/push-material-inspection.json`；上面的初次“继续追踪”步骤已被本轮实际检查收窄。

4个嵌入PNG与 `ed607b755` 合成manifest精确匹配。169个JPEG名称集合/页数/尺寸与T1.1.1商业日漫卷册记录完全吻合，但缺逐页源hash，不能把关联当许可。沿182个根tree及本地对象共读取1449个tree，无缺失tree；仍不能从这些根定位169个JPEG完整路径。34份库已readonly immutable检查，12份M2-AC1业务库与生成页hash匹配、5份P18业务库领域表为空；存在22个路径单元格，不签发WAL/删除页隐私结论。

隔离数据库副本保留在 `G:/CODEX/New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT/push-materials/`，只读核查前后hash一致，不清理。6个P04日志仍保护且未暂存，无新增commit/push/历史改写。继续精确步骤：取得用户的来源/许可记录或材料处置选择，按最新报告记录证据；如果缺许可，冻结独立发布方案供裁决，不擅自把清理/历史重写当下一步。全量审计其他AC与独立Review仍未完成。

备选方案已具体写入 `reports/MATERIAL_DISPOSITION_OPTIONS.md`：完整历史推送仍需材料传播证明；许可不足时建议独立的干净源码快照新分支，保留原main/远端main和全部证据。仅设计，未创建导出/分支/新仓库或释放新Task。下一步等待用户材料信息或方案选择，不自动实施。

当前用户裁决覆盖上述等待许可分支：用户明确“我自己的，但是不传播”。169个JPEG及其压缩外层blob已登记禁止上传（`evidence/push-material-disposition.json`），push=BLOCKED_OWNER_NO_DISTRIBUTION。保留全部本地素材与历史；不再重复索要许可，也不推完整main或3个分批候选。推荐下一步由Codex冻结独立干净源码快照的发布目标与Task；尚未释放、不自动创建分支或push。

## 2026-11-12 段 B 恢复点

- 当前 Task 已按 ZCode 受托裁决从 `blocked` 恢复为 `in_progress`。段 A 基线仍为 `349e61faff5f93067af5d4ce2d9e394e0d665b8c`，原有 PASS/NOT_TESTED 作为历史保留；段 B 审计当前 AD-002 产品，固定 base=`10e4ee013835605800d3830fb960ae8d3aa04167`。
- 阶段 0：branch=`main`、工作树 clean；`87f61d8…`、`349e61…`、`b1c1f5a5…` 祖先关系 EXIT 0；`349e61…..HEAD` 为 2366 commits；`.tmp.driveupload` 在旧树中有 2148 个条目。完整命令与 EXIT 见 [阶段 0 日志](logs/stage0-resume-verification-20261112.log)；提交前 WORKTREE SHA-256=`B561337B697AD62506049EF310EF04A52B8C69487CE31F6C9046E2B9B470EB6D`，Git BLOB SHA-256=`7E2A4911D7F1AB2D21DE48C4AC4B77F2C8BACCC5FA6CB1D6C2DFF681F32260A7`（commit `304a40addb4818f415b1e86d5c5b65205eca3605`）。
- 段 B release gates 在 `df120fb56567278e7e9a954e7a81c3f6465625c1` 实测：default PASS/EXIT 0（3 warnings）、TaskPath PASS/EXIT 0（3 warnings）、18 pins PASS/EXIT 0、API 1/79/6=86 EXIT 0。原始日志见 [segment-b-release-gates-df120fb.log](logs/segment-b-release-gates-df120fb.log)，commit `4b5aa2d6a327c7ffa2c5b3025473fb5a6f3f1179`。
- 范围裁决摘要和传播风险证据见 [ZCode 裁决记录](reports/ZCODE-SCOPE-ADJUDICATION-2026-11-12.md)。本地证据支持素材历史于 2026-10-30 随 main push 进入当时公开仓库的高置信推论；当前远端实时可见性未核验，不 push、不删除、不改写历史、不 GC/prune。
- 段 B 启动时 AUDIT-00–14 均未执行；目前 AUDIT-00 已 PASS（仅基线/清单），AUDIT-01–14 仍 NOT_TESTED。报告、JSON 清单与命令日志见 Task Canonical Evidence（commit `1a8238b9f86427efe5c48918f3bc0f2942611732`）。审计仅本地与只读隔离，私有图片只可用元数据定位，禁止素材内容级访问、导出、复制或显示真实路径。若发现新的真实用户数据泄漏面、需改产品文件、超出 allowed_paths 修治理问题或阶段 0 基线/祖先条件变化，停止并记录。

### 测试映射检查点（2026-11-12）

- ZCode 只读裁决见 `reports/TEST-MAPPING-ADJUDICATION-2026-11-12.md`（session `sess_8a2f7064-f80d-49a5-b96f-6d5ba20dd1ca`）；对应 CLI 和原始清单定位搜索见 `logs/test-mapping-adjudication-20261112.log`。裁决区分当前 Python Core/Avalonia 测试面与冻结 Legacy suites，并允许仅在 audit 路径增加 `.NET` runner。
- 对 `audit`、`doc`、`verification`、`archive` 文本做定向查找，只找到状态占位，没有 AUDIT-01–14 原始逐项定义。没有运行 probes、pytest、`.NET` 或其他专项测试；AUDIT-01–14 继续为 `NOT_TESTED`，Release Gate 继续 `BLOCKED`。
- 下一步先将“逐项清单缺失”交 ZCode 作范围裁决。未获裁决前不猜测 AUDIT-01–14 各自范围、不执行专项测试、不读取漫画图像内容。

### 测试执行边界检查点（2026-11-12）

- ZCode 后续裁决选定“证据采集与逐项判定解耦”：AUDIT-01–14 全部为 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`；可以继续 pytest/Core、probes、Avalonia `.NET`、适用 smoke 与 governance 的限定 suite 证据。详细裁决与 CLI 日志见 Task Canonical Evidence `TESTEXEC-1` / `TESTEXEC-LOG-1`。
- `smoke` 的当前架构范围为 `core,wire`；`packaged` 固定依赖旧 `apps/desktop/src-tauri`，与 `frontend/rust/desktop/npm-audit` 一并登记 `NOT_RUN-legacy`。
- `.NET` 使用 8 个测试 `.csproj` 分别 `dotnet test --no-restore`；TRX 写到仓外，仓库默认 `obj/bin` 只允许 ignored 派生物。每个项目执行前后 `git status --porcelain` 必须逐字节一致。8/8 项目 restore assets 已只读确认存在。不得使用 `--artifacts-path`、复制资产或 restore。
- 下一步：在 audit runner 中添加 `.NET` suite 并将 smoke 限定为 `core,wire`，实现提交后按 probes → pytest → `.NET` 8 项 → smoke → governance 执行；任何环境/状态偏差按具名阻断，不清理、不恢复。

### 段 B probes 检查点（2026-11-12）

- runner 实现固定在 `5ab8ae006580f4c3aab6d61ce180794921dc7641`；结果在 HEAD `5ab8ae006580f4c3aab6d61ce180794921dc7641` 生成，命令 `python audit/V1-FULL-AUDIT/tests/audit_runner.py probes`，EXIT 1，耗时 1.295s。原始输出与 JSON 见 Task Canonical Evidence `PROBES-LOG-1` / `PROBES-RESULT-1`。
- 隔离 probes 中，directory junction 发布越界和 nmbak 磁盘失败后的数据库变更/错误信息缺失两个观察待 ZCode 定级；`../` 备份路径写入预期被 `_managed_relative_path` 拒绝。详细解释边界见 `reports/PROBES-RESULT-SEGMENT-B.md`；没有修复或重跑。
- AUDIT-01–14 仍全部 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`。下一项运行根 `pytest`，保持 suite 结果与 AUDIT-NN 状态隔离；其后按已保存裁决执行 8 个 `.NET` 项目、smoke `core,wire`、governance。

### 段 B pytest 与 probes 分级检查点（2026-11-12）

- 根目录 `tests` 已通过 `python audit/V1-FULL-AUDIT/tests/audit_runner.py pytest` 执行一次，作为 Python Core 限定 suite 证据。子进程 argv、cwd、branch、生成 HEAD、UTC 起始时点、elapsed、完整输出和 EXIT 见 `logs/pytest-segment-b-20261112T081732598825Z.log` 及 `evidence/pytest-segment-b-20261112T081732598825Z.json`。生成 HEAD=`425bd0565134b36642c93922ebd80c648b97d627`，EXIT=1，3,519 passed / 16 failed / 10 skipped / 11 warnings，elapsed=288.543s。
- 16 项失败按观察分为 reader export hook 3 项、FEA11 v7 fixture 查询缺 `chapters.custom_rank` 1 项、plugin sandbox 12 项；未推断共同根因、未修复、未重跑。详见 `reports/PYTEST-RESULT-SEGMENT-B-2026-11-12.md`。10 个 skip 与 11 个 warning 的原因/类别也记在报告和完整日志中。
- suite 状态已更新，但不映射到 `AUDIT-01–14`；这些逐项仍为 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`。当前 pytest 结果不是 App/UI、真实 GUI、安装、升级/回退或 Release Gate 通过证据。
- ZCode 只读确认 probes 原有分级：`reports/PROBE-TRIAGE-SEGMENT-B-2026-11-12.md` 与 `logs/probe-triage-confirmation-20261112.log`。两项建议均为 Medium / High confidence；`../` 备份路径为 defense-verified。未独立复现；实现修复超出本 Task。
- 原始 pytest 数据和 ZCode 确认日志在证据提交 `40f47362894f2ea6dcd66d463a72328aad37bbc6` 固定；本恢复点文档随后单独提交并 pin 回 Task。
- 下一步按既有裁决逐一运行 8 个 `.NET` 测试项目（`--no-restore`，TRX 写到 workspace；每项前后 porcelain 必须逐字节一致）。如有不忽略的状态变化立即停止，不清理、不恢复。之后执行 smoke `core,wire` 与 governance；`frontend/rust/desktop/npm-audit/packaged` 继续 `NOT_RUN-legacy`，真实 GUI 继续 BLOCKED。

### 段 B Avalonia .NET TestHost 阻断检查点（2026-11-12）

- 已按裁决执行 `python audit/V1-FULL-AUDIT/tests/audit_runner.py dotnet`，覆盖 App、Appearance、ApplicationCore、CoreClient、DesignSystem、Host、PresentationAvalonia、ThemeEngine 8 个项目；生成时 HEAD=`da589416344b8254c9c1061f1d4e3dd61b3e7a93`，branch=`main`。8 个 runner 均 EXIT=1、TIMED_OUT=False，8/8 `status_identical=True`；逐项证据 JSON/log 固定在提交 `426a4fc5d5a551f04cf58979176baa4150351d5c`。
- 8 个 TRX 外部 workspace 只读 XML 计数均为 total/executed/passed/failed=0。TestHost 在 `SetParentProcessExitCallback` → `ProcessManager.OpenProcess` 抛 Win32Exception(5) 后退出，尚未发现或执行任何测试用例。ZCode 只读裁定状态为 `BLOCKED-TESTHOST-ACCESS`，保留原始 EXIT=1，不记产品测试失败、NOT_RUN 或 PASS；详见 `reports/DOTNET-RESULT-SEGMENT-B-2026-11-12.md` 和 `logs/dotnet-result-adjudication-20261112.log`。
- 对每项日志中的 `GIT_STATUS_BEFORE_HEX` 解码核对：porcelain 基线依次包含 0/2/4/6/8/10/12/14 条，只涉及审计目录中前序 runner 产物；8 组运行期间均字节不变。没有清理、恢复或修改源码。
- 不推断 Win32 错误的底层成因，也不提权、关闭安全控制、改 runner/测试参数或重跑绕过。TRX 留在 `G:/CODEX/New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT/dotnet/results-20261112T083119769139Z/`，按 resource manifest 保留，不复制进仓库。
- 按 ZCode 裁决，下一步继续 smoke `core,wire` 与 governance；`frontend/rust/desktop/npm-audit/packaged` 仍为 `NOT_RUN-legacy`，真实 GUI 仍 BLOCKED。所有 AUDIT-01–14 继续 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`，Release Gate 继续 BLOCKED。

### 段 B smoke `core,wire` 检查点（2026-11-12）

- 已运行一次 `python audit/V1-FULL-AUDIT/tests/audit_runner.py smoke`，argv 限定 `--only core,wire`。生成 HEAD=`2a7aed313f9673b327cfbb87dbbe2cfde1269037`，branch=`main`，EXIT=1，elapsed=1.783s；完整 runner log、report JSON 与 runner JSON 见 Task Canonical Evidence。
- 17 项检查中 10 PASS、7 FAIL；Wire 6/6 PASS，Core 4 PASS / 7 FAIL。frontend 与 packaged 显式 SKIP。ZCode 只读裁定 7 项 Core 失败为 `BLOCKED-SANDBOX-GRANT` 前置阻断及级联：`icacls` 无法授予当前解释器 `python.exe` AppContainer 访问；`CORE-AUDIT` 缺少 `hook_invoked` 是 hook 未能启动后的级联。保留程序 `FAIL` 和原始 EXIT=1，不能汇总为 suite PASS。详细报告：`reports/SMOKE-RESULT-SEGMENT-B-2026-11-12.md`。
- 核心安全拒绝/允许语义、timeout、Job Object 子进程树清理均为零证据；不能从 10 个限定 PASS 外推。`CORE-FAIL-CLOSED` PASS，仅证明授权失败时拒绝执行且 fail-closed。
- ZCode 没有发现可把这些失败独立归因到产品缺陷的证据；`icacls` 的底层错误码/环境原因未知。与 .NET TestHost Win32 error 5 不建立共同根因。
- 下一步按裁决运行最终 governance 并绑定审计 HEAD；Legacy 前端/Rust/npm-audit/packaged 仍 `NOT_RUN-legacy`，GUI 仍 BLOCKED。AUDIT-01–14 和 Release Gate 状态不变。

### 段 B governance suite 检查点（2026-11-12）

- `python audit/V1-FULL-AUDIT/tests/audit_runner.py governance` 已运行默认治理 check 一次，生成 HEAD=`3e0c960a482f5420666faec82d9c0f89e8396159`，branch=`main`，EXIT=0，elapsed=1.281s，3 条既有 warning。原始 log/JSON 固定在 evidence commit `1e9c15344`。
- 此 suite 仅执行默认 `check.ps1`；最后一笔 Task Canonical Evidence pinbackfill 后，仍须在最终 HEAD 执行 default + TaskPath `check.ps1`、`verify_pins.ps1`、`generate_api_inventory.py --check`。这些结果决定最终治理状态；当前 Task 和 Release Gate 未关闭。

### 段 B checkpoint Review 与补验（2026-11-12）

- ZCode fresh context 对 reviewed_head=`499a6b8e6eb293487abf391c46d00263230940ad` 给出 `PASS_FOR_CHECKPOINT`；Review 不是全审批准或 Task 关闭。完整 finding 摘要见 `reports/ZCODE-CHECKPOINT-REVIEW-SEGMENT-B-2026-11-12.md`。
- 原 Review 初始 R-1 为 `NOT_VERIFIED`；R-2/R-3 为 P3 Task 文案问题；R-4 是 probe 3 的非阻断 observation。原 Review 与 addendum 摘要分别见 `reports/ZCODE-CHECKPOINT-REVIEW-SEGMENT-B-2026-11-12.md` 和 `reports/ZCODE-CHECKPOINT-REVIEW-ADDENDUM-2026-11-12.md`。
- ZCode addendum 已关闭 R-1/R-2/R-3，R-4 保持 observation。R-1 补验由实现侧 Codex 在固定 reviewed_head 的 Git objects 上执行：37 个 diff 路径全部属于当时 `allowed_paths`；45 条 CANONICAL + 1 条 SOURCE_PIN 的 BLOB content SHA-256 全匹配且 `commit:path` 存在。ZCode 接受该日志为 closure evidence，但 actual 值未由 Reviewer 亲自重算。原始补验日志 `logs/review-checkpoint-recheck-20261112.log` EXIT 0；addendum 原始 CLI 记录 `logs/zcode-checkpoint-review-addendum-20261112.log` EXIT 0。
- 下一步：将 Review/addendum 原始日志与报告 pin 入 Task，重生成 Task ledger；随后在最终 pinbackfill HEAD 运行 governance default + TaskPath、18 pins、API inventory。完成门禁后，将固定交付 head 交给新的 ZCode 独立上下文作全审 review。AUDIT-01–14 仍因原始清单缺失保持阻断，Release Gate 仍为 BLOCKED。

### 段 B 最终 checkpoint Review（2026-11-12）

- ZCode 新独立上下文对 reviewed_head=`d9478939f2cee81104f18ea757d81cec71c36225` 给出 `PASS_FOR_CHECKPOINT`（0 P0 / 0 P1）；原始 CLI session/turn/trace 和完整回答见 `logs/zcode-final-audit-review-20261112.log`，摘要见 `reports/ZCODE-FINAL-CHECKPOINT-REVIEW-2026-11-12.md`。
- F-1/F-2 已按建议在 `logs/review-final-integrity-20261112.log` 补证：固定 `reviewed_head=d9478939f2cee81104f18ea757d81cec71c36225` 的 52/52 行 BLOB SHA-256 匹配、0 mismatch；两个 diff 区间共 36 个路径条目，全部在 allowed_paths；该日志生成于 HEAD `75e3aefb2c35c276086fad50ece70421a67fbb53`，EXIT 0。
- F-3 的四项治理门禁已在 `logs/final-governance-gates-20261112.log` 重新运行并完整落盘：generated HEAD=`b9b6c5801060370eb4171c30eb77a935800e2f6f`；default 与 TaskPath check 各 EXIT 0（各 3 warnings），18 pins EXIT 0（18/18），API inventory EXIT 0（1/79/6=86）。该日志生成前工作树 clean。
- 在 HEAD=`ac188dde54fed9bf8d0adc0f62bd25bb7adb8951` 又执行了完整复跑，并将输出、每项时点/EXIT 和 56 行当前 Task pin 逐项 blob 复算写入 `logs/postreview-final-verification-20261112.log`：default/TaskPath 各 EXIT 0（各 3 warnings），18 pins EXIT 0（18/18），API inventory EXIT 0（1/79/6=86），56/56 pin 无 mismatch；日志生成前工作树 clean。
- 原 ZCode Reviewer addendum 已将 F-1/F-2/F-3 全部 CLOSED、R-4 保持 observation；详见 `reports/ZCODE-FINAL-REVIEW-ADDENDUM-2026-11-12.md` 与原始 CLI log。addendum 提出的既有 Task pin 复算及 reviewed_head 到补证 HEAD 的路径集合跟进，已由 `logs/postaddendum-integrity-20261112.log` 覆盖：generated HEAD=`b17fead6d2cbbd2324ffb0a85096eb50448050ff`、reviewed_head=`d9478939f2cee81104f18ea757d81cec71c36225`，11/11 路径均 allowed、57/57 既有 pins 匹配、EXIT 0。后续 Task pinbackfill 与该 HEAD 的最终门禁结果见下方 2026-11-12 current-head checkpoint。

### ZCode current-head checkpoint 与补记（2026-11-12；范围恢复前的历史状态）

- ZCode fresh independent context 对 reviewed_head=`453327ff19ea012026b76d2e10cdcf2c93c58038` 给出 `PASS_FOR_CHECKPOINT`（0 P0 / 0 P1），session=`sess_210ecf7f-a2a3-4d81-a7df-f4f30596ea84`；报告和原始 JSON 分别见 `reports/ZCODE-CURRENT-HEAD-CHECKPOINT-REVIEW-2026-11-12.md`、`logs/zcode-current-head-checkpoint-review-20261112.log`。
- N-1 指出的状态/恢复文案滞后已更新；N-2 所需该 HEAD 四项门禁原始日志已写入 `logs/final-post-pinbackfill-gates-20261112.log` 并纳入 Task Canonical Evidence。N-1/N-2 均为 P3 finding，整改不改变原始限制；N-3/R-4 是 P4 observation。
- 该门禁日志 generated HEAD=`453327ff19ea012026b76d2e10cdcf2c93c58038`：default 与 TaskPath check 各 EXIT 0（各 3 warnings），18 pins EXIT 0（18/18），API inventory EXIT 0（1/79/6=86）；每项含 UTC 时点与完整输出。
- 当时 Task 继续 `in_progress`；AUDIT-01–14 被记为 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`。原始附件恢复后，该逐项状态被后续裁决更正为 `NOT_TESTED`；Release Gate 仍为 `BLOCKED`。pytest 的 16 个失败、.NET TestHost 与 smoke sandbox 阻断、未运行项目和真实 GUI/安装/升级回退缺口仍是有效证据限制。此 checkpoint 不等于全审完成、集成通过或 Task 关闭。

### 历史生命周期裁决更正与恢复点（2026-11-12；原始附件恢复前）

- ZCode 初次生命周期裁决曾建议 `closed_with_limitations`，但误把 Codex prompt 的选项描述归因给用户。更正裁决已明确撤回该授权论证和状态建议；初次报告仅作审计轨迹，标为 `SUPERSEDED`。
- 随后的更正裁决当时要求 Task 保持 `in_progress`，并等待对永久限制作具体取舍；其依据是原始专项清单缺失。
- 原始与更正裁决报告/CLI log 已列入 Canonical Evidence；见 `reports/ZCODE-LIFECYCLE-ADJUDICATION-2026-11-12.md`、`reports/ZCODE-LIFECYCLE-ADJUDICATION-CORRECTION-2026-11-12.md`。N-1/N-2 已闭合；产品测试失败、阻断与未验证限制保持原样。
- 后续对 Task 自身可达 Git 历史的定向搜索记录在 `logs/original-checklist-git-history-search-20261112.log`（generated HEAD=`5cb792e0966817bd642d173ab7db844b2dce092c`）：最早 Task blob `1248f2b8a` 只有通用 AC1–AC4 与 `AUDIT-00–14` 范围；`-SAUDIT-14`、`-S15项专项` 在 Task/audit 子树中未找到逐项定义。该日志已 pin 入 Task；只能说明当前仓库可达历史未保存该清单，不外推到仓外来源。

### 原始附件恢复与当前续审检查点（2026-11-12）

- 原始用户附件已恢复至 `source/ORIGINAL-USER-AUDIT-INSTRUCTIONS-2026-10-24.txt`，25,572 bytes；SHA-256=`3EA8E623AE7EC6E492385005828DC43368563A78E4A91C9CAF8BB75DBB399EAF`，raw worktree Git blob 与 HEAD blob 均为 `b775b8663c3827ed4a75d6b64ff2236b92151038`。恢复报告、两份恢复日志和原件均已纳入 Task Canonical Evidence。
- ZCode 原始范围恢复裁决的 CLI 外层记录：session=`sess_a2d20ca9-eaa7-49f8-95bf-2e67edbf8824`、turn=`turn_1a64fded-8e70-42b5-8f49-7fab16e23712`、trace=`422fc57e-18d3-48ef-927a-c580d3eed95a`、CLI EXIT=0。正文中的 ID 自述与外层 envelope 不一致，已在报告披露。ZCode 的 plan-mode shell 尝试被拦截，没有执行且无 shell EXIT；既有治理结果不是该会话重跑所得。
- 当前状态纠正为 AUDIT-00 limited PASS（只覆盖现有 baseline/source inventory）；AUDIT-01–14 全部 `NOT_TESTED`，不把 suite 结果外推为专项 PASS。Release Gate `BLOCKED`；Task `in_progress`；AC2/AC3/AC4 `PARTIAL`。原“等用户接受永久限制或重新提供清单”的分支终止，无需新的用户输入。
- 下一步按 ZCode 执行序列先补 AUDIT-00 的 `01_PROJECT_INVENTORY.md`，再做 AUDIT-01/02、suite 专项映射、AUDIT-11、AUDIT-08/05/06、AUDIT-14、合成验证和最终报告。实际 GUI、TestHost、sandbox grant、干净 Windows、真实付费 API 与私有漫画内容仍按各子项具名 `BLOCKED`/`NOT_RUN`；任何产品源码或超出 `allowed_paths` 的改动均停在新 Task 裁决。
- ZCode 裁决及阶段性门禁记录见 Task Canonical Evidence `ZCODE-ORIGINAL-SCOPE-ADJUDICATION-1`、`ZCODE-ORIGINAL-SCOPE-GATES-1`、`SCOPE-POSTCOMMIT-GATES-1`。此恢复检查点不等于全审通过、最终 Review 或 Task 关闭。

### AUDIT-00 静态项目盘点完成（2026-11-12）

- 报告 `reports/01_PROJECT_INVENTORY.md` 与命令日志 `logs/audit-00-inventory-20261112.log` 在 commit `943e4615afd34865818a1287461ac57188f430ca` 固定。日志 generated HEAD=`6f5153e47ff6adfcedde49712636c75e21bd43ef`；清单/接口/迁移/入口/model-pin 检查 EXIT 0；旧 `packaging/new_manga.spec` 在产品基线缺失的探测按预期 EXIT 128。
- AUDIT-00 状态更新为 `PASS`（静态盘点）；外部模型文件字节、构建、安装、真实 GUI 和运行时行为不在此 PASS 内。报告记录的陈旧打包说明/入口是待 AUDIT-02/12 复核的静态观察，未改产品文件。
- 当前下一步为 AUDIT-01/02 架构与静态扫描；AUDIT-01–14 仍为 `NOT_TESTED`，AC2/AC3/AC4 与 Release Gate 状态未变，Task 继续 `in_progress`。
