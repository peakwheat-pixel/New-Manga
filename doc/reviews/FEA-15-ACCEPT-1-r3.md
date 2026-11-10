<!-- Reviewer session: sess_88acf941-2220-4c42-a4bf-ca95923a8cfe; turn: turn_9468ad3b-8897-4f2f-ac00-80593bbc27a7; CLI EXIT 0. Response preserved verbatim below. -->

全部核验完成。以下为 r3 收口增量审查报告。

---

# FEA-15-ACCEPT-1 独立 Review r3 报告（收口增量审查）

- **Reviewer**：ZCode 独立 Review 会话（r1/r2 原作者会话，落盘标注 `sess_88acf941-2220-4c42-a4bf-ca95923a8cfe`；未参与实现/返修/裁决，全程只读——未修改文件/提交/删除/push）
- **Reviewed head**：`9629beca79b4310a60bf7a333f6e6d05c598fa51`（= 当前 main HEAD，工作区 clean）
- **增量范围**：`d0d8a3ab..9629beca` 共 6 个提交（aeac7a8c1 r2 入库 → bf8eedd64 最终裁决 → 1ecd61332 资源证据 → b64f743fb SRC-26..28 登记 → 78f394ceb DIAG/GOV 建卡 → 9629beca7 终态+指针切换），12 个文件，全部 ⊆ allowed_paths 或属裁决授权的独立治理 commit（建卡先例 `164ebabcf`）；`.gitattributes` 零改动；无生产代码/测试/契约字节改动

## 结论：**approved**（0×P0/P1，1×P2 + 4×P3；P2 为收口补证项，绑定 integration_commit 回填同批完成，不推翻终态）

`closed_with_limitations` 终态授权链完整成立；诚实义务（失败/NOT_RUN/未修复项不称通过）逐项核验通过；保留资源经我独立核验真实存在，非仅凭检查器放行。

## 核验明细

| 核验点 | 结果 |
|---|---|
| 最终裁决 + closeout-gate 裁决 | 两份均 `sess_2a802094` 出具、原字节入库；终态授权五项依据（用户裁决链、scope 预设缺口路径、r1+r2 双 approved、done 门槛不可达【AC1 红态无法 MET】、A3-1/FEA-14 先例）核验成立；closeout-gate 裁决三原则（减行先行、建卡先于指针切换、指针永不悬空）在执行链中被遵守 |
| AC 标记 | **AC1 保持 `[ ]` `<<PARTIAL`**（全量 EXIT 1 原样，未改称通过）✓；**AC5 翻 `[x]` `<<MET`**，依据=最终裁决 §二确切措辞（结论=带 limitation 收口；门禁=gates-final@delivery_head 三件套 + 00:23 登记后双跑；diff ⊆ allowed_paths r1/r2 核验）✓；§4.3 一致表合法（`:749` 允许 closed_with_limitations 保留 `[ ]` AC）✓ |
| 失败与 NOT_RUN 不被误称通过 | Closeout「保留限制」行原样保留 pytest 16 failed / .NET 127 failed、安装/可见 UI/真实库升级回退 NOT_RUN；STATUS「刚收口」与 PLAN 节点行同口径 ✓ |
| SRC-26/27/28 pin | **三方一致**（blob=工作区=声称，@`1ecd61332`）✓；三条为 blob 口径 pin，不扩大 P2-1 受影响集 |
| resource-manifest.json | 7 资源行、`closeout_counts` deleted/moved/migrated/archived 全 0、各资源 deleted/moved/modified 全 false——**未清理任何资源** ✓；AppContainer profiles 行用**描述性集合**（`用户级 AppContainer profiles（具体实例与路径未知；*）`）+ `PRESERVE_UNKNOWN`，process_check/notes 明示「未知实例不作存在性断言」「不是假定的具体磁盘路径」——比 closeout-gate 裁决原案（NOT_APPLICABLE）更诚实，不虚构路径 ✓ |
| **保留资源真实性（独立核验，非检查器放行）** | manifest 声称的全部真实路径逐一 Test-Path 通过：隔离根/clean-tree/clean-tree 构建树/FEA-11 fixtures/C:\Python314\python.exe/C:\Python314 均存在，类型一致；构建产物 `NewManga.App.exe` 在位；`git worktree list` 确认 clean-tree 为登记的 linked worktree（detached `d63d735a7`）；旧安装包仍在。**附注**：FEA-11\fixtures 实有 **18,310 个目录**（test_ 前缀 17,885），远超 62 候选——manifest 的「62 项仅按时间窗观察」表述准确（未声称全集），且此规模佐证「归属未证明、不清理」是唯一安全处置 |
| workspace-inventory 两份 | 首份（follow）：`files=49681; errors=30; EXIT=1`，30 个 ERROR 全为 `[WinError 5]`、集中于 `source-fixture\.{codex,dsh,gemini,qoder,workbuddy}\skills\*`；nofollow：`entries=49711; links=32; errors=0; EXIT=0`。SRC-27 如实标「**资源清点（不完整）**」✓。我实测其中 `ask-matt` 等为指向 `~/.skills-manager` 的**符号链接**（nofollow 的 links=32 与此吻合）——首份的拒绝访问与链接遍历相关，两份并存+不完整标注诚实 |
| DIAG/GOV 新卡与指针原子切换 | `FEA-15-DIAG-ACL-1`（ready、owner=codex、depends_on=ACCEPT-1、scope 五项+只读 out_of_scope 与最终裁决 §四A 一致）与 `FEA-15-PIN-EOL-GOV-1`（proposed、pending_scope_review、§4.4 前置+「执行前必须重新盘点当前全集」）建卡于独立治理 commit ✓；**9629beca7 单 commit 内完成 ACCEPT-1 终态 + STATUS 指针切 DIAG**（单一指针原子切换、无悬空瞬时态）✓；PLAN 本卡行翻终态+两卡合并行（ready/proposed 串行）、LEDGER 全部计数同步（582→584、cwl 51→52、in_review 3→2、proposed 5→6、ready 1→2、named-in-plan 2→3）✓ |
| Review 完整性 | r1/r2/两份裁决/r2 报告全部入库；r2 三项前置闭合（00:23 复核已记 Closeout、AC5 已翻 MET、终态已定）✓ |

## Findings

### P0 / P1

无。

### P2

**P2-R3-1 终态 head 的门禁留证缺口（终态后 `-TaskPath` 复核未入账、00:23 复核无日志文件）**
- 事实：仓库内不存在任何 HEAD=`d0d8a3ab` 或 `9629beca` 的门禁日志文件（evidence_dir 仅有 gates.log/gates-post/gates-control/gates-final 四份，最新为 `gates-final.log`@`ab31381fa`、00:21、4 warnings）。Closeout 记载的「`d0d8a3ab1` 00:23 登记后默认和指定 Task 检查 PASS（3 warnings、EXIT 0），pins 18/18」**仅有文字记录、无日志留证**；最终裁决 §二明文要求的「终态 commit 之后再只读跑一次 `-TaskPath`（验证 `[x]+MET` 组合），EXIT 补记 Closeout」在 `9629beca` 上**既无 Closeout 记录也无日志**——而 `[x]+MET` 的 AC5 组合恰恰首次出现在该 head。用户侧确认当前默认/指定 gate 与 18 pins 均 EXIT 0，但该结果未落任何账面。
- 为什么是 P2 而非 P1：终态授权依据链（用户裁决+r1/r2 approved+done 不可达）不依赖这份日志文件；00:23 复核有带时间戳的文字记录且 3 warnings 与 SRC-25 登记后的预期完全自洽；补证动作与既定待办（`integration_commit: null` 回填）天然同批。
- 处置（approved 的组成条件）：下一次治理 commit（回填 integration_commit 时）同批执行——在最终 head 跑默认+`-TaskPath`+pins 三件套 → 日志落 `verification/FEA-15-ACCEPT-1/`（其「evidence_dir 未登记过程文件」警告按既有机制登记为 SRC-29 消解）→ Closeout 补记两条 EXIT（00:23 复核补档说明 + 终态后复核）。

### P3

- **P3-R3-1 pin 基数现值更新**：卡内 pin 总数现为 **33 条**（EV5+SRC28），跨 checkout 不可复现仍为 **27 条**（SRC-26/27/28 三方一致、不计入）。Closeout/最终裁决的「30 中 27」是 r2 时点数；GOV 卡已自我要求「执行前必须重新盘点当前全集」（处理正确），本报告代为登记 r3 现值 33/27 供其直接采用。
- **P3-R3-2 STATUS「测试基线」行滞后**：仍写 PREREQ-2 旧数「pytest 3446/0/10；.NET 1804/0/107（0 failed）」，与本卡实测 3515/16/12、127 failed 并存且未标时点，易误读为当前基线 0 failed；建议随下一治理 commit 更新或注明「PREREQ-2 时点，ACCEPT-1 实测见 verification/FEA-15-ACCEPT-1/」。
- **P3-R3-3 README NOT_RUN 段末行滞后于终态**（「r2、最终验收结论与最终门禁仍待完成」已过时）——系最终裁决 §三「不动 README、避免 EV-04 pin 链再翻」的**明示决策**，非违规；提示后续读者以 Closeout Record 为准，可留 GOV 卡统一处置。
- **P3-R3-4 资源表移出任务卡后的检查器语义边界**：任务卡 Resource Manifest 表整体替换为 JSON 引用后，`check.ps1` 的 PRESERVE_*/integrity 行校验不再作用于本卡资源（门禁 EXIT 0 不再覆盖资源路径真实性）。JSON 内容诚实且比原表格详尽，路径真实性已由本 r3 独立核验补位；建议在 GOV 卡或治理工具演进时把 JSON manifest 纳入检查器管辖，避免「检查器放行」与「路径证实」在后续卡中再次脱钩。

## 未实测项

1. 本 r3 未复跑任何门禁/测试/构建；9629beca 上的门禁结论以用户侧通报 EXIT 0 为凭，文件留证待 P2-R3-1 处置补齐。
2. `integration_commit: null` 待回填（裁决既定安排，与 P2-R3-1 同批）。
3. source-fixture 下 30 个 ERROR 的 ACL/符号链接根因未深挖（属 DIAG-ACL-1 观察 input，不属本卡）。
4. FEA-11 fixtures 18,310 目录的全量归属/清点未做（超出本卡范围；62 候选时窗观察为登记口径）。
5. GOV/DIAG 两卡内容仅作建卡合规性审查（ready/proposed 状态、scope、allowed_paths、out_of_scope），其执行未开始、无可审。

---

**推荐下一步**（可直接转发）：

> **致 ZCode 裁决会话（`sess_2a802094`）/ Codex**：r3 收口增量审查已出，结论 **approved**（绑定 `9629beca`；终态 `closed_with_limitations` 与指针切换核验成立，保留资源经独立核验真实存在）。下一步单批治理 commit 完成：① 在最终 head 跑 `check.ps1` 默认+`-TaskPath`+`verify_pins` 三件套，日志落 `verification/FEA-15-ACCEPT-1/gates-closeout.log` 并登记 SRC-29（P2-R3-1）；② 回填 `integration_commit`；③ Closeout 补记两条复核 EXIT；④ 顺手处置 P3-R3-2（STATUS 测试基线行标注时点）。随后 `FEA-15-DIAG-ACL-1`（ready、Owner=Codex）即可认领开工——建议把 source-fixture 符号链接/ACL 观察（r3 附注）纳入其 AC1 环境矩阵 input。本报告请逐字保存至 `doc/reviews/FEA-15-ACCEPT-1-r3.md` 并记录本会话 ID。
