---
id: GOV-EVIDENCE-PIN-REPAIR-1-AC5-REVIEW
kind: review
reviewer: pin-exc-reviewer（DSH 子 agent，独立上下文、只读）
reviewer_kind: subagent
reviewed_head: 881c6cac28faef5796599c11b550de9af10247f8
base_commit: ce66a0df18e6095fe41634149c478aa8d35403e6
decision: rejected
---

# 独立 Review：GOV-EVIDENCE-PIN-REPAIR-1 整卡 AC5

verdict: **REJECTED**
reviewed_head: `881c6cac28faef5796599c11b550de9af10247f8`
reviewer: `pin-exc-reviewer`（DSH 子 agent，**独立上下文**，未参与该卡实施或返修；只读复核，只写本文件）
identity: 未参与 AC1–AC7 的实施、登记或门禁修改；本节结论只对该 head 有效。

## 1. 方法与实测

环境：PowerShell 7.6.8 / Python 3.14.6 / git 2.52.0.windows.1；复核开始时 `git status --porcelain` 为空。
所有临时探针均在系统 temp 目录，结束后删除；未修改仓库其它文件。

| # | 命令或方法 | 结果 |
|---|---|---|
| M1 | `git rev-parse 881c6cac2` / `git diff --stat ce66a0df1 881c6cac2` | head 匹配；diff 15 文件，含 9 张卡、GOV 卡、handoff、check.ps1、audit 工具、registry、batch4 log |
| M2 | `pwsh -NoProfile -File tools/governance/check.ps1` | PASS (3 warnings)，EXIT 0，1124 ms |
| M3 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-EVIDENCE-PIN-REPAIR-1.md` | PASS (3 warnings)，EXIT 0，1065 ms |
| M4 | 对 33 张有登记项的卡逐一跑 `check.ps1 -TaskPath`（Python 循环） | **17 PASS / 16 FAIL**；用户抽查的 8 张（FEA-GOV-4/5/6/10、FEA-05-PORT-1/WIRE-1、FEA-11-HOST-AUTH-2、P02PRE-R1H-H2-COLLECTOR）**全部 PASS** |
| M5 | `python -B tools/governance/audit_evidence_pins.py --json <temp>`（全仓） | 7,096 行；`FAIL 4 / EXEMPTED 82 / NOT_ENFORCED 15 / WARN 269`；FAIL=2 条 FEA-05-PORT-1 多路径 + 2 条空壳行；NOT_ENFORCED=15 条 P02-NEW-TIME-X6 |
| M6 | `python -B -m unittest tools.governance.tests.test_evidence_eol_forms -v` | `Ran 7 tests in 158.861s` → OK |
| M7 | registry 独立 JSON 校验（5 个既有条目 + 114 条全量） | 114 条、每条 12 字段、id/fingerprint 唯一、无通配符；类型 PATH_MISSING 51 / SHA_MISMATCH 46 / COMMIT_FORMAT 13 / SHA_MULTI 2 / COMMIT_PATH_MISSING 2 |
| M8 | AC3 独立重算 + 基线对照 | 三条 `-supersede` 的 blob SHA-256 逐字等于原行值；EV-11/12/13 原行相对 `8db997f9` 逐字节未变 |
| M9 | `git diff ce66a0df1 881c6cac2 -- doc/tasks/*.md` | 9 张卡均为新增（Resource 表/新证据行/AC1 勾选），无既有证据行删除；FEA-GOV-5 的 3 处删除是 AC 行 |
| M10 | `git diff ce66a0df1 881c6cac2 -- tools/governance/check.ps1` / `audit_evidence_pins.py` | 只新增/改写例外资格、多摘要键、COMMIT_FORMAT/SHA_MULTI 钩子及工具映射；无测试文件改动 |

## 2. 六问逐项结论

### Q1 AC3（EV-11/12/13 supersede）：**PASS（行本身）**

- FEA-11 卡 113–115 行：三条 `-supersede` 的 commit 均为 `5cbec0e822af224809f3d898c82fe30a025b5ab1`，
  sha256 分别为原行记录值 `4a7e1ca8…` / `60a3d02a…` / `cdc51f96…`；`sha256(git cat-file blob 5cbec0e8:<path>)`
  三条逐字相等（M8）。
- 原 EV-11/12/13 三行相对 `8db997f9…` 的基线字节**完全未变**（M8）；改的是追加行与表下说明。
- 但：GOV 卡 69–70 行的 AC3 定义仍写“表下说明「旧值在本仓无任何字节表示可复现，已被取代」”，与
  5cbec0e8 可复现事实矛盾；AC3 证据日志 `verification/.../ac3-ev11-supersede-2026-11-16.log` 仍以 `head: 8db997f94`
  和旧锚点 `f1a2e8805a…` / `53ce9d55…` / `5ec365f…` 记录，与当前 FEA 卡的 `5cbec0e8…` 不一致（见 P1-4）。

### Q2 AC7（EOL 门禁）：**FAIL（字段“未变”被放宽；混合行尾与七列分支本身 PASS）**

- 混合行尾：`Get-ByteForms`（`tools/governance/check.ps1:260-300`）对同时含 CRLF 与裸 LF 的字节只返回 `Raw`，
  不产生 LF/CRLF 派生形态；含 NUL 或裸 CR 返回 `null`。**PASS**；7 项 EOL 测试全过（M6）。
- 七列显式 basis 分支（`check.ps1:1091-1129`）在 AC7 提交 `86add17cf→35f87d915` 与 final diff 中均未改动；
  `BLOB/WORKTREE/EXTERNAL_SHA256` 仍只比原始字节。**PASS**。
- 但 `Get-BaselineRowEligible`（`check.ps1:359-380`）新增：
  `$commitOk = ($baseC -eq $nowC) -or (($baseC -notmatch $hexRe) -and ($nowC -notmatch $hexRe))`，
  即任何两种“非十六进制 commit”都被视为未变（如 `-` ↔ `(见提交)`）。这违反 AC7 条件 4 的“字段未变”，
  使行尾推断资格可以在 commit 单元格文本已改写时仍然成立（当前 13 条 COMMIT_FORMAT 行恰好逐字相同，未触发）。
  **FAIL**（P2-1）。

### Q3 AC6（例外通道）：**FAIL（结构 PASS；三重校验/逐字一致 FAIL；Resource 不可豁免 PASS）**

- 114 条全部一行为一指纹：12 字段精确、id/fingerprint 唯一、无 `*?[]` 通配、无按类放行；类型
  PATH_MISSING 51 / SHA_MISMATCH 46 / COMMIT_FORMAT 13 / SHA_MULTI 2 / COMMIT_PATH_MISSING 2（M7）。**PASS**。
- 三重校验：`Test-EvidenceExceptionEligibility` 只在命中失败行时由 `Get-EvidenceException` 调用
  （`check.ps1:103-145, 180/199/207`），不是对 114 条逐条预检。`P02-NEW-TIME-X6` 的 **15 条**登记项
  （EXC-BATCH2-044…058）所在卡基线与当前均为 `status: superseded`，而资格/当前状态只接受
  `done`/`closed_with_limitations`（`check.ps1:105-110, 155-157`）——这 15 条永远无法生效，巡检也标为
  `NOT_ENFORCED 15`（M5）。因此“114 条均已三重校验”不成立。**FAIL**（P1-2）。
- 字段逐字一致：`Test-EvidenceExceptionEligibility` 的 commit 比较把任意非十六进制文本视为相等
  （`check.ps1:127`）；sha 比较从单元格中**抽取** 64 位摘要后按列表比较（`check.ps1:130-138`），
  不绑定原始单元格字节/分隔符。这违反裁定 Q1=A“commit 原文逐字相同”与 Q2=A/Q4.1“摘要列表绑定原始单元格字节”。
  当前 114 条的 baseline 字段恰好都逐字相同，但门禁本身已弱于此要求。**FAIL**（P1-3）。
- Resource：Resource Manifest 校验仍在独立分支（`check.ps1` Resource 段，无 `Get-EvidenceException`）；
  本批对 Resource 的修改是卡片单元修正，未登记例外。**PASS**。
- 测试：`test_evidence_exceptions.py` 仍只有 10 个既有用例，**没有** COMMIT_FORMAT、SHA_MULTI、空壳行/占位行、
  摘要列表顺序/分隔符/“列表中已有匹配摘要”的用例；裁定 Q4.5 的新增测试要求未满足（P2-3）。

### Q4 AC4（逐条判定）：**FAIL**

- 用户抽查的 8 张卡全部 PASS（M4）；batch4 的 9 张卡在样例中均 PASS。**这部分 PASS**。
- 但“门禁口径下 **34 张受影响卡全部 PASS**”在完整 `check.ps1 -TaskPath` 口径不成立：33 张有登记项的卡中
  **16 张 FAIL**（如 `DISPLAY-PERF-DECISION-1` 5 errors、`FEA-12-PREREQ-1` 1 error、`P02-NEW-TIME-X6` 1 error、
  `P02PRE-R1H-H2-RUN` 3 errors；均为 Resource/ integration_commit / evidence_dir 等其他门禁项，不是证据 pin）。
  该说法即使只想表达“证据 pin 口径”也应限定，不能写成完整门禁全绿（P2-2）。
- 2 条多路径行（`FEA-05-PORT-1.md:107-108`）：`check.ps1 -TaskPath` PASS（10 warnings），但 4 条
  EXEMPTED（EXC-BATCH6-111…114）承担了 COMMIT_PATH_MISSING + SHA_MULTI；巡检仍 FAIL 2（PATH_MISSING）。
  “多路径行门禁已过”成立（经由例外，不是原生通过）；但 registry 理由“真实文件另由 -supersede/新行确认”
  不实——卡内没有针对 `IHostController.cs`/`HostController.cs`/`NullHostController.cs` 或两个测试文件的
  独立新行/ supersede 行，`EV-INTAKE-*` 是证据目录补登（P1-4/P2-5）。
- 2 条空壳行（`FEA-05-WIRE-1.md:126`、`FEA-GOV-6.md:67`）：巡检 FAIL 2（SHA_NOT_64_HEX）；`check.ps1` 的
  `Get-TableRows` 把首格 `-` 当作表分隔符过滤（`check.ps1:244-249`），因此两个卡完整门禁 PASS，而
  `check.ps1:1077` 的“整行为占位符”结构错误对这两行**不可达**。裁定 Q3 明确要求“判为行结构非法并保持错误”；
  现在的“PASS”是跳过，不是保留错误。**FAIL**（P1-1）。
- 15 条 P02-NEW-TIME-X6 登记项不在“剩余 4 条”里，却在 registry 中占 15/114；AC4 的“16 → 4”未计入，
  handoff/log 也未披露这一堆死亡条目（P1-2）。

### Q5 无绿洗：**FAIL（历史证据字节 PASS；门禁/陈述 FAIL）**

- 历史证据行字节：final diff 的 9 张卡只有新增（Resource 表、EV-INTAKE/EV-GOV6 行、FEA-GOV-5 AC1 勾选），
  无既有证据行删除或改写；FEA-GOV-5 的 3 处删除是 AC 行（M9）。**PASS**。
- 但本轮 `check.ps1` 的 commit 非十六进制归一化、sha 摘要抽取（P1-3），以及空壳行被 parser 跳过（P1-1）
  都属于放宽/绕过，不是“只收紧或只对齐”；batch4 log 19 行的“只收紧或只对齐”不实。
- 测试：final diff 无测试文件改动；`test_evidence_exceptions.py` 的 EV-01→EV-11 替换是 AC7 后 EV-01 原生通过
  导致的状态更新，不是删断言；但新增钩子/空壳行无测试（P2-3）。
- 结论：没有删测试/改历史证据字节；但存在门禁放宽与不实陈述，不能判“无绿洗”。**FAIL**。

### Q6 新问题（false statements）：**FAIL**

- `doc/tasks/GOV-EVIDENCE-PIN-REPAIR-1.md:70`：AC3 仍称“旧值在本仓无任何字节表示可复现”——已被
  `5cbec0e8` 的 blob SHA-256 反证。
- `doc/handoffs/NEXT-SESSION-STARTER.md:246`：“34 张受影响卡全部 PASS”（完整门禁 16/33 FAIL）；
  `:251`：“真正问题是本仓无任何字节表示能复现它”（同上反证）。
- `verification/.../ac4-batch4-2026-11-17.log:19`：“只收紧或只对齐”（commit 归一化是放宽）；
  `:30`：“空壳行不再阻断”（实际是 parser 跳过）；`:33`：“34 张…全部 PASS”（同上）。
- registry `EXC-BATCH6-112/114` 的 reason：“真实文件另由 -supersede/新行确认”——卡内无这些文件的新行/ supersede。
- `ac3-ev11-supersede` log 仍以 `head: 8db997f94` 和旧锚点 `f1a2e880…`/`53ce9d55…`/`5ec365f…` 记录，
  与当前 `5cbec0e8…` 的 supersede 行不一致。
- batch4 log `# head: ce66a0df1`（本批提交是 881c6cac2）是陈旧 metadata（次要）。

## 3. Findings

| ID | 级别 | 位置 | 问题与影响 | 复现证据 | 建议 |
|---|---|---|---|---|---|
| P1-1 | **P1** | `check.ps1:244-249`（`Get-TableRows`）、`:1077`；`FEA-05-WIRE-1.md:126`、`FEA-GOV-6.md:67` | 首格 `-` 的空壳行被当表分隔符过滤，`行结构非法` 检查不可达；两卡完整门禁 PASS 是跳过而非按 Q3 保持错误，巡检仍 FAIL 2。 | `check.ps1 -TaskPath FEA-05-WIRE-1/FEA-GOV-6` → PASS (3w)；巡检 → 两行 `SHA_NOT_64_HEX`；`Get-TableRows` 过滤首格 `^[-: ]+$`。 | 在 `Get-TableRows` 前保留原始行，或对“整行占位符”单独扫描；门禁应报错，不能静默过滤；补测试。 |
| P1-2 | **P1** | `evidence-pin-exceptions.json` 中 `EXC-BATCH2-044…058`；`check.ps1:105-110,155-157` | 15 条登记项在 `P02-NEW-TIME-X6`（基线/当前 `superseded`）中，资格只接受 done/closed，永远无法生效；114 条并非都可三重校验，AC4 的“16→4”未计入。 | 巡检 `NOT_ENFORCED 15`；baseline/current status=superseded；`Test-EvidenceExceptionEligibility` 只在命中时调用。 | 删除这 15 条；或在裁定中明确 superseded 是否算“终态”并让资格/当前状态一致；AC4/handoff 如实披露。 |
| P1-3 | **P1** | `check.ps1:127,130-138` | 资格校验把任意非 hex commit 视为相同，并从 sha 单元格抽取摘要按列表比较，不绑定原始单元格字节；违反裁定 Q1=A“commit 原文逐字相同”、Q2=A/Q4.1“绑定原始单元格字节”。当前 114 条字段恰好逐字相同，但门禁已弱于此要求。 | `Test-EvidenceExceptionEligibility` 的 `$commitOk` 归一化；`$shaOk` 用 `[regex]::Matches` 抽取 64-hex 后 join。 | 恢复 commit 逐字比较（COMMIT_FORMAT 用 raw commit）；SHA_MULTI 保存/比较原始 sha 单元格字节与顺序；补负例（分隔符/顺序/已匹配摘要）。 |
| P1-4 | **P1** | GOV 卡 70；handoff 246/251；batch4 log 19/30/33；registry 多路径 reason；AC3 log | 多处 false statement：AC3 仍称“无任何字节可复现”；handoff 称 34 卡全 PASS、EV-11 无字节；batch4 称空壳不再阻断/只收紧闭/对齐；多路径 reason 称真实文件已由新行确认。 | 见上文行号；`5cbec0e8` 可复现；完整门禁 16/33 FAIL；卡内无多路径文件的独立新行。 | 逐条更正；把“34 卡全 PASS”限定为证据 pin 口径或撤回；AC3 改为“5cbec0e8 溯源补全”，并更新 AC3 log 锚点。 |
| P2-1 | P2 | `check.ps1:377`（`Get-BaselineRowEligible`） | 任何非 hex commit 文本变化仍判“字段未变”，AC7 行尾推断资格被放宽（当前 13 条 COMMIT_FORMAT 行未触发）。 | `$commitOk` 的 `-notmatch $hexRe` 双非 hex 分支；AC7 裁定条件 4“字段未变”。 | 恢复逐字 commit；或把非 hex 表示作为显式白名单，并补一条“commit 文本已改但行尾形态匹配仍不得推断”的测试。 |
| P2-2 | P2 | handoff 246；batch4 log 33 | “34 张受影响卡全部 PASS”在完整 `check.ps1 -TaskPath` 下不成立（33 张中 16 FAIL，均为其他门禁项）；用户抽查的 8 张 PASS。 | M4 的 16 个失败卡；M4 的 8 个样例 PASS。 | 限定为“证据 pin 口径 34 张 PASS”；不要用全局 PASS(3w) 代表 34 张。 |
| P2-3 | P2 | `test_evidence_exceptions.py`；AC6 裁定 Q4.5 | 10 个测试无 COMMIT_FORMAT/SHA_MULTI/空壳行/摘要列表顺序与分隔符用例；新增钩子未被测试保护。 | 10 个 `def test_` 名单；无相关字符串。 | 补 Q4.5 要求的正负例，尤其是“空壳行必须报错”“摘要列表顺序/分隔符变化不得豁免”。 |
| P2-4 | P2 | `ac4-batch4...log:2`；`ac3-ev11...log:2` | 证据 log head 分别是 ce66a0df1 / 8db997f94，而对应代码/卡片已在 881c6cac2/5cbec0e8 后变化；AC3 log 锚点仍是旧 f1a2/53ce/5ec。 | log 头与锚点；M8 当前行。 | 证据记录写实际 head（或“ce66→881”“8db→5cbec0e8”）并更新锚点。 |
| P2-5 | P2 | FEA-05-PORT-1:107-108；registry EXC-BATCH6-112/114 | 多路径行门禁 PASS 依赖 4 条例外；卡内没有对真实 3 个 controller/2 个 test 文件的独立新行或 supersede，registry 的“真实文件另由…确认”不成立。 | 卡内搜索这些文件名仅出现在多路径行；EV-INTAKE 是 evidence_dir 补登；gate warnings 4 EXEMPTED。 | 为真实文件逐条追加可验证新行，或修正 reason；不要声称未发生的确认。 |

P0：无。P1：P1-1…P1-4。P2：P2-1…P2-5。

## 4. 结论

**AC5 不能判 MET。** AC3 的三条 supersede 行与原始行字节本身正确（Q1 PASS）；AC7 的混合行尾与七列 basis 分支
正确（Q2 的该两部分 PASS）；AC6 的结构/无通配与 Resource 不豁免正确；用户抽查的 8 张卡也 PASS。但：

1. 2 条空壳行被门禁 parser 跳过，违反 Q3“保持结构错误”（P1-1）；
2. 15 条 P02-NEW-TIME-X6 例外永远无法生效，114 条并非都可三重校验（P1-2）；
3. 门禁对非 hex commit 与摘要是“归一化/抽取”比较，不是裁定要求的逐字/原始单元格绑定（P1-3）；
4. AC3 卡、handoff、batch4 log、registry 多路径 reason 存在多处 false statement（P1-4）；
5. 完整门禁 16/33 卡失败，“34 卡全部 PASS”不成立于完整口径（P2-2）；新增钩子/空壳行无测试（P2-3）。

因此整卡 AC5 结论为 **REJECTED**；AC4 的“收敛”仅是“证据 pin 口径下 4 条剩余”的部分结论，不能升级为
“34 卡完整门禁全绿”。本 Review 只读，未 commit/push，未修改除本文件以外的任何文件。
