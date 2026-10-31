---
document_id: FEA-00-dsh-r6c
kind: independent_review
reviewer: reviewer-r6
reviewer_kind: subagent
reviewer_source: "DSH 派发子 agent reviewer-r6，独立上下文（Agent Teams spawn_teammate，fresh context；未参与本变更实现与返修）"
base_commit: 47734a336eec3b03ed6f2440540aa3bee6a3c821
reviewed_head: 83c422345cf9a5be711c002f19a7ba0f2e95f7d6
decision: approved
---

# Review：FEA-00 治理检查器 r6c 返修（关 E-01/E-02）

## 结论

**`approved`（可交 DSH 集成；附 1 条非阻断 P2 证据归档建议）。**

r6b 的两项 finding 均**关闭**，且 R-01/R-02 保持关闭、R-03 的 accepted limitation 仍成立：本 Reviewer 用自建隔离夹具独立重跑作者声明的全部数字（checker EXIT、31 测试、22 场景矩阵四个基线、判别力 8 failures、四个既有探针），全部复现；另用 **22 个自建新样本**（E-01/E-02 变体 + 预防回归）验证当前 head **22/22 符合预期**、在父提交 `47734a336` 上 **11 mismatch**，并用 markdown-it-py 4.2.0（commonmark preset）逐条核验 CommonMark 语义。未发现新的 P0/P1/P2 代码缺陷。

唯一记录问题是证据归档（非阻断 P2，见 Findings E-03）：`r6c-verification.md` §3 引用的「Reviewer 探针复跑」日志在实施者证据目录 `FEA-00-R2-fix2\` 中缺失，其中 `probe-family-r6c.log` 由实施侧写入了 **reviewer 证据目录** `review-r6b\`（时间 23:33:42）；其余三个名字对应的是 reviewer 自己的日志。相关结论本身均已被本 Reviewer 独立复现为真，故不影响集成判定，但建议补齐实施侧日志与哈希并避免写入 reviewer 证据目录。

## 固定指纹（本 Review 实测）

| 对象 | 值 | 测量方式 |
|---|---|---|
| `reviewed_head` = `83c422345` parent | `47734a336` | `git show --format=%P` |
| 提交边界 | 仅两文件：`tools/governance/check.ps1` **+42/−12**、`tools/governance/tests/test_architecture_assertions.py` **+41/−0**（合计 **+83/−12**，与声明一致） | `git show --stat/--numstat` |
| `83c422345:tools/governance/check.ps1` blob | `dd800c588e3d227a21abe908bc27c0a523995ae0` | `git rev-parse` |
| `83c422345:…test_architecture_assertions.py` blob | `161435c931cb76810054efe0d71e672d6c662512` | `git rev-parse` |
| 工作区两文件 blob（`git hash-object --no-filters`） | 与上述 HEAD blob **逐字节相同** | `git hash-object` |
| 工作区 `check.ps1` SHA-256 | `d1c2f6632c384bbf53a8ea8cc740ea86338f8ee30c5d9b989181978ff5fe765b` | `Get-FileHash` |
| 工作区测试文件 SHA-256 | `6caf51767b36d59567a1a635479e042f3a67f07179a93f0230c75df0b7337ec0` | `Get-FileHash` |
| 对比基线副本（自 git blob 提取，逐字节校验） | parent `504797ba7` = `13e08555…`；`1672f3c40` = `ab2cc3ab…`；`2f611e2aa` = `5b7b36c3…`；`47734a336` = `960ffa59…` | `git cat-file` + `Get-FileHash` |
| `r6c_matrix.py` | `2a3f09b76759b6009811fce82b49b7a3a853a1d2560cdd1b01e673ad7b93d834`（与 §4 一致） | `Get-FileHash` |
| `matrix-r6c-current/47734a336/parent/1672f3c40-22.log` | 与 §4 声明哈希逐一一致（`288b1f87…` / `f0c8298e…` / `c8f6bdac…` / `60cdbc27…`） | `Get-FileHash` |
| `r6c_e3_probe.py` / `r6c-e3-probe.log` | `36a36b07…` / `7ffa90e8…`（与 §4 一致） | `Get-FileHash` |
| `git status --porcelain` | 无 tracked 修改；审查前 12 个既有 untracked（含 r6/r6b 报告），审查后新增本报告 1 个 | 只读复核 |

## 逐项 disposition

| finding | 级别 | disposition | 证据（本 Reviewer 独立实测） |
|---|---|---|---|
| **E-01** 行内 HTML 注释不再抑制 inline 解析（fail-open E1a/E1b + fail-closed E1d） | P1（r6b） | **closed** | `probe_family` 当前：E1a/E1b **REJECT**、E1d **PASS**、CTRL×2 PASS（7/7）；父提交 `47734a336`：E1a/E1b PASS、E1d REJECT（5 处相反）→ 修复有效。新增 4 个 E-01 变体（注释含标签/多行/嵌套标记/双反引号）全部 REJECT，注释后置/无 span/转义/ATX 组合全部 PASS。新增测试 `test_inline_html_comment_backticks_form_code_span`（single/double）与 `test_inline_html_comment_backtick_does_not_swallow_next_field` 在 `47734a336` 上失败、当前通过 |
| **E-02 ①** 块级 HTML 开行缩进 | P2（r6b） | **closed** | 自建：`<pre>` 0/1/2/3 空格缩进、`<!--` 块 0/3 空格缩进全部 **PASS**（父提交上 1/2/3 空格为 REJECT）。新增测试 `test_indented_block_openers_suppress_inline_parsing`（pre-1sp/2sp/3sp、comment-2sp）在父提交上 4 个 subTest 全失败 |
| **E-02 ②** 段落起始完整 `<code>` 块 | P2（r6b） | **closed** | 自建：`<code>` 块 0 空格 / 2 空格 / 带属性 / 大写 + 尾随空格全部 **PASS**（父提交上 0/2 空格与大写均 REJECT）。新增测试 `test_paragraph_leading_code_block_suppresses_inline_parsing` 在父提交上失败 |
| **R-01** 行首 `<code>…</code>` 不结束段落 | P1（r6） | **closed（保持）** | 22 场景矩阵（含 16 个旧场景）当前 **0 mismatch**；r6b 的 A1–A6 变体在复跑中仍全部 REJECT（`new-samples-r6b18-current.log` 18/18） |
| **R-02** 行内 `<pre>/<code>` 内反引号仍开启 span | P2（r6） | **closed（保持）** | 同上；r6b 的 B1–B4 变体仍全部 REJECT；`probe_extra` 当前 **4/4 OK** |
| **R-03** setext/列表/块引用边界 | P2（r6） | **accepted（维持）** | 21 用例探针复跑 0 mismatch，其中 3 个 R-03 observation probe 仍 REJECT（与 r6/r6b 一致，未扩大）；`r6-verification.md` §5 的触发条件/方向/继承来源记录未变 |

**判定：`47734a336` 上被 E-01/E-02 破坏的 5 个行为样本全部恢复；新增的 4 条测试具有判别力（在父提交上 8 个失败实例），22 场景矩阵锁定 E-01/E-02 六个样本。**

## Standards（可选视角：executed）

- 提交范围合规（仅 checker + 测试）；`Test-BlockHtmlStart` 为单一职责小函数并有注释说明 CommonMark 0–3 空格规则；`<code>` 块识别显式区分「段落首行」与「段落续行」，避免重新打开 R-01；测试沿用既有 `unittest` + workspace 夹具，4 条新测试均带 CommonMark 依据注释。
- 无新增 Fowler smell；`Test-BlockHtmlStart` 与 `:463` 段落切分的 `^ {0,3}` 现在语义一致，消除了 r6b 的 duplicated knowledge。
- **证据归档（P2，非阻断）**：见 Findings E-03——实施侧复跑日志未入 `FEA-00-R2-fix2\`，且有 1 个文件写入 reviewer 证据目录 `review-r6b\`（`probe-family-r6c.log`，23:33:42）。§4.4 要求日志带 EXIT 并逐次归档；本 Reviewer 已独立复现全部声明，故不影响结论，但建议整改。
- §4.4 覆盖性：r6c 事前范围把 22 场景矩阵（16 + E-01/E-02 六样本）写入 `pre-change-scope.md` §3/§4，覆盖了本轮被改变的行为类（行内注释位置无关性、块开行缩进、段落起始 `<code>` 块），较 r6b 有明显改进。

## Spec（可选视角：executed）

来源 = r6b Findings + 用户本轮 6 项要求。逐项：

1. 提交边界与 blob：**符合**（+83/−12、两 blob 与声明一致、工作区与 HEAD 一致、无 tracked 修改）。
2. 独立重跑：checker **EXIT=0**；测试 **31/31 OK**；22 场景矩阵 **0 / 6 / 0 / 3 / 11**（当前 / `47734a336` / `2f611e2aa` / `1672f3c40` / parent）——**全部与声明一致**。
3. 四个既有探针复跑：`probe_family` 7/7、`r6b_new_samples` 18/18、`reviewer_r6b_probe` 21/21、`probe_extra` 4/4——**全部符合**。
4. 自建新样本：22 个期望用例当前 **0 mismatch**，父提交 **11 mismatch**；无新 fail-open / fail-closed（见下表）。
5. R-03 accepted limitation：记录充分、未扩大，**仍可接受**；E-01/E-02 **均可判 closed**。
6. 新 P0/P1/P2：**无代码缺陷**；1 条非阻断 P2 证据归档问题（E-03）。

## Architecture

- E-01 修复把「HTML 注释抑制 inline 解析」恢复为**位置无关**（`:411-416`），与 CommonMark 的 inline 注释语义一致；opener 先于注释时注释仍被跳过（leftmost 优先），自建 T3/T4/E1c 变体验证通过。
- E-02 修复引入 `Test-BlockHtmlStart`（`:352-364`）：块级 HTML 开行允许 0–3 空格，与段落切分规则一致；`<pre>`（type-6 可打断段落）与段落首行完整 `<code>`（type-7）分别按块处理，行内 `<pre>/<code>` 与段落续行 `<code>` 保持 inline——两条路径均有测试锁定，R-01/R-02 未回退。
- 交互检查：注释在 span 内、span 在注释后、注释块内容含 `<pre>`、4 空格缩进（indented code 对照）、tab 缩进、大写标签、`<code>` 带属性——行为均与 CommonMark 一致或落在既有近似内（见「既有近似」）。
- 未发现新的状态泄漏：`BlockState.HtmlTag/Comment` 的跨段落传播在无闭合标签时由第二趟 HTML 过滤兜底为 fail-closed（T1/T2 与「未闭合 `<code>` 块」样本在各版本一致为 REJECT）。

## Verification

| 场景 | 命令 | 对象 | 结果 | 证据日志 |
|---|---|---|---|---|
| 治理全量 checker | `pwsh -NoProfile -File tools/governance/check.ps1` | 工作区 = `83c422345` | **EXIT=0**；scope 15；`PASS (2 warnings)` | `review-r6c/checker-current.log` |
| 架构断言测试 | `python -B -m unittest discover -s tools/governance/tests -p test_architecture_assertions.py -v` | 同上 | **EXIT=0**；`Ran 31 tests`，`OK`（67.2s） | `unittest-current.log` |
| 22 场景矩阵 | `python -B -W ignore …/r6c_matrix.py` | 当前 | **EXIT=0**；22 场景 **0 mismatch** | `matrix22-current.log` |
| 22 场景矩阵 | 同上 + `FEA_CHECKER_SOURCE=chk-47734a336.ps1` | `47734a336`（r6b） | **EXIT=1**；**6 mismatch**（= E-01/E-02 六样本） | `matrix22-47734a336.log` |
| 22 场景矩阵 | 同上 + `chk-2f611e2aa.ps1` | `2f611e2aa`（r6a） | **EXIT=0**；0 mismatch | `matrix22-2f611e2aa.log` |
| 22 场景矩阵 | 同上 + `chk-1672f3c40.ps1` | `1672f3c40` | **EXIT=1**；3 mismatch（r5 P1/P2-1/P2-2） | `matrix22-1672f3c40.log` |
| 22 场景矩阵 | 同上 + `chk-504797ba7.ps1` | parent `504797ba7` | **EXIT=1**；11 mismatch | `matrix22-parent-504797ba7.log` |
| **新增测试判别力** | 同上 unittest + `FEA_CHECKER_SOURCE=chk-47734a336.ps1` | 父提交 `47734a336` | **EXIT=1**；`Ran 31 tests`，**FAILED (failures=8)**：`test_indented_block_openers_suppress_inline_parsing` ×4（pre-1/2/3sp、comment-2sp）、`test_inline_html_comment_backticks_form_code_span` ×2（single/double）、`test_inline_html_comment_backtick_does_not_swallow_next_field` ×1、`test_paragraph_leading_code_block_suppresses_inline_parsing` ×1 | `unittest-with-47734a336-checker.log` |
| Reviewer 21 用例探针 | `python -B -W ignore reviewer_r6c_probe.py` | 当前 | **EXIT=0**；21 用例 **0 mismatch**；R-03 的 3 个 observation probe 仍 REJECT | `probe21-current.log` |
| Reviewer r6b 18 预期样本 | `python -B -W ignore r6b_new_samples_r6c.py` | 当前 | **EXIT=0**；18 用例 **0 mismatch**；probe D1/D2/D3/D6 PASS、D4/D5 REJECT（均符合 CommonMark） | `new-samples-r6b18-current.log` |
| Reviewer R-01/R-02 专项 | `python -B -W ignore probe_extra_r6c.py` | 当前 / `1672f3c40` / parent | 当前 **4/4 OK**；`1672f3c40` 3 mismatch、parent 3 mismatch（预期内） | `probe-extra.log` |
| Reviewer E-01/E-02 家族 | `python -B -W ignore probe_family_r6c.py [checker]` | 当前 / `47734a336` | 当前 7/7 正确；`47734a336` 上 E1a/E1b PASS、E1d/E2a/E2b REJECT（r6b 回归复现） | `probe-family-current.log` / `probe-family-47734a336.log` |
| **Reviewer 自建新样本（22 期望用例）** | `python -B -W ignore r6c_new_samples.py [checker]` | 当前 / `47734a336` | 当前 **0 mismatch**；`47734a336` **11 mismatch** | `new-samples-current.log` / `new-samples-47734a336.log` |
| CommonMark 参考核验 | `python -B -W ignore commonmark_check_r6c.py`（markdown-it-py 4.2.0, commonmark preset） | — | 22 个新样本逐条核验：E1e–E1h 字段落 code span（应 REJECT）、E1i–E1l 可见（应 PASS）、E2c–E2k 可见（应 PASS）、REG 隐藏（应 REJECT）——与自建期望一致 | `commonmark-check-r6c.log` |
| 边界探针（既有近似判定） | `probe_edges.py` + T9/T10/未闭合块跨版本对比 | 当前 / `47734a336` / `2f611e2aa`（+`1672f3c40`/parent） | T1/T2/T9 与未闭合 `<code>` 块在各版本一致（REJECT，fail-closed，**既有近似**，非 r6c 引入）；T4/T8/T10 由 r6c 修正 | `probe-edges.log` / `probe-edges2.log` / `probe-unclosed-code-block.log` / `commonmark-edges.log` |
| 全 governance 测试目录 | `python -B -m unittest discover -s tools/governance/tests -p "test_*.py" -v` | 当前 | **EXIT=1**；`Ran 48 tests`，3 failures 全在 `test_residual_runtime_identity`（不调用 `check.ps1`，与 r6/r6b 同源的既有状态） | `unittest-all-governance.log` |
| 证据哈希核验 | `Get-FileHash` 对比 `r6-verification.md` §4 | — | `r6c_matrix.py`、4 份 r6c 矩阵日志、`r6c_e3_probe.py`/`r6c-e3-probe.log` 哈希**全部一致** | 本报告「固定指纹」 |

### Reviewer 自建新样本（22 期望用例；不复用作者样本）

| 组 | 样本 | 期望 | 当前 `83c422345` | 父提交 `47734a336` |
|---|---|---|---|---|
| E-01 | E1e 注释内含 HTML 标签与反引号 + 后续 span | REJECT | REJECT ✓ | PASS ✗（回归） |
| E-01 | E1f 多行行内注释含反引号 + 后续 span | REJECT | REJECT ✓ | PASS ✗ |
| E-01 | E1g 嵌套注释标记（首个 `-->` 结束） | REJECT | REJECT ✓ | PASS ✗ |
| E-01 | E1h 注释内双反引号 + 后续单反引号 span | REJECT | REJECT ✓ | REJECT |
| E-01 | E1i 注释在权威字段之后 | PASS | PASS ✓ | PASS |
| E-01 | E1j 注释内反引号不得吞掉下一行字段 | PASS | PASS ✓ | REJECT ✗ |
| E-01 | E1k 转义反引号 + 注释组合 | PASS | PASS ✓ | PASS |
| E-01 | E1l 注释 + ATX 标题边界 | PASS | PASS ✓ | PASS |
| E-02 | E2c/E2d/E2e/E2f `<pre>` 块 0/1/2/3 空格缩进 | PASS | PASS ✓ ×4 | 0sp PASS；1–3sp REJECT ✗ |
| E-02 | E2g/E2h `<!--` 块 0/3 空格缩进 | PASS | PASS ✓ ×2 | 0sp PASS；3sp REJECT ✗ |
| E-02 | E2i/E2j `<code>` 块 0/2 空格缩进 | PASS | PASS ✓ ×2 | REJECT ✗ ×2 |
| E-02 | E2k `<code class="x">` 段落首行块 | PASS | PASS ✓ | REJECT ✗ |
| 回归 | REG-R-01 段落续行 `<code>` 行 + 跨行 span | REJECT | REJECT ✓ | REJECT |
| 回归 | REG-R-02 行内 `<code>`/`<pre>` 内反引号 | REJECT | REJECT ✓ ×2 | REJECT |
| 回归 | REG `<code>示例</code>` 带尾随内容（非 type-7 块） | REJECT | REJECT ✓ | REJECT |
| 回归 | C 自由正文（`doc/STATUS.md`）跨行 span | PASS | PASS ✓ | PASS |

### 既有近似（非 r6c 引入，fail-closed，记录备查）

- T1「字段位于 `<code>` 块与 `</code>` 之间且含空行」、T2「`<code>` 未闭合后接 span」、T9「`</code>` 后同段落接 span」、以及「未闭合 `<code>` 块 + 空行 + 字段」样本：当前/`47734a336`/`2f611e2aa`/`1672f3c40` **一致为 REJECT**（仅 parent 为 PASS），属 type-7 HTML block 结束条件（空行 vs `</code>`）的既有近似，方向 fail-closed；markdown-it 显示这些样本中字段在渲染上可见，因此是已知的保守误拒。建议与 R-03 一并登记为 accepted limitation（不在本轮回归范围）。
- tab 缩进 `<pre>`：当前 REJECT，markdown-it 亦显示字段落入 code span（REJECT 正确），非回归。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-01 | P1（r6） | `check.ps1:463` | 行首 `<code>…</code>` 误判段落边界 → fail-open | 22 场景矩阵当前 0 mismatch；r6b A1–A6 复跑全 REJECT | — | **closed** |
| R-02 | P2（r6） | `check.ps1:398-409` | 行内 `<pre>/<code>` 内反引号被跳过 → fail-open | r6b B1–B4 复跑全 REJECT；`probe_extra` 4/4 OK | — | **closed** |
| R-03 | P2（r6） | `check.ps1:463` | setext/列表/块引用边界未识别 → fail-closed 误拒 | 21 用例探针 0 mismatch；3 个 R-03 probe 仍 REJECT（未扩大） | 登记为正式 accepted limitation | **accepted（维持）** |
| E-01 | P1（r6b） | `check.ps1:411-416` | 行内 HTML 注释未抑制解析 → fail-open（E1a/E1b）+ fail-closed（E1d） | 当前 `probe_family` 7/7 正确、父提交 5 处相反；22 场景矩阵 0/6；新增 3 条测试在父提交失败 | 已修（位置无关注释检测），并补测试 | **closed** |
| E-02 | P2（r6b） | `check.ps1:352-364`、`:418-436` | 块级 HTML 开行缩进与段落首行 `<code>` 块未识别 → fail-closed | 自建 0–3 空格 `<pre>`/`<!--`、段落首行 `<code>`（含属性/大写）全部 PASS；父提交 11 mismatch；新增 2 条测试在父提交失败 | 已修（`Test-BlockHtmlStart` + type-7 首行判定） | **closed** |
| **E-03** | **P2（新，非阻断）** | `FEA-00-R2-fix2\r6-verification.md` §3（证据归档） | §3「Reviewer 探针复跑」引用的日志未归档到实施者证据目录：`FEA-00-R2-fix2\` 下无 `probe-family-r6c.log` / `probe21-current.log` / `new-samples-current.log` / `probe-extra.log` 及其哈希；其中 `probe-family-r6c.log` 落在 **reviewer 证据目录** `review-r6b\`（23:33:42 写入，664 bytes，内容为 `probe_family.py` 对当前 checker 的运行结果），其余三个名字对应 reviewer 自己的日志。影响：§4.4 日志/哈希可追溯性不足、reviewer 证据目录边界被写入；不影响结论（本 Reviewer 已独立复现全部声明为真） | `Get-ChildItem`/`Get-FileHash` 全库搜索：`probe-family-r6c.log` 仅存在于 `agent-output\dsh\review-r6b\`；`FEA-00-R2-fix2\` 只剩 `r6c_matrix.py`、`r6c_e3_probe.py`、`r6c-e3-probe.log` 与 5 份矩阵日志（哈希均与 §4 一致） | 把实施侧复跑日志（带 EXIT）复制/重新生成到 `FEA-00-R2-fix2\` 并在 §4 记哈希；后续避免写入 reviewer 证据目录（`review-r6*`） | **open（非阻断）** |

## 残余风险与 NOT_RUN

- **NOT_RUN**：完整 CommonMark 规范测试套件；HTML block type 1/3/4/5（`<script>`/`<?`/`<!X`/`<![CDATA[`）、HTML block type-7 结束条件全形态、表格、脚注、缩进代码块（4 空格以上，已属 R-03 同族 accepted limitation）。
- **残余风险**：HTML/CommonMark 交互仍是近似实现；本轮已修正「注释位置无关性」「0–3 空格块开行」「段落首行 `<code>` 块」三条规则并有测试锁定，但 type-7 块**结束条件**（空行 vs `</code>`）仍是既有近似（T1/T2/T9 与未闭合 `<code>` 块，fail-closed，非本轮引入），建议随 R-03 一并登记。
- 全 governance 测试目录 3 个失败（`test_residual_runtime_identity`）与本变更无调用关系，属既有仓库状态。
- 产品功能、真实删除、迁移、并发、GUI 均 `NOT_RUN`（不属本变更范围）。
- 本报告只对 `reviewed_head = 83c422345` 有效。

## 独立性、仓库状态与证据位置

- 本 Reviewer 为 DSH 派发的独立上下文子 agent，**未参与**本变更的实现与返修；结论基于自建夹具与独立重跑，未采信作者日志。
- 全程只读仓库：未执行 `git add/commit/checkout/stash`；未修改任何 tracked 文件；`doc/reviews/FEA-00-dsh-r6.md`（`6d3ea16d…5c4166`）与 `doc/reviews/FEA-00-dsh-r6b.md`（`4a9dca25…0e7397`）字节未变（复核哈希一致）。
- 审查前 `git status --porcelain`：12 个既有 untracked（10 个既有文档 + r6/r6b 报告），无 tracked 修改；审查后新增本报告，共 13 个 untracked。
- 证据目录：`G:\CODEX\New Manga.workspace\agent-output\dsh\review-r6c\`（本报告引用的全部日志、探针脚本与自建夹具产物；临时夹具目录已清理）。
- 唯一非阻断记录问题见 Findings E-03（实施侧日志归档与 reviewer 目录边界）。
