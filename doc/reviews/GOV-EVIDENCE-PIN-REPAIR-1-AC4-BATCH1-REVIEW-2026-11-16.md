---
id: GOV-EVIDENCE-PIN-REPAIR-1-AC4-BATCH1-REVIEW
kind: review
reviewer: pin-exc-reviewer（DSH 子 agent，独立上下文、只读）
reviewer_kind: subagent
reviewed_head: 3fd04d4cb74b6f261bafc47c6a66f53e9ba75762
base_commit: 8fe6b7ca86aadcb0aecaceb0634cecfae60f4ea5
decision: rejected
---

# 独立 Review：GOV-EVIDENCE-PIN-REPAIR-1 AC4 batch 1

verdict: **REJECTED**
reviewed_head: `3fd04d4cb74b6f261bafc47c6a66f53e9ba75762`（父 `8fe6b7ca86aadcb0aecaceb0634cecfae60f4ea5`）
reviewer: `pin-exc-reviewer`（DSH 子 agent，**独立上下文**，未参与该批任何实施或返修；只读复核，只写本文件）
ruling: `doc/reviews/GOV-EVIDENCE-PIN-REPAIR-1-GATE-RULING-2026-11-16.md`（Q1=B；资格基线 `8db997f94683c6c959c30ba672af6df5d1bbc977`）

## 1. 方法与实测

环境：Windows / PowerShell 7.6.8 / Python 3.14.6 / git 2.52.0.windows.1；仓库 `G:\CODEX\New Manga`，复核开始时
`git status --porcelain` 为空，HEAD 即被核 head `3fd04d4cb`。所有临时探针都在系统 temp 目录，结束后删除；未修改仓库其它文件。

| # | 命令或方法 | EXIT | 关键输出 |
|---|---|---|---|
| M1 | `git rev-parse HEAD` / `git rev-parse 3fd04d4cb^` / `git cat-file -t 8db997f9…` / `git rev-parse 65d97a077^` | 0 | HEAD=`3fd04d4cb74b6f261bafc47c6a66f53e9ba75762`；父=`8fe6b7ca86aadcb0aecaceb0634cecfae60f4ea5`；基线类型 `commit`；AC3 提交的父=`8db997f9…` |
| M2 | Python `json` 独立校验 `tools/governance/evidence-pin-exceptions.json` | 0 | `entries=5`；每条字段数=12 且恰为规定集合；id/fingerprint 无重复；无通配符；sha256 为 64 位小写；基线为 40 位 commit |
| M3 | 按 Task 要求的方法逐路径重算历史 blob：`git log --all --format=%H -- <path>` + `git cat-file blob` + SHA-256 | 0 | EV-01：22 commits / 22 distinct blobs，记录值 `a4213091…` **不存在**；EV-03：12/12，记录值 `2e7bdab9…` **不存在**；两者 worktree/LF/CRLF 也不匹配 |
| M3b | 对 EV-11/12/13 路径做同一历史 blob 检查（复核者追加） | 0 | 三条记录值都**存在**：`doc/tasks/FEA-11-HOST-AUTH-3/4/5.md` 在 `5cbec0e822af224809f3d898c82fe30a025b5ab1` 的 blob SHA-256 分别等于 `4a7e1ca8…` / `60a3d02a…` / `cdc51f96…`（2928 / 1921 / 1995 bytes） |
| M4 | 复核 supersede 行：`git cat-file -t` + `git cat-file blob <commit>:<path>` | 0 | 三个 commit 均为完整 40 位且可解析；blob SHA-256 与登记值一致：`e1c529bd…`（EV-11，24593 B）/ `4ec9662d…`（EV-12，3205 B）/ `a83791cb…`（EV-13，5883 B） |
| M5 | `git diff 8fe6b7ca8 3fd04d4cb -- doc/tasks/FEA-11-HOST-AUTH-2.md`、`--unified=0`、行级 SHA-256 对比 | 0 | 只有 2 行（129/131）变化，均为 Resource 行；父/head 的 20 条 `\| EV-` 证据行**逐字节相同**，3 条 supersede 行亦逐字节相同 |
| M6 | `pwsh -NoProfile -File tools/governance/check.ps1` | 0 | `PASS (3 warnings)`；实测 **1192 ms**（< 10 s） |
| M7 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-HOST-AUTH-2.md` | 0 | `PASS (8 warnings)`；实测 **2127 ms**；8 = 5 条 `EXEMPTED[EXC-FEA11HA2-01..05]` + 3 条全局 warning |
| M8 | `python -B -m unittest tools.governance.tests.test_evidence_exceptions tools.governance.tests.test_audit_evidence_pins` | 0 | `Ran 23 tests in 208.163s` → `OK` |
| M9 | 判别力探针：把父提交卡字节以正确文件名放到 temp，再跑 `-TaskPath` | 1 | 父状态确为 **7 errors**：5 条 `Evidence SHA-256 不匹配` + `Resource 最终路径未验证：—` + `Resource manifest 不存在：—` |
| M10 | 判别力探针：head 卡仅把当前 `status: done` 改为 `status: in_review` 后跑 `-TaskPath` | 1 | 5 条 `EXEMPTED[…]` 仍全部出现；说明门禁没有按“卡片重开/非终态”使例外失效（另有与探针 checkout 无关的其它 error，不影响该观察） |
| M11 | 只读巡检 `python -B tools/governance/audit_evidence_pins.py`（全仓，诊断用，186336 ms） | 1（有 FAIL） | `FAIL: 440   EXEMPTED: 5   SUPERSEDED: 0   WARN: 1671`；440 + 5 = 基线分诊总数 445 |

补充：M11 是巡检工具、不是门禁；门禁耗时以 M6/M7 为准。M3b 的 `5cbec0e8` 是 2026-11-08 的 FEA-11-HOST-AUTH-2 closeout
提交，且是 `8db997f9`（资格基线）与 `3fd04d4cb`（被核 head）的祖先；三份 re-home 卡在该提交首次入库。

## 2. 六项逐项结论

### 2.1 登记表严格性：**PASS**

- `entries` 恰 5 条；每条 12 个字段（`id/card/task_id/evidence_id/path/commit/sha256/class/error_type/reason/ruling/expires_when`），无多余字段。
- 无通配符（`path`/`evidence_id` 均无 `*?[]`）；5 个 id 唯一；8 字段行指纹无重复；`sha256` 均为 64 位小写十六进制；`commit` 为 7–40 位 hex 或 `-`。
- `eligibility_baseline = 8db997f94683c6c959c30ba672af6df5d1bbc977` 可解析且类型为 `commit`；它确为 `65d97a077` 的父提交。
- 门禁自身也会在启动时校验上述结构（`check.ps1` 22–84 行），非法结构直接 `Add-Error`，不是静默通过。

### 2.2 门禁资格校验是否 fail-closed：**PASS（但有 P2 收口项）**

- `Test-EvidenceExceptionEligibility`（86–118 行）只读取**资格基线**卡：`git cat-file -e <baseline>:<card>`，要求基线
  card 的 `status ∈ {done, closed_with_limitations}`，并要求 `<evidence_id>` 行在基线中 `path/commit/sha256/class`
  与登记项逐字相等；否则返回 false。
- `Get-EvidenceException`（120–132 行）以 `card|task_id|evidence_id|path|commit|sha256|class|error_type` 精确键查找；
  登记项不匹配或资格不成立时返回 `$null`，调用点继续 `Add-Error`。
- 例外调用点只有 3 处：`PATH_MISSING`（913）、`COMMIT_PATH_MISSING`（929）、`SHA_MISMATCH`（953）；**没有**按类别、
  按 `status`、按目录的放行路径。`$historicalAcExempt`（989 行）是既有的 §4.3.1 AC 门禁（`83f4ab4c3`），不是证据 pin 例外。
- 降级只产生 `Add-Warning "EXEMPTED[...]"`，不是静默通过；M7 的 8 warnings 可证。
- Resource Manifest 校验位于 994–1061 行，独立于证据行循环，代码中**没有** `Get-EvidenceException` 调用；本批也没有
  登记任何 Resource 例外。**Resource 校验未被豁免。**
- P2 收口项：资格只检查**基线卡**的 `status`，不检查**当前卡**状态；`expires_when` 只是 prose，门禁不读。M10 已实测
  `in_review` 仍降级。按裁定 Q2.4“卡片重开或状态变为非终态时，例外失效”，此处应由门禁强制（见 R-02）。

### 2.3 5 条登记是否名副其实：**FAIL（2/5 PASS，3/5 FAIL）**

- `EV-01`、`EV-03`：**PASS**。M3 独立重跑确认记录值不在该路径任何历史 blob，也不在 worktree/LF/CRLF；理由与
  “全部 22/12 个历史 blob”计数一致，确为不可复现、只能走 warning 例外。
- `EV-11/12/13-supersede` 行本身：**PASS**。M4 确认三条都记录完整 40 位 commit，`git cat-file blob <commit>:<path>`
  的 SHA-256 与登记值逐字相等；三行都在原行之后、基线中不存在、路径未跨、各有且仅有一个替代项。
- `EV-11/12/13` 的例外理由：**FAIL**。登记表 43/57/71 行称“原行记录值在本仓无任何字节表示可复现”；卡片 119–120 行
  重复该说法，但附带“（commit 列是 -，当前工作树、LF、CRLF 三种形态都不匹配）”的限定。M3b 证明无保留的断言不成立——
  三条原值恰好是 closeout 提交 `5cbec0e8` 中三份 re-home 卡的 blob SHA-256，且该提交是资格基线与 head 的祖先。按裁定
  Q3“哈希错须定位权威 blob”“不可恢复的历史行才可逐条申请 warning 例外”，这三条**不是不可恢复**，其例外依据与
  裁定不符（详见 R-01）。
- 计数：登记表 5 条 = 卡内 5 条缺陷证据行（EV-01/03/11/12/13）；GOV 卡 80 行记录“5 条登记例外”，批量日志
  29 行记录 `entries = 5`，三者一致。**数量一致，但 3 条理由不实。**

### 2.4 是否改动历史证据字节：**PASS**

- `git diff 8fe6b7ca8 3fd04d4cb -- doc/tasks/FEA-11-HOST-AUTH-2.md` 只有 129/131 两行：worktree 行 source 改为 `—`、
  原文移入末列；test-fixture 行 destination 与 `sha256/manifest` 补全。**证据行 0 改动**（20 条逐字节相同），
  **supersede 行 0 改动**（逐字节相同）。
- 全量 diff 只有 6 个文件：FEA 卡、GOV 卡 AC4 一行、巡检工具、登记表、`test_audit_evidence_pins.py`、新增 batch log；
  没有删除/重命名既有证据文件。

### 2.5 门禁结果与性能：**PASS**

- 全局：`PASS (3 warnings)`，EXIT 0，**1192 ms**（< 10 s）。
- 单卡：`PASS (8 warnings)`，EXIT 0，**2127 ms**；5 条 `EXEMPTED` 均带 ID 与理由，不是静默。
- 单测：23 tests，208.163 s，`OK`（与“约 3–4 分钟”的预期一致）。
- 父状态 7 errors 的判别力探针也成立（M9），说明 7→0 不是基线本身已绿。

### 2.6 没有绿洗：**PASS（有 P2）**

- 没有删除任何 `test_*` 方法；`test_audit_evidence_pins.py` 的改动主要是把“已知坏卡必须 rc=1”更新为“全部已登记
  ⇒ rc=0 / EXEMPTED: 5”，这是状态变化，不是放宽门禁。`test_without_registry_the_rows_still_fail`、
  `test_empty_registry_changes_nothing`、`test_any_field_change…`、`test_row_added_after_baseline…`、
  `test_wildcard…`、`test_unresolvable_baseline…`、`test_duplicate_fingerprint…` 均保留并通过。
- 但同一 diff 还把旧行断言从“精确 `SUPERSEDED` + `SUPERSEDED_BY_EV-*` code”改成
  `assertIn(verdict, ("EXEMPTED", "SUPERSEDED"))` 且不再校验 code（见 R-05）；这是可收窄的测试强度损失。
- 登记表 5 条与卡/日志一致；但 GOV 卡 80 行与日志 30 行的“余 443 条”与实测不符（R-04）。

## 3. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 |
|---|---|---|---|---|---|
| R-01 | **P1** | `tools/governance/evidence-pin-exceptions.json:43,57,71`；`doc/tasks/FEA-11-HOST-AUTH-2.md:119-120` | EV-11/12/13 三条例外以“原值在本仓无任何字节表示可复现”为依据；事实上三条原值都能在 closeout 提交 `5cbec0e8` 精确复现。按 Q3，只有不可恢复的历史行才可申请 warning 例外；这三条目前把 3 条**可恢复**行降为 warning，5 条例外的依据只有 2 条成立。 | `git cat-file blob 5cbec0e8:doc/tasks/FEA-11-HOST-AUTH-3.md` → SHA-256 `4a7e1ca8…`；`-4.md` → `60a3d02a…`；`-5.md` → `cdc51f96…`；`5cbec0e8` 是 `8db997f9` 与 `3fd04d4cb` 的祖先（`git merge-base --is-ancestor` EXIT 0），2026-11-08 FEA-11-HOST-AUTH-2 closeout。 | DSH 重新裁定这三条：优先按 Q2.3/Q3 用 `5cbec0e8` 这个权威 blob 重 pin/替代；若因“不得改历史证据字节”仍必须保留 warning 例外，须给出新的、与 Q3 不冲突的裁定依据，并修正登记理由与卡内说明。EV-01/03 两条可保留。 |
| R-02 | **P2** | `tools/governance/check.ps1:86-118`（`Test-EvidenceExceptionEligibility`），`expires_when` 字段 | 资格只看**基线卡**终态，不看当前卡状态；卡片重开/变为 `in_review` 后，5 条例外仍降级为 warning，违背裁定 Q2.4“重开或非终态时例外失效”。 | M10：head 卡仅把 `status: done` 改 `in_review`，`-TaskPath` 仍输出 5 条 `EXEMPTED[…]`。 | 在资格校验中同时要求当前 `$taskStatus ∈ {done, closed_with_limitations}`；或把“重开即失效”做成可执行断言并加测试。 |
| R-03 | **P2** | `doc/tasks/FEA-11-HOST-AUTH-2.md:131`；`verification/FEA-11-HOST-AUTH-2/RESOURCE-MANIFEST.json` | test-fixture 行现声明 `PRESERVE_REFERENCED` + destination=`verification/.../tools`，其 `sha256/manifest` 指向的清单却把同一 test-fixture 记为 `NOT_APPLICABLE`（source 还是 `verification/.../tools/* + Host.Tests fixtures`）。门禁对内联表只检查“清单文件存在”（1052–1055 行），不核对清单内容，故 PASS 但证据指针不自洽。 | 清单 `resources[test-fixture] = {disposition: NOT_APPLICABLE, destination_path: NOT_APPLICABLE}`；卡片行 `PRESERVE_REFERENCED`。 | 或改引一份真正记录该目录的清单/条目，或把该行与清单口径统一（例如按清单记为 NOT_APPLICABLE，若该目录只是仓库内 tracked 工具）；不要用不覆盖该资源的清单充当完整性证据。 |
| R-04 | **P2** | `doc/tasks/GOV-EVIDENCE-PIN-REPAIR-1.md:80`；`verification/GOV-EVIDENCE-PIN-REPAIR-1/ac4-batch1-fea11-host-auth-2-2026-11-16.log:30` | 两处写“余 443 条待判/FAIL”。分诊总数 445 是证据行；本批把其中 5 行转为 EXEMPTED，剩余应为 **440**，不是 443（443 = 445 − 2，疑似把 2 条 Resource error 误算进 445）。 | M11：全仓巡检 `FAIL: 440   EXEMPTED: 5`；440 + 5 = 445；`ac4-triage-2026-11-16.json` 的 `total=445`。 | 改为“余 440 条”，并说明 2 条 Resource error 是门禁附加项、不在 445 条证据行内。 |
| R-05 | **P2** | `tools/governance/tests/test_audit_evidence_pins.py:123-125`（另 91-96 行） | 旧行断言的期望从“精确 `SUPERSEDED` + `SUPERSEDED_BY_EV-*` code”弱化为“`EXEMPTED` 或 `SUPERSEDED` 均可”，且不再检查 code。状态变化（rc 1→0）本身合理，但测试不再能区分“登记表优先”与“supersede 回退”两种不同路径。 | 父版 `assertEqual(by_id[old]["verdict"], "SUPERSEDED")` + `assertIn("SUPERSEDED_BY_"+old.upper(), code)`；head 版只剩 `assertIn(verdict, ("EXEMPTED","SUPERSEDED"))`。 | 对“有登记项”的情形精确断言 `EXEMPTED` 并保留一个 code/理由断言；另加“无登记项 ⇒ SUPERSEDED”的独立测试以覆盖回退路径。 |
| R-06 | **P2** | `tools/governance/audit_evidence_pins.py:132-159, 267-269` | 巡检工具的 `EXEMPTED` 只按登记表指纹匹配，**不检查**基线卡是否终态、行是否逐字存在于基线，也不比较 `class`；而卡内 123 行把该工具列为复核方式。它可能把门禁会判 `EVIDENCE_EXCEPTION_INELIGIBLE` 的行显示成 `EXEMPTED`，造成诊断误判。 | 代码只做 `registry_match` → `verdict = "EXEMPTED"`；与 `check.ps1` 的 `Test-EvidenceExceptionEligibility` 不同。 | 让工具的 `EXEMPTED` 复用与门禁相同的资格判定，或改名为 `REGISTERED` 并明确“≠ 门禁已豁免”。 |

P0：无。P1：R-01。P2：R-02…R-06。

## 4. 结论

**AC6 通道是否可信**：作为**机械门禁**基本可信——只对基线终态卡中逐字存在的行降级、只产生带 ID/理由的 warning、
Resource Manifest 完全不在例外范围内，且单测覆盖了“无登记表仍失败 / 字段变化仍失败 / 基线后新增行不豁免 / 通配符拒绝 /
基线不可解析拒绝 / 重复指纹拒绝”等负例。但有两处需收口：当前卡非终态不使例外失效（R-02），巡检工具的 `EXEMPTED`
标签没有复用门禁资格判定（R-06）。二者不改变“门禁本身 fail-closed”的结论，但会影响长期可信度。

**Batch 1 的 5 条例外是否可采纳**：
- `EV-01`、`EV-03`：**可采纳**——独立重跑确认记录值在全部历史 blob 中不存在，理由与证据一致。
- `EV-11/12/13`：**按现有依据不可采纳**——原值能在 `5cbec0e8` 精确复现，登记理由“无任何字节表示”不实，与裁定
  Q3 的“不可恢复才可例外”冲突；其 supersede 行本身合法，但不能用“不可复现”解释原行例外。请 DSH 重新裁定这三条，
  再决定是重 pin 还是保留一个理由正确的 warning 例外。
- 因此本批整体 **REJECTED**；若拆开处理，EV-01/03 的 2 条例外与 Resource 的两处单元修正（test-fixture 的清单
  指针需按 R-03 修正）可以先采纳，EV-11/12/13 退回重裁。

**建议下一步**：由 DSH 处理 R-01（重裁 EV-11/12/13）并顺带修正 R-02…R-06；重裁后重跑两条 `check.ps1` 命令与
`python -B -m unittest tools.governance.tests.test_evidence_exceptions tools.governance.tests.test_audit_evidence_pins`，
再按新 head 送独立复核。本 Review 只读，未 commit/push，也未修改除本文件以外的任何文件。
