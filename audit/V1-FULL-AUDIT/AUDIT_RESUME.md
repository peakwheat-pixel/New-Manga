- 第五轮收敛门禁与第四轮 reviewed-HEAD 门禁归档：generated HEAD=`86f47fee363f9a3b84a9a6f75d8493178afe8c75` 四项 EXIT 0（default/TaskPath 各 3 warnings；verify_pins 18/18；API 1/79/6=86），日志 `logs/audit-post-evidence-86f47fee-*.log`；第四轮复审 reviewed HEAD=`6350081a535d5c67c57c0f1c6123a68ed5bbdf57` 的四项门禁（此前仅存 Task workspace）已按同一布局归档为 `logs/audit-post-evidence-6350081a-*.log` 与 `evidence/audit-post-evidence-6350081a-*.json`，四项均 EXIT 0，并将 pin 入 Task Canonical Evidence。

- 第六轮回填（2026-11-13）：Task 卡 pins 483/483（6350081a 归档门禁 8、86f47fee 门禁 8、第四轮复审证据 5）；AC4/Rolling 同步 483；下一步跑门禁并以 clean head 做收敛后复审。

- 第六轮回填后门禁：generated HEAD=`6c1773433a1121eccf27922eba73ecccaaa981a6` 四项均 EXIT 0（default/TaskPath 各 3 warnings；verify_pins 18/18；API 1/79/6=86）；日志 `logs/audit-post-evidence-6c177343-*.log`、metadata `evidence/audit-post-evidence-6c177343-*.json`。

- 第五轮复审（2026-11-13）：Codex 对 `reviewed_head=1ae79bb99534e3a06fc77a284c3a5089e12fce34` 复审，EXIT 0，643.5s；确认 483/483 pins；结论 REJECT，仅剩 F1 当前摘要 462 vs 483 与 F2 专项报告/索引旧措辞；并明确认可最后一次门禁未回填属滚动 limitation。报告 `reports/CODEX-FINAL4-REVIEW-2026-11-13.md`。

- 第六轮收敛后门禁：generated HEAD=`c9953bac5970272e502c0dad2949ae40dda38a8d` 四项均 EXIT 0（default/TaskPath 各 3 warnings；verify_pins 18/18；API 1/79/6=86）；日志 `logs/audit-post-evidence-c9953bac-*.log`、metadata `evidence/audit-post-evidence-c9953bac-*.json`。

- 第七轮回填（2026-11-13）：Task 卡 pins 496/496（第五轮复审证据 5、c9953bac 门禁 8）；AC4/Rolling 同步 496；下一步跑门禁并以 clean head 做第六轮复审。

- 第六轮复审（2026-11-13）：Codex 对 `reviewed_head=c2f5bc8273314f18fe91ea29781339f659872899` 复审，EXIT 0，1397.3s；确认 496/496 pins；结论 REJECT，仅剩 F1（Task AC3/AC4/Rolling 旧轮次摘要）与 F2（AUDIT-07 第 76 行、索引第 49 行旧 ZCode 措辞）；滚动门禁 limitation 被接受。报告 `reports/CODEX-FINAL5-REVIEW-2026-11-13.md`。

- 第七轮修复后门禁：generated HEAD=`484094a1ab7764222a82ebd758c047b805181720` 四项均 EXIT 0（default/TaskPath 各 3 warnings；verify_pins 18/18；API 1/79/6=86）；日志 `logs/audit-post-evidence-484094a1-*.log`、metadata `evidence/audit-post-evidence-484094a1-*.json`。

- 第八轮回填（2026-11-13）：Task 卡 pins 509/509（第六轮复审证据 5、484094a1 门禁 8）；Task status 由 `changes_requested` 改为 `in_review` 并附第六轮复审记录；下一步跑门禁并以 clean head 做第七轮复审。

- 进入 REVIEW 后门禁：Task status=`in_review`，AC 标题改为 lifecycle v3 要求的 `- [ ] **ACn**` 格式后，generated HEAD=`0de08632b2a8ed4fd9812d39ab5ad07881151bfe` 四项均 EXIT 0（default/TaskPath 各 **4 warnings**（未登记过程文件提示，非失败）；verify_pins 18/18；API 1/79/6=86）；日志 `logs/audit-post-evidence-0de08632-*.log`、metadata `evidence/audit-post-evidence-0de08632-*.json`。

- 第七轮复审（2026-11-13）：Codex 对 `reviewed_head=9bd7264ca3b91a5ddcfe831f9b1beeb47e13dca3` 复审，EXIT 0，1036.6s；确认 509/509 pins；关闭 AUDIT-08 P3-4；结论 REJECT，仅剩 F1 状态摘要同步（STATUS/LEDGER/PLAN/AUDIT_STATUS/AUDIT_PLAN/GATE/FINAL）、0de08632b warning=4 与 AUDIT_TASKS/P7 快照措辞。报告 `reports/CODEX-FINAL6-REVIEW-2026-11-13.md`。

- 第八轮同步后门禁：generated HEAD=`9b0be2cd120af176a188f60fd59d1c5425056f5b` 四项均 EXIT 0（default/TaskPath；verify_pins 18/18；API 1/79/6=86）；日志 `logs/audit-post-evidence-9b0be2cd-*.log`、metadata `evidence/audit-post-evidence-9b0be2cd-*.json`。

- 第九轮回填（2026-11-13）：Task 卡 pins 522/522（第七轮复审证据 5、9b0be2cd 门禁 8）；Task status 由 `changes_requested` 改为 `in_review`，TASK_LEDGER 重跑并反映 in_review；下一步跑门禁并以 clean head 做第八轮复审。

- 第八轮复审（2026-11-13）：Codex 对 `reviewed_head=6b09ca1f42a0145fa63fa317c2beb3b0596fe848` 复审，EXIT 0，729.2s；确认 522/522 pins；结论 REJECT，仅剩 F1 摘要/候选措辞（本轮修复）；F2 滚动门禁 limitation 接受。报告 `reports/CODEX-FINAL7-REVIEW-2026-11-13.md`。

- 第九轮修复后门禁：generated HEAD=`46a8fe6edb489efbafb88f83610e9b48f00d6d0d` 四项均 EXIT 0（default/TaskPath；verify_pins 18/18；API 1/79/6=86）；日志 `logs/audit-post-evidence-46a8fe6e-*.log`、metadata `evidence/audit-post-evidence-46a8fe6e-*.json`。

- 第十轮回填（2026-11-13）：Task 卡 pins 535/535（第八轮复审证据 5、46a8fe6e 门禁 8）；Task status 由 `changes_requested` 改为 `in_review`，TASK_LEDGER 重跑；下一步跑门禁并以 clean head 做第九轮复审。

- 第九轮复审（2026-11-13）：Codex 对 `reviewed_head=f251270833f3ea775f6f577dbfa33e6c88073162` 复审，EXIT 0，1306.9s；确认 535/535 pins；结论 REJECT，仅剩 AUDIT_PLAN/AUDIT_STATUS/Task AC4·Rolling/FINAL/13_GATE 当前指针同步（本轮修复）；指出最新已记录门禁为 `46a8fe6e`。报告 `reports/CODEX-FINAL8-REVIEW-2026-11-13.md`。

- 第十轮复审（2026-11-13）：Codex 对 `reviewed_head=9bbd5db468c2e416d4bc24e9495ebd1a19faa9f8` 复审，EXIT 0，972.3s；确认 535/535 pins；结论 REJECT，仅剩 Task AC3 与 13_GATE 审查来源两处指针（本轮修复）。报告 `reports/CODEX-FINAL9-REVIEW-2026-11-13.md`。

- 第十一轮 Codex 回退复审（2026-11-14）：reviewed_head=`89f2925ff0ad6d11d4f77aec0c23346f2c817b78`，EXIT 0，873.1s；确认 535/535 pins；结论 REJECT，仅剩当前轮次指针同步（本轮修复）。用户 2026-11-14 裁决最终裁决改为 ZCode 优先，本复审作为回退输入。报告 `reports/CODEX-FINAL10-REVIEW-2026-11-14.md`。

- 2026-11-14 用户裁决：最终裁决与独立 Review 改为 **ZCode 优先、Codex 回退**；ZCode 仍因 provider `1310` 不可用（reset 2026-11-17 18:40:33），本轮以 Codex 回退执行第十一轮复审（reviewed_head `89f2925ff`，REJECT：仅剩轮次指针同步），并同步全部当前指针。最终裁决待 ZCode 恢复后确认。

## 2026-11-13 用户裁决：最终独立 Review 与裁决改为 Codex 优先

- 用户 2026-11-13 指示：“调整流程，裁决交给 codex 或者 zcode，优先 codex”。本 Task 的最终独立 Review 与候选/finding 裁决改为 **Codex 优先**；Codex 不可用或不适配时回退 **ZCode**。历史 ZCode 裁决、Review 与 evidence pin 原字节保留，不追改、不据此恢复 ZCode 独占裁决。
- Reviewer 字段同步更新为 Codex（fresh independent context；fallback ZCode）。Review 仍须上下文独立：产出该变更的同一会话/实例不得自审；本 Task 由 DSH 集成，Codex 以新上下文做只读 Review。
- ZCode provider 额度失败（1310/429，reset 2026-11-17 18:40:33）不再阻塞 Review 路径；Codex CLI 0.162.0 于 2026-11-13 探测 EXIT 0（session `01a1d4c6-e6b0-7df2-9a05-4ddc83a50712`），已具备派发条件。
- 该裁决不改变 Task 状态、AC1–AC4、Release Gate BLOCKED，也不授权修改产品源码、既有测试、契约、Schema、依赖、真实用户数据或 Git 历史。
- 返修后门禁：generated HEAD=`076dfbb63ad7f2b63605bfc16cdd8079e96dd6b2` 的四项门禁均 EXIT 0（default/TaskPath 各 3 warnings；verify_pins 18/18；API 1/79/6=86），原始输出 `logs/audit-post-evidence-076dfbb6-*.log`。下一步以该 clean head 派发 Codex 复审修订后的交付。

- 复审（2026-11-13）：Codex 对 `reviewed_head=226eb048006ffa804ebefd9f98e51bbc13793f31` 完成返修复审（session `01a1d4f3-9736-7402-8c3e-ce701f1e2490`，EXIT 0，817.3s），结论 **REJECT**；确认 428 pins、70e/b723 gate pins 与 9 项重命名有效；剩余返修：状态/计数口径（398↔428）、076dfbb6 门禁未 pin、专项报告与台账旧 ZCode 口径、`AUDIT-14-CAND-003` 表述。报告 `reports/CODEX-REREVIEW-2026-11-13.md`。

- 第三轮返修（2026-11-13）：Task AC4/Rolling checkpoint 更新为 441 pins；回填 076dfbb6 gate 批次（8 条）与复审证据（5 条）；STATUS 同步为 428/428 并控制预算；AUDIT_STATUS、AUDIT_PLAN、P7 集成报告、专项报告与详细台账的旧口径已修正；pins 441/441 复算通过。下一步跑四项门禁并以 clean head 做最终复审。

- 三轮返修后门禁：generated HEAD=`d248ed28faebf025d599e4701216f4da7ee17f3b` 四项 EXIT 0（default/TaskPath 各 3 warnings；verify_pins 18/18；API 1/79/6=86），原始输出 `logs/audit-post-evidence-d248ed28-*.log`。下一步以该 clean head 做最终 Codex 复审。

- 第三轮最终复审（2026-11-13）：Codex 对 `reviewed_head=42810143b025a90de2f651a73059243dd6a0259e` 完成最终复审，EXIT 0，994.6s；确认 441/441 pins、无重复 ID、14 项更正正确、六批门禁一致；剩余返修为当前状态措辞（441 vs 428/398）、专项报告旧 ZCode 措辞与 `AUDIT-14-CAND-003` 表述。报告 `reports/CODEX-FINAL2-REVIEW-2026-11-13.md`。

- 最终回填（2026-11-13）：Task 卡 pins 462/462（d248ed28 批次 8、第三轮复审证据 5、fee77cc0 批次 8）；AC4/Rolling 同步 462；第四轮门禁在 fee77cc0 与后续 HEAD 均 EXIT 0。下一步以 clean head 做最终复审并完成 DSH 集成/closeout。

- 第四轮收敛复审（2026-11-13）：Codex 对 `reviewed_head=6350081a535d5c67c57c0f1c6123a68ed5bbdf57` 复审，EXIT 0，1031.6s；确认 462/462 pins、无重复、14 项更正正确、计数自洽；结论 REJECT，剩余：STATUS/AUDIT_STATUS 写 441、AUDIT_PLAN/13_GATE/FINAL 旧 Review 状态、专项报告旧措辞、6350081a 门禁批次未入仓。报告 `reports/CODEX-FINAL3-REVIEW-2026-11-13.md`。

## 2026-11-13 P7 Codex 最终独立 Review（Codex-first 裁决）

- 用户裁决后，以 Codex CLI 0.162.0（`gpt-6-luna` / xhigh）对 clean HEAD=`d92859c9ac8a4d3122d6cabfe4d44af980574104` 派发全新上下文只读 Review；session `01a1d4ce-6b79-7b43-939d-834e3cdc21a9`、EXIT 0、耗时 1,911.5s、Review 前后工作树 clean。原始报告 `reports/CODEX-FINAL-REVIEW-2026-11-13.md`，派发元数据 `evidence/codex-final-review-20261113.meta.json`。
- 前两次派发（`-s read-only` 与 `-s workspace-write`）因本机 Codex 无法 spawn 子进程（Windows error 740）在前置检查停止；第二次另因 8 个未跟踪 gate 文件判定工作树不 clean 而停止。两者均未形成裁决，不计为 Review。
- 结论 **REJECT**（交付文档问题，不是产品通过）。返修项：①当前状态与 Codex-first 裁决未同步到 Task AC3/AC4、STATUS、AUDIT_STATUS、AUDIT_PLAN、AUDIT_RESUME、11_ISSUES、12_REMEDIATION_PLAN、13_RELEASE_GATE、FINAL_AUDIT_REPORT；②70e92876 与 b72363aa gate batch 尚未 pin，P7 集成报告 398/371 矛盾；③9 个 evidence_id 各对应两行（`AUDIT-RUNNER-SOURCE-2` 与 8 个 `QUOTA-POSTPIN-GATE-*-1`）；④`AUDIT-14-CAND-003` 对当前 CI 的断言过强，裁决为 close。
- 裁决要点：05/06 三候选 INVESTIGATE；07-001 finding P2；07-002 accepted limitation；09-001 finding P3；12-001 finding P3（交付工具）；14-001 finding（非产品 P0–P3 计数，P3 优先级）；14-002 INVESTIGATE；14-003 close；14-004 close；AUDIT-11-INC-001 维持 INVESTIGATE 且不计 P。产品计数 P0=0/P1=0/P2=2/P3=2；开放 finding 共 7（3 原有 + 4 新增）。AC1 MET；AC2 可收口 MET（保留原 FAIL/BLOCKED/PARTIAL 与 NOT_RUN）；AC3/AC4 不可收口；Task 维持 in_progress；Release Gate BLOCKED。
- 下一步：DSH 按 Review 要求同步裁决与返修文档、pin 70e/b723 批次与本次 Review 证据、重命名重复 evidence_id、统一 398 计数，再以修订后 clean head 交独立上下文复审（Codex），最后由 DSH 集成与生命周期裁决。

- 返修执行（2026-11-13）：同步 Task/STATUS/AUDIT_* 状态与 Codex-first 裁决；Task AC2=MET、AC3/AC4 保留 PARTIAL 并更新原因；回填 70e92876 与 b72363aa gate 批次及本次 Review 证据共 30 条 pins；重命名 9 个重复 evidence_id（`AUDIT-RUNNER-SOURCE-2-5A54390F` 与 8 个 `QUOTA-POSTPIN-GATE-*-ED17A790`）；Task 卡 pins 428/428 复算通过。下一步以修订后 clean head 派发 Codex 复审。

## 2026-11-13 P7 DSH 续审与集成核验检查点

- 复原与固定：HEAD=`48ccb75ce1a547cf89e4d38cd577b868e15de5ce`，branch=`main`，工作树 clean；与用户记录一致，未 reset/clean/merge/改历史或覆盖他人文件。
- ZCode 可用性复核：2026-11-13 19:36（本地）以 `--mode plan --json --locale zh-CN` 最小探测，provider 仍返回 `1310` / HTTP `429`、EXIT 1、stdout 仅 CRLF、无 session/response；reset 提示 `2026-11-17 18:40:33`。原始 stdout/stderr 保留于 Task workspace，脱敏摘要与哈希见 `logs/zcode-final-review-probe-20261113T1935Z.log`、`evidence/zcode-final-review-probe-20261113T1935Z.json`。该探测**不构成 Review**；11 个候选与 `AUDIT-11-INC-001` 仍待 ZCode。
- 集成核验（DSH，非 Review）：`reports/P7-INTEGRATION-CONSISTENCY-CHECK-2026-11-13.md`。复算 Task 卡 371 条 Canonical Evidence：357 pass、14 FAIL；14 项（AUDIT-03 十项、AUDIT-04 四项）记录的是 worktree CRLF 字节 SHA-256，而 basis=BLOB；按 ZCode AUDIT-08 closure review 的 BLOB 基准更正为该 commit 的 raw Git BLOB SHA-256 后 371/371 PASS。脚本 `tests/verify_canonical_evidence.py`；更正前输出 `logs/task-card-pin-recompute-20261113-pre-correction.log`、`evidence/task-card-pin-recompute-20261113-pre-correction.json`，更正后 `logs/task-card-pin-recompute-20261113.log`、`evidence/task-card-pin-recompute-20261113.json`，根因与逐项值见 `evidence/task-card-pin-mismatch-investigation-20261113.json`、`evidence/task-card-pin-correction-20261113.json`。
- 报告一致性：3 triaged findings / 1 INVESTIGATE / 11 候选 / 1 关闭非产品观察、P0–P3 计数、测试数值、AC1–AC4、R1–R4 与 Release Gate BLOCKED 均一致；记录到的文档漂移（AUDIT_STATUS 旧 NOT_TESTED 段、PLAN/INDEX 旧 gate 批次、Task 卡 AC4 旧 batch、遗留候选未处置）已记录并部分更正，不由 DSH 裁决候选。
- 门禁：修复 `doc/STATUS.md` 预算后，generated HEAD=`52b86d3984f76abdebb4bddf25837b19639ff771` 的四项门禁均 EXIT 0（default/TaskPath 各 3 warnings；verify_pins 18/18；API 1/79/6=86），原始输出 `logs/audit-post-evidence-52b86d39-*.log`、`evidence/audit-post-evidence-52b86d39-*.json`。同一轮首次在 `18357fdcd286ebf8e2c6b1780fcb86d1295d0423` 上运行 default/TaskPath 时因 STATUS 3,205 bytes 超预算 EXIT 1，失败批次原样保留为 `audit-post-evidence-18357fdc-*`；两次运行均记录 HEAD/EXIT。
- Pinbackfill 后门禁：generated HEAD=`70e92876204932d106f312fcc386177fd2da35f4` 的四项门禁均 EXIT 0（default/TaskPath 各 3 warnings；verify_pins 18/18；API 1/79/6=86），原始输出 `logs/audit-post-evidence-70e92876-*.log`、`evidence/audit-post-evidence-70e92876-*.json`。Task 卡在本次回填后共 398 条 Canonical Evidence pins，按同一 BLOB 算法复算 398/398 PASS（`logs/task-card-pin-recompute-20261113-final.log`）。
- 下一步：本次提交与门禁后，以届时 clean HEAD 重派 ZCode fresh-context 只读 Review（候选逐项裁决 + 证据复核 + Release Gate），再由 ZCode 裁决、DSH 集成。Task 仍 `in_progress`；AC2/AC3/AC4 `PARTIAL`；Release Gate `BLOCKED`；无待处理人工批准。

## 2026-11-13 P7 ZCode 独立 Review 派发阻断

- 待审固定 HEAD=`3c40eb5ce987cecc6c73cb8dec37fbdef9948538`，branch=`main`；ZCode 启动前确认该 HEAD 且工作树 clean。Task P7 交付文件与当前门禁已固定，无审查期间工作区变更。
- 完整只读 Review 以 ZCode CLI `0.17.1`、`--mode plan --json --locale zh-CN` 派发，EXIT 1；stdout 0 bytes、无 response/sessionId。stderr 为 ProviderBusinessError `1310`，提示每周/月额度于 `2026-11-17 18:40:33` 重置。
- 随后用 workspace 临时 provider 配置对已存在的 Team Coding Plan provider 做最小只读探测，仍 EXIT 1；CLI 实际解析到 `account:bigmodel-individual-coding-plan` 并返回相同 `1310`，无 response/sessionId。没有改动原始凭据或全局 provider 配置。
- 可复核记录：`source/zcode-final-review-prompt-20261113.txt`、`logs/zcode-final-review-attempts-20261113.log`、`evidence/zcode-final-review-attempts-20261113.json` 及其引用的 stdout/stderr 原始文件。外部临时配置和原始派发回执保留于 `G:/CODEX/New Manga.workspace/task-envs/NEW-MANGA-V1-FULL-AUDIT/`、`agent-output/ZCode/NEW-MANGA-V1-FULL-AUDIT/`。
- 上述记录提交后，generated HEAD=`77310033f77d5b793fe4ff3734e1ba7cf049c06c` 的 default / TaskPath / verify_pins / API 四项均 EXIT 0；default/TaskPath 各 3 warnings，pins 18/18，API 1/79/6=86。原始日志与 JSON 由 commit=`e61a271fb06f708db67e465be87a396fffc92c47` 固定；本次 Canonical Evidence pinbackfill 将其与派发失败证据一并纳入，再于 pinbackfill HEAD 重跑四项门禁。
- Task Card pinbackfill HEAD=`3a1ceccacd5e972413c2d170760ede83ae39a5d1` 后，default/TaskPath/verify_pins/API 再次均 EXIT 0（3 warnings/3 warnings、18/18、1/79/6=86）；原始日志与 JSON 由 commit=`7ecf21c7d724c93c6890703a15394b5854348c69` 固定。该滚动 gate batch 将在下一次 Task-card 更新时回填 Canonical Evidence。
- 该失败不构成 Review 或候选裁决。AC2/AC3/AC4 仍 PARTIAL，Task 仍 `in_progress`，Release Gate 仍 `BLOCKED`；下一步是在 ZCode provider 可用后，以届时 clean HEAD 重派独立 Review，并复核当前证据与门禁。无待处理的人工批准。

## 2026-11-13 P7 当前 pinbackfill 后门禁检查点

- Task card pinbackfill HEAD=87ee1ea75aefac15a313767c64c149e286d3a8e8，branch=main。该提交后的 default / TaskPath / verify_pins / API 四项全部 EXIT 0：default 与 TaskPath 各 3 warnings；verify_pins 18/18；API inventory 1/79/6=86。quota checkpoint 与其后 generated HEAD=77310033 的门禁现已随本轮卡面 pinbackfill 纳入 Canonical Evidence。
- 原始输出与 JSON：logs/audit-post-evidence-87ee1ea7-default.log、evidence/audit-post-evidence-87ee1ea7-default.json；TaskPath、pins、API 同 stem 文件。该 batch 是当前 Task Card commit 后的 gate 结果；按 rolling pinbackfill 规则，Task Card 在本轮复核前的 Canonical Evidence 已固定至 a3a429cc batch，本批记录于本检查点供 ZCode 复核，后续 Task-card 更新再 pin。
- 该批后续 gate output 已固定。原计划的 ZCode CLI plan-mode 独立只读 Review 于 `3c40eb5c` 派发，但因 provider quota `1310` 无 response/sessionId；具体尝试和限制见本文件顶部。Task 仍 in_progress；AC2/AC3/AC4 PARTIAL；Release Gate BLOCKED。

## 2026-11-13 P7 final-pinbackfill gate batch

- Task card HEAD=a3a429cc955f12765253a14680e79bab2389dd89，branch=main。该 HEAD 上 default / TaskPath / verify_pins / API 四项门禁均 EXIT 0：default 和 TaskPath 各 3 warnings；18 pins；API inventory 1/79/6=86。
- 原始日志与 JSON：logs/audit-post-evidence-a3a429cc-default.log、evidence/audit-post-evidence-a3a429cc-default.json；TaskPath、pins、API 同 stem 文件。此批在提交后按 rolling pin 规则进入下一次 Canonical Evidence pinbackfill。
- 运行时 working tree 仅新增本批日志/JSON，产品源码、真实用户数据与远端未改动。提交该证据批后，将本批 hashes 回填 Task Card，再把固定 reviewed HEAD 交 ZCode fresh-context read-only Review。
- Task 保持 in_progress，AC2/AC3/AC4 PARTIAL，Release Gate BLOCKED；本检查不构成产品发布通过。

## 2026-11-13 P7 post-pinbackfill 门禁检查点

- Task card pinbackfill HEAD=e72bf97816a33e50c8cff5968c198975c3faddbd，branch=main。该提交包含 55 条新增 Canonical Evidence pins；新增 pin 的 Git BLOB SHA-256 逐项复算为 55/55 匹配。
- post-pinbackfill 门禁均在 generated HEAD=e72bf97816a33e50c8cff5968c198975c3faddbd 运行并 EXIT 0：default check 3 warnings；TaskPath check 3 warnings；verify_pins 18/18；API inventory 1/79/6=86。原始输出/metadata 分别为 logs/audit-post-evidence-e72bf978-default.log 与 evidence/audit-post-evidence-e72bf978-default.json、TaskPath、pins、API 同 stem 文件。
- 本次门禁验证了 P7 Task pinbackfill 提交。下一步将该批日志/JSON 纳入 Canonical Evidence；其后再在新增 pinbackfill HEAD 运行四项门禁。最终 ZCode fresh-context Review 仍待执行。
- 当前 Task in_progress；AC2/AC3/AC4 PARTIAL；Release Gate BLOCKED。真实模型、付费 API、完整 GUI、清洁安装、升级/回退/卸载等限制仍见 reports/FINAL_AUDIT_REPORT.md 与 reports/13_RELEASE_GATE.md。

## 2026-11-13 P7 综合报告与门禁检查点

- 产品审计基线=10e4ee013835605800d3830fb960ae8d3aa04167，branch=main。P7 编号交付册、去重台账、整改路线、Release Gate 与 FINAL_AUDIT_REPORT 已提交于 3fc756a1aed8ca366ac0b324ff293cc3e1f9ebb0；报告覆盖段 B AUDIT-00–14 现有结果与限制，没有把候选写成正式 finding，也没有把未测项写成 PASS。
- 首批 P7 preflight 结果在 generated HEAD=5a54390f63ed3283ba4a10df359dbc9f3a518a19 上四项均 EXIT 0，evidence commit=592e3f6a9626b45b2962bce4d22f99875ec2e179。加入报告与 38 个证据 pins 后在 generated HEAD=3fc756a1aed8ca366ac0b324ff293cc3e1f9ebb0 重跑：default / TaskPath 各 3 warnings、EXIT 0；verify_pins 18/18、EXIT 0；API inventory 1/79/6=86、EXIT 0。该批日志与 JSON 固定于 c0665ff90408d78097e787bd53af63d96bb32ecf；Task card 后续增加本批 8 个 pins，因此仍需在最终 pinbackfill commit 后重跑。
- 当前段 B 专项：00 limited PASS；01/03/08/11 FAIL；02 BLOCKED；04–07、09、10、12–14 PARTIAL。P7 台账登记 3 个已 triage findings（SEG-B-PROBES-001/002 Medium / High confidence；NM-AUD-0001 P2）、1 个 INVESTIGATE、11 个 REVIEW_PENDING 候选、1 个已披露关闭的非产品 P3 observation。候选 adjudication 未由审计作者代替 ZCode。
- 第三批 gate evidence generated HEAD=c0665ff90408d78097e787bd53af63d96bb32ecf，固定于 commit 4b91a2d7ff51e2ac6c05eef7c02a4640335fcf92：default / TaskPath 各 3 warnings、EXIT 0；verify_pins 18/18、EXIT 0；API inventory 1/79/6=86、EXIT 0。当前 Task card 已添加该批八个 BLOB pins；再完成这一轮 pinbackfill 后必须重跑四项门禁。
- 全项目 pytest 3,519 passed / 16 failed / 10 skipped / 11 warnings，EXIT 1；Avalonia TestHost 8/8 runner EXIT 1、TRX 0；smoke EXIT 1；AUDIT-13 Core acceptance 31 passed / 0 skipped / EXIT 0。AUDIT-09/10/12/13 的详细结果和 NOT_RUN 界限见正式编号报告与 AUDIT_EVIDENCE_INDEX.md。
- Task 仍 in_progress，AC2/AC3/AC4 PARTIAL，Release Gate BLOCKED。没有改产品源码、冻结契约、Schema、依赖、真实用户数据或远端；没有安装、发布或 push。下一步为回填当前 gate pins、更新 TASK_LEDGER、在 pinbackfill 后重跑四项治理门禁，然后派发固定 delivery HEAD 的 ZCode 独立只读 Review 和候选 adjudication。

## 2026-11-13 AUDIT-07 图片修复、排版与导出检查点

- Task 仍 `in_progress`；产品基线=`10e4ee013835605800d3830fb960ae8d3aa04167`；测试和静态捕获 generated HEAD=`4daa7169752b8f9c85fd8f8a01e5660f98f10481`，branch=`main`。
- AUDIT-07=`PARTIAL`：7 组隔离命令累计 263 passed / 3 failed / 0 skipped。inpaint/pipeline 38、Pillow rendering 73、source-style 5、font storage 6、searchable export 7、region revision restore 7 各 EXIT 0；Core/rerender/export 组 127 passed/3 failed/EXIT 1。
- 3 个失败均来自 P16 reader export hook options 参数测试：ZIP override 返回 `standard` 而非 `store`；text override 返回 `txt` 而非 `json`；空 override 案例没有预期的 `hook_invoked` audit event。该测试未比较排版像素质量，候选 `AUDIT-07-CAND-001` 归属与级别待 ZCode 裁决；`AUDIT-07-CAND-002` 为用户字体 license_note 未验证的边界观察，待 ZCode 裁决。
- 活动 Core 的 Pillow renderer 只扫描 Windows Fonts；FEA-14-FONT-1 明确把用户字体渲染消费留给 FONT-2。修复 learned routes 均静态标记 not_implemented；不宣称 LaMa 模型或真实修复质量通过。真实权重/GT/GUI/缩放/导出视觉对照/用户字体许可均 `NOT_RUN`。
- `audit07-static-scope-20261112T205724Z` generated HEAD=`4daa7169752b8f9c85fd8f8a01e5660f98f10481`：产品源码/原有测试/依赖/合同相对 base diff EXIT 0；审计 out-of-scope=0；仓库已跟踪字体/模型资产各 0。详见 `logs/audit07-static-scope-20261112T205724Z.log` 与 JSON。
- 全矩阵、限制、准确失败栈见 `reports/AUDIT-07-REPAIR-TYPESET-EXPORT-2026-11-13.md`。阶段证据提交 `46fd59e67b5369637946ecae3af670341a6ad75d` 后 default/TaskPath/pins/API 全部 EXIT 0；Task 卡与台账 pinbackfill 于 `27b16028168d1e86987dff7e968f9147b614d34c` 固定。该 HEAD 上的 post-pinbackfill default/TaskPath 各 EXIT 0（各 3 warnings）、18 pins EXIT 0（18/18）、API inventory EXIT 0（1/79/6=86）；四份日志和 JSON 路径见 `AUDIT_EVIDENCE_INDEX.md`，待下次卡面 pinbackfill 纳入 Canonical Evidence。独立 Review 待全审交付后由 ZCode fresh context 执行。下一项按 DAG 执行 AUDIT-09；全 Task AC2/AC3/AC4 仍 PARTIAL、Release Gate BLOCKED。

## 2026-11-13 AUDIT-04 OCR 与文本检测检查点

- 当前 Task 仍 `in_progress`；产品基线=`10e4ee013835605800d3830fb960ae8d3aa04167`；定向测试 generated HEAD=`c20e819009a810ae3828aef7eb8644eb9a3eae80`。
- AUDIT-04=`PARTIAL`：providers 组 175 passed、Core detect 组 40 passed；各 EXIT 0、无 skip。测试使用合成 frame、fake engine/decoder/Paddle payload 与 fake detector outputs，不验证真实 OCR/detection accuracy。
- 最终静态捕获 `audit04-static-20261112T203819Z` generated HEAD=`c20e819009a810ae3828aef7eb8644eb9a3eae80`：`src/apps/tests` 基线 diff EXIT 0、working-tree whitespace EXIT 0；采集时 21 条工作树路径均在 allowed_paths，out-of-scope=0。305 条 base-to-HEAD 路径含 14 条继承 FEA-11 HOST-AUTH-4 路径，不是本 Task 工作树修改。
- 默认检测 Manga ONNX、默认 Japanese Manga OCR ONNX 与 Korean Paddle OCR 路由有静态/单元证据；ORT CPU/auto→CPU 仅 fake runtime policy 证据。真实模型权重、人工 GT、日/韩文识别率、真实 CPU 推理、模型 teardown/长时恢复和 Avalonia GUI 缩放映射均 `NOT_RUN`。
- 本轮排除 `tests/providers/test_detection_doctr_real.py` 与 `test_detection_manga_real.py`。没有调用 Vision API、下载模型或读真实漫画。既有 Avalonia TestHost 8/8 runner `BLOCKED-TESTHOST-ACCESS` 未重试。
- 详细矩阵、链路和限制见 `reports/AUDIT-04-OCR-DETECTION-2026-11-13.md`；不新建 issue ID，不给识别准确率结论。全 Task AC2/AC3/AC4 仍 `PARTIAL`，Release Gate `BLOCKED`。下一项按 DAG 执行 AUDIT-07。

## 2026-11-13 AUDIT-03 合成导入与路径检查点

- 当前 Task 仍 in_progress；产品基线=10e4ee013835605800d3830fb960ae8d3aa04167；当前核心回归 generated HEAD=8071caccae1a7885fb41b95889cbdc0e80eeb963；产品目录 src/apps/tests 相对基线 git diff --quiet EXIT 0。
- AUDIT-03=FAIL；定向活动 Core 组 87 passed/EXIT 0，FEA-09 ReferencedSource 组 77 passed/EXIT 0；两组都是合成临时素材。详细矩阵、主机架构路径与限制见 reports/AUDIT-03-IMPORT-PROJECT-2026-11-13.md。
- 路径探针 generated HEAD=934c81017cadf20e96fd2ee60bfa247086638be6；SEG-B-PROBES-001 实测 publish 通过 managed/books 目录 junction 在 managed root 外创建 revision 文件。既有只读 triage 级别 Medium/High confidence，本轮不重定级。probe suite 其他两项涉及 AUDIT-08/11和已验证防线，不外推至 AUDIT-03。
- 活动 Core 普通路径测试检查原图 hash 不变；这不抹去 managed publication 的 root containment defect。该 junction probe 没有覆盖真实用户路径或修改现存原图文件。
- 中间试跑中包含的 tests/m2_acceptance/test_acceptance_loop.py 使用 PySide/QML 历史 harness，不在当前产品范围且未纳入正式证据。.NET 定向 Host/App tests 未重跑；历史基线状态 BLOCKED-TESTHOST-ACCESS。真实 GUI、安装包、项目根移动和 Avalonia 进程重启均 NOT_RUN。
- 探针复现的 SEG-B-PROBES-001 不新建 issue ID；不修改 product source，修复需独立实现 Task。AC2/AC3/AC4 仍 PARTIAL，Release Gate BLOCKED。下一项按 DAG 继续 AUDIT-04。

# 恢复入口

## 2026-11-13 AUDIT-09/10/12/13 检查点

- 产品基线=`10e4ee013835605800d3830fb960ae8d3aa04167`；本批报告/测试 evidence generated HEAD=`4e04e68c0db07ab136bc801e7fee27e7a5097564`，branch=`main`。当前阶段结果：AUDIT-09 `PARTIAL`、AUDIT-10 `PARTIAL`、AUDIT-12 `PARTIAL`、AUDIT-13 `PARTIAL`；原 AC2/AC3/AC4 与 Release Gate 继续 `PARTIAL` / `BLOCKED`。
- AUDIT-09 真实 Legacy/V2 空态 UI、设置、沉浸 Reader `H`/`Esc` 观察已捕获；Fluent Host 115.344 秒仍未 ready。Reader Retry 与可见合成选择不一致作为 `AUDIT-09-CAND-001`，不定级。真实页编辑、导入、OCR/翻译、导出、无障碍与完整多分辨率矩阵 `NOT_RUN`。详见 `reports/AUDIT-09-UI-UX-2026-11-13.md`。
- AUDIT-10 对 PNG decode、8 区域 layout/page compose、simple-fill 做 20 次批量重复；规范结果 median/p95 分别为 0.968/1.040 ms、1.330/1.373 ms、9.132/9.543 ms、109.972/110.846 ms。没有真实 I/O、OCR/translation model、benchmark threshold 或 soak。详见 `reports/AUDIT-10-PERFORMANCE-STABILITY-2026-11-13.md`。
- AUDIT-12 Release configuration build EXIT 0；inventory 发现旧 zip/setup 与当前产品 build 输出，但 package provenance 未绑定当前 fixed product baseline；按 Task scope 未安装/启动/卸载。`AUDIT-12-CAND-001` 为单文件 publish 默认 repo 内输出并递归清理目录的静态候选。详见 `reports/AUDIT-12-WINDOWS-DELIVERY-2026-11-13.md`。
- AUDIT-13 三个 production Core acceptance 文件 31 passed / 0 skipped / EXIT 0；只提供 A/D/E/G/H 的部分 synthetic coverage，B/C/F 和真实完整 UI 链未测。详见 `reports/AUDIT-13-E2E-2026-11-13.md`。
- 证据日志/JSON：`logs/audit09-ui-*.log`、`logs/audit10-performance-20261112T222445371097Z.log`、`evidence/audit10-performance-metrics-20261112T222445371097Z.json`、`logs/audit12-delivery-inventory-20261112T223042315179Z.log`、`logs/audit13-core-acceptance-20261112T222650072377Z.log`。未触碰真实漫画、用户库、provider 凭据或产品源码。
- 下一步按 DAG 进入 P7：全量 candidate/finding 去重、整改路线、正式报告和 Release Gate；证据固定后交 ZCode fresh context 独立 Review。历史 01/02、08、11 的 review 只适用于各自 reviewed head，不替代最终交付 review。

## 2026-11-13 AUDIT-14 静态阶段检查点

- 当前 Task 仍 `in_progress`；产品基线=`10e4ee013835605800d3830fb960ae8d3aa04167`，静态 inventory 生成 HEAD=`a9924499fc5271fb1f917ea031d701c419003dcc`，branch=`main`。本阶段只写 `audit/V1-FULL-AUDIT/**`；`git diff --quiet <base> HEAD -- src apps tests` EXIT 0，未改产品代码、contracts、schema、依赖或原有测试。
- AUDIT-14=`PARTIAL`：传统 `MainWindow` 四页的静态 Host 接线可见；当前 V2 Studio 对 Run/text/flag/Final-Split surfaces 明确采用 `NOT_WIRED` 或无对应数据源。需求归属待独立裁决。
- 文档核对发现 V1 与未来规划没有权威逐项总账；README 的 Managed Copy 和 0.1.0 示例、索引“没有 README”以及 V11R 计划 ACTIVE 等与当前状态存在漂移。README 5 个功能域/4 个一级页面仅是声明数量，不能算作正式 V1 commitment count；未来计划数量 `NOT_COUNTABLE`。
- 4 项候选 `AUDIT-14-CAND-001…004` 均 `REVIEW_PENDING`，未定级；静态命令/输出在 `logs/audit14-static-20261112T192852Z.log` 和配套 JSON，完整分析在 `reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md`。真实 UI、安装包、模型/漫画数据均 `NOT_RUN`。
- `e67fef47461a0de6a600c7fcf67b6a13c9b64635` 上首轮 default/TaskPath 因状态文档 3209/3200 bytes、计划 7002/7000 bytes 各 EXIT 1；压缩两行摘要后复跑均 EXIT 0（各 3 warnings），pins 18/18 EXIT 0、API 1/79/6=86 EXIT 0。两批原始输出均保留在 `AUDIT_EVIDENCE_INDEX.md`。
- ZCode 复核已按用户报告“额度恢复”再试：固定 `reviewed_head=26888045ff475fb2e34b043c55c168f4bd78cd52`，fresh plan 调用因 provider `1310` / HTTP `429` 再次失败，提示额度重置于 `2026-11-17 18:40:33`；EXIT 1、stdout 为空、无 session/response。raw stderr 仅存 task-env，脱敏回执与 dispatch 记录已落盘；05/06 和 14 共 7 项候选均仍 `REVIEW_PENDING`。不重试同一限额，继续独立审计。
- 下一步：按专项顺序推进 AUDIT-03（导入/路径发布）；之后 AUDIT-04、07、09、10、12、13。全审 AC2/AC3/AC4 与 Release Gate 继续 `PARTIAL` / `BLOCKED`；最终定级仍交 ZCode，不自行定级或关闭。

## 2026-11-13 AUDIT-05/06 阶段检查点

- 当前 Task `NEW-MANGA-V1-FULL-AUDIT` 仍 `in_progress`，产品基线为 `10e4ee013835605800d3830fb960ae8d3aa04167`。本阶段测试生成 HEAD=`d96529ebff6cf752ad64a676d05ec622da09e565`，分支 `main`；产品源码和原有测试相对基线无差异，新增测试只位于本审计目录。
- AUDIT-05=`PARTIAL`：`audit05-06-targeted-20261113` 为 247 passed / 3 deselected / EXIT 0；真实 SFX 权重、人工 GT 和 UI 为 `NOT_RUN`。AUDIT-06=`PARTIAL`：`audit06-context-20261113` 为 84 passed / EXIT 0；真实 API、账单/重放、远端取消语义为 `NOT_RUN`。
- 三个待 ZCode 裁决候选：同位 primary/SFX 双 Region；无账单级 spend cap/idempotency key；glossary 优先级未由生产校验强制。候选、证据和限制见 `AUDIT_ISSUES.md` 与 `reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md`；不得视作已定级 finding 或修复授权。
- 完整命令、生成 HEAD、UTC 与 EXIT 见两批 log/JSON；独立审计测试为 `tests/test_audit05_sfx_regression.py` 与 `tests/test_audit06_context_observations.py`。
- ZCode 对 reviewed_head=`dfef8d8919fe2d19013e65c84948fb288c2c9928` 的 fresh-context plan Review 尝试于 `2026-11-12T19:06:50Z` 发出，但 provider 返回 code `1310` / HTTP `429`，提示额度到 `2026-11-17 18:40:33` 重置；EXIT 1、无有效 response/session。该失败回执已脱敏落盘，不算独立 Review；三项候选继续 `REVIEW_PENDING`。在额度重置前不重复相同调用。
- 下一步：保留独立 Review 待办，继续 DAG 节点 AUDIT-14；不依赖本次候选裁决的审计继续推进。全 Task AC2/AC3/AC4 仍 `PARTIAL`，Release Gate 仍 `BLOCKED`。

2026-10-24；HEAD 349e61faff5f93067af5d4ce2d9e394e0d665b8c；branch main；worktree G:/CODEX/New Manga。

先核对 git status / git rev-parse HEAD 与 evidence/source-manifest.json；保留原6个P04诊断文件。已完成基线/盘点。下一步查看 evidence/*.json 和 logs/*.log 的 EXIT，未有结果的套件通过 `python audit/V1-FULL-AUDIT/tests/audit_runner.py <suite>` 执行；suite=pytest/frontend/rust/smoke/governance/dependencies。所有运行数据 G:/CODEX/New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT。不得直接复跑未知仍运行任务；先检查进程。审计未完成，不宣称PASS。

## 2026-10-24 推送准备 checkpoint

TaskStatus=in_progress；ExecutionState=BLOCKED_MATERIAL_PROVENANCE（仅推送准备阻断，全量审计未关闭）。产品 start/head 仍为上述 `349e61faf`；没有新增提交、暂存、上传、清理或历史改写。

已同步 Status/Plan/Task/TASK_LEDGER；治理检查 PASS（3 warnings），不表示全量审计 PASS。工作区仍有本审计未提交文件、3 份已修改治理文档和6份既有P04日志；具体保护 hash 见 `evidence/push-worktree-ownership.json`，P04均不暂存。完整结果和后续指令见 `reports/PUSH_READINESS.md`；固定推送候选、base和证据hash见 `evidence/push-manifest.json`。

历史离线扫描已覆盖17455个新增blob、2144个zlib对象与3份ZIP；4项凭据命中均为测试占位值。材料许可/数据库隐私仍未证明，173个嵌入图像未取得当前主线标准对象路径映射；不能push。下一精确步骤：按报告追溯嵌入tree/材料来源；不因本次文档同步批量暂存整包审计，尚未冻结的全量审计证据与未分配Reviewer状态均保留。

## 材料复核 checkpoint（当前恢复点）

产品HEAD/branch/worktree不变，Task仍in_progress；推送准备仍BLOCKED_MATERIAL_PROVENANCE。读取 `reports/MATERIAL_CLEARANCE.md` 和 `evidence/push-material-inspection.json`；上面的初次“继续追踪”步骤已被本轮实际检查收窄。

4个嵌入PNG与 `ed607b755` 合成manifest精确匹配。169个JPEG名称集合/页数/尺寸与T1.1.1商业日漫卷册记录完全吻合，但缺逐页源hash，不能把关联当许可。沿182个根tree及本地对象共读取1449个tree，无缺失tree；仍不能从这些根定位169个JPEG完整路径。34份库已readonly immutable检查，12份M2-AC1业务库与生成页hash匹配、5份P18业务库领域表为空；存在22个路径单元格，不签发WAL/删除页隐私结论。

隔离数据库副本保留在 `G:/CODEX/New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT/push-materials/`，只读核查前后hash一致，不清理。6个P04日志仍保护且未暂存，无新增commit/push/历史改写。继续精确步骤：取得用户的来源/许可记录或材料处置选择，按最新报告记录证据；如果缺许可，冻结独立发布方案供裁决，不擅自把清理/历史重写当下一步。全量审计其他AC与独立Review仍未完成。

备选方案已具体写入 `reports/MATERIAL_DISPOSITION_OPTIONS.md`：完整历史推送仍需材料传播证明；许可不足时建议独立的干净源码快照新分支，保留原main/远端main和全部证据。仅设计，未创建导出/分支/新仓库或释放新Task。下一步等待用户材料信息或方案选择，不自动实施。

当前用户裁决覆盖上述等待许可分支：用户明确“我自己的，但是不传播”。169个JPEG及其压缩外层blob已登记禁止上传（`evidence/push-material-disposition.json`），push=BLOCKED_OWNER_NO_DISTRIBUTION。保留全部本地素材与历史；不再重复索要许可，也不推完整main或3个分批候选。推荐下一步由Codex冻结独立干净源码快照的发布目标与Task；尚未释放、不自动创建分支或push。

## 2026-11-12 段 B 恢复点

- 当前 Task 已按 ZCode 受托裁决从 `blocked` 恢复为 `in_progress`。段 A 基线仍为 `349e61faff5f93067af5d4ce2d9e394e0d665b8c`，原有 PASS/NOT_TESTED 作为历史保留；段 B 审计当前 AD-002 产品，固定 base=`10e4ee013835605800d3830fb960ae8d3aa04167`。
- 阶段 0：branch=`main`、工作树 clean；`87f61d8…`、`349e61…`、`b1c1f5a5…` 祖先关系 EXIT 0；`349e61…..HEAD` 为 2366 commits；`.tmp.driveupload` 在旧树中有 2148 个条目。完整命令与 EXIT 见 [阶段 0 日志](logs/stage0-resume-verification-20261112.log)；提交前 WORKTREE SHA-256=`B561337B697AD62506049EF310EF04A52B8C69487CE31F6C9046E2B9B470EB6D`，Git BLOB SHA-256=`7E2A4911D7F1AB2D21DE48C4AC4B77F2C8BACCC5FA6CB1D6C2DFF681F32260A7`（commit `304a40addb4818f415b1e86d5c5b65205eca3605`）。
- 段 B release gates 在 `df120fb56567278e7e9a954e7a81c3f6465625c1` 实测：default PASS/EXIT 0（3 warnings）、TaskPath PASS/EXIT 0（3 warnings）、18 pins PASS/EXIT 0、API 1/79/6=86 EXIT 0。原始日志见 [segment-b-release-gates-df120fb.log](logs/segment-b-release-gates-df120fb.log)，commit `4b5aa2d6a327c7ffa2c5b3025473fb5a6f3f1179`。
- 范围裁决摘要和传播风险证据见 [ZCode 裁决记录](reports/ZCODE-SCOPE-ADJUDICATION-2026-11-12.md)。本地证据支持素材历史于 2026-10-30 随 main push 进入当时公开仓库的高置信推论；当前远端实时可见性未核验，不 push、不删除、不改写历史、不 GC/prune。
- 段 B 启动时 AUDIT-00–14 均未执行；目前 AUDIT-00 已 PASS（仅基线/清单），AUDIT-01–14 仍 NOT_TESTED。报告、JSON 清单与命令日志见 Task Canonical Evidence（commit `1a8238b9f86427efe5c48918f3bc0f2942611732`）。审计仅本地与只读隔离，私有图片只可用元数据定位，禁止素材内容级访问、导出、复制或显示真实路径。若发现新的真实用户数据泄漏面、需改产品文件、超出 allowed_paths 修治理问题或阶段 0 基线/祖先条件变化，停止并记录。

### 测试映射检查点（2026-11-12）

- ZCode 只读裁决见 `reports/TEST-MAPPING-ADJUDICATION-2026-11-12.md`（session `sess_8a2f7064-f80d-49a5-b96f-6d5ba20dd1ca`）；对应 CLI 和原始清单定位搜索见 `logs/test-mapping-adjudication-20261112.log`。裁决区分当前 Python Core/Avalonia 测试面与冻结 Legacy suites，并允许仅在 audit 路径增加 `.NET` runner。
- 对 `audit`、`doc`、`verification`、`archive` 文本做定向查找，只找到状态占位，没有 AUDIT-01–14 原始逐项定义。没有运行 probes、pytest、`.NET` 或其他专项测试；AUDIT-01–14 继续为 `NOT_TESTED`，Release Gate 继续 `BLOCKED`。
- 下一步先将“逐项清单缺失”交 ZCode 作范围裁决。未获裁决前不猜测 AUDIT-01–14 各自范围、不执行专项测试、不读取漫画图像内容。

### 测试执行边界检查点（2026-11-12）

- ZCode 后续裁决选定“证据采集与逐项判定解耦”：AUDIT-01–14 全部为 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`；可以继续 pytest/Core、probes、Avalonia `.NET`、适用 smoke 与 governance 的限定 suite 证据。详细裁决与 CLI 日志见 Task Canonical Evidence `TESTEXEC-1` / `TESTEXEC-LOG-1`。
- `smoke` 的当前架构范围为 `core,wire`；`packaged` 固定依赖旧 `apps/desktop/src-tauri`，与 `frontend/rust/desktop/npm-audit` 一并登记 `NOT_RUN-legacy`。
- `.NET` 使用 8 个测试 `.csproj` 分别 `dotnet test --no-restore`；TRX 写到仓外，仓库默认 `obj/bin` 只允许 ignored 派生物。每个项目执行前后 `git status --porcelain` 必须逐字节一致。8/8 项目 restore assets 已只读确认存在。不得使用 `--artifacts-path`、复制资产或 restore。
- 下一步：在 audit runner 中添加 `.NET` suite 并将 smoke 限定为 `core,wire`，实现提交后按 probes → pytest → `.NET` 8 项 → smoke → governance 执行；任何环境/状态偏差按具名阻断，不清理、不恢复。

### 段 B probes 检查点（2026-11-12）

- runner 实现固定在 `5ab8ae006580f4c3aab6d61ce180794921dc7641`；结果在 HEAD `5ab8ae006580f4c3aab6d61ce180794921dc7641` 生成，命令 `python audit/V1-FULL-AUDIT/tests/audit_runner.py probes`，EXIT 1，耗时 1.295s。原始输出与 JSON 见 Task Canonical Evidence `PROBES-LOG-1` / `PROBES-RESULT-1`。
- 隔离 probes 中，directory junction 发布越界和 nmbak 磁盘失败后的数据库变更/错误信息缺失两个观察待 ZCode 定级；`../` 备份路径写入预期被 `_managed_relative_path` 拒绝。详细解释边界见 `reports/PROBES-RESULT-SEGMENT-B.md`；没有修复或重跑。
- AUDIT-01–14 仍全部 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`。下一项运行根 `pytest`，保持 suite 结果与 AUDIT-NN 状态隔离；其后按已保存裁决执行 8 个 `.NET` 项目、smoke `core,wire`、governance。

### 段 B pytest 与 probes 分级检查点（2026-11-12）

- 根目录 `tests` 已通过 `python audit/V1-FULL-AUDIT/tests/audit_runner.py pytest` 执行一次，作为 Python Core 限定 suite 证据。子进程 argv、cwd、branch、生成 HEAD、UTC 起始时点、elapsed、完整输出和 EXIT 见 `logs/pytest-segment-b-20261112T081732598825Z.log` 及 `evidence/pytest-segment-b-20261112T081732598825Z.json`。生成 HEAD=`425bd0565134b36642c93922ebd80c648b97d627`，EXIT=1，3,519 passed / 16 failed / 10 skipped / 11 warnings，elapsed=288.543s。
- 16 项失败按观察分为 reader export hook 3 项、FEA11 v7 fixture 查询缺 `chapters.custom_rank` 1 项、plugin sandbox 12 项；未推断共同根因、未修复、未重跑。详见 `reports/PYTEST-RESULT-SEGMENT-B-2026-11-12.md`。10 个 skip 与 11 个 warning 的原因/类别也记在报告和完整日志中。
- suite 状态已更新，但不映射到 `AUDIT-01–14`；这些逐项仍为 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`。当前 pytest 结果不是 App/UI、真实 GUI、安装、升级/回退或 Release Gate 通过证据。
- ZCode 只读确认 probes 原有分级：`reports/PROBE-TRIAGE-SEGMENT-B-2026-11-12.md` 与 `logs/probe-triage-confirmation-20261112.log`。两项建议均为 Medium / High confidence；`../` 备份路径为 defense-verified。未独立复现；实现修复超出本 Task。
- 原始 pytest 数据和 ZCode 确认日志在证据提交 `40f47362894f2ea6dcd66d463a72328aad37bbc6` 固定；本恢复点文档随后单独提交并 pin 回 Task。
- 下一步按既有裁决逐一运行 8 个 `.NET` 测试项目（`--no-restore`，TRX 写到 workspace；每项前后 porcelain 必须逐字节一致）。如有不忽略的状态变化立即停止，不清理、不恢复。之后执行 smoke `core,wire` 与 governance；`frontend/rust/desktop/npm-audit/packaged` 继续 `NOT_RUN-legacy`，真实 GUI 继续 BLOCKED。

### 段 B Avalonia .NET TestHost 阻断检查点（2026-11-12）

- 已按裁决执行 `python audit/V1-FULL-AUDIT/tests/audit_runner.py dotnet`，覆盖 App、Appearance、ApplicationCore、CoreClient、DesignSystem、Host、PresentationAvalonia、ThemeEngine 8 个项目；生成时 HEAD=`da589416344b8254c9c1061f1d4e3dd61b3e7a93`，branch=`main`。8 个 runner 均 EXIT=1、TIMED_OUT=False，8/8 `status_identical=True`；逐项证据 JSON/log 固定在提交 `426a4fc5d5a551f04cf58979176baa4150351d5c`。
- 8 个 TRX 外部 workspace 只读 XML 计数均为 total/executed/passed/failed=0。TestHost 在 `SetParentProcessExitCallback` → `ProcessManager.OpenProcess` 抛 Win32Exception(5) 后退出，尚未发现或执行任何测试用例。ZCode 只读裁定状态为 `BLOCKED-TESTHOST-ACCESS`，保留原始 EXIT=1，不记产品测试失败、NOT_RUN 或 PASS；详见 `reports/DOTNET-RESULT-SEGMENT-B-2026-11-12.md` 和 `logs/dotnet-result-adjudication-20261112.log`。
- 对每项日志中的 `GIT_STATUS_BEFORE_HEX` 解码核对：porcelain 基线依次包含 0/2/4/6/8/10/12/14 条，只涉及审计目录中前序 runner 产物；8 组运行期间均字节不变。没有清理、恢复或修改源码。
- 不推断 Win32 错误的底层成因，也不提权、关闭安全控制、改 runner/测试参数或重跑绕过。TRX 留在 `G:/CODEX/New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT/dotnet/results-20261112T083119769139Z/`，按 resource manifest 保留，不复制进仓库。
- 按 ZCode 裁决，下一步继续 smoke `core,wire` 与 governance；`frontend/rust/desktop/npm-audit/packaged` 仍为 `NOT_RUN-legacy`，真实 GUI 仍 BLOCKED。所有 AUDIT-01–14 继续 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`，Release Gate 继续 BLOCKED。

### 段 B smoke `core,wire` 检查点（2026-11-12）

- 已运行一次 `python audit/V1-FULL-AUDIT/tests/audit_runner.py smoke`，argv 限定 `--only core,wire`。生成 HEAD=`2a7aed313f9673b327cfbb87dbbe2cfde1269037`，branch=`main`，EXIT=1，elapsed=1.783s；完整 runner log、report JSON 与 runner JSON 见 Task Canonical Evidence。
- 17 项检查中 10 PASS、7 FAIL；Wire 6/6 PASS，Core 4 PASS / 7 FAIL。frontend 与 packaged 显式 SKIP。ZCode 只读裁定 7 项 Core 失败为 `BLOCKED-SANDBOX-GRANT` 前置阻断及级联：`icacls` 无法授予当前解释器 `python.exe` AppContainer 访问；`CORE-AUDIT` 缺少 `hook_invoked` 是 hook 未能启动后的级联。保留程序 `FAIL` 和原始 EXIT=1，不能汇总为 suite PASS。详细报告：`reports/SMOKE-RESULT-SEGMENT-B-2026-11-12.md`。
- 核心安全拒绝/允许语义、timeout、Job Object 子进程树清理均为零证据；不能从 10 个限定 PASS 外推。`CORE-FAIL-CLOSED` PASS，仅证明授权失败时拒绝执行且 fail-closed。
- ZCode 没有发现可把这些失败独立归因到产品缺陷的证据；`icacls` 的底层错误码/环境原因未知。与 .NET TestHost Win32 error 5 不建立共同根因。
- 下一步按裁决运行最终 governance 并绑定审计 HEAD；Legacy 前端/Rust/npm-audit/packaged 仍 `NOT_RUN-legacy`，GUI 仍 BLOCKED。AUDIT-01–14 和 Release Gate 状态不变。

### 段 B governance suite 检查点（2026-11-12）

- `python audit/V1-FULL-AUDIT/tests/audit_runner.py governance` 已运行默认治理 check 一次，生成 HEAD=`3e0c960a482f5420666faec82d9c0f89e8396159`，branch=`main`，EXIT=0，elapsed=1.281s，3 条既有 warning。原始 log/JSON 固定在 evidence commit `1e9c15344`。
- 此 suite 仅执行默认 `check.ps1`；最后一笔 Task Canonical Evidence pinbackfill 后，仍须在最终 HEAD 执行 default + TaskPath `check.ps1`、`verify_pins.ps1`、`generate_api_inventory.py --check`。这些结果决定最终治理状态；当前 Task 和 Release Gate 未关闭。

### 段 B checkpoint Review 与补验（2026-11-12）

- ZCode fresh context 对 reviewed_head=`499a6b8e6eb293487abf391c46d00263230940ad` 给出 `PASS_FOR_CHECKPOINT`；Review 不是全审批准或 Task 关闭。完整 finding 摘要见 `reports/ZCODE-CHECKPOINT-REVIEW-SEGMENT-B-2026-11-12.md`。
- 原 Review 初始 R-1 为 `NOT_VERIFIED`；R-2/R-3 为 P3 Task 文案问题；R-4 是 probe 3 的非阻断 observation。原 Review 与 addendum 摘要分别见 `reports/ZCODE-CHECKPOINT-REVIEW-SEGMENT-B-2026-11-12.md` 和 `reports/ZCODE-CHECKPOINT-REVIEW-ADDENDUM-2026-11-12.md`。
- ZCode addendum 已关闭 R-1/R-2/R-3，R-4 保持 observation。R-1 补验由实现侧 Codex 在固定 reviewed_head 的 Git objects 上执行：37 个 diff 路径全部属于当时 `allowed_paths`；45 条 CANONICAL + 1 条 SOURCE_PIN 的 BLOB content SHA-256 全匹配且 `commit:path` 存在。ZCode 接受该日志为 closure evidence，但 actual 值未由 Reviewer 亲自重算。原始补验日志 `logs/review-checkpoint-recheck-20261112.log` EXIT 0；addendum 原始 CLI 记录 `logs/zcode-checkpoint-review-addendum-20261112.log` EXIT 0。
- 下一步：将 Review/addendum 原始日志与报告 pin 入 Task，重生成 Task ledger；随后在最终 pinbackfill HEAD 运行 governance default + TaskPath、18 pins、API inventory。完成门禁后，将固定交付 head 交给新的 ZCode 独立上下文作全审 review。AUDIT-01–14 仍因原始清单缺失保持阻断，Release Gate 仍为 BLOCKED。

### 段 B 最终 checkpoint Review（2026-11-12）

- ZCode 新独立上下文对 reviewed_head=`d9478939f2cee81104f18ea757d81cec71c36225` 给出 `PASS_FOR_CHECKPOINT`（0 P0 / 0 P1）；原始 CLI session/turn/trace 和完整回答见 `logs/zcode-final-audit-review-20261112.log`，摘要见 `reports/ZCODE-FINAL-CHECKPOINT-REVIEW-2026-11-12.md`。
- F-1/F-2 已按建议在 `logs/review-final-integrity-20261112.log` 补证：固定 `reviewed_head=d9478939f2cee81104f18ea757d81cec71c36225` 的 52/52 行 BLOB SHA-256 匹配、0 mismatch；两个 diff 区间共 36 个路径条目，全部在 allowed_paths；该日志生成于 HEAD `75e3aefb2c35c276086fad50ece70421a67fbb53`，EXIT 0。
- F-3 的四项治理门禁已在 `logs/final-governance-gates-20261112.log` 重新运行并完整落盘：generated HEAD=`b9b6c5801060370eb4171c30eb77a935800e2f6f`；default 与 TaskPath check 各 EXIT 0（各 3 warnings），18 pins EXIT 0（18/18），API inventory EXIT 0（1/79/6=86）。该日志生成前工作树 clean。
- 在 HEAD=`ac188dde54fed9bf8d0adc0f62bd25bb7adb8951` 又执行了完整复跑，并将输出、每项时点/EXIT 和 56 行当前 Task pin 逐项 blob 复算写入 `logs/postreview-final-verification-20261112.log`：default/TaskPath 各 EXIT 0（各 3 warnings），18 pins EXIT 0（18/18），API inventory EXIT 0（1/79/6=86），56/56 pin 无 mismatch；日志生成前工作树 clean。
- 原 ZCode Reviewer addendum 已将 F-1/F-2/F-3 全部 CLOSED、R-4 保持 observation；详见 `reports/ZCODE-FINAL-REVIEW-ADDENDUM-2026-11-12.md` 与原始 CLI log。addendum 提出的既有 Task pin 复算及 reviewed_head 到补证 HEAD 的路径集合跟进，已由 `logs/postaddendum-integrity-20261112.log` 覆盖：generated HEAD=`b17fead6d2cbbd2324ffb0a85096eb50448050ff`、reviewed_head=`d9478939f2cee81104f18ea757d81cec71c36225`，11/11 路径均 allowed、57/57 既有 pins 匹配、EXIT 0。后续 Task pinbackfill 与该 HEAD 的最终门禁结果见下方 2026-11-12 current-head checkpoint。

### ZCode current-head checkpoint 与补记（2026-11-12；范围恢复前的历史状态）

- ZCode fresh independent context 对 reviewed_head=`453327ff19ea012026b76d2e10cdcf2c93c58038` 给出 `PASS_FOR_CHECKPOINT`（0 P0 / 0 P1），session=`sess_210ecf7f-a2a3-4d81-a7df-f4f30596ea84`；报告和原始 JSON 分别见 `reports/ZCODE-CURRENT-HEAD-CHECKPOINT-REVIEW-2026-11-12.md`、`logs/zcode-current-head-checkpoint-review-20261112.log`。
- N-1 指出的状态/恢复文案滞后已更新；N-2 所需该 HEAD 四项门禁原始日志已写入 `logs/final-post-pinbackfill-gates-20261112.log` 并纳入 Task Canonical Evidence。N-1/N-2 均为 P3 finding，整改不改变原始限制；N-3/R-4 是 P4 observation。
- 该门禁日志 generated HEAD=`453327ff19ea012026b76d2e10cdcf2c93c58038`：default 与 TaskPath check 各 EXIT 0（各 3 warnings），18 pins EXIT 0（18/18），API inventory EXIT 0（1/79/6=86）；每项含 UTC 时点与完整输出。
- 当时 Task 继续 `in_progress`；AUDIT-01–14 被记为 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`。原始附件恢复后，该逐项状态被后续裁决更正为 `NOT_TESTED`；Release Gate 仍为 `BLOCKED`。pytest 的 16 个失败、.NET TestHost 与 smoke sandbox 阻断、未运行项目和真实 GUI/安装/升级回退缺口仍是有效证据限制。此 checkpoint 不等于全审完成、集成通过或 Task 关闭。

### 历史生命周期裁决更正与恢复点（2026-11-12；原始附件恢复前）

- ZCode 初次生命周期裁决曾建议 `closed_with_limitations`，但误把 Codex prompt 的选项描述归因给用户。更正裁决已明确撤回该授权论证和状态建议；初次报告仅作审计轨迹，标为 `SUPERSEDED`。
- 随后的更正裁决当时要求 Task 保持 `in_progress`，并等待对永久限制作具体取舍；其依据是原始专项清单缺失。
- 原始与更正裁决报告/CLI log 已列入 Canonical Evidence；见 `reports/ZCODE-LIFECYCLE-ADJUDICATION-2026-11-12.md`、`reports/ZCODE-LIFECYCLE-ADJUDICATION-CORRECTION-2026-11-12.md`。N-1/N-2 已闭合；产品测试失败、阻断与未验证限制保持原样。
- 后续对 Task 自身可达 Git 历史的定向搜索记录在 `logs/original-checklist-git-history-search-20261112.log`（generated HEAD=`5cb792e0966817bd642d173ab7db844b2dce092c`）：最早 Task blob `1248f2b8a` 只有通用 AC1–AC4 与 `AUDIT-00–14` 范围；`-SAUDIT-14`、`-S15项专项` 在 Task/audit 子树中未找到逐项定义。该日志已 pin 入 Task；只能说明当前仓库可达历史未保存该清单，不外推到仓外来源。

### 原始附件恢复与当前续审检查点（2026-11-12）

- 原始用户附件已恢复至 `source/ORIGINAL-USER-AUDIT-INSTRUCTIONS-2026-10-24.txt`，25,572 bytes；SHA-256=`3EA8E623AE7EC6E492385005828DC43368563A78E4A91C9CAF8BB75DBB399EAF`，raw worktree Git blob 与 HEAD blob 均为 `b775b8663c3827ed4a75d6b64ff2236b92151038`。恢复报告、两份恢复日志和原件均已纳入 Task Canonical Evidence。
- ZCode 原始范围恢复裁决的 CLI 外层记录：session=`sess_a2d20ca9-eaa7-49f8-95bf-2e67edbf8824`、turn=`turn_1a64fded-8e70-42b5-8f49-7fab16e23712`、trace=`422fc57e-18d3-48ef-927a-c580d3eed95a`、CLI EXIT=0。正文中的 ID 自述与外层 envelope 不一致，已在报告披露。ZCode 的 plan-mode shell 尝试被拦截，没有执行且无 shell EXIT；既有治理结果不是该会话重跑所得。
- 当前状态纠正为 AUDIT-00 limited PASS（只覆盖现有 baseline/source inventory）；AUDIT-01–14 全部 `NOT_TESTED`，不把 suite 结果外推为专项 PASS。Release Gate `BLOCKED`；Task `in_progress`；AC2/AC3/AC4 `PARTIAL`。原“等用户接受永久限制或重新提供清单”的分支终止，无需新的用户输入。
- 下一步按 ZCode 执行序列先补 AUDIT-00 的 `01_PROJECT_INVENTORY.md`，再做 AUDIT-01/02、suite 专项映射、AUDIT-11、AUDIT-08/05/06、AUDIT-14、合成验证和最终报告。实际 GUI、TestHost、sandbox grant、干净 Windows、真实付费 API 与私有漫画内容仍按各子项具名 `BLOCKED`/`NOT_RUN`；任何产品源码或超出 `allowed_paths` 的改动均停在新 Task 裁决。
- ZCode 裁决及阶段性门禁记录见 Task Canonical Evidence `ZCODE-ORIGINAL-SCOPE-ADJUDICATION-1`、`ZCODE-ORIGINAL-SCOPE-GATES-1`、`SCOPE-POSTCOMMIT-GATES-1`。此恢复检查点不等于全审通过、最终 Review 或 Task 关闭。

### AUDIT-00 静态项目盘点完成（2026-11-12）

- 报告 `reports/01_PROJECT_INVENTORY.md` 与命令日志 `logs/audit-00-inventory-20261112.log` 在 commit `943e4615afd34865818a1287461ac57188f430ca` 固定。日志 generated HEAD=`6f5153e47ff6adfcedde49712636c75e21bd43ef`；清单/接口/迁移/入口/model-pin 检查 EXIT 0；旧 `packaging/new_manga.spec` 在产品基线缺失的探测按预期 EXIT 128。
- Task pinbackfill 后门禁记录在 commit `c31278e0f532d3d2bebb969cd4c7943cf4407b8b`：generated HEAD=`caff9f29a52a2743ec0f25fc4c79b1dd9ba78ce4`；default check EXIT 0、TaskPath check EXIT 0（各 3 warnings）、18/18 pins EXIT 0、API 1/79/6=86 EXIT 0。Task 行已 pin 该门禁日志。
- AUDIT-00 状态更新为 `PASS`（静态盘点）；外部模型文件字节、构建、安装、真实 GUI 和运行时行为不在此 PASS 内。报告记录的陈旧打包说明/入口是待 AUDIT-02/12 复核的静态观察，未改产品文件。
- 当前下一步为 AUDIT-01/02 架构与静态扫描；AUDIT-01–14 仍为 `NOT_TESTED`，AC2/AC3/AC4 与 Release Gate 状态未变，Task 继续 `in_progress`。

### AUDIT-01/02 与 sidecar 生命周期复现检查点（2026-11-12）

- 审计检查 HEAD=`bb99ab8eaf07ddc95722ad7bd49e972a1c0054a7`；产品基线仍为 `10e4ee013835605800d3830fb960ae8d3aa04167`。AUDIT-01 阶段报告记 `FAIL`，AUDIT-02 记 `BLOCKED`；全审 Task 仍 `in_progress`，Release Gate 仍 `BLOCKED`。
- 机器扫描证据：`logs/source-architecture-scan-20261112.log` + `evidence/source-architecture-scan-20261112.json`（Python AST 268 文件 / 0 syntax errors；.NET 10 source projects / 13 refs / 0 project cycles）。`dotnet build` EXIT 0，日志 `logs/dotnet-build-audit01-02-20261112.log`；`dotnet format whitespace` EXIT 2、1,556 diagnostics，日志 `logs/dotnet-format-whitespace-20261112.log`；Python lint/type/security 工具发现见 `logs/python-tool-discovery-20261112.log`（七项均未安装）。
- `NM-AUD-0001` 通过 `tests/sidecar_lifecycle_probe.ps1` + `audit_runner.py sidecar-lifecycle` 隔离复现：正式 run `20261112T143133097703Z` 的 pre-cancel 与 direct dispose 后新 helper 均仍存活（dispose 约 2,011 ms 返回），日志和 JSON 记录 generated HEAD、程序集 SHA-256、argv 与 cleanup 成功；两个 helper 都已由 probe 终止。中间 run `20261112T142759897356Z` 复用了旧 PID marker，已在报告标为无效并排除。测试未调用真实 Core/Bridge sidecar、未访问用户数据；产品源码未改。
- 最新阶段说明见 `reports/AUDIT-01-02-ARCHITECTURE-STATIC-2026-11-12.md`，问题项见 `AUDIT_ISSUES.md`。下一步：按计划做 suite-to-audit 映射，随后 AUDIT-11 安全静态审阅；AUDIT-03–14 除已明示项外保持 `NOT_TESTED`。ZCode 需复核 `NM-AUD-0001` severity 和报告边界。

### suite 映射与 AUDIT-11 阶段检查点（2026-11-12）

- 起点 HEAD=`beaa13406438fab46ef56fa5a8852bf04ce7133d`，branch=`main`；本阶段开始时 tracked worktree clean。源代码/产品基线未修改。
- suite 证据映射见 `reports/SUITE-TO-AUDIT-MAPPING-SEGMENT-B-2026-11-12.md`；它保留既有 suite EXIT 和结果，不从总测试通过数推导专项 PASS。映射报告和日志记录生成 HEAD 与 EXIT。
- AUDIT-11 静态阶段报告见 `reports/AUDIT-11-SECURITY-STATIC-2026-11-12.md`，阶段结论 `FAIL`：`SEG-B-PROBES-001` junction 写越界、`SEG-B-PROBES-002` restore 磁盘写故障恢复缺陷均 Medium / High confidence；`NM-AUD-0001` 经 ZCode 对 `beaa13406438fab46ef56fa5a8852bf04ce7133d` 的阶段 Review `ACCEPT`，维持 P2。独立 Review 对 `e10fd1ee7e326255ffebb4ca529ecee5dfa477d9` 给出 `ACCEPT`（0 个 P0/P1/P2、1 个 P3）；P3 经字节复核确认是提交前删除一处尾随 ASCII 空格，未重跑 scanner，见 `reports/ZCODE-AUDIT-11-REVIEW-2026-11-12.md` 和 hash-drift log。
- 静态扫描 638 个源码文件、Python AST errors 0；dependency scan `dotnet list ... --no-restore` EXIT 0、18 projects/current configured sources 无已知漏洞结果，但可能查询 NuGet 网络；`pip-audit` 不可用。源码 manifest 23 个文件在产品基线与审计 HEAD 间无差异。精确命令、时点、generated HEAD、EXIT、hash 和副作用边界见对应 logs。
- 治理证据：阶段提交 `e0bbe10c3` 后第一次 default/TaskPath check 因 `doc/STATUS.md` 超预算各 EXIT 1；`c3bd266cb` 将状态摘要压缩后重跑 default/TaskPath check 均 EXIT 0（各 3 warnings）、`verify_pins.ps1` EXIT 0（18/18）、API inventory EXIT 0（1/79/6=86）。成功复核生成 HEAD=`c3bd266cb01007b8e9da679790433a149dfdc00e`；原失败和成功日志均保留以显示修复过程。
- Task pinbackfill HEAD=`9bcb1886bcdd6f49eadeb57d208458e52a994b2c` 上再次复核：default/TaskPath check EXIT 0（各 3 warnings）、18 pins EXIT 0（18/18）、API inventory EXIT 0（1/79/6=86）。日志由 commit `1d245610e51e11b48547c1c1b42f810344014d92` 固定并纳入 Task Canonical Evidence。
- 追加 Canonical Evidence rows 的 HEAD=`1e9f34e03a0cf10fede372c7e6ad11ffb8777eb0` 上又完成 default/TaskPath/pins/API 四项复核，均 EXIT 0（warning、18/18 与 1/79/6=86 详情见命令输出）；原始日志 commit `4177c2d31d327bb98f4bab0948449cdba223661f`，已在后续 pinbackfill 中纳入 Task Canonical Evidence。
- 检查点记录当时状态：AUDIT-00 limited PASS；AUDIT-01 FAIL/P2；AUDIT-02 BLOCKED；AUDIT-03、08 尚未完成；AUDIT-11 阶段 FAIL、Review ACCEPT，其余矩阵面 PARTIAL/NOT_TESTED。该 2026-11-12 顺序已由下方新检查点更新。
- 当时下一步为 AUDIT-08 与 AUDIT-05/06；AUDIT-08 已在下方 2026-11-13 检查点完成有限执行。产品修复、远端查询/补救、真实私人素材访问仍不在本 Task 范围。

### AUDIT-08 隔离数据库专项检查点（2026-11-13）

- 检查前 HEAD=`5802af0a2cf812b3a977f58c5b7c161bba2c9199`，branch=`main`；此前 AUDIT-08 探针源已提交，产品源码、Schema、依赖、契约和原有测试未改。
- `reports/AUDIT-08-SQLITE-PERSISTENCE-2026-11-13.md` 按原始 AUDIT-08 逐项登记覆盖与限制。最终合并批次 `284 passed / 0 skipped / EXIT 0`；4 个隔离探针及 connection ownership 6 项单独复跑也 EXIT 0。临时数据均在 `New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT/`。
- 独立复跑 `SEG-B-PROBES-002` 后再次确认 `database_changed=true`、`typed_error=false`、`rollback_id_in_error=false`、`pre_restore_packages=1`。EXIT 0 表示 finding probe 成功确认缺陷；AUDIT-08 状态为 `FAIL`，并非产品恢复通过。多文件部分写仍属未实测的静态推断。
- 原始命令/时点/generated HEAD/EXIT 固定于 `logs/pytest-audit08-*.log` 和同名 evidence JSON；初始 278 项批次发生在新增探针源提交前，不作最终批次依据。证据提交为 `057f7666c7e5d13a5cc68cae8f5d97079af35436`。
- 阶段报告及状态文档提交 `80b326f0542ce74bf6f5d3e8c993a6767236973e` 后，在 generated HEAD=`80b326f0542ce74bf6f5d3e8c993a6767236973e` 上 default/TaskPath check 各 3 warnings、EXIT 0；verify_pins 18/18、EXIT 0；API inventory 1/79/6=86、EXIT 0。四类原始输出固定在 `94cdcd58cbed5ffc91704955ae6db5d4b0b790e7`，并回填到 Task Canonical Evidence。
- Task Canonical Evidence pinbackfill HEAD=`0742a572eba783d9ff3b7a064850f0d932c98823` 与 `25614d45ef71894460ed1c6616837b5e60f3573e` 上 post-pinbackfill default/TaskPath check 各 3 warnings、EXIT 0；verify_pins 18/18、EXIT 0；API inventory 1/79/6=86、EXIT 0。前者日志 `logs/audit08-post-pinbackfill-*.log`，后者 `logs/audit08-final-pinbackfill-*.log`；均已纳入 Task Canonical Evidence。
- 未覆盖：真实/用户数据库、运行时任务转换、应用级路径迁移、真实损坏恢复、断电/硬件故障、多文件部分写及压力上限。未执行任何产品修复。
- 后续按当前 DAG 审阅 AUDIT-05/06，再推进 AUDIT-14、AUDIT-03/04/07/10/13 和可执行的 AUDIT-09/12。全审 AC2/AC3/AC4 `PARTIAL`，Release Gate `BLOCKED`。
- ZCode 对固定 head `fb1f6086b6436f6c471d1bd52e97873588450813` 的 AUDIT-08 首轮独立 Review 为 `ACCEPT`（0 P0/P1/P2、2 P3），报告与原始回执见 `reports/ZCODE-AUDIT-08-REVIEW-2026-11-13.md` 和 `evidence/zcode-audit08-review-20261113.json`。P3-1 指出“异常中断”未独立映射；已在覆盖矩阵单列，并明确仅有 error-path rollback 窄面证据。P3-2 指出 0742a572 上 post-pinbackfill 四项门禁日志未列入 Canonical Evidence；本次 pinbackfill 已添加该 HEAD 的 default log/JSON、TaskPath/pins/API 五项，亦 pin 了报告修订后 a932b756 HEAD 的四项门禁输出。
- 原始 28 条 AUDIT08 Canonical Evidence 的 raw Git blob SHA-256 已由 `logs/audit08-canonical-pin-hash-verify-20261113.log` 记录（生成 HEAD=`bc2858ec223cb9e2b93153ee8144606f2844ddc5`，28/28 PASS、EXIT 0）。其后在 HEAD=`f3320cc9de84dd769c60064537555d5ccd59005c` 独立复算当时 34 条 pins 与 `d6658d12` 五项最终门禁输出，39/39 PASS、EXIT 0；见 `logs/audit08-pin-verify-followup-20261113.log`。
- ZCode 对 `f3320cc9de84dd769c60064537555d5ccd59005c` 的 follow-up Review 为 `ACCEPT`（0 P0/P1/P2、1 P3）；P3-3 指出的 `d6658d123` 最终门禁五文件已加入 Task Canonical Evidence。原始回执、dispatch 与报告见 `evidence/zcode-audit08-followup-review-20261113.json`、`logs/zcode-audit08-followup-review-dispatch-20261113.log`、`reports/ZCODE-AUDIT-08-FOLLOWUP-REVIEW-2026-11-13.md`。P3-3 closure review 待执行；后续门禁日志按 Task 表注滚动纳入下一 pinbackfill。

### AUDIT-08 Review 收口后恢复点（2026-11-13）

- 本检查点从 HEAD=`f6aceb167813aaa9ef7a1ca4506538aa40a90fc9` 恢复；产品基线仍为 `10e4ee013835605800d3830fb960ae8d3aa04167`。本轮只更新审计证据与文档，不修改产品源码、原有测试、契约、Schema 或依赖。
- ZCode fresh-context closure Review 对 reviewed_head=`6375afacbd069b004c6af6adc7f79454d1307b70` 判 `ACCEPT`（0 P0/P1/P2），确认 P3-3 CLOSED，并发现 P3-4：follow-up 人类报告没有说明 dispatch SHA 采用 WORKTREE 字节，Task 表采用 Git BLOB 字节。两种值均真实，差异来自 CRLF→LF 归一化；报告已同步注明两种 hash basis，fresh closure re-review 尚未执行。报告、原始 JSON/stdout、prompt、dispatch 与 stderr 均已纳入 Task Canonical Evidence。
- 两批待回填 post-pinbackfill 门禁均已在 Task Canonical Evidence 表登记：generated HEAD=`ac55c50d93e0b8b9d9237346e26077abe608fe45` 与 `995a71d462408d7f75013554e611ce7a44f618a4`。每批 default / TaskPath check 各 3 warnings、EXIT 0；`verify_pins` 18/18、EXIT 0；API inventory 1/79/6=86、EXIT 0。每批五项（default log/JSON、TaskPath、pins、API）均保留各自生成 HEAD 与 EXIT。
- 当前工作树中 Task 卡的 pinbackfill 以及本恢复点文档待提交；之后须运行默认与 `-TaskPath` governance check、`verify_pins.ps1` 和 API inventory check，保存日志并提交。再对干净证据 HEAD 派发 fresh-context ZCode 只读 closure re-review，核验 P3-4 是否关闭；按回执更新 Task/恢复点并继续下一 DAG 节点 AUDIT-05/06。AUDIT-08 与全项目审计仍为 `FAIL` / `in_progress`，不得将门禁通过误记为专项或全审 PASS。
