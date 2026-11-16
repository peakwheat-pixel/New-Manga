verdict: APPROVED_WITH_FINDINGS
reviewed_head: f1a2e8805a9575c9838f9f18d89de5480e053f8d
reviewer: ac6-reviewer（DSH 派发的独立上下文子 agent；未参与本卡实施、返修或证据生成）
date: 2026-11-16（Asia/Shanghai）
scope: `doc/tasks/GOV-DECLARATION-SCAN-CLEANUP-1.md` 的 AC3（L2 清理）与 AC7（B2 单元修复）
implementation_chain: `23e8d7152`（65）→ `f1a2e8805`（0）；全链 `154 → 147 → 144 → 80 → 65 → 17 → 0`
repo: `G:\CODEX\New Manga`（Windows；`core.autocrlf=true`；所有字节判断用 `read_bytes()` / `git cat-file blob`）

## 1. 复核方法与实测

### 1.1 实测归零（独立运行，输出到仓外）

命令：

```powershell
python -B tools/governance/clean_workspace.py --audit-declarations `
  --out "G:\CODEX\New Manga.workspace\ac6-review-2026-11-16"
```

实测（EXIT=0，15.0 s）：

```text
declaration audit: 6800 declaration(s), 5611 protected root(s), 0 error(s), 821 warning(s)
```

JSON `declaration-audit.json`（249618 B）：`counts.declarations=6800`、`counts.protected_roots=5611`、`counts.errors=0`、`counts.warnings=821`，与实施者声称的 **6800 / 5611 / 821** 完全一致；`errors` 数组长度为 0。

仓内 `verification/GOV-DECLARATION-SCAN-CLEANUP-1/` 另有两份（当前 **untracked**）的 AC6 前后 JSON，我核验了其自校验哈希，均自洽：

| 文件 | errors | warnings | declarations | protected_roots | report_sha256 |
|---|---:|---:|---:|---:|---|
| `ac3-baseline-audit-2026-11-16.json` | 154 | 732 | 6755 | 5593 | `afddd7cc…d04962`（自洽） |
| `ac3-after-audit-2026-11-16.json` | 0 | 821 | 6800 | 5611 | `f7364159…cdd24a`（自洽） |

> 这两份 JSON 只存在于工作区，**未进入被核 head**（`git status` 显示 `??`）。见 Finding F-7。

另核 `verification/GOV-DECLARATION-SCAN-CLEANUP-1/ac3-disposition-map-2026-11-16.md`：**154 个 `ERR-` 行**，头部锚定同一 `report_sha256 = afddd7cc…d04962`，分类合计 **B1 64 / B2 79 / B3 11 = 154**；该分类合计与 baseline JSON 的 code 计数一致（B1 = `TABLE_SCHEMA_INCOMPLETE 53` + `TABLE_DELIMITER 10` + `TABLE_ROW_ARITY 1`；B3 = `DECL_UNKNOWN_DISPOSITION 8` + `FILE_UNREADABLE 1` + `JSON_PARSE 2`；余下 79 为 B2）。逐行 code/文件未逐条重放，但行数、锚定哈希与分类合计三项均与 baseline JSON 对得上。

`protected_roots` 单调性：baseline JSON **5593**，最终实测 **5611**；AC3 链路各提交消息/日志给出的中间值为 5598 → 5601 → 5601 → 5601，均不低于 5593。**未对每个中间 commit 独立重跑 audit**（会改动工作区/需 checkout），因此“从未低于 5593”只由基线 JSON + 最终实测 + 提交消息链支持，而非 6 轮独立实测。

### 1.2 保留态不可回退性（16/16 独立重算）

独立脚本按通道重算 `tools/governance/historical-evidence-interpretation.json` 的 `pinned_defect_retentions`：

- `pin.channel == "WORKTREE"`：对 `pin.path` 取 `read_bytes()` 的 sha256；
- `pin.channel == "BLOB"`：对 `git -C <repo> cat-file blob <pin.commit>:<pin.path>` 的 stdout 取 sha256；
- 注意：`pin.path` 与 `origin_file` 并非同一字段；HIE-R016 的 pin 是 `archive/history/legacy-shell/README.md`，origin 是 `doc/tasks/LEGACY-SHELL-ARCHIVE-1.md`。

结果：**16/16 全部 OK**，0 mismatch。代表性明细：

| id | channel | pin.path | 实测 sha256 | 结果 |
|---|---|---|---|---|
| HIE-R001 | WORKTREE | `doc/tasks/FEA-07-IMMERSIVE-F11-1.md` | `4ea62822…5db1b2` | OK |
| HIE-R002 | BLOB | `doc/tasks/FEA-07.md` | `c64b6a97…0b3eb` | OK |
| HIE-R004 | WORKTREE | `verification/FEA-07-RESIDUAL-2/RESOURCE-MANIFEST.json` | `014316d2…cf8b8` | OK |
| HIE-R005 | WORKTREE | `verification/FEA-07-RESIDUAL-3/RESOURCE-MANIFEST.json` | `d97f0617…f50244d` | OK |
| HIE-R010 | WORKTREE | `verification/FEA-11-RENDITION-1/RESOURCE-MANIFEST.json` | `8ded4d9b…d26f8` | OK |
| HIE-R012 | WORKTREE | `verification/FEA-11-RUN-GRANT-2/RESOURCE-MANIFEST.json` | `35c1015a…facb2` | OK |
| HIE-R015 | WORKTREE | `verification/FEA-15-ACCEPT-1/resource-manifest.json` | `27e8b3f7…0abd1` | OK |
| HIE-R016 | WORKTREE | `archive/history/legacy-shell/README.md` | `ff7d7fc0…653e` | OK |

审计 JSON 的 `warnings` 中仍存在 **16 条** `DECL_PINNED_DEFECT_RETAINED`，每条 `message` 都带 `original_code=`，抽查（实为全量）原样 code：

- HIE-R001/R002/R003/R007/R013：`DECL_RELATIVE_UNRESOLVED`
- HIE-R004/R006/R009/R011/R015：`DECL_GLOB`
- HIE-R005：`DECL_ENV`
- HIE-R008/R010/R014：`DECL_DESTINATION_UNRESOLVED`
- HIE-R012：`DECL_MISSING_SOURCE`
- HIE-R016：`DECL_RELATIVE_AMBIGUOUS`

即保留态不是“消音”：原始错误码、原始 message、pin 卡片/证据/通道/commit/sha 仍在警告中可见；`clean_workspace.py` 对每条 retention 仍执行 `SOURCE_DRIFT`/`ERROR_MISMATCH` fail-closed 校验（见 `tools/governance/clean_workspace.py:2055-2094`）。

### 1.3 规则是否被放宽（绿洗检查）

`git diff 23e8d7152 f1a2e8805 -- tools/governance/clean_workspace.py` 只有 13 行变化：

1. `HISTORICAL_EVIDENCE_DIGEST` 常量：`e2186de3…d59228` → `a0fc430f…13c4fd3`；
2. `pinned_defect_retentions[].pin` 的精确字段集由 `card evidence_id commit sha256 channel` 扩展为 `… channel path`；
3. pin 字节校验收 `pin.path`（而不是 `origin_file`）读取/取 blob。

`DISPOSITION_RE` 在 base `517072586`、`23e8d7152`、`f1a2e8805` 三处逐字符相同，仍为：

```text
^(DELETE_SAFE|MIGRATE|ARCHIVE|ALREADY_ABSENT|NOT_APPLICABLE|PRESERVE_[A-Z0-9_]+)$
```

`DISPOSITION_ALIASES` 仍为封闭 5 个精确 token（`PRESERVE`、`READ_ONLY_REFERENCED`、`MODIFIED_IN_PLACE`、`RESTORED_IN_PLACE`、`NOT_CREATED_NO_SCRATCH`），精确大小写匹配，未列 token 仍 `DECL_UNKNOWN_DISPOSITION`。本提交没有新增整文件/目录/通配豁免，也没有按错误码/前缀整体忽略；累计 diff（`517072586..f1a2e8805`）只出现裁决允许的别名表、逐表绑定、逐文件 raw 绑定、逐条 pin 保留态，以及 AC4 的 Ruling C/D 成员不变量；`PROTECTION_REGRESSION`、`SOURCE_DRIFT`、`ERROR_MISMATCH` 均保持 fail-closed。Ruling D 的 `if not has_line` 不是放宽：有行级身份时仍校验 `sha(lines[number-1]) == origin_line_raw_sha256`（`clean_workspace.py:2311-2322`）。

`HISTORICAL_EVIDENCE_DIGEST` 自行重算：

| commit | canonical sha256（对完整 policy 做 `json.dumps(ensure_ascii=False, sort_keys=True, separators=(",", ":"))`） | 与代码常量 |
|---|---|---|
| `23e8d7152` | `e2186de34cec23893a5a73707277eb2075fdbb828564eb4e8cf2eca967d59228` | 匹配旧常量 |
| `f1a2e8805` | `a0fc430f3b15bcef31ad0cb1a0358b7b4834cae3b9a5e43f895b37df413c4fd3` | 匹配新常量 |

### 1.4 字节边界

`git diff --stat 23e8d7152 f1a2e8805`：**52 files changed, 269 insertions(+), 87 deletions(-)**。

分类：`doc/tasks/*.md` **45**；`tools/governance/` **3**（`clean_workspace.py`、`historical-evidence-interpretation.json`、`tests/test_historical_binding_policy.py`）；`verification/GOV-DECLARATION-SCAN-CLEANUP-1/**` **2 A**（`ac7-allowed-cells-2026-11-16.md`、`ac7-execution-2026-11-16.log`）；另 **2**：`doc/STATUS.md`、`doc/handoffs/NEXT-SESSION-STARTER.md`。

特别核验：

```text
git diff 23e8d7152 f1a2e8805 -- "*RESOURCE-MANIFEST.json" "*resource-manifest.json" `
  tools/governance/residual-runtime-identity.json
→ 0 行

git diff --name-status 23e8d7152 f1a2e8805 -- verification/
→ A  verification/.../ac7-allowed-cells-2026-11-16.md
→ A  verification/.../ac7-execution-2026-11-16.log
（无 M / D / R）

git diff --check 23e8d7152 f1a2e8805
→ EXIT=0，无输出
```

结论：`verification/**` 历史文件零修改（只有本卡新增 2 个 A）；`RESOURCE-MANIFEST.json` / `resource-manifest.json` 零字节改动；`residual-runtime-identity.json` 零字节改动。两项特别边界要求均通过。

但最终的 52 文件与实施者“45 张 doc/tasks + 3 个 tools + 新增 verification 证据”的声明不一致：多出 `doc/STATUS.md` 与 `doc/handoffs/NEXT-SESSION-STARTER.md` 2 个文件（见 F-6）。

### 1.5 单元级 diff 与路径真实性（45 个 doc/tasks 全量扫描）

用 `git show` 取两个 commit 的 blob 做逐行 `difflib`，对 45 个被改文件逐 hunk 解析 Resource Manifest 表格行。结果：

- 全部改动都落在 `## Resource Manifest` 节内；没有正文、其他表、其他行的改动（本卡 `GOV-DECLARATION-SCAN-CLEANUP-1.md` 的 AC 标记除外）。
- 被改单元格列索引只出现 `2/3/4/6`（source_path / disposition / destination_path / reference/process check）；**列 5（sha256/manifest）零改动**。
- 新值（去掉占位符 `—` 后）中的绝对路径/仓库相对路径逐条 `Test-Path`，全部 **EXISTS**：`G:/CODEX/New Manga.workspace/tmp`、`FEA-08`、`FEA-11/fixtures`、`task-envs/{GATE4-PAGES-UPGRADE-1,GATE4-READER-PAGE-1,GIT-CLEAN-PUBLICATION-1,INSTALLER-MATRIX-1,SIDECAR-REBUILD-1}`、`artifacts/publish`、`FEA-15-A2-1/out/NewManga-0.1.1-win-x64`、`FEA-15-PIN-BASIS-ENFORCE-1`、`archive/history/legacy-shell/README.md`、`C:/Users/49745/AppData/{Local/Temp,Roaming/com.newmanga.desktop,Roaming/NewManga}`、`verification/FEA-11-HOST-AUTH-2/tools`、`tests/fea11`、`G:/$RECYCLE.BIN`。**不存在“把不存在路径写成 `PRESERVE_*`”**。
- 但存在 **2 处未列入 `allowed_cells` / 65 条修复计划的单元格改写**，其中 1 处语义错误；另有 13 处未闭合反引号和 14 处末列附注改写。详见 Findings。
- 保护集合 containment 抽查：7 个被改为 `—`/NA 的 `..\New Manga.workspace\tmp` 行在基线是 `DECL_TRAVERSAL` 错误（`resolve_declared_path` 在 `..` 处 fail，未注册保护），不构成基线保护根丢失；`FEA-15-PIN-BASIS-ENFORCE-1.md:362` 的 repo 根仍由同行 `destination_path` 保护（head 保护索引实测 `IN G:\CODEX\New Manga`）；其余保护→非保护改动只涉及非路径 vault 文本或原本已非保护的 `DELETE_SAFE`。未发现基线保护根被删；完整 5593 根的逐根差分未重算（需在基线 commit 重跑 scan）。

### 1.6 测试与治理检查（EXIT 与关键行）

| # | 命令 | EXIT | 关键输出 |
|---|---|---:|---|
| 1 | `python -B -m unittest discover -s tools/governance/tests -p "test_historical_binding_policy.py"` | 0 | `Ran 16 tests … OK` |
| 2 | `python -B -m unittest tools.governance.tests.test_residual_runtime_identity` | 0 | `Ran 14 tests … OK`（有 ResourceWarning，不影响结果） |
| 3 | `pwsh -NoProfile -File tools/governance/check.ps1` | 0 | `Governance check: PASS (3 warnings)` |
| 4 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-DECLARATION-SCAN-CLEANUP-1.md` | 0 | `Governance check: PASS (3 warnings)` |

注：未运行 `test_canonical_evidence_basis`，也未跑全量 .NET 测试（按复核要求，避免 `test.ps1` 对 `verification/READER-OVERLAY-HEADLESS-PNG-1/` 的既有副作用）。

### 1.7 标记与状态

- `doc/tasks/GOV-DECLARATION-SCAN-CLEANUP-1.md:83-85`：AC3 为 `[x]`，行末 `<<MET>>`（第 85 行）。
- 同文件 `:96-100`：AC7 为 `[x]`，行末 `<<MET>>`（第 100 行）。
- 同文件 `:92`：AC6 仍为 `[ ]`。
- `doc/STATUS.md:8`：`**Release Gate \`BLOCKED\`**` 仍在；`doc/STATUS.md:10` 仅把“154→144”更新为“154→0”（允许路径）。
- `git diff --check` EXIT=0；`check.ps1` 两轮均 PASS。

## 2. 逐项结论表

| # | 必核项 | 结论 | 证据 |
|---:|---|---|---|
| 1 | 实测归零：`errors=0`，记录 declarations/protected_roots/warnings | **PASS** | 独立 audit：6800 / 5611 / 0 / 821，EXIT=0；仓外 `declaration-audit.json` |
| 2 | 不可回退性：16 条保留态逐一按通道重算 sha256，且原始错误码可见 | **PASS** | 16/16 pin OK；16 条 `DECL_PINNED_DEFECT_RETAINED` 均带 `original_code=`；`historical-evidence-interpretation.json:1756-2077` |
| 3 | 是否放宽规则（绿洗）：`DISPOSITION_RE`、整文件/目录/通配豁免、digest 一致性 | **PASS** | 23e8→head 仅 13 行；`DISPOSITION_RE` 三处相同；别名表 5 token；digest 新旧均重算匹配；累计 diff 无全局忽略 |
| 4 | 字节边界：stat 符合声明；manifest/RRI 空 diff；verification 无既有文件修改 | **PASS（边界）/ FAIL（声明计数，P2）** | manifest/RRI 0 行；verification 仅 2 A；`git diff --check` EXIT=0；实际 52 文件 vs 声明 45+3+verification，多 STATUS/STARTER（F-6） |
| 5 | 单元级 diff：只动 Resource Manifest 列明单元格；无臆造路径/错配 | **FAIL（P1）** | 45 文件均只动 Resource Manifest 行，但 `FEA-15-PIN-BASIS-ENFORCE-1.md:362` 有未列明且语义错误的 source 改写（F-1）；`FEA-11-LINEAGE-1.md:175` 未列明 NA 改写（F-4）；13 处未闭合反引号（F-2）；14 处末列附注（F-3） |
| 6 | 测试：两套 Python 单测 + 两轮 check.ps1 | **PASS** | 16/16 OK；14/14 OK；check.ps1 PASS(3w)；TaskPath PASS(3w)；全部 EXIT=0 |
| 7 | 未越权：AC3/AC7 标记、AC6 未勾、STATUS Gate BLOCKED | **PASS（标记/状态）** | AC3/AC7 `[x] <<MET>>` 行末；AC6 `[ ]`；`doc/STATUS.md:8` 仍 `BLOCKED`；另见 F-5（STARTER 越出 allowed_paths） |

## 3. Findings

### P0

无。

### P1

**F-1（越界单元改写 + 语义错误，必须返修）**：`doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md:362`（Resource Manifest「main worktree」行）的 `source_path` 由 `G:/CODEX/New Manga` 改为 `G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1`。

- 该行不在 `ac7-allowed-cells-2026-11-16.md`（该文件只列了同文件 `:370` 的 `*.log` glob 行，见清单第 75 行），也不在 `ac7-repair-plan-2026-11-16.md` 的 65 条（ERR-094 只指向 `:370` 的 glob）。
- 该行在 `23e8d7152` 的 65 条错误中**不存在**；`G:/CODEX/New Manga` 是仓库根，不属于 `WORKSPACE_SUBDIRS`，不会被 `DECL_GENERALIZED` 命中，因此这处改写没有错误驱动，属无依据改写。
- 语义错误：行首仍是「main worktree」，源路径却变成 FEA-15 的 task 目录；destination 仍是 `G:/CODEX/New Manga`，所以仓库根仍被保护（最终保护索引实测 `IN G:\CODEX\New Manga`），审计仍为 0，属于**静默数据错误**。
- 违反 `doc/reviews/GOV-DECLARATION-SCAN-CLEANUP-1-AC3-CODEX-RULING-2026-11-16.md` §Q4 的 AC5 补充（“仅允许 allowed_cells 所列替换，同一文件其他字节不得变化”）与 AC7 验收判据“改动只落在列明单元”。
- 修复建议：将该单元格恢复为 `G:/CODEX/New Manga`，重跑 `--audit-declarations` 确认仍为 0（按 23e8 事实，该行不是错误源，恢复不应引入新错误），然后重做 AC7 的单元级复核。

### P2

**F-2（13 处未闭合反引号，文档/值形态损坏）**：新单元格出现奇数个反引号，扫描器 `clean_cell` 虽能吸收，但 Markdown 与 `allowed_cells` 的“新值”不一致，违反裁决 §Q4 #3“修复后的值须语义真实、可解析”：

| 文件:行 | 新值（原样） |
|---|---|
| `doc/tasks/FEA-06-RESIDUAL-1.md:151` | `—\`` |
| `doc/tasks/FEA-06-RESIDUAL-2.md:340` | `—\`` |
| `doc/tasks/FEA-06.md:264` | `—\`` |
| `doc/tasks/FEA-07-AC5-NATIVE-1.md:267` | `` `C:/Users/49745/AppData/Local/Temp ``（缺闭合） |
| `doc/tasks/FEA-07-RESIDUAL-4.md:125` | `` `C:/Users/49745/AppData/Local/Temp ``（缺闭合） |
| `doc/tasks/FEA-07-V2-F11-1.md:88` | `` `C:/Users/49745/AppData/Local/Temp ``（缺闭合） |
| `doc/tasks/FEA-08.md:197` | `` G:/CODEX/New Manga.workspace/FEA-08` ``（缺起始） |
| `doc/tasks/FEA-11-HOST-AUTH-2.md:120` | `` `verification/FEA-11-HOST-AUTH-2/tools ``（缺闭合） |
| `doc/tasks/FEA-11-RENDITION-1.md:209` | `` `tests/fea11 ``（缺闭合） |
| `doc/tasks/FEA-11-RESIDUAL-4A.md:190` | `` `G:/CODEX/New Manga.workspace/FEA-11/fixtures ``（缺闭合） |
| `doc/tasks/FEA-11-SCAN-1.md:268` | `` `G:/CODEX/New Manga.workspace/FEA-11/fixtures ``（缺闭合） |
| `doc/tasks/FEA-14-SET-1.md:119` | `` `C:/Users/49745/AppData/Roaming/NewManga ``（缺闭合） |
| `doc/tasks/REAL-TRANSLATE-PROVIDER-1.md:114` | `—\`` |

**F-3（14 处末列附注改写，超出「源/目标/disposition」列）**：以下行的第 6 列（reference/process check）也被追加/改写，严格说不在 AC7 列明单元内：

`FEA-00A-PREP-1.md:69`、`FEA-01-FREEZE-1.md:80`、`FEA-08.md:198`、`FEA-11-LINEAGE-1.md:176`、`FEA-15-A2-1.md:107`、`FEA-15-A3-1.md:78`、`FEA-15-A3-1.md:80`、`FEA-15-A4-1.md:76`、`FEA-15-PIN-BASIS-ENFORCE-1.md:370`、`FEA-C10-DRAFT.md:86`、`FEA-C11-PREREQ-1.md:73`、`FEA-C14-DRAFT.md:108`、`FEA-CONTRACT-WRAP-1.md:88`、`FEA-D06-GAP.md:105`。

其中 FEA-15-A2/A3/A4 的 `allowed_cells` 依据写了 `(+note)`，7 个 tmp 行写了“原声明写明”，FEA-11-LINEAGE 写了“说明保留在本行末列”，所以有部分披露；但 `allowed_cells` 的“新值/新 disposition”列并未列出末列，仍与“只允许所列替换”的字面要求不一致。无保护语义损失，属流程/证据一致性问题。

**F-4（未列明的 NA→`—` 改写）**：`doc/tasks/FEA-11-LINEAGE-1.md:175` 的 `source_path` 由 `NOT_APPLICABLE（main 工作树实施）` 改为 `—`，disposition 仍 `NOT_APPLICABLE`。该行不在 65 条计划，也不在 `allowed_cells`；它原本只是 `DECL_SOURCE_NOT_A_PATH` 警告（不是 error），属无必要的范围外清理。

**F-5（越出 `allowed_paths`）**：`doc/handoffs/NEXT-SESSION-STARTER.md` 在 `f1a2e8805` 中被改 11 行（以及此前 5 个 batch commit 各改一次），但本卡 frontmatter 的 `allowed_paths` 只列了 `doc/handoffs/GOV-DECLARATION-SCAN-CLEANUP-1-handoff.md`，没有 `NEXT-SESSION-STARTER.md`。内容本身是如实进度更新，不涉及产品/证据字节，仍属授权边界问题。

**F-6（stat 声明不完整）**：被核 commit 实际 52 文件 / +269−87；实施声明与 `ac7-execution` 日志按“45 张 doc/tasks + 3 个 tools = 48 文件 / +121−84”表述。多出的 4 个是 `doc/STATUS.md`、`doc/handoffs/NEXT-SESSION-STARTER.md` 和 2 个 verification 证据文件；其中前两个未在声明中列出。建议在 AC6 回填时把 stat 口径改成“52 文件（含 2 个指针/证据文件）”或明确 48 文件只是 AC7 代码/卡子集。

**F-7（AC6 证据未入 head）**：`ac3-baseline-audit-2026-11-16.json` 与 `ac3-after-audit-2026-11-16.json` 当前是 `??`（untracked），没有进入 `f1a2e8805`。AC6 明确要求回填 baseline/after 两轮 JSON；在固定 head 被核时，这两份证据不可从 commit 复现（虽工作区文件本身自洽）。AC6 关闭前应纳入 commit 或明确证据存放策略。

**F-8（AC7 数字口径不一致，文档级）**：AC7 原文写“12 条活 pin B2 与 3 条活 pin B3”，但实际 `pinned_defect_retentions` 是 **16 条全 B2**（12 个 verification manifest + 3 个 doc/tasks 卡 + 1 个 archive README）；3 条 B3 是由 `raw_non_declaration_bindings`（HIE-O04/O05/O06）以 `DECL_HISTORICAL_EVIDENCE_PRESERVED` 保留的。机制上 3 条 B3 仍可审计（警告带 `original_codes=`），但 AC7 的 12+3 表述与最终 16+3 的实际结构不一致，建议在 AC6 回填时对齐。

## 4. 结论（一句话）

**AC3 的 `<<MET>>` 成立**（154→0、6800/5611/821、16/16 pin 可复验且原始错误码可见、规则未被放宽）；**AC7 的 `<<MET>>` 当前不严格成立**——`FEA-15-PIN-BASIS-ENFORCE-1.md:362` 有一处未列入 `allowed_cells` 且语义错误的源路径改写（P1），另有 13 处未闭合反引号和 14 处末列附注超出“仅列明单元”的字面约束，需按 F-1～F-4 定点返修并重跑 audit/单元级 diff 后，AC7 才能维持 `[x] <<MET>>`。

## §5 返修收敛复核（2026-11-16，第二轮）

verdict: APPROVED_WITH_FINDINGS
reviewed_head: 314aafbdadf06e1543816718feadffa559ac0f95（父 f1a2e8805；push 后新 head）
reviewer: ac6-reviewer（同一独立上下文；未参与 f1a2e8805 之后的返修）

### 5.1 逐项结论

| # | 收敛项 | 结论 | 证据 |
|---:|---|---|---|
| 1 | P1 是否真修好：`FEA-15-PIN-BASIS-ENFORCE-1.md` 只应有 `*.log` glob 一行改动，main-worktree source 回到 `G:/CODEX/New Manga` | **PASS** | `git diff 23e8d7152 314aafbda -- doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md` 只有 1 行（`:370` glob → 目录本体）；main-worktree 行未出现在 diff 中，已回到 `G:/CODEX/New Manga` |
| 2 | P2 反引号：`git diff 23e8d7152 314aafbda -- doc/tasks` 每个新增行反引号奇偶 | **PASS** | 78 个新增行，**0 个奇数反引号**；上一轮 13 处未闭合全部消失 |
| 3 | `allowed_cells` 反向生成（99 单元格/45 文件）：抽样旧值→新值一致、无未列明单元格、无“不存在路径写成 `PRESERVE_*`” | **PASS（表单元格）/ P2（卡片行与列表完整性）** | 抽 10 个表单元格（行 10/11/34/35/58/60/63/41/43/52）全部与 diff 精确匹配；**95/95 个 Resource Manifest 表单元格**均被列明且匹配，无未列明表单元格；36 个路径型新值全部 `EXISTS`，0 个缺失，0 个 `PRESERVE_*`+缺失。P2 见 5.3：2 个卡片行旧值截断、2 行 `allowed_paths` 插入未列、`列序号` 口径错 |
| 4 | 审计与不变量：errors=0；declarations/protected_roots/warnings；16 条 retention pin | **PASS（独立 audit）/ P1（已入库 after JSON 过期）** | 独立 audit EXIT=0：**6800 / 5611 / 0 / 822**；16/16 retention pin 重算匹配（WORKTREE `read_bytes` / BLOB `git cat-file`）。但仓内 `ac3-after-audit-2026-11-16.json` 仍是 **821，report_sha256=f7364159…**（19:39:45，f1a2 版），与新 head 的 822 / `26225e7b…` 不一致 |
| 5 | 范围：只含 45 doc/tasks + tools + 本卡文档/新增证据；manifest/RRI 空；verification 既有文件 0 修改 | **PASS（文件集/边界）/ P1（allowed_paths 通配）/ P2（STARTER 事后授权）** | 55 文件 = 45 `doc/tasks` + 3 tools + 4 verification（全部 **A**）+ `doc/STATUS.md` + `doc/handoffs/NEXT-SESSION-STARTER.md` + 本复核报告；`*RESOURCE-MANIFEST.json`/`resource-manifest.json`/`residual-runtime-identity.json` diff **0 行**；verification 无 M/D；`git diff --check` EXIT=0。P1 见 5.3：卡片把 `doc/tasks/*.md` 加入 `allowed_paths` |
| 6 | warnings +1 的解释：首版误改消掉 `DECL_SOURCE_NOT_A_PATH`，重放恢复原文后回来 | **PASS** | 旧 821 → 新 822；warning 集合差分 **+1 / -0**，唯一新增即 `doc/tasks/FEA-11-LINEAGE-1.md` 的 `source 'NOT_APPLICABLE（main 工作树实施）'`；`f1a2e8805` 该行为 `—`，`314aafbda` 恢复原文，解释成立 |

### 5.2 详细实测

**P1 修复**：`git diff 23e8d7152 314aafbda -- doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md` 只有一个 hunk，`agent-output logs` 行由 `G:/CODEX/New Manga.workspace/FEA-15-PIN-BASIS-ENFORCE-1/*.log` 改为目录本体；「main worktree」行（`:362`）已不在 diff 中，即 source 回到 `G:/CODEX/New Manga`。`git diff f1a2e8805 314aafbda -- doc/tasks/FEA-11-LINEAGE-1.md` 显示 `:175` 由 `—` 恢复为 `NOT_APPLICABLE（main 工作树实施）`，同时 `:176` 去掉首版追加的末列附注；`23e8d7152→314aafbda` 的该文件只剩 `:176` 一行合法修复。

**反引号**：对 `git diff 23e8d7152 314aafbda -- doc/tasks` 的 78 个新增行逐行 `count("`")`，奇数行 0；上一轮的 `—``、`` `C:/.../Temp `` 等 13 处全部不再是新增行形态。

**allowed_cells**：文件 `verification/GOV-DECLARATION-SCAN-CLEANUP-1/ac7-allowed-cells-2026-11-16.md` 共 99 行 / 45 文件。其中 **95 行是 Resource Manifest 表单元格，4 行是卡片 AC3/AC7 行**。抽查 10 个表单元格（含 source、destination、disposition）全部与 `23e8d7152→314aafbda` 的逐格 diff 精确匹配；独立比对显示 **95/95 个表单元格**均有列明、无未列明表单元格。路径语义：36 个路径型新值全部可解析（`Test-Path` / `Path.exists` 为真），0 个缺失；6 个抽检新值（`C:/Users/49745/AppData/Local/Temp`、`C:/Users/49745/AppData/Roaming/com.newmanga.desktop`、`G:/CODEX/New Manga.workspace/FEA-08`、`G:/CODEX/New Manga.workspace/FEA-15-A2-1/out/NewManga-0.1.1-win-x64`、`verification/FEA-11-HOST-AUTH-2/tools`、`tests/fea11`）均存在；所有 `PRESERVE_*` 新值均存在。

**审计/不变量**：独立 `--audit-declarations`（仓外 `ac6-review-2026-11-16-r2`）EXIT=0，`declaration audit: 6800 declaration(s), 5611 protected root(s), 0 error(s), 822 warning(s)`；16/16 retention pin 重算匹配，16 条 `DECL_PINNED_DEFECT_RETAINED` 仍在 warnings。仓内 `ac3-after-audit-2026-11-16.json` 是 19:39:45 的 f1a2 版（821 / `f7364159…`），不是 314 的 822 / `26225e7b…`；`ac7-execution-2026-11-16.log:14` 已写 822，形成日志/证据文件不一致。

**范围/边界**：`git diff --stat 23e8d7152 314aafbda` 为 55 文件；`git diff --name-status -- verification/` 只有 4 个 **A**（baseline/after audit JSON、allowed-cells、execution log），无 M/D/R；manifest/RRI 过滤 diff 0 行；`git diff --check` EXIT=0。文件集符合“45 doc/tasks + tools + 本卡文档/新证据”，但卡片 frontmatter 新增 `doc/tasks/*.md` 与 `doc/handoffs/NEXT-SESSION-STARTER.md`：前者把 AC5 补充的精确路径授权扩成整目录通配，后者是对首版 F-5 的事后补授权。

**+1 warning**：旧 audit 821 → 新 audit 822；warning 多重集合差分新增 1 条、删除 0 条，新增项恰为 `DECL_SOURCE_NOT_A_PATH` + `doc/tasks/FEA-11-LINEAGE-1.md` + `NOT_APPLICABLE（main 工作树实施）`。`f1a2e8805` 与 `314aafbda` 的该行分别为 `—` 与恢复后的原文，解释与字节事实一致。

### 5.3 Findings（本轮）

**P0**：无。

**P1**：

- **P1-5.1 `allowed_paths` 扩成 `doc/tasks/*.md` 通配**：`doc/tasks/GOV-DECLARATION-SCAN-CLEANUP-1.md` 的 frontmatter 在 314 新增 `doc/tasks/*.md`（注释称“仅 AC7 allowed_cells 列明的 Resource Manifest 单元”）。Codex 裁决 §Q4 明确要求 `allowed_paths` 是 67 条对应文件的**精确路径集合**，并明确“**不得授权整个 `doc/tasks/*.md`**、整张表或整行随意改动”。注释不能改变 frontmatter 的授权面；应改为 45 个精确文件路径（或删除该通配后由精确清单承担）。
- **P1-5.2 已入库 after 审计 JSON 过期**：仓内 `verification/.../ac3-after-audit-2026-11-16.json` 是 **821 warnings / `f7364159…`** 的 f1a2 版（`generated_at=19:39:45`），而新 head 独立 audit 是 **822 / `26225e7b…`**；`ac7-execution-2026-11-16.log` 也写 822。AC6 的 baseline/after 证据必须对应固定 head；应重跑并入库 822 版 after JSON（或在报告中明确 821 是 pre-fix、822 才是 after）。

**P2**：

- **P2-5.1 allowed_cells 列表不完整/不精确**：99 行 = 95 个表单元格 + 4 个卡片 AC 行；卡片新增的 2 行 `allowed_paths`（`doc/handoffs/NEXT-SESSION-STARTER.md`、`doc/tasks/*.md`）和 `## AC6 复核处置` 新节未列入；第 88/90 行旧值被截断到 112 字符（如 `…剩 65 条未钉住 `、`…裁定已落盘，Q`），与真实旧行不完全一致。表单元格 95/95 已覆盖，故不影响 AC7 单元修复的机械核验，但“99 单元格全部列明”的说法不成立。
- **P2-5.2 `列序号` 口径错**：allowed_cells 表头称“列序号按该表表头”，实际是“该行被改单元格的序号”（如行 63 写 `1`，实际是表第 2 列 source_path；行 11 写 `2`，实际是第 3 列 disposition；卡片行写 `0`）。应改名或改为真实表列号，避免复核者误读。
- **P2-5.3 STARTER/STATUS 的事后声明**：`doc/handoffs/NEXT-SESSION-STARTER.md` 通过新增 `allowed_paths` 条目正式化（首版 F-5 的形式问题被消除，但属事后自我授权）；`doc/STATUS.md:10` 已写“复核 P1/P2 已返修”，而本轮仍发现 P1-5.1/P1-5.2，STATUS 的时点表述略超前。
- **P2-5.4 covered 范围表述**：`ac7-execution` 日志把“其他代码/政策”写为 5 个（STATUS、STARTER、3 个 tools），但 23e8→314 实际还包含 4 个 verification 新证据和本复核报告；日志的“45 文件/5 其他”是 AC7 子集口径，建议在 AC6 回填时统一为 55 文件全量口径（本复核报告自身是否计入可由 DSH 定）。

### 5.4 结论

本次返修**真实修好了上一轮的 P1（main-worktree 误配）和 P2（13 处反引号）**，审计仍为 0/6800/5611/822、16/16 pin 仍可复验、+1 warning 解释成立；但收敛不能判 `APPROVED`：新增的 `allowed_paths: doc/tasks/*.md` 通配违反 Codex §Q4 的精确路径要求（P1-5.1），已入库的 after JSON 仍是 821 的 f1a2 版而非 314 的 822（P1-5.2）；另有 allowed_cells 卡片行截断/未列、列序号口径、STARTER 事后授权等 P2。**AC3 的 `<<MET>>` 继续成立；AC7 的语义修复在 45 张卡上成立；AC6 关闭前应先处置 P1-5.1/P1-5.2（并重生成 822 after JSON），再复跑本收敛检查。**

## §6 二轮收敛确认（2026-11-16，head a66d2530e）

verdict: APPROVED_WITH_FINDINGS
reviewed_head: a66d2530e4d646854a4287d183b8f80f1e499b5e（父 314aafbda）
reviewer: ac6-reviewer（同一独立上下文；未参与 a66d2530e 的返修）

### 6.1 三项结论

| # | 项 | 结论 | 证据 |
|---:|---|---|---|
| 1 | P1-5.1：`allowed_paths` 无 `doc/tasks/*.md` 通配；45 条精确路径与 `23e8d7152→a66d2530e` 的 diff 文件集一致（卡自身除外） | **PASS（核心）/ P2（有效列表重复与额外）** | 新增块确实是 **45 条精确路径**（D-14…TOOL-SOFTWARE-SMOKE，含卡自身），无 `*` 通配；与 `git diff --name-only 23e8d7152 a66d2530e -- doc/tasks` 的 45 文件逐一对应。但 frontmatter 原有卡自身条目 + 新增块又列了一次卡自身 ⇒ **47 条 doc/tasks 条目 / 46 唯一**；另保留 `doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md`（不在本次 diff，若 AC6 回填需要可说明保留理由） |
| 2 | P1-5.2：`ac3-after-audit-2026-11-16.json` 是当前 head 真实结果（0 / 822 / 6800 / 5611，sha `26225e7b` 开头，且非 821/f736…） | **PASS** | 仓内 after JSON：errors=0、warnings=822、declarations=6800、protected_roots=5611、`report_sha256=26225e7b3c6da8f46e722f6cedfddf0dea78f2b4ae44289a7de5ea31a522aa2d`、`generated_at=2026-11-16T20:19:27+08:00`；在 a66d2530e 独立重跑 audit 得到**完全相同的 counts 与 report_sha256**；不是首版 821/`f7364159…` |
| 3 | P2：allowed-cells (a) 旧值不再截断、(b) 明确「列位置 = 表内单元格序号」、(c) 卡自身结构性编辑单列 §2 | **PASS（a/b/c）/ P2（§2 的 45 条表述与有效列表不一致）** | (a) §1 的 95 个表单元格旧值完整（无 112 字符截断），原截断的卡 AC 行已移出表；(b) 第 4 行明确「「列位置」= 该行在本表内第几个单元格（从 0 起）」；(c) 第 107 行起 `## 2. 本卡结构性编辑（非 Resource Manifest 单元）` 单列 `allowed_paths` 精确化、`## AC6 复核处置`、AC 标记。P2：§2 写「45 条精确文件路径」，但有效 frontmatter 为 47 条/46 唯一（同第 1 项） |

### 6.2 详细实测

- **allowed_paths**：`git diff 23e8d7152 a66d2530e -- doc/tasks/GOV-DECLARATION-SCAN-CLEANUP-1.md` 显示新增块以注释「AC7 逐单元授权的 45 张历史卡（**不是** doc/tasks/*.md 通配…）」开头，后接 45 条 `- doc/tasks/…` 精确路径；无 `doc/tasks/*.md`。diff 文件集也是 45 个 `doc/tasks` 文件，新增块与之一一对应。有效 frontmatter 的 `doc/tasks` 条目为 47（46 唯一）：卡自身在原条目和新增块各出现一次；`GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md` 为原有保留项、不在本次 diff（AC6 回填 GOV-RESIDUAL 时可能需要，建议在 §2 说明）。
- **after JSON**：仓内 `verification/GOV-DECLARATION-SCAN-CLEANUP-1/ac3-after-audit-2026-11-16.json` 已从首版 821/`f7364159…` 更新为 822/`26225e7b…`；`generated_at` 为 20:19:27。独立重跑 `python -B tools/governance/clean_workspace.py --audit-declarations --out <仓外>` 得到 `6800 declaration(s), 5611 protected root(s), 0 error(s), 822 warning(s)`，`report_sha256` 与仓内 after JSON 完全相同；不是 821/f736 首版。
- **allowed-cells**：114 行；§1「Resource Manifest 单元（95 个，覆盖 44 个文件）」；原第 88/90 行的 112 字符截断已消失（这两条卡 AC 行不再作为表行，而在 §2 结构性摘要中）；第 4 行给出 0 起的「列位置」定义；§2 第 107-113 行列卡自身结构性编辑。§2 的「45 条精确文件路径」与有效 47/46 的差异见第 1 项；§2 对卡 AC 行的旧值用 `[ ] <<PARTIAL>>` 摘要而非完整原文，作为“结构性编辑摘要”可接受，但不宜再称“旧值逐字”。

### 6.3 结论

**P1-5.1（通配）与 P1-5.2（after JSON 过期）均已真实修复；P2 allowed-cells 的 (a)(b)(c) 也成立。** 唯一未闭合的是 allowed_paths 的**有效集合**：新增块本身是 45 条精确路径且与 diff 一致，但原 frontmatter 保留了卡自身条目、导致 47 条/46 唯一，另有 `GOV-RESIDUAL` 保留项（不在本次 diff）。这属于 P2（无未授权文件改动、无通配、45 条新增路径正确），故 **verdict = APPROVED_WITH_FINDINGS**；若要求字面「45 条精确集合」，删去重复的卡自身条目（并说明 GOV-RESIDUAL 保留理由）即可，不需要重开 P1。**AC3/AC7 的 `<<MET>>` 在语义上继续成立；AC6 可在完成这一处列表去重/说明后关闭。**
