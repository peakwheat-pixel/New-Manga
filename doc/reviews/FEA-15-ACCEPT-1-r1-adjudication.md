<!-- ZCode session: sess_2a802094-24f6-4254-9bfa-33cad3a6bf4e; turn: turn_1b88b29d-e756-4416-a92d-4ecd7e6f1c82; CLI EXIT 0. Response preserved verbatim below. -->

Review 报告与卡面已核验（含 EV/SRC 29 条 pin、`ui-process-smoke.log` 的 L1 诚实自标、AC 标记现状）。出裁决。

---

# 裁决：FEA-15-ACCEPT-1 r1 Review 处置与收口次序

## 〇、总裁定

r1（`sess_88acf941`，绑定 `e55a23dc9`，0×P0/P1）**质量合格、结论采信**。「approved 附 P2 处置条件」的合规形态既不是 changes_requested 返修循环，也不是保留未闭合条件直接集成，而是：**保持 `in_review` → 卡内闭合可闭合条件 → 固定最终内容 head 补门禁 → 原 Reviewer 增量复审 r2（绑定新 head）→ approved → 集成 → 终态**。P2-1 不在本卡闭合（越界），以「如实登记 + 挂后续 GOV 卡」作为本卡层面的处置完成。终态推荐 `closed_with_limitations`。诊断卡在本卡终态后释放，现在不释放。

## 一、Review 结论定性（用户核心问题）

- §4.1 明文「新 head 使旧 Review 结论自动降级」——**条件修正会产生新 head，r1 的 approved 不能平移**；但修正全部为 P2/P3 级文档措辞/表头/登记，不触及 r1 已核验的实质面（数字、日志、AC 判定），r1 自己的处置建议也是「收口时修正/顺手处理」，**不构成 changes_requested**。
- 因此采用项目既定先例（approved_with_conditions → 条件闭合 → r2 增量追认）：**r2 = 原 Reviewer 会话 `sess_88acf941`（只读新 head）**，核对范围限两点——①四条处置条件逐项闭合情况；②`e55a23dc9..最终 head` 增量 diff 无夹带无新问题。**不做全新全量复审**（22 文件+对象级核验重复一遍边际价值≈0）。禁止 Codex 自审不变；本裁决会话（`sess_2a802094`）不做 r2（保留第六步结论确认角色，避免裁决/审查角色混同）。r2 未出或未闭合前，**不得集成、不得终态**——未闭合条件不是通过。

## 二、逐项 Findings 裁决

**P2-1（26/29 pin 为本机 CRLF 工作区口径，跨 checkout 不可复现）——本卡不修，登记 + 挂后续 GOV 卡。**
- `.gitattributes` 不在本卡 allowed_paths（用户已明确），且 eol 口径是全仓治理决策不是本卡私事：r27 核验先例（300 pin 中 187 个为工作区字节口径）+ §4.4 硬要求（**改变 pin 校验语义的裁定必须先盘点受影响全集、实测基线矩阵，假设不符即作废**）——统一到 blob/LF 会让历史工作区口径 pin 大面积转红，必须先核验后裁定。
- **本卡内也不单独改 26 条 pin 值**：只改值不加 eol 规则会造成反向不可复现（本机复核又不匹配），口径修复必须「eol 规则 + pin 重算 + renormalize 决策」配套，整体属 GOV 卡。
- 本卡闭合方式 = 在 README（或卡面 Closeout）加登记行：「EV/SRC 29 条 pin 为本机 CRLF 工作区口径，26 条跨 checkout 不可复现（r1 P2-1），修复挂 pin 口径治理卡」——与验收卡诚实披露义务一致，登记到位即视为本卡处置闭合。**终态卡此后不回写**：GOV 卡的口径修正映射表放其自身 evidence 目录，经 LEDGER/PLAN 交叉引用，本卡字节保持原样。

**P2-2（README:9「堆栈指向 Directory.Exists(.git)」超范围表述）——卡内修正。**
README 在 allowed_paths。改为报告建议措辞：「堆栈终止于 `get_RepoRoot()` 的 NotNull 失败；`.git` 文件形态归因由源码审查与对照实验支持」。注意**连锁**：README 是 EV-04 pin 对象，修正后 EV-04 的 commit/sha256 必须回填至最终版所在 commit（见第四节次序）。

**P3-1（SRC 表缺表头）——修**（卡面内补表头行）。
**P3-2（三份裁决日志命名与时序相反）——只加注记，不改名不挪文件**（任何挪动=SRC pin 全废）。在 README 注明实际演进链：`zcode-second-decision-raw.log`（第二份）→ `zcode-serial-decision-raw.log`（串行化补充，撤回并行诊断卡）→ `zcode-evidence-decision.log`（第三份/最终），按 P3-2 澄清对照三份原文落注。
**P3-3（logs/ 子目录约定 vs 平铺）——不挪**（同上，pin 保全优先），README 加一行「实际平铺、功能等价、结构偏离证据计划文字」说明。
**P3-4（Handoff 概括句）——本卡不改 Handoff**；在 Closeout 记一句「概括句已经 r1 以 `git diff --name-status` 证实」，列举习惯留给后续卡。

**未验证项 1 / 处置 3（固定交付 head 最终门禁）——收口硬前置，必须补**：在最终内容 head（Commit 2 之后、日志入库之前）跑三件套（`check.ps1` 默认 + `-TaskPath` + `verify_pins`）全 EXIT 0、日志入库；随后收口 commit 再做一次**只读** `-TaskPath` 复核（AC5 标记翻 MET 后门禁须仍 PASS），EXIT 记入 Closeout 文字。r1 已确认 doc-only 差异对门禁低敏感，该双跑口径足以闭合 AC5。

## 三、AC 与终态定性

- AC1 维持 `[ ]` `<<PARTIAL: … 根因挂 FEA-15-DIAG-ACL-1>>`（实质读法：全量基线未满足；程序读法虽可辩 MET，但既有 PARTIAL 登记更诚实，不为了终态改判定）。
- AC5 在门禁留证 + 结论定型后翻 `[x]` `<<MET>>`（其义务=给出结论+门禁+diff 合规，均可满足；结论本身=「带 limitation」与 MET 不矛盾）。
- AC2/3/4/6 维持 MET。
- **终态推荐 `closed_with_limitations`**（非 done）：§4.2「done 要求所有已释放 AC 通过」，AC1 的红态面在 DIAG 卡闭环前无法 MET；FEA-15-A3-1 与 FEA-14 七切片均为同类先例。limitation 清单=①分类③（sandbox 15 + Host ACL 96 + export_hook 根因）挂 DIAG/FIX 卡；②A2 安装与 A4 真实用户库 NOT_RUN 挂 PACKAGE-GAP-1/后续；③P2-1 pin 口径挂 GOV 卡。`resource_closeout_status: complete` 在终态前翻转——三行 `PRESERVE_UNKNOWN` 即终态处置（**保留就是处置，不执行任何物理清理**；62 fixtures、`C:\Python314` ACL、AppContainer profile、clean-tree 均维持现状）。终态选择若用户另有指示，从其指示。

## 四、生命周期与提交/pin 次序（执行序列）

1. **Commit 1（r1 入库）**：`doc/reviews/FEA-15-ACCEPT-1-r1.md` 逐字提交（allowed_paths 已覆盖），不动其他文件。
2. **Commit 2（条件闭合·内容）**：P2-2 措辞修正 + P2-1 登记行 + P3-1 表头 + P3-2/P3-3 注记 + P3-4 Closeout 一句话。**此 head 即最终内容 head**。
3. **门禁三件套**在 Commit 2 head 上执行 → `gates-final.log` 写入 verification/。
4. **Commit 3（收口）**：gates-final.log + AC5 翻 MET + EV-04 pin 回填（指向 Commit 2 的 README blob/工作区口径同现有 29 条——本卡内一致，口径统一归 GOV 卡）+ Closeout 追加 r1 条件闭合记录；status 保持 `in_review`。随后只读跑 `-TaskPath` 复核一次（EXIT 记 Closeout）。
5. **r2 增量复审**：`sess_88acf941` 只读最终 head，按第一节范围出 `doc/reviews/FEA-15-ACCEPT-1-r2.md`（approved，绑定最终 head）→ **Commit 4**（r2 入库）。
6. **结论确认**：ZCode 裁决会话确认验收结论措辞与 limitation 清单、终态（closed_with_limitations）。
7. **集成（Codex）**：`integration_commit` 回填 + 集成后验证（check 默认一次）+ `resource_closeout_status: complete` + status → 终态 + STATUS/PLAN/LEDGER 指针移出 Active。不 push（维持 out_of_scope，除非门禁全过+用户授权）。
8. **释放后续卡**（唯一 Active 空出后）：`FEA-15-DIAG-ACL-1`（优先）→ 随其结论 `FEA-15-FIX-TESTDEBT-1`；`FEA-15-PIN-EOL-GOV-1`（pin 口径治理，§4.4 核验前置：受影响全集盘点→口径裁定→eol 规则→renormalize→历史 pin 处置）；`FEA-15-PACKAGE-GAP-1` 待用户产品决策。四卡串行释放（唯一 Active），DIAG 与 GOV 的先后可由用户调换，默认 DIAG 优先（测试红态根因优先于 pin 治理）。

**明确禁止**：本卡内动 `.gitattributes`、挪动/改名任何已 pin 文件、改 26 条 pin 值、以 r1 平移集成（无 r2）、任何物理清理、Codex 自审。

---

**推荐下一步**：Codex 按 1→4 执行（Commit 1 → Commit 2 → 门禁 → Commit 3），随后派发 `sess_88acf941` 出 r2。可转发指令：

```text
ZCode 裁决 2026-11-11（r1 处置）：r1 approved 附条件成立，采「条件闭合+r2 增量追认」路径，不做 changes_requested 循环、不保留未闭合条件集成。按序：1) Commit1 入库 doc/reviews/FEA-15-ACCEPT-1-r1.md 逐字不动。2) Commit2 条件闭合（最终内容 head）：README:9 改「堆栈终止于 get_RepoRoot() 的 NotNull 失败；.git 文件形态归因由源码与对照实验支持」；加 P2-1 登记行「EV/SRC 29 条 pin 为本机 CRLF 工作区口径，26 条跨 checkout 不可复现（r1 P2-1），修复挂 pin 口径治理卡」；SRC 表补表头；README 加三份裁决日志时序注记（second=第二份/serial=串行化补充/evidence=第三份最终）与「实际平铺、功能等价」结构说明；Closeout 记 P3-4 一句话。禁止动 .gitattributes、挪动/改名已 pin 文件、改 26 条 pin 值。3) 在 Commit2 head 跑 check.ps1 默认+-TaskPath+verify_pins 全 EXIT0 → gates-final.log。4) Commit3 收口：gates-final.log + AC5 翻 [x]<<MET>> + EV-04 pin 回填至 Commit2 的 README + Closeout 记 r1 条件逐项闭合；status 保持 in_review；再只读跑 -TaskPath 一次 EXIT 记 Closeout。5) 派 sess_88acf941 只读最终 head 出 r2（核对四条件闭合+e55a23dc9..最终head 增量 diff 无夹带，approved 绑定新 head）→ Commit4 入库 r2。6) ZCode 裁决会话确认结论措辞与 limitation 清单（分类③挂 DIAG/FIX、A2/A4 NOT_RUN 挂 PACKAGE-GAP、P2-1 挂 GOV）后 Codex 集成：integration_commit 回填+集成后验证+resource_closeout_status:complete（PRESERVE_UNKNOWN 三行即终态处置，不物理清理）+status→closed_with_limitations+指针更新。不 push。7) 本卡终态后串行释放 FEA-15-DIAG-ACL-1（优先）→FIX-TESTDEBT-1；FEA-15-PIN-EOL-GOV-1（§4.4 全集核验前置）；PACKAGE-GAP-1 待用户决策。
```
