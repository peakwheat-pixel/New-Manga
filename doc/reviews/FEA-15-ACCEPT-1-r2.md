<!-- Reviewer session: sess_88acf941-2220-4c42-a4bf-ca95923a8cfe; turn: turn_e86a8a39-851f-49ff-8e9b-eae70e132e0b; CLI EXIT 0. Response preserved verbatim below. -->

增量核验完成。以下是 r2 复审报告。

---

# FEA-15-ACCEPT-1 独立 Review r2 报告（增量复审）

- **Reviewer**：ZCode 独立 Review 会话（r1 作者会话，r1 报告落盘标注 `sess_88acf941-2220-4c42-a4bf-ca95923a8cfe`；本 r2 由同一 Reviewer 会话按 r1-adjudication §一 的指定，以只读方式对新 head 做增量复审——未参与实现/返修，全程未修改任何文件/提交/删除/push）
- **Reviewed head**：`d0d8a3ab1b3d9877ef6f33a4f67ee36052cad0d1`（= 当前 main HEAD，工作区 clean，`git status --porcelain` 为空）
- **增量范围**：`e55a23dc9..d0d8a3ab` 共 5 个提交（cce587b10 r1 入库 → e0bfd4c6e 条件闭合内容 → ab31381fa 裁决入库【新 delivery_head】→ 18e01a3ed gates-final.log → d0d8a3ab SRC-25/EV-04 回填收口）
- **增量 diff**：仅 5 个文件（`doc/reviews/FEA-15-ACCEPT-1-r1.md`、`doc/reviews/FEA-15-ACCEPT-1-r1-adjudication.md`、`doc/tasks/FEA-15-ACCEPT-1.md`、`verification/FEA-15-ACCEPT-1/README.md`、`verification/FEA-15-ACCEPT-1/gates-final.log`），**全部 ⊆ allowed_paths**；任务卡改动逐 hunk 核验 = frontmatter 两字段（reviewer 会话 ID、delivery_head 6ad10aacf→ab31381fa）+ EV-04 行 + SRC 表头 + SRC-25 行 + Closeout 3 行，README 改动 = 4 hunk（P2-2 措辞、三条说明行、NOT_RUN 末行更新）。**无夹带**；`.gitattributes` 未动；r1 报告落盘内容与我原输出逐字一致。

## 结论：**approved**（绑定 `d0d8a3ab`；附 3 项收口前置条件，见「未完成前置」）

r1 四条处置条件全部闭合或按裁决合法延期；增量无新 P0/P1/P2；AC 状态登记诚实（AC5 保持 PARTIAL 未虚标）。

## r1 条件逐项闭合核验

| r1 条件 | 闭合情况 | 核验证据 |
|---|---|---|
| 1. P2-1 pin 口径修复授权 | **延期处置成立**（详见下节独立判定） | README 新增登记行（d0d8a3ab 版 L19）原文明示「29 条 EV/SRC pin 使用本机工作区字节口径，其中 26 条与 Git blob 哈希不同，跨 checkout 不可复现；需后续 pin 口径治理卡处理，本卡不改仓库级行尾规则」；裁决 §二 明确本卡不修的三条技术理由与 FEA-15-PIN-EOL-GOV-1 承接 |
| 2. P2-2 README:9 措辞 | **已正确修正** | 原句「堆栈指向 `Directory.Exists(.git)`」改为「堆栈终止于 `get_RepoRoot()` 的 NotNull 失败；`.git` 文件形态与失败的关联由源码和对照实验支持」——与 r1 建议措辞逐字对应；连锁义务（EV-04 回填）同步完成（见下） |
| 3. 固定 head 门禁三件套 | **已在 delivery_head 上执行** | `gates-final.log` 头行 `HEAD=ab31381fa`（= 新 delivery_head）：default/TASK/PINS 三段 `Governance check: PASS`、`PIN AUDIT: PASS (all 18)`，DEFAULT_EXIT=0 / TASK_EXIT=0 / PINS_EXIT=0，finished 2026-11-11T00:21:44——r1「未验证项 1」要求的固定 head 门禁已闭合（残留项见「未完成前置」第 1 条） |
| 4. P3-1..4 | **全部落地** | P3-1：SRC 表已补 `evidence_id/AC/Gate/path/commit/sha256/class` 表头成独立表格；P3-2：README 注明三份裁决日志实际顺序（second=中期 II→serial=串行化补充→evidence=最终）；P3-3：README 注明「实际平铺…与原证据计划的 logs/ 子目录结构不同」；P3-4：Closeout 记录「概括句已由 r1 以 git diff --name-status 核实」 |

## EV-04 / SRC-25 pin 核验（本 r2 独立复算）

| pin | 声称（commit / sha256） | blob 口径 | 工作区口径 | 判定 |
|---|---|---|---|---|
| EV-04 | `e0bfd4c6e` / `e4405800…8a1d` | `e4405800…8a1d` 一致 | `e4405800…8a1d` 一致 | **三方一致** ✓（README 为 i/lf w/lf 文件，无行尾转换；blob OID 在 e0bfd4c6e 与 d0d8a3ab 相同，pin 指向最后修改 commit，有效） |
| SRC-25 | `18e01a3ed` / `85543378…37c0` | `54376731…84b3` **不一致** | `85543378…37c0` 一致 | 声称值与工作区一致；blob（LF）不符——`i/lf w/crlf`（blob 1685B / 工作区 1723B / 38 行，恰为每行一个 `\r`）。**SRC-25 沿用了工作区 CRLF 口径**，与裁决「本卡内口径一致，统一归 GOV 卡」一致 |

gates-final.log 仅在 18e01a3ed 入库一次、其后未变；commit/sha 均指向真实存在对象，无伪造。

## 对 P2-1 延期的独立判定（明确措辞，不把未修复写成已修复）

**事实定性：P2-1 未修复。** `.gitattributes` 在本增量零改动、无任何 `verification/FEA-15-ACCEPT-1` eol 规则；原 26 条 pin 的跨 checkout 不可复现状态原样存在，且新增 SRC-25 使受影响集实际变为 **30 条 pin 中 27 条**（26 原有 + SRC-25；README 登记行的「29 条中 26 条」写于 SRC-25 登记之前，未覆盖新增项——见 P3-A）。

**判定：该延期满足我 r1 批准条件的实质，接受。** 理由：

1. r1 处置 1 的原文是「**由裁决方授权**修复 pin 口径…建议并入…或独立 GOV 卡」——条件实质是「取得被授权的、不造成新问题的修复路径」，不是「必须在本卡内修复」。裁决会话（`sess_2a802094`，2026-11-11）已作出明确决策并入库：本卡不修（`.gitattributes` 越 allowed_paths；eol 口径是全仓决策——r27 先例 300 pin 中 187 个同为工作区口径；只改 pin 值不加 eol 规则会造成本机反向不可复现；统一口径有 §4.4「先盘点全集、实测基线矩阵」硬前置）。
2. 披露义务已履行：README 登记行如实写明风险与去向，未使用任何「已修复/已解决」措辞；Closeout 同步声明「治理修复待另行释放」。诚实性完整。
3. 承接路径已命名并入库（裁决 §四.8 `FEA-15-PIN-EOL-GOV-1`，含 §4.4 核验前置步骤）。

**附跟踪条件（approved 的组成部分，防登记行成为孤儿）**：FEA-15-PIN-EOL-GOV-1 目前仅存在于裁决文本，**尚未在 REBASELINE_PLAN/TASK_LEDGER 登记 proposed**（本增量未触碰这两个文件）。按裁决序列它在本卡终态后释放；届时必须完成 proposed 登记，且其 §4.4 盘点基数须按「30 条中 27 条」的当前全集（含 SRC-25），不得按「29 中 26」旧数。

## gates-final.log 四条警告核验

- 3 条与既往相同（11 个非终态 Task、STATUS 3196B/PLAN 6983B 预算 80%），治理侧非本卡缺陷。
- 第 4 条「evidence_dir 含未登记过程文件：…gates-final.log」为**自指警告**：门禁运行于 ab31381fa 时该日志尚未入库/登记。Closeout 已如实登记成因（「生成时该日志尚未登记，故 4 条警告。本次登记日志后须再复核」）。解释成立；三段均 `PASS` + EXIT 0，4 警告无一为阻断项。
- **登记后的只读 `-TaskPath` 复核尚未执行**（预期应回到 3 警告 + PASS）——Closeout 自己声明「须再复核」，这正是下节前置条件第 1 条。

## 新 Findings

**P0 / P1 / P2**：无。

**P3**：

- **P3-A** SRC-25 加入后受影响 pin 全集为 27/30，README 登记行（写于 e0bfd4c6e）仍为「29 条中 26 条」且未覆盖新增项；建议终态/GOV 卡盘点时以当前全集为准（本报告已代为登记该事实）。
- **P3-B** AC5 的 PARTIAL 理由文字已过时：仍写「最终门禁待固定交付 head 后复核」，而固定 head 门禁（gates-final）现已存在；剩余实义是「登记后复核 + 最终结论」。翻 MET 时应同步改写理由，避免遗留过时表述。
- **P3-C** 裁决 §三（「AC5 在门禁留证+结论定型后翻 MET」）与 §四.4（「Commit 3 内翻 MET」）时序表述不一致，执行取 §三 保守侧（r2 与结论确认后再翻）——方向正确，但终态收口时须补齐「登记后 -TaskPath 复核 → AC5 翻 MET → Closeout 记 EXIT」链条，不能只完成一半。
- **P3-D** `FEA-15-PIN-EOL-GOV-1` 未登记 proposed（见上节跟踪条件）。

## 未验证项 / 未完成前置（终态前必须完成）

1. **登记后门禁复核**：gates-final.log 入库 + SRC-25 登记后，在最终 head 只读复跑 `check.ps1 -TaskPath`（预期 3 警告 PASS），EXIT 记入 Closeout——裁决 §二/§四.4 明文要求，当前未执行。
2. **AC5 最终翻转**：待本 r2 + ZCode 裁决会话结论确认（closed_with_limitations + limitation 清单三条：分类③挂 DIAG/FIX、A2/A4 NOT_RUN 挂 PACKAGE-GAP、P2-1 挂 GOV）后翻 `[x]` `<<MET>>` 并同步改写理由（P3-B/C）。
3. **集成与终态**：integration_commit 回填、`resource_closeout_status: complete`（PRESERVE_UNKNOWN 三行即终态处置、不物理清理）、STATUS/PLAN/LEDGER 指针移出、`FEA-15-DIAG-ACL-1` 与 `FEA-15-PIN-EOL-GOV-1` 按序释放并登记 proposed。
4. 本 r2 为只读复审：未复跑任何测试/构建/门禁；结论基于 gates-final.log 内容、Git 对象三方哈希比对与增量 diff 核验。r1 全量核验结论（22 文件+对象级）对新 head 仍有效，未重复执行。

---

**推荐下一步**（可直接转发）：

> **致 ZCode 裁决会话（`sess_2a802094`）/ Codex**：r2 增量复审已出，结论 **approved**（绑定 `d0d8a3ab`，0×P0/P1/P2，4×P3；r1 四条件全部闭合，P2-1 延期经独立判定成立——未修复、已如实登记、挂 GOV 卡，附跟踪条件）。请按序收口：① 在 `d0d8a3ab` 只读复跑 `check.ps1 -TaskPath`（预期 3 警告 PASS），EXIT 记入 Closeout；② ZCode 裁决会话确认最终结论措辞（`closed_with_limitations`）与 limitation 清单；③ AC5 翻 `[x]` `<<MET>>` 并改写理由（P3-B/C）→ Commit 4 入库本 r2 报告至 `doc/reviews/FEA-15-ACCEPT-1-r2.md`；④ Codex 集成（integration_commit 回填、resource_closeout_status: complete、终态、指针移出）；⑤ 唯一 Active 空出后按序释放 `FEA-15-DIAG-ACL-1`（优先）与 `FEA-15-PIN-EOL-GOV-1`（两卡均须先登记 proposed；GOV 卡盘点基数=30 pin 中 27 条工作区口径，含 SRC-25）。
