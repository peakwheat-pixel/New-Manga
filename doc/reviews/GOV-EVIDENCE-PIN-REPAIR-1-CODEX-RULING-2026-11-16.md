---
id: GOV-EVIDENCE-PIN-REPAIR-1-CODEX-RULING
kind: review
reviewer: Codex（codex exec，model gpt-6-luna，reasoning xhigh，read-only 沙箱）
reviewed_by_context: 独立（未参与实施）
reviewed_head: 9f2db6463
decision: APPROVED_WITH_CONDITIONS
---

# EV-11 失效 pin 处置 —— Codex 书面裁定与 DSH 采纳

- **派发者**：DSH（Lead / Architect / Integrator）
- **裁定时间**：2026-11-16
- **裁定原文**：`G:\CODEX\New Manga.workspace\tmp-dsh\r3\codex-ev11-ruling.md`（2,272 B）
- **裁定者自述限制（如实保留）**：其 shell 无法启动（Win32 740）⇒ 未能独立重跑仓库命令，裁定基于 DSH 提供的事实。

## 裁定原文（逐字）

```
verdict: APPROVED_WITH_CONDITIONS  
Q1: D（C→B）：由 DSH 先按当前 Plan/Status 释放并冻结一张独立治理修复 Task，再授权对 `FEA-11-HOST-AUTH-2.md` append-only 追加 `EV-11-supersede` 行及说明；EV-11 原行逐字保留，不改历史计数。  
Q2: DSH 以 Lead 身份有权裁定并释放该修复 Task，但不能跳过当前 Task 激活与范围冻结；修复须由不同上下文的 Reviewer 独审，报告记录审查者身份与来源。必须留下：(1) 原 EV-11 行修复前后逐字相同的证据；(2) 新行使用可解析的完整 commit 和 64 位 SHA-256，且对 `git cat-file blob <commit>:doc/tasks/FEA-11-HOST-AUTH-3.md` 的内容计算 SHA-256 后等于 `e1c529bd6cc72b8de0648f9402ff03349bf8d17b00df951f9d95c9e638c959c0`；(3) 新说明明确旧 40 位值在本仓无对应 commit 对象、已被新行取代；(4) 范围 diff 证明只追加修订记录、未改历史证据或绝对计数；独立 Review 通过，`check.ps1` 对两张卡均 PASS，并附额外 SHA-256 语义巡检结果。修复后保留 `canonical_evidence_status: complete`，无需改摘要；以表下说明标明 supersession。  
Q3: 建议独立只读巡检（伪代码）：遍历 `doc/tasks/**/*.md` 的 Canonical Evidence 表，按表头解析六列/七列格式；对每个 canonical 行要求 SHA-256 匹配 `^[0-9a-fA-F]{64}$`；若 commit 非 `-`，要求 `git rev-parse --verify "<commit>^{commit}"` 成功，并比较该 commit 下 `<path>` blob 内容的 SHA-256 与表值；若无 commit，则要求路径存在且当前文件字节 SHA-256 与表值相等，否则报错。提交证据变更及 Task closeout 时运行受影响卡巡检；每个里程碑或每月运行全仓巡检。先作为独立命令纳入证据验收，不并入 `check.ps1`；只有基准测量证明耗时可接受后再考虑集成。  
风险与遗留:
- 修复 Task 完成前，EV-11 仍是失效 pin；现有 `check.ps1` PASS 不能单独证明该值是合法 SHA-256 或有效证据锚点。
- 下一步建议：由 DSH 建立并释放该治理修复 Task，再按上述条件执行和验收。本轮受 shell 无法启动（Win32 740）限制，未能独立重跑仓库命令；裁定以题述已实测事实和所给项目授权文本为依据。
```

## DSH 采纳（Lead 名义）

按裁定 **Q1=D（C→B）**执行：先建立并冻结独立治理修复卡 `GOV-EVIDENCE-PIN-REPAIR-1`（即本文件所在卡的来源），
在卡内再对 `FEA-11-HOST-AUTH-2.md` 做 **append-only** `EV-11-supersede` 追加；Q2 的四项证据要求逐条落到该卡 AC3；
Q3 的只读巡检先实现为 `tools/governance/audit_evidence_pins.py`，**不并入** `check.ps1`。

### 对 DSH 提供事实的更正（重要，不掩盖）

- 派发给 Codex 的题述把 EV-11 的值描述为「40 位十六进制、不是 shat256」，**这是错的**：
  实测长度 **64**（`4a7e1ca8bacfebcd74b5347eb1bed9b6fa8bd49e2e480ffc904296389413a82c`），是**合法长度**的 sha256。
  它真正的问题是：**本仓没有任何字节表示（commit blob / 当前工作树 / LF / CRLF）能复现该摘要**。
- 该更正不影响裁定的 Q1/Q2/Q3 结论（处置方式与证据要求与长度无关），但**影响事实认定**，故在采纳记录中显式更正，
  `check.ps1` PASS 不能证明该值有效这一条判断仍成立。

### 对裁定 Q3「巡检」的实测结果（本卡 AC1/AC2）

- 全仓 canonical 行：**7080**（665 张卡）；FAIL **445** 行 / **103** 张卡。
- 分类：COMMIT_NOT_FOUND=12, PATH_MISSING=109, SHA_MISMATCH=110, SHA_NOT_64_HEX=214
- WARN（历史形态可接受，不判缺陷）：blob 与工作树不一致但能对上某种签出表示 1671 行、
  纯工作树基准 1669 行。
- 结论：EV-11 **不是孤例**，但规模（445 行 / 103 卡）远大于裁定时的假设 ⇒ 采纳裁定「先建卡、再逐条判定」的路径，
  不进行任何批量重算或批量改写。

### 未采纳项

无。裁定的可执行条款全部采纳；仅对题述事实做上述更正。
