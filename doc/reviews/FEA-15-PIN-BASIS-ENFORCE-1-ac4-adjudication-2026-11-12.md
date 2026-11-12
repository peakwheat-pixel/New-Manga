---
task_id: FEA-15-PIN-BASIS-ENFORCE-1
adjudicator: ZCode CLI 独立 AC4 adjudication session（与 AC4 v2 Review sess_426becfe-44b9-4e2e-9f16-9eaccdddbd05、AC2/AC3 adjudication sess_dbdb62fe-a206-4477-a209-657882bae35b、AC1d sess_fd863071-c665-4b61-89be-2156ace80595、AC1c A sess_72137bd6-9553-424d-b09f-4184866cd387、释放 sess_7b34d23e-ddaf-4ec5-bbb3-964edd74fc58 均为不同会话；未参与本 Task 任何实现、返修或 Review）
session: sess_b3fbf940-0ae4-446e-9eb0-e3d29e347451
decision_turn: turn_718a6417-c6ea-407e-8b4c-63ccd198ed4b
reviewed_head: 139ae06223d0458a97e8f37c5ef5b7480f3410b2
decision: AC4 ACCEPT_WITH_LIMITATIONS；P2-1/P2-2 均 ACCEPT_AS_LIMITATION；AC5 RELEASED（条件释放，见 §4）；R-001 与 Review-R-001 均不关闭
scope: AC4 增量裁决与 AC5 释放决定；不构成 AC5 最终 Task adjudication，不使 Task 进入 done，不批准最终集成关闭，不处置 R-001 终裁
---

# FEA-15-PIN-BASIS-ENFORCE-1 AC4 adjudication（2026-11-12）

## 0. 裁决性质、身份与基准

本报告是 **AC4 的增量 adjudication**，并决定是否释放 AC5。它不是 AC5 最终终裁。裁决者为本
adjudication session，全程只读：未改任何文件、未提交、未 push、未运行任何 gate/测试/AC5 门禁、
未执行四个历史 TaskPath。session/turn ID 已从 CLI JSON receipt 实测：sess_b3fbf940-0ae4-446e-9eb0-e3d29e347451 / turn_718a6417-c6ea-407e-8b4c-63ccd198ed4b。

裁决基准 HEAD `139ae06223d0458a97e8f37c5ef5b7480f3410b2` 的核实来源：会话附带 git 快照
（main @ 139ae0622，clean）、workspace 门禁日志 main-postfinal-card-gates-139ae0622.log 的
GENERATED_HEAD 同值且四项 EXIT=0，以及 Task/README/STATUS/PLAN 指针链互恰。本会话因只读
约束未自行运行 git 命令，此方法边界如实记录。

## 1. 裁决输入核实（只读，逐份读原文）

| 对象 | 核实结果 |
|---|---|
| Task 卡 doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md | AC1–AC3 `<<MET>>`；AC4 `<<PARTIAL>>` 待本裁决；AC5 `<<BLOCKED>>` 未释放 |
| STATUS.md / REBASELINE_PLAN.md | 两处均登记 in_progress、AC4 Review 完成待裁决、AC5 未释放；ACTIVE 唯一为本 Task，指针互恰 |
| AC2/AC3 adjudication（含 Addendum A） | ACCEPT_WITH_LIMITATIONS；AC4 释放范围 §5+A.1–A.4；AC5 NOT RELEASED；Review-R-001 DEFERRED 为 AC5 集成前置；释放裁决 R-001 留终裁 |
| AC4 v2 Review（sess_426becfe / turn_80b3a6dd） | APPROVED_WITH_LIMITATIONS，P0/P1=0，P2-1/P2-2/P3-1；建议处置方向与本裁决输入一致 |
| ac4-v2-t-gates-nativecwd.log | T default/TaskPath EXIT=1（Plan 7035/7000 bytes，各 2 warnings）；pins 16 mismatch（C01b/C02/C03/C05–C16/FEA01）EXIT=1；API EXIT=0；focused pytest 18 passed+9 subtests EXIT=0；ACTUAL_PROCESS_CWD=clone-t 全程在场的字段核验通过 |
| ac4-v2-f-gates-nativecwd.log | F default/TaskPath PASS（各 3 warnings）EXIT=0；pins 仅 C04b/C17 EXIT=1；API EXIT=0；focused pytest 16 passed+2 skipped+9 subtests EXIT=0 |
| ac4-v2-t-pin-eol-normalization.log | C1：16/16，normalized_sha256==pin_sha256==候选 HEAD blob，EXIT=0 |
| ac4-v2-generator-integrity-t.log / -f.log | C2：双侧各 2/2，HEAD_BLOB==BASE_BLOB==SOURCE_BLOB 且 blob SHA==PIN-POLICY-1 冻结 pin；T 侧 CRLF 归一化相等、F 侧 raw 相等（eol_matches_setting=True 双侧），各 EXIT=0 |
| ac4-v2-inventory-audit.log | FILE_DIFF=PASS 11/11（Addendum A.1 允许集精确匹配）；ROW_DELTA T/F 均 +8/-1/~0；8 条 ADDED 全部来自本 Task 卡；唯一 REMOVED 行为 evidence_id `ac1a-stop-readme` 的 README pin 更新替代（可归因 Task 生命周期）；4737 历史路径=1032 raw-equal+3705 T 侧归一化相等+0 failures；EXIT=0 |
| ac2ac3-full-pytest-4ed7f32.log | 61 passed、2 skipped、3 failed、62 subtests、EXIT=1；3 failed 全在 test_residual_runtime_identity.py（169 TABLE_DELIMITER，首例 CHAPTER-SELECTOR-1.md），与旧 dd6372420 baseline control 同名复现；本 checkpoint 未重跑 baseline（README/卡面如实披露） |
| ac4-v2-clone-creation-audit.log | START 22:21:18.6Z；T config last-write 22:21:20.9Z、F 22:21:29.4Z；checkout reflog 2026-11-12T06:20:42+08:00=22:20:42Z——确认该日志不能证明配置先于 checkout |
| 主线门禁 | 7b8b4abc2 与 139ae0622 两轮 default/TaskPath（各 3 warnings）/18 pins/API 均 EXIT=0（逐份读日志核实） |
| 错误 CWD 首跑 | README 明确登记四个 invalid/wrong-CWD 日志作废不用于结果；采纳 native-CWD 日志为唯一有效载体 |

## 2. AC4 裁决：ACCEPT_WITH_LIMITATIONS

AC4 验收语义（Windows autocrlf true/false fresh checkout 对照、三层逐行对照、Linux 未测则记
NOT_RUN）在候选 HEAD `4ed7f32b3ce9104ecee11aad593bde222055a0df` 双 clone 上全部成立且经独立
Review 与本裁决双重复核。接受以下已登记 limitation（均不得改写为 PASS）。

### 2.1 T/F 非零结果的解释（锚定确认）

1. **T default/TaskPath EXIT=1（Plan 工作树 7035 bytes > 7000 预算）**：机制与 AC1c A 裁决已
   锚定的 7056/6992 完全同源——autocrlf=true 检出使 LF blob 确定性膨胀为 CRLF。本裁决确认
   锚定为 autocrlf=true 环境确定性效应，非产品缺陷；结果保持 FAIL 原样。
2. **T pins 16 mismatch EXIT=1**：与 AC1c A 集合逐项一致，且 C1 归一化 16/16 闭合。保持 FAIL。
3. **F pins C04b/C17 EXIT=1**：与 dd6372420 基线集合一致的既有 EOL 限制。保持 FAIL。
4. **full suite 3 failed / EXIT=1**：基线同名复现、本 checkpoint 未重跑 baseline 已如实披露。
   保持 FAIL。
5. **Linux NOT_RUN；四个历史 TaskPath NOT_RUN；AC5 gates NOT_RUN。**

### 2.2 P2-1 处置：ACCEPT_AS_LIMITATION（不阻断 AC4）

- 理由：六份生成日志的输出 SHA 是生成时工作树 CRLF 字节，Canonical pin 是入库 LF blob 字节，
  属**证据标注口径**问题；内容零篡改已由双向字节核对闭合（如 audit JSON 28,227=27,650+577 CR），
  pin→blob 主链路 22/22 PASS。README P2-1 段已补录六组 worktree/blob SHA pair 对照表，双口径
  声明在场，实质满足 Review 的修复方向。标签澄清足以接纳为 limitation。
- 必要条件（AC5 交付内完成/保持）：(a) 六组 pair 对照表与双口径声明在 AC5 的 README/Task/
  Handoff 中保持在场，不得删除；(b) 历史日志与 pins 字节不动；(c) AC5 Handoff 固化声明
  「生成日志 SHA=生成时工作树字节；Canonical pin=Git blob 字节」；(d) 不要求任何产品代码改动。

### 2.3 P2-2 处置：ACCEPT_AS_LIMITATION（不阻断 AC4，附 AC5 文档前置）

- 理由：审计日志的 config last-write（22:21:20.9/22:21:29.4Z）晚于 checkout reflog
  （22:20:42Z）38.9/47.4 秒，且审计 START（22:21:18Z）介于其间——该日志**不能证明**两个
  clone-local 配置先于 checkout 写入，AC2/AC3 adjudication §5.1 指定的顺序证明义务未被满足。
  但 AC4 的实质命题（两 clone 分别处于 autocrlf=true/false 检出形态）有独立字节证据闭合：
  F 侧 4737 历史路径 raw-equal（LF）、T 侧 3705 项经 CRLF→LF 归一化相等、C2 双侧
  eol_matches_setting=True——若配置未生效，两侧不可能呈现与各自配置一致的互补确定性形态。
  时序命题与形态命题可分离，前者未证明、后者已证明。
- 必要条件：(a) **任何文档不得声称时序已被证明**；README「当前执行状态」段残留的
  「配置先于 checkout」旧表述须在 AC5 文档更新时按 P2-2 口径修正为「最终配置值已核实；顺序
  未经该审计日志证明」；(b) Codex 须在 AC5 交付文档中澄清 CONFIG_LAST_WRITE_UTC 与
  CHECKOUT_REFLOG_UTC 两字段的语义与采集方式（例如审计脚本是否重写 config 刷新 last-write、
  reflog 字段是 clone 还是 checkout reflog），或提供 reflog 原文等补充证据；无法澄清则永久
  登记为 evidence-quality limitation，**不得反向声称已证明先配置后 checkout**；(c) 后续任何
  fresh clone 顺序证明须按 AC1c B 先例形态采集（config last-write < checkout reflog），采集
  前不触碰 config；(d) 不要求重跑 T/F gates（行为结论不受影响）。

### 2.4 附带确认

- P3-1（7eef↔4ed 提交图映射）：接受为 informational，其登记义务转为 AC5 集成前置（见 §4 条件
  1）。candidate 4ed 为 dd6372420 上的 4 提交 cherry-pick replay、非 implementation 7eef 的
  祖先、主仓库无 4ed 对象——独立 Review 已核实四个实现/测试文件 blob 一致。
- 四个 wrong-CWD 首跑日志作废处置确认；native-CWD 日志为唯一有效载体。

## 3. AC4 小结

AC4 在已释放范围内判定 **MET（带 §2.1–§2.3 limitation，限 Windows；Linux NOT_RUN 如实
保留）**。Task 卡 AC4 行可由 Owner 更新为 `[x] <<MET>>`，正文引用本裁决并列明 limitation；
依据入 Canonical Evidence，不在行末标记写原因（v3 规则）。

## 4. AC5：RELEASED（条件释放）

前置齐备：AC4 经本裁决处置完毕；Review-R-001 四类负例测试已落地（ee0b25ac）并经 AC4 v2
Review 确认覆盖充分；主线 139ae0622 四项门禁 EXIT=0。**释放 AC5**，范围与条件如下：

1. **候选映射与集成形态（防误集成）**：AC5 集成 = 将实现分支四个提交
   （fd843602→5e216dc5→ee0b25ac→7eefb54d，branch `codex/fea-15-pin-basis-enforce-1`）
   cherry-pick（或等价内容合入）到当前 main HEAD，产生集成 head；**禁止**直接合并/推送 4ed
   （其对象仅存在于 validation clone，主仓库不可达）。合入后须校验四个文件 Git blob 与已核实
   值一致：check.ps1=1a6f7ab3…、TASK.md=89371702…、test_canonical_evidence_basis.py=2b82fb2d…、
   test_architecture_assertions.py=26f79e8a…。集成提交/Handoff 登记映射：implementation 7eef ↔
   candidate 4ed ↔ 集成 head。
2. **必跑 gates（集成后 main HEAD 逐项实跑并记录 HEAD/UTC/EXIT）**：check default、check 本卡
   TaskPath、四个历史 TaskPath（AGPL-RELEASE-1、AD002-FOLLOWUPS-1、FEA-06-PREREQ-1、
   CHAPTER-SELECTOR-1）、verify_pins（18 pins）、API inventory。任何 FAIL 如实登记并停止回报
   裁决，不得改写、不得修补历史文件。
3. **full suite 口径**：非卡面 AC5 强制项；若运行，3 个 residual runtime identity failures 预期
   同名复现，必须原样保留 FAIL/EXIT=1；建议（非强制）在集成后 head 重跑一次以消除「本
   checkpoint 未重跑 baseline」披露缺口。不得以 full suite 红态掩盖或替代 gates 记录。
4. **文档义务（集成提交内或之前完成）**：§2.2 与 §2.3 的全部必要条件；P3-1 映射登记；Handoff、
   Canonical Evidence、Resource Manifest 刷新；Linux 维持 NOT_RUN 记录；T/F 非零结果与 3 failed
   全部按 FAIL 保留。
5. **Review/终裁独立性**：AC5 集成后须由 fresh ZCode session（与既往全部 session 不同）独立
   Review，再由另一个不同 session 的最终 adjudication；R-001（释放裁决保留项）与 Review-R-001
   的终闭合由最终 Integrator disposition 显式裁定。本裁决不构成 AC5 终裁、不使 Task 进入
   done、不批准最终集成关闭。
6. **继续禁止**：不迁移历史 pin；不改 .gitattributes、18 frozen pins、verify_pins.ps1、历史
   Task/Review/Handoff/checkpoint/evidence 字节；不做 renormalize 及 dry-run；不清理/prune/
   GC/repack；不 push（push 另需用户授权）。

## 5. 保留项状态（均不自动关闭）

| 项 | 状态 |
|---|---|
| R-001（释放裁决保留项） | 开放，留 AC5 最终 Integrator adjudication 显式裁定 |
| Review-R-001（AC2/AC3 Review P2） | 负例已落地且确认充分；终闭合确认仍在 AC5 终裁 |
| 四个历史 TaskPath | NOT_RUN；AC5 释放后为 AC5 gates 必跑项（本裁决未执行） |
| Linux cross-check | NOT_RUN 维持；无真实环境则如实记录，不因 AC5 释放消失 |
| T Plan 预算 FAIL / T 16 mismatch / F C04b/C17 / full suite 3 failed | 保持 FAIL 原样，任何文档不得改写为 PASS |
| worktree/blob 双字节口径（含 P2-1）/ P2-2 时序未证明 | limitation 登记，进 AC5 Handoff |

## 6. 诚实性边界

本裁决全程只读，未修改任何文件、未提交、未 push、未运行任何测试或门禁、未执行四个历史
TaskPath；输入核实仅基于文档与既有日志原文读取。session/turn ID 落盘时取真实值；伪造、篡改
或回退为占位符视为证据缺陷。本裁决不称为最终 Task 完成：AC5 的最终集成、独立 Review 与
Integrator disposition 未实际完成前均维持 NOT_RUN。
