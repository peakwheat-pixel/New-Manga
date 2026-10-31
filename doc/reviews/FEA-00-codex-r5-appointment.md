# FEA-00 Codex r5 复审 Appointment 记录

日期：2026-10-31（Asia/Shanghai）。派发者：DSH。本文件是 Appointment 登记；不是 Review 报告本体，也不构成集成批准或实现授权。

## Appointment

| 项 | 值 |
|---|---|
| 被审对象 | commit **`1672f3c405ab8d420fa7c8854a565d212d1b0649`**（`fix(governance): mask multi-line code spans in architecture assertions`；parent `504797ba7`） |
| reviewer | Codex（独立新会话，未参与该修复的实施与提交） |
| reviewer_kind | `agent` |
| 通道 | `codex exec`（`codex-cli 0.162.0`），`-s danger-full-access -c windows.sandbox=unelevated -m gpt-6-luna -c model_reasoning_effort=xhigh`。选择 danger-full-access 是因为复审必须实际运行测试与隔离矩阵（只读沙箱无法创建隔离夹具，r4 已因此无法执行）；仓库只读由 prompt 约束，并以 `git status --porcelain` 零改动自证 |
| reviewer 会话 ID | `01a19248-6422-7380-92a1-82eadf5438d8` |
| 派发 prompt | `G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-00-R2-fix2/codex-r5-review-prompt.md` |
| 原始输出 | `G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-00-R2-fix2/codex-r5-review-result.md`（SHA-256 `984f02cb100239ec71f9f7292069eea53b6511e4fe41b616c72aded83c8f9043`） |
| 入库报告 | `doc/reviews/FEA-00-codex-r5.md`（原字节，同上 SHA-256） |

## r5 结论（转述）

`changes_requested`。

- **三条指定验证通过**：`check.ps1` EXIT=0 / PASS（scope 15）；16 个架构断言测试 OK；13 场景矩阵 0 mismatch。
- **P1**：`check.ps1:415` —— HTML 处理（行内 `<pre>`/`<code>`）先于跨行 code span 识别，先切断段落，导致跨行双反引号内的 AD-003 sentinel 在组合场景被接受（实测 PASS/EXIT=0，漏报）。
- **P2-1**：`check.ps1:349` —— 未识别反斜杠转义的反引号（`\``），会把 `历史说明：\`literal` 与 sentinel 值配对，误屏蔽合法 sentinel（实测预期 PASS、实际 REJECT）。
- **P2-2**：`check.ps1:440` —— 段落切分只识别空行，未把 ATX 标题（`## …`）当作块边界；跨标题的反引号被错误配对并屏蔽后续 sentinel（实测预期 PASS、实际 REJECT）。
- **P2-3**：`pre-change-scope.md:9` 的基线描述与固定 base 不一致：parent `504797ba7` 的 `$staticFiles` 实为 **14**（不是 12）；`checker-before-r5.ps1`/`test-before-r5.py` 是工作区 21:30 快照（`04d9373e…`/`b4c26ba0…`），并非 parent blob（`13e08555…`/`4d639ba7…`）。因此旧矩阵只证明"在 21:30 版本上加入跨行修复"的增量，不能单独代表 commit `1672f3c40` 相对 parent 的完整基线。

## 仓库零改动核验

复审结束时其 `git status --porcelain` 仅列出 7 个既有 untracked 文件（Fluent 设计 2 份、FEA-00 r2/r3 报告、r2 remediation handoff、r4 报告与 Appointment）；DSH 复核同一结果，无跟踪文件被修改。

## 处置状态

P1 与三条 P2 尚未修复；P2-3 的证据更正由 DSH 负责。修复后须重新固定 base/head、重跑正负例与完整测试，并由未参与修复的 Reviewer 再次复审。本记录不替代上述步骤。
