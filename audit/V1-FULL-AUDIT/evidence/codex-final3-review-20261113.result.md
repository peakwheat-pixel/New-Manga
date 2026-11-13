## 审查身份与 reviewed_head / 工作树状态

Codex 全新上下文只读审查。`branch=main`；实际 `reviewed_head=6350081a535d5c67c57c0f1c6123a68ed5bbdf57`，与 `expected_head` 一致。审查开始和结束时 `git status --porcelain` 均为空，工作树 clean。

核验命令摘要：`git status --porcelain`、`git rev-parse HEAD`、`git branch --show-current`，以及只读文档、日志、代码和 Git 对象哈希核验。未修改文件。

## 总结结论

**REJECT**，阻断原因是审计交付状态存在当前摘要与证据不一致，以及专项报告残留未标明的旧裁决文字；另有当前 HEAD 门禁证据未能从仓库记录中追溯。不是产品发布批准或产品审计 PASS。

462 条 Canonical Evidence pins 本身通过核验；候选裁决与问题计数基本自洽，Release Gate 应继续保持 `BLOCKED`。AC1、AC2 可维持 `MET`；AC3、AC4 仍为 `PARTIAL`，当前不能收口。

## 发现：按严重度排序

以下均为 **审计交付阻断，不计入产品 P0–P3**。

1. **当前摘要的计数与 Review 状态仍落后。** [STATUS.md](<G:/CODEX/New Manga/doc/STATUS.md:7>) 和 [AUDIT_STATUS.md](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_STATUS.md:4>) 把当前 pins 写为 `441/441`；实际 Task 卡为 462 条。 [AUDIT_PLAN.md](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_PLAN.md:5>) 仍称最新 gate 为 `d248ed28`、已完成三轮 Review；[13_RELEASE_GATE.md](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:15>) 仍把已修复的文档事项写成最新 Review 的 REJECT 原因，并称只有 441 pins；[FINAL_AUDIT_REPORT.md](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/FINAL_AUDIT_REPORT.md:3>) 仍以首轮 `d92859c9…` 作为报告状态。Task 的 AC3 描述也仍把重复 ID、门禁未 pin 等旧问题写作当前原因，见 [Task 卡](<G:/CODEX/New Manga/doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md:37>)。

   **最小返修：**同步当前入口至 462 pins 和最新 gate / Review 状态，区分历史 REJECT 原因与当前结论；保留已固定的历史 Review 原件，不追改历史记录。P7 集成报告自称“早期快照”，其中的旧计数可作为历史记录保留，但不能作为当前状态依据。

2. **专项报告仍有与裁决台账冲突的旧文字。** [AUDIT-05/06 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md:5>) 仍称待 ZCode 裁决；[AUDIT-07 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-07-REPAIR-TYPESET-EXPORT-2026-11-13.md:5>) 仍称严重度留给 ZCode，正文继续标 `REVIEW_PENDING`；[AUDIT-09 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-09-UI-UX-2026-11-13.md:41>) 明称候选当前仍未裁决、请 ZCode 复核；[AUDIT-14 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md:54>) 仍把 ZCode 定级列为后续工作。这些与 [11_ISSUES.md](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:11>)、[AUDIT_ISSUES.md](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:5>) 的 Codex 裁决相矛盾。

   **最小返修：**把这些状态和动作明确标为阶段快照，或改为引用当前台账；保留原始测试结果及所有 `NOT_RUN` / 限制，不把候选状态改写成产品验证通过。

3. **最新 HEAD 的治理门禁缺少可追溯证据指针。** `ed17a790`、`52b86d39`、`d248ed28`、`fee77cc0` 的已 pin 批次均能定位；其日志显示各批对应门禁 `EXIT=0`。但 [AUDIT_RESUME.md](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_RESUME.md:17>) 只笼统声称 fee77 及“后续 HEAD”均通过，未给出后续 HEAD 的完整 hash、日志路径或 pin。仓库当前可核验的 pin 中未找到与本次 `reviewed_head=6350081a…` 对应的门禁批次。

   **最小返修：**如果后续 HEAD 的门禁已运行，补齐其完整 HEAD、四项日志/metadata 路径并纳入 pins；否则在最终交付 HEAD 上运行并记录门禁，再复核 pins。此项仍属 `AC4` 收口所需证据。

## 11 个候选的逐项裁决

| ID | 结论 | 进入 P0–P3 计数 | severity/priority | 依据 | 建议后续 Task / 验证 |
|---|---|---:|---|---|---|
| AUDIT-05-CAND-001 | INVESTIGATE | 否 | N/A | 合成 same-geometry primary/SFX 保留双 Region；既有仲裁取舍存在，但预期去重语义未定。见 [05/06 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md:34>)。 | 先定相同/近似区域、人工修改及 `skip`/`translate` 语义，再做仲裁与 Region 数量回归。 |
| AUDIT-06-CAND-001 | INVESTIGATE | 否 | N/A | 有 StepRun 与重试上限；没有账单级预算或 provider idempotency key。未调用付费 API，无重复计费证据。见 [台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:13>)。 | 先由需求决定预算和幂等合同；用 fake provider 测重试和预算边界。 |
| AUDIT-06-CAND-002 | INVESTIGATE | 否 | N/A | glossary 随请求发送，但生产路径未强制术语匹配；原始需求合同及真实模型行为未知。见 [05/06 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-05-06-SFX-TRANSLATION-2026-11-13.md:45>)。 | 核对 glossary 需求合同，再用合成响应覆盖漏词、错词与冲突词条。 |
| AUDIT-07-CAND-001 | finding | 是，P2 | P2 | 定向测试记录 127 passed / 3 failed；ZIP `store`、JSON text override 和空 options hook events 不符预期。见 [07 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-07-REPAIR-TYPESET-EXPORT-2026-11-13.md:72>)。 | 另开实现 Task 修正 options/hook 行为；跑对应单测及 export 回归。 |
| AUDIT-07-CAND-002 | accepted limitation | 否 | N/A | `license_note` 不验证授权；仓库 tracked font assets 为 0，FEA-14-FONT-1 默认不随包分发字体，未发现未授权分发证据。见 [台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:116>)。 | 保留限制；若未来随包或消费用户字体，另行核验授权和渲染路径。 |
| AUDIT-09-CAND-001 | finding | 是，P3 | P3 | synthetic UI 截图显示已有选中作品/章节，但 Retry 提示先选择；我核看了该合成截图。它不证明普遍性或内部根因。见 [报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-09-UI-UX-2026-11-13.md:41>)、[截图](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/screenshots/audit09-v2-reader-retry-banner-20261113.jpg>)。 | 隔离 UI fixture 覆盖已选/未选、零页、切换、Retry/返回，再按真实 selection 状态修正。 |
| AUDIT-12-CAND-001 | finding | 是，P3 | P3（交付工具） | `publish.ps1` 默认写入仓库 `artifacts/win-x64-single`，并可递归删除目录；脚本未运行，无误删证据。见 [台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:30>)。 | 另开 Task 将输出改到相邻 workspace；在 disposable 目录验证规范化目标和清理范围。 |
| AUDIT-14-CAND-001 | finding | 否 | P3 优先级（非产品 P 级计数） | README/AD-003 等文档存在漂移，且无权威逐项 V1 manifest，不能可靠计算完成率。见 [14 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md:34>)。 | 建立有日期/版本的 V1 manifest，再对齐 README、AD-003、STATUS 与索引。 |
| AUDIT-14-CAND-002 | INVESTIGATE | 否 | N/A | V2 Studio 有静态 `NOT_WIRED` 能力，但是否属于 V1 承诺未知，GUI 未测。见 [14 报告](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md:25>)。 | 先映射 V1 manifest；若纳入 V1，再单独做真实 Host/GUI 验收。 |
| AUDIT-14-CAND-003 | close | 否 | N/A | workflow 不传 `-IconPath`，installer 仅在旧图标存在时设置该路径；现有证据不能证明当前发布会失败。见 [台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:44>)。 | 不开缺陷 Task；如清理旧路径，先核调用方并经授权隔离验证。 |
| AUDIT-14-CAND-004 | close | 否 | N/A | 多 shell 路由说明回归面较大，但没有具体运行故障证据。见 [台账](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/AUDIT_ISSUES.md:51>)。 | 不开缺陷 Task；未来真实 UI 验证记录 shell × page × 操作矩阵。 |

## AUDIT-11-INC-001 裁决

维持 `INVESTIGATE`，不分配 severity，也不计入 P0–P3 或 finding 数。本地 reflog 和提交关系支持“私有素材对象可能随历史 main push 进入公开仓库”的高置信推论；**当前远端是否可见、可下载或可 fetch 仍未知**。远端缓存/对象状态及当时完整授权语境也未知。没有证据可推断为“已公开”，也没有证据可推断风险已消除。下一步只能在另立且范围获准的只读调查中核验远端可见性；本轮未访问远端或采取补救。

## P0–P3 和 finding 总计核验

[11_ISSUES.md](<G:/CODEX/New Manga/audit/V1-FULL-AUDIT/reports/11_ISSUES.md:9>) 的计数边界自洽：

- 原有开放 finding：3 项（`SEG-B-PROBES-001/002`，Medium / High confidence，不映射 P 级；`NM-AUD-0001`，P2）。
- 11 个候选：4 finding、4 INVESTIGATE、1 accepted limitation、2 close。
- 新增 finding：`AUDIT-07-CAND-001` P2、`AUDIT-09-CAND-001` P3、`AUDIT-12-CAND-001` P3、`AUDIT-14-CAND-001` 文档 finding（P3 优先级，不计产品 P 级）。
- 开放 finding 合计 **7 项**：2 项未映射 P 级、P2 两项、产品 P3 两项、非产品文档 finding 一项。
- 产品 P0/P1/P2/P3 = **0/0/2/2**。P0/P1 为已分配数量，不代表已证明不存在。`AUDIT-11-INC-001` 与关闭的非产品观察 `AUDIT11-REV-001` 不计入开放 finding。

## R1–R4 次序意见

建议沿用 R1 → R2 → R3 → R4，并落实 R1 的边界：

1. **R1**：优先安排 `AUDIT-11-INC-001` 的独立、获准只读远端可见性调查；不得夹带删除或历史改写。再分别处理 junction containment 和 restore 失败语义。
2. **R2**：处理 `NM-AUD-0001` sidecar 生命周期问题。
3. **R3**：先修复 P2 的 AUDIT-07 导出 finding，再处理 AUDIT-09 Reader 提示和 AUDIT-12 发布工具路径；05/06/14-002 先完成需求裁定。按计划补齐 GUI、安装和关键链路验证。
4. **R4**：建立权威 V1 manifest，并在进一步判断 V2 Studio 承诺前完成范围映射。**本次 P7 文档同步是当前 AC3 的返修项，不应等到未来 R4。**

## Release Gate 决定

**保持 `BLOCKED`；不满足 `PASS` 或 `CONDITIONAL`。** 七项开放 finding 未修复，Python Core 全量 pytest 仍有 16 failed / EXIT 1，Avalonia TestHost 未进入测试，真实模型/API、完整 UI、当前基线安装与升级/回退等关键路径仍有具名 `NOT_RUN` / `BLOCKED`。`AUDIT-11-INC-001` 的远端现状未知。不得把这些限制改写成通过，也不宣告产品发布 PASS。

## AC1–AC4 与 Task 生命周期建议

- **AC1：MET。**
- **AC2：MET。** 这表示审计专项有结果或具名限制，不代表各专项测试 PASS；既有 FAIL / PARTIAL / BLOCKED 保持原状。
- **AC3：PARTIAL，不可收口。** 当前状态/计数和专项报告仍有过时裁决文字，且最终报告需要同步本次 Review。
- **AC4：PARTIAL，不可收口。** 462 pins 核验通过，但后续 HEAD 门禁声明不可追溯；本次 Review 结果也需由 DSH 纳入治理证据并完成集成/closeout。

按协作协议 §4，建议 Task 保持 `in_progress`（如已进入 Review 阶段，由 DSH 按流程记录 `changes_requested`，返修后再以新 head 进入 `in_review`）；不得置为 `done` 或 `closed_with_limitations`。只有 AC 全通过、最终证据与治理门禁固定、资源 closeout 完成，并由 DSH 集成裁决后，才能关闭。

## 明确未执行的检查及边界

没有重跑测试、构建、`tools/governance/check.ps1` 或其他门禁；没有访问远端、push、安装、发布、清理或写入文件；没有读取或重建私有素材。我读取了专项报告、现存日志/元数据、相关发布脚本和一张审计记录为 synthetic 的 UI 截图。

462 pins 的核验使用只读 Git 对象读取与内存 SHA-256 计算：462 行均能定位到 commit/path，**462/462 BLOB SHA-256 匹配，462 个 ID 唯一，0 个失败**；没有运行仓库自带的 `verify_canonical_evidence.py`，因为该脚本会写 log/JSON。`ed17a790`、`52b86d39`、`d248ed28`、`fee77cc0` 批次的已有日志显示四项门禁 `EXIT=0`；这不替代当前 `reviewed_head` 的门禁证据。

**建议下一步：**由 DSH 最小修订当前状态摘要和专项报告中的旧裁决措辞，补齐或固定最终 HEAD 的门禁证据与本次 Review 记录，然后以新 clean head 再做独立复审。