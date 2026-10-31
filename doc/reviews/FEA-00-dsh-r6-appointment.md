# FEA-00 DSH r6 复审 Appointment 与 DSH 实施记录

日期：2026-10-31（Asia/Shanghai）。派发者：DSH（Lead / Architect / Integrator）。本文件是 Appointment 登记与 DSH 实施/核验记录，不是 Review 报告本体，也不构成集成批准、Task 释放或实现授权。

## Appointment

| 项 | 值 |
|---|---|
| reviewer | `reviewer-r6`（DSH 派发的独立上下文子 agent，未参与本变更实现） |
| reviewer_kind | `subagent` |
| reviewer_source | Agent Teams `spawn_teammate`，fresh context；由 DSH 主会话派发 |
| 独立性依据 | 2026-10-31 用户裁决：不再要求非作者或不同角色；同一 Agent 会话/实例不得自审，作者可派发独立上下文子 agent 审查 |
| 通道 | 本会话 Agent Teams（`spawn_teammate`，独立上下文） |
| 被审对象 | commit `2f611e2aa`（`tools/governance/check.ps1`、`tools/governance/tests/test_architecture_assertions.py`）；parent `1672f3c40` |
| 固定基线 parent | `504797ba7`（`1672f3c40^`），`check.ps1` blob `13e08555…`，测试 blob `4d639ba7…` |
| 审查报告 | `doc/reviews/FEA-00-dsh-r6.md`（由 reviewer-r6 写入） |
| 证据目录 | `G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-00-R2-fix2/` |

## 用户本轮要求（原文要点）

1. 重构 `Get-AuthorityLines`：先按原始段落（空行 + ATX 标题为块边界）识别并屏蔽跨行 code span，再做 fence/HTML 处理（关闭 P1、P2-2）；
2. 扫描反引号时识别反斜杠转义（奇偶）——转义反引号不开启 code span（关闭 P2-1）；
3. 以 parent `13e08555…`（`git show 1672f3c40^`）重跑旧基线矩阵并更新 `pre-change-scope.md`，明确 parent 为 `504797ba7`、`$staticFiles` 14、scope 15（关闭 P2-3）；
4. 补 3 个组合正负例（行内 `<pre>` × 跨行 span、转义反引号正例、ATX 标题边界正例），跑完整 checker 与全部测试，提交新 commit，再派子 Reviewer 复审。

## DSH 实施与固定证据

| 项 | 值 |
|---|---|
| 提交 | `2f611e2aa`（fix(governance): handle escaped backticks and block boundaries in authority parsing） |
| 提交范围 | 仅 `tools/governance/check.ps1`（+126/−? → 167 insertions、23 deletions 两文件合计）与测试文件；无其他 tracked 修改 |
| 提交后 `check.ps1` blob | `add3cf30c08f746836aaa70926ed8ffa25df6f93` |
| 提交后测试 blob | `723f71ed85a9c3d2daa533c53e494434c753f9a4` |
| 工作区文件 SHA-256 | `check.ps1` `5b7b36c3…d0eda7cb`；测试 `b295fa9a…5afb9d7f` |
| `pre-change-scope.md`（r6 修订） | parent 绑定 `504797ba7`；`$staticFiles` 14；scope 15；16 场景矩阵 |
| parent 基线矩阵 | `baseline-matrix-parent-r6.log`：16 场景 **9 mismatch**（原 13 场景 8 mismatch） |
| HEAD 基线矩阵 | `baseline-matrix-head-1672f3c40.log`：16 场景 **3 mismatch**（= r5 P1/P2-1/P2-2） |
| 修复后矩阵 | `final-matrix-r6-16.log`：16 场景 **0 mismatch** |
| 完整 checker | `EXIT=0`，`PASS (2 warnings)`，scope 15 |
| 全部测试 | `Ran 25 tests ... OK`，`EXIT=0` |
| 额外专项探测 | `r6_probe.py`：6 组 CommonMark 交互，0 unexpected |

## 边界

- reviewer-r6 的结论以 `doc/reviews/FEA-00-dsh-r6.md` 为准；本 Appointment 不预判其 decision。
- 本轮只覆盖治理检查器静态判别；产品功能、真实删除、迁移、并发、GUI 均 `NOT_RUN`。
- 提交后未 push；Reviewer 复审结果与 findings 处置由 DSH 记录。

## r6b 返修与复审（2026-10-31 续）

首次复审 `doc/reviews/FEA-00-dsh-r6.md`（reviewed_head `2f611e2aa`，decision **`changes_requested`**）发现：

| finding | 级别 | 摘要 |
|---|---|---|
| R-01 | P1 | `$isBlockBoundary` 把行首 `<code>…</code>` 当段落边界；`<code>` 是 type-7 HTML block，不能打断段落。`2f611e2aa` 相对 `1672f3c40` 引入判别力回归（漏报） |
| R-02 | P2 | 掩码扫描跳过行内 `<pre>/<code>` 之间的内容，但 inline raw HTML 不抑制 inline 解析，导致漏报（继承缺口） |
| R-03 | P2 | 段落边界未识别 setext/列表/引用，合法 sentinel 可能误报 REJECT（fail-closed；继承缺口） |

DSH 返修：commit **`47734a336`**（parent `2f611e2aa`）：

- `$isBlockBoundary` 移除 `<code>`（保留 `<pre>`/`<!--`/fence/ATX）；
- `Mask-ParagraphCrossLineCode` 的 HTML 检测限定在行首、且只识别块级 `<pre>`；
- 新增 2 条回归测试（行首 `<code>` 不结束段落；行内 HTML 中反引号仍开启 span），25 → 27；
- 返修中自纠一次：HTML 检测正则去掉捕获组后 `$BlockState.HtmlTag = $open.Groups[1].Value` 变为空串，导致 `<pre>` 块状态失效；改为显式 `'pre'` 后修复。
- **R-03 裁定**：accepted limitation（fail-closed、无安全绕过、继承自 `1672f3c40`、超出用户本轮「空行 + ATX 标题」冻结范围），记录于 `r6-verification.md` §5。

返修后 DSH 自验证：checker `EXIT=0` `PASS (2 warnings)`；27/27 tests `OK`；16 场景矩阵 0 mismatch；Reviewer 的 R-01/R-02 探针 4/4 OK、21 用例探针 0 mismatch。

r6b 复审：同一 `reviewer-r6`（未参与返修）独立复审新 head `47734a336`，报告写入 `doc/reviews/FEA-00-dsh-r6b.md`（不覆盖 r6 报告原字节）。

## r6c 返修与第三轮复审（2026-10-31 续）

r6b 复审（`doc/reviews/FEA-00-dsh-r6b.md`，reviewed_head `47734a336`，decision **`changes_requested`**）的 disposition：R-01 **closed**、R-02 **closed**、R-03 **accepted**；新增 **E-01（P1，fail-open + fail-closed）** 与 **E-02（P2，fail-closed）**。

DSH 返修：commit **`83c422345`**（parent `47734a336`）：

- **E-01**：`<!--` 检测恢复为**位置无关**（HTML 注释在行内任意位置都抑制其内容的 inline 解析）；行内 `<pre>`/`<code>` 标签仍按 inline 处理。
- **E-02 ①**：新增 `Test-BlockHtmlStart`，块级 HTML 开行允许 **0–3 空格**缩进（与段落切分 `^ {0,3}` 一致）。
- **E-02 ②**：段落首行的**完整 `<code>` 标签行**按 type-7 HTML block 处理；行内 `<code>` 与段落续行 `<code>` 仍按 inline 处理（保持 R-01/R-02 关闭）。
- 测试 27 → **31**；矩阵扩至 **22 场景**（16 + E-01/E-02 六样本）；新增 `r6c_matrix.py`、`r6c_e3_probe.py`。

返修后 DSH 自验证：checker `EXIT=0` `PASS (2 warnings)`；31/31 tests `OK`；22 场景矩阵当前 **0 mismatch**（r6b `47734a336` 6、`2f611e2aa` 0、`1672f3c40` 3、parent `504797ba7` 11）；Reviewer E 家族探针 7/7、E3 探针 8/8、21 用例 0 mismatch、R-01/R-02 4/4；新测试在 r6b checker 上 **8 failures**。

r6c 复审：同一 `reviewer-r6` 独立复审 `83c422345`，报告 `doc/reviews/FEA-00-dsh-r6c.md`。

## r6c 复审结论与 E-03 处置（2026-11-01）

- 报告：`doc/reviews/FEA-00-dsh-r6c.md`（SHA-256 `67d72db3…7b5c1b`，reviewed_head `83c422345`），decision **`approved`**。
- disposition：**E-01 closed**、**E-02 closed**、**R-01 closed（保持）**、**R-02 closed（保持）**、**R-03 accepted（维持）**；无 P0/P1/P2 代码缺陷。
- **E-03（P2，非阻断，证据归档）**：已处置——实施侧探针日志归档到 `G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-00-R2-fix2/` 并补 `EXIT`：`probe-family-r6c.log`（`db4408f8…`）、`probe21-current.log`（`559b4290…`）、`new-samples-current.log`（`b4014481…`）、`probe-extra.log`（`4ecb5db8…`）；后续不再写入 `review-r6*` reviewer 证据目录。哈希同步登记在 `r6-verification.md` §4。
- Reviewer 记录的 type-7 `<code>` 块结束条件近似（空行 vs `</code>`，`1672f3c40` 起一致）并入 **R-03 accepted limitation**，记录在 `r6-verification.md` §5。
- 集成状态：`83c422345` 已在 `main`，**未 push**；推送由 DSH 按用户授权决定。独立复审已确认该 head 可交集成。

## 收口记录（2026-11-01）

按 r6c 报告的建议完成 P0-1～P0-4：

| 项 | 处置 |
|---|---|
| P0-1 判别力 artefact | `unittest-r6c-discriminative-31.log`（环境头 + `EXIT=1` + `Ran 31 tests / FAILED (failures=8)`），哈希 `359a8566…`，登记于 `r6-verification.md` §4 |
| P0-2 过期表述 | `r6-verification.md` §3 标题改为「已提交 `83c422345`」；§5 末条改为已复审 approved 与 disposition 记录；**未改 `check.ps1`**（保持已审字节） |
| P0-3 集成验证 | `integration-checker.log`（EXIT=0 / PASS 2 warnings）、`integration-unittest-31.log`（EXIT=0 / Ran 31 OK）、`integration-matrix22.log`（EXIT=0 / 22 场景 0 mismatch），哈希见 `r6-verification.md` §4；集成方式为 main 就地包含该 commit，无来源分支合并动作 |
| P0-4 归档提交 | commit **`b6bdb3877`**（11 个 Review/Appointment/Handoff 文档，+1132 行）；归档前后代码 blob 未变（`dd800c58…` / `161435c9…`）；归档后 `check.ps1` 复验 EXIT=0（`post-archive-checker.log`） |

`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md`、`doc/design/FLUENT_MANGA_USER_CONCEPT_2026-10-30.md` 属产品设计线，保持 untracked，未混入本次归档。`main` 仍无 upstream，未 push。
