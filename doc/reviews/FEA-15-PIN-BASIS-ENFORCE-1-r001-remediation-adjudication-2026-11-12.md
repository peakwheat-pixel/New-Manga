# FEA-15-PIN-BASIS-ENFORCE-1 追加裁决：R-001 失败行处置路径（2026-11-12，同会话第二裁）

| 项 | 值 |
|---|---|
| session | `sess_14d54cdc-c657-466a-9678-23eb966f8ea1`（与本会话第一裁同一 fresh 会话；与 sess_1bff86d4 及其余既往 session 均不同） |
| 本轮 decision turn | `turn_4707ecd4-9c3c-4132-a3c3-f8cd8af535c9`（rollout `turnId` 字段实测） |
| reviewed HEAD | `d4c4d9ffbbd3a59f79f4cd242dac19ffa23af1eb`（main，clean，未变） |
| decision | **择 A：授权活动卡最小收口订正并重审**（详见下）；R-001 此刻仍 OPEN，仅在订正后全行 audit `EXIT=0` 且日志入库时按 sess_1bff86d4 **原条件、不修订**关闭 |

## 一、对前授权断言的复核

- 上一份报告写“用户明令不得自动批准修改”，依据是**当时任务书原文**（“不得自动批准修改”“不要自行修改任何源/历史文件或 pins”）——在当时语境下该表述正确。
- 本轮用户已以当前活跃对话指令显式更新授权：“持续推进，全部授权……裁决交给 ZCode”“不需要人工批准，你自己批准”“额度已恢复，继续停止的任务”，并自我限定：**不是** 18 frozen pins/冻结契约修改许可、**不是** push 授权。我照单采信：裁决内事项由我裁定，不再退回用户；push 与冻结物修改继续排除。

## 二、约束冲突的逐字裁定（决定性推理）

sess_1bff86d4 §3 D2 原文三条款并存：(1) 失败行“**按 P2-1 双口径惯例如实区分 worktree/blob 基准并登记**”；(2) R-001 关闭条件＝收口提交内全行 blob audit `EXIT=0`；(3) “不得修改 pin 字节或历史行来凑 PASS”。

- **宽解读**（任何既有行 pin 字节都禁改）下，(1)+(2) 逻辑上不可同时满足——失败行 pin 现为 worktree/原件值，不改则 audit 永远 FAIL，R-001 永不可关，(1) 的“区分并登记”无处落地。该解读使同一裁决自相矛盾。
- **窄解读**（禁令射程＝无证据篡改、抹除原值、触碰历史文件字节以制造虚假 PASS）下，(1)(2)(3) 协调一致，且与本卡 174 行先例（“卡内 pin 指向实际 Git blob……工作树 SHA 另行登记”、ac1c-boundary-matrix 四行即此形态）、AC4 §2.2 双口径定义（“Canonical pin=Git blob 字节；生成日志 SHA=生成时工作树字节”）、R-001 义务原文（“BLOB pin 指向包含文件的实际 commit”）体系一致。
- **裁定采窄解读**。这不是预设优先级，而是唯一使既有裁决体系自洽的读法；该解释性裁定本身随本报告留痕，可被后续 adjudicator 复核推翻（若被推翻则自动落入 B 停止态）。AC4 P2-1 必要条件 (b)“历史日志与 pins 字节不动”所指的是**当时已正确（blob 值、主链路 22/22 PASS）的六组 pin 与六份历史日志原件**，其场景与本次 10 行（pin 写反方向）相反，不构成对本次订正的禁止；条件 (a)“双口径声明不得删除”本轮只增不删，完全遵守。

**订正≠凑 PASS 的判别**：每个新值均为 git 历史实测唯一值（行 1 commit、行 9 blob SHA）或本卡已确立语义的正确值（10 行 blob 值）；原 generation-time 值**永久保留**于卡内说明段并注明证据来源；外部原件与已入库 evidence 字节不动；audit 仍可由任何第三方独立复跑。本轮**不把 EXIT=1 改判 PASS**——该审计日志原样入库，作为订正前事实记录。

## 三、具体授权（择 A）

**允许（授权 Owner=Codex 在写会话执行，无需再等人工批准）**，仅限以下字节：

1. **行 1** `ac2ac3-ac4-v2-review-readme`：仅 commit 列改为 `d714232eefbe66e62f15b4534dce90d22927ddc5`；**pin 字节不动**（该 commit 中 README blob SHA 已实测==pin）。
2. **行 9** `ac5-review-readme`：仅 sha256 列补全为 `596bfde7c22a53b3ae3b49bc50b016eaa5669ab4460b67ce61ea5f7fbecdc9b0`。
3. **10 个 EOL 行**（#2–#8、#10–#12）：仅 sha256 列改为各自 actual（Git blob 值＝审计日志 actual 列，与本会话复算逐位一致）；commit/path/class 列不动。
4. Canonical Evidence 区**新增纯文本说明段**（仿 174 行先例，非表格行）：逐行登记原 worktree/original SHA＋证据来源（外部原件路径 / 主仓工作树 / Resource Manifest 行号）＋双口径声明＋“原件与 blob 去 CR 逐字节等价（sess_14d54cdc 实测）”＋本裁决 session/turn。
5. Rolling Checkpoint 追加订正轨迹（旧值→新值→依据→本裁决 ID）。
6. 按 sess_1bff86d4 §7 既有授权的收口增补行（本追加裁决报告、重审日志等）。

**执行后关闭序列**：clean HEAD 重跑**全节** blob audit（覆盖订正＋增补后的当前全部数据行，行数>88 属预期）→ 新日志入 `verification/FEA-15-PIN-BASIS-ENFORCE-1/` 并 pin → `EXIT=0` 则 R-001 按**原条件**关闭、Closeout Record 记录、Task 终态 `closed_with_limitations`（D5 限制清单全部保留，12 行订正史入 Handoff）；**EXIT≠0 或新失败则 R-001 仍 OPEN、Task 停留 in_progress、再次回报再裁**。STATUS/Plan/Ledger 指针更新守 Plan 6999/7000 bytes 红线。

**禁止**：改 18 frozen pins、任何历史 Task/Review/Handoff/checkpoint/已入库 evidence 文件字节、`.gitattributes`、renormalize；改外部原件或 workspace 资源、清理/gc/prune/repack；把 FEA-06（13 errors）、CHAPTER-SELECTOR（6 errors）、full suite 3 failed 或本轮 audit 的 12 项 FAIL 观测改写为 PASS；push；超出第 1–6 项的字节改动。

## 四、状态与遗留

- **R-001**：本裁定时刻 **OPEN**（前次 audit EXIT=1 事实不变）；仅在上述关闭序列满足后转 CLOSED。
- **Task**：此刻 `in_progress`；目标终态 `closed_with_limitations`（条件如上）。
- **路径 B**：因 A 成立而不启用；若本窄解读被推翻或订正后重审仍失败，自动落入 B 之停止态（R-001 OPEN、Task in_progress、停止、回报）——届时是否修订关闭条件属用户专属权力。
- **必须用户决定的事项**：**无**（本授权范围内）。用户专属保留（本轮未授权、不得自行启动）：push；18 frozen pins/历史卡治理修复；FEA-06/CHAPTER-SELECTOR 修复 Task。

**推荐下一步**：由 Codex 在写会话按第三节第 1–6 项执行订正并在 clean HEAD 重跑全节 blob audit（可直接转发）：

```
任务：FEA-15-PIN-BASIS-ENFORCE-1 R-001 失败行处置已由 ZCode 追加裁决（session sess_14d54cdc-c657-466a-9678-23eb966f8ea1 / turn_4707ecd4-9c3c-4132-a3c3-f8cd8af535c9，用户已授权自主推进）：择路径 A，授权活动卡最小订正。请执行：
1) Task 卡 Canonical Evidence 仅改 12 处：行 ac2ac3-ac4-v2-review-readme 的 commit 列→d714232eefbe66e62f15b4534dce90d22927ddc5（pin 不动）；行 ac5-review-readme 的 sha256→596bfde7c22a53b3ae3b49bc50b016eaa5669ab4460b67ce61ea5f7fbecdc9b0；其余 10 行（ac4-release-card-gates/ac4-release-preliminary-gates/ac4-release-clean-gates/ac5-integration-blob-map/ac5-integration-gates/ac5-zcode-review/ac5-zcode-review-receipt/ac5-post-pinbackfill-gates/ac5-review-post-pinbackfill-budget-fail/ac5-review-post-budget-fix-gates）sha256→各自 actual（Git blob 值，见 canonical-evidence-blob-audit-full-section-d4c4d9ffb.log actual 列）；
2) 新增说明段逐行保留原 worktree/original SHA 及来源（外部原件路径/Resource Manifest 行），声明双口径与去 CR 等价实测、原件与历史 evidence 字节未动；Rolling Checkpoint 记订正轨迹；落盘两份裁决报告并按 sess_1bff86d4 §7 增补收口行；
3) clean HEAD 重跑全节 blob audit，新日志入 verification/FEA-15-PIN-BASIS-ENFORCE-1/ 并 pin；EXIT=0 → R-001 关闭、Closeout Record、Task=closed_with_limitations、更新 STATUS/Plan/Ledger（守 Plan 预算红线）、终态四门复跑；EXIT≠0 → 停止，R-001 保持 open，回报再裁；
4) 全程不改 18 frozen pins/历史文件字节/外部原件，不改写任何历史 FAIL，不 push。
```