<!-- ZCode session: sess_2a802094-24f6-4254-9bfa-33cad3a6bf4e; turn: turn_5f3a0fe6-11a5-4688-8767-c246c80cb5ff; CLI EXIT 0. Response preserved verbatim below. -->

r2、提交链（`d0d8a3ab1` ← `aeac7a8c1`，工作区 clean）与全部前置事实核验完毕。r2 的 approved 附三项收口前置均在本裁决覆盖范围内。以下为最终收口裁决。

---

# 最终裁决：FEA-15-ACCEPT-1 终态授权与后续任务释放

## 一、`closed_with_limitations` 授权：**确认成立**

依据链（协议 §4 终态条款逐项满足）：
1. **用户明确裁决**：用户本轮请求明示求授终态，连同全程裁决链（授权接续、Owner 改派、收口路径、r1 处置）构成协议要求的用户裁决依据；
2. **scope 冻结预设缺口路径**：DSH 2026-11-10 冻结 + FEA-15 §S5 用户批准范围本就预设 NOT_RUN/缺口披露；
3. **双 Review approved**：r1（`e55a23dc9`，0×P0/P1）+ r2（`d0d8a3ab`，0×P0/P1/P2，r1 四条件闭合核验 + P2-1 延期独立判定成立）；
4. **done 门槛不可达**：AC1 的 A5 红态面（pytest 16 fail / .NET 127 fail，分类③根因未定）在诊断/修复卡闭环前无法 MET，§4.2「done 要求所有已释放 AC 通过」不满足——closed_with_limitations 是唯一诚实终态；
5. **先例**：FEA-15-A3-1、FEA-14 七切片同类收口。

**验收结论定型：带 limitation 的验收收口（closed_with_limitations），原始全量 16/127 fail 保持原始状态登记、不得改称通过。** Limitation 清单三条：①分类③（sandbox 15 + export_hook 3 + Host ACL 96 根因未定）挂 `FEA-15-DIAG-ACL-1` → `FEA-15-FIX-TESTDEST-1`（笔误防歧义：任务 ID 以建卡时登记为准，建议 `FEA-15-FIX-TESTDEBT-1`）；②A2 当前版本安装 / A3 可见 UI / A4 真实用户库 NOT_RUN，挂 `FEA-15-PACKAGE-GAP-1`（待用户产品决策）与后续卡；③P2-1 pin 口径（**30 条中 27 条**工作区口径，含 SRC-25，以 r2 P3-A 当前全集为准）挂 `FEA-15-PIN-EOL-GOV-1`。

## 二、AC5 确切措辞与门禁收尾

```
- [x] **AC5 结论与门禁**：验收结论（通过/带 limitation/不通过）+ `check.ps1`（默认 + `-TaskPath`）+ pins；diff ⊆ allowed_paths。 <<MET>>
```

- AC1 维持 `[ ]` `<<PARTIAL: 构建和 pins PASS；pytest 与 .NET 全量 EXIT 1，部分失败根因仍待诊断>>`（理由仍准确，不改写为 PASS——终态条款要求）。
- 依据入 Closeout（MET 不带行内原因）：结论=closed_with_limitations；门禁=`gates-final.log`（delivery_head `ab31381fa` 三件套 EXIT 0）+ `d0d8a3ab` 2026-11-11 00:23 登记后双跑 PASS/3 warnings/EXIT 0 + pins 18/18；diff ⊆ allowed_paths（r1 全量 + r2 增量核验）。
- r2 前置 1 补齐：00:23 复核结果**记入 Closeout**（若未记）；终态 commit（AC5 翻 MET + 元数据）之后再只读跑一次 `-TaskPath`（验证 `[x]+MET` 组合，EXIT 补记 Closeout）。P3-B/C 同步闭合：翻 MET 即改写过时理由，链条完整。

## 三、终态元数据与资源记录（终态 commit 内容，全部 ⊆ allowed_paths）

- frontmatter：`status: closed_with_limitations`；`resource_closeout_status: complete`；`canonical_evidence_status: complete`（已 ✓）；`delivery_head: ab31381fa`（已 ✓）；reviewer 会话 ID（已 ✓）。
- `integration_commit` 自引用处理：终态 commit 无法自含 hash，由**紧随的治理 commit**（第四节建卡 commit）回填——`17618c0fb` 回填先例。
- Closeout 追加终态行：验收结论与 limitation 三条；00:23 复核与终态后复核 EXIT；P3-A 事实修正（「受影响 pin 全集以 r2 P3-A 为准：30 条中 27 条；README 登记行保持原字节不再改」——**不动 README**，避免 EV-04 pin 链再翻）；资源终态声明。
- 资源记录（终态处置=保留，**不执行任何物理清理**）：62 fixtures / `C:\Python314` ACL / AppContainer profile = `PRESERVE_UNKNOWN`；clean-tree 构建 = `PRESERVE_REFERENCED`；均已在 manifest，closeout 行确认即 complete。
- 同 commit 内（PLAN/LEDGER/STATUS 属本卡 allowed_paths，导航回填合规）：PLAN 节点行翻终态 + **DIAG 与 GOV 两卡 proposed 节点登记**（闭合 P3-D 一半）；LEDGER 同步；STATUS 移出 Active 指针。

## 四、后续任务释放

**A. `FEA-15-DIAG-ACL-1`（本卡终态后立即创建并 ready，成为唯一 Active）——冻结范围授权**：
- `kind: diagnosis`、`governance_version: 3`、`owner/suggested_owner: codex`、`depends_on: [FEA-15-ACCEPT-1]`、base=建卡时实测 main HEAD、主树串行、`evidence_dir: verification/FEA-15-DIAG-ACL-1/`；
- `allowed_paths`：本卡 + `doc/reviews/FEA-15-DIAG-ACL-1-*.md` + `doc/handoffs/FEA-15-DIAG-ACL-1-*.md` + `verification/FEA-15-DIAG-ACL-1/**` + STATUS/REBASELINE_PLAN/TASK_LEDGER 导航回填；
- **Scope 五项**：① sandbox 15 + export_hook 3 根因（AppContainer 执行链、系统标准库/用户包依赖、既有 48/24 ACE 状态影响）；② Host ACL 96 项根因（`SourceSecurity.PrivateDirectory→SetSecurityInfo`，跨环境复现条件矩阵）；③ `C:\Python314` ACE 与 AppContainer profile 归属可行性评估（**只评估不清理**）；④ 62 共享 fixture 处置方案（只出方案）；⑤ 修复建议清单（含 v7 测试债要点，作 FIX 卡输入）。允许「不可判定」结论但须给出证据边界。
- **out_of_scope**：不改生产/测试代码、不修/不撤销任何 ACL、不清理任何文件、不动冻结契约、不 push；系统解释器 ACL 写入禁令持续。

**B. `FEA-15-PIN-EOL-GOV-1`：proposed 登记，不 ready。**
- **proposed 登记的合规路径（用户问题）**：PLAN/LEDGER 的 proposed **节点行**在本卡 allowed_paths 内，随终态 commit 登记；**卡文件创建不属本卡 allowed_paths**，走紧随其后的**独立治理 commit**（治理动作先例 = `164ebabcf` 冻结 commit 本身即建卡+PLAN 登记、不属任何任务 diff）。该治理 commit 同时：创建 DIAG 卡（ready）+ GOV 卡（proposed）+ 回填上一 commit 的 `integration_commit` + STATUS 指向 DIAG。
- GOV 卡释放前置 = §4.4 语义核验：受影响全集盘点（**基数 30 pin 中 27 条，含 SRC-25**；并复核 r27 的 187 条历史工作区口径 pin）→ 口径裁定 → eol 规则设计 → 基线矩阵实测 → `.gitattributes` 变更 → renormalize 决策 → 历史 pin 处置方案。盘点未完成不得改 `.gitattributes`。

**C. 唯一 Active 顺序**：本卡终态 → `FEA-15-DIAG-ACL-1`（Active）→ 终态后串行 `FEA-15-FIX-TESTDEBT-1`（条件=诊断结论）→ `FEA-15-PIN-EOL-GOV-1`（默认后置于 FIX；用户可调换）→ `FEA-15-PACKAGE-GAP-1` 恒待用户产品决策，不自动释放。

## 五、真实阻塞

**无。** 全部收口动作有协议条款与仓库先例支撑；不触冻结契约、不动 `.gitattributes`、不要求任何越界写入。唯一注意事项（非阻塞）：终态 commit 与建卡治理 commit 分两次提交，前者严格 ⊆ 本卡 allowed_paths。

---

**推荐下一步**：Codex 执行收口双 commit（终态 commit → 治理 commit），完成后 FEA-15-DIAG-ACL-1 认领开工。可转发指令：

```text
ZCode 最终裁决 2026-11-11（FEA-15-ACCEPT-1 收口）：r2 approved（绑定 d0d8a3ab）+三项前置被本裁决闭合，授权终态=closed_with_limitations（依据：用户裁决链+scope 预设缺口路径+双 Review approved+done 门槛不可达+A3-1/FEA-14 先例）。Commit A（终态，⊆ 本卡 allowed_paths）：status→closed_with_limitations；resource_closeout_status→complete；AC5 翻 [x]<<MET>>（理由改写：结论=带 limitation 收口；门禁=gates-final.log@ab31381fa 三件套+d0d8a3ab 00:23 双跑 PASS 3 warnings+pins 18/18；diff ⊆ allowed_paths r1/r2 核验）；AC1 维持 PARTIAL 不改；Closeout 追加：验收结论+limitation 三条（分类③挂 DIAG-ACL-1/FIX-TESTDEBT-1；A2/A3/A4 真实层 NOT_RUN 挂 PACKAGE-GAP-1 待用户；P2-1=30 条 pin 中 27 条工作区口径挂 PIN-EOL-GOV-1，README 登记行保持原字节）、00:23 复核 EXIT、资源终态声明（PRESERVE_UNKNOWN/PRESERVE_REFERENCED 即终态处置，不物理清理）；PLAN 节点翻终态+DIAG/GOV proposed 节点行；LEDGER 同步；STATUS 移出 Active。Commit A 后只读跑 check.ps1 -TaskPath 一次 EXIT 补记说明（随 Commit B 或 Closeout 追记）。Commit B（独立治理 commit，不属任何任务 diff，先例 164ebabcf）：回填 Commit A 为 integration_commit；创建 doc/tasks/FEA-15-DIAG-ACL-1.md（ready：kind=diagnosis、gov v3、owner=codex、depends_on FEA-15-ACCEPT-1、主树串行、evidence_dir=verification/FEA-15-DIAG-ACL-1/、allowed_paths=本卡+reviews+handoffs+该 verification 目录+STATUS/PLAN/LEDGER 导航回填；scope 五项=①sandbox15+export_hook3 根因②Host ACL96 根因③Python314 ACE/profile 归属可行性评估（只评估不清理）④62 fixture 处置方案⑤修复建议清单含 v7 测试债要点；out_of_scope=不改生产/测试代码/不修不撤销 ACL/不清理/不触冻结契约/不 push/系统解释器 ACL 写入禁令持续；允许不可判定结论但须给证据边界）；创建 doc/tasks/FEA-15-PIN-EOL-GOV-1.md（proposed 不 ready；释放前置=§4.4 全集盘点：基数 30 pin 中 27 条含 SRC-25+复核 r27 的 187 历史工作区口径 pin→口径裁定→eol 规则→基线矩阵→.gitattributes→renormalize→历史 pin 处置；盘点未完成禁改 .gitattributes）；STATUS 指向 DIAG-ACL-1 为唯一 Active。后续顺序：DIAG-ACL-1→FIX-TESTDEBT-1→PIN-EOL-GOV-1（可调换）→PACKAGE-GAP-1 恒待用户。全程不 push、不动冻结契约、不清理任何文件。原始全量 16/127 fail 保持原始登记。
```
