## 审查身份与 reviewed_head / 工作树状态

**Reviewer：Codex，全新上下文；reviewed_head=`c2f5bc8273314f18fe91ea29781339f659872899`；branch=`main`；工作树 clean。**

审查开始与结束均核对了 `git status --porcelain`、`git rev-parse HEAD` 和 `git branch --show-current`：工作树状态为空，`HEAD` 与 `expected_head` 一致，分支为 `main`。

## 总结结论

**REJECT。**

`ACCEPT_WITH_LIMITATIONS` 所允许的“最新门禁尚未按滚动规则回填”本身可以接受；当前还有两处未收敛的文档冲突，因此它不是唯一剩余问题。产品 Release Gate 继续 **BLOCKED**，本结论不表示产品发布通过。

## 发现：按严重度排序

**F1｜审计当前摘要与 Task 检查点过时，阻断 AC3/AC4 收口。** Task 的 AC3 仍写“四轮 Review”，AC4 只列首轮与返修复审；`Rolling checkpoint` 则称有“三轮 Review”，并将第三轮称为最终复审。[Task AC 摘要](<G:/CODEX/New Manga/doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md:37>) [Task rolling checkpoint](<G:/CODEX/New Manga/doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md:578>) 与现行五轮记录不一致；五轮及 496 pins 已出现在 [AUDIT_STATUS](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_STATUS.md:4>)、[AUDIT_PLAN](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_PLAN.md:5>)、[AUDIT_RESUME](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_RESUME.md:7>) 和 [Release Gate](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:5>)。

最小返修：同步 Task 的 AC3/AC4 说明与 rolling checkpoint，补上第四、五轮 Review 摘要及当前已归档门禁批次。记录本次 Review 时，再绑定本次 `reviewed_head` 和结论。最新 HEAD 门禁未入库的滚动限制应单独标清，不应再用旧轮次摘要描述当前状态。

**F2｜专项报告与证据索引仍把已裁决事项写成待 ZCode 裁决。** [AUDIT-07 专项](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-07-REPAIR-TYPESET-EXPORT-2026-11-13.md:76>) 仍称 `AUDIT-07-CAND-002` 为 `REVIEW_PENDING`、待 ZCode 判断；其结论段还称两项候选均由 ZCode 最终裁决。[AUDIT_EVIDENCE_INDEX](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_EVIDENCE_INDEX.md:49>) 仍称 05/06 候选的严重度和 finding 状态待 ZCode 裁决。这些文字没有标为阶段快照，且与专项报告顶部、索引其他条目和 [当前问题台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:43>) 的 Codex 裁决冲突。

最小返修：将这些残留句子标明为阶段快照并链接当前处置，或直接更新为现行状态。`AUDIT-07-CAND-002` 应指向 `accepted limitation`；05/06 三项应指向 `INVESTIGATE`。

`P7-INTEGRATION-CONSISTENCY-CHECK` 自称早期固定 HEAD 快照，其中 371、398、441 是历史检查点；我没有将这些数字当作当前 496 pins。[P7 快照说明](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/P7-INTEGRATION-CONSISTENCY-CHECK-2026-11-13.md:3>) [398/398 历史检查点](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/P7-INTEGRATION-CONSISTENCY-CHECK-2026-11-13.md:24>)

## 11 个候选的逐项裁决表

| ID | 结论 | 是否进入 P0–P3 计数 | severity / priority | 依据 | 建议后续 Task / 验证 |
|---|---|---|---|---|---|
| `AUDIT-05-CAND-001` | INVESTIGATE | 否 | N/A | 合成同几何场景会产生双 SFX Region；产品去重语义未定。[台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:43>) | 先裁决相同/近似区域、人工修改及 `skip`/`translate` 语义；再用合成用例验证 Region 数与请求数。 |
| `AUDIT-06-CAND-001` | INVESTIGATE | 否 | N/A | 有重试上限，没有账单级预算；未调用付费 API，也没有重复扣费证据。[台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:44>) | 先确定是否要求费用上限；再用 fake provider 验证重试和预算耗尽。 |
| `AUDIT-06-CAND-002` | INVESTIGATE | 否 | N/A | glossary 会进入请求，但逐项强制匹配的需求未证实，真实模型未测。[台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:45>) | 明确 glossary 合同后，以 fake provider 覆盖冲突词条、漏匹配和无效输出。 |
| `AUDIT-07-CAND-001` | finding | 是 | P2 | 定向测试 `127 passed / 3 failed`：ZIP `store`、JSON text override、空 options 的 hook audit events 不符预期。[台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:28>) | 新实现 Task 修正 options/hook 行为，重跑相关单测和 export 回归。 |
| `AUDIT-07-CAND-002` | accepted limitation | 否 | N/A | `license_note` 只是备注；tracked font assets 为 0，没有随包分发的未授权证据。用户字体许可仍 `NOT_RUN`。[台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:46>) | 当前不据此开缺陷 Task；如未来决定随包字体，再核验许可来源与范围。 |
| `AUDIT-09-CAND-001` | finding | 是 | P3 | 合成空章节场景显示作品/章节已选中，但 Retry 提示先选择；根因和普遍性未知。[台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:29>) | 用隔离 Host/UI fixture 覆盖有页、零页、切换选择和 Retry，再修正提示与状态。 |
| `AUDIT-12-CAND-001` | finding | 是 | P3（交付工具） | 静态检查发现 `publish.ps1` 默认输出在仓库内并递归清理；脚本未运行，没有已误删证据。[台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:30>) | 新 Task 将默认输出移至相邻 workspace，并只在 disposable 目录验证清理范围。 |
| `AUDIT-14-CAND-001` | finding | 否 | N/A / P3 优先级 | README、AD-003 与实现清单有漂移，缺少可逐项核验的 V1 承诺总账；属于文档 finding。[台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:31>) | 建立带版本和日期的 V1 manifest，对齐 README、AD-003、STATUS 与索引。 |
| `AUDIT-14-CAND-002` | INVESTIGATE | 否 | N/A | V2 Studio 有静态 `NOT_WIRED` 能力，但其 V1 归属未知，真实 GUI 未测。[台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:47>) | 先用权威 V1 manifest 确定归属；只有纳入 V1 后再决定实现和 GUI 验收。 |
| `AUDIT-14-CAND-003` | close | 否 | N/A | 现有 workflow 不传 `IconPath`，证据没有证明缺图标会导致当前 release 失败。[台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:48>) | 不开缺陷 Task；如清理旧路径，先核实调用者并纳入维护 Task。 |
| `AUDIT-14-CAND-004` | close | 否 | N/A | 多 shell 是架构观察，没有具体运行故障证据。[台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:49>) | 不开缺陷 Task；后续真实 UI 验证记录 shell × page 矩阵。 |

## AUDIT-11-INC-001 裁决

维持 **INVESTIGATE**；不分配 severity，不计入 P0–P3 或 finding 数。仓库内本地历史证据支持“私有素材对象可能随历史 main push 传播”的高置信推论。**当前远端可见性、是否可下载或 fetch、远端缓存与对象状态仍未知。** 不得推断为已公开，也不得推断为已消除。[问题台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:37>)

最小后续步骤是另开范围冻结且授权的只读调查 Task，记录目标、时间、方法与结果。删除、历史改写或其他补救须另行裁决。

## P0–P3 和 finding 总计核验

- 产品等级：P0=0、P1=0、P2=2（`NM-AUD-0001`、`AUDIT-07-CAND-001`）、P3=2（`AUDIT-09-CAND-001`、`AUDIT-12-CAND-001`）。P0/P1 表示当前已分配数量，不证明不存在此等级问题。
- 开放 finding 共 7：3 项原已 triage（两项 SEG-B Medium / High confidence，不映射 P 级；`NM-AUD-0001` 为 P2）加 4 项候选 finding，其中 `AUDIT-14-CAND-001` 是非产品文档 finding，P3 优先级不计入产品 P0–P3。
- `AUDIT-11-INC-001` 是调查风险，不计 finding；已关闭的 `AUDIT11-REV-001` 是非产品 P3 observation，不计开放 finding。[总表与计数边界](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:7>)

## R1–R4 次序意见

同意 [整改计划](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/12_REMEDIATION_PLAN.md:5>) 的顺序：

1. **R1**：先安排独立、获授权的远端可见性只读调查；再分别处理 junction 越界和 restore 失败语义。调查不得顺带删除或改写历史。
2. **R2**：处理 sidecar 取消、Dispose 与 Host shutdown 生命周期。
3. **R3**：先处理 07-001 P2，再处理 09-001、12-001；05/06 与 14-002 先完成需求或 V1 归属裁定。
4. **R4**：推进 V1 manifest 与文档治理；14-001 应先于 14-002 的归属裁定。14-003/004 已关闭，不安排缺陷修复。

## Release Gate 决定

**保持 BLOCKED；不宣告产品发布 PASS。** 七项开放 finding、pytest 的 16 个失败、Avalonia TestHost 的 TRX `0 tests`、关键 UI/安装/模型检查的 `NOT_RUN` 或 `BLOCKED`，以及 `AUDIT-11-INC-001` 未知的远端状态，均支持此结论。[Release Gate 阻断依据](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:9>)

`52b86d39` 与 `ed17a790` 两批已归档门禁的四项记录均为 `EXIT 0`；default/TaskPath 各有 3 warnings，`verify_pins` 为 18/18，API inventory 合计 86 项。它们只证明各自的治理窄面。当前 `c2f5bc827` 的最新门禁据用户说明保存在仓外 Task workspace；本次未读取该路径，也不独立确认其内容。按滚动 pinbackfill 规则，未入库本身是**可接受 limitation**，不解除 Release Gate。

## AC1–AC4 与 Task 生命周期建议

- **AC1：MET。**
- **AC2：MET，可收口。** 保留专项原有 `FAIL`、`BLOCKED`、`PARTIAL` 和具名 `NOT_RUN`，不能将它们概括成 PASS。
- **AC3：当前不可收口。** Task 当前摘要与专项/索引仍有未修复的状态冲突。
- **AC4：当前不可收口。** Pins 已复核，但本次 Review 为 REJECT，且最新 HEAD 门禁没有仓内证据供独立核验。未回填这一点单独看可以接受，文档返修和 Review 记录仍待完成。

Task 当前应保持未完成。完成 F1/F2 的最小返修后，以新固定 head 交由新的独立 Review 上下文复审；随后由 DSH 集成、补齐治理检查和资源 closeout，再依生命周期更新状态。不得据此将产品 Release Gate 改为通过。[Task 状态与 AC](<G:/CODEX/New Manga/doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md:35>) [生命周期规则](<G:/CODEX/New Manga/doc/09_COLLABORATION.md:83>)

## 明确未执行的检查及边界

- 独立解析 Task Canonical Evidence 表并以只读 Git 对象复核：**496 条唯一 pins**，473 条 `CANONICAL`、23 条 `SOURCE_PIN`；496 条均声明 `BLOB`，commit 引用解析为 commit、路径解析为 blob，SHA-256 全部匹配。未读取或渲染唯一截图 pin 的图像内容。
- 历史 398 条复算 JSON 记录为 398/398 PASS；398 组路径、commit、SHA、类别与基准元组都能在当前 496 条表中找到。14 条 AUDIT-03/04 更正（10 条 / 4 条）有必要且正确：旧值逐项匹配 Git BLOB 转为 CRLF 的哈希，新值逐项匹配 raw Git BLOB SHA-256。[更正记录](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/evidence/task-card-pin-correction-20261113.json>) [P7 更正说明](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/P7-INTEGRATION-CONSISTENCY-CHECK-2026-11-13.md:22>)
- `52b86d39`、`ed17a790` 门禁日志与结果 JSON 的 pins 均通过上述核验；ZCode 额度回执显示 provider `1310`、HTTP `429`、EXIT 1、无 session/response。该失败不是 Review；Codex 优先路径已启用。[ZCode 额度证据](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/evidence/zcode-final-review-probe-20261113T1935Z.json>)
- 未运行产品测试、重型扫描、应用、GUI、真实模型、人工 GT、付费 API、clean Windows 安装/升级/回退/卸载、publish 脚本或治理检查脚本；未访问远端或其他外部系统；未读取或重建私有漫画、模型或用户素材。
- 未修改任何文件。结束时 `git status --porcelain` 仍为空，`HEAD` 未变化。

**建议下一步：** 由 DSH 记录本次 Review 为 `changes_requested`，先修正 Task 当前摘要、`AUDIT-07` 和 Evidence Index 的残留措辞，再固定新 head 进行独立复审。