## decision=approved

**结论**：N-01..N-05 五条文档缺口全部收口，且未引入新的实质性（P0–P2）问题。C 表格外另附 2 条 P3 advisory（不影响批准）。

### N-01..N-05 逐条核对

| ID | 结论 | 依据（一句） |
|---|---|---|
| N-01 | **通过** | Handoff 正文已无「diff 仅上述 8 文件」类断言：全文 grep `8 文件` 仅命中 §7 处置表 `:120` 历史 finding 的**引述**（`Handoff 变更面"8 文件"计数不实`），非现行声明；`:19` 与 `:62` 均为 12 文件口径，相互一致。 |
| N-02 | **通过** | `:19` 给出 `git diff --name-only a8b94df1..2a1078b6` = **12 文件 = 代码 4 + 证据 6 + 治理 2**，与所列清单逐项自洽：代码 4（viewmodel.py、test_viewmodels.py、test_qml_contract.py、test_bootstrap.py）、证据 6（目录 glob 恰为 `probe-heartbeat-leak-fixed.{py,log}` + `targeted-suite.log` + `full-suite.log` + `targeted-suite-r2.log` + `full-suite-r2.log`）、治理 2（Task + Handoff），全部落在 Task `:57-60` 的 allowed 清单内。 |
| N-03 | **通过** | R2 重跑日志已有双指针：`AC5:61` 分列 R1 `targeted-suite.log`/`full-suite.log` 与 R2 **`targeted-suite-r2.log`/`full-suite-r2.log`**；§3 表 `2b`/`3b` 两行分别指向两份 `-r2.log`，`-r2.log` 引用数由 0 → 4。 |
| N-04 | **通过** | frontmatter `:7` 已加 `reviewed_head: 2a1078b6（R2 交付，当前被审固定点）`；`:18` Commit 链补全为 `a8b94df1 → 6e37f05d → 3ce82240 → 528ba4d4 → 2a1078b6`，五个 hash 均为实际前缀，无缺环。 |
| N-05 | **通过** | 计数与枚举一致：`:38` 由「4 处」改为「**5 处落点**」，其枚举恰为 5 项（reader fixture、qml_contract 三个 fixture、bootstrap finally），R2 增补的第 6 项在 `:42` 显式标注「R2 补 try/finally」；`AC3:59` 由「5 处」改为「**6 处落点**」并列出该项，两处不再互相矛盾。 |

### 补充核对（复核要求第 1 条）

- **diff 范围**：当前 HEAD=`f93ea667`（`refs/heads/agent/zcode/DIAG-READING-EXPORT-001-FIX-B-reader-heartbeat-lifecycle`），reflog 显示其为 `2a1078b6` 的**直接子提交**、R3 唯一提交，commit message = `docs(DIAG-READING-EXPORT-001-FIX-B): R3 docs-only per DSH re-review -- N-01..N-05 counting/pointer/frontmatter fixes`（未声明任何代码/测试/证据产物）。全仓 mtime 排序中，Handoff 为**最新文件**，其下依次为 R2 的 `full-suite-r2.log`、`targeted-suite-r2.log` 与 R2 触碰的 `test_viewmodels.py`、`viewmodel.py`——即除本 Handoff 外无更晚写入的受管文件，与「R3 仅 Handoff 一文件」相符。
- **环境限制（如实披露）**：本会话 `pwsh` 通路在会话启动阶段即被沙箱阻断（每条命令均返回 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\DIAG-FIX-B-zcode)`），`danger-full-access` 升级亦因「无审批通道」失败，故**未能以 git 命令逐 hunk**核验 `2a1078b6..f93ea667`。上述判定改用文件系统级证据（worktree `HEAD`、reflog、packed-refs、提交对象可读性、全仓 mtime 排序、内容级 grep/枚举一致性）合成，与上一轮 DSH 复核在同类阻断下的处置方式一致。第 1 条因此是**内容与文件面通过、命令级 BLOCKED**，不构成对 N-01..N-05 结论的影响。
- **R2 增量自证**：mtime 最新 5 个受管文件（Handoff、`targeted-suite-r2.log`、`full-suite-r2.log`、`test_viewmodels.py`、`viewmodel.py`）与 §7 尾 `:125` 声明的 R2 5 文件清单逐项吻合，该清单可信。

### 非阻断 advisory（P3，建议下一轮或集成面顺手处理，不影响本次批准）

- **A-01**：`:120` §7 R-05 行处置文本仍写「改分组口径"10 文件 = 代码 4 + 证据 4 + 治理 2"」，与 `:19` 现行 12 文件 / 证据 6 口径冲突（R-05 的修正值本身在 R2 已失效）。该行属历史记录，但未标注「随后由 R3 更正为 12」，读者可能误读。
- **A-02**：frontmatter `:7` 声明 `reviewed_head: 2a1078b6（…当前被审固定点）`，而含该声明的 Handoff 内容本身位于其后继提交 `f93ea667`；即 R3 文档修订**未被任何 reviewed_head 绑定**（§7 已明确 R3 为文档收口，故本轮按 docs-only 认定不使既有批准失效）。建议 Codex 集成时以「`2a1078b6` = 内容批准点 + `f93ea667` = 文档收口点」双点记录，避免绑定窗口歧义。

**推荐下一步（基于当前仓库状态）**：由 Codex（Integrator）在集成面复验并合并 `f93ea667`，记录「内容批准 `2a1078b6` / 文档收口 `f93ea667`」双点绑定后关闭 FIX-B；A-01 一行级修正可作为集成面的可选随附提交。
