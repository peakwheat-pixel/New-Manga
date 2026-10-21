---
task: WORKSPACE-DECLARATION-REMEDIATION-1-REVIEW
reviewer: Codex
author: workspace-hardening
base_commit: f0f19596f
reviewed_head: 66e5972825db46b3f1565cc8fa37a69f8cc836b0
implementation_head: dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1
decision: changes_requested
review_mode: read_only
---

## 1. 结论（A–E）

**结论：`changes_requested`。** 冻结的审计 JSON 与日志支持 163 → 15 的结果，但实现仍有会跳过真实保护声明的 fail-closed 缺口，不能据此批准集成。

**A — 真实性：** `audit-before.json` / `audit-after.json` 与报告中的数字一致：declarations **1858→1855**、protected roots **1264→1262**、errors **163→15**、warnings **54→239**。错误分类也一致：`JSON_PARSE` 69→2、`DECL_BARE_NAME` 57→0、`DECL_UNKNOWN_DISPOSITION` 9→0、`DECL_RELATIVE_UNRESOLVED` 6→0、`DECL_DESTINATION_UNRESOLVED` 7→1、`FILE_UNREADABLE` 3→0。after 的 15 条与 [RESIDUAL.md](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/RESIDUAL.md:5>) 的 15 条按 code/file/locator 逐项对应，无漏报。

declarations 减少的 3 条分别是两条现存路径不存在的 prose 声明，以及一条 `NOT_APPLICABLE`；两条保护性声明均不存在为当前路径。因此这次 **2 个保护根减少对所审快照可解释**。但保护差异检查不能消除下面发现的通用路径误判风险。另有 6 条泛化 destination 从错误降为 `DECL_DESTINATION_GENERALIZED` warning，这属于实际错误分类变化，见 F-03。

**B — fail-closed：** 不通过。真实路径可能因 CJK/空格被跳过；malformed JSON 可以通过 instrumentation 文件名降为 warning；泛化 destination 也会被降级。严格 GB18030 fallback 还没有验证可被该编码解码的二进制或损坏输入。

**C — AC1–AC7：** AC1 数据齐全；AC2、AC3、AC5、AC6 存在未满足项；AC4 有未覆盖风险；AC7 的历史日志和冻结证据一致，但部分安全反例未测试，`run_evidence.py` 本轮未运行。

**D — 残余：** 15 条都应继续保留为错误，逐条裁定见第 4 节。6 条泛化根和 4 条 env 值都不应通过通用解析启发式降级。

**E — 边界与治理：** `f0f19596f..dca07bd3d` 仅改 `clean_workspace.py` 和本 Task 的 evidence 目录；`dca07bd3d..HEAD` 只新增 Handoff、更新 Task，均在 `allowed_paths` 内。交付 diff 无删除，也无历史 Task/旧 evidence 改动。Task 的 28 个证据行均 pin 到 evidence commit 且 SHA 正确，manifest 的 26 项也全部复算通过。Task frontmatter 与 Handoff 存在，但记录的 `check.ps1` 为 **exit 1（7 errors、3 warnings）**，所以完整治理门未通过。

本轮没有修改文件或执行 Git 写命令、push、GC、prune。目标 worktree 起始和结束均 clean；主仓现有 status 计数前后均为 1245，未见本轮新增变化。

## 2. Findings

### F-01 — P1：真实 path-like source / evidence path 被 prose 启发式跳过

[clean_workspace.py](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/tools/governance/clean_workspace.py:712>) 的 `is_descriptive_value()` 按 CJK 字符和空白词数判断叙述文本；`add_declaration()` / `add_evidence_pin()` 在解析身份前调用它。只读内存探针显示，合法但带空格或中文的路径（例如 `G:/CODEX/New Manga.workspace/temp/my real data`、`G:/CODEX/New Manga.workspace/temp/中文目录`、`数据/原稿`）可被判为 descriptive，成为 warning，**0 declarations、0 errors、无保护**。这违反 AC3“真实 path-like `PRESERVE_*` 失败仍 fatal”和 F-02。

**最小修正：** 只对明确的非路径占位符/纯 prose 跳过；一旦 `is_path_like()` 为真，就走路径解析并在无法解析时 fatal。增加含空格、CJK、不可解析路径的正反例。

### F-02 — P1：malformed JSON 可用 instrumentation 名称绕过 fatal

[clean_workspace.py](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/tools/governance/clean_workspace.py:1343>) 在 filename 匹配 `stdout|stderr|meta|trace|results|report|runner|probe|summary|output` 时，可把 JSON 解析失败降为 `JSON_NON_DECLARATION`。该规则也用于 tracked 文件。若真实声明文件被截断在声明 token 出现前，并被命名为 `*.stdout.json`，就既无 token、又匹配 instrumentation 名，因而只警告并继续。现有测试覆盖了 `.stdout.json` **含 token 时 fatal**，以及普通 tracked 文件 fatal，没有覆盖无 token 的 `.stdout.json`。

**最小修正：** 不以可变文件名单独给 tracked 文件免责；对可降级的 instrumentation 使用精确路径/来源白名单或显式登记，并加入“真声明文件改名 `.stdout.json`、截断在 token 之前”的反例。否则维持 fatal。

### F-03 — P1：path-like generalized destination 被降为 warning

`add_destination()` 将 `DECL_GENERALIZED` 转成 warning 并不登记保护，见 [clean_workspace.py](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/tools/governance/clean_workspace.py:977>)。只读内存探针中，独立 destination `G:/CODEX/New Manga.workspace/temp` 得到 0 errors、0 declarations。源行不一定独立保护该 destination；这也超出“只缩小什么算声明”的范围，并削弱 Task 明确保留的 F-03。after 的 6 条 `DECL_DESTINATION_GENERALIZED` warning 对应这类降级。

**最小修正：** 恢复 path-like generalized destination 的 fatal；若需允许特定 workspace root，另立 Task 冻结明确策略、范围和等价保护测试后再实现。

### F-04 — P1：近似资源表 schema 被跳过，而非 fatal

[clean_workspace.py](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/tools/governance/clean_workspace.py:1189>) 在 Resource Manifest 表含 `resource_type` 或 `source_path`、但缺少必要列时发出 warning 并跳过。比如有 `resource_type | source_path` 的真实表缺少 `disposition`，可能携带未登记保护路径。当前 malformed 测试只覆盖**完整 schema 下的错误行列数**，没有覆盖不完整 schema。Canonical Evidence 表的缺列也有类似跳过行为。

**最小修正：** 表头只要声明了资源/evidence 身份列但 schema 不完整，就按 malformed integrity error 处理；只有不声明这些字段的叙述表才 warning。为缺列和错误行列数都增加测试。

### F-05 — P2：GB18030 strict fallback 未证明能拒绝可解码的二进制/损坏文件

[read_text()](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/tools/governance/clean_workspace.py:287>) 对所有扫描文件都尝试严格 GB18030 解码。严格解码能拒绝部分坏字节，但某些非 UTF-8 二进制字节组合也能构成合法 GB18030 文本；这类文件会被接受并只产生 warning，若声明表被损坏或误解码，可能漏掉保护。现有反例仅验证“UTF-8 和 GB18030 均无法解码”，没有覆盖“非 UTF-8 但可按 GB18030 解码的二进制/损坏内容”。

**最小修正：** 将 fallback 限定到已知 legacy 来源，或加入足以拒绝二进制特征的规则与反例；不能仅凭 strict decoder 成功就把任意文件当作合法历史文本。

### F-06 — P2：`RESIDUAL.md` 缺少 AC6 要求的原始 message

Task AC6 明确要求 `RESIDUAL.md` 逐项含 `file/code/message/tracked/owner/...`，见 [Task AC6](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/doc/tasks/WORKSPACE-DECLARATION-REMEDIATION-1.md:66>)。但 [RESIDUAL.md 表头](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/RESIDUAL.md:5>) 没有 `message` 字段；部分 message 仅在 `triage-summary.json` 中。Handoff 声称 RESIDUAL 含 message，与文件不符。

**最小修正：** 在每条残余中加入审计原始 message，并重新冻结对应 evidence/pin。

### F-07 — P2：测试日志缺 shell 类型字段

[existing-tests.log](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/existing-tests.log:1>) 和 `new-tests.log` 含 command、CWD、EXIT_CODE、解释器路径，但没有 shell 类型。协作协议 §6.12 要求全仓/定向测试日志含 shell/venv 头及解释器路径；因此现有日志不满足完整格式要求。

**最小修正：** 记录实际父 shell 与 `subprocess` 是否使用 shell（本 runner 是直接启动，`shell=False`），更新日志与 pins。

### F-08 — P2：Handoff 的证据行数与 Task 不一致

Task 有 **28** 条 Canonical Evidence 行，均 pin 到 `dca07bd3d` 且 SHA 匹配；Handoff §6 却称 **27** 条。证据本身的 28 个 pin 均有效，26 行 manifest 也全部匹配，这是计数记录错误，不是 hash 错误。

**最小修正：** 修正 Handoff 的行数并同步其 evidence 引用。

## 3. AC1–AC7 判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 | **MET** | before JSON 为 163 errors；TRIAGE 有 163 行，按分类计数一致。 |
| AC2 | **FAIL** | BOM 处理代码存在，但无 BOM 测试；文件名启发式可让 malformed 声明 JSON 降级，见 F-02。 |
| AC3 | **FAIL** | 合法 path-like source/evidence 可被误判 prose，失去保护，见 F-01。 |
| AC4 | **PARTIAL** | GB18030 正反例覆盖了合法 legacy 文本和双编码失败，但没有覆盖可被 GB18030 解码的二进制/损坏文件，见 F-05。 |
| AC5 | **PARTIAL** | 英文精确 schema、叙述表跳过及完整 schema 下错误行列数 fatal 均有实现/测试；不完整声明表头仍会 warning 跳过，见 F-04。Frozen protection delta 只发现 3 条旧解析器声明差异，均为当前不存在的 prose 路径，未证明当前快照有真实中文表保护丢失。 |
| AC6 | **FAIL** | 15 条准确匹配 after 错误，但 `RESIDUAL.md` 缺少每条原始 message，见 F-06。 |
| AC7 | **PARTIAL** | 日志记录旧 80 tests `OK` / exit 0、新 14 tests `OK` / exit 0；两个 replay 均 15/15 REJECT、0 deleted、18/18 source。关键安全反例仍未覆盖；runner 本轮未运行。 |

## 4. 15 条残余逐条裁定建议

| # | 残余 | 建议 |
|---:|---|---|
| 1 | `TABLE_ROW_ARITY`：`GOV-DEBT-CLEANUP-2.md` | **保留 fatal。** 这是 7 列对 6 列的 malformed 历史资源表；只能由另一个明确授权的 Task 修复/补充记录，不能解析时跳过。 |
| 2 | `DECL_RELATIVE_AMBIGUOUS`：`P19.md:5` | **保留 fatal。** 用户/Task Owner 明确 repo-relative 或 workspace-relative 根后再解析。 |
| 3 | `DECL_ENV`：`P19.md:6`，`%TEMP%/p19-ac2-r1` | **保留 fatal，另立 Task 裁定。** 必须把目标绑定为具体规范路径；不允许全局忽略 `%TEMP%`。 |
| 4 | `DECL_ENV`：`P19.md:7`，`%TEMP%/p19-ac2-main-1` | **保留 fatal，另立 Task 裁定。** 同 #3，逐项确认目标，不按变量名整体豁免。 |
| 5 | `DECL_GENERALIZED`：`SEC-FIX-PATH-ECHO-1.md:5`，workspace root | **保留 fatal，另立策略 Task。** 将 root 缩到具体资源，或由用户/Codex 明确批准一种受控 root policy。 |
| 6 | `DECL_GENERALIZED`：`WORKSPACE-CONSOLIDATION-1.md:10`，`task-envs` root | **保留 fatal，另立策略 Task。** 在明确允许的根列表和保护语义落地前，不降级。 |
| 7 | `DECL_GENERALIZED`：`WORKSPACE-CONSOLIDATION-1.md:11`，workspace root | **保留 fatal，另立策略 Task。** 同 #6；不能默认把整个 workspace root 当作可忽略声明。 |
| 8 | `DECL_GENERALIZED`：`WORKSPACE-CONSOLIDATION-1.md:12`，`worktrees` root | **保留 fatal，另立策略 Task。** 需明确该根下所有后代是否均受保护。 |
| 9 | `DECL_GENERALIZED`：`WORKSPACE-CONSOLIDATION-1.md:14`，`review-scratch` root | **保留 fatal，另立策略 Task。** 需明确受保护范围和生命周期。 |
| 10 | `DECL_GENERALIZED`：`WORKSPACE-CONSOLIDATION-1.md:15`，`temp` root | **保留 fatal，另立策略 Task。** 需明确允许的根与保护含义，不能按目录名自动豁免。 |
| 11 | `JSON_PARSE`：untracked `run-baseline-20261014T0430CST-ac3fix.json` | **保留 fatal。** 修复为单一有效 JSON，或在有内容/来源证据时显式裁定为非声明文件。 |
| 12 | `JSON_PARSE`：tracked `run-baseline-20261014T0915CST-p02-admission-r2.json` | **保留 fatal。** 同 #11；不能依赖 instrumentation 文件名解除保护完整性错误。 |
| 13 | `DECL_DESTINATION_UNRESOLVED`：P19 destination 文本 `Same ignored target/dist locations in this worktree` | **保留 fatal，直到源数据明确标注。** 可由另一个授权 Task改为显式 prose/`NOT_APPLICABLE` 表达或修正为真实目标路径；不要用宽泛 path-like prose 启发式降级 F-03。 |
| 14 | `DECL_ENV`：`P19-UI-FIX-1/resource-manifest.json` 的 `%APPDATA%/...` | **保留 fatal，另立 Task 裁定。** 将其解析到具体用户/环境的规范路径并记录依据；不全局展开 `%APPDATA%`。 |
| 15 | `DECL_ENV`：同一 manifest 的第二条 `%APPDATA%/...` | **保留 fatal，另立 Task 裁定。** 与 #14 分别确认，不能以同类项为由合并或忽略。 |

6 条泛化声明实际为 **5 条来自 `WORKSPACE-CONSOLIDATION-1`、1 条来自 `SEC-FIX-PATH-ECHO-1`**。建议在独立 Task 中定义有限、显式授权的 root policy；在该策略获批并通过覆盖测试前，6 条均保留 fatal。4 条 env 声明同样应由独立 Task 逐项解析，不允许按 `%TEMP%` / `%APPDATA%` 类型整体降级。

## 5. 运行证据

| 只读命令/检查 | 结果 |
|---|---|
| `git -C <worktree> status --short --branch`（Review 开始与结束） | exit 0；目标 worktree clean |
| `git diff --name-status f0f19596f..dca07bd3d`、删除路径 diff | exit 0；仅解析器和本 Task evidence；删除列表为空 |
| `git diff --name-status dca07bd3d..HEAD` | exit 0；Task 与 Handoff 两个允许路径 |
| `python -B` 读取 Git blob 并复算 audit、15 条残余、28 条 Task pins、26 条 manifest | exit 0；残余逐项匹配，pin/manifest SHA 不匹配数均为 0 |
| 读取 `existing-tests.log`、`new-tests.log` | NOT_RUN（Review 未重跑测试）；冻结日志分别记录 80/80、14/14 `OK`，exit 0 |
| 读取两份 incident replay JSON | NOT_RUN（Review 未重跑 replay）；两份均记录 15 candidates / 15 rejected / 0 deleted / 18 sources |
| 真实仓库 `--audit-declarations` | NOT_RUN；按用户允许使用冻结的 JSON/log。冻结记录为 before 163 errors、after 15 errors，after exit 2 |
| `run_evidence.py` | **NOT_RUN**；脚本会写入 evidence 目录并重跑测试/replay/audit。冻结 `environment.json` 的 `failures` 为空，各子命令结果符合预期；Handoff 声称 runner exit 0，本轮未独立重执行 |
| `check.ps1 -TaskPath ...` | NOT_RUN；已读交付日志记录 exit 1、7 errors、3 warnings，尚非全绿 |

**建议下一步：** 由 Task Owner 在原 Task 范围内修复 F-01 至 F-04，补上 F-05 的输入边界测试，并补齐残余 message、日志 shell 字段及 Handoff 计数；重新冻结证据后以新 head 提交独立复审。