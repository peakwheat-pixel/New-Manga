---
task_id: FEA-15-PIN-BASIS-ENFORCE-1
adjudicator: ZCode CLI 0.17.1 independent adjudication session（与 AC2/AC3 Review session `sess_6b151e7e-8133-4b6a-ae6f-3c47296e5b7a`、AC1d session `sess_fd863071-c665-4b61-89be-2156ace80595` 均不同）
session: sess_dbdb62fe-a206-4477-a209-657882bae35b
decision_turn: turn_842ced10-318d-498e-836c-ca44d987f990
reviewed_head: 5e216dc53102ff93db39124b97ab85d88f18643b
base_commit: bfae0b9bd6a9b85a9a546d2adda0b684783ddb24
main_head_at_decision: 3407550370f97967c828f25dec9d716e154685e0
review_reference: doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac2-ac3-zcode-review-2026-11-12.md
decision: AC2/AC3 ACCEPT_WITH_LIMITATIONS；Review-R-001 DEFERRED（AC5 集成前置）；R-002…R-006 non-blocking；P3-6 撤回确认；R-007 修复确认；AC4 RELEASED（限定范围）；AC5 NOT RELEASED
scope: AC2/AC3 增量裁决；不构成 AC5 最终 Task adjudication，不使 Task 进入 done，不批准集成
---

# FEA-15-PIN-BASIS-ENFORCE-1 AC2/AC3 增量裁决（2026-11-12）

## 0. 裁决性质与身份声明

本报告是 **AC2/AC3 的增量 adjudication**，不是 AC5 最终 Task adjudication。它处置 AC2/AC3 Review 的结论与 findings、决定 AC2/AC3 的接受状态、处置 R-001…R-007，并释放（限定范围的）AC4；它不批准集成、不关闭 Task、不处置释放裁决保留项 R-001（见 §4.8）。

裁决者为本 adjudication session，未参与实现、返修或该 Review。本报告落盘时 session/turn ID 已在 frontmatter 登记为真实值（`sess_dbdb62fe-a206-4477-a209-657882bae35b` / `turn_842ced10-318d-498e-836c-ca44d987f990`）；不得在任何副本中回退为占位符或编造值。

## 1. 裁决输入核实（只读）

| 项 | 核实结果 |
|---|---|
| main HEAD | `3407550370f97967c828f25dec9d716e154685e0`（`git rev-parse main` 逐位一致）；工作树 `git status --porcelain` 为空，clean |
| 实现分支 | `codex/fea-15-pin-basis-enforce-1` HEAD `5e216dc53102ff93db39124b97ab85d88f18643b`（`test(governance): respect status fixture byte budget`）；该 HEAD 仅在此分支，不在 main/origin/main |
| 基线 R0 | `bfae0b9bd6a9b85a9a546d2adda0b684783ddb24` 在 main 与实现分支上均可达 |
| 实现范围 | R0→`5e216dc…` diff 恰为 4 文件、+433/−27、2 commits（`fd8436021` → `5e216dc53`）：`doc/templates/TASK.md`、`tools/governance/check.ps1`、`tools/governance/tests/test_architecture_assertions.py`、`tools/governance/tests/test_canonical_evidence_basis.py`（新增）——全部在 frontmatter `allowed_paths` 内，无越界 |
| Review | decision `approved` / 正文 `APPROVED_WITH_LIMITATIONS`，0×P0、0×P1，1×P2 + 6×P3，AC2/AC3 `PASS`（限已释放范围），AC4/AC5 NOT_RUN |
| 日志抽查 | 8 份 ac2ac3 日志逐份读取，GENERATED_HEAD、环境、计数、EXIT 与 Review/README 表述一致（明细见 §2 各行） |

## 2. Decision（结果）

1. **AC2：`ACCEPT_WITH_LIMITATIONS`，在已释放范围内判定 `<<MET>>`**。
2. **AC3：`ACCEPT_WITH_LIMITATIONS`，在已释放范围内判定 `<<MET>>`**。
3. **接受三项已记录 limitation**（均不得改写为 PASS，详见 §3）：
   - full governance suite 在 validation HEAD `a2a3401…`（`core.autocrlf=false`）为 56 passed / 2 skipped / 3 failed / EXIT=1；3 failures 全部位于 `test_residual_runtime_identity.py`，伴随 169 个 `TABLE_DELIMITER` errors（首例 `doc/tasks/CHAPTER-SELECTOR-1.md`）；同三失败在未变更基线 `dd637242…` 同配置原样复现（3 failed / 9 passed / EXIT=1）。既有基线限制，非本 Task 引入。
   - false checkout（`core.autocrlf=false`）下 `verify_pins.ps1` `EXIT=1`，C04b/C17 EOL mismatch；同两 mismatch 在未变更基线 `dd637242…` 同配置复现；main true checkout（`core.autocrlf=true`）18/18 `EXIT=0`。既有 EOL 限制。
   - focused basis suite 在 `core.autocrlf=false` 侧 11 passed / 2 skipped（两个需 blob/worktree 字节差异的用例在该 checkout 下前提不成立）；其覆盖由 `core.autocrlf=true` 侧 implementation HEAD 13 passed 补齐，两环境口径互补、均有日志。
4. **Review-R-001（P2，额外负例覆盖）：`DEFERRED`，不阻塞 AC2/AC3 接受；但列为 AC5 集成前置条件**（AC4 不受阻），详见 §4.1。
5. **R-002…R-006：接受为 non-blocking informational**，登记为后续改进候选，不构成本 Task 义务，详见 §4.2–§4.6。
6. **P3-6：撤回确认**（§4.7）；**R-007：修复确认 @ `06432c1fb…`**（§4.8 前段）。
7. **AC4：现在释放**，精确范围与停止条件见 §5。
8. **AC5：明确未释放**（§6）。

## 3. AC2/AC3 最终裁决依据

- **AC2（模板七列 + checker 新旧识别与 basis 校验）**：Review 确认模板新增七列且默认 BLOB 说明清晰、checker 区分 legacy 六列与新七列、旧六列保留 r194 语义、新 basis 校验按 BLOB/WORKTREE/EXTERNAL_SHA256 声明来源执行并 fail-closed、EXTERNAL_SHA256 不可读不通过。实现 diff 严格限于 4 个已释放文件。判定 **MET（限已释放范围）**。
- **AC3（判别测试覆盖）**：AC3 字面清单（旧格式、basis 缺失/非法、三类来源、commit 不含路径、缺失路径、PNG exact bytes、CRLF 与 mixed-EOL、旧格式结果不变断言）由 `test_canonical_evidence_basis.py`（+298 行）专项覆盖，并在两种 EOL 环境实测：implementation HEAD `5e216dc…` `core.autocrlf=true` 13 passed/EXIT=0（行使 blob/worktree 字节相异的 legacy 备选路径）；validation HEAD `a2a3401…` `core.autocrlf=false` 11 passed/2 skipped/EXIT=0；architecture fixtures 31 passed/43 subtests/EXIT=0。判定 **MET（限已释放范围）**。
- **limitations 的接受理由**：三项限制均有未变更基线 `dd637242…` 同配置复现或明确的环境前提解释，本实现未触碰 `clean_workspace.py`、历史 Task、18 frozen pins、`.gitattributes`；把它们登记为 limitation 而非缺陷，符合「失败不得改写为 PASS」的纪律。
- 附注（精确化，非纠错）：post-review gates 日志 `ac2ac3-post-review-gates.log` 的 GENERATED_HEAD 为 `3e05096b…`（Review 报告入库提交），该日志随后以 `340755037`（`docs(verification): record post-review AC2 AC3 gates`）入库；当前 main HEAD 为 `340755037`。四项 gates（default/TaskPath 各 EXIT=0 各 3 warnings；pins 18/18 EXIT=0；API 1/79/6=86 EXIT=0）的执行 HEAD 以日志记录为准。

## 4. Findings 逐项处置

### 4.1 R-001（P2）——额外负例覆盖：`DEFERRED`，转为 AC5 集成前置条件

Reviewer 判定其不阻塞 AC3 字面清单，本裁决维持不阻塞 **AC2/AC3 接受与 AC4 释放**；但为防止后续重构弱化 fail-closed 边界，处置为：**AC5 集成提交合入 main 之前必须落地并通过**以下四类负例测试（载体 `tools/governance/tests/test_canonical_evidence_basis.py`，属已释放 `tools/governance/tests/**` 范围）：

1. 新七列表行 arity 非法（列数不足/超出）；
2. 非法 SHA（非 64 位十六进制）；
3. 无效 BLOB commit（commit 不存在，或 commit 存在但不含该路径）；
4. basis 与路径方向错误（WORKTREE 指向仓外路径、EXTERNAL_SHA256 指向仓内路径）。

落地时机由 Owner 自选：可并入 AC4 证据提交，或 AC5 前单独提交；AC5 集成门禁须核验其存在且通过。本裁决不关闭它，其最终闭合在 AC5 终裁确认。

### 4.2 R-002（P3）`Get-GitBlobSha256` stdout/stderr 串行读取理论死锁——non-blocking，informational。接受登记；后续治理工具 Task 可顺手改为并行读取或加超时；本 Task 不处理。

### 4.3 R-003（P3）`$repoRoot` 隐式作用域引用——non-blocking，informational。接受登记；后续重构时显式传参；本 Task 不处理。

### 4.4 R-004（P3）词法路径判断不追踪符号链接最终目标——non-blocking，informational。接受登记；可作为后续 Task（仿 Resource Manifest 拒绝符号链接）；本 Task 不处理。

### 4.5 R-005（P3）WORKTREE basis 不校验 `commit` 列——non-blocking，informational。接受登记；后续可要求该列为空或占位；本 Task 不处理。

### 4.6 R-006（P3）Canonical Evidence 段缺失/无行时错误数膨胀且首条文案略有误导——non-blocking，informational。接受登记；拒绝方向正确；后续可优化报错条件；本 Task 不处理。

### 4.7 P3-6——撤回确认

同一 Review session follow-up turn `turn_ade3c4aa-…` 的撤回**确认有效**：目标运行时 PowerShell 7.6.9 属 7.4+，native stdout 重定向到文件保留原始字节（Microsoft Learn `about_Redirection`），首轮「旧表达式损坏二进制 blob 哈希」及派生表述不成立，从有效 findings 中移除；有效集合为 1×P2 + 6×P3，不影响 `APPROVED_WITH_LIMITATIONS` 结论。撤回记录与来源链接已按原字节保留在 Review 报告，视为诚实复核的正例。

### 4.8 R-007 与释放裁决 R-001 的区分（防混淆）

- **R-007（README hash typo）**：确认已在 main `06432c1fb94b7fe8a81c575a27076868a448a074` 修复（`docs(verification): correct AC2 implementation commit hash`），closed/fixed。
- **释放裁决 R-001（`…-zcode-release-adjudication-2026-11-11.md` 第 22 行）**：「R-001 不因实现自动关闭，须由最终 Integrator 据证据明确裁定；仓内新证据 BLOB pin 指向包含文件的实际 commit；仓外资源保留并按清单核验，不清理。」这是与 §4.1 Review-R-001 **不同的另一条保留裁决项**。本裁决**不关闭**它：它仍开放，留给 AC5 最终 Integrator adjudication 显式裁定。Task 卡「`R-001` 不因实现自动关闭」的表述即指此项，与本报告 §4.1 互不覆盖。

## 5. AC4：RELEASED（精确范围）

**释放决定**：AC2/AC3 已接受且其前置（AC1d `AC1D_PASS`、独立 Review `APPROVED_WITH_LIMITATIONS`、本裁决）齐备，AC4 现在释放，Owner=codex，在指定 workspace 隔离副本执行。

**范围（全部要素）**：

1. **载体**：两个新 fresh clone（`git clone --no-checkout`，checkout 前写 clone-local 配置，参照 AC1c B 先例并在日志记录 `.git/config` 写入时间先于 checkout reflog 时间）：
   - clone-T：`core.autocrlf=true`、`core.longpaths=true`；
   - clone-F：`core.autocrlf=false`、`core.longpaths=true`；
   - 两侧检出于同一固定候选 HEAD：validation HEAD `a2a3401eb703c3ae7899375755c981eabbf47572`；若按 §4.1 追加 R-001 负例测试提交，则以追加后的最新候选 HEAD 为准，两侧同 HEAD，并在证据中记录全部相关 HEAD。
2. **候选 gate 与测试（两侧同跑，逐项记录 UTC 时间戳、HEAD、EXIT）**：
   - `pwsh -NoProfile -File tools/governance/check.ps1`（default）；
   - `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md`；
   - `pwsh -NoProfile -File tools/governance/verify_pins.ps1`（记录逐 pin 结果与任何 EOL mismatch）；
   - `python tools/generate_api_inventory.py --check`；
   - `python -m pytest tools/governance/tests/test_canonical_evidence_basis.py -q`（EOL 敏感面核心；两侧行为互补属预期：true 侧 13 passed / false 侧 11 passed+2 skipped 的既有口径）。
   - full suite 与 architecture suite 为可选记录项：若运行，失败须对照 `dd637242…` 基线口径如实登记，不得改写。
3. **逐行对照**：
   - **历史行不变性**：`git diff --name-status bfae0b9… <候选HEAD>` 全集必须恰为本 Task 已释放增量文件集合（含 R-001 负例测试文件如追加，亦在已释放范围）；出现任何集合外增删即触发停止条件。
   - **本 Task 新行增量**：对增量文件逐一比较两种 checkout 的工作树字节；所有字节差异必须可由 `core.autocrlf` 设置完整解释（CRLF/LF 转换对）；无法解释的字节差异即触发停止条件。
4. **EOL pin mismatch**：clone-F 侧预期仅 C04b/C17 mismatch（与 `dd637242…` 基线集合一致），如实记录为 FAIL/limitation；不得为消除 mismatch 修改任何 pin。
5. **Linux**：默认 `NOT_RUN` 如实记录；仅当存在真实可用 Linux 环境且不拖累主线时才实测，否则不测、不声明。
6. **禁止事项**：不修改 `.gitattributes`、18 frozen pins、`tools/governance/verify_pins.ps1`、历史 Task/Review/Handoff/checkpoint/evidence 字节；不做 renormalize 及 dry-run；不实施 AC5 集成；不做最终 Task close；不执行资源清理/prune/GC/repack；不 push。
7. **停止条件（任一命中即停，保留现场并回报裁决）**：
   - 任何未解释的历史行变化或文件集合增删；
   - 任何超出已记录基线集合（C04b/C17）的新 EOL pin mismatch 或新失败；
   - 任何无法由 autocrlf 设置解释的字节差异。

**证据**：全部日志与对照矩阵入 `verification/FEA-15-PIN-BASIS-ENFORCE-1/`（建议 `ac4-*.log` 命名），按卡片分离提交；README 增补 AC4 段落。

## 6. AC5：NOT RELEASED

AC5（集成后 default/本卡/四个历史 TaskPath、18 pins、API 全量实跑、Handoff/Canonical Evidence/资源清单更新、fresh ZCode 独立 Review 与不同 session 最终 adjudication、Release-R-001 由最终 Integrator 显式裁决、Task 生命周期收口）**明确未释放**。其前置为 AC4 完成且结果经处置、§4.1 Review-R-001 负例测试落地。本裁决不批准任何集成提交、不使 Task 进入 done、不构成最终 Task adjudication。

## 7. 推荐下一步

1. **（Codex）** 落盘本裁决至 `doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac2-ac3-adjudication-2026-11-12.md`，填入真实 session/turn ID 后提交（docs commit）。
2. **（Codex）** 更新 Task 卡：AC2/AC3 勾选并标注 `<<MET>>`（附本裁决与三项 limitation 引用）；AC4 状态改为已释放待执行；登记 Review-R-001 处置与 §4.8 双 R-001 区分；刷新 rolling checkpoint 与 Canonical Evidence 行（本 Task 保持六列旧格式）。
3. **（Codex）** 按 §5 执行 AC4 跨 checkout 对照，证据按卡片分离提交。
4. **（Codex）** 在 AC5 集成前落地 §4.1 四类负例测试（可并入步骤 3 提交）。
5. **AC4 证据入库后**：由新的独立 ZCode session 处置 AC4 结果并决定是否释放 AC5；AC5 集成与终裁不在本轮授权内。

可直接转发的指令：

```
任务：FEA-15-PIN-BASIS-ENFORCE-1 AC2/AC3 增量裁决已下（ACCEPT_WITH_LIMITATIONS，AC2/AC3 MET 限已释放范围；R-001 DEFERRED 为 AC5 集成前置；AC4 已释放）。请依次执行：
1) 将裁决报告原文保存为 doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac2-ac3-adjudication-2026-11-12.md，填入真实 adjudicator session/turn ID 后提交；
2) 更新 Task 卡 doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md：AC2/AC3 勾选 <<MET>> 并引用该裁决与三项 limitation；AC4 改为已释放待执行；登记 R-001 处置与双 R-001 区分；刷新 rolling checkpoint；
3) 按裁决 §5 在 workspace 新建 clone-T（autocrlf=true）/clone-F（autocrlf=false）于候选 HEAD a2a3401eb703c3ae7899375c981eabbf47572（如追加负例测试则以最新候选 HEAD），两侧运行 check default/TaskPath、verify_pins、API、focused basis suite，逐项记录 HEAD/UTC/EXIT；逐行核对历史行不变性与新行增量，所有字节差异须可由 autocrlf 解释；预期 false 侧仅 C04b/C17 mismatch；任何集合外增删/新 mismatch/未解释差异即停止回报；Linux 记 NOT_RUN；不改 .gitattributes/pins/verify_pins.ps1/历史字节，不集成、不 close、不 push；证据入 verification/FEA-15-PIN-BASIS-ENFORCE-1/；
4) 在 AC5 集成前于 tools/governance/tests/test_canonical_evidence_basis.py 落地四类负例测试（行 arity/非法 SHA/无效 BLOB commit/basis 路径方向错误）；
5) 完成后停：AC4 结果交新的独立 ZCode session 处置；AC5 未释放。
```

## 8. 诚实性边界

- 本裁决全程只读：未改文件、未提交、未 push；git 核验仅用 `rev-parse`/`status`/`log`/`branch --contains`/`diff --stat` 等只读命令。
- 三项 limitation、false-checkout mismatch、AC4/AC5 NOT_RUN 均保持原状态；任何后续文档不得将其改写为 PASS。
- session/turn ID 已按落盘授权登记为真实值（frontmatter：`sess_dbdb62fe-a206-4477-a209-657882bae35b` / `turn_842ced10-318d-498e-836c-ca44d987f990`）；伪造、篡改或回退为占位符均视为证据缺陷。

## Addendum A（2026-11-12）：AC4 §5 核验口径澄清

本 Addendum 隶属于同日 AC2/AC3 增量裁决（session `sess_dbdb62fe-a206-4477-a209-657882bae35b`，decision turn `turn_842ced10-318d-498e-836c-ca44d987f990`；本 Addendum turn `turn_6d382ad1-4b0b-4bb8-b954-1e605a897078`）。它**不改变**主裁决任何 Decision（AC2/AC3 `ACCEPT_WITH_LIMITATIONS`、R-001…R-007 处置、AC4 RELEASED、AC5 NOT RELEASED 均不变），仅消除 §5 执行前的三处口径歧义。与主裁决冲突之处以本 Addendum 为准。

### A.1 文件级对照的判定依据与允许集（澄清 §5.3 第 1 项）

§5.3 原文「全集必须恰为本 Task 已释放增量文件集合」澄清为：对照 `git diff --name-status bfae0b9bd6a9b85a9a546d2adda0b684783ddb24..<候选HEAD>` 的路径全集必须**精确等于下列 11 个路径**（已逐一核验：R0→`dd6372420a459cdc9a4c39377f663f1b5d0d8646` 的 main 前进 7 项 + 实现 overlay 4 项）：

Main 前进（R0→dd637242，7 项）：
1. `doc/reviews/FEA-15-PIN-BASIS-ENFORCE-1-ac1d-baseline-confirmation-2026-11-12.md`（A）
2. `doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md`（M）
3. `verification/FEA-15-PIN-BASIS-ENFORCE-1/README.md`（M）
4. `verification/FEA-15-PIN-BASIS-ENFORCE-1/ac1c-b-r0-assertions-taskpath-bfae0b9.log`（A）
5. `verification/FEA-15-PIN-BASIS-ENFORCE-1/ac1d-canonical-evidence-blob-audit-0851085.log`（A）
6. `verification/FEA-15-PIN-BASIS-ENFORCE-1/post-ac1d-pinbackfill-gates-d362d228.log`（A）
7. `verification/FEA-15-PIN-BASIS-ENFORCE-1/r0-main-gates-bfae0b9.log`（A）

实现 overlay（dd637242→候选，cherry-pick，4 项）：
8. `doc/templates/TASK.md`
9. `tools/governance/check.ps1`
10. `tools/governance/tests/test_architecture_assertions.py`
11. `tools/governance/tests/test_canonical_evidence_basis.py`

判定依据：全部 11 路径均落在 Task frontmatter `allowed_paths` 内，且每一项要么是 main 上已授权入库的 AC1d/AC1c B Task-local 治理文档与日志（本 Task 生命周期产物），要么是已 Review 的实现文件。**接受全部 11 个现有路径为 AC4 允许集**；原 §5.3 表述中「增量文件集合」指此集合，而非仅 4 个代码文件。

- 后续 Task 卡更新：AC4 期间 **main 侧**的 Task 卡/checkpoint/STATUS 更新是正常生命周期文档义务，**不参与**候选 HEAD 的 diff 对照（对照发生在冻结候选 HEAD 上）；两 fresh clone 检出后为 clean 冻结态，**禁止**在 clone 内修改任何文件（含 Task 卡）后再跑对照。
- 若按主裁决 §4.1 追加 R-001 负例测试且落在同一 `tools/governance/tests/test_canonical_evidence_basis.py` 路径：允许集**不变**（仍为上述 11 路径，第 11 项内容更新）；若新 HEAD 的 diff 出现任何第 12 个路径或上述路径的状态变化无法归因（如出现 D 状态），触发停止条件。

### A.2 「逐行」对照的义务定义（澄清 §5.3 第 2 项）

Task 卡 AC4 原文「逐行区分历史行不变性与 Task 自身新行增量」指的是 **pin/evidence row inventory 的行级对照**，不是文件名状态 diff；§5.3 原表述只覆盖了文件级，本 Addendum 将行级对照补为 AC4 的**必做义务**，与文件级（A.1）和文件字节级（原 §5.3 第 2 项，工作树字节差异须可由 `core.autocrlf` 解释）三层并行：

1. **必跑命令与产物**（全部记录 UTC、clone 路径、HEAD、EXIT 与输出 SHA-256）：
   - 在保留的 R0 clone（`bfae0b9…`，clean，`core.autocrlf=false`）生成 **R0 基准 inventory**；
   - 在 clone-T 与 clone-F 各自候选 HEAD 生成 **候选 inventory ×2**；
   - 用 frozen delta generator 生成两份行级 delta：R0→clone-T、R0→clone-F（输出建议 `ac4-inventory-delta-r0-to-<head>-{t,f}.json`）。
2. **行级判定**：
   - **历史行**＝R0 基准 inventory 中已存在的行；**本 Task 新行**＝候选 inventory 相对 R0 的 ADDED 行。
   - 历史行不变性：clone-F（与 R0 同为 autocrlf=false）历史行 identity 与 sha 逐行不变；clone-T（autocrlf=true）历史行允许且仅允许 EOL 引起的哈希差异，且每条差异行经 CRLF→LF 归一化后与 R0 对应行逐字节相等（AC1d 的 146,220 CRLF pairs 归一化先例为口径依据）。
   - 新行归因：两份 delta 的全部 ADDED/CHANGED/REMOVED 行必须逐行归因于 A.1 允许集内的文件；REMOVED≠0 即触发人工归因，无法归因即停止。
3. **frozen generator 的允许调用方式**：
   - 冻结 wrapper `verification/FEA-15-PIN-BASIS-ENFORCE-1/capture_pin_basis_baseline.py`（SOURCE_PIN，SHA-256 `e4300b7bdbca9870e3b50354e011d955dfd56236d45a2d95b90fedf52073a03a`）第 58–59 行硬断言 `HEAD==2df8db7…`，**不得修改其字节、亦不得在候选 clone 直接调用**（会立即 SystemExit）。
   - 允许方式：新建 AC4 专用 wrapper（新文件，路径在 `verification/FEA-15-PIN-BASIS-ENFORCE-1/**` 允许范围内，如 `ac4_inventory_capture.py`），复刻冻结 wrapper 的模式——`sys.dont_write_bytecode=True`、以 `importlib` 从**被测 clone 内**的 `verification/FEA-15-PIN-POLICY-1/pin_inventory.py` / `pin_inventory_delta.py` 加载 frozen generator；inventory 模式仅重绑 `module.OUT`，delta 模式仅重绑 `BASELINE`/`EXPECTED_BASELINE_HEAD`/`CURRENT`/`OUTPUT`（与 Addendum 2 批准的重绑定集合同构：`EXPECTED_BASELINE_HEAD` 置 `bfae0b9bd6a9b85a9a546d2adda0b684783ddb24`）；HEAD 断言改为断言被测 clone 的预期候选 HEAD。
   - **generator 字节同一性前置断言（必做）**：wrapper 须记录并比对每个被测 clone 内 generator 源的 SHA-256 与 Git blob，确认与 `2df8db7…`/`bfae0b9…` 处的 PIN-POLICY-1 冻结源一致（R0→候选路径集不含 generator，故必须逐字节相同）；任何不一致即停止，不得运行 inventory。
   - 禁止：以环境变量、monkey-patch 或任何方式改写 frozen generator 内部常量/逻辑；禁止修改冻结 wrapper 与三个 generator 的任何字节；禁止把 inventory 输出写回历史路径（覆盖 `pin-inventory-2df8db7.json` 等）。

### A.3 fresh clone 源 HEAD（确认，不改动）

维持主裁决：两 fresh clone（`git clone --no-checkout` + checkout 前 clone-local `core.autocrlf=true|false`、`core.longpaths=true`）检出于候选 HEAD `a2a3401eb703c3ae7899375755c981eabbf47572`；若追加 R-001 负例测试，则在保留的 validation clone（`G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/validation-ac2ac3`，`a2a3401…` 对象仅存在于该 clone，main 仓库不可达）上追加提交产生**新候选 HEAD**，两 clone 检出于同一新 HEAD，并记录全部相关 HEAD。

理由（明确记录，不改变结论）：`a2a3401…` 形态 = main 基线 `dd637242…` + 4 实现 overlay，是 AC5 集成的预演形态，其 default/TaskPath/API/pins 已有 `ac2ac3-candidate-gates.log` 与 `ac2ac3-baseline-controls.log` 同形态基线可比；`5e216dc…` 实现分支基于 R0、不含 main AC1d 前进，不是集成形态；R0 clone 保留作 A.2 的基准 inventory 载体与历史证据，不作 AC4 gate 载体。故不从 `5e216dc…` 或 R0 clone 建立 AC4 clone。

### A.4 保留状态、已释放操作与停止条件（汇总）

- **保留不变**：主裁决全部 Decision；三项 AC2/AC3 limitation 与 false-checkout C04b/C17 mismatch 保持 FAIL/limitation 原状态；AC5 NOT RELEASED；冻结 wrapper/generator/`.gitattributes`/18 pins/`verify_pins.ps1`/历史字节不可改；禁止集成、close、push、清理/prune/GC/repack。
- **属 AC4 已释放范围的操作**：A.1 对照；A.2 三层对照及新建 AC4 wrapper（新文件）与 inventory/delta 输出（新文件，入 `verification/FEA-15-PIN-BASIS-ENFORCE-1/`）；§5.2 全部 gates 与测试；R-001 四类负例测试（限 `test_canonical_evidence_basis.py` 路径内追加）；Linux 如实记 `NOT_RUN`。
- **停止条件（在主裁决 §5.7 基础上追加）**：diff 路径集 ≠ A.1 允许集精确匹配（含出现 D 状态或第 12 路径）；generator SHA-256 与冻结源不一致；行级 delta 出现无法归因允许集的 ADDED/CHANGED 行、或任何无法归因的 REMOVED 行；clone-T 历史行差异无法经 CRLF→LF 归一化闭合。任一命中即停、保留现场、回报裁决。
