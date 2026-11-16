# MAINT-1 Gate 条件 6 收口独立复核报告（2026-11-16）

- **verdict:** `APPROVED_WITH_FINDINGS`
- **被复核 head:** `b18a2ef904667be6b074b7dd0f38fa09053516c6`（复核全程 `git rev-parse HEAD` 未变）
- **reviewer:** 独立上下文子 agent `c6-reviewer`（由 DSH lead 派发）；未参与 `MAINT-1-RELEASE-MONITOR` / Gate 条件 6 的任何实现、返修或此前 Review；只读复核，唯一写入为本报告。依据 2026-10-31 裁决，独立性按「上下文独立」口径成立。
- **判据:** `audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:30`；剩余动作原文 `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md:229-237`；被复核收口报告 `doc/reviews/MAINT-1-GATE-CONDITION-6-CLOSURE-2026-11-16.md`。
- **复核时点:** 2026-11-16T15:37–15:50 +08:00（UTC 07:37–07:50）。
- **工作区说明（诚实登记）:** 复核开始时 `git status --porcelain` 为空；15:39 起出现两处**非本会话产生**的未提交改动（`doc/handoffs/NEXT-SESSION-STARTER.md` 修改、`doc/reviews/GOV-DECLARATION-SCAN-CLEANUP-1-AC3-BASELINE-REDERIVATION-2026-11-16.md` 未跟踪），HEAD 未移动，本报告不将其纳入被复核 head 的事实（见 P2-4），本会话未触碰这两处文件。

## 1. 复核方法与实测清单

### 1.1 四件套重跑（本机、被复核 head、只读）

| # | 命令 | 实测结果 | EXIT | 与 `gates.log` 对照 |
|---:|---|---|---:|---|
| 1 | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)`；WARN 13 个非终态 Task / STATUS 3177 B/28 行 / PLAN 6960 B/64 行 | 0 | 判定行、EXIT 一致（`gates.log:17-18`）。STATUS 3174→3177 属被复核 head 自身对 STATUS 的更新（`git diff 6a408e5aa b18a2ef90 -- doc/STATUS.md`） |
| 2 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/MAINT-1-RELEASE-MONITOR.md` | `Governance check: PASS (3 warnings)` | 0 | 一致（`gates.log:27-28`） |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，C01b…FEA01 全 `OK` | 0 | 一致（`gates.log:50-51`） |
| 4 | `python -B tools/generate_api_inventory.py --check` | `OK: rendered counts match FEA-C07 doc`（表 `1/80/6 = 87`） | 0 | 一致（`gates.log:168-169`） |
| — | `apps/desktop-avalonia/scripts/test.ps1` | **按复核指示未重跑**（8 分钟且会改写证据文件）；以 `gates.log` §5 与内嵌 summary JSON 为准：`TEST PASS (Debug): 1591/1639 passed, 48 skipped`（EXIT=0，`gates.log:701-704`）；summary 内部自洽 `1591 = 258 + 364 + 969`、`48 = 0 + 44 + 4`（`gates.log:663-694`） | 0（日志） | 一致 |

重跑命令 1 的耗时 1 s；命令 2 为 1 s；命令 3 为 0.3 s；命令 4 为 0.1 s。默认 check 在本次重跑时工作区已被上述**非本会话**改动污染，仍 PASS（该两文件不在 `check.ps1` 的 15 份当前文档范围内）。

### 1.2 13 张非终态卡的 `-TaskPath` 重跑

按 `check.ps1:258` 的终态集合（`done / closed_with_limitations / cancelled / superseded / historical`）独立枚举 `doc/tasks/*.md` 的 `status:`：

`in_progress` 6（`DOC-CTRLCHAR-FIX-1`、`GATE3-MATRIX-EXPAND-1`、`GATE3-SETTINGS-SHORTCUT-1`、`INSTALLER-MATRIX-1`、`MAINT-1-RELEASE-MONITOR`、`SIDECAR-REBUILD-1`）、`in_review` 2（`GIT-CLEAN-PUBLICATION-1`、`GIT-CLEAN-RUST-ISOLATION-1`）、`proposed` 2（`GIT-CLEAN-CORE-ENV-2`、`GOV-DECLARATION-SCAN-CLEANUP-1`）、`blocked` 1（`FEA11-ENTRY-MISSING-1`）、`approved` 1（`GIT-CLEAN-PUBLICATION-DIAG-1`）、`ready` 1（`GIT-CLEAN-RUST-CAPACITY-DESIGN-1`），合计 **13**。

逐张重跑 `check.ps1 -TaskPath doc/tasks/<ID>.md`：**13/13 rc=0、`Governance check: PASS (3 warnings)`**（合计 12.9 s），与 `p2-2-before-after.log:19-32` 及“13/13 全 PASS”声明一致。

### 1.3 三口径重算（§3 载体）

对 `doc/tasks/MAINT-1-RELEASE-MONITOR.md:384-393` 的 8 行，按表内 `commit:path` 用 `git cat-file blob` 取原始字节重算 SHA-256，并 `git cat-file -e`：

- **8/8 PASS，0 FAIL**：`EV-MR-1`…`EV-MR-4`（commit `6a408e5aa`）、`EV-C6-1`…`EV-C6-4`（commit `3cc4e1186`）全 64 位十六进制值与表内一致，`cat-file-e=0`。
- 与 `threeway.log:8-23` 的 8 行 PASS 一致（该日志 expected/actual 只打印 16 位前缀，故本复核按表内全值独立复算，而非只看日志）。
- 证据文件实际字节：`MAINTENANCE-RECORD.md` 4912 B、`model-api-verification.log` 616 B、Final Review 20559 B、Errata 载体 6704 B、`gates.log` 40120 B、`p2-2-before-after.log` 2592 B、`resource-closeout.log` 922 B、收口报告 7997 B。

### 1.4 交付头 / 变更面 / 绿洗的独立检查

- `git log --oneline 6a408e5aa..b18a2ef90`：`96c548444`（收口 A：载体+登记+精度修复+P1-1）→ `45af57007`（Resource Manifest 格式修复）→ `3cc4e1186`（证据）→ `b18a2ef90`（卡面字段+三口径）。
- `git diff --stat 45af57007 b18a2ef90`：9 文件、884 插入、10 删除；仅 `doc/STATUS.md`、收口报告、Task 卡、4 个 `condition6-closeout/*`、`threeway.log`、`verification/READER-OVERLAY-HEADLESS-PNG-1/render-info.md`。
- `git diff --name-only 45af57007 b18a2ef90 | grep '^(tools|apps|src|tests|doc/contracts)/'` → 空；`git diff 6a408e5aa b18a2ef90` 的非 `doc/|audit/|verification/` 路径 → 空；`git diff 6a408e5aa b18a2ef90 -- tools/governance/check.ps1` → 空。**零源码/测试/契约/pin/阈值改动成立。**
- Gate 文档 `git diff -U0`：`13_RELEASE_GATE.md` **+13/-0**、`RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md` **+16/-0**（纯追加，见 §2 第 6、7 项）。
- `verification/READER-OVERLAY-HEADLESS-PNG-1/`：`git diff 6a408e5aa b18a2ef90` 为空；但中间态 `45af57007` 的该文件 blob 为 `578b19f285`（706 B），基线 `6a408e5aa`/`3cc4e1186`/`b18a2ef90` 均为 `96d7ef7ba6`（1345 B）——说明测试副作用先在 `45af57007` 被提交、后在 `3cc4e1186` 恢复（P2-3）。
- 载体/字段跨提交：`6a408e5aa`/`96c548444`/`45af57007`/`3cc4e1186` 的 `integration_commit`/`delivery_head` 均为 `null`、两 status 均 `pending`；只有 `b18a2ef90` 为四值落定，且 `EV-C6-*` 四行仅从 `b18a2ef90` 起存在（P1-1）。
- EOL 仿真（不改文件）：`git cat-file --filters HEAD:doc/REBASELINE_PLAN.md` = **7024 B**（64 CRLF）、`HEAD:doc/STATUS.md` = **3205 B**（28 CRLF）；`.gitattributes:40` 仅对 `doc/tasks/*.md` 钉 `eol=lf`，`:17` 钉 `check.ps1`，未覆盖这两个预算文件；`core.autocrlf=true` 来自系统 `C:/Program Files/Git/etc/gitconfig`（P2-1）。
- 非终态枚举与 PLAN 覆盖：`6a408e5aa` 的当前 DAG 文本只覆盖 13 张中的 **7** 张（缺 `FEA11-ENTRY-MISSING-1`、`DOC-CTRLCHAR-FIX-1`、`GATE3-MATRIX-EXPAND-1`、`GATE3-SETTINGS-SHORTCUT-1`、`INSTALLER-MATRIX-1`、`GOV-DECLARATION-SCAN-CLEANUP-1`）；`b18a2ef90` 覆盖 **13/13**。`BLOCKED：FEA11-ENTRY-MISSING-1` 与唯一 `blocked` 卡一致；`表外节点` 行 9 项均为非终态、无终态卡残留（P2-7 另有 SIDECAR 行冲突）。

## 2. 逐项结论

| # | 复核项 | 结论 | 关键证据 |
|---:|---|---|---|
| 1 | 四件套实测真实、可复现 | **PASS**（附 P2-1/P2-2/P2-5） | 见 §1.1；`gates.log:3,5,17-18,27-28,50-51,168-169,174-177,701-704`；命令/`# head:`/`EXIT=` 与判定行自洽；`.NET` 未重跑但 summary 自洽。可复现性有 EOL 前提（P2-1） |
| 2 | 交付 head 命题 | **FAIL（部分成立）** | “其后两个提交只加证据/卡面字段、零源码/测试/契约/pin”成立（§1.4）；但 `45af57007` 上四字段仍 `null/pending`、`EV-C6-*` 四行尚未存在，且该提交包含 `render-info.md` 测试副作用（`git show 45af57007:doc/tasks/MAINT-1-RELEASE-MONITOR.md` 与 `git show 45af57007:verification/.../render-info.md`）。载体完成态实际在 `b18a2ef90`（P1-1/P2-3） |
| 3 | 载体成立性（7 列 BLOB / Manifest / Closeout / 三口径） | **PASS**（附 P2-4/P2-6/P2-8/P2-9） | `doc/tasks/MAINT-1-RELEASE-MONITOR.md:376-393`（7 列、8 行全 `BLOB`）、`:395-404`、`:406-414`、frontmatter `:16-20` 四字段与 Closeout 一致；三口径 8/8 独立复算（§1.3） |
| 4 | §3.2-③ / P2-2 修复名副其实 | **PASS**（附 P2-7） | 独立枚举 13 张非终态卡；`doc/REBASELINE_PLAN.md:59-60` 覆盖 13/13；13/13 `-TaskPath` PASS；`BLOCKED` 与唯一 blocked 卡一致；`表外` 9 项均非终态、无终态残留 |
| 5 | P1-1 处置是否过度/不足 | **PASS**（残风险低） | `doc/reviews/MAINT-1-FEA-LINE-CLOSEOUT-v2-2026-11-14.md:58-66` 明写“不等于 8/8 MET”；`MAINT-1-FEA-POST-ROADMAP-2026-11-14.md:8` 无 MET 断言；`verification/MAINT-2-C1-BATCH-1/README.md:5` 原文即 `AC8 … = PARTIAL`；卡 `:366-369` 登记“轮次 24 按 Errata 读” |
| 6 | 是否有绿洗 | **FAIL（文档级）** | 无代码/测试/check 阈值/契约/pin 改动（§1.4），Gate 两文档纯追加；但 `doc/REBASELINE_PLAN.md` 压缩删除了 `:49` 的“根因 UNKNOWN”、`:53` 的“仅部分证据”、`:45` 的“（AC3 limitation）”、`:52` 的“NOT_RUN 见卡面”、`:63` 两个节点的 `done`，与收口报告 `:35` “语义、状态与 commit hash 未变”不符（P1-2） |
| 7 | Gate 总体未被偷偷升级 | **PASS** | `audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:3` 仍 `**结论：BLOCKED**`、`:32` 发布决定原文未改（+13/-0）；新增段 `:34-45` 明写“Gate 总体仍 BLOCKED”；`doc/STATUS.md:8` 仍 `Release Gate **BLOCKED**`（仅条件 6 改为“已关闭”） |

## 3. Findings

### P0

无。

### P1

**P1-1（交付 head 与载体完成态错位；Gate 登记早于事实）**
收口报告 `:52-53` 称 `45af57007` 是“载体、登记与精度修复的最终内容提交”，但：
- `git show 45af57007:doc/tasks/MAINT-1-RELEASE-MONITOR.md` 的四个字段仍是 `integration_commit: null` / `delivery_head: null` / `canonical_evidence_status: pending` / `resource_closeout_status: pending`；三节中 `Canonical Evidence` 只有 `EV-MR-1…4` 4 行，`EV-C6-1…4`（四件套/ P2-2 / 资源 / 收口报告）到 `b18a2ef90` 才出现。
- 四件套实测（`gates.log:3` 的 head=45af57007）因此是在“载体字段未落值、Gate 证据行未落表”的树上跑的；而条件 6 动作 ② 明确要求这四字段。
- 13_RELEASE_GATE 的“四项完成态缺口已逐项关闭”段于 `96c548444` 提交（`gates.log` 的 head 尚未冻结、四字段仍 pending），属于提前登记；最终状态由后续提交补齐，但“交付 head 上载体已完成”这一命题不成立。
- 建议：要么把 `delivery_head` 改成“载体落值后的最终 head”并在该 head 重跑三项快速门禁（check/pins/inventory，非 .NET），要么在收口报告/卡面明写“门禁在内容 head 45af57007；四字段与三条 Gate 证据行为事后回填，gated 面为 docs-only 差异”，并同步修正 `:52-53` 的措辞。

**P1-2（PLAN 压缩删除实质限定信息，与“语义/状态未变”声明不符）**
收口报告 `:35` 称压缩“语义、状态与 commit hash 未变”，但 `git diff 6a408e5aa b18a2ef90 -- doc/REBASELINE_PLAN.md` 显示至少五处实质信息被删：
- `:49` `3 done（ZCode；根因 UNKNOWN）` → `3 done（ZCode）`（删除根因未定 caveat）；
- `:53` `done（…；零 src；仅部分证据）` → 删除“仅部分证据”；
- `:45` `A3 closed_with_limitations（AC3 limitation）` → 删除 AC3 limitation；
- `:52` `均 done（…；各 ACCEPT_WITH_LIMITATIONS，NOT_RUN 见卡面）` → 删除“NOT_RUN 见卡面”指针；
- `:63` `CLEANUP-TOOL-HARDENING-1 done（368c07809）` / `DECLARATION-REMEDIATION-1 done（bb7887442）` → 删除两个 `done` 状态词。
此改动不改变产品结论，但在权威 PLAN 中删除 caveat/状态词，属于“弱化披露”；且报告声明不实。当前 PLAN 6960 B、上限 7000 B，仅余 40 B，不足以全量恢复上述约 80 B 文本；建议（a）在 PLAN 其他历史行继续压缩同量文本后恢复这 5 处限定，或（b）把限定迁入 `doc/TASK_LEDGER.md` / 对应卡面，并在 PLAN 留短指针（如“caveat 见 TASK_LEDGER”），同时更正报告措辞。

### P2

**P2-1（字节预算的 EOL 前提未钉死；fresh checkout 会超限）**
`check.ps1:661-669` 用工作树字节判定 `STATUS ≤ 3200`、`PLAN ≤ 7000`。当前工作树是 LF（6960/3177），但在 `core.autocrlf=true`（系统 gitconfig）下 checkout 形态为 `PLAN 7024 B`、`STATUS 3205 B`（`git cat-file --filters` 实测），两者均超预算；`.gitattributes:40` 只钉了 `doc/tasks/*.md`，未覆盖这两文件。即“PLAN 6960 B / 保留 40 B 余量”只在 LF 工作树成立，fresh clone 会令默认 check FAIL。该问题在本轮前已存在（6990→7054 的老口径亦如此，`doc/handoffs/NEXT-SESSION-STARTER.md:212` 有同类记录），但条件 6 的“default governance 门禁可复现”应补此前提。建议按既有 GOV-EOL-PIN 先例为 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md` 加 `text eol=lf`，并在 clean checkout 上复跑记录。

**P2-2（`gates.log` §5 启动时点与 elapsed/finished 不自洽）**
`:3` 起跑 `07:25:49Z`；`:175` 写 `started_utc: 2026-11-16T07:25:5x（紧接上面四项之后）`；`:176`/`:702` 为 `finished 07:34:28Z` / `elapsed=461s`，倒推起点应为 `07:26:47Z`。四件快速门禁本机实测合计约 2.5 s，无法填平约 55 s 差；该窗口恰与 `p2-2-before-after.log:4` 的 `07:26:20Z` P2-2 实验重合，故“紧接上面四项之后”与时间戳都不准确。不影响 head/EXIT/判定行。建议更正为实际起点或注明 p2-2 实验插在中间。

**P2-3（`45af57007` 提交了测试副作用；README §4 “提交前恢复”表述不准确）**
`verification/READER-OVERLAY-HEADLESS-PNG-1/render-info.md` 在 `45af57007` 为 706 B（测试产物），`3cc4e1186` 才恢复 1345 B 基线；最终 `6a408e5aa..b18a2ef90` 为空。该路径不在本卡 `allowed_paths`（不含 `verification/READER-OVERLAY-HEADLESS-PNG-1/**`），`45af57007` 实为一次越界写入（虽净零）。`condition6-closeout/README.md:36-38` 的“本次已在提交前用 `git checkout` 恢复”应改为“在证据提交中恢复”。

**P2-4（Closeout Record 的 rolling checkpoint 声明在 head 上不成立；且该路径不在 allowed_paths）**
卡 `:414` 称“STATUS / Plan / TASK_LEDGER / rolling checkpoint（NEXT-SESSION-STARTER）已更新至本轮”，但 `git show b18a2ef90:doc/handoffs/NEXT-SESSION-STARTER.md` 的 `:5`/`:21`/`:31` 仍是 R15 / head `74b2a704a`，未含 R16；复核期间（15:39）观察到未提交的 R16 版本，但未被本 head 收纳。且 `doc/handoffs/**` 不在本卡 `allowed_paths`。建议：把该更新与 allowed_paths 一并登记，或把该句改为“STATUS/Plan/TASK_LEDGER 已更新；NEXT-SESSION-STARTER 随后续文档提交更新”。

**P2-5（收口报告逐项目数字与日志不符）**
收口报告 `:67` 写 `CoreClient 256/0/0`，但 `gates.log:663-667` 的 summary 为 `total 258 / passed 258 / failed 0 / skipped 0`，且报告自己的总数 `1591 = 258 + 364 + 969` 要求 258。应改为 `258/0/0`（`256` 是上一轮旧数字）。

**P2-6（Resource Manifest 的 dataset/model 指针悬空）**
卡 `:404` 称“ONNX 权重 pin 见 `GATE4-MODEL-RECOVERED-1` 的 Canonical Evidence”，但 `doc/tasks/GATE4-MODEL-RECOVERED-1.md` 从未存在（`git log --all -- doc/tasks/GATE4-MODEL-RECOVERED-1.md` 为空），实际只有 `verification/GATE4-MODEL-RECOVERED-1/README.md`，其标题为 §1–§7、无 Canonical Evidence 节。该行是 `NOT_APPLICABLE` 的附带指针，建议改为指向该 README 或 `doc/reviews/EVIDENCE-INDEX-2026-11-15.md:49`。

**P2-7（SIDECAR 行状态与卡/台账冲突；P2-2 叙述少计 1 张）**
`doc/REBASELINE_PLAN.md:56` 仍写 `SIDECAR-REBUILD-1 … done`，而 `doc/tasks/SIDECAR-REBUILD-1.md:6` 与 `doc/TASK_LEDGER.md:48` 均为 `in_progress`；`-TaskPath` 只查 ID 是否出现在当前 DAG（`check.ps1:702`），因此不会发现该状态冲突。此为既存问题，本轮未引入也未修复，但“三指针精度”标题下宜登记。另：收口报告 `:21`（及卡 `:360`）说“漏掉 5 张非终态卡”，实际 PLAN 前态漏 6 张（含 `GOV-DECLARATION-SCAN-CLEANUP-1`）；同节 `:30` 已单独披露第 6 张，属叙述精度问题。

**P2-8（`canonical_evidence_status: complete` 的语义风险）**
卡在 `status: in_progress`（伞形哨位）下设 `canonical_evidence_status: complete`，该字段在其他卡通常表示任务级证据完整；Closeout `:413` 已明确“保持 in_progress、不冒充 done”，风险被披露，但工具/读者仍可能把它读成完成信号。建议在 frontmatter 附近或 Closeout 首行加一句“complete 仅指条件 6 载体，不代表 Task 完成”。

**P2-9（`resource-closeout.log` 格式小缺陷）**
`:3` 的 `# at_utc:` 被换行截断（时间值落到 `:4` 且无 `#` 前缀）；`:9-12` 四个 theme 根字节数为空（四项合计 0，`380788+380769+380784+380791 = 1,523,132` 仍成立）。不影响核销结论，建议修正日志格式。

## 4. 结论

**条件 6 在最终 head `b18a2ef90` 上实质成立**（default governance / TaskPath / verify_pins / API inventory 全 PASS，载体三节与 7 列 BLOB 表、三口径 8/8 独立复算、13/13 非终态卡登记与 `-TaskPath` 均成立），但“交付 head `45af57007` 即载体完成头”与“PLAN 压缩语义/状态未变”两项 P1 须修正后方宜采纳；**Gate 总体仍 `BLOCKED`**（`13_RELEASE_GATE.md:3/:32`、`STATUS:8`，条件 3/4/5 未关闭）。
