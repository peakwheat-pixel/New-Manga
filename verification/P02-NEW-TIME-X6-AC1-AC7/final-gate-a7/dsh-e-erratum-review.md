# DSH 独立 Reviewer — E 文档勘误专项复核报告

- **REVIEW_HEAD**：`738759cd3cbd2ca47177b95c64402b57c491ba40`
  （核对方式：读 `…-INTEGRATION/.git` → `gitdir` → `<gitdir>/HEAD` = `ref: refs/heads/codex/p02-newtime-ac-integration-20261015` → `.git/refs/heads/codex/p02-newtime-ac-integration-20261015` = `738759cd…`；与 `final-gate-a7/resource-inventory.json:61` 记录的 integration worktree head 一致。**未执行 `git status/diff/log`**，见"未执行项"。）
- **VERDICT**：**APPROVED**
- 范围：只读；仅核 `final-gate-a7/` 的 `current-summary.json`、`integration-adjudication.md`、`codex-verification.json`、`source-evidence-manifest.json`、`source-manifest-verify.json`（+ 必要原始字段对照）。未重做 full audit、未新增 I3、未写文件/提交/启动 EXE/采集/Build。

---

## 一、四项数值纠偏核对（逐项对原始字段）

### ① DSH-A7-02：I1 四次失败 `node_exit_code` 由派生 null → 1 —— **一致 ✔**

| 场景 | 原始 `execution-metadata.node_exit_code` | 原始 `runner-execution.exit_code` | 原始 verdict | 新 current-summary |
|---|---|---|---|---|
| ac3-debounce-a2 | `1`（…ac3-debounce-a2/execution-metadata.json:55） | `1`（runner-execution.json:6） | `ERROR`（ac3-debounce.json:59-63） | `1` / ERROR / FAIL ✔ |
| ac4-write-refresh | `1`（:55） | `1`（:6） | `ERROR`（element not found `region-frame-syn-region-ac4-001`，ac4-write-refresh.json:82-85） | `1` / ERROR / FAIL ✔ |
| ac4-write-refresh-a2 | `1`（:55） | `1`（:6） | `ERROR`（同上） | `1` / ERROR / FAIL ✔ |
| ac5-keyboard | `1`（:56） | `1`（:6） | `ERROR`（element not found `inspector-revision-history`，ac5-keyboard.json:257-260） | `1` / ERROR / FAIL ✔ |

- 被纠偏的旧派生值确为 `null`：`closeout-a7/rollup-summary.json:145/152/159/166`，原样保留未改。
- 仅术语细节（不构成问题）：原文件字段名是 `runner-execution.json#exit_code`，summary/adjudication 写作 `runner.exit_code`，语义等价。

### ② CV-A7-01：EXE SHA 单字符 B→F 抄录错误 —— **一致 ✔，且未越界**

- 错误串 `…4BEF415F2F0E007…` 全仓仅 2 处命中：`closeout-a7/rollup-summary.json:13`（原样保留）、`integration-adjudication.md:7`（纠错引用说明）。**无第三处扩散**。
- 新 `current-summary.json:13` = `92AC7B8EFB646FE77DF8245B13C9AF9314BEF415B2F0E007B1CDCEA729BC13FD`（64 hex，B 位正确）✔
- 原始侧一致：a7 `ac6-contrast-a7/execution-metadata.json:6` 的 `pinned_exe_sha256` ✔；`closeout-a7/handoff.md:12` ✔；旧 i1/i2 rollup 亦为正确 B 值（错字仅限 closeout-a7 派生文件，"抄录错误"定性成立）。
- "实际 EXE 一致"的独立支撑：`i1/ac1-identity/ac1-identity.json:54-57` 记录 `sha256File(PINNED_EXE)` 实算值 = 正确 B 值，且 `:1172 pinned_binary_hash_matches = true`。
- 未替换/未重建 EXE 与"原始 EXE 未改"一致；EXE 路径当前仍存在（glob 命中）。**本轮未重算 EXE 哈希**（见限制）。

### ③ DSH-A7-04：`source_head`/closeout_base + 三个新字段 —— **一致 ✔**

| 字段 | 值 | 原始对照 |
|---|---|---|
| `closeout_base` | `a8d9219ba192c9a7feb1437240e51535938073fa` | 旧 `rollup-summary.json:17 source_head`、`handoff.md:8`、`findings.md:8` ✔ |
| `source_content_commit` | `cbad5a8f9c82564e37996fdbfc205d69bb154d78` | `closeout-a7/owner-evidence-manifest.json:4-5 source_commit/review_head` ✔ |
| `reviewed_head` | `4abb8d288e005dc58e3270b12389d33cd7a52ac1` | `codex-verification.json:3`、`review-dispatch.json:4`、`current-summary:110/231` ✔ |
| `integration_commit` | `38d926026e9032a528ce578dba7290c5ce65356b` | `codex-verification.json:4`、`current-summary:111/232`、`adjudication.md:3` ✔ |

- 说明（P4 级、非新增、不要求返修）：新汇总不再有字面 `source_head` 键，语义改由 `closeout_base` 承载，已在 DSH-A7-04 明示；无既有消费者依赖该键名。

### ④ 唯一派生口径 + 旧物原样保留/HISTORICAL —— **一致 ✔**

- `integration-adjudication.md:3`：唯一结果 = 本目录 `current-summary.json`，旧 i1/i2/RES 汇总、旧 Handoff、旧 Review 均为历史证据；`:10`（DSH-A7-05）明确 "i2 BLOCKED/旧 Handoff/旧 r1 平铺 PASS 均 HISTORICAL"，且"未移动/删除任何历史文件"。
- 旧 BLOCKED 文件仍在且未改：`runs/p02-newtime-ac-20261014-i2/rollup-summary.json:5 status="BLOCKED"`。
- 旧 Handoff 仍在且未改：`closeout-a7/handoff.md`（Source HEAD `a8d9219b`、`READY_FOR_BOUNDED_REVIEW`）。
- 旧 mutable manifest 原样保留：`RES-P02-AC6-CDP-RECOVERY/manifest/owner-evidence-manifest.json` 仍绑 `e4233e72…`，且含 mutable 路径 `doc/tasks/RES-P02-AC6-CDP-RECOVERY.md`、`doc/handoffs/RES-P02-AC6-CDP-RECOVERY-antigravity-20261015.md`；其历史 verify record 仍为 `PASS/17`，未被改写成新口径（DSH-A7-03 明确其"现时 FAIL 原样保留"，本轮**未复跑**该判定）。
- `resource-inventory.json:97-100` deleted/moved/archived = 0，与 adjudication"删除/迁移/归档=0"一致。

### ⑤ 新 source manifest 排除 mutable、绑定 4abb8d28、官方 verify PASS 102 —— **结构一致 ✔（helper 未复跑）**

- `source-evidence-manifest.json:4-5` `source_commit` = `review_head` = `4abb8d288e005dc58e3270b12389d33cd7a52ac1` ✔（冻结 hex，非手抄占位）。
- `files` 数组恰好 **102** 条，与 `source-manifest-verify.json:7 files_checked=102`、`:2 verify=PASS`、`:3 problems=[]`、`:5-6` 的 source_commit/review_head 完全对齐 ✔。
- 排除 mutable：对 `doc/`、`STATUS`、`REBASELINE`、`orchestrator`、`TASK-`、`runtime`、`checkpoint`、`snapshot` 全文件 grep **0 命中**；条目仅落在 `apps/…/e2e/p02-new-time/**`(12) + `verification/P02-NEW-TIME-X6-AC1-AC7/runs/**`(86) + `RES-…/closeout-a7/**`(4) ✔。
- 无自引用：manifest 不含 `final-gate-a7/*`（尤其不含自身与 current-summary）✔。
- 路径存在性（对 helper 的替代性核对）：102/102 条在磁盘上均可由目录枚举命中 ✔。
- 未复跑：官方 `generate-evidence-manifest.py --verify` 与逐文件 `sha256/bytes/git_blob` 重算。

---

## 二、是否改变 AC 范围 / 原始运行数据 / 返修预算

- **AC 范围未变**：AC1–AC6 的 `status/layer/evidence_dir/各项数值`与旧 `closeout-a7/rollup-summary.json` 逐字段一致；AC7 由旧"Rollup & Findings / READY_FOR_BOUNDED_REVIEW"变为"Evidence / Review / Integration / PASS + APPROVED + reviewed_head + integration_commit"，属集成状态推进而非范围扩大。
- **原始运行数据未改**：四份 `execution-metadata/runner-execution` 文件内容仍为 1（只在派生汇总中纠正引用值）；a7 数值与 `ac6-contrast.json:690-691/705-706/708-709`（samples 10、computed 10、fails []、not_verifiable []、mapped 0/unmapped 10）及 `:461 contrast_ratio 13.87`、`:392 alpha=false` 一致；带 F 错字的旧文件仍为 F（可反证未回改原始/历史文件）。
- **返修预算未变**：`revision-output.json` = `revision_type="E"`、`counts_toward_repair_budget=false`、`reviewer_needed=true`；`convergence-output.json` = `further_implementation_repair_allowed=false`、`forbid_implementation_repair_beyond="I2"`、`reasons: implementation repairs used 2/2`；未开启 I3。本 E 不占 I1/I2。

---

## 三、问题计数

- **本轮新增：P0 = 0，P1 = 0，P2 = 0，P3 = 0，P4 = 0。**
- 保留 backlog（**非新增、不重计**）：`codex-verification.json:39-45` 既有 P3=3 / P4=3；`convergence-output.json:31-42` backlog = DSH-A7-01…06、CV-A7-01、P-01…P-03。
- 非阻断观察（仅记录，不构成 finding、不触发返修）：新 manifest 收录了带 CV-A7-01 错字的旧 Owner 汇总（已由 adjudication 显式标注）；a7 `pinned_exe_sha256` 为 `env.mjs` 常量而非 a7 运行时重算，二进制实算证据来自 I1 `ac1-identity.json`（属既有 P4 限制同类）；manifest 未收录已被 a7 取代的 I1 `ac6-contrast` 原始证据（范围选择，非 mutable 违规）。

## 四、实际执行 / 未执行与限制

**实际执行（只读）**：5 个目标文件全文核对；对 4 份 I1 失败 `execution-metadata`/`runner-execution`、4 份 `ac*.json` verdict、a7 `execution-metadata`、`ac6-contrast.json`、旧 `closeout-a7` 4 件、旧 i1/i2 rollup、旧 mutable manifest 及其 verify record、`resource-inventory.json`、`revision-*/convergence-output.json`、`review-dispatch.json` 的字段对照；manifest 102 条结构/路径存在性核对；HEAD 由 worktree gitdir → refs 读取确认。

**未执行（环境限制）**：
1. 官方 helper `generate-evidence-manifest.py --verify …/source-evidence-manifest.json` **未运行**：本会话任何 `pwsh` 调用（含 `Write-Output` 探测）均失败于 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(<worktree>)`；提权重试因"no approval channel available"被拒。因此逐文件 sha256/bytes/git_blob 零信任重算未做。
2. `git status/diff/log`、EXE `sha256` 与字节数实测未做；"工作区干净"仅由 `resource-inventory.json:62 git_status=[]` 记录支撑，非本轮实测。
3. 旧 mutable manifest"现时 FAIL"未复跑；未执行任何采集/EXE 启动/Build。

**限制**：以上 1–3 为工具层限制，不改变本报告对 E 内容数值纠偏的结论（四项纠偏均已对原始字节级字段逐条比对通过）。Task/STATUS 仍待最终资源/治理收口，本轮未以其 done 与否判断 E 内容。

**结论**：E 勘误的四项数值纠偏与原始数据完全一致，未引入新 P0–P2，未改变 AC 范围、原始运行数据与返修预算；VERDICT = **APPROVED**，无需实现返修。

**建议下一步**：无需任何实现返修；由主控 Codex 继续进行资源/治理与 Task/STATUS 最终收口。若需官方 manifest 零信任复跑与本 E 报告归档，请在具备可执行 shell 的会话中运行：
`python C:/Users/49745/.agents/skills/multi-agent-project-orchestrator/scripts/generate-evidence-manifest.py --repo . --verify verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/source-evidence-manifest.json`（本报告不写文件，由主控保存）。
