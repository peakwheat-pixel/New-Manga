# P7 集成核验记录（DSH，2026-11-13）

**性质：** Lead / Integrator 的机械核验记录（2026-11-13 早期快照），**不是**独立 Review，也不裁决候选。独立 Review 已由 Codex 三轮完成（`reports/CODEX-FINAL-REVIEW`、`CODEX-REREVIEW`、`CODEX-FINAL2-REVIEW-2026-11-13.md`）。
**核验时固定状态：** `HEAD=48ccb75ce1a547cf89e4d38cd577b868e15de5ce`，branch=`main`，工作树 clean。
**ZCode 可用性（历史快照）：** 2026-11-13 19:36（本地）最小 plan 探测返回 provider `1310` / HTTP `429`、EXIT 1、无 session/response；据此当时未执行独立 Review。该状态随后由用户裁决改为 Codex 优先，并已实际执行三轮独立 Review；11 个候选与 `AUDIT-11-INC-001` 均已裁决（见 `reports/11_ISSUES.md`）。

## 1. Canonical Evidence 复算

**方法：** `audit/V1-FULL-AUDIT/tests/verify_canonical_evidence.py` 只读解析 Task 卡 Canonical Evidence 表，逐行用 `git cat-file -t/-e` 定位 commit 与 path，并对 `sha256_basis=BLOB` 的行用 `git cat-file blob` 重算 raw Git BLOB SHA-256。

**结果（更正前）：** 371 行 pins；357 行匹配；**14 行 `FAIL_SHA256`**：

| 域 | evidence 前缀数 | 涉及 commit |
|---|---:|---|
| AUDIT-03 | 10（CORE-LOG/RESULT、REFERENCE-LOG/RESULT、PROBE-LOG/RESULT、COLLECTION-FAIL-LOG/RESULT、LEGACY-EXCLUDED-LOG/RESULT） | `03b1a7acc5a324dcd1884df82d748569b2c7f91e` |
| AUDIT-04 | 4（PROVIDERS-LOG/RESULT、CORE-DETECT-LOG/RESULT） | `c10c3ac39e354f08a068825915ece29bd506e969` |

**根因（已实测）：** 14 项记录值全部是**工作区（CRLF）字节**的 SHA-256，而不是 Git BLOB（LF）的 SHA-256。对每项把 commit 中的 BLOB 做 `LF→CRLF` 变换后，SHA-256 与记录值**精确匹配 14/14**；直接 BLOB 字节则 14/14 不匹配。记录值同时等于当前工作区文件 SHA-256，且这些路径各自只有一次提交（pinned commit），不存在后续内容替换。

**基准依据：** ZCode 对 AUDIT-08 的 closure review 已裁定 Task Canonical Evidence 表继续使用 `sha256_basis=BLOB`，worktree/blob 差异由 CRLF→LF 归一化解释（见 `reports/ZCODE-AUDIT-08-CLOSURE-REVIEW-2026-11-13.md`）。本核验沿用该基准。

**处置：** 按上述基准把 14 行的记录值更正为对应 commit 的 raw Git BLOB SHA-256；`class`/`sha256_basis`/`path`/`commit` 不变。逐项旧值/新值见 `evidence/task-card-pin-correction-20261113.json`。复算原始输出分两份：更正前（对从 `HEAD` 精确导出的 133,609 字节原卡副本运行，`TASK` 指向该副本）为 `logs/task-card-pin-recompute-20261113-pre-correction.log` / `evidence/task-card-pin-recompute-20261113-pre-correction.json`，**357 pass / 14 fail**；更正后（当前 Task 卡）为 `logs/task-card-pin-recompute-20261113.log` / `evidence/task-card-pin-recompute-20261113.json`，**371/371 PASS、failed=0**。

**pinbackfill 后复核（历史检查点）：** 本轮回填新增 27 条 pins（ZCode 额度复核 3、复算/更正 6、报告/脚本 2、52b86d39 gate batch 8、ed17a790 gate batch 8）后，Task 卡当时共 398 条 pins；按同一 BLOB 算法复算 **398/398 PASS**，见 `logs/task-card-pin-recompute-20261113-final.log`、`evidence/task-card-pin-recompute-20261113-final.json`。

**待 ZCode 复核：** 是否接受该更正；是否需要把本审计其他文档（例如历史报告）中的 worktree SHA-256 标注统一标注为 WORKTREE 基准。

## 2. 报告与台账一致性

| 核对项 | 结果 |
|---|---|
| 已 triage 产品 finding：`SEG-B-PROBES-001`、`SEG-B-PROBES-002`（Medium / High confidence）、`NM-AUD-0001`（P2） | `11_ISSUES`、`AUDIT_ISSUES`、`FINAL_AUDIT_REPORT`、`13_RELEASE_GATE` 计数与内容一致（3 项） |
| 未决调查风险 `AUDIT-11-INC-001` | 1 项，`INVESTIGATE`，无正式 severity，一致 |
| REVIEW_PENDING 候选 | 11 项；逐 ID 核对：05-1、06-1、06-2、07-1、07-2、09-1、12-1、14-1…14-4，共 11/11 |
| 已披露关闭的非产品观察 `AUDIT11-REV-001` | 1 项；P3 observation，已关闭，不计产品问题，一致 |
| P0 / P1 / P2 / 开放 P3 产品 finding | 0 / 0 / 1 / 0；各处均注明“未分配不等于证明不存在”，一致 |
| pytest 3,519 passed / 16 failed / 10 skipped / 11 warnings / EXIT 1 | Task 卡 AC2、`AUDIT_TASKS`、`FINAL_AUDIT_REPORT`、`13_RELEASE_GATE` 一致 |
| Avalonia TestHost 8/8 runner EXIT 1、TRX 0 tests；smoke EXIT 1；AUDIT-13 31 passed / 0 skipped / EXIT 0 | 同上四处一致 |
| AC 状态：AC1 MET；AC2/AC3/AC4 PARTIAL | Task 卡、`STATUS`、`REBASELINE_PLAN`、`AUDIT_STATUS` 一致 |
| Release Gate：BLOCKED，不建议发布 | `13_RELEASE_GATE` 六条阻断依据与 `FINAL_AUDIT_REPORT` 一致 |
| R1–R4 处置顺序 | `12_REMEDIATION_PLAN` 为 R1（SEC-01/02/03）→ R2（CORE-01）→ R3（候选 + VAL-01…04）→ R4（14-CAND-001…004），无逆序引用 |

**发现的文档漂移（记录，不自行定级）：**

1. `AUDIT_STATUS.md` 第 28 行仍写 `AUDIT-07/09/10/12/13 NOT_TESTED`；该段自称“逐项状态以原件恢复后的最新裁决为准”，但与同文件顶部及 `AUDIT_TASKS.md` 的最新 `PARTIAL` 相矛盾，容易被误读为当前状态。
2. `AUDIT_PLAN.md` 第 5 行与 `AUDIT_EVIDENCE_INDEX.md` 的 P7 条目仍停在 `3a1cecca` / `77310033` 批次，未包含 `ed17a790` 与本轮批次。
3. Task 卡 AC4 文本仍描述旧 gate batch（`generated HEAD=77310033`）。
4. Task 卡 14 项 pin 的 SHA-256 基准错误（已在第 1 节更正）。
5. `AUDIT-05/06` 与 `AUDIT-14` 的 7 项候选当时保持 `REVIEW_PENDING`（阶段快照）；后续已由 Codex 七轮 Review 全部裁决；`AUDIT-08` P3-4 已由第七轮复审关闭。

**处置：** 更新 `AUDIT_STATUS.md`、`AUDIT_EVIDENCE_INDEX.md`、Task 卡 Rolling checkpoint 与 AC4 文本；漂移 1 保留原文历史性说明并在检查点标注最新状态。其余项的独立 Review 已由 Codex 完成（首轮与复审均 REJECT，要求返修；见 `reports/CODEX-FINAL-REVIEW-2026-11-13.md` 与 `reports/CODEX-REREVIEW-2026-11-13.md`）；DSH 仅做集成与返修，不自行裁决候选。

## 3. 本轮未执行的检查（具名限制）

- **未执行**（本记录自身）：独立 Review、11 候选裁决、`AUDIT-11-INC-001` 处置、AUDIT-08 P3-4 fresh re-review；这些已由 Codex 七轮 Review 完成（见 `reports/` 下对应报告），P3-4 已关闭。
- **未重跑** 重型测试、真实模型 / 人工 GT / 付费 API、完整 GUI 编辑与导出、accessibility/DPI、clean Windows install/upgrade/rollback/uninstall、长时 soak 与完整 shell 流程；这些继续按原报告保留 `NOT_RUN` / `BLOCKED`。
- **未访问** 远端、未 push、未删除、未改产品源码 / 既有测试 / 契约 / Schema / 依赖 / 真实用户数据 / Git 历史。
- **未安装** 任何工具或依赖；AUDIT-02 的工具缺口保持原状。

## 4. 结论边界

本记录只说明：在当前固定 HEAD 上，Canonical Evidence 的 Git BLOB 可机械复核——更正后当时 **371/371**，积压回填后 **398/398**，首轮返修后 **428/428**，复审与最终复审回填后 **441/441**（当前 Task 卡 441 条）；报告的计数、AC 与 Gate 文字自洽。它**不**构成 Review、候选裁决、产品通过或 Release Gate 解锁；Release Gate 维持 `BLOCKED`，Task 维持 `in_progress`，AC3/AC4 维持 `PARTIAL`（AC1/AC2 已 `MET`）。
