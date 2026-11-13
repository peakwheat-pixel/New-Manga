# P3-a · 两处 `TaskPath FAIL` 处置（MAINT-1，2026-11-14）

来源：`FEA-15-PIN-BASIS-ENFORCE-1` 保留限制「`FEA-06-PREREQ-1` TaskPath FAIL（13 errors）、`CHAPTER-SELECTOR-1` TaskPath FAIL（6 errors）」。

## 1. `CHAPTER-SELECTOR-1` — 已修复并转绿

**性质**：纯格式不兼容，非事实问题。5 个 AC 均为 `[x]` 且正文已写 `→ **MET**：…`，检查器要求行末 `<<MET>>` 标记。

**改动（6 行，append-only 语义）**：
1. AC1–AC5 行末补 `<<MET>>`（不新增任何主张，仅把已有结论变成机器可读）。
2. Resource Manifest 的 `sha256/manifest` 列原为长描述文本，检查器按路径解析失败；改为真实存在的证据索引 `verification/CHAPTER-SELECTOR-1/live-evidence.json`，并把原描述**迁入** `reference/process check and result` 列（原文保留，未删）。

**验证**：`check.ps1 -TaskPath doc/tasks/CHAPTER-SELECTOR-1.md` → **PASS**（3 warnings）。diff 为 6 增 6 删，无换行符污染。

## 2. `FEA-06-PREREQ-1` — 仅诊断，未修改

**性质**：状态与证据自相矛盾，不能靠补格式解决。当前 13 个错误分四类：

| 类 | 错误 | 说明 |
|---|---|---|
| A 状态口径 | `DONE 不能保留未完成 AC`；AC1/AC3 为 `PARTIAL`；AC1/AC3/AC5 为 `[ ]` 无标记 | 卡面 `canonical_evidence_status` 自述「AC1/AC3/AC5 residual 已转 PREREQ-2」，但检查器没有"转出"概念，只认 MET/PARTIAL/BLOCKED/NA |
| B 字段格式 | `canonical_evidence_status` / `resource_closeout_status` 的值带了括号说明，不等于字面 `complete` | 值本身是"带注释的 complete" |
| C 证据重钉 | 4 条 `Evidence SHA-256 不匹配`（appearance-tests / motion-tests / sln-test / build）；`Canonical evidence 路径缺失：…/Services/AppearanceCoordinator.cs` | 与「30 条 pin 中 27 条跨 checkout 不可复现」同源：pin 基于别的 checkout/时点，当前工作树复现不出 |
| D 清单 | `DONE 必须逐项填写 Resource Manifest`、`evidence_dir 含未登记文件`（3 个） | 清单未随后续新增证据更新 |

**为何本轮不改**：
- C 类只能通过**重钉证据**解决，属于 pin 基准策略（`FEA-15-PIN-POLICY-1` / `PIN-BASIS-ENFORCE-1` 的既有议题），必须独立成卡并保留历史 pin 字节，不能顺手改哈希。
- A 类的正确处置需要二选一裁决（见下），涉及历史 AC 行语义，不能由本轮单方面改。

**处置选项（待裁决）**：

| 选项 | 做法 | 代价 |
|---|---|---|
| **O1**（推荐） | AC1/AC3/AC5 行末追加 `<<NOT_APPLICABLE: residual 已转 FEA-06-PREREQ-2 AC5/AC6>>`；字段值改为字面 `complete`（说明移到正文注释行）；清单补登记 3 个未登记文件；SHA 漂移另立 pin 卡 | 改 A/B/D 三类，C 类仍 FAIL，所以本卡**不会转绿** |
| O2 | 保持 `done`，把整卡标记为已知治理债，不再尝试修复 | 零改动，但 `FEA-15-PIN-BASIS-ENFORCE-1` 的保留限制永久存在 |
| O3 | 状态改 `closed_with_limitations` | 与 TASK_LEDGER 计数、历史 Review 冲突，代价最大 |

**本轮结论**：取 O2（保持现状、登记债），并把 O1 留给后续 pin 策略卡；理由是本轮不重钉证据、不改历史 AC 语义，符合红线 2/4。若后续判定 C 类可解，再按 O1 + pin 卡一次性收口。

## 3. DoD 影响

`check.ps1` **默认**运行（DoD §4 所指）始终 PASS；两处失败仅在 `-TaskPath` 单卡模式下暴露。
`CHAPTER-SELECTOR-1` 关闭后，单卡 FAIL 清单从 2 张降为 1 张（`FEA-06-PREREQ-1`）。
