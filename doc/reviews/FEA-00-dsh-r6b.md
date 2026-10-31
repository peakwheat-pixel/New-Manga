---
document_id: FEA-00-dsh-r6b
kind: independent_review
reviewer: reviewer-r6
reviewer_kind: subagent
reviewer_source: "DSH 派发子 agent reviewer-r6，独立上下文（Agent Teams spawn_teammate，fresh context；未参与本变更实现与返修）"
base_commit: 2f611e2aa1f1e480b6da16461d6c014f54a56c95
reviewed_head: 47734a336eec3b03ed6f2440540aa3bee6a3c821
decision: changes_requested
---

# Review：FEA-00 治理检查器 r6b 返修（关 R-01/R-02）

## 结论

**`changes_requested`。**

r6 的三项 disposition 全部核实：**R-01 关闭、R-02 关闭、R-03 的 accepted limitation 裁定可接受**（详见 Findings 表）。用户要求 1–6 中强制项（提交边界、独立重跑、探针复跑、自建样本）均通过，且作者声明的数字全部独立复现。

但自建新样本发现本 commit **引入 2 类新的行为回归**（相对其父提交 `2f611e2aa`，后者在这些样本上是正确的）：

- **E-01（P1，fail-open + fail-closed 双方向）**：R-02 修复把「HTML 注释抑制 inline 解析」一并移出行内位置——`<!--` 现在只在行首被识别。CommonMark 中 HTML 注释无论出现在行内何处，其内容都不参与 inline 解析。现状：
  - fail-open：行内注释中的反引号被当作 span 定界符，使 sentinel 落入本应被识别的跨行 code span 却被**接受**（E1a/E1b；父提交正确拒绝）；
  - fail-closed：同一反引号当 opener 吞掉下一行合法字段 → **误拒**（E1d；父提交正确通过）。
- **E-02（P2，fail-closed）**：`Mask-ParagraphCrossLineCode` 的块级 HTML 识别被过度收窄，两类块上下文失效，块内反引号与后续合法字段配对 → **误拒**：
  - ① 行首判定要求标签位于列 0，未容忍 CommonMark 允许的 0–3 个前导空格（段落切分正则 `^ {0,3}` 是容忍的）→ ` <pre>`/`  <pre>`/`   <pre>`/`  <!--` 块开行未识别（E2a/E2b/D1/D2）；
  - ② 段落起始（空行后）的 `<code>`（type-7 HTML block）被从掩码的块识别中整体移除 → `<code>` 块内反引号参与 inline 扫描（E3a；父提交正确通过）。

两类回归都不影响当前仓库文档（checker EXIT=0、自由正文边界未扩大），但 E-01 属 fail-open（可接受被 code span 隐藏的权威字段），与 r5 P1、r6 R-01 同类。按 `doc/templates/REVIEW.md` 批准门槛（P0/P1 未解决不可批准），**本 head 不建议直接交 DSH 集成**。修复面很小（YAGNI 口径：注释位置无关性 + 行首缩进容忍 + 段落起始 `<code>` 块，约 10 行 + 5 条回归样本，见建议），闭环后可再交独立复审或按同源样本复验。

## 固定指纹（本 Review 实测）

| 对象 | 值 | 测量方式 |
|---|---|---|
| `reviewed_head` = `47734a336` parent | `2f611e2aa` | `git show --format=%P` |
| 提交边界 | 仅两文件：`tools/governance/check.ps1` **+10/−6**、`tools/governance/tests/test_architecture_assertions.py` **+18/−0**（合计 **+28/−6**，与声明一致） | `git show --stat/--numstat` |
| `47734a336:tools/governance/check.ps1` blob | `40bfc177fd205cf8638a023a69face3b9990184f` | `git rev-parse` |
| `47734a336:…test_architecture_assertions.py` blob | `2a694b77dc2e685c7a9b6f9e944f452e84b00583` | `git rev-parse` |
| 工作区两文件 blob（`git hash-object --no-filters`） | 与上述 HEAD blob **逐字节相同** | `git hash-object` |
| 工作区 `check.ps1` SHA-256 | `960ffa59c8937b2f35729894d4e05c696ce2ce4c3e3480248db9df018064c498` | `Get-FileHash` |
| 工作区测试文件 SHA-256 | `5c088010a195ac43896cc7f6805214a368cdc62bb072fb75e6b71e0ee6c708b0` | `Get-FileHash` |
| 直接父 `2f611e2aa:check.ps1` SHA-256（对比基线） | `5b7b36c372ff39340f6bf9cc7988218d1c8abf1615fc8dbd867c6389d0eda7cb` | 复核 `review-r6/chk-2f611e2aa.ps1`（与 git blob 一致） |
| 固定基线 parent `504797ba7:check.ps1` | `13e08555e4d7f107623f1daaea325bb8c8f776fb88e75b2ec9b87e2e25bde5f5`（未变化） | `review-r6/chk-504797ba7.ps1` |
| 证据文件 `final-matrix-r6b-16.log` | `ce59f25f9b32282a641dcea9698789266e47df12f48866a25ef1963d26a13a44`（与作者 §4 一致） | `Get-FileHash` |
| 证据文件 `r6-verification.md`（r6b 修订） | `11af60fc15fd27c386195e7abaeb53e5eadebfb809a61294a57d859ac538eed6` | `Get-FileHash` |
| 证据文件 `pre-change-scope.md`（r6b 修订） | `f6664017775dc72d7965846bd3142305dccd106d745262b086331f38f80e45f8` | `Get-FileHash` |
| `git status --porcelain` | 无 tracked 修改；审查开始前 11 个既有 untracked（含 r6 报告），审查后新增本报告 1 个 | 只读复核 |

## 逐项 disposition（R-01 / R-02 / R-03）

| finding | r6 级别 | 本轮 disposition | 证据（本 Reviewer 独立实测） |
|---|---|---|---|
| **R-01** 行首 `<code>…</code>` 被当作段落边界 → fail-open | P1 | **closed** | 原始样本 A1 与 5 个变体（A2 跨行闭合 / A3 带属性 / A4 大写 / A5 缩进 2 空格 / A6 单独行）在当前 head 全部 **REJECT**；同一批在父提交 `2f611e2aa` 上 A1–A5 全为 **PASS**（证明修复有效且必要）。新增测试 `test_line_start_code_element_does_not_end_paragraph` 在 `2f611e2aa` checker 上失败、在当前 head 上通过 |
| **R-02** 行内 `<pre>/<code>` 内反引号被跳过 → fail-open | P2 | **closed** | 原始样本与变体 B1–B4（同行/跨行闭合、code/pre、blockish）在当前 head 全部 **REJECT**；父提交上 B1/B2 为 **PASS**。新增测试 `test_backticks_inside_inline_html_elements_still_form_code_span`（`code`/`pre` 两个子用例）在 `2f611e2aa` checker 上失败、当前 head 通过；r6 的 4 样本专项探针当前 head **4/4 OK** |
| **R-03** setext/列表/块引用边界未识别 → fail-closed | P2 | **accepted（裁定可接受）** | 触发条件、方向（fail-closed、无安全绕过）、继承来源（`1672f3c40`）、范围依据（用户本轮只要求「空行 + ATX 标题」）已记录在 `r6-verification.md` §1 表与 §5；本 Reviewer 复跑 r6 的 setext/列表/引用探针，当前 head 仍 **REJECT**（与 r6 一致，未扩大）；该限制不产生 fail-open。**建议**：把「R-03」登记为正式 accepted limitation（例如在 `pre-change-scope.md`/checker 头注释中给出触发条件），后续扩展边界集合时另立范围 |

> 说明：R-01/R-02 的「closed」判定以**当前 head 实测通过 + 父提交实测失败**双证据为准，不采信作者日志。

## Standards（可选视角：executed）

- 提交范围、注释风格、测试结构符合仓库既有约定；新测试沿用 `unittest` + workspace 隔离夹具；两条新测试均带注释说明 CommonMark 依据。
- **文档级小问题（并入 E-01）**：`check.ps1:398-400` 新注释「Only a line-start block opener suppresses inline parsing. An inline `<pre>`/`<code>` tag does not」只覆盖了标签，未说明「HTML 注释在行内任意位置仍应抑制解析」——这正是 E-01 的注释与实现一起被过度收窄的地方。
- **§4.4 覆盖性（过程观察）**：r6b 事前范围的 16 场景矩阵未包含本轮被改变的行为类（行内 HTML 注释、缩进块开行），因此「0/16 mismatch」不足以覆盖 R-02 语义改动的全部影响面。建议下一轮把 E-01/E-02 的样本加入矩阵，避免「同一类改动再漏」。
- baseline smell（判断项）：无新增值得报告的 smell；E-02 根因是两处缩进规则不一致（`:401` 的列 0 判定 vs `:463` 的 `^ {0,3}`），属 possible Duplicated Knowledge。

## Spec（可选视角：executed）

来源 = r6 Findings + 用户本轮 6 项要求。核对结果：

1. 提交边界与 blob：**符合**（+28/−6，两 blob 与声明一致，工作区与 HEAD 一致，无 tracked 修改）。
2. 独立重跑：checker **EXIT=0**、测试 **27/27 OK**、16 场景矩阵 **0 / 9 / 3**——**全部与声明一致**。
3. r6 探针复跑：21 用例 **0 mismatch**；4 样本专项 **4/4 OK**——**与声明一致**。
4. 自建新样本：R-01/R-02 变体全部符合预期；但发现 **E-01/E-02** 两类新回归（作者未覆盖、未声明）。
5. R-03 裁定：记录充分（触发、方向、继承、范围），**可接受**。
6. 新 P0/P1/P2：**E-01（P1）、E-02（P2）**。

潜在 scope creep：无；返修只动 checker 与测试。

## Architecture

- R-01/R-02 的修复方向正确：段落边界只保留可打断段落的块结构（`<pre>`/`<!--`/fence/ATX），行内标签不再抑制 inline 解析。两条规则现在有测试锁定（27 用例含判别力）。
- 但「HTML 抑制 inline 解析」这条规则被**过度收窄**：CommonMark 中 HTML **注释**的抑制是位置无关的（行内注释内容不参与 inline 解析），HTML **标签**则只在块上下文（行首、≤3 空格）抑制。当前实现把两者都绑到「严格列 0 的行首」条件（`check.ps1:401`），于是产生 E-01（注释）与 E-02（缩进块开行）两个方向的偏差。
- 段落切分（`:463`，`^ {0,3}`）与掩码行首判定（`:401`，要求列 0）不一致，是 E-02 的直接根因。

## Verification

| 场景 | 命令 | 对象 | 结果 | 证据日志 |
|---|---|---|---|---|
| 治理全量 checker | `pwsh -NoProfile -File tools/governance/check.ps1` | 工作区 = `47734a336` | **EXIT=0**；scope 15；`PASS (2 warnings)`（7 个非终态 Task；REBASELINE_PLAN 6624 bytes/58 lines） | `review-r6b/checker-current.log` |
| 架构断言测试 | `python -B -m unittest discover -s tools/governance/tests -p test_architecture_assertions.py -v` | 同上 | **EXIT=0**；`Ran 27 tests`，`OK`（57.5s） | `review-r6b/unittest-current.log` |
| 16 场景矩阵 | `python -B -W ignore …/r6_matrix.py` | 当前 checker | **EXIT=0**；16 场景 **0 mismatch** | `matrix-current.log` |
| 16 场景矩阵 | 同上 + `FEA_CHECKER_SOURCE=checker-baseline-parent.ps1` | parent `504797ba7` | **EXIT=1**；**9 mismatch** | `matrix-parent.log` |
| 16 场景矩阵 | 同上 + `FEA_CHECKER_SOURCE=checker-head-1672f3c40.ps1` | HEAD `1672f3c40` | **EXIT=1**；**3 mismatch**（P1/P2-1/P2-2 组合用例） | `matrix-head-1672f3c40.log` |
| 新增测试判别力 | 同上 unittest + `FEA_CHECKER_SOURCE=chk-2f611e2aa.ps1` | 父提交 `2f611e2aa` | **EXIT=1**；`Ran 27 tests`，`FAILED (failures=3)`：`test_line_start_code_element_does_not_end_paragraph` ×1、`test_backticks_inside_inline_html_elements_still_form_code_span` ×2（`code`/`pre` 子用例）；其余 25 用例通过 | `unittest-with-2f611e2aa-checker.log` |
| r6 的 21 用例探针（复跑） | `python -B -W ignore reviewer_r6b_probe.py` | 当前 | **EXIT=0**；21 用例 **0 mismatch**；R-03 的 3 个 observation probe 仍 REJECT（与裁定一致） | `probe21-current.log` |
| r6 的 R-01/R-02 专项（复跑） | `python -B -W ignore probe_extra_r6b.py` | 当前/1672f3c40/parent | 当前 **4/4 OK**（3 REJECT + `line-start-pre-control` PASS）；`1672f3c40` 3 mismatch（预期内）；parent 3 mismatch（预期内） | `probe-extra.log` |
| Reviewer 新样本（18 期望用例） | `python -B -W ignore r6b_new_samples.py [checker]` | 当前 / `2f611e2aa` / `1672f3c40` | 当前 **0 mismatch**；`2f611e2aa` 7 mismatch（A1–A5、B1、B2 被接受）；`1672f3c40` 6 mismatch | `new-samples-current.log` / `-prev-2f611e2aa.log` / `-head-1672f3c40.log` |
| E-01/E-02 家族探针 | `python -B -W ignore probe_family.py [checker]` | 当前 / `2f611e2aa` | 当前：E1a **PASS（期望 REJECT）**、E1b **PASS（期望 REJECT）**、E1d **REJECT（期望 PASS）**、E2a **REJECT（期望 PASS）**、E2b **REJECT（期望 PASS）**、两个未缩进对照 PASS；父提交：E1a/E1b REJECT、E1d/E2a/E2b PASS（**全部正确**） | `probe-family-current.log` / `probe-family-prev-2f611e2aa.log` |
| E-02 的 `<code>` 块探针 | `python -B -W ignore`（内联脚本，见 `probe-code-block.log`） | 当前 / `2f611e2aa` | 当前：E3a `<code>` 块 + 无空行 **REJECT（期望 PASS）**、E3b/E3c **PASS**；父提交：E3a/E3b/E3c 全 **PASS** | `probe-code-block.log` |
| CommonMark 参考核验 | `python -B -W ignore commonmark_check.py` + 家族/块脚本（markdown-it-py 4.2.0, commonmark preset） | — | E1a：marker 落在 `<code>` 内（应 REJECT）；E1b：整条字段落在 code span（应 REJECT）；E1d：字段为独立可见段落（应 PASS）；E2a/E2b：`<pre>`/`<!--` 块内容隐藏、字段可见（应 PASS）；E3a：`<code>` 块后字段为可见文本（应 PASS）；未缩进对照同样可见（应 PASS） | `commonmark-check.log` / `commonmark-check-family.log` / `commonmark-check-codeblock.log` |
| 全 governance 测试目录 | `python -B -m unittest discover -s tools/governance/tests -p "test_*.py" -v` | 当前 | **EXIT=1**；`Ran 44 tests`，3 failures 全部在 `test_residual_runtime_identity`（仅用 `git` + `clean_workspace`，不调用 `check.ps1`；与 r6 同源的既有状态，不计入本变更回归） | `unittest-all-governance.log` |
| 提交边界 | `git show --stat/--numstat`、`git rev-parse`、`git hash-object`、`git status` | — | 见「固定指纹」 | — |

### 自建新样本（不复用作者样本；夹具在 `review-r6b/` 自建，未触碰 tracked 文件）

| 组 | 样本 | 期望 | 当前 `47734a336` | 父提交 `2f611e2aa` |
|---|---|---|---|---|
| R-01 | A1 行首 `<code>README</code>` 同行闭合 + 跨行 span | REJECT | REJECT ✓ | PASS（r6 回归） |
| R-01 | A2 `<code>` 跨行闭合（开/闭在不同行） | REJECT | REJECT ✓ | PASS |
| R-01 | A3 `<code class="sample">` 带属性 | REJECT | REJECT ✓ | PASS |
| R-01 | A4 `<CODE>` 大写 | REJECT | REJECT ✓ | PASS |
| R-01 | A5 `  <code>` 缩进 2 空格 | REJECT | REJECT ✓ | PASS |
| R-01 | A6 `<code>` 单独行 + `</code>` 在后 | REJECT | REJECT ✓ | REJECT |
| R-02 | B1 `<code>` 内反引号 + 同行闭合 | REJECT | REJECT ✓ | PASS |
| R-02 | B2 `<pre>` 内反引号 + 同行闭合 | REJECT | REJECT ✓ | PASS |
| R-02 | B3 行内 `<code>` 后开 span、跨行闭合 | REJECT | REJECT ✓ | REJECT |
| R-02 | B4 行内 `<pre>` 包住多行 span | REJECT | REJECT ✓ | REJECT |
| 预防回归 | C1 行首 `<pre>` 对照（type-6 可打断段落） | PASS | PASS ✓ | PASS |
| 预防回归 | C2 `<pre>` 块内单反引号 + 块后字段 | PASS | PASS ✓ | PASS |
| 预防回归 | C3 行内 `<code>` 后接合法字段 | PASS | PASS ✓ | PASS |
| 预防回归 | C4 行内 `<code>` 内转义反引号 + 字段 | PASS | PASS ✓ | PASS |
| 预防回归 | C5 行内 `<code>` + 未闭合反引号 + ATX 标题 + 字段 | PASS | PASS ✓ | PASS |
| 预防回归 | C6 同行已闭合 span + 字段 | PASS | PASS ✓ | PASS |
| 预防回归 | C7 自由正文（`doc/STATUS.md`）跨行 span | PASS | PASS ✓ | PASS |
| 预防回归 | C8 CRLF 行尾 ATX 边界 | PASS | PASS ✓ | PASS |
| 预防回归 | E3b `<code>` 块 + `</code>` 后空行 + 字段 | PASS | PASS ✓ | PASS |
| 预防回归 | E3c `<code>` 块（无块内反引号）+ 字段 | PASS | PASS ✓ | PASS |
| **E-01** | **E1a** 行内注释含 1 个反引号 → 后续真实 span 包住字段 | **REJECT** | **PASS ✗（fail-open 回归）** | REJECT ✓ |
| **E-01** | **E1b** 行内注释含 2 个反引号 → 双反引号 span 包住字段 | **REJECT** | **PASS ✗（fail-open 回归）** | REJECT ✓ |
| **E-01** | **E1d** 行内注释含反引号 → 当作 opener 吞掉下一行合法字段 | **PASS** | **REJECT ✗（fail-closed 回归）** | PASS ✓ |
| **E-02** | **E2a** ` <pre>`（1 空格）块开行 + 块内反引号 | **PASS** | **REJECT ✗（fail-closed 回归）** | PASS ✓ |
| **E-02** | **E2b** `  <!--`（2 空格）缩进注释块 + 块内反引号 | **PASS** | **REJECT ✗（fail-closed 回归）** | PASS ✓ |
| **E-02** | **E3a** 段落起始 `<code>`（type-7 块，`</code>` 后无空行）+ 块内反引号 | **PASS** | **REJECT ✗（fail-closed 回归）** | PASS ✓ |
| 对照 | 未缩进 `<pre>`/`<!--` 同类样本（CTRL） | PASS | PASS ✓ | PASS |

### 非 finding 的行为变化（记录备查）

- **D5（tab 缩进 `<pre>`）**：当前 head REJECT、父提交 PASS；markdown-it 显示 tab 行属段落续行、`<pre>` 为 inline、反引号 span 成立、字段落进 `<code>` → **REJECT 是 CommonMark 正确行为**，属改进，不计回归。
- **E1c（字段前先出现 span opener、后出现行内注释）**：markdown-it 显示 opener 先配对（leftmost 优先），字段部分可见 → 期望 PASS，当前 head PASS ✓，不构成 finding。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-01 | P1（r6） | `check.ps1:463` | 行首 `<code>…</code>` 被当作段落边界 → 跨行 span 内 sentinel 被接受 | 见 disposition 表：A1–A6 当前全 REJECT、父提交 A1–A5 PASS；新增测试在父提交失败 | —（已修） | **closed** |
| R-02 | P2（r6） | `check.ps1:398-409` | 行内 `<pre>/<code>` 内反引号被跳过 → 跨行 span 漏报 | B1–B4 当前全 REJECT、父提交 B1/B2 PASS；新增测试在父提交失败；4 样本专项 4/4 OK | —（已修） | **closed** |
| R-03 | P2（r6） | `check.ps1:463` | setext/列表/块引用边界未识别 → fail-closed 误拒 | 3 探针当前仍 REJECT（与 r6 一致，未扩大）；`r6-verification.md` §1/§5 已记录触发、方向、继承、范围依据 | 登记为正式 accepted limitation（可在 checker 头注释与 `pre-change-scope.md` 交叉引用） | **accepted** |
| **E-01** | **P1（新）** | `check.ps1:398-413`（`<!--` 分支被并入「严格列 0 行首」条件 `:401`） | CommonMark 中 HTML 注释在**行内任意位置**都抑制其内容的 inline 解析。现在行内注释里的反引号被当作 span 定界符：① fail-open——后续真实 opener 与注释反引号错配，字段被包进跨行 span 却被**接受**（E1a/E1b）；② fail-closed——注释反引号当 opener 吞掉下一行合法字段（E1d）。两项均为本 commit 引入（父提交 `2f611e2aa` 正确） | 隔离夹具（AD-003 sentinel 行替换）：当前 E1a/E1b **PASS（EXIT=0）**、E1d **REJECT（EXIT=1）**；父提交 E1a/E1b **REJECT**、E1d **PASS**。markdown-it-py 4.2.0 (commonmark)：E1a marker 落在 `<code>` 内、E1b 整条字段落在 code span、E1d 字段为独立可见段落。日志：`probe-family-current.log` / `probe-family-prev-2f611e2aa.log` / `commonmark-check-family.log` | 把 `<!--` 检测移回**任意位置**（注释内容不参与 inline 解析），`<pre>/<code>` 标签保持行首块级判定；补 E1a/E1b（REJECT）、E1d（PASS）三条回归样本 | **open** |
| **E-02** | P2（新） | `check.ps1:401`（行首判定 `$i -eq 0 -or chars[$i-1] -eq 10`，不允许 0–3 空格）与 `:463`（`^ {0,3}`）不一致；`:407`（`$open` 只识别 `pre`，段落起始的 `<code>` 块不再抑制扫描） | 掩码阶段的块级 HTML 识别被过度收窄，两类块上下文失效：① 缩进 1–3 空格的块开行（` <pre>`/`  <pre>`/`   <pre>`/`  <!--`）未被识别；② 段落起始（空行后）的 `<code>`（CommonMark type-7 HTML block）不再抑制块内反引号扫描。两者都使块内容反引号与后续合法字段配对 → 合法文档被误拒（fail-closed）。本 commit 引入（父提交按「任意位置识别」在这三类样本上恰好正确） | 当前 E2a（1 空格 `<pre>`）、E2b（2 空格 `<!--` 块）、D1（2 空格）、D2（3 空格）、E3a（段落起始 `<code>` 块）均 **REJECT**；父提交全部 **PASS**；未缩进对照（CTRL）与 E3b/E3c 当前/父提交均 PASS。markdown-it：缩进块开行成立、`<code>` 块后字段为可见文本、字段独立可见段落（均应 PASS）。日志：`probe-family-current.log`、`new-samples-current.log`（D1/D2）、`probe-code-block.log`（E3a/E3b/E3c）、`commonmark-check-family.log`、`commonmark-check-codeblock.log` | ① 行首块开行判定允许 ≤3 前导空格（复用已有 `$line` 与 `^ {0,3}(?:<!--|(?i:<\s*pre(?=[\s>/]|$)))` 正则）；② 恢复段落起始 `<code>` 的块识别（仅当 `<code>` 位于段落首行时抑制到 `</code>`，不要恢复行内跳过，以免重新引入 R-01/R-02）；补相应正例（1–3 空格缩进的 `<pre>`/`<!--`、段落起始 `<code>` 块） | **open** |

## 残余风险与 NOT_RUN

- **NOT_RUN**：完整 CommonMark 规范测试套件；HTML block type 1/3/4/5（`<script>`/`<?`/`<!X`/`<![CDATA[`）、表格、脚注等组合；缩进代码块（已属 R-03 同族 accepted limitation）。
- **残余风险**：HTML/CommonMark 交互仍是近似实现，E-01/E-02 说明「注释位置无关性」「块开行缩进容忍」「段落起始 `<code>` 块」三条规则尚未抽成单一可测规则，后续改动仍可能再引入同类偏差；建议把这三条规则加上判别力样本并纳入 §4.4 矩阵。
- 产品功能、真实删除、迁移、并发、GUI 均 `NOT_RUN`（不属本变更范围）。
- 全 governance 测试目录 3 个失败（`test_residual_runtime_identity`）与本变更无调用关系（不 import/执行 `check.ps1`），属既有仓库状态。
- 本报告只对 `reviewed_head = 47734a336` 有效；E-01/E-02 修复后须对新 head 重新安排独立复审（或由 DSH 用同源样本复验并记录）。

## 独立性、仓库状态与证据位置

- 本 Reviewer 为 DSH 派发的独立上下文子 agent，**未参与**本变更的实现与返修；结论基于自建夹具与独立重跑，未采信作者日志。
- 全程只读仓库：未执行 `git add/commit/checkout/stash`；未修改任何 tracked 文件；`doc/reviews/FEA-00-dsh-r6.md` 与 `review-r6/` 证据保持原字节（r6 报告 SHA-256 复核 = `6d3ea16d…5c4166`，未变）。
- 审查前 `git status --porcelain`：11 个既有 untracked（10 个既有文档 + r6 报告），无 tracked 修改；审查后新增本报告，共 12 个 untracked。
- 证据目录：`G:\CODEX\New Manga.workspace\agent-output\dsh\review-r6b\`（本报告引用的全部日志、探针脚本与夹具产物；夹具临时目录已清理）。
