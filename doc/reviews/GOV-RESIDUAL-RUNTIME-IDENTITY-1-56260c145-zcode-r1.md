---
task_id: GOV-RESIDUAL-RUNTIME-IDENTITY-1
reviewer: zcode
author: dsh
base_commit: 43a7d73c850f669cc2595343a1747a661c277f2e
reviewed_head: 56260c1451da7b1e0d93fcc31a5782f6685da134
decision: changes_requested
---

# Review：GOV-RESIDUAL-RUNTIME-IDENTITY-1（r1，zcode）

审查日 2026-10-22；只读审查，未修改除本文件外的任何文件。Reviewer 未参与本 Task 任何实现。

## 范围与依据

- 范围：`43a7d73c8` → `56260c145`，共两个提交（`bb04c78d4` 交付 + `56260c145` 转 in_review/pin EV，经 reflog `.git/logs/HEAD:1713-1714` 确认 main 上无中间提交）。
- diff 全量（`git diff --stat base..head`）：12 个文件、+2716/−25，全部落在 Task `allowed_paths` 内（Task/Handoff/证据目录 7 文件 + STATUS/REBASELINE_PLAN/TASK_LEDGER 导航同步）。
- 禁止路径核验：`git diff --name-only base..head -- tools/governance/ doc/tasks/P19.md verification/ENV-BUNDLE-1-FU1/resource-manifest.json verification/P19-UI-FIX-1/resource-manifest.json` 输出为**空**——生产解析器、schema、例外表与三份历史原件零字节改动。工作树 tracked 修改 0（`git status --porcelain` 1246 行全为 `??`）。
- 审查环境披露：主会话 Bash 工具不可用（"No permission client configured"），独立复跑与哈希复核通过只读 Explore 子代理执行，命令限于本 Review 授权的只读清单（`--audit-declarations --out` 至 `G:/CODEX/New Manga.workspace/temp/GOV-RESIDUAL-RUNTIME-IDENTITY-1/zcode-review-r1-audit/`、SHA-256 计算、`git diff/show/status --check`、`check.ps1`、路径存在性检查）。解释器版本未记录（audit 输出与作者记录可比，不影响判读）。

## Architecture 结论

研究型交付，无产品代码变更。架构面结论良好：

1. **生产隔离成立**：`probe-protected.py` 经 `importlib` 加载生产 `clean_workspace.py`，`ProtectionIndex.finalize` 的 no-op 仅作用于加载后的模块对象（L25），不写生产文件（diff 空，字节级证实）；`finalize` 生产语义为「索引含任何 error 即 `fail()` 拒绝一切删除」（clean_workspace.py L1169-1174），no-op 只屏蔽最终中止闸门，不影响索引构建与 `evaluate` 的 same/descendant/ancestor 三关系判定（L1112-1133），故 hits 评估结论不被误导。
2. **证据体系设计正确**：`--audit-declarations` 为纯只读模式（`scan_repo_declarations` docstring 明示 Read-only；报告仅写 `--out` 目录；errors 时优雅 exit 2）；audit 产物双重落盘（workspace temp + 入库 raw）逐字节一致（含 `generated_at` 2026-10-22T09:15:18+08:00），互证无事后修饰。
3. **保护语义只增不减**：本 Task 交付新增 8 个保护根（1926→1934，均为 PRESERVE 类），未缩小既有集合；`r212` 禁令、五广域根、旧 pin 均未触碰。
4. 注意点（非缺陷）：在「Task 文档本身即声明源」的体系里，本 Task 自身 Resource Manifest 也进入被审计面并引入 2 个新 fatal（见 R-002）——这是该体系首次显式暴露自指效应，后续实施 Task 的断言口径必须处理。

## Verification 结论

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 禁止范围合规 | `git diff --stat/--name-only base..head`（含禁止路径过滤） | 56260c145 | **PASS**：12 文件全在 allowed_paths；tools/governance、P19.md、两份 manifest 零改动 | 本 Review 复跑原始输出（经只读子代理） |
| AC1 审计复现与七项身份 | `python -B tools/governance/clean_workspace.py --audit-declarations --out <workspace>/temp/GOV-RESIDUAL-RUNTIME-IDENTITY-1/zcode-review-r1-audit` | 活树 56260c145 | **PASS（带 R-002 口径说明）**：7 项目标错误的 code/message/file/locator 逐字复现，EXIT=2；活树计数 2636/1934/**9**/281，其中 2 个新错来自本 Task 自身文档（R-002）；Task 声称的 2627/1926/7/276 为 base 时点（Task 文件未入库）口径，与 `raw/audit-run.log`、`raw/declaration-audit.json`、workspace temp 副本三方一致，自洽成立 | 子代理复跑 stdout 全文；matrix.md/declaration-audit.json 逐项比对 |
| AC2 历史展开值来源 | 抽查 tracked 证据引用原文 | 56260c145 工作区 | **PASS**：`doc/tasks/WORKSPACE-CONSOLIDATION-1.md:167`（TEMP 证据 1）与 `verification/M2-AC5/raw/cleanstart-gate.json:9`（APPDATA 证据 1）引用逐字属实；`appdata-source-before.json` 3 条 + `appdata-source-preservation-check.json` 4 条 recorded SHA 与 `historical-env-evidence.json` 引用完全一致；当前环境值被明确标注「仅对照、不作证据」 | 本 Review Read 逐字比对 |
| AC2 字节交叉校验 | 独立 SHA-256 计算 4 个 AppData 文件 | 活树，2026-10-22 | **PASS**：`library.db`（311296B，`7809968c…`）、`run-owner.lock`（1B，`6e340b9c…`）、`.preview-lifecycle.lock`（325B，`c459db54…`）与历史记录**相等**；`catalog.sqlite`（24576B，`b16c8a30…`）≠ 记录 `0f094275…`——与 Task 声称的「3/4 相等、1 项 delta 已解释」**完全一致** | 子代理只读哈希计算原始输出 |
| AC3 存在性与归属 | 只读存在性检查（`os.path.exists`） | 活树 | **PASS**：`worktrees/P19-AC3-1`、`Temp/p19-ac2-r1`、`Temp/p19-ac2-main-1`、`Local/pyinstaller` 均 False；`APPDATA/…/managed` 为 True——与 `historical-env-evidence.json` existence_checks 及 matrix「其余五项无现存资源」一致；归属（P19 / ENV-BUNDLE-1-FU1 / P19-UI-FIX-1）与三份原件内容逐一对应 | 子代理复验输出；原件 Read 比对 |
| AC4 probe 只读性与结果 | 静态审查 probe-protected.py + 生产代码 + diff | 56260c145 | **PASS**：脚本除写自身 `raw/` 产物外无任何写操作；finalize no-op 影响面如 Architecture 节所述不误导结论；「唯一真实保护缺口 = `C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop`（目录及 catalog/data/derived hits=0、exists=true）」成立——`raw/protection-evaluation.json` 的评估逻辑经生产代码静态核实，且复跑确认两条 `%APPDATA%` 声明在活树仍因 DECL_ENV 被拒、未注册为保护根 | 本 Review 静态分析 + 子代理复跑 |
| AC4 运行记录真实性 | verification-log §4 与 raw 产物比对 | — | **FAIL → R-001**：日志 COUNTS 行（2627/1926/7/276）与其同段 WROTE 的 raw 产物（2636/1934/9/281）矛盾 | 见 Findings R-001 |
| AC5 矩阵结论 | 逐项复核 matrix.md 七项判定 | — | **PASS**：事实/技术可解/无用户裁决对象的判定均有上述独立复核支撑；E6/E7 locator 精度缺陷的说法经生产代码证实（JSON 声明 locator 固定拼在 disposition 字段路径，clean_workspace.py L1407-1429） | 本 Review 各项比对 |
| AC6 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1` 复跑 | 活树 | **PASS**：`Governance check: PASS (2 warnings)`、EXIT=0，两条 WARN（14 个非终态 Task、STATUS 80% 预算 2843B/29 行）与 verification-log §5 记录逐字一致；check.ps1 确认只读（唯一临时写为系统 Temp 自清理文件） | 子代理复跑输出全文 |
| AC6 空白检查 | `git diff --check` 与 `git diff --cached --check` | 活树 | **PASS**：均 EXIT=0 | 子代理复跑 |
| NOT_RUN 项如实性 | 产品测试套件 / `--apply` | — | **符合预期**：本 Task 无产品代码变更，NOT_RUN 登记如实；未发现把 NOT_RUN 写成 PASS 的情况 | verification-log §6 |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-001 | P1 | `verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/verification-log.txt:76-77`（COUNTS 行）vs `raw/protection-evaluation.json:2-16` | verification-log §4 把 probe 运行的 COUNTS 记为 `2627/1926/7/276`，但同一代码块随后 `WROTE` 的 `raw/protection-evaluation.json` 实际 counts 为 `2636/1934/9/281`。probe-protected.py 单次运行中 stdout COUNTS 与写盘 payload 同源于 `index.counts()`（L29/L75-95），不可能输出两组数字——日志把 Task 文件入库前另一次运行的计数呈现为与 WROTE 同次的连续输出，违反其自身第 10 行「每条命令均实际运行」的记录声明。影响 AC4 证据记录真实性；核心结论（APPDATA hits=0）不受影响（raw 产物未被修饰，且在含更多保护根的 1934 根索引下 hits=0 蕴含任何子集索引下同样 hits=0） | 本 Review 独立复跑在活树得 2636/1934/9/281、EXIT=2，与 raw 产物 counts 完全一致，证明该次 WROTE 运行的索引状态即活树（Task 文件已入库）；2627/7 只能对应入库前的另一次运行 | 作者在 Task「交付与运行记录」或 Handoff **追加勘误段**（不改已 pin 的 EV-05/EV-07 字节）：如实说明 probe 实际运行次数与时点、§4 COUNTS 行的真实来源；r2 复审确认。禁止改写已入库日志正文掩盖矛盾 | open |
| R-002 | P2 | `doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-1.md:109`（`refs/heads/main` 行）、`:111`（`Temp/p19*（11 个现存目录…）` 行） | 交付自身的 Resource Manifest 引入 2 个新 fatal 声明错误（`DECL_RELATIVE_UNRESOLVED refs/heads/main` + `DECL_GLOB …p19*…`），使 main 活树声明错误基数 7→9（本 Review 复跑证实）。Task/Handoff/matrix/verification-log 均未披露该自指影响；后续实施 Task 若在活树以「7 errors」为精确断言将失真（须回退 base 口径或区分错误来源）。注：`raw/protection-evaluation.json` 如实保留了 9 errors（未修饰，正分） | 本 Review 复跑输出前两行 ERROR 即本 Task 文件；`raw/protection-evaluation.json:17-29` 同记 | 在 closeout 或后续实施 Task 冻结断言口径：区分「7 项历史错误（base 口径）」与「活树 9 项（含本 Task 2 项）」；本 Task 文档两行是否改写由实施 Task 一并裁定（本 Task 已 pin，不宜动） | open |
| R-003 | P2 | `doc/STATUS.md:7`、`doc/REBASELINE_PLAN.md:9`、`doc/TASK_LEDGER.md:42` | `56260c145` 将 Task frontmatter 转为 `in_review` 但未同步三份权威导航（三处仍 `in_progress`），权威指针与 Task 文件状态不一致 | 三文件当前字节 Read；`git show 56260c145:doc/tasks/…` L6 为 `status: in_review` | Review 后集成/closeout 流程中统一同步三处状态 | open |

## 结论与复审

**decision: changes_requested。**

核心研究结论全部经独立复核成立：七项错误身份逐字复现；`%TEMP%`/`%APPDATA%` 历史展开值的 tracked 证据与 4 项 SHA-256 交叉校验全部属实（含 1 项如实登记的 delta）；「唯一真实保护缺口 = `C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop`（用户数据，hits=0）」「其余五项无现存资源/无缺口」「无一项需用户裁决、七项均技术可解」的判定均有证据支撑；禁止范围字节级零违规；真实资源操作 0/0/0 与 git 证据一致；NOT_RUN 项如实登记。

但 R-001（P1，verification-log §4 运行记录与 raw 产物矛盾）未解决，按 Review 批准门槛不可 approved。R-001 属证据记录层面而非结论层面，处置成本低（追加勘误，不动已 pin 字节）；R-002/R-003 一并处置后交 r2。

**复审要求（r2）**：
1. R-001 勘误追加到位（说明 probe 运行次数/时点/COUNTS 行来源），EV-05/EV-07 字节不变；
2. R-002 以 closeout 记录或实施 Task 口径条款处置；
3. R-003 三处导航同步；
4. r2 仅复审上述处置，不重开已核实的取证结论。
